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

from retraite_notionnelle.web.pages import Contexte, Saisie, rendre

RACINE = Path(__file__).resolve().parents[1]
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
        "91 %": "la part financée, que la page dessine en barre et n'écrit pas",
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


@pytest.fixture(scope="module")
def contexte() -> Contexte:
    return Contexte()


@pytest.fixture(scope="module")
def parcours() -> str:
    return PARCOURS.read_text(encoding="utf-8")


def _prose(corps: str) -> str:
    """Le texte rendu, balises retirées et blancs repliés."""
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", corps)))


def _saisie_par_defaut() -> dict[str, str]:
    """Les paramètres de l'exemple que le simulateur ouvre déjà rempli.

    `rendre(contexte, "/simuler", {})` ne calcule rien : la page attend qu'on
    clique. Le parcours, lui, décrit l'écran d'APRÈS le clic, et ses chiffres
    en viennent. La requête est celle que le site écrit lui-même pour sa
    saisie par défaut, jamais une liste de paramètres recopiée ici.
    """
    return dict(parse_qsl(html.unescape(Saisie().requete().lstrip("?"))))


def _rendue(contexte: Contexte, chemin: str) -> str:
    parametres = _saisie_par_defaut() if chemin == "/simuler" else {}
    return _prose(rendre(contexte, chemin, parametres)[1])


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


def _lignes_rendues(contexte: Contexte, chemin: str, parametres: dict) -> dict:
    """Les lignes de résultat du simulateur, par numéro : titre, pension, écart."""
    corps = rendre(contexte, chemin, parametres)[1]
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


def test_le_parcours_rejoue_ses_carrieres(contexte, parcours):
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
        rendues = _lignes_rendues(contexte, chemin, parametres)
        assert rendues, f"{chemin} ne rend aucune ligne de résultat pour {qui}"
        suite = parcours[adresse.end():adresse.end() + 900]
        lignes = LIGNE_TABLEAU.findall(suite)
        assert lignes, f"aucun tableau sous l'adresse de {qui}"
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


@pytest.mark.parametrize("titre,chemin", sorted(PAGES_DES_SECTIONS.items()))
def test_chaque_chiffre_du_parcours_est_sur_sa_page(contexte, parcours, titre, chemin):
    """Tout montant et tout pourcentage d'une section se lit sur sa page.

    C'est le contrôle qui a manqué : « le salaire net baisse de 117 € » ne
    venait plus d'aucune page, et rien ne le disait. Ce qui ne vient pas de la
    page se déclare dans `HORS_PAGE`, avec sa raison.
    """
    section = _sections(parcours)[titre]
    # Les tableaux de carrières ont leur propre contrôle, plus précis : les
    # sauter ici évite de redire la même chose deux fois.
    section = LIGNE_TABLEAU.sub("", section)
    portees = _valeurs(_rendue(contexte, chemin))
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


@pytest.mark.parametrize("titre,chemin", sorted(PAGES_DES_SECTIONS.items()))
def test_chaque_compte_du_parcours_est_sur_sa_page(contexte, parcours, titre, chemin):
    """Les comptes sans unité, que l'œil ne signale pas.

    « 43 dispositifs », « 96 séries », « 51 points » : trois chiffres qui
    avaient dérivé sans que personne s'en aperçoive, parce qu'aucun symbole
    ne les distingue du reste de la phrase. Le couple « nombre + nom » est
    cherché tel quel dans la page, la casse en moins.
    """
    section = _sections(parcours)[titre]
    page = _rendue(contexte, chemin).lower()
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
