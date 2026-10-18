"""Le parcours de présentation dit-il ce que le site affiche ?

`docs/parcours_presentation.md` est le document qu'on suit pour parler en
public. Il a porté pendant deux jours les chiffres d'une matinée, gelés dans
une zone `recit` que `verifier_prose.py` ne relit pas — le régime est juste
pour un procès-verbal, il ne l'est pas pour un mode d'emploi. Le modèle a
bougé quatre fois dans la journée, et le document demandait d'annoncer une
BAISSE du salaire net là où l'écran montrait une hausse de trois cents euros.

Ce test fait pour lui ce que `test_le_README_donne_le_solde_que_la_page_cout_calcule`
fait pour le tableau des soldes : il rend les pages et confronte. Deux
mécaniques, parce que le document contient deux sortes de chiffres.

1. **Les carrières.** Le document donne l'adresse complète de chaque
   simulation, paramètres compris, et un tableau juste en dessous. Le test lit
   l'adresse, rejoue la simulation, et compare ligne à ligne. Ajouter une
   carrière au parcours ne demande donc pas de toucher à ce fichier.

2. **Les autres chiffres.** Chaque section du parcours est titrée par la page
   qu'elle décrit ; `PAGES_DES_SECTIONS` fait la correspondance. Tout montant
   et tout pourcentage d'une de ces sections doit se retrouver dans le rendu
   de cette page-là. Ce qui ne vient pas de la page — une saisie que le
   présentateur tape, un chiffre rappelé d'une autre page — se déclare dans
   `HORS_PAGE`, avec sa raison : c'est une liste qui doit rester courte, et
   qu'un troisième test empêche de se remplir de lignes mortes.

La comparaison porte sur les VALEURS, jamais sur la typographie : le parcours
arrondit à l'euro ce que la page sert au centime, et les trois espaces des
milliers du dépôt — fine, insécable, ordinaire — se valent ici.
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import parse_qsl

import pytest

from retraite_notionnelle.saisie import Saisie
from retraite_notionnelle.web.site import disponible, rendre

RACINE = Path(__file__).resolve().parents[1]
#: Le document que ce test tient, et lui seul : `zones.yaml` le dit `tenu` par
#: ce fichier, qui doit le nommer, sans quoi la conservation le regèle.
PARCOURS = RACINE / "docs" / "parcours_presentation.md"

#: La section du parcours, par son titre, et la page dont elle parle. Une
#: section absente de cette table n'est pas contrôlée : elle ne décrit pas une
#: page (le préambule, les consignes de salle, les questions attendues, qui
#: renvoient à plusieurs pages à la fois).
PAGES_DES_SECTIONS = {
    "### 1. Programme — trois minutes": "/",
    "### 2. Simuler — six minutes, c'est le cœur": "/simuler",
    "### Trois carrières prêtes à cliquer": "/simuler",
    "### 3. Cas types — trois minutes": "/cas-types",
    "### 4. Coût — trois minutes": "/cout",
    "### 4 bis. Risque — deux minutes, si on a le temps": "/risque",
    "### 5. Avantages — deux minutes": "/avantages",
    "### 6. Méthode et Données — deux minutes, pour finir": "/donnees",
}

#: Ce qu'une section décrivant une page peut écrire sans que la page le porte.
#: Chaque entrée dit pourquoi. Le test n'accepte que ces chiffres-là, à la
#: lettre : un nouveau demande qu'on ait regardé d'où il vient.
HORS_PAGE: dict[str, dict[str, str]] = {
    "/": {},
    "/simuler": {
        "3 500 €": "la saisie de l'exemple, tapée par le présentateur",
        "1 443 €": "la saisie de la carrière au SMIC",
        "3 000 €": "la saisie de la carrière du fonctionnaire",
        "2 751 €": "la saisie de la carrière née en 2000",
        "23 %": "la somme 18 + 5, dite par le parcours",
        "18 %": "le taux de la proposition, rappelé par le parcours",
        "5 %": "la part capitalisée, rappelée par le parcours",
        "1 050 €": "le plancher, montré page Programme et rappelé ici",
        "82 %": "la part patronale de l'État, détaillée page Méthode",
        "16 %": "le déficit projeté par le COR, chiffré page Coût",
    },
    "/cas-types": {},
    "/cout": {},
    "/risque": {},
    "/avantages": {},
    "/donnees": {},
}

#: Un nombre suivi de son unité, tel que le parcours et les pages l'écrivent.
#: Le signe compte — « +296 € » n'est pas « 296 € » — et l'espace des milliers
#: se présente sous ses trois formes.
NOMBRE = re.compile(r"(?<![\d  ])([+-]?)(?!0\d)"
                    r"(\d[\d   ]*(?:,\d+)?)\s?(Md\s?€|€|%)")
ADRESSE = re.compile(r"<https://g-pliberal\.github\.io/retraitecomptenotionelle/#"
                     r"(/[a-z-]+)\?([^>]+)>")
LIGNE_TABLEAU = re.compile(r"^\|\s*(\d)\.\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$",
                           re.M)
BLOC_SCENARIO = re.compile(r'<div class="scenario">(.*?)<div class="glose">(.*?)</div>',
                           re.S)
#: Ce qu'on tolère entre le chiffre du parcours et celui de la page, par unité.
#: Un euro parce que le parcours arrondit à l'unité ; un vingtième de point
#: pour le reste, qui est la dernière décimale que les pages affichent.
MARGES = {"€": 0.5, "Md €": 0.05, "%": 0.05}

#: Les noms que le parcours fait suivre d'un compte, et que la page écrit de
#: la même façon. Ce sont eux qui ont dérivé le plus vite — 43 dispositifs
#: pour 37, 96 séries pour 98, 51 points pour 54 — parce qu'aucune unité ne
#: les signale à l'œil. Le couple « nombre + nom » doit se lire sur la page,
#: la casse en moins : la page titre « 89 Régimes recensés », le parcours
#: écrit « 89 régimes recensés ».
COMPTES = ("dispositifs", "séries", "valeurs", "régimes", "institutions",
           "points", "calculés", "onglets")
COMPTE = re.compile(r"(?<![\d  ])(?!0\d)(\d[\d   ]*)\s("
                    + "|".join(COMPTES) + r")\b")


#: Les ancres des chiffres que le paquet donne (action 163) : le parcours se lit
#: comme on le lit, sans elles.
ANCRES = re.compile(r"<!--chiffre:.*?-->|<!--/-->")


@pytest.fixture(scope="module")
def parcours() -> str:
    return ANCRES.sub("", PARCOURS.read_text(encoding="utf-8"))


def test_aucun_compte_du_parcours_ne_s_ecrit_a_la_main():
    """Les comptes du parcours — valeurs, séries, régimes, dispositifs — sont
    ceux que les pages tirent du paquet. Écrits à la main, ils ont rougi la
    suite neuf fois du 6 au 17 octobre 2026, chaque fois que des données
    entraient (action 163). Ancrés sur le paquet, GitHub les récrit avec lui ;
    un compte ancré ne se lit plus ici, son ancre le sépare de son nom."""
    brut = PARCOURS.read_text(encoding="utf-8")
    assert [trouve.group(0) for trouve in COMPTE.finditer(brut)] == []


#: Un chiffre ancré, sa valeur comprise : ce qui reste quand on l'ôte est ce
#: qui s'écrit à la main.
ANCRE_ENTIERE = re.compile(r"<!--chiffre:.*?-->.*?<!--/-->", re.S)
#: La saisie d'un chiffre ancré sur la page Simuler.
MESURE_SIMULEE = re.compile(r"<!--chiffre:mesure\(simulateur\?([^)]*)\)-->")


def test_aucun_tableau_de_carriere_ne_s_ecrit_a_la_main():
    """Les pensions et les écarts des carrières du parcours sont ceux que la
    page Simuler affiche. Écrits à la main, ils ont rougi la suite chaque fois
    que le modèle bougeait, et le tableau de l'exemple, qu'aucune adresse ne
    précède, datait du 20 septembre (action 163). Ancrés sur la page
    (``mesure(simulateur…)``), GitHub les récrit avec elle, sur la saisie de
    l'adresse qui précède le tableau : ses ancres la répètent, et une adresse
    changée sans elles ferait dire au tableau la carrière d'avant."""
    brut = PARCOURS.read_text(encoding="utf-8")
    lignes = LIGNE_TABLEAU.findall(ANCRE_ENTIERE.sub("", brut))
    assert len(lignes) >= 13, "le parcours a perdu des lignes de ses tableaux de carrières"
    ecrits = [_ecrit(*trouve) for _numero, _libelle, *cellules in lignes
              for trouve in NOMBRE.findall(" ".join(cellules))]
    assert ecrits == []
    for adresse in ADRESSE.finditer(brut):
        saisie = dict(parse_qsl(html.unescape(adresse.group(2))))
        tableau = brut[adresse.end():].split("\n\n", 2)[1]
        lues = [{cle: valeur for cle, valeur in parse_qsl(argument)
                 if cle not in ("systeme", "quoi")}
                for argument in MESURE_SIMULEE.findall(tableau)]
        assert lues and all(lue == saisie for lue in lues), (
            f"le tableau sous l'adresse de {saisie.get('statut')} {saisie.get('salaire')} "
            "ne se mesure pas sur sa saisie")


