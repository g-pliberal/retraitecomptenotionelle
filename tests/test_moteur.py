"""Tests du moteur : indexation, âge de référence, conversion, fusion, compte."""

from __future__ import annotations

import pytest

from retraite_notionnelle.config import (
    Parametres,
    RACINE_DONNEES,
    SourceCotisations,
)
from retraite_notionnelle.donnees.macro import DonneesMacro
from retraite_notionnelle.donnees.mortalite import DonneesMortalite
from retraite_notionnelle.donnees.population import Population
from retraite_notionnelle.moteur.conversion import Convertisseur
from retraite_notionnelle.carriere import (
    Metier,
    profil_salaire,
)
from retraite_notionnelle.moteur.compte import ConstructeurCompte
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def macro() -> DonneesMacro:
    return DonneesMacro(RACINE_DONNEES)


# -- indexation --------------------------------------------------------------
# Les règles d'indexation, leur lissage et le SMIC annuel s'éprouvent sur le
# portage : tests/js/indexation.test.js (action 161, quatrième vague).


def test_le_salaire_moyen_refait_les_niveaux_que_l_insee_publie(macro):
    """L'ancrage est un niveau publié, et non un arrondi.

    Le modèle cumule les croissances du salaire moyen à partir du niveau de
    2024, LU dans la série certifiée : il était écrit à la main jusqu'au
    6 octobre 2026, 40 000 € pour 40 897 €. Le cumul doit alors retrouver les
    niveaux de TOUTES les années publiées, de 1949 à la dernière, à l'écart
    près des cinq décimales des croissances : un ancrage faux, ou des
    croissances tirées d'une autre source, l'en écarteraient du même coup.
    """
    from retraite_notionnelle.carriere import ancrage_salaire_moyen, indice_salaire_moyen

    niveaux = macro.salaire_moyen_niveau
    assert ancrage_salaire_moyen(macro) == (2024, niveaux(2024))
    assert niveaux(2024) == pytest.approx(40_897.0, abs=0.5)
    indice = indice_salaire_moyen(macro, niveaux.premiere_annee, niveaux.derniere_annee)
    for annee in niveaux.annees():
        assert indice[annee] == pytest.approx(niveaux(annee), rel=1e-4), annee


def test_le_cas_type_au_smic_gagne_le_smic_de_chaque_annee():
    """Le cas type au SMIC gagne le salaire minimum, non une part du moyen.

    Il s'écrivait 0,55 fois le salaire moyen à toutes les années, quand le
    minimum en a valu 0,40 en 1970 et 0,52 en 2024 : ses années de 1970
    comptaient 39 % de trop, celles d'aujourd'hui 6 %. Chaque année entière de
    sa carrière porte désormais au compte le SMIC annuel de cette année-là,
    et le rattachement à un vingtile lit ce que cela fait en multiple du
    salaire moyen, comme le simulateur.
    """
    from retraite_notionnelle.carriere import PROFIL_SMIC
    from retraite_notionnelle.castypes import CAS_TYPES
    from retraite_notionnelle.moteur.conversion import niveau_relatif
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur(Parametres())
    cas = next(c for c in CAS_TYPES if c.code == "smic_carriere_complete")
    assert (cas.profil_carriere, cas.niveau_salaire) == (PROFIL_SMIC, 1.0)
    carriere = cas.construire(simulateur, 1955)
    entieres = [l for l in carriere.lignes if l.fraction_annee == 1.0]
    assert {l.annee for l in entieres} >= {1973, 1990, 2000, 2010}
    for ligne in entieres:
        assert ligne.revenu == pytest.approx(simulateur.macro.smic_annuel(ligne.annee))
    niveau = cas.niveau_relatif(simulateur, 1955)
    assert niveau == pytest.approx(niveau_relatif(carriere, simulateur.macro))
    assert 0.45 < niveau < 0.55


