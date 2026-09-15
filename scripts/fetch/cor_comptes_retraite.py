#!/usr/bin/env python3
"""Récupération des comptes du système de retraite auprès du COR.

    python scripts/fetch/cor_comptes_retraite.py

CE QU'ON VIENT CHERCHER, ET POURQUOI PAS AILLEURS
--------------------------------------------------
La page « Coût » du dépôt sait ce qui a été VERSÉ : les Comptes de la
protection sociale de la DREES publient la dépense du risque vieillesse-survie
depuis 1959. Ils ne savent pas ce qui a été ENCAISSÉ, et cette ignorance n'est
pas un oubli du dépôt : **les Comptes de la protection sociale ne ventilent pas
leurs ressources par risque.** Le jeu 305 de la DREES ne porte que des postes
``E`` — des prestations ; son classeur annexe donne bien les ressources, mais
pour la protection sociale TOUT ENTIÈRE, maladie et famille comprises. Il n'y a
donc pas de « recettes du risque vieillesse » chez le producteur des dépenses,
et la piste que la feuille de route indiquait — « ressources par risque, même
source » — n'existe pas.

Ce que quelqu'un publie, en revanche, c'est le compte du SYSTÈME DE RETRAITE :
dépenses, ressources et solde du même périmètre, avec la même convention, année
par année. C'est le COR, dans son rapport annuel, et personne d'autre. Le
critère 1 du manifeste — le producteur prime sur le repreneur — ne le désigne
pas comme producteur des comptes de chaque régime, qui sont ceux des rapports à
la Commission des comptes de la Sécurité sociale ; il le désigne comme
producteur de leur CONSOLIDATION, que nul autre n'établit. C'est la même
position que celle où le manifeste met déjà ses hypothèses de long terme. Les
valeurs entrent donc au niveau ``haute``, jamais ``certifiee``.

CE QUE LE FICHIER PRODUIT CONTIENT
-----------------------------------
Trois séries en part de PIB, tirées des classeurs de données que le COR publie
à côté de son rapport :

* ``depenses`` et ``ressources``, 2002 à l'horizon de projection, chacune
  scindée en ``observe`` — les rapports à la CCSS — et ``projete`` — le
  scénario de référence du COR ;
* ``solde``, la même chose, qui doit être la différence des deux à l'unité de
  calcul près : c'est le contrôle que ``scripts/verifier_donnees.py`` exerce.

Et une quatrième, sans équivalent ailleurs : la STRUCTURE des ressources —
cotisations, contribution d'équilibre de l'État à ses propres fonctionnaires,
impôts et taxes affectés, subventions d'équilibre, transferts. Elle n'est pas
décorative. Un système en comptes notionnels se finance par des cotisations
assises sur des revenus ; ces parts-là disent quelle fraction des ressources
actuelles porte ce nom, et donc ce qu'un coefficient d'équilibre supposerait
de reconduire.

POURQUOI LE SCRIPT CHERCHE LE RAPPORT AU LIEU DE L'ADRESSER
------------------------------------------------------------
Le COR republie son rapport chaque année, sous une adresse neuve et des noms de
fichiers qui changent de suffixe (``Données_RA2026_P2.xlsx``,
``Données_RA2026_P3_2.xlsx``…). Écrire l'adresse en dur, c'est récupérer le
millésime de l'année où le script a été écrit. On part donc de la page
d'accueil, on y suit le lien du rapport annuel, et on cherche les figures par
leur TITRE dans tous les classeurs de la page : un titre de figure survit à un
changement de numérotation de partie, un nom de fichier non.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fetch.lecture_xlsx import feuilles  # noqa: E402

RACINE_SITE = "https://www.cor-retraites.fr"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
SORTIE = Path("data/brut/cor_comptes_retraite.json")

#: Lien du rapport annuel sur la page d'accueil du COR.
LIEN_RAPPORT = re.compile(r'href="(/rapports-du-cor/rapport-annuel[^"]*)"')

#: Classeurs de données attachés à la page du rapport.
LIEN_CLASSEUR = re.compile(r'href="(/sites/default/files/[^"]+\.xlsx)"')

#: Titres cherchés, et la clé sous laquelle chaque bloc est écrit. Le titre est
#: comparé sans accents ni casse, sur son DÉBUT seulement : le COR ponctue ses
#: intitulés différemment d'une année à l'autre — double espace, parenthèse
#: ajoutée — mais n'en change pas l'attaque.
FIGURES: tuple[tuple[str, str], ...] = (
    ("comptes", "depenses et ressources du systeme de retraite"),
    ("solde", "solde du systeme de retraite observe et projete"),
    ("structure", "structure des ressources du systeme de retraite de"),
)

#: Marqueurs que le COR met en tête de ligne pour dire ce qui est observé et ce
#: qui est projeté. Ils sont la seule frontière datée entre les deux, et c'est
#: le critère 2 du manifeste qui en dépend.
MARQUEURS = {"obs": "observe", "sc. ref": "projete", "sc ref": "projete"}

#: Bornes du contrôle de vraisemblance des années lues en en-tête.
PREMIERE_ANNEE_PLAUSIBLE, DERNIERE_ANNEE_PLAUSIBLE = 1980, 2120


def _sans_accents(texte: str) -> str:
    plie = unicodedata.normalize("NFD", texte)
    plie = "".join(c for c in plie if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", plie).strip().lower()


def _recuperer(url: str) -> bytes:
    demande = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=180) as reponse:
        return reponse.read()


def page_du_rapport() -> str:
    """Adresse de la page du dernier rapport annuel, lue sur la page d'accueil."""
    accueil = _recuperer(RACINE_SITE + "/").decode("utf-8", "replace")
    liens = LIEN_RAPPORT.findall(accueil)
    if not liens:
        raise LookupError(
            "aucun lien de rapport annuel sur la page d'accueil du COR — "
            "la structure du site a changé"
        )
    return RACINE_SITE + liens[0]


