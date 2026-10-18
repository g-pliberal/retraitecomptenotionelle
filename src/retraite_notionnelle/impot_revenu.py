"""L'impôt sur le revenu d'un foyer, de son barème à son montant, chaque année.

Le dépôt ne calculait aucun impôt sur le revenu : le site affiche un net
« avant impôt sur le revenu », les indicateurs de cycle de vie s'arrêtent aux
prélèvements sociaux, la page Coût n'a pas d'effet retour par l'impôt (action
138, étape 5). Ce module calcule l'impôt d'un FOYER pour les revenus d'une
année, de 1960 à la dernière loi de finances lue, et au-delà sur un barème
projeté (:mod:`~retraite_notionnelle.donnees.impot_revenu`). Les indicateurs
de cycle de vie le prennent, après impôt
(:func:`~retraite_notionnelle.cycle_de_vie.convention_apres_impot`) ; le site
et la page Coût le prendront plus tard.

LE FOYER. Une personne seule — célibataire, divorcée ou veuve — ou un couple
marié ou pacsé, imposé en commun ; des enfants à charge ou non ; des salaires,
des bénéfices d'indépendant et des pensions imposables, c'est-à-dire déjà nets de la CSG déductible de
leur année (:func:`~retraite_notionnelle.cycle_de_vie.revenus_imposables`,
:func:`~retraite_notionnelle.cycle_de_vie.parts_imposables_par_annee`) : ce
module part du net imposable. Chaque déclarant dit son âge au 31 décembre de
l'année des revenus, pour l'abattement des personnes âgées, et s'il est
invalide.

CE QU'IL REND. L'impôt, et chacune des étapes qui y mènent, et le revenu
fiscal de référence (CGI, art. 1417, IV), qui servira à la CSG des pensions :
pour un foyer qui n'a que des salaires et des pensions, c'est le revenu net
imposable, abattement des personnes âgées déduit.

LES ÉTAPES, dans l'ordre de l'article 193 du code et de ses rédactions
successives :

1. les revenus nets : les salaires, moins 10 % de frais professionnels (CGI,
   art. 83, 3°), bornés par personne ; les pensions, moins 10 % (art. 158, 5,
   a), au moins un minimum par pensionné, au plus un maximum par foyer ;
   jusqu'aux revenus de 2005, 80 % seulement de leur somme, l'abattement de
   20 % s'appréciant pour chaque membre du foyer jusqu'à sa limite (DB 5 F
   3122) ; les bénéfices d'un indépendant, sans frais professionnels, réduits
   de l'abattement des adhérents d'un organisme de gestion agréé de 1976 à
   2005, majorés pour qui n'y adhère pas de 2006 à 2022
   (:func:`benefice_retenu`) ;
2. le revenu net global, puis l'abattement des personnes de plus de 65 ans ou
   invalides (art. 157 bis), le revenu net imposable, arrondi ;
3. le nombre de parts (art. 194 et 195) : un, deux pour un couple ou un veuf
   ayant un enfant à charge, une demi-part par enfant, une part entière par
   enfant à partir du troisième (selon les années :
   ``parts_par_rang_d_enfant``), une demi-part au parent qui vit seul avec ses
   enfants (case T), une demi-part par déclarant invalide ;
4. l'impôt brut du barème, par part, multiplié par les parts ; depuis 1981, le
   plafonnement des effets du quotient familial, et les réductions
   complémentaires de l'invalide (depuis 1998) et du veuf (depuis 2012) ;
5. la décote, dont la règle a changé six fois (:func:`decote`) ; la réduction
   sous condition de revenus de 2016 à 2019 ; les majorations et minorations
   exceptionnelles des années 1960 à 1992 ; la réduction exceptionnelle des
   revenus de 2013 ; les 5 % retranchés de l'impôt des revenus de 2001 ;
6. l'exonération du foyer dont le revenu, net de frais professionnels,
   n'excède pas la limite de l'année, de 1973 à 2013 (:func:`exonere`) ; le
   seuil de mise en recouvrement ; la prime pour l'emploi de 2000 à 2014,
   sur le revenu d'activité de chacun — ses salaires, son bénéfice majoré de
   11,11 % (:func:`revenus_de_la_prime`) —, et le crédit d'impôt exceptionnel
   des revenus de 2008, restitués au-delà de l'impôt dû, en entier au foyer
   qui n'est pas imposable.

LES MONNAIES ET LES ARRONDIS. L'impôt d'une année en francs se calcule en
francs : ``unite="euro"`` (le défaut) prend et rend des euros, convertis au
taux légal ; ``unite="monnaie"`` prend et rend la monnaie de l'année. Les
arrondis suivent le code : le revenu imposable à la dizaine de francs
inférieure jusqu'aux revenus de 1997 (art. 193), au franc, puis à l'euro, le
plus proche ensuite, ainsi que chaque élément qui y concourt ; l'impôt au
franc le plus proche depuis 1979, à la dizaine de centimes avant (art. 1657,
1), puis à l'euro le plus proche.

CE QU'IL NE FAIT PAS, et que :data:`HORS_CHAMP` énumère : les revenus autres
que les salaires, les bénéfices et les pensions, le bénéfice des régimes micro
(qu'on lui donne déjà réduit de son abattement forfaitaire), les charges
déductibles, les réductions et
crédits d'impôt autres que la prime pour l'emploi, les réductions de 2001 et
de 2013 et le crédit de 2008, les demi-parts des anciens combattants et de
qui vit seul après avoir élevé un enfant (case L), les enfants en résidence
alternée ou majeurs rattachés, les départements d'outre-mer, la contribution
exceptionnelle sur les hauts revenus, le travail à temps partiel de la prime
pour l'emploi (le foyer travaille à temps plein, toute l'année), le seuil
sous lequel une restitution n'est pas faite (art. 1965 L : 50 F, puis 8 €),
l'exonération de qui vit de salaires et de pensions sous le minimum garanti
(art. 5, 2°), la déduction de 500 F des personnes âgées d'avant 1973,
l'abattement de 2 000 F des contribuables à une part de 1978 (loi n°
78-1239, art. 2, IV) et celui de l'article 157 ter.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .donnees.chargement import Fiabilite
from .donnees.impot_revenu import FRANC, BaremesImpotRevenu, ParametresImpot
from .somme import somme_ordonnee

#: Ce que le module ne calcule pas : voir l'en-tête.
HORS_CHAMP = (
    "revenus autres que les salaires, les bénéfices et les pensions",
    "abattement forfaitaire des régimes micro : le bénéfice s'entend après lui",
    "limites de chiffre d'affaires ou de recettes de l'abattement des adhérents, de 1976 à 1982",
    "charges déductibles et pensions alimentaires",
    "réductions et crédits d'impôt autres que la prime pour l'emploi, les réductions de 2001 "
    "et de 2013 et le crédit de 2008",
    "demi-parts des anciens combattants et de qui vit seul après avoir élevé un enfant (case L)",
    "enfants en résidence alternée ou majeurs rattachés",
    "abattement des départements d'outre-mer",
    "contribution exceptionnelle sur les hauts revenus",
    "temps partiel et activité sur une partie de l'année, pour la prime pour l'emploi",
    "seuil de restitution de l'article 1965 L (50 F, puis 8 €)",
    "exonération de l'article 5, 2° : salaires et pensions sous le minimum garanti",
    "déduction de 500 F des personnes âgées d'avant 1973",
    "abattement de 2 000 F des contribuables à une part de 1978, et celui de l'article 157 ter",
)

#: L'âge, atteint au 31 décembre de l'année des revenus, qui ouvre
#: l'abattement des personnes âgées : « âgé de plus de soixante-cinq ans au
#: 31 décembre de l'année d'imposition » (art. 157 bis), que l'administration
#: entend comme né avant le 1er janvier de l'année des revenus moins 64
#: (brochure pratique 2025 : « né avant le 1.1.1960 » pour les revenus 2024).
AGE_ABATTEMENT = 65

#: « Jusqu'à l'imposition des revenus 1978, cette part supplémentaire n'est
#: appliquée qu'aux enfants majeurs invalides à charge » (IPP, note de la
#: table du quotient familial) : le mineur invalide l'a depuis 1979.
PREMIERE_ANNEE_ENFANT_INVALIDE = 1979

#: La première année de revenus dont le barème plafonne l'avantage du
#: quotient familial : la loi de finances pour 1982 (art. 197, VII,
#: LEGIARTI000006308325, « Ce plafond était de 7.500 F pour l'imposition des
#: revenus de 1981 »).
PREMIERE_ANNEE_PLAFONNEMENT = 1981

#: Jusqu'aux revenus de 2004, le montant minimal de la prime pour l'emploi est
#: un plancher : « Le montant total de la prime accordée au foyer fiscal ne
#: peut être inférieur à 160 F » (art. 200 sexies, IV, LEGIARTI000006303351),
#: puis à 25 euros ; depuis les revenus de 2005, un seuil : « La prime n'est
#: pas due lorsque son montant avant imputation est inférieur à 30 Euros »
#: (LEGIARTI000006303356).
PREMIERE_ANNEE_SEUIL_DE_LA_PPE = 2005

#: Le revenu d'activité d'un non-salarié dans la prime pour l'emploi (art.
#: 200 sexies, I, B, 3°, c à e) : son bénéfice, avant l'abattement des
#: adhérents (BOI 5 B-12-01, n° 17) et la majoration de qui n'adhère pas
#: (BOI-IR-RICI-310-10-30-20130522, n° 90), « majoré de 11,11 % » (III,
#: LEGIARTI000006303351), comme le salaire y est pris avant ses frais
#: professionnels ; son déficit se déduit de ses salaires (BOI 5 B-12-01,
#: n° 15 : « il est fait masse »), « diminué [...] de 11,11 % » depuis les
#: revenus de 2001 (LEGIARTI000006303352), « multiplié par (1-0.1111) » (notice
#: 2041 GS des revenus de 2014). La majoration s'arrondit à l'unité la plus
#: proche (BOI 5 B-12-01, n° 16 : « Majoration 11,11 % = + 7 777 F »).
TAUX_NON_SALARIES_DE_LA_PPE = 0.1111
PREMIERE_ANNEE_DEFICIT_MINORE = 2001

#: LE BÉNÉFICE D'UN INDÉPENDANT (art. 158, 4 bis et 7, lus dans LEGI le 16
#: octobre 2026). Ses régimes : le réel, adhérent d'un centre ou d'une
#: association de gestion agréés (ou de ce que le 7 leur assimile, l'expert-
#: comptable conventionné), le réel sans eux, et le micro, dont le
#: bénéfice s'entend après son abattement forfaitaire et qui n'a ni
#: abattement ni majoration.
REGIMES_DU_BENEFICE = ("reel_adherent", "reel_non_adherent", "micro")

#: Ses catégories : les bénéfices industriels et commerciaux (l'artisan, le
#: commerçant), les bénéfices non commerciaux (le libéral), les bénéfices
#: agricoles.
CATEGORIES_DU_BENEFICE = ("bic", "bnc", "ba")

#: L'abattement des adhérents naît de la loi de finances rectificative pour
#: 1974 (n° 74-1114, art. 1er, III, que l'index n'a qu'en notice, lue le 17
#: octobre 2026 au texte définitif que le Sénat a adopté le 20 décembre 1974) :
#: les adhérents d'un centre de gestion agréé « placés sous un régime réel
#: d'imposition [...] bénéficient d'un abattement de 10 % sur leur bénéfice
#: imposable », sans seuil ni limite. Le décret n° 75-911 du 6 octobre 1975,
#: qui fait agréer les centres, ne l'accorde qu'à qui a été adhérent « pendant
#: toute la durée des exercices concernés », ou dont l'exercice était ouvert
#: depuis moins de trois mois à l'agrément ou à l'adhésion (art. 17,
#: LEGIARTI000006323772) : l'exercice de l'année 1975 n'y entre pas, celui de
#: 1976 le premier.
PREMIERE_ANNEE_ABATTEMENT_ADHERENTS = 1976
TAUX_ABATTEMENT_DE_1974 = 0.10
#: La loi de finances pour 1978 (n° 77-1467, texte définitif adopté par le
#: Sénat le 16 décembre 1977) porte le taux « de 10 % à 20 %, sauf pour la
#: fraction du bénéfice qui excède la limite de 150 000 F prévue à l'article
#: 6 », dès les revenus de 1977 (art. 7, II, et 1er, III), et « aucun
#: abattement n'est appliqué sur la fraction du bénéfice qui excède une fois
#: et demie la limite de la dernière tranche du barème » : 1,5 fois les
#: 238 200 F de son article 2, un barème pour deux parts, soit 357 300 F, là
#: où celle des salaires est arrondie à la dizaine de milliers de francs
#: supérieure (360 000 F). La loi de finances pour 1979 fixe les deux à
#: 360 000 F pour les revenus de 1978 et de 1979 (art. 11,
#: LEGIARTI000006273141).
PREMIERE_ANNEE_ABATTEMENT_DE_20 = 1977
SEUIL_ET_LIMITE_DE_1977 = (150000, 357300)
#: Les bénéfices non commerciaux ont le leur, de mêmes taux, seuils et
#: limites, par les associations agréées des professions libérales de la loi
#: de finances pour 1977 (art. 64) : le 4 ter de l'article 158, de sa
#: rédaction du 1er juillet 1979 (LEGIARTI000006307959, « pour l'imposition
#: des revenus de 1978 et de 1979 ») à celle du 15 juillet 1985, qui le
#: fond dans le 4 bis (LEGIARTI000006307964, revenus de 1984). Le décret
#: n° 77-1519 du 31 décembre 1977, qui les fait agréer, veut l'adhésion de
#: toute l'année, ou depuis moins de trois mois après son début (art. 16,
#: LEGIARTI000006323746) : la première est 1978.
PREMIERE_ANNEE_ABATTEMENT_BNC = 1978
#: La dernière, avant que le barème de 2006 ne l'intègre (LEGIARTI000006307988).
DERNIERE_ANNEE_ABATTEMENT_ADHERENTS = 2005

#: Jusqu'aux revenus de 1995, « le taux de l'abattement est ramené à 10 %
#: pour la fraction du bénéfice qui excède » un seuil, en francs : 150 000 F
#: pour les revenus de 1978 à 1981, 165 000 F pour ceux de 1982 et 1983, puis
#: la limite du cinquième alinéa du a du 5, celle des salaires des dirigeants
#: (de 182 000 F pour les revenus de 1984 à 469 000 F pour ceux de 1995). Chaque montant est celui de la
#: rédaction en vigueur au milieu de l'année qui suit les revenus — celle qui
#: écrit le plafond de ces revenus —, sans l'indexation annuelle que le code
#: prescrit quand une rédaction n'en écrit pas de nouveau (1988, 1992, 1993).
#: La rédaction du 11 avril 1997 (LEGIARTI000006307975, revenus de 1996)
#: supprime la fraction à 10 %.
SEUILS_ABATTEMENT_REDUIT = {
    1978: 150000, 1979: 150000, 1980: 150000, 1981: 150000,
    1982: 165000, 1983: 165000, 1984: 182000, 1985: 192200, 1986: 250000,
    1987: 320000, 1988: 320000, 1989: 413200, 1990: 426400, 1991: 440000,
    1992: 440000, 1993: 440000, 1994: 469000, 1995: 469000,
}

#: La majoration du bénéfice au réel de qui n'adhère pas (art. 158, 7, 1°) :
#: 1,25 de sa rédaction du 31 décembre 2006 (LEGIARTI000006307988, revenus de
#: 2006) aux revenus de 2019 ; puis 1,20, 1,15 et 1,10 pour les revenus de
#: 2020, 2021 et 2022 (loi n° 2020-1721, art. 34, que l'index n'a pas, lu au
#: BOFiP, BOI-IR-BASE-10-10-20-20210512, n° 55) ; abrogée « à compter de
#: l'imposition des revenus de l'année 2023 » (LEGIARTI000042978882). Un
#: déficit n'est pas majoré (même BOI, n° 90).
PREMIERE_ANNEE_MAJORATION = 2006
COEFFICIENT_MAJORATION = 1.25
COEFFICIENTS_MAJORATION_DEGRESSIFS = {2020: 1.20, 2021: 1.15, 2022: 1.10}
DERNIERE_ANNEE_MAJORATION = 2022


@dataclass(frozen=True)
class Declarant:
    """Un déclarant du foyer, ses revenus imposables de l'année et sa situation."""

    #: Salaires imposables : le brut moins les cotisations et la CSG
    #: déductible de l'année.
    salaires: float = 0.0
    #: Pensions et retraites imposables, nettes de la CSG déductible.
    pensions: float = 0.0
    #: Âge atteint au 31 décembre de l'année des revenus.
    age: int | None = None
    invalide: bool = False
    #: Bénéfice imposable d'une activité indépendante, net de ses cotisations
    #: sociales et de la CSG déductible ; négatif, un déficit.
    benefices: float = 0.0
    #: Son régime (:data:`REGIMES_DU_BENEFICE`) et sa catégorie
    #: (:data:`CATEGORIES_DU_BENEFICE`).
    regime: str = "reel_adherent"
    categorie: str = "bic"

    def __post_init__(self):
        if self.regime not in REGIMES_DU_BENEFICE:
            raise ValueError(f"régime du bénéfice inconnu : {self.regime!r}")
        if self.categorie not in CATEGORIES_DU_BENEFICE:
            raise ValueError(f"catégorie du bénéfice inconnue : {self.categorie!r}")


