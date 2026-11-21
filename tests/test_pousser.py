"""Ce que `scripts/pousser.sh` fait, et ce qu'il refuse de faire.

Le script est la recette de publication du dépôt : tout va sur `main`, et la
branche `claude/…` qu'une session web se voit assigner ne sert qu'à faire taire
un compteur. `CLAUDE.md` raconte ce que son absence a coûté — des lignées sans
ancêtre commun, un `main` trois jours en arrière, et des sessions entières
dépensées à expliquer un chiffre faux. Ces tests le tiennent.

Chaque cas monte un dépôt complet dans un répertoire temporaire : un dépôt nu
qui joue GitHub, un clone qui joue la session. Rien ne touche au réseau ni au
dépôt courant.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "pousser.sh"


def git(depot: Path, *arguments: str) -> str:
    """Un git dans ``depot``, qui lève si la commande échoue."""
    acheve = subprocess.run(
        ["git", *arguments], cwd=depot, capture_output=True, text=True, encoding="utf-8",
        check=True,
    )
    return acheve.stdout.strip()


def pousser(depot: Path, *options: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(SCRIPT), *options], cwd=depot, capture_output=True, text=True,
        encoding="utf-8",
    )


def commiter(depot: Path, nom: str, texte: str = "x") -> str:
    (depot / nom).write_text(texte, encoding="utf-8")
    git(depot, "add", nom)
    git(depot, "commit", "--quiet", "-m", f"ajoute {nom}")
    return git(depot, "rev-parse", "HEAD")


@pytest.fixture(scope="module")
def modele_d_atelier(tmp_path_factory) -> Path:
    """L'atelier, monté une fois par module, que chaque cas copie : sous
    Windows, la machine chargée, un git coûte près d'une seconde, et monter
    l'atelier prenait de dix à vingt-cinq secondes par cas."""
    racine = tmp_path_factory.mktemp("atelier")
    distant = racine / "origin.git"
    subprocess.run(["git", "init", "--quiet", "--bare", "--initial-branch=main",
                    str(distant)], check=True)
    # Copiés pour chaque cas, les dépôts n'écrivent rien en arrière-plan.
    for cle, valeur in (("maintenance.auto", "false"), ("gc.auto", "0"),
                        ("receive.autogc", "false")):
        git(distant, "config", cle, valeur)

    amorce = racine / "amorce"
    subprocess.run(["git", "clone", "--quiet", str(distant), str(amorce)], check=True)
    git(amorce, "config", "user.email", "essai@exemple.fr")
    git(amorce, "config", "user.name", "Essai")
    git(amorce, "checkout", "--quiet", "-B", "main")
    commiter(amorce, "depart.txt")
    git(amorce, "push", "--quiet", "origin", "main")

    session = racine / "session"
    subprocess.run(["git", "clone", "--quiet", str(distant), str(session)], check=True)
    git(session, "config", "maintenance.auto", "false")
    git(session, "config", "gc.auto", "0")
    # L'identité d'une session web : la seule adresse qu'elle publie.
    git(session, "config", "user.email", "noreply@anthropic.com")
    git(session, "config", "user.name", "Claude")
    git(session, "checkout", "--quiet", "-b", "claude/essai")
    return racine


@pytest.fixture
def atelier(modele_d_atelier: Path, tmp_path: Path) -> tuple[Path, Path]:
    """Un dépôt nu qui joue GitHub, et un clone posé sur une branche de session,
    copiés du modèle : la session suit le dépôt nu de sa copie."""
    distant, session = tmp_path / "origin.git", tmp_path / "session"
    shutil.copytree(modele_d_atelier / "origin.git", distant)
    shutil.copytree(modele_d_atelier / "session", session)
    git(session, "remote", "set-url", "origin", str(distant))
    return distant, session


def test_l_atelier_ne_lance_aucune_maintenance(modele_d_atelier: Path):
    """Copiés pour chaque cas, le dépôt nu et la session ne doivent rien écrire
    en arrière-plan : la maintenance automatique que git détache après un
    commit, ou que le dépôt nu lance en recevant une poussée
    (``receive.autogc``), tient un verrou que la copie ne retrouve plus. Le
    17 octobre 2026, sur GitHub, la copie du modèle de ``test_hook_tdd.py`` a
    échoué ainsi."""
    attendu = {"origin.git": (("maintenance.auto", "false"), ("gc.auto", "0"),
                              ("receive.autogc", "false")),
               "session": (("maintenance.auto", "false"), ("gc.auto", "0"))}
    for depot, cles in attendu.items():
        for cle, valeur in cles:
            lu = subprocess.run(["git", "-C", str(modele_d_atelier / depot), "config",
                                 "--get", cle], capture_output=True, text=True).stdout.strip()
            assert lu == valeur, f"{depot} : {cle}"


def tete_distante(distant: Path, branche: str) -> str:
    return git(distant, "rev-parse", branche)


# -- ce qu'il publie ----------------------------------------------------------


def test_le_travail_va_sur_main_et_pas_sur_la_branche(atelier):
    """La règle du dépôt : tout sur `main`, quelle que soit la branche locale."""
    distant, session = atelier
    tete = commiter(session, "travail.txt")

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert "main ←" in acheve.stdout, "le script dit ce qu'il a poussé"
    assert tete_distante(distant, "main") == tete

    with pytest.raises(subprocess.CalledProcessError):
        # La branche de session n'a pas été créée : une session ne saurait pas
        # la supprimer ensuite (403), et le script s'interdit de la créer.
        tete_distante(distant, "claude/essai")


def test_sans_rien_a_publier_le_script_se_tait(atelier):
    """Silencieux quand il n'y a rien à faire : c'est ce qui le rend relançable."""
    _, session = atelier
    commiter(session, "travail.txt")
    assert pousser(session).returncode == 0

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert acheve.stdout.strip() == "", "rien à publier, donc rien à dire"


