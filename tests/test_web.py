"""Tests du contenu du site.

Le site tourne entièrement dans le navigateur ; ce qu'il affiche est produit ici
par :mod:`retraite_notionnelle.web.pages`, qui ne dépend que de la bibliothèque
standard et sert de référence au portage JavaScript.
"""

from __future__ import annotations

import dataclasses
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
from retraite_notionnelle.donnees.bilan import EcartsFiges
from retraite_notionnelle.donnees.chargement import (
    DonneeInsuffisante,
    charger_periodes_non_travaillees,
)
from retraite_notionnelle.web.pages import (
    _annee_flux,
    _annees_cascade,
    _annees_flux,
    _caisse_flux,
    _compte_flux,
    _date_en_clair,
    _libelles_cascade,
    _marches_cascade,
    _milliards,
    _part_et_milliards,
    _pib_de_conversion,
    COMPOSANTE_GARANTIE,
    MARCHES_HORS_SYSTEMES,
    MARCHES_SYSTEMES,
    _VUES_DE_PAGE,
    SCENARIOS_MONTRES,
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
    POPULATIONS,
    RATTACHEMENTS,
    TABLES,
    TITRES,
    Contexte,
    ErreurSaisie,
    Saisie,
    _champs_modelisation,
    _fraction_en_mots,
    _ordre_de_grandeur,
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


@pytest.mark.parametrize("chemin", ["/", "/simuler", "/cas-types", "/methode"])
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
    l'autre est maintenant dans son titre — l'assiette, dite du point de vue
    du lecteur : ce qu'il a cotisé, sa part seule ou les deux —, et depuis
    quand la carrière est recalculée est dans la glose.
    """
    texte = page("/simuler", naissance=1960, statut="agent_sncf",
                 debut=20, liquidation=52)
    for attendu in ("1. Système de répartition actuel",
                    "2. Ce que vous avez cotisé, part salariale seule",
                    "3. Ce que vous avez cotisé, part salariale + patronale",
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
        assert f"Revenu d&#x27;activité {mode} mensuel" in corps
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


def test_le_champ_de_revenu_ecarte_la_pension(contexte):
    """Un retraité ne doit pas pouvoir y écrire sa pension sans être averti.

    « Revenu mensuel », sous une date de départ déjà passée, se lit comme « ce
    que vous touchez aujourd'hui ». Le montant serait alors cotisé comme un
    salaire, et la pension rendue serait fausse sans rien avoir l'air de l'être
    — d'où le mot « d'activité » dans le LIBELLÉ, qui se lit sans rien ouvrir,
    et la conduite à tenir dans le complément, dans les deux unités de saisie.
    """
    for unite, libelle in (("euros_mois", "Revenu d&#x27;activité"),
                           ("moyen", "Niveau de revenu d&#x27;activité")):
        _, corps = rendre(contexte, "/simuler", {"unite_revenu": unite})
        assert libelle in corps
        assert "Jamais une pension" in corps
        assert "déposez votre relevé" in corps


# -- la saisie par la pension ------------------------------------------------


def _pension_affichee(contexte, corps: str) -> float:
    """Le montant que la page écrit sur la barre du système actuel.

    Lu sur le HTML et non recalculé : c'est ce que le lecteur voit qui doit
    valoir ce qu'il a tapé, et un contrôle qui relancerait le modèle ne dirait
    rien de la chaîne d'affichage — mensualisation, net, euros constants — que
    l'inversion doit traverser À L'ENVERS pour poser sa cible.

    À l'euro depuis le 23 septembre 2026, comme toute la vue des résultats :
    une pension saisie en euros ronds s'y relit donc à l'identique.
    """
    depart = corps.find("1. Système de répartition actuel")
    assert depart >= 0, "la barre du système actuel a disparu de la page"
    montant = re.search(
        r'<span class="chiffre principal">.*?'
        r'<span class="somme">([\d\u202f]+)</span>',
        corps[depart:], re.S,
    )
    assert montant, f"aucun montant lisible : {corps[depart:depart + 300]}"
    return float(montant.group(1).replace("\u202f", ""))


@pytest.mark.parametrize("pension,mode", [
    (1500, "net"), (2400, "net"), (1000, "net"), (2000, "brut"),
])
def test_la_pension_saisie_est_celle_que_le_systeme_actuel_sert(
    contexte, pension, mode,
):
    """L'aller-retour, qui est tout l'objet de la fonctionnalité.

    On saisit une pension ; la page doit afficher CETTE pension sur la barre du
    système actuel, au centime près. Si elle affichait autre chose, le revenu
    déduit ne serait le revenu de personne, et les trois autres systèmes
    seraient calculés sur une carrière qui n'est pas celle du lecteur.
    """
    _, corps = rendre(contexte, "/simuler", {
        "saisie_par": "pension", "pension": str(pension), "montants": mode,
        "naissance": "1955-06-01", "debut": "1975-01", "liquidation": "2017-06",
    })
    assert "Saisie refusée" not in corps
    assert abs(_pension_affichee(contexte, corps) - pension) < 0.5


def test_le_revenu_deduit_est_annonce_avant_les_quatre_montants(contexte):
    """La réponse à la question posée passe devant la réponse aux autres."""
    _, corps = rendre(contexte, "/simuler", {
        "saisie_par": "pension", "pension": "1500",
        "naissance": "1955-06-01", "debut": "1975-01", "liquidation": "2017-06",
    })
    assert "Le revenu que votre pension suppose" in corps
    assert corps.index("Le revenu que votre pension suppose") < corps.index(
        "Système de répartition actuel"
    )


def test_le_lien_de_reprise_decrit_la_meme_carriere(contexte):
    """Reprendre en saisissant le revenu doit rendre la même pension.

    C'est le seul endroit où la bascule de saisie traduit : elle ne le peut pas
    d'elle-même, faute de connaître le résultat d'un calcul qui n'a pas encore
    eu lieu, et c'est la page de résultats qui porte le nombre trouvé. Si ce
    lien perdait le revenu, le lecteur qui veut corriger sa carrière repartirait
    de la valeur par défaut sans que rien ne le dise.
    """
    _, corps = rendre(contexte, "/simuler", {
        "saisie_par": "pension", "pension": "1500",
        "naissance": "1955-06-01", "debut": "1975-01", "liquidation": "2017-06",
    })
    # DANS LE BLOC DU REVENU DÉDUIT, et nulle part ailleurs : la bascule du
    # formulaire porte elle aussi « saisie_par=revenu », mais sans le nombre
    # trouvé — elle ne peut pas le connaître. Chercher le premier lien venu
    # aurait mesuré la bascule en croyant mesurer la reprise.
    bloc = re.search(r'<div class="carte revenu-deduit">(.*?)</div>', corps, re.S)
    assert bloc, "le bloc du revenu déduit a disparu de la page"
    lien = re.search(r'href="#/simuler\?([^"]*saisie_par=revenu[^"]*)"',
                     bloc.group(1))
    assert lien, "la page ne propose pas de reprendre la carrière en revenu"
    requete = dict(parse_qsl(html.unescape(lien.group(1))))
    assert requete["saisie_par"] == "revenu"
    _, repris = rendre(contexte, "/simuler", requete)
    assert "Saisie refusée" not in repris
    # L'arrondi à l'euro du revenu écrit dans le lien déplace la pension de
    # quelques euros : c'est la même carrière, pas le même centime.
    assert abs(_pension_affichee(contexte, repris) - 1500) < 15


@pytest.mark.parametrize("pension,phrase", [
    ("9000", "plafonne à"),
    ("1", "font ce plancher"),
])
def test_une_pension_que_nulle_carriere_ne_sert_est_refusee(
    contexte, pension, phrase,
):
    """Les refus disent une règle du droit, jamais une limite du calcul.

    Au-dessus du plafond de tranche, cotiser n'acquiert plus rien ; au-dessous
    du minimum contributif, le droit sert un montant qu'aucun revenu ne fait
    descendre. Rendre malgré tout un revenu approché aurait été le pire des
    trois choix : un chiffre faux, vraisemblable, et que rien ne signale.
    """
    _, corps = rendre(contexte, "/simuler", {
        "saisie_par": "pension", "pension": pension,
        "naissance": "1955-06-01", "debut": "1975-01", "liquidation": "2017-06",
    })
    assert "Saisie refusée" in corps
    assert phrase in corps


def test_la_situation_est_la_premiere_question_et_commande_la_saisie(contexte):
    """« En activité ou à la retraite » vient avant tout, et décide du reste.

    C'est la question qui a remplacé « je saisis : mon revenu / ma pension » —
    une question de modélisation posée à quelqu'un qui n'est pas venu
    modéliser. Elle doit donc arriver AVANT le premier champ, et emporter avec
    elle ce que le formulaire demande : un actif ne connaît pas sa pension, un
    retraité ne se souvient pas de son salaire.
    """
    _, actif = rendre(contexte, "/simuler", {})
    assert "Vous êtes" in actif
    assert actif.index("Vous êtes") < actif.index('id="naissance"'), (
        "la situation ne vient plus avant le premier champ"
    )
    assert 'id="salaire"' in actif and 'id="pension"' not in actif

    _, retraite = rendre(contexte, "/simuler", {"situation": "retraite"})
    assert 'id="pension"' in retraite and 'id="salaire"' not in retraite

    # Le lien de la bascule porte les DEUX réglages : cliquer reconfigure le
    # formulaire d'un coup, sans passer par un second contrôle.
    lien = re.search(r'aria-label="Vous êtes".*?href="#/simuler\?([^"]*)"',
                     actif, re.S)
    assert lien, "la bascule de situation ne mène nulle part"
    requete = dict(parse_qsl(html.unescape(lien.group(1))))
    assert requete["situation"] == "retraite"
    assert requete["saisie_par"] == "pension"


def test_une_adresse_qui_ne_dit_que_la_situation_ouvre_la_bonne_saisie(contexte):
    """Le défaut suit la situation ; l'explicite l'emporte.

    Une adresse partagée à la main — « ?situation=retraite » — doit ouvrir le
    formulaire sur la pension, sans qu'on ait à écrire le second réglage. Mais
    un retraité qui a choisi de saisir ce qu'il gagnait garde son choix, parce
    que son adresse le dit.
    """
    assert Saisie.depuis_requete({"situation": "retraite"}).saisie_par == "pension"
    assert Saisie.depuis_requete({"situation": "actif"}).saisie_par == "revenu"
    assert Saisie.depuis_requete(
        {"situation": "retraite", "saisie_par": "revenu"}).saisie_par == "revenu"


def test_le_desaccord_de_situation_est_dit_et_non_corrige(contexte):
    """La situation et la date peuvent se contredire, et c'est sans danger.

    Le modèle ne lit QUE la date : aucun chiffre ne dépend de la situation
    déclarée. Corriger la date effacerait une carrière saisie, refuser la
    saisie arrêterait quelqu'un sur un réglage qui ne change aucun résultat —
    le formulaire le dit, et laisse la date décider.
    """
    # L'exemple par défaut est celui d'un actif : se déclarer retraité le
    # contredit, et c'est le premier clic de qui vient pour sa pension.
    _, incoherent = rendre(contexte, "/simuler", {"situation": "retraite"})
    assert "Vous vous dites à la retraite" in incoherent
    assert "Saisie refusée" not in incoherent

    # Et dans l'autre sens.
    _, inverse = rendre(contexte, "/simuler", {
        "situation": "actif", "naissance": "1955-06-01", "debut": "1975-01",
        "liquidation": "2017-06"})
    assert "Vous vous dites en activité" in inverse

    # Une situation cohérente ne dit rien du tout.
    _, coherent = rendre(contexte, "/simuler", {
        "situation": "retraite", "naissance": "1955-06-01",
        "debut": "1975-01", "liquidation": "2017-06"})
    assert "Vous vous dites" not in coherent


def test_un_retraite_peut_encore_saisir_ce_qu_il_gagnait(contexte):
    """L'échappatoire est offerte là où elle sert, et dans ce sens-là seul.

    Un retraité qui a gardé ses fiches de paie doit pouvoir donner son revenu ;
    une bascule permanente aurait remis à tout le monde la question qu'on vient
    de retirer, une ligne sous le champ suffit. Le chemin inverse — un actif
    qui vise une pension — n'est pas offert sur le formulaire de tout le monde :
    il passe par la situation, et la page dit alors que c'est la date qui
    compte.
    """
    _, retraite = rendre(contexte, "/simuler", {"situation": "retraite"})
    # PAR SON TEXTE, et non par le premier lien venu : la bascule de situation
    # porte elle aussi « saisie_par=revenu », mais elle change de situation en
    # même temps. Chercher au plus court aurait mesuré la bascule.
    lien = re.search(
        r'href="#/simuler\?([^"]*)">Ou saisir ce que vous gagniez\.</a>',
        retraite)
    assert lien, "un retraité ne peut plus saisir ce qu'il gagnait"
    requete = dict(parse_qsl(html.unescape(lien.group(1))))
    assert requete["situation"] == "retraite" and requete["saisie_par"] == "revenu"
    _, repris = rendre(contexte, "/simuler", requete)
    assert 'id="salaire"' in repris and 'id="pension"' not in repris

    # En activité, aucune ligne de ce genre : le formulaire reste nu.
    _, actif = rendre(contexte, "/simuler", {})
    assert "Ou saisir" not in actif


def test_la_bascule_net_brut_traduit_la_pension_saisie(contexte):
    """Changer d'affichage ne doit pas changer la carrière qu'on a décrite.

    Le nombre du formulaire est un NET en mode net. Le recopier tel quel dans
    l'autre mode le ferait relire comme un brut — une pension plus petite d'un
    dixième —, et la page reviendrait en décrivant une autre carrière que celle
    qu'on venait de calculer, sans un mot. C'est le bogue que la bascule évite
    depuis toujours pour les salaires ; la pension l'avait rouvert.
    """
    base = {"saisie_par": "pension", "pension": "1800",
            "naissance": "1975-01-01", "debut": "1996-01",
            "liquidation": "2039-01"}
    _, corps = rendre(contexte, "/simuler", base)
    bloc = re.search(r'<div class="bascule"[^>]*aria-label="Montants".*?</div>',
                     corps, re.S)
    assert bloc, "la bascule des montants a disparu"
    lien = re.search(r'href="#/simuler\?([^"]*)"', bloc.group(0))
    assert lien, "la bascule ne mène nulle part"
    vers_brut = dict(parse_qsl(html.unescape(lien.group(1))))
    assert vers_brut["montants"] == "brut"
    # 1 800 € nets valent environ 1 980 € bruts : une pension ne supporte que
    # la CSG, la CRDS et la CASA, soit 9,1 %.
    assert 1960 <= float(vers_brut["pension"]) <= 2000, (
        f"la pension n'a pas été traduite : {vers_brut['pension']}"
    )
    # Et la carrière est la même des deux côtés : le revenu déduit en brut est
    # celui du net, converti par la fiche de paie du statut.
    _, en_brut = rendre(contexte, "/simuler", vers_brut)
    assert abs(_pension_affichee(contexte, en_brut)
               - float(vers_brut["pension"])) < 1.5


def test_les_deux_revenus_de_la_page_ne_se_contredisent_pas(contexte):
    """La page en affiche deux, et elle doit dire pourquoi ils diffèrent.

    Le bloc du haut donne le revenu du MILIEU de carrière — celui que le
    formulaire demande —, les barres donnent ce que la carrière paie l'année de
    référence des fiches de paie. Le profil de carrière fait monter le revenu
    avec l'âge : les deux nombres diffèrent, et les lire à quelques centimètres
    l'un de l'autre sans explication faisait douter des deux.
    """
    commun = {"saisie_par": "pension", "pension": "1800",
              "naissance": "1975-01-01", "debut": "1996-01",
              "liquidation": "2039-01"}
    _, ascendant = rendre(contexte, "/simuler", commun)
    assert "Les barres en portent un second" in ascendant
    deduit = re.search(r'<p class="cle-chiffre">([\d\u202f]+)', ascendant)
    paie = re.search(r'<span class="chiffre salaire">.*?'
                     r'<span class="somme">([\d\u202f]+)', ascendant, re.S)
    assert deduit and paie, "un des deux revenus a disparu de la page"
    assert deduit.group(1) != paie.group(1), (
        "les deux revenus coïncident : la phrase qui les distingue n'a plus "
        "lieu d'être, et ce test ne mesure plus rien"
    )

    # Sous un profil PLAT, le revenu ne bouge pas avec l'âge : les deux
    # tombent sur le même euro, et la phrase se tait plutôt que d'expliquer
    # une différence qui n'existe pas.
    _, plat = rendre(contexte, "/simuler", {**commun, "profil": "plat"})
    assert "Les barres en portent un second" not in plat


def test_le_formulaire_de_pension_retire_les_revenus(contexte):
    """Les deux nombres ne peuvent pas compter à la fois.

    Laisser les champs de revenu à côté du champ de pension ferait croire que
    la carrière porte les deux, alors que l'un est saisi et l'autre cherché.
    """
    _, revenu = rendre(contexte, "/simuler", {"saisie_par": "revenu"})
    _, pension = rendre(contexte, "/simuler", {
        "saisie_par": "pension", "pension": "1500"})
    assert 'id="salaire"' in revenu and 'id="pension"' not in revenu
    assert 'id="pension"' in pension and 'id="salaire"' not in pension
    # L'unité de saisie ne gouverne plus aucun nombre : elle s'efface avec eux.
    assert "× salaire moyen" in revenu and "× salaire moyen" not in pension


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
    texte = page("/simuler", naissance=1958, liquidation=65, salaire=1300,
                 unite_revenu="euros_mois")
    assert "Le système 4 : un taux pour tous" in texte
    assert "Garantie vieillesse" in texte
    assert "rente du pilier capitalisé" in texte
    assert "l'impôt en finance" in texte
    assert "personne seule, 300\u00a0€" in texte
    texte = page("/simuler", naissance=1958, liquidation=62, salaire=1300,
                 unite_revenu="euros_mois")
    assert "avant les 65 ans" in texte


def test_la_page_ecrit_les_cinq_points_volontaires_partout_ou_ils_pesent(page):
    """Les cinq points rendus se lisent sur la pension ET sur la fiche de paie.

    La règle de ce bloc : nulle part le site n'additionne en silence une
    épargne facultative à une cotisation obligatoire. Le total du système 4
    est annoncé comme un PLAFOND — « retraite jusqu'à » —, la ligne sous lui
    écrit le plancher qu'on touche sans rien ajouter et ce que les cinq points
    rendus ajoutent si on les place ; et sur la fiche de paie, le net affiché
    est le net PLEIN — la fiche ne retient pas ce que personne n'impose —,
    puis le placement et ce qui reste à qui le fait.
    """
    texte = page("/simuler", naissance=1995, liquidation=64, salaire=3000,
                 unite_revenu="euros_mois")
    plat = " ".join(texte.split())
    # Le grand nombre du système 4 dit qu'il est un plafond, et lui seul : les
    # trois premiers systèmes ne dépendent d'aucune décision de l'assuré.
    assert "retraite jusqu'à" in texte
    assert texte.count("retraite jusqu'à") == 1
    # Sous la barre, le plancher puis ce qui s'y ajoute, et à quelle condition.
    assert "de rente capitalisée obligatoire" in texte
    assert "par mois sans rien ajouter" in plat
    assert "de plus si vous placez les cinq points rendus, sans risque" in plat
    # Le dépliant du pilier dit ce que chacune des deux sert.
    assert "que vous versez librement" in texte
    # Le chiffre de tête est le net plein, et la phrase le dit.
    assert "C'est votre salaire net plein" in plat
    assert "pas une retenue" in plat
    # La fiche de paie porte le placement SOUS le net, et ce qui reste après.
    assert "Placé volontairement sur un compte à votre nom" in texte
    assert "restant si vous les placez" in texte
    assert "ne sont sur la fiche de paie de personne" in plat


def test_la_proposition_se_compare_a_taux_egal_cotise(contexte):
    """Les 18 + 5 + 5 valent les 28 % d'aujourd'hui, et les pages le disent.

    C'est la raison d'être des cinq points volontaires : sans eux, le site
    opposerait deux systèmes qui ne coûtent pas le même prix.
    """
    from retraite_notionnelle.web.pages import TAUX_ACTUEL_TOTAL

    base = contexte.base
    assert base.taux_retraite_propose == pytest.approx(
        round(TAUX_ACTUEL_TOTAL, 2))
    programme = _prose(rendre(contexte, "/", {})[1])
    assert "que personne ne vous impose" in programme
    # La ligne du total est une ligne de TABLEAU, que `_prose` retire : on la
    # cherche donc dans le corps rendu, et la phrase qui la commente en prose.
    cout = rendre(contexte, "/cout", {})[1]
    assert "Total versé si les points rendus sont replacés" in cout
    assert "le simulateur, lui, montre la seconde ligne du total" in (
        _prose(cout).lower())
    methode = _prose(rendre(contexte, "/methode", {})[1])
    assert "convention de comparaison" in methode


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


@pytest.mark.parametrize("chemin", ["/", "/simuler", "/cas-types", "/methode"])
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


def test_le_paquet_est_a_jour(contexte):
    """Le paquet et la feuille de style servis au site doivent refléter le dépôt.

    S'il échoue : ``python scripts/construire_donnees.py``.

    Le contexte du module est passé au constructeur, et ce n'est pas une
    élégance : depuis que le paquet embarque le bilan figé, le construire
    suppose le coût agrégé, soit dix-huit secondes. Les autres tests de ce
    module l'ont déjà calculé sous les mêmes réglages, et la mémoire du
    contexte est partagée.
    """
    construction = _construction()
    for chemin, contenu in construction.sorties(contexte).items():
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
    """Lance ``node --test`` : le site doit calculer comme la référence Python.

    TOUS les fichiers d'essai du dossier y passent, et la liste se lit sur le
    disque : elle était écrite en dur, et le jour où le lecteur de PDF a reçu
    les siens ils ne tournaient nulle part. Un fichier ajouté au dossier est
    lancé ici sans que personne ait à y penser.
    """
    import shutil
    import subprocess
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")

    racine = Path(__file__).resolve().parents[1]
    fichiers = sorted(
        str(chemin.relative_to(racine))
        for chemin in (racine / "tests" / "js").glob("*.test.js")
    )
    assert fichiers, "aucun fichier d'essai JavaScript trouvé"
    execution = subprocess.run(
        ["node", "--test", *fichiers],
        cwd=racine, capture_output=True, text=True, encoding="utf-8", check=False,
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
            "population": alea.choice([code for code, _ in POPULATIONS]),
            "rattachement": alea.choice([code for code, _ in RATTACHEMENTS]),
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
            cwd=racine, capture_output=True, text=True, encoding="utf-8", check=False,
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
    # La carte est à l'euro, la fiche de paie au centime : ils ne diffèrent
    # que de l'arrondi.
    for rang, attendu in enumerate([tableau[0]] * 3 + [tableau[1]]):
        assert abs(cartes[rang] - attendu) <= 0.5, (
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
        # Génération 1969 : âge légal de 64 ans, donc quatre trimestres dans
        # l'année qui le précède. La fenêtre reste ouverte aux générations 1965
        # à 1968, dont la suspension de 2026 laisse l'âge légal entre 63 ans et
        # 63 ans et 9 mois.
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
    """Et le sélecteur doit trouver quelque chose, pas seulement exister.

    L'étiquette compte autant que le montant : le système 4 annonce
    « retraite jusqu'à », et `resume()` dans ``index.html`` reprend ce qui
    suit le mot « retraite » pour que l'annonce vocale dise le plafond comme
    un plafond. Un scénario dont l'étiquette ne commencerait plus par
    « retraite » ferait dire à l'oreille autre chose qu'à l'œil.
    """
    corps = rendre(contexte, "/simuler", {"naissance": "1975"})[1]
    blocs = re.findall(r'<div class="scenario">(.*?)<div class="barre', corps, re.S)
    assert len(blocs) == 4
    etiquettes = []
    for bloc in blocs:
        assert re.search(r'class="titre">[^<]+<', bloc), "système sans titre"
        trouve = re.search(r'class="chiffre principal">\s*<span class="categorie">'
                           r'(retraite[^<]*)</span>\s*<span class="somme">[^<]+<',
                           bloc)
        assert trouve, "scénario sans montant mis en avant"
        etiquettes.append(trouve.group(1))
    # Un seul plafond, et c'est celui de la proposition : les trois autres
    # systèmes ne dépendent d'aucune décision de l'assuré.
    assert etiquettes[:3] == ["retraite"] * 3
    assert etiquettes[3] == "retraite jusqu'à"


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
            cwd=racine, capture_output=True, text=True, encoding="utf-8", check=False,
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

    # LA SAISIE PAR LA PENSION A SA PROPRE SÉRIE, et elle est plus courte parce
    # qu'elle coûte vingt fois plus cher : chacune de ces pages inverse le
    # scénario 1 par une dichotomie de dix-huit coupes. C'est la seule boucle
    # du site dont le résultat dépend de l'ordre des opérations flottantes —
    # une différence d'un ulp sur une comparaison et les deux moteurs prennent
    # des branches différentes —, et c'est donc celle qu'il faut le plus
    # sûrement comparer sur des carrières auxquelles personne n'a pensé. Les
    # montants tirés balaient les trois refus autant que les inversions qui
    # aboutissent.
    for numero in range(12):
        debut = alea.randint(14, 30)
        requete = {
            "naissance": str(alea.randint(1930, 2000)),
            "naissance_mois": str(alea.randint(1, 12)),
            "sexe": alea.choice(["H", "F"]),
            "statut": alea.choice(statuts),
            "debut": str(debut),
            "liquidation": str(alea.randint(max(41, debut + 1), 75)),
            "montants": alea.choice(["net", "brut"]),
            "saisie_par": "pension",
            "pension": alea.choice(
                ["1", "500", "1200", "1500", "2400", "9000",
                 f"{alea.uniform(200, 5000):.2f}"]
            ),
        }
        cas.append({
            "nom": f"pension_{numero}",
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
            cwd=racine, capture_output=True, text=True, encoding="utf-8", check=False,
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
            cwd=racine, capture_output=True, text=True, encoding="utf-8", check=False,
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

    DEUX MODULES N'EN SONT PAS, et c'est délibéré : le lecteur de PDF et la
    lecture du relevé ne servent qu'à celui qui dépose un relevé de carrière
    sur le simulateur. Les précharger ferait payer à tous les autres — la
    grande majorité — quarante kilo-octets qu'ils n'ouvriront jamais, et sur le
    chemin critique du premier calcul. Ils sont donc importés à la demande,
    dans le gestionnaire du dépôt, et le test l'exige dans les deux sens : ce
    qui est chargé à la demande n'est jamais préchargé, et ce qui ne l'est pas
    doit l'être.
    """
    import re
    from pathlib import Path

    racine = Path(__file__).resolve().parents[1]
    page = (racine / "index.html").read_text(encoding="utf-8")

    precharges = set(re.findall(
        r'<link rel="modulepreload" href="moteur/js/([\w.-]+\.js)">', page))
    a_la_demande = set(re.findall(
        r'import\(\s*"\./moteur/js/([\w.-]+\.js)"\s*\)', page))
    presents = {chemin.name for chemin in (racine / "moteur" / "js").iterdir()
                if chemin.suffix == ".js"}

    assert a_la_demande <= presents, (
        f"importés à la demande mais absents du dossier : {a_la_demande - presents}"
    )
    assert not (precharges & a_la_demande), (
        "préchargés ET importés à la demande, donc téléchargés deux fois : "
        f"{sorted(precharges & a_la_demande)}"
    )
    assert precharges == presents - a_la_demande, (
        f"préchargés mais absents du dossier : {precharges - presents} ; "
        f"présents mais non préchargés : {presents - a_la_demande - precharges}"
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
        "pages.js", "restitution.js",
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
    # Un bouton caché ne se lit pas davantage : « Effacer ma saisie » ne paraît
    # que lorsque le navigateur a retenu une saisie, et c'est alors un contrôle.
    texte = re.sub(r"<button\b[^>]*\bhidden>.*?</button>", " ", texte, flags=re.S)
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
    # LA BARRE A BOUGÉ DEUX FOIS LE MÊME JOUR, le 22 septembre 2026, et elle
    # redescend. Elle était montée de trois mots pour une bascule « Je saisis :
    # mon revenu / ma pension » — un CONTRÔLE, que ce compte ne sait pas
    # distinguer d'une phrase. Cette bascule a été remplacée le jour même par
    # la question qui la rendait inutile — « Vous êtes : en activité / à la
    # retraite » —, qui coûte autant mais répond à sa place, et la date de
    # départ n'a plus à dire « effectif, ou souhaité » quand on vient de
    # l'apprendre. La barre descend donc SOUS ce qu'elle valait avant les deux
    # changements. C'est le seul sens dans lequel on la déplace sans se
    # justifier ; la monter demande, chaque fois, qu'un contrôle l'exige.
    vierge = rendre(contexte, "/simuler", {})[1]
    assert _mots_visibles(vierge) <= 162, "le formulaire reprend de la prose"

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
    # La population de la table est un réglage de MODÉLISATION, pas
    # d'identité : sans effet par défaut, et le même pour les deux sexes.
    assert (resultat(sexe="H", population="fonctionnaires_civils_etat")
            == resultat(sexe="F", population="fonctionnaires_civils_etat"))
    assert resultat(population="fonctionnaires_civils_etat") != resultat()
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
    _, corps = rendre(contexte, "/methode", {})
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
    assert "function reprendre(" in page and "reprendre(contenu, {" in page

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


def test_la_cascade_suit_la_liste_des_systemes():
    """Aucun système ne peut entrer dans le site sans entrer dans la cascade.

    ``SCENARIOS_MONTRES`` est le seul endroit où les systèmes sont listés, et
    la cascade en déduit ses marches. Reste ce qu'une main doit écrire : le NOM
    de chaque marche. Ce test tient les deux listes face à face, de sorte
    qu'ajouter un système au site fasse tomber le test plutôt que sortir une
    figure à qui il manque une marche — laquelle sommerait encore juste, ce qui
    est le pire des cas : fausse et d'apparence intacte.
    """
    assert SCENARIOS_MONTRES[0] == "actuel", "l'étalon ouvre la chaîne"
    assert set(MARCHES_SYSTEMES) == set(SCENARIOS_MONTRES[1:]), (
        "MARCHES_SYSTEMES et SCENARIOS_MONTRES ont divergé : "
        f"{set(MARCHES_SYSTEMES) ^ set(SCENARIOS_MONTRES[1:])}"
    )
    # Et l'ordre des marches est celui de la liste, non celui du dictionnaire.
    libelles = _libelles_cascade(Contexte(), 0.1, 0.4)
    rapports = {code: 1.0 for code in SCENARIOS_MONTRES}
    rapports[COMPOSANTE_GARANTIE] = 0.0
    marches = _marches_cascade(1000.0, 0.1, rapports, libelles)
    attendus = ["Réversion supprimée"] + [
        MARCHES_SYSTEMES[code][0].format(**libelles)
        for code in SCENARIOS_MONTRES[1:]
    ] + ["Garantie vieillesse"]
    assert [marche.libelle for marche in marches] == attendus


def test_aucune_etiquette_de_cascade_n_ecrit_un_nombre_en_dur(contexte):
    """Un chiffre d'étiquette se recalcule, ou il ment au premier réglage.

    Le taux de la proposition est un réglage que l'adresse porte, et la part de
    réversion dans la masse versée tombe d'un dixième aujourd'hui à un
    dix-huitième en 2070. Les gabarits d'étiquette ne portent donc aucun
    chiffre : ils portent des accolades, que ``_libelles_cascade`` remplit.
    """
    chiffre = re.compile(r"\d")
    for code, (libelle, glose) in {**MARCHES_SYSTEMES, **MARCHES_HORS_SYSTEMES}.items():
        assert not chiffre.search(libelle), f"{code} : chiffre en dur dans « {libelle} »"
        assert not chiffre.search(glose), f"{code} : chiffre en dur dans sa glose"
    # Et le rendu, lui, en porte : les accolades ont bien été remplies.
    corps = rendre(contexte, "/cout", {})[1]
    taux = g.pourcentage(contexte.base.taux_cotisation_liberal, decimales=0)
    assert f"Cotisation unique de {taux}" in corps


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
    for generation, attendu in ((1920, 5.0), (1945, 0.0), (1958, -0.5)):
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
        [sys.executable, "-X", "utf8", "-m", "pytest", "--collect-only", "-q",
         "-p", "no:cacheprovider", str(racine / "tests")],
        capture_output=True, text=True, encoding="utf-8", cwd=racine,
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
        # Sans ses espaces de fin : `construire_tableaux_md.py` écrit le bloc
        # ligne par ligne `rstrip()`-ée, et la ligne du pilier, qui n'a pas de
        # colonne d'écart, n'était plus retrouvée pour ses seuls blancs.
        ligne = ligne.rstrip()
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


@pytest.mark.parametrize("chemin", list(TITRES))
def test_aucune_page_ne_montre_de_balise_echappee(contexte, chemin):
    """Une balise échappée s'affiche en toutes lettres au lecteur.

    La légende d'un tableau est échappée par ``g.tableau``, et c'est voulu :
    elle n'est qu'une phrase. Deux légendes de la page Pourquoi changer y
    avaient pourtant reçu un mot du glossaire, et le visiteur lisait, sous le
    titre « Combien la retraite vous prend-elle chaque mois ? », une ligne de
    ``<span class="mot">`` et de ``role="button"`` — la première chose qu'un
    nouveau venu y voyait, relevée le 23 septembre 2026. Le mot du glossaire
    se pose dans une phrase, jamais dans une légende.
    """
    corps = rendre(contexte, chemin, {})[1]
    echappees = re.findall(r"&lt;/?[a-z][a-z0-9]*\b", corps)
    assert not echappees, f"{chemin} : balises affichées en clair, {echappees[:3]}"


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
        cwd=racine, capture_output=True, text=True, encoding="utf-8", check=True,
    )
    assert json.loads(lecture.stdout) == dict(g.ICONES)


# -- le pont vers le site parent ---------------------------------------------
#
# La page est servie sous partiliberalfrancais.fr/retraite/, et parfois dans un
# cadre de la page d'accueil de ce site. Elle n'en charge rien ; elle n'y
# renvoie que par un lien, et ce lien doit ressortir de tout cadre.


def test_le_pont_vers_le_site_parent_ressort_de_tout_cadre():
    """Un seul pont, en pied de page, et rien du site parent dans l'en-tête.

    ``target="_top"`` : ouvert dans le cadre que la page d'accueil du site
    ouvre sur le simulateur, un lien ordinaire chargerait le site DANS le
    cadre. Hors cadre, l'attribut ne change rien. L'en-tête, lui, ne porte
    aucune adresse extérieure : il a porté le pont, en petites capitales
    au-dessus du nom du site, et c'était une rangée de plus sur chacune des
    neuf pages pour dire d'où l'on vient ; la navigation du site n'y est pas
    recopiée non plus, elle se périmerait à sa prochaine mise en page.
    """
    import re

    pont = (f'href="{g.SITE_PARENT}" target="_top"')
    entete = g.entete("/")
    assert pont in g.pied()
    assert pont not in entete
    exterieures = set(re.findall(r'href="(https?://[^"]+)"', entete))
    assert exterieures == set(), exterieures
    # Dans le cadre, le site pose ``plf-embedded`` sur ``<body>`` ; sa propre
    # navigation est alors juste au-dessus, et le pont ferait doublon.
    assert "body.plf-embedded footer .retour-site" in g.FEUILLE_DE_STYLE


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
        cwd=racine, capture_output=True, text=True, encoding="utf-8", check=True,
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


#: Ce que chaque page peut imposer à qui l'ouvre : mots de PROSE, tracés
#: ouverts, tableaux ouverts, et mots DANS LES TABLEAUX. Les bornes sont celles
#: de la refonte, arrondies vers le haut : elles n'interdisent pas d'écrire,
#: elles interdisent de revenir à une page qu'on ne lit pas.
#:
#: LA PROSE ET LES TABLEAUX ONT ÉTÉ SÉPARÉS le 21 septembre 2026, et c'est ce
#: qui a permis de RENDRE à la page Avantages le plafond qu'on lui avait
#: desserré la veille. Un tableau se parcourt du regard, une phrase se lit :
#: les compter ensemble faisait qu'ajouter un dispositif à l'inventaire —
#: c'est-à-dire faire le travail que cette page existe pour montrer — coûtait
#: du budget de PROSE, et poussait à relever le plafond à chaque découverte.
#: Deux découvertes en deux jours l'avaient déjà fait une fois.
#:
#: Le quatrième nombre est donc le budget des tableaux. Il vaut ``None`` pour
#: la page Avantages, dont les tableaux SONT l'inventaire : il se calcule alors
#: à ``MOTS_PAR_DISPOSITIF`` par ligne, et grandit tout seul avec elle. C'est la
#: seule page où une donnée commande un budget, et c'est la seule dont le
#: contenu soit une liste que le dépôt allonge.
#:
#: Une page échappe à la règle des mots : « /simuler » EST un formulaire : ce
#: qu'on y compte est fait de libellés de champs et de deux cents options de
#: menus, que personne ne lit à la suite.
BUDGETS_DE_LECTURE: dict[str, tuple[int, int, int]] = {
    # Deux tableaux sur l'accueil : celui qui oppose les deux systèmes terme à
    # terme, et celui du plancher — l'argument le plus parlant du site, remonté
    # en haut de page par la revue de septembre 2026. Plus l'entrée, deux
    # lignes et un bouton qui disent que le site est un simulateur.
    "/": (470, 0, 2, 240),
    "/simuler": (1500, 0, 0, 0),
    # Partager ne porte que des cartes : leur texte est court par
    # construction — il doit tenir dans une image de 1200 × 675.
    "/partager": (400, 0, 0, 0),
    # Cas types et Données ont gagné, à la revue de septembre 2026, ce qu'un
    # lecteur doit lire AVANT les chiffres : la clé de lecture des grilles et
    # la trajectoire du système actuel pour l'une, le résumé en langage
    # courant pour l'autre. Les bornes suivent, d'un paragraphe chacune.
    "/cas-types": (500, 0, 1, 310),
    # Coût tenait à 700 mots, et les atteignait exactement. La carte des flux,
    # le 23 septembre 2026, en ajoute deux cent trente : cent dix de prose — sa
    # question, sa réponse, sa source — et cent vingt d'étiquettes, le nom et
    # le montant de chacun des nœuds de ses deux schémas, que le décompte ne
    # sait pas distinguer d'une phrase. Les tracés ouverts restent deux : un
    # schéma de Sankey n'est pas un graphique dans le temps, et le test de la
    # page le compte à part. Son année se choisit depuis le même jour, comme
    # celle de la cascade : vingt-deux mots de plus — le sélecteur, une phrase
    # de la source qui dit à quel PIB les flux sont comptés, et les
    # successions, qui rendent une part de la garantie et paient avec l'impôt.
    "/cout": (970, 2, 0, 0),
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
    # en déloger un autre. Puis de 1950 à 2000 le 20 septembre 2026, pour la
    # quarante-troisième ligne : les bonifications de services de la SNCF et
    # de la RATP, que les fiches déclaraient et que personne n'avait
    # inventoriées.
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
    #
    # LE PLAFOND DE PROSE EST PLUS SERRÉ QU'AVANT LE DESSERRAGE. Le 21
    # septembre 2026, l'ajout d'une
    # quatrième carte — que cotise-t-on sans rien acquérir ? — avait fait
    # passer le plafond de 2 000 à 2 250 mots, faute de place : la page était
    # exactement à 1 997. Le lendemain, deux dispositifs de plus le faisaient
    # à nouveau sauter, et l'on voyait le défaut : c'étaient les SEPT TABLEAUX
    # de l'inventaire, ouverts à dessein depuis que la page a cessé de
    # promettre quarante dispositifs sans les nommer, qui consommaient la
    # moitié du budget. Les tableaux comptent désormais à part, et la prose
    # est tenue à 1 300 mots — moins que les 2 000 d'avant le desserrage, et
    # bien moins que les 2 250 d'après. Ce que le total autorise a grandi,
    # puisque les lignes ont leur propre plafond ; ce qu'on peut IMPOSER À LIRE
    # a diminué. Et ajouter un dispositif ne coûte plus une phrase à personne.
    #
    # Le budget des tableaux vaut ``None`` : il se calcule sur l'inventaire.
    "/avantages": (1300, 5, 8, None),
    # Méthode et Sources font une page depuis le 23 septembre 2026. Leurs
    # bornes s'additionnaient à 700 mots de prose, pour 631 lus ; la page
    # fusionnée en montre 557 — un seul « En clair », plus de plan —, et sa
    # borne est serrée d'autant.
    "/methode": (600, 0, 1, 120),
    # Risque répond à la question d'un lecteur qui n'a pas fait d'économie
    # en deux cartes, chacune avec le tableau qui la montre : les cas
    # documentés à l'étranger, et le compte projeté du COR. Ce sont ces deux
    # tableaux, et le plan de douze sections, qui portent le budget ; la
    # prose ouverte tient en trois cents mots. Tout le reste est replié.
    # Les tableaux sont passés de 250 à 270 mots le 23 septembre 2026 : le
    # compte du COR y dit chaque part du PIB aussi en milliards, dix cases de
    # quatre mots de plus, et rien d'autre n'y est entré.
    "/risque": (650, 0, 2, 270),
}


#: Ce qu'une ligne de l'inventaire coûte, en mots, aux tableaux de la page
#: Avantages : le libellé du dispositif, son coût, et — quand la case est vide
#: — la phrase qui dit pourquoi. Vingt-six en moyenne sur les quarante-cinq
#: lignes d'aujourd'hui ; trente laisse de quoi écrire une raison un peu
#: longue sans que le test se plaigne de ce qu'il devrait encourager.
MOTS_PAR_DISPOSITIF = 30


def _mots(html: str) -> int:
    return len(re.sub(r"<[^>]+>", " ", html).split())


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
    mots_max, traces_max, tableaux_max, mots_tableaux_max = \
        BUDGETS_DE_LECTURE[chemin]
    visible = _hors_depliants(rendre(contexte, chemin, {})[1])

    # LA PROSE ET LES TABLEAUX NE SE LISENT PAS DE LA MÊME FAÇON, et les
    # compter ensemble faisait payer à la prose ce qu'un inventaire coûte en
    # lignes. Ils sont donc mesurés à part — voir l'en-tête des budgets.
    sans_tableaux = re.sub(r"<table\b.*?</table>", " ", visible, flags=re.S)
    mots = _mots(sans_tableaux)
    assert mots <= mots_max, (
        f"{chemin} : {mots} mots de prose à traverser avant d'avoir rien "
        f"déplié, {mots_max} au plus"
    )

    if mots_tableaux_max is None:
        # La page Avantages MONTRE l'inventaire : ses tableaux grandissent avec
        # lui, et leur budget aussi. C'est la seule page dont une donnée
        # commande le plafond, et c'est la seule dont le contenu soit une liste
        # que le dépôt a vocation à allonger.
        mots_tableaux_max = MOTS_PAR_DISPOSITIF * len(
            contexte.inventaire_avantages().avantages
        )
    mots_tableaux = _mots(visible) - mots
    assert mots_tableaux <= mots_tableaux_max, (
        f"{chemin} : {mots_tableaux} mots dans les tableaux ouverts, "
        f"{mots_tableaux_max} au plus"
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
                                    "/risque"])
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
    assert "Ce que d'autres caisses versent" in texte
    assert "Assurance vieillesse des parents au foyer" in texte
    assert "Points Agirc-Arrco des chômeurs" in texte
    assert "Deux de ces recettes financent des droits que les scénarios" in texte
    # L'assurance chômage paie ce que le compte porte : sa recette reste.
    assert "L'assurance chômage, elle, paie ce que le compte notionnel porte" in texte
    # Le dépliant dit que le coefficient retire les deux autres, et ce qu'on
    # lirait sans ce retrait, sur deux des systèmes comparés.
    assert "Le coefficient d'équilibre du dépliant suivant retire les deux autres" in texte
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
    # Et les deux schémas de Sankey de la carte des flux : une seule année,
    # deux systèmes, et ce qu'aucune courbe ne montre — qui paie quoi.
    assert visible.count('<figure class="sankey"') == 2
    assert visible.count("<table") == 0, (
        "un tableau déplié sur la page Coût : les chiffres se rangent sous le "
        "graphique qu'ils décrivent, ou dans une section repliée"
    )
    # La même borne que `BUDGETS_DE_LECTURE` : la page en avait deux, 650 ici
    # et 700 là, et la note « Ce que personne n'a cotisé » de l'action 44 a
    # trouvé la page à 650 mots exactement. Une borne, celle du budget.
    mots = len(re.sub(r"<[^>]+>", " ", visible).split())
    assert mots <= BUDGETS_DE_LECTURE["/cout"][0], (
        f"{mots} mots à lire avant d'avoir rien déplié"
    )

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
    assert len(cartes) == 3, f"{len(cartes)} cartes, trois attendues"
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


