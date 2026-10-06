#!/usr/bin/env python3
"""Les deux fusions que ``scripts/pousser.sh`` confie à git, le temps d'un rebasage.

    python scripts/fusionner.py ancres    BASE COURANT AUTRE [TAILLE]
    python scripts/fusionner.py ensembles BASE COURANT AUTRE [TAILLE]

Ce sont deux pilotes de fusion git (``gitattributes``, « Defining a custom
merge driver ») : git les appelle avec la version de la base, celle de la
branche courante — au rebasage, ``main`` — et celle du commit rejoué ; le
pilote écrit le résultat dans le fichier COURANT, et rend 0 s'il a fusionné,
1 s'il reste un conflit, marqué comme git le marque. ``.gitattributes`` dit
quel fichier relève duquel ; ``pousser.sh`` les déclare à git par ``-c``, pour
son seul rebasage. Un git lancé à la main ne les connaît pas, et fusionne ces
fichiers comme du texte, comme avant.

POURQUOI (action 148, étape 3)
------------------------------
Mesuré sur les 200 derniers commits de ``main`` (27 septembre - 6 octobre
2026) : le README est touché par 108 commits, dont 93 n'y déplacent que ce que
les scripts écrivent, chiffres ancrés et blocs produits ;
``integration-partiliberalfrancais.md`` par 53, tous pour cela. Deux sessions
qui changent le modèle récrivent les mêmes ancres, chacune à sa valeur, et git
déclare le conflit sur la ligne : rejoués deux à deux comme s'ils avaient été
menés en parallèle, 95 couples de commits successifs du README sur 107
entraient en conflit, dont 94 sur cela seul. Or ces valeurs, GitHub les refait
après chaque envoi (``tests.yml``, ``regenerer.py``). La référence de la
conservation, de même : 21 couples sur 26 en conflit, deux sessions y ajoutant
leurs lignes au même endroit.

``ancres``
    La prose. Une fusion de texte d'abord, celle de git. Si elle bute, une
    seconde, où ce que les scripts écrivent ne compte plus : le contenu des
    ancres que ``verifier_prose.py --corriger`` recalcule, et les blocs
    produits, entre ``<!-- nom:debut -->`` et ``<!-- nom:fin -->``. Chacun
    prend une valeur unique, posée dans les trois versions avant de fusionner :
    celle de ``main`` s'il l'a changée, sinon celle du commit rejoué. Le texte
    écrit à la main, lui, se fusionne comme avant, et un conflit qui en porte
    reste un conflit. Une ancre écrite à la main (``tenu``, ``illustration``,
    ``a_verifier``), une ancre citée dans un bloc de code, une valeur dont la
    forme change — ses décimales, son signe typographique, le texte autour du
    nombre — sont du texte écrit à la main.
``ensembles``
    ``tests/temoins/conservation.json`` : des listes d'empreintes et de clés,
    rangées dans des dictionnaires. Chaque liste se fusionne comme un ensemble
    (avec ses doublons) : ce que chaque côté ajoute reste, ce que chaque côté
    retire part. Une liste triée le reste ; une autre garde l'ordre de
    ``main``, et chaque ajout du commit rejoué se place après son prédécesseur.
    Le fichier s'écrit comme ``conservation.py --figer`` l'écrit.

Ce module ne lit que la bibliothèque standard : ``pousser.sh`` le copie hors du
répertoire de travail avant de rebaser, et le lance sans le paquet.
"""

from __future__ import annotations

import collections
import difflib
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

