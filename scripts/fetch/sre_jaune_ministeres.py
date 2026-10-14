"""La figure 3B du jaune pensions du PLF 2027 : les crédits de dix-sept
ministères, décomposés selon leur nature, lus sur les tracés de leurs barres.

    (lu par scripts/fetch/sre_jaune_pensions.py, qui l'écrit dans
    data/brut/sre_jaune_pensions_2027.json, table « 3B »)

**LA FIGURE N'IMPRIME AUCUNE VALEUR.** Elle empile, page 24, cinq parts des
crédits que le PLF 2027 ouvre à chaque ministère : la contribution employeur
au CAS « Pensions » sur ses dépenses de personnel (T2 CAS), celle que les
opérateurs de l'Enseignement supérieur versent sur leurs crédits de
fonctionnement (T3 CAS, pour ce ministère seul), les cotisations salariales,
le reste des dépenses de personnel et le reste des dépenses. Ses barres sont
des rectangles peints (``lecture_pdf.aplats_de_page``) : leurs longueurs,
rapportées à l'axe, sont les parts.

**L'ÉCHELLE SE LIT SUR L'AXE**, non sur les barres : le trait de 0 % et ses
dix graduations, de dix points chacune. Le producteur pose ses points sur une
grille de 0,12 point, un six-centième de pouce, soit 2 100 pas sur l'axe :
chaque part se lit à un vingtième de point près (:data:`TOLERANCE`), et une
part plus petite n'a que l'épaisseur d'un pas.

**CE QUE LE TEXTE IMPRIME S'Y RETROUVE** (:data:`CHIFFRES_DU_TEXTE`) : les
parts de l'Éducation nationale et de l'Intérieur que disent la synthèse, les
figures B et B bis et la lecture de la figure, en points et en milliards ; la
Justice au bas de « entre 18 et 28 % » ; les deux derniers ministères sous
1 %. Ce qui ne s'y retrouve pas est signalé (:func:`incoherences_3b`), et
déclaré, s'il tient au document (:data:`INCOHERENCES_3B`).
"""

from __future__ import annotations

import re
import statistics
from collections import Counter

#: La page de la figure, dans l'arbre des pages du document, dont l'empreinte
#: est au manifeste.
PAGE = 24

#: Les dix-sept ministères, de haut en bas, avec leur libellé tel que la
#: figure l'imprime : deux sont coupés d'une ellipse. La Santé et les
#: Transports, qui ne versent pas de contribution, n'y sont pas.
MINISTERES: tuple[tuple[str, str], ...] = (
    ("education_nationale", "Éducation nationale"),
    ("interieur", "Intérieur"),
    ("enseignement_superieur", "Enseignement supérieur, recherche et espace"),
    ("justice", "Justice"),
    ("action_comptes_publics", "Action et comptes publics"),
    ("armees", "Armées et anciens combattants"),
    ("transition_ecologique", "Transition écologique, biodiversité et négociations…"),
    ("agriculture", "Agriculture, agro-alimentaire et souveraineté alimentaire"),
    ("culture", "Culture"),
    ("services_premier_ministre", "Services du Premier ministre"),
    ("europe_affaires_etrangeres", "Europe et affaires étrangères"),
    ("sports", "Sports, jeunesse et vie associative"),
    ("outre_mer", "Outre-Mer"),
    ("travail_solidarites", "Travail et solidarités"),
    ("economie_finances", "Économie, finances et souveraineté industrielle, énergétique…"),
    ("amenagement_territoire", "Aménagement du territoire et de la décentralisation"),
    ("ville_logement", "Ville et logement"),
)