# -- le schéma de Sankey --------------------------------------------------------


def _caisses_d_essai() -> tuple[g.CaisseSankey, ...]:
    """Deux caisses dont le compte tombe juste : un déficit, puis un passage."""
    n = g.NoeudSankey
    return (
        g.CaisseSankey(
            "Caisse", 100.0, "100",
            (n("A", 60.0, "60", "var(--serie-5)"),
             n("B & <C>", 30.0, "30", "var(--serie-6)"),
             n("Manque", 10.0, "10", "var(--manque)")),
            (n("X", 90.0, "90", "var(--serie-2)"), n("Y", 10.0, "10", "var(--serie-4)")),
        ),
        g.CaisseSankey("Seconde", 20.0, "20", (n("D", 20.0, "20", "var(--serie-7)"),),
                       (n("Z", 20.0, "20", "var(--serie-3)"),)),
    )


def _rubans_sankey(html: str) -> list[tuple[float, float, float, float, float, float]]:
    """Chaque ruban d'un schéma : abscisse, haut et bas à son départ, puis à son arrivée.

    Le tracé est ``M x1 h1 C … x2 h2 L x2 b2 C … x1 b1 Z`` : ses bords se
    lisent aux positions fixes de ses nombres.
    """
    rubans = []
    for trace in re.findall(r'<path class="ruban" fill="[^"]+" d="([^"]+)"/>', html):
        v = [float(x) for x in re.findall(r"-?\d+\.\d", trace)]
        rubans.append((v[0], v[1], v[15], v[6], v[7], v[9]))
    return rubans


