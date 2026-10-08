"""Le maximum des pensions du régime général (action 138, étape 17).

La pension du régime général ne passe pas une part du plafond de la Sécurité
sociale de l'année de sa date d'effet : 40 % jusqu'en 1971, 44, 46 puis 48 % de
1972 à 1974, 50 % depuis 1975 (arrêté du 9 octobre 1986, article 2 ; fiche
``pension_maximale_regime_general``). Le maximum suit le taux au-delà du taux
plein : l'ajournement d'avant 1983, le taux acquis au 31 mars 1983, et la
surcote, qui s'applique à la pension ramenée au maximum (circulaire Cnav
n° 2007-5).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.droit import liquider
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
FRANC = 6.55957

#: Le barème « Montant maximum de la retraite personnelle » de la Cnav, aux
#: dates où le plafond n'a pas changé en cours d'année : (date, montant, unité).
BAREME = [
    ("1958-01-01", 240_000, "AF"), ("1959-01-01", 264_000, "AF"),
    ("1962-01-01", 3_840, "F"), ("1963-01-01", 4_176, "F"), ("1964-01-01", 4_560, "F"),
    ("1966-01-01", 5_184, "F"), ("1967-01-01", 5_472, "F"), ("1968-01-01", 5_760, "F"),
    ("1969-01-01", 6_528, "F"), ("1970-01-01", 7_200, "F"), ("1971-01-01", 7_920, "F"),
    ("1972-01-01", 9_662.40, "F"), ("1973-01-01", 11_260.80, "F"),
    ("1974-01-01", 13_363.20, "F"), ("1975-01-01", 16_500, "F"),
    ("1976-01-01", 18_960, "F"), ("1977-01-01", 21_660, "F"), ("1978-01-01", 24_000, "F"),
    ("1979-01-01", 26_820, "F"), ("1980-01-01", 30_060, "F"), ("1981-01-01", 34_380, "F"),
    ("1997-01-01", 82_320, "F"), ("2001-01-01", 89_700, "F"), ("2002-01-01", 14_112, "€"),
    ("2010-01-01", 17_310, "€"), ("2020-01-01", 20_568, "€"), ("2022-01-01", 20_568, "€"),
    ("2023-01-01", 21_996, "€"), ("2025-01-01", 23_550, "€"), ("2026-01-01", 24_030, "€"),
]


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _euros(montant: float, unite: str) -> float:
    return montant if unite == "€" else montant / FRANC / (100 if unite == "AF" else 1)


def _maximum(simulateur, date: str) -> float | None:
    """La part du plafond que la version de ``date`` fixe, au plafond de l'année."""
    regle = simulateur.scenario_actuel.fiches_datees.regle(
        liquider.FICHE_DE_LA_PENSION_MAXIMALE, date)
    if not regle["existe"]:
        return None
    pourcentage = [p for debut, p in regle["pourcentages"] if str(debut) <= date][-1]
    return pourcentage * simulateur.macro.plafond_securite_sociale(int(date[:4]))


def _regime_general(simulateur, naissance: int, age: float, niveau: float = 5.0):
    carriere = simulateur.carriere_simple(
        annee_naissance=naissance, sexe="H", affiliation="salarie_prive_cadre",
        age_debut=20, age_liquidation=age, niveau_salaire=niveau)
    resultat = simulateur.scenario_actuel.calculer(carriere)
    pension, = [p for p in resultat.pensions_par_regime if p.regime == "regime_general"]
    return carriere, pension


# -- la fiche -------------------------------------------------------------------

@pytest.mark.parametrize("date, montant, unite", BAREME)
def test_le_maximum_est_celui_du_bareme_de_la_cnav(simulateur, date, montant, unite):
    """40 %, 44, 46 et 48 %, puis 50 % du plafond de l'année : le barème de la
    caisse, au franc près, le plafond du dépôt étant arrondi à l'euro."""
    assert _maximum(simulateur, date) == pytest.approx(_euros(montant, unite), rel=1e-3)


def test_le_bareme_de_1965_reprend_le_plafond_de_1966(simulateur):
    """Le barème porte 5 184 F au 1er janvier 1965 comme en 1966 : 40 % du plafond
    de 1966, quand celui de 1965, certifié au Journal officiel, en donne 4 896.
    Le modèle compte sur le plafond de l'année (lecture divergente de la fiche)."""
    assert _maximum(simulateur, "1965-01-01") == pytest.approx(4_896 / FRANC, rel=1e-3)
    assert _maximum(simulateur, "1966-01-01") == pytest.approx(5_184 / FRANC, rel=1e-3)


def test_aucun_maximum_avant_1949_ni_hors_du_regime_general(simulateur):
    assert _maximum(simulateur, "1948-12-01") is None
    carriere = simulateur.carriere_simple(
        annee_naissance=1925, sexe="H", affiliation="salarie_prive_cadre",
        age_debut=20, age_liquidation=65, niveau_salaire=5.0)
    assert liquider.pension_maximale(simulateur.scenario_actuel, "msa_salaries", carriere) is None
    assert liquider.pension_maximale(simulateur.scenario_actuel, "regime_general", carriere)


