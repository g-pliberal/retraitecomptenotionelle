"""Ce que la régénération a déjà fabriqué (``retraite_notionnelle/fabrique.py``) :
une étape inchangée ne se refait pas, et le moindre changement de ce qu'elle lit
ou écrit la fait refaire."""

from __future__ import annotations

import re

from retraite_notionnelle import fabrique
from retraite_notionnelle.config import RACINE_PROJET


def test_un_extrait_de_pages_js_ne_retient_que_sa_declaration():
    texte = ('const A = 1;\nexport const SCENARIOS_MONTRES = [\n  "actuel",\n];\n'
             "function page() {}\n")
    motif = fabrique.EXTRAITS["paquet"][0][1]
    assert fabrique.extrait(texte, motif) == fabrique.extrait(
        texte.replace("function page() {}", "function page() { return 2; }"), motif)
    assert fabrique.extrait(texte, motif) != fabrique.extrait(
        texte.replace('"actuel"', '"notionnel_liberal"'), motif)
    assert fabrique.extrait("sans motif", motif) == "sans motif"


def test_le_paquet_suit_tout_ce_que_la_fabrique_lit_de_pages_js():
    """La fabrique lit de ``pages.js`` les systèmes montrés et ceux du bilan,
    le classement comparé, l'écart de taux de la dette, les années des
    variantes d'espérance de vie, et la saisie des carrières d'exemple du
    bilan figé, que le portage simule (action 161, étape 5) : chaque
    déclaration qu'elle lit, et chaque constante qu'une fonction lue nomme,
    entre dans l'empreinte du paquet, retrouvée dans la page du jour."""
    texte = (RACINE_PROJET / "moteur/js/pages.js").read_text(encoding="utf-8")
    extraits = [fabrique.extrait(texte, motif) for chemin, motif in fabrique.EXTRAITS["paquet"]
                if chemin == "moteur/js/pages.js"]
    assert extraits and texte not in extraits, "un motif ne se retrouve plus dans pages.js"
    declarees = {re.match(r"export (?:const|function) (\w+)", extrait).group(1)
                 for extrait in extraits}
    source = (RACINE_PROJET / "scripts/construire_donnees.py").read_text(encoding="utf-8")
    lues = set(re.findall(r"\bpages\.([A-Za-z_]\w*)", source)) - {"js"}
    assert lues
    for nom in lues:
        # Le site nomme ses fonctions à la manière du JavaScript.
        declaree = nom if nom.isupper() else re.sub(r"_(\w)", lambda m: m[1].upper(), nom)
        assert declaree in declarees, f"pages.{nom} n'entre pas dans l'empreinte du paquet"
    for extrait in extraits:
        if extrait.startswith("export function"):
            for constante in re.findall(r"\b[A-Z][A-Z0-9_]+\b", extrait):
                assert constante in declarees, constante


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
