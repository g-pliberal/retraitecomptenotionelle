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
:func:`majoration_pour_enfants` ; ceux que l'emploi classé ajoute dans le
régime qui le pensionne, bonification de services ou majoration de durée :
:func:`trimestres_des_emplois`.

Et les trimestres des périodes assimilées que la chronologie porte (action
130, sixième domaine) : le complément de l'apprentissage, jusqu'à la durée
du contrat, et les jours de stage, d'inscription des sportifs de haut niveau
et de congé supplémentaire de naissance, à l'assurance seule :
:func:`trimestres_assimiles`.

Et les services du code des pensions AU JOUR, que le décompte final arrondit
une seule fois (R. 26) et que la décote lit sans arrondi (L. 14, I) :
:func:`jours_de_la_ligne`, :func:`arrondir_les_services`.

Ce que l'étape écrit, :class:`Durees`, suit son schéma,
``data/reference/etapes/compter_les_durees.yaml``. Son jumeau est
``moteur/js/droit/compter.js``.
"""

from __future__ import annotations

import datetime
import math
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

from .. import chronologie as chrono
from ..calendrier import DateMois, trimestres_civils
from ..donnees.chargement import Fiabilite
from . import coordonner
from .commun import ligne_cotisee, periode_de_liquidation
from .etranger import TrimestresEtrangers, compter_les_periodes, famille_des_regimes
from ..somme import somme_ordonnee

if TYPE_CHECKING:
    from collections.abc import Callable

    from ..carriere import Carriere
    from ..donnees.regimes import PeriodeRegime
    from ..scenarios.actuel import ScenarioActuel
    from .coordonner import Coordination

#: La version du schéma de l'étape : la deuxième compte les trimestres des
#: enfants enfant par enfant, chacun dans son régime ; la troisième, les
#: trimestres que les périodes hors de France apportent ; la quatrième, ceux
#: que les emplois classés ajoutent ; la cinquième, les services du code des
#: pensions au jour ; la sixième, ceux des périodes assimilées.
SCHEMA_VERSION = 6

#: La fiche du décompte des services du code des pensions, lue à la date
#: d'effet (:func:`decompte_des_services`) : l'unité et le seuil du décompte
#: final (R. 26 ; décret n° 2003-1306, article 16 ; décret n° 2004-1056,
#: article 13), et la durée d'assurance comptée au jour (L. 14, I).
FICHE_DU_DECOMPTE = "decompte_des_services_fonction_publique"

#: Le mois des pensions, en jours : l'année de trois cent soixante jours,
#: le trimestre de quatre-vingt-dix — « Un trimestre équivaut à 90 jours »
#: (CNRACL, « Trimestres liquidables »).
JOURS_PAR_MOIS = 30
JOURS_PAR_TRIMESTRE = 90
JOURS_PAR_AN = 360

#: Ce que le minimum garanti compte (``contenu.parametres.minimum_garanti`` de
#: la fiche) : les ``services_effectifs``, arrondis au décompte final, sans
#: bonification (L. 17 depuis 2004) ; ou le décompte de la pension,
#: bonifications comprises (``liquidation``, le b de L. 17 d'avant 2004).
MINIMA_DU_DECOMPTE = ("services_effectifs", "liquidation")

#: La tolérance des jours, qu'un produit par une quotité laisse flottants : un
#: millionième de jour, que l'arrondi du décompte n'atteint jamais.
EPSILON_JOURS = 1e-6

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

#: La fiche de la bonification du cinquième des militaires (L. 12, i), que
#: l'inventaire des avantages mesure à part des emplois classés.
FICHE_DES_MILITAIRES = "bonification_cinquieme_militaires"

#: Les fiches des bonifications et des majorations que l'emploi CLASSÉ, ou le
#: service militaire, ouvre dans le régime qui le pensionne, lues par
#: :class:`FichesDatees <retraite_notionnelle.scenarios.actuel.FichesDatees>`
#: à la date d'effet. L'ordre est celui du cumul, que les versions de
#: septembre 2023 bornent à vingt trimestres : celle des militaires après les
#: bonifications des emplois classés (L. 12), la majoration des hospitaliers
#: après toutes (décret n° 2003-1306, article 21, III).
FICHES_DES_EMPLOIS = ("bonification_cinquieme_police_penitentiaire",
                      "bonification_cinquieme_sapeurs_pompiers",
                      FICHE_DES_MILITAIRES,
                      "majoration_duree_hospitaliers_actifs")

#: Ce qu'une version de ces fiches accorde (``contenu.parametres.nature``) : une
#: ``bonification``, aux services liquidés et à la durée tous régimes, ou une
#: ``majoration``, à la seule durée que le régime oppose à sa décote.
NATURES_DES_EMPLOIS = ("bonification", "majoration")

#: Les conditions qu'une version de ces fiches pose à la carrière
#: (``contenu.parametres.condition``), toutes lues sur la table des emplois
#: classés de la génération (``legislation/categorie_active.csv``) :
#:
#: * ``duree_de_l_age_minore`` — la durée de services dans les statuts de la
#:   fiche qui ouvre l'âge anticipé ou minoré, ou la radiation pour invalidité ;
#: * ``categorie_active_en_fonction`` — les conditions de la catégorie active,
#:   durée de services actifs et âge anticipé, réunies à la radiation des
#:   cadres, l'agent étant alors dans l'un des statuts de la fiche ;
#: * ``duree_de_la_categorie_active`` — la durée de services actifs, l'agent
#:   ayant servi dans l'un des statuts de la fiche ;
#: * ``durees_et_age_de_l_emploi`` — les années servies dans les statuts de la
#:   fiche (``annees_dans_l_emploi``) et celles de la fonction publique civile
#:   (``annees_de_services``), l'âge anticipé atteint si ``age_anticipe`` ; la
#:   radiation pour invalidité imputable au service en dispense ;
#: * ``duree_dans_l_emploi`` — les années servies dans les statuts de la fiche
#:   (``annees_dans_l_emploi``), et, si ``en_fonction``, la dernière année des
#:   services qu'elle compte (``services_comptes``) servie dans l'un d'eux : la
#:   bonification du cinquième « à tous les militaires », qui ne va aux
#:   « anciens militaires » que depuis septembre 2023 (L. 12, i).
CONDITIONS_DES_EMPLOIS = ("duree_de_l_age_minore", "categorie_active_en_fonction",
                          "duree_de_la_categorie_active", "durees_et_age_de_l_emploi",
                          "duree_dans_l_emploi")

#: L'âge au-delà duquel une version supprime la bonification
#: (``contenu.parametres.age_de_suppression``), quand elle ne l'écrit pas en
#: années : « l'âge mentionné à l'article L. 161-17-2 du code de la sécurité
#: sociale », l'âge légal de la génération (L. 12, i, de 2011 à 2023).
AGE_LEGAL = "age_legal"

#: La tolérance des années de service, qu'une somme de fractions de mois laisse
#: flottantes : un milliardième d'année.
EPSILON_ANNEES = 1e-9

#: La fiche de l'apprentissage, que l'emploi porte en attribut, et celle de
#: chaque motif de période assimilée (``chronologie.MOTIFS_D_ASSIMILATION``) :
#: le sixième domaine (action 130).
FICHE_DE_L_APPRENTISSAGE = "apprentissage"
FICHES_DES_ASSIMILEES = {
    "stage_de_formation_professionnelle": "stages_formation_professionnelle",
    "stage_d_insertion": "stages_formation_professionnelle",
    "sportif_de_haut_niveau": "sportifs_haut_niveau",
    "conge_supplementaire_de_naissance": "conge_supplementaire_naissance",
}
#: Comment une version compte ses trimestres : la durée du contrat
#: d'apprentissage (D. 373-3), des jours dans l'année civile (R. 351-12, 2°, c
#: et 4°, i et k), ou des périodes continues (R. 351-12, 9°, b).
DECOMPTES_DES_ASSIMILEES = ("duree_du_contrat", "jours_dans_l_annee", "periodes_continues")
#: Les jours d'exécution du contrat en mois civils incomplets qui font un mois
#: (D. 373-3, 2°).
JOURS_PAR_MOIS_DE_CONTRAT = 30


@dataclass(frozen=True)
class TrimestresEnfant:
    """Ce qu'un enfant ouvre, et le régime qui le porte."""

    #: L'enfant, tel que la chronologie le nomme.
    enfant: str
    #: Sa naissance (AAAA-MM-JJ), déclarée ou présumée.
    naissance: str
    #: Code du régime dans lequel le droit attribue ses trimestres.
    regime: str
    #: Dispositif qui les accorde : ``mda``, ``bonifications``, ou celui d'un
    #: régime spécial qui a sa fiche (``enfants_sncf``, ``enfants_ratp``,
    #: ``enfants_ieg``, ``enfants_crpcen``).
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
        return somme_ordonnee(enfant.trimestres for enfant in self.enfants)

    @property
    def services(self) -> int:
        """Ceux d'entre eux qui entrent aux services, tous enfants confondus."""
        return somme_ordonnee(enfant.services for enfant in self.enfants)

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


