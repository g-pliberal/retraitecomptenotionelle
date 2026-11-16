"""Les types de la revalorisation que le pont échange (action 161, étape 1 du
retrait des règles Python) : ce qu'une pension sert aujourd'hui, régime par
régime, et ce que l'étape « faire vivre » inscrit au journal, sans aucun corps
de règle. ``revalorisation.py`` les réimporte le temps du retrait.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..donnees.chargement import Fiabilite
from ..somme import somme_ordonnee



@dataclass(frozen=True)
class RegimeServi:
    """La pension d'un régime, de la liquidation à aujourd'hui."""

    regime: str
    #: Montant annuel brut à la liquidation, en euros de l'année de
    #: liquidation : celui que le scénario 1 calcule.
    au_depart: float
    #: Le coefficient NOMINAL qui le mène à aujourd'hui.
    coefficient: float
    #: La règle suivie — voir les constantes ``REGLE_*``.
    regle: str
    fiabilite: Fiabilite
    #: Régime provisionné (RAFP) : servi à part, hors des totaux de la
    #: répartition, comme à la liquidation.
    hors_repartition: bool = False
    #: Ce que la révision du minimum contributif retire, en euros de
    #: l'échéance, quand une pension étrangère commence après le départ
    #: (R. 173-8, :func:`reviser_le_minimum`).
    revision: float = 0.0
    #: Ce que les majorations forfaitaires de 1972 à 1982, que le coefficient
    #: porte, ne donnent pas au plancher auquel la pension est portée — le
    #: minimum des pensions, l'AVTS, la pension d'invalidité de l'ex-invalide —,
    #: en euros de l'échéance (:func:`plancher_non_majore`) : retiré.
    plancher_non_majore: float = 0.0
    #: Ce que le maximum du jour de la dernière majoration forfaitaire de 1972
    #: à 1982 change à la pension, majorée sur son montant entier, en euros de
    #: l'échéance (:func:`maximum_du_jour`) : ajouté, ce que le maximum de sa
    #: liquidation en avait retiré ; négatif, ce que celui du jour ne laisse pas.
    maximum_du_jour: float = 0.0
    #: La majoration exceptionnelle des petites pensions, due depuis le
    #: 1er septembre 2023, en euros de l'échéance
    #: (:func:`majorer_les_petites_pensions`). La réversion ne la lit pas.
    majoration: float = 0.0
    #: Ce que le taux plein ouvre depuis le 1er septembre 2023 à la RCO d'un
    #: chef d'exploitation parti avant — points gratuits et complément
    #: différentiel —, en euros de l'échéance (:func:`relever_les_exploitants`).
    relevement: float = 0.0
    #: Ce que la révision d'une pension agricole déjà liquidée ajoute à la
    #: base des non-salariés agricoles, en euros de l'échéance : les plans de
    #: revalorisation servis à la règle des pensions dues, et la pension
    #: majorée de référence ouverte en 2009 aux pensions prises avant
    #: (:func:`reviser_les_exploitants`).
    plans: float = 0.0
    pmr: float = 0.0
    #: La majoration pour conjoint à charge (L. 351-13) : sa part de
    #: ``au_depart``, que le coefficient ne mène pas, et celle de l'échéance,
    #: nominale — elle ne se revalorise pas, et commence parfois après le
    #: départ (``PensionRegime.conjoint``). La réversion ne la lit pas.
    conjoint_au_depart: float = 0.0
    conjoint: float = 0.0

    @property
    def aujourd_hui(self) -> float:
        return ((self.au_depart - self.conjoint_au_depart) * self.coefficient
                - self.revision - self.plancher_non_majore + self.maximum_du_jour
                + self.majoration + self.relevement + self.plans + self.pmr + self.conjoint)


@dataclass(frozen=True)
class MajorationExceptionnelle:
    """La majoration exceptionnelle d'une petite pension, telle que la caisse
    la calcule le mois où elle est due (fiche ``majoration_exceptionnelle_2023``,
    :func:`majorer_les_petites_pensions`) : en euros par mois, chaque montant
    tronqué au centime (circulaire Cnav n° 2023-21)."""

    regime: str
    #: Le premier jour du mois où elle est due (AAAA-MM-JJ), ou celui de sa
    #: révision, quand une pension commence après.
    date: str
    #: La majoration théorique, au prorata de la durée cotisée dans le régime.
    theorique: float
    #: Le plafond du régime, au prorata de sa durée validée.
    plafond: float
    #: La pension du régime ce mois-là, sans sa surcote, majoration pour
    #: enfants comprise, que le plafond borne avec la majoration.
    pension: float
    #: La majoration retenue sous le plafond du régime.
    retenue: float
    #: La majoration servie, sous le plafond tous régimes de L. 173-2.
    servie: float
    #: Le coefficient qui la mène de sa date à l'échéance (L. 161-23-1).
    coefficient: float

    @property
    def a_l_echeance(self) -> float:
        """Son montant annuel à l'échéance."""
        return self.servie * 12.0 * self.coefficient


