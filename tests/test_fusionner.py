"""Les deux pilotes de fusion de ``scripts/fusionner.py`` (action 148, étape 3).

``pousser.sh`` les déclare à git le temps de son rebasage : la prose dont
seuls divergent les chiffres ancrés et les blocs produits, que GitHub refait,
garde la valeur de ``main`` ; la référence de la conservation se fusionne par
ensembles. Ce qui s'écrit à la main reste un conflit. Les cas de
``test_pousser.py`` les jouent dans un vrai rebasage ; ceux-ci, sur trois
versions écrites pour l'occasion.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import fusionner  # noqa: E402
import verifier_prose  # noqa: E402


def ancre(valeur: str, sonde: str = "poids(moteur/donnees.json)") -> str:
    return f"<!--chiffre:{sonde}-->{valeur}<!--/-->"


def prose(paquet: str, phrase: str = "Le paquet pèse", tests: str = "3 546") -> str:
    return (f"# Titre\n\n{phrase} {ancre(paquet)} Ko.\n\n"
            f"Il y a {ancre(tests, 'tests()')} tests.\n\nUne autre phrase.\n")


# -- la prose -------------------------------------------------------------------


def test_deux_valeurs_d_une_meme_ancre_gardent_celle_de_main():
    """Deux sessions changent le modèle et récrivent la même ancre : git
    déclarait le conflit ; le pilote garde la valeur de main."""
    base, main, session = prose("100"), prose("110"), prose("120")
    assert not fusionner.fusion_de_texte(main, base, session)[0], "git bute"
    propre, resultat = fusionner.fusionner_prose(base, main, session)
    assert propre
    assert resultat == main


def test_la_prose_d_un_cote_et_l_ancre_de_l_autre_se_fusionnent():
    """Main récrit la phrase, la session la valeur de son ancre : les deux
    restent, la phrase de main et la valeur de la session."""
    base = prose("100")
    main = prose("100", phrase="Le paquet du site pèse")
    session = prose("120", tests="3 600")
    propre, resultat = fusionner.fusionner_prose(base, main, session)
    assert propre
    assert resultat == prose("120", phrase="Le paquet du site pèse", tests="3 600")


def test_un_conflit_de_prose_reste_un_conflit():
    base = prose("100")
    main = prose("110", phrase="Le paquet du site pèse")
    session = prose("120", phrase="Le paquet compressé pèse")
    propre, resultat = fusionner.fusionner_prose(base, main, session)
    assert not propre
    assert "<<<<<<< main" in resultat and ">>>>>>> session" in resultat


def test_une_ancre_ecrite_a_la_main_reste_un_conflit():
    """``illustration``, ``tenu`` et ``a_verifier`` ne recalculent rien : leur
    chiffre s'écrit à la main, et deux mains qui divergent sont un conflit."""
    def texte(valeur: str) -> str:
        return f"Un exemple : {ancre(valeur, 'illustration()')} %.\n"
    assert not fusionner.fusionner_prose(texte("12,5"), texte("13"), texte("12"))[0]


def test_une_forme_qui_change_est_ecrite_a_la_main():
    """``--corriger`` garde les décimales et le signe typographique d'un
    chiffre ; une session qui les change écrit à la main."""
    base, main, session = prose("100"), prose("110"), prose("100,5")
    assert not fusionner.fusionner_prose(base, main, session)[0]
    assert fusionner.forme("+7,96") == fusionner.forme("−1,13")
    assert fusionner.forme("1 228") == fusionner.forme("98")
    assert fusionner.forme("79,5") != fusionner.forme("79,54")


def test_une_ancre_citee_dans_un_bloc_de_code_est_du_texte():
    def texte(valeur: str) -> str:
        return f"La forme :\n\n```\n{ancre(valeur)}\n```\n"
    assert not fusionner.fusionner_prose(texte("1"), texte("2"), texte("3"))[0]


def test_un_bloc_produit_garde_la_version_de_main():
    def texte(lignes: str, titre: str = "Le tableau") -> str:
        return (f"## {titre}\n\n<!-- annuel:debut -->\n| Année | Coût |\n|---|---:|\n"
                f"{lignes}<!-- annuel:fin -->\n\nLa suite.\n")
    base = texte("| 2026 | 8,50 |\n")
    main = texte("| 2026 | 8,49 |\n| 2027 | 8,60 |\n")
    session = texte("| 2026 | 8,51 |\n", titre="Le tableau annuel")
    propre, resultat = fusionner.fusionner_prose(base, main, session)
    assert propre
    assert resultat == texte("| 2026 | 8,49 |\n| 2027 | 8,60 |\n", titre="Le tableau annuel")


def test_une_ancre_ajoutee_garde_sa_valeur():
    """Ce qu'un seul côté ajoute n'a pas d'autre valeur que la sienne."""
    base = prose("100")
    main = prose("110")
    session = prose("120") + f"Et {ancre('7', 'lignes(README.md)')} lignes.\n"
    propre, resultat = fusionner.fusionner_prose(base, main, session)
    assert propre
    assert resultat == prose("110") + f"Et {ancre('7', 'lignes(README.md)')} lignes.\n"


