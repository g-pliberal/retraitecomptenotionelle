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

LES NAISSANCES DE L'ANNÉE ET L'ENTRÉE DANS L'EMPLOI (:func:`dates_des_departs`),
deux mesures que ``cout.py`` ne fait pas, la pension restant celle de la
grille. Née toute l'année et non en janvier, une cohorte n'a, au 31 décembre
de l'année de son départ, que ses natifs des premiers mois de partis
(:func:`compter_retraites`). Entrée dans l'emploi à l'âge que l'échantillon
interrégimes de cotisants de 2017 donne à sa génération, et non au même âge à
chacune (limite n° 2 de ``cout.py``), elle part au taux plein d'autant plus
tard (:func:`decalage_d_entree`) : les générations de 1966 à 1970 entrent un an
après celle de 1960, et Destinie, le modèle de l'AWG pour la France, les fait
partir plus tard (fiche, § 3.3 ; note du 19 octobre 2026, « l'entrée dans
l'emploi »).

LES DÉPARTS HORS DU TAUX PLEIN (:func:`dates_a_l_age_legal`), une troisième
mesure. La grille fait partir chacun au taux plein ; la génération 1953 est
partie à 9,4 % avec une décote dès l'âge légal (EIR,
:func:`part_decotee_des_l_age_legal`). La même part de la génération, prise à
ses cohortes qui n'ont le taux plein qu'après lui (:func:`part_avec_decote`),
part à l'âge légal : ses 65 ans et plus reculent moins, les moins de 65 ans
presque comme avant (note du 19 octobre 2026, « les départs hors du taux
plein »).

L'ÂGE DE DÉPART DE CHAQUE GÉNÉRATION (:func:`ages_moyens_de_depart`,
:func:`parts_parties`), confronté au COR (figures 4.5 à 4.7 du rapport de juin
2026, ``tests/temoins/cor_age_depart_generations_2026.json``). Chaque cohorte
pesée du poids de son cas type l'année où sa génération atteint 65 ans, la
grille de ``cout.py`` fait partir les générations 1975 à 2000 à 63,8 ans, sept
dixièmes d'an avant les 64,5 ans du COR ; entrées selon leur génération, à son
âge, à deux dixièmes près sous chacune des mesures. Ce qui la distingue de la
France est la forme de ses départs : moins avant l'âge légal, où partent les
carrières longues, presque aucun après 66 ans (note du 24 octobre 2026,
« l'âge de départ de chaque génération »).

CE QUI MANQUE. Les têtes de la proposition : son âge légal de 65 ans reporte
des départs que ``AvenirAnnuel`` ne compte pas à part. La couverture de chaque
système est donc celle du droit en vigueur, et sa prestation porte ce que le
report change — à ``cout.py`` d'exposer ces têtes. Et le flux des pensions
nouvelles que l'AWG décompose à part (fiche France, tableau 14).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable, Collection, Mapping, Sequence

from .calendrier import DateMois
from .cout import _DEMI_TRANCHE, masse_du_scenario
from .donnees.chargement import charger_table_csv, dans_un_instantane
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
                      survies: Mapping[tuple[str, int, int], float] | None = None,
                      mois: Mapping[tuple[str, int, int], int] | None = None,
                      decotes: Mapping[tuple[str, int, int], tuple[float, int, int]] | None = None,
                      ) -> float:
    """Les retraités de l'année, en personnes : les cohortes de la grille
    parties au plus tard cette année-là, chacune l'année que ``depart`` lui
    donne, de la génération ``pensionne.generation + decalage``, pesées comme
    ``cout._masses`` pèse ses têtes — l'effectif de la classe d'âge, fois la
    survie propre du cas type, ``survies`` par ``(code, generation,
    decalage)`` (``cout._survies_alignees``, un par défaut), fois le poids du
    cas type. ``age`` ôte les plus jeunes.

    ``mois``, par la même clé, fait naître chaque cohorte toute l'année, et
    non en janvier comme la grille : partie, née en janvier, le mois ``m`` de
    l'année de son départ, elle n'en a au 31 décembre que les ``(13 - m) / 12``
    de partis, au même âge (:func:`dates_des_departs`).

    ``decotes``, par la même clé, fait partir une part de la cohorte avant son
    taux plein, avec une décote, et le reste au taux plein : ``(part, annee,
    mois)``, la date de ce départ-là, dont le mois ne compte que si ``mois``
    fait naître la cohorte toute l'année (:func:`dates_a_l_age_legal`)."""
    survies = survies or {}
    mois = mois or {}
    decotes = decotes or {}
    total = 0.0
    for pensionne in pensionnes:
        part = poids_cas.get(pensionne.code, 0.0)
        if part <= 0.0:
            continue
        poids = 0.0
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            age_atteint = annee - pensionne.generation - decalage
            if age_atteint < age:
                continue
            cle = (pensionne.code, pensionne.generation, decalage)
            decotee, annee_decotee, mois_decote = decotes.get(cle, (0.0, 0, 0))
            partis = ((1.0 - decotee) * _partis(annee, depart(pensionne, decalage), mois.get(cle))
                      + decotee * _partis(annee, annee_decotee,
                                          mois_decote if cle in mois else None))
            if partis:
                poids += partis * population.effectif(age_atteint, annee) * survies.get(cle, 1.0)
        total += part * poids
    return total


