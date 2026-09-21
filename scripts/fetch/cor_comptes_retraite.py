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

Et une cinquième, depuis le rapport de 2023 seulement : la VENTILATION du
poste « transferts d'organismes extérieurs » de la dernière année de chaque
rapport — « dont CNAF », « dont Unédic », autres —, en milliards d'euros. Elle
ne fait pas série à elle seule, quatre années au plus ; elle CONTRÔLE la série
que ``ccss_transferts_retraite.py`` va chercher chez le producteur, et c'est
pour cela qu'on la lit dans chaque rapport annuel encore en ligne, et non dans
le seul dernier.

Et une sixième, qui règle une question que le dépôt tranchait par déduction :
le TAUX DE PRÉLÈVEMENT, en part des revenus d'activité, observé de 2002 à 2025
et projeté jusqu'en 2070 (figure « Les déterminants de l'évolution des
ressources du système de retraite »). Les ressources du COR reculent en part de
PIB sur l'horizon projeté — 13,95 % en 2025, 12,91 % en 2070 —, et rien, dans
les deux colonnes du compte, ne dit si c'est l'assiette qui rétrécit ou le taux
qui baisse. La réponse change tout pour qui veut chiffrer ce qu'un taux unique
rapporterait : elle est ici, et c'est le TAUX qui baisse, de 32,14 % à 30,05 %,
l'assiette restant à peu près stable en part de PIB. Le dépôt supposait
l'inverse.

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

#: La page qui liste tous les rapports du COR, et les rapports annuels qu'on y
#: reconnaît à leur adresse — « évolutions et perspectives des retraites en
#: France », depuis 2014.
LISTE_RAPPORTS = RACINE_SITE + "/documents/rapports-du-cor?page={page}"
LIEN_ANNUEL = re.compile(
    r'href="(/rapports-du-cor/[^"]*evolutions-perspectives-retraites-france[^"]*)"'
)

#: Intitulé de la série cherchée dans la figure des déterminants des
#: ressources. La figure en porte deux — le taux de prélèvement et la
#: contribution de l'État aux régimes équilibrés — et il faut donc la nommer.
INTITULE_TAUX = "Taux de prélèvement en % des revenus d'activité"

#: Lignes de la ventilation des transferts, du libellé du COR au code du dépôt.
#: Le tableau porte le total des ressources en dernière ligne, sous deux noms.
LIGNES_VENTILATION: tuple[tuple[str, str], ...] = (
    ("transferts", "transferts externes"),
    ("cnaf", "dont cnaf"),
    ("unedic", "dont unedic"),
    ("autres", "autres transferts externes"),
    ("produits_financiers", "produits financiers"),
    ("total_ressources", "total ressources"),
    ("total_ressources", "total financement"),
)

#: Classeurs de données attachés à la page du rapport.
LIEN_CLASSEUR = re.compile(r'href="(/sites/default/files/[^"]+\.xlsx)"')

#: Les deux figures de SENSIBILITÉ, et la dimension que chacune fait varier.
#: Le COR y republie la dépense et le solde du système, sous la MÊME convention
#: et le MÊME champ que le compte principal, une ligne par variante. C'est la
#: seule publication qui dise ce qu'une hypothèse déplace sans changer de
#: périmètre, et le dépôt n'en lisait aucune jusqu'au 21 septembre 2026.
SENSIBILITES: tuple[tuple[str, str], ...] = (
    ("productivite",
     "sensibilite de la part des depenses et du solde du systeme de retraite "
     "dans le pib a l'hypothese de croissance de la productivite"),
    ("chomage",
     "sensibilite de la part des depenses et du solde du systeme de retraite "
     "dans le pib aux hypotheses de taux de chomage"),
)

#: Les deux grandeurs que porte une figure de sensibilité, reconnues au DÉBUT
#: de leur intitulé : la figure du chômage écrit « Soldes » au pluriel.
GRANDEURS_SENSIBILITE: tuple[tuple[str, str], ...] = (
    ("depenses", "depenses"),
    ("solde", "solde"),
)

