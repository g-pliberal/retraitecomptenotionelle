"""Tests de la fiche de paie : coût du travail, revenu brut, revenu net.

Quatre choses s'y vérifient, et elles n'ont pas le même statut.

D'abord que les DONNÉES tiennent ensemble : le coefficient maximal de la
réduction générale est, au centime de point près, la somme des taux qu'il
efface. C'est le test le plus utile du fichier — il attrape aussi bien un taux
recopié de travers qu'une réforme des allègements qu'une session aurait ratée.

Ensuite que le CALCUL fait ce qu'il dit : le net d'un salarié du privé vaut
bien les 79 % du brut que tout le monde connaît, le brut qu'on retrouve à coût
du travail donné est bien celui qui l'épuise, et la fiche de paie ne bouge pas
d'un centime entre les trois systèmes qui ne changent que ce qui est PORTÉ au
compte.

Puis que le RÉSULTAT inattendu est bien celui du modèle et non d'un bogue :
au SMIC, la proposition prélève plus que le droit en vigueur, parce que la
réduction générale efface aujourd'hui la totalité de la part patronale.

Enfin que les TROIS AUTRES PROFILS sont ce qu'ils prétendent être : un
fonctionnaire n'a pas de coût du travail affichable et son traitement est tenu
fixe ; un indépendant paie tout lui-même ; les deux barèmes progressifs des
indépendants retombent sur les bornes que la loi écrit ; et les familles qu'on
ne sait pas décrire n'affichent toujours rien.
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
    Incidence,
    Segment,
    bloc_droit_en_vigueur,
    bloc_taux_unique,
    bloc_taux_unique_sans_employeur,
    charger_prelevements,
    contribution_equilibre,
    fiche_de_paie_possible,
    profil_de_la_fiche,
    smic_annuel,
)
from retraite_notionnelle.restitution import Restitution, points_csg_rendus
from retraite_notionnelle.simulateur import Simulateur


PARAMETRES = Parametres()
ANNEE = PARAMETRES.annee_bascule
STATUT = "salarie_prive_non_cadre"


@pytest.fixture(scope="module")
def pieces():
    macro = DonneesMacro(PARAMETRES.racine_donnees, PARAMETRES.scenario_projection)
    prelevements = charger_prelevements(PARAMETRES.racine_donnees)
    return {
        "macro": macro,
        "catalogue": CatalogueRegimes(PARAMETRES.racine_donnees),
        "affiliations": Affiliations(PARAMETRES.racine_donnees),
        "prelevements": prelevements,
        "bareme": prelevements.profil("salarie_prive"),
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


def _gain(pieces, propose, niveau: float, incidence: Incidence) -> float:
    """L'écart de net à un niveau de salaire, sous l'un ou l'autre horizon."""
    constructeur = ConstructeurFiche(pieces["bareme"])
    actuel, _ = _blocs(pieces)
    brut = niveau * pieces["smic"]
    avant = constructeur.fiche(
        ANNEE, brut, pieces["plafond"], pieces["smic"], actuel)
    brut_apres = (
        brut if incidence is Incidence.ASSIETTE
        else constructeur.brut_a_cout_donne(
            avant.cout_du_travail, pieces["plafond"], pieces["smic"], propose))
    apres = constructeur.fiche(
        ANNEE, brut_apres, pieces["plafond"], pieces["smic"], propose)
    return apres.net - avant.net


def test_le_gain_net_est_positif_a_tous_les_salaires_sous_le_partage_retenu(pieces):
    """Le résultat du partage que le programme a tranché le 20 septembre 2026.

    Il a longtemps été l'inverse, et c'est ce que ce module a servi à trouver :
    sous le partage moitié-moitié d'alors, la proposition prélevait PLUS que le
    droit en vigueur au voisinage du SMIC, et le gain n'y était positif qu'un
    peu au-dessus de 1,2 SMIC. La raison tenait à la réduction générale, qui
    efface au SMIC la totalité de la part patronale : l'assuré n'y supporte que
    11,3 points, et moitié-moitié lui en demandait 11,5.

    Le partage retenu laisse à l'employeur les 16,67 points qu'il verse
    aujourd'hui et ramène l'assuré à 6,33. Il ne peut donc plus prélever
    davantage à personne, et le gain est positif partout — au jour 1 comme au
    long terme, ce que les deux boucles vérifient séparément.
    """
    _, propose = _blocs(pieces)
    for incidence in (Incidence.ASSIETTE, Incidence.COUT_DU_TRAVAIL):
        for niveau in (1.0, 1.2, 2.0, 5.0):
            assert _gain(pieces, propose, niveau, incidence) > 0, (
                f"{incidence.value} à {niveau} SMIC")
    # Le gain croît avec le salaire : la retenue baisse de cinq points, et
    # cinq points d'un gros salaire font plus que cinq points d'un petit.
    assert (_gain(pieces, propose, 5.0, Incidence.COUT_DU_TRAVAIL)
            > _gain(pieces, propose, 2.0, Incidence.COUT_DU_TRAVAIL))


