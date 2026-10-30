"""La base de législation de la Cnav, exploitée en entier (action 175, étape 1).

`scripts/fetch/cnav_api.py` est le module commun des récupérateurs qui lisent
la base : l'adresse de son API, l'en-tête de leurs requêtes, la lecture d'une
réponse déjà téléchargée. `scripts/fetch/cnav_legislation.py` lit la base
entière — ses trois collections, ses menus, ses fenêtres d'information, les
références qu'elles lient, et celles que les références citent, de proche en
proche — et tient le registre `data/reference/legislation/cnav/`, où chaque
barème, exposé, liste, référence et fenêtre a son sort, et où
`citations.csv` garde qui cite qui. Ces tests les tiennent ensemble, sans
réseau : le module lit ce qu'on lui donne, le récupérateur range ce qu'il lit,
aucun objet du registre n'est sans sort, et chaque sort renvoie à ce qui
existe.
"""

from __future__ import annotations

import ast
import csv
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
FETCH = RACINE / "scripts" / "fetch"
REGISTRE = RACINE / "data" / "reference" / "legislation" / "cnav"
GENRES = ("baremes", "exposes", "listes", "references", "fenetres", "mises_a_jour", "documents")
SORTS = ("branche", "recoupe", "limite", "hors_modele", "a_lire")
#: Les genres dont l'API peut ne pas servir un objet lié : il reste sans titre.
SANS_TITRE_POSSIBLE = ("references", "fenetres", "documents")

#: Les récupérateurs qui lisent la base : les dix que l'action 175 a relevés
#: le 29 octobre 2026 — neuf `cnav_*.py` qui nomment l'API, et `ines.py` —,
#: `cnav_revalorisation_salaires.py`, qui en lit les circulaires sous `/Pdf/`,
#: et celui de la base entière.
LECTEURS_DE_LA_BASE = (
    "cnav_assiette_avpf.py",
    "cnav_avts.py",
    "cnav_baremes_rci.py",
    "cnav_minimum_contributif.py",
    "cnav_minimum_vieillesse.py",
    "cnav_points_avant_1973.py",
    "cnav_revalorisation_pensions.py",
    "cnav_revalorisation_salaires.py",
    "cnav_revalorisation_salaires_anciennes.py",
    "cnav_reversion.py",
    "ines.py",
    "cnav_legislation.py",
)


def _module(nom: str):
    if str(FETCH) not in sys.path:
        sys.path.insert(0, str(FETCH))
    chemin = FETCH / f"{nom}.py"
    specification = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules[nom] = module
    specification.loader.exec_module(module)
    return module


# -- le module commun -----------------------------------------------------------


def test_une_reponse_deja_telechargee_se_lit_entiere_ou_seule(tmp_path):
    """La liste entière de `/baremes`, telle que l'API la sert — un JSON que
    précède une marque d'ordre des octets —, ou la réponse d'un seul barème :
    le module y trouve le contenu d'un barème par son nom, avec ou sans
    `.aspx`, et refuse un nom qu'elle ne porte pas."""
    module = _module("cnav_api")
    fiches = [{"fileLeafRef": "aspa_montant_bar.aspx", "titre": "ASPA", "contenu": "<p>ASPA</p>"},
              {"fileLeafRef": "mfe_montant_bar.aspx", "titre": "MFE", "contenu": "<p>MFE</p>"}]
    liste = tmp_path / "baremes.json"
    liste.write_bytes(b"\xef\xbb\xbf" + json.dumps(fiches).encode("utf-8"))
    seul = tmp_path / "aspa.json"
    seul.write_text(json.dumps(fiches[0]), encoding="utf-8")
    assert module.contenus(["aspa_montant_bar", "mfe_montant_bar.aspx"], fichier=liste) == {
        "aspa_montant_bar": "<p>ASPA</p>", "mfe_montant_bar.aspx": "<p>MFE</p>"}
    assert module.contenus(["aspa_montant_bar"], fichier=seul) == {
        "aspa_montant_bar": "<p>ASPA</p>"}
    with pytest.raises(KeyError, match="mfe_montant_bar"):
        module.contenus(["mfe_montant_bar"], fichier=seul)
    assert module.adresse_bareme("aspa_montant_bar") == module.adresse_bareme(
        "aspa_montant_bar.aspx") == ("https://legislation.lassuranceretraite.fr/api/v1/"
                                     "baremes/baremesByFileLeafRef/aspa_montant_bar.aspx")


def test_les_recuperateurs_de_la_base_passent_par_le_module_commun():
    """L'adresse de la base et l'en-tête des requêtes ne se redéfinissent plus
    dans chaque script : ils sont dans `cnav_api.py`, et l'adresse n'est écrite
    nulle part ailleurs."""
    for chemin in sorted((RACINE / "scripts").rglob("*.py")):
        if chemin.name != "cnav_api.py":
            assert "https://legislation.lassuranceretraite.fr" not in chemin.read_text(
                encoding="utf-8"), f"{chemin.relative_to(RACINE)} redéfinit l'adresse"
    for nom in LECTEURS_DE_LA_BASE:
        texte = (FETCH / nom).read_text(encoding="utf-8")
        assert re.search(r"^import cnav_api\b", texte, re.M), f"{nom} ne passe pas par cnav_api"
        assert "User-Agent" not in texte, f"{nom} redéfinit l'en-tête"


