"""La dépense de retraite en ses quatre facteurs, à la manière de l'Ageing Report.

La Commission européenne et le Comité de politique économique (le groupe de
travail sur le vieillissement, l'AWG) décomposent la dépense de pensions de
chaque État en quatre facteurs (2024 Ageing Report, volume 1, encadré I.1.1 ;
fiche France, figure 4) :

    dépense / PIB = (65 ans et plus / 20-64 ans)                    la DÉPENDANCE
                  × (pensionnés / 65 ans et plus)                   la COUVERTURE
                  × (pension moyenne / PIB par heure travaillée)    la PRESTATION
                  × (20-64 ans / heures travaillées des 20-74 ans)  le MARCHÉ DU TRAVAIL

Le dépôt n'avait que deux de ces facteurs, les têtes et la pension relative
(:meth:`~.cout.Avenir.decomposition`), et supposait la couverture constante
(limite n° 2 de ``cout.py``). Ce module tire les quatre de la trajectoire que
``cout.py`` calcule, sans y toucher — il lit ses sorties —, et les chiffre
comme l'AWG, pour se confronter à la projection de la France que l'Ageing
Report de 2024 publie (``tests/temoins/ageing_report_france.json``,
``scripts/fetch/ageing_report.py`` ; action 138, étape 3 ; registre des
modèles, ``ageing_report``).

L'EFFET D'UN FACTEUR, COMME L'AWG LE CHIFFRE (:func:`effet`). Sur chaque pas
de la grille — 2022, 2025, puis de cinq ans en cinq ans jusqu'en 2070 —, la
dépense en part de PIB au début du pas, multipliée par la variation relative
du facteur sur le pas ; les pas s'additionnent, et le RÉSIDU est ce que la
somme des quatre effets laisse de la variation de la dépense. Ni la fiche ni le
volume 1 n'écrivent la formule : appliquée aux séries de leur annexe
statistique, elle redonne au dix-millième de point les effets publiés de la
dépendance, de la couverture, de la couverture des 65 ans et plus et du taux
d'emploi (``tests/test_facteurs_depense.py``). Une variation relative n'est pas
un logarithme : le résidu de l'AWG n'est pas nul même quand les quatre facteurs
font exactement la dépense ; il porte les produits croisés des variations,
négatifs quand la dépendance monte et que le reste baisse.

CE QUE LE DÉPÔT DÉCOMPOSE (:func:`annees_du_modele`). La trajectoire PROPRE du
modèle, ``AvenirAnnuel.base_modele`` — la masse de ses cas types mise à
l'échelle de la dernière année publiée, réversion portée à la part que le COR
projette —, et non la dépense que la page Coût affiche, observée par la DREES
jusqu'en 2024 puis projetée par le COR : celle-ci change de périmètre entre
les deux, et ses têtes ne sont pas celles du modèle. Chaque système en tire la
sienne par son rapport de masses (:func:`~.cout.masse_du_scenario`), comme la
page, garantie vieillesse à part.

* La DÉPENDANCE est celle des projections de population 2026 de l'INSEE, que
  la page lit déjà (``AvenirAnnuel.dependance``).
* La COUVERTURE rapporte aux 65 ans et plus les retraités du modèle
  (``AvenirAnnuel.tetes``) : les cohortes parvenues à l'âge de départ de leur
  cas type, pesées par les poids des cas types — des personnes, résidentes, de
  droit direct. L'AWG compte des pensionnés, résidents ou non, de droit direct,
  d'invalidité ou de réversion seule : les niveaux ne se comparent pas, les
  variations si.
* Le dépôt n'a pas d'heures : l'EMPLOI en tient lieu, un indice, un la
  première année, qui croît comme la masse salariale rapportée au salaire
  moyen par tête — l'emploi salarié des comptes nationaux sur les années
  publiées, la trajectoire d'emploi du COR ensuite. La PRESTATION et le MARCHÉ DU TRAVAIL
  n'ont donc pas de niveau qui se lise, seulement des variations, les seules
  que l'effet regarde. L'intensité du travail et l'allongement des carrières
  au-delà de 64 ans, que l'AWG sépare, sont nuls par construction.
* Dans la projection, le PIB croît comme la masse salariale — « partage de la
  valeur ajoutée stable » (``hypotheses_projection.yaml``) — : le PIB par
  emploi y suit le salaire moyen, et la prestation du système actuel y suit la
  pension moyenne relative du modèle (:meth:`~.cout.Avenir.decomposition`),
  réversion comprise.

LA COUVERTURE PARTAGÉE PAR ÂGE (:func:`retraites_par_age`,
:func:`partager_couverture`). Les retraités de 65 ans et plus et les plus
jeunes, comptés comme ``cout.py`` compte ses têtes, dont ce module refait le
geste sans y toucher : la couverture est leur somme rapportée aux 65 ans et
plus, et son effet se partage exactement entre les deux, pas à pas. L'annexe
de l'AWG publie ses pensionnés de 65 ans et plus : le même partage s'y fait,
et les deux se comparent terme à terme (action 138, étape 3, note « la
couverture de 2022-2030 »).

CE QUI MANQUE. Les têtes de la proposition : son âge légal de 65 ans reporte
des départs que ``AvenirAnnuel`` ne compte pas à part. La couverture de chaque
système est donc celle du droit en vigueur, et sa prestation porte ce que le
report change — à ``cout.py`` d'exposer ces têtes. Et le flux des pensions
nouvelles que l'AWG décompose à part (fiche France, tableau 14).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .cout import masse_du_scenario
from .somme import somme_ordonnee

#: Les années où l'AWG fait ses pas : la première de la projection, 2022,
#: puis 2025 et chaque cinquième année jusqu'à 2070.
GRILLE_AWG: tuple[int, ...] = (2022, *range(2025, 2071, 5))

#: Les quatre facteurs, dans l'ordre de l'équation : ce sont les propriétés de
#: :class:`AnneeDepense`.
FACTEURS: tuple[str, ...] = ("dependance", "couverture", "prestation", "marche_du_travail")

#: Les sous-périodes du tableau 9 de la fiche France.
PERIODES_AWG: tuple[tuple[int, int], ...] = (
    (2022, 2030), (2030, 2040), (2040, 2050), (2050, 2060), (2060, 2070), (2022, 2070),
)


def effet(part_pib: Mapping[int, float], facteur: Mapping[int, float],
          grille: Sequence[int] = GRILLE_AWG) -> dict[int, float]:
    """L'effet d'un facteur, cumulé depuis la première année de la grille,
    à chacune des suivantes, dans l'unité de ``part_pib``.

    Pas à pas : la part de PIB au début du pas, multipliée par la variation
    relative du facteur sur le pas. C'est la formule de l'AWG, retrouvée sur
    son annexe statistique (en-tête du module).
    """
    cumul = 0.0
    resultat: dict[int, float] = {}
    for debut, fin in zip(grille, grille[1:]):
        cumul += part_pib[debut] * (facteur[fin] / facteur[debut] - 1.0)
        resultat[fin] = cumul
    return resultat


@dataclass(frozen=True)
class AnneeDepense:
    """Une année de la dépense et ce qui la fait, en grandeurs brutes.

    Les quatre facteurs en sont les propriétés, et leur produit refait la part
    de PIB exactement : ``part_pib == dependance × couverture × prestation ×
    marche_du_travail × 100``.
    """

    annee: int
    #: La dépense de l'année, en millions d'euros courants.
    depense: float
    #: Le PIB de l'année, en millions d'euros courants.
    pib: float
    #: Les retraités, en personnes.
    retraites: float
    #: Les 65 ans et plus, puis les 20-64 ans, en personnes.
    population_65: float
    population_20_64: float
    #: L'emploi, en indice : seules ses variations se lisent.
    emploi: float

    @property
    def part_pib(self) -> float:
        """La dépense en pour cent du PIB, comme l'AWG l'écrit."""
        return 100.0 * self.depense / self.pib

    @property
    def dependance(self) -> float:
        return self.population_65 / self.population_20_64

    @property
    def couverture(self) -> float:
        return self.retraites / self.population_65

    @property
    def prestation(self) -> float:
        """La pension moyenne rapportée au PIB par emploi."""
        return (self.depense / self.retraites) / (self.pib / self.emploi)

    @property
    def marche_du_travail(self) -> float:
        return self.population_20_64 / self.emploi


@dataclass(frozen=True)
class Decomposition:
    """La variation de la dépense, en points de PIB, et ce que chaque facteur
    en fait, cumulés depuis la première année de la grille."""

    grille: tuple[int, ...]
    #: La part de PIB de chaque année de la grille.
    part_pib: dict[int, float]
    #: Sa variation depuis la première année, à chacune des suivantes.
    variation: dict[int, float]
    #: L'effet de chaque facteur, par année de la grille.
    effets: dict[str, dict[int, float]]
    #: Ce que les effets laissent de la variation.
    residu: dict[int, float]

    def entre(self, debut: int, fin: int) -> dict[str, float]:
        """La variation, chaque effet et le résidu de ``debut`` à ``fin``, deux
        années de la grille : les cumuls s'y retranchent, les pas étant
        additifs."""
        def cumul(serie: dict[int, float], annee: int) -> float:
            return 0.0 if annee == self.grille[0] else serie[annee]

        resultat = {"variation": cumul(self.variation, fin) - cumul(self.variation, debut)}
        for nom, serie in self.effets.items():
            resultat[nom] = cumul(serie, fin) - cumul(serie, debut)
        resultat["residu"] = cumul(self.residu, fin) - cumul(self.residu, debut)
        return resultat


def decomposer(annees: Mapping[int, AnneeDepense],
               grille: Sequence[int] = GRILLE_AWG) -> Decomposition:
    """La décomposition de l'AWG sur ces années, aux pas de ``grille``."""
    grille = tuple(grille)
    manquantes = [annee for annee in grille if annee not in annees]
    if manquantes:
        raise ValueError(f"années absentes de la trajectoire : {manquantes}")
    part_pib = {annee: annees[annee].part_pib for annee in grille}
    effets = {nom: effet(part_pib, {annee: getattr(annees[annee], nom) for annee in grille},
                         grille)
              for nom in FACTEURS}
    variation = {annee: part_pib[annee] - part_pib[grille[0]] for annee in grille[1:]}
    residu = {annee: variation[annee] - somme_ordonnee(effets[nom][annee] for nom in FACTEURS)
              for annee in grille[1:]}
    return Decomposition(grille=grille, part_pib=part_pib, variation=variation,
                         effets=effets, residu=residu)


