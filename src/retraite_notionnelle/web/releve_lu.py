"""Lire un relevé de carrière officiel, tel qu'une caisse l'imprime.

Le simulateur accepte une carrière année par année — ``année:régime:revenu``,
parfois ``:trimestres`` —, et jusqu'ici il fallait la recopier à la main depuis
son relevé. Ce module fait le chemin inverse : il prend les LIGNES DE TEXTE
d'un relevé — celles que ``scripts/fetch/lecture_pdf.py`` tire du PDF déposé
sur le site, ou celles qu'on colle depuis l'écran de sa caisse — et en rend la
saisie du formulaire.

Il ne va rien chercher, et ne peut pas : le répertoire de gestion des carrières
uniques n'est pas ouvert, et son accès passe par une authentification
personnelle (``docs/limites.md`` §5). C'est l'assuré qui télécharge son relevé,
et la lecture se fait chez lui — le PDF ne quitte jamais la page.

**Ce que le relevé donne, et ce qu'il ne donne pas.** Il donne l'année, le
régime, le revenu porté au compte et les trimestres retenus. Il ne donne ni le
mois, ni la part de primes, ni le caractère cadre ou non cadre d'un emploi —
c'est la présence de points Agirc, avant leur fusion de 2019, qui le dit. Et
son revenu est PLAFONNÉ : le régime général ne reporte au compte que la part
du salaire brut qui tombe sous le plafond de la Sécurité sociale, si bien
qu'une rémunération plus élevée n'y figure pas en entier. C'est le relevé qui
est ainsi, pas la lecture ; ``docs/limites.md`` le dit, et le site le répète à
qui dépose son relevé.

**Les francs.** Un relevé du régime général porte les revenus dans la monnaie
de leur année : en francs de 1960 à 2001, en anciens francs avant 1960. Le
guide « Mon relevé de carrière, comment le lire ? » de l'Assurance retraite le
dit de la table des revenus minimums qu'il publie en regard, et ces deux
colonnes se lisent l'une contre l'autre. La conversion se fait donc ici, au
taux légal — 6,55957 francs pour un euro, cent anciens francs pour un franc —,
et la lecture dit dans son rapport ce qu'elle a converti.

Le module ne dépend que de la bibliothèque standard, et son portage JavaScript,
``moteur/js/releve-lu.js``, en reprend les fonctions une à une : c'est ce
fichier-ci qui fait foi, et ``tests/test_releve_lu.py`` tient les deux.
"""

from __future__ import annotations

import re
import unicodedata
import math
from dataclasses import dataclass

#: Le taux légal de conversion, fixé le 31 décembre 1998 et jamais révisé.
FRANCS_PAR_EURO = 6.55957
#: Cent anciens francs valent un franc depuis le 1er janvier 1960.
ANCIENS_FRANCS_PAR_FRANC = 100.0
#: La première année en euros sur un relevé.
PREMIERE_ANNEE_EN_EUROS = 2002
#: La première année en nouveaux francs.
PREMIERE_ANNEE_EN_NOUVEAUX_FRANCS = 1960

#: Les bornes de `pages.py`, reprises ici pour ne pas lire comme une année de
#: carrière un nombre à quatre chiffres qui n'en est pas une.
ANNEE_MINIMALE = 1914
ANNEE_MAXIMALE = 2095

#: Au-delà, la ligne n'est pas un trimestre mais un montant : un relevé ne
#: valide jamais plus de quatre trimestres dans une année civile.
TRIMESTRES_PAR_AN = 4

#: Au-delà, la ligne n'est pas une ligne de tableau. Une année de relevé porte
#: son millésime, un revenu, des trimestres, parfois des points : cinq nombres
#: au plus. Quarante nombres sur une ligne, c'est une couche de doublure où
#: toute une page a été collée bout à bout.
NOMBRES_PAR_LIGNE = 6

#: Au-delà, la ligne n'est pas une ligne de tableau non plus : c'est une
#: PHRASE. « Pour valider un trimestre, il faut avoir perçu un certain revenu.
#: En 2026, il faut avoir perçu au moins 1 803,00 € pour valider 1 trimestre »
#: porte une année, un montant en euros et des trimestres, tous correctement
#: étiquetés : rien, dans les nombres, ne la distingue d'une ligne de carrière.
#: Ce qui l'en distingue, c'est qu'elle est écrite en français. Une cellule de
#: tableau ne l'est pas : le nom d'un employeur et celui d'une caisse tiennent
#: en quelques mots.
MOTS_PAR_LIGNE = 12

