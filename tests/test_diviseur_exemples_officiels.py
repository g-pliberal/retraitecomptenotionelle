"""Le diviseur éprouvé sur les exemples officiels de quatre comptes étrangers.

Action 138, étape 11 (registre, chantier 138.11). Chaque pays publie, avec ses
diviseurs, la table de mortalité qui les fait : on la lit à sa source, on la
donne au diviseur du dépôt (``diviseur_de_courbe``, et son jumeau
``diviseurDeCourbe``), et l'on confronte le résultat au chiffre publié. Un
écart se comprend avant de se corriger ; ici, il n'en reste aucun qui ne
s'explique.

* **Finlande** (mémo de l'ETK du 26 octobre 2023, ``eak2024.pdf``, annexe 1,
  lu le 14 octobre 2026) : EAL2009 = 16,778288 et EAL2024 = 17,718722, au taux
  de 2 %, de 62 à 100 ans. La formule de l'ETK est celle du dépôt : survie
  moyenne de l'année, actualisée en son milieu. Exact au millionième.
* **Pologne** (communiqué du président du GUS du 25 mars 2026, sa table en
  mois ; table D, « Tablica trwania życia dla obu płci łącznie w 2025 r. »,
  publiée le 27 juillet 2026, lus le 14 octobre 2026) : 222,7 mois à 65 ans.
  Sans actualisation, le diviseur du dépôt est l'espérance de vie du GUS, à
  l'intervalle ouvert de 100 ans près, que la table close par ``T100/l100``.
  Le communiqué arrondit l'espérance au centième d'année AVANT de la
  multiplier par douze : sans cet arrondi, 222,76 mois donneraient 222,8.
* **Suède** (PFS 2026:2, décidée le 2 septembre 2026, génération 1960 ; SCB,
  ``LivslangdFemarigA``, « totalt », risques de 2020-2024, lus le 14 octobre
  2026) : 19,13 à 62 ans, 17,34 à 65 ans. Le diviseur suédois est la valeur de
  douze mensualités versées d'avance (SFB 62:36), la survie linéaire dans
  l'année, au taux de 1,6 % ; celui du dépôt, une rente continue. Il est donc
  plus court d'un vingt-quatrième d'année, à 0,1 % près : 17,298 contre 17,34.
  La formule suédoise, écrite ici, refait la grille au centième de 62 à 103
  ans ; au-delà, elle lit la mortalité d'après 110 ans, que SCB ne publie pas,
  et la PFS borne le diviseur à 1,00.
* **Italie** (Nota tecnica du décret du 20 novembre 2024, tableaux A et C.2,
  lue le 14 octobre 2026) : le diviseur à 65 ans, 19,049, est la moyenne des
  deux sexes de deux termes, la pension directe, 17,590, et la réversion,
  1,460. Le second, la réversion tarifée dans le diviseur, est un choix du
  programme que le propriétaire tranche (registre, ``a_trancher``) : seul le
  premier s'éprouve ici. L'Italie le compte en annuité annuelle d'avance au
  taux de 1,5 %, moins ``k = 0,4615`` pour treize mensualités d'avance ; la
  rente continue du dépôt vaut l'annuité moins un demi : elle est plus courte
  de 0,5 − 0,4615 = 0,0385 an, à 0,004 près. La formule italienne, écrite ici,
  refait les deux sexes et leur moyenne au millième, de 57 à 71 ans (six
  dix-millièmes au plus, les quotients étant publiés à sept décimales).

Ce que ces écarts disent au dépôt : le terme des versements. La pension
française se paie par mois à terme échu (R. 355-2 du code de la sécurité
sociale) ; le diviseur exact serait l'annuité moins 13/24 d'année, et non la
rente continue. Le registre le garde ``a_trancher`` : le README définit le
diviseur comme l'espérance de vie restante, que le dépôt calcule exactement.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from retraite_notionnelle.moteur.conversion import diviseur_de_courbe

RACINE = Path(__file__).resolve().parents[1]


def _lire(texte: str) -> list[float]:
    return [float(x) for x in texte.split()]


# ---------------------------------------------------------------------------
# Les tables, lues à leur source
# ---------------------------------------------------------------------------

#: SCB, risques de décès en pour mille, deux sexes, 2020-2024, de 62 à 110 ans.
SUEDE_RISQUES_2020_2024 = _lire("""
    5.59 6.38 7.19 7.90 8.82 9.80 10.76 12.06 13.10 14.62 16.20 17.96 20.03
    22.29 24.63 27.97 31.67 35.45 39.56 45.16 51.27 58.49 66.68 75.89 84.83
    97.93 112.09 126.15 143.52 161.60 179.67 202.32 222.65 240.67 263.58
    287.99 313.89 341.24 370.01 400.13 431.52 464.08 497.68 532.18 567.40
    603.14 639.14 675.13 710.80
