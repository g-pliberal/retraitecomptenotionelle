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
from retraite_notionnelle.donnees.chargement import (
    DonneeInsuffisante,
    charger_periodes_non_travaillees,
)
from retraite_notionnelle.web.pages import (
    AGES_REFERENCE,
    ANNEE_CARRIERE_MAXIMALE,
    ANNEE_CARRIERE_MINIMALE,
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
    TITRES,
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


@pytest.mark.parametrize("plage", [
    "0:999999999:chomage_indemnise",
    "1:2147483647:maladie",
    "1200:1300:maladie",
    f"1990:{ANNEE_CARRIERE_MAXIMALE + 1}:maladie",
    f"{ANNEE_CARRIERE_MINIMALE - 1}:1990:maladie",
])
def test_une_plage_d_interruption_hors_de_toute_carriere_est_refusee(plage):
    """La boucle reprenait les deux années telles quelles.

    Le calcul se fait chez le lecteur et l'adresse EST la saisie :
    « ?interruptions=0:999999999:chomage_indemnise » remplissait la mémoire de
    l'onglet et le figeait — et le lien partagé figeait celui d'un autre. Aucune
    carrière ne sort de la fenêtre contrôlée ici, et le refus est immédiat.
    """
    with pytest.raises(ErreurSaisie, match="carrière possible"):
        Saisie(interruptions=plage).interruptions_analysees()


def test_une_plage_d_interruption_aux_bornes_reste_acceptee():
    plages = Saisie(
        interruptions=f"{ANNEE_CARRIERE_MINIMALE}:{ANNEE_CARRIERE_MAXIMALE}:maladie"
    ).interruptions_analysees()
    assert plages[ANNEE_CARRIERE_MINIMALE] == "maladie"
    assert plages[ANNEE_CARRIERE_MAXIMALE] == "maladie"


def test_une_plage_d_interruption_a_l_envers_est_refusee():
    """« 2004:2003 » ne décrivait rien : la boucle ne tournait pas."""
    with pytest.raises(ErreurSaisie, match="avant de commencer"):
        Saisie(interruptions="2004:2003:maladie").interruptions_analysees()


def test_un_motif_d_interruption_inconnu_est_refuse():
    """Une faute de frappe retombait sur « sans_activite », donc sur zéro
    trimestre au lieu de quatre : elle changeait la pension sans un mot."""
    motifs = charger_periodes_non_travaillees(Contexte().base.racine_donnees)
    with pytest.raises(ErreurSaisie, match="motif inconnu"):
        Saisie(interruptions="1998:2002:educaton_enfant").interruptions_analysees(motifs)


def test_les_motifs_acceptes_sont_ceux_que_le_moteur_sait_traiter():
    """Ni plus — une liste écrite à la main aurait dérivé des données — ni
    moins : chaque motif du paquet doit rester saisissable."""
    motifs = charger_periodes_non_travaillees(Contexte().base.racine_donnees)
    assert motifs, "le paquet ne porte plus aucune période non travaillée"
    for motif in motifs:
        plages = Saisie(
            interruptions=f"1998:1999:{motif}"
        ).interruptions_analysees(motifs)
        assert plages[1998] == motif


def test_le_motif_n_est_controle_que_si_les_donnees_sont_fournies():
    """Une saisie ne connaît pas les données : sans elles, le motif passe."""
    assert Saisie(interruptions="1998:1999:peu_importe").interruptions_analysees()


@pytest.mark.parametrize("champ", ["naissance", "salaire", "primes", "euros"])
@pytest.mark.parametrize("valeur", ["nan", "inf", "-inf", "1e400", "1_975"])
def test_un_nombre_non_fini_ou_exotique_est_refuse(champ, valeur):
    """``float`` et ``Number`` ne lisent pas le même langage.

    « nan » et « 1_975 » sont des nombres pour Python, pas pour JavaScript :
    les deux lectures se seraient séparées sur une adresse forgée. « 1e400 »,
    lui, passe des deux côtés et vaut l'infini, que le calcul propage sans
    jamais échouer — le simulateur affichait « Ce revenu vaut inf fois le
    salaire moyen », et « ?naissance=inf » levait un OverflowError nu.
    """
    with pytest.raises(ErreurSaisie):
        Saisie.depuis_requete({"unite_revenu": "euros_mois", champ: valeur})


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
    # Chaque métier est un groupe de champs, et son rang en est la légende.
    assert vierge.count('<legend class="rang">') == 2
    assert 'name="metier2_debut" value=""' in vierge

    rempli = page("/", naissance=1975, metier2_debut=40, metier2_statut="artisan")
    assert rempli.count('<legend class="rang">') == 3
    assert 'name="metier3_debut" value=""' in rempli


def test_le_formulaire_s_arrete_au_nombre_maximal_de_metiers(page):
    champs = {"naissance": 1960, "liquidation": 64}
    for rang in range(2, METIERS_MAXIMUM + 1):
        champs[f"metier{rang}_debut"] = 30 + rang
        champs[f"metier{rang}_statut"] = "artisan"
    texte = page("/", **champs)
    assert texte.count('<legend class="rang">') == METIERS_MAXIMUM
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


def test_le_balayage_des_temoins_couvre_tous_les_statuts():
    """Un statut sans témoin n'est comparé à rien, des deux côtés du portage.

    Le balayage « un statut, une génération » se voulait le catalogue entier ;
    il en oubliait treize, dont les huit sections libérales écrites depuis. Ce
    n'est pas une lacune de couverture ordinaire : c'est le SEUL dispositif qui
    confronte `moteur/js/` au modèle Python, et il ne confronte que ce qu'il
    simule. `tranche_1_3_pass`, ajoutée d'un seul côté, n'a été prise que parce
    qu'un statut du balayage l'empruntait — la même faute sur une borne que seul
    un officier ministériel traverse serait passée sans bruit.

    La liste reste écrite à la main, pour qu'on voie ce qui est couvert ; ce
    test la force à rester complète.
    """
    import importlib.util
    from pathlib import Path

    from retraite_notionnelle.carriere import Affiliations
    from retraite_notionnelle.config import RACINE_DONNEES

    chemin = Path(__file__).resolve().parents[1] / "scripts" / "construire_temoins.py"
    specification = importlib.util.spec_from_file_location("construire_temoins", chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)

    manquants = set(Affiliations(RACINE_DONNEES).codes) - set(module.STATUTS)
    assert not manquants, (
        "statuts sans témoin, donc sans comparaison Python/JavaScript : "
        + ", ".join(sorted(manquants))
    )
    inconnus = set(module.STATUTS) - set(Affiliations(RACINE_DONNEES).codes)
    assert not inconnus, "statuts balayés mais absents du routage : " + ", ".join(
        sorted(inconnus)
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
              # La première cellule d'une ligne est un en-tête de ligne
              # depuis que les tableaux en portent : les deux balises sont
              # admises ici, faute de quoi les lignes « + avantage » ne
              # seraient plus exclues et le total serait compté deux fois.
              or re.search(r"<t[dh][^>]*>\+ ", ligne)):
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


def test_les_refus_de_saisie_sont_ecrits_a_l_identique_par_les_deux_moteurs():
    """Un refus est une page comme une autre, et il se compare comme telle.

    Le tirage au hasard de la page précédente ne produit que des carrières
    valides : il ne dirait rien des phrases que le simulateur écrit quand il
    refuse. Ce sont pourtant elles que le lecteur lit le plus souvent, et elles
    citent des bornes — années, motifs, âges — qu'un portage peut écrire
    autrement sans qu'aucun chiffre ne bouge.
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
    refuses = [
        {"interruptions": "0:999999999:chomage_indemnise"},
        {"interruptions": "1200:1300:maladie"},
        # Une année qu'aucun des deux moteurs n'écrit pareil une fois relue :
        # « 1e+21 » en JavaScript, l'entier exact en Python.
        {"interruptions": "999999999999999999999:2000:maladie"},
        {"interruptions": "0009999:2000:maladie"},
        {"interruptions": "-1990:2000:maladie"},
        {"interruptions": "2004:2003:maladie"},
        {"interruptions": "1998:2002:educaton_enfant"},
        {"interruptions": "1995-1997"},
        {"naissance": "inf"},
        {"naissance": "1_975"},
        {"naissance": "1700"},
        {"unite_revenu": "euros_mois", "salaire": "nan"},
        {"unite_revenu": "euros_mois", "salaire": "1e400"},
        {"unite_revenu": "euros_mois", "salaire": "1"},
        {"debut": "12"},
        {"liquidation": "90"},
        {"enfants": "99"},
        {"primes": "0.99"},
        {"euros": "9999"},
        {"statut": "astronaute"},
        {"metier2_debut": "18", "metier2_statut": "salarie_prive_cadre"},
    ]
    # Les voisines immédiates de ces refus, qui doivent au contraire calculer :
    # une borne posée d'un cran trop loin se verrait ici, et nulle part ailleurs.
    acceptees = [
        {"interruptions": "1995:1999:education_enfant"},
        {"interruptions": f"{ANNEE_CARRIERE_MINIMALE}:1990:sans_activite"},
        {"unite_revenu": "euros_mois", "salaire": "1e3"},
        {"enfants": str(ENFANTS_MAXIMUM)},
    ]

    cas = []
    for prefixe, champs_, refuse in (("refus", refuses, True),
                                     ("accepte", acceptees, False)):
        for numero, champs in enumerate(champs_):
            requete = {"naissance": "1975", **champs}
            corps = temoins.sans_bloc_json(rendre(contexte, "/", requete)[1])
            # Le test ne vaut que si chaque saisie tombe du côté attendu : une
            # borne relâchée les ferait toutes calculer, et la comparaison
            # passerait sans rien couvrir.
            assert ('class="erreur"' in corps) is refuse, (
                f"{prefixe}_{numero} {requete} : le simulateur "
                + ("calcule au lieu de refuser" if refuse
                   else "refuse au lieu de calculer")
            )
            cas.append({
                "nom": f"{prefixe}_{numero}", "requete": requete, "corps": corps,
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
    autorisees = ("https://github.com/g-pliberal/", "http://www.w3.org/2000/svg")
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


# -- accessibilité -------------------------------------------------------------
#
# Ce que le site promet dans ses mentions légales, vérifié ici. Une déclaration
# d'accessibilité qui n'est adossée à aucun contrôle se périme au premier
# changement de gabarit : celui qui suit ne se périme pas.

#: Plancher de contraste des textes courants, et des textes agrandis ou des
#: contours de composants — WCAG 2.1, critères 1.4.3 et 1.4.11.
CONTRASTE_TEXTE = 4.5
CONTRASTE_COMPOSANT = 3.0


def _couleur(nom: str, theme: str) -> str:
    """Une variable de la feuille de style, dans l'un des deux thèmes.

    Le thème sombre redéfinit les mêmes noms dans un bloc
    ``prefers-color-scheme`` : la première définition est celle du clair, la
    dernière celle du sombre.
    """
    trouvees = re.findall(rf"--{nom}:\s*(#[0-9a-f]{{6}})\s*;", g.FEUILLE_DE_STYLE)
    assert trouvees, f"couleur « --{nom} » absente de la feuille de style"
    return trouvees[0] if theme == "clair" else trouvees[-1]


def _luminance(hexa: str) -> float:
    """Luminance relative, au sens de WCAG 2.1."""
    canaux = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, v, b = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        for c in canaux
    ]
    return 0.2126 * r + 0.7152 * v + 0.0722 * b


def _contraste(premiere: str, seconde: str) -> float:
    claire, sombre = sorted((_luminance(premiere), _luminance(seconde)),
                            reverse=True)
    return (claire + 0.05) / (sombre + 0.05)


@pytest.mark.parametrize("theme", ["clair", "sombre"])
def test_les_textes_tiennent_le_plancher_de_contraste(theme):
    """Tout ce qui s'écrit, sur chacun des trois fonds de la page.

    ``--texte-doux`` porte les aides de saisie, les gloses, les graduations des
    graphiques et le pied de page : c'est la couleur la plus employée du site
    après le texte courant, et la première à céder quand la palette bouge. Elle
    a déjà cédé une fois — l'aide sous chaque libellé de champ était peinte à
    80 % d'opacité, ce qui la ramenait à 4,23:1 sur le fond clair.
    """
    for fond in ("fond", "fond-carte", "fond-appui"):
        for texte in ("texte", "texte-doux", "accent", "alerte"):
            mesure = _contraste(_couleur(texte, theme), _couleur(fond, theme))
            assert mesure >= CONTRASTE_TEXTE, (
                f"{theme} : --{texte} sur --{fond} tombe à {mesure:.2f}:1, "
                f"sous le plancher de {CONTRASTE_TEXTE}:1"
            )


@pytest.mark.parametrize("theme", ["clair", "sombre"])
def test_le_contour_des_champs_se_distingue_du_fond(theme):
    """Un champ de saisie se reconnaît à son contour : encore faut-il le voir.

    WCAG 1.4.11 demande 3:1 entre un composant d'interface et ce qui l'entoure.
    Le filet décoratif ``--trait`` plafonne à 1,4:1 — c'est voulu, il ne porte
    aucune information —, et les champs ont donc leur propre couleur de bord.
    """
    for fond in ("fond", "fond-carte"):
        mesure = _contraste(_couleur("trait-champ", theme), _couleur(fond, theme))
        assert mesure >= CONTRASTE_COMPOSANT, (
            f"{theme} : le contour des champs tombe à {mesure:.2f}:1 sur "
            f"--{fond}, sous le plancher de {CONTRASTE_COMPOSANT}:1"
        )


def test_la_feuille_de_style_respecte_le_reglage_mouvement_reduit():
    """La jauge d'attente glisse sans fin ; une animation sans fin rend malade.

    Le système le signale, et la feuille l'écoute — WCAG 2.2.2 et 2.3.3.
    """
    assert "@media (prefers-color-scheme: dark)" in g.FEUILLE_DE_STYLE
    bloc = g.FEUILLE_DE_STYLE.split("@media (prefers-reduced-motion: reduce)")
    assert len(bloc) == 2, "la feuille ne tient pas compte du mouvement réduit"
    assert "animation-iteration-count: 1 !important" in bloc[1], (
        "une animation qui boucle doit cesser de boucler"
    )


@pytest.mark.parametrize("chemin", list(TITRES))
def test_chaque_tableau_porte_un_titre_et_des_en_tetes_de_ligne(contexte, chemin):
    """Un tableau sans titre s'annonce « tableau, 7 colonnes, 12 lignes ».

    Et sans en-tête de ligne, une cellule lue au hasard n'est rattachée à rien :
    la synthèse vocale énonce « moins 31 % » sans dire de quel cas type ni de
    quelle génération. RGAA 4.1, critères 5.4 et 5.7.
    """
    corps = rendre(contexte, chemin, {})[1]
    tableaux = re.findall(r"<table>(.*?)</table>", corps, re.S)
    for rang, tableau_html in enumerate(tableaux, start=1):
        assert tableau_html.startswith("<caption>"), (
            f"{chemin} : le tableau n° {rang} n'a pas de titre"
        )
        lignes = re.findall(r"<tr>(.*?)</tr>", tableau_html, re.S)
        for ligne in lignes[1:]:
            assert ligne.startswith("<th ") and 'scope="row"' in ligne, (
                f"{chemin} : une ligne du tableau n° {rang} n'a pas d'en-tête"
            )


@pytest.mark.parametrize("chemin", list(TITRES))
def test_toute_zone_defilante_est_atteignable_au_clavier(contexte, chemin):
    """Une boîte qui défile sans être focusable est hors d'atteinte au clavier.

    Les moteurs ne s'accordent pas sur ce point — Firefox rend focusables les
    boîtes défilantes, les autres non —, et un tableau plus large que l'écran
    devient alors impossible à parcourir sans souris. WCAG 2.1.1.
    """
    corps = rendre(contexte, chemin, {})[1]
    for ouverture in re.findall(r'<div class="defilant"[^>]*>', corps):
        assert 'tabindex="0"' in ouverture, (
            f"{chemin} : zone défilante inatteignable au clavier — {ouverture}"
        )


@pytest.mark.parametrize("chemin", list(TITRES))
def test_aucune_information_ne_vit_dans_une_infobulle(contexte, chemin):
    """``title`` ne s'ouvre ni au clavier, ni au doigt, ni sous synthèse vocale.

    Les gloses des douze cas types et des huit systèmes y ont vécu : elles sont
    désormais en clair, sous le tableau qu'elles expliquent.
    """
    corps = rendre(contexte, chemin, {})[1]
    assert ' title="' not in corps, (
        f"{chemin} : une information n'est accessible qu'au survol de la souris"
    )


def test_chaque_champ_du_formulaire_porte_une_etiquette(page):
    """Un champ sans étiquette est un champ dont personne ne sait ce qu'il veut.

    Le contrôle vaut aussi pour les listes déroulantes, et ignore les champs
    cachés, qui ne sont pas saisis.
    """
    texte = page("/")
    etiquetes = set(re.findall(r'<label for="([^"]+)"', texte))
    for balise in re.findall(r"<(?:input|select)\b[^>]*>", texte):
        if 'type="hidden"' in balise:
            continue
        identifiant = re.search(r'id="([^"]+)"', balise)
        assert identifiant, f"champ sans identifiant : {balise}"
        assert identifiant.group(1) in etiquetes, (
            f"champ sans étiquette : {identifiant.group(1)}"
        )


def test_les_metiers_forment_des_groupes_de_champs_nommes(page):
    """« Revenu brut mensuel » est le même libellé dans chaque bloc de métier.

    Seul le rang les distingue : il doit donc être la LÉGENDE d'un groupe, qui
    est énoncée avec chacun des champs qu'elle couvre, et non un intertitre, qui
    ne se voit qu'à l'œil. WCAG 3.3.2.
    """
    texte = page("/")
    groupes = re.findall(r'<fieldset class="metier[^"]*">(.{0,80})', texte, re.S)
    assert len(groupes) >= 2, "les métiers ne forment plus des groupes de champs"
    for debut in groupes:
        assert debut.startswith('<legend class="rang">'), (
            f"un groupe de métier n'a pas de légende : {debut!r}"
        )


def test_les_champs_qui_decrivent_la_personne_sont_reconnaissables(page):
    """WCAG 1.3.5 : un champ qui demande une information sur l'utilisateur doit
    dire laquelle, pour que le navigateur et les aides à la saisie la
    reconnaissent."""
    texte = page("/")
    assert 'id="naissance"' in texte and 'autocomplete="bday-year"' in texte
    assert 'id="sexe"' in texte and 'autocomplete="sex"' in texte


def test_le_lien_d_evitement_ouvre_chaque_page(contexte):
    """Premier élément parcouru au clavier, et seul moyen d'atteindre le contenu
    sans retraverser l'en-tête à chaque page. RGAA 12.7."""
    entete = g.entete("/")
    assert entete.startswith('<a class="evitement" href="#contenu">'), entete[:80]
    assert 'aria-label="Navigation principale"' in entete, (
        "le repère de navigation doit porter un nom"
    )


def test_les_mentions_legales_sont_joignables_depuis_toute_page():
    """La loi veut qu'elles le soient. Le pied est posé une fois, à côté de
    ``<main>``, et ne dépend donc pas de la page affichée."""
    pied = g.pied()
    assert 'href="#/mentions"' in pied
    assert "aucune valeur officielle" in pied, (
        "le pied doit dire que le simulateur n'engage aucune caisse"
    )


def test_la_page_des_mentions_dit_l_hebergeur_et_l_etat_d_accessibilite(contexte):
    """Les trois obligations que la page porte, et le trou qu'elle signale.

    La LCEN impose de nommer l'hébergeur ; l'éditeur personne morale doit
    s'identifier, et ce qui manque pour cela doit être visible plutôt que
    comblé au jugé.
    """
    _, corps = rendre(contexte, "/mentions", {})
    assert "GitHub, Inc." in corps, "l'hébergeur doit être nommé"
    assert "conformité partielle" in corps, (
        "l'état d'accessibilité doit être déclaré, et sans le surestimer"
    )
    assert "Aucun audit externe" in corps
    assert corps.count("a-completer") >= 4, (
        "les mentions que l'éditeur doit encore fournir doivent rester visibles"
    )
    assert "ne collecte rien" in corps


def test_chaque_page_du_site_est_comparee_au_portage(contexte):
    """Une page qui n'a pas de témoin n'est comparée à rien.

    Les deux rendus — Python et JavaScript — ne divergeraient alors qu'à
    l'écran, et personne ne le saurait avant un lecteur.
    """
    import json
    from pathlib import Path

    temoins = json.loads(
        (Path(__file__).resolve().parent / "temoins" / "pages.json")
        .read_text(encoding="utf-8")
    )
    couverts = {page["chemin"] for page in temoins.values()}
    assert set(TITRES) <= couverts, (
        f"pages sans témoin : {set(TITRES) - couverts} — les ajouter à "
        "scripts/construire_temoins.py"
    )


def test_le_focus_ne_retombe_pas_au_debut_du_document_apres_un_rendu():
    """``<main>`` est remplacé en bloc : ce qui avait le focus vient de
    disparaître, et le navigateur le renvoie sur ``<body>``. Au clavier, la
    tabulation suivante repart alors du tout début du document."""
    from pathlib import Path

    page = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
    assert 'main id="contenu" tabindex="-1"' in page, (
        "<main> doit pouvoir recevoir le focus"
    )
    assert "function reprendre(" in page and "reprendre(contenu)" in page

    #: Sauf au tout premier rendu : le focus est alors là où le navigateur l'a
    #: laissé, c'est-à-dire au début du document — d'où le lien d'évitement est
    #: le premier élément qu'une tabulation rencontre. Le déplacer dans <main>
    #: dès le chargement rendrait ce lien inatteignable en avant, et la page
    #: perdrait le raccourci même qu'elle offre.
    assert "let premierRendu = true;" in page
    assert "if (premierRendu) {" in page

    #: Le lien d'évitement ne peut pas se contenter de son « #contenu » : ici
    #: l'adresse EST la route, et l'écrire renverrait le simulateur à sa page
    #: d'accueil, perdant la simulation en cours.
    assert 'closest("a.evitement")' in page and "evenement.preventDefault()" in page


# -- la description détaillée des graphiques -----------------------------------


def test_un_graphique_porte_le_tableau_de_ses_points():
    """Un tracé est une image ; le tableau de ses points en est la description.

    Le tableau est produit par la fonction qui trace, à partir des mêmes séries
    : c'est ce qui garantit qu'il ne peut pas s'en écarter. Le contrôle porte
    donc sur ce que cette fonction restitue — toutes les valeurs, un tiret là où
    la série n'en a pas, et les valeurs PROPRES de chaque série même quand le
    graphique les empile.
    """
    series = (
        g.Serie("Première", (1.0, None, 3.0), "var(--serie-1)"),
        g.Serie("Seconde", (10.0, 20.0, 30.0), "var(--serie-2)"),
    )
    for empile in (False, True):
        html = g.graphique("Un essai", (1990, 1991, 1992), series,
                           unite="Md €", empile=empile)
        detail = html[html.index('<details class="donnees-graphique">'):]
        assert "année par année (3 lignes)" in detail

        lignes = re.findall(r"<tr>(.*?)</tr>", detail, re.S)
        assert len(lignes) == 4, "une ligne d'en-tête et trois années"
        assert "Première (Md €)" in lignes[0] and "Seconde (Md €)" in lignes[0]

        valeurs = [re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", ligne)
                   for ligne in lignes[1:]]
        assert valeurs == [
            ["1990", "1", "10"],
            # La série n'a pas de valeur cette année-là : la courbe s'y
            # interrompt, et le tableau ne l'invente pas davantage.
            ["1991", "—", "20"],
            ["1992", "3", "30"],
        ], valeurs


def test_le_tableau_d_un_graphique_nomme_ce_que_porte_son_axe():
    """La trajectoire d'un retraité se lit en âges, non en années : une colonne
    « Année » pour une suite d'âges serait un contresens, et c'est la seule
    chose que le tracé ne dit pas de lui-même."""
    series = (g.Serie("Cumul", (0.0, 31.0), "var(--actuel)"),)
    html = g.graphique("Un essai", (64, 65), series, nom_abscisse="Âge")
    assert "âge par âge (2 lignes)" in html
    assert '<th class="" scope="col">Âge</th>' in html


@pytest.mark.parametrize("chemin", list(TITRES))
def test_aucun_graphique_n_est_livre_sans_ses_chiffres(contexte, chemin):
    """Le tableau est émis par ``graphique()`` : il ne peut donc pas manquer.

    Ce test le vérifie sur les pages réellement rendues — c'est lui qui
    échouerait si quelqu'un réécrivait un tracé à la main, hors de la fonction
    qui en produit la description.
    """
    corps = rendre(contexte, chemin, {})[1]
    traces = corps.count('<figure class="graphique">')
    tableaux = corps.count('<details class="donnees-graphique">')
    assert traces == tableaux, (
        f"{chemin} : {traces} graphiques pour {tableaux} tableaux de données"
    )


def test_le_graphique_de_la_trajectoire_porte_ses_ages(contexte):
    """Sur la page de résultats, le seul graphique qui ne se lit pas en années."""
    corps = rendre(contexte, "/", {
        "naissance": "1975", "statut": "salarie_prive_non_cadre",
        "debut": "21", "liquidation": "64", "salaire": "3500",
        "unite_revenu": "euros_mois",
    })[1]
    assert "âge par âge" in corps
    assert '<th class="" scope="col">Âge</th>' in corps


def test_le_tableau_des_regles_d_indexation_sort_bien_du_modele(contexte):
    """Les seuls chiffres du site qui soient écrits à la main.

    La page Méthode affiche, pour neuf règles d'indexation, le rendement cumulé
    1941-2025 et la part du pouvoir d'achat conservée. Ces valeurs ne sont pas
    calculées au rendu : elles sont dans le gabarit, en toutes lettres, parce
    qu'elles ne dépendent d'aucune carrière et coûteraient neuf parcours de
    quatre-vingt-cinq ans à chaque affichage de la page.

    Le prix de ce choix est qu'elles peuvent se démentir en silence — ce qui
    était arrivé à l'une d'elles. Ce test les recalcule depuis le modèle.

    La convention des bornes est celle de ``coefficient`` : une somme versée en
    1940 est revalorisée à partir de l'année suivante, donc par les taux de 1941
    à 2025 inclus — ce que l'intitulé de la colonne appelle « appliquée
    1941-2025 ».
    """
    from dataclasses import replace

    from retraite_notionnelle.config import ModeIndexation
    from retraite_notionnelle.moteur.indexation import Indexation

    simulateur = contexte.simulateur()

    def cumul(mode: ModeIndexation, lissage: int = 1) -> float:
        parametres = replace(simulateur.parametres, mode_indexation=mode,
                             lissage_indexation=lissage)
        return Indexation(simulateur.macro, parametres).coefficient(1940, 2025)

    prix = cumul(ModeIndexation.PRIX)
    attendues = [
        ("Triple lock inversé, littéral", ModeIndexation.TRIPLE_LOCK_INVERSE, 1),
        ("Moyenne des trois taux", ModeIndexation.MOYENNE_TROIS_TAUX, 1),
        ("Triple lock inversé, tout en nominal",
         ModeIndexation.TRIPLE_LOCK_INVERSE_NOMINAL, 1),
        ("Indexation sur les prix", ModeIndexation.PRIX, 1),
        ("Médiane des trois taux", ModeIndexation.MEDIANE_TROIS_TAUX, 1),
        ("Revalorisation réellement pratiquée",
         ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE, 1),
        ("Masse salariale (règle d'équilibre)", ModeIndexation.MASSE_SALARIALE, 1),
        ("PIB nominal", ModeIndexation.PIB_NOMINAL, 1),
        ("PIB nominal lissé sur 5 ans (Italie)", ModeIndexation.PIB_NOMINAL, 5),
    ]

    corps = rendre(contexte, "/methode", {})[1]
    debut = corps.index("Règle appliquée 1941-2025")
    tableau_html = corps[debut:corps.index("</table>", debut)]
    # La mise en valeur d'une cellule — la ligne littérale est en gras — n'est
    # pas son contenu : on compare des nombres, pas du balisage.
    def texte(cellule: str) -> str:
        return re.sub(r"<[^>]+>", "", cellule).strip()

    lignes = {
        cellules[0]: cellules[1:]
        for cellules in (
            [texte(cellule)
             for cellule in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", ligne)]
            for ligne in re.findall(r"<tr>(.*?)</tr>", tableau_html, re.S)
        )
        if cellules
    }

    for libelle, mode, lissage in attendues:
        assert libelle in lignes, f"ligne « {libelle} » absente du tableau"
        comptes, prix_affiche, conserve = lignes[libelle]
        valeur = cumul(mode, lissage)
        assert comptes == "×" + g.nombre(valeur, 1), (
            f"{libelle} : la page affiche {comptes}, le modèle donne "
            f"×{g.nombre(valeur, 1)}"
        )
        assert prix_affiche == "×" + g.nombre(prix, 1)
        attendu = g.pourcentage(valeur / prix, decimales=1)
        assert conserve == attendu, (
            f"{libelle} : la page conserve {conserve}, le modèle donne {attendu}"
        )

    # La prose qui entoure le tableau cite deux de ses chiffres. Le premier est
    # calculé comme lui ; le second est une phrase — « près de cinq fois les
    # prix » —, qui n'est vraie que dans une fourchette. Elle y est.
    reference = cumul(ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE) / prix
    assert 4.5 <= reference < 5.5, (
        f"la page dit « près de cinq fois les prix » pour un rapport de "
        f"{reference:.2f} : la phrase ne tient plus"
    )
    assert f"×{g.nombre(cumul(ModeIndexation.TRIPLE_LOCK_INVERSE), 1)}" in corps


def test_la_correction_des_trois_generations_se_retrouve(contexte):
    """Le seul chiffre du site qui reste écrit à la main, et pourquoi.

    La page Méthode dit de combien la ligne de neutralisation — revalorisation
    réellement pratiquée plutôt qu'indexation sur les prix — déplace l'écart du
    scénario 2, pour trois générations. Le calculer à l'affichage demande six
    simulations, soit plus d'une seconde : c'est le seul endroit où la mesure
    coûte trop cher pour être refaite à chaque page.

    Elle est donc écrite, et vérifiée ici. Le texte nomme désormais la carrière
    — un salarié du privé non cadre au salaire moyen, de 20 à 62 ans —, sans
    quoi personne, ce test compris, ne pourrait refaire le calcul.
    """
    from dataclasses import replace

    from retraite_notionnelle.config import ModeIndexation, Parametres
    from retraite_notionnelle.simulateur import Simulateur

    def correction(generation: int) -> float:
        ecarts = {}
        for mode in (ModeIndexation.PRIX,
                     ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE):
            simulateur = Simulateur(replace(Parametres(), mode_indexation=mode))
            carriere = simulateur.carriere_simple(
                annee_naissance=generation, sexe="H",
                affiliation="salarie_prive_non_cadre", age_debut=20,
                age_liquidation=62, niveau_salaire=1.0,
                profil_carriere="ascendant")
            ecarts[mode] = simulateur.simuler(carriere).variation(
                "notionnel_retroactif") * 100
        return (ecarts[ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE]
                - ecarts[ModeIndexation.PRIX])

    corps = rendre(contexte, "/methode", {})[1]
    assert "un salarié du privé non cadre" in corps, (
        "la page doit dire sur quelle carrière ces points sont mesurés"
    )
    for generation, attendu in ((1920, 6.2), (1945, 0.0), (1958, -0.4)):
        mesure = correction(generation)
        assert round(mesure, 1) == attendu, (
            f"génération {generation} : la page annonce {attendu:+.1f} point(s), "
            f"le modèle en donne {mesure:+.1f}"
        )
        signe = "+" if attendu >= 0 else "-"
        écrit = f"{signe}{abs(attendu):.1f}".replace(".", ",")
        assert écrit in corps, f"« {écrit} » a disparu de la page"


def test_le_README_dit_le_vrai_nombre_de_tests():
    """Troisième chiffre de données annoncé en prose, et le plus volatil.

    Le README annonçait 321 tests et `docs/limites.md` 390 : le dépôt en
    comptait 520. Les deux phrases étaient vraies le jour où elles ont été
    écrites, et aucune n'a suivi. C'est la même dérive que « 472 tests pour
    485 », déjà corrigée à la main une fois — la corriger à la main ne suffit
    donc pas, il faut que quelque chose compte.

    Le décompte se fait par une collecte pytest dans un PROCESSUS SÉPARÉ.
    Interroger la session courante donnerait un nombre faux dès que quelqu'un
    lance un sous-ensemble (`-k`, un fichier) : le test échouerait sans qu'une
    ligne du dépôt ait bougé.
    """
    import re
    import subprocess
    import sys
    from pathlib import Path

    racine = Path(__file__).resolve().parents[1]
    collecte = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         "-p", "no:cacheprovider", str(racine / "tests")],
        capture_output=True, text=True, cwd=racine,
    )
    compte = re.search(r"(\d+) tests? collected", collecte.stdout)
    assert compte, f"collecte illisible : {collecte.stdout[-400:]}"
    reels = int(compte.group(1))

    for nom, motif in (("README.md", r"(\d+) tests Python"),
                       ("docs/limites.md", r"(\d+) tests couvrent")):
        texte = (racine / nom).read_text(encoding="utf-8")
        annonces = re.findall(motif, texte)
        assert annonces, f"{nom} n'annonce plus de nombre de tests"
        for annonce in annonces:
            assert int(annonce) == reels, (
                f"{nom} annonce {annonce} tests, le dépôt en collecte {reels}"
            )


