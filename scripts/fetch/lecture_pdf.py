"""Extraction de texte PDF avec mise en page, sans dépendance externe.

Écrit pour les barèmes de la CNBF, seule source des valeurs du point des
avocats. Le dépôt n'a qu'une dépendance, PyYAML, et ce module n'en ajoute
aucune : il n'utilise que ``re`` et ``zlib`` de la bibliothèque standard.

Deux difficultés, toutes deux rencontrées sur les barèmes de la CNBF :

1. **Les colonnes.** L'étiquette et sa valeur ne se suivent pas dans l'ordre du
   flux : elles partagent une ligne à l'écran. On reconstitue donc la mise en
   page à partir des opérateurs de position (``Td``, ``TD``, ``Tm``).

2. **Les polices à encodage propre.** Les nombres qui comptent — valeur de
   service, coût d'acquisition du point — sont écrits avec une police Type0
   « Identity-H », où chaque caractère est un numéro de glyphe et non une
   lettre. Sans la table ``/ToUnicode`` de la police, ils sortent en charabia,
   ou pas du tout. C'est exactement ce qui masquait les valeurs cherchées.
"""
from __future__ import annotations

import re
import zlib

OCTAL = re.compile(r"\\([0-7]{1,3})")


# -- objets et flux ---------------------------------------------------------


def _objets(octets: bytes) -> dict[int, bytes]:
    return {
        int(m.group(1)): m.group(2)
        for m in re.finditer(rb"(\d+)\s+0\s+obj\b(.*?)\bendobj", octets, re.S)
    }


def _flux(objet: bytes) -> bytes | None:
    m = re.search(rb"stream\r?\n(.*?)endstream", objet, re.S)
    if not m:
        return None
    donnees = m.group(1)
    if b"/FlateDecode" in objet:
        try:
            return zlib.decompress(donnees.strip(b"\r\n"))
        except Exception:
            return None
    return donnees


# -- tables ToUnicode -------------------------------------------------------


def _cmap(contenu: bytes) -> dict[int, str]:
    """Lit une table ToUnicode : code de glyphe -> caractère."""
    table: dict[int, str] = {}

    def caracteres(hexa: bytes) -> str:
        brut = bytes.fromhex(hexa.decode("ascii"))
        return brut.decode("utf-16-be", errors="replace")

    for bloc in re.findall(rb"beginbfchar(.*?)endbfchar", contenu, re.S):
        for src, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", bloc):
            table[int(src, 16)] = caracteres(dst)
    for bloc in re.findall(rb"beginbfrange(.*?)endbfrange", contenu, re.S):
        for debut, fin, dst in re.findall(
            rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", bloc
        ):
            premier = int(dst, 16)
            for i, code in enumerate(range(int(debut, 16), int(fin, 16) + 1)):
                table[code] = chr(premier + i)
    return table


def _polices(octets: bytes) -> dict[bytes, dict[int, str]]:
    """Associe chaque nom de police (/F1…) à sa table ToUnicode."""
    objets = _objets(octets)
    tables: dict[bytes, dict[int, str]] = {}
    for objet in objets.values():
        for nom, numero in re.findall(rb"/(\w+)\s+(\d+)\s+0\s+R", objet):
            police = objets.get(int(numero))
            if not police or b"/Font" not in police:
                continue
            m = re.search(rb"/ToUnicode\s+(\d+)\s+0\s+R", police)
            if not m:
                continue
            contenu = _flux(objets.get(int(m.group(1)), b""))
            if contenu:
                tables[nom] = _cmap(contenu)
    return tables


# -- lecture du texte -------------------------------------------------------


def _litteral(brut: bytes) -> str:
    texte = brut.decode("latin-1")
    texte = OCTAL.sub(lambda m: chr(int(m.group(1), 8)), texte)
    return texte.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")


def _hexa(brut: bytes, table: dict[int, str] | None) -> str:
    chiffres = re.sub(rb"[^0-9A-Fa-f]", b"", brut).decode("ascii")
    if len(chiffres) % 4:
        chiffres = chiffres.ljust(len(chiffres) + 4 - len(chiffres) % 4, "0")
    codes = [int(chiffres[i:i + 4], 16) for i in range(0, len(chiffres), 4)]
    if table:
        return "".join(table.get(code, "") for code in codes)
    return "".join(chr(code) if 32 <= code < 0x3000 else "" for code in codes)