@dataclass(frozen=True)
class TrimestresEmploi:
    """Ce que l'emploi classé ajoute dans le régime qui le pensionne.

    Une BONIFICATION de services — le cinquième des policiers — entre aux
    services liquidés, mais « dans la limite du taux maximal de 75 % »
    (service des retraites de l'État) : seules celles de L. 12 portent le
    pourcentage au-delà (L. 13), et elle n'en est pas ; celle des militaires,
    au i de L. 12, en est. Elle entre aussi à la
    durée d'assurance, qui « totalise la durée des services et bonifications
    admissibles en liquidation » (L. 14, I), et par elle à la durée tous
    régimes ; mais non à celle qui ouvre la surcote du fonctionnaire : « les
    bonifications de durée de services et majorations de durée d'assurance, à
    l'exclusion de celles accordées au titre des enfants et du handicap […]
    ne sont pas prises en compte » (L. 14, III). Une MAJORATION de durée qui
    ne vaut que « pour l'application des dispositions du I de l'article
    L. 14 » ne joue que sur la décote du régime qui l'accorde.
    """

    #: Le régime qui la sert.
    regime: str
    #: La fiche et la version appliquées, et le texte qui fait naître celle-ci.
    fiche: str
    version: str
    texte: str | None
    #: Trimestres ajoutés aux services liquidés, sous le pourcentage maximum.
    services: int
    #: Trimestres ajoutés à la durée d'assurance tous régimes, hors de celle
    #: qui ouvre la surcote du fonctionnaire.
    duree: int
    #: Trimestres ajoutés à la seule durée que ce régime oppose à sa décote, et
    #: au minimum garanti qui en dépend.
    majoration: int
    #: La bonification porte-t-elle le pourcentage au-delà du maximum, comme
    #: celles de L. 12 (``taux_maximum_bonifie``) ?
    au_dela_du_maximum: bool
    fiabilite: Fiabilite


