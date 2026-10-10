#!/usr/bin/env python3
"""Ce que les sessions Claude Code consomment, et ce qui le leur coûte.

    python scripts/consommation.py                    # les sessions du poste, 30 jours
    python scripts/consommation.py --jours 7 --limite 20
    python scripts/consommation.py chemin/session.jsonl dossier/

Chaque appel au modèle relit tout son contexte : ce qui y entre est payé une
fois par appel qui suit, jusqu'à la fin de la session ou à la compaction qui
l'en retire. Le script lit les transcriptions (un fichier JSONL par session,
sous ``~/.claude/projects/<dossier de travail en tirets>/``, ses sous-agents
dans ``<session>/subagents/``) et attribue la croissance du contexte d'un
appel au suivant à ce qui est entré entre les deux : la sortie du modèle
(``output_tokens``), puis, au prorata de leur taille, les résultats d'outils,
les ajouts du harnais (rappels, hooks) et les messages de l'utilisateur.
Chaque part, multipliée par le nombre d'appels qui l'ont relue, donne ses
jetons relus ; leur somme est exactement celle des contextes de chaque
appel. Feuille de route, action 135, étape 1 du contexte.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shlex
import struct
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from retraite_notionnelle.somme import somme_ordonnee as additionner  # noqa: E402

#: Pour répartir une croissance entre les blocs entrés ensemble, et pour
#: détailler le contexte de départ : une estimation, que seule la somme
#: mesurée par l'API corrige.
CARACTERES_PAR_JETON = 3.5
#: Une image sans dimensions lisibles.
JETONS_PAR_IMAGE = 1600
#: Les entrées du harnais qui ne vont pas au modèle.
ATTACHEMENTS_MUETS = {"prompt_snapshot", "deferred_tools_record", "credential_org"}
#: Les commandes qui lisent un fichier, dont le nom suit.
LECTEURS = {"cat", "sed", "head", "tail", "less", "nl", "awk"}


@dataclass
class Part:
    """Ce qui est entré dans le contexte, et ce que cela a coûté."""

    categorie: str  # depart, sortie, outil, harnais, utilisateur
    etiquette: str  # « Read », « hook SessionStart:startup », « environment »…
    fichier: str | None = None
    commande: str | None = None
    estimation: float = 0.0  # jetons estimés, pour le prorata
    jetons: float = 0.0  # jetons attribués
    relu: float = 0.0  # jetons × appels qui l'ont relu


@dataclass
class Appel:
    contexte: int
    sortie: int


@dataclass
class Session:
    nom: str
    appels: list[Appel] = field(default_factory=list)
    parts: list[Part] = field(default_factory=list)
    compactions: int = 0
    cout: float | None = None

    @property
    def relu(self) -> float:
        return additionner(appel.contexte for appel in self.appels)


# --- L'estimation des blocs ------------------------------------------------


def _dimensions_d_image(donnees: str) -> tuple[int, int] | None:
    try:
        tete = base64.b64decode(donnees[:64] + "=" * (-len(donnees[:64]) % 4))
    except ValueError:
        return None
    if tete[:8] == b"\x89PNG\r\n\x1a\n" and len(tete) >= 24:
        return struct.unpack(">II", tete[16:24])
    return None


def estimer(contenu) -> float:
    """Les jetons d'un contenu de bloc : texte, liste de blocs ou image."""
    if contenu is None:
        return 0.0
    if isinstance(contenu, str):
        return len(contenu) / CARACTERES_PAR_JETON
    if isinstance(contenu, list):
        return additionner(estimer(bloc) for bloc in contenu)
    if isinstance(contenu, dict):
        if contenu.get("type") == "image":
            source = contenu.get("source") or {}
            dimensions = _dimensions_d_image(source.get("data", ""))
            if dimensions:
                return dimensions[0] * dimensions[1] / 750
            return JETONS_PAR_IMAGE
        if "text" in contenu:
            return estimer(contenu["text"])
        if "content" in contenu:
            return estimer(contenu["content"])
        return len(json.dumps(contenu, ensure_ascii=False)) / CARACTERES_PAR_JETON
    return len(str(contenu)) / CARACTERES_PAR_JETON


# --- Les étiquettes --------------------------------------------------------


def _relatif(chemin: str, dossier: str | None) -> str:
    if dossier and chemin.startswith(dossier.rstrip("/") + "/"):
        return chemin[len(dossier.rstrip("/")) + 1 :]
    return chemin


