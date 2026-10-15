"""Le lecteur PDF de la fabrique : celui du site, que node fait tourner.

Le dépôt n'a plus qu'un lecteur de PDF, ``moteur/js/lecture-pdf.js`` (action
161, étape 4 ; note de décision 0003 : ce qui tourne aux deux endroits s'écrit
une fois, en JavaScript). Le site le charge pour lire le relevé qu'un lecteur
dépose ; la fabrique le fait tourner par node, par ``lecture_pdf.mjs``, à
travers ce module, qui garde le chemin et les fonctions que ses scripts
importent — ``lecture_pdf`` depuis ``scripts/fetch/``, ``fetch.lecture_pdf``
depuis ``scripts/`` — et, au-dessus du lecteur, ce que seule la fabrique
utilise et qui reste donc en Python : la lecture par abscisse
(:func:`fragments_par_page`, ``lignes_par_page(par_abscisse=True)``,
:func:`texte_de_ligne`) et les rectangles peints d'une page
(:func:`aplats_de_page`). L'histoire du lecteur — les barèmes de la CNBF, le
jaune budgétaire, le relevé d'info-retraite — est dans l'en-tête du
JavaScript, qui l'a reprise du cœur Python qu'il a remplacé.

Ce module n'a pas d'autre dépendance que la bibliothèque standard, et node ;
sans node, il s'arrête net, sans repli : il n'y a plus de second lecteur pour
en tenir lieu.
"""
from __future__ import annotations

import functools
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple

#: Le lecteur du site, que la fabrique fait tourner par node.
LECTEUR = Path(__file__).resolve().with_name("lecture_pdf.mjs")


@functools.lru_cache(maxsize=8)
def _demander(octets: bytes, question: str, argument: float = 3.0):
    """Ce que le lecteur du site répond d'un document (``lecture_pdf.mjs``).

    Un script relit souvent le même document — ses lignes, puis ses lignes par
    page — : les dernières réponses se gardent. Sans node, la lecture s'arrête
    net, sans repli : il n'y a plus de second lecteur pour en tenir lieu."""
    if shutil.which("node") is None:
        raise RuntimeError("node est absent : le lecteur PDF du dépôt, "
                           "moteur/js/lecture-pdf.js, ne tourne pas sans lui")
    fini = subprocess.run(["node", str(LECTEUR), question, str(argument)], input=octets,
                          capture_output=True, check=False, timeout=600)
    if fini.returncode:
        raise RuntimeError("le lecteur PDF a échoué : "
                           + fini.stderr.decode("utf-8", errors="replace")[-2000:])
    reponse = json.loads(fini.stdout)
    if "erreur" in reponse:
        raise (LookupError if reponse["erreur"] == "LookupError" else RuntimeError)(
            reponse["message"])
    return reponse["rendu"]


# -- la lecture par abscisse ----------------------------------------------------


def _normaliser(texte: str) -> str:
    """Une espace pour toute suite d'espaces ordinaires ; UNE ESPACE INSÉCABLE
    pour toute suite d'insécables (U+00A0, U+202F), et elle reste insécable.
    Le jaune budgétaire sépare ses milliers d'une fine insécable et ses
    cellules d'une espace de position : « 1 339 945 1 654 863 » ne se
    découpe en deux nombres que si les deux espaces restent différentes."""
    texte = re.sub(r"[  ]+", " ", texte)
    return re.sub(r"[ \t\r\n\f\v]+", " ", texte).strip()


def lignes_pdf(octets: bytes, tolerance: float = 3.0) -> list[str]:
    """Les lignes visuelles du document, de haut en bas, telles que le lecteur
    du site les assemble (``lignesPdf``) : ses commentaires disent pourquoi le
    numéro de flux entre dans la clé de regroupement."""
    return list(_demander(octets, "lignes", tolerance))


def _assembler_par_abscisse(fragments: list[tuple[int, int, float, float, str]],
                            tolerance: float) -> list[str]:
    """Les mêmes lignes que celles du lecteur du site, chacune relue de gauche
    à droite.

    LE TRI DE HAUT EN BAS DÉSORDONNE UNE LIGNE DONT LES CELLULES NE SONT PAS
    TOUT À FAIT À LA MÊME HAUTEUR. Le jaune pensions du PLF 2027 centre
    chaque cellule de ses tableaux dans sa case : une ordonnée de 700,5 pour
    l'une, de 700 pour sa voisine, et le tri, qui range l'ordonnée avant
    l'abscisse, rendait la ligne des civils de son tableau 50 dans le
    désordre — « 0,9% 0,4% 8,7% 4,0% … FPE Civils 0,0% » pour « FPE Civils
    8,7% 4,0% 0,9% 0,4% … ». Les fragments d'une ligne se regroupent ici
    comme dans le lecteur du site, puis se relisent par abscisse croissante.
    """
    return [texte for _, texte in _lignes_par_abscisse(fragments, tolerance)]


