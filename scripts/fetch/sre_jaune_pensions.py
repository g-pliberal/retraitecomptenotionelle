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

Un quatrième, qui n'est pas une bonification : **les taux de contribution
employeur** depuis 2000 — tableau 14 de l'édition 2027, 12 de celle de 2026,
reconnu à son titre —, l'État, la CNRACL, le FSPOEIE et le droit commun. Le
dépôt en tire la seule série qu'il n'avait pas, celle du FSPOEIE (action 159,
étape 3) ; les autres colonnes recoupent ses séries, et restent au JSON.

**LES RÉFÉRENTS** (action 159, étape 4), de l'édition 2027 seule : le stock
de pensions au 31 décembre 2025 (A-1, droit direct et droit dérivé) et le
flux de 2025, en entier (B-1), par motif de départ (B-3 pour l'État, B-3 bis
pour la CNRACL), par catégorie et par grade (B-4, B-5) — âges, durées,
décote et surcote, taux et indice de liquidation, minimum garanti, pension.
Leurs cases vides ne laissent rien dans le texte d'une ligne : ils se
lisent case par case, chacune à sa place (``lecture_pdf.fragments_par_page``),
la première ligne du tableau plaçant les colonnes, et chaque ligne reconnue
à son intitulé dans l'ordre que son gabarit dit (:class:`Gabarit`). Ce
qu'ils disent les uns des autres se recoupe (:func:`incoherences_referents`).
``scripts/verifier_donnees.py`` les certifie dans
``data/reference/macro/caracteristiques_fonction_publique.csv``.

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
jaune soit une valeur de leurs lignes. La colonne du FSPOEIE va, elle, dans
``data/reference/legislation/contribution_employeur_public.csv``.

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
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_pdf import fragments_par_page, lignes_par_page, texte_de_ligne  # noqa: E402
from source_locale import (  # noqa: E402
    RACINE, jeux_bloques, lire_ou_telecharger, option_fichier, telecharger,
)