# -- le récupérateur de la base entière ----------------------------------------


def test_les_liens_d_un_contenu_disent_ce_qu_ils_visent():
    """Les formes de lien que la base sert, relevées le 29 octobre 2026 : une
    référence par la route du site ou un PDF de `/Pdf/`, au besoin sous le
    préfixe d'un partage (`/%3ab%3a/r`) et suivi de paramètres ; un barème ou
    une liste, que le site ouvre par la même route, au besoin sous un
    sous-dossier ; un exposé ; une fenêtre d'information (`#/infosupp/`),
    exemple, lexique ou complément, au besoin sous le préfixe d'un partage ; un
    document qu'un barème joint (`Bareme/Pages/doc_communs/`), page ou PDF.
    Légifrance et le CLEISS ne sont pas des objets de la base."""
    module = _module("cnav_legislation")
    contenu = "".join(f'<a href="{lien}">x</a>' for lien in (
        "#/references-reglementaires?file_leaf_ref=circulaire_cnav_2014_039_12062014.aspx#1",
        "/Pdf/circulaire_cnav_2024_28_14102024.pdf",
        "/%3ab%3a/r/Pdf/circulaire_cnav_2006_06_13012006.pdf?csf=1&amp;web=1&amp;e=Cewl0G",
        "#/bareme?file_leaf_ref=periode_guerre_validation_periode_list.aspx#a",
        "/%3au%3a/r#/bareme?file_leaf_ref=bareme_vendeur_domicile/"
        "cotisation_salaire_vente_domicile_2026_bar.aspx",
        "#/expose?file_leaf_ref=retraite_personnelle_taux_taux_retraite_ex.aspx",
        "http://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000006742631",
        "https://www.cleiss.fr/docs/ol/algerie.html",
        "#/infosupp/ex_delai.aspx",
        "Bareme/Pages/doc_communs/listes_baremes/change/BNL-CETAUX_HONGRIE.htm",
        "/%3ab%3a/rBareme/Pages/doc_communs/listes_baremes/"
        "ti_cotisation_assiette_maximale_cotisation.pdf?csf=1&amp;web=1",
        "/%3au%3a/r#/infosupp/ex_carte_invalidite.aspx?csf=1&amp;web=1&amp;e=sw1Ggi",
        "#/references-reglementaires?file_leaf_ref=LE_MIN_10031970_59%20373%20AG.aspx",
        "/Pdf/circulaire_cnav_2024_28_14102024.pdf",
    ))
    assert module.liens(contenu) == [
        ("reference", "circulaire_cnav_2014_039_12062014.aspx"),
        ("reference", "circulaire_cnav_2024_28_14102024.pdf"),
        ("reference", "circulaire_cnav_2006_06_13012006.pdf"),
        ("bareme", "periode_guerre_validation_periode_list.aspx"),
        ("bareme", "cotisation_salaire_vente_domicile_2026_bar.aspx"),
        ("expose", "retraite_personnelle_taux_taux_retraite_ex.aspx"),
        ("fenetre", "ex_delai.aspx"),
        ("document", "listes_baremes/change/BNL-CETAUX_HONGRIE.htm"),
        ("document", "listes_baremes/ti_cotisation_assiette_maximale_cotisation.pdf"),
        ("fenetre", "ex_carte_invalidite.aspx"),
        ("reference", "LE_MIN_10031970_59 373 AG.aspx"),
    ]


def test_un_bareme_prend_le_theme_de_son_menu_ou_du_bareme_qui_le_lie():
    """Le menu des barèmes n'en nomme que les pages d'accueil ; une page
    d'accueil lie ses éditions, qui prennent son thème. Un barème qu'aucun menu
    n'atteint reste sans thème, et un exposé prend celui de son `menuId`."""
    module = _module("cnav_legislation")
    menu = [{"id": "m1", "libelle": "Carrière", "themes": [
        {"id": "t1", "libelle": "Versements volontaires de cotisations", "sousThemes": [
            {"id": "s1", "libelle": "Versement pour la retraite"}]},
        {"id": "t2", "libelle": "Salaire validant 1 trimestre", "sousThemes": []}]}]
    par_menu = {"s1": [{"fileLeafRef": "vplr_cout_par_trimestre_bar.aspx"}],
                "t2": [{"fileLeafRef": "salaire_validant_un_trimestre_montant_bar.aspx"}]}
    contenus = {
        "vplr_cout_par_trimestre_bar.aspx":
            '<a href="#/bareme?file_leaf_ref=vplr_cout_par_trimestre_2021_bar.aspx">2021</a>',
        "vplr_cout_par_trimestre_2021_bar.aspx":
            '<a href="#/bareme?file_leaf_ref=vplr_cout_par_trimestre_bar.aspx">retour</a>',
        "salaire_validant_un_trimestre_montant_bar.aspx": "<p>1 803,00 €</p>",
        "smic_smig_smic_mensuel_mayotte_bar.aspx": "<p>orphelin</p>",
    }
    versement = "Carrière > Versements volontaires de cotisations > Versement pour la retraite"
    assert module.themes_des_baremes(menu, par_menu, contenus) == {
        "vplr_cout_par_trimestre_bar.aspx": versement,
        "vplr_cout_par_trimestre_2021_bar.aspx": versement,
        "salaire_validant_un_trimestre_montant_bar.aspx": "Carrière > Salaire validant 1 trimestre",
    }
    assert module.chemins(menu)["s1"] == versement


