#!/usr/bin/env python3
"""Le jaune pensions, lu : les bonifications dénombrées par celui qui les paie.

    python scripts/fetch/sre_jaune_pensions.py                 # lit l'édition 2027, écrit data/brut/sre_jaune_pensions_2027.json
    python scripts/fetch/sre_jaune_pensions.py --edition 2026  # l'édition 2026, data/brut/sre_jaune_pensions.json
    python scripts/fetch/sre_jaune_pensions.py --confronter    # chaque chiffre du jaune cité dans le YAML des avantages est-il dans le document ?
    python scripts/fetch/sre_jaune_pensions.py --fichier ~/Téléchargements/34465.pdf

**DEUX ÉDITIONS SE LISENT.** L'annexe au PLF 2026 (`sre_jaune_pensions` du
manifeste : le stock de 2024, le flux de 2023) et celle au PLF 2027
(`sre_jaune_pensions_2027` : le stock et le flux de 2025), que porte
désormais `bonifications_jaune.csv`. Les tableaux gardent leurs numéros d'une
édition à l'autre, non leur mise en page : celle de 2027 centre ses cellules
dans leur case, coupe le tableau 50 entre deux pages et pose l'insécable des
milliers à part. Le lecteur relit donc ses lignes de gauche à droite
(``par_abscisse``), le tableau 50 se suit sur la page d'après, et
:func:`_recoller` rend aux chiffres leur insécable ; l'édition 2026, elle, se
lit exactement comme avant. Ce que le tableau 50 dit contre lui-même est
signalé, non corrigé (:func:`incoherences_50`).

Le « Rapport sur les pensions de retraite de la fonction publique », annexe
au projet de loi de finances (le jaune budgétaire), est LE SEUL DOCUMENT
PUBLIC QUI DÉNOMBRE LES BONIFICATIONS DE SERVICE : combien de pensions en
portent une, pour combien de trimestres, et ce qu'elles pèsent sur la pension
mensuelle. Trois tableaux servent au dépôt, et ce script les lit :

* **A-7**, en annexe : pour les pensions EN PAIEMENT en fin d'année — un
  stock, 2024 dans l'édition 2026, 2025 dans celle de 2027 —, le
  nombre de bénéficiaires et la durée moyenne, en trimestres, de six
  bonifications, en cinq colonnes (civils de l'État hors La Poste et Orange,
  tous civils de l'État, militaires, FPT, FPH).
* **50**, dans le corps du rapport : sur le FLUX des liquidants — 2023, puis
  2025 —, la
  proportion de bénéficiaires, le gain en trimestres et LE GAIN SUR LE
  MONTANT MENSUEL DE LA PENSION, en euros — la seule valorisation publiée —,
  en huit colonnes (une par bonification, plus l'ensemble) et quatre
  populations.
* **B-1**, en annexe : les caractéristiques du même flux, dont on ne garde
  que les lignes complètes — huit valeurs pour huit colonnes —, parce que le
  tableau laisse des cellules vides que la lecture ligne à ligne ne saurait
  replacer sans deviner.

**LE DOCUMENT NE SE TÉLÉCHARGE PAS DEPUIS UNE SESSION** : ``budget.gouv.fr``
refuse les adresses de sortie du proxy. Mais l'annexe est déposée au
Parlement, et l'Assemblée nationale sert le même fichier, octet pour octet :
c'est le ``miroir`` du manifeste, avec l'empreinte SHA-256 du document. Le
script lit d'abord ``data/brut/12-Jaune2026_Pensions.pdf`` s'il est là, sinon
le miroir, et refuse un fichier dont l'empreinte diffère.

**CE QUE LA LECTURE A COÛTÉ.** Les polices du jaune sont rangées dans des
flux d'objets compressés et ses chaînes sont des codes à un octet : le lecteur
PDF du dépôt en rendait « 5DSSRUW » pour « Rapport » avant d'apprendre les
deux (voir ``lecture_pdf.py``). Il reste un défaut du document lui-même : la
table Unicode d'une de ses polices n'a pas les lettres accentuées, si bien
que « bénéficiaires » s'y lit « bnficiaires » — pdfminer rend la même chose.
Les intitulés sont donc reconnus sans leurs accents ; les nombres, eux, sont
intacts.

**OÙ LES VALEURS VONT.** ``scripts/verifier_donnees.py --appliquer`` lit le
JSON écrit ici et verse les trois tableaux, à plat, dans
``data/reference/legislation/bonifications_jaune.csv``, au niveau
``certifiee`` — clé (tableau, ligne, population, mesure). Les fiches de
``avantages_non_contributifs.yaml`` y renvoient par leur champ
``denombrement``, et un test exige que chaque chiffre qu'elles citent du
jaune soit une valeur de leurs lignes.

**CE QUE ``--confronter`` PROUVE EN PLUS.** Les valeurs du jaune ont d'abord
été saisies à l'écran dans les notes des fiches. ``--confronter`` relit chaque
note qui cite le jaune, en extrait les nombres, et dit pour chacun s'il figure
dans les tableaux lus — sans passer par le CSV ni par le champ, c'est-à-dire
même pour une note qui n'aurait pas encore son ``denombrement``. Un nombre
absent est une faute de saisie ou un chiffre pris ailleurs : dans les deux
cas, à regarder.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_pdf import lignes_par_page  # noqa: E402
from source_locale import (  # noqa: E402
    RACINE, jeux_bloques, lire_ou_telecharger, option_fichier, telecharger,
)

#: Les éditions que le script sait lire : le jeu du manifeste, le fichier
#: écrit, et la façon de relire les lignes. L'édition 2027 centre chaque
#: cellule dans sa case, à des hauteurs qui varient d'un demi-point : ses
#: lignes se relisent de gauche à droite (``par_abscisse`` du lecteur PDF).
EDITIONS = {
    2026: {"identifiant": "sre_jaune_pensions", "sortie": "sre_jaune_pensions.json",
           "par_abscisse": False},
    2027: {"identifiant": "sre_jaune_pensions_2027", "sortie": "sre_jaune_pensions_2027.json",
           "par_abscisse": True},
}
#: L'édition que porte data/reference/legislation/bonifications_jaune.csv.
EDITION = 2027
IDENTIFIANT = EDITIONS[EDITION]["identifiant"]
SORTIE = RACINE / "data" / "brut" / EDITIONS[EDITION]["sortie"]
AVANTAGES = RACINE / "data" / "reference" / "legislation" / "avantages_non_contributifs.yaml"

#: Les colonnes du tableau A-7, dans l'ordre du document.
COLONNES_A7 = ("fpe_civils_hors_poste_orange", "fpe_civils", "fpe_militaires", "fpt", "fph")
#: Les six bonifications du tableau A-7, reconnues sur l'intitulé sans accents.
BONIFICATIONS_A7 = (
    ("depaysement", "hors d'europe"),
    ("enfant", "pour enfant"),
    ("campagne_ou_cinquieme", "campagne"),
    ("service_aerien_sous_marin", "sous-marins"),
    ("enseignement_technique", "enseignement technique"),
    ("hors_l12", "l12"),
)
#: Les colonnes du tableau 50, dans l'ordre du document.
COLONNES_50 = ("depaysement", "enfant", "campagne", "service_aerien_sous_marin",
               "enseignement_technique", "cinquieme_l12", "hors_l12", "ensemble")
POPULATIONS_50 = ("fpe_civils", "fpe_militaires", "fpt", "fph")
#: L'intitulé de chaque population, cherché comme un mot : il ouvre la ligne
#: (« FPE Civils 9,0% … ») ou suit l'intitulé du bloc (« Gain en FPE Civils
#: 19,8 … », « Gain en durée Militaires … »).
MOTS_50 = (("fpe_civils", re.compile(r"\bfpe civils\b")),
           ("fpe_militaires", re.compile(r"\bmilitaires\b")),
           ("fpt", re.compile(r"\bfpt\b")),
           ("fph", re.compile(r"\bfph\b")))
BLOCS_50 = ("proportion", "gain_trimestres", "gain_mensuel_eur")
#: Les colonnes du tableau B-1.
COLONNES_B1 = ("fpe_civils_hors_poste_orange", "fpe_civils", "fpe_militaires", "fpe_total",
               "ouvriers_etat", "fpt", "fph", "cnracl_total")

#: Un nombre du document : milliers séparés d'une espace insécable (le lecteur
#: PDF garde la fine du jaune comme telle) ou, dans une note saisie, d'une
#: espace ordinaire ; décimales à virgule.
NOMBRE = re.compile(r"^-?\d{1,3}(?:[  ]\d{3})*(?:,\d+)?$")
CELLULE = re.compile(r"-?\d{1,3}(?: \d{3})*(?:,\d+)?%?|-?\d+(?:,\d+)?%?")
ABSENT = {"n.d.", "n.d", "n.p.", "n.p", "ns", "nd", "np"}


def sans_accents(texte: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texte)
                   if unicodedata.category(c) != "Mn").lower()


def _valeur(jeton: str) -> float | int | None:
    """« 1 339 945 » → 1339945 ; « 27,4 » → 27.4 ; « 9,0% » → 0.09 ;
    « 266 € » → 266 ; « n.d. » → None. Autre chose : ValueError."""
    propre = jeton.strip()
    if propre.lower() in ABSENT:
        return None
    pourcentage = propre.endswith("%")
    propre = propre.rstrip("%€ ").strip()
    if not NOMBRE.match(propre):
        raise ValueError(f"pas un nombre du tableau : {jeton!r}")
    nombre = float(propre.replace(" ", "").replace(" ", "").replace(",", "."))
    if pourcentage:
        return round(nombre / 100, 6)
    return int(nombre) if nombre == int(nombre) and "," not in propre else nombre


def _recoller(ligne: str) -> str:
    """L'édition 2027 pose l'insécable des milliers à part, si bien que le
    lecteur l'entoure de deux espaces de position : « 1 \u00a0 343 \u00a0 118 ».
    Elle se recolle ici à ses chiffres."""
    return re.sub(r"(?<=\d) ?\u00a0 ?(?=\d)", "\u00a0", ligne)


def _cellules(ligne: str) -> list[str]:
    """Les cellules numériques d'une ligne : un nombre dont les milliers
    tiennent par une insécable, son éventuel « % » collé ou « € » détaché, et
    les marques d'absence. Les cellules, elles, sont séparées d'une espace
    ordinaire — celle que le lecteur pose entre deux positions, après que
    :func:`_recoller` a rendu ses chiffres à l'insécable des milliers."""
    jetons = _recoller(ligne).split(" ")
    cellules: list[str] = []
    i = 0
    while i < len(jetons):
        jeton = jetons[i]
        if jeton.lower() in ABSENT:
            cellules.append(jeton)
        elif CELLULE.fullmatch(jeton):
            nombre = jeton
            # Un pourcentage ou un montant détaché : « 10,4 % », « 266 € ».
            if i + 1 < len(jetons) and jetons[i + 1] in ("%", "€"):
                i += 1
                nombre += " " + jetons[i]
            cellules.append(nombre)
        i += 1
    return cellules