#: Les éditions que le script sait lire : le jeu du manifeste, le fichier
#: écrit, et la façon de relire les lignes. L'édition 2027 centre chaque
#: cellule dans sa case, à des hauteurs qui varient d'un demi-point : ses
#: lignes se relisent de gauche à droite (``par_abscisse`` du lecteur PDF).
EDITIONS = {
    2026: {"identifiant": "sre_jaune_pensions", "sortie": "sre_jaune_pensions.json",
           "par_abscisse": False, "referents": False},
    2027: {"identifiant": "sre_jaune_pensions_2027", "sortie": "sre_jaune_pensions_2027.json",
           "par_abscisse": True, "referents": True},
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
#: Les colonnes du tableau des taux de contribution employeur — 14 dans
#: l'édition 2027, 12 dans celle de 2026 —, dans l'ordre du document : les
#: trois taux de l'État (civils, allocation temporaire d'invalidité,
#: militaires), la CNRACL, le FSPOEIE et le droit commun d'un non-cadre (Cnav
#: et Arrco). Avant 2006, l'État n'appelait rien : la ligne n'a que les trois
#: dernières.
COLONNES_EMPLOYEUR = ("fpe_civils", "fpe_ati", "fpe_militaires", "cnracl", "fspoeie",
                      "droit_commun_non_cadre")
#: Le titre du tableau, sans accents : son numéro change d'une édition à l'autre.
TITRE_EMPLOYEUR = "taux de contribution employeur des fonctionnaires et des ouvriers"
LIGNE_ANNEE = re.compile(r"^((?:19|20)\d\d) ")
TAUX = re.compile(r"(\d+,\d+) ?%")

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


def tableau_taux_employeur(pages: list[list[str]]) -> dict:
    """Le tableau des taux de contribution employeur, une ligne par année
    depuis 2000 : six taux, ou les trois derniers avant 2006. Les renvois du
    document — « * », plus haut de 0,10 point en novembre et décembre 2012 ;
    « ** », la moyenne de 2013 de l'État, que sa baisse de décembre abaisse —
    ne sont pas des valeurs : le taux imprimé est lu tel quel."""
    page = _page(pages, lambda ligne: ligne.startswith("tableau") and TITRE_EMPLOYEUR in ligne)
    lu: dict = {}
    for ligne in page:
        annee = LIGNE_ANNEE.match(ligne.strip())
        taux = TAUX.findall(ligne)
        if annee is None or not taux:
            continue
        if len(taux) not in (len(COLONNES_EMPLOYEUR), 3):
            raise ValueError(f"taux employeur, {annee.group(1)} : {len(taux)} taux lus "
                             f"dans {ligne!r}")
        colonnes = COLONNES_EMPLOYEUR[-len(taux):]
        lu[annee.group(1)] = dict(zip(colonnes, (_valeur(t + "%") for t in taux), strict=True))
    if not lu:
        raise ValueError("taux employeur : aucune ligne d'année lue")
    return lu


# -- les référents : le stock et le flux de 2025, case par case ----------------

#: Ce qui sépare deux mots ou deux cases ; l'insécable, elle, tient les
#: milliers d'un nombre.
ESPACES = re.compile(r"[ \t\r\n\f\v]+")
#: Les fragments d'un même mot se suivent à moins de six points : les
#: chiffres posés un à un, à la même abscisse, ou le signe moins, deux points
#: avant les siens. Au-delà, un nouveau mot commence — sauf de part et
#: d'autre d'une insécable, qui tient les milliers d'un nombre quelle que
#: soit la taille de ses chiffres : quatorze points et demi de « 343 » à
#: l'insécable qui le suit, au tableau A-1.
ECART_DANS_UN_MOT = 6.0
INSECABLES = "  "
#: Un renvoi à une note : « (5) », « (10) ».
RENVOI = re.compile(r"^\(\d+\)$")
#: Une case vide de sens : « n.d. », « n.d », « n.p. », « n.s. », renvoi
#: collé ou non, ou le tiret seul d'une case sans objet.
ABSENCE = re.compile(r"^(?:n\.?[dps]\.?(?:\(\d+\))?|-)$", re.IGNORECASE)
#: Un nombre de case : milliers tenus par l'insécable, ou collés (« 1230 »,
#: au tableau B-5), décimales à virgule, signe moins et « % » collés.
NOMBRE_CASE = re.compile(r"^-?(?:\d{1,3}(?: \d{3})+|\d+)(?:,\d+)?%?$")
#: La largeur moyenne d'un caractère des tableaux, en points : de quoi
#: trouver le milieu d'une case centrée. « 39 146 » s'étend sur vingt
#: points, le tiret d'une case sans objet sur deux.
LARGEUR_CARACTERE = 3.5


def _jetons(rangee: list[tuple[float, str]]) -> list[tuple[float, str]]:
    """Les mots d'une ligne de fragments (abscisse, texte), chacun avec
    l'abscisse où il commence.

    Un mot s'arrête à une espace ordinaire, que le document pose au bord de
    chaque case, ou à un saut de plus de :data:`ECART_DANS_UN_MOT` points
    hors d'une insécable. Ainsi les chiffres posés un à un se rejoignent,
    « 39 », l'insécable et « 146 » font « 39 146 », et le signe moins posé
    deux points avant ses chiffres fait un nombre négatif ; le tiret d'une
    case sans objet, que suit l'espace de sa case, reste seul."""
    jetons: list[list] = []
    ouvert = False
    precedente: float | None = None
    for x, morceau in rangee:
        insecable = ouvert and (jetons[-1][1][-1] in INSECABLES or morceau[:1] in INSECABLES)
        if precedente is not None and x - precedente > ECART_DANS_UN_MOT and not insecable:
            ouvert = False
        precedente = x
        for rang, partie in enumerate(ESPACES.split(morceau)):
            if rang:
                ouvert = False
            if not partie:
                continue
            if ouvert:
                jetons[-1][1] += partie
            else:
                jetons.append([x, partie])
                ouvert = True
    return [(x, re.sub(f"[{INSECABLES}]+", " ", texte)) for x, texte in jetons]


def _cases(rangee: list[tuple[float, str]], seuil: float) -> tuple[str, list[tuple[float, str]]]:
    """(intitulé, cases) d'une ligne. Les mots posés avant ``seuil`` font
    l'intitulé ; après lui, les nombres et les marques d'absence sont les
    cases, chacune à l'abscisse de son milieu, le « % » détaché rendu à son
    nombre, les renvois écartés."""
    mots: list[str] = []
    cases: list[tuple[float, str]] = []
    for x, jeton in _jetons(rangee):
        if x < seuil:
            mots.append(jeton)
        elif RENVOI.match(jeton):
            continue
        elif jeton in ("%", "€") and cases and NOMBRE_CASE.match(cases[-1][1]):
            if jeton == "%":
                cases[-1] = (cases[-1][0], cases[-1][1] + "%")
        elif NOMBRE_CASE.match(jeton) or ABSENCE.match(jeton):
            cases.append((x, jeton))
        else:
            mots.append(jeton)
    return " ".join(mots), [(x + LARGEUR_CARACTERE * len(texte) / 2, texte)
                            for x, texte in cases]


def _valeur_case(jeton: str) -> float | int | None:
    """« 23 780 » → 23780 ; « 1230 » → 1230 ; « 64,2 » → 64.2 ; « 41,5% » →
    0.415 ; « -212,2 » → -212.2 ; « n.d. », le tiret seul → None."""
    if ABSENCE.match(jeton):
        return None
    if not NOMBRE_CASE.match(jeton):
        raise ValueError(f"pas une case du tableau : {jeton!r}")
    propre = jeton.rstrip("%").replace(" ", "")
    nombre = float(propre.replace(",", "."))
    if jeton.endswith("%"):
        return round(nombre / 100, 6)
    return nombre if "," in propre else int(nombre)


@dataclass(frozen=True)
class Gabarit:
    """Ce qu'un tableau du jaune porte : ses colonnes, et ses lignes dans
    l'ordre du document.

    Chaque colonne est un couple (population, champ) — le champ est le
    motif de départ, la catégorie ou le grade que la colonne retient, ou
    l'``ensemble``. Chaque ligne est un triplet (champ imposé, indicateur,
    motif) : le motif reconnaît l'intitulé, sans accents, que la ligne porte
    ou que portent les lignes d'intitulé qui l'encadrent ; le champ imposé
    remplace celui de la colonne, pour une ligne qui ne compte qu'un motif
    de départ (« Départs pour invalidité »). ``rang`` dit quelle ligne de
    référence suivre après le titre : la seconde, pour les pensions de
    droit dérivé du tableau A-1."""

    numero: str
    titre: str
    colonnes: tuple[tuple[str, str], ...]
    lignes: tuple[tuple[str | None, str, str], ...]
    rang: int = 0


def _effectifs(champ: str | None, motif: str) -> tuple[tuple[str | None, str, str], ...]:
    """Un effectif de départs, et la part de chaque sexe."""
    return ((champ, "departs", motif), (champ, "part_hommes", r"\bhommes"),
            (champ, "part_femmes", r"\bfemmes"))


#: Ce que les tableaux du flux disent de chaque colonne, dans l'ordre du
#: document : âges, durées, décote et surcote, taux et indice de
#: liquidation, minimum garanti, majoration pour enfants, pension.
CARACTERISTIQUES_DU_FLUX = tuple((None, indicateur, motif) for indicateur, motif in (
    ("age_radiation", r"radiation des cadres"),
    ("age_premiere_mise_en_paiement", r"premi\w* mise en paiement"),
    ("part_remuneres_avant_liquidation", r"encore r\w*mun"),
    ("services_trimestres", r"services acquis"),
    ("bonifications_trimestres", r"bonifications acquises"),
    ("duree_tous_regimes_trimestres", r"assurance tous r"),
    ("part_decote", r"pensions avec d\w*cote"),
    ("perte_decote_eur", r"perte mensuelle"),
    ("taux_decote", r"taux moyen de d\w*cote"),
    ("cout_decote_meur", r"induit par la d\w*cote"),
    ("part_surcote", r"pensions avec surcote"),
    ("gain_surcote_eur", r"n\w*fice mensuel"),
    ("taux_surcote", r"taux moyen de surcote"),
    ("cout_surcote_meur", r"induit par la surcote"),
    ("taux_liquidation", r"taux moyen de liquidation(?! hors)"),
    ("taux_liquidation_hors_decote_surcote", r"liquidation hors"),
    ("part_taux_plein", r"taux plein"),
    ("part_taux_80", r"taux de 80"),
    ("indice_liquidation", r"indice moyen"),
    ("part_minimum_garanti", r"au minimum garanti"),
    ("majoration_enfants_eur", r"suppl\w*ment apport|majoration de pension pour enfants \(en euros"),
    ("part_majoration_enfants", r"cette majoration"),
    ("pension_principale_eur", r"avantage principal(?! et)"),
    ("pension_avec_accessoires_eur", r"avantage principal et accessoires"),
))

#: Les sept colonnes du stock (tableau A-1).
POPULATIONS_A1 = ("fpe_civils_hors_poste_orange", "fpe_civils", "fpe_militaires",
                  "ouvriers_etat", "fpt", "fph", "cnracl_total")
MOTIFS_DE_DEPART = ("anciennete", "motifs_familiaux", "invalidite")
PENSION_DU_STOCK = ((None, "pension_principale_eur", r"avantage principal(?! et)"),
                    (None, "pension_avec_accessoires_eur", r"avantage principal et accessoires"))

#: Les tableaux référents de l'édition 2027 : le stock au 31 décembre 2025
#: (A-1), le flux de 2025 en entier (B-1), par motif de départ (B-3 pour
#: l'État, B-3 bis pour la CNRACL), par catégorie et par grade (B-4 pour
#: l'État, B-5 pour la CNRACL).
GABARITS = (
    Gabarit("A-1", "tableau n°a - 1", tuple((p, "droit_direct") for p in POPULATIONS_A1), (
        (None, "effectif", r"^effectif\b"),
        (None, "effectif_hommes", r"\bhommes"),
        (None, "effectif_femmes", r"\bfemmes"),
        (None, "age_moyen", r"age moyen(?! de)"),
        (None, "age_premiere_mise_en_paiement", r"premi\w* mise en paiement"),
        (None, "services_trimestres", r"services acquis"),
        (None, "taux_liquidation", r"taux moyen de liquidation"),
        (None, "indice_liquidation", r"indice moyen"),
        *PENSION_DU_STOCK)),
    Gabarit("A-1", "tableau n°a - 1", tuple((p, "droit_derive") for p in POPULATIONS_A1), (
        (None, "effectif", r"^effectif\b"),
        (None, "effectif_hommes", r"\bhommes"),
        (None, "effectif_femmes", r"\bfemmes"),
        (None, "effectif_orphelins", r"orphelins"),
        (None, "age_moyen", r"age moyen(?! de)"),
        (None, "age_premiere_mise_en_paiement", r"premi\w* mise en paiement"),
        *PENSION_DU_STOCK), rang=1),
    Gabarit("B-1", "tableau n°b - 1", tuple((p, "ensemble") for p in COLONNES_B1), (
        *_effectifs(None, r"ensemble des d"),
        *_effectifs("invalidite", r"pour invalidit"),
        *_effectifs("carriere_longue", r"carri\w*re longue"),
        *_effectifs("motifs_familiaux", r"motifs familiaux"),
        *_effectifs("categorie_active", r"cat\w*gorie active"),
        *CARACTERISTIQUES_DU_FLUX)),
    Gabarit("B-3", "tableau n°b - 3", tuple(
        (p, m) for p in ("fpe_civils_hors_poste_orange", "fpe_civils", "fpe_militaires")
        for m in MOTIFS_DE_DEPART), (
        *_effectifs(None, r"ensemble des d"),
        *_effectifs("categorie_active", r"cat\w*gorie active"),
        *CARACTERISTIQUES_DU_FLUX)),
    Gabarit("B-3bis", "tableau n°b - 3bis", tuple(
        (p, m) for p in ("fpt", "fph", "cnracl_total") for m in MOTIFS_DE_DEPART), (
        *_effectifs(None, r"ensemble des d"),
        *_effectifs("categorie_active", r"cat\w*gorie active"),
        *CARACTERISTIQUES_DU_FLUX)),
    Gabarit("B-4", "tableau n°b - 4", (
        *((p, c) for p in ("fpe_civils_hors_poste_orange", "fpe_civils")
          for c in ("sedentaire", "active_57", "active_52", "carriere_longue")),
        ("militaires_terre_mer_air", "non_officiers"), ("militaires_terre_mer_air", "officiers"),
        ("militaires_gendarmerie", "non_officiers"), ("militaires_gendarmerie", "officiers")), (
        *_effectifs(None, r"ensemble des d"),
        *CARACTERISTIQUES_DU_FLUX)),
    Gabarit("B-5", "tableau n°b - 5", tuple(
        (p, c) for p in ("fpt", "fph", "cnracl_total")
        for c in ("sedentaire", "active", "carriere_longue")), (
        *_effectifs(None, r"ensemble des d"),
        *CARACTERISTIQUES_DU_FLUX)),
)


def _apres_le_titre(positionnees: list[list[list[tuple[float, str]]]], titre: str
                    ) -> list[list[tuple[float, str]]]:
    """Les lignes qui suivent le titre d'un tableau, page après page. Le
    titre se reconnaît à la ligne entière : « Tableau n°B - 3 » n'est pas
    « Tableau n°B - 3bis »."""
    for rang_page, page in enumerate(positionnees):
        for rang, rangee in enumerate(page):
            if sans_accents(texte_de_ligne(rangee)) == titre:
                return page[rang + 1:] + [r for suite in positionnees[rang_page + 1:]
                                          for r in suite]
    raise LookupError(f"le titre « {titre} » n'est sur aucune page")


def tableau_referent(positionnees: list[list[list[tuple[float, str]]]], gabarit: Gabarit) -> dict:
    """Un tableau référent, rangé {population: {champ: {indicateur: valeur}}}.

    LA LIGNE DE RÉFÉRENCE PLACE LES COLONNES. C'est la première du tableau
    (« Ensemble des départs », « Effectif ») : elle a une case par colonne,
    et le milieu de chacune. Une case de toute autre ligne va à la colonne
    dont le milieu est le plus proche — une case vide ne laissant rien dans
    le texte d'une ligne, c'est sa place qui dit sa colonne. Puis chaque
    ligne de cases prend, dans l'ordre, l'indicateur que le gabarit attend,
    pourvu que son intitulé, ou celui des lignes d'intitulé qui l'encadrent,
    le reconnaisse : le jaune pose certains intitulés au-dessus de leurs
    cases, d'autres en dessous. La lecture s'arrête à la ligne « Source » ;
    elle passe d'une page à la suivante, dont elle saute le numéro.
    """
    lignes = _apres_le_titre(positionnees, gabarit.titre)
    nombre = len(gabarit.colonnes)
    premier = gabarit.lignes[0][2]
    vues = 0
    for debut, rangee in enumerate(lignes):
        mots, cases = _cases(rangee, float("-inf"))
        if len(cases) == nombre and re.search(premier, sans_accents(mots)):
            if vues == gabarit.rang:
                break
            vues += 1
    else:
        raise LookupError(f"{gabarit.numero} : aucune ligne « {premier} » à {nombre} cases")
    milieux = [x for x, _ in cases]
    pas = min(b - a for a, b in zip(milieux, milieux[1:]))
    if pas <= 0:
        raise ValueError(f"{gabarit.numero} : colonnes dans le désordre {milieux}")
    seuil = min(x for x, _ in _jetons(lignes[debut]) if x > milieux[0] - pas) - 0.2 * pas

    zone: list[tuple[str, list[tuple[float, str]]]] = []
    for rangee in lignes[debut:]:
        texte = sans_accents(texte_de_ligne(rangee))
        if texte.startswith("source"):
            break
        if re.fullmatch(r"\d{1,3}", texte):
            continue
        zone.append(_cases(rangee, seuil))

    lu: dict = {}
    attendues = iter(gabarit.lignes)
    attendue = next(attendues)
    for k, (mots, cases) in enumerate(zone):
        if not cases:
            continue
        if attendue is None:
            break
        champ_impose, indicateur, motif = attendue
        avant = zone[k - 1][0] if k > 0 and not zone[k - 1][1] else ""
        apres = zone[k + 1][0] if k + 1 < len(zone) and not zone[k + 1][1] else ""
        contexte = " ".join(filter(None, (avant, mots, apres)))
        if not re.search(motif, sans_accents(contexte)):
            raise ValueError(f"{gabarit.numero} : « {contexte} » là où « {indicateur} » "
                             f"était attendu")
        rangs: dict[int, float | int | None] = {}
        for x, jeton in cases:
            colonne = min(range(nombre), key=lambda j: abs(milieux[j] - x))
            if abs(milieux[colonne] - x) > pas / 2 or colonne in rangs:
                raise ValueError(f"{gabarit.numero}, {indicateur} : la case « {jeton} » "
                                 f"n'a pas de colonne à elle")
            rangs[colonne] = _valeur_case(jeton)
        for colonne, valeur in rangs.items():
            population, champ = gabarit.colonnes[colonne]
            indicateurs = lu.setdefault(population, {}).setdefault(champ_impose or champ, {})
            if indicateur in indicateurs:
                # Une ligne au champ imposé ne prend qu'une case par
                # population : « Départ avec bénéfice d'une catégorie
                # active » n'en a qu'aux départs pour ancienneté.
                raise ValueError(f"{gabarit.numero}, {population}, {champ_impose} : deux cases "
                                 f"pour « {indicateur} »")
            indicateurs[indicateur] = valeur
        attendue = next(attendues, None)
    if attendue is not None:
        raise ValueError(f"{gabarit.numero} : la ligne « {attendue[1]} » manque")
    return lu


def referents(positionnees: list[list[list[tuple[float, str]]]]) -> dict:
    """Les tableaux référents, par numéro : les deux blocs du tableau A-1
    se rangent sous le même numéro, l'un en ``droit_direct``, l'autre en
    ``droit_derive``."""
    lu: dict = {}
    for gabarit in GABARITS:
        for population, champs in tableau_referent(positionnees, gabarit).items():
            lu.setdefault(gabarit.numero, {}).setdefault(population, {}).update(champs)
    return lu


def incoherences_referents(lu: dict) -> list[str]:
    """Ce que les tableaux référents disent contre eux-mêmes, ou contre leurs
    voisins : une colonne lue de travers, une ligne prise pour une autre, s'y
    verraient. Les hommes et les femmes font l'effectif, ou cent pour cent ;
    le total de l'État, ses civils et ses militaires ; celui de la CNRACL, la
    territoriale et l'hospitalière ; les motifs de départ du tableau B-3,
    l'ensemble des départs du B-1 ; les catégories des civils partis pour
    ancienneté au B-4, leur colonne du B-3."""
    messages: list[str] = []

    def valeur(tableau, population, champ, indicateur):
        return lu.get(tableau, {}).get(population, {}).get(champ, {}).get(indicateur)

    for tableau, populations in lu.items():
        for population, champs in populations.items():
            for champ, indicateurs in champs.items():
                hommes, femmes = indicateurs.get("part_hommes"), indicateurs.get("part_femmes")
                if hommes is not None and femmes is not None and abs(hommes + femmes - 1) > 0.0015:
                    messages.append(f"{tableau}, {population}, {champ} : {_pourcent(hommes)} "
                                    f"d'hommes et {_pourcent(femmes)} de femmes")
                effectif = indicateurs.get("effectif")
                parts = [indicateurs.get(c) for c in ("effectif_hommes", "effectif_femmes",
                                                      "effectif_orphelins")]
                if effectif is not None and parts[0] is not None and sum(
                        p or 0 for p in parts) != effectif:
                    messages.append(f"{tableau}, {population}, {champ} : les sexes ne font pas "
                                    f"l'effectif ({effectif})")
    sommes = [(("B-1", "fpe_total", "ensemble"),
               [("B-1", "fpe_civils", "ensemble"), ("B-1", "fpe_militaires", "ensemble")]),
              (("B-1", "cnracl_total", "ensemble"),
               [("B-1", "fpt", "ensemble"), ("B-1", "fph", "ensemble")]),
              (("B-1", "fpe_civils", "ensemble"),
               [("B-3", "fpe_civils", m) for m in MOTIFS_DE_DEPART]),
              (("B-1", "fpe_militaires", "ensemble"),
               [("B-3", "fpe_militaires", m) for m in MOTIFS_DE_DEPART]),
              (("B-1", "cnracl_total", "ensemble"),
               [("B-3bis", "cnracl_total", m) for m in MOTIFS_DE_DEPART]),
              (("B-3", "fpe_civils", "anciennete"),
               [("B-4", "fpe_civils", c)
                for c in ("sedentaire", "active_57", "active_52", "carriere_longue")])]
    for total, termes in sommes:
        attendu = valeur(*total, "departs")
        trouves = [valeur(*terme, "departs") for terme in termes]
        if attendu is None or None in trouves:
            messages.append(f"{total[0]}, {total[1]} : un effectif de départs manque")
        elif sum(trouves) != attendu:
            messages.append(f"{total[0]}, {total[1]}, {total[2]} : {attendu} départs, "
                            f"{sum(trouves)} dans ses parts du tableau {termes[0][0]}")
    return messages


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
    """Les tableaux de l'édition. Celle de 2027 se lit une fois, en lignes de
    fragments : leur texte sert aux trois tableaux des bonifications et aux
    taux employeurs, leur place aux tableaux référents."""
    if EDITIONS[edition]["par_abscisse"]:
        positionnees = fragments_par_page(octets)
        pages = [[texte_de_ligne(rangee) for rangee in page] for page in positionnees]
    else:
        positionnees, pages = [], lignes_par_page(octets)
    tables = {"A-7": tableau_a7(pages), "50": tableau_50(pages), "B-1": tableau_b1(pages),
              "taux_employeur": tableau_taux_employeur(pages)}
    if EDITIONS[edition]["referents"]:
        tables["referents"] = referents(positionnees)
    return tables


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

    # Les taux employeurs et les référents ne sont pas des bonifications :
    # aucune note ne les cite, et un chiffre mal saisi ne doit pas s'y
    # retrouver par hasard.
    formes = _valeurs_du_document({k: v for k, v in tables.items()
                                   if k not in ("taux_employeur", "referents")})
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
    if "referents" in tables:
        incoherences += incoherences_referents(tables["referents"])

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
    a7, b1, employeur = tables["A-7"], tables["B-1"], tables["taux_employeur"]
    effectif = f"{a7['effectif']['fpe_civils']:,}".replace(",", " ")
    print(f"{sortie.relative_to(RACINE)} : A-7, {len(a7['bonifications'])} bonifications × "
          f"{len(COLONNES_A7)} colonnes sur {effectif} pensions civiles de l'État ; "
          f"tableau 50, {len(BLOCS_50)} blocs × {len(POPULATIONS_50)} populations × "
          f"{len(COLONNES_50)} colonnes ; B-1, {len(b1)} lignes complètes ; taux employeurs, "
          f"{min(employeur)}-{max(employeur)}")
    for numero, populations in tables.get("referents", {}).items():
        cases = [v for champs in populations.values() for indicateurs in champs.values()
                 for v in indicateurs.values()]
        print(f"  référent {numero} : {sum(v is not None for v in cases)} valeurs, "
              f"{sum(v is None for v in cases)} cases sans objet")
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
