"""Compter les durées (docs/architecture.md, § 7.2).

Les trimestres de chaque compte, régime par régime et année par année :

* l'ASSURANCE, périodes assimilées comprises, qui commande le taux plein et
  proratise la pension du régime ;
* les SERVICES, qui proratisent celle de la fonction publique (L. 13 du code
  des pensions), dans les limites que L. 9 pose à ce qui n'est pas un service
  effectif ;
* les trimestres COTISÉS, qui ouvrent la carrière longue et majorent le
  minimum contributif.

Et les trimestres dus au titre des enfants, que le droit accorde DANS un
régime, celui que la priorité entre régimes désigne (R. 173-15) :
:func:`majoration_pour_enfants`.

Ce que l'étape écrit, :class:`Durees`, suit son schéma,
``data/reference/etapes/compter_les_durees.yaml``. Son jumeau est
``moteur/js/droit/compter.js``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from .. import chronologie as chrono
from ..calendrier import DateMois
from ..donnees.chargement import Fiabilite
from . import coordonner
from .commun import derniere_annee
from .etranger import TrimestresEtrangers, compter_les_periodes, famille_des_regimes

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..donnees.regimes import PeriodeRegime
    from ..scenarios.actuel import ScenarioActuel
    from .coordonner import Coordination

#: La version du schéma de l'étape : la deuxième compte les trimestres des
#: enfants enfant par enfant, chacun dans son régime ; la troisième, les
#: trimestres que les périodes hors de France apportent.
SCHEMA_VERSION = 3

#: Les trois comptes, dans l'ordre où l'étape les écrit.
COMPTES = ("assurance", "services", "cotises")

#: Le seul dispositif pour enfants qu'un régime EN POINTS puisse porter : une
#: majoration de durée d'assurance ne touche que la durée, qu'il oppose aussi ;
#: une bonification entre aux services, qu'il n'a pas.
_MAJORATION_DE_DUREE = "mda"

#: Le régime à qui R. 173-15 donne la priorité parmi les régimes alignés.
_REGIME_GENERAL = "regime_general"

#: Les conditions qu'une version de la bonification ou de la majoration de
#: la fonction publique pose à l'enfant (``contenu.parametres.condition`` de
#: la fiche ``enfants_fonction_publique``). Jusqu'en 2003, R. 13 vaut pour
#: chacun des enfants (LEGIARTI000006362901) ; de 2004 à 2010, il suppose une
#: interruption d'activité dans un congé du statut — l'enfant est donc né en
#: service (LEGIARTI000006362902) ; depuis 2011, le congé de maternité du code
#: de la sécurité sociale suffit (LEGIARTI000023449727), mais l'enfant doit
#: être né avant la radiation des cadres (juris-cnracl, « Bonification pour
#: enfants »). Pour les enfants nés depuis 2004, la majoration de L. 12 bis ne
#: va qu'aux femmes « ayant accouché postérieurement à leur recrutement » —
#: condition que les régimes spéciaux reprennent mot pour mot (décrets
#: n° 2003-1306, article 21 ; n° 2008-639, article 13 ; n° 2008-637,
#: article 24…).
CONDITIONS = ("tout_enfant", "ne_en_service", "ne_avant_radiation",
              "accouchement_apres_recrutement")


@dataclass(frozen=True)
class TrimestresEnfant:
    """Ce qu'un enfant ouvre, et le régime qui le porte."""

    #: L'enfant, tel que la chronologie le nomme.
    enfant: str
    #: Sa naissance (AAAA-MM-JJ), déclarée ou présumée.
    naissance: str
    #: Code du régime dans lequel le droit attribue ses trimestres.
    regime: str
    #: Dispositif qui les accorde : ``mda`` ou ``bonifications``.
    dispositif: str
    #: La fiche et la version appliquées, et le texte qui fait naître celle-ci.
    fiche: str
    version: str
    texte: str | None
    #: Trimestres accordés pour cet enfant. Ils jouent sur la durée
    #: d'assurance tous régimes, donc sur la décote et la surcote.
    trimestres: int
    #: Ceux d'entre eux qui entrent dans les SERVICES du régime, et relèvent
    #: donc son prorata. Une bonification en est ; la majoration de durée
    #: d'assurance de L. 12 bis n'en est pas.
    services: int
    fiabilite: Fiabilite