def test_la_carriere_heurtee_valide_ce_que_le_droit_donne_au_chomage():
    """La carrière heurtée de la maquette Osiris de la DSS (étude d'impact du
    projet de loi instituant un système universel de retraite, 2020, p. 202 du
    PDF) : un non-cadre du privé au salaire du tiers inférieur, environ
    30 000 € par an quand le salaire moyen en fait 38 000, entré à vingt-deux
    ans, perd son emploi à quarante-deux, touche l'ARE deux ans puis l'ASS deux
    ans, reste un an et demi au chômage non indemnisé, puis est inactif
    jusqu'au départ.

    Le droit lui valide quatre trimestres par année d'ARE et d'ASS (R. 351-12,
    4°, c, du code de la sécurité sociale) ; pour la première période de
    chômage non indemnisé, six au plus si elle suit le 31 décembre 2010, quatre
    avant (R. 351-12, 4°, d ; décret n° 2011-934, art. 2) ; rien pour
    l'inactivité. Avec cent deux trimestres au plus, il part au taux plein par
    l'âge (L. 351-8, 1°, fiche ``age_annulation_decote``) : soixante-sept ans,
    né en 1955 ou après, soixante-cinq, né en 1950.
    """
    from retraite_notionnelle.castypes import CARRIERE_HEURTEE as cas
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur(Parametres())
    assert (cas.affiliation, cas.age_debut, cas.caisses) == (
        "salarie_prive_non_cadre", 22, ("cnav",))
    assert cas.niveau_salaire == pytest.approx(30_000 / 38_000, abs=0.01)
    for generation, depart, non_indemnise in ((1950, 65, 4), (1960, 67, 4),
                                              (1980, 67, 6)):
        carriere = cas.construire(simulateur, generation)
        assert carriere.age_liquidation == depart, generation
        par_periode: dict[str, list[int]] = {}
        trimestres: dict[str, int] = {}
        for ligne in carriere.lignes:
            par_periode.setdefault(ligne.type_periode, []).append(ligne.annee - generation)
            trimestres[ligne.type_periode] = (trimestres.get(ligne.type_periode, 0)
                                              + ligne.trimestres_valides)
        assert par_periode["emploi"] == list(range(22, 42)), generation
        assert par_periode["chomage_indemnise"] == [42, 43]
        assert par_periode["chomage_solidarite"] == [44, 45]
        assert par_periode["chomage_non_indemnise"] == [46, 47]
        # Jusqu'au départ : l'année du départ n'a de ligne que s'il en reste
        # un mois, ce que décide le jour de naissance présumé (R. 351-37).
        derniere = max(ligne.annee for ligne in carriere.lignes) - generation
        assert depart - 1 <= derniere <= depart, generation
        assert par_periode["inactivite"] == list(range(48, derniere + 1))
        assert trimestres == {"emploi": 80, "chomage_indemnise": 8,
                              "chomage_solidarite": 8,
                              "chomage_non_indemnise": non_indemnise,
                              "inactivite": 0}, generation


def test_l_inapte_de_la_cnav_part_au_taux_plein_des_l_age_legal():
    """L'inapte de la grille du coût (action 138, étape 7) : les nouveaux
    retraités de 2021 pour inaptitude au travail hors ex-invalides, que la
    Cnav décrit (étude 2023-014, tableaux 2 à 4) — 19 358 anciens titulaires
    de l'AAH et 27 332 autres inaptes : un premier trimestre l'année de leurs
    vingt ans ; 94 et 131 trimestres, 116 en moyenne ; 56 et 71 % de ces
    trimestres cotisés, quelque 76 sur 116 ; un salaire annuel moyen de 56 et
    77 % du SMIC de 2021 (19 073,64 €), 68 % en moyenne. Le chômage fait
    l'essentiel de leurs périodes assimilées, avec, pour les femmes, l'AVPF et
    la majoration pour enfants, et pour les autres inaptes la maladie en fin
    de carrière (graphique 1) ; l'emploi et le chômage se mêlent à tout âge
    jusque vers cinquante ans, et les années sans report se multiplient
    ensuite (graphiques 5 à 8). Le cas type travaille à 0,90 SMIC de vingt à
    quarante-sept ans, une année sur trois au chômage indemnisé, de vingt et
    un à quarante-huit ans, puis n'a plus d'activité : 76 trimestres cotisés
    sur 116. Il a, né en 1959 et parti en 2021, le salaire annuel moyen
    publié. Jusqu'au 19 octobre 2026, il travaillait à 70 % du SMIC de vingt
    à quarante-neuf ans, ses 116 trimestres tous cotisés, pour un salaire
    annuel moyen de 55 % du SMIC.

    Reconnu inapte, il a le taux plein dès l'âge légal quelle que soit sa durée
    (L. 351-8, 2°, fiche ``inaptitude_au_travail``) : à soixante ans né en
    1950, à soixante-deux né en 1960 et après, la réforme de 2023 lui gardant
    cet âge. Sans l'inaptitude, la même carrière attendrait l'âge d'annulation
    de la décote, soixante-cinq puis soixante-sept ans."""
    import re
    from dataclasses import replace

    from retraite_notionnelle.castypes import INAPTE_CNAV as cas

    simulateur = Simulateur(Parametres())
    assert cas.inaptitude and cas.mortalite == "cnav_inaptitude"
    assert (cas.affiliation, cas.age_debut, cas.niveau_salaire, cas.caisses) == (
        "salarie_prive_non_cadre", 20, 0.9, ("cnav",))
    sans = replace(cas, inaptitude=False)
    for generation, depart, annulation in ((1950, 60, 65), (1960, 62, 67),
                                           (1980, 62, 67)):
        carriere = cas.construire(simulateur, generation)
        assert carriere.age_liquidation == depart, generation
        assert carriere.inaptitude, generation
        trimestres: dict[str, int] = {}
        for ligne in carriere.lignes:
            if ligne.annee <= carriere.annee_liquidation and ligne.trimestres_valides:
                trimestres[ligne.type_periode] = (trimestres.get(ligne.type_periode, 0)
                                                  + ligne.trimestres_valides)
        assert trimestres == {"emploi": 76, "chomage_indemnise": 40}, generation
        assert sans.construire(simulateur, generation).age_liquidation == annulation, generation
    general = next(pension for pension in simulateur.simuler(
        cas.construire(simulateur, 1959)).actuel.pensions_par_regime
        if pension.regime == "regime_general")
    salaire_annuel_moyen = float(re.search(r"SR ([\d,]+\.\d\d) €", general.detail)
                                 .group(1).replace(",", ""))
    assert salaire_annuel_moyen / 19_073.64 == pytest.approx(0.68, abs=0.01)
    assert "taux 50.000%" in general.detail


