"""Ce que la régénération a déjà fabriqué (``retraite_notionnelle/fabrique.py``) :
une étape inchangée ne se refait pas, et le moindre changement de ce qu'elle lit
ou écrit la fait refaire."""

from __future__ import annotations

from retraite_notionnelle import fabrique


def test_le_paquet_ne_lit_de_pages_js_que_les_systemes_montres():
    texte = ('const A = 1;\nexport const SCENARIOS_MONTRES = [\n  "actuel",\n];\n'
             "function page() {}\n")
    motif = fabrique.EXTRAITS["paquet"][0][1]
    assert fabrique.extrait(texte, motif) == fabrique.extrait(
        texte.replace("function page() {}", "function page() { return 2; }"), motif)
    assert fabrique.extrait(texte, motif) != fabrique.extrait(
        texte.replace('"actuel"', '"notionnel_liberal"'), motif)
    assert fabrique.extrait("sans motif", motif) == "sans motif"


def test_le_paquet_suit_le_moteur_du_portage_mais_pas_le_texte_des_pages():
    """La table des agrégats se calcule par le portage (action 161, étape 5) :
    une retouche du moteur JavaScript refait le paquet, une retouche du texte
    des pages non, qui n'en donne que la liste des systèmes montrés."""
    lus = fabrique.fichiers("paquet")
    assert {"moteur/js/simulateur.js", "moteur/js/mortalite.js", "moteur/js/libm.js",
            "moteur/js/droit/liquider.js", "src/retraite_notionnelle/pont.mjs"} <= lus
    assert "moteur/js/pages.js" not in lus


def test_une_etape_retenue_est_a_jour_tant_que_rien_ne_bouge(monkeypatch, tmp_path):
    monkeypatch.setattr(fabrique, "FICHIER", tmp_path / "fabrique.json")
    empreintes = {"paquet": "a"}
    monkeypatch.setattr(fabrique, "empreinte", lambda etape: empreintes[etape])
    monkeypatch.delenv(fabrique.SANS_MEMOIRE, raising=False)
    assert not fabrique.a_jour("paquet")
    fabrique.retenir("paquet")
    assert fabrique.a_jour("paquet")
    empreintes["paquet"] = "b"
    assert not fabrique.a_jour("paquet")
    monkeypatch.setenv(fabrique.SANS_MEMOIRE, "1")
    empreintes["paquet"] = "a"
    assert not fabrique.a_jour("paquet")
