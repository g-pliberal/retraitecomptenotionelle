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

from ..calendrier import DateMois
from ..donnees.chargement import Fiabilite
from . import coordonner
from .commun import derniere_annee

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..donnees.regimes import PeriodeRegime
    from ..scenarios.actuel import ScenarioActuel
    from .coordonner import Coordination

#: La version du schéma de l'étape.
SCHEMA_VERSION = 1

#: Les trois comptes, dans l'ordre où l'étape les écrit.
COMPTES = ("assurance", "services", "cotises")

#: Le seul dispositif pour enfants qu'un régime EN POINTS puisse porter : une
#: majoration de durée d'assurance ne touche que la durée, qu'il oppose aussi ;
#: une bonification entre aux services, qu'il n'a pas.
_MAJORATION_DE_DUREE = "mda"

#: Le régime à qui R. 173-15 donne la priorité parmi les régimes alignés.
_REGIME_GENERAL = "regime_general"

#: Quand le droit à la bonification d'un régime spécial est OUVERT, dans les
#: trois versions de R. 13 du code des pensions. Jusqu'en 2003, elle vaut pour
#: chacun des enfants (LEGIARTI000006362901). De 2004 à 2010, elle suppose une
#: interruption d'activité dans un congé du statut — l'enfant est donc né en
#: service (LEGIARTI000006362902). Depuis 2011, le congé de maternité du code
#: de la sécurité sociale suffit (LEGIARTI000023449727), mais l'enfant doit
#: être né avant la radiation des cadres (juris-cnracl, « Bonification pour
#: enfants »). Les deux bornes se lisent à l'année de liquidation.
_BONIFICATION_NE_EN_SERVICE_DEPUIS = 2004
_BONIFICATION_NE_AVANT_RADIATION_DEPUIS = 2011

#: Pour les enfants nés depuis 2004, la majoration de L. 12 bis ne va qu'aux
#: femmes « ayant accouché postérieurement à leur recrutement » — condition
#: que les régimes spéciaux reprennent mot pour mot (décrets n° 2003-1306,
#: article 21 ; n° 2008-639, article 13 ; n° 2008-637, article 24…).
_MAJORATION_APRES_RECRUTEMENT_DEPUIS = 2004


@dataclass(frozen=True)
class MajorationEnfants:
    """Trimestres dus au titre des enfants, et régime qui les porte."""

    #: Code du régime dans lequel le droit attribue les trimestres.
    regime: str
    #: Dispositif qui les accorde : ``mda`` ou ``bonifications``.
    dispositif: str
    #: Trimestres accordés au total, tous enfants confondus. Ils jouent sur la
    #: durée d'assurance tous régimes, donc sur la décote et la surcote.
    trimestres: int
    #: Ceux d'entre eux qui entrent dans les SERVICES du régime, et relèvent
    #: donc son prorata. Une bonification en est ; une majoration de durée
    #: d'assurance n'en est pas — voir l'en-tête de
    #: `legislation/majoration_duree_assurance.csv`.
    services: int
    fiabilite: Fiabilite


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
                "regime": enfants.regime, "dispositif": enfants.dispositif,
                "trimestres": enfants.trimestres, "services": enfants.services,
                "fiabilite": enfants.fiabilite.name.lower()},
            "trimestres": self.trimestres,
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
            retenus_ligne if ligne.services_fonction_publique else 0
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
    # famille de la part que la majoration est censée lui rendre. UN SEUL
    # régime les accorde, celui que désigne R. 173-15 : le régime spécial
    # qui peut pensionner, sinon le régime général — voir
    # :func:`majoration_pour_enfants`.
    majoration_enfants = (
        majoration_pour_enfants(
            moteur, carriere, trimestres_par_regime, annee_liquidation
        ) if avantages_non_contributifs else None
    )
    bonifications_par_regime: dict[str, int] = {}
    if majoration_enfants is not None:
        bonifications_par_regime[majoration_enfants.regime] = (
            majoration_enfants.services
        )
        # LA DURÉE ET LES SERVICES NE SONT PAS LA MÊME CASE, et la
        # majoration se range dans les deux : tout ce qui est accordé joue
        # sur la durée d'assurance — tous régimes, donc la décote, et celle
        # du régime, donc sa proratisation — quand la seule part `services`
        # entre aux services, qui proratisent la pension de la fonction
        # publique. Ce module les confondait, et sur-créditait les mères
        # fonctionnaires de deux trimestres de services par enfant né depuis
        # 2004, là où L. 12 bis n'accorde qu'une majoration de durée.
        trimestres += majoration_enfants.trimestres
        trimestres_par_regime[majoration_enfants.regime] += (
            majoration_enfants.trimestres
        )
        hors_annee["assurance"][majoration_enfants.regime] = (
            majoration_enfants.trimestres
        )
        hors_annee["services"][majoration_enfants.regime] = (
            majoration_enfants.services
        )
    return Durees(carriere, par_annee, hors_annee, majoration_enfants, trimestres,
                  trimestres_par_regime, bonifications_par_regime)


