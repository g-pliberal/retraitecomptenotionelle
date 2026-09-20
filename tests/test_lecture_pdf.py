"""Le lecteur PDF du dépôt, sur ce que le jaune budgétaire lui a appris.

Le jaune pensions du PLF 2026 sortait en lettres décalées — « 5DSSRUW » pour
« Rapport » — pour quatre raisons, chacune tenue ici par un document minimal
fabriqué à la main : les polices rangées dans un flux d'objets, les chaînes
littérales à un octet par code, le même nom de police qui désigne une police
différente d'une page à l'autre, et le rang du groupe qui portait le nom de la
police, faux depuis l'origine. Puis trois défauts de lecture qui collaient ou
salissaient les tableaux : les espaces posées seules, les dictionnaires en
ligne du contenu balisé, et les reculs d'un tableau ``TJ``.
"""

from __future__ import annotations

import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "fetch"))
from lecture_pdf import lignes_pdf  # noqa: E402


def _objet(numero: int, corps: bytes) -> bytes:
    return b"%d 0 obj\n" % numero + corps + b"\nendobj\n"


def _flux(dictionnaire: bytes, donnees: bytes, comprimer: bool = False) -> bytes:
    if comprimer:
        donnees = zlib.compress(donnees)
        dictionnaire = dictionnaire[:-2] + b" /Filter /FlateDecode >>"
    return (dictionnaire[:-2] + b" /Length %d >>\nstream\n" % len(donnees)
            + donnees + b"\nendstream")


def _cmap(largeur: int, correspondances: dict[int, str]) -> bytes:
    plage = b"<00> <FF>" if largeur == 1 else b"<0000> <FFFF>"
    chars = b"".join(
        b"<%s> <%s>\n" % (("%0*X" % (2 * largeur, code)).encode(),
                          lettre.encode("utf-16-be").hex().upper().encode())
        for code, lettre in correspondances.items()
    )
    return (b"1 begincodespacerange\n" + plage + b"\nendcodespacerange\n"
            + b"%d beginbfchar\n" % len(correspondances) + chars + b"endbfchar\n")


def _document(*objets: bytes) -> bytes:
    return b"%PDF-1.5\n" + b"".join(objets) + b"trailer\n<< >>\n%%EOF\n"


def _flux_d_objets(numero: int, contenus: dict[int, bytes]) -> bytes:
    """Un ``/ObjStm`` : en tête les paires « numéro décalage », puis les objets."""
    tete = b""
    corps = b""
    for num, contenu in contenus.items():
        tete += b"%d %d " % (num, len(corps))
        corps += contenu + b"\n"
    donnees = tete + b"\n" + corps
    dictionnaire = b"<< /Type /ObjStm /N %d /First %d >>" % (len(contenus), len(tete) + 1)
    return _objet(numero, _flux(dictionnaire, donnees, comprimer=True))


def test_les_polices_rangees_dans_un_flux_d_objets_sont_lues():
    """Page et police dans un ``/ObjStm`` compressé ; codes à un octet en
    chaîne littérale, que seule la table ToUnicode sait traduire."""
    contenu = b"BT /TT0 12 Tf 70 700 Td (\\001\\002\\002\\003) Tj ET"
    pdf = _document(
        _objet(5, _flux(b"<< >>", contenu)),
        _objet(7, _flux(b"<< >>", _cmap(1, {1: "A", 2: "n", 3: "e"}))),
        _flux_d_objets(9, {
            4: b"<< /Type /Page /Contents 5 0 R /Resources << /Font << /TT0 6 0 R >> >> >>",
            6: b"<< /Type /Font /Subtype /TrueType /ToUnicode 7 0 R >>",
        }),
    )
    assert lignes_pdf(pdf) == ["Anne"], lignes_pdf(pdf)


def test_le_meme_nom_de_police_change_de_table_d_une_page_a_l_autre():
    """Word sous-ensemble ses polices par page : le ``/TT0`` de la page 2 n'est
    pas celui de la page 1. Une table unique par nom lisait la page 2 avec les
    codes de la page 1."""
    pdf = _document(
        _objet(1, b"<< /Type /Page /Contents 2 0 R /Resources << /Font << /TT0 3 0 R >> >> >>"),
        _objet(2, _flux(b"<< >>", b"BT /TT0 12 Tf 70 700 Td (\\001\\002) Tj ET")),
        _objet(3, b"<< /Type /Font /ToUnicode 4 0 R >>"),
        _objet(4, _flux(b"<< >>", _cmap(1, {1: "U", 2: "N"}))),
        _objet(5, b"<< /Type /Page /Contents 6 0 R /Resources << /Font << /TT0 7 0 R >> >> >>"),
        _objet(6, _flux(b"<< >>", b"BT /TT0 12 Tf 70 700 Td (\\001\\002\\003\\004) Tj ET")),
        _objet(7, b"<< /Type /Font /ToUnicode 8 0 R >>"),
        _objet(8, _flux(b"<< >>", _cmap(1, {1: "D", 2: "E", 3: "U", 4: "X"}))),
    )
    assert lignes_pdf(pdf) == ["UN", "DEUX"], lignes_pdf(pdf)