def test_un_schema_de_sankey_remplit_exactement_ses_caisses():
    """Le compte tombe juste, et le dessin le montre : les rubans qui entrent
    dans une caisse la couvrent de haut en bas, bord à bord, sans se chevaucher,
    et ceux qui en sortent aussi. Chaque ruban garde son épaisseur d'un bout à
    l'autre, et cette épaisseur est son montant à l'échelle."""
    echelle = 2.0
    html = g.sankey("Essai", "Un essai", _caisses_d_essai(), echelle)
    caisses = [(float(y), float(h)) for y, h in re.findall(
        r'<rect class="noeud caisse" x="[^"]+" y="([^"]+)" width="[^"]+" height="([^"]+)"/>',
        html)]
    assert len(caisses) == 2
    rubans = _rubans_sankey(html)
    assert len(rubans) == 3 + 2 + 1 + 1
    entree = g.X_CAISSE_SANKEY
    sortie = g.X_CAISSE_SANKEY + g.LARGEUR_NOEUD_SANKEY
    for (haut, hauteur), caisse in zip(caisses, _caisses_d_essai()):
        assert hauteur == pytest.approx(caisse.valeur * echelle)
        for bords in (
            # Le bord droit des rubans qui entrent, le bord gauche de ceux qui sortent.
            sorted((h2, b2) for x1, h1, b1, x2, h2, b2 in rubans
                   if x2 == entree and haut <= h2 < haut + hauteur),
            sorted((h1, b1) for x1, h1, b1, x2, h2, b2 in rubans
                   if x1 == sortie and haut <= h1 < haut + hauteur),
        ):
            assert bords[0][0] == pytest.approx(haut)
            for (_, bas), (suivant, _) in zip(bords, bords[1:]):
                assert suivant == pytest.approx(bas, abs=0.11)
            assert bords[-1][1] == pytest.approx(haut + hauteur, abs=0.11)
    epaisseurs = sorted(round(b1 - h1, 1) for _, h1, b1, _, h2, b2 in rubans)
    assert epaisseurs == sorted(round(b2 - h2, 1) for _, h1, b1, _, h2, b2 in rubans)
    attendues = [noeud.valeur * echelle for caisse in _caisses_d_essai()
                 for noeud in caisse.sources + caisse.usages]
    assert epaisseurs == sorted(attendues)