def _page(pages: list[list[str]], critere) -> list[str]:
    for page in pages:
        if any(critere(sans_accents(ligne)) for ligne in page):
            return page
    raise LookupError("le tableau attendu n'est sur aucune page")


def tableau_a7(pages: list[list[str]]) -> dict:
    """Le tableau A-7 : effectif du régime, puis, par bonification, le nombre
    de bénéficiaires et la durée moyenne, en cinq colonnes."""
    page = _page(pages, lambda ligne: ligne.replace(" ", "").startswith("effectiftotaldur"))
    lu: dict = {"effectif": {}, "bonifications": {}}
    courante: list[int | None] | None = None
    for ligne in page:
        plat = sans_accents(ligne)
        cellules = _cellules(ligne)
        if plat.replace(" ", "").startswith("effectiftotaldur"):
            lu["effectif"] = dict(zip(COLONNES_A7, map(_valeur, cellules), strict=True))
        elif plat.startswith("bnficiaires") or plat.startswith("beneficiaires"):
            courante = [_valeur(c) for c in cellules]
        elif plat.startswith("bonifications") and courante is not None:
            code = next((code for code, motif in BONIFICATIONS_A7 if motif in plat), None)
            if code is None:
                raise ValueError(f"bonification inconnue dans A-7 : {ligne!r}")
            lu["bonifications"][code] = {
                "beneficiaires": dict(zip(COLONNES_A7, courante, strict=True))}
        elif (plat.startswith("dure moyenne") or plat.startswith("duree moyenne")) and lu["bonifications"]:
            dernier = list(lu["bonifications"])[-1]
            lu["bonifications"][dernier]["duree_trimestres"] = dict(
                zip(COLONNES_A7, map(_valeur, cellules), strict=True))
            courante = None
    if len(lu["bonifications"]) != len(BONIFICATIONS_A7):
        raise ValueError(f"A-7 : {len(lu['bonifications'])} bonifications lues, "
                         f"{len(BONIFICATIONS_A7)} attendues")
    for code, table in lu["bonifications"].items():
        for colonne in COLONNES_A7:
            n, total = table["beneficiaires"][colonne], lu["effectif"][colonne]
            if n is not None and total is not None and n > total:
                raise ValueError(f"A-7 : {code}, {colonne} : {n} bénéficiaires pour "
                                 f"{total} pensions")
    return lu


