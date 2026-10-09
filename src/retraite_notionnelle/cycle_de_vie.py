"""Les indicateurs de cycle de vie : ce qu'une carrière verse, ce qu'elle reçoit.

Le taux de remplacement compare une pension à un salaire, le jour du départ. Il
ne dit ni pendant combien de temps la pension sera servie, ni ce qu'elle a
coûté : un départ tardif le relève alors qu'il raccourcit la retraite, et un
système qui prélève davantage pour servir autant n'y paraît pas. Les autres
modèles le complètent par quatre indicateurs que le dépôt n'avait pas (action
138, étape 9 ; registre des modèles, chantier « 138.9 ») :

* la DURÉE DE RETRAITE, en années, en part de la vie et rapportée à la
  carrière — le premier indicateur d'équité que suit le COR (décret
  n° 2014-654 du 20 juin 2014) ;
* le TAUX DE RÉCUPÉRATION, somme des pensions sur somme des cotisations,
  chacune rapportée au salaire moyen par tête de son année
  (TRAJECTOiRE, ``txRecuperation``), avec ses deux voisins de la même unité :
  le taux d'annuité, pensions sur revenus d'activité, et le taux de
  remplacement sur le cycle de vie, pension moyenne d'une année de retraite
  sur revenu moyen d'une année de carrière ;
* le RENDEMENT INTERNE, le taux qui égalise la valeur actuelle des
  cotisations et celle des pensions (le COR, « calculs SG-COR ») : réel quand
  les flux sont déflatés des prix, relatif quand ils sont rapportés au salaire
  moyen, comme le COR l'actualise depuis son rapport de juin 2026 ;
* le PATRIMOINE RETRAITE, valeur au départ des pensions espérées, actualisées
  à 1,5 % réel, en années de dernier revenu (l'OCDE, *Pensions at a Glance*),
  avec deux voisins que calcule PROST, de la Banque mondiale : la valeur
  actuelle nette, patrimoine moins cotisations capitalisées au même taux, et
  le taux de remplacement au décès, ce que la pension de la dernière année
  vaut contre le dernier revenu mené jusque-là par le salaire moyen.

DEUX FLUX PAR SYSTÈME (:class:`Flux`). Chaque carrière est vue, sous chacun
des six systèmes, comme deux chroniques en euros courants, année civile par
année civile : ce qu'elle verse, ce qu'elle reçoit.

CE QUI EST VERSÉ, C'EST CE QUE LA PAIE SUPPORTE pour la retraite, et non ce
qui est porté au compte : la cotisation salariale et la patronale, aux taux
du droit en vigueur de chaque régime, de l'État la part de sa contribution
que la Cour des comptes rattache à la retraite de l'agent, et les
contributions d'équilibre de l'Agirc-Arrco — l'ASF, l'AGFF, la CET de l'Agirc,
la CEG et la CET —, que le compte ne porte pas, mais que la paie supporte
pour la retraite complémentaire (:func:`cotisations_versees`,
:mod:`~retraite_notionnelle.contributions_equilibre`). Les scénarios 2 à 5
ne diffèrent entre eux que par ce qui est porté au compte, non par ce que la
paie supporte : l'employeur verse toujours sa part, elle finance toujours le
système, elle n'ouvre plus de droit à celui qui la voit passer. Ils versent
donc tous ce que prélève le compte du scénario 4, et jusqu'à la bascule les
contributions d'équilibre (:func:`cotisations_reformees`) : ce que verse le
scénario 1 jusqu'à elle, puis le taux du régime fusionné, qu'ils prélèvent
pour tous et qui remplace la complémentaire et ses contributions. Le 6 verse
ce que verse le scénario 1 jusqu'à la bascule, puis son taux unique et les
deux parts de son pilier capitalisé, puisque la rente qu'il sert entre dans
ce qu'il reçoit (:func:`cotisations_liberales`). Ce que les régimes
provisionnés — le RAFP — encaissent et servent est hors des deux flux, comme
il est hors de la comparaison des six systèmes.

CE QUI EST REÇU, C'EST CE QUI EST SERVI, année après année
(:func:`niveaux_actuels`, :func:`niveaux_notionnels`). Le scénario 1 suit le
droit : chaque régime revalorisé par ses textes jusqu'à l'année courante
(:func:`~retraite_notionnelle.revalorisation.faire_vivre`), puis par la
convention de projection de la page Coût — les prix, et pour l'Agirc-Arrco la
valeur de service que le COR projette (:func:`~.cout.coefficient_actuel`).
Les systèmes notionnels suivent la règle de leur compte, et celle du stock à
la bascule (:class:`~.revalorisation.RevalorisationServie`), sur toute la
retraite et non jusqu'à l'année courante seulement. Le niveau d'une année est
celui du 31 décembre, revalorisations de l'année comprises : une
revalorisation d'octobre (le régime général de 2014 à 2018) ou de novembre
(l'Agirc-Arrco) y compte pour l'année entière. N'y entrent ni l'ASPA ni la
garantie vieillesse, que l'impôt finance et qui ne sont pas la contrepartie
d'une cotisation, ni la réversion, qui est un droit d'un autre.

LA FIN DE LA RETRAITE est une convention (:class:`Convention`), et les
références n'ont pas la même :

* la SURVIE DE GÉNÉRATION du dépôt, la table du diviseur, par sexe ou des
  deux sexes réunis : chaque année de pension compte pour la probabilité d'y
  être en vie, sachant qu'on l'était au départ. C'est l'espérance que
  l'OCDE calcule, sur la mortalité de cohorte de l'ONU, et le défaut ;
* un ÂGE DE DÉCÈS FIXE : 60 ans plus l'espérance de vie à 60 ans de la
  génération pour le COR (:func:`age_de_deces_cor`), le même arrondi à l'année
  et augmenté de six mois pour TRAJECTOiRE.

Les cotisations, elles, ne sont pas pondérées par la survie : comme chez le
COR et l'OCDE, la carrière est celle de qui atteint le départ.

EN NET, chaque année au taux de son année. La pension perd les prélèvements
de l'année où elle est servie, au taux plein de CSG (:func:`prelevements_par_annee`) :
rien avant le 1er juillet 1980, puis la cotisation maladie, la CSG, la CRDS, la
CASA, que l'IPP retrace (:mod:`~retraite_notionnelle.donnees.prelevements_historiques`),
dont la dernière marche tient au-delà. Ce qui la rapporte à un revenu
d'activité le rapporte au revenu net de la même année (:func:`revenus_nets`) :
la fiche de paie du droit en vigueur, ramenée aux prélèvements de son année,
et celle de la proposition pour le scénario 6 après la bascule, comme le site.
Le patrimoine reste en années de dernier revenu brut, comme l'OCDE l'exprime.

À CHAQUE ÂGE DE DÉPART (:func:`balayage`). Calculés au seul âge où un cas type
part, les indicateurs ne disent pas ce qu'un départ plus tôt ou plus tard
change. TRAJECTOiRE les calcule de trimestre en trimestre, de l'âge
d'ouverture, carrière longue comprise, à l'âge d'annulation de la décote,
sous plusieurs productivités, en net, avec la pension nette rapportée à
l'ASPA et le taux de remplacement net en euros courants, constants et en
salaire moyen ; le dépôt fait de même (:class:`Depart`), sous les trois
productivités du COR (:func:`hypotheses_de_productivite`).

CE QUE LE MODULE NE FAIT PAS. La pension nette l'est au taux plein de CSG, sans
le taux réduit ni le médian que le revenu fiscal d'un foyer ouvrirait ; la
maladie des pensions des régimes de base autres que le régime général, que
l'IPP n'écrit pas, n'y est pas ; l'indépendant garde les prélèvements hors
retraite de l'année courante. Il ne s'affiche pas encore sur le site, et n'a
pas de jumeau JavaScript, pas plus que
:mod:`~retraite_notionnelle.contributions_equilibre`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

from pathlib import Path

from . import pilote
from .config import RevalorisationStock
from .contributions_equilibre import contributions_d_une_carriere, part_salariale_annualisee
from .cout import coefficient_actuel
from .donnees.chargement import charger_yaml
from .donnees.prelevements_historiques import FAMILLES, charger_prelevements_historiques
from .donnees.mortalite import AGE_TERMINAL
from .remuneration import (
    charger_prelevements,
    fiche_depuis_brut,
    profil_de_la_fiche,
    remuneration_de_la_carriere,
)
from .revalorisation import RevalorisationServie, faire_vivre
from .somme import somme_ordonnee

#: Les six systèmes, dans l'ordre de la comparaison : les attributs de
#: :class:`~retraite_notionnelle.simulateur.Comparaison`.
SCENARIOS: tuple[str, ...] = (
    "actuel",
    "notionnel_retroactif",
    "notionnel_prospectif",
    "notionnel_retroactif_employeur",
    "notionnel_prospectif_employeur",
    "notionnel_liberal",
)

#: Le taux réel auquel l'OCDE actualise le patrimoine retraite (*Pensions at
#: a Glance 2025*, p. 160-161 ; registre, ``modeles_ocde``).
TAUX_ACTUALISATION_OCDE = 0.015

#: Les bornes de la recherche d'un rendement interne : de −50 % à +100 % par
#: an. Un rendement hors de ces bornes n'a pas de sens pour une carrière, et
#: la dichotomie n'en cherche pas.
BORNES_RENDEMENT = (-0.5, 1.0)


@dataclass(frozen=True)
class Convention:
    """Comment une retraite finit, et comment on la compte.

    Le défaut est la convention de l'OCDE : la survie de génération du sexe de
    la carrière, le patrimoine actualisé à 1,5 % réel, la pension brute. Celle
    du COR se bâtit carrière par carrière (:func:`convention_cor`)."""

    #: L'âge du décès, quand la convention le fixe ; ``None`` pour la survie
    #: de génération du dépôt.
    age_deces: float | None = None
    #: La table des deux sexes réunis, comme les cas types du COR, qui n'en
    #: ont pas ; celle du sexe de la carrière sinon.
    unisexe: bool = False
    #: Le taux réel du patrimoine retraite.
    taux_actualisation: float = TAUX_ACTUALISATION_OCDE
    #: Ce que les prélèvements retirent à la pension, en part du brut, pour
    #: des indicateurs nets (:func:`taux_de_prelevement`). Les cotisations ne
    #: changent pas.
    prelevement: float = 0.0
    #: Le même, année par année, que l'histoire des prélèvements donne
    #: (:func:`prelevements_par_annee`) : une année qu'il ne porte pas prend
    #: ``prelevement``.
    prelevements: dict[int, float] | None = None

    @property
    def nette(self) -> bool:
        """La pension est-elle nette des prélèvements ?"""
        return self.prelevement > 0.0 or bool(self.prelevements)

    def retenu(self, annee: int) -> float:
        """La part de la pension de l'année ``annee`` que les prélèvements
        laissent."""
        if self.prelevements is not None and annee in self.prelevements:
            return 1.0 - self.prelevements[annee]
        return 1.0 - self.prelevement


@dataclass(frozen=True)
class Flux:
    """Ce qu'une carrière verse et reçoit sous un système, en euros courants
    de chaque année."""

    scenario: str
    #: Ce qui est versé chaque année pour la retraite, salariale et patronale
    #: (:func:`cotisations_versees`).
    cotisations: dict[int, float]
    #: Les revenus d'activité des années cotisées.
    revenus: dict[int, float]
    #: Le niveau ANNUEL de la pension au 31 décembre de chaque année à partir
    #: de celle du départ : ce qu'elle sert sur une année entière.
    niveaux: dict[int, float]
    #: Le premier mois servi, en date décimale : l'année du départ et ses mois
    #: écoulés, ``(mois − 1) / 12``.
    debut: float
    #: L'âge à ce premier mois.
    age: float
    sexe: str
    #: Le dernier revenu d'activité annualisé, en euros de l'année du départ :
    #: le dénominateur du taux de remplacement, et celui du patrimoine.
    dernier_revenu: float
    #: Les mêmes revenus et le même dernier revenu, nets (:func:`revenus_nets`),
    #: que les indicateurs nets opposent à la pension nette ; ``None`` quand
    #: le flux ne les porte pas, ou qu'un statut de la carrière n'a pas de
    #: fiche de paie.
    revenus_nets: dict[int, float] | None = None
    dernier_revenu_net: float | None = None

    @property
    def naissance(self) -> float:
        """L'origine des âges, en date décimale."""
        return self.debut - self.age

    @property
    def annee_liquidation(self) -> int:
        return int(math.floor(self.debut + 1e-9))

    @property
    def duree_carriere(self) -> int:
        """Les années de carrière : celles qui portent un revenu d'activité,
        comme TRAJECTOiRE les compte (``dureeCarriere``)."""
        return somme_ordonnee(1 for revenu in self.revenus.values() if revenu > 0)


