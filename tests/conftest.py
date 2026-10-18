"""Les trois niveaux de la suite, et la suite rapide.

    python -m pytest -m rapide    # les règles et les étapes, sous deux minutes
    python -m pytest              # tout : la suite complète, avant d'envoyer sur main

``docs/architecture.md`` (§ 10) range les tests en trois niveaux :

``rapide``
    Les règles — exemples officiels et cas de bascule — et les étapes, chacune
    seule. C'est la suite qu'on relance en travaillant ; son budget est de
    deux minutes (§ 9.1).
``complet``
    Les témoins, joués par les deux moteurs, le site et ses pages, et les
    agrégats de la page Coût, avec les scripts qui les déplacent.
``controle``
    La confrontation aux autres modèles, la certification des données et les
    lecteurs de sources, la prose et les affirmations du site, les registres,
    l'outillage du dépôt.

Chaque test reçoit la marque de son niveau, et ``-m`` choisit. Un fichier
qu'aucune table ne nomme est ``rapide`` : les fichiers de tests qui naissent
sont presque tous ceux d'une règle, et une règle doit être dans la suite
rapide. Un fichier lent qui naît se range donc ici, dans ``COMPLETS`` ou dans
``CONTROLES``, sans quoi il ferait sortir la suite rapide de son budget.

``python -m pytest``, sans ``-m``, ne choisit rien : il lance les trois
niveaux, comme avant. C'est la suite complète, que ``CLAUDE.md`` demande avant
tout envoi sur ``main``, et que GitHub rejoue à chaque envoi.

Une marque de plus ne dit pas un niveau mais un moment : ``site``, le filet
qu'on rejoue en une minute après une retouche des pages, du formulaire ou d'un
champ de saisie, avant la suite complète (``python -m pytest -m site``).

Un fichier isolé — qui ne lit rien du modèle, seulement ce qu'il déclare dans
``ISOLES`` — ne rejoue pas un cas qui a réussi tant que rien de ce qu'il lit
n'a bougé.
"""

from __future__ import annotations

import hashlib
import inspect
import os
import re
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from retraite_notionnelle import memoire

NIVEAUX = {
    "rapide": "les règles et les étapes, chacune seule : la suite rapide",
    "complet": "les témoins, le site et les agrégats de la page Coût",
    "controle": "les confrontations, la certification, la prose, les registres, l'outillage",
}

#: Les témoins, le site et les agrégats : niveau ``complet``.
COMPLETS = {
    # Le site : ses pages, figées en témoins et rejouées par le portage
    # JavaScript (``node --test`` compris), son formulaire, le parcours de
    # présentation.
    "test_web.py", "test_web_saisie.py", "test_web_revues.py", "test_formulaire.py",
    "test_parcours.py",
    # Le pont par lequel le Python lit le site : il lance node.
    "test_site.py",
    # Le système 1 au format de « Mon estimation retraite » : les deux
    # moteurs, et la page qui le montre.
    "test_estimation_du_site.py",
    # La page Coût et les scripts qui la déplacent : chacun recalcule le coût
    # agrégé, sous une variante.
    "test_cout.py", "test_cout_age_depart.py", "test_age_conjoncturel.py",
    "test_age_depart_csp.py", "test_avantages.py", "test_garantie_par_sexe.py",
    "test_solde_fusion.py", "test_stock_age_legal.py",
    "test_proposition_prospective.py", "test_postes_ecartes.py", "test_effet_retour.py",
    "test_chiffrage_plf.py", "test_scenarios_meres.py", "test_grille_large.py",
    # Ce que les pages qui agrègent lisent du modèle, figé sous la référence,
    # confronté au modèle qui le calcule.
    "test_agregats.py",
}