#: Les cinq parts, dans l'ordre de la légende, qui est celui où elles
#: s'empilent depuis l'axe, avec la peinture des barres : trois motifs
#: hachurés de la page, puis deux aplats, bleu et gris. La légende peint ses
#: cases des mêmes couleurs, et de motifs qui portent d'autres noms.
PARTS: tuple[tuple[str, tuple], ...] = (
    ("t2_cas", ("motif", "P631")),
    ("t3_cas", ("motif", "P633")),
    ("cotisations_salariales", ("motif", "P635")),
    ("reste_personnel", ("rgb", 0.184, 0.333, 0.592)),
    ("reste_depenses", ("rgb", 0.816, 0.808, 0.808)),
)
#: Le début de chaque ligne de la légende, dans le même ordre.
LEGENDE = ("T2 CAS", "T3 CAS", "Cotisations salariales", "Reste des dépenses de personnel",
           "Reste des dépenses")

#: Un vingtième de point : un peu plus que le pas de la grille du tracé, un
#: deux-mille-centième de l'axe.
TOLERANCE = 0.0005

#: Ce que le texte du jaune imprime des parts que la figure trace : la page,
#: le ministère, les parts dont il parle, celles qu'il prend pour dénominateur
#: (``None`` : tous les crédits ; sinon la masse salariale), et ce qu'il
#: imprime — un pourcentage à l'unité, deux montants en milliards au dixième,
#: ou une borne. La figure doit tomber dans son arrondi, à :data:`TOLERANCE`
#: près.
PERSONNEL = ("t2_cas", "cotisations_salariales", "reste_personnel")
CHIFFRES_DU_TEXTE: tuple[tuple, ...] = (
    (7, "education_nationale", ("t2_cas", "cotisations_salariales"), None, "32 %"),
    (7, "interieur", ("t2_cas", "cotisations_salariales"), None, "30 %"),
    (10, "education_nationale", ("t2_cas", "cotisations_salariales"), None, "28,5 / 89,1"),
    (11, "education_nationale", ("t2_cas",), None, "25,1 / 89,1"),
    (11, "education_nationale", ("t2_cas",), None, "28 %"),
    (11, "education_nationale", ("cotisations_salariales",), None, "3,4 / 89,1"),
    (11, "education_nationale", ("cotisations_salariales",), None, "4 %"),
    (11, "education_nationale", PERSONNEL, None, "84,6 / 89,1"),
    (11, "education_nationale", ("t2_cas", "cotisations_salariales"), PERSONNEL, "34 %"),
    (12, "interieur", ("t2_cas",), None, "9,3 / 34,2"),
    (12, "interieur", ("t2_cas",), None, "27 %"),
    (12, "interieur", ("cotisations_salariales",), None, "1,1 / 34,2"),
    (12, "interieur", ("cotisations_salariales",), None, "3 %"),
    (12, "interieur", PERSONNEL, None, "25,1 / 34,2"),
    (12, "interieur", ("t2_cas", "cotisations_salariales"), PERSONNEL, "41 %"),
    (24, "education_nationale", ("reste_personnel",), None, "63 %"),
    (24, "education_nationale", ("reste_depenses",), None, "5 %"),
    (24, "amenagement_territoire", ("t2_cas",), None, "< 1 %"),
    (24, "ville_logement", ("t2_cas",), None, "< 1 %"),
    (25, "justice", ("t2_cas",), None, "18 %"),
    (25, "justice", ("t2_cas", "cotisations_salariales"), None, "20 %"),
    (25, "education_nationale", ("t2_cas", "cotisations_salariales"), None, "32 %"),
)


#: Ce que la figure dit contre elle-même ou contre le texte : un motif des
#: messages de :func:`incoherences_3b`, et l'explication. Les parts restent
#: telles que la figure les trace ; une incohérence qui n'est pas ici est une
#: lecture de travers.
INCOHERENCES_3B: tuple[tuple[str, str], ...] = (
    (r"^3B, enseignement_superieur : la barre fait ",
     "À la figure 3B, la barre de l'Enseignement supérieur fait 119,1 % de l'axe : son "
     "reste des dépenses, 98,4 %, compte aussi les 19,1 points de son T3 CAS, versés sur "
     "des crédits de fonctionnement ; le cadre du graphique la rogne à 100 %."),
    (r"^3B, justice, t2_cas\+cotisations_salariales : ",
     "Page 25, « entre 20 % et 32 % si l'on y ajoute les cotisations salariales » : la "
     "borne basse ajoute les parts arrondies de la Justice, 18 et 2 %, quand la figure "
     "en trace 20,9."),
)