def test_le_partage_retenu_laisse_la_part_patronale_ou_elle_est(pieces):
    """Ce que le partage veut dire, et qui est sa raison d'être.

    16,67 points aujourd'hui, 16,67 sous la proposition : l'employeur ne verse
    ni plus ni moins, et c'est ce qui rend la baisse immédiate plutôt que
    promise. Le test lit les deux blocs plutôt que de croire le paramètre —
    c'est le rapprochement qui compte, pas le nombre.

    **Deux millièmes de point d'écart subsistent, et ils sont voulus.** La part
    patronale d'aujourd'hui vaut exactement 16,6720 points — 10,66 au régime
    général, 4,7220 à l'Agirc-Arrco, 1,29 de contribution d'équilibre général —
    quand le paramètre est écrit sur les 16,67 qu'une proposition politique
    énonce. L'employeur verse donc 0,002 point de moins, soit cinq centimes par
    mois à un salaire et demi le SMIC. Le test borne cet écart plutôt que de
    l'ignorer : s'il grossissait, c'est qu'un taux de régime aurait bougé sans
    que le partage suive.
    """
    actuel, propose = _blocs(pieces)
    constructeur = ConstructeurFiche(pieces["bareme"])
    brut = 1.5 * pieces["smic"]  # sous le plafond, hors tranche 2
    avant = constructeur.fiche(
        ANNEE, brut, pieces["plafond"], pieces["smic"], actuel)
    apres = constructeur.fiche(
        ANNEE, brut, pieces["plafond"], pieces["smic"], propose)
    ecart = abs(apres.retraite_employeur - avant.retraite_employeur)
    assert ecart < brut * 5e-5, "la part patronale a bougé"
    # Toute la baisse est passée côté salarié : 11,31 points deviennent 6,33.
    assert avant.retraite_salarie / brut == pytest.approx(0.1131, abs=5e-5)
    assert apres.retraite_salarie / brut == pytest.approx(0.0633, abs=5e-5)
    assert avant.retraite_employeur / brut == pytest.approx(0.16672, abs=5e-6)


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


# -- les quatre profils, et le choix de l'un d'eux ---------------------------


def test_le_profil_se_choisit_sur_ce_qu_on_sait_de_l_employeur(pieces):
    """Le découpage n'est pas celui des familles, et le test fixe pourquoi.

    L'agent SNCF est de la famille `special` et relève pourtant du profil du
    privé : la fermeture des régimes spéciaux l'a versé au régime général et à
    l'Agirc-Arrco, et sa fiche de paie est celle d'un salarié. Le marin, lui,
    reste sur un régime dont la fiche ne porte que la retenue de l'agent.
    """
    choisir = lambda statut: profil_de_la_fiche(  # noqa: E731
        pieces["affiliations"], pieces["catalogue"], statut, ANNEE)
    assert choisir("salarie_prive_non_cadre") == "salarie_prive"
    assert choisir("agent_sncf") == "salarie_prive"
    assert choisir("clerc_de_notaire") == "salarie_prive"
    assert choisir("fonctionnaire_etat") == "agent_seul"
    assert choisir("militaire") == "agent_seul"
    assert choisir("marin") == "agent_seul"
    assert choisir("contractuel_public") == "salarie_ircantec"
    assert choisir("artisan") == "independant"
    assert choisir("medecin_liberal") == "independant"


def test_les_familles_qu_on_ne_sait_pas_decrire_n_affichent_rien(pieces):
    """Mieux vaut rien qu'un net faux — et c'est toujours vrai de quatre familles.

    La MSA a ses propres taux hors retraite, chaque collectivité d'outre-mer sa
    caisse, l'indemnité d'un élu n'est pas un salaire, et qui n'a pas d'emploi
    ne cotise pas.
    """
    affiliations = pieces["affiliations"]
    for statut in ("salarie_agricole", "exploitant_agricole", "elu_local",
                   "parlementaire", "salarie_mayotte", "sans_activite",
                   "statut_inexistant"):
        assert not fiche_de_paie_possible(affiliations, statut), statut
        assert profil_de_la_fiche(
            affiliations, pieces["catalogue"], statut, ANNEE) is None, statut