#: Les contrôles : niveau ``controle``.
CONTROLES = {
    # La prose et les affirmations du site, confrontées au dépôt.
    "test_prose.py", "test_affirmations.py",
    # La confrontation à OpenFisca, seconde implémentation écrite par d'autres
    # (ses exemples officiels restent rapides, plus bas), à Destinie 2, à
    # TRAJECTOiRE et à Ines, exécutés à part, dont les sorties sont figées ; et
    # celle de la part des nouveaux retraités au minimum contributif à l'EACR.
    # OpenFisca au-delà des carrières simples, une famille de profils à la
    # fois (action 153).
    "test_oracle.py", "test_oracle_familles.py", "test_oracle_enfants.py",
    "test_oracle_categorie_active.py", "test_oracle_carriere_longue_fonction_publique.py",
    "test_oracle_minima.py", "test_oracle_points_enfants_arrco.py",
    "test_oracle_salaire_annuel_moyen.py", "test_oracle_periodes_assimilees.py",
    "test_destinie.py",
    "test_trajectoire.py", "test_ines.py", "test_part_minimum_contributif.py",
    # Les cas types statutaires, confrontés aux départs de 2025 que le jaune
    # pensions décrit (action 159, étape 4).
    "test_flux_fonction_publique.py",
    # Les indicateurs de cycle de vie, confrontés au COR, à TRAJECTOiRE et à
    # l'OCDE, sous leurs conventions.
    "test_cycle_de_vie_references.py",
    # La dépense en ses quatre facteurs, confrontée à l'Ageing Report de 2024
    # (sa formule et son identité restent rapides, plus bas).
    "test_facteurs_depense.py",
    # Les leviers qui équilibreraient chaque système, confrontés à ceux du COR
    # (le témoin et le geste de l'âge restent rapides, plus bas).
    "test_leviers.py",
    # Le niveau de pension des cas types, confronté à Ancetre par régime
    # principal (le témoin et la mesure restent rapides, plus bas).
    "test_controle_ancetre.py",
    # L'âge des retraités, l'âge où ils partent et leurs conditions de départ,
    # confrontés à l'EACR (le témoin et la mesure restent rapides, plus bas).
    "test_controle_eacr.py",
    # Les données : leur socle, leur certification, les lecteurs des
    # documents qui les apportent.
    "test_donnees.py", "test_verification.py", "test_bonifications_jaune.py",
    "test_juris_cnracl_taux.py", "test_lecture_pdf.py", "test_sre_jaune_pensions.py",
    "test_sre_jaune_referents.py", "test_sre_jaune_ministeres.py",
    "test_pap_plf_2026.py", "test_opef_frais_per.py", "test_ccss_regimes.py",
    "test_ccss_transferts_retraite.py",
    # Les registres.
    "test_frontiere_contributive.py", "test_sources_a_explorer.py",
    "test_source_locale.py", "test_referents.py",
    # Les régimes dont la règle d'une génération change avec l'année de son
    # départ, déclarés un à un sur le balayage de toutes les générations
    # depuis 1920 (action 121).
    "test_regle_de_chacun.py",
    # L'outillage du dépôt : l'index de la DILA, la publication sur main et
    # ses pilotes de fusion, ce partage-ci, le filet des déplacements
    # (docs/architecture.md, § 12), l'arbre du dépôt, ce que les sessions
    # consomment, le hook qui refuse les lectures d'un bloc, celui du test
    # d'abord (action 162), et la carte des jumeaux Python et JavaScript
    # (action 161).
    "test_dila_index.py", "test_pousser.py", "test_fusionner.py", "test_niveaux.py",
    "test_conservation.py", "test_outillage.py", "test_arbre.py", "test_consommation.py",
    "test_hook_lecture.py", "test_hook_tdd.py", "test_jumeaux.py",
    # La saisie outillée des simulateurs officiels, et la confrontation d'une
    # carrière réelle à « Mon estimation retraite » (docs/architecture.md, § 3.5).
    "test_simulateurs.py", "test_estimation_officielle.py",
}

