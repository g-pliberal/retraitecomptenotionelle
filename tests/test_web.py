"""Tests du contenu du site.

Le site tourne entièrement dans le navigateur ; ce qu'il affiche est produit ici
par :mod:`retraite_notionnelle.web.pages`, qui ne dépend que de la bibliothèque
standard et sert de référence au portage JavaScript.
"""

from __future__ import annotations

import html
import re
from urllib.parse import parse_qsl

import pytest

from retraite_notionnelle.web import gabarit as g
from retraite_notionnelle.web.gabarit import (
    Cellule,
    euros,
    franciser,
    pourcentage,
    tableau,
)
from retraite_notionnelle.donnees.chargement import DonneeInsuffisante
from retraite_notionnelle.web.pages import (
    AGES_REFERENCE,
    DECIMALES_DIVISEUR,
    DECIMALES_FACTEUR,
    DECIMALES_MULTIPLE,
    ANNEE_MAXIMALE,
    ANNEE_MINIMALE,
    ENFANTS_MAXIMUM,
    INDEXATIONS,
    LISSAGE_MAXIMUM,
    METIERS_MAXIMUM,
    PAS_MULTIPLE,
    PROFILS,
    PROJECTIONS,
    TABLES,
    Contexte,
    ErreurSaisie,
    Saisie,
    rendre,
    statuts,
)


@pytest.fixture(scope="module")
def contexte() -> Contexte:
    return Contexte()


def _echelle():
    """L'échelle des salaires du jeu de paramètres par défaut.

    ``Saisie.parcours`` en a besoin depuis que le formulaire accepte des euros :
    convertir « 2 500 € par mois » en multiple suppose le salaire moyen.
    """
    return Contexte().echelle(Saisie())


@pytest.fixture(scope="module")
def page(contexte):
    """Rend une page entière, comme le fait ``index.html`` dans le navigateur.

    Le site n'assemble jamais autre chose : l'en-tête, le corps rendu, le pied.
    """
    def rendu(chemin: str = "/", **parametres: object) -> str:
        _, corps = rendre(contexte, chemin,
                          {nom: str(valeur) for nom, valeur in parametres.items()})
        return g.entete(chemin) + corps + g.pied()

    return rendu


# -- pages -------------------------------------------------------------------


@pytest.mark.parametrize("chemin", ["/", "/cas-types", "/methode", "/donnees"])
def test_les_pages_repondent(page, chemin):
    texte = page(chemin)
    assert "Retraite à comptes notionnels" in texte


def test_accueil_sans_parametres_ne_calcule_rien(page):
    """Une visite nue montre le formulaire, pas des résultats surgis de nulle part."""
    texte = page("/")
    assert "Simuler une carrière" in texte
    assert "Résultats" not in texte


def test_simulation_affiche_les_trois_scenarios(page):
    texte = page("/", naissance=1960, statut="agent_sncf",
                 debut=20, liquidation=52)
    for attendu in ("Système actuel", "rétroactifs depuis 1941",
                    "à compter de 2026", "Résultats"):
        assert attendu in texte


def test_la_saisie_est_reinjectee_dans_le_formulaire(page):
    """L'adresse porte les paramètres : la page doit être rechargeable telle quelle."""
    texte = page("/", naissance=1955, statut="mineur",
                 debut=18, liquidation=55)
    assert 'value="1955"' in texte
    assert '<option value="mineur" selected>' in texte


def test_saisie_invalide_affiche_un_message_et_pas_de_trace(page):
    texte = page("/", naissance=1700)
    assert "Saisie refusée" in texte
    assert "Traceback" not in texte


def test_carriere_impossible_est_signalee_sans_planter(page):
    texte = page("/", naissance=1990, statut="salarie_prive_non_cadre",
                 debut=30, liquidation=45)
    assert "Traceback" not in texte


def test_la_decomposition_par_regle_d_indexation_est_presente(page):
    """Le point le plus contre-intuitif du modèle doit être exposé, pas caché."""
    texte = page("/", naissance=1960, statut="salarie_prive_non_cadre",
                 debut=20, liquidation=62)
    assert "D'où vient l'écart" in texte
    assert "Triple lock inversé, tout en nominal" in texte
    assert texte.count("Rendement cumulé") >= 1


def test_pas_de_decomposition_si_l_indexation_est_deja_choisie(page):
    texte = page("/", naissance=1960, statut="salarie_prive_non_cadre",
                 debut=20, liquidation=62, indexation="prix")
    assert "D'où vient l'écart" not in texte


# -- résultats bruts ---------------------------------------------------------
#
# Ce que la page publie sous « Les résultats complets en JSON », et que le
# portage JavaScript doit retrouver à l'identique.


def test_statuts_proposes(contexte):
    donnees = statuts(contexte)
    codes = {entree["code"] for entree in donnees}
    assert "salarie_prive_non_cadre" in codes
    assert all(entree["libelle"] for entree in donnees)


def test_simulation_en_dictionnaire(contexte):
    saisie = Saisie.depuis_requete(
        {"naissance": "1975", "statut": "fonctionnaire_etat",
         "debut": "23", "liquidation": "64", "primes": "0.2"}
    )
    donnees = contexte.simuler(saisie).dictionnaire()
    assert donnees["assure"]["annee_naissance"] == 1975
    scenarios = donnees["scenarios"]
    assert scenarios["actuel"]["pension_annuelle"] > 0
    assert scenarios["notionnel_retroactif"]["pension_annuelle"] > 0
    assert donnees["fiabilite"]


def test_statut_inconnu_est_refuse(contexte):
    """La saisie est bien formée : c'est le catalogue des régimes qui tranche."""
    saisie = Saisie.depuis_requete(
        {"naissance": "1975", "statut": "astronaute",
         "debut": "23", "liquidation": "64"}
    )
    with pytest.raises(ErreurSaisie):
        contexte.simuler(saisie)


# -- saisie ------------------------------------------------------------------


def test_saisie_par_defaut_est_valide():
    Saisie().verifier()


@pytest.mark.parametrize("champs", [
    {"naissance": "1700"},
    {"debut": "12"},
    {"liquidation": "90"},
    {"naissance": "1980", "debut": "30", "liquidation": "25"},
    {"salaire": "50"},
])
def test_saisies_refusees(champs):
    with pytest.raises(ErreurSaisie):
        Saisie.depuis_requete(champs)


@pytest.mark.parametrize("champ", ["bascule", "euros"])
@pytest.mark.parametrize("valeur", ["1800", "9999", "-5", "0"])
def test_les_annees_hors_bornes_sont_refusees(champ, valeur):
    """Une adresse forgée à la main ne doit pas franchir les bornes du champ.

    Elles n'existaient que sur le formulaire, donc opposables au navigateur
    seulement. « ?euros=9999 » traversait toute la chaîne sans erreur et
    faisait afficher des pensions à soixante chiffres, l'année des euros
    servant d'exposant à l'inflation cumulée.
    """
    with pytest.raises(ErreurSaisie):
        Saisie.depuis_requete({champ: valeur})


@pytest.mark.parametrize("champ", ["bascule", "euros"])
def test_les_annees_aux_bornes_sont_acceptees(champ):
    for valeur in (ANNEE_MINIMALE, ANNEE_MAXIMALE):
        assert getattr(
            Saisie.depuis_requete({champ: str(valeur)}), champ
        ) == valeur


def test_le_nombre_d_enfants_reste_borne():
    """Les majorations du scénario 1 en dépendent : le champ n'était borné que
    dans le formulaire, et « ?enfants=999 » gonflait la pension de référence."""
    assert Saisie.depuis_requete(
        {"enfants": str(ENFANTS_MAXIMUM)}
    ).enfants == ENFANTS_MAXIMUM
    for refuse in ("-1", str(ENFANTS_MAXIMUM + 1), "999"):
        with pytest.raises(ErreurSaisie):
            Saisie.depuis_requete({"enfants": refuse})


def test_toute_borne_du_formulaire_est_opposable_hors_du_navigateur(contexte):
    """Aucun champ numérique ne doit être borné dans le seul HTML.

    Le formulaire porte des attributs « min » et « max » ; le navigateur les
    respecte, une adresse partagée non. Ce test relit le formulaire rendu et
    vérifie que chaque borne déclarée est bien refusée par le modèle.
    """
    formulaire = rendre(contexte, "/", {})[1]
    champs = re.findall(
        r'<input type="number" id="([a-z_0-9]+)" name="[^"]*" value="[^"]*"'
        r'(?: min="(-?[0-9.]+)")?(?: max="(-?[0-9.]+)")?',
        formulaire,
    )
    assert champs, "le formulaire ne déclare plus aucun champ numérique"
    for nom, minimum, maximum in champs:
        for borne, pas in ((minimum, -1), (maximum, +1)):
            if not borne:
                continue
            dehors = float(borne) + pas
            valeur = str(int(dehors)) if float(borne).is_integer() else str(dehors)
            with pytest.raises(ErreurSaisie, match=r"."):
                Saisie.depuis_requete({nom: valeur})


def test_valeur_non_numerique_est_refusee_proprement():
    with pytest.raises(ErreurSaisie):
        Saisie.depuis_requete({"naissance": "mille-neuf-cent"})


def test_virgule_decimale_acceptee():
    assert Saisie.depuis_requete({"salaire": "1,5"}).salaire == 1.5


