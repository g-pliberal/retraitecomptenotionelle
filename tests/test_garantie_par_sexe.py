"""Le déplacement par sexe : sa contrainte, et le raccord qui le rend lisible.

Ce script ne touche à aucun moteur : il redéplace la distribution de l'EIR,
sexe par sexe, sous une contrainte de masse. Le seul test qui compte vraiment
est donc le premier — si la colonne ``r = 1`` ne redonne pas le coût que la
page affiche, toute la sensibilité porte à côté, et silencieusement.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from retraite_notionnelle.config import Parametres
from retraite_notionnelle.cout import calculer_cout
from retraite_notionnelle.donnees.assiette import AssietteActivite
from retraite_notionnelle.donnees.depenses import DepensesRetraite
from retraite_notionnelle.donnees.equilibre import ComptesRetraite
from retraite_notionnelle.donnees.population import Population
from retraite_notionnelle.simulateur import Simulateur

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import garantie_par_sexe  # noqa: E402


@pytest.fixture(scope="module")
def lectures():
    return garantie_par_sexe.calculer(Parametres())


@pytest.fixture(scope="module")
def garantie_de_l_enquete():
    parametres = Parametres()
    racine = parametres.racine_donnees
    simulateur = Simulateur(parametres)
    cout = calculer_cout(simulateur, DepensesRetraite(racine), Population(racine),
                         ComptesRetraite(racine), assiette=AssietteActivite(racine))
    ligne = cout.annee(simulateur.distribution.millesime)
    assert ligne is not None and ligne.garantie is not None
    return parametres, simulateur, ligne.garantie


def test_le_rapport_un_redonne_le_cout_que_la_page_affiche(
        lectures, garantie_de_l_enquete):
    """Un facteur par sexe, mais les deux égaux : c'est la convention en vigueur.

    Le coût d'un plancher différentiel est LINÉAIRE en la distribution, et la
    colonne « ensemble » de l'enquête est le mélange de ses deux colonnes de
    sexe. Déplacer les deux du même facteur doit donc rendre, au centime, ce
    que donne le déplacement de l'ensemble. Ce test est le raccord : il tombe
    si le poids des sexes cesse d'être celui de l'enquête, si la contrainte de
    masse est mal posée, ou si le script cesse de lire le facteur de la page.
    """
    parametres, simulateur, garantie = garantie_de_l_enquete
    majore = [l for l in lectures if l.plancher.startswith("plancher majoré")]
    assert majore, "le plancher majoré doit être parcouru"
    reference = next(l for l in majore if l.rapport == 1.0)
    assert reference.facteur_femmes == pytest.approx(garantie.facteur)
    assert reference.facteur_hommes == pytest.approx(garantie.facteur)
    # Le coût de la trajectoire est celui des 65 ans et plus ; celui du script,
    # celui de TOUS les retraités de l'enquête, comme le tableau des quatre
    # lectures de la page. Les deux se déduisent l'un de l'autre par le rapport
    # des effectifs, et c'est cette identité qu'on vérifie.
    attendu = (garantie.cout_constants / 1000.0
               * simulateur.effectifs.effectif(
                   "tous_regimes", simulateur.distribution.millesime)
               / garantie.effectif)
    # PAS À ZÉRO, ET LA SOURCE DIT POURQUOI. La DREES publie ses parts
    # arrondies au centième de point : sa colonne « ensemble » n'est donc le
    # mélange exact de ses deux colonnes de sexe qu'à cet arrondi près, et le
    # coût recomposé s'en écarte d'autant — 1,4·10⁻⁴ en valeur relative, soit
    # quatre millions sur vingt-huit milliards. Redresser les parts pour
    # fermer l'écart inventerait une précision que la source ne donne pas.
    # La borne reste assez étroite pour attraper toute dérive de structure.
    assert reference.cout_mds == pytest.approx(attendu, rel=1e-3)
    assert reference.ecart_mds == pytest.approx(0.0)


def test_la_contrainte_de_masse_tient_sur_toute_la_colonne(lectures):
    """Quel que soit ``r``, la moyenne d'ensemble bouge du même facteur.

    C'est ce qui fait de l'exercice une RÉPARTITION et non une hypothèse de
    plus : la grille de cas types garde le dernier mot sur l'agrégat, et le
    script ne décide que du partage entre les deux sexes.
    """
    from retraite_notionnelle.donnees.distribution import (
        DistributionPensions, part_femmes,
    )
    parametres = Parametres()
    racine = parametres.racine_donnees
    millesime = Simulateur(parametres).distribution.millesime
    poids = part_femmes(racine, millesime)
    moyennes = {
        sexe: garantie_par_sexe._moyenne(
            DistributionPensions(racine, sexe=sexe, millesime=millesime))
        for sexe in ("F", "H")
    }
    ensemble = poids * moyennes["F"] + (1.0 - poids) * moyennes["H"]
    reference = next(l for l in lectures if l.rapport == 1.0)
    for lecture in lectures:
        deplacee = (poids * moyennes["F"] * lecture.facteur_femmes
                    + (1.0 - poids) * moyennes["H"] * lecture.facteur_hommes)
        assert deplacee / ensemble == pytest.approx(reference.facteur_femmes)


def test_l_ecart_uniforme_est_toujours_une_borne_basse(lectures):
    """Le sens de l'écart n'est pas douteux, et le tableau doit le montrer.

    Déplacer davantage les pensions des femmes — qui sont les plus basses —
    tout en tenant la moyenne d'ensemble fait passer plus de monde sous le
    plancher, et jamais moins. La convention uniforme sous-estime donc le
    coût, et c'est ce que la réserve des limites affirme.
    """
    for plancher in {lecture.plancher for lecture in lectures}:
        colonne = sorted((l for l in lectures if l.plancher == plancher),
                         key=lambda l: -l.rapport)
        assert colonne[0].rapport == 1.0
        couts = [lecture.cout_mds for lecture in colonne]
        assert couts == sorted(couts), plancher
        assert couts[-1] > couts[0], plancher
        # Et l'ampleur reste seconde : le tableau ne vaudrait rien s'il
        # laissait croire que la réserve emporte le chiffrage.
        assert couts[-1] / couts[0] < 1.10, plancher


def test_le_tableau_se_rend_sans_exploser(lectures):
    texte = garantie_par_sexe.tableau(lectures, Parametres())
    assert "r=fF/fH" in texte
    assert texte.count("Md") >= len(lectures)