def test_l_ex_invalide_de_la_cnav_part_au_taux_plein_des_l_age_legal():
    """L'ex-invalide de la grille du coût (action 138, étape 7) : les nouveaux
    retraités de 2021 dont la pension de vieillesse remplace la pension
    d'invalidité, que la Cnav décrit (étude 2023-014, tableaux 2 à 4 et
    graphique 3) — 56 914 personnes : un premier trimestre l'année de leurs
    dix-huit ans, 171 trimestres en moyenne, dont 64 % cotisés, un salaire
    annuel moyen de 97 % du SMIC de 2021 (19 073,64 €). Le cas type travaille
    de dix-huit à quarante-cinq ans, puis touche une pension d'invalidité
    jusqu'au départ : 112 trimestres cotisés sur 176, 64 %. Son salaire de
    1,29 SMIC fait, né en 1959 et parti en 2021, le salaire annuel moyen
    publié, à un point près.

    La pension d'invalidité prend fin à l'âge légal, et la pension de vieillesse
    « allouée en cas d'inaptitude au travail » la remplace (L. 341-15, fiche
    ``pension_d_invalidite_substituee``) : le taux plein quelle que soit la
    durée (L. 351-8, 2°), à soixante ans né en 1950, à soixante-deux né en 1955
    et après, la réforme de 2023 lui gardant cet âge. Inactive au lieu
    d'invalide, la même carrière n'aurait que ses trimestres cotisés, et
    attendrait l'âge d'annulation de la décote, soixante-cinq puis soixante-sept
    ans."""
    import re
    from dataclasses import replace

    from retraite_notionnelle.castypes import EX_INVALIDE_CNAV as cas, cas_type_affiche

    simulateur = Simulateur(Parametres())
    assert not cas.inaptitude and cas.mortalite == "cnav_ex_invalide"
    assert cas_type_affiche(cas.code) == "smic_carriere_complete"
    assert (cas.affiliation, cas.age_debut, cas.niveau_salaire, cas.caisses) == (
        "salarie_prive_non_cadre", 18, 1.29, ("cnav",))
    inactif = replace(cas, interruptions_relatives=tuple(
        (decalage, "inactivite") for decalage, _ in cas.interruptions_relatives))
    for generation, depart, invalides, annulation in ((1950, 60, 56, 65), (1955, 62, 64, 67),
                                                      (1980, 62, 64, 67)):
        carriere = cas.construire(simulateur, generation)
        assert carriere.age_liquidation == depart, generation
        invalidite = carriere.pension_d_invalidite
        assert invalidite is not None and invalidite.debut.annee == generation + 46, generation
        trimestres: dict[str, int] = {}
        for ligne in carriere.lignes:
            if ligne.annee <= carriere.annee_liquidation:
                trimestres[ligne.type_periode] = (trimestres.get(ligne.type_periode, 0)
                                                  + ligne.trimestres_valides)
        assert trimestres == {"emploi": 112, "invalidite": invalides}, generation
        assert inactif.construire(simulateur, generation).age_liquidation == annulation, generation
    general = next(pension for pension in simulateur.simuler(
        cas.construire(simulateur, 1959)).actuel.pensions_par_regime
        if pension.regime == "regime_general")
    salaire_annuel_moyen = float(re.search(r"SR ([\d,]+\.\d\d) €", general.detail)
                                 .group(1).replace(",", ""))
    assert salaire_annuel_moyen / 19_073.64 == pytest.approx(0.97, abs=0.01)
    assert "taux 50.000%" in general.detail


