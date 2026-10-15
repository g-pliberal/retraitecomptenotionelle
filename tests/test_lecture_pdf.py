"""Le lecteur PDF du dépôt, sur ce que le jaune budgétaire lui a appris.

Le jaune pensions du PLF 2026 sortait en lettres décalées — « 5DSSRUW » pour
« Rapport » — pour quatre raisons, chacune tenue ici par un document minimal
fabriqué à la main : les polices rangées dans un flux d'objets, les chaînes
littérales à un octet par code, le même nom de police qui désigne une police
différente d'une page à l'autre, et le rang du groupe qui portait le nom de la
police, faux depuis l'origine. Puis trois défauts de lecture qui collaient ou
salissaient les tableaux : les espaces posées seules, les dictionnaires en
ligne du contenu balisé, et les reculs d'un tableau ``TJ``. Et deux que le
relevé de carrière d'info-retraite (2026) a montrés, qui le rendaient page par
page du bas vers le haut : le repère retourné de la page, et la page coupée en
plusieurs flux. Et les tracés d'une page, que la figure 3B du jaune
pensions du PLF 2027 a demandés : ses barres sont des rectangles peints.

Le lecteur est celui du site, ``moteur/js/lecture-pdf.js``, que ces tests font
tourner par node à travers le module de la fabrique : ils tiennent à la fois le
lecteur, le pont et ce que la fabrique garde en Python. Ils sont les seuls ; un
fichier pour node seul rejouait les mêmes documents, jusqu'à l'action 161.
"""

from __future__ import annotations

import shutil
import sys
import zlib
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "fetch"))
from lecture_pdf import Aplat, aplats_de_page, lignes_pdf  # noqa: E402

#: Le lecteur est celui du site, que node fait tourner.
pytestmark = pytest.mark.skipif(shutil.which("node") is None,
                                reason="node absent : le lecteur PDF ne tourne pas sans lui")


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


def test_les_separateurs_et_la_ligne_suivante_sont_des_espaces():
    """``str.strip`` tient pour espaces \\x1c à \\x1f et \\x85 : une chaîne qui
    n'a qu'eux compte pour une insécable, et ils tombent aux bouts d'une ligne.
    Une police sans table ToUnicode écrit « … » par l'octet \\x85, et le
    programme d'une police lu comme du texte sème les séparateurs : les
    documents de la fabrique en sont pleins, et le lecteur du site, dont
    ``trim`` les ignore, les lit de même (action 161, étape 4)."""
    contenu = (b"BT /F1 10 Tf 60 720 Td (A) Tj 100 0 Td (\\205) Tj 100 0 Td (B) Tj "
               b"-200 -20 Td (\\034Titre\\035) Tj 0 -20 Td (Suite\\205) Tj 0 -20 Td (FIN) Tj ET")
    pdf = _document(_objet(1, _flux(b"<< >>", contenu)))
    assert lignes_pdf(pdf) == ["A \u00a0 B", "Titre", "Suite", "FIN"], lignes_pdf(pdf)


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


def test_un_echappement_octal_au_dela_de_377_perd_son_debordement():
    """La norme ignore le débordement d'un octal au-delà d'un octet :
    « \\501 » est « A », avec une table ou sans."""
    sans_table = b"BT /F1 10 Tf 70 700 Td (A\\501B) Tj ET"
    assert lignes_pdf(_document(_objet(1, _flux(b"<< >>", sans_table)))) == ["AAB"]
    avec_table = _document(
        _objet(1, b"<< /Type /Page /Resources << /Font << /F1 2 0 R >> >> /Contents 4 0 R >>"),
        _objet(2, b"<< /Type /Font /Subtype /TrueType /Encoding /WinAnsiEncoding "
                  b"/ToUnicode 3 0 R >>"),
        _objet(3, _flux(b"<< >>", _cmap(1, {0x41: "a", 0x42: "b"}))),
        _objet(4, _flux(b"<< >>", b"BT /F1 10 Tf 70 700 Td (A\\501B) Tj ET")),
    )
    assert lignes_pdf(avec_table) == ["aab"], lignes_pdf(avec_table)


