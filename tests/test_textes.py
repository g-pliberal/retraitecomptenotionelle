"""La liste de contrôle des textes : ``data/reference/textes/``.

``docs/architecture.md``, § 6.6. Chaque rédaction d'un article qui touche les
retraites est rattachée à une version de fiche, déclarée sans effet, à
rattacher ou à examiner ; le cliquet compte celles qui n'ont aucun statut, et
ne peut que décroître. Le statut se lit dans les fiches : ce test le fait lire
sur une liste et des fiches de poche, puis tient la liste du dépôt et son
cliquet.
"""

from __future__ import annotations

import shutil
from datetime import date

import pytest
import yaml

from retraite_notionnelle.noyau import textes

A, B, C, D, E, F, G = (f"LEGIARTI{n:012d}" for n in range(1, 8))


@pytest.fixture
def liste(tmp_path):
    """Sept rédactions de poche, dont une inscrite par le script."""
    (tmp_path / "textes.csv").write_text("texte,titre\ncss,Code de la sécurité sociale\n",
                                         encoding="utf-8")
    lignes = ["id,texte,article,debut,fin,inscrite_le"]
    for ident in (A, B, C, D, E, F, G):
        lignes.append(f"{ident},css,L351-1,1985-01-01,,"
                      + ("2026-09-26" if ident == F else ""))
    (tmp_path / "redactions.csv").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    (tmp_path / "perimetre.yaml").write_text(
        yaml.safe_dump({"codes": [], "cliquet": {"redactions_sans_statut": 1}}),
        encoding="utf-8")
    return tmp_path


FICHES = {
    "regle": {
        "versions": [{"id": "v1", "textes": [{"id": A}]}],
        "textes_sans_effet": [{"id": B, "motif": "renvoi d'alinéa"}],
        "textes_a_rattacher": [{"reference": f"L. 351-1, version de 1985 ({C})"}],
        "sources": {"lectures": [{"type": "legifrance", "reference": f"L. 351-1, {D}",
                                  "date": "2026-09-26"}]},
        "textes_a_relire": [{"id": E, "question": "change-t-il le droit ?"}],
    },
}


def test_le_statut_se_lit_dans_les_fiches(liste):
    """Une version qui la cite : rattachée ; déclarée sans effet ; nommée dans
    un texte à rattacher ou dans une lecture : à rattacher ; à relire, ou
    inscrite par le script : à examiner ; sinon, rien."""
    assert textes.statuts(liste, FICHES) == {
        A: "rattachee", B: "sans_effet", C: "a_rattacher", D: "a_rattacher",
        E: "a_examiner", F: "a_examiner", G: None}
    assert textes.controler(liste, FICHES) == []


def test_deux_fiches_donnent_le_statut_le_plus_etabli(liste):
    fiches = {**FICHES, "autre": {"textes_a_rattacher": [{"id": A}], "textes_sans_effet": [{"id": G}]}}
    statuts = textes.statuts(liste, fiches)
    assert statuts[A] == "rattachee" and statuts[G] == "sans_effet"


def test_le_cliquet_ne_monte_pas(liste):
    """Une rédaction qui perd son statut fait monter le compte : le contrôle
    le refuse. Une rédaction qui en gagne un le fait baisser : le cliquet doit
    suivre."""
    sans_lecture = {"regle": {**FICHES["regle"], "sources": {}}}
    erreurs = textes.controler(liste, sans_lecture)
    assert any("2 rédactions sans statut, le cliquet en admet 1" in e for e in erreurs), erreurs
    tout = {**FICHES, "autre": {"textes_sans_effet": [{"id": G}]}}
    erreurs = textes.controler(liste, tout)
    assert any("l'abaisser à 0" in e for e in erreurs), erreurs


def test_la_liste_refuse_ce_qui_n_est_pas_une_redaction(liste):
    with (liste / "redactions.csv").open("a", encoding="utf-8") as flux:
        flux.write(f"{A},css,L351-1,1985-01-01,,\n")
        flux.write("JORFTEXT000000000001,inconnu,1,hier,,\n")
    erreurs = textes.controler(liste, FICHES)
    assert any(f"{A} deux fois" in e for e in erreurs), erreurs
    assert any("n'est pas un identifiant de rédaction" in e for e in erreurs), erreurs
    assert any("« inconnu » absent de textes.csv" in e for e in erreurs), erreurs
    assert any("« hier » n'est pas une date" in e for e in erreurs), erreurs


H, I = (f"LEGIARTI{n:012d}" for n in range(8, 10))


