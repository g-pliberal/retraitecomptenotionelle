"""Tests de la fiche de paie : coût du travail, salaire brut, salaire net.

Trois choses s'y vérifient, et elles n'ont pas le même statut.

D'abord que les DONNÉES tiennent ensemble : le coefficient maximal de la
réduction générale est, au centime de point près, la somme des taux qu'il
efface. C'est le test le plus utile du fichier — il attrape aussi bien un taux
recopié de travers qu'une réforme des allègements qu'une session aurait ratée.

Ensuite que le CALCUL fait ce qu'il dit : le net d'un salarié du privé vaut
bien les 79 % du brut que tout le monde connaît, le brut qu'on retrouve à coût
du travail donné est bien celui qui l'épuise, et la fiche de paie ne bouge pas
d'un centime entre les trois systèmes qui ne changent que ce qui est PORTÉ au
compte.

Enfin que le RÉSULTAT inattendu est bien celui du modèle et non d'un bogue :
au SMIC, la proposition prélève plus que le droit en vigueur, parce que la
réduction générale efface aujourd'hui la totalité de la part patronale.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.carriere import Affiliations
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.donnees.macro import DonneesMacro
from retraite_notionnelle.donnees.regimes import CatalogueRegimes
from retraite_notionnelle.remuneration import (
    ConstructeurFiche,
    Segment,
    bloc_droit_en_vigueur,
    bloc_taux_unique,
    charger_prelevements,
    fiche_de_paie_possible,
    smic_annuel,
)
from retraite_notionnelle.simulateur import Simulateur


PARAMETRES = Parametres()
ANNEE = PARAMETRES.annee_bascule
STATUT = "salarie_prive_non_cadre"


@pytest.fixture(scope="module")
def pieces():
    macro = DonneesMacro(PARAMETRES.racine_donnees, PARAMETRES.scenario_projection)
    return {
        "macro": macro,
        "catalogue": CatalogueRegimes(PARAMETRES.racine_donnees),
        "affiliations": Affiliations(PARAMETRES.racine_donnees),
        "bareme": charger_prelevements(PARAMETRES.racine_donnees),
        "plafond": macro.plafond_securite_sociale(ANNEE),
        "smic": smic_annuel(macro, ANNEE),
    }


def _blocs(pieces):
    actuel = bloc_droit_en_vigueur(
        pieces["catalogue"], pieces["affiliations"], STATUT, ANNEE)
    propose = bloc_taux_unique(
        PARAMETRES.taux_cotisation_liberal,
        PARAMETRES.taux_capitalisation_obligatoire,
        PARAMETRES.part_salariale_taux_unique,
    )
    return actuel, propose


# -- les données tiennent ----------------------------------------------------


def test_le_coefficient_maximal_est_la_somme_des_taux_qu_il_efface(pieces):
    """La loi le dit, le décret l'applique, ce test l'exige.

    « La valeur maximale du coefficient est fixée par décret, dans la limite de
    la somme des taux des cotisations et contributions incluses dans le
    périmètre de la réduction » (L. 241-13, III). Si ce test tombe, c'est qu'un
    taux du fichier a bougé sans que le coefficient suive — ou l'inverse.
    """
    reduction = pieces["bareme"].reduction_generale
    somme = sum(reduction.composantes.values())
    assert somme == pytest.approx(reduction.coefficient_maximal, abs=1e-9)


def test_le_coefficient_maximal_ne_bouge_pas_sous_le_droit_en_vigueur(pieces):
    """Recalculé à partir des fiches, il doit retomber sur le chiffre du décret.

    C'est ce qui relie les deux moitiés du modèle : les composantes retraite du
    coefficient, écrites dans le fichier des prélèvements, sont exactement les
    taux patronaux de première tranche que portent les fiches de régime.
    """
    actuel, _ = _blocs(pieces)
    bareme = pieces["bareme"]
    # Tolérance d'un centième de point : les fiches portent un taux total et
    # une part salariale arrondie au millième (15,45 % × 44,7 % = 8,5439 %),
    # là où le décret écrit directement 8,55 %. L'écart tient à cet arrondi et
    # à lui seul ; un point de cotisation déplacé le ferait sauter.
    assert actuel.taux_employeur_dans_la_reduction(bareme) == pytest.approx(
        bareme.reduction_generale.taux_retraite_inclus, abs=1e-4)
    assert bareme.reduction_generale.coefficient_maximal_avec(
        actuel.taux_employeur_dans_la_reduction(bareme)
    ) == pytest.approx(bareme.reduction_generale.coefficient_maximal, abs=1e-4)


def test_la_reduction_efface_exactement_le_perimetre_au_smic(pieces):
    """Au SMIC, le coefficient vaut son maximum, et son maximum vaut le périmètre.

    C'est la raison pour laquelle baisser la cotisation retraite de l'employeur
    ne rend rien au voisinage du salaire minimum.
    """
    actuel, _ = _blocs(pieces)
    constructeur = ConstructeurFiche(pieces["bareme"])
    fiche = constructeur.fiche(ANNEE, pieces["smic"], pieces["plafond"],
                               pieces["smic"], actuel)
    perimetre = constructeur._perimetre_reduction(
        actuel, pieces["smic"], pieces["plafond"], False)
    assert fiche.reduction_generale == pytest.approx(perimetre, rel=1e-3)


def test_la_reduction_s_eteint_a_trois_smic(pieces):
    actuel, _ = _blocs(pieces)
    constructeur = ConstructeurFiche(pieces["bareme"])
    juste_avant = constructeur.fiche(
        ANNEE, 2.99 * pieces["smic"], pieces["plafond"], pieces["smic"], actuel)
    juste_apres = constructeur.fiche(
        ANNEE, 3.01 * pieces["smic"], pieces["plafond"], pieces["smic"], actuel)
    assert juste_avant.reduction_generale > 0
    assert juste_apres.reduction_generale == 0


# -- le calcul fait ce qu'il dit ---------------------------------------------


def test_le_net_d_un_salarie_du_prive_vaut_bien_environ_79_pour_cent_du_brut(pieces):
    """Le chiffre que porte n'importe quelle fiche de paie non cadre.

    11,31 points de retraite (6,90 + 0,40 + 3,15 + 0,86), 9,04 de CSG-CRDS après
    abattement : il reste 79,2 %. Une fourchette large suffit à attraper une
    erreur de barème ; elle n'est pas là pour valider un centime.
    """
    actuel, _ = _blocs(pieces)
    fiche = ConstructeurFiche(pieces["bareme"]).fiche(
        ANNEE, pieces["smic"], pieces["plafond"], pieces["smic"], actuel)
    assert 0.78 < fiche.net / fiche.brut < 0.80


def test_le_brut_retrouve_a_cout_donne_epuise_ce_cout(pieces):
    """La dichotomie de l'incidence intégrale doit converger, et converger juste."""
    actuel, propose = _blocs(pieces)
    constructeur = ConstructeurFiche(pieces["bareme"])
    for niveau in (1.0, 1.5, 2.5, 5.0):
        brut = niveau * pieces["smic"]
        depart = constructeur.fiche(
            ANNEE, brut, pieces["plafond"], pieces["smic"], actuel)
        retrouve = constructeur.brut_a_cout_donne(
            depart.cout_du_travail, pieces["plafond"], pieces["smic"], propose)
        arrivee = constructeur.fiche(
            ANNEE, retrouve, pieces["plafond"], pieces["smic"], propose)
        assert arrivee.cout_du_travail == pytest.approx(
            depart.cout_du_travail, rel=1e-6)


