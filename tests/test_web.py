"""Tests du contenu du site.

Le site tourne entièrement dans le navigateur, et son texte n'est écrit qu'une
fois, en JavaScript (``moteur/js/pages.js`` et ``gabarit.js``). Ces tests le
lisent là où il est, par :mod:`retraite_notionnelle.web.site` ; ce qu'ils
confrontent aux pages — la saisie, les simulations, les agrégats — vient du
modèle Python, qui fait foi.

Trois fichiers le testent : celui-ci, les pages, leur rendu et ce que le
site charge ; ``test_web_saisie.py``, la saisie ; ``test_web_revues.py``,
les revues du 15 septembre 2026 et ce qu'elles ont fait naître. Ce qu'ils
se partagent est dans ``outils_web.py``.
"""

from __future__ import annotations

import dataclasses
import html
import itertools
import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl

import pytest

from retraite_notionnelle import fabrique
from retraite_notionnelle.cout import COMPOSANTE_GARANTIE
from retraite_notionnelle.donnees.bilan import EcartsFiges
from retraite_notionnelle.donnees.chargement import (
    DonneeInsuffisante,
    charger_periodes_non_travaillees,
)
from retraite_notionnelle.saisie import (
    AGE_DEBUT_MINIMAL,
    AGE_LIQUIDATION_MAXIMAL,
    AGES_REFERENCE,
    ANNEE_CARRIERE_MAXIMALE,
    ANNEE_CARRIERE_MINIMALE,
    ANNEE_MAXIMALE,
    ANNEE_MINIMALE,
    ENFANTS_MAXIMUM,
    INDEXATIONS,
    LISSAGE_MAXIMUM,
    METIERS_MAXIMUM,
    PROFILS,
    PROJECTIONS,
    RELEVE_MAXIMUM,
    SANS_EMPLOI,
    POPULATIONS,
    RATTACHEMENTS,
    TABLES,
    ErreurSaisie,
    Saisie,
)
from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.web.site import disponible, module, rendre, site
from outils_web import (
    FEUILLE_DE_STYLE, SIMULATION_TEMOIN, TITRES, _hors_depliants, _sans_blocs, contexte,
    g, page, pages,
)


#: Le site, en JavaScript : ses pages et ses modules se lisent par node
#: (``web/site.py``), le Python ne les rendant plus depuis la phase 8. Sans
#: node, rien du site ne se lit, et ses tests sont sautés.
pytestmark = pytest.mark.skipif(not disponible(),
                                reason="node absent : le site ne se lit pas sans lui")


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
    formulaire demande depuis qu'il porte des calendriers : né en 1955 —
    présumé le 15 janvier, et la page le dit —, entré à dix-huit ans, en
    janvier 1973, parti à cinquante-cinq, au 1er février 2010 (R. 351-37).
    """
    texte = page("/simuler", naissance=1955, statut="mineur",
                 debut=18, liquidation=55)
    assert 'id="naissance" name="naissance" value="1955-01-15"' in texte
    assert "jour présumé" in texte
    assert 'id="debut" name="debut" value="1973-01-01"' in texte
    assert 'id="liquidation" name="liquidation" value="2010-02-01"' in texte
    assert '<option value="mineur" selected data-fermeture="2010-09">' in texte


def test_le_calendrier_se_lit_et_se_rend(page):
    """Une carrière datée au mois : le formulaire la rend telle qu'elle a été
    saisie, et l'âge qu'elle fait s'écrit sous le champ. Né le 15 mars 1962,
    on commence à travailler en septembre 1984 à 22 ans et 6 mois, et l'on a
    64 ans et 3 mois révolus au 1er juillet 2026 : un départ se compte du
    mois qui suit l'anniversaire (R. 351-37)."""
    texte = page("/simuler", naissance="1962-03-15", debut="1984-09",
                 liquidation="2026-07")
    assert 'id="naissance" name="naissance" value="1962-03-15"' in texte
    assert 'id="debut" name="debut" value="1984-09-01"' in texte
    assert 'id="liquidation" name="liquidation" value="2026-07-01"' in texte
    assert "soit 22 ans et 6 mois" in texte
    assert "soit 64 ans et 3 mois" in texte
    assert "jour présumé" not in texte


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


def test_statuts_proposes():
    donnees = pages.statuts(site().contexte)
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

    dates = {s["code"]: s for s in pages.statuts(site().contexte)}
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


# -- rendu -------------------------------------------------------------------


def test_les_nombres_sont_a_la_francaise():
    assert g.euros(1234567) == "1 234 567 €"
    assert g.pourcentage(-0.937, signe=True) == "-93,7 %"
    assert g.pourcentage(0.5, signe=True) == "+50,0 %"


def test_franciser_les_libelles_du_moteur():
    assert g.franciser("SR 17,542 € × taux 63.75%") == (
        "SR 17 542 € × taux 63,75 %"
    )


def test_l_echappement_protege_des_injections(page):
    texte = page("/simuler", interruptions="<script>alert(1)</script>")
    assert "<script>alert(1)</script>" not in texte
    assert "&lt;script&gt;" in texte


def test_cellule_teintee_selon_la_valeur():
    assert "background" in g.Cellule("-90 %", intensite=-0.9).style()
    assert g.Cellule("+0 %", intensite=0.0).style() == ""
    rendu = g.tableau(["a"], [[g.Cellule("x", intensite=-0.5)]], ["nombre"])
    assert "rgba(162, 71, 46" in rendu


# -- rendu commun aux deux modes ---------------------------------------------


@pytest.mark.parametrize("chemin", ["/", "/simuler", "/cas-types", "/methode"])
def test_rendre_produit_un_corps_pour_chaque_page(chemin):
    titre, corps = rendre(chemin)
    assert titre
    assert len(corps) > 500


@pytest.mark.parametrize("chemin", ["/simuler", "/cas-types", "/methode"])
def test_les_ages_rendus_ne_doublent_pas_leur_unite(chemin):
    """« 64 ans ans ».

    L'âge s'écrivait « 64 » et les appelants ajoutaient « ans ». Le jour où il
    s'est mis à s'écrire « 64 ans et 7 mois », l'unité s'est retrouvée en
    double sur chaque page — et aucun test ne pouvait le voir, puisque les deux
    portages étaient d'accord et que les témoins avaient été régénérés avec la
    faute. Celui-ci regarde le texte rendu.
    """
    import re

    _, corps = rendre(chemin, {
        "naissance": "1962", "naissance_mois": "3", "debut": "22",
        "liquidation": "64", "liquidation_mois": "7",
        "statut": "salarie_prive_non_cadre",
    })
    for faute in ("ans ans", "mois mois", "ans et ans"):
        assert faute not in corps, f"{faute!r} dans {chemin}"
    # Et l'âge s'y lit bien en ans et en mois.
    if chemin == "/simuler":
        assert re.search(r"64 ans et 7 mois", corps)


def test_rendre_ignore_un_chemin_inconnu():
    titre, _ = rendre("/n-importe-quoi")
    assert titre == "Programme"


def test_rendre_ne_leve_jamais_sur_une_saisie_invalide():
    _, corps = rendre("/simuler", {"naissance": "1700"})
    assert "Saisie refusée" in corps


def test_statuts():
    codes = {entree["code"] for entree in pages.statuts(site().contexte)}
    assert "salarie_prive_non_cadre" in codes


# -- liens -------------------------------------------------------------------


def test_les_liens_passent_par_l_ancre():
    """Sur GitHub Pages le site est servi dans un sous-chemin : pas de lien absolu."""
    _, corps = rendre("/simuler")
    entete = g.entete("/")
    assert 'href="#/cas-types"' in entete
    assert 'href="/cas-types"' not in entete
    assert 'action="#/simuler"' in corps