#: L'ancre, telle que ``verifier_prose.py`` la lit (``ANCRE``) : la sonde, son
#: argument, sa tolérance, puis le contenu, que ``--corriger`` récrit.
ANCRE = re.compile(r"<!--chiffre:(\w+)\(([^)]*)\)(?:~([\d,.]+)%)?-->(.*?)<!--/-->", re.DOTALL)
#: Un nombre de la prose, comme ``verifier_prose._NOMBRE``.
NOMBRE = r"[−+-]?\d{1,3}(?:[ \u00a0\u202f]\d{3})+(?:,\d+)?|[−+-]?\d+(?:,\d+)?"
#: Les sondes qui ne recalculent rien : leur chiffre s'écrit à la main.
A_LA_MAIN = frozenset({"tenu", "illustration", "a_verifier"})
#: Le repère d'un bloc produit, comme ``verifier_prose.lignes_produites``.
REPERE = re.compile(r"[ \t]*<!-- ([\w-]+):(debut|fin) -->[ \t]*")


class Conflit(Exception):
    """Les deux côtés ont changé la même chose, chacun à sa façon."""


# --------------------------------------------------------------------------
# La fusion de texte, celle de git.
# --------------------------------------------------------------------------


def fusion_de_texte(courant: str, base: str, autre: str, taille: int = 7) -> tuple[bool, str]:
    """``git merge-file`` : (fusionné sans conflit, résultat marqué au besoin).

    L'algorithme est l'histogramme, celui que la stratégie ``ort`` de git
    prend par défaut ; un git trop ancien pour le choisir prend le sien.
    ``merge-file`` rend le nombre de conflits, 128 et plus sur une erreur.
    """
    with tempfile.TemporaryDirectory() as dossier:
        chemins = []
        for nom, texte in (("courant", courant), ("base", base), ("autre", autre)):
            chemin = Path(dossier) / nom
            chemin.write_bytes(texte.encode("utf-8"))
            chemins.append(str(chemin))
        commun = ["git", "merge-file", "-p", f"--marker-size={taille}",
                  "-L", "main", "-L", "base", "-L", "session"]
        for options in (["--diff-algorithm=histogram"], []):
            fini = subprocess.run([*commun, *options, *chemins], capture_output=True)
            if 0 <= fini.returncode < 128:
                return fini.returncode == 0, fini.stdout.decode("utf-8")
    raise RuntimeError(fini.stderr.decode("utf-8", "replace"))


# --------------------------------------------------------------------------
# La prose : ce que les scripts écrivent, et le reste.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Fente:
    """Un passage qu'un script écrit : une ancre recalculée, ou un bloc produit."""

    cle: str        # l'ancre sans son contenu, ou le nom du bloc
    debut: int
    fin: int
    valeur: str
    ancre: bool


def _lignes_de_code(texte: str) -> set[int]:
    """Les lignes d'un bloc clôturé (``verifier_prose._blocs_de_code``)."""
    dedans, lignes = False, set()
    for numero, ligne in enumerate(texte.split("\n"), 1):
        if ligne.lstrip().startswith("```"):
            dedans = not dedans
            lignes.add(numero)
        elif dedans:
            lignes.add(numero)
    return lignes


def fentes(texte: str) -> list[Fente]:
    """Ce que les scripts écrivent dans un document, dans l'ordre du texte."""
    trouvees: list[Fente] = []
    ouverts: dict[str, int] = {}
    code = _lignes_de_code(texte)
    position = 0
    for numero, ligne in enumerate(texte.split("\n"), 1):
        repere = None if numero in code else REPERE.fullmatch(ligne.rstrip("\r"))
        if repere and repere.group(2) == "debut":
            ouverts[repere.group(1)] = position + len(ligne) + 1
        elif repere and repere.group(1) in ouverts:
            debut = ouverts.pop(repere.group(1))
            trouvees.append(Fente(f"bloc {repere.group(1)}", debut, position,
                                  texte[debut:position], False))
        position += len(ligne) + 1
    blocs = [(f.debut, f.fin) for f in trouvees]
    for trouve in ANCRE.finditer(texte):
        if trouve.group(1) in A_LA_MAIN:
            continue
        if texte.count("\n", 0, trouve.start()) + 1 in code:
            continue
        if any(debut <= trouve.start() < fin for debut, fin in blocs):
            continue
        debut, fin = trouve.span(4)
        trouvees.append(Fente(texte[trouve.start():debut], debut, fin,
                              trouve.group(4), True))
    return sorted(trouvees, key=lambda f: f.debut)