@dataclass(frozen=True)
class Indicateurs:
    """Les indicateurs de cycle de vie d'une carrière, sous un système."""

    scenario: str
    #: Les années de retraite, espérées sous la survie de génération, fixées
    #: sous un âge de décès, à compter du premier mois servi.
    duree_retraite: float
    #: La même, rapportée à la vie entière : durée / (âge au départ + durée).
    part_de_vie: float
    duree_carriere: int
    #: Pensions sur cotisations, chacune rapportée au salaire moyen de son
    #: année ; ``None`` sans cotisation.
    taux_recuperation: float | None
    #: Pensions sur revenus d'activité, même unité ; nettes sur nets sous une
    #: convention nette.
    taux_annuite: float | None
    #: Pension moyenne d'une année de retraite sur revenu moyen d'une année de
    #: carrière, même unité et même règle.
    taux_remplacement_cycle: float | None
    #: Le rendement interne des flux déflatés des prix, et celui des flux
    #: rapportés au salaire moyen ; ``None`` quand aucun taux ne les égalise.
    rendement_reel: float | None
    rendement_smpt: float | None
    #: La valeur au départ des pensions espérées, actualisées au taux réel de
    #: la convention, en années de dernier revenu.
    patrimoine: float | None
    #: Le patrimoine moins la valeur au départ des cotisations, capitalisées
    #: au même taux : la valeur actuelle nette d'être couvert (PROST, de la
    #: Banque mondiale), en années de dernier revenu.
    valeur_nette: float | None = None
    #: La pension de la dernière année de la retraite — espérée, ou fixée par
    #: l'âge de décès —, rapportée au dernier revenu mené jusqu'à elle par le
    #: salaire moyen : ce qu'une pension perd sur les salaires en une retraite
    #: (PROST, « replacement rate at death ») ; nette sur net sous une
    #: convention nette.
    remplacement_au_deces: float | None = None

    @property
    def duree_relative(self) -> float | None:
        """La durée de retraite rapportée à la durée de carrière."""
        if self.duree_carriere <= 0:
            return None
        return self.duree_retraite / self.duree_carriere

    def dictionnaire(self) -> dict:
        return {
            "duree_retraite": self.duree_retraite,
            "part_de_vie": self.part_de_vie,
            "duree_carriere": self.duree_carriere,
            "duree_relative": self.duree_relative,
            "taux_recuperation": self.taux_recuperation,
            "taux_annuite": self.taux_annuite,
            "taux_remplacement_cycle": self.taux_remplacement_cycle,
            "rendement_reel": self.rendement_reel,
            "rendement_smpt": self.rendement_smpt,
            "patrimoine": self.patrimoine,
            "valeur_nette": self.valeur_nette,
            "remplacement_au_deces": self.remplacement_au_deces,
        }


