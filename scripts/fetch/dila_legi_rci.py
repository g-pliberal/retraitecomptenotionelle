#!/usr/bin/env python3
"""Taux des complémentaires obligatoires des indépendants, chez DILA.

    python scripts/fetch/dila_legi_rci.py

**Ce script télécharge environ 1,1 Go et met un quart d'heure.** Comme celui de
la MSA, dont il reprend la mécanique, il n'a pas à être lancé souvent : les
régimes qu'il documente sont fermés depuis 2013 et leurs taux ne bougeront
plus.

POURQUOI IL EXISTE.

Le catalogue routait l'artisan de 1979 à 2005 et le commerçant de 2004 à 2005
vers le RCI, dont la première période commence en 2013 : le moteur ne trouvait
aucune période active, n'ajoutait rien, et ces années ne portaient AUCUNE
cotisation au compte notionnel. Écrire les deux fiches manquantes demandait
leurs taux, et aucune source ouverte ne les porte en série :
OpenFisca-France-Pension ne modélise les indépendants qu'à partir du RCI de
2013 (`independants/salref_rci.yaml`), et les barèmes IPP, sa source amont,
couvrent la CANCAVA et l'ORGANIC — les régimes de BASE — mais pas leur étage
complémentaire.

Ils sont pourtant écrits, décret par décret, dans le code de la sécurité
sociale :

    « Le taux de la cotisation annuelle d'assurance vieillesse complémentaire
      des industriels et commerçants est fixé à 6,5 %. Ce taux s'applique sur
      le revenu professionnel dans une limite égale à trois fois le plafond
      prévu à l'article L. 241-3. »  (D. 635-10, état du 26 mars 2005)

Quatre articles suffisent, et il faut les quatre :

* **D. 635-6** porte le taux des artisans jusqu'en 2004. Trois états le
  couvrent, et deux d'entre eux ÉCHELONNENT plusieurs années d'un coup —
  « à compter du 1er janvier 1997 à 4,90 %, à compter du 1er janvier 1998 à
  5,30 % … » —, si bien qu'une seule version datée donne quatre taux ;
* **D. 635-7** prend le relais en 2004, et le découpe en deux tranches à
  partir de 2008 ;
* **D. 635-10** porte celui des commerçants, de 2004 à 2012 ;
* **D. 635-4** porte l'ASSIETTE d'avant 2004 — « dans la limite d'un plafond
  égal à trois fois celui mentionné à l'article L. 633-10 » —, sans quoi les
  taux seraient appliqués à la mauvaise borne.

DEUX PIÈGES.

* Les mêmes numéros d'article existent dans d'autres codes : `D635-6` et
  `D635-7` sont aussi des articles du code de l'ÉDUCATION, sur le diplôme
  d'État de sage-femme. Le filtre retient donc le contexte et non le seul
  numéro.
* Le *Journal officiel* écrit tantôt « 6,5 % », tantôt « 6, 5 % » — un espace
  après la virgule —, et les textes anciens « 4,40 p. 100 ».

CE QUE LE SCRIPT NE DONNE PAS. Le plus ancien état de D. 635-6 est du
21 décembre 1985 ; les six premières années du régime des artisans, 1979-1984,
ne sont couvertes par aucune version datée. La fiche porte pour elles le taux
de 1985 et le dit.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RACINE = "https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
SORTIE = Path("data/brut/dila_legi_rci.json")

#: Les articles qui portent les taux, et le régime auquel chacun se rapporte.
#: D. 635-7 traverse la fusion : il porte la complémentaire des artisans
#: jusqu'en 2012 et le RCI, qui l'absorbe, à partir de 2013. Un même article,
#: deux régimes — d'où la bascule ci-dessous plutôt qu'un nom fixe.
ARTICLES = {
    "D635-6": "rco_artisans",
    "D635-7": "rco_artisans",
    "D635-10": "nric",
    "D635-4": "assiette",
}

#: Année de la fusion des deux complémentaires dans le RCI.
FUSION = 2013

NOMBRE = r"(\d+(?:\s*,\s*\d+)?)\s*(?:%|p\.\s*100)"

#: « à compter du 1er janvier 1997 à 4,90 % » / « 6,20 % pour l'année 2003 »
ECHELONNE = (
    re.compile(rf"à compter du 1er janvier (\d{{4}})\s*à\s*{NOMBRE}"),
    re.compile(rf"{NOMBRE}\s*pour l'année (\d{{4}})"),
    re.compile(rf"pour l'année (\d{{4}})\s*à\s*{NOMBRE}"),
)

FILTRE = r"""
import re, sys
CIBLE = re.compile(r"<NUM>\s*(D635-4|D635-6|D635-7|D635-10)\s*</NUM>")
BALISES = re.compile(r"<[^>]+>")
tampon = ""
for bloc in iter(lambda: sys.stdin.buffer.read(1 << 20), b""):
    tampon += bloc.decode("utf-8", errors="replace")
    morceaux = tampon.split("<?xml")
    tampon = morceaux.pop()
    for morceau in morceaux:
        cible = CIBLE.search(morceau)
        if not cible or "Code de la s" not in morceau:
            continue
        debut = re.search(r"<DATE_DEBUT>(.*?)</DATE_DEBUT>", morceau)
        texte = re.sub(r"\s+", " ", BALISES.sub(" ", morceau)).strip()
        print("@@@ %s %s" % (cible.group(1), debut.group(1) if debut else "?"))
        print(texte[:3000])
        sys.stdout.flush()
