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
  ``droits_apres_la_premiere_pension``) : le modèle ne la présume pas ;
* le fonctionnaire radié des cadres pour invalidité liquide sa pension à la
  radiation, à tout âge (fiche ``retraite_pour_invalidite_fonction_publique``) ;
* la pension de vieillesse de l'ex-invalide remplace sa pension d'invalidité
  d'office, au premier jour du mois qui suit l'âge de la substitution, dans
  le régime général et les régimes alignés, avant son départ déclaré s'il le
  faut ; l'invalide qui travaille la demande à son départ, au plus tard à
  l'âge du taux plein automatique ; le demandeur d'emploi indemnisé, six
  mois après l'âge au plus tard (:func:`~.invalidite.substitution`) ;
* la personne peut DIRE la date où elle demande une pension
  (:attr:`~retraite_notionnelle.carriere.Carriere.demandes_de_pension`) : une
  date plus tardive que la présumée la remplace — pour éviter une décote qui
  tient à l'âge, toucher la surcote qu'un régime accorde à l'âge seul —, et
  une unité prend la plus tardive des demandes de ses régimes ; une date plus
  précoce ne l'avance pas, et :class:`DemandeExaminee` dit pourquoi. Une
  pension demandée avant le départ ferait de la fin de la carrière une
  activité exercée après une première pension : c'est le départ qui se
  déclare alors à cette date, et l'activité qui suit comme une activité après
  le départ (:mod:`.cumul`, :mod:`.seconde`).

Le départ reste UNIQUE quand toutes les unités liquident au départ déclaré, et
quand aucune n'y est ouverte sans que rien soit demandé plus tard : la page le
dit alors non ouvert, comme avant.

:func:`liquider_les_departs` liquide ensuite chaque départ, dans l'ordre des
dates, chacun sur la carrière arrêtée à sa date et voyant les pensions déjà
servies. Le jumeau de ce module est ``moteur/js/droit/departs.js``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from . import compter, coordonner, etranger, invalidite, ouvrir
from .commun import derniere_annee, ligne_cotisee

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
#: Une date que la personne demande, plus tardive que la présumée.
MOTIF_DEMANDE = "demande"
#: La pension de vieillesse qui remplace la pension d'invalidité
#: (:func:`~.invalidite.substitution`).
MOTIF_INVALIDITE = "invalidite"
#: La pension du fonctionnaire radié des cadres pour invalidité, à la radiation
#: (fiche ``retraite_pour_invalidite_fonction_publique``).
MOTIF_RADIATION = "radiation"

#: Ce qu'une demande devient quand elle ne date pas sa pension : servie avec
#: la pension que la loi lui attache — le régime liquidé avec elle, ou le
#: régime de base d'une complémentaire —, ou sans pension de ce régime.
ENSEMBLE = "ensemble"
SANS_PENSION = "sans_pension"


@dataclass(frozen=True)
class Depart:
    """Un départ : le mois où il prend effet, et les régimes qui y liquident."""

    date: DateMois
    #: Les régimes qui liquident ce mois-là ; vide pour le départ unique, où
    #: tous liquident ensemble.
    regimes: frozenset[str] = field(default_factory=frozenset)
    #: ``depart``, au départ déclaré ; ``ouverture``, un régime qui n'ouvrait
    #: pas encore ; ``sortie``, la pension militaire, demandée à la sortie de
    #: l'armée ; ``demande``, la date que la personne demande ;
    #: ``invalidite``, la pension de vieillesse qui remplace la pension
    #: d'invalidité ; ``radiation``, la pension du fonctionnaire radié des
    #: cadres pour invalidité.
    motif: str = MOTIF_DEPART

    @property
    def date_effet(self) -> str:
        """La date d'effet (AAAA-MM-JJ) : le premier jour du mois."""
        return f"{self.date.annee:04d}-{self.date.mois:02d}-01"

    @property
    def unique(self) -> bool:
        """Le départ unique, où tous les régimes liquident ensemble."""
        return not self.regimes


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
    #: ``invalidite`` ou ``radiation`` : la date présumée, que la demande
    #: n'avance pas ;
    #: ``ensemble`` : celle de la pension que la loi lui attache ;
    #: ``sans_pension`` : la carrière n'a pas de pension dans ce régime.
    motif: str

    def donnees(self) -> dict:
        return {"regime": self.regime, "demandee": Depart(self.demandee).date_effet,
                "retenue": None if self.retenue is None else Depart(self.retenue).date_effet,
                "motif": self.motif}


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
    départ de plus pour une pension nulle. Une période qui ne valide rien —
    celle « sans activité » qui suit une radiation — n'en ouvre pas."""
    for ligne, regimes in routage:
        if code not in regimes:
            continue
        if not ligne.cotise:
            if ligne.trimestres_valides > 0:
                return True
            continue
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
    carrière longue, ou du départ des assurés handicapés, quand la durée
    COTISÉE au départ déclaré l'ouvre plus tôt. Après ce départ, l'assuré ne
    cotise plus : ni l'une ni l'autre ne se projette, elles se lisent acquises
    (:meth:`CarriereLongue.age_de_depart`, :func:`~.invalidite.age_du_handicap`).
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
    for anticipe in (_carriere_longue_acquise(moteur, carriere, opposent),
                     _handicap_acquis(moteur, carriere, opposent)):
        if anticipe is not None and anticipe < age:
            age = anticipe
    return carriere.date_de_l_age(age)


