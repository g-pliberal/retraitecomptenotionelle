"""Les types du droit que le pont échange (action 161, étape 1 du retrait des
règles Python) : ce que les étapes du scénario 1 écrivent — pensions,
avantages, compléments, cumul, départs, foyer, liquidation, réversion,
seconde liquidation —, sans aucun corps de règle. Ils logeaient dans les
fichiers de ``droit/``, qui les réimportent le temps du retrait ; leurs jumeaux
sont ceux de ``moteur/js/droit/``.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..calendrier import DateMois
from ..donnees.chargement import Fiabilite
from ..somme import somme_ordonnee

#: La version du schéma de l'étape que :meth:`Foyer.donnees` suit.
SCHEMA_DU_FOYER = 1

#: La version du schéma de la réversion que :meth:`Reversion.donnees` suit.
SCHEMA_DE_LA_REVERSION = 1



@dataclass(frozen=True)
class PensionRegime:
    """Pension annuelle brute servie par un régime."""

    regime: str
    montant: float
    type_calcul: str
    detail: str
    fiabilite: Fiabilite
    #: Quand les régimes liquident à des dates différentes
    #: (:mod:`~retraite_notionnelle.droit.departs`) : la date d'effet de cette
    #: pension (AAAA-MM-JJ), et son montant à cette date, dans ses euros. Le
    #: champ ``montant`` est alors celui du départ déclaré — la pension servie
    #: avant lui y est menée, celle qui commence après y est ramenée par les
    #: prix. ``None`` pour un départ unique, où tout liquide à la même date.
    date_effet: str | None = None
    montant_a_l_effet: float | None = None
    #: La prestation versée en une fois, sous le seuil de points d'un régime
    #: qui en a un (le RAFP, décret n° 2004-569, article 9), ou la petite
    #: pension que son régime remplace par un versement unique — le régime
    #: général, l'Agirc-Arrco, l'Ircantec (:func:`~.completer.verser_en_capital`)
    #: — : ce capital, en euros de la liquidation ; ``None`` pour une rente.
    #: ``montant`` reste la rente qu'il remplace, et la réversion sait qu'il
    #: n'y en a pas après lui quand sa fiche le dit (``rien_apres_un_capital``).
    capital: float | None = None
    #: La majoration pour conjoint à charge que la pension porte (L. 351-13),
    #: depuis chaque date où elle change : ``((date, montant), ...)``, en
    #: euros courants, sans revalorisation. Celle de la date d'effet est dans
    #: ``montant`` ; la revalorisation sert celle de chaque échéance
    #: (:func:`majoration_du_conjoint`, fiche ``majoration_conjoint_a_charge``).
    conjoint: tuple[tuple[str, float], ...] = ()
    #: Ce que la réversion du régime général lit du maximum des pensions
    #: (fiche ``pension_maximale_regime_general``), aux euros de ``montant`` :
    #: ce que le maximum a retiré de la pension calculée, que la réversion
    #: reprend, la caisse la calculant sur la pension « sans être comparé[e] au
    #: minimum et au maximum » ; ce que la surcote ajoute à la pension ramenée,
    #: que le maximum de la réversion laisse passer (circulaire Cnav n° 2018-4,
    #: § 5) ; le coefficient de l'ajournement d'avant 1983 ou du taux acquis au
    #: 31 mars 1983, qui multiplie le maximum « opposable à l'assuré »
    #: (circulaire n° 120/82, § 4).
    ecretement_du_maximum: float = 0.0
    surcote: float = 0.0
    coefficient_du_maximum: float = 1.0
    #: La pension a-t-elle été liquidée sur la durée d'assurance maximum que sa
    #: date d'effet prenait en compte — 120 trimestres avant 1972, 128 en 1972,
    #: 136 en 1973, 144 en 1974 — ? Les majorations forfaitaires de 1972 à 1982
    #: le lisent (fiche ``majorations_forfaitaires_1972_1982``).
    sur_la_duree_maximum: bool = False
    #: Les planchers auxquels l'étape « compléter » a comparé la pension,
    #: chacun ``(nature, montant)`` — ``minimum``, la pension minimum d'avant
    #: le 1er avril 1983 (L. 345) ; ``avts`` et ``pension_d_invalidite``, le
    #: plancher de la pension substituée (L. 341-15) —, et la pension d'avant
    #: eux, aux euros de sa date d'effet. Les majorations forfaitaires de 1972
    #: à 1982 relèvent celle-ci, et des planchers ceux que leur version nomme :
    #: elles s'appliquaient « au montant de base, avant comparaison au minimum
    #: et au maximum » (exposé de la Cnav, « Montant de la retraite personnelle »).
    planchers: tuple[tuple[str, float], ...] = ()
    avant_les_planchers: float = 0.0


@dataclass(frozen=True)
class AvantageApplique:
    """Effet en euros d'un avantage non contributif du droit positif.

    Les trois avantages s'appliquent dans cet ordre, et l'ordre compte : la
    MDA ajoute des trimestres, donc modifie la décote et la proratisation AVANT
    que la majoration ne multiplie, et le minimum ne comble qu'ensuite. Leurs
    effets s'additionnent exactement au total : c'est ce qui rend la cascade
    vérifiable ligne à ligne.
    """

    code: str
    libelle: str
    montant: float
    detail: str = ""
    #: Part de chaque régime, dans l'ordre des pensions, quand l'avantage se
    #: répartit entre eux — la majoration pour enfants, plafond compris, et le
    #: minimum contributif.
    par_regime: tuple[tuple[str, float], ...] = ()
    #: Ce que les enfants À CHARGE à la date d'effet ajoutent à la majoration
    #: pour enfants, régime par régime, depuis chaque date où leur nombre
    #: change, la première étant la date d'effet : ``((date, ((régime, part),
    #: ...)), ...)``. Les parts de la première sont dans ``par_regime`` ; elles
    #: cessent avec la charge (:func:`parts_de_la_majoration`, fiche
    #: ``majoration_enfants_a_charge_agirc_arrco``).
    a_charge: tuple[tuple[str, tuple[tuple[str, float], ...]], ...] = ()
    #: Les parts de la majoration pour enfants nés ou élevés, régime par régime,
    #: sans le coefficient d'anticipation qui a pu réduire celles de
    #: ``par_regime``, sous le même plafond : ce que la réversion reprend quand
    #: sa version le dit (:func:`parts_sans_anticipation`, fiche
    #: ``reversion_agirc_arrco``).
    par_regime_sans_anticipation: tuple[tuple[str, float], ...] = ()


@dataclass(frozen=True)
class MajorationProportionnelle:
    """Ce que les plans de revalorisation de 1997 à 2008 ajoutent à la
    retraite proportionnelle du chef d'exploitation
    (:func:`majoration_retraite_proportionnelle`)."""

    #: Le nombre minimal annuel moyen de points, A ou C, et le nombre annuel
    #: moyen n de la pension, au plancher de seize.
    minimum: float
    moyenne: float
    #: Les années retenues, DCE, trente-sept et demie au plus.
    duree: float
    #: Les points ajoutés, minorés et réduits à la part servie, ceux des
    #: années de conjoint compris, et leur montant.
    points: float
    complement: float
    fiabilite: Fiabilite
    #: Ceux des années de conjoint et d'aide familial : le nombre minimal
    #: annuel B (ou C), les années retenues, les points qu'elles ajoutent,
    #: minorés (:func:`_points_des_conjoints`).
    conjoint_minimum: float = 0.0
    conjoint_annees: float = 0.0
    conjoint_points: float = 0.0


@dataclass(frozen=True)
class MinimumEcrete:
    """Ce que la révision du minimum contributif relit après le départ : sa
    majoration « est révisée lorsque le montant des avantages personnels de
    retraite a varié », et le plafond auquel le total des pensions se compare
    est celui de l'entrée en jouissance, « revalorisé [...] dans les
    conditions prévues à l'article L. 161-23-1 » (R. 173-8). En euros de la
    liquidation."""

    #: Le complément de tous les régimes, avant l'écrêtement.
    avant_ecretement: float
    #: Ce qui sépare les pensions du plafond de l'article L. 173-2 : le
    #: plafond, moins les pensions, celles d'autres départs et les pensions
    #: étrangères qu'il compte ; négatif quand elles le dépassent.
    marge: float
    #: Le complément de chaque régime, après l'écrêtement.
    par_regime: tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class PetitePension:
    """Ce que la majoration exceptionnelle des petites pensions relit d'une
    pension de base liquidée avant le 1er septembre 2023 (loi n° 2023-270,
    article 18, V ; décret n° 2023-754, article 3 ; circulaire Cnav
    n° 2023-21) : :func:`~retraite_notionnelle.revalorisation.majorer_les_petites_pensions`
    la calcule le mois où elle est due, sur ce que les pensions servent alors.
    Ses régimes sont ceux qui portent le minimum contributif : le régime
    général, les régimes des artisans et des commerçants qu'il a intégrés,
    celui des salariés agricoles et celui des cultes. En euros de la date
    d'effet de la pension."""

    #: Le régime « concerné », qui sert la pension et doit la majoration.
    regime: str
    #: Liquidée au taux plein, par la durée, l'âge ou l'inaptitude
    #: (circulaire, 2.2).
    taux_plein: bool
    #: Les durées cotisée et validée dans le régime, en trimestres, et la
    #: durée d'assurance maximum de la génération (L. 351-1, troisième
    #: alinéa), qui proratise la majoration sur la première et son plafond
    #: sur la seconde (circulaire, 3.1 et 3.2.2).
    cotisee: int
    validee: int
    maximum: int
    #: Les trimestres cotisés tous régimes de base, français et étrangers,
    #: quatre par an au plus, l'AVPF exclue : cent vingt ouvrent la majoration
    #: (circulaire, 2.3).
    cotises_tous_regimes: int
    #: Ce que la surcote ajoute à la pension, que la comparaison aux plafonds
    #: écarte (circulaire, 3.2.3).
    surcote: float = 0.0