@dataclass(frozen=True)
class Foyer:
    """Un foyer fiscal : un déclarant, ou deux imposés en commun."""

    declarants: tuple[Declarant, ...]
    #: Enfants à charge, mineurs, à charge exclusive ou principale.
    enfants: int = 0
    #: Ceux d'entre eux qui sont titulaires de la carte d'invalidité : une
    #: demi-part de plus chacun (art. 195, 2), depuis les revenus de 1979 pour
    #: un enfant mineur (IPP, note de la table du quotient familial).
    enfants_invalides: int = 0
    #: Une personne seule veuve : le veuf qui a un enfant à charge garde la
    #: part du conjoint (art. 194, I).
    veuf: bool = False
    #: Une personne seule qui vit seule avec ses enfants : la demi-part du
    #: parent isolé (art. 194, II, case T).
    vit_seul: bool = True

    def __post_init__(self):
        if len(self.declarants) not in (1, 2):
            raise ValueError("un foyer a un déclarant, ou deux s'il est un couple")
        if self.veuf and len(self.declarants) == 2:
            raise ValueError("un couple n'est pas veuf")
        if self.enfants < 0 or not 0 <= self.enfants_invalides <= self.enfants:
            raise ValueError("un nombre d'enfants négatif, ou plus d'enfants invalides que d'enfants")

    @property
    def couple(self) -> bool:
        return len(self.declarants) == 2

    @property
    def parts_de_base(self) -> float:
        """Les parts que le plafonnement ne touche pas : une, deux pour un couple."""
        return 2.0 if self.couple else 1.0