#: Les tests qui ne sont pas du niveau de leur fichier.
EXCEPTIONS = {
    # Les exemples officiels sont des règles, et la suite rapide les joue.
    ("test_oracle.py", "test_les_exemples_publies_par_les_caisses_sont_reproduits"): "rapide",
    ("test_oracle.py", "test_le_temoin_des_exemples_officiels_est_source"): "rapide",
    ("test_oracle.py", "test_un_ecart_connu_entre_et_ne_change_pas_en_silence"): "rapide",
    # La formule de l'Ageing Report, refaite sur ses propres séries, sans modèle.
    ("test_facteurs_depense.py",
     "test_le_temoin_de_l_ageing_report_dit_sa_source_et_tient_ses_identites"): "rapide",
    ("test_facteurs_depense.py", "test_la_formule_de_l_awg_refait_ses_effets_publies"): "rapide",
    ("test_facteurs_depense.py",
     "test_les_quatre_facteurs_font_la_part_de_pib_et_un_seul_qui_bouge_fait_tout"): "rapide",
    ("test_facteurs_depense.py",
     "test_la_couverture_se_partage_exactement_entre_les_ages"): "rapide",
    # Le témoin des leviers du COR, et le geste de l'âge refait sur ses séries.
    ("test_leviers.py", "test_le_temoin_du_cor_dit_sa_source_et_redonne_le_rapport"): "rapide",
    ("test_leviers.py",
     "test_le_recul_deplace_des_generations_entieres_et_avance_sur_une_marge"): "rapide",
    ("test_leviers.py", "test_les_leviers_et_les_ecarts_se_lisent_dans_le_bilan"): "rapide",
    ("test_leviers.py", "test_le_geste_de_l_age_refait_les_ages_d_equilibre_du_cor"): "rapide",
    # Le témoin d'Ancetre, et la mesure sur une grille d'essai.
    ("test_controle_ancetre.py",
     "test_le_temoin_d_ancetre_dit_sa_source_et_redonne_le_rapport"): "rapide",
    ("test_controle_ancetre.py", "test_chaque_caisse_de_la_grille_a_son_regime_principal"): "rapide",
    ("test_controle_ancetre.py",
     "test_la_pension_d_un_cas_type_pese_ses_cohortes_parties"): "rapide",
    ("test_controle_ancetre.py",
     "test_un_regime_principal_moyenne_ses_cas_types_a_leur_poids"): "rapide",
    # Le témoin de l'EACR, et la mesure sur une grille d'essai.
    ("test_controle_eacr.py",
     "test_le_temoin_de_l_eacr_dit_sa_source_et_redonne_ses_totaux"): "rapide",
    ("test_controle_eacr.py", "test_les_tranches_couvrent_tous_les_ages"): "rapide",
    ("test_controle_eacr.py",
     "test_une_cohorte_compte_ses_tetes_et_dit_si_elle_part_l_annee_meme"): "rapide",
    ("test_controle_eacr.py", "test_les_conditions_de_depart_se_lisent_en_parts"): "rapide",
    # Le portage JavaScript, rejoué contre le Python : deux moteurs.
    ("test_cumul_activites.py",
     "test_le_portage_javascript_concorde_sur_des_cumuls_tires_au_hasard"): "complet",
    # Les étapes de l'acquisition, sur une requête sur cinq des témoins.
    ("test_droit.py", "test_les_deux_moteurs_ecrivent_les_memes_etapes"): "complet",
    # Les étapes de la liquidation et le journal, sur la même requête sur cinq.
    ("test_liquidation.py",
     "test_les_deux_moteurs_liquident_et_journalisent_a_l_identique"): "complet",
    # Les deux minima des exploitants agricoles, dans les deux moteurs.
    ("test_minima_agricoles.py",
     "test_les_deux_moteurs_servent_les_memes_minima_agricoles"): "complet",
    # Le bilan du compte sur la grille : il lit le coût agrégé.
    ("test_bilan_compte.py",
     "test_la_grille_donne_une_duree_de_rotation_a_la_suedoise"): "complet",
    # Les gardes d'une seconde qui ont rougi main, du 6 au 17 octobre 2026,
    # sans qu'aucune session les ait joués (action 163, garde 3) : les modules
    # préchargés, les comptes du README et du parcours, le menu des statuts, la
    # table des niveaux et les isolés, le bloc « Reprise » et les notes ; puis
    # les tableaux des carrières du parcours.
    ("test_web.py", "test_les_modules_sont_tous_precharges"): "rapide",
    ("test_web.py", "test_le_README_n_ecrit_a_la_main_ni_statuts_ni_regimes"): "rapide",
    ("test_web_revues.py", "test_le_menu_des_statuts_est_groupe_par_famille"): "rapide",
    ("test_niveaux.py", "test_chaque_exception_vise_un_test_qui_existe"): "rapide",
    ("test_niveaux.py", "test_un_fichier_isole_n_importe_rien_du_depot"): "rapide",
    ("test_prose.py", "test_chaque_action_en_cours_s_ouvre_sur_son_bloc_reprise"): "rapide",
    ("test_prose.py",
     "test_les_notes_de_la_feuille_de_route_se_rangent_par_action"): "rapide",
    ("test_parcours.py", "test_aucun_compte_du_parcours_ne_s_ecrit_a_la_main"): "rapide",
    ("test_parcours.py", "test_aucun_tableau_de_carriere_ne_s_ecrit_a_la_main"): "rapide",
}


