"""Les fichiers fabriqués, écrits sans ligne géante.

Le paquet du site et le bilan figé s'écrivaient en JSON compact, d'une seule
ligne, de quatre millions de caractères pour le paquet ; le témoin des pages
gardait le HTML de chacune en une chaîne, sur une ligne qui allait jusqu'à
767 000 caractères. Un ``grep`` ou un ``sed`` lancé par Bash en rendait la
ligne entière, et le diff d'un témoin la page entière quand un seul chiffre
avait bougé (feuille de route, action 135, étape 4 du contexte).

Les deux écrivains de ce module coupent aux bornes de la structure, et
seulement ce qui dépasse :data:`LARGEUR` : un objet JSON ou un élément de page
plus long passe à la ligne entre ses éléments, et ainsi de suite en
descendant ; ce qui tient reste sur sa ligne, une année du bilan comme une
ligne de tableau. Les coupes ne dépendent que du contenu : un chiffre qui
change ne déplace que sa ligne. Une chaîne JSON, une balise et un texte ne se
coupent pas : ce sont les seules lignes qui dépassent encore.
"""

from __future__ import annotations

import json
import re

#: Au-delà, un objet ou un tableau JSON, une ligne de page ou l'un de ses
#: éléments passe à la ligne entre ses éléments. Chaque année du bilan y
#: tient, et neuf lignes de tableau du site sur dix (7 octobre 2026).
LARGEUR = 300


# -- le JSON -------------------------------------------------------------------


def _compact(valeur) -> str:
    return json.dumps(valeur, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


def _cle(cle) -> str:
    """La clé telle que ``json.dumps`` l'écrit : un entier y devient une chaîne."""
    return _compact({cle: None})[1:-len(":null}")]


def json_en_lignes(valeur, largeur: int = LARGEUR) -> str:
    """Le JSON compact de ``valeur``, clés triées, où un objet ou un tableau
    de plus de ``largeur`` caractères passe à la ligne entre ses éléments,
    sans indentation.

    Ôter ses retours à la ligne redonne, à l'octet, ce qu'écrit
    ``json.dumps(valeur, ensure_ascii=False, sort_keys=True,
    separators=(",", ":"))`` : le fichier ne grossit que d'un octet par
    ligne, et se relit à l'identique.
    """
    texte = _compact(valeur)
    if len(texte) <= largeur:
        return texte
    if isinstance(valeur, dict):
        # L'ordre de ``sort_keys`` : celui des clés avant leur conversion en
        # chaînes, qui range 2 avant 10.
        elements = [_cle(cle) + ":" + json_en_lignes(element, largeur)
                    for cle, element in sorted(valeur.items(),
                                               key=lambda paire: paire[0])]
        return "{\n" + ",\n".join(elements) + "\n}"
    if isinstance(valeur, (list, tuple)):
        elements = [json_en_lignes(element, largeur) for element in valeur]
        return "[\n" + ",\n".join(elements) + "\n]"
    return texte


# -- le HTML -------------------------------------------------------------------

#: Une balise ou un commentaire. Le site échappe « < » et « > » partout
#: ailleurs (``echapper``, ``moteur/js/format.js``) : une balise finit au
#: premier « > ». Une page qui y manquerait serait coupée moins bien, jamais
#: altérée : les morceaux se recousent quelles que soient les coupes.
_BALISE = re.compile(r"<!--.*?-->|<(/?)([A-Za-z][^\s/>]*)[^>]*>", re.DOTALL)
#: Les éléments sans balise de fin.
_VIDES = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                    "link", "meta", "source", "track", "wbr"})


def html_en_morceaux(html: str, largeur: int = LARGEUR) -> list[str]:
    """Le HTML en morceaux, dont la concaténation le redonne à l'octet.

    Un morceau par ligne, sa fin de ligne comprise. Une ligne de plus de
    ``largeur`` caractères se coupe entre ses éléments, et un élément trop
    long entre ses enfants, sa balise ouvrante et sa balise fermante à part ;
    une balise, un commentaire ou un texte ne se coupent pas. Un morceau ne
    passe donc à la ligne qu'à sa fin.
    """
    morceaux: list[str] = []
    lignes = html.split("\n")
    for rang, ligne in enumerate(lignes):
        fin = "\n" if rang < len(lignes) - 1 else ""
        if len(ligne) > largeur:
            coupes = _couper(ligne, largeur)
            coupes[-1] += fin
            morceaux.extend(coupes)
        elif ligne or fin:
            morceaux.append(ligne + fin)
    return morceaux


def _couper(ligne: str, largeur: int) -> list[str]:
    """Une ligne trop longue, coupée entre ses éléments."""
    # Les jetons : début, fin, nom de l'élément, et +1 pour une balise qui
    # l'ouvre, -1 pour une balise qui le ferme, 0 pour tout le reste — texte,
    # commentaire, élément sans fin.
    jetons: list[tuple[int, int, str, int]] = []
    position = 0
    for balise in _BALISE.finditer(ligne):
        if balise.start() > position:
            jetons.append((position, balise.start(), "", 0))
        nom = (balise.group(2) or "").lower()
        if balise.group(1):
            sens = -1
        elif not nom or nom in _VIDES or balise.group(0).endswith("/>"):
            sens = 0
        else:
            sens = 1
        jetons.append((balise.start(), balise.end(), nom, sens))
        position = balise.end()
    if position < len(ligne):
        jetons.append((position, len(ligne), "", 0))

    # La balise fermante de chaque élément ouvert, si elle est sur la ligne :
    # une ligne ferme parfois ce qu'une autre a ouvert, et inversement.
    fermante: dict[int, int] = {}
    ouverts: list[tuple[str, int]] = []
    for rang, (_, _, nom, sens) in enumerate(jetons):
        if sens > 0:
            ouverts.append((nom, rang))
        elif sens < 0:
            for profondeur in range(len(ouverts) - 1, -1, -1):
                if ouverts[profondeur][0] == nom:
                    fermante[ouverts[profondeur][1]] = rang
                    del ouverts[profondeur:]
                    break

    morceaux: list[str] = []

    def emettre(premier: int, dernier: int) -> None:
        rang = premier
        while rang < dernier:
            fin = fermante.get(rang, rang)
            debut, bout = jetons[rang][0], jetons[fin][1]
            if fin == rang or bout - debut <= largeur:
                morceaux.append(ligne[debut:bout])
            else:
                morceaux.append(ligne[debut:jetons[rang][1]])
                emettre(rang + 1, fin)
                morceaux.append(ligne[jetons[fin][0]:bout])
            rang = fin + 1

    emettre(0, len(jetons))
    return _blancs_au_suivant(morceaux)


def _blancs_au_suivant(morceaux: list[str]) -> list[str]:
    """Un morceau fait de blancs rejoint le suivant, ou le dernier s'il finit
    la ligne : l'indentation reste devant ce qu'elle indente."""
    colles: list[str] = []
    attente = ""
    for morceau in morceaux:
        if morceau.isspace():
            attente += morceau
        else:
            colles.append(attente + morceau)
            attente = ""
    if attente:
        if colles:
            colles[-1] += attente
        else:
            colles.append(attente)
    return colles