#: Titres cherchés, et la clé sous laquelle chaque bloc est écrit. Le titre est
#: comparé sans accents ni casse, sur son DÉBUT seulement : le COR ponctue ses
#: intitulés différemment d'une année à l'autre — double espace, parenthèse
#: ajoutée — mais n'en change pas l'attaque.
FIGURES: tuple[tuple[str, str], ...] = (
    ("comptes", "depenses et ressources du systeme de retraite"),
    ("solde", "solde du systeme de retraite observe et projete"),
    ("structure", "structure des ressources du systeme de retraite de"),
    ("determinants", "evolution des ressources du systeme de retraite dans le sc"),
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


#: Titre du SECOND bloc de la figure des ressources : la même grandeur sous
#: l'autre convention comptable du COR. Comparé sans accents ni casse.
TITRE_EEC = "donnees complementaires : convention eec"


def lire_bloc_eec(grille: dict) -> dict[str, dict[str, float]]:
    """Les ressources sous la convention EEC, variante de productivité par variante.

    POURQUOI CE SECOND LECTEUR EXISTE. ``_annees_en_tete`` s'arrête au premier
    bloc de la feuille, et c'est voulu : c'est celui que la figure trace. Mais
    la feuille des ressources en porte un second, sous l'autre convention du
    COR, et c'est la seule publication française qui chiffre ce que la
    convention comptable déplace. Le premier bloc ne peut pas le donner.

    CE QUE LES DEUX CONVENTIONS SONT. Sous **EPR**, les contributions et
    subventions d'équilibre « évoluent de manière à équilibrer chaque année le
    solde » des régimes de fonctionnaires et des régimes spéciaux : l'État paie
    exactement ce qu'il faut, et ces régimes ne montrent jamais de déficit.
    Sous **EEC**, son effort est figé en part de PIB. Les besoins de ces
    régimes reculant en projection, l'État y paie plus que nécessaire, et les
    ressources du système sont plus hautes : c'est pourquoi le solde EEC est le
    plus favorable des deux, ce qui surprend qui lit « effort constant » comme
    une hypothèse sévère.

    CE QUE LE LECTEUR REND, ET CE QU'IL NE CHOISIT PAS. Les quatre lignes
    projetées du bloc sont étiquetées par leur hypothèse de productivité, et
    non par un nom. Le script les rend TOUTES, sous leur étiquette ; choisir
    celle du scénario de référence est le travail de ``verifier_donnees.py``,
    qui lit cette hypothèse dans le fichier du dépôt. Un récupérateur qui
    trancherait ici figerait un scénario dans une couche qui ne le connaît pas.
    """
    lignes = sorted({l for l, _ in grille})
    depart = next(
        (l for l in lignes
         if isinstance(grille.get((l, 0)) or grille.get((l, 1)), str)
         and _sans_accents(grille.get((l, 0)) or grille.get((l, 1))).startswith(TITRE_EEC)),
        None,
    )
    if depart is None:
        raise LookupError("bloc « convention EEC » introuvable dans la figure")

    colonnes: dict[int, int] = {}
    for ligne in lignes:
        if ligne <= depart:
            continue
        trouvees = {
            c: int(v) for (l, c), v in grille.items()
            if l == ligne and isinstance(v, float)
            and PREMIERE_ANNEE_PLAUSIBLE <= v <= DERNIERE_ANNEE_PLAUSIBLE
            and v == int(v)
        }
        if len(trouvees) >= 8:
            colonnes = trouvees
            entete = ligne
            break
    if not colonnes:
        raise LookupError("aucune ligne d'années sous le bloc « convention EEC »")

    variantes: dict[str, dict[str, float]] = {}
    for ligne in lignes:
        if ligne <= entete:
            continue
        etiquette = grille.get((ligne, 2))
        if not isinstance(etiquette, float):
            continue
        valeurs = {
            str(annee): grille[(ligne, c)] for c, annee in sorted(colonnes.items())
            if isinstance(grille.get((ligne, c)), float)
        }
        if len(valeurs) >= 8:
            # L'étiquette est une hypothèse de productivité — 0,007 pour le
            # scénario de référence de 2026 —, écrite telle que le classeur la
            # porte, à l'arrondi du millième près.
            variantes[f"{round(etiquette, 4):g}"] = valeurs
    if not variantes:
        raise LookupError("aucune variante chiffrée sous le bloc « convention EEC »")
    return variantes


def _etiquette_variante(valeur) -> str | None:
    """Le nom sous lequel une ligne de variante est écrite dans le JSON.

    LE RÉCUPÉRATEUR NE NOMME PAS LES SCÉNARIOS, IL LES TRANSCRIT. Le COR
    étiquette ses variantes de productivité par leur HYPOTHÈSE — 0,01 et
    0,004 — et ses variantes de chômage par un libellé — « Var C5% », « Var
    C10% ». Traduire l'un ou l'autre en « haute » et « basse » ici figerait
    dans une couche qui ne connaît pas les scénarios du dépôt un partage qui
    leur appartient : c'est ``verifier_donnees.py`` qui rapproche ces
    étiquettes de ``hypotheses_projection.yaml``, comme il le fait déjà pour
    le bloc EEC. Seule exception, le marqueur du scénario de référence, qui
    est le même mot dans toutes les figures du COR et qu'on normalise.
    """
    if isinstance(valeur, float):
        return f"{round(valeur, 4):g}"
    if not isinstance(valeur, str) or not valeur.strip():
        return None
    plie = _sans_accents(valeur)
    if plie in MARQUEURS:
        return "reference" if MARQUEURS[plie] == "projete" else None
    return plie


def lire_sensibilite(grille: dict) -> dict[str, dict[str, dict[str, float]]]:
    """Une figure de sensibilité : la dépense et le solde, variante par variante.

    POURQUOI UN TROISIÈME LECTEUR. ``lire_bloc`` s'arrête au premier bloc de la
    feuille et range les lignes sous ``observe``/``projete`` ; une figure de
    sensibilité porte DEUX blocs — la dépense, puis le solde —, chacun avec son
    propre en-tête d'années, et ses lignes ne se distinguent pas par un
    marqueur temporel mais par une VARIANTE. Les deux rangements n'ont rien de
    commun.

    CE QUE LE LECTEUR REND. ``{grandeur: {variante: {année: part de PIB}}}``,
    la grandeur valant ``depenses`` ou ``solde``. La ligne ``Obs`` est écartée :
    elle est la même dans toutes les variantes, elle est déjà dans le compte
    principal, et une observation n'appartient à aucun scénario.

    CE QU'IL NE REND PAS : les RESSOURCES. Le COR ne les publie pas dans ces
    figures — il y donne la dépense et le solde, et la ressource en est la
    somme. Cette dérivation est le travail de ``verifier_donnees.py``, qui la
    contrôle d'abord sur le scénario de référence, où les trois grandeurs sont
    publiées séparément.
    """
    lignes = sorted({l for l, _ in grille})
    entetes: dict[int, dict[int, int]] = {}
    for ligne in lignes:
        annees = {
            c: int(v) for (l, c), v in grille.items()
            if l == ligne and isinstance(v, float)
            and PREMIERE_ANNEE_PLAUSIBLE <= v <= DERNIERE_ANNEE_PLAUSIBLE
            and v == int(v)
        }
        if len(annees) >= 8:
            entetes[ligne] = annees
    if not entetes:
        raise LookupError("aucune ligne d'années dans la figure de sensibilité")

    # UN SEUL PASSAGE, ET LES EN-TÊTES SERVENT DE BORNES. Les deux blocs se
    # suivent sans ligne vide entre eux : une boucle qui s'arrêterait à la
    # première ligne sans valeur lirait l'en-tête du second bloc comme une
    # donnée, puis son intitulé, et rangerait la dépense sous « solde ». La
    # grandeur est donc portée par la ligne qui la nomme, et réécrite à chaque
    # intitulé reconnu.
    lu: dict[str, dict[str, dict[str, float]]] = {}
    grandeur = ""
    annees: dict[int, int] = {}
    for ligne in lignes:
        if ligne in entetes:
            annees = entetes[ligne]
            continue
        if not annees:
            continue
        premiere = min(annees)
        intitule = grille.get((ligne, premiere - 2))
        if isinstance(intitule, str) and intitule.strip():
            plie = _sans_accents(intitule)
            grandeur = next(
                (code for code, debut in GRANDEURS_SENSIBILITE
                 if plie.startswith(debut)), "")
        etiquette = _etiquette_variante(grille.get((ligne, premiere - 1)))
        if not grandeur or not etiquette:
            continue
        valeurs = {
            str(annee): grille[(ligne, c)] for c, annee in sorted(annees.items())
            if isinstance(grille.get((ligne, c)), float)
        }
        if valeurs:
            lu.setdefault(grandeur, {})[etiquette] = valeurs

    manquantes = [code for code, _ in GRANDEURS_SENSIBILITE if code not in lu]
    if manquantes:
        raise LookupError(
            "grandeurs absentes de la figure de sensibilité : "
            + ", ".join(manquantes)
        )
    references = [code for code, variantes in lu.items() if "reference" not in variantes]
    if references:
        raise LookupError(
            "figure de sensibilité sans son scénario de référence : "
            + ", ".join(sorted(references))
        )
    return lu


def sensibilites(adresses: list[str]) -> dict[str, dict[str, dict[str, dict[str, float]]]]:
    """Les figures de sensibilité de ``SENSIBILITES``, cherchées par leur titre."""
    trouves: dict[str, dict] = {}
    for adresse in adresses:
        if len(trouves) == len(SENSIBILITES):
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
            for cle, attendu in SENSIBILITES:
                if cle not in trouves and attendu in plie:
                    trouves[cle] = lire_sensibilite(grille)
    manquantes = [cle for cle, _ in SENSIBILITES if cle not in trouves]
    if manquantes:
        raise LookupError(
            "figures de sensibilité introuvables dans les classeurs du "
            "rapport : " + ", ".join(manquantes)
        )
    return trouves


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


def bloc_eec(adresses: list[str]) -> dict[str, dict[str, float]]:
    """Cherche la figure des ressources et y lit son second bloc."""
    for adresse in adresses:
        try:
            classeur = feuilles(_recuperer(adresse))
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError):
            continue
        for grille in classeur.values():
            titre = grille.get((0, 0)) or grille.get((0, 1)) or ""
            if not isinstance(titre, str):
                continue
            plie = _sans_accents(titre)
            if "ressources du systeme de retraite en %" not in plie:
                continue
            if TITRE_EEC not in _sans_accents(" ".join(
                    v for v in grille.values() if isinstance(v, str))):
                continue
            return lire_bloc_eec(grille)
    raise LookupError("figure des ressources sans bloc « convention EEC »")