def _lignes_par_abscisse(fragments: list[tuple[int, int, float, float, str]],
                         tolerance: float) -> list[tuple[list[tuple[float, str]], str]]:
    """Chaque ligne de :func:`_assembler_par_abscisse`, avec ses fragments
    (abscisse, texte) rangés de gauche à droite. Une ligne sans texte n'en
    est pas une : elle ne se rend pas, de sorte que les deux lectures
    gardent les mêmes rangs."""
    lignes: list[list[tuple[float, str]]] = []
    courante: list[tuple[float, str]] = []
    ordonnee = None
    feuille = None
    for page, bande, y, x, morceau in fragments:
        meme_ligne = (ordonnee is not None and (page, bande) == feuille
                      and abs(y - ordonnee) <= tolerance)
        if not meme_ligne and courante:
            lignes.append(courante)
            courante = []
        courante.append((x, morceau))
        ordonnee, feuille = y, (page, bande)
    if courante:
        lignes.append(courante)
    rendu: list[tuple[list[tuple[float, str]], str]] = []
    for ligne in lignes:
        rangee = sorted(ligne, key=lambda f: f[0])
        texte = texte_de_ligne(rangee)
        if texte:
            rendu.append((rangee, texte))
    return rendu


def texte_de_ligne(rangee: list[tuple[float, str]]) -> str:
    """Le texte d'une ligne de fragments (abscisse, texte) rangés de gauche à
    droite : deux fragments posés à des abscisses différentes sont séparés
    d'une espace, ceux d'un même tableau ``TJ`` restent collés."""
    morceaux: list[str] = []
    abscisse = None
    for x, morceau in rangee:
        if abscisse is not None and abs(x - abscisse) > 0.01:
            morceaux.append(" ")
        morceaux.append(morceau)
        abscisse = x
    return _normaliser("".join(morceaux))


def _fragments_des_pages(octets: bytes) -> list[list[tuple[int, int, float, float, str]]]:
    """Les fragments du document, page par page, de haut en bas, tels que le
    lecteur du site les pose (``fragmentsParPage``)."""
    return [[(int(p), int(b), float(y), float(x), texte) for p, b, y, x, texte in page]
            for page in _demander(octets, "fragments")]


def fragments_par_page(octets: bytes, tolerance: float = 3.0
                       ) -> list[list[list[tuple[float, str]]]]:
    """Les lignes de :func:`lignes_par_page` relues de gauche à droite
    (``par_abscisse``), chacune gardée en fragments : (abscisse, texte).

    UNE CELLULE VIDE NE LAISSE RIEN DANS LE TEXTE D'UNE LIGNE. Le tableau
    B-1 du jaune pensions du PLF 2027 n'a pas de total de l'État sur la
    plupart de ses lignes, ni de militaires sur celles de la surcote : lue
    en texte, sa ligne de la surcote a six nombres pour huit colonnes, et
    rien ne dit lesquelles manquent. L'abscisse le dit, chaque cellule étant
    posée dans sa colonne. Les rangs des pages et des lignes sont ceux de
    :func:`lignes_par_page`, dont le texte se refait en joignant les
    fragments d'une espace là où l'abscisse change.
    """
    return [[rangee for rangee, _ in _lignes_par_abscisse(page, tolerance)]
            for page in _fragments_des_pages(octets)]


def lignes_par_page(octets: bytes, tolerance: float = 3.0,
                    par_abscisse: bool = False) -> list[list[str]]:
    """Les mêmes lignes que :func:`lignes_pdf`, mais groupées par page.

    Écrit pour les rapports à la CCSS, dont le numéro de fiche est une TÊTE DE
    PAGE : il vaut pour la page qui le porte, et pour elle seule. Savoir où une
    page commence et finit est donc ce qui permet de rattacher un tableau à sa
    fiche — et le rapport de 2025 montre pourquoi on ne peut pas s'en passer :
    ses pages sortent du flux dans l'ordre INVERSE des fiches, 4.15 puis 4.14
    puis 4.13, si bien que le marqueur le plus proche au-dessus d'un tableau
    est celui de la fiche VOISINE, jamais la sienne.

    On ne refait pas l'extraction : le découpage se lit dans les mêmes
    fragments, dont le premier champ est déjà le numéro de page.

    ``par_abscisse`` relit chaque ligne de gauche à droite
    (:func:`_assembler_par_abscisse`) ; sans lui, rien ne change pour les
    lecteurs écrits avant.
    """
    if par_abscisse:
        return [_assembler_par_abscisse(page, tolerance) for page in _fragments_des_pages(octets)]
    return [list(page) for page in _demander(octets, "pages", tolerance)]