def test_aucun_renvoi_vers_un_service_qui_n_existe_pas():
    """Il n'y a pas de serveur : proposer une adresse d'API serait un lien mort."""
    _, corps = rendre("/simuler", {"naissance": "1960",
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


#: L'écart relatif que tolère, hors de Linux, la comparaison d'un fichier
#: fabriqué : la libm de Windows déplace la dernière décimale de quelques
#: flottants, de 7 · 10⁻¹⁴ au plus le 4 octobre 2026. Le portage, lui,
#: tolère 10⁻⁹ (``tests/js/comparer.mjs``).
TOLERANCE_HORS_LINUX = 1e-12


def _egaux_a_la_tolerance(ecrit, attendu, tolerance: float = TOLERANCE_HORS_LINUX) -> bool:
    """Deux JSON lus : mêmes clés, mêmes types, mêmes chaînes, et des
    flottants égaux à ``tolerance`` près, en écart relatif."""
    if type(ecrit) is not type(attendu):
        return False
    if isinstance(ecrit, float):
        return (math.isclose(ecrit, attendu, rel_tol=tolerance)
                or math.isnan(ecrit) and math.isnan(attendu))
    if isinstance(ecrit, dict):
        return ecrit.keys() == attendu.keys() and all(
            _egaux_a_la_tolerance(ecrit[cle], attendu[cle], tolerance) for cle in ecrit)
    if isinstance(ecrit, list):
        return len(ecrit) == len(attendu) and all(
            _egaux_a_la_tolerance(a, b, tolerance) for a, b in zip(ecrit, attendu))
    return ecrit == attendu


def _fichier_a_jour(chemin: Path, contenu: bytes, plateforme: str = sys.platform) -> bool:
    """Le fichier versionné est-il ce que le dépôt en fabrique ?

    Au bit près sous Linux, où la CI le fabrique et le compare. Ailleurs, ce
    que la CI a écrit ne se refait pas au bit près, et l'échec n'apprendrait
    rien qu'un vrai oubli ne dise pareil : un JSON qui n'en diffère qu'à la
    dernière décimale de ses flottants est à jour.
    """
    ecrit = chemin.read_bytes()
    if ecrit == contenu:
        return True
    if plateforme == "linux" or chemin.suffix != ".json":
        return False
    return _egaux_a_la_tolerance(json.loads(ecrit), json.loads(contenu))


def test_le_paquet_est_a_jour(contexte):
    """Le paquet et la feuille de style servis au site doivent refléter le dépôt.

    S'il échoue : ``python scripts/construire_donnees.py``. Au bit près sous
    Linux ; ailleurs, à la dernière décimale près (``_fichier_a_jour``).

    Le contexte du module est passé au constructeur, et ce n'est pas une
    élégance : depuis que le paquet embarque le bilan figé, le construire
    suppose le coût agrégé, soit dix-huit secondes. Les autres tests de ce
    module l'ont déjà calculé sous les mêmes réglages, et la mémoire du
    contexte est partagée.

    Juste après une régénération réussie, rien à refaire : l'empreinte de ce
    que le paquet lit et écrit n'a pas bougé (``fabrique.py`` ; GitHub, qui
    n'a pas de mémoire, refait tout).
    """
    if fabrique.a_jour("paquet"):
        pytest.skip("paquet inchangé depuis la dernière fabrication")
    construction = _construction()
    for chemin, contenu in construction.sorties(contexte).items():
        assert chemin.exists(), f"{chemin.name} est absent"
        assert _fichier_a_jour(chemin, contenu), (
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
    qui montre exactement quels montants le changement déplace. Juste après
    une régénération réussie, rien à refaire (``fabrique.py``). Au bit près
    sous Linux ; ailleurs, à la dernière décimale près (``_fichier_a_jour``).
    """
    if fabrique.a_jour("témoins"):
        pytest.skip("témoins inchangés depuis la dernière fabrication")
    import importlib.util
    from pathlib import Path

    chemin = Path(__file__).resolve().parents[1] / "scripts" / "construire_temoins.py"
    specification = importlib.util.spec_from_file_location("construire_temoins", chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)

    for fichier, contenu in module.construire().items():
        assert fichier.exists(), f"{fichier.name} est absent"
        assert _fichier_a_jour(fichier, contenu), (
            f"{fichier.name} est périmé — lancer python scripts/construire_temoins.py"
        )


def test_hors_de_linux_un_fichier_fabrique_se_compare_a_la_derniere_decimale_pres():
    """La comparaison des deux tests précédents, hors de Linux : un ulp passe ;
    un écart relatif de 10⁻⁹, ce que le portage tolère encore, échoue, comme
    toute clé, toute chaîne ou tout type qui change."""
    temoin = {"pension": 1234.56, "taux": [0.1, 0.2], "nom": "cas", "annees": 42}
    assert _egaux_a_la_tolerance(temoin, {**temoin, "pension": math.nextafter(1234.56, 2e3)})
    assert not _egaux_a_la_tolerance(temoin, {**temoin, "pension": 1234.56 * (1 + 1e-9)})
    assert not _egaux_a_la_tolerance(temoin, {**temoin, "decote": 0.0})
    assert not _egaux_a_la_tolerance(temoin, {c: v for c, v in temoin.items() if c != "nom"})
    assert not _egaux_a_la_tolerance(temoin, {**temoin, "nom": "autre cas"})
    assert not _egaux_a_la_tolerance(temoin, {**temoin, "annees": 42.0})
    assert not _egaux_a_la_tolerance(temoin, {**temoin, "taux": [0.1]})


def test_sous_linux_un_fichier_fabrique_se_compare_au_bit_pres(tmp_path):
    """La CI, sous Linux, ne tolère rien : un ulp y rend le fichier périmé.
    Ailleurs, seul un JSON se compare à la tolérance."""
    ecrit = json.dumps({"pension": 1234.56}).encode("utf-8")
    un_ulp = json.dumps({"pension": math.nextafter(1234.56, 2e3)}).encode("utf-8")
    temoin, texte = tmp_path / "temoin.json", tmp_path / "temoin.txt"
    temoin.write_bytes(ecrit)
    texte.write_bytes(ecrit)
    assert not _fichier_a_jour(temoin, un_ulp, "linux")
    assert _fichier_a_jour(temoin, un_ulp, "win32")
    assert not _fichier_a_jour(texte, un_ulp, "win32")


def test_une_adresse_d_avant_le_calendrier_et_ses_dates_font_les_memes_chiffres():
    """Les deux témoins de la carrière décalée : l'un écrit à l'ancienne — un
    âge, un mois, et pas de jour, présumé le 15 —, l'autre en dates, née le 15
    septembre 1975, entrée en décembre 1997 et partie au 1er mai 2040, au mois
    qui suit son anniversaire (R. 351-37). Ils décrivent la même carrière et
    portent les mêmes chiffres, au bit près : sans quoi tout lien partagé
    avant le calendrier mentirait."""
    import json

    chemin = Path(__file__).resolve().parent / "temoins" / "simulations.json"
    temoins = json.loads(chemin.read_text(encoding="utf-8"))
    ancienne = temoins["mois_carriere_decalee"]
    nouvelle = temoins["mois_carriere_decalee_au_calendrier"]
    assert (ancienne["requete"]["naissance"], ancienne["requete"]["naissance_mois"]) == (
        "1975", "9")
    assert nouvelle["requete"]["naissance"] == "1975-09-15"
    assert ancienne["resultat"] == nouvelle["resultat"]


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
def test_le_tableau_du_detail_s_additionne_a_l_ecran(nom, champs):
    """Ce que la page affirme du tableau doit se vérifier sur les nombres AFFICHÉS.

    Pas sur ceux du modèle : un lecteur additionne ce qu'il lit. Le contrôle
    porte donc sur le HTML rendu, lignes de régime d'un côté, total de l'autre,
    la ligne « hors total » exclue puisqu'elle s'annonce comme telle.
    """
    corps = rendre("/simuler", champs)[1]
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
              or re.search(r"<t[dh][^>]*>\+ ", ligne)
              # Une ligne en retrait détaille l'étage du dessus, dont la
              # ligne porte déjà la somme.
              or re.search(r'<t[dh][^>]*><span class="dont">', ligne)):
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


def _systeme_actuel(champs: dict[str, str]) -> tuple[int, str]:
    """Le montant du système 1, tel qu'il s'affiche, et la ligne qui le compose."""
    corps = rendre("/simuler", champs)[1]
    bloc = _bloc(corps, '<div class="scenario">', '<div class="barre actuel">')
    montant = re.search(r'<span class="chiffre principal">.*?'
                        r'<span class="somme">([^<]+)</span>', bloc, re.S).group(1)
    composition = bloc.partition('<span class="composition">')[2]
    ligne = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", composition)))
    return int(re.sub(r"\D", "", montant)), ligne.strip()


@pytest.mark.parametrize("nom,champs,libelles", [
    ("cadre", {"naissance": "1962", "statut": "salarie_prive_cadre", "debut": "22",
               "liquidation": "64", "unite_revenu": "moyen", "salaire": "1.6"},
     ["retraite de base", "retraite complémentaire"]),
    # Trois étages : l'ASV des médecins conventionnés s'ajoute aux deux autres.
    ("médecin", {"naissance": "1965", "statut": "medecin_liberal", "debut": "28",
                 "liquidation": "66", "unite_revenu": "moyen", "salaire": "2"},
     ["retraite de base", "retraite complémentaire", "retraite additionnelle"]),
    # Déjà parti : les montants sont ceux d'aujourd'hui, chaque régime
    # revalorisé par sa règle, et la majoration pour enfants avec eux.
    ("retraité, deux enfants", {"naissance": "1945", "statut": "salarie_prive_cadre",
                                "debut": "20", "liquidation": "60", "enfants": "2",
                                "unite_revenu": "moyen", "salaire": "1.5"},
     ["retraite de base", "retraite complémentaire"]),
    # Le minimum vieillesse, qu'aucun régime ne sert : un terme à part.
    ("petite pension, minimum vieillesse",
     {"naissance": "1950", "sexe": "F", "debut": "30", "liquidation": "65",
      "unite_revenu": "moyen", "salaire": "0.15"},
     ["retraite de base", "retraite complémentaire", "minimum vieillesse"]),
])
def test_le_systeme_actuel_dit_sa_base_et_ses_complementaires(nom, champs, libelles):
    """Sous le montant du système 1, ce qu'il additionne : la retraite de base,
    puis ce qui s'y ajoute. Les parts sont arrondies à l'euro, et font le
    montant affiché : un lecteur les additionne de tête."""
    montant, ligne = _systeme_actuel(champs)
    termes = re.findall(r"(\d[\d   ]*) ?€ de ([^+]+?)(?: \+|$)", ligne)
    assert [libelle.strip() for _, libelle in termes] == [
        f"{libelle}" for libelle in libelles], f"{nom} : {ligne}"
    parts = [int(re.sub(r"\D", "", euros)) for euros, _ in termes]
    assert sum(parts) == montant, f"{nom} : {ligne} ne fait pas {montant} €"


def test_un_regime_integre_se_dit_d_une_seule_pension():
    """Un agent de la SNCF n'a pas de complémentaire : son régime tient les
    deux rôles, et la ligne le dit au lieu de ne rien écrire."""
    montant, ligne = _systeme_actuel({"naissance": "1960", "statut": "agent_sncf",
                                      "liquidation": "57"})
    assert montant > 0
    assert ligne.startswith("une seule pension, sans complémentaire à part"), ligne
    assert "€" not in ligne


def test_le_detail_range_la_base_avant_les_complementaires():
    """Le moteur rend les régimes dans l'ordre alphabétique de leurs codes,
    l'Agirc avant le régime général. Le détail les range par étage — la base,
    puis les complémentaires, chacune en retrait sous leur somme —, et la
    somme est celle des lignes affichées."""
    corps = rendre("/simuler", {"naissance": "1962", "statut": "salarie_prive_cadre",
                                "debut": "22", "liquidation": "64",
                                "unite_revenu": "moyen", "salaire": "1.6"})[1]
    tableau = _bloc(corps, "de quoi votre pension actuelle est faite", "</table>")
    ordre = ["Retraite de base", "Régime général", "Retraite complémentaire",
             "Association générale des institutions de retraite des cadres",
             "Association pour le régime de retraite complémentaire des salariés",
             "Régime unifié Agirc-Arrco", "<strong>Pension du système actuel"]
    rangs = [tableau.index(texte) for texte in ordre]
    assert rangs == sorted(rangs)
    complementaires = _nombres(_bloc(tableau, "Retraite complémentaire",
                                     "Pension du système actuel"))
    somme, *lignes = complementaires
    assert len(lignes) == 3 and round(sum(lignes), 2) == somme


def _euros(texte: str) -> list[int]:
    """Les montants à l'euro d'un texte, dans l'ordre où ils s'y lisent."""
    return [int(re.sub(r"\D", "", euros))
            for euros in re.findall(r"(\d[\d   ]*) ?€", texte)]


@pytest.mark.parametrize("nom,champs", [
    ("carrière ordinaire", {"naissance": "1975"}),
    ("cadre", {"naissance": "1962", "statut": "salarie_prive_cadre", "debut": "22",
               "liquidation": "64", "unite_revenu": "moyen", "salaire": "1.6"}),
    ("petit salaire", {"naissance": "1980", "unite_revenu": "moyen", "salaire": "0.6"}),
    ("haut salaire", {"naissance": "1985", "statut": "salarie_prive_cadre",
                      "unite_revenu": "moyen", "salaire": "3.2"}),
    ("fonctionnaire", {"naissance": "1975", "sexe": "F", "statut": "fonctionnaire_etat",
                       "debut": "22", "liquidation": "64", "primes": "0.2"}),
    ("médecin", {"naissance": "1965", "statut": "medecin_liberal", "debut": "28",
                 "liquidation": "66", "unite_revenu": "moyen", "salaire": "2"}),
    ("montants bruts", {"naissance": "1990", "montants": "brut",
                        "unite_revenu": "moyen", "salaire": "1.3"}),
])
def test_la_ligne_de_la_proposition_fait_ses_montants(nom, champs):
    """Sous le montant de la proposition, la répartition et la rente
    obligatoire font le plancher « sans rien ajouter », et le plancher plus la
    rente volontaire fait le montant affiché : à l'euro, comme un lecteur les
    additionne. Arrondis un à un, 2 316 + 10 + 10 y faisaient 2 336 € sous
    « jusqu'à 2 337 ». Le plancher est aussi celui que le résumé écrit en tête
    de page."""
    corps = rendre("/simuler", champs)[1]
    bloc = _bloc(corps, '<span class="titre">4. La proposition',
                 '<div class="barre liberal">')
    montant = int(re.sub(r"\D", "", re.search(
        r'<span class="chiffre principal">.*?<span class="somme">([^<]+)</span>',
        bloc, re.S).group(1)))
    ligne = html.unescape(re.sub(r"\s+", " ", re.sub(
        r"<[^>]+>", " ", bloc.partition('<span class="composition">')[2])))
    repartition, obligatoire, plancher, volontaire = _euros(ligne)
    assert repartition + obligatoire == plancher, f"{nom} : {ligne}"
    assert plancher + volontaire == montant, f"{nom} : {ligne} sous {montant} €"
    resume = _bloc(corps, "Avec notre proposition", "</p>")
    assert _euros(resume)[:2] == [plancher, montant], f"{nom} : {resume}"


def _centimes(cellule: str) -> float | None:
    """Le montant d'une case, au centime ; ``None`` pour un tiret."""
    montant = re.search(r"([\d ]+,\d{2}) €", cellule)
    if montant is None:
        assert "—" in cellule, cellule
        return None
    return float(montant.group(1).replace(" ", "").replace(",", "."))


@pytest.mark.parametrize("nom,champs", [
    # Le système 4 y part un an plus tard, et le régime unique a sa ligne.
    ("carrière ordinaire", {"naissance": "1975"}),
    ("cadre", {"naissance": "1962", "statut": "salarie_prive_cadre", "debut": "22",
               "liquidation": "64", "unite_revenu": "moyen", "salaire": "1.6"}),
    ("fonctionnaire, rente RAFP",
     {"naissance": "1960", "statut": "fonctionnaire_etat", "primes": "0.2"}),
    ("mère de trois enfants", {"naissance": "1968", "sexe": "F", "enfants": "3"}),
    ("médecin, trois étages", {"naissance": "1965", "statut": "medecin_liberal",
                               "debut": "28", "liquidation": "66",
                               "unite_revenu": "moyen", "salaire": "2"}),
    ("petite pension, minimum vieillesse et garantie",
     {"naissance": "1950", "sexe": "F", "debut": "30", "liquidation": "65",
      "unite_revenu": "moyen", "salaire": "0.15"}),
])
def test_le_tableau_par_origine_s_additionne_colonne_par_colonne(nom, champs):
    """Les quatre systèmes, régime par régime : chaque colonne fait son total
    sur les montants AFFICHÉS, à un demi-centime près par ligne, comme le
    tableau du système 1 ; l'étage de plusieurs régimes fait, lui, au centime,
    la somme des lignes qui le suivent. Les totaux sont ceux que la page écrit
    ailleurs — la pension du système 1, celle de la chaîne du système 2 — et,
    pour le système 4, celle du modèle ramenée aux euros du même départ."""
    corps = rendre("/simuler", champs)[1]
    debut = corps.index("Les quatre systèmes, régime par régime, en euros de")
    tableau = corps[debut:corps.index("</table>", debut)]
    lignes = []
    for ligne in re.findall(r"<tr>(.*?)</tr>", tableau, re.S)[1:]:
        cellules = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", ligne, re.S)
        lignes.append((cellules[0], [_centimes(c) for c in cellules[1:]]))
    *detail, (libelle_total, totaux) = lignes
    assert "Pension de répartition" in libelle_total, nom

    retrait = '<span class="dont">'
    feuilles = []
    for rang, (libelle, montants) in enumerate(detail):
        suivantes = []
        for autre, autres in detail[rang + 1:]:
            if not autre.startswith(retrait):
                break
            suivantes.append(autres)
        if suivantes and not libelle.startswith(retrait):
            for colonne, montant in enumerate(montants):
                presents = [s[colonne] for s in suivantes if s[colonne] is not None]
                assert montant == (round(sum(presents), 2) if presents else None), (
                    f"{nom} : {libelle}, colonne {colonne + 1}")
        else:
            feuilles.append(montants)
    for colonne, total in enumerate(totaux):
        presents = [f[colonne] for f in feuilles if f[colonne] is not None]
        assert sum(presents) == pytest.approx(
            total, abs=0.005 * len(presents) + 0.005), f"{nom} : système {colonne + 1}"

    systeme1 = _bloc(corps, "de quoi votre pension actuelle est faite", "</table>")
    assert totaux[0] == _centimes(_bloc(systeme1, "<strong>Pension du système actuel",
                                        "</tr>")), nom
    chaine = _bloc(corps, "Construction du compte notionnel rétroactif", "</table>")
    assert totaux[1] == _nombres(_bloc(chaine, "Pension annuelle, en euros de",
                                       "</tr>"))[-1], nom
    resultat = Contexte().simuler(Saisie.depuis_requete(champs)).dictionnaire()
    liberal = resultat["scenarios"]["notionnel_liberal"]["pension_annuelle"]
    ramene = (liberal * resultat["liquidation_liberal"]["coefficient_euros_constants"]
              / resultat["unite"]["coefficient"])
    assert totaux[3] == round(ramene, 2), nom
    if champs.get("statut") == "fonctionnaire_etat":
        assert "Hors tableau : Retraite additionnelle de la fonction publique" in corps


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
def test_les_chaines_de_calcul_se_refont_depuis_l_ecran(nom, champs):
    """Chaque ligne d'une chaîne doit se retrouver depuis celles du dessus.

    C'est ce que la page promet : « la chaîne de calcul est arithmétique ». Le
    contrôle porte donc sur les nombres AFFICHÉS, coefficients compris — un
    coefficient trop court rend la chaîne infaisable même quand le modèle a
    raison. Les bornes ne sont pas choisies : elles se déduisent des précisions
    d'affichage, et suivront si celles-ci changent.
    """
    corps = rendre("/simuler", champs)[1]
    pas_diviseur = 0.5 * 10 ** -pages.DECIMALES_DIVISEUR
    pas_facteur = 0.5 * 10 ** -pages.DECIMALES_FACTEUR

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


def test_le_salaire_net_des_cartes_est_celui_de_la_fiche_de_paie():
    """Le même nombre est écrit à deux endroits : il doit y être le même.

    Ce test remplace celui qui vérifiait « mensuel × 12 = annuel » sur chaque
    carte. Le total annuel a quitté l'affichage — une pension se pense au mois,
    comme un salaire —, et avec lui le recoupement qu'il permettait. Le salaire
    net en offre un autre, et meilleur : il est écrit une fois en tête de
    chaque carte, et une seconde fois dans la fiche de paie repliée. Deux
    chemins de calcul, deux rendus, un seul nombre attendu. En net, demandé :
    le brut est le défaut depuis le 4 octobre 2026, et la carte dit alors le
    salaire brut.
    """
    corps = rendre("/simuler", {**SIMULATION_TEMOIN, "montants": "net"})[1]
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


def test_les_colonnes_derivees_de_la_page_cout_se_refont():
    """Écarts et économies de la page Coût, reconstitués depuis les cumuls affichés.

    Ces colonnes ne sont pas des mesures : ce sont des différences et des
    rapports entre deux nombres de la même ligne ou de la ligne de référence.
    Elles doivent donc se retrouver, aux arrondis d'affichage près.
    """
    corps = rendre("/cout", {})[1]
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

    def fraction_des_cultes() -> float:
        """La fraction d'avant 1998 du régime des cultes : le maximum au prorata
        de la durée, décoté ou surcoté, et ses majorations au minimum
        contributif."""
        trouve = re.search(r"avant 1998, maximum ([\d,]+\.\d+) € × (\d+)/(\d+)"
                           r"(?: × (?:décote|surcote) ([\d.]+))?([^=]*)=", detail)
        if not trouve:
            return 0.0
        maximum, retenus, duree, coefficient, majorations = trouve.groups()
        return (sans_virgules(maximum) * int(retenus) / int(duree) * float(coefficient or 1.0)
                + sum(sans_virgules(m) for m in re.findall(r"\+ ([\d,]+\.\d+) € pour",
                                                            majorations)))

    if detail.startswith("avant 1998, maximum"):
        return fraction_des_cultes()
    annuites = re.match(r"(?:SR|forfait) ([\d,]+\.\d+) € × taux ([\d.]+)% × (\d+)/(\d+)",
                        detail)
    if annuites:
        reference, taux, acquis, requis = annuites.groups()
        montant = sans_virgules(reference) * float(taux) / 100 * int(acquis) / int(requis)
        # Le taux maximum atteint : les bonifications de L. 12 portent le
        # pourcentage de 75 à 80 %, et le prorata s'y arrête — à 80/75 dans les
        # trois régimes du code des pensions, dont le taux plein est de 75 %.
        maximum = re.search(r"taux maximum (\d+)% atteint", detail)
        if maximum:
            montant = min(montant, sans_virgules(reference) * float(taux) / 100
                          * int(maximum.group(1)) / 75)
        surcote = re.search(r"surcote parentale ([\d.]+)%", detail)
        if surcote:
            montant *= 1 + float(surcote.group(1)) / 100
        # Les deux planchers disent de combien ils relèvent la pension.
        plancher = re.search(
            r"porté au minimum (?:contributif|garanti) par \+ ([\d,]+\.\d+) €", detail)
        return (montant + fraction_des_cultes()
                + (sans_virgules(plancher.group(1)) if plancher else 0.0))

    # La pension agricole que borne la moitié du plafond (L. 732-24, III) :
    # le plafond, et la surcote qui le majore.
    plafond = re.match(r"moitié du plafond ([\d,]+\.\d+) €"
                       r"(?: × coefficient de majoration ([\d.]+))?", detail)
    if plafond:
        return sans_virgules(plafond.group(1)) * float(plafond.group(2) or 1.0)

    points = re.search(r"([\d,]+\.\d+) points × valeur de service ([\d.]+)", detail)
    # La part des non-salariés agricoles depuis 2026 qui se calcule sur le
    # revenu annuel moyen des années depuis 2016 : revenu × taux × durée.
    revenu = re.search(
        r"revenu annuel moyen ([\d,]+\.\d+) € × taux ([\d.]+)% × (\d+)/(\d+)", detail)
    if not points and not revenu:
        return None
    montant = 0.0
    if points:
        montant = sans_virgules(points.group(1)) * float(points.group(2))
        # Coefficient de durée de la proportionnelle agricole : « 37,5 /
        # durée requise », affiché à la suite de la valeur de service parce
        # qu'il ne multiplie que les points, ni le forfait ni les cotisations.
        duree = re.search(
            r"points × valeur de service [\d.]+ € × ([\d.]+)", detail)
        if duree:
            montant *= float(duree.group(1))
    if revenu:
        montant += (sans_virgules(revenu.group(1)) * float(revenu.group(2)) / 100
                    * int(revenu.group(3)) / int(revenu.group(4)))
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
    # Les deux minima des exploitants disent ce qu'ils ajoutent : la pension
    # majorée de référence en euros, le complément de la RCO en points, à la
    # valeur de service de la formule.
    majoree = re.search(
        r"porté à la pension majorée de référence par \+ ([\d,]+\.\d+) €", detail)
    if majoree:
        montant += sans_virgules(majoree.group(1))
    differentiel = re.search(r"complément différentiel de ([\d,]+) points", detail)
    if differentiel and points:
        montant += sans_virgules(differentiel.group(1)) * float(points.group(2))
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
    for statut in [affiliation["code"] for affiliation in pages.statuts(site().contexte)]:
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
                                 "coefficient de majoration", "surcote parentale",
                                 "pension majorée de référence",
                                 "complément différentiel"):
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
                             "coefficient de majoration", "surcote parentale",
                             "pension majorée de référence", "complément différentiel"):
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
                        "coefficient de majoration", "surcote parentale",
                        "pension majorée de référence", "complément différentiel"}, (
        f"branches non exercées : {branches}"
    )