@dataclass(frozen=True)
class MajorationEnfants:
    """Trimestres dus au titre des enfants, enfant par enfant.

    Chaque enfant a son régime : la priorité entre régimes (R. 173-15) se lit
    pour chacun, et le régime général accorde ceux qu'un régime spécial
    n'ouvre pas — « si un ou plusieurs enfants n'ouvrent pas droit à
    majoration » (circulaire Cnav 2017-01, fiches n° 6.2a et 6.2b, point 3).
    """

    #: Les enfants qui ouvrent un droit, dans l'ordre de leurs filiations.
    enfants: tuple[TrimestresEnfant, ...]

    @property
    def trimestres(self) -> int:
        """Trimestres accordés au total, tous enfants confondus."""
        return sum(enfant.trimestres for enfant in self.enfants)

    @property
    def services(self) -> int:
        """Ceux d'entre eux qui entrent aux services, tous enfants confondus."""
        return sum(enfant.services for enfant in self.enfants)

    @property
    def fiabilite(self) -> Fiabilite:
        """La fiabilité la plus basse des enfants."""
        return min(enfant.fiabilite for enfant in self.enfants)

    def par_regime(self) -> dict[str, tuple[int, int]]:
        """Les trimestres et les services que porte chaque régime, dans l'ordre
        de son premier enfant."""
        sommes: dict[str, tuple[int, int]] = {}
        for enfant in self.enfants:
            trimestres, services = sommes.get(enfant.regime, (0, 0))
            sommes[enfant.regime] = (trimestres + enfant.trimestres,
                                     services + enfant.services)
        return sommes

    @property
    def regimes(self) -> list[str]:
        """Les régimes qui portent des trimestres d'enfants."""
        return list(self.par_regime())

    @property
    def dispositifs(self) -> list[str]:
        """Les dispositifs qui les accordent, dans l'ordre des enfants."""
        return list(dict.fromkeys(enfant.dispositif for enfant in self.enfants))


