"""L'exonération Lodeom : en Guadeloupe, en Guyane, en Martinique et à La Réunion,
l'employeur qui y a droit ne reçoit pas la réduction générale dégressive unique.

L. 752-3-2 (LEGIARTI000053280451, en vigueur au 1er janvier 2026 ; ses barèmes
ne changent ni le 1er juillet 2026 ni en 2028) et D. 752-7 (LEGIARTI000052196887)
lui donnent une exonération totale des cotisations patronales du périmètre de
L. 241-13 d'avant 2025 jusqu'à 1,3, 2 ou 1,7 SMIC selon son barème —
compétitivité, compétitivité renforcée, innovation et croissance —, dégressive
ensuite, nulle à 2,2, 2,7 ou 3,5 SMIC, le dernier barème s'en tenant aux
cotisations de 1,7 SMIC de 1,7 à 2,5 SMIC. Elle ne se cumule avec aucune autre
(VI). T, la valeur maximale du coefficient, est la somme des taux du périmètre
pour une rémunération égale au SMIC (D. 752-7, III) : 0,3241 dans une entreprise
de cinquante salariés et plus, l'employeur type du dépôt (BOSS, § 1380, que cite
la fiche Sage de janvier 2026). L'employeur garde les taux réduits de maladie
(7 %) et de famille (3,45 %), que la loi de financement pour 2026 ôte aux autres
(loi n° 2025-1403, article 40, V et VI) : jusqu'à 2,5 et 3,5 fois 1 820 heures
du SMIC du 31 décembre 2023 (décret n° 2025-1446, article 3), 11,52 € de l'heure
(arrêté du 26 avril 2023).

Les valeurs attendues sont posées à la main depuis ces textes : aucun exemple
chiffré de 2026 n'a pu être lu à la source, le BOSS et l'Urssaf refusant la
connexion de la session. L'arrondi du coefficient à quatre décimales est celui
du BOSS (fiche Sage) et du simulateur de l'Urssaf ; D. 752-7 ne le dit pas.

Le modèle refait T des fiches de régime, comme le coefficient maximal de la
réduction générale (``test_remuneration.py``) : 0,32412 et non 0,3241, la part
patronale de l'Agirc-Arrco y valant 60 % de 7,87 %, 4,722 %, quand le BOSS
compte 4,72 %. Ce qui suit T se compare donc à un dix-millième près ; les
coefficients arrondis sont pris loin d'un demi dix-millième, où l'écart ne
change pas l'arrondi.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import Affiliations, LigneRelevee, prolonger_releve
from retraite_notionnelle.donnees.regimes import CatalogueRegimes
from retraite_notionnelle.remuneration import (
    ConstructeurFiche,
    bloc_droit_en_vigueur,
    charger_prelevements,
)
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
PARAMETRES = Parametres()
STATUT = "salarie_prive_non_cadre"
ANNEE = 2026
#: 1 820 heures du SMIC du 1er janvier 2026 (D. 241-7, IV) : 21 876,40 €.
SMIC = 12.02 * 1820
PLAFOND = 48_060.0
#: BOSS, § 1380 : « au 1er janvier 2026, la valeur maximale de T » d'une
#: entreprise de cinquante salariés et plus.
T = 0.3241
#: 2,5 et 3,5 fois 1 820 heures de 11,52 € : 52 416 € et 73 382,40 €.
SEUIL_MALADIE = 2.5 * 11.52 * 1820
SEUIL_FAMILLE = 3.5 * 11.52 * 1820
#: Ce que l'employeur verse hors du périmètre, rapporté au brut : les accidents
#: du travail au-delà des 0,49 point que L. 241-13 y fait entrer, l'AGS et le
#: financement du dialogue social.
HORS_PERIMETRE = 0.0300 - 0.0049 + 0.0025 + 0.00016


@pytest.fixture(scope="module")
def pieces():
    profil = charger_prelevements(PARAMETRES.racine_donnees).profil("salarie_prive")
    bloc = bloc_droit_en_vigueur(CatalogueRegimes(PARAMETRES.racine_donnees),
                                 Affiliations(PARAMETRES.racine_donnees), STATUT, ANNEE)
    return {"profil": profil, "bloc": bloc}


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _fiche(pieces, brut: float, lodeom: str = ""):
    return ConstructeurFiche(pieces["profil"], lodeom).fiche(
        ANNEE, brut, PLAFOND, SMIC, pieces["bloc"])


def _employeur(fiche, code: str) -> float:
    return next(ligne.employeur for ligne in fiche.lignes if ligne.code == code)


def test_t_est_la_somme_des_taux_du_perimetre_pour_un_salaire_au_smic(pieces):
    """Les composantes de la réduction générale, la maladie et la famille à
    leurs taux réduits : 40,21 % moins 6 et 1,8 points."""
    lodeom = pieces["profil"].lodeom
    assert lodeom.coefficient_maximal == T
    assert sum(lodeom.composantes.values()) == pytest.approx(T, abs=1e-12)
    generale = pieces["profil"].reduction_generale
    assert set(lodeom.composantes) == set(generale.composantes)
    ecarts = {code: generale.composantes[code] - taux
              for code, taux in lodeom.composantes.items()
              if generale.composantes[code] != taux}
    assert ecarts == pytest.approx({"maladie": 0.06, "famille": 0.018})
    assert lodeom.composantes_retraite == generale.composantes_retraite


@pytest.mark.parametrize("bareme, multiple", [
    ("competitivite", 1.2),
    ("competitivite_renforcee", 1.9),
    ("innovation_et_croissance", 1.6),
])
def test_sous_son_seuil_l_exoneration_efface_tout_le_perimetre(pieces, bareme, multiple):
    """« Le montant de l'exonération est égal au montant des cotisations et
    contributions à la charge de l'employeur » du périmètre (III) : il ne
    reste à verser que ce qui en est dehors, et la maladie et la famille
    portent leurs taux réduits."""
    brut = multiple * SMIC
    fiche = _fiche(pieces, brut, bareme)
    assert fiche.lodeom == bareme
    assert fiche.reduction_generale == pytest.approx(T * brut, rel=1e-4)
    assert fiche.cotisations_patronales == pytest.approx(HORS_PERIMETRE * brut, abs=1e-6)
    assert _employeur(fiche, "maladie") == pytest.approx(0.07 * brut, abs=1e-6)
    assert _employeur(fiche, "famille") == pytest.approx(0.0345 * brut, abs=1e-6)
    assert fiche.part_retraite_dans_la_reduction == pytest.approx(0.1667 / T, rel=1e-4)


def test_sans_lodeom_la_reduction_generale_et_les_taux_pleins(pieces):
    """Le salarié du privé de métropole, ou d'un employeur d'outre-mer qui n'y
    a pas droit : 13 % et 5,25 %, et la réduction générale de 1,2 SMIC,
    0,02 + 0,3821 × (½ × (3 / 1,2 − 1))^1,75 = 0,25096, arrondi à 0,2510."""
    brut = 1.2 * SMIC
    fiche = _fiche(pieces, brut)
    assert fiche.lodeom == ""
    assert _employeur(fiche, "maladie") == pytest.approx(0.13 * brut, abs=1e-6)
    assert _employeur(fiche, "famille") == pytest.approx(0.0525 * brut, abs=1e-6)
    assert fiche.reduction_generale == pytest.approx(0.2510 * brut, abs=1e-6)


@pytest.mark.parametrize("bareme, multiple, coefficient", [
    # 1,3 × T / 0,9 × (2,2 / 1,6 − 1) = 0,4681444 × 0,375 = 0,1755542
    ("competitivite", 1.6, 0.1756),
    # 2 × T / 0,7 × (2,7 / 2,2 − 1) = 0,926 × 0,2272727 = 0,2104545
    ("competitivite_renforcee", 2.2, 0.2105),
    # 1,7 × T × (3,5 / 3 − 1) = 0,55097 × 0,1666667 = 0,0918283
    ("innovation_et_croissance", 3.0, 0.0918),
])
def test_au_dela_le_coefficient_de_d_752_7(pieces, bareme, multiple, coefficient):
    """Le produit du brut par le coefficient de D. 752-7, II, arrondi à
    quatre décimales."""
    brut = multiple * SMIC
    fiche = _fiche(pieces, brut, bareme)
    assert fiche.reduction_generale == pytest.approx(coefficient * brut, abs=1e-6)


def test_l_innovation_s_en_tient_aux_cotisations_de_1_7_smic_jusqu_a_2_5_smic(pieces):
    """« Dans la limite de la part correspondant à un revenu d'activité de
    l'année égal au salaire minimum de croissance annuel majoré de 70 % »
    (III, C) : 0,3241 × 1,7 × 21 876,40 = 12 053,24 €."""
    for multiple in (1.7, 2.0, 2.4999):
        fiche = _fiche(pieces, multiple * SMIC, "innovation_et_croissance")
        assert fiche.reduction_generale == pytest.approx(T * 1.7 * SMIC, rel=1e-4), multiple


@pytest.mark.parametrize("bareme, multiple", [
    ("competitivite", 2.2),
    ("competitivite", 2.5),
    ("competitivite_renforcee", 2.7),
    ("innovation_et_croissance", 3.5),
])
def test_nulle_a_sa_sortie_et_jamais_relayee_par_la_reduction_generale(
        pieces, bareme, multiple):
    """Le barème s'éteint à son seuil de sortie ; au-delà, l'employeur ne
    reprend pas la réduction générale, qui ne se cumule pas avec elle (VI) et
    que le simulateur de l'Urssaf écarte de même — elle vaudrait 2,68 % du
    brut à 2,5 SMIC."""
    assert _fiche(pieces, multiple * SMIC, bareme).reduction_generale == 0.0


def test_les_taux_reduits_s_arretent_a_2_5_et_3_5_smic_de_2023(pieces):
    """La maladie à 7 % jusqu'à 52 416 €, la famille à 3,45 % jusqu'à
    73 382,40 € : des montants fixes, que le SMIC de 2026 ne déplace pas."""
    bareme = "innovation_et_croissance"
    au_seuil = _fiche(pieces, SEUIL_MALADIE, bareme)
    assert _employeur(au_seuil, "maladie") == pytest.approx(0.07 * SEUIL_MALADIE, abs=1e-6)
    passe = SEUIL_MALADIE + 1.0
    au_dela = _fiche(pieces, passe, bareme)
    assert _employeur(au_dela, "maladie") == pytest.approx(0.13 * passe, abs=1e-6)
    assert _employeur(au_dela, "famille") == pytest.approx(0.0345 * passe, abs=1e-6)
    passe = SEUIL_FAMILLE + 1.0
    assert _employeur(_fiche(pieces, passe, bareme), "famille") == pytest.approx(
        0.0525 * passe, abs=1e-6)


def test_un_bareme_inconnu_est_refuse(pieces):
    with pytest.raises(ValueError, match="Lodeom"):
        ConstructeurFiche(pieces["profil"], "zone_franche")


def _releve(simulateur, lodeom: str = "") -> list[LigneRelevee]:
    """Deux années déclarées, puis la dernière prolongée jusqu'au départ, comme
    la saisie le fait d'un relevé (``contexte.py``)."""
    declare = [LigneRelevee(2025, STATUT, 33_000.0, lodeom=lodeom),
               LigneRelevee(2026, STATUT, 34_000.0, lodeom=lodeom)]
    return prolonger_releve(declare, DateMois(2039, 1), simulateur.macro)