def test_une_destination_abimee_de_la_table_ne_perd_pas_le_document():
    """Trois chiffres se complètent d'un zéro, comme toute chaîne hexadécimale
    de la norme ; un octet seul, ou un surrogat sans sa moitié, n'est pas de
    l'UTF-16 et rend « \ufffd », comme le décodeur ``utf-16-be``. Une seule
    destination de trois chiffres levait, et le document entier était perdu."""
    table = (b"1 begincodespacerange\n<00> <FF>\nendcodespacerange\n"
             b"4 beginbfchar\n<01> <041>\n<02> <41>\n<03> <D800>\n<04> <0042>\nendbfchar\n")
    pdf = _document(
        _objet(1, b"<< /Type /Page /Resources << /Font << /F1 2 0 R >> >> /Contents 4 0 R >>"),
        _objet(2, b"<< /Type /Font /Subtype /TrueType /ToUnicode 3 0 R >>"),
        _objet(3, _flux(b"<< >>", table)),
        _objet(4, _flux(b"<< >>", b"BT /F1 10 Tf 70 700 Td (\\001\\002\\003\\004) Tj ET")),
    )
    assert lignes_pdf(pdf) == ["\u0410\ufffd\ufffdB"], lignes_pdf(pdf)


def test_une_table_vide_se_lit_comme_aucune_table():
    """Une table ToUnicode qui ne dit rien — son codespacerange seul — ne
    traduit rien : la police se lit comme sans table, « é » compris."""
    vide = b"1 begincodespacerange\n<00> <FF>\nendcodespacerange\n"
    pdf = _document(
        _objet(1, b"<< /Type /Page /Resources << /Font << /F1 2 0 R >> >> /Contents 4 0 R >>"),
        _objet(2, b"<< /Type /Font /Subtype /Type1 /ToUnicode 3 0 R >>"),
        _objet(3, _flux(b"<< >>", vide)),
        _objet(4, _flux(b"<< >>", b"BT /F1 10 Tf 70 700 Td (Caf\\351 5) Tj ET")),
    )
    assert lignes_pdf(pdf) == ["Café 5"], lignes_pdf(pdf)


def test_un_code_que_cp1252_ne_definit_pas_rend_le_caractere_de_remplacement():
    """Une police WinAnsi traduit par cp1252 les codes que sa table ne dit
    pas ; cinq octets — \\x81, \\x8d, \\x8f, \\x90, \\x9d — n'y ont pas de
    lettre, et rendent « \ufffd », comme le décodeur du Python."""
    pdf = _document(
        _objet(1, b"<< /Type /Page /Resources << /Font << /F1 2 0 R >> >> /Contents 4 0 R >>"),
        _objet(2, b"<< /Type /Font /Subtype /TrueType /Encoding /WinAnsiEncoding "
                  b"/ToUnicode 3 0 R >>"),
        _objet(3, _flux(b"<< >>", _cmap(1, {0x41: "A"}))),
        _objet(4, _flux(b"<< >>", b"BT /F1 10 Tf 70 700 Td "
                                  b"(A\\201B\\215C\\217D\\220E\\235F) Tj ET")),
    )
    assert lignes_pdf(pdf) == ["A\ufffdB\ufffdC\ufffdD\ufffdE\ufffdF"], lignes_pdf(pdf)


def test_l_insecable_n_est_pas_une_espace_de_la_syntaxe():
    """Entre deux opérandes, la norme ne compte pour espace ni l'insécable ni
    aucun octet au-delà de l'ASCII : « 0\xa0700 Td » n'est pas un déplacement,
    et « HAUT » reste à l'origine, sous « BAS »."""
    contenu = (b"BT /F1 10 Tf 0 100 Td (BAS) Tj ET "
               b"BT /F1 10 Tf 0\xa0700 Td (HAUT) Tj ET")
    pdf = _document(_objet(1, _flux(b"<< >>", contenu)))
    assert lignes_pdf(pdf) == ["BAS", "HAUT"], lignes_pdf(pdf)


