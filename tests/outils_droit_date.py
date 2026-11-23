"""Ce que comptent les cliquets de la note de décision 0009.

``docs/decisions/0009-le-droit-date-dans-les-versions-de-fiche.md``, « Cinq
cliquets tiennent la décision », et son rectificatif du 19 novembre 2026. Ce
module relève ; ``test_cliquets_du_droit_date.py`` compare au nombre posé.

**Les renvois des fichiers de régime.** Un renvoi est un champ que le schéma
marque ``renvoi: true`` (``donnees.regimes.INTERRUPTEURS``) et qui nomme une
fiche. Il se lit dans le fichier tel qu'il s'écrit, en quatre blocs, sur les
lignes du bloc qui porte son champ (``donnees.axes.famille``), et non dans la
vue en périodes que le chargeur en refait pendant le gel. Il se compte en
séries : dans un régime, un même champ qui renvoie à la même fiche de ligne en
ligne, dans l'ordre du fichier, n'est qu'un renvoi, qui commence à la
première. Trois renvois gardent une valeur de repli, écrite dans la même ligne
de liquidation (``REPLIS``).

**Les constantes datées du moteur.** Dans le moteur hors du site, une
constante nommée — ``const NOM``, ``static NOM``, ou ``Classe.NOM`` posée après
sa classe, le nom en majuscules — est datée quand sa valeur porte un
``DateMois(``, une date « AAAA-MM-JJ » ou « AAAA-MM », ou une année de 1900 à
2099. Hors d'elles, toute ligne de code qui porte une telle année se relève
aussi, par fichier et par année. Les commentaires ne comptent pas, ni les
libellés : d'une chaîne, seule une date entière est gardée. Le relevé de
l'évaluation du 18 novembre (``docs/decisions/0009/evaluation-du-18-novembre/
constantes.py``) en est le premier état ; il gardait les libellés, coupait une
déclaration à sa septième ligne et ne voyait pas les statiques posées après
leur classe ni les générations à décimales (``1961.667``).

**Les chiffres sans date.** Un âge, un taux, une durée que la loi fixe n'ont
pas de date, et ce relevé-là ne les voit pas. Un second prend donc toute
constante nommée dont la valeur écrit un nombre, sans date ni année
(``constantes_chiffrees``). Un nombre écrit en clair dans une expression, sans
nom, reste hors de vue : rien ne le distingue d'un rang ou d'une unité.
"""

from __future__ import annotations

import re
from pathlib import Path

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees import axes, regimes
from retraite_notionnelle.donnees.chargement import charger_yaml

RACINE = Path(__file__).resolve().parents[1]
MOTEUR = RACINE / "moteur" / "js"
#: Le site : ses pages, son gabarit, son routeur, ses adresses.
SITE = ("pages.js", "gabarit.js", "routeur.js", "adresses.js")

#: Les renvois qui gardent une valeur de repli, et le champ qui la porte
#: (``data/reference/regimes/_schema.yaml`` : « la valeur ci-dessus ne servant
#: que de repli »).
REPLIS = {
    "age_ouverture_par_generation": "age_ouverture",
    "age_taux_plein_par_generation": "age_taux_plein",
    "duree_requise_par_generation": "duree_requise_trimestres",
}


def blocs_des_regimes(racine: Path = RACINE_DONNEES) -> list[tuple[str, dict]]:
    """Le code de chaque régime calculé et son fichier, tel qu'il s'écrit :
    ses quatre blocs, renvois non résolus."""
    lus = []
    for chemin, _ in regimes.fichiers_de_regimes(racine):
        fiche = charger_yaml(chemin)
        if "liquidation" in fiche:
            lus.append((fiche["code"], fiche))
    return lus


def _jour(valeur) -> str:
    return str(valeur)