def test_le_releve_la_declare_et_la_derniere_annee_la_prolonge(simulateur):
    """Déclarée sur les lignes du relevé, elle suit l'emploi que la dernière
    année prolonge jusqu'au départ : l'employeur ne verse que le reste, et le
    net du salarié ne bouge pas."""
    releve = _releve(simulateur, "competitivite")
    assert [ligne.annee for ligne in releve] == list(range(2025, 2039))
    assert {ligne.lodeom for ligne in releve} == {"competitivite"}
    carriere = simulateur.carriere_releve(1975, "F", releve, 64.0)
    assert {ligne.lodeom for ligne in carriere.lignes} == {"competitivite"}
    avec = simulateur.simuler(carriere).remuneration
    sans = simulateur.simuler(
        simulateur.carriere_releve(1975, "F", _releve(simulateur), 64.0)).remuneration
    assert len(avec.annees) == len(sans.annees) == 2038 - 2026 + 1
    for lodeom, generale in zip(avec.annees, sans.annees):
        assert lodeom.droit_en_vigueur.lodeom == "competitivite"
        assert generale.droit_en_vigueur.lodeom == ""
        assert lodeom.droit_en_vigueur.net == pytest.approx(generale.droit_en_vigueur.net)
        assert (lodeom.droit_en_vigueur.cout_du_travail
                < generale.droit_en_vigueur.cout_du_travail)