"""


def _nombre(brut: str) -> float:
    return float(re.sub(r"\s", "", brut).replace(",", ".")) / 100.0


def taux(texte: str) -> list[tuple[int, float]]:
    """Les paires (année, taux) qu'une version de l'article échelonne."""
    trouves: dict[int, float] = {}
    for indice, forme in enumerate(ECHELONNE):
        for m in forme.finditer(texte):
            annee, valeur = ((m.group(2), m.group(1)) if indice == 1
                             else (m.group(1), m.group(2)))
            trouves[int(annee)] = _nombre(valeur)
    return sorted(trouves.items())


#: « est due en sus … une cotisation additionnelle fixée à 0,10 p. 100 »
ADDITIONNELLE = re.compile(rf"cotisation additionnelle fixée à\s*{NOMBRE}")

#: « fixé à : 1° 7,2 % … 2° 7,6 % » — le découpage en tranches de 2008
TRANCHES = re.compile(rf"1°\s*{NOMBRE}.{{0,200}}?2°\s*{NOMBRE}", re.S)

#: « fixé pour l'année 2004 à 3,5 % pour le premier semestre et à 4,5 % pour
#: le second semestre » — la seule année que le code écrit en demi-exercices
SEMESTRES = re.compile(
    rf"pour l'année (\d{{4}}) à\s*{NOMBRE}\s*pour le premier semestre "
    rf"et à\s*{NOMBRE}\s*pour le second"
)


def taux_simple(texte: str) -> float | tuple[float, float] | None:
    """Le taux que pose une version qui n'échelonne pas par année.

    Trois rédactions, et il faut les trois : un taux unique, un taux unique
    augmenté d'une cotisation additionnelle — c'est l'état de 1985, dont les
    deux lignes se cumulent —, et le découpage en deux tranches introduit en
    2008, qui est rendu par un couple.
    """
    tranches = TRANCHES.search(texte)
    if tranches and "taux de la cotisation annuelle" in texte:
        return _nombre(tranches.group(1)), _nombre(tranches.group(2))
    m = re.search(rf"taux de la cotisation annuelle[^.]{{0,200}}?fixé à\s*{NOMBRE}",
                  texte)
    if m is None:
        return None
    valeur = _nombre(m.group(1))
    ajout = ADDITIONNELLE.search(texte)
    return valeur + _nombre(ajout.group(1)) if ajout else valeur


def taux_semestriels(texte: str) -> tuple[int, float] | None:
    """L'année que le code écrit en deux demi-exercices, ramenée à sa moyenne.

    La convention du dépôt est un taux ANNUEL : 3,5 % sur six mois puis 4,5 %
    sur les six suivants font 4 % sur l'année.
    """
    m = SEMESTRES.search(texte)
    if m is None:
        return None
    return int(m.group(1)), (_nombre(m.group(2)) + _nombre(m.group(3))) / 2


def dernier_dump() -> str:
    with urllib.request.urlopen(RACINE, timeout=120) as reponse:
        page = reponse.read().decode("utf-8", errors="replace")
    noms = sorted(re.findall(r'href="(Freemium_legi_global_[^"]+\.tar\.gz)"', page))
    if not noms:
        raise LookupError("aucun dump global dans le répertoire LEGI de la DILA")
    return RACINE + noms[-1]


def depouiller(url: str) -> list[tuple[str, str, str]]:
    """Lit le dump en flux : (article, date d'effet, texte), non ordonné."""
    lecture = subprocess.Popen(
        ["curl", "-sS", "--max-time", "5400", url], stdout=subprocess.PIPE
    )
    detar = subprocess.Popen(
        ["tar", "-xzO"], stdin=lecture.stdout, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    lecture.stdout.close()
    filtre = subprocess.Popen(
        [sys.executable, "-c", FILTRE], stdin=detar.stdout,
        stdout=subprocess.PIPE, text=True,
    )
    detar.stdout.close()
    sortie, _ = filtre.communicate()
    lecture.wait()

    versions = []
    for bloc in sortie.split("@@@ ")[1:]:
        entete, _, corps = bloc.partition("\n")
        article, _, debut = entete.strip().partition(" ")
        versions.append((article, debut.strip(), corps))
    return versions


def main() -> int:
    try:
        url = dernier_dump()
    except (urllib.error.HTTPError, urllib.error.URLError, LookupError) as erreur:
        print(f"ÉCHEC   répertoire LEGI : {erreur}", file=sys.stderr)
        return 1

    print(f"Dump      {url.rsplit('/', 1)[-1]}")
    print("Lecture en flux d'environ 9 Go décompressés : comptez un quart d'heure.\n")
    versions = depouiller(url)
    if not versions:
        print("ÉCHEC   aucune version des articles D. 635-* dans le dump",
              file=sys.stderr)
        return 1

    # Une version qui échelonne plusieurs années les donne toutes ; une version
    # qui pose un taux unique le donne pour l'année de son entrée en vigueur et
    # les suivantes, jusqu'à ce qu'une autre le remplace.
    series: dict[str, dict[int, float]] = {
        "rco_artisans": {}, "nric": {}, "rci": {}}
    simples: dict[str, list[tuple[int, float]]] = {
        "rco_artisans": [], "nric": [], "rci": []}
    for article, debut, corps in sorted(versions, key=lambda v: v[1]):
        regime = ARTICLES.get(article)
        if regime not in series:
            continue
        if regime == "rco_artisans" and debut[:4].isdigit() \
                and int(debut[:4]) >= FUSION:
            regime = "rci"
        semestriel = taux_semestriels(corps)
        if semestriel is not None:
            series[regime][semestriel[0]] = semestriel[1]
            continue
        echelonnes = taux(corps)
        if echelonnes:
            series[regime].update(dict(echelonnes))
            continue
        valeur = taux_simple(corps)
        if valeur is not None and debut[:4].isdigit():
            simples[regime].append((int(debut[:4]), valeur))

    for regime, poses in simples.items():
        for annee, valeur in sorted(poses):
            series[regime].setdefault(annee, valeur)

    for regime, serie in series.items():
        if not serie and regime != "rci":
            print(f"ÉCHEC   aucun taux lu pour {regime}", file=sys.stderr)
            return 1
        for annee, valeur in sorted(serie.items()):
            dit = (" / ".join(f"{x:.2%}" for x in valeur)
                   if isinstance(valeur, tuple) else f"{valeur:.2%}")
            print(f"OK      {regime:<14} {annee} : {dit}")
        plates = [x for v in serie.values()
                  for x in (v if isinstance(v, tuple) else (v,))]
        if not all(0.0 < x < 0.20 for x in plates):
            print(f"\nSérie invraisemblable pour {regime}, rien n'est écrit",
                  file=sys.stderr)
            return 1

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": url,
            "articles": "code de la sécurité sociale, D. 635-4, D. 635-6, "
                        "D. 635-7 et D. 635-10",
            "recupere_le": date.today().isoformat(),
            "versions_lues": len(versions),
            "note": "taux de cotisation des complémentaires obligatoires des "
                    "artisans et des commerçants, fondues dans le RCI au "
                    "1er janvier 2013. Le plus ancien état de D. 635-6 est du "
                    "21 décembre 1985 : 1979-1984 n'est couvert par aucune "
                    "version datée.",
            "serie": {f"{r}|{a}|taux_cotisation": v
                      for r, s in series.items() for a, v in sorted(s.items())},
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    total = sum(len(s) for s in series.values())
    print(f"\n{total} taux écrits dans {SORTIE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
