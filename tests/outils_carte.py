"""Ce qu'une fiche mûre dit d'elle-même, confronté au dépôt.

Le contrat C.2 (``data/reference/contrats/fiche.yaml``) demande à la fiche
d'une règle modélisée son code : « les fonctions des deux moteurs, les
paramètres, les tests ». Une fiche mûre l'écrit sous une forme que ce module
lit, et qu'il confronte à ce que le dépôt porte :

- ``python`` et ``javascript`` : « fichier : fonction, Classe.méthode ; … »,
  le fichier pris de ``src/retraite_notionnelle/`` pour le Python, de la
  racine du dépôt pour le JavaScript ; un nom y est une fonction, une classe,
  une méthode, un accesseur ou une constante de module ;
- ``parametres`` : des clauses que sépare « ; », chacune « source : a, b,
  … » — « contenu.parametres de chaque version : », tous ceux que ses
  versions portent et rien d'autre, clause qu'exige toute fiche dont les
  versions en portent ; « regimes/x.yaml, regimes/y.yaml : », des champs que
  portent les périodes de ces fiches de régime, qu'elle concerne ; un ou
  plusieurs fichiers des données de référence, « legislation/x.yaml »,
  « macro/y.csv » ou « regimes/z.csv », hors des fiches, mais avec les YAML
  que le catalogue range parmi elles sans en faire des régimes
  (``FICHIERS_HORS_REGIMES``), et, s'il le faut, des clés, pointées, des
  colonnes ou des mesures qu'ils portent —, ou « aucun : » et la raison,
  seule ;
- ``tests`` : les fichiers qui la tiennent, en liste, ou nommés dans une
  phrase.

Chaque approximation y touche des versions que la fiche porte. Né le
18 octobre 2026 dans ``test_limite_age.py``, pour les quinze fiches de la
limite d'âge (action 130), il sert depuis le 19 aux fiches que la même
action fait mûrir (``test_carte.py``), et depuis le 22 à toutes celles qui
ont un code.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees.regimes import FICHIERS_HORS_REGIMES

RACINE = Path(__file__).resolve().parents[1]
#: Ce qui définit un nom dans chaque moteur — une fonction, une classe, une
#: méthode, un accesseur, une constante de module —, et le dossier d'où le
#: champ ``code`` d'une fiche nomme ses fichiers.
DEFINITIONS = {
    "python": (RACINE / "src" / "retraite_notionnelle",
               r"^[ \t]*(?:async[ \t]+)?(?:def|class)[ \t]+{0}\b"
               r"|^{0}[ \t]*(?::[^=\n]*)?=(?!=)"),
    "javascript": (RACINE,
                   r"^[ \t]*(?:export[ \t]+)?(?:(?:async[ \t]+)?function|class)[ \t]+{0}\b"
                   r"|^[ \t]*(?:static[ \t]+)?(?:(?:get|set)[ \t]+)?{0}[ \t]*\([^)]*\)[ \t]*\{{"
                   r"|^(?:export[ \t]+)?(?:const|let|var)[ \t]+{0}\b"),
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
    tables = [(version.get("contenu") or {}).get("parametres") for version in fiche.get("versions") or []]
    portes = {cle for table in tables if isinstance(table, dict) for cle in table}
    clauses = [clause.strip() for clause in texte.split(";") if clause.strip()] or [""]
    sortie, sources = [], []
    for clause in clauses:
        source, _, noms = (morceau.strip() for morceau in clause.partition(":"))
        nommes = {cle.strip() for cle in noms.split(",") if cle.strip()}
        sources.append(source)
        chemins = [chemin.strip() for chemin in source.split(",")]
        if source == "aucun":
            if portes:
                sortie.append(f"{nom}, parametres : « aucun », quand ses versions portent "
                              f"{sorted(portes)}")
            if len(clauses) > 1:
                sortie.append(f"{nom}, parametres : « aucun » va seul (« {texte} »)")
        elif source == DES_VERSIONS:
            if nommes != portes:
                sortie.append(f"{nom}, parametres : « {DES_VERSIONS} : » et tous ceux de ses "
                              f"versions, à rien près ({sorted(nommes ^ portes)})")
        elif nommes and all(_fiche_de_regime(c) for c in chemins):
            sortie += _ecarts_des_regimes(fiche, [c[len("regimes/"):-len(".yaml")]
                                                  for c in chemins], nommes)
        elif all(re.fullmatch(r"\w+(?:/[\w-]+)+\.(?:yaml|csv)", c) for c in chemins):
            sortie += _ecarts_des_donnees(nom, chemins, nommes)
        else:
            sortie.append(f"{nom}, parametres : « {clause} » ne nomme ni ses versions, ni une "
                          "fiche de régime, ni des données de référence, ni « aucun »")
    if portes and DES_VERSIONS not in sources:
        sortie.append(f"{nom}, parametres : « {DES_VERSIONS} : » et tous ceux de ses versions "
                      f"({sorted(portes)}) y manquent")
    return sortie


def _fiche_de_regime(chemin: str) -> bool:
    """Un YAML de ``regimes/`` est une fiche de régime, hors des données que le
    catalogue y range sans en faire un régime (``FICHIERS_HORS_REGIMES``)."""
    return (re.fullmatch(r"regimes/\w+\.yaml", chemin) is not None
            and chemin.removeprefix("regimes/") not in FICHIERS_HORS_REGIMES)


def _ecarts_des_regimes(fiche: dict, regimes: list[str], nommes: set[str]) -> list[str]:
    nom = fiche["id"]
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


def _ecarts_des_donnees(nom: str, chemins: list[str], nommes: set[str]) -> list[str]:
    """Les fichiers des données de référence existent ; les noms sont des clés,
    pointées, de l'un des YAML, ou des colonnes de l'un des CSV, ou ce qu'une
    ligne mesure : une valeur de sa première colonne, ou de sa colonne
    ``mesure``."""
    sortie, portes = [], set()
    for relatif in chemins:
        chemin = RACINE_DONNEES / "reference" / relatif
        fiche = relatif.startswith("regles/") or _fiche_de_regime(relatif)
        if fiche or not chemin.is_file():
            sortie.append(f"{nom}, parametres : {relatif} n'existe pas, ou n'est pas une donnée")
            continue
        texte = chemin.read_text(encoding="utf-8")
        if relatif.endswith(".csv"):
            entete, *lignes = [ligne.split(",") for ligne in texte.splitlines()
                               if ligne.strip() and not ligne.startswith("#")]
            colonnes = [colonne.strip() for colonne in entete]
            portes |= set(colonnes)
            for rang in {0, colonnes.index("mesure") if "mesure" in colonnes else 0}:
                portes |= {ligne[rang].strip() for ligne in lignes if len(ligne) > rang}
        else:
            portes |= set(_cles(yaml.safe_load(texte)))
    sortie += [f"{nom}, parametres : {', '.join(chemins)} ne porte pas {cle}"
               for cle in sorted(nommes - portes)]
    return sortie


def _cles(donnee, prefixe: str = ""):
    if isinstance(donnee, dict):
        for cle, valeur in donnee.items():
            yield f"{prefixe}{cle}"
            yield from _cles(valeur, f"{prefixe}{cle}.")