def _morceaux(commande: str) -> list[list[str]]:
    """Les commandes simples d'une ligne, séparées par ``&&``, ``;`` ou ``|``,
    sans leurs redirections ; les guillemets protègent ce qu'ils citent."""
    lexeur = shlex.shlex(commande, posix=True, punctuation_chars=True)
    lexeur.whitespace_split = True
    try:
        jetons = list(lexeur)
    except ValueError:
        jetons = commande.split()
    morceaux, courant, redirige = [], [], False
    for jeton in jetons:
        if jeton and set(jeton) <= set("&|;()"):
            morceaux.append(courant)
            courant, redirige = [], False
        elif jeton and set(jeton) <= set("<>&"):
            if courant and courant[-1].isdigit():
                courant.pop()  # le « 2 » de « 2>&1 »
            redirige = True
        elif redirige:
            redirige = False
        else:
            courant.append(jeton)
    return [morceau for morceau in morceaux + [courant] if morceau]


def decrire_commande(commande: str) -> tuple[str, str | None]:
    """La commande d'un appel Bash, réduite à son verbe, et le fichier qu'elle
    lit s'il y en a un : ``cd x && sed -n 1,9p a.py | tail`` → (« sed », a.py)."""
    for mots in _morceaux(commande):
        while mots and re.fullmatch(r"[A-Z_][A-Z0-9_]*=.*", mots[0]):
            mots = mots[1:]
        if not mots or mots[0] in {"cd", "export", "set", "source", "."}:
            continue
        verbe = os.path.basename(mots[0])
        reste = mots[1:]
        if verbe in {"python", "python3", "node", "bash", "sh", "uv"}:
            if reste[:1] == ["-m"] and len(reste) > 1:
                return f"{verbe} -m {reste[1]}", None
            scripts = [mot for mot in reste if not mot.startswith("-")]
            if scripts and not scripts[0].startswith("<"):
                return f"{verbe} {scripts[0]}", None
            return verbe, None
        if verbe in {"git", "npm", "pip"} and reste:
            sous = next((mot for mot in reste if not mot.startswith("-")), "")
            return f"{verbe} {sous}".strip(), None
        fichier = None
        if verbe in LECTEURS:
            arguments = [mot for mot in reste if not mot.startswith("-")]
            if verbe in {"sed", "awk"} and arguments and "-e" not in reste:
                arguments = arguments[1:]
            if arguments and not arguments[-1].startswith(("<", ">")):
                fichier = arguments[-1]
        return verbe, fichier
    return "(vide)", None


def decrire_outil(nom: str, entree: dict, dossier: str | None) -> tuple[str, str | None, str | None]:
    """(étiquette, fichier, commande) d'un appel d'outil."""
    if nom in {"Read", "NotebookRead"}:
        chemin = entree.get("file_path") or entree.get("notebook_path") or ""
        return nom, _relatif(chemin, dossier), None
    if nom == "Bash":
        verbe, fichier = decrire_commande(entree.get("command", ""))
        return nom, _relatif(fichier, dossier) if fichier else None, verbe
    if nom in {"Grep", "Glob"}:
        return nom, None, nom
    return nom, None, None


# --- La lecture d'une transcription ----------------------------------------


def _blocs(message) -> list:
    contenu = (message or {}).get("content")
    if isinstance(contenu, str):
        return [{"type": "text", "text": contenu}]
    return contenu or []


def _contexte(usage: dict) -> int:
    return (
        usage.get("input_tokens", 0)
        + usage.get("cache_creation_input_tokens", 0)
        + usage.get("cache_read_input_tokens", 0)
    )


