"""Les artisans et les commerçants, caisse par caisse (action 138, étape 18).

Le plafond propre du RCI : de 2013 à 2024, la première tranche de la
complémentaire des indépendants (7 %) s'arrête à un plafond que la caisse
publie chaque année, et non au plafond de la sécurité sociale ; la seconde
(8 %) part de lui (D. 635-7, fiche ``rci_seuil_premiere_tranche``). Depuis
2025, le texte coupe au plafond de la sécurité sociale.

Les taux propres : au régime général depuis 2018, l'artisan et le commerçant
cotisent à leur barème (D. 633-3, fiche ``cotisation_vieillesse_independants``),
17,15 % sous le plafond et 0,60 % sur la totalité, 0,72 % depuis 2025, et non
aux 15,45 % et 2,30 à 2,51 % du salarié et de son employeur. La fiche de paie
le prélève, le compte notionnel le porte.

Les points d'avant 1973 : les années d'artisan et de commerçant de 1949 à 1972
ont leur régime, ``cancava_avant_1973`` et ``organic_avant_1973`` — des points,
un par 3 % ou 5 % du plafond (D. 634-8), servis à la valeur du point de la date
d'effet et minorés selon l'article 3 du décret n° 73-937 —, hors de la pension
alignée (L. 634-3 ; fiche ``points_avant_1973_independants``).

L'assiette abattue : pour les périodes courant à compter du 1er janvier 2025,
l'assiette sociale de l'indépendant est son revenu avant cotisations, abattu de
26 %, l'abattement borné entre 1,76 % et 130 % du plafond (L. 136-3, III ;
D. 136-5 ; fiche ``assiette_sociale_independants``). La fiche de paie reçoit
l'assiette ; son profil sait la tirer du revenu brut, et l'inverse.

Les points d'invalidité : pour chaque mois de pension d'invalidité ou
d'incapacité au métier, le RCI porte au compte le quotient, au centième, des
points cotisés avant l'invalidité par les mois d'activité qui les ont cotisés,
deux points par mois à qui n'en a cotisé aucun depuis l'arrêté du 19 juin 2024
(règlement du RCI, article 9) ; avant 2013, seize points par trimestre ou le
quotient par trimestre à l'artisan, deux points par mois au commerçant
(annexe 1, 3 ; fiche ``points_invalidite_independants``).
"""

from __future__ import annotations

import importlib.util
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import AnneeCarriere, Carriere, LigneRelevee, Metier
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees import regimes
from retraite_notionnelle.donnees.regimes import CatalogueRegimes
from retraite_notionnelle.droit import acquerir, compter, coordonner
from retraite_notionnelle.moteur.compte import ConstructeurCompte
from retraite_notionnelle.remuneration import (
    ConstructeurFiche, bloc_droit_en_vigueur, charger_prelevements, smic_annuel)
from retraite_notionnelle.simulateur import Simulateur

from outils_pont import Saisies

RACINE = Path(__file__).resolve().parents[1]

#: Le plafond de cotisation RCI que la caisse a publié chaque année : circulaires
#: Cnav 2020-42 à 2023-33 de 2021 à 2024, publications du RSI puis de la
#: Sécurité sociale des indépendants avant (fiche ``rci_seuil_premiere_tranche``).
PLAFOND_RCI = {
    2013: 37_032, 2014: 37_513, 2015: 37_513, 2016: 37_546, 2017: 37_546,
    2018: 37_846, 2019: 37_960, 2020: 38_340, 2021: 38_493, 2022: 38_916,
    2023: 40_784, 2024: 42_946,
}


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _tranches(catalogue, annee: int):
    premiere, seconde = sorted(catalogue["rci"].periodes_actives(annee),
                               key=lambda p: p.taux_cotisation_retraite)
    return premiere, seconde


def test_le_plafond_du_rci_est_celui_que_la_caisse_publie(simulateur):
    """Chaque année de 2013 à 2024, la première tranche s'arrête au plafond
    publié et la seconde part de lui, jusqu'à quatre plafonds de la sécurité
    sociale de l'année ; en 2013, il vaut le plafond de la sécurité sociale."""
    catalogue = CatalogueRegimes(RACINE_DONNEES)
    for annee, plafond_rci in PLAFOND_RCI.items():
        pss = simulateur.macro.plafond_securite_sociale(annee)
        premiere, seconde = _tranches(catalogue, annee)
        assert premiere.bornes_assiette_en_euros(pss, annee) == (0.0, plafond_rci)
        assert seconde.bornes_assiette_en_euros(pss, annee) == (plafond_rci, 4 * pss)
    assert PLAFOND_RCI[2013] == simulateur.macro.plafond_securite_sociale(2013)


def test_chaque_annee_d_une_periode_a_bornes_annuelles_a_sa_borne():
    """Une année sans montant retomberait sans bruit sur le plafond de la
    sécurité sociale : toute période qui en porte les couvre toutes."""
    for regime in CatalogueRegimes(RACINE_DONNEES):
        for periode in regime.periodes:
            for bornes in (periode.borne_basse_par_annee, periode.borne_haute_par_annee):
                if not bornes:
                    continue
                assert periode.fin is not None, (regime.code, periode.debut)
                assert [annee for annee, _ in bornes] == list(
                    range(periode.debut, periode.fin + 1)), (regime.code, periode.debut)


def test_depuis_2025_la_premiere_tranche_s_arrete_au_plafond_de_la_securite_sociale(
        simulateur):
    """D. 635-7 dans sa rédaction du 7 juillet 2024, pour les périodes courant
    à compter du 1er janvier 2025 : 8,1 % jusqu'au plafond annuel, 9,1 % au-delà."""
    catalogue = CatalogueRegimes(RACINE_DONNEES)
    for annee in (2025, 2026):
        pss = simulateur.macro.plafond_securite_sociale(annee)
        premiere, seconde = _tranches(catalogue, annee)
        assert (premiere.taux_cotisation_retraite, seconde.taux_cotisation_retraite) == (
            pytest.approx(0.081), pytest.approx(0.091))
        assert premiere.bornes_assiette_en_euros(pss, annee) == (0.0, pss)
        assert seconde.bornes_assiette_en_euros(pss, annee) == (pss, 4 * pss)


def test_une_borne_annuelle_exige_l_annee():
    """Sans l'année, la borne propre ne peut pas se lire : le moteur refuse
    plutôt que de couper au plafond de la sécurité sociale."""
    premiere, _ = _tranches(CatalogueRegimes(RACINE_DONNEES), 2019)
    with pytest.raises(ValueError, match="année par année"):
        premiere.bornes_assiette_en_euros(40_524)