def test_une_liste_et_une_reference_prennent_les_themes_de_ce_qui_les_lie():
    """Une liste, une référence et une fenêtre n'ont pas de menu : elles
    prennent le premier niveau du thème de chaque objet qui les lie, une liste
    ou une fenêtre le passant à ce qu'elle lie à son tour. Une référence ne le
    passe pas aux textes qu'elle cite : passé de citation en citation, le 29
    octobre 2026, il en donnait plus de cinq à 1 637 références, et seize à un
    article de code que toute la base cite ; `citations.csv` dit qui les
    cite."""
    module = _module("cnav_legislation")
    themes = {("exposes", "e1.aspx"): "Carrière > Cotisations-salaires",
              ("exposes", "e2.aspx"): "Mayotte - Législation > Carrière",
              ("baremes", "b.aspx"): "Carrière > Salaire validant 1 trimestre"}
    liens = {("exposes", "e1.aspx"): [("listes", "l.aspx"), ("references", "r1.aspx"),
                                      ("fenetres", "ex_delai.aspx")],
             ("exposes", "e2.aspx"): [("references", "r1.aspx")],
             ("baremes", "b.aspx"): [("references", "r2.pdf")],
             ("listes", "l.aspx"): [("references", "r3.aspx")],
             ("listes", "seule.aspx"): [("references", "r4.aspx")],
             ("references", "r3.aspx"): [("references", "LO_CSS_R742-13.aspx")],
             ("fenetres", "ex_delai.aspx"): [("references", "r5.aspx")]}
    assert module.themes_lies(liens, themes) == {
        ("listes", "l.aspx"): "Carrière",
        ("references", "r1.aspx"): "Carrière ; Mayotte - Législation",
        ("references", "r2.pdf"): "Carrière",
        ("references", "r3.aspx"): "Carrière",
        ("fenetres", "ex_delai.aspx"): "Carrière",
        ("references", "r5.aspx"): "Carrière",
    }


def test_la_base_se_suit_de_reference_en_reference():
    """Les références citent d'autres textes, et ceux-ci d'autres encore : le
    29 octobre 2026, les 2 298 références que les collections lient en
    citaient 2 020 autres, sur quatre rangs. La base est ce que ses objets
    atteignent, de proche en proche, et ce que sa recherche sert sans que rien
    ne le lie, avec ce que cela cite — les racines ; une référence que rien
    n'atteint n'en est pas."""
    module = _module("cnav_legislation")
    liens = {("exposes", "e.aspx"): [("references", "r1.aspx"), ("fenetres", "ex_delai.aspx")],
             ("fenetres", "ex_delai.aspx"): [("references", "r4.aspx")],
             ("mises_a_jour", "232"): [("references", "r6.pdf")],
             ("references", "r1.aspx"): [("references", "r2.aspx")],
             ("references", "r2.aspx"): [("references", "r3.pdf"), ("references", "r1.aspx")],
             ("references", "orpheline.aspx"): [("references", "r1.aspx")],
             ("references", "AC_SS_04122003.aspx"): [("references", "r7.aspx")]}
    assert module.fermeture(liens) == {"r1.aspx", "r2.aspx", "r3.pdf", "r4.aspx", "r6.pdf"}
    assert module.fermeture(liens, racines={"AC_SS_04122003.aspx"}) == {
        "r1.aspx", "r2.aspx", "r3.pdf", "r4.aspx", "r6.pdf", "AC_SS_04122003.aspx", "r7.aspx"}


def test_un_document_joint_se_suit_de_page_en_page():
    """Un barème joint des documents, pages ou PDF, sous
    `Bareme/Pages/doc_communs/` ; une page en lie d'autres, par un chemin
    relatif — le 29 octobre 2026, les 81 que lient les barèmes en atteignaient
    134 —, et charge ses valeurs par un script, qui n'est pas un document."""
    module = _module("cnav_legislation")
    page = "".join((
        '<link href="_layouts/CAMPUS/Campus-baremes/style/bnl_exp.css">',
        '<script src="_layouts/CAMPUS/Campus-baremes/js/declare/changece/decCEHONGRIE.js">',
        '<a href="https://legislation.lassuranceretraite.fr/#/bareme?file_leaf_ref=',
        'taux_change_taux_change_monnaie_par_pays_bar.aspx">retour</a>',
        '<a href="../../lb_global/BNL-GLOB-L_B_CEHONGRIE.htm">liste globale</a>',
        '<img src="/_layouts/CAMPUS/Campus-baremes/images/som_prece_dp.gif">'))
    assert module.liens(page, document="listes_baremes/change/BNL-CETAUX_HONGRIE.htm") == [
        ("bareme", "taux_change_taux_change_monnaie_par_pays_bar.aspx"),
        ("document", "lb_global/BNL-GLOB-L_B_CEHONGRIE.htm")]
    assert module.date_http("Mon, 24 Apr 2023 09:24:32 GMT") == "2023-04-24T09:24:32Z"
    assert module.date_http("") == ""