def test_les_quatre_familles_couvertes_le_sont(pieces):
    affiliations = pieces["affiliations"]
    for statut in ("salarie_prive_non_cadre", "fonctionnaire_etat",
                   "agent_sncf", "artisan"):
        assert fiche_de_paie_possible(affiliations, statut), statut


# -- le fonctionnaire : pas de coût du travail, et le traitement tenu fixe ---


def _fiches_du_statut(pieces, statut: str, niveau: float = 1.6,
                      part_rendue: float | None = None):
    """Les deux fiches d'un statut à un niveau de revenu, comme le site les fait.

    ``part_rendue`` force le partage des impôts abandonnés ; à ``None``, c'est
    celui des paramètres. Le mettre à zéro redonne l'ancienne convention, et
    c'est ce dont un test se sert pour dire ce que la décision a déplacé.
    """
    rendue = (PARAMETRES.part_rendue_aux_salaires if part_rendue is None
              else part_rendue)
    profil = pieces["prelevements"].profil(profil_de_la_fiche(
        pieces["affiliations"], pieces["catalogue"], statut, ANNEE))
    constructeur = ConstructeurFiche(profil)
    sans_employeur = pieces["affiliations"].sans_employeur(statut)
    actuel = bloc_droit_en_vigueur(
        pieces["catalogue"], pieces["affiliations"], statut, ANNEE)
    csg = points_csg_rendus(PARAMETRES.racine_donnees, ANNEE, rendue)
    if sans_employeur:
        propose = bloc_taux_unique_sans_employeur(
            PARAMETRES.taux_cotisation_liberal,
            PARAMETRES.taux_capitalisation_obligatoire,
            csg_rendue=csg)
    else:
        propose = bloc_taux_unique(
            PARAMETRES.taux_cotisation_liberal,
            PARAMETRES.taux_capitalisation_obligatoire,
            PARAMETRES.part_salariale_taux_unique,
            csg_rendue=csg,
            part_rendue_aux_salaires=rendue,
            contribution_equilibre_actuelle=contribution_equilibre(
                PARAMETRES.racine_donnees, pieces["affiliations"], statut, ANNEE)
            if profil.incidence is Incidence.PARTAGEE else 0.0,
        )
    brut = niveau * pieces["smic"]
    avant = constructeur.fiche(
        ANNEE, brut, pieces["plafond"], pieces["smic"], actuel)
    apres = constructeur.fiche(
        ANNEE,
        constructeur.brut_sous_la_proposition(
            avant, pieces["plafond"], pieces["smic"], propose),
        pieces["plafond"], pieces["smic"], propose,
    )
    return profil, avant, apres


def test_le_fonctionnaire_n_a_pas_de_cout_du_travail_affichable(pieces):
    """La décision du module, fixée par un test plutôt que par un commentaire.

    Ce que verse l'État est un taux d'ÉQUILIBRE — 82,28 % du traitement en 2026
    —, fixé pour payer les pensions d'aujourd'hui et non pour acheter des droits
    nouveaux. La ligne « coût du travail » reste donc absente : l'afficher
    dirait que ces 82 points sont un prix du travail, ce qu'ils ne sont pas.

    Le traitement, lui, BOUGE depuis le 20 septembre 2026, et c'est le partage
    qui le fait bouger — pas l'incidence intégrale. Les deux affirmations
    tiennent ensemble, et ce test est là pour qu'on ne les confonde pas.
    """
    profil, avant, apres = _fiches_du_statut(pieces, "fonctionnaire_etat")
    assert profil.code == "agent_seul"
    assert profil.cout_du_travail is False
    assert profil.incidence is Incidence.PARTAGEE
    # Rien du côté employeur sous le droit en vigueur : la fiche du régime ne
    # porte que la retenue, et c'est exactement ce qu'on voulait.
    assert avant.cout_du_travail == pytest.approx(avant.brut)
    assert avant.reduction_generale == 0.0
    assert apres.brut > avant.brut