@dataclass(frozen=True)
class ChefDExploitation:
    """Ce que le relèvement de septembre 2023 relit d'un chef d'exploitation
    parti avant : le taux plein ouvre depuis les points gratuits et le
    complément différentiel de la RCO à qui n'avait pas la durée requise tous
    régimes (loi n° 2023-270, article 18, VI) ;
    :func:`~retraite_notionnelle.revalorisation.relever_les_exploitants` les
    calcule au 1er septembre 2023, sur ce que ses pensions servent alors."""

    #: Le régime de base des non-salariés agricoles.
    regime: str
    #: Son taux plein, la durée requise, ses durées et sa durée de référence
    #: (:class:`~retraite_notionnelle.droit.liquider.EligibleAgricole`).
    eligible: object
    #: Les points de RCO acquis à la liquidation au titre des années de chef,
    #: par cotisation ou à titre gratuit : le N du complément (D. 732-166-4,
    #: :func:`points_rco_de_chef`).
    points: float
    #: Les points gratuits que le taux plein ouvre, quand la durée requise ne
    #: les avait pas ouverts à la liquidation (L. 732-56, D. 732-154).
    gratuits: float
    #: Le complément différentiel a-t-il été servi à la liquidation ?
    complement: bool


@dataclass(frozen=True)
class ExploitantAgricole:
    """Ce que la révision des pensions des non-salariés agricoles déjà
    liquidées relit de leur liquidation : les plans de revalorisation de 1997
    à 2008, servis chaque année à la règle des pensions dues cette année-là —
    celles prises avant 1997 comprises —, puis la pension majorée de référence
    que la loi n° 2008-1330 ouvre en 2009 aux pensions prises avant
    (:func:`~retraite_notionnelle.revalorisation.reviser_les_exploitants`)."""

    #: Le régime de base des non-salariés agricoles.
    regime: str
    #: La carrière du départ qui l'a liquidée, sa date d'effet comprise.
    carriere: object
    #: Son :class:`~retraite_notionnelle.droit.liquider.EligibleAgricole`.
    eligible: object
    #: Sa durée d'assurance, en trimestres.
    trimestres: int
    #: La pension de base avant les plans et la pension majorée de référence.
    pension: PensionRegime
    #: La majoration des plans servie à la liquidation (:class:`MajorationProportionnelle`).
    plans: MajorationProportionnelle | None
    #: La pension majorée de référence servie à la liquidation, en euros de
    #: la date d'effet : celle d'une pension prise de 2009 à 2021 se refait
    #: depuis 2022 à la règle unique (loi n° 2021-1679, article 1er, II).
    pmr: float = 0.0
    #: La durée de chef d'une pension prise avant 1997, en trimestres, que ses
    #: points au compte reconstituent pour la pension majorée de référence de
    #: 2009 (:func:`duree_de_chef_reconstituee`) ; ``None`` pour une autre.
    chef_reconstitue: float | None = None