def _fiche(simulateur, annee: int, revenu: float, statut: str = "artisan") -> dict:
    """Ce que la fiche de paie du droit en vigueur prélève pour la retraite,
    régime par régime : (part de l'assuré, part de l'employeur)."""
    bloc = bloc_droit_en_vigueur(simulateur.catalogue, simulateur.affiliations,
                                 statut, annee)
    profil = charger_prelevements(RACINE_DONNEES).profil("independant")
    fiche = ConstructeurFiche(profil).fiche(
        annee, revenu, simulateur.macro.plafond_securite_sociale(annee),
        smic_annuel(simulateur.macro, annee), bloc)
    return {ligne.code: (ligne.salarie, ligne.employeur)
            for ligne in fiche.lignes if ligne.retraite}


def _fiche_rci(simulateur, annee: int, revenu: float) -> float:
    return _fiche(simulateur, annee, revenu)["rci"][0]


def test_la_fiche_de_paie_preleve_au_plafond_propre(simulateur):
    """60 000 € de revenu en 2019 : 7 % de 37 960 €, 8 % de 22 040 €."""
    assert _fiche_rci(simulateur, 2019, 60_000.0) == pytest.approx(
        0.07 * 37_960 + 0.08 * (60_000 - 37_960))


def _pension_rci(simulateur, niveau: float) -> float:
    carriere = Carriere.depuis_parcours(
        annee_naissance=1960, sexe="H",
        metiers=[Metier(affiliation="artisan", age_debut=21.0, niveau_salaire=niveau)],
        age_liquidation=64.0, macro=simulateur.macro)
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return {p.regime: p for p in resultat.pensions_par_regime}["rci"].montant


def test_les_points_du_rci_suivent_le_plafond_propre(simulateur, monkeypatch):
    """Au-dessus du plafond propre, le point de cotisation de plus achète des
    points : la pension RCI d'un artisan né en 1960 gagne quelques millièmes ;
    sous lui, rien ne bouge."""
    propre = {niveau: _pension_rci(simulateur, niveau) for niveau in (0.8, 2.0)}
    monkeypatch.setattr(regimes.PeriodeRegime, "bornes_de_l_annee",
                        lambda self, annee: (None, None))
    au_plafond = {niveau: _pension_rci(Simulateur(), niveau) for niveau in (0.8, 2.0)}
    assert propre[0.8] == pytest.approx(au_plafond[0.8])
    assert 1.001 < propre[2.0] / au_plafond[2.0] < 1.01


#: Le barème propre de D. 633-3 au régime général, depuis 2018 : (sous le
#: plafond, sur la totalité). LEGIARTI000031799496 et 000041967101, puis
#: LEGIARTI000049904636 pour les périodes courant depuis le 1er janvier 2025.
BAREME_PROPRE = {annee: (0.1715, 0.0060 if annee < 2025 else 0.0072)
                 for annee in range(2018, 2027)}


def test_au_regime_general_l_artisan_garde_son_bareme(simulateur):
    """Chaque année depuis 2018, la période du régime général porte le barème
    propre du non-salarié à côté des taux du salarié, qu'il ne remplace pas."""
    catalogue = CatalogueRegimes(RACINE_DONNEES)
    for annee, attendu in BAREME_PROPRE.items():
        (periode,) = [p for p in catalogue["regime_general"].periodes_actives(annee)
                      if p.assiette == "plafonnee"]
        assert periode.taux_du_cotisant(True) == pytest.approx(attendu), annee
        assert periode.taux_du_cotisant(False) == (
            periode.taux_cotisation_retraite, periode.taux_cotisation_deplafonnee)
    (avant,) = catalogue["regime_general"].periodes_actives(2017)
    assert avant.taux_du_cotisant(True) == avant.taux_du_cotisant(False)


@pytest.mark.parametrize("statut, annee", [
    ("artisan", 2019), ("commercant", 2024), ("artisan", 2025),
    ("liberal_non_reglemente", 2020), ("micro_entrepreneur", 2026),
])
def test_la_fiche_de_paie_preleve_le_bareme_propre(simulateur, statut, annee):
    """60 000 € de revenu : 17,15 % jusqu'au plafond, et 0,60 % (0,72 % depuis
    2025) sur le tout — 7 309,87 € en 2019, et non les 7 640,96 € qu'un salarié
    et son employeur versent."""
    pss = simulateur.macro.plafond_securite_sociale(annee)
    plafonne, deplafonne = BAREME_PROPRE[annee]
    assert _fiche(simulateur, annee, 60_000.0, statut)["regime_general"] == (
        pytest.approx(plafonne * pss + deplafonne * 60_000), 0.0)


def test_le_salarie_garde_ses_taux(simulateur):
    """Le salarié du privé et son employeur : 15,45 % sous le plafond et
    2,30 % sur la totalité en 2019, partagés comme la fiche le dit."""
    salarie, employeur = _fiche(simulateur, 2019, 60_000.0,
                                "salarie_prive_non_cadre")["regime_general"]
    assert salarie + employeur == pytest.approx(0.1545 * 40_524 + 0.023 * 60_000)