def majoration_pour_enfants(moteur: ScenarioActuel, carriere: Carriere,
                            trimestres_par_regime: dict[str, int],
                            annee_liquidation: int
                            ) -> MajorationEnfants | None:
    """Trimestres dus au titre des enfants, et régime qui les porte.

    Le droit n'attribue pas ces trimestres au-dessus des régimes : il les
    donne DANS un régime. Ce qu'ils y font dépend de leur nature — une
    bonification entre aux services et relève donc la proratisation, une
    majoration de durée d'assurance ne joue que sur la décote tous régimes
    confondus. C'est le champ `services` du résultat qui les sépare, et
    c'est lui, non `trimestres`, que l'appelant ajoute au compte du régime.

    **Un seul régime les accorde, et l'article R. 173-15 du code de la
    sécurité sociale dit lequel.** Le modèle retenait celui qui accordait
    le plus. Le droit suit un ordre, et ne laisse pas le choix à l'assurée :

    1. un RÉGIME SPÉCIAL — une fiche qui déclare ``bonifications`` — passe
       le premier « si celui-ci est susceptible d'accorder en vertu de ses
       propres règles une pension à l'intéressé », c'est-à-dire si
       l'assurée y a servi la durée qu'il exige
       (:class:`ServicesOuvrantPension`) et si le droit y est ouvert pour
       ses enfants (:func:`bonification_ouverte`). Il passe même quand il
       accorde moins : la CNRACL le rappelle, jugement à l'appui (TA
       Amiens, 2 juin 2017, n° 1501559), l'agent ne peut pas renoncer à sa
       bonification pour les huit trimestres du régime général. Entre deux
       régimes spéciaux, le dernier servi ;
    2. sinon le RÉGIME GÉNÉRAL, prioritaire parmi les régimes alignés ;
    3. sans lui, le régime de la dernière affiliation et, entre deux
       affiliations simultanées, celui qui compte le plus de trimestres :
       c'est ainsi que le modèle approche « le régime susceptible
       d'attribuer la pension la plus élevée ».

    Un régime spécial qui ne peut pas servir de pension rétablit l'agent au
    régime général. Le modèle ne fait pas ce rétablissement et garde les
    services dans le régime spécial : sans régime aligné pour recevoir la
    majoration, c'est donc ce régime spécial qui la porte, faute de mieux.

    **Un régime en points porte aussi la majoration de DURÉE.** Elle ne
    joue que sur la durée d'assurance — la décote et la surcote —, et un
    régime en points qui en oppose une s'en sert comme un régime en
    annuités : c'est la CNAVPL, à qui L. 643-1-1 rend L. 351-4 depuis le
    1er avril 2010. Le moteur ne la cherchait que dans les annuités, et une
    libérale qui n'avait cotisé qu'à sa section n'en recevait aucun
    trimestre. Une BONIFICATION, elle, entre aux services, que seul un
    régime en annuités proratise : les mines, en points, en déclarent une,
    et elle reste hors de ce décompte.

    Renvoie ``None`` quand rien n'est dû : pas d'enfant, aucun régime
    porteur, dispositif pas encore né, droit fermé, ou assuré qui n'en est
    pas le bénéficiaire.
    """
    if carriere.nombre_enfants <= 0:
        return None
    # Les régimes spéciaux qui peuvent pensionner, ceux qui ne le peuvent
    # pas, et les régimes alignés : (trimestres validés, majoration).
    speciaux: dict[str, tuple[int, MajorationEnfants]] = {}
    sans_pension: dict[str, tuple[int, MajorationEnfants]] = {}
    alignes: dict[str, tuple[int, MajorationEnfants]] = {}
    # Ce qu'a coûté d'écarter un régime spécial : la fiabilité de la règle
    # qui l'a écarté, que la majoration servie ailleurs hérite.
    fiabilite_ecartes = Fiabilite.CERTIFIEE
    for code, valides in trimestres_par_regime.items():
        if code not in moteur.catalogue:
            continue
        regime = moteur.catalogue[code]
        periode = regime.periode(min(annee_liquidation, derniere_annee(regime)))
        if periode is None:
            continue
        for dispositif in periode.avantages_non_contributifs:
            if (periode.type_calcul != "annuites"
                    and dispositif != _MAJORATION_DE_DUREE):
                continue
            accorde = moteur.majorations_enfants.par_enfant(
                dispositif, carriere.sexe, carriere.annee_naissance_des_enfants,
                annee_liquidation, carriere.nombre_enfants,
            )
            if accorde is None:
                continue
            trimestres, services, fiabilite = accorde
            majoration = MajorationEnfants(
                regime=code, dispositif=dispositif,
                trimestres=trimestres * carriere.nombre_enfants,
                services=services * carriere.nombre_enfants,
                fiabilite=fiabilite,
            )
            if dispositif == _MAJORATION_DE_DUREE:
                alignes[code] = (valides, majoration)
                continue
            droit = droit_regime_special(moteur, periode, carriere,
                                               annee_liquidation)
            if droit is None:
                continue
            pension, ouvert, fiabilite_regle = droit
            if not ouvert:
                # Le droit fermé se lit sur la date de naissance que le
                # modèle prête aux enfants : la ligne le dit déjà.
                fiabilite_ecartes = min(fiabilite_ecartes, fiabilite)
                continue
            majoration = replace(
                majoration, fiabilite=min(fiabilite, fiabilite_regle))
            if pension:
                speciaux[code] = (valides, majoration)
            else:
                fiabilite_ecartes = min(fiabilite_ecartes, fiabilite_regle)
                sans_pension[code] = (valides, majoration)
    if speciaux:
        return derniere_affiliation(moteur, carriere, speciaux, annee_liquidation)
    if _REGIME_GENERAL in alignes:
        retenue = alignes[_REGIME_GENERAL][1]
    elif alignes:
        retenue = derniere_affiliation(moteur, carriere, alignes, annee_liquidation)
    elif sans_pension:
        return derniere_affiliation(moteur, carriere, sans_pension, annee_liquidation)
    else:
        return None
    if fiabilite_ecartes < retenue.fiabilite:
        retenue = replace(retenue, fiabilite=fiabilite_ecartes)
    return retenue


