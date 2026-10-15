"""Le banc synthétique du lecteur PDF : des documents fabriqués (action 161, étape 4).

Outil provisoire, à retirer avec le cœur Python du lecteur (voir
``fabrique.py``). Chaque document est lu par ``lignes_pdf`` et
``lignes_par_page`` (Python) et par ``lignesPdf`` et ``lignesParPage``
(JavaScript, par node, en un seul lot), tels qu'ils sont sur le disque.

    python -I scripts/banc_lecture_pdf/synthetique.py cibles
    python -I scripts/banc_lecture_pdf/synthetique.py hasard N GRAINE [risque…]

``cibles`` : un document par écart que l'analyse a relevé entre les deux
lecteurs, tous alignés depuis (deuxième partie de l'étape 4) : chacun doit se
lire pareil. ``hasard`` : N documents tirés au hasard, sans les risques relevés
sauf ceux que l'on nomme (``RISQUES``) ; aucun écart n'est attendu, avec ou
sans eux.
"""
from __future__ import annotations

import base64
import json
import random
import subprocess
import sys
import zlib
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
from commun import TRAVAIL, lecteur_python  # noqa: E402

_PY = lecteur_python()
lignes_pdf, lignes_par_page = _PY.lignes_pdf, _PY.lignes_par_page
SORTIE = TRAVAIL / "synthetique"


# -- fabrique ------------------------------------------------------------------

def objet(n: int, corps: bytes) -> bytes:
    return b"%d 0 obj\n" % n + corps + b"\nendobj\n"


EVITER_FIN_NL = [False]


def flux(dic: bytes, donnees: bytes, comprimer: bool = False, queue: bytes = b"") -> bytes:
    if comprimer:
        while EVITER_FIN_NL[0] and zlib.compress(donnees)[-1] in (10, 13):
            donnees += b" "
        donnees = zlib.compress(donnees) + queue
        dic = dic[:-2] + b" /Filter /FlateDecode >>"
    return dic[:-2] + b" /Length %d >>\nstream\n" % len(donnees) + donnees + b"\nendstream"


def document(*objets: bytes) -> bytes:
    return b"%PDF-1.5\n" + b"".join(objets) + b"trailer\n<< >>\n%%EOF\n"


def cmap(largeur: int, chars: dict[int, str], plages: list = (), brut_dst: dict | None = None
         ) -> bytes:
    plage = b"<00> <FF>" if largeur == 1 else b"<0000> <FFFF>"
    corps = b"1 begincodespacerange\n" + plage + b"\nendcodespacerange\n"
    if chars:
        corps += b"%d beginbfchar\n" % len(chars)
        for code, lettre in chars.items():
            corps += b"<%s> <%s>\n" % (("%0*X" % (2 * largeur, code)).encode(),
                                       lettre.encode("utf-16-be").hex().upper().encode())
        corps += b"endbfchar\n"
    if brut_dst:
        corps += b"%d beginbfchar\n" % len(brut_dst)
        for code, dst in brut_dst.items():
            corps += b"<%s> <%s>\n" % (("%0*X" % (2 * largeur, code)).encode(), dst)
        corps += b"endbfchar\n"
    if plages:
        corps += b"%d beginbfrange\n" % len(plages) + b"".join(plages) + b"endbfrange\n"
    return corps


def page_simple(contenu: bytes, police: bytes, table: bytes | None, *,
                comprimer_contenu=False, comprimer_table=False, queue=b"") -> bytes:
    """Une page, sa police /F1 et sa table ToUnicode (ou aucune)."""
    vers_table = b" /ToUnicode 5 0 R" if table is not None else b""
    objs = [objet(1, b"<< /Type /Page /Resources << /Font << /F1 4 0 R >> >> /Contents 3 0 R >>"),
            objet(3, flux(b"<< >>", contenu, comprimer_contenu, queue)),
            objet(4, police[:-2] + vers_table + b" >>")]
    if table is not None:
        objs.append(objet(5, flux(b"<< >>", table, comprimer_table)))
    return document(*objs)


