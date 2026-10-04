#!/usr/bin/env python3
"""Minimum contributif et plafond d'écrêtement, dans le code de la sécurité sociale.

    python scripts/fetch/dila_index.py legi --recuperer   # l'index, une fois
    python scripts/fetch/dila_legi_minimum_contributif.py        # une minute
    python scripts/fetch/dila_legi_minimum_contributif.py --dump   # le dump global, 1,1 Go

Le script lit l'index LEGI du dépôt — le dump global plus les incréments
quotidiens de la DILA, qui n'a pas régénéré ce dump depuis juillet 2025 : le
dump seul ignore tout texte paru depuis. ``--dump`` garde l'ancienne voie.

`docs/limites.md` a longtemps écrit que le minimum contributif ne figurait
« dans aucune source machine ouverte », que ses montants n'étaient publiés que
dans des circulaires CNAV en PDF, et qu'il n'y avait donc « pas de chemin de
certification automatique à écrire ». C'était la même erreur que pour la MSA,
et elle se corrige de la même façon : *la donnée est dans la loi, il suffisait
de chercher par le numéro d'article*.

Trois articles suffisent, et ils disent tout :

* **R. 351-25**, dans sa rédaction de 1985 à 2004, porte le premier montant :
  « 26 400 F par an au 1er avril 1983 », revalorisé « aux mêmes dates et selon
  les mêmes taux que les pensions de vieillesse » ;
* **D. 351-2-1** porte les deux montants, en euros et par an — 6 511,06 € et
  6 706,39 € au 1er janvier 2004, …, 8 509,61 € pour le minimum, 10 170,86 €
  pour le minimum majoré au titre des périodes cotisées, au 1er septembre
  2023 ;
* **D. 173-21-0-0-1** porte le plafond d'écrêtement de l'article L. 173-2 :
  « Le montant mensuel total des pensions personnelles de retraite […] est fixé
  à 1 120 euros au 1er février 2014. Ce montant est revalorisé aux mêmes dates
  et dans les mêmes proportions que le salaire minimum de croissance. »

Ce sont des **ancres datées**, non des séries : le code n'est pas modifié à
chaque revalorisation, il la confie à la loi. Chaque ancre est donc écrite À
LA DATE QUE LE TEXTE LUI DONNE — « au 1er janvier 2008 » —, et non à l'entrée
en vigueur de la rédaction qui la porte : la rédaction du 31 décembre 2007
fixe le montant du 1er janvier 2008, que le récupérateur écrivait « 2007 »
jusqu'au 4 octobre 2026. Il ne lisait pas davantage les rédactions de 2004 et
de 2006, qui écrivent « Euros » avec une capitale. Entre deux ancres, ce que
la caisse a réellement servi, date par date, vient de son barème
(``cnav_minimum_contributif.py``).

Les montants sont écrits en euros PAR AN, unité du dépôt : le franc de 1983 est
converti à 6,55957, le plafond, publié au mois, multiplié par douze.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dila_index import filtrer_index  # noqa: E402

RACINE = "https://echanges.dila.gouv.fr/OPENDATA/LEGI/"

#: Les trois articles utiles, et ce qu'on va y chercher.
ARTICLES = ("R351-25", "D351-2-1", "D173-21-0-0-1")

#: Le taux de conversion du franc en euro, fixé le 31 décembre 1998.
FRANCS_PAR_EURO = 6.55957

MOIS = {"janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
        "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11,
        "décembre": 12}

SORTIE = Path("data/brut/dila_legi_minimum_contributif.json")

# Le Journal officiel aère les milliers par une espace insécable et sépare les
# décimales par une virgule : « 8 509,61 euros », « 1 120 euros ».
NOMBRE = r"(\d[\d  ]*(?:,\d+)?)\s*euros?"

#: Les deux montants de D. 351-2-1 sont dans la même unité et se suivent :
#:
#:     « Le montant minimum […] est fixé à 8 509,61 euros par an au
#:       1er septembre 2023. Ce montant minimum est MAJORÉ au titre des
#:       périodes ayant donné lieu à cotisations à la charge de l'assuré, de
#:       façon à atteindre 10 170,86 euros par an au 1er septembre 2023. »
#:
#: Plutôt que de s'accrocher à un verbe — « est fixé à », « est porté à », « de
#: façon à atteindre » : la rédaction a changé trois fois en vingt ans — on
#: relève TOUS les montants annuels de l'article et l'on retient le plus petit
#: pour le minimum, le plus grand pour le majoré. C'est ce que dit le texte, et
#: c'est vérifiable : le script refuse d'écrire si le second n'excède pas le
#: premier.
#: Chaque montant porte sa date : « 6 511,06 Euros par an au 1er janvier
#: 2004 » — avec une capitale en 2004 et 2006 —, « 26 400 F par an au 1er
#: avril 1983 » dans R. 351-25.
FORME_ANNUELLE = re.compile(
    r"(\d[\d  ]*(?:,\d+)?)\s*(euros?|F)\s*par an au 1er (\w+) (\d{4})",
    re.IGNORECASE)
FORME_PLAFOND = re.compile(rf"est fixé à\s*{NOMBRE}\s*au 1er (\w+) (\d{{4}})")

#: Bornes de vraisemblance d'un minimum de pension, en euros par an. Elles
#: écartent une année ou un numéro d'article qu'on aurait pris pour un montant.
MONTANT_MINIMAL, MONTANT_MAXIMAL = 1_000.0, 30_000.0


def _nombre(brut: str) -> float:
    return float(re.sub(r"[\s ]", "", brut).replace(",", "."))


def _jour(mois: str, annee: str) -> str:
    return f"{int(annee):04d}-{MOIS[mois.lower()]:02d}-01"


def montants(texte: str) -> dict[str, tuple[str, float]]:
    """Montants annuels portés par une version de D. 351-2-1 ou de R. 351-25,
    chacun avec la date que le texte lui donne.

    Le plus petit est le minimum, le plus grand sa majoration au titre des
    périodes cotisées. Une version qui n'en porte qu'un — les rédactions
    d'avant la création de la majoration — ne renseigne que le premier.
    """
    valeurs = sorted({
        (valeur, _jour(m.group(3), m.group(4)))
        for m in FORME_ANNUELLE.finditer(texte)
        for valeur in [_nombre(m.group(1)) / (FRANCS_PAR_EURO if m.group(2) == "F" else 1)]
        if MONTANT_MINIMAL <= valeur <= MONTANT_MAXIMAL
    })
    if not valeurs:
        return {}
    (base, jour_base), (majore, jour_majore) = valeurs[0], valeurs[-1]
    if len(valeurs) == 1:
        return {"montant_base": (jour_base, base)}
    return {"montant_base": (jour_base, base), "montant_majore": (jour_majore, majore)}


def plafond(texte: str) -> tuple[str, float] | None:
    """Plafond mensuel de D. 173-21-0-0-1, ramené à l'année, et sa date d'effet."""
    m = FORME_PLAFOND.search(texte)
    if m is None:
        return None
    return _jour(m.group(2), m.group(3)), _nombre(m.group(1)) * 12


def dernier_dump() -> str:
    """L'adresse du dump global le plus récent, que DILA renomme à chaque envoi."""
    with urllib.request.urlopen(RACINE, timeout=120) as reponse:
        page = reponse.read().decode("utf-8", errors="replace")
    noms = sorted(re.findall(r'href="(Freemium_legi_global_[^"]+\.tar\.gz)"', page))
    if not noms:
        raise LookupError("aucun dump global dans le répertoire LEGI de la DILA")
    return RACINE + noms[-1]