def lire(chemin: Path, nom: str | None = None) -> Session:
    """Les appels d'une session, et les parts entrées entre chacun d'eux."""
    session = Session(nom or chemin.stem)
    outils: dict[str, tuple[str, str | None, str | None]] = {}
    attente: list[Part] = []  # ce qui est entré depuis le dernier appel
    entrees: list[list[Part]] = []  # entrees[i] : avant l'appel i
    vus: set[str] = set()
    with open(chemin, encoding="utf-8") as flux:
        for ligne in flux:
            try:
                entree = json.loads(ligne)
            except json.JSONDecodeError:
                continue
            if entree.get("isSidechain"):
                continue
            genre = entree.get("type")
            dossier = entree.get("cwd")
            if genre == "cost-state":
                cout = entree.get("totalCostUSD")
                if isinstance(cout, (int, float)):
                    session.cout = max(session.cout or 0.0, float(cout))
            elif genre == "assistant":
                message = entree.get("message") or {}
                for bloc in _blocs(message):
                    if bloc.get("type") == "tool_use":
                        outils[bloc.get("id", "")] = decrire_outil(
                            bloc.get("name", "?"), bloc.get("input") or {}, dossier
                        )
                cle = entree.get("requestId") or message.get("id") or entree.get("uuid")
                usage = message.get("usage")
                # Une entrée `<synthetic>` (une interruption, une erreur de
                # l'API) n'est pas un appel : son contexte nul passerait pour
                # une compaction, et le contexte rechargé à l'appel suivant
                # irait tout entier à ce qui le précède.
                if cle in vus or not usage or not _contexte(usage):
                    continue
                vus.add(cle)
                session.appels.append(Appel(_contexte(usage), usage.get("output_tokens", 0)))
                entrees.append(attente)
                attente = []
            elif genre == "user":
                for bloc in _blocs(entree.get("message")):
                    if bloc.get("type") == "tool_result":
                        etiquette, fichier, commande = outils.get(
                            bloc.get("tool_use_id", ""), ("?", None, None)
                        )
                        attente.append(
                            Part("outil", etiquette, fichier, commande, estimer(bloc.get("content")))
                        )
                    else:
                        attente.append(Part("utilisateur", "message", estimation=estimer(bloc)))
            elif genre == "attachment":
                piece = entree.get("attachment") or {}
                sorte = piece.get("type", "?")
                if sorte in ATTACHEMENTS_MUETS:
                    continue
                if "rendered" in entree:
                    taille = additionner(estimer(r.get("content")) for r in entree.get("rendered") or [])
                else:
                    taille = estimer(piece.get("content") or piece.get("stdout"))
                etiquette = f"hook {piece['hookName']}" if piece.get("hookName") else sorte
                attente.append(Part("harnais", etiquette, estimation=taille))
    attribuer(session, entrees)
    return session


def attribuer(session: Session, entrees: list[list[Part]]) -> None:
    """Répartit le contexte de chaque appel entre les parts qui l'ont fait."""
    appels = session.appels
    if not appels:
        return
    # Les segments : une compaction (un contexte qui retombe) en ouvre un neuf.
    debuts = [0] + [i for i in range(1, len(appels)) if appels[i].contexte < appels[i - 1].contexte]
    session.compactions = len(debuts) - 1
    bornes = debuts + [len(appels)]
    for debut, fin in zip(bornes, bornes[1:]):
        longueur = fin - debut
        depart = appels[debut].contexte
        # Le départ se détaille entre ce que le harnais y a mis d'identifiable
        # et le reste : le prompt système, les outils, et, après une
        # compaction, le résumé.
        connues = [p for p in entrees[debut] if p.estimation > 0]
        total_connu = additionner(p.estimation for p in connues)
        facteur = min(1.0, depart / total_connu) if total_connu else 0.0
        for part in connues:
            part.jetons = part.estimation * facteur
            part.relu = part.jetons * longueur
            part.categorie = "depart"
            session.parts.append(part)
        residu = depart - additionner(p.jetons for p in connues)
        nom = "système et outils" if debut == 0 else "résumé de compaction"
        session.parts.append(Part("depart", nom, jetons=residu, relu=residu * longueur))
        for i in range(debut, fin - 1):
            croissance = appels[i + 1].contexte - appels[i].contexte
            restants = fin - (i + 1)
            sortie = min(appels[i].sortie, croissance)
            session.parts.append(Part("sortie", "sortie du modèle", jetons=sortie, relu=sortie * restants))
            reste = croissance - sortie
            parts = [p for p in entrees[i + 1] if p.estimation > 0]
            somme = additionner(p.estimation for p in parts)
            if not somme:
                if reste:
                    session.parts.append(
                        Part("harnais", "non identifié", jetons=reste, relu=reste * restants)
                    )
                continue
            for part in parts:
                part.jetons = reste * part.estimation / somme
                part.relu = part.jetons * restants
                session.parts.append(part)


# --- La recherche des transcriptions ---------------------------------------


def dossier_par_defaut() -> Path:
    base = os.environ.get("CLAUDE_CONFIG_DIR")
    return (Path(base) if base else Path.home() / ".claude") / "projects"


def trouver(chemins: list[Path], jours: float | None) -> list[tuple[Path, str]]:
    """Les transcriptions, chacune avec son nom : le projet, la session, et
    le sous-agent s'il y a lieu."""
    limite = time.time() - jours * 86400 if jours else None
    trouves = []
    for chemin in chemins:
        fichiers = [chemin] if chemin.is_file() else sorted(chemin.rglob("*.jsonl"))
        for fichier in fichiers:
            if limite and fichier.stat().st_mtime < limite:
                continue
            if fichier.parent.name == "subagents":
                nom = f"{fichier.parents[1].name[:8]}/{fichier.stem}"
            else:
                nom = fichier.stem[:8]
            projet = next(
                (p.name for p in fichier.parents if p.parent.name == "projects"), None
            )
            trouves.append((fichier, f"{projet[-28:]}:{nom}" if projet else nom))
    return trouves