def _partis(annee: int, parti: int, mois: int | None) -> float:
    """La part d'une cohorte partie au 31 décembre de ``annee`` : rien avant
    l'année ``parti`` de son départ ; cette année-là, ``(13 - mois) / 12``
    quand elle est née toute l'année et partie, née en janvier, le mois
    ``mois`` ; toute ensuite."""
    if annee < parti:
        return 0.0
    return (13 - mois) / 12 if annee == parti and mois is not None else 1.0


def ages_medians_du_premier_trimestre(racine: Path) -> dict[tuple[str, int], float]:
    """L'âge où la moitié des affiliés d'avant 23 ans de chaque génération de
    l'échantillon interrégimes de cotisants de 2017, sexe par sexe, avaient
    cotisé un trimestre (``macro/premier_trimestre.csv``), par ``(sexe,
    génération)`` : la part de chaque âge est celle de la fin de l'année où il
    est atteint, en moyenne à cet âge et demi, et l'âge se lit entre deux
    parts, en droite ligne."""
    table, _fiabilites = charger_table_csv(
        Path(racine) / "reference" / "macro" / "premier_trimestre.csv",
        ("sexe", "generation", "trimestre", "age"), "part")
    parts: dict[tuple[str, int], dict[int, float]] = {}
    for (sexe, generation, trimestre, age), part in table.items():
        if trimestre == "cotise":
            parts.setdefault((sexe, int(generation)), {})[int(age)] = part
    medianes = {}
    for cle, par_age in parts.items():
        ages = sorted(par_age)
        for avant, apres in zip(ages, ages[1:]):
            if par_age[avant] < 50.0 <= par_age[apres]:
                medianes[cle] = (avant + 0.5 + (50.0 - par_age[avant])
                                 / (par_age[apres] - par_age[avant]) * (apres - avant))
                break
    return medianes


def decalage_d_entree(medianes: Mapping[tuple[str, int], float], sexe: str,
                      generation: int, reference: int) -> float:
    """De combien la génération ``generation`` entre dans l'emploi plus tard
    que ``reference``, au trimestre près : l'écart de leurs âges médians du
    premier trimestre cotisé (:func:`ages_medians_du_premier_trimestre`), lus
    entre les deux générations voisines quand l'EIC ne suit pas la leur, à la
    première ou à la dernière au-delà."""
    def mediane(annee: int) -> float:
        suivies = sorted(g for s, g in medianes if s == sexe)
        annee = min(max(annee, suivies[0]), suivies[-1])
        apres = next(g for g in suivies if g >= annee)
        if apres == annee:
            return medianes[(sexe, annee)]
        avant = max(g for g in suivies if g < annee)
        return (medianes[(sexe, avant)] + (medianes[(sexe, apres)] - medianes[(sexe, avant)])
                * (annee - avant) / (apres - avant))

    return round((mediane(generation) - mediane(reference)) * 4) / 4