# -- profil de rémunération ---------------------------------------------------


def test_le_passe_ne_depend_pas_de_l_age_de_depart():
    """Travailler plus longtemps ne doit pas réécrire les salaires d'avant.

    L'étalon de la déformation salariale a longtemps été la carrière de
    l'assuré, si bien qu'une même année civile se trouvait moins « avancée »
    dans une carrière plus longue, donc moins payée. Allonger sa carrière
    rabaissait alors son propre passé — de 5,2 % entre 60 et 67 ans en profil
    ascendant, de 8,4 % en fortement ascendant —, ce qui surestimait de quatre
    points le gain à travailler plus longtemps dans le système actuel, dont le
    salaire de référence ne retient que les meilleures années.

    L'étalon est désormais la carrière complète de la GÉNÉRATION, que l'assuré
    ne choisit pas. Le passé est donc strictement invariant, et ce test le dit
    sur les trois profils, y compris pour un départ au-delà du taux plein, où
    l'avancement plafonne.
    """
    simulateur = Simulateur(Parametres())
    for profil in ("plat", "ascendant", "fortement_ascendant"):
        passes = []
        for age in (58, 60, 64, 67, 70):
            carriere = simulateur.carriere_simple(
                annee_naissance=1975, sexe="H",
                affiliation="salarie_prive_non_cadre",
                age_debut=21, age_liquidation=age, profil_carriere=profil,
            )
            passes.append(sum(l.revenu for l in carriere.lignes if l.annee < 2026))
        assert passes[0] == pytest.approx(passes[-1]), profil
        assert all(p == pytest.approx(passes[0]) for p in passes), profil


# -- profil de rémunération -------------------------------------------------
# `profil_salaire` et `_facteur_secteur` s'éprouvent sur le portage :
# tests/js/profil-salaire.test.js (action 161, quatrième vague) ; la
# confrontation des deux jumeaux au bit près, dans test_facade_jumeau.py.


#: Les noms que tout objet de JavaScript hérite de son prototype.
NOMS_HERITES = ("constructor", "toString", "__proto__", "hasOwnProperty", "valueOf")

_NOMS_HERITES_JS = """
import { readFileSync } from "node:fs";
import {
  Carriere, bornesDeformation, chomageComplementaires, dispenseAssietteMinimale,
  forfaitMicro, profilDeLAffiliation, profilSalaire,
} from "./moteur/js/carriere.js";
import { DonneesMacro } from "./moteur/js/macro.js";
import { Affiliations } from "./moteur/js/regimes.js";
const noms = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("moteur/donnees.json", "utf8"));
const macro = new DonneesMacro(paquet);
const chomage = chomageComplementaires(paquet);
const affiliations = new Affiliations(paquet);
const lu = (calcul) => {
  try {
    const valeur = calcul();
    return ["valeur", typeof valeur === "function" ? "une fonction" : valeur ?? null];
  } catch (erreur) {
    return ["refus", erreur.constructor.name === "TypeError" ? erreur.message : ""];
  }
};
process.stdout.write(JSON.stringify(noms.map((nom) => ({
  profil: lu(() => profilSalaire(paquet, nom, 30, 2000)),
  bornes: lu(() => bornesDeformation(paquet, nom)),
  groupe: lu(() => profilDeLAffiliation(nom)),
  dispense: lu(() => dispenseAssietteMinimale(paquet, nom, "artisan", 2020)),
  nature: lu(() => chomage.nature(nom, 2000)),
  part: lu(() => chomage.partValidee(nom, 2000, nom)),
  solidarite: lu(() => chomage.tauxSolidarite(nom, 2000, true)),
  forfait: lu(() => forfaitMicro(macro, nom, 2020)),
  releve: lu(() => Carriere.depuisReleve({
    annee_naissance: 1960, sexe: "H", age_liquidation: 62, macro,
    releve: [{ annee: 2000, affiliation: "salarie_prive_non_cadre", revenu: 20000,
               trimestres: null, type_periode: "emploi" },
             { annee: 2001, affiliation: "salarie_prive_non_cadre", revenu: 20000,
               trimestres: null, type_periode: nom }],
  }).lignes.map((ligne) => [ligne.trimestres_valides, ligne.services_fonction_publique,
    ligne.services_plafond_trimestres_par_enfant, ligne.reputes_cotises_nature])),
  libelle: lu(() => affiliations.libelle(nom)),
  periodes: lu(() => affiliations.periodes(nom)),
  regimes: lu(() => affiliations.regimes(nom, 2000)),
}))));
"""