#: Ce que le droit fait d'une pension, pour un mois d'activité.
LIBRE = "libre"


INTEGRAL = "integral"


PLAFONNEE = "plafonnee"


NON_DUE = "non_due"


SUSPENDUE = "suspendue"


REDUITE = "reduite"


SEUIL_NON_PUBLIE = "seuil_non_publie"


NON_CALCULE = "non_calcule"


#: L'ordre où se dit le statut d'un mois : celui de la pension la plus
#: touchée.
PRIORITE = (NON_DUE, SUSPENDUE, REDUITE, SEUIL_NON_PUBLIE, NON_CALCULE, PLAFONNEE,
            INTEGRAL, LIBRE)


@dataclass(frozen=True)
class PensionEnCumul:
    """Ce que le droit fait d'une pension, des mois d'une tranche."""

    regime: str
    #: :data:`LIBRE`, :data:`INTEGRAL`, :data:`PLAFONNEE`, :data:`NON_DUE`,
    #: :data:`SUSPENDUE`, :data:`REDUITE`, :data:`SEUIL_NON_PUBLIE` ou
    #: :data:`NON_CALCULE`.
    statut: str
    #: La version de la fiche qui le dit, et pourquoi.
    regle: str
    motif: str
    #: La pension du mois, et ce qui n'en est pas servi, en euros de l'année.
    montant: float
    reduction: float
    #: Le plafond mensuel de la règle qui la touche, ou ``None``.
    plafond: float | None = None

    def donnees(self) -> dict:
        return {"regime": self.regime, "statut": self.statut, "regle": self.regle,
                "motif": self.motif, "montant": self.montant, "reduction": self.reduction,
                "plafond": self.plafond}