def test_la_fenetre_de_lissage_se_saisit_librement_mais_reste_bornee():
    """Fenêtre libre, et non plus un choix entre trois valeurs.

    La borne haute est un garde-fou de sens, pas une limite du moteur : au-delà
    d'une trentaine d'années la moyenne couvre presque toute une carrière.
    """
    for annees in (1, 2, 7, 17, LISSAGE_MAXIMUM):
        assert Saisie.depuis_requete({"lissage": str(annees)}).lissage == annees
    assert Saisie.depuis_requete({}).lissage == 1

    for refusee in ("0", "-3", str(LISSAGE_MAXIMUM + 1)):
        with pytest.raises(ErreurSaisie):
            Saisie.depuis_requete({"lissage": refusee})
    with pytest.raises(ErreurSaisie):
        Saisie.depuis_requete({"lissage": "au jugé"})


def test_option_inconnue_retombe_sur_le_defaut():
    saisie = Saisie.depuis_requete({"indexation": "au_doigt_mouille"})
    assert saisie.indexation == "masse_salariale"


def test_interruptions_analysees():
    saisie = Saisie(interruptions="1995:1997:education_enfant, 2001:2001:maladie")
    plages = saisie.interruptions_analysees()
    assert plages[1995] == "education_enfant"
    assert plages[1997] == "education_enfant"
    assert plages[2001] == "maladie"
    assert 1998 not in plages


def test_interruption_mal_formee_est_refusee():
    with pytest.raises(ErreurSaisie):
        Saisie(interruptions="1995-1997").interruptions_analysees()


# -- l'unité des revenus saisis ----------------------------------------------


def test_le_formulaire_vierge_demande_des_euros():
    """C'est la question qui revenait : personne ne connaît son salaire en ratio."""
    saisie = Saisie.depuis_requete({})
    assert saisie.unite_revenu == "euros_mois"
    assert saisie.revenu_en_euros is True


def test_un_salaire_mensuel_devient_un_multiple():
    """2 500 € par mois contre 40 000 € annuels d'ancrage, à l'échelle de 2026."""
    saisie = Saisie.depuis_requete({"unite_revenu": "euros_mois", "salaire": "2500"})
    echelle = _echelle()
    assert saisie.niveaux(echelle) == pytest.approx([2500 * 12 / echelle.moyen])
    assert saisie.parcours(echelle)[0].niveau_salaire == pytest.approx(
        saisie.niveaux(echelle)[0]
    )


def test_le_multiple_reste_disponible():
    saisie = Saisie.depuis_requete({"unite_revenu": "moyen", "salaire": "1.4"})
    assert saisie.revenu_en_euros is False
    assert saisie.parcours(_echelle())[0].niveau_salaire == 1.4


def test_une_adresse_d_avant_les_euros_reste_lue_en_multiples():
    """Un « salaire » nu vaut un multiple : le lire en euros en ferait un euro."""
    saisie = Saisie.depuis_requete({"naissance": "1975", "salaire": "1.4"})
    assert saisie.unite_revenu == "moyen"
    assert saisie.parcours(_echelle())[0].niveau_salaire == 1.4


def test_l_unite_s_ecrit_toujours_dans_l_adresse():
    """C'est ce qui distingue une adresse neuve d'une adresse d'avant les euros."""
    for unite in ("euros_mois", "moyen"):
        requete = Saisie.depuis_requete({"unite_revenu": unite, "salaire": "1"}).requete()
        assert f"unite_revenu={unite}" in requete


def test_un_salaire_hors_bornes_est_refuse_en_euros():
    """Le refus doit dire quoi corriger, donc redire les bornes en euros."""
    saisie = Saisie.depuis_requete({"unite_revenu": "euros_mois", "salaire": "200"})
    with pytest.raises(ErreurSaisie, match="bruts par mois"):
        saisie.parcours(_echelle())


def test_un_salaire_negatif_ou_nul_est_refuse():
    for montant in ("0", "-1500"):
        with pytest.raises(ErreurSaisie):
            Saisie.depuis_requete({"unite_revenu": "euros_mois", "salaire": montant})


def test_l_unite_vaut_pour_tous_les_metiers():
    echelle = _echelle()
    saisie = Saisie.depuis_requete({
        "unite_revenu": "euros_mois", "salaire": "2500",
        "metier2_debut": "40", "metier2_statut": "artisan",
        "metier2_salaire": "5000",
    })
    premier, second = saisie.niveaux(echelle)
    assert second == pytest.approx(2 * premier)


def _lien_de_bascule(contexte, parametres):
    """L'adresse que porte le lien « saisir plutôt … », lue comme une requête."""
    corps = rendre(contexte, "/", parametres)[1]
    lien = re.search(r'<a href="#/\?([^"]*)">([^<]*)</a></p>', corps)
    assert lien, "le formulaire ne porte plus de lien de bascule d'unité"
    return dict(parse_qsl(html.unescape(lien.group(1)))), html.unescape(lien.group(2))


def test_la_bascule_d_unite_convertit_les_montants(contexte):
    """Le piège que ce lien existe pour éviter.

    Un menu HTML ne convertit rien : basculer l'unité sans retoucher le nombre
    aurait fait lire « 3 500 » comme 3 500 fois le salaire moyen, et la page
    aurait refusé la saisie au lieu de la traduire. Le lien, lui, porte les
    montants déjà convertis.
    """
    suite, libelle = _lien_de_bascule(contexte, {"naissance": "1975"})
    assert libelle == "Saisir plutôt un multiple du salaire moyen"
    assert suite["unite_revenu"] == "moyen"
    # 3 500 € par mois, à l'échelle d'un salaire moyen de 3 475 € : environ 1.
    assert float(suite["salaire"]) == pytest.approx(1.0, abs=0.05)
    # Et la page qui suit ce lien calcule, au lieu de refuser.
    corps = rendre(contexte, "/", suite)[1]
    assert "Saisie refusée" not in corps


def test_la_bascule_revient_au_meme_revenu(contexte):
    """Aller et retour : de combien le revenu décrit peut-il bouger ?

    Pas de zéro : le multiple s'écrit au millième, et un millième de salaire
    moyen vaut environ trois euros cinquante par mois. L'écart est donc borné
    par un demi-pas, plus l'arrondi à l'euro — et cette borne est CALCULÉE
    depuis le pas du champ, pour qu'elle suive si le pas change un jour. Le
    balayage porte sur tout le domaine accepté : sur trois valeurs choisies, un
    aller-retour semble exact alors qu'il ne l'est pas.
    """
    echelle = contexte.echelle(Saisie())
    borne = echelle.mensuel(PAS_MULTIPLE) / 2 + 1

    def aller_retour(euros: int) -> int:
        return round(echelle.mensuel(round(echelle.niveau(euros), DECIMALES_MULTIPLE)))

    plancher, plafond = round(echelle.mensuel(0.1)), round(echelle.mensuel(10))
    pire = max(abs(aller_retour(euros) - euros)
               for euros in range(plancher, plafond + 1))
    assert pire <= borne, f"{pire} € d'écart, au-delà des {borne:.2f} € admis"
    # Et l'ordre de grandeur, pour que la borne ne se relâche pas en silence.
    assert pire == 2


def test_la_bascule_ne_fait_jamais_sortir_des_bornes(contexte):
    """Un revenu accepté doit le rester une fois converti.

    Sinon le lien mènerait à une page qui refuse ce qu'elle affichait juste
    avant — l'arrondi peut faire franchir 0,1 ou 10 à un revenu qui les frôle.
    """
    echelle = contexte.echelle(Saisie())
    for euros in range(round(echelle.mensuel(0.1)), round(echelle.mensuel(10)) + 1):
        multiple = round(echelle.niveau(euros), DECIMALES_MULTIPLE)
        assert 0.1 <= multiple <= 10, f"{euros} € donne {multiple}"
    for millieme in range(100, 10001):
        euros = round(echelle.mensuel(millieme / 1000))
        assert 0.1 <= echelle.niveau(euros) <= 10, f"{millieme / 1000} donne {euros} €"


def test_les_bornes_annoncees_par_le_refus_sont_acceptees(contexte):
    """Un message d'erreur ne doit pas nommer un montant qu'il refuserait.

    Il dit « de 348 à 34 754 € » : les deux valeurs sont arrondies, et un
    arrondi du mauvais côté nommerait une borne hors bornes.
    """
    echelle = contexte.echelle(Saisie())
    for borne in (round(echelle.mensuel(0.1)), round(echelle.mensuel(10))):
        saisie = Saisie.depuis_requete({
            "unite_revenu": "euros_mois", "salaire": str(borne),
        })
        saisie.parcours(echelle)  # ne doit pas lever


def test_la_bascule_convertit_tous_les_metiers(contexte):
    suite, _ = _lien_de_bascule(contexte, {
        "naissance": "1975", "unite_revenu": "euros_mois", "salaire": "2900",
        "metier2_debut": "40", "metier2_statut": "artisan",
        "metier2_salaire": "5800",
    })
    assert float(suite["metier2_salaire"]) == pytest.approx(
        2 * float(suite["salaire"]), rel=0.01
    )


def test_les_valeurs_du_lien_tombent_sur_le_pas_des_champs(contexte):
    """Un navigateur refuse de soumettre un nombre qui rate le pas déclaré.

    Le lien écrit des valeurs arrondies ; si le champ annonçait un pas plus
    grossier, la page d'arrivée serait impossible à valider.
    """
    for parametres in ({"naissance": "1975"},
                       {"naissance": "1975", "unite_revenu": "moyen", "salaire": "1.2"}):
        suite, _ = _lien_de_bascule(contexte, parametres)
        corps = rendre(contexte, "/", suite)[1]
        champ = re.search(r'id="salaire"[^>]*value="([^"]*)"[^>]*step="([^"]*)"', corps)
        valeur, pas = float(champ.group(1)), float(champ.group(2))
        assert round(valeur / pas) == pytest.approx(valeur / pas, abs=1e-9)