def durees_validees(temoin: Mapping) -> dict[tuple[str, int], dict[int, float]]:
    """Le cumul des trimestres validés par affilié d'avant 23 ans de chaque
    génération de l'échantillon interrégimes de cotisants de 2017, sexe par
    sexe, à la fin de l'année de chaque âge, de 16 ans au dernier que
    l'échantillon voit (``tests/temoins/drees_duree_validee_2017.json``,
    ``scripts/fetch/drees_duree_validee.py``), par ``(sexe, génération)``."""
    return {(sexe, int(generation)): {int(age): float(cumul) for age, cumul in cumuls.items()}
            for sexe, generations in temoin["cumuls"].items()
            for generation, cumuls in generations.items()}


def decalage_par_la_duree(durees: Mapping[tuple[str, int], Mapping[int, float]], sexe: str,
                          generation: int, reference: int) -> float:
    """De combien la génération ``generation`` a validé moins de trimestres que
    ``reference``, en années de quatre trimestres, au trimestre près : l'écart
    de leurs cumuls au dernier âge que l'échantillon voit chez l'une et l'autre
    (:func:`durees_validees`), quand :func:`decalage_d_entree` lit celui de leur
    premier trimestre cotisé ; entre les deux générations voisines, en droite
    ligne, quand l'EIC ne suit pas la sienne, à la première ou à la dernière
    au-delà."""
    if (sexe, reference) not in durees:
        raise ValueError(f"l'EIC ne suit pas la génération {reference}")
    suivies = sorted(g for s, g in durees if s == sexe)

    def ecart(annee: int) -> float:
        propres, autres = durees[(sexe, annee)], durees[(sexe, reference)]
        age = min(max(propres), max(autres))
        return (autres[age] - propres[age]) / 4

    annee = min(max(generation, suivies[0]), suivies[-1])
    apres = next(g for g in suivies if g >= annee)
    if apres == annee:
        return round(ecart(annee) * 4) / 4
    avant = max(g for g in suivies if g < annee)
    return round((ecart(avant) + (ecart(apres) - ecart(avant)) * (annee - avant)
                  / (apres - avant)) * 4) / 4


#: La génération de l'EIR dont les départs avec décote donnent leur part à la
#: grille (:func:`part_decotee_des_l_age_legal`) : les nés en 1953, les plus
#: récents que l'enquête de 2020 voie presque tous partis, comme pour la
#: surcote de la population (``scripts/grille_large.py``).
GENERATION_DES_DECOTES = 1953
#: L'année de l'enquête qui compte la génération :data:`GENERATION_DES_DECOTES`,
#: celle dont les poids rapportent sa part à la grille (:func:`part_avec_decote`).
ANNEE_DES_DECOTES = 2020
#: Les places du départ que l'EIR range à l'âge légal ou après lui : à cet âge,
#: entre lui et l'âge d'annulation de la décote, à ce dernier, au-delà.
PLACES_DES_L_AGE_LEGAL: tuple[str, ...] = ("age_legal", "entre", "age_annulation",
                                           "apres_annulation")