def test_un_schema_de_sankey_ne_superpose_aucune_etiquette():
    """Les nœuds minuscules sont ceux où deux étiquettes se chevaucheraient :
    l'écart entre deux nœuds d'une colonne est fait pour en loger deux, et le
    cadre descend assez bas pour loger la dernière."""
    n = g.NoeudSankey
    minuscules = tuple(n(f"N{rang}", 0.01, "0,0", "var(--serie-5)") for rang in range(4))
    caisse = g.CaisseSankey("Caisse", 0.04, "0,0", minuscules,
                            (n("U", 0.04, "0,0", "var(--serie-2)"),))
    html = g.sankey("Essai", "Un essai", (caisse,), 1.0)
    noms = [float(y) for y in re.findall(
        r'<text class="nom" x="[^"]+" y="([^"]+)" text-anchor="end">', html)]
    assert len(noms) == 4
    for haut, bas in zip(noms, noms[1:]):
        # Deux lignes de treize unités, plus de quoi respirer.
        assert bas - haut >= g.ECART_NOEUDS_SANKEY >= 30
    hauteur = float(re.search(r'viewBox="0 0 \d+ (\d+)"', html).group(1))
    montants = [float(y) for y in re.findall(r'<text class="montant" x="[^"]+" y="([^"]+)"', html)]
    assert max(montants) + 4 <= hauteur


def test_un_schema_de_sankey_se_lit_aussi_en_tableau():
    """Un schéma est une image : chacun de ses rubans est redit dans le tableau
    replié dessous, de qui à qui et combien, et le texte est échappé partout."""
    html = g.sankey("Essai", "Un essai", _caisses_d_essai(), 1.0,
                    ("D'où", "Où"))
    assert html.startswith('<figure class="sankey" role="group" aria-label="Essai">')
    assert "<figcaption>Un essai</figcaption>" in html
    tableau = html[html.index('<details class="donnees-sankey">'):]
    assert "(7 lignes)" in tableau
    lignes = re.findall(
        r'<tr><th class="" scope="row">(.*?)</th><td class="">(.*?)</td>'
        r'<td class="nombre">(.*?)</td></tr>', tableau)
    assert lignes == [
        ("A", "Caisse", "60"), ("B &amp; &lt;C&gt;", "Caisse", "30"),
        ("Manque", "Caisse", "10"), ("Caisse", "X", "90"), ("Caisse", "Y", "10"),
        ("D", "Seconde", "20"), ("Seconde", "Z", "20"),
    ]
    assert "B & <C>" not in html and html.count("B &amp; &lt;C&gt;") == 2
    # Les titres de colonne ne se posent qu'une fois, au-dessus de la première caisse.
    assert html.count('class="colonne"') == 2
    assert g.sankey("Rien", "Rien", (), 1.0) == ""


def test_deux_schemas_comparés_partagent_leur_echelle():
    """Le plus gros prend toute la hauteur prévue ; l'autre, la sienne à la
    même échelle — sans quoi un système deux fois plus petit paraîtrait aussi
    gros."""
    echelle = g.echelle_sankey(400.0, 200.0)
    assert echelle * 400.0 == pytest.approx(g.HAUTEUR_SANKEY)
    assert g.echelle_sankey() == 0.0 and g.echelle_sankey(0.0) == 0.0


def test_la_carte_des_flux_dessine_le_compte_de_la_bascule(contexte):
    """Qui paie quoi, dans les deux systèmes, sur le compte même du tableau
    poste par poste — et à la même échelle.

    Chaque caisse tombe juste : ses payeurs, déficit compris, somment à ce
    qu'elle brasse, et ses usages aussi. Le système actuel encaisse l'impôt ;
    le régime unique de la proposition ne l'encaisse pas, et l'impôt paie à
    part la garantie vieillesse, comme le pilier capitalisé est placé à part.
    Par défaut, l'année est celle de la bascule.
    """
    bilan = _compte_flux(contexte, contexte.base.annee_bascule)
    ligne = bilan.ligne
    caisses = {s: _caisse_flux(ligne, bilan.pib, s, s, "Cotisations")
               for s in ("actuel", "notionnel_liberal")}
    for systeme, caisse in caisses.items():
        # Au dix-millième : les parts que le COR publie, arrondies, ne somment
        # pas tout à fait à un — la tolérance de `test_cout.py`, pour la même
        # raison. Un millième de milliard, que le dessin ne peut pas montrer.
        assert sum(n.valeur for n in caisse.sources) == pytest.approx(
            caisse.valeur, rel=1e-4)
        assert sum(n.valeur for n in caisse.usages) == pytest.approx(caisse.valeur)
        assert caisse.valeur == pytest.approx(
            max(ligne.ressources_de(systeme), ligne.depense(systeme)))
    sources = {s: {n.libelle for n in c.sources} for s, c in caisses.items()}
    assert "Impôts" in sources["actuel"]
    assert "Impôts" not in sources["notionnel_liberal"]
    # La TVA à taux unique entre au régime unique sous son nom (23 septembre
    # 2026), et elle seule des impôts.
    assert "TVA" in sources["notionnel_liberal"]
    assert {n.libelle for n in caisses["actuel"].usages} >= {"Pensions de réversion"}

    corps = rendre(contexte, "/cout", {})[1]
    carte = re.search(r'<section class="cle" id="cout-flux".*?</section>', corps, re.S)
    assert carte, "la carte des flux a disparu de la page Coût"
    schemas = re.findall(r'<figure class="sankey".*?</figure>', carte.group(0), re.S)
    assert len(schemas) == 2
    assert "Budget de l&#x27;État" in schemas[1] and "Pilier capitalisé" in schemas[1]
    assert "Budget de l&#x27;État" not in schemas[0]
    # La même échelle : les deux caisses de répartition sont dans le rapport de
    # ce qu'elles brassent.
    hauteurs = [float(re.search(r'<rect class="noeud caisse"[^>]*height="([^"]+)"',
                                schema).group(1)) for schema in schemas]
    assert hauteurs[0] / hauteurs[1] == pytest.approx(
        caisses["actuel"].valeur / caisses["notionnel_liberal"].valeur, rel=2e-3)
    # Le solde n'est pas caché : un déficit est un payeur, un excédent un
    # usage, et la réponse chiffre l'un ou l'autre. Avec la TVA à taux unique,
    # la bascule est en excédent.
    solde = ligne.solde("notionnel_liberal") * bilan.pib
    verbe = "placerait" if solde >= 0 else "emprunterait"
    # Les blancs de la source sont repliés, mais pas les espaces fines des
    # montants : `\s` les attraperait aussi.
    assert f"{verbe} {_milliards_flux(abs(solde))}" in html.unescape(
        re.sub(r"[ \t\n]+", " ", carte.group(0)))


def _milliards_flux(meur: float) -> str:
    return g.nombre(meur / 1000, 0 if meur >= 10_000 else 1) + "\u202fMd\u202f\u20ac"


def test_les_schemas_offrent_les_annees_de_la_cascade_a_compter_de_la_bascule(contexte):
    """Comme la cascade, mais jamais avant la bascule : la proposition n'y est
    pas encore appliquée, et son schéma serait celui du système actuel sous un
    autre nom. Une année qu'on ne propose pas retombe sur la première, sans
    erreur — une adresse partagée doit afficher les schémas."""
    solde = contexte.cout().solde
    obs, fin = solde.derniere_annee_observee, solde.derniere_annee
    bascule = contexte.base.annee_bascule
    assert bascule > obs, "le témoin suppose une bascule postérieure à l'année mesurée"
    offertes = _annees_flux(solde, bascule)
    assert offertes == tuple(a for a in _annees_cascade(solde, bascule) if a >= bascule)
    assert offertes[0] == bascule and offertes[-1] == fin and obs not in offertes
    # Une bascule déjà passée : l'année mesurée ouvre la liste, comme celle de
    # la cascade ; une bascule à l'horizon : l'horizon seul.
    assert _annees_flux(solde, obs - 5)[0] == obs
    assert _annees_flux(solde, fin) == (fin,)
    for demandee, attendue in (("", bascule), ("2070", 2070), (str(obs), bascule),
                               ("2035", bascule), ("deux mille", bascule),
                               ('"><script>', bascule)):
        assert _annee_flux(solde, bascule, {"flux": demandee}) == attendue, demandee
    assert _annee_flux(solde, bascule, None) == bascule


def test_chaque_annee_des_schemas_tombe_juste(contexte):
    """Pour toutes les années offertes, chaque caisse brasse ce qu'elle reçoit
    et ce qu'elle verse. La garantie de l'année est payée par l'impôt et, de
    plus en plus, par ce que les successions en rendent : les deux somment à
    la garantie, et la part des successions croît avec les années."""
    solde = contexte.cout().solde
    bascule = contexte.base.annee_bascule
    reprises = []
    for annee in _annees_flux(solde, bascule):
        compte = _compte_flux(contexte, annee)
        for systeme in ("actuel", "notionnel_liberal"):
            caisse = _caisse_flux(compte.ligne, compte.pib, systeme, systeme, "C")
            assert sum(n.valeur for n in caisse.sources) == pytest.approx(
                caisse.valeur, rel=1e-4), (annee, systeme)
            assert sum(n.valeur for n in caisse.usages) == pytest.approx(
                caisse.valeur), (annee, systeme)
        assert 0.0 <= compte.reprises < compte.garantie, annee
        assert compte.garantie == pytest.approx(
            compte.ligne.postes_depenses("notionnel_liberal")["garantie_vieillesse"])
        # Les milliards suivent la règle du site entier, et nulle autre.
        assert compte.pib == _pib_de_conversion(contexte.comptes(), annee)
        reprises.append(compte.reprises / compte.garantie)
    assert reprises[-1] > reprises[0], "les successions rendent plus à l'horizon"