def test_le_compte_porte_ce_que_l_artisan_a_verse(simulateur):
    """Le compte notionnel inscrit ce qui a été versé : le barème propre au
    régime général depuis 2018, celui du RSI avant (0,50 % en 2016)."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1965, sexe="H", affiliation="artisan", mois_naissance=1,
        age_debut=22, age_liquidation=64, niveau_salaire=2.0, profil_carriere="plat")
    constructeur = ConstructeurCompte(simulateur.macro, simulateur.catalogue,
                                      simulateur.affiliations, simulateur.indexation,
                                      simulateur.parametres)
    for annee, (code, plafonne, deplafonne) in {
            2016: ("rsi", 0.1715, 0.0050), 2019: ("regime_general", *BAREME_PROPRE[2019]),
            2025: ("regime_general", *BAREME_PROPRE[2025])}.items():
        versees = constructeur.cotisation_annuelle(carriere, annee)
        pss = simulateur.macro.plafond_securite_sociale(annee)
        revenu = versees.revenu
        assert revenu > pss
        assert dict(versees.par_regime)[code] == pytest.approx(
            plafonne * pss + deplafonne * revenu), annee


#: Quatre rédactions de D. 633-3, telles que l'index LEGI les porte, raccourcies
#: de ce que le lecteur ne lit pas : le calendrier, la dérogation en note et la
#: date d'application.
REDACTIONS_D633_3 = [
    ("LEGIARTI000028435871", "2014-01-01",
     "I. - Le taux des cotisations assises sur le revenu d'activité dans la limite du "
     "plafond est fixé à : a) 16,95 % pour l'année 2014 ; b) 17,05 % pour l'année "
     "2015 ; c) 17,15 % à compter de l'année 2016. II. - Le taux des cotisations "
     "assises sur la totalité du revenu d'activité est fixé à 0,20 %."),
    ("LEGIARTI000029924551", "2015-01-01",
     "Conformément au décret n° 2014-1531 du 17 décembre 2014 article 13 II, ces "
     "dispositions s'appliquent aux cotisations de sécurité sociale dues au titre des "
     "périodes courant à compter du 1er janvier 2015. I. - Le taux des cotisations "
     "assises sur le revenu d'activité dans la limite du plafond est fixé à : a) 17,05 % "
     "pour l'année 2015 ; b) 17,15 % à compter de l'année 2016. II. - Le taux des "
     "cotisations assises sur la totalité du revenu d'activité est fixé à : a) 0,35 % "
     "pour l'année 2015 ; b) 0,50 % pour l'année 2016 ; c) 0,60 % à compter de l'année "
     "2017."),
    ("LEGIARTI000031799496", "2016-01-01",
     "Conformément à l'article 10 II du décret n° 2015-1856 du 30 décembre 2015, pour "
     "l'année 2016, par dérogation aux dispositions de l'article D. 633-3 dans sa "
     "rédaction résultant de l'article 7 du présent décret : le taux de la cotisation "
     "mentionné au II de l'article D. 633-3 est fixé à 0,5 %. I.-Le taux des cotisations "
     "assises sur le revenu d'activité dans la limite du plafond est fixé à 17,15 %. "
     "II.-Le taux des cotisations assises sur la totalité du revenu d'activité est fixé "
     "à 0,60 %."),
    ("LEGIARTI000049904636", "2024-07-07",
     "Conformément à l’article 6 du décret n° 2024-688 du 5 juillet 2024, ces "
     "dispositions s'appliquent au calcul des cotisations et des contributions dues par "
     "les travailleurs indépendants non agricoles au titre des périodes courant à "
     "compter du 1er janvier 2025. I.-Le taux des cotisations assises sur l'assiette de "
     "cotisations dans la limite du plafond est fixé à 17,15 %. II.-Le taux des "
     "cotisations assises sur la totalité de l'assiette de cotisations est fixé à 0,72 %."),
]


def _recuperateur():
    nom = "dila_legi_taux_independants"
    chemin = RACINE / "scripts" / "fetch" / f"{nom}.py"
    specification = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules[nom] = module
    specification.loader.exec_module(module)
    return module


def test_le_bareme_se_lit_dans_les_redactions_de_d_633_3():
    """Le récupérateur date chaque taux au 1er janvier, suit le calendrier
    d'une rédaction, la dérogation de 2016 en note et la date d'application
    que la rédaction de 2024 écrit, et rend le barème que la table certifie."""
    recuperateur = _recuperateur()
    redactions = [recuperateur.lire_redaction(*r) for r in REDACTIONS_D633_3]
    assert [r["application"] for r in redactions] == [
        "2014-01-01", "2015-01-01", "2016-01-01", "2025-01-01"]
    serie = recuperateur.series(redactions)
    lues = {int(a): (t["plafonne"], t["deplafonne"]) for a, t in serie.items()}
    assert lues[2014] == (0.1695, 0.002)
    assert lues[2015] == (0.1705, 0.0035)
    assert lues[2016] == (0.1715, 0.005)
    for annee in range(2017, 2025):
        assert lues[annee] == (0.1715, 0.006), annee
    assert lues[2025] == (0.1715, 0.0072)
    for annee, attendu in BAREME_PROPRE.items():
        if annee in lues:
            assert lues[annee] == pytest.approx(attendu), annee


def test_une_redaction_illisible_arrete_le_recuperateur():
    """Rien n'est écrit plutôt qu'un taux deviné."""
    recuperateur = _recuperateur()
    with pytest.raises(ValueError, match="alinéas"):
        recuperateur.lire_redaction("LEGIARTI000000000000", "2030-01-01",
                                    "Le taux est fixé à 18 %.")


#: (revenu brut, assiette) en 2026, au plafond de 48 060 € : l'abattement de
#: 26 %, son plancher de 845,86 € et son plafond de 62 478 €, et le revenu sous
#: le plancher, qui n'a pas d'assiette.
ABATTEMENTS_2026 = [(40_000.0, 29_600.0), (2_000.0, 2_000.0 - 0.0176 * 48_060),
                    (300_000.0, 300_000.0 - 1.30 * 48_060), (500.0, 0.0)]


def _profil_independant():
    return charger_prelevements(RACINE_DONNEES).profil("independant")


def test_l_assiette_abattue_suit_l_article_l_136_3():
    """26 % du revenu brut, ni moins de 1,76 % ni plus de 130 % du plafond ;
    avant 2025, l'assiette est le revenu lui-même, et un salarié n'a pas
    d'abattement de ce genre."""
    profil = _profil_independant()
    for brut, assiette in ABATTEMENTS_2026:
        assert profil.assiette_abattue(brut, 48_060.0, 2026) == pytest.approx(assiette)
    assert profil.assiette_abattue(40_000.0, 46_368.0, 2024) == 40_000.0
    salarie = charger_prelevements(RACINE_DONNEES).profil("salarie_prive")
    assert salarie.assiette_abattue(40_000.0, 48_060.0, 2026) == 40_000.0


def test_la_reciproque_rend_le_revenu_brut():
    """Du revenu brut à l'assiette et retour, à toute hauteur, les deux coudes
    compris ; une assiette nulle rend le plancher."""
    profil = _profil_independant()
    plancher = 0.0176 * 48_060
    for brut in [plancher, *range(1_000, 400_001, 1_500), 3_253.0, 240_300.0]:
        assiette = profil.assiette_abattue(brut, 48_060.0, 2026)
        assert profil.revenu_avant_abattement(assiette, 48_060.0, 2026) == pytest.approx(
            brut), brut
    assert profil.revenu_avant_abattement(0.0, 48_060.0, 2026) == pytest.approx(plancher)
    assert profil.revenu_avant_abattement(40_000.0, 46_368.0, 2024) == 40_000.0


#: Le jumeau JavaScript : les mêmes bornes et la même ligne de fiche de paie.
_JUMEAU = """
import { readFileSync } from "node:fs";
import { CatalogueRegimes, Affiliations } from "./moteur/js/regimes.js";
import { BaremePrelevements, ConstructeurFiche, blocDroitEnVigueur }
  from "./moteur/js/remuneration.js";
const { annees, pss, fiche } = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("./moteur/donnees.json", "utf8"));
const catalogue = new CatalogueRegimes(paquet);
const bornes = annees.map((annee, rang) => catalogue.obtenir("rci").periodesActives(annee)
  .map((p) => p.bornesAssietteEnEuros(pss[rang], annee)));
const bloc = blocDroitEnVigueur(catalogue, new Affiliations(paquet), "artisan", fiche.annee);
const profil = new BaremePrelevements(paquet.prelevements_remuneration).profil("independant");
const lignes = new ConstructeurFiche(profil).fiche(
  fiche.annee, fiche.revenu, fiche.pss, fiche.smic, bloc).lignes;
const retraite = Object.fromEntries(lignes.filter((ligne) => ligne.retraite)
  .map((ligne) => [ligne.code, [ligne.salarie, ligne.employeur]]));
const abattues = fiche.bruts.map(([brut, pss, annee]) => {
  const assiette = profil.assietteAbattue(brut, pss, annee);
  return [assiette, profil.revenuAvantAbattement(assiette, pss, annee)];
});
process.stdout.write(JSON.stringify({ bornes, retraite, abattues }));
"""


