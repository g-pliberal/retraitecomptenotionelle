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
import os
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
    "test_proposition_prospective.py", "test_postes_ecartes.py",
    "test_chiffrage_plf.py", "test_scenarios_meres.py", "test_grille_large.py",
}

#: Les contrôles : niveau ``controle``.
CONTROLES = {
    # La prose et les affirmations du site, confrontées au dépôt.
    "test_prose.py", "test_affirmations.py",
    # La confrontation à OpenFisca, seconde implémentation écrite par d'autres
    # (ses exemples officiels restent rapides, plus bas), à Destinie 2 et à
    # TRAJECTOiRE, exécutés à part, dont les sorties sont figées.
    "test_oracle.py", "test_destinie.py", "test_trajectoire.py",
    # Les données : leur socle, leur certification, les lecteurs des
    # documents qui les apportent.
    "test_donnees.py", "test_verification.py", "test_bonifications_jaune.py",
    "test_juris_cnracl_taux.py", "test_lecture_pdf.py", "test_sre_jaune_pensions.py",
    "test_pap_plf_2026.py", "test_opef_frais_per.py",
    # Les registres.
    "test_frontiere_contributive.py", "test_sources_a_explorer.py",
    "test_source_locale.py", "test_referents.py",
    # L'outillage du dépôt : l'index de la DILA, la publication sur main et
    # ses pilotes de fusion, ce partage-ci, le filet des déplacements
    # (docs/architecture.md, § 12), l'arbre du dépôt et ce que les sessions
    # consomment.
    "test_dila_index.py", "test_pousser.py", "test_fusionner.py", "test_niveaux.py",
    "test_conservation.py", "test_outillage.py", "test_arbre.py", "test_consommation.py",
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
    # Le portage JavaScript, rejoué contre le Python : deux moteurs.
    ("test_cumul_activites.py",
     "test_le_portage_javascript_concorde_sur_des_cumuls_tires_au_hasard"): "complet",
    ("test_releve_lu.py", "test_le_portage_javascript_lit_les_memes_releves"): "complet",
    # Les étapes de l'acquisition, sur une requête sur cinq des témoins.
    ("test_droit.py", "test_les_deux_moteurs_ecrivent_les_memes_etapes"): "complet",
    # Les étapes de la liquidation et le journal, sur la même requête sur cinq.
    ("test_liquidation.py",
     "test_les_deux_moteurs_liquident_et_journalisent_a_l_identique"): "complet",
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


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """Marque chaque test de son niveau, avant que ``-m`` ne choisisse ; passe
    ceux d'un fichier isolé qui ont réussi tels quels (:data:`ISOLES`)."""
    vises = {Path(str(argument).split("::")[0]).name for argument in config.args}
    for item in items:
        nom = getattr(item, "originalname", None) or item.name
        item.add_marker(niveau(item.path.name, nom))
        if (item.path.name, nom) in SITE:
            item.add_marker("site")
        fichier = item.path.name
        if fichier not in ISOLES or os.environ.get(TESTS_SANS_MEMOIRE):
            continue
        empreinte = empreinte_isolee(fichier)
        if fichier not in vises and marque_de_reussite(empreinte, item.nodeid).exists():
            item.add_marker(pytest.mark.skip(
                reason="réussi au dernier passage, et rien de ce qu'il lit n'a bougé"))


# -- les fichiers isolés : ne se rejoue que ce qui a bougé ----------------------

#: Les fichiers de tests qui ne lisent rien du modèle, seulement ce qu'ils
#: déclarent ici et les outils qu'ils lancent. Un cas qui y a réussi ne se
#: rejoue pas tant que ni son fichier, ni ce qu'il lit, ni ces outils n'ont
#: bougé : son résultat serait le même. La mémoire en est commune aux
#: worktrees, comme celle des calculs. Visé expressément, le fichier se
#: rejoue ; ``TESTS_SANS_MEMOIRE=1`` rejoue tout, et GitHub, sans mémoire,
#: aussi.
ISOLES: dict[str, tuple[str, ...]] = {
    # Le script de publication, sur des dépôts montés dans un dossier
    # temporaire. Sous Windows, la machine chargée, un git coûte près d'une
    # seconde : ses onze cas tenaient le cinquième de la suite chaude, le
    # 4 octobre 2026. Ses pilotes de fusion, que le script donne à git
    # (action 148, étape 3), sont de ce qu'il lit.
    "test_pousser.py": ("scripts/pousser.sh", "scripts/fusionner.py"),
}
#: Les outils qu'un fichier isolé lance : leur version et leur configuration
#: entrent dans son empreinte.
OUTILS_DES_ISOLES = (("git", "--version"), ("bash", "--version"),
                     ("git", "config", "--system", "--list"),
                     ("git", "config", "--global", "--list"))
TESTS_SANS_MEMOIRE = "TESTS_SANS_MEMOIRE"
#: Où les réussites se gardent : une marque par cas, sous l'empreinte.
REUSSITES = memoire.DOSSIER.parent / "tests"
#: Les empreintes gardées, les plus récentes.
EMPREINTES_DES_ISOLES = 8
RACINE = Path(__file__).resolve().parents[1]
_EMPREINTES: dict[str, str] = {}


def empreinte_isolee(fichier: str) -> str:
    """Tout ce dont dépend le résultat d'un fichier isolé : lui-même, ce
    ``conftest.py``, ce qu'il déclare lire, les outils qu'il lance, leurs
    variables ``GIT_*``, Python et pytest. Une fois par processus."""
    if fichier not in _EMPREINTES:
        somme = hashlib.sha256(f"{sys.version}|{sys.platform}|{pytest.__version__}".encode())
        for chemin in (f"tests/{fichier}", "tests/conftest.py", *ISOLES[fichier]):
            somme.update(chemin.encode() + b"\0" + (RACINE / chemin).read_bytes())
        for outil in OUTILS_DES_ISOLES:
            try:
                acheve = subprocess.run(outil, capture_output=True)
                somme.update(acheve.stdout + acheve.stderr + str(acheve.returncode).encode())
            except OSError as souci:
                somme.update(repr(souci).encode())
        for nom in sorted(n for n in os.environ if n.startswith("GIT_")):
            somme.update(f"{nom}={os.environ[nom]}".encode())
        _EMPREINTES[fichier] = somme.hexdigest()[:24]
    return _EMPREINTES[fichier]


def marque_de_reussite(empreinte: str, nodeid: str) -> Path:
    return REUSSITES / empreinte / hashlib.sha256(nodeid.encode()).hexdigest()[:24]


def pytest_runtest_logreport(report):
    """Un cas d'un fichier isolé a réussi : il se marque, sous l'empreinte que
    ce processus a prise en le collectant (le maître de xdist, qui ne collecte
    rien, ne marque rien)."""
    if report.when != "call" or not report.passed or os.environ.get(TESTS_SANS_MEMOIRE):
        return
    fichier = Path(report.nodeid.split("::")[0]).name
    if fichier not in _EMPREINTES:
        return
    marque = marque_de_reussite(_EMPREINTES[fichier], report.nodeid)
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
    l'empêche pas de garder."""
    monkeypatch.setattr(memoire, "DOSSIER", tmp_path / "calculs")
    monkeypatch.setattr(memoire, "_EN_MEMOIRE", {})
    monkeypatch.setattr(memoire, "_code_retouche", lambda: False)
    monkeypatch.delenv(memoire.SANS_MEMOIRE, raising=False)
    return memoire