#: Ce que le parcours écrit à la main parmi ses chiffres à unité, et pourquoi.
#: Le reste est ancré : sur la page qui l'affiche, le paquet où elle le lit ou
#: le modèle. Restent les saisies — ce que le présentateur tape, ce que la page
#: pose en exemple —, un réglage de salle, une promesse que la page écrit sans
#: la calculer, et les mots de la salle.
ECRITS_A_LA_MAIN = {
    "125 %": "le zoom du navigateur, un réglage de salle",
    "150 %": "le zoom du navigateur, un réglage de salle",
    "3 500 €": "la saisie de l'exemple, tapée par le présentateur",
    "1 443 €": "la saisie de la carrière au SMIC",
    "3 000 €": "la saisie de la carrière du fonctionnaire",
    "2 751 €": "la saisie de la carrière née en 2000",
    "300 €": "une pension du foyer que l'accueil pose en exemple (FOYERS_GARANTIE)",
    "1 500 €": "l'autre pension du même foyer",
    "100 %": "la quatrième promesse de l'accueil, que la page écrit sans la calculer",
    "30 %": "la question de la salle, citée telle qu'elle vient",
}


def test_aucun_chiffre_a_unite_du_parcours_ne_s_ecrit_a_la_main():
    """Les montants et les taux du parcours sont ceux que le site produit, et
    GitHub les récrit avec lui. Écrits à la main, ils rougissaient la suite
    chaque fois que le modèle bougeait, et ceux qu'aucune page ne confronte
    dérivaient sans bruit : le 18 octobre 2026, le parcours donnait « 12 % »
    d'une baisse que l'accueil chiffrait à 13, et « 8 % en 2070 » d'un
    réglage qui n'y retirait plus rien (action 163). Seuls s'écrivent à la
    main ceux qu'``ECRITS_A_LA_MAIN`` déclare, et chacun y sert encore."""
    brut = PARCOURS.read_text(encoding="utf-8")
    ecrits = {_ecrit(*trouve) for trouve in NOMBRE.findall(ANCRE_ENTIERE.sub("", brut))}
    assert sorted(ecrits - set(ECRITS_A_LA_MAIN)) == [], "chiffres écrits à la main"
    assert sorted(set(ECRITS_A_LA_MAIN) - ecrits) == [], "déclarations qui ne servent plus"


