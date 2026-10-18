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

LA PART STABLE, MESURÉE (:func:`pensionnes_de_2022`, :func:`au_perimetre`).
L'AWG compte deux fois plus de pensionnés de moins de 65 ans que le modèle :
l'invalidité, que sa fiche France étend à l'AAH (§ 3.1), et la réversion
seule, que l'âge légal ne fait pas reculer. Le témoin de leurs sources
(``tests/temoins/pensionnes_de_2022.json``) les compte au 31 décembre 2022 :
avec les retraités d'Ancetre, ils refont ses pensionnés d'avant 60 ans à 2 %
près ; les rentiers d'accident du travail, qu'il ne compte pas, les
dépasseraient de 15 %. Ils gardent leur prévalence dans leur classe d'âge, non
leur rapport aux 65 ans et plus (note du 17 octobre 2026, « la part stable
mesurée »).

LA DATE DE CHAQUE COHORTE (:func:`depart_de_la_grille`). La grille ne
simule qu'une génération sur cinq, née en janvier, et faisait partir les cinq
cohortes qu'elle représente à son âge de départ. Sous la suspension de 2026,
celle de 1965 part avec 170 trimestres, quand celles de 1966 et 1967 en
doivent 172 : la grille les faisait partir un an trop tôt, et comptait trop
de retraités de moins de 65 ans en 2030 (note du 18 octobre 2026, « la
grille »). ``cout.py`` fait désormais partir chaque cohorte l'année que le
droit de sa génération lui donne (``cout.Pensionne.departs``), et les têtes
qu'on en refait la comptent de là (note du 18 octobre 2026, « la date de
chaque cohorte »).