@dataclass(frozen=True, eq=False)
class Durees:
    """Ce que l'étape écrit. Son schéma :
    ``data/reference/etapes/compter_les_durees.yaml``.

    Deux activités d'une même année s'additionnent dans ``par_annee`` ; le
    plafond de l'année, ses trimestres civils, s'applique quand on les lit
    (:meth:`cumul_plafonne`), régime par régime ou groupe par groupe.
    """

    #: La carrière dont les durées sont comptées, rétablissement fait.
    carriere: Carriere
    #: Par compte, par régime et par année, les trimestres crédités.
    par_annee: dict[str, dict[str, dict[int, int]]]
    #: Ce qui ne tient à aucune année — les trimestres des enfants —, et
    #: s'ajoute donc hors plafond annuel : par compte et par régime.
    hors_annee: dict[str, dict[str, int]]
    #: Les trimestres dus au titre des enfants, et le régime qui les porte.
    enfants: MajorationEnfants | None
    #: La durée d'assurance tous régimes, enfants compris.
    trimestres: int
    #: La durée d'assurance de chaque régime, plafonnée année par année,
    #: enfants compris dans celui qui les porte.
    trimestres_par_regime: dict[str, int]
    #: Les BONIFICATIONS, à part des services : seules elles peuvent porter le
    #: taux au-delà du maximum (`taux_maximum_bonifie`).
    bonifications_par_regime: dict[str, int]
    #: Les trimestres que les périodes hors de France apportent, par famille
    #: de régimes : hors de :attr:`trimestres` et de la durée de chaque
    #: régime, qui proratise ; :meth:`pour_le_taux` les y ajoute.
    etranger: TrimestresEtrangers | None = None

    def pour_le_taux(self, famille: str | None, nationale: bool = False) -> int:
        """La durée d'assurance tous régimes que le taux d'un régime de cette
        famille lit (:func:`~.etranger.famille_du_regime`) : celle de la
        carrière, enfants compris, et les trimestres étrangers que la famille
        retient — sans ceux qu'un accord compare, pour la pension nationale."""
        if self.etranger is None or famille is None:
            return self.trimestres
        return self.trimestres + self.etranger.trimestres(famille, nationale)

    @property
    def trimestres_etrangers(self) -> int:
        """Les trimestres étrangers que retient la famille des régimes de la
        carrière : ceux que le résultat ajoute à sa durée tous régimes."""
        return 0 if self.etranger is None else self.etranger.trimestres(
            self.etranger.famille)

    def cumul_plafonne(self, table: str, membres: tuple[str, ...]) -> int:
        """Les trimestres d'un compte, pour un régime ou un groupe de régimes
        liquidés ensemble : sommés ANNÉE PAR ANNÉE, sans dépasser les
        trimestres civils de chaque année, plus ce qui ne tient à aucune."""
        sommes: dict[int, int] = {}
        for membre in membres:
            for annee, trimestres in self.par_annee[table].get(membre, {}).items():
                sommes[annee] = sommes.get(annee, 0) + trimestres
        return (sum(min(somme, self.carriere.plafond_trimestres(annee))
                    for annee, somme in sommes.items())
                + sum(self.hors_annee[table].get(membre, 0) for membre in membres))

    def donnees(self) -> dict:
        """Les durées, telles que leur schéma les décrit."""
        enfants = self.enfants
        return {
            "schema_version": SCHEMA_VERSION,
            "personne": self.carriere.personne,
            "comptes": [
                {"compte": compte, "regime": regime, "annee": annee,
                 "trimestres": trimestres}
                for compte in COMPTES
                for regime, annees in self.par_annee[compte].items()
                for annee, trimestres in annees.items()],
            "enfants": None if enfants is None else {
                "trimestres": enfants.trimestres, "services": enfants.services,
                "fiabilite": enfants.fiabilite.name.lower(),
                "par_enfant": [
                    {"enfant": e.enfant, "naissance": e.naissance, "regime": e.regime,
                     "dispositif": e.dispositif, "fiche": e.fiche, "version": e.version,
                     "trimestres": e.trimestres, "services": e.services,
                     "fiabilite": e.fiabilite.name.lower()}
                    for e in enfants.enfants]},
            "trimestres": self.trimestres,
            "etranger": None if self.etranger is None else self.etranger.donnees(),
        }