def test_il_rattrape_ce_que_main_a_recu_entre_temps(atelier, tmp_path):
    """Une autre session a poussé : les commits de celle-ci se rebasent dessus."""
    distant, session = atelier
    mienne = commiter(session, "mienne.txt")

    autre = tmp_path / "autre"
    subprocess.run(["git", "clone", "--quiet", str(distant), str(autre)], check=True)
    git(autre, "config", "user.email", "autre@exemple.fr")
    git(autre, "config", "user.name", "Autre")
    sienne = commiter(autre, "sienne.txt")
    git(autre, "push", "--quiet", "origin", "main")

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    journal = git(session, "log", "--format=%H", "-2")
    assert sienne in journal, "le commit de l'autre session est dessous"
    assert mienne not in journal, "le mien a été rebasé, donc réécrit"
    assert tete_distante(distant, "main") == git(session, "rev-parse", "HEAD")


def test_l_adresse_noreply_du_compte_github_passe(atelier):
    """L'adresse que GitHub attribue au compte ne désigne personne : elle part."""
    distant, session = atelier
    git(session, "config", "user.email", "240225789+g-pliberal@users.noreply.github.com")
    tete = commiter(session, "travail.txt")

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert tete_distante(distant, "main") == tete


# -- ce qu'il refuse ----------------------------------------------------------


def test_il_refuse_une_adresse_nominative_sans_rien_pousser(atelier):
    """Une adresse publiée ne s'efface qu'en réécrivant l'historique entier."""
    distant, session = atelier
    avant = tete_distante(distant, "main")
    git(session, "config", "user.email", "prenom.nom@exemple.fr")
    commiter(session, "travail.txt")

    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "adresse nominative" in acheve.stderr
    assert tete_distante(distant, "main") == avant, "rien poussé"


def test_il_refuse_le_committer_nominatif_que_son_rebasage_a_pose(atelier, tmp_path):
    """Un rebasage réécrit le committer à l'identité du poste : un commit signé
    d'une session web en ressort signé du poste, et ne doit pas partir."""
    distant, session = atelier
    commiter(session, "mienne.txt")

    autre = tmp_path / "autre"
    subprocess.run(["git", "clone", "--quiet", str(distant), str(autre)], check=True)
    git(autre, "config", "user.email", "autre@exemple.fr")
    git(autre, "config", "user.name", "Autre")
    sienne = commiter(autre, "sienne.txt")
    git(autre, "push", "--quiet", "origin", "main")

    git(session, "config", "user.email", "prenom.nom@exemple.fr")
    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "adresse nominative" in acheve.stderr
    assert tete_distante(distant, "main") == sienne, "rien poussé"
    assert git(session, "log", "-1", "--format=%ae %ce") == (
        "noreply@anthropic.com prenom.nom@exemple.fr"
    ), "l'auteur est resté, le committer est devenu le poste"


def test_il_refuse_sans_ancetre_commun(atelier, tmp_path):
    """Le cas grave de CLAUDE.md : deux lignées étrangères, rien n'est poussé."""
    distant, session = atelier
    avant = tete_distante(distant, "main")

    git(session, "checkout", "--quiet", "--orphan", "claude/orpheline")
    git(session, "rm", "--quiet", "-rf", ".")
    commiter(session, "etrangere.txt")

    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "aucun ancêtre commun" in acheve.stderr
    assert tete_distante(distant, "main") == avant, "rien poussé"


def test_il_refuse_un_conflit_de_rebasage_sans_rien_pousser(atelier, tmp_path):
    """Un conflit se résout à la main : le script ne devine pas à notre place."""
    distant, session = atelier
    commiter(session, "partage.txt", "version de la session")

    autre = tmp_path / "autre"
    subprocess.run(["git", "clone", "--quiet", str(distant), str(autre)], check=True)
    git(autre, "config", "user.email", "autre@exemple.fr")
    git(autre, "config", "user.name", "Autre")
    attendu = commiter(autre, "partage.txt", "version de l'autre")
    git(autre, "push", "--quiet", "origin", "main")

    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "conflit" in acheve.stderr
    assert tete_distante(distant, "main") == attendu, "rien poussé"
    assert git(session, "status", "--porcelain") == "", "le rebasage a été abandonné"


# -- la tête détachée ---------------------------------------------------------


def test_il_refuse_un_commit_qui_change_le_code_sans_test(atelier):
    """Le test d'abord (CLAUDE.md, action 162) : le code ne part qu'avec son
    test, et le refus nomme le commit et dit comment déclarer un remaniement."""
    distant, session = atelier
    avant = tete_distante(distant, "main")
    _envoyer(session, "le taux passe à deux", {"src/regle.py": "TAUX = 2\n"})

    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "sans toucher aux tests" in acheve.stderr
    assert "le taux passe à deux" in acheve.stderr and "Sans-test:" in acheve.stderr
    assert tete_distante(distant, "main") == avant, "rien poussé"


@pytest.mark.parametrize("message, fichiers", [
    ("le taux et son test", {"src/regle.py": "TAUX = 2\n",
                             "tests/test_regle.py": "def test_taux():\n    pass\n"}),
    ("un commentaire\n\nSans-test: un commentaire, rien ne change",
     {"src/regle.py": "TAUX = 1  # le taux\n"}),
])
def test_le_code_part_avec_son_test_ou_sa_declaration(atelier, message, fichiers):
    distant, session = atelier
    tete = _envoyer(session, message, fichiers)

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert tete_distante(distant, "main") == tete


@pytest.mark.parametrize("fichiers", [
    {".github/workflows/tests.yml": "on: push\n"},
    {".claude/settings.json": "{}\n"},
    {".claude/hooks/tdd.py": "# le hook\n", "tests/test_hook.py": "def test_x():\n    pass\n"},
    {"scripts/pousser.sh": "# l'envoi\n", "tests/test_envoi.py": "def test_x():\n    pass\n"},
    {"scripts/publier_fabrique.sh": "# le verdict\n",
     "tests/test_envoi.py": "def test_x():\n    pass\n"},
    {"scripts/publier_inscription.sh": "# l'inscription\n",
     "tests/test_envoi.py": "def test_x():\n    pass\n"},
])
def test_une_garde_ne_change_qu_avec_sa_declaration(atelier, fichiers):
    """Les gardes du dépôt — les workflows de GitHub, les hooks et leurs
    réglages, ce script, ceux qui publient le verdict et l'inscription, qui
    poussent sur main depuis GitHub (action 184) — ne changent qu'avec
    l'accord du propriétaire, demandé avant (action 163, étape 6). Un commit
    qui en touche une le déclare par une ligne ``Garde-modifiée: <raison>`` ;
    sinon rien ne part, et le refus nomme le commit et la garde."""
    distant, session = atelier
    avant = tete_distante(distant, "main")
    _envoyer(session, "une garde retouchée", fichiers)

    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "une garde retouchée" in acheve.stderr and "Garde-modifiée:" in acheve.stderr
    assert next(iter(fichiers)) in acheve.stderr
    assert tete_distante(distant, "main") == avant, "rien poussé"

    git(session, "commit", "--quiet", "--amend", "-m",
        "une garde retouchée\n\nGarde-modifiée: le propriétaire l'a demandé")
    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr


#: Les deux tests de la feuille de route, réduits à ce que l'atelier peut tenir :
#: le premier exige le bloc « Reprise ».
_PROSE = '''from pathlib import Path


def test_chaque_action_en_cours_s_ouvre_sur_son_bloc_reprise():
    assert "**Reprise" in Path("docs/feuille_de_route.md").read_text(encoding="utf-8")


def test_les_notes_de_la_feuille_de_route_se_rangent_par_action():
    pass
'''


def test_il_refuse_une_feuille_de_route_qui_ne_tient_pas_ses_regles(atelier):
    """Six rouges de main, du 6 au 17 octobre 2026, venaient du bloc « Reprise »,
    que la session écrit au dernier commit, après ses tests (action 163,
    étape 2). Quand un commit à publier touche la feuille de route ou ses
    notes, leurs deux tests se jouent à l'envoi : rouges, rien ne part. Un
    envoi qui n'y touche pas ne les joue pas."""
    distant, session = atelier
    _envoyer(session, "les tests de la prose", {"tests/test_prose.py": _PROSE})
    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr

    avant = tete_distante(distant, "main")
    _envoyer(session, "une action sans son bloc",
             {"docs/feuille_de_route.md": "### 1. Une action — `en cours`\n\nRien.\n"})
    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "feuille de route" in acheve.stderr
    assert "test_chaque_action_en_cours_s_ouvre_sur_son_bloc_reprise" in acheve.stderr
    assert tete_distante(distant, "main") == avant, "rien poussé"

    tete = _envoyer(session, "le bloc", {"docs/feuille_de_route.md":
                                         "### 1. Une action — `en cours`\n\n"
                                         "**Reprise, au 17 octobre 2026.** Tout.\n"})
    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert tete_distante(distant, "main") == tete


#: Un test qui garde un fichier commun, à la façon d'un cliquet : le nombre de
#: valeurs ne passe pas deux.
_COMMUN = '''from pathlib import Path


def test_le_compteur_ne_peut_que_baisser():
    assert len(list(Path("valeurs").iterdir())) <= 2
'''


def _poser_le_filet(session: Path) -> None:
    _envoyer(session, "le filet et son test", {
        "tests/test_commun.py": _COMMUN,
        "tests/filet_avant_envoi.txt": "# un lot par ligne\ntests/test_commun.py\n",
        "valeurs/a.txt": "a",
        # Ce que pytest laisse derrière lui ne se commite pas.
        ".gitignore": "__pycache__/\n",
    })
    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr


def test_il_refuse_deux_chantiers_verts_seuls_et_rouges_reunis(atelier, tmp_path):
    """Le 19 novembre 2026, deux chantiers, verts chacun de son côté, ont
    porté ensemble un compteur à 1 445 valeurs quand son cliquet en admettait
    1 442 : `main` est resté rouge 38 minutes, le temps d'une course de
    GitHub et de la réparation. Avant d'envoyer, le travail des autres
    rattrapé, le script joue les tests que nomme
    `tests/filet_avant_envoi.txt`, ceux des fichiers que tous les chantiers
    écrivent : rouges, rien ne part."""
    distant, session = atelier
    _poser_le_filet(session)
    _autre_session_pousse(distant, tmp_path, "valeurs/b.txt")
    avant = tete_distante(distant, "main")

    _envoyer(session, "une valeur de plus", {"valeurs/c.txt": "c",
                                             "tests/test_valeur.py": "# c\n"})
    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "filet" in acheve.stderr
    assert "test_le_compteur_ne_peut_que_baisser" in acheve.stderr
    assert tete_distante(distant, "main") == avant, "rien poussé"

    tete = _envoyer(session, "le cliquet suit", {
        "tests/test_commun.py": _COMMUN.replace("<= 2", "<= 3")})
    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert tete_distante(distant, "main") == tete


def test_le_filet_ne_se_joue_pas_pour_la_seule_documentation(atelier, tmp_path):
    """Une note de feuille de route ne déplace aucun compteur : elle part sans
    attendre le filet, même sur un `main` qu'un autre a laissé rouge."""
    distant, session = atelier
    _poser_le_filet(session)
    _autre_session_pousse(distant, tmp_path, "valeurs/b.txt")
    _autre_session_pousse(distant, tmp_path / "encore", "valeurs/c.txt")

    _envoyer(session, "une note", {"docs/note.md": "Une note.\n"})
    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert git(distant, "show", "main:docs/note.md") == "Une note."


def _autre_session_pousse(distant: Path, tmp_path: Path, nom: str, texte: str = "x") -> str:
    autre = tmp_path / "autre"
    subprocess.run(["git", "clone", "--quiet", str(distant), str(autre)], check=True)
    git(autre, "config", "user.email", "autre@exemple.fr")
    git(autre, "config", "user.name", "Autre")
    sienne = commiter(autre, nom, texte)
    git(autre, "push", "--quiet", "origin", "main")
    return sienne


def test_une_tete_detachee_publie_sur_main(atelier):
    """Une session créée par une autre part détachée : elle publie quand même,
    et le script ne crée aucune branche, faute d'en avoir une à faire suivre."""
    distant, session = atelier
    git(session, "checkout", "--quiet", "--detach")
    tete = commiter(session, "travail.txt")

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert "main ←" in acheve.stdout
    assert tete_distante(distant, "main") == tete
    assert git(session, "rev-parse", "--abbrev-ref", "HEAD") == "HEAD", "toujours détachée"
    assert git(distant, "for-each-ref", "--format=%(refname)", "refs/heads") == "refs/heads/main"

    relance = pousser(session)
    assert relance.returncode == 0, relance.stderr
    assert relance.stdout.strip() == ""