#: Ce qui annonce la date du document. Un relevé ne rapporte jamais l'avenir :
#: les années postérieures à son édition sont des projections — « En partant au
#: 01/06/2060 … vous pourriez avoir droit à 2 764,30 € » — et non des carrières.
EDITION = ("edite le", "editee le", "situation au", "releve au", "arrete au",
           "mis a jour le")


@dataclass(frozen=True)
class Regime:
    """Un régime tel qu'un relevé le nomme.

    ``genre`` vaut :

    - ``"base"`` pour un régime qui porte une carrière en euros — ses lignes
      deviennent des lignes de relevé ;
    - ``"points"`` pour un régime de base qui compte en POINTS et non en
      euros : les professions libérales depuis 2004, les exploitants
      agricoles. Ses années et ses trimestres se lisent, son revenu non — un
      nombre de points n'est pas un revenu, et le déduire du barème de la
      caisse serait inventer un chiffre que le relevé ne porte pas ;
    - ``"indice"`` pour un régime complémentaire, qui ne porte aucune carrière
      mais RENSEIGNE le statut : des points Agirc dans une année disent que
      l'emploi de cette année-là était un emploi de cadre, ce qu'aucune colonne
      du régime général ne dit. Lu comme une carrière, il ferait doublon avec
      la base et doublerait les trimestres.
    """

    code: str
    genre: str
    statut: str
    #: Ce que la caisse imprime : son nom, son sigle, ses variantes.
    alias: tuple[str, ...]


#: Les régimes qu'un relevé nomme, et le statut du simulateur qui leur
#: correspond. L'ordre ne compte pas : c'est l'alias le plus long qui gagne,
#: sans quoi « agirc » trancherait avant « agirc-arrco ».
REGIMES = (
    Regime("regime_general", "base", "salarie_prive_non_cadre", (
        "regime general", "cnav", "carsat", "assurance retraite",
        "caisse nationale d assurance vieillesse", "cramif", "cgss",
        "securite sociale des independants", "ssi", "rsi", "organic", "cancava",
    )),
    Regime("msa_salaries", "base", "salarie_agricole", (
        "msa salaries", "salaries agricoles", "mutualite sociale agricole salaries",
    )),
    Regime("msa_exploitants", "points", "exploitant_agricole", (
        "msa non salaries", "non salaries agricoles", "exploitants agricoles",
        "amexa", "ava agricole",
    )),
    Regime("pension_civile_etat", "base", "fonctionnaire_etat", (
        "service des retraites de l etat", "sre", "pensions civiles et militaires",
        "pension civile", "fonction publique d etat", "retraites de l etat",
    )),
    Regime("cnracl", "base", "fonctionnaire_territorial_hospitalier", (
        "cnracl", "agents des collectivites locales",
    )),
    Regime("fspoeie", "base", "ouvrier_etat", ("fspoeie", "ouvriers de l etat")),
    Regime("cnieg", "base", "agent_ieg", (
        "cnieg", "industries electriques et gazieres",
    )),
    Regime("sncf", "base", "agent_sncf", ("cprp sncf", "cprpsncf", "sncf")),
    Regime("ratp", "base", "agent_ratp", ("crp ratp", "crpratp", "ratp")),
    Regime("enim", "base", "marin", ("enim", "marins", "gens de mer")),
    Regime("crpcen", "base", "clerc_de_notaire", (
        "crpcen", "clercs et employes de notaires",
    )),
    Regime("cavimac", "base", "ministre_du_culte", ("cavimac", "cultes")),
    Regime("mines", "base", "mineur", ("canssm", "regime des mines", "mines")),
    Regime("banque_de_france", "base", "agent_banque_de_france", ("banque de france",)),
    Regime("crpnpac", "base", "personnel_navigant", (
        "crpnpac", "personnel navigant", "navigants de l aeronautique",
    )),
    Regime("opera", "base", "personnel_opera", ("opera national de paris", "cropera")),
    Regime("comedie_francaise", "base", "personnel_comedie_francaise",
           ("comedie francaise",)),
    Regime("cnbf", "points", "avocat", ("cnbf", "barreaux francais", "avocats")),
    Regime("carmf", "points", "medecin_liberal", ("carmf", "medecins de france")),
    Regime("carcdsf", "points", "chirurgien_dentiste_ou_sage_femme", (
        "carcdsf", "chirurgiens dentistes", "sages femmes",
    )),
    Regime("carpimko", "points", "auxiliaire_medical", ("carpimko", "auxiliaires medicaux")),
    Regime("cavp", "points", "pharmacien", ("cavp", "pharmaciens")),
    Regime("cavec", "points", "expert_comptable", ("cavec", "experts comptables")),
    Regime("cavamac", "points", "agent_general_assurance", (
        "cavamac", "agents generaux d assurances",
    )),
    Regime("cprn", "points", "notaire", ("cprn", "crn", "notaires")),
    Regime("cavom", "points", "officier_ministeriel", ("cavom", "officiers ministeriels")),
    Regime("cnavpl", "points", "profession_liberale", (
        "cipav", "cnavpl", "professions liberales",
    )),
    Regime("ircantec", "indice", "contractuel_public", ("ircantec",)),
    Regime("agirc", "indice", "salarie_prive_cadre", ("agirc",)),
    Regime("arrco", "indice", "salarie_prive_non_cadre", (
        "agirc arrco", "arrco", "retraite complementaire",
    )),
    Regime("rafp", "indice", "fonctionnaire_etat", (
        "rafp", "retraite additionnelle de la fonction publique",
    )),
)

