"""Liquider chaque régime (docs/architecture.md, § 7.3).

Chaque régime liquide sa pension sous ses propres règles, sur ce que le
relevé lui a acquis :

* EN ANNUITÉS : un salaire de référence (:func:`salaire_de_reference`) ou un
  forfait, un taux — le taux plein, décote et surcote faites
  (:func:`decote_opposable`, :func:`trimestres_de_decote`,
  :func:`coefficient_surcote_datee`) —, et une durée proratisée
  (:func:`duree_proratisation`), plafonnée au taux maximum ;
* EN POINTS : les points à la valeur de service de la liquidation
  (:func:`valeur_du_point`), le rendement pour les années sans prix d'achat,
  le forfait d'un régime mixte ; l'abattement avant le taux plein et la
  majoration après (:func:`abattement_points`, :func:`surcote_points`) ; le
  capital du RAFP sous son seuil.

Un régime que la coordination réunit à celui qui lui succède est liquidé par
lui, sur leurs années réunies. L'étape dit aussi ce que l'étape suivante lit
pour compléter : pour chaque régime qui porte le minimum contributif ou le
minimum garanti, les durées et la condition qui les ouvrent.

Ce qu'elle écrit, :class:`Pensions`, suit son schéma,
``data/reference/etapes/liquider_chaque_regime.yaml``. Les tables sont celles
que le moteur du scénario 1 tient, jusqu'aux fiches (phase 6). Son jumeau est
``moteur/js/droit/liquider.js``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from ..carriere import salaire_moyen_annuel
from ..donnees.chargement import Fiabilite
from .. import revalorisation
from . import acquerir, coordonner, cultes, invalidite, ouvrir
from .compter import trimestres_de_la_ligne_entre
from .commun import PensionRegime, date_d_effet, derniere_annee
from .etranger import famille_du_regime
from .ouvrir import TRIMESTRES_DECOTE_MILITAIRE
from ..somme import somme_ordonnee

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..donnees.regimes import PeriodeRegime
    from ..scenarios.actuel import ScenarioActuel
    from .liquidation import Contexte
    from .ouvrir import Ouverture
    from .releve import Releve

#: La version du schéma de l'étape que :meth:`Pensions.donnees` suit.
SCHEMA_VERSION = 1

#: Trimestres dont l'âge d'annulation de la décote est minoré, pour ouvrir le
#: minimum garanti à qui n'a pas la durée, selon l'année où l'âge d'ouverture
#: du droit est atteint : tableau de l'article 3 du décret n° 2010-1744 du
#: 30 décembre 2010, pris pour le IV de l'article 45 de la loi n° 2010-1330.
#: Aucun à partir de 2016.
MINORATION_AGE_MINIMUM_GARANTI = {2011: 9, 2012: 7, 2013: 5, 2014: 3, 2015: 1}

#: Coefficients d'anticipation de l'Agirc-Arrco, sous leur forme de barème.
#: Le régime n'applique pas la décote du régime de base : il a ses propres
#: coefficients, publiés en deux tables — l'une indexée sur les trimestres
#: manquants, l'autre sur l'âge — dont il retient la plus favorable.
#:
#: Les deux tables descendent par paliers réguliers, et c'est cette régularité
#: qu'on écrit ici plutôt que quarante lignes de barème : un point de
#: pourcentage par trimestre jusqu'à douze, un point et quart jusqu'à vingt,
#: un point trois quarts au-delà — ce dernier palier n'existant que dans la
#: table des âges, qui descend jusqu'à 0,43 pour dix ans d'anticipation.
_PALIERS_ANTICIPATION: tuple[tuple[int, float], ...] = (
    (12, 0.01), (20, 0.0125), (40, 0.0175),
)

#: Les barèmes de minoration qui comptent des ANNÉES manquantes et non des
#: trimestres : les deux de l'IRCEC (RAAP, RACD, RACL) et celui de la CAVOM,
#: qui est le second sous un autre nom. Voir ``abattement_ircec``.
_ABATTEMENTS_IRCEC = ("ircec", "ircec_age_seul", "cavom")

#: Ceux des précédents que seul l'âge annule : la durée d'assurance n'y ouvre
#: pas le taux plein.
_ABATTEMENTS_PAR_ANNEE_AGE_SEUL = ("ircec_age_seul", "cavom")

#: Dernière ligne de la table des âges : dix ans d'anticipation. Au-delà, le
#: barème ne descend plus.
_COEFFICIENT_ANTICIPATION_PLANCHER = 0.43

#: Majoration par trimestre ENTIER écoulé entre l'âge du taux plein et la
#: liquidation — le 1° du IV de l'article 16 de l'arrêté du 30 décembre 1970,
#: « 0,75 % par trimestre entier écoulé entre le soixante-cinquième
#: anniversaire de l'assuré et la date d'entrée en jouissance de la pension ».
#: Aucune condition de durée ne s'y attache : c'est le temps qui compte.
_SURCOTE_IRCANTEC_AGE = 0.0075

#: Majoration par trimestre COTISÉ au-delà de la durée requise, entre l'âge
#: légal et l'âge du taux plein — le 2° du même IV, « 0,625 % par trimestre
#: accompli ». Son assiette est celle de la surcote du régime général, bornée
#: en haut par l'âge où le 1° prend le relais : « en aucun cas une même période
#: ne peut donner lieu à la fois à l'attribution de la majoration prévue au 1°
#: et à celle prévue au 2° ».
_SURCOTE_IRCANTEC_DUREE = 0.00625

#: LA RÉFORME AGRICOLE DE 2026 COUPE LA CARRIÈRE AU 1ER JANVIER 2016 : les
#: années d'avant comptent par leurs points, celles d'après par leur revenu
#: (L. 732-24, I) — « les revenus n'étant pas disponibles avant l'année
#: 2016 », écrit la MSA.
ANNEE_DES_REVENUS_AGRICOLES = 2016


def _sans_zeros_inutiles(valeur: float, decimales: int) -> str:
    """Un nombre à ``decimales`` chiffres au plus, sans les zéros de fin.

    Certaines valeurs de service sont des barèmes PUBLIÉS à quatre décimales —
    1,8026 € à l'Agirc-Arrco —, d'autres sont CALCULÉES et en portent bien
    davantage. Les tronquer toutes à quatre inventait un écart de vingt-huit
    centimes entre la formule affichée et le montant de la ligne ; les afficher
    toutes à six aurait inventé, à l'inverse, une précision que le barème n'a
    pas. Chacune est donc écrite à la précision qu'elle porte.
    """
    return f"{valeur:.{decimales}f}".rstrip("0").rstrip(".")


def _formule_points(termes: list[str], coefficient: float) -> str:
    """La formule d'un régime en points, telle qu'on doit pouvoir la refaire.

    Le coefficient multiplie la SOMME des termes, il ne s'y ajoute pas : il
    vient donc après, et la somme prend ses parenthèses dès qu'elle en compte
    plusieurs. Sans lui, la formule affichée ne retrouvait pas le montant de la
    ligne — à dix ans d'anticipation elle en donnait 2,3 fois trop, sans que
    rien à l'écran ne dise pourquoi.

    Il se nomme par ce qu'il fait : « coefficient d'anticipation » quand il
    retire, « coefficient de majoration » quand il ajoute. Un seul régime
    ajoute — l'Ircantec, dont le IV de l'article 16 de l'arrêté du 30 décembre
    1970 majore les points d'une liquidation tardive —, et l'appeler
    « anticipation » aurait écrit le contraire de ce qu'il vaut.
    """
    formule = " + ".join(termes) or "aucun droit"
    if coefficient == 1.0 or not termes:
        return formule
    if len(termes) > 1:
        formule = f"({formule})"
    nom = "de majoration" if coefficient > 1.0 else "d'anticipation"
    return f"{formule} × coefficient {nom} {coefficient:.4f}"


def _au_trimestre_superieur(trimestres: float) -> int:
    """Nombre de trimestres arrondi à l'entier supérieur, jamais négatif.

    C'est la règle de l'article R. 351-27 pour la décote, et celle que la
    caisse illustre dans son exemple pour les coefficients d'anticipation : un
    assuré à qui il manque trois ans et dix mois se voit opposer seize
    trimestres, pas quinze. La tolérance de 10⁻³ évite qu'un flottant tout juste
    au-dessus d'un entier n'en fasse compter un de plus.
    """
    return max(0, -(-int(round(trimestres * 1000)) // 1000))


#: RAFP — les barèmes actuariels qui modulent la valeur de service selon l'âge
#: à la date d'effet : « Ce barème est établi par le conseil d'administration
#: de l'établissement public gestionnaire du régime » (décret n° 2004-569,
#: art. 8). Chacun avec le premier mois d'effet qu'il régit (fiche
#: `rafp_majoration_capital`).
_MAJORATION_RAFP: tuple[tuple[DateMois, dict[int, float]], ...] = (
    # Délibération du 10 novembre 2005, âge pivot à 60 ans, que celle du 5
    # février 2015 garde aux prestations d'avant le 1er mars 2015 ; ses
    # valeurs, au rapport annuel 2012 de l'ERAFP (annexe 1).
    (DateMois(2005, 1), {
        60: 1.00, 61: 1.04, 62: 1.08, 63: 1.13, 64: 1.18, 65: 1.23, 66: 1.29,
        67: 1.35, 68: 1.42, 69: 1.49, 70: 1.57, 71: 1.65, 72: 1.74, 73: 1.84,
        74: 1.96, 75: 2.08,
    }),
    # Délibération du 5 février 2015 : « ≤ 62 1,00 » … « ≥ 75 1,81 », aux
    # prestations qui prennent effet « au premier jour du mois suivant la date
    # à laquelle cette délibération sera devenue exécutoire », le 1er mars
    # 2015. Le tableau que l'ERAFP publie à part écrit 1,80 à 75 ans : la
    # délibération, son rapport annuel et son simulateur, 1,81.
    (DateMois(2015, 3), {
        62: 1.00, 63: 1.04, 64: 1.08, 65: 1.12, 66: 1.17, 67: 1.22, 68: 1.28,
        69: 1.33, 70: 1.40, 71: 1.47, 72: 1.54, 73: 1.62, 74: 1.71, 75: 1.81,
    }),
)

#: RAFP — les barèmes de conversion de la rente en capital (arrêté du 26
#: novembre 2004, art. 12 ; décret n° 2004-569, art. 9), par âge à la date
#: d'effet : celui de la délibération du 10 novembre 2005, que celle du 5
#: février 2015 confirme, au rapport annuel 2012 ; puis celui de la
#: délibération n° 2 du 16 décembre 2021, « au 1er janvier 2022 ».
_CONVERSION_CAPITAL_RAFP: tuple[tuple[DateMois, dict[int, float]], ...] = (
    (DateMois(2005, 1), {
        60: 25.98, 61: 25.30, 62: 24.62, 63: 23.92, 64: 23.22, 65: 22.51,
        66: 21.80, 67: 21.08, 68: 20.36, 69: 19.63, 70: 18.90, 71: 18.16,
        72: 17.43, 73: 16.70, 74: 15.97, 75: 15.24,
    }),
    (DateMois(2022, 1), {
        62: 27.11, 63: 26.34, 64: 25.57, 65: 24.79, 66: 24.02, 67: 23.25,
        68: 22.47, 69: 21.70, 70: 20.92, 71: 20.15, 72: 19.37, 73: 18.61,
        74: 17.84, 75: 17.07,
    }),
)


@dataclass(frozen=True)
class FractionnementRafp:
    """Le capital du RAFP versé en deux fois, comme le conseil
    d'administration l'a réglé : « Le conseil d'administration peut décider
    que le capital est versé par fractions lorsque le nombre de points acquis
    à la date de la liquidation est supérieur ou égal à un seuil qu'il
    détermine et inférieur à 5 125 » (décret n° 2004-569, art. 9, rédaction
    du décret n° 2018-873)."""

    #: Le premier mois d'effet qu'il régit.
    debut: DateMois
    #: Les points à partir desquels le capital se fractionne.
    seuil: int
    #: La première fraction, en mois de la rente : « divisé par 12 et
    #: multiplié par 15 », puis « par 4 ».
    mois_de_rente: int
    #: Le mois, après la liquidation initiale, où le solde est payé.
    mois_du_solde: int
    #: Au-delà de tant de mois entre la retraite de base et la date d'effet
    #: du RAFP, le capital se verse en une fois ; ``None`` : aucune borne.
    ecart_maximal: int | None


#: Délibérations n° 3 du 28 mars 2019 (effet au 1er mai 2019), n° 5 du 30
#: avril 2020 (au-delà du 31 mai 2020) et n° 7 du 8 février 2024 (« à compter
#: du 1er avril 2024 »). Avant mai 2019, le capital se versait en une fois.
_FRACTIONNEMENT_RAFP: tuple[FractionnementRafp, ...] = (
    FractionnementRafp(DateMois(2019, 5), 4600, 15, 16, None),
    FractionnementRafp(DateMois(2020, 6), 4600, 15, 16, 15),
    FractionnementRafp(DateMois(2024, 4), 4900, 4, 5, 4),
)

#: Les mois du premier ordinal, pour dire quand le solde se paie.
_ORDINAUX = {5: "cinquième", 16: "seizième"}


def _bareme_rafp(baremes: tuple[tuple[DateMois, dict[int, float]], ...],
                 date_effet: DateMois) -> dict[int, float]:
    """Le barème qui régit une prestation prenant effet à cette date : le
    dernier dont le premier mois d'effet ne la dépasse pas."""
    retenu = baremes[0][1]
    for debut, bareme in baremes:
        if debut <= date_effet:
            retenu = bareme
    return retenu


def _au_mois(bareme: dict[int, float], age: float) -> float:
    """Le coefficient d'un barème par âge entier, à l'âge en années et en mois.

    « Le coefficient est calculé en fonction de l'âge du demandeur à la date
    d'effet de prestation du RAFP, en tenant compte du nombre d'années et du
    nombre de mois » (ERAFP, rapports annuels 2012, 2014 et 2015, et tableau
    des coefficients de conversion) : entre deux âges entiers, au prorata des
    mois révolus, sans arrondi, que ni les délibérations ni ces notes ne
    disent. En deçà du premier âge, la valeur du premier ; au-delà du dernier,
    celle du dernier.
    """
    premier, dernier = min(bareme), max(bareme)
    age = min(float(dernier), max(float(premier), age))
    ans = int(age + 1e-9)
    if ans >= dernier:
        return bareme[dernier]
    mois = int((age - ans) * 12 + 1e-6)
    bas = bareme[ans]
    return bas + (bareme[ans + 1] - bas) * mois / 12


def majoration_rafp(age_liquidation: float, date_effet: DateMois) -> float:
    """Coefficient de majoration du RAFP à l'âge et à la date d'effet."""
    return _au_mois(_bareme_rafp(_MAJORATION_RAFP, date_effet), age_liquidation)


def conversion_capital_rafp(age_liquidation: float, date_effet: DateMois) -> float:
    """Coefficient de conversion en capital du RAFP, à l'âge et à la date d'effet."""
    return _au_mois(_bareme_rafp(_CONVERSION_CAPITAL_RAFP, date_effet), age_liquidation)


def fractionnement_rafp(points: float, date_effet: DateMois,
                        mois_apres_la_base: int) -> FractionnementRafp | None:
    """Le fractionnement qui s'applique à un capital de ``points`` prenant
    effet à cette date, ``mois_apres_la_base`` mois après la retraite de base ;
    ``None`` quand le capital se verse en une fois. Le capital d'une réversion
    ne se fractionne jamais (« Le versement d'un capital aux bénéficiaires de
    droits dérivés ne donne pas lieu à un fractionnement »)."""
    retenu = None
    for regle in _FRACTIONNEMENT_RAFP:
        if regle.debut <= date_effet:
            retenu = regle
    if retenu is None or points < retenu.seuil:
        return None
    if retenu.ecart_maximal is not None and mois_apres_la_base > retenu.ecart_maximal:
        return None
    return retenu


@dataclass(frozen=True)
class PrestationRafp:
    """La prestation du RAFP, telle que l'ERAFP la verse : une rente à partir
    de 5 125 points, un capital en deçà, versé en une fois ou en deux.
    ``premiere_fraction`` et ``mois_du_solde`` ne valent que pour le second."""

    forme: str  # « rente », « capital » ou « capital_fractionne »
    capital: float | None = None
    conversion: float | None = None
    premiere_fraction: float | None = None
    mois_du_solde: int | None = None
    seuil_du_fractionnement: int | None = None


def prestation_rafp(rente: float, points: float, seuil: float, age: float,
                    date_effet: DateMois, mois_apres_la_base: int) -> PrestationRafp:
    """La forme de la prestation du RAFP et ses montants : ``rente`` est la
    rente annuelle, majorée ; ``points`` ceux qu'elle compte, que ``seuil``
    (5 125) sépare de la rente. Le capital est « déterminé sur la base du
    montant de la rente annuelle par application d'un barème actuariel »
    (décret n° 2004-569, art. 9) ; sa première fraction, « le produit du
    nombre de points acquis par la valeur de service du point en vigueur,
    après application du barème actuariel [...], divisé par 12 et multiplié
    par » 15 puis 4 : autant de mois de la rente."""
    if not 0 < points < seuil:
        return PrestationRafp("rente")
    conversion = conversion_capital_rafp(age, date_effet)
    capital = rente * conversion
    fraction = fractionnement_rafp(points, date_effet, mois_apres_la_base)
    if fraction is None:
        return PrestationRafp("capital", capital, conversion)
    return PrestationRafp("capital_fractionne", capital, conversion,
                          rente * fraction.mois_de_rente / 12, fraction.mois_du_solde,
                          fraction.seuil)


def mois_apres_le_depart(carriere: Carriere, age: float) -> int:
    """Les mois qui séparent un départ à ``age`` du départ que la personne
    déclare, celui de sa pension de base : le RAFP qui attend l'âge légal
    prend effet après elle. Zéro sans départ déclaré."""
    from .. import chronologie as chrono

    acte = (chrono.depart(carriere.chronologie, carriere.personne)
            if carriere.chronologie else None)
    if acte is None or acte["attributs"].get("age") is None:
        return 0
    return max(0, math.floor((age - float(acte["attributs"]["age"])) * 12 + 0.5))


def _coefficient_anticipation(trimestres_manquants: float,
                              maximum: int) -> float | None:
    """Coefficient d'anticipation Agirc-Arrco pour un nombre de trimestres.

    ``maximum`` est la dernière ligne du barème : vingt trimestres pour la
    table des trimestres manquants, quarante pour celle des âges. Au-delà, la
    table ne dit rien et ``None`` est renvoyé — la prolonger reviendrait à
    inventer un coefficient plus favorable que celui de l'autre table, alors
    que le régime retient la plus avantageuse des deux.

    Les trimestres sont comptés en ENTIERS ARRONDIS AU SUPÉRIEUR : le barème
    est un escalier, et un assuré à qui il manque trois ans et dix mois se voit
    opposer seize trimestres, pas quinze. C'est la lecture que la caisse
    illustre elle-même dans son exemple.
    """
    manquants = _au_trimestre_superieur(trimestres_manquants)
    if manquants <= 0:
        return 1.0
    if manquants > maximum:
        return None
    coefficient = 1.0
    precedent = 0
    for borne, pas in _PALIERS_ANTICIPATION:
        tranche = min(manquants, borne) - precedent
        if tranche > 0:
            coefficient -= tranche * pas
        precedent = borne
        if manquants <= borne:
            break
    return max(0.0, coefficient)

#: Barèmes de décote lus dans une table, et non dans la fiche du régime : le
#: coefficient et l'âge d'annulation y montent en charge avec la date où le
#: droit s'ouvre. ``regimes_speciaux_age_fixe`` prend le coefficient de la table
#: des régimes spéciaux, et l'âge d'annulation propre au ballet de l'Opéra, que
#: borne celui écrit dans la fiche.
_BAREMES_DECOTE_EN_TABLE = frozenset(
    {"fonction_publique", "regimes_speciaux", "regimes_speciaux_age_fixe"}
)

#: Ceux des régimes spéciaux réformés en 2008 : leurs marches tombent au
#: 1er juillet (:func:`millesime_du_bareme`), et leur décompte par la durée a
#: sa borne (:func:`borne_de_la_duree`).
_BAREMES_REGIMES_SPECIAUX = frozenset({"regimes_speciaux", "regimes_speciaux_age_fixe"})


@dataclass(frozen=True)
class EligibleMinimum:
    """Régime de base susceptible d'être porté au minimum contributif.

    Quatre grandeurs, et pas une seule, parce que le droit en demande quatre :
    la pension à relever, les deux fractions de durée qui proratisent le
    montant de base et sa majoration, la condition de taux plein qui ouvre le
    droit, et le coefficient de surcote qu'il faut retirer avant de comparer
    au plancher puis rendre après.
    """

    #: Indice de la pension dans :attr:`Pensions.regimes`.
    indice: int
    #: Durée d'assurance acquise dans le régime / durée requise, bornée à 1.
    prorata_assurance: float
    #: Durée COTISÉE acquise dans le régime / durée requise, bornée à 1.
    prorata_cotise: float
    #: La pension est-elle liquidée au taux plein dans ce régime ?
    taux_plein: bool
    #: Coefficient de surcote déjà incorporé au montant de la pension.
    surcote: float = 1.0
    #: Ce que le minimum d'une pension proratisée lit en plus (fiche
    #: ``minimum_contributif_international``) : les durées d'assurance et
    #: cotisée du régime, non bornées, sa durée maximum, qui proratise, et
    #: la durée requise pour le taux plein.
    duree_regime: int = 0
    cotisee_regime: int = 0
    proratisation: int = 0
    requis: int = 0
    #: La part du montant que le minimum ne relève pas : la fraction d'avant
    #: 1998 des cultes, qui a ses propres majorations (:mod:`.cultes`).
    hors_minimum: float = 0.0
    #: Ce que le minimum d'un polypensionné lit depuis 2004 (fiche
    #: ``minimum_contributif``) : la durée d'assurance et la durée cotisée
    #: tous régimes de base, celles du régime comprises, sommées régime par
    #: régime sans limite de quatre trimestres par an.
    duree_tous_regimes: int = 0
    cotisee_tous_regimes: int = 0
    #: Le régime valide-t-il l'AVPF et l'AVA, que la majoration compte depuis
    #: septembre 2023 ? Le régime général, seul.
    porte_avpf: bool = False


@dataclass(frozen=True)
class EligibleMinimumGaranti:
    """Régime de la fonction publique susceptible d'atteindre son plancher."""

    #: Indice de la pension dans :attr:`Pensions.regimes`.
    indice: int
    #: Durée de services acquise dans le régime, en trimestres.
    trimestres_services: int
    #: La pension est-elle liquidée au taux plein, ou l'assuré atteignait-il
    #: l'âge d'ouverture de ses droits avant 2011 ?
    ouvert: bool
    #: Durée des services et bonifications qui ouvre le pourcentage maximum :
    #: le d de L. 17 y rapporte le minimum d'une pension de moins de quinze
    #: ans. ``None`` garde le c, un quinzième de 57,5 % par année.
    duree_maximum: int | None = None


@dataclass(frozen=True)
class EligiblePlafondEnfants:
    """La pension d'un régime du code des pensions, dont le plafond de L. 18,
    V, borne la majoration pour enfants au traitement qui l'a liquidée
    (:func:`~.completer.majoration_sous_le_traitement`, fiche
    ``majoration_enfants_plafond_fonction_publique``)."""

    #: Indice de la pension dans :attr:`Pensions.regimes`.
    indice: int
    #: Le traitement ou la solde de L. 15, en euros par an à la date d'effet.
    traitement: float
    #: La part du montant que la surcote de L. 14, III, y ajoute, en euros :
    #: depuis la décision du Conseil d'État du 29 décembre 2020, la pension se
    #: compare au traitement sans elle.
    surcote: float