@dataclass(frozen=True)
class TrancheDeCumul:
    """Des mois consécutifs d'une même année, où le droit traite chaque pension
    de la même façon. Les montants sont mensuels, en euros de l'année."""

    debut: DateMois
    #: Le premier mois qui n'en est plus.
    fin: DateMois
    #: Le revenu brut de l'activité, et toutes les pensions servies, avant
    #: réduction.
    revenu: float
    pensions: float
    #: Le plafond de la règle qui touche la pension, ou ``None``.
    plafond: float | None
    par_regime: tuple[PensionEnCumul, ...]

    @property
    def mois(self) -> int:
        return self.fin.rang - self.debut.rang

    @property
    def reduction(self) -> float:
        """Ce qui n'est pas servi, par mois."""
        return somme_ordonnee(p.reduction for p in self.par_regime)

    @property
    def principale(self) -> PensionEnCumul | None:
        """La pension qui dit le statut de la tranche : la plus touchée."""
        return min(self.par_regime, key=lambda p: PRIORITE.index(p.statut), default=None)

    @property
    def statut(self) -> str:
        principale = self.principale
        return principale.statut if principale is not None else LIBRE

    def donnees(self) -> dict:
        principale = self.principale
        return {"debut": jour(self.debut), "fin": jour(self.fin), "mois": self.mois,
                "statut": self.statut,
                "regle": principale.regle if principale is not None else None,
                "motif": principale.motif if principale is not None else None,
                "revenu": self.revenu, "pensions": self.pensions, "plafond": self.plafond,
                "reduction": self.reduction,
                "par_regime": [p.donnees() for p in self.par_regime]}


@dataclass(frozen=True)
class Cumul:
    """L'activité exercée après le départ, et ce que chaque pension en garde."""

    debut: DateMois
    fin: DateMois
    affiliation: str
    #: ``dernier`` ou ``autre``.
    employeur: str
    #: Le groupe de régimes dont relève l'activité (:func:`groupe_de_l_activite`).
    groupe: str | None
    #: Le mois où le cumul devient intégral, s'il le devient pendant l'activité.
    integral_depuis: DateMois | None
    tranches: tuple[TrancheDeCumul, ...]

    @property
    def non_servi(self) -> float:
        """Ce que l'activité fait perdre de pension, en tout, en euros de
        chaque année."""
        return somme_ordonnee(t.reduction * t.mois for t in self.tranches)

    def donnees(self) -> dict:
        return {"debut": jour(self.debut), "fin": jour(self.fin),
                "affiliation": self.affiliation, "employeur": self.employeur,
                "groupe": self.groupe,
                "integral_depuis": (jour(self.integral_depuis)
                                    if self.integral_depuis is not None else None),
                "non_servi": self.non_servi,
                "tranches": [t.donnees() for t in self.tranches]}


def jour(date_mois: DateMois) -> str:
    return f"{date_mois.annee:04d}-{date_mois.mois:02d}-01"


@dataclass(frozen=True)
class DemandeExaminee:
    """Une pension dont la personne dit la date de demande, et la date où le
    modèle la sert : la demandée quand elle vient après la présumée, la
    présumée sinon, avec sa raison."""

    regime: str
    demandee: DateMois
    #: Le mois où la pension commence ; ``None`` sans pension de ce régime.
    retenue: DateMois | None
    #: ``demande`` : la date demandée ; ``depart``, ``ouverture``, ``sortie``,
    #: ``invalidite``, ``radiation`` ou ``limite_d_age`` : la date présumée,
    #: que la demande
    #: n'avance pas ;
    #: ``ensemble`` : celle de la pension que la loi lui attache ;
    #: ``sans_pension`` : la carrière n'a pas de pension dans ce régime.
    motif: str

    def donnees(self) -> dict:
        return {"regime": self.regime, "demandee": jour(self.demandee),
                "retenue": None if self.retenue is None else jour(self.retenue),
                "motif": self.motif}


#: Les trois barèmes de l'allocation : une personne seule ; un couple dont la
#: personne est seule allocataire, au plus le montant d'une personne seule
#: (D. 815-1, a) ; un couple dont les deux membres le sont, qui se partagent
#: le montant du couple par moitié (D. 815-1, b).
PERSONNE_SEULE = "personne_seule"


COUPLE = "couple"


DEUX_ALLOCATAIRES = "deux_allocataires"


#: Ce que la cascade des avantages dit de chacun.
DETAILS = {
    PERSONNE_SEULE: "allocation différentielle, barème d'une personne seule",
    COUPLE: ("allocation différentielle, plafond du couple, au plus le montant "
             "d'une personne seule"),
    DEUX_ALLOCATAIRES: ("allocation différentielle, barème d'un couple "
                        "d'allocataires, servie par moitié"),
}