#: Le filet du site : le budget de mots du formulaire vierge, ses bornes
#: opposées hors du navigateur, les pages figées et leur portage, et le
#: catalogue des affirmations. Ce sont eux qu'une retouche de
#: ``moteur/js/pages.js`` fait tomber, et la suite complète ne les montrait
#: qu'au bout de cinq minutes.
SITE = {
    ("test_web.py", "test_le_simulateur_tient_en_peu_de_mots"),
    ("test_web.py", "test_les_temoins_du_portage_sont_a_jour"),
    ("test_web.py", "test_le_portage_javascript_retrouve_les_chiffres_du_modele"),
    ("test_web.py", "test_chaque_page_du_site_est_comparee_au_portage"),
    ("test_web_saisie.py", "test_toute_borne_du_formulaire_est_opposable_hors_du_navigateur"),
    ("test_web_saisie.py", "test_les_bornes_des_calendriers_sont_opposables_hors_du_navigateur"),
    ("test_affirmations.py", "test_rien_n_echappe_au_catalogue"),
}


def niveau(fichier: str, test: str) -> str:
    """Le niveau d'un test, par son fichier et, au besoin, par son nom."""
    if (fichier, test) in EXCEPTIONS:
        return EXCEPTIONS[(fichier, test)]
    if fichier in COMPLETS:
        return "complet"
    if fichier in CONTROLES:
        return "controle"
    return "rapide"


def pytest_configure(config):
    for nom, sens in NIVEAUX.items():
        config.addinivalue_line("markers", f"{nom}: {sens}")
    config.addinivalue_line(
        "markers", "site: le filet du site, après une retouche des pages ou de la saisie")
    if os.environ.get(PRESOMPTIONS_DECALEES):
        _decaler_les_presomptions()


# -- les présomptions décalées : les tests qui en dépendent ---------------------

#: Posée, cette variable rejoue les tests sous d'autres présomptions que celles
#: du vocabulaire (``data/reference/vocabulaire/valeurs.yaml``) : ceux qui
#: échouent en dépendent, quand un test qui raconte une date doit la déclarer
#: entière (feuille de route, action 135, levier 2). Le portage, qui lit les
#: siennes dans le paquet, n'est pas décalé : ses confrontations au Python
#: échouent sans rien dire des tests. Les mémoires se taisent le temps de la
#: mesure : rien de ce qui s'y calcule ne se garde.
PRESOMPTIONS_DECALEES = "PRESOMPTIONS_DECALEES"
#: Les valeurs de la mesure : le 1er du mois, l'autre branche de R. 351-37 ;
#: les enfants et le mariage trois ans plus tôt et plus tard.
DECALAGES = {"jour_de_naissance": 1, "naissance_des_enfants": 27, "mariage_des_conjoints": 30}


