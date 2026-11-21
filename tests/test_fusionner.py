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


def test_deux_valeurs_en_lettres_d_une_meme_ancre_gardent_celle_de_main():
    """Le parcours écrit en lettres des chiffres que GitHub récrit (action
    163) : elles se fusionnent comme des chiffres. La demie qui tombe change
    la forme, comme une décimale ; la majuscule aussi, que ``--corriger``
    garde."""
    def texte(valeur: str) -> str:
        return (f"# Titre\n\nLa liste (soit {ancre(valeur, 'entrees(x.yaml:statuts)')}) "
                "les range.\n\nUne autre phrase.\n")
    base, main, session = texte("soixante-deux"), texte("soixante-treize"), texte("dix")
    assert not fusionner.fusion_de_texte(main, base, session)[0], "git bute"
    assert fusionner.fusionner_prose(base, main, session) == (True, main)
    assert fusionner.forme("seize ans et demi") == fusionner.forme("vingt et un ans et demi")
    assert fusionner.forme("seize ans et demi") != fusionner.forme("dix-sept ans")
    assert fusionner.forme("Treize") != fusionner.forme("quatorze")


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
    assert fusionner.LETTRES.pattern == verifier_prose.LETTRES_ANCREES.pattern
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


# -- les témoins, fusionnés entrée par entrée ---------------------------------------