@pytest.fixture
def histoire(tmp_path):
    """L'histoire de poche de trois articles (action 184, étape 2) : L. 351-1
    en quatre rédactions, dont une à venir ; une annexe dont deux articles
    distincts portent le même numéro, en vigueur ensemble ; deux articles sans
    numéro ; L. 351-2, qu'aucune fiche ne cite."""
    (tmp_path / "textes.csv").write_text("texte,titre\ncss,Code de la sécurité sociale\n",
                                         encoding="utf-8")
    lignes = ["id,texte,article,debut,fin,inscrite_le",
              f"{A},css,L351-1,1985-01-01,2004-01-01,",
              f"{B},css,L351-1,2004-01-01,2023-09-01,",
              f"{C},css,L351-1,2023-09-01,2027-01-01,2026-09-26",
              f"{I},css,L351-1,2027-01-01,,2026-09-26",
              f"{D},css,L351-2,1985-01-01,,",
              f"{E},css,Annexe,1985-01-01,,",
              f"{F},css,Annexe,1985-01-01,,",
              f"{G},css,,1985-01-01,,",
              f"{H},css,,1990-01-01,,"]
    (tmp_path / "redactions.csv").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    (tmp_path / "perimetre.yaml").write_text(
        yaml.safe_dump({"codes": [], "cliquet": {"redactions_sans_statut": 0}}),
        encoding="utf-8")
    return tmp_path


LECTRICE = {"regle": {"versions": [{"id": "v1", "textes": [{"id": A}, {"id": E}, {"id": G}]}]}}


def test_une_fiche_voit_les_redactions_des_articles_qu_elle_cite_et_n_a_pas_lues(histoire):
    """Une fiche qui cite une rédaction d'un article voit les autres
    rédactions de cet article qui n'ont pas de statut final : en vigueur ou à
    venir d'abord, puis de la plus récente à la plus ancienne. Un article
    qu'elle ne cite pas n'y est pas, ni un article sans numéro, que rien ne
    distingue d'un autre ; deux rédactions du même numéro en vigueur ensemble
    sont deux articles, que l'on signale."""
    vue = textes.non_lues(histoire, LECTRICE, date(2026, 11, 3))
    assert list(vue) == ["regle"]
    assert [(r["id"], r["vivante"], r["homonyme"], r["statut"]) for r in vue["regle"]] == [
        (I, True, False, "a_examiner"), (C, True, False, "a_examiner"),
        (F, True, True, None), (B, False, False, None)]


def test_une_redaction_lue_sort_de_la_vue(histoire):
    """Rattachée ou déclarée sans effet par une autre fiche, une rédaction a
    son statut final ; nommée par la fiche elle-même, à relire ou à rattacher,
    elle est lue. Nommée à rattacher par une autre fiche seulement, elle reste
    à lire."""
    fiches = {"regle": {**LECTRICE["regle"], "textes_a_relire": [{"id": I}]},
              "autre": {"versions": [{"id": "v1", "textes": [{"id": B}]}],
                        "textes_a_rattacher": [{"id": C}]}}
    vue = textes.non_lues(histoire, fiches, date(2026, 11, 3))
    assert [(r["id"], r["statut"]) for r in vue["regle"]] == [(C, "a_rattacher"), (F, None)]
    assert [r["id"] for r in vue["autre"]] == [I], "la rédaction à venir, que regle seule nomme"


def test_la_liste_du_depot_tient_et_son_cliquet_est_juste():
    """Les rédactions du périmètre, chacune une fois, datées, sous un texte
    connu ; et autant de rédactions sans statut que le cliquet en admet."""
    assert textes.controler() == []


def test_le_perimetre_est_declare():
    """Chaque code dit pourquoi il est là ; ceux qu'on ne prend pas en entier
    disent quels articles, par un motif qui se compile."""
    import re

    perimetre = textes.perimetre()
    assert perimetre["codes"]
    cles = [code["cle"] for code in perimetre["codes"]]
    assert len(cles) == len(set(cles))
    for code in perimetre["codes"]:
        assert len(str(code["pourquoi"]).split()) >= 3, code["cle"]
        if code.get("articles"):
            re.compile(code["articles"])
    assert set(cles) <= set(textes.titres())