def forme(contenu: str) -> str:
    """Ce que ``--corriger`` garde d'un chiffre ancré : tout, sauf sa valeur —
    le texte autour du nombre, ses décimales, son signe typographique."""
    def gabarit(nombre: re.Match) -> str:
        ecrit = nombre.group(0)
        decimales = len(ecrit.split(",")[1]) if "," in ecrit else 0
        return f"\0{'±' if ecrit[0] in '−+' else ''}{decimales}\0"
    return re.sub(NOMBRE, gabarit, contenu)


def _correspondance(depuis: list[Fente], vers: list[Fente]) -> dict[int, int]:
    """Les fentes d'une version retrouvées dans une autre, par leurs clés."""
    paires = difflib.SequenceMatcher(None, [f.cle for f in depuis], [f.cle for f in vers],
                                     autojunk=False).get_matching_blocks()
    return {i + k: j + k for i, j, n in paires for k in range(n)}


def _poser(texte: str, fentes_: list[Fente], valeurs: dict[int, str]) -> str:
    for rang in sorted(valeurs, reverse=True):
        fente = fentes_[rang]
        texte = texte[:fente.debut] + valeurs[rang] + texte[fente.fin:]
    return texte


def aligner(base: str, courant: str, autre: str) -> tuple[str, str, str]:
    """Les trois versions, chaque passage écrit par un script ramené à une
    valeur unique : celle de ``main`` (le courant) s'il l'a changée, sinon
    celle du commit rejoué. Ce qui reste à fusionner est écrit à la main."""
    fb, fc, fa = fentes(base), fentes(courant), fentes(autre)
    vers_c, vers_a = _correspondance(fb, fc), _correspondance(fb, fa)
    poser_b: dict[int, str] = {}
    poser_c: dict[int, str] = {}
    poser_a: dict[int, str] = {}
    for i, fente in enumerate(fb):
        if i not in vers_c or i not in vers_a:
            continue
        c, a = fc[vers_c[i]], fa[vers_a[i]]
        if fente.ancre and not forme(fente.valeur) == forme(c.valeur) == forme(a.valeur):
            continue
        retenue = c.valeur if c.valeur != fente.valeur else a.valeur
        poser_b[i], poser_c[vers_c[i]], poser_a[vers_a[i]] = retenue, retenue, retenue
    return (_poser(base, fb, poser_b), _poser(courant, fc, poser_c),
            _poser(autre, fa, poser_a))


def fusionner_prose(base: str, courant: str, autre: str, taille: int = 7) -> tuple[bool, str]:
    """La fusion de texte ; si elle bute, la même, ce que les scripts écrivent
    mis à part. Rend (fusionné, résultat) ; en conflit, le résultat est celui
    de la fusion de texte, marqué comme git le marque."""
    propre, resultat = fusion_de_texte(courant, base, autre, taille)
    if propre:
        return True, resultat
    b, c, a = aligner(base, courant, autre)
    propre_aligne, aligne = fusion_de_texte(c, b, a, taille)
    if propre_aligne:
        return True, aligne
    return False, resultat


# --------------------------------------------------------------------------
# La référence de la conservation : des ensembles.
# --------------------------------------------------------------------------

ABSENT = object()


def _ecart(courant: int, autre: int) -> int:
    """Ce que deux côtés ont changé au compte d'un élément, réuni : le même
    changement compte une fois, comme git compte une même ligne ajoutée."""
    if courant == autre or autre == 0:
        return courant
    if courant == 0:
        return autre
    if (courant > 0) == (autre > 0):
        return max(courant, autre) if courant > 0 else min(courant, autre)
    return courant + autre