# -- les flux ----------------------------------------------------------------


def _par_annee(couples) -> dict[int, float]:
    """Des montants datés, sommés par année : une année peut porter plusieurs
    lignes, un statut quitté et un autre pris."""
    sommes: dict[int, float] = {}
    for annee, montant in couples:
        if montant:
            sommes[annee] = sommes.get(annee, 0.0) + montant
    return sommes


def cotisations_versees(simulateur, carriere) -> dict[int, float]:
    """Ce que le droit en vigueur prélève sur ``carriere`` pour sa retraite,
    année par année et sans bascule : la cotisation salariale et la patronale,
    de l'État la part que ``Parametres.contribution_etat`` lui rattache, et les
    contributions d'équilibre de l'Agirc-Arrco.

    Le compte des scénarios 4 et 5, bâti sans le régime fusionné de la
    bascule : il porte, chaque année, les taux du droit en vigueur de chaque
    régime, part patronale comprise. Pour l'État, qui ne cotise pas mais
    équilibre, le défaut est la part de son taux que la Cour des comptes
    rattache à la retraite de l'agent lui-même — 44,1 % du traitement d'un
    civil en 2025 sur 78,28 % versés (``ContributionEtat.RETRAITE_SEULE``) :
    le reste paie l'invalidité, les majorations pour enfants, les départs
    anticipés et la démographie du régime, ce que le COR retire aussi de son
    rendement interne en n'y comptant que les cotisations, « sans les autres
    ressources telles que les impôts et taxes affectés et les transferts ».
    Le COR et TRAJECTOiRE ne comptent, pour l'État, que la retenue de l'agent ;
    la recette de la page Coût, le taux entier (``cout.TAUX_REELS``). Ce que
    les régimes provisionnés encaissent n'y est pas.

    Le compte ne porte pas les contributions d'équilibre de l'Agirc-Arrco,
    qui n'achètent aucun point et ne sont pas des cotisations (décision du
    2 octobre 2026) ; la paie du salarié du privé les supporte pour la
    retraite complémentaire, et TRAJECTOiRE comme le COR les comptent : elles
    s'ajoutent ici à ce que le compte prélève
    (:func:`~retraite_notionnelle.contributions_equilibre.contributions_d_une_carriere`)."""
    compte = simulateur.constructeur_employeur.construire(
        carriere,
        annee_liquidation=carriere.annee_liquidation,
        annee_debut=carriere.premiere_annee,
    )
    return _par_annee([(ligne.annee, ligne.cotisation) for ligne in compte.cotisations]
                      + sorted(contributions_d_une_carriere(simulateur, carriere).items()))


def cotisations_reformees(simulateur, comparaison) -> dict[int, float]:
    """Ce que versent les scénarios 2 à 5 : ce que prélève le compte du
    scénario 4, part patronale comprise — les taux du droit en vigueur
    jusqu'à la bascule, ceux de :func:`cotisations_versees`, puis le taux du
    régime fusionné, celui du statut pivot, que la réforme prélève pour tous.
    Un agent de l'État n'y verse plus, après la bascule, que ce taux-là : la
    contribution d'équilibre de l'État ne finance plus ses droits. Les
    contributions d'équilibre de l'Agirc-Arrco s'y ajoutent jusqu'à la
    bascule, où la paie les supportait ; après elle, le régime fusionné
    remplace la complémentaire, et son taux les omet, comme celui du
    scénario 6."""
    compte = comparaison.notionnel_retroactif_employeur.compte
    bascule = simulateur.parametres.annee_bascule
    equilibre = contributions_d_une_carriere(simulateur, comparaison.carriere)
    return _par_annee([(ligne.annee, ligne.cotisation) for ligne in compte.cotisations]
                      + [(annee, montant) for annee, montant in sorted(equilibre.items())
                         if annee < bascule])


def cotisations_liberales(simulateur, versees: dict[int, float],
                          liberal) -> dict[int, float]:
    """Ce que le scénario 6 fait verser : le droit en vigueur avant la
    bascule, son compte ensuite — le taux unique, sur la carrière que l'âge
    légal de 65 ans a peut-être prolongée —, et les deux parts de son pilier,
    dont il sert la rente."""
    bascule = simulateur.parametres.annee_bascule
    couples = [(annee, montant) for annee, montant in versees.items() if annee < bascule]
    couples += [(ligne.annee, ligne.cotisation) for ligne in liberal.compte.cotisations
                if ligne.annee >= bascule]
    pilier = liberal.capitalisation
    if pilier is not None and pilier.actif:
        couples += [(annee.annee, annee.versement_brut) for annee in pilier.annees]
    return _par_annee(couples)


def revenus_d_activite(carriere) -> dict[int, float]:
    """Les revenus d'activité des années cotisées, en euros courants."""
    return _par_annee((ligne.annee, ligne.revenu) for ligne in carriere.lignes
                      if ligne.cotise)