def test_les_textes_generaux_de_la_fonction_publique_sont_declares():
    """Le propriétaire l'a tranché le 11 novembre 2026 : les trois lois
    statutaires de la fonction publique et le décret des rémunérations
    n'entrent que par les articles qu'une fiche cite. Chacun est déclaré sous
    le titre que l'index lui donne, et dit pourquoi."""
    generaux = textes.perimetre()["textes_generaux"]
    titres = [texte["titre"] for texte in generaux]
    assert len(titres) == len(set(titres))
    for numero in ("Loi n° 84-16 du 11 janvier 1984", "Loi n° 84-53 du 26 janvier 1984",
                   "Loi n° 86-33 du 9 janvier 1986", "Décret n° 85-1148 du 24 octobre 1985"):
        assert [t for t in titres if t.startswith(numero + " ")], numero
    codes = {code["titre"] for code in textes.perimetre()["codes"]}
    for texte in generaux:
        assert len(str(texte["pourquoi"]).split()) >= 3, texte["titre"]
        assert texte["titre"] not in codes, texte["titre"]


def test_le_controle_suit_une_liste_copiee(tmp_path):
    """Le contrôle ne lit que les fichiers de la liste : une copie le rejoue."""
    shutil.copytree(textes.TEXTES, tmp_path, dirs_exist_ok=True)
    assert textes.controler(tmp_path) == []


def test_deux_textes_du_meme_jour_ne_partagent_pas_une_cle():
    """Le 10 juillet 2026, un arrêté par section libérale approuve ses
    règlements : tous ont la clé datée ``arrete_2026_07_10``. Le texte déjà
    inscrit garde la sienne ; un texte nouveau prend le sigle qui finit son
    titre, ou un rang, et jamais la clé d'un autre."""
    import importlib.util
    import sqlite3
    from pathlib import Path

    chemin = Path(__file__).resolve().parents[1] / "scripts" / "textes.py"
    spec = importlib.util.spec_from_file_location("script_textes", chemin)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)

    cavec = "Arrêté du 10 juillet 2026 portant approbation des règlements (CAVEC)"
    carmf = "Arrêté du 10 juillet 2026 portant approbation des règlements (CARMF)"
    carpimko = "Arrêté du 10 juillet 2026 portant approbation des règlements (CARPIMKO)"
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE doc (id TEXT, titre TEXT, num TEXT, date TEXT, fin TEXT)")
    db.executemany("INSERT INTO doc VALUES (?, ?, ?, ?, ?)", [
        (A, cavec, "2", "2026-07-11", "2999-01-01"),
        (B, carmf, "2", "2026-07-11", "2999-01-01"),
        (C, carpimko, "5", "2026-07-11", "2999-01-01"),
    ])
    fiches = {"f": {"textes_a_rattacher": [{"reference": f"{A}, {B} et {C}"}]}}
    lignes, titres = script.selection(db, {"codes": [], "textes_cites": True}, fiches,
                                      {"arrete_2026_07_10": cavec})
    assert titres == {"arrete_2026_07_10": cavec, "arrete_2026_07_10_carmf": carmf,
                      "arrete_2026_07_10_carpimko": carpimko}
    assert {ident: ligne["texte"] for ident, ligne in lignes.items()} == {
        A: "arrete_2026_07_10", B: "arrete_2026_07_10_carmf",
        C: "arrete_2026_07_10_carpimko"}
    assert script.cle_libre("arrete_2026_07_10", "Arrêté du 10 juillet 2026 (CARMF)",
                            {**titres, "arrete_2026_07_10_carmf": carmf}) == \
        "arrete_2026_07_10_carmf_2"
    assert script.cle_libre("arrete_2026_07_10", "Arrêté du 10 juillet 2026 sans sigle",
                            titres) == "arrete_2026_07_10_2"