def test_le_README_dit_le_vrai_nombre_de_statuts_et_de_regimes():
    """Deux comptes annoncés en quatre endroits, et rien ne les recoupait.

    Le README écrit « les 22 statuts et les 37 régimes du catalogue », et
    répète le second deux fois de plus ; `docs/limites.md` l'écrit deux fois
    encore. Ce sont des chiffres de données, pas de prose : ils bougent chaque
    fois qu'une fiche ou un statut est ajouté, et rien n'obligeait la phrase à
    suivre. Le dépôt s'est déjà fait prendre — « 472 tests pour 485 » — par la
    main qui écrit ces lignes. Ici, les fichiers comptent eux-mêmes.
    """
    from pathlib import Path

    from retraite_notionnelle.carriere import Affiliations
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.donnees.regimes import CatalogueRegimes

    racine = Path(__file__).resolve().parents[1]
    statuts_reels = len(Affiliations(RACINE_DONNEES).codes)
    regimes_reels = len(list(CatalogueRegimes(RACINE_DONNEES)))

    for nom in ("README.md", "docs/limites.md"):
        texte = (racine / nom).read_text(encoding="utf-8")
        for annonce, attendu, quoi in (
            (r"(\d+) statuts", statuts_reels, "statuts"),
            (r"(\d+) (?:régimes|fiches de régime|fiches du catalogue)",
             regimes_reels, "régimes"),
        ):
            for trouve in re.findall(annonce, texte):
                assert int(trouve) == attendu, (
                    f"{nom} annonce {trouve} {quoi}, le dépôt en compte {attendu}"
                )


