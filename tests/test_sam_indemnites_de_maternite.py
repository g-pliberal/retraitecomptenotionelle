"""Les indemnités journalières de maternité au salaire annuel moyen.

Pour les pensions prenant effet à compter du 1er septembre 2023, les congés de
maternité débutés avant le 1er janvier 2012 portent au compte de l'année de la
naissance un montant forfaitaire : une fraction du salaire médian de l'année
précédente (loi n° 2010-1330, article 118, VI, second alinéa ; R. 351-29, IV
et V ; arrêté du 29 avril 2024, JORFTEXT000049496470). La circulaire Cnav
2025/11 du 28 mars 2025 en donne l'arrondi, l'écrêtement et des exemples
chiffrés, rejoués ici tels qu'elle les écrit.
"""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from retraite_notionnelle.config import RACINE_PROJET
from retraite_notionnelle.donnees.chargement import charger_yaml
from retraite_notionnelle.types_du_pont.carriere import AnneeCarriere

from facade import Carriere, liquider, Simulateur

FICHE = RACINE_PROJET / "data" / "reference" / "regles" / "sam_indemnites_de_maternite.yaml"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _forfait() -> dict:
    """Les paramètres du forfait, dans la version en vigueur de la fiche."""
    version = charger_yaml(FICHE)["versions"][-1]
    assert version["bornes"]["liquidation.date_effet"][1] is None
    return json.loads(json.dumps(version["contenu"]["parametres"]["forfait"]))


_PORTAGE = """
import { forfaitsDeMaternite, retenirAvecLesIndemnites } from "./moteur/js/droit/liquider.js";
const [fonction, ...arguments_] = JSON.parse(process.argv[1]);
const fonctions = { forfaitsDeMaternite, retenirAvecLesIndemnites };
process.stdout.write(JSON.stringify(fonctions[fonction](...arguments_)));
"""


def _portage(fonction: str, *arguments):
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne se vérifie pas ici")
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _PORTAGE, json.dumps([fonction, *arguments])],
        cwd=RACINE_PROJET, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    return json.loads(execution.stdout)


def test_le_salaire_median_est_celui_de_l_arrete():
    """Arrêté du 29 avril 2024, article 1er (JORFARTI000049496475) : soixante-deux
    années, de 1950 (336 euros) à 2011 (20 793 euros) ; les années que les
    exemples de la circulaire Cnav 2025/11 citent, et quelques autres."""
    median = _forfait()["salaire_median"]
    assert sorted(int(annee) for annee in median) == list(range(1950, 2012))
    lus = {1950: 336, 1955: 546, 1960: 941, 1961: 991, 1962: 1128, 1968: 1616, 1972: 2439,
           1976: 4256, 1977: 4718, 1980: 6712, 1982: 8592, 1989: 12554, 1990: 13223,
           1993: 14487, 1994: 14511, 1999: 16051, 2000: 16310, 2001: 16505, 2002: 16941,
           2006: 18374, 2009: 19965, 2010: 20346, 2011: 20793}
    assert {annee: median[str(annee)] for annee in lus} == lus
    assert sum(median.values()) == 524_647


def test_le_montant_forfaitaire_est_celui_des_exemples_de_la_caisse():
    """Circulaire Cnav 2025/11, § 2.4 : des jumeaux nés en 1990, 12 554 € ×
    298/365 = 10 249,567, soit 10 250 € ; une première naissance en 2002,
    16 505 × 140/365 = 6 330,68, soit 6 331 € ; une deuxième en 2003, 16 941 ×
    140/365, soit 6 498 € ; une troisième en 2007, 18 374 × 228/365 =
    11 477,45, soit 11 477 €. Le montant va à l'année de la naissance."""
    forfait = _forfait()
    assert _portage("forfaitsDeMaternite", forfait, ["1990-06-15", "1990-06-15"]) \
        == [[1990, 10250]]
    assert _portage("forfaitsDeMaternite", forfait, ["2002-04-01", "2003-09-01"]) \
        == [[2002, 6331], [2003, 6498]]
    assert _portage("forfaitsDeMaternite", forfait,
                    ["1999-01-10", "2001-03-02", "2007-05-20"])[-1] == [2007, 11477]


def test_les_fractions_sont_celles_de_r_351_29():
    """R. 351-29, V : 140/365 pour les deux premières naissances, 228/365
    au-delà de la deuxième, 298/365 pour des jumeaux, 403/365 pour une
    naissance multiple de plus de deux enfants. Posé à la main sur le salaire
    médian de 1979, 5 869 € : 2 251,12 ; 3 666,11 ; 4 791,68 ; 6 480,02."""
    forfait = _forfait()
    assert _portage("forfaitsDeMaternite", forfait,
                    ["1980-02-01", "1980-11-30"]) == [[1980, 2251], [1980, 2251]]
    assert _portage("forfaitsDeMaternite", forfait,
                    ["1975-02-01", "1977-02-01", "1980-02-01"])[-1] == [1980, 3666]
    assert _portage("forfaitsDeMaternite", forfait, ["1980-02-01"] * 2) == [[1980, 4792]]
    assert _portage("forfaitsDeMaternite", forfait, ["1980-02-01"] * 3) == [[1980, 6480]]
    # Après des jumeaux, la mère a déjà mis au monde deux enfants (L. 331-4).
    assert _portage("forfaitsDeMaternite", forfait,
                    ["1975-02-01", "1975-02-01", "1980-02-01"])[-1] == [1980, 3666]