def test_le_formulaire_renvoie_l_unite_qu_il_affiche(contexte):
    """L'unité n'est plus un champ visible : le formulaire doit la porter caché.

    Sans cela, valider le formulaire après avoir suivi le lien de bascule
    retomberait dans l'unité par défaut, avec des nombres de l'autre.
    """
    for unite in ("euros_mois", "moyen"):
        salaire = "3500" if unite == "euros_mois" else "1"
        corps = rendre(contexte, "/", {"unite_revenu": unite, "salaire": salaire})[1]
        assert f'<input type="hidden" name="unite_revenu" value="{unite}">' in corps


def test_un_refus_garde_l_unite_de_saisie(contexte):
    """Une faute de frappe ailleurs ne doit pas changer d'unité sous les doigts."""
    corps = rendre(contexte, "/", {
        "naissance": "1700", "unite_revenu": "moyen", "salaire": "1.2",
    })[1]
    assert "Saisie refusée" in corps
    assert '<input type="hidden" name="unite_revenu" value="moyen">' in corps
    assert "Niveau de revenu" in corps


def test_le_formulaire_dit_brut_et_donne_l_echelle(contexte):
    """La question posée — « brut ou net ? » — trouve sa réponse sur le champ."""
    _, corps = rendre(contexte, "/", {})
    assert "Revenu brut mensuel" in corps
    assert "la ligne « brut » de la fiche de paie" in corps
    # L'échelle est chiffrée : « 1 = salaire moyen » ne dit rien à personne.
    assert "SMIC" in corps and "moyenne" in corps and "plafond" in corps


def test_le_multiple_est_traduit_en_euros(contexte):
    _, corps = rendre(contexte, "/", {"unite_revenu": "moyen", "salaire": "1"})
    assert "1 = salaire moyen, soit" in corps


# -- plusieurs métiers -------------------------------------------------------


def test_les_metiers_suivants_sont_lus_dans_la_requete():
    saisie = Saisie.depuis_requete({
        "statut": "salarie_prive_non_cadre", "salaire": "0.9",
        "metier2_debut": "35", "metier2_statut": "fonctionnaire_etat",
        "metier2_salaire": "1.2",
        "metier3_debut": "50", "metier3_statut": "artisan",
    })
    assert [(m.debut, m.statut, m.salaire) for m in saisie.metiers] == [
        (35.0, "fonctionnaire_etat", 1.2),
        # Le niveau non renseigné est celui du métier précédent : changer de
        # statut n'est pas changer de revenu.
        (50.0, "artisan", 1.2),
    ]
    parcours = saisie.parcours(_echelle())
    assert len(parcours) == 3
    assert parcours[0].affiliation == "salarie_prive_non_cadre"
    assert parcours[0].niveau_salaire == 0.9
    assert parcours[2].affiliation == "artisan"


def test_une_adresse_sans_metier_decrit_une_carriere_d_un_seul_metier():
    """Toutes les adresses déjà partagées doivent continuer de valoir."""
    saisie = Saisie.depuis_requete({"naissance": "1960", "statut": "mineur"})
    assert saisie.metiers == []
    assert [metier.affiliation for metier in saisie.parcours(_echelle())] == ["mineur"]


def test_une_ligne_de_metier_a_moitie_remplie_est_refusee():
    """La ligne vide du formulaire ne décrit rien ; à moitié remplie, elle ment."""
    with pytest.raises(ErreurSaisie, match="âge auquel il commence"):
        Saisie.depuis_requete({"metier2_statut": "artisan"})
    with pytest.raises(ErreurSaisie, match="statut d'affiliation"):
        Saisie.depuis_requete({"metier2_debut": "40"})


@pytest.mark.parametrize("champs", [
    # Un métier antérieur au précédent : les périodes se recouvriraient.
    {"debut": "21", "metier2_debut": "20", "metier2_statut": "artisan"},
    # Un métier postérieur au départ à la retraite.
    {"liquidation": "64", "metier2_debut": "70", "metier2_statut": "artisan"},
    # Deux métiers commençant la même année.
    {"metier2_debut": "40", "metier2_statut": "artisan",
     "metier3_debut": "40", "metier3_statut": "marin"},
    # Un niveau de revenu hors bornes.
    {"metier2_debut": "40", "metier2_statut": "artisan", "metier2_salaire": "40"},
])
def test_metiers_incoherents_sont_refuses(champs):
    with pytest.raises(ErreurSaisie):
        Saisie.depuis_requete(champs)


def test_un_metier_de_statut_inconnu_est_refuse(contexte):
    saisie = Saisie.depuis_requete({
        "naissance": "1975", "metier2_debut": "40", "metier2_statut": "astronaute",
    })
    with pytest.raises(ErreurSaisie, match="astronaute"):
        contexte.simuler(saisie)


def test_changer_de_metier_change_le_resultat(contexte):
    commun = {"naissance": "1975", "debut": "21", "liquidation": "64"}
    seul = contexte.simuler(Saisie.depuis_requete(commun)).dictionnaire()
    reconverti = contexte.simuler(Saisie.depuis_requete({
        **commun, "metier2_debut": "42", "metier2_statut": "artisan",
    })).dictionnaire()

    assert reconverti["assure"]["affiliations"] == [
        "salarie_prive_non_cadre", "artisan",
    ]
    assert (reconverti["scenarios"]["notionnel_retroactif"]["pension_annuelle"]
            != seul["scenarios"]["notionnel_retroactif"]["pension_annuelle"])


def test_le_formulaire_offre_toujours_une_ligne_de_metier_de_plus(page):
    """C'est ainsi qu'on ajoute un métier : sans une ligne de JavaScript."""
    vierge = page("/")
    assert vierge.count('<p class="rang">') == 2
    assert 'name="metier2_debut" value=""' in vierge

    rempli = page("/", naissance=1975, metier2_debut=40, metier2_statut="artisan")
    assert rempli.count('<p class="rang">') == 3
    assert 'name="metier3_debut" value=""' in rempli


def test_le_formulaire_s_arrete_au_nombre_maximal_de_metiers(page):
    champs = {"naissance": 1960, "liquidation": 64}
    for rang in range(2, METIERS_MAXIMUM + 1):
        champs[f"metier{rang}_debut"] = 30 + rang
        champs[f"metier{rang}_statut"] = "artisan"
    texte = page("/", **champs)
    assert texte.count('<p class="rang">') == METIERS_MAXIMUM
    assert f'name="metier{METIERS_MAXIMUM + 1}_debut"' not in texte


def test_la_page_recapitule_le_parcours(page):
    texte = page("/", naissance=1975, debut=21, liquidation=64,
                 metier2_debut=42, metier2_statut="artisan")
    assert "Carrière en 2 métiers" in texte
    assert "Artisan de 42 ans à 64 ans" in texte


def test_requete_reconstruit_les_metiers():
    requete = Saisie.depuis_requete({
        "metier2_debut": "40", "metier2_statut": "artisan",
        "metier2_salaire": "1.5",
    }).requete()
    assert "metier2_debut=40" in requete
    assert "metier2_statut=artisan" in requete
    assert "metier2_salaire=1.5" in requete
    assert "metier3_debut" not in requete


def test_requete_reconstruit_les_parametres():
    requete = Saisie(naissance=1960, statut="mineur").requete()
    assert "naissance=1960" in requete
    assert "statut=mineur" in requete


# -- rendu -------------------------------------------------------------------


def test_les_nombres_sont_a_la_francaise():
    assert euros(1234567) == "1 234 567 €"
    assert pourcentage(-0.937, signe=True) == "-93,7 %"
    assert pourcentage(0.5, signe=True) == "+50,0 %"


def test_franciser_les_libelles_du_moteur():
    assert franciser("SR 17,542 € × taux 63.75%") == (
        "SR 17 542 € × taux 63,75 %"
    )


def test_l_echappement_protege_des_injections(page):
    texte = page("/", interruptions="<script>alert(1)</script>")
    assert "<script>alert(1)</script>" not in texte
    assert "&lt;script&gt;" in texte


def test_cellule_teintee_selon_la_valeur():
    assert "background" in Cellule("-90 %", intensite=-0.9).style()
    assert Cellule("+0 %", intensite=0.0).style() == ""
    rendu = tableau(["a"], [[Cellule("x", intensite=-0.5)]], ["nombre"])
    assert "rgba(162, 71, 46" in rendu


# -- rendu commun aux deux modes ---------------------------------------------


@pytest.mark.parametrize("chemin", ["/", "/cas-types", "/methode", "/donnees"])
def test_rendre_produit_un_corps_pour_chaque_page(contexte, chemin):
    titre, corps = rendre(contexte, chemin)
    assert titre
    assert len(corps) > 500


