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

CE QUE LE MODULE NE FAIT PAS. Il ne connaît que les prélèvements de 2026 sur
les pensions : une pension « nette » l'est au taux plein de l'année courante,
tenu toute la retraite (:func:`taux_de_prelevement`) ; l'histoire de ces
prélèvements, que l'IPP publie, reste à reprendre. Il ne s'affiche pas encore
sur le site, et n'a pas de jumeau JavaScript, pas plus que
:mod:`~retraite_notionnelle.contributions_equilibre`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

from .config import RevalorisationStock
from .contributions_equilibre import contributions_d_une_carriere
from .cout import coefficient_actuel
from .donnees.mortalite import AGE_TERMINAL
from .remuneration import charger_prelevements
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
    #: Pensions sur revenus d'activité, même unité.
    taux_annuite: float | None
    #: Pension moyenne d'une année de retraite sur revenu moyen d'une année de
    #: carrière, même unité.
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
    #: (PROST, « replacement rate at death »).
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
    pension = resultat.pension_annuelle
    garantie = resultat.garantie_vieillesse
    if calcul.garantie and garantie is not None:
        pension = garantie.pension_contributive
    rente = resultat.rente_capitalisation_obligatoire
    return {
        annee: (pension * macro.coefficient_prix(liquidation, annee)
                * revalorisation.coefficient_stock(liquidation, annee, calcul.prospectif)
                + rente)
        for annee in range(liquidation, derniere_annee + 1)
    }


def flux_des_systemes(simulateur, comparaison) -> dict[str, Flux]:
    """Les deux flux d'une carrière sous chacun des six systèmes."""
    carriere = comparaison.carriere
    derniere = max(_derniere_annee(comparaison.carriere_de(scenario))
                   for scenario in SCENARIOS)
    revalorisation = _revalorisation(simulateur, derniere)
    versees = cotisations_versees(simulateur, carriere)
    actuels = niveaux_actuels(simulateur, comparaison, revalorisation, derniere)
    systemes = {
        "actuel": Flux(
            scenario="actuel", cotisations=versees,
            revenus=revenus_d_activite(carriere), niveaux=actuels,
            debut=_debut(carriere), age=carriere.age_liquidation, sexe=carriere.sexe,
            dernier_revenu=comparaison.dernier_revenu_annualise,
        ),
    }
    reformees = cotisations_reformees(simulateur, comparaison)
    for scenario in SCENARIOS[1:]:
        carriere_du_scenario = comparaison.carriere_de(scenario)
        reporte = carriere_du_scenario is not carriere
        cotisations = reformees
        if simulateur.calculs[scenario].garantie:
            cotisations = cotisations_liberales(simulateur, versees,
                                                getattr(comparaison, scenario))
        systemes[scenario] = Flux(
            scenario=scenario, cotisations=cotisations,
            revenus=revenus_d_activite(carriere_du_scenario),
            niveaux=niveaux_notionnels(simulateur, comparaison, scenario,
                                       revalorisation, actuels, derniere),
            debut=_debut(carriere_du_scenario),
            age=carriere_du_scenario.age_liquidation, sexe=carriere_du_scenario.sexe,
            dernier_revenu=(comparaison.dernier_revenu_annualise_liberal
                            if reporte else comparaison.dernier_revenu_annualise),
        )
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
    retenu = 1.0 - convention.prelevement
    esperees = []
    if convention.age_deces is not None:
        deces = flux.naissance + convention.age_deces
        for annee, niveau in sorted(flux.niveaux.items()):
            debut, fin = max(annee, flux.debut), min(annee + 1, deces)
            if fin > debut:
                esperees.append((annee, niveau * (fin - debut) * retenu,
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
            esperees.append((annee, niveau * vie * retenu, (debut + fin) / 2.0, vie))
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
    3.A, note), ce que :func:`taux_de_prelevement` retient pour tous."""
    return Convention(
        age_deces=age_de_deces_cor(simulateur.mortalite,
                                   comparaison.carriere.annee_naissance),
        unisexe=True,
        prelevement=taux_de_prelevement(simulateur, comparaison.actuel),
    )


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
    """Les indicateurs de cycle de vie d'un système, sous ``convention``."""
    esperees = pensions_esperees(flux, simulateur, convention)
    duree = somme_ordonnee(vie for _, _, _, vie in esperees)
    annees = [annee for annee, _, _, _ in esperees] + list(flux.cotisations) + list(flux.revenus)
    premiere, derniere = min(annees), max(annees)
    prix, salaires = _indices(simulateur.macro, premiere, derniere)

    pensions_smpt = somme_ordonnee(montant / salaires[annee] for annee, montant, _, _ in esperees)
    cotisations_smpt = somme_ordonnee(montant / salaires[annee]
                                      for annee, montant in flux.cotisations.items())
    revenus_smpt = somme_ordonnee(montant / salaires[annee]
                                  for annee, montant in flux.revenus.items())
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
        if duree > 0.0 and derniere_servie in flux.niveaux:
            remplacement_au_deces = (
                flux.niveaux[derniere_servie] * (1.0 - convention.prelevement)
                / (flux.dernier_revenu * salaires[derniere_servie] / salaires[liquidation]))

    return Indicateurs(
        scenario=flux.scenario,
        duree_retraite=duree,
        part_de_vie=duree / (flux.age + duree) if flux.age + duree > 0 else 0.0,
        duree_carriere=carriere,
        taux_recuperation=pensions_smpt / cotisations_smpt if cotisations_smpt > 0 else None,
        taux_annuite=pensions_smpt / revenus_smpt if revenus_smpt > 0 else None,
        taux_remplacement_cycle=(
            (pensions_smpt / duree) / (revenus_smpt / carriere)
            if duree > 0 and carriere > 0 and revenus_smpt > 0 else None),
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
    return {scenario: indicateurs(flux, simulateur, convention)
            for scenario, flux in flux_des_systemes(simulateur, comparaison).items()}


def grille(simulateur, resultat, convention: Convention = Convention()
           ) -> dict[tuple[str, int], dict[str, Indicateurs]]:
    """Les indicateurs de la grille des cas types
    (:func:`~retraite_notionnelle.castypes.calculer_cas_types`), case par
    case et système par système."""
    return {cle: indicateurs_des_systemes(simulateur, comparaison, convention)
            for cle, comparaison in sorted(resultat.resultats.items())}
