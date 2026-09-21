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

#: Le seul cas type dont l'âge de départ ne répond pas à son âge d'entrée : sa
#: fiche date le départ sur l'âge d'OUVERTURE, qui ignore la durée par
#: construction. L'exploitant agricole y répondait aussi tant que
#: `age_taux_plein_droit` rendait l'ouverture pour une carrière tout en points.
SUR_L_OUVERTURE = ("profession_liberale",)


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


def test_un_seul_cas_type_ne_repond_pas_a_son_age_d_entree(mesure):
    """Et la raison se vérifie, au lieu de se supposer.

    La profession libérale date son départ sur l'âge d'OUVERTURE, qui ignore la
    durée par construction : déplacer son âge d'entrée de huit ans n'y change
    rien, et son écart à sa catégorie vient d'ailleurs. C'est la première des
    trois raisons qui font de ce contrefactuel une borne basse.

    Ils étaient DEUX jusqu'au 21 septembre 2026, l'exploitant agricole aussi,
    et c'était un défaut du moteur : voir le test suivant.
    """
    insensibles = {d.code for d in mesure["decalages"] if d.insensible}
    assert insensibles == set(SUR_L_OUVERTURE)

    fiches = {cas.code: cas for cas in CAS_TYPES}
    for code in SUR_L_OUVERTURE:
        assert fiches[code].regle_liquidation == "ouverture", code


def test_une_carriere_tout_en_points_se_voit_opposer_sa_duree(simulateur):
    """Le défaut que la recherche d'âge d'entrée a fait voir.

    `age_taux_plein_droit` rendait l'âge d'ouverture dès que la carrière
    n'avait aucune période en annuités — le modèle faisait donc liquider « au
    taux plein » des carrières que `_abattement_points` servait minorées. Le
    droit oppose bien cette durée aux régimes en points : L. 643-3 I du code de
    la sécurité sociale pour les professions libérales, L. 732-24 II du code
    rural pour les non-salariés agricoles.

    L'exploitant agricole en est le témoin : entré à vingt-huit ans il n'a pas
    la durée requise à l'âge d'ouverture, et la règle doit maintenant le faire
    attendre. Entré à vingt ans il l'a, et elle ne le retarde pas.
    """
    from dataclasses import replace

    cas = next(c for c in CAS_TYPES if c.code == "exploitant_agricole")
    ouverture = simulateur.scenario_actuel.age_ouverture_droit(
        cas.construire(simulateur, 1955, "droit"))

    tot = replace(cas, age_debut=20).age_liquidation_pour(simulateur, 1955)
    tard = replace(cas, age_debut=28).age_liquidation_pour(simulateur, 1955)
    assert tot == pytest.approx(ouverture, abs=0.01)
    assert tard > tot + 0.9, "la durée manquante doit retarder le départ"


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