@dataclass(frozen=True)
class ImpotDuFoyer:
    """L'impôt d'un foyer pour les revenus d'une année, étape par étape, dans
    l'unité demandée."""

    annee: int
    #: La monnaie du calcul : celle de l'année.
    monnaie: str
    #: L'unité des montants ci-dessous : ``euro`` ou ``monnaie``.
    unite: str
    parts: float
    #: Par déclarant, les salaires et les pensions après leurs abattements de
    #: 10 %, et l'abattement de 20 % qu'ils ont reçu.
    salaires_nets: tuple[float, ...]
    pensions_nettes: tuple[float, ...]
    abattement_vingt_pour_cent: float
    #: Par déclarant, le bénéfice retenu (:func:`benefice_retenu`), et, pour
    #: le foyer, l'abattement des adhérents et la majoration qu'il a reçus.
    benefices_retenus: tuple[float, ...]
    abattement_adherents: float
    majoration_des_benefices: float
    revenu_net_global: float
    abattement_age_invalidite: float
    revenu_net_imposable: float
    revenu_fiscal_de_reference: float
    #: L'impôt du barème avec toutes les parts, puis avec les seules parts de
    #: base, et l'impôt brut retenu : après plafonnement et réductions
    #: complémentaires.
    impot_sans_plafonnement: float
    impot_brut: float
    plafonnement: float
    reduction_complementaire: float
    decote: float
    reduction_sous_condition_de_revenus: float
    minoration_exceptionnelle: float
    majoration_exceptionnelle: float
    reduction_exceptionnelle: float
    reduction_proportionnelle: float
    #: La cotisation : l'impôt avant les crédits d'impôt.
    impot_avant_credits: float
    #: Par déclarant, le revenu d'activité que retient la prime pour l'emploi
    #: (:func:`revenus_de_la_prime`) ; rien hors des années de la prime.
    revenus_d_activite: tuple[float, ...]
    prime_pour_l_emploi: float
    credit_exceptionnel: float
    #: La cotisation atteint-elle le seuil de mise en recouvrement ?
    mis_en_recouvrement: bool
    #: Le foyer est-il exonéré, son revenu net de frais professionnels sous la
    #: limite de l'année (:func:`exonere`) ? Sa cotisation est alors nulle.
    exonere: bool
    #: Ce que le foyer paie ; négatif, ce qui lui est restitué.
    impot: float
    fiabilite: Fiabilite = Fiabilite.HAUTE
    #: Ce que le calcul a laissé de côté ou approché, pour ce foyer et cette année.
    remarques: tuple[str, ...] = field(default_factory=tuple)


# -- les arrondis ------------------------------------------------------------


def _au_plus_proche(valeur: float, pas: float = 1.0) -> float:
    """L'arrondi du code : la fraction égale à la moitié comptée pour un."""
    return math.floor(round(valeur / pas, 6) + 0.5) * pas


def _arrondir_element(annee: int, valeur: float) -> float:
    """Un abattement ou un revenu net : au franc, puis à l'euro le plus proche,
    depuis les revenus de 1998 (art. 193, LEGIARTI000006308269) ; au centime
    avant (art. 1657, 1 : « bases arrondies au centime de franc inférieur »)."""
    if annee >= 1998:
        return _au_plus_proche(valeur)
    return math.floor(round(valeur * 100, 6)) / 100


def _arrondir_revenu_imposable(annee: int, valeur: float) -> float:
    """Le revenu imposable : à la dizaine de francs inférieure jusqu'aux
    revenus de 1997 (art. 193, et sa rédaction de 1950 au millier d'anciens
    francs), au plus proche ensuite."""
    if annee >= 1998:
        return _au_plus_proche(valeur)
    return math.floor(round(valeur / 10, 6)) * 10.0