def _prose(corps: str) -> str:
    """Le texte rendu, balises retirées et blancs repliés."""
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", corps)))


def _saisie_par_defaut() -> dict[str, str]:
    """Les paramètres de l'exemple que le simulateur ouvre déjà rempli.

    `rendre("/simuler", {})` ne calcule rien : la page attend qu'on
    clique. Le parcours, lui, décrit l'écran d'APRÈS le clic, et ses chiffres
    en viennent. La requête est celle que le site écrit lui-même pour sa
    saisie par défaut, jamais une liste de paramètres recopiée ici.
    """
    return dict(parse_qsl(html.unescape(Saisie().requete().lstrip("?"))))


def _rendue(chemin: str) -> str:
    # Le parcours décrit l'exemple en net — « 3 500 € net par mois » —, le
    # défaut de son temps ; le brut l'est depuis le 4 octobre 2026. La page se
    # rend dans le mode qu'il décrit.
    parametres = ({**_saisie_par_defaut(), "montants": "net"} if chemin == "/simuler"
                  else {})
    return _prose(rendre(chemin, parametres)[1])


def _nombre(somme: str) -> float:
    """« 1 966,77 » et « 1 967 € » deviennent tous deux un nombre."""
    return float(re.sub(r"[  \s€]|Md", "", somme).replace(",", "."))


