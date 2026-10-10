"""Tests des revues du site du 15 septembre 2026 — l'expérience de
l'utilisateur, la clarté des arguments, l'architecture, la touche IA —, et
de ce qu'elles ont fait naître : l'entrée depuis le site du parti (action
29), la certification datée (action 13), les réglages des pages agrégées.

Détachés de ``test_web.py`` le 30 septembre 2026 ; ce qu'ils partagent avec
lui est dans ``outils_web.py``.
"""

from __future__ import annotations

import dataclasses
import html
import itertools
import re
from pathlib import Path
from urllib.parse import parse_qsl

import pytest

from retraite_notionnelle.cout import COMPOSANTE_GARANTIE
from retraite_notionnelle.donnees.bilan import EcartsFiges
from retraite_notionnelle.donnees.chargement import (
    DonneeInsuffisante,
    charger_periodes_non_travaillees,
)
from retraite_notionnelle.saisie import (
    AGE_DEBUT_MINIMAL,
    AGE_LIQUIDATION_MAXIMAL,
    AGES_REFERENCE,
    ANNEE_CARRIERE_MAXIMALE,
    ANNEE_CARRIERE_MINIMALE,
    ANNEE_MAXIMALE,
    ANNEE_MINIMALE,
    ENFANTS_MAXIMUM,
    INDEXATIONS,
    LISSAGE_MAXIMUM,
    METIERS_MAXIMUM,
    PROFILS,
    PROJECTIONS,
    RELEVE_MAXIMUM,
    SANS_EMPLOI,
    POPULATIONS,
    RATTACHEMENTS,
    TABLES,
    ErreurSaisie,
    Saisie,
)
from retraite_notionnelle.contexte import Contexte, Montants
from retraite_notionnelle.web.site import disponible, module, rendre, site
from outils_web import (
    FEUILLE_DE_STYLE, PAGES_AGREGEES, SIMULATION_TEMOIN, TITRES, _hors_depliants,
    _prose, contexte, g, page, pages,
)


#: Le site, en JavaScript : ses pages et ses modules se lisent par node
#: (``web/site.py``), le Python ne les rendant plus depuis la phase 8. Sans
#: node, rien du site ne se lit, et ses tests sont sautés.
pytestmark = pytest.mark.skipif(not disponible(),
                                reason="node absent : le site ne se lit pas sans lui")


# -- la revue du 15 septembre 2026 : le thème « expérience utilisateur » --------


def test_le_glossaire_ne_porte_aucun_chiffre_qui_bouge():
    """Une définition ne porte aucun montant qui dériverait.

    Un plafond, une durée requise, un taux de décote y vieilliraient sans que
    rien ne les recoupe. Les seuls nombres admis sont ceux d'un exemple ou
    d'une date. La table n'est écrite qu'une fois, dans le gabarit du site ;
    elle était recopiée dans le rendu Python, et un test comparait les deux
    copies, jusqu'à ce que la phase 8 retire la seconde.
    """
    for terme, definition in g.GLOSSAIRE.items():
        assert not re.search(r"\d[\d\u202f]{3,}\s*€", definition), (
            f"« {terme} » : un montant en euros dans une définition"
        )


def test_le_jargon_du_relecteur_porte_sa_definition():
    """Les mots que la revue extérieure relevait comme non définis.

    Chacun est un mot du glossaire là où il paraît : sur les résultats du
    simulateur pour le taux de remplacement, le coefficient de conversion, le
    capital notionnel et l'âge de référence ; dans le formulaire, sous un
    point d'interrogation, pour le statut d'affiliation, la table de
    conversion et l'âge de référence ; sur l'accueil pour les trimestres, la
    décote, la surcote et le salaire de référence.
    """
    def termes(corps: str) -> set[str]:
        return set(re.findall(
            r'<span class="terme" role="button" tabindex="0" aria-expanded="false">(.*?)</span>',
            corps,
        ))

    def bulles(corps: str) -> str:
        return " ".join(re.findall(r'<span class="bulle" role="note" hidden>(.*?)</span>',
                                   corps))

    resultats = rendre("/simuler", SIMULATION_TEMOIN)[1]
    assert {"taux de remplacement", "coefficient de conversion",
            } <= termes(resultats)
    assert any(mot.startswith("capital notionnel") for mot in termes(resultats))
    # L'appel d'une bulle porte son texte tel quel — c'est du HTML de phrase —,
    # là où le mot du glossaire échappe le sien.
    for cle in ("statut d'affiliation", "table de conversion",
                "part patronale", "indexation"):
        assert g.GLOSSAIRE[cle] in bulles(resultats), cle

    accueil = rendre("/", {})[1]
    assert {"trimestres", "décote", "surcote", "taux plein", "répartition",
            "25 meilleures années"} <= termes(accueil)
    cout = rendre("/cout", {})[1]
    assert {"répartition", "part du PIB", "comptes notionnels",
            "taux de remplacement"} <= termes(cout)
    assert "réglage annuel" in termes(rendre("/cas-types", {})[1])

# L'âge de référence ne se règle plus, et sa note n'existe plus : la
# conversion des droits acquis était propre aux deux variantes « dès la
# bascule », que le site ne compare plus depuis qu'il est passé à quatre
# systèmes. Le MODÈLE la calcule toujours — voir tests/test_simulateur.py —,
# mais aucune page ne la montre, et il n'y a donc plus rien à vérifier ici.


def test_le_menu_des_statuts_est_groupe_par_famille(page):
    """Soixante-deux options à la file ne se parcourent pas.

    Le menu du premier métier range les statuts sous un ``<optgroup>`` par
    famille, dans l'ordre de ``FAMILLES_STATUT`` ; celui des périodes
    suivantes y ajoute le groupe des périodes sans emploi, en dernier. Chaque
    option reste une option : le script qui grise les statuts fermés les
    parcourt par ``menu.options``, que les groupes ne cachent pas.
    """
    from retraite_notionnelle.carriere import FAMILLES_STATUT

    texte = page("/simuler")
    premier = re.search(r'<select id="statut".*?</select>', texte, re.S).group(0)
    groupes = re.findall(r'<optgroup label="([^"]+)">', premier)
    assert groupes == list(FAMILLES_STATUT.values())
    assert premier.count("<option") == 67
    sncf = re.search(r'<optgroup label="Régimes spéciaux">(.*?)</optgroup>', premier).group(1)
    assert 'value="agent_sncf"' in sncf
    prive = re.search(r'<optgroup label="Salariés du privé">(.*?)</optgroup>', premier).group(1)
    assert 'value="salarie_prive_non_cadre"' in prive

    second = re.search(r'<select id="metier2_statut".*?</select>', texte, re.S).group(0)
    assert re.findall(r'<optgroup label="([^"]+)">', second)[-1] == "Sans emploi"
    assert second.startswith('<select id="metier2_statut" name="metier2_statut">'
                             '<option value="" selected>— aucun —</option><optgroup')


def test_la_page_cas_types_ouvre_sur_la_proposition():
    """Le lecteur pressé s'arrêtait sur un contrefactuel.

    Les cinq grilles sont derrière des onglets — des boutons radio, un
    panneau par scénario —, et l'onglet coché à l'ouverture est le scénario
    6. Les quatre autres panneaux sont dans la page, ``hidden`` : là où
    ``:has()`` manque, la page montre le premier et cache les autres.
    """
    corps = rendre("/cas-types", {})[1]
    radios = re.findall(r'<input type="radio" name="grille" id="grille-([^"]+)"( checked)?>',
                        corps)
    assert [code for code, _ in radios] == [
        "notionnel_liberal", "notionnel_retroactif",
        "notionnel_retroactif_employeur",
    ]
    assert [bool(coche) for _, coche in radios] == [True, False, False]
    panneaux = re.findall(r'<div class="panneau" data-onglet="([^"]+)"( hidden)?>', corps)
    assert [code for code, _ in panneaux] == [code for code, _ in radios]
    assert [bool(cache) for _, cache in panneaux] == [False, True, True]
    # Chaque radio porte son libellé, et le premier dit ce qu'il est.
    assert '<label for="grille-notionnel_liberal">4. La proposition</label>' in corps
    # La feuille de style sait montrer chacun des trois panneaux.
    for code, _ in radios:
        assert f'.onglets:has(#grille-{code}:checked) ~ .panneaux > .panneau[data-onglet="{code}"]' in FEUILLE_DE_STYLE, code
    # Et les trois chiffres d'ouverture sont lus sur cette grille-là.
    assert "génération 2000, système 4" in corps


#: Les tournures où un nombre écrit en toutes lettres NE compte pas les
#: systèmes. Sans cette liste, le contrôle ci-dessous se déclencherait sur des
#: phrases justes : un indice qui vaut « près de cinq fois les prix » n'a rien
#: à voir avec le nombre de systèmes comparés.
COMPTES_LEGITIMES = (
    "fois les prix",
)


@pytest.mark.parametrize("chemin", list(TITRES))
def test_aucune_page_ne_compte_plus_de_quatre_systemes(chemin):
    """Le site en compare QUATRE, et doit le dire partout de la même façon.

    Passer de six à quatre a touché cinquante-deux phrases. Les tests de
    structure en ont rattrapé la plupart, et une première version de celui-ci a
    rattrapé « Six calculs pour votre carrière ». Il cherchait des mots — « six
    systèmes », « six montants » — et il a donc laissé passer exactement ce
    qu'il ne cherchait pas : le TITRE de la page Simuler, « Votre carrière,
    calculée six fois », que l'auteur du site a vu avant lui. Plus la carte à
    publier, qui portait la même phrase et qui voyage sans le site autour
    d'elle.

    Il ne cherche donc plus des tournures connues, mais TROIS FORMES :

    * un numéro de système au-delà de quatre, qui n'a plus de référent ;
    * un décompte en toutes lettres suivi d'un mot qui désigne les systèmes ;
    * « calculée N fois » ou « calculée de N façons », quel que soit N.

    Le compte du MODÈLE n'est pas visé : il en calcule toujours six, et les
    commentaires du code le disent. Ce test ne lit que ce qui s'affiche, sur
    les huit routes — c'est là que vivaient les deux phrases fausses.
    """
    corps = rendre(chemin,
                   {"naissance": "1975-01-01"}
                   if chemin == "/simuler" else {})[1]
    texte = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", corps)))

    def fautes(motif: str) -> list[str]:
        # La tournure légitime se reconnaît à ce qui SUIT le nombre — « cinq
        # fois les prix » —, donc sur la fenêtre, pas sur la correspondance,
        # qui s'arrête au mot compté.
        trouvees = []
        for t in re.finditer(motif, texte, re.I):
            fenetre = texte[t.start():t.end() + 24]
            if any(bon in fenetre for bon in COMPTES_LEGITIMES):
                continue
            trouvees.append(texte[max(0, t.start() - 50):t.end() + 50])
        return trouvees

    numeros = fautes(r"\b(?:systèmes?|scénarios?) [5-9]\b")
    assert not numeros, f"{chemin} : un numéro au-delà de quatre — {numeros}"

    decomptes = fautes(
        r"\b(?:cinq|six|sept|huit|neuf) "
        r"(?:systèmes?|scénarios?|calculs?|montants?|courbes?|barres?|façons?|fois)\b"
    )
    assert not decomptes, f"{chemin} : un décompte périmé — {decomptes}"

    calculees = fautes(r"calculées? (?:de )?(?!quatre)\w+ (?:fois|façons)")
    assert not calculees, f"{chemin} : « calculée » mal comptée — {calculees}"



def test_une_classe_du_bloc_scenario_ne_reprend_pas_un_composant():
    """Une classe du bloc des scénarios ne doit pas être stylée SANS ANCÊTRE.

    La ligne qui décompose le montant de la proposition s'était appelée
    `partage`. Ce nom était déjà celui de la barre de boutons de partage, dont
    la règle — sans ancêtre, donc applicable partout — porte un filet or de
    3 px sur toute la largeur : le filet est venu se tirer en travers du bloc,
    entre le montant et sa barre, et rien dans le HTML ne l'expliquait. La
    règle était à six cents lignes de là, dans un composant sans rapport.

    Le discriminant est exactement celui-là : une classe stylée sous un ancêtre
    (`.engagements .chiffre`) ne peut pas descendre ici, une classe stylée nue
    (`.partage`) le peut. `barre` fait exception, et c'est voulu : c'est le
    composant que le bloc emploie, pas un nom qu'il lui reprend.
    """
    import re

    feuille = re.sub(r"/\*.*?\*/", "", FEUILLE_DE_STYLE, flags=re.S)
    selecteurs = [
        " ".join(morceau.split())
        for tete in re.findall(r"(?:^|\})\s*([^{}@][^{}]*?)\{", feuille, re.S)
        for morceau in tete.split(",")
    ]
    for classe in ("entete", "titre", "montant", "chiffre", "somme", "unite",
                   "annuel", "glose", "composition", "capitalise"):
        nues = [s for s in selecteurs if re.match(rf"^\.{classe}\b", s)]
        assert not nues, (
            f".{classe} est stylée sans ancêtre par {nues} : la règle "
            "s'appliquera aussi dans le bloc des scénarios, qui pose cette "
            "classe, sans que rien ne le montre à la lecture du HTML"
        )


def test_les_pages_longues_portent_leur_plan():
    """Un plan déduit des sections, et qui les ouvre sans toucher à la route.

    Coût et Données listent, sous leurs trois chiffres, chaque carte et chaque
    section repliée qu'elles contiennent ; chaque lien porte la route de la
    page et l'identifiant de la section, et la section porte cet identifiant.
    Les autres pages, courtes, n'ont pas de plan.
    """
    for chemin, attendus in (
        ("/cout", ["cout-bilan", "cout-provenance", "cout-flux", "cout-depenses",
                   "cout-ressources",
                   "cout-transferts", "cout-scenarios", "cout-cascade",
                   "cout-equilibre", "cout-postes",
                   "cout-dette",
                   "cout-frise", "cout-garantie", "cout-capitalisation", "cout-poids", "cout-sources",
                   "cout-limites"]),
    ):
        corps = rendre(chemin, {})[1]
        plan = re.search(r'<nav class="plan" aria-label="Dans cette page">.*?</nav>', corps, re.S)
        assert plan, f"{chemin} : pas de plan"
        liens = re.findall(r'<a href="([^"]+)" data-vers="([^"]+)">', plan.group(0))
        assert [vers for _, vers in liens] == attendus
        assert {href for href, _ in liens} == {g.lien(chemin)}
        for identifiant in attendus:
            assert f' id="{identifiant}"' in corps, identifiant
        # Le plan vient APRÈS les trois chiffres : le résultat d'abord, la
        # carte ensuite.
        assert corps.index('<div class="fiches reperes">') < corps.index('<nav class="plan"')
    for chemin in ("/", "/cas-types", "/methode", "/simuler"):
        assert '<nav class="plan"' not in rendre(chemin, {})[1], chemin

    from pathlib import Path

    page_html = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
    assert 'closest("a[data-vers]")' in page_html and "noeud.open = true" in page_html