def test_le_forfait_ne_vaut_que_pour_un_conge_debute_avant_2012():
    """Loi n° 2010-1330, article 118, VI : les « congés de maternité ayant
    débuté avant le 1er janvier 2012 ». Le congé débute six semaines avant
    l'accouchement, huit pour un troisième enfant, douze pour des jumeaux
    (L. 331-3 et L. 331-4) : une naissance du 31 janvier 2012 est d'un congé
    de 2011, sur le salaire médian de 2011 (20 793 × 140/365 = 7 975,40) ;
    celle du 1er mars 2012, d'un congé de 2012. Avant 1951, l'arrêté ne fixe
    aucun salaire médian."""
    forfait = _forfait()
    assert _portage("forfaitsDeMaternite", forfait, ["2011-12-31"]) == [[2011, 7804]]
    assert _portage("forfaitsDeMaternite", forfait, ["2012-01-31"]) == [[2012, 7975]]
    assert _portage("forfaitsDeMaternite", forfait, ["2012-02-11"]) == [[2012, 7975]]
    assert _portage("forfaitsDeMaternite", forfait, ["2012-02-12"]) == []
    assert _portage("forfaitsDeMaternite", forfait, ["2012-03-01"]) == []
    assert _portage("forfaitsDeMaternite", forfait,
                    ["2001-01-01", "2003-01-01", "2012-02-25"])[2:] == [[2012, 12989]]
    assert _portage("forfaitsDeMaternite", forfait, ["2012-03-24"] * 2) == [[2012, 16976]]
    assert _portage("forfaitsDeMaternite", forfait, ["2012-03-25"] * 2) == []
    assert _portage("forfaitsDeMaternite", forfait, ["1950-07-01", "1951-07-01"]) \
        == [[1951, 129]]


def test_l_ecretement_est_celui_des_exemples_de_la_caisse():
    """Circulaire Cnav 2025/11, § 2.4.1.4 et 2.4.2. Avant 2005, le total peut
    passer le plafond : en 2002, 25 000 + 6 331 = 31 331 €, pour un plafond de
    28 224 €. Depuis 2005, les indemnités s'écrêtent en priorité : en 2007,
    25 800 + 11 477 ramenés au plafond, 32 184 €. Sous le plafond, tout
    compte : en 2003, 4 600 + 6 498 = 11 098 €."""
    forfait = _forfait()
    assert _portage("retenirAvecLesIndemnites", forfait, 2002, 25000, 6331, 28224) == 31331
    assert _portage("retenirAvecLesIndemnites", forfait, 2007, 25800, 11477, 32184) == 32184
    assert _portage("retenirAvecLesIndemnites", forfait, 2003, 4600, 6498, 29184) == 11098
    # Posé à la main : la bascule est au 1er janvier 2005, et un salaire déjà
    # au plafond ne reçoit plus rien.
    assert _portage("retenirAvecLesIndemnites", forfait, 2004, 29000, 5000, 29712) == 34000
    assert _portage("retenirAvecLesIndemnites", forfait, 2005, 29000, 5000, 30192) == 30192
    assert _portage("retenirAvecLesIndemnites", forfait, 2005, 30192, 5000, 30192) == 30192


def _carriere(sexe: str, age_liquidation: float, naissances, lignes=None,
              affiliation: str = "salarie_prive_non_cadre") -> Carriere:
    lignes = lignes or [(annee, 30_000.0 if annee == 2007 else 15_000.0)
                        for annee in range(1995, 2011)]
    return Carriere.depuis_lignes(
        1960, sexe,
        [AnneeCarriere(annee=annee, revenu=revenu, affiliation=affiliation,
                       trimestres_valides=4) for annee, revenu in lignes],
        age_liquidation=age_liquidation, nombre_enfants=len(naissances),
        naissances_enfants=tuple(naissances))


def _moyenne(simulateur, carriere, supplements: dict) -> float:
    """La moyenne posée à la main : chaque salaire, son supplément, le
    coefficient de l'année."""
    macro = simulateur.macro
    retenus = [(ligne.revenu + supplements.get(ligne.annee, 0.0))
               * macro.coefficient_revalorisation_portee_au_compte(
                   ligne.annee, carriere.annee_liquidation, carriere.mois_liquidation)
               for ligne in carriere.lignes]
    return sum(retenus) / len(retenus)


def _sam(simulateur, carriere, code: str = "regime_general") -> float:
    annee = carriere.annee_liquidation
    return liquider.salaire_de_reference(
        simulateur.scenario_actuel, code, carriere,
        simulateur.catalogue[code].periode(annee), annee, True, carriere.annee_naissance)