#: Les motifs d'une année sans revenu, tels que le relevé les nomme. Le premier
#: qui se trouve dans la ligne l'emporte, l'ordre va donc du plus précis au plus
#: général : « chomage non indemnise » avant « chomage ».
MOTIFS = (
    ("chomage non indemnise", "chomage_non_indemnise"),
    ("non indemnise", "chomage_non_indemnise"),
    ("chomage", "chomage_indemnise"),
    ("pole emploi", "chomage_indemnise"),
    ("france travail", "chomage_indemnise"),
    ("accident du travail", "accident_travail"),
    ("accident de travail", "accident_travail"),
    ("maternite", "maternite"),
    ("adoption", "maternite"),
    ("invalidite", "invalidite"),
    ("maladie", "maladie"),
    ("service national", "service_militaire"),
    ("service militaire", "service_militaire"),
    ("avpf", "education_enfant"),
    ("parent au foyer", "education_enfant"),
    ("education enfant", "education_enfant"),
    ("congé parental", "education_enfant"),
    ("conge parental", "education_enfant"),
    ("sans activite", "sans_activite"),
    ("inactivite", "sans_activite"),
)

#: Ce à quoi se reconnaît un relevé, et sans quoi l'on ne lit rien.
#:
#: Un document quelconque porte des années et des nombres : le rapport de
#: l'OPEF sur les frais de l'épargne retraite, cent pages sans le moindre
#: relevé, y nommait au passage la Banque de France et rendait vingt-deux
#: « années de carrière » que personne n'avait vécues. Remplir un formulaire
#: avec cela serait pire que ne rien remplir — le lecteur corrigerait des
#: chiffres au lieu de comprendre qu'il s'est trompé de fichier.
#:
#: Ce qu'on cherche est donc le TITRE du document, ou l'en-tête de la colonne
#: qui compte les trimestres. Le mot « trimestre » seul ne suffit pas : ce même
#: rapport de l'OPEF écrit « trimestre par trimestre » au détour d'une phrase
#: sur le calcul d'une performance, et cela rouvrait la porte en entier.
MARQUEURS = ("trimestres retenus", "trimestres cotises", "trimestres valides",
             "trimestres assimiles", "nombre de trimestres", "total des trimestres",
             "trimestres acquis", "releve de carriere",
             "releve de situation individuelle", "releve individuel de situation",
             "duree d assurance")

#: Ce qui désigne un emploi, et interdit donc de lire la ligne comme une
#: interruption même quand elle ne porte aucun revenu — une année d'emploi à
#: revenu inconnu reste une année d'emploi.
EMPLOIS = ("salarie", "emploi", "activite", "apprentissage", "employeur",
           "travailleur", "stage", "titulaire", "services")


def arrondi(montant: float) -> int:
    """L'euro le plus proche, la moitié vers le haut.

    Ni ``round``, qui arrondit à l'entier PAIR — 2,5 y fait 2 —, ni la règle de
    JavaScript, qui l'arrondit vers le haut : les deux se séparent une fois sur
    deux cents sur des revenus convertis de francs, et le portage rendrait
    alors une saisie différente de celle-ci. La règle est donc écrite, et la
    même des deux côtés.
    """
    return math.floor(montant + 0.5)