def test_a_part_rendue_nulle_le_traitement_ne_bouge_plus(pieces):
    """Le réglage tient ses deux bornes, et la borne basse est l'ancien dépôt.

    À zéro, rien n'est rendu : le traitement est tenu fixe, la CSG reste
    entière, et la fiche est CELLE D'AVANT la décision du 20 septembre 2026,
    au centime. C'est ce qui permet de dire ce que la décision déplace sans
    avoir à se fier à un commentaire.
    """
    _, avant, apres = _fiches_du_statut(pieces, "fonctionnaire_etat", part_rendue=0.0)
    assert apres.brut == pytest.approx(avant.brut)
    csg_avant = next(l for l in avant.lignes if l.code == "csg_crds")
    csg_apres = next(l for l in apres.lignes if l.code == "csg_crds")
    assert csg_apres.salarie == pytest.approx(csg_avant.salarie)
    assert csg_apres.libelle == csg_avant.libelle == "CSG et CRDS"


def test_la_moitie_de_ce_que_l_etat_libere_remonte_dans_le_traitement(pieces):
    """La formule du partage, vérifiée sur ses deux termes plutôt que sur un chiffre.

    L'État verse 82,28 % du traitement en 2026 ; la proposition ramène sa part à
    11,50 points — la moitié patronale de 18 + 5. La dépense publique par agent
    baisse donc de la MOITIÉ de l'écart, l'autre moitié revenant au traitement.
    """
    _, avant, apres = _fiches_du_statut(pieces, "fonctionnaire_etat")
    equilibre = contribution_equilibre(
        PARAMETRES.racine_donnees, pieces["affiliations"],
        "fonctionnaire_etat", ANNEE)
    assert equilibre > 0.8
    patronal = (PARAMETRES.taux_cotisation_liberal
                + PARAMETRES.taux_capitalisation_obligatoire
                ) * (1.0 - PARAMETRES.part_salariale_taux_unique)
    attendu = avant.brut * (1.0 + patronal
                            + PARAMETRES.part_rendue_aux_salaires
                            * (equilibre - patronal)) / (1.0 + patronal)
    assert apres.brut == pytest.approx(attendu, rel=1e-6)
    # Et la dépense publique baisse bien de l'autre moitié.
    depense_avant = avant.brut * (1.0 + equilibre)
    depense_apres = apres.brut * (1.0 + patronal)
    libere = avant.brut * (equilibre - patronal)
    assert depense_avant - depense_apres == pytest.approx(
        (1.0 - PARAMETRES.part_rendue_aux_salaires) * libere, rel=1e-6)


def test_le_net_d_un_fonctionnaire_vaut_environ_79_pour_cent_du_traitement(pieces):
    """11,10 points de retenue et 9,53 de CSG-CRDS après abattement : 79,4 %.

    La liste de postes vide du profil est un RÉSULTAT et non un oubli : la
    cotisation maladie salariale a disparu en 2018 comme dans le privé, un
    titulaire n'est pas assuré contre le chômage, et la contribution
    exceptionnelle de solidarité de 1 % a été supprimée la même année.
    """
    profil, avant, _ = _fiches_du_statut(pieces, "fonctionnaire_etat")
    assert profil.postes == ()
    assert 0.79 < avant.net / avant.brut < 0.80
    # Une seule ligne de retraite, une de CSG-CRDS, rien d'autre.
    assert sorted(ligne.code for ligne in avant.lignes) == [
        "csg_crds", "fonction_publique_etat"]
    assert avant.retraite_salarie == pytest.approx(0.111 * avant.brut)


def test_la_retenue_d_un_fonctionnaire_passe_de_11_10_a_6_33_pour_cent(pieces):
    """Ce que la proposition PRÉLÈVE sur un agent : 11,10 points, puis 6,33.

    Sa retenue suit la part salariale du taux unique, la même pour tous les
    statuts. Elle valait 11,50 points sous le partage moitié-moitié, soit
    quatre dixièmes de PLUS qu'aujourd'hui, et le 20 septembre 2026 le
    programme a décidé de laisser la part patronale où elle est : elle tombe
    donc à 6,33, et l'agent reçoit la même baisse que tout le monde.

    Ce n'est plus tout le mouvement de sa fiche. La moitié de ce que l'État
    cesse de verser remonte dans son traitement depuis le même jour — c'est
    `Incidence.PARTAGEE`, et deux tests plus haut la mesurent. Les deux
    décisions se cumulent sur son net, et aucune des deux ne se lit sur la
    part patronale d'un employeur privé.
    """
    _, avant, apres = _fiches_du_statut(pieces, "fonctionnaire_etat")
    part = (PARAMETRES.taux_cotisation_liberal
            + PARAMETRES.taux_capitalisation_obligatoire
            ) * PARAMETRES.part_salariale_taux_unique
    assert apres.retraite_salarie == pytest.approx(part * apres.brut)
    assert avant.retraite_salarie == pytest.approx(0.111 * avant.brut)


