"""Tests du contenu du site.

Le site tourne entièrement dans le navigateur ; ce qu'il affiche est produit ici
par :mod:`retraite_notionnelle.web.pages`, qui ne dépend que de la bibliothèque
standard et sert de référence au portage JavaScript.
"""

from __future__ import annotations

import html
import itertools
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
    _date_en_clair,
    AGE_DEBUT_MINIMAL,
    AGE_LIQUIDATION_MAXIMAL,
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
    PAGES_AGREGEES,
    PAS_MULTIPLE,
    PROFILS,
    PROJECTIONS,
    RELEVE_MAXIMUM,
    SANS_EMPLOI,
    TABLES,
    TITRES,
    Contexte,
    ErreurSaisie,
    Saisie,
    _champs_modelisation,
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
    return Contexte().echelle(Saisie(montants="brut"))


@pytest.fixture(scope="module")
def page(contexte):
    """Rend une page entière, comme le fait ``index.html`` dans le navigateur.

    Le site n'assemble jamais autre chose : l'en-tête, le corps rendu, le pied.
    """
    # Le rendu est mémorisé : une trentaine de tests demandent la même page,
    # et `/cout` coûtait trois secondes et demie à chaque fois. Rendre deux
    # fois la même adresse donne la même chaîne — et une chaîne ne se modifie
    # pas, donc la partager ne peut pas faire communiquer deux tests.
    memo: dict[tuple, str] = {}

    def rendu(chemin: str = "/simuler", **parametres: object) -> str:
        arguments = {nom: str(valeur) for nom, valeur in parametres.items()}
        cle = (chemin, tuple(sorted(arguments.items())))
        if cle not in memo:
            _, corps = rendre(contexte, chemin, arguments)
            memo[cle] = g.entete(chemin) + corps + g.pied()
        return memo[cle]

    return rendu


# -- pages -------------------------------------------------------------------


@pytest.mark.parametrize("chemin", ["/", "/simuler", "/cas-types", "/methode", "/donnees"])
def test_les_pages_repondent(page, chemin):
    texte = page(chemin)
    assert "Retraite à comptes notionnels" in texte


def test_accueil_sans_parametres_ne_calcule_rien(page):
    """Une visite nue montre le formulaire, pas des résultats surgis de nulle part."""
    texte = page("/simuler")
    # Le titre de la page est devenu son affiche ; la carte qui porte les
    # champs s'intitule « Votre carrière ».
    assert "Votre carrière, calculée" in texte
    assert 'name="naissance"' in texte
    assert "Résultats" not in texte


def test_simulation_affiche_les_quatre_systemes(page):
    """Les quatre systèmes comparés, nommés par leur assiette.

    Les libellés ont changé à la refonte : « Notionnel rétroactif » ne disait
    rien à qui n'avait pas lu la page Méthode. Ce qui distingue un système de
    l'autre est maintenant dans son titre — l'assiette —, et depuis quand la
    carrière est recalculée est dans la glose.
    """
    texte = page("/simuler", naissance=1960, statut="agent_sncf",
                 debut=20, liquidation=52)
    for attendu in ("1. Système de répartition actuel",
                    "2. Compte notionnel, part salariale seule",
                    "3. Compte notionnel, part salariale + patronale",
                    "4. La proposition du Parti libéral français",
                    "recalculée depuis 1941", "Résultats"):
        assert attendu in texte


def test_la_saisie_est_reinjectee_dans_le_formulaire(page):
    """L'adresse porte les paramètres : la page doit être rechargeable telle quelle.

    Les âges d'une adresse ancienne reviennent en dates, puisque c'est ce que le
    formulaire demande depuis qu'il porte des calendriers : né en 1955, entré à
    dix-huit ans, parti à cinquante-cinq.
    """
    texte = page("/simuler", naissance=1955, statut="mineur",
                 debut=18, liquidation=55)
    assert 'id="naissance" name="naissance" value="1955-01-01"' in texte
    assert 'id="debut" name="debut" value="1973-01-01"' in texte
    assert 'id="liquidation" name="liquidation" value="2010-01-01"' in texte
    assert '<option value="mineur" selected data-fermeture="2010-09">' in texte


def test_le_calendrier_se_lit_et_se_rend(page):
    """Une carrière datée au mois : le formulaire la rend telle qu'elle a été
    saisie, et l'âge qu'elle fait s'écrit sous le champ."""
    texte = page("/simuler", naissance="1962-03-15", debut="1984-09",
                 liquidation="2026-07")
    assert 'id="naissance" name="naissance" value="1962-03-15"' in texte
    assert 'id="debut" name="debut" value="1984-09-01"' in texte
    assert 'id="liquidation" name="liquidation" value="2026-07-01"' in texte
    assert "soit 22 ans et 6 mois" in texte
    assert "soit 64 ans et 4 mois" in texte


def test_saisie_invalide_affiche_un_message_et_pas_de_trace(page):
    texte = page("/simuler", naissance=1700)
    assert "Saisie refusée" in texte
    assert "Traceback" not in texte


def test_carriere_impossible_est_signalee_sans_planter(page):
    texte = page("/simuler", naissance=1990, statut="salarie_prive_non_cadre",
                 debut=30, liquidation=45)
    assert "Traceback" not in texte


#: Le titre de la décomposition tel qu'il s'écrit dans la page : il y est le
#: résumé d'une section repliée, où les apostrophes sont échappées.
DECOMPOSITION = html.escape("D'où vient l'écart")


def test_la_decomposition_par_regle_d_indexation_est_presente(page):
    """Le point le plus contre-intuitif du modèle doit être exposé, pas caché."""
    texte = page("/simuler", naissance=1960, statut="salarie_prive_non_cadre",
                 debut=20, liquidation=62)
    assert DECOMPOSITION in texte
    assert "Triple lock inversé, tout en nominal" in texte
    assert texte.count("Rendement cumulé") >= 1


def test_pas_de_decomposition_si_l_indexation_est_deja_choisie(page):
    texte = page("/simuler", naissance=1960, statut="salarie_prive_non_cadre",
                 debut=20, liquidation=62, indexation="prix")
    assert DECOMPOSITION not in texte


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


def test_un_statut_ferme_est_refuse_a_qui_y_entre_apres_la_fermeture(contexte):
    """Un jeune d'aujourd'hui ne peut pas se déclarer mineur.

    Le régime des mines est fermé aux recrutés depuis le 1er septembre 2010
    (décret n° 2010-975). Le routage le savait et envoyait ce mineur-là au
    régime général, en silence : la page affichait « Mineur » au-dessus d'une
    pension de salarié du privé. Le refus dit la date d'entrée, la date de
    fermeture et le statut de droit commun qui porte le même calcul.
    """
    saisie = Saisie.depuis_requete(
        {"naissance": "2000", "statut": "mineur", "debut": "20", "liquidation": "64"}
    )
    with pytest.raises(ErreurSaisie) as refus:
        contexte.simuler(saisie)
    message = str(refus.value)
    assert "« Mineur »" in message
    assert "depuis septembre 2010" in message
    assert "commence en janvier 2020" in message
    assert "« Salarié du secteur privé, non cadre »" in message

    # Le même statut, pour qui y était avant : accepté, et au régime des mines.
    saisie = Saisie.depuis_requete(
        {"naissance": "1980", "statut": "mineur", "debut": "20", "liquidation": "64"}
    )
    regimes = {p.regime for p in contexte.simuler(saisie).actuel.pensions_par_regime}
    assert "mines" in regimes


def test_la_fermeture_se_lit_au_mois_et_sur_la_date_d_entree(contexte):
    """La loi ferme la RATP « aux recrutés à compter du 1er septembre 2023 ».

    Né en décembre 2001, entré à vingt et un ans : décembre 2022, avant la
    fermeture, régime spécial. Un métier commencé en octobre 2022 n'a sa
    première LIGNE qu'en 2023 — l'année d'un changement revient au métier qui
    en occupe le plus de mois — et n'est pas recruté après la fermeture pour
    autant : c'est la date d'entrée qui décide, non la première ligne.
    """
    def regimes(champs):
        return {p.regime for p in contexte.simuler(
            Saisie.depuis_requete(champs)).actuel.pensions_par_regime}

    avant = {"naissance": "2001", "naissance_mois": "12", "statut": "agent_ratp",
             "debut": "21", "liquidation": "64"}
    assert "ratp" in regimes(avant)
    with pytest.raises(ErreurSaisie, match="septembre 2023"):
        regimes({**avant, "naissance": "2002", "naissance_mois": "9"})

    second_metier = {"naissance": "1975", "naissance_mois": "10",
                     "statut": "salarie_prive_non_cadre", "debut": "21",
                     "liquidation": "64", "metier2_debut": "47",
                     "metier2_statut": "agent_ratp", "metier2_salaire": "1"}
    assert "ratp" in regimes(second_metier)
    with pytest.raises(ErreurSaisie, match=r"Métier n° 2 : le statut"):
        regimes({**second_metier, "metier2_debut": "48"})


def test_le_menu_des_statuts_est_date(page, contexte):
    """Chaque statut dit entre quelles dates il se déclare, et le menu grise
    ceux que l'entrée saisie ferme — sauf la sélection, qu'un navigateur
    n'enverrait pas si elle était désactivée."""
    texte = page("/simuler", naissance=1975, statut="salarie_prive_non_cadre",
                 debut=21, liquidation=64)
    assert ">Mineur (recrutés avant septembre 2010)<" in texte
    assert ">Artiste-auteur (écrivain, illustrateur, photographe…) (depuis 1977)<" in texte
    assert ">Salarié du secteur privé, non cadre<" in texte
    # Entré en 1996 : la SEITA (fermée en 1981) est grisée, les mines non.
    assert '<option value="agent_seita" disabled data-fermeture="1981-01">' in texte
    assert '<option value="mineur" data-fermeture="2010-09">' in texte
    # La sélection reste choisissable, même fermée à cette date.
    texte = page("/simuler", naissance=1975, statut="agent_seita", debut=21, liquidation=64)
    assert '<option value="agent_seita" selected data-fermeture="1981-01">' in texte
    assert "Saisie refusée" in texte

    # Un statut dont les régimes changent sans qu'il se ferme n'est pas daté,
    # et se déclare à toute date : le libéral non réglementé installé en 2020
    # est au régime général et au RCI, celui de 2010 à la Cipav.
    assert (">Profession libérale non réglementée (consultant, formateur, coach, "
            "développeur…) (depuis 1949)<") in texte
    def regimes(champs):
        return {p.regime for p in contexte.simuler(
            Saisie.depuis_requete(champs)).actuel.pensions_par_regime}
    assert regimes({"naissance": "1995", "statut": "liberal_non_reglemente",
                    "debut": "25", "liquidation": "64"}) >= {"regime_general", "rci"}
    assert regimes({"naissance": "1985", "statut": "liberal_non_reglemente",
                    "debut": "25", "liquidation": "64"}) >= {"cnavpl", "cipav_complementaire"}

    dates = {s["code"]: s for s in statuts(contexte)}
    assert dates["mineur"]["fermeture_entrants"] == "2010-09"
    assert dates["mineur"]["releve_par"] == "salarie_prive_non_cadre"
    assert dates["artiste_auteur"]["ouverture"] == 1977
    assert dates["salarie_prive_non_cadre"]["fermeture_entrants"] is None


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
    formulaire = rendre(contexte, "/simuler", {})[1]
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


def test_les_bornes_des_calendriers_sont_opposables_hors_du_navigateur(contexte):
    """Même exigence pour les dates que pour les nombres.

    Un calendrier s'ouvre sur les seules dates que le modèle accepte — « min »
    et « max » sont posés depuis la date de naissance saisie —, mais une adresse
    forgée à la main ne passe par aucun calendrier. Ce test relit les champs
    date du formulaire rendu et vérifie que le mois d'à côté est refusé.
    """
    formulaire = rendre(contexte, "/simuler", {})[1]
    champs = re.findall(
        r'<input type="date" id="([a-z_0-9]+)"[^>]*?'
        r' min="(\d{4}-\d{2})-\d{2}" max="(\d{4}-\d{2})-\d{2}"',
        formulaire,
    )
    assert champs, "le formulaire ne déclare plus aucun calendrier"
    for nom, minimum, maximum in champs:
        for borne, pas in ((minimum, -1), (maximum, +1)):
            annee, mois = (int(part) for part in borne.split("-"))
            rang = annee * 12 + mois - 1 + pas
            dehors = f"{rang // 12:04d}-{rang % 12 + 1:02d}"
            # Une ligne de métier ne se lit qu'entière : sans statut, elle est
            # refusée pour cette raison-là, et ne dirait rien de sa borne.
            requete = {nom: dehors}
            if nom.startswith("metier"):
                requete[f"{nom.split('_')[0]}_statut"] = "artisan"
            with pytest.raises(ErreurSaisie, match=r"."):
                Saisie.depuis_requete(requete)


def test_les_adresses_d_avant_le_calendrier_valent_toujours():
    """Le formulaire demande des dates ; les adresses déjà partagées portaient
    des âges, en deux champs. Les deux doivent décrire la même carrière, et se
    réécrire de la même façon — sans quoi tout lien envoyé mentirait."""
    ancienne = Saisie.depuis_requete({
        "naissance": "1975", "naissance_mois": "9",
        "debut": "22", "debut_mois": "3",
        "liquidation": "64", "liquidation_mois": "7",
    })
    nouvelle = Saisie.depuis_requete({
        "naissance": "1975-09-01", "debut": "1997-12", "liquidation": "2040-04",
    })
    assert ancienne.requete() == nouvelle.requete()
    assert nouvelle.mois_de(nouvelle.debut) == "1997-12"
    assert nouvelle.mois_de(nouvelle.liquidation) == "2040-04"
    # Et l'âge décimal d'avant les mois, que personne n'écrit plus mais que
    # certaines adresses portent encore.
    assert Saisie.depuis_requete({"liquidation": "64.5"}).liquidation == 64.5


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
    # En brut : ce test mesure la conversion euros → multiple, et le mode
    # net y ajouterait la conversion net → brut, qui a son propre test.
    saisie = Saisie.depuis_requete({"unite_revenu": "euros_mois",
                                    "salaire": "2500", "montants": "brut"})
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
        "unite_revenu": "euros_mois", "salaire": "2500", "montants": "brut",
        "metier2_debut": "40", "metier2_statut": "artisan",
        "metier2_salaire": "5000",
    })
    premier, second = saisie.niveaux(echelle)
    assert second == pytest.approx(2 * premier)


def _lien_de_bascule(contexte, parametres):
    """L'adresse que porte le lien « saisir plutôt … », lue comme une requête."""
    corps = rendre(contexte, "/simuler", parametres)[1]
    # La bascule d'unité écrit ses deux états ; celui qui s'applique n'est pas
    # un lien. On cherche donc la branche PROPOSÉE, dans la bascule « Unité ».
    bloc = re.search(r'<div class="bascule" role="group" aria-label="Unité">'
                     r'.*?</div>', corps, re.S)
    assert bloc, "le formulaire ne porte plus de bascule d'unité"
    lien = re.search(r'<a href="#/simuler\?([^"]*)">([^<]*)</a>', bloc.group(0))
    assert lien, "la bascule d'unité ne propose aucun autre état"
    return dict(parse_qsl(html.unescape(lien.group(1)))), html.unescape(lien.group(2))


def test_la_bascule_d_unite_convertit_les_montants(contexte):
    """Le piège que ce lien existe pour éviter.

    Un menu HTML ne convertit rien : basculer l'unité sans retoucher le nombre
    aurait fait lire « 3 500 » comme 3 500 fois le salaire moyen, et la page
    aurait refusé la saisie au lieu de la traduire. Le lien, lui, porte les
    montants déjà convertis.
    """
    suite, libelle = _lien_de_bascule(
        contexte, {"naissance": "1975", "montants": "brut"})
    assert libelle == "× salaire moyen"
    assert suite["unite_revenu"] == "moyen"
    # 3 500 € par mois, à l'échelle d'un salaire moyen de 3 475 € : environ 1.
    assert float(suite["salaire"]) == pytest.approx(1.0, abs=0.05)
    # Et la page qui suit ce lien calcule, au lieu de refuser.
    corps = rendre(contexte, "/simuler", suite)[1]
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
    # En brut : les bornes que le message nomme sont des bornes de BRUT,
    # puisque c'est l'unité du modèle. En net, le nombre saisi est converti
    # avant d'être borné, et le test porterait sur autre chose.
    echelle = contexte.echelle(Saisie(montants="brut"))
    for borne in (round(echelle.mensuel(0.1)), round(echelle.mensuel(10))):
        saisie = Saisie.depuis_requete({
            "unite_revenu": "euros_mois", "salaire": str(borne),
            "montants": "brut",
        })
        saisie.parcours(echelle)  # ne doit pas lever


