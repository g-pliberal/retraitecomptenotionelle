#!/usr/bin/env python3
"""Confronte au dépôt les chiffres que la prose affirme.

    python scripts/verifier_prose.py              # confronte, sans rien écrire
    python scripts/verifier_prose.py --corriger   # réécrit les chiffres ancrés qui ont dérivé
    python scripts/verifier_prose.py --inventaire # ce qui n'est pas encore déclaré
    python scripts/verifier_prose.py --sondes     # le vocabulaire des sondes

Le problème qu'il traite
------------------------

Le dépôt affirme deux mille cinq cents chiffres en prose, et une vingtaine
seulement étaient tenus par un test. Les autres étaient des souvenirs : la
feuille de route donnait « plus de trois mille lignes » à ``actuel.py``, qui en
faisait 4 251, et « douze mille lignes » au portage, qui en faisait 22 776 ;
le README annonçait un paquet de 2874 Ko quand il en pesait 2944.

Mais le mal n'est pas le chiffre faux, c'est qu'on ne puisse pas savoir. Le
dépôt écrit son ÉTAT et son HISTOIRE dans les mêmes fichiers, dans la même
typographie, sans frontière : « 263 Ko de modèle » est faux aujourd'hui et
était vrai du temps de Pyodide, une ligne plus haut. Un lecteur ne tranche pas,
et un test qui corrigerait ce chiffre abîmerait le récit.

D'où la distinction que ce script rend mécanique, et qui est tout son objet :

``etat``
    La zone décrit ce qui est VRAI AUJOURD'HUI. Tout chiffre y est ancré sur
    une sonde qui le recalcule, et un chiffre nu y est refusé.
``recit``
    La zone raconte ce qui s'est passé un jour : un procès-verbal, juste à sa
    date. Ses chiffres sont gelés, et il ne faut surtout pas les mettre à jour.
``produit``
    La zone est écrite par un script, qui a déjà son test de péremption.
``a_declarer``
    Personne n'a encore tranché. Le cliquet de ``zones.yaml`` compte ces
    sections, et ce compte ne peut que décroître.

L'ancre
-------

Un chiffre ancré porte, autour de lui, la sonde qui le recalcule ::

    `actuel.py` fait <!--chiffre:lignes(src/retraite_notionnelle/scenarios/actuel.py)-->4 251<!--/--> lignes

C'est le geste de ``construire_regimes_md.py``, qui écrit ``docs/regimes.md``
entre deux repères — en plus fin : le repère tient dans une phrase au lieu
d'encadrer un tableau, et le commentaire HTML ne se voit ni sur GitHub ni
sur le site.

Une sonde qui arrondit se déclare ::

    <!--chiffre:poids_comprime(moteur/donnees.json)~5%-->310<!--/-->

Ce que le script NE fait pas
----------------------------

Il ne juge pas une phrase, seulement un nombre : « la bascule ne reprend aucun
droit acquis » lui échappe entièrement. C'est l'objet de l'action 34 de la
feuille de route, et les deux se complètent.

Il ne sait pas non plus ancrer un chiffre écrit en toutes lettres. Il les
signale dans les zones ``etat`` — « douze mille lignes » est un chiffre comme
un autre, et il avait vieilli de dix mille — avec pour seule issue de le
réécrire en chiffres.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
ZONES = RACINE / "data" / "reference" / "prose" / "zones.yaml"

# --------------------------------------------------------------------------
# Les sondes : le vocabulaire fermé de ce qu'un chiffre peut affirmer.
# --------------------------------------------------------------------------


def _fichiers(motif: str) -> list[Path]:
    """Les fichiers d'un chemin, d'un motif, ou de plusieurs joints par « + ».

    Un terme précédé de « - » est RETIRÉ de ce que les précédents ont réuni.
    C'est ce qui permet de dire le poids du premier chargement sans y compter
    les modules chargés à la demande : ``moteur/js/*.js - moteur/js/lecture-pdf.js``
    désigne le moteur moins son lecteur de PDF, que le navigateur ne télécharge
    que si quelqu'un dépose un relevé. Sans ce retrait, la phrase du README
    annonçait un poids que le lecteur ne transfère pas.
    """
    reels: list[Path] = []
    retires: list[Path] = []
    # Le séparateur est le signe ENTOURÉ D'ESPACES, et rien d'autre : un nom de
    # fichier porte des traits d'union — « lecture-pdf.js » — et découper sur le
    # signe seul cherchait un fichier nommé « moteur/js/lecture ».
    for terme in re.split(r"\s+(?=[+-]\s)", motif):
        part = terme.strip()
        enlever = part.startswith("-")
        part = part.lstrip("+-").strip()
        if not part:
            continue
        trouves = sorted(RACINE.glob(part)) if any(c in part for c in "*?[") \
            else [RACINE / part]
        morceau = [f for f in trouves if f.is_file()]
        if not morceau:
            raise ValueError(f"aucun fichier pour « {part} »")
        (retires if enlever else reels).extend(morceau)
    return [f for f in reels if f not in retires]


def sonde_lignes(motif: str) -> float:
    """Nombre de lignes du fichier, ou somme sur les fichiers du motif."""
    return sum(len(f.read_text(encoding="utf-8").splitlines()) for f in _fichiers(motif))


def sonde_fichiers(motif: str) -> float:
    """Nombre de fichiers que le motif désigne."""
    return len(_fichiers(motif))


def sonde_poids(motif: str) -> float:
    """Poids en kilo-octets (1024), somme sur les fichiers du motif."""
    return sum(f.stat().st_size for f in _fichiers(motif)) / 1024


def sonde_poids_comprime(motif: str) -> float:
    """Poids en kilo-octets une fois compressé, comme le sert un hébergeur.

    Chaque fichier est compressé pour lui-même, et les tailles s'ajoutent :
    c'est ce que le navigateur télécharge. Compresser leur concaténation
    donnerait un chiffre plus flatteur que la réalité.
    """
    return sum(len(gzip.compress(f.read_bytes())) for f in _fichiers(motif)) / 1024


def _lignes_csv(chemin: str) -> list[dict]:
    """Les lignes de données d'un CSV du dépôt, commentaires écartés.

    Les tables de `data/reference/` portent leur source et leur mode d'emploi
    en tête, derrière des `#` : c'est ainsi que le modèle les lit
    (`charger_serie_annuelle`), et les compter pour des données donnerait,
    sur `duree_assurance_requise.csv`, une dizaine de lignes qui n'existent
    pas.
    """
    with (RACINE / chemin).open(encoding="utf-8") as flux:
        lignes = (ligne for ligne in flux if not ligne.lstrip().startswith("#"))
        return list(csv.DictReader(lignes))


def sonde_lignes_csv(chemin: str) -> float:
    """Nombre de lignes de données d'un CSV — ni en-tête ni commentaires."""
    return len(_lignes_csv(chemin))


def _colonne_csv(argument: str) -> tuple[list[dict], str, float, str]:
    """``fichier.csv:colonne[*facteur][?clé=valeur&…]``, décomposé.

    Le facteur est là pour deux raisons, et elles reviennent partout : le
    dépôt stocke les taux en fraction — `coefficient_minoration.csv` porte
    0,01250 — quand la prose les écrit en pour-cent, et il stocke en montant
    annuel ce que la prose donne au mois. `coefficient*100` et `valeur/12`
    disent ce passage au lieu de le taire.
    """
    if ":" not in argument:
        raise ValueError("il faut « fichier.csv:colonne?clé=valeur »")
    chemin, reste = argument.split(":", 1)
    specification, _, condition = reste.partition("?")
    if "/" in specification:
        colonne, _, diviseur = specification.partition("/")
        facteur = str(1 / float(diviseur))
    else:
        colonne, _, facteur = specification.partition("*")
    lignes = _lignes_csv(chemin)
    if lignes and colonne not in lignes[0]:
        raise ValueError(f"« {colonne} » n'est pas une colonne de {chemin} ; "
                         f"il y a {', '.join(lignes[0])}")
    for critere in filter(None, condition.split("&")):
        champ, _, valeur = critere.partition("=")
        if lignes and champ not in lignes[0]:
            raise ValueError(f"« {champ} » n'est pas une colonne de {chemin}")
        lignes = [l for l in lignes if l[champ] == valeur]
    return lignes, colonne, float(facteur) if facteur else 1.0, chemin


def sonde_cellule(argument: str) -> float:
    """Une cellule d'un CSV : ``fichier.csv:colonne?clé=valeur``.

    C'est ce qui manquait pour ancrer un paramètre de DROIT : la durée requise
    d'une génération, l'âge légal d'une autre, le taux de décote d'un
    trimestre. Ils vivent dans les tables certifiées de
    `data/reference/legislation/`, une ligne par génération ou par année, et
    aucune sonde ne savait y descendre — `limites.md` les recopiait donc à la
    main. Plusieurs critères se joignent par `&`, et la désignation doit
    tomber sur une ligne et une seule : deux lignes, c'est une désignation qui
    ne dit pas ce qu'elle croit dire.
    """
    lignes, colonne, facteur, chemin = _colonne_csv(argument)
    if len(lignes) != 1:
        raise ValueError(f"« {argument} » désigne {len(lignes)} lignes de "
                         f"{chemin}, il en faut une")
    return float(lignes[0][colonne].replace(",", ".")) * facteur


def _bornes_csv(argument: str) -> list[float]:
    lignes, colonne, facteur, chemin = _colonne_csv(argument)
    valeurs = [float(l[colonne].replace(",", ".")) * facteur
               for l in lignes if l[colonne] not in ("", None)]
    if not valeurs:
        raise ValueError(f"« {argument} » ne rend aucune valeur de {chemin}")
    return valeurs


def sonde_minimum(argument: str) -> float:
    """La plus petite valeur d'une colonne : ``fichier.csv:colonne?clé=valeur``.

    Une table de droit se décrit par ses bornes — « 151 → 172 trimestres »,
    « 60 → 64 ans » —, et ce sont elles qui bougent quand une réforme entre.
    """
    return min(_bornes_csv(argument))


def sonde_maximum(argument: str) -> float:
    """La plus grande valeur d'une colonne, mêmes règles que `minimum`."""
    return max(_bornes_csv(argument))


def sonde_distinctes(argument: str) -> float:
    """Combien de valeurs différentes une colonne porte.

    Une table peut ranger en lignes ce que la prose compte en colonnes : les
    coefficients de revalorisation des salaires portés au compte tiennent une
    ligne par couple (circulaire, année de perception), et ce que le lecteur
    veut savoir est le nombre de CIRCULAIRES.
    """
    lignes, colonne, facteur, _ = _colonne_csv(argument)
    return len({l[colonne] for l in lignes})


def sonde_partout(argument: str) -> float:
    """La valeur qu'un champ porte dans toutes les entrées qu'on désigne.

    ``regimes.*.periodes.*.plafond_majoration_enfants`` : le plafond de la
    majoration familiale de l'Agirc-Arrco est écrit dans chaque période de
    chaque fiche, et la prose l'annonce une fois. La sonde refuse dès que deux
    entrées ne portent pas la même valeur — c'est tout son intérêt : une prose
    qui annonce un nombre unique ment dès qu'il cesse de l'être.
    """
    argument, facteur = _facteur(argument)
    valeurs = _charge(argument)
    valeurs = valeurs if isinstance(valeurs, list) else [valeurs]
    distinctes = {float(v) * facteur for v in valeurs if isinstance(v, (int, float))}
    if not distinctes:
        raise ValueError(f"« {argument} » ne rend aucun nombre")
    if len(distinctes) > 1:
        raise ValueError(f"« {argument} » rend {len(distinctes)} valeurs "
                         f"différentes ({sorted(distinctes)}), pas une")
    return distinctes.pop()


def _descendre(donnees, chemin: str, origine: str):
    """``clé.sous_clé``, et ``*`` pour traverser toutes les entrées d'un cran.

    ``institutions.*.jeux`` rend la réunion des jeux de toutes les
    institutions : le manifeste des sources range ses jeux par institution, et
    leur nombre — le seul qui intéresse le lecteur — ne se lit nulle part sans
    ce passage. Il était écrit en toutes lettres, « cent vingt jeux », pour
    161.
    """
    for rang, cle in enumerate(chemin.split(".")):
        if cle == "*":
            reste = ".".join(chemin.split(".")[rang + 1:])
            suite = donnees.values() if isinstance(donnees, dict) else donnees
            reuni = []
            for branche in suite:
                if not reste:
                    reuni.append(branche)
                    continue
                try:
                    feuille = _descendre(branche, reste, origine)
                except ValueError:
                    continue      # une entrée qui ne porte pas le champ
                reuni += list(feuille) if isinstance(feuille, (list, dict)) \
                    else [feuille]
            if not reuni:
                raise ValueError(f"« {chemin} » ne rend rien dans {origine}")
            return reuni
        if isinstance(donnees, list) and "=" in cle:
            # « code=regime_general » : l'entrée d'une liste qui porte ce champ.
            # Les fiches de régime sont des listes, et leur rang n'y dit rien.
            champ, _, voulu = cle.partition("=")
            trouves = [e for e in donnees
                       if isinstance(e, dict) and str(e.get(champ)) == voulu]
            if len(trouves) != 1:
                raise ValueError(f"« {cle} » désigne {len(trouves)} entrées "
                                 f"dans {origine}, il en faut une")
            donnees = trouves[0]
        elif isinstance(donnees, list):
            donnees = donnees[int(cle)]
        elif cle in donnees:
            donnees = donnees[cle]
        else:
            raise ValueError(f"« {cle} » introuvable dans {origine}")
    return donnees


def _facteur(argument: str) -> tuple[str, float]:
    """``…*100`` ou ``…/12`` en fin d'argument : le changement d'unité.

    Le même que celui des sondes de CSV : une fiche stocke 0,4466 quand la
    prose écrit 44,66 %.
    """
    trouve = re.search(r"([*/])([\d.]+)$", argument)
    if not trouve:
        return argument, 1.0
    nombre = float(trouve.group(2))
    return argument[: trouve.start()], nombre if trouve.group(1) == "*" else 1 / nombre


