"""La pension minimum d'avant le 1er avril 1983 (action 138, étape 6).

Avant le minimum contributif, la pension au taux de soixante-cinq ans était
portée au « minimum de base prévu à l'article L. 345 du code de la sécurité
sociale », entier à soixante trimestres d'assurance dans le régime général ou
à l'ex-invalide, « réduit à autant de soixantièmes que l'assuré justifie de
trimestres d'assurance » sinon (décret n° 45-0179, article 70-5, rédaction de
1976) ; les décrets « fixant le montant de divers avantages de vieillesse » le
fixent avec l'allocation aux vieux travailleurs salariés, au même montant. Le
modèle ne servait aucun minimum avant 1983 (fiche ``minimum_contributif``,
versions ``pension_minimum_de_1945`` et ``pension_minimum_de_1976``).

L'assuré présumé né le 15 liquide au 1er du mois qui suit son anniversaire :
né le 15 mars 1915, il part à soixante-cinq ans le 1er avril 1980.
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.droit.commun import date_d_effet
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
LEGISLATION = RACINE / "data" / "reference" / "legislation"

#: L'AVTS du 1er décembre 1979, 7 400 F (décret n° 79-1057), et du 1er janvier
#: 1981, 8 500 F (décret n° 80-1159), en euros.
AVTS_DECEMBRE_1979 = 7_400 / 6.55957
AVTS_JANVIER_1981 = 8_500 / 6.55957


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, naissance: int, liquidation: float, debut: float,
              salaire: float, affiliation: str = "salarie_prive_non_cadre"):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, mois_naissance=3, jour_naissance=15, sexe="H",
        metiers=[Metier(affiliation=affiliation, age_debut=debut, niveau_salaire=salaire)],
        age_liquidation=liquidation, macro=simulateur.macro)
    resultat = simulateur.scenario_actuel.calculer(carriere)
    minimum = next((a for a in resultat.avantages_appliques
                    if a.code == "minimum_contributif"), None)
    return (date_d_effet(carriere), resultat,
            {p.regime: p for p in resultat.pensions_par_regime}, minimum)


@pytest.mark.parametrize("affiliation,regime", [
    ("salarie_prive_non_cadre", "regime_general"),
    ("salarie_agricole", "msa_salaries"),
])
def test_soixante_trimestres_ouvrent_le_minimum_entier(simulateur, affiliation, regime):
    """Quinze ans au demi-SMIC, liquidés à soixante-cinq ans en avril 1980 :
    912 € de pension, portés aux 7 400 F de l'AVTS."""
    effet, resultat, pensions, minimum = _calculer(simulateur, 1915, 65.0, 50.0, 0.5,
                                                   affiliation)
    assert effet == "1980-04-01"
    assert resultat.taux_liquidation == pytest.approx(0.50)
    assert pensions[regime].montant == pytest.approx(AVTS_DECEMBRE_1979, abs=0.01)
    assert minimum is not None and minimum.libelle == "Pension minimum (AVTS)"
    assert "porté à la pension minimum" in pensions[regime].detail


def test_sous_soixante_trimestres_le_minimum_se_reduit_en_soixantiemes(simulateur):
    """Vingt-huit trimestres en avril 1981 : 28/60 des 8 500 F."""
    effet, _, pensions, minimum = _calculer(simulateur, 1916, 65.0, 58.0, 0.5)
    assert effet == "1981-04-01"
    assert pensions["regime_general"].montant == pytest.approx(
        AVTS_JANVIER_1981 * 28 / 60, abs=0.01)
    assert minimum is not None


def test_la_pension_abattue_avant_soixante_cinq_ans_n_y_a_pas_droit(simulateur):
    """Cent trente-trois trimestres à soixante ans en 1978 : 25 %, le taux qui
    croît avec l'âge, et aucun minimum, quelle que soit la durée."""
    effet, resultat, pensions, minimum = _calculer(simulateur, 1918, 60.0, 20.0, 0.4)
    assert effet == "1978-04-01"
    assert resultat.taux_liquidation == pytest.approx(0.25)
    assert minimum is None
    assert "minimum" not in pensions["regime_general"].detail


@pytest.mark.parametrize("affiliation,regime", [
    ("artisan", "cancava"),
    ("commercant", "organic"),
])
def test_l_artisan_et_le_commercant_au_titre_de_leurs_periodes_d_apres_1972(
        simulateur, affiliation, regime):
    """Vingt-huit trimestres, tous d'après 1972, liquidés en avril 1981 : le
    minimum de base en soixantièmes, comme au régime général (décret
    n° 73-937, article 7)."""
    effet, _, pensions, minimum = _calculer(simulateur, 1916, 65.0, 58.0, 0.3, affiliation)
    assert effet == "1981-04-01"
    assert pensions[regime].montant == pytest.approx(AVTS_JANVIER_1981 * 28 / 60, abs=0.01)
    assert minimum is not None and minimum.par_regime[0][0] == regime


def test_avec_des_periodes_d_avant_1973_le_cumul_s_arrete_au_minimum_entier(simulateur):
    """Vingt-cinq ans d'artisanat, de 1956 à 1981 : la part d'après 1972 de la
    pension, portée à ses soixantièmes, dépasserait avec celle d'avant le
    minimum entier ; « l'application dudit article L. 345 ne peut avoir pour
    effet de porter à un montant supérieur à celui du minimum de base entier le
    montant cumulé » des deux (décret n° 73-937, article 7). Les années d'avant
    1973 ont leur pension, en points (action 138, étape 18) : c'est la somme des
    deux qui s'arrête au minimum entier."""
    _, _, pensions, minimum = _calculer(simulateur, 1916, 65.0, 40.0, 0.3, "artisan")
    assert pensions["cancava_avant_1973"].montant > 0
    assert (pensions["cancava"].montant + pensions["cancava_avant_1973"].montant
            == pytest.approx(AVTS_JANVIER_1981, abs=0.01))
    assert minimum is not None