def texte_pdf(octets: bytes) -> str:
    return "\n".join(lignes_pdf(octets))


# -- tracés -----------------------------------------------------------------


#: Une matrice de la norme, « a b c d e f » : le point (x, y) qu'elle
#: transforme devient (a x + c y + e, b x + d y + f). Les tracés composent leur
#: repère comme le texte le fait dans le lecteur du site (``composer``) : ces
#: lignes en sont le seul double, pour les seuls rectangles peints.
Matrice = tuple[float, float, float, float, float, float]
IDENTITE: Matrice = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def _composer(m: Matrice, n: Matrice) -> Matrice:
    """La matrice qui applique ``m``, puis ``n`` : la norme écrit m × n."""
    a, b, c, d, e, f = m
    a2, b2, c2, d2, e2, f2 = n
    return (a * a2 + b * c2, a * b2 + b * d2,
            c * a2 + d * c2, c * b2 + d * d2,
            e * a2 + f * c2 + e2, e * b2 + f * d2 + f2)


class Aplat(NamedTuple):
    """Un rectangle peint, en points de la feuille, ``x0 <= x1`` et
    ``y0 <= y1`` : une barre, une case de légende, ou — ``trait`` — un filet
    tracé, une graduation, d'épaisseur nulle dans un sens. ``peinture`` est
    une couleur, ``("rgb", r, v, b)`` ou ``("cmjn", c, m, j, n)``, ou un motif
    de la page, ``("motif", "P631")``."""

    peinture: tuple
    x0: float
    y0: float
    x1: float
    y1: float
    trait: bool = False


#: Les jetons d'un flux, lus pour ses tracés. Une chaîne, un dictionnaire en
#: ligne et un crochet ne tracent rien, mais une chaîne peut contenir « re »
#: ou « f » : ils se lisent d'un bloc pour ne pas être pris pour des
#: opérateurs. Une chaîne garde ses parenthèses équilibrées sur un niveau.
JETONS_TRACE = re.compile(
    rb"(?P<chaine>\((?:[^()\\]|\\.|\((?:[^()\\]|\\.)*\))*\))"
    rb"|(?P<dict><<.*?>>)"
    rb"|(?P<hex><[0-9A-Fa-f\s]*>)"
    rb"|(?P<nom>/[^\s/\[\]()<>{}%]*)"
    rb"|(?P<nombre>[-+]?(?:\d+\.?\d*|\.\d+))"
    rb"|(?P<operateur>[A-Za-z'\"][A-Za-z0-9*'\"]*)"
    rb"|(?P<commentaire>%[^\r\n]*)",
    re.S,
)
REMPLIR = frozenset({b"f", b"F", b"f*"})
TRACER = frozenset({b"S", b"s"})
LES_DEUX = frozenset({b"B", b"B*", b"b", b"b*"})


def _couleur(operandes: list, espace: str | None) -> tuple:
    """La peinture que posent ``sc`` et ``scn`` : un motif s'il est nommé,
    sinon une couleur, selon le nombre de ses composantes."""
    if operandes and isinstance(operandes[-1], str):
        return ("motif", operandes[-1])
    nombres = [x for x in operandes if isinstance(x, float)]
    if len(nombres) == 1:
        return ("rgb", nombres[0], nombres[0], nombres[0])
    if len(nombres) == 3:
        return ("rgb", *nombres)
    if len(nombres) == 4:
        return ("cmjn", *nombres)
    return ("couleur", espace, *nombres)


def _boite(points: list[tuple[float, float]]) -> tuple[float, float, float, float] | None:
    """Les bornes d'un sous-chemin qui est un rectangle droit — quatre coins,
    ou deux points d'un même filet —, ``None`` pour toute autre figure."""
    xs = sorted({round(x, 6) for x, _ in points})
    ys = sorted({round(y, 6) for _, y in points})
    if len(xs) > 2 or len(ys) > 2:
        return None
    coins = {(round(x, 6), round(y, 6)) for x, y in points}
    if len(points) >= 4:
        if coins != {(x, y) for x in xs for y in ys}:
            return None
    elif len(points) < 2 or (len(xs) == 2 and len(ys) == 2):
        return None
    return xs[0], ys[0], xs[-1], ys[-1]