@dataclass(frozen=True)
class EligibleAgricole:
    """La pension des non-salariés agricoles, que la pension majorée de
    référence relève et dont le complément différentiel de la RCO lit les
    durées (:func:`~.completer.pension_majoree`,
    :func:`~.completer.complement_differentiel`).

    Le modèle ne connaît que le statut de chef d'exploitation, à titre
    principal : la durée non salariée agricole est donc aussi celle de chef.
    """

    #: Indice de la pension dans :attr:`Pensions.regimes`.
    indice: int
    #: Liquidée au taux plein dans le régime : durée requise, âge du taux
    #: plein, inaptitude ou handicap (L. 732-54-1, L. 732-63 depuis 2023).
    taux_plein: bool
    #: La durée tous régimes atteint-elle la durée requise ? Ce que le
    #: complément de la RCO demandait jusqu'en août 2023 (L. 732-63, I, 2°).
    duree_requise_atteinte: bool
    #: Coefficient de surcote déjà incorporé au montant, que la PMR retire
    #: avant de comparer (D. 732-111, D. 732-112).
    surcote: float
    #: Durée d'assurance non salariée agricole, en trimestres : celle des
    #: années, sans les trimestres pour enfants.
    duree: int
    #: Les trimestres pour enfants que le régime porte, que les durées
    #: comptent depuis 2026 (D. 732-110, D. 732-166-3).
    enfants: int
    #: La durée de référence DR, en trimestres : celle de la retraite
    #: forfaitaire (R. 732-61, 1°), 150 au moins (D. 732-111, D. 732-166-4).
    reference: int


@dataclass(frozen=True)
class Pensions:
    """Ce que l'étape « liquider chaque régime » écrit."""

    #: La personne dont les pensions sont liquidées.
    personne: str
    #: La pension de chaque régime qui liquide, dans l'ordre du relevé.
    regimes: tuple[PensionRegime, ...]
    #: Les régimes de base qui portent le minimum contributif.
    minimum: tuple[EligibleMinimum, ...]
    #: Les régimes de la fonction publique qui portent le minimum garanti.
    garanti: tuple[EligibleMinimumGaranti, ...]
    #: La plus longue des durées requises des régimes en annuités.
    requis: int
    #: Le plus haut des taux de liquidation des régimes en annuités.
    taux: float
    fiabilite: Fiabilite
    #: La pension des non-salariés agricoles, quand elle porte la pension
    #: majorée de référence ; ``None`` sinon.
    agricole: EligibleAgricole | None = None
    #: Les pensions du code des pensions, que le plafond de L. 18 borne.
    plafonds: tuple[EligiblePlafondEnfants, ...] = ()

    def donnees(self) -> dict:
        """Les pensions, telles que le schéma de l'étape les décrit."""
        regimes = [{"regime": p.regime, "montant": p.montant, "calcul": p.type_calcul,
                    "detail": p.detail, "fiabilite": p.fiabilite.name.lower()}
                   for p in self.regimes]
        for eligible in self.minimum:
            regimes[eligible.indice]["minimum"] = {
                "prorata_assurance": eligible.prorata_assurance,
                "prorata_cotise": eligible.prorata_cotise,
                "taux_plein": eligible.taux_plein,
                "surcote": eligible.surcote,
            }
            if eligible.hors_minimum:
                regimes[eligible.indice]["minimum"]["hors_minimum"] = eligible.hors_minimum
        for eligible in self.garanti:
            regimes[eligible.indice]["garanti"] = {
                "trimestres_services": eligible.trimestres_services,
                "ouvert": eligible.ouvert,
                "duree_maximum": eligible.duree_maximum,
            }
        if self.agricole is not None:
            regimes[self.agricole.indice]["agricole"] = {
                "taux_plein": self.agricole.taux_plein,
                "duree_requise_atteinte": self.agricole.duree_requise_atteinte,
                "surcote": self.agricole.surcote,
                "duree": self.agricole.duree,
                "enfants": self.agricole.enfants,
                "reference": self.agricole.reference,
            }
        for eligible in self.plafonds:
            regimes[eligible.indice]["plafond_enfants"] = {
                "traitement": eligible.traitement,
                "surcote": eligible.surcote,
            }
        return {"schema_version": SCHEMA_VERSION, "personne": self.personne,
                "regimes": regimes, "requis": self.requis, "taux": self.taux,
                "fiabilite": self.fiabilite.name.lower()}


