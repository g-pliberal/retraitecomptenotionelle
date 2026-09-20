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

Et deux autres, rencontrées sur le jaune budgétaire des pensions (PLF 2026),
qui rendaient tout le document en lettres décalées — « 5DSSRUW » pour
« Rapport » :

3. **Les flux d'objets.** Un PDF 1.5 et plus range ses dictionnaires — pages,
   polices, ressources — dans des flux ``/ObjStm`` compressés, où ``N 0 obj``
   n'apparaît plus. Un lecteur qui ne les déplie pas ne voit aucune police,
   donc aucune table, et lit tout en latin-1.

4. **Les chaînes littérales à encodage propre.** Une police TrueType
   sous-ensemble numérote ses glyphes dans l'ordre d'apparition — ``\001``
   pour le premier caractère écrit, ``\002`` pour le deuxième — et les pose
   en chaînes ``(…)`` à un octet par code, non en hexadécimal. La table
   ``/ToUnicode`` vaut pour elles aussi, avec la largeur de code que son
   ``codespacerange`` déclare : un octet ici, deux pour une police Type0.
"""
from __future__ import annotations

import re
import zlib

OCTAL = re.compile(r"\\([0-7]{1,3})")
#: Les échappements d'une chaîne littérale : octal, les cinq lettres de la
#: norme (\n \r \t \b \f), la barre devant une parenthèse ou une barre, et la
#: barre en fin de ligne, qui ne vaut rien. Traités en une passe, de gauche à
#: droite, comme le fait un lecteur : deux passes rendaient « \\101 » en « A ».
ECHAPPEMENT = re.compile(r"\\(?:([0-7]{1,3})|\r\n|\r|\n|(.))", re.S)
LETTRES = {"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f"}


# -- objets et flux ---------------------------------------------------------


def _objets(octets: bytes) -> dict[int, bytes]:
    """Tous les objets du fichier, ceux des flux d'objets compris.

    Un flux ``/ObjStm`` porte ``/N`` objets ; ses données commencent par
    ``N`` paires « numéro décalage », puis, à ``/First`` octets du début, les
    objets eux-mêmes, sans ``obj``/``endobj``. On les range sous leur numéro,
    comme les autres. Le flux lui-même reste dans le dictionnaire : il ne
    porte ni texte ni police, il ne gêne pas.
    """
    objets = {
        int(m.group(1)): m.group(2)
        for m in re.finditer(rb"(\d+)\s+0\s+obj\b(.*?)\bendobj", octets, re.S)
    }
    for objet in list(objets.values()):
        if b"/ObjStm" not in objet:
            continue
        contenu = _flux(objet)
        nombre = re.search(rb"/N\s+(\d+)", objet)
        premier = re.search(rb"/First\s+(\d+)", objet)
        if not contenu or not nombre or not premier:
            continue
        debut = int(premier.group(1))
        tete = contenu[:debut].split()
        paires = [(int(tete[i]), int(tete[i + 1]))
                  for i in range(0, min(2 * int(nombre.group(1)), len(tete) - 1), 2)]
        for rang, (numero, decalage) in enumerate(paires):
            fin = paires[rang + 1][1] if rang + 1 < len(paires) else len(contenu) - debut
            objets.setdefault(numero, contenu[debut + decalage:debut + fin])
    return objets


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


class Table(dict):
    """Une table ToUnicode, avec la largeur en octets de ses codes.

    ``codespacerange`` la déclare : ``<00> <FF>`` pour une police simple, un
    octet ; ``<0000> <FFFF>`` pour une police Type0, deux. Sans déclaration,
    deux — c'est ce que le lecteur a toujours supposé pour l'hexadécimal.
    """

    largeur = 2


def _cmap(contenu: bytes) -> Table:
    """Lit une table ToUnicode : code de glyphe -> caractère."""
    table = Table()
    largeurs = {
        len(src) // 2
        for bloc in re.findall(rb"begincodespacerange(.*?)endcodespacerange", contenu, re.S)
        for src, _ in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", bloc)
    }
    if largeurs:
        table.largeur = max(largeurs)

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
                # Une destination hors du plan Unicode — les rapports à la CCSS
                # en portent, dans des plages que rien n'utilise — ne doit pas
                # faire tomber la lecture de tout le document.
                if premier + i > 0x10FFFF:
                    break
                table[code] = chr(premier + i)
    return table


def _dictionnaire(objet: bytes, cle: bytes, objets: dict[int, bytes]) -> bytes:
    """Le dictionnaire que ``cle`` (``/Resources``, ``/Font``) désigne dans
    ``objet`` : écrit sur place entre ``<<`` et ``>>``, imbrications
    comprises, ou par référence à un autre objet. Vide si absent."""
    m = re.search(rb"%s\s*(?:(\d+)\s+0\s+R|<<)" % re.escape(cle), objet)
    if not m:
        return b""
    if m.group(1):
        return objets.get(int(m.group(1)), b"")
    debut = m.end() - 2
    profondeur = 0
    for i in range(debut, len(objet) - 1):
        if objet[i:i + 2] == b"<<":
            profondeur += 1
        elif objet[i:i + 2] == b">>":
            profondeur -= 1
            if profondeur == 0:
                return objet[debut:i + 2]
    return objet[debut:]


def _table_de(police: bytes, objets: dict[int, bytes]) -> Table | None:
    m = re.search(rb"/ToUnicode\s+(\d+)\s+0\s+R", police)
    contenu = _flux(objets.get(int(m.group(1)), b"")) if m else None
    return _cmap(contenu) if contenu else None


def _polices_par_contenu(objets: dict[int, bytes]) -> dict[int, dict[bytes, Table]]:
    """Pour chaque flux de contenu, les polices que SA page déclare.

    Le même nom — ``/TT0``, ``/F1`` — désigne une police différente d'une
    page à l'autre dès qu'un producteur sous-ensemble ses polices par page,
    ce que Word fait : chaque page a son ``/TT0`` et sa table. Une table
    unique par nom, la dernière rencontrée, traduisait donc chaque page avec
    les codes d'une autre — et c'est ce qui rendait le jaune budgétaire en
    lettres décalées. On lit donc, page par page, ``/Resources`` puis
    ``/Font``, et l'on rattache la table au numéro du flux ``/Contents``.
    """
    par_contenu: dict[int, dict[bytes, Table]] = {}
    for numero_objet, objet in objets.items():
        # Une page rattache ses polices à son flux ``/Contents`` ; un
        # formulaire (``/Subtype /Form``, un tableau collé depuis Excel, par
        # exemple) est son propre flux et porte ses propres ressources.
        page = b"/Contents" in objet
        if not page and not (b"/Form" in objet and b"/Resources" in objet):
            continue
        polices = _dictionnaire(_dictionnaire(objet, b"/Resources", objets), b"/Font", objets)
        if not polices:
            continue
        tables: dict[bytes, Table] = {}
        for nom, numero in re.findall(rb"/(\w+)\s+(\d+)\s+0\s+R", polices):
            table = _table_de(objets.get(int(numero), b""), objets)
            if table:
                tables[nom] = table
        if not page:
            par_contenu[numero_objet] = tables
            continue
        m = re.search(rb"/Contents\s*(?:(\d+)\s+0\s+R|\[([^\]]*)\])", objet)
        if not m:
            continue
        numeros = [int(m.group(1))] if m.group(1) else [
            int(n) for n in re.findall(rb"(\d+)\s+0\s+R", m.group(2))]
        for numero in numeros:
            par_contenu[numero] = tables
    return par_contenu


def _polices(octets: bytes) -> dict[bytes, dict[int, str]]:
    """Associe chaque nom de police (/F1…) à sa table ToUnicode, pour tout
    le document : le repli quand aucune page ne rattache le flux."""
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


def _litteral(brut: bytes, table: dict[int, str] | None = None) -> str:
    texte = ECHAPPEMENT.sub(
        lambda m: chr(int(m.group(1), 8)) if m.group(1)
        else LETTRES.get(m.group(2), m.group(2)) if m.group(2) is not None else "",
        brut.decode("latin-1"))
    if not table:
        return texte
    # Les octets de la chaîne sont des codes de la police, pas des lettres :
    # la table les traduit, par un ou par deux selon ce qu'elle déclare. Un
    # code qu'elle ne connaît pas et qui tombe dans l'ASCII imprimable est
    # rendu tel quel — une police qui numérote ses glyphes n'en produit pas,
    # une police à encodage standard n'en produit que.
    octets = texte.encode("latin-1", errors="replace")
    largeur = getattr(table, "largeur", 1)
    codes = [int.from_bytes(octets[i:i + largeur], "big")
             for i in range(0, len(octets), largeur)]
    return "".join(
        table[code] if code in table else (chr(code) if 32 <= code < 127 else "")
        for code in codes
    )


def _hexa(brut: bytes, table: dict[int, str] | None) -> str:
    chiffres = re.sub(rb"[^0-9A-Fa-f]", b"", brut).decode("ascii")
    pas = 2 * getattr(table, "largeur", 2)
    if len(chiffres) % pas:
        chiffres = chiffres.ljust(len(chiffres) + pas - len(chiffres) % pas, "0")
    codes = [int(chiffres[i:i + pas], 16) for i in range(0, len(chiffres), pas)]
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
    # Un dictionnaire en ligne — les propriétés d'un contenu balisé, « /Span
    # <</Lang (en-US)>> BDC » — porte des chaînes qui ne sont pas du texte :
    # on le saute d'un bloc, sinon « en-US » s'imprime entre chaque cellule.
    rb"|(?P<dict><<.*?>>)"
    rb"|(?P<hex><[0-9A-Fa-f\s]+>)"
    rb"|(?P<txt>\((?:[^()\\]|\\.)*\))"
    # Les crochets d'un tableau ``TJ`` et les nombres qu'il intercale entre
    # ses chaînes : un recul de plus d'un cinquième de cadratin est une espace
    # que le producteur n'a pas écrite — Word pose « Rapport » et « sur » dans
    # le même tableau, séparés par -250, et les coller rend « Rapportsur ».
    rb"|(?P<ouvre>\[)"
    rb"|(?P<ferme>\])"
    rb"|(?P<nombre>-?\d+(?:\.\d+)?)",
    re.S,
)
ESPACE_DE_TABLEAU = -180.0
#: Le groupe qui porte le nom de la police dans un jeton ``Tf`` : celui qui
#: suit le groupe nommé, quel que soit le rang des autres. Un rang écrit en
#: dur — 9 — désignait en fait le groupe ``txt``, si bien que le nom de la
#: police restait à ``None`` et qu'aucune table ToUnicode n'était appliquée
#: aux chaînes : le charabia « 5DSSRUW » venait de là autant que du reste.
NOM_DE_POLICE = JETONS.groupindex["tf"] + 1


def _reels(operandes: bytes) -> list[float]:
    """La tête numérique d'un opérateur de position.

    On s'arrête au premier jeton qui n'est pas un nombre, ce qui laisse de côté
    le nom de l'opérateur — le groupe capturé porte « 0 -1.6 Td », le « Td »
    compris — et, surtout, l'opérande réduit à « - » que certains producteurs
    émettent. ``float`` levait alors, et TOUT le rapport devenait illisible :
    c'est ce qui fermait celui de 1995 à la CCSS, vingt méga-octets pourtant
    lisibles par ailleurs.

    On ne devine jamais la valeur manquante — la mettre à zéro déplacerait le
    texte sans prévenir. C'est à l'appelant de vérifier qu'il en a assez, et de
    SAUTER l'opérateur sinon, ce qui laisse le curseur où il était.
    """
    valeurs: list[float] = []
    for jeton in operandes.split():
        try:
            valeurs.append(float(jeton))
        except ValueError:
            break
    return valeurs


def _fragments(octets: bytes) -> list[tuple[int, float, float, str]]:
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
    objets = _objets(octets)
    communes = _polices(octets)
    par_contenu = _polices_par_contenu(objets)
    fragments: list[tuple[int, float, float, str]] = []
    for page, (numero, objet) in enumerate(objets.items()):
        # Une image JPEG contient « Tj » une fois sur dix, par hasard : on ne
        # la lit pas comme du texte.
        if b"/Image" in objet[:max(objet.find(b"stream"), 0)]:
            continue
        contenu = _flux(objet)
        if not contenu or (b"Tj" not in contenu and b"TJ" not in contenu):
            continue
        tables = par_contenu.get(numero, communes)
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
        dans_tableau = False
        for jeton in JETONS.finditer(contenu):
            if jeton.group("dict"):
                continue
            if jeton.group("ouvre") or jeton.group("ferme"):
                dans_tableau = bool(jeton.group("ouvre"))
                continue
            if jeton.group("nombre"):
                if dans_tableau and float(jeton.group("nombre")) < ESPACE_DE_TABLEAU:
                    fragments.append((page, y, x, " "))
                continue
            if jeton.group("tm"):
                nombres = _reels(jeton.group("tm"))
                if len(nombres) < 6:
                    continue
                echelle_x, echelle_y = nombres[0], nombres[3]
                x, y = nombres[4], nombres[5]
            elif jeton.group("td"):
                nombres = _reels(jeton.group("td"))
                if len(nombres) < 2:
                    continue
                x += nombres[0] * echelle_x
                y += nombres[1] * echelle_y
                if jeton.group("td").rstrip().endswith(b"TD"):
                    interligne = -nombres[1] * echelle_y
            elif jeton.group("tl"):
                nombres = _reels(jeton.group("tl"))
                if not nombres:
                    continue
                interligne = nombres[0] * echelle_y
            elif jeton.group("etoile") or jeton.group("retour"):
                y -= interligne
            elif jeton.group("tf"):
                police = jeton.group(NOM_DE_POLICE)
            else:
                morceau = (_hexa(jeton.group("hex"), tables.get(police))
                           if jeton.group("hex")
                           else _litteral(jeton.group("txt")[1:-1], tables.get(police)))
                if morceau.strip():
                    fragments.append((page, y, x, morceau))
                elif morceau:
                    # Une chaîne qui n'est qu'une espace est l'espace entre
                    # deux mots que le producteur a posés séparément —
                    # « (Effectif) ( ) (total) » — : la jeter les colle. Une
                    # insécable — la fine des milliers — reste insécable.
                    insecable = morceau.strip(" \t\r\n\f\v")
                    fragments.append((page, y, x, " " if insecable else " "))

    return fragments


def _normaliser(texte: str) -> str:
    """Une espace pour toute suite d'espaces ordinaires ; UNE ESPACE INSÉCABLE
    pour toute suite d'insécables (U+00A0, U+202F), et elle reste insécable.
    Le jaune budgétaire sépare ses milliers d'une fine insécable et ses
    cellules d'une espace de position : « 1 339 945 1 654 863 » ne se
    découpe en deux nombres que si les deux espaces restent différentes."""
    texte = re.sub(r"[  ]+", " ", texte)
    return re.sub(r"[ \t\r\n\f\v]+", " ", texte).strip()


def _assembler(fragments: list[tuple[int, float, float, str]],
               tolerance: float) -> list[str]:
    """Regroupe des fragments déjà triés en lignes visuelles."""
    lignes: list[str] = []
    courante: list[str] = []
    ordonnee = None
    feuille = None
    abscisse = None
    for page, y, x, morceau in fragments:
        meme_ligne = (ordonnee is not None and page == feuille
                      and abs(y - ordonnee) <= tolerance)
        if meme_ligne or ordonnee is None:
            # DEUX FRAGMENTS POSÉS À DES ABSCISSES DIFFÉRENTES SONT SÉPARÉS
            # PAR UNE ESPACE. Word n'écrit pas les espaces d'un tableau : il
            # pose chaque cellule, et souvent chaque mot, par son propre
            # ``Tm``. Les coller rendait « Prise en charge de cotisations »
            # comme « Priseenchargedecotisations », et surtout « 4 929 5 002 »
            # comme « 49295002 » — un nombre qui n'existe pas. Les glyphes
            # d'un même tableau ``TJ``, eux, gardent la même abscisse et
            # restent collés : « 2023 » ne devient pas « 2 0 2 3 ».
            if meme_ligne and abscisse is not None and abs(x - abscisse) > 0.01:
                courante.append(" ")
            courante.append(morceau)
        else:
            lignes.append(_normaliser("".join(courante)))
            courante = [morceau]
        ordonnee, feuille, abscisse = y, page, x
    if courante:
        lignes.append(re.sub(r"\s+", " ", "".join(courante)).strip())
    return [l for l in lignes if l]


def lignes_pdf(octets: bytes, tolerance: float = 3.0) -> list[str]:
    """Reconstitue les lignes visuelles du document, de haut en bas.

    LE NUMÉRO DE FLUX FAIT PARTIE DE LA CLÉ, et c'est tout sauf un détail.
    Chaque page d'un PDF a son propre repère : l'ordonnée 700 y désigne le même
    endroit de la feuille, page 1 comme page 60. Regrouper les fragments sur la
    seule ordonnée collait bout à bout la ligne du haut de CHAQUE page — un
    titre de la page 1 suivi d'un chiffre de la page 40 et d'une note de la
    page 97, dans une même chaîne. Sur la chronologie de la CARMF, cent pages
    de tableaux, cela rendait huit lignes pour cent quatre-vingt mille
    caractères, et l'on en concluait que la mise en page « ne se reconstituait
    pas ». Elle se reconstitue très bien : c'est le lecteur qui empilait les
    pages.
    """
    fragments = _fragments(octets)
    fragments.sort(key=lambda f: (f[0], -f[1], f[2]))
    return _assembler(fragments, tolerance)


def lignes_par_page(octets: bytes, tolerance: float = 3.0) -> list[list[str]]:
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
    """
    fragments = _fragments(octets)
    fragments.sort(key=lambda f: (f[0], -f[1], f[2]))
    pages: dict[int, list[tuple[int, float, float, str]]] = {}
    for fragment in fragments:
        pages.setdefault(fragment[0], []).append(fragment)
    return [_assembler(pages[page], tolerance) for page in sorted(pages)]


def texte_pdf(octets: bytes) -> str:
    return "\n".join(lignes_pdf(octets))


if __name__ == "__main__":
    import sys
    print(texte_pdf(open(sys.argv[1], "rb").read()))