def _decaler_les_presomptions() -> None:
    """Le vocabulaire lui-même dit d'autres valeurs : un test qui y lit la
    sienne passe, un test qui l'écrit en dur échoue."""
    from retraite_notionnelle import chronologie
    from retraite_notionnelle.noyau import vocabulaire

    lire = vocabulaire.presomptions

    def decalees(dossier=vocabulaire.VOCABULAIRE):
        table = lire(dossier)
        if Path(dossier) == vocabulaire.VOCABULAIRE:
            for nom, valeur in DECALAGES.items():
                table[nom] = {**table[nom], "valeur": valeur}
        return table

    vocabulaire.presomptions = decalees
    chronologie._vocabulaire = decalees
    for variable in (memoire.SANS_MEMOIRE, "TESTS_SANS_MEMOIRE", "FABRIQUE_SANS_MEMOIRE"):
        os.environ[variable] = "1"


#: Un test qui confronte le Python au portage, que node fait tourner.
_CONFRONTE_AU_PORTAGE = re.compile(r'"node"|tests/js/|comparer[-\w]*\.mjs')


def _confronte_au_portage(item) -> bool:
    """Le test lui-même, ou l'une des fixtures qu'il demande, qui fait souvent
    tourner node une fois pour tous les cas d'un fichier."""
    fonctions = [getattr(item, "function", None)]
    definitions = getattr(getattr(item, "_fixtureinfo", None), "name2fixturedefs", {})
    for nom in getattr(item, "fixturenames", ()):
        fonctions += [definition.func for definition in definitions.get(nom, ())]
    for fonction in fonctions:
        try:
            if _CONFRONTE_AU_PORTAGE.search(inspect.getsource(fonction)):
                return True
        except (AttributeError, OSError, TypeError):
            continue
    return False


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """Marque chaque test de son niveau, avant que ``-m`` ne choisisse ; passe
    ceux d'un fichier isolé qui ont réussi tels quels (:data:`ISOLES`), et,
    les présomptions décalées, ceux qui confrontent le Python au portage."""
    vises = {Path(str(argument).split("::")[0]).name for argument in config.args}
    vises |= {f"{Path(argument.split('::')[0]).name}::{argument.split('::')[1].split('[')[0]}"
              for argument in map(str, config.args) if "::" in argument}
    decalees = os.environ.get(PRESOMPTIONS_DECALEES)
    for item in items:
        nom = getattr(item, "originalname", None) or item.name
        item.add_marker(niveau(item.path.name, nom))
        if (item.path.name, nom) in SITE:
            item.add_marker("site")
        if decalees and _confronte_au_portage(item):
            item.add_marker(pytest.mark.skip(
                reason="le portage lit ses présomptions dans le paquet, que la mesure ne décale pas"))
        cle = cle_isolee(item.path.name, nom)
        if cle is None or os.environ.get(TESTS_SANS_MEMOIRE):
            continue
        empreinte = empreinte_isolee(cle)
        if cle not in vises and marque_de_reussite(empreinte, item.nodeid).exists():
            item.add_marker(pytest.mark.skip(
                reason="réussi au dernier passage, et rien de ce qu'il lit n'a bougé"))


# -- les fichiers isolés : ne se rejoue que ce qui a bougé ----------------------