def compter(moteur: ScenarioActuel, coordination: Coordination,
            avantages_non_contributifs: bool = True) -> Durees:
    """L'étape : les trimestres de chaque compte, puis ceux des enfants.

    ``avantages_non_contributifs`` à faux retire les trimestres des enfants :
    la valorisation des droits acquis du scénario prospectif ne mesure que
    du contributif pur (voir :meth:`ScenarioActuel.calculer`).
    """
    carriere = coordination.carriere
    annee_liquidation = carriere.annee_liquidation
    trimestres = carriere.trimestres_actuels
    # Ce qui reste du budget de services que L. 9 ouvre dans une limite —
    # trois ans par enfant pour le congé parental. Il se tient sur toute la
    # carrière, et non année par année : deux congés de deux ans pour un
    # seul enfant n'ouvrent que trois ans de services.
    budget_services_plafonnes: dict[int, int] = {}
    # Les trois comptes, ANNÉE PAR ANNÉE. Deux activités cumulées peuvent
    # verser au même régime, ou à deux régimes liquidés ensemble : leurs
    # trimestres s'y additionnent sans dépasser les trimestres civils de
    # l'année. Une année d'une seule activité n'est pas touchée.
    par_annee: dict[str, dict[str, dict[int, int]]] = {
        "assurance": {}, "services": {}, "cotises": {},
    }

    def crediter_trimestres(table: str, code: str, annee: int,
                            trimestres: int) -> None:
        annees = par_annee[table].setdefault(code, {})
        annees[annee] = annees.get(annee, 0) + trimestres

    # Ce qui ne tient à aucune année — la majoration pour enfants — et
    # s'ajoute donc hors plafond annuel.
    hors_annee: dict[str, dict[str, int]] = {
        "assurance": {}, "services": {}, "cotises": {},
    }
    for ligne, regimes in zip(carriere.lignes, coordination.regimes):
        retenus_ligne = carriere.trimestres_retenus(ligne)
        if retenus_ligne <= 0:
            continue
        services_ligne = (
            services_a_temps_partiel(retenus_ligne, ligne.quotite)
            if ligne.services_fonction_publique else 0
        )
        plafond = ligne.services_plafond_trimestres_par_enfant
        if services_ligne and plafond:
            restant = budget_services_plafonnes.setdefault(
                plafond, plafond * carriere.nombre_enfants
            )
            services_ligne = min(services_ligne, restant)
            budget_services_plafonnes[plafond] = restant - services_ligne
        for code in regimes:
            if code not in moteur.catalogue:
                continue
            crediter_trimestres("assurance", code, ligne.annee, retenus_ligne)
            if services_ligne:
                crediter_trimestres("services", code, ligne.annee, services_ligne)
            if ligne.cotise:
                crediter_trimestres("cotises", code, ligne.annee, retenus_ligne)
    durees = Durees(carriere, par_annee, hors_annee, None, trimestres, {}, {})
    # Durée d'assurance validée dans chaque régime, PÉRIODES ASSIMILÉES
    # COMPRISES : le coefficient de proratisation du régime général porte
    # sur la durée d'assurance, pas sur les seules années cotisées. Une
    # année de chômage indemnisé ne verse rien au compte mais compte bien
    # dans le rapport durée acquise / durée requise.
    trimestres_par_regime = {code: durees.cumul_plafonne("assurance", (code,))
                             for code in par_annee["assurance"]}

    # Les trimestres accordés au titre des enfants ne flottent pas au-dessus
    # des régimes : le droit les attribue DANS un régime, et ils comptent
    # donc aussi dans sa proratisation, pas seulement dans la décote tous
    # régimes confondus. Les ignorer là amputait la pension d'une mère de
    # famille de la part que la majoration est censée lui rendre. Pour
    # chaque enfant, UN SEUL régime les accorde, celui que désigne
    # R. 173-15 : le régime spécial qui peut pensionner et où l'enfant ouvre
    # le droit, sinon le régime général — voir :func:`majoration_pour_enfants`.
    majoration_enfants = (
        majoration_pour_enfants(
            moteur, carriere, trimestres_par_regime, annee_liquidation
        ) if avantages_non_contributifs else None
    )
    bonifications_par_regime: dict[str, int] = {}
    if majoration_enfants is not None:
        # LA DURÉE ET LES SERVICES NE SONT PAS LA MÊME CASE, et la
        # majoration se range dans les deux : tout ce qui est accordé joue
        # sur la durée d'assurance — tous régimes, donc la décote, et celle
        # du régime, donc sa proratisation — quand la seule part `services`
        # entre aux services, qui proratisent la pension de la fonction
        # publique. Ce module les confondait, et sur-créditait les mères
        # fonctionnaires de deux trimestres de services par enfant né depuis
        # 2004, là où L. 12 bis n'accorde qu'une majoration de durée.
        trimestres += majoration_enfants.trimestres
        for regime, (accordes, services) in majoration_enfants.par_regime().items():
            bonifications_par_regime[regime] = services
            trimestres_par_regime[regime] += accordes
            hors_annee["assurance"][regime] = accordes
            hors_annee["services"][regime] = services
    # Les périodes hors de France comptent pour le taux, chacune au titre que
    # la coordination lui a donné, sans dépasser quatre trimestres par année
    # avec ceux de la carrière : jamais dans la durée d'un régime.
    etranger = (compter_les_periodes(carriere, coordination.etranger,
                                     carriere.trimestres_actuels,
                                     famille_des_regimes(moteur, par_annee["assurance"]))
                if coordination.etranger else None)
    return Durees(carriere, par_annee, hors_annee, majoration_enfants, trimestres,
                  trimestres_par_regime, bonifications_par_regime, etranger)


