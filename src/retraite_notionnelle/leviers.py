"""Les trois leviers qui équilibreraient chaque système, à la manière du COR.

Le rapport annuel du COR chiffre ce que chacun des trois leviers du système de
retraite devrait faire, SEUL, pour que les comptes tombent justes (rapport de
juin 2026, partie 2, chapitre 6 ; figure 2.24 et tableau 2.11) :

* la PENSION moyenne relative, que l'équilibre de l'année ramène à ce que les
  ressources paient ;
* le TAUX DE PRÉLÈVEMENT global, les ressources rapportées aux revenus
  d'activité, que l'équilibre de l'année relève de ce qui manque ;
* l'ÂGE effectif moyen de départ, que l'équilibre de l'année recule jusqu'à
  ce que les retraités en moins et les cotisants en plus comblent le manque ;

et, sur un horizon — 2030, 2045, 2050, 2070 —, l'ajustement immédiat et
uniforme qui l'équilibrerait en moyenne : le « pension gap », les soldes
cumulés sur les pensions cumulées, et le « tax gap », les mêmes soldes sur
les revenus d'activité cumulés. Le dépôt avait les deux premiers leviers d'une
année, pour une pension (:class:`~.cout.PensionFinancee`), et écartait l'âge
(action 138, étape 3 ; registre, ``maquette_globale_cor`` et
``simulateur_aurain``). Ce module chiffre les trois, chaque année, pour chaque
système, sur le bilan que ``cout.py`` calcule, sans y toucher, et les horizons ;
``tests/test_leviers.py`` se confronte au COR
(``tests/temoins/cor_leviers_2026.json``, ``scripts/fetch/cor_leviers.py``).

LA PENSION ET LE PRÉLÈVEMENT se lisent dans le bilan : l'équilibre de l'année
multiplie les pensions par le coefficient de ``SoldeAnnuel`` — la pension
relative varie donc de ``coefficient − 1`` —, ou ajoute au taux le manque
rapporté aux revenus d'activité. Les revenus d'activité sont l'assiette
mesurée, salaires bruts et revenu mixte (:class:`~.donnees.assiette.AssietteActivite`),
dont la part dans le PIB est celle de sa dernière année publiée, comme
:func:`~.cout.financer` la prend : la même pour tous les systèmes.

L'ÂGE, COMME LE COR LE CHIFFRE. Le rapport ne dit pas comment il passe d'un
manque à un âge ; il renvoie à l'abaque du COR (Lettre n° 11, avril 2015), où
l'équilibre s'écrit

    taux de prélèvement × cotisants = pension relative × retraités,

et où reculer l'âge relève le rapport des cotisants aux retraités. Le geste
retenu ici (:func:`releve_age`) : reculer l'âge de ``Δ`` ans retire des
retraités ceux qui ont de ``a`` à ``a + Δ`` ans — la population de ces âges
que l'INSEE projette, ``a`` étant l'âge où l'on part —, et en compte une
part ``e`` parmi les cotisants ; ``Δ`` est celui qui multiplie le rapport des
cotisants aux retraités par ce que l'équilibre demande, la dépense sur les
ressources. Appliqué aux propres séries du COR — ses cotisants par retraité
(``decomposition_depense_retraite.csv``), sa pension relative spontanée et
d'équilibre, son âge spontané —, il redonne l'âge d'équilibre que le COR
publie à 0,05 an près chaque année de 2030 à 2070, pour une part ``e`` de 60
à 70 % selon le nombre de retraités qu'on prête au COR, qui ne le publie
qu'en croissance. Le dépôt garde la sienne, la part des reportés en emploi
qu'il a lue dans les évaluations de la réforme de 2010
(``Parametres.part_reportes_en_emploi``, la moitié) : un peu moins de
cotisants par année de recul, donc un peu plus d'âge — 0,2 an en 2070.

Comme ceux du COR, ces leviers sont MÉCANIQUES : reculer l'âge ne change pas
la pension de qui part plus tard, ni les cotisations n'ôtent rien au PIB. Ils
disent la taille du manque dans trois unités, non une réforme.

CE QUI EST PRÉSUMÉ, ET DÉCLARÉ.

* Les retraités sont ceux du modèle (``AvenirAnnuel.tetes``), les mêmes pour
  tous les systèmes, comme dans :mod:`.facteurs_depense` : l'âge légal de 65
  ans de la proposition ne les déplace pas.
* Les cotisants n'ont pas de niveau dans le modèle, qui n'a qu'un indice
  d'emploi (:func:`~.facteurs_depense.indice_emploi`) : ils sont ancrés sur
  le rapport des cotisants aux retraités que le COR observe en 2024, la
  dernière année qu'il observe, et croissent comme l'emploi.
* L'âge où l'on prend la génération déplacée est 64 ans et demi
  (:data:`AGE_DE_DEPART`), celui que le COR projette à législation inchangée
  de 2040 à 2070 (64,5 à 64,6 ans) ; avant 2040, son âge monte de 63,9 à
  64,5 ans, et la génération déplacée change de moins de 2 %.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .somme import somme_ordonnee

#: L'âge effectif moyen de départ autour duquel le recul déplace des
#: générations, en années : en-tête du module.
AGE_DE_DEPART = 64.5

#: Les horizons du tableau 2.11 du COR, et l'année d'où part l'ajustement
#: immédiat (« dès 2026 », rapport de juin 2026, p. 126).
HORIZONS_COR: tuple[int, ...] = (2030, 2045, 2050, 2070)
DEBUT_AJUSTEMENT = 2026

#: L'année où les cotisants du modèle sont ancrés sur ceux du COR : la
#: dernière qu'il observe (figure 2.3 du rapport de juin 2026).
ANNEE_ANCRAGE = 2024

#: Les bornes du recul cherché, en années : en deçà, un excédent fait AVANCER
#: l'âge.
RECUL_MINIMAL, RECUL_MAXIMAL = -10.0, 15.0


def population_entre(population, annee: int, debut: float, fin: float) -> float:
    """Les personnes qui ont de ``debut`` à ``fin`` ans au 1er janvier de
    ``annee``, âges fractionnaires compris : chaque âge révolu compte pour la
    part de l'année qu'il couvre. Négatif quand ``fin`` précède ``debut``."""
    if fin < debut:
        return -population_entre(population, annee, fin, debut)
    total = []
    age = debut
    while age < fin - 1e-12:
        suivant = min(fin, float(int(age) + 1))
        total.append(population.effectif(int(age), annee) * (suivant - age))
        age = suivant
    return somme_ordonnee(total)


def releve_age(rapport: float, retraites: float, cotisants: float, population,
               annee: int, age: float = AGE_DE_DEPART, part_en_emploi: float = 0.5,
               precision: float = 1e-6) -> float:
    """Le recul de l'âge effectif, en années, qui multiplie le rapport des
    cotisants aux retraités par ``rapport`` — la dépense sur les ressources.

    Reculer de ``Δ`` retire des retraités la population de ``age`` à
    ``age + Δ`` ans, et en ajoute aux cotisants la part ``part_en_emploi``.
    Négatif quand le système a une marge (``rapport`` sous un) : l'âge avance.
    Bissection : le rapport croît avec le recul.
    """
    cible = rapport * cotisants / retraites

    def ecart(recul: float) -> float:
        deplaces = population_entre(population, annee, age, age + recul)
        return (cotisants + part_en_emploi * deplaces) / (retraites - deplaces) - cible

    bas, haut = RECUL_MINIMAL, RECUL_MAXIMAL
    if ecart(bas) > 0.0 or ecart(haut) < 0.0:
        raise ValueError(f"{annee} : aucun recul de {bas:g} à {haut:g} ans "
                         f"ne multiplie le rapport démographique par {rapport:.4f}")
    while haut - bas > precision:
        milieu = (bas + haut) / 2.0
        if ecart(milieu) < 0.0:
            bas = milieu
        else:
            haut = milieu
    return (bas + haut) / 2.0


@dataclass(frozen=True)
class Leviers:
    """Ce que chaque levier, seul, devrait faire pour équilibrer une année."""

    annee: int
    #: La variation relative de la pension moyenne : négative quand il faut
    #: rogner.
    pension: float
    #: Le relèvement du taux de prélèvement, en fraction des revenus
    #: d'activité : 0,01 pour un point.
    prelevement: float
    #: Le recul de l'âge effectif moyen de départ, en années ; ``None`` quand
    #: aucun recul de :data:`RECUL_MINIMAL` à :data:`RECUL_MAXIMAL` ans ne
    #: suffit — le scénario 2, qui encaisse trois fois ce qu'il sert.
    age: float | None


@dataclass(frozen=True)
class Demographie:
    """Les retraités et les cotisants d'une année, en personnes."""

    retraites: float
    cotisants: float


