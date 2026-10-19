"""Ce qu'une fiche mûre dit d'elle-même, confronté au dépôt.

Le contrat C.2 (``data/reference/contrats/fiche.yaml``) demande à la fiche
d'une règle modélisée son code : « les fonctions des deux moteurs, les
paramètres, les tests ». Une fiche mûre l'écrit sous une forme que ce module
lit, et qu'il confronte à ce que le dépôt porte :

- ``python`` et ``javascript`` : « fichier : fonction, Classe.méthode ; … »,
  le fichier pris de ``src/retraite_notionnelle/`` pour le Python, de la
  racine du dépôt pour le JavaScript ;
- ``parametres`` : « contenu.parametres de chaque version : a, b, … », tous
  ceux que ses versions portent et rien d'autre ; quand ses versions n'en
  portent pas, « regimes/x.yaml, regimes/y.yaml : a, b, … », des champs que
  portent les périodes de ces fiches de régime, qu'elle concerne, ou
  « aucun : » et la raison ;
- ``tests`` : les fichiers qui la tiennent, en liste, ou nommés dans une
  phrase.

Chaque approximation y touche des versions que la fiche porte. Né le
18 octobre 2026 dans ``test_limite_age.py``, pour les quinze fiches de la
limite d'âge (action 130), il sert depuis le 19 aux fiches que la même
action fait mûrir (``test_carte.py``).
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from retraite_notionnelle.config import RACINE_DONNEES

RACINE = Path(__file__).resolve().parents[1]
#: Ce qui définit un nom dans chaque moteur — une fonction, une classe, une
#: méthode —, et le dossier d'où le champ ``code`` d'une fiche nomme ses
#: fichiers.
DEFINITIONS = {
    "python": (RACINE / "src" / "retraite_notionnelle",
               r"^[ \t]*(?:async[ \t]+)?(?:def|class)[ \t]+{0}\b"),
    "javascript": (RACINE,
                   r"^[ \t]*(?:export[ \t]+)?(?:(?:async[ \t]+)?function|class)[ \t]+{0}\b"
                   r"|^[ \t]*(?:static[ \t]+)?{0}[ \t]*\([^)]*\)[ \t]*\{{"),
}
#: La source des paramètres que portent les versions de la fiche.
DES_VERSIONS = "contenu.parametres de chaque version"


def ecarts(fiche: dict) -> list[str]:
    """Ce que la fiche dit d'elle-même et que le dépôt dément : rien, si elle
    tient."""
    nom = fiche["id"]
    sortie = []
    versions = {version["id"] for version in fiche.get("versions") or []}
    for approximation in fiche.get("approximations") or []:
        touchees = approximation.get("version") or []
        touchees = touchees if isinstance(touchees, list) else [touchees]
        if not set(touchees) <= versions:
            sortie.append(f"{nom} : une approximation touche {sorted(set(touchees) - versions)}, "
                          "qui ne sont pas de ses versions")
    code = fiche.get("code") or {}
    for moteur, (dossier, motif) in DEFINITIONS.items():
        for cite in str(code.get(moteur) or "").split(";"):
            chemin, _, noms = (morceau.strip() for morceau in cite.partition(":"))
            if not noms:
                sortie.append(f"{nom}, {moteur} : « {cite.strip()} » ne nomme pas de fonction")
                continue
            if not (dossier / chemin).is_file():
                sortie.append(f"{nom}, {moteur} : {chemin} n'existe pas")
                continue
            texte = (dossier / chemin).read_text(encoding="utf-8")
            for partie in (p.strip() for n in noms.split(",") for p in n.split(".")):
                if not re.search(motif.format(re.escape(partie)), texte, re.M):
                    sortie.append(f"{nom}, {moteur} : {chemin} ne définit pas {partie}")
    sortie += _ecarts_des_parametres(fiche, str(code.get("parametres") or ""))
    tests = code.get("tests") or []
    if not tests:
        sortie.append(f"{nom} : son code ne nomme aucun test")
    for cite in tests if isinstance(tests, list) else [tests]:
        chemins = re.findall(r"\b(?:tests|scripts)/[\w/.-]*\w", str(cite))
        if not chemins:
            sortie.append(f"{nom} : « {cite} » ne nomme aucun fichier de test")
        sortie += [f"{nom} : le test {chemin} n'existe pas" for chemin in chemins
                   if not (RACINE / chemin).is_file()]
    return sortie


def _ecarts_des_parametres(fiche: dict, texte: str) -> list[str]:
    nom = fiche["id"]
    portes = {cle for version in fiche.get("versions") or []
              for cle in (version.get("contenu") or {}).get("parametres") or {}}
    source, _, noms = (morceau.strip() for morceau in texte.partition(":"))
    if source == "aucun":
        return [f"{nom}, parametres : « aucun », quand ses versions portent {sorted(portes)}"] \
            if portes else []
    nommes = {cle.strip() for cle in noms.split(",") if cle.strip()}
    if source == DES_VERSIONS or portes:
        if source == DES_VERSIONS and nommes == portes:
            return []
        return [f"{nom}, parametres : « {DES_VERSIONS} : » et tous ceux de ses versions, "
                f"à rien près ({sorted(nommes ^ portes)})"]
    regimes = re.findall(r"regimes/(\w+)\.yaml", source)
    if not regimes or not nommes:
        return [f"{nom}, parametres : ni ceux de ses versions, ni ceux d'une fiche de "
                f"régime, ni « aucun » (« {texte} »)"]
    sortie = [f"{nom}, parametres : {regime} n'est pas de ses régimes"
              for regime in regimes if regime not in (fiche.get("regimes") or [])]
    champs = set()
    for regime in regimes:
        chemin = RACINE_DONNEES / "reference" / "regimes" / f"{regime}.yaml"
        if not chemin.is_file():
            sortie.append(f"{nom}, parametres : regimes/{regime}.yaml n'existe pas")
            continue
        donnee = yaml.safe_load(chemin.read_text(encoding="utf-8"))
        champs |= {cle for periode in donnee.get("periodes") or [] for cle in periode}
    sortie += [f"{nom}, parametres : aucune période de {', '.join(regimes)} ne porte {cle}"
               for cle in sorted(nommes - champs)]
    return sortie