def _arrondir_impot(annee: int, valeur: float) -> float:
    """Une cotisation, une décote, une réduction : au franc ou à l'euro le plus
    proche depuis les revenus de 1979 (art. 1657, 1, LEGIARTI000006312651) ; à
    la dizaine de centimes avant (sa rédaction de 1950, en anciens francs)."""
    if annee >= 1979:
        return _au_plus_proche(valeur)
    return _au_plus_proche(valeur, 0.1)


# -- les étapes ----------------------------------------------------------------


def impot_du_bareme(parametres: ParametresImpot, revenu: float, parts: float) -> float:
    """L'impôt du barème : celui d'une part, multiplié par les parts, arrondi."""
    quotient = revenu / parts
    impot_par_part = 0.0
    seuils, taux = parametres.seuils, parametres.taux
    for rang, seuil in enumerate(seuils):
        haut = seuils[rang + 1] if rang + 1 < len(seuils) else math.inf
        if quotient > seuil:
            impot_par_part += (min(quotient, haut) - seuil) * taux[rang]
    return _arrondir_impot(parametres.annee, impot_par_part * parts)


def nombre_de_parts(foyer: Foyer, parametres: ParametresImpot) -> float:
    """Le quotient familial du foyer (art. 194 et 195)."""
    qf = parametres["quotient_familial"]
    parts = foyer.parts_de_base
    if foyer.veuf and foyer.enfants:
        parts += qf.get("veuf_avec_enfant", 0.0)
    parts += somme_ordonnee(parametres.parts_d_enfant(rang)
                            for rang in range(1, foyer.enfants + 1))
    if _parent_isole(foyer):
        parts += qf.get("parent_isole", 0.0)
    parts += qf.get("invalide", 0.0) * _invalidites(foyer, parametres.annee)
    return parts


def _invalidites(foyer: Foyer, annee: int) -> int:
    """Les demi-parts d'invalidité : une par déclarant invalide, une par enfant
    invalide depuis les revenus de 1979."""
    enfants = foyer.enfants_invalides if annee >= PREMIERE_ANNEE_ENFANT_INVALIDE else 0
    return _nombre(d.invalide for d in foyer.declarants) + enfants


def _nombre(drapeaux) -> int:
    """Combien de vrais."""
    return len([d for d in drapeaux if d])


def _parent_isole(foyer: Foyer) -> bool:
    return not foyer.couple and not foyer.veuf and foyer.enfants > 0 and foyer.vit_seul


def _revenus_nets(foyer: Foyer, parametres: ParametresImpot, salaires: tuple[float, ...],
                  pensions: tuple[float, ...]) -> tuple[tuple[float, ...], tuple[float, ...], float]:
    """Les salaires et pensions de chaque déclarant après leurs abattements de
    10 %, puis l'abattement de 20 % du foyer (jusqu'aux revenus de 2005)."""
    annee = parametres.annee
    d = parametres["deductions"]
    salaires_nets = []
    for salaire in salaires:
        deduction = d.get("frais_professionnels_taux", 0.0) * salaire
        if "frais_professionnels_minimum" in d:
            deduction = max(deduction, d["frais_professionnels_minimum"])
        if "frais_professionnels_maximum" in d:
            deduction = min(deduction, d["frais_professionnels_maximum"])
        deduction = _arrondir_element(annee, min(deduction, salaire))
        salaires_nets.append(salaire - deduction)
    abattements = []
    for pension in pensions:
        abattement = d.get("pensions_taux", 0.0) * pension
        if "pensions_minimum" in d:
            abattement = max(abattement, d["pensions_minimum"])
        abattements.append(min(abattement, pension))
    total = somme_ordonnee(abattements)
    if "pensions_maximum" in d and total > d["pensions_maximum"]:
        # Le maximum vaut pour le foyer : chaque pensionné en garde sa part.
        abattements = [a * d["pensions_maximum"] / total for a in abattements]
    abattements = [_arrondir_element(annee, a) for a in abattements]
    pensions_nettes = [p - a for p, a in zip(pensions, abattements)]
    vingt = 0.0
    if d.get("vingt_pour_cent_taux"):
        for salaire, pension in zip(salaires_nets, pensions_nettes):
            base = salaire + pension
            limite = d.get("vingt_pour_cent_plafond")
            assiette = base if limite is None else min(base, limite)
            abattement = d["vingt_pour_cent_taux"] * assiette
            if limite is not None and annee in (1973, 1974):
                # « Pour les revenus 1973 et 1974, les salariés avaient
                # également droit à un abattement de 10 % au-delà du plafond »
                # (IPP, note de la table des déductions).
                abattement += 0.10 * max(base - limite, 0.0)
            vingt += _arrondir_element(annee, abattement)
    return tuple(salaires_nets), tuple(pensions_nettes), vingt


def benefice_retenu(declarant: Declarant, parametres: ParametresImpot,
                    benefice: float | None = None) -> float:
    """Le bénéfice d'un déclarant tel que l'impôt le retient (art. 158) : réduit
    de l'abattement de l'adhérent d'un organisme de gestion agréé, 10 % en
    1976, 20 % de 1977 à 2005, à 10 % sur la fraction qui excède le seuil de
    l'année jusqu'en 1995 (:data:`SEUILS_ABATTEMENT_REDUIT`), et nul au-delà
    d'une limite, celle de 1977 (:data:`SEUIL_ET_LIMITE_DE_1977`), puis celle
    de l'abattement de 20 % des salaires (« la limite fixée au cinquième
    alinéa du a du 5 ») ; majoré, de 2006 à 2022, pour qui n'adhère pas. Un
    déficit, le bénéfice d'un régime micro, ceux des autres années restent
    tels quels. ``benefice``, dans la monnaie de l'année, remplace
    celui du déclarant."""
    annee = parametres.annee
    benefice = declarant.benefices if benefice is None else benefice
    if benefice <= 0.0 or declarant.regime == "micro":
        return benefice
    if declarant.regime == "reel_non_adherent":
        if not PREMIERE_ANNEE_MAJORATION <= annee <= DERNIERE_ANNEE_MAJORATION:
            return benefice
        coefficient = COEFFICIENTS_MAJORATION_DEGRESSIFS.get(annee, COEFFICIENT_MAJORATION)
        return _arrondir_element(annee, benefice * coefficient)
    return benefice - _abattement_adherent(declarant, parametres, benefice)


def _abattement_adherent(declarant: Declarant, parametres: ParametresImpot,
                         benefice: float) -> float:
    """L'abattement de l'article 158, 4 bis et 4 ter, d'un bénéfice positif
    d'adhérent, et ce qui les précède : la loi de finances rectificative pour
    1974, la loi de finances pour 1978."""
    annee = parametres.annee
    premiere = (PREMIERE_ANNEE_ABATTEMENT_BNC if declarant.categorie == "bnc"
                else PREMIERE_ANNEE_ABATTEMENT_ADHERENTS)
    if not premiere <= annee <= DERNIERE_ANNEE_ABATTEMENT_ADHERENTS:
        return 0.0
    if annee < PREMIERE_ANNEE_ABATTEMENT_DE_20:
        return _arrondir_element(annee, TAUX_ABATTEMENT_DE_1974 * benefice)
    if annee == PREMIERE_ANNEE_ABATTEMENT_DE_20:
        seuil, plafond = SEUIL_ET_LIMITE_DE_1977
    else:
        plafond = parametres["deductions"].get("vingt_pour_cent_plafond", math.inf)
        seuil = min(SEUILS_ABATTEMENT_REDUIT.get(annee, plafond), plafond)
    abattement = 0.20 * min(benefice, seuil) + 0.10 * max(min(benefice, plafond) - seuil, 0.0)
    return _arrondir_element(annee, abattement)