def test_les_bornes_d_assiette_sont_les_memes_des_deux_cotes():
    """Le JavaScript recopie la table des tranches : elle doit rester à jour.

    `BORNES_ASSIETTE` existe deux fois — dans `donnees/regimes.py` et dans
    `moteur/js/regimes.js` — parce que le portage ne lit pas le Python. Une
    tranche ajoutée d'un seul côté ne fait échouer aucun import : le JavaScript
    retombe sur `[0, null]`, c'est-à-dire SANS PLAFOND, et le régime prélève
    alors sur la totalité du revenu. C'est exactement ce qui est arrivé en
    ajoutant `tranche_1_3_pass` pour la Cipav : le portage cotisait 39 146 €
    là où le modèle en cotisait 19 356, sans qu'aucune erreur soit levée — seul
    le témoin l'a vu.
    """
    import re
    from pathlib import Path

    from retraite_notionnelle.donnees.regimes import BORNES_ASSIETTE

    racine = Path(__file__).resolve().parents[1]
    source = (racine / "moteur" / "js" / "regimes.js").read_text(encoding="utf-8")
    bloc = re.search(r"BORNES_ASSIETTE = Object\.freeze\(\{(.*?)\}\);",
                     source, re.S)
    assert bloc, "la table des bornes n'est plus reconnaissable dans le portage"

    js = {}
    for nom, basse, haute in re.findall(
        r"^\s*(\w+):\s*\[([\d.]+),\s*([\d.]+|null)\]", bloc.group(1), re.M
    ):
        js[nom] = (float(basse), None if haute == "null" else float(haute))

    assert js == dict(BORNES_ASSIETTE), (
        "les tranches divergent entre le modèle et son portage : "
        f"seulement en Python {sorted(set(BORNES_ASSIETTE) - set(js))}, "
        f"seulement en JavaScript {sorted(set(js) - set(BORNES_ASSIETTE))}"
    )