FILTRE = r"""
import re, sys
CIBLE = re.compile(r"<NUM>\s*(%s)\s*</NUM>")
BALISES = re.compile(r"<[^>]+>")
tampon = ""
for bloc in iter(lambda: sys.stdin.buffer.read(1 << 20), b""):
    tampon += bloc.decode("utf-8", errors="replace")
    morceaux = tampon.split("<?xml")
    tampon = morceaux.pop()
    for morceau in morceaux:
        trouve = CIBLE.search(morceau)
        if not trouve:
            continue
        debut = re.search(r"<DATE_DEBUT>(.*?)</DATE_DEBUT>", morceau)
        texte = re.sub(r"\s+", " ", BALISES.sub(" ", morceau)).strip()
        print("@@@ %%s %%s" %% (trouve.group(1), debut.group(1) if debut else "?"))
        print(texte[:3000])
        sys.stdout.flush()
"""


def depouiller(url: str) -> list[tuple[str, str, str]]:
    """Lit le dump en flux et renvoie (article, date d'entrée en vigueur, texte)."""
    motif = "|".join(re.escape(a) for a in ARTICLES)
    lecture = subprocess.Popen(
        ["curl", "-sS", "--max-time", "5400", url], stdout=subprocess.PIPE
    )
    detar = subprocess.Popen(
        ["tar", "-xzO"], stdin=lecture.stdout, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    lecture.stdout.close()
    filtre = subprocess.Popen(
        [sys.executable, "-X", "utf8", "-c", FILTRE % motif],
        stdin=detar.stdout, stdout=subprocess.PIPE, text=True, encoding="utf-8",
    )
    detar.stdout.close()
    sortie, _ = filtre.communicate()
    lecture.wait()
    return _analyser(sortie)


def _analyser(sortie: str):
    versions = []
    for bloc in sortie.split("@@@ ")[1:]:
        entete, _, corps = bloc.partition("\n")
        article, _, debut = entete.strip().partition(" ")
        versions.append((article, debut.strip(), corps))
    return versions


def depouiller_index(chemin: str | None = None):
    """Le même filtre, passé sur l'index du dépôt au lieu du dump."""
    motif = "|".join(re.escape(a) for a in ARTICLES)
    sortie, source = filtrer_index("legi", FILTRE % motif, chemin)
    return _analyser(sortie), source


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--dump", action="store_true",
                           help="lire le dump global de la DILA (1,1 Go) au lieu de l'index")
    analyseur.add_argument("--index", help="chemin de l'index LEGI")
    options = analyseur.parse_args(arguments)

    if options.dump:
        try:
            url = dernier_dump()
        except (urllib.error.HTTPError, urllib.error.URLError, LookupError) as erreur:
            print(f"ÉCHEC   répertoire LEGI : {erreur}", file=sys.stderr)
            return 1
        print(f"Dump      {url.rsplit('/', 1)[-1]}")
        print("Lecture en flux d'environ 9 Go décompressés : comptez un quart d'heure.\n")
        lu = depouiller(url)
        source = url
    else:
        try:
            lu, source = depouiller_index(options.index)
        except FileNotFoundError as erreur:
            print(f"ÉCHEC   {erreur}", file=sys.stderr)
            return 1
        print(f"Source    {source}\n")
    versions = lu
    if not versions:
        print("ÉCHEC   aucune version des articles "
              f"{', '.join(ARTICLES)} dans le dump", file=sys.stderr)
        return 1

    # Une ancre est un montant qui CHANGE. L'article est réécrit plus souvent
    # qu'il n'est revalorisé — les versions de 2009 et de 2020 répètent le
    # montant de 2008 sans y toucher, la revalorisation se faisant par l'effet
    # de la loi et non par modification du code. On ne garde donc que la
    # PREMIÈRE version qui porte chaque valeur, à la date que son texte lui
    # donne. Elle seule compte : les rédactions de 2009 et de 2020 datent le
    # majoré de 7 603,41 € « au 1er janvier 2006 », reprise fautive de la
    # rédaction de 2006, quand celle du 31 décembre 2007 l'a fixé au 1er
    # janvier 2008.
    lues: dict[str, list[tuple[str, str, float]]] = {}
    for article, debut, corps in sorted(versions, key=lambda v: (v[1], v[0])):
        if article in ("R351-25", "D351-2-1"):
            if article == "R351-25" and " F par an" not in corps:
                continue  # l'article R. 351-25 renuméroté en 2009 parle d'autre chose
            for mesure, (jour, valeur) in montants(corps).items():
                lues.setdefault(mesure, []).append((debut, jour, valeur))
        else:
            lu = plafond(corps)
            if lu is not None:
                lues.setdefault("plafond_ecretement", []).append((debut, *lu))

    serie: dict[str, float] = {}
    ancres: dict[str, str] = {}
    for mesure, relevees in lues.items():
        precedente = None
        for _, jour, valeur in relevees:
            if precedente is not None and abs(valeur - precedente) < 1e-9:
                continue  # même montant redit : ce n'est pas une nouvelle ancre
            serie[f"{mesure}|{jour}"] = valeur
            ancres[mesure] = jour
            precedente = valeur

    for cle, valeur in sorted(serie.items()):
        mesure, _, jour = cle.partition("|")
        print(f"OK      {mesure} au {jour} : {valeur:,.2f} €/an")

    manquantes = {"montant_base", "montant_majore", "plafond_ecretement"} - set(ancres)
    if manquantes:
        print(f"\nÉCHEC   mesures introuvables : {sorted(manquantes)}", file=sys.stderr)
        return 1
    if serie[f"montant_majore|{ancres['montant_majore']}"] <= serie[
            f"montant_base|{ancres['montant_base']}"]:
        print("\nÉCHEC   le minimum majoré n'est pas supérieur au minimum : "
              "la lecture est fausse, rien n'est écrit", file=sys.stderr)
        return 1

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": source,
            "articles": "code de la sécurité sociale, R. 351-25, D. 351-2-1 et "
                        "D. 173-21-0-0-1",
            "recupere_le": date.today().isoformat(),
            "versions_lues": len(versions),
            "note": "ancres datées, non séries, chacune à la date que le texte "
                    "lui donne : le code n'est pas modifié à chaque "
                    "revalorisation, il la confie à la loi. Montants en euros par "
                    "an ; le franc de 1983 converti à 6,55957, le plafond, publié "
                    "au mois, multiplié par douze.",
            "serie": dict(sorted(serie.items())),
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"\n{len(serie)} ancres écrites dans {SORTIE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