def part_decotee_des_l_age_legal(racine: Path) -> float:
    """La part de la génération :data:`GENERATION_DES_DECOTES` partie avec une
    décote à l'âge légal ou après lui, tous régimes, que l'EIR range par la
    place de leur départ dans leur régime principal
    (``macro/departs_generations.csv``) : la part de chaque place dans la
    génération, fois celle de ses départs pris avec une décote. Avant l'âge
    légal ne décotent que les régimes qui ouvrent plus tôt, catégories actives
    et régimes spéciaux, dont la grille garde le départ (:func:`dates_a_l_age_legal`)."""
    table, _fiabilites = charger_table_csv(
        Path(racine) / "reference" / "macro" / "departs_generations.csv",
        ("generation", "tableau", "colonne", "sexe", "indicateur"), "valeur")
    generation = str(GENERATION_DES_DECOTES)
    return somme_ordonnee(
        table[(generation, "position", place, "ensemble", "part")]
        * table[(generation, "position", place, "ensemble", "condition_decote")]
        for place in PLACES_DES_L_AGE_LEGAL) / 1e4


def part_avec_decote(cible: float, poids: Mapping[tuple[str, int, int], float],
                     decotables: Collection[tuple[str, int, int]]) -> float:
    """La part de chaque cohorte ``decotables`` qui part avec une décote à
    l'âge légal : ``cible``, la part de sa génération partie ainsi
    (:func:`part_decotee_des_l_age_legal`), rapportée au poids de ces cohortes
    parmi toutes celles de la génération, ``poids`` par ``(code, generation,
    decalage)``, comme la population de l'étape 14 rapporte la part de l'EIR à
    ses carrières incomplètes ; une au plus, rien sans cohorte qui le puisse."""
    toutes = somme_ordonnee(poids.values())
    eligibles = somme_ordonnee(p for cle, p in poids.items() if cle in decotables)
    return min(1.0, cible * toutes / eligibles) if eligibles else 0.0


#: La caisse et l'année de la table H de l'EACR dont le flux de liquidants dit
#: la part décotée des générations que l'EIR ne suit pas
#: (:func:`part_decotee_du_flux`) : la Cnav, en 2024, l'année la plus récente.
CAISSE_DU_FLUX = "0015"
ANNEE_DU_FLUX = 2024
#: La génération qu'on prête à ce flux : celle des liquidants de
#: :data:`ANNEE_DU_FLUX` à l'âge moyen des nouveaux retraités de l'année,
#: 63,6 ans tous régimes (table C, tirée d'Ancetre).
GENERATION_DU_FLUX = 1960


def part_decotee_du_flux(temoin: Mapping) -> float:
    """La part des liquidants de la Cnav de :data:`ANNEE_DU_FLUX` partis avec
    une décote, parmi ceux qui sont partis au taux plein, avec une décote ou
    avec une surcote (``tests/temoins/drees_eacr_tables_2026.json``, table H,
    ``controle_eacr.conditions_publiees``) : tous partent à l'âge légal ou
    après lui, les départs anticipés de la Cnav, carrières longues et
    inaptes, se prenant au taux plein."""
    from .controle_eacr import conditions_publiees

    return next(conditions.decote for conditions in conditions_publiees(temoin, ANNEE_DU_FLUX)
                if conditions.caisse == CAISSE_DU_FLUX and conditions.champ == "flux")


def part_decotee_de_la_generation(generation: int, de_1953: float, du_flux: float) -> float:
    """La part de ``generation`` partie avec une décote dès l'âge légal :
    ``de_1953``, celle de la génération :data:`GENERATION_DES_DECOTES`, jusqu'à
    elle (:func:`part_decotee_des_l_age_legal`) ; ``du_flux``, celle des
    liquidants de la Cnav de :data:`ANNEE_DU_FLUX` (:func:`part_decotee_du_flux`),
    depuis la génération :data:`GENERATION_DU_FLUX` ; en droite ligne entre
    les deux."""
    if generation <= GENERATION_DES_DECOTES:
        return de_1953
    if generation >= GENERATION_DU_FLUX:
        return du_flux
    return de_1953 + ((du_flux - de_1953) * (generation - GENERATION_DES_DECOTES)
                      / (GENERATION_DU_FLUX - GENERATION_DES_DECOTES))