def _charge(argument: str):
    """``fichier:clé.sous_clé`` ; le fichier peut être un YAML ou un JSON.

    Un cran ``champ=valeur`` choisit, dans une liste, l'entrée qui le porte :
    ``regimes.code=regime_general.periodes.debut=2023.part_salariale``.
    """
    if ":" not in argument:
        raise ValueError("il faut « fichier:clé.sous_clé »")
    chemin, cle = argument.split(":", 1)
    texte = (RACINE / chemin).read_text(encoding="utf-8")
    donnees = json.loads(texte) if chemin.endswith(".json") \
        else yaml.safe_load(texte)
    return _descendre(donnees, cle, chemin) if cle else donnees


def sonde_entrees(argument: str) -> float:
    """Longueur d'une liste ou d'un dictionnaire, filtre optionnel.

    ``fichier:clé`` compte tout ; ``fichier:clé?champ=a|b`` ne compte que les
    entrées dont ``champ`` vaut l'une des valeurs données. C'est ce qui sépare,
    dans l'inventaire, les 89 lignes des 72 régimes calculés.
    """
    filtre = None
    if "?" in argument:
        argument, condition = argument.split("?", 1)
        champ, _, valeurs = condition.partition("=")
        filtre = (champ, set(valeurs.split("|")))
    entrees = _charge(argument)
    if filtre is None:
        return len(entrees)
    champ, valeurs = filtre
    suite = entrees.values() if isinstance(entrees, dict) else entrees
    return sum(1 for e in suite if str(e.get(champ)) in valeurs)