def test_une_tete_detachee_se_rebase_sur_main(atelier, tmp_path):
    distant, session = atelier
    git(session, "checkout", "--quiet", "--detach")
    commiter(session, "mienne.txt")
    sienne = _autre_session_pousse(distant, tmp_path, "sienne.txt")

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert git(session, "rev-parse", "HEAD~1") == sienne
    assert tete_distante(distant, "main") == git(session, "rev-parse", "HEAD")


def test_une_tete_detachee_garde_les_refus(atelier, tmp_path):
    """Détachée, elle refuse ce que refuse une branche : ici un conflit."""
    distant, session = atelier
    git(session, "checkout", "--quiet", "--detach")
    commiter(session, "partage.txt", "version de la session")
    attendu = _autre_session_pousse(distant, tmp_path, "partage.txt", "version de l'autre")

    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "conflit" in acheve.stderr
    assert tete_distante(distant, "main") == attendu, "rien poussé"


def test_une_tete_detachee_refuse_une_adresse_nominative(atelier):
    distant, session = atelier
    avant = tete_distante(distant, "main")
    git(session, "checkout", "--quiet", "--detach")
    git(session, "config", "user.email", "prenom.nom@exemple.fr")
    commiter(session, "travail.txt")

    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "adresse nominative" in acheve.stderr
    assert tete_distante(distant, "main") == avant, "rien poussé"


# -- la retenue : enregistrer sans publier ------------------------------------


def references_distantes(distant: Path) -> str:
    return git(distant, "for-each-ref", "--format=%(refname) %(objectname)")


def test_un_travail_retenu_ne_part_pas_a_la_fin_du_tour(atelier):
    """Le cas dangereux : un chantier qui attend son tour commite et retient ;
    le hook `Stop` relance le script nu à chaque fin de tour, et rien ne doit
    partir, ni sur `main` ni sur aucune référence de GitHub. Le travail reste
    dans le dépôt local, la retenue hors de tout commit."""
    distant, session = atelier
    avant = tete_distante(distant, "main")
    refs = references_distantes(distant)
    tete = commiter(session, "travail.txt")

    retenir = pousser(session, "--retenir", "attend la relecture")
    assert retenir.returncode == 0, retenir.stderr
    for _ in range(2):
        tour = pousser(session)
        assert tour.returncode == 0, tour.stderr
        assert "retenu" in tour.stdout and "attend la relecture" in tour.stdout
        assert "1 commit" in tour.stdout
    assert tete_distante(distant, "main") == avant, "rien publié"
    assert references_distantes(distant) == refs, "aucune branche ni référence créée"
    assert git(session, "rev-parse", "HEAD") == tete, "le travail est toujours là"
    assert git(session, "status", "--porcelain") == "", "la retenue n'est pas un fichier suivi"


def test_lever_la_retenue_publie_sur_main(atelier):
    distant, session = atelier
    tete = commiter(session, "travail.txt")
    assert pousser(session, "--retenir", "attend son tour").returncode == 0

    lever = pousser(session, "--lever")
    assert lever.returncode == 0, lever.stderr
    assert "main ←" in lever.stdout
    assert tete_distante(distant, "main") == tete
    assert pousser(session).stdout.strip() == "", "la retenue est levée pour de bon"


def test_lever_garde_les_refus_et_la_retenue(atelier):
    """Lever passe par toutes les vérifications ; refusé, rien ne part, et la
    retenue tient : le tour suivant ne publie pas en douce la version réparée."""
    distant, session = atelier
    avant = tete_distante(distant, "main")
    git(session, "config", "user.email", "prenom.nom@exemple.fr")
    commiter(session, "travail.txt")
    assert pousser(session, "--retenir", "attend son tour").returncode == 0

    lever = pousser(session, "--lever")
    assert lever.returncode != 0
    assert "adresse nominative" in lever.stderr
    assert tete_distante(distant, "main") == avant
    git(session, "config", "user.email", "noreply@anthropic.com")
    git(session, "commit", "--quiet", "--amend", "--no-edit", "--reset-author")
    assert "retenu" in pousser(session).stdout
    assert tete_distante(distant, "main") == avant, "toujours retenu"


def test_une_retenue_dit_sa_raison(atelier):
    """Une option mal écrite ne publie rien et ne retient rien : elle refuse."""
    distant, session = atelier
    avant = tete_distante(distant, "main")
    commiter(session, "travail.txt")
    for options in (["--retenir"], ["--retenir", "  "], ["--inconnue"],
                    ["--lever", "--retenir", "x"]):
        acheve = pousser(session, *options)
        assert acheve.returncode != 0, options
        assert tete_distante(distant, "main") == avant, options
    assert "raison" in pousser(session, "--retenir").stderr
    assert not (session / ".git" / "retenue").exists()


def test_un_worktree_voit_la_retenue_du_depot(atelier, tmp_path):
    """Un agent isolé dans un worktree part du `HEAD` retenu : la retenue vaut
    pour tout le dépôt, pas pour le seul répertoire où elle a été posée."""
    distant, session = atelier
    avant = tete_distante(distant, "main")
    commiter(session, "travail.txt")
    assert pousser(session, "--retenir", "attend son tour").returncode == 0
    arbre = tmp_path / "arbre"
    git(session, "worktree", "add", "--quiet", "-b", "agent", str(arbre))

    acheve = pousser(arbre)
    assert acheve.returncode == 0, acheve.stderr
    assert "retenu" in acheve.stdout
    assert tete_distante(distant, "main") == avant


def test_lever_sans_rien_a_publier_ote_la_retenue(atelier):
    _, session = atelier
    assert pousser(session, "--retenir", "rien encore").returncode == 0
    lever = pousser(session, "--lever")
    assert lever.returncode == 0, lever.stderr
    assert pousser(session).stdout.strip() == ""