def test_l_annee_des_schemas_se_choisit_et_garde_celle_de_la_cascade(contexte):
    """``flux`` pose l'année des schémas ; les deux sélecteurs de la page se
    gardent l'un l'autre ; le tableau poste par poste reste à la bascule."""
    bascule = contexte.base.annee_bascule
    corps = rendre(contexte, "/cout", {"flux": "2070", "cascade": "2040"})[1]
    carte = re.search(r'<section class="cle" id="cout-flux".*?</section>', corps, re.S)
    assert carte
    carte = carte.group(0)
    choix = re.search(r'<div class="bascule" role="group" aria-label="Année des '
                      r'schémas">.*?</div>', carte).group(0)
    assert '<span class="actif" aria-current="true">2070</span>' in choix
    liens = re.findall(r'<a href="([^"]+)">(\d{4})</a>', choix)
    assert liens and all(adresse == f"#/cout?cascade=2040&flux={annee}"
                         for adresse, annee in liens), liens
    cascade = re.search(r'<div class="bascule" role="group" aria-label="Année '
                        r'décomposée">.*?</div>', corps).group(0)
    assert '<span class="actif" aria-current="true">2040</span>' in cascade
    assert all(adresse.endswith("&flux=2070") for adresse, _ in
               re.findall(r'<a href="([^"]+)">(\d{4})</a>', cascade))
    texte = html.unescape(re.sub(r"[ \t\n]+", " ", carte))
    assert "Le système actuel, en 2070" in texte and "Notre proposition, en 2070" in texte
    assert "En 2070, le régime unique" in texte and "part du PIB de 2070" in texte
    # En 2070 les successions rendent une part de la garantie : un payeur de plus.
    assert ">Successions</text>" in carte
    # Le tableau poste par poste, lui, reste à l'année de la bascule.
    assert f"Ressources et dépenses du système de retraite en {bascule}," in corps
    # Une valeur qui n'est pas une année offerte ne voyage pas : elle est
    # ramenée, et c'est l'année ramenée que les liens de la cascade portent.
    corps = rendre(contexte, "/cout", {"flux": '"><script>alert(1)</script>'})[1]
    assert "<script>alert" not in corps
    assert f'<a href="#/cout?cascade=2030&flux={bascule}">2030</a>' in corps


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
    # La composition de l'image, et sa signature. Elle sait composer les deux
    # schémas de Sankey d'une carte, chacun à ses proportions.
    assert '.closest("button.partager")' in page
    assert '"figure.graphique, figure.sankey"' in page
    assert "svg.viewBox.baseVal" in page
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
        cwd=racine, capture_output=True, text=True, encoding="utf-8", check=True,
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
    assert premier.count("<option") == 63
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
                   if chemin == "/simuler" else {})[1]
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
        ("/cout", ["cout-bilan", "cout-provenance", "cout-flux", "cout-depenses",
                   "cout-ressources",
                   "cout-transferts", "cout-scenarios", "cout-cascade",
                   "cout-equilibre", "cout-postes",
                   "cout-dette",
                   "cout-frise", "cout-garantie", "cout-capitalisation", "cout-poids", "cout-sources",
                   "cout-limites"]),
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

    corps = rendre(contexte, "/methode", {})[1]
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
    # Et l'inventaire ne s'impose toujours pas : il reste replié. Depuis que
    # Sources est la fin de la page Méthode, un tableau y est ouvert — celui
    # des règles d'indexation, qui est la réponse de Méthode —, mais pas lui.
    assert '<table id="inventaire">' not in _hors_depliants(corps)

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
    """Le scénario 6 affiche des écarts rouges : la clé dit contre quoi ils se lisent.

    La clé était sur la page Coût ; elle est en tête de Cas types, AVANT les
    trois chiffres d'ouverture et les grilles, et dit de quel côté de un se
    trouve le réglage annuel de la proposition. Elle renvoie à la section de
    Coût qui le chiffre.

    Elle a ouvert sur « ces pourcentages ne sont pas des baisses de pension »
    jusqu'au 23 septembre 2026, jour où l'accueil s'est mis à dire l'ordre de
    grandeur de la baisse, lu sur cette même grille. Elle dit désormais contre
    quoi ils se lisent — la promesse du système actuel —, et ne peut plus
    démentir, un clic plus loin, ce que l'accueil affirme.
    """
    corps = rendre(contexte, "/cas-types", {})[1]
    cle = corps.index("Ces pourcentages se lisent contre une")
    assert cle < corps.index('<div class="fiches reperes">')
    assert cle < corps.index('<div class="panneaux">')
    assert "Pour la proposition, ce facteur est " in corps
    assert 'data-vers="cout-equilibre"' in corps
    assert "Ces pourcentages se lisent contre une" in _hors_depliants(corps)
    assert "ne sont pas des baisses" not in corps


def _reglage_proposition_attendu(contexte):
    """Le coefficient de la proposition, recalculé ici sans passer par la page."""
    solde = contexte.cout().solde
    debut, fin = solde.premiere_annee_projetee, solde.derniere_annee
    coefficients = {annee: solde.annee(annee).coefficient("notionnel_liberal")
                    for annee in range(debut, fin + 1)}
    annee_minimum = min(coefficients, key=coefficients.get)
    return debut, fin, coefficients, annee_minimum


def test_cas_types_dit_du_reglage_ce_que_le_solde_dit(contexte):
    """La phrase de Cas types se calcule ; elle ne s'écrit plus.

    Le 19 septembre 2026 au soir, la page affirmait en texte fixe que le
    coefficient d'équilibre de la proposition « est supérieur à un chaque
    année ». Le 20 au matin, quatre changements du modèle de coût l'avaient
    fait passer sous un sur les quarante-cinq années projetées, et la page
    Coût du même site le chiffrait à 0,92 en 2070 pendant que Cas types
    promettait une marge. Le parcours de présentation demandait de lire la
    phrase à voix haute. Ce test lit le solde, en déduit la phrase attendue,
    et exige que Cas types et Coût la portent toutes les deux.
    """
    debut, fin, coefficients, annee_minimum = _reglage_proposition_attendu(contexte)
    sous_un = sum(1 for c in coefficients.values() if c < 1.0)
    cas_types = rendre(contexte, "/cas-types", {})[1]
    cout = rendre(contexte, "/cout", {})[1]
    minimum = g.nombre(coefficients[annee_minimum], 2)
    dernier = g.nombre(coefficients[fin], 2)

    if sous_un == 0:
        assert (f"supérieur à un sur chacune des années projetées, de {debut} à {fin}"
                in cas_types)
        assert "Un coefficient supérieur à un est une marge" in cas_types
        assert "inférieur à un" not in cas_types
        assert f"Les {dernier} de la proposition en {fin} disent une marge" in cout
    elif sous_un == len(coefficients):
        assert f"inférieur à un de {debut} à {fin}" in cas_types
        assert f"{minimum} au plus bas en {annee_minimum}" in cas_types
        assert f"{dernier} en {fin}" in cas_types
        assert "Un coefficient inférieur à un est un manque" in cas_types
        assert "supérieur à un chaque année" not in cas_types
        assert f"Les {dernier} de la proposition en {fin} disent un manque" in cout
        assert f"son plus bas, {minimum} en {annee_minimum}" in cout
    else:
        # Assez de décimales pour qu'un plus bas sous un ne s'écrive pas 1,00 :
        # c'est le cas depuis la TVA à taux unique, 0,999 en 2044.
        from retraite_notionnelle.web.pages import _decimales_sous_un

        precis = g.nombre(coefficients[annee_minimum],
                          _decimales_sous_un(coefficients[annee_minimum]))
        assert f"inférieur à un {sous_un} années sur {len(coefficients)}" in cas_types
        assert f"{precis} en {annee_minimum}" in cas_types
        assert f"{dernier} en {fin}" in cas_types
        assert f"son plus bas, {precis} en {annee_minimum}" in cout
    # Et dans aucun cas la page ne lit plus un coefficient comme une économie.
    assert "comme\nune économie" not in cout
    assert "Le coefficient se lit dans les deux sens" in cout


def test_le_README_donne_le_solde_que_la_page_cout_calcule(contexte):
    """Le tableau du README (section « Un coût n'est pas un solde ») est celui
    de la page Coût, ligne par ligne.

    Il a été faux plusieurs jours de suite : −1,93 % et 0,89 pour la
    proposition quand le site affichait −1,52 % et 0,92, et 1,87 pour le
    scénario 3 deux paragraphes après un tableau qui disait 1,64. La section
    est devenue une zone `etat` de `zones.yaml`, et ses nombres portent une
    ancre que la sonde `mesure` recalcule ; ce test reste, parce qu'il
    confronte le README à la PAGE et non au modèle — deux chemins qui
    pourraient diverger. Il lit les nombres sous leurs ancres.
    """
    from pathlib import Path

    from retraite_notionnelle.cout import SCENARIOS

    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
    solde = contexte.cout().solde
    comptes = contexte.comptes()
    observe = solde.annee(solde.derniere_annee_observee)
    horizon = solde.annee(solde.derniere_annee)

    # Les deux soldes se lisent en part du PIB ET en milliards, sur la page
    # (« −0,17 % · −5,1 Md € ») comme dans le README (« −0,17 % du PIB,
    # −5,1 Md€ ») : la normalisation efface la seule différence, la typographie.
    def normaliser(texte: str) -> str:
        texte = re.sub(r"<!--.*?-->", "", texte)
        return (texte.replace("**", "").replace("−", "-").replace(" du PIB", "")
                .replace("\u202f", " ").replace("\u00a0", " ")
                .replace(" \u00b7 ", ", ").replace("Md €", "Md€").strip())

    for numero, (scenario, _libelle) in enumerate(SCENARIOS, start=1):
        ligne = re.search(rf"^\| {numero}\. [^|]*\|([^|]*)\|([^|]*)\|([^|]*)\|$",
                          readme, re.M)
        assert ligne, f"le README n'a plus de ligne {numero} dans le tableau des soldes"
        moyen = solde.solde_moyen(scenario, solde.premiere_annee_projetee,
                                  solde.derniere_annee)
        attendu = [
            _part_et_milliards(
                observe.solde(scenario),
                observe.solde(scenario) * _pib_de_conversion(comptes, observe.annee),
                decimales=2, signe=True),
            _part_et_milliards(
                moyen, moyen * _pib_de_conversion(comptes, solde.derniere_annee),
                decimales=2, signe=True),
            g.nombre(horizon.coefficient(scenario), 2),
        ]
        assert [normaliser(c) for c in ligne.groups()] == [normaliser(a) for a in attendu], (
            f"ligne {numero} du README : {ligne.groups()} ; la page Coût dit {attendu}")

    coefficient_3 = g.nombre(horizon.coefficient("notionnel_prospectif"), 2)
    economie_3 = g.pourcentage(1 - 1 / horizon.coefficient("notionnel_prospectif"), decimales=0)
    assert normaliser(
        f"Lire les {coefficient_3} du\nscénario 3 en {solde.derniere_annee} comme "
        f"une économie de {economie_3}") in normaliser(readme), (
        "la phrase du README sur le scénario 3 ne dit plus ce que dit le tableau")


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
    # La partie « D'où viennent les chiffres » de Méthode et sources, qui a été
    # la page Sources, garde sa phrase en langage courant : elle est devenue
    # l'introduction de la partie, une page ne portant qu'un « En clair ».
    methode = rendre(contexte, "/methode", {})[1]
    sources = methode[methode.index('<h2 id="sources" tabindex="-1">'):]
    assert "viennent des\ninstitutions qui les produisent" in sources
    assert methode.count("<strong>En clair.</strong>") == 1


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


def test_les_resultats_s_ouvrent_sur_le_resume_la_cle_puis_les_montants(contexte):
    """Sous « Résultats » : trois phrases qui répondent à la question de
    l'électeur, puis la clé qui dit ce qu'on regarde, puis les quatre montants,
    puis seulement les repères techniques. Dans l'ordre inverse, un téléphone
    montrait un coefficient de conversion et pas un euro ; sans le résumé, il
    montrait dix nombres et rien qui dise lesquels comparer."""
    corps = rendre(contexte, "/simuler", SIMULATION_TEMOIN)[1]
    visible = _hors_depliants(corps)
    resultats = visible.index('id="resultats"')
    bref = visible.index('<section class="en-bref"', resultats)
    lecture = visible.index("Quatre calculs pour votre carrière", resultats)
    premier = visible.index('<div class="scenario">', lecture)
    reperes = visible.index('<div class="fiches">', resultats)
    assert bref < lecture < premier < reperes
    cle = visible[lecture:premier]
    assert "C'est la référence." in cle
    # La clé nomme la proposition, et dit ce que sont les deux autres : sans
    # cela, l'électeur comparait le 1 au 2, que personne ne propose.
    assert "Le système 4 est notre proposition." in cle
    assert "Les systèmes 2 et 3 ne sont pas des\npropositions" in cle
    assert "votre <strong>salaire</strong> pendant" in cle
    assert "la <strong>pension</strong> que le système promet" in cle
    # Le troisième chiffre est annoncé lui aussi : il est apparu sans que la
    # clé change, et elle a promis « deux chiffres par ligne » au-dessus de
    # trois pendant le temps d'une session.
    assert "ce qu'elles en paient\n<strong>vraiment</strong>" in cle
    # Le mode se lit dans la clé, et il vaut pour les TROIS chiffres : c'est
    # précisément ce que la bascule garantit, et ce que le site ne faisait pas
    # quand il opposait un salaire net à une pension brute.
    # Le mot du mode et l'unité sont sur deux lignes du gabarit : on compare
    # donc sur le texte aplati, comme le lecteur le lit.
    aplati = " ".join(cle.split())
    assert "en net tous les trois, par mois, en euros d'aujourd'hui" in aplati
    # Ce que la clé disait APRÈS les chiffres qu'elle annonçait — que le
    # troisième n'est pas une prévision, et la CSG que le net suppose — se lit
    # sous les barres, une fois qu'on sait de quoi il parle. La clé en était
    # deux fois plus longue.
    carte = " ".join(visible[premier:reperes].split())
    assert "n'est pas une prévision" in carte
    assert "au <strong>taux plein</strong>" in carte
    paragraphe = cle[:cle.index("</p>")]
    assert len(re.sub(r"<[^>]+>", " ", paragraphe).split()) < 90, (
        "la clé de lecture s'allonge de nouveau")


def _somme_affichee(texte: str) -> float:
    return float(texte.replace("\u202f", "").replace(",", "."))


def test_la_vue_des_resultats_est_a_l_euro(contexte):
    """« 2 795 € » dans « En bref », « 2 795,42 » sur la barre juste dessous :
    deux écritures du même nombre, relevées le 23 septembre 2026. Ce qui se
    lit sans rien déplier — les quatre barres, la ligne qui compose le
    système 4, ce que le salaire devient — est à l'euro. Le centime, que la
    caisse verse, reste dans les dépliants, là où l'on refait le calcul.
    """
    corps = rendre(contexte, "/simuler", SIMULATION_TEMOIN)[1]
    visible = _hors_depliants(corps)
    au_centime = re.findall(
        r'\d,\d\d\u202f€|<span class="somme">[\d\u202f]+,\d\d<', visible)
    assert not au_centime, f"montants au centime sur la vue : {au_centime[:3]}"
    assert re.search(r"\d,\d\d\u202f€", corps), "le détail a perdu ses centimes"


