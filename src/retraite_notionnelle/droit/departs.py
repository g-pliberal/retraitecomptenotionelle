"""Le départ de chaque régime (docs/architecture.md, § 7.4).

Le droit ne connaît pas de départ « tous régimes » : chaque régime sert sa
pension quand l'assuré la demande et remplit SES conditions (fiche
``liquidation_regime_par_regime``). Le modèle liquidait tout à la date du
départ déclaré, à l'âge du régime le plus précoce : l'aide-soignante partie de
l'hôpital à cinquante-sept ans y touchait un régime général décoté que le droit
ne lui ouvre qu'à l'âge légal, et le militaire passé au privé voyait sa pension
militaire commencer avec les autres, trente ans après sa sortie de l'armée.

Cette étape dit, pour une carrière et son départ déclaré, QUAND chaque régime
liquide :

* une UNITÉ est un régime de base ou intégré, ou le groupe que la loi fait
  liquider ensemble — un régime et celui qui lui succède, les régimes alignés,
  les trois régimes du code des pensions (:func:`~.coordonner.groupes_de_succession`) ;
  chaque complémentaire suit l'unité avec laquelle ses années sont routées, et
  le RAFP n'ouvre qu'à l'âge légal (fiche ``rafp_age_d_ouverture``) ;
* chaque unité s'ouvre à SON âge — celui que l'étape « ouvrir le droit » lui
  oppose, carrière longue comprise — et se quitte à la fin de ses années ;
* la présomption ``depart_de_chaque_regime`` date la demande : au départ
  déclaré ; à l'ouverture, pour l'unité qui n'ouvre pas encore ; à la sortie
  de l'armée, pour la pension militaire, que L. 84 du code des pensions
  soustrait à l'extinction des droits et au cumul, et dont le montant ne
  dépend pas de ce que l'assuré fait ensuite. Toute autre pension demandée
  avant le départ figerait son taux sur la durée acquise à cette date,
  perdrait la surcote que l'activité poursuivie ouvre, et, depuis 2015,
  éteindrait les droits de cette activité (fiche
  ``droits_apres_la_premiere_pension``) : le modèle ne la présume pas.

Le départ reste UNIQUE quand toutes les unités liquident au départ déclaré, et
quand aucune n'y est ouverte : la page le dit alors non ouvert, comme avant.

:func:`liquider_les_departs` liquide ensuite chaque départ, dans l'ordre des
dates, chacun sur la carrière arrêtée à sa date et voyant les pensions déjà
servies. Le jumeau de ce module est ``moteur/js/droit/departs.js``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from . import compter, coordonner, ouvrir
from .commun import derniere_annee

if TYPE_CHECKING:
    from ..carriere import AnneeCarriere, Carriere
    from ..donnees.regimes import PeriodeRegime
    from ..scenarios.actuel import ScenarioActuel
    from .liquidation import Contexte, Liquidation

#: L'étage des régimes qui forment une unité : ceux qui servent la pension de
#: base, seuls ou avec leurs complémentaires.
ETAGES_DES_UNITES = frozenset({"base", "integre"})

#: Le RAFP, que l'article 6 du décret n° 2004-569 n'ouvre qu'à l'âge légal.
RAFP = "rafp"

#: Ce qui date un départ, par rapport au départ déclaré.
MOTIF_DEPART = "depart"
MOTIF_OUVERTURE = "ouverture"
MOTIF_SORTIE = "sortie"


@dataclass(frozen=True)
class Depart:
    """Un départ : le mois où il prend effet, et les régimes qui y liquident."""

    date: DateMois
    #: Les régimes qui liquident ce mois-là ; vide pour le départ unique, où
    #: tous liquident ensemble.
    regimes: frozenset[str] = field(default_factory=frozenset)
    #: ``depart``, au départ déclaré ; ``ouverture``, un régime qui n'ouvrait
    #: pas encore ; ``sortie``, la pension militaire, demandée à la sortie de
    #: l'armée.
    motif: str = MOTIF_DEPART

    @property
    def date_effet(self) -> str:
        """La date d'effet (AAAA-MM-JJ) : le premier jour du mois."""
        return f"{self.date.annee:04d}-{self.date.mois:02d}-01"

    @property
    def unique(self) -> bool:
        """Le départ unique, où tous les régimes liquident ensemble."""
        return not self.regimes