def test_l_inventaire_est_une_table_qui_se_filtre_et_se_trie(contexte):
    """Quatre-vingt-neuf régimes en cinq tableaux de prose ne se cherchaient
    qu'au Ctrl+F.

    Une seule table, chaque ligne portant sa famille et sa couverture en
    ``data-``, un champ de recherche et deux menus devant elle, des en-têtes
    qui sont des boutons de tri. Sans script, elle se lit entière.
    """
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.donnees.regimes import charger_inventaire

    corps = rendre("/methode", {})[1]
    lignes = charger_inventaire(RACINE_DONNEES)
    table = re.search(r'<table id="inventaire">.*?</table>', corps, re.S).group(0)
    rangs = re.findall(r'<tr data-famille="([^"]+)" data-couverture="([^"]+)" data-fiabilite="[^"]*">', table)
    assert len(rangs) == len(lignes)
    assert [famille for famille, _ in rangs] == [l.famille for l in lignes]
    assert table.count('<button type="button" class="tri"') == 7
    assert 'data-cible="inventaire"' in corps
    assert 'id="inventaire-recherche"' in corps and 'data-filtre="texte"' in corps
    assert 'id="inventaire-famille"' in corps and 'id="inventaire-couverture"' in corps
    assert (f'data-compte-de="inventaire" data-unite="régimes">{len(lignes)} régimes</p>'
            in corps)
    # Une couverture qu'aucune ligne ne porte n'est pas proposée au filtre, et
    # chacune de celles que l'inventaire porte l'est.
    selecteur = re.search(r'<select id="inventaire-couverture".*?</select>', corps, re.S).group(0)
    proposees = set(re.findall(r'<option value="([^"]+)"', selecteur))
    assert proposees == {ligne.couverture for ligne in lignes}
    # La fiabilité de chaque fiche calculée est dans la ligne du régime.
    catalogue = {r.code: str(r.fiabilite) for r in contexte.simulateur().catalogue}
    for ligne in lignes:
        if ligne.couverture in ("modelise", "partiel"):
            assert ligne.code in catalogue, ligne.code
    assert ">certifiee<" in table or ">haute<" in table
    # Et l'inventaire ne s'impose toujours pas : il reste replié. Depuis que
    # Sources est la fin de la page Méthode, un tableau y est ouvert — celui
    # des règles d'indexation, qui est la réponse de Méthode —, mais pas lui.
    assert '<table id="inventaire">' not in _hors_depliants(corps)

    from pathlib import Path

    page_html = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
    assert 'closest?.(".filtres[data-cible]")' in page_html
    assert 'closest("th > button.tri")' in page_html and 'setAttribute("aria-sort"' in page_html


def test_aucun_chemin_de_fichier_n_est_cite_en_texte_brut():
    """« docs/limites.md » se lisait sans qu'on puisse l'ouvrir : chaque renvoi
    à un document du dépôt est un lien vers ce document."""
    for chemin in TITRES:
        corps = rendre(chemin, {})[1]
        for cite in re.findall(r"<code>(docs/[^<]+|scripts/[^<]+|data/[^<]+)</code>", corps):
            assert False, f"{chemin} : « {cite} » cité en texte brut"


# -- la revue du 15 septembre 2026 : le thème « clarté des arguments » ----------


def test_la_cle_de_lecture_des_cas_types_precede_les_chiffres():
    """Le scénario 6 affiche des écarts rouges : la clé dit contre quoi ils se lisent.

    La clé était sur la page Coût ; elle est en tête de Cas types, AVANT les
    trois chiffres d'ouverture et les grilles, et dit de quel côté de un se
    trouve le réglage annuel de la proposition. Elle renvoie à la section de
    Coût qui le chiffre.

    Elle a ouvert sur « ces pourcentages ne sont pas des baisses de pension »
    jusqu'au 23 septembre 2026, jour où l'accueil s'est mis à dire l'ordre de
    grandeur de la baisse, lu sur cette même grille. Elle dit désormais contre
    quoi ils se lisent — la promesse du système actuel —, et ne peut plus
    démentir, un clic plus loin, ce que l'accueil affirme.
    """
    corps = rendre("/cas-types", {})[1]
    cle = corps.index("Ces pourcentages se lisent contre une")
    assert cle < corps.index('<div class="fiches reperes">')
    assert cle < corps.index('<div class="panneaux">')
    assert "Pour la proposition, ce facteur est " in corps
    assert 'data-vers="cout-equilibre"' in corps
    assert "Ces pourcentages se lisent contre une" in _hors_depliants(corps)
    assert "ne sont pas des baisses" not in corps


def _reglage_proposition_attendu(contexte):
    """Le coefficient de la proposition, recalculé ici sans passer par la page."""
    solde = contexte.cout().solde
    debut, fin = solde.premiere_annee_projetee, solde.derniere_annee
    coefficients = {annee: solde.annee(annee).coefficient("notionnel_liberal")
                    for annee in range(debut, fin + 1)}
    annee_minimum = min(coefficients, key=coefficients.get)
    return debut, fin, coefficients, annee_minimum


def test_cas_types_dit_du_reglage_ce_que_le_solde_dit(contexte):
    """La phrase de Cas types se calcule ; elle ne s'écrit plus.

    Le 19 septembre 2026 au soir, la page affirmait en texte fixe que le
    coefficient d'équilibre de la proposition « est supérieur à un chaque
    année ». Le 20 au matin, quatre changements du modèle de coût l'avaient
    fait passer sous un sur les quarante-cinq années projetées, et la page
    Coût du même site le chiffrait à 0,92 en 2070 pendant que Cas types
    promettait une marge. Le parcours de présentation demandait de lire la
    phrase à voix haute. Ce test lit le solde, en déduit la phrase attendue,
    et exige que Cas types et Coût la portent toutes les deux.
    """
    debut, fin, coefficients, annee_minimum = _reglage_proposition_attendu(contexte)
    sous_un = sum(1 for c in coefficients.values() if c < 1.0)
    cas_types = rendre("/cas-types", {})[1]
    cout = rendre("/cout", {})[1]
    minimum = g.nombre(coefficients[annee_minimum], 2)
    dernier = g.nombre(coefficients[fin], 2)

    if sous_un == 0:
        assert (f"supérieur à un sur chacune des années projetées, de {debut} à {fin}"
                in cas_types)
        assert "Un coefficient supérieur à un est une marge" in cas_types
        assert "inférieur à un" not in cas_types
        assert f"Les {dernier} de la proposition en {fin} disent une marge" in cout
    elif sous_un == len(coefficients):
        # Sous un partout, le dernier aussi s'écrit sans 1,00, comme le plus
        # bas : la proposition peut finir tout près de un.
        precis = g.nombre(coefficients[annee_minimum],
                          pages.decimales_sous_un(coefficients[annee_minimum]))
        dernier = g.nombre(coefficients[fin], pages.decimales_sous_un(coefficients[fin]))
        assert f"inférieur à un de {debut} à {fin}" in cas_types
        assert f"{precis} au plus bas en {annee_minimum}" in cas_types
        assert f"{dernier} en {fin}" in cas_types
        assert "Un coefficient inférieur à un est un manque" in cas_types
        assert "supérieur à un chaque année" not in cas_types
        assert f"Les {dernier} de la proposition en {fin} disent un manque" in cout
        assert f"son plus bas, {minimum} en {annee_minimum}" in cout
    else:
        # Assez de décimales pour qu'un plus bas sous un ne s'écrive pas 1,00 :
        # c'est le cas depuis la TVA à taux unique, 0,999 en 2044.
        precis = g.nombre(coefficients[annee_minimum],
                          pages.decimales_sous_un(coefficients[annee_minimum]))
        assert f"inférieur à un {sous_un} années sur {len(coefficients)}" in cas_types
        assert f"{precis} en {annee_minimum}" in cas_types
        assert f"{dernier} en {fin}" in cas_types
        assert f"son plus bas, {precis} en {annee_minimum}" in cout
    # Et dans aucun cas la page ne lit plus un coefficient comme une économie.
    assert "comme\nune économie" not in cout
    assert "Le coefficient se lit dans les deux sens" in cout


def test_le_README_donne_le_solde_que_la_page_cout_calcule(contexte):
    """Le tableau du README (section « Un coût n'est pas un solde ») est celui
    de la page Coût, ligne par ligne.

    Il a été faux plusieurs jours de suite : −1,93 % et 0,89 pour la
    proposition quand le site affichait −1,52 % et 0,92, et 1,87 pour le
    scénario 3 deux paragraphes après un tableau qui disait 1,64. La section
    est devenue une zone `etat` de `zones.yaml`, et ses nombres portent une
    ancre que la sonde `mesure` recalcule ; ce test reste, parce qu'il
    confronte le README à la PAGE et non au modèle — deux chemins qui
    pourraient diverger. Il lit les nombres sous leurs ancres.
    """
    from pathlib import Path

    from retraite_notionnelle.cout import SCENARIOS

    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
    solde = contexte.cout().solde
    # Le PIB par lequel la page convertit une part en milliards : celui des
    # comptes du site, que sa règle lit.
    comptes = site().contexte.comptes()
    observe = solde.annee(solde.derniere_annee_observee)
    horizon = solde.annee(solde.derniere_annee)

    # Les deux soldes se lisent en part du PIB ET en milliards, sur la page
    # (« −0,17 % · −5,1 Md € ») comme dans le README (« −0,17 % du PIB,
    # −5,1 Md€ ») : la normalisation efface la seule différence, la typographie.
    def normaliser(texte: str) -> str:
        texte = re.sub(r"<!--.*?-->", "", texte)
        return (texte.replace("**", "").replace("−", "-").replace(" du PIB", "")
                .replace("\u202f", " ").replace("\u00a0", " ")
                .replace(" \u00b7 ", ", ").replace("Md €", "Md€").strip())

    for numero, (scenario, _libelle) in enumerate(SCENARIOS, start=1):
        ligne = re.search(rf"^\| {numero}\. [^|]*\|([^|]*)\|([^|]*)\|([^|]*)\|$",
                          readme, re.M)
        assert ligne, f"le README n'a plus de ligne {numero} dans le tableau des soldes"
        moyen = solde.solde_moyen(scenario, solde.premiere_annee_projetee,
                                  solde.derniere_annee)
        attendu = [
            pages._part_et_milliards(
                observe.solde(scenario),
                observe.solde(scenario) * pages._pib_de_conversion(comptes, observe.annee),
                decimales=2, signe=True),
            pages._part_et_milliards(
                moyen, moyen * pages._pib_de_conversion(comptes, solde.derniere_annee),
                decimales=2, signe=True),
            g.nombre(horizon.coefficient(scenario), 2),
        ]
        assert [normaliser(c) for c in ligne.groups()] == [normaliser(a) for a in attendu], (
            f"ligne {numero} du README : {ligne.groups()} ; la page Coût dit {attendu}")

    coefficient_3 = g.nombre(horizon.coefficient("notionnel_prospectif"), 2)
    economie_3 = g.pourcentage(1 - 1 / horizon.coefficient("notionnel_prospectif"), decimales=0)
    assert normaliser(
        f"Lire les {coefficient_3} du\nscénario 3 en {solde.derniere_annee} comme "
        f"une économie de {economie_3}") in normaliser(readme), (
        "la phrase du README sur le scénario 3 ne dit plus ce que dit le tableau")


def test_les_comparaisons_rappellent_que_le_systeme_actuel_derive(contexte):
    """« Aujourd'hui » n'est pas un point fixe, et les tableaux le disent.

    Cas types sous ses grilles, Coût dans la section des six systèmes : le
    solde du système actuel, observé puis projeté par le COR, est écrit à côté
    de la comparaison, avec les deux années. Les nombres viennent des comptes,
    pas d'une constante.
    """
    comptes = contexte.comptes()
    obs = comptes.derniere_annee_observee
    horizon = comptes.derniere_annee
    attendu_obs = g.pourcentage(-comptes.solde(obs), decimales=2)
    attendu_horizon = g.pourcentage(-comptes.solde(horizon), decimales=2)
    assert horizon > obs + 20, "les comptes ne portent plus la projection"

    cas_types = rendre("/cas-types", {})[1]
    rappel = re.search(r"« Aujourd'hui » n'est pas un point fixe.*?</p>",
                       cas_types, re.S)
    assert rappel, "Cas types ne rappelle plus la trajectoire du système actuel"
    assert f"{attendu_obs} du PIB en {obs}" in rappel.group(0)
    assert f"{attendu_horizon} en {horizon}" in rappel.group(0)
    assert "système\nqui dérive" in rappel.group(0)
    assert rappel.start() > cas_types.index('<div class="panneaux">')

    cout = rendre("/cout", {})[1]
    assert "comparer un scénario à lui, c'est le\ncomparer à un système qui dérive" in cout
    assert f"{attendu_obs}\ndu PIB en {obs}" in cout


def test_chaque_tableau_de_scenarios_distingue_proposition_et_contrefactuel():
    """Un badge là où l'erreur de lecture se produit, non dans un préambule.

    Sur Cas types, chaque panneau porte le sien dans son titre ; sur Coût, les
    quatre tableaux qui alignent les systèmes le portent en tête de ligne.
    Le système actuel n'en a pas : c'est la référence.
    """
    cas_types = rendre("/cas-types", {})[1]
    titres = re.findall(r'<div class="panneau" data-onglet="([^"]+)"[^>]*><h3>.*?'
                        r'<span class="badge (\w+)">', cas_types)
    assert titres == [("notionnel_liberal", "proposition")] + [
        (code, "contrefactuel") for code in ("notionnel_retroactif",
                                             "notionnel_retroactif_employeur")]

    cout = rendre("/cout", {})[1]
    lignes = re.findall(r'<th class="" scope="row">(\d)\. [^<]*(?:<span class="badge (\w+)">)?',
                        cout)
    # Quatre tableaux à quatre lignes : le passé, l'avenir, l'équilibre, la
    # dette.
    assert lignes.count(("1", "")) == 4, lignes
    assert lignes.count(("4", "proposition")) == 4
    for numero in "23":
        assert lignes.count((numero, "contrefactuel")) == 4, numero
    assert ".badge.proposition" in FEUILLE_DE_STYLE