def _lignes_du_tableau_50(pages: list[list[str]]) -> list[str]:
    """Les lignes du tableau 50, de son titre à sa ligne « Sources ». L'édition
    2027 le coupe entre deux pages : la lecture passe alors à la suivante,
    jusqu'à cette ligne ou à la fin de la page."""
    for rang, page in enumerate(pages):
        debut = next((k for k, ligne in enumerate(page)
                      if sans_accents(ligne).startswith("tableau 50")), None)
        if debut is None:
            continue
        suite = pages[rang + 1] if rang + 1 < len(pages) else []
        lignes: list[str] = []
        for ligne in page[debut:] + suite:
            if sans_accents(ligne).startswith("sources"):
                break
            lignes.append(ligne)
        return lignes
    raise LookupError("le tableau attendu n'est sur aucune page")


def tableau_50(pages: list[list[str]]) -> dict:
    """Le tableau 50 : trois blocs (proportion, gain en trimestres, gain
    mensuel) × quatre populations × huit colonnes. Les libellés de bloc sont
    entremêlés aux lignes — « Gain en durée Militaires n.p. 6,4 … » — : on
    reconnaît la population, on prend ses huit cellules, et le bloc est le
    rang d'apparition de cette population."""
    vus: dict[str, int] = {p: 0 for p in POPULATIONS_50}
    lu: dict = {bloc: {} for bloc in BLOCS_50}
    for ligne in _lignes_du_tableau_50(pages):
        plat = sans_accents(ligne)
        population = next((code for code, mot in MOTS_50 if mot.search(plat)), None)
        if population is None:
            continue
        cellules = _cellules(ligne)
        if len(cellules) != len(COLONNES_50) or vus[population] == len(BLOCS_50):
            continue
        bloc = BLOCS_50[vus[population]]
        vus[population] += 1
        lu[bloc][population] = dict(zip(COLONNES_50, map(_valeur, cellules), strict=True))
    for bloc in BLOCS_50:
        manque = [p for p in POPULATIONS_50 if p not in lu[bloc]]
        if manque:
            raise ValueError(f"tableau 50, bloc {bloc} : populations absentes {manque}")
    for population, valeurs in lu["proportion"].items():
        individuelles = [v for c, v in valeurs.items() if c != "ensemble" and v is not None]
        if valeurs["ensemble"] is not None and individuelles and valeurs["ensemble"] < max(individuelles):
            raise ValueError(f"tableau 50 : {population}, l'ensemble ({valeurs['ensemble']}) "
                             f"est sous une bonification seule ({max(individuelles)})")
    return lu