""")

#: ETK, mémo eak2024.pdf, annexe 1 : risques en pour mille de 62 à 100 ans,
#: q100 = 1 000, pour 2009 (mortalité 2003-2007) et 2024 (2018-2022).
FINLANDE_RISQUES_2003_2007 = _lire("""
    9.59 10.29 11.05 12.31 13.02 13.69 15.26 16.54 18.40 20.32 21.98 25.28
    26.72 30.65 33.10 38.32 43.19 47.67 53.66 60.03 66.50 76.00 83.82 94.07
    106.44 117.49 130.85 149.96 162.49 188.32 202.56 225.06 238.53 257.39
    283.97 309.15 332.80 349.08 1000.00
""")

FINLANDE_RISQUES_2018_2022 = _lire("""
    7.62 7.95 9.25 9.95 10.76 11.36 13.09 13.90 15.30 16.54 18.51 20.20
    22.37 24.63 27.23 29.49 33.20 37.00 42.65 47.92 55.66 60.86 68.82 79.23
    89.89 102.84 113.40 127.12 146.89 167.55 186.73 206.36 229.71 251.56
    281.64 302.21 335.08 332.56 1000.00
""")

#: Nota tecnica, tableau A : probabilités de mort de 2023, de 57 à 119 ans.
ITALIE_HOMMES_2023 = _lire("""
    0.0047679 0.0051418 0.0055808 0.0061001 0.0067188 0.0074133 0.0082921
    0.0091737 0.0101843 0.0112657 0.0123808 0.0135255 0.0149923 0.0168331
    0.0188242 0.0210861 0.0229580 0.0255079 0.0271700 0.0298034 0.0334159
    0.0380877 0.0427315 0.0500621 0.0561440 0.0627106 0.0699165 0.0765799
    0.0860164 0.0981704 0.1128744 0.1278743 0.1452182 0.1650864 0.1861044
    0.2057569 0.2290189 0.2499055 0.2693988 0.2976836 0.3216615 0.3453783
    0.3696101 0.3998852 0.4357998 0.4696011 0.5039111 0.5384345 0.5728597
    0.6068779 0.6401860 0.6725058 0.7035823 0.7331983 0.7611755 0.7873800
    0.8117172 0.8341352 0.8546181 0.8731848 0.8898802 0.9047735 0.9179502
""")

ITALIE_FEMMES_2023 = _lire("""
    0.0026936 0.0028841 0.0032159 0.0035542 0.0038934 0.0043023 0.0046764
    0.0050852 0.0056979 0.0063450 0.0069262 0.0075227 0.0082550 0.0091926
    0.0103040 0.0117036 0.0131335 0.0147842 0.0165309 0.0188035 0.0213463
    0.0244716 0.0275714 0.0322113 0.0367799 0.0421512 0.0477931 0.0535917
    0.0618865 0.0724171 0.0842423 0.0976538 0.1124177 0.1298549 0.1466190
    0.1643034 0.1844927 0.2057978 0.2307524 0.2559014 0.2774486 0.2987334
    0.3235643 0.3545996 0.3943162 0.4263282 0.4590162 0.4921130 0.5253374
    0.5584056 0.5910349 0.6229601 0.6539399 0.6837584 0.7122365 0.7392341
    0.7646464 0.7884067 0.8104837 0.8308774 0.8496115 0.8667368 0.8823163
""")

#: GUS, table D de 2025, deux sexes : q_x de 60 à 99 ans ; à 100 ans,
#: l100 = 1 802 et T100 = 4 300, l'intervalle ouvert.
POLOGNE_2025 = _lire("""
    0.00923 0.01014 0.01114 0.01231 0.01355 0.01486 0.01624 0.01764 0.01907
    0.02058 0.02218 0.02393 0.02586 0.02799 0.03036 0.03304 0.03598 0.03929
    0.04301 0.04722 0.05206 0.05757 0.06386 0.0712 0.07955 0.08896 0.0993
    0.11068 0.12259 0.13529 0.14856 0.16265 0.17732 0.19296 0.2093 0.22628
    0.24373 0.2616 0.27994 0.29801
""")

POLOGNE_ESPERANCE_A_100 = 4300 / 1802

#: PFS 2026:2, § 1, génération 1960, de 62 à 103 ans.
PFS_2026_2 = dict(zip(range(62, 104), _lire("""
    19.13 18.53 17.93 17.34 16.75 16.15 15.56 14.96 14.37 13.78 13.19 12.61
    12.02 11.45 10.87 10.30 9.75 9.20 8.66 8.13 7.62 7.12 6.64 6.18 5.74 5.31
    4.92 4.55 4.20 3.88 3.59 3.32 3.08 2.86 2.65 2.45 2.26 2.09 1.93 1.79 1.65
    1.53