def demographie_du_modele(avenir, macro, rapport_ancrage: float,
                          ancrage: int = ANNEE_ANCRAGE) -> dict[int, Demographie]:
    """Les retraités du modèle, et des cotisants qui en sont ``rapport_ancrage``
    fois plus l'année ``ancrage``, puis croissent comme l'emploi (en-tête du
    module)."""
    from .facteurs_depense import indice_emploi

    lignes = [ligne for ligne in avenir.annees if ligne.tetes > 0.0]
    par_annee = {ligne.annee: ligne for ligne in lignes}
    if ancrage not in par_annee:
        raise ValueError(f"le modèle ne compte pas de retraités en {ancrage}")
    emploi = indice_emploi(macro, lignes[0].annee, lignes[-1].annee)
    par_emploi = rapport_ancrage * par_annee[ancrage].tetes / emploi[ancrage]
    return {ligne.annee: Demographie(retraites=ligne.tetes,
                                     cotisants=par_emploi * emploi[ligne.annee])
            for ligne in lignes}


def leviers(solde, scenario: str, part_assiette: float,
            demographie: Mapping[int, Demographie], population,
            annees: Sequence[int], age: float = AGE_DE_DEPART,
            part_en_emploi: float = 0.5) -> dict[int, Leviers]:
    """Les trois leviers de ``scenario``, chaque année de ``annees``.

    ``solde`` est le bilan que rend ``calculer_cout`` (``Cout.solde``),
    ``part_assiette`` les revenus d'activité en part de PIB.
    """
    resultat: dict[int, Leviers] = {}
    for annee in annees:
        ligne = solde.annee(annee)
        if ligne is None or annee not in demographie:
            raise ValueError(f"{annee} : absente du bilan ou des retraités du modèle")
        coefficient = ligne.coefficient(scenario)
        effectifs = demographie[annee]
        try:
            recul = releve_age(1.0 / coefficient, effectifs.retraites, effectifs.cotisants,
                               population, annee, age, part_en_emploi)
        except ValueError:
            recul = None
        resultat[annee] = Leviers(
            annee=annee,
            pension=coefficient - 1.0,
            prelevement=-ligne.solde(scenario) / part_assiette,
            age=recul,
        )
    return resultat