def _abattement_age_invalidite(foyer: Foyer, parametres: ParametresImpot,
                               revenu_net_global: float) -> float:
    """L'abattement de l'article 157 bis, par déclarant de plus de 65 ans ou
    invalide, plein ou réduit selon le revenu net global du foyer."""
    a = parametres["abattement_age_invalidite"]
    if not a:
        return 0.0
    ayants_droit = _nombre((d.age is not None and d.age >= AGE_ABATTEMENT) or d.invalide
                            for d in foyer.declarants)
    if revenu_net_global <= a["seuil_plein"]:
        montant = a["abattement_plein"]
    elif revenu_net_global <= a["seuil_reduit"]:
        montant = a["abattement_reduit"]
    else:
        montant = 0.0
    return float(montant * ayants_droit)


def exonere(foyer: Foyer, parametres: ParametresImpot, salaires_nets: tuple[float, ...],
            pensions_nettes: tuple[float, ...], benefices: tuple[float, ...]) -> bool:
    """Le foyer est-il exonéré de l'impôt, son revenu « net de frais
    professionnels » sous la limite de l'année ? De 1973 à 2013 : les lois de
    finances pour 1974 à 1977, puis l'article 5, 2° bis, du code. Le revenu
    est celui du foyer : les salaires après leurs frais professionnels, mais
    avant les 20 % ; les pensions après leurs 10 % ; les bénéfices avant
    l'abattement des adhérents. La limite des plus de 65 ans vaut si l'un des
    époux l'est (DB 5 B 132 du 1er septembre 1999, n° 6 et 7). De 1973 à 1976,
    celle de qui vit « principalement » de salaires et de pensions — plus de
    la moitié de son revenu (DB 5 B 131, n° 3) — n'est pas celle des autres
    (``limite_autres``), qui n'ont pas celle des plus de 65 ans."""
    e = parametres["exoneration"]
    if "limite" not in e:
        return False
    salaires_et_pensions = somme_ordonnee(salaires_nets) + somme_ordonnee(pensions_nettes)
    revenu = salaires_et_pensions + somme_ordonnee(benefices)
    if "limite_autres" in e and not salaires_et_pensions > revenu / 2:
        return revenu <= e["limite_autres"]
    age = any(d.age is not None and d.age >= AGE_ABATTEMENT for d in foyer.declarants)
    limite = e["limite_plus_de_65_ans"] if age and "limite_plus_de_65_ans" in e else e["limite"]
    return revenu <= limite


def _plafonnement(foyer: Foyer, parametres: ParametresImpot, revenu: float, parts: float,
                  impot_plein: float) -> tuple[float, float, float]:
    """L'impôt après plafonnement des effets du quotient familial (art. 197,
    I, 2) : rend l'impôt retenu, le supplément que le plafonnement ajoute, et
    la réduction complémentaire qui en retranche une part."""
    plafonds = parametres["plafonds_quotient_familial"]
    if parametres.annee < PREMIERE_ANNEE_PLAFONNEMENT or "general" not in plafonds:
        return impot_plein, 0.0, 0.0
    base = foyer.parts_de_base
    if parts <= base:
        return impot_plein, 0.0, 0.0
    demi_parts = round((parts - base) * 2)
    general = plafonds["general"]
    if _parent_isole(foyer):
        # La part du premier enfant du parent isolé : sa demi-part et celle de
        # la case T, plafonnées ensemble (art. 197, I, 2, deuxième phrase).
        premier = plafonds.get("parent_isole_premier_enfant", 2 * general)
        avantage = premier + general * (demi_parts - 2)
    else:
        avantage = general * demi_parts
    impot_de_base = impot_du_bareme(parametres, revenu, base)
    plafonne = impot_de_base - avantage
    if plafonne <= impot_plein:
        return impot_plein, 0.0, 0.0
    supplement = plafonne - impot_plein
    # Les réductions complémentaires, quand le plafonnement s'applique : par
    # demi-part d'invalidité, et pour la part du veuf qui a un enfant à charge.
    complement = (plafonds.get("reduction_complementaire_invalide", 0.0)
                  * _invalidites(foyer, parametres.annee))
    if foyer.veuf and foyer.enfants:
        complement += plafonds.get("reduction_complementaire_veuf", 0.0)
    reduction = min(complement, supplement)
    return plafonne - reduction, supplement, reduction


def decote(foyer: Foyer, parametres: ParametresImpot, impot: float, parts: float) -> float:
    """La décote, selon la règle de l'année.

    - 1961 à 1972, la franchise et la décote de l'IPP : l'impôt qui n'excède
      pas la franchise (``seuil_celibataire``) est effacé, celui qui reste sous
      la limite (``seuil_couple``) réduit de sorte que l'impôt soit continu
      aux deux seuils ; un foyer d'au plus ``nombre_de_parts_limite`` parts a
      les siens. L'IPP ne cite aucun texte : une lecture de ses colonnes.
    - 1973 à 1980 : aucune, la loi de finances pour 1974 (art. 2) les ayant
      « intégrées au barème », avec les minorations dégressives.
    - 1981 à 1985 : la différence entre un seuil et l'impôt, pour une part ou
      une part et demie seulement (art. 197, VI, LEGIARTI000006308325).
    - 1986 à 1999 : la différence entre le seuil et l'impôt, pour tous (DB 5 B
      321, 2000).
    - depuis 2000 : la différence entre le seuil et une fraction de l'impôt —
      la moitié jusqu'en 2013, la totalité en 2014, les trois quarts de 2015 à
      2019, 45,25 % depuis ; un seuil propre aux couples depuis 2014."""
    d = parametres["decote"]
    annee = parametres.annee
    if not d or impot <= 0:
        return 0.0
    if annee <= 1972:
        franchise, limite = d["seuil_celibataire"], d["seuil_couple"]
        if "nombre_de_parts_limite" in d and parts <= d["nombre_de_parts_limite"]:
            franchise = d["seuil_1_faible_nombre_de_parts"]
            limite = d["seuil_2_faible_nombre_de_parts"]
        if impot <= franchise:
            return impot
        if impot >= limite:
            return 0.0
        apres = (impot - franchise) * limite / (limite - franchise)
        return _arrondir_impot(annee, impot - apres)
    if annee <= 1985:
        seuil = {1.0: d.get("seuil_une_part"), 1.5: d.get("seuil_une_part_et_demie")}.get(parts)
        taux = 1.0
    else:
        seuil = d["seuil_couple"] if foyer.couple and "seuil_couple" in d else d["seuil_celibataire"]
        taux = d.get("taux", 1.0 if annee <= 1999 else 0.5)
    if not seuil:
        return 0.0
    return min(impot, max(_arrondir_impot(annee, seuil - taux * impot), 0.0))


def _reduction_sous_condition(foyer: Foyer, parametres: ParametresImpot, impot: float,
                              rfr: float, parts: float) -> float:
    """La réduction de 20 % des revenus de 2016 à 2019 (art. 197, I, 4, b),
    dégressive entre ses deux seuils de revenu fiscal de référence."""
    r = parametres["reduction_sous_condition_de_revenus"]
    if not r or impot <= 0:
        return 0.0
    multiple = 2.0 if foyer.couple else 1.0
    demi_parts = (parts - foyer.parts_de_base) * 2
    bas = r["seuil_bas"] * multiple + r["majoration_par_demi_part"] * demi_parts
    haut = r["seuil_haut"] * multiple + r["majoration_par_demi_part"] * demi_parts
    if rfr <= bas:
        taux = r["taux"]
    elif rfr < haut:
        taux = r["taux"] * (haut - rfr) / (haut - bas)
    else:
        return 0.0
    return _arrondir_impot(parametres.annee, taux * impot)


