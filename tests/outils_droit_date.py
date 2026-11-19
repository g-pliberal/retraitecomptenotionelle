"""Ce que comptent les cliquets de la note de décision 0009.

``docs/decisions/0009-le-droit-date-dans-les-versions-de-fiche.md``, « Cinq
cliquets tiennent la décision », et son rectificatif du 19 novembre 2026. Ce
module relève ; ``test_cliquets_du_droit_date.py`` compare au nombre posé.

**Les renvois des fichiers de régime.** Un renvoi est un champ de période que
le schéma marque ``renvoi: true`` (``donnees.regimes.INTERRUPTEURS``) et qui
nomme une fiche. Il se compte en séries : dans un régime, un même champ qui
renvoie à la même fiche de période en période n'est qu'un renvoi, qui commence
à la première. Trois renvois gardent une valeur de repli, écrite dans la même
période (``REPLIS``).

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
"""

from __future__ import annotations

import re
from pathlib import Path

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees import regimes

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


def periodes_des_regimes(racine: Path = RACINE_DONNEES) -> list[tuple[str, list[dict]]]:
    """Le code de chaque régime et ses périodes, telles que le fichier les
    écrit, renvois non résolus."""
    return [(fiche["code"], list(fiche.get("periodes") or []))
            for _, fiche in regimes.fichiers_de_regimes(racine)]


def renvois(regimes_lus: list[tuple[str, list[dict]]]) -> list[dict]:
    """Les renvois, en séries : le régime, le champ, la fiche, l'année où la
    série commence et sa première période."""
    series = []
    for code, periodes in regimes_lus:
        for champ in regimes.INTERRUPTEURS:
            precedent = None
            for periode in periodes:
                cible = periode.get(champ)
                cible = tuple(cible) if isinstance(cible, list) else cible
                if cible is not None and cible != precedent:
                    series.append({"regime": code, "champ": champ, "fiche": cible,
                                   "debut": periode.get("debut"), "periode": periode})
                precedent = cible
    return series


def valeurs_de_repli(regimes_lus: list[tuple[str, list[dict]]]) -> list[tuple[str, int, str]]:
    """Chaque valeur de repli écrite à côté de son renvoi : le régime, le
    début de la période, le champ qui la porte."""
    return [(code, periode.get("debut"), repli)
            for code, periodes in regimes_lus
            for periode in periodes
            for champ, repli in REPLIS.items()
            if periode.get(champ) is not None and periode.get(repli) is not None]


def texte_cite(serie: dict) -> str | None:
    """Le texte que cite un renvoi, ou ``None``.

    La période qui ouvre le renvoi le cite dans ``textes_des_renvois``, par
    champ : l'identifiant du texte, et le jour depuis lequel le renvoi vaut
    (``champs_periode``, depuis la surcote de la Banque de France). Les
    renvois d'avant n'en citent aucun : l'étape de la note qui les date et les
    cite remplit ce champ, ou le refait."""
    cite = (serie["periode"].get("textes_des_renvois") or {}).get(serie["champ"]) or {}
    return cite.get("id")


# --- Les constantes datées du moteur -------------------------------------

_DATE_ENTIERE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")
_ANNEE = re.compile(r"(?<![\w.])(?:19|20)\d\d(?!\w)")
_DATEE = re.compile(r"DateMois\(|[\"'`]\d{4}-\d{2}(?:-\d{2})?[\"'`]")
_CONSTANTE = re.compile(r"^(?:export\s+)?(?:const|static)\s+([A-Z][A-Z0-9_]{2,})\s*=\s*(.*)$")
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


def releve_d_une_source(source: str) -> dict[str, int]:
    """Les constantes datées d'un fichier, sous leur nom, et les années en
    clair du reste de son code, sous leurs quatre chiffres : pour chacune, le
    nombre de ses déclarations ou de ses occurrences."""
    lignes = code_nu(source).split("\n")
    trouve: dict[str, int] = {}
    i = 0
    while i < len(lignes):
        ligne = lignes[i].strip()
        declaration = _CONSTANTE.match(ligne) or _POSEE.match(ligne)
        if declaration:
            valeur, j = declaration.group(2), i
            profondeur = _profondeur(valeur)
            while ((profondeur > 0 or not valeur.rstrip().endswith(";"))
                   and j + 1 < len(lignes)):
                j += 1
                valeur += " " + lignes[j].strip()
                profondeur += _profondeur(lignes[j])
            if _DATEE.search(valeur) or _ANNEE.search(valeur):
                trouve[declaration.group(1)] = trouve.get(declaration.group(1), 0) + 1
                i = j + 1
                continue
            i = j + 1
            continue
        for annee in _ANNEE.findall(ligne):
            trouve[annee] = trouve.get(annee, 0) + 1
        i += 1
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