def pages_annuelles() -> list[str]:
    """Les pages des rapports annuels, du plus récent au plus ancien.

    L'ordre se lit dans l'adresse, qui porte l'année du rapport ; la liste du
    site n'en garantit aucun.
    """
    pages: dict[str, None] = {}
    for numero in range(8):
        try:
            html = _recuperer(LISTE_RAPPORTS.format(page=numero)).decode("utf-8", "replace")
        except urllib.error.HTTPError:
            break
        liens = LIEN_ANNUEL.findall(html)
        if not liens:
            break
        for lien in liens:
            pages[RACINE_SITE + lien] = None

    def annee(page: str) -> int:
        m = re.search(r"(20\d\d)", page)
        return int(m.group(1)) if m else 0

    return sorted(pages, key=annee, reverse=True)


def lire_ventilation(grille: dict) -> dict[str, float] | None:
    """Les lignes de la ventilation des transferts, en millions d'euros.

    Le tableau du COR est en milliards ; on le porte en millions, l'unité des
    rapports à la CCSS avec lesquels ``verifier_donnees.py`` le confronte.
    """
    valeurs: dict[str, float] = {}
    for (ligne, colonne), cellule in grille.items():
        if colonne != 1 or not isinstance(cellule, str):
            continue
        plie = _sans_accents(cellule)
        for code, attendu in LIGNES_VENTILATION:
            if plie.startswith(attendu) and code not in valeurs:
                montant = grille.get((ligne, 2))
                if isinstance(montant, float):
                    valeurs[code] = round(montant * 1000.0, 1)
    if {"transferts", "cnaf", "unedic"} <= set(valeurs):
        return valeurs
    return None