def classeurs(page: str) -> list[str]:
    """Adresses des classeurs de données attachés à la page du rapport."""
    html = _recuperer(page).decode("utf-8", "replace")
    vus: dict[str, None] = {}
    for lien in LIEN_CLASSEUR.findall(html):
        vus[RACINE_SITE + urllib.parse.quote(urllib.parse.unquote(lien))] = None
    return list(vus)


def _annees_en_tete(grille: dict) -> tuple[int, dict[int, int]]:
    """Ligne d'en-tête du premier bloc, et les colonnes qui portent une année.

    Une feuille du COR porte parfois DEUX blocs — le scénario de référence,
    puis des « données complémentaires » sous une autre convention, avec leur
    propre en-tête d'années. Seul le premier est rendu : c'est celui que la
    figure trace, et c'est celui dont les notes de bas de feuille disent le
    champ.
    """
    for ligne in sorted({l for l, _ in grille}):
        colonnes = {
            c: int(v) for (l, c), v in grille.items()
            if l == ligne and isinstance(v, float)
            and PREMIERE_ANNEE_PLAUSIBLE <= v <= DERNIERE_ANNEE_PLAUSIBLE
            and v == int(v)
        }
        if len(colonnes) >= 8:
            return ligne, colonnes
    raise LookupError("aucune ligne d'années dans la feuille")


def lire_bloc(grille: dict) -> list[dict]:
    """Séries d'un bloc de figure : intitulé, marqueur observé/projeté, valeurs.

    L'intitulé se REPORTE d'une ligne à la suivante : le COR écrit « Dépenses »
    une fois et met « Obs » puis « Sc. Ref » dessous, sans le répéter.
    """
    entete, colonnes = _annees_en_tete(grille)
    premiere_colonne = min(colonnes)
    series: list[dict] = []
    intitule = ""
    ligne = entete + 1
    while True:
        valeurs = {
            annee: grille[(ligne, c)] for c, annee in sorted(colonnes.items())
            if isinstance(grille.get((ligne, c)), float)
        }
        if not valeurs:
            break
        textes = [
            grille[(ligne, c)] for c in range(premiere_colonne)
            if isinstance(grille.get((ligne, c)), str) and grille[(ligne, c)].strip()
        ]
        marqueur = ""
        if textes and _sans_accents(textes[-1]) in MARQUEURS:
            marqueur = MARQUEURS[_sans_accents(textes.pop())]
        if textes:
            intitule = textes[-1].strip()
        series.append({"intitule": intitule, "marqueur": marqueur,
                       "valeurs": {str(a): v for a, v in valeurs.items()}})
        ligne += 1
    return series