def test_une_page_jointe_suit_les_pages_que_declare_son_script_de_valeurs():
    """Le script de valeurs d'une page jointe n'est pas un document, mais il
    déclare souvent, pour chaque période ou chaque pays, la page qui porte les
    valeurs : la page l'ouvre `depuis` le dossier qu'elle donne, sinon à côté
    d'elle. Le 30 octobre 2026, treize pages en chargeaient un, qui déclaraient
    plus de trois cents pages que rien d'autre ne lie : les taux de cotisation
    d'avant 2014, les salaires forfaitaires des gens de maison, les taux de
    change par pays."""
    module = _module("cnav_legislation")
    page = ('<script src="_layouts/CAMPUS/Campus-baremes/js/declare/decTAUXDECOTISATIONS.js">'
            '</script><script>function orientelavaleur() { var valeur = 1; '
            'depuis = "../listes_baremes/cotisation/"; orientevaleur(ovaleur,valeur,depuis); }'
            '</script>')
    assert module.script_de_valeurs(page) == (
        "_layouts/CAMPUS/Campus-baremes/js/declare/decTAUXDECOTISATIONS.js")
    script = ('var t_p = new Array("Du 01/11/2012 au 31/12/2013","BNL-TAUX_COTISATIONS2012.htm");'
              'var t_p = new Array("01/07/1930 au 31/12/1935","BNL-TAUX_COTISATIONS3035cat5.htm");'
              'var t_p = new Array("Du 01/11/2012 au 31/12/2013","BNL-TAUX_COTISATIONS2012.htm");')
    assert module.declarees(page, "listes_baremes/BNL-L_B_TAUXDECOTISATIONS.htm", script) == [
        ("document", "listes_baremes/cotisation/BNL-TAUX_COTISATIONS2012.htm"),
        ("document", "listes_baremes/cotisation/BNL-TAUX_COTISATIONS3035cat5.htm")]
    sans_depuis = '<script src="_layouts/CAMPUS/Campus-baremes/js/declare/decGENSMAIS.js"></script>'
    assert module.declarees(sans_depuis, "listes_baremes/BNL-L_B_GENSMAIS.htm",
                            'per = new Array ("ho", "m_100000", "gensmais/BNL-GM_H-48.htm");') == [
        ("document", "listes_baremes/gensmais/BNL-GM_H-48.htm")]
    assert module.script_de_valeurs('<a href="BNL-GM_H-48.htm">') is None


def test_une_page_declaree_que_le_site_ne_sert_pas_n_entre_pas_au_registre():
    """Un script de valeurs compose ses chemins depuis la page qui le charge
    d'ordinaire : chargé par une autre — une sous-page, une « vision globale »
    —, il en compose de faux (`listes_baremes/change/change/…`), et il déclare
    des pages que le site n'a pas. Une page que seul un script déclare n'entre
    donc au registre que si le site la sert ; un lien mort d'une page reste,
    comme les autres objets que la base nomme sans les servir."""
    module = _module("cnav_legislation")
    documents = {"a.htm": {"corps": b""}, "b.htm": None, "c.htm": None}
    liens = {("documents", "p.htm"): [("documents", "a.htm"), ("documents", "b.htm"),
                                      ("documents", "c.htm"), ("references", "r.pdf")]}
    assert module.sans_les_pages_declarees_absentes(
        documents, liens, declarees_seulement={"a.htm", "b.htm"}) == {"b.htm"}
    assert documents == {"a.htm": {"corps": b""}, "c.htm": None}
    assert liens == {("documents", "p.htm"): [("documents", "a.htm"), ("documents", "c.htm"),
                                              ("references", "r.pdf")]}


def test_les_fenetres_se_lisent_par_leurs_collections():
    """`/lexique`, `/exemple` et `/complementInformation` servent chacune ses
    fenêtres d'un appel : 392 le 29 octobre 2026, quand les objets de la base
    n'en liaient que 178. La collection dit la nature."""
    module = _module("cnav_legislation")
    collections = {
        "lexique": [{"file_leaf_ref": "conjoint_lex.aspx", "titre": "Conjoint"}],
        "exemple": [{"file_leaf_ref": "ex_dom_exonere.aspx", "titre": "Assuré DOM exonéré"}],
        "complementInformation": [{"file_leaf_ref": "ex_delai.aspx", "titre": "Délai"}],
    }
    assert module.fenetres_des_collections(collections) == {
        "conjoint_lex.aspx": {"file_leaf_ref": "conjoint_lex.aspx", "titre": "Conjoint",
                              "nature": "lexique"},
        "ex_dom_exonere.aspx": {"file_leaf_ref": "ex_dom_exonere.aspx",
                                "titre": "Assuré DOM exonéré", "nature": "exemple"},
        "ex_delai.aspx": {"file_leaf_ref": "ex_delai.aspx", "titre": "Délai",
                          "nature": "complement"},
    }