def test_un_independant_qui_la_declarerait_n_en_recoit_rien(simulateur):
    """L. 752-3-2 exonère des employeurs : l'artisan n'en a pas, et sa fiche
    de paie reste la sienne."""
    def fiches(lodeom):
        releve = [LigneRelevee(2026, "artisan", 34_000.0, lodeom=lodeom)]
        carriere = simulateur.carriere_releve(1975, "F", releve, 64.0)
        return [(a.droit_en_vigueur.cout_du_travail, a.droit_en_vigueur.lodeom)
                for a in simulateur.simuler(carriere).remuneration.annees]

    assert fiches("competitivite") == fiches("")


#: Le jumeau JavaScript : les mêmes fiches, et la même carrière.
_JUMEAU = """
import { readFileSync } from "node:fs";
import { CatalogueRegimes, Affiliations } from "./moteur/js/regimes.js";
import { BaremePrelevements, ConstructeurFiche, blocDroitEnVigueur }
  from "./moteur/js/remuneration.js";
import { Simulateur } from "./moteur/js/simulateur.js";
const { cas, releves, statut, annee, plafond, smic } = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("./moteur/donnees.json", "utf8"));
const bloc = blocDroitEnVigueur(new CatalogueRegimes(paquet), new Affiliations(paquet),
  statut, annee);
const profil = new BaremePrelevements(paquet.prelevements_remuneration)
  .profil("salarie_prive");
const fiches = cas.map(([brut, lodeom]) => {
  const fiche = new ConstructeurFiche(profil, lodeom).fiche(
    annee, brut, plafond, smic, bloc);
  return [fiche.coutDuTravail, fiche.reductionGenerale, fiche.lodeom,
    fiche.partRetraiteDansLaReduction,
    fiche.lignes.map((ligne) => [ligne.code, ligne.salarie, ligne.employeur])];
});
const simulateur = new Simulateur(paquet);
const carrieres = releves.map((releve) => simulateur.simuler(simulateur.carriereReleve({
  annee_naissance: 1975, sexe: "F", releve, age_liquidation: 64,
})).remuneration.annees.map((a) => [a.annee, a.droitEnVigueur.coutDuTravail,
  a.droitEnVigueur.reductionGenerale, a.droitEnVigueur.lodeom,
  a.proposition.brut, a.proposition.coutDuTravail]));
process.stdout.write(JSON.stringify({ fiches, carrieres }));
"""