def test_une_image_n_est_pas_lue_comme_du_texte():
    """Une image JPEG contient « Tj » par hasard ; elle n'a rien à dire."""
    pdf = _document(
        _objet(1, _flux(b"<< /Type /XObject /Subtype /Image /Width 1 /Height 1 >>",
                        b"\x00 BT (BRUIT) Tj ET \xff")),
        _objet(2, _flux(b"<< >>", b"BT /F1 10 Tf 70 700 Td (TEXTE) Tj ET")),
    )
    assert lignes_pdf(pdf) == ["TEXTE"], lignes_pdf(pdf)


def test_une_police_simple_lit_par_un_octet_quoi_que_declare_sa_table():
    """InDesign écrit <0000> <FFFF> en codespacerange d'une police TrueType
    dont les entrées font un octet ; lue par deux, la page du rapport de
    l'OPEF perdait ses lettres. Et ce que la table ne dit pas, l'encodage
    WinAnsi de la police le dit : « é » est le code 233."""
    pdf = _document(
        _objet(1, b"<< /Type /Page /Contents 2 0 R /Resources << /Font << /F1 3 0 R >> >> >>"),
        _objet(2, _flux(b"<< >>", b"BT /F1 10 Tf 70 700 Td (du\\351) Tj ET")),
        _objet(3, b"<< /Type /Font /Subtype /TrueType /Encoding /WinAnsiEncoding /ToUnicode 4 0 R >>"),
        _objet(4, _flux(b"<< >>", _cmap(2, {0x64: "d", 0x75: "u"}))),
    )
    assert lignes_pdf(pdf) == ["dué"], lignes_pdf(pdf)


def test_chaque_objet_texte_repart_de_l_origine_de_la_page():
    """``BT`` remet la matrice de texte à l'identité : un ``Td`` qui suit part
    de l'origine de la page, non du curseur laissé par l'objet précédent.

    Un producteur qui ouvre un ``BT`` par ligne — et c'est ainsi que sont faits
    les relevés de carrière que le site reçoit — voyait sinon ses ordonnées
    s'additionner : la deuxième ligne se retrouvait à 1 380 au lieu de 680, la
    page partait vers le haut, et le tri de haut en bas rendait le document à
    l'envers, une ligne par fragment.
    """
    contenu = (b"BT /F1 10 Tf 60 700 Td (HAUT) Tj ET "
               b"BT /F1 10 Tf 60 680 Td (MILIEU) Tj ET "
               b"BT /F1 10 Tf 60 660 Td (BAS) Tj ET")
    pdf = _document(_objet(1, _flux(b"<< >>", contenu)))
    assert lignes_pdf(pdf) == ["HAUT", "MILIEU", "BAS"], lignes_pdf(pdf)


def test_le_repere_retourne_de_la_page_se_lit_de_haut_en_bas():
    """« 0.05 0 0 -0.05 0 841.9 cm » : des vingtièmes de point, l'origine en
    haut de la feuille, les ordonnées croissant vers le bas. C'est ainsi que
    le relevé de carrière d'info-retraite (2026) ouvre chaque page, et ses
    glyphes se redressent par « 1 0 0 -1 x y Tm ». Lu sans ce repère, il
    sortait du pied de page au titre.

    Une image posée entre ``q`` et ``Q`` compose son propre repère, que ``Q``
    défait ; le tampon de la marge, tourné d'un quart de tour, reste dans sa
    bande et se lit dans le sens de ses glyphes, vers le haut de la feuille.
    """
    contenu = (b"0.05 0 0 -0.05 0 841.9 cm "
               b"q 1698 0 0 -421 1013 11519 cm /X1 Do Q "
               b"BT /F1 200 Tf 1 0 0 -1 800 1000 Tm (HAUT) Tj ET "
               b"BT 0 -1 -1 0 385 6942 Tm (TAMPON) Tj 0 -1 -1 0 385 6000 Tm (LATERAL) Tj ET "
               b"BT 1 0 0 -1 800 1400 Tm (MILIEU) Tj ET "
               b"BT 1 0 0 -1 800 1800 Tm (BAS) Tj ET")
    pdf = _document(_objet(1, _flux(b"<< >>", contenu)))
    assert lignes_pdf(pdf) == ["HAUT", "MILIEU", "BAS", "TAMPON LATERAL"], lignes_pdf(pdf)