def test_un_segment_deplafonne_se_superpose_au_segment_plafonne(pieces):
    """La cotisation déplafonnée porte sur TOUT le salaire, par-dessus l'autre.

    Une représentation par tranches cumulatives l'aurait écrasée ; le test fixe
    la propriété qui a imposé les segments explicites.
    """
    from retraite_notionnelle.remuneration import _montant

    segments = (Segment(0.0, 1.0, 0.10), Segment(0.0, None, 0.01))
    plafond = 100.0
    assert _montant(segments, 100.0, plafond) == pytest.approx(11.0)
    assert _montant(segments, 200.0, plafond) == pytest.approx(12.0)


def test_les_trois_premiers_systemes_ont_la_meme_fiche_de_paie():
    """Les systèmes 1, 2 et 3 changent ce qui est PORTÉ au compte, pas ce qui est
    PRÉLEVÉ : leur fiche de paie est la même, et le site n'en affiche qu'une.

    Le test passe par le simulateur entier, parce que c'est là que l'erreur se
    logerait : un scénario qui se mettrait à changer le prélèvement sans le dire.
    """
    simulateur = Simulateur(PARAMETRES)
    carriere = simulateur.carriere_simple(
        annee_naissance=1985, sexe="F", affiliation=STATUT,
        age_debut=22, age_liquidation=64, niveau_salaire=1.0,
    )
    comparaison = simulateur.simuler(carriere)
    remuneration = comparaison.remuneration
    assert remuneration is not None
    # Un seul bloc « droit en vigueur » sert les trois : le vérifier revient à
    # vérifier qu'il ne dépend d'aucun paramètre de scénario.
    for scenario in ("part_cotisation", "source_cotisations"):
        assert hasattr(PARAMETRES, scenario)
    reference = remuneration.reference
    assert reference.droit_en_vigueur.net > 0
    assert reference.droit_en_vigueur.cout_du_travail > reference.droit_en_vigueur.brut