def test_l_artisan_abattu_avant_soixante_cinq_ans_n_y_a_pas_droit(simulateur):
    """Le taux de soixante ans, en 1978 : 25 %, et aucun minimum, comme au
    régime général, même quand la durée tous régimes atteindrait la durée
    requise."""
    _, resultat, _, minimum = _calculer(simulateur, 1918, 60.0, 20.0, 0.3, "artisan")
    assert resultat.taux_liquidation == pytest.approx(0.25)
    assert minimum is None


def test_la_regle_bascule_au_1er_avril_1983(simulateur):
    """La pension minimum vaut jusqu'au 31 mars 1983, le minimum contributif
    depuis ; avant le 12 mai 1976, la règle est présumée, au niveau estimé."""
    minimum = simulateur.scenario_actuel.minimum_contributif
    mars, avril = minimum.regle("1983-03-01"), minimum.regle("1983-04-01")
    assert not mars["existe"] and mars["pension_minimum"]["trimestres_du_minimum_entier"] == 60
    assert avril["existe"] and not avril.get("pension_minimum")
    assert minimum.regle("1976-05-01")["fiabilite"] == "estimee"
    assert "fiabilite" not in minimum.regle("1976-06-01")
    assert minimum.pension_minimum(1983, 3)[0] == pytest.approx(11_300 / 6.55957)
    assert minimum.pension_minimum(1944, 12) == (0.0, Fiabilite.CERTIFIEE)


def test_la_serie_datee_redonne_l_avts_de_chaque_31_decembre():
    """Chaque montant au 31 décembre de la série datée est celui de la colonne
    ``avts`` du minimum vieillesse d'avant l'ASPA : les deux tables lisent le
    même barème de la Cnav."""
    def lire(nom):
        with (LEGISLATION / nom).open(encoding="utf-8") as flux:
            return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))

    datees = sorted((l["date"], float(l["valeur"])) for l in lire("pension_minimum_avant_1983.csv"))
    annuelles = {int(l["annee"]): float(l["avts"])
                 for l in lire("minimum_vieillesse_avant_2007.csv")}
    for annee in range(1945, 2007):
        au_31 = [valeur for jour, valeur in datees if jour <= f"{annee}-12-31"][-1]
        assert au_31 == pytest.approx(annuelles[annee], abs=1e-6), annee


REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "40", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "interruptions": "", "liquidation": "65", "naissance": "1915", "naissance_mois": "3",
    "primes": "0", "profil": "plat", "projection": "cor_reference", "salaire": "0.3",
    "sexe": "H", "statut": "salarie_prive_non_cadre", "stock": "prix", "table": "unisexe",
}
#: La saisie ne commence pas une carrière après quarante ans : vingt-cinq ans
#: au tiers du salaire moyen, sous l'AVTS.
CAS = [
    {},
    {"statut": "salarie_agricole"},
    {"naissance": "1918", "liquidation": "60", "debut": "20"},
    {"naissance": "1917", "sexe": "F", "enfants": "3"},
    # L'artisan et le commerçant, avec des périodes d'avant 1973.
    {"statut": "artisan"},
    {"statut": "commercant", "naissance": "1916"},
    # De part et d'autre du 1er avril 1983.
    {"naissance": "1918", "naissance_mois": "2"},
    {"naissance": "1918", "naissance_mois": "3"},
]


def test_les_deux_moteurs_servent_la_meme_pension_minimum():
    """Chaque étape de la liquidation écrit la même donnée en Python et en
    JavaScript, la pension minimum comprise."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    from test_liquidation import _ecarts, _python

    requetes = [{**REQUETE, **cas} for cas in CAS]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(requetes, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-liquidation.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    obtenus, attendus = json.loads(execution.stdout), _python(requetes)
    assert not any("erreur" in attendu for attendu in attendus), attendus
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
    portees = [rang for rang, attendu in enumerate(attendus)
               if "porté à la pension minimum" in json.dumps(attendu, ensure_ascii=False)]
    assert portees, "aucune requête n'est portée à la pension minimum"


def test_le_maximum_de_r_732_70_lit_l_avts(simulateur):
    """« M = PM-AVTS/37,5 x VP », où « AVTS représente le montant de
    l'allocation aux vieux travailleurs salariés » (R. 732-70) : au plafond de
    2025, 113,4 points, arrondis à 113, les « 23 à 113 points » que la MSA
    annonce ; la retraite forfaitaire, figée depuis 2014, en donnait 115."""
    from retraite_notionnelle.droit.acquerir import points_msa

    actuel = simulateur.scenario_actuel
    assert actuel.minimum_contributif.avts(2025)[0] == pytest.approx(4_023.51)
    assert actuel.minimum_contributif.avts(2015)[0] == pytest.approx(3_379.95)
    periode = actuel.catalogue["msa_non_salaries"].periode(2025)
    plafond = actuel.macro.plafond_securite_sociale(2025)
    assert points_msa(actuel, periode, 2025, plafond) == 113