WINANSI = b"<< /Type /Font /Subtype /TrueType /Encoding /WinAnsiEncoding >>"
SIMPLE = b"<< /Type /Font /Subtype /Type1 >>"
TYPE0 = b"<< /Type /Font /Subtype /Type0 /Encoding /Identity-H >>"


def finit_par(octet: int, fabriquer) -> bytes:
    """Le premier contenu dont la compression finit par ``octet``."""
    for n in range(100_000):
        contenu = fabriquer(n)
        if zlib.compress(contenu)[-1] == octet:
            return contenu
    raise RuntimeError("introuvable")


def cibles() -> list[tuple[str, bytes]]:
    docs = []
    # 1. Un flux de contenu compressé qui finit par \n, puis par \r.
    docs.append(("contenu_finit_par_LF", page_simple(
        b"BT /F1 10 Tf 60 700 Td (FLUX 1399) Tj ET", SIMPLE, None, comprimer_contenu=True)))
    cr = finit_par(13, lambda n: b"BT /F1 10 Tf 60 700 Td (FLUX %d) Tj ET" % n)
    docs.append(("contenu_finit_par_CR", page_simple(cr, SIMPLE, None, comprimer_contenu=True)))
    # 2. Une table ToUnicode compressée qui finit par \n : la police perd sa table.
    corr = {1: "R", 2: "a", 3: "p", 4: "o", 5: "r", 6: "t"}
    table = finit_par(10, lambda n: cmap(1, corr) + b"%% %d\n" % n)
    docs.append(("table_finit_par_LF", page_simple(
        b"BT /F1 10 Tf 60 700 Td (\\001\\002\\003\\003\\004\\005\\006) Tj ET",
        SIMPLE, table, comprimer_table=True)))
    # 3. Un flux suivi de plus de mille octets de bavardage avant endstream.
    docs.append(("flux_tres_bavard", page_simple(
        b"BT /F1 10 Tf 60 700 Td (BAVARD) Tj ET", SIMPLE, None, comprimer_contenu=True,
        queue=b"\n" + b"x" * 1500)))
    docs.append(("flux_peu_bavard", page_simple(
        b"BT /F1 10 Tf 60 700 Td (BAVARD) Tj ET", SIMPLE, None, comprimer_contenu=True,
        queue=b"\n" + b"x" * 100)))
    # 4. Une table vide (son codespacerange seul), police simple, WinAnsi, Type0.
    vide = cmap(1, {})
    texte = b"BT /F1 10 Tf 60 700 Td (Caf\\351 \\200 5) Tj 60 680 Td <41424344> Tj ET"
    docs.append(("table_vide_simple", page_simple(texte, SIMPLE, vide)))
    docs.append(("table_vide_winansi", page_simple(texte, WINANSI, vide)))
    docs.append(("table_vide_type0", page_simple(
        b"BT /F1 10 Tf 60 700 Td <00410042> Tj 60 680 Td (\\000A\\000B) Tj ET", TYPE0, cmap(2, {}))))
    # 5. Un échappement octal au-delà de \377, sans table et avec.
    docs.append(("octal_haut_sans_table", page_simple(
        b"BT /F1 10 Tf 60 700 Td (A\\501B) Tj ET", SIMPLE, None)))
    docs.append(("octal_haut_avec_table", page_simple(
        b"BT /F1 10 Tf 60 700 Td (A\\501B) Tj ET", WINANSI, cmap(1, {0x41: "A", 0x42: "B", 0x41 + 0x100 - 0x100: "A"}))))
    # 6. Les codes que cp1252 ne définit pas, dans une police WinAnsi à table.
    docs.append(("cp1252_indefini", page_simple(
        b"BT /F1 10 Tf 60 700 Td (A\\201B\\215C\\217D\\220E\\235F) Tj ET",
        WINANSI, cmap(1, {0x41: "A"}))))
    # 7. Les espaces que Python et JavaScript ne reconnaissent pas de même.
    docs.append(("nel_en_fin_de_ligne", page_simple(
        b"BT /F1 10 Tf 60 700 Td (Suite\\205) Tj ET", SIMPLE, None)))
    docs.append(("nel_seul", page_simple(
        b"BT /F1 10 Tf 60 700 Td (A) Tj 100 0 Td (\\205) Tj 100 0 Td (B) Tj ET", SIMPLE, None)))
    docs.append(("separateur_x1c", page_simple(
        b"BT /F1 10 Tf 60 700 Td (\\034Titre\\034) Tj ET", SIMPLE, None)))
    docs.append(("bom_par_table", page_simple(
        b"BT /F1 10 Tf 60 700 Td (\\001A\\001) Tj ET", SIMPLE,
        cmap(1, {1: "﻿", 0x41: "A"}))))
    # 8. Une destination de table à nombre impair de chiffres.
    docs.append(("destination_un_octet", page_simple(
        b"BT /F1 10 Tf 60 700 Td (\\001\\002) Tj ET", SIMPLE,
        cmap(1, {2: "B"}, brut_dst={1: b"41"}))))
    docs.append(("destination_trois_chiffres", page_simple(
        b"BT /F1 10 Tf 60 700 Td (\\001\\002) Tj ET", SIMPLE,
        cmap(1, {2: "B"}, brut_dst={1: b"041"}))))
    # 9. Défauts communs : la dernière ligne perd ses insécables.
    docs.append(("insecables_derniere_ligne", page_simple(
        b"BT /F1 10 Tf 60 720 Td (1\\2401 339\\240945 1\\240654) Tj "
        b"0 -20 Td (1\\2401 339\\240945 1\\240654) Tj ET", WINANSI, cmap(1, {0x41: "A"}))))
    # 10. /Contents qui désigne un objet tableau : flux non réunis, polices perdues.
    contenus = [b"q 0.5 0 0 0.5 0 0 cm", b"BT /F1 10 Tf 60 700 Td (\\001\\002) Tj ET Q"]
    docs.append(("contents_indirect", document(
        objet(1, b"<< /Type /Page /Resources << /Font << /F1 4 0 R >> >> /Contents 6 0 R >>"),
        objet(6, b"[2 0 R 3 0 R]"),
        objet(2, flux(b"<< >>", contenus[0])), objet(3, flux(b"<< >>", contenus[1])),
        objet(4, SIMPLE[:-2] + b" /ToUnicode 5 0 R >>"),
        objet(5, flux(b"<< >>", cmap(1, {1: "O", 2: "K"}))),
        objet(7, b"<< /Type /Page /Resources << /Font << /F1 8 0 R >> >> /Contents 9 0 R >>"),
        objet(8, SIMPLE[:-2] + b" /ToUnicode 10 0 R >>"),
        objet(9, flux(b"<< >>", b"BT /F1 10 Tf 60 650 Td (\\001\\002) Tj ET")),
        objet(10, flux(b"<< >>", cmap(1, {1: "x", 2: "y"}))))))
    return docs


