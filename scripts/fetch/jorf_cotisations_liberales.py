#!/usr/bin/env python3
"""Cotisations des complémentaires libéraux, décret par décret, chez DILA.

    python scripts/fetch/jorf_cotisations_liberales.py
    python scripts/fetch/jorf_cotisations_liberales.py --dump /chemin/JORF.tar.gz

**Ce script télécharge environ 1,7 Go et met une vingtaine de minutes.**

POURQUOI IL EXISTE.

Deux passes avaient conclu que les complémentaires des sections libérales
étaient hors de portée : les caisses ne publient que l'année en cours, et leurs
statuts renvoient les montants au conseil d'administration. Les deux constats
sont vrais et ne concluent rien, parce qu'ils regardaient au mauvais endroit.

**Un décret par an fixe ces montants, pour TOUTES les sections à la fois**, et
le Journal officiel le publie. Son intitulé varie — « fixant pour l'année 2020
les cotisations d'assurance vieillesse complémentaire et d'invalidité-décès des
professions libérales » — mais son corps a toujours la même forme :

    « 5° Section professionnelle des auxiliaires médicaux :
      - cotisation forfaitaire : 1 648 euros ;
      - taux de la cotisation proportionnelle : 3 % ;
      - limites de l'assiette de la cotisation proportionnelle :
        - seuil : 25 246 euros ;
        - plafond : 176 313 euros. »

Ce que ce script en tire, section par section et année par année : la cotisation
forfaitaire, le taux proportionnel, les bornes de l'assiette, la valeur d'achat
du point, le montant de la première classe, le taux d'appel. Soit la série que
personne ne publiait — 1998 à 2024 selon les sections.

TROIS PIÈGES DE FORME, ET CE QUE LE SCRIPT EN FAIT.

* **L'UNITÉ CHANGE DE NOM** : « EUR » jusqu'en 2007, « € » en 2008, « euros »
  ensuite. Les trois sont acceptées.
* **LES PUCES CHANGENT DE SIGNE** : tiret cadratin « ― » dans les années 2010,
  tiret simple précédé d'un guillemet « «- » quand le décret RÉÉCRIT un article
  d'un décret antérieur, rien du tout avant 2010 où les champs se suivent en
  phrases. Le motif ne s'appuie donc pas sur la puce mais sur l'intitulé du
  champ, qui est stable.
* **LA NUMÉROTATION DES SECTIONS N'EST PAS FIABLE** : elle apparaît en 2012 et
  le décret de 2004 n'en a pas. Le découpage se fait sur « Section
  professionnelle des … », qui est constant.

CE QUE LE SCRIPT NE FAIT PAS : il ne devine rien. Une section absente d'un
décret l'est parce que ses paramètres n'ont pas changé cette année-là, ou parce
qu'un autre texte les porte ; le fichier de sortie le laisse absent, à charge de
la fiche de dire ce qu'elle en fait.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tarfile
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RACINE = "https://echanges.dila.gouv.fr/OPENDATA/JORF/"
SORTIE = (Path(__file__).resolve().parents[2] / "data" / "brut"
          / "jorf_cotisations_liberales.json")

#: Les neuf sections, dans l'ordre où les décrets les énumèrent, avec le motif
#: qui les reconnaît dans « Section professionnelle des … ».
SECTIONS = (
    ("cprn", r"notaires"),
    ("cavom", r"officiers minist.riels"),
    ("carmf", r"m.decins"),
    ("carcdsf", r"chirurgiens-dentistes"),
    ("carpimko", r"auxiliaires m.dicaux"),
    ("carpv", r"v.t.rinaires"),
    ("cavec", r"experts?[- ]comptables"),
    ("cipav", r"architectes"),
    ("cavp", r"pharmaciens"),
)

#: Les champs à retenir. L'intitulé est stable d'un décret à l'autre ; la puce,
#: l'unité et la numérotation ne le sont pas.
CHAMP = re.compile(
    r"(cotisation forfaitaire(?: de la (?:classe [A-Z1-9IV]+|section [A-Z] classe \d))?"
    r"|section [A-Z],? classe \d|classe [A-Z1-9IV]+|classe sp.ciale"
    r"|taux de (?:la )?cotisation(?: proportionnelle| de la section [A-Z]"
    r"|(?: proportionnelle)? de (?:la )?(?:premi.re|deuxi.me|1re|2e) tranche)?"
    r"|taux d.appel de la cotisation"
    r"|valeur d.(?:achat|acquisition) du point(?: (?:de la )?section [A-Z])?"
    r"|cotisation de r.f.rence|cotisation proportionnelle"
    r"|seuil|plafond)"
    r"\s*:\s*([\d][\d   ,.]*)\s*(euros|EUR|€|%)",
    re.I,
)

#: Le décret annuel, quel que soit son intitulé. Le mot COMPLÉMENTAIRE est
#: exigé : un décret jumeau fixe chaque année la cotisation forfaitaire du
#: régime de BASE, dans la même forme et avec les mêmes sections, et il n'a
#: rien à faire ici — jusqu'en 2001 il est d'ailleurs libellé en francs.
ANNEE = re.compile(
    r"[Pp]our l.ann.e (\d{4})[, ]+"
    r"(?:le montant annuel des cotisations|les cotisations)"
    r"[^.]{0,200}?vieillesse compl.mentaire"
)

#: Ruptures VÉRIFIÉES À LA MAIN, que le contrôle de continuité doit laisser
#: passer. La CAVEC a RELETTRÉ ses classes : « classe IV : 1 904 € » en 2004,
#: « classe A : 2 262 € » en 2008, puis « classe A : 549 € » en 2012. La lettre
#: A ne désigne plus la même classe de part et d'autre de 2009 — ce n'est pas
#: une cotisation divisée par quatre, c'est une grille renumérotée.
RUPTURES_CONNUES = {("cavec", "classe a")}


def _nombre(brut: str) -> float:
    for espace in (" ", " ", " "):
        brut = brut.replace(espace, "")
    return float(brut.replace(",", "."))


def dernier_dump() -> str:
    with urllib.request.urlopen(RACINE, timeout=120) as reponse:
        page = reponse.read().decode("utf-8", "replace")
    noms = re.findall(r'href="(Freemium_jorf_global_[^"]+\.tar\.gz)"', page)
    if not noms:
        raise LookupError("aucun dump global dans " + RACINE)
    return RACINE + sorted(noms)[-1]


def telecharger(url: str, cible: Path) -> None:
    print(f"Téléchargement de {url}", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=1800) as reponse, \
            cible.open("wb") as sortie:
        while True:
            morceau = reponse.read(1 << 20)
            if not morceau:
                break
            sortie.write(morceau)


def _texte(xml: str) -> str:
    import html
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", xml)))


def decrets(archive: Path) -> dict[int, str]:
    """Année -> corps du décret qui fixe les cotisations de cette année-là."""
    par_annee: dict[int, str] = {}
    with tarfile.open(archive, "r|gz") as flux:      # lecture en STREAM
        for membre in flux:
            if not membre.isfile() or not membre.name.endswith(".xml"):
                continue
            if "/article/" not in membre.name:
                continue
            brut = flux.extractfile(membre).read().decode("utf-8", "replace")
            if "Section professionnelle des" not in brut:
                continue
            texte = _texte(brut)
            trouve = ANNEE.search(texte)
            if not trouve:
                continue
            annee, corps = int(trouve.group(1)), texte[trouve.start():]
            # Un même décret peut être découpé en plusieurs articles : on garde
            # le plus complet, celui qui porte l'énumération entière.
            if annee not in par_annee or len(corps) > len(par_annee[annee]):
                par_annee[annee] = corps
    return par_annee


def depouiller(corps: str) -> dict[str, dict[str, float]]:
    bornes = []
    for cle, motif in SECTIONS:
        for trouve in re.finditer(
            r"Section professionnelle des " + motif, corps, re.I
        ):
            bornes.append((trouve.start(), cle))
    bornes.sort()
    releve: dict[str, dict[str, float]] = {}
    for rang, (debut, cle) in enumerate(bornes):
        fin = bornes[rang + 1][0] if rang + 1 < len(bornes) else len(corps)
        champs = {}
        for trouve in CHAMP.finditer(corps[debut:fin]):
            nom = re.sub(r"\s+", " ", trouve.group(1)).strip().lower()
            unite = trouve.group(3)
            champs[nom] = (_nombre(trouve.group(2)),
                           "%" if unite == "%" else "euros")
        if champs:
            releve[cle] = champs
    return releve


def verifier(releve: dict[int, dict]) -> list[str]:
    """Continuité des séries : une valeur qui double d'une année à l'autre est
    une erreur de lecture, pas une revalorisation.

    Deux valeurs ne sont comparées que si elles portent LA MÊME UNITÉ. Le décret
    change parfois de langue sans changer de règle : le seuil d'assiette de la
    CARCDSF vaut « 32 334 euros » en 2015 et « 85 % du plafond annuel » en 2016,
    ce qui est le même seuil dit autrement.
    """
    anomalies = []
    suites: dict[tuple[str, str], dict[int, tuple[float, str]]] = {}
    for annee, sections in releve.items():
        for cle, champs in sections.items():
            for nom, valeur in champs.items():
                suites.setdefault((cle, nom), {})[annee] = valeur
    for (cle, nom), suite in sorted(suites.items()):
        if (cle, nom) in RUPTURES_CONNUES:
            continue
        annees = sorted(suite)
        for avant, apres in zip(annees, annees[1:]):
            (valeur_avant, unite_avant) = suite[avant]
            (valeur_apres, unite_apres) = suite[apres]
            if apres - avant > 3 or valeur_avant == 0:
                continue
            if unite_avant != unite_apres:
                continue
            rapport = valeur_apres / valeur_avant
            if not 0.5 <= rapport <= 2.0:
                anomalies.append(
                    f"{cle}/{nom} : {avant} {valeur_avant} -> {apres} {valeur_apres}"
                )
    return anomalies


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument(
        "--dump", type=Path,
        help="dump JORF déjà téléchargé, pour ne pas reprendre 1,7 Go",
    )
    arguments = analyseur.parse_args()

    archive = arguments.dump
    temporaire = None
    if archive is None:
        temporaire = SORTIE.parent / "_jorf_global.tar.gz"
        temporaire.parent.mkdir(parents=True, exist_ok=True)
        try:
            telecharger(dernier_dump(), temporaire)
        except (urllib.error.HTTPError, urllib.error.URLError, LookupError) as erreur:
            print(f"ÉCHEC   téléchargement : {erreur}", file=sys.stderr)
            return 1
        archive = temporaire

    par_annee = decrets(archive)
    releve = {annee: depouiller(corps) for annee, corps in par_annee.items()}
    releve = {annee: sections for annee, sections in releve.items() if sections}
    if not releve:
        print("ÉCHEC   aucun décret annuel trouvé", file=sys.stderr)
        return 1

    anomalies = verifier(releve)
    if anomalies:
        print("\nSéries incohérentes, rien n'est écrit :", file=sys.stderr)
        for anomalie in anomalies:
            print(f"  {anomalie}", file=sys.stderr)
        return 1

    plat = {}
    for annee, sections in sorted(releve.items()):
        for cle, champs in sorted(sections.items()):
            for nom, (valeur, unite) in sorted(champs.items()):
                plat[f"{cle}|{annee}|{nom}"] = [valeur, unite]

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": RACINE,
            "recupere_le": date.today().isoformat(),
            "note": "décrets annuels fixant les cotisations des régimes "
                    "complémentaires des sections professionnelles libérales",
            "serie": plat,
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    if temporaire is not None:
        temporaire.unlink(missing_ok=True)

    annees = sorted(releve)
    print(f"{len(plat)} valeurs écrites dans {SORTIE}")
    print(f"Couverture {annees[0]}-{annees[-1]}, {len(annees)} décrets")
    for cle, _ in SECTIONS:
        vus = sorted(a for a in releve if cle in releve[a])
        if vus:
            print(f"  {cle:9s} {vus[0]}-{vus[-1]} ({len(vus)} années)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