def revenus_nets(simulateur, carriere, proposition: bool = False) -> dict[int, float] | None:
    """Ce que la paie laisse de chaque revenu d'activité, année par année,
    aux prélèvements de son année : la fiche de paie du droit en vigueur
    (:func:`~retraite_notionnelle.remuneration.fiche_depuis_brut`), qui
    retient les cotisations retraite de l'année et les autres prélèvements de
    l'année courante, ramenée à ceux de l'année par l'histoire que l'IPP
    retrace (:meth:`~.donnees.prelevements_historiques.PrelevementsHistoriques.hors_retraite`)
    — la CSG et la CRDS depuis 1991 et 1996, la maladie, le veuvage,
    l'assurance chômage du salarié du privé, la maladie et la contribution de
    solidarité de l'agent public — et par les contributions d'équilibre de
    l'Agirc-Arrco de l'année, l'ASF, l'AGFF ou la CEG, au lieu de celles de
    l'année courante. L'indépendant garde les prélèvements hors retraite de
    l'année courante. La fiche se lit sur le revenu annualisé, sous le plafond
    de l'année entière, puis se ramène aux mois travaillés.

    Les primes d'un fonctionnaire perdent les prélèvements hors retraite,
    sans la retenue pour pension, que la loi n'assied que sur le traitement
    (:func:`~retraite_notionnelle.remuneration.bloc_droit_en_vigueur`). La
    RAFP qu'elles paient reste hors du net, comme elle est hors des deux flux.

    Avec ``proposition``, les années de la bascule au départ se lisent sur la
    fiche de paie de la proposition (:func:`~.remuneration.remuneration_de_la_carriere`),
    qui laisse un net plus fort du même brut : son rapport du net au brut,
    appliqué au revenu de l'année, comme le site le fait pour le taux de
    remplacement net du scénario 6 (``contexte.Montants``). Les scénarios 2 à 5
    gardent la fiche du droit en vigueur, comme le site. ``None`` quand un
    statut de la carrière n'a pas de fiche de paie — l'exploitant agricole —,
    dont le net ne se calcule pas."""
    couples = []
    for ligne in carriere.lignes:
        if not ligne.cotise:
            continue
        net = _net_annualise(simulateur, carriere, ligne)
        if net is None:
            return None
        couples.append((ligne.annee, net * ligne.fraction_annee))
    nets = _par_annee(couples)
    if proposition:
        remuneration = remuneration_de_la_carriere(
            carriere, simulateur.macro, simulateur.catalogue, simulateur.affiliations,
            simulateur.parametres)
        bruts = revenus_d_activite(carriere)
        for annee in () if remuneration is None else remuneration.annees:
            fiche = annee.proposition
            if fiche.brut > 0.0 and annee.annee in bruts:
                nets[annee.annee] = bruts[annee.annee] * fiche.net / fiche.brut
    return nets


#: Les postes de la fiche de paie que les contributions d'équilibre de l'année
#: remplacent : la CEG et la CET, que la fiche prélève aux taux de l'année
#: courante.
POSTES_EQUILIBRE = ("equilibre_general", "equilibre_technique")


def _net_annualise(simulateur, carriere, ligne) -> float | None:
    """Le net du revenu annualisé d'une ligne cotisée, primes comprises, aux
    prélèvements de son année (:func:`revenus_nets`)."""
    racine = simulateur.parametres.racine_donnees
    macro = simulateur.macro
    annualise = ligne.revenu_annualise
    fiche = fiche_depuis_brut(racine, macro, simulateur.catalogue, simulateur.affiliations,
                              ligne.affiliation, ligne.annee, annualise, ligne.part_primes)
    if fiche is None:
        return None
    profil = profil_de_la_fiche(simulateur.affiliations, simulateur.catalogue,
                                ligne.affiliation, ligne.annee)
    famille = FAMILLES.get(profil)
    if famille is None:
        return fiche.net
    historique = charger_prelevements_historiques(racine)
    plafond = macro.plafond_securite_sociale(ligne.annee)
    courante = charger_prelevements(racine).annee
    retraite = fiche.retraite_salarie
    hors_retraite = (historique.hors_retraite_annuel(famille, courante, annualise, plafond, retraite)
                     - historique.hors_retraite_annuel(famille, ligne.annee, annualise, plafond,
                                                       retraite))
    equilibre = somme_ordonnee(l.salarie for l in fiche.lignes if l.code in POSTES_EQUILIBRE)
    if equilibre > 0.0:
        equilibre -= part_salariale_annualisee(simulateur, carriere, ligne)
    return fiche.net + hors_retraite + equilibre


def _dernier_revenu_net(dernier_revenu: float, revenus: dict[int, float],
                        nets: dict[int, float] | None) -> float | None:
    """Le dernier revenu annualisé, net : le rapport du net au brut de la
    dernière année cotisée, celle que le simulateur annualise."""
    if nets is None or not revenus:
        return None
    annee = max(revenus)
    return dernier_revenu * nets.get(annee, 0.0) / revenus[annee]


def _debut(carriere) -> float:
    return carriere.annee_liquidation + carriere.fraction_annee_liquidation


def _derniere_annee(carriere) -> int:
    """La dernière année qu'une pension peut atteindre : l'âge terminal de la
    table de mortalité."""
    return int(math.floor(_debut(carriere) - carriere.age_liquidation + AGE_TERMINAL)) + 1


@lru_cache(maxsize=8)
def _revalorisation(simulateur, derniere_annee: int) -> RevalorisationServie:
    """La règle des pensions notionnelles servies, jusqu'à ``derniere_annee`` :
    celle du simulateur s'arrête à l'année courante, la page Coût bâtit la
    sienne jusqu'à son horizon, et une retraite va plus loin."""
    return RevalorisationServie(simulateur, simulateur.parametres.annee_debut_repartition,
                                derniere_annee)


def _hors_repartition(simulateur, regime: str) -> bool:
    return (simulateur.parametres.isoler_capitalisation
            and simulateur.catalogue[regime].hors_repartition)


def _servie(vivante) -> float:
    """La répartition d'une pension menée à une échéance, majoration pour
    enfants comprise : ce que :func:`faire_vivre` rend, sans le RAFP."""
    return (somme_ordonnee(r.aujourd_hui for r in vivante.regimes if not r.hors_repartition)
            + vivante.majoration_enfants * vivante.coefficient_majoration)


def _au_depart(simulateur, resultat) -> float:
    """La répartition du scénario 1 au départ, sans l'ASPA."""
    regimes = somme_ordonnee(p.montant for p in resultat.pensions_par_regime
                             if not _hors_repartition(simulateur, p.regime))
    majoration = somme_ordonnee(a.montant for a in resultat.avantages_appliques
                                if a.code == "majoration_enfants")
    return regimes + majoration


def _parts_convenues(simulateur, resultat, revalorisation) -> dict[str, float]:
    """La part de la pension du scénario 1 que sert, au bout de ses fusions,
    un régime à valeur de service convenue (:func:`~.cout.parts_convenues`),
    rapportée à la répartition sans l'ASPA, comme les niveaux qu'elle mène."""
    total = _au_depart(simulateur, resultat)
    parts: dict[str, float] = {}
    if total <= 0.0:
        return parts
    for pension in resultat.pensions_par_regime:
        convenu = revalorisation.regime_convenu(pension.regime)
        if convenu is not None and pension.montant > 0.0:
            parts[convenu] = parts.get(convenu, 0.0) + pension.montant / total
    return parts


def niveaux_actuels(simulateur, comparaison, revalorisation,
                    derniere_annee: int) -> dict[int, float]:
    """Le niveau annuel de la pension du scénario 1, de l'année du départ à
    ``derniere_annee``, en euros courants.

    Ce que le droit a servi jusqu'à l'année courante, régime par régime
    (:func:`faire_vivre`) ; au-delà, ou pour un départ à venir, la convention
    de projection de la page Coût : les prix, et la valeur de service que le
    COR projette pour l'Agirc-Arrco (:func:`~.cout.coefficient_actuel`).
    """
    carriere = comparaison.carriere
    resultat = comparaison.actuel
    macro = simulateur.macro
    liquidation = carriere.annee_liquidation
    courante = simulateur.parametres.annee_courante
    niveaux: dict[int, float] = {}
    if liquidation <= courante:
        for annee in range(liquidation, courante + 1):
            niveaux[annee] = _servie(faire_vivre(simulateur, carriere, resultat, annee))
        ancre = courante
    else:
        niveaux[liquidation] = _au_depart(simulateur, resultat)
        ancre = liquidation
    depart = niveaux[ancre]
    parts = _parts_convenues(simulateur, resultat, revalorisation)
    for annee in range(ancre + 1, derniere_annee + 1):
        niveaux[annee] = (depart * macro.coefficient_prix(ancre, annee)
                          * coefficient_actuel(parts, revalorisation, ancre, annee))
    return niveaux