def test_un_avis_prend_le_theme_de_ce_qu_il_met_a_jour():
    """Un avis de mise à jour (`/mises-a-jour`) dit quels barèmes et exposés
    ont changé, et selon quelle circulaire : il prend le premier niveau de leur
    thème."""
    module = _module("cnav_legislation")
    liens = {("mises_a_jour", "232"): [("baremes", "asi_montant_bar.aspx"),
                                       ("exposes", "asi_ex.aspx"),
                                       ("references", "circulaire_cnav_2019_15_05042019.pdf")],
             ("mises_a_jour", "233"): [("references", "circulaire_cnav_2019_16_05042019.pdf")]}
    themes = {("baremes", "asi_montant_bar.aspx"):
              "Allocations du minimum > Allocation supplémentaire d'invalidité",
              ("exposes", "asi_ex.aspx"): "Allocation du minimum > ASI"}
    assert module.themes_des_avis(liens, themes) == {
        "232": "Allocation du minimum ; Allocations du minimum"}


def test_la_recherche_se_mene_par_annees_mois_natures_et_mots_du_droit():
    """La recherche de la base ne rend pas plus de 250 résultats par requête,
    et ne compte rien : elle se mène par année, par mois de chaque année, par
    nature de texte et par mot du droit des retraites — le 29 octobre 2026, les
    années et les mois trouvaient 6 131 références ; soixante mots du droit,
    36 de plus ; soixante autres, 7 de plus encore. Elle rend les noms qu'elle
    sert, une fois chacun, et ne garde de ses résultats que ces noms : les
    contenus des 1 672 premières requêtes pesaient 405 Mo."""
    module = _module("cnav_legislation")
    requetes = module.requetes_de_recherche()
    assert len(requetes) == len(set(requetes))
    assert {"1945", "2026", "/06/2014", "/12/1972", "circulaire", "arrangement", "retraite",
            "Andorre", "note technique", "carrière longue"} <= set(requetes)
    resultats = {"2014": [{"filename": "AC_SS_04122003.aspx", "contenu": "…"}, {"filename": ""},
                          {"filename": "circulaire_cnav_2014_039_12062014.aspx"},
                          {"filename": "searchWordCustomFilterFr", "type": "nimporteQuelsMots"}],
                 "/06/2014": [{"filename": "AC_SS_04122003.aspx"}], "décret": None}
    assert module.trouvees(resultats) == {"AC_SS_04122003.aspx",
                                          "circulaire_cnav_2014_039_12062014.aspx"}
    assert module.noms_par_requete(resultats) == {
        "2014": ["AC_SS_04122003.aspx", "circulaire_cnav_2014_039_12062014.aspx"],
        "/06/2014": ["AC_SS_04122003.aspx"], "décret": None}


def test_une_fenetre_dit_sa_nature(monkeypatch):
    """L'API sert une fenêtre d'information sous sa nature — `exemple`,
    `lexique` ou `complementInformation`, que son nom ne dit pas : le 29
    octobre 2026, `ex_delai.aspx` était un complément —, et répond 500 à celle
    qu'elle ne sert pas."""
    import urllib.error

    module = _module("cnav_legislation")
    servies = {
        "ex_delai.aspx": {"complementInformation": {
            "titre": "Délai de distance", "date_modification": "2025-10-27T23:54:00Z[UTC]"}},
        "conjoint_lex.aspx": {"lexique": {
            "titre": "Conjoint", "date_modification": "2023-06-02T05:31:00Z[UTC]"}},
    }

    def obtenir(route, delai=60):
        nom = route.rsplit("/", 1)[1]
        if nom not in servies:
            raise urllib.error.HTTPError(route, 500, "Internal Server Error", {}, None)
        return servies[nom]

    monkeypatch.setattr(module.cnav_api, "obtenir", obtenir)
    monkeypatch.setattr(module.time, "sleep", lambda pause: None)
    assert module._fenetre("ex_delai.aspx") == ("ex_delai.aspx", {
        "titre": "Délai de distance", "date_modification": "2025-10-27T23:54:00Z[UTC]",
        "nature": "complement"})
    assert module._fenetre("conjoint_lex.aspx")[1]["nature"] == "lexique"
    assert module._fenetre("date_arrete_compte_lex.aspx") == ("date_arrete_compte_lex.aspx", None)


def test_un_texte_est_date_du_jour_que_son_titre_porte():
    """L'API date un texte de la veille au soir, en temps universel — minuit à
    Paris, à deux heures près — : la circulaire 2014-39 « du 12/06/2014 » porte
    `2014-06-11T20:00:00Z[UTC]`, la 2025-29 « du 22/12/2025 »
    `2025-12-21T23:00:00Z[UTC]`. Une date de modification, elle, garde son
    instant, sans la zone que l'API y accroche."""
    module = _module("cnav_legislation")
    assert module.date_du_texte("2014-06-11T20:00:00Z[UTC]") == "2014-06-12"
    assert module.date_du_texte("2025-12-21T23:00:00Z[UTC]") == "2025-12-22"
    assert module.date_du_texte("") == ""
    assert module.instant("2023-05-31T08:09:00Z[UTC]") == "2023-05-31T08:09:00Z"