# -- le hasard ---------------------------------------------------------------

RISQUES = ("fin_nl", "octal_haut", "table_vide", "cp1252_indefini", "espaces_unicode",
           "hex_impair")


def hasard(n: int, graine: int, risques: set[str]) -> list[tuple[str, bytes]]:
    r = random.Random(graine)
    docs = []
    for k in range(n):
        docs.append((f"h{graine}-{k}", _document_au_hasard(r, risques)))
    return docs


def _nombre(r: random.Random) -> bytes:
    choix = r.random()
    if choix < 0.05:
        return b"-"
    if choix < 0.5:
        return b"%d" % r.randint(-800, 800)
    return b"%.2f" % r.uniform(-800, 800)


def _octets_de_chaine(r: random.Random, risques: set[str], largeur: int) -> bytes:
    sortie = b""
    for _ in range(r.randint(0, 12)):
        c = r.random()
        if c < 0.45:
            sortie += bytes([r.choice(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ,.%")])
        elif c < 0.55:
            sortie += r.choice([b"\\n", b"\\r", b"\\t", b"\\(", b"\\)", b"\\\\", b"\\\n", b"\\b", b"\\f",
                                b"\\q"])
        elif c < 0.7:
            interdits = _interdits(risques)
            v = r.choice([v for v in range(0o777 if "octal_haut" in risques else 0o400)
                          if v not in interdits])
            sortie += (b"\\%o" % v if "octal_haut" in risques and r.random() < 0.5
                       else b"\\%03o" % v)
        elif c < 0.8:
            sortie += bytes([r.choice([0xA0, 0xE9, 0xE8, 0x80, 0x92, 0x96, 0x9C, 0xAB, 0xBB])])
        elif c < 0.9 and "cp1252_indefini" in risques:
            sortie += bytes([r.choice([0x81, 0x8D, 0x8F, 0x90, 0x9D])])
        elif c < 0.95 and "espaces_unicode" in risques:
            sortie += bytes([r.choice([0x85, 0x1C, 0x1D, 0x1E, 0x1F])])
        else:
            sortie += b" "
    return b"(" + sortie + b")"


def _interdits(risques: set[str]) -> set[int]:
    interdits = set()
    if "espaces_unicode" not in risques:
        interdits |= {0x1C, 0x1D, 0x1E, 0x1F, 0x85}
    if "cp1252_indefini" not in risques:
        interdits |= {0x81, 0x8D, 0x8F, 0x90, 0x9D}
    return interdits


def _hexa(r: random.Random, largeur: int, risques: set[str] = frozenset()) -> bytes:
    interdits = _interdits(risques)
    codes = []
    while len(codes) < r.randint(0, 6):
        c = r.randint(0, 0xFF if largeur == 1 else 0x2FF)
        if not ({c & 0xFF, c >> 8} & interdits):
            codes.append(c)
    hexa = "".join("%0*X" % (2 * largeur, c) for c in codes)
    if r.random() < 0.2:
        hexa = hexa[:-1]
    if r.random() < 0.2:
        hexa = " ".join(hexa[i:i + 3] for i in range(0, len(hexa), 3))
    return b"<" + hexa.encode() + b">"


def _contenu(r: random.Random, risques: set[str], polices: list[tuple[bytes, int]]) -> bytes:
    ops: list[bytes] = []
    if r.random() < 0.3:
        ops.append(b"0.05 0 0 -0.05 0 841.9 cm" if r.random() < 0.5 else
                   b"%s %s %s %s %s %s cm" % tuple(_nombre(r) for _ in range(6)))
    largeur = 1
    for _ in range(r.randint(1, 30)):
        c = r.random()
        if c < 0.08:
            ops.append(b"BT")
        elif c < 0.12:
            ops.append(b"ET")
        elif c < 0.2:
            nom, largeur = r.choice(polices)
            ops.append(b"/%s %s Tf" % (nom, _nombre(r)))
        elif c < 0.3:
            ops.append(b"%s %s %s" % (_nombre(r), _nombre(r), r.choice([b"Td", b"TD"])))
        elif c < 0.36:
            m = r.choice([b"1 0 0 1", b"9 0 0 9", b"0 -1 -1 0", b"0 1 -1 0", b"1 0 0 -1",
                          b"%s %s %s %s" % tuple(_nombre(r) for _ in range(4))])
            ops.append(m + b" %s %s Tm" % (_nombre(r), _nombre(r)))
        elif c < 0.4:
            ops.append(b"%s TL" % _nombre(r))
        elif c < 0.43:
            ops.append(b"T*")
        elif c < 0.47:
            ops.append(r.choice([b"q", b"Q"]))
        elif c < 0.5:
            ops.append(b"%s %s %s %s %s %s cm" % tuple(_nombre(r) for _ in range(6)))
        elif c < 0.53:
            ops.append(b"/Span <</Lang (en-US)>> BDC")
        elif c < 0.7:
            ops.append(_octets_de_chaine(r, risques, largeur) + b" Tj")
        elif c < 0.78:
            ops.append(_hexa(r, largeur, risques) + b" Tj")
        elif c < 0.9:
            elements = []
            for _ in range(r.randint(1, 5)):
                e = r.random()
                if e < 0.4:
                    elements.append(_octets_de_chaine(r, risques, largeur))
                elif e < 0.6:
                    elements.append(_hexa(r, largeur, risques))
                else:
                    elements.append(b"%d" % r.choice([-250, -180, -179, 120, -1000, 5]))
            ops.append(b"[" + b" ".join(elements) + b"] TJ")
        elif c < 0.95:
            ops.append(_octets_de_chaine(r, risques, largeur) + b" '")
        else:
            ops.append(b"1 2 " + _octets_de_chaine(r, risques, largeur) + b' "')
    return r.choice([b" ", b"\n", b"\r\n"]).join(ops)


def _table(r: random.Random, risques: set[str], largeur: int) -> bytes:
    if "table_vide" in risques and r.random() < 0.3:
        return cmap(largeur, {})
    chars = {}
    for _ in range(r.randint(1, 20)):
        code = r.randint(0, 0xFF if largeur == 1 else 0x2FF)
        chars[code] = r.choice("abcdefghijklmnopqrstuvwxyzABCDEFG0123456789 €’é  "
                               + ("﻿\x85\x1c" if "espaces_unicode" in risques else ""))
    plages = []
    for _ in range(r.randint(0, 3)):
        debut = r.randint(0, 0xF0 if largeur == 1 else 0x2F0)
        fin = debut + r.randint(0, 8)
        f = "%0*X" % (2 * largeur, debut), "%0*X" % (2 * largeur, fin)
        if r.random() < 0.5:
            plages.append(b"<%s> <%s> <%04X>\n" % (f[0].encode(), f[1].encode(), r.randint(0x41, 0x7A)))
        else:
            dst = b" ".join(b"<%04X>" % r.randint(0x41, 0x7A) for _ in range(r.randint(1, 10)))
            plages.append(b"<%s> <%s> [%s]\n" % (f[0].encode(), f[1].encode(), dst))
    brut = None
    if "hex_impair" in risques and r.random() < 0.3:
        brut = {r.randint(0, 0xFF if largeur == 1 else 0x2FF): r.choice([b"41", b"041", b"00410"])}
    return cmap(largeur, chars, plages, brut)


def _document_au_hasard(r: random.Random, risques: set[str]) -> bytes:
    objets = []
    numero = [100]

    def nouveau() -> int:
        numero[0] += 1
        return numero[0]

    EVITER_FIN_NL[0] = "fin_nl" not in risques
    comprimer = lambda: r.random() < 0.7  # noqa: E731
    en_flux_d_objets: dict[int, bytes] = {}
    for _ in range(r.randint(1, 4)):
        polices = []
        refs = []
        for i in range(r.randint(1, 3)):
            nom = b"F%d" % r.randint(1, 3)
            genre = r.choice(["type0", "winansi", "simple", "sans"])
            largeur = 2 if genre == "type0" else 1
            n_police = nouveau()
            dic = {"type0": TYPE0, "winansi": WINANSI, "simple": SIMPLE, "sans": SIMPLE}[genre]
            if genre != "sans":
                n_table = nouveau()
                objets.append(objet(n_table, flux(b"<< >>", _table(r, risques, largeur), comprimer())))
                dic = dic[:-2] + b" /ToUnicode %d 0 R >>" % n_table
            if r.random() < 0.3:
                en_flux_d_objets[n_police] = dic
            else:
                objets.append(objet(n_police, dic))
            polices.append((nom, largeur))
            refs.append(b"/%s %d 0 R" % (nom, n_police))
        n_contenus = [nouveau() for _ in range(r.choice([1, 1, 2, 3]))]
        for n in n_contenus:
            objets.append(objet(n, flux(b"<< >>", _contenu(r, risques, polices), comprimer())))
        contents = (b"%d 0 R" % n_contenus[0] if len(n_contenus) == 1 and r.random() < 0.7
                    else b"[" + b" ".join(b"%d 0 R" % n for n in n_contenus) + b"]")
        ressources = b"<< /Font << %s >> >>" % b" ".join(refs)
        objets.append(objet(nouveau(), b"<< /Type /Page /Resources %s /Contents %s >>"
                            % (ressources, contents)))
    if en_flux_d_objets:
        tete, corps = b"", b""
        for num, contenu in en_flux_d_objets.items():
            tete += b"%d %d " % (num, len(corps))
            corps += contenu + b"\n"
        donnees = tete + b"\n" + corps
        dic = b"<< /Type /ObjStm /N %d /First %d >>" % (len(en_flux_d_objets), len(tete) + 1)
        while "fin_nl" not in risques and zlib.compress(donnees)[-1] in (10, 13):
            donnees += b" "
        objets.append(objet(nouveau(), flux(dic, donnees, comprimer=True)))
    r.shuffle(objets)
    return document(*objets)


# -- confrontation -----------------------------------------------------------

def lire_en_python(pdf: bytes) -> dict:
    try:
        return {"lignes": lignes_pdf(pdf), "pages": lignes_par_page(pdf)}
    except Exception as e:  # noqa: BLE001
        return {"erreur": f"{type(e).__name__}: {e}"}


def confronter(docs: list[tuple[str, bytes]]) -> list[dict]:
    SORTIE.mkdir(parents=True, exist_ok=True)
    lot = SORTIE / "lot.json"
    rendu = SORTIE / "rendu.json"
    lot.write_text(json.dumps([{"nom": nom, "b64": base64.b64encode(pdf).decode()}
                               for nom, pdf in docs]))
    subprocess.run(["node", str(ICI / "synthetique.mjs"), str(lot), str(rendu)], check=True)
    js = {e["nom"]: e for e in json.loads(rendu.read_text())}
    ecarts = []
    for nom, pdf in docs:
        py = lire_en_python(pdf)
        j = {k: v for k, v in js[nom].items() if k != "nom"}
        if py != j:
            ecarts.append({"nom": nom, "python": py, "javascript": j, "pdf": pdf})
    return ecarts


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "cibles":
        docs = cibles()
        ecarts = {e["nom"]: e for e in confronter(docs)}
        for nom, pdf in docs:
            py = lire_en_python(pdf)
            if nom in ecarts:
                e = ecarts[nom]
                print(f"ÉCART  {nom}\n   py: {e['python'].get('lignes', e['python'])!r}\n"
                      f"   js: {e['javascript'].get('lignes', e['javascript'])!r}")
                if e["python"].get("lignes") == e["javascript"].get("lignes"):
                    print(f"   (pages) py: {e['python'].get('pages')!r}\n"
                          f"           js: {e['javascript'].get('pages')!r}")
            else:
                print(f"pareil {nom}: {py.get('lignes', py)!r}")
    else:
        n, graine = int(sys.argv[2]), int(sys.argv[3])
        risques = set(sys.argv[4:])
        docs = hasard(n, graine, risques)
        ecarts = confronter(docs)
        print(f"{len(docs)} documents, risques {sorted(risques) or 'aucun'} : "
              f"{len(ecarts)} écart(s)")
        for e in ecarts[:4]:
            print(f"  {e['nom']}\n    py: {str(e['python'])[:300]}\n    js: {str(e['javascript'])[:300]}")
        (SORTIE / f"ecarts-{graine}.json").write_text(json.dumps(
            [{**e, "pdf": base64.b64encode(e["pdf"]).decode()} for e in ecarts]))