def tableau_b1(pages: list[list[str]]) -> dict:
    """Les lignes complètes du tableau B-1 : huit valeurs, huit colonnes."""
    page = _page(pages, lambda ligne: ligne.startswith("ensemble des dparts") or ligne.startswith("ensemble des departs"))
    lu: dict = {}
    for ligne in map(_recoller, page):
        plat = sans_accents(ligne)
        cellules = _cellules(ligne)
        if len(cellules) != len(COLONNES_B1) or plat.startswith(("hommes", "femmes")):
            continue
        libelle = re.sub(r"\s*\(\d+\)\s*", " ", ligne[:ligne.find(cellules[0])]).strip()
        if not libelle:
            continue
        cle = re.sub(r"[^a-z0-9]+", "_", sans_accents(libelle)).strip("_")
        lu[cle] = {"libelle": libelle,
                   "valeurs": dict(zip(COLONNES_B1, map(_valeur, cellules), strict=True))}
    if "ensemble_des_dparts" not in lu and "ensemble_des_departs" not in lu:
        raise ValueError("B-1 : la ligne « Ensemble des départs » n'a pas huit valeurs")
    return lu


def _pourcent(part: float) -> str:
    return f"{part * 100:.1f} %".replace(".", ",")


def incoherences_50(lu: dict) -> list[str]:
    """Ce que le tableau 50 dit contre lui-même : un « ensemble » — la part des
    liquidants qui portent AU MOINS une bonification — plus grand que la somme
    des parts de chacune, au-delà de ce que les arrondis permettent. Le
    document se trompe alors sur une case. Elle reste telle qu'il l'imprime,
    et la lecture le dit : l'édition 2027 donne 4,0 % des civils de l'État
    liquidants à la bonification pour enfant, quand son ensemble, 56,7 %, en
    demande plus de 34, et que son tableau B-22 compte 20 736 bénéficiaires
    sur 47 104 pensions, 44,0 % : un chiffre manque à la case."""
    messages: list[str] = []
    for population, valeurs in lu["proportion"].items():
        parts = [v for c, v in valeurs.items() if c != "ensemble" and v is not None]
        ensemble = valeurs["ensemble"]
        if ensemble is not None and parts and ensemble > sum(parts) + 0.005:
            messages.append(f"tableau 50, {population} : l'ensemble ({_pourcent(ensemble)}) "
                            f"dépasse la somme des parts de chaque bonification "
                            f"({_pourcent(sum(parts))}) ; une case du document est fausse")
    return messages