#: Ce qu'elle en dit avant 2007, quand le minimum tient en deux étages.
DETAILS_DEUX_ETAGES = {
    PERSONNE_SEULE: ("allocation aux vieux travailleurs salariés et allocation "
                     "supplémentaire, sous le plafond d'une personne seule"),
    COUPLE: ("allocation aux vieux travailleurs salariés et allocation "
             "supplémentaire, sous le plafond du couple"),
    DEUX_ALLOCATAIRES: ("allocation aux vieux travailleurs salariés et allocation "
                        "supplémentaire du ménage, sous le plafond du couple, "
                        "servie par moitié"),
}


@dataclass(frozen=True)
class Foyer:
    """Ce que l'étape « foyer et net » écrit, à une date."""

    personne: str
    #: La date à laquelle les ressources sont lues : l'effet de la
    #: liquidation, ou l'échéance (AAAA-MM-JJ).
    date: str | None
    #: Toutes les pensions que le bénéficiaire reçoit, régimes provisionnés,
    #: majorations et pensions étrangères compris.
    ressources: float
    #: L'ASPA : le complément jusqu'au barème, nul quand les ressources
    #: l'atteignent — pour un couple d'allocataires, la part de la personne.
    minimum_vieillesse: float
    #: Le barème lu, quand l'allocation est ouverte : celui d'une personne
    #: seule, ou le plafond du couple.
    plafond: float | None
    fiabilite: Fiabilite
    #: Celles des ressources qu'un autre État sert, à part des pensions
    #: françaises : l'allocation ne complète que ce qu'elles laissent.
    etrangeres: float = 0.0
    #: Le barème du foyer : :data:`PERSONNE_SEULE`, :data:`COUPLE` ou
    #: :data:`DEUX_ALLOCATAIRES`.
    bareme: str = PERSONNE_SEULE
    #: Les ressources du conjoint, que le plafond du couple compte avec les
    #: siennes : déclarées, nulles sinon ; nulles sans conjoint.
    ressources_conjoint: float = 0.0
    #: Avant 2007, le minimum à deux étages (:func:`avant_l_aspa`) : il ne
    #: porte pas les ressources au plafond, qu'il ne fait que borner.
    deux_etages: bool = False

    def avantage(self) -> AvantageApplique:
        """L'ASPA, sous la forme où la cascade des avantages la dit."""
        return AvantageApplique(
            code="minimum_vieillesse",
            libelle="Minimum vieillesse (ASPA)",
            montant=self.minimum_vieillesse,
            detail=(DETAILS_DEUX_ETAGES if self.deux_etages else DETAILS)[self.bareme],
        )

    def servie_avec(self, pensions: float) -> float:
        """Les pensions françaises de la personne et l'allocation, ensemble :
        le barème d'une personne seule, moins ce que les pensions étrangères,
        servies à part, en remplissent ; dans un couple, ses pensions et sa
        part de l'allocation, que le barème ne dit plus ; avant 2007, ses
        pensions et les deux étages, que le plafond borne sans les y porter."""
        if self.bareme == PERSONNE_SEULE and not self.deux_etages:
            return self.plafond - self.etrangeres
        return pensions + self.minimum_vieillesse

    def donnees(self) -> dict:
        """Le foyer, tel que le schéma de l'étape le décrit."""
        return {"schema_version": SCHEMA_DU_FOYER, "personne": self.personne,
                "date": self.date, "ressources": self.ressources,
                "etrangeres": self.etrangeres, "bareme": self.bareme,
                "ressources_conjoint": self.ressources_conjoint,
                "minimum_vieillesse": self.minimum_vieillesse,
                "fiabilite": self.fiabilite.name.lower()}


@dataclass(frozen=True)
class Demande:
    """La demande (contrat C.6, ``demande``)."""

    personne: str
    #: La date d'effet (AAAA-MM-JJ) ; ``None`` pour une carrière sans départ.
    date_effet: str | None
    #: L'événement qui l'appelle — sa sorte au vocabulaire — et sa date.
    evenement: str = "depart"
    date_evenement: str | None = None
    motif: str = "vieillesse"
    nature: str = "definitive"
    #: Les régimes que la demande vise ; aucun : tous ceux où un droit est
    #: acquis, quand ils liquident tous au même départ (:mod:`.departs`).
    regimes: tuple[str, ...] = ()

    def donnees(self) -> dict:
        """La demande, telle que le contrat C.6 la décrit. Les régimes qu'elle
        ne nomme pas encore sont un manque, que le tableau de bord compte."""
        donnee = {"personne": self.personne, "date_effet": self.date_effet,
                  "evenement": {"sorte": self.evenement,
                                "date": self.date_evenement or self.date_effet},
                  "motif": self.motif, "nature": self.nature}
        if self.regimes:
            donnee["regimes"] = list(self.regimes)
        return donnee


@dataclass(frozen=True)
class Mesure:
    """Ce qu'une liquidation d'essai mesure (contrat C.6, ``mesure``)."""

    code: str
    neutralisation: str
    montant: float


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


#: Ce qui ouvre la demande, ou ce qui la ferme.
OUVERTE = "ouverte"