def _unite(brute: str) -> str:
    return "Md €" if brute.startswith("Md") else brute


def _valeurs(texte: str) -> dict[str, set[float]]:
    """Les nombres d'un texte, par unité : ce qu'il affirme, sans sa typographie."""
    trouves: dict[str, set[float]] = {"€": set(), "Md €": set(), "%": set()}
    for signe, corps, brute in NOMBRE.findall(texte):
        valeur = _nombre(corps)
        trouves[_unite(brute)].add(-valeur if signe == "-" else valeur)
    return trouves


def _graphies(nombre: str) -> set[str]:
    """Le même nombre sous les trois espaces des milliers du dépôt.

    « 41527 » s'écrit « 41 527 » avec une espace fine sur les pages, insécable
    ailleurs, et ordinaire dans le markdown du parcours. Les trois disent le
    même nombre, et la recherche ne doit pas dépendre de laquelle a été tapée.
    """
    nu = re.sub(r"[   ]", "", nombre)
    tete = len(nu) % 3 or 3
    groupes = [nu[:tete]] + [nu[i:i + 3] for i in range(tete, len(nu), 3)]
    return {nombre, nu} | {espace.join(groupes)
                           for espace in (" ", " ", " ")}


def _ecrit(signe: str, corps: str, brute: str) -> str:
    """Le chiffre tel qu'une entrée de `HORS_PAGE` le nomme."""
    return re.sub(r"[  ]", " ", f"{signe}{corps.strip()} {_unite(brute)}")


def _lignes_rendues(chemin: str, parametres: dict) -> dict:
    """Les lignes de résultat du simulateur, par numéro : titre, pension, écart."""
    corps = rendre(chemin, parametres)[1]
    lignes = {}
    for bloc, glose in BLOC_SCENARIO.findall(corps):
        titre = re.search(r'<span class="titre">(\d)\. ([^<]+)</span>', bloc)
        montant = re.search(r'<span class="chiffre principal">.*?'
                            r'<span class="somme">([^<]+)</span>', bloc, re.S)
        if not (titre and montant):
            continue
        ecart = re.search(r"écart au système actuel : ([^·]+)", _prose(glose))
        lignes[titre.group(1)] = (
            titre.group(2).strip(),
            _nombre(montant.group(1)),
            (ecart.group(1).strip() if ecart else ""),
        )
    return lignes


def _sections(texte: str) -> dict[str, str]:
    """Le corps de chaque section du parcours, par son titre exact."""
    titres = list(re.finditer(r"^#{2,3} .+$", texte, re.M))
    corps = {}
    for i, titre in enumerate(titres):
        fin = titres[i + 1].start() if i + 1 < len(titres) else len(texte)
        corps[titre.group(0)] = texte[titre.end():fin]
    return corps