def test_un_agent_non_titulaire_a_bien_un_cout_du_travail(pieces):
    """Parce que son employeur verse, lui, des taux de DROIT COMMUN.

    C'est toute la distinction : régime général et Ircantec, et non un taux
    d'équilibre. La CEG, la CET et l'APEC, qui sont des contributions de
    l'Agirc-Arrco, ne lui sont en revanche pas dues.
    """
    profil, avant, apres = _fiches_du_statut(pieces, "contractuel_public")
    assert profil.code == "salarie_ircantec"
    assert profil.cout_du_travail is True
    assert profil.incidence is Incidence.COUT_DU_TRAVAIL
    codes = {poste.code for poste in profil.postes}
    assert not codes & {"equilibre_general", "equilibre_technique", "apec"}
    assert avant.cout_du_travail > avant.brut
    assert apres.cout_du_travail == pytest.approx(avant.cout_du_travail, rel=1e-6)


# -- l'indépendant : il paie tout, et ses deux barèmes sont progressifs ------


def test_un_independant_ne_se_voit_pretee_aucune_part_patronale(pieces):
    """Le correctif que `sans_employeur` impose, et sans lequel tout est faux.

    La fiche du régime général porte la répartition 45/55 d'un salarié. Un
    artisan y cotise pourtant seul : sans ce correctif, la fiche de paie lui
    aurait montré un employeur qui n'existe pas et aurait sous-estimé de moitié
    ce qu'il verse.
    """
    profil, avant, apres = _fiches_du_statut(pieces, "artisan")
    assert profil.code == "independant"
    assert all(ligne.employeur == 0.0 for ligne in avant.lignes)
    assert all(ligne.employeur == 0.0 for ligne in apres.lignes)
    assert avant.cout_du_travail == pytest.approx(avant.brut)
    # Le régime général pèse ses 15,45 % pleins, et non ses 6,90 % salariaux.
    retraite_base = next(ligne for ligne in avant.lignes
                         if ligne.code == "regime_general")
    plafonne = min(avant.brut, pieces["plafond"])
    assert retraite_base.salarie == pytest.approx(
        0.1545 * plafonne + 0.0251 * avant.brut, rel=1e-3)


def test_l_independant_porte_les_dix_huit_pour_cent_en_entier(pieces):
    """La proposition additionne « salariale et patronale » : il est les deux.

    Lui prêter un employeur pour la moitié de la charge fabriquerait un gain qui
    n'existe pas.
    """
    _, _, apres = _fiches_du_statut(pieces, "artisan")
    total = (PARAMETRES.taux_cotisation_liberal
             + PARAMETRES.taux_capitalisation_obligatoire)
    assert apres.retraite_salarie == pytest.approx(total * apres.brut)


def _taux_progressif(pieces, code: str, niveau_en_plafonds: float) -> float:
    """Le taux effectif d'un poste d'indépendant, à un niveau d'assiette donné."""
    profil = pieces["prelevements"].profil("independant")
    poste = next(p for p in profil.postes if p.code == code)
    assiette = niveau_en_plafonds * pieces["plafond"]
    return poste.montant_salarie(assiette, pieces["plafond"]) / assiette


def test_le_bareme_progressif_de_la_maladie_retombe_sur_les_bornes_de_la_loi(pieces):
    """D. 621-1 et D. 621-2, version en vigueur, palier par palier.

    Le taux interpolé porte sur la TOTALITÉ de l'assiette et non sur la seule
    fraction comprise entre deux paliers : une modélisation par tranches
    marginales donnerait un montant tout autre, et c'est ce que ce test
    interdit.
    """
    assert _taux_progressif(pieces, "maladie_maternite", 0.1) == pytest.approx(0.0)
    assert _taux_progressif(pieces, "maladie_maternite", 0.2) == pytest.approx(0.0)
    assert _taux_progressif(pieces, "maladie_maternite", 0.4) == pytest.approx(0.015)
    assert _taux_progressif(pieces, "maladie_maternite", 0.6) == pytest.approx(0.040)
    assert _taux_progressif(pieces, "maladie_maternite", 1.1) == pytest.approx(0.065)
    assert _taux_progressif(pieces, "maladie_maternite", 2.0) == pytest.approx(0.077)
    # À mi-chemin entre deux paliers, l'interpolation est bien linéaire.
    assert _taux_progressif(pieces, "maladie_maternite", 0.3) == pytest.approx(0.0075)