def sonde_valeur(argument: str) -> float:
    """Valeur scalaire d'un YAML : ``fichier.yaml:clé.sous_clé``, ``*100`` au besoin."""
    argument, facteur = _facteur(argument)
    valeur = _charge(argument)
    if not isinstance(valeur, (int, float)):
        raise ValueError(f"« {argument} » ne rend pas un nombre mais {type(valeur).__name__}")
    return float(valeur) * facteur


_COMPTE_TESTS: list[float] = []


def sonde_tests(_: str = "") -> float:
    """Nombre de tests que pytest collecte, compté dans un autre processus.

    Dans celui-ci, le compte serait faux dès qu'on lance un sous-ensemble.
    C'est la leçon de ``test_le_README_dit_le_vrai_nombre_de_tests``, que
    cette sonde remplace en la rendant disponible à toute la prose.
    """
    if not _COMPTE_TESTS:
        collecte = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "pytest", "--collect-only", "-q",
             "-p", "no:cacheprovider", str(RACINE / "tests")],
            capture_output=True, text=True, encoding="utf-8", cwd=RACINE,
        )
        trouve = re.search(r"(\d+) tests? collected", collecte.stdout)
        if not trouve:
            raise ValueError(f"collecte illisible : {collecte.stdout[-300:]}")
        _COMPTE_TESTS.append(float(trouve.group(1)))
    return _COMPTE_TESTS[0]