def _pension_contributive(calcul, resultat) -> float:
    """La pension de répartition qu'un système notionnel sert au départ, sans
    la garantie vieillesse du scénario 6, que l'impôt finance."""
    garantie = resultat.garantie_vieillesse
    if calcul.garantie and garantie is not None:
        return garantie.pension_contributive
    return resultat.pension_annuelle


def niveaux_notionnels(simulateur, comparaison, scenario: str, revalorisation,
                       actuels: dict[int, float], derniere_annee: int) -> dict[int, float]:
    """Le niveau annuel de la pension d'un système notionnel, en euros
    courants : sa règle d'indexation depuis le départ, et celle du stock à la
    bascule (:meth:`~.revalorisation.RevalorisationServie.coefficient_stock`).

    Une réforme prospective ne touche pas qui est parti avant elle : il garde
    la pension du scénario 1, revalorisée par le droit jusqu'à la bascule,
    puis selon ``revalorisation_stock``. Le scénario 6 sert sa part
    contributive — la garantie vieillesse, que l'impôt finance, n'y est pas —
    et la rente de son pilier, nominale et constante.
    """
    parametres = simulateur.parametres
    calcul = simulateur.calculs[scenario]
    macro = simulateur.macro
    resultat = getattr(comparaison, scenario)
    liquidation = comparaison.carriere_de(scenario).annee_liquidation
    bascule = parametres.annee_bascule
    if calcul.prospectif and liquidation <= bascule:
        niveaux = {annee: niveau for annee, niveau in actuels.items() if annee <= bascule}
        base = actuels[bascule]
        reindexe = parametres.revalorisation_stock is RevalorisationStock.REINDEXE
        for annee in range(bascule + 1, derniere_annee + 1):
            reel = revalorisation.coefficient(bascule, annee) if reindexe else 1.0
            niveaux[annee] = base * macro.coefficient_prix(bascule, annee) * reel
        return niveaux
    pension = _pension_contributive(calcul, resultat)
    rente = resultat.rente_capitalisation_obligatoire
    return {
        annee: (pension * macro.coefficient_prix(liquidation, annee)
                * revalorisation.coefficient_stock(liquidation, annee, calcul.prospectif)
                + rente)
        for annee in range(liquidation, derniere_annee + 1)
    }


def flux_des_systemes(simulateur, comparaison, nets: bool = False) -> dict[str, Flux]:
    """Les deux flux d'une carrière sous chacun des six systèmes ; avec
    ``nets``, leurs revenus nets aussi (:func:`revenus_nets`), qu'une fiche
    de paie par année coûte."""
    carriere = comparaison.carriere
    derniere = max(_derniere_annee(comparaison.carriere_de(scenario))
                   for scenario in SCENARIOS)
    revalorisation = _revalorisation(simulateur, derniere)
    versees = cotisations_versees(simulateur, carriere)
    actuels = niveaux_actuels(simulateur, comparaison, revalorisation, derniere)
    # Les revenus de chaque carrière, et leur net : sur la fiche du droit en
    # vigueur, ou sur celle de la proposition pour le scénario 6.
    revenus = {}
    for scenario in SCENARIOS:
        cle = (id(comparaison.carriere_de(scenario)), simulateur.calculs[scenario].garantie
               if scenario in simulateur.calculs else False)
        if cle not in revenus:
            carriere_du_scenario = comparaison.carriere_de(scenario)
            revenus[cle] = (revenus_d_activite(carriere_du_scenario),
                            revenus_nets(simulateur, carriere_du_scenario, cle[1])
                            if nets else None)

    def flux(scenario: str, cotisations: dict[int, float],
             niveaux: dict[int, float]) -> Flux:
        carriere_du_scenario = comparaison.carriere_de(scenario)
        bruts, nets_du_scenario = revenus[(id(carriere_du_scenario),
                                           simulateur.calculs[scenario].garantie
                                           if scenario in simulateur.calculs else False)]
        dernier = (comparaison.dernier_revenu_annualise_liberal
                   if carriere_du_scenario is not carriere
                   else comparaison.dernier_revenu_annualise)
        return Flux(
            scenario=scenario, cotisations=cotisations, revenus=bruts, niveaux=niveaux,
            debut=_debut(carriere_du_scenario), age=carriere_du_scenario.age_liquidation,
            sexe=carriere_du_scenario.sexe, dernier_revenu=dernier,
            revenus_nets=nets_du_scenario,
            dernier_revenu_net=_dernier_revenu_net(dernier, bruts, nets_du_scenario),
        )

    systemes = {"actuel": flux("actuel", versees, actuels)}
    reformees = cotisations_reformees(simulateur, comparaison)
    for scenario in SCENARIOS[1:]:
        cotisations = reformees
        if simulateur.calculs[scenario].garantie:
            cotisations = cotisations_liberales(simulateur, versees,
                                                getattr(comparaison, scenario))
        systemes[scenario] = flux(scenario, cotisations, niveaux_notionnels(
            simulateur, comparaison, scenario, revalorisation, actuels, derniere))
    return systemes


# -- la fin de la retraite ---------------------------------------------------


def _integrale_survie(courbe: tuple[float, ...], debut: float, fin: float) -> float:
    """∫ S(x) dx de ``debut`` à ``fin`` années après le départ, la force de
    mortalité constante entre deux anniversaires du départ — l'hypothèse de
    :meth:`~retraite_notionnelle.donnees.mortalite.DonneesMortalite.survie_annuelle`,
    qui rend S exponentielle par morceaux."""
    total = 0.0
    x = debut
    while x < fin - 1e-12:
        rang = int(math.floor(x + 1e-12))
        borne = min(fin, rang + 1)
        if rang + 1 >= len(courbe):
            break
        haut, bas = courbe[rang], courbe[rang + 1]
        if haut <= 0.0:
            break
        u0, u1 = x - rang, borne - rang
        if bas <= 0.0:
            # La dernière cellule s'éteint : la survie y décroît linéairement.
            total += haut * ((u1 - u0) - (u1 * u1 - u0 * u0) / 2.0)
        elif abs(bas - haut) <= 1e-15 * haut:
            total += haut * (u1 - u0)
        else:
            logarithme = math.log(bas / haut)
            total += haut * (math.exp(logarithme * u1) - math.exp(logarithme * u0)) / logarithme
        x = borne
    return total