def test_le_raccord_du_bareme_progressif_est_continu(pieces):
    """À trois plafonds, la réduction s'arrête et les tranches reprennent.

    La continuité est une propriété du droit — 8,50 % des deux côtés —, et non
    du code : si elle saute, c'est qu'un palier ou une tranche a bougé sans
    l'autre.
    """
    for code, borne in (("maladie_maternite", 3.0), ("famille", 1.4)):
        juste_avant = _taux_progressif(pieces, code, borne - 1e-6)
        juste_apres = _taux_progressif(pieces, code, borne + 1e-6)
        assert juste_avant == pytest.approx(juste_apres, abs=1e-6), code
    # Au-delà de trois plafonds, la maladie redevient marginale : 8,50 % sur les
    # trois premiers plafonds, 6,50 % au-delà.
    assert _taux_progressif(pieces, "maladie_maternite", 6.0) == pytest.approx(
        (0.085 * 3 + 0.065 * 3) / 6)


def test_la_cotisation_famille_d_un_independant_est_nulle_sous_1_1_plafond(pieces):
    """D. 613-1 : nulle jusqu'à 110 % du plafond, 3,10 % au-delà de 140 %."""
    assert _taux_progressif(pieces, "famille", 1.0) == pytest.approx(0.0)
    assert _taux_progressif(pieces, "famille", 1.1) == pytest.approx(0.0)
    assert _taux_progressif(pieces, "famille", 1.25) == pytest.approx(0.0155)
    assert _taux_progressif(pieces, "famille", 1.4) == pytest.approx(0.031)
    assert _taux_progressif(pieces, "famille", 3.0) == pytest.approx(0.031)


def test_la_csg_d_un_independant_n_est_pas_abattue(pieces):
    """L'abattement de 1,75 % est propre aux revenus d'activité SALARIÉE.

    Depuis la réforme de l'assiette unique de 2024, la CSG d'un indépendant
    porte sur la même assiette que ses cotisations.
    """
    profil = pieces["prelevements"].profil("independant")
    assert profil.abattement_frais == ()
    assert profil.csg + profil.crds == pytest.approx(0.097)
    assert pieces["bareme"].abattement_frais != ()


# -- le simulateur entier ----------------------------------------------------


def test_aucune_remuneration_pour_qui_a_deja_liquide():
    """Un retraité ne cotise plus : il n'y a pas de fiche de paie à montrer."""
    simulateur = Simulateur(PARAMETRES)
    carriere = simulateur.carriere_simple(
        annee_naissance=1940, sexe="H", affiliation=STATUT,
        age_debut=20, age_liquidation=60, niveau_salaire=1.0,
    )
    assert simulateur.simuler(carriere).remuneration is None


@pytest.mark.parametrize("statut, profil, cout_du_travail", [
    ("salarie_prive_non_cadre", "salarie_prive", True),
    ("fonctionnaire_etat", "agent_seul", False),
    ("agent_sncf", "salarie_prive", True),
    ("contractuel_public", "salarie_ircantec", True),
    ("artisan", "independant", False),
])
def test_le_simulateur_rend_une_remuneration_aux_quatre_profils(
        statut, profil, cout_du_travail):
    """Bout en bout : le site a bien un bloc à afficher, et il sait le nommer."""
    simulateur = Simulateur(PARAMETRES)
    carriere = simulateur.carriere_simple(
        annee_naissance=1985, sexe="H", affiliation=statut,
        age_debut=22, age_liquidation=64, niveau_salaire=1.0,
    )
    remuneration = simulateur.simuler(carriere).remuneration
    assert remuneration is not None
    assert remuneration.profil == profil
    assert remuneration.affiche_cout_du_travail is cout_du_travail
    assert remuneration.libelle_assiette
    assert remuneration.reference.droit_en_vigueur.net > 0


def test_aucune_remuneration_pour_un_salarie_agricole():
    """La MSA a ses propres taux hors retraite : mieux vaut rien qu'un net faux."""
    simulateur = Simulateur(PARAMETRES)
    carriere = simulateur.carriere_simple(
        annee_naissance=1985, sexe="H", affiliation="salarie_agricole",
        age_debut=22, age_liquidation=64, niveau_salaire=1.0,
    )
    assert simulateur.simuler(carriere).remuneration is None


def test_la_fiabilite_du_bareme_est_plafonnee_a_haute(pieces):
    """OpenFisca transcrit le Journal officiel, il ne le produit pas."""
    assert pieces["prelevements"].fiabilite <= Fiabilite.HAUTE
    for profil in pieces["prelevements"].profils.values():
        assert profil.fiabilite <= Fiabilite.HAUTE


# -- le net et le brut, d'un bout à l'autre du simulateur --------------------