def services_a_temps_partiel(trimestres: int, quotite: float) -> int:
    """Les trimestres de services d'une année travaillée à ``quotite`` : sa
    durée réelle, quand la durée d'assurance la compte entière (L. 11 et L. 14
    du code des pensions ; D. 37-3 pour la retraite progressive). Arrondie
    au trimestre, un demi-trimestre et plus comptant pour un — les
    quarante-cinq jours de L. 13 —, année par année."""
    if quotite >= 1.0:
        return trimestres
    return int(trimestres * quotite + 0.5)


def majoration_pour_enfants(moteur: ScenarioActuel, carriere: Carriere,
                            trimestres_par_regime: dict[str, int],
                            annee_liquidation: int
                            ) -> MajorationEnfants | None:
    """Trimestres dus au titre des enfants, enfant par enfant, et régime qui
    porte ceux de chacun.

    Le droit n'attribue pas ces trimestres au-dessus des régimes : il les
    donne DANS un régime. Ce qu'ils y font dépend de leur nature — une
    bonification entre aux services et relève donc la proratisation, une
    majoration de durée d'assurance ne joue que sur la décote tous régimes
    confondus. C'est le champ `services` du résultat qui les sépare, et
    c'est lui, non `trimestres`, que l'appelant ajoute au compte du régime.

    **Chaque enfant compte à sa date.** La version de la fiche qui
    s'applique se lit sur la naissance de l'enfant et sur la date d'effet de
    la pension (:class:`~retraite_notionnelle.scenarios.actuel.MajorationsPourEnfants`),
    et la condition qu'elle lui pose — né en service, né avant la radiation,
    né après le recrutement — sur sa naissance (:func:`bonification_ouverte`).
    Un enfant né à la date d'effet ou après n'ouvre rien : le vocabulaire
    des dates tient cette combinaison pour impossible (§ 4.2).

    **Pour chaque enfant, un seul régime les accorde, et l'article
    R. 173-15 du code de la sécurité sociale dit lequel.** Le modèle
    retenait celui qui accordait le plus. Le droit suit un ordre, et ne
    laisse pas le choix à l'assurée :

    1. un RÉGIME SPÉCIAL — une fiche qui déclare ``bonifications`` — passe
       le premier « si celui-ci est susceptible d'accorder en vertu de ses
       propres règles une pension à l'intéressé », c'est-à-dire si
       l'assurée y a servi la durée qu'il exige
       (:class:`ServicesOuvrantPension`) et si l'enfant y ouvre le droit
       (:func:`bonification_ouverte`). Il passe même quand il accorde moins :
       la CNRACL le rappelle, jugement à l'appui (TA Amiens, 2 juin 2017,
       n° 1501559), l'agent ne peut pas renoncer à sa bonification pour les
       huit trimestres du régime général. Entre deux régimes spéciaux, le
       dernier servi ;
    2. sinon le RÉGIME GÉNÉRAL, prioritaire parmi les régimes alignés : il
       est compétent pour l'enfant qui n'ouvre pas droit à majoration dans
       le régime spécial (circulaire Cnav 2017-01, fiches n° 6.2a et 6.2b,
       point 3) ;
    3. sans lui, le régime de la dernière affiliation et, entre deux
       affiliations simultanées, celui qui compte le plus de trimestres :
       c'est ainsi que le modèle approche « le régime susceptible
       d'attribuer la pension la plus élevée ».

    Un régime spécial qui ne peut pas servir de pension rétablit l'agent au
    régime général. Sans régime aligné pour recevoir la majoration, c'est
    donc ce régime spécial qui la porte, faute de mieux.

    **Un régime en points porte aussi la majoration de DURÉE.** Elle ne
    joue que sur la durée d'assurance — la décote et la surcote —, et un
    régime en points qui en oppose une s'en sert comme un régime en
    annuités : c'est la CNAVPL, à qui L. 643-1-1 rend L. 351-4 depuis le
    1er avril 2010. Le moteur ne la cherchait que dans les annuités, et une
    libérale qui n'avait cotisé qu'à sa section n'en recevait aucun
    trimestre. Une BONIFICATION, elle, entre aux services, que seul un
    régime en annuités proratise : les mines, en points, en déclarent une,
    et elle reste hors de ce décompte.

    Renvoie ``None`` quand aucun enfant n'ouvre rien : pas d'enfant, aucun
    régime porteur, dispositif pas encore né, droit fermé, ou assuré qui
    n'en est pas le bénéficiaire.
    """
    # La date d'effet de la pension, au mois de la liquidation : l'année est
    # celle que l'appelant demande, comme pour le droit à pension.
    mois = carriere.date_liquidation.mois if carriere.age_liquidation is not None else 1
    date_effet = f"{annee_liquidation:04d}-{mois:02d}-01"
    nes = [(enfant, naissance) for enfant, naissance in carriere.naissances_des_enfants
           if naissance < date_effet]
    if not nes:
        return None
    # Les régimes qui peuvent porter les trimestres, et le dispositif de
    # chacun, lus une fois pour tous les enfants.
    candidats: list[tuple[str, int, str, PeriodeRegime]] = []
    for code, valides in trimestres_par_regime.items():
        if code not in moteur.catalogue:
            continue
        regime = moteur.catalogue[code]
        periode = regime.periode(min(annee_liquidation, derniere_annee(regime)))
        if periode is None:
            continue
        for dispositif in periode.avantages_non_contributifs:
            if dispositif not in moteur.majorations_enfants.FICHES:
                continue
            if (periode.type_calcul != "annuites"
                    and dispositif != _MAJORATION_DE_DUREE):
                continue
            candidats.append((code, valides, dispositif, periode))
    # Le droit à pension de chaque régime spécial, et la dernière année de
    # chaque régime : lus une fois, et seulement s'il le faut.
    droits: dict[str, coordonner.DroitPension | None] = {}
    dernieres: dict[str, int] = {}

    def droit_de(periode: PeriodeRegime) -> coordonner.DroitPension | None:
        if periode.regime not in droits:
            droits[periode.regime] = coordonner.droit_a_pension(
                moteur, periode.regime, carriere, annee_liquidation)
        return droits[periode.regime]

    def retenir(parmi: dict[str, tuple[int, TrimestresEnfant]]) -> TrimestresEnfant:
        if len(parmi) > 1 and not dernieres:
            dernieres.update(dernieres_annees(moteur, carriere, annee_liquidation))
        return choisir(parmi, dernieres)

    enfants: list[TrimestresEnfant] = []
    for enfant, naissance in nes:
        # Les régimes spéciaux qui peuvent pensionner, ceux qui ne le
        # peuvent pas, et les régimes alignés : (trimestres validés, ce que
        # l'enfant y ouvre).
        speciaux: dict[str, tuple[int, TrimestresEnfant]] = {}
        sans_pension: dict[str, tuple[int, TrimestresEnfant]] = {}
        alignes: dict[str, tuple[int, TrimestresEnfant]] = {}
        # Ce qu'a coûté d'écarter un régime spécial : la fiabilité de la
        # règle qui l'a écarté, que la majoration servie ailleurs hérite.
        fiabilite_ecartes = Fiabilite.CERTIFIEE
        for code, valides, dispositif, periode in candidats:
            accorde = moteur.majorations_enfants.par_enfant(
                dispositif, carriere.sexe, naissance, date_effet,
                [jour for _, jour in nes])
            if accorde is None:
                continue
            ouvre = TrimestresEnfant(
                enfant=enfant, naissance=naissance, regime=code, dispositif=dispositif,
                fiche=accorde.fiche, version=accorde.version, texte=accorde.texte,
                trimestres=accorde.trimestres, services=accorde.services,
                fiabilite=accorde.fiabilite)
            if dispositif == _MAJORATION_DE_DUREE:
                alignes[code] = (valides, ouvre)
                continue
            droit = droit_de(periode)
            if droit is None:
                continue
            if not bonification_ouverte(accorde.condition, chrono.annee_de(naissance),
                                        droit.recrutement, droit.derniere):
                # Le droit fermé se lit sur la date de naissance de l'enfant,
                # présumée ou déclarée : la version le dit déjà.
                fiabilite_ecartes = min(fiabilite_ecartes, accorde.fiabilite)
                continue
            ouvre = replace(ouvre, fiabilite=min(accorde.fiabilite, droit.fiabilite))
            if droit.pension:
                speciaux[code] = (valides, ouvre)
            else:
                fiabilite_ecartes = min(fiabilite_ecartes, droit.fiabilite)
                sans_pension[code] = (valides, ouvre)
        if speciaux:
            enfants.append(retenir(speciaux))
            continue
        if _REGIME_GENERAL in alignes:
            retenue = alignes[_REGIME_GENERAL][1]
        elif alignes:
            retenue = retenir(alignes)
        elif sans_pension:
            enfants.append(retenir(sans_pension))
            continue
        else:
            continue
        if fiabilite_ecartes < retenue.fiabilite:
            retenue = replace(retenue, fiabilite=fiabilite_ecartes)
        enfants.append(retenue)
    return MajorationEnfants(tuple(enfants)) if enfants else None