def sonde_tenu(nom: str) -> None:
    """Le chiffre est tenu ailleurs, par un test qu'on nomme.

    Rend ``None`` : rien n'est recalculé ici. Mais le test nommé doit exister,
    de sorte qu'on ne puisse pas le supprimer ou le renommer en laissant
    derrière soi un chiffre que plus personne ne tient.
    """
    for fichier in (RACINE / "tests").rglob("*.py"):
        if re.search(rf"^def {re.escape(nom)}\(", fichier.read_text(encoding="utf-8"),
                     re.MULTILINE):
            return None
    raise ValueError(f"aucun test ne s'appelle « {nom} » dans tests/")


def sonde_illustration(_: str = "") -> None:
    """Le nombre est un exemple, pas une affirmation sur le dépôt.

    « un « −12,5 % » deviendrait « −13 % » d'un côté et « −12 % » de l'autre »
    illustre un arrondi ; aucun de ces trois nombres ne prétend décrire quoi
    que ce soit. La limite est celle que l'action 34 de la feuille de route
    pose pour les affirmations du site, et elle se tient en relecture : est une
    illustration ce qui ne peut pas devenir faux.
    """
    return None


def sonde_a_verifier(raison: str) -> None:
    """Personne ne tient ce chiffre, et voici pourquoi — une dette, comptée.

    C'est l'aveu, pas l'échappatoire : le cliquet de ``zones.yaml`` compte ces
    ancres et ne les laisse que décroître. Une zone d'état peut donc être
    déclarée avant que tous ses chiffres soient calculables, sans que le dépôt
    oublie lesquels ne le sont pas.
    """
    if len(raison) < 15:
        raise ValueError("un « à vérifier » sans raison lisible n'en est pas un")
    return None


def sonde_mesure(argument: str) -> float:
    """Ce que le modèle calcule : ``nom?clé=valeur``, voir `mesures_prose.py`.

    Les autres sondes lisent le dépôt ; celle-ci lit le MODÈLE — un écart de
    pension, un coût en milliards, une part de PIB. C'est la matière des six
    résultats du README et du §5 de `limites.md`, qu'aucune table ne porte et
    que la prose recopiait d'une exécution.
    """
    sys.path.insert(0, str(RACINE / "scripts"))
    from mesures_prose import mesurer

    return mesurer(argument)


SONDES = {
    "tenu": sonde_tenu,
    "illustration": sonde_illustration,
    "a_verifier": sonde_a_verifier,
    "lignes": sonde_lignes,
    "fichiers": sonde_fichiers,
    "poids": sonde_poids,
    "poids_comprime": sonde_poids_comprime,
    "lignes_csv": sonde_lignes_csv,
    "cellule": sonde_cellule,
    "minimum": sonde_minimum,
    "maximum": sonde_maximum,
    "distinctes": sonde_distinctes,
    "partout": sonde_partout,
    "entrees": sonde_entrees,
    "valeur": sonde_valeur,
    "tests": sonde_tests,
    "mesure": sonde_mesure,
}