@dans_un_instantane
def dates_des_departs(parametres, entree_depuis: int | None = None,
                      cas_types: tuple | None = None,
                      generations: tuple[int, ...] | None = None,
                      a_l_ouverture: bool = False,
                      durees: Mapping[tuple[str, int], Mapping[int, float]] | None = None,
                      ) -> dict[tuple[str, int, int], DateMois]:
    """Le mois où part, née en janvier comme la grille, chacune des cinq
    cohortes de chaque couple de la grille du coût, par ``(code, generation,
    decalage)`` (:func:`compter_retraites`) : celui de la carrière que le droit
    de sa génération lui donne, comme ``cout._carrieres_voisines`` la refait,
    ou celui de la génération de la grille, décalé d'autant d'années, pour une
    cohorte qu'elle ne sait pas simuler. Les carrières se refont sans rien
    simuler : ``Pensionne`` ne garde que l'année.

    ``entree_depuis`` fait entrer dans l'emploi chaque génération d'un cas type
    qui part au taux plein plus tard que la génération ``entree_depuis``,
    d'autant que celles de son sexe dans l'EIC (:func:`decalage_d_entree`), quand
    la grille les fait toutes entrer au même âge (limite n° 2 de ``cout.py``) ;
    ceux qui partent à un âge ou après leurs services gardent leur date.
    ``durees``, le cumul des trimestres validés à chaque âge
    (:func:`durees_validees`), y lit le retard sur la durée validée
    (:func:`decalage_par_la_duree`) et non sur le premier trimestre cotisé.
    ``a_l_ouverture`` fait partir chaque cohorte d'un cas type qui part au
    taux plein dès l'ouverture de son droit, avec une décote si le taux plein
    vient après (``regle_liquidation="ouverture"``)."""
    from . import cout as module
    from .castypes import GRILLE_DU_COUT, carriere_de_la_grille, carrieres_de_la_grille
    from .simulateur import Simulateur

    simulateur = Simulateur(parametres).pour_la_projection()
    cas_types = GRILLE_DU_COUT if cas_types is None else cas_types
    generations = module.generations() if generations is None else generations
    medianes = (None if entree_depuis is None
                else ages_medians_du_premier_trimestre(parametres.racine_donnees))
    cas_de = {cas.code: cas for cas in cas_types}
    carrieres, _ecartees = carrieres_de_la_grille(simulateur, cas_types, generations, "droit")
    dates = {}
    for (code, generation), carriere in carrieres.items():
        cas = cas_de[code]
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            propre = cas
            if medianes is not None and cas.regle_liquidation == "taux_plein":
                entree = (decalage_d_entree(medianes, cas.sexe, generation + decalage,
                                            entree_depuis) if durees is None
                          else decalage_par_la_duree(durees, cas.sexe, generation + decalage,
                                                     entree_depuis))
                if entree:
                    propre = replace(cas, age_debut=cas.age_debut + entree)
            if a_l_ouverture and cas.regle_liquidation == "taux_plein":
                propre = replace(propre, regle_liquidation="ouverture")
            date = DateMois(carriere.annee_liquidation + decalage, carriere.mois_liquidation)
            if decalage or propre is not cas:
                try:
                    date = carriere_de_la_grille(simulateur, propre, generation + decalage,
                                                 "droit").date_liquidation
                except (ValueError, KeyError):
                    pass
            dates[(code, generation, decalage)] = date
    return dates