#: Les opérateurs de texte utiles. ``TL`` fixe l'interligne, que ``T*``, ``'``
#: et ``"`` appliquent pour passer à la ligne suivante : sans eux, tout un
#: paragraphe reste à la même ordonnée et se retrouve collé sur une seule ligne.
JETONS = re.compile(
    rb"(?P<tm>[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+Tm)"
    rb"|(?P<td>[-\d.]+\s+[-\d.]+\s+T[dD])"
    rb"|(?P<tl>[-\d.]+\s+TL)"
    rb"|(?P<etoile>T\*)"
    rb"|(?P<retour>[)\]]\s*[\'\"])"
    rb"|(?P<tf>/(\w+)\s+[-\d.]+\s+Tf)"
    rb"|(?P<hex><[0-9A-Fa-f\s]+>)"
    rb"|(?P<txt>\((?:[^()\\]|\\.)*\))"
)


def lignes_pdf(octets: bytes, tolerance: float = 3.0) -> list[str]:
    """Reconstitue les lignes visuelles du document, de haut en bas.

    LE NUMÉRO DE FLUX FAIT PARTIE DE LA CLÉ, et c'est tout sauf un détail.
    Chaque page d'un PDF a son propre repère : l'ordonnée 700 y désigne le même
    endroit de la feuille, page 1 comme page 60. Regrouper les fragments sur la
    seule ordonnée, comme le faisait cette fonction, collait donc bout à bout
    la ligne du haut de CHAQUE page du document — un titre de la page 1 suivi
    d'un chiffre de la page 40 et d'une note de la page 97, dans une même
    chaîne. Sur un document d'une page le défaut ne se voit pas. Sur la
    chronologie de la CARMF, cent pages de tableaux, il rendait huit lignes
    pour cent quatre-vingt mille caractères, et l'on en concluait que la mise
    en page « ne se reconstituait pas ». Elle se reconstitue très bien : c'est
    le lecteur qui empilait les pages.
    """
    tables = _polices(octets)
    fragments: list[tuple[int, float, float, str]] = []
    for page, objet in enumerate(_objets(octets).values()):
        contenu = _flux(objet)
        if not contenu or (b"Tj" not in contenu and b"TJ" not in contenu):
            continue
        x = y = 0.0
        # ÉCHELLE DE LA MATRICE DE TEXTE. `Tm` ne pose pas seulement une
        # position, il pose un repère : « 9 0 0 9 82.97 723.62 Tm » place le
        # curseur ET multiplie par neuf tout ce qui suit. Les décalages `Td`
        # qui viennent ensuite sont exprimés dans CE repère, pas en points de
        # la page. Les additionner tels quels, comme le faisait cette
        # fonction, écrasait les interlignes d'un facteur neuf : des lignes
        # distantes de 14,4 points sur la feuille se retrouvaient à 1,6 l'une
        # de l'autre, donc sous la tolérance de regroupement, donc fondues en
        # une seule. C'est ce qui rendait illisibles les tableaux de la
        # chronologie de la CARMF — trente-six lignes ramenées à quatre.
        echelle_x = echelle_y = 1.0
        interligne = 0.0
        police = None
        for jeton in JETONS.finditer(contenu):
            if jeton.group("tm"):
                nombres = jeton.group("tm").split()
                echelle_x, echelle_y = float(nombres[0]), float(nombres[3])
                x, y = float(nombres[4]), float(nombres[5])
            elif jeton.group("td"):
                nombres = jeton.group("td").split()
                x += float(nombres[0]) * echelle_x
                y += float(nombres[1]) * echelle_y
                if jeton.group("td").rstrip().endswith(b"TD"):
                    interligne = -float(nombres[1]) * echelle_y
            elif jeton.group("tl"):
                interligne = float(jeton.group("tl").split()[0]) * echelle_y
            elif jeton.group("etoile") or jeton.group("retour"):
                y -= interligne
            elif jeton.group("tf"):
                police = jeton.group(9)
            else:
                morceau = (_hexa(jeton.group("hex"), tables.get(police))
                           if jeton.group("hex")
                           else _litteral(jeton.group("txt")[1:-1]))
                if morceau.strip():
                    fragments.append((page, y, x, morceau))

    fragments.sort(key=lambda f: (f[0], -f[1], f[2]))
    lignes: list[str] = []
    courante: list[str] = []
    ordonnee = None
    feuille = None
    for page, y, _, morceau in fragments:
        meme_ligne = (ordonnee is not None and page == feuille
                      and abs(y - ordonnee) <= tolerance)
        if meme_ligne or ordonnee is None:
            courante.append(morceau)
        else:
            lignes.append(re.sub(r"\s+", " ", "".join(courante)).strip())
            courante = [morceau]
        ordonnee, feuille = y, page
    if courante:
        lignes.append(re.sub(r"\s+", " ", "".join(courante)).strip())
    return [l for l in lignes if l]


def texte_pdf(octets: bytes) -> str:
    return "\n".join(lignes_pdf(octets))


if __name__ == "__main__":
    import sys
    print(texte_pdf(open(sys.argv[1], "rb").read()))