#: Les fichiers de tests qui ne lisent rien du modèle, seulement ce qu'ils
#: déclarent ici et les outils qu'ils lancent, et, sous ``fichier::test``,
#: les tests qui, dans un fichier qui le lit, n'en lisent rien eux-mêmes. Un
#: cas qui y a réussi ne se rejoue pas tant que ni son fichier, ni ce qu'il
#: lit, fichiers ou dossiers entiers, ni ces outils n'ont bougé : son
#: résultat serait le même. La mémoire en est commune aux worktrees, comme
#: celle des calculs. Visé expressément, le fichier — ou le test, pour un
#: test déclaré seul — se rejoue ; ``TESTS_SANS_MEMOIRE=1`` rejoue tout, et
#: GitHub, sans mémoire, aussi.
ISOLES: dict[str, tuple[str, ...]] = {
    # Le script de publication, sur des dépôts montés dans un dossier
    # temporaire. Sous Windows, la machine chargée, un git coûte près d'une
    # seconde : ses onze cas tenaient le cinquième de la suite chaude, le
    # 4 octobre 2026. Ses pilotes de fusion, que le script donne à git
    # (action 148, étape 3), sont de ce qu'il lit, comme le hook du test
    # d'abord, qu'il consulte avant d'envoyer (action 162).
    "test_pousser.py": ("scripts/pousser.sh", "scripts/fusionner.py",
                        ".claude/hooks/tdd.py"),
    # ``node --test`` (action 135) : 13 s, la mémoire des calculs pleine. Il
    # ne lit que le portage et le site, le paquet, les témoins, les essais
    # JavaScript et les quotients de mortalité qu'il refait au bit près ; le
    # paquet suit le modèle, mais c'est à d'autres tests de le dire à jour.
    "test_web.py::test_le_portage_javascript_retrouve_les_chiffres_du_modele": (
        "moteur", "tests/js", "tests/temoins", "data/reference/mortalite"),
}
#: Les outils qu'un fichier isolé lance : leur version et leur configuration
#: entrent dans son empreinte.
OUTILS_DES_ISOLES = (("git", "--version"), ("bash", "--version"),
                     ("git", "config", "--system", "--list"),
                     ("git", "config", "--global", "--list"), ("node", "--version"))
TESTS_SANS_MEMOIRE = "TESTS_SANS_MEMOIRE"
#: Où les réussites se gardent : une marque par cas, sous l'empreinte.
REUSSITES = memoire.DOSSIER.parent / "tests"
#: Les empreintes gardées, les plus récentes.
EMPREINTES_DES_ISOLES = 8
RACINE = Path(__file__).resolve().parents[1]
_EMPREINTES: dict[str, str] = {}


def cle_isolee(fichier: str, test: str) -> str | None:
    """La clé de :data:`ISOLES` qui couvre ce test, le test seul d'abord."""
    for cle in (f"{fichier}::{test}", fichier):
        if cle in ISOLES:
            return cle
    return None


def _lus(chemin: str) -> list[str]:
    """Le fichier déclaré, ou tous ceux du dossier déclaré, à toute
    profondeur : un fichier qui y naît ou en disparaît change l'empreinte."""
    dossier = RACINE / chemin
    if not dossier.is_dir():
        return [chemin]
    return sorted(f.relative_to(RACINE).as_posix() for f in dossier.rglob("*")
                  if f.is_file() and "__pycache__" not in f.parts)


def empreinte_isolee(cle: str) -> str:
    """Tout ce dont dépend le résultat d'un fichier ou d'un test isolé : son
    fichier, ce ``conftest.py``, ce qu'il déclare lire, les outils qu'il
    lance, leurs variables ``GIT_*`` et ``NODE_*``, Python et pytest. Une fois
    par processus."""
    if cle not in _EMPREINTES:
        somme = hashlib.sha256(f"{cle}|{sys.version}|{sys.platform}|{pytest.__version__}".encode())
        fichier = cle.split("::")[0]
        for declare in (f"tests/{fichier}", "tests/conftest.py", *ISOLES[cle]):
            for chemin in _lus(declare):
                somme.update(chemin.encode() + b"\0" + (RACINE / chemin).read_bytes())
        for outil in OUTILS_DES_ISOLES:
            try:
                acheve = subprocess.run(outil, capture_output=True)
                somme.update(acheve.stdout + acheve.stderr + str(acheve.returncode).encode())
            except OSError as souci:
                somme.update(repr(souci).encode())
        for nom in sorted(n for n in os.environ if n.startswith(("GIT_", "NODE_"))):
            somme.update(f"{nom}={os.environ[nom]}".encode())
        _EMPREINTES[cle] = somme.hexdigest()[:24]
    return _EMPREINTES[cle]


