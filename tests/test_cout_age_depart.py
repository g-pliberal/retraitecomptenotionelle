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
HORS_CHAMP = ("militaire", "agent_sncf_conduite", "agent_ieg",
              "fonctionnaire_actif", "profession_liberale")

#: Les deux cas types dont la carrière est ENTIÈREMENT en points : le moteur
#: ne leur opposait ni durée, ni âge d'ouverture, ni carrière longue.
TOUT_EN_POINTS = ("exploitant_agricole", "profession_liberale")


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


def test_tous_les_cas_types_comparables_repondent_a_leur_age_d_entree(mesure):
    """L'angle mort du contrefactuel est refermé.

    Deux cas types n'y répondaient pas, et la raison qu'on leur prêtait était
    fausse — « des régimes en points, auxquels le modèle n'oppose aucune durée
    requise ». C'était un défaut du moteur, corrigé le 21 septembre 2026 : les
    neuf cas types comparables répondent tous, et la recherche d'âge d'entrée
    ne laisse plus personne de côté.
    """
    assert not [d.code for d in mesure["decalages"] if d.insensible]


def test_une_carriere_tout_en_points_se_voit_opposer_sa_duree(simulateur):
    """Le premier défaut que la recherche d'âge d'entrée a fait voir.

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


def test_une_carriere_tout_en_points_se_voit_opposer_un_age(simulateur):
    """Le second, et le plus visible : on pouvait liquider à cinquante ans.

    `calculer` ne lisait l'âge d'ouverture opposable que sur les périodes en
    ANNUITÉS. Une carrière entière en points n'en ayant aucune, aucun âge ne
    lui était opposé : le simulateur servait une pension d'exploitant agricole
    à cinquante ans sans rien refuser, quand il refusait la même chose à
    l'artisan de la page voisine.
    """
    artisan = next(c for c in CAS_TYPES if c.code == "artisan")
    temoin = simulateur.scenario_actuel.calculer(
        artisan._carriere(simulateur, 2000, 50.0))
    assert not temoin.liquidation_ouverte, "l'artisan sert de témoin"

    for code in TOUT_EN_POINTS:
        cas = next(c for c in CAS_TYPES if c.code == code)
        resultat = simulateur.scenario_actuel.calculer(
            cas._carriere(simulateur, 2000, 50.0))
        assert not resultat.liquidation_ouverte, code
        assert resultat.motif_ouverture == "non_ouverte", code
        assert resultat.age_ouverture_opposable is not None, code


def test_la_carriere_longue_est_ouverte_aux_regimes_en_points(simulateur):
    """Et les deux règles d'âge la lisent sur la même liste.

    L. 732-18-1 du code rural la donne aux non-salariés agricoles, le II de
    L. 643-3 du code de la sécurité sociale aux professions libérales par
    renvoi à L. 351-1-1. Ne l'ouvrir qu'au taux plein faisait rendre à celui-ci
    un âge ANTÉRIEUR à celui que l'ouverture accordait — deux règles du même
    droit qui se contredisent.
    """
    actuel = simulateur.scenario_actuel
    cas = next(c for c in CAS_TYPES if c.code == "exploitant_agricole")
    carriere = cas.construire(simulateur, 2000, "droit")

    assert actuel.age_taux_plein_droit(carriere) >= actuel.age_ouverture_droit(carriere)
    resultat = actuel.calculer(carriere)
    assert resultat.motif_ouverture == "carriere_longue"
    assert resultat.liquidation_ouverte


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


def test_le_plafond_de_decote_ne_mord_sur_aucune_liquidation_ouverte(simulateur):
    """Le plafond de vingt trimestres est l'arithmétique des deux âges.

    Il est écrit là où le droit a voulu l'écrire — R. 643-7 pour les libéraux,
    R. 723-38 pour les avocats, le I de L. 14 pour la fonction publique — et
    absent de R. 351-27 2° comme de R. 732-61. La raison est que l'écart entre
    l'âge d'ouverture et l'âge d'annulation vaut AU PLUS vingt trimestres :
    exactement vingt pour les générations 1930 à 1961, douze pour celles
    d'après 1968. Sur toute liquidation que le droit ouvre, le décompte par
    l'âge est donc borné par construction.

    Ce test le vérifie plutôt que de le supposer : il rejoue chaque décote en
    ôtant le plafond, et refuse qu'une seule liquidation OUVERTE en soit
    changée. S'il tombe un jour, c'est que les âges ont bougé, et le plafond
    cessera d'être invisible.
    """
    import dataclasses

    from retraite_notionnelle.scenarios import actuel as A

    original = A.ScenarioActuel._trimestres_de_decote
    mordu = {"oui": False}

    def espion(self, periode, carriere, trimestres, requis, age_liquidation,
               age_annulation):
        borne = original(self, periode, carriere, trimestres, requis,
                         age_liquidation, age_annulation)
        if periode.decote_trimestres_maximum is None or borne <= 0:
            return borne
        libre = dataclasses.replace(periode, decote_trimestres_maximum=None)
        if original(self, libre, carriere, trimestres, requis, age_liquidation,
                    age_annulation) > borne + 1e-9:
            mordu["oui"] = True
        return borne

    A.ScenarioActuel._trimestres_de_decote = espion
    try:
        ouvertes = 0
        for cas in CAS_TYPES:
            for generation in (1950, 1970, 1990):
                for quarts in range(232, 272):   # 58,0 à 68,0 ans, au trimestre
                    mordu["oui"] = False
                    resultat = simulateur.scenario_actuel.calculer(
                        cas._carriere(simulateur, generation, quarts / 4))
                    if not resultat.liquidation_ouverte:
                        continue
                    ouvertes += 1
                    assert not mordu["oui"], (
                        f"{cas.code}, génération {generation}, départ à "
                        f"{quarts / 4} ans : le plafond a mordu")
    finally:
        A.ScenarioActuel._trimestres_de_decote = original
    assert ouvertes > 500, "le balayage doit voir des liquidations ouvertes"


def test_l_ecart_des_deux_ages_ne_depasse_jamais_vingt_trimestres(simulateur):
    """La raison pour laquelle le plafond ne mord pas, mesurée dans les tables.

    Vingt trimestres exactement de 1930 à 1961 — soixante ans contre
    soixante-cinq —, puis dix-huit, quinze, treize et douze à mesure que les
    réformes relèvent l'âge d'ouverture sans toucher à l'annulation.
    """
    actuel = simulateur.scenario_actuel
    ecarts = {}
    for generation in range(1930, 2016):
        ouverture = actuel.ages_ouverture.age(generation)
        annulation = actuel.ages_annulation_decote.age(generation)
        if ouverture is None or annulation is None:
            continue
        ecarts[generation] = round((annulation[0] - ouverture[0]) * 4, 2)

    assert ecarts, "les deux tables doivent se recouvrir"
    assert max(ecarts.values()) == 20.0
    assert all(ecarts[g] == 20.0 for g in range(1930, 1962) if g in ecarts)
    assert ecarts[2000] == 12.0


def test_le_liberal_retrouve_le_cas_type_du_COR(simulateur):
    """Le cas type n° 13 du rapport annuel de juin 2026, à trois mois près.

    Le COR décrit un médecin libéral de secteur 1 né en 1960 : il « peut
    prétendre à un départ à 62 ans » et « atteint le taux plein à 66 ans et
    9 mois ». La fiche du dépôt, rendue à la règle ordinaire une fois le défaut
    des carrières tout en points corrigé, donne 62,00 et 67,00 pour la même
    génération.

    C'est la première confrontation du dépôt à un cas type libéral publié, et
    elle vaut mieux que la moyenne d'un groupe de la nomenclature : les deux
    âges sont construits sous la même convention — on part au taux plein — là
    où l'enquête Emploi mesure un comportement.
    """
    actuel = simulateur.scenario_actuel
    fiche = next(cas for cas in CAS_TYPES if cas.code == "profession_liberale")
    assert fiche.regle_liquidation == "taux_plein"
    assert fiche.ecart_liquidation == 0

    carriere = fiche.construire(simulateur, 1960, "droit")
    assert actuel.age_ouverture_droit(carriere) == pytest.approx(62.0, abs=0.01)
    assert actuel.age_taux_plein_droit(carriere) == pytest.approx(66.75, abs=0.3)


def test_le_militaire_est_seul_a_porter_un_ecart_de_liquidation():
    """Le champ a perdu son second usager, et ne doit pas en retrouver un par mégarde.

    `ecart_liquidation` porte la durée de services de la pension militaire, qui
    ne s'ouvre pas à un âge mais à une durée. Le libéral l'a porté jusqu'au
    22 septembre 2026 pour contourner un défaut du moteur ; le défaut corrigé,
    il l'a rendu.
    """
    porteurs = {cas.code: cas.ecart_liquidation
                for cas in CAS_TYPES if cas.ecart_liquidation}
    assert porteurs == {"militaire": 25}