# --------------------------------------------------------------------------
# Lire les chiffres de la prose.
# --------------------------------------------------------------------------

#: Ce qui fait d'un nombre une affirmation, et non une date ou une référence.
UNITES = (
    "%", "€", "Ko", "Mo", "Go",
    "lignes?", "tests?", "régimes?", "statuts?", "fiches?", "valeurs?",
    "fichiers?", "sections?", "colonnes?", "cellules?", "pages?", "caractères?",
    "entrées?", "sources?", "séries?", "cas types?", "scénarios?",
    "millions?", "milliards?", "points?", "ans", "trimestres?",
    "secondes?", "minutes?", "heures?",
)
_UNITE = "|".join(UNITES)

#: Un nombre : « 4 251 », « 79,5 », « −28 », « 2874 », « 11 975,57 ». Le
#: séparateur de milliers du dépôt est l'espace ordinaire. La décimale
#: manquait au premier motif, et « 7 603,41 » se lisait donc comme DEUX
#: nombres — l'ancre le refusait, et une correction en aurait fait « 7 603 ».
#: L'espace insécable et l'espace fine, que la prose emploie aussi — « 1 569 € »
#: —, devaient être dans la classe ; ils y étaient devenus deux espaces
#: ordinaires, et « 1 569 » se lisait lui aussi comme deux nombres.
_NOMBRE = r"[−+-]?\d{1,3}(?:[ \u00a0\u202f]\d{3})+(?:,\d+)?|[−+-]?\d+(?:,\d+)?"

_ESPACE = r"[ \t]*\n?[ \t]*"   # la coupe de ligne, jamais le blanc de paragraphe
CHIFFRE = re.compile(rf"(?<![\w.-])({_NOMBRE}){_ESPACE}({_UNITE})(?![\w'’])")

#: Les mêmes, en toutes lettres — ceux que l'ancre ne sait pas tenir.
_LETTRES = (r"(?:un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|"
            r"treize|quatorze|quinze|seize|vingt|trente|quarante|cinquante|"
            r"soixante|cent|cents|mille|million|millions|milliard|milliards)")
CHIFFRE_LETTRES = re.compile(
    rf"\b((?:{_LETTRES}[- ]){{0,3}}(?:mille|million|millions|milliard|milliards|cents?))"
    rf"{_ESPACE}(?:de{_ESPACE})?({_UNITE})(?![\w'’])", re.IGNORECASE)

ANCRE = re.compile(r"<!--chiffre:(\w+)\(([^)]*)\)(?:~([\d,.]+)%)?-->(.*?)<!--/-->", re.DOTALL)


def _blocs_de_code(texte: str) -> set[int]:
    """Les lignes d'un bloc clôturé. Une ancre y est une citation de syntaxe,
    pas une ancre : `docs/fraicheur.md` montre la forme de l'ancre, et il ne
    faut pas que le contrôle aille chercher le fichier qu'elle nomme."""
    dedans, lignes = False, set()
    for numero, ligne in enumerate(texte.split("\n"), 1):
        if ligne.lstrip().startswith("```"):
            dedans = not dedans
            lignes.add(numero)
        elif dedans:
            lignes.add(numero)
    return lignes


def _nettoyer(texte: str) -> str:
    """Masque ce qui n'est pas de la prose, sans déplacer un seul caractère.

    Les blocs et les incises de code portent des numéros d'article, des
    options et des extraits de sortie ; les adresses portent des ancres. Rien
    de tout cela n'est une affirmation, et tout y ressemble.
    """
    lignes = texte.split("\n")
    dans_bloc = False
    for i, ligne in enumerate(lignes):
        if ligne.lstrip().startswith("```"):
            dans_bloc = not dans_bloc
            lignes[i] = " " * len(ligne)
            continue
        if dans_bloc or ligne.startswith("    ") or ligne.startswith("\t"):
            lignes[i] = " " * len(ligne)
    texte = "\n".join(lignes)
    for motif in (r"`[^`\n]*`", r"<!--.*?-->", r"\]\([^)\s]*\)", r"https?://\S+"):
        texte = re.sub(motif, lambda m: " " * len(m.group(0)), texte, flags=re.DOTALL)
    return texte


# --------------------------------------------------------------------------
# Découper un document en sections, et savoir de quelle zone chacune relève.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Section:
    titre: str          # le titre sans ses dièses, « (préambule) » avant le premier
    debut: int          # numéro de la première ligne, à partir de 1
    fin: int            # numéro de la dernière ligne, incluse