def test_le_portage_javascript_rend_les_memes_plafond_bareme_et_assiette(simulateur):
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    catalogue = simulateur.catalogue
    annees = [*PLAFOND_RCI, 2025, 2026]
    pss = [simulateur.macro.plafond_securite_sociale(annee) for annee in annees]
    bruts = [(brut, 48_060.0, 2026) for brut, _ in ABATTEMENTS_2026] + [
        (40_000.0, 46_368.0, 2024), (61_234.5, 47_100.0, 2025)]
    fiche = {"annee": 2019, "revenu": 60_000.0, "pss": pss[annees.index(2019)],
             "smic": smic_annuel(simulateur.macro, 2019), "bruts": bruts}
    profil = _profil_independant()
    attendu = {
        "bornes": [[list(p.bornes_assiette_en_euros(plafond, annee))
                    for p in catalogue["rci"].periodes_actives(annee)]
                   for annee, plafond in zip(annees, pss)],
        "retraite": _fiche(simulateur, 2019, 60_000.0),
        "abattues": [
            [profil.assiette_abattue(brut, plafond, annee),
             profil.revenu_avant_abattement(
                 profil.assiette_abattue(brut, plafond, annee), plafond, annee)]
            for brut, plafond, annee in bruts],
    }
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _JUMEAU,
         json.dumps({"annees": annees, "pss": pss, "fiche": fiche})],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    obtenu = json.loads(execution.stdout)
    assert obtenu["bornes"] == attendu["bornes"]
    assert set(obtenu["retraite"]) == set(attendu["retraite"])
    for code, (salarie, employeur) in attendu["retraite"].items():
        assert obtenu["retraite"][code] == [pytest.approx(salarie, abs=1e-9),
                                            pytest.approx(employeur, abs=1e-9)], code
    assert obtenu["abattues"] == [[pytest.approx(a, abs=1e-9), pytest.approx(b, abs=1e-9)]
                                  for a, b in attendu["abattues"]]


# -- les points d'avant 1973 -------------------------------------------------


def _carriere(affiliation: str, debut: int, fin: int, naissance: int,
              liquidation: int, part_du_plafond: float, macro) -> Carriere:
    lignes = [AnneeCarriere(annee=annee, affiliation=affiliation, trimestres_valides=4,
                            revenu=part_du_plafond * macro.plafond_securite_sociale(annee))
              for annee in range(debut, fin + 1)]
    return Carriere(annee_naissance=naissance, sexe="H", lignes=lignes,
                    age_liquidation=float(liquidation - naissance))


def _pensions(simulateur, carriere) -> dict:
    return {p.regime: p for p in simulateur.scenario_actuel.calculer(carriere)
            .pensions_par_regime}


def test_les_annees_d_avant_1973_ont_leur_regime():
    """L'artisan et le commerçant de 1949 à 1972 relèvent des droits en points ;
    la CANCAVA et l'ORGANIC alignées commencent en 1973."""
    catalogue = CatalogueRegimes(RACINE_DONNEES)
    affiliations = Simulateur().scenario_actuel.affiliations
    for statut, avant, apres in (("artisan", "cancava_avant_1973", "cancava"),
                                 ("commercant", "organic_avant_1973", "organic")):
        assert affiliations.regimes(statut, 1972) == (avant,)
        assert apres in affiliations.regimes(statut, 1973)
        assert catalogue[apres].periodes[0].debut == 1973
        assert catalogue[avant].periode(1960).type_calcul == "points"


@pytest.mark.parametrize("statut, regime, points", [
    ("artisan", "cancava_avant_1973", 100 / 3),
    ("commercant", "organic_avant_1973", 20.0),
])
def test_un_point_par_trois_ou_cinq_pour_cent_du_plafond(simulateur, statut, regime, points):
    """D. 634-8 : un point par 3 % du plafond chez l'artisan, par 5 % chez le
    commerçant, au plafond au plus ; servis à la valeur du 1er janvier 2025
    (10,6667 € et 14,71063 €, circulaire Cnav 2024/39). Né en janvier 1958
    avec la durée, parti à 67 ans en janvier 2025 : rien n'est minoré."""
    valeur = {"cancava_avant_1973": 10.6667, "organic_avant_1973": 14.71063}[regime]
    for part, attendus in ((2.0, points), (0.5, points / 2)):
        carriere = Carriere(annee_naissance=1958, sexe="H", age_liquidation=67.0, lignes=[
            AnneeCarriere(annee=1972, affiliation=statut, trimestres_valides=4,
                          revenu=part * simulateur.macro.plafond_securite_sociale(1972)),
            *(AnneeCarriere(annee=annee, affiliation="salarie_prive_non_cadre",
                            trimestres_valides=4, revenu=30_000.0)
              for annee in range(1973, 2025))])
        pension = _pensions(simulateur, carriere)[regime]
        assert pension.montant == pytest.approx(attendus * valeur, rel=1e-6), pension.detail


def test_les_annees_d_avant_1973_sortent_de_la_proratisation(simulateur):
    """Les treize années de 1960 à 1972 ne sont plus des annuités de la pension
    alignée, mais des points : 128 trimestres sur 150, et 346,67 points à la
    valeur de 2005 (8,0199 €)."""
    pensions = _pensions(simulateur, _carriere(
        "artisan", 1960, 2004, 1940, 2005, 0.8, simulateur.macro))
    assert "× 128/150" in pensions["cancava"].detail, pensions["cancava"].detail
    assert pensions["cancava_avant_1973"].montant == pytest.approx(
        13 * 0.8 * 100 / 3 * 8.0199, rel=1e-6)


def test_la_minoration_de_l_article_3(simulateur):
    """Un commerçant de 1955 à 1972 seul, parti à soixante ans en 1995 : 72
    trimestres tous régimes, vingt trimestres jusqu'à soixante-cinq ans, le plus
    petit des deux décomptes, à 2,5 % chacun — la moitié de ses points."""
    carriere = _carriere("commercant", 1955, 1972, 1935, 1995, 1.0, simulateur.macro)
    pension = _pensions(simulateur, carriere)["organic_avant_1973"]
    valeur = simulateur.scenario_actuel.valeurs_point.service_au(
        "organic_avant_1973", 1995, 1)[0]
    assert pension.montant == pytest.approx(18 * 20 * valeur * 0.5, rel=1e-6), pension.detail


