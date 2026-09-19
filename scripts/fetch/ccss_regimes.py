#!/usr/bin/env python3
"""Effectifs et masses de CHAQUE régime, dans les rapports à la CCSS.

    python scripts/fetch/ccss_regimes.py [--depuis 2013] [--jusqu 2026]

CE QU'ON VIENT CHERCHER, ET POURQUOI C'EST LÀ
----------------------------------------------
Chaque fiche de régime d'un rapport à la Commission des comptes de la Sécurité
sociale ouvre sur un « Tableau 1 • Données générales » qui porte, année par
année et pour le régime seul :

* ``Cotisants vieillesse`` et ``Bénéficiaires vieillesse``, ces derniers
  ventilés entre droit direct et droit dérivé seul ;
* ``Produits nets`` et ``dont cotisations nettes`` ;
* ``Charges nettes`` et ``dont prestations nettes``.

C'est la seule source qui donne les EFFECTIFS et les MASSES d'un régime dans le
même tableau, à l'unité et au million d'euros près. La fiche 4.1, que
``docs/feuille_de_route.md`` documente sous l'action 35, n'en est qu'un extrait
— les cotisants, sans les masses, et sans le régime général.

Un rapport porte quatre ou cinq exercices. On ne retient d'un rapport que les
années ANTÉRIEURES à sa parution — les comptes clos, jamais les prévisions
marquées « (p) » —, et quand plusieurs rapports donnent la même année, c'est le
PREMIER qui l'arrête qui l'emporte. C'est la règle que
``ccss_transferts_retraite.py`` a établie et qu'on ne change pas ici : les
rapports suivants reprennent une année pour mémoire, parfois sur un périmètre
révisé.

CE QUE CE SCRIPT NE FAIT PAS, ET IL FAUT LE DIRE
-------------------------------------------------
**Il ne moissonne pas les quarante-sept millésimes.** Les rapports remontent à
1979 et le lecteur PDF du dépôt les ouvre presque tous — le recensement est
sous l'action 35 —, mais la mise en page des fiches de régime n'est stable que
depuis le milieu des années 2010. Avant, chaque époque a la sienne, et les
tableaux ne portent pas les mêmes lignes. Ce script lit la mise en page
MODERNE ; ce qu'il ne sait pas lire, il le compte et le dit, plutôt que de
rendre une série trouée sans prévenir.

Le lecteur du dépôt échoue en outre sur quelques rapports — celui de 2012 ne
rend que deux lignes. Ils sont signalés dans le fichier produit.

CE QUE LE FICHIER PRODUIT CONTIENT
-----------------------------------
Une table longue : régime, série, année, valeur, et le rapport qui l'arrête.
Le libellé de série est celui du rapport, recopié tel quel et seulement replié
— les rapports écrivent « Cotisantsvieillesse » sans espace, la mise en page
les ayant mangés.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ccss_transferts_retraite as CCSS  # noqa: E402
from lecture_pdf import lignes_par_page, lignes_pdf  # noqa: E402

SORTIE = Path("data/brut/ccss_regimes.json")
CACHE = Path("data/brut/ccss_rapports")

#: Une entrée du sommaire : « 5.6 Régime spécial des agents de la SNCF .... 190 ».
#: Le numéro de chapitre N'EST PAS figé : les fiches de régime sont au
#: chapitre 5 en 2019 et ailleurs en 2017, où le 5 porte « du régime général
#: aux autres régimes de base ». Les chercher au chapitre 5 ne rendait qu'un
#: régime pour ce millésime — d'où l'agnosticisme.
SOMMAIRE = re.compile(r"^(\d\.\d+)\s*(.{6,90}?)\s*\.{4,}")
#: Le numéro de fiche, répété en tête de chaque page de la fiche.
MARQUEUR = re.compile(r"^(\d\.\d+)\b")
#: Le même numéro, mais collé à la FIN d'une ligne. La mise en page l'y pousse
#: quand la tête de page tombe à hauteur d'une note : le rapport de 2022 écrit
#: « correspond à la moyenne de ces deux taux . 5.6 ». Six pages à tableau
#: n'avaient aucun marqueur en début de ligne, cinq l'avaient en fin.
MARQUEUR_FIN = re.compile(r"(?:^|\s)(\d\.\d+)\s*$")
#: Le titre du tableau, dont la mise en page mange parfois les espaces.
TABLEAU = re.compile(r"onn[ée]es\s?g[ée]n[ée]rales", re.I)
#: Au-delà, l'en-tête d'années n'appartient plus au tableau.
PORTEE_ENTETE = 30
#: Au-delà, le marqueur de fiche trouvé en remontant n'est plus le bon.
PORTEE_FICHE = 120
#: Une ligne de tableau doit porter au moins ça de libellé.
LIBELLE_MINIMUM = 6


#: Le même régime change de graphie d'un rapport à l'autre : la mise en page
#: mange les espaces à des endroits différents — « Régimespécial des agents
#: delaSNCF », « Régime spécial des agents de la SNCF », « Régime spécial
#: desagents de la SNCF » — et les polices à encodage propre rendent certains
#: titres en charabia. Cinquante et un libellés pour une vingtaine de caisses :
#: sans cette table, la série est inexploitable. On reconnaît donc le régime à
#: un MOTIF distinctif, cherché dans le titre replié, sans espaces ni accents.
#: L'ordre compte : le plus spécifique d'abord.
CANONIQUES: tuple[tuple[str, str], ...] = (
    ("brancheMALADIE", "rsi_maladie"),          # jamais fondu dans le RSI vieillesse
    ("brancheVIEILLESSE", "rsi_vieillesse"),
    ("independants", "rsi"),
    # « salaries » tout court attrapait « NON-salariés » : deux fiches d'un
    # même rapport tombaient sur msa_salaries, qui se contredisait alors
    # lui-même — 659 061 contre 522 534 cotisants en 2012. Les motifs agricoles
    # exigent donc « agricole », et jamais le mot seul.
    # Le RCO des exploitants s'intitule « retraite complémentaire obligatoire
    # des NON-SALARIÉS AGRICOLES », qui porte « salariesagricoles » en
    # sous-chaîne : sans cette ligne en tête, il tombait sur msa_salaries, qui
    # se contredisait alors lui-même — 659 061 contre 522 534 cotisants.
    ("retraitecomplementaireobligatoire", "msa_exploitants_complementaire"),
    ("nonsalariesagricoles", "msa_exploitants"),
    ("exploitantsagricoles", "msa_exploitants"),
    ("salariesagricoles", "msa_salaries"),
    ("agricoledessalaries", "msa_salaries"),
    ("agricoledesexploitants", "msa_exploitants"),
    ("cnracl", "cnracl"),
    ("territoriaux", "cnracl"),
    ("canssm", "canssm"),
    ("danslesmines", "canssm"),
    ("desmines", "canssm"),
    # L'Agirc et l'Arrco n'ont fusionné qu'au 1er janvier 2019 : avant, ce sont
    # DEUX régimes, avec deux fiches et deux comptes. Les fondre sous un seul
    # code mélangeait leurs séries d'avant-fusion.
    ("agircarrco", "agirc_arrco"),
    ("agirc", "agirc"),
    ("arrco", "arrco"),
    ("sncf", "sncf"),
    ("ratp", "ratp"),
    ("crpcen", "crpcen"),
    ("clercs", "crpcen"),
    ("cnieg", "cnieg"),
    ("electriques", "cnieg"),
    ("fspoeie", "fspoeie"),
    ("enim", "enim"),
    ("invalidesdelamarine", "enim"),
    ("cnavpl", "cnavpl"),
    ("professionsliberales", "cnavpl"),
    ("ircantec", "ircantec"),
    ("banquedefrance", "banque_de_france"),
    ("cnbf", "cnbf"),
    ("barreaufrancais", "cnbf"),
    ("cultes", "cavimac"),
    ("saspa", "saspa"),
    ("personnesagees", "saspa"),
    ("navig", "crpnpac"),
    ("fonctionnairescivilsetmilitaires", "fonction_publique_etat"),
    ("autresregimes", "autres_regimes"),
)

#: Les accents et les espaces sautent avant la reconnaissance : les titres les
#: portent de façon instable.
ACCENTS = str.maketrans("àâäéèêëîïôöùûüç", "aaaeeeeiioouuuc")

#: Ces caisses ont DEUX fiches dans le même rapport, une pour leur régime de
#: base et une pour leur complémentaire, et le motif ne les distingue pas.
#: Les fondre faisait dire à un même rapport deux chiffres pour la même
#: case — 57 536 et 53 269 cotisants à la CNBF en 2012 —, et douze des
#: dix-sept conflits « un rapport contre lui-même » venaient de là.
A_DEUX_ETAGES = frozenset({"cnbf", "cnavpl", "msa_exploitants", "rci"})


def canonique(titre: str) -> str | None:
    """Le code de caisse d'un titre de fiche, ou ``None`` si on ne le reconnaît pas.

    Le suffixe ``_complementaire`` n'est posé que pour les caisses qui ont
    vraiment les deux étages : l'Agirc-Arrco ou l'Ircantec SONT des régimes
    complémentaires, et leur accoler le suffixe n'apprendrait rien.
    """
    nu = titre.lower().translate(ACCENTS)
    nu = "".join(c for c in nu if c.isalnum())
    if "nonsalaries" in nu and "agricole" not in nu:
        return None          # « régimes de non-salariés non agricoles » : pas une caisse
    for motif, code in CANONIQUES:
        if motif.lower() in nu:
            if code in A_DEUX_ETAGES and "complementaire" in nu:
                return code + "_complementaire"
            return code
    return None


def _replie(texte: str) -> str:
    return " ".join(texte.split())


def rapports_tous() -> dict[int, str]:
    """Un rapport par millésime, SANS le plancher de 2013.

    ``ccss_transferts_retraite.rapports()`` écarte tout ce qui précède
    ``PREMIERE_ANNEE_LISIBLE``. Ce plancher est juste pour les séries que ce
    module-là certifie, et faux ici : le recensement de l'archive montre que
    quarante des quarante-sept millésimes s'ouvrent. On refait donc le tri, à
    l'identique pour le reste — l'automne de préférence, le printemps sinon.
    """
    page = CCSS._recuperer(CCSS.PAGE_RAPPORTS).decode("utf-8", "replace")
    par_annee: dict[int, list[str]] = {}
    for lien, annee in CCSS.LIEN_RAPPORT.findall(page):
        if not lien.startswith("http"):
            lien = CCSS.RACINE_SITE + lien
        par_annee.setdefault(int(annee), []).append(lien)
    choisis: dict[int, str] = {}
    for annee, liens in par_annee.items():
        noms = {l: l.rsplit("/", 1)[-1] for l in liens}
        automne = [l for l in liens if CCSS.AUTOMNE.search(noms[l])]
        printemps = [l for l in liens if CCSS.PRINTEMPS.search(noms[l])]
        choisis[annee] = (automne or printemps or liens)[0]
    if not choisis:
        raise LookupError("aucun rapport à la CCSS sur la page qui les liste")
    return dict(sorted(choisis.items()))


#: Ce qui, dans un titre de tableau, ne distingue rien : le numéro, la puce,
#: les mots « données générales » eux-mêmes. Ce qui reste — « toutes
#: branches », « ensemble des risques », « régime unifié » — est le
#: qualificatif qui sépare deux tableaux d'une même fiche.
BRUIT_TITRE = re.compile(
    r"tableau\s*\d*|donn[ée]es?\s*g[ée]n[ée]rales?|[^\w\s]", re.I
)


def _cle_tableau(ligne: str) -> str:
    """Le qualificatif d'un tableau, réduit à ce qui le distingue.

    Le titre doit servir de CLÉ D'UN RAPPORT À L'AUTRE : c'est lui qui sépare
    « Données générales — toutes branches » de la vieillesse seule. Mais la
    mise en page l'écrit « Donnéesgénérales » ici et « Données générales » là,
    et le garder brut fragmentait la clé entre millésimes : la confrontation
    entre rapports, qui est tout l'intérêt du garde-fou, tombait de 30 % à
    19 % des valeurs. On réduit donc le titre à son qualificatif, sans
    espaces, sans accents et sans ponctuation.
    """
    nu = _replie(ligne).lower().translate(ACCENTS)
    nu = BRUIT_TITRE.sub(" ", nu)
    return " ".join(nu.split())


def sommaire(lignes: list[str]) -> dict[str, str]:
    """Numéro de fiche -> titre, lu au sommaire du rapport."""
    titres: dict[str, str] = {}
    for ligne in lignes[:600]:
        m = SOMMAIRE.match(ligne.strip())
        if m:
            titres.setdefault(m.group(1), _replie(m.group(2)))
    return titres


def _fiche_de_la_page(page: list[str]) -> str | None:
    """Le numéro de fiche que porte cette page, s'il est unique.

    LE NUMÉRO DE FICHE EST UNE TÊTE DE PAGE : il vaut pour la page qui le
    porte, et pour elle seule. Le chercher en remontant depuis le tableau,
    comme le faisait ce module, suppose que le flux sorte les pages dans
    l'ordre du document — ce qui est faux. **Le rapport de 2025 les sort dans
    l'ordre INVERSE des fiches** : 4.15, puis 4.14, puis 4.13… Le marqueur le
    plus proche au-dessus d'un tableau y est donc celui de la fiche VOISINE.
    C'est ainsi qu'un tableau « de la branche vieillesse de la CNRACL » se
    retrouvait porté au crédit de la SNCF, et que la CNRACL héritait du SRE.

    Deux remèdes avaient été tentés avant celui-ci, et tous deux ont fait
    pire : préférer le titre du tableau quand il nomme le régime, et délimiter
    les fiches par intervalles. Le bon niveau n'était ni l'un ni l'autre, mais
    la PAGE, qu'il a fallu exposer dans ``lecture_pdf``.

    Une page qui porte deux numéros différents est ambiguë — un pied de page
    de fin de fiche et une tête de page de la suivante — et on ne devine pas :
    on rend ``None``, et le tableau part aux orphelins.
    """
    marques = {m.group(1) for m in
               (MARQUEUR.match(l.strip()) for l in page) if m}
    if len(marques) == 1:
        return marques.pop()
    if marques:
        return None          # page ambiguë : on ne devine pas
    # Rien en début de ligne : le numéro est peut-être collé en fin.
    tardifs = {m.group(1) for m in
               (MARQUEUR_FIN.search(l.strip()) for l in page) if m}
    return tardifs.pop() if len(tardifs) == 1 else None


def _entete(lignes: list[str], rang: int) -> tuple[int, list] | None:
    """La première ligne d'années sous le titre du tableau.

    LES ANNÉES DOIVENT ÊTRE STRICTEMENT CROISSANTES, et c'est tout l'enjeu.
    Se contenter de « non décroissantes » faisait passer une NOTE DE BAS DE
    PAGE pour un en-tête : « (***) Le taux de cotisation T2 a été fixé à
    11,81 % entre le 1er janvier 2017 et le 30 avril 2017, puis… » porte trois
    fois 2017 et se lisait en colonnes [%, 2017, 2017, %, 2017]. Toute la
    fiche de la SNCF était alors datée de 2017, ce qui donnait quatre valeurs
    différentes pour cette seule année selon le rapport lu — 21, 34, 69 puis
    116 — et expliquait à lui seul cinquante-trois des conflits.
    """
    for j in range(rang, min(rang + PORTEE_ENTETE, len(lignes))):
        colonnes = CCSS._colonnes(lignes[j])
        annees = [a for a, _ in (c for c in colonnes if c is not None)]
        if len(annees) >= 3 and all(x < y for x, y in zip(annees, annees[1:])):
            return j, colonnes
    return None


def lire_tableau(lignes: list[str], depart: int, colonnes: list) -> dict[str, dict[int, float]]:
    """Les lignes chiffrées qui suivent l'en-tête, jusqu'au tableau suivant."""
    valeurs: dict[str, dict[int, float]] = {}
    for ligne in lignes[depart + 1:depart + 60]:
        if TABLEAU.search(ligne):
            break
        libelle = CCSS._libelle(ligne).strip()
        if len(libelle) < LIBELLE_MINIMUM:
            continue
        lus = CCSS._valeurs(ligne, libelle, colonnes)
        if lus:
            valeurs.setdefault(_replie(libelle), {}).update(lus)
    return valeurs


def lire_rapport(annee_rapport: int, octets: bytes) -> tuple[dict, int]:
    """Les tableaux « Données générales » d'un rapport, par régime.

    On parcourt PAGE PAR PAGE, parce que c'est la page qui dit à quelle fiche
    un tableau appartient. La fenêtre de lecture déborde sur la page suivante :
    un tableau annoncé en bas d'une page a ses lignes sur l'autre, et le
    tronquer à la page perdait la moitié des séries.

    Rend aussi le nombre de tableaux qu'on a vus sans savoir à quel régime les
    rattacher : c'est la mesure de ce que la mise en page de l'époque refuse.
    """
    pages = lignes_par_page(octets)
    titres = sommaire([l for page in pages for l in page])
    trouves: dict[tuple[str, str, str], dict[str, dict[int, float]]] = {}
    orphelins = 0
    for numero, page in enumerate(pages):
        if not any(TABLEAU.search(l) for l in page):
            continue
        fiche = _fiche_de_la_page(page)
        regime = titres.get(fiche or "")
        code = canonique(regime) if regime else None
        # La fenêtre déborde sur DEUX pages : un tableau annoncé en bas d'une
        # page a son en-tête sur la suivante et ses dernières lignes sur celle
        # d'après. S'arrêter à une seule page voisine faisait tomber le rapport
        # de 2026 de 407 valeurs à 107.
        suite = page + [l for autre in pages[numero + 1:numero + 3] for l in autre]
        for i, ligne in enumerate(page):
            if not TABLEAU.search(ligne):
                continue
            if code is None:
                orphelins += 1
                continue
            tete = _entete(suite, i)
            if tete is None:
                continue
            rang, colonnes = tete
            tableau = _cle_tableau(ligne)
            for libelle, annees in lire_tableau(suite, rang, colonnes).items():
                cible = trouves.setdefault((code, regime, tableau), {}).setdefault(libelle, {})
                for a, v in annees.items():
                    if a < annee_rapport:      # jamais une prévision
                        cible[a] = v
    return trouves, orphelins


#: Deux rapports qui donnent la même année du même régime doivent tomber
#: d'accord. Un écart relatif au-delà de ce seuil n'est pas un arrondi : c'est
#: une colonne lue de travers, ou un périmètre révisé. On n'arbitre pas — on
#: écarte, et on le dit.
ECART_TOLERE = 0.01


def _reconcilier(serie: dict) -> tuple[list[dict], list[dict]]:
    """Ne garde que ce sur quoi les rapports s'accordent.

    La moisson d'avant 2013 l'exige. Les rapports de 2000 à 2006 sont des scans
    océrisés : la reconstitution de mise en page y sépare les milliers — « 2
    937,4 » ressort en « 937,4 » d'un côté et « 2 » de l'autre — et met les
    colonnes dans le désordre une fois sur quatre. Une lecture isolée n'y est
    donc pas fiable, et la seule défense qui ne demande pas de juger sur le
    fond est la REDONDANCE : chaque rapport porte quatre ou cinq exercices, et
    une année donnée est donc lue par plusieurs. Quand ils divergent, on ne
    tranche pas ; on retire la valeur et on la verse aux conflits, où elle
    reste consultable.
    """
    valeurs: list[dict] = []
    conflits: list[dict] = []
    for regime, libelles in serie.items():
        for (tableau, libelle), annees in libelles.items():
            for annee, lectures in sorted(annees.items()):
                montants = [v for v, _ in lectures]
                # L'échelle est le plus GRAND en valeur absolue. Prendre le
                # plus petit faisait diviser par zéro dès qu'un rapport lisait
                # 0 — « ×709 000 000 000 » pour un écart de 0 à 709 —, ce qui
                # rendait le classement des conflits illisible sans rien
                # changer au verdict.
                echelle = max(max(abs(m) for m in montants), 1e-9)
                etendue = max(montants) - min(montants)
                accord = etendue / echelle <= ECART_TOLERE
                enregistrement = {
                    "regime": regime, "tableau": tableau,
                    "serie": libelle, "annee": annee,
                    "lectures": [{"valeur": v, "rapport": r} for v, r in lectures],
                }
                enregistrement["ecart_relatif"] = etendue / echelle
                if accord:
                    premier = min(lectures, key=lambda x: x[1])
                    valeurs.append({
                        "regime": regime, "tableau": tableau,
                        "serie": libelle, "annee": annee,
                        "valeur": premier[0], "rapport": premier[1],
                        "lectures": len(lectures),
                    })
                else:
                    conflits.append(enregistrement)
    return valeurs, conflits


#: Un cotisant de la SNCF et un cotisant de la CNRACL ne sont pas du même
#: ordre : quand une série d'une caisse porte une valeur vingt fois éloignée
#: de sa propre médiane, ce n'est pas une évolution, c'est un tableau attribué
#: au mauvais régime.
FACTEUR_ABERRANT = 3.0


def _ecarts_de_magnitude(valeurs: list[dict]) -> tuple[list[dict], list[dict]]:
    """Écarte les valeurs qui n'ont pas l'ordre de grandeur de leur propre série.

    C'est le filet sous l'attribution par marqueur de page, qui se trompe
    parfois de fiche. Le test est volontairement grossier — un facteur trois
    autour de la médiane de la caisse pour cette série — parce qu'il ne doit
    attraper QUE le franc mélange : 2 151 694 cotisants portés à la SNCF quand
    sa médiane en dit 130 000. Il ne voit pas, et ne prétend pas voir, une
    confusion entre deux régimes de taille voisine : la CNRACL et le SRE, à
    deux millions chacun, lui passeraient sous le nez.
    """
    par_serie: dict[tuple[str, str], list[float]] = {}
    for v in valeurs:
        par_serie.setdefault((v["regime"], v["serie"]), []).append(abs(v["valeur"]))
    medianes = {}
    for cle, suite in par_serie.items():
        suite = sorted(suite)
        medianes[cle] = suite[len(suite) // 2]
    gardees, aberrantes = [], []
    for v in valeurs:
        pivot = medianes[(v["regime"], v["serie"])]
        val = abs(v["valeur"])
        if pivot > 0 and val > 0 and max(val / pivot, pivot / val) > FACTEUR_ABERRANT:
            aberrantes.append({**v, "mediane_serie": pivot})
        else:
            gardees.append(v)
    return gardees, aberrantes


def _doublons(valeurs: list[dict]) -> tuple[list[dict], list[dict]]:
    """Écarte les cases qu'un même millésime remplit deux fois différemment.

    C'est le détecteur EXACT du tableau attribué au mauvais régime, là où
    ``_ecarts_de_magnitude`` n'est qu'un filet grossier. Une caisse n'a qu'un
    effectif de cotisants pour une année : si deux tableaux en donnent deux,
    l'un des deux n'est pas à elle. On le voit sans rien savoir des ordres de
    grandeur, donc y compris quand les deux régimes se ressemblent — 135 775
    et 112 621 cotisants portés tous deux à la CNIEG en 2023, le second étant
    celui de la SNCF ; 2 144 492 et 2 016 662 portés à la CNRACL en 2024, le
    second étant celui du SRE. Ni l'un ni l'autre n'aurait été vu autrement.

    On n'arbitre pas : les deux partent, parce que rien dans le texte ne dit
    lequel est le bon.

    MAIS SEULEMENT AU SEIN D'UN MÊME TABLEAU. Une fiche porte souvent sa table
    vieillesse et sa table « toutes branches », dont les lignes portent les
    mêmes libellés sans mesurer la même chose. Les confondre revenait à jeter
    318 valeurs justes une fois l'attribution par page réparée.
    """
    par_case: dict[tuple[str, str, int], list[dict]] = {}
    for v in valeurs:
        par_case.setdefault((v["regime"], v["serie"], v["annee"]), []).append(v)
    gardees, doubles = [], []
    for lot in par_case.values():
        # DEUX TABLEAUX DIFFÉRENTS NE SE CONTREDISENT PAS : ils mesurent deux
        # choses. Une fiche porte souvent sa table vieillesse ET sa table
        # « toutes branches », et leurs « prestations légales nettes » n'ont
        # aucune raison d'être égales — 10 577 contre 5 751 millions à la MSA
        # salariés en 2016. Rejeter ces paires écartait 318 valeurs justes,
        # soit la totalité des doublons une fois l'attribution réparée. On ne
        # rejette donc que la contradiction VRAIE : deux valeurs du MÊME
        # tableau pour la même case.
        par_tableau: dict[str, set[float]] = {}
        for v in lot:
            par_tableau.setdefault(v.get("tableau", ""), set()).add(round(v["valeur"], 6))
        if any(len(s) > 1 for s in par_tableau.values()):
            doubles.extend(lot)
            continue
        vus: set[str] = set()
        for v in lot:
            if v.get("tableau", "") not in vus:
                vus.add(v.get("tableau", ""))
                gardees.append(v)
    return gardees, doubles


def main() -> int:
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--depuis", type=int, default=2013)
    arg.add_argument("--jusqu", type=int, default=2100)
    options = arg.parse_args()

    try:
        rapports = rapports_tous()
    except (urllib.error.HTTPError, urllib.error.URLError, LookupError) as erreur:
        print(f"échec : {erreur}", file=sys.stderr)
        return 1

    #: régime -> série -> année -> (valeur, rapport qui l'arrête)
    serie: dict[str, dict[str, dict[int, tuple[float, int]]]] = {}
    titres_vus: dict[str, set[str]] = {}
    illisibles: list[int] = []
    for annee, url in sorted(rapports.items()):
        if not options.depuis <= annee <= options.jusqu:
            continue
        try:
            octets = CCSS._telecharger(annee, url)
            trouves, orphelins = lire_rapport(annee, octets)
        except Exception as erreur:                       # noqa: BLE001
            print(f"  {annee} : illisible ({type(erreur).__name__})", file=sys.stderr)
            illisibles.append(annee)
            continue
        if not trouves:
            illisibles.append(annee)
        n = sum(len(v) for r in trouves.values() for v in r.values())
        print(f"  {annee} : {len(trouves):>2} régimes, {n:>4} valeurs"
              f"{f', {orphelins} tableaux sans régime' if orphelins else ''}")
        for (code, titre, tableau), libelles in trouves.items():
            for libelle, annees in libelles.items():
                cible = serie.setdefault(code, {}).setdefault((tableau, libelle), {})
                titres_vus.setdefault(code, set()).add(titre)
                for a, v in annees.items():
                    cible.setdefault(a, []).append((v, annee))

    valeurs, conflits = _reconcilier(serie)
    valeurs, aberrantes = _ecarts_de_magnitude(valeurs)
    valeurs, doubles = _doublons(valeurs)
    if not valeurs:
        print("échec : aucun tableau lu", file=sys.stderr)
        return 1

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(
            {
                "source": CCSS.PAGE_RAPPORTS,
                "fiabilite": "certifiee",
                "rapports_illisibles": illisibles,
                "conflits": conflits,
                "ecarts_de_magnitude": aberrantes,
                "cases_remplies_deux_fois": doubles,
                "titres_par_caisse": {k: sorted(v) for k, v in sorted(titres_vus.items())},
                "valeurs": valeurs,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    annees = sorted({v["annee"] for v in valeurs})
    print(f"\n{len(valeurs)} valeurs — {len({v['regime'] for v in valeurs})} régimes, "
          f"{annees[0]}-{annees[-1]} → {SORTIE}")
    print(f"{len(conflits)} lectures écartées faute d'accord entre rapports")
    print(f"{len(aberrantes)} écartées pour écart de magnitude dans leur propre série")
    print(f"{len(doubles)} écartées parce que deux tableaux remplissent la même case")
    if illisibles:
        print(f"rapports sans tableau lisible : {illisibles}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