@dataclass(frozen=True)
class RelevementAgricole:
    """Ce que le taux plein ouvre, depuis le 1er septembre 2023, à la RCO d'un
    chef d'exploitation parti avant sans la durée requise tous régimes (fiche
    ``relevement_des_exploitants_2023``, :func:`relever_les_exploitants`)."""

    #: Le jour où il est dû (AAAA-MM-JJ).
    date: str
    #: Les points gratuits de L. 732-56, et ceux du complément différentiel
    #: de L. 732-63, attribués ce jour-là.
    points_gratuits: float
    points_complement: int
    #: La valeur de service du point de RCO ce jour-là, et le SMIC net
    #: agricole horaire que le complément a lu.
    valeur_point: float
    smic_net: float
    #: Le coefficient qui mène la valeur du point jusqu'à l'échéance.
    coefficient: float

    @property
    def a_l_echeance(self) -> float:
        """Son montant annuel à l'échéance."""
        return ((self.points_gratuits + self.points_complement) * self.valeur_point
                * self.coefficient)


@dataclass(frozen=True)
class RevisionAgricole:
    """Ce que la révision d'une pension des non-salariés agricoles déjà
    liquidée sert à l'échéance (:func:`reviser_les_exploitants`)."""

    #: L'année dont la règle des plans de revalorisation est servie — 2008 au
    #: plus —, ou ``None`` quand les plans ne révisent rien ; les points de la
    #: liquidation et ceux de cette année.
    annee_des_plans: int | None
    points_a_la_liquidation: float
    points_servis: float
    #: Ce que leur révision ajoute, en euros de l'échéance.
    plans: float
    #: La pension majorée de référence d'une pension prise avant 2009, à
    #: l'échéance : entière, et la majoration servie, écrêtée ; d'une pension
    #: prise de 2009 à 2021, depuis 2022 : entière, et ce que la règle unique
    #: change à la majoration de la liquidation menée par le coefficient ; d'une
    #: pension prise depuis 2009 que sa révision refait (D. 732-114) : entière,
    #: et ce que la révision y change.
    pmr_entiere: float | None
    pmr: float


@dataclass(frozen=True)
class Revalorisee:
    """Ce que l'étape « faire vivre » écrit : les pensions du système 1 menées
    à une échéance. Son schéma : ``data/reference/etapes/faire_vivre.yaml``."""

    personne: str
    #: L'année de l'échéance, dont les euros sont ceux de tous les montants.
    annee: int
    regimes: tuple[RegimeServi, ...]
    #: La majoration pour enfants à la liquidation, et le coefficient qui la
    #: mène à l'échéance : chaque part à celui du régime qui la porte, celle
    #: des enfants qui ne sont plus à charge retirée.
    majoration_enfants: float
    coefficient_majoration: float
    #: Le montant total brut mensuel de décembre 2019 qui a choisi la tranche
    #: de 2020, ou ``None`` quand la pension n'a pas traversé cette date.
    mensuel_decembre_2019: float | None
    fiabilite: Fiabilite
    #: Les majorations exceptionnelles de septembre 2023, régime par régime,
    #: telles que la caisse les a calculées (:class:`MajorationExceptionnelle`).
    majorations: tuple[MajorationExceptionnelle, ...] = ()
    #: Le relèvement d'un chef d'exploitation de septembre 2023
    #: (:class:`RelevementAgricole`) ; ``None`` sans lui.
    relevement: RelevementAgricole | None = None
    #: La révision d'une pension agricole déjà liquidée
    #: (:class:`RevisionAgricole`) ; ``None`` sans elle.
    exploitant: RevisionAgricole | None = None

    def donnees(self) -> dict:
        """La revalorisation, telle que le schéma de l'étape la décrit."""
        return {
            "schema_version": 1,
            "personne": self.personne,
            "date": f"{self.annee:04d}-12-31",
            "regimes": [{"regime": r.regime, "coefficient": r.coefficient,
                         "regle": r.regle, "fiabilite": r.fiabilite.name.lower(),
                         "revision": r.revision,
                         "majoration_exceptionnelle": r.majoration,
                         "relevement_des_exploitants": r.relevement}
                        | ({"plancher_non_majore": r.plancher_non_majore}
                           if r.plancher_non_majore else {})
                        | ({"maximum_du_jour": r.maximum_du_jour}
                           if r.maximum_du_jour else {})
                        | ({"majoration_conjoint_a_charge": r.conjoint}
                           if r.conjoint or r.conjoint_au_depart else {})
                        | ({"plans_de_revalorisation": r.plans} if r.plans else {})
                        | ({"pension_majoree_de_2009": r.pmr} if r.pmr else {})
                        for r in self.regimes],
            "majoration": self.coefficient_majoration,
            "mensuel_decembre_2019": self.mensuel_decembre_2019,
            "fiabilite": self.fiabilite.name.lower(),
        }