def droit_regime_special(moteur: ScenarioActuel, periode: PeriodeRegime,
                         carriere: Carriere, annee_liquidation: int,
                         condition: str, naissance: int
                         ) -> tuple[bool, bool, Fiabilite] | None:
    """Ce que ce régime spécial peut pour un enfant de cette assurée, né
    cette année-là, sous la condition que la version de la fiche lui pose.

    Rend ``(pension, ouvert, fiabilite)`` : peut-il lui servir une pension
    — a-t-elle servi la durée qu'il exige à la date de sa radiation —, le
    droit y est-il ouvert pour cet enfant, et la fiabilité de la durée
    exigée. ``None`` si elle n'y a jamais servi.

    La radiation est datée comme pour la pension différée : au 1er janvier
    qui suit la dernière année de services. Quand elle ne précède pas le
    départ, l'agent part en fonctions, et c'est le départ qui la date. Un
    régime que la table ne porte pas est présumé pouvoir pensionner, au
    niveau ``estimee``.

    Les trois régimes interpénétrés se lisent ensemble : la durée exigée
    porte sur tous les services de L. 5, et le recrutement comme la
    radiation sont ceux de la carrière publique entière
    (:func:`~retraite_notionnelle.droit.coordonner.droit_a_pension`).
    """
    droit = coordonner.droit_a_pension(moteur, periode.regime, carriere,
                                       annee_liquidation)
    if droit is None:
        return None
    return (droit.pension,
            bonification_ouverte(condition, naissance, droit.recrutement, droit.derniere),
            droit.fiabilite)