def pensions_esperees(flux: Flux, simulateur, convention: Convention
                      ) -> list[tuple[int, float, float, float]]:
    """Chaque année servie : (année, pension espérée en euros courants, instant
    moyen en date décimale, années de vie espérées dans l'année).

    Sous un âge de décès fixe, la pension court du premier mois servi au
    décès. Sous la survie de génération, chaque morceau d'année compte pour
    l'espérance de le vivre, sachant qu'on était en vie au départ.
    """
    esperees = []
    if convention.age_deces is not None:
        deces = flux.naissance + convention.age_deces
        for annee, niveau in sorted(flux.niveaux.items()):
            debut, fin = max(annee, flux.debut), min(annee + 1, deces)
            if fin > debut:
                esperees.append((annee, niveau * (fin - debut) * convention.retenu(annee),
                                 (debut + fin) / 2.0, fin - debut))
        return esperees
    courbe = simulateur.mortalite.courbe(flux.age, flux.debut,
                                         None if convention.unisexe else flux.sexe)
    for annee, niveau in sorted(flux.niveaux.items()):
        debut, fin = max(annee, flux.debut), annee + 1
        if fin <= debut:
            continue
        vie = _integrale_survie(courbe, debut - flux.debut, fin - flux.debut)
        if vie > 0.0:
            esperees.append((annee, niveau * vie * convention.retenu(annee),
                             (debut + fin) / 2.0, vie))
    return esperees


def age_de_deces_cor(mortalite, generation: int) -> float:
    """L'âge de décès des cas types du COR : « 60 + l'espérance de vie à 60
    ans de la génération » (annexe méthodologique en ligne du rapport de juin
    2026, § 2.3 b), les deux sexes réunis — ses cas types n'en ont pas. Celle
    du dépôt, en table de génération : la moyenne des deux espérances, puisque
    la table unisexe moyenne les deux survies."""
    return 60.0 + mortalite.esperance_residuelle(60.0, generation + 60.0, None)


def convention_cor(simulateur, comparaison) -> Convention:
    """Les conventions du rendement interne des cas types du COR : les deux
    sexes réunis, le décès à 60 ans plus l'espérance de vie à 60 ans de la
    génération, la pension nette — « les cas types de cadre et de non-cadre
    sont soumis au taux plein de la CSG » (rapport annuel de juin 2026, figure
    3.A, note), ce que :func:`taux_de_prelevement` retient pour tous, chaque
    année au taux de son année (:func:`prelevements_par_annee`)."""
    return Convention(
        age_deces=age_de_deces_cor(simulateur.mortalite,
                                   comparaison.carriere.annee_naissance),
        unisexe=True,
        prelevement=taux_de_prelevement(simulateur, comparaison.actuel),
        prelevements=prelevements_par_annee(simulateur, comparaison),
    )


def _parts_assujetties(simulateur, resultat) -> tuple[float, float]:
    """Les parts de la pension du scénario 1 au départ que servent le régime
    général et les complémentaires (``regimes_maladie``) : celles qui ont payé
    une cotisation maladie, la première jusqu'en 1997, la seconde toujours."""
    prelevements = charger_prelevements(simulateur.parametres.racine_donnees).pensions
    total = _au_depart(simulateur, resultat)
    if total <= 0.0:
        return 0.0, 1.0
    general = somme_ordonnee(p.montant for p in resultat.pensions_par_regime
                             if p.regime in prelevements.regimes_generaux)
    complementaire = somme_ordonnee(p.montant for p in resultat.pensions_par_regime
                                    if p.regime in prelevements.regimes_maladie)
    return general / total, complementaire / total


def prelevements_par_annee(simulateur, comparaison) -> dict[int, float]:
    """Ce que les prélèvements de chaque année retirent aux pensions de
    ``comparaison``, du premier départ de ses systèmes à la dernière année
    qu'une pension peut atteindre, au taux plein de CSG : l'histoire que
    l'IPP retrace (:mod:`~retraite_notionnelle.donnees.prelevements_historiques`),
    dont la dernière marche tient au-delà. Aucun prélèvement avant le
    1er juillet 1980, où naît la cotisation maladie des pensions ; celle du
    régime général sur sa part de la pension, jusqu'en 1997, celle des
    complémentaires sur la leur. Les autres systèmes gardent les parts du
    scénario 1, comme ils gardent son taux de l'année courante."""
    historique = charger_prelevements_historiques(simulateur.parametres.racine_donnees)
    general, complementaire = _parts_assujetties(simulateur, comparaison.actuel)
    carrieres = [comparaison.carriere_de(scenario) for scenario in SCENARIOS]
    premiere = min(carriere.annee_liquidation for carriere in carrieres)
    derniere = max(_derniere_annee(carriere) for carriere in carrieres)
    return {annee: historique.taux_pension_annuel(annee, general, complementaire)
            for annee in range(premiere, derniere + 1)}


def taux_de_prelevement(simulateur, resultat) -> float:
    """Ce que les prélèvements de l'année courante retirent à la pension du
    scénario 1 de ``resultat``, en part du brut : la CSG au taux plein, la
    CRDS et la CASA sur toute la pension, la cotisation maladie sur sa part
    complémentaire. Les autres systèmes gardent le taux de la même personne,
    comme le simulateur le fait (``contexte.Montants``)."""
    prelevements = charger_prelevements(simulateur.parametres.racine_donnees).pensions
    total = _au_depart(simulateur, resultat)
    if total <= 0.0:
        return prelevements.taux_total
    complementaire = somme_ordonnee(p.montant for p in resultat.pensions_par_regime
                                    if p.regime in prelevements.regimes_maladie)
    return prelevements.taux_total + prelevements.maladie_complementaire * complementaire / total


# -- les indicateurs ---------------------------------------------------------


def _indices(macro, premiere: int, derniere: int) -> tuple[dict[int, float], dict[int, float]]:
    """Les prix et le salaire moyen par tête de chaque année, en indices
    (un la première année) : ce par quoi un montant courant se déflate."""
    prix, salaires = {premiere: 1.0}, {premiere: 1.0}
    for annee in range(premiere + 1, derniere + 1):
        prix[annee] = prix[annee - 1] * (1.0 + macro.inflation(annee))
        salaires[annee] = salaires[annee - 1] * (1.0 + macro.salaire_moyen(annee))
    return prix, salaires


def rendement_interne(flux: list[tuple[float, float]]) -> float | None:
    """Le taux ``r`` qui annule ``Σ montant × (1 + r)^-(t − t₀)``, par
    dichotomie ; ``None`` quand aucun taux des bornes ne l'annule.

    Les cotisations, négatives, précèdent les pensions : la somme décroît
    avec le taux, de positive aux taux bas, où les pensions lointaines pèsent
    le plus, à négative aux taux hauts. Une seule racine, donc, et la
    dichotomie la trouve sans dérivée, comme celle du pilier
    (:func:`~.moteur.capitalisation._taux_interne`).
    """
    if not flux:
        return None
    origine = min(instant for instant, _ in flux)

    def valeur(taux: float) -> float:
        return somme_ordonnee(montant * (1.0 + taux) ** -(instant - origine)
                              for instant, montant in flux)

    bas, haut = BORNES_RENDEMENT
    if valeur(bas) <= 0.0 or valeur(haut) >= 0.0:
        return None
    for _ in range(200):
        milieu = 0.5 * (bas + haut)
        if valeur(milieu) > 0.0:
            bas = milieu
        else:
            haut = milieu
        if haut - bas < 1e-12:
            break
    return 0.5 * (bas + haut)


def _instant_cotisation(flux: Flux, annee: int) -> float:
    """Le milieu de la part cotisée d'une année : l'année entière, sauf celle
    du départ, cotisée jusqu'au premier mois servi."""
    if annee == flux.annee_liquidation:
        return annee + max(flux.debut - annee, 0.0) / 2.0
    return annee + 0.5