def temoin(entrees: dict) -> str:
    """Un témoin de ``tests/temoins/``, écrit comme ``construire_temoins.py``
    l'écrit."""
    return json.dumps(entrees, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


BASE = {"cas_a": {"pension": [1000.0, 1010.5]}, "cas_b": {"pension": [900.0]},
        "cas_c": {"pension": [800.0]}, "cas_d": {"pension": [700.0]}}


def avec(**changes) -> dict:
    entrees = json.loads(json.dumps(BASE))
    for cle, valeur in changes.items():
        if valeur is None:
            entrees.pop(cle)
        else:
            entrees[cle] = valeur
    return entrees


def test_deux_corrections_sur_deux_cas_voisins_se_fusionnent_entree_par_entree():
    """Deux sessions corrigent deux régimes : chacune déplace son cas, et les
    deux cas se suivent dans le fichier. Marqué ``-merge``, le témoin gardait
    la version de main et perdait la correction de la session ; entrée par
    entrée, les deux corrections restent, sans rien perdre."""
    main = avec(cas_b={"pension": [905.0]})
    session = avec(cas_c={"pension": [812.25]}, cas_e={"pension": [1.0]})
    propre, resultat = fusionner.fusionner_cles(temoin(BASE), temoin(main), temoin(session))
    assert propre
    assert resultat == temoin(avec(cas_b={"pension": [905.0]}, cas_c={"pension": [812.25]},
                                   cas_e={"pension": [1.0]}))


def test_une_meme_entree_changee_des_deux_cotes_reste_un_conflit():
    """Le cas dangereux : deux corrections déplacent le même cas, chacune à sa
    valeur. Aucune des deux n'est la bonne, qui vient de leur réunion : le
    conflit reste, marqué comme git le marque, et rien ne se devine."""
    main = avec(cas_b={"pension": [905.0]})
    session = avec(cas_b={"pension": [910.0]})
    propre, resultat = fusionner.fusionner_cles(temoin(BASE), temoin(main), temoin(session))
    assert not propre
    assert "<<<<<<<" in resultat


def test_une_entree_d_une_liste_ne_se_fusionne_pas_comme_un_ensemble():
    """Une entrée est un tout : deux côtés qui changent deux nombres d'un même
    cas sont en conflit, à la différence de la référence de la conservation."""
    main = avec(cas_a={"pension": [1001.0, 1010.5]})
    session = avec(cas_a={"pension": [1000.0, 1011.0]})
    assert not fusionner.fusionner_cles(temoin(BASE), temoin(main), temoin(session))[0]


def test_un_meme_changement_des_deux_cotes_compte_une_fois():
    main = avec(cas_b={"pension": [905.0]}, cas_d=None)
    session = avec(cas_b={"pension": [905.0]}, cas_d=None)
    assert fusionner.fusionner_cles(temoin(BASE), temoin(main), temoin(session)) == (
        True, temoin(main))


def test_une_entree_retiree_d_un_cote_part_et_retiree_contre_changee_reste_un_conflit():
    main = avec(cas_d=None)
    session = avec(cas_a={"pension": [1.0, 2.0]})
    assert fusionner.fusionner_cles(temoin(BASE), temoin(main), temoin(session)) == (
        True, temoin(avec(cas_d=None, cas_a={"pension": [1.0, 2.0]})))
    session = avec(cas_d={"pension": [701.0]})
    assert not fusionner.fusionner_cles(temoin(BASE), temoin(main), temoin(session))[0]


def test_un_nan_inchange_n_est_pas_un_changement():
    """``json`` lit et écrit ``NaN``, que Python ne dit pas égal à lui-même."""
    base = temoin({"x": {"v": float("nan")}, "y": {"v": 1.0}})
    main = temoin({"x": {"v": float("nan")}, "y": {"v": 2.0}})
    session = temoin({"x": {"v": float("nan")}, "y": {"v": 1.0}, "z": {"v": 3.0}})
    propre, resultat = fusionner.fusionner_cles(base, main, session)
    assert propre
    assert resultat == temoin({"x": {"v": float("nan")}, "y": {"v": 2.0}, "z": {"v": 3.0}})


def test_un_temoin_illisible_reste_un_conflit():
    main = temoin(avec(cas_b={"pension": [905.0]}))
    session = temoin(avec(cas_b={"pension": [910.0]})).replace("910.0", "910.0,,")
    assert not fusionner.fusionner_cles(temoin(BASE), main, session)[0]


def test_les_temoins_par_cas_relevent_de_la_fusion_par_cles():
    """``.gitattributes`` confie au pilote les témoins rangés une entrée par
    cas ; ceux des pages, qui suivent les agrégats, gardent la version de
    main, et le paquet reste à refaire."""
    import subprocess
    sortie = subprocess.run(
        ["git", "check-attr", "merge", "--",
         *(f"tests/temoins/{nom}.json" for nom in
           ("simulations", "sorties", "droit", "servis", "valeurs", "pages"))],
        cwd=RACINE, capture_output=True, text=True, check=True).stdout
    lu = dict(ligne.split(": merge: ") for ligne in sortie.splitlines())
    assert lu == {**{f"tests/temoins/{nom}.json": "cles" for nom in
                     ("simulations", "sorties", "droit", "servis", "valeurs")},
                  "tests/temoins/pages.json": "unset"}


# -- les compteurs des cliquets, dont les baisses s'additionnent ---------------------


def cliquets(repli: int, sans_texte: int = 306, commentaire: str = "valeurs de repli") -> str:
    """Les compteurs de ``tests/test_cliquets_du_droit_date.py``, tels qu'ils
    s'écrivent : un nombre par ligne, l'un sous l'autre."""
    return (f'"""Les cliquets."""\n\n#: Les {commentaire}.\nVALEURS_DE_REPLI = {repli}\n'
            f"#: Les renvois sans texte.\nRENVOIS_SANS_TEXTE = {sans_texte}\n")


def perimetre(sans_statut: int, sans_reponse: int = 429) -> str:
    return (f"cliquet:\n  # Les rédactions sans aucun statut.\n"
            f"  redactions_sans_statut: {sans_statut}\n"
            f"  citees_sans_reponse: {sans_reponse}\n  pose_le: 2026-11-19\n")


def test_deux_baisses_d_un_meme_cliquet_s_additionnent():
    """Deux chantiers abaissent le même compteur, chacun de ce qu'il a réglé :
    git bute sur la ligne, et la bonne valeur, celle des deux réunis, n'est
    écrite d'aucun côté. Les deux baisses s'additionnent ; le filet joué avant
    l'envoi recompte, et refuse si les deux chantiers avaient réglé la même
    chose."""
    assert not fusionner.fusion_de_texte(cliquets(97), cliquets(100), cliquets(95))[0]
    assert fusionner.fusionner_compteurs(cliquets(100), cliquets(97), cliquets(95)) == (
        True, cliquets(92))
    assert fusionner.fusionner_compteurs(perimetre(9208), perimetre(9203, 428),
                                         perimetre(9195)) == (True, perimetre(9190, 428))


def test_un_compteur_qui_monte_d_un_cote_reste_un_conflit():
    """Un cliquet ne peut que baisser : une hausse ne se fond jamais dans la
    baisse de l'autre côté, qui la cacherait."""
    propre, resultat = fusionner.fusionner_compteurs(cliquets(100), cliquets(97), cliquets(101))
    assert not propre
    assert "<<<<<<<" in resultat


def test_un_compteur_sous_zero_reste_un_conflit():
    assert not fusionner.fusionner_compteurs(cliquets(3), cliquets(1), cliquets(0))[0]


def test_un_texte_change_autour_d_un_compteur_reste_un_conflit():
    """Seul un nombre change sur la ligne, des deux côtés ; le reste du texte
    s'écrit à la main, et son conflit reste un conflit."""
    main = cliquets(97).replace("VALEURS_DE_REPLI = 97", "VALEURS_DE_REPLI = 97  # au 21")
    assert not fusionner.fusionner_compteurs(cliquets(100), main, cliquets(95))[0]
    assert not fusionner.fusionner_compteurs(
        cliquets(100), cliquets(97, commentaire="valeurs écrites"),
        cliquets(95, commentaire="valeurs posées"))[0]


def test_deux_compteurs_differents_se_fusionnent_comme_du_texte():
    assert fusionner.fusionner_compteurs(perimetre(9208), perimetre(9203),
                                         perimetre(9208, 427)) == (True, perimetre(9203, 427))


def test_les_cliquets_relevent_de_la_fusion_des_compteurs():
    import subprocess
    fichiers = ["tests/test_cliquets_du_droit_date.py", "data/reference/textes/perimetre.yaml"]
    sortie = subprocess.run(["git", "check-attr", "merge", "--", *fichiers], cwd=RACINE,
                            capture_output=True, text=True, check=True).stdout
    assert sortie.splitlines() == [f"{f}: merge: compteurs" for f in fichiers]


def test_un_identifiant_ou_une_date_change_des_deux_cotes_reste_un_conflit():
    """Seule une ligne faite d'un nom et d'un seul nombre est un compteur. Un
    identifiant d'article, une date, un nombre au milieu d'un texte ne
    s'additionnent jamais (relecture du 21 novembre 2026 : l'identifiant
    LEGIARTI000006778516 ressortait LEGIARTI6776484, la date du 19 au 16)."""
    def article(identifiant: str) -> str:
        return f"articles:\n  - LEGIARTI{identifiant}\n  - fin\n"
    assert not fusionner.fusionner_compteurs(article("000006778516"), article("000006778510"),
                                             article("000006778508"))[0]

    def pose(jour: int) -> str:
        return f"cliquet:\n  redactions_sans_statut: 10\n  pose_le: 2026-11-{jour}\n"
    assert not fusionner.fusionner_compteurs(pose(19), pose(18), pose(17))[0]

    def phrase(n: int) -> str:
        return f"#: Les {n} renvois.\nX = 1\n"
    assert not fusionner.fusionner_compteurs(phrase(10), phrase(9), phrase(8))[0]