def test_les_pages_techniques_s_ouvrent_en_langage_courant():
    """Trois ou quatre phrases simples avant le détail, sur Coût, Méthode et
    Données — et elles se lisent sans rien déplier."""
    for chemin, phrase in (
        ("/cout", "ont coûté un peu plus qu&#x27;elles n&#x27;ont rapporté"),
        ("/methode", "Votre pension serait votre\ncompte divisé par le nombre d&#x27;années"),
    ):
        corps = rendre(chemin, {})[1]
        resume = re.search(r'<div class="note resume"><strong>En clair\.</strong>(.*?)</div>',
                           corps, re.S)
        assert resume, f"{chemin} : pas de résumé en langage courant"
        assert phrase in resume.group(0).replace("'", "&#x27;"), chemin
        texte = re.sub(r"<[^>]+>", "", resume.group(1))
        phrases = [p for p in re.split(r"(?<=[.!?])\s", texte.strip()) if p]
        assert 3 <= len(phrases) <= 5, f"{chemin} : {len(phrases)} phrases"
        if '<div class="fiches reperes">' in corps:
            assert resume.start() < corps.index('<div class="fiches reperes">'), chemin
        assert "En clair." in _hors_depliants(corps)
    # La partie « D'où viennent les chiffres » de Méthode et sources, qui a été
    # la page Sources, garde sa phrase en langage courant : elle est devenue
    # l'introduction de la partie, une page ne portant qu'un « En clair ».
    methode = rendre("/methode", {})[1]
    sources = methode[methode.index('<h2 id="sources" tabindex="-1">'):]
    assert "viennent des\ninstitutions qui les produisent" in sources
    assert methode.count("<strong>En clair.</strong>") == 1


def test_l_autocritique_de_la_page_cout_est_un_encart_de_vigilance():
    """La comparaison à la projection du COR est un gage de sérieux : elle est
    marquée comme un point de vigilance, non noyée dans un paragraphe."""
    corps = rendre("/cout", {})[1]
    encart = re.search(r'<div class="note vigilance"><strong>Point de vigilance : le '
                       r"modèle ne refait\nla projection du COR qu'à quelques points "
                       r"près\.</strong>(.*?)</div>", corps, re.S)
    assert encart, "le point de vigilance a disparu"
    texte = re.sub(r"\s+", " ", encart.group(1))
    assert "chez le COR" in texte and "dans le modèle" in texte
    assert ".note.vigilance" in FEUILLE_DE_STYLE


# -- action 29 : l'entrée, pour qui arrive du site du parti --------------------


def test_l_accueil_ouvre_sur_le_simulateur_avant_les_engagements():
    """Un visiteur doit savoir en dix secondes que le site est un simulateur,
    et où cliquer.

    Depuis la refonte en affiche, ce n'est plus un bloc qui dit « simulez » et
    renvoie ailleurs : c'est LE FORMULAIRE LUI-MÊME, court, en crème, posé sous
    le titre et avant les quatre engagements. La preuve est à hauteur de la
    promesse, et le premier écran ne demande plus de cliquer pour commencer.

    Il est hors de tout dépliant, il porte l'adresse du simulateur, et le
    rappel du bas de page reste. Dans le cadre que le site du parti ouvre sur
    cette page, le titre du simulateur est masqué par l'hôte : ce bloc est
    alors la seule chose qui dise « simulez »."""
    corps = rendre("/", {})[1]
    visible = _hors_depliants(corps)
    formulaire = visible.index('<form class="creme simulateur-court"')
    engagements = visible.index('<section class="engagements"')
    affiche = visible.index('<div class="affiche">')
    assert affiche < formulaire < engagements
    # Il soumet vers le simulateur, et ses champs sont ceux du grand
    # formulaire : c'est la même adresse qui les reçoit.
    entete = visible[formulaire:engagements]
    assert f'action="{g.lien("/simuler")}"' in entete
    assert "Et vous, ça donne combien" in entete
    # Les champs se lisent sur le corps brut : `_hors_depliants` vide les
    # menus déroulants de leurs options, et emporte l'attribut du `<select>`.
    brut = corps[corps.index('<form class="creme simulateur-court"'):]
    brut = brut[:brut.index("</form>")]
    for champ in ("naissance", "debut", "statut", "liquidation"):
        assert f'name="{champ}"' in brut, f"le champ {champ} manque"
    bouton = f'<a class="bouton" href="{g.lien("/simuler")}">'
    assert visible.count(bouton) == 1, "le rappel du bas de page a disparu"
    assert ".simulateur-court .grille" in FEUILLE_DE_STYLE


def test_le_formulaire_dit_que_l_exemple_est_rempli(page):
    """Qui arrive sur le formulaire peut calculer tout de suite : une ligne
    visible le dit, avant le premier champ, et sans rien annoncer de plus."""
    texte = page("/simuler")
    assert "L'exemple est déjà rempli" in texte
    assert texte.index("L'exemple est déjà rempli") < texte.index("Date de naissance")
    assert "Résultats" not in texte


def test_les_resultats_s_ouvrent_sur_le_resume_la_cle_puis_les_montants():
    """Sous « Résultats » : trois phrases qui répondent à la question de
    l'électeur, puis la clé qui dit ce qu'on regarde, puis les quatre montants,
    puis seulement les repères techniques. Dans l'ordre inverse, un téléphone
    montrait un coefficient de conversion et pas un euro ; sans le résumé, il
    montrait dix nombres et rien qui dise lesquels comparer.

    En net, demandé : la note de la CSG, que la page ne porte qu'en net, se lit
    sous les barres, et le brut est le défaut depuis le 4 octobre 2026."""
    corps = rendre("/simuler", {**SIMULATION_TEMOIN, "montants": "net"})[1]
    visible = _hors_depliants(corps)
    resultats = visible.index('id="resultats"')
    bref = visible.index('<section class="en-bref"', resultats)
    lecture = visible.index("Quatre calculs pour votre carrière", resultats)
    premier = visible.index('<div class="scenario">', lecture)
    reperes = visible.index('<div class="fiches">', resultats)
    assert bref < lecture < premier < reperes
    cle = visible[lecture:premier]
    assert "C'est la référence." in cle
    # La clé nomme la proposition, et dit ce que sont les deux autres : sans
    # cela, l'électeur comparait le 1 au 2, que personne ne propose.
    assert "Le système 4 est notre proposition." in cle
    assert "Les systèmes 2 et 3 ne sont pas des\npropositions" in cle
    assert "votre <strong>salaire</strong> pendant" in cle
    assert "la <strong>pension</strong> que le système promet" in cle
    # Le troisième chiffre est annoncé lui aussi : il est apparu sans que la
    # clé change, et elle a promis « deux chiffres par ligne » au-dessus de
    # trois pendant le temps d'une session.
    assert "ce qu'elles en paient\n<strong>vraiment</strong>" in cle
    # Le mode se lit dans la clé, et il vaut pour les TROIS chiffres : c'est
    # précisément ce que la bascule garantit, et ce que le site ne faisait pas
    # quand il opposait un salaire net à une pension brute.
    # Le mot du mode et l'unité sont sur deux lignes du gabarit : on compare
    # donc sur le texte aplati, comme le lecteur le lit.
    aplati = " ".join(cle.split())
    assert "en net tous les trois, par mois, en euros d'aujourd'hui" in aplati
    # Ce que la clé disait APRÈS les chiffres qu'elle annonçait — que le
    # troisième n'est pas une prévision, et la CSG que le net suppose — se lit
    # sous les barres, une fois qu'on sait de quoi il parle. La clé en était
    # deux fois plus longue.
    carte = " ".join(visible[premier:reperes].split())
    assert "n'est pas une prévision" in carte
    assert "le revenu fiscal de référence de votre foyer" in carte
    paragraphe = cle[:cle.index("</p>")]
    assert len(re.sub(r"<[^>]+>", " ", paragraphe).split()) < 90, (
        "la clé de lecture s'allonge de nouveau")


def _somme_affichee(texte: str) -> float:
    return float(texte.replace("\u202f", "").replace(",", "."))


def test_la_vue_des_resultats_est_a_l_euro():
    """« 2 795 € » dans « En bref », « 2 795,42 » sur la barre juste dessous :
    deux écritures du même nombre, relevées le 23 septembre 2026. Ce qui se
    lit sans rien déplier — les quatre barres, la ligne qui compose le
    système 4, ce que le salaire devient — est à l'euro. Le centime, que la
    caisse verse, reste dans les dépliants, là où l'on refait le calcul.
    """
    corps = rendre("/simuler", SIMULATION_TEMOIN)[1]
    visible = _hors_depliants(corps)
    au_centime = re.findall(
        r'\d,\d\d\u202f€|<span class="somme">[\d\u202f]+,\d\d<', visible)
    assert not au_centime, f"montants au centime sur la vue : {au_centime[:3]}"
    assert re.search(r"\d,\d\d\u202f€", corps), "le détail a perdu ses centimes"


def test_le_resume_des_resultats_redit_les_chiffres_des_barres():
    """« En bref » ne calcule rien : il redit, arrondis à l'euro, les montants
    que les barres affichent juste dessous — le système actuel, la
    proposition sans rien ajouter puis avec les points rendus, le salaire net.

    ET IL LE FAIT SYMÉTRIQUEMENT. Le manque de financement est écrit pour les
    deux systèmes, dans les mêmes mots et au même euro que sous leurs barres :
    le taire pour l'un flatterait l'autre (action 62). Les systèmes 2 et 3,
    étalons et non choix, n'y figurent pas.

    En net, demandé : le salaire que les barres affichent est alors le salaire
    net dont le résumé parle. Le brut, défaut depuis le 4 octobre 2026, est tenu
    à la fin, sur les pensions.
    """
    corps = rendre("/simuler", {**SIMULATION_TEMOIN, "montants": "net"})[1]
    bref = re.search(r'<section class="en-bref".*?</section>', corps, re.S).group(0)
    # Les blancs ORDINAIRES seuls sont repliés : `split()` couperait aussi
    # l'espace fine insécable des milliers, que les montants portent.
    texte = re.sub(r"[ \t\n]+", " ", re.sub(r"<[^>]+>", " ", bref))
    blocs = corps.split('<div class="scenario">')[1:]
    actuel, liberal = blocs[0], blocs[3]

    def principal(bloc: str) -> float:
        return _somme_affichee(re.search(
            r'class="chiffre principal">.*?<span class="somme">([^<]+)</span>',
            bloc, re.S).group(1))

    def euro(montant: float) -> str:
        return g.euros(montant)

    assert euro(principal(actuel)) in texte
    assert euro(principal(liberal)) in texte
    plancher = _somme_affichee(re.search(
        r"soit\s+([\d\u202f]+)\u202f€ par\s+mois sans rien ajouter",
        liberal).group(1))
    assert f"serait de {euro(plancher)} nets par mois" in texte
    assert f"jusqu'à {euro(principal(liberal))}" in texte
    # Les manques, au même euro que sous les barres, et dans les mêmes mots :
    # « Elle n'est pas entièrement financée », « Elle non plus ». Un système
    # que ses comptes financent n'en a pas, et le résumé ne lui en prête pas :
    # c'est le cas de la proposition depuis la TVA à taux unique.
    manques = {}
    for nom, bloc in (("actuel", actuel), ("liberal", liberal)):
        trouve = re.search(r"il manque ([^<]+) par mois", bloc)
        manques[nom] = trouve.group(1) if trouve else None
        if trouve:
            assert f"il manque {trouve.group(1)} par mois" in texte
    assert manques["actuel"], "le système actuel du témoin n'est pas financé"
    assert "Elle n'est pas entièrement financée" in texte
    assert ("Elle non plus n'est pas entièrement financée" in texte) == bool(
        manques["liberal"])
    # Le salaire net, celui que « Et pendant que vous cotisez » chiffre au même
    # euro.
    gain = _somme_affichee(re.search(
        r'<span class="ecart">\+([\d\u202f]+)\u202f€ par mois</span>',
        liberal).group(1))
    assert f"augmente de {euro(gain)} par mois" in texte
    # Ni le 2 ni le 3 : leurs montants ne sont pas dans le résumé.
    for bloc in blocs[1:3]:
        assert euro(principal(bloc)) not in texte
    # Le renvoi vers « qui paiera » vise un dépliant qui existe, sans toucher
    # à la route.
    assert 'data-vers="resultats-financement"' in bref
    assert 'id="resultats-financement"' in corps
    # En brut, le défaut : les mêmes pensions que les barres, dites brutes.
    en_brut = rendre("/simuler", SIMULATION_TEMOIN)[1]
    bref = re.search(r'<section class="en-bref".*?</section>', en_brut, re.S).group(0)
    texte = re.sub(r"[ \t\n]+", " ", re.sub(r"<[^>]+>", " ", bref))
    blocs = en_brut.split('<div class="scenario">')[1:]
    for bloc in (blocs[0], blocs[3]):
        assert euro(principal(bloc)) in texte
    assert "bruts par mois" in texte


def test_le_resume_dit_au_retraite_que_sa_pension_serait_recalculee():
    """La première question d'un retraité : « et la mienne ? ». L'étape 2 du
    programme y répond — les pensions liquidées avant la bascule sont
    recalculées sur ce qui a été cotisé —, et le résumé le dit dans ces mots,
    sans ligne de salaire.

    La pension qu'il y lit est celle qu'il touche AUJOURD'HUI, et c'est celle
    qu'il a saisie : 1 600 € bruts en 2026, et non 1 600 € en avril 2017. Le
    résumé disait « votre retraite était de », et donnait la pension du
    départ ramenée par les prix — ce que personne n'a jamais touché."""
    corps = rendre("/simuler", {
        "situation": "retraite", "saisie": "pension", "unite_revenu": "euros_mois",
        "naissance": "1955-03-01", "liquidation": "2017-04-01",
        "debut": "1975-09-01", "statut": "salarie_prive_non_cadre",
        "pension": "1600"})[1]
    bref = re.search(r'<section class="en-bref".*?</section>', corps, re.S).group(0)
    texte = re.sub(r"[ \t\n]+", " ", re.sub(r"<[^>]+>", " ", bref))
    assert "votre retraite est aujourd'hui de 1\u202f600\u202f€ bruts par mois" in texte
    assert "celle de votre départ, en avril 2017, revalorisée depuis" in texte
    assert "elle serait recalculée sur ce qui a été cotisé" in texte
    assert "Pendant que vous travaillez" not in texte


