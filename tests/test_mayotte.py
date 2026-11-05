"""Mayotte : la caisse de sécurité sociale de Mayotte et son régime de retraite
des salariés (fiche ``cssm_mayotte``), dans les deux moteurs (action 177,
étape 3).

LA VALIDATION DES TRIMESTRES. « Pour le calcul de la durée d'assurance, il y a
lieu de retenir autant de trimestres que le salaire annuel correspondant aux
retenues subies par l'assuré sur sa rémunération représente de fois le montant
du salaire minimum garanti en vigueur à Mayotte au 1er janvier de l'année
considérée, calculé sur la base de 200 heures, avec un maximum de quatre
trimestres par année civile » (décret n° 87-175 du 16 mars 1987, article 3,
LEGIARTI000006770151 ; décret n° 2003-589 du 1er juillet 2003, article 8,
LEGIARTI000006781027 et LEGIARTI000026514455). « Pour les périodes
postérieures au 31 décembre 2016 », 150 heures (rédaction du 26 septembre
2016, LEGIARTI000033155442) ; depuis 2018, du « salaire minimum de croissance
en vigueur à Mayotte » (rédaction du 22 octobre 2023, LEGIARTI000048241292).
Le Smig du 1er janvier est celui des barèmes de la Cnav, depuis 2002
(``legislation/mayotte_smig_et_plafond.csv``) : le modèle validait au Smic
national.

LE PLAFOND. « Le salaire servant au calcul de la pension est le salaire annuel
moyen déterminé à partir des vingt-cinq meilleurs salaires annuels reportés au
compte de l'assuré dans la limite du plafond annuel de cotisations mentionné
au II de l'article 19 de l'ordonnance du 27 mars 2002 » (décret n° 2003-589,
article 7, LEGIARTI000006781026, LEGIARTI000026514457, LEGIARTI000033155445) :
celui de la caisse de sécurité sociale de Mayotte, que l'article 21 fixe à
825 € par mois en 2003, puis à 1 070 € en 2011, revalorisé chaque année
comme le plafond de la métropole « majoré de cinq points et un dixième »
(LEGIARTI000006781041, LEGIARTI000026514398), et que la même série porte
depuis 2005, première année entière du barème de la Cnav. Le modèle
plafonnait au plafond de la Sécurité sociale.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import AnneeCarriere, Carriere, LigneRelevee
from retraite_notionnelle.droit import liquider
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
STATUT = "salarie_mayotte"
#: Le travailleur non salarié de Mayotte, artisan ou commerçant, affilié à la
#: même caisse depuis le 1er juillet 2012 (action 177, étape 8).
INDEPENDANT = "independant_mayotte"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


#: Le jumeau JavaScript : les lignes de chaque relevé, et le résultat entier.
_JUMEAU = """
import { readFileSync } from "node:fs";
import { Simulateur } from "./moteur/js/simulateur.js";
const cas = JSON.parse(process.argv[1]);
const simulateur = new Simulateur(JSON.parse(readFileSync("./moteur/donnees.json", "utf8")));
const sortie = cas.map(({ releve, naissance, age }) => {
  const carriere = simulateur.carriereReleve({
    annee_naissance: naissance, sexe: "F", releve, age_liquidation: age });
  return {
    lignes: carriere.lignes.map((l) => [l.annee, l.trimestres_valides, l.revenu,
      l.assiette_minimale_base]),
    resultat: simulateur.simuler(carriere).dictionnaire(),
  };
});
process.stdout.write(JSON.stringify(sortie));
"""


def _ecarts(obtenu, attendu, chemin="") -> list[str]:
    """Ce qui sépare le JavaScript du Python, à 1e-9 près en relatif."""
    if attendu is None:
        return []
    if isinstance(attendu, dict):
        if not isinstance(obtenu, dict):
            return [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]
        return [e for cle, v in attendu.items()
                for e in _ecarts(obtenu.get(cle), v, f"{chemin}.{cle}")]
    if isinstance(attendu, list):
        if not isinstance(obtenu, list) or len(obtenu) != len(attendu):
            return [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]
        return [e for rang, v in enumerate(attendu)
                for e in _ecarts(obtenu[rang], v, f"{chemin}[{rang}]")]
    if isinstance(attendu, bool) or not isinstance(attendu, (int, float)):
        return [] if obtenu == attendu else [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]
    if obtenu is None or abs(obtenu - attendu) > 1e-9 * max(1.0, abs(attendu)):
        return [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]
    return []


@pytest.fixture
def deux_moteurs(simulateur):
    """Ce qui rend les lignes de chaque relevé, par année, en Python, une fois
    vérifié que le JavaScript rend les mêmes lignes et le même résultat entier.
    Une fixture, et non une fonction : la garde des présomptions saute les
    tests qui la demandent, `"node"` lu dans sa source (`tests/conftest.py`)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    sys.path.insert(0, str(RACINE / "scripts"))
    from construire_temoins import _fini

    def confronter(cas) -> list[dict]:
        attendus, lignes = [], []
        for c in cas:
            carriere = simulateur.carriere_releve(
                c["naissance"], "F", [LigneRelevee(**ligne) for ligne in c["releve"]],
                c["age"])
            lignes.append({ligne.annee: ligne for ligne in carriere.lignes})
            attendus.append({
                "lignes": [[l.annee, l.trimestres_valides, l.revenu, l.assiette_minimale_base]
                           for l in carriere.lignes],
                "resultat": _fini(simulateur.simuler(carriere).dictionnaire())})
        execution = subprocess.run(
            ["node", "--input-type=module", "-e", _JUMEAU, json.dumps(cas)],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
        assert execution.returncode == 0, execution.stderr[-2000:]
        ecarts = _ecarts(json.loads(execution.stdout), attendus)
        assert not ecarts, ecarts[:10]
        return lignes

    return confronter


def test_un_trimestre_se_valide_a_mayotte_au_smig_mahorais(deux_moteurs):
    """Le salaire qui valide un trimestre, à Mayotte : 200 heures du Smig
    mahorais du 1er janvier jusqu'en 2016, 150 depuis 2017. En 2002, 1 100 €
    font deux trimestres à 200 heures de 2,71 €, 542 €, et aucun au Smic
    national, 1 334 € ; en 2010, 4 750 € en font quatre à 1 186 € (5,93 €), deux
    à 1 772 € ; en 2016, 2 910 € n'en font qu'un à 1 460 € (7,30 €), quand
    150 heures du Smic national, 1 450,50 €, en feraient deux ; en 2017,
    2 220 € en font deux à 150 heures de 7,37 €, 1 105,50 €, un à 1 464 € ; en
    2025, 5 400 € en font quatre à 1 347 € (8,98 €), trois à 1 782 €. Dans les
    deux moteurs."""
    [mahoraise] = deux_moteurs([
        {"naissance": 1960, "age": 66.0, "releve": [
            {"annee": annee, "affiliation": STATUT, "revenu": revenu}
            for annee, revenu in ((2002, 1100.0), (2010, 4750.0), (2016, 2910.0),
                                  (2017, 2220.0), (2025, 5400.0))]}])
    assert {annee: mahoraise[annee].trimestres_valides
            for annee in (2002, 2010, 2016, 2017, 2025)} == {
        2002: 2, 2010: 4, 2016: 1, 2017: 2, 2025: 4}


#: Le plafond annuel de la caisse de sécurité sociale de Mayotte, au barème de
#: la Cnav « Salaire plafond - Mayotte » : 912 € par mois du 1er juillet 2004 au
#: 31 décembre 2010, 1 070 € en 2011 — le montant de l'article 21 —, 1 492 € en
#: 2016, 1 934 € en 2020 et 2 644 € en 2024.
PLAFONDS_DE_LA_CAISSE = {2005: 10_944.0, 2011: 12_840.0, 2016: 17_904.0,
                         2020: 23_208.0, 2024: 31_728.0}


def _salariee_a_25_000_euros() -> Carriere:
    """Une salariée de Mayotte née en 1961, partie à soixante-quatre ans en
    2025, à 25 000 € chacune des années de ``PLAFONDS_DE_LA_CAISSE``."""
    return Carriere.depuis_lignes(
        1961, "F", [AnneeCarriere(annee=annee, revenu=25_000.0, affiliation=STATUT,
                                  trimestres_valides=4) for annee in PLAFONDS_DE_LA_CAISSE],
        age_liquidation=64)


def test_le_salaire_annuel_moyen_de_mayotte_s_ecrete_au_plafond_de_la_caisse(simulateur):
    """Cinq années à 25 000 € : chacune s'écrête au plafond de la caisse de son
    année, 10 944 € en 2005, 23 208 € en 2020, que le plafond de la Sécurité
    sociale, de 30 192 € à 46 368 €, laissait entière ; celle de 2024 le reste,
    sous 31 728 €. Moins de vingt-cinq années : le salaire annuel moyen les
    prend toutes, revalorisées à la date d'effet."""
    macro = simulateur.macro
    carriere = _salariee_a_25_000_euros()
    liquidation = carriere.annee_liquidation
    assert liquidation == 2025
    assert all(macro.plafond_securite_sociale(annee) > 25_000.0
               for annee in PLAFONDS_DE_LA_CAISSE)
    attendu = sum(
        min(25_000.0, plafond) * macro.coefficient_revalorisation_portee_au_compte(
            annee, liquidation, carriere.mois_liquidation)
        for annee, plafond in PLAFONDS_DE_LA_CAISSE.items()) / len(PLAFONDS_DE_LA_CAISSE)
    periode = simulateur.catalogue["cssm_mayotte"].periode(liquidation)
    assert liquider.salaire_de_reference(
        simulateur.scenario_actuel, "cssm_mayotte", carriere, periode, liquidation,
        True, 1961) == pytest.approx(attendu, rel=1e-12)


def test_les_deux_moteurs_plafonnent_au_plafond_de_la_caisse(deux_moteurs):
    """La même salariée, sur son relevé : le portage rend les mêmes lignes et le
    même résultat entier, sa pension de Mayotte comprise."""
    deux_moteurs([{"naissance": 1961, "age": 64.0, "releve": [
        {"annee": annee, "affiliation": STATUT, "revenu": 25_000.0}
        for annee in PLAFONDS_DE_LA_CAISSE]}])


def test_l_independant_de_mayotte_valide_ses_trimestres_au_smic_de_mayotte(
        deux_moteurs, simulateur):
    """« Les résidents à Mayotte ayant la qualité de travailleurs non salariés
    des professions artisanales, industrielles et commerciales, et agricoles
    sont affiliés obligatoirement au régime de retraite de base obligatoire de
    sécurité sociale défini à l'article 5 » (ordonnance n° 2002-411, article
    23-1, LEGIARTI000025021004), depuis le 1er juillet 2012 (article 23-4, II,
    LEGIARTI000025021012), et « le droit à pension de vieillesse des
    travailleurs non salariés est déterminé selon les dispositions prévues au
    chapitre Ier » (article 23-4, I) : ses trimestres se valident comme ceux du
    salarié, au salaire minimum de Mayotte (décret n° 2003-589, article 8). La
    Cnav l'écrit pour 2025 : « le salaire ou revenu cotisé à retenir en 2025
    est de 1 347 euros pour la validation d'un trimestre » et, « concernant les
    travailleurs indépendants, le montant de cotisations à retenir », 135 €
    pour un trimestre et 541 € pour quatre (circulaire n° 2025-04 du
    20 janvier 2025), 10,05 % de ces revenus, le taux de 2025 (décret
    n° 2011-2085, article 4-2, LEGIARTI000038680068). En 2013, 2 800 € font
    deux trimestres à 200 heures de 6,96 €, 1 392 €, un seul au seuil de la
    métropole, 1 886 € ; en 2017, 2 220 € en font deux à 150 heures de 7,37 €,
    un à 1 464 € ; en 2025, 5 400 €, qui font 542,70 € de cotisations, en
    font quatre, trois à 1 782 €. Sa pension vient de la caisse de Mayotte,
    et il paie seul : aucune part d'employeur. Dans les deux moteurs."""
    releve = [{"annee": annee, "affiliation": INDEPENDANT, "revenu": revenu}
              for annee, revenu in ((2013, 2800.0), (2017, 2220.0), (2025, 5400.0))]
    [artisane] = deux_moteurs([{"naissance": 1965, "age": 64.0, "releve": releve}])
    assert {annee: artisane[annee].trimestres_valides for annee in (2013, 2017, 2025)} == {
        2013: 2, 2017: 2, 2025: 4}
    resultat = simulateur.simuler(simulateur.carriere_releve(
        1965, "F", [LigneRelevee(**ligne) for ligne in releve], 64.0)).dictionnaire()
    assert [part["regime"] for part in resultat["scenarios"]["actuel"]["par_regime"]] == [
        "cssm_mayotte"]
    assert resultat["contribution_employeur"]["employeur"] == 0.0


def test_l_independant_de_mayotte_cotise_au_moins_sur_450_heures_du_smic_de_mayotte(
        deux_moteurs):
    """« Elle ne peut être calculée sur une assiette inférieure à 450 fois le
    salaire horaire minimum interprofessionnel de croissance applicable à
    Mayotte prévu à l'article L. 3231-2 du code du travail » (décret
    n° 2011-2085, article 4-2, I, LEGIARTI000038680068), pour « les cotisations
    de sécurité sociale dues au titre des périodes courant à compter du
    1er janvier 2019 » (décret n° 2019-632, article 2, LEGIARTI000038680034).
    L'artisane qui déclare 1 000 € cotise en 2019 sur 450 heures de 7,57 €,
    3 406,50 €, et en 2025 de 8,98 €, 4 041 € : trois trimestres, à 150 heures
    du même Smic, au lieu d'aucun ; au Smic de la métropole, l'assiette serait
    de 4 513,50 € et de 5 346 €. En 2018, aucun minimum : 1 000 € ne font aucun
    trimestre, sous 1 119 €. Dans les deux moteurs."""
    [artisane] = deux_moteurs([{"naissance": 1965, "age": 64.0, "releve": [
        {"annee": annee, "affiliation": INDEPENDANT, "revenu": 1000.0}
        for annee in (2018, 2019, 2025)]}])
    assert artisane[2018].assiette_minimale_base == 0.0
    assert artisane[2019].assiette_minimale_base == pytest.approx(3406.50)
    assert artisane[2025].assiette_minimale_base == pytest.approx(4041.0)
    assert [artisane[annee].trimestres_valides for annee in (2018, 2019, 2025)] == [0, 3, 3]


def test_depuis_2026_l_assiette_minimale_de_mayotte_veut_quatre_vingt_dix_jours(simulateur):
    """« L'assiette minimale s'applique aux travailleurs indépendants dont la
    durée d'affiliation est au moins égale à quatre-vingt-dix jours au cours de
    l'année considérée » (article 4-2, I, dans la rédaction du décret
    n° 2026-82, du 1er janvier 2026, LEGIARTI000053297541) : deux mois
    d'activité en 2026 n'en portent pas ; trois en portent une entière,
    450 heures de 9,33 €, 4 198,50 €, que le texte ne réduit pas ; en 2025, deux
    mois en portaient une."""
    from retraite_notionnelle.donnees.chargement import (
        assiette_minimale, charger_assiettes_minimales)

    table = charger_assiettes_minimales(simulateur.macro.racine)
    regle_2026 = assiette_minimale(table, INDEPENDANT, 2026)
    regle_2025 = assiette_minimale(table, INDEPENDANT, 2025)
    assert regle_2026 is not None and regle_2025 is not None
    assert regle_2026.montant(48_060.0, 9.33, 59 / 365) == 0.0
    assert regle_2026.montant(48_060.0, 9.33, 92 / 365) == pytest.approx(4198.50)
    assert regle_2025.montant(47_100.0, 8.98, 59 / 365) == pytest.approx(4041.0)


#: Le taux de la cotisation d'assurance vieillesse de base de l'indépendant de
#: Mayotte, « pour chaque année civile de 2019 à 2036, conformément au tableau
#: suivant » (décret n° 2011-2085, article 4-2, I, LEGIARTI000038680068, créé
#: par le décret n° 2019-632 pour « les périodes courant à compter du
#: 1er janvier 2019 », puis LEGIARTI000053297541 au 1er janvier 2026, qui garde
#: le tableau), assise sur le revenu « dans la limite du plafond » : aucune part
#: sur la totalité du revenu.
TAUX_DE_L_INDEPENDANT = {2019: 0.0585, 2020: 0.0655, 2021: 0.0725, 2022: 0.0795,
                         2023: 0.0865, 2024: 0.0935, 2025: 0.1005, 2026: 0.1075}


def test_l_independant_de_mayotte_cotise_au_taux_de_l_article_4_2(simulateur):
    """Chaque année depuis 2019, la période de la caisse porte le taux propre de
    l'assuré sans employeur à côté de ceux du salarié, qu'il ne remplace pas ;
    en 2018, aucun texte lu ne lui en donne un."""
    regime = simulateur.catalogue["cssm_mayotte"]
    for annee, taux in TAUX_DE_L_INDEPENDANT.items():
        (periode,) = [p for p in regime.periodes_actives(annee) if p.assiette == "plafonnee"]
        assert periode.taux_du_cotisant(True) == pytest.approx((taux, 0.0)), annee
        assert periode.taux_du_cotisant(False) == (
            periode.taux_cotisation_retraite, periode.taux_cotisation_deplafonnee)
    (avant,) = [p for p in regime.periodes_actives(2018) if p.assiette == "plafonnee"]
    assert avant.taux_du_cotisant(True) == avant.taux_du_cotisant(False)


@pytest.fixture
def compte_en_deux_moteurs(simulateur):
    """Ce que le compte du droit en vigueur porte à chaque régime une année de
    la carrière, au centime, en Python, une fois vérifié que le JavaScript
    porte la même chose. Une fixture, pour la garde des présomptions."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    script = """
import { readFileSync } from "node:fs";
import { AnneeCarriere, Carriere } from "./moteur/js/carriere.js";
import { Contexte } from "./moteur/js/contexte.js";
const contexte = new Contexte(JSON.parse(readFileSync("moteur/donnees.json", "utf8")));
const simulateur = contexte.simulateur();
const [naissance, lignes, annee] = JSON.parse(process.argv[1]);
const carriere = new Carriere({
  ...naissance, lignes: lignes.map((ligne) => new AnneeCarriere(ligne)) });
process.stdout.write(JSON.stringify(
  simulateur.constructeurEmployeur.cotisationAnnuelle(carriere, annee).par_regime));
"""

    def compte(naissance: dict, lignes: list[dict], annee: int) -> dict[str, float]:
        carriere = Carriere(**naissance, lignes=[AnneeCarriere(**l) for l in lignes])
        obtenu = {code: round(montant, 2) for code, montant in
                  simulateur.constructeur_employeur.cotisation_annuelle(
                      carriere, annee).par_regime}
        execution = subprocess.run(
            ["node", "--input-type=module", "-e", script,
             json.dumps([naissance, lignes, annee])],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
        assert execution.returncode == 0, execution.stderr[-2000:]
        assert {code: round(montant, 2)
                for code, montant in json.loads(execution.stdout)} == obtenu
        return obtenu

    return compte


def test_le_compte_porte_ce_que_l_independant_de_mayotte_a_verse(compte_en_deux_moteurs):
    """L'artisane de Mayotte à 10 000 € par an, sous le plafond de la caisse
    (23 208 € en 2020, 31 728 € en 2024) et au-dessus de son assiette
    minimale : son compte reçoit 5,85 % de 10 000 €, 585 €, en 2019, et
    9,35 %, 935 €, en 2024 — non les 15,45 % et 2,30 % du salarié et de son
    employeur au régime général, 1 775 € en 2019. Dans les deux moteurs."""
    naissance = dict(annee_naissance=1965, sexe="F", jour_naissance=15, age_liquidation=64.0)
    lignes = [dict(annee=annee, revenu=10_000.0, affiliation=INDEPENDANT,
                   trimestres_valides=4) for annee in range(2019, 2025)]
    assert compte_en_deux_moteurs(naissance, lignes, 2019) == {"cssm_mayotte": 585.0}
    assert compte_en_deux_moteurs(naissance, lignes, 2024) == {"cssm_mayotte": 935.0}


def test_l_independant_de_mayotte_cotise_sous_le_plafond_de_sa_caisse(
        compte_en_deux_moteurs):
    """L'article 4-2 assied la cotisation « dans la limite du plafond prévu au I
    de l'article 28-1 » de l'ordonnance n° 96-1122, le plafond de cotisations
    « créé à Mayotte », et non celui de la Sécurité sociale. 30 000 € en 2020 :
    23 208 € × 6,55 % = 1 520,12 €, non 30 000 € × 6,55 % = 1 965 € ;
    50 000 € en 2024 : 31 728 € × 9,35 % = 2 966,57 €, non 46 368 € × 9,35 %
    = 4 335,41 €. Dans les deux moteurs."""
    naissance = dict(annee_naissance=1965, sexe="F", jour_naissance=15, age_liquidation=64.0)
    lignes = [dict(annee=annee, revenu=revenu, affiliation=INDEPENDANT, trimestres_valides=4)
              for annee, revenu in ((2020, 30_000.0), (2024, 50_000.0))]
    assert compte_en_deux_moteurs(naissance, lignes, 2020) == {"cssm_mayotte": 1520.12}
    assert compte_en_deux_moteurs(naissance, lignes, 2024) == {"cssm_mayotte": 2966.57}


def test_la_fiche_de_paie_de_l_independant_de_mayotte_preleve_son_taux(simulateur):
    """10 000 € de revenu en 2019 : 585 € de vieillesse de base, à la seule
    charge de l'assuré."""
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.remuneration import (
        ConstructeurFiche, bloc_droit_en_vigueur, charger_prelevements, smic_annuel)

    bloc = bloc_droit_en_vigueur(simulateur.catalogue, simulateur.affiliations,
                                 INDEPENDANT, 2019, macro=simulateur.macro)
    profil = charger_prelevements(RACINE_DONNEES).profil("independant")
    fiche = ConstructeurFiche(profil).fiche(
        2019, 10_000.0, simulateur.macro.plafond_securite_sociale(2019),
        smic_annuel(simulateur.macro, 2019), bloc)
    retraite = {ligne.code: (ligne.salarie, ligne.employeur)
                for ligne in fiche.lignes if ligne.retraite}
    assert retraite == {"cssm_mayotte": (pytest.approx(585.0), 0.0)}


def test_la_fiche_de_paie_de_l_independant_de_mayotte_s_arrete_au_plafond_de_sa_caisse(
        simulateur):
    """30 000 € de revenu en 2020, au-dessus du plafond de la caisse (23 208 €)
    et sous celui de la Sécurité sociale (41 136 €) : 23 208 € × 6,55 % =
    1 520,12 €, à la seule charge de l'assuré, dans les deux moteurs."""
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.remuneration import (
        ConstructeurFiche, bloc_droit_en_vigueur, charger_prelevements, smic_annuel)

    macro = simulateur.macro
    bloc = bloc_droit_en_vigueur(simulateur.catalogue, simulateur.affiliations,
                                 INDEPENDANT, 2020, macro=macro)
    profil = charger_prelevements(RACINE_DONNEES).profil("independant")
    fiche = ConstructeurFiche(profil).fiche(
        2020, 30_000.0, macro.plafond_securite_sociale(2020), smic_annuel(macro, 2020), bloc)
    retraite = {ligne.code: (round(ligne.salarie, 2), ligne.employeur)
                for ligne in fiche.lignes if ligne.retraite}
    assert retraite == {"cssm_mayotte": (1520.12, 0.0)}
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    script = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { ConstructeurFiche, blocDroitEnVigueur, smicAnnuel } from "./moteur/js/remuneration.js";
const contexte = new Contexte(JSON.parse(readFileSync("moteur/donnees.json", "utf8")));
const simulateur = contexte.simulateur();
const macro = simulateur.macro;
const bloc = blocDroitEnVigueur(simulateur.catalogue, simulateur.affiliations,
  "independant_mayotte", 2020, 0.0, macro);
const profil = simulateur.baremePrelevements.profil("independant");
const fiche = new ConstructeurFiche(profil).fiche(
  2020, 30000, macro.plafond_securite_sociale.valeur(2020), smicAnnuel(macro, 2020), bloc);
process.stdout.write(JSON.stringify(fiche.lignes.filter((l) => l.retraite)
  .map((l) => [l.code, Math.round(l.salarie * 100) / 100, l.employeur])));
"""
    execution = subprocess.run(["node", "--input-type=module", "-e", script], cwd=RACINE,
                               capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    assert json.loads(execution.stdout) == [["cssm_mayotte", 1520.12, 0.0]]


#: Les deux rédactions de l'article 4-2, I, telles que l'index LEGI les porte,
#: raccourcies de ce que le lecteur ne lit pas : la note d'application, le
#: tableau de la vieillesse, et le II, que le lecteur ne doit pas prendre.
REDACTIONS_4_2 = [
    ("LEGIARTI000038680068", "2019-06-25",
     "Conformément aux dispositions de l'article 2 du décret n° 2019-632 du 24 juin "
     "2019, ces dispositions s'appliquent aux cotisations de sécurité sociale dues au "
     "titre des périodes courant à compter du 1er janvier 2019. I.-La cotisation "
     "annuelle d'assurance vieillesse de base due par les travailleurs indépendants, "
     "mentionnée au 1° du I de l'article 28-2 de l'ordonnance du 20 décembre 1996 "
     "susvisée, est assise sur le revenu d'activité, tel que défini au II de "
     "l'article 28-1 de la même ordonnance, dans la limite du plafond prévu au I de "
     "l'article 28-1 de l'ordonnance du 20 décembre 1996 susvisée. Le taux de cette "
     "cotisation est fixé, pour chaque année civile de 2019 à 2036, conformément au "
     "tableau suivant : Année Cotisation au régime d'assurance vieillesse obligatoire "
     "de base 2019 5,85 % 2020 6,55 % 2021 7,25 % 2022 7,95 % 2023 8,65 % 2024 9,35 % "
     "2025 10,05 % 2026 10,75 % 2027 11,45 % 2028 12,15 % 2029 12,85 % 2030 13,55 % "
     "2031 14,25 % 2032 14,95 % 2033 15,65 % 2034 16,35 % 2035 17,05 % 2036 17,75 % "
     "II.-La cotisation d'assurance maladie-maternité due par les travailleurs "
     "indépendants [...] Année Cotisation d'assurance maladie-maternité 2019 2,10 % "
     "2020 2,40 %"),
    ("LEGIARTI000053297541", "2026-01-01",
     "I.-La cotisation annuelle d'assurance vieillesse de base due par les travailleurs "
     "indépendants [...] dans la limite du plafond prévu au I de l'article 28-1 de "
     "l'ordonnance du 20 décembre 1996 susvisée. [...] L'assiette minimale s'applique "
     "aux travailleurs indépendants dont la durée d'affiliation est au moins égale à "
     "quatre-vingt-dix jours au cours de l'année considérée. Le taux de cette "
     "cotisation est fixé, pour chaque année civile de 2019 à 2036, conformément au "
     "tableau suivant : Année Cotisation au régime d'assurance vieillesse obligatoire "
     "de base 2019 5,85 % 2020 6,55 % 2021 7,25 % 2022 7,95 % 2023 8,65 % 2024 9,35 % "
     "2025 10,05 % 2026 10,75 % 2027 11,45 % 2028 12,15 % 2029 12,85 % 2030 13,55 % "
     "2031 14,25 % 2032 14,95 % 2033 15,65 % 2034 16,35 % 2035 17,05 % 2036 17,75 % "
     "II.-La cotisation d'assurance maladie-maternité [...] 2019 2,10 %"),
]


def _recuperateur():
    import importlib.util

    nom = "dila_legi_taux_mayotte"
    chemin = RACINE / "scripts" / "fetch" / f"{nom}.py"
    specification = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules[nom] = module
    specification.loader.exec_module(module)
    return module


def test_le_taux_se_lit_dans_les_redactions_de_l_article_4_2():
    """Le récupérateur lit le tableau du I, et lui seul, date la première
    rédaction au 1er janvier 2019, la date d'application qu'elle écrit, et rend
    chaque année depuis 2019 le taux que la table certifie, sans part sur la
    totalité."""
    recuperateur = _recuperateur()
    redactions = [recuperateur.lire_redaction(*r) for r in REDACTIONS_4_2]
    assert [r["application"] for r in redactions] == ["2019-01-01", "2026-01-01"]
    assert redactions[0]["plafonne"][2036] == 0.1775
    serie = recuperateur.series(redactions)
    lues = {int(a): (t["plafonne"], t["deplafonne"], t["article"]) for a, t in serie.items()}
    assert min(lues) == 2019
    for annee, taux in TAUX_DE_L_INDEPENDANT.items():
        article = "LEGIARTI000053297541" if annee >= 2026 else "LEGIARTI000038680068"
        assert lues[annee] == (taux, 0.0, article), annee


def test_une_redaction_de_l_article_4_2_illisible_arrete_le_recuperateur():
    """Rien n'est écrit plutôt qu'un taux deviné : ni un tableau absent, ni une
    cotisation sur la totalité du revenu, que le lecteur ne sait pas lire."""
    recuperateur = _recuperateur()
    with pytest.raises(ValueError, match="tableau"):
        recuperateur.lire_redaction("LEGIARTI000000000000", "2030-01-01",
                                    "I.-Le taux est fixé à 18 %. II.-Rien.")
    with pytest.raises(ValueError, match="plafond"):
        recuperateur.lire_redaction(
            "LEGIARTI000000000000", "2030-01-01",
            "I.-La cotisation est assise sur la totalité du revenu. Année Cotisation "
            "2030 18,00 % II.-Rien.")