#: Les pages se lisent dans le portage, par node (``web/site.py``) : sans
#: lui, les tests qui les rendent sont sautés, et ceux qui ne lisent que le
#: parcours tournent.
site_requis = pytest.mark.skipif(not disponible(),
                                 reason="node absent : le site ne se lit pas sans lui")


def test_les_sections_nommees_existent_toutes(parcours):
    """La table des sections est-elle encore à jour ?

    Un titre renommé sortirait sa section du contrôle sans bruit : c'est la
    panne que ce test doit éviter d'abord, avant de vérifier un seul chiffre.
    """
    titres = set(_sections(parcours))
    manquants = sorted(set(PAGES_DES_SECTIONS) - titres)
    assert not manquants, (
        f"sections nommées dans PAGES_DES_SECTIONS et absentes du parcours : "
        f"{manquants} — le titre a changé, ou la section a disparu")


@site_requis
def test_le_parcours_rejoue_ses_carrieres(parcours):
    """Chaque adresse du parcours est rejouée, et son tableau confronté.

    Le document donne l'adresse complète, paramètres compris : le test la lit,
    rend la page, et compare chaque ligne du tableau qui suit. Le montant est
    comparé à l'euro près, l'écart à la décimale.
    """
    adresses = list(ADRESSE.finditer(parcours))
    assert len(adresses) >= 3, "le parcours ne donne plus ses carrières en adresse"
    for adresse in adresses:
        chemin, requete = adresse.group(1), html.unescape(adresse.group(2))
        parametres = dict(parse_qsl(requete))
        qui = f"{parametres.get('statut')} {parametres.get('salaire')}"
        rendues = _lignes_rendues(chemin, parametres)
        assert rendues, f"{chemin} ne rend aucune ligne de résultat pour {qui}"
        suite = parcours[adresse.end():adresse.end() + 900]
        lignes = LIGNE_TABLEAU.findall(suite)
        assert lignes, f"aucun tableau sous l'adresse de {qui}"
        _confronter(qui, lignes, rendues)


@site_requis
def test_le_parcours_rejoue_l_exemple_du_simulateur(parcours):
    """Le tableau de l'exemple, celui que la page ouvre déjà rempli, n'a pas
    d'adresse au-dessus de lui : il se confronte à la page rendue comme le
    parcours la décrit, en net. Aucun test ne le lisait, et il datait du
    20 septembre (action 163)."""
    lignes = LIGNE_TABLEAU.findall(_sections(parcours)["### 2. Simuler — six minutes, c'est le cœur"])
    assert len(lignes) == 4, "le parcours ne donne plus les quatre lignes de l'exemple"
    _confronter("l'exemple", lignes,
                _lignes_rendues("/simuler", {**_saisie_par_defaut(), "montants": "net"}))


def _confronter(qui: str, lignes: list[tuple], rendues: dict) -> None:
    """Chaque ligne d'un tableau du parcours contre celle que la page rend : le
    montant à l'euro près, l'écart à la décimale."""
    for numero, _libelle, montant, ecart in lignes:
        assert numero in rendues, (
            f"[{qui}] le parcours donne une ligne {numero} que la page ne rend pas")
        _titre, pension, ecart_rendu = rendues[numero]
        annonce = _nombre(montant)
        assert abs(annonce - pension) <= MARGES["€"], (
            f"[{qui}] ligne {numero} : le parcours annonce {montant}, "
            f"la page affiche {pension:.2f} €")
        attendu = ecart.strip()
        if attendu == "référence":
            assert ecart_rendu == "référence", (
                f"[{qui}] ligne {numero} n'est plus la référence")
            continue
        trouve = NOMBRE.search(ecart_rendu)
        assert trouve, f"[{qui}] la page ne donne plus d'écart pour la ligne {numero}"
        rendu = _nombre(trouve.group(2)) * (-1 if trouve.group(1) == "-" else 1)
        voulu = NOMBRE.search(attendu)
        assert voulu, f"[{qui}] le parcours n'écrit pas d'écart lisible : {ecart!r}"
        annonce_ecart = _nombre(voulu.group(2)) * (-1 if voulu.group(1) == "-" else 1)
        assert abs(annonce_ecart - rendu) <= MARGES["%"], (
            f"[{qui}] ligne {numero} : le parcours annonce un écart de "
            f"{ecart}, la page affiche {ecart_rendu}")


