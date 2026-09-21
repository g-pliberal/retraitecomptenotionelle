"""Ce que l'erreur d'âge coûte : mesuré, et laissé dehors pour une raison chiffrée.

La confrontation par catégorie socioprofessionnelle avait trouvé 1,17 an
d'écart en valeur absolue, et le dépôt avait écrit qu'il ne corrigeait rien.
Ces tests tiennent la raison chiffrée de ne pas corriger : le contrefactuel qui
rapproche chaque cas type de sa catégorie **ne déplace pas les cinq scénarios
notionnels**, et il ÉLOIGNE le système actuel de la projection du COR au lieu
de l'en rapprocher. L'âge de départ n'est donc pas l'explication de l'écart que
le § 5 ter de `limites.md` laisse ouvert.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from retraite_notionnelle import cout as C
from retraite_notionnelle.castypes import CAS_TYPES
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.donnees.assiette import AssietteActivite
from retraite_notionnelle.donnees.depenses import DepensesRetraite
from retraite_notionnelle.donnees.equilibre import ComptesRetraite
from retraite_notionnelle.donnees.population import Population
from retraite_notionnelle.simulateur import Simulateur

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import cout_age_depart as CAD  # noqa: E402

#: Les cas types que `cas_types_csp.yaml` laisse hors champ : le contrefactuel
#: ne doit pas y toucher.
HORS_CHAMP = ("militaire", "agent_sncf_conduite", "agent_ieg", "fonctionnaire_actif")

#: Les deux régimes EN POINTS, auxquels le modèle n'oppose aucune durée
#: requise : leur âge de départ ne répond pas à leur âge d'entrée.
EN_POINTS = ("exploitant_agricole", "profession_liberale")


@pytest.fixture(scope="module")
def simulateur():
    return Simulateur(Parametres())


@pytest.fixture(scope="module")
def mesure(simulateur):
    racine = simulateur.parametres.racine_donnees
    donnees = (DepensesRetraite(racine), Population(racine),
               ComptesRetraite(racine), AssietteActivite(racine))
    decalages = CAD.chercher_decalages(simulateur)
    corrigee = CAD.grille_contrefactuelle(decalages)
    return {
        "decalages": decalages,
        "corrigee": corrigee,
        "reference": CAD.trajectoire(simulateur, donnees, CAS_TYPES),
        "contrefactuel": CAD.trajectoire(simulateur, donnees, corrigee),
    }


def test_le_contrefactuel_ne_touche_ni_les_fiches_ni_les_hors_champ(mesure):
    """Aucun âge trouvé ici n'entre dans `castypes.py`.

    Une fiche se réécrit sur ce qu'on sait d'une carrière, pas sur ce qui
    rapproche une moyenne d'une autre. Le contrefactuel est une grille de
    plus, et la grille de référence en sort intacte.
    """
    fiches = {cas.code: cas.age_debut for cas in CAS_TYPES}
    corrigee = {cas.code: cas.age_debut for cas in mesure["corrigee"]}
    assert set(corrigee) == set(fiches)
    for code in HORS_CHAMP:
        assert corrigee[code] == fiches[code], code

    for decalage in mesure["decalages"]:
        assert decalage.entree_fiche == fiches[decalage.code]
        assert (CAD.ENTREE_MINIMALE <= decalage.entree_contrefactuelle
                <= CAD.ENTREE_MAXIMALE), decalage.code


def test_deux_cas_types_ne_repondent_pas_a_leur_age_d_entree(mesure, simulateur):
    """Et la raison se vérifie, au lieu de se supposer.

    L'exploitant agricole et la profession libérale relèvent de régimes en
    points : le modèle ne leur oppose aucune durée requise, leur départ suit
    l'âge légal, et le déplacer de huit ans d'âge d'entrée n'y change rien.
    Leur écart à leur catégorie vient donc d'ailleurs, et ce contrefactuel ne
    le porte pas — c'est la première des trois raisons qui en font une borne
    basse.
    """
    insensibles = {d.code for d in mesure["decalages"] if d.insensible}
    assert insensibles == set(EN_POINTS)

    for code in EN_POINTS:
        cas = next(c for c in CAS_TYPES if c.code == code)
        resultat = simulateur.scenario_actuel.calculer(
            cas.construire(simulateur, 1955, "droit"))
        assert resultat.trimestres_requis == 0, code


def test_les_scenarios_notionnels_ne_bougent_pas(mesure):
    """Le résultat qui ferme le sujet.

    Les cinq scénarios que le site compare se déplacent de moins d'un dixième
    de point de PIB — l'erreur d'âge leur est invisible. Dans un compte
    notionnel, partir plus tôt allonge le diviseur autant que la carrière
    raccourcie retire au capital : les deux termes se répondent.
    """
    for scenario, _ in C.SCENARIOS:
        if scenario == "actuel":
            continue
        ecart = mesure["contrefactuel"][scenario] - mesure["reference"][scenario]
        assert abs(ecart) < 0.001, f"{scenario} : {ecart * 100:+.2f} point"


def test_corriger_les_ages_eloigne_le_modele_du_COR(mesure):
    """Et c'est la réponse à la question ouverte du § 5 ter.

    Le système actuel, lui, bouge — une carrière plus longue y vaut une
    pension plus forte, sans diviseur pour l'amortir. Mais il bouge dans le
    MAUVAIS sens : l'écart avec la projection du COR se creuse. L'âge de
    départ n'explique donc pas cet écart, et la piste du taux de remplacement
    reste entière.
    """
    avant = mesure["reference"]["actuel"]
    apres = mesure["contrefactuel"]["actuel"]
    assert apres > avant
    assert abs(apres - CAD.COR_HORIZON) > abs(avant - CAD.COR_HORIZON)
    assert 0.002 < apres - avant < 0.02


def test_les_deux_criteres_d_age_tirent_en_sens_contraire(mesure, simulateur):
    """Ce que la mesure laisse ouvert, et qu'elle ne tranche pas.

    Rapprocher chaque cas type de SA catégorie éloigne leur SOMME de l'âge
    conjoncturel tous régimes. Les deux critères ne peuvent pas être satisfaits
    ensemble, et les quatre cas types hors champ — un douzième de la grille, à
    des âges de quarante-quatre à cinquante-sept ans — sont le suspect. Ce test
    tient le constat, pas son explication.
    """
    fiches = CAD.concordance(simulateur, CAS_TYPES)
    contrefactuel = CAD.concordance(simulateur, mesure["corrigee"])
    assert abs(fiches) < 0.2
    assert contrefactuel < fiches
    assert abs(contrefactuel) > abs(fiches)