def renvois(regimes_lus: list[tuple[str, dict]]) -> list[dict]:
    """Les renvois, en séries : le régime, le champ, la fiche, le jour où la
    série commence et sa première ligne."""
    series = []
    for code, fiche in regimes_lus:
        for champ in regimes.INTERRUPTEURS:
            precedent = None
            for ligne in fiche.get(axes.famille(champ)) or ():
                cible = ligne.get(champ)
                cible = tuple(cible) if isinstance(cible, list) else cible
                if cible is not None and cible != precedent:
                    series.append({"regime": code, "champ": champ, "fiche": cible,
                                   "du": _jour(ligne["du"]), "ligne": ligne})
                precedent = cible
    return series


def valeurs_de_repli(regimes_lus: list[tuple[str, dict]]) -> list[tuple[str, str, str]]:
    """Chaque valeur de repli écrite à côté de son renvoi : le régime, le
    jour où sa ligne de liquidation commence, le champ qui la porte."""
    return [(code, _jour(ligne["du"]), repli)
            for code, fiche in regimes_lus
            for ligne in fiche["liquidation"]
            for champ, repli in REPLIS.items()
            if ligne.get(champ) is not None and ligne.get(repli) is not None]


def texte_cite(serie: dict) -> str | None:
    """Le texte que cite un renvoi, ou ``None``.

    La ligne qui ouvre le renvoi le cite dans ``textes``, par champ :
    l'identifiant du texte, et le jour depuis lequel le renvoi vaut. Les
    renvois d'avant n'en citent aucun : l'étape de la note qui les date et les
    cite remplit ce champ, ou le refait."""
    cite = (serie["ligne"].get("textes") or {}).get(serie["champ"]) or {}
    return cite.get("id")


# --- Les constantes datées du moteur -------------------------------------

_DATE_ENTIERE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")
_ANNEE = re.compile(r"(?<![\w.])(?:19|20)\d\d(?!\w)")
_DATEE = re.compile(r"DateMois\(|[\"'`]\d{4}-\d{2}(?:-\d{2})?[\"'`]")
_CONSTANTE = re.compile(r"^(?:export\s+)?(?:const|static)\s+([A-Z][A-Z0-9_]{2,})\s*=\s*(.*)$")
_NOMBRE = re.compile(r"(?<![\w$.])\d")
_RANG = re.compile(r"(?<=\w)\[\d+\]")
_POSEE = re.compile(r"^([A-Z]\w*\.[A-Z][A-Z0-9_]{2,})\s*=\s*(.*)$")


def code_nu(source: str) -> str:
    """Le code sans ses commentaires ni ses libellés, ligne pour ligne : une
    chaîne ne garde que la date entière qu'elle porte."""
    sortie, i, fin = [], 0, len(source)
    while i < fin:
        caractere = source[i]
        if source.startswith("//", i):
            suite = source.find("\n", i)
            i = fin if suite < 0 else suite
        elif source.startswith("/*", i):
            suite = source.find("*/", i + 2)
            suite = fin if suite < 0 else suite + 2
            sortie.append("\n" * source.count("\n", i, suite))
            i = suite
        elif caractere in "\"'`":
            suite = i + 1
            while suite < fin and source[suite] != caractere:
                suite += 2 if source[suite] == "\\" else 1
            corps = source[i + 1:suite]
            sortie.append(caractere + (corps if _DATE_ENTIERE.match(corps) else "")
                          + caractere + "\n" * corps.count("\n"))
            i = suite + 1
        else:
            sortie.append(caractere)
            i += 1
    return "".join(sortie)


def _profondeur(texte: str) -> int:
    return sum(texte.count(c) for c in "([{") - sum(texte.count(c) for c in ")]}")