def test_une_police_type0_lit_ses_codes_sur_deux_octets():
    """Identity-H : deux octets par code, en hexadécimal comme en littéral."""
    pdf = _document(
        _objet(1, b"<< /Type /Page /Contents 2 0 R /Resources << /Font << /C2_0 3 0 R >> >> >>"),
        _objet(2, _flux(b"<< >>", b"BT /C2_0 12 Tf 70 700 Td <00350044> Tj "
                                  b"0 -20 Td (\\000\\065\\000\\104) Tj ET")),
        _objet(3, b"<< /Type /Font /Subtype /Type0 /Encoding /Identity-H /ToUnicode 4 0 R >>"),
        _objet(4, _flux(b"<< >>", _cmap(2, {0x35: "R", 0x44: "a"}))),
    )
    assert lignes_pdf(pdf) == ["Ra", "Ra"], lignes_pdf(pdf)


def test_un_formulaire_porte_ses_propres_polices():
    """Un tableau collé depuis Excel est un ``/Form`` avec ses ressources."""
    pdf = _document(
        _objet(1, b"<< /Type /Page /Contents 2 0 R /Resources << /XObject << /Fm0 3 0 R >> >> >>"),
        _objet(2, _flux(b"<< >>", b"q /Fm0 Do Q")),
        _objet(3, _flux(b"<< /Type /XObject /Subtype /Form /BBox [0 0 100 100] "
                        b"/Resources << /Font << /F5 4 0 R >> >> >>",
                        b"BT /F5 8 Tf 10 50 Td (\\001\\002) Tj ET")),
        _objet(4, b"<< /Type /Font /ToUnicode 5 0 R >>"),
        _objet(5, _flux(b"<< >>", _cmap(1, {1: "O", 2: "K"}))),
    )
    assert lignes_pdf(pdf) == ["OK"], lignes_pdf(pdf)


def test_les_espaces_posees_seules_et_les_reculs_du_tableau_separent_les_mots():
    """« (Effectif) ( ) (total) » et « [(Rapport) -250 (sur)] TJ » : deux
    façons d'écrire une espace sans l'écrire, que le lecteur collait."""
    contenu = (b"BT /F1 10 Tf 70 700 Td (Effectif) Tj ( ) Tj (total) Tj "
               b"0 -20 Td [(Rapport) -250 (sur) -20 (les)] TJ ET")
    pdf = _document(_objet(1, _flux(b"<< >>", contenu)))
    assert lignes_pdf(pdf) == ["Effectif total", "Rapport surles"], lignes_pdf(pdf)


def test_un_dictionnaire_en_ligne_du_contenu_balise_ne_s_imprime_pas():
    """« /Span <</Lang (en-US)>> BDC » : la chaîne est une propriété, pas du texte."""
    contenu = (b"BT /F1 10 Tf 70 700 Td /Span <</MCID 3 /Lang (en-US)>> BDC "
               b"(FPE) Tj EMC ( ) Tj /Span <</Lang (en-US)>> BDC (Civils) Tj EMC ET")
    pdf = _document(_objet(1, _flux(b"<< >>", contenu)))
    assert lignes_pdf(pdf) == ["FPE Civils"], lignes_pdf(pdf)


def test_les_echappements_d_une_chaine_litterale_se_lisent_en_une_passe():
    """« \\\\101 » est une barre suivie de « 101 », pas la lettre A ; « \\n »
    et « \\( » sont ce que la norme dit."""
    contenu = b"BT /F1 10 Tf 70 700 Td (a\\\\101\\(b\\)\\101) Tj ET"
    pdf = _document(_objet(1, _flux(b"<< >>", contenu)))
    assert lignes_pdf(pdf) == ["a\\101(b)A"], lignes_pdf(pdf)


def test_une_image_n_est_pas_lue_comme_du_texte():
    """Une image JPEG contient « Tj » par hasard ; elle n'a rien à dire."""
    pdf = _document(
        _objet(1, _flux(b"<< /Type /XObject /Subtype /Image /Width 1 /Height 1 >>",
                        b"\x00 BT (BRUIT) Tj ET \xff")),
        _objet(2, _flux(b"<< >>", b"BT /F1 10 Tf 70 700 Td (TEXTE) Tj ET")),
    )
    assert lignes_pdf(pdf) == ["TEXTE"], lignes_pdf(pdf)