def _minoration(parametres: ParametresImpot, impot: float, revenu: float, parts: float) -> float:
    """Les minorations exceptionnelles, selon les notes de l'IPP : de 1966 à
    1972, par paliers de revenu ou d'impôt ; de 1984 à 1992, un taux par
    tranche d'impôt, raccordé entre elles par « la différence entre une somme
    et 14 % de l'impôt » (17 % en 1985)."""
    m = parametres["minorations_exceptionnelles"]
    annee = parametres.annee
    if not m or impot <= 0:
        return 0.0
    if annee <= 1972:
        base = revenu if annee <= 1967 else impot
        s2, s3, s4 = m["seuil_impot_2"], m["seuil_impot_3"], m["seuil_impot_4"]
        haut, bas = m["taux_1"], m.get("taux_5", 0.0)
        if base <= s2:
            taux = haut
        elif base <= s3:
            taux = haut + (bas - haut) * (base - s2) / (s3 - s2)
        elif base <= s4:
            taux = bas
        else:
            taux = 0.0
        return _arrondir_impot(annee, taux * impot)
    s = [m.get(f"seuil_impot_{rang}") for rang in range(1, 6)]
    if impot <= s[1]:
        montant = m["taux_1"] * impot
    elif s[2] is not None and impot <= s[2]:
        montant = m["formule_seuil_2"] - m["taux_formule"] * impot
    elif s[3] is not None and impot <= s[3]:
        montant = m["taux_3"] * impot
    elif s[4] is not None and impot <= s[4]:
        montant = m["formule_seuil_4"] - m["taux_formule"] * impot
    elif s[4] is not None and revenu / parts <= m.get("revenu_par_part_maximum", math.inf):
        montant = m["taux_5"] * impot
    else:
        montant = 0.0
    return _arrondir_impot(annee, max(montant, 0.0))


def _paliers_de_1968(impot: float, pas: float, taux_haut: float) -> float:
    """1968 : +2 % de 6 000 à 7 000 F d'impôt, +4 % de 7 000 à 8 000 F…
    jusqu'à +14 % de 12 000 à 14 000 F, 15 % au-delà ; 1969, la moitié, à
    partir de 7 000 F (IPP, notes des majorations)."""
    if impot > 14000:
        return taux_haut
    palier = math.floor((min(impot, 13999.99) - 6000) / 1000) + 1
    return pas * min(palier, 7)


def _majoration(parametres: ParametresImpot, impot: float, revenu: float) -> float:
    """Les majorations exceptionnelles, selon les notes de l'IPP : le « décime »
    et le « demi-décime » de 1960 à 1965 au-delà d'un revenu ; de 1967 à 1971,
    un taux par tranche d'impôt, appliqué à tout l'impôt ; de 1980 à 1984, un
    taux sur la fraction de l'impôt qui excède un seuil (sur tout l'impôt, par
    tranche, en 1983), qui n'est pas due sous son ``minimum`` (« inférieure à
    200 F » en 1980 : loi de finances rectificative pour 1981, art. 1er)."""
    m = parametres["majorations_exceptionnelles"]
    annee = parametres.annee
    if not m or impot <= 0:
        return 0.0
    if "seuil_revenu" in m:
        taux = m["taux_1"] if revenu > m["seuil_revenu"] else 0.0
        return _arrondir_impot(annee, taux * impot)
    if annee == 1968:
        taux = _paliers_de_1968(impot, 0.02, m["taux_3"]) if impot > m["seuil_1"] else 0.0
        return _arrondir_impot(annee, taux * impot)
    if annee == 1969:
        if impot <= m["seuil_1"]:
            return 0.0
        taux = _paliers_de_1968(impot, 0.02, 2 * m["taux_3"]) / 2 if impot <= 14000 else m["taux_3"]
        return _arrondir_impot(annee, taux * impot)
    if annee <= 1971 or annee == 1983:
        taux = 0.0
        for rang in (1, 2, 3):
            if f"seuil_{rang}" in m and impot > m[f"seuil_{rang}"]:
                taux = m[f"taux_{rang}"]
        return _arrondir_impot(annee, taux * impot)
    if annee == 1981 and impot <= 25000:
        # « Pour les revenus 1981, seuls les contribuables dont l'impôt est
        # supérieur à 25 000 FRF sont concernés » (IPP).
        return 0.0
    majoration = _arrondir_impot(annee, m["taux_1"] * max(impot - m["seuil_1"], 0.0))
    return majoration if majoration >= m.get("minimum", 0.0) else 0.0


def _reduction_exceptionnelle(foyer: Foyer, parametres: ParametresImpot, impot: float,
                              rfr: float, parts: float) -> float:
    """La réduction exceptionnelle des revenus de 2013 (loi n° 2014-891, art. 1) :
    350 € pour une personne seule, 700 € pour un couple, sous un seuil de
    revenu fiscal de référence majoré par demi-part, dégressive au-delà."""
    r = parametres["reduction_exceptionnelle"]
    if not r or impot <= 0:
        return 0.0
    multiple = 2.0 if foyer.couple else 1.0
    seuil = r["seuil"] * multiple + r["majoration_par_demi_part"] * (parts - foyer.parts_de_base) * 2
    montant = r["montant"] * multiple
    if rfr <= seuil:
        reduction = montant
    else:
        reduction = max(seuil + montant - rfr, 0.0)
    return _arrondir_impot(parametres.annee, min(reduction, impot))


def _reduction_proportionnelle(parametres: ParametresImpot, impot: float) -> float:
    """Les 5 % retranchés de l'impôt des revenus de 2001 (loi n° 2002-1050,
    art. 1 ; BOI 5 B-6-03, n° 1) : « sur les droits bruts après application
    des effets du plafonnement du quotient familial et de la décote mais avant
    imputation des réductions et crédits d'impôt, de la prime pour l'emploi »."""
    r = parametres["reduction_proportionnelle"]
    if not r or impot <= 0:
        return 0.0
    return _arrondir_impot(parametres.annee, impot * r["taux"])


def _credit_exceptionnel(foyer: Foyer, parametres: ParametresImpot, impot: float,
                         revenu: float, rfr: float, parts: float) -> float:
    """Le crédit d'impôt exceptionnel des revenus de 2008 (loi n° 2009-431,
    art. 1 ; BOI 5 B-25-09) : les deux tiers de l'``impot`` après plafonnement
    et décote sous le premier seuil de revenu imposable par part ; au-delà,
    jusqu'au second, le crédit du foyer au premier seuil, arrondi comme le
    tableau de l'annexe 2 du BOI, décroissant linéairement jusqu'à zéro. Le
    revenu fiscal de référence par part ne dépasse pas le second seuil."""
    c = parametres["credit_exceptionnel"]
    if not c or impot <= 0:
        return 0.0
    plein, maximum = c["revenu_par_part_plein"], c["revenu_par_part_maximum"]
    par_part = revenu / parts
    if par_part >= maximum or rfr / parts > maximum:
        return 0.0
    if par_part <= plein:
        return _arrondir_impot(parametres.annee, impot * c["taux"])
    au_seuil = impot_du_bareme(parametres, plein * parts, parts)
    au_seuil, _, _ = _plafonnement(foyer, parametres, plein * parts, parts, au_seuil)
    au_seuil -= decote(foyer, parametres, au_seuil, parts)
    credit_maximum = _arrondir_impot(parametres.annee, au_seuil * c["taux"])
    return _arrondir_impot(parametres.annee,
                           credit_maximum * (maximum - par_part) / (maximum - plein))