def test_la_bascule_convertit_tous_les_metiers(contexte):
    suite, _ = _lien_de_bascule(contexte, {
        "naissance": "1975", "unite_revenu": "euros_mois", "salaire": "2900",
        "montants": "brut",
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
        corps = rendre(contexte, "/simuler", suite)[1]
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
        corps = rendre(contexte, "/simuler", {"unite_revenu": unite, "salaire": salaire})[1]
        assert f'<input type="hidden" name="unite_revenu" value="{unite}">' in corps


def test_un_refus_garde_l_unite_de_saisie(contexte):
    """Une faute de frappe ailleurs ne doit pas changer d'unité sous les doigts."""
    corps = rendre(contexte, "/simuler", {
        "naissance": "1700", "unite_revenu": "moyen", "salaire": "1.2",
    })[1]
    assert "Saisie refusée" in corps
    assert '<input type="hidden" name="unite_revenu" value="moyen">' in corps
    assert "Niveau de revenu" in corps


def test_le_formulaire_dit_brut_ou_net_et_donne_l_echelle(contexte):
    """La question posée — « brut ou net ? » — trouve sa réponse sur le champ.

    Et elle la trouve DANS LE MODE COURANT : demander un « revenu brut » sous
    une bascule qui annonce le net ferait taper l'un pour l'autre, et le modèle
    lirait sans broncher un net comme un brut. Les repères chiffrés suivent
    aussi — un SMIC net n'est pas un SMIC brut.
    """
    for mode, ligne in (("brut", "la ligne « brut » de la fiche de paie"),
                        ("net", "la ligne « net à payer » de la fiche de paie")):
        _, corps = rendre(contexte, "/simuler", {"montants": mode})
        assert f"Revenu {mode} mensuel" in corps
        assert ligne in corps
        # L'échelle est chiffrée : « 1 = salaire moyen » ne dit rien à personne.
        assert "SMIC" in corps and "salaire moyen" in corps
        # Et pas de « plafond » sous le champ : le mot s'y lit comme le maximum
        # que le champ accepte, ce que le plafond de la Sécurité sociale n'est pas.
        assert not re.search(r"plafond [\d\u202f]+\u202f€", corps)

    # Et les deux repères sont bien convertis, non recopiés : le SMIC net d'un
    # salarié du privé vaut environ 79 % de son brut.
    _, brut = rendre(contexte, "/simuler", {"montants": "brut"})
    _, net = rendre(contexte, "/simuler", {"montants": "net"})
    def smic(corps):
        return float(re.search(r"SMIC ([\d\u202f]+)\u202f€", corps)
                     .group(1).replace("\u202f", ""))
    assert 0.75 < smic(net) / smic(brut) < 0.85


def test_le_multiple_est_traduit_en_euros(contexte):
    _, corps = rendre(contexte, "/simuler", {"unite_revenu": "moyen", "salaire": "1"})
    assert "1 = salaire moyen, soit" in corps


# -- le relevé de carrière ---------------------------------------------------


def _releve(premiere: int, derniere: int,
            statut: str = "salarie_prive_non_cadre") -> str:
    """Un relevé plausible, une ligne par année, quatre trimestres chacune."""
    return ",".join(
        f"{annee}:{statut}:{14000 + 500 * (annee - premiere)}:4"
        for annee in range(premiere, derniere + 1)
    )


def test_le_releve_est_lu_ligne_a_ligne():
    saisie = Saisie.depuis_requete({
        "naissance": "1975", "liquidation": "64",
        "releve": "1998:salarie_prive_non_cadre:14200:4\n"
                  "1999:salarie_prive_cadre:19800",
    })
    assert saisie.releve_actif
    lignes = saisie.releve_analyse()
    assert [(l.annee, l.affiliation, l.revenu, l.trimestres) for l in lignes] == [
        (1998, "salarie_prive_non_cadre", 14200.0, 4),
        # Le quatrième champ manque : le modèle déduira les trimestres du
        # montant cotisé, comme il le fait d'une carrière paramétrique.
        (1999, "salarie_prive_cadre", 19800.0, None),
    ]


def test_le_releve_remplace_la_carriere_parametrique(contexte):
    """Deux simulations, mêmes bornes : le relevé n'emprunte rien au profil."""
    commun = {"naissance": "1975", "liquidation": "64", "debut": "23",
              "statut": "salarie_prive_non_cadre", "unite_revenu": "moyen",
              "salaire": "1"}
    lue = contexte.simuler(Saisie.depuis_requete({
        **commun, "releve": _releve(1998, 2038)}))
    reconstituee = contexte.simuler(Saisie.depuis_requete(commun))
    assert lue.carriere.annee_liquidation == reconstituee.carriere.annee_liquidation
    assert [ligne.annee for ligne in lue.carriere.lignes] == list(range(1998, 2039))
    # Les revenus sont ceux du relevé, en euros de chaque année, et non ceux
    # qu'un niveau relatif et un profil auraient fabriqués.
    assert lue.carriere.ligne(1998).revenu == 14000.0
    assert lue.carriere.ligne(1998).revenu != reconstituee.carriere.ligne(1998).revenu


def test_les_trimestres_declares_l_emportent_sur_le_montant(contexte):
    """Le relevé fait foi : un temps partiel ne se lit sur aucun salaire."""
    saisie = Saisie.depuis_requete({
        "naissance": "1975", "liquidation": "64",
        "releve": "2000:salarie_prive_non_cadre:30000:2",
    })
    carriere = contexte.simuler(saisie).carriere
    assert carriere.ligne(2000).trimestres_valides == 2


def test_l_annee_du_depart_est_tronquee_par_la_liquidation(contexte):
    """Le relevé donne l'année ; la date de liquidation dit jusqu'où elle compte."""
    saisie = Saisie.depuis_requete({
        "naissance": "1975", "liquidation": "64", "liquidation_mois": "7",
        "releve": _releve(1998, 2039),
    })
    carriere = contexte.simuler(saisie).carriere
    assert carriere.ligne(2038).fraction_annee == 1.0
    # Départ à 64 ans et 7 mois, donc au 1er août 2039 : sept mois travaillés.
    assert carriere.ligne(2039).fraction_annee == 7 / 12
    # Sept mois : deux trimestres civils au plus, quoi qu'en dise la ligne du
    # relevé, qui en déclare quatre.
    assert carriere.ligne(2039).trimestres_valides == 2


def test_les_interruptions_valent_encore_sur_un_releve(contexte):
    """Le relevé ne dit pas la NATURE de l'année ; le champ des motifs, si."""
    saisie = Saisie.depuis_requete({
        "naissance": "1975", "liquidation": "64",
        "releve": _releve(1998, 2038),
        "interruptions": "2005:2006:chomage_indemnise",
    })
    carriere = contexte.simuler(saisie).carriere
    chomage = carriere.ligne(2005)
    assert chomage.type_periode == "chomage_indemnise"
    assert not chomage.cotisations_versees
    assert chomage.revenu == 0.0
    # Le revenu de la ligne devient le salaire de référence sur lequel les
    # régimes complémentaires continuent d'acquérir des points.
    assert chomage.revenu_reference == 17500.0
    assert carriere.ligne(2007).cotisations_versees


def test_un_releve_vide_laisse_la_carriere_parametrique():
    assert not Saisie.depuis_requete({"releve": "   "}).releve_actif


@pytest.mark.parametrize("ligne", [
    "2005:salarie_prive_non_cadre",          # trois champs exigés
    "2005:salarie_prive_non_cadre:1:2:3",    # quatre au plus
    "deux-mille:salarie_prive_non_cadre:1:4",
    "2005::24000:4",                         # statut manquant
    "2005:salarie_prive_non_cadre:abc:4",
    "2005:salarie_prive_non_cadre:-1:4",
    "2005:salarie_prive_non_cadre:24000:5",
    "2005:salarie_prive_non_cadre:24000:-1",
    "2005:salarie_prive_non_cadre:24000:4, 2005:artisan:9000:4",
    f"{ANNEE_CARRIERE_MINIMALE - 1}:salarie_prive_non_cadre:1:4",
    f"{ANNEE_CARRIERE_MAXIMALE + 1}:salarie_prive_non_cadre:1:4",
    "1970:salarie_prive_non_cadre:1:4",      # avant les quatorze ans de l'assuré
    "2039:salarie_prive_non_cadre:1:4",      # après le départ à la retraite
])
def test_une_ligne_de_releve_fautive_est_refusee(ligne):
    saisie = Saisie.depuis_requete({
        "naissance": "1975", "liquidation": "64", "releve": ligne,
    })
    with pytest.raises(ErreurSaisie):
        saisie.releve_analyse()


def test_un_releve_demesure_est_refuse():
    """L'adresse EST la saisie : un relevé forgé dans un lien figeait l'onglet.

    Le refus tombe sur le NOMBRE de lignes, avant que la première ne soit lue :
    c'est ce qui le rend gratuit. Compter les lignes analysées ferait payer au
    lecteur tout le relevé qu'on voulait justement lui épargner.
    """
    lignes = ",".join(
        f"{annee}:salarie_prive_non_cadre:100:4"
        for annee in range(1930, 1930 + RELEVE_MAXIMUM + 1)
    )
    saisie = Saisie.depuis_requete({
        "naissance": "1975", "liquidation": "64", "releve": lignes,
    })
    with pytest.raises(ErreurSaisie, match="au plus"):
        saisie.releve_analyse()


def test_aucune_carriere_n_atteint_la_borne_du_releve():
    """La borne du relevé est au-dessus de ce que la fenêtre des âges permet.

    Une carrière tient entre l'âge de début minimal et l'âge de liquidation
    maximal ; une année ne s'y déclare qu'une fois. La borne doit rester
    au-dessus de ce compte, faute de quoi elle refuserait une carrière que le
    reste du formulaire accepte.
    """
    assert RELEVE_MAXIMUM > AGE_LIQUIDATION_MAXIMAL - AGE_DEBUT_MINIMAL


def test_un_statut_ferme_est_refuse_aussi_sur_un_releve(contexte):
    """Le refus parle d'années déclarées, non d'un « métier n° 2 » inexistant."""
    saisie = Saisie.depuis_requete({
        "naissance": "1975", "liquidation": "64",
        "releve": "2015:mineur:24000:4",
    })
    with pytest.raises(ErreurSaisie, match="première année déclarée"):
        contexte.simuler(saisie)


def test_un_statut_inconnu_du_releve_est_refuse(contexte):
    saisie = Saisie.depuis_requete({
        "naissance": "1975", "liquidation": "64",
        "releve": "2005:cosmonaute:24000:4",
    })
    with pytest.raises(ErreurSaisie, match="cosmonaute"):
        contexte.simuler(saisie)


def test_le_releve_voyage_dans_l_adresse():
    """Il est un paramètre comme les autres : un lien décrit la carrière entière."""
    saisie = Saisie.depuis_requete({"releve": _releve(2000, 2002)})
    parametres = dict(parse_qsl(saisie.requete()))
    assert parametres["releve"] == _releve(2000, 2002)
    assert Saisie.depuis_requete(parametres).releve == saisie.releve


def test_la_page_dit_que_la_carriere_a_ete_lue(page):
    texte = page("/simuler", naissance=1975, liquidation=64, releve=_releve(1998, 2038))
    assert "lue sur un relevé" in texte
    assert "41 années de 1998 à 2038" in texte
    # Le dépliant est ouvert : sinon l'adresse porterait une carrière que la
    # page ne montrerait pas.
    assert '<details class="releve" open>' in texte


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
    with pytest.raises(ErreurSaisie, match="date à laquelle il commence"):
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
    """C'est ainsi qu'on ajoute un métier : sans une ligne de JavaScript.

    La ligne de plus est REPLIÉE : elle ne coûte qu'un résumé tant qu'on ne
    veut pas s'en servir. Les périodes déjà décrites, elles, restent des
    groupes de champs, et leur rang en est la légende.
    """
    vierge = page("/simuler")
    assert vierge.count('<legend class="rang">') == 1
    assert vierge.count("<span>Ajouter une période") == 1
    assert 'name="metier2_debut" value=""' in vierge

    rempli = page("/simuler", naissance=1975, metier2_debut=40, metier2_statut="artisan")
    assert rempli.count('<legend class="rang">') == 2
    assert rempli.count("<span>Ajouter une période") == 1
    assert 'name="metier3_debut" value=""' in rempli


def test_le_formulaire_s_arrete_au_nombre_maximal_de_metiers(page):
    champs = {"naissance": 1960, "liquidation": 64}
    for rang in range(2, METIERS_MAXIMUM + 1):
        champs[f"metier{rang}_debut"] = 30 + rang
        champs[f"metier{rang}_statut"] = "artisan"
    texte = page("/simuler", **champs)
    assert texte.count('<legend class="rang">') == METIERS_MAXIMUM
    assert "<span>Ajouter une période" not in texte
    assert f'name="metier{METIERS_MAXIMUM + 1}_debut"' not in texte


def test_la_page_recapitule_le_parcours(page):
    texte = page("/simuler", naissance=1975, debut=21, liquidation=64,
                 metier2_debut=42, metier2_statut="artisan")
    assert "Carrière en 2 périodes" in texte
    assert "Artisan de 42 ans à 64 ans" in texte


def test_les_motifs_du_menu_existent_dans_la_table_des_periodes():
    """Le menu ne peut pas proposer un motif que le moteur ne connaîtrait pas.

    ``_ligne_annuelle`` rabat tout motif inconnu sur « sans activité » : un code
    mal orthographié dans le formulaire validerait zéro trimestre au lieu de
    quatre, et changerait la pension sans un mot.
    """
    table = charger_periodes_non_travaillees(Contexte().base.racine_donnees)
    for code, _ in SANS_EMPLOI:
        assert code in table, f"motif proposé par le formulaire et absent de la table : {code}"


def test_une_periode_sans_emploi_vaut_l_interruption_qu_elle_decrit(contexte):
    """Une ligne « sans emploi » et le champ « Interruptions » disent la même
    chose : c'est le même chemin dans le moteur, et les chiffres doivent l'être
    aussi, jusqu'au dernier."""
    base = {"naissance": "1962-03-15", "debut": "1984-09", "liquidation": "2026-07",
            "unite_revenu": "euros_mois", "salaire": "2600"}
    par_ligne = contexte.simuler(Saisie.depuis_requete({
        **base, "metier2_debut": "2020-03", "metier2_statut": "chomage_indemnise",
    })).dictionnaire()
    par_champ = contexte.simuler(Saisie.depuis_requete({
        **base, "interruptions": "2020:2026:chomage_indemnise",
    })).dictionnaire()
    assert par_ligne == par_champ


def test_la_fin_d_activite_retire_les_annees_qu_elle_couvre(contexte):
    """Le défaut que la ligne comble : sans elle, le calcul suppose qu'on a
    travaillé jusqu'au mois du départ."""
    base = {"naissance": "1962-03-15", "debut": "1984-09", "liquidation": "2026-07",
            "unite_revenu": "euros_mois", "salaire": "2600"}
    continu = contexte.simuler(Saisie.depuis_requete(base))
    arrete = contexte.simuler(Saisie.depuis_requete({
        **base, "metier2_debut": "2020-03", "metier2_statut": "sans_activite",
    }))
    assert arrete.actuel.pension_mensuelle < continu.actuel.pension_mensuelle
    assert (arrete.notionnel_retroactif.pension_mensuelle
            < continu.notionnel_retroactif.pension_mensuelle)
    # Six années de moins au compte : celles que la ligne couvre.
    cotisees = lambda comparaison: sum(  # noqa: E731
        1 for ligne in comparaison.carriere.lignes if ligne.cotise
    )
    assert cotisees(continu) - cotisees(arrete) == 7


@pytest.mark.parametrize("debut, premiere_annee_creuse", [
    # Sept mois sans emploi sur douze : l'année revient à ce qui l'occupe le
    # plus, c'est-à-dire au creux.
    ("2020-06", 2020),
    # Six mois partout : à égalité, l'année reste travaillée.
    ("2020-07", 2021),
    ("2020-08", 2021),
])
def test_l_annee_ou_l_activite_s_arrete_revient_au_plus_grand_nombre_de_mois(
    debut, premiere_annee_creuse,
):
    """La même convention que pour un changement de métier : le moteur ne
    connaît qu'un statut par année civile, et c'est le plus long qui l'emporte."""
    saisie = Saisie.depuis_requete({
        "naissance": "1962-01-01", "debut": "1984-09", "liquidation": "2026-07",
        "metier2_debut": debut, "metier2_statut": "sans_activite",
    })
    assert min(saisie.interruptions_de_carriere()) == premiere_annee_creuse


def test_une_periode_sans_emploi_ne_demande_pas_de_revenu(page):
    """Elle n'en paie aucun : le champ disparaît plutôt que de demander un
    nombre dont rien ne serait fait."""
    avec_metier = page("/simuler", naissance="1975-01-01", debut="1996-01",
                       liquidation="2039-01", metier2_debut="2020-01",
                       metier2_statut="artisan")
    assert 'name="metier2_salaire"' in avec_metier
    sans_emploi = page("/simuler", naissance="1975-01-01", debut="1996-01",
                       liquidation="2039-01", metier2_debut="2020-01",
                       metier2_statut="chomage_indemnise")
    assert 'name="metier2_salaire"' not in sans_emploi
    assert "Deuxième période, sans emploi" in sans_emploi


def test_aucun_menu_ne_propose_deux_fois_la_meme_valeur(page):
    """Deux options de même valeur dans un menu, c'est une saisie qui ne revient
    pas : le navigateur choisit la première, et la seconde est inatteignable.
    Le risque est né avec les périodes sans emploi, dont « sans activité » est
    AUSSI une affiliation."""
    texte = page("/simuler")
    for menu in re.findall(r"<select\b.*?</select>", texte, re.S):
        valeurs = re.findall(r'<option value="([^"]*)"', menu)
        doublons = {valeur for valeur in valeurs if valeurs.count(valeur) > 1}
        assert not doublons, f"valeurs proposées deux fois : {doublons}"


def test_le_premier_metier_reste_une_affiliation(contexte):
    """« sans_activite » est aussi une affiliation — celle de qui n'a jamais
    travaillé —, et les adresses qui la portent en premier métier ne doivent pas
    changer de sens."""
    saisie = Saisie.depuis_requete({"statut": "sans_activite"})
    assert [ligne.sans_emploi for ligne in saisie.lignes_carriere] == [False]
    assert saisie.interruptions_de_carriere() == {}
    assert [metier.affiliation for metier in saisie.parcours(_echelle())] == [
        "sans_activite"
    ]
    # Et le menu de la première ligne la propose toujours sous son nom de
    # statut, quand celui des lignes suivantes la range avec les creux.
    texte = rendre(contexte, "/simuler", {})[1]
    premier = texte.split('name="metier2_statut"')[0]
    assert '<option value="sans_activite">Sans activité professionnelle' in premier


def test_la_page_recapitule_une_periode_sans_emploi(page):
    """Une ligne peut ne pas être un métier : le résumé la nomme comme les
    autres, et dit à quel âge l'activité s'est arrêtée."""
    texte = page("/simuler", naissance=1975, debut=21, liquidation=64,
                 metier2_debut=58, metier2_statut="chomage_indemnise")
    assert "Carrière en 2 périodes" in texte
    assert "chômage indemnisé de 58 ans à 64 ans" in texte


def test_requete_reconstruit_les_metiers():
    requete = Saisie.depuis_requete({
        "metier2_debut": "40", "metier2_statut": "artisan",
        "metier2_salaire": "1.5",
    }).requete()
    # Quarante ans, pour qui est né en janvier 1975, c'est janvier 2015 :
    # l'adresse porte la date, le formulaire la rend au calendrier.
    assert "metier2_debut=2015-01" in requete
    assert "metier2_statut=artisan" in requete
    assert "metier2_salaire=1.5" in requete
    assert "metier3_debut" not in requete


def test_requete_reconstruit_les_parametres():
    requete = Saisie(naissance=1960, statut="mineur").requete()
    assert "naissance=1960" in requete
    assert "statut=mineur" in requete


def test_la_situation_de_foyer_traverse_l_adresse_et_le_modele():
    """« foyer=couple » retire l'allocation d'isolement du scénario 6, et rien
    d'autre : l'adresse la porte, le formulaire la relit, le modèle la reçoit."""
    from retraite_notionnelle.config import Parametres, SituationFoyer

    saisie = Saisie.depuis_requete({"foyer": "couple"})
    assert saisie.foyer == "couple"
    assert "foyer=couple" in saisie.requete()
    assert saisie.parametres(Parametres()).situation_foyer is SituationFoyer.COUPLE
    assert Saisie.depuis_requete({"foyer": "n'importe quoi"}).foyer == "seul"


def test_la_page_detaille_la_garantie_vieillesse_du_scenario_6(page):
    """À 65 ans et à petit salaire, la garantie est servie et la page dit
    combien l'impôt en finance ; à 62 ans, elle dit pourquoi rien n'est servi."""
    texte = page("/simuler", naissance=1958, liquidation=65, salaire=1500,
                 unite_revenu="euros_mois")
    assert "Le système 4 : un taux pour tous" in texte
    assert "Garantie vieillesse" in texte
    assert "rente du pilier obligatoire" in texte
    assert "l'impôt en finance" in texte
    assert "personne seule, 300\u00a0€" in texte
    texte = page("/simuler", naissance=1958, liquidation=62, salaire=1500,
                 unite_revenu="euros_mois")
    assert "avant les 65 ans" in texte


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
    texte = page("/simuler", interruptions="<script>alert(1)</script>")
    assert "<script>alert(1)</script>" not in texte
    assert "&lt;script&gt;" in texte


def test_cellule_teintee_selon_la_valeur():
    assert "background" in Cellule("-90 %", intensite=-0.9).style()
    assert Cellule("+0 %", intensite=0.0).style() == ""
    rendu = tableau(["a"], [[Cellule("x", intensite=-0.5)]], ["nombre"])
    assert "rgba(162, 71, 46" in rendu


# -- rendu commun aux deux modes ---------------------------------------------


@pytest.mark.parametrize("chemin", ["/", "/simuler", "/cas-types", "/methode", "/donnees"])
def test_rendre_produit_un_corps_pour_chaque_page(contexte, chemin):
    titre, corps = rendre(contexte, chemin)
    assert titre
    assert len(corps) > 500


@pytest.mark.parametrize("chemin", ["/simuler", "/cas-types", "/methode"])
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
    if chemin == "/simuler":
        assert re.search(r"64 ans et 7 mois", corps)


def test_rendre_ignore_un_chemin_inconnu(contexte):
    titre, _ = rendre(contexte, "/n-importe-quoi")
    assert titre == "Programme"


def test_rendre_ne_leve_jamais_sur_une_saisie_invalide(contexte):
    _, corps = rendre(contexte, "/simuler", {"naissance": "1700"})
    assert "Saisie refusée" in corps


def test_statuts(contexte):
    codes = {entree["code"] for entree in statuts(contexte)}
    assert "salarie_prive_non_cadre" in codes


# -- liens -------------------------------------------------------------------


def test_les_liens_passent_par_l_ancre(contexte):
    """Sur GitHub Pages le site est servi dans un sous-chemin : pas de lien absolu."""
    _, corps = rendre(contexte, "/simuler")
    entete = g.entete("/")
    assert 'href="#/cas-types"' in entete
    assert 'href="/cas-types"' not in entete
    assert 'action="#/simuler"' in corps


def test_aucun_renvoi_vers_un_service_qui_n_existe_pas(contexte):
    """Il n'y a pas de serveur : proposer une adresse d'API serait un lien mort."""
    _, corps = rendre(contexte, "/simuler", {"naissance": "1960",
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
    assert {"series", "regimes", "inventaire", "affiliations", "quotients", "calibrations",
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
    corps = rendre(contexte, "/simuler", champs)[1]
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
    # La tolérance suit le NOMBRE DE LIGNES, et c'est de l'arithmétique, non de
    # la complaisance : chaque ligne est arrondie au centime pour l'affichage,
    # le total l'est une seule fois, et les arrondis peuvent s'ajouter jusqu'à
    # un demi-centime par ligne. Un seuil fixe à un centime passait tant que les
    # arrondis se compensaient ; il tombait au premier tableau où ils ne le
    # faisaient pas, sans qu'aucune ligne ne soit fausse. Ce que ce test doit
    # garder est que l'écran S'ADDITIONNE, pas que les flottants tombent juste.
    tolerance = 0.005 * len(regimes) + 0.005
    assert sum(regimes) == pytest.approx(total, abs=tolerance), (
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
    corps = rendre(contexte, "/simuler", champs)[1]
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


def test_le_salaire_net_des_cartes_est_celui_de_la_fiche_de_paie(contexte):
    """Le même nombre est écrit à deux endroits : il doit y être le même.

    Ce test remplace celui qui vérifiait « mensuel × 12 = annuel » sur chaque
    carte. Le total annuel a quitté l'affichage — une pension se pense au mois,
    comme un salaire —, et avec lui le recoupement qu'il permettait. Le salaire
    net en offre un autre, et meilleur : il est écrit une fois en tête de
    chaque carte, et une seconde fois dans la fiche de paie repliée. Deux
    chemins de calcul, deux rendus, un seul nombre attendu.
    """
    corps = rendre(contexte, "/simuler", SIMULATION_TEMOIN)[1]
    blocs = re.findall(r'<div class="scenario">(.*?)<div class="barre', corps, re.S)
    assert len(blocs) == 4, f"{len(blocs)} systèmes affichés, quatre attendus"
    # Le nombre des cartes est NU depuis que l'unité est passée sous lui
    # (« 2 540,34 » puis « € net/mois ») : `_nombres` cherche un symbole et n'en
    # trouve plus. On le lit donc directement, à la française.
    def _nu(texte: str) -> float:
        return float(texte.replace("\u202f", "").replace(",", "."))

    cartes = [_nu(re.search(r'class="chiffre salaire">\s*'
                            r'<span class="categorie">salaire</span>\s*'
                            r'<span class="somme">(.*?)</span>',
                            bloc, re.S).group(1))
              for bloc in blocs]
    # La ligne « Salaire net » du tableau : deux cellules, le droit en vigueur
    # puis la proposition. Les trois premières cartes portent la première.
    ligne = re.search(r"<strong>Salaire net</strong>.*?</tr>", corps, re.S).group(0)
    tableau = _nombres(re.sub(r"<[^>]+>", " ", ligne))
    assert len(tableau) == 2, f"la ligne du tableau porte {len(tableau)} nombres"
    for rang, attendu in enumerate([tableau[0]] * 3 + [tableau[1]]):
        assert abs(cartes[rang] - attendu) <= 0.005, (
            f"carte {rang + 1} : {cartes[rang]} en tête, {attendu} dans la fiche"
        )


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
            if "—" in ligne[rang_ecart]:
                # La composante « dont garantie vieillesse » du scénario 6 :
                # une part d'une ligne, pas un système, et sans écart à refaire.
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
    # Coefficient de durée de la proportionnelle agricole : « 37,5 / durée
    # requise », affiché à la suite de la valeur de service parce qu'il ne
    # multiplie que les points, ni le forfait ni les cotisations.
    duree = re.search(
        r"points × valeur de service [\d.]+ € × ([\d.]+)", detail)
    if duree:
        montant *= float(duree.group(1))
    # Part forfaitaire d'un régime MIXTE : la retraite forfaitaire agricole,
    # proratisée sur la durée, s'ajoute aux points.
    forfait = re.search(r"forfait ([\d,]+\.\d+) € \(\d+/\d+\)", detail)
    if forfait:
        montant += sans_virgules(forfait.group(1))
    cotisations = re.search(
        r"cotisations revalorisées ([\d,]+) € × rendement ([\d.]+)%", detail)
    if cotisations:
        montant += sans_virgules(cotisations.group(1)) * float(cotisations.group(2)) / 100
    # Le coefficient d'un régime en points se nomme par ce qu'il fait :
    # « anticipation » quand il retire, « majoration » quand il ajoute — c'est
    # le cas de l'Ircantec liquidée après le taux plein, et lui seul.
    coefficient = re.search(
        r"coefficient (?:d'anticipation|de majoration) ([\d.]+)", detail)
    if coefficient:
        montant *= float(coefficient.group(1))
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
        # Génération 1969 : la première dont l'âge légal est 64 ans depuis la
        # suspension de 2026, donc quatre trimestres entre 63 ans et l'âge
        # légal — pour 1965, la fenêtre s'est refermée avec la suspension.
        ("surcote parentale", {"naissance": "1969", "sexe": "F", "enfants": "3",
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
                                 "coefficient d'anticipation",
                                 "coefficient de majoration", "surcote parentale"):
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
                             "coefficient d'anticipation",
                             "coefficient de majoration", "surcote parentale"):
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
                        "coefficient d'anticipation",
                        "coefficient de majoration", "surcote parentale"}, (
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
                                   rendre(contexte, "/simuler", champs)[1]):
            classes.update(attribut.split())
    for selecteur in selecteurs:
        for classe in re.findall(r"\.([a-z-]+)", selecteur):
            assert classe in classes, (
                f"« {selecteur} » vise « .{classe} », absent du HTML rendu"
            )


def test_le_resume_vocal_annonce_bien_les_montants(contexte):
    """Et le sélecteur doit trouver quelque chose, pas seulement exister."""
    corps = rendre(contexte, "/simuler", {"naissance": "1975"})[1]
    blocs = re.findall(r'<div class="scenario">(.*?)<div class="barre', corps, re.S)
    assert len(blocs) == 4
    for bloc in blocs:
        assert re.search(r'class="titre">[^<]+<', bloc), "système sans titre"
        assert re.search(r'class="chiffre principal">\s*<span class="categorie">'
                         r'retraite</span>\s*<span class="somme">[^<]+<',
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
            "corps": temoins.sans_bloc_json(rendre(contexte, "/simuler", requete)[1]),
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
            corps = temoins.sans_bloc_json(rendre(contexte, "/simuler", requete)[1])
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

    #: Les deux polices de l'affiche sont servies par le dépôt — les charger
    #: chez Google aurait emporté l'adresse IP du lecteur chez un tiers à
    #: chaque visite, et fait mentir la phrase « rien n'est envoyé ».
    feuille = g.FEUILLE_DE_STYLE
    assert "fonts.googleapis.com" not in feuille
    assert "fonts.gstatic.com" not in feuille
    polices = Path(__file__).resolve().parents[1] / "moteur" / "polices"
    for fichier in re.findall(r"url\((polices/[^)]+)\)", feuille):
        assert (polices.parent / fichier).is_file(), f"police absente : {fichier}"
    assert len(re.findall(r"@font-face", feuille)) == 4

    #: Seules adresses tolérées, et aucune n'est chargée avec la page : le
    #: dépôt lui-même (liens que le lecteur suit s'il le veut), l'espace de
    #: noms SVG, qui n'est jamais requêté, et l'intention de publication de X,
    #: que le bouton « Publier sur X » ouvre dans un onglet — c'est une
    #: navigation demandée par le lecteur, pas une requête faite dans son dos.
    autorisees = ("https://github.com/g-pliberal/", "http://www.w3.org/2000/svg",
                  "https://x.com/intent/post")
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
#: Il n'y a plus qu'un thème depuis la refonte : la bande est celle de
#: l'affiche, mesurée sur le vert profond.
BANDE_LUMINOSITE = (0.70, 0.87)
CHROMA_MINIMAL = 0.10
ECART_MINIMAL_VISION_NORMALE = 15.0

SCENARIOS_COLORES = ("actuel", "retroactif", "retroactif-employeur", "liberal")


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


def _simuler_daltonisme(hexa: str, genre: str) -> str:
    """La couleur telle qu'un œil deutéranope ou protanope la reçoit.

    Matrices de Viénot, Brettel et Mollon (1999), la référence usuelle : on
    passe en espace LMS, on écrase le cône manquant en le reconstruisant depuis
    les deux autres, et on revient en sRGB.
    """
    canaux = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, v, b = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        for c in canaux
    ]
    grand_l = 17.8824 * r + 43.5161 * v + 4.11935 * b
    moyen = 3.45565 * r + 27.1554 * v + 3.86714 * b
    court = 0.0299566 * r + 0.184309 * v + 1.46709 * b
    if genre == "deuteranopie":
        grand_l2, moyen2, court2 = grand_l, 0.494207 * grand_l + 1.24827 * court, court
    else:
        grand_l2, moyen2, court2 = 2.02344 * moyen - 2.52581 * court, moyen, court
    rouge = 0.080944 * grand_l2 - 0.130504 * moyen2 + 0.116721 * court2
    vert = -0.0102485 * grand_l2 + 0.0540194 * moyen2 - 0.113615 * court2
    bleu = -0.000365294 * grand_l2 - 0.00412163 * moyen2 + 0.693513 * court2

    def encoder(canal: float) -> int:
        canal = max(0.0, min(1.0, canal))
        canal = (12.92 * canal if canal <= 0.0031308
                 else 1.055 * canal ** (1 / 2.4) - 0.055)
        return round(max(0.0, min(1.0, canal)) * 255)

    return "#%02x%02x%02x" % (encoder(rouge), encoder(vert), encoder(bleu))


def _palette() -> list[str]:
    """Les six couleurs de scénario lues dans la feuille de style."""
    return [_couleur(nom) for nom in SCENARIOS_COLORES]


def test_la_palette_des_scenarios_reste_lisible():
    """Six courbes qui se croisent ne peuvent pas être séparées par la couleur
    seule si cette couleur est trop pâle ou trop proche de sa voisine.

    La palette précédente échouait aux trois contrôles : quatre de ses cinq
    couleurs passaient sous le plancher de chroma — elles lisaient gris —, et sa
    pire paire voisine tombait à ΔE 11,8 en vision normale, sous le plancher de
    15. Ce test ne rejoue pas la simulation daltonienne, mais il arrête la
    dérive qui l'avait provoquée.
    """
    couleurs = _palette()
    assert len(set(couleurs)) == 4, "deux systèmes partagent une couleur"
    bas, haut = BANDE_LUMINOSITE
    for couleur in couleurs:
        clarte, a, b = _oklab(couleur)
        assert bas <= clarte <= haut, (
            f"{couleur} : clarté {clarte:.3f} hors de la bande {bas}–{haut}"
        )
        assert (a * a + b * b) ** 0.5 >= CHROMA_MINIMAL, (
            f"{couleur} : chroma trop faible, la couleur lit gris"
        )
    for premiere, seconde in itertools.combinations(couleurs, 2):
        x, y = _oklab(premiere), _oklab(seconde)
        ecart = 100 * sum((u - v) ** 2 for u, v in zip(x, y)) ** 0.5
        assert ecart >= ECART_MINIMAL_VISION_NORMALE, (
            f"{premiere} et {seconde} : ΔE {ecart:.1f}, sous le plancher de "
            f"{ECART_MINIMAL_VISION_NORMALE:.0f} en vision normale"
        )
    # ET SOUS DALTONISME. C'est le contrôle que la palette à six couleurs ne
    # pouvait pas passer — le meilleur arrangement possible y descendait à
    # ΔE 8,6, et aucun choix de teintes n'y changeait rien : six catégories ne
    # se distinguent pas toutes pour un œil qui confond le rouge et le vert. À
    # quatre, la contrainte se relâche, et il est tenu. Il est donc vérifié ici
    # plutôt que sous-traité à une relecture extérieure.
    for genre in ("deuteranopie", "protanopie"):
        vues = [_simuler_daltonisme(couleur, genre) for couleur in couleurs]
        for premiere, seconde in itertools.combinations(vues, 2):
            x, y = _oklab(premiere), _oklab(seconde)
            ecart = 100 * sum((u - v) ** 2 for u, v in zip(x, y)) ** 0.5
            assert ecart >= ECART_MINIMAL_VISION_NORMALE, (
                f"{genre} : {premiere} et {seconde} se confondent (ΔE "
                f"{ecart:.1f})"
            )
    # La couleur n'est pas seule pour autant : le tracé porte aussi son motif
    # de tirets, qui ne se perd jamais, et la légende le reprend.
    pleine = g.Serie("Pleine", (1.0, 2.0, 3.0), "var(--actuel)")
    tiretee = g.Serie("Tiretée", (1.0, 2.0, 3.0), "var(--liberal)", tirets=True)
    trace = g.graphique("t", (2000, 2001, 2002), (pleine, tiretee))
    assert trace.count("stroke-dasharray") >= 1, (
        "une série en tirets doit se distinguer autrement que par sa couleur"
    )


# -- accessibilité -------------------------------------------------------------
#
# Le site ne déclare plus son accessibilité — le site d'accueil porte cette
# déclaration —, mais il continue de la mesurer. Une promesse écrite se périme
# au premier changement de gabarit ; ces contrôles-là ne se périment pas.

#: Plancher de contraste des textes courants, et des textes agrandis ou des
#: contours de composants — WCAG 2.1, critères 1.4.3 et 1.4.11.
CONTRASTE_TEXTE = 4.5
CONTRASTE_COMPOSANT = 3.0


def _couleur(nom: str) -> str:
    """Une variable de la feuille de style, telle que l'écran la rend.

    Il n'y a plus qu'un thème depuis la refonte en affiche : le vert profond
    EST l'identité du site, et non un habit de nuit qu'on quitte le matin.
    Seule la première définition compte donc — celle de ``:root``. Les
    suivantes sont celles du bloc ``@media print``, qui reteinte toute la
    palette en noir sur blanc pour ne pas coûter une cartouche par page, et
    qu'aucun écran ne voit.
    """
    ecran = g.FEUILLE_DE_STYLE.split("@media print")[0]
    trouvees = re.findall(rf"--{nom}:\s*(#[0-9a-f]{{6}})\s*;", ecran)
    assert trouvees, f"couleur « --{nom} » absente de la feuille de style"
    return trouvees[0]


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


def test_les_textes_tiennent_le_plancher_de_contraste():
    """Tout ce qui s'écrit, sur chacun des trois fonds de la page.

    ``--texte-doux`` porte les aides de saisie, les gloses, les graduations des
    graphiques et le pied de page : c'est la couleur la plus employée du site
    après le texte courant, et la première à céder quand la palette bouge. Elle
    a déjà cédé une fois — l'aide sous chaque libellé de champ était peinte à
    80 % d'opacité, ce qui la ramenait à 4,23:1 sur le fond clair.
    """
    for fond in ("fond", "fond-carte", "fond-appui"):
        for texte in ("texte", "texte-doux", "accent", "alerte"):
            mesure = _contraste(_couleur(texte), _couleur(fond))
            assert mesure >= CONTRASTE_TEXTE, (
                f"--{texte} sur --{fond} tombe à {mesure:.2f}:1, "
                f"sous le plancher de {CONTRASTE_TEXTE}:1"
            )


def test_le_contour_des_champs_se_distingue_du_fond():
    """Un champ de saisie se reconnaît à son contour : encore faut-il le voir.

    WCAG 1.4.11 demande 3:1 entre un composant d'interface et ce qui l'entoure.
    Le filet décoratif ``--trait`` plafonne à 1,4:1 — c'est voulu, il ne porte
    aucune information —, et les champs ont donc leur propre couleur de bord.
    """
    for fond in ("fond", "fond-carte"):
        mesure = _contraste(_couleur("trait-champ"), _couleur(fond))
        assert mesure >= CONTRASTE_COMPOSANT, (
            f"le contour des champs tombe à {mesure:.2f}:1 sur "
            f"--{fond}, sous le plancher de {CONTRASTE_COMPOSANT}:1"
        )


def test_la_feuille_de_style_respecte_le_reglage_mouvement_reduit():
    """La jauge d'attente glisse sans fin ; une animation sans fin rend malade.

    Le système le signale, et la feuille l'écoute — WCAG 2.2.2 et 2.3.3.
    """
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
    tableaux = re.findall(r"<table[^>]*>(.*?)</table>", corps, re.S)
    for rang, tableau_html in enumerate(tableaux, start=1):
        assert tableau_html.startswith("<caption>"), (
            f"{chemin} : le tableau n° {rang} n'a pas de titre"
        )
        lignes = re.findall(r"<tr[^>]*>(.*?)</tr>", tableau_html, re.S)
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
    texte = page("/simuler")
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
    texte = page("/simuler", naissance=1975, metier2_debut=40,
                 metier2_statut="artisan")
    groupes = re.findall(r'<fieldset class="metier[^"]*">(.{0,80})', texte, re.S)
    assert len(groupes) >= 2, "les métiers ne forment plus des groupes de champs"
    for debut in groupes:
        assert debut.startswith('<legend class="rang">'), (
            f"un groupe de métier n'a pas de légende : {debut!r}"
        )
    # La ligne encore vide, elle, est un dépliant : c'est son résumé qui la
    # nomme, et la nommer deux fois ferait lire deux titres pour une période
    # qui n'existe pas.
    vide = re.search(r'<details class="metier facultatif">(.*?)</summary>',
                     texte, re.S)
    assert vide and "<span>Ajouter une période" in vide.group(1), (
        "la ligne à remplir n'annonce plus ce qu'elle ajoute"
    )


#: Ce qu'on LIT à l'ouverture d'une page : bulles fermées, dépliants fermés,
#: menus repliés. C'est la mesure qui compte pour le texte d'un formulaire —
#: tout le reste attend qu'on le demande.
def _mots_visibles(corps: str) -> int:
    texte = re.sub(r'<span class="bulle"[^>]*hidden>.*?</span>', " ", corps, flags=re.S)
    texte = re.sub(r"<option\b.*?</option>", " ", texte, flags=re.S)
    texte = _sans_blocs(texte, "div", r'<div class="panneau"[^>]*\bhidden>')

    def replie(trouve: re.Match) -> str:
        bloc = trouve.group(0)
        if re.match(r"<details[^>]*\bopen", bloc):
            return bloc
        resume = re.search(r"<summary>.*?</summary>", bloc, re.S)
        return resume.group(0) if resume else " "

    texte = re.sub(r"<details\b.*?</details>", replie, texte, flags=re.S)
    return len(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", texte)).split())


def test_le_simulateur_tient_en_peu_de_mots(contexte):
    """Le formulaire s'ouvrait sur quatre-vingt-dix mots avant le premier champ.

    Ce qui est nécessaire pour remplir un champ ou lire un chiffre reste écrit ;
    tout ce qui explique, nuance ou justifie s'ouvre sous un point
    d'interrogation. Ce test tient la porte fermée : la prose revient toujours,
    une phrase à la fois.
    """
    vierge = rendre(contexte, "/simuler", {})[1]
    assert _mots_visibles(vierge) <= 160, "le formulaire reprend de la prose"

    resultats = rendre(contexte, "/simuler", {
        "naissance": "1962-03-15", "debut": "1984-09", "liquidation": "2026-07",
        "unite_revenu": "euros_mois", "salaire": "2600",
    })[1]
    assert _mots_visibles(resultats) <= 1700, "les résultats reprennent de la prose"


def test_le_sexe_ne_change_rien_par_defaut(contexte):
    """C'est ce qui justifie sa place dans les options de modélisation.

    Il ne compte que de deux façons — table de conversion par sexe, majoration
    de durée d'assurance réservée à la mère —, et les deux réglages qui les
    commandent sont eux-mêmes dans les options.
    """
    base = {"naissance": "1962-03-15", "debut": "1984-09",
            "liquidation": "2026-07", "unite_revenu": "euros_mois",
            "salaire": "2600"}

    def resultat(**champs) -> str:
        import json
        dictionnaire = contexte.simuler(
            Saisie.depuis_requete({**base, **champs})
        ).dictionnaire()
        # Le résultat REDIT le sexe saisi : c'est ce qui a servi à calculer,
        # et le comparer reviendrait à comparer la saisie à elle-même.
        dictionnaire["assure"].pop("sexe")
        return json.dumps(dictionnaire, sort_keys=True)

    assert resultat(sexe="H") == resultat(sexe="F")
    assert resultat(sexe="H", table="par_sexe") != resultat(sexe="F", table="par_sexe")
    assert resultat(sexe="H", enfants="2") != resultat(sexe="F", enfants="2")
    # Et le champ n'est plus dans la grille d'identité : il est dans le
    # dépliant des options, avec la table et les enfants.
    corps = rendre(contexte, "/simuler", {})[1]
    avant_options = corps.split('<details class="options">')[0]
    assert 'id="sexe"' not in avant_options
    assert 'id="sexe"' in corps


def test_les_champs_qui_decrivent_la_personne_sont_reconnaissables(page):
    """WCAG 1.3.5 : un champ qui demande une information sur l'utilisateur doit
    dire laquelle, pour que le navigateur et les aides à la saisie la
    reconnaissent."""
    texte = page("/simuler")
    # « bday » et non « bday-year » : le champ demande la date entière depuis
    # qu'il ouvre un calendrier, et c'est cette date que le navigateur sait
    # remplir.
    assert 'id="naissance"' in texte and 'autocomplete="bday"' in texte
    assert 'id="sexe"' in texte and 'autocomplete="sex"' in texte


def test_le_lien_d_evitement_ouvre_chaque_page(contexte):
    """Premier élément parcouru au clavier, et seul moyen d'atteindre le contenu
    sans retraverser l'en-tête à chaque page. RGAA 12.7."""
    entete = g.entete("/")
    assert entete.startswith('<a class="evitement" href="#contenu">'), entete[:80]
    assert 'aria-label="Navigation principale"' in entete, (
        "le repère de navigation doit porter un nom"
    )


def test_le_pied_avertit_depuis_toute_page():
    """Le pied est posé une fois, à côté de ``<main>``, et ne dépend donc pas
    de la page affichée : ce qu'il dit, il le dit partout."""
    pied = g.pied()
    assert "aucune valeur officielle" in pied, (
        "le pied doit dire que le simulateur n'engage aucune caisse"
    )
    assert "info-retraite.fr" in pied, "le pied doit renvoyer à la caisse"
    assert "CC BY-SA 4.0" in pied, "le pied doit dire sous quelle licence citer"


def test_le_site_ne_porte_aucune_mention_legale(contexte):
    """Le simulateur est encarté dans partiliberalfrancais.fr, qui l'édite et
    l'héberge : l'identification de l'éditeur, la politique de données
    personnelles et la déclaration d'accessibilité sont les siennes.

    Deux déclarations concurrentes valent moins qu'une, et celle d'ici se
    périmait sans que rien ne le dise — elle nommait GitHub, Inc. comme
    hébergeur, ce qui n'est vrai que de l'adresse GitHub Pages. Le test
    empêche qu'elle revienne par une page ou un pied de page.
    """
    interdits = ("Mentions légales", "Directeur de la publication",
                 "directeur de la publication", "a-completer",
                 "conformité partielle", "règlement (UE) 2016/679",
                 "défenseurdesdroits", "RGAA")
    pages = [("pied", g.pied())] + [
        (chemin, rendre(contexte, chemin, {})[1]) for chemin in TITRES
    ]
    for ou, corps in pages:
        for interdit in interdits:
            assert interdit not in corps, f"{interdit!r} est revenu sur {ou}"


def test_la_page_des_donnees_dit_sous_quelle_licence_reprendre(contexte):
    """Ce que l'hôte ne peut pas porter à la place du dépôt : ses licences.

    Une mention légale se délègue à l'éditeur du site d'accueil ; la licence
    du code, celle des infographies et l'obligation de citer le producteur
    d'une série, non — elles portent sur ce fichier-ci.
    """
    _, corps = rendre(contexte, "/donnees", {})
    assert "Apache 2.0" in corps
    assert "CC BY-SA" in corps
    assert "Licence Ouverte" in corps
    assert "cite le producteur, pas ce site" in corps


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


def test_un_graphique_descend_sous_l_axe_quand_une_serie_est_negative():
    """Une réserve se trace sous l'axe, et l'axe monte dans le cadre.

    Tant que rien n'est négatif, le plancher vaut zéro et l'axe des abscisses
    est au bas du cadre : c'est l'échelle de tous les graphiques du site, et
    elle ne doit pas bouger. Une valeur négative abaisse le plancher d'un
    nombre entier de pas, si bien que zéro reste une graduation ; l'axe passe
    alors par zéro, et le repère vertical descend jusqu'au plancher, pas
    jusqu'à l'axe.
    """
    positive = g.Serie("Dette", (0.0, 10.0, 30.0), "var(--actuel)")
    negative = g.Serie("Réserve", (0.0, -20.0, -50.0), "var(--liberal)")

    sans = g.graphique("t", (2025, 2026, 2027), (positive,), repere=2026)
    axe = re.search(r'<line class="axe"[^>]*y1="([\d.]+)"', sans).group(1)
    assert axe == str(g.HAUTEUR_TRACE - g.MARGE_BAS) + ".0"
    assert re.findall(r'<text class="graduation"[^>]*>(-?[\d,]+)</text>', sans)[:6] == [
        "0", "10", "20", "30", "40", "50"]

    avec = g.graphique("t", (2025, 2026, 2027), (positive, negative), repere=2026)
    graduations = re.findall(r'<text class="graduation"[^>]*>(-?[\d,]+)</text>', avec)
    # Amplitude 80 : le pas passe à 20, le plancher tombe à -60 (un multiple
    # du pas sous -50), le sommet à 40 (le premier multiple au-dessus de 30).
    assert graduations[:7] == ["-60", "-40", "-20", "0", "20", "40", "2025"]
    axe = float(re.search(r'<line class="axe"[^>]*y1="([\d.]+)"', avec).group(1))
    assert g.MARGE_HAUT < axe < g.HAUTEUR_TRACE - g.MARGE_BAS
    repere = float(re.search(r'<line class="repere"[^>]*y2="([\d.]+)"', avec).group(1))
    assert repere == g.HAUTEUR_TRACE - g.MARGE_BAS
    # La courbe négative finit plus bas que l'axe, la positive plus haut.
    chemins = re.findall(r'<path class="courbe"[^>]*d="([^"]+)"', avec)
    assert float(chemins[0].split()[-1]) < axe < float(chemins[1].split()[-1])


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
    traces = corps.count('<figure class="graphique"')
    tableaux = corps.count('<details class="donnees-graphique">')
    assert traces == tableaux, (
        f"{chemin} : {traces} graphiques pour {tableaux} tableaux de données"
    )


def test_le_graphique_de_la_trajectoire_porte_ses_ages(contexte):
    """Sur la page de résultats, le seul graphique qui ne se lit pas en années."""
    corps = rendre(contexte, "/simuler", {
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
    for generation, attendu in ((1920, 5.2), (1945, 0.0), (1958, -0.5)):
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

    Ce test ne survit que pour l'arborescence du README, qui annonce le compte
    DANS UN BLOC DE CODE : une ancre y serait visible, et `verifier_prose.py`
    n'y touche donc pas — c'est le premier de ses angles morts, nommé dans
    `docs/fraicheur.md`. Les deux autres phrases qui donnaient ce compte, dans
    le README et dans `limites.md`, portent maintenant la sonde `tests()` et se
    corrigent toutes seules.
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

    texte = (racine / "README.md").read_text(encoding="utf-8")
    annonces = re.findall(r"(\d+) tests Python", texte)
    assert annonces, "l'arborescence du README n'annonce plus de nombre de tests"
    for annonce in annonces:
        assert int(annonce) == reels, (
            f"l'arborescence du README annonce {annonce} tests, le dépôt en "
            f"collecte {reels}"
        )


def test_le_README_montre_la_simulation_que_le_modele_calcule_vraiment():
    """Le bloc d'exemple du README doit être le résultat, pas son souvenir.

    Le §3 du README colle la sortie de ``comparaison.tableau()`` pour une
    fonctionnaire née en 1975. C'est la pièce la plus lue du dépôt, et rien ne
    l'obligeait à suivre le modèle : elle avait dérivé de 1,7 % sur la pension du
    scénario 1 sans que personne ne s'en aperçoive, et l'écart du scénario 4 y
    valait +7,0 % quand le modèle en servait +9,0 %. Ce test la recalcule.
    """
    from pathlib import Path

    from retraite_notionnelle import Parametres
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur(Parametres())
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1975, sexe="F", affiliation="fonctionnaire_etat",
        age_debut=22, age_liquidation=64,
        part_primes=0.2, profil_carriere="ascendant",
    ))
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
    # Le README ne colle pas tout le tableau : il garde les six scénarios, la
    # ligne hors répartition et le bloc « qui verse la cotisation ». Ce sont
    # exactement les lignes qui portent des chiffres, et donc celles qui dérivent.
    portees = re.compile(r"^(?:\d\. |   hors répartition|  (?:part |total|contribution))")
    verifiees = 0
    for ligne in comparaison.tableau().split("\n"):
        if not portees.match(ligne):
            continue
        verifiees += 1
        assert ligne in readme, (
            "le bloc d'exemple du README a dérivé : le modèle écrit\n"
            f"  {ligne}\net le README ne le porte pas"
        )
    assert verifiees >= 10, "le tableau n'a plus la forme que le README colle"


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
    """Ce que le premier chargement transfère, et qui le tient.

    Ce test mesurait `moteur/donnees.json` seul, à cinq pour cent près, pour
    une phrase qui annonce TOUT le premier chargement — les données, la
    feuille de style, les vingt-cinq modules préchargés et la page. Il est
    donc resté vert pendant que la phrase dérivait de 310 Ko à plus du
    double : il recoupait la mauvaise grandeur.

    La phrase porte maintenant ses deux sondes, et
    `tests/test_prose.py::test_aucun_chiffre_ancre_n_a_derive` les recalcule à
    chaque exécution. Ce qui reste à tenir ici, c'est qu'on ne puisse pas les
    retirer : un chiffre désancré redeviendrait un souvenir, en silence.
    """
    import re
    from pathlib import Path

    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
    annonce = re.search(
        r"chargement transfère <!--chiffre:poids_comprime\(([^)]*)\)-->[\d  ]+<!--/--> Ko compressés\s*"
        r"\(<!--chiffre:poids\(([^)]*)\)-->[\d  ]+<!--/--> Ko bruts\)", readme)
    assert annonce, "le README ne dit plus, sous sonde, ce que le premier chargement transfère"
    for charge in annonce.groups():
        for morceau in ("moteur/donnees.json", "moteur/style.css",
                        "moteur/js/*.js", "index.html"):
            assert morceau in charge, (
                f"la sonde du premier chargement oublie {morceau} : c'est ainsi "
                "que l'ancienne mesure comptait le paquet pour le tout"
            )


def test_le_balayage_des_temoins_visite_six_generations():
    """Chaque statut est simulé à plusieurs générations, pour que les périodes
    ANCIENNES des fiches soient visitées autant que les récentes.

    Le balayage n'en connaissait qu'une, née en 1975 : corriger le régime des
    salariés agricoles n'avait déplacé aucun témoin. Il en faut au moins
    cinq en plus du cas de base, dont une née avant 1934 — les tables par
    génération ne répondent pas toutes en deçà — et une après 1961, qui
    liquide sous la loi de 2023.
    """
    import importlib.util
    from pathlib import Path

    chemin = Path(__file__).resolve().parents[1] / "scripts" / "construire_temoins.py"
    specification = importlib.util.spec_from_file_location("construire_temoins", chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    generations = set(module.GENERATIONS_BALAYEES)
    assert len(generations) >= 5
    assert min(generations) < 1934
    assert max(generations) > 1961
    noms = {c["nom"] if isinstance(c, dict) else c[0] for c in module._cas()}
    # Un statut fermé aux nouveaux entrants n'est balayé qu'aux générations
    # qui peuvent encore y entrer : l'agent des chemins de fer secondaires né
    # en 1975 n'est qu'un salarié du privé, et le formulaire le refuse.
    for statut in module.STATUTS:
        for naissance in generations:
            attendu = module.debut_admissible(statut, naissance) is not None
            assert (f"statut_{statut}_{naissance}" in noms) == attendu, (statut, naissance)
    assert module.debut_admissible("agent_chemins_fer_secondaires", 1975) is None
    assert module.debut_admissible("agent_chemins_fer_secondaires", 1935) == 19
    assert module.debut_admissible("mineur", 1975) == 21


# -- le ruban entre deux courbes ----------------------------------------------


def _rubans(html: str) -> list[tuple[str, str]]:
    """Les rubans d'écart d'un graphique : leur teinte et leur chemin."""
    return re.findall(r'<path class="ecart (plus|moins)" d="([^"]+)"/>', html)


def test_le_ruban_d_ecart_se_peint_du_cote_de_celle_qui_est_au_dessus():
    """Vert là où la première série passe au-dessus, rouge là où elle passe dessous.

    C'est ce qui fait qu'un graphique de ressources et de dépenses se lit sans
    savoir lire un graphique : l'écart n'est plus à mesurer à l'œil, il est
    peint. Encore faut-il qu'il le soit du bon côté, et sur la bonne portion.
    """
    haute = g.Serie("Ce qui rentre", (12.0, 10.0), "var(--serie-5)")
    basse = g.Serie("Ce qui sort", (10.0, 12.0), "var(--serie-2)")
    html = g.graphique("Un essai", (2000, 2001), (haute, basse), ecart=(0, 1))
    rubans = _rubans(html)
    assert [teinte for teinte, _ in rubans] == ["plus", "moins"], (
        "le ruban doit changer de teinte au croisement"
    )


def test_le_ruban_d_ecart_change_de_teinte_a_l_intersection_exacte():
    """Et non à l'année suivante.

    Les deux courbes se croisent au milieu du segment : le ruban vert doit
    s'arrêter là, le rouge y commencer, et les deux s'y rejoindre en un point —
    même abscisse, même ordonnée. Sans cette interpolation, une moitié de
    l'année serait peinte de la mauvaise couleur, ce qui se voit.
    """
    haute = g.Serie("Ce qui rentre", (12.0, 10.0), "var(--serie-5)")
    basse = g.Serie("Ce qui sort", (10.0, 12.0), "var(--serie-2)")
    html = g.graphique("Un essai", (2000, 2001), (haute, basse), ecart=(0, 1))
    rubans = _rubans(html)

    def sommets(chemin: str) -> list[tuple[float, float]]:
        return [(float(x), float(y))
                for x, y in re.findall(r"[ML](-?[\d.]+) (-?[\d.]+)", chemin)]

    fin_du_vert = sommets(rubans[0][1])
    debut_du_rouge = sommets(rubans[1][1])
    # Le dernier point du bord supérieur du vert et le premier du rouge : c'est
    # le croisement, et il est le même des deux côtés.
    croisement = fin_du_vert[1]
    assert croisement == debut_du_rouge[0], (
        f"les deux rubans ne se rejoignent pas : {croisement} ≠ {debut_du_rouge[0]}"
    )
    # Le croisement est à mi-chemin des deux années — les deux courbes sont
    # symétriques — et le ruban y est d'épaisseur nulle.
    milieu = (g.MARGE_GAUCHE + g.LARGEUR_TRACE - g.MARGE_DROITE) / 2
    assert abs(croisement[0] - milieu) < 0.2, croisement
    epaisseur = [point for point in fin_du_vert if point[0] == croisement[0]]
    assert len({point[1] for point in epaisseur}) == 1, (
        "au croisement, les deux bords du ruban doivent porter la même ordonnée"
    )


def test_le_ruban_d_ecart_se_tait_sur_une_annee_manquante():
    """Un ruban interpolé par-dessus un trou affirmerait un écart que personne
    n'a mesuré. La courbe, elle, s'y interrompt déjà."""
    haute = g.Serie("Ce qui rentre", (12.0, None, 10.0), "var(--serie-5)")
    basse = g.Serie("Ce qui sort", (10.0, 11.0, 12.0), "var(--serie-2)")
    html = g.graphique("Un essai", (2000, 2001, 2002), (haute, basse), ecart=(0, 1))
    assert _rubans(html) == [], "un trou dans la série ne doit rien peindre"


def test_le_ruban_d_ecart_se_nomme_dans_la_legende():
    """La couleur seule ne porte jamais de sens : WCAG 1.4.1."""
    series = (g.Serie("A", (2.0, 3.0), "var(--serie-5)"),
              g.Serie("B", (1.0, 4.0), "var(--serie-2)"))
    html = g.graphique("Un essai", (2000, 2001), series, ecart=(0, 1),
                       libelle_ecart="L'écart entre les deux")
    assert "L&#x27;écart entre les deux" in html
    assert '<span class="pastille ecart-plus">' in html
    assert '<span class="pastille ecart-moins">' in html


# -- les mots du glossaire -----------------------------------------------------


def test_un_mot_du_glossaire_ne_coupe_pas_son_paragraphe():
    """Le piège dans lequel ce dépliant est tombé une fois.

    ``<details>`` fait partie des balises dont l'analyseur HTML FERME un ``<p>``
    ouvert : un mot du glossaire posé au milieu d'une phrase coupait le
    paragraphe en deux, et la fin de la phrase tombait à la ligne, hors du
    paragraphe. Le mot est donc un ``<button>``, qui est du contenu de phrase.
    """
    assert "<details" not in g.mot("répartition", "Les cotisations d'aujourd'hui…")
    # Un `<span role="button">`, et non un `<button>` : Chromium rend tout bouton
    # en bloc en ligne, qui ne coule pas dans une phrase.
    assert 'role="button" tabindex="0"' in g.mot("répartition", "Les cotisations d'aujourd'hui…")
    assert "<button" not in g.mot("répartition", "Les cotisations d'aujourd'hui…")


@pytest.mark.parametrize("chemin", list(TITRES))
def test_aucun_depliant_ne_coupe_un_paragraphe(contexte, chemin):
    """Et la règle vaut pour toute la page, pas seulement pour le glossaire.

    ``<details>``, ``<div>``, ``<ul>``, ``<h2>`` ferment un ``<p>`` ouvert. Le
    navigateur ne s'en plaint pas : il referme et continue, et la mise en page
    se décale sans que rien ne le dise. Ce contrôle regarde ce que le gabarit
    écrit, avant que l'analyseur ne le corrige.
    """
    corps = rendre(contexte, chemin, {})[1]
    for paragraphe in re.findall(r"<p\b[^>]*>(.*?)</p>", corps, re.S):
        for balise in ("<details", "<div", "<ul", "<ol", "<h2", "<h3", "<h4",
                       "<table", "<figure", "<section"):
            assert balise not in paragraphe, (
                f"{chemin} : {balise} dans un paragraphe — l'analyseur HTML y "
                f"fermera le <p>, et la suite de la phrase tombera hors de lui"
            )


@pytest.mark.parametrize("chemin", list(TITRES))
def test_chaque_mot_du_glossaire_porte_sa_definition(contexte, chemin):
    """Un mot signalé sans définition serait un bouton qui n'ouvre rien.

    Le bouton porte ``aria-expanded`` — sans quoi une synthèse vocale l'annonce
    comme un bouton ordinaire, sans dire qu'il déplie quelque chose — et la
    bulle le suit immédiatement, repliée : c'est sur cette adjacence que le
    script d'``index.html`` s'appuie pour la trouver.
    """
    corps = rendre(contexte, chemin, {})[1]
    mots = re.findall(r'<span class="mot">(.*?)</span></span>', corps, re.S)
    assert len(mots) == corps.count('<span class="mot">'), (
        f"{chemin} : un mot du glossaire est mal formé"
    )
    for mot in mots:
        # Deux ancres possibles : le mot de jargon, souligné dans la phrase, et
        # l'appel — un point d'interrogation posé après un titre ou un libellé
        # de champ, qui n'a pas de texte et doit donc porter son nom.
        assert mot.startswith(
            '<span class="terme" role="button" tabindex="0" aria-expanded="false">'
        ) or re.match(
            r'<button type="button" class="terme appel" aria-expanded="false" '
            r'aria-label="[^"]+"><svg class="icone" ', mot,
        ), mot[:90]
        bulle = re.search(r'<span class="bulle" role="note" hidden>(.*)', mot, re.S)
        assert bulle and bulle.group(1).strip(), f"{chemin} : mot sans définition"


# -- la bibliothèque de pictogrammes -----------------------------------------


def _icones_vendues() -> dict[str, str]:
    """Les originaux de ``moteur/icones/``, réduits à leur tracé.

    Le fichier est celui de Lucide, recopié sans retouche : la table du gabarit
    doit en dire exactement le contenu, sans quoi le site dessinerait autre
    chose que ce que le dossier prétend contenir.
    """
    from pathlib import Path

    dossier = Path(__file__).resolve().parents[1] / "moteur" / "icones"
    trace = {}
    for fichier in sorted(dossier.glob("*.svg")):
        dedans = re.search(r"<svg\b[^>]*>(.*?)</svg>", fichier.read_text(
            encoding="utf-8"), re.S).group(1)
        trace[fichier.stem] = "".join(
            ligne.strip() for ligne in dedans.splitlines()
        )
    return trace


def test_les_pictogrammes_disent_ce_que_leurs_fichiers_disent():
    """La table du gabarit est une COPIE, et doit le rester.

    Elle existe parce que le portage JavaScript n'utilise aucune bibliothèque et
    que la page ne charge aucune ressource tierce : le tracé est donc écrit dans
    le code. Rien ne garantirait alors qu'il soit celui de Lucide — sinon ce
    test, qui rouvre les originaux.
    """
    vendus = _icones_vendues()
    assert vendus, "le dossier des pictogrammes est vide"
    assert set(g.ICONES) == set(vendus), (
        "la table et le dossier ne portent pas les mêmes pictogrammes : "
        f"{set(g.ICONES) ^ set(vendus)}"
    )
    for nom, trace in vendus.items():
        assert g.ICONES[nom] == trace, f"le tracé de « {nom} » s'écarte de son fichier"


def test_les_deux_portages_dessinent_les_memes_pictogrammes():
    """Un chevron qui différerait d'un moteur à l'autre ne se verrait pas dans
    les témoins de page — ils sont rendus par les deux, mais comparés entre
    eux. La table est donc LUE dans le portage, et non relue à l'œil."""
    import json
    import shutil
    import subprocess
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    racine = Path(__file__).resolve().parents[1]
    lecture = subprocess.run(
        ["node", "--input-type=module", "-e",
         'import { ICONES } from "./moteur/js/gabarit.js";'
         "process.stdout.write(JSON.stringify(ICONES));"],
        cwd=racine, capture_output=True, text=True, check=True,
    )
    assert json.loads(lecture.stdout) == dict(g.ICONES)


# -- le pont vers le site parent ---------------------------------------------
#
# La page est servie sous partiliberalfrancais.fr/retraite/, et parfois dans un
# cadre de la page d'accueil de ce site. Elle n'en charge rien ; elle n'y
# renvoie que par un lien, et ce lien doit ressortir de tout cadre.


def test_le_pont_vers_le_site_parent_ressort_de_tout_cadre():
    """Un seul pont, en tête et en pied, et rien d'autre du site parent.

    ``target="_top"`` : ouvert dans le cadre que la page d'accueil du site
    ouvre sur le simulateur, un lien ordinaire chargerait le site DANS le
    cadre. Hors cadre, l'attribut ne change rien. Le lien est la seule adresse
    extérieure de l'en-tête : la navigation du site n'est pas recopiée, elle
    se périmerait à sa prochaine mise en page.
    """
    import re

    pont = (f'href="{g.SITE_PARENT}" target="_top"')
    entete = g.entete("/")
    assert pont in entete
    assert pont in g.pied()
    exterieures = set(re.findall(r'href="(https?://[^"]+)"', entete))
    assert exterieures == {g.SITE_PARENT}, exterieures
    # Dans le cadre, le site pose ``plf-embedded`` sur ``<body>`` ; sa propre
    # navigation est alors juste au-dessus, et le pont ferait doublon.
    assert "body.plf-embedded .marque .retour" in g.FEUILLE_DE_STYLE


def test_la_coquille_est_la_meme_des_deux_cotes_du_portage():
    """L'en-tête et le pied sont écrits deux fois, en Python et en JavaScript.

    Les témoins de page ne comparent que le corps : c'est ici, et seulement
    ici, qu'un lien ajouté d'un seul côté se verrait.
    """
    import json
    import shutil
    import subprocess
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    racine = Path(__file__).resolve().parents[1]
    lecture = subprocess.run(
        ["node", "--input-type=module", "-e",
         'import { entete, pied } from "./moteur/js/gabarit.js";'
         'process.stdout.write(JSON.stringify([entete("/cout"), pied()]));'],
        cwd=racine, capture_output=True, text=True, check=True,
    )
    assert json.loads(lecture.stdout) == [g.entete("/cout"), g.pied()]


def test_le_site_ne_dessine_plus_aucun_pictogramme_a_la_main(contexte):
    """Ni emoji, ni caractère détourné en icône.

    C'est ce qui rendait l'ancienne icône de page laide et instable : un emoji
    n'a pas le même dessin d'un système à l'autre, et aucune grille commune avec
    le reste. La règle vaut pour le HTML rendu, la page qui le porte et la
    feuille de style.
    """
    from pathlib import Path

    racine = Path(__file__).resolve().parents[1]
    emoji = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]")
    for chemin in TITRES:
        corps = rendre(contexte, chemin, {})[1]
        assert not emoji.findall(corps), f"{chemin} porte un emoji"
    for fichier in ("index.html", "moteur/style.css"):
        texte = (racine / fichier).read_text(encoding="utf-8")
        assert not emoji.findall(texte), f"{fichier} porte un emoji"


def test_l_icone_du_site_est_un_fichier_de_la_meme_grille():
    """L'icône de page est le seul pictogramme que le navigateur charge : elle
    doit être un dessin, du même jeu que les autres, et non un caractère."""
    from pathlib import Path

    racine = Path(__file__).resolve().parents[1]
    icone = (racine / "moteur" / "icone.svg").read_text(encoding="utf-8")
    page = (racine / "index.html").read_text(encoding="utf-8")
    assert 'href="moteur/icone.svg"' in page, "la page ne charge plus son icône"
    assert "<text" not in icone, "l'icône du site est redevenue un caractère"
    # Le même tracé que le pictogramme de la bibliothèque, au trait près.
    for trace in re.findall(r'd="([^"]+)"', g.ICONES["trending-up"]):
        assert trace in icone, "l'icône du site s'écarte du jeu de pictogrammes"
    assert 'stroke-width="2"' in icone


def _regles_du_telephone() -> str:
    """Le contenu de la requête média des écrans étroits."""
    return g.FEUILLE_DE_STYLE.split("@media (max-width: 34rem)")[1].split("\n}\n")[0]


def test_le_titre_d_un_scenario_ne_reserve_pas_de_hauteur_sur_telephone():
    """``flex: 1 1 14rem`` donne une largeur en ligne, une HAUTEUR en colonne.

    L'entête d'un scénario passe en colonne sous 34 rem, et le raccourci écrit
    pour la disposition en ligne y réservait 224 px sous chaque intitulé : six
    trous d'un tiers d'écran entre les six titres et leurs montants, si bien
    que le premier chiffre de la page tombait sous la ligne de flottaison. La
    règle qui rend au titre sa hauteur de texte est dans cette requête média,
    et doit y rester.
    """
    telephone = _regles_du_telephone()
    assert ".scenario .entete { flex-direction: column;" in telephone
    assert ".scenario .titre { flex: 0 1 auto; max-width: 100%; }" in telephone


def test_le_montant_d_un_scenario_se_replie_plutot_que_de_deborder():
    """Le téléphone ne rend pas la page avec la police ni la taille demandées.

    Aucun des empattements de la charte n'existe sur Android, qui y substitue
    un serif plus large, et le système grossit le texte par-dessus. Une somme
    qui ne se coupe pas dans une rangée qui ne se replie pas finissait donc
    hors de la carte : « par mois, en euros d'aujourd'hui » sortait de l'écran,
    et emportait la page entière dans un défilement horizontal. Les libellés se
    replient, les sommes non, la rangée passe à la ligne en dernier recours.
    """
    telephone = _regles_du_telephone()
    montant = telephone.split(".scenario .montant {")[1].split("}")[0]
    assert "flex-wrap: wrap" in montant
    # `margin-left: auto` cale le montant à droite de l'entête, ce qui n'a de
    # sens qu'en ligne : en colonne, il poussait la somme seule contre le bord
    # droit de l'écran, loin du titre qu'elle chiffre.
    assert "margin-left: 0" in montant
    chiffre = telephone.split(".scenario .chiffre {")[1].split("}")[0]
    assert "white-space: normal" in chiffre and "min-width: 0" in chiffre
    assert ".scenario .chiffre .somme { white-space: nowrap; }" in telephone


def test_l_appel_d_une_bulle_tient_la_cible_tactile():
    """24 px de côté, au doigt comme au pouce (WCAG 2.5.8).

    Le padding seul dimensionnait l'appel en proportion du texte qui le porte :
    dans une glose ou une note, il tombait à 19 px. Les minima l'en empêchent.
    """
    regle = g.FEUILLE_DE_STYLE.split(".mot > .terme.appel {")[1].split("}")[0]
    assert "min-width: 1.5rem" in regle and "min-height: 1.5rem" in regle


def test_tous_les_depliants_portent_le_meme_chevron(contexte):
    """Le marqueur natif d'un ``<details>`` n'a ni la même forme ni la même
    taille d'un navigateur à l'autre : chaque résumé porte donc le chevron du
    jeu, et la feuille de style masque celui du navigateur."""
    for chemin in TITRES:
        corps = rendre(contexte, chemin, {})[1]
        resumes = re.findall(r"<summary>(.{0,40})", corps, re.S)
        for debut in resumes:
            assert debut.startswith('<svg class="icone" '), (
                f"{chemin} : un dépliant sans chevron — {debut!r}"
            )
    style = g.FEUILLE_DE_STYLE
    assert 'summary::marker { content: ""; }' in style
    assert "details[open] > summary > .icone { transform: rotate(180deg); }" in style


def test_le_script_du_site_sait_ouvrir_les_mots_du_glossaire():
    """Le basculement vit dans ``index.html``, en écoute déléguée.

    Posé sur chaque bouton, il disparaîtrait avec lui : le contenu de ``<main>``
    est remplacé en bloc à chaque rendu. Ce test tient l'accord entre ce que le
    gabarit écrit et ce que la page sait ouvrir.
    """
    from pathlib import Path

    page = (Path(__file__).resolve().parents[1] / "index.html").read_text(
        encoding="utf-8")
    assert '.closest(".mot > .terme")' in page
    assert 'setAttribute("aria-expanded"' in page
    # Échap referme, et rend le focus au mot : sans cela le clavier n'a aucun
    # moyen de refermer une bulle ouverte (WCAG 1.4.13).
    assert 'evenement.key !== "Escape"' in page


# -- la discipline de la page Coût ---------------------------------------------


def _sans_blocs(corps: str, balise: str, ouverture: str) -> str:
    """``corps`` sans les blocs ``<balise …>`` reconnus par ``ouverture``.

    Les blocs s'imbriquent — le tableau de points d'un graphique vit dans une
    carte, elle-même parfois dans une section repliée —, et une expression
    régulière non gourmande s'arrêterait à la première fermeture. On apparie
    donc les balises, en comptant chaque ``<balise`` ouverte dans le bloc.
    """
    morceaux = []
    position = 0
    debut = re.compile(ouverture)
    bornes = re.compile(rf"<{balise}\b|</{balise}>")
    while position < len(corps):
        trouve = debut.search(corps, position)
        if not trouve:
            morceaux.append(corps[position:])
            break
        morceaux.append(corps[position:trouve.start()])
        profondeur = 0
        fin = len(corps)
        for borne in bornes.finditer(corps, trouve.start()):
            profondeur += -1 if borne.group(0).startswith("</") else 1
            if profondeur == 0:
                fin = borne.end()
                break
        position = fin
    return "".join(morceaux)


def _hors_depliants(corps: str) -> str:
    """Ce que la page montre sans qu'on ait rien déplié.

    Les sections repliées, les panneaux d'onglets que la feuille de style
    cache tant que leur onglet n'est pas choisi, et les bulles du glossaire,
    fermées tant qu'on ne les demande pas : rien de tout cela ne se lit à
    l'ouverture de la page.

    LES OPTIONS D'UN MENU DÉROULANT non plus. Un ``<select>`` fermé occupe une
    ligne et montre un libellé, quel que soit le nombre d'options qu'il porte ;
    les compter reviendrait à imputer au lecteur de l'accueil les soixante-dix
    statuts d'affiliation du catalogue — quatre cent cinquante mots qu'il ne
    voit pas, et qui feraient dépasser son budget au simple fait que le site
    connaît beaucoup de régimes. Le menu est donc réduit à ce qu'il montre.
    """
    sans_bulles = re.sub(r'<span class="bulle"[^>]*hidden>.*?</span>', " ", corps,
                         flags=re.S)
    sans_options = re.sub(r"<select\b[^>]*>.*?</select>", "<select></select>",
                          sans_bulles, flags=re.S)
    return _sans_blocs(
        _sans_blocs(sans_options, "details", r"<details\b"),
        "div", r'<div class="panneau"[^>]*\bhidden>',
    )


#: Ce que chaque page peut imposer à qui l'ouvre : mots à traverser, tracés
#: ouverts, tableaux ouverts. Les bornes sont celles de la refonte, arrondies
#: vers le haut d'environ un tiers : elles n'interdisent pas d'écrire, elles
#: interdisent de revenir à une page qu'on ne lit pas.
#:
#: Une page échappe à la règle des mots : « /simuler » EST un formulaire : ce
#: qu'on y compte est fait de libellés de champs et de deux cents options de
#: menus, que personne ne lit à la suite.
BUDGETS_DE_LECTURE: dict[str, tuple[int, int, int]] = {
    # Deux tableaux sur l'accueil : celui qui oppose les deux systèmes terme à
    # terme, et celui du plancher — l'argument le plus parlant du site, remonté
    # en haut de page par la revue de septembre 2026. Plus l'entrée, deux
    # lignes et un bouton qui disent que le site est un simulateur.
    "/": (670, 0, 2),
    "/simuler": (1500, 0, 0),
    # Trajectoire porte UN graphique, et c'est son sujet : il est donc ouvert,
    # là où celui de Coût attend qu'on déplie. Le reste de la page tient en
    # deux blocs de texte et le formulaire court.
    "/trajectoire": (500, 1, 0),
    # Partager ne porte que des cartes : leur texte est court par
    # construction — il doit tenir dans une image de 1200 × 675.
    "/partager": (400, 0, 0),
    # Cas types et Données ont gagné, à la revue de septembre 2026, ce qu'un
    # lecteur doit lire AVANT les chiffres : la clé de lecture des grilles et
    # la trajectoire du système actuel pour l'une, le résumé en langage
    # courant pour l'autre. Les bornes suivent, d'un paragraphe chacune.
    "/cas-types": (750, 0, 1),
    "/cout": (700, 2, 0),
    # LA SEULE PAGE DU SITE QUI DÉPASSE LE MILLIER DE MOTS, et c'est son objet
    # même. Elle affirme qu'il existe trente-neuf avantages non contributifs :
    # elle doit donc les NOMMER tous, dire ce que chacun coûte, et — pour les
    # vingt-quatre qui n'ont pas de montant — pourquoi il manque. Cela fait sept
    # tableaux et huit cents mots, qu'on ne peut pas replier sans défaire la
    # page : une liste cachée derrière un dépliant ne prouve rien.
    #
    # LA BORNE SUIT L'INVENTAIRE, et c'est assumé : elle est passée de 1900 à
    # 1950 mots le jour où trois dispositifs de plus ont été trouvés dans les
    # comptes de la protection sociale — l'indemnité temporaire de résidence
    # outre-mer, la retraite du combattant et la majoration des assurés
    # handicapés. Chacun coûte une ligne de tableau et son libellé. Refuser ces
    # mots-là reviendrait à choisir la longueur de la page contre son
    # exhaustivité, qui est sa seule raison d'être. En revanche la borne ne
    # suit PAS la prose : tout mot ajouté qui ne nomme pas un dispositif doit
    # en déloger un autre.
    #
    # Quatre graphiques ouverts, contre deux sur Coût, et c'est délibéré : ils
    # ne répondent pas à la même question et n'ont pas le même statut. Le
    # premier COMPTE des lignes d'inventaire et ne calcule rien ; le deuxième
    # chiffre ce que les avantages coûtent, au meilleur niveau connu, sur les
    # cinq ans où les comptes détaillent leurs postes ; le troisième donne la
    # même décomposition sur soixante-six ans, du modèle seul, parce qu'une
    # série de cinq points ne montre aucune évolution ; le quatrième mesure des
    # annuités, qui est une autre grandeur encore.
    #
    # LE TROISIÈME EST LE PRIX D'UNE HONNÊTETÉ, et on ne peut pas le replier.
    # Les postes publiés s'arrêtent à 2020 et la réversion à 2004 : une page qui
    # promet « l'évolution du coût au cours du temps » et montre cinq points ne
    # tient pas sa promesse, et une page qui empilerait ces séries sur toute la
    # longueur dessinerait des falaises qui ne sont que des débuts de
    # publication. Deux tracés, deux périmètres, chacun cohérent de bout en
    # bout. Les replier reviendrait à demander au lecteur de déplier pour
    # comprendre que les chiffres ne s'additionnent pas.
    "/avantages": (1950, 4, 7),
    "/methode": (500, 0, 1),
    "/donnees": (300, 0, 0),
}


@pytest.mark.parametrize("chemin", list(TITRES))
def test_aucune_page_ne_depasse_son_budget_de_lecture(contexte, chemin):
    """Le temps du lecteur n'est pas gratuit, et le site le dépensait.

    Les six pages alignaient de mille à six mille mots dépliés, seize tableaux
    et sept graphiques, sans qu'aucune ne dise par où commencer. Tout ce
    qu'elles doivent pouvoir justifier est toujours là — rien n'a été retiré —,
    mais replié : une pile de titres qui se parcourt du regard, et qui s'ouvre
    là où l'on veut savoir.

    Ce test tient la discipline page par page. Il ne dit pas quoi écrire ; il
    dit combien on peut en imposer avant que le lecteur ait choisi de lire.
    """
    mots_max, traces_max, tableaux_max = BUDGETS_DE_LECTURE[chemin]
    visible = _hors_depliants(rendre(contexte, chemin, {})[1])

    mots = len(re.sub(r"<[^>]+>", " ", visible).split())
    assert mots <= mots_max, (
        f"{chemin} : {mots} mots à traverser avant d'avoir rien déplié, "
        f"{mots_max} au plus"
    )
    traces = visible.count('<figure class="graphique"')
    assert traces <= traces_max, f"{chemin} : {traces} graphiques ouverts"
    tableaux = visible.count("<table")
    assert tableaux <= tableaux_max, f"{chemin} : {tableaux} tableaux ouverts"


#: Une carrière ordinaire, qui déclenche les sept sections de détail de la page
#: de résultats : salarié du privé, départ après la bascule, indexation par
#: défaut. C'est la simulation sur laquelle se mesure la discipline de cette
#: page, que le budget de lecture ci-dessus ne voit pas — il rend « /simuler »
#: sans paramètres, donc sans résultats.
SIMULATION_TEMOIN = {
    "naissance": "1975-01-01",
    "debut": "1996-01-01",
    "liquidation": "2039-01-01",
    "statut": "salarie_prive_non_cadre",
    "unite_revenu": "euros_mois",
    "salaire": "3500",
}


def test_la_page_de_resultats_replie_son_detail(contexte):
    """Qui vient de calculer sa pension veut son chiffre, pas une leçon.

    La page alignait sous ses six montants sept sections ouvertes — un
    graphique, neuf tableaux, quatre mille mots —, soit dix écrans de téléphone
    à traverser après le résultat. Tout y est encore, rangé dans des sections
    nommées qu'on ouvre une par une ; ce test tient la discipline, et la même
    borne de mots que le formulaire : les résultats n'ajoutent rien à ce qu'il
    faut traverser.
    """
    mots_max = BUDGETS_DE_LECTURE["/simuler"][0]
    corps = rendre(contexte, "/simuler", SIMULATION_TEMOIN)[1]
    assert "Résultats" in corps, "la simulation témoin ne calcule rien"

    visible = _hors_depliants(corps)
    mots = len(re.sub(r"<[^>]+>", " ", visible).split())
    assert mots <= mots_max, (
        f"{mots} mots à traverser sur la page de résultats, {mots_max} au plus"
    )
    assert visible.count("<table") == 0, "un tableau de détail reste ouvert"
    assert visible.count('<figure class="graphique"') == 0, (
        "un graphique reste ouvert"
    )
    # Et le détail est là, replié : six sections, plus lourdes à elles seules
    # que tout ce qui reste ouvert. Il y en avait sept ; celle qui détaillait
    # « du système 1 au système 3, ligne à ligne » est partie avec les variantes
    # « dès la bascule », dont elle expliquait la conversion des droits acquis.
    assert len(re.findall(r'<details class="section"[ >]', corps)) >= 6
    assert len(visible) < len(corps) / 2, (
        "le détail replié pèse moins que ce qui reste ouvert"
    )


#: Les pages assez longues pour avoir un détail à ranger. Trajectoire et
#: Partager n'en sont pas : la première porte un graphique et deux
#: paragraphes, la seconde quatre cartes. Leur imposer trois sections repliées
#: reviendrait à leur demander d'abord d'en écrire le contenu.
@pytest.mark.parametrize("chemin", ["/", "/cas-types", "/cout", "/methode",
                                    "/donnees"])
def test_chaque_page_range_son_detail_dans_des_sections(contexte, chemin):
    """Replier n'est pas supprimer : ce qui sort du chemin doit y être rangé.

    Une page qui tiendrait son budget de lecture en ayant simplement perdu la
    moitié de son contenu passerait le test précédent. Celui-ci vérifie
    l'autre moitié du marché : le détail est là, dans des sections nommées, et
    il pèse plus que ce qui reste ouvert.
    """
    corps = rendre(contexte, chemin, {})[1]
    # Un panneau d'onglet replié est une section nommée qu'on ouvre à la
    # demande, comme un dépliant : la page Cas types en range quatre.
    sections = (len(re.findall(r'<details class="section"[ >]', corps))
                + len(re.findall(r'<div class="panneau"[^>]*\bhidden>', corps)))
    assert sections >= 3, f"{chemin} : {sections} sections repliées"
    visible = _hors_depliants(corps)
    assert len(visible) < len(corps) / 2, (
        f"{chemin} : le détail replié pèse moins que ce qui reste ouvert"
    )
    # Et chaque section porte un titre qui dit ce qu'elle contient : c'est lui
    # qui tient lieu de sommaire.
    for titre in re.findall(r'<details class="section"(?: id="[^"]+")?><summary>(.*?)</summary>',
                            corps):
        assert len(titre.split()) >= 3, f"{chemin} : section mal nommée — {titre}"


def test_la_page_cout_ventile_ce_que_d_autres_caisses_versent(contexte):
    """Le poste « transferts » est ventilé par celui qui paie, et la page en tire
    la seule chose que le coefficient ne dit pas : la recette suit le droit."""
    corps = rendre(contexte, "/cout", {})[1]
    texte = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", corps)))
    assert "Ce que la branche famille et l'assurance chômage versent" in texte
    assert "Assurance vieillesse des parents au foyer" in texte
    assert "Points Agirc-Arrco des chômeurs" in texte
    assert "Ces recettes financent des droits que les scénarios" in texte
    # Le dépliant dit que le coefficient retire la recette, et ce qu'on lirait
    # sans ce retrait, sur deux des systèmes comparés.
    assert "Le coefficient d'équilibre du dépliant suivant les leur retire" in texte
    assert re.search(r"la proposition afficherait \d,\d\d en 20\d\d au lieu de \d,\d\d", texte)
    assert "et le système 2" in texte


def test_la_page_cout_tient_en_deux_graphiques_et_sans_tableau_ouvert(contexte):
    """Le temps du lecteur n'est pas gratuit, et cette page le dépensait.

    Elle portait sept graphiques et neuf tableaux dépliés, huit mille mots à
    traverser avant d'atteindre un résultat. Ce qu'elle doit pouvoir justifier
    est toujours là — rien n'a été retiré —, mais replié, et les trois tracés
    qui suivaient la même grandeur sur trois fenêtres n'en font plus qu'un.

    Les bornes sont larges à dessein : elles n'interdisent pas d'écrire, elles
    interdisent de revenir à une page qu'on ne lit pas.
    """
    corps = rendre(contexte, "/cout", {})[1]
    visible = _hors_depliants(corps)

    traces = visible.count('<figure class="graphique"')
    assert traces <= 2, f"{traces} graphiques ouverts sur la page Coût"
    assert visible.count("<table") == 0, (
        "un tableau déplié sur la page Coût : les chiffres se rangent sous le "
        "graphique qu'ils décrivent, ou dans une section repliée"
    )
    mots = len(re.sub(r"<[^>]+>", " ", visible).split())
    assert mots <= 650, f"{mots} mots à lire avant d'avoir rien déplié"

    # Et tout le reste est bien là, rangé.
    assert len(re.findall(r'<details class="section"[ >]', corps)) >= 8
    assert corps.count('<figure class="graphique"') > traces


def test_chaque_carte_de_la_page_cout_porte_sa_question_et_sa_reponse(contexte):
    """Une carte sans réponse est un graphique nu : le lecteur doit le lire.

    L'ordre compte autant que la présence — question, réponse, tracé — parce
    que c'est lui qui permet de s'arrêter à la deuxième ligne.
    """
    corps = rendre(contexte, "/cout", {})[1]
    cartes = re.findall(r'<section class="cle"[^>]*>(.*?)</section>', corps, re.S)
    assert len(cartes) == 2, f"{len(cartes)} cartes, deux attendues"
    for carte in cartes:
        titre = re.match(r"<h3>(.*?)</h3>", carte, re.S)
        assert titre, carte[:80]
        assert titre.group(1).endswith("?"), (
            f"une carte ne pose pas de question : {titre.group(1)}"
        )
        reponse = re.search(r'<p class="reponse">(.*?)</p>', carte, re.S)
        assert reponse and len(reponse.group(1).split()) >= 15, (
            "la réponse doit tenir seule, sans le graphique"
        )
        assert carte.index('class="reponse"') < carte.index("<figure"), (
            "la réponse vient avant le tracé : c'est ce qui permet de s'arrêter"
        )
        assert '<p class="source">' in carte, (
            "une carte qui se partage hors du site doit porter sa source"
        )
        assert '<button type="button" class="partager">' in carte, (
            "une carte doit pouvoir sortir du site en image"
        )


def test_chaque_carte_a_publier_part_d_un_bouton_et_non_d_une_capture(contexte):
    """La page Partager demandait une capture d'écran ; elle n'en demande plus.

    Les cartes étaient rendues à leur taille réelle dans un cadre qui défilait,
    à charge pour le militant de faire défiler, de capturer et de recadrer une
    image que le site savait composer lui-même. Elles portent maintenant la
    MÊME barre que les graphiques — un seul jeu de classes, un seul code —, et
    chacune emporte le compte et l'adresse.
    """
    corps = rendre(contexte, "/partager", {})[1]
    cartes = re.findall(r'<figure class="carte">(.*?)</figure>', corps, re.S)
    assert len(cartes) == 4, f"{len(cartes)} cartes, quatre attendues"
    for carte in cartes:
        assert carte.index("<figcaption>") < carte.index('class="cadre-carte"'), (
            "la légende nomme la carte, et se lit AVANT elle"
        )
        assert '<button type="button" class="partager">' in carte, (
            "une carte à publier doit partir d'un bouton, et non d'une capture"
        )
        assert '<button type="button" class="partager-x">' in carte
        assert g.SIGNATURE in carte and g.ADRESSE_SITE in carte, (
            "une image qui quitte le site doit dire qui l'a faite et où aller"
        )
    assert "captur" not in corps.lower(), (
        "la page invite encore à capturer l'écran : le bouton compose l'image"
    )


def test_la_barre_de_partage_n_est_ecrite_qu_une_fois(contexte):
    """Deux endroits partagent — la carte d'un graphique, la carte à publier —
    et ils ne doivent pas diverger. Le gabarit n'en écrit qu'une, et les deux
    pages la reprennent telle quelle."""
    barre = g.barre_partage()
    for chemin in ("/cout", "/partager"):
        corps = rendre(contexte, chemin, {})[1]
        assert barre in corps, f"{chemin} écrit sa propre barre de partage"
    # Deux gestes, et pas un de plus : le troisième bouton demandait de choisir
    # avant d'agir, et laissait chacun des trois incomplet.
    assert barre.count("<button") == 2, barre


# -- lire un graphique, et le faire sortir en image ----------------------------


def test_un_graphique_porte_de_quoi_se_lire_au_survol():
    """Ce qu'il faut pour retrouver une année depuis une position de pointeur.

    Deux abscisses, et rien d'autre : les VALEURS ne sont pas redites dans le
    SVG. Elles sont déjà dans le tableau de points que la même fonction pose
    juste dessous, mises en forme exactement comme la page les écrit. Les
    réécrire en attribut ferait deux vérités là où il en faut une — et les
    flottants de Python et de JavaScript ne s'écrivent pas pareil, si bien que
    les deux portages divergeraient sur un contenu qu'aucun œil ne lit.
    """
    series = (g.Serie("A", (1.0, 2.0, 3.0), "var(--serie-1)"),)
    html = g.graphique("Un essai", (2000, 2001, 2002), series)

    figure = re.search(r"<figure[^>]*>", html).group(0)
    assert f'data-gauche="{g.nombre_brut(g.MARGE_GAUCHE)}"' in figure
    assert f'data-droite="{g.nombre_brut(g.LARGEUR_TRACE - g.MARGE_DROITE)}"' in figure
    # Focusable, et annoncée comme un groupe : les flèches y parcourent les
    # années, ce qu'une image ne saurait pas faire.
    assert 'tabindex="0"' in figure and 'role="group"' in figure
    # La place où le script dessine, et celle où il écrit. Vides dans le HTML
    # servi : la page reste lisible sans une ligne de script.
    assert '<g class="survol"></g>' in html
    assert '<div class="lecture" role="status" aria-live="polite" hidden></div>' in html
    assert "Flèches gauche et droite" in html
    # Aucune valeur n'est recopiée hors du tableau de points.
    avant_details = html[:html.index('<details class="donnees-graphique">')]
    assert "data-valeurs" not in avant_details


def test_la_precision_des_chiffres_se_regle_a_part_de_celle_de_l_axe():
    """Un axe qui gradue de quatre en quatre ne doit pas arrondir les séries.

    C'est tout le sujet du graphique de tête de la page Coût : l'écart entre ce
    qui rentre et ce qui sort vaut un point et demi de PIB, et il disparaîtrait
    si la lecture au survol annonçait « 14 » contre « 13 ».
    """
    series = (g.Serie("A", (14.12, 13.95), "var(--serie-1)"),)
    grossier = g.graphique("Essai", (2024, 2025), series, decimales=0)
    fin = g.graphique("Essai", (2024, 2025), series, decimales=0, decimales_donnees=1)
    assert ">14<" in grossier and ">14,1<" not in grossier
    assert ">14,1<" in fin and ">13,9<" in fin
    # L'axe, lui, n'a pas bougé d'un caractère : seuls les chiffres changent.
    avant = grossier[:grossier.index('<details class="donnees-graphique">')]
    apres = fin[:fin.index('<details class="donnees-graphique">')]
    assert avant == apres


def test_le_script_du_site_sait_lire_et_exporter_un_graphique():
    """Le comportement vit dans ``index.html``, en écoute déléguée.

    Le gabarit écrit les prises — un bouton, deux abscisses, une zone vide — et
    la page les anime. Rien ne relie les deux que ces noms : ce test les tient
    ensemble, faute de quoi un bouton pourrait rester sans effet sans qu'aucun
    autre contrôle ne s'en aperçoive.
    """
    from pathlib import Path

    page = (Path(__file__).resolve().parents[1] / "index.html").read_text(
        encoding="utf-8")
    # La lecture au survol, au doigt et au clavier.
    assert '.closest("figure.graphique")' in page
    assert "dataset.gauche" in page and "dataset.droite" in page
    assert '"pointermove"' in page and "ArrowLeft" in page
    # Les chiffres viennent du tableau de points, et de nulle part ailleurs.
    assert 'nextElementSibling?.querySelector("table")' in page
    # La composition de l'image, et sa signature.
    assert '.closest("button.partager")' in page
    assert "toBlob" in page and "navigator.share" in page
    assert "SIGNATURE" in page and "SIGNATURE_SITE" in page
    # Les DEUX gestes de la barre, et le compte rendu qui les suit. Le libellé
    # du bouton ne sert plus d'accusé de réception : il change sous le doigt la
    # cible qu'on vient de toucher.
    assert '.closest("button.partager-x")' in page
    assert '.partage > .etat' in page
    # La signature n'est pas écrite deux fois : elle vient du gabarit.
    assert "@pliberal" not in page, (
        "la signature est écrite en dur dans index.html — elle doit venir de "
        "gabarit.SIGNATURE, comme tout ce que le site écrit"
    )


def test_la_signature_des_images_nomme_le_compte_et_le_site():
    """Une image qui circule n'a plus de barre d'adresse ni de pied de page.

    Sans ces trois lignes, elle sort du site sans dire d'où elle vient, ni où
    aller la vérifier, et le premier qui la republie en devient la source.
    """
    assert g.SIGNATURE.startswith("@")
    assert "libéral" in g.SIGNATURE_SITE.lower()
    # L'adresse est celle du site parent, et non celle de GitHub Pages : c'est
    # là que le lecteur d'un post doit atterrir.
    assert "partiliberalfrancais.fr" in g.ADRESSE_SITE
    assert "://" not in g.ADRESSE_SITE, "une adresse d'image se lit, pas se clique"
    # Et les deux portages disent la même chose : le JavaScript est la seule
    # copie, et c'est celle que la page lit.
    from pathlib import Path

    js = (Path(__file__).resolve().parents[1] / "moteur" / "js" / "gabarit.js"
          ).read_text(encoding="utf-8")
    assert f'export const SIGNATURE = "{g.SIGNATURE}";' in js
    assert f'export const SIGNATURE_SITE = "{g.SIGNATURE_SITE}";' in js
    assert f'export const ADRESSE_SITE = "{g.ADRESSE_SITE}";' in js


def _script_du_site() -> str:
    from pathlib import Path

    return (Path(__file__).resolve().parents[1] / "index.html").read_text(
        encoding="utf-8")


def test_le_filigrane_ne_paraît_qu_une_fois_et_traverse_l_image():
    """Une signature posée en pied part au premier recadrage.

    Et recadrer ne demande rien de plus qu'une capture d'écran : le pied d'une
    image republiée est ce qui disparaît le plus facilement, alors que c'est lui
    qui dit d'où elle vient. D'où un filigrane — mais UN SEUL.

    Il a d'abord été une grille, le compte répété soixante-dix fois en diagonale
    sur toute la surface. C'était la réponse littérale à « qu'il ne puisse pas
    être rogné », et c'était invivable : une image couverte de son propre
    filigrane ressemble à une planche de contact, et personne ne republie une
    planche de contact. « Je ne veux le voir apparaître qu'une fois. »

    Une seule marque, donc, et ce test tient les deux conditions qui lui
    permettent quand même de résister : elle est posée sur la DIAGONALE et
    occupe une large part de sa longueur — elle traverse le cadre, au lieu de se
    loger dans un coin qu'on découpe —, et elle reste assez pâle pour qu'on ne
    la voie qu'en la cherchant. Les deux composeurs d'image la posent EN
    DERNIER : posée avant, une aire pleine la recouvrirait.
    """
    page = _script_du_site()
    assert "function filigrane(dessin, largeur, hauteur, couleur)" in page
    corps = page[page.index("function filigrane(dessin"):]
    corps = corps[:corps.index("\n}\n")]

    # Une fois, et une seule. Ni boucle, ni second tracé.
    assert corps.count("fillText(SIGNATURE") == 1, (
        "le filigrane écrit le compte plus d'une fois : il doit paraître une "
        "fois, pas faire une trame"
    )
    assert "for (" not in corps, "une boucle dans le filigrane, c'est une grille"

    # Sur la diagonale, et à l'échelle de l'image : c'est ce qui la fait
    # traverser le cadre au lieu de se loger dans un coin.
    assert "Math.atan2(hauteur, largeur)" in corps, (
        "l'angle doit être celui de la diagonale, qui n'est pas le même pour "
        "une carte de 1200 × 675 et pour l'image d'un graphique"
    )
    part = float(re.search(r"const PART_FILIGRANE = ([\d.]+);", page).group(1))
    assert part >= 2 / 3, (
        f"{part} de la diagonale : trop court pour traverser le cadre, un "
        "recadrage l'emporterait en entier"
    )

    # Assez pâle pour ne se voir qu'en la cherchant : « il faut quelque chose de
    # subtil et discret ». Une lettre de 300 px se remarque plus qu'une de 14 à
    # opacité égale, d'où une borne plus basse que celle de la grille.
    opacite = float(re.search(r"const OPACITE_FILIGRANE = ([\d.]+);", page).group(1))
    assert 0.02 <= opacite <= 0.055, (
        f"{opacite} : sous 2 % le filigrane ne dit plus rien ; au-dessus de "
        "5,5 % une marque de cette taille se lit comme un tampon"
    )

    appels = [m.start() for m in re.finditer(r"^  filigrane\(dessin", page, re.M)]
    assert len(appels) == 2, (
        f"{len(appels)} images composées portent le filigrane, deux attendues — "
        "celle d'un graphique et celle d'une carte à publier"
    )
    for depart in appels:
        assert "toBlob" in page[depart:depart + 600], (
            "le filigrane doit être posé en dernier, juste avant l'export"
        )


# -- la revue du 15 septembre 2026 : le thème « expérience utilisateur » --------


def test_le_glossaire_est_le_meme_des_deux_cotes_du_portage():
    """Un mot défini deux fois, de deux façons, n'est plus un glossaire.

    La table est écrite dans le gabarit Python et recopiée dans le portage ;
    ce test lit la copie et la compare entrée pour entrée, comme pour les
    pictogrammes. Les témoins de page l'auraient vu aussi, mais seulement pour
    les mots qu'une page emploie.
    """
    import json
    import shutil
    import subprocess
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    racine = Path(__file__).resolve().parents[1]
    lecture = subprocess.run(
        ["node", "--input-type=module", "-e",
         'import { GLOSSAIRE } from "./moteur/js/gabarit.js";'
         "process.stdout.write(JSON.stringify(GLOSSAIRE));"],
        cwd=racine, capture_output=True, text=True, check=True,
    )
    assert json.loads(lecture.stdout) == dict(g.GLOSSAIRE)
    # Et aucune définition ne porte un chiffre qui bouge : un plafond, une
    # durée requise, un taux de décote y dériveraient sans que rien ne les
    # recoupe. Les seuls nombres admis sont ceux d'un exemple ou d'une date.
    for terme, definition in g.GLOSSAIRE.items():
        assert not re.search(r"\d[\d\u202f]{3,}\s*€", definition), (
            f"« {terme} » : un montant en euros dans une définition"
        )


def test_le_jargon_du_relecteur_porte_sa_definition(contexte):
    """Les mots que la revue extérieure relevait comme non définis.

    Chacun est un mot du glossaire là où il paraît : sur les résultats du
    simulateur pour le taux de remplacement, le coefficient de conversion, le
    capital notionnel et l'âge de référence ; dans le formulaire, sous un
    point d'interrogation, pour le statut d'affiliation, la table de
    conversion et l'âge de référence ; sur l'accueil pour les trimestres, la
    décote, la surcote et le salaire de référence.
    """
    def termes(corps: str) -> set[str]:
        return set(re.findall(
            r'<span class="terme" role="button" tabindex="0" aria-expanded="false">(.*?)</span>',
            corps,
        ))

    def bulles(corps: str) -> str:
        return " ".join(re.findall(r'<span class="bulle" role="note" hidden>(.*?)</span>',
                                   corps))

    resultats = rendre(contexte, "/simuler", SIMULATION_TEMOIN)[1]
    assert {"taux de remplacement", "coefficient de conversion",
            } <= termes(resultats)
    assert any(mot.startswith("capital notionnel") for mot in termes(resultats))
    # L'appel d'une bulle porte son texte tel quel — c'est du HTML de phrase —,
    # là où le mot du glossaire échappe le sien.
    for cle in ("statut d'affiliation", "table de conversion",
                "part patronale", "indexation"):
        assert g.GLOSSAIRE[cle] in bulles(resultats), cle

    accueil = rendre(contexte, "/", {})[1]
    assert {"trimestres", "décote", "surcote", "taux plein", "répartition",
            "25 meilleures années"} <= termes(accueil)
    cout = rendre(contexte, "/cout", {})[1]
    assert {"répartition", "part du PIB", "comptes notionnels",
            "taux de remplacement"} <= termes(cout)
    assert "réglage annuel" in termes(rendre(contexte, "/cas-types", {})[1])

# L'âge de référence ne se règle plus, et sa note n'existe plus : la
# conversion des droits acquis était propre aux deux variantes « dès la
# bascule », que le site ne compare plus depuis qu'il est passé à quatre
# systèmes. Le MODÈLE la calcule toujours — voir tests/test_simulateur.py —,
# mais aucune page ne la montre, et il n'y a donc plus rien à vérifier ici.


def test_le_menu_des_statuts_est_groupe_par_famille(page):
    """Soixante-deux options à la file ne se parcourent pas.

    Le menu du premier métier range les statuts sous un ``<optgroup>`` par
    famille, dans l'ordre de ``FAMILLES_STATUT`` ; celui des périodes
    suivantes y ajoute le groupe des périodes sans emploi, en dernier. Chaque
    option reste une option : le script qui grise les statuts fermés les
    parcourt par ``menu.options``, que les groupes ne cachent pas.
    """
    from retraite_notionnelle.carriere import FAMILLES_STATUT

    texte = page("/simuler")
    premier = re.search(r'<select id="statut".*?</select>', texte, re.S).group(0)
    groupes = re.findall(r'<optgroup label="([^"]+)">', premier)
    assert groupes == list(FAMILLES_STATUT.values())
    assert premier.count("<option") == 62
    sncf = re.search(r'<optgroup label="Régimes spéciaux">(.*?)</optgroup>', premier).group(1)
    assert 'value="agent_sncf"' in sncf
    prive = re.search(r'<optgroup label="Salariés du privé">(.*?)</optgroup>', premier).group(1)
    assert 'value="salarie_prive_non_cadre"' in prive

    second = re.search(r'<select id="metier2_statut".*?</select>', texte, re.S).group(0)
    assert re.findall(r'<optgroup label="([^"]+)">', second)[-1] == "Sans emploi"
    assert second.startswith('<select id="metier2_statut" name="metier2_statut">'
                             '<option value="" selected>— aucun —</option><optgroup')


def test_la_page_cas_types_ouvre_sur_la_proposition(contexte):
    """Le lecteur pressé s'arrêtait sur un contrefactuel.

    Les cinq grilles sont derrière des onglets — des boutons radio, un
    panneau par scénario —, et l'onglet coché à l'ouverture est le scénario
    6. Les quatre autres panneaux sont dans la page, ``hidden`` : là où
    ``:has()`` manque, la page montre le premier et cache les autres.
    """
    corps = rendre(contexte, "/cas-types", {})[1]
    radios = re.findall(r'<input type="radio" name="grille" id="grille-([^"]+)"( checked)?>',
                        corps)
    assert [code for code, _ in radios] == [
        "notionnel_liberal", "notionnel_retroactif",
        "notionnel_retroactif_employeur",
    ]
    assert [bool(coche) for _, coche in radios] == [True, False, False]
    panneaux = re.findall(r'<div class="panneau" data-onglet="([^"]+)"( hidden)?>', corps)
    assert [code for code, _ in panneaux] == [code for code, _ in radios]
    assert [bool(cache) for _, cache in panneaux] == [False, True, True]
    # Chaque radio porte son libellé, et le premier dit ce qu'il est.
    assert '<label for="grille-notionnel_liberal">4. La proposition</label>' in corps
    # La feuille de style sait montrer chacun des trois panneaux.
    for code, _ in radios:
        assert f'.onglets:has(#grille-{code}:checked) ~ .panneaux > .panneau[data-onglet="{code}"]' in g.FEUILLE_DE_STYLE, code
    # Et les trois chiffres d'ouverture sont lus sur cette grille-là.
    assert "génération 2000, système 4" in corps


#: Les tournures où un nombre écrit en toutes lettres NE compte pas les
#: systèmes. Sans cette liste, le contrôle ci-dessous se déclencherait sur des
#: phrases justes : un indice qui vaut « près de cinq fois les prix » n'a rien
#: à voir avec le nombre de systèmes comparés.
COMPTES_LEGITIMES = (
    "fois les prix",
)


@pytest.mark.parametrize("chemin", list(TITRES))
def test_aucune_page_ne_compte_plus_de_quatre_systemes(contexte, chemin):
    """Le site en compare QUATRE, et doit le dire partout de la même façon.

    Passer de six à quatre a touché cinquante-deux phrases. Les tests de
    structure en ont rattrapé la plupart, et une première version de celui-ci a
    rattrapé « Six calculs pour votre carrière ». Il cherchait des mots — « six
    systèmes », « six montants » — et il a donc laissé passer exactement ce
    qu'il ne cherchait pas : le TITRE de la page Simuler, « Votre carrière,
    calculée six fois », que l'auteur du site a vu avant lui. Plus la carte à
    publier, qui portait la même phrase et qui voyage sans le site autour
    d'elle.

    Il ne cherche donc plus des tournures connues, mais TROIS FORMES :

    * un numéro de système au-delà de quatre, qui n'a plus de référent ;
    * un décompte en toutes lettres suivi d'un mot qui désigne les systèmes ;
    * « calculée N fois » ou « calculée de N façons », quel que soit N.

    Le compte du MODÈLE n'est pas visé : il en calcule toujours six, et les
    commentaires du code le disent. Ce test ne lit que ce qui s'affiche, sur
    les huit routes — c'est là que vivaient les deux phrases fausses.
    """
    corps = rendre(contexte, chemin,
                   {"naissance": "1975-01-01"}
                   if chemin in ("/simuler", "/trajectoire") else {})[1]
    texte = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", corps)))

    def fautes(motif: str) -> list[str]:
        # La tournure légitime se reconnaît à ce qui SUIT le nombre — « cinq
        # fois les prix » —, donc sur la fenêtre, pas sur la correspondance,
        # qui s'arrête au mot compté.
        trouvees = []
        for t in re.finditer(motif, texte, re.I):
            fenetre = texte[t.start():t.end() + 24]
            if any(bon in fenetre for bon in COMPTES_LEGITIMES):
                continue
            trouvees.append(texte[max(0, t.start() - 50):t.end() + 50])
        return trouvees

    numeros = fautes(r"\b(?:systèmes?|scénarios?) [5-9]\b")
    assert not numeros, f"{chemin} : un numéro au-delà de quatre — {numeros}"

    decomptes = fautes(
        r"\b(?:cinq|six|sept|huit|neuf) "
        r"(?:systèmes?|scénarios?|calculs?|montants?|courbes?|barres?|façons?|fois)\b"
    )
    assert not decomptes, f"{chemin} : un décompte périmé — {decomptes}"

    calculees = fautes(r"calculées? (?:de )?(?!quatre)\w+ (?:fois|façons)")
    assert not calculees, f"{chemin} : « calculée » mal comptée — {calculees}"



def test_une_classe_du_bloc_scenario_ne_reprend_pas_un_composant():
    """Une classe du bloc des scénarios ne doit pas être stylée SANS ANCÊTRE.

    La ligne qui décompose le montant de la proposition s'était appelée
    `partage`. Ce nom était déjà celui de la barre de boutons de partage, dont
    la règle — sans ancêtre, donc applicable partout — porte un filet or de
    3 px sur toute la largeur : le filet est venu se tirer en travers du bloc,
    entre le montant et sa barre, et rien dans le HTML ne l'expliquait. La
    règle était à six cents lignes de là, dans un composant sans rapport.

    Le discriminant est exactement celui-là : une classe stylée sous un ancêtre
    (`.engagements .chiffre`) ne peut pas descendre ici, une classe stylée nue
    (`.partage`) le peut. `barre` fait exception, et c'est voulu : c'est le
    composant que le bloc emploie, pas un nom qu'il lui reprend.
    """
    import re

    feuille = re.sub(r"/\*.*?\*/", "", g.FEUILLE_DE_STYLE, flags=re.S)
    selecteurs = [
        " ".join(morceau.split())
        for tete in re.findall(r"(?:^|\})\s*([^{}@][^{}]*?)\{", feuille, re.S)
        for morceau in tete.split(",")
    ]
    for classe in ("entete", "titre", "montant", "chiffre", "somme", "unite",
                   "annuel", "glose", "composition", "capitalise"):
        nues = [s for s in selecteurs if re.match(rf"^\.{classe}\b", s)]
        assert not nues, (
            f".{classe} est stylée sans ancêtre par {nues} : la règle "
            "s'appliquera aussi dans le bloc des scénarios, qui pose cette "
            "classe, sans que rien ne le montre à la lecture du HTML"
        )


def test_les_pages_longues_portent_leur_plan(contexte):
    """Un plan déduit des sections, et qui les ouvre sans toucher à la route.

    Coût et Données listent, sous leurs trois chiffres, chaque carte et chaque
    section repliée qu'elles contiennent ; chaque lien porte la route de la
    page et l'identifiant de la section, et la section porte cet identifiant.
    Les autres pages, courtes, n'ont pas de plan.
    """
    for chemin, attendus in (
        ("/cout", ["cout-bilan", "cout-provenance", "cout-depenses", "cout-ressources",
                   "cout-transferts", "cout-scenarios", "cout-equilibre", "cout-dette",
                   "cout-frise", "cout-garantie", "cout-capitalisation", "cout-poids", "cout-sources",
                   "cout-limites"]),
        ("/donnees", ["donnees-series", "donnees-fiabilite", "donnees-inventaire",
                      "donnees-sources", "donnees-reutilisation"]),
    ):
        corps = rendre(contexte, chemin, {})[1]
        plan = re.search(r'<nav class="plan" aria-label="Dans cette page">.*?</nav>', corps, re.S)
        assert plan, f"{chemin} : pas de plan"
        liens = re.findall(r'<a href="([^"]+)" data-vers="([^"]+)">', plan.group(0))
        assert [vers for _, vers in liens] == attendus
        assert {href for href, _ in liens} == {g.lien(chemin)}
        for identifiant in attendus:
            assert f' id="{identifiant}"' in corps, identifiant
        # Le plan vient APRÈS les trois chiffres : le résultat d'abord, la
        # carte ensuite.
        assert corps.index('<div class="fiches reperes">') < corps.index('<nav class="plan"')
    for chemin in ("/", "/cas-types", "/methode", "/simuler"):
        assert '<nav class="plan"' not in rendre(contexte, chemin, {})[1], chemin

    from pathlib import Path

    page_html = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
    assert 'closest("a[data-vers]")' in page_html and "noeud.open = true" in page_html


def test_l_inventaire_est_une_table_qui_se_filtre_et_se_trie(contexte):
    """Quatre-vingt-neuf régimes en cinq tableaux de prose ne se cherchaient
    qu'au Ctrl+F.

    Une seule table, chaque ligne portant sa famille et sa couverture en
    ``data-``, un champ de recherche et deux menus devant elle, des en-têtes
    qui sont des boutons de tri. Sans script, elle se lit entière.
    """
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.donnees.regimes import charger_inventaire

    corps = rendre(contexte, "/donnees", {})[1]
    lignes = charger_inventaire(RACINE_DONNEES)
    table = re.search(r'<table id="inventaire">.*?</table>', corps, re.S).group(0)
    rangs = re.findall(r'<tr data-famille="([^"]+)" data-couverture="([^"]+)" data-fiabilite="[^"]*">', table)
    assert len(rangs) == len(lignes)
    assert [famille for famille, _ in rangs] == [l.famille for l in lignes]
    assert table.count('<button type="button" class="tri"') == 7
    assert 'data-cible="inventaire"' in corps
    assert 'id="inventaire-recherche"' in corps and 'data-filtre="texte"' in corps
    assert 'id="inventaire-famille"' in corps and 'id="inventaire-couverture"' in corps
    assert (f'data-compte-de="inventaire" data-unite="régimes">{len(lignes)} régimes</p>'
            in corps)
    # Une couverture qu'aucune ligne ne porte n'est pas proposée au filtre.
    assert 'value="a_modeliser"' not in corps
    # La fiabilité de chaque fiche calculée est dans la ligne du régime.
    catalogue = {r.code: str(r.fiabilite) for r in contexte.simulateur().catalogue}
    for ligne in lignes:
        if ligne.couverture in ("modelise", "partiel"):
            assert ligne.code in catalogue, ligne.code
    assert ">certifiee<" in table or ">haute<" in table
    # Et l'inventaire ne s'impose toujours pas : il reste replié.
    assert "<table" not in _hors_depliants(corps)

    from pathlib import Path

    page_html = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
    assert 'closest?.(".filtres[data-cible]")' in page_html
    assert 'closest("th > button.tri")' in page_html and 'setAttribute("aria-sort"' in page_html


def test_aucun_chemin_de_fichier_n_est_cite_en_texte_brut(contexte):
    """« docs/limites.md » se lisait sans qu'on puisse l'ouvrir : chaque renvoi
    à un document du dépôt est un lien vers ce document."""
    for chemin in TITRES:
        corps = rendre(contexte, chemin, {})[1]
        for cite in re.findall(r"<code>(docs/[^<]+|scripts/[^<]+|data/[^<]+)</code>", corps):
            assert False, f"{chemin} : « {cite} » cité en texte brut"


# -- la revue du 15 septembre 2026 : le thème « clarté des arguments » ----------


def test_la_cle_de_lecture_des_cas_types_precede_les_chiffres(contexte):
    """Le scénario 6 affiche −28 % à −76 % : sans la clé, on lit une baisse.

    La clé était sur la page Coût ; elle est en tête de Cas types, AVANT les
    trois chiffres d'ouverture et les grilles, et dit la phrase qui compte : un
    coefficient supérieur à un n'est pas une économie, c'est une marge. Elle
    renvoie à la section de Coût qui le chiffre.
    """
    corps = rendre(contexte, "/cas-types", {})[1]
    cle = corps.index("Ces pourcentages ne sont pas des baisses de")
    assert cle < corps.index('<div class="fiches reperes">')
    assert cle < corps.index('<div class="panneaux">')
    assert "Un coefficient supérieur à un est une marge" in corps
    assert 'data-vers="cout-equilibre"' in corps
    assert "Ces pourcentages ne sont pas des baisses" in _hors_depliants(corps)


def test_les_comparaisons_rappellent_que_le_systeme_actuel_derive(contexte):
    """« Aujourd'hui » n'est pas un point fixe, et les tableaux le disent.

    Cas types sous ses grilles, Coût dans la section des six systèmes : le
    solde du système actuel, observé puis projeté par le COR, est écrit à côté
    de la comparaison, avec les deux années. Les nombres viennent des comptes,
    pas d'une constante.
    """
    comptes = contexte.comptes()
    obs = comptes.derniere_annee_observee
    horizon = comptes.derniere_annee
    attendu_obs = g.pourcentage(-comptes.solde(obs), decimales=2)
    attendu_horizon = g.pourcentage(-comptes.solde(horizon), decimales=2)
    assert horizon > obs + 20, "les comptes ne portent plus la projection"

    cas_types = rendre(contexte, "/cas-types", {})[1]
    rappel = re.search(r"« Aujourd'hui » n'est pas un point fixe.*?</p>",
                       cas_types, re.S)
    assert rappel, "Cas types ne rappelle plus la trajectoire du système actuel"
    assert f"{attendu_obs} du PIB en {obs}" in rappel.group(0)
    assert f"{attendu_horizon} en {horizon}" in rappel.group(0)
    assert "système\nqui dérive" in rappel.group(0)
    assert rappel.start() > cas_types.index('<div class="panneaux">')

    cout = rendre(contexte, "/cout", {})[1]
    assert "comparer un scénario à lui, c'est le\ncomparer à un système qui dérive" in cout
    assert f"{attendu_obs}\ndu PIB en {obs}" in cout


def test_chaque_tableau_de_scenarios_distingue_proposition_et_contrefactuel(contexte):
    """Un badge là où l'erreur de lecture se produit, non dans un préambule.

    Sur Cas types, chaque panneau porte le sien dans son titre ; sur Coût, les
    quatre tableaux qui alignent les systèmes le portent en tête de ligne.
    Le système actuel n'en a pas : c'est la référence.
    """
    cas_types = rendre(contexte, "/cas-types", {})[1]
    titres = re.findall(r'<div class="panneau" data-onglet="([^"]+)"[^>]*><h3>.*?'
                        r'<span class="badge (\w+)">', cas_types)
    assert titres == [("notionnel_liberal", "proposition")] + [
        (code, "contrefactuel") for code in ("notionnel_retroactif",
                                             "notionnel_retroactif_employeur")]

    cout = rendre(contexte, "/cout", {})[1]
    lignes = re.findall(r'<th class="" scope="row">(\d)\. [^<]*(?:<span class="badge (\w+)">)?',
                        cout)
    # Quatre tableaux à quatre lignes : le passé, l'avenir, l'équilibre, la
    # dette.
    assert lignes.count(("1", "")) == 4, lignes
    assert lignes.count(("4", "proposition")) == 4
    for numero in "23":
        assert lignes.count((numero, "contrefactuel")) == 4, numero
    assert ".badge.proposition" in g.FEUILLE_DE_STYLE


def test_les_pages_techniques_s_ouvrent_en_langage_courant(contexte):
    """Trois ou quatre phrases simples avant le détail, sur Coût, Méthode et
    Données — et elles se lisent sans rien déplier."""
    for chemin, phrase in (
        ("/cout", "ont coûté un peu plus qu&#x27;elles n&#x27;ont rapporté"),
        ("/methode", "Votre pension serait votre\ncompte divisé par le nombre d&#x27;années"),
        ("/donnees", "viennent des institutions qui les produisent"),
    ):
        corps = rendre(contexte, chemin, {})[1]
        resume = re.search(r'<div class="note resume"><strong>En clair\.</strong>(.*?)</div>',
                           corps, re.S)
        assert resume, f"{chemin} : pas de résumé en langage courant"
        assert phrase in resume.group(0).replace("'", "&#x27;"), chemin
        texte = re.sub(r"<[^>]+>", "", resume.group(1))
        phrases = [p for p in re.split(r"(?<=[.!?])\s", texte.strip()) if p]
        assert 3 <= len(phrases) <= 5, f"{chemin} : {len(phrases)} phrases"
        if '<div class="fiches reperes">' in corps:
            assert resume.start() < corps.index('<div class="fiches reperes">'), chemin
        assert "En clair." in _hors_depliants(corps)


def test_l_autocritique_de_la_page_cout_est_un_encart_de_vigilance(contexte):
    """La comparaison à la projection du COR est un gage de sérieux : elle est
    marquée comme un point de vigilance, non noyée dans un paragraphe."""
    corps = rendre(contexte, "/cout", {})[1]
    encart = re.search(r'<div class="note vigilance"><strong>Point de vigilance : notre '
                       r"projection\ns'écarte de celle du COR\.</strong>(.*?)</div>",
                       corps, re.S)
    assert encart, "le point de vigilance a disparu"
    assert "celui du COR recule" in re.sub(r"\s+", " ", encart.group(1))
    assert ".note.vigilance" in g.FEUILLE_DE_STYLE


# -- action 29 : l'entrée, pour qui arrive du site du parti --------------------


def test_l_accueil_ouvre_sur_le_simulateur_avant_les_engagements(contexte):
    """Un visiteur doit savoir en dix secondes que le site est un simulateur,
    et où cliquer.

    Depuis la refonte en affiche, ce n'est plus un bloc qui dit « simulez » et
    renvoie ailleurs : c'est LE FORMULAIRE LUI-MÊME, court, en crème, posé sous
    le titre et avant les quatre engagements. La preuve est à hauteur de la
    promesse, et le premier écran ne demande plus de cliquer pour commencer.

    Il est hors de tout dépliant, il porte l'adresse du simulateur, et le
    rappel du bas de page reste. Dans le cadre que le site du parti ouvre sur
    cette page, le titre du simulateur est masqué par l'hôte : ce bloc est
    alors la seule chose qui dise « simulez »."""
    corps = rendre(contexte, "/", {})[1]
    visible = _hors_depliants(corps)
    formulaire = visible.index('<form class="creme simulateur-court"')
    engagements = visible.index('<section class="engagements"')
    affiche = visible.index('<div class="affiche">')
    assert affiche < formulaire < engagements
    # Il soumet vers le simulateur, et ses champs sont ceux du grand
    # formulaire : c'est la même adresse qui les reçoit.
    entete = visible[formulaire:engagements]
    assert f'action="{g.lien("/simuler")}"' in entete
    assert "Et vous, ça donne combien" in entete
    # Les champs se lisent sur le corps brut : `_hors_depliants` vide les
    # menus déroulants de leurs options, et emporte l'attribut du `<select>`.
    brut = corps[corps.index('<form class="creme simulateur-court"'):]
    brut = brut[:brut.index("</form>")]
    for champ in ("naissance", "debut", "statut", "liquidation"):
        assert f'name="{champ}"' in brut, f"le champ {champ} manque"
    bouton = f'<a class="bouton" href="{g.lien("/simuler")}">'
    assert visible.count(bouton) == 1, "le rappel du bas de page a disparu"
    assert ".simulateur-court .grille" in g.FEUILLE_DE_STYLE


def test_le_formulaire_dit_que_l_exemple_est_rempli(page):
    """Qui arrive sur le formulaire peut calculer tout de suite : une ligne
    visible le dit, avant le premier champ, et sans rien annoncer de plus."""
    texte = page("/simuler")
    assert "L'exemple est déjà rempli" in texte
    assert texte.index("L'exemple est déjà rempli") < texte.index("Date de naissance")
    assert "Résultats" not in texte


def test_les_resultats_s_ouvrent_sur_la_cle_de_lecture_puis_les_montants(contexte):
    """Sous « Résultats » : cinq phrases qui disent ce qu'on regarde, puis les
    quatre montants, puis seulement les repères techniques. Dans l'ordre
    inverse, un téléphone montrait un coefficient de conversion et pas un
    euro."""
    corps = rendre(contexte, "/simuler", SIMULATION_TEMOIN)[1]
    visible = _hors_depliants(corps)
    resultats = visible.index('id="resultats"')
    lecture = visible.index("Quatre calculs pour votre carrière", resultats)
    premier = visible.index('<div class="scenario">', lecture)
    reperes = visible.index('<div class="fiches">', resultats)
    assert lecture < premier < reperes
    cle = visible[lecture:premier]
    assert "C'est la référence." in cle
    assert "votre <strong>salaire</strong> pendant" in cle
    assert "votre <strong>pension</strong> une fois" in cle
    # Le mode se lit dans la clé, et il vaut pour les DEUX chiffres : c'est
    # précisément ce que la bascule garantit, et ce que le site ne faisait pas
    # quand il opposait un salaire net à une pension brute.
    # Le mot du mode et l'unité sont sur deux lignes du gabarit : on compare
    # donc sur le texte aplati, comme le lecteur le lit.
    aplati = " ".join(cle.split())
    assert "en net, l'un comme l'autre, par mois, en euros d'aujourd'hui" in aplati
    assert "au <strong>taux plein</strong>" in aplati


def test_un_scenario_n_affiche_que_les_euros_de_l_annee_de_reference(contexte):
    """UNE PENSION par scénario, et dans une seule unité.

    Chaque ligne portait deux nombres pour la même grandeur : le pouvoir
    d'achat d'aujourd'hui, et la somme nominale du mois du départ — « 3 190,21 €
    par mois, en euros de 2039 ». Des euros d'une année que personne n'a en
    poche, qu'il fallait une légende pour distinguer des autres, et qui
    doublaient les quatre lignes de la comparaison.

    Ce que ce test interdit est donc la SECONDE UNITÉ, pas le second chiffre.
    Le salaire net que le système laisse pendant la carrière a le droit de se
    tenir à côté de la pension : c'est une autre grandeur, elle porte son
    étiquette, et c'est même ce qui sépare les quatre systèmes avant la
    retraite. Une seule chose reste exigée — un seul `chiffre principal`, celui
    de la pension, et lui seul dans les euros de l'année de référence.
    """
    corps = rendre(contexte, "/simuler", SIMULATION_TEMOIN)[1]
    depart = SIMULATION_TEMOIN["liquidation"][:4]
    for bloc in corps.split('<div class="scenario">')[1:]:
        entete = bloc.split('<div class="barre')[0]
        assert entete.count('class="chiffre principal"') == 1
        assert f"en euros de {depart}" not in entete
        # L'unité longue a quitté les cartes — deux mots suffisent sous chaque
        # nombre — et la clé de lecture la porte une fois pour toutes. Ce que
        # la carte doit dire, c'est le MODE, et le même pour ses deux chiffres.
        assert entete.count("€ net/mois") == 2
        # Le second chiffre, s'il est là, dit de quoi il parle : sans son
        # étiquette, deux nombres se toucheraient sans que rien ne les sépare.
        if 'class="chiffre salaire"' in entete:
            assert ">salaire</span>" in entete
            assert "€ net/mois" in entete
    assert "Deux fois le même montant" not in corps
    assert "grand chiffre" not in corps
    assert f"en euros de {depart}" not in corps.split('<div class="carte">')[0]
    assert ("en net, l'un comme l'autre, par mois, en euros d'aujourd'hui"
            in " ".join(corps.split()))


def test_le_salaire_net_se_lit_a_cote_de_chaque_pension(contexte):
    """Les quatre systèmes portent leur salaire net, et trois portent le même.

    C'est le propos : les systèmes 1, 2 et 3 ne changent pas ce qui est
    PRÉLEVÉ, seulement ce qui est porté au compte. Voir le même nombre trois
    fois puis un quatrième différent est ce qui le montre sans une phrase.
    L'écart n'est donc écrit que sur la ligne qui en a un.
    """
    corps = rendre(contexte, "/simuler", SIMULATION_TEMOIN)[1]
    entetes = [bloc.split('<div class="barre')[0]
               for bloc in corps.split('<div class="scenario">')[1:]]
    assert len(entetes) == 4
    salaires = [re.search(r'class="chiffre salaire">\s*'
                          r'<span class="categorie">salaire</span>\s*'
                          r'<span class="somme">([^<]+)</span>', entete)
                for entete in entetes]
    assert all(salaires), "un scénario n'affiche pas son salaire net"
    montants = [s.group(1) for s in salaires]
    assert montants[0] == montants[1] == montants[2], (
        "les systèmes 1 à 3 prélèvent la même chose : leur salaire net doit "
        f"être le même, et vaut {montants[:3]}"
    )
    assert montants[3] != montants[0], (
        "le système 4 change le prélèvement : son salaire net doit différer"
    )
    assert entetes[3].count('class="ecart"') == 1
    assert sum(entete.count('class="ecart"') for entete in entetes[:3]) == 0


def test_le_tableau_du_plancher_est_en_haut_de_l_accueil(contexte):
    """L'argument le plus parlant du site — « 300 € et 1 500 € : 0 € aujourd'hui,
    500 € avec la garantie » — se lit sans rien déplier, avant le tableau qui
    oppose les deux systèmes, et n'est plus répété dans le dépliant."""
    corps = rendre(contexte, "/", {})[1]
    visible = _hors_depliants(corps)
    assert "Ce que le plancher individualisé change, par mois" in visible
    # Des espaces insécables : « 1 500 / € » se coupait en deux sur un téléphone.
    assert visible.index("300\u00a0€ et 1\u00a0500\u00a0€") < visible.index("Le système actuel et notre programme")
    assert corps.count("<caption><span>Ce que le plancher individualisé change, par mois</span></caption>") == 1
    assert "Le tableau du haut de page le montre" in corps


# -- la revue du 15 septembre 2026 : le thème « architecture » -----------------


def test_la_navigation_est_groupee_par_fonction():
    """Le message, la preuve, la confiance, et ce qu'on en fait : quatre
    groupes, et non huit liens à la file.

    Le groupement reste, et il reste DIT : chaque groupe porte son étiquette
    dans le HTML, où les synthèses vocales la lisent comme la structure du
    menu. Ce qui a changé à la refonte, c'est qu'elle ne se voit plus — huit
    pages sous quatre intertitres prenaient deux fois la hauteur du bandeau,
    devenu collant. La feuille la sort de l'écran sans la sortir de l'arbre
    d'accessibilité : `clip-path`, et non `display: none`.
    """
    entete = g.entete("/cout")
    groupes = re.findall(r'<span class="groupe"><span class="etiquette">(.*?)</span>'
                         r'<span class="liens">(.*?)</span></span>', entete)
    assert [etiquette for etiquette, _ in groupes] == [
        "Le programme", "La preuve", "La confiance", "Faire connaître"]
    pages = [re.findall(r'href="([^"]+)"', liens) for _, liens in groupes]
    assert pages == [["#/"],
                     ["#/simuler", "#/trajectoire", "#/cas-types", "#/cout",
                      "#/avantages"],
                     ["#/methode", "#/donnees"],
                     ["#/partager"]]
    assert 'href="#/cout" aria-current="page"' in entete
    assert [chemin for chemin, _ in g.LIENS] == [
        "/", "/simuler", "/trajectoire", "/cas-types", "/cout", "/avantages",
        "/methode", "/donnees", "/partager"]
    # Toute page de la barre est une page que le routeur sait rendre, et
    # réciproquement : depuis le retrait des mentions légales, le site n'a plus
    # aucune page hors barre.
    assert set(chemin for chemin, _ in g.LIENS) == set(TITRES)
    # L'étiquette est masquée à l'œil, pas à l'oreille.
    assert "nav .etiquette" in g.FEUILLE_DE_STYLE
    etiquette = g.FEUILLE_DE_STYLE.split("nav .etiquette {")[1].split("}")[0]
    assert "clip-path" in etiquette and "display: none" not in etiquette, (
        "une étiquette en display:none quitte aussi l'arbre d'accessibilité"
    )
    # L'onglet courant ne se signale pas QUE par la couleur : un soulignement
    # épais le marque, et `aria-current` l'annonce.
    actif = g.FEUILLE_DE_STYLE.split('nav a[aria-current="page"] {')[1].split("}")[0]
    assert "border-bottom-color" in actif


def test_les_pages_complementaires_se_renvoient_l_une_a_l_autre(contexte):
    """Programme, Méthode et Cas types se renvoient dans les deux sens.

    Programme renvoyait à Méthode et à Cas types ; rien ne revenait. Méthode
    renvoie désormais au programme et aux treize carrières, Cas types à la
    proposition. Le contrôle porte sur les six sens.
    """
    pages = {chemin: rendre(contexte, chemin, {})[1]
             for chemin in ("/", "/methode", "/cas-types")}
    for depuis, vers in (("/", "/methode"), ("/", "/cas-types"),
                         ("/methode", "/"), ("/methode", "/cas-types"),
                         ("/cas-types", "/methode"), ("/cas-types", "/")):
        assert f'href="{g.lien(vers)}"' in pages[depuis], f"{depuis} ne renvoie pas vers {vers}"
    assert "treize carrières types</a> montrent ce\nqu'elle déplace" in pages["/methode"]
    assert '<a href="#/">la proposition</a>' in pages["/cas-types"]


def test_la_methode_dit_comment_le_site_est_construit(contexte):
    """L'argument de confiance d'un public technique, sur la page Méthode.

    Un dépliant dit le modèle de référence, le portage sans bibliothèque, les
    témoins comparés, le paquet de données — sans un nombre de tests ni de
    témoins, qui dériveraient : le README les porte, et un test les recalcule.
    """
    corps = rendre(contexte, "/methode", {})[1]
    section = re.search(r'<details class="section"><summary>.*?<span>Comment ce site est '
                        r'construit, et comment on le vérifie</span></summary>(.*?)</details>',
                        corps, re.S)
    assert section, "le dépliant de construction manque"
    dedans = section.group(1)
    for attendu in (f'href="{g.DEPOT}/tree/main/src"', "portage en JavaScript",
                    "comparée caractère par caractère", f'href="{g.DEPOT}/tree/main/tests"',
                    'href="#/donnees"'):
        assert attendu in dedans, attendu
    assert not re.search(r"\b\d{3,} (?:tests|témoins|carrières)", dedans), (
        "un nombre de tests ou de témoins écrit à la main dériverait"
    )


def test_la_page_donnees_se_lit_comme_une_base(contexte):
    """Deux tables filtrables et triables : l'inventaire, croisé par famille,
    couverture et fiabilité, et les séries certifiées, par niveau."""
    corps = rendre(contexte, "/donnees", {})[1]
    inventaire = re.search(r'<table id="inventaire">.*?</table>', corps, re.S).group(0)
    assert 'id="inventaire-fiabilite"' in corps and 'data-filtre="fiabilite"' in corps
    fiabilites = re.findall(r'data-fiabilite="([^"]*)"', inventaire)
    assert len(fiabilites) == inventaire.count("<tr ")
    assert {f for f in fiabilites if f} <= {"certifiee", "haute", "moyenne", "estimee"}
    assert any(fiabilites), "aucune fiche calculée ne porte sa fiabilité"

    series = re.search(r'<table id="series">.*?</table>', corps, re.S)
    assert series, "la table des séries n'est plus filtrable"
    assert 'data-cible="series"' in corps and 'id="series-recherche"' in corps
    assert 'data-filtre="niveau"' in corps
    assert series.group(0).count('<button type="button" class="tri"') == 5
    assert len(re.findall(r'<tr data-niveau="', series.group(0))) == series.group(0).count("<tr ")
    assert 'data-compte-de="series" data-unite="séries">' in corps

    from pathlib import Path

    page_html = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
    assert 'compte.dataset.unite' in page_html


def test_chaque_route_porte_sa_description():
    """Une méta-description par page, que le routeur pose comme il pose le
    titre — et la même table des deux côtés du portage."""
    import json
    import shutil
    import subprocess
    from pathlib import Path

    from retraite_notionnelle.web.pages import DESCRIPTIONS

    assert set(DESCRIPTIONS) == set(TITRES)
    for chemin, description in DESCRIPTIONS.items():
        assert 60 <= len(description) <= 250, f"{chemin} : {len(description)} caractères"
        assert description.endswith("."), chemin
    racine = Path(__file__).resolve().parents[1]
    page = (racine / "index.html").read_text(encoding="utf-8")
    assert "DESCRIPTIONS[cible.chemin]" in page
    assert "description.content = " in page
    # La description de l'accueil est celle que le HTML servi porte déjà : la
    # première page ne doit pas changer de description en s'ouvrant.
    assert f'<meta name="description" content="{DESCRIPTIONS["/"]}">' in page

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    lecture = subprocess.run(
        ["node", "--input-type=module", "-e",
         'import { DESCRIPTIONS } from "./moteur/js/pages.js";'
         "process.stdout.write(JSON.stringify(DESCRIPTIONS));"],
        cwd=racine, capture_output=True, text=True, check=True,
    )
    assert json.loads(lecture.stdout) == DESCRIPTIONS


# -- la revue du 15 septembre 2026 : le thème « gommer la touche IA » ----------


def _prose(corps: str) -> str:
    """Le texte d'une page hors de ses tableaux, où « — » est une case vide.

    Le bloc de réglages des pages agrégées en sort aussi : ce sont les champs
    du simulateur, rendus une seconde fois, et le tiret de « Masse salariale —
    règle d'équilibre » y sépare un libellé de sa glose, il n'y ouvre pas une
    incise. Les compter sur trois pages de plus ne dirait rien de leur prose ;
    ils restent comptés là où ils sont écrits, dans les options du simulateur.
    """
    sans_reglages = re.sub(r'<details class="section options reglages"[^>]*>.*?</details>', " ",
                           corps, flags=re.S)
    sans_tables = re.sub(r"<table.*?</table>", " ", sans_reglages, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", sans_tables)))


#: Le nombre de phrases portant une incise en tiret cadratin que chaque page
#: peut encore compter, hors tableaux. Les bornes sont celles de la relecture
#: de septembre 2026, où le site en comptait de deux à quatre fois plus : elles
#: n'interdisent pas l'incise, qui est une ponctuation française, elles
#: interdisent d'y revenir comme à un tic.
INCISES_MAXIMUM = {
    "/": 3, "/simuler": 14, "/trajectoire": 5, "/cas-types": 9, "/cout": 22,
    "/methode": 9, "/donnees": 6, "/partager": 4,
    # Celles qui restent sur Avantages sont citées et non rédigées : le
    # message de refus du garde-fou, et une énumération de choix que le dépôt
    # refuse de trancher à la place du lecteur.
    "/avantages": 3,
}


@pytest.mark.parametrize("chemin", list(TITRES))
def test_les_incises_en_tiret_restent_rares(contexte, chemin):
    """Le tiret cadratin en incise — « — c'est-à-dire […] — » — est le tic de
    ponctuation le plus reconnaissable d'un texte généré, et le site en
    faisait un usage dense : quatorze phrases sur l'accueil, une quarantaine
    sur Coût. La plupart sont devenues des parenthèses, des deux-points ou des
    phrases séparées ; ce test tient le compte."""
    prose = _prose(rendre(contexte, chemin, {})[1])
    phrases = [p for p in re.split(r"(?<=[.!?])\s+", prose) if " — " in p]
    assert len(phrases) <= INCISES_MAXIMUM[chemin], (
        f"{chemin} : {len(phrases)} phrases avec une incise en tiret, "
        f"{INCISES_MAXIMUM[chemin]} au plus — " + " | ".join(p[:80] for p in phrases)
    )


@pytest.mark.parametrize("chemin", list(TITRES))
def test_le_procede_ce_n_est_pas_x_c_est_y_a_disparu(contexte, chemin):
    """« Ce n'est pas une économie, c'est une marge » : efficace une fois,
    reconnaissable comme procédé à la dixième. Le site le répétait sur chaque
    page ; il n'en reste aucun, et les contrastes se disent autrement — une
    comparaison, un exemple, une question."""
    prose = _prose(rendre(contexte, chemin, {})[1])
    procede = re.compile(r"(?:n'est pas|ne sont pas)[^.;]{0,80}?(?:, c'est|: c'est)|, et non |\bnon pas ")
    trouves = procede.findall(prose)
    assert not trouves, f"{chemin} : {trouves}"


def test_le_programme_casse_ses_triades_et_porte_une_voix(contexte):
    """« Il est illisible. Il est inégal. Il n'est pas piloté. » est devenu une
    liste asymétrique, et l'accueil porte une note signée : qui publie ce
    site, pourquoi, et avec quelles réserves.

    La note a changé de place à la refonte en affiche. Elle était le quatrième
    bloc de texte du premier écran ; elle est maintenant dans le dépliant qui
    dit comment vérifier, parce que c'est le même geste — et parce que le
    premier écran doit tenir son budget de lecture. Ce qui reste visible est
    l'engagement, en une phrase sur le panneau crème : tout est chiffré, sur
    des données publiques et un modèle ouvert."""
    corps = rendre(contexte, "/", {})[1]
    assert "Il est illisible." not in corps and "Il n'est pas piloté." not in corps
    assert "Illisible, d'abord." in corps and "Et personne ne le pilote." in corps
    note = re.search(r'<div class="note signee">(.*?)</div>', corps, re.S)
    assert note, "la note signée manque"
    assert "Nous avons choisi" in note.group(1)
    assert "Nos réserves sont écrites" in note.group(1)
    assert "Le Parti libéral français, septembre 2026." in note.group(1)
    # Elle est rangée, pas supprimée : dans le dépliant « Tout vérifier ».
    assert "Pourquoi ce site." not in _hors_depliants(corps)
    verifier = corps[corps.index("Tout vérifier, page par page"):]
    assert "Pourquoi ce site." in verifier
    # Et l'engagement, lui, reste sous les yeux.
    visible = _hors_depliants(corps)
    assert "Vérifiez plutôt que de nous croire" in visible
    assert "sur des données publiques" in visible


def test_la_rubrique_des_reserves_de_la_page_cout_ne_suit_plus_le_patron(contexte):
    """« Ce que cette page ne dit pas » était un titre de gabarit, le même
    d'une page à l'autre ; celui de Coût dit ce qu'il contient, et une phrase
    d'entrée dit pourquoi il est là."""
    for chemin in TITRES:
        corps = rendre(contexte, chemin, {})[1]
        assert "<span>Ce que cette page ne dit pas</span>" not in corps, chemin
        assert "ne dit pas</span>" not in corps, chemin
    cout = rendre(contexte, "/cout", {})[1]
    # Le nombre est dans le titre, et il doit suivre la liste : le volet C en a
    # ajouté une douzième, sur ce que les scénarios font de la réversion.
    assert "<span>Douze réserves à lire avant de citer ces chiffres</span>" in cout
    assert "Une page de chiffres vaut par ce qu'elle laisse de côté" in cout
    debut = cout.index("Une page de chiffres vaut par ce qu'elle laisse de côté")
    liste = cout[debut:cout.index("</ul>", debut)]
    assert liste.count("<li><strong>") == 12, liste.count("<li><strong>")



# -- action 13 : la certification datée série par série -------------------------


def test_la_page_donnees_ne_promet_que_la_plus_ancienne_verification(contexte):
    """« Recontrôlé le 16 septembre » était la date du dernier passage, fût-il
    partiel. La page dit désormais le MINIMUM des dates de fiche — la seule
    affirmation que le journal soutient —, et la table date chaque série."""
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.donnees.chargement import journal_certification

    journal = journal_certification(RACINE_DONNEES)
    dates = sorted(trace["verifiee_le"] for trace in journal["series"].values())
    corps = rendre(contexte, "/donnees", {})[1]
    ancienne = _date_en_clair(dates[0])
    recente = _date_en_clair(dates[-1])
    assert f"la vérification la plus ancienne remonte au {ancienne}" in re.sub(
        r"\s+", " ", corps)
    assert f"la plus récente au {recente}" in re.sub(r"\s+", " ", corps)
    assert journal["dernier_passage_le"] not in corps.split("<table")[0], (
        "la date du dernier passage ne doit plus être présentée comme celle de tout"
    )
    table = re.search(r'<table id="series">.*?</table>', corps, re.S).group(0)
    assert '<th class="texte date" scope="col"><button type="button" class="tri" data-colonne="3">Vérifiée le</button></th>' in table
    assert table.count(f">{dates[0]}<") >= 1


# -- les trois pages agrégées obéissent aux réglages du simulateur ------------
#
# Elles ne calculent aucune carrière saisie — elles croisent des carrières
# types avec des générations —, mais elles doivent le faire sous les MÊMES
# règles que le simulateur. Jusqu'au 19 septembre 2026, elles calculaient
# toujours sous les paramètres par défaut : changer l'indexation dans le
# simulateur déplaçait la pension affichée, et pas un chiffre de la page Coût.
# Les deux pages disaient alors, sans le dire, deux choses différentes.


@pytest.mark.parametrize("chemin", list(PAGES_AGREGEES))
def test_une_page_agregee_porte_son_bloc_de_reglages(page, chemin):
    corps = page(chemin)
    assert 'class="section options reglages"' in corps
    assert "Recalculer cette page" in corps
    # Le formulaire vise la route NUE : le routeur colle la requête derrière
    # l'action, et une action qui en porterait déjà une en donnerait deux.
    assert f'action="#{chemin}"' in corps


@pytest.mark.parametrize("chemin", list(PAGES_AGREGEES))
def test_une_page_agregee_au_defaut_ne_dit_rien_des_reglages(page, chemin):
    """Tant que rien n'est changé, la page est celle d'avant."""
    corps = page(chemin)
    assert "ne sont pas ceux des réglages par défaut" not in corps
    # Et ses liens sont nus : une adresse partagée ne porte que ce que son
    # auteur a effectivement réglé.
    assert '<a href="#/cout"' in corps or '<a href="#/simuler"' in corps
    assert "#/cout?" not in corps


@pytest.mark.parametrize("chemin", list(PAGES_AGREGEES))
def test_un_reglage_explicite_au_defaut_rend_la_page_du_defaut(page, chemin):
    """« indexation=masse_salariale » est le défaut : la page ne doit pas bouger.

    C'est ce qui garantit que la lecture des réglages est ADDITIVE : une
    adresse qui ne demande rien de neuf rend exactement la page d'avant.
    """
    assert page(chemin, indexation="masse_salariale") == page(chemin)


@pytest.mark.parametrize("chemin", list(PAGES_AGREGEES))
def test_une_page_agregee_ignore_la_carriere_de_l_adresse(page, chemin):
    """Une adresse de simulateur collée sur la page Coût n'y décrit que des règles.

    La naissance, le statut et le revenu qu'elle porte n'ont aucun sens dans un
    agrégat : ils sont ignorés, et une faute dans l'un d'eux ne peut pas faire
    échouer la page.
    """
    assert page(chemin, naissance="1962", statut="fonctionnaire_civil",
                salaire="3000", unite_revenu="euros_mois") == page(chemin)


@pytest.mark.parametrize("chemin", list(PAGES_AGREGEES))
def test_une_page_agregee_dit_quand_elle_n_est_plus_au_defaut(page, chemin):
    corps = page(chemin, indexation="prix", bascule="2030")
    assert "ne sont pas ceux des réglages par défaut" in corps
    # L'apostrophe est échappée dans la page : on compare sur le texte lu.
    assert "règle d'indexation : Prix" in html.unescape(corps)
    assert "année de bascule : 2030" in corps
    # Et de quoi revenir en arrière, sans avoir à effacer une adresse à la main.
    assert f'<a href="#{chemin}">revenir aux réglages par défaut</a>' in corps


@pytest.mark.parametrize("chemin", list(PAGES_AGREGEES))
def test_les_reglages_suivent_le_lecteur_d_une_page_a_l_autre(page, chemin):
    """Sans cela, changer une règle ici et cliquer là ramènerait au défaut."""
    corps = page(chemin, indexation="prix")
    assert '<a href="#/simuler?indexation=prix"' in corps
    assert '#/methode?indexation=prix' in corps
    # Le bandeau de navigation les porte aussi : c'est lui qu'on clique.
    assert '#/cout?indexation=prix' in g.entete(chemin)


def test_un_reglage_deplace_les_chiffres_de_la_page_cout(contexte):
    """Le cœur de l'affaire : ce sont les CHIFFRES qui doivent bouger.

    L'indexation sur les prix, au lieu de la croissance de la masse salariale,
    écrase la valeur réelle des comptes notionnels : la masse de pensions que
    chaque système notionnel servirait s'en trouve nettement réduite. Le
    rapport que la page trace est celui-là.
    """
    defaut = contexte.cout()
    prix = contexte.pour(
        Saisie.modelisation({"indexation": "prix"}).parametres(contexte.base)
    ).cout()
    annee = defaut.derniere_annee
    for scenario in ("notionnel_retroactif", "notionnel_liberal"):
        assert prix.annee(annee).rapports[scenario] < defaut.annee(annee).rapports[scenario]
    # Et le contexte d'origine n'a pas bougé : deux jeux de règles cohabitent.
    assert contexte.cout().annee(annee).rapports == defaut.annee(annee).rapports


def test_un_reglage_hors_bornes_ne_fait_pas_tomber_la_page(page):
    """Une adresse mal formée doit afficher une phrase, pas une trace d'exécution."""
    corps = page("/cout", bascule="1800")
    assert "Saisie refusée" in corps
    # Et la page est rendue derrière, sous les règles par défaut.
    assert "ne sont pas ceux des réglages par défaut" not in corps
    assert 'class="section options reglages"' in corps


def test_une_adresse_qui_ne_porte_que_des_reglages_ne_demande_pas_de_calcul(page):
    """Cliquer « Simuler » dans le bandeau ne doit pas calculer une carrière.

    Les liens du site portent les réglages partout, y compris vers le
    simulateur. Sans cette règle, le seul fait d'avoir changé l'indexation
    aurait fait calculer d'office, à chaque passage par le bandeau, la carrière
    d'exemple que personne n'a saisie.
    """
    assert "Saisie refusée" not in page("/simuler", indexation="prix")
    assert not Saisie.depuis_requete({"indexation": "prix"}).demandee
    assert Saisie.depuis_requete({"naissance": "1975"}).demandee


def test_un_contexte_derive_partage_ce_qui_ne_depend_pas_des_regles(contexte):
    """Dériver ne doit rien recharger : les séries observées sont les mêmes."""
    derive = contexte.pour(
        Saisie.modelisation({"bascule": "2030"}).parametres(contexte.base))
    assert derive is not contexte
    assert derive.depenses() is contexte.depenses()
    assert derive.comptes() is contexte.comptes()
    assert derive.population() is contexte.population()
    # Un jeu de règles identique ne dérive rien du tout.
    assert contexte.pour(contexte.base) is contexte


def test_les_champs_de_modelisation_sont_ecrits_une_seule_fois(contexte):
    """Le simulateur et les pages agrégées proposent le MÊME jeu de règles.

    Deux listes de champs auraient suffi à les faire diverger, et deux pages du
    même site auraient alors proposé deux jeux de règles qui n'en sont qu'un.
    """
    champs = _champs_modelisation(Saisie())
    assert champs in rendre(contexte, "/simuler", {})[1]
    assert champs in rendre(contexte, "/cout", {})[1]


def test_le_routeur_ne_prend_pas_une_adresse_reglee_pour_une_simulation():
    """« #/?indexation=prix » est l'accueil réglé, et non une vieille adresse.

    Le routeur d'``index.html`` renvoie sur le simulateur toute adresse qui
    porte « #/ » suivi d'une requête : ce sont les liens partagés d'avant que
    l'accueil ne devienne le programme. Depuis que les réglages suivent le
    lecteur, le lien de l'accueil en porte une lui aussi — et cliquer
    « Programme » après avoir changé l'indexation envoyait sur le simulateur.
    """
    from pathlib import Path

    page = (Path(__file__).resolve().parents[1] / "index.html").read_text(
        encoding="utf-8")
    assert "CLES_MODELISATION" in page, (
        "le routeur doit savoir distinguer une règle d'un champ de carrière"
    )
    assert "!CLES_MODELISATION.includes(cle)" in page


def test_la_bascule_net_brut_decrit_la_meme_carriere(contexte):
    """Le piège que ce lien existe pour éviter, et c'est le même qu'à l'unité.

    En mode net, le nombre du formulaire est un NET. Le recopier tel quel dans
    l'autre mode le ferait relire comme un brut, et la page reviendrait en
    décrivant une autre carrière — mieux payée d'un quart. Le lien porte donc
    le montant traduit, et l'aller-retour doit retomber sur le nombre de
    départ.
    """
    depart = {"naissance": "1975", "unite_revenu": "euros_mois",
              "salaire": "2500", "montants": "net"}
    # La bascule écrit ses DEUX états ; celui qui s'applique n'est pas un lien.
    # On cherche donc la branche « brut » sous sa forme de lien, et on vérifie
    # au passage que « net » est bien marqué comme l'état courant.
    corps = rendre(contexte, "/simuler", depart)[1]
    assert '<span class="actif" aria-current="true">net</span>' in corps
    lien = re.search(r'<a href="#/simuler\?([^"]*)">brut</a>', corps)
    assert lien, "la page ne porte pas de branche « brut »"
    vers_brut = dict(parse_qsl(html.unescape(lien.group(1))))
    assert vers_brut["montants"] == "brut"
    # Un net de 2 500 € vaut un brut d'environ 3 160 € pour un salarié du privé.
    assert 3000 < float(vers_brut["salaire"]) < 3300

    retour = rendre(contexte, "/simuler", vers_brut)[1]
    assert '<span class="actif" aria-current="true">brut</span>' in retour
    lien = re.search(r'<a href="#/simuler\?([^"]*)">net</a>', retour)
    assert lien, "la page ne porte pas de branche « net »"
    vers_net = dict(parse_qsl(html.unescape(lien.group(1))))
    assert float(vers_net["salaire"]) == pytest.approx(2500, abs=2)


def test_les_deux_modes_decrivent_la_meme_pension_a_neuf_points_pres(contexte):
    """Même carrière, deux modes : le rapport des pensions est celui du barème.

    C'est le seul test qui relie les deux moitiés de la bascule — la saisie,
    qui convertit un net en brut, et l'affichage, qui retire 9,1 % de la
    pension. S'il tombe, l'une des deux a bougé sans l'autre.
    """
    def pension(parametres):
        corps = rendre(contexte, "/simuler", parametres)[1]
        entete = corps.split('<div class="scenario">')[1].split('<div class="barre')[0]
        brut = re.search(r'class="chiffre principal">\s*'
                         r'<span class="categorie">retraite</span>\s*'
                         r'<span class="somme">([^<]+)</span>', entete)
        assert brut, entete[:200]
        return float(brut.group(1).replace(" ", "").replace(",", "."))

    commun = {"naissance": "1985-03-01", "sexe": "F",
              "statut": "salarie_prive_non_cadre", "debut": "2007-09-01",
              "liquidation": "2049-03-01", "unite_revenu": "euros_mois"}
    # Le même salaire, dit une fois en brut et une fois en net : la bascule
    # donne la correspondance, et on la reprend ici pour ne pas la deviner.
    en_brut = pension({**commun, "salaire": "3158", "montants": "brut"})
    en_net = pension({**commun, "salaire": "2500", "montants": "net"})
    assert en_net == pytest.approx(en_brut * (1 - 0.091), rel=2e-3)


def test_le_mode_des_montants_voyage_dans_l_adresse(contexte):
    """Une adresse partagée décrit la carrière qu'on a calculée, mode compris.

    Le mode gouverne l'interprétation du nombre « salaire » : une adresse qui
    l'omettrait retomberait sur le défaut et décrirait une autre carrière.
    C'est pourquoi `requete` l'écrit toujours, comme l'unité.
    """
    saisie = Saisie.depuis_requete({"naissance": "1975", "montants": "brut"})
    assert "montants=brut" in saisie.requete()
    assert "montants=net" in Saisie.depuis_requete({"naissance": "1975"}).requete()
    # Et le formulaire le renvoie quand on le soumet, par un champ caché.
    corps = rendre(contexte, "/simuler", {"naissance": "1975", "montants": "brut"})[1]
    assert '<input type="hidden" name="montants" value="brut">' in corps


def test_le_taux_de_remplacement_parle_la_langue_du_mode(contexte):
    """Le défaut que la question « obtient-on les mêmes chiffres ? » a révélé.

    Le modèle calcule le taux de remplacement BRUT sur BRUT. Affiché tel quel à
    côté de montants nets, il serait le seul chiffre de la page à parler
    l'autre langue — et il mentirait dans un sens précis : une pension est
    moins prélevée qu'un salaire, 9,1 % contre une vingtaine de points, si bien
    que le taux NET dépasse le taux brut de plusieurs points. C'est un fait
    connu du système français, et rarement montré.
    """
    commun = {"naissance": "1985-03-01", "sexe": "F",
              "statut": "salarie_prive_non_cadre", "debut": "2007-09-01",
              "liquidation": "2049-03-01", "unite_revenu": "euros_mois"}

    def taux(parametres):
        corps = rendre(contexte, "/simuler", parametres)[1]
        lus = []
        for bloc in corps.split('<div class="scenario">')[1:]:
            glose = bloc.split('class="glose"')[1].split("</div>")[0]
            plat = " ".join(re.sub(r"<[^>]+>", "", html.unescape(glose)).split())
            trouve = re.search(r"(\d+,\d+) % · écart", plat)
            assert trouve, plat[:120]
            lus.append(float(trouve.group(1).replace(",", ".")))
        return lus

    en_brut = taux({**commun, "salaire": "3158", "montants": "brut"})
    en_net = taux({**commun, "salaire": "2500", "montants": "net"})
    assert len(en_brut) == 4
    for brut, net in zip(en_brut, en_net):
        assert net > brut, "le taux net doit dépasser le taux brut"
        # Le rapport des deux prélèvements : 0,909 de pension contre environ
        # 0,79 de salaire. Une fourchette large suffit — elle n'est pas là pour
        # valider un dixième de point, mais pour attraper un taux resté brut.
        assert 1.10 < net / brut < 1.20, f"{net} / {brut}"


def test_la_bascule_ecrit_ses_deux_etats_et_dit_lequel_s_applique(contexte):
    """Ce qui sépare une bascule d'un lien, et pourquoi elle l'a remplacé.

    Un lien seul — « Voir les montants en brut » — demande au lecteur de
    déduire l'état courant de la phrase qui propose d'en changer, ce que
    personne ne fait, et il ne se voit pas parce qu'il ressemble au texte. Les
    deux états côte à côte disent à la fois où l'on est et où l'on peut aller.

    Trois propriétés, et chacune a coûté un aller-retour : les deux libellés
    sont là, un seul est un lien, et l'état courant porte `aria-current` — sans
    quoi une synthèse vocale lirait deux mots sans savoir lequel s'applique.
    """
    for mode, autre in (("net", "brut"), ("brut", "net")):
        corps = rendre(contexte, "/simuler",
                       {"naissance": "1975", "montants": mode})[1]
        bascules = re.findall(
            r'<div class="bascule" role="group" aria-label="Montants">.*?</div>',
            corps, re.S)
        assert bascules, "la page ne porte aucune bascule de montants"
        for bloc in bascules:
            assert f'<span class="actif" aria-current="true">{mode}</span>' in bloc
            assert f">{autre}</a>" in bloc
            # Un seul lien : l'état courant n'a pas d'adresse, c'est celle où
            # l'on est déjà.
            assert bloc.count("<a href=") == 1
            assert 'role="group"' in bloc and 'aria-label="Montants"' in bloc


def test_l_aide_du_champ_ne_promet_pas_une_conversion_qui_n_aura_pas_lieu(contexte):
    """Deux phrases contradictoires à deux lignes d'écart, et rien pour trancher.

    Sous un statut dont le dépôt n'a pas les prélèvements hors retraite — la
    MSA, l'élu, l'ultramarin, qui n'a pas d'emploi —, le nombre saisi est lu
    TEL QUEL. Un avertissement le disait ; l'aide du champ, juste au-dessus,
    continuait de promettre que « le modèle remonte au brut par les
    prélèvements de votre statut ». Le lecteur voyait donc deux phrases se
    contredire sans savoir laquelle le concernait.
    """
    base = {"naissance": "1985-03-01", "sexe": "F", "debut": "2007-09-01",
            "liquidation": "2049-03-01", "unite_revenu": "euros_mois",
            "salaire": "1800", "montants": "net"}
    promesse = "remonte au brut par les prélèvements de votre statut"
    # Là où la conversion a lieu, l'aide la décrit.
    corps = rendre(contexte, "/simuler",
                   {**base, "statut": "salarie_prive_non_cadre"})[1]
    assert promesse in corps
    assert "il ne peut pas remonter au brut" not in corps
    # Là où elle n'a pas lieu, l'aide le dit, et l'avertissement la double.
    for statut in ("salarie_agricole", "elu_local", "salarie_mayotte",
                   "sans_activite"):
        corps = rendre(contexte, "/simuler", {**base, "statut": statut})[1]
        assert promesse not in corps, f"{statut} : l'aide promet une conversion"
        assert "il ne peut pas remonter au brut" in corps, statut
        assert "lu <strong>tel quel</strong>" in corps, statut


def test_la_cle_de_lecture_ne_dement_jamais_les_chiffres_qu_elle_explique(contexte):
    """Une clé de lecture fausse est pire qu'absente : elle enseigne l'erreur.

    Elle a dit « Montants BRUTS et au centime, comme la caisse les verse :
    avant CSG, CRDS et impôt » au-dessus de quatre montants nets, et « un brut
    sur un brut, donc plus bas qu'un taux calculé sur des nets » au-dessus d'un
    taux de remplacement calculé, précisément, sur des nets — en disant donc au
    lecteur de corriger mentalement dans le mauvais sens le seul chiffre de la
    page qu'il ne peut pas vérifier.
    """
    saisie = {"naissance": "1985-03-01", "sexe": "F",
              "statut": "salarie_prive_non_cadre", "debut": "2007-09-01",
              "liquidation": "2049-03-01", "unite_revenu": "euros_mois",
              "salaire": "2500"}
    attendu = {
        "net": ("Montants <strong>nets</strong>", "un net sur un net"),
        "brut": ("Montants <strong>bruts</strong>", "un brut sur un brut"),
    }
    for mode, (montants, rapport) in attendu.items():
        corps = rendre(contexte, "/simuler", {**saisie, "montants": mode})[1]
        assert montants in corps, f"{mode} : la clé de lecture ne dit pas l'unité"
        assert rapport in corps, f"{mode} : le taux de remplacement est mal décrit"
        # Et surtout : elle ne dit pas l'autre.
        autre_montants, autre_rapport = attendu["brut" if mode == "net" else "net"]
        assert autre_montants not in corps, f"{mode} : la clé annonce l'autre unité"
        assert autre_rapport not in corps, f"{mode} : le taux annonce l'autre unité"
    # Le glossaire, lui, sert les deux modes ET les pages qui n'ont pas de
    # bascule : il ne peut donc nommer ni l'un ni l'autre.
    assert "Ici, un brut sur un brut" not in g.GLOSSAIRE["taux de remplacement"]


def test_aucune_adresse_du_site_ne_porte_deux_croisillons(contexte):
    """Le bogue qui a cassé la bascule, et que rien ne voyait venir.

    Ici la ROUTE vit dans le fragment : `#/simuler?...`. Ajouter une ancre de
    section au bout — `#resultats`, pour revenir sur les chiffres — ne fabrique
    donc pas une ancre, mais allonge la DERNIÈRE VALEUR de la requête. La
    bascule des résultats écrivait `montants=brut#resultats`, qui n'est pas un
    mode connu : le modèle retombait sur son défaut, la page revenait en net,
    et le salaire déjà converti en brut y était relu comme un net — une
    carrière mieux payée d'un quart, sans un mot.

    Le test vaut pour tout le site, et pas pour la seule bascule : c'est un
    piège de la forme des adresses, que n'importe quel lien peut retrouver.
    Pour aller à une section, le site a `data-vers`, que le routeur traite
    sans toucher à l'adresse.
    """
    routes = [("/simuler", {"naissance": "1975", "montants": "net"}),
              ("/simuler", {"naissance": "1975", "montants": "brut"}),
              ("/", {}), ("/cout", {}), ("/donnees", {}), ("/programme", {})]
    for route, parametres in routes:
        corps = rendre(contexte, route, parametres)[1]
        for adresse in re.findall(r'href="([^"]*)"', corps):
            fragment = html.unescape(adresse)
            assert fragment.count("#") <= 1, (
                f"{route} : l'adresse {fragment!r} porte deux croisillons ; "
                "la route occupe déjà le fragment, un second `#` entre dans "
                "la requête")


def test_les_deux_branches_d_une_bascule_ne_se_separent_jamais(contexte):
    """Sur un téléphone, c'est la légende qui passe à la ligne, pas le contrôle.

    La première version mettait la légende et les deux branches à plat dans un
    conteneur qui se replie : à 390 px, « UNITÉ » gardait « € par mois » et
    renvoyait « × salaire moyen » à la ligne suivante. Deux touches décalées
    d'une ligne ne se lisent plus comme un choix entre deux états — elles se
    lisent comme deux boutons. Les branches vivent donc dans une enveloppe
    commune, que la feuille de style déclare insécable.
    """
    corps = rendre(contexte, "/simuler", {"naissance": "1975"})[1]
    bascules = re.findall(
        r'<div class="bascule" role="group" aria-label="[^"]+">(.*?)</div>',
        corps, re.S)
    assert bascules, "la page ne porte aucune bascule"
    for dedans in bascules:
        # L'enveloppe est le DERNIER enfant de la bascule : ce qu'elle
        # contient court jusqu'à son `</span>` final.
        choix = re.search(r'<span class="choix">(.*)</span>\s*$', dedans, re.S)
        assert choix, f"les branches ne sont pas enveloppées : {dedans}"
        # Les deux états sont DANS l'enveloppe, et la légende en dehors.
        assert choix.group(1).count("<a href=") == 1
        assert 'class="actif"' in choix.group(1)
        assert 'class="legende"' not in choix.group(1)
    assert ".bascule > .choix" in g.FEUILLE_DE_STYLE
    assert "flex-wrap: nowrap" in g.FEUILLE_DE_STYLE


def test_la_bascule_des_resultats_precede_les_montants(contexte):
    """Un réglage qu'on découvre après avoir lu les chiffres arrive trop tard.

    Elle était sous les quatre systèmes, entre eux et la fiabilité : on lisait
    quatre nombres, puis on apprenait qu'on aurait pu les lire autrement. Elle
    ouvre maintenant la carte.
    """
    corps = rendre(contexte, "/simuler", SIMULATION_TEMOIN)[1]
    carte = corps.split('<h2 id="resultats"')[1]
    assert carte.index('class="bascule"') < carte.index('<div class="scenario">')