def _handicap_acquis(moteur: ScenarioActuel, carriere: Carriere,
                     periodes: list[tuple[str, PeriodeRegime]]) -> float | None:
    """L'âge que le départ anticipé des assurés handicapés ouvre aux régimes de
    ``periodes`` sur la durée accomplie au départ déclaré, ou ``None`` : la
    lecture de :func:`~.ouvrir.ouvrir`, sur la plus longue de leurs durées
    requises."""
    if not periodes or carriere.incapacite_permanente is None:
        return None
    requis = max(ouvrir.duree_requise(moteur, periode, carriere)[0]
                 for _, periode in periodes) or 160
    codes = [code for code, _ in periodes]
    famille = etranger.famille_des_regimes(moteur, codes)
    etrangers = etranger.trimestres_etrangers(moteur, carriere)
    return invalidite.age_du_handicap(
        moteur, carriere, requis, codes,
        (etrangers.cotises[famille], etrangers.pour_le_taux[famille]))


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
        if ligne_cotisee(moteur, carriere, ligne) and ligne.annee <= annee_liquidation)
    famille = etranger.famille_des_regimes(moteur, [code for code, _ in periodes])
    etrangers = etranger.trimestres_etrangers(moteur, carriere)
    majoration = compter.majoration_pour_enfants(
        moteur, carriere, {code: cotises for code, _ in periodes}, annee_liquidation)
    cotises = moteur.carriere_longue.cotises_reputes(
        carriere, cotises + etrangers.trimestres_cotises(famille),
        majoration.trimestres if majoration is not None else 0)
    anticipe = moteur.carriere_longue.age_de_depart(
        carriere, annee_liquidation, cotises, requis, etrangers.cotises[famille])
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


def regimes_de_la_carriere(moteur: ScenarioActuel, carriere: Carriere
                           ) -> tuple[list[str], dict[str, frozenset[str]]]:
    """Les régimes de base et intégrés où ``carriere`` acquiert un droit
    jusqu'à sa liquidation, dans l'ordre de leurs codes, et, pour chaque
    complémentaire, ceux de ces régimes avec lesquels ses années sont
    routées : ce qu'une retraite progressive liquide à sa date
    (:mod:`.progressive`)."""
    carriere = coordonner.retablir(moteur, carriere)
    routage = _routage(moteur, carriere)
    codes = sorted(code for code in {code for _, regimes in routage for code in regimes}
                   if _periode(moteur, code, carriere.annee_liquidation) is not None
                   and _acquiert(moteur, code, routage))
    bases = [code for code in codes
             if moteur.catalogue[code].etage in ETAGES_DES_UNITES]
    suivies: dict[str, set[str]] = {}
    for _, regimes in routage:
        routees = {code for code in regimes if code in bases}
        for code in regimes:
            if code in codes and code not in bases:
                suivies.setdefault(code, set()).update(routees)
    return bases, {code: frozenset(avec) for code, avec in suivies.items()}


def regimes_actifs(moteur: ScenarioActuel, carriere: Carriere) -> frozenset[str]:
    """Les régimes de base et intégrés où ``carriere`` exerce une activité
    l'année de sa liquidation : ceux du temps partiel qu'une retraite
    progressive garde (:mod:`.progressive`). Aucun quand elle ne travaille pas
    cette année-là."""
    carriere = coordonner.retablir(moteur, carriere)
    return frozenset(
        code for ligne, regimes in _routage(moteur, carriere)
        if ligne.annee == carriere.annee_liquidation
        and ligne.type_periode == "emploi" and ligne.revenu > 0
        for code in regimes if moteur.catalogue[code].etage in ETAGES_DES_UNITES)


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
    return departs_et_demandes(moteur, carriere)[0]