def indice_emploi(macro, debut: int, fin: int) -> dict[int, float]:
    """L'emploi de ``debut`` à ``fin``, un la première année.

    Chaque année, la croissance de la masse salariale rapportée à celle du
    salaire moyen par tête : l'emploi salarié des comptes nationaux sur les
    années publiées ; ensuite, la trajectoire d'emploi des hypothèses, que les
    deux séries composent pareillement (``Macro._prolonger_avec_emploi``) —
    celle par laquelle le PIB de la page croît.
    """
    indice = {debut: 1.0}
    for annee in range(debut + 1, fin + 1):
        indice[annee] = (indice[annee - 1] * (1.0 + macro.masse_salariale(annee))
                         / (1.0 + macro.salaire_moyen(annee)))
    return indice


def annees_du_modele(avenir, population, macro,
                     scenario: str = "actuel") -> dict[int, AnneeDepense]:
    """Les grandeurs de chaque année de la trajectoire, pour un système.

    ``avenir`` est la trajectoire que rend ``calculer_cout`` (``Cout.avenir``),
    ``population`` et ``macro`` celles de son calcul. La dépense d'un système
    est la base du modèle, mise à sa mesure par son rapport de masses comme la
    page la met (:func:`~.cout.masse_du_scenario`) ; les retraités sont ceux du
    droit en vigueur pour tous les systèmes (en-tête du module).
    """
    lignes = [ligne for ligne in avenir.annees if ligne.tetes > 0.0 and ligne.pib > 0.0]
    if not lignes:
        return {}
    emploi = indice_emploi(macro, lignes[0].annee, lignes[-1].annee)
    resultat: dict[int, AnneeDepense] = {}
    for ligne in lignes:
        depense = masse_du_scenario(ligne.base_modele, ligne.part_derives,
                                    ligne.rapports[scenario], scenario,
                                    ligne.reversion_servie, ligne.reforme_en_vigueur)
        population_20_64 = population.actifs(ligne.annee)
        resultat[ligne.annee] = AnneeDepense(
            annee=ligne.annee,
            depense=depense / ligne.coefficient_constants,
            pib=ligne.pib,
            retraites=ligne.tetes,
            population_65=ligne.dependance * population_20_64,
            population_20_64=population_20_64,
            emploi=emploi[ligne.annee],
        )
    return resultat


