"""Le salaire annuel moyen du régime général, et ce qui le nourrit, datés.

Action 138, étape 16 : les règles que le relevé des modèles publics a montrées
fausses au scénario 1, relues au texte et chez la caisse — R. 351-29 et ses
rédactions, le décret n° 72-1229, les circulaires Cnav 1/73, 95/94 et 2004/27,
R. 634-1-1 pour les artisans et les commerçants, R. 381-3 et le barème de la
Cnav pour l'assurance vieillesse des parents au foyer, les colonnes de
revalorisation de la caisse depuis 1946. Le jumeau JavaScript de chaque test est
dans ``tests/js/moteur.test.js``.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.droit import liquider
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


#: Quatre années à la main : une pleine, une moitié travaillée et moitié
#: assimilée, une pleine, une dont le salaire ne valide aucun trimestre.
VALEURS = [(1960, 1000.0), (1961, 4000.0), (1962, 3000.0), (1963, 500.0)]
TRIMESTRES = {1960: [4, 0], 1961: [2, 2], 1962: [4, 0], 1963: [0, 0]}
VALIDANTES = {1960, 1961, 1962}


def _regle(**parametres) -> dict:
    regle = {"selection": "meilleures", "avant_la_liquidation": False,
             "calcul": "annuel", "trimestres_comptes": "cotises_et_assimiles",
             "annees_assimilees_exclues": False, "annees_sans_trimestre": "retenues"}
    regle.update(parametres)
    return regle


def test_la_moyenne_suit_la_version_de_la_date_d_effet():
    """Chaque version de la fiche `salaire_annuel_moyen`, sur les mêmes quatre
    années.

    Depuis 2004, l'année qui ne valide aucun trimestre sort (R. 351-29,
    circulaire 2004/27) ; de juillet 1995 à 2003, elle compte, en moyenne
    annuelle (circulaire 95/94) ; de 1973 à juin 1995, la somme des salaires
    est rapportée aux trimestres, assimilés compris, puis multipliée par quatre
    (circulaire 1/73) ; avant 1973, les dix DERNIÈRES années, sans celles de
    deux trimestres assimilés, rapportées à leurs trimestres cotisés — avant
    soixante ans, ou avant l'effet depuis juillet 1948 si c'est mieux.
    """
    moyenne = liquider.moyenne_selon_la_regle
    depuis_2004 = _regle(annees_sans_trimestre="exclues")
    assert moyenne(depuis_2004, VALEURS, TRIMESTRES, VALIDANTES, 10, 9999) \
        == pytest.approx(8000.0 / 3)
    assert moyenne(_regle(), VALEURS, TRIMESTRES, VALIDANTES, 10, 9999) \
        == pytest.approx(8500.0 / 4)
    # Les meilleures d'abord : sur deux années, 1961 et 1962.
    assert moyenne(_regle(), VALEURS, TRIMESTRES, VALIDANTES, 2, 9999) == 3500.0
    trimestriel = _regle(calcul="trimestriel")
    assert moyenne(trimestriel, VALEURS, TRIMESTRES, VALIDANTES, 10, 9999) \
        == pytest.approx(8500.0 * 4 / 12)
    avant_1948 = _regle(selection="dernieres", calcul="trimestriel",
                        trimestres_comptes="cotises", annees_assimilees_exclues=True)
    # Les deux dernières années d'avant 1963, l'année des soixante ans, sans
    # 1961 et ses deux trimestres assimilés : 1960 et 1962.
    assert moyenne(avant_1948, VALEURS, TRIMESTRES, VALIDANTES, 2, 1963) \
        == pytest.approx(4000.0 * 4 / 8)
    # Depuis juillet 1948, les deux dernières d'avant l'effet, 1962 et 1963,
    # valent mieux : 3 500 € sur quatre trimestres.
    depuis_1948 = dict(avant_1948, avant_la_liquidation=True)
    assert moyenne(depuis_1948, VALEURS, TRIMESTRES, VALIDANTES, 2, 1963) \
        == pytest.approx(3500.0 * 4 / 4)


def _carriere(annee_naissance: int, age_liquidation: float, lignes) -> Carriere:
    return Carriere.depuis_lignes(
        annee_naissance, "H",
        [AnneeCarriere(annee=annee, revenu=revenu, affiliation="salarie_prive_non_cadre",
                       trimestres_valides=trimestres)
         for annee, revenu, trimestres in lignes],
        age_liquidation=age_liquidation)


def test_une_annee_sans_trimestre_ne_compte_plus_depuis_2004(simulateur):
    """Un salarié né en 1950, vingt années à 30 000 €, puis une année à
    100 €, qui ne valide aucun trimestre : liquidé en 2012, son salaire moyen
    est celui des vingt bonnes années ; liquidé en 2003, la petite année tirait
    sa moyenne vers le bas. C'est ce que trois modèles publics faisaient et que
    le dépôt ne faisait pas (OpenFisca-France-Pension, calcul_pension, CALIPER)."""
    actuel = simulateur.scenario_actuel
    macro = simulateur.macro
    lignes = [(annee, 30_000.0, 4) for annee in range(1985, 2001)]
    lignes.append((2001, 100.0, 0))
    code = "regime_general"

    tardive = _carriere(1950, 62, lignes)
    periode = simulateur.catalogue[code].periode(2012)
    revalorise = [min(30_000.0, macro.plafond_securite_sociale(annee))
                  * macro.coefficient_revalorisation_portee_au_compte(
                      annee, 2012, tardive.mois_liquidation)
                  for annee in range(1985, 2001)]
    sam = liquider.salaire_de_reference(actuel, code, tardive, periode, 2012, True, 1950)
    assert sam == pytest.approx(sum(sorted(revalorise, reverse=True)) / len(revalorise))

    precoce = _carriere(1950, 53, lignes)
    periode = simulateur.catalogue[code].periode(2003)
    revalorise = [min(revenu, macro.plafond_securite_sociale(annee))
                  * macro.coefficient_revalorisation_portee_au_compte(
                      annee, 2003, precoce.mois_liquidation)
                  for annee, revenu, _ in lignes]
    sam = liquider.salaire_de_reference(actuel, code, precoce, periode, 2003, True, 1950)
    assert sam == pytest.approx(sum(sorted(revalorise, reverse=True)) / len(revalorise))


def test_avant_juillet_1995_la_moyenne_se_rapporte_aux_trimestres(simulateur):
    """Une année d'entrée qui ne valide que deux trimestres compte pour deux
    trimestres, non pour une année : avant le 1er juillet 1995, la somme des
    salaires retenus est rapportée à leurs trimestres et multipliée par quatre
    (circulaire Cnav 1/73 ; circulaire 95/94)."""
    actuel = simulateur.scenario_actuel
    macro = simulateur.macro
    lignes = [(1975, 4_000.0, 2)] + [(annee, 20_000.0, 4) for annee in range(1976, 1985)]
    carriere = _carriere(1925, 65, lignes)
    periode = simulateur.catalogue["regime_general"].periode(1990)
    revalorise = [min(revenu, macro.plafond_securite_sociale(annee))
                  * macro.coefficient_revalorisation_portee_au_compte(
                      annee, 1990, carriere.mois_liquidation)
                  for annee, revenu, _ in lignes]
    sam = liquider.salaire_de_reference(actuel, "regime_general", carriere, periode, 1990,
                                        True, 1925)
    assert sam == pytest.approx(sum(sorted(revalorise, reverse=True)) * 4 / 38)


def test_les_artisans_et_commercants_ont_leur_table(simulateur):
    """R. 634-1-1 : vingt années pour un commerçant né en 1948, quinze pour
    1943, vingt-quatre pour 1952, quand les salariés en ont vingt-cinq dès
    1948 ; depuis 2026, la règle commune de R. 173-3-2."""
    actuel = simulateur.scenario_actuel
    periode = simulateur.catalogue["rsi"].periode(2010)
    for naissance, attendu in ((1943, 15), (1948, 20), (1952, 24), (1953, 25)):
        carriere = _carriere(naissance, 2010.5 - naissance, [(2000, 30_000.0, 4)])
        assert liquider.nombre_d_annees_retenues(
            actuel, periode, carriere, naissance) == attendu, naissance
    salarie = simulateur.catalogue["regime_general"].periode(2010)
    carriere = _carriere(1948, 62, [(2000, 30_000.0, 4)])
    assert liquider.nombre_d_annees_retenues(actuel, salarie, carriere, 1948) == 25


def test_l_assiette_de_l_avpf_est_celle_de_la_cnav(simulateur):
    """R. 381-3 : 169 heures par mois du SMIC du 1er juillet précédent, que la
    Cnav publie depuis la naissance de l'AVPF, le 1er juillet 1972 — 1 715,35 €
    par mois en 2021, 2 031,38 € en 2026 (circulaire 2025/33). Au-delà, le texte,
    sur le SMIC du 1er juillet 2026 (12,31 €)."""
    macro = simulateur.macro
    assert macro.revenu_avpf(1971) == 0.0
    assert macro.revenu_avpf(1972) == pytest.approx(6 * 667.32 / 6.55957)
    assert macro.revenu_avpf(2021) == pytest.approx(12 * 1_715.35)
    assert macro.revenu_avpf(2026) == pytest.approx(12 * 2_031.38)
    assert macro.revenu_avpf(2027) == pytest.approx(2_028 * 12.31)


def test_la_colonne_de_revalorisation_est_celle_de_la_date_d_effet(simulateur):
    """Trois coefficients recopiés à la main de la page de la Cnav des
    coefficients d'avant 2013 et du barème d'avril 2013, qu'un défaut du
    récupérateur ne pourrait pas reproduire : le salaire de 1970 d'un départ de
    janvier 1990, celui de 1947 d'un départ de juin 1949, celui de 1990 d'un
    départ de mai 2013."""
    lu = simulateur.macro.coefficient_revalorisation_portee_au_compte
    assert lu(1970, 1990, 1) == pytest.approx(5.629)
    assert lu(1947, 1949, 6) == pytest.approx(1.6)
    assert lu(1990, 2013, 5) == pytest.approx(1.431)


def test_avant_1972_le_trimestre_se_valide_au_trimestre_de_l_avts(simulateur):
    """R. 351-9 (action 138, étape 6) : de 1949 à 1971, autant de trimestres que
    le salaire annuel représente de fois « le montant trimestriel de
    l'allocation aux vieux travailleurs salariés au 1er janvier », celui des
    villes de plus de 5 000 habitants jusqu'en 1962 ; de 1946 à 1948, autant de
    fois 18 F. Le modèle validait quatre trimestres à toute année travaillée
    avant 1972 ; il le fait encore avant 1946, où la règle se lit sur la retenue.
    Les montants viennent du barème de la Cnav : 34 000 anciens francs au
    1er octobre 1948, 72 380 au 1er janvier 1956, 800 F au 1er avril 1962 — qui
    ne compte qu'en 1963 —, 1 750 F au 1er octobre 1970 (décret n° 70-879)."""
    valides = simulateur.macro.trimestres_valides

    def francs(montant: float) -> float:
        return montant / 6.55957

    assert valides(francs(1.0), 1940) == 4
    assert [valides(francs(f), 1946) for f in (17.99, 18.0, 71.99, 72.0)] == [0, 1, 3, 4]
    assert [valides(francs(f), 1949) for f in (84.99, 85.0, 170.0)] == [0, 1, 2]
    assert [valides(francs(f), 1962) for f in (180.95, 723.79, 723.80)] == [1, 3, 4]
    assert [valides(francs(f), 1963) for f in (199.99, 200.0)] == [0, 1]
    assert [valides(francs(f), 1971) for f in (437.49, 437.50, 1_749.0, 1_750.0)] == [
        0, 1, 3, 4]
    # 1972 : 200 heures du SMIC de janvier, 3,94 F, la règle d'avant inchangée.
    assert [valides(francs(f), 1972) for f in (787.0, 788.0)] == [0, 1]