def bonification_ouverte(condition: str, naissance: int, recrutement: int,
                         derniere: int) -> bool:
    """L'enfant né cette année-là ouvre-t-il le droit dans le régime spécial ?

    La condition est celle que la version de la fiche lui pose
    (:data:`CONDITIONS`), et la naissance se compare, à l'année près, au
    recrutement et à la dernière année de services :

    * ``tout_enfant`` — la bonification de L. 12 b jusqu'en 2003 ;
    * ``ne_en_service`` — de 2004 à 2010, R. 13 n'admet que les congés du
      statut : l'enfant naît entre le recrutement et la radiation ;
    * ``ne_avant_radiation`` — depuis 2011, R. 13 admet le congé de
      maternité du code de la sécurité sociale : l'enfant naît avant la
      radiation ;
    * ``accouchement_apres_recrutement`` — la majoration de L. 12 bis, pour
      un enfant né depuis 2004, ne va qu'à la femme « ayant accouché
      postérieurement à [son] recrutement ».

    Hors la fonction publique, les régimes spéciaux reprennent la dernière
    condition mot pour mot ; le modèle leur prête aussi les autres, comme il
    leur prête la fiche. Une condition que le moteur ne connaît pas l'arrête
    (§ 6.7).
    """
    if condition == "tout_enfant":
        return True
    if condition == "ne_en_service":
        return recrutement <= naissance <= derniere
    if condition == "ne_avant_radiation":
        return naissance <= derniere
    if condition == "accouchement_apres_recrutement":
        return naissance >= recrutement
    raise ValueError(f"condition inconnue pour les trimestres d'un enfant : {condition!r}")