def test_les_selecteurs_du_resume_vocal_existent_dans_le_html():
    """Le résumé lu par les synthèses vocales vise des classes du HTML rendu.

    Elles vivent dans deux fichiers que rien ne relie : le sélecteur est écrit
    dans ``index.html``, la classe dans ``moteur/js/pages.js``. « .mensuel » y a été visé
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
                                   rendre("/simuler", champs)[1]):
            classes.update(attribut.split())
    for selecteur in selecteurs:
        for classe in re.findall(r"\.([a-z-]+)", selecteur):
            assert classe in classes, (
                f"« {selecteur} » vise « .{classe} », absent du HTML rendu"
            )


def test_le_resume_vocal_annonce_bien_les_montants():
    """Et le sélecteur doit trouver quelque chose, pas seulement exister.

    L'étiquette compte autant que le montant : le système 4 annonce
    « retraite jusqu'à », et `resume()` dans ``index.html`` reprend ce qui
    suit le mot « retraite » pour que l'annonce vocale dise le plafond comme
    un plafond. Un scénario dont l'étiquette ne commencerait plus par
    « retraite » ferait dire à l'oreille autre chose qu'à l'œil.
    """
    corps = rendre("/simuler", {"naissance": "1975"})[1]
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


def _refus_du_modele(contexte, requete: dict) -> str | None:
    """Ce que le modèle Python refuse de cette saisie, ou ``None`` s'il la calcule."""
    try:
        contexte.simuler(Saisie.depuis_requete(requete))
    except ErreurSaisie as erreur:
        return str(erreur)
    return None


