"""Le mois, seule unité de temps que le droit de la retraite manipule vraiment.

Le modèle a longtemps travaillé à l'année, et arrondissait l'âge de liquidation
à l'année civile la plus proche. Cet arrondi n'était pas une imprécision de
détail : il déplaçait la pension de six à sept pour cent d'un mois à l'autre,
au milieu de l'année, et l'arrondi au pair de Python le faisait dépendre de la
PARITÉ du millésime — deux assurés déclarant « soixante-quatre ans et six mois »
étaient traités différemment selon leur génération.

Ce module porte la date au mois, et rien de plus. Le pas du moteur reste
l'année, parce que les données le sont : un salaire est déclaré à l'année, le
salaire moyen par tête est une moyenne annuelle, un quotient de mortalité est
publié par âge entier. Découper ces grandeurs en douze n'ajouterait aucune
vérité — la répartition uniforme qu'il faudrait supposer redonne exactement le
total annuel, au centime près.

Le mois sert donc là, et seulement là, où le réel porte une date :

* **les bornes de la carrière** — l'année d'entrée et l'année de liquidation
  sont des années INCOMPLÈTES, et n'ont jamais valu ni zéro ni un ;
* **l'âge à la liquidation** — il commande le diviseur actuariel et la décote ;
* **les dates d'effet du droit** — revalorisations de la Cnav, générations que
  la loi coupe au 1er juillet 1951 et au 1er septembre 1961.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Mois par année. Nommé pour que les divisions par douze se lisent.
MOIS_PAR_AN = 12


@dataclass(frozen=True, order=True)
class DateMois:
    """Un mois d'une année civile — la plus fine des dates du modèle.

    Les pensions prennent effet le premier jour d'un mois : c'est la maille du
    droit, et il n'y a rien à gagner à descendre au jour, que les données ne
    portent pas.
    """

    annee: int
    mois: int  # 1 = janvier, 12 = décembre

    def __post_init__(self) -> None:
        if not 1 <= self.mois <= MOIS_PAR_AN:
            raise ValueError(f"mois attendu entre 1 et 12, reçu {self.mois}")

    # -- arithmétique --------------------------------------------------------

    @property
    def rang(self) -> int:
        """Rang absolu du mois, pour additionner et soustraire sans cas particulier."""
        return self.annee * MOIS_PAR_AN + (self.mois - 1)

    @classmethod
    def depuis_rang(cls, rang: int) -> "DateMois":
        return cls(rang // MOIS_PAR_AN, rang % MOIS_PAR_AN + 1)

    def plus_mois(self, mois: int) -> "DateMois":
        return DateMois.depuis_rang(self.rang + mois)

    def __str__(self) -> str:
        """« janvier 2000 » : la page, et le détail d'une pension datée
        (:mod:`~retraite_notionnelle.droit.departs`), l'écrivent ainsi."""
        return f"{NOMS_DE_MOIS[self.mois - 1]} {self.annee}"


NOMS_DE_MOIS = (
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
)


def en_mois(age: float) -> int:
    """Âge en années décimales -> âge en mois entiers.

    Les âges du modèle circulent en années décimales — 64,25 pour soixante-quatre
    ans et trois mois — parce que c'est ainsi que le code de la sécurité sociale
    les écrit et que les URL du simulateur les portent. La conversion arrondit au
    mois le plus proche : un âge saisi en ans et en mois se retrouve à
    l'identique, et un âge saisi autrement se voit rattaché au mois qu'il désigne.
    """
    return round(age * MOIS_PAR_AN)


def decomposer(age: float) -> tuple[int, int]:
    """Âge en années décimales -> (années entières, mois)."""
    mois = en_mois(age)
    return mois // MOIS_PAR_AN, mois % MOIS_PAR_AN


def formater_age(age: float) -> str:
    """« 64,58 » -> « 64 ans et 7 mois »."""
    annees, mois = decomposer(age)
    if mois == 0:
        return f"{annees} ans"
    return f"{annees} ans et {mois} mois"


def origine_des_ages(naissance: DateMois, jour: int) -> DateMois:
    """Le mois d'où les âges se comptent, pour qui est né ce mois-là, ce
    jour-là : celui de la naissance pour qui est né un 1er, le suivant pour
    les autres.

    La pension prend effet le premier jour d'un mois, qui ne peut précéder
    l'âge qui l'ouvre (R. 351-37 du code de la sécurité sociale, qui ne la
    laissait pas « antérieure [...] au soixantième anniversaire » jusqu'en
    2004 ; L. 90 du code des pensions la fait due au premier du mois qui suit
    la cessation d'activité) : né le 16 mai 1964, l'assuré atteint l'âge
    légal de 62 ans et 9 mois le 16 février 2027, et sa retraite prend effet
    au 1er mars 2027 au plus tôt (circulaire Cnav n° 2026-07, point 1.1) ; né
    un 1er, il l'a le jour même.

    Les âges du modèle sont donc des âges au premier jour d'un mois, en mois
    révolus : né le 15 mars, on a, à tout 1er du mois, l'âge de qui est né le
    1er avril. Le mois que rend cette fonction est celui d'où un âge devient
    une date de départ, ou d'ouverture d'un décompte, et d'où une date
    redevient un âge. Un métier, lui, commence dans le mois où l'on a l'âge
    dit, compté du mois de naissance : on commence à travailler le jour qu'on
    veut. La génération ne se lit pas d'ici non plus : la loi coupe au
    1er juillet 1951 et au 1er septembre 1961 des assurés nés avant ou après,
    au vrai mois.
    """
    return naissance if jour == 1 else naissance.plus_mois(1)


def mois_travailles(annee: int, debut: DateMois, fin: DateMois) -> int:
    """Mois de l'année civile ``annee`` compris entre ``debut`` et ``fin``.

    ``debut`` est inclus, ``fin`` est EXCLUE : une pension prend effet le
    premier du mois, et ce mois-là n'est plus travaillé. Le résultat vaut douze
    pour une année pleine, zéro pour une année hors carrière, et le compte juste
    aux deux bords.
    """
    premier = DateMois(annee, 1).rang
    dernier = DateMois(annee, MOIS_PAR_AN).rang + 1
    return max(0, min(dernier, fin.rang) - max(premier, debut.rang))


def fraction_annee(annee: int, debut: DateMois, fin: DateMois) -> float:
    """Part de l'année civile réellement couverte par la carrière."""
    return mois_travailles(annee, debut, fin) / MOIS_PAR_AN


def trimestres_civils(mois: int) -> int:
    """Trimestres civils entiers contenus dans un nombre de mois.

    Le droit ne retient, l'année du point de départ, que les trimestres civils
    ÉCOULÉS : un départ au 1er août laisse deux trimestres derrière lui, quel
    que soit le montant cotisé pendant ces sept mois. C'est un plafond, pas un
    décompte — le nombre de trimestres réellement validés reste commandé par le
    montant, comme le veut l'article R. 351-9.
    """
    return mois // 3