@dataclass(frozen=True)
class TrimestresAssimiles:
    """Ce qu'une période assimilée apporte dans une année, au régime qui la
    valide : des trimestres d'assurance, qui comptent pour le taux et la
    proratisation, non cotisés (D. 351-1-2 ne les nomme pas) et sans services."""

    #: ``apprentissage``, ou le motif de la période (vocabulaire,
    #: ``motifs_d_assimilation``).
    motif: str
    #: Le régime qui les valide.
    regime: str
    #: L'année civile où ils comptent.
    annee: int
    #: La fiche et la version appliquées, et le texte qui fait naître celle-ci.
    fiche: str
    version: str
    texte: str | None
    #: Les trimestres, avant le plafond de l'année.
    trimestres: int
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
    #: La durée d'assurance tous régimes, enfants et bonifications des emplois
    #: classés compris.
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
    #: Ce que les emplois classés ajoutent, régime par régime : leur durée est
    #: dans :attr:`trimestres` ; leurs services et leurs majorations, la
    #: liquidation du régime qui les sert les y lit
    #: (:meth:`services_des_emplois`, :meth:`majorations_des_emplois`).
    emplois: tuple[TrimestresEmploi, ...] = ()
    #: La version de la fiche du décompte qui vaut à la date d'effet — son
    #: identifiant et ses paramètres —, ``None`` quand elle ne compte pas au
    #: jour (:func:`decompte_des_services`).
    decompte: dict | None = None
    #: Les services de la fonction publique AU JOUR, par compte —
    #: ``assurance``, le temps partiel compté plein, et ``services``, à sa
    #: quotité —, par régime de la famille et par année : des jours de l'année
    #: de trois cent soixante, que les régimes du code des pensions liquident.
    jours: dict[str, dict[str, dict[int, float]]] = field(default_factory=dict)
    #: Ce que les fractions de trimestre de ces services changent à
    #: :attr:`trimestres`, quand la durée d'assurance de leur décote se compte
    #: au jour : la somme, année par année, de la durée au jour — leurs jours,
    #: et les trimestres des autres régimes, quatre au plus (R. 26 bis) —
    #: moins la durée en trimestres entiers.
    ecart_au_jour: float = 0.0
    #: Les trimestres des périodes assimilées, période par période et année
    #: par année, avant le plafond de l'année : ils sont dans ``par_annee``,
    #: au compte ``assurance`` seul (:func:`trimestres_assimiles`).
    assimilees: tuple[TrimestresAssimiles, ...] = ()
    #: Le plafond des années où une période assimilée compte : leurs
    #: trimestres civils jusqu'à la date d'effet, quatre pour une année
    #: pleine, même quand la carrière n'en couvre qu'une partie (R. 351-12).
    plafonds_assimilees: dict[int, int] = field(default_factory=dict)

    def au_jour(self, membres: tuple[str, ...]) -> bool:
        """Ces régimes comptent-ils leurs services au jour, à la date d'effet ?"""
        return (self.decompte is not None
                and any(m in self.decompte["parametres"]["regimes"] for m in membres))

    def duree_au_jour(self, membres: tuple[str, ...]) -> bool:
        """La décote de ces régimes lit-elle une durée d'assurance au jour, sans
        arrondi (L. 14, I ; Conseil d'État, 2 février 2010, n° 311495) ?"""
        return self.au_jour(membres) and bool(self.decompte["parametres"]["duree_au_jour"])

    def jours_de_services(self, membres: tuple[str, ...]) -> float:
        """Les jours de services de ces régimes, sommés année par année, trois
        cent soixante au plus par année."""
        sommes: dict[int, float] = {}
        for membre in membres:
            for annee, jours in self.jours.get("services", {}).get(membre, {}).items():
                sommes[annee] = sommes.get(annee, 0.0) + jours
        return somme_ordonnee(min(float(JOURS_PAR_AN), jours) for jours in sommes.values())

    def services_effectifs(self, membres: tuple[str, ...]) -> int:
        """Les services effectifs de ces régimes, en trimestres, arrondis au
        décompte final (:func:`arrondir_les_services`)."""
        return arrondir_les_services(self.jours_de_services(membres),
                                     self.decompte["parametres"])

    def services_liquidables(self, membres: tuple[str, ...]) -> int:
        """Le décompte final des trimestres liquidables : les services au jour,
        arrondis, et les bonifications qui ne tiennent à aucune année, en
        trimestres entiers — un an par enfant, ce qui ne change pas l'arrondi."""
        return self.services_effectifs(membres) + somme_ordonnee(
            self.hors_annee["services"].get(membre, 0) for membre in membres)

    def services_des_emplois(self, membres: tuple[str, ...]) -> int:
        """Les trimestres que les emplois classés ajoutent aux services
        liquidés de ces régimes, sous le pourcentage maximum."""
        return somme_ordonnee(e.services for e in self.emplois if e.regime in membres)

    def majorations_des_emplois(self, membres: tuple[str, ...]) -> int:
        """Les trimestres que les emplois classés ajoutent à la seule durée
        que ces régimes opposent à leur décote (L. 14, I)."""
        return somme_ordonnee(e.majoration for e in self.emplois if e.regime in membres)

    @property
    def duree_hors_surcote(self) -> int:
        """Ce que :attr:`trimestres` doit aux emplois classés, et que la
        surcote du fonctionnaire ne lit pas (L. 14, III), « quel que soit le
        régime de retraite de base au titre duquel elles ont été acquises »."""
        return somme_ordonnee(e.duree for e in self.emplois)

    def bonifications_des_emplois(self, membres: tuple[str, ...]) -> int:
        """Ceux de leurs trimestres de services qui portent le pourcentage
        au-delà du maximum, comme les bonifications de L. 12."""
        return somme_ordonnee(e.services for e in self.emplois
                              if e.regime in membres and e.au_dela_du_maximum)

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

    def plafond(self, table: str, annee: int) -> int:
        """Les trimestres qu'un compte retient au plus d'une année : les
        trimestres civils de l'activité qui en couvre le plus, quatre pour
        l'année pleine d'une période assimilée même quand la carrière n'en
        couvre qu'une partie (R. 351-12), et, l'année de la date d'effet, ceux
        qui précèdent le trimestre civil de l'effet, même sans ligne de
        carrière : le compte est « arrêté au dernier jour du trimestre civil
        précédant la date prévue pour l'entrée en jouissance de la pension »
        (R. 351-1), périodes assimilées comprises (circulaire Cnav n° 2004/29,
        point 2121)."""
        plafond = self.carriere.plafond_trimestres(annee)
        if table == "assurance":
            plafond = max(plafond, self.plafonds_assimilees.get(annee, 0))
        return min(plafond, plafond_de_l_annee(self.carriere, annee))

    def cumul_plafonne(self, table: str, membres: tuple[str, ...],
                       annees: Callable[[int], bool] | None = None) -> int:
        """Les trimestres d'un compte, pour un régime ou un groupe de régimes
        liquidés ensemble : sommés ANNÉE PAR ANNÉE, sans dépasser le plafond
        de chaque année (:meth:`plafond`), plus ce qui ne tient à aucune.
        ``annees`` ne garde que les années qu'il accepte, et rien de ce qui ne
        tient à aucune : la durée accomplie en situation de handicap."""
        sommes: dict[int, int] = {}
        for membre in membres:
            for annee, trimestres in self.par_annee[table].get(membre, {}).items():
                if annees is None or annees(annee):
                    sommes[annee] = sommes.get(annee, 0) + trimestres
        return (somme_ordonnee(min(somme, self.plafond(table, annee))
                    for annee, somme in sommes.items())
                + (0 if annees is not None else
                   somme_ordonnee(self.hors_annee[table].get(membre, 0) for membre in membres)))

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
            "emplois": [
                {"regime": e.regime, "fiche": e.fiche, "version": e.version,
                 "services": e.services, "duree": e.duree, "majoration": e.majoration,
                 "au_dela_du_maximum": e.au_dela_du_maximum,
                 "fiabilite": e.fiabilite.name.lower()}
                for e in self.emplois],
            "au_jour": None if self.decompte is None else {
                "version": self.decompte["id"],
                "jours": [
                    {"compte": compte, "regime": regime, "annee": annee, "jours": jours}
                    for compte in ("assurance", "services")
                    for regime, annees in self.jours.get(compte, {}).items()
                    for annee, jours in annees.items()],
                "ecart": self.ecart_au_jour,
            },
            "assimilees": [
                {"motif": a.motif, "regime": a.regime, "annee": a.annee, "fiche": a.fiche,
                 "version": a.version, "trimestres": a.trimestres,
                 "fiabilite": a.fiabilite.name.lower()}
                for a in self.assimilees],
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
    # LES SERVICES DU CODE DES PENSIONS AU JOUR, à côté des trimestres : le
    # décompte final les arrondit une seule fois (R. 26), et la durée que la
    # décote lit ne les arrondit pas (L. 14, I). Les arrondir année par année
    # perdait la fraction de l'année d'entrée et celle du départ : dix mois en
    # 1976 et sept en 2017 font deux mois de plus que 165 trimestres, soit
    # 166 au décompte final, quand le modèle en comptait 165 et une décote.
    # Les jours se comptent dans toute la famille de la fonction publique : les
    # trois régimes liquident aussi les services de ceux qu'ils réunissent —
    # les pensions civiles d'avant 1948, et les deux autres régimes du code
    # (:func:`~.coordonner.groupes_de_succession`), que l'étape ne connaît pas
    # encore. Ne les compter que dans les trois perdait les services d'avant
    # 1948 d'un fonctionnaire de l'État.
    decompte = decompte_des_services(moteur, carriere, annee_liquidation)
    jours: dict[str, dict[str, dict[int, float]]] = {"assurance": {}, "services": {}}
    budget_jours: dict[int, float] = {}
    #: Par année, les jours d'assurance au jour, et les trimestres que les
    #: autres lignes valident : la durée au jour de l'année.
    jours_par_annee: dict[int, float] = {}
    autres_par_annee: dict[int, int] = {}

    def crediter_jours(compte: str, code: str, annee: int, nombre: float) -> None:
        annees = jours[compte].setdefault(code, {})
        annees[annee] = annees.get(annee, 0.0) + nombre

    for ligne, regimes in zip(carriere.lignes, coordination.regimes):
        retenus_ligne = carriere.trimestres_retenus(ligne)
        comptes_au_jour = ([code for code in regimes if code in moteur.catalogue
                            and moteur.catalogue[code].famille == "fonction_publique"]
                           if decompte is not None else [])
        if comptes_au_jour and ligne.services_fonction_publique:
            # Une ligne de services se compte au jour même quand elle ne
            # valide aucun trimestre entier : deux mois d'entrée en novembre.
            duree_jours = jours_de_la_ligne(carriere, ligne)
            if duree_jours > 0:
                services_jours = (duree_jours if ligne.quotite >= 1.0
                                  else duree_jours * ligne.quotite)
                plafond_enfants = ligne.services_plafond_trimestres_par_enfant
                if plafond_enfants:
                    restant = budget_jours.setdefault(
                        plafond_enfants,
                        float(plafond_enfants * carriere.nombre_enfants * JOURS_PAR_TRIMESTRE))
                    services_jours = min(services_jours, restant)
                    budget_jours[plafond_enfants] = restant - services_jours
                for code in comptes_au_jour:
                    crediter_jours("assurance", code, ligne.annee, float(duree_jours))
                    if services_jours > 0:
                        crediter_jours("services", code, ligne.annee, services_jours)
                jours_par_annee[ligne.annee] = (jours_par_annee.get(ligne.annee, 0.0)
                                                + duree_jours)
        elif retenus_ligne > 0:
            autres_par_annee[ligne.annee] = autres_par_annee.get(ligne.annee, 0) + retenus_ligne
        if retenus_ligne <= 0:
            continue
        # Une année que tous ses régimes valident sans cotisation — l'activité
        # cultuelle d'avant 1979 — entre dans la durée, pas parmi les
        # trimestres cotisés (:func:`~.commun.ligne_cotisee`).
        cotisee = ligne_cotisee(moteur, carriere, ligne)
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
            if cotisee:
                crediter_trimestres("cotises", code, ligne.annee, retenus_ligne)
    # Ce que la durée au jour change à la durée tous régimes, année par année :
    # les jours de services, et les trimestres que les autres régimes valident,
    # quatre au plus (R. 26 bis), moins ce que l'année compte en trimestres
    # entiers.
    ecart_au_jour = 0.0
    if decompte is not None and decompte["parametres"]["duree_au_jour"]:
        for annee in sorted(jours_par_annee):
            entiers = carriere.trimestres_par_annee(carriere.lignes_de(annee)).get(annee, 0)
            au_jour_annee = min(4.0, autres_par_annee.get(annee, 0)
                                + jours_par_annee[annee] / JOURS_PAR_TRIMESTRE)
            ecart_au_jour += au_jour_annee - entiers
    # Les périodes assimilées : à l'assurance de leur régime, année par année,
    # et à la durée tous régimes, dans les trimestres civils que leur année
    # laisse libres.
    assimilees = (trimestres_assimiles(moteur, carriere, par_annee["assurance"])
                  if avantages_non_contributifs else ())
    plafonds_assimilees: dict[int, int] = {}
    if assimilees:
        par_annee_assimilees: dict[int, int] = {}
        for assimilee in assimilees:
            crediter_trimestres("assurance", assimilee.regime, assimilee.annee,
                                assimilee.trimestres)
            par_annee_assimilees[assimilee.annee] = (
                par_annee_assimilees.get(assimilee.annee, 0) + assimilee.trimestres)
        for annee in sorted(par_annee_assimilees):
            plafond = plafond_de_l_annee(carriere, annee)
            plafonds_assimilees[annee] = plafond
            deja = carriere.trimestres_par_annee(carriere.lignes_de(annee)).get(annee, 0)
            trimestres += max(0, min(par_annee_assimilees[annee], plafond - deja))
    durees = Durees(carriere, par_annee, hors_annee, None, trimestres, {}, {},
                    plafonds_assimilees=plafonds_assimilees)
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
    # Ce que les emplois classés ajoutent : leur bonification à la durée tous
    # régimes, comme les services et bonifications admissibles en liquidation
    # (L. 14, I), hors de toute année ; le reste, la liquidation du régime qui
    # les sert l'y lit.
    emplois = (trimestres_des_emplois(moteur, carriere, annee_liquidation)
               if avantages_non_contributifs else ())
    trimestres += somme_ordonnee(emploi.duree for emploi in emplois)
    return Durees(carriere, par_annee, hors_annee, majoration_enfants, trimestres,
                  trimestres_par_regime, bonifications_par_regime, etranger, emplois,
                  decompte=decompte, jours=jours if decompte is not None else {},
                  ecart_au_jour=ecart_au_jour, assimilees=assimilees,
                  plafonds_assimilees=plafonds_assimilees)