""")))

#: Nota tecnica, tableau C.2 : le terme de la pension directe (« dante
#: causa »), hommes, femmes, total, de 57 à 71 ans.
ITALIE_C2_DIRECTE = {57: (21.266, 23.534, 22.400), 58: (20.678, 22.942, 21.810),
                     59: (20.086, 22.344, 21.215), 60: (19.490, 21.743, 20.616),
                     61: (18.892, 21.137, 20.015), 62: (18.294, 20.528, 19.411),
                     63: (17.695, 19.916, 18.805), 64: (17.098, 19.299, 18.198),
                     65: (16.502, 18.677, 17.590), 66: (15.908, 18.055, 16.981),
                     67: (15.316, 17.431, 16.374), 68: (14.726, 16.804, 15.765),
                     69: (14.136, 16.173, 15.155), 70: (13.550, 15.540, 14.545),
                     71: (12.971, 14.906, 13.939)}
ITALIE_K = 0.4615

#: Le communiqué du GUS, en mois, à l'âge rond.
GUS_2026 = {60: 268.9, 62: 250.0, 65: 222.7, 67: 205.4, 70: 180.6, 80: 106.4, 90: 54.2}


def _courbe(risques: list[float], premier_age: int, age: int, echelle: float = 1.0) -> list[float]:
    """Les survies depuis ``age``, ``l_(x+1) = l_x (1 − q_x)``, jusqu'au bout de
    la table."""
    courbe = [1.0]
    for q in risques[age - premier_age:]:
        courbe.append(courbe[-1] * (1.0 - q / echelle))
    return courbe


def _finlande(risques: list[float]) -> list[float]:
    return _courbe(risques, 62, 62, 1000.0)


def _suede(age: int) -> list[float]:
    return _courbe(SUEDE_RISQUES_2020_2024, 62, age, 1000.0)


def _italie(risques: list[float], age: int) -> list[float]:
    return _courbe(risques, 57, age)


def _pologne(age: int) -> list[float]:
    return _courbe(POLOGNE_2025, 60, age)


def _cas() -> dict[str, tuple[list[float], float]]:
    """Chaque courbe et son taux, sous un nom, pour les deux moteurs."""
    cas = {"fi_2009": (_finlande(FINLANDE_RISQUES_2003_2007), 0.02),
           "fi_2024": (_finlande(FINLANDE_RISQUES_2018_2022), 0.02)}
    cas.update({f"se_{age}": (_suede(age), 0.016) for age in PFS_2026_2})
    for age in ITALIE_C2_DIRECTE:
        cas[f"it_h_{age}"] = (_italie(ITALIE_HOMMES_2023, age), 0.015)
        cas[f"it_f_{age}"] = (_italie(ITALIE_FEMMES_2023, age), 0.015)
    cas.update({f"pl_{age}": (_pologne(age), 0.0) for age in GUS_2026})
    return cas


def _python() -> dict[str, float]:
    return {nom: diviseur_de_courbe(courbe, taux) for nom, (courbe, taux) in _cas().items()}


@pytest.fixture(scope="module")
def deux_moteurs() -> dict[str, dict[str, float]]:
    """Le diviseur de chaque cas, par le Python et par le portage."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    entree = json.dumps({nom: [courbe, taux] for nom, (courbe, taux) in _cas().items()})
    script = ('import { diviseurDeCourbe } from "./moteur/js/conversion.js";'
              f"const cas = {entree};"
              "const sortie = {};"
              "for (const [nom, [courbe, taux]] of Object.entries(cas))"
              " sortie[nom] = diviseurDeCourbe(courbe, taux);"
              "console.log(JSON.stringify(sortie));")
    sortie = subprocess.run(["node", "--input-type=module", "-e", script], cwd=RACINE,
                            capture_output=True, text=True, encoding="utf-8", check=True)
    return {"python": _python(), "javascript": json.loads(sortie.stdout)}


def test_les_deux_moteurs_rendent_le_meme_diviseur(deux_moteurs):
    python, javascript = deux_moteurs["python"], deux_moteurs["javascript"]
    assert python.keys() == javascript.keys()
    for nom, valeur in python.items():
        assert javascript[nom] == pytest.approx(valeur, rel=1e-13), nom


# ---------------------------------------------------------------------------
# Finlande : la formule même du dépôt
# ---------------------------------------------------------------------------