def test_le_resume_des_resultats_redit_les_chiffres_des_barres(contexte):
    """« En bref » ne calcule rien : il redit, arrondis à l'euro, les montants
    que les barres affichent juste dessous — le système actuel, la
    proposition sans rien ajouter puis avec les points rendus, le salaire net.

    ET IL LE FAIT SYMÉTRIQUEMENT. Le manque de financement est écrit pour les
    deux systèmes, dans les mêmes mots et au même euro que sous leurs barres :
    le taire pour l'un flatterait l'autre (action 62). Les systèmes 2 et 3,
    étalons et non choix, n'y figurent pas.
    """
    corps = rendre(contexte, "/simuler", SIMULATION_TEMOIN)[1]
    bref = re.search(r'<section class="en-bref".*?</section>', corps, re.S).group(0)
    # Les blancs ORDINAIRES seuls sont repliés : `split()` couperait aussi
    # l'espace fine insécable des milliers, que les montants portent.
    texte = re.sub(r"[ \t\n]+", " ", re.sub(r"<[^>]+>", " ", bref))
    blocs = corps.split('<div class="scenario">')[1:]
    actuel, liberal = blocs[0], blocs[3]

    def principal(bloc: str) -> float:
        return _somme_affichee(re.search(
            r'class="chiffre principal">.*?<span class="somme">([^<]+)</span>',
            bloc, re.S).group(1))

    def euro(montant: float) -> str:
        return euros(montant)

    assert euro(principal(actuel)) in texte
    assert euro(principal(liberal)) in texte
    plancher = _somme_affichee(re.search(
        r"soit\s+([\d\u202f]+)\u202f€ par\s+mois sans rien ajouter",
        liberal).group(1))
    assert f"serait de {euro(plancher)} nets par mois" in texte
    assert f"jusqu'à {euro(principal(liberal))}" in texte
    # Les manques, au même euro que sous les barres, et dans les mêmes mots :
    # « Elle n'est pas entièrement financée », « Elle non plus ». Un système
    # que ses comptes financent n'en a pas, et le résumé ne lui en prête pas :
    # c'est le cas de la proposition depuis la TVA à taux unique.
    manques = {}
    for nom, bloc in (("actuel", actuel), ("liberal", liberal)):
        trouve = re.search(r"il manque ([^<]+) par mois", bloc)
        manques[nom] = trouve.group(1) if trouve else None
        if trouve:
            assert f"il manque {trouve.group(1)} par mois" in texte
    assert manques["actuel"], "le système actuel du témoin n'est pas financé"
    assert "Elle n'est pas entièrement financée" in texte
    assert ("Elle non plus n'est pas entièrement financée" in texte) == bool(
        manques["liberal"])
    # Le salaire net, celui que « Et pendant que vous cotisez » chiffre au même
    # euro.
    gain = _somme_affichee(re.search(
        r'<span class="ecart">\+([\d\u202f]+)\u202f€ par mois</span>',
        liberal).group(1))
    assert f"augmente de {euro(gain)} par mois" in texte
    # Ni le 2 ni le 3 : leurs montants ne sont pas dans le résumé.
    for bloc in blocs[1:3]:
        assert euro(principal(bloc)) not in texte
    # Le renvoi vers « qui paiera » vise un dépliant qui existe, sans toucher
    # à la route.
    assert 'data-vers="resultats-financement"' in bref
    assert 'id="resultats-financement"' in corps


def test_le_resume_dit_au_retraite_que_sa_pension_serait_recalculee(contexte):
    """La première question d'un retraité : « et la mienne ? ». L'étape 2 du
    programme y répond — les pensions liquidées avant la bascule sont
    recalculées sur ce qui a été cotisé —, et le résumé le dit dans ces mots,
    sans ligne de salaire.

    La pension qu'il y lit est celle qu'il touche AUJOURD'HUI, et c'est celle
    qu'il a saisie : 1 600 € nets en 2026, et non 1 600 € en avril 2017. Le
    résumé disait « votre retraite était de », et donnait la pension du
    départ ramenée par les prix — ce que personne n'a jamais touché."""
    corps = rendre(contexte, "/simuler", {
        "situation": "retraite", "saisie": "pension", "unite_revenu": "euros_mois",
        "naissance": "1955-03-01", "liquidation": "2017-04-01",
        "debut": "1975-09-01", "statut": "salarie_prive_non_cadre",
        "pension": "1600"})[1]
    bref = re.search(r'<section class="en-bref".*?</section>', corps, re.S).group(0)
    texte = re.sub(r"[ \t\n]+", " ", re.sub(r"<[^>]+>", " ", bref))
    assert "votre retraite est aujourd'hui de 1\u202f600\u202f€ nets par mois" in texte
    assert "celle de votre départ, en avril 2017, revalorisée depuis" in texte
    assert "elle serait recalculée sur ce qui a été cotisé" in texte
    assert "Pendant que vous travaillez" not in texte


def test_le_retraite_lit_le_chemin_de_sa_pension_depuis_son_depart(contexte):
    """Le cas type de ``tests/test_revalorisation.py``, saisi sur le site : un
    non-cadre né en 1950, parti en janvier 2012. Sa pension de 2026 est
    1 780,61 € bruts par mois — celle de son départ, 1 477,46 €, menée par
    les treize revalorisations du régime général (×1,2215) et la valeur du
    point Agirc-Arrco (×1,1589). Le dépliant refait ce chemin régime par
    régime, dit la tranche de 2020 — 1 537,80 € en décembre 2019, donc 1 % —
    et ce que la page affichait avant : la pension du départ ramenée par les
    prix, 1 844,09 €, que ce retraité n'a jamais touchée."""
    corps = rendre(contexte, "/simuler", {
        "situation": "retraite", "saisie_par": "revenu", "salaire": "0.8",
        "unite_revenu": "moyen", "naissance": "1950-01-01", "liquidation": "62",
        "debut": "20", "statut": "salarie_prive_non_cadre", "sexe": "H"})[1]
    debut = corps.index('id="resultats-aujourdhui"')
    bloc = corps[debut:corps.index("</details>", debut)]
    texte = re.sub(r"[ \t\n]+", " ", re.sub(r"<[^>]+>", " ", bloc)).replace("\u202f", " ")
    assert "Votre pension a pris effet en janvier 2012." in texte
    assert "385,34 € ×1,1589 446,55 €" in texte
    assert "1 092,13 € ×1,2215 1 334,06 €" in texte
    assert "Pension du système actuel 1 477,46 € ×1,2052 1 780,61 €" in texte
    assert "votre pension de départ vaudrait 1 844,09 € bruts par mois" in texte
    assert "Pour vous, 1 537,80 € en décembre 2019 : +1,0 %." in texte


def test_aucun_lien_ne_remplace_la_route_par_une_ancre(contexte):
    """Ici l'adresse EST la route : un lien « #resultats-financement » la
    remplaçait, et le routeur, ne reconnaissant aucune page, rendait
    l'accueil — le lecteur qui cliquait dans la clé de lecture perdait sa
    simulation. Tout lien interne vise une route ; une section se rejoint par
    ``data-vers``, que le script de la page traite sans toucher à l'adresse."""
    pages = [("/simuler", SIMULATION_TEMOIN)] + [(chemin, {}) for chemin in TITRES]
    for chemin, parametres in pages:
        corps = rendre(contexte, chemin, parametres)[1]
        ancres = re.findall(r'href="(#[^/"][^"]*)"', corps)
        assert not ancres, f"{chemin} : {ancres}"


def test_tout_lien_interne_mene_a_une_page_qui_existe(contexte):
    """Un lien vers « #/methode/ » ne mène pas à la page Méthode : le routeur
    ne connaît pas cette route, et rend l'accueil. Trois liens du site
    portaient cette barre de trop — vers Méthode depuis l'accueil et depuis
    les résultats, vers les sources depuis les résultats —, et l'électeur qui
    les suivait revenait au programme sans comprendre pourquoi."""
    pages = [("/simuler", SIMULATION_TEMOIN)] + [(chemin, {}) for chemin in TITRES]
    for chemin, parametres in pages:
        corps = g.entete(chemin) + rendre(contexte, chemin, parametres)[1]
        for cible in re.findall(r'href="#(/[^"?]*)', corps):
            assert cible in TITRES, f"{chemin} : lien vers {cible!r}, route inconnue"


def test_chaque_renvoi_vise_une_section_qui_existe(contexte):
    """``data-vers`` ouvre une section sans toucher à la route : une cible
    absente laisse le lien agir en lien ordinaire, et le lecteur arrive en
    haut d'une page au lieu de la section promise. La cible est cherchée sur
    la page que le lien désigne — la même, le plus souvent ; celle de Coût
    quand Carrières types renvoie au coefficient d'équilibre."""
    pages = [("/simuler", SIMULATION_TEMOIN)] + [(chemin, {}) for chemin in TITRES]
    rendues = {}
    for chemin, parametres in pages:
        corps = rendre(contexte, chemin, parametres)[1]
        rendues.setdefault(chemin, corps)
        for route, cible in re.findall(
                r'href="#(/[^"?]*)[^"]*" data-vers="([^"]+)"', corps):
            destination = corps if route == chemin else rendues.setdefault(
                route, rendre(contexte, route, {})[1])
            assert f'id="{cible}"' in destination, (
                f"{chemin} : section {cible!r} absente de {route}")


#: Les questions de l'accueil, dans l'ordre où elles s'y posent.
QUESTIONS_DE_L_ELECTEUR = (
    "Ma retraite va-t-elle baisser ?",
    "Je suis déjà à la retraite : qu'est-ce qui change pour moi ?",
    "Pourquoi changer de système ?",
    "Que deviennent mes trimestres et mes points ?",
    "À quel âge pourrai-je partir ?",
    "Qu'est-ce qui change sur ma fiche de paie ?",
    "Et les petites retraites ?",
    "Et si je meurs ? Et mon conjoint ?",
    "Mon argent sera-t-il placé en Bourse ?",
    "Et les fonctionnaires, les régimes spéciaux ?",
    "Comment passe-t-on d'un système à l'autre ?",
    "Combien cela coûte-t-il, et qui paie ?",
    "Ces chiffres sont-ils fiables ?",
)


#: Ce que chaque question de l'accueil range derrière sa réponse courte : le
#: titre du développement qui la traitait, jusqu'au 23 septembre 2026, dans
#: un second empilement de dépliants, « Pour aller plus loin ».
DEVELOPPEMENTS_DES_QUESTIONS = {
    "Pourquoi changer de système ?": "En quoi ce serait plus juste",
    "Qu'est-ce qui change sur ma fiche de paie ?": "Les impôts que nous supprimons",
    "Et les petites retraites ?":
        "Le plancher, et ce qu'il change pour les petites pensions",
    "Mon argent sera-t-il placé en Bourse ?": "La part capitalisée :",
    "Combien cela coûte-t-il, et qui paie ?":
        "Ce qui pouvait nous arrêter, et ce que nous en avons fait",
    "Ces chiffres sont-ils fiables ?": "Pourquoi ce site.",
}


def test_l_accueil_range_chaque_sujet_sous_une_seule_question(contexte):
    """« Même moi je m'y perds » (23 septembre 2026).

    L'accueil alignait deux piles de dépliants : onze questions de l'électeur,
    puis neuf « Pour aller plus loin » qui reprenaient les mêmes sujets dans la
    voix du programme — le plancher, la part capitalisée, le coût —, et vers
    lesquels chaque réponse courte renvoyait : vingt titres en deux voix. Il
    n'y a plus qu'une liste de treize questions : chaque développement est
    rangé derrière la réponse courte de la question qu'il traite, et les deux
    dépliants qui ne faisaient que redire sont partis — le calcul, que les
    trois gestes disent en clair, et un plan du site que le bandeau porte.
    """
    corps = html.unescape(rendre(contexte, "/", {})[1])
    assert "Pour aller plus loin" not in corps
    depliants = re.findall(
        r'<details class="section"(?: id="[^"]+")?><summary>.*?<span>(.*?)</span>'
        r"</summary>(.*?)</details>", corps, re.S)
    # Une seule liste, faite de questions.
    assert [titre for titre, _ in depliants] == list(QUESTIONS_DE_L_ELECTEUR)
    reponses = dict(depliants)
    for question, developpement in DEVELOPPEMENTS_DES_QUESTIONS.items():
        assert developpement in reponses[question], (question, developpement)
        # La réponse courte vient d'abord, le développement ensuite.
        assert reponses[question].index("<p>") < reponses[question].index(
            developpement), question
    # Les trois gestes ne se disent qu'une fois : en clair, sous leur titre.
    assert corps.count("On inscrit</strong>") == 1
    assert corps.count("On revalorise</strong>") == 1


def test_l_accueil_repond_aux_questions_de_l_electeur(contexte):
    """L'électeur arrive avec ses questions, pas avec le plan du programme.

    Elles sont posées dans ses mots, après le tableau qui oppose les deux
    systèmes, chacune repliée sur sa réponse : la liste se parcourt du regard
    et ne coûte rien au budget de lecture. La première est celle qui coûte, et
    sa réponse dit ce que le simulateur montrera.
    """
    corps = rendre(contexte, "/", {})[1]
    texte = html.unescape(corps)
    rangs = [texte.index(f"<span>{question}</span></summary>")
             for question in QUESTIONS_DE_L_ELECTEUR]
    assert rangs == sorted(rangs), "les questions ne sont plus dans l'ordre"
    assert texte.index("Le système actuel et notre programme") < rangs[0]
    assert rangs[-1] < texte.index("Vérifiez plutôt que de nous croire")
    # Repliées : aucune réponse ne se lit sans avoir ouvert sa question.
    visible = html.unescape(_hors_depliants(corps))
    assert "<h2>Vos questions</h2>" in visible
    for question in QUESTIONS_DE_L_ELECTEUR:
        assert question not in visible
    # La réponse à la première question ne se dérobe pas.
    assert ("Le plus souvent, elle sera plus basse que ce que le système "
            "actuel\npromet, de l'ordre ") in texte
    # Les montants de la garantie sont ceux des paramètres.
    base = contexte.base
    assert g.euros(base.garantie_vieillesse_mensuelle
                   + base.allocation_isolement_mensuelle) in texte


def _replier(texte: str) -> str:
    """Les blancs du HTML repliés, SAUF les espaces fines et insécables.

    ``str.split()`` les compte pour des blancs : « 31 % » avec son espace fine
    en devenait un autre texte que celui que la page écrit.
    """
    return re.sub(r"[ \t\n]+", " ", texte)


def test_l_accueil_dit_de_combien_la_retraite_baisse(contexte):
    """« Pour que les gens aient une idée de la baisse » (23 septembre 2026).

    L'accueil disait que la retraite serait le plus souvent plus basse, sans
    dire de combien. Il le dit à deux endroits, et au même chiffre : dans le
    tableau qui oppose les deux systèmes, OUVERT — c'est ce que le lecteur
    pressé voit —, et dans la réponse à la première question, qui détaille les
    trois écarts médians. Les chiffres sont ceux du bilan figé, écrits sans
    signe parce que la phrase dit « baisse » ; l'ordre de grandeur en toutes
    lettres est tiré des deux écarts de ce qu'on touche sans rien ajouter.
    """
    corps = rendre(contexte, "/", {})[1]
    texte = _replier(html.unescape(corps))
    ecarts = contexte.bilan().ecarts
    assert ecarts is not None, "le bilan figé ne porte pas les écarts médians"
    ordre = _ordre_de_grandeur(ecarts)

    # Le tableau, sans rien déplier.
    visible = _replier(html.unescape(_hors_depliants(corps)))
    assert (f'<th class="" scope="row">Votre retraite</th><td class="texte">ce que '
            f'votre régime promet</td><td class="texte">{ordre} de moins, en '
            "médiane</td>") in visible

    # La réponse : l'ordre de grandeur en gras, puis les trois médianes.
    assert (f"<strong>Le plus souvent, elle sera plus basse que ce que le "
            f"système actuel promet, {ordre}.</strong>") in texte
    for ecart in (ecarts.a_venir, ecarts.a_venir_volontaire, ecarts.deja_liquidees):
        assert ecart < 0.0
        assert f"{pourcentage(-ecart, decimales=0)}" in texte
    assert (f"la baisse médiane est de {pourcentage(-ecarts.a_venir, decimales=0)} "
            "pour qui n'est pas encore à la retraite") in texte
    assert (f"la pension d'aujourd'hui baisse ainsi de "
            f"{pourcentage(-ecarts.deja_liquidees, decimales=0)} en médiane") in texte
    # La preuve est à un clic : la grille des carrières types.
    assert '<a href="#/cas-types">treize carrières types</a>' in texte