NAISSANCES = ("1998-05-12", "2007-03-03", "2013-06-01")


def test_la_mere_recoit_le_forfait_depuis_septembre_2023(simulateur):
    """Née en janvier 1960, seize années à 15 000 €, 30 000 € en 2007 ; trois
    enfants, en 1998, 2007 et 2013. Pension de février 2024 : 1998 reçoit
    15 548 × 140/365 = 5 963,62, soit 5 964 € ; 2007, 18 374 × 140/365 =
    7 047,56, soit 7 048 €, que le plafond de 32 184 € ramène à 2 184 € ; la
    naissance de 2013 est d'un congé d'après 2011. Pension de février 2023 :
    rien, comme pour le père."""
    mere = _carriere("F", 64, NAISSANCES)
    assert (mere.annee_liquidation, mere.mois_liquidation) == (2024, 2)
    assert _sam(simulateur, mere) == pytest.approx(
        _moyenne(simulateur, mere, {1998: 5_964.0, 2007: 2_184.0}), abs=0.005)

    avant = _carriere("F", 63, NAISSANCES)
    assert _sam(simulateur, avant) == pytest.approx(_moyenne(simulateur, avant, {}), abs=0.005)
    pere = _carriere("H", 64, NAISSANCES)
    assert _sam(simulateur, pere) == pytest.approx(_moyenne(simulateur, pere, {}), abs=0.005)


def test_le_forfait_va_aussi_a_la_salariee_agricole_et_non_a_l_independante(simulateur):
    """Circulaire Cnav 2025/11, § 1 : « Ces dispositions s'appliquent aux
    salariés du régime général et aux salariés du régime agricole. L'article
    D. 634-1 CSS exclut expressément l'article R. 351-29 CSS des textes
    applicables aux travailleurs indépendants. »"""
    agricole = _carriere("F", 64, NAISSANCES[:1], affiliation="salarie_agricole")
    assert _sam(simulateur, agricole, "msa_salaries") == pytest.approx(
        _moyenne(simulateur, agricole, {1998: 5_964.0}), abs=0.005)
    lignes = [(annee, 15_000.0) for annee in range(1995, 2011)]
    sans = _carriere("F", 64, (), lignes=lignes, affiliation="artisan")
    avec = _carriere("F", 64, NAISSANCES[:1], lignes=lignes, affiliation="artisan")
    assert _sam(simulateur, avec, "regime_general") == _sam(simulateur, sans, "regime_general")


def test_le_forfait_demande_une_cotisation_l_annee_de_la_naissance_ou_la_precedente(simulateur):
    """R. 351-29, IV : « une affiliation aux assurances sociales du régime
    général [...] ayant fait l'objet d'un versement de cotisations, quel qu'en
    soit le montant », « au cours de l'année civile de la naissance [...] ou
    de l'année civile précédant celle-ci ». Une naissance de 1994, pour une
    carrière commencée en 1995, vaut par l'année précédente à une naissance de
    1996 seulement ; et le forfait ne valide aucun trimestre (circulaire Cnav
    2025/11, § 2.4.2) : une année sans salaire au compte n'entre pas dans la
    moyenne."""
    trop_tot = _carriere("F", 64, ("1994-06-01",))
    assert _sam(simulateur, trop_tot) == pytest.approx(
        _moyenne(simulateur, trop_tot, {}), abs=0.005)
    lignes = [(annee, 15_000.0) for annee in range(1995, 2011) if annee != 2000]
    interrompue = _carriere("F", 64, ("2000-06-01",), lignes=lignes)
    assert _sam(simulateur, interrompue) == pytest.approx(
        _moyenne(simulateur, interrompue, {}), abs=0.005)


def test_les_parents_nes_avant_1948_gardent_les_annees_de_leur_generation(simulateur):
    """R. 173-3-2, III (LEGIARTI000054589934) : « Par dérogation au I, le nombre
    d'années mentionné à ce I est égal, pour les assurés nés avant le 1er
    janvier 1948, à celui mentionné à l'article R. 351-29-1 ». Les vingt-quatre
    et vingt-trois années des parents sont au I : la mère née en 1947 garde
    ses vingt-quatre années, celle de 1948 passe de vingt-cinq à vingt-trois.
    La session indépendante de la preuve du 20 novembre 2026 l'a relevé."""
    lignes = [(annee, 15_000.0) for annee in range(1980, 2000)]

    def annees(naissance: int) -> int:
        mere = Carriere.depuis_lignes(
            naissance, "F",
            [AnneeCarriere(annee=annee, revenu=revenu, affiliation="salarie_prive_non_cadre",
                           trimestres_valides=4) for annee, revenu in lignes],
            age_liquidation=2027 - naissance, nombre_enfants=2,
            naissances_enfants=("1975-04-04", "1978-05-05"))
        periode = simulateur.catalogue["regime_general"].periode(mere.annee_liquidation)
        return liquider.nombre_d_annees_retenues(
            simulateur.scenario_actuel, periode, mere, naissance, 2)

    assert annees(1947) == 24
    assert annees(1948) == 23