def _pourcent(part: float) -> str:
    return f"{part * 100:.1f} %".replace(".", ",")


def _lettres(texte: str) -> str:
    """Les seules lettres sans accent d'un libellé, en minuscules : la police
    de la figure n'a pas toutes les lettres accentuées, et le lecteur rend
    « ducation nationale » pour « Éducation nationale »."""
    return re.sub(r"[^a-z]", "", texte.lower())


def _nombre(texte: str) -> float:
    return float(texte.strip().replace(",", "."))


def intervalle(imprime: str) -> tuple[float, float]:
    """Ce qu'un chiffre du texte laisse à la part, en fraction : « 32 % »,
    de 31,5 à 32,5 points ; « 25,1 / 89,1 », des milliards au dixième, de
    25,05 / 89,15 à 25,15 / 89,05 ; « < 1 % », de 0 à 1 point."""
    if imprime.startswith("<"):
        return 0.0, _nombre(imprime.strip("<% ")) / 100
    if "/" in imprime:
        part, total = (_nombre(x) for x in imprime.split("/"))
        return (part - 0.05) / (total + 0.05), (part + 0.05) / (total - 0.05)
    valeur = _nombre(imprime.rstrip("% "))
    return (valeur - 0.5) / 100, (valeur + 0.5) / 100


def _libelles(lignes: list[str]) -> tuple[list[str], list[str]]:
    """Les libellés des barres, de haut en bas — les lignes entre le titre du
    graphique et les graduations de son axe —, et les lignes de la légende,
    qui suivent les graduations."""
    debut = next((i for i, ligne in enumerate(lignes) if ligne.endswith("(PLF 2027)")), None)
    fin = next((i for i, ligne in enumerate(lignes)
                if debut is not None and i > debut and ligne.startswith("0% ")
                and ligne.endswith(" 100%")), None)
    if debut is None or fin is None:
        raise LookupError("figure 3B : ni son titre ni son axe ne sont sur la page")
    return lignes[debut + 1:fin], lignes[fin + 1:fin + 1 + len(LEGENDE)]


def _echelle(aplats: list) -> tuple[float, float, tuple[float, float]]:
    """L'abscisse de 0 %, la longueur de l'axe, en points, et la hauteur du
    graphique : le trait de l'axe et ses dix graduations sont onze traits
    verticaux de même hauteur, également espacés. Le dernier est posé un
    vingtième de point trop à gauche : le pas se prend sur leur médiane."""
    verticaux = [a for a in aplats if a.trait and a.x0 == a.x1 and a.y1 - a.y0 > 50]
    hauteurs = Counter((round(a.y0, 2), round(a.y1, 2)) for a in verticaux)
    if not hauteurs:
        raise LookupError("figure 3B : aucune graduation sur la page")
    hauteur = hauteurs.most_common(1)[0][0]
    xs = sorted(a.x0 for a in verticaux if (round(a.y0, 2), round(a.y1, 2)) == hauteur)
    if len(xs) != 11:
        raise LookupError(f"figure 3B : {len(xs)} traits verticaux, pour l'axe et ses "
                          "dix graduations")
    pas = statistics.median(b - a for a, b in zip(xs, xs[1:]))
    for rang, x in enumerate(xs):
        if abs(x - (xs[0] + rang * pas)) > TOLERANCE * 10 * pas:
            raise LookupError(f"figure 3B : la graduation de {10 * rang} % n'est pas à sa place")
    return xs[0], 10 * pas, hauteur