def test_une_page_en_plusieurs_flux_se_lit_d_un_seul_tenant():
    """``/Contents [2 0 R 3 0 R 4 0 R]`` : trois flux qui n'en font qu'un. Le
    relevé d'info-retraite pose le repère dans le premier, et coupe ses lignes
    entre les suivants : la ``Tm`` à la fin de l'un, la chaîne qu'elle place au
    début de l'autre. Lus chacun pour soi, la chaîne tombait à l'origine de la
    page, et le titre se coupait en deux pages."""
    pdf = _document(
        _objet(1, b"<< /Type /Page /Contents [2 0 R 3 0 R 4 0 R] >>"),
        _objet(2, _flux(b"<< >>", b"0.05 0 0 -0.05 0 841.9 cm")),
        _objet(3, _flux(b"<< >>", b"BT /F1 200 Tf 1 0 0 -1 800 1000 Tm (RELEVE) Tj "
                                  b"1 0 0 -1 3000 1000 Tm")),
        _objet(4, _flux(b"<< >>", b"(DE CARRIERE) Tj 1 0 0 -1 800 1400 Tm "
                                  b"(Detail par annee) Tj ET")),
    )
    assert lignes_pdf(pdf) == ["RELEVE DE CARRIERE", "Detail par annee"], lignes_pdf(pdf)



def test_un_tableau_de_flux_range_a_part_garde_les_polices_de_sa_page():
    """``/Contents 6 0 R``, où l'objet 6 n'est qu'un tableau de flux : c'est
    ainsi que le jaune pensions du PLF 2027 pose ses 250 pages. Lu comme un
    flux, ce tableau ne rattachait les polices de la page à aucun des siens,
    qui prenaient celles du document — ici la table de l'autre page, « xy » —,
    et ses flux se lisaient chacun pour soi : la ``Tm`` de l'un ne plaçait plus
    la chaîne de l'autre."""
    def page(numero: int, police: int, contenus: bytes) -> bytes:
        return _objet(numero, b"<< /Type /Page /Resources << /Font << /F1 %d 0 R >> >> "
                              b"/Contents %s >>" % (police, contenus))

    pdf = _document(
        page(1, 4, b"6 0 R"),
        _objet(6, b"[2 0 R 3 0 R]"),
        _objet(2, _flux(b"<< >>", b"BT /F1 10 Tf 1 0 0 1 60 700 Tm")),
        _objet(3, _flux(b"<< >>", b"(\\001\\002) Tj ET")),
        _objet(4, b"<< /Type /Font /Subtype /Type0 /ToUnicode 5 0 R >>"),
        _objet(5, _flux(b"<< >>", _cmap(1, {1: "O", 2: "K"}))),
        page(7, 8, b"9 0 R"),
        _objet(8, b"<< /Type /Font /Subtype /Type0 /ToUnicode 10 0 R >>"),
        _objet(9, _flux(b"<< >>", b"BT /F1 10 Tf 60 650 Td (\\001\\002) Tj ET")),
        _objet(10, _flux(b"<< >>", _cmap(1, {1: "x", 2: "y"}))),
    )
    assert lignes_pdf(pdf) == ["OK", "xy"], lignes_pdf(pdf)