def _noms_herites_en_python(noms) -> list[dict]:
    """Ce que le Python rend sous chacun de ces noms, comme le lit le portage :
    une valeur, ou un refus — un ``ValueError`` ou un ``KeyError``, et jamais
    une ``TypeError``, qui serait une faute de programme."""
    from retraite_notionnelle.carriere import (
        Affiliations, Carriere, LigneRelevee, bornes_deformation, profil_de_l_affiliation)
    from retraite_notionnelle.donnees.chargement import (
        charger_chomage_complementaires, charger_cotisation_micro,
        charger_dispenses_assiette_minimale, dispense_assiette_minimale, forfait_micro)
    from retraite_notionnelle.donnees.macro import DonneesMacro

    macro = DonneesMacro(RACINE_DONNEES)
    chomage = charger_chomage_complementaires(RACINE_DONNEES)
    affiliations = Affiliations(RACINE_DONNEES)

    def lu(calcul):
        try:
            return ["valeur", calcul()]
        except (KeyError, ValueError):
            return ["refus", ""]

    def releve(nom):
        lignes = [LigneRelevee(2000, "salarie_prive_non_cadre", 20000.0),
                  LigneRelevee(2001, "salarie_prive_non_cadre", 20000.0, type_periode=nom)]
        return [[ligne.trimestres_valides, ligne.services_fonction_publique,
                 ligne.services_plafond_trimestres_par_enfant, ligne.reputes_cotises_nature]
                for ligne in Carriere.depuis_releve(1960, "H", lignes, 62, macro).lignes]

    return [{
        "profil": lu(lambda: profil_salaire(RACINE_DONNEES, nom, 30, 2000)),
        "bornes": lu(lambda: list(bornes_deformation(RACINE_DONNEES, nom))),
        "groupe": lu(lambda: profil_de_l_affiliation(nom)),
        "dispense": lu(lambda: dispense_assiette_minimale(
            charger_dispenses_assiette_minimale(RACINE_DONNEES), nom, "artisan", 2020)),
        "nature": lu(lambda: chomage.nature(nom, 2000)),
        "part": lu(lambda: chomage.part_validee(nom, 2000, nom)),
        "solidarite": lu(lambda: chomage.taux_solidarite(nom, 2000, True)),
        "forfait": lu(lambda: forfait_micro(charger_cotisation_micro(RACINE_DONNEES), nom, 2020)),
        "releve": lu(lambda: releve(nom)),
        "libelle": lu(lambda: affiliations.libelle(nom)),
        "periodes": lu(lambda: list(affiliations.periodes(nom))),
        "regimes": lu(lambda: list(affiliations.regimes(nom, 2000))),
    } for nom in noms]


def test_un_nom_herite_du_prototype_n_est_dans_aucune_table_du_portage():
    """Le portage lit ses tables dans des objets de JavaScript, qui héritent
    de leur prototype : ``constructor`` ou ``toString`` y sont des clés, que
    ``in`` et ``table[nom]`` trouvent ; le Python, qui lit des dictionnaires,
    ne les connaît pas. Sous un tel nom, le portage calculait un profil au lieu
    de le refuser, levait une ``TypeError`` sur une dispense, une part validée
    du chômage ou le forfait d'un micro-entrepreneur, donnait au chômage une
    nature qui est une fonction, et des trimestres NaN à l'année d'un relevé
    que le Python tient sans activité ; une affiliation de ce nom avait un
    libellé et des régimes. Aucune saisie n'y mène — la page ne laisse passer
    que les noms de ses listes, que ``contient`` vérifie —, mais le jumeau qui
    reste rend ce que rend le Python (action 161, étape 6)."""
    import json
    import shutil
    import subprocess
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _NOMS_HERITES_JS, json.dumps(NOMS_HERITES)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    portage = json.loads(execution.stdout)
    python = json.loads(json.dumps(_noms_herites_en_python(NOMS_HERITES)))
    ecarts = [f"{nom}, {lecture} : python={python[rang][lecture]} portage={valeur}"
              for rang, nom in enumerate(NOMS_HERITES)
              for lecture, valeur in portage[rang].items()
              if valeur != python[rang][lecture]]
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts)


# -- âge de référence --------------------------------------------------------
# Le cliquet, le défaut fixé à la bascule et l'écart d'anticipation
# s'éprouvent sur le portage : tests/js/age-reference.test.js (action 161,
# quatrième vague).


# -- conversion --------------------------------------------------------------
# Le diviseur, sa table, son taux anticipé et le mois du départ s'éprouvent
# sur le portage : tests/js/conversion.test.js (action 161, quatrième vague).