# --- Le rapport ------------------------------------------------------------


def _m(jetons: float) -> str:
    return f"{jetons / 1e6:,.2f}".replace(",", " ")


def _k(jetons: float) -> str:
    return f"{jetons / 1e3:,.0f}".replace(",", " ")


def _classement(titre: str, sommes: dict[str, list[float]], total: float, limite: int) -> list[str]:
    lignes = [f"\n{titre}", f"  {'Mjetons relus':>13} {'part':>6} {'kjetons':>8} {'fois':>5}  "]
    for cle, (relu, jetons, fois) in sorted(sommes.items(), key=lambda kv: -kv[1][0])[:limite]:
        lignes.append(
            f"  {_m(relu):>13} {100 * relu / total:>5.1f}% {_k(jetons):>8} {int(fois):>5}  {cle}"
        )
    return lignes


def rapport(sessions: list[Session], limite: int = 15) -> str:
    sessions = [s for s in sessions if s.appels]
    if not sessions:
        return "Aucune session lue."
    lignes = [
        "Par session : appels, contexte de départ et d'arrivée (kjetons), jetons relus "
        "(millions), coût, et la part de chaque origine dans les jetons relus.",
        f"  {'session':<40} {'appels':>6} {'départ':>7} {'fin':>7} {'Mrelus':>7} "
        f"{'coût':>7} {'départ':>7} {'sortie':>7} {'outils':>7} {'harnais':>7} {'util.':>6} {'compact.':>8}",
    ]
    total = additionner(s.relu for s in sessions)
    for s in sorted(sessions, key=lambda s: -s.relu):
        parts = defaultdict(float)
        for part in s.parts:
            parts[part.categorie] += part.relu
        cout = f"{s.cout:.2f} $" if s.cout is not None else "—"
        lignes.append(
            f"  {s.nom[:40]:<40} {len(s.appels):>6} {_k(s.appels[0].contexte):>7} "
            f"{_k(s.appels[-1].contexte):>7} {_m(s.relu):>7} {cout:>7} "
            + " ".join(
                f"{100 * parts[c] / s.relu:>6.0f}%" if s.relu else "     —"
                for c in ("depart", "sortie", "outil", "harnais")
            )
            + f" {100 * parts['utilisateur'] / s.relu if s.relu else 0:>5.0f}% {s.compactions:>8}"
        )
    couts = [s.cout for s in sessions if s.cout is not None]
    lignes.append(
        f"  {'total, ' + str(len(sessions)) + ' sessions':<40} {additionner(len(s.appels) for s in sessions):>6} "
        f"{'':>7} {'':>7} {_m(total):>7} {(f'{additionner(couts):.2f} $' if couts else '—'):>7}"
    )

    def cumuler(cle_de) -> dict[str, list[float]]:
        sommes: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0, 0])
        for s in sessions:
            for part in s.parts:
                cle = cle_de(part)
                if cle:
                    somme = sommes[cle]
                    somme[0] += part.relu
                    somme[1] += part.jetons
                    somme[2] += 1
        return sommes

    lignes += _classement(
        "Par origine, toutes sessions confondues :",
        cumuler(lambda p: f"{p.categorie} · {p.etiquette}"),
        total,
        limite,
    )
    lignes += _classement(
        "Les fichiers lus (Read, cat, sed, head, tail…) :", cumuler(lambda p: p.fichier), total, limite
    )
    lignes += _classement(
        "Les commandes et les recherches :",
        cumuler(lambda p: p.commande if p.categorie != "depart" else None),
        total,
        limite,
    )
    lignes += _classement(
        "Les ajouts du harnais, hooks compris, hors départ :",
        cumuler(lambda p: p.etiquette if p.categorie == "harnais" else None),
        total,
        limite,
    )
    return "\n".join(lignes)


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("chemins", nargs="*", type=Path, help="transcriptions ou dossiers")
    analyseur.add_argument("--jours", type=float, default=30, help="ancienneté maximale (30)")
    analyseur.add_argument("--limite", type=int, default=15, help="lignes par classement (15)")
    options = analyseur.parse_args(arguments)
    chemins = options.chemins or [dossier_par_defaut()]
    jours = None if options.chemins else options.jours
    sessions = [lire(fichier, nom) for fichier, nom in trouver(chemins, jours)]
    print(rapport(sessions, options.limite))
    return 0


if __name__ == "__main__":
    sys.exit(main())
