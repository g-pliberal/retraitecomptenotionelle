"""La baisse des pensions des complémentaires que l'État règle, dès la bascule,
telle que le modèle la calcule, et l'ordre d'intégration qui en suit.

Action 186, chantier 6, étape 1 bis
(``docs/feuille_de_route/186/2026-11-07-complementaires-baisse-avant-integration.md``).
La décision 43 ne laisse ses pensions qu'à l'Agirc-Arrco « jusqu'à ce qu'elle
coule » ; les autres baissent dès la bascule, en cinq ans au plus (décisions 2
et 3), par cinquièmes, et seules les pensions déjà servies (le propriétaire,
le 7 novembre 2026). La baisse se lit au coût agrégé du scénario 6 : celle du
cas type de la caisse quand la grille en a un, celle de l'ensemble sinon. Ce
fichier calcule le coût, d'où son niveau (``tests/conftest.py``) ; la
mécanique, sous une baisse posée à la main, est dans
``test_integration_complementaires.py``.
"""
from __future__ import annotations

import pytest

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle import integration_complementaires as ic

#: Les complémentaires dont l'État fixe les pensions (décision 43).
REGLEES_PAR_L_ETAT = ("msa_exploitants_complementaire", "ircantec", "cnbf_complementaire",
                      "rci_complementaire", "cnavpl_complementaire", "crpnpac")


@pytest.fixture(scope="module")
def baisses():
    return ic.baisses_du_modele()


@pytest.fixture(scope="module")
def projections(baisses):
    return ic.projeter_les_caisses(RACINE_DONNEES, baisses=baisses)


def test_l_agirc_arrco_garde_ses_pensions(baisses):
    """Décision 43 : « On ne bouge que les pensions des régimes que l'on peut
    bouger en tant que politique » ; l'Agirc-Arrco, qui fixe les siennes par
    accord (L. 921-4 du code de la sécurité sociale), les garde."""
    assert "agirc_arrco" not in baisses
    assert set(baisses) == set(REGLEES_PAR_L_ETAT)


def test_la_baisse_de_l_ensemble_est_pres_du_quart(baisses):
    """Note des deux lectures de la décision 29 : les retraités d'aujourd'hui
    perdent 104 Md€ en 2026, « près du quart de la dépense de retraite »,
    réversions servies gardées, la garantie vieillesse rendue. Avant la
    garantie, que le régime général paie, et sur les seuls droits directs,
    un peu plus : entre un cinquième et un tiers. Les avocats et les navigants,
    que la grille du coût ne compte pas, la prennent."""
    for caisse in ("cnbf_complementaire", "crpnpac"):
        assert 0.20 < baisses[caisse].taux < 1 / 3, caisse
    assert baisses["cnbf_complementaire"] == baisses["crpnpac"]


def test_chaque_caisse_suit_son_cas_type(baisses):
    """Les cas types publiés (page Cas types, génération 1960, au départ) : le
    chef d'exploitation agricole perd 51 %, le contractuel du public 34 %,
    l'artisan 25 %, le libéral 10 % ; l'ordre des baisses suit."""
    taux = {caisse: baisses[caisse].taux for caisse in REGLEES_PAR_L_ETAT}
    assert (taux["msa_exploitants_complementaire"] > taux["ircantec"]
            > taux["rci_complementaire"] > taux["cnavpl_complementaire"])


def test_le_stock_s_eteint(baisses):
    """Les pensions servies à la bascule font presque toute la dépense de 2026,
    et plus rien en 2070 : ceux qui les touchent sont morts."""
    for caisse, baisse in baisses.items():
        parts = [baisse.part_du_stock[a] for a in range(2026, ic.FIN + 1)]
        assert parts[0] > 0.8, caisse
        assert parts[-1] < 0.01, caisse
        assert all(a >= b - 1e-9 for a, b in zip(parts, parts[1:])), caisse


def test_les_deux_premieres_ne_bougent_pas(projections):
    """La complémentaire agricole tombe dès 2026 : sa baisse, par cinquièmes,
    ne lui rend en 2026 qu'un cinquième de quelque 45 % de 1,085 Md€, moins
    de 0,1 Md€, quand il lui en manque 0,124. L'Agirc-Arrco ne baisse rien
    (décision 43) : 2032, comme sans la baisse."""
    assert projections["msa_exploitants_complementaire"].annee_integration == 2026
    assert projections["agirc_arrco"].annee_integration == 2032


def test_la_baisse_recule_les_avocats_et_l_ircantec(projections):
    """Une baisse des dépenses ne peut que reculer l'épuisement des réserves :
    la CNBF passe après 2042, l'Ircantec après 2055, leurs années sans la
    baisse."""
    cnbf = projections["cnbf_complementaire"].annee_integration
    ircantec = projections["ircantec"].annee_integration
    assert cnbf is None or cnbf > 2042
    assert ircantec is None or ircantec > 2055


def test_l_ordre_d_integration_sous_la_baisse(projections):
    """La complémentaire agricole, l'Agirc-Arrco, puis la CNBF : les seules
    que la baisse ne repousse pas au-delà de 2070 (note de l'étape 1 bis)."""
    ordre = ic.ordre_d_integration(projections)
    assert [caisse for caisse, _ in ordre[:3]] == [
        "msa_exploitants_complementaire", "agirc_arrco", "cnbf_complementaire"]
    annees = [annee for _, annee in ordre if annee is not None]
    assert annees == sorted(annees)


def test_la_projection_par_defaut_porte_la_baisse(projections):
    """Sans ``baisses``, la projection prend celle du modèle : ce sont les
    décisions."""
    defaut = ic.projeter_les_caisses(RACINE_DONNEES)
    for caisse, projection in projections.items():
        assert defaut[caisse].annee_integration == projection.annee_integration, caisse