def liquider_chaque_regime(moteur: ScenarioActuel, releve: Releve, ouverture: Ouverture,
                           contexte: Contexte | None = None,
                           regimes: frozenset[str] | None = None,
                           nationale: bool = False) -> Pensions:
    """La pension de chaque régime où le relevé porte un droit.

    La durée requise de référence, que l'étape « ouvrir le droit » a lue, est
    celle que l'abattement des complémentaires oppose. Le contexte dit ce que
    le calcul neutralise : la décote, la surcote et l'abattement liés à l'âge
    pour valoriser des droits acquis ; l'AVPF pour en mesurer l'apport.
    ``regimes`` sont ceux que la demande vise, quand ils ne liquident pas tous
    au même départ (:mod:`.departs`) ; ``None`` : tous. ``nationale`` liquide
    la pension NATIONALE de qui a des périodes qu'un accord compare : leurs
    trimestres n'entrent pas dans la durée du taux (fiche
    ``pension_proratisee``).
    """
    carriere = releve.carriere
    durees, droits = releve.durees, releve.droits
    annee_liquidation = carriere.annee_liquidation
    age_liquidation = carriere.age_liquidation or 0.0
    requis_reference = ouverture.requis
    ignorer_penalite_age = contexte is not None and contexte.neutralise("decote_surcote")
    avpf = contexte is None or not contexte.neutralise("avpf")
    #: Les majorations de la fraction d'avant 1998 des cultes, que la cascade
    #: des avantages non contributifs mesure avec le minimum contributif.
    majorations_des_cultes = (contexte is None
                              or not contexte.neutralise("avantages_non_contributifs"))
    #: Le départ anticipé des assurés handicapés ouvre-t-il cette liquidation
    #: (:func:`~.ouvrir.ouvrir`) ? Ses régimes la servent alors au taux plein,
    #: majorée, et les complémentaires qui les suivent sans coefficient.
    par_le_handicap = ouverture.motif == "handicap"
    version_du_handicap = (invalidite.version_du_handicap(moteur, carriere)
                           if par_le_handicap else None)
    regimes_du_handicap = (moteur.invalidites.regimes("handicap")
                           if par_le_handicap else frozenset())
    codes = [code for code in droits.codes if regimes is None or code in regimes]
    groupes = releve.groupes

    pensions: list[PensionRegime] = []
    fiabilite_globale = Fiabilite.CERTIFIEE
    trimestres_requis = 0
    taux_retenu = 0.0
    #: Régimes de base qui portent le minimum contributif : indice dans
    #: ``pensions``, prorata de durée d'assurance, prorata de durée
    #: COTISÉE, et condition de taux plein remplie ou non.
    eligibles_minimum: list[EligibleMinimum] = []
    #: Régimes de la fonction publique qui portent le minimum garanti.
    eligibles_garanti: list[EligibleMinimumGaranti] = []
    #: Les pensions du code des pensions, que le plafond de L. 18 borne.
    eligibles_plafond: list[EligiblePlafondEnfants] = []
    #: La pension des non-salariés agricoles, que la pension majorée de
    #: référence relève.
    agricole: EligibleAgricole | None = None

    # Ce que les étapes de l'acquisition ont écrit, sous les noms que la
    # liquidation lit.
    cumul_cotisations = droits.cumul_cotisations
    points_acquis = droits.points_acquis
    fiabilite_points = droits.fiabilite_points
    gratuits_attribues = droits.gratuits
    trimestres_par_regime = durees.trimestres_par_regime
    bonifications_par_regime = durees.bonifications_par_regime
    cumul_plafonne = durees.cumul_plafonne
    majoration_enfants = durees.enfants

    for code in codes:
        # La durée tous régimes que le taux de ce régime lit : les périodes
        # hors de France y entrent, celles que sa famille retient
        # (:mod:`.etranger`) ; jamais dans sa durée, qui proratise.
        famille = famille_du_regime(moteur, code)
        trimestres = durees.pour_le_taux(famille, nationale)
        cumul = cumul_cotisations.get(code, 0.0)
        regime = moteur.catalogue[code]
        periode = regime.periode(min(annee_liquidation, derniere_annee(regime)))
        if periode is None:
            continue
        fiabilite_globale = min(fiabilite_globale, regime.fiabilite)
        membres = groupes.get(code, (code,))
        if membres[0] != code:
            # Liquidé par le régime qui lui a succédé.
            continue

        if periode.type_calcul in ("points", "mixte"):
            if periode.meilleures_annees_non_salaries:
                # LA PENSION AGRICOLE DEPUIS 2026 n'est plus une somme de
                # points : voir `pension_des_non_salaries_agricoles`.
                pension = pension_des_non_salaries_agricoles(
                    moteur, periode, carriere, releve, code, trimestres,
                    requis_reference, age_liquidation, annee_liquidation,
                    ignorer_penalite_age,
                )
                fiabilite_globale = min(fiabilite_globale, pension.fiabilite)
                if "pension_majoree_reference" in periode.avantages_non_contributifs:
                    agricole = eligible_agricole(
                        moteur, periode, carriere, releve, membres, trimestres,
                        age_liquidation, len(pensions),
                        1.0 if ignorer_penalite_age else abattement_points(
                            moteur, periode, carriere, trimestres, requis_reference,
                            age_liquidation, annee_liquidation,
                            durees.trimestres_par_regime.get(code, 0)),
                        code in regimes_du_handicap)
                pensions.append(pension)
                continue
            montant = 0.0
            fiabilite_regime = regime.fiabilite
            details = []

            points = points_acquis.get(code, 0.0)
            #: Ce que vaut un point dans le montant, quand il a une valeur de
            #: service : la part des points abattus s'y mesure.
            service_des_points: float | None = None
            # BARÈME DU TRIMESTRE : la pension minière est la durée, majorée
            # du coefficient de l'article 131-1, multipliée par la valeur du
            # trimestre de la date d'effet — l'une et l'autre lues dans
            # `bareme_trimestre_<nom>.csv`. La fiche ne portait que la
            # seconde, et par les prix.
            trimestre = (
                moteur.baremes_trimestre.valeurs(
                    periode.bareme_trimestre, carriere.date_liquidation)
                if points and periode.bareme_trimestre else None
            )
            if trimestre is not None:
                valeur_trimestre, coefficient_duree, fiabilite_trimestre = trimestre
                montant += points * coefficient_duree * valeur_trimestre
                fiabilite_regime = min(
                    fiabilite_regime, fiabilite_trimestre, fiabilite_points[code]
                )
                details.append(
                    f"{points:,.2f} trimestres × coefficient de majoration de "
                    f"la durée {coefficient_duree:.3f} × valeur du trimestre "
                    f"{_sans_zeros_inutiles(valeur_trimestre, 2)} €"
                )
            elif points:
                valeur = valeur_du_point(moteur,
                    periode.points_de or code, carriere.date_liquidation
                )
                if valeur is None and periode.valeur_point_euros is not None:
                    # Valeur de service écrite dans la fiche : le régime
                    # dont la caisse est seule à la publier n'a rien de
                    # certifiable dans `valeurs_point.csv`, et retombait
                    # donc sur le rendement instantané.
                    valeur = (
                        valeur_point_fiche(moteur, periode, annee_liquidation),
                        Fiabilite.MOYENNE,
                    )
                if valeur is not None:
                    service, fiabilite_service = valeur
                    # COEFFICIENT DE DURÉE de la proportionnelle agricole :
                    # la pension vaut « points × valeur du point × 37,5 /
                    # durée requise en années ». Il est neutre pour les
                    # générations qui devaient 37,5 ans, et retire un
                    # huitième à celles qui en doivent 43 — sans lui, le
                    # maximum du barème cesse de valoir ce que le code lui
                    # fait valoir.
                    coefficient_duree = 1.0
                    if periode.bareme_points == "msa_proportionnelle":
                        requis, fiabilite_duree = ouvrir.duree_requise(moteur, 
                            periode, carriere
                        )
                        if fiabilite_duree is not None:
                            fiabilite_regime = min(
                                fiabilite_regime, fiabilite_duree
                            )
                        if requis > 0:
                            coefficient_duree = 37.5 / (requis / 4.0)
                    montant += points * service * coefficient_duree
                    service_des_points = service * coefficient_duree
                    fiabilite_regime = min(
                        fiabilite_regime, fiabilite_service, fiabilite_points[code]
                    )
                    gratuits = gratuits_attribues.get(code, (0.0, 0))[0]
                    details.append(
                        f"{points:,.2f} points × valeur de service "
                        f"{_sans_zeros_inutiles(service, 6)} €"
                        + ("" if coefficient_duree == 1.0
                           else f" × {coefficient_duree:.4f}")
                        # Les points gratuits sont DANS le compte : la
                        # formule se refait sur le total, et le lecteur
                        # voit d'où vient ce qu'il n'a pas cotisé.
                        + ("" if not gratuits
                           else f" (dont {gratuits:,.2f} points gratuits)")
                    )

            # RÉGIME MIXTE : une part forfaitaire s'ajoute aux points. Le
            # régime agricole en est le seul exemple — sa retraite
            # forfaitaire vaut l'allocation aux vieux travailleurs salariés
            # pour une carrière complète, et se proratise sur la durée
            # (L. 732-24). Le moteur traitait `mixte` comme un synonyme de
            # `points` et ne la servait pas du tout.
            if (periode.type_calcul == "mixte"
                    and periode.pension_forfaitaire_annuelle is not None):
                requis, _ = ouvrir.duree_requise(moteur, periode, carriere)
                proratisation, fiabilite_prorata = duree_proratisation(moteur, 
                    periode, carriere, requis
                )
                if fiabilite_prorata is not None:
                    fiabilite_regime = min(fiabilite_regime, fiabilite_prorata)
                acquis = min(trimestres_par_regime.get(code, 0), proratisation)
                if proratisation > 0 and acquis > 0:
                    forfait = (
                        periode.pension_forfaitaire_annuelle
                        * moteur.macro.coefficient_prix(
                            periode.pension_forfaitaire_annee or annee_liquidation,
                            annee_liquidation,
                        )
                        * acquis / proratisation
                    )
                    montant += forfait
                    details.append(
                        f"forfait {forfait:,.2f} € ({acquis}/{proratisation})"
                    )

            # Années sans prix d'achat connu : le rendement instantané prend
            # le relais, régime par régime et année par année. Il fait
            # partie du barème du point — c'est le rapport de la valeur de
            # service au prix d'achat —, et une fiche qui emprunte ce barème
            # (`points_de`) emprunte donc aussi le rendement : sans quoi elle
            # ne trouvait aucune ligne sous son propre code, et sa pension
            # tombait à zéro sans rien dire.
            if cumul:
                rendement, fiabilite_rendement = moteur.rendements.rendement(
                    periode.points_de or code,
                    min(annee_liquidation, derniere_annee(regime)),
                )
                montant += cumul * rendement
                fiabilite_regime = min(fiabilite_regime, fiabilite_rendement)
                details.append(
                    f"cotisations revalorisées {cumul:,.0f} € "
                    f"× rendement {rendement:.2%}"
                )

            fiabilite_globale = min(fiabilite_globale, fiabilite_regime)
            montant_brut = montant
            abattement = 1.0
            #: Les points qui gardent le coefficient pour âge, et ce
            #: coefficient, quand il est plus sévère que celui des autres.
            abattus_a_l_age: tuple[float, float] | None = None
            if not ignorer_penalite_age:
                # Le coefficient d'anticipation multiplie le montant : sans
                # lui, la formule affichée ne le retrouve pas — à dix ans
                # d'anticipation elle en donnait deux fois trop, sans que
                # rien à l'écran ne dise pourquoi.
                abattement = abattement_points(moteur,
                    periode, carriere, trimestres, requis_reference,
                    age_liquidation, annee_liquidation,
                    trimestres_par_regime.get(code, 0),
                    handicap=par_le_handicap,
                )
                # LA TRANCHE C D'AVANT 2016 GARDE LE COEFFICIENT POUR ÂGE.
                # L'exonération au taux plein ne vaut que « sur les tranches
                # A et B des rémunérations » (accords du 13 novembre 2003 et
                # du 18 mars 2011), la table des trimestres manquants pas
                # davantage pour ces droits (annexe V de la convention de
                # 1947) : les points de l'Agirc constitués sur la tranche C
                # jusqu'au 31 décembre 2015 prennent le coefficient de l'âge
                # avant celui du 1° de l'article L. 351-8 (accord du 17
                # novembre 2017, articles 84, 2 et 102). Le coefficient
                # affiché est celui de la pension entière, moyenne des deux
                # pondérée par leurs montants : la formule le refait.
                abattus = droits.points_abattus.get(code, 0.0)
                if abattus > 0 and service_des_points is not None and montant > 0:
                    pour_age = coefficient_pour_age(
                        moteur, periode, carriere, age_liquidation)
                    if pour_age < abattement:
                        part = min(1.0, abattus * service_des_points / montant)
                        abattement = abattement * (1.0 - part) + pour_age * part
                        abattus_a_l_age = (abattus, pour_age)
                montant *= abattement
            detail = _formule_points(details, abattement)
            if abattus_a_l_age is not None:
                detail += (
                    f", dont {abattus_a_l_age[0]:,.2f} points de la tranche C "
                    f"d'avant 2016 au coefficient pour âge {abattus_a_l_age[1]:.4f}"
                )
            # Les années qu'aucun prix d'achat ne couvre encore passent par
            # le rendement : le seuil se compare donc aux points que vaut
            # TOUT le montant, à la valeur de service de la liquidation.
            points_totaux = points
            capital = None
            if periode.capital_seuil_points is not None:
                valeur = valeur_du_point(moteur,
                    periode.points_de or code, carriere.date_liquidation)
                if valeur is not None and valeur[0] > 0:
                    points_totaux = montant_brut / valeur[0]
            if (periode.capital_seuil_points is not None
                    and 0 < points_totaux < periode.capital_seuil_points):
                # SOUS LE SEUIL, UN CAPITAL. Le RAFP ne sert de rente qu'à
                # partir de 5 125 points ; en deçà, il verse « points ×
                # coefficient de majoration × valeur de service × coefficient
                # de conversion en capital » (décret n° 2004-569, art. 9), en
                # une fois, ou en deux près du seuil depuis mai 2019
                # (:func:`prestation_rafp`). Le montant annuel reste celui de
                # la rente dont le capital est l'équivalent actuariel : c'est
                # lui que les comparaisons annuelles savent lire.
                versee = prestation_rafp(
                    montant, points_totaux, periode.capital_seuil_points,
                    age_liquidation, carriere.date_de_l_age(age_liquidation),
                    mois_apres_le_depart(carriere, age_liquidation))
                capital = versee.capital
                if versee.forme == "capital":
                    detail += (
                        f" ; versé en capital, {capital:,.0f} € en une fois "
                        f"(moins de {periode.capital_seuil_points:,.0f} points)"
                    )
                else:
                    detail += (
                        f" ; versé en capital, {capital:,.0f} € en deux fois, "
                        f"{versee.premiere_fraction:,.0f} € à la liquidation et le "
                        f"solde le {_ORDINAUX[versee.mois_du_solde]} mois qui la suit "
                        f"(de {versee.seuil_du_fractionnement:,.0f} à "
                        f"{periode.capital_seuil_points - 1:,.0f} points)"
                    )
            if (periode.type_calcul == "mixte"
                    and "pension_majoree_reference" in periode.avantages_non_contributifs):
                agricole = eligible_agricole(
                    moteur, periode, carriere, releve, membres, trimestres,
                    age_liquidation, len(pensions), abattement,
                    code in regimes_du_handicap)
            pensions.append(PensionRegime(
                regime=code, montant=montant, type_calcul=periode.type_calcul,
                detail=detail,
                fiabilite=fiabilite_regime,
                capital=capital,
            ))
            continue

        # Régimes en annuités — et régimes FORFAITAIRES, dont la pension ne
        # dépend pas du revenu mais de la seule durée. Le second cas se
        # traite comme le premier en remplaçant le salaire de référence par
        # le montant forfaitaire : c'est bien un `montant × taux × durée /
        # durée requise`, à ceci près que le montant est le même pour tous.
        # Faute de ce montant, la fiche retombait sur la moyenne des
        # revenus, c'est-à-dire sur un taux de remplacement de 100 %.
        plafonner = periode.assiette in ("plafonnee", "tranche_1", "tranche_a")
        annees_alignees: tuple[int, str] | None = None
        # LA PENSION DES CULTES EN DEUX FRACTIONS (:mod:`.cultes`) : ce qui suit
        # ne calcule que celle des périodes d'après 1997, sur leur salaire
        # annuel moyen et leur durée ; l'autre s'y ajoute plus bas.
        durees_cultes = (
            cultes.durees(durees, membres,
                          enfants=annee_liquidation >= cultes.ALIGNEMENT)
            if periode.fractions_des_cultes else None
        )
        if periode.pension_forfaitaire_annuelle is not None:
            salaire_reference = (
                periode.pension_forfaitaire_annuelle
                * moteur.macro.coefficient_prix(
                    periode.pension_forfaitaire_annee or annee_liquidation,
                    annee_liquidation,
                )
            )
        else:
            enfants_majores = (carriere.nombre_enfants
                               if majoration_enfants is not None else 0)
            # LES ANNÉES D'UN ANCIEN EXPLOITANT : depuis 2026, la part des
            # vingt-cinq que R. 173-3-2 laisse aux régimes alignés. Celles
            # d'un travailleur migrant : la pension proratisée les réduit
            # aussi au prorata des périodes étrangères équivalentes.
            annees_alignees = (
                annees_des_regimes_alignes(
                    moteur, carriere, releve, membres,
                    nombre_d_annees_retenues(
                        moteur, periode, carriere, carriere.annee_naissance,
                        enfants_majores),
                    etrangers=0 if nationale else trimestres_etrangers_au_salaire_moyen(
                        moteur, carriere, durees, famille))
                if periode.salaire_reference in (
                    "25_meilleures_annees", "10_meilleures_annees")
                else None
            )
            salaire_reference = salaire_de_reference(moteur, 
                code, carriere, periode, annee_liquidation, plafonner,
                carriere.annee_naissance, avpf, membres,
                enfants_majores=enfants_majores,
                depuis=None if durees_cultes is None else cultes.ALIGNEMENT,
                annees=None if annees_alignees is None else annees_alignees[0],
            )
        requis, fiabilite_duree = ouvrir.duree_requise(moteur, periode, carriere)
        if fiabilite_duree is not None:
            fiabilite_globale = min(fiabilite_globale, fiabilite_duree)
        trimestres_requis = max(trimestres_requis, requis)
        # Le dénominateur de la PRORATISATION n'est pas la durée requise :
        # l'article R. 351-6 en fixe une autre, plus courte pour les
        # générations d'avant 1949. Confondre les deux retirait à un assuré
        # né en 1945 avec 156 trimestres les 2,5 % que 156/160 lui coûte,
        # là où 156/154 lui donne le coefficient plein.
        proratisation, fiabilite_proratisation = duree_proratisation(moteur, 
            periode, carriere, requis
        )
        if fiabilite_proratisation is not None:
            fiabilite_globale = min(fiabilite_globale, fiabilite_proratisation)
        # Le numérateur n'est pas le même selon le régime : services et
        # bonifications dans la fonction publique (L. 13), durée
        # d'assurance partout ailleurs (R. 351-1).
        # Le plafond est la durée requise, que les BONIFICATIONS seules
        # peuvent dépasser, et dans la limite d'un taux : « Le pourcentage
        # maximum fixé à l'article L 13 peut-être augmenté de cinq points du
        # chef des bonifications » (L. 12 CPCMR). Le module plafonnait
        # services et bonifications ensemble à la durée requise, et servait
        # 75 % à une mère de trois enfants à qui le droit en doit près de 80.
        bonifications = (
            somme_ordonnee(bonifications_par_regime.get(m, 0) for m in membres)
            + durees.bonifications_des_emplois(membres)
            if periode.taux_maximum_bonifie and periode.taux_plein else 0
        )
        # Les membres d'un groupe liquidé ensemble se somment ANNÉE PAR
        # ANNÉE : deux activités cumulées dans deux régimes alignés ne
        # valident pas huit trimestres la même année. Le code des pensions
        # compte ses services au jour, et ne les arrondit qu'au décompte final
        # (R. 26 ; fiche decompte_des_services_fonction_publique).
        au_jour = durees_cultes is None and durees.au_jour(membres)
        numerateur = (
            durees_cultes.depuis_1998 if durees_cultes is not None
            else durees.services_liquidables(membres) if au_jour
            else cumul_plafonne(
                "services"
                if moteur.catalogue[code].famille == "fonction_publique"
                else "assurance",
                membres,
            )
        )
        #: La durée d'assurance que sa décote lit, au jour, sans arrondi
        #: (L. 14, I) : celle des trimestres entiers, et ce que les fractions
        #: de ses services y changent.
        ecart_au_jour = durees.ecart_au_jour if au_jour and durees.duree_au_jour(membres) else 0.0
        if (durees_cultes is None and majoration_enfants is not None
                and moteur.catalogue[code].famille == "special"):
            # LA MAJORATION DE DURÉE N'ENTRE PAS AUX SERVICES d'un régime
            # spécial, qui liquide ses services et ses bonifications : la SNCF
            # (décret n° 2008-639, articles 12 et 13 III), la RATP (décret
            # n° 2008-637, articles 23 et 24 III), et les régimes à qui le
            # modèle prête L. 12 bis. Sa durée dans le régime les portait
            # toutes ; seules les bonifications y restent.
            portes = majoration_enfants.par_regime()
            numerateur -= somme_ordonnee(portes[m][0] - portes[m][1] for m in membres if m in portes)
        #: Ce que l'emploi classé ajoute à la seule durée que ce régime oppose
        #: à sa décote (:class:`~.compter.TrimestresEmploi`).
        majorations_emplois = durees.majorations_des_emplois(membres)
        if durees_cultes is None:
            # LA BONIFICATION DE L'EMPLOI CLASSÉ entre aux services, sous le
            # pourcentage maximum : le minimum qui suit borne les services et
            # elle ensemble à la durée requise, et seules les bonifications de
            # L. 12 le dépassent.
            numerateur += durees.services_des_emplois(membres)
        trimestres_regime = min(numerateur, proratisation + bonifications)
        #: Rapport des trimestres liquidables à la durée requise, borné au
        #: taux maximum — 80/75 avec des bonifications, un sans elles.
        rapport_maximum = (periode.taux_maximum_bonifie / periode.taux_plein
                           if bonifications else 1.0)
        if (periode.duree_maximum_avant_age is not None
                and periode.duree_maximum_avant_age_trimestres is not None
                and age_liquidation < periode.duree_maximum_avant_age):
            # DURÉE LIQUIDABLE PLAFONNÉE PAR L'ÂGE. L'article R. 13 du code
            # des pensions de retraite des marins : « le maximum des
            # annuités liquidables dans les pensions d'ancienneté dont la
            # liquidation est demandée avant cinquante-cinq ans est fixé à
            # vingt-cinq annuités ». Un marin parti à cinquante ans avec
            # trente ans de mer touche 50 % du salaire forfaitaire, non
            # 60 %. C'est la seule règle du catalogue où l'ÂGE borne la
            # durée, et non l'inverse.
            # Levé « au profit d'un marin âgé d'au moins cinquante-deux ans
            # et demi, réunissant trente-sept annuités et demie de
            # services » : le même alinéa, b).
            levee = (periode.duree_maximum_levee_age is not None
                     and periode.duree_maximum_levee_trimestres is not None
                     and age_liquidation >= periode.duree_maximum_levee_age
                     and trimestres_regime
                     >= periode.duree_maximum_levee_trimestres)
            if not levee:
                trimestres_regime = min(
                    trimestres_regime,
                    periode.duree_maximum_avant_age_trimestres,
                )
        if periode.trimestres_retenus_maximum is not None:
            # LA DURÉE RETENUE MONTE PLUS LENTEMENT QUE LE DÉNOMINATEUR. De
            # 1972 à 1974, « la pension est égale à autant de cent
            # cinquantièmes de la pension calculée selon les taux prévus […]
            # que l'assuré justifie de trimestres d'assurance, dans la limite
            # de 128 » en 1972, de 136 en 1973, de 144 en 1974 (décret
            # n° 45-0179, article 72-1, au régime général ; décret
            # n° 50-1225, article 59-1, aux salariés agricoles) : une
            # carrière complète liquidée en 1972 reçoit 128/150 de la
            # pension normale, non la pension entière.
            trimestres_regime = min(trimestres_regime,
                                    periode.trimestres_retenus_maximum)

        taux = periode.taux_plein or 0.5
        #: La version de la retraite pour invalidité, quand ce régime du code
        #: des pensions liquide à la radiation des cadres pour invalidité.
        pour_invalidite = invalidite.retraite_pour_invalidite(moteur, code, carriere)
        #: Part du taux qui vient de la surcote. Le minimum contributif se
        #: compare à la pension AVANT surcote : il faut donc pouvoir la
        #: retirer, puis la rendre.
        coefficient_surcote = 1.0
        #: Trimestres de décote effectivement retenus : la condition
        #: d'ouverture du minimum garanti en dépend.
        trimestres_decote = 0.0
        #: Âge d'annulation de la décote, que l'ouverture transitoire du
        #: minimum garanti minore.
        age_annulation: float | None = None
        #: Le facteur dont la décote réduit le taux : la fraction d'avant 1998
        #: des cultes subit la même (décret n° 2006-1325, art. 2, II).
        facteur_decote = 1.0
        #: La durée du régime avant sa majoration après l'âge du taux plein,
        #: quand elle a été majorée : le détail la dit.
        duree_non_majoree: int | None = None
        if not ignorer_penalite_age:
            decote, age_annulation, fiabilite_decote = decote_opposable(moteur, 
                periode, carriere, annee_liquidation
            )
            trimestres_decote = trimestres_de_decote(moteur,
                periode, carriere, trimestres + majorations_emplois + ecart_au_jour, requis,
                age_liquidation, age_annulation
            )
            if au_jour and durees.duree_au_jour(membres) and trimestres_regime >= proratisation:
                # La pension que l'arrondi du décompte final porte au
                # pourcentage maximum ne subit pas de décote, quand même la
                # durée d'assurance, qui ne s'arrondit pas, n'atteindrait pas la
                # durée requise : « les dispositions de l'article L. 14 ne
                # sauraient avoir pour effet de lui appliquer la décote »
                # (Conseil d'État, 2 février 2010, n° 311495).
                trimestres_decote = 0.0
            if (taux_plein_des_femmes(periode, carriere, durees, age_liquidation)
                    or invalidite.taux_plein_de_l_inapte(
                        moteur, code, carriere, age_liquidation)
                    or pour_invalidite is not None
                    or code in regimes_du_handicap
                    or (invalidite.sans_decote_du_fonctionnaire(moteur, code, carriere)
                        and ouvrir.droit_militaire(moteur, periode, carriere) is None)):
                # Le taux de soixante-cinq ans des femmes d'avant 1983 ; le
                # taux plein de l'inapte, quelle que soit sa durée (L. 351-8,
                # 2°), le taux de soixante-cinq ans avant 1983 ; la pension du
                # fonctionnaire mis à la retraite pour invalidité, que « le
                # coefficient de minoration » n'atteint pas (L. 14, I) ; le
                # départ anticipé des assurés handicapés, au taux plein
                # (L. 351-8, 4° bis ; R. 37 bis) ; le fonctionnaire handicapé,
                # que le coefficient de minoration n'atteint jamais (L. 14, I).
                trimestres_decote = 0.0
            if decote and trimestres_decote > 0:
                # Les régimes sans décote (fonction publique avant 2004,
                # régimes spéciaux avant 2008) ne subissent que la
                # proratisation : leur `decote_par_trimestre` est nul.
                if fiabilite_decote is not None:
                    fiabilite_globale = min(fiabilite_globale, fiabilite_decote)
                facteur_decote = max(0.0, 1.0 - decote * trimestres_decote)
                taux *= facteur_decote
            if periode.majoration_d_ajournement and decote:
                # Avant le 1er avril 1983, le taux croît avec l'âge seul,
                # au-delà de soixante-cinq ans comme en deçà.
                ajournement = ecart_au_taux_plein(
                    moteur, periode, carriere, age_liquidation, age_annulation)
                if ajournement > 0:
                    coefficient_surcote = 1.0 + decote * ajournement
                    taux *= coefficient_surcote
            # La durée majorée après l'âge du taux plein, puis la garantie du
            # taux acquis au 31 mars 1983 : la Cnav compare « une pension au
            # taux de 50 % avec la durée d'assurance au régime général
            # corrigée, et une pension au taux supérieur à 50 % déterminé en
            # fonction de l'âge de l'assuré au 31 mars 1983 avec la durée
            # d'assurance au régime général non corrigée » (circulaire
            # n° 8/89, point 21), et sert la plus forte.
            majores = duree_majoree_apres_taux_plein(
                moteur, periode, carriere, durees, membres, trimestres_regime,
                proratisation, age_annulation)
            acquis = taux_acquis_au_31_mars_1983(moteur, periode, carriere)
            if acquis is not None and acquis * trimestres_regime > taux * majores:
                coefficient_surcote = acquis / (periode.taux_plein or 0.5)
                taux = acquis
            elif majores > trimestres_regime:
                duree_non_majoree = trimestres_regime
                trimestres_regime = majores
            # La surcote ne récompense que les trimestres COTISÉS APRÈS
            # l'âge légal ET au-delà de la durée requise. Les compter tous
            # majorait la pension de qui a commencé tôt sans jamais
            # travailler au-delà de l'âge d'ouverture. Celle du fonctionnaire
            # ne lit pas les bonifications des emplois classés (L. 14, III).
            supplementaires = max(0, trimestres - requis - (
                durees.duree_hors_surcote
                if moteur.catalogue[code].famille == "fonction_publique" else 0))
            # La surcote se compte depuis l'âge légal DE DROIT COMMUN, même
            # pour un emploi classé, et le militaire n'en a aucune : le III
            # de l'article L. 14 ne la donne qu'au « fonctionnaire civil ».
            age_ouverture = ouvrir.age_surcote(moteur, periode, carriere)
            if (periode.surcote_par_trimestre and supplementaires > 0
                    and age_liquidation >= age_ouverture
                    and ouvrir.droit_militaire(moteur, periode, carriere) is None):
                if periode.surcote_bareme:
                    # Barème DATÉ : chaque trimestre civil de surcote au
                    # taux en vigueur quand il a été accompli, depuis le
                    # trimestre qui suit l'âge légal (D. 351-1-4).
                    coefficient_surcote, fiabilite_surcote = (
                        coefficient_surcote_datee(moteur, 
                            periode, carriere, trimestres, requis,
                            supplementaires, age_ouverture,
                        )
                    )
                    if fiabilite_surcote is not None:
                        fiabilite_globale = min(fiabilite_globale, fiabilite_surcote)
                else:
                    if periode.bareme_decote in _BAREMES_REGIMES_SPECIAUX:
                        supplementaires = trimestres_de_surcote_regimes_speciaux(
                            carriere, trimestres, requis, age_ouverture)
                    else:
                        supplementaires = min(
                            supplementaires,
                            _trimestres_cotises_apres(
                                carriere, age_ouverture, annee_liquidation
                            ),
                        )
                    if supplementaires > 0:
                        coefficient_surcote = (
                            1.0 + periode.surcote_par_trimestre * supplementaires
                        )
                taux *= coefficient_surcote

        taux_retenu = max(taux_retenu, taux)
        prorata = min(trimestres_regime / proratisation, rapport_maximum)
        montant = salaire_reference * taux * prorata
        #: Le taux plein, que le minimum contributif et les majorations de la
        #: fraction d'avant 1998 des cultes demandent : durée requise, ou âge
        #: d'annulation de la décote, ou inaptitude. Lu pour eux seuls.
        taux_plein_du_regime = (
            (durees_cultes is not None
             or "minimum_contributif" in periode.avantages_non_contributifs)
            and (trimestres >= requis
                 or age_liquidation >= ouvrir.age_taux_plein(moteur, periode, carriere)
                 or invalidite.taux_plein_de_l_inapte(
                     moteur, code, carriere, age_liquidation)
                 or code in regimes_du_handicap)
        )
        fraction_cultes = (
            cultes.fraction_d_avant_1998(
                moteur, carriere, durees_cultes, proratisation, taux_plein_du_regime,
                facteur_decote, coefficient_surcote, ouverture.trimestres_cotises,
                majorations_des_cultes)
            if durees_cultes is not None else None
        )
        #: La fraction d'après 1997 seule, que le détail dit avant l'autre.
        montant_apres_1997 = montant
        #: Ce que la surcote ajoute à la pension, en euros : le plafond de L. 18
        #: la laisse hors de la pension qu'il compare au traitement.
        surcote_du_montant = max(0.0, montant * (1.0 - 1.0 / coefficient_surcote))
        if fraction_cultes is not None:
            montant += fraction_cultes.montant
            fiabilite_globale = min(fiabilite_globale, fraction_cultes.fiabilite)
        #: Ce que la retraite pour invalidité ajoute à la pension : le
        #: plancher de L. 30, la rente viagère de L. 28, le plafond de
        #: L. 30 ter (:func:`~.invalidite.pension_du_fonctionnaire_invalide`).
        detail_invalidite = ""
        if pour_invalidite is not None:
            montant, detail_invalidite = invalidite.pension_du_fonctionnaire_invalide(
                moteur, carriere, pour_invalidite, montant, salaire_reference,
                annee_liquidation)
        # LA MAJORATION DU DÉPART ANTICIPÉ DES ASSURÉS HANDICAPÉS : « la
        # pension est augmentée à proportion d'un nombre égal au tiers du
        # quotient » de la durée cotisée en situation de handicap dans le
        # régime par sa durée d'assurance, limitée au maximum, sans dépasser
        # la pension d'une durée entière (D. 351-1-5, II) ; au fonctionnaire,
        # les services accomplis en situation de handicap sur les services et
        # bonifications admis, sous la pension du pourcentage maximum (R. 33
        # bis ; décret n° 2003-1306, article 24 bis ; décret n° 2004-1056,
        # article 20 bis). Le minimum contributif se compare au montant
        # calculé seul, et la majoration s'y ajoute (circulaire Cnav
        # n° 2026-18, 3.3.3, règle 3) : elle reste hors de ce qu'il relève.
        majoration_handicap = 0.0
        detail_handicap = ""
        if code in regimes_du_handicap and version_du_handicap is not None:
            fonctionnaire = moteur.catalogue[code].famille == invalidite.FONCTION_PUBLIQUE
            en_situation = durees.cumul_plafonne(
                "services" if fonctionnaire else "cotises", membres,
                lambda annee: invalidite.annee_en_situation_de_handicap(carriere, annee))
            coefficient = invalidite.coefficient_de_majoration(
                version_du_handicap, en_situation, trimestres_regime)
            if coefficient > 0:
                entiere = salaire_reference * (periode.taux_plein or 0.5)
                brute = montant * coefficient
                majoration_handicap = max(0.0, min(brute, entiere - montant))
                montant += majoration_handicap
                detail_handicap = (
                    f", majoration des assurés handicapés {coefficient:.2f}"
                    + (" écrêtée à la pension entière"
                       if brute > majoration_handicap + 1e-9 else ""))
        if "minimum_contributif" in periode.avantages_non_contributifs:
            # Le minimum ne relève que les régimes de base qui le portent,
            # et au prorata de la durée acquise DANS CE régime — durée
            # d'assurance pour le montant de base, durée COTISÉE pour la
            # majoration au titre des périodes cotisées.
            #
            # Et il ne relève que les pensions LIQUIDÉES AU TAUX PLEIN
            # (L. 351-10) : durée requise atteinte, ou âge d'annulation de
            # la décote atteint. Le servir à un assuré décoté, comme le
            # faisait ce module, revenait à faire garantir par le système
            # actuel un départ que le droit sanctionne — et gonflait
            # l'étalon de 20 % sur les petites pensions parties tôt.
            # Le minimum se proratise « dans les mêmes conditions que la
            # pension » : c'est donc la durée de proratisation, et non la
            # durée requise, qui fait office ici aussi.
            # Des cultes, seule la fraction d'après 1997 : ses durées, et la
            # fraction d'avant 1998 hors de ce que le minimum relève.
            cotisee_regime = (cumul_plafonne("cotises", membres) if durees_cultes is None
                              else durees_cultes.cotises_depuis_1998)
            cotises_regime = min(cotisee_regime, proratisation)
            duree_regime = (cumul_plafonne("assurance", membres) if durees_cultes is None
                            else durees_cultes.depuis_1998)
            # Les autres régimes de base, que le minimum d'un polypensionné
            # compte depuis 2004 : chacun pour sa durée, « même si [les
            # trimestres] se superposent, et non limités à 4 par an »
            # (exposé de la Cnav « Calcul du minimum contributif »).
            autres_de_base = [
                autre for autre, nombre in durees.trimestres_par_regime.items()
                if autre not in membres and nombre > 0 and autre in moteur.catalogue
                and moteur.catalogue[autre].etage in ("base", "integre")]
            eligibles_minimum.append(EligibleMinimum(
                indice=len(pensions),
                prorata_assurance=prorata,
                prorata_cotise=cotises_regime / proratisation,
                taux_plein=taux_plein_du_regime,
                surcote=coefficient_surcote,
                duree_regime=duree_regime,
                cotisee_regime=cotisee_regime,
                proratisation=proratisation,
                requis=requis,
                hors_minimum=((0.0 if fraction_cultes is None else fraction_cultes.montant)
                              + majoration_handicap),
                duree_tous_regimes=duree_regime + somme_ordonnee(
                    durees.trimestres_par_regime[autre] for autre in autres_de_base),
                cotisee_tous_regimes=cotisee_regime + somme_ordonnee(
                    cumul_plafonne("cotises", (autre,)) for autre in autres_de_base),
                porte_avpf="regime_general" in membres,
            ))
        if "minimum_garanti" in periode.avantages_non_contributifs:
            # Depuis la loi du 9 novembre 2010, le minimum garanti n'est dû
            # qu'au taux plein — décote nulle, ou durée requise atteinte.
            # Les assurés qui atteignaient l'âge d'ouverture de leurs
            # droits avant 2011 gardent le droit inconditionnel, et le c
            # de L. 17 sous quinze ans de services ; les autres ont le d,
            # que la même loi a créé (voir `MinimumGaranti.montant`). Le
            # parent de trois enfants qui garde l'ancien calcul garde aussi
            # l'ancien L. 17 (article 44, IV, de la loi) ; l'âge qui compte
            # pour les autres est celui d'avant son départ anticipé.
            age_ouverture = ouvrir.age_ouverture(moteur, periode, carriere,
                                                 parents_compris=False)
            parent = ouvrir.depart_parent_trois_enfants(moteur, periode, carriere)
            ancien_droit = (carriere.annee_naissance + age_ouverture < 2011
                            or (parent is not None and parent.ancien_calcul))
            # L'âge qui ouvre le minimum sans la durée est l'âge
            # d'annulation de la décote, MINORÉ à titre transitoire selon
            # l'année où l'âge d'ouverture est atteint (IV de l'article 45
            # de la loi, article 3 du décret n° 2010-1744) : le modèle le
            # refusait neuf trimestres trop longtemps à qui ouvrait ses
            # droits en 2011.
            fonction_publique = moteur.catalogue[code].famille == "fonction_publique"
            minoration = MINORATION_AGE_MINIMUM_GARANTI.get(
                carriere.mois_de_l_anniversaire(age_ouverture).annee, 0
            ) if fonction_publique else 0
            # Le minimum compte les SERVICES EFFECTIFS, sans les bonifications
            # (L. 17), arrondis au décompte final (CNRACL, « Les modalités de
            # calcul ») ; avant 2004, le décompte de la pension.
            eligibles_garanti.append(EligibleMinimumGaranti(
                indice=len(pensions),
                trimestres_services=(
                    durees.services_effectifs(membres)
                    if au_jour and durees.decompte["parametres"]["minimum_garanti"]
                    == "services_effectifs"
                    else numerateur if au_jour
                    else cumul_plafonne("services", membres)),
                # La pension liquidée pour invalidité a le minimum garanti
                # sans condition de taux plein (« pour les motifs prévus aux
                # 2° à 5° du I de l'article L. 24 »), et le c de L. 17 sous
                # quinze ans, en quinzièmes.
                ouvert=(
                    pour_invalidite is not None
                    or ancien_droit
                    or trimestres_decote <= 0
                    or trimestres + majorations_emplois + ecart_au_jour >= requis - 1e-9
                    or (minoration > 0 and age_annulation is not None
                        and age_liquidation + 1e-9
                        >= age_annulation - minoration / 4.0)
                ),
                # Le d et la minoration ne valent que pour la fonction
                # publique : la Banque de France a les siens depuis son
                # décret de 2012, que sa fiche ne date pas.
                duree_maximum=(
                    proratisation
                    if fonction_publique and not ancien_droit and pour_invalidite is None
                    else None
                ),
            ))
        if (code in coordonner.REGIMES_CODE_DES_PENSIONS
                and periode.pension_forfaitaire_annuelle is None):
            # LE PLAFOND DE L. 18 : la pension majorée pour enfants ne peut
            # excéder le traitement ou la solde qui l'a liquidée. L'étape qui
            # complète lit ce traitement, et ce que la surcote ajoute à la
            # pension, que la retraite pour invalidité a pu relever.
            eligibles_plafond.append(EligiblePlafondEnfants(
                indice=len(pensions), traitement=salaire_reference,
                surcote=min(surcote_du_montant, montant)))
        detail = (
                f"{'forfait' if periode.pension_forfaitaire_annuelle is not None else 'SR'} "
                # Salaire de référence au centime et taux au millième : à
                # l'euro et au centième, refaire « SR × taux × durée »
                # ratait le montant de 1,20 € sur un régime spécial, le
                # taux arrondi pesant à lui seul 0,89 €.
                f"{salaire_reference:,.2f} € × taux {taux:.3%} "
                f"× {trimestres_regime}/{proratisation}"
                + (f", taux maximum {periode.taux_maximum_bonifie:.0%} atteint"
                   if trimestres_regime / proratisation > rapport_maximum else "")
                + ("" if duree_non_majoree is None else
                   f", {duree_non_majoree} trimestres majorés après l'âge du taux plein")
                + ("" if pour_invalidite is None else
                   ", retraite pour invalidité"
                   + (f" : {detail_invalidite}" if detail_invalidite else ""))
                + detail_handicap
                + ("" if annees_alignees is None else
                   f", {annees_alignees[0]} années au plus au salaire annuel moyen "
                   f"({annees_alignees[1]})")
                # La succession est DITE : sans elle, le lecteur cherche
                # la ligne de la CANCAVA et ne la trouve pas.
                + ("" if len(membres) == 1 else
                   f", {len(membres)} caisses liquidées ensemble "
                   f"({', '.join(membres[1:])} puis {membres[0]})")
        )
        if fraction_cultes is not None:
            # Les deux fractions des cultes, chacune avec son montant ; avant
            # 1998, la seule qui existe.
            detail = (
                f"{fraction_cultes.detail} = {fraction_cultes.montant:,.2f} €"
                if annee_liquidation < cultes.ALIGNEMENT
                else (f"{detail} = {montant_apres_1997:,.2f} € ; "
                      f"{fraction_cultes.detail} = {fraction_cultes.montant:,.2f} €")
            )
        pensions.append(PensionRegime(
            regime=code, montant=montant, type_calcul="annuites",
            detail=detail,
            fiabilite=min(moteur.catalogue[m].fiabilite for m in membres),
        ))

    return Pensions(
        personne=carriere.personne,
        regimes=tuple(pensions),
        minimum=tuple(eligibles_minimum),
        garanti=tuple(eligibles_garanti),
        requis=trimestres_requis,
        taux=taux_retenu,
        fiabilite=fiabilite_globale,
        agricole=agricole,
        plafonds=tuple(eligibles_plafond),
    )