@dans_un_instantane
def dates_a_l_age_legal(parametres, entree_depuis: int | None = None,
                        cas_types: tuple | None = None,
                        generations: tuple[int, ...] | None = None,
                        durees: Mapping[tuple[str, int], Mapping[int, float]] | None = None,
                        ) -> dict[tuple[str, int, int], DateMois]:
    """Le mois où partirait avec une décote, à l'âge légal de sa génération
    (L. 161-17-2), chaque cohorte de la grille du coût qui n'a le taux plein
    qu'après lui, par ``(code, generation, decalage)``
    (:func:`dates_des_departs`, dont ``entree_depuis`` et ``durees``) : celle d'un cas type
    qui part au taux plein, dont le droit s'ouvre à cet âge et non avant. Les
    catégories actives, que leur classement ouvre plus tôt, gardent leur
    départ, comme ceux qui ont le taux plein dès l'ouverture, carrières
    longues et inaptes, et ceux qui partent à un âge ou après leurs
    services."""
    from .simulateur import Simulateur

    ages_legaux = Simulateur(parametres).scenario_actuel.ages_ouverture
    taux_plein = dates_des_departs(parametres, entree_depuis, cas_types, generations,
                                   durees=durees)
    ouvertures = dates_des_departs(parametres, entree_depuis, cas_types, generations,
                                   a_l_ouverture=True, durees=durees)
    legales = {}
    for (code, generation, decalage), date in ouvertures.items():
        legal = ages_legaux.age(generation + decalage)
        mois_atteints = (date.annee - generation - decalage) * 12 + date.mois - 1
        if (legal is not None and date.rang < taux_plein[(code, generation, decalage)].rang
                and mois_atteints >= round(legal[0] * 12)):
            legales[(code, generation, decalage)] = date
    return legales


def grille_ponderee(parametres) -> tuple[list, object, Callable[[int], dict[str, float]]]:
    """La grille du coût sous ces paramètres, comme ``calculer_cout`` la pèse :
    ses couples, que ``memoire.cout`` garde, sous la démographie centrale ; la
    pyramide de l'INSEE ; et les poids de chaque année, recalés sur les
    groupes du COR."""
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
        module._ponderation(simulateur, "effectifs", grille,
                            tetes=module._tetes_par_poids(pensionnes, population)),
        pensionnes, population,
        revalorisation, ComptesRetraite(racine, variante=variante).decomposition)
    return pensionnes, population, poids


def parts_decotees(parametres, pensionnes, poids: Callable[[int], dict[str, float]],
                   legales: Mapping[tuple[str, int, int], DateMois],
                   decote_du_flux: float | None = None,
                   ) -> dict[tuple[str, int, int], tuple[float, DateMois]]:
    """La part de chaque cohorte de la grille qui n'a le taux plein qu'après
    l'âge légal et y part avec une décote, et le mois de ce départ, ``legales``
    par ``(code, generation, decalage)`` (:func:`dates_a_l_age_legal`) : la part de
    la génération :data:`GENERATION_DES_DECOTES` partie ainsi
    (:func:`part_decotee_des_l_age_legal`), ou celle de chaque génération quand
    ``decote_du_flux`` la dit (:func:`part_decotee_de_la_generation`),
    rapportée au poids des cohortes de :data:`GENERATION_DES_DECOTES` qui le
    peuvent, en :data:`ANNEE_DES_DECOTES` (:func:`part_avec_decote`)."""
    from . import cout as module

    poids_enquete = poids(ANNEE_DES_DECOTES)
    survies_enquete = module._survies_alignees(pensionnes, poids_enquete, ANNEE_DES_DECOTES)
    generation = {
        (pensionne.code, pensionne.generation, decalage):
            poids_enquete.get(pensionne.code, 0.0)
            * survies_enquete.get((pensionne.code, pensionne.generation, decalage), 1.0)
        for pensionne in pensionnes
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1)
        if pensionne.generation + decalage == GENERATION_DES_DECOTES}
    de_1953 = part_decotee_des_l_age_legal(parametres.racine_donnees)
    du_flux = de_1953 if decote_du_flux is None else decote_du_flux
    parts = {nee: part_avec_decote(part_decotee_de_la_generation(nee, de_1953, du_flux),
                                   generation, legales)
             for nee in {code_nee + decalage for _code, code_nee, decalage in legales}}
    return {(code, code_nee, decalage): (parts[code_nee + decalage], date)
            for (code, code_nee, decalage), date in legales.items()}