def marque_de_reussite(empreinte: str, nodeid: str) -> Path:
    return REUSSITES / empreinte / hashlib.sha256(nodeid.encode()).hexdigest()[:24]


def pytest_runtest_logreport(report):
    """Un cas d'un fichier isolé a réussi : il se marque, sous l'empreinte que
    ce processus a prise en le collectant (le maître de xdist, qui ne collecte
    rien, ne marque rien)."""
    if report.when != "call" or not report.passed or os.environ.get(TESTS_SANS_MEMOIRE):
        return
    parties = report.nodeid.split("::")
    cle = cle_isolee(Path(parties[0]).name, parties[-1].split("[")[0])
    if cle not in _EMPREINTES:
        return
    marque = marque_de_reussite(_EMPREINTES[cle], report.nodeid)
    try:
        if not marque.parent.exists():
            marque.parent.mkdir(parents=True, exist_ok=True)
            anciennes = sorted((d for d in REUSSITES.iterdir() if d != marque.parent),
                               key=lambda d: d.stat().st_mtime, reverse=True)
            for ancienne in anciennes[EMPREINTES_DES_ISOLES - 1:]:
                shutil.rmtree(ancienne, ignore_errors=True)
        marque.touch()
    except OSError:              # la mémoire n'est qu'un raccourci
        pass


# -- le rouge du test d'abord ----------------------------------------------------


def pytest_sessionfinish(session, exitstatus):
    """Le test d'abord (``CLAUDE.md``, « Travailler ») : une séance qui échoue
    pendant qu'un test s'écrit a vu le rouge, et le hook
    ``.claude/hooks/tdd.py``, qui le lit, laisse alors toucher au code sans
    rappel. Le maître seul, sous xdist : il reçoit les échecs de tous."""
    if session.testsfailed and not hasattr(session.config, "workerinput"):
        runpy.run_path(str(RACINE / ".claude" / "hooks" / "tdd.py"))["noter_le_rouge"](
            session.config.rootpath)


# -- la mémoire des calculs, et ce qui la fait taire -----------------------------


@pytest.fixture
def monkeypatch(monkeypatch, request):
    """``monkeypatch``, sous lequel la mémoire des calculs se tait.

    Un test qui remplace une fonction du modèle ne doit ni recevoir un coût
    gardé, calculé sans son remplacement, ni en garder un qui l'aurait subi
    (``retraite_notionnelle/memoire.py``). Les tests de la mémoire elle-même
    demandent ``memoire_isolee``, qui la rouvre dans un dossier à eux.
    """
    if "memoire_isolee" in request.fixturenames:
        yield monkeypatch
        return
    with memoire.modele_modifie():
        yield monkeypatch


@pytest.fixture
def memoire_isolee(monkeypatch, tmp_path):
    """La mémoire des calculs, vide, dans un dossier propre à ce test, et qui
    ne regarde pas le dépôt : qu'un fichier Python y change pendant la suite ne
    l'empêche pas de garder, et les calculs factices des tests, écrits hors du
    modèle, s'y gardent sous leur seule clé."""
    monkeypatch.setattr(memoire, "DOSSIER", tmp_path / "calculs")
    monkeypatch.setattr(memoire, "_EN_MEMOIRE", {})
    monkeypatch.setattr(memoire, "_code_retouche", lambda: False)
    monkeypatch.setattr(memoire, "_code_hors_du_modele", lambda calcul: ())
    monkeypatch.delenv(memoire.SANS_MEMOIRE, raising=False)
    return memoire