#: L'âge où l'AWG range ses pensionnés parmi les « vieux » : celui de la
#: dépendance.
AGE_VIEILLESSE = 65


def partager_couverture(part_pib: Mapping[int, float], retraites: Mapping[int, float],
                        retraites_agees: Mapping[int, float],
                        population_65: Mapping[int, float],
                        grille: Sequence[int] = GRILLE_AWG) -> dict[str, dict[int, float]]:
    """L'effet de la couverture, partagé entre les retraités de 65 ans et plus
    (``vieillesse``) et les plus jeunes (``precoce``), cumulé comme
    :func:`effet`.

    La couverture est la somme de deux rapports aux 65 ans et plus, et sa
    variation relative sur un pas la somme de leurs variations rapportées à
    la couverture du début : les deux parts refont l'effet de la couverture
    exactement. Ce n'est pas le partage de l'AWG, dont les trois effets
    (couverture des 65 ans et plus, des plus jeunes rapportée aux 50-64 ans,
    effet de cohorte) ne s'ajoutent pas ; celui-ci se refait des deux côtés
    sur les mêmes séries.
    """
    def rapport(serie: Mapping[int, float], annee: int) -> float:
        return serie[annee] / population_65[annee]

    cumuls = {"vieillesse": 0.0, "precoce": 0.0}
    resultat: dict[str, dict[int, float]] = {nom: {} for nom in cumuls}
    for debut, fin in zip(grille, grille[1:]):
        couverture = rapport(retraites, debut)
        agees = rapport(retraites_agees, fin) - rapport(retraites_agees, debut)
        jeunes = ((rapport(retraites, fin) - rapport(retraites_agees, fin))
                  - (rapport(retraites, debut) - rapport(retraites_agees, debut)))
        cumuls["vieillesse"] += part_pib[debut] * agees / couverture
        cumuls["precoce"] += part_pib[debut] * jeunes / couverture
        for nom in cumuls:
            resultat[nom][fin] = cumuls[nom]
    return resultat