def test_le_pilote_lit_l_ancre_comme_verifier_prose():
    """Le pilote ne lit que la bibliothèque standard : ses motifs et ses sondes
    écrites à la main sont recopiés de ``verifier_prose.py``, et ne doivent
    pas s'en écarter."""
    assert fusionner.ANCRE.pattern == verifier_prose.ANCRE.pattern
    nombres = "4 251, 79,5, −28, 2874, 11 975,57, 1\u00a0569, 1\u202f569, +7,96, -3"
    assert (re.findall(fusionner.NOMBRE, nombres)
            == re.findall(verifier_prose._NOMBRE, nombres))
    assert fusionner.A_LA_MAIN <= set(verifier_prose.SONDES)
    assert verifier_prose.sonde_illustration() is None
    assert verifier_prose.sonde_a_verifier("une dette que l'on avoue") is None
    assert verifier_prose.sonde_tenu("test_le_pilote_lit_l_ancre_comme_verifier_prose") is None


# -- la référence de la conservation ----------------------------------------------


def reference(entrees: list[str], paragraphes: list[str]) -> str:
    """Une référence, écrite comme ``conservation.py --figer`` l'écrit."""
    texte = json.dumps(
        {"entrees": {"veille.yaml:journal": entrees},
         "paragraphes": {"docs/parcours.md": {"Le parcours": paragraphes}}},
        ensure_ascii=False, indent=1, sort_keys=True)
    return texte + "\n"


def test_deux_refigements_du_meme_jour_se_fusionnent_par_ensembles():
    """Deux sessions refigent le même jour : chacune ajoute son entrée du
    journal au même endroit de la liste triée, et récrit un paragraphe du
    parcours, dont les empreintes suivent l'ordre du texte. Tout reste, rien
    de retiré ne revient, et l'ordre du texte se garde."""
    base = reference(["2026-10-05 | a", "2026-10-06 | b", "2026-10-06 | c"],
                     ["f3", "a1", "c2"])
    main = reference(["2026-10-05 | a", "2026-10-06 | b", "2026-10-06 | c",
                      "2026-10-06 | d"], ["f3", "b9", "c2"])
    session = reference(["2026-10-05 | a", "2026-10-06 | b", "2026-10-06 | c",
                         "2026-10-06 | e"], ["f3", "a1", "c2", "e4"])
    assert not fusionner.fusion_de_texte(main, base, session)[0], "git bute"
    propre, resultat = fusionner.fusionner_ensembles(base, main, session)
    assert propre
    assert resultat == reference(
        ["2026-10-05 | a", "2026-10-06 | b", "2026-10-06 | c", "2026-10-06 | d",
         "2026-10-06 | e"], ["f3", "b9", "c2", "e4"])


def test_un_meme_ajout_des_deux_cotes_compte_une_fois():
    base = reference(["a"], ["p1"])
    main = reference(["a", "b"], ["p1", "p2"])
    session = reference(["a", "b", "c"], ["p1", "p2"])
    propre, resultat = fusionner.fusionner_ensembles(base, main, session)
    assert propre
    assert resultat == reference(["a", "b", "c"], ["p1", "p2"])


def test_une_section_retiree_d_un_cote_ne_revient_pas():
    base = json.dumps({"paragraphes": {"d": {"s": ["x"], "t": ["y"]}}})
    main = json.dumps({"paragraphes": {"d": {"t": ["y", "z"]}}})
    session = json.dumps({"paragraphes": {"d": {"s": ["x"], "t": ["y"], "u": ["w"]}}})
    propre, resultat = fusionner.fusionner_ensembles(base, main, session)
    assert propre
    assert json.loads(resultat) == {"paragraphes": {"d": {"t": ["y", "z"], "u": ["w"]}}}


def test_une_reference_illisible_reste_un_conflit():
    """Ce qui n'est pas du JSON se fusionne comme du texte, conflit compris."""
    base = reference(["a"], ["p1"])
    main = reference(["a", "b"], ["p1"])
    session = reference(["a", "c"], ["p1"]).replace('"c"', '"c",,')
    propre, resultat = fusionner.fusionner_ensembles(base, main, session)
    assert not propre
    assert "<<<<<<< main" in resultat


# -- le pilote, tel que git l'appelle ----------------------------------------------


def test_le_pilote_ecrit_dans_le_fichier_courant_et_dit_s_il_a_fusionne(tmp_path):
    chemins = {}
    for nom, texte in (("base", prose("100")), ("courant", prose("110")),
                       ("autre", prose("120"))):
        chemins[nom] = tmp_path / nom
        chemins[nom].write_bytes(texte.encode("utf-8"))
    arguments = ["ancres", *(str(chemins[n]) for n in ("base", "courant", "autre")), "7"]
    assert fusionner.main(arguments) == 0
    assert chemins["courant"].read_bytes().decode("utf-8") == prose("110")

    chemins["courant"].write_bytes(prose("110", phrase="Main dit").encode("utf-8"))
    chemins["autre"].write_bytes(prose("120", phrase="La session dit").encode("utf-8"))
    assert fusionner.main(arguments) == 1
    assert "<<<<<<<" in chemins["courant"].read_bytes().decode("utf-8")
    assert fusionner.main(["inconnu", "a", "b", "c"]) == 2