def demandes(moteur: ScenarioActuel, carriere: Carriere) -> tuple[DemandeExaminee, ...]:
    """Les pensions dont ``carriere`` dit la date de demande, examinées."""
    return departs_et_demandes(moteur, carriere)[1]


def departs_et_demandes(moteur: ScenarioActuel, carriere: Carriere
                        ) -> tuple[tuple[Depart, ...], tuple[DemandeExaminee, ...]]:
    """Les départs de ``carriere`` (:func:`departs`), et ce que devient chaque
    date de demande qu'elle dit (:class:`DemandeExaminee`), en un calcul."""
    if carriere.age_liquidation is None:
        return (), ()
    declare = carriere.date_liquidation
    unique = (Depart(declare),)
    demandees = carriere.demandes_de_pension
    carriere = coordonner.retablir(moteur, carriere)
    routage = _routage(moteur, carriere)
    codes = sorted(code for code in {code for _, regimes in routage for code in regimes}
                   if _periode(moteur, code, carriere.annee_liquidation) is not None
                   and _acquiert(moteur, code, routage))
    bases = [code for code in codes
             if moteur.catalogue[code].etage in ETAGES_DES_UNITES]
    if not bases:
        return unique, _examiner(demandees, {}, set(), None)
    unites = _unites(moteur, carriere, bases, routage)
    unite_de = {code: i for i, unite in enumerate(unites) for code in unite}

    # Chaque complémentaire suit les unités dont elle partage les années.
    suivies: dict[str, set[int]] = {}
    for _, regimes in routage:
        indices = {unite_de[code] for code in regimes if code in unite_de}
        for code in regimes:
            if code in codes and code not in unite_de:
                suivies.setdefault(code, set()).update(indices)

    # La date présumée de chaque unité, et ce qui la date ; puis la demande,
    # quand elle vient après : la plus tardive des régimes de l'unité.
    ouvertures = [_ouverture(moteur, carriere, unite) for unite in unites]
    # La pension de vieillesse de l'ex-invalide, quand elle commence au plus
    # tard au départ déclaré : d'office, elle ne s'avance ni ne se reporte ;
    # l'invalide qui travaille la demande, et sa demande la date.
    substituee = invalidite.substitution(moteur, carriere)
    if substituee is not None and substituee.date > declare:
        substituee = None
    substitues = moteur.invalidites.regimes("substitution")
    dates: list[tuple[DateMois, str]] = []
    for i, unite in enumerate(unites):
        # Le fonctionnaire radié des cadres pour invalidité liquide sa pension
        # à la radiation, à tout âge : « la jouissance de la pension civile est
        # immédiate » (L. 24, I, 2°).
        radiation = next((carriere.radiation_pour_invalidite for code in sorted(unite)
                          if invalidite.radiation_du_regime(moteur, code, carriere)
                          is not None), None)
        if radiation is not None:
            dates.append((radiation.date, MOTIF_RADIATION))
            continue
        if substituee is not None and not unite.isdisjoint(substitues):
            presumee = (substituee.date, MOTIF_INVALIDITE)
            voulue = max((demandees[code] for code in unite if code in demandees),
                         default=None)
            dates.append((voulue, MOTIF_DEMANDE)
                         if (substituee.maintien == invalidite.ACTIVITE
                             and voulue is not None and voulue > presumee[0])
                         else presumee)
            continue
        if ouvertures[i] > declare:
            presumee = (ouvertures[i], MOTIF_OUVERTURE)
        else:
            plus_tot = max(ouvertures[i], _sortie(carriere, unite, routage))
            presumee = ((plus_tot, MOTIF_SORTIE)
                        if plus_tot < declare and _pension_militaire(moteur, carriere, unite)
                        else (declare, MOTIF_DEPART))
        voulue = max((demandees[code] for code in unite if code in demandees), default=None)
        dates.append((voulue, MOTIF_DEMANDE) if voulue is not None and voulue > presumee[0]
                     else presumee)
    if (all(ouverture > declare for ouverture in ouvertures)
            and all(motif != MOTIF_DEMANDE for _, motif in dates)):
        return unique, ()

    par_regime: dict[str, tuple[DateMois, str]] = {
        code: dates[i] for code, i in unite_de.items()}
    for code, indices in suivies.items():
        par_regime[code] = max((dates[i] for i in sorted(indices)), key=lambda d: d[0],
                               default=(declare, MOTIF_DEPART))
    legal = None
    if RAFP in par_regime:
        legal = carriere.date_de_l_age(age_legal(moteur, carriere))
        if legal > par_regime[RAFP][0]:
            par_regime[RAFP] = (legal, MOTIF_OUVERTURE)
    for code, (quand, _) in list(par_regime.items()):
        if code not in unite_de and code in demandees and demandees[code] > quand:
            par_regime[code] = (demandees[code], MOTIF_DEMANDE)

    examens = _examiner(demandees, par_regime, set(unite_de), legal)
    par_date: dict[DateMois, set[str]] = {}
    for code, (quand, _) in par_regime.items():
        par_date.setdefault(quand, set()).add(code)
    if set(par_date) == {declare}:
        return unique, examens

    def motif(quand: DateMois) -> str:
        """Ce qui date un départ : l'acte de la personne d'abord, puis la
        sortie de l'armée, puis la substitution de la pension d'invalidité ;
        l'ouverture d'un régime sinon — le RAFP à l'âge légal compris, qui
        peut précéder le départ déclaré."""
        if quand == declare:
            return MOTIF_DEPART
        motifs = {par_regime[code][1] for code in par_date[quand]}
        for retenu in (MOTIF_DEMANDE, MOTIF_SORTIE, MOTIF_RADIATION, MOTIF_INVALIDITE):
            if retenu in motifs:
                return retenu
        return MOTIF_OUVERTURE

    return tuple(Depart(quand, frozenset(par_date[quand]), motif(quand))
                 for quand in sorted(par_date)), examens