@dataclass(frozen=True)
class ActuelAujourdhui:
    """Le système 1 aujourd'hui : ce que le droit sert, régime par régime."""

    #: L'année courante, dont les euros sont ceux de tous les montants rendus.
    annee: int
    regimes: tuple[RegimeServi, ...]
    #: La majoration pour enfants, à la liquidation. Elle suit les régimes
    #: qui la portent, chaque part au coefficient du sien : c'est le
    #: coefficient qu'on lit ici, pondéré par les parts.
    majoration_enfants: float
    coefficient_majoration: float
    #: L'ASPA à la liquidation, puis celle d'aujourd'hui : un montant
    #: différentiel, recalculé sur le barème de l'année et sur les pensions
    #: d'aujourd'hui, et ouvert à 65 ans même si le départ a eu lieu avant.
    minimum_vieillesse_au_depart: float
    minimum_vieillesse: float
    #: Le montant total brut mensuel de décembre 2019 qui a choisi la tranche
    #: de 2020, ou ``None`` quand la pension n'a pas traversé cette date. Nul
    #: pour une pension prise en janvier 2020, qui n'était pas encore servie.
    mensuel_decembre_2019: float | None
    fiabilite: Fiabilite

    @property
    def pension_annuelle(self) -> float:
        """La répartition, comme :attr:`ResultatActuel.pension_annuelle`."""
        return (somme_ordonnee(r.aujourd_hui for r in self.regimes if not r.hors_repartition)
                + self.majoration_enfants * self.coefficient_majoration
                + self.minimum_vieillesse)

    @property
    def pension_hors_repartition(self) -> float:
        return somme_ordonnee(r.aujourd_hui for r in self.regimes if r.hors_repartition)


@dataclass(frozen=True)
class PensionAujourdhui:
    """Ce qu'un retraité touche aujourd'hui, dans chacun des six systèmes.

    En euros COURANTS de :attr:`annee` — ceux du relevé bancaire.
    """

    annee: int
    actuel: ActuelAujourdhui
    #: La pension annuelle d'aujourd'hui des cinq scénarios notionnels, au sens
    #: de ``pension_annuelle`` : la répartition, garantie vieillesse comprise
    #: pour le 6, rente capitalisée à part.
    notionnels: dict[str, float]
    #: Ce que la règle d'indexation a fait de la pension depuis le départ, en
    #: termes RÉELS, scénario par scénario : un coefficient au-dessus de un
    #: veut dire que la pension a battu les prix.
    coefficients_notionnels: dict[str, float]
    #: Scénario 6 : la garantie d'aujourd'hui, et la rente du pilier capitalisé
    #: — qui garde son pouvoir d'achat —, dont sa part volontaire.
    garantie_vieillesse: float
    rente_capitalisee: float
    rente_capitalisee_volontaire: float
    #: Les deux termes de la garantie d'aujourd'hui : le plancher de l'année,
    #: et ce qu'il regarde — la pension obligatoire, répartition et rente
    #: capitalisée. ``garantie_ouverte`` dit si les 65 ans sont atteints,
    #: ``garantie_residence`` si la condition de résidence de l'ASPA l'est.
    garantie_ouverte: bool = False
    plancher_garantie: float = 0.0
    ressources_garantie: float = 0.0
    garantie_residence: bool = True

    def pension(self, scenario: str) -> float:
        """La pension annuelle d'aujourd'hui d'un des six scénarios."""
        if scenario == "actuel":
            return self.actuel.pension_annuelle
        return self.notionnels[scenario]

    def pension_totale(self, scenario: str) -> float:
        """Répartition et capitalisation réunies — seul le 6 a la seconde."""
        if scenario == "notionnel_liberal":
            return self.notionnels[scenario] + self.rente_capitalisee
        return self.pension(scenario)