CE QUI MANQUE. Les têtes de la proposition : son âge légal de 65 ans reporte
des départs que ``AvenirAnnuel`` ne compte pas à part. La couverture de chaque
système est donc celle du droit en vigueur, et sa prestation porte ce que le
report change — à ``cout.py`` d'exposer ces têtes. Et le flux des pensions
nouvelles que l'AWG décompose à part (fiche France, tableau 14).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from .cout import _DEMI_TRANCHE, masse_du_scenario
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
                 stable: float = 0.0,
                 population_stable: Mapping[int, float] | None = None,
                 ) -> tuple[dict[int, float], dict[int, float]]:
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
    pas la trajectoire : des pensionnés qu'elle n'a pas — l'invalidité, l'AAH,
    la réversion seule, que l'AWG compte et que l'âge légal ne fait pas
    reculer (:func:`pensionnes_de_2022`). Elle garde son rapport à
    ``population_stable`` : aux 65 ans et plus par défaut, elle n'a pas d'effet
    de couverture ; aux 20-64 ans, elle garde sa prévalence parmi eux, et
    recule, rapportée aux 65 ans et plus, quand ceux-ci croissent plus vite.
    """
    premiere = grille[0]
    if population_stable is None:
        population_stable = population_65

    def couverture(serie: Mapping[int, float], annee: int) -> float:
        return serie[annee] / population_65_propre[annee]

    def jeunes_de(annee: int) -> float:
        return couverture(retraites, annee) - couverture(retraites_agees, annee)

    def stables_de(annee: int) -> float:
        return (stable * population_stable[annee] / population_stable[premiere]
                / (population_65[annee] / population_65[premiere]))

    portes_agees = {annee: population_65[annee] * agees * couverture(retraites_agees, annee)
                    / couverture(retraites_agees, premiere) for annee in grille}
    portes = {annee: portes_agees[annee]
              + population_65[annee] * jeunes
              * (stables_de(annee) + (1.0 - stable) * jeunes_de(annee) / jeunes_de(premiere))
              for annee in grille}
    return portes, portes_agees


#: Les tranches d'âge du témoin des pensionnés de 2022 qui font les moins de
#: 65 ans, au 31 décembre ; la dernière du témoin, ``65_et_plus``, les autres.
JEUNES: tuple[str, ...] = ("moins_de_55", "55_59", "60_61", "62_64")

#: Ceux des pensionnés de l'AWG que le modèle n'a pas et que l'âge légal ne
#: fait pas reculer : l'invalidité et l'AAH, que la retraite relaie sans
#: rupture, et la réversion seule, qui n'en dépend pas.
STABLES: tuple[str, ...] = ("invalidite", "aah", "reversion_seule")


def pensionnes_de_2022(temoin: Mapping, rentes_at_mp: bool = False,
                       ) -> dict[str, dict[str, float]]:
    """Les pensionnés du 31 décembre 2022 au périmètre de l'AWG, par catégorie
    puis par tranche d'âge, en personnes, du témoin de leurs sources
    (``tests/temoins/pensionnes_de_2022.json``).

    Les retraités de droit direct et de réversion seule d'Ancetre, résidents
    en France ou non ; les pensionnés d'invalidité de chaque caisse de l'EACR ;
    les bénéficiaires de l'AAH de la CNAF, portés à la France entière, MSA
    comprise, par le total de la DREES, et avant 62 ans seulement : après, ils
    sont aussi retraités, et Ancetre les compte déjà. ``rentes_at_mp`` y ajoute
    les rentiers d'accident du travail de l'EACR, que l'AWG ne compte pas.
    """
    tranches = temoin["tranches"]

    def par_caisse(categorie: str) -> dict[str, float]:
        return {tranche: float(somme_ordonnee(caisse["tranches"][tranche]
                                              for caisse in temoin[categorie]["caisses"].values()))
                for tranche in tranches}

    aah = temoin["aah"]
    echelle = aah["total_france"] / aah["total"]
    avant_62_ans = JEUNES[:3]
    resultat = {
        "droit_direct": {t: float(temoin["droit_direct"]["tranches"][t]) for t in tranches},
        "reversion_seule": {t: float(temoin["reversion_seule"]["tranches"][t]) for t in tranches},
        "invalidite": par_caisse("invalidite"),
        "aah": {t: aah["tranches"][t] * echelle if t in avant_62_ans else 0.0 for t in tranches},
    }
    if rentes_at_mp:
        resultat["rentes_at_mp"] = par_caisse("rentes_at_mp")
    return resultat


def depart_de_la_grille(pensionne, decalage: int) -> int:
    """L'année où ``cout.py`` fait partir une cohorte de la grille : celle que
    le droit de sa génération lui donne (``cout.Pensionne.liquidation``)."""
    return pensionne.liquidation(decalage)


def compter_retraites(pensionnes, population, annee: int, poids_cas: Mapping[str, float],
                      depart: Callable[[object, int], int], age: int = 0,
                      survies: Mapping[tuple[str, int, int], float] | None = None) -> float:
    """Les retraités de l'année, en personnes : les cohortes de la grille
    parties au plus tard cette année-là, chacune l'année que ``depart`` lui
    donne, de la génération ``pensionne.generation + decalage``, pesées comme
    ``cout._masses`` pèse ses têtes — l'effectif de la classe d'âge, fois la
    survie propre du cas type, ``survies`` par ``(code, generation,
    decalage)`` (``cout._survies_alignees``, un par défaut), fois le poids du
    cas type. ``age`` ôte les plus jeunes."""
    survies = survies or {}
    total = 0.0
    for pensionne in pensionnes:
        part = poids_cas.get(pensionne.code, 0.0)
        if part <= 0.0:
            continue
        poids = 0.0
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            age_atteint = annee - pensionne.generation - decalage
            if age_atteint >= age and annee >= depart(pensionne, decalage):
                poids += population.effectif(age_atteint, annee) * survies.get(
                    (pensionne.code, pensionne.generation, decalage), 1.0)
        total += part * poids
    return total


def retraites_par_age(parametres, annees: Sequence[int],
                      age: int = AGE_VIEILLESSE) -> dict[int, tuple[float, float]]:
    """Chaque année, les retraités du modèle de tous âges, puis ceux d'``age``
    ans et plus, en personnes.

    Ce sont les têtes de ``calculer_cout`` (``AvenirAnnuel.tetes``), sous la
    démographie centrale et les réglages de la page : la même grille, que
    ``memoire.cout`` garde, les mêmes poids recalés sur les groupes du COR, la
    somme de ``cout._masses`` (:func:`compter_retraites`), qui en ôte les moins
    d'``age`` ans. ``cout.py`` ne les expose pas par âge : ce geste le refait,
    et ``tests/test_facteurs_depense.py`` vérifie qu'il redonne ses têtes.
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
    resultat: dict[int, tuple[float, float]] = {}
    for annee in annees:
        poids_annee = poids(annee)
        survies = module._survies_alignees(pensionnes, poids_annee, annee)
        resultat[annee] = tuple(
            compter_retraites(pensionnes, population, annee, poids_annee,
                              depart_de_la_grille, minimum, survies)
            for minimum in (0, age))
    return resultat