def decouper(texte: str) -> list[Section]:
    """Les sections du document, titre par titre.

    Un ``#`` dans un bloc de code clôturé est un commentaire de programme, pas
    un titre : le README en porte neuf, qui ouvraient autant de sections
    fantômes — « Le cas général : grille cas type × génération » est une ligne
    de Python. Elles gonflaient le cliquet et, plus grave, coupaient la
    section réelle qui les contient : un régime déclaré sur elle ne valait
    alors que jusqu'au premier commentaire.
    """
    lignes = texte.split("\n")
    citations = _blocs_de_code(texte)
    marques = [(i, re.match(r"(#{1,6}) (.+)", l)) for i, l in enumerate(lignes, 1)
               if i not in citations]
    titres = [(i, m.group(2).strip()) for i, m in marques if m]
    sections, debut_corps = [], titres[0][0] if titres else len(lignes) + 1
    if debut_corps > 1:
        sections.append(Section("(préambule)", 1, debut_corps - 1))
    for rang, (ligne, titre) in enumerate(titres):
        fin = titres[rang + 1][0] - 1 if rang + 1 < len(titres) else len(lignes)
        sections.append(Section(titre, ligne, fin))
    return sections


class Zonage:
    """La déclaration de ``zones.yaml``, interrogeable ligne par ligne."""

    def __init__(self, declaration: dict):
        self.fichiers = declaration.get("fichiers", {}) or {}
        self.cliquet = declaration.get("cliquet", {}) or {}

    def regime(self, fichier: str, section: Section) -> str:
        regle = self.fichiers.get(fichier)
        if regle is None:
            return "a_declarer"
        return (regle.get("sections", {}) or {}).get(
            section.titre, regle.get("defaut", "a_declarer"))

    def prefixes_recit(self, fichier: str) -> list[str]:
        regle = self.fichiers.get(fichier) or {}
        return regle.get("paragraphes_recit", []) or []

    def blocs_produits(self, fichier: str) -> list[str]:
        """Les repères dont un script écrit le contenu.

        Un tableau que `construire_tableaux_md.py` réécrit depuis le modèle
        n'a pas à porter une ancre par cellule : il est tenu par son script et
        par le test qui refuse une prose périmée — c'est le régime `produit`,
        mais sur un BLOC au lieu d'une section entière, parce qu'un document
        mêle la prose et ce qui se calcule.
        """
        regle = self.fichiers.get(fichier) or {}
        return regle.get("blocs_produits", []) or []


def lignes_produites(lignes: list[str], reperes: list[str]) -> set[int]:
    """Les lignes qu'un script écrit, repère par repère.

    Les deux lignes de repère comprises : elles ne portent pas de chiffre, et
    les inclure évite d'avoir à dire de quel côté elles tombent.
    """
    produites: set[int] = set()
    for repere in reperes:
        debut, fin = f"<!-- {repere}:debut -->", f"<!-- {repere}:fin -->"
        dedans = False
        for numero, ligne in enumerate(lignes, 1):
            if ligne.strip() == debut:
                dedans = True
            if dedans:
                produites.add(numero)
            if ligne.strip() == fin:
                dedans = False
    return produites


def paragraphes_geles(lignes: list[str], prefixes: list[str]) -> set[int]:
    """Les lignes d'un procès-verbal enclavé dans une section d'état.

    « **Ce que ça a déplacé.** » ouvre, dans une action de la feuille de route,
    un paragraphe qui date : ses chiffres sont ceux du jour où l'action a été
    faite, et les rafraîchir serait réécrire l'histoire.
    """
    if not prefixes:
        return set()
    geles, gele = set(), False
    for numero, ligne in enumerate(lignes, 1):
        if any(ligne.startswith(prefixe) for prefixe in prefixes):
            gele = True
        elif not ligne.strip():
            gele = False
        elif ligne.startswith("#"):
            gele = False
        if gele:
            geles.add(numero)
    return geles


# --------------------------------------------------------------------------
# Confronter.
# --------------------------------------------------------------------------


@dataclass
class Anomalie:
    fichier: str
    ligne: int
    genre: str      # « derive », « sonde », « nu », « lettres », « section »
    message: str


def _en_nombre(texte: str) -> float:
    return float(unicodedata.normalize("NFKC", texte)
                 .replace("−", "-").replace(" ", "").replace(" ", "")
                 .replace(",", "."))


def _ecrire_comme(valeur: float, modele: str) -> str:
    """Réécrit une valeur dans la typographie du chiffre qu'elle remplace."""
    decimales = len(modele.split(",")[1]) if "," in modele else 0
    rendu = f"{valeur:.{decimales}f}"
    signe, chiffres = ("-", rendu[1:]) if rendu.startswith("-") else ("", rendu)
    entier, _, fraction = chiffres.partition(".")
    separateur = next((e for e in (" ", "\u00a0", "\u202f") if e in modele), "")
    if separateur:
        entier = separateur.join(
            [entier[: len(entier) % 3 or 3]]
            + [entier[i:i + 3] for i in range(len(entier) % 3 or 3, len(entier), 3)]
        )
    # Un chiffre écrit avec un signe typographique — « −1,13 », « +7,96 » —
    # est un chiffre SIGNÉ : il garde un signe, quel que soit celui que la
    # valeur prend. Le trait d'union, lui, ne sert qu'aux négatifs.
    if modele[:1] in ("−", "+"):
        signe = "−" if signe else "+"
    return f"{signe}{entier}" + (f",{fraction}" if fraction else "")