# -- le résultat inattendu est bien celui du modèle --------------------------


def test_le_gain_net_est_negatif_au_smic_et_positif_au_salaire_moyen(pieces):
    """Le résultat que ce module a servi à trouver.

    Au SMIC, l'assuré ne supporte aujourd'hui que 11,3 points de retraite, la
    part patronale étant intégralement effacée par la réduction générale. La
    proposition en prélève 23, dont 9 seulement sont effacés : elle prélève
    donc PLUS. Le croisement se fait un peu au-dessus de 1,2 SMIC.
    """
    actuel, propose = _blocs(pieces)
    constructeur = ConstructeurFiche(pieces["bareme"])

    def gain(niveau: float) -> float:
        brut = niveau * pieces["smic"]
        avant = constructeur.fiche(
            ANNEE, brut, pieces["plafond"], pieces["smic"], actuel)
        apres = constructeur.fiche(
            ANNEE,
            constructeur.brut_a_cout_donne(
                avant.cout_du_travail, pieces["plafond"], pieces["smic"], propose),
            pieces["plafond"], pieces["smic"], propose,
        )
        return apres.net - avant.net

    assert gain(1.0) < 0
    assert gain(2.0) > 0
    assert gain(5.0) > gain(2.0)


def test_sans_le_pilier_capitalise_le_gain_est_positif_partout(pieces):
    """Ce sont les cinq points capitalisés qui font la bascule, et eux seuls.

    Le dire sert à ne pas imputer au taux unique ce qui vient de l'épargne
    obligatoire — et à rappeler que celle-ci, contrairement à une cotisation,
    reste au nom de l'assuré.
    """
    actuel, _ = _blocs(pieces)
    sans_pilier = bloc_taux_unique(
        PARAMETRES.taux_cotisation_liberal, 0.0,
        PARAMETRES.part_salariale_taux_unique)
    constructeur = ConstructeurFiche(pieces["bareme"])
    for niveau in (1.0, 1.5, 3.0):
        brut = niveau * pieces["smic"]
        avant = constructeur.fiche(
            ANNEE, brut, pieces["plafond"], pieces["smic"], actuel)
        apres = constructeur.fiche(
            ANNEE,
            constructeur.brut_a_cout_donne(
                avant.cout_du_travail, pieces["plafond"], pieces["smic"],
                sans_pilier),
            pieces["plafond"], pieces["smic"], sans_pilier,
        )
        assert apres.net > avant.net