def _examiner(demandees: dict[str, DateMois], par_regime: dict[str, tuple[DateMois, str]],
              unites: set[str], legal: DateMois | None) -> tuple[DemandeExaminee, ...]:
    """Ce que devient chaque date demandée : celle de sa pension, ou la date
    retenue et sa raison (:class:`DemandeExaminee`)."""
    examens = []
    for code in sorted(demandees):
        demandee = demandees[code]
        if code not in par_regime:
            examens.append(DemandeExaminee(code, demandee, None, SANS_PENSION))
            continue
        retenue, motif = par_regime[code]
        if retenue == demandee:
            motif = MOTIF_DEMANDE
        elif code == RAFP and retenue == legal:
            motif = MOTIF_OUVERTURE
        elif motif == MOTIF_DEMANDE or code not in unites:
            motif = ENSEMBLE
        examens.append(DemandeExaminee(code, demandee, retenue, motif))
    return tuple(examens)


@dataclass(frozen=True)
class PensionServie:
    """Une pension déjà liquidée, que les départs suivants voient servie : ce
    qu'elle vaut au mois de leur date d'effet, son régime, et sa propre date
    d'effet (AAAA-MM-JJ), que le versement forfaitaire unique lit : il ne
    reste, depuis 2016, qu'à qui a pris sa première retraite avant."""

    regime: str
    montant: float
    date_effet: str | None = None


def liquider_les_departs(moteur: ScenarioActuel, carriere: Carriere,
                         contexte: Contexte, nature: str = "definitive",
                         liste: tuple[Depart, ...] | None = None,
                         journal: object | None = None,
                         progressive: tuple | None = None) -> list[Liquidation]:
    """Chaque départ liquidé, dans l'ordre des dates : sur la carrière arrêtée
    à sa date, pour ses seuls régimes, en voyant servies les pensions des
    départs qui le précèdent, menées jusqu'à lui (R. 173-7 : le minimum
    contributif s'écrête sur les pensions du mois de sa date d'effet).
    ``progressive`` est la retraite progressive ouverte et sa liquidation
    provisoire (:mod:`.progressive`) : chaque départ en garde le plancher."""
    from . import liquidation as _liquidation
    from . import progressive as _progressive
    from ..revalorisation import mener_au_mois

    liste = departs(moteur, carriere) if liste is None else liste
    liquidations: list[Liquidation] = []
    for depart in liste:
        demande = _liquidation.Demande(
            personne=carriere.personne, date_effet=depart.date_effet,
            date_evenement=depart.date_effet, nature=nature,
            regimes=() if depart.unique else tuple(sorted(depart.regimes)))
        servies = tuple(
            PensionServie(pension.regime, montant, anterieure.demande.date_effet)
            for anterieure in liquidations
            for pension, montant in zip(anterieure.regimes, mener_au_mois(
                moteur, anterieure.regimes, anterieure.carriere.date_liquidation,
                depart.date)))
        initiales, recalcul = (), True
        if progressive is not None:
            ouverte, provisoire = progressive
            initiales = _progressive.initiales(
                moteur, ouverte, provisoire, depart.date,
                None if depart.unique else depart.regimes)
            recalcul = _progressive.recalculee(depart.date)
        etat = _liquidation.Etat(carriere.liquidee_au(depart.date), journal, servies,
                                 initiales, recalcul)
        liquidations.append(_liquidation.liquider(demande, etat, contexte))
    return liquidations