def test_une_lecture_garde_les_sorts_et_inscrit_le_neuf_a_lire():
    """Ce que la base sert de neuf entre `a_lire` ; ce qui attend encore prend
    ce que la base en dit ; ce qui a son sort le garde, avec la date de la
    version qui l'a reçu, que la veille comparera à la base ; ce qui en
    disparaît sort du registre s'il n'a pas été lu, et y reste sinon."""
    module = _module("cnav_legislation")

    def ligne(nom, titre, date, sort="a_lire", renvoi="", script=""):
        return {"nom": nom, "titre": titre, "theme": "A", "modifie_le": date,
                "sort": sort, "renvoi": renvoi, "script": script}

    registre = {
        "lu.aspx": ligne("lu.aspx", "Lu", "2025-01-01T00:00:00Z", "branche",
                         "data/x.csv", "scripts/fetch/x.py"),
        "attend.aspx": ligne("attend.aspx", "Attend", "2025-01-01T00:00:00Z"),
        "parti.aspx": ligne("parti.aspx", "Parti", "2025-01-01T00:00:00Z"),
        "parti_lu.aspx": ligne("parti_lu.aspx", "Parti lu", "2025-01-01T00:00:00Z",
                               "hors_modele", "les rachats, que le modèle ne pratique pas"),
    }
    lus = {"lu.aspx": {"titre": "Lu, retitré", "theme": "B", "modifie_le": "2026-03-01T00:00:00Z"},
           "attend.aspx": {"titre": "Attend", "theme": "B", "modifie_le": "2026-03-01T00:00:00Z"},
           "neuf.aspx": {"titre": "Neuf", "theme": "C", "modifie_le": "2026-10-01T00:00:00Z"}}
    nouveau, rapport = module.inscrire(registre, lus, "modifie_le")
    assert nouveau == {
        "lu.aspx": {**ligne("lu.aspx", "Lu, retitré", "2025-01-01T00:00:00Z", "branche",
                            "data/x.csv", "scripts/fetch/x.py"), "theme": "B"},
        "attend.aspx": {**ligne("attend.aspx", "Attend", "2026-03-01T00:00:00Z"), "theme": "B"},
        "neuf.aspx": {**ligne("neuf.aspx", "Neuf", "2026-10-01T00:00:00Z"), "theme": "C"},
        "parti_lu.aspx": registre["parti_lu.aspx"],
    }
    assert rapport == {"nouveaux": ["neuf.aspx"], "modifies": ["lu.aspx"],
                       "disparus": ["parti.aspx", "parti_lu.aspx"]}


def test_une_reference_ne_se_relit_que_si_ce_qui_la_lie_a_change():
    """Les quelque deux mille références se lisent une à une : une lecture ne
    redemande que celles que le registre ne porte pas, ou sans titre, et
    celles que lie un objet neuf ou que sa date de modification dit changé."""
    module = _module("cnav_legislation")
    liens = {("baremes", "b.aspx"): [("references", "r1.aspx"), ("references", "r2.pdf")],
             ("exposes", "e.aspx"): [("references", "r2.pdf"), ("references", "r3.aspx")],
             ("listes", "l.aspx"): [("references", "r4.aspx")]}
    registre = {"r1.aspx": {"titre": "R1"}, "r2.pdf": {"titre": "R2"}, "r3.aspx": {"titre": ""}}
    assert module.references_a_lire(liens, registre, changes={("exposes", "e.aspx")}) == {
        "r2.pdf", "r3.aspx", "r4.aspx"}
    assert module.references_a_lire(liens, registre, changes=set()) == {"r3.aspx", "r4.aspx"}


def test_une_route_qui_flanche_se_redemande(monkeypatch):
    """Le 29 octobre 2026, la base a répondu 500 à `/expose`, deux fois de
    suite, puis l'a servi une minute plus tard : une route se redemande après
    une pause qui double, jusqu'à quatre fois. Une référence que l'API ne sert
    pas répond 500 elle aussi, à chaque fois : elle ne se redemande qu'une
    fois."""
    import urllib.error

    module = _module("cnav_legislation")
    appels, pauses = [], []

    def obtenir(route, delai=60):
        appels.append(route)
        if route == "/expose" and len(appels) < 3:
            raise urllib.error.HTTPError(route, 500, "Internal Server Error", {}, None)
        if route.startswith("/reference/"):
            raise urllib.error.HTTPError(route, 500, "Internal Server Error", {}, None)
        return [{"route": route}]

    monkeypatch.setattr(module.cnav_api, "obtenir", obtenir)
    monkeypatch.setattr(module.time, "sleep", pauses.append)
    assert module._obtenir("/expose") == [{"route": "/expose"}]
    assert (len(appels), pauses) == (3, [2, 4])
    assert module._reference("inconnue.pdf") == ("inconnue.pdf", None)
    assert len(appels) == 5 and pauses == [2, 4, 2]