def dernieres_annees(moteur: ScenarioActuel, carriere: Carriere,
                     annee_liquidation: int) -> dict[str, int]:
    """La dernière année où chaque régime reçoit une ligne de la carrière,
    jusqu'à la liquidation : l'affiliation « en dernier lieu » de R. 173-15."""
    dernieres: dict[str, int] = {}
    for ligne in carriere.lignes:
        if (ligne.annee > annee_liquidation
                or carriere.trimestres_retenus(ligne) <= 0):
            continue
        for code in coordonner.regimes_de(
                moteur, ligne, ligne.annee,
                carriere.date_entree(ligne.affiliation),
                revenu=ligne.revenu if ligne.cotise else ligne.revenu_reference,
                plafond=moteur.macro.plafond_securite_sociale(ligne.annee)):
            dernieres[code] = max(dernieres.get(code, 0), ligne.annee)
    return dernieres


def choisir(candidats: dict[str, tuple[int, TrimestresEnfant]],
            dernieres: dict[str, int]) -> TrimestresEnfant:
    """Le candidat du régime où l'assurée a été affiliée en dernier lieu.

    À égalité — deux affiliations simultanées —, celui qui compte le plus
    de trimestres, puis le dernier code par ordre alphabétique, pour que le
    résultat ne dépende pas de l'ordre d'un dictionnaire.
    """
    if len(candidats) == 1:
        return next(iter(candidats.values()))[1]
    code = max(candidats,
               key=lambda c: (dernieres.get(c, 0), candidats[c][0], c))
    return candidats[code][1]


def trimestres_de_la_ligne_entre(carriere: Carriere, ligne, debut: DateMois,
                                 fin: DateMois) -> float:
    """Part des trimestres d'UNE ligne acquise entre deux dates, ``fin`` exclue.

    Les trimestres de la ligne sont répartis sur ses mois — les premiers de
    l'année pour celle du départ, les derniers pour celle de l'entrée —, comme
    le fait :func:`~retraite_notionnelle.scenarios.actuel._trimestres_entre_dates`,
    qui en fait la somme.
    """
    retenus = carriere.trimestres_retenus(ligne)
    mois_ligne = round(carriere.part_retenue(ligne.annee) * 12)
    if retenus <= 0 or mois_ligne <= 0:
        return 0.0
    premier = (DateMois(ligne.annee, 1)
               if mois_ligne == 12 or ligne.annee == carriere.annee_liquidation
               else DateMois(ligne.annee, 13 - mois_ligne))
    dernier = premier.plus_mois(mois_ligne)
    recouvrement = (min(fin.rang, dernier.rang) - max(debut.rang, premier.rang))
    return retenus * recouvrement / mois_ligne if recouvrement > 0 else 0.0