def test_un_texte_general_n_entre_que_par_ses_articles_cites():
    """Un décret de régime dont une fiche cite un article entre en entier. Un
    texte général déclaré au périmètre — le statut de la fonction publique de
    l'État, dont trois articles sur cent touchent les retraites — n'apporte
    que l'article cité, avec toutes ses rédactions, comme un code hors de ses
    chapitres (action 184, étape 4)."""
    import sqlite3

    script = _script()
    regime = "Décret n° 2003-1306 du 26 décembre 2003 relatif au régime de retraite des fonctionnaires affiliés à la CNRACL"
    general = "Loi n° 84-16 du 11 janvier 1984 portant dispositions statutaires relatives à la fonction publique de l'Etat (1)."
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE doc (id TEXT, titre TEXT, num TEXT, date TEXT, fin TEXT)")
    db.executemany("INSERT INTO doc VALUES (?, ?, ?, ?, ?)", [
        (A, regime, "1", "2004-01-01", "2999-01-01"),
        (B, regime, "2", "2004-01-01", "2999-01-01"),
        (C, general, "68", "1984-01-12", "2011-07-01"),
        (D, general, "68", "2011-07-01", "2999-01-01"),
        (E, general, "34", "1984-01-12", "2999-01-01"),
    ])
    fiches = {"f": {"versions": [{"id": "v1", "textes": [{"id": A}, {"id": D}]}]}}
    perimetre = {"codes": [], "textes_cites": True,
                 "textes_generaux": [{"titre": general, "pourquoi": "le statut entier"}]}
    lignes, titres = script.selection(db, perimetre, fiches)
    assert titres == {"decret_2003_1306": regime, "loi_84_16": general}
    assert {ident: (ligne["texte"], ligne["article"]) for ident, ligne in lignes.items()} == {
        A: ("decret_2003_1306", "1"), B: ("decret_2003_1306", "2"),
        C: ("loi_84_16", "68"), D: ("loi_84_16", "68")}
    sans = {"codes": [], "textes_cites": True}
    assert set(script.selection(db, sans, fiches)[0]) == {A, B, C, D, E}, \
        "non déclaré, le même texte entre en entier"


def test_le_mot_a_mot_d_une_redaction_non_lue():
    """Ce qu'une rédaction change à la dernière version qui a été en vigueur
    du même article, dans l'index ; une version mort-née ne compte pas ; une
    rédaction identique se propose sans effet, la fiche la déclare."""
    import importlib.util
    import sqlite3
    from pathlib import Path

    chemin = Path(__file__).resolve().parents[1] / "scripts" / "textes.py"
    spec = importlib.util.spec_from_file_location("script_textes", chemin)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)

    titre = "Code de la sécurité sociale"
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE doc (id TEXT, date TEXT, fin TEXT, nature TEXT, num TEXT, "
               "titre TEXT, texte TEXT)")
    db.executemany("INSERT INTO doc VALUES (?, ?, ?, 'Article CODE', 'L351-1', ?, ?)", [
        (A, "1985-01-01", "2004-01-01", titre, "La pension est due à 60 ans."),
        (B, "2004-01-01", "2010-01-01", titre, "La pension est due à 62 ans."),
        (C, "2010-01-01", "2010-01-01", titre, "La pension est due à 63 ans."),
        (D, "2010-01-01", "2999-01-01", titre, "La pension est due à 62 ans."),
    ])
    assert script.mot_a_mot(db, titre, "L351-1", A) == "(première version)"
    assert script.mot_a_mot(db, titre, "L351-1", B) == "La pension est due à [-60-]{+62+} ans."
    assert script.mot_a_mot(db, titre, "L351-1", D).startswith("(texte inchangé)")
    assert "textes_sans_effet" in script.mot_a_mot(db, titre, "L351-1", D)
    assert script.mot_a_mot(db, titre, "L351-1", E) == "(absente de l'index)"


def _script():
    """`scripts/textes.py`, chargé comme un module."""
    import importlib.util
    from pathlib import Path

    chemin = Path(__file__).resolve().parents[1] / "scripts" / "textes.py"
    spec = importlib.util.spec_from_file_location("script_textes", chemin)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    return script


def test_le_detail_d_une_fiche_montre_ses_redactions_en_vigueur_et_compte_les_passees(histoire):
    """Le détail d'une fiche montre ses rédactions non lues en vigueur ou à
    venir, celles que la veille compte ; les passées, il les compte, et ne les
    montre que sur demande : avec leur mot à mot, elles noyaient les autres
    (action 184)."""
    script = _script()
    vue = textes.non_lues(histoire, LECTRICE, date(2026, 11, 3))["regle"]
    entete = "regle : 4 rédactions non lues des articles qu'elle cite, dont 3 en vigueur ou à venir."
    vivantes = [
        f"  css L351-1  2027-01-01 → en vigueur  {I}  [en vigueur ou à venir ; a_examiner]",
        f"  css L351-1  2023-09-01 → 2027-01-01  {C}  [en vigueur ou à venir ; a_examiner]",
        f"  css Annexe  1985-01-01 → en vigueur  {F}  "
        "[en vigueur ou à venir, même numéro qu'un autre article ; sans statut]"]
    assert script.detail("regle", vue, {}) == [
        entete, "", *vivantes, "",
        "1 rédaction passée, non montrée : python scripts/textes.py --non-lues regle --toutes"]
    assert script.detail("regle", vue, {}, toutes=True) == [
        entete, "", *vivantes,
        f"  css L351-1  2004-01-01 → 2023-09-01  {B}  [passée ; sans statut]"]