def sans_accent(texte: str) -> str:
    """Le texte en minuscules, sans accent et sans ponctuation séparatrice.

    C'est la forme sur laquelle les alias se cherchent : « Agirc-Arrco »,
    « AGIRC ARRCO » et « agirc/arrco » sont le même nom, et une caisse ne
    l'écrit pas deux fois de la même façon d'un document à l'autre.
    """
    decompose = unicodedata.normalize("NFD", texte.lower())
    plat = "".join(c for c in decompose if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", plat)).strip()


#: Un montant : des chiffres, des groupes de milliers de TROIS chiffres
#: exactement — séparés par une espace ordinaire, une insécable ou une fine —,
#: puis des centimes derrière une virgule ou un point. La règle des trois
#: chiffres est ce qui sépare « 1998 14 200 4 » en une année, un montant et des
#: trimestres : « 14 200 » se recolle, « 4 » reste seul.
MONTANT = re.compile(
    r"(?<![\d,.])(\d{1,3}(?:[     ]\d{3})+|\d+)"
    r"(?:[.,](\d{1,2}))?(?![\d])"
)

#: Une date écrite en clair. Un relevé de fonction publique décrit ses services
#: par leurs bornes — « du 01/09/1996 au 31/08/2001 » — et ces jours et ces mois
#: sont des nombres qu'on lirait pour des trimestres : ils sont donc retirés de
#: la ligne avant tout comptage, et leur année retenue à part.
DATE = re.compile(r"(?<!\d)(\d{1,2})[/.-](\d{1,2})[/.-]((?:1[89]|20)\d{2})(?!\d)")

#: Ce qui annonce la date de naissance sur un relevé. Elle y figure en tête,
#: sous le nom de l'assuré : c'est la seule donnée du formulaire, hors la
#: carrière elle-même, que le document porte — et celle dont tout le reste
#: dépend, l'âge légal comme la durée requise.
NAISSANCE = ("date de naissance", "ne le", "nee le", "ne e le")


@dataclass(frozen=True)
class LigneLue:
    """Une année, telle que le relevé la porte, avant toute agrégation."""

    annee: int
    statut: str
    #: En euros de l'année, francs déjà convertis.
    revenu: float
    #: `None` quand le relevé ne les porte pas : le modèle les déduira.
    trimestres: int | None
    motif: str | None
    #: La ligne d'origine, pour que le lecteur retrouve ce qui a été lu.
    source: str


@dataclass(frozen=True)
class Lecture:
    """Ce qu'un relevé a donné, et ce qu'il n'a pas donné."""

    lignes: tuple[LigneLue, ...]
    interruptions: tuple[tuple[int, int, str], ...]
    #: Les lignes qui portaient une année sans qu'on sache quoi en faire.
    ignorees: tuple[str, ...]
    #: Les régimes reconnus, dans l'ordre où ils sont apparus.
    regimes: tuple[str, ...]
    #: Ce que la lecture a supposé, en toutes lettres.
    notes: tuple[str, ...]
    #: La date de naissance lue en tête du relevé, « AAAA-MM-JJ », ou `None`.
    naissance: str | None = None

    @property
    def vide(self) -> bool:
        return not self.lignes

    def parametres(self) -> dict[str, str]:
        """La saisie du formulaire : le relevé, et les interruptions."""
        releve = "\n".join(
            f"{ligne.annee}:{ligne.statut}:{arrondi(ligne.revenu)}"
            + ("" if ligne.trimestres is None else f":{ligne.trimestres}")
            for ligne in self.lignes
        )
        interruptions = ",".join(
            f"{debut}:{fin}:{motif}" for debut, fin, motif in self.interruptions
        )
        return {"releve": releve, "interruptions": interruptions}


def _regime_de(plat: str) -> Regime | None:
    """Le régime que nomme une ligne déjà mise à plat, le plus long d'abord."""
    trouve = None
    longueur = 0
    for regime in REGIMES:
        for alias in regime.alias:
            if len(alias) > longueur and re.search(rf"(?<![a-z0-9]){re.escape(alias)}"
                                                   rf"(?![a-z0-9])", plat):
                trouve, longueur = regime, len(alias)
    return trouve


def _motif_de(plat: str) -> str | None:
    for texte, motif in MOTIFS:
        if sans_accent(texte) in plat:
            return motif
    return None


#: Ce qu'une caisse écrit derrière un nombre, et qui dit ce que le nombre est.
#: C'est l'information la plus sûre d'un relevé, et la seule qui ne dépende pas
#: de la mise en page : « 49 150 € » est un revenu où qu'il se trouve dans la
#: ligne, « 4 trim. » une durée, « 203,91 pts » des points. Un tableau qui ne
#: les écrit pas se lit à la position, comme avant.
EUROS = ("eur", "euro", "euros")
POINTS = ("pt", "pts", "point", "points")


def _unite(suite: str) -> str | None:
    """Ce que l'unité écrite derrière un nombre dit de ce nombre.

    Le signe € se cherche sur le texte BRUT : il ne survit pas à la mise à
    plat, qui ne garde que des lettres et des chiffres. Le reste se lit sur le
    premier mot qui suit, « trim. » comme « trimestres ».
    """
    if suite.lstrip().startswith("\u20ac"):
        return "revenu"
    plat = sans_accent(suite)
    premier = plat.split(" ")[0] if plat else ""
    if premier in EUROS:
        return "revenu"
    if premier.startswith("trim"):
        return "trimestre"
    if premier in POINTS:
        return "point"
    return None


#: Ce qu'on regarde derrière un nombre pour y chercher son unité : de quoi
#: couvrir « trimestres » sans mordre sur la colonne suivante.
SUITE_LUE = 12


def _nombres(reste: str) -> list[tuple[float, str | None]]:
    """Les nombres d'une ligne, avec leur unité quand elle est écrite.

    La virgule décimale et les milliers sont recollés ; l'unité est cherchée
    dans les quelques caractères qui suivent le nombre.
    """
    valeurs = []
    for trouve in MONTANT.finditer(reste):
        entier, centimes = trouve.group(1), trouve.group(2)
        nombre = float(re.sub(r"[     ]", "", entier))
        if centimes:
            nombre += float(centimes) / (10 ** len(centimes))
        suite = reste[trouve.end():trouve.end() + SUITE_LUE]
        valeurs.append((nombre, _unite(suite)))
    return valeurs


def _en_euros(montant: float, annee: int) -> float:
    """Le montant d'une année, ramené en euros de cette année-là."""
    if annee >= PREMIERE_ANNEE_EN_EUROS:
        return montant
    if annee >= PREMIERE_ANNEE_EN_NOUVEAUX_FRANCS:
        return montant / FRANCS_PAR_EURO
    return montant / (FRANCS_PAR_EURO * ANCIENS_FRANCS_PAR_FRANC)


@dataclass
class _Annee:
    """Une année en cours d'agrégation : un relevé la coupe par employeur."""

    revenu: float = 0.0
    trimestres: int | None = None
    statut: str = ""
    revenu_du_statut: float = -1.0
    motif: str | None = None
    source: str = ""


def _annee_et_nombres(
    ligne: str,
) -> tuple[int | None, list[tuple[float, str | None]], bool, bool, int]:
    """L'année de la ligne, les nombres qui restent, et si elle couvre une plage.

    Les dates en clair sont retirées d'abord : leurs jours et leurs mois sont
    des nombres de un à trente et un, qu'on lirait pour des trimestres. Quand
    une ligne en porte deux d'années différentes, elle décrit une PÉRIODE de
    plusieurs années — un état de services de la fonction publique — que la
    maille annuelle du modèle ne sait pas répartir : on ne la lit pas, on la
    montre.
    """
    dates = DATE.findall(ligne)
    reste = DATE.sub(" ", ligne)
    nombres = _nombres(reste)
    annees_des_dates = [int(annee) for _, _, annee in dates]
    plage = len(set(annees_des_dates)) > 1
    annee = None
    for rang, (nombre, unite) in enumerate(nombres):
        # Le millésime ouvre la ligne, ou ne porte pas d'unité. La réserve est
        # pour le tableau qui écrit « 2011 Points Agirc 415,20 » : lue comme
        # une unité, la colonne suivante ferait de l'année un nombre de points,
        # et la ligne n'aurait plus de millésime du tout.
        if (float(nombre).is_integer() and ANNEE_MINIMALE <= nombre <= ANNEE_MAXIMALE
                and (unite is None or rang == 0)):
            annee = int(nombre)
            nombres = nombres[:rang] + nombres[rang + 1:]
            break
    # L'année peut n'être portée que par une DATE — « 01/01/2025 31/12/2025
    # 49 150 € » est une ligne de carrière dont le millésime ne s'écrit nulle
    # part ailleurs. L'appelant a besoin de le savoir : un pied de page
    # (« 7 / 7 Edité le 22/09/2026 ») porte lui aussi une date, et rien d'autre
    # qui ressemble à une carrière.
    par_la_date = annee is None and bool(annees_des_dates)
    if par_la_date:
        annee = annees_des_dates[0]
    return annee, nombres, plage, par_la_date, len(annees_des_dates)


def _naissance_de(ligne: str, plat: str) -> str | None:
    """La date de naissance qu'une ligne d'en-tête annonce, au format ISO."""
    if not any(marqueur in plat for marqueur in NAISSANCE):
        return None
    date = DATE.search(ligne)
    if date is None:
        return None
    jour, mois, annee = date.groups()
    return f"{int(annee):04d}-{int(mois):02d}-{int(jour):02d}"


#: Ce qu'on lit devant une date pour savoir si elle est celle du document.
AVANT_LA_DATE = 24


def _annee_du_document(lignes: list[str]) -> int | None:
    """L'année d'édition du document, quand il la porte en toutes lettres.

    C'est la date qui SUIT le marqueur, et non la plus tardive de la ligne :
    une couche de doublure colle toute une page sur une seule ligne, et l'on y
    trouve « Edité le 22/09/2026 » à côté de « En partant au 01/06/2066 ». Lire
    le maximum de la ligne donnait 2066, et le plafond ne plafonnait plus rien.
    """
    derniere = None
    for ligne in lignes:
        for trouve in DATE.finditer(ligne):
            avant = sans_accent(ligne[max(0, trouve.start() - AVANT_LA_DATE):
                                      trouve.start()])
            if not any(avant.endswith(marqueur) for marqueur in EDITION):
                continue
            annee = int(trouve.group(3))
            if derniere is None or annee > derniere:
                derniere = annee
    return derniere


def lire_releve(lignes: list[str], annee_maximale: int | None = None) -> Lecture:
    """Lit un relevé, ligne à ligne, et rend la carrière qu'il décrit.

    Quatre règles, et elles suffisent à lire les relevés des deux formes —
    celui du régime général, une seule caisse et un seul tableau, et le relevé
    de situation individuelle, qui empile un tableau par régime :

    1. **Une ligne qui NOMME un régime le rend courant** pour celles qui
       suivent, jusqu'au prochain. C'est ainsi que le relevé tous régimes est
       bâti, et le nom peut aussi bien tenir dans la ligne de l'année.
    2. **Une ligne de carrière porte son année**, en général la première. Ce
       qui suit est fait de nombres — le revenu, les trimestres — et de mots —
       l'employeur, la nature de la période. Un nombre supérieur à quatre est
       un revenu ; un nombre de quatre au plus est un compte de trimestres.
    3. **Une année revient autant de fois que le relevé la coupe** : un
       employeur par ligne, parfois une période par ligne. Les revenus
       s'additionnent, les trimestres aussi, plafonnés à quatre — c'est la
       règle du droit, et c'est ce que le total du relevé affiche.
    4. **Ce qui n'est pas compris n'est pas deviné.** Une ligne qui porte une
       année sans qu'on sache lire ce qui l'accompagne ressort telle quelle
       dans ``ignorees``, et le site la montre : c'est au lecteur de trancher,
       pas au programme de choisir à sa place un chiffre vraisemblable.
    """
    courant: Regime | None = None
    section: Regime | None = None
    annees: dict[int, _Annee] = {}
    ignorees: list[str] = []
    regimes: list[str] = []
    cadres: set[int] = set()
    francs = False
    points = False
    naissance: str | None = None

    # Le plafond des années lues : celui que l'appelant donne — le site passe
    # l'année courante —, resserré par la date d'édition du document quand il
    # la porte. Ce qui est postérieur est une projection, pas une carrière.
    edition = _annee_du_document(lignes)
    if edition is not None:
        annee_maximale = edition if annee_maximale is None else min(annee_maximale,
                                                                    edition)

    plat_entier = sans_accent(" ".join(lignes))
    if not any(marqueur in plat_entier for marqueur in MARQUEURS):
        return Lecture((), (), (), (), (
            "Ce document ne ressemble pas à un relevé de carrière : ni son "
            "titre, ni la colonne des trimestres qu'une caisse imprime toujours "
            "ne s'y trouvent. Rien n'en a été lu, plutôt que d'en tirer des "
            "années qui n'existent pas.",
        ), None)

    for brute in lignes:
        ligne = brute.strip()
        if not ligne:
            continue
        plat = sans_accent(ligne)
        entete = _naissance_de(ligne, plat)
        if entete is not None:
            # La ligne qui porte la date de naissance n'est pas une ligne de
            # carrière : lue comme telle sous un titre de régime, elle
            # ouvrirait une année de travail à l'âge de zéro an.
            if naissance is None:
                naissance = entete
            continue
        regime = _regime_de(plat)
        if regime is not None:
            # DEUX RÉGIMES COURANTS, ET C'EST LE RELEVÉ QUI L'IMPOSE. La
            # SECTION est le dernier régime nommé, quel qu'il soit : un relevé
            # tous régimes empile ses tableaux sous un titre, et les lignes qui
            # suivent « Ircantec » sont des lignes d'Ircantec même si elles ne
            # le répètent pas. La BASE est le dernier régime qui porte une
            # carrière : c'est de lui que vient le statut de l'année, jamais de
            # la caisse qui ne tient que des points.
            section = regime
            if regime.genre != "indice":
                courant = regime
            if regime.code not in regimes:
                regimes.append(regime.code)

        annee, nombres, plage, par_la_date, dates = _annee_et_nombres(ligne)
        if annee is None:
            continue
        if plage:
            ignorees.append(ligne)
            continue
        # UNE LIGNE DE TABLEAU PORTE QUELQUES COLONNES, PAS QUARANTE. Un PDF
        # peut porter deux fois le même texte — une couche visible, mise en
        # page, et une couche de doublure où tout est collé bout à bout. C'est
        # le cas de l'estimation retraite d'Info Retraite, dont la doublure
        # rendait des lignes de deux cents caractères où les dates et les
        # montants de toute une page se suivaient sans séparateur. Additionnés
        # à l'année qu'ils touchaient, ils y faisaient des revenus de deux
        # millions d'euros.
        if len(nombres) > NOMBRES_PAR_LIGNE:
            ignorees.append(ligne)
            continue
        if annee_maximale is not None and annee > annee_maximale:
            continue
        # UNE PÉRIODE A DEUX BORNES. Quand le millésime ne vient que d'une
        # date, une seule date ne suffit pas : « Valeur du point au 01/11/2025
        # : 1,4386 € » et « 3 / 7 Edité le 22/09/2026 » en portent une, et
        # toutes deux se lisaient comme une année de carrière — l'une y
        # ajoutait un euro et quarante, l'autre sept euros et trois trimestres.
        if par_la_date and dates < 2:
            continue
        if len([mot for mot in plat.split(" ") if len(mot) > 1
                and not mot.isdigit()]) > MOTS_PAR_LIGNE:
            continue

        motif = _motif_de(plat)
        emploi = any(mot in plat for mot in EMPLOIS)

        # Un régime complémentaire ne porte pas de carrière : ses points
        # feraient un revenu qui n'en est pas un, et ses années doubleraient
        # celles de la base. Mais sa ligne n'est pas perdue pour autant : elle
        # porte la durée tous régimes de l'année — « 2025 4 trim. 203,91 pts
        # Agirc-Arrco » —, et parfois un revenu en euros que la base n'a pas
        # reporté. On lui prend donc ce qui est ÉTIQUETÉ, et rien d'autre.
        # Le régime qui gouverne la ligne : celui qu'elle nomme, sinon celui
        # de la section où elle se trouve.
        gouverne = regime if regime is not None else section
        indice_seul = gouverne is not None and gouverne.genre == "indice"
        if indice_seul and gouverne.code == "agirc":
            cadres.add(annee)
        if courant is None:
            if nombres:
                ignorees.append(ligne)
            continue

        etiquetes = [unite for _, unite in nombres if unite]
        revenu = 0.0
        trimestres = None
        if etiquetes:
            for valeur, unite in nombres:
                if unite == "revenu":
                    revenu = max(revenu, valeur)
                elif unite == "trimestre" and valeur <= TRIMESTRES_PAR_AN:
                    # Le dernier l'emporte, et jamais un cumul de carrière :
                    # « 172 trimestres » est un total, pas une année.
                    trimestres = int(valeur)
                # Les points sont lus, et jetés : ce n'est pas un revenu.
        elif indice_seul:
            # Une ligne qui ne nomme qu'un régime complémentaire et n'écrit
            # aucune unité ne dit rien qu'on sache lire : ses nombres sont des
            # points bien plus souvent que des euros.
            continue
        else:
            for valeur, _ in nombres:
                if valeur > TRIMESTRES_PAR_AN or not float(valeur).is_integer():
                    revenu = max(revenu, valeur)
                else:
                    # LE DERNIER l'emporte, et non le premier : les trimestres
                    # sont la colonne de droite d'un relevé, et une année
                    # assimilée y porte « 0 4 » — zéro euro, quatre trimestres.
                    trimestres = int(valeur)
        if courant.genre == "points":
            # Le nombre lu est un nombre de POINTS, pas un revenu. L'année et
            # ses trimestres se gardent ; le revenu reste à compléter.
            if revenu:
                points = True
            revenu = 0.0
        if par_la_date and not etiquetes:
            # L'année ne vient que d'une date, et aucun nombre ne porte son
            # unité : la ligne ne dit pas de carrière. Si elle nomme tout de
            # même un régime, elle ressort — c'est une ligne dont une cellule
            # manque, et le lecteur doit la voir.
            if regime is not None and not indice_seul:
                ignorees.append(ligne)
            continue
        if revenu == 0.0 and trimestres is None and not motif and not emploi:
            ignorees.append(ligne)
            continue

        montant = _en_euros(revenu, annee)
        cumul = annees.setdefault(annee, _Annee())
        cumul.revenu += montant
        if trimestres is not None:
            cumul.trimestres = min(TRIMESTRES_PAR_AN,
                                   (cumul.trimestres or 0) + trimestres)
        # Le statut de l'année est celui du régime qui y a porté le plus :
        # l'année d'un changement de métier relève d'un seul régime, et c'est
        # la convention que le modèle applique partout ailleurs.
        if montant >= cumul.revenu_du_statut or not cumul.statut:
            cumul.statut = courant.statut
            cumul.revenu_du_statut = montant
        if motif and not cumul.motif:
            cumul.motif = motif
        if not cumul.source:
            cumul.source = ligne
        if annee < PREMIERE_ANNEE_EN_EUROS and revenu:
            francs = True

    lues: list[LigneLue] = []
    interruptions: list[tuple[int, int, str]] = []
    for annee in sorted(annees):
        cumul = annees[annee]
        statut = cumul.statut
        if annee in cadres and statut == "salarie_prive_non_cadre":
            statut = "salarie_prive_cadre"
        # Une année sans revenu n'est pas une année travaillée : le relevé y
        # porte une période assimilée, que le formulaire décrit par son motif
        # et non par une ligne de carrière à zéro euro.
        if cumul.revenu <= 0 and cumul.motif:
            interruptions.append((annee, annee, cumul.motif))
        lues.append(LigneLue(annee, statut, cumul.revenu, cumul.trimestres,
                             cumul.motif, cumul.source))

    notes = []
    if francs:
        notes.append(
            "Les revenus antérieurs à 2002 ont été convertis en euros : "
            "divisés par 6,55957 pour les francs, par 655,957 pour les années "
            "antérieures à 1960, qu'un relevé porte en anciens francs."
        )
    if cadres:
        notes.append(
            "Des points Agirc figurent au relevé : les années qu'ils couvrent "
            "sont lues comme des années de cadre."
        )
    if points:
        notes.append(
            "Un régime qui compte en points — professions libérales, "
            "exploitants agricoles — ne porte pas de revenu au relevé : ses "
            "années sont lues sans montant, à compléter à la main."
        )
    if any(regime in ("regime_general", "msa_salaries") for regime in regimes):
        notes.append(
            "Le revenu porté au relevé est plafonné : au-delà du plafond de la "
            "Sécurité sociale, le salaire n'y figure pas en entier, et la "
            "simulation lit ce que le relevé porte."
        )
    return Lecture(tuple(lues), tuple(_fusionner(interruptions)),
                   tuple(ignorees), tuple(regimes), tuple(notes), naissance)



def _fusionner(interruptions: list[tuple[int, int, str]]
               ) -> list[tuple[int, int, str]]:
    """Recolle les années voisines de même motif en une seule plage.

    Le champ « Interruptions » du formulaire s'écrit par plages, et huit années
    de chômage consécutives y tiennent en une ligne plutôt qu'en huit.
    """
    fusionnees: list[tuple[int, int, str]] = []
    for debut, fin, motif in sorted(interruptions):
        if fusionnees and fusionnees[-1][2] == motif and fusionnees[-1][1] == debut - 1:
            fusionnees[-1] = (fusionnees[-1][0], fin, motif)
        else:
            fusionnees.append((debut, fin, motif))
    return fusionnees