@pytest.mark.parametrize(("part", "mots"), [
    (0.24, "un quart"), (0.31, "un tiers"), (0.26, "un quart"),
    (0.48, "la moitié"), (0.05, "un dixième"), (0.9, "trois quarts"),
])
def test_une_part_se_dit_par_la_fraction_la_plus_proche(part, mots):
    assert _fraction_en_mots(part) == mots


def test_l_ordre_de_grandeur_elide_ce_qu_il_faut():
    """« d'un quart », mais « de la moitié » et « de deux cinquièmes »."""
    def ecarts(a_venir, deja):
        return EcartsFiges(a_venir=a_venir, a_venir_volontaire=a_venir,
                           deja_liquidees=deja, cases_a_venir=1,
                           cases_deja_liquidees=1)

    assert _ordre_de_grandeur(ecarts(-0.31, -0.26)) == "de l'ordre d'un quart à un tiers"
    assert _ordre_de_grandeur(ecarts(-0.33, -0.34)) == "de l'ordre d'un tiers"
    assert _ordre_de_grandeur(ecarts(-0.5, -0.4)) == (
        "de l'ordre de deux cinquièmes à la moitié")
    # Les cinq points volontaires n'entrent pas dans l'ordre de grandeur.
    assert _ordre_de_grandeur(EcartsFiges(
        a_venir=-0.31, a_venir_volontaire=-0.05, deja_liquidees=-0.31,
        cases_a_venir=1, cases_deja_liquidees=1)) == "de l'ordre d'un tiers"


def test_un_paquet_sans_ecarts_ne_fait_pas_tomber_l_accueil():
    """Un bilan écrit avant les écarts médians : l'accueil se tait sur le chiffre.

    Le navigateur garde le paquet en cache (``force-cache``) : un lecteur
    revenu après le 23 septembre 2026 peut recevoir le nouveau code et l'ancien
    paquet. L'accueil ne doit pas en tomber ; il retrouve la réponse d'avant,
    sans chiffre, et le tableau sa ligne d'avant.
    """
    ancien = Contexte()
    ancien._donnees["bilan"] = dataclasses.replace(ancien.bilan(), ecarts=None)
    corps = rendre(ancien, "/", {})[1]
    texte = _replier(html.unescape(corps))
    assert ("<strong>Le plus souvent, elle sera plus basse que ce que le "
            "système actuel promet.</strong> Votre retraite vaudra") in texte
    assert "baisse médiane" not in texte
    assert "Votre retraite</th>" not in texte
    assert "c'est une avance, reprise sur la succession. Pour votre cas" in texte


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
    retraite. Ce que les comptes du système FINANCENT de cette pension y a
    rejoint le salaire, pour la même raison et sous la même règle : une
    étiquette, et l'unité des autres.

    Une seule chose reste exigée — un seul `chiffre principal`, celui de la
    pension, et lui seul dans les euros de l'année de référence.
    """
    corps = rendre(contexte, "/simuler", SIMULATION_TEMOIN)[1]
    depart = SIMULATION_TEMOIN["liquidation"][:4]
    for bloc in corps.split('<div class="scenario">')[1:]:
        entete = bloc.split('<div class="barre')[0]
        assert entete.count('class="chiffre principal"') == 1
        assert f"en euros de {depart}" not in entete
        # L'unité longue a quitté les cartes — deux mots suffisent sous chaque
        # nombre — et la clé de lecture la porte une fois pour toutes. Ce que
        # la carte doit dire, c'est le MODE, et le même pour TOUS ses chiffres :
        # le test compte donc les unités plutôt qu'il n'en fixe le nombre, et
        # exige qu'aucune ne s'écarte des autres.
        unites = re.findall(r'<span class="unite">([^<]*)</span>', entete)
        assert unites
        assert set(unites) == {"€ net/mois"}
        # Le second chiffre, s'il est là, dit de quoi il parle : sans son
        # étiquette, deux nombres se toucheraient sans que rien ne les sépare.
        if 'class="chiffre salaire"' in entete:
            assert ">salaire</span>" in entete
            assert "€ net/mois" in entete
        # Le troisième, de même : il dit ce que les comptes financent de la
        # pension promise, et il ne paraît que là où ils en financent moins
        # qu'elle. Sans son étiquette, il se lirait comme un montant de plus.
        if 'class="chiffre finance"' in entete:
            assert ">vraiment payé</span>" in entete
    assert "Deux fois le même montant" not in corps
    assert "grand chiffre" not in corps
    assert f"en euros de {depart}" not in corps.split('<div class="carte">')[0]
    assert ("en net tous les trois, par mois, en euros d'aujourd'hui"
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
    # L'écart de SALAIRE, et lui seul : le troisième chiffre de chaque ligne
    # porte le sien — « il manque tant par mois » —, dans le même idiome et
    # sous la même classe. Les distinguer par le texte plutôt que par le
    # compte évite de faire échouer ce test-ci pour un manque de financement,
    # qui n'est pas son sujet.
    def _ecarts_de_salaire(entete: str) -> list[str]:
        return [texte for texte in re.findall(r'<span class="ecart">(.*?)</span>',
                                              entete, re.S)
                if "il manque" not in texte]

    assert len(_ecarts_de_salaire(entetes[3])) == 1
    assert sum(len(_ecarts_de_salaire(entete)) for entete in entetes[:3]) == 0


def test_le_tableau_du_plancher_est_en_haut_de_l_accueil(contexte):
    """L'argument le plus parlant du site — « 300 € et 1 500 € : 0 € aujourd'hui,
    500 € avec la garantie » — se lit sans rien déplier, avant le tableau qui
    oppose les deux systèmes, et n'est plus répété dans le dépliant."""
    corps = rendre(contexte, "/", {})[1]
    visible = _hors_depliants(corps)
    assert "Ce que le plancher individualisé change, par mois" in visible
    # Des espaces insécables : « 1 500 / € » se coupait en deux sur un téléphone.
    # Les montants sont ceux du site, à espace fine insécable, depuis que les
    # deux colonnes sont calculées (23 septembre 2026).
    assert "\u202f€ et 1\u202f500\u202f€" in visible
    assert visible.index("300\u202f€ et 1\u202f500\u202f€") < visible.index("Le système actuel et notre programme")
    assert corps.count("<caption><span>Ce que le plancher individualisé change, par mois</span></caption>") == 1
    assert "Le tableau du haut de page le montre" in corps


# -- la revue du 15 septembre 2026 : le thème « architecture » -----------------


def test_la_navigation_met_l_electeur_d_abord():
    """Deux voix dans le bandeau : ce que l'électeur vient chercher, puis ce
    qui permet de le vérifier.

    Dix onglets de même poids ne disaient pas par où commencer, et six d'entre
    eux ne répondent qu'à qui veut vérifier. Les pages qui répondent aux
    questions de l'électeur — le programme, sa retraite, le coût, pourquoi
    changer — restent des onglets ; celles qui les prouvent passent derrière
    une étiquette qui SE VOIT, « Pour vérifier ». Les autres étiquettes restent
    dites aux synthèses vocales et sorties de l'écran, par `clip-path` et non
    par `display: none`.

    Les libellés disent ce qu'on trouve : « Avantages » se lisait comme les
    avantages de la réforme, « Risque » ne disait pas de quoi, « Trajectoire »
    et « Cas types » étaient des mots du modèle.
    """
    entete = g.entete("/cout")
    groupes = re.findall(r'<span class="(groupe(?: secondaire)?)"><span class="etiquette">(.*?)</span>'
                         r'(?:<button type="button" class="deplier"[^>]*>.*?</button>)?'
                         r'<span class="liens"(?: id="[^"]+")?>(.*?)</span></span>', entete)
    assert [(classe, etiquette) for classe, etiquette, _ in groupes] == [
        ("groupe", "L&#x27;essentiel"), ("groupe", "Faire connaître"),
        ("groupe secondaire", "Pour vérifier")]
    pages = [re.findall(r'href="([^"]+)"', liens) for _, _, liens in groupes]
    assert pages == [["#/", "#/simuler", "#/cout", "#/risque"],
                     ["#/partager"],
                     ["#/cas-types", "#/avantages", "#/methode"]]
    libelles = [re.findall(r">([^<]+)</a>", liens) for _, _, liens in groupes]
    assert libelles == [["Programme", "Simuler", "Coût", "Pourquoi changer"],
                        ["Partager"],
                        ["Carrières types", "Droits non cotisés",
                         "Méthode et sources"]]
    assert 'href="#/cout" aria-current="page"' in entete
    assert [chemin for chemin, _ in g.LIENS] == [
        "/", "/simuler", "/cout", "/risque", "/partager",
        "/cas-types", "/avantages", "/methode"]
    # Le titre de chaque page est le libellé de son onglet : c'est lui que
    # l'onglet du navigateur affiche.
    assert dict(g.LIENS) == TITRES
    assert list(TITRES) == [chemin for chemin, _ in g.LIENS]
    # L'étiquette est masquée à l'œil, pas à l'oreille ; celle du groupe
    # secondaire, elle, se voit.
    assert "nav .etiquette" in g.FEUILLE_DE_STYLE
    etiquette = g.FEUILLE_DE_STYLE.split("nav .etiquette {")[1].split("}")[0]
    assert "clip-path" in etiquette and "display: none" not in etiquette, (
        "une étiquette en display:none quitte aussi l'arbre d'accessibilité"
    )
    visible = g.FEUILLE_DE_STYLE.split("nav .groupe.secondaire .etiquette {")[1].split("}")[0]
    assert "clip-path: none" in visible
    # L'onglet courant ne se signale pas QUE par la couleur : un soulignement
    # épais le marque, et `aria-current` l'annonce.
    actif = g.FEUILLE_DE_STYLE.split('nav a[aria-current="page"] {')[1].split("}")[0]
    assert "border-bottom-color" in actif


def test_les_adresses_des_pages_parties_menent_a_leur_contenu(contexte):
    """Huit pages au lieu de dix (23 septembre 2026) : « Cumul versé » redisait
    un dépliant des résultats, « Sources » est devenue la fin de Méthode.

    Leurs adresses restent valides — le site parent et des partages les
    portent — et rendent la page qui les a remplacées ; la section qui porte
    leur contenu existe sur cette page, et le routeur d'``index.html`` l'ouvre.
    """
    from pathlib import Path

    from retraite_notionnelle.web.pages import ANCIENNES_ROUTES

    assert set(ANCIENNES_ROUTES) == {"/trajectoire", "/donnees"}
    for ancienne, (page, section) in ANCIENNES_ROUTES.items():
        assert ancienne not in TITRES and page in TITRES
        parametres = SIMULATION_TEMOIN if page == "/simuler" else {}
        titre, corps = rendre(contexte, ancienne, parametres)
        assert (titre, corps) == rendre(contexte, page, parametres), ancienne
        assert f'id="{section}"' in corps, (ancienne, section)

    racine = Path(__file__).resolve().parents[1]
    portage = (racine / "moteur" / "js" / "pages.js").read_text(encoding="utf-8")
    assert '"/trajectoire": ["/simuler", "cumul"],' in portage
    assert '"/donnees": ["/methode", "sources"],' in portage
    script = (racine / "index.html").read_text(encoding="utf-8")
    assert "ANCIENNES_ROUTES[route]" in script
    assert "if (section) { ouvrirSection(section); }" in script


def test_sur_un_telephone_le_groupe_pour_verifier_se_replie():
    """« Le menu sur téléphone occupe quatre lignes avant même le titre »
    (23 septembre 2026). Le groupe « Pour vérifier » en prenait deux à lui
    seul : il se replie derrière un bouton qui porte son nom et son état, à la
    suite des onglets, et la barre tient en deux rangées à 390 points.

    Le bouton n'existe qu'à l'écran étroit : au-delà, l'étiquette reste un
    texte et les liens restent sous les yeux. Il s'ouvre de lui-même quand la
    page courante est dans le groupe, pour que l'onglet courant se voie. Le
    basculement vit dans ``index.html``, en écoute déléguée : le bandeau est
    réécrit à chaque page, un gestionnaire posé sur le bouton partirait avec.
    """
    def bouton(chemin: str) -> str:
        entete = g.entete(chemin)
        trouves = re.findall(r'<button type="button" class="deplier"[^>]*>', entete)
        assert len(trouves) == 1, f"{chemin} : {len(trouves)} boutons de repli"
        cible = re.search(r'aria-controls="([^"]+)"', trouves[0]).group(1)
        assert f'<span class="liens" id="{cible}">' in entete
        return trouves[0]

    assert 'aria-expanded="false"' in bouton("/")
    assert 'aria-expanded="false"' in bouton("/cout")
    secondaires = dict(g.GROUPES_NAVIGATION)[g.GROUPE_SECONDAIRE]
    for chemin, _ in secondaires:
        assert 'aria-expanded="true"' in bouton(chemin), chemin

    style = g.FEUILLE_DE_STYLE
    assert "nav .deplier { display: none; }" in style
    etroit = style.split("@media (max-width: 48rem) {\n  nav .groupe.secondaire { display: contents; }")
    assert len(etroit) == 2, "le repli n'est plus réservé à l'écran étroit"
    assert 'nav .deplier[aria-expanded="false"] + .liens { display: none; }' in etroit[1]

    from pathlib import Path
    script = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
    assert 'closest?.("nav button.deplier")' in script
    assert 'bouton.setAttribute("aria-expanded", String(ouvrir));' in script


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
                    'href="#/methode" data-vers="sources"'):
        assert attendu in dedans, attendu
    assert not re.search(r"\b\d{3,} (?:tests|témoins|carrières)", dedans), (
        "un nombre de tests ou de témoins écrit à la main dériverait"
    )