def revenus_de_la_prime(parametres: ParametresImpot, salaires: tuple[float, ...],
                       benefices: tuple[float, ...]) -> tuple[float, ...]:
    """Par déclarant, le revenu d'activité de la prime pour l'emploi : ses
    salaires avant leurs frais professionnels (BOI 5 B-12-01, n° 13), et son
    bénéfice déclaré, majoré de 11,11 %, ou son déficit, minoré de 11,11 %
    depuis les revenus de 2001 (:data:`TAUX_NON_SALARIES_DE_LA_PPE`) ; rien
    hors des années de la prime."""
    if not parametres["prime_pour_l_emploi"]:
        return ()
    revenus = []
    for salaire, benefice in zip(salaires, benefices):
        ajustement = 0.0
        if benefice > 0 or parametres.annee >= PREMIERE_ANNEE_DEFICIT_MINORE:
            ajustement = _au_plus_proche(abs(benefice) * TAUX_NON_SALARIES_DE_LA_PPE)
        revenus.append(salaire + benefice + ajustement)
    return tuple(revenus)


def prime_pour_l_emploi(foyer: Foyer, parametres: ParametresImpot,
                        revenus: tuple[float, ...], rfr: float, parts: float) -> float:
    """La prime pour l'emploi (art. 200 sexies), de 2000 à 2014, pour un foyer
    qui travaille à temps plein toute l'année : par personne active, une part
    croissante de son revenu d'activité (:func:`revenus_de_la_prime`), puis
    décroissante ; les majorations du couple dont un seul travaille et des
    personnes à charge."""
    p = parametres["prime_pour_l_emploi"]
    if not p:
        return 0.0
    base = p["rfr_couple"] if foyer.couple else p["rfr_personne_seule"]
    if rfr > base + p["rfr_par_demi_part"] * (parts - foyer.parts_de_base) * 2:
        return 0.0
    actifs = [r for r in revenus if r >= p["revenu_minimum"]]
    mono_emploi = foyer.couple and len(actifs) == 1
    prime = 0.0
    forfait_famille = False
    for revenu in actifs:
        if revenu <= p["revenu_taux_plein"]:
            prime_individuelle = p["taux_entree"] * revenu
        elif revenu < p["revenu_maximum"]:
            prime_individuelle = p["taux_sortie"] * (p["revenu_maximum"] - revenu)
        else:
            prime_individuelle = 0.0
        if mono_emploi:
            if revenu <= p["revenu_maximum"]:
                prime_individuelle += p["majoration_mono_emploi"]
            elif revenu <= p["revenu_taux_plein_mono_emploi"]:
                prime_individuelle = p["majoration_mono_emploi"]
                forfait_famille = True
            elif revenu < p["revenu_maximum_mono_emploi"]:
                prime_individuelle = p["taux_sortie_mono_emploi"] * (
                    p["revenu_maximum_mono_emploi"] - revenu)
                forfait_famille = True
            else:
                prime_individuelle = 0.0
        prime += prime_individuelle
    if not actifs:
        return 0.0
    total_actif = somme_ordonnee(actifs)
    if _parent_isole(foyer) and p["revenu_maximum"] < total_actif < p["revenu_maximum_mono_emploi"]:
        forfait_famille = True
    if foyer.enfants and (prime > 0 or forfait_famille):
        premier = (p["majoration_parent_isole"] if _parent_isole(foyer)
                   else p["majoration_par_personne_a_charge"])
        if forfait_famille:
            prime += premier
        else:
            prime += premier + p["majoration_par_personne_a_charge"] * (foyer.enfants - 1)
    prime = _arrondir_impot(parametres.annee, prime)
    if parametres.annee < PREMIERE_ANNEE_SEUIL_DE_LA_PPE:
        prime = max(prime, p["montant_minimum"]) if prime > 0 else 0.0
    elif prime < p["montant_minimum"]:
        prime = 0.0
    if parametres.annee == 2000:
        # La prime des revenus de 2000 versée deux fois : loi n° 2001-1276,
        # art. 1er, reproduit au BOI 5 B-12-02 : « un complément égal au
        # montant de cette prime ».
        prime *= 2
    return prime


def _remarques(foyer: Foyer, parametres: ParametresImpot, la_decote: float,
               minoration: float, majoration: float, ppe: float,
               benefices: tuple[float, ...] = ()) -> tuple[str, ...]:
    """Ce que le calcul de ce foyer doit à une règle qu'aucun texte lu ne
    porte, ou à une hypothèse."""
    annee = parametres.annee
    remarques = []
    if parametres.projete:
        remarques.append(f"barème projeté ({parametres.indexation}) au-delà des revenus de "
                         f"{parametres.derniere_annee_lue}")
    if la_decote and annee <= 1972:
        remarques.append("franchise et décote des années 1960 : une lecture des colonnes de "
                         "l'IPP, sans texte lu")
    if minoration or majoration:
        remarques.append("minoration ou majoration exceptionnelle : la règle des notes de "
                         "l'IPP, sans texte lu")
    if ppe:
        remarques.append("prime pour l'emploi d'un travail à temps plein toute l'année")
    if annee < PREMIERE_ANNEE_PLAFONNEMENT and any(d.invalide for d in foyer.declarants):
        remarques.append("invalide : les régimes des couples d'avant 1981 ne sont pas repris")
    adherents = [b for d, b in zip(foyer.declarants, benefices)
                 if b > 0 and d.regime == "reel_adherent"]
    if any(b > SEUILS_ABATTEMENT_REDUIT.get(annee, math.inf) for b in adherents):
        remarques.append("abattement des adhérents : le seuil de sa fraction à 10 % est celui de "
                         "la rédaction de l'année, sans l'indexation que le code prescrit, "
                         "et sa limite celle des salaires")
    return tuple(remarques)


# -- le calcul ----------------------------------------------------------------


def _conversion(parametres: ParametresImpot, unite: str) -> float:
    """Ce par quoi multiplier un montant de l'unité demandée pour l'avoir dans
    la monnaie de l'année."""
    if unite not in ("euro", "monnaie"):
        raise ValueError(f"unité inconnue : {unite!r}")
    return FRANC if (unite == "euro" and parametres.monnaie == "FRF") else 1.0


def impot_du_foyer(foyer: Foyer, annee: int, baremes: BaremesImpotRevenu, *,
                   unite: str = "euro", indexation: str = "prix",
                   croissance=None) -> ImpotDuFoyer:
    """L'impôt du ``foyer`` sur ses revenus d'``annee``.

    ``unite="euro"`` : les revenus du foyer et l'impôt rendu sont en euros,
    convertis au taux légal pour une année en francs ; ``unite="monnaie"`` :
    dans la monnaie de l'année. Au-delà de la dernière loi de finances lue,
    ``indexation`` et ``croissance`` projettent le barème
    (:meth:`~retraite_notionnelle.donnees.impot_revenu.BaremesImpotRevenu.parametres`)."""
    return impot_aux_parametres(foyer, baremes.parametres(annee, indexation, croissance),
                                unite=unite)