CAS_AVANT_1973 = [
    {"statut": "artisan", "naissance": "1945-03-15", "debut": "20",
     "liquidation": "2005-04"},
    {"statut": "commercant", "naissance": "1947-06-15", "debut": "19",
     "liquidation": "2010-01"},
]


def test_les_deux_moteurs_servent_les_memes_points_d_avant_1973():
    """Le résultat entier, des six scénarios, est le même en Python et en
    JavaScript pour un artisan et un commerçant entrés avant 1973."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    sys.path.insert(0, str(RACINE / "scripts"))
    from construire_temoins import _fini
    saisies = Saisies()
    attendus = [{"requete": cas, "resultat": _fini(saisies.simuler(cas).dictionnaire())}
                for cas in CAS_AVANT_1973]
    texte = json.dumps(attendus, ensure_ascii=False)
    assert "cancava_avant_1973" in texte and "organic_avant_1973" in texte
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        fichier.write(texte)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, (execution.stdout + execution.stderr)[-2000:]


# --- Les points d'invalidité -------------------------------------------------


def test_les_complementaires_des_artisans_et_des_commercants_portent_la_regle():
    """Chaque année, une seule période de la complémentaire porte la règle : la
    première tranche du RCI, la période de la RCO des artisans, du NRIC."""
    catalogue = CatalogueRegimes(RACINE_DONNEES)
    attendues = {"rci": ("mois", True, 2.0, (2024, 7)),
                 "rco_artisans": ("trimestre", True, 16.0, None),
                 "nric": ("mois", False, 2.0, None)}
    for code, (par, proportionnels, forfait, depuis) in attendues.items():
        regime = catalogue[code]
        for annee in range(regime.creation, 2027 if code == "rci" else 2013):
            regles = [p.points_invalidite for p in regime.periodes_actives(annee)
                      if p.points_invalidite is not None]
            assert len(regles) == 1, (code, annee)
            regle = regles[0]
            assert (regle.par, regle.proportionnels, regle.forfait,
                    regle.forfait_depuis) == (par, proportionnels, forfait, depuis)


def _invalide(simulateur, affiliation: str, naissance: int, invalidite: range,
              age_debut: float = 22.0, age_liquidation: float = 62.0):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, sexe="H",
        metiers=[Metier(affiliation=affiliation, age_debut=age_debut, niveau_salaire=1.0)],
        age_liquidation=age_liquidation, macro=simulateur.macro,
        interruptions={annee: "invalidite" for annee in invalidite})
    actuel = simulateur.scenario_actuel
    coordination = coordonner.coordonner(actuel, carriere)
    droits = acquerir.acquerir(actuel, coordination, compter.compter(actuel, coordination))
    return carriere, coordination, droits


def _credites(droits, code: str, annees) -> dict[int, float]:
    credites: dict[int, float] = {}
    for regime, annee, points, _ in droits.points:
        if regime == code and annee in annees:
            credites[annee] = credites.get(annee, 0.0) + points
    return credites


def test_le_rci_porte_le_quotient_des_points_cotises_par_les_mois(simulateur):
    """Artisan né en 1962, à son compte depuis 1984, invalide de 2016 à 2023 :
    chaque année d'invalidité vaut douze fois le quotient, au centième, de ses
    points cotisés au RCI et à la RCO des artisans (au coefficient 0,2778 de la
    fusion) avant 2016 par ses mois d'activité, et rien d'autre ne les crédite."""
    carriere, coordination, droits = _invalide(
        simulateur, "artisan", 1962, range(2016, 2024))
    cotises = sum(points * {"rci": 1.0, "rco_artisans": 0.2778}[regime]
                  for regime, annee, points, _ in droits.points
                  if regime in ("rci", "rco_artisans") and annee < 2016)
    mois = sum(carriere.part_retenue_ligne(ligne) * 12 for ligne in carriere.lignes
               if ligne.cotise and ligne.annee < 2016)
    par_mois = math.floor(cotises / math.floor(mois) * 100 + 0.5) / 100
    assert 5 < par_mois < 20
    assert _credites(droits, "rci", range(2016, 2024)) == {
        annee: pytest.approx(12 * par_mois) for annee in range(2016, 2024)}


def test_le_commercant_d_avant_2013_a_deux_points_par_mois(simulateur):
    """Commerçant invalide de 2008 à 2019 : deux points par mois au NRIC
    jusqu'en 2012, le quotient au RCI ensuite — ses points du NRIC, repris un
    pour un, par ses mois d'activité depuis 2004, la création du NRIC."""
    carriere, _, droits = _invalide(simulateur, "commercant", 1958, range(2008, 2020))
    assert _credites(droits, "nric", range(2008, 2013)) == {
        annee: pytest.approx(24.0) for annee in range(2008, 2013)}
    cotises = sum(points for regime, annee, points, _ in droits.points
                  if regime == "nric" and annee < 2008)
    mois = sum(carriere.part_retenue_ligne(ligne) * 12 for ligne in carriere.lignes
               if ligne.cotise and 2004 <= ligne.annee < 2008)
    par_mois = math.floor(cotises / math.floor(mois) * 100 + 0.5) / 100
    assert _credites(droits, "rci", range(2013, 2020)) == {
        annee: pytest.approx(12 * par_mois) for annee in range(2013, 2020)}


def test_l_artisan_d_avant_2013_a_le_quotient_par_trimestre(simulateur):
    """Artisan invalide de 1995 à 2012 : chaque trimestre vaut le quotient, au
    centième, de ses points de la RCO des artisans depuis 1979 par ses
    trimestres cotisés."""
    carriere, _, droits = _invalide(simulateur, "artisan", 1955, range(1995, 2013))
    cotises = sum(points for regime, annee, points, _ in droits.points
                  if regime == "rco_artisans" and annee < 1995)
    trimestres = math.floor(sum(
        carriere.part_retenue_ligne(ligne) * 12 for ligne in carriere.lignes
        if ligne.cotise and 1979 <= ligne.annee < 1995)) // 3
    par_trimestre = math.floor(cotises / trimestres * 100 + 0.5) / 100
    assert _credites(droits, "rco_artisans", range(1995, 2013)) == {
        annee: pytest.approx(4 * par_trimestre) for annee in range(1995, 2013)}