def test_la_finlande_au_millionieme(deux_moteurs):
    """EAL2009 et EAL2024, au millionième, et le coefficient qui s'en tire."""
    for moteur in deux_moteurs.values():
        assert round(moteur["fi_2009"], 6) == 16.778288
        assert round(moteur["fi_2024"], 6) == 17.718722
        assert round(round(moteur["fi_2009"], 6) / round(moteur["fi_2024"], 6), 5) == 0.94692


# ---------------------------------------------------------------------------
# Pologne : l'espérance de vie, arrondie au centième d'année
# ---------------------------------------------------------------------------

def _mois_gus(diviseur: float, courbe: list[float]) -> float:
    """Le diviseur, clos par l'intervalle ouvert de 100 ans, en mois, comme le
    communiqué l'écrit : l'espérance arrondie au centième d'année, puis par
    douze, au dixième."""
    esperance = diviseur + courbe[-1] * POLOGNE_ESPERANCE_A_100
    return round(round(esperance, 2) * 12, 1)


def test_la_pologne_au_dixieme_de_mois(deux_moteurs):
    for moteur in deux_moteurs.values():
        for age, publie in GUS_2026.items():
            assert _mois_gus(moteur[f"pl_{age}"], _pologne(age)) == publie, age
    # L'arrondi au centième d'année fait le dixième de mois : sans lui, 222,8.
    brut = deux_moteurs["python"]["pl_65"] + _pologne(65)[-1] * POLOGNE_ESPERANCE_A_100
    assert round(brut * 12, 1) == 222.8


# ---------------------------------------------------------------------------
# Suède : douze mensualités d'avance
# ---------------------------------------------------------------------------

def _delningstal(courbe: list[float], taux: float = 0.016) -> float:
    """SFB 62:36, rapport orange, annexe A.8 : douze mensualités versées
    d'avance, la survie linéaire dans l'année."""
    total = 0.0
    for annee in range(len(courbe) - 1):
        for mois in range(12):
            survie = courbe[annee] + (courbe[annee + 1] - courbe[annee]) * mois / 12
            total += survie * (1.0 + taux) ** -(annee + mois / 12) / 12
    return total


def test_la_suede_au_centieme_par_sa_convention():
    for age, publie in PFS_2026_2.items():
        assert round(_delningstal(_suede(age)), 2) == publie, age


def test_le_diviseur_du_depot_est_plus_court_d_un_vingt_quatrieme_d_annee(deux_moteurs):
    """Rente continue contre mensualités d'avance : 1/24 d'année, que
    l'actualisation écorne d'un millième au plus."""
    for moteur in deux_moteurs.values():
        assert round(moteur["se_65"], 2) == 17.30
        for age, publie in PFS_2026_2.items():
            ecart = _delningstal(_suede(age)) - moteur[f"se_{age}"]
            assert ecart == pytest.approx(1 / 24, abs=0.002), age
            assert publie - moteur[f"se_{age}"] == pytest.approx(1 / 24, abs=0.007), age


# ---------------------------------------------------------------------------
# Italie : l'annuité d'avance moins k, le terme de la pension directe
# ---------------------------------------------------------------------------

def _annuite_italienne(courbe: list[float], taux: float = 0.015) -> float:
    """Nota tecnica, allegato tecnico : la somme des survies actualisées, de
    t = 0 à w − x, moins k."""
    return sum(survie * (1.0 + taux) ** -t for t, survie in enumerate(courbe)) - ITALIE_K


def test_l_italie_au_millieme_par_sa_convention():
    for age, (hommes, femmes, total) in ITALIE_C2_DIRECTE.items():
        h = _annuite_italienne(_italie(ITALIE_HOMMES_2023, age))
        f = _annuite_italienne(_italie(ITALIE_FEMMES_2023, age))
        # Les quotients publiés à sept décimales laissent un demi-millième.
        assert h == pytest.approx(hommes, abs=0.0006), age
        assert f == pytest.approx(femmes, abs=0.0006), age
        assert (h + f) / 2 == pytest.approx(total, abs=0.0006), age


def test_le_diviseur_du_depot_rend_la_pension_directe_moins_0_0385(deux_moteurs):
    """La rente continue vaut l'annuité d'avance moins un demi, à l'ordre près
    de l'actualisation ; l'Italie retire 0,4615."""
    for moteur in deux_moteurs.values():
        for age, (hommes, femmes, total) in ITALIE_C2_DIRECTE.items():
            depot = (moteur[f"it_h_{age}"] + moteur[f"it_f_{age}"]) / 2
            assert total - depot == pytest.approx(0.5 - ITALIE_K, abs=0.004), age
        assert round((moteur["it_h_65"] + moteur["it_f_65"]) / 2, 3) == 17.548