def _aplats(contenu: bytes) -> list[Aplat]:
    """Les rectangles qu'un flux de contenu remplit ou trace.

    La matrice courante (``cm``, que ``q`` et ``Q`` sauvent et rendent) porte
    chaque point sur la feuille, comme pour le texte ; une courbe n'est pas un
    rectangle, et une découpe (``W n``) ne peint rien : la barre qu'elle rogne
    garde sa longueur entière. Un formulaire (``Do``) ne se déplie pas, ni une
    image en ligne, que l'on saute.
    """
    matrice = IDENTITE
    remplissage: tuple = ("rgb", 0.0, 0.0, 0.0)
    trait: tuple = ("rgb", 0.0, 0.0, 0.0)
    espaces: dict[str, str | None] = {"remplissage": None, "trait": None}
    sauves: list[tuple] = []
    chemins: list[list[tuple[float, float]]] = []
    courbes: set[int] = set()
    operandes: list = []
    aplats: list[Aplat] = []

    def point(x: float, y: float) -> tuple[float, float]:
        a, b, c, d, e, f = matrice
        return a * x + c * y + e, b * x + d * y + f

    def peindre(peinture: tuple, en_trait: bool) -> None:
        for rang, chemin in enumerate(chemins):
            boite = None if rang in courbes else _boite(chemin)
            if boite:
                aplats.append(Aplat(peinture, *boite, trait=en_trait))

    position = 0
    while (jeton := JETONS_TRACE.search(contenu, position)):
        position = jeton.end()
        if jeton.group("nombre"):
            operandes.append(float(jeton.group("nombre")))
            continue
        if jeton.group("nom"):
            operandes.append(jeton.group("nom")[1:].decode("latin-1"))
            continue
        operateur = jeton.group("operateur")
        if not operateur:
            if not jeton.group("commentaire"):
                operandes.append(None)
            continue
        nombres = [x for x in operandes if isinstance(x, float)]
        if operateur == b"q":
            sauves.append((matrice, remplissage, trait, dict(espaces)))
        elif operateur == b"Q":
            if sauves:
                matrice, remplissage, trait, espaces = sauves.pop()
        elif operateur == b"cm" and len(nombres) == 6:
            matrice = _composer(tuple(nombres), matrice)
        elif operateur == b"m" and len(nombres) == 2:
            chemins.append([point(*nombres)])
        elif operateur == b"l" and len(nombres) == 2 and chemins:
            chemins[-1].append(point(*nombres))
        elif operateur in (b"c", b"v", b"y") and len(nombres) >= 4 and chemins:
            chemins[-1].append(point(*nombres[-2:]))
            courbes.add(len(chemins) - 1)
        elif operateur == b"re" and len(nombres) == 4:
            x, y, largeur, hauteur = nombres
            chemins.append([point(x, y), point(x + largeur, y),
                            point(x + largeur, y + hauteur), point(x, y + hauteur)])
        elif operateur in REMPLIR or operateur in TRACER or operateur in LES_DEUX \
                or operateur == b"n":
            if operateur in REMPLIR or operateur in LES_DEUX:
                peindre(remplissage, False)
            if operateur in TRACER or operateur in LES_DEUX:
                peindre(trait, True)
            chemins, courbes = [], set()
        elif operateur == b"rg" and len(nombres) == 3:
            remplissage = ("rgb", *nombres)
        elif operateur == b"RG" and len(nombres) == 3:
            trait = ("rgb", *nombres)
        elif operateur == b"g" and len(nombres) == 1:
            remplissage = ("rgb", *nombres * 3)
        elif operateur == b"G" and len(nombres) == 1:
            trait = ("rgb", *nombres * 3)
        elif operateur == b"k" and len(nombres) == 4:
            remplissage = ("cmjn", *nombres)
        elif operateur == b"K" and len(nombres) == 4:
            trait = ("cmjn", *nombres)
        elif operateur == b"cs" and operandes and isinstance(operandes[-1], str):
            espaces["remplissage"] = operandes[-1]
        elif operateur == b"CS" and operandes and isinstance(operandes[-1], str):
            espaces["trait"] = operandes[-1]
        elif operateur in (b"sc", b"scn"):
            remplissage = _couleur(operandes, espaces["remplissage"])
        elif operateur in (b"SC", b"SCN"):
            trait = _couleur(operandes, espaces["trait"])
        elif operateur == b"ID":
            # Les octets d'une image en ligne vont jusqu'à « EI » : ils ne
            # se lisent pas comme des jetons.
            fin = re.compile(rb"\sEI(?=\s|$)").search(contenu, position)
            position = fin.end() if fin else len(contenu)
        operandes = []
    return aplats


def aplats_de_page(octets: bytes, page: int) -> list[Aplat]:
    """Les rectangles peints de la page ``page`` du document, comptée à
    partir de 1 dans l'ordre de son arbre des pages, que le lecteur du site
    retrouve (``contenuDeLaPage``)."""
    return _aplats(_demander(octets, "page", page).encode("latin-1"))


if __name__ == "__main__":
    import sys
    print(texte_pdf(open(sys.argv[1], "rb").read()))