def test_le_retraite_lit_le_chemin_de_sa_pension_depuis_son_depart():
    """Le cas type de ``tests/test_revalorisation.py``, saisi sur le site : un
    non-cadre né en 1950, parti en janvier 2012. Sa pension de 2026 est
    1 821,75 € bruts par mois — celle de son départ, 1 502,73 €, menée par
    les treize revalorisations du régime général (×1,2215) et la valeur du
    point Agirc-Arrco (×1,1855), depuis celle de son départ, fixée en avril
    2011 (étape 138.20). Le dépliant refait ce chemin régime par régime, dit
    la tranche de 2020 — 1 573,32 € en décembre 2019, donc 1 % — et ce que la
    page affichait avant : la pension du départ ramenée par les prix,
    1 875,63 €, que ce retraité n'a jamais touchée."""
    corps = rendre("/simuler", {
        "situation": "retraite", "saisie_par": "revenu", "salaire": "0.8",
        "unite_revenu": "moyen", "naissance": "1950-01-01", "liquidation": "62",
        "debut": "20", "statut": "salarie_prive_non_cadre", "sexe": "H"})[1]
    debut = corps.index('id="resultats-aujourdhui"')
    bloc = corps[debut:corps.index("</details>", debut)]
    texte = re.sub(r"[ \t\n]+", " ", re.sub(r"<[^>]+>", " ", bloc)).replace("\u202f", " ")
    assert "Votre pension a pris effet en janvier 2012." in texte
    assert "385,12 € ×1,1855 456,56 €" in texte
    assert "1 117,61 € ×1,2215 1 365,18 €" in texte
    assert "Pension du système actuel 1 502,73 € ×1,2123 1 821,75 €" in texte
    assert "votre pension de départ vaudrait 1 875,63 € bruts par mois" in texte
    assert "Pour vous, 1 573,32 € en décembre 2019 : +1,0 %." in texte


def test_aucun_lien_ne_remplace_la_route_par_une_ancre():
    """Ici l'adresse EST la route : un lien « #resultats-financement » la
    remplaçait, et le routeur, ne reconnaissant aucune page, rendait
    l'accueil — le lecteur qui cliquait dans la clé de lecture perdait sa
    simulation. Tout lien interne vise une route ; une section se rejoint par
    ``data-vers``, que le script de la page traite sans toucher à l'adresse."""
    pages = [("/simuler", SIMULATION_TEMOIN)] + [(chemin, {}) for chemin in TITRES]
    for chemin, parametres in pages:
        corps = rendre(chemin, parametres)[1]
        ancres = re.findall(r'href="(#[^/"][^"]*)"', corps)
        assert not ancres, f"{chemin} : {ancres}"


def test_tout_lien_interne_mene_a_une_page_qui_existe():
    """Un lien vers « #/methode/ » ne mène pas à la page Méthode : le routeur
    ne connaît pas cette route, et rend l'accueil. Trois liens du site
    portaient cette barre de trop — vers Méthode depuis l'accueil et depuis
    les résultats, vers les sources depuis les résultats —, et l'électeur qui
    les suivait revenait au programme sans comprendre pourquoi."""
    pages = [("/simuler", SIMULATION_TEMOIN)] + [(chemin, {}) for chemin in TITRES]
    for chemin, parametres in pages:
        corps = g.entete(chemin) + rendre(chemin, parametres)[1]
        for cible in re.findall(r'href="#(/[^"?]*)', corps):
            assert cible in TITRES, f"{chemin} : lien vers {cible!r}, route inconnue"


def test_chaque_renvoi_vise_une_section_qui_existe():
    """``data-vers`` ouvre une section sans toucher à la route : une cible
    absente laisse le lien agir en lien ordinaire, et le lecteur arrive en
    haut d'une page au lieu de la section promise. La cible est cherchée sur
    la page que le lien désigne — la même, le plus souvent ; celle de Coût
    quand Carrières types renvoie au coefficient d'équilibre."""
    pages = [("/simuler", SIMULATION_TEMOIN)] + [(chemin, {}) for chemin in TITRES]
    rendues = {}
    for chemin, parametres in pages:
        corps = rendre(chemin, parametres)[1]
        rendues.setdefault(chemin, corps)
        for route, cible in re.findall(
                r'href="#(/[^"?]*)[^"]*" data-vers="([^"]+)"', corps):
            destination = corps if route == chemin else rendues.setdefault(
                route, rendre(route, {})[1])
            assert f'id="{cible}"' in destination, (
                f"{chemin} : section {cible!r} absente de {route}")


#: Les questions de l'accueil, dans l'ordre où elles s'y posent.
QUESTIONS_DE_L_ELECTEUR = (
    "Ma retraite va-t-elle baisser ?",
    "Je suis déjà à la retraite : qu'est-ce qui change pour moi ?",
    "Pourquoi changer de système ?",
    "Que deviennent mes trimestres et mes points ?",
    "À quel âge pourrai-je partir ?",
    "Qu'est-ce qui change sur ma fiche de paie ?",
    "Et les petites retraites ?",
    "Et si je meurs ? Et mon conjoint ?",
    "Mon argent sera-t-il placé en Bourse ?",
    "Et les fonctionnaires, les régimes spéciaux ?",
    "Comment passe-t-on d'un système à l'autre ?",
    "Combien cela coûte-t-il, et qui paie ?",
    "Ces chiffres sont-ils fiables ?",
)


#: Ce que chaque question de l'accueil range derrière sa réponse courte : le
#: titre du développement qui la traitait, jusqu'au 23 septembre 2026, dans
#: un second empilement de dépliants, « Pour aller plus loin ».
DEVELOPPEMENTS_DES_QUESTIONS = {
    "Pourquoi changer de système ?": "En quoi ce serait plus juste",
    "Qu'est-ce qui change sur ma fiche de paie ?": "Les impôts que nous supprimons",
    "Et les petites retraites ?":
        "Le plancher, et ce qu'il change pour les petites pensions",
    "Mon argent sera-t-il placé en Bourse ?": "La part capitalisée :",
    "Combien cela coûte-t-il, et qui paie ?":
        "Ce qui pouvait nous arrêter, et ce que nous en avons fait",
    "Ces chiffres sont-ils fiables ?": "Pourquoi ce site.",
}


def test_l_accueil_range_chaque_sujet_sous_une_seule_question():
    """« Même moi je m'y perds » (23 septembre 2026).

    L'accueil alignait deux piles de dépliants : onze questions de l'électeur,
    puis neuf « Pour aller plus loin » qui reprenaient les mêmes sujets dans la
    voix du programme — le plancher, la part capitalisée, le coût —, et vers
    lesquels chaque réponse courte renvoyait : vingt titres en deux voix. Il
    n'y a plus qu'une liste de treize questions : chaque développement est
    rangé derrière la réponse courte de la question qu'il traite, et les deux
    dépliants qui ne faisaient que redire sont partis — le calcul, que les
    trois gestes disent en clair, et un plan du site que le bandeau porte.
    """
    corps = html.unescape(rendre("/", {})[1])
    assert "Pour aller plus loin" not in corps
    depliants = re.findall(
        r'<details class="section"(?: id="[^"]+")?><summary>.*?<span>(.*?)</span>'
        r"</summary>(.*?)</details>", corps, re.S)
    # Une seule liste, faite de questions.
    assert [titre for titre, _ in depliants] == list(QUESTIONS_DE_L_ELECTEUR)
    reponses = dict(depliants)
    for question, developpement in DEVELOPPEMENTS_DES_QUESTIONS.items():
        assert developpement in reponses[question], (question, developpement)
        # La réponse courte vient d'abord, le développement ensuite.
        assert reponses[question].index("<p>") < reponses[question].index(
            developpement), question
    # Les trois gestes ne se disent qu'une fois : en clair, sous leur titre.
    assert corps.count("On inscrit</strong>") == 1
    assert corps.count("On revalorise</strong>") == 1


def test_l_accueil_repond_aux_questions_de_l_electeur(contexte):
    """L'électeur arrive avec ses questions, pas avec le plan du programme.

    Elles sont posées dans ses mots, après le tableau qui oppose les deux
    systèmes, chacune repliée sur sa réponse : la liste se parcourt du regard
    et ne coûte rien au budget de lecture. La première est celle qui coûte, et
    sa réponse dit ce que le simulateur montrera.
    """
    corps = rendre("/", {})[1]
    texte = html.unescape(corps)
    rangs = [texte.index(f"<span>{question}</span></summary>")
             for question in QUESTIONS_DE_L_ELECTEUR]
    assert rangs == sorted(rangs), "les questions ne sont plus dans l'ordre"
    assert texte.index("Le système actuel et notre programme") < rangs[0]
    assert rangs[-1] < texte.index("Vérifiez plutôt que de nous croire")
    # Repliées : aucune réponse ne se lit sans avoir ouvert sa question.
    visible = html.unescape(_hors_depliants(corps))
    assert "<h2>Vos questions</h2>" in visible
    for question in QUESTIONS_DE_L_ELECTEUR:
        assert question not in visible
    # La réponse à la première question ne se dérobe pas.
    assert ("Le plus souvent, elle sera plus basse que ce que le système "
            "actuel\npromet, de l'ordre ") in texte
    # Les montants de la garantie sont ceux des paramètres.
    base = contexte.base
    assert g.euros(base.garantie_vieillesse_mensuelle
                   + base.allocation_isolement_mensuelle) in texte


def _replier(texte: str) -> str:
    """Les blancs du HTML repliés, SAUF les espaces fines et insécables.

    ``str.split()`` les compte pour des blancs : « 31 % » avec son espace fine
    en devenait un autre texte que celui que la page écrit.
    """
    return re.sub(r"[ \t\n]+", " ", texte)


def test_l_accueil_dit_de_combien_la_retraite_baisse(contexte):
    """« Pour que les gens aient une idée de la baisse » (23 septembre 2026).

    L'accueil disait que la retraite serait le plus souvent plus basse, sans
    dire de combien. Il le dit à deux endroits, et au même chiffre : dans le
    tableau qui oppose les deux systèmes, OUVERT — c'est ce que le lecteur
    pressé voit —, et dans la réponse à la première question, qui détaille les
    trois écarts médians. Les chiffres sont ceux du bilan figé, écrits sans
    signe parce que la phrase dit « baisse » ; l'ordre de grandeur en toutes
    lettres est tiré des deux écarts de ce qu'on touche sans rien ajouter.
    """
    corps = rendre("/", {})[1]
    texte = _replier(html.unescape(corps))
    ecarts = contexte.bilan().ecarts
    assert ecarts is not None, "le bilan figé ne porte pas les écarts médians"
    ordre = pages._ordre_de_grandeur(site().contexte.bilan().ecarts)

    # Le tableau, sans rien déplier.
    visible = _replier(html.unescape(_hors_depliants(corps)))
    assert (f'<th class="" scope="row">Votre retraite</th><td class="texte">ce que '
            f'votre régime promet</td><td class="texte">{ordre} de moins, en '
            "médiane</td>") in visible

    # La réponse : l'ordre de grandeur en gras, puis les trois médianes.
    assert (f"<strong>Le plus souvent, elle sera plus basse que ce que le "
            f"système actuel promet, {ordre}.</strong>") in texte
    for ecart in (ecarts.a_venir, ecarts.a_venir_volontaire, ecarts.deja_liquidees):
        assert ecart < 0.0
        assert f"{g.pourcentage(-ecart, decimales=0)}" in texte
    assert (f"la baisse médiane est de {g.pourcentage(-ecarts.a_venir, decimales=0)} "
            "pour qui n'est pas encore à la retraite") in texte
    assert (f"la pension d'aujourd'hui baisse ainsi de "
            f"{g.pourcentage(-ecarts.deja_liquidees, decimales=0)} en médiane") in texte
    # La preuve est à un clic : la grille des carrières types.
    assert '<a href="#/cas-types">treize carrières types</a>' in texte


@pytest.mark.parametrize(("part", "mots"), [
    (0.24, "un quart"), (0.31, "un tiers"), (0.26, "un quart"),
    (0.48, "la moitié"), (0.05, "un dixième"), (0.9, "trois quarts"),
])
def test_une_part_se_dit_par_la_fraction_la_plus_proche(part, mots):
    assert pages._fraction_en_mots(part) == mots


def test_l_ordre_de_grandeur_elide_ce_qu_il_faut():
    """« d'un quart », mais « de la moitié » et « de deux cinquièmes »."""
    def ecarts(a_venir, deja, volontaire=None):
        """Les écarts du bilan, tels que le site les lit dans son paquet."""
        return module("bilan").EcartsFiges(dataclasses.asdict(EcartsFiges(
            a_venir=a_venir, a_venir_volontaire=a_venir if volontaire is None else volontaire,
            deja_liquidees=deja, cases_a_venir=1, cases_deja_liquidees=1)))

    assert pages._ordre_de_grandeur(ecarts(-0.31, -0.26)) == "de l'ordre d'un quart à un tiers"
    assert pages._ordre_de_grandeur(ecarts(-0.33, -0.34)) == "de l'ordre d'un tiers"
    assert pages._ordre_de_grandeur(ecarts(-0.5, -0.4)) == (
        "de l'ordre de deux cinquièmes à la moitié")
    # Les cinq points volontaires n'entrent pas dans l'ordre de grandeur.
    assert pages._ordre_de_grandeur(ecarts(-0.31, -0.31, volontaire=-0.05)) == (
        "de l'ordre d'un tiers")


def test_un_scenario_n_affiche_que_les_euros_de_l_annee_de_reference():
    """UNE PENSION par scénario, et dans une seule unité.

    Chaque ligne portait deux nombres pour la même grandeur : le pouvoir
    d'achat d'aujourd'hui, et la somme nominale du mois du départ — « 3 190,21 €
    par mois, en euros de 2039 ». Des euros d'une année que personne n'a en
    poche, qu'il fallait une légende pour distinguer des autres, et qui
    doublaient les quatre lignes de la comparaison.

    Ce que ce test interdit est donc la SECONDE UNITÉ, pas le second chiffre.
    Le salaire net que le système laisse pendant la carrière a le droit de se
    tenir à côté de la pension : c'est une autre grandeur, elle porte son
    étiquette, et c'est même ce qui sépare les quatre systèmes avant la
    retraite. Ce que les comptes du système FINANCENT de cette pension y a
    rejoint le salaire, pour la même raison et sous la même règle : une
    étiquette, et l'unité des autres.

    Une seule chose reste exigée — un seul `chiffre principal`, celui de la
    pension, et lui seul dans les euros de l'année de référence.
    """
    corps = rendre("/simuler", SIMULATION_TEMOIN)[1]
    depart = SIMULATION_TEMOIN["liquidation"][:4]
    for bloc in corps.split('<div class="scenario">')[1:]:
        entete = bloc.split('<div class="barre')[0]
        assert entete.count('class="chiffre principal"') == 1
        assert f"en euros de {depart}" not in entete
        # L'unité longue a quitté les cartes — deux mots suffisent sous chaque
        # nombre — et la clé de lecture la porte une fois pour toutes. Ce que
        # la carte doit dire, c'est le MODE, et le même pour TOUS ses chiffres :
        # le test compte donc les unités plutôt qu'il n'en fixe le nombre, et
        # exige qu'aucune ne s'écarte des autres.
        unites = re.findall(r'<span class="unite">([^<]*)</span>', entete)
        assert unites
        assert set(unites) == {"€ brut/mois"}
        # Le second chiffre, s'il est là, dit de quoi il parle : sans son
        # étiquette, deux nombres se toucheraient sans que rien ne les sépare.
        if 'class="chiffre salaire"' in entete:
            assert ">salaire</span>" in entete
            assert "€ brut/mois" in entete
        # Le troisième, de même : il dit ce que les comptes financent de la
        # pension promise, et il ne paraît que là où ils en financent moins
        # qu'elle. Sans son étiquette, il se lirait comme un montant de plus.
        if 'class="chiffre finance"' in entete:
            assert ">vraiment payé</span>" in entete
    assert "Deux fois le même montant" not in corps
    assert "grand chiffre" not in corps
    assert f"en euros de {depart}" not in corps.split('<div class="carte">')[0]
    assert ("en brut tous les trois, par mois, en euros d'aujourd'hui"
            in " ".join(corps.split()))