def retraites_par_age(parametres, annees: Sequence[int],
                      age: int = AGE_VIEILLESSE,
                      nes_toute_l_annee: bool = False,
                      entree_depuis: int | None = None,
                      avec_decote: bool = False,
                      decote_du_flux: float | None = None,
                      durees: Mapping[tuple[str, int], Mapping[int, float]] | None = None,
                      ) -> dict[int, tuple[float, float]]:
    """Chaque année, les retraités du modèle de tous âges, puis ceux d'``age``
    ans et plus, en personnes.

    Ce sont les têtes de ``calculer_cout`` (``AvenirAnnuel.tetes``), sous la
    démographie centrale et les réglages de la page : la même grille, que
    ``memoire.cout`` garde, les mêmes poids recalés sur les groupes du COR, la
    somme de ``cout._masses`` (:func:`compter_retraites`), qui en ôte les moins
    d'``age`` ans. ``cout.py`` ne les expose pas par âge : ce geste le refait,
    et ``tests/test_facteurs_depense.py`` vérifie qu'il redonne ses têtes.
    ``nes_toute_l_annee`` fait naître chaque cohorte toute l'année, et
    ``entree_depuis`` entrer chaque génération dans l'emploi à son âge
    (:func:`dates_des_departs`) : ce ne sont plus les têtes de ``cout.py``, et
    la pension reste celle de la grille. ``avec_decote`` fait partir à l'âge
    légal, avec une décote, une part de chaque cohorte qui n'a le taux plein
    qu'après lui (:func:`dates_a_l_age_legal`) : la part de la génération
    :data:`GENERATION_DES_DECOTES` partie ainsi
    (:func:`part_decotee_des_l_age_legal`), rapportée au poids de ses cohortes
    qui le peuvent, en :data:`ANNEE_DES_DECOTES` (:func:`part_avec_decote`).
    ``decote_du_flux``, la part décotée des liquidants de la Cnav de
    :data:`ANNEE_DU_FLUX` (:func:`part_decotee_du_flux`), y fait suivre à
    chaque génération la sienne (:func:`part_decotee_de_la_generation`),
    rapportée de même. ``durees``, le cumul des trimestres validés à chaque
    âge (:func:`durees_validees`), lit l'entrée de chaque génération sur sa
    durée validée et non sur son premier trimestre cotisé
    (:func:`decalage_par_la_duree`).
    """
    from . import cout as module

    pensionnes, population, poids = grille_ponderee(parametres)
    depart, mois = depart_de_la_grille, None
    if nes_toute_l_annee or entree_depuis is not None:
        dates = dates_des_departs(parametres, entree_depuis, durees=durees)
        if entree_depuis is not None:
            def depart(pensionne, decalage: int) -> int:
                date = dates.get((pensionne.code, pensionne.generation, decalage))
                return depart_de_la_grille(pensionne, decalage) if date is None else date.annee
        if nes_toute_l_annee:
            mois = {cle: date.mois for cle, date in dates.items()}
    decotes = None
    if avec_decote:
        legales = dates_a_l_age_legal(parametres, entree_depuis, durees=durees)
        decotes = {cle: (part, date.annee, date.mois)
                   for cle, (part, date) in parts_decotees(
                       parametres, pensionnes, poids, legales, decote_du_flux).items()}
    resultat: dict[int, tuple[float, float]] = {}
    for annee in annees:
        poids_annee = poids(annee)
        survies = module._survies_alignees(pensionnes, poids_annee, annee)
        resultat[annee] = tuple(
            compter_retraites(pensionnes, population, annee, poids_annee,
                              depart, minimum, survies, mois, decotes)
            for minimum in (0, age))
    return resultat


def _age_au_depart(date: DateMois, nee: int) -> float:
    """L'âge, en années, d'une cohorte née en janvier de ``nee`` qui part le
    mois ``date`` : ses années, et les mois qui les suivent."""
    return date.annee - nee + (date.mois - 1) / 12