def eligible_agricole(moteur, periode: PeriodeRegime, carriere: Carriere, releve: Releve,
                      membres: tuple[str, ...], trimestres: int, age_liquidation: float,
                      indice: int, coefficient: float, par_le_handicap: bool
                      ) -> EligibleAgricole:
    """Ce que la pension majorée de référence et le complément différentiel de
    la RCO lisent de la pension de base des non-salariés agricoles.

    Le TAUX PLEIN est celui du minimum contributif : la durée requise tous
    régimes, l'âge du taux plein, l'inaptitude ou le handicap (L. 732-54-1,
    3°, depuis février 2014 ; D. 732-109, 3°, a) avant). La DURÉE est celle
    des périodes cotisées ou assimilées pour la retraite forfaitaire, année par
    année ; les trimestres pour enfants n'y entrent que depuis 2026, et la
    règle les ajoute (D. 732-110). La DURÉE DE RÉFÉRENCE est celle de la
    retraite forfaitaire, que le modèle lit comme le forfait la lit, au moins
    trente-sept ans et demi. ``coefficient`` est celui de la décote ou de la
    surcote du régime ; seule la surcote est retirée avant de comparer à la
    PMR."""
    durees = releve.durees
    code = membres[0]
    requis, _ = ouvrir.duree_requise(moteur, periode, carriere)
    proratisation, _ = duree_proratisation(moteur, periode, carriere, requis)
    annees = durees.cumul_plafonne("assurance", membres, lambda annee: True)
    toutes = durees.cumul_plafonne("assurance", membres)
    return EligibleAgricole(
        indice=indice,
        taux_plein=(trimestres >= requis
                    or age_liquidation >= ouvrir.age_taux_plein(moteur, periode, carriere)
                    or invalidite.taux_plein_de_l_inapte(moteur, code, carriere,
                                                         age_liquidation)
                    or par_le_handicap),
        duree_requise_atteinte=trimestres >= requis,
        surcote=max(1.0, coefficient),
        duree=annees,
        enfants=max(0, toutes - annees),
        reference=max(150, proratisation),
    )