def verifier_ancres(fichier: str, texte: str) -> tuple[str, list[Anomalie]]:
    """Recalcule chaque chiffre ancré ; rend le texte corrigé et les écarts."""
    anomalies: list[Anomalie] = []
    citations = _blocs_de_code(texte)

    def remplacer(trouve: re.Match) -> str:
        nom, argument, tolerance, ecrit = trouve.groups()
        ligne = texte[: trouve.start()].count("\n") + 1
        if ligne in citations:
            return trouve.group(0)
        if nom not in SONDES:
            anomalies.append(Anomalie(fichier, ligne, "sonde",
                                      f"sonde inconnue « {nom} » ; "
                                      f"vocabulaire : {', '.join(sorted(SONDES))}"))
            return trouve.group(0)
        try:
            attendu = SONDES[nom](argument)
        except Exception as souci:                      # noqa: BLE001
            anomalies.append(Anomalie(fichier, ligne, "sonde",
                                      f"{nom}({argument}) ne répond pas : {souci}"))
            return trouve.group(0)
        if attendu is None:      # tenu ailleurs, illustration, ou dette avouée
            return trouve.group(0)
        nombres = re.findall(_NOMBRE, ecrit)
        if len(nombres) != 1:
            anomalies.append(Anomalie(fichier, ligne, "derive",
                                      f"l'ancre {nom}({argument}) entoure "
                                      f"{len(nombres)} nombres, il en faut un"))
            return trouve.group(0)
        dit = _en_nombre(nombres[0])
        # La prose arrondit : « 670 Ko » est juste pour 670,42. On compare donc
        # à la précision qu'elle s'est donnée, et pas au-delà.
        decimales = len(nombres[0].split(",")[1]) if "," in nombres[0] else 0
        attendu = round(attendu, decimales)
        marge = float(tolerance.replace(",", ".")) / 100 if tolerance else 0.0
        if abs(dit - attendu) <= max(marge * abs(attendu), 10 ** -9):
            return trouve.group(0)
        juste = _ecrire_comme(attendu, nombres[0])
        anomalies.append(Anomalie(
            fichier, ligne, "derive",
            f"la prose dit {nombres[0]}, {nom}({argument}) en donne {juste}"))
        # Le remplacement porte sur le CONTENU de l'ancre, jamais sur sa
        # sonde : « 0 » provisoire autour de ``annee=2070`` réécrivait
        # l'argument en « annee=251170 », premier « 0 » venu.
        debut, fin = trouve.span(4)
        contenu = ecrit.replace(nombres[0], juste, 1)
        return (trouve.group(0)[: debut - trouve.start()] + contenu
                + trouve.group(0)[fin - trouve.start():])

    return ANCRE.sub(remplacer, texte), anomalies


def verifier_zones(fichier: str, texte: str, zonage: Zonage) -> list[Anomalie]:
    """Dans une zone d'état, un chiffre nu est une promesse que rien ne tient."""
    anomalies: list[Anomalie] = []
    lignes = texte.split("\n")
    # Un chiffre ancré est déjà tenu : on efface l'ancre AVEC son contenu, et
    # sans bouger un caractère, pour que le reste du texte reste contrôlé.
    masque = _nettoyer(ANCRE.sub(lambda m: " " * len(m.group(0)), texte))
    geles = paragraphes_geles(lignes, zonage.prefixes_recit(fichier))
    geles |= lignes_produites(lignes, zonage.blocs_produits(fichier))
    regle = zonage.fichiers.get(fichier)
    declarees = set((regle or {}).get("sections", {}) or {})
    etat = set()
    for section in decouper(texte):
        if regle is not None and section.titre in declarees:
            declarees.discard(section.titre)
        if zonage.regime(fichier, section) == "etat":
            etat.update(range(section.debut, section.fin + 1))
    a_tenir = etat - geles
    for motif, genre, dire in (
        (CHIFFRE, "nu", "n'est ancré sur rien"),
        (CHIFFRE_LETTRES, "lettres",
         ": un chiffre en toutes lettres ne s'ancre pas ; le réécrire en chiffres"),
    ):
        for trouve in motif.finditer(masque):
            numero = masque[: trouve.start()].count("\n") + 1
            if numero not in a_tenir:
                continue
            ecrit = " ".join(trouve.group(0).split())
            anomalies.append(Anomalie(fichier, numero, genre, f"« {ecrit} » {dire}"))
    for orpheline in sorted(declarees):
        anomalies.append(Anomalie(fichier, 0, "section",
                                  f"zones.yaml déclare « {orpheline} », "
                                  "qui n'est plus dans le document"))
    return anomalies


def documents(zonage: Zonage) -> list[str]:
    """Les documents soumis au contrôle : ceux que zones.yaml énumère."""
    return sorted(zonage.fichiers)


def inventorier(zonage: Zonage) -> dict[str, list[str]]:
    """Les sections dont personne n'a encore dit ce qu'elles affirment."""
    reste: dict[str, list[str]] = {}
    for fichier in documents(zonage):
        chemin = RACINE / fichier
        if not chemin.exists():
            continue
        texte = chemin.read_text(encoding="utf-8")
        titres = [s.titre for s in decouper(texte)
                  if zonage.regime(fichier, s) == "a_declarer"]
        if titres:
            reste[fichier] = titres
    return reste