def test_une_reference_liee_sous_une_casse_fautive_prend_le_nom_que_l_api_sert(monkeypatch):
    """La base lie « Circulaire_cnav_2016_35_02082016.pdf », que l'API ne sert
    pas, et « circulaire_cnav_2016_35_02082016.pdf », qu'elle sert : une
    référence qu'elle ne sert pas sous son nom se redemande en minuscules, et
    le registre la porte une fois, sous le nom servi."""
    import urllib.error

    module = _module("cnav_legislation")

    def obtenir(route, delai=60):
        nom = route.rsplit("/", 1)[1]
        if nom != nom.lower():
            raise urllib.error.HTTPError(route, 500, "Internal Server Error", {}, None)
        return {"file_leaf_ref": nom, "titre": "Circulaire Cnav 2016/35 du 02/08/2016"}

    monkeypatch.setattr(module.cnav_api, "obtenir", obtenir)
    monkeypatch.setattr(module.time, "sleep", lambda pause: None)
    servi = {"file_leaf_ref": "circulaire_cnav_2016_35_02082016.pdf",
             "titre": "Circulaire Cnav 2016/35 du 02/08/2016"}
    assert module._reference("Circulaire_cnav_2016_35_02082016.pdf") == (
        "Circulaire_cnav_2016_35_02082016.pdf", servi)
    liens = {("exposes", "e.aspx"): [("references", "Circulaire_cnav_2016_35_02082016.pdf"),
                                     ("listes", "l.aspx")],
             ("listes", "l.aspx"): [("references", "circulaire_cnav_2016_35_02082016.pdf")],
             ("references", "Circulaire_cnav_2016_35_02082016.pdf"): [
                 ("references", "LO_CSS_R742-13.aspx")],
             ("references", "circulaire_cnav_2016_35_02082016.pdf"): [
                 ("references", "LO_CSS_R742-13.aspx"), ("references", "D_IM_2011007_07092011.aspx")]}
    assert module.renommer(liens, {"Circulaire_cnav_2016_35_02082016.pdf":
                                   "circulaire_cnav_2016_35_02082016.pdf"}) == {
        ("exposes", "e.aspx"): [("references", "circulaire_cnav_2016_35_02082016.pdf"),
                                ("listes", "l.aspx")],
        ("listes", "l.aspx"): [("references", "circulaire_cnav_2016_35_02082016.pdf")],
        ("references", "circulaire_cnav_2016_35_02082016.pdf"): [
            ("references", "LO_CSS_R742-13.aspx"), ("references", "D_IM_2011007_07092011.aspx")]}


# -- le registre ---------------------------------------------------------------


def _registre() -> dict[str, list[dict]]:
    return {genre: list(csv.DictReader(
        ligne for ligne in (REGISTRE / f"{genre}.csv").read_text(encoding="utf-8").splitlines()
        if not ligne.startswith("#"))) for genre in GENRES}


def _chaines(chemin: Path) -> set[str]:
    """Les chaînes du code d'un script, docstrings exclues."""
    arbre = ast.parse(chemin.read_text(encoding="utf-8"))
    docstrings = {id(noeud.value) for noeud in ast.walk(arbre)
                  if isinstance(noeud, ast.Expr) and isinstance(noeud.value, ast.Constant)}
    return {noeud.value for noeud in ast.walk(arbre)
            if isinstance(noeud, ast.Constant) and isinstance(noeud.value, str)
            and id(noeud) not in docstrings}


def _cites(chaine: str) -> set[str]:
    """Les noms qu'une chaîne du code peut donner à un objet : elle-même, et,
    pour une adresse de document joint, son chemin sous `doc_communs/`."""
    return {chaine, *([chaine.split("doc_communs/", 1)[1]] if "doc_communs/" in chaine else [])}


def _nomme(chaines: set[str], nom: str) -> bool:
    """Le script nomme-t-il l'objet : son nom, avec ou sans extension, son
    adresse s'il est un document joint, ou un motif qui le donne,
    `…_csg_{}_bar` pour l'année que le script y met ?"""
    souche = nom.rsplit(".", 1)[0]
    cites = set().union(*map(_cites, chaines)) if chaines else set()
    return bool({nom, souche} & cites) or any(
        "{}" in chaine and re.fullmatch(re.escape(chaine).replace(r"\{\}", r"\d{4}"), souche)
        for chaine in chaines)


def test_le_registre_est_hors_de_l_empreinte_du_modele():
    """Aucun calcul ne lit le registre : hors de l'empreinte de la mémoire des
    calculs (`memoire.HORS_DU_MODELE`), comme la veille, un sort qu'une session
    y écrit ne refait pas le coût."""
    from retraite_notionnelle import memoire

    for genre in GENRES:
        assert not memoire.du_modele(f"data/reference/legislation/cnav/{genre}.csv"), genre