def lire(octets: bytes, edition: int = EDITION) -> dict:
    pages = lignes_par_page(octets, par_abscisse=EDITIONS[edition]["par_abscisse"])
    return {"A-7": tableau_a7(pages), "50": tableau_50(pages), "B-1": tableau_b1(pages)}


# -- confrontation aux valeurs saisies -----------------------------------------

CHIFFRE_CITE = re.compile(
    r"(?<!\d)(?<!\d,)(\d{1,3}(?: \d{3})+|\d+,\d+|\d+(?= ?€)|\d+(?= ?%))(?!\d|,\d)")


def chiffres_cites(texte: str) -> list[str]:
    """Les nombres d'une note qui cite le jaune : milliers à espaces, décimales
    à virgule, montants en euros, pourcentages. Une année ou un numéro
    d'article n'y ressemble pas."""
    return [m.group(1) for m in CHIFFRE_CITE.finditer(texte)]


def _valeurs_du_document(tables: dict) -> set[str]:
    """Toutes les valeurs lues, sous les formes qu'une note peut citer."""
    formes: set[str] = set()

    def ajouter(v):
        if v is None or isinstance(v, str):
            return
        if isinstance(v, float) and v < 1 and v > 0 and round(v * 100, 4) == round(v * 100, 1):
            formes.add(f"{v * 100:.1f}".replace(".", ","))
        if isinstance(v, float):
            formes.add(f"{v:.1f}".replace(".", ","))
        else:
            formes.add(f"{v:,}".replace(",", " "))
            formes.add(str(v))

    def parcourir(noeud):
        if isinstance(noeud, dict):
            for x in noeud.values():
                parcourir(x)
        else:
            ajouter(noeud)

    parcourir(tables)
    return formes