def _par_marqueur(series: list[dict],
                  intitule: str | None = None) -> dict[str, dict[str, float]]:
    """Les valeurs d'une série, rangées sous ``observe`` et ``projete``.

    ``intitule`` à ``None`` prend la seule série marquée de la feuille : la
    figure du solde n'en porte qu'une, sous un intitulé — « Convention EPR » —
    qui nomme une convention comptable et non la grandeur, et qu'on aurait tort
    de chercher par son nom.

    L'année de jonction est portée par les DEUX marqueurs, pour que la courbe
    du rapport se raccorde sans trou : elle revient ici à l'observé, qui prime
    sur le projeté — c'est le critère 2 du manifeste, et il ne souffre pas
    d'exception quand le producteur donne exactement la même valeur des deux
    côtés.
    """
    cherche = _sans_accents(intitule) if intitule is not None else None
    rangees: dict[str, dict[str, float]] = {"observe": {}, "projete": {}}
    intitules = set()
    for serie in series:
        if not serie["marqueur"]:
            continue
        if cherche is not None and _sans_accents(serie["intitule"]) != cherche:
            continue
        intitules.add(serie["intitule"])
        rangees[serie["marqueur"]].update(serie["valeurs"])
    if len(intitules) > 1:
        raise LookupError(f"séries marquées ambiguës : {sorted(intitules)}")
    for annee in set(rangees["observe"]) & set(rangees["projete"]):
        rangees["projete"].pop(annee)
    if not rangees["observe"]:
        raise LookupError(f"série « {intitule} » introuvable ou sans marqueur")
    return rangees


def blocs(adresses: list[str]) -> dict[str, list[dict]]:
    """Cherche chaque figure par son titre, dans tous les classeurs de la page."""
    trouves: dict[str, list[dict]] = {}
    for adresse in adresses:
        if len(trouves) == len(FIGURES):
            break
        try:
            classeur = feuilles(_recuperer(adresse))
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError):
            continue
        for grille in classeur.values():
            titre = grille.get((0, 0)) or grille.get((0, 1)) or ""
            if not isinstance(titre, str):
                continue
            plie = _sans_accents(titre)
            for cle, attendu in FIGURES:
                if cle in trouves or attendu not in plie:
                    continue
                trouves[cle] = lire_bloc(grille)
    manquantes = [cle for cle, _ in FIGURES if cle not in trouves]
    if manquantes:
        raise LookupError(
            "figures introuvables dans les classeurs du rapport : "
            + ", ".join(manquantes)
        )
    return trouves


def main() -> int:
    try:
        page = page_du_rapport()
        lus = blocs(classeurs(page))
    except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
        print(f"COR indisponible : {erreur}", file=sys.stderr)
        return 1
    except LookupError as erreur:
        print(f"Rapport du COR illisible : {erreur}", file=sys.stderr)
        return 1

    charge = {
        "source": page,
        "unite": "part du produit intérieur brut, en fraction",
        "comptes": {
            "depenses": _par_marqueur(lus["comptes"], "Dépenses"),
            "ressources": _par_marqueur(lus["comptes"], "Ressources"),
            # Le solde est publié à part, et c'est une chance : il ne sert pas
            # à écrire une série de référence mais à CONTRÔLER les deux autres,
            # dont il doit être la différence.
            "solde": _par_marqueur(lus["solde"]),
        },
        "structure": {
            serie["intitule"]: serie["valeurs"] for serie in lus["structure"]
            if serie["intitule"]
        },
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(charge, ensure_ascii=False, indent=1, sort_keys=True),
        encoding="utf-8",
    )

    observe = charge["comptes"]["ressources"]["observe"]
    projete = charge["comptes"]["ressources"]["projete"]
    print(f"{SORTIE} écrit depuis {page}")
    print(f"Observé : {min(observe)}-{max(observe)} ; "
          f"projeté : {min(projete)}-{max(projete)}")
    print(f"Structure des ressources : {len(charge['structure'])} postes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