@pytest.mark.parametrize("chemin", ["/", "/cas-types", "/methode"])
def test_les_ages_rendus_ne_doublent_pas_leur_unite(contexte, chemin):
    """« 64 ans ans ».

    L'âge s'écrivait « 64 » et les appelants ajoutaient « ans ». Le jour où il
    s'est mis à s'écrire « 64 ans et 7 mois », l'unité s'est retrouvée en
    double sur chaque page — et aucun test ne pouvait le voir, puisque les deux
    portages étaient d'accord et que les témoins avaient été régénérés avec la
    faute. Celui-ci regarde le texte rendu.
    """
    import re

    _, corps = rendre(contexte, chemin, {
        "naissance": "1962", "naissance_mois": "3", "debut": "22",
        "liquidation": "64", "liquidation_mois": "7",
        "statut": "salarie_prive_non_cadre",
    })
    for faute in ("ans ans", "mois mois", "ans et ans"):
        assert faute not in corps, f"{faute!r} dans {chemin}"
    # Et l'âge s'y lit bien en ans et en mois.
    if chemin == "/":
        assert re.search(r"64 ans et 7 mois", corps)


def test_rendre_ignore_un_chemin_inconnu(contexte):
    titre, _ = rendre(contexte, "/n-importe-quoi")
    assert titre == "Simuler"


def test_rendre_ne_leve_jamais_sur_une_saisie_invalide(contexte):
    _, corps = rendre(contexte, "/", {"naissance": "1700"})
    assert "Saisie refusée" in corps


def test_statuts(contexte):
    codes = {entree["code"] for entree in statuts(contexte)}
    assert "salarie_prive_non_cadre" in codes


# -- liens -------------------------------------------------------------------


def test_les_liens_passent_par_l_ancre(contexte):
    """Sur GitHub Pages le site est servi dans un sous-chemin : pas de lien absolu."""
    _, corps = rendre(contexte, "/")
    entete = g.entete("/")
    assert 'href="#/cas-types"' in entete
    assert 'href="/cas-types"' not in entete
    assert 'action="#/"' in corps


def test_aucun_renvoi_vers_un_service_qui_n_existe_pas(contexte):
    """Il n'y a pas de serveur : proposer une adresse d'API serait un lien mort."""
    _, corps = rendre(contexte, "/", {"naissance": "1960",
                                      "statut": "salarie_prive_non_cadre",
                                      "debut": "20", "liquidation": "62"})
    assert "/api/" not in corps
    assert "Les résultats complets en JSON" in corps


# -- ce que charge le site ---------------------------------------------------