def _cohortes_pesees(departs: Mapping[tuple[str, int, int], DateMois],
                     poids: Callable[[int], Mapping[str, float]],
                     decotes: Mapping[tuple[str, int, int], tuple[float, DateMois]] | None,
                     ):
    """Chaque cohorte de ``departs`` qui pèse : l'année où elle naît, le poids
    de son cas type l'année où sa génération atteint :data:`AGE_VIEILLESSE`
    ans, et ses départs, ``(part, mois)`` — au taux plein, et avec une décote
    pour la part que ``decotes`` dit, le mois qu'il dit."""
    decotes = decotes or {}
    for cle, date in departs.items():
        code, generation, decalage = cle
        nee = generation + decalage
        part = poids(nee + AGE_VIEILLESSE).get(code, 0.0)
        if part <= 0.0:
            continue
        decotee, legale = decotes.get(cle, (0.0, date))
        yield nee, part, ((1.0 - decotee, date), (decotee, legale))


def _moyennes(termes: Mapping[object, list[tuple[float, float]]]) -> dict:
    """La moyenne de chaque clé, ses ``(poids, valeur)`` pesés."""
    return {cle: somme_ordonnee(part * valeur for part, valeur in lignes)
            / somme_ordonnee(part for part, _valeur in lignes)
            for cle, lignes in sorted(termes.items())}


def ages_moyens_de_depart(departs: Mapping[tuple[str, int, int], DateMois],
                          poids: Callable[[int], Mapping[str, float]],
                          decotes: Mapping[tuple[str, int, int], tuple[float, DateMois]]
                          | None = None) -> dict[int, float]:
    """L'âge moyen de départ de chaque génération de la grille, par année de
    naissance : celui de ses cohortes, ``departs`` par ``(code, generation,
    decalage)`` (:func:`dates_des_departs`), chacune née en janvier, à l'âge du
    mois où elle part, pesée du poids de son cas type l'année où sa génération
    atteint :data:`AGE_VIEILLESSE` ans (``poids``, ceux de ``cout.py``). Le COR
    compte chaque liquidant (figure 4.5 du rapport de juin 2026) ; l'effectif
    de la pyramide ne pèse pas, qui commençait à 50 ans quand la mesure a été
    écrite, le militaire partant à 48. ``decotes``, par la même clé, fait
    partir une part de la cohorte avant son taux plein, avec une décote, le
    mois dit (:func:`parts_decotees`)."""
    termes: dict[int, list[tuple[float, float]]] = {}
    for nee, part, sorties in _cohortes_pesees(departs, poids, decotes):
        age = somme_ordonnee(fraction * _age_au_depart(date, nee) for fraction, date in sorties)
        termes.setdefault(nee, []).append((part, age))
    return _moyennes(termes)


def parts_parties(departs: Mapping[tuple[str, int, int], DateMois],
                  poids: Callable[[int], Mapping[str, float]],
                  ages: Sequence[int],
                  decotes: Mapping[tuple[str, int, int], tuple[float, DateMois]]
                  | None = None) -> dict[tuple[int, int], float]:
    """La part de chaque génération de la grille partie au 31 décembre de
    l'année de chacun des ``ages``, par ``(année de naissance, âge)``, comme le
    COR compte les retraités de chaque génération et de chaque âge (figures
    4.6 et 4.7 du rapport de juin 2026) : ses cohortes pesées comme
    :func:`ages_moyens_de_depart` les pèse, nées toute l'année et non en
    janvier comme la grille (:func:`_partis`)."""
    termes: dict[tuple[int, int], list[tuple[float, float]]] = {}
    for nee, part, sorties in _cohortes_pesees(departs, poids, decotes):
        for age in ages:
            partis = somme_ordonnee(fraction * _partis(nee + age, date.annee, date.mois)
                                    for fraction, date in sorties)
            termes.setdefault((nee, age), []).append((part, partis))
    return _moyennes(termes)