def _periode(moteur: ScenarioActuel, code: str, annee: int) -> PeriodeRegime | None:
    if code not in moteur.catalogue:
        return None
    regime = moteur.catalogue[code]
    return regime.periode(min(annee, derniere_annee(regime)))


def _routage(moteur: ScenarioActuel, carriere: Carriere
             ) -> list[tuple[AnneeCarriere, tuple[str, ...]]]:
    """Chaque ligne jusqu'au départ déclaré, et les régimes qui la reçoivent :
    le routage que toute l'acquisition lit (:func:`~.coordonner.coordonner`)."""
    plafond = moteur.macro.plafond_securite_sociale
    return [
        (ligne, tuple(coordonner.regimes_de(
            moteur, ligne, ligne.annee, carriere.date_entree(ligne.affiliation),
            revenu=ligne.revenu if ligne.cotise else ligne.revenu_reference,
            plafond=plafond(ligne.annee))))
        for ligne in carriere.lignes if ligne.annee <= carriere.annee_liquidation
    ]


def _acquiert(moteur: ScenarioActuel, code: str,
              routage: list[tuple[AnneeCarriere, tuple[str, ...]]]) -> bool:
    """Une ligne au moins ouvre-t-elle un droit dans ce régime ? Une période
    validée sans cotisation en ouvre (des trimestres) ; une année cotisée, si
    l'assiette du régime n'y est pas nulle — le RAFP ne prend que les primes,
    et le fonctionnaire qui n'en a pas n'y acquiert rien : il ne fait pas un
    départ de plus pour une pension nulle."""
    for ligne, regimes in routage:
        if code not in regimes:
            continue
        if not ligne.cotise:
            return True
        periode = _periode(moteur, code, ligne.annee)
        if periode is None or periode.part_du_revenu(ligne.revenu, ligne.part_primes) > 0:
            return True
    return False


def _unites(moteur: ScenarioActuel, carriere: Carriere, bases: list[str],
            routage: list[tuple[AnneeCarriere, tuple[str, ...]]]
            ) -> list[frozenset[str]]:
    """Les unités : chaque régime de base ou intégré, ceux que le droit fait
    liquider ensemble réunis, dans l'ordre de leur premier membre."""
    derniere: dict[str, int] = {}
    for ligne, regimes in routage:
        for code in regimes:
            derniere[code] = max(derniere.get(code, ligne.annee), ligne.annee)
    groupes = coordonner.groupes_de_succession(
        moteur, bases, carriere.annee_liquidation, derniere, carriere)
    unites: list[frozenset[str]] = []
    vus: set[str] = set()
    for code in bases:
        if code in vus:
            continue
        unite = frozenset(groupes.get(code, (code,)))
        vus |= unite
        unites.append(unite)
    return unites


def _ouverture(moteur: ScenarioActuel, carriere: Carriere,
               unite: frozenset[str]) -> DateMois:
    """Le premier mois où l'unité peut servir sa pension à cet assuré.

    L'âge que l'étape « ouvrir le droit » oppose à chacun de ses régimes — le
    plus précoce, puisque l'unité liquide d'un tenant —, ou celui de la
    carrière longue quand la durée COTISÉE au départ déclaré l'ouvre plus tôt.
    Après ce départ, l'assuré ne cotise plus : la carrière longue ne se
    projette pas, elle se lit acquise (:meth:`CarriereLongue.age_de_depart`).
    """
    annee = carriere.annee_liquidation
    periodes = [(code, periode) for code in sorted(unite)
                if (periode := _periode(moteur, code, annee)) is not None]
    annuites = [(c, p) for c, p in periodes if p.type_calcul == "annuites"]
    autres = [(c, p) for c, p in periodes if p.type_calcul != "annuites"]
    retenues = annuites or ouvrir.sans_ages_propres(autres)
    if not retenues:
        return carriere.date_liquidation
    age = min(ouvrir.age_ouverture(moteur, periode, carriere) for _, periode in retenues)
    opposent = annuites or ouvrir.periodes_opposant_une_duree(autres)
    longue = _carriere_longue_acquise(moteur, carriere, opposent)
    if longue is not None and longue < age:
        age = longue
    return carriere.date_de_l_age(age)