def test_une_ligne_aux_cellules_decalees_se_relit_de_gauche_a_droite():
    """Trois cellules d'une même ligne, centrées chacune dans sa case : 700,5,
    700 et 699,6 d'ordonnée. Le tri de haut en bas les rend dans l'ordre des
    hauteurs, « B A C » ; ``par_abscisse`` les relit de gauche à droite, comme
    il faut le tableau 50 du jaune pensions du PLF 2027. Sans l'option, rien
    ne change pour les lecteurs écrits avant elle."""
    from lecture_pdf import lignes_par_page

    contenu = (b"BT /F1 10 Tf 120 700.5 Td (B) Tj ET "
               b"BT /F1 10 Tf 60 700 Td (A) Tj ET "
               b"BT /F1 10 Tf 180 699.6 Td (C) Tj ET "
               b"BT /F1 10 Tf 60 680 Td (SUIVANTE) Tj ET")
    pdf = _document(_objet(1, _flux(b"<< >>", contenu)))
    assert lignes_par_page(pdf) == [["B A C", "SUIVANTE"]], lignes_par_page(pdf)
    assert lignes_par_page(pdf, par_abscisse=True) == [["A B C", "SUIVANTE"]], (
        lignes_par_page(pdf, par_abscisse=True))


def test_les_fragments_d_une_ligne_gardent_leur_abscisse():
    """Une case vide ne laisse rien dans le texte d'une ligne : « 1 3 » ne dit
    pas que la case du milieu manque. Les fragments le disent, chacun à son
    abscisse ; leur texte, joint par :func:`texte_de_ligne`, est celui que
    ``lignes_par_page`` rend, aux mêmes rangs."""
    from lecture_pdf import fragments_par_page, lignes_par_page, texte_de_ligne

    contenu = (b"BT /F1 10 Tf 60 700 Td (Ligne) Tj ET "
               b"BT /F1 10 Tf 120 700.5 Td (1) Tj ET "
               b"BT /F1 10 Tf 240 699.6 Td (3) Tj ET "
               b"BT /F1 10 Tf 60 680 Td (SUIVANTE) Tj ET")
    pdf = _document(_objet(1, _flux(b"<< >>", contenu)))
    pages = fragments_par_page(pdf)
    assert [[[(round(x), texte) for x, texte in ligne] for ligne in page] for page in pages] == [
        [[(60, "Ligne"), (120, "1"), (240, "3")], [(60, "SUIVANTE")]]]
    assert [[texte_de_ligne(ligne) for ligne in page] for page in pages] == (
        lignes_par_page(pdf, par_abscisse=True)) == [["Ligne 1 3", "SUIVANTE"]]


def test_un_flux_comprime_qui_finit_par_un_retour_a_la_ligne_se_lit():
    """Les données compressées peuvent finir par l'octet du retour à la ligne :
    ôté avec la fin de ligne qui précède ``endstream``, il tronquait le flux,
    zlib le refusait, et la page disparaissait sans bruit — cinq pages du
    jaune pensions du PLF 2027, dont celle de ses tableaux B-20 et B-21. Le
    premier contenu se compresse justement en finissant par ``\\n``, le second
    par ``\\r`` : ce dernier octet est celui de la somme Adler-32, qui ne dépend
    que du contenu, et un flux sur cent trente environ finit ainsi."""
    for contenu, fin, lue in ((b"BT /F1 10 Tf 60 700 Td (FLUX 1399) Tj ET", b"\n", "FLUX 1399"),
                              (b"BT /F1 10 Tf 60 700 Td (FLUX 1699) Tj ET", b"\r", "FLUX 1699")):
        assert zlib.compress(contenu).endswith(fin)
        pdf = _document(_objet(1, _flux(b"<< >>", contenu, comprimer=True)))
        assert lignes_pdf(pdf) == [lue], lignes_pdf(pdf)


def test_un_flux_comprime_tronque_ne_rend_rien():
    """Un flux dont la fin manque ne rend pas une demi-page : le lecteur le
    tient pour illisible, comme avant."""
    contenu = b"BT /F1 10 Tf 60 700 Td (FLUX 1399) Tj ET"
    tronque = zlib.compress(contenu)[:-6]
    objet = _objet(1, b"<< /Filter /FlateDecode /Length %d >>\nstream\n" % len(tronque)
                   + tronque + b"\nendstream")
    assert lignes_pdf(_document(objet)) == [], lignes_pdf(_document(objet))