def au_perimetre(population_65: Mapping[int, float], agees: float, jeunes: float,
                 retraites: Mapping[int, float], retraites_agees: Mapping[int, float],
                 population_65_propre: Mapping[int, float],
                 grille: Sequence[int] = GRILLE_AWG,
                 stable: float = 0.0) -> tuple[dict[int, float], dict[int, float]]:
    """Les retraités d'une trajectoire, portés à un autre périmètre : les
    retraités de tous âges, puis ceux de 65 ans et plus, sur ``population_65``.

    La première année de la grille, les deux couvertures sont celles de
    l'autre périmètre (``agees`` et ``jeunes`` retraités par personne de 65
    ans et plus) ; ensuite, chacune suit la variation relative qu'elle a dans
    la trajectoire (``retraites``, ``retraites_agees``, sur
    ``population_65_propre``). Ce qui sépare l'effet de couverture ainsi porté
    de celui de l'autre périmètre est la dynamique ; ce qui le sépare de
    celui de la trajectoire, le niveau.

    ``stable`` est la part des plus jeunes de l'autre périmètre qui ne suit
    pas la trajectoire, et garde son rapport aux 65 ans et plus : des
    pensionnés que la trajectoire n'a pas — l'invalidité, que l'AWG compte
    et que l'âge légal ne fait pas reculer.
    """
    premiere = grille[0]

    def couverture(serie: Mapping[int, float], annee: int) -> float:
        return serie[annee] / population_65_propre[annee]

    def jeunes_de(annee: int) -> float:
        return couverture(retraites, annee) - couverture(retraites_agees, annee)

    portes_agees = {annee: population_65[annee] * agees * couverture(retraites_agees, annee)
                    / couverture(retraites_agees, premiere) for annee in grille}
    portes = {annee: portes_agees[annee]
              + population_65[annee] * jeunes
              * (stable + (1.0 - stable) * jeunes_de(annee) / jeunes_de(premiere))
              for annee in grille}
    return portes, portes_agees