def test_le_salaire_net_se_lit_a_cote_de_chaque_pension():
    """Les quatre systèmes portent leur salaire net, et trois portent le même.

    C'est le propos : les systèmes 1, 2 et 3 ne changent pas ce qui est
    PRÉLEVÉ, seulement ce qui est porté au compte. Voir le même nombre trois
    fois puis un quatrième différent est ce qui le montre sans une phrase.
    L'écart n'est donc écrit que sur la ligne qui en a un.
    """
    corps = rendre("/simuler", SIMULATION_TEMOIN)[1]
    entetes = [bloc.split('<div class="barre')[0]
               for bloc in corps.split('<div class="scenario">')[1:]]
    assert len(entetes) == 4
    salaires = [re.search(r'class="chiffre salaire">\s*'
                          r'<span class="categorie">salaire</span>\s*'
                          r'<span class="somme">([^<]+)</span>', entete)
                for entete in entetes]
    assert all(salaires), "un scénario n'affiche pas son salaire net"
    montants = [s.group(1) for s in salaires]
    assert montants[0] == montants[1] == montants[2], (
        "les systèmes 1 à 3 prélèvent la même chose : leur salaire net doit "
        f"être le même, et vaut {montants[:3]}"
    )
    assert montants[3] != montants[0], (
        "le système 4 change le prélèvement : son salaire net doit différer"
    )
    # L'écart de SALAIRE, et lui seul : le troisième chiffre de chaque ligne
    # porte le sien — « il manque tant par mois » —, dans le même idiome et
    # sous la même classe. Les distinguer par le texte plutôt que par le
    # compte évite de faire échouer ce test-ci pour un manque de financement,
    # qui n'est pas son sujet.
    def _ecarts_de_salaire(entete: str) -> list[str]:
        return [texte for texte in re.findall(r'<span class="ecart">(.*?)</span>',
                                              entete, re.S)
                if "il manque" not in texte]

    assert len(_ecarts_de_salaire(entetes[3])) == 1
    assert sum(len(_ecarts_de_salaire(entete)) for entete in entetes[:3]) == 0


def test_le_tableau_du_plancher_est_en_haut_de_l_accueil():
    """L'argument le plus parlant du site — « 300 € et 1 500 € : 0 € aujourd'hui,
    500 € avec la garantie » — se lit sans rien déplier, avant le tableau qui
    oppose les deux systèmes, et n'est plus répété dans le dépliant."""
    corps = rendre("/", {})[1]
    visible = _hors_depliants(corps)
    assert "Ce que le plancher individualisé change, par mois" in visible
    # Des espaces insécables : « 1 500 / € » se coupait en deux sur un téléphone.
    # Les montants sont ceux du site, à espace fine insécable, depuis que les
    # deux colonnes sont calculées (23 septembre 2026).
    assert "\u202f€ et 1\u202f500\u202f€" in visible
    assert visible.index("300\u202f€ et 1\u202f500\u202f€") < visible.index("Le système actuel et notre programme")
    assert corps.count("<caption><span>Ce que le plancher individualisé change, par mois</span></caption>") == 1
    assert "Le tableau du haut de page le montre" in corps


# -- la revue du 15 septembre 2026 : le thème « architecture » -----------------


def test_la_navigation_met_l_electeur_d_abord():
    """Deux voix dans le bandeau : ce que l'électeur vient chercher, puis ce
    qui permet de le vérifier.

    Dix onglets de même poids ne disaient pas par où commencer, et six d'entre
    eux ne répondent qu'à qui veut vérifier. Les pages qui répondent aux
    questions de l'électeur — le programme, sa retraite, le coût, pourquoi
    changer — restent des onglets ; celles qui les prouvent passent derrière
    une étiquette qui SE VOIT, « Pour vérifier ». Les autres étiquettes restent
    dites aux synthèses vocales et sorties de l'écran, par `clip-path` et non
    par `display: none`.

    Les libellés disent ce qu'on trouve : « Avantages » se lisait comme les
    avantages de la réforme, « Risque » ne disait pas de quoi, « Trajectoire »
    et « Cas types » étaient des mots du modèle.
    """
    entete = g.entete("/cout")
    groupes = re.findall(r'<span class="(groupe(?: secondaire)?)"><span class="etiquette">(.*?)</span>'
                         r'(?:<button type="button" class="deplier"[^>]*>.*?</button>)?'
                         r'<span class="liens"(?: id="[^"]+")?>(.*?)</span></span>', entete)
    assert [(classe, etiquette) for classe, etiquette, _ in groupes] == [
        ("groupe", "L&#x27;essentiel"), ("groupe", "Faire connaître"),
        ("groupe secondaire", "Pour vérifier")]
    pages = [re.findall(r'href="([^"]+)"', liens) for _, _, liens in groupes]
    # « Le saviez-vous ? » rejoint Partager le 4 octobre 2026 : des cartes à
    # publier, ce qu'on fait APRÈS avoir lu, et non un cinquième onglet en tête.
    assert pages == [["#/", "#/simuler", "#/cout", "#/risque"],
                     ["#/partager", "#/saviez-vous"],
                     ["#/cas-types", "#/avantages", "#/methode"]]
    libelles = [re.findall(r">([^<]+)</a>", liens) for _, _, liens in groupes]
    assert libelles == [["Programme", "Simuler", "Coût", "Pourquoi changer"],
                        ["Partager", "Le saviez-vous ?"],
                        ["Carrières types", "Droits non cotisés",
                         "Méthode et sources"]]
    assert 'href="#/cout" aria-current="page"' in entete
    assert [chemin for chemin, _ in g.LIENS] == [
        "/", "/simuler", "/cout", "/risque", "/partager", "/saviez-vous",
        "/cas-types", "/avantages", "/methode"]
    # Le titre de chaque page est le libellé de son onglet : c'est lui que
    # l'onglet du navigateur affiche.
    assert dict(g.LIENS) == TITRES
    assert list(TITRES) == [chemin for chemin, _ in g.LIENS]
    # L'étiquette est masquée à l'œil, pas à l'oreille ; celle du groupe
    # secondaire, elle, se voit.
    assert "nav .etiquette" in FEUILLE_DE_STYLE
    etiquette = FEUILLE_DE_STYLE.split("nav .etiquette {")[1].split("}")[0]
    assert "clip-path" in etiquette and "display: none" not in etiquette, (
        "une étiquette en display:none quitte aussi l'arbre d'accessibilité"
    )
    visible = FEUILLE_DE_STYLE.split("nav .groupe.secondaire .etiquette {")[1].split("}")[0]
    assert "clip-path: none" in visible
    # L'onglet courant ne se signale pas QUE par la couleur : un soulignement
    # épais le marque, et `aria-current` l'annonce.
    actif = FEUILLE_DE_STYLE.split('nav a[aria-current="page"] {')[1].split("}")[0]
    assert "border-bottom-color" in actif


def test_les_adresses_des_pages_parties_menent_a_leur_contenu():
    """Huit pages au lieu de dix (23 septembre 2026) : « Cumul versé » redisait
    un dépliant des résultats, « Sources » est devenue la fin de Méthode.

    Leurs adresses restent valides — le site parent et des partages les
    portent — et rendent la page qui les a remplacées ; la section qui porte
    leur contenu existe sur cette page, et le routeur d'``index.html`` l'ouvre.
    """
    from pathlib import Path

    assert set(pages.ANCIENNES_ROUTES) == {"/trajectoire", "/donnees"}
    for ancienne, (page, section) in pages.ANCIENNES_ROUTES.items():
        assert ancienne not in TITRES and page in TITRES
        parametres = SIMULATION_TEMOIN if page == "/simuler" else {}
        titre, corps = rendre(ancienne, parametres)
        assert (titre, corps) == rendre(page, parametres), ancienne
        assert f'id="{section}"' in corps, (ancienne, section)

    racine = Path(__file__).resolve().parents[1]
    portage = (racine / "moteur" / "js" / "pages.js").read_text(encoding="utf-8")
    assert '"/trajectoire": ["/simuler", "cumul"],' in portage
    assert '"/donnees": ["/methode", "sources"],' in portage
    script = (racine / "index.html").read_text(encoding="utf-8")
    assert "ANCIENNES_ROUTES[route]" in script
    assert "if (section) { ouvrirSection(section); }" in script


def test_sur_un_telephone_le_groupe_pour_verifier_se_replie():
    """« Le menu sur téléphone occupe quatre lignes avant même le titre »
    (23 septembre 2026). Le groupe « Pour vérifier » en prenait deux à lui
    seul : il se replie derrière un bouton qui porte son nom et son état, à la
    suite des onglets, et la barre tient en deux rangées à 390 points.

    Le bouton n'existe qu'à l'écran étroit : au-delà, l'étiquette reste un
    texte et les liens restent sous les yeux. Il s'ouvre de lui-même quand la
    page courante est dans le groupe, pour que l'onglet courant se voie. Le
    basculement vit dans ``index.html``, en écoute déléguée : le bandeau est
    réécrit à chaque page, un gestionnaire posé sur le bouton partirait avec.
    """
    def bouton(chemin: str) -> str:
        entete = g.entete(chemin)
        trouves = re.findall(r'<button type="button" class="deplier"[^>]*>', entete)
        assert len(trouves) == 1, f"{chemin} : {len(trouves)} boutons de repli"
        cible = re.search(r'aria-controls="([^"]+)"', trouves[0]).group(1)
        assert f'<span class="liens" id="{cible}">' in entete
        return trouves[0]

    assert 'aria-expanded="false"' in bouton("/")
    assert 'aria-expanded="false"' in bouton("/cout")
    secondaires = dict(g.GROUPES_NAVIGATION)[g.GROUPE_SECONDAIRE]
    for chemin, _ in secondaires:
        assert 'aria-expanded="true"' in bouton(chemin), chemin

    style = FEUILLE_DE_STYLE
    assert "nav .deplier { display: none; }" in style
    etroit = style.split("@media (max-width: 48rem) {\n  nav .groupe.secondaire { display: contents; }")
    assert len(etroit) == 2, "le repli n'est plus réservé à l'écran étroit"
    assert 'nav .deplier[aria-expanded="false"] + .liens { display: none; }' in etroit[1]

    from pathlib import Path
    script = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
    assert 'closest?.("nav button.deplier")' in script
    assert 'bouton.setAttribute("aria-expanded", String(ouvrir));' in script


def test_les_pages_complementaires_se_renvoient_l_une_a_l_autre():
    """Programme, Méthode et Cas types se renvoient dans les deux sens.

    Programme renvoyait à Méthode et à Cas types ; rien ne revenait. Méthode
    renvoie désormais au programme et aux treize carrières, Cas types à la
    proposition. Le contrôle porte sur les six sens.
    """
    pages = {chemin: rendre(chemin, {})[1]
             for chemin in ("/", "/methode", "/cas-types")}
    for depuis, vers in (("/", "/methode"), ("/", "/cas-types"),
                         ("/methode", "/"), ("/methode", "/cas-types"),
                         ("/cas-types", "/methode"), ("/cas-types", "/")):
        assert f'href="{g.lien(vers)}"' in pages[depuis], f"{depuis} ne renvoie pas vers {vers}"
    assert "treize carrières types</a> montrent ce\nqu'elle déplace" in pages["/methode"]
    assert '<a href="#/">la proposition</a>' in pages["/cas-types"]


def test_la_methode_dit_comment_le_site_est_construit():
    """L'argument de confiance d'un public technique, sur la page Méthode.

    Un dépliant dit le modèle de référence, le portage sans bibliothèque, les
    témoins comparés, le paquet de données — sans un nombre de tests ni de
    témoins, qui dériveraient : le README les porte, et un test les recalcule.
    """
    corps = rendre("/methode", {})[1]
    section = re.search(r'<details class="section"><summary>.*?<span>Comment ce site est '
                        r'construit, et comment on le vérifie</span></summary>(.*?)</details>',
                        corps, re.S)
    assert section, "le dépliant de construction manque"
    dedans = section.group(1)
    for attendu in (f'href="{g.DEPOT}/tree/main/src"', "portage en JavaScript",
                    "comparées nombre par nombre", "chaque page est figée en témoin",
                    f'href="{g.DEPOT}/tree/main/tests"',
                    'href="#/methode" data-vers="sources"'):
        assert attendu in dedans, attendu
    assert not re.search(r"\b\d{3,} (?:tests|témoins|carrières)", dedans), (
        "un nombre de tests ou de témoins écrit à la main dériverait"
    )


def test_la_page_risque_chiffre_le_prelevement_depuis_le_modele(contexte):
    """Ce que la retraite prélève, recalculé ici plutôt que recopié.

    La page tient trois chiffres qui ne viennent d'aucune source extérieure :
    ce qu'un salarié du privé verse chaque mois pour sa retraite à trois
    niveaux de salaire, la part de la pension promise que ses propres
    cotisations ne financent pas, et le solde du système. Ce test les refait
    depuis le modèle et les cherche dans la page : un taux de cotisation qui
    change, un compte du COR mis à jour, et c'est ici que la phrase périmée
    apparaît.
    """
    from retraite_notionnelle.calendrier import MOIS_PAR_AN

    corps = rendre("/risque", {})[1]
    # La carrière de référence de la page, à ses trois niveaux de salaire,
    # simulée par le modèle.
    exemples = [contexte.simuler(Saisie(
        naissance=pages.NAISSANCE_RISQUE, statut="salarie_prive_non_cadre",
        debut=pages.DEBUT_RISQUE, liquidation=pages.LIQUIDATION_RISQUE,
        salaire=niveau, unite_revenu="moyen", demandee=True,
    )) for _, niveau in pages.NIVEAUX_RISQUE]

    # Les trois lignes du tableau des salaires, au centime.
    for comparaison in exemples:
        fiche = comparaison.remuneration.reference.droit_en_vigueur
        assert g.euros(fiche.retraite_totale / MOIS_PAR_AN) in corps
        assert g.euros(fiche.brut / MOIS_PAR_AN) in corps
    moyen = exemples[1]
    fiche_moyen = moyen.remuneration.reference.droit_en_vigueur
    verse = g.euros(fiche_moyen.retraite_totale / MOIS_PAR_AN)
    # Le chiffre de tête est celui du salaire moyen, et il est aussi dans le
    # chapeau de l'affiche : les deux doivent bouger ensemble.
    assert corps.count(verse) >= 3, verse
    # Au SMIC, la part du brut est plus faible qu'au salaire moyen : ce sont
    # les allègements généraux, et la page l'explique.
    parts = [c.remuneration.reference.droit_en_vigueur.retraite_totale
             / c.remuneration.reference.droit_en_vigueur.brut for c in exemples]
    assert parts[0] < parts[1] < parts[2]
    assert "allègements généraux compris" in corps

    # L'écart entre la promesse et ce que les cotisations financent.
    constants = moyen.coefficient_euros_constants
    promis = moyen.actuel.pension_annuelle * constants
    finance = moyen.notionnel_retroactif_employeur.pension_annuelle * constants
    assert finance < promis, "l'exemple ne montre plus d'écart à financer"
    assert g.pourcentage(1 - finance / promis, decimales=0) in corps
    assert g.pourcentage(finance / promis, decimales=0) in corps

    # Le solde, lu dans les mêmes comptes que la page Coût.
    solde = contexte.cout().solde
    horizon = solde.annee(solde.derniere_annee)
    assert g.pourcentage(
        -horizon.solde("actuel") / horizon.depense("actuel"), decimales=0) in corps
    assert f'scope="row">{solde.derniere_annee_observee} (observé)</th>' in corps