@dataclass(frozen=True)
class EcartsSurHorizon:
    """L'ajustement immédiat et uniforme qui équilibre en moyenne, de
    ``debut`` à ``fin`` (tableau 2.11 du COR)."""

    debut: int
    fin: int
    #: Les soldes cumulés sur les pensions cumulées : la part de chaque
    #: pension à rogner, négative quand il faut rogner.
    pension_gap: float
    #: Les mêmes soldes, changés de signe, sur les revenus d'activité
    #: cumulés : le relèvement du taux, en fraction.
    tax_gap: float


def ecarts_sur_horizon(solde, scenario: str, part_assiette: float, pib: Mapping[int, float],
                       debut: int = DEBUT_AJUSTEMENT, fin: int = 2070) -> EcartsSurHorizon:
    """Le pension gap et le tax gap de ``debut`` à ``fin``, bornes comprises,
    chaque année pesée par son PIB ``pib`` — celui de la trajectoire, le bilan
    ne le portant que sur les années publiées.

    En euros constants (:func:`pib_constant`), le tax gap du système actuel
    est celui du tableau 2.11 du COR à 0,05 point près, à chaque horizon ; en
    euros courants, qui pèsent davantage les dernières années, 0,4 point de
    plus en 2070 : c'est donc en euros constants que le COR cumule.
    """
    annees = range(debut, fin + 1)
    lignes = [solde.annee(annee) for annee in annees]
    if any(ligne is None for ligne in lignes) or any(pib.get(annee, 0.0) <= 0.0
                                                      for annee in annees):
        raise ValueError(f"le bilan ou le PIB ne couvre pas {debut}-{fin}")
    soldes = somme_ordonnee(ligne.solde(scenario) * pib[ligne.annee] for ligne in lignes)
    depenses = somme_ordonnee(ligne.depense(scenario) * pib[ligne.annee] for ligne in lignes)
    revenus = somme_ordonnee(part_assiette * pib[annee] for annee in annees)
    return EcartsSurHorizon(debut=debut, fin=fin, pension_gap=soldes / depenses,
                            tax_gap=-soldes / revenus)