# -- la pension -----------------------------------------------------------------

def test_le_maximum_ramene_la_pension_de_1990(simulateur):
    """Un cadre au plafond toute sa carrière, liquidé à soixante-cinq ans en 1990 :
    ses salaires portés au compte, revalorisés, font un salaire annuel moyen au-dessus
    du plafond de l'année, et sa pension de 50 % est ramenée à la moitié du plafond."""
    carriere, pension = _regime_general(simulateur, 1925, 65)
    plafond = simulateur.macro.plafond_securite_sociale(1990)
    assert carriere.annee_liquidation == 1990
    assert pension.montant == pytest.approx(0.5 * plafond)
    assert "ramenée au maximum des pensions" in pension.detail


def test_le_maximum_suit_l_ajournement_d_avant_1983(simulateur):
    """Liquidée à soixante-dix ans en 1982, la pension a le taux de 75 % — 50 %
    majorés de 1,25 point par trimestre d'ajournement — et le maximum aussi : «
    le pourcentage susvisé est majoré de 1,25% par trimestre d'ajournement »."""
    carriere, pension = _regime_general(simulateur, 1912, 70)
    plafond = simulateur.macro.plafond_securite_sociale(carriere.annee_liquidation)
    assert "taux 75.000%" in pension.detail
    assert pension.montant == pytest.approx(0.75 * plafond)


def test_le_maximum_suit_le_taux_acquis_au_31_mars_1983(simulateur):
    """Né en mars 1917, parti en septembre 1983 : le taux acquis de 55 %, et le
    maximum de 55 % du plafond, comme les 48 906 F de la circulaire n° 22/83."""
    carriere, pension = _regime_general(simulateur, 1917, 66.5)
    plafond = simulateur.macro.plafond_securite_sociale(1983)
    assert "taux 55.000%" in pension.detail
    assert pension.montant == pytest.approx(0.55 * plafond)


def test_la_pension_sous_le_maximum_ne_bouge_pas(simulateur):
    """Au salaire moyen, la pension reste celle que le taux et la durée donnent."""
    _, pension = _regime_general(simulateur, 1925, 65, niveau=1.0)
    assert "maximum des pensions" not in pension.detail


# -- la circulaire n° 22/83 ------------------------------------------------------

#: Le maximum de 1983, 50 % du plafond de 88 920 F, dans l'unité de la
#: comparaison : en « taux × trimestres » d'un salaire annuel moyen.
def _en_trimestres(salaire_annuel_moyen: float) -> float:
    return 44_460 * 150 / salaire_annuel_moyen


@pytest.mark.parametrize("sam, trimestres, majores, ancienne", [
    # 1er cas : 21 528,98 F au taux acquis, 22 181,37 F sur la durée corrigée.
    (97_859, 60, 68, False),
    # 2e cas : 52 028,36 F ramenés à 48 906, 48 929,50 F ramenés à 44 460.
    (97_859, 145, 150, True),
    # 3e cas : 65 208 F ramenés à 48 906, 66 880 F ramenés à 44 460.
    (152_000, 117, 132, True),
])
def test_les_trois_cas_de_la_circulaire_22_83(sam, trimestres, majores, ancienne):
    """« Dispositions antérieures au 1.4.83 Montant maximum de la pension : 48 906
    Dispositions applicables à partir du 1-4-83 Montant maximum de la pension :
    44 460 » : la Cnav compare les deux pensions ramenées à leur maximum."""
    assert liquider.taux_acquis_l_emporte(
        0.55, trimestres, 0.5, majores, _en_trimestres(sam), 0.5, 1.0) is ancienne
    assert 44_460 * 0.55 / 0.5 == pytest.approx(48_906)


def test_sans_maximum_le_troisieme_cas_irait_a_la_regle_nouvelle():
    """Sans le maximum, 55 % × 117 passe sous 50 % × 132 : c'est le maximum qui
    décide le troisième cas de la circulaire."""
    assert not liquider.taux_acquis_l_emporte(0.55, 117, 0.5, 132, None, 0.5, 1.0)


# -- les deux moteurs -----------------------------------------------------------

REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "20", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "interruptions": "", "liquidation": "65", "naissance": "1925", "primes": "0",
    "profil": "plat", "projection": "cor_reference", "salaire": "5", "sexe": "H",
    "statut": "salarie_prive_cadre", "stock": "prix", "table": "unisexe",
}
#: Le maximum de 1990, celui de l'ajournement de 1982, du taux acquis de 1983 ;
#: une pension surcotée de 2015, sous le maximum ; une pension au salaire moyen.
CAS = [
    {},
    {"naissance": "1912", "liquidation": "70"},
    {"naissance": "1917", "naissance_mois": "3", "liquidation": "66.5"},
    {"naissance": "1950", "liquidation": "65"},
    {"salaire": "1"},
]


def test_les_deux_moteurs_ramenent_au_meme_maximum():
    """Le journal de l'échéancier — les composantes et leur formule — est le même
    en Python et en JavaScript."""
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
    assert "ramenée au maximum des pensions" in json.dumps(attendus, ensure_ascii=False)
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