def test_la_population_ne_change_rien_au_scenario_1_et_baisse_les_notionnels():
    """Le garde-fou de l'action 14 : le défaut n'appartient pas au notionnel.
    Le scénario 1 sert la même pension quelle que soit la longévité — aucun
    diviseur ne l'a calculée —, et c'est pourquoi le transfert y est du même
    ordre. Les scénarios notionnels, eux, voient leur pension baisser sous la
    table de la population, de l'ordre de l'écart de diviseur."""
    from retraite_notionnelle.castypes import CAS_TYPES
    from retraite_notionnelle.simulateur import Simulateur

    cas = next(c for c in CAS_TYPES if c.code == "fonctionnaire_sedentaire")
    commun = Simulateur(Parametres(population_conversion=None))
    corrige = Simulateur(Parametres(population_conversion="fonctionnaires_civils_etat"))
    carriere = cas.construire(commun, 1975)
    avec, sans = commun.simuler(carriere), corrige.simuler(carriere)
    assert sans.actuel.pension_annuelle == avec.actuel.pension_annuelle
    rapport = (sans.notionnel_retroactif.pension_annuelle
               / avec.notionnel_retroactif.pension_annuelle)
    assert 0.92 < rapport < 0.97


def test_le_rattachement_par_la_pension_est_un_point_fixe():
    """Par la pension, le vingtile dépend de la pension qui dépend du diviseur.
    `Convertisseur.resoudre` itère jusqu'à ce que le vingtile de la pension
    servie soit celui qui l'a servie — ou, s'il oscille entre deux voisins,
    s'arrête au sixième tour, ce qui rend le résultat déterministe. Ce test
    tient le point fixe là où il existe, et vérifie que le rang parmi les
    retraités n'est pas le rang par le salaire : le SMIC à carrière
    complète, quatrième vingtile par le salaire, est au cinquième par sa
    pension. Le rang se lit parmi les retraités qui résident en France,
    ceux que décrivent les vingtiles de niveau de vie de l'INSEE : 57 %
    d'entre eux touchent moins de 1 500 € par mois, contre 59 % en comptant
    ceux qui vivent à l'étranger, dont la pension française est petite —
    c'est ce qui le faisait classer au sixième jusqu'au 23 septembre 2026."""
    from retraite_notionnelle.castypes import CAS_TYPES
    from retraite_notionnelle.simulateur import Simulateur

    par_salaire = Simulateur(Parametres())
    par_pension = Simulateur(Parametres(rattachement_niveau_de_vie="pension"))
    assert par_pension.convertisseur.rattache_par_pension
    assert not par_salaire.convertisseur.rattache_par_pension
    cas = next(c for c in CAS_TYPES if c.code == "smic_carriere_complete")
    carriere = cas.construire(par_salaire, 1975)
    resultat = par_pension.simuler(carriere).notionnel_retroactif_employeur
    retenue = resultat.conversion.table.split("_generation_")[1]
    attendue = par_pension.convertisseur.population_par_pension(
        resultat.pension_annuelle, carriere.annee_liquidation)
    # Le point fixe peut osciller entre deux vingtiles voisins — la pension
    # du sixième retombe au cinquième, qui la renvoie au sixième — ; le
    # dernier tour est alors retenu. Ici il est atteint : le vingtile de la
    # pension servie est celui qui l'a servie.
    assert retenue == "niveau_de_vie_v05"
    assert attendue == retenue
    assert par_pension.distribution.part_sous(1500.0) == pytest.approx(0.573, abs=0.005)
    salaire = par_salaire.simuler(carriere).notionnel_retroactif_employeur
    assert salaire.conversion.table.endswith("niveau_de_vie_v04")
    assert resultat.pension_annuelle < salaire.pension_annuelle


# -- fusion -----------------------------------------------------------------
# La fusion des régimes s'éprouve sur le portage, catalogue des fiches
# compris : tests/js/fusion.test.js (action 161, quatrième vague).


# -- le mois -----------------------------------------------------------------
# Le mois de la liquidation — sa date, l'origine des âges, le demi-mois,
# l'année du départ au prorata, ses trimestres, le relevé tronqué, le taux
# de remplacement annualisé, la circulaire du mois : tests/js/mois.test.js
# (action 161, quatrième vague).


# Le diviseur sous les trois hypothèses d'espérance de vie, et le capital
# rétroactif qu'elles ne touchent pas : tests/js/conversion.test.js.