def test_la_page_risque_cite_le_COR_mot_pour_mot():
    """Les phrases du COR sont citées, pas résumées.

    Elles portent l'essentiel de l'argumentaire, et elles valent parce
    qu'elles viennent de l'institution qui projette : les paraphraser les
    affaiblirait, et les déformer serait pire. Ce test tient les citations à
    la lettre. Elles ont été relevées dans le rapport annuel de juin 2026.
    """
    corps = rendre("/risque", {})[1]
    # Sur la prose remise à plat : le gabarit coupe les lignes où il veut, et
    # une citation ne doit pas dépendre de l'endroit où elle est coupée.
    texte = _prose(corps)
    for citation in (
        "trois des quatre leviers étudiés",
        "présentent un caractère récessif",
        "renforcent les difficultés à financer les dépenses publiques autres "
        "que les retraites, à l'instar de l'école, la santé ou la sécurité",
        "54,6 % en 2025 à 45,3 % en 2070",
        "demeurerait durablement en besoin de financement",
        "qui conduit à abaisser le PIB par habitant",
    ):
        assert citation in texte, citation
    # Les deux blocs de citation sont des citations, et le HTML le dit.
    assert corps.count("<blockquote>") == 2


def test_la_page_risque_range_ses_sections_et_se_relie():
    """Le plan, l'ordre des sections, et les liens qui font le tour du site."""
    corps = rendre("/risque", {})[1]
    plan = re.search(r'<nav class="plan".*?</nav>', corps, re.S).group(0)
    assert re.findall(r'data-vers="([^"]+)"', plan) == [
        "risque-prelevement", "risque-promesse", "risque-salaire",
        "risque-croissance", "risque-pauvres", "risque-jeunes",
        "risque-evince", "risque-deja", "risque-objections",
        "risque-ailleurs", "risque-droit", "risque-sources",
    ]
    for chemin in ("/simuler", "/cout", "/"):
        assert f'href="{g.lien(chemin)}"' in corps, chemin
    assert f'href="{g.lien("/risque")}"' in rendre("/", {})[1]

    # La bibliographie est dans le dépôt, à l'adresse annoncée.
    from pathlib import Path
    assert f'href="{g.DEPOT}/blob/main/docs/risque_de_defaut.md"' in corps
    assert (Path(__file__).resolve().parents[1] / "docs" / "risque_de_defaut.md").exists()

    # La page reste un réquisitoire honnête : elle cite le travail qui
    # contredit sa propre thèse générationnelle, et elle refuse d'affirmer une
    # éviction que personne n'a démontrée.
    texte = _prose(corps)
    assert "cité contre notre propre thèse" in texte
    assert "il ne démontre pas un mécanisme" in texte
    # Aucune probabilité de défaut n'est inventée.
    assert not re.search(r"probabilité de \d", _prose(corps))


def test_la_page_donnees_se_lit_comme_une_base():
    """Deux tables filtrables et triables : l'inventaire, croisé par famille,
    couverture et fiabilité, et les séries certifiées, par niveau."""
    corps = rendre("/methode", {})[1]
    inventaire = re.search(r'<table id="inventaire">.*?</table>', corps, re.S).group(0)
    assert 'id="inventaire-fiabilite"' in corps and 'data-filtre="fiabilite"' in corps
    fiabilites = re.findall(r'data-fiabilite="([^"]*)"', inventaire)
    assert len(fiabilites) == inventaire.count("<tr ")
    assert {f for f in fiabilites if f} <= {"certifiee", "haute", "moyenne", "estimee"}
    assert any(fiabilites), "aucune fiche calculée ne porte sa fiabilité"

    series = re.search(r'<table id="series">.*?</table>', corps, re.S)
    assert series, "la table des séries n'est plus filtrable"
    assert 'data-cible="series"' in corps and 'id="series-recherche"' in corps
    assert 'data-filtre="niveau"' in corps
    assert series.group(0).count('<button type="button" class="tri"') == 5
    assert len(re.findall(r'<tr data-niveau="', series.group(0))) == series.group(0).count("<tr ")
    assert 'data-compte-de="series" data-unite="séries">' in corps

    from pathlib import Path

    page_html = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
    assert 'compte.dataset.unite' in page_html


def test_chaque_route_porte_sa_description():
    """Une méta-description par page, que le routeur pose comme il pose le
    titre."""
    from pathlib import Path

    DESCRIPTIONS = pages.DESCRIPTIONS
    assert set(DESCRIPTIONS) == set(TITRES)
    for chemin, description in DESCRIPTIONS.items():
        assert 60 <= len(description) <= 250, f"{chemin} : {len(description)} caractères"
        assert description.endswith("."), chemin
    racine = Path(__file__).resolve().parents[1]
    page = (racine / "index.html").read_text(encoding="utf-8")
    assert "DESCRIPTIONS[cible.chemin]" in page
    assert "description.content = " in page
    # La description de l'accueil est celle que le HTML servi porte déjà : la
    # première page ne doit pas changer de description en s'ouvrant.
    assert f'<meta name="description" content="{DESCRIPTIONS["/"]}">' in page


# -- la revue du 15 septembre 2026 : le thème « gommer la touche IA » ----------


#: Le nombre de phrases portant une incise en tiret cadratin que chaque page
#: peut encore compter, hors tableaux. Les bornes sont celles de la relecture
#: de septembre 2026, où le site en comptait de deux à quatre fois plus : elles
#: n'interdisent pas l'incise, qui est une ponctuation française, elles
#: interdisent d'y revenir comme à un tic.
INCISES_MAXIMUM = {
    "/": 3, "/simuler": 14, "/cas-types": 9, "/cout": 22,
    # Méthode et Sources ont fait une page le 23 septembre 2026 : ses bornes
    # s'additionnent, 9 et 6.
    "/methode": 15, "/partager": 4, "/risque": 4,
    # Écrite le 4 octobre 2026 sans aucune : une règle, sa source, et rien
    # entre deux tirets.
    "/saviez-vous": 0,
    # Celles qui restent sur Avantages sont citées et non rédigées : le
    # message de refus du garde-fou, et une énumération de choix que le dépôt
    # refuse de trancher à la place du lecteur.
    "/avantages": 3,
}


@pytest.mark.parametrize("chemin", list(TITRES))
def test_les_incises_en_tiret_restent_rares(chemin):
    """Le tiret cadratin en incise — « — c'est-à-dire […] — » — est le tic de
    ponctuation le plus reconnaissable d'un texte généré, et le site en
    faisait un usage dense : quatorze phrases sur l'accueil, une quarantaine
    sur Coût. La plupart sont devenues des parenthèses, des deux-points ou des
    phrases séparées ; ce test tient le compte."""
    prose = _prose(rendre(chemin, {})[1])
    phrases = [p for p in re.split(r"(?<=[.!?])\s+", prose) if " — " in p]
    assert len(phrases) <= INCISES_MAXIMUM[chemin], (
        f"{chemin} : {len(phrases)} phrases avec une incise en tiret, "
        f"{INCISES_MAXIMUM[chemin]} au plus — " + " | ".join(p[:80] for p in phrases)
    )


@pytest.mark.parametrize("chemin", list(TITRES))
def test_le_procede_ce_n_est_pas_x_c_est_y_a_disparu(chemin):
    """« Ce n'est pas une économie, c'est une marge » : efficace une fois,
    reconnaissable comme procédé à la dixième. Le site le répétait sur chaque
    page ; il n'en reste aucun, et les contrastes se disent autrement — une
    comparaison, un exemple, une question."""
    prose = _prose(rendre(chemin, {})[1])
    procede = re.compile(r"(?:n'est pas|ne sont pas)[^.;]{0,80}?(?:, c'est|: c'est)|, et non |\bnon pas ")
    trouves = procede.findall(prose)
    assert not trouves, f"{chemin} : {trouves}"


def test_le_programme_casse_ses_triades_et_porte_une_voix():
    """« Il est illisible. Il est inégal. Il n'est pas piloté. » est devenu une
    liste asymétrique, et l'accueil porte une note signée : qui publie ce
    site, pourquoi, et avec quelles réserves.

    La note a changé de place à la refonte en affiche. Elle était le quatrième
    bloc de texte du premier écran ; elle est allée dans le dépliant qui disait
    comment vérifier, parce que c'est le même geste — et parce que le premier
    écran doit tenir son budget de lecture. Ce dépliant, un plan du site que le
    bandeau porte déjà, est parti le 23 septembre 2026 : la note répond
    désormais à « Ces chiffres sont-ils fiables ? », qui est la même question.
    Ce qui reste visible est l'engagement, en une phrase sur le panneau
    crème : tout est chiffré, sur des données publiques et un modèle ouvert."""
    corps = rendre("/", {})[1]
    assert "Il est illisible." not in corps and "Il n'est pas piloté." not in corps
    assert "Illisible, d'abord." in corps and "Et personne ne le pilote." in corps
    note = re.search(r'<div class="note signee">(.*?)</div>', corps, re.S)
    assert note, "la note signée manque"
    assert "Nous avons choisi" in note.group(1)
    assert "Nos réserves sont écrites" in note.group(1)
    assert "Le Parti libéral français, septembre 2026." in note.group(1)
    # Elle est rangée, pas supprimée : sous la question de la fiabilité.
    assert "Pourquoi ce site." not in _hors_depliants(corps)
    fiables = re.search(
        r'<details class="section" id="tout-verifier"><summary>.*?'
        r"Ces chiffres sont-ils fiables \?.*?</details>", corps, re.S)
    assert fiables and "Pourquoi ce site." in fiables.group(0)
    # Et l'engagement, lui, reste sous les yeux.
    visible = _hors_depliants(corps)
    assert "Vérifiez plutôt que de nous croire" in visible
    assert "sur des données publiques" in visible


#: Réserves au plus sur la page Coût. Il y en a cinq ; à quatorze, la liste
#: disait surtout que personne n'y avait fait le tri.
RESERVES_MAXIMUM = 8


def test_la_rubrique_des_reserves_de_la_page_cout_ne_suit_plus_le_patron():
    """« Ce que cette page ne dit pas » était un titre de gabarit, le même
    d'une page à l'autre ; celui de Coût dit ce qu'il contient, et une phrase
    d'entrée dit pourquoi il est là."""
    for chemin in TITRES:
        corps = rendre(chemin, {})[1]
        assert "<span>Ce que cette page ne dit pas</span>" not in corps, chemin
        assert "ne dit pas</span>" not in corps, chemin
    cout = rendre("/cout", {})[1]
    # Le titre ne compte plus. Il disait « Dix » le 17 septembre et « Quatorze »
    # le 20 : chaque chantier de la page y ajoutait sa ligne, et le compteur
    # était devenu un aveu. Ce qui se règle est dit sous son réglage, ce qui
    # décrit un système dans le dépliant de ce système, et la liste ne garde
    # que ce que le lecteur ne peut ni changer ni lire ailleurs. Le plafond
    # oblige la prochaine réserve à en fusionner une plutôt que de s'ajouter.
    assert "<span>À lire avant de citer ces chiffres</span>" in cout
    assert "réserves à lire avant de citer" not in cout
    assert "Une page de chiffres vaut par ce qu'elle laisse de côté" in cout
    debut = cout.index("Une page de chiffres vaut par ce qu'elle laisse de côté")
    liste = cout[debut:cout.index("</ul>", debut)]
    assert 3 <= liste.count("<li><strong>") <= RESERVES_MAXIMUM, liste.count("<li><strong>")
    # Les réserves déplacées sont lues là où elles se règlent ou se décrivent.
    assert "La recette réagit sur quatre points" in cout[cout.index('id="cout-postes"'):]
    assert "Seul le système actuel sert la pension de" in cout[cout.index('id="cout-postes"'):]
    assert "sans toucher aux écarts entre carrières" in cout[cout.index('id="cout-equilibre"'):]
    simuler = rendre("/simuler", {})[1]
    assert "où ce stock est éteint" in simuler



# -- action 13 : la certification datée série par série -------------------------


def test_la_page_donnees_ne_promet_que_la_plus_ancienne_verification():
    """« Recontrôlé le 16 septembre » était la date du dernier passage, fût-il
    partiel. La page dit désormais le MINIMUM des dates de fiche — la seule
    affirmation que le journal soutient —, et la table date chaque série."""
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.donnees.chargement import journal_certification

    journal = journal_certification(RACINE_DONNEES)
    dates = sorted(trace["verifiee_le"] for trace in journal["series"].values())
    corps = rendre("/methode", {})[1]
    ancienne = pages._date_en_clair(dates[0])
    recente = pages._date_en_clair(dates[-1])
    assert f"la vérification la plus ancienne remonte au {ancienne}" in re.sub(
        r"\s+", " ", corps)
    assert f"la plus récente au {recente}" in re.sub(r"\s+", " ", corps)
    assert journal["dernier_passage_le"] not in corps.split("<table")[0], (
        "la date du dernier passage ne doit plus être présentée comme celle de tout"
    )
    table = re.search(r'<table id="series">.*?</table>', corps, re.S).group(0)
    assert '<th class="texte date" scope="col"><button type="button" class="tri" data-colonne="3">Vérifiée le</button></th>' in table
    assert table.count(f">{dates[0]}<") >= 1