def ventilations(pages: list[str]) -> dict[str, dict[str, float]]:
    """La ventilation des transferts de chaque rapport annuel qui la publie.

    Les rapports sont pris du plus récent au plus ancien, et la lecture
    s'arrête au premier qui ne porte pas le tableau : le COR ne le publie que
    depuis 2023, et rien ne justifie de télécharger les classeurs des neuf
    rapports d'avant pour le vérifier à chaque fois.
    """
    trouvees: dict[str, dict[str, float]] = {}
    for page in pages:
        annee_lue = None
        for adresse in classeurs(page):
            try:
                classeur = feuilles(_recuperer(adresse))
            except (urllib.error.HTTPError, urllib.error.URLError, ValueError):
                continue
            for grille in classeur.values():
                titre = grille.get((0, 0)) or grille.get((0, 1)) or ""
                if not isinstance(titre, str):
                    continue
                m = re.search(r"systeme de retraite en (20\d\d)", _sans_accents(titre))
                if not m or "structure" not in _sans_accents(titre):
                    continue
                valeurs = lire_ventilation(grille)
                if valeurs:
                    annee_lue = m.group(1)
                    trouvees[annee_lue] = valeurs
                    break
            if annee_lue:
                break
        if annee_lue is None:
            break
    return trouvees