def test_le_portage_javascript_rend_les_memes_fiches(pieces, simulateur):
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    baremes = ["", "competitivite", "competitivite_renforcee", "innovation_et_croissance"]
    cas = [(multiple * SMIC, bareme) for bareme in baremes
           for multiple in (0.9, 1.2, 1.3, 1.6, 2.0, 2.2, 2.4, 2.6, 3.0, 3.4, 3.6)]
    cas += [(SEUIL_MALADIE, "competitivite_renforcee"),
            (SEUIL_FAMILLE + 1.0, "innovation_et_croissance")]
    attendu_fiches = []
    for brut, bareme in cas:
        fiche = _fiche(pieces, brut, bareme)
        attendu_fiches.append([
            fiche.cout_du_travail, fiche.reduction_generale, fiche.lodeom,
            fiche.part_retraite_dans_la_reduction,
            [[ligne.code, ligne.salarie, ligne.employeur] for ligne in fiche.lignes]])
    releves = [_releve(simulateur, bareme) for bareme in baremes]
    attendu_carrieres = [
        [[a.annee, a.droit_en_vigueur.cout_du_travail,
          a.droit_en_vigueur.reduction_generale, a.droit_en_vigueur.lodeom,
          a.proposition.brut, a.proposition.cout_du_travail]
         for a in simulateur.simuler(
             simulateur.carriere_releve(1975, "F", releve, 64.0)).remuneration.annees]
        for releve in releves]
    entree = {
        "cas": cas, "statut": STATUT, "annee": ANNEE, "plafond": PLAFOND, "smic": SMIC,
        "releves": [[{"annee": l.annee, "affiliation": l.affiliation,
                      "revenu": l.revenu, "lodeom": l.lodeom} for l in releve]
                    for releve in releves],
    }
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _JUMEAU, json.dumps(entree)],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    obtenu = json.loads(execution.stdout)
    assert len(obtenu["fiches"]) == len(attendu_fiches)
    for rang, (attendue, rendue) in enumerate(zip(attendu_fiches, obtenu["fiches"])):
        assert rendue[2] == attendue[2], cas[rang]
        assert rendue[:2] + [rendue[3]] == pytest.approx(
            attendue[:2] + [attendue[3]], abs=1e-6), cas[rang]
        assert [ligne[0] for ligne in rendue[4]] == [ligne[0] for ligne in attendue[4]]
        assert [ligne[1:] for ligne in rendue[4]] == [
            pytest.approx(ligne[1:], abs=1e-6) for ligne in attendue[4]], cas[rang]
    assert len(obtenu["carrieres"]) == len(attendu_carrieres)
    for rendue, attendue in zip(obtenu["carrieres"], attendu_carrieres):
        assert [annee[3] for annee in rendue] == [annee[3] for annee in attendue]
        assert [annee[:3] + annee[4:] for annee in rendue] == [
            pytest.approx(annee[:3] + annee[4:], abs=1e-6) for annee in attendue]