def test_le_README_dit_le_vrai_poids_du_paquet():
    """« 165 Ko compressés (621 Ko brut) » est une mesure, pas une impression.

    Elle annonçait 277 Ko compressés et 1 Mo brut, pour un paquet qui en fait
    165 et 621 : la phrase avait été écrite une fois, et les données avaient
    changé depuis. C'est le sort de tout chiffre recopié que rien ne recoupe.

    La tolérance est large — cinq pour cent —, parce que le README arrondit et
    qu'il n'a pas à être réécrit pour un kilo-octet ; elle est assez serrée pour
    attraper un doublement.
    """
    import gzip
    import re
    from pathlib import Path

    racine = Path(__file__).resolve().parents[1]
    paquet = (racine / "moteur" / "donnees.json").read_bytes()
    brut = len(paquet) / 1024
    compresse = len(gzip.compress(paquet)) / 1024

    annonce = re.search(r"transfère (\d+) Ko compressés \((\d+) Ko brut\)",
                        (racine / "README.md").read_text(encoding="utf-8"))
    assert annonce, "le README ne dit plus ce que le premier chargement transfère"
    dit_compresse, dit_brut = (int(annonce.group(1)), int(annonce.group(2)))

    for dit, mesure, quoi in ((dit_compresse, compresse, "compressé"),
                              (dit_brut, brut, "brut")):
        assert abs(dit - mesure) / mesure < 0.05, (
            f"le README annonce {dit} Ko {quoi}, le paquet en fait "
            f"{mesure:.0f} — écart de {abs(dit - mesure) / mesure:.0%}"
        )