# -- les trois pages agrégées obéissent aux réglages du simulateur ------------
#
# Elles ne calculent aucune carrière saisie — elles croisent des carrières
# types avec des générations —, mais elles doivent le faire sous les MÊMES
# règles que le simulateur. Jusqu'au 19 septembre 2026, elles calculaient
# toujours sous les paramètres par défaut : changer l'indexation dans le
# simulateur déplaçait la pension affichée, et pas un chiffre de la page Coût.
# Les deux pages disaient alors, sans le dire, deux choses différentes.


@pytest.mark.parametrize("chemin", list(PAGES_AGREGEES))
def test_une_page_agregee_porte_son_bloc_de_reglages(page, chemin):
    corps = page(chemin)
    assert 'class="section options reglages"' in corps
    assert "Recalculer cette page" in corps
    # Le formulaire vise la route NUE : le routeur colle la requête derrière
    # l'action, et une action qui en porterait déjà une en donnerait deux.
    assert f'action="#{chemin}"' in corps


@pytest.mark.parametrize("chemin", list(PAGES_AGREGEES))
def test_une_page_agregee_au_defaut_ne_dit_rien_des_reglages(page, chemin):
    """Tant que rien n'est changé, la page est celle d'avant.

    CE QUE CE TEST GARDE, c'est qu'aucun RÉGLAGE ne voyage dans un lien que le
    lecteur n'a pas demandé : une adresse partagée ne doit porter que ce que
    son auteur a effectivement changé. Les VUES sont l'autre chose — l'année
    que la cascade de Coût décompose —, et celles-là voyagent par construction,
    puisqu'un sélecteur n'a pas d'autre façon de dire où il mène. La
    distinction est dans ``_VUES_DE_PAGE`` ; ici on vérifie qu'un lien ne porte
    rien D'AUTRE qu'une vue.
    """
    corps = page(chemin)
    assert "ne sont pas ceux des réglages par défaut" not in corps
    assert '<a href="#/cout"' in corps or '<a href="#/simuler"' in corps
    vues = {cle for cles in pages._VUES_DE_PAGE.values() for cle in cles}
    for requete in re.findall(r'<a href="#/[a-z-]+\?([^"]*)"', corps):
        portees = {couple.split("=")[0] for couple in requete.split("&")}
        assert portees <= vues, (
            f"{chemin} : un lien porte {portees - vues}, qui n'est pas une vue"
        )


@pytest.mark.parametrize("chemin", list(PAGES_AGREGEES))
def test_un_reglage_explicite_au_defaut_rend_la_page_du_defaut(page, chemin):
    """« indexation=masse_salariale » est le défaut : la page ne doit pas bouger.

    C'est ce qui garantit que la lecture des réglages est ADDITIVE : une
    adresse qui ne demande rien de neuf rend exactement la page d'avant.
    """
    assert page(chemin, indexation="masse_salariale") == page(chemin)


@pytest.mark.parametrize("chemin", list(PAGES_AGREGEES))
def test_une_page_agregee_ignore_la_carriere_de_l_adresse(page, chemin):
    """Une adresse de simulateur collée sur la page Coût n'y décrit que des règles.

    La naissance, le statut et le revenu qu'elle porte n'ont aucun sens dans un
    agrégat : ils sont ignorés, et une faute dans l'un d'eux ne peut pas faire
    échouer la page.
    """
    assert page(chemin, naissance="1962", statut="fonctionnaire_civil",
                salaire="3000", unite_revenu="euros_mois") == page(chemin)


@pytest.mark.parametrize("chemin", list(PAGES_AGREGEES))
def test_une_page_agregee_dit_quand_elle_n_est_plus_au_defaut(page, chemin):
    corps = page(chemin, indexation="prix", bascule="2030")
    assert "ne sont pas ceux des réglages par défaut" in corps
    # L'apostrophe est échappée dans la page : on compare sur le texte lu.
    assert "règle d'indexation : Prix" in html.unescape(corps)
    assert "année de bascule : 2030" in corps
    # Et de quoi revenir en arrière, sans avoir à effacer une adresse à la main.
    assert f'<a href="#{chemin}">revenir aux réglages par défaut</a>' in corps


@pytest.mark.parametrize("chemin", list(PAGES_AGREGEES))
def test_les_reglages_suivent_le_lecteur_d_une_page_a_l_autre(page, chemin):
    """Sans cela, changer une règle ici et cliquer là ramènerait au défaut."""
    corps = page(chemin, indexation="prix")
    assert '<a href="#/simuler?indexation=prix"' in corps
    assert '#/methode?indexation=prix' in corps
    # Le bandeau de navigation les porte aussi : c'est lui qu'on clique.
    assert '#/cout?indexation=prix' in g.entete(chemin)


def test_un_reglage_deplace_les_chiffres_de_la_page_cout(contexte):
    """Le cœur de l'affaire : ce sont les CHIFFRES qui doivent bouger.

    L'indexation sur les prix, au lieu de la croissance de la masse salariale,
    écrase la valeur réelle des comptes notionnels : la masse de pensions que
    chaque système notionnel servirait s'en trouve nettement réduite. Le
    rapport que la page trace est celui-là.
    """
    defaut = contexte.cout()
    prix = contexte.pour(
        Saisie.modelisation({"indexation": "prix"}).parametres(contexte.base)
    ).cout()
    annee = defaut.derniere_annee
    for scenario in ("notionnel_retroactif", "notionnel_liberal"):
        assert prix.annee(annee).rapports[scenario] < defaut.annee(annee).rapports[scenario]
    # Et le contexte d'origine n'a pas bougé : deux jeux de règles cohabitent.
    assert contexte.cout().annee(annee).rapports == defaut.annee(annee).rapports


def test_un_reglage_hors_bornes_ne_fait_pas_tomber_la_page(page):
    """Une adresse mal formée doit afficher une phrase, pas une trace d'exécution."""
    corps = page("/cout", bascule="1800")
    assert "Saisie refusée" in corps
    # Et la page est rendue derrière, sous les règles par défaut.
    assert "ne sont pas ceux des réglages par défaut" not in corps
    assert 'class="section options reglages"' in corps


def test_une_adresse_qui_ne_porte_que_des_reglages_ne_demande_pas_de_calcul(page):
    """Cliquer « Simuler » dans le bandeau ne doit pas calculer une carrière.

    Les liens du site portent les réglages partout, y compris vers le
    simulateur. Sans cette règle, le seul fait d'avoir changé l'indexation
    aurait fait calculer d'office, à chaque passage par le bandeau, la carrière
    d'exemple que personne n'a saisie.
    """
    assert "Saisie refusée" not in page("/simuler", indexation="prix")
    assert not Saisie.depuis_requete({"indexation": "prix"}).demandee
    assert Saisie.depuis_requete({"naissance": "1975"}).demandee


def test_un_contexte_derive_partage_ce_qui_ne_depend_pas_des_regles(contexte):
    """Dériver ne doit rien recharger : les séries observées sont les mêmes."""
    derive = contexte.pour(
        Saisie.modelisation({"bascule": "2030"}).parametres(contexte.base))
    assert derive is not contexte
    assert derive.depenses() is contexte.depenses()
    assert derive.comptes() is contexte.comptes()
    assert derive.population() is contexte.population()
    # Un jeu de règles identique ne dérive rien du tout.
    assert contexte.pour(contexte.base) is contexte


def test_les_champs_de_modelisation_sont_ecrits_une_seule_fois():
    """Le simulateur et les pages agrégées proposent le MÊME jeu de règles.

    Deux listes de champs auraient suffi à les faire diverger, et deux pages du
    même site auraient alors proposé deux jeux de règles qui n'en sont qu'un.
    """
    champs = pages._champs_modelisation(module("saisie").Saisie())
    assert champs in rendre("/simuler", {})[1]
    assert champs in rendre("/cout", {})[1]


def test_le_routeur_ne_prend_pas_une_adresse_reglee_pour_une_simulation():
    """« #/?indexation=prix » est l'accueil réglé, et non une vieille adresse.

    Le routeur d'``index.html`` renvoie sur le simulateur toute adresse qui
    porte « #/ » suivi d'une requête : ce sont les liens partagés d'avant que
    l'accueil ne devienne le programme. Depuis que les réglages suivent le
    lecteur, le lien de l'accueil en porte une lui aussi — et cliquer
    « Programme » après avoir changé l'indexation envoyait sur le simulateur.
    """
    from pathlib import Path

    page = (Path(__file__).resolve().parents[1] / "index.html").read_text(
        encoding="utf-8")
    assert "CLES_MODELISATION" in page, (
        "le routeur doit savoir distinguer une règle d'un champ de carrière"
    )
    assert "!CLES_MODELISATION.includes(cle)" in page


def test_la_bascule_net_brut_decrit_la_meme_carriere():
    """Le piège que ce lien existe pour éviter, et c'est le même qu'à l'unité.

    En mode net, le nombre du formulaire est un NET. Le recopier tel quel dans
    l'autre mode le ferait relire comme un brut, et la page reviendrait en
    décrivant une autre carrière — mieux payée d'un quart. Le lien porte donc
    le montant traduit, et l'aller-retour doit retomber sur le nombre de
    départ.
    """
    depart = {"naissance": "1975", "unite_revenu": "euros_mois",
              "salaire": "2500", "montants": "net"}
    # La bascule écrit ses DEUX états ; celui qui s'applique n'est pas un lien.
    # On cherche donc la branche « brut » sous sa forme de lien, et on vérifie
    # au passage que « net » est bien marqué comme l'état courant.
    corps = rendre("/simuler", depart)[1]
    assert '<span class="actif" aria-current="true">net avant impôt</span>' in corps
    lien = re.search(r'<a href="#/simuler\?([^"]*)">brut</a>', corps)
    assert lien, "la page ne porte pas de branche « brut »"
    vers_brut = dict(parse_qsl(html.unescape(lien.group(1))))
    assert vers_brut["montants"] == "brut"
    # Un net de 2 500 € vaut un brut d'environ 3 160 € pour un salarié du privé.
    assert 3000 < float(vers_brut["salaire"]) < 3300

    retour = rendre("/simuler", vers_brut)[1]
    assert '<span class="actif" aria-current="true">brut</span>' in retour
    lien = re.search(r'<a href="#/simuler\?([^"]*)">net avant impôt</a>', retour)
    assert lien, "la page ne porte pas de branche « net »"
    vers_net = dict(parse_qsl(html.unescape(lien.group(1))))
    assert float(vers_net["salaire"]) == pytest.approx(2500, abs=2)


def test_les_deux_modes_decrivent_la_meme_pension_a_neuf_points_pres(contexte):
    """Même carrière, deux modes : le rapport des pensions est celui du barème.

    C'est le seul test qui relie les deux moitiés de la bascule — la saisie,
    qui convertit un net en brut, et l'affichage, qui retire de la pension
    9,1 % et la cotisation maladie de sa part complémentaire. S'il tombe,
    l'une des deux a bougé sans l'autre.
    """
    def pension(parametres):
        corps = rendre("/simuler", parametres)[1]
        entete = corps.split('<div class="scenario">')[1].split('<div class="barre')[0]
        brut = re.search(r'class="chiffre principal">\s*'
                         r'<span class="categorie">retraite</span>\s*'
                         r'<span class="somme">([^<]+)</span>', entete)
        assert brut, entete[:200]
        return float(brut.group(1).replace(" ", "").replace(",", "."))

    commun = {"naissance": "1985-03-01", "sexe": "F",
              "statut": "salarie_prive_non_cadre", "debut": "2007-09-01",
              "liquidation": "2049-03-01", "unite_revenu": "euros_mois"}
    # Le même salaire, dit une fois en brut et une fois en net : la bascule
    # donne la correspondance, et on la reprend ici pour ne pas la deviner.
    en_brut = pension({**commun, "salaire": "3158", "montants": "brut"})
    en_net = pension({**commun, "salaire": "2500", "montants": "net"})
    # Le taux de la personne, que le modèle tire de sa pension du scénario 1 :
    # 9,1 %, et 1 % de sa part complémentaire (action 138, étape 2).
    saisie = Saisie.depuis_requete({**commun, "salaire": "3158", "montants": "brut"})
    taux = Montants.depuis(saisie, contexte.base, contexte.simuler(saisie)).taux_pension
    assert 0.0 < taux <= 0.101
    assert en_net == pytest.approx(en_brut * (1 - taux), rel=2e-3)


def test_la_complementaire_paie_sa_cotisation_maladie_sur_la_page(contexte):
    """En net, l'étage complémentaire du système 1 paie un point de plus que la
    base, celui de la cotisation maladie : la composition sous le montant le
    montre, et la note du mode dit le taux de la personne, le revenu fiscal
    présumé et l'hypothèse des autres systèmes (action 138, étape 2). Un
    revenu en multiple du salaire moyen ne dépend pas du mode : la carrière est
    la même des deux côtés."""
    commun = {"naissance": "1985-03-01", "sexe": "F",
              "statut": "salarie_prive_non_cadre", "debut": "2007-09-01",
              "liquidation": "2049-03-01", "unite_revenu": "moyen", "salaire": "1"}

    def etages(corps):
        bloc = re.search(r'<span class="composition">(.*?)</span>', corps, re.S)
        assert bloc, "la composition du système 1 a disparu"
        texte = re.sub(r"<[^>]+>", "", html.unescape(bloc.group(1)))
        return {libelle.strip(): float(re.sub(r"\D", "", montant))
                for montant, libelle in re.findall(r"([\d\s]+)\s*€\s*de ([^+]+)", texte)}

    en_brut = etages(rendre("/simuler", {**commun, "montants": "brut"})[1])
    corps = rendre("/simuler", {**commun, "montants": "net"})[1]
    en_net = etages(corps)
    saisie = Saisie.depuis_requete({**commun, "montants": "net"})
    montants = Montants.depuis(saisie, contexte.base, contexte.simuler(saisie))
    taux, base_seule = montants.taux_pension, montants.taux_sans_maladie
    assert montants.taux_maladie == pytest.approx(0.01)
    base, complementaire = "retraite de base", "retraite complémentaire"
    assert en_net[base] == pytest.approx(en_brut[base] * (1 - base_seule), abs=2.5)
    assert en_net[complementaire] == pytest.approx(
        en_brut[complementaire] * (1 - base_seule - 0.01), abs=2.5)
    note = re.search(r"La pension est nette de ([\d,]+)", html.unescape(corps))
    assert note, "la note du mode a disparu"
    assert note.group(1) == f"{taux * 100:.1f}".replace(".", ",")
    assert "1 % de cotisation maladie" in corps
    assert "présumé fait de vos seules pensions" in corps
    assert "ne change pas vos prélèvements" in corps