# -- les périodes assimilées (action 130, sixième domaine) ----------------------

def date_d_effet(carriere: Carriere) -> str:
    """La date d'effet de la pension (AAAA-MM-JJ) : le premier jour du mois
    de la liquidation."""
    mois = carriere.date_liquidation.mois if carriere.age_liquidation is not None else 1
    return f"{carriere.annee_liquidation:04d}-{mois:02d}-01"


def plafond_de_l_annee(carriere: Carriere, annee: int) -> int:
    """Les trimestres civils d'une année que la durée d'assurance peut
    compter : quatre, et ceux qui précèdent la date d'effet l'année où la
    pension prend effet, sauf l'année où l'exploitant agricole cesse, qui en
    compte quatre (:attr:`~retraite_notionnelle.carriere.Carriere.annee_de_cessation_agricole`)."""
    if annee < carriere.annee_liquidation or annee == carriere.annee_de_cessation_agricole:
        return 4
    mois = carriere.date_liquidation.mois if carriere.age_liquidation is not None else 1
    return trimestres_civils(mois - 1)


def trimestres_assimiles(moteur: ScenarioActuel, carriere: Carriere,
                         assurance: dict[str, dict[int, int]]
                         ) -> tuple[TrimestresAssimiles, ...]:
    """Les trimestres des périodes assimilées de la carrière, année par
    année, avant le plafond de l'année : ceux de l'apprentissage
    (:func:`trimestres_de_l_apprentissage`), puis ceux des périodes que la
    personne déclare, dans leur ordre (:func:`trimestres_des_periodes`).

    Une année dont un relevé déposé porte les trimestres n'en reçoit aucun :
    ce que la caisse a validé fait foi, périodes assimilées comprises. Les
    trimestres ne sont pas cotisés, et n'entrent pas aux services.
    """
    if not carriere.chronologie:
        return ()
    effet = date_d_effet(carriere)
    assimilees = (trimestres_de_l_apprentissage(moteur, carriere, assurance, effet)
                  + trimestres_des_periodes(moteur, carriere, effet))
    return tuple(a for a in assimilees
                 if a.trimestres > 0 and a.annee not in carriere.annees_declarees)


def _jour(texte: str) -> datetime.date:
    return datetime.date.fromisoformat(texte)


def _premier_janvier(annee: int) -> datetime.date:
    return datetime.date(annee, 1, 1)


def _mois_suivant(jour: datetime.date) -> datetime.date:
    return (datetime.date(jour.year + 1, 1, 1) if jour.month == 12
            else datetime.date(jour.year, jour.month + 1, 1))