def _carriere_longue_acquise(moteur: ScenarioActuel, carriere: Carriere,
                             periodes: list[tuple[str, PeriodeRegime]]) -> float | None:
    """L'âge que la carrière longue ouvre aux régimes de ``periodes`` sur la
    durée cotisée au départ déclaré, ou ``None`` : la même lecture que
    :func:`~.ouvrir.age_carriere_longue`, sans la projection d'un assuré qui
    continuerait de cotiser."""
    if not periodes:
        return None
    requis = max(ouvrir.duree_requise(moteur, periode, carriere)[0]
                 for _, periode in periodes) or 160
    annee_liquidation = carriere.annee_liquidation
    cotises = carriere.trimestres_cumules(
        ligne for ligne in carriere.lignes
        if ligne.cotise and ligne.annee <= annee_liquidation)
    majoration = compter.majoration_pour_enfants(
        moteur, carriere, {code: cotises for code, _ in periodes}, annee_liquidation)
    cotises = moteur.carriere_longue.cotises_reputes(
        carriere, cotises, majoration.trimestres if majoration is not None else 0)
    anticipe = moteur.carriere_longue.age_de_depart(
        carriere, annee_liquidation, cotises, requis)
    return None if anticipe is None else anticipe[0]


def _sortie(carriere: Carriere, unite: frozenset[str],
            routage: list[tuple[AnneeCarriere, tuple[str, ...]]]) -> DateMois:
    """Le mois où l'assuré quitte l'unité : le 1er janvier qui suit sa dernière
    année d'activité dans ses régimes (présomption
    ``radiation_au_1er_janvier_suivant``), ou le départ déclaré s'il y
    travaille encore cette année-là."""
    declare = carriere.date_liquidation
    annees = [ligne.annee for ligne, regimes in routage
              if ligne.cotise and not unite.isdisjoint(regimes)]
    if not annees or max(annees) >= declare.annee:
        return declare
    return DateMois(max(annees) + 1, 1)


def _pension_militaire(moteur: ScenarioActuel, carriere: Carriere,
                       unite: frozenset[str]) -> bool:
    """L'unité sert-elle une pension militaire ? Celle de l'État, quand
    l'assuré n'y a servi que sous l'uniforme : il la garde à part, hors des
    régimes interpénétrés (:func:`~.coordonner.regimes_interpenetres`).

    C'est la seule que la présomption fasse demander avant le départ : la
    pension à jouissance immédiate est l'objet même de la retraite militaire,
    L. 84 du code des pensions la soustrait à L. 161-22, à L. 161-22-1 A puis
    à L. 161-22-1, et ce que l'assuré fait après sa sortie ne change pas
    son montant."""
    return ("fonction_publique_etat" in unite
            and "fonction_publique_etat" not in coordonner.regimes_interpenetres(
                moteur, carriere))


def age_legal(moteur: ScenarioActuel, carriere: Carriere) -> float:
    """L'âge de L. 161-17-2 pour la génération de l'assuré : celui du RAFP."""
    lu = moteur.ages_ouverture.age(carriere.generation)
    return lu[0] if lu is not None else 60.0