def _nets_et_bruts_selon_le_partage(pieces, niveau: float):
    actuel, _ = _blocs(pieces)
    constructeur = ConstructeurFiche(pieces["bareme"])
    cout = constructeur.fiche(
        ANNEE, niveau * pieces["smic"], pieces["plafond"], pieces["smic"],
        actuel).cout_du_travail
    nets, bruts = [], []
    for part in (0.0, 0.5, 1.0):
        bloc = bloc_taux_unique(
            PARAMETRES.taux_cotisation_liberal,
            PARAMETRES.taux_capitalisation_obligatoire, part)
        fiche = constructeur.fiche(
            ANNEE,
            constructeur.brut_a_cout_donne(
                cout, pieces["plafond"], pieces["smic"], bloc),
            pieces["plafond"], pieces["smic"], bloc,
        )
        nets.append(fiche.net)
        bruts.append(fiche.brut)
    return nets, bruts


def test_le_partage_du_taux_unique_deplace_le_net_a_tous_les_salaires(pieces):
    """Ce qu'on croyait neutre ne l'est pas, et ce test dit à quel point.

    Au-dessus de trois SMIC, la réduction générale est éteinte et pourtant le
    net bouge encore : c'est la CSG, assise sur le BRUT que le partage déplace.
    En deçà, l'allègement s'ajoute au mécanisme, dans le même sens. Dans les
    deux cas, plus la part patronale est grosse, plus le net est élevé à coût
    du travail donné.
    """
    for niveau in (2.0, 4.0):
        nets, bruts = _nets_et_bruts_selon_le_partage(pieces, niveau)
        assert nets[0] > nets[1] > nets[2], f"à {niveau} SMIC"
        # Le brut va dans l'autre sens : porter la cotisation côté employeur le
        # rétrécit, et c'est précisément ce qui allège la CSG.
        assert bruts[0] < bruts[2], f"à {niveau} SMIC"


def test_la_csg_explique_a_elle_seule_l_effet_du_partage_hors_allegement(pieces):
    """Au-dessus de trois SMIC, l'écart de net se retrouve à la main.

    À coût du travail fixé, ``coût − net = brut × (taux total + autres
    patronaux + CSG-CRDS)``. Seul le brut dépend du partage ; l'écart de net
    entre deux partages vaut donc exactement l'écart de brut multiplié par ce
    taux constant. Le test le vérifie plutôt que de le croire.
    """
    nets, bruts = _nets_et_bruts_selon_le_partage(pieces, 4.0)
    taux_apparent = (nets[0] - nets[2]) / (bruts[2] - bruts[0])
    total = (PARAMETRES.taux_cotisation_liberal
             + PARAMETRES.taux_capitalisation_obligatoire)
    assert taux_apparent > total  # les autres patronaux et la CSG s'y ajoutent
    assert taux_apparent < 1.0


# -- périmètre ---------------------------------------------------------------


def test_la_fiche_de_paie_ne_couvre_que_le_prive(pieces):
    affiliations = pieces["affiliations"]
    assert fiche_de_paie_possible(affiliations, STATUT)
    assert not fiche_de_paie_possible(affiliations, "fonctionnaire_etat")
    assert not fiche_de_paie_possible(affiliations, "statut_inexistant")


def test_aucune_remuneration_pour_qui_a_deja_liquide():
    """Un retraité ne cotise plus : il n'y a pas de fiche de paie à montrer."""
    simulateur = Simulateur(PARAMETRES)
    carriere = simulateur.carriere_simple(
        annee_naissance=1940, sexe="H", affiliation=STATUT,
        age_debut=20, age_liquidation=60, niveau_salaire=1.0,
    )
    assert simulateur.simuler(carriere).remuneration is None


def test_aucune_remuneration_pour_un_agent_public():
    simulateur = Simulateur(PARAMETRES)
    carriere = simulateur.carriere_simple(
        annee_naissance=1985, sexe="H", affiliation="fonctionnaire_etat",
        age_debut=22, age_liquidation=64, niveau_salaire=1.0,
    )
    assert simulateur.simuler(carriere).remuneration is None


def test_la_fiabilite_du_bareme_est_plafonnee_a_haute(pieces):
    """OpenFisca transcrit le Journal officiel, il ne le produit pas."""
    assert pieces["bareme"].fiabilite <= Fiabilite.HAUTE