def test_la_page_risque_chiffre_le_prelevement_depuis_le_modele(contexte):
    """Ce que la retraite prélève, recalculé ici plutôt que recopié.

    La page tient trois chiffres qui ne viennent d'aucune source extérieure :
    ce qu'un salarié du privé verse chaque mois pour sa retraite à trois
    niveaux de salaire, la part de la pension promise que ses propres
    cotisations ne financent pas, et le solde du système. Ce test les refait
    depuis le modèle et les cherche dans la page : un taux de cotisation qui
    change, un compte du COR mis à jour, et c'est ici que la phrase périmée
    apparaît.
    """
    from retraite_notionnelle.web.pages import (
        MOIS_PAR_AN, NIVEAUX_RISQUE, _risque_exemple,
    )

    corps = rendre(contexte, "/risque", {})[1]
    exemples = [_risque_exemple(contexte, niveau) for _, niveau in NIVEAUX_RISQUE]

    # Les trois lignes du tableau des salaires, au centime.
    for comparaison in exemples:
        fiche = comparaison.remuneration.reference.droit_en_vigueur
        assert g.euros(fiche.retraite_totale / MOIS_PAR_AN) in corps
        assert g.euros(fiche.brut / MOIS_PAR_AN) in corps
    moyen = exemples[1]
    fiche_moyen = moyen.remuneration.reference.droit_en_vigueur
    verse = g.euros(fiche_moyen.retraite_totale / MOIS_PAR_AN)
    # Le chiffre de tête est celui du salaire moyen, et il est aussi dans le
    # chapeau de l'affiche : les deux doivent bouger ensemble.
    assert corps.count(verse) >= 3, verse
    # Au SMIC, la part du brut est plus faible qu'au salaire moyen : ce sont
    # les allègements généraux, et la page l'explique.
    parts = [c.remuneration.reference.droit_en_vigueur.retraite_totale
             / c.remuneration.reference.droit_en_vigueur.brut for c in exemples]
    assert parts[0] < parts[1] < parts[2]
    assert "allègements généraux compris" in corps

    # L'écart entre la promesse et ce que les cotisations financent.
    constants = moyen.coefficient_euros_constants
    promis = moyen.actuel.pension_annuelle * constants
    finance = moyen.notionnel_retroactif_employeur.pension_annuelle * constants
    assert finance < promis, "l'exemple ne montre plus d'écart à financer"
    assert g.pourcentage(1 - finance / promis, decimales=0) in corps
    assert g.pourcentage(finance / promis, decimales=0) in corps

    # Le solde, lu dans les mêmes comptes que la page Coût.
    solde = contexte.cout().solde
    horizon = solde.annee(solde.derniere_annee)
    assert g.pourcentage(
        -horizon.solde("actuel") / horizon.depense("actuel"), decimales=0) in corps
    assert f'scope="row">{solde.derniere_annee_observee} (observé)</th>' in corps


def test_la_page_risque_cite_le_COR_mot_pour_mot(contexte):
    """Les phrases du COR sont citées, pas résumées.

    Elles portent l'essentiel de l'argumentaire, et elles valent parce
    qu'elles viennent de l'institution qui projette : les paraphraser les
    affaiblirait, et les déformer serait pire. Ce test tient les citations à
    la lettre. Elles ont été relevées dans le rapport annuel de juin 2026.
    """
    corps = rendre(contexte, "/risque", {})[1]
    # Sur la prose remise à plat : le gabarit coupe les lignes où il veut, et
    # une citation ne doit pas dépendre de l'endroit où elle est coupée.
    texte = _prose(corps)
    for citation in (
        "trois des quatre leviers étudiés",
        "présentent un caractère récessif",
        "renforcent les difficultés à financer les dépenses publiques autres "
        "que les retraites, à l'instar de l'école, la santé ou la sécurité",
        "54,6 % en 2025 à 45,3 % en 2070",
        "demeurerait durablement en besoin de financement",
        "qui conduit à abaisser le PIB par habitant",
    ):
        assert citation in texte, citation
    # Les deux blocs de citation sont des citations, et le HTML le dit.
    assert corps.count("<blockquote>") == 2


def test_la_page_risque_range_ses_sections_et_se_relie(contexte):
    """Le plan, l'ordre des sections, et les liens qui font le tour du site."""
    corps = rendre(contexte, "/risque", {})[1]
    plan = re.search(r'<nav class="plan".*?</nav>', corps, re.S).group(0)
    assert re.findall(r'data-vers="([^"]+)"', plan) == [
        "risque-prelevement", "risque-promesse", "risque-salaire",
        "risque-croissance", "risque-pauvres", "risque-jeunes",
        "risque-evince", "risque-deja", "risque-objections",
        "risque-ailleurs", "risque-droit", "risque-sources",
    ]
    for chemin in ("/simuler", "/cout", "/"):
        assert f'href="{g.lien(chemin)}"' in corps, chemin
    assert f'href="{g.lien("/risque")}"' in rendre(contexte, "/", {})[1]

    # La bibliographie est dans le dépôt, à l'adresse annoncée.
    from pathlib import Path
    assert f'href="{g.DEPOT}/blob/main/docs/risque_de_defaut.md"' in corps
    assert (Path(__file__).resolve().parents[1] / "docs" / "risque_de_defaut.md").exists()

    # La page reste un réquisitoire honnête : elle cite le travail qui
    # contredit sa propre thèse générationnelle, et elle refuse d'affirmer une
    # éviction que personne n'a démontrée.
    texte = _prose(corps)
    assert "cité contre notre propre thèse" in texte
    assert "il ne démontre pas un mécanisme" in texte
    # Aucune probabilité de défaut n'est inventée.
    assert not re.search(r"probabilité de \d", _prose(corps))


def test_la_page_donnees_se_lit_comme_une_base(contexte):
    """Deux tables filtrables et triables : l'inventaire, croisé par famille,
    couverture et fiabilité, et les séries certifiées, par niveau."""
    corps = rendre(contexte, "/methode", {})[1]
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
        cwd=racine, capture_output=True, text=True, encoding="utf-8", check=True,
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
    "/": 3, "/simuler": 14, "/cas-types": 9, "/cout": 22,
    # Méthode et Sources ont fait une page le 23 septembre 2026 : ses bornes
    # s'additionnent, 9 et 6.
    "/methode": 15, "/partager": 4, "/risque": 4,
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
    bloc de texte du premier écran ; elle est allée dans le dépliant qui disait
    comment vérifier, parce que c'est le même geste — et parce que le premier
    écran doit tenir son budget de lecture. Ce dépliant, un plan du site que le
    bandeau porte déjà, est parti le 23 septembre 2026 : la note répond
    désormais à « Ces chiffres sont-ils fiables ? », qui est la même question.
    Ce qui reste visible est l'engagement, en une phrase sur le panneau
    crème : tout est chiffré, sur des données publiques et un modèle ouvert."""
    corps = rendre(contexte, "/", {})[1]
    assert "Il est illisible." not in corps and "Il n'est pas piloté." not in corps
    assert "Illisible, d'abord." in corps and "Et personne ne le pilote." in corps
    note = re.search(r'<div class="note signee">(.*?)</div>', corps, re.S)
    assert note, "la note signée manque"
    assert "Nous avons choisi" in note.group(1)
    assert "Nos réserves sont écrites" in note.group(1)
    assert "Le Parti libéral français, septembre 2026." in note.group(1)
    # Elle est rangée, pas supprimée : sous la question de la fiabilité.
    assert "Pourquoi ce site." not in _hors_depliants(corps)
    fiables = re.search(
        r'<details class="section" id="tout-verifier"><summary>.*?'
        r"Ces chiffres sont-ils fiables \?.*?</details>", corps, re.S)
    assert fiables and "Pourquoi ce site." in fiables.group(0)
    # Et l'engagement, lui, reste sous les yeux.
    visible = _hors_depliants(corps)
    assert "Vérifiez plutôt que de nous croire" in visible
    assert "sur des données publiques" in visible


#: Réserves au plus sur la page Coût. Il y en a cinq ; à quatorze, la liste
#: disait surtout que personne n'y avait fait le tri.
RESERVES_MAXIMUM = 8


def test_la_rubrique_des_reserves_de_la_page_cout_ne_suit_plus_le_patron(contexte):
    """« Ce que cette page ne dit pas » était un titre de gabarit, le même
    d'une page à l'autre ; celui de Coût dit ce qu'il contient, et une phrase
    d'entrée dit pourquoi il est là."""
    for chemin in TITRES:
        corps = rendre(contexte, chemin, {})[1]
        assert "<span>Ce que cette page ne dit pas</span>" not in corps, chemin
        assert "ne dit pas</span>" not in corps, chemin
    cout = rendre(contexte, "/cout", {})[1]
    # Le titre ne compte plus. Il disait « Dix » le 17 septembre et « Quatorze »
    # le 20 : chaque chantier de la page y ajoutait sa ligne, et le compteur
    # était devenu un aveu. Ce qui se règle est dit sous son réglage, ce qui
    # décrit un système dans le dépliant de ce système, et la liste ne garde
    # que ce que le lecteur ne peut ni changer ni lire ailleurs. Le plafond
    # oblige la prochaine réserve à en fusionner une plutôt que de s'ajouter.
    assert "<span>À lire avant de citer ces chiffres</span>" in cout
    assert "réserves à lire avant de citer" not in cout
    assert "Une page de chiffres vaut par ce qu'elle laisse de côté" in cout
    debut = cout.index("Une page de chiffres vaut par ce qu'elle laisse de côté")
    liste = cout[debut:cout.index("</ul>", debut)]
    assert 3 <= liste.count("<li><strong>") <= RESERVES_MAXIMUM, liste.count("<li><strong>")
    # Les réserves déplacées sont lues là où elles se règlent ou se décrivent.
    assert "La recette réagit sur quatre points" in cout[cout.index('id="cout-postes"'):]
    assert "Seul le système actuel sert la pension de" in cout[cout.index('id="cout-postes"'):]
    assert "sans toucher aux écarts entre carrières" in cout[cout.index('id="cout-equilibre"'):]
    simuler = rendre(contexte, "/simuler", {})[1]
    assert "où ce stock est éteint" in simuler



# -- action 13 : la certification datée série par série -------------------------


def test_la_page_donnees_ne_promet_que_la_plus_ancienne_verification(contexte):
    """« Recontrôlé le 16 septembre » était la date du dernier passage, fût-il
    partiel. La page dit désormais le MINIMUM des dates de fiche — la seule
    affirmation que le journal soutient —, et la table date chaque série."""
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.donnees.chargement import journal_certification

    journal = journal_certification(RACINE_DONNEES)
    dates = sorted(trace["verifiee_le"] for trace in journal["series"].values())
    corps = rendre(contexte, "/methode", {})[1]
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
    """Tant que rien n'est changé, la page est celle d'avant.

    CE QUE CE TEST GARDE, c'est qu'aucun RÉGLAGE ne voyage dans un lien que le
    lecteur n'a pas demandé : une adresse partagée ne doit porter que ce que
    son auteur a effectivement changé. Les VUES sont l'autre chose — l'année
    que la cascade de Coût décompose —, et celles-là voyagent par construction,
    puisqu'un sélecteur n'a pas d'autre façon de dire où il mène. La
    distinction est dans ``_VUES_DE_PAGE`` ; ici on vérifie qu'un lien ne porte
    rien D'AUTRE qu'une vue.
    """
    corps = page(chemin)
    assert "ne sont pas ceux des réglages par défaut" not in corps
    assert '<a href="#/cout"' in corps or '<a href="#/simuler"' in corps
    vues = {cle for cles in _VUES_DE_PAGE.values() for cle in cles}
    for requete in re.findall(r'<a href="#/[a-z-]+\?([^"]*)"', corps):
        portees = {couple.split("=")[0] for couple in requete.split("&")}
        assert portees <= vues, (
            f"{chemin} : un lien porte {portees - vues}, qui n'est pas une vue"
        )


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
    for rang, (brut, net) in enumerate(zip(en_brut, en_net)):
        assert net > brut, "le taux net doit dépasser le taux brut"
        # Le rapport des deux prélèvements : 0,909 de pension contre environ
        # 0,79 de salaire. Une fourchette large suffit — elle n'est pas là pour
        # valider un dixième de point, mais pour attraper un taux resté brut.
        # La proposition, quatrième ligne, se rapporte à SA fiche de paie, qui
        # prélève moins sur le même brut : son rapport est plus bas.
        bornes = (1.03, 1.12) if rang == 3 else (1.10, 1.20)
        assert bornes[0] < net / brut < bornes[1], f"{net} / {brut}"


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
              ("/", {}), ("/cout", {}), ("/methode", {}), ("/programme", {})]
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


def test_le_script_de_la_page_s_analyse():
    """Le script d'``index.html`` n'est chargé par aucun test dans un navigateur :
    une déclaration en double y a rendu le site blanc le 19 septembre 2026 sans
    qu'aucun test ne le dise. ``node --check`` le lit comme le navigateur le
    lira, et refuse ce qui ne s'analyse pas."""
    import subprocess
    import tempfile
    from pathlib import Path
    page = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
    script = re.search(r'<script type="module">(.*?)</script>', page, re.S).group(1)
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as fichier:
        fichier.write(script)
    resultat = subprocess.run(["node", "--check", fichier.name],
                              capture_output=True, text=True, encoding="utf-8")
    assert resultat.returncode == 0, resultat.stderr


def test_le_reglage_des_frais_du_pilier_voyage_avec_les_autres():
    """« frais=detail » se lit, s'applique aux paramètres et se réécrit dans
    l'adresse ; le défaut ne s'écrit pas."""
    from retraite_notionnelle.config import Parametres
    from retraite_notionnelle.web.pages import CLES_MODELISATION, Saisie

    assert "frais" in CLES_MODELISATION
    defaut = Saisie.depuis_requete({})
    assert defaut.frais == "paliers" and defaut.requete_modelisation() == ""
    saisie = Saisie.modelisation({"frais": "detail", "naissance": "1980-01"})
    assert saisie.frais == "detail" and not saisie.demandee
    parametres = saisie.parametres(Parametres())
    assert parametres.frais_arrerages_capitalisation == 0.0220
    assert parametres.frais_gestion_paliers == ()
    assert saisie.requete_modelisation() == "frais=detail"
    # Une valeur inconnue retombe sur le défaut, sans erreur.
    assert Saisie.depuis_requete({"frais": "gratuit"}).frais == "paliers"


def test_la_colonne_aspa_de_l_accueil_sert_le_bareme_de_l_aspa():
    """« Aujourd'hui (ASPA) » : ce que l'ASPA sert vraiment, sur ses deux barèmes
    lus — personne seule, couple d'allocataires —, et non les montants de la
    garantie appliqués au foyer, que la colonne recopiait jusqu'au
    23 septembre 2026. Le couple à 300 € et 300 € reçoit aujourd'hui 1 020 € et
    en recevrait 1 000 ; la personne seule à 300 €, 744 € contre 750."""
    from retraite_notionnelle.web import gabarit as g
    from retraite_notionnelle.web.pages import Contexte, FOYERS_GARANTIE, _tableau_garantie

    contexte = Contexte()
    annee = contexte.base.annee_euros_garantie_vieillesse
    minimum = contexte.simulateur().scenario_actuel.minimum_vieillesse
    seul = minimum.plafond(annee)[0] / 12
    couple = minimum.plafond_couple(annee)[0] / 12
    assert seul == pytest.approx(1043.59) and couple == pytest.approx(1620.18)
    rendu = _tableau_garantie(contexte)
    for foyer in FOYERS_GARANTIE:
        plafond = seul if len(foyer) == 1 else couple
        assert g.euros(max(0.0, plafond - sum(foyer))) in rendu, foyer
    assert g.euros(1020.18) in rendu and g.euros(743.59) in rendu