def droit_regime_special(moteur: ScenarioActuel, periode: PeriodeRegime,
                         carriere: Carriere, annee_liquidation: int
                         ) -> tuple[bool, bool, Fiabilite] | None:
    """Ce que ce régime spécial peut pour les enfants de cette assurée.

    Rend ``(pension, ouvert, fiabilite)`` : peut-il lui servir une pension
    — a-t-elle servi la durée qu'il exige à la date de sa radiation —, le
    droit y est-il ouvert pour ses enfants, et la fiabilité de la durée
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
            bonification_ouverte(carriere, droit.recrutement,
                                 droit.derniere, annee_liquidation),
            droit.fiabilite)


def bonification_ouverte(carriere: Carriere, recrutement: int, derniere: int,
                         annee_liquidation: int) -> bool:
    """Le droit aux trimestres d'enfants d'un régime spécial est-il ouvert ?

    La chronologie date la naissance des enfants — présumée aux trente
    ans de leur mère tant que rien n'est déclaré (présomption
    ``naissance_des_enfants``, :attr:`Carriere.annee_naissance_des_enfants`)
    —, et le modèle lit, sur cette date, la condition que le texte pose à
    chaque génération d'enfants :

    * né depuis 2004, la majoration de L. 12 bis ne va qu'à la femme
      « ayant accouché postérieurement à [son] recrutement » ;
    * né avant 2004, la bonification de L. 12 b vaut pour tout enfant
      jusqu'en 2003, pour l'enfant né en service de 2004 à 2010 — R. 13
      n'admet alors que les congés du statut —, pour l'enfant né avant la
      radiation depuis 2011 — R. 13 admet le congé de maternité du code
      de la sécurité sociale. Les deux bornes se lisent à la liquidation.

    Hors la fonction publique, les régimes spéciaux reprennent la première
    condition mot pour mot ; le modèle leur applique la seconde, comme il
    leur applique déjà la table de la fonction publique.
    """
    naissance = carriere.annee_naissance_des_enfants
    if naissance >= _MAJORATION_APRES_RECRUTEMENT_DEPUIS:
        return naissance >= recrutement
    if annee_liquidation >= _BONIFICATION_NE_AVANT_RADIATION_DEPUIS:
        return naissance <= derniere
    if annee_liquidation >= _BONIFICATION_NE_EN_SERVICE_DEPUIS:
        return recrutement <= naissance <= derniere
    return True


def derniere_affiliation(moteur: ScenarioActuel, carriere: Carriere,
                         candidats: dict[str, tuple[int, MajorationEnfants]],
                         annee_liquidation: int) -> MajorationEnfants:
    """Le candidat du régime où l'assurée a été affiliée en dernier lieu.

    À égalité — deux affiliations simultanées —, celui qui compte le plus
    de trimestres, puis le dernier code par ordre alphabétique, pour que le
    résultat ne dépende pas de l'ordre d'un dictionnaire. La dernière année
    se lit sur les lignes que chaque régime reçoit ; on ne la cherche que
    s'il faut départager.
    """
    if len(candidats) == 1:
        return next(iter(candidats.values()))[1]
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
            if code in candidats:
                dernieres[code] = max(dernieres.get(code, 0), ligne.annee)
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