def test_sans_point_cotise_deux_points_par_mois_depuis_juillet_2024(simulateur):
    """Un artisan invalide dès sa première année n'a cotisé aucun point : rien
    jusqu'en juin 2024, deux points par mois depuis juillet — six mois de 2024,
    convention des mois non datés d'une ligne, puis toute l'année."""
    _, _, droits = _invalide(simulateur, "artisan", 1960, range(2022, 2027),
                             age_debut=62.0, age_liquidation=67.0)
    assert _credites(droits, "rci", range(2022, 2027)) == {
        2024: pytest.approx(12.0), 2025: pytest.approx(24.0), 2026: pytest.approx(24.0)}


def test_les_points_d_invalidite_relevent_la_pension_du_rci(simulateur):
    """L'artisan invalide de 2016 à 2023 garde, au RCI, l'essentiel de la
    pension qu'il aurait eue en travaillant ; sans les points, il en perdait les
    trois quarts."""
    def pension(interruptions):
        carriere = Carriere.depuis_parcours(
            annee_naissance=1962, sexe="H",
            metiers=[Metier(affiliation="artisan", age_debut=22.0, niveau_salaire=1.0)],
            age_liquidation=62.0, macro=simulateur.macro, interruptions=interruptions)
        resultat = simulateur.scenario_actuel.calculer(carriere)
        return {p.regime: p.montant for p in resultat.pensions_par_regime}["rci"]
    invalide = pension({annee: "invalidite" for annee in range(2016, 2024)})
    actif = pension(None)
    assert 0.6 < invalide / actif < 1.0


CAS_INVALIDITE = [
    {"statut": "artisan", "naissance": "1962-03-15", "debut": "22",
     "liquidation": "2024-04", "interruptions": "2016:2023:invalidite"},
    {"statut": "commercant", "naissance": "1958-03-15", "debut": "22",
     "liquidation": "2020-04", "interruptions": "2008:2019:invalidite"},
    {"statut": "artisan", "naissance": "1955-06-15", "debut": "20",
     "liquidation": "2017-07", "interruptions": "1995:2016:invalidite"},
]


def test_les_deux_moteurs_servent_les_memes_points_d_invalidite():
    """Le résultat entier, des six scénarios, est le même en Python et en
    JavaScript pour trois indépendants invalides."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    sys.path.insert(0, str(RACINE / "scripts"))
    from construire_temoins import _fini
    saisies = Saisies()
    attendus = [{"requete": cas, "resultat": _fini(saisies.simuler(cas).dictionnaire())}
                for cas in CAS_INVALIDITE]
    texte = json.dumps(attendus, ensure_ascii=False)
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        fichier.write(texte)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, (execution.stdout + execution.stderr)[-2000:]


# --- Le conjoint collaborateur ------------------------------------------------


def _conjoint(simulateur, affiliation: str, revenus: dict[int, float],
              naissance: int = 1962, liquidation: int = 2026):
    carriere = Carriere.depuis_releve(
        annee_naissance=naissance, sexe="F", age_liquidation=float(liquidation - naissance),
        releve=[LigneRelevee(annee, affiliation, revenu) for annee, revenu in revenus.items()],
        macro=simulateur.macro)
    actuel = simulateur.scenario_actuel
    coordination = coordonner.coordonner(actuel, carriere)
    droits = acquerir.acquerir(actuel, coordination, compter.compter(actuel, coordination))
    return carriere, droits


@pytest.mark.parametrize("affiliation", ["conjoint_collaborateur_artisan",
                                         "conjoint_collaborateur_commercant"])
def test_sans_revenu_le_conjoint_cotise_au_tiers_du_plafond(simulateur, affiliation):
    """Depuis l'affiliation obligatoire de 2007, une année d'emploi du conjoint
    collaborateur sans revenu cotise sur « un revenu forfaitaire égal au tiers
    du plafond » (D. 633-19-2, 1°), l'option que la caisse applique à défaut de
    choix (R. 662-1) ; avant, l'assurance volontaire non souscrite ne valide
    rien. Un revenu saisi est l'assiette choisie, et reste tel quel."""
    macro = simulateur.macro
    carriere, _ = _conjoint(simulateur, affiliation,
                            {2005: 0.0, 2006: 0.0, 2007: 0.0, 2019: 0.0, 2020: 9000.0})
    lignes = {ligne.annee: ligne for ligne in carriere.lignes}
    assert lignes[2005].revenu == lignes[2006].revenu == 0.0
    assert lignes[2005].trimestres_valides == 0
    for annee in (2007, 2019):
        assert lignes[annee].revenu == pytest.approx(macro.plafond_securite_sociale(annee) / 3)
        assert lignes[annee].trimestres_valides == 4
    assert lignes[2020].revenu == 9000.0


def test_le_conjoint_route_ses_regimes():
    """Le régime de base des artisans ou des commerçants dès l'assurance
    volontaire de 1983, la complémentaire de sa profession depuis 2007, le RCI
    depuis 2013, le régime général depuis 2018."""
    from retraite_notionnelle.carriere import Affiliations
    affiliations = Affiliations(RACINE_DONNEES)
    attendus = {"conjoint_collaborateur_artisan": {
                    1983: ["cancava"], 2006: ["rsi"], 2007: ["rsi", "rco_artisans"],
                    2013: ["rsi", "rci"], 2018: ["regime_general", "rci"]},
                "conjoint_collaborateur_commercant": {
                    1983: ["organic"], 2006: ["rsi"], 2007: ["rsi", "nric"],
                    2013: ["rsi", "rci"], 2018: ["regime_general", "rci"]}}
    for code, debuts in attendus.items():
        assert affiliations.sans_employeur(code)
        assert {p["debut"]: p["regimes"] for p in affiliations.periodes(code)} == debuts


def test_le_forfait_ouvre_les_points_du_rci_et_de_la_complementaire(simulateur):
    """La complémentaire cotise sur le revenu retenu pour la base
    (D. 635-10-2) : au forfait, le conjoint d'un artisan acquiert les points
    qu'acquiert l'artisan au tiers du plafond, à la RCO des artisans de 2007 à
    2012 et au RCI depuis."""
    macro = simulateur.macro
    annees = range(2007, 2026)
    _, conjoint = _conjoint(simulateur, "conjoint_collaborateur_artisan",
                            {annee: 0.0 for annee in annees})
    _, artisan = _conjoint(simulateur, "artisan",
                           {annee: macro.plafond_securite_sociale(annee) / 3
                            for annee in annees})
    for code, periode in (("rco_artisans", range(2007, 2013)), ("rci", range(2013, 2026))):
        attendus = _credites(artisan, code, periode)
        assert set(attendus) == set(periode)
        assert _credites(conjoint, code, periode) == {
            annee: pytest.approx(points) for annee, points in attendus.items()}


CAS_CONJOINT = [
    {"statut": "artisan", "naissance": "1962-03-15", "liquidation": "2026-04",
     "releve": "\n".join(f"{annee}:conjoint_collaborateur_artisan:0"
                         for annee in range(1990, 2026))},
    {"statut": "commercant", "naissance": "1960-03-15", "liquidation": "2024-04",
     "releve": "\n".join(f"{annee}:conjoint_collaborateur_commercant:"
                         f"{0 if annee % 3 else 7500}" for annee in range(1985, 2024))},
]