def test_une_tete_detachee_se_retient_aussi(atelier):
    distant, session = atelier
    avant = tete_distante(distant, "main")
    git(session, "checkout", "--quiet", "--detach")
    commiter(session, "travail.txt")
    assert pousser(session, "--retenir", "attend son tour").returncode == 0
    assert "retenu" in pousser(session).stdout
    assert tete_distante(distant, "main") == avant
    assert pousser(session, "--lever").returncode == 0
    assert tete_distante(distant, "main") == git(session, "rev-parse", "HEAD")


# -- le compteur de commits « non poussés » -----------------------------------


def test_la_branche_locale_recoit_origin_main_pour_amont(atelier):
    """Sans amont, le compteur compare à un point fixe et monte à chaque commit."""
    _, session = atelier
    commiter(session, "travail.txt")
    assert pousser(session).returncode == 0

    amont = git(session, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    assert amont == "origin/main"
    assert git(session, "rev-list", "--count", "@{upstream}..HEAD") == "0"


def test_la_reference_de_suivi_d_une_branche_supprimee_est_nettoyee(atelier):
    """Le fantôme : la branche n'est plus sur GitHub, son pointeur local survit.

    C'est ce qui faisait remonter le compteur MALGRÉ le script. Les branches
    `claude/*` se suppriment à la main depuis GitHub — une session ne peut pas,
    elle reçoit un 403 — et la référence de suivi locale, elle, reste figée sur
    le commit du clone. Tout ce qui compte ``origin/<branche>..HEAD`` lit alors
    une branche entière de retard sur quelque chose qui n'existe plus.

    Le script supprime ce pointeur, et le geste est purement local : il ne crée
    ni n'efface rien sur le distant.
    """
    distant, session = atelier
    branche = "claude/essai"

    # La branche a existé sur le distant, puis a été supprimée à la main.
    git(session, "push", "--quiet", "origin", f"HEAD:refs/heads/{branche}")
    git(session, "fetch", "--quiet", "origin")
    fantome = git(session, "rev-parse", f"refs/remotes/origin/{branche}")
    git(distant, "update-ref", "-d", f"refs/heads/{branche}")

    commiter(session, "un.txt")
    commiter(session, "deux.txt")
    assert git(session, "rev-parse", f"refs/remotes/origin/{branche}") == fantome
    assert git(session, "rev-list", "--count",
               f"refs/remotes/origin/{branche}..HEAD") == "2", "le compteur ment"

    assert pousser(session).returncode == 0

    reste = subprocess.run(
        ["git", "rev-parse", "--quiet", "--verify", f"refs/remotes/origin/{branche}"],
        cwd=session, capture_output=True, text=True, encoding="utf-8",
    )
    assert reste.returncode != 0, "le pointeur de suivi du fantôme est supprimé"
    assert git(session, "rev-list", "--count", "@{upstream}..HEAD") == "0"


def test_la_reference_de_suivi_vivante_est_conservee_et_suit(atelier):
    """Quand la branche existe encore, on la fait suivre au lieu de l'oublier."""
    distant, session = atelier
    branche = "claude/essai"
    git(session, "push", "--quiet", "origin", f"HEAD:refs/heads/{branche}")

    tete = commiter(session, "travail.txt")
    assert pousser(session).returncode == 0

    assert tete_distante(distant, branche) == tete, "la branche suit ce que main porte"
    assert git(session, "rev-list", "--count",
               f"refs/remotes/origin/{branche}..HEAD") == "0"


# -- les fichiers fabriqués, que GitHub refait (action 148) --------------------


def _marquer_fabrique(distant: Path, tmp_path: Path) -> Path:
    """Pose, sur main, un ``.gitattributes`` qui marque ``fabrique.json``
    ``-merge``, comme le dépôt marque ses fichiers fabriqués ; rend un second
    clone, l'autre session."""
    autre = tmp_path / "autre"
    subprocess.run(["git", "clone", "--quiet", str(distant), str(autre)], check=True)
    git(autre, "config", "user.email", "autre@exemple.fr")
    git(autre, "config", "user.name", "Autre")
    commiter(autre, ".gitattributes", "fabrique.json -merge\n")
    commiter(autre, "fabrique.json", "{}\n")
    git(autre, "push", "--quiet", "origin", "main")
    return autre


def _preparer(atelier, tmp_path):
    distant, session = atelier
    autre = _marquer_fabrique(distant, tmp_path)
    git(session, "pull", "--quiet", "--rebase", "origin", "main")
    return distant, session, autre


def test_un_conflit_sur_un_fichier_fabrique_garde_la_version_de_main(atelier, tmp_path):
    """Deux sessions changent le modèle et refabriquent : la seconde passe,
    avec la version de main ; GitHub refera le fichier."""
    distant, session, autre = _preparer(atelier, tmp_path)
    (session / "source.py").write_text("ma règle\n", encoding="utf-8")
    (session / "fabrique.json").write_text('{"session": 1}\n', encoding="utf-8")
    git(session, "add", "-A")
    git(session, "commit", "--quiet", "-m", "le modèle change, refabriqué")
    commiter(autre, "fabrique.json", '{"autre": 1}\n')
    git(autre, "push", "--quiet", "origin", "main")

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    tete = tete_distante(distant, "main")
    assert tete == git(session, "rev-parse", "HEAD")
    assert git(session, "show", f"{tete}:fabrique.json") == '{"autre": 1}'
    assert git(session, "show", f"{tete}:source.py") == "ma règle"
    assert git(session, "status", "--porcelain") == ""


#: Le script du paquet, dans l'atelier : il réunit les règles en un paquet,
#: comme ``construire_donnees.py`` réunit les données ; ``PAQUET_EN_PANNE``
#: le fait échouer, comme un hook interrompu ou une donnée illisible.
CONSTRUIRE = """import json, os, pathlib, sys
if os.environ.get("PAQUET_EN_PANNE"):
    sys.exit(1)
regles = sorted(p.read_text().strip() for p in pathlib.Path("regles").glob("*.yaml"))
pathlib.Path("moteur/donnees.json").write_text(json.dumps(regles) + "\\n")
"""


def _poser_le_paquet(atelier, tmp_path):
    """Pose sur main un paquet que ``.gitattributes`` marque
    ``refaire=<son script>``, le script, et une règle ; rend l'autre session."""
    distant, session = atelier
    autre = _marquer_fabrique(distant, tmp_path)
    for nom, texte in ((".gitattributes", "fabrique.json -merge\n"
                        "moteur/donnees.json -merge refaire=scripts/construire_donnees.py\n"),
                       ("scripts/construire_donnees.py", CONSTRUIRE),
                       ("regles/base.yaml", "base\n"),
                       ("moteur/donnees.json", '["base"]\n')):
        ecrire(autre, nom, texte)
    git(autre, "add", "-A")
    git(autre, "commit", "--quiet", "-m", "le paquet et son script")
    git(autre, "push", "--quiet", "origin", "main")
    git(session, "pull", "--quiet", "--rebase", "origin", "main")
    return distant, session, autre


def en_panne_de_paquet(depot: Path) -> subprocess.CompletedProcess:
    """``pousser.sh``, le script du paquet en échec."""
    return subprocess.run(["env", "PAQUET_EN_PANNE=1", "bash", str(SCRIPT)], cwd=depot,
                          capture_output=True, text=True, encoding="utf-8")


def _corriger(depot: Path, regle: str) -> str:
    """Une correction et son paquet refait, comme une session les commite."""
    ecrire(depot, f"regles/{regle}.yaml", f"{regle}\n")
    subprocess.run(["python3", "scripts/construire_donnees.py"], cwd=depot, check=True)
    git(depot, "add", "-A")
    git(depot, "commit", "--quiet", "-m", f"la règle {regle}, son paquet refait")
    return git(depot, "rev-parse", "HEAD")


def test_une_correction_part_avec_le_paquet_des_sources_reunies(atelier, tmp_path):
    """Les deux moteurs lisent leurs règles au paquet : une correction publiée
    avec le paquet d'une autre session laisserait sur main le test de la
    correction rouge, jusqu'au commit où GitHub refait le paquet (le
    14 novembre 2026, quatre fois, file de l'action 130). Le rebasage garde
    celui de main, puis le script que ``.gitattributes`` nomme le refait des
    sources réunies, dans le dernier commit de la session : les deux
    corrections partent, chacune dans le paquet."""
    distant, session, autre = _poser_le_paquet(atelier, tmp_path)
    _corriger(session, "cipav")
    _corriger(autre, "carmf")
    git(autre, "push", "--quiet", "origin", "main")

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    tete = tete_distante(distant, "main")
    assert tete == git(session, "rev-parse", "HEAD")
    assert git(session, "show", f"{tete}:moteur/donnees.json") == '["base", "carmf", "cipav"]'
    assert git(session, "show", f"{tete}:regles/cipav.yaml") == "cipav"
    assert git(session, "rev-list", "--count", "origin/main~1..HEAD") == "1", \
        "le paquet refait entre dans le dernier commit, sans commit de plus"
    assert git(session, "status", "--porcelain") == ""


def test_un_paquet_qui_n_a_pas_pu_etre_refait_ne_part_pas(atelier, tmp_path):
    """Le cas dangereux : le rebasage a gardé le paquet de main, et le script
    échoue, ou le hook est interrompu pendant qu'il tourne. Rien ne part, pas
    même au tour suivant, tant que le paquet n'a pas été refait ; le tour
    suivant le refait, puis publie."""
    distant, session, autre = _poser_le_paquet(atelier, tmp_path)
    _corriger(session, "cipav")
    _corriger(autre, "carmf")
    git(autre, "push", "--quiet", "origin", "main")
    attendu = tete_distante(distant, "main")

    en_panne = en_panne_de_paquet(session)
    assert en_panne.returncode != 0
    assert "scripts/construire_donnees.py" in en_panne.stderr
    assert tete_distante(distant, "main") == attendu, "rien poussé"
    assert git(session, "show", "HEAD:moteur/donnees.json") == '["base", "carmf"]', \
        "le rebasage est fait, le paquet de main encore là"

    encore = en_panne_de_paquet(session)
    assert encore.returncode != 0
    assert tete_distante(distant, "main") == attendu, "le tour suivant ne publie pas non plus"

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert git(session, "show", f"{tete_distante(distant, 'main')}:moteur/donnees.json") == \
        '["base", "carmf", "cipav"]'


def test_un_paquet_a_refaire_attend_que_le_repertoire_soit_propre(atelier, tmp_path):
    """Le script lit le répertoire de travail : une source modifiée sans être
    commitée entrerait dans le paquet du commit. Il attend qu'elle le soit."""
    distant, session, autre = _poser_le_paquet(atelier, tmp_path)
    _corriger(session, "cipav")
    _corriger(autre, "carmf")
    git(autre, "push", "--quiet", "origin", "main")
    attendu = tete_distante(distant, "main")
    assert en_panne_de_paquet(session).returncode != 0
    ecrire(session, "regles/cipav.yaml", "cipav retouchée\n")

    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "commit" in acheve.stderr
    assert tete_distante(distant, "main") == attendu, "rien poussé"


def test_un_commit_qui_ne_portait_que_du_fabrique_disparait(atelier, tmp_path):
    distant, session, autre = _preparer(atelier, tmp_path)
    commiter(session, "source.py", "ma règle\n")
    commiter(session, "fabrique.json", '{"session": 1}\n')
    attendu = commiter(autre, "fabrique.json", '{"autre": 1}\n')
    git(autre, "push", "--quiet", "origin", "main")

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert git(session, "rev-parse", "HEAD~1") == attendu, "le commit vide est sauté"
    assert git(session, "show", "HEAD:fabrique.json") == '{"autre": 1}'


def test_un_conflit_sur_une_source_refuse_meme_avec_du_fabrique(atelier, tmp_path):
    distant, session, autre = _preparer(atelier, tmp_path)
    (session / "source.py").write_text("ma règle\n", encoding="utf-8")
    (session / "fabrique.json").write_text('{"session": 1}\n', encoding="utf-8")
    git(session, "add", "-A")
    git(session, "commit", "--quiet", "-m", "le modèle change")
    (autre / "source.py").write_text("sa règle\n", encoding="utf-8")
    (autre / "fabrique.json").write_text('{"autre": 1}\n', encoding="utf-8")
    git(autre, "add", "-A")
    git(autre, "commit", "--quiet", "-m", "le modèle change autrement")
    attendu = git(autre, "rev-parse", "HEAD")
    git(autre, "push", "--quiet", "origin", "main")

    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "conflit" in acheve.stderr
    assert tete_distante(distant, "main") == attendu, "rien poussé"
    assert git(session, "status", "--porcelain") == "", "le rebasage a été abandonné"


def test_l_adresse_du_robot_de_github_passe(atelier):
    """Le commit fabriqué par GitHub (tests.yml) signe de l'adresse noreply de
    son robot : elle ne désigne personne."""
    distant, session = atelier
    git(session, "config", "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com")
    tete = commiter(session, "fabrique.txt")
    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert tete_distante(distant, "main") == tete


# -- la prose et la référence de la conservation, que deux pilotes fusionnent
# (scripts/fusionner.py, action 148, étape 3) ----------------------------------

REFERENCE = "tests/temoins/conservation.json"


def ecrire(depot: Path, nom: str, texte: str) -> None:
    chemin = depot / nom
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_bytes(texte.encode("utf-8"))


def paquet(valeur: str, phrase: str = "Le paquet pèse") -> str:
    return (f"# Le site\n\n{phrase} <!--chiffre:poids(moteur/donnees.json)-->{valeur}"
            "<!--/--> Ko.\n\nUne autre phrase.\n")


def journal(*cles: str) -> str:
    """La référence de la conservation, écrite comme ``--figer`` l'écrit."""
    lignes = ",\n".join(f'   "{cle}"' for cle in cles)
    return f'{{\n "entrees": {{\n  "journal": [\n{lignes}\n  ]\n }}\n}}\n'


def _poser_les_pilotes(atelier, tmp_path):
    """Pose sur main le ``.gitattributes`` du dépôt pour la prose et la
    référence, un README à chiffre ancré et une référence ; rend le second
    clone, l'autre session."""
    distant, session = atelier
    autre = tmp_path / "autre"
    subprocess.run(["git", "clone", "--quiet", str(distant), str(autre)], check=True)
    git(autre, "config", "user.email", "autre@exemple.fr")
    git(autre, "config", "user.name", "Autre")
    ecrire(autre, ".gitattributes", f"*.md merge=ancres\n{REFERENCE} merge=ensembles\n")
    ecrire(autre, "README.md", paquet("100"))
    ecrire(autre, REFERENCE, journal("2026-10-06 | a"))
    git(autre, "add", "-A")
    git(autre, "commit", "--quiet", "-m", "les pilotes")
    git(autre, "push", "--quiet", "origin", "main")
    git(session, "pull", "--quiet", "--rebase", "origin", "main")
    return distant, session, autre


def _envoyer(depot: Path, message: str, fichiers: dict[str, str]) -> str:
    for nom, texte in fichiers.items():
        ecrire(depot, nom, texte)
    git(depot, "add", "-A")
    git(depot, "commit", "--quiet", "-m", message)
    return git(depot, "rev-parse", "HEAD")


def test_un_conflit_sur_les_seuls_chiffres_ancres_garde_ceux_de_main(atelier, tmp_path):
    """Deux sessions changent le modèle et récrivent la même ancre, chacune à sa
    valeur : la seconde passe, avec la valeur de main, que GitHub refera."""
    distant, session, autre = _poser_les_pilotes(atelier, tmp_path)
    _envoyer(session, "le modèle change", {"source.py": "ma règle\n", "README.md": paquet("120")})
    _envoyer(autre, "le modèle change autrement", {"README.md": paquet("110")})
    git(autre, "push", "--quiet", "origin", "main")

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    tete = tete_distante(distant, "main")
    assert tete == git(session, "rev-parse", "HEAD")
    assert git(session, "show", f"{tete}:README.md") == paquet("110").strip()
    assert git(session, "show", f"{tete}:source.py") == "ma règle"
    assert git(session, "status", "--porcelain") == ""


def test_un_conflit_de_prose_refuse_toujours(atelier, tmp_path):
    """Ce qui s'écrit à la main ne se devine pas : le conflit reste un conflit."""
    distant, session, autre = _poser_les_pilotes(atelier, tmp_path)
    _envoyer(session, "ma phrase", {"README.md": paquet("120", "Le paquet du site pèse")})
    attendu = _envoyer(autre, "sa phrase",
                       {"README.md": paquet("110", "Le paquet compressé pèse")})
    git(autre, "push", "--quiet", "origin", "main")

    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "conflit" in acheve.stderr
    assert tete_distante(distant, "main") == attendu, "rien poussé"
    assert git(session, "status", "--porcelain") == "", "le rebasage a été abandonné"


def test_deux_refigements_de_la_conservation_se_fusionnent(atelier, tmp_path):
    """Deux sessions refigent la référence le même jour, et y ajoutent chacune
    son entrée du journal au même endroit : les deux restent."""
    distant, session, autre = _poser_les_pilotes(atelier, tmp_path)
    _envoyer(session, "ma veille", {REFERENCE: journal("2026-10-06 | a", "2026-10-06 | b")})
    _envoyer(autre, "sa veille", {REFERENCE: journal("2026-10-06 | a", "2026-10-06 | c")})
    git(autre, "push", "--quiet", "origin", "main")

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    tete = tete_distante(distant, "main")
    assert git(session, "show", f"{tete}:{REFERENCE}") == journal(
        "2026-10-06 | a", "2026-10-06 | b", "2026-10-06 | c").strip()


# -- les témoins rangés par cas, fusionnés entrée par entrée (pilote `cles`) ------

TEMOIN = "tests/temoins/simulations.json"


def cas(**pensions: float) -> str:
    """Un témoin par cas, écrit comme ``construire_temoins.py`` l'écrit : une
    ligne par cas, pour que deux cas voisins fassent buter la fusion de git."""
    lignes = ",\n".join(f' "{nom}": {valeur}' for nom, valeur in sorted(pensions.items()))
    return "{\n" + lignes + "\n}\n"


def _poser_le_temoin(atelier, tmp_path):
    distant, session = atelier
    autre = tmp_path / "autre"
    subprocess.run(["git", "clone", "--quiet", str(distant), str(autre)], check=True)
    git(autre, "config", "user.email", "autre@exemple.fr")
    git(autre, "config", "user.name", "Autre")
    ecrire(autre, ".gitattributes", f"{TEMOIN} merge=cles\n")
    ecrire(autre, TEMOIN, cas(cnav=1000.0, carmf=900.0, cipav=800.0))
    git(autre, "add", "-A")
    git(autre, "commit", "--quiet", "-m", "le témoin")
    git(autre, "push", "--quiet", "origin", "main")
    git(session, "pull", "--quiet", "--rebase", "origin", "main")
    return distant, session, autre


def test_deux_corrections_qui_deplacent_deux_cas_voisins_passent_toutes_deux(atelier, tmp_path):
    """Deux chantiers en parallèle : l'un corrige la CARMF, l'autre la CIPAV,
    et chacun refait le témoin. Le second publie après le premier, sans
    attendre son tour : les deux corrections et leurs deux cas restent."""
    distant, session, autre = _poser_le_temoin(atelier, tmp_path)
    _envoyer(session, "la CIPAV corrigée", {"cipav.py": "ma règle\n",
                                            TEMOIN: cas(cnav=1000.0, carmf=900.0, cipav=812.5)})
    _envoyer(autre, "la CARMF corrigée", {"carmf.py": "sa règle\n",
                                          TEMOIN: cas(cnav=1000.0, carmf=905.0, cipav=800.0)})
    git(autre, "push", "--quiet", "origin", "main")

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    tete = tete_distante(distant, "main")
    assert git(session, "show", f"{tete}:{TEMOIN}") == cas(
        cnav=1000.0, carmf=905.0, cipav=812.5).strip()
    assert git(session, "show", f"{tete}:cipav.py") == "ma règle"
    assert git(session, "show", f"{tete}:carmf.py") == "sa règle"


def test_un_meme_cas_deplace_par_deux_corrections_refuse(atelier, tmp_path):
    """Le cas dangereux : les deux corrections déplacent le même cas, chacune
    à sa valeur. Aucune n'est celle de leur réunion : rien ne part, et la
    session refait le témoin sur les sources réunies."""
    distant, session, autre = _poser_le_temoin(atelier, tmp_path)
    _envoyer(session, "la CNAV corrigée", {TEMOIN: cas(cnav=1010.0, carmf=900.0, cipav=800.0)})
    attendu = _envoyer(autre, "la CNAV corrigée autrement",
                       {TEMOIN: cas(cnav=1020.0, carmf=900.0, cipav=800.0)})
    git(autre, "push", "--quiet", "origin", "main")

    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "conflit" in acheve.stderr
    assert TEMOIN in acheve.stderr, "le refus nomme le témoin"
    assert "python scripts/construire_temoins.py" in acheve.stderr, \
        "et dit de refaire les témoins des sources réunies"
    assert tete_distante(distant, "main") == attendu, "rien poussé"
    assert git(session, "status", "--porcelain") == "", "le rebasage a été abandonné"


# -- les compteurs des cliquets (pilote `compteurs`) -----------------------------

CLIQUETS = "tests/test_cliquets_du_droit_date.py"


def compteur(valeur: int) -> str:
    return f'"""Les cliquets."""\n\n#: Les valeurs de repli.\nVALEURS_DE_REPLI = {valeur}\n'


def _poser_le_cliquet(atelier, tmp_path):
    distant, session = atelier
    autre = tmp_path / "autre"
    subprocess.run(["git", "clone", "--quiet", str(distant), str(autre)], check=True)
    git(autre, "config", "user.email", "autre@exemple.fr")
    git(autre, "config", "user.name", "Autre")
    ecrire(autre, ".gitattributes", f"{CLIQUETS} merge=compteurs\n")
    ecrire(autre, CLIQUETS, compteur(100))
    git(autre, "add", "-A")
    git(autre, "commit", "--quiet", "-m", "le cliquet")
    git(autre, "push", "--quiet", "origin", "main")
    git(session, "pull", "--quiet", "--rebase", "origin", "main")
    return distant, session, autre


def test_deux_chantiers_qui_abaissent_le_meme_cliquet_passent_tous_deux(atelier, tmp_path):
    distant, session, autre = _poser_le_cliquet(atelier, tmp_path)
    _envoyer(session, "cinq renvois retirés", {CLIQUETS: compteur(95)})
    _envoyer(autre, "trois renvois retirés", {CLIQUETS: compteur(97)})
    git(autre, "push", "--quiet", "origin", "main")

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert git(session, "show", f"{tete_distante(distant, 'main')}:{CLIQUETS}") == \
        compteur(92).strip()


def test_un_cliquet_qui_monte_d_un_cote_refuse(atelier, tmp_path):
    distant, session, autre = _poser_le_cliquet(atelier, tmp_path)
    _envoyer(session, "un renvoi de plus", {CLIQUETS: compteur(101)})
    attendu = _envoyer(autre, "trois renvois retirés", {CLIQUETS: compteur(97)})
    git(autre, "push", "--quiet", "origin", "main")

    acheve = pousser(session)
    assert acheve.returncode != 0
    assert "conflit" in acheve.stderr
    assert tete_distante(distant, "main") == attendu, "rien poussé"


def test_un_paquet_a_moitie_ecrit_par_un_hook_interrompu_se_refait(atelier, tmp_path):
    """Le hook de fin de tour a un temps compté : interrompu pendant le script,
    il laisse un paquet à moitié écrit. Le tour suivant le reprend de zéro."""
    distant, session, autre = _poser_le_paquet(atelier, tmp_path)
    _corriger(session, "cipav")
    _corriger(autre, "carmf")
    git(autre, "push", "--quiet", "origin", "main")
    assert en_panne_de_paquet(session).returncode != 0
    ecrire(session, "moteur/donnees.json", '["base", "car')

    acheve = pousser(session)
    assert acheve.returncode == 0, acheve.stderr
    assert git(session, "show", f"{tete_distante(distant, 'main')}:moteur/donnees.json") == \
        '["base", "carmf", "cipav"]'