@dataclass(frozen=True)
class ReversionRegime:
    """La réversion d'un régime du défunt."""

    regime: str
    #: La pension du défunt dans ce régime, à l'année des montants.
    base: float
    montant: float
    motif: str
    fiche: str | None = None
    version: str | None = None
    texte: str | None = None
    taux: float = 0.0
    #: La date d'effet (AAAA-MM-JJ) : le premier jour du mois qui suit le
    #: décès, ou qui suit l'âge requis.
    date_effet: str | None = None
    fiabilite: Fiabilite = Fiabilite.ESTIMEE
    #: La part du montant qui reverse la majoration pour enfants du défunt,
    #: hors du taux : l'Agirc-Arrco la reverse en entier depuis 2019.
    majoration: float = 0.0
    #: Le minimum que D. 353-1 garantit à cette réversion du régime général ou
    #: d'un régime aligné, soixantièmes et prorata faits, ou l'article 18 du
    #: décret n° 2008-639 à celle de la SNCF, sa part faite ; 0 sans lui.
    minimum: float = 0.0
    #: La majoration de 10 % du survivant de trois enfants (L. 353-1, R. 353-2),
    #: comprise dans le montant.
    majoration_trois_enfants: float = 0.0
    #: La majoration de 11,1 % du survivant aux petites retraites (L. 353-6),
    #: et le jour où elle commence : comprise dans le montant quand elle
    #: commence au plus tard à la date d'effet de la ligne, à part sinon.
    majoration_petites_retraites: float = 0.0
    majoration_petites_retraites_effet: str | None = None
    #: La part de ``base`` que le minimum contributif y ajoute (L. 351-10) :
    #: la réversion du régime général et des régimes alignés se calcule sans
    #: elle, sur ``base - minimum_contributif``.
    minimum_contributif: float = 0.0
    #: Ce que le maximum des pensions avait retiré de ``base``, que la
    #: réversion du régime général reprend, et le maximum de cette réversion :
    #: son taux du maximum des pensions de l'année, l'ajournement d'avant 1983
    #: le majorant, et de la surcote du défunt ; 0 sans lui.
    ecretement_du_maximum: float = 0.0
    maximum: float = 0.0
    #: Le plafond de ressources auquel la réversion se mesure — celui d'une
    #: personne seule ou du ménage au régime général, deux plafonds de la
    #: Sécurité sociale à la complémentaire des indépendants —, et les
    #: ressources qu'il retient à côté d'elle : celles du survivant, ses
    #: revenus d'activité abattus, celles de son nouveau conjoint s'il vit en
    #: couple, les réversions des autres régimes de base ; 0 sans plafond.
    plafond: float = 0.0
    ressources_retenues: float = 0.0
    #: Ce plafond est-il celui du ménage : le survivant vit en couple au jour
    #: qu'il mesure, et les ressources de son nouveau conjoint s'ajoutent aux
    #: siennes, sous 1,6 fois le plafond d'une personne seule au régime
    #: général, sous le même à la complémentaire des indépendants. Non quand
    #: l'union se forme après ce jour — la révision qui suit la compte —, ni
    #: avant juillet 2004, qui ne compte que ses ressources personnelles.
    plafond_du_menage: bool = False
    #: Les mois de la période de référence de ces ressources, à la date
    #: d'effet (R. 353-1) : les trois mois civils qui la précèdent, les douze
    #: quand celles des trois mois excèdent le quart du plafond ; 0 quand la
    #: version les compare sur l'année, à leur montant de ce jour.
    periode_de_reference: int = 0
    #: Le moment que précèdent ces mois : la date d'effet (``date_d_effet``),
    #: depuis juillet 2004 ; avant, la demande (``demande``), puis le décès
    #: (``deces``) quand la condition n'est pas remplie à la demande — le
    #: dernier examiné quand elle ne l'est à aucun. ``None`` sans plafond.
    ressources_examinees_au: str | None = None
    #: Les moments dont la version a examiné les ressources, dans l'ordre,
    #: jusqu'à celui-là : aucun de ceux qui le précèdent ne remplissait la
    #: condition — avant juillet 2004, la demande refusée, quand les ressources
    #: retenues sont celles du décès. Vide quand ``ressources_examinees_au``
    #: est ``None``.
    moments_examines: tuple[str, ...] = ()
    #: La part du survivant dans la réversion du régime, partagée avec les
    #: précédents conjoints au prorata des mariages (L. 353-3) : 1 sans eux.
    part: float = 1.0
    #: Le jour où l'union nouvelle du survivant éteint la réversion
    #: (``perte_au_remariage``), quand elle suit la date d'effet ; ``None``
    #: sinon.
    fin: str | None = None
    #: La limite de cumul de la réversion d'avant juillet 2004 avec les
    #: retraites personnelles du survivant (D. 355-1) : la plus haute de la
    #: limite forfaitaire, de la limite calculée et de la réversion même ;
    #: 0 sans elle.
    limite_cumul: float = 0.0
    #: La majoration forfaitaire pour enfant à charge (L. 353-5), comprise
    #: dans le montant, et ce qu'elle devient ensuite : depuis chaque jour où
    #: le nombre des enfants à charge change, ``(jour, montant)``, la dernière
    #: étape nulle — le dernier enfant n'est plus à charge, ou le survivant a
    #: sa propre retraite.
    majoration_forfaitaire_enfants: float = 0.0
    majoration_forfaitaire_enfants_etapes: tuple[tuple[str, float], ...] = ()
    #: Les majorations forfaitaires qui relèvent la réversion après sa date
    #: d'effet — 4 % au 1er décembre 1982, 3,846 % au 1er janvier 1995 —,
    #: chacune ``(jour, montant)``, hors du montant.
    majorations_forfaitaires: tuple[tuple[str, float], ...] = ()
    #: Le jour où la retraite personnelle du survivant, qui suit la date
    #: d'effet, revoit la réversion d'avant juillet 2004 par la limite de cumul
    #: de ce jour (D. 355-1), et ce qu'elle en retire alors, majoration de 10 %
    #: comprise, hors du montant : ``None`` et 0 sans elle. ``limite_cumul``
    #: est alors la limite de ce jour.
    cumul_effet: str | None = None
    reduction_du_cumul: float = 0.0
    #: Le jour de la dernière révision de la réversion sous le plafond de
    #: ressources (R. 353-1-1) — le recalcul aux règles de 2004 qu'ouvre la
    #: retraite du survivant quand elle les précède, la révision qui suit sa
    #: retraite, le ménage qu'il forme ou ses cinquante-cinq ans sinon —, et ce
    #: qu'elle en retire alors, majoration de 10 % comprise, négatif quand elle
    #: y ajoute, hors du montant : ``None`` et 0 sans révision. ``revisions``
    #: les dit toutes, ``(jour, ce qu'elle retire)``, dans l'ordre.
    revision_effet: str | None = None
    reduction_de_la_revision: float = 0.0
    revisions: tuple[tuple[str, float], ...] = ()
    #: Les ressources que chaque révision retient à côté de la réversion, par
    #: an, ``(jour, ressources)`` dans l'ordre de ``revisions`` : celles des
    #: trois mois qui la précèdent (:func:`_ressources_de_la_periode`), et les
    #: réversions des autres régimes de base ce jour-là.
    ressources_des_revisions: tuple[tuple[str, float], ...] = ()
    #: Le jour d'où la réversion soumise aux règles de ressources n'est plus
    #: révisable (R. 353-1-1) : trois mois après la retraite que le survivant
    #: date ; sa date d'effet quand il a, sans la dater, des retraites ; le
    #: mois qui suit son âge légal quand il n'a ni retraite ni activité ;
    #: ``None`` quand il travaille sans retraite datée, et pour la réversion
    #: d'avant juillet 2004 qu'aucune retraite n'a recalculée.
    derniere_revision: str | None = None

    def donnees(self) -> dict:
        return {"regime": self.regime, "base": self.base, "taux": self.taux,
                "montant": self.montant, "motif": self.motif,
                "date_effet": self.date_effet, "fiche": self.fiche,
                "version": self.version, "texte": self.texte,
                "fiabilite": self.fiabilite.name.lower(),
                "majoration": self.majoration, "minimum": self.minimum,
                "majoration_trois_enfants": self.majoration_trois_enfants,
                "majoration_petites_retraites": self.majoration_petites_retraites,
                "majoration_petites_retraites_effet":
                    self.majoration_petites_retraites_effet,
                "minimum_contributif": self.minimum_contributif,
                "ecretement_du_maximum": self.ecretement_du_maximum,
                "maximum": self.maximum, "plafond": self.plafond,
                "ressources_retenues": self.ressources_retenues,
                "plafond_du_menage": self.plafond_du_menage,
                "periode_de_reference": self.periode_de_reference,
                "ressources_examinees_au": self.ressources_examinees_au,
                "moments_examines": list(self.moments_examines), "part": self.part,
                "fin": self.fin, "limite_cumul": self.limite_cumul,
                "majoration_forfaitaire_enfants": self.majoration_forfaitaire_enfants,
                "majoration_forfaitaire_enfants_etapes": [
                    {"date": jour, "montant": montant}
                    for jour, montant in self.majoration_forfaitaire_enfants_etapes],
                "majorations_forfaitaires": [
                    {"date": jour, "montant": montant}
                    for jour, montant in self.majorations_forfaitaires],
                "cumul_effet": self.cumul_effet,
                "reduction_du_cumul": self.reduction_du_cumul,
                "revision_effet": self.revision_effet,
                "reduction_de_la_revision": self.reduction_de_la_revision,
                "revisions": [{"date": jour, "reduction": reduction,
                               "ressources": dict(self.ressources_des_revisions).get(jour)}
                              for jour, reduction in self.revisions],
                "derniere_revision": self.derniere_revision}