def _declarations(lignes: list[str]):
    """Les constantes nommées d'un code nu, chacune avec sa valeur entière,
    et, entre elles, les autres lignes : ``(nom, valeur)`` ou ``(None,
    ligne)``."""
    i = 0
    while i < len(lignes):
        ligne = lignes[i].strip()
        declaration = _CONSTANTE.match(ligne) or _POSEE.match(ligne)
        if not declaration:
            yield None, ligne
            i += 1
            continue
        valeur, j = declaration.group(2), i
        profondeur = _profondeur(valeur)
        while ((profondeur > 0 or not valeur.rstrip().endswith(";"))
               and j + 1 < len(lignes)):
            j += 1
            valeur += " " + lignes[j].strip()
            profondeur += _profondeur(lignes[j])
        yield declaration.group(1), valeur
        i = j + 1


def _est_datee(valeur: str) -> bool:
    return bool(_DATEE.search(valeur) or _ANNEE.search(valeur))


def releve_d_une_source(source: str) -> dict[str, int]:
    """Les constantes datées d'un fichier, sous leur nom, et les années en
    clair du reste de son code, sous leurs quatre chiffres : pour chacune, le
    nombre de ses déclarations ou de ses occurrences."""
    trouve: dict[str, int] = {}
    for nom, valeur in _declarations(code_nu(source).split("\n")):
        if nom is None:
            for annee in _ANNEE.findall(valeur):
                trouve[annee] = trouve.get(annee, 0) + 1
        elif _est_datee(valeur):
            trouve[nom] = trouve.get(nom, 0) + 1
    return trouve


def chiffres_d_une_source(source: str) -> dict[str, int]:
    """Les constantes d'un fichier qui portent un chiffre sans date : celles
    dont la valeur écrit un nombre, et que le relevé des constantes datées ne
    prend pas. Le rang lu dans une autre constante (``TABLE[0]``) n'est pas
    un nombre de la constante."""
    trouve: dict[str, int] = {}
    for nom, valeur in _declarations(code_nu(source).split("\n")):
        if nom is not None and not _est_datee(valeur) and _NOMBRE.search(_RANG.sub("", valeur)):
            trouve[nom] = trouve.get(nom, 0) + 1
    return trouve


def fichiers_du_moteur(dossier: Path = MOTEUR) -> list[Path]:
    return sorted(chemin for chemin in dossier.rglob("*.js") if chemin.name not in SITE)


def constantes_datees(dossier: Path = MOTEUR) -> dict[str, int]:
    """Le relevé du moteur hors du site : « fichier : NOM » ou « fichier :
    année », le fichier pris de la racine du dépôt."""
    racine = dossier.parents[1]
    return {f"{chemin.relative_to(racine).as_posix()} : {nom}": nombre
            for chemin in fichiers_du_moteur(dossier)
            for nom, nombre in releve_d_une_source(chemin.read_text(encoding="utf-8")).items()}


def constantes_chiffrees(sans_regle: frozenset[str] = frozenset(),
                         dossier: Path = MOTEUR) -> dict[str, int]:
    """Le relevé des chiffres sans date du moteur hors du site, sous les mêmes
    clés que ``constantes_datees``. ``sans_regle`` nomme les fichiers que la
    liste écarte en entier, parce qu'ils ne portent aucune règle."""
    racine = dossier.parents[1]
    return {f"{chemin.relative_to(racine).as_posix()} : {nom}": nombre
            for chemin in fichiers_du_moteur(dossier)
            if chemin.relative_to(racine).as_posix() not in sans_regle
            for nom, nombre in chiffres_d_une_source(chemin.read_text(encoding="utf-8")).items()}


def nomme_par_la_fiche(fiche: dict, fichier: str, nom: str) -> bool:
    """Le champ ``code.javascript`` de la fiche nomme-t-il ``nom`` dans ce
    fichier (« fichier : a, b ; … », ``tests/outils_carte.py``) ?"""
    code = fiche.get("code")
    javascript = code.get("javascript") if isinstance(code, dict) else None
    for clause in str(javascript or "").split(";"):
        chemin, _, noms = clause.partition(":")
        if chemin.strip() == fichier and nom in {n.strip().strip("`") for n in noms.split(",")}:
            return True
    return False