def main() -> int:
    try:
        page = page_du_rapport()
        adresses = classeurs(page)
        lus = blocs(adresses)
        eec = bloc_eec(adresses)
        sensibilite = sensibilites(adresses)
        ventilation = ventilations(pages_annuelles())
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
        # En part des REVENUS D'ACTIVITÉ, et non du PIB : c'est le taux que le
        # COR projette lui-même, et le seul endroit où il dise si ses
        # ressources reculent parce que l'assiette rétrécit ou parce que le
        # taux baisse. Voir INTITULE_TAUX.
        "taux_prelevement": _par_marqueur(lus["determinants"], INTITULE_TAUX),
        # Les ressources sous l'AUTRE convention du COR, variante de
        # productivité par variante : la seule publication française qui
        # chiffre ce qu'une convention comptable déplace. Voir lire_bloc_eec.
        "ressources_eec": eec,
        # La dépense et le solde du MÊME compte, variante par variante, sur
        # les deux dimensions que le COR fait varier séparément : la
        # productivité et le chômage. La ressource n'y est pas publiée ; elle
        # est la somme des deux, et verifier_donnees.py contrôle cette
        # dérivation sur le scénario de référence avant de s'en servir.
        "sensibilite": sensibilite,
        # En MILLIONS d'euros, contrairement au reste : c'est un contrôle de la
        # série des rapports à la CCSS, qui sont écrits dans cette unité.
        "ventilation_transferts": ventilation,
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
    print(f"Ventilation des transferts : {', '.join(sorted(ventilation)) or 'aucune'}")
    for dimension, grandeurs in sorted(sensibilite.items()):
        variantes = sorted(grandeurs["depenses"])
        print(f"Sensibilité {dimension} : {', '.join(variantes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