def departs(moteur: ScenarioActuel, carriere: Carriere) -> tuple[Depart, ...]:
    """Les départs de ``carriere``, dans l'ordre des dates.

    Un seul, le départ déclaré, quand tous les régimes y liquident ou
    qu'aucune unité n'y est ouverte ; sinon, un par date, chacun avec les
    régimes qu'il liquide. Aucun pour une carrière sans départ.
    """
    if carriere.age_liquidation is None:
        return ()
    declare = carriere.date_liquidation
    unique = (Depart(declare),)
    carriere = coordonner.retablir(moteur, carriere)
    routage = _routage(moteur, carriere)
    codes = sorted(code for code in {code for _, regimes in routage for code in regimes}
                   if _periode(moteur, code, carriere.annee_liquidation) is not None
                   and _acquiert(moteur, code, routage))
    bases = [code for code in codes
             if moteur.catalogue[code].etage in ETAGES_DES_UNITES]
    if not bases:
        return unique
    unites = _unites(moteur, carriere, bases, routage)
    unite_de = {code: i for i, unite in enumerate(unites) for code in unite}

    # Chaque complémentaire suit les unités dont elle partage les années.
    suivies: dict[str, set[int]] = {}
    for _, regimes in routage:
        indices = {unite_de[code] for code in regimes if code in unite_de}
        for code in regimes:
            if code in codes and code not in unite_de:
                suivies.setdefault(code, set()).update(indices)

    ouvertures = [_ouverture(moteur, carriere, unite) for unite in unites]
    if all(ouverture > declare for ouverture in ouvertures):
        return unique

    dates: dict[int, DateMois] = {}
    for i, unite in enumerate(unites):
        if ouvertures[i] > declare:
            dates[i] = ouvertures[i]
            continue
        plus_tot = max(ouvertures[i], _sortie(carriere, unite, routage))
        if plus_tot < declare and _pension_militaire(moteur, carriere, unite):
            dates[i] = plus_tot
        else:
            dates[i] = declare

    par_regime: dict[str, DateMois] = {code: dates[i] for code, i in unite_de.items()}
    for code, indices in suivies.items():
        par_regime[code] = max((dates[i] for i in indices), default=declare)
    if RAFP in par_regime:
        legal = carriere.date_de_l_age(age_legal(moteur, carriere))
        par_regime[RAFP] = max(par_regime[RAFP], legal)

    par_date: dict[DateMois, set[str]] = {}
    for code, quand in par_regime.items():
        par_date.setdefault(quand, set()).add(code)
    if set(par_date) == {declare}:
        return unique
    return tuple(
        Depart(quand, frozenset(par_date[quand]),
               MOTIF_DEPART if quand == declare
               else MOTIF_OUVERTURE if quand > declare else MOTIF_SORTIE)
        for quand in sorted(par_date))


@dataclass(frozen=True)
class PensionServie:
    """Une pension déjà liquidée, que les départs suivants voient servie : ce
    qu'elle vaut au mois de leur date d'effet, et son régime."""

    regime: str
    montant: float


def liquider_les_departs(moteur: ScenarioActuel, carriere: Carriere,
                         contexte: Contexte, nature: str = "definitive",
                         liste: tuple[Depart, ...] | None = None,
                         journal: object | None = None) -> list[Liquidation]:
    """Chaque départ liquidé, dans l'ordre des dates : sur la carrière arrêtée
    à sa date, pour ses seuls régimes, en voyant servies les pensions des
    départs qui le précèdent, menées jusqu'à lui (R. 173-7 : le minimum
    contributif s'écrête sur les pensions du mois de sa date d'effet)."""
    from . import liquidation as _liquidation
    from ..revalorisation import mener_au_mois

    liste = departs(moteur, carriere) if liste is None else liste
    liquidations: list[Liquidation] = []
    for depart in liste:
        demande = _liquidation.Demande(
            personne=carriere.personne, date_effet=depart.date_effet,
            date_evenement=depart.date_effet, nature=nature,
            regimes=() if depart.unique else tuple(sorted(depart.regimes)))
        servies = tuple(
            PensionServie(pension.regime, montant)
            for anterieure in liquidations
            for pension, montant in zip(anterieure.regimes, mener_au_mois(
                moteur, anterieure.regimes, anterieure.carriere.date_liquidation,
                depart.date)))
        etat = _liquidation.Etat(carriere.liquidee_au(depart.date), journal, servies)
        liquidations.append(_liquidation.liquider(demande, etat, contexte))
    return liquidations