def impot_aux_parametres(foyer: Foyer, parametres: ParametresImpot, *,
                         unite: str = "euro") -> ImpotDuFoyer:
    """L'impôt du ``foyer`` sur ses revenus de l'année de ``parametres``, lus
    ou projetés : :func:`impot_du_foyer`, pour qui tient déjà les paramètres
    de chaque année — les indicateurs de cycle de vie, qui en prennent la
    chronique d'un siècle
    (:meth:`~retraite_notionnelle.donnees.impot_revenu.BaremesImpotRevenu.chronique`)."""
    annee = parametres.annee
    vers = _conversion(parametres, unite)
    salaires = tuple(_au_plus_proche(d.salaires * vers) for d in foyer.declarants)
    pensions = tuple(_au_plus_proche(d.pensions * vers) for d in foyer.declarants)
    salaires_nets, pensions_nettes, vingt = _revenus_nets(foyer, parametres, salaires, pensions)
    benefices = tuple(_au_plus_proche(d.benefices * vers) for d in foyer.declarants)
    retenus = tuple(benefice_retenu(d, parametres, b) for d, b in zip(foyer.declarants, benefices))
    abattement_adherents = somme_ordonnee(max(b - r, 0.0) for b, r in zip(benefices, retenus))
    majoration_benefices = somme_ordonnee(max(r - b, 0.0) for b, r in zip(benefices, retenus))
    revenu_net_global = max(somme_ordonnee(salaires_nets) + somme_ordonnee(pensions_nettes)
                            - vingt + somme_ordonnee(retenus), 0.0)
    revenu_net_global = _arrondir_element(annee, revenu_net_global)
    abattement = min(_abattement_age_invalidite(foyer, parametres, revenu_net_global),
                     revenu_net_global)
    revenu = _arrondir_revenu_imposable(annee, revenu_net_global - abattement)
    assiette = {"salaires_nets": salaires_nets, "pensions_nettes": pensions_nettes,
                "abattement_vingt_pour_cent": vingt, "benefices": benefices,
                "benefices_retenus": retenus,
                "abattement_adherents": abattement_adherents,
                "majoration_des_benefices": majoration_benefices,
                "revenu_net_global": revenu_net_global,
                "abattement_age_invalidite": abattement}
    activite = revenus_de_la_prime(parametres, salaires, benefices)
    exoneration = exonere(foyer, parametres, salaires_nets, pensions_nettes, benefices)
    return _liquider(foyer, parametres, revenu, activite, assiette, unite, vers, exoneration)


def impot_d_un_revenu_imposable(foyer: Foyer, annee: int, revenu_net_imposable: float,
                                baremes: BaremesImpotRevenu, *, unite: str = "euro",
                                indexation: str = "prix", croissance=None) -> ImpotDuFoyer:
    """L'impôt d'un foyer dont on connaît le revenu net imposable, comme dans
    les exemples de l'administration : les revenus de ses déclarants sont
    ignorés, et ni la prime pour l'emploi ni l'exonération ne se calculent."""
    parametres = baremes.parametres(annee, indexation, croissance)
    vers = _conversion(parametres, unite)
    revenu = _arrondir_revenu_imposable(annee, revenu_net_imposable * vers)
    assiette = {"salaires_nets": (), "pensions_nettes": (), "abattement_vingt_pour_cent": 0.0,
                "benefices_retenus": (), "abattement_adherents": 0.0,
                "majoration_des_benefices": 0.0,
                "revenu_net_global": revenu, "abattement_age_invalidite": 0.0}
    return _liquider(foyer, parametres, revenu, (), assiette, unite, vers)


def _liquider(foyer: Foyer, parametres: ParametresImpot, revenu: float,
              activite: tuple[float, ...], assiette: dict, unite: str,
              vers: float, exoneration: bool = False) -> ImpotDuFoyer:
    """Du revenu net imposable à l'impôt : les parts, le barème et son
    plafonnement, la décote et les autres corrections, l'exonération, la prime
    pour l'emploi, le seuil de mise en recouvrement. Les montants sont dans la
    monnaie de l'année ; ``vers`` y convertit l'unité demandée."""
    annee = parametres.annee
    rfr = revenu
    parts = nombre_de_parts(foyer, parametres)
    impot_plein = impot_du_bareme(parametres, revenu, parts)
    impot_brut, supplement, reduction_complementaire = _plafonnement(
        foyer, parametres, revenu, parts, impot_plein)
    la_decote = decote(foyer, parametres, impot_brut, parts)
    impot = impot_brut - la_decote
    reduction_scr = _reduction_sous_condition(foyer, parametres, impot, rfr, parts)
    impot -= reduction_scr
    minoration = _minoration(parametres, impot, revenu, parts)
    impot -= minoration
    majoration = _majoration(parametres, impot, revenu)
    impot += majoration
    reduction_exc = _reduction_exceptionnelle(foyer, parametres, impot, rfr, parts)
    impot = max(impot - reduction_exc, 0.0)
    reduction_prop = _reduction_proportionnelle(parametres, impot)
    impot -= reduction_prop
    if exoneration:
        # « sont exonérés de l'impôt sur le revenu » : la cotisation tombe ; les
        # crédits restent, restitués en entier au foyer qui n'est pas imposable.
        impot = 0.0

    ppe = prime_pour_l_emploi(foyer, parametres, activite, rfr, parts) if activite else 0.0
    credit = _credit_exceptionnel(foyer, parametres, impot_brut - la_decote, revenu, rfr, parts)
    recouvrement = parametres["recouvrement"]
    mis_en_recouvrement = impot > 0 and impot >= recouvrement.get("seuil", 0.0)
    # Le foyer dont la cotisation n'est pas mise en recouvrement n'est pas
    # imposable : ses crédits lui sont restitués en entier (art. 200 sexies,
    # IV ; BOI 5 B-12-01, n° 53 : « la totalité de la prime pour l'emploi
    # lorsque le contribuable n'est pas imposable »).
    net = (impot if mis_en_recouvrement else 0.0) - ppe - credit
    if 0 <= net < recouvrement.get("seuil_apres_credits", 0.0):
        net = 0.0
    retour = 1.0 / vers
    return ImpotDuFoyer(
        annee=annee, monnaie=parametres.monnaie, unite=unite, parts=parts,
        salaires_nets=tuple(s * retour for s in assiette["salaires_nets"]),
        pensions_nettes=tuple(p * retour for p in assiette["pensions_nettes"]),
        abattement_vingt_pour_cent=assiette["abattement_vingt_pour_cent"] * retour,
        benefices_retenus=tuple(b * retour for b in assiette["benefices_retenus"]),
        abattement_adherents=assiette["abattement_adherents"] * retour,
        majoration_des_benefices=assiette["majoration_des_benefices"] * retour,
        revenu_net_global=assiette["revenu_net_global"] * retour,
        abattement_age_invalidite=assiette["abattement_age_invalidite"] * retour,
        revenu_net_imposable=revenu * retour,
        revenu_fiscal_de_reference=rfr * retour,
        impot_sans_plafonnement=impot_plein * retour,
        impot_brut=impot_brut * retour,
        plafonnement=supplement * retour,
        reduction_complementaire=reduction_complementaire * retour,
        decote=la_decote * retour,
        reduction_sous_condition_de_revenus=reduction_scr * retour,
        minoration_exceptionnelle=minoration * retour,
        majoration_exceptionnelle=majoration * retour,
        reduction_exceptionnelle=reduction_exc * retour,
        reduction_proportionnelle=reduction_prop * retour,
        impot_avant_credits=impot * retour,
        revenus_d_activite=tuple(r * retour for r in activite),
        prime_pour_l_emploi=ppe * retour,
        credit_exceptionnel=credit * retour,
        mis_en_recouvrement=mis_en_recouvrement,
        exonere=exoneration,
        impot=net * retour,
        fiabilite=parametres.fiabilite,
        remarques=_remarques(foyer, parametres, la_decote, minoration, majoration, ppe,
                             assiette.get("benefices", ())),
    )