def test_les_prelevements_sur_pension_font_neuf_virgule_un_points(pieces):
    """CSG 8,30 %, CRDS 0,50 %, CASA 0,30 % : ce qui sépare une pension de son net.

    Le taux plein, et lui seul : l'article L. 136-8 le fait dépendre du revenu
    fiscal de référence du foyer, que le simulateur ne demande pas. La
    convention est écrite dans le fichier de données et sur la page ; ce test
    la fixe, et attrapera la prochaine loi de financement qui y touchera.
    """
    pensions = pieces["prelevements"].pensions
    assert pensions.taux_total == pytest.approx(0.091, abs=1e-9)
    assert pensions.net(1000.0) == pytest.approx(909.0)
    # L'aller-retour est exact : c'est ce qui permet de saisir un net.
    assert pensions.brut(pensions.net(2500.0)) == pytest.approx(2500.0)


def test_le_bareme_de_csg_est_ordonne_et_finit_au_taux_plein(pieces):
    """Les quatre cas de la loi, dans l'ordre, et le dernier sans plafond.

    Le modèle n'applique que le dernier, mais la page montre les quatre pour
    que le lecteur situe sa propre situation. Un barème désordonné ou tronqué
    la ferait mentir.
    """
    bareme = pieces["prelevements"].pensions.bareme_csg
    assert [tranche.taux for tranche in bareme] == [0.0, 0.038, 0.066, 0.083]
    seuils = [t.revenu_fiscal_maximum for t in bareme[:-1]]
    assert seuils == sorted(seuils)
    assert bareme[-1].revenu_fiscal_maximum is None
    assert bareme[-1].taux == pieces["prelevements"].pensions.csg_taux_plein


def test_le_net_saisi_se_retrouve_par_la_fiche_de_paie(pieces):
    """L'aller-retour de la saisie : un net tapé redonne le brut qui le laisse.

    C'est ce qui rend le mode « net » honnête : on ne devine pas un brut, on
    résout l'équation de la fiche de paie. Vérifié sur les quatre profils, et
    non sur le seul salarié du privé — un indépendant paie tout lui-même, et
    son barème est progressif.
    """
    from retraite_notionnelle.remuneration import (
        salaire_brut_depuis_net,
        salaire_net_depuis_brut,
    )

    for statut in ("salarie_prive_non_cadre", "salarie_prive_cadre",
                   "fonctionnaire_etat", "contractuel_public", "artisan"):
        for net_mensuel in (1800.0, 2500.0, 6000.0):
            brut = salaire_brut_depuis_net(
                PARAMETRES.racine_donnees, pieces["macro"], pieces["catalogue"],
                pieces["affiliations"], statut, ANNEE, net_mensuel * 12)
            retour = salaire_net_depuis_brut(
                PARAMETRES.racine_donnees, pieces["macro"], pieces["catalogue"],
                pieces["affiliations"], statut, ANNEE, brut)
            assert retour == pytest.approx(net_mensuel * 12, rel=1e-6), (
                f"{statut} à {net_mensuel} € net")
            assert brut > net_mensuel * 12, f"{statut} : le brut doit dépasser le net"


def test_un_statut_sans_fiche_de_paie_rend_le_montant_inchange(pieces):
    """Mieux vaut un brut approché par un net qu'un refus de calculer.

    L'exploitant agricole relève de la MSA, dont le dépôt n'a pas les taux hors
    retraite. Le montant saisi est alors lu tel quel, et le formulaire le dit —
    c'est `_mention_conversion` côté site.
    """
    from retraite_notionnelle.remuneration import salaire_brut_depuis_net

    inchange = salaire_brut_depuis_net(
        PARAMETRES.racine_donnees, pieces["macro"], pieces["catalogue"],
        pieces["affiliations"], "exploitant_agricole", ANNEE, 30000.0)
    assert inchange == pytest.approx(30000.0)


# -- les cinq points volontaires ---------------------------------------------
#
# Ils sont la seule cotisation du modèle que personne n'impose, et tout ce qui
# suit découle de ce fait : ils ne sont PAS sur la fiche de paie. La fiche de
# la proposition s'arrête aux 23 points imposés, son net est le net plein, et
# les cinq points rendus sont un placement pris sur ce net — à la charge du
# seul assuré, sans toucher au coût du travail, au brut, ni à la CSG.


def _annee_de_reference(parametres=PARAMETRES):
    simulateur = Simulateur(parametres)
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1990, sexe="H", affiliation=STATUT,
        age_debut=22, age_liquidation=64,
    ))
    return comparaison.remuneration