def confronter(tables: dict, avantages: Path = AVANTAGES) -> tuple[list[str], list[str]]:
    """Rend (trouvés, manquants) : les chiffres cités avec le jaune dans les
    notes du YAML, selon qu'ils figurent ou non dans les tableaux lus."""
    import yaml

    formes = _valeurs_du_document(tables)
    trouves: list[str] = []
    manquants: list[str] = []
    document = yaml.safe_load(avantages.read_text(encoding="utf-8"))
    entrees = document.get("avantages", document) if isinstance(document, dict) else document
    if isinstance(entrees, dict):
        entrees = [v for v in entrees.values() if isinstance(v, dict)]

    def textes(noeud):
        if isinstance(noeud, str):
            yield noeud
        elif isinstance(noeud, dict):
            for x in noeud.values():
                yield from textes(x)
        elif isinstance(noeud, list):
            for x in noeud:
                yield from textes(x)

    for entree in entrees:
        code = entree.get("code", "?") if isinstance(entree, dict) else "?"
        for texte in textes(entree):
            if "jaune" not in texte.lower():
                continue
            for chiffre in chiffres_cites(texte):
                (trouves if chiffre in formes else manquants).append(f"{code} : {chiffre}")
    return trouves, manquants


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    option_fichier(analyseur)
    analyseur.add_argument("--confronter", action="store_true",
                           help="vérifie que chaque chiffre du jaune cité dans "
                                "avantages_non_contributifs.yaml figure dans les tableaux lus")
    analyseur.add_argument("--edition", type=int, choices=sorted(EDITIONS), default=EDITION,
                           help=f"l'édition du jaune, par l'année du PLF (défaut : {EDITION}, "
                                "celle que porte bonifications_jaune.csv)")
    options = analyseur.parse_args(argv)
    edition = EDITIONS[options.edition]
    identifiant = edition["identifiant"]
    sortie = RACINE / "data" / "brut" / edition["sortie"]
    jeu = next((j for j in jeux_bloques() if j["id"] == identifiant), None)
    if jeu is None:
        print(f"{identifiant} absent de data/sources.yaml, ou plus déclaré bloqué", file=sys.stderr)
        return 1
    try:
        octets = lire_ou_telecharger(jeu["url"], telecharger, options.fichier,
                                     nom_local=jeu.get("fichier_local"),
                                     miroir=jeu.get("miroir"), sha256=jeu.get("sha256"))
    except (OSError, ValueError) as erreur:
        print(f"échec de la lecture du document : {erreur}", file=sys.stderr)
        return 1
    try:
        tables = lire(octets, options.edition)
    except (LookupError, ValueError) as erreur:
        print(f"jaune : {erreur} — rien n'est écrit", file=sys.stderr)
        return 1
    incoherences = incoherences_50(tables["50"])

    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps({
        "edition": options.edition,
        "source": jeu["url"],
        "miroir": jeu.get("miroir"),
        "sha256": jeu.get("sha256"),
        "recupere_le": date.today().isoformat(),
        "producteur": f"Direction du budget, annexe au projet de loi de finances pour "
                      f"{options.edition} (données du Service des retraites de l'État, de la "
                      "CNRACL et du FSPOEIE). C'est le producteur de la donnée, non une "
                      "transcription.",
        "incoherences": incoherences,
        "tables": tables,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    a7, b1 = tables["A-7"], tables["B-1"]
    effectif = f"{a7['effectif']['fpe_civils']:,}".replace(",", " ")
    print(f"{sortie.relative_to(RACINE)} : A-7, {len(a7['bonifications'])} bonifications × "
          f"{len(COLONNES_A7)} colonnes sur {effectif} pensions civiles de l'État ; "
          f"tableau 50, {len(BLOCS_50)} blocs × {len(POPULATIONS_50)} populations × "
          f"{len(COLONNES_50)} colonnes ; B-1, {len(b1)} lignes complètes")
    for message in incoherences:
        print(f"  INCOHÉRENT  {message}")

    if options.confronter:
        trouves, manquants = confronter(tables)
        print(f"confrontation : {len(trouves)} chiffres cités retrouvés dans le document, "
              f"{len(manquants)} manquant(s)")
        for ligne in manquants:
            print(f"  MANQUE  {ligne}")
        return 1 if manquants else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