def test_les_deux_moteurs_servent_les_memes_droits_au_conjoint():
    """Le résultat entier, des six scénarios, est le même en Python et en
    JavaScript pour deux conjoints collaborateurs, au forfait et à l'option."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    sys.path.insert(0, str(RACINE / "scripts"))
    from construire_temoins import _fini
    saisies = Saisies()
    attendus = [{"requete": cas, "resultat": _fini(saisies.simuler(cas).dictionnaire())}
                for cas in CAS_CONJOINT]
    texte = json.dumps(attendus, ensure_ascii=False)
    assert "rco_artisans" in texte and "nric" in texte
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        fichier.write(texte)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, (execution.stdout + execution.stderr)[-2000:]


# --- Les dispenses de l'assiette minimale ---------------------------------------


def _dispense(simulateur, affiliation: str, motif: str, annees, revenu: float = 3000.0,
              naissance: int = 1962, liquidation: int = 2027):
    releve = [LigneRelevee(annee, affiliation, revenu, dispense_assiette_minimale=motif)
              for annee in annees]
    carriere = simulateur.carriere_releve(naissance, "F", releve,
                                          float(liquidation - naissance))
    return carriere, {ligne.annee: ligne for ligne in carriere.lignes}


def test_les_familles_des_dispenses_sont_celles_de_l_assiette_minimale():
    """Les statuts que `dispenses_assiette_minimale.yaml` range par famille
    sont ceux qui subissent l'assiette minimale, ni plus ni moins."""
    from retraite_notionnelle.donnees.chargement import (
        charger_assiettes_minimales, charger_yaml)
    familles = charger_yaml(RACINE_DONNEES / "reference" / "legislation"
                            / "dispenses_assiette_minimale.yaml")["familles"]
    ranges = [s for statuts in familles.values() for s in statuts]
    assert len(ranges) == len(set(ranges))
    assert set(ranges) == {s for r in charger_assiettes_minimales(RACINE_DONNEES)
                           for s in r.statuts}


def test_le_rsa_dispense_de_l_assiette_minimale_depuis_2016(simulateur):
    """L. 131-6-3, de la loi n° 2015-1702, puis L. 613-11 : l'artisan au RSA qui
    déclare 3 000 € cotise sur 3 000 € depuis 2016, et ne valide que ce qu'ils
    valident ; avant, rien ne l'en dispensait."""
    _, sans = _dispense(simulateur, "artisan", "", range(2014, 2026))
    _, rsa = _dispense(simulateur, "artisan", "rsa", range(2014, 2026))
    for annee in (2014, 2015):
        assert rsa[annee].dispense_assiette_minimale == ""
        assert rsa[annee].assiette_minimale_base == sans[annee].assiette_minimale_base > 0
        assert rsa[annee].trimestres_valides == sans[annee].trimestres_valides
    for annee in range(2016, 2026):
        assert rsa[annee].dispense_assiette_minimale == "rsa"
        assert rsa[annee].assiette_minimale_base == 0.0
        assert rsa[annee].revenu == sans[annee].revenu == 3000.0
    assert sans[2025].trimestres_valides == 3 and rsa[2025].trimestres_valides == 1


def test_l_activite_saisonniere_depuis_2020_et_les_dispenses_de_d_642_4(simulateur):
    """L'activité accessoire saisonnière, depuis la loi n° 2019-1446 ; le libéral
    dont l'activité n'est pas principale, de 2004 à 2015 seulement (D. 642-4),
    et jamais l'artisan."""
    _, saison = _dispense(simulateur, "commercant", "activite_saisonniere",
                          range(2018, 2022))
    assert [saison[a].assiette_minimale_base == 0.0 for a in range(2018, 2022)] == [
        False, False, True, True]
    _, liberal = _dispense(simulateur, "profession_liberale", "activite_non_principale",
                           range(2014, 2018))
    assert [liberal[a].dispense_assiette_minimale for a in range(2014, 2018)] == [
        "activite_non_principale", "activite_non_principale", "", ""]
    _, artisan = _dispense(simulateur, "artisan", "pensionne", range(2010, 2012))
    assert all(ligne.assiette_minimale_base > 0 for ligne in artisan.values())
    with pytest.raises(ValueError, match="inconnue"):
        _dispense(simulateur, "artisan", "chomage", range(2020, 2021))


def test_le_rsa_ecarte_aussi_le_minimum_de_la_carpimko(simulateur):
    """L. 613-11 couvre « le cas échéant » les complémentaires des libéraux
    (L. 644-1, L. 644-2) : le demi-plafond de la CARPIMKO, en 2026, ne s'oppose
    pas à l'infirmière au RSA ; la dispense de D. 642-4, elle, ne touchait que
    la base."""
    def carpimko(motif, fin):
        carriere, _ = _dispense(simulateur, "auxiliaire_medical", motif,
                                range(2010, fin + 1), liquidation=2028)
        return next(p["montant"] for p in simulateur.simuler(carriere).dictionnaire()
                    ["scenarios"]["actuel"]["par_regime"]
                    if p["regime"] == "carpimko_complementaire")

    assert carpimko("rsa", 2025) == pytest.approx(carpimko("", 2025))
    assert carpimko("rsa", 2026) < carpimko("", 2026)
    assert carpimko("activite_non_principale", 2026) == pytest.approx(carpimko("", 2026))


#: Le jumeau JavaScript : les lignes d'un relevé qui porte des dispenses, et
#: le résultat entier.
_JUMEAU_DISPENSES = """
import { readFileSync } from "node:fs";
import { Simulateur } from "./moteur/js/simulateur.js";
const cas = JSON.parse(process.argv[1]);
const simulateur = new Simulateur(JSON.parse(readFileSync("./moteur/donnees.json", "utf8")));
const sortie = cas.map(({ releve, naissance, age }) => {
  const carriere = simulateur.carriereReleve({
    annee_naissance: naissance, sexe: "F", releve, age_liquidation: age });
  return {
    lignes: carriere.lignes.map((l) => [l.annee, l.trimestres_valides,
      l.assiette_minimale_base, l.dispense_assiette_minimale]),
    resultat: simulateur.simuler(carriere).dictionnaire(),
  };
});
process.stdout.write(JSON.stringify(sortie));
"""