@dataclass(frozen=True)
class Reversion:
    """Ce que la liquidation d'une réversion écrit : régime par régime."""

    #: Le survivant, et le défunt dont les régimes servent la réversion.
    personne: str
    defunt: str
    #: Le décès (AAAA-MM-JJ), et l'année dont les montants sont les euros.
    deces: str
    annee: int
    #: Les ressources du survivant hors réversions, et si elles sont présumées.
    ressources: float
    ressources_presumees: bool
    regimes: tuple[ReversionRegime, ...]
    #: Le décès est-il supposé (présomption ``deces_apres_le_depart``) plutôt
    #: que déclaré ?
    deces_suppose: bool = False
    #: Le défunt est-il mort avant son départ ? La réversion porte alors sur
    #: la pension qu'il « eût obtenue » à son décès (R. 353-6).
    avant_le_depart: bool = False

    @property
    def total(self) -> float:
        return somme_ordonnee(r.montant for r in self.regimes)

    def donnees(self) -> dict:
        return {"schema_version": SCHEMA_DE_LA_REVERSION, "personne": self.personne,
                "defunt": self.defunt, "deces": self.deces,
                "deces_suppose": self.deces_suppose,
                "avant_le_depart": self.avant_le_depart, "annee": self.annee,
                "ressources": self.ressources,
                "ressources_presumees": self.ressources_presumees,
                "total": self.total,
                "regimes": [r.donnees() for r in self.regimes]}


