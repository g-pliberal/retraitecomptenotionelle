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


def pousser(depot: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(SCRIPT)], cwd=depot, capture_output=True, text=True,
        encoding="utf-8",
    )


def commiter(depot: Path, nom: str, texte: str = "x") -> str:
    (depot / nom).write_text(texte, encoding="utf-8")
    git(depot, "add", nom)
    git(depot, "commit", "--quiet", "-m", f"ajoute {nom}")
    return git(depot, "rev-parse", "HEAD")


@pytest.fixture
def atelier(tmp_path: Path) -> tuple[Path, Path]:
    """Un dépôt nu qui joue GitHub, et un clone posé sur une branche de session."""
    distant = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--quiet", "--bare", "--initial-branch=main",
                    str(distant)], check=True)

    amorce = tmp_path / "amorce"
    subprocess.run(["git", "clone", "--quiet", str(distant), str(amorce)], check=True)
    git(amorce, "config", "user.email", "essai@exemple.fr")
    git(amorce, "config", "user.name", "Essai")
    git(amorce, "checkout", "--quiet", "-B", "main")
    commiter(amorce, "depart.txt")
    git(amorce, "push", "--quiet", "origin", "main")

    session = tmp_path / "session"
    subprocess.run(["git", "clone", "--quiet", str(distant), str(session)], check=True)
    # L'identité d'une session web : la seule adresse qu'elle publie.
    git(session, "config", "user.email", "noreply@anthropic.com")
    git(session, "config", "user.name", "Claude")
    git(session, "checkout", "--quiet", "-b", "claude/essai")
    return distant, session


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