def _trimestre_suivant(jour: datetime.date) -> datetime.date:
    """Le premier jour du trimestre civil qui suit celui de ce jour."""
    mois = 3 * ((jour.month - 1) // 3) + 4
    return (datetime.date(jour.year + 1, 1, 1) if mois > 12
            else datetime.date(jour.year, mois, 1))


def version_ouverte(moteur: ScenarioActuel, fiche: str, motif: str | None,
                    debut: datetime.date, fin: datetime.date, effet: str
                    ) -> tuple[datetime.date, dict] | None:
    """Le premier jour d'une période où la fiche ouvre un droit, et la
    version qui l'ouvre : son début, ou le premier 1er janvier qui le suit,
    puisque les versions se coupent à des 1er janvier. La période commencée
    avant la version qui l'ouvre compte pour ses jours d'après (circulaire
    Cnav 2024-18, 3.2.1.2 ; circulaire 2016-41, point 4) ; celle qui commence
    sous une version ouverte garde celle-ci jusqu'à sa fin — le stage
    commencé la dernière année de son dispositif (circulaire 2024-18,
    annexe 1). ``None`` quand rien ne l'ouvre avant ``fin``."""
    jour = debut
    while jour < fin:
        version = moteur.fiches_datees.version_aux_dates(
            fiche, {"periode.debut": jour.isoformat(), "liquidation.date_effet": effet})
        if version is not None and version["parametres"].get("existe"):
            parametres = version["parametres"]
            if parametres.get("decompte") not in DECOMPTES_DES_ASSIMILEES:
                raise ValueError(f"{fiche}.{version['id']} : décompte inconnu, "
                                 f"{parametres.get('decompte')!r}")
            if motif is None or motif in (parametres.get("motifs") or ()):
                return jour, version
        jour = _premier_janvier(jour.year + 1)
    return None


def _regime_de(moteur: ScenarioActuel, parametres: dict, annee: int,
               assurance: dict[str, dict[int, int]]) -> str | None:
    """Le régime qui valide une période assimilée : le premier de la version
    qui a validé des trimestres cette année, sinon le premier qu'il connaît."""
    connus = [code for code in parametres.get("regimes") or () if code in moteur.catalogue]
    return next((code for code in connus if assurance.get(code, {}).get(annee)),
                connus[0] if connus else None)


def trimestres_du_contrat(debut: datetime.date, fin: datetime.date) -> dict[int, int]:
    """Les trimestres d'un contrat d'apprentissage, année par année
    (D. 373-3) : un mois par mois civil entier d'exécution, un mois par
    trente jours des mois incomplets, totalisés ; un trimestre par trois
    mois, arrondi à l'entier inférieur. Chaque trimestre civil entier va à
    son année ; ce qui reste, à l'année où le contrat prend fin. ``fin`` est
    exclue."""
    mois_entiers, jours = 0, 0
    jour = debut
    while jour < fin:
        suivant = _mois_suivant(jour)
        if jour.day == 1 and suivant <= fin:
            mois_entiers += 1
        else:
            jours += (min(suivant, fin) - jour).days
        jour = suivant
    total = (mois_entiers + jours // JOURS_PAR_MOIS_DE_CONTRAT) // 3
    par_annee: dict[int, int] = {}
    trimestre = (debut if debut.day == 1 and debut.month % 3 == 1
                 else _trimestre_suivant(debut))
    while _trimestre_suivant(trimestre) <= fin:
        par_annee[trimestre.year] = par_annee.get(trimestre.year, 0) + 1
        trimestre = _trimestre_suivant(trimestre)
    reste = total - somme_ordonnee(par_annee.values())
    if reste > 0:
        derniere = (fin - datetime.timedelta(days=1)).year
        par_annee[derniere] = par_annee.get(derniere, 0) + reste
    return par_annee


def _contrats(carriere: Carriere) -> list[tuple[datetime.date, datetime.date]]:
    """Les contrats d'apprentissage de la carrière : ses emplois qui portent
    l'attribut, ceux qui se suivent sans interruption réunis — le temps
    partiel coupe un contrat en morceaux."""
    contrats: list[list[datetime.date]] = []
    for periode in chrono.periodes(carriere.chronologie, carriere.personne):
        if periode["sorte"] != chrono.EMPLOI or not periode["attributs"].get("apprentissage"):
            continue
        debut, fin = _jour(periode["debut"]), _jour(periode["fin"])
        if contrats and contrats[-1][1] == debut:
            contrats[-1][1] = fin
        else:
            contrats.append([debut, fin])
    return [(debut, fin) for debut, fin in sorted(contrats)]


def trimestres_de_l_apprentissage(moteur: ScenarioActuel, carriere: Carriere,
                                  assurance: dict[str, dict[int, int]], effet: str
                                  ) -> list[TrimestresAssimiles]:
    """Le complément de l'apprentissage, année par année : les trimestres du
    contrat (:func:`trimestres_du_contrat`) moins ceux que l'année a déjà
    validés dans son régime (D. 373-4), quand la version de la fiche ouvre le
    droit — le contrat d'avant 2014 ne compte qu'à partir du 1er janvier 2014.

    Le moteur ne sait pas quels trimestres de l'année la rémunération de
    l'apprenti valide, et ceux d'un autre emploi de la même année : il
    retire tous ceux du régime, et l'apprenti qui change d'emploi en cours
    d'année reçoit moins que le complément (fiche ``apprentissage``)."""
    resultat: list[TrimestresAssimiles] = []
    fin_de_carriere = _jour(effet)
    for debut, fin in _contrats(carriere):
        fin = min(fin, fin_de_carriere)
        ouverte = version_ouverte(moteur, FICHE_DE_L_APPRENTISSAGE, None, debut, fin, effet)
        if ouverte is None:
            continue
        ouverture, version = ouverte
        parametres = version["parametres"]
        for annee, du_contrat in sorted(trimestres_du_contrat(ouverture, fin).items()):
            regime = _regime_de(moteur, parametres, annee, assurance)
            if regime is None:
                continue
            valides = assurance.get(regime, {}).get(annee, 0)
            resultat.append(TrimestresAssimiles(
                motif=FICHE_DE_L_APPRENTISSAGE, regime=regime, annee=annee,
                fiche=FICHE_DE_L_APPRENTISSAGE, version=version["id"],
                texte=version["texte"], trimestres=max(0, du_contrat - valides),
                fiabilite=Fiabilite.depuis_texte(parametres["fiabilite"])))
    return resultat


def jours_par_annee(debut: datetime.date, fin: datetime.date,
                    jours: int | None = None) -> dict[int, int]:
    """Les jours d'une période, année civile par année civile, ``fin``
    exclue ; ou ``jours`` qu'elle compte entre ses dates, répartis au
    prorata de ses jours de calendrier, sans fraction : chaque année reçoit
    ce que son cumul arrondi à l'entier inférieur lui laisse."""
    calendrier: dict[int, int] = {}
    jour = debut
    while jour < fin:
        suivant = min(_premier_janvier(jour.year + 1), fin)
        calendrier[jour.year] = (suivant - jour).days
        jour = suivant
    if jours is None:
        return calendrier
    total = somme_ordonnee(calendrier.values())
    reparti: dict[int, int] = {}
    cumul, donnes = 0, 0
    for annee, nombre in calendrier.items():
        cumul += nombre
        part = jours * cumul // total - donnes
        reparti[annee] = part
        donnes += part
    return reparti


def _anniversaire(carriere: Carriere, age: int) -> datetime.date:
    """Le jour anniversaire de cet âge : le 1er mars pour qui est né un
    29 février."""
    naissance = _jour(chrono.naissance(carriere.chronologie, carriere.personne)["debut"])
    try:
        return naissance.replace(year=naissance.year + age)
    except ValueError:
        return datetime.date(naissance.year + age, 3, 1)


def trimestres_des_periodes(moteur: ScenarioActuel, carriere: Carriere, effet: str
                            ) -> list[TrimestresAssimiles]:
    """Les trimestres des périodes assimilées que la personne déclare.

    Les jours dans l'année (``jours_dans_l_annee``) — stages, congé
    supplémentaire de naissance — s'additionnent par fiche et par année, une
    période comptant ses ``jours`` déclarés ou ses jours de calendrier : un
    trimestre par tranche que la version dit, sans report d'une année sur
    l'autre. Les périodes continues (``periodes_continues``) — les sportifs de
    haut niveau — comptent un trimestre par tranche de jours continus depuis
    le premier jour d'inscription après l'âge que la version dit, affecté à
    l'année qui en porte le plus, quand les revenus de cette année ne
    dépassent pas la fraction du plafond de la sécurité sociale qu'elle dit,
    et jusqu'à son plafond de trimestres. Les jours d'après la date d'effet
    ne comptent pas."""
    fin_de_carriere = _jour(effet)
    # Par fiche et par année : le motif et la version de la première période,
    # puis les jours, ou les trimestres des périodes continues.
    jours_cumules: dict[tuple[str, int], list] = {}
    continues: dict[tuple[str, int], list] = {}
    sportifs: dict[str, int] = {}
    for periode in chrono.periodes_assimilees(carriere.chronologie, carriere.personne):
        attributs = periode["attributs"]
        motif = attributs["motif"]
        fiche = FICHES_DES_ASSIMILEES[motif]
        debut, fin_declaree = _jour(periode["debut"]), _jour(periode["fin"])
        fin = min(fin_declaree, fin_de_carriere)
        ouverte = version_ouverte(moteur, fiche, motif, debut, fin, effet)
        if ouverte is None:
            continue
        ouverture, version = ouverte
        parametres = version["parametres"]
        par_tranche = int(parametres["jours_par_trimestre"])
        if parametres["decompte"] == "jours_dans_l_annee":
            jours = attributs.get("jours")
            if jours is not None:
                jours = jours * (fin - ouverture).days // (fin_declaree - debut).days
            for annee, nombre in jours_par_annee(ouverture, fin, jours).items():
                cle = (fiche, annee)
                jours_cumules.setdefault(cle, [motif, version, 0])[2] += nombre
            continue
        if parametres["decompte"] == "periodes_continues":
            ouverture = max(ouverture, _anniversaire(carriere, int(parametres["age_minimum"])))
            plafond = int(parametres["plafond_trimestres"])
            tranche = ouverture
            while (tranche + datetime.timedelta(days=par_tranche) <= fin
                   and sportifs.get(fiche, 0) < plafond):
                fin_tranche = tranche + datetime.timedelta(days=par_tranche)
                repartis = jours_par_annee(tranche, fin_tranche)
                annee = max(repartis, key=lambda a: (repartis[a], -a))
                tranche = fin_tranche
                revenus = somme_ordonnee(ligne.revenu for ligne in carriere.lignes_de(annee))
                if revenus > (float(parametres["ressources_maximum_en_plafonds"])
                              * moteur.macro.plafond_securite_sociale(annee)):
                    continue
                sportifs[fiche] = sportifs.get(fiche, 0) + 1
                continues.setdefault((fiche, annee), [motif, version, 0])[2] += 1
            continue
        raise ValueError(f"{fiche}.{version['id']} : la fiche d'une période assimilée "
                         f"ne compte pas la durée d'un contrat")
    resultat: list[TrimestresAssimiles] = []
    for comptes, en_jours in ((jours_cumules, True), (continues, False)):
        for (fiche, annee), (motif, version, nombre) in comptes.items():
            parametres = version["parametres"]
            regime = _regime_de(moteur, parametres, annee, {})
            if regime is None:
                continue
            resultat.append(TrimestresAssimiles(
                motif=motif, regime=regime, annee=annee, fiche=fiche, version=version["id"],
                texte=version["texte"],
                trimestres=(nombre // int(parametres["jours_par_trimestre"]) if en_jours
                            else nombre),
                fiabilite=Fiabilite.depuis_texte(parametres["fiabilite"])))
    return resultat


def decompte_des_services(moteur: ScenarioActuel, carriere: Carriere,
                          annee_liquidation: int) -> dict | None:
    """La version de la fiche du décompte (:data:`FICHE_DU_DECOMPTE`) qui vaut
    à la date d'effet — son identifiant et ses paramètres —, ``None`` quand
    elle ne compte pas au jour : sans version, ou d'avant le code de 1964.

    Un paramètre que le moteur ne connaît pas l'arrête (§ 6.7) : une unité
    nulle, un seuil hors d'elle, un minimum garanti sans nom connu.
    """
    mois = carriere.date_liquidation.mois if carriere.age_liquidation is not None else 1
    version = moteur.fiches_datees.version(
        FICHE_DU_DECOMPTE, f"{annee_liquidation:04d}-{mois:02d}-01")
    if version is None or not version["parametres"].get("existe"):
        return None
    parametres = version["parametres"]
    unite, seuil = parametres["unite_jours"], parametres["seuil_jours"]
    if not (isinstance(unite, int) and unite > 0 and 0 < seuil <= unite):
        raise ValueError(f"{FICHE_DU_DECOMPTE}.{version['id']} : unité {unite!r}, "
                         f"seuil {seuil!r}")
    if parametres["minimum_garanti"] not in MINIMA_DU_DECOMPTE:
        raise ValueError(f"{FICHE_DU_DECOMPTE}.{version['id']} : minimum garanti "
                         f"inconnu, {parametres['minimum_garanti']!r}")
    return {"id": version["id"], "parametres": parametres}


def jours_de_la_ligne(carriere: Carriere, ligne) -> int:
    """Les jours de services qu'une ligne compte, l'année de trois cent
    soixante jours : ses mois, coupés au départ, de trente jours chacun ; sur
    un relevé, les trimestres qu'il porte, fractions comprises, à
    quatre-vingt-dix jours (:attr:`~retraite_notionnelle.carriere.AnneeCarriere.jours_de_services`),
    sans dépasser ces mois.

    Le modèle connaît la carrière au mois : la fraction d'un mois se néglige
    au décompte final, celle de deux mois fait le trimestre — le texte compte
    au jour, et le seuil de quarante-cinq jours tombe entre les deux.
    """
    part = carriere.part_retenue_ligne(ligne)
    if part <= 0:
        return 0
    jours = round(part * 12) * JOURS_PAR_MOIS
    if ligne.jours_de_services is not None:
        jours = min(jours, ligne.jours_de_services)
    return jours


def arrondir_les_services(jours: float, parametres: dict) -> int:
    """Le décompte final des trimestres liquidables, en trimestres : les jours
    de services par unités entières (le trimestre depuis 2004, le semestre
    avant), la fraction d'au moins ``seuil_jours`` comptée pour une unité,
    la fraction plus courte négligée (R. 26).

    « Services liquidables : 20 ans 6 mois et 13 jours ; Bonifications : 1 an
    1 mois et 2 jours [...] En liquidation du droit : 86 trimestres 1 mois et
    15 jours soit 86 trimestres et 45 jours donc 87 trimestres » (CNRACL,
    « Trimestres liquidables »).
    """
    unite = int(parametres["unite_jours"])
    seuil = float(parametres["seuil_jours"])
    entieres = math.floor((jours + EPSILON_JOURS) / unite)
    if jours - entieres * unite + EPSILON_JOURS >= seuil:
        entieres += 1
    return entieres * unite // JOURS_PAR_TRIMESTRE


def services_a_temps_partiel(trimestres: int, quotite: float) -> int:
    """Les trimestres de services d'une année travaillée à ``quotite`` : sa
    durée réelle, quand la durée d'assurance la compte entière (L. 11 et L. 14
    du code des pensions ; D. 37-3 pour la retraite progressive). Arrondie
    au trimestre, un demi-trimestre et plus comptant pour un — les
    quarante-cinq jours de L. 13 —, année par année."""
    if quotite >= 1.0:
        return trimestres
    return int(trimestres * quotite + 0.5)


def trimestres_des_emplois(moteur: ScenarioActuel, carriere: Carriere,
                           annee_liquidation: int) -> tuple[TrimestresEmploi, ...]:
    """Ce que les emplois classés de la carrière ajoutent, une fiche après
    l'autre (:data:`FICHES_DES_EMPLOIS`).

    La version de chaque fiche se lit à la date d'effet de la pension. Une
    fiche sans version à cette date, ou dont la version dit que le droit
    n'existe pas encore, n'ajoute rien ; les autres disent le statut qui
    ouvre le droit, le régime qui le sert, et comment le compter
    (:func:`trimestres_d_un_emploi`). Une version qui borne le cumul — « dans
    la limite de vingt trimestres » depuis septembre 2023 (L. 14, I ; décret
    n° 2003-1306, article 21, III) — ne garde de son effet en durée que ce
    que les fiches qui la précèdent lui laissent.
    """
    mois = carriere.date_liquidation.mois if carriere.age_liquidation is not None else 1
    date_effet = f"{annee_liquidation:04d}-{mois:02d}-01"
    emplois: list[TrimestresEmploi] = []
    for nom in FICHES_DES_EMPLOIS:
        version = moteur.fiches_datees.version(nom, date_effet)
        if version is None or not version["parametres"].get("existe"):
            continue
        emploi = trimestres_d_un_emploi(moteur, carriere, nom, version)
        if emploi is None:
            continue
        cumul = version["parametres"].get("cumul_maximum_trimestres")
        if cumul is not None:
            # Une bonification y porte ses services et sa durée, une
            # majoration sa seule majoration : l'un ou l'autre se borne.
            reste = max(0, int(cumul) - somme_ordonnee(e.duree + e.majoration for e in emplois))
            emploi = replace(emploi, services=min(emploi.services, reste),
                             duree=min(emploi.duree, reste),
                             majoration=min(emploi.majoration, reste))
            if not (emploi.services or emploi.majoration):
                continue
        emplois.append(emploi)
    return tuple(emplois)


def trimestres_d_un_emploi(moteur: ScenarioActuel, carriere: Carriere, fiche: str,
                           version: dict) -> TrimestresEmploi | None:
    """Ce qu'un emploi classé ouvre, ou ``None`` s'il n'ouvre rien.

    Une BONIFICATION est une fraction du temps servi dans les statuts qui
    l'ouvrent — « un cinquième du temps qu'ils ont effectivement passé en
    position d'activité dans des services actifs de police » (loi n° 57-444,
    article 1er) —, sous son plafond — « cinq annuités » —, diminuée des
    services accomplis au-delà de l'âge qui la réduit — « à concurrence de la
    durée des services accomplis au-delà de cinquante-cinq ans », puis
    cinquante-sept, jusqu'en août 2023 —, ceux-ci comptés au mois
    (:func:`services_au_dela`). Celle des militaires perd « une annuité pour
    chaque année supplémentaire de service » (``reduction_par_annee_entiere``),
    et n'est plus due au-delà de l'âge qui la supprime (``age_de_suppression``)
    : le service des retraites de l'État n'en accorde « aucune […] au delà de
    62 ans », sauf au militaire radié « le lendemain de ses 62 ans », à qui il
    en reste deux ans. Elle entre aux services liquidés et à la durée tous
    régimes.

    Une MAJORATION est une fraction des services effectifs de la fonction
    publique civile — « un an par période de dix années de services
    effectifs », au prorata (loi n° 2003-775, article 78) —, sans plafond.
    Elle n'entre qu'à la durée que le régime oppose à sa décote.

    L'une et l'autre se comptent en trimestres, arrondies comme les services
    et bonifications de L. 13, un demi-trimestre et plus comptant pour un.
    La condition est celle que la version nomme
    (:data:`CONDITIONS_DES_EMPLOIS`, :func:`condition_d_un_emploi`). Une
    nature ou une condition que le moteur ne connaît pas l'arrête (§ 6.7).
    """
    parametres = version["parametres"]
    nature = parametres["nature"]
    if nature not in NATURES_DES_EMPLOIS:
        raise ValueError(f"{fiche}.{version['id']} : nature inconnue, {nature!r}")
    condition = parametres["condition"]
    if condition not in CONDITIONS_DES_EMPLOIS:
        raise ValueError(f"{fiche}.{version['id']} : condition inconnue, {condition!r}")
    statuts = list(parametres["statuts"])
    regime = parametres["regime"]
    if (regime not in moteur.catalogue
            or regime not in coordonner.regimes_routes(moteur, statuts)):
        return None
    borne = coordonner.borne_carriere(carriere)
    servies = carriere.duree_de_service(statuts, borne)
    if servies <= 0:
        return None
    ouverte = condition_d_un_emploi(moteur, carriere, condition, parametres, servies)
    if ouverte is None:
        return None
    fiabilite = min(Fiabilite.depuis_texte(parametres["fiabilite"]), ouverte)
    bonification = nature == "bonification"
    base = (servies if bonification
            else carriere.duree_de_service(list(parametres["services_comptes"]), borne))
    annees = base * float(parametres["fraction"])
    if parametres.get("plafond_trimestres") is not None:
        annees = min(annees, int(parametres["plafond_trimestres"]) / 4)
    if parametres.get("age_de_suppression") is not None:
        age, lue = age_de_suppression(moteur, carriere, fiche, version)
        if services_au_dela(carriere, statuts, age, borne, servies) > EPSILON_ANNEES:
            return None
        fiabilite = min(fiabilite, lue)
    if parametres.get("age_de_reduction") is not None:
        au_dela = services_au_dela(carriere, statuts, float(parametres["age_de_reduction"]),
                                   borne, servies)
        annees -= (math.floor(au_dela + EPSILON_ANNEES)
                   if parametres.get("reduction_par_annee_entiere") else au_dela)
    trimestres = int(annees * 4 + 0.5) if annees > 0 else 0
    if trimestres <= 0:
        return None
    return TrimestresEmploi(
        regime=regime, fiche=fiche, version=version["id"], texte=version["texte"],
        services=trimestres if bonification else 0,
        duree=trimestres if bonification else 0,
        majoration=0 if bonification else trimestres,
        au_dela_du_maximum=bool(parametres["au_dela_du_maximum"]), fiabilite=fiabilite)


def services_au_dela(carriere: Carriere, statuts: list[str], age: float,
                     borne: int | None, servies: float) -> float:
    """Les années servies dans ces statuts au-delà de cet âge, ``servies``
    étant celles de toute la carrière : depuis le premier mois vécu entier à
    cet âge (:meth:`~retraite_notionnelle.carriere.Carriere.date_de_l_age`),
    au mois près (:meth:`~retraite_notionnelle.carriere.Carriere.duree_de_service_avant`).

    Le militaire radié le lendemain de ses soixante-deux ans, qui part au
    premier du mois suivant, n'a rien servi au-delà de cet âge ; il a servi
    trois ans au-delà de cinquante-neuf.
    """
    avant = carriere.duree_de_service_avant(statuts, carriere.date_de_l_age(age), borne)
    return max(0.0, servies - avant)


def age_de_suppression(moteur: ScenarioActuel, carriere: Carriere, fiche: str,
                       version: dict) -> tuple[float, Fiabilite]:
    """L'âge au-delà duquel la version supprime la bonification, et la
    fiabilité de sa lecture : écrit en années, ou l'âge légal de la
    génération (:data:`AGE_LEGAL`). Une valeur que le moteur ne connaît pas
    l'arrête (§ 6.7)."""
    parametres = version["parametres"]
    age = parametres["age_de_suppression"]
    if age == AGE_LEGAL:
        legal = moteur.ages_ouverture.age(carriere.generation)
        if legal is None:
            raise ValueError(f"{fiche}.{version['id']} : pas d'âge légal pour la "
                             f"génération {carriere.generation}")
        return legal
    if isinstance(age, bool) or not isinstance(age, (int, float)):
        raise ValueError(f"{fiche}.{version['id']} : âge de suppression inconnu, {age!r}")
    return float(age), Fiabilite.depuis_texte(parametres["fiabilite"])


def services_actifs_requis(moteur: ScenarioActuel, carriere: Carriere, classement: str,
                           statuts: list[str], base: float) -> float:
    """Les années de services classés qu'exige l'âge anticipé ou minoré.

    ``base`` est la durée d'avant la loi du 9 novembre 2010, quinze ans ou
    vingt-cinq ; son article 35 la relève selon l'année où ``statuts`` l'ont
    atteinte (décret n° 2011-2103, article 6) : quinze ans à qui les avait
    avant le 1er juillet 2011, dix-sept à qui les atteint depuis 2015. Qui ne
    l'atteint pas se voit opposer la durée relevée, qu'il n'a pas non plus.
    """
    atteinte = carriere.date_de_service(statuts, base)
    annee = 9999.0 if atteinte is None else atteinte.annee + (atteinte.mois - 1) / 12
    requises = moteur.durees_services_actifs.annees_requises(classement, annee)
    return base if requises is None else requises[0]


def condition_d_un_emploi(moteur: ScenarioActuel, carriere: Carriere, condition: str,
                          parametres: dict, servies: float) -> Fiabilite | None:
    """La condition remplie, et la fiabilité de ce qu'elle a lu ; ``None``
    sinon. ``servies`` : les années servies dans les statuts de la fiche.

    La durée de services classés et l'âge anticipé ou minoré sont ceux de la
    génération, au classement que la version nomme. Les services actifs
    sont ceux de tous les statuts classés, les super-actifs compris : ils
    « peuvent être comptabilisés comme services actifs » (L. 24, I, 1°).
    La durée dans l'emploi du militaire ne lit aucun classement : ses dix-sept
    ans, quinze avant juillet 2011, sont écrits dans la version.
    """
    if condition == "duree_dans_l_emploi":
        if servies + EPSILON_ANNEES < float(parametres["annees_dans_l_emploi"]):
            return None
        if parametres["en_fonction"]:
            borne = coordonner.borne_carriere(carriere)
            comptes = carriere.bornes_de_service(list(parametres["services_comptes"]), borne)
            dans_l_emploi = carriere.bornes_de_service(list(parametres["statuts"]), borne)
            if comptes is None or dans_l_emploi is None or dans_l_emploi[1] < comptes[1]:
                return None
        return Fiabilite.depuis_texte(parametres["fiabilite"])
    derogation = moteur.ages_categorie_active.derogation(
        parametres["classement"], carriere.generation)
    if condition == "durees_et_age_de_l_emploi":
        radiation = carriere.radiation_pour_invalidite
        if radiation is not None and radiation.imputable:
            return Fiabilite.depuis_texte(parametres["fiabilite"])
        borne = coordonner.borne_carriere(carriere)
        publiques = carriere.duree_de_service(list(parametres["services_comptes"]), borne)
        if (servies + 1e-9 < float(parametres["annees_dans_l_emploi"])
                or publiques + 1e-9 < float(parametres["annees_de_services"])):
            return None
        if not parametres["age_anticipe"]:
            return Fiabilite.depuis_texte(parametres["fiabilite"])
        if (derogation is None or carriere.age_liquidation is None
                or carriere.age_liquidation + 1e-9 < derogation.age_ouverture):
            return None
        return derogation.fiabilite
    if condition == "duree_de_l_age_minore":
        if carriere.radiation_pour_invalidite is not None:
            return Fiabilite.depuis_texte(parametres["fiabilite"])
        if derogation is None or servies + 1e-9 < services_actifs_requis(
                moteur, carriere, parametres["classement"], list(parametres["statuts"]),
                derogation.services_requis):
            return None
        return derogation.fiabilite
    borne = coordonner.borne_carriere(carriere)
    classes = list(moteur.affiliations.classements_actifs)
    actifs = carriere.duree_de_service(classes, borne)
    if derogation is None or actifs + 1e-9 < services_actifs_requis(
            moteur, carriere, parametres["classement"], classes, derogation.services_requis):
        return None
    if condition == "duree_de_la_categorie_active":
        return derogation.fiabilite
    # ``categorie_active_en_fonction`` : l'âge anticipé atteint à la
    # radiation, et la dernière année de la fonction publique civile servie
    # dans l'un des statuts de la fiche.
    if (carriere.age_liquidation is None
            or carriere.age_liquidation + 1e-9 < derogation.age_ouverture):
        return None
    publiques = carriere.bornes_de_service(list(parametres["services_comptes"]), borne)
    dans_l_emploi = carriere.bornes_de_service(list(parametres["statuts"]), borne)
    if publiques is None or dans_l_emploi is None or dans_l_emploi[1] < publiques[1]:
        return None
    return derogation.fiabilite


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
        periode = periode_de_liquidation(regime, DateMois(annee_liquidation, mois))
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

    Hors la fonction publique, la SNCF, la RATP, les IEG et la CRPCEN ont
    leur fiche, qui pose l'une de ces conditions ; les autres régimes spéciaux reçoivent
    celles de la fonction publique avec sa fiche. Une condition que le moteur
    ne connaît pas l'arrête (§ 6.7).
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
    qui en fait la somme. Ceux que les mois de la ligne couvrent
    (:meth:`~retraite_notionnelle.carriere.Carriere.trimestres_ecoules`).
    """
    retenus = carriere.trimestres_ecoules(ligne)
    mois_ligne = round(carriere.part_retenue(ligne.annee) * 12)
    if retenus <= 0 or mois_ligne <= 0:
        return 0.0
    premier = (DateMois(ligne.annee, 1)
               if mois_ligne == 12 or ligne.annee == carriere.annee_liquidation
               else DateMois(ligne.annee, 13 - mois_ligne))
    dernier = premier.plus_mois(mois_ligne)
    recouvrement = (min(fin.rang, dernier.rang) - max(debut.rang, premier.rang))
    return retenus * recouvrement / mois_ligne if recouvrement > 0 else 0.0
