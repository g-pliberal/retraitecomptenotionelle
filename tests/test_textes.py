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


def test_le_controle_suit_une_liste_copiee(tmp_path):
    """Le contrôle ne lit que les fichiers de la liste : une copie le rejoue."""
    shutil.copytree(textes.TEXTES, tmp_path, dirs_exist_ok=True)
    assert textes.controler(tmp_path) == []