def test_une_hypothese_d_esperance_de_vie_hors_de_l_insee_est_refusee(tmp_path):
    """Trois hypothèses, celles de l'INSEE ; une autre est refusée, et une
    variante dont la table manque aussi : elle retomberait sur la loi, calée
    sur les espérances de la centrale. La page Coût refuse une pyramide d'une
    autre hypothèse que celle de son simulateur (action 138, étape 7)."""
    import shutil

    with pytest.raises(ValueError, match="inconnue"):
        DonneesMortalite(RACINE_DONNEES, cache_disque=False, hypothese="moyenne")
    (tmp_path / "reference" / "mortalite").mkdir(parents=True)
    shutil.copy(RACINE_DONNEES / "reference" / "mortalite" / "esperances_vie.csv",
                tmp_path / "reference" / "mortalite")
    assert DonneesMortalite(tmp_path, cache_disque=False).annees_projetees is None
    with pytest.raises(FileNotFoundError, match="quotients_projetes_haute.csv"):
        DonneesMortalite(tmp_path, cache_disque=False, hypothese="haute")
    basse = Simulateur(Parametres(hypothese_esperance_vie="basse"))
    assert basse.pour_la_projection().parametres.hypothese_esperance_vie == "basse"
    with pytest.raises(ValueError, match="hypothèse d'espérance de vie"):
        Population(RACINE_DONNEES).verifier_hypothese("basse")


#: Trois carrières, que le portage simule sous les hypothèses basse et haute :
#: une salariée, un fonctionnaire, un artisan parti avant la bascule.
CARRIERES_DES_VARIANTES = (
    (1975, "F", "salarie_prive_non_cadre", 22, 64),
    (1990, "H", "fonctionnaire_etat", 24, 62.5),
    (1962, "H", "artisan", 20, 66),
)