def _refus_de_la_page(corps: str) -> str | None:
    """Le refus que la page écrit, ou ``None`` si elle calcule."""
    trouve = re.search(r'<div class="erreur"><strong>Saisie refusée\.</strong> (.*?)</div>',
                       corps, re.S)
    return html.unescape(trouve.group(1)) if trouve else None


#: Ce qu'un rendu ne doit jamais laisser passer : un nombre que le calcul n'a
#: pas su écrire, une valeur absente, un objet écrit tel quel.
TROUS = ("NaN", "undefined", "Infinity", "[object Object]")


def test_les_pages_au_hasard_calculent_et_refusent_comme_le_modele(contexte):
    """Des saisies auxquelles personne n'a pensé, dans les deux unités et
    jusqu'à leurs bords.

    Jusqu'à la phase 8, ce test comparait ces pages, caractère par caractère, à
    celles que rendait le Python — le texte du site était écrit deux fois. Il
    ne l'est plus qu'en JavaScript ; ce qui reste à confronter, ce sont les
    deux moteurs. Une saisie que le modèle refuse, la page la refuse du même
    mot ; une saisie qu'il calcule, la page la rend sans trou — ni ``NaN``, ni
    ``undefined``, ni ``Infinity``. La comparaison des seuls résultats
    (``tests/js/comparer.mjs``) ne voit ni les libellés, ni les aides chiffrées,
    ni le lien de bascule d'unité : c'est là que ces trous se logeraient.
    """
    import random

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

    requetes = []
    for _ in range(40):
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
        requetes.append(requete)

    # LA SAISIE PAR LA PENSION A SA PROPRE SÉRIE, et elle est plus courte parce
    # qu'elle coûte vingt fois plus cher : chacune de ces pages inverse le
    # scénario 1 par une dichotomie de dix-huit coupes. C'est la seule boucle
    # du site dont le résultat dépend de l'ordre des opérations flottantes —
    # une différence d'un ulp sur une comparaison et les deux moteurs prennent
    # des branches différentes —, et c'est donc celle qu'il faut le plus
    # sûrement comparer sur des carrières auxquelles personne n'a pensé. Les
    # montants tirés balaient les trois refus autant que les inversions qui
    # aboutissent.
    for _ in range(12):
        debut = alea.randint(14, 30)
        requetes.append({
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
        })

    for requete in requetes:
        corps = re.sub(r'(<pre class="json">).*?(</pre>)', r"\1\2",
                       rendre("/simuler", requete)[1], flags=re.S)
        assert _refus_de_la_page(corps) == _refus_du_modele(contexte, requete), requete
        for trou in TROUS:
            assert trou not in corps, (trou, requete)


