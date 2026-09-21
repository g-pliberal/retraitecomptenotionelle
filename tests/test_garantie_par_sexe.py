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

from dataclasses import replace

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


def test_le_rapport_mesure_redonne_le_cout_que_la_page_affiche(
        lectures, garantie_de_l_enquete):
    """La ligne marquée d'une étoile est celle que le modèle applique.

    Le script ne recalcule pas la trajectoire : il redéplace la distribution à
    la main. Si sa ligne mesurée ne redonne pas le coût de la page, toute la
    sensibilité porte à côté, et silencieusement. Ce test est le raccord : il
    tombe si le poids des sexes cesse d'être celui de l'enquête, si la
    contrainte de masse est mal posée, ou si le script cesse de lire le
    facteur et le rapport que le modèle applique.
    """
    parametres, simulateur, garantie = garantie_de_l_enquete
    majore = [l for l in lectures if l.plancher.startswith("plancher majoré")]
    assert majore, "le plancher majoré doit être parcouru"
    reference = next(l for l in majore if l.mesure)
    assert reference.rapport == pytest.approx(
        simulateur.caracteristiques.rapport_deplacement())
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
    # L'écart est compté depuis la convention uniforme, qui est en tête de
    # colonne : celui de la ligne mesurée est donc ce que la mesure a coûté.
    assert reference.ecart_mds > 0.0


def test_le_rapport_un_redonne_l_ancienne_convention(lectures):
    """La colonne « 1,00 » doit rendre ce que le modèle donnait avant la mesure.

    Elle est le repère de ce que la convention uniforme valait, et elle ne vaut
    que si elle le vaut exactement : ce test la confronte à une trajectoire
    calculée sous ``rapport_deplacement_sexe = 1``, c'est-à-dire au modèle
    d'avant le 21 septembre 2026.
    """
    parametres = replace(Parametres(), rapport_deplacement_sexe=1.0)
    racine = parametres.racine_donnees
    simulateur = Simulateur(parametres)
    cout = calculer_cout(simulateur, DepensesRetraite(racine), Population(racine),
                         ComptesRetraite(racine), assiette=AssietteActivite(racine))
    ligne = cout.annee(simulateur.distribution.millesime)
    assert ligne is not None and ligne.garantie is not None
    attendu = (ligne.garantie.cout_constants / 1000.0
               * simulateur.effectifs.effectif(
                   "tous_regimes", simulateur.distribution.millesime)
               / ligne.garantie.effectif)
    uniforme = next(l for l in lectures
                    if l.plancher.startswith("plancher majoré") and l.rapport == 1.0)
    # Le mélange des deux colonnes de sexe ne redonne la colonne « ensemble »
    # qu'à l'arrondi de publication près — voir le test précédent.
    assert uniforme.cout_mds == pytest.approx(attendu, rel=1e-3)
    # Et la mesure coûte PLUS que la convention qu'elle remplace : c'est tout
    # ce que la réserve des limites annonçait.
    mesure = next(l for l in lectures
                  if l.plancher.startswith("plancher majoré") and l.mesure)
    assert mesure.cout_mds > uniforme.cout_mds


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
    uniforme = next(l for l in lectures if l.rapport == 1.0)
    for lecture in lectures:
        deplacee = (poids * moyennes["F"] * lecture.facteur_femmes
                    + (1.0 - poids) * moyennes["H"] * lecture.facteur_hommes)
        assert deplacee / ensemble == pytest.approx(uniforme.facteur_femmes)


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
        assert sum(1 for lecture in colonne if lecture.mesure) == 1
        couts = [lecture.cout_mds for lecture in colonne]
        assert couts == sorted(couts), plancher
        assert couts[-1] > couts[0], plancher
        # Et l'ampleur reste seconde : le tableau ne vaudrait rien s'il
        # laissait croire que la réserve emporte le chiffrage.
        assert couts[-1] / couts[0] < 1.10, plancher


def test_les_minima_pesent_sur_les_femmes_et_restent_sous_le_pour_cent(lectures):
    """Ce que les minima apportent : mesuré, signé, et petit.

    Le troisième terme du rapport ne vient pas de la même étagère que les deux
    autres : les effectifs de bénéficiaires sont LUS sur l'enquête, la masse
    est prise au modèle, faute qu'aucune série ne la publie. Ce test tient ce
    que la page en dit — qu'il pèse sur les femmes, que son sens est le même
    que celui des deux autres, et qu'il reste sous le pour cent de coût, ce qui
    est la raison de ne pas le retenir dans ``r``.
    """
    lectures_minima = garantie_par_sexe.minima(Parametres())
    assert {l.champ for l in lectures_minima} == {"régime principal", "tous régimes"}
    mesure = Simulateur(Parametres()).caracteristiques.rapport_deplacement()
    for lecture in lectures_minima:
        # Les bénéficiaires sont d'abord des femmes, et le minimum pèse donc
        # plus lourd dans leur pension — davantage de têtes sur une pension
        # moyenne plus basse.
        assert lecture.beneficiaires["F"] > lecture.beneficiaires["H"]
        assert lecture.part["F"] > lecture.part["H"]
        # Le terme va donc dans le même sens que les deux autres.
        assert 0.97 < lecture.rapport < 1.0
        assert 0.5 < mesure * lecture.rapport < mesure
    # Le champ le plus étroit — les bénéficiaires de leur régime principal —
    # concentre le plus les femmes, et pèse donc le plus.
    principal = next(l for l in lectures_minima if l.champ == "régime principal")
    tous = next(l for l in lectures_minima if l.champ == "tous régimes")
    assert principal.rapport < tous.rapport
    # Et ce que cela ferait au coût reste sous le pour cent : c'est la mesure
    # qui justifie de laisser ce terme hors du rapport retenu.
    reference = next(l for l in lectures
                     if l.plancher.startswith("plancher majoré") and l.mesure)
    colonne = sorted((l for l in lectures if l.plancher.startswith("plancher majoré")),
                     key=lambda l: abs(l.rapport - mesure * principal.rapport))
    assert colonne[0].cout_mds / reference.cout_mds < 1.01


def test_le_tableau_se_rend_sans_exploser(lectures):
    texte = garantie_par_sexe.tableau(lectures, Parametres())
    assert "r=fF/fH" in texte
    assert texte.count("Md") >= len(lectures)
    lectures_minima = garantie_par_sexe.minima(Parametres())
    rendu = garantie_par_sexe.tableau_minima(lectures_minima, 0.834)
    assert "régime principal" in rendu and "tous régimes" in rendu