def test_le_mode_des_montants_voyage_dans_l_adresse():
    """Une adresse partagée décrit la carrière qu'on a calculée, mode compris.

    Le mode gouverne l'interprétation du nombre « salaire » : une adresse qui
    l'omettrait retomberait sur le défaut et décrirait une autre carrière.
    C'est pourquoi `requete` l'écrit toujours, comme l'unité.
    """
    saisie = Saisie.depuis_requete({"naissance": "1975", "montants": "net"})
    assert "montants=net" in saisie.requete()
    assert "montants=brut" in Saisie.depuis_requete({"naissance": "1975"}).requete()
    # Et le formulaire le renvoie quand on le soumet, par un champ caché.
    corps = rendre("/simuler", {"naissance": "1975", "montants": "net"})[1]
    assert '<input type="hidden" name="montants" value="net">' in corps


def test_le_taux_de_remplacement_parle_la_langue_du_mode():
    """Le défaut que la question « obtient-on les mêmes chiffres ? » a révélé.

    Le modèle calcule le taux de remplacement BRUT sur BRUT. Affiché tel quel à
    côté de montants nets, il serait le seul chiffre de la page à parler
    l'autre langue — et il mentirait dans un sens précis : une pension est
    moins prélevée qu'un salaire, 9,1 % contre une vingtaine de points, si bien
    que le taux NET dépasse le taux brut de plusieurs points. C'est un fait
    connu du système français, et rarement montré.
    """
    commun = {"naissance": "1985-03-01", "sexe": "F",
              "statut": "salarie_prive_non_cadre", "debut": "2007-09-01",
              "liquidation": "2049-03-01", "unite_revenu": "euros_mois"}

    def taux(parametres):
        corps = rendre("/simuler", parametres)[1]
        lus = []
        for bloc in corps.split('<div class="scenario">')[1:]:
            glose = bloc.split('class="glose"')[1].split("</div>")[0]
            plat = " ".join(re.sub(r"<[^>]+>", "", html.unescape(glose)).split())
            trouve = re.search(r"(\d+,\d+) % · écart", plat)
            assert trouve, plat[:120]
            lus.append(float(trouve.group(1).replace(",", ".")))
        return lus

    en_brut = taux({**commun, "salaire": "3158", "montants": "brut"})
    en_net = taux({**commun, "salaire": "2500", "montants": "net"})
    assert len(en_brut) == 4
    for rang, (brut, net) in enumerate(zip(en_brut, en_net)):
        assert net > brut, "le taux net doit dépasser le taux brut"
        # Le rapport des deux prélèvements : 0,909 de pension contre environ
        # 0,79 de salaire. Une fourchette large suffit — elle n'est pas là pour
        # valider un dixième de point, mais pour attraper un taux resté brut.
        # La proposition, quatrième ligne, se rapporte à SA fiche de paie, qui
        # prélève moins sur le même brut : son rapport est plus bas.
        bornes = (1.03, 1.12) if rang == 3 else (1.10, 1.20)
        assert bornes[0] < net / brut < bornes[1], f"{net} / {brut}"


def test_la_bascule_ecrit_ses_deux_etats_et_dit_lequel_s_applique():
    """Ce qui sépare une bascule d'un lien, et pourquoi elle l'a remplacé.

    Un lien seul — « Voir les montants en brut » — demande au lecteur de
    déduire l'état courant de la phrase qui propose d'en changer, ce que
    personne ne fait, et il ne se voit pas parce qu'il ressemble au texte. Les
    deux états côte à côte disent à la fois où l'on est et où l'on peut aller.

    Trois propriétés, et chacune a coûté un aller-retour : les deux libellés
    sont là, un seul est un lien, et l'état courant porte `aria-current` — sans
    quoi une synthèse vocale lirait deux mots sans savoir lequel s'applique.
    """
    libelles = {"net": "net avant impôt", "brut": "brut"}
    for code, autre_code in (("net", "brut"), ("brut", "net")):
        mode, autre = libelles[code], libelles[autre_code]
        corps = rendre("/simuler",
                       {"naissance": "1975", "montants": code})[1]
        bascules = re.findall(
            r'<div class="bascule" role="group" aria-label="Montants">.*?</div>',
            corps, re.S)
        assert bascules, "la page ne porte aucune bascule de montants"
        for bloc in bascules:
            assert f'<span class="actif" aria-current="true">{mode}</span>' in bloc
            assert f">{autre}</a>" in bloc
            # Un seul lien : l'état courant n'a pas d'adresse, c'est celle où
            # l'on est déjà.
            assert bloc.count("<a href=") == 1
            assert 'role="group"' in bloc and 'aria-label="Montants"' in bloc


def test_l_aide_du_champ_ne_promet_pas_une_conversion_qui_n_aura_pas_lieu():
    """Deux phrases contradictoires à deux lignes d'écart, et rien pour trancher.

    Sous un statut dont le dépôt n'a pas les prélèvements hors retraite — la
    MSA, l'élu, l'ultramarin, qui n'a pas d'emploi —, le nombre saisi est lu
    TEL QUEL. Un avertissement le disait ; l'aide du champ, juste au-dessus,
    continuait de promettre que « le modèle remonte au brut par les
    prélèvements de votre statut ». Le lecteur voyait donc deux phrases se
    contredire sans savoir laquelle le concernait.
    """
    base = {"naissance": "1985-03-01", "sexe": "F", "debut": "2007-09-01",
            "liquidation": "2049-03-01", "unite_revenu": "euros_mois",
            "salaire": "1800", "montants": "net"}
    promesse = "remonte au brut par les prélèvements de votre statut"
    # Là où la conversion a lieu, l'aide la décrit.
    corps = rendre("/simuler",
                   {**base, "statut": "salarie_prive_non_cadre"})[1]
    assert promesse in corps
    assert "il ne peut pas remonter au brut" not in corps
    # Là où elle n'a pas lieu, l'aide le dit, et l'avertissement la double.
    for statut in ("salarie_agricole", "elu_local", "salarie_mayotte",
                   "sans_activite"):
        corps = rendre("/simuler", {**base, "statut": statut})[1]
        assert promesse not in corps, f"{statut} : l'aide promet une conversion"
        assert "il ne peut pas remonter au brut" in corps, statut
        assert "lu <strong>tel quel</strong>" in corps, statut


def test_la_cle_de_lecture_ne_dement_jamais_les_chiffres_qu_elle_explique():
    """Une clé de lecture fausse est pire qu'absente : elle enseigne l'erreur.

    Elle a dit « Montants BRUTS et au centime, comme la caisse les verse :
    avant CSG, CRDS et impôt » au-dessus de quatre montants nets, et « un brut
    sur un brut, donc plus bas qu'un taux calculé sur des nets » au-dessus d'un
    taux de remplacement calculé, précisément, sur des nets — en disant donc au
    lecteur de corriger mentalement dans le mauvais sens le seul chiffre de la
    page qu'il ne peut pas vérifier.
    """
    saisie = {"naissance": "1985-03-01", "sexe": "F",
              "statut": "salarie_prive_non_cadre", "debut": "2007-09-01",
              "liquidation": "2049-03-01", "unite_revenu": "euros_mois",
              "salaire": "2500"}
    attendu = {
        "net": ("Montants <strong>nets</strong> avant impôt", "un net sur un net"),
        "brut": ("Montants <strong>bruts</strong>", "un brut sur un brut"),
    }
    for mode, (montants, rapport) in attendu.items():
        corps = rendre("/simuler", {**saisie, "montants": mode})[1]
        assert montants in corps, f"{mode} : la clé de lecture ne dit pas l'unité"
        assert rapport in corps, f"{mode} : le taux de remplacement est mal décrit"
        # Et surtout : elle ne dit pas l'autre.
        autre_montants, autre_rapport = attendu["brut" if mode == "net" else "net"]
        assert autre_montants not in corps, f"{mode} : la clé annonce l'autre unité"
        assert autre_rapport not in corps, f"{mode} : le taux annonce l'autre unité"
    # Le glossaire, lui, sert les deux modes ET les pages qui n'ont pas de
    # bascule : il ne peut donc nommer ni l'un ni l'autre.
    assert "Ici, un brut sur un brut" not in g.GLOSSAIRE["taux de remplacement"]


def test_aucune_adresse_du_site_ne_porte_deux_croisillons():
    """Le bogue qui a cassé la bascule, et que rien ne voyait venir.

    Ici la ROUTE vit dans le fragment : `#/simuler?...`. Ajouter une ancre de
    section au bout — `#resultats`, pour revenir sur les chiffres — ne fabrique
    donc pas une ancre, mais allonge la DERNIÈRE VALEUR de la requête. La
    bascule des résultats écrivait `montants=brut#resultats`, qui n'est pas un
    mode connu : le modèle retombait sur son défaut, la page revenait en net,
    et le salaire déjà converti en brut y était relu comme un net — une
    carrière mieux payée d'un quart, sans un mot.

    Le test vaut pour tout le site, et pas pour la seule bascule : c'est un
    piège de la forme des adresses, que n'importe quel lien peut retrouver.
    Pour aller à une section, le site a `data-vers`, que le routeur traite
    sans toucher à l'adresse.
    """
    routes = [("/simuler", {"naissance": "1975", "montants": "net"}),
              ("/simuler", {"naissance": "1975", "montants": "brut"}),
              ("/", {}), ("/cout", {}), ("/methode", {}), ("/programme", {})]
    for route, parametres in routes:
        corps = rendre(route, parametres)[1]
        for adresse in re.findall(r'href="([^"]*)"', corps):
            fragment = html.unescape(adresse)
            assert fragment.count("#") <= 1, (
                f"{route} : l'adresse {fragment!r} porte deux croisillons ; "
                "la route occupe déjà le fragment, un second `#` entre dans "
                "la requête")


def test_les_deux_branches_d_une_bascule_ne_se_separent_jamais():
    """Sur un téléphone, c'est la légende qui passe à la ligne, pas le contrôle.

    La première version mettait la légende et les deux branches à plat dans un
    conteneur qui se replie : à 390 px, « UNITÉ » gardait « € par mois » et
    renvoyait « × salaire moyen » à la ligne suivante. Deux touches décalées
    d'une ligne ne se lisent plus comme un choix entre deux états — elles se
    lisent comme deux boutons. Les branches vivent donc dans une enveloppe
    commune, que la feuille de style déclare insécable.
    """
    corps = rendre("/simuler", {"naissance": "1975"})[1]
    bascules = re.findall(
        r'<div class="bascule" role="group" aria-label="[^"]+">(.*?)</div>',
        corps, re.S)
    assert bascules, "la page ne porte aucune bascule"
    for dedans in bascules:
        # L'enveloppe est le DERNIER enfant de la bascule : ce qu'elle
        # contient court jusqu'à son `</span>` final.
        choix = re.search(r'<span class="choix">(.*)</span>\s*$', dedans, re.S)
        assert choix, f"les branches ne sont pas enveloppées : {dedans}"
        # Les deux états sont DANS l'enveloppe, et la légende en dehors.
        assert choix.group(1).count("<a href=") == 1
        assert 'class="actif"' in choix.group(1)
        assert 'class="legende"' not in choix.group(1)
    assert ".bascule > .choix" in FEUILLE_DE_STYLE
    assert "flex-wrap: nowrap" in FEUILLE_DE_STYLE


def test_la_bascule_des_resultats_precede_les_montants():
    """Un réglage qu'on découvre après avoir lu les chiffres arrive trop tard.

    Elle était sous les quatre systèmes, entre eux et la fiabilité : on lisait
    quatre nombres, puis on apprenait qu'on aurait pu les lire autrement. Elle
    ouvre maintenant la carte.
    """
    corps = rendre("/simuler", SIMULATION_TEMOIN)[1]
    carte = corps.split('<h2 id="resultats"')[1]
    assert carte.index('class="bascule"') < carte.index('<div class="scenario">')


def test_le_script_de_la_page_s_analyse():
    """Le script d'``index.html`` n'est chargé par aucun test dans un navigateur :
    une déclaration en double y a rendu le site blanc le 19 septembre 2026 sans
    qu'aucun test ne le dise. ``node --check`` le lit comme le navigateur le
    lira, et refuse ce qui ne s'analyse pas."""
    import subprocess
    import tempfile
    from pathlib import Path
    page = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
    script = re.search(r'<script type="module">(.*?)</script>', page, re.S).group(1)
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as fichier:
        fichier.write(script)
    resultat = subprocess.run(["node", "--check", fichier.name],
                              capture_output=True, text=True, encoding="utf-8")
    assert resultat.returncode == 0, resultat.stderr


def test_le_reglage_des_frais_du_pilier_voyage_avec_les_autres():
    """« frais=detail » se lit, s'applique aux paramètres et se réécrit dans
    l'adresse ; le défaut ne s'écrit pas."""
    from retraite_notionnelle.config import Parametres
    from retraite_notionnelle.saisie import CLES_MODELISATION, Saisie

    assert "frais" in CLES_MODELISATION
    defaut = Saisie.depuis_requete({})
    assert defaut.frais == "paliers" and defaut.requete_modelisation() == ""
    saisie = Saisie.modelisation({"frais": "detail", "naissance": "1980-01"})
    assert saisie.frais == "detail" and not saisie.demandee
    parametres = saisie.parametres(Parametres())
    assert parametres.frais_arrerages_capitalisation == 0.0220
    assert parametres.frais_gestion_paliers == ()
    assert saisie.requete_modelisation() == "frais=detail"
    # Une valeur inconnue retombe sur le défaut, sans erreur.
    assert Saisie.depuis_requete({"frais": "gratuit"}).frais == "paliers"


def test_la_colonne_aspa_de_l_accueil_sert_le_bareme_de_l_aspa():
    """« Aujourd'hui (ASPA) » : ce que l'ASPA sert vraiment, sur ses deux barèmes
    lus — personne seule, couple d'allocataires —, et non les montants de la
    garantie appliqués au foyer, que la colonne recopiait jusqu'au
    23 septembre 2026. Le couple à 300 € et 300 € reçoit aujourd'hui 1 020 € et
    en recevrait 1 000 ; la personne seule à 300 €, 744 € contre 750."""
    from retraite_notionnelle.contexte import Contexte

    contexte = Contexte()
    annee = contexte.base.annee_euros_garantie_vieillesse
    minimum = contexte.simulateur().scenario_actuel.minimum_vieillesse
    seul = minimum.plafond(annee)[0] / 12
    couple = minimum.plafond_couple(annee)[0] / 12
    # Au centime : le couple porte l'annuel du texte, 19 442,21 €, dont le
    # mensuel publié, 1 620,18 €, est l'arrondi.
    assert seul == pytest.approx(1043.59, abs=0.005)
    assert couple == pytest.approx(1620.18, abs=0.005)
    rendu = pages.tableau_garantie(site().contexte)
    for foyer in pages.FOYERS_GARANTIE:
        plafond = seul if len(foyer) == 1 else couple
        assert g.euros(max(0.0, plafond - sum(foyer))) in rendu, foyer
    assert g.euros(1020.18) in rendu and g.euros(743.59) in rendu