def repartir_les_annees(nombre: int, durees: dict[str, int],
                        minimums: dict[str, int] | None = None,
                        priorite: tuple[str, ...] = ()) -> dict[str, int]:
    """``nombre`` années réparties au prorata des ``durees`` (R. 173-3-2, II).

    « Les nombres d'années obtenus sont arrondis à chaque étape à l'entier
    non nul le plus proche, la fraction d'année égale à 0,5 étant comptée
    pour une année » ; quand leur total dépasse le nombre à répartir, « la ou
    les années surnuméraires sont retranchées au régime [...] pour lequel [...]
    la durée d'assurance [...] est la plus longue », et, à égalité, dans
    l'ordre de ``priorite``. Un total inférieur reste tel : le texte n'en dit
    rien. Les ``minimums`` sont ceux d'une première répartition, qu'une
    seconde partagera : autant d'années que de sous-périodes.

    Les durées sont des trimestres, entiers : l'arrondi se fait en entiers,
    sans flottant.
    """
    minimums = minimums or {}
    presentes = {cle: duree for cle, duree in durees.items() if duree > 0}
    total = somme_ordonnee(presentes.values())
    if total <= 0 or nombre <= 0:
        return {}
    parts = {
        cle: max(1, minimums.get(cle, 1),
                 (2 * nombre * duree + total) // (2 * total))
        for cle, duree in presentes.items()
    }
    rang = {cle: i for i, cle in enumerate(priorite)}
    excedent = somme_ordonnee(parts.values()) - nombre
    for cle in sorted(presentes,
                      key=lambda c: (-presentes[c], rang.get(c, len(rang)))):
        if excedent <= 0:
            break
        retire = min(excedent, parts[cle] - max(1, minimums.get(cle, 1)))
        if retire > 0:
            parts[cle] -= retire
            excedent -= retire
    return parts


def durees_des_non_salaries(carriere: Carriere, durees,
                            code: str) -> tuple[int, int, int]:
    """Les durées des trois parts de L. 732-24 : celle du 1°, depuis 2016,
    celle du a et celle du b, d'avant 2016.

    Les majorations de durée comptent pour le 1°, ou pour le a de qui n'a été
    affilié qu'avant 2016 ; les trimestres des enfants, « en outre », pour le b
    (R. 732-61 ; R. 732-66, III).
    """
    coupure = ANNEE_DES_REVENUS_AGRICOLES
    par_annee = durees.par_annee["assurance"].get(code, {})
    avant = somme_ordonnee(min(n, carriere.plafond_trimestres(annee))
                for annee, n in par_annee.items() if annee < coupure)
    apres = somme_ordonnee(min(n, carriere.plafond_trimestres(annee))
                for annee, n in par_annee.items() if annee >= coupure)
    enfants = durees.hors_annee["assurance"].get(code, 0)
    return (apres + enfants if apres > 0 else 0,
            avant + (enfants if apres == 0 else 0),
            avant + enfants if avant > 0 else 0)


def premiere_repartition(moteur, carriere: Carriere, releve: Releve, code: str,
                         total: int, duree_b: int, duree_1: int) -> dict[str, int]:
    """La première répartition de R. 173-3-2 : ``total`` années entre les
    régimes alignés, ensemble (clé ``alignes``), et celui des non-salariés
    agricoles (clé ``code``), au prorata de leurs durées.

    Chacun reçoit au moins autant d'années que la seconde répartition en
    partagera : les deux périodes du régime agricole, et, pour qui est né avant
    1953, chacun des régimes alignés.
    """
    durees = releve.durees
    alignes = tuple(autre for autre in durees.trimestres_par_regime
                    if autre in coordonner.REGIMES_ALIGNES)
    groupes_alignes = {coordonner.tete_de_succession(moteur, autre, carriere.annee_liquidation)
                       for autre in alignes}
    return repartir_les_annees(
        total,
        {"alignes": durees.cumul_plafonne("assurance", alignes) if alignes else 0,
         code: durees.trimestres_par_regime.get(code, 0)},
        minimums={
            "alignes": (1 if carriere.generation >= coordonner.LURA_PREMIERE_GENERATION
                        else len(groupes_alignes)),
            code: (1 if duree_b > 0 else 0) + (1 if duree_1 > 0 else 0),
        },
        priorite=(code, "alignes"),
    )


def duree_du_regime_aligne(carriere: Carriere, durees,
                           membres: tuple[str, ...]) -> int:
    """La durée d'un régime aligné que les répartitions comparent : ses
    trimestres année par année, bornés aux trimestres civils de l'année, plus
    ceux des enfants ; pour les artisans et les commerçants, les seules années
    alignées, depuis 1973 (circulaire Cnav n° 2004/29, point 2122)."""
    sommes: dict[int, int] = {}
    for membre in membres:
        for annee, n in durees.par_annee["assurance"].get(membre, {}).items():
            if (membre in coordonner.REGIMES_DES_ARTISANS_ET_COMMERCANTS
                    and annee < coordonner.ALIGNEMENT_DES_ARTISANS_ET_COMMERCANTS):
                continue
            sommes[annee] = sommes.get(annee, 0) + n
    return (somme_ordonnee(min(somme, carriere.plafond_trimestres(annee))
                for annee, somme in sommes.items())
            + somme_ordonnee(durees.hors_annee["assurance"].get(membre, 0) for membre in membres))


def annees_au_prorata(total: int, duree: int, somme: int) -> int:
    """R. 173-4-3 : ``total`` années au prorata de ``duree`` sur ``somme``,
    « arrondi, pour chaque régime, au nombre d'années le plus proche sans que ce
    nombre puisse être inférieur à 1. La fraction d'année égale à 0,5 est
    comptée pour une année », et sans dépasser ``total``. En entiers."""
    if somme <= 0:
        return total
    return min(total, max(1, (2 * total * duree + somme) // (2 * somme)))


def trimestres_etrangers_au_salaire_moyen(moteur, carriere: Carriere, durees,
                                          famille: str | None) -> int:
    """Les trimestres des régimes étrangers « équivalant au régime général »
    qui réduisent, avec la durée des régimes alignés, les années du salaire
    annuel moyen de la pension proratisée (fiche ``pension_proratisee``) : de
    2004 à juin 2022, « réduites au prorata » ; depuis, hors de la liquidation
    unique seulement (circulaire Cnav n° 2021/33, points 3 et 4). Aucun
    ailleurs, ni pour la pension nationale, qui ne compte pas l'étranger."""
    etranger = durees.etranger
    effet = date_d_effet(carriere)
    if etranger is None or effet is None or famille is None:
        return 0
    version = moteur.carrieres_hors_de_france.version("proratisation", {
        "liquidation.date_effet": effet,
        "assure.generation": f"{carriere.annee_naissance:04d}-01-01"})
    regle = None if version is None else version["parametres"].get(
        "annees_du_salaire_annuel_moyen")
    if regle == "reduites_au_prorata" or (
            regle == "entieres_sous_la_liquidation_unique"
            and not coordonner.lura_applicable(carriere)):
        return etranger.trimestres_au_salaire_moyen(famille)
    return 0


def annees_des_regimes_alignes(moteur, carriere: Carriere, releve: Releve,
                               membres: tuple[str, ...],
                               total: int, etrangers: int = 0) -> tuple[int, str] | None:
    """Le nombre d'années que retient le salaire annuel moyen d'un régime
    aligné quand d'autres régimes les partagent, et l'article qui le dit ; ou
    ``None`` si rien ne les partage.

    **Entre régimes alignés, depuis 2004** : « le nombre d'années retenu pour
    calculer ce salaire ou revenu est déterminé [...] en multipliant le nombre
    d'années fixé dans le régime considéré [...] par le rapport entre la durée
    d'assurance accomplie au sein de ce régime et le total des durées
    d'assurance accomplies dans les régimes susvisés », arrondi au plus proche
    sans descendre sous un ni dépasser le nombre de départ (R. 173-4-3). Le
    régime général, les salariés agricoles et les artisans et commerçants — le
    RSI depuis 2006 — que la liquidation unique ne réunit pas : l'assuré né
    avant 1953, ou parti avant le 1er juillet 2017. Un assuré né en 1944, avec
    126 trimestres au régime général et 48 chez les artisans, retient 15
    années sur 21 (circulaire Cnav n° 2004/29).

    **Avec les exploitants agricoles, depuis 2026** : le nombre d'années « fait
    l'objet d'une répartition au prorata des durées d'assurance » entre
    l'ensemble des régimes alignés et celui des non-salariés agricoles, puis,
    pour qui est né avant 1953, entre chacun des régimes alignés, les
    nombres « arrondis à chaque étape à l'entier non nul le plus proche », les
    années surnuméraires retranchées à la plus longue durée (R. 173-3-2, II) :
    six sur vingt-cinq, dans l'exemple de la MSA, pour dix années de salarié
    agricole contre trente-trois d'exploitant. La répartition vaut où vaut la
    réforme agricole : la période du régime des exploitants qui la porte le dit.

    **Avec les régimes étrangers équivalents, pour la pension proratisée** :
    « Prorata = durée d'assurance au régime général ÷ durée totale des régimes
    retenus », les régimes alignés et les ``etrangers`` trimestres des régimes
    étrangers « équivalant au régime général »
    (:func:`trimestres_etrangers_au_salaire_moyen`) : 66 trimestres au régime
    général, 20 en Belgique et 74 en Allemagne retiennent « 25 meilleures
    années x 66/160ème = 10 » (circulaire ministérielle DSS/3A/DACI/2008/219
    du 3 juillet 2008, exemple 2). La liquidation unique réunit les régimes
    alignés en un seul, face aux périodes étrangères. Avec les exploitants, la
    part des régimes alignés s'y répartit de même.
    """
    if coordonner.REGIMES_ALIGNES.isdisjoint(membres):
        return None
    durees = releve.durees
    exploitants = coordonner.REGIME_DES_NON_SALARIES_AGRICOLES
    periode = (moteur.catalogue[exploitants].periode(carriere.annee_liquidation)
               if exploitants in moteur.catalogue else None)
    reforme = periode is not None and periode.meilleures_annees_non_salaries
    part: int | None = total
    article: str | None = None
    if reforme and durees.trimestres_par_regime.get(exploitants, 0) > 0:
        duree_1, _, duree_b = durees_des_non_salaries(carriere, durees, exploitants)
        part = premiere_repartition(
            moteur, carriere, releve, exploitants, total, duree_b, duree_1).get("alignes")
        if part is None:
            return None
        article = "R. 173-3-2"
    # Chaque régime aligné sa part, hors de la liquidation unique ; et face
    # aux régimes étrangers équivalents.
    lura = coordonner.lura_applicable(carriere)
    if etrangers or (not lura and carriere.date_liquidation.rang
                     >= coordonner.REPARTITION_ENTRE_REGIMES_ALIGNES_DEPUIS.rang):
        propre = coordonner.tete_de_succession(
            moteur, membres[0], carriere.annee_liquidation)
        if lura:
            durees_des_groupes = {propre: duree_du_regime_aligne(carriere, durees, membres)}
        else:
            # Un régime, et non un nom de caisse : la CANCAVA et le RSI qui
            # lui succède sont un seul régime, par leur tête de succession,
            # que la liquidation les réunisse ou non.
            groupes: dict[str, list[str]] = {}
            for autre in durees.trimestres_par_regime:
                if autre in coordonner.REGIMES_ALIGNES:
                    groupes.setdefault(coordonner.tete_de_succession(
                        moteur, autre, carriere.annee_liquidation), []).append(autre)
            durees_des_groupes = {
                tete: duree for tete, duree in (
                    (tete, duree_du_regime_aligne(carriere, durees, tuple(groupe)))
                    for tete, groupe in groupes.items())
                if duree > 0}
        if propre in durees_des_groupes and (len(durees_des_groupes) >= 2 or etrangers):
            if reforme and not etrangers:
                return (repartir_les_annees(
                    part, durees_des_groupes,
                    priorite=("regime_general", "msa_salaries"),
                )[propre], "R. 173-3-2")
            return (annees_au_prorata(part, durees_des_groupes[propre],
                                      somme_ordonnee(durees_des_groupes.values()) + etrangers),
                    "R. 173-4-3, périodes étrangères comprises" if etrangers
                    else "R. 173-4-3")
    return None if article is None else (part, article)


def moyenne_des_meilleures_annees(valeurs: list[float], annees: int) -> int:
    """La moyenne des ``annees`` meilleures valeurs, toutes s'il y en a moins.

    « Le nombre de points annuel moyen ainsi obtenu est arrondi à l'entier le
    plus proche. La fraction égale à 0,5 est comptée pour un point » (R. 732-66,
    II).
    """
    meilleures = sorted(valeurs, reverse=True)[:max(0, annees)]
    if not meilleures:
        return 0
    return math.floor(somme_ordonnee(meilleures) / len(meilleures) + 0.5 + 1e-9)


def pension_des_non_salaries_agricoles(
        moteur, periode: PeriodeRegime, carriere: Carriere, releve: Releve,
        code: str, trimestres: int, requis_reference: int,
        age_liquidation: float, annee_liquidation: int,
        ignorer_penalite_age: bool) -> PensionRegime:
    """La pension des non-salariés agricoles depuis le 1er janvier 2026.

    **L. 732-24 dans sa rédaction de 2026** (loi n° 2025-199, article 87) :
    pour qui a été affilié avant 2016, la pension « cumule »

    * 1° un montant calculé comme au régime général « sur les bases des seuls
      revenus des années à compter du 1er janvier 2016 » — le revenu annuel
      moyen de leurs meilleures années, au taux plein, au prorata de la
      durée depuis 2016 (L. 732-18) ;
    * 2° a) la retraite forfaitaire, 3 905,37 € au 1er janvier 2025
      (D. 732-62), au prorata de la seule durée d'avant 2016 ;
    * 2° b) la moyenne des points des années d'avant 2016 « dont la prise en
      considération est la plus avantageuse », arrondie à l'entier,
      multipliée par le quart des trimestres d'avant 2016, par la valeur du
      point et par cent cinquante sur la durée de la génération (R. 732-66).

    Les deux moyennes portent sur la part des vingt-cinq années que
    R. 173-3-2 donne à leur période : une première répartition entre les
    régimes alignés et celui-ci, au prorata de leurs durées, puis une
    seconde entre les périodes d'avant et d'après 2016. La minoration de
    R. 351-27 multiplie les trois parts (L. 732-24, II ; R. 732-68), la
    pension ne dépasse pas la moitié du plafond (III), et la surcote du
    régime général la majore. Pour qui n'a été affilié qu'à partir de 2016,
    le 1° seul.

    **Les années sans barème de points** — celles d'avant 1990, que le moteur
    valorise au rendement faute d'en avoir lu le barème — entrent dans la
    moyenne pour les points que vaut leur rendement.

    **Les pensions de 2026 et de 2027** (``calcul_provisoire_non_salaries``)
    sont d'abord liquidées par l'ancienne section : le forfait sur toute la
    durée, et les points de 2016 à 2027 un à un, ceux d'avant 2016 par la même
    moyenne (loi n° 2025-199, article 87, VIII, B). Le nouveau calcul, fait
    au plus tard le 31 mars 2028, les révise s'il leur est plus favorable :
    la plus forte des deux est servie.
    """
    durees, droits = releve.durees, releve.droits
    regime = moteur.catalogue[code]
    fiabilite = regime.fiabilite
    requis, fiabilite_duree = ouvrir.duree_requise(moteur, periode, carriere)
    proratisation, fiabilite_prorata = duree_proratisation(
        moteur, periode, carriere, requis)
    for lue in (fiabilite_duree, fiabilite_prorata,
                droits.fiabilite_points.get(code)):
        if lue is not None:
            fiabilite = min(fiabilite, lue)
    coupure = ANNEE_DES_REVENUS_AGRICOLES

    duree_1, duree_a, duree_b = durees_des_non_salaries(carriere, durees, code)

    # LE NOMBRE D'ANNÉES DE CHAQUE MOYENNE (R. 173-3-2). Les régimes alignés
    # d'abord, contre celui-ci, chacun pour sa durée ; puis les deux périodes
    # de celui-ci, pour les durées du b et du 1°.
    enfants_majores = carriere.nombre_enfants if durees.enfants is not None else 0
    total = nombre_d_annees_retenues(
        moteur, periode, carriere, carriere.annee_naissance, enfants_majores)
    premiere = premiere_repartition(moteur, carriere, releve, code, total, duree_b, duree_1)
    seconde = repartir_les_annees(
        premiere.get(code, 0), {"avant": duree_b, "apres": duree_1},
        priorite=("avant", "apres"),
    )
    annees_avant, annees_apres = seconde.get("avant", 0), seconde.get("apres", 0)

    # 2° b) LES POINTS D'AVANT 2016, par la moyenne de leurs meilleures
    # années. Une année sans barème y entre pour les points que vaut son
    # rendement, à la valeur de service de la liquidation.
    valeur = valeur_point_fiche(moteur, periode, annee_liquidation)
    coefficient_duree = 150.0 / requis if requis > 0 else 1.0
    service = valeur * coefficient_duree
    points_par_annee: dict[int, float] = {}
    for regime_du_credit, annee, points, _ in droits.points:
        if regime_du_credit == code:
            points_par_annee[annee] = points_par_annee.get(annee, 0.0) + points
    rendement: float | None = None
    for regime_du_credit, annee, cotisation in droits.cotisations:
        if regime_du_credit != code or annee >= coupure or service <= 0:
            continue
        if rendement is None:
            rendement, fiabilite_rendement = moteur.rendements.rendement(
                periode.points_de or code,
                min(annee_liquidation, derniere_annee(regime)),
            )
            fiabilite = min(fiabilite, fiabilite_rendement)
        points_par_annee[annee] = (points_par_annee.get(annee, 0.0)
                                   + cotisation * rendement / service)
    points_avant = [points for annee, points in points_par_annee.items()
                    if annee < coupure]
    retenues = min(annees_avant, len(points_avant))
    moyenne = (moyenne_des_meilleures_annees(points_avant, annees_avant)
               if duree_b > 0 else 0)
    points_b = moyenne * duree_b / 4.0
    part_b = points_b * service

    # 2° a) LA RETRAITE FORFAITAIRE, au prorata de la durée d'avant 2016.
    forfait = (
        (periode.pension_forfaitaire_annuelle or 0.0)
        * moteur.macro.coefficient_prix(
            periode.pension_forfaitaire_annee or annee_liquidation,
            annee_liquidation,
        )
    )
    retenue_a = min(duree_a, proratisation)
    part_a = forfait * retenue_a / proratisation if proratisation > 0 else 0.0

    # 1° LE REVENU ANNUEL MOYEN DEPUIS 2016, au taux plein du régime général
    # et au prorata de la durée depuis 2016 (L. 732-18, L. 351-1).
    taux = (moteur.catalogue["regime_general"].periode(annee_liquidation).taux_plein
            or 0.5)
    retenue_1 = min(duree_1, proratisation)
    revenu_moyen = (
        salaire_de_reference(
            moteur, code, carriere, periode, annee_liquidation, True,
            carriere.annee_naissance, avpf=False, membres=(code,),
            depuis=coupure, annees=annees_apres, plancher=True,
        )
        if retenue_1 > 0 and annees_apres > 0 else 0.0
    )
    part_1 = (revenu_moyen * taux * retenue_1 / proratisation
              if proratisation > 0 else 0.0)

    coefficient = 1.0
    if not ignorer_penalite_age:
        coefficient = abattement_points(
            moteur, periode, carriere, trimestres, requis_reference,
            age_liquidation, annee_liquidation,
            durees.trimestres_par_regime.get(code, 0),
        )
    minoration, majoration = min(coefficient, 1.0), max(coefficient, 1.0)

    termes = []
    if part_1 > 0:
        termes.append(
            f"revenu annuel moyen {revenu_moyen:,.2f} € × taux {taux:.3%} "
            f"× {retenue_1}/{proratisation}")
    if part_a > 0:
        termes.append(f"forfait {part_a:,.2f} € ({retenue_a}/{proratisation})")
    if part_b > 0:
        # Le rapport de cent cinquante à la durée, à six décimales comme la
        # valeur du point : à quatre, 150/170 écrit 0,8824, et la formule
        # manquait le montant de soixante-dix centimes.
        termes.append(
            f"{points_b:,.2f} points × valeur de service "
            f"{_sans_zeros_inutiles(valeur, 6)} € × "
            f"{_sans_zeros_inutiles(coefficient_duree, 6)}")
    brut = (part_1 + part_a + part_b) * minoration
    plafond = 0.5 * moteur.macro.plafond_securite_sociale(annee_liquidation)
    if brut > plafond:
        montant = plafond * majoration
        detail = (
            f"moitié du plafond {plafond:,.2f} €"
            + ("" if majoration == 1.0
               else f" × coefficient de majoration {majoration:.4f}")
            + f" (L. 732-24, III), au lieu de {_formule_points(termes, minoration)}"
        )
    else:
        montant = brut * majoration
        detail = _formule_points(termes, coefficient)
    explications = []
    if part_b > 0:
        explications.append(
            f"{moyenne} points par an, moyenne arrondie des {retenues} "
            f"meilleures années d'avant 2016, sur {duree_b} trimestres")
    if part_1 > 0:
        explications.append(
            f"revenu des {annees_apres} meilleures années depuis 2016")

    if periode.calcul_provisoire_non_salaries:
        # LE CALCUL PROVISOIRE de 2026 et 2027 : le forfait sur toute la
        # durée, et les points d'après 2016 un à un.
        retenue = min(durees.trimestres_par_regime.get(code, 0), proratisation)
        forfait_total = forfait * retenue / proratisation if proratisation > 0 else 0.0
        points_provisoires = points_b + somme_ordonnee(
            points for annee, points in points_par_annee.items() if annee >= coupure)
        termes_provisoires = []
        if points_provisoires > 0:
            termes_provisoires.append(
                f"{points_provisoires:,.2f} points × valeur de service "
                f"{_sans_zeros_inutiles(valeur, 6)} € × "
                f"{_sans_zeros_inutiles(coefficient_duree, 6)}")
        if forfait_total > 0:
            termes_provisoires.append(
                f"forfait {forfait_total:,.2f} € ({retenue}/{proratisation})")
        provisoire = (points_provisoires * service + forfait_total) * coefficient
        if provisoire > montant:
            explications = (
                [f"dont {points_b:,.2f} points d'avant 2016, {moyenne} par an, "
                 f"moyenne arrondie des {retenues} meilleures années"]
                if part_b > 0 else [])
            explications.append(
                f"calcul provisoire de 2026 et 2027, que le recalcul de 2028 "
                f"ne dépasse pas ({montant:,.2f} €)")
            montant = provisoire
            detail = _formule_points(termes_provisoires, coefficient)
        else:
            explications.append(
                f"recalcul de 2028, plus fort que le calcul provisoire de 2026 "
                f"et 2027 ({provisoire:,.2f} €)")
    if explications:
        detail += " ; " + " ; ".join(explications)
    return PensionRegime(
        regime=code, montant=montant, type_calcul=periode.type_calcul,
        detail=detail, fiabilite=fiabilite,
    )


def _annee_et_mois(quand: int | DateMois | date) -> tuple[int, int]:
    """Une année se lit au 31 décembre, une date au 1er de son mois."""
    if isinstance(quand, int):
        return quand, 12
    if isinstance(quand, DateMois):
        return quand.annee, quand.mois
    return quand.year, quand.month


def valeur_du_point(moteur, code: str,
                    quand: int | DateMois | date) -> tuple[float, Fiabilite] | None:
    """Ce que vaut, au jour ``quand``, un point acquis dans ``code``.

    ``quand`` est la date d'effet d'une pension — un :class:`DateMois`, ou une
    :class:`~datetime.date` lue au 1er de son mois — ou une année, lue au 31
    décembre. LA LIQUIDATION SERT LA VALEUR DU JOUR : « la valeur de service du
    point de retraite du régime à cette même date » (circulaire Agirc-Arrco
    2020-02-DRJ, sur l'article 92 de l'accord du 17 novembre 2017), que
    :meth:`~retraite_notionnelle.scenarios.actuel.ValeursPoint.service_au`
    lit. Lire l'année donnait à un départ de janvier 2022 la valeur de
    novembre, 1,3498 € au lieu de 1,2841 €.

    Un régime fermé ne sert plus ses points : ils ont été convertis dans son
    successeur, au coefficient que l'accord de fusion a fixé. La méthode
    remonte la chaîne des successions (UNIRS -> Arrco -> Agirc-Arrco,
    Agirc -> Agirc-Arrco, IPACTE et IGRANTE -> Ircantec) en cumulant ces
    coefficients, qui sont LUS dans ``regimes/conversions_points.csv`` et
    non plus déduits d'un rapport de valeurs de service.

    **Les déduire coûtait cher.** Le rapport était pris entre la dernière
    valeur publiée du régime d'origine et la PREMIÈRE du successeur ; or les
    séries ``arrco`` et ``ircantec`` sont rétro-remplies bien avant leur
    fusion, si bien qu'on comparait deux valeurs distantes de quarante ou
    soixante-dix ans. Le point UNIRS ressortait quinze fois trop cher pour
    toute liquidation postérieure à 1998, le point IPACTE cinquante fois
    trop cher au-delà de 2022. Et là même où les deux bornes tombaient
    juste, la valeur du successeur était celle du 31 décembre quand la
    conversion s'opère au 1er janvier : un pour cent de trop peu sur tous
    les points d'avant 2019.

    Quand la chaîne s'arrête — plus de successeur, ou aucun coefficient
    déclaré — la dernière valeur publiée est ramenée en euros de la
    liquidation par l'indice des prix, pris un an plus tôt comme la
    revalorisation du 1er janvier le prend. C'est une approximation, signalée
    comme telle par la fiabilité renvoyée ; c'est surtout un aveu
    d'ignorance, préférable à un coefficient inventé. L'Agirc-Arrco, dont les
    accords projettent la valeur de service au salaire moyen moins 1,16 %,
    suit depuis le 5 octobre 2026 la convention du COR, que
    ``conventions_points`` porte (action 147, étape 4) ; elle suivait les
    prix, la convention de « Mon estimation retraite », qui compte les points
    à leur valeur actuelle : la fiche ``agirc_arrco_valeur_achat`` garde les
    deux lectures. La valeur prolongée d'une année est celle de son 31
    décembre : un départ antérieur au relèvement de l'année prend celle de
    l'année d'avant (:meth:`~retraite_notionnelle.scenarios.actuel.ValeursPoint.millesime`).
    """
    annee_liquidation, mois = _annee_et_mois(quand)
    conversion = 1.0
    courant = code
    fiabilite = Fiabilite.CERTIFIEE
    for _ in range(len(moteur.catalogue) + 1):  # garde-fou : jamais de boucle
        derniere = moteur.valeurs_point.derniere_annee_servie(courant)
        if derniere is None:
            return None
        if annee_liquidation <= derniere:
            valeur = moteur.valeurs_point.service_au(courant, annee_liquidation, mois)
            if valeur is None:
                # Liquidation antérieure au premier barème publié. Symétrique
                # du cas ci-dessous : la première valeur connue est ramenée
                # en euros de la liquidation par l'indice des prix, et la
                # fiabilité tombe pour le dire.
                premiere_connue = moteur.valeurs_point.premiere_annee_servie(courant)
                ancienne = moteur.valeurs_point.service(courant, premiere_connue)
                return (
                    conversion * ancienne[0]
                    * moteur.macro.coefficient_prix(premiere_connue, annee_liquidation),
                    min(fiabilite, ancienne[1], Fiabilite.MOYENNE),
                )
            return conversion * valeur[0], min(fiabilite, valeur[1])

        successeur = (moteur.catalogue[courant].integre_dans
                      if courant in moteur.catalogue else None)
        reprise = (moteur.conversions_points.fusion(courant, successeur)
                   if successeur else None)
        if reprise is None:
            # AVEC UN AN DE RETARD : une valeur revalorisée au 1er janvier
            # l'est des prix de l'année écoulée (L. 161-25, moyenne des
            # douze derniers indices mensuels). La prolonger par les prix de
            # l'année même donnait à la valeur 2026 du point RCO et de la
            # CNAVPL les +1,75 % de l'hypothèse d'inflation, là où la
            # revalorisation de 2026 est de 0,9 %.
            millesime = moteur.valeurs_point.millesime(courant, annee_liquidation, mois)
            if millesime <= derniere:
                # Avant le relèvement de l'année, la dernière valeur publiée
                # reste celle du jour.
                valeur = moteur.valeurs_point.service(courant, millesime)
                return conversion * valeur[0], min(fiabilite, valeur[1])
            # Ce que le COR suppose de la valeur de l'Agirc-Arrco au-delà du
            # dernier barème — le salaire moyen moins 1,16 point jusqu'en
            # 2037, moins 0,86 ensuite — l'emporte sur les prix
            # (``conventions_points``, ValeursPoint.indice_convenu).
            ancienne = moteur.valeurs_point.service(courant, derniere)
            return (
                conversion * ancienne[0]
                * moteur.valeurs_point.indice_convenu(
                    courant, "valeur_service", derniere, millesime,
                    moteur.macro, ("prix", 1)),
                min(fiabilite, ancienne[1], Fiabilite.MOYENNE),
            )

        conversion *= reprise.coefficient
        fiabilite = min(fiabilite, reprise.fiabilite)
        courant = successeur
    return None  # pragma: no cover - chaîne de successions cyclique


def assiette_de_reference(moteur, periode: PeriodeRegime, ligne) -> float:
    """La rémunération que ce régime liquide : voir la fonction du même
    nom, et, pour un régime à grille, le salaire forfaitaire de la
    catégorie — le marin liquide « sur le salaire forfaitaire de la
    catégorie dans laquelle il a été classé » (R. 11), non sur sa paie.
    Le forfait est proratisé sur les mois de l'année, comme le revenu.

    Une année RÉTABLIE porte au compte le dernier traitement de l'agent,
    non ce qu'il a perçu cette année-là (voir
    :func:`~retraite_notionnelle.droit.coordonner.retablir`).
    """
    if ligne.revenu_retabli > 0 and periode.assiette != "primes_uniquement":
        return ligne.revenu_retabli
    if periode.assiette_grille:
        forfait_grille = moteur.grilles.forfait(
            periode.assiette_grille, ligne.annee, ligne.revenu_annualise,
            lambda a: salaire_moyen_annuel(moteur.macro, a),
        )
        if forfait_grille is not None:
            return forfait_grille[0] * ligne.fraction_annee
    if periode.assiette_forfaitaire:
        # L'ASSIETTE FORFAITAIRE EST AUSSI LE SALAIRE PORTÉ AU COMPTE. Le
        # régime des cultes liquide aux règles du régime général (L. 382-27),
        # dont le salaire annuel moyen est fait des salaires qui ont porté
        # cotisation — ici le forfait de R. 382-89. La CAVIMAC l'écrit :
        # « Ces salaires correspondent à une base SMIC pour tous les assurés
        # cultuels. » Le moteur prenait le revenu saisi, et servait au
        # ministre déclaré à une fois et demie le salaire moyen une pension
        # de base plus de deux fois trop haute. Le forfait
        # est celui de l'année — 169 heures mensuelles avant 2002, 151,67
        # ensuite —, proratisé sur ses mois.
        annuelle = moteur.catalogue[periode.regime].periode(ligne.annee) or periode
        if annuelle.assiette_repere_smic is not None:
            return (annuelle.assiette_repere_smic
                    * moteur.macro.smic_horaire(ligne.annee) * ligne.fraction_annee)
    return _assiette_de_reference(periode, ligne)


def salaire_de_reference(moteur, code: str, carriere: Carriere,
                         periode: PeriodeRegime,
                         annee_liquidation: int, plafonner: bool,
                         generation: int | None = None,
                         avpf: bool = True,
                         membres: tuple[str, ...] | None = None,
                         enfants_majores: int = 0,
                         depuis: int | None = None,
                         annees: int | None = None,
                         plancher: bool = False) -> float:
    """Salaire de référence, exprimé en euros de l'année de liquidation.

    ``depuis``, ``annees`` et ``plancher`` servent au revenu annuel moyen des
    non-salariés agricoles depuis 2016 (L. 732-24, I, 1°) : les seules années
    à partir de ``depuis``, les ``annees`` meilleures d'entre elles, et chaque
    revenu relevé au repère d'assiette de la période — le minimum sur lequel
    la cotisation a été appelée.

    **Il porte sur les seules années passées DANS CE régime** — ou dans
    l'un des ``membres`` de sa chaîne de succession, quand ``code`` liquide
    pour un régime qu'il a absorbé : les années CANCAVA d'un artisan sont
    des années du RSI, puis du régime général, et n'entrent qu'une fois
    dans un seul salaire annuel moyen. Voir
    :func:`~retraite_notionnelle.droit.coordonner.groupes_de_succession`.

    Un régime ne
    liquide que ce qui lui a été déclaré : la pension civile se calcule sur
    le traitement des six derniers mois de service, pas sur le dernier
    salaire d'une carrière poursuivie ailleurs, et le salaire annuel moyen
    du régime général ne retient que les salaires portés à son compte. Sans
    cette condition, un polypensionné passé de la fonction publique au privé
    liquidait sa pension civile sur son salaire privé de fin de carrière —
    et le prorata de durée, lui, restait celui du régime : le modèle
    rapportait une part de carrière publique à une assiette qui ne l'était
    pas.

    Trois autres règles de droit commandent ce calcul, et le modèle les
    applique toutes.

    La première est la **revalorisation des salaires portés au compte** :
    les salaires anciens sont réévalués par les coefficients annuels que
    fixe l'arrêté, et le modèle les LIT au lieu de les reconstituer. Il les
    approchait par « les salaires jusqu'en 1986, les prix depuis », ce qui
    décrit les arrêtés dans les grandes lignes mais ignore leurs
    revalorisations semestrielles, leurs gels, leurs revalorisations
    exceptionnelles et leurs changements de DÉLAI d'application : cette
    approximation sur-revalorisait les salaires anciens de 12 % sur
    quarante ans. La grandeur commande le salaire de référence deux fois
    plutôt qu'une, puisque la moyenne porte sur les N MEILLEURES années et
    que « meilleures » se juge sur des salaires revalorisés.

    La seconde est le **nombre d'années retenues**, que la loi du 22 juillet
    1993 fait passer de dix à vingt-cinq à raison d'une par génération. Le
    lire à l'année de liquidation opposait vingt-cinq années à des assurés
    auxquels la loi n'en a jamais demandé plus de dix — et étendre la
    moyenne aux années les plus faibles ne peut que l'abaisser.

    Le salaire retenu est celui de l'assiette du régime, et pas la
    rémunération entière : la pension civile porte sur le seul traitement
    indiciaire, primes exclues. C'est le paramètre qui commande le taux de
    remplacement d'un fonctionnaire, puisque les primes n'ouvrent de droit
    qu'au RAFP.
    """
    avpf_ouvert = (
        avpf and "avpf" in periode.avantages_non_contributifs
    )
    # Les coefficients des arrêtés ne valent que pour un salaire PORTÉ AU
    # COMPTE. Un régime qui liquide sur le dernier traitement ne porte rien
    # à un compte : lui appliquer les coefficients du régime général serait
    # une erreur de catégorie. Le traitement d'un FONCTIONNAIRE suit le
    # point d'indice — l'agent garde son indice, et c'est le point de
    # l'année du départ qui dit ce que vaut son traitement de l'année
    # d'avant — ; les autres régimes à dernier salaire restent sur les
    # prix, avec la réserve que `docs/limites.md` leur attache.
    porte_au_compte = periode.salaire_reference not in (
        "derniers_6_mois", "dernier_salaire"
    )
    suit_le_point = (
        not porte_au_compte
        and moteur.catalogue[code].famille == "fonction_publique"
    )
    # Le MOIS de la liquidation désigne la circulaire applicable : les
    # arrêtés ne prennent pas tous effet au 1er janvier, et deux d'entre
    # eux portent l'année 2022. Le mois ne vaut que si l'année passée est
    # bien celle de la liquidation — certains appels bornent l'année à la
    # dernière que porte la fiche du régime.
    mois_liquidation = (
        carriere.mois_liquidation
        if (carriere.age_liquidation is not None
            and annee_liquidation == carriere.annee_liquidation)
        else 1
    )

    def revaloriser(perception: int, arrivee: int) -> float:
        if not porte_au_compte:
            if suit_le_point:
                ratio = moteur.minimum_garanti.ratio_point_indice(perception, arrivee)
                if ratio is not None:
                    return ratio
            return moteur.macro.coefficient_revalorisation_salaires(
                perception, arrivee
            )
        return moteur.macro.coefficient_revalorisation_portee_au_compte(
            perception, arrivee, mois_liquidation
        )
    codes_admis = frozenset(membres) if membres else frozenset((code,))
    # LA RÈGLE DE LA DATE D'EFFET. Le salaire annuel moyen du régime général
    # n'a pas toujours été la moyenne annuelle des meilleures années : les dix
    # DERNIÈRES jusqu'en 1972, rapportées à leurs trimestres jusqu'en juin 1995,
    # sans les années qui ne valident aucun trimestre depuis 2004. La période
    # renvoie à la fiche datée qui le dit (`regles_du_salaire_annuel_moyen`).
    regle = (
        moteur.fiches_datees.regle(
            periode.regles_du_salaire_annuel_moyen,
            f"{annee_liquidation:04d}-{mois_liquidation:02d}-01")
        if periode.regles_du_salaire_annuel_moyen else None
    )
    # LE REVENU D'UNE ANNÉE, TOUTES ACTIVITÉS DU RÉGIME RÉUNIES. Deux
    # activités cumulées qui versent au même régime — ou à deux régimes
    # alignés que la liquidation unique réunit — forment un seul revenu
    # annuel, écrêté UNE fois au plafond : c'est la somme des salaires et
    # revenus d'une même année que la LURA écrête (R. 173-4-4-1, 1°).
    # Une année d'une seule activité n'a qu'un terme, et rien ne bouge.
    par_annee: dict[int, list[float]] = {}
    # Les trimestres de chaque année au régime, cotisés — assurance vieillesse
    # des parents au foyer comprise — puis assimilés : ce que la moyenne
    # d'avant juillet 1995 met au dénominateur, et ce qu'elle écarte avant 1973.
    trimestres: dict[int, list[int]] = {}
    for ligne in carriere.lignes:
        if ligne.annee >= annee_liquidation:
            continue
        if depuis is not None and ligne.annee < depuis:
            continue
        if codes_admis.isdisjoint(coordonner.regimes_de(moteur, 
                ligne, ligne.annee,
                carriere.date_entree(ligne.affiliation),
                revenu=ligne.revenu if ligne.cotise else ligne.revenu_reference,
                plafond=moteur.macro.plafond_securite_sociale(ligne.annee))):
            continue
        avpf_de_la_ligne = (not ligne.cotise and avpf_ouvert
                            and ligne.revenu_avpf > 0)
        if regle is not None:
            compte = trimestres.setdefault(ligne.annee, [0, 0])
            compte[0 if ligne.cotise or avpf_de_la_ligne else 1] += ligne.trimestres_valides
        if not ligne.cotise:
            # Assurance vieillesse des parents au foyer : la CNAF cotise
            # sur une assiette forfaitaire, et ce salaire est PORTÉ AU
            # COMPTE. C'est ce qui la distingue d'une période assimilée,
            # laquelle valide des trimestres sans jamais ajouter de salaire
            # — et c'est ce que le modèle ne faisait pas, alors que le cas
            # type « carrière interrompue » l'annonçait.
            if not avpf_de_la_ligne:
                continue
            revenu = ligne.revenu_avpf
        else:
            revenu = max(assiette_de_reference(moteur, periode, ligne),
                         acquerir.assiette_minimale(moteur, codes_admis, ligne))
            if plancher and periode.assiette_repere_smic is not None:
                revenu = max(revenu, periode.assiette_repere_smic
                             * moteur.macro.smic_horaire(ligne.annee)
                             * ligne.fraction_annee)
        # TRANCHE DE SALAIRE. Un régime qui liquide TRANCHE PAR TRANCHE —
        # le personnel navigant, dont l'article R. 426-16-1 attribue
        # 1,85 % par annuité à la première et 1,4 % à la seconde — a
        # besoin que son salaire de référence soit celui de SA tranche, et
        # non le salaire entier. Sans quoi les deux périodes simultanées
        # calculeraient le même salaire moyen et la seconde paierait une
        # deuxième fois sur la première.
        #
        # Le découpage ne s'applique qu'aux assiettes dont la borne basse
        # n'est pas nulle : `plafonnee`, `tranche_1` et `tranche_a` partent
        # de zéro et continuent de passer par `plafonner` ci-dessous,
        # exactement comme avant. Aucun régime en annuités du catalogue
        # n'utilisait de tranche à borne basse avant celui-ci : ce bloc ne
        # déplace donc aucun chiffre existant.
        borne_basse, borne_haute = periode.bornes_assiette_en_euros(
            moteur.macro.plafond_securite_sociale(ligne.annee)
            * ligne.fraction_annee
        )
        if borne_basse > 0:
            revenu = max(0.0, min(revenu, borne_haute or revenu) - borne_basse)
        cumul = par_annee.setdefault(ligne.annee, [0.0, 0.0])
        cumul[0] += revenu
        cumul[1] = max(cumul[1], ligne.fraction_annee)

    revenus: list[float] = []
    annees_des_revenus: list[int] = []
    # Le dernier revenu avant revalorisation, et son année : ce qu'une
    # pension différée revalorise autrement (voir plus bas).
    dernier_brut: tuple[int, float] | None = None
    for annee in sorted(par_annee):
        revenu, fraction = par_annee[annee]
        if plafonner:
            # Le plafond se proratise sur les mois travaillés : l'année
            # d'entrée dans la vie active n'est pas pleine, et un plafond
            # de douze mois y laisserait passer un salaire qu'il aurait
            # écrêté.
            revenu = min(
                revenu,
                moteur.macro.plafond_securite_sociale(annee) * fraction,
            )
        if periode.ecretement_salaire_reference is not None:
            # L'ÉCRÊTEMENT de la CRPCEN : « n'est compté que pour moitié pour
            # la part excédant trois fois le plafond […] ; il n'est pas pris
            # en compte pour la part excédant sept fois ce plafond »
            # (décret n° 90-1215, article 89), le plafond proratisé comme
            # ci-dessus.
            seuil, part, haut = periode.ecretement_salaire_reference
            plafond = moteur.macro.plafond_securite_sociale(annee) * fraction
            revenu = (min(revenu, seuil * plafond)
                      + part * max(0.0, min(revenu, haut * plafond) - seuil * plafond))
        dernier_brut = (annee, revenu)
        revenus.append(revenu * revaloriser(annee, annee_liquidation))
        annees_des_revenus.append(annee)

    if not revenus:
        return 0.0

    reference = periode.salaire_reference
    if regle is not None and reference in ("25_meilleures_annees", "10_meilleures_annees"):
        # Une année « valide » au sens de R. 351-9 si son salaire, toutes
        # activités du régime réunies, atteint le seuil d'un trimestre — ou si
        # le relevé lui en reconnaît un.
        validantes = {
            annee for annee in par_annee
            if trimestres[annee][0] >= 1
            or moteur.macro.trimestres_valides(par_annee[annee][0], annee) >= 1
        }
        return moyenne_selon_la_regle(
            regle, list(zip(annees_des_revenus, revenus)), trimestres, validantes,
            annees if annees is not None else nombre_d_annees_retenues(
                moteur, periode, carriere, generation, enfants_majores),
            carriere.annee_naissance + AGE_DES_DIX_DERNIERES_ANNEES,
        )
    if annees is not None:
        retenus = sorted(revenus, reverse=True)[:annees]
    elif reference in ("25_meilleures_annees", "10_meilleures_annees"):
        retenus = sorted(revenus, reverse=True)[:nombre_d_annees_retenues(
            moteur, periode, carriere, generation, enfants_majores)]
    elif reference in ("derniers_6_mois", "dernier_salaire"):
        # Le traitement des six derniers mois est celui EN VIGUEUR au
        # départ. L'année de la liquidation est incomplète — l'assuré n'y a
        # travaillé que quelques mois —, mais c'est bien son traitement que
        # liquide le régime : on l'annualise plutôt que de reculer d'un an.
        # La ligne du régime, et non l'activité principale : un
        # fonctionnaire qui cumule une activité libérale liquide son
        # traitement, quel que soit le rang de la ligne.
        derniere = next((
            ligne for ligne in carriere.lignes_de(annee_liquidation)
            if not codes_admis.isdisjoint(coordonner.regimes_de(moteur, 
                ligne, annee_liquidation,
                carriere.date_entree(ligne.affiliation),
                revenu=ligne.revenu,
                plafond=moteur.macro.plafond_securite_sociale(annee_liquidation)))
        ), None)
        if (derniere is not None and derniere.cotise
                and derniere.fraction_annee > 0
                and not codes_admis.isdisjoint(coordonner.regimes_de(moteur, 
                    derniere, annee_liquidation,
                    carriere.date_entree(derniere.affiliation),
                    revenu=derniere.revenu,
                    plafond=moteur.macro.plafond_securite_sociale(annee_liquidation)))):
            # À temps plein : le traitement indiciaire du grade, que le temps
            # partiel d'une retraite progressive réduit sans le changer.
            traitement = (assiette_de_reference(moteur, periode, derniere)
                          / (derniere.fraction_annee * derniere.quotite))
            if plafonner:
                traitement = min(
                    traitement,
                    moteur.macro.plafond_securite_sociale(annee_liquidation),
                )
            return traitement
        # LA PENSION DIFFÉRÉE. L'agent n'est plus en service l'année de la
        # liquidation : il a été radié des cadres au plus tard à la fin de
        # sa dernière année de service, et sa pension attend l'âge. Le
        # traitement qu'il détenait suit alors les revalorisations des
        # PENSIONS, de la radiation à la mise en paiement (L. 25 du code
        # des pensions, article 26 du décret n° 2003-1306, article 22 du
        # décret n° 2004-1056), et non le point d'indice des actifs, que
        # le moteur lui appliquait : +6,3 % de 2011 à 2026, quand les
        # pensions prenaient près d'un quart. Avant 2004, la péréquation
        # faisait suivre le point à toute pension : rien ne change.
        if (dernier_brut is not None
                and code in coordonner.REGIMES_CODE_DES_PENSIONS):
            derniere_annee, brut = dernier_brut
            radiation = date(derniere_annee + 1, 1, 1)
            paiement = date(annee_liquidation, mois_liquidation, 1)
            if radiation < paiement and paiement >= revalorisation.FIN_PEREQUATION:
                coefficient = revalorisation.coefficient_traitement_differe(
                    moteur.revalorisations_pensions,
                    moteur.minimum_garanti.ratio_point_indice,
                    derniere_annee, radiation, paiement)
                if coefficient is not None:
                    return brut * coefficient
        return revenus[-1]
    elif reference == "carriere_entiere":
        retenus = revenus
    else:
        retenus = revenus
    return somme_ordonnee(retenus) / len(retenus)


#: Les dix dernières années d'avant 1973 se comptent « avant l'âge de soixante
#: ans » (ordonnance du 19 octobre 1945, article 71) : avant l'année où il tombe.
AGE_DES_DIX_DERNIERES_ANNEES = 60


def moyenne_selon_la_regle(regle: dict, valeurs: list[tuple[int, float]],
                           trimestres: dict[int, list[int]], validantes: set[int],
                           nombre: int, annee_soixante_ans: int) -> float:
    """Le salaire annuel moyen que la version de la date d'effet forme.

    ``valeurs`` porte, année par année et dans leur ordre, le salaire du régime
    revalorisé ; ``trimestres``, ses trimestres cotisés puis assimilés ;
    ``validantes``, les années dont le salaire valide au moins un trimestre.
    La fiche ``salaire_annuel_moyen`` dit d'où vient chaque paramètre :

    * ``annees_sans_trimestre: exclues`` — depuis 2004, une année qui ne valide
      aucun trimestre n'entre plus dans la moyenne (R. 351-29) ;
    * ``annees_assimilees_exclues`` — avant 1973, pas d'année qui compte deux
      trimestres assimilés ou plus (article 74 du décret du 29 décembre 1945) ;
    * ``selection: dernieres`` — avant 1973, les ``nombre`` dernières années
      d'avant l'année des soixante ans, et, depuis juillet 1948
      (``avant_la_liquidation``), celles d'avant l'effet si leur moyenne est
      plus avantageuse ; ``meilleures`` sinon, sur les salaires revalorisés ;
    * ``calcul: trimestriel`` — jusqu'au 30 juin 1995, la somme des salaires
      retenus rapportée à leurs trimestres, multipliée par quatre (circulaire
      Cnav 1/73), assimilés compris depuis 1973 ; ``annuel`` ensuite, la somme
      rapportée au nombre d'années (circulaire Cnav 95/94).

    Les sommes se font dans l'ordre où le moteur les faisait — les meilleures
    années de la plus forte à la plus faible —, si bien qu'une carrière que la
    règle ne touche pas garde son salaire moyen au bit près.
    """
    candidates = valeurs
    if regle["annees_sans_trimestre"] == "exclues":
        candidates = [(annee, valeur) for annee, valeur in candidates if annee in validantes]
    if regle["annees_assimilees_exclues"]:
        candidates = [(annee, valeur) for annee, valeur in candidates
                      if trimestres[annee][1] < 2]
    avec_assimiles = regle["trimestres_comptes"] == "cotises_et_assimiles"

    def moyenne(retenues: list[tuple[int, float]]) -> float:
        if not retenues:
            return 0.0
        somme = somme_ordonnee(valeur for _, valeur in retenues)
        if regle["calcul"] == "trimestriel":
            denominateur = somme_ordonnee(
                min(4, trimestres[annee][0] + (trimestres[annee][1] if avec_assimiles else 0))
                for annee, _ in retenues)
            if denominateur > 0:
                return somme * 4.0 / denominateur
        return somme / len(retenues)

    if regle["selection"] == "dernieres":
        choix = [[c for c in candidates if c[0] < annee_soixante_ans][-nombre:]]
        if regle["avant_la_liquidation"]:
            choix.append(candidates[-nombre:])
        return max(moyenne(retenues) for retenues in choix)
    return moyenne(sorted(candidates, key=lambda c: c[1], reverse=True)[:nombre])


def nombre_d_annees_retenues(moteur, periode: PeriodeRegime, carriere: Carriere,
                             generation: int | None,
                             enfants_majores: int = 0) -> int:
    """Le nombre des meilleures années que retient le salaire annuel moyen.

    Vingt-cinq, ou dix, selon la période ; lu à la génération quand la
    période le dit — la loi du 22 juillet 1993 le fait passer de dix à
    vingt-cinq à raison d'une année par génération, deux fois plus lentement
    pour les artisans et les commerçants (R. 634-1-1), dont la table vaut
    jusqu'aux pensions prenant effet en 2025 : la version de la date d'effet
    le dit (fiche ``revenu_annuel_moyen_independants``).
    """
    annees = 10 if periode.salaire_reference == "10_meilleures_annees" else 25
    if periode.salaire_reference_par_generation and generation is not None:
        table = moteur.annees_salaire_reference
        if periode.salaire_reference_par_generation == "independants":
            date_effet = date_d_effet(carriere)
            regle = (None if date_effet is None else moteur.fiches_datees.regle(
                periode.regles_du_salaire_annuel_moyen
                or "revenu_annuel_moyen_independants", date_effet))
            if regle is None or regle.get("table") == "independants":
                table = moteur.annees_revenu_independants
        par_generation = table.annees(generation)
        if par_generation is not None:
            annees = par_generation[0]
        # LES PARENTS : vingt-quatre années pour qui bénéficie d'une
        # majoration ou d'une bonification au titre d'un enfant,
        # vingt-trois pour deux enfants et plus, pour les pensions
        # prenant effet à compter du 1er septembre 2026 (article
        # R. 173-3-2, décret n° 2026-699 du 29 juillet 2026, pris pour
        # l'article 103 de la loi de financement pour 2026). La moyenne
        # porte sur moins d'années, donc sur de meilleures : c'est la
        # mesure « mères de famille » de cette loi, et elle vaut à qui
        # détient les trimestres, la mère par défaut dans ce modèle.
        if (enfants_majores > 0 and carriere.age_liquidation is not None
                and carriere.date_liquidation.rang
                >= moteur.PARENTS_MEILLEURES_ANNEES_DEPUIS.rang):
            annees = max(1, annees - (1 if enfants_majores == 1 else 2))
    return annees


def duree_proratisation(moteur, periode: PeriodeRegime, carriere: Carriere,
                         requis: int) -> tuple[int, Fiabilite | None]:
    """Dénominateur du coefficient de proratisation, dans ce régime.

    Il vaut la durée requise partout, sauf pour les générations 1944 à 1948
    et celles qui les précèdent, auxquelles l'article R. 351-6 oppose une
    durée maximale plus courte — 150 trimestres avant 1944, puis 152, 154,
    156, 158 et 160. La table ne répond que là ; ailleurs, c'est la durée
    requise qui fait office, comme le droit le veut depuis 1949.

    **La table est celle du code de la sécurité sociale**, et la fiche dit
    qui la suit : le régime général et les régimes alignés. La fonction
    publique et les régimes spéciaux ont la leur, calendaire et non
    générationnelle (article L. 13 du code des pensions) ; elle n'est pas
    modélisée, et leur durée requise continue d'y faire office. Leur
    appliquer la table du privé remplacerait une approximation par une
    autre, sans que rien ne l'établisse.

    Et la durée de proratisation ne dépasse jamais la durée requise : les
    périodes anciennes, dont la durée maximale est plus courte que
    150 trimestres — 120 sous les ordonnances de 1945 —, gardent la leur.
    """
    if not periode.duree_proratisation_par_generation:
        return requis, None
    par_generation = moteur.durees_proratisation.trimestres(carriere.generation)
    if par_generation is None:
        return requis, None
    return min(par_generation[0], requis), par_generation[1]


def millesime_du_bareme(moteur, periode: PeriodeRegime, carriere: Carriere,
                        annee_liquidation: int) -> int:
    """La ligne du barème de décote en table qui vaut pour cet assuré.

    La fonction publique titre sa colonne à l'année civile où les conditions
    sont réunies (loi du 21 août 2003, article 66, III). Les régimes spéciaux
    ont leurs marches au 1er juillet : « pour les personnes remplissant les
    conditions […] entre le 1er juillet 2010 et le 30 juin 2011 inclus », puis
    « au 1er juillet de chaque année ». Chaque ligne de leur table porte donc
    la règle du 1er juillet de l'année précédente au 30 juin de l'année
    écrite, et se lit au MOIS où l'assuré réunit les conditions, comme la
    durée requise (:func:`ouvrir.mois_ouverture_des_droits`) : un droit ouvert
    de juillet à décembre lit la ligne de l'année qui suit. Le moteur lisait
    l'année civile, et servait au second semestre la marche d'avant : rien au
    second semestre 2010, puis un huitième de point de moins par trimestre et
    un ou deux trimestres de moins à l'âge d'annulation — quatorze trimestres
    à 1,125 % au lieu de quinze à 1,25 % au second semestre 2019.
    """
    if periode.bareme_decote not in _BAREMES_REGIMES_SPECIAUX:
        return ouvrir.annee_ouverture_des_droits(moteur, periode, carriere,
                                                 annee_liquidation)
    ouverture = DateMois.depuis_rang(
        ouvrir.mois_ouverture_des_droits(moteur, periode, carriere))
    return ouverture.annee + (1 if ouverture.mois >= 7 else 0)


#: La surcote des régimes spéciaux ne compte que les trimestres « cotisés et
#: effectués après le 1er juillet 2008 » (:func:`trimestres_de_surcote_regimes_speciaux`).
SURCOTE_REGIMES_SPECIAUX_DEPUIS = DateMois(2008, 7)


def trimestres_de_surcote_regimes_speciaux(carriere: Carriere, trimestres: int,
                                           requis: int, age_surcote: float) -> int:
    """Les trimestres de surcote des régimes spéciaux réformés en 2008.

    Chacun des six décrets écrit la même règle : « Lorsque la durée
    d'assurance […] est supérieure au nombre de trimestres nécessaires pour
    obtenir le pourcentage maximum de la pension […], sans être inférieure à
    cent soixante trimestres, et que l'agent a atteint l'âge [de son
    article], […] le nombre de trimestres pris en compte […] est égal […] au
    nombre de trimestres d'assurance […] cotisés et effectués après le
    1er juillet 2008, au-delà de l'âge [de son article] et en sus du nombre
    de trimestres mentionné à l'alinéa précédent » (décret n° 2008-639,
    article 13, II ; le même à la RATP, aux IEG, à la CRPCEN, à la
    Comédie-Française et à l'Opéra). Le moteur leur appliquait la règle du
    régime général : ni le seuil de cent soixante trimestres, ni la date,
    et l'âge lu à l'année. Un clerc de notaire né en 1945, dont le droit
    s'ouvre à cinquante-cinq ans et qui part en 2009, se voyait compter en
    surcote ses trimestres d'après cinquante-cinq ans, quand le texte ne lui
    en compte que deux, ceux du second semestre 2008.

    Les trimestres au-delà de la durée requise sont les derniers de la
    carrière, comme ceux d'après l'âge et la date : le plus petit des deux
    nombres est leur intersection. Ceux d'après l'âge et la date se comptent
    au mois près, jusqu'à la date d'effet de la pension.
    """
    if trimestres < 160:
        return 0
    debut = carriere.date_de_l_age(age_surcote)
    if debut.rang < SURCOTE_REGIMES_SPECIAUX_DEPUIS.rang:
        debut = SURCOTE_REGIMES_SPECIAUX_DEPUIS
    fin = carriere.date_liquidation
    apres = 0.0
    if debut.rang < fin.rang:
        for ligne in carriere.lignes:
            if ligne.cotise:
                apres += trimestres_de_la_ligne_entre(carriere, ligne, debut, fin)
    return min(max(0, trimestres - requis), int(apres + 1e-9))


def borne_de_la_duree(moteur, periode: PeriodeRegime, carriere: Carriere,
                      cible: int) -> int:
    """Le plus grand décompte de la décote par la durée, aux régimes spéciaux.

    Le 2° de chaque décret de la réforme de 2008 compte les trimestres qui
    manquent à la durée requise, mais : « Toutefois, le nombre de trimestres
    pris en compte ne peut excéder la différence entre ledit nombre de
    trimestres permettant d'obtenir le pourcentage maximum de la pension et
    150, ce maximum étant réduit, le cas échéant, du nombre de trimestres
    d'assurance […] cotisés et effectués au-delà de l'âge auquel le droit à
    pension est ouvert » (décret n° 2008-639, article 13, I, 2° ; le même
    alinéa à la RATP, aux IEG, à la CRPCEN, à la Comédie-Française et à
    l'Opéra). La CNIEG l'applique ainsi : Madame D, 165 trimestres requis,
    quatre cotisés depuis l'ouverture de son droit, n'en compte pas plus de
    onze par la durée (page « Décote » de son site ; la circulaire n° 2024/15,
    § 4, en donne un autre, à dix-huit). ``cible`` est la durée
    que le 2° oppose, abaissée à la SNCF pour la décote (article 35, II).
    Les trimestres d'après l'ouverture se comptent au mois près, jusqu'à la
    date d'effet de la pension.
    """
    ouverture = carriere.date_de_l_age(ouvrir.age_ouverture(moteur, periode, carriere))
    fin = carriere.date_liquidation
    apres = 0.0
    if ouverture.rang < fin.rang:
        for ligne in carriere.lignes:
            if ligne.cotise:
                apres += trimestres_de_la_ligne_entre(carriere, ligne, ouverture, fin)
    return max(0, cible - 150 - int(apres + 1e-9))


def decote_opposable(moteur, periode: PeriodeRegime, carriere: Carriere,
            annee_liquidation: int
            ) -> tuple[float | None, float, Fiabilite | None]:
    """Décote opposable : coefficient, âge d'annulation, fiabilité.

    Un régime sans décote — fonction publique avant 2006, régimes spéciaux
    avant 2008 — n'en acquiert pas une parce que la table en porte une :
    ``None`` dans la fiche reste ``None`` ici, et le coefficient renvoyé
    est ``None``.

    **Les barèmes en table se lisent à l'ouverture du droit, pas à la
    liquidation** — à l'année, et au mois pour les régimes spéciaux
    (:func:`millesime_du_bareme`). Le III de l'article 66 de la loi du 21 août
    2003 titre sa colonne « Année au cours de laquelle sont réunies les
    conditions mentionnées au I et au II de l'article L. 24 », et les
    décrets de 2008 des régimes spéciaux visent « les personnes remplissant
    les conditions définies à l'article 6 » entre deux dates. Un
    fonctionnaire dont le droit s'ouvre en 2008 garde donc 0,375 % et
    « limite d'âge moins douze trimestres » quelle que soit l'année de son
    départ ; qui part avant l'âge d'ouverture réunit les conditions à la
    liquidation, et c'est ce millésime-là qui vaut. Le modèle lisait le
    barème à l'année de liquidation, et c'est la confrontation à
    OpenFisca-France-Pension qui l'a fait voir : deux trimestres de décote
    de trop pour un sédentaire né en 1948 parti à soixante-deux ans.

    **La fonction publique n'a pas la décote du régime général.** L'article
    L. 14 du code des pensions lui donne la sienne, montée en charge de
    2006 à 2020, et surtout un âge d'annulation qui n'est pas un âge en
    propre : c'est la LIMITE D'ÂGE du grade, diminuée d'un nombre de
    trimestres décroissant. Un sédentaire liquidant en 2012 voyait sa
    décote s'annuler à 63 ans, pas à 67 — et chaque trimestre manquant lui
    coûtait 0,875 %, pas 1,25 %. Lui opposer le barème du privé retirait
    jusqu'à un sixième de sa pension.

    **Et les régimes spéciaux ont ce barème avec quatre ans de retard.**
    La réforme de 2008 ne leur applique aucune décote avant le 1er juillet
    2010, puis un dixième du taux plein, un dixième de plus chaque année
    jusqu'à 1,25 % en 2019 : un cheminot parti en 2011 décotait de 0,125 %
    par trimestre manquant, non de 1,25 %.
    """
    age_annulation = ouvrir.age_taux_plein(moteur, periode, carriere)
    if periode.bareme_decote in _BAREMES_DECOTE_EN_TABLE:
        table = (moteur.decote_fonction_publique
                 if periode.bareme_decote == "fonction_publique"
                 else moteur.decote_regimes_speciaux)
        parametres = table.parametres(
            millesime_du_bareme(moteur, periode, carriere, annee_liquidation)
        )
        if parametres is None:
            return None, age_annulation, None
        trimestres_avant, coefficient, fiabilite = parametres
        if periode.bareme_decote == "regimes_speciaux_age_fixe":
            # Les catégories d'âge atypique — artistes du ballet, musiciens
            # de l'orchestre — n'ont pas l'âge de référence de droit
            # commun : le V de l'article 14 leur donne « l'âge minimum
            # d'ouverture du droit à pension qui leur est applicable majoré
            # de quatre trimestres pour la période du 1er juillet 2010 au
            # 30 juin 2011 inclus, six trimestres pour la période du 1er
            # juillet 2011 au 30 juin 2012 inclus et huit trimestres pour
            # les périodes postérieures au 30 juin 2012 ». Aux mêmes dates,
            # ce sont les vingt trimestres de la réforme moins la diminution
            # de la table — seize, quatorze, douze —, bornés à l'âge que la
            # fiche porte, celui des huit trimestres. Le moteur gardait
            # quarante-deux ans dès 2010 pour le ballet.
            ouverture = ouvrir.age_ouverture(moteur, periode, carriere)
            return (coefficient,
                    min(age_annulation, ouverture + (20 - trimestres_avant) / 4.0),
                    fiabilite)
        return coefficient, age_annulation - trimestres_avant / 4.0, fiabilite
    if periode.decote_par_trimestre is None:
        return None, age_annulation, None
    if periode.age_table:
        # Le taux que le règlement de la section écrit pour la génération,
        # quand il en écrit un : la CARCDSF de 2011 à 2023.
        propre = moteur.ages_regimes.decote(periode.age_table, carriere.generation)
        if propre is not None:
            return propre[0], age_annulation, propre[1]
    if periode.decote_par_generation:
        par_generation = moteur.coefficients_minoration.coefficient(
            carriere.generation
        )
        if par_generation is not None:
            return par_generation[0], age_annulation, par_generation[1]
    return periode.decote_par_trimestre, age_annulation, None


def trimestres_de_decote(moteur, periode: PeriodeRegime, carriere: Carriere,
                          trimestres: int,
                          requis: int, age_liquidation: float,
                          age_annulation: float) -> float:
    """Trimestres de décote opposables, plafond compris.

    **Le militaire a le sien, et il ne compte pas des âges.** Le II de
    l'article L. 14 lui oppose, non la distance à un âge d'annulation, mais
    « le nombre de trimestres manquants […] pour atteindre […] la durée de
    services militaires effectifs nécessaire pour pouvoir bénéficier d'une
    liquidation de la pension […] augmentée d'une durée de services
    effectifs de dix trimestres » — dans la limite de dix trimestres, et non
    de vingt. Un sous-officier parti à quarante ans avec dix-sept ans de
    services ne perd donc que les deux trimestres et demi qui le séparent de
    dix-neuf ans et demi, quand le barème des civils lui aurait retiré le
    quart de sa pension pour être parti vingt-deux ans avant l'âge légal.

    Le décompte retient le plus favorable des deux : trimestres manquants
    pour la durée requise, ou trimestres manquants jusqu'à l'âge
    d'annulation de la décote.

    **Le plafond de vingt trimestres n'est pas une règle de plus : c'est
    l'arithmétique des deux âges.** Il est écrit là où le droit a voulu
    l'écrire — R. 643-7 pour les professions libérales, R. 723-38 pour les
    avocats, le I de L. 14 pour la fonction publique — et absent de
    R. 351-27 2° comme de R. 732-61, qui ne s'en sont jamais souciés. La
    raison est mesurable dans les tables du dépôt : l'écart entre l'âge
    d'ouverture et l'âge d'annulation vaut EXACTEMENT vingt trimestres pour
    les générations 1930 à 1961, puis descend à dix-huit, quinze, treize et
    douze à mesure que les réformes relèvent le premier sans toucher au
    second. Sur toute liquidation que le droit ouvre, le décompte par l'âge
    est donc au plus de vingt par construction, et le plafond ne mord
    jamais — ``tests/test_moteur.py`` le vérifie sur toute la grille.

    Il ne mordrait que sur une liquidation ANTÉRIEURE à l'âge d'ouverture,
    que le modèle refuse depuis qu'il sait opposer un âge à toutes les
    carrières. Le garder ne coûte donc rien et protège d'un changement
    d'âges qui casserait l'identité ; le retirer demanderait de vérifier
    les trois textes qui l'écrivent. On le garde, et cette phrase dit
    pourquoi il ne se voit pas.

    Le décompte par l'ÂGE est arrondi à l'entier supérieur, comme le veut
    l'article R. 351-27. Les âges d'annulation des générations 1951 à 1954
    valent 65,33, 65,75, 66,17 et 66,58 ans : sans cet arrondi, on opposait
    13,32 trimestres à un assuré né en 1951 parti à 62 ans, quand le droit
    lui en oppose 14. Le barème d'anticipation de l'Agirc-Arrco, lui,
    arrondissait déjà — les deux décomptes suivent maintenant la même règle.
    """
    militaire = ouvrir.droit_militaire(moteur, periode, carriere)
    if militaire is not None:
        manquants_services = max(
            0, militaire.trimestres_cible - militaire.trimestres_servis
        )
        # Le nombre de trimestres manquants « est arrondi à l'entier
        # supérieur » (L. 14, II) : la durée d'assurance, au jour, en garde
        # les fractions.
        manquants_duree = _au_trimestre_superieur(requis - trimestres)
        return float(min(manquants_services, manquants_duree,
                         TRIMESTRES_DECOTE_MILITAIRE))
    manquants_age = float(_au_trimestre_superieur(
        (age_annulation - age_liquidation) * 4
    ))
    if periode.decote_par_la_duree_seule:
        # La CRPN depuis 2022 : la durée seule compte, et l'âge d'annulation
        # ne fait qu'effacer la décote une fois atteint (R. 6527-22 et
        # R. 6527-23 du code des transports).
        trimestres_decote = (
            0.0 if manquants_age <= 0 else float(max(0, requis - trimestres))
        )
    elif periode.decote_annulee_par_la_duree:
        # La SNCF compte la décote par la durée sur une cible abaissée de
        # deux à dix trimestres selon la génération (décret n° 2008-639,
        # article 35, II) ; partout ailleurs, rien n'est retranché. Et les
        # régimes spéciaux bornent ce décompte (:func:`borne_de_la_duree`).
        cible = requis - retranche_decote(moteur, periode, carriere)
        # Arrondi à l'entier supérieur (L. 14, I) : la durée d'assurance du
        # code des pensions se compte au jour, et en garde les fractions.
        par_duree = _au_trimestre_superieur(cible - trimestres)
        if periode.bareme_decote in _BAREMES_REGIMES_SPECIAUX:
            par_duree = min(par_duree, borne_de_la_duree(moteur, periode, carriere, cible))
        trimestres_decote = min(par_duree, manquants_age)
    else:
        # Avant l'ordonnance du 26 mars 1982, le taux ne dépendait QUE de
        # l'âge : le régime général servait 20 % à 60 ans, majorés de
        # 4 points par année différée, puis — loi Boulin — 50 % à 65 ans,
        # diminués de 5 points par année anticipée. Aucune durée, si longue
        # fût-elle, n'ouvrait le taux plein avant l'âge. Annuler la décote
        # par la durée, comme le fait le droit d'après 1982, servait le taux
        # plein à 60 ans à des générations auxquelles la loi ne l'a jamais
        # donné.
        trimestres_decote = manquants_age
        if periode.ajournement_par_annee_d_assurance:
            trimestres_decote = float(max(0, -ecart_au_taux_plein(
                moteur, periode, carriere, age_liquidation, age_annulation)))
    if trimestres_decote <= 0:
        return 0.0
    if periode.decote_trimestres_maximum is not None:
        trimestres_decote = min(trimestres_decote, periode.decote_trimestres_maximum)
    return trimestres_decote


#: L'ordonnance n° 82-270 du 26 mars 1982 entre en vigueur le 1er avril 1983
#: (article 9) : jusqu'au 31 mars, le taux dépend de l'âge seul.
ORDONNANCE_DU_26_MARS_1982 = DateMois(1983, 4)


def ecart_au_taux_plein(moteur, periode: PeriodeRegime, carriere: Carriere,
                        age_liquidation: float, age_annulation: float) -> int:
    """Avant le 1er avril 1983, les trimestres qui séparent la liquidation du
    taux plein : négatifs en deçà, la décote ; positifs au-delà, la
    majoration d'ajournement.

    **Au-delà de soixante-cinq ans, le taux croissait encore.** « En
    application de la législation en vigueur jusqu'au 31 mars 1983, le taux
    de 50 % augmente, sans limitation, de 2,5 % par trimestre d'âge après 65
    ans » (circulaire Cnav n° 22/83, point 313) ; jusqu'en 1971, les 20 %
    étaient « augmenté[s] en cas d'ajournement de 1 % par trimestre
    postérieur au soixantième anniversaire » (circulaire n° 93 SS du 17 mai
    1951), sans borne non plus. Le moteur arrêtait le taux au taux plein. Au
    delà, il compte les trimestres civils entiers, comme en deçà.

    **Avant 1951, des années d'assurance, et non d'âge.** L'article 63 de
    l'ordonnance du 19 octobre 1945 majorait les 20 % « de 4 p. 100 du
    salaire annuel de base par année d'assurance accomplie postérieurement à
    cet âge » : qui cessait de cotiser à soixante ans gardait 20 % à tout
    âge. La loi n° 51-374 n'en fait des années d'âge que pour une entrée en
    jouissance postérieure au 31 décembre 1950 (``ajournement_par_annee_d_assurance``).
    """
    if periode.ajournement_par_annee_d_assurance:
        age_ouverture = ouvrir.age_ouverture(moteur, periode, carriere)
        annees = _trimestres_cotises_apres(
            carriere, age_ouverture, carriere.annee_liquidation) // 4
        return 4 * annees - round((age_annulation - age_ouverture) * 4)
    if age_liquidation >= age_annulation:
        return int((age_liquidation - age_annulation + 1e-9) * 4)
    return -_au_trimestre_superieur((age_annulation - age_liquidation) * 4)


def taux_plein_des_femmes(periode: PeriodeRegime, carriere: Carriere, durees,
                          age_liquidation: float) -> bool:
    """Le taux de soixante-cinq ans, avant 1983, aux femmes de trente-sept ans
    et demi d'assurance.

    « La pension est également calculée au taux normalement applicable à
    soixante-cinq ans au profit : […] c) Des femmes assurées […] qui
    réunissent trente-sept ans et demi d'assurance dans le régime général ou
    dans ce régime et celui des salariés agricoles : Lorsque la pension prend
    effet à une date comprise dans la période du 1er janvier au 31 décembre
    1978 et qu'à cette date l'intéressée a atteint l'âge de soixante-trois
    ans ; Lorsque la pension prend effet à une date postérieure au 31
    décembre 1978 et qu'à cette date l'intéressée a atteint l'âge de soixante
    ans » (décret n° 45-0179, article 70-2 ; décret n° 51-727, article 1er
    bis, chez les salariés agricoles). Le moteur leur servait la moitié du
    taux à soixante ans. La durée est celle des régimes que la période
    nomme : le régime général, les assurances sociales d'avant 1945, que le
    modèle tient à part, et les salariés agricoles.
    """
    if (periode.age_taux_plein_femmes is None or carriere.sexe != "F"
            or age_liquidation < periode.age_taux_plein_femmes - 1e-9):
        return False
    return (durees.cumul_plafonne("assurance", periode.duree_taux_plein_femmes_regimes)
            >= (periode.duree_taux_plein_femmes_trimestres or 0))


def taux_acquis_au_31_mars_1983(moteur, periode: PeriodeRegime,
                                carriere: Carriere) -> float | None:
    """Le taux que garde qui avait passé soixante-cinq ans au 1er avril 1983.

    « Les dispositions de l'article L. 331 du code de la sécurité sociale,
    telles qu'elles résultent de la présente ordonnance, ne sauraient avoir
    pour effet de réduire le montant de la pension à un montant inférieur à
    celui qu'elle aurait atteint si la liquidation en était intervenue avant
    le 1er avril 1983, compte tenu de l'âge atteint à cette date »
    (ordonnance n° 82-270, article 11 ; décret n° 82-628, article 16, chez
    les salariés agricoles par l'article 8). La Cnav l'applique ainsi : « le
    taux majoré pour ajournement doit obligatoirement être déterminé en
    fonction de l'âge au 1er avril 1983 sans pouvoir être accru si l'assuré
    fixe l'entrée en jouissance de sa pension au-delà de cette date » ; né en
    mars 1917, « Coefficient acquis au 31-3-83 : 55 % » (circulaire n° 22/83,
    point 313).

    Le taux et le coefficient sont ceux de la période du régime en vigueur
    en 1982, quand elle croissait avec l'âge (``majoration_d_ajournement``),
    et les trimestres ceux que l'âge a accomplis le 31 mars 1983, l'âge
    tombant le premier du mois de naissance. La Cnav compare deux pensions,
    la nouvelle sur la durée « corrigée » après soixante-cinq ans
    (:func:`duree_majoree_apres_taux_plein`), l'ancienne sur la durée non
    corrigée : l'appelant compare les deux produits du taux et de la durée
    (fiche ``decote_avant_1983``).
    """
    # L'âge en mois révolus au 31 mars 1983, dernier jour d'un mois : les mois
    # écoulés depuis le mois de naissance, moins un, quel que soit le jour.
    mois = ORDONNANCE_DU_26_MARS_1982.rang - carriere.date_naissance.rang - 1
    if (carriere.date_liquidation.rang < ORDONNANCE_DU_26_MARS_1982.rang
            or mois < 12 * 60):
        return None
    annee = ORDONNANCE_DU_26_MARS_1982.annee - 1
    ancienne = moteur.catalogue[periode.regime].periode(annee)
    if ancienne is None or not ancienne.majoration_d_ajournement:
        return None
    coefficient, age_annulation, _ = decote_opposable(moteur, ancienne, carriere, annee)
    if not coefficient:
        return None
    ecoules = int((mois / 12.0 - age_annulation + 1e-9) * 4)
    if ecoules <= 0:
        return None
    return (ancienne.taux_plein or 0.5) * (1.0 + coefficient * ecoules)


def trimestres_d_ajournement(carriere: Carriere, age_taux_plein: float) -> int:
    """Les trimestres entiers écoulés entre l'âge du taux plein et la date
    d'effet de la pension.

    « Les trimestres d'ajournement se décomptent : du 1er jour du mois qui
    suit le 65ème anniversaire (ou à partir du jour anniversaire pour les
    assurés nés le 1er jour d'un mois), jusqu'à la date fixée pour le point
    de départ de la pension » (circulaire Cnav n° 8/89, point 12 ; n° 2004/20,
    point 12) ; depuis 2011, de l'âge du taux plein de la génération. C'est
    le premier mois où l'âge est révolu (:meth:`Carriere.date_de_l_age`).
    """
    debut = carriere.date_de_l_age(age_taux_plein)
    return max(0, (carriere.date_liquidation.rang - debut.rang) // 3)


def duree_majoree_apres_taux_plein(moteur, periode: PeriodeRegime, carriere: Carriere,
                                   durees, membres: tuple[str, ...],
                                   trimestres_regime: int, proratisation: int,
                                   age_annulation: float | None) -> int:
    """La durée du régime, majorée de 2,5 % par trimestre d'ajournement au-delà
    de l'âge du taux plein, pour qui n'a pas la durée.

    **La règle remplace l'ajournement au 1er avril 1983.** « L'assuré âgé de
    plus de soixante-cinq ans et qui ne justifie pas de 150 trimestres
    d'assurance dans le régime général de la sécurité sociale bénéficie […]
    d'une majoration de sa durée d'assurance dans ce régime égale à 2,5 p.
    100 par trimestre postérieur à son soixante-cinquième anniversaire sans
    que cette majoration puisse avoir pour effet de porter au-delà de 150
    trimestres sa durée d'assurance », le total « arrondi au chiffre
    immédiatement supérieur » (décret n° 45-0179, article 70-6, puis R.
    351-7 ; décret n° 50-1225, article 55-6, aux salariés agricoles). Elle
    est « indépendante du fait d'avoir exercé ou non une activité
    professionnelle » après l'âge (circulaire Cnav n° 22/83, point 312) :
    c'est le temps écoulé qui compte (:func:`trimestres_d_ajournement`), et
    la circulaire n° 8/89 en donne l'exemple, 80 trimestres, 21 trimestres
    d'ajournement, « 80 + (80 x 52,50 %) = 122 ». Depuis 2011, l'âge est
    celui du taux plein de la génération, que la décote lit
    (``age_annulation``).

    **Depuis 2004, la durée de tous les régimes** (``duree_majoree_tous_regimes``) :
    la majoration n'est due que « tant qu'ils n'ont pas accompli dans le
    régime général et, le cas échéant, dans un ou plusieurs autres régimes
    obligatoires, une durée totale d'assurance au moins égale à la limite »
    (L. 351-6), et « les trimestres d'assurance de chaque régime se
    totalisent même s'ils se superposent » (circulaire n° 2004/20, point
    3215). La durée majorée du régime reste bornée à la limite, la durée de
    proratisation ; et quand la durée tous régimes ainsi corrigée la dépasse,
    un régime aligné liquidé à part des autres ne reçoit que sa part de ce
    qui manque aux régimes alignés, « la différence entre la limite […] et
    la durée totale d'assurance de l'assuré, avant majoration, dans ces
    régimes » multipliée par « le rapport entre la durée d'assurance
    accomplie dans ce régime […] et la durée totale d'assurance accomplie
    par l'assuré dans l'ensemble de ces régimes », arrondie au plus proche
    (R. 173-4-2). La circulaire n° 2004/20 (point 45) en donne cinq
    exemples : 140 trimestres au régime général et 5 chez les salariés
    agricoles, majorés de 5 %, font 147 au régime général, que le partage
    ramène à 145. Un régime spécial ne partage rien : 59 trimestres au
    régime général et 90 dans un régime spécial en font 62 et 90.
    """
    if not periode.duree_majoree_apres_taux_plein or age_annulation is None:
        return trimestres_regime
    ajournement = trimestres_d_ajournement(carriere, age_annulation)
    limite = proratisation
    if ajournement <= 0 or trimestres_regime >= limite:
        return trimestres_regime
    durees_de_base = {
        code: nombre for code, nombre in durees.trimestres_par_regime.items()
        if code in moteur.catalogue
        and moteur.catalogue[code].etage in ("base", "integre") and nombre > 0
    }
    hors_regime = somme_ordonnee(nombre for code, nombre in durees_de_base.items()
                      if code not in membres)
    if periode.duree_majoree_tous_regimes and trimestres_regime + hors_regime >= limite:
        return trimestres_regime
    # 2,5 %, c'est un quarantième : le calcul en entiers évite que 140 × 1,05
    # ne s'arrondisse à 148.
    majores = min(-(-trimestres_regime * (40 + ajournement) // 40), limite)
    if periode.duree_majoree_tous_regimes:
        alignes = {code: nombre for code, nombre in durees_de_base.items()
                   if code in coordonner.REGIMES_ALIGNES}
        if (any(code not in membres for code in alignes)
                and majores + hors_regime > limite):
            total_alignes = somme_ordonnee(alignes.values()) + (
                trimestres_regime - somme_ordonnee(alignes.get(code, 0) for code in membres))
            numerateur = (limite - total_alignes) * trimestres_regime
            part = (2 * numerateur + total_alignes) // (2 * total_alignes)
            majores = min(majores, trimestres_regime + max(0, part))
    return majores


def retranche_decote(moteur, periode: PeriodeRegime, carriere: Carriere) -> int:
    """Trimestres retranchés à la durée requise pour compter la décote."""
    propre = ouvrir.duree_propre(moteur, periode, carriere)
    return 0 if propre is None else propre[1]


def valeur_point_fiche(moteur, periode: PeriodeRegime, annee: int) -> float:
    """Valeur de service du point écrite dans la fiche, à l'année demandée.

    La MSA est seule à publier celle de sa retraite proportionnelle — ni le
    code rural, ni les barèmes IPP, ni OpenFisca ne la portent —, et elle le
    fait dans un communiqué annuel. Une ancre datée suffit : la loi
    (L. 161-23-1) revalorise cette valeur sur les prix, et c'est donc l'index
    des prix qui la porte d'une année à l'autre.
    """
    if periode.valeur_point_euros is None:
        return 0.0
    return periode.valeur_point_euros * moteur.macro.coefficient_prix(
        periode.valeur_point_annee or annee, annee
    )


def abattement_points(moteur, periode: PeriodeRegime, carriere: Carriere,
                       trimestres: int, requis: int,
                       age_liquidation: float,
                       annee_liquidation: int,
                       trimestres_regime: int = 0,
                       handicap: bool = False) -> float:
    """Coefficient d'un régime en points : abattu avant le taux plein,
    majoré après.

    Il ne dépassait jamais un, et c'était un droit manquant : voir
    :func:`surcote_points`, qui rend la majoration que la fiche écrit
    quand l'abattement est revenu à un. ``trimestres_regime`` est la durée
    d'affiliation à ce régime-là, que la CIPAV oppose à sa surcote.
    ``handicap`` dit la liquidation ouverte par le départ anticipé des
    assurés handicapés : le régime général la sert au taux plein (L. 351-8,
    4° bis), et l'Agirc-Arrco, l'Ircantec et la complémentaire des
    indépendants le suivent sans coefficient.

    « Avant le taux plein » est une condition de DURÉE autant que d'âge :
    une complémentaire est servie sans abattement dès que l'assuré a le
    taux plein au régime de base, même s'il liquide avant l'âge d'annulation
    de la décote.

    L'Agirc-Arrco ne reprend pas la décote du régime de base : elle publie
    ses propres COEFFICIENTS D'ANTICIPATION, en deux tables — l'une indexée
    sur les trimestres manquants, l'autre sur l'âge — et retient la plus
    avantageuse pour l'assuré. Les deux ne se recoupent pas : douze
    trimestres manquants valent 0,88, quand la décote du régime de base
    n'en donnerait que 0,85 ; mais dix ans d'anticipation valent 0,43, là
    où elle en donnerait 0,50.

    **L'Ircantec a le même barème, et son texte l'écrit.** L'article 16 de
    l'arrêté du 30 décembre 1970 donne le coefficient 0,43 dix ans avant
    l'âge normal, « majoré de 0,017 5 par trimestre » jusqu'à cinq ans
    avant, de 0,012 5 par trimestre sur les deux suivantes et de 0,01 par
    trimestre sur les trois dernières : ce sont, marche pour marche, les
    paliers de l'Agirc-Arrco. Son paragraphe 2 est la seconde table —
    l'assuré qui n'a pas la durée requise se voit appliquer le même
    escalier « en assimilant à l'âge de soixante-cinq ans l'âge auquel
    [il] aurait effectivement accompli la durée d'assurance », sans
    pouvoir descendre sous le coefficient de son âge, ce qui est
    exactement « la plus avantageuse des deux ». Le modèle lui opposait
    1,1 % par trimestre, taux moyen qui tombe juste aux deux extrémités du
    barème — 0,78 à cinq ans, 1,00 à zéro — et nulle part entre les deux :
    à douze trimestres il retirait 13,2 % là où l'arrêté en retire 12.
    """
    if periode.abattement_points in ("agirc_arrco", "ircantec"):
        # AVANT L'ASF, L'ÂGE SEUL. Jusqu'à l'accord du 4 février 1983,
        # l'Agirc et l'Arrco servaient le taux plein à soixante-cinq ans et
        # abattaient toute anticipation, quelle que soit la durée : c'est
        # l'ASF qui a financé la retraite à soixante ans sans abattement
        # pour qui avait le taux plein au régime de base. Une période sans
        # durée requise — ni en dur, ni lue à la génération — porte ce
        # droit-là, et la table par durée ne s'y consulte pas.
        par_age_seul = (
            periode.duree_requise_trimestres is None
            and not periode.duree_requise_par_generation
        )
        # L'INAPTE A LE TAUX PLEIN AU RÉGIME GÉNÉRAL, et la complémentaire le
        # suit : « sans coefficient » pour qui a obtenu la pension du régime
        # général ou agricole « à taux plein » (accord du 17 novembre 2017,
        # article 84, 3 ; avant lui, depuis 1983, les accords de l'ASF) ;
        # « Toutefois, ce coefficient de réduction n'est pas applicable : 1°
        # Dans le cas d'une inaptitude au travail reconnue entre soixante et
        # soixante-cinq ans par la sécurité sociale », dès 1971 à l'Ircantec
        # (arrêté du 30 décembre 1970, article 16), l'âge suivant ensuite
        # celui de l'inapte.
        inapte = ((not par_age_seul or periode.abattement_points == "ircantec")
                  and invalidite.taux_plein_de_l_inapte(
                      moteur, invalidite.REGIME_DES_SALARIES, carriere, age_liquidation))
        # LE DÉPART ANTICIPÉ DES ASSURÉS HANDICAPÉS, au taux plein du régime
        # général, que l'Agirc-Arrco suit « à l'âge auquel il a obtenu la
        # pension [...] à taux plein » (accord du 17 novembre 2017, article
        # 84, 3), et que l'Ircantec exempte de coefficient : « b) Les agents et
        # anciens agents handicapés admis à faire liquider leur retraite au
        # régime général en application de l'article L. 351-1-3 » (arrêté du
        # 30 décembre 1970, article 16).
        if inapte or handicap or (not par_age_seul and trimestres >= requis):
            abattement = 1.0
        else:
            par_duree = (
                None if par_age_seul
                else _coefficient_anticipation(requis - trimestres, 20)
            )
            par_age = coefficient_pour_age(moteur, periode, carriere, age_liquidation)
            candidats = [c for c in (par_duree, par_age) if c is not None]
            abattement = max(candidats) if candidats else 1.0
    elif periode.abattement_points in _ABATTEMENTS_IRCEC:
        abattement = abattement_ircec(moteur, 
            periode, carriere, trimestres, requis,
            age_liquidation, annee_liquidation,
        )
    else:
        abattement = abattement_regime_de_base(moteur,
            periode, carriere, trimestres, requis,
            age_liquidation, annee_liquidation, handicap,
        )
    if abattement < 1.0 and taux_plein_anticipe(moteur, 
            periode, carriere, age_liquidation):
        abattement = 1.0

    if abattement < 1.0:
        # ABATTU ET MAJORÉ NE SE RENCONTRENT PAS. Les deux majorations de
        # l'arrêté supposent l'une l'âge du taux plein dépassé, l'autre la
        # durée requise dépassée — c'est-à-dire, dans les deux cas, un
        # coefficient d'anticipation déjà revenu à 1. L'écrire coûte une
        # ligne et dispense de s'en convaincre à chaque lecture.
        return abattement
    return surcote_points(moteur, 
        periode, carriere, trimestres, requis,
        age_liquidation, annee_liquidation, trimestres_regime,
    )


def coefficient_pour_age(moteur, periode: PeriodeRegime, carriere: Carriere,
                         age_liquidation: float) -> float:
    """Le coefficient d'anticipation de la table des âges : les trimestres
    qui séparent la liquidation de l'âge du taux plein de la période,
    arrondis au supérieur, et le plancher au-delà de dix ans (accord du 17
    novembre 2017, article 84, 2 ; table de septembre 2026, tableau 3)."""
    ecart_age = max(
        0.0,
        (ouvrir.age_taux_plein(moteur, periode, carriere) - age_liquidation) * 4,
    )
    par_age = _coefficient_anticipation(ecart_age, 40)
    return _COEFFICIENT_ANTICIPATION_PLANCHER if par_age is None else par_age


def taux_plein_anticipe(moteur, periode: PeriodeRegime, carriere: Carriere,
                         age_liquidation: float) -> bool:
    """Le taux plein qu'une section ouvre aux mères avant son âge.

    La CARCDSF permet « un départ anticipé à la retraite sans qu'il soit
    fait application du taux de minoration […] aux affiliées
    chirurgiens-dentistes ou sages-femmes, au titre de l'incidence sur leur
    vie professionnelle de la maternité […] à raison d'une année
    d'anticipation par enfant mis au monde, dans la limite de 5 années
    maximum » (statuts approuvés le 13 avril 2011, article 19 II, puis
    règlement du 10 juillet 2026, article 3 II) ; ses statuts de 2007
    l'écrivaient déjà, de 64 ans pour un enfant à 60 ans pour cinq.

    Les dispositions générales et particulières « sont exclusives les unes
    des autres » (article 4) : l'anticipation n'abaisse pas l'âge dont se
    compte la minoration, elle ouvre le taux plein à un âge. Une mère de
    deux enfants partie à 65 ans n'en perd rien ; partie à 64, elle est
    minorée comme tout affilié, depuis 67 ans.
    """
    if (periode.taux_plein_anticipe_par_enfant_annees is None
            or carriere.sexe != "F" or carriere.nombre_enfants <= 0):
        return False
    anticipation = (carriere.nombre_enfants
                    * periode.taux_plein_anticipe_par_enfant_annees)
    if periode.taux_plein_anticipe_maximum_annees is not None:
        anticipation = min(anticipation,
                           periode.taux_plein_anticipe_maximum_annees)
    return (age_liquidation
            >= ouvrir.age_taux_plein(moteur, periode, carriere) - anticipation - 1e-9)


def abattement_regime_de_base(moteur, periode: PeriodeRegime,
                               carriere: Carriere, trimestres: int,
                               requis: int, age_liquidation: float,
                               annee_liquidation: int,
                               handicap: bool = False) -> float:
    """Coefficient qui reprend la décote du régime de base : un taux par
    trimestre manquant, au plus favorable de l'âge et de la durée.

    **Deux pentes, quand la fiche en écrit deux.** La CAVP minore « de
    1,25 % par trimestre d'anticipation entre l'âge d'ouverture des droits
    et 65 ans ; 0,5 % par trimestre d'anticipation entre 65 ans et l'âge
    fixé au 1° de l'article L. 351-8 » (règlement approuvé le 10 juillet
    2026, article 12, déjà dans ses statuts depuis l'arrêté du 23 juin
    2011). Les trimestres d'avant le palier se comptent au premier taux,
    les autres au second : un pharmacien parti à soixante-quatre ans en
    perd quatre à 1,25 % et huit à 0,5 %, soit 9 %.

    Le régime en points que la fiche ``inaptitude_au_travail`` nomme — les
    assurances sociales d'avant 1945 — sert l'inapte sans abattement, comme
    les régimes en annuités qu'elle nomme.
    """
    if invalidite.taux_plein_de_l_inapte(moteur, periode.regime, carriere, age_liquidation):
        return 1.0
    # La complémentaire des indépendants que la fiche
    # ``retraite_anticipee_handicap`` nomme est « liquidée sans aucun
    # abattement [...] à partir de l'âge fixé aux articles L. 634-3-2 ou
    # L. 634-3-3 de ce même code si l'assuré remplit les conditions permettant
    # d'ouvrir droit à la retraite anticipée prévue par ces articles »
    # (règlement approuvé par l'arrêté du 9 février 2012, article 12).
    if handicap and periode.regime in moteur.invalidites.regimes("handicap"):
        return 1.0
    decote, age_annulation, _ = decote_opposable(moteur,
        periode, carriere, annee_liquidation
    )
    if decote is None:
        return 1.0
    trimestres_decote = trimestres_de_decote(moteur, 
        periode, carriere, trimestres, requis, age_liquidation,
        age_annulation
    )
    if (periode.decote_palier_age is not None
            and periode.decote_par_trimestre_apres_palier is not None
            and trimestres_decote > 0):
        avant = min(trimestres_decote, max(0, _au_trimestre_superieur(
            (periode.decote_palier_age - age_liquidation) * 4)))
        apres = trimestres_decote - avant
        return max(0.0, 1.0 - decote * avant
                   - periode.decote_par_trimestre_apres_palier * apres)
    return max(0.0, 1.0 - decote * trimestres_decote)


#: RACL, de 2014 à mai 2024 : l'annexe « Coefficients d'applications en cas
#: de départ en retraite avant l'âge du taux plein » de l'arrêté du 21
#: novembre 2013 (JORFARTI000028254004), pour les générations d'avant 1955 —
#: l'âge normal de liquidation, et le coefficient de un à quatre, cinq à huit,
#: neuf à douze, treize à seize, dix-sept à vingt trimestres d'anticipation.
#: « Pour les adhérents nés antérieurement au 1er janvier 1953, le
#: coefficient de minoration est égal à 6 % par année d'anticipation » avant
#: soixante-cinq ans ; 1953 et 1954, « Le tableau joint en annexe ». Les nés
#: à compter de 1955 suivent l'article 21, 5 % par année manquante.
_MINORATION_RACL_2014 = {
    1952: (65.0, (0.06, 0.12, 0.18, 0.24, 0.30)),
    1953: (65 + 8 / 12, (0.05, 0.10, 0.15, 0.21, 0.27)),
    1954: (66 + 4 / 12, (0.04, 0.08, 0.13, 0.18, 0.24)),
}


def abattement_ircec(moteur, periode: PeriodeRegime, carriere: Carriere,
                      trimestres: int, requis: int,
                      age_liquidation: float,
                      annee_liquidation: int) -> float:
    """Coefficient de minoration des trois régimes de l'IRCEC.

    Les règlements du RAAP (art. 27), du RACD (art. 21) et du RACL
    (art. 21) ne reprennent pas la décote du régime de base : ils comptent
    des ANNÉES manquantes jusqu'à l'âge du taux plein — celui du 1° de
    l'article L. 351-8 —, « 2,5 % par année pour chacune des deux premières
    années manquantes ; 5 % par année manquante supplémentaire ». Une
    année entamée compte entière : l'annexe de l'arrêté du 21 novembre
    2013 le chiffre trimestre par trimestre, un à quatre trimestres
    d'anticipation valant 2,5 %, cinq à huit 5 %, neuf à douze 10 %.

    « Toutefois, si cela est plus favorable à l'adhérent », les mêmes
    coefficients que ceux du régime de base : c'est la décote de la fiche,
    et le coefficient retenu est le plus haut des deux. La pension est
    servie sans minoration dès l'âge légal si celle du régime de base
    l'est au taux plein, c'est-à-dire dès que la durée requise est réunie.

    ``ircec_age_seul`` est le RACL de 2014 à 2024 : « 5 % par année
    manquante », sans marche à 2,5 %, sans renvoi au régime de base, et un
    taux plein que la durée n'ouvrait pas — il fallait l'âge. L'arrêté du
    13 mai 2025 l'a aligné sur les deux autres. Le modèle leur opposait à
    tous trois 1,25 % par trimestre depuis soixante-sept ans : vingt-cinq
    pour cent à soixante-deux ans pour qui n'a pas sa durée, là où l'IRCEC
    en retire vingt.

    ``cavom`` est la même règle, écrite par un autre règlement : « 5 % par
    année manquante entre l'âge auquel est demandée la liquidation […] et
    l'âge prévu au 2° », et « ce coefficient n'est pas susceptible de
    fractionnement » (règlement du régime complémentaire de la CAVOM,
    article 1er, I, 3°, approuvé par l'arrêté du 10 juillet 2026, déjà dans
    ses statuts depuis l'arrêté du 12 décembre 2024). Le texte ne dit pas
    si l'année entamée compte ; le modèle la compte, comme l'IRCEC l'écrit
    en toutes lettres. La durée d'assurance n'y ouvre pas le taux plein :
    la fiche lui opposait la décote du régime de base, que la durée
    annule, et un officier ministériel parti à l'âge légal avec sa durée
    ne perdait rien de sa complémentaire.
    """
    if (periode.abattement_points == "ircec_age_seul"
            and carriere.annee_naissance < 1955):
        # Les générations d'avant 1955 ont leur annexe : 6 % par année avant
        # soixante-cinq ans jusqu'en 1952, un tableau pour 1953 et 1954. Le
        # moteur leur opposait 5 % par année avant l'âge d'annulation de leur
        # génération.
        age_normal, bareme = _MINORATION_RACL_2014[max(carriere.annee_naissance, 1952)]
        if age_liquidation >= age_normal - 1e-9:
            return 1.0
        anticipation = _au_trimestre_superieur((age_normal - age_liquidation) * 4)
        return max(0.0, 1.0 - bareme[min(len(bareme), -(-anticipation // 4)) - 1])
    age_taux_plein = ouvrir.age_taux_plein(moteur, periode, carriere)
    age_seul = periode.abattement_points in _ABATTEMENTS_PAR_ANNEE_AGE_SEUL
    if age_liquidation >= age_taux_plein - 1e-9:
        return 1.0
    if not age_seul and trimestres >= requis:
        return 1.0
    annees = -(-_au_trimestre_superieur(
        (age_taux_plein - age_liquidation) * 4) // 4)
    if age_seul:
        propre = 1.0 - 0.05 * annees
    else:
        propre = 1.0 - 0.025 * min(annees, 2) - 0.05 * max(0, annees - 2)
    propre = max(0.0, propre)
    if age_seul:
        return propre
    return max(propre, abattement_regime_de_base(moteur, 
        periode, carriere, trimestres, requis,
        age_liquidation, annee_liquidation,
    ))


def coefficient_surcote_datee(moteur, periode: PeriodeRegime, carriere: Carriere,
                               trimestres: int, requis: int,
                               supplementaires: int, age_ouverture: float
                               ) -> tuple[float, Fiabilite | None]:
    """Coefficient de surcote, trimestre civil par trimestre civil.

    La règle est celle de la circulaire Cnav 2018-04 (point 2), que le
    modèle suivait à l'année près : la PÉRIODE DE RÉFÉRENCE commence au
    plus tard des trois — le premier jour du trimestre civil qui suit
    l'âge légal, le premier jour du mois qui suit l'acquisition de la
    durée requise, le 1er janvier 2004 — et s'achève au dernier jour du
    trimestre civil qui précède la date d'effet. Chaque trimestre civil de
    cette période compte, dans la limite des trimestres cotisés reportés
    au compte pour l'année, et au plus ``supplementaires`` en tout ; puis
    chacun prend le taux du barème à sa date. Un assuré né le 15 avril, à
    l'âge légal en avril, ne surcote qu'à partir de juillet : le modèle
    comptait avril, et servait un trimestre de trop.

    La durée acquise se lit dans l'ordre des années. Les trimestres qui ne
    tiennent à aucune année — la majoration pour enfants — sont réputés
    acquis d'emblée : ils sont dus quelle que soit la date du départ, et la
    caisse ne les date pas davantage.

    LA FONCTION PUBLIQUE COMPTE DES DURÉES, ET NON DES TRIMESTRES CIVILS.
    L. 14, III, du code des pensions retient « le nombre de trimestres
    d'assurance effectués après le 1er janvier 2004, au-delà de l'âge
    [légal] et en sus du nombre de trimestres nécessaire » : la période
    s'ouvre le jour où les conditions sont réunies, et se découpe en
    trimestres de durée dont seuls les entiers comptent. La CNRACL en donne
    l'exemple : l'agent né le 1er janvier 1962, à l'âge légal le 1er juillet
    2024, qui travaille jusqu'au 31 décembre 2025, a « effectué 6
    trimestres supplémentaires de services effectifs à partir du
    01/07/2024 ». La règle du régime général, que le modèle lui appliquait,
    n'ouvre la période qu'au trimestre civil suivant : partie en février
    2026 après un âge légal atteint à la mi-octobre 2024, une fonctionnaire
    a quinze mois de services au-delà, cinq trimestres entiers, et le
    modèle lui en comptait quatre.

    Le modèle datant au mois, la période s'ouvre au premier mois où l'âge
    est révolu : celui qui suit l'anniversaire — service-public.gouv.fr
    l'écrit pour un fonctionnaire né le 9 octobre 1964, « taux plein à 62 ans
    et 9 mois (1er août 2027) » —, ou celui-ci pour qui est né un 1er,
    comme l'agent de la CNRACL. Le trimestre civil du régime général, lui,
    suit celui où tombe l'anniversaire.
    """
    annee_liquidation = carriere.annee_liquidation
    date_legal = carriere.mois_de_l_anniversaire(age_ouverture)
    en_duree = periode.regime in coordonner.REGIMES_CODE_DES_PENSIONS
    trimestre_legal = (date_legal.mois - 1) // 3
    debut_age = (carriere.date_de_l_age(age_ouverture) if en_duree
                 else DateMois(date_legal.annee, 1).plus_mois(3 * (trimestre_legal + 1)))

    par_annee = carriere.trimestres_par_annee(
        ligne for ligne in carriere.lignes if ligne.annee <= annee_liquidation
    )
    cotises_par_annee = carriere.trimestres_par_annee(
        ligne for ligne in carriere.lignes
        if ligne.cotise and ligne.annee <= annee_liquidation
    )
    acquis = trimestres - somme_ordonnee(par_annee.values())
    debut_duree = None
    if acquis >= requis:
        debut_duree = moteur.SURCOTE_DEPUIS
    for annee in sorted(par_annee):
        if debut_duree is not None:
            break
        valides = par_annee[annee]
        if acquis + valides >= requis:
            manquants = requis - acquis
            debut_duree = DateMois(annee, 1).plus_mois(3 * manquants)
        acquis += valides
    if debut_duree is None:
        return 1.0, None
    debut = DateMois.depuis_rang(max(
        debut_age.rang, debut_duree.rang, moteur.SURCOTE_DEPUIS.rang
    ))
    # Le trimestre de départ est ramené au trimestre civil qui le
    # contient s'il commence en cours de trimestre : la durée acquise au
    # 30 juin ouvre la période au 1er juillet, celle acquise au 31 mai
    # l'ouvre au 1er juin, mais un trimestre civil ne se compte qu'entier.
    # La fonction publique, qui compte des durées, n'arrondit pas.
    if (debut.mois - 1) % 3 and not en_duree:
        debut = DateMois(debut.annee, 1).plus_mois(3 * ((debut.mois - 1) // 3 + 1))
    fin = carriere.date_liquidation
    date_65 = carriere.mois_de_l_anniversaire(moteur.SURCOTE_AGE_MAJORE)
    trimestre_65 = (date_65.annee, (date_65.mois - 1) // 3)

    dates: list[tuple[DateMois, bool]] = []
    restants_par_annee = dict(cotises_par_annee)
    courant = debut
    while courant.rang + 2 < fin.rang and len(dates) < supplementaires:
        if restants_par_annee.get(courant.annee, 0) > 0:
            restants_par_annee[courant.annee] -= 1
            apres_65 = (courant.annee, (courant.mois - 1) // 3) > trimestre_65
            # Un trimestre de durée est accompli à son dernier mois, et
            # c'est le taux de ce mois-là qu'il prend : celui de novembre
            # 2008 à janvier 2009 est au 1,25 % de la LFSS pour 2009.
            dates.append((courant.plus_mois(2) if en_duree else courant, apres_65))
        courant = courant.plus_mois(3)
    if not dates:
        return 1.0, None
    if not moteur.surcote_baremes.connait(periode.surcote_bareme or ""):
        return 1.0 + (periode.surcote_par_trimestre or 0.0) * len(dates), None
    return moteur.surcote_baremes.coefficient(periode.surcote_bareme, dates)


def surcote_points(moteur, periode: PeriodeRegime, carriere: Carriere,
                    trimestres: int, requis: int,
                    age_liquidation: float,
                    annee_liquidation: int,
                    trimestres_regime: int = 0) -> float:
    """Majoration d'un régime en points liquidé APRÈS le taux plein.

    Trois façons de compter, parce que les textes en écrivent trois, et la
    fiche dit laquelle par ``surcote_points`` :

    ``regime_general`` — la règle de l'article L. 351-1-2, mot pour mot
    celle que la branche en annuités sert : trimestres COTISÉS « après
    l'âge prévu au premier alinéa de l'article L. 351-1 et au-delà de la
    limite mentionnée au deuxième alinéa du même article ». C'est celle du
    régime de base des professions libérales — R. 643-8, 0,75 % par
    trimestre depuis 2004, 1,25 % pour les trimestres accomplis à compter
    du 1er septembre 2023 — et celle des exploitants agricoles (D. 732-42).
    Le militaire n'en a aucune, et le décompte part de l'âge légal de droit
    commun, comme là-bas.

    ``par_age_seul`` — les statuts des sections libérales ne comptent ni
    durée ni cotisation, seulement le TEMPS : « 1,25 % par trimestre
    séparant le premier jour du trimestre civil suivant celui où le médecin
    atteint cet âge de la date d'effet de la retraite » (CARMF, art. 15),
    « par trimestre civil entier d'ajournement postérieur à l'âge du taux
    plein dans la limite de vingt trimestres » (CARPIMKO, art. 12 ter),
    « par trimestre plein de prorogation au-delà de cet âge, dans la limite
    maximale de 25 % » (CAVEC, art. 13). Le décompte part de
    ``surcote_age_debut``, ou de l'âge du taux plein lu à la génération ;
    il s'arrête à ``surcote_age_maximum`` — le soixante-dixième
    anniversaire, chez les médecins et les notaires — et à
    ``surcote_trimestres_maximum`` ; il ne retient que des multiples de
    ``surcote_pas_trimestres`` quand le texte dit « par année pleine » ;
    il change de taux à ``surcote_palier_age`` — 0,75 % au lieu de 1,25 %
    après soixante-cinq ans, à la CARMF et à l'ASV — ; et il n'est dû
    qu'au-delà de ``surcote_affiliation_minimale_trimestres`` d'affiliation
    au régime, « si, à 67 ans, vous réunissez 30 années d'affiliation à la
    Cipav ».

    ``ircantec`` — le IV de l'article 16 de l'arrêté du 30 décembre 1970,
    paragraphe 4 dans la version que le décret du 23 septembre 2008 a
    introduite « à compter du 1er janvier 2010 », majore le total des
    points de DEUX façons qui ne se recouvrent pas : 1° « 0,75 % par
    trimestre entier écoulé entre le soixante-cinquième anniversaire de
    l'assuré et la date d'entrée en jouissance de la pension » — du temps
    écoulé, comme ``par_age_seul`` ; 2° « 0,625 % par trimestre accompli »
    de durée cotisée au-delà de l'âge légal et de la durée requise, en deçà
    de ce même âge — l'assiette de ``regime_general``, bornée en haut par
    l'âge où le 1° prend le relais, car « en aucun cas une même période ne
    peut donner lieu à la fois » aux deux.

    Le modèle ne servait que la troisième : la branche en points ne lisait
    pas ``surcote_par_trimestre``, et neuf fiches de non-salariés en
    écrivaient une pour rien.
    """
    mode = periode.surcote_points
    if mode == "aucune":
        return 1.0
    if mode == "rafp":
        # Le RAFP module sa valeur de service par un barème d'âge, sans
        # taux par trimestre, au mois près : 1,08 à 64 ans, 1,10 à 64 ans
        # et 6 mois, 1,22 à 67, 1,40 à 70 — 1,18 à 64 ans avant mars 2015.
        return majoration_rafp(age_liquidation, carriere.date_de_l_age(age_liquidation))
    if mode == "ircantec":
        return surcote_ircantec(moteur, 
            periode, carriere, trimestres, requis,
            age_liquidation, annee_liquidation,
        )
    taux = periode.surcote_par_trimestre
    if not taux:
        return 1.0
    if mode == "regime_general":
        supplementaires = max(0, trimestres - requis)
        age_ouverture = ouvrir.age_ouverture_commun(moteur, periode, carriere)
        if (supplementaires <= 0 or age_liquidation < age_ouverture
                or ouvrir.droit_militaire(moteur, periode, carriere) is not None):
            return 1.0
        supplementaires = min(
            supplementaires,
            _trimestres_cotises_apres(carriere, age_ouverture, annee_liquidation),
        )
        return 1.0 + taux * supplementaires
    if mode != "par_age_seul":
        raise ValueError(f"surcote_points inconnu : {mode!r}")

    minimum = periode.surcote_affiliation_minimale_trimestres
    if minimum is not None and trimestres_regime < minimum:
        return 1.0
    debut = periode.surcote_age_debut
    if debut is None:
        debut = ouvrir.age_taux_plein(moteur, periode, carriere)
    if periode.surcote_depuis_la_duree:
        par_la_duree = age_de_la_duree_atteinte(moteur, periode, carriere,
                                                trimestres, requis, age_liquidation)
        if par_la_duree is not None:
            debut = min(debut, par_la_duree)
    fin = age_liquidation
    if periode.surcote_age_maximum is not None:
        fin = min(fin, periode.surcote_age_maximum)
    if periode.age_table:
        # La borne que le règlement écrit par génération : la CAVP s'arrête
        # à soixante-six ans pour les nés de juillet 1951 à 1952, à
        # soixante-huit pour ceux de 1953 à 1955, et ne majore rien avant.
        borne = moteur.ages_regimes.age_surcote_maximum(
            periode.age_table, carriere.generation)
        if borne is not None:
            fin = min(fin, borne)
    # Des trimestres civils ENTIERS : deux mois de plus ne valent rien.
    ecoules = int((max(0.0, fin - debut) + 1e-9) * 4)
    if periode.surcote_trimestres_cotises:
        # « Pour chaque année pleine COTISÉE dans le présent régime »
        # (CAVAMAC, statuts dans la rédaction de l'arrêté du 4 août 2023,
        # article 16) : le temps écoulé sans cotiser ne compte plus.
        ecoules = min(ecoules, _trimestres_cotises_apres(
            carriere, debut, annee_liquidation))
    if periode.surcote_trimestres_maximum is not None:
        ecoules = min(ecoules, periode.surcote_trimestres_maximum)
    pas = max(1, periode.surcote_pas_trimestres)
    ecoules -= ecoules % pas
    if ecoules <= 0:
        return 1.0
    palier = periode.surcote_palier_age
    if palier is None or periode.surcote_par_trimestre_apres_palier is None:
        return 1.0 + taux * ecoules
    avant_palier = min(ecoules, max(0, int((palier - debut + 1e-9) * 4)))
    return (1.0
            + taux * avant_palier
            + periode.surcote_par_trimestre_apres_palier
            * (ecoules - avant_palier))


def age_de_la_duree_atteinte(moteur, periode: PeriodeRegime, carriere: Carriere,
                             trimestres: int, requis: int,
                             age_liquidation: float) -> float | None:
    """Le premier âge, depuis l'âge légal de droit commun et de trimestre en
    trimestre, où la durée d'assurance atteint la durée requise ; ``None`` si
    elle ne l'atteint pas avant la liquidation.

    La CARPIMKO majore la pension « lorsque la liquidation de la retraite est
    ajournée au-delà de l'âge auquel elle aurait pu être liquidée sans
    abattement », et sert le taux plein « à partir de l'âge prévu à l'article
    L. 161-17-2 […] au profit des assurés remplissant les conditions leur
    permettant de liquider leur pension du régime de base sans abattement »
    (règlement de 2026, articles 5 et 3 ; statuts de 2015, articles 12 ter et
    11). La caisse écrit la surcote « au-delà de 62 ans […] si l'affilié a
    effectué le nombre de trimestres requis ». Le moteur la comptait de l'âge
    du taux plein de sa table, soixante-sept ans depuis la génération 1961.
    La durée à un âge est celle de la liquidation, moins ce que les lignes de
    la carrière ont validé depuis, au mois près.
    """
    legal = ouvrir.age_ouverture_commun(moteur, periode, carriere)
    fin = carriere.date_de_l_age(age_liquidation)
    trimestre = 0
    while True:
        age = legal + trimestre / 4.0
        debut = carriere.date_de_l_age(age)
        if debut.rang >= fin.rang:
            return None
        depuis = somme_ordonnee(trimestres_de_la_ligne_entre(carriere, ligne, debut, fin)
                     for ligne in carriere.lignes)
        if trimestres - depuis + 1e-9 >= requis:
            return age
        trimestre += 1


def surcote_ircantec(moteur, periode: PeriodeRegime, carriere: Carriere,
                      trimestres: int, requis: int,
                      age_liquidation: float,
                      annee_liquidation: int) -> float:
    """Les deux taux du IV de l'article 16 — voir :func:`surcote_points`."""
    age_taux_plein = ouvrir.age_taux_plein(moteur, periode, carriere)

    # 1° — LE TEMPS ÉCOULÉ, en trimestres ENTIERS : l'arrêté le dit, et
    # deux mois de plus ne valent rien.
    ecoules = int((max(0.0, age_liquidation - age_taux_plein) + 1e-9) * 4)

    # 2° — LA DURÉE COTISÉE EN DEÇÀ. Les trimestres au-delà de la durée
    # requise sont les DERNIERS de la carrière : les compter ici suppose
    # donc que la durée requise était déjà atteinte avant l'âge du taux
    # plein, sans quoi ils tombent dans la fenêtre du 1° et y sont déjà
    # payés.
    supplementaires = 0
    age_ouverture = ouvrir.age_ouverture_commun(moteur, periode, carriere)
    if age_liquidation >= age_ouverture:
        cotises, avant = _fenetre_ircantec(
            carriere, trimestres, age_ouverture, age_taux_plein, age_liquidation)
        supplementaires = max(0, avant - requis)
        if supplementaires > 0:
            supplementaires = min(supplementaires, cotises)
    return (1.0
            + _SURCOTE_IRCANTEC_AGE * ecoules
            + _SURCOTE_IRCANTEC_DUREE * supplementaires)


def _trimestres_cotises_apres(carriere: Carriere, age: float,
                              annee_liquidation: int) -> int:
    """Trimestres cotisés à partir de l'année où l'assuré atteint ``age``.

    Seuls ceux-là ouvrent droit à la surcote : c'est une récompense du travail
    prolongé, pas de l'entrée précoce dans la vie active.
    """
    return carriere.trimestres_cumules(
        ligne
        for ligne in carriere.lignes
        if ligne.cotise
        and ligne.annee <= annee_liquidation
        and ligne.annee - carriere.annee_naissance >= age
    )


def _fenetre_ircantec(carriere: Carriere, trimestres: int, age_bas: float,
                      age_haut: float, age_liquidation: float) -> tuple[int, int]:
    """La fenêtre du 2° de la surcote de l'Ircantec : les trimestres cotisés
    de l'âge d'ouverture à l'âge du taux plein, et la durée d'assurance que
    les lignes de la carrière atteignent à la fin de la fenêtre, bornée par
    celle de la liquidation.

    Elle se compte d'anniversaire à anniversaire, au mois près, comme le 1°,
    un trimestre valant une période de quatre-vingt-dix jours ; et « lorsque
    le trimestre ayant donné lieu à cotisation débute avant l'âge prévu au 1°
    et se termine après l'atteinte de ce même âge, le trimestre accompli est
    pris en compte dans la durée d'assurance donnant lieu à la majoration du
    total des points prévus au présent 2° » (arrêté du 30 décembre 1970,
    article 16, IV, rédaction du 14 septembre 2023) : la fenêtre que l'âge du
    taux plein ferme compte son trimestre entamé. Le moteur la comptait par
    année civile, à l'âge atteint dans l'année : jusqu'à deux trimestres
    d'écart à chaque bout.
    """
    debut = carriere.date_de_l_age(age_bas)
    borne = carriere.date_de_l_age(age_haut)
    fin = carriere.date_de_l_age(age_liquidation)
    # L'âge du taux plein ferme la fenêtre quand son anniversaire précède la
    # date d'effet, même si celle-ci tombe au premier mois qui le suit.
    fermee = carriere.mois_de_l_anniversaire(age_haut).rang < fin.rang
    haut = borne if fermee else fin

    def compte(total: float) -> int:
        return int(math.ceil(total - 1e-9)) if fermee else int(total + 1e-9)

    cotises = compte(somme_ordonnee(trimestres_de_la_ligne_entre(carriere, ligne, debut, haut)
                         for ligne in carriere.lignes if ligne.cotise))
    origine = DateMois(carriere.annee_naissance, 1)
    avant = compte(somme_ordonnee(trimestres_de_la_ligne_entre(carriere, ligne, origine, haut)
                       for ligne in carriere.lignes))
    return cotises, min(trimestres, avant)


def _assiette_de_reference(periode: PeriodeRegime, ligne) -> float:
    """Part de la rémunération que ce régime prend en compte.

    Même découpage que dans la boucle de cotisation : un régime qui ne cotise
    que sur le traitement indiciaire ne peut pas liquider sur la rémunération
    primes comprises, sans quoi les primes ouvriraient deux fois des droits —
    au RAFP et à la pension civile — alors qu'elles n'en ouvrent qu'au RAFP.
    """
    return periode.part_du_revenu(ligne.revenu, ligne.part_primes)