def controler(zonage: Zonage, corriger: bool) -> tuple[list[Anomalie], list[str]]:
    anomalies: list[Anomalie] = []
    reecrits: list[str] = []
    for fichier in documents(zonage):
        chemin = RACINE / fichier
        if not chemin.exists():
            anomalies.append(Anomalie(fichier, 0, "section",
                                      "zones.yaml déclare un fichier absent"))
            continue
        texte = chemin.read_text(encoding="utf-8")
        corrige, ecarts = verifier_ancres(fichier, texte)
        anomalies += ecarts
        anomalies += verifier_zones(fichier, texte, zonage)
        if corriger and corrige != texte:
            chemin.write_text(corrige, encoding="utf-8", newline="\n")
            reecrits.append(fichier)
    return anomalies, reecrits


def compter_dettes() -> int:
    """Les ancres ``a_verifier`` du dépôt : ce qu'on s'est avoué devoir."""
    total = 0
    for fichier in sorted(RACINE.glob("*.md")) + sorted((RACINE / "docs").glob("*.md")):
        texte = fichier.read_text(encoding="utf-8")
        citations = _blocs_de_code(texte)
        for trouve in ANCRE.finditer(texte):
            if texte[: trouve.start()].count("\n") + 1 in citations:
                continue
            total += trouve.group(1) == "a_verifier"
    return total


def _cliquet(nom: str, reel: int, inscrit, quoi: str, remede: str) -> list[Anomalie]:
    if inscrit is None:
        return [Anomalie("zones.yaml", 0, "cliquet",
                         f"le cliquet n'est pas posé : ajouter cliquet.{nom}: {reel}")]
    if reel > inscrit:
        return [Anomalie("zones.yaml", 0, "cliquet",
                         f"{reel} {quoi}, le cliquet en admet {inscrit} : {remede}")]
    if reel < inscrit:
        return [Anomalie("zones.yaml", 0, "cliquet",
                         f"{reel} {quoi} et le cliquet en admet encore "
                         f"{inscrit} : l'abaisser à {reel}")]
    return []


def controler_cliquet(zonage: Zonage) -> list[Anomalie]:
    """Le compte des sections non déclarées ne peut que décroître.

    C'est la seule clause qui fasse avancer le dépôt sans qu'on y pense : une
    session qui ajoute une section la déclare, et celle qui en déclare une
    vieille abaisse le cliquet. Le jour où il tombe à zéro, plus un chiffre du
    dépôt n'est un souvenir.
    """
    return (
        _cliquet("sections_a_declarer",
                 sum(len(t) for t in inventorier(zonage).values()),
                 zonage.cliquet.get("sections_a_declarer"),
                 "sections ne sont pas déclarées",
                 "les déclarer dans zones.yaml (--inventaire les liste)")
        + _cliquet("chiffres_a_verifier", compter_dettes(),
                   zonage.cliquet.get("chiffres_a_verifier"),
                   "chiffres portent une ancre « a_verifier »",
                   "leur donner une sonde qui les recalcule")
    )


# --------------------------------------------------------------------------


def charger_zonage() -> Zonage:
    return Zonage(yaml.safe_load(ZONES.read_text(encoding="utf-8")))


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--corriger", action="store_true",
                           help="réécrire les chiffres ancrés qui ont dérivé")
    analyseur.add_argument("--inventaire", action="store_true",
                           help="lister les sections qui ne sont pas déclarées")
    analyseur.add_argument("--sondes", action="store_true",
                           help="lister le vocabulaire des sondes")
    arguments = analyseur.parse_args()

    if arguments.sondes:
        for nom, sonde in sorted(SONDES.items()):
            premiere = (sonde.__doc__ or "").strip().split("\n")[0]
            print(f"  {nom:16} {premiere}")
        return 0

    zonage = charger_zonage()

    if arguments.inventaire:
        reste = inventorier(zonage)
        for fichier, titres in reste.items():
            print(f"\n{fichier} — {len(titres)} sections à déclarer")
            for titre in titres:
                print(f"    {titre}")
        total = sum(len(t) for t in reste.values())
        print(f"\n{total} sections au total ; cliquet posé à "
              f"{zonage.cliquet.get('sections_a_declarer', '—')}")
        return 0

    anomalies, reecrits = controler(zonage, arguments.corriger)
    anomalies += controler_cliquet(zonage)

    for fichier in reecrits:
        print(f"{fichier} réécrit")
    if arguments.corriger:
        anomalies = [a for a in anomalies if a.genre != "derive"]

    for anomalie in sorted(anomalies, key=lambda a: (a.fichier, a.ligne)):
        localisation = f"{anomalie.fichier}:{anomalie.ligne}" if anomalie.ligne \
            else anomalie.fichier
        print(f"{localisation}: {anomalie.message}", file=sys.stderr)
    if anomalies:
        print(f"\n{len(anomalies)} anomalies", file=sys.stderr)
        return 1
    print("la prose déclarée dit le vrai")
    return 0


if __name__ == "__main__":
    sys.exit(main())