def test_chaque_objet_de_la_base_a_son_sort():
    """Le registre porte chaque barème, exposé, liste, référence et fenêtre une
    seule fois, rangés par nom, et chacun a l'un des cinq sorts ; une fenêtre,
    sa nature."""
    for genre, lignes in _registre().items():
        noms = [ligne["nom"] for ligne in lignes]
        assert noms, f"{genre} : registre vide"
        assert noms == sorted(set(noms)), f"{genre} : noms en double ou en désordre"
        assert len({nom.lower() for nom in noms}) == len(noms), (
            f"{genre} : deux noms qui ne diffèrent que par la casse")
        for ligne in lignes:
            assert ligne["sort"] in SORTS, (
                f"{genre}/{ligne['nom']} : sort « {ligne['sort']} », hors de {SORTS}")
            assert ligne["titre"].strip() or genre in SANS_TITRE_POSSIBLE, (
                f"{genre}/{ligne['nom']} : sans titre")
            if genre == "fenetres" and ligne["titre"].strip():
                assert ligne["nature"] in ("exemple", "lexique", "complement"), ligne["nom"]


def test_les_citations_relient_des_references_du_registre():
    """`citations.csv` garde, pour chaque référence, les textes qu'elle cite :
    ce que la base ne dit qu'en lisant chaque référence, et ce qui permet de la
    relire sans redemander ce qui n'a pas changé. Chaque citation relie deux
    références du registre, une fois, rangée."""
    references = {ligne["nom"] for ligne in _registre()["references"]}
    lignes = list(csv.DictReader(
        ligne for ligne in (REGISTRE / "citations.csv").read_text(encoding="utf-8").splitlines()
        if not ligne.startswith("#")))
    paires = [(ligne["reference"], ligne["cite"]) for ligne in lignes]
    assert len(paires) > 1000, "le graphe des citations a disparu"
    assert paires == sorted(set(paires)), "citations en double ou en désordre"
    for reference, cite in paires:
        assert reference in references and cite in references, (reference, cite)
        assert reference != cite, reference


def test_un_sort_renvoie_a_ce_qui_existe():
    """`branche` nomme la série que l'objet nourrit et le script qui le lit,
    et ce script le nomme ; `recoupe`, le test qui le confronte ; `limite`, la
    fiche ou la limite qui dit ce que le modèle n'en sert pas ; `hors_modele`,
    sa raison ; `a_lire`, rien. Plusieurs renvois se séparent par « ; »."""
    for genre, lignes in _registre().items():
        for ligne in lignes:
            objet, sort = f"{genre}/{ligne['nom']}", ligne["sort"]
            renvois = [r.strip() for r in ligne["renvoi"].split(";") if r.strip()]
            scripts = [s.strip() for s in ligne["script"].split(";") if s.strip()]
            if sort == "a_lire":
                assert not renvois and not scripts, f"{objet} : à lire, sans renvoi"
                continue
            assert renvois, f"{objet} : {sort} sans renvoi"
            assert sort == "branche" or not scripts, f"{objet} : un script hors de `branche`"
            if sort == "hors_modele":
                continue
            for renvoi in renvois:
                fichier, _, test = renvoi.partition("::")
                assert (RACINE / fichier.split("#")[0]).is_file(), (
                    f"{objet} : {renvoi} n'existe pas")
                assert not fichier.startswith("data/brut/"), (
                    f"{objet} : {renvoi} n'est pas versionné, et n'existe pas sur un "
                    "clone neuf : la série que le dépôt garde")
                if sort == "recoupe":
                    assert test and re.search(rf"^def {re.escape(test)}\(", (
                        RACINE / fichier).read_text(encoding="utf-8"), re.M), (
                        f"{objet} : le test {renvoi} n'existe pas")
            if sort == "branche":
                assert scripts, f"{objet} : branché sans script"
                for script in scripts:
                    assert (RACINE / script).is_file(), f"{objet} : {script} n'existe pas"
                    assert _nomme(_chaines(RACINE / script), ligne["nom"]), (
                        f"{objet} : {script} ne le nomme pas")


def test_ce_que_lit_un_recuperateur_est_branche_sur_lui():
    """Un barème, une circulaire ou un document joint que nomme le code d'un
    récupérateur de la base est `branche`, et son registre nomme ce
    récupérateur : la base ne nourrit aucune série sans que le registre le
    dise. Un avis de mise à jour n'a pour nom que son numéro, que n'importe
    quelle chaîne du code peut porter : il n'est pas de ce qu'un nom désigne."""
    registre = {ligne["nom"]: ligne for genre, lignes in _registre().items()
                if genre != "mises_a_jour" for ligne in lignes}
    par_souche = {nom.rsplit(".", 1)[0]: ligne for nom, ligne in registre.items()}
    for nom in LECTEURS_DE_LA_BASE:
        script = f"scripts/fetch/{nom}"
        for chaine in sorted(set().union(*map(_cites, _chaines(FETCH / nom)))):
            ligne = registre.get(chaine) or par_souche.get(chaine)
            if ligne is None:
                continue
            assert ligne["sort"] == "branche", f"{chaine} : lu par {script}, et {ligne['sort']}"
            assert script in [s.strip() for s in ligne["script"].split(";")], (
                f"{chaine} : lu par {script}, que son registre ne nomme pas")