@site_requis
@pytest.mark.parametrize("titre,chemin", sorted(PAGES_DES_SECTIONS.items()))
def test_chaque_chiffre_du_parcours_est_sur_sa_page(parcours, titre, chemin):
    """Tout montant et tout pourcentage d'une section se lit sur sa page.

    C'est le contrôle qui a manqué : « le salaire net baisse de 117 € » ne
    venait plus d'aucune page, et rien ne le disait. Ce qui ne vient pas de la
    page se déclare dans `HORS_PAGE`, avec sa raison.
    """
    section = _sections(parcours)[titre]
    # Les tableaux de carrières ont leur propre contrôle, plus précis : les
    # sauter ici évite de redire la même chose deux fois.
    section = LIGNE_TABLEAU.sub("", section)
    portees = _valeurs(_rendue(chemin))
    exemptes = HORS_PAGE.get(chemin, {})
    absents = []
    for signe, corps, brute in NOMBRE.findall(section):
        if _ecrit(signe, corps, brute) in exemptes:
            continue
        unite = _unite(brute)
        valeur = _nombre(corps) * (-1 if signe == "-" else 1)
        if not any(abs(porte - valeur) <= MARGES[unite] for porte in portees[unite]):
            absents.append(_ecrit(signe, corps, brute))
    assert not absents, (
        f"{titre}\n  chiffres que {chemin} n'affiche pas : {absents}\n"
        f"  — soit la page a bougé et le parcours doit suivre, soit le chiffre "
        f"vient d'ailleurs et sa raison va dans HORS_PAGE[{chemin!r}]")


@site_requis
@pytest.mark.parametrize("titre,chemin", sorted(PAGES_DES_SECTIONS.items()))
def test_chaque_compte_du_parcours_est_sur_sa_page(parcours, titre, chemin):
    """Les comptes sans unité, que l'œil ne signale pas.

    « 43 dispositifs », « 96 séries », « 51 points » : trois chiffres qui
    avaient dérivé sans que personne s'en aperçoive, parce qu'aucun symbole
    ne les distingue du reste de la phrase. Le couple « nombre + nom » est
    cherché tel quel dans la page, la casse en moins.
    """
    section = _sections(parcours)[titre]
    page = _rendue(chemin).lower()
    absents = [f"{nombre.strip()} {nom}"
               for nombre, nom in COMPTE.findall(section)
               if not any(f"{graphie} {nom}" in page
                          for graphie in _graphies(nombre.strip()))]
    assert not absents, (
        f"{titre}\n  comptes que {chemin} n'écrit pas : {absents}\n"
        f"  — la page a bougé, et le parcours doit suivre")


def test_les_exemptions_servent_encore(parcours):
    """Une exemption qui ne sert plus est une dette qu'on oublie.

    `HORS_PAGE` dit ce qu'une section peut écrire sans que sa page le porte.
    Le jour où la phrase qui portait le chiffre disparaît, l'exemption reste,
    et la liste s'allonge sans que personne la relise. Ce test la tient courte.
    """
    sections = _sections(parcours)
    par_page: dict[str, str] = {}
    for titre, chemin in PAGES_DES_SECTIONS.items():
        par_page[chemin] = par_page.get(chemin, "") + sections.get(titre, "")
    ecrits = {chemin: {_ecrit(*trouve) for trouve in NOMBRE.findall(texte)}
              for chemin, texte in par_page.items()}
    mortes = [(chemin, chiffre)
              for chemin, exemptes in HORS_PAGE.items()
              for chiffre in exemptes
              if chiffre not in ecrits.get(chemin, set())]
    assert not mortes, (
        f"exemptions de HORS_PAGE que le parcours n'écrit plus : {mortes} — "
        "les retirer")