@dataclass(frozen=True)
class PeriodeDeDroits:
    """Des mois consécutifs d'activité que le droit traite de même."""

    debut: DateMois
    fin: DateMois
    #: :data:`NOUVELLE_PENSION`, :data:`ETEINTS`, :data:`DERNIER_EMPLOYEUR` ou
    #: :data:`REGIMES_NON_LIQUIDES`.
    motif: str
    #: La version de la fiche ``droits_apres_la_premiere_pension``.
    regle: str

    def donnees(self) -> dict:
        return {"debut": jour(self.debut), "fin": jour(self.fin), "motif": self.motif,
                "regle": self.regle}


@dataclass(frozen=True)
class NouvellePension:
    """La nouvelle pension d'un régime, ou la seconde retraite complémentaire."""

    regime: str
    date_effet: DateMois
    #: Les trimestres validés et le salaire mensuel moyen de la période — le
    #: revenu annuel moyen, pour l'indépendant —, en euros de l'année de la
    #: date d'effet ; les points, pour l'Agirc-Arrco.
    trimestres: int
    salaire_mensuel: float
    points: float
    #: Par an, avant le plafond, le plafond, et le montant servi, en euros de
    #: l'année de la date d'effet.
    brute: float
    plafond: float | None
    montant: float
    revenu_annuel_moyen: float = 0.0
    #: Le versement forfaitaire unique qui la remplace, en euros de sa date
    #: d'effet, ou ``None`` : la seconde pension du RCI de moins de quarante
    #: points (fiche ``versement_unique_rci``) ; ``montant`` reste la pension
    #: qu'il remplace.
    capital: float | None = None

    def donnees(self) -> dict:
        return {"regime": self.regime, "date_effet": jour(self.date_effet),
                "trimestres": self.trimestres, "salaire_mensuel": self.salaire_mensuel,
                "revenu_annuel_moyen": self.revenu_annuel_moyen,
                "points": self.points, "brute": self.brute, "plafond": self.plafond,
                "montant": self.montant, "capital": self.capital}


@dataclass(frozen=True)
class PensionDeRegimeNouveau:
    """La pension d'un régime que l'activité après le départ ouvre, liquidée à
    sa date : par an, en euros de cette date."""

    regime: str
    date_effet: DateMois
    montant: float
    detail: str

    def donnees(self) -> dict:
        return {"regime": self.regime, "date_effet": jour(self.date_effet),
                "montant": self.montant, "detail": self.detail}


@dataclass(frozen=True)
class DroitsApresDepart:
    """Ce que l'activité après le départ ouvre de droits, mois par mois, et
    les pensions nouvelles qu'elle constitue."""

    periodes: tuple[PeriodeDeDroits, ...]
    pensions: tuple[NouvellePension, ...]
    #: Les régimes de base de l'activité dont le modèle ne calcule pas la
    #: nouvelle pension.
    non_calcules: tuple[str, ...]
    #: Les pensions des régimes qui n'en servaient pas, que l'activité ouvre
    #: (:func:`liquider_les_regimes_nouveaux`).
    regimes_nouveaux: tuple[PensionDeRegimeNouveau, ...] = ()

    @property
    def montant(self) -> float:
        return somme_ordonnee(p.montant for p in self.pensions)

    def donnees(self) -> dict:
        return {"periodes": [p.donnees() for p in self.periodes],
                "pensions": [p.donnees() for p in self.pensions],
                "non_calcules": list(self.non_calcules), "montant": self.montant,
                "regimes_nouveaux": [p.donnees() for p in self.regimes_nouveaux]}