def indicateurs(flux: Flux, simulateur, convention: Convention = Convention()
                ) -> Indicateurs:
    """Les indicateurs de cycle de vie d'un système, sous ``convention``.

    Sous une convention nette, la pension est nette, et ce qui la rapporte à
    un revenu d'activité — le taux d'annuité, le remplacement sur le cycle de
    vie et au décès — la rapporte au revenu net (:attr:`Flux.revenus_nets`),
    ou ne se calcule pas sans lui. Le patrimoine reste en années de dernier
    revenu brut, comme l'OCDE exprime son patrimoine net ; les cotisations
    sont ce que la paie supporte, brutes par nature."""
    esperees = pensions_esperees(flux, simulateur, convention)
    duree = somme_ordonnee(vie for _, _, _, vie in esperees)
    annees = [annee for annee, _, _, _ in esperees] + list(flux.cotisations) + list(flux.revenus)
    premiere, derniere = min(annees), max(annees)
    prix, salaires = _indices(simulateur.macro, premiere, derniere)
    nette = convention.nette
    revenus = flux.revenus_nets if nette else flux.revenus
    dernier = flux.dernier_revenu_net if nette else flux.dernier_revenu

    pensions_smpt = somme_ordonnee(montant / salaires[annee] for annee, montant, _, _ in esperees)
    cotisations_smpt = somme_ordonnee(montant / salaires[annee]
                                      for annee, montant in flux.cotisations.items())
    revenus_smpt = (None if revenus is None else
                    somme_ordonnee(montant / salaires[annee] for annee, montant in revenus.items()))
    carriere = flux.duree_carriere

    def chronique(indice: dict[int, float]) -> list[tuple[float, float]]:
        versees = [(_instant_cotisation(flux, annee), -montant / indice[annee])
                   for annee, montant in flux.cotisations.items()]
        recues = [(instant, montant / indice[annee])
                  for annee, montant, instant, _ in esperees]
        return versees + recues

    patrimoine = valeur_nette = remplacement_au_deces = None
    if flux.dernier_revenu > 0.0:
        liquidation = flux.annee_liquidation
        actualisation = 1.0 + convention.taux_actualisation

        def au_depart(annee: int, montant: float, instant: float) -> float:
            """Un montant courant, en euros du départ, actualisé au départ —
            capitalisé jusqu'à lui s'il le précède."""
            return (montant * prix[liquidation] / prix[annee]
                    * actualisation ** -(instant - flux.debut))

        patrimoine = somme_ordonnee(au_depart(annee, montant, instant)
                                    for annee, montant, instant, _ in esperees)
        valeur_nette = patrimoine - somme_ordonnee(
            au_depart(annee, montant, _instant_cotisation(flux, annee))
            for annee, montant in flux.cotisations.items())
        patrimoine /= flux.dernier_revenu
        valeur_nette /= flux.dernier_revenu
        derniere_servie = int(math.floor(flux.debut + duree - 1e-9))
        if duree > 0.0 and derniere_servie in flux.niveaux and dernier:
            remplacement_au_deces = (
                flux.niveaux[derniere_servie] * convention.retenu(derniere_servie)
                / (dernier * salaires[derniere_servie] / salaires[liquidation]))

    return Indicateurs(
        scenario=flux.scenario,
        duree_retraite=duree,
        part_de_vie=duree / (flux.age + duree) if flux.age + duree > 0 else 0.0,
        duree_carriere=carriere,
        taux_recuperation=pensions_smpt / cotisations_smpt if cotisations_smpt > 0 else None,
        taux_annuite=pensions_smpt / revenus_smpt if revenus_smpt else None,
        taux_remplacement_cycle=(
            (pensions_smpt / duree) / (revenus_smpt / carriere)
            if duree > 0 and carriere > 0 and revenus_smpt else None),
        rendement_reel=rendement_interne(chronique(prix)) if flux.cotisations else None,
        rendement_smpt=rendement_interne(chronique(salaires)) if flux.cotisations else None,
        patrimoine=patrimoine,
        valeur_nette=valeur_nette,
        remplacement_au_deces=remplacement_au_deces,
    )


def indicateurs_des_systemes(simulateur, comparaison,
                             convention: Convention = Convention()
                             ) -> dict[str, Indicateurs]:
    """Les indicateurs d'une carrière sous chacun des six systèmes."""
    systemes = flux_des_systemes(simulateur, comparaison,
                                 nets=convention.nette)
    return {scenario: indicateurs(flux, simulateur, convention)
            for scenario, flux in systemes.items()}


def grille(simulateur, resultat, convention: Convention = Convention()
           ) -> dict[tuple[str, int], dict[str, Indicateurs]]:
    """Les indicateurs de la grille des cas types
    (:func:`~retraite_notionnelle.castypes.calculer_cas_types`), case par
    case et système par système."""
    return {cle: indicateurs_des_systemes(simulateur, comparaison, convention)
            for cle, comparaison in sorted(resultat.resultats.items())}


# -- à chaque âge de départ --------------------------------------------------


#: Le pas du balayage des âges de départ : le trimestre, que la décote et la
#: surcote comptent, et que TRAJECTOiRE balaie (``casTypesCOR.R``, au commit
#: ``0963b57``).
PAS_DES_AGES = 0.25


def hypotheses_de_productivite(racine_donnees) -> tuple[str, ...]:
    """Les scénarios de projection du COR, de la productivité la plus basse à
    la plus haute : 0,4, 0,7 et 1,0 % par an depuis son rapport de juin 2025,
    qui a retiré le 1,3 % que TRAJECTOiRE balaie encore. Les jeux de
    référence d'une autre institution, l'OCDE, n'en sont pas."""
    scenarios = charger_yaml(Path(racine_donnees) / "reference" / "macro"
                             / "hypotheses_projection.yaml").get("scenarios", {})
    return tuple(sorted(scenarios, key=lambda nom: float(scenarios[nom]["productivite_reelle"])))


def convention_nette(simulateur, comparaison, cor: bool = False) -> Convention:
    """La convention du balayage : celle du dépôt — la survie de génération
    du sexe de la carrière, le patrimoine à 1,5 % réel —, ou celle du COR
    (:func:`convention_cor`) ; la pension nette des prélèvements de l'année
    courante au taux plein dans les deux cas (:func:`taux_de_prelevement`),
    chaque année au taux de son année (:func:`prelevements_par_annee`)."""
    if cor:
        return convention_cor(simulateur, comparaison)
    return Convention(prelevement=taux_de_prelevement(simulateur, comparaison.actuel),
                      prelevements=prelevements_par_annee(simulateur, comparaison))


def minimum_vieillesse(simulateur, annee: int) -> float | None:
    """Le minimum vieillesse d'une personne seule l'année ``annee``, en euros
    par an : l'ASPA depuis 2007, menée sur les prix au-delà de son barème ;
    avant, ses deux étages, l'AVTS et l'allocation supplémentaire (action
    138, étape 6). ``None`` avant la loi du 14 mars 1941."""
    bareme = simulateur.scenario_actuel.minimum_vieillesse
    if annee <= bareme.DERNIERE_ANNEE_A_DEUX_ETAGES:
        etages = bareme.deux_etages(annee)
        return None if etages is None else etages.avts + etages.supplementaire
    plafond = bareme.plafond(annee)
    return None if plafond is None else plafond[0]