def _barres(aplats: list, origine: float, longueur: float,
            hauteur: tuple[float, float]) -> list[dict[str, tuple[float, float]]]:
    """Les barres, de haut en bas : pour chacune, les bornes des parts qu'elle
    trace, en fraction de l'axe. Une case de la légende, hors du graphique,
    n'en est pas."""
    peintures = {peinture: code for code, peinture in PARTS}
    bas, haut = hauteur
    rangees: dict[float, dict[str, tuple[float, float]]] = {}
    for aplat in aplats:
        if aplat.trait or aplat.peinture not in peintures or aplat.y0 < bas or aplat.y1 > haut:
            continue
        code = peintures[aplat.peinture]
        barre = rangees.setdefault(round(aplat.y0, 1), {})
        if code in barre:
            raise LookupError(f"figure 3B : deux {code} sur la barre d'ordonnée {aplat.y0:.1f}")
        barre[code] = ((aplat.x0 - origine) / longueur, (aplat.x1 - origine) / longueur)
    return [rangees[y] for y in sorted(rangees, reverse=True)]


def _empilement(code: str, barre: dict[str, tuple[float, float]]) -> None:
    """Les parts d'une barre partent de l'axe et s'y suivent dans l'ordre de
    la légende, chacune où finit la précédente, à un pas du tracé près : c'est
    ce qui attache chaque peinture à sa part."""
    fin = 0.0
    for part, _ in PARTS:
        if part not in barre:
            continue
        debut, suivante = barre[part]
        if abs(debut - fin) > TOLERANCE:
            raise LookupError(f"figure 3B, {code} : {part} commence à {_pourcent(debut)}, "
                              f"et non où finit la part d'avant ({_pourcent(fin)})")
        fin = suivante


def figure_3b(aplats: list, lignes: list[str]) -> dict:
    """La figure lue : pour chaque ministère, la part de ses crédits que
    trace chacune de ses parts, en fraction de l'axe, et l'échelle, en points
    de la feuille. ``aplats`` sont les rectangles de la page, ``lignes`` son
    texte, ligne à ligne."""
    libelles, legende = _libelles(lignes)
    if len(libelles) != len(MINISTERES):
        raise LookupError(f"figure 3B : {len(libelles)} libellés, pour "
                          f"{len(MINISTERES)} ministères")
    for (_, attendu), lu in zip(MINISTERES, libelles):
        if _lettres(lu) != _lettres(attendu):
            raise LookupError(f"figure 3B : « {lu} » à la place de « {attendu} »")
    for attendu, lu in zip(LEGENDE, legende):
        if not _lettres(lu).startswith(_lettres(attendu)):
            raise LookupError(f"figure 3B : la légende dit « {lu} » à la place de « {attendu} »")
    origine, longueur, hauteur = _echelle(aplats)
    barres = _barres(aplats, origine, longueur, hauteur)
    if len(barres) != len(MINISTERES):
        raise LookupError(f"figure 3B : {len(barres)} barres, pour {len(MINISTERES)} ministères")
    ministeres = {}
    for (code, _), barre in zip(MINISTERES, barres):
        _empilement(code, barre)
        ministeres[code] = {part: round(barre[part][1] - barre[part][0], 6)
                            for part, _ in PARTS if part in barre}
    return {"page": PAGE, "origine": round(origine, 4), "longueur": round(longueur, 4),
            "ministeres": ministeres}


def incoherences_3b(figure: dict) -> list[str]:
    """Ce que la figure dit contre elle-même — une barre qui ne fait pas
    l'axe — ou contre le texte du document."""
    messages: list[str] = []
    ministeres = figure["ministeres"]
    for code, parts in ministeres.items():
        total = sum(parts.values())
        if abs(total - 1) > TOLERANCE:
            messages.append(f"3B, {code} : la barre fait {_pourcent(total)} de l'axe")
    for page, code, parts, sur, imprime in CHIFFRES_DU_TEXTE:
        lues = ministeres[code]
        valeur = sum(lues.get(p, 0.0) for p in parts)
        if sur is not None:
            valeur /= sum(lues.get(p, 0.0) for p in sur)
        bas, haut = intervalle(imprime)
        if not bas - TOLERANCE <= valeur <= haut + TOLERANCE:
            base = "" if sur is None else " de la masse salariale"
            messages.append(f"3B, {code}, {'+'.join(parts)} : {_pourcent(valeur)}{base} à la "
                            f"figure, « {imprime} » au texte, page {page}")
    return messages