def _construction():
    import importlib.util
    from pathlib import Path

    chemin = Path(__file__).resolve().parents[1] / "scripts" / "construire_donnees.py"
    specification = importlib.util.spec_from_file_location("construire_donnees", chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_le_paquet_est_a_jour():
    """Le paquet et la feuille de style servis au site doivent refléter le dépôt.

    S'il échoue : ``python scripts/construire_donnees.py``.
    """
    construction = _construction()
    for chemin, contenu in construction.sorties().items():
        assert chemin.exists(), f"{chemin.name} est absent"
        assert chemin.read_bytes() == contenu, (
            f"{chemin.name} est périmé — lancer python scripts/construire_donnees.py"
        )


def test_le_paquet_contient_les_donnees_du_modele():
    import json

    construction = _construction()
    paquet = json.loads(construction.PAQUET.read_text(encoding="utf-8"))

    assert paquet["version"] == construction.VERSION
    assert {"series", "regimes", "affiliations", "quotients", "calibrations",
            "valeurs_point", "rendements_points", "hypotheses"} <= set(paquet)
    from retraite_notionnelle.donnees.regimes import CatalogueRegimes
    from retraite_notionnelle.config import RACINE_DONNEES

    assert len(paquet["regimes"]) == len(CatalogueRegimes(RACINE_DONNEES))
    assert {"inflation", "salaire_moyen", "productivite", "pass"} <= set(paquet["series"])


def test_toutes_les_calibrations_de_mortalite_sont_livrees():
    """Le navigateur lit une table, il ne recalibre rien.

    La calibration est une double bissection : la refaire dans la page coûterait
    du temps et ferait dépendre le résultat de la ``libm`` du navigateur. On
    vérifie donc que le paquet couvre tout le domaine où le modèle la consulte.
    """
    import json

    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.donnees.mortalite import DonneesMortalite

    paquet = json.loads(_construction().PAQUET.read_text(encoding="utf-8"))
    mortalite = DonneesMortalite(RACINE_DONNEES, cache_disque=False)
    for sexe in DonneesMortalite.SEXES:
        serie = mortalite._e60[sexe]
        for annee in range(serie.premiere_annee, serie.derniere_annee + 1):
            assert f"{annee}|{sexe}" in paquet["calibrations"]


def test_les_temoins_du_portage_sont_a_jour():
    """Les chiffres que doit retrouver le portage JavaScript.

    S'il échoue : ``python scripts/construire_temoins.py`` — et relire le diff,
    qui montre exactement quels montants le changement déplace.
    """
    import importlib.util
    from pathlib import Path

    chemin = Path(__file__).resolve().parents[1] / "scripts" / "construire_temoins.py"
    specification = importlib.util.spec_from_file_location("construire_temoins", chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)

    for fichier, contenu in module.construire().items():
        assert fichier.exists(), f"{fichier.name} est absent"
        assert fichier.read_bytes() == contenu, (
            f"{fichier.name} est périmé — lancer python scripts/construire_temoins.py"
        )


def test_le_portage_javascript_retrouve_les_chiffres_du_modele():
    """Lance ``node --test`` : le site doit calculer comme la référence Python."""
    import shutil
    import subprocess
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")

    racine = Path(__file__).resolve().parents[1]
    execution = subprocess.run(
        ["node", "--test", "tests/js/moteur.test.js"],
        cwd=racine, capture_output=True, text=True, check=False,
    )
    assert execution.returncode == 0, execution.stdout + execution.stderr


def test_le_portage_javascript_concorde_sur_des_carrieres_tirees_au_hasard():
    """Les témoins figés couvrent des cas choisis ; celui-ci, des cas non prévus.

    Un portage se trompe rarement là où on l'a regardé. On tire donc des
    carrières au hasard — graine fixe, donc reproductible —, on les calcule ici,
    et ``tests/js/comparer.mjs`` vérifie que le site retrouve chaque valeur.
    """
    import json
    import random
    import shutil
    import subprocess
    import tempfile
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")

    contexte = Contexte()
    alea = random.Random(20260828)
    statuts = list(contexte.simulateur().affiliations.codes)
    cas = []
    for numero in range(60):
        # Les âges sont tirés EN MOIS, et le mois de naissance avec : c'est là
        # que le portage a le plus de chances de diverger, puisque le mois
        # commande la date de liquidation, les mois cotisés de l'année du
        # départ, les trimestres civils qu'ils valident et le diviseur.
        debut = alea.randint(14 * 12, 30 * 12)
        liquidation = alea.randint(max(41 * 12, debut + 12), 75 * 12)
        requete = {
            "naissance": str(alea.randint(1900, 2005)),
            "naissance_mois": str(alea.randint(1, 12)),
            "sexe": alea.choice(["H", "F"]),
            "statut": alea.choice(statuts),
            "debut": str(debut // 12),
            "debut_mois": str(debut % 12),
            "liquidation": str(liquidation // 12),
            "liquidation_mois": str(liquidation % 12),
            "salaire": f"{alea.uniform(0.1, 9):.3f}",
            "profil": alea.choice([code for code, _ in PROFILS]),
            "primes": f"{alea.uniform(0, 0.6):.3f}",
            "enfants": str(alea.randint(0, 6)),
            "indexation": alea.choice([code for code, _ in INDEXATIONS]),
            # Fenêtre quelconque, et non plus l'une des trois autrefois
            # proposées : c'est la saisie libre qu'il s'agit de contrôler.
            "lissage": str(alea.randint(1, LISSAGE_MAXIMUM)),
            "age_reference": alea.choice([code for code, _ in AGES_REFERENCE]),
            "table": alea.choice([code for code, _ in TABLES]),
            "projection": alea.choice([code for code, _ in PROJECTIONS]),
            "bascule": str(alea.randint(1945, 2065)),
            "euros": str(alea.randint(1945, 2065)),
            "interruptions": alea.choice(["", f"{alea.randint(1985, 2005)}:"
                                          f"{alea.randint(2006, 2015)}:education_enfant"]),
        }
        # Plusieurs métiers : la carrière se coupe en tranches, chacune sous son
        # statut. C'est le découpage qui est tiré au hasard ici — combien de
        # changements, à quels âges, vers quels régimes —, parce que c'est là
        # que les deux implémentations peuvent se séparer sans qu'on le voie.
        possibles = range(debut // 12 + 1, liquidation // 12)
        changements = sorted(alea.sample(
            possibles, min(alea.randint(0, 3), len(possibles))
        ))
        for rang, age_changement in enumerate(changements, start=2):
            requete[f"metier{rang}_debut"] = str(age_changement)
            requete[f"metier{rang}_statut"] = alea.choice(statuts)
            requete[f"metier{rang}_salaire"] = f"{alea.uniform(0.1, 9):.3f}"
        nom = f"aleatoire_{numero}"
        try:
            resultat = contexte.simuler(Saisie.depuis_requete(requete)).dictionnaire()
        except (ErreurSaisie, DonneeInsuffisante, KeyError, ValueError) as erreur:
            cas.append({"nom": nom, "requete": requete, "erreur": str(erreur)})
            continue
        cas.append({"nom": nom, "requete": requete, "resultat": _sans_nan(resultat)})

    racine = Path(__file__).resolve().parents[1]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(cas, fichier, ensure_ascii=False)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", "tests/js/comparer.mjs", chemin],
            cwd=racine, capture_output=True, text=True, check=False,
        )
    finally:
        Path(chemin).unlink(missing_ok=True)
    assert execution.returncode == 0, execution.stdout + execution.stderr


@pytest.mark.parametrize("nom,champs", [
    ("carrière ordinaire", {"naissance": "1975"}),
    # Un régime PROVISIONNÉ : sa rente est retirée des cinq scénarios, donc du
    # total. Posée au-dessus de lui, sa ligne faisait un tableau qui ne
    # s'additionnait pas — 33 176,69 + 667,12 valait 33 176,69 à l'écran.
    ("fonctionnaire, rente RAFP",
     {"naissance": "1960", "statut": "fonctionnaire_etat", "primes": "0.2"}),
    # Un minimum contributif : il est déjà compris dans la ligne du régime qui
    # le sert, et le sous-total l'en retire avant que la ligne suivante ne le
    # rende visible.
    ("bas salaire, minimum contributif",
     {"naissance": "1955", "unite_revenu": "moyen", "salaire": "0.4"}),
])
def test_le_tableau_du_detail_s_additionne_a_l_ecran(contexte, nom, champs):
    """Ce que la page affirme du tableau doit se vérifier sur les nombres AFFICHÉS.

    Pas sur ceux du modèle : un lecteur additionne ce qu'il lit. Le contrôle
    porte donc sur le HTML rendu, lignes de régime d'un côté, total de l'autre,
    la ligne « hors total » exclue puisqu'elle s'annonce comme telle.
    """
    corps = rendre(contexte, "/", champs)[1]
    debut = corps.index("de quoi votre pension actuelle est faite")
    tableau = corps[debut:corps.index("</table>", debut)]
    lignes = re.findall(r"<tr>(.*?)</tr>", tableau, re.S)

    def somme(cellules: str) -> float:
        montant = re.search(r"([\d\u202f]+,\d{2})\u202f€", cellules)
        return float(montant.group(1).replace("\u202f", "").replace(",", "."))

    regimes, total = [], None
    for ligne in lignes[1:]:                       # la première est l'en-tête
        if "Pension du système actuel" in ligne:
            total = somme(ligne)
        elif ("hors total" in ligne or "Sous-total" in ligne
              or re.search(r"<td[^>]*>\+ ", ligne)):
            continue
        elif "€" in ligne:
            regimes.append(somme(ligne))

    assert total is not None, f"{nom} : pas de ligne de total"
    assert regimes, f"{nom} : aucune ligne de régime"
    assert sum(regimes) == pytest.approx(total, abs=0.01), (
        f"{nom} : les lignes affichées font {sum(regimes):.2f} €, "
        f"le total affiché {total:.2f} €"
    )


def _nombres(bloc: str) -> list[float]:
    """Les montants d'un fragment de HTML, dans l'ordre où ils s'y lisent."""
    return [float(m.replace("\u202f", "").replace(",", "."))
            for m in re.findall(r"([\d\u202f]+(?:,\d+)?)\u202f€", bloc)]


def _cellules(tableau: str) -> list[list[str]]:
    return [[re.sub(r"<[^>]+>", "", c) for c in
             re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", ligne, re.S)]
            for ligne in re.findall(r"<tr>(.*?)</tr>", tableau, re.S)]


def _bloc(corps: str, debut: str, fin: str) -> str:
    rang = corps.index(debut)
    return corps[rang:corps.index(fin, rang)]


@pytest.mark.parametrize("nom,champs", [
    ("carrière ordinaire", {"naissance": "1975"}),
    ("cadre", {"naissance": "1980", "statut": "salarie_prive_cadre",
               "unite_revenu": "moyen", "salaire": "2.5"}),
    ("artisan", {"naissance": "1970", "statut": "artisan"}),
    ("régime spécial", {"naissance": "1960", "statut": "agent_sncf",
                        "liquidation": "52"}),
    ("polypensionné", {"naissance": "1968", "unite_revenu": "moyen",
                       "salaire": "1", "metier2_debut": "40",
                       "metier2_statut": "artisan", "metier2_salaire": "1.5"}),
])
def test_les_chaines_de_calcul_se_refont_depuis_l_ecran(contexte, nom, champs):
    """Chaque ligne d'une chaîne doit se retrouver depuis celles du dessus.

    C'est ce que la page promet : « la chaîne de calcul est arithmétique ». Le
    contrôle porte donc sur les nombres AFFICHÉS, coefficients compris — un
    coefficient trop court rend la chaîne infaisable même quand le modèle a
    raison. Les bornes ne sont pas choisies : elles se déduisent des précisions
    d'affichage, et suivront si celles-ci changent.
    """
    corps = rendre(contexte, "/", champs)[1]
    pas_diviseur = 0.5 * 10 ** -DECIMALES_DIVISEUR
    pas_facteur = 0.5 * 10 ** -DECIMALES_FACTEUR

    # -- la cascade du scénario 1 au scénario 3 -----------------------------
    # Muette quand la bascule est postérieure au départ : il n'y a alors pas de
    # phase notionnelle à détailler, et le reste de la page le dit.
    if "Du scénario 1 au scénario 3" in corps:
        _verifier_cascade(nom, corps, pas_diviseur, pas_facteur)

    # -- le compte du scénario 2 --------------------------------------------
    compte = _bloc(corps, "Cotisations effectivement versées", "</table>")
    cotisations, capital, pension = _nombres(compte)[:3]
    rendement, diviseur = (
        float(x.replace("\u202f", "").replace(",", "."))
        for x in re.findall(r">×?([\d\u202f]+,\d+)(?: \(|</td>)", compte)[:2]
    )
    borne = 0.5 + cotisations * pas_facteur + rendement * 0.5
    assert abs(cotisations * rendement - capital) <= borne, f"{nom} : capital"
    borne = 0.01 + capital * pas_diviseur / diviseur + 0.5 / diviseur
    assert abs(capital / diviseur - pension) <= borne, f"{nom} : pension"


def _verifier_cascade(nom, corps, pas_diviseur, pas_facteur):
    """Les six lignes qui mènent du scénario 1 au scénario 3."""
    cascade = _bloc(corps, "Du scénario 1 au scénario 3", "</table>")
    rangs = {ligne[0][0]: ligne for ligne in _cellules(cascade)
             if ligne and ligne[0][:2] in ("a)", "b)", "c)", "d)", "e)", "f)")}
    valeur = {cle: _nombres(" ".join(ligne))[0] for cle, ligne in rangs.items()}
    coefficient = {
        cle: float(re.search(r"([\d\u202f]+,\d+)", ligne[1]).group(1)
                   .replace("\u202f", "").replace(",", "."))
        for cle, ligne in rangs.items()
        if re.search(r"([\d\u202f]+,\d+)", ligne[1])
    }

    # a) est au centime, b) à l'euro : chacun apporte sa propre imprécision.
    borne = 0.5 + valeur["a"] * pas_diviseur + coefficient["b"] * 0.005
    assert abs(valeur["a"] * coefficient["b"] - valeur["b"]) <= borne, f"{nom} : b)"
    borne = 0.5 + valeur["b"] * pas_facteur + coefficient["c"] * 0.5
    assert abs(valeur["b"] * coefficient["c"] - valeur["c"]) <= borne, f"{nom} : c)"
    assert abs(valeur["c"] + valeur["d"] - valeur["e"]) <= 1.5, f"{nom} : e)"
    borne = 0.5 + valeur["f"] * pas_diviseur / coefficient["f"] + 0.5 / coefficient["f"]
    assert abs(valeur["e"] / coefficient["f"] - valeur["f"]) <= borne, f"{nom} : f)"


def test_les_cinq_scenarios_donnent_le_meme_montant_au_mois_et_a_l_annee(contexte):
    """Mensuel × 12 = annuel, sur les nombres affichés, pour les cinq blocs."""
    corps = rendre(contexte, "/", {"naissance": "1975"})[1]
    blocs = re.findall(r'<div class="scenario">(.*?)<div class="barre', corps, re.S)
    assert len(blocs) == 5, f"{len(blocs)} scénarios affichés, cinq attendus"
    for bloc in blocs:
        mensuel = _nombres(re.search(r'principal">(.*?)</span>\s*<span class="annuel',
                                     bloc, re.S).group(1))[0]
        annuel = _nombres(re.search(r'class="annuel">(.*?)</span>', bloc, re.S).group(1))[0]
        # Chacun est arrondi au centime : l'écart ne peut passer 12 × 0,005 €.
        assert abs(mensuel * 12 - annuel) <= 0.06 + 0.005, bloc[:120]


def test_les_colonnes_derivees_de_la_page_cout_se_refont(contexte):
    """Écarts et économies de la page Coût, reconstitués depuis les cumuls affichés.

    Ces colonnes ne sont pas des mesures : ce sont des différences et des
    rapports entre deux nombres de la même ligne ou de la ligne de référence.
    Elles doivent donc se retrouver, aux arrondis d'affichage près.
    """
    corps = rendre(contexte, "/cout", {})[1]
    tableaux = re.findall(r"<table.*?</table>", corps, re.S)
    for tableau in tableaux:
        lignes = _cellules(tableau)
        entete = lignes[0] if lignes else []
        if not any("Écart" in cellule for cellule in entete):
            continue
        rang_cumul = next(i for i, c in enumerate(entete) if c.startswith("Cumul"))
        rang_ecart = next(i for i, c in enumerate(entete) if "Écart" in c)
        rang_economie = next((i for i, c in enumerate(entete) if "économie" in c), None)

        def milliards(cellule: str) -> float:
            return float(re.search(r"(-?[\d\u202f]+(?:,\d+)?)", cellule)
                         .group(1).replace("\u202f", "").replace(",", "."))

        reference = None
        for ligne in lignes[1:]:
            cumul = milliards(ligne[rang_cumul])
            if reference is None:
                reference = cumul
                continue
            ecart = float(re.search(r"(-?[\d,+]+)\u202f%", ligne[rang_ecart])
                          .group(1).replace(",", ".").lstrip("+"))
            attendu = (cumul / reference - 1) * 100
            assert abs(attendu - ecart) <= 0.1, f"écart : {ligne[0][:30]}"
            if rang_economie is not None and "—" not in ligne[rang_economie]:
                economie = milliards(ligne[rang_economie])
                assert abs((cumul - reference) - economie) <= 1.5, (
                    f"économie : {ligne[0][:30]}"
                )


@pytest.mark.parametrize("nom,champs", [
    ("départ à l'âge de référence", {"naissance": "1975", "liquidation": "67"}),
    ("départ anticipé de deux ans", {"naissance": "1975", "liquidation": "62"}),
    # Dix ans d'anticipation : le coefficient tombe à 0,43, et la formule
    # affichée donnait deux fois trop sans dire pourquoi.
    ("départ très anticipé", {"naissance": "1975", "debut": "30", "liquidation": "55"}),
    ("bas salaire", {"naissance": "1955", "unite_revenu": "moyen", "salaire": "0.4"}),
])
def test_la_formule_affichee_retrouve_la_pension_du_regime(contexte, nom, champs):
    """La colonne « Calcul » doit produire le montant de la ligne.

    Elle est écrite pour être refaite : points × valeur de service, cotisations
    × rendement, et le coefficient d'anticipation quand il s'applique. Ce
    dernier manquait, si bien qu'à dix ans d'anticipation la formule donnait
    2,3 fois le montant affiché.
    """
    comparaison = contexte.simuler(Saisie.depuis_requete(champs))
    for pension in comparaison.actuel.pensions_par_regime:
        if "points ×" not in pension.detail:
            continue
        points = re.search(r"([\d,]+\.\d+) points × valeur de service ([\d.]+)",
                           pension.detail)
        refait = float(points.group(1).replace(",", "")) * float(points.group(2))
        cotisations = re.search(
            r"cotisations revalorisées ([\d,]+) € × rendement ([\d.]+)%",
            pension.detail,
        )
        if cotisations:
            refait += (float(cotisations.group(1).replace(",", ""))
                       * float(cotisations.group(2)) / 100)
        anticipation = re.search(r"coefficient d'anticipation ([\d.]+)", pension.detail)
        if anticipation:
            refait *= float(anticipation.group(1))
        # Les points sont affichés au centième et les cotisations à l'euro :
        # l'écart ne peut venir que de là.
        assert refait == pytest.approx(pension.montant, abs=0.25), (
            f"{nom}, {pension.regime} : « {pension.detail} » donne {refait:,.2f} €, "
            f"la ligne affiche {pension.montant:,.2f} €"
        )


def _refaire_la_formule(detail: str) -> float | None:
    """Le montant que produit une formule affichée, ou None si elle n'en est pas une.

    Les deux familles : régimes en points — points × valeur de service, plus
    éventuellement cotisations × rendement, le tout multiplié par un coefficient
    d'anticipation — et régimes en annuités — salaire de référence × taux ×
    durée, éventuellement porté au minimum contributif.
    """
    def sans_virgules(texte: str) -> float:
        return float(texte.replace(",", ""))

    annuites = re.match(r"(?:SR|forfait) ([\d,]+\.\d+) € × taux ([\d.]+)% × (\d+)/(\d+)",
                        detail)
    if annuites:
        reference, taux, acquis, requis = annuites.groups()
        montant = sans_virgules(reference) * float(taux) / 100 * int(acquis) / int(requis)
        surcote = re.search(r"surcote parentale ([\d.]+)%", detail)
        if surcote:
            montant *= 1 + float(surcote.group(1)) / 100
        # Les deux planchers disent de combien ils relèvent la pension.
        plancher = re.search(
            r"porté au minimum (?:contributif|garanti) par \+ ([\d,]+\.\d+) €", detail)
        return montant + (sans_virgules(plancher.group(1)) if plancher else 0.0)

    points = re.search(r"([\d,]+\.\d+) points × valeur de service ([\d.]+)", detail)
    if not points:
        return None
    montant = sans_virgules(points.group(1)) * float(points.group(2))
    cotisations = re.search(
        r"cotisations revalorisées ([\d,]+) € × rendement ([\d.]+)%", detail)
    if cotisations:
        montant += sans_virgules(cotisations.group(1)) * float(cotisations.group(2)) / 100
    anticipation = re.search(r"coefficient d'anticipation ([\d.]+)", detail)
    if anticipation:
        montant *= float(anticipation.group(1))
    return montant


def test_toute_formule_affichee_retrouve_le_montant_de_sa_ligne(contexte):
    """Balayage de tous les statuts, à l'heure et anticipé.

    La colonne « Calcul » est écrite pour être refaite. Trois facteurs y
    manquaient : le coefficient d'anticipation des régimes en points — 2,3 fois
    d'écart à dix ans d'anticipation —, les décimales des points, et le montant
    du relèvement au minimum contributif.
    """
    ecarts = []
    controlees = 0
    branches = set()
    # Deux branches que le balayage par statut n'atteint pas : le minimum
    # garanti de la fonction publique, qui demande une carrière très courte, et
    # la surcote parentale, qui demande une mère de trois enfants au-delà de
    # l'âge de référence. Elles sont nommées, sans quoi elles resteraient
    # muettes — le minimum garanti l'est resté jusqu'ici.
    particuliers = [
        ("fonctionnaire_etat", {"naissance": "1950", "statut": "fonctionnaire_etat",
                                "debut": "40", "liquidation": "62",
                                "unite_revenu": "moyen", "salaire": "0.3"}),
        ("surcote parentale", {"naissance": "1965", "sexe": "F", "enfants": "3",
                               "debut": "20", "liquidation": "64",
                               "unite_revenu": "moyen", "salaire": "1"}),
    ]
    for statut in [affiliation["code"] for affiliation in statuts(contexte)]:
        # Quatre carrières par statut : complète, très anticipée, ancienne, et
        # une carrière COURTE — c'est elle qui déclenche les planchers, minimum
        # contributif et minimum garanti, et aucune des trois autres ne les
        # atteignait. Le relèvement au minimum garanti est resté sans montant
        # affiché jusqu'à ce que celle-ci l'exerce.
        for naissance, debut, liquidation in (("1975", "21", "67"),
                                              ("1975", "30", "55"),
                                              ("1955", "20", "64"),
                                              ("1960", "38", "64")):
            champs = {"naissance": naissance, "statut": statut, "debut": debut,
                      "liquidation": liquidation, "unite_revenu": "moyen",
                      "salaire": "0.4"}
            try:
                comparaison = contexte.simuler(Saisie.depuis_requete(champs))
            except (ErreurSaisie, DonneeInsuffisante, KeyError, ValueError):
                continue
            for pension in comparaison.actuel.pensions_par_regime:
                refait = _refaire_la_formule(pension.detail)
                if refait is None or pension.montant == 0:
                    continue
                controlees += 1
                for marqueur in ("minimum contributif", "minimum garanti",
                                 "coefficient d'anticipation", "surcote parentale"):
                    if marqueur in pension.detail:
                        branches.add(marqueur)
                # Les grandeurs de la formule sont arrondies pour l'affichage :
                # un euro sur le salaire de référence, un centime sur les points.
                if abs(refait - pension.montant) > 0.25:
                    ecarts.append(
                        f"{statut}/{naissance}/{liquidation} {pension.regime} : "
                        f"« {pension.detail[:70]} » donne {refait:,.2f} €, "
                        f"la ligne affiche {pension.montant:,.2f} €"
                    )
    for nom, champs in particuliers:
        for pension in contexte.simuler(
                Saisie.depuis_requete(champs)).actuel.pensions_par_regime:
            refait = _refaire_la_formule(pension.detail)
            if refait is None or pension.montant == 0:
                continue
            controlees += 1
            for marqueur in ("minimum contributif", "minimum garanti",
                             "coefficient d'anticipation", "surcote parentale"):
                if marqueur in pension.detail:
                    branches.add(marqueur)
            if abs(refait - pension.montant) > 0.25:
                ecarts.append(
                    f"{nom} {pension.regime} : « {pension.detail[:70]} » donne "
                    f"{refait:,.2f} €, la ligne affiche {pension.montant:,.2f} €"
                )

    assert not ecarts, "\n".join(ecarts[:8])
    # Un balayage qui n'exerce rien passe toujours : le compte et la liste des
    # branches sont le garde-fou. Écrit une première fois, ce test dépaquetait
    # mal les statuts et contrôlait ZÉRO formule, en vert.
    assert controlees > 150, f"{controlees} formules seulement ont été refaites"
    assert branches == {"minimum contributif", "minimum garanti",
                        "coefficient d'anticipation", "surcote parentale"}, (
        f"branches non exercées : {branches}"
    )


def test_les_selecteurs_du_resume_vocal_existent_dans_le_html(contexte):
    """Le résumé lu par les synthèses vocales vise des classes du HTML rendu.

    Elles vivent dans deux fichiers que rien ne relie : le sélecteur est écrit
    dans ``index.html``, la classe dans ``pages.py``. « .mensuel » y a été visé
    pendant tout ce temps sans jamais exister, si bien que l'annonce se
    réduisait au titre — exactement ce que cette région est là pour éviter.
    """
    from pathlib import Path

    racine = Path(__file__).resolve().parents[1]
    amorce = (racine / "index.html").read_text(encoding="utf-8")
    resume = amorce[amorce.index("function resume("):amorce.index("function chargement(")]
    selecteurs = re.findall(r'querySelector(?:All)?\("([^"]+)"\)', resume)
    assert selecteurs, "le résumé vocal ne vise plus aucune classe"

    # Deux rendus : « .erreur » n'existe que sur le chemin du refus, les autres
    # que sur celui du calcul. Chaque classe visée doit exister dans l'un des deux.
    classes = set()
    for champs in ({"naissance": "1975"}, {"naissance": "1700"}):
        for attribut in re.findall(r'class="([^"]*)"',
                                   rendre(contexte, "/", champs)[1]):
            classes.update(attribut.split())
    for selecteur in selecteurs:
        for classe in re.findall(r"\.([a-z-]+)", selecteur):
            assert classe in classes, (
                f"« {selecteur} » vise « .{classe} », absent du HTML rendu"
            )


def test_le_resume_vocal_annonce_bien_les_montants(contexte):
    """Et le sélecteur doit trouver quelque chose, pas seulement exister."""
    corps = rendre(contexte, "/", {"naissance": "1975"})[1]
    blocs = re.findall(r'<div class="scenario">(.*?)<div class="barre', corps, re.S)
    assert len(blocs) == 5
    for bloc in blocs:
        assert re.search(r'class="titre">[^<]+<', bloc), "scénario sans titre"
        assert re.search(r'class="chiffre principal">\s*<span class="somme">[^<]+<',
                         bloc), "scénario sans montant mis en avant"


def test_le_portage_javascript_arrondit_comme_python():
    """Les demis, là où les deux langages divergent par défaut.

    ``round`` va au pair en Python, ``Math.round`` monte en JavaScript. Le lien
    de bascule d'unité écrit un nombre arrondi : s'il différait d'un côté, le
    site et la référence n'enverraient pas vers la même adresse. Les valeurs
    balayées ici sont choisies pour tomber PILE sur un demi — seizièmes et
    huitièmes, exacts en binaire — puisque c'est le seul cas litigieux.
    """
    import json
    import random
    import shutil
    import struct
    import subprocess
    import tempfile
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")

    alea = random.Random(20260910)
    valeurs = set()
    for n in range(1, 2000):
        # n/16 et n/8 sont exacts en binaire : leur 4e et 3e décimale est un 5
        # franc, et c'est la parité du chiffre précédent qui doit trancher.
        valeurs.update((n / 16, n / 8, n / 2, n / 1000))
    for _ in range(2000):
        valeurs.add(alea.uniform(0.1, 10))
        valeurs.add(alea.uniform(0, 40000))
        # Des doubles quelconques, tirés bit à bit : aucune structure décimale.
        tire = struct.unpack("<d", struct.pack("<Q", alea.getrandbits(64)))[0]
        if tire == tire and 0 <= abs(tire) < 1e15:
            valeurs.add(abs(tire))

    cas = [{"x": x, "attendus": [f"{round(x, d):g}" for d in range(5)]}
           for x in sorted(valeurs)]

    racine = Path(__file__).resolve().parents[1]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(cas, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", "tests/js/comparer-arrondis.mjs", chemin],
            cwd=racine, capture_output=True, text=True, check=False,
        )
    finally:
        Path(chemin).unlink(missing_ok=True)
    assert execution.returncode == 0, execution.stdout + execution.stderr


def test_le_portage_javascript_rend_les_memes_pages_au_hasard():
    """Le HTML, et pas seulement les nombres, sur des saisies non prévues.

    La comparaison des seuls résultats ne voit ni les libellés, ni les aides
    chiffrées, ni le lien de bascule d'unité — c'est-à-dire précisément là où
    l'arrondi d'AFFICHAGE se décide. Les paramètres du modèle restent fixes :
    ce que ce test balaie, c'est la saisie du revenu, dans les deux unités et
    jusqu'à ses bords.
    """
    import importlib.util
    import json
    import random
    import shutil
    import subprocess
    import tempfile
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")

    racine = Path(__file__).resolve().parents[1]
    specification = importlib.util.spec_from_file_location(
        "construire_temoins", racine / "scripts" / "construire_temoins.py"
    )
    temoins = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(temoins)

    contexte = Contexte()
    alea = random.Random(20260910)
    statuts = list(contexte.simulateur().affiliations.codes)
    # Les bords comptent plus que le milieu : ce sont eux que l'arrondi fait
    # basculer d'un côté ou de l'autre des bornes du modèle.
    echelle = contexte.echelle(Saisie())
    plancher, plafond = round(echelle.mensuel(0.1)), round(echelle.mensuel(10))
    euros = [str(plancher - 1), str(plancher), str(plafond), str(plafond + 1),
             "0", "3500", "1", f"{alea.uniform(1, 40000):.2f}"]
    multiples = ["0.099", "0.1", "10", "10.001", "1", "0.0005",
                 f"{alea.uniform(0.1, 10):.4f}", f"{alea.uniform(0.1, 10):.6f}"]

    cas = []
    for numero in range(40):
        unite = alea.choice(["euros_mois", "moyen"])
        debut = alea.randint(14, 30)
        requete = {
            "naissance": str(alea.randint(1900, 2005)),
            "naissance_mois": str(alea.randint(1, 12)),
            "sexe": alea.choice(["H", "F"]),
            "statut": alea.choice(statuts),
            "debut": str(debut),
            "liquidation": str(alea.randint(max(41, debut + 1), 75)),
            "unite_revenu": unite,
            "salaire": alea.choice(euros if unite == "euros_mois" else multiples),
            "profil": alea.choice([code for code, _ in PROFILS]),
        }
        for rang, age in enumerate(sorted(alea.sample(
                range(debut + 1, int(requete["liquidation"])),
                min(alea.randint(0, 2), max(0, int(requete["liquidation"]) - debut - 1)),
        )), start=2):
            requete[f"metier{rang}_debut"] = str(age)
            requete[f"metier{rang}_statut"] = alea.choice(statuts)
            requete[f"metier{rang}_salaire"] = alea.choice(
                euros if unite == "euros_mois" else multiples
            )
        cas.append({
            "nom": f"page_{numero}",
            "requete": requete,
            "corps": temoins.sans_bloc_json(rendre(contexte, "/", requete)[1]),
        })

    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(cas, fichier, ensure_ascii=False)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", "tests/js/comparer-pages.mjs", chemin],
            cwd=racine, capture_output=True, text=True, check=False,
        )
    finally:
        Path(chemin).unlink(missing_ok=True)
    assert execution.returncode == 0, execution.stdout + execution.stderr


def _sans_nan(valeur):
    """NaN et infinis en ``null`` : la norme JSON ne connaît qu'eux."""
    if isinstance(valeur, float) and (valeur != valeur or valeur in (
            float("inf"), float("-inf"))):
        return None
    if isinstance(valeur, dict):
        return {cle: _sans_nan(v) for cle, v in valeur.items()}
    if isinstance(valeur, list):
        return [_sans_nan(v) for v in valeur]
    return valeur


def test_la_page_ne_depend_d_aucun_service_exterieur():
    """« Tout doit déjà être là » : aucune requête vers un tiers au chargement."""
    from pathlib import Path

    page = (Path(__file__).resolve().parents[1] / "index.html").read_text()
    assert 'href="moteur/style.css"' in page
    assert 'from "./moteur/js/pages.js"' in page
    assert "cdn.jsdelivr.net" not in page

    #: Seules adresses tolérées : le dépôt lui-même (liens que le lecteur suit
    #: s'il le veut) et l'espace de noms SVG, qui n'est jamais requêté.
    autorisees = ("https://github.com/gillesg-droid/", "http://www.w3.org/2000/svg")
    for hote in ("http://", "https://"):
        for morceau in page.split(hote)[1:]:
            adresse = hote + morceau.split('"')[0]
            assert adresse.startswith(autorisees), (
                f"adresse extérieure dans la page : {adresse}"
            )


def test_le_prechargement_du_paquet_correspond_a_la_requete():
    """Un préchargement qui ne correspond pas au ``fetch`` est pire qu'inutile.

    Le navigateur ne réutilise le ``<link rel="preload">`` que si la requête a
    exactement le même mode et les mêmes identifiants. Sinon il télécharge le
    paquet **deux fois** — 186 Ko en trop à chaque première visite — en n'émettant
    qu'un avertissement de console que personne ne lit. Les deux déclarations sont
    donc verrouillées ensemble ici : ``crossorigin`` sur le lien, et un ``fetch``
    nu, sans ``mode`` ni ``credentials`` qui s'en écarteraient.
    """
    import re
    from pathlib import Path

    page = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")

    prechargement = re.search(r"<link rel=\"preload\"[^>]*donnees\.json[^>]*>", page)
    appel = re.search(r"fetch\(\"moteur/donnees\.json\",\s*(\{[^}]*\})\)", page)
    assert prechargement and appel, "préchargement ou requête introuvables dans index.html"

    assert "crossorigin" in prechargement.group(0), (
        "le préchargement doit porter crossorigin, sinon il ne correspond pas au fetch"
    )
    options = appel.group(1)
    assert "credentials" not in options and "mode" not in options, (
        f"la requête s'écarte du préchargement ({options}) : le paquet serait "
        "téléchargé deux fois"
    )


def test_les_modules_sont_tous_precharges():
    """La liste de préchargement doit suivre le contenu de ``moteur/js/``.

    Le portage est un graphe profond de cinq niveaux : sans déclaration, le
    navigateur ne découvre chaque niveau qu'après avoir reçu le précédent, soit
    cinq aller-retours avant le premier calcul — une seconde entière sur une
    connexion mobile. Les ``modulepreload`` les font partir ensemble.

    Une liste écrite à la main dérive dès qu'un module est ajouté ou renommé :
    un module oublié réintroduit silencieusement la cascade, un module fantôme
    fait télécharger un fichier qui n'existe plus. Les deux échouent ici.
    """
    import re
    from pathlib import Path

    racine = Path(__file__).resolve().parents[1]
    page = (racine / "index.html").read_text(encoding="utf-8")

    precharges = set(re.findall(
        r'<link rel="modulepreload" href="moteur/js/([\w.-]+\.js)">', page))
    presents = {chemin.name for chemin in (racine / "moteur" / "js").iterdir()
                if chemin.suffix == ".js"}

    assert precharges == presents, (
        f"préchargés mais absents du dossier : {precharges - presents} ; "
        f"présents mais non préchargés : {presents - precharges}"
    )


def test_le_pied_est_pose_hors_du_contenu_remplace():
    """Un ``<footer>`` dans ``<main>`` n'est pas un repère « contentinfo ».

    Il disparaît alors de la navigation par repères des lecteurs d'écran. Le
    pied est donc inséré au montage de la coquille, à côté de ``<main>``, et le
    rendu d'une page ne réinjecte que le corps — il est statique, le
    reconstruire à chaque calcul ne servait rien non plus.
    """
    import re
    from pathlib import Path

    page = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")

    assert re.search(r"insertAdjacentHTML\([^)]*gabarit\.pied\(\)", page, re.S), (
        "le pied doit être posé une fois, au montage de la coquille"
    )
    assert "contenu.innerHTML = corps;" in page, (
        "le rendu d'une page ne doit réinjecter que le corps"
    )
    assert "corps + gabarit.pied()" not in page, (
        "le pied ne doit plus être réinséré dans <main> à chaque rendu"
    )


def test_le_resultat_est_annonce_aux_lecteurs_d_ecran():
    """Le contenu de ``<main>`` est remplacé en bloc : rien ne le signale.

    Sans région annoncée, valider le formulaire ne produit aucun retour audible
    — alors que c'est l'interaction centrale du site.
    """
    import re
    from pathlib import Path

    page = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")

    region = re.search(r'<p id="annonce"[^>]*>', page)
    assert region, "la région d'annonce a disparu de la page"
    assert 'aria-live="polite"' in region.group(0), "la région doit être annoncée poliment"
    assert 'role="status"' in region.group(0)
    assert "hors-ecran" in region.group(0), "la région ne doit pas s'afficher"

    # Les trois issues d'un rendu doivent s'entendre : résultat, refus, échec.
    assert page.count("annoncer(") >= 3, (
        "le résultat, le refus de saisie et l'échec de calcul doivent tous être annoncés"
    )


def test_le_style_d_amorcage_ne_vise_que_des_elements_existants():
    """Pas de règle orpheline dans la page : ce qui ne sert plus s'enlève.

    L'écran d'attente a déjà survécu à un moteur entier ; ses règles lui
    survivaient à leur tour. Chaque classe et chaque identifiant stylés doivent
    donc se retrouver dans le corps de la page ou dans le script qui le remplace.
    """
    import re
    from pathlib import Path

    page = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
    style = re.search(r"<style>(.*?)</style>", page, re.S).group(1)
    reste = page.replace(style, "")

    selecteurs = " ".join(re.findall(r"^([^{}@]+)\{", style, re.M))
    for nom in set(re.findall(r"[#.]([\w-]+)", selecteurs)):
        assert nom in reste, (
            f"« {nom} » est stylé dans index.html mais n'existe nulle part dans la page"
        )

    balises = set(re.findall(r"\b(\w+)(?=\s*[.#{]|\s+[\w.#])", selecteurs))
    for balise in balises & {"code", "table", "img", "button", "input", "ul", "li"}:
        assert f"<{balise}" in reste, (
            f"la règle visant <{balise}> ne correspond à aucun élément de la page"
        )


def test_le_moteur_javascript_est_versionne():
    """Le site n'a aucune étape de construction : tout ce qu'il charge est là."""
    from pathlib import Path

    moteur = Path(__file__).resolve().parents[1] / "moteur"
    assert (moteur / "donnees.json").exists()
    assert (moteur / "style.css").exists()

    modules = {chemin.name for chemin in (moteur / "js").iterdir()}
    attendus = {
        "format.js", "serie.js", "config.js", "macro.js", "mortalite.js",
        "regimes.js", "indexation.js", "conversion.js", "fusion.js",
        "age-reference.js", "carriere.js", "compte.js", "scenario-actuel.js",
        "scenario-notionnel.js", "simulateur.js", "castypes.js", "gabarit.js",
        "pages.js",
    }
    assert attendus <= modules, f"manquant : {attendus - modules}"

    #: Le portage ne tire aucune bibliothèque : il ne doit rien importer
    #: d'autre que lui-même.
    for chemin in (moteur / "js").iterdir():
        for ligne in chemin.read_text(encoding="utf-8").splitlines():
            if ligne.startswith("import ") and " from " in ligne:
                origine = ligne.rsplit(" from ", 1)[1].strip(' ;"')
                assert origine.startswith("./"), (
                    f"{chemin.name} importe depuis l'extérieur : {origine}"
                )

# -- palette des scénarios ----------------------------------------------------

#: Bornes du contrôle de palette catégorielle, en OKLCh / OKLab. Elles viennent
#: du validateur de la compétence « dataviz », qui les applique en dehors de ce
#: dépôt ; on en reprend ici les trois qui se calculent sans simuler une vision
#: daltonienne. La quatrième — séparation sous deutéranopie et protanopie — a
#: été vérifiée à l'extérieur au moment où la palette a été posée, et c'est elle
#: qui a fait rejeter la précédente : sa pire paire voisine tombait à ΔE 4,3.
BANDE_LUMINOSITE = {"clair": (0.43, 0.77), "sombre": (0.48, 0.67)}
CHROMA_MINIMAL = 0.10
ECART_MINIMAL_VISION_NORMALE = 15.0

SCENARIOS_COLORES = ("actuel", "retroactif", "prospectif",
                     "retroactif-employeur", "prospectif-employeur")


def _oklab(hexa: str) -> tuple[float, float, float]:
    """sRGB hexadécimal vers OKLab. Formules de Björn Ottosson."""
    canaux = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, v, b = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        for c in canaux
    ]
    l = (0.4122214708 * r + 0.5363325363 * v + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * v + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * v + 0.6299787005 * b) ** (1 / 3)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def _palette(theme: str) -> list[str]:
    """Les cinq couleurs de scénario lues dans la feuille de style.

    Le thème sombre les redéfinit dans un bloc ``prefers-color-scheme`` : on
    prend la DERNIÈRE définition pour le sombre, la première pour le clair.
    """
    feuille = g.FEUILLE_DE_STYLE
    couleurs = []
    for nom in SCENARIOS_COLORES:
        trouvees = re.findall(rf"--{nom}:\s*(#[0-9a-f]{{6}})\s*;", feuille)
        assert trouvees, f"couleur « --{nom} » absente de la feuille de style"
        couleurs.append(trouvees[0] if theme == "clair" else trouvees[-1])
    return couleurs


@pytest.mark.parametrize("theme", ["clair", "sombre"])
def test_la_palette_des_scenarios_reste_lisible(theme):
    """Cinq courbes qui se croisent ne peuvent pas être séparées par la couleur
    seule si cette couleur est trop pâle ou trop proche de sa voisine.

    La palette précédente échouait aux trois contrôles : quatre de ses cinq
    couleurs passaient sous le plancher de chroma — elles lisaient gris —, et sa
    pire paire voisine tombait à ΔE 11,8 en vision normale, sous le plancher de
    15. Ce test ne rejoue pas la simulation daltonienne, mais il arrête la
    dérive qui l'avait provoquée.
    """
    couleurs = _palette(theme)
    assert len(set(couleurs)) == 5, "deux scénarios partagent une couleur"
    bas, haut = BANDE_LUMINOSITE[theme]
    for couleur in couleurs:
        clarte, a, b = _oklab(couleur)
        assert bas <= clarte <= haut, (
            f"{couleur} : clarté {clarte:.3f} hors de la bande {bas}–{haut}"
        )
        assert (a * a + b * b) ** 0.5 >= CHROMA_MINIMAL, (
            f"{couleur} : chroma trop faible, la couleur lit gris"
        )
    for premiere, seconde in zip(couleurs, couleurs[1:]):
        x, y = _oklab(premiere), _oklab(seconde)
        ecart = 100 * sum((u - v) ** 2 for u, v in zip(x, y)) ** 0.5
        assert ecart >= ECART_MINIMAL_VISION_NORMALE, (
            f"{premiere} et {seconde} : ΔE {ecart:.1f}, sous le plancher de "
            f"{ECART_MINIMAL_VISION_NORMALE:.0f} en vision normale"
        )