def _proches(obtenu, attendu, chemin="") -> list[str]:
    if attendu is None:
        return []
    if isinstance(attendu, bool) or not isinstance(attendu, (int, float)):
        if isinstance(attendu, dict):
            return [e for cle, v in attendu.items()
                    for e in _proches(obtenu.get(cle), v, f"{chemin}.{cle}")]
        if isinstance(attendu, list):
            if not isinstance(obtenu, list) or len(obtenu) != len(attendu):
                return [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]
            return [e for i, v in enumerate(attendu)
                    for e in _proches(obtenu[i], v, f"{chemin}[{i}]")]
        return [] if obtenu == attendu else [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]
    if obtenu is None or abs(obtenu - attendu) > 1e-9 * max(1.0, abs(attendu)):
        return [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]
    return []


@pytest.fixture
def deux_moteurs(simulateur):
    """Ce qui rend les lignes de chaque relevé, par année, en Python, une fois
    vérifié que le JavaScript rend les mêmes lignes et le même résultat entier.
    Une fixture, et non une fonction : la garde des présomptions saute les
    tests qui la demandent, `"node"` lu dans sa source (`tests/conftest.py`),
    le portage ne décalant pas les siennes."""
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
                "lignes": [[l.annee, l.trimestres_valides, l.assiette_minimale_base,
                            l.dispense_assiette_minimale] for l in carriere.lignes],
                "resultat": _fini(simulateur.simuler(carriere).dictionnaire())})
        execution = subprocess.run(
            ["node", "--input-type=module", "-e", _JUMEAU_DISPENSES, json.dumps(cas)],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
        assert execution.returncode == 0, execution.stderr[-2000:]
        ecarts = _proches(json.loads(execution.stdout), attendus)
        assert not ecarts, ecarts[:10]
        return lignes

    return confronter


def test_les_deux_moteurs_servent_les_memes_droits_aux_dispenses(deux_moteurs):
    """Les lignes et le résultat entier, en Python et en JavaScript, pour un
    artisan au RSA puis saisonnier et une infirmière libérale au RSA."""
    cas = [
        {"naissance": 1962, "age": 65.0, "releve": [
            {"annee": a, "affiliation": "artisan", "revenu": 3000.0 + 100 * (a % 7),
             "dispense_assiette_minimale": ("" if a < 2016 else "rsa" if a < 2021
                                            else "activite_saisonniere")}
            for a in range(1995, 2027)]},
        {"naissance": 1963, "age": 65.0, "releve": [
            {"annee": a, "affiliation": "auxiliaire_medical", "revenu": 4000.0,
             "dispense_assiette_minimale": "rsa" if a % 2 else "activite_non_principale"}
            for a in range(2005, 2028)]},
    ]
    _, infirmiere = deux_moteurs(cas)
    assert any(not l.dispense_assiette_minimale and l.assiette_minimale_base > 0
               for l in infirmiere.values())


# --- L'assiette minimale, de 1973 à nos jours ------------------------------------

FRANCS_PAR_EURO = 6.55957


def test_l_assiette_minimale_des_artisans_et_commercants_court_depuis_1973(deux_moteurs):
    """« Toutefois, le montant de la cotisation annuelle ne peut être inférieur
    à celui de la cotisation qui serait due au titre d'un revenu égal à 200 fois
    le montant horaire du salaire minimum de croissance en vigueur le 1er janvier
    de l'année considérée » (décret n° 73-76 du 22 janvier 1973, article 2,
    LEGIARTI000006765785, du 24 janvier 1973 au 21 décembre 1985, que D. 633-2
    reprend mot pour mot) : l'artisane et la commerçante qui déclarent 100 € par
    an cotisent sur 910 F en 1973, 2 586 F en 1980 et 4 556 F en 1984, ce que
    les tables de la caisse publient, et valident un trimestre chaque année ;
    en 1972, aux caisses d'avant l'alignement, aucun minimum. Dans les deux
    moteurs."""
    lignes = deux_moteurs([
        {"naissance": 1945, "age": 65.0, "releve": [
            {"annee": a, "affiliation": metier, "revenu": 100.0} for a in range(1970, 1990)]}
        for metier in ("artisan", "commercant")])
    for metier in lignes:
        assert metier[1972].assiette_minimale_base == 0.0
        for annee, francs in ((1973, 910), (1980, 2586), (1984, 4556)):
            assert metier[annee].assiette_minimale_base == pytest.approx(
                francs / FRANCS_PAR_EURO, rel=1e-6), annee
            assert metier[annee].trimestres_valides == 1, annee


def test_l_assiette_minimale_de_2022_est_celle_du_decret_n_2022_1438(deux_moteurs):
    """« Par dérogation aux articles D. 633-2 et D. 642-4 du code de la sécurité
    sociale, la cotisation annuelle due au titre de l'année 2022 en application
    des articles L. 633-1 et L. 642-1 du même code ne peut être calculée sur une
    assiette inférieure à 4 758 euros » (décret n° 2022-1438 du 16 novembre
    2022, article 1er, JORFARTI000046566175) : de quoi « valider trois
    trimestres », dit sa notice, à 1 585,50 € le trimestre, quand 11,5 % du
    plafond gelé, 4 730,64 €, n'en valident que deux. L'artisane et la libérale
    qui déclarent 3 000 € par an valident trois trimestres en 2021, en 2022 et
    en 2023. Dans les deux moteurs."""
    lignes = deux_moteurs([
        {"naissance": 1962, "age": 64.0, "releve": [
            {"annee": a, "affiliation": metier, "revenu": 3000.0} for a in range(2020, 2025)]}
        for metier in ("artisan", "profession_liberale")])
    for metier in lignes:
        assert metier[2021].assiette_minimale_base == pytest.approx(4730.64)
        assert metier[2022].assiette_minimale_base == 4758.0
        assert [metier[a].trimestres_valides for a in (2021, 2022, 2023)] == [3, 3, 3]


# --- Le revenu cotisé -----------------------------------------------------------


def test_les_trimestres_cotises_de_l_exemple_de_la_caisse(simulateur):
    """L'exemple de la caisse, « Détermination des trimestres cotisés au régime
    des indépendants par année civile » (version du 2 juin 2023) : 1 000 € de
    cotisations de retraite de base versées en 2016, au taux de 17,65 %, font un
    « revenu cotisé » de 5 665,72 € et valident 3,90 trimestres, « arrondis à 3
    trimestres cotisés », sur un revenu minimum de 1 450,50 € par trimestre. Le
    modèle, qui porte au compte le revenu de la cotisation définitive (D. 633-10,
    R. 634-1 ; action 177, étape 5), en valide autant."""
    revenu_cotise = 1000.0 / 0.1765
    assert revenu_cotise == pytest.approx(5665.72, abs=0.005)
    carriere = simulateur.carriere_releve(
        1962, "F", [LigneRelevee(2016, "artisan", revenu_cotise)], 64.0)
    (annee,) = [ligne for ligne in carriere.lignes if ligne.annee == 2016]
    assert annee.trimestres_valides == 3