_VARIANTES_JS = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { PARAMETRES_DEFAUT } from "./moteur/js/config.js";
import { DonneesMortalite } from "./moteur/js/mortalite.js";
const carrieres = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("moteur/donnees.json", "utf8"));
const contexte = new Contexte(paquet);
const sortie = { simulations: {} };
for (const hypothese of ["basse", "haute"]) {
  const simulateur = contexte.simulateur({ ...PARAMETRES_DEFAUT, hypothese_esperance_vie: hypothese });
  sortie.simulations[hypothese] = carrieres.map(([naissance, sexe, affiliation, debut, depart]) =>
    simulateur.simuler(simulateur.carriereSimple({
      annee_naissance: naissance, sexe, affiliation, age_debut: debut, age_liquidation: depart,
    })).dictionnaire());
}
try {
  new DonneesMortalite(paquet, undefined, "moyenne");
  sortie.refus = null;
} catch (erreur) {
  sortie.refus = erreur.message;
}
process.stdout.write(JSON.stringify(sortie));
"""


def test_le_portage_javascript_lit_les_memes_variantes():
    """Le portage simule trois carrières sous les hypothèses basse et haute :
    le navigateur refait les deux tables des écarts que le paquet porte
    (``quotientsProjetes``), et chaque simulateur lit celle de ses paramètres.
    Une hypothèse inconnue y est refusée comme en Python. Les simulations,
    vues identiques à ce que le moteur Python rendait, sont figées au témoin
    des valeurs (action 161, étape 8m)."""
    import json
    import shutil
    import subprocess
    from pathlib import Path

    from outils_valeurs import valeur_figee

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _VARIANTES_JS,
         json.dumps(CARRIERES_DES_VARIANTES)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    sortie = json.loads(execution.stdout)
    assert "inconnue" in sortie["refus"]
    simulations = sortie["simulations"]
    assert [len(simulations[h]) for h in ("basse", "haute")] == [3, 3]
    assert simulations["basse"] != simulations["haute"]
    assert valeur_figee("simulations des variantes", simulations) == simulations


# -- le cœur notionnel, recomposé sans le moteur ------------------------------


def test_le_compte_notionnel_se_recompose_a_la_main():
    """Le capital, la pension et le diviseur, recalculés ici par leur définition.

    Jusqu'au 23 septembre 2026, aucun test ne contrôlait le cœur notionnel
    autrement que par des instantanés : une année de revalorisation en moins,
    un capital multiplié par 0,95 ne faisaient échouer que des témoins, que
    l'on régénère. Ce test écrit la règle et la confronte au moteur :

    - chaque année de la carrière, de la première à celle de la liquidation
      incluse, porte sa ligne de cotisation ;
    - une cotisation versée l'année t est revalorisée des taux des années t+1
      à la liquidation incluse — le produit est écrit ici, sans passer par
      ``Indexation.coefficient`` ;
    - la pension est le capital divisé par le diviseur ;
    - à taux d'actualisation nul, le diviseur est l'espérance de vie
      résiduelle, que ``test_mortalite`` confronte aux tables publiées.
    """
    simulateur = Simulateur(Parametres())
    carriere = simulateur.carriere_simple(
        annee_naissance=1975, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=64, niveau_salaire=0.9,
    )
    resultat = simulateur.simuler(carriere).notionnel_retroactif_employeur
    compte = resultat.compte
    liquidation = compte.annee_liquidation
    annees = [ligne.annee for ligne in compte.cotisations]
    # Jusqu'à la liquidation incluse quand la carrière y porte des mois — une
    # liquidation au 1er janvier n'en porte aucun.
    fin = min(liquidation, carriere.derniere_annee)
    assert annees == list(range(carriere.premiere_annee, fin + 1))

    indexation = simulateur.indexation
    attendu = 0.0
    for ligne in compte.cotisations:
        facteur = 1.0
        for annee in range(ligne.annee + 1, liquidation + 1):
            facteur *= 1.0 + indexation.taux(annee).taux
        attendu += ligne.cotisation * facteur
    assert compte.capital == pytest.approx(attendu, rel=1e-12)
    assert compte.capital > 0.0

    conversion = resultat.conversion
    assert resultat.pension_annuelle == pytest.approx(compte.capital / conversion.diviseur)
    # Un taux d'actualisation positif rend le diviseur plus petit que
    # l'espérance de vie résiduelle ; nul, il lui est égal.
    assert conversion.taux_anticipe >= 0.0
    assert conversion.diviseur <= conversion.esperance_residuelle + 1e-9
    sans_actualisation = Convertisseur(
        simulateur.mortalite,
        Parametres(taux_anticipe_conversion=0.0),
    ).coefficient(conversion.age_liquidation, conversion.annee_liquidation,
                  None, carriere.mois_liquidation)
    assert sans_actualisation.diviseur == pytest.approx(
        sans_actualisation.esperance_residuelle)


@pytest.mark.parametrize("nom,source,cumul", [
    ("un cadre, aux taux historiques", SourceCotisations.TAUX_HISTORIQUES, False),
    ("deux activités cumulées", SourceCotisations.TAUX_HISTORIQUES, True),
    ("un taux d'acquisition commun", SourceCotisations.TAUX_UNIFORME, False),
])
def test_le_capital_se_partage_entre_ceux_qui_ont_encaisse(nom, source, cumul):
    """Chaque cotisation garde le régime qui l'a encaissée, et le capital se
    partage entre eux sans reste : c'est ce que « Le détail du calcul »
    affiche, régime par régime.

    Avant la bascule, les régimes en répartition du routage — ou le taux
    commun, qui réunit leurs assiettes et n'appartient à aucun ; depuis, le
    seul régime unique. Un régime provisionné n'y est jamais : ce qu'il
    encaisse ne rejoint pas le compte.
    """
    simulateur = Simulateur(Parametres())
    metiers = [Metier(affiliation="salarie_prive_cadre", age_debut=22.0,
                      niveau_salaire=1.4)]
    if cumul:
        metiers.append(Metier(affiliation="medecin_liberal", age_debut=35.0,
                              niveau_salaire=0.8, cumul=True))
    carriere = simulateur.carriere_parcours(
        annee_naissance=1972, sexe="F", metiers=metiers, age_liquidation=65.0)
    constructeur = ConstructeurCompte(
        simulateur.macro, simulateur.catalogue, simulateur.affiliations,
        simulateur.indexation, simulateur.parametres.avec(source_cotisations=source))
    fusionne = simulateur.regime_fusionne
    compte = constructeur.construire(carriere, carriere.annee_liquidation,
                                     carriere.premiere_annee, fusionne)

    for ligne in compte.cotisations:
        assert sum(montant for _, montant in ligne.par_regime) == pytest.approx(
            ligne.cotisation, rel=1e-12, abs=1e-9), (nom, ligne.annee)
        codes = {code for code, _ in ligne.par_regime}
        if ligne.annee >= fusionne.annee_bascule:
            assert codes <= {"regime_unifie"}, (nom, ligne.annee, codes)
        elif source is SourceCotisations.TAUX_UNIFORME:
            assert codes <= {"taux_commun"}, (nom, ligne.annee, codes)
        else:
            assert codes <= set(ligne.regimes), (nom, ligne.annee, codes)
            assert not any(simulateur.catalogue[code].hors_repartition
                           for code in codes), (nom, ligne.annee, codes)
    assert sum(compte.capital_par_regime.values()) == pytest.approx(
        compte.capital, rel=1e-12)
    assert compte.capital_par_regime["regime_unifie"] > 0.0
    if cumul:
        assert {"regime_general", "cnavpl"} <= compte.capital_par_regime.keys()