def test_un_flux_comprime_suivi_de_beaucoup_d_octets_parasites_se_lit():
    """Ce qui traîne derrière la fin d'un flux comprimé ne compte pas, si long
    soit-il : zlib s'arrête à la somme qui le clôt."""
    contenu = b"BT /F1 10 Tf 60 700 Td (BAVARD) Tj ET"
    donnees = zlib.compress(contenu) + b"\n" + b"x" * 1500
    objet = _objet(1, b"<< /Filter /FlateDecode /Length %d >>\nstream\n" % len(donnees)
                   + donnees + b"\nendstream")
    assert lignes_pdf(_document(objet)) == ["BAVARD"], lignes_pdf(_document(objet))


def _arbre(*pages: bytes) -> list[bytes]:
    """Un catalogue et un arbre de pages, dont les feuilles sont rangées à
    rebours des numéros de leurs objets : 10 + rang de la dernière à la
    première."""
    numeros = [10 + rang for rang in range(len(pages))][::-1]
    enfants = b" ".join(b"%d 0 R" % n for n in numeros)
    return [_objet(1, b"<< /Type /Catalog /Pages 2 0 R >>"),
            _objet(2, b"<< /Type /Pages /Kids [%s] /Count %d >>" % (enfants, len(pages))),
            *(_objet(n, page) for n, page in zip(numeros, pages))]


def test_les_rectangles_d_une_page_se_lisent_en_points_de_la_feuille():
    """La page se trouve par l'arbre des pages, non par le rang de ses flux ;
    son ``/Contents`` désigne un objet qui n'est qu'un tableau de flux, et le
    premier réduit la feuille de moitié, comme celui du jaune la réduit à
    99,88 %. Un rectangle posé par ``re``, un chemin fermé de quatre coins
    sous un motif, un filet tracé se rendent avec leur peinture ; une courbe
    n'est pas un rectangle, une découpe ne peint rien, et ce que ``q`` et
    ``Q`` enferment ne déborde pas."""
    trace = (b"0.2 0.4 0.6 rg 10 20 30 40 re f "
             b"q /Pattern cs /P1 scn 100 0 m 120 0 l 120 10 l 100 10 l h f Q "
             b"0 0 m 10 10 20 0 30 0 c f 0 0 500 500 re W n "
             b"0.5 G 50 0 m 50 100 l S 1 1 2 2 re f")
    pdf = _document(
        *_arbre(b"<< /Type /Page /Contents 3 0 R >>", b"<< /Type /Page /Contents 4 0 R >>"),
        _objet(3, _flux(b"<< >>", b"BT /F1 12 Tf 10 10 Td (0 0 5 5 re f) Tj ET")),
        _objet(4, b"[5 0 R 6 0 R 7 0 R]"),
        _objet(5, _flux(b"<< >>", b"q 0.5 0 0 0.5 0 0 cm")),
        _objet(6, _flux(b"<< >>", trace, comprimer=True)),
        _objet(7, _flux(b"<< >>", b"Q 1 1 2 2 re f")),
    )
    assert aplats_de_page(pdf, 1) == []
    assert aplats_de_page(pdf, 2) == [
        Aplat(("rgb", 0.2, 0.4, 0.6), 5.0, 10.0, 20.0, 30.0),
        Aplat(("motif", "P1"), 50.0, 0.0, 60.0, 5.0),
        Aplat(("rgb", 0.5, 0.5, 0.5), 25.0, 0.0, 25.0, 50.0, trait=True),
        Aplat(("rgb", 0.2, 0.4, 0.6), 0.5, 0.5, 1.5, 1.5),
        Aplat(("rgb", 0.0, 0.0, 0.0), 1.0, 1.0, 3.0, 3.0),
    ]
    try:
        aplats_de_page(pdf, 3)
    except LookupError:
        pass
    else:
        raise AssertionError("une page qui n'existe pas se lit")