class _Agee:
    """La population, sans ceux qui n'ont pas encore ``age_minimum`` ans :
    les têtes que ``cout._masses`` y compte sont celles de cet âge et plus."""

    def __init__(self, population, age_minimum: int) -> None:
        self._population = population
        self._age_minimum = age_minimum

    def effectif(self, age: int, annee: int) -> float:
        return self._population.effectif(age, annee) if age >= self._age_minimum else 0.0


def retraites_par_age(parametres, annees: Sequence[int],
                      age: int = AGE_VIEILLESSE) -> dict[int, tuple[float, float]]:
    """Chaque année, les retraités du modèle de tous âges, puis ceux d'``age``
    ans et plus, en personnes.

    Ce sont les têtes de ``calculer_cout`` (``AvenirAnnuel.tetes``), sous la
    démographie centrale et les réglages de la page : la même grille, que
    ``memoire.cout`` garde, les mêmes poids recalés sur les groupes du COR, la
    même somme (``cout._masses``), sur une population dont les moins
    d'``age`` ans sont ôtés. ``cout.py`` ne les expose pas par âge : ce geste
    le refait, et ``tests/test_facteurs_depense.py`` vérifie qu'il redonne ses
    têtes.
    """
    from . import cout as module
    from . import memoire
    from .castypes import GRILLE_DU_COUT
    from .donnees.equilibre import ComptesRetraite, variante_du_scenario
    from .donnees.population import Population
    from .revalorisation import RevalorisationServie
    from .simulateur import Simulateur

    racine = parametres.racine_donnees
    simulateur = Simulateur(parametres)
    grille = GRILLE_DU_COUT
    pensionnes, _ = memoire.memoriser_pour(
        parametres, ("grille_du_cout", parametres, grille, "droit"),
        lambda: module._pensionnes(simulateur, grille, "droit"))
    population = Population(racine, parametres.hypothese_esperance_vie)
    pensionnes = module._sous_la_demographie(simulateur, pensionnes, population)
    revalorisation = RevalorisationServie(
        simulateur.pour_la_projection(),
        min((p.annee_liquidation for p in pensionnes), default=module.HORIZON)
        - module._DEMI_TRANCHE,
        module.HORIZON,
    )
    variante = variante_du_scenario(parametres.scenario_projection,
                                    racine / "reference" / "macro")
    poids = module._poids_par_groupe(
        module._ponderation(simulateur, "effectifs", grille), pensionnes, population,
        revalorisation, ComptesRetraite(racine, variante=variante).decomposition)
    agee = _Agee(population, age)
    resultat: dict[int, tuple[float, float]] = {}
    for annee in annees:
        poids_annee = poids(annee)
        _, _, toutes = module._masses(pensionnes, population, annee, poids_annee,
                                      revalorisation)
        _, _, agees = module._masses(pensionnes, agee, annee, poids_annee, revalorisation)
        resultat[annee] = (toutes[module.TETES_TOUTES], agees[module.TETES_TOUTES])
    return resultat