def _triee(liste: list) -> bool:
    try:
        return liste == sorted(liste)
    except TypeError:
        return False


def _liste(base: list, courant: list, autre: list) -> list:
    """Trois versions d'une liste, fusionnées comme des ensembles à doublons."""
    nb, nc, na = (collections.Counter(x) for x in (base, courant, autre))
    reste = {x: nb[x] + _ecart(nc[x] - nb[x], na[x] - nb[x]) for x in set(nb) | set(nc) | set(na)}
    reste = {x: n for x, n in reste.items() if n > 0}
    if (all(_triee(x) for x in (base, courant, autre))
            and max(len(base), len(courant), len(autre)) >= 3):
        return sorted(collections.Counter(reste).elements())
    resultat: list = []
    for x in courant:
        if reste.get(x, 0) > 0:
            resultat.append(x)
            reste[x] -= 1
    for rang, x in enumerate(autre):
        if reste.get(x, 0) <= 0:
            continue
        place = 0
        for precedent in reversed(autre[:rang]):
            if precedent in resultat:
                place = len(resultat) - resultat[::-1].index(precedent)
                break
        resultat.insert(place, x)
        reste[x] -= 1
    return resultat


def fusionner_valeurs(base, courant, autre):
    """Fusion à trois voies d'une valeur JSON : dictionnaires clé à clé, listes
    de nombres ou de textes comme des ensembles, le reste en entier."""
    if courant == autre:
        return courant
    if courant == base:
        return autre
    if autre == base:
        return courant
    presents = [x for x in (base, courant, autre) if x is not ABSENT]
    if all(isinstance(x, dict) for x in presents):
        cles = sorted({cle for x in presents for cle in x})
        resultat = {}
        for cle in cles:
            valeur = fusionner_valeurs(*(x.get(cle, ABSENT) if x is not ABSENT else ABSENT
                                         for x in (base, courant, autre)))
            if valeur is not ABSENT:
                resultat[cle] = valeur
        return resultat
    if all(isinstance(x, list) and all(isinstance(e, (str, int, float)) for e in x)
           for x in presents):
        fusion = _liste(*(x if x is not ABSENT else [] for x in (base, courant, autre)))
        if not fusion and ABSENT in (courant, autre):
            return ABSENT
        return fusion
    raise Conflit("les deux côtés ont changé la même valeur")


def fusionner_ensembles(base: str, courant: str, autre: str, taille: int = 7) -> tuple[bool, str]:
    """La référence de la conservation, fusionnée par ensembles ; si l'un des
    trois n'est pas du JSON, ou qu'une valeur ne se fusionne pas, la fusion de
    texte."""
    try:
        valeurs = [json.loads(x) for x in (base, courant, autre)]
        fusion = fusionner_valeurs(*valeurs)
    except (ValueError, Conflit):
        return fusion_de_texte(courant, base, autre, taille)
    # Comme ``conservation.py --figer`` l'écrit.
    return True, json.dumps(fusion, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


FUSIONS = {"ancres": fusionner_prose, "ensembles": fusionner_ensembles}


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) not in (4, 5) or arguments[0] not in FUSIONS:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    mode, base, courant, autre = arguments[:4]
    taille = int(arguments[4]) if len(arguments) == 5 and arguments[4].isdigit() else 7
    try:
        textes = [Path(x).read_bytes().decode("utf-8") for x in (base, courant, autre)]
    except UnicodeDecodeError:
        # Pas du texte : la fusion de git, sur place, sans rien de plus.
        fini = subprocess.run(["git", "merge-file", f"--marker-size={taille}",
                               courant, base, autre], capture_output=True)
        return 0 if fini.returncode == 0 else 1
    propre, resultat = FUSIONS[mode](textes[0], textes[1], textes[2], taille)
    Path(courant).write_bytes(resultat.encode("utf-8"))
    return 0 if propre else 1


if __name__ == "__main__":
    raise SystemExit(main())