def test_les_refus_de_saisie_disent_le_mot_du_modele(contexte):
    """Un refus est une page comme une autre, et le modèle en dit le mot.

    Le tirage au hasard de la page précédente ne produit guère que des
    carrières valides : il ne dirait rien des phrases que le simulateur écrit
    quand il refuse. Ce sont pourtant elles que le lecteur lit le plus
    souvent, et elles citent des bornes — années, motifs, âges — que les deux
    moteurs pourraient écrire autrement sans qu'aucun chiffre ne bouge. La
    saisie se lit dans les deux langages : le refus de la page doit être
    celui du modèle, mot pour mot.
    """
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
        # L'invalidité et l'inaptitude (docs/architecture.md, § 11) : un champ
        # orphelin, une réponse qui n'en est pas une, une date hors de la
        # carrière, un taux hors de ses bornes, une radiation qui ne clôt
        # aucun emploi de fonctionnaire civil, ou que la carrière ne suit pas.
        {"taux_invalidite": "50"},
        {"inaptitude": "peut-etre"},
        {"invalidite": "1980-01"},
        {"radiation_invalidite": "2010-01", "taux_invalidite": "150"},
        {"radiation_invalidite": "2010-01"},
        {"statut": "fonctionnaire_etat", "radiation_invalidite": "2010-01"},
        # L'invalidité du conjoint : sans conjoint, illisible, avant sa naissance.
        {"conjoint_invalidite": "2024-02"},
        {"conjoint": "1962", "conjoint_invalidite": "2024-13"},
        {"conjoint": "1962", "conjoint_invalidite": "1961-12"},
        # Sa propre retraite : sans conjoint, illisible, avant sa naissance.
        {"conjoint_retraite": "2024-02"},
        {"conjoint": "1962", "conjoint_retraite": "2024-13"},
        {"conjoint": "1962", "conjoint_retraite": "1961-12"},
        # Son ménage et ses revenus d'activité : sans conjoint, une union que la
        # saisie ne connaît pas, des revenus d'activité au-delà de ses
        # ressources, les ressources d'un nouveau conjoint sans union.
        {"nouvelle_union": "pacs"},
        {"conjoint": "1962", "nouvelle_union": "veuvage"},
        {"conjoint": "1962", "ressources_conjoint": "4000", "activite_conjoint": "4100"},
        {"conjoint": "1962", "ressources_nouveau_conjoint": "5000"},
        # Les carrières hors de France (docs/architecture.md, § 11) : une ligne
        # incomplète, une activité ou un État que la saisie ne connaît pas, la
        # France, des dates hors de la carrière ou qui se chevauchent, une
        # pension sans montant, un État absent du tableau des accords.
        {"etranger1_pays": "DE"},
        {"etranger1_pays": "DE", "etranger1_debut": "1990-01", "etranger1_fin": "1992-01",
         "etranger1_activite": "independante"},
        {"etranger1_pays": "FR", "etranger1_debut": "1990-01", "etranger1_fin": "1992-01"},
        {"etranger1_pays": "Maroc", "etranger1_debut": "1990-01", "etranger1_fin": "1992-01"},
        {"etranger1_pays": "DE", "etranger1_debut": "1988-01", "etranger1_fin": "1992-01"},
        {"etranger1_pays": "DE", "etranger1_debut": "2035-01", "etranger1_fin": "2042-01"},
        {"etranger1_pays": "DE", "etranger1_debut": "1995-01", "etranger1_fin": "1999-01",
         "etranger2_pays": "AT", "etranger2_debut": "1998-12", "etranger2_fin": "2001-01"},
        {"pension_etrangere1_pays": "DE", "pension_etrangere1_debut": "2040-01"},
        {"pension_etrangere1_pays": "DE", "pension_etrangere1": "300",
         "pension_etrangere1_debut": "2051-01"},
        {"etranger1_pays": "ZZ", "etranger1_debut": "1995-01", "etranger1_fin": "1999-01"},
        {"residence": "OI"},
    ]
    # Les voisines immédiates de ces refus, qui doivent au contraire calculer :
    # une borne posée d'un cran trop loin se verrait ici, et nulle part ailleurs.
    acceptees = [
        {"interruptions": "1995:1999:education_enfant"},
        {"interruptions": f"{ANNEE_CARRIERE_MINIMALE}:1990:sans_activite"},
        {"unite_revenu": "euros_mois", "salaire": "1e3"},
        {"enfants": str(ENFANTS_MAXIMUM)},
        {"inaptitude": "oui"},
        {"invalidite": "2020-03"},
        {"statut": "fonctionnaire_etat", "radiation_invalidite": "2010-01",
         "metier2_debut": "2010-01", "metier2_statut": "sans_activite"},
        {"statut": "fonctionnaire_etat", "radiation_invalidite": "2010-06",
         "invalidite_imputable": "oui", "taux_invalidite": "60",
         "metier2_debut": "2010-06", "metier2_statut": "salarie_prive_non_cadre"},
        {"conjoint": "1962", "conjoint_invalidite": "1962-02"},
        {"conjoint": "1962", "conjoint_retraite": "1962-02"},
        {"conjoint": "1962", "ressources_conjoint": "4000", "activite_conjoint": "4000",
         "nouvelle_union": "concubinage", "ressources_nouveau_conjoint": "0"},
        {"etranger1_pays": "DE", "etranger1_debut": "1989-01", "etranger1_fin": "1992-01",
         "etranger1_activite": "non_salariee", "pension_etrangere1_pays": "DE",
         "pension_etrangere1": "300", "pension_etrangere1_debut": "2050-01",
         "residence": "PT"},
        {"etranger1_pays": "autre", "etranger1_debut": "1995-01", "etranger1_fin": "1999-01",
         "etranger2_pays": "OI", "etranger2_debut": "1999-01", "etranger2_fin": "2001-01"},
    ]

    for champs_, refuse in ((refuses, True), (acceptees, False)):
        for champs in champs_:
            requete = {"naissance": "1975", **champs}
            page = _refus_de_la_page(rendre("/simuler", requete)[1])
            modele = _refus_du_modele(contexte, requete)
            # Le test ne vaut que si chaque saisie tombe du côté attendu : une
            # borne relâchée les ferait toutes calculer, et la comparaison
            # passerait sans rien couvrir.
            assert (page is not None) is refuse, (
                f"{requete} : le simulateur "
                + ("calcule au lieu de refuser" if refuse else "refuse au lieu de calculer"))
            assert page == modele, requete


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
    feuille = FEUILLE_DE_STYLE
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
        r'<link rel="modulepreload" href="moteur/js/([\w./-]+\.js)">', page))
    a_la_demande = set(re.findall(
        r'import\(\s*"\./moteur/js/([\w./-]+\.js)"\s*\)', page))
    # Les étapes du droit ont leur dossier, moteur/js/droit/ : elles sont du
    # graphe comme les autres modules.
    dossier = racine / "moteur" / "js"
    presents = {chemin.relative_to(dossier).as_posix() for chemin in dossier.rglob("*.js")}

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
        "pages.js", "saisie.js", "contexte.js", "restitution.js",
    }
    assert attendus <= modules, f"manquant : {attendus - modules}"

    #: Le portage ne tire aucune bibliothèque : il ne doit rien importer
    #: d'autre que lui-même — un module de moteur/js/droit/ remonte d'un cran,
    #: sans sortir du dossier.
    dossier = (moteur / "js").resolve()
    for chemin in dossier.rglob("*.js"):
        for ligne in chemin.read_text(encoding="utf-8").splitlines():
            if ligne.startswith("import ") and " from " in ligne:
                origine = ligne.rsplit(" from ", 1)[1].strip(' ;"')
                cible = (chemin.parent / origine).resolve()
                assert origine.startswith(("./", "../")) and dossier in cible.parents, (
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
    ecran = FEUILLE_DE_STYLE.split("@media print")[0]
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
    bloc = FEUILLE_DE_STYLE.split("@media (prefers-reduced-motion: reduce)")
    assert len(bloc) == 2, "la feuille ne tient pas compte du mouvement réduit"
    assert "animation-iteration-count: 1 !important" in bloc[1], (
        "une animation qui boucle doit cesser de boucler"
    )


@pytest.mark.parametrize("chemin", list(TITRES))
def test_chaque_tableau_porte_un_titre_et_des_en_tetes_de_ligne(chemin):
    """Un tableau sans titre s'annonce « tableau, 7 colonnes, 12 lignes ».

    Et sans en-tête de ligne, une cellule lue au hasard n'est rattachée à rien :
    la synthèse vocale énonce « moins 31 % » sans dire de quel cas type ni de
    quelle génération. RGAA 4.1, critères 5.4 et 5.7.
    """
    corps = rendre(chemin, {})[1]
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
def test_toute_zone_defilante_est_atteignable_au_clavier(chemin):
    """Une boîte qui défile sans être focusable est hors d'atteinte au clavier.

    Les moteurs ne s'accordent pas sur ce point — Firefox rend focusables les
    boîtes défilantes, les autres non —, et un tableau plus large que l'écran
    devient alors impossible à parcourir sans souris. WCAG 2.1.1.
    """
    corps = rendre(chemin, {})[1]
    for ouverture in re.findall(r'<div class="defilant"[^>]*>', corps):
        assert 'tabindex="0"' in ouverture, (
            f"{chemin} : zone défilante inatteignable au clavier — {ouverture}"
        )


@pytest.mark.parametrize("chemin", list(TITRES))
def test_aucune_information_ne_vit_dans_une_infobulle(chemin):
    """``title`` ne s'ouvre ni au clavier, ni au doigt, ni sous synthèse vocale.

    Les gloses des douze cas types et des huit systèmes y ont vécu : elles sont
    désormais en clair, sous le tableau qu'elles expliquent.
    """
    corps = rendre(chemin, {})[1]
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


def test_le_simulateur_tient_en_peu_de_mots():
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
    # Le 28 septembre 2026, elle monte de trois mots pour un contrôle : le
    # dépliant « Conjoint et réversion », qui ouvre les champs du conjoint (le
    # domaine de la réversion), et dont les champs restent repliés.
    # Le 30 septembre 2026, elle monte de quatre mots pour un contrôle : le
    # dépliant « Retraite progressive et cumul emploi-retraite » (le domaine
    # des départs multiples), dont les champs restent repliés eux aussi. Le
    # même jour, deux de plus : le titre dit aussi « dates des pensions », les
    # champs où l'assuré date chaque pension, repliés avec les autres.
    # Le 1er octobre 2026, elle monte de trois mots pour un contrôle : le
    # dépliant « Invalidité et inaptitude » (le domaine de l'invalidité et de
    # l'inaptitude), dont les champs restent repliés. Le même jour, de quatre :
    # le dépliant « Carrière hors de France » (le domaine des carrières hors de
    # France), replié lui aussi.
    # Le 4 octobre 2026, elle monte de deux mots pour un contrôle : la
    # bascule des montants dit « net avant impôt », le mot d'Info-retraite.
    # Le 8 octobre 2026, de deux encore : le dépliant de l'invalidité dit
    # aussi « taux plein », les champs de l'ancien déporté, de l'ancien
    # combattant et du travail manuel (L. 351-8, 3° à 5°), repliés avec eux.
    vierge = rendre("/simuler", {})[1]
    assert _mots_visibles(vierge) <= 182, "le formulaire reprend de la prose"

    resultats = rendre("/simuler", {
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
    corps = rendre("/simuler", {})[1]
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


def test_le_lien_d_evitement_ouvre_chaque_page():
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


def test_le_site_ne_porte_aucune_mention_legale():
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
        (chemin, rendre(chemin, {})[1]) for chemin in TITRES
    ]
    for ou, corps in pages:
        for interdit in interdits:
            assert interdit not in corps, f"{interdit!r} est revenu sur {ou}"


def test_la_page_des_donnees_dit_sous_quelle_licence_reprendre():
    """Ce que l'hôte ne peut pas porter à la place du dépôt : ses licences.

    Une mention légale se délègue à l'éditeur du site d'accueil ; la licence
    du code, celle des infographies et l'obligation de citer le producteur
    d'une série, non — elles portent sur ce fichier-ci.
    """
    _, corps = rendre("/methode", {})
    assert "Apache 2.0" in corps
    assert "CC BY-SA" in corps
    assert "Licence Ouverte" in corps
    assert "cite le producteur, pas ce site" in corps


def test_chaque_page_du_site_est_comparee_au_portage():
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
    assert pages.SCENARIOS_MONTRES[0] == "actuel", "l'étalon ouvre la chaîne"
    assert set(pages.MARCHES_SYSTEMES) == set(pages.SCENARIOS_MONTRES[1:]), (
        "MARCHES_SYSTEMES et SCENARIOS_MONTRES ont divergé : "
        f"{set(pages.MARCHES_SYSTEMES) ^ set(pages.SCENARIOS_MONTRES[1:])}"
    )
    # Et l'ordre des marches est celui de la liste, non celui du dictionnaire.
    libelles = pages._libelles_cascade(site().contexte, 0.1, 0.4)
    rapports = {code: 1.0 for code in pages.SCENARIOS_MONTRES}
    rapports[COMPOSANTE_GARANTIE] = 0.0
    marches = pages._marches_cascade(1000.0, 0.1, rapports, libelles)
    attendus = ["Réversion supprimée"] + [
        pages.MARCHES_SYSTEMES[code][0].format(**libelles)
        for code in pages.SCENARIOS_MONTRES[1:]
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
    for code, (libelle, glose) in {**pages.MARCHES_SYSTEMES, **pages.MARCHES_HORS_SYSTEMES}.items():
        assert not chiffre.search(libelle), f"{code} : chiffre en dur dans « {libelle} »"
        assert not chiffre.search(glose), f"{code} : chiffre en dur dans sa glose"
    # Et le rendu, lui, en porte : les accolades ont bien été remplies.
    corps = rendre("/cout", {})[1]
    taux = g.pourcentage(contexte.base.taux_cotisation_liberal, decimales=0)
    assert f"Cotisation unique de {taux}" in corps


@pytest.mark.parametrize("chemin", list(TITRES))
def test_aucun_graphique_n_est_livre_sans_ses_chiffres(chemin):
    """Le tableau est émis par ``graphique()`` : il ne peut donc pas manquer.

    Ce test le vérifie sur les pages réellement rendues — c'est lui qui
    échouerait si quelqu'un réécrivait un tracé à la main, hors de la fonction
    qui en produit la description.
    """
    corps = rendre(chemin, {})[1]
    traces = corps.count('<figure class="graphique"')
    tableaux = corps.count('<details class="donnees-graphique">')
    assert traces == tableaux, (
        f"{chemin} : {traces} graphiques pour {tableaux} tableaux de données"
    )


def test_le_graphique_de_la_trajectoire_porte_ses_ages():
    """Sur la page de résultats, le seul graphique qui ne se lit pas en années."""
    corps = rendre("/simuler", {
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

    corps = rendre("/methode", {})[1]
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


def test_la_correction_des_trois_generations_se_retrouve():
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

    corps = rendre("/methode", {})[1]
    assert "un salarié du privé non cadre" in corps, (
        "la page doit dire sur quelle carrière ces points sont mesurés"
    )
    for generation, attendu in ((1920, 5.5), (1945, 0.0), (1958, -0.5)):
        mesure = correction(generation)
        assert round(mesure, 1) == attendu, (
            f"génération {generation} : la page annonce {attendu:+.1f} point(s), "
            f"le modèle en donne {mesure:+.1f}"
        )
        signe = "+" if attendu >= 0 else "-"
        écrit = f"{signe}{abs(attendu):.1f}".replace(".", ",")
        assert écrit in corps, f"« {écrit} » a disparu de la page"


def test_le_README_ne_compte_plus_ses_tests():
    """Le nombre de tests décrit le dépôt lui-même, et il sort de la prose.

    Le README annonçait 321 tests et `docs/limites.md` 390 quand le dépôt en
    comptait 520. Une sonde, `tests()`, les avait ensuite tenus justes ; mais
    le compte change à chaque session, et chaque test ajouté obligeait à
    récrire trois phrases. L'architecture tranche (`docs/architecture.md`,
    § 9.3) : les chiffres qui décrivent le dépôt lui-même — ses lignes, ses
    tests — sortent de la prose, et un script les affiche à la demande,
    `python scripts/tableau_de_bord.py --cout`. Ce test tient la règle là où
    le compte s'écrivait : l'arborescence du README, qu'aucune ancre ne
    pouvait tenir, et les deux phrases qui portaient la sonde.
    """
    import re
    from pathlib import Path

    racine = Path(__file__).resolve().parents[1]
    limites = sorted((racine / "docs" / "limites").glob("*.md"))
    for chemin in ("README.md", "docs/limites.md",
                   *(p.relative_to(racine).as_posix() for p in limites)):
        texte = (racine / chemin).read_text(encoding="utf-8")
        comptes = re.findall(r"\d[\d\s]*\s+tests (?:Python|couvrent)|<!--chiffre:tests\(\)-->", texte)
        assert not comptes, (
            f"{chemin} compte encore ses tests ({comptes}) : ce chiffre ne s'écrit "
            "plus, `python scripts/tableau_de_bord.py --cout` l'affiche")


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

    limites = sorted((racine / "docs" / "limites").glob("*.md"))
    for nom in ("README.md", "docs/limites.md",
                *(p.relative_to(racine).as_posix() for p in limites)):
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
def test_aucun_depliant_ne_coupe_un_paragraphe(chemin):
    """Et la règle vaut pour toute la page, pas seulement pour le glossaire.

    ``<details>``, ``<div>``, ``<ul>``, ``<h2>`` ferment un ``<p>`` ouvert. Le
    navigateur ne s'en plaint pas : il referme et continue, et la mise en page
    se décale sans que rien ne le dise. Ce contrôle regarde ce que le gabarit
    écrit, avant que l'analyseur ne le corrige.
    """
    corps = rendre(chemin, {})[1]
    for paragraphe in re.findall(r"<p\b[^>]*>(.*?)</p>", corps, re.S):
        for balise in ("<details", "<div", "<ul", "<ol", "<h2", "<h3", "<h4",
                       "<table", "<figure", "<section"):
            assert balise not in paragraphe, (
                f"{chemin} : {balise} dans un paragraphe — l'analyseur HTML y "
                f"fermera le <p>, et la suite de la phrase tombera hors de lui"
            )


@pytest.mark.parametrize("chemin", list(TITRES))
def test_chaque_mot_du_glossaire_porte_sa_definition(chemin):
    """Un mot signalé sans définition serait un bouton qui n'ouvre rien.

    Le bouton porte ``aria-expanded`` — sans quoi une synthèse vocale l'annonce
    comme un bouton ordinaire, sans dire qu'il déplie quelque chose — et la
    bulle le suit immédiatement, repliée : c'est sur cette adjacence que le
    script d'``index.html`` s'appuie pour la trouver.
    """
    corps = rendre(chemin, {})[1]
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
def test_aucune_page_ne_montre_de_balise_echappee(chemin):
    """Une balise échappée s'affiche en toutes lettres au lecteur.

    La légende d'un tableau est échappée par ``g.tableau``, et c'est voulu :
    elle n'est qu'une phrase. Deux légendes de la page Pourquoi changer y
    avaient pourtant reçu un mot du glossaire, et le visiteur lisait, sous le
    titre « Combien la retraite vous prend-elle chaque mois ? », une ligne de
    ``<span class="mot">`` et de ``role="button"`` — la première chose qu'un
    nouveau venu y voyait, relevée le 23 septembre 2026. Le mot du glossaire
    se pose dans une phrase, jamais dans une légende.
    """
    corps = rendre(chemin, {})[1]
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
    assert "body.plf-embedded footer .retour-site" in FEUILLE_DE_STYLE


def test_le_site_ne_dessine_plus_aucun_pictogramme_a_la_main():
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
        corps = rendre(chemin, {})[1]
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
    return FEUILLE_DE_STYLE.split("@media (max-width: 34rem)")[1].split("\n}\n")[0]


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
    regle = FEUILLE_DE_STYLE.split(".mot > .terme.appel {")[1].split("}")[0]
    assert "min-width: 1.5rem" in regle and "min-height: 1.5rem" in regle


def test_tous_les_depliants_portent_le_meme_chevron():
    """Le marqueur natif d'un ``<details>`` n'a ni la même forme ni la même
    taille d'un navigateur à l'autre : chaque résumé porte donc le chevron du
    jeu, et la feuille de style masque celui du navigateur."""
    for chemin in TITRES:
        corps = rendre(chemin, {})[1]
        resumes = re.findall(r"<summary>(.{0,40})", corps, re.S)
        for debut in resumes:
            assert debut.startswith('<svg class="icone" '), (
                f"{chemin} : un dépliant sans chevron — {debut!r}"
            )
    style = FEUILLE_DE_STYLE
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
    # Les tableaux sont passés de 240 à 245 mots le 7 octobre 2026 : la ligne
    # « Votre retraite » dit la baisse médiane en fractions CALCULÉES
    # (`ordreDeGrandeur`), « d'un quart » quand les deux écarts médians
    # tombent sur la même, « d'un cinquième à un quart » sinon — trois mots de
    # plus, qu'un écart de 22,6 % passé à 22,5 % a suffi à écrire.
    "/": (470, 0, 2, 245),
    "/simuler": (1500, 0, 0, 0),
    # Partager ne porte que des cartes : leur texte est court par
    # construction — il doit tenir dans une image de 1200 × 675.
    "/partager": (400, 0, 0, 0),
    # Le saviez-vous ? en porte douze, rangées sous quatre titres : une
    # cinquantaine de mots par carte, barre de partage et pied compris. Ce
    # qui explique chaque règle, et le lien vers son texte, sont repliés sous
    # la carte (673 mots ouverts le 4 octobre 2026).
    "/saviez-vous": (700, 0, 0, 0),
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
    visible = _hors_depliants(rendre(chemin, {})[1])

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


def test_la_page_de_resultats_replie_son_detail():
    """Qui vient de calculer sa pension veut son chiffre, pas une leçon.

    La page alignait sous ses six montants sept sections ouvertes — un
    graphique, neuf tableaux, quatre mille mots —, soit dix écrans de téléphone
    à traverser après le résultat. Tout y est encore, rangé dans des sections
    nommées qu'on ouvre une par une ; ce test tient la discipline, et la même
    borne de mots que le formulaire : les résultats n'ajoutent rien à ce qu'il
    faut traverser.
    """
    mots_max = BUDGETS_DE_LECTURE["/simuler"][0]
    corps = rendre("/simuler", SIMULATION_TEMOIN)[1]
    assert "Résultats" in corps, "la simulation témoin ne calcule rien"

    visible = _hors_depliants(corps)
    mots = len(re.sub(r"<[^>]+>", " ", visible).split())
    assert mots <= mots_max, (
        f"{mots} mots à traverser sur la page de résultats, {mots_max} au plus"
    )
    # Le seul tableau ouvert est un résultat, non un détail : le système 1 au
    # format de l'estimation officielle (action 142, étape 3).
    assert visible.count("<table") == visible.count(
        'class="carte estimation-officielle"'), "un tableau de détail reste ouvert"
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
def test_chaque_page_range_son_detail_dans_des_sections(chemin):
    """Replier n'est pas supprimer : ce qui sort du chemin doit y être rangé.

    Une page qui tiendrait son budget de lecture en ayant simplement perdu la
    moitié de son contenu passerait le test précédent. Celui-ci vérifie
    l'autre moitié du marché : le détail est là, dans des sections nommées, et
    il pèse plus que ce qui reste ouvert.
    """
    corps = rendre(chemin, {})[1]
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


def test_la_page_cout_ventile_ce_que_d_autres_caisses_versent():
    """Le poste « transferts » est ventilé par celui qui paie, et la page en tire
    la seule chose que le coefficient ne dit pas : la recette suit le droit."""
    corps = rendre("/cout", {})[1]
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


def test_les_parts_de_l_impot_et_la_depense_du_cor_se_calculent(contexte):
    """Trois chiffres de la page Coût étaient écrits en dur, et deux avaient
    vieilli : « 38 % » des impôts affectés pour le fonds de solidarité
    vieillesse, lu pour 2024 dans les recettes du fonds, quand ses versements
    de 2025 en font moins du tiers ; « 27 % » des ressources de 2024 pour les
    trois postes que la proposition ne reconduit pas, quand le compte en donne
    28 ; « quelque 420 milliards » pour la dépense du COR. Ils se calculent sur
    le compte, et la page écrit ce qu'il dit. Elle ne dit plus que la
    compensation des allègements n'apparaît pas au compte de la retraite : le
    COR l'y range (rapport annuel de 2026, tableau 2.2).
    """
    from retraite_notionnelle.donnees.equilibre import POSTES_TRANSFERTS

    def plat(texte):
        return " ".join(html.unescape(texte).split())

    comptes = contexte.comptes()
    texte = plat(re.sub(r"<[^>]+>", " ", rendre("/cout", {})[1]))

    ventilee = comptes.annees_ventilees()[-1]
    fin = min([ventilee] + [comptes.transferts[poste.code].derniere_annee
                            for poste in POSTES_TRANSFERTS
                            if poste.organisme == "solidarite"])
    part = (comptes.transfert_part_ressources("solidarite", fin)
            / comptes.part("impots_et_taxes", fin))
    phrase = plat(f"En {fin}, ce que ce fonds verse aux régimes en vaut "
                  f"{g.pourcentage(part, decimales=0)}.")
    # Deux fois : sous le tableau des postes, et dans la carte « Qui paie ? ».
    assert texte.count(phrase) == 2, phrase

    trois = sum(comptes.part(code, ventilee) for code in (
        "contribution_equilibre_etat", "subventions_equilibre", "impots_et_taxes"))
    assert plat(f"Trois postes : {g.pourcentage(trois, decimales=0)} des "
                f"ressources en {ventilee}") in texte

    derniere = contexte.depenses().derniere_annee
    cor = comptes.depense(derniere) * comptes.pib(derniere)
    assert plat(f"publie le Conseil d'orientation des retraites, "
                f"{pages.milliards(cor, 1)} la même année") in texte

    for perime in ("38 % en financent", "plus du tiers finance",
                   "quelque 420 milliards", "n'apparaît pas au compte de la retraite"):
        assert perime not in texte, perime


def test_la_page_cout_tient_en_deux_graphiques_et_sans_tableau_ouvert():
    """Le temps du lecteur n'est pas gratuit, et cette page le dépensait.

    Elle portait sept graphiques et neuf tableaux dépliés, huit mille mots à
    traverser avant d'atteindre un résultat. Ce qu'elle doit pouvoir justifier
    est toujours là — rien n'a été retiré —, mais replié, et les trois tracés
    qui suivaient la même grandeur sur trois fenêtres n'en font plus qu'un.

    Les bornes sont larges à dessein : elles n'interdisent pas d'écrire, elles
    interdisent de revenir à une page qu'on ne lit pas.
    """
    corps = rendre("/cout", {})[1]
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


def test_chaque_carte_de_la_page_cout_porte_sa_question_et_sa_reponse():
    """Une carte sans réponse est un graphique nu : le lecteur doit le lire.

    L'ordre compte autant que la présence — question, réponse, tracé — parce
    que c'est lui qui permet de s'arrêter à la deuxième ligne.
    """
    corps = rendre("/cout", {})[1]
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
    bilan = pages._compte_flux(site().contexte, contexte.base.annee_bascule)
    ligne = bilan.ligne
    caisses = {s: pages._caisse_flux(ligne, bilan.pib, s, s, "Cotisations")
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
    # Une TVA à taux unique entrerait au régime unique sous son nom, et elle
    # seule des impôts ; la proposition ne réforme plus la TVA depuis le
    # 24 septembre 2026, et aucun impôt n'y entre.
    assert ("TVA" in sources["notionnel_liberal"]) == (contexte.base.taux_tva_liberal > 0.0)
    assert {n.libelle for n in caisses["actuel"].usages} >= {"Pensions de réversion"}

    corps = rendre("/cout", {})[1]
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
    # usage, et la réponse chiffre l'un ou l'autre.
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
    solde = site().contexte.cout().solde
    obs, fin = solde.derniere_annee_observee, solde.derniere_annee
    bascule = contexte.base.annee_bascule
    assert bascule > obs, "le témoin suppose une bascule postérieure à l'année mesurée"
    offertes = pages._annees_flux(solde, bascule)
    assert offertes == [a for a in pages._annees_cascade(solde, bascule) if a >= bascule]
    assert offertes[0] == bascule and offertes[-1] == fin and obs not in offertes
    # Une bascule déjà passée : l'année mesurée ouvre la liste, comme celle de
    # la cascade ; une bascule à l'horizon : l'horizon seul.
    assert pages._annees_flux(solde, obs - 5)[0] == obs
    assert pages._annees_flux(solde, fin) == [fin]
    for demandee, attendue in (("", bascule), ("2070", 2070), (str(obs), bascule),
                               ("2035", bascule), ("deux mille", bascule),
                               ('"><script>', bascule)):
        assert pages._annee_flux(solde, bascule, {"flux": demandee}) == attendue, demandee
    assert pages._annee_flux(solde, bascule, None) == bascule


def test_chaque_annee_des_schemas_tombe_juste(contexte):
    """Pour toutes les années offertes, chaque caisse brasse ce qu'elle reçoit
    et ce qu'elle verse. La garantie de l'année est payée par l'impôt et, de
    plus en plus, par ce que les successions en rendent : les deux somment à
    la garantie, et la part des successions croît avec les années."""
    solde = site().contexte.cout().solde
    bascule = contexte.base.annee_bascule
    reprises = []
    for annee in pages._annees_flux(solde, bascule):
        compte = pages._compte_flux(site().contexte, annee)
        for systeme in ("actuel", "notionnel_liberal"):
            caisse = pages._caisse_flux(compte.ligne, compte.pib, systeme, systeme, "C")
            assert sum(n.valeur for n in caisse.sources) == pytest.approx(
                caisse.valeur, rel=1e-4), (annee, systeme)
            assert sum(n.valeur for n in caisse.usages) == pytest.approx(
                caisse.valeur), (annee, systeme)
        assert 0.0 <= compte.reprises < compte.garantie, annee
        assert compte.garantie == pytest.approx(
            compte.ligne.postes_depenses("notionnel_liberal")["garantie_vieillesse"])
        # Les milliards suivent la règle du site entier, et nulle autre.
        assert compte.pib == pages._pib_de_conversion(site().contexte.comptes(), annee)
        reprises.append(compte.reprises / compte.garantie)
    assert reprises[-1] > reprises[0], "les successions rendent plus à l'horizon"


def test_l_annee_des_schemas_se_choisit_et_garde_celle_de_la_cascade(contexte):
    """``flux`` pose l'année des schémas ; les deux sélecteurs de la page se
    gardent l'un l'autre ; le tableau poste par poste reste à la bascule."""
    bascule = contexte.base.annee_bascule
    corps = rendre("/cout", {"flux": "2070", "cascade": "2040"})[1]
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
    corps = rendre("/cout", {"flux": '"><script>alert(1)</script>'})[1]
    assert "<script>alert" not in corps
    assert f'<a href="#/cout?cascade=2030&flux={bascule}">2030</a>' in corps


def test_chaque_carte_a_publier_part_d_un_bouton_et_non_d_une_capture():
    """La page Partager demandait une capture d'écran ; elle n'en demande plus.

    Les cartes étaient rendues à leur taille réelle dans un cadre qui défilait,
    à charge pour le militant de faire défiler, de capturer et de recadrer une
    image que le site savait composer lui-même. Elles portent maintenant la
    MÊME barre que les graphiques — un seul jeu de classes, un seul code —, et
    chacune emporte le compte et l'adresse.
    """
    corps = rendre("/partager", {})[1]
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


def test_la_barre_de_partage_n_est_ecrite_qu_une_fois():
    """Deux endroits partagent — la carte d'un graphique, la carte à publier —
    et ils ne doivent pas diverger. Le gabarit n'en écrit qu'une, et les deux
    pages la reprennent telle quelle."""
    barre = g.barre_partage()
    for chemin in ("/cout", "/partager"):
        corps = rendre(chemin, {})[1]
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