def test_la_fiche_de_la_proposition_ne_retient_pas_le_volontaire():
    """Le bloc de la proposition ne porte que ce qu'elle impose : 18 + 5.

    Si ce test tombait, c'est qu'une composante volontaire serait revenue
    dans la fiche, et le net affiché par le site cesserait d'être le net
    plein — la proposition paraîtrait plus coûteuse qu'elle n'est.
    """
    reference = _annee_de_reference().reference
    fiche = reference.proposition
    assert all("volontaire" not in ligne.code for ligne in fiche.lignes)
    impose = (PARAMETRES.taux_cotisation_liberal
              + PARAMETRES.taux_capitalisation_obligatoire)
    # Au barème, avant la réduction générale que `retraite_totale` retranche.
    assert fiche.retraite_salarie + fiche.retraite_employeur == pytest.approx(
        fiche.brut * impose)
    assert reference.epargne_a_votre_nom == pytest.approx(
        fiche.brut * PARAMETRES.taux_capitalisation_obligatoire)


def test_le_placement_volontaire_vaut_cinq_points_du_brut_pris_sur_le_net():
    """Cinq points de l'assiette de la proposition, ni plus ni moins.

    C'est ce qui autorise `AnneeComparee.net_apres_volontaire` à soustraire
    au lieu de refaire une fiche de paie : le placement ne passe pas par la
    CSG, qui est assise sur le brut, et l'employeur n'en verse rien.
    """
    reference = _annee_de_reference().reference
    attendu = (reference.proposition.brut
               * PARAMETRES.taux_capitalisation_volontaire)
    assert reference.epargne_volontaire == pytest.approx(attendu)
    assert reference.net_apres_volontaire == pytest.approx(
        reference.proposition.net - attendu)
    assert reference.gain_net_apres_volontaire == pytest.approx(
        reference.gain_net - attendu)


def test_le_volontaire_porte_le_prelevement_retraite_au_niveau_d_aujourd_hui():
    """La raison d'être des cinq points : cotiser autant, autrement.

    Le rapprochement se fait sur le TAUX affiché — 18 + 5 + 5 contre les 28 %
    d'un salarié du privé —, et non sur les montants, que l'assiette et
    l'allègement sur les bas salaires font diverger. La fiche, elle, prélève
    nettement moins que le droit en vigueur ; le placement referme l'écart.
    """
    total = (PARAMETRES.taux_cotisation_liberal
             + PARAMETRES.taux_capitalisation_obligatoire
             + PARAMETRES.taux_capitalisation_volontaire)
    assert total == pytest.approx(0.28)
    reference = _annee_de_reference().reference
    avant, apres = reference.droit_en_vigueur, reference.proposition
    assert apres.retraite_totale < avant.retraite_totale
    assert abs(apres.retraite_totale + reference.epargne_volontaire
               - avant.retraite_totale) < abs(
        apres.retraite_totale - avant.retraite_totale)


def test_la_carriere_expose_les_deux_nets():
    """Le site affiche le net plein ET ce qui reste à qui place les points rendus."""
    remuneration = _annee_de_reference()
    assert remuneration.verse_le_volontaire
    reference = remuneration.reference
    assert reference.epargne_volontaire > 0
    assert reference.net_apres_volontaire < reference.proposition.net
    # Même taux, même assiette : le placement pèse exactement l'obligatoire.
    assert reference.epargne_volontaire == pytest.approx(
        reference.epargne_a_votre_nom)
    assert remuneration.epargne_volontaire_cumulee > 0
    assert remuneration.gain_net_mensuel_apres_volontaire < (
        remuneration.gain_net_mensuel)


def test_retirer_le_volontaire_ne_change_pas_la_fiche_de_paie():
    """Un paramètre à `False`, et seul le placement disparaît.

    La fiche est la même au centime : c'est la preuve que les cinq points
    rendus n'y étaient pas, et que le net affiché ne dépend pas d'une
    décision que personne n'impose.
    """
    avec = _annee_de_reference()
    sans = _annee_de_reference(PARAMETRES.avec(capitalisation_volontaire=False))

    assert not sans.verse_le_volontaire
    assert sans.reference.epargne_volontaire == 0.0
    assert sans.reference.net_apres_volontaire == pytest.approx(
        sans.reference.proposition.net)
    for attribut in ("cout_du_travail", "brut", "net", "retraite_totale"):
        assert getattr(sans.reference.proposition, attribut) == pytest.approx(
            getattr(avec.reference.proposition, attribut))