def pension_au_depart(simulateur, comparaison, scenario: str) -> float:
    """La pension brute du premier mois servi, annualisée, en euros de
    l'année du départ du système : celle dont partent les niveaux de
    :func:`niveaux_actuels` et de :func:`niveaux_notionnels`, sans l'ASPA ni
    la garantie vieillesse, rente du pilier comprise. Une réforme
    prospective sert à qui part avant elle la pension du scénario 1."""
    if scenario == "actuel":
        return _au_depart(simulateur, comparaison.actuel)
    calcul = simulateur.calculs[scenario]
    liquidation = comparaison.carriere_de(scenario).annee_liquidation
    if calcul.prospectif and liquidation <= simulateur.parametres.annee_bascule:
        return _au_depart(simulateur, comparaison.actuel)
    resultat = getattr(comparaison, scenario)
    return _pension_contributive(calcul, resultat) + resultat.rente_capitalisation_obligatoire


def derniere_annee_pleine(carriere) -> int | None:
    """La dernière année civile travaillée en entier avant celle du départ :
    TRAJECTOiRE y lit le dernier revenu de son taux de remplacement net, pour
    éviter les années incomplètes de la fin de carrière. ``None`` sans
    année pleine."""
    couverture: dict[int, float] = {}
    for ligne in carriere.lignes:
        if ligne.cotise and ligne.annee < carriere.annee_liquidation:
            couverture[ligne.annee] = couverture.get(ligne.annee, 0.0) + ligne.fraction_annee
    pleines = [annee for annee, part in couverture.items() if part >= 1.0 - 1e-9]
    return max(pleines) if pleines else None


@dataclass(frozen=True)
class RemplacementNet:
    """La pension nette du départ sur le revenu net de la dernière année
    pleine, chacun ramené à une même unité : TRAJECTOiRE publie les trois
    (``txRemplacementNetEuroCourant``, ``…EuroConstant``, ``…Smpt``). Elles ne
    diffèrent que de ce que les prix et le salaire moyen ont fait entre
    l'année du revenu et celle du départ."""

    #: Chacun en euros de son année.
    courants: float
    #: Chacun en euros constants.
    constants: float
    #: Chacun en salaire moyen par tête de son année : le taux de remplacement
    #: du simulateur, en net.
    salaire_moyen: float


def remplacement_net(simulateur, carriere, nets: dict[int, float] | None,
                     pension_nette: float) -> RemplacementNet | None:
    """Le taux de remplacement net au départ de ``carriere``, en trois unités ;
    ``None`` sans année pleine ou sans revenu net."""
    annee = derniere_annee_pleine(carriere)
    if annee is None or not nets or nets.get(annee, 0.0) <= 0.0:
        return None
    courants = pension_nette / nets[annee]
    liquidation = carriere.annee_liquidation
    macro = simulateur.macro
    return RemplacementNet(
        courants=courants,
        constants=courants / macro.coefficient_prix(annee, liquidation),
        salaire_moyen=courants / macro.coefficient_salaire_moyen(annee, liquidation),
    )


@dataclass(frozen=True)
class Depart:
    """Un âge du balayage, et ce qu'y donne chacun des six systèmes, en net."""

    age: float
    #: L'année du départ du scénario 1 ; celui du scénario 6 est plus tard
    #: quand son âge légal le reporte (``Comparaison.carriere_de``).
    annee: int
    #: Les indicateurs de chaque système, sous la convention nette.
    indicateurs: dict[str, Indicateurs]
    #: La pension nette du premier mois servi, annualisée, en euros de l'année
    #: du départ de chaque système.
    pensions_nettes: dict[str, float]
    #: La même, rapportée au minimum vieillesse d'une personne seule de cette
    #: année (:func:`minimum_vieillesse`) ; ``None`` sans barème.
    pensions_aspa: dict[str, float | None]
    #: Le taux de remplacement net au départ ; ``None`` sans revenu net.
    remplacements: dict[str, RemplacementNet | None]


def depart(simulateur, comparaison, cor: bool = False,
           age: float | None = None) -> Depart:
    """Ce que donne, en net, le départ de ``comparaison`` sous les six
    systèmes (:func:`convention_nette`)."""
    convention = convention_nette(simulateur, comparaison, cor)
    systemes = flux_des_systemes(simulateur, comparaison, nets=True)
    pensions, aspa, remplacements = {}, {}, {}
    for scenario, flux in systemes.items():
        carriere = comparaison.carriere_de(scenario)
        nette = (pension_au_depart(simulateur, comparaison, scenario)
                 * convention.retenu(carriere.annee_liquidation))
        minimum = minimum_vieillesse(simulateur, carriere.annee_liquidation)
        pensions[scenario] = nette
        aspa[scenario] = nette / minimum if minimum else None
        remplacements[scenario] = remplacement_net(simulateur, carriere, flux.revenus_nets,
                                                   nette)
    return Depart(
        age=comparaison.carriere.age_liquidation if age is None else age,
        annee=comparaison.carriere.annee_liquidation,
        indicateurs={scenario: indicateurs(flux, simulateur, convention)
                     for scenario, flux in systemes.items()},
        pensions_nettes=pensions, pensions_aspa=aspa, remplacements=remplacements,
    )


def ages_de_depart(simulateur, cas, generation: int,
                   pas: float = PAS_DES_AGES) -> tuple[float, ...]:
    """Les âges de départ du cas type ``cas`` né en ``generation``, de ``pas``
    en ``pas`` : de l'âge d'ouverture, carrière longue comprise, à l'âge
    d'annulation de la décote, les âges « au plus tôt » et « au taux plein
    automatique » de :func:`~retraite_notionnelle.pilote.ages_de_l_estimation`,
    chacun un point fixe sur la carrière que l'âge déplace. Le dernier est
    toujours l'âge d'annulation, même s'il n'est pas à un pas du précédent.
    Vide quand le droit n'oppose aucun âge à la carrière."""
    ages = pilote.ages_de_l_estimation(
        simulateur.scenario_actuel,
        lambda age: cas.carriere_a(simulateur, generation, age),
        cas.age_liquidation_pour(simulateur, generation))
    if ages is None:
        return ()
    debut, fin = float(ages["legal"]), float(ages["automatique"])
    nombre = int(math.floor((fin - debut) / pas + 1e-9))
    balayes = [round(debut + rang * pas, 9) for rang in range(nombre + 1)]
    if fin - balayes[-1] > 1e-9:
        balayes.append(fin)
    return tuple(balayes)


def balayage(simulateur, cas, generation: int, cor: bool = False,
             pas: float = PAS_DES_AGES) -> tuple[Depart, ...]:
    """Les indicateurs nets du cas type ``cas`` né en ``generation``, à
    chacun de ses âges de départ (:func:`ages_de_depart`), sous les
    hypothèses macroéconomiques de ``simulateur`` : une productivité, que
    :func:`hypotheses_de_productivite` énumère."""
    return tuple(
        depart(simulateur, simulateur.simuler(cas.carriere_a(simulateur, generation, age)),
               cor, age)
        for age in ages_de_depart(simulateur, cas, generation, pas))