def pib_constant(avenir) -> dict[int, float]:
    """Le PIB de chaque année de la trajectoire, en euros constants."""
    return {ligne.annee: ligne.pib * ligne.coefficient_constants
            for ligne in avenir.annees if ligne.pib > 0.0}


@dataclass(frozen=True)
class LeviersDuModele:
    """Les leviers d'un système, chaque année, et ses écarts sur les horizons
    du COR."""

    annuels: dict[int, Leviers]
    horizons: dict[int, EcartsSurHorizon]


def leviers_du_modele(parametres, scenario: str = "actuel",
                      annees: Sequence[int] = tuple(range(2025, 2071))) -> LeviersDuModele:
    """Les leviers de ``scenario`` sous ces réglages : le bilan que
    ``calculer_cout`` rend (par la mémoire des calculs), les 20 ans et plus de
    l'INSEE, l'assiette mesurée, les cotisants par retraité que le COR observe
    en 2024, la part des reportés en emploi des réglages."""
    from . import memoire
    from .donnees.assiette import AssietteActivite
    from .donnees.equilibre import DecompositionDepense
    from .donnees.population import Population
    from .simulateur import Simulateur

    cout = memoire.cout(parametres)
    racine = parametres.racine_donnees
    assiette = AssietteActivite(racine)
    part_assiette = assiette.part_pib(assiette.derniere_annee)
    rapport = DecompositionDepense(racine / "reference" / "macro").valeur(
        "cotisants_par_retraite", "ensemble", ANNEE_ANCRAGE)
    if rapport is None:
        raise ValueError(f"le COR ne publie pas de cotisants par retraité en {ANNEE_ANCRAGE}")
    demographie = demographie_du_modele(cout.avenir, Simulateur(parametres).macro, rapport)
    annuels = leviers(cout.solde, scenario, part_assiette, demographie,
                      Population(racine, parametres.hypothese_esperance_vie), annees,
                      part_en_emploi=parametres.part_reportes_en_emploi)
    pib = pib_constant(cout.avenir)
    horizons = {fin: ecarts_sur_horizon(cout.solde, scenario, part_assiette, pib, fin=fin)
                for fin in HORIZONS_COR}
    return LeviersDuModele(annuels=annuels, horizons=horizons)
