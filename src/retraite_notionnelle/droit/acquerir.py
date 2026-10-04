"""Acquérir les droits (docs/architecture.md, § 7.2).

Ce que chaque année verse aux régimes qui la reçoivent, et ce qu'ils en font :

* des POINTS, par un prix d'achat, un barème en points, des points par
  trimestre validé ou le barème nommé de la proportionnelle agricole, chacun
  avec le taux de majoration pour enfants de son année d'acquisition ;
* des COTISATIONS, revalorisées aux prix de l'année de liquidation, pour les
  régimes dont on n'a pas le prix d'achat du point, et pour les années qui
  suivent le dernier barème quand aucun texte ne dit ce que ce prix suit, que
  la liquidation convertit par leur rendement ;
* la DURÉE qu'un régime plafonne, et la part de ses points qu'il retient ;
* les POINTS attribués sans cotisation, à la liquidation.

Les salaires portés au compte restent calculés par la liquidation du régime,
qui en choisit l'assiette, jusqu'à la phase 5.

Ce que l'étape écrit, :class:`Droits`, suit son schéma,
``data/reference/etapes/acquerir_les_droits.yaml``. Son jumeau est
``moteur/js/droit/acquerir.js``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from ..carriere import salaire_moyen_annuel
from ..donnees.chargement import (
    charger_chomage_complementaires,
    Fiabilite,
    assiette_minimale as _assiette_minimale_de,
    charger_assiettes_minimales,
)
from . import compter
from .commun import derniere_annee
from . import liquider, ouvrir

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..donnees.regimes import PeriodeRegime
    from ..scenarios.actuel import ScenarioActuel
    from .compter import Durees
    from .coordonner import Coordination

#: La version du schéma de l'étape.
SCHEMA_VERSION = 1


def assiette_minimale(moteur: ScenarioActuel, codes, ligne) -> float:
    """L'assiette minimale que la ligne oppose à l'un de ces régimes.

    Celle du régime de BASE d'un indépendant (D. 633-2, D. 642-4), portée
    par la ligne ; nulle pour tout autre régime — la complémentaire des
    artisans et commerçants n'a pas de minimum.
    """
    if ligne.assiette_minimale_base <= 0:
        return 0.0
    regle = _assiette_minimale_de(charger_assiettes_minimales(moteur.macro.racine),
                                  ligne.affiliation, ligne.annee)
    if regle is None or regle.regimes.isdisjoint(codes):
        return 0.0
    return ligne.assiette_minimale_base


def points_msa(moteur: ScenarioActuel, periode: PeriodeRegime, annee: int,
               revenu: float) -> float:
    """Points de retraite proportionnelle agricole d'une année (R. 732-71).

    Le barème est un escalier à quatre marches, et chacune de ses bornes est
    une grandeur que le modèle connaît déjà :

    * jusqu'à **400 SMIC horaires**, quinze points, quel que soit le revenu ;
    * de 400 à **800 SMIC**, une pente de quinze à trente points ;
    * de 800 SMIC à **deux fois le minimum contributif** non majoré, trente
      points, et le barème ne bouge pas sur toute cette plage ;
    * au-delà, une pente de trente points au maximum **M** de l'année, que
      l'article R. 732-70 définit par ``M = (PM − AVTS) / (37,5 × VP)`` —
      PM étant la pension maximale du régime général, c'est-à-dire la moitié
      du plafond, AVTS l'allocation aux vieux travailleurs salariés et VP la
      valeur du point. Le plafond de revenu de cette dernière marche est le
      plafond de la Sécurité sociale lui-même.

    **Le barème s'auto-vérifie.** Au minimum d'assiette du chef
    d'exploitation — six cents fois le SMIC horaire, D. 731-120 —, la deuxième marche
    donne 22,5 points, et au plafond la quatrième en donne 113,4 en 2025 avec
    l'AVTS, que le dernier alinéa arrondit « au nombre entier le plus proche » :
    ce sont les « 23 à 113 points » que la MSA et le ministère annoncent
    sans jamais publier la formule. Et la pension maximale qui en résulte
    pour une carrière pleine vaut exactement ``PM − AVTS``, la valeur du
    point s'annulant : le forfait complète la proportionnelle jusqu'à la
    pension maximale du régime général, ce qui est bien la construction du
    régime.
    """
    smic = moteur.macro.smic_horaire(annee)
    pass_annuel = moteur.macro.plafond_securite_sociale(annee)
    valeur_point = liquider.valeur_point_fiche(moteur, periode, annee)
    if smic <= 0 or pass_annuel <= 0 or valeur_point <= 0:
        return 0.0
    # L'AVTS est le montant de la retraite forfaitaire elle-même : la loi
    # les a égalés jusqu'en 2014 (L. 732-24), puis a figé le forfait sur
    # l'AVTS de cette année-là. Les deux ont depuis divergé — 4 023,51 €
    # d'AVTS au 1er janvier 2025 contre 3 850 € environ de forfait —, ce qui
    # porte M à 115,1 points au lieu de 113,4 : un pour cent et demi de trop
    # sur la marche la plus haute du barème. La fiche ne porte qu'un
    # montant, et c'est celui-là ; le jour où l'AVTS entrera dans le dépôt,
    # c'est ici qu'elle se substituera.
    avts = (periode.pension_forfaitaire_annuelle or 0.0) * moteur.macro.coefficient_prix(
        periode.pension_forfaitaire_annee or annee, annee
    )
    # Le minimum en vigueur au 1er janvier de l'année : R. 732-71 ne dit pas
    # à quelle date le lire.
    minimum_contributif, _, _, _ = moteur.minimum_contributif.valeurs(annee)
    maximum = (0.5 * pass_annuel - avts) / (37.5 * valeur_point)
    if revenu <= 400 * smic:
        points = 15.0
    elif revenu <= 800 * smic:
        points = min(30.0, 15.0 + 15.0 * (revenu - 400 * smic) / (400 * smic))
    elif revenu <= 2 * minimum_contributif or pass_annuel <= 2 * minimum_contributif:
        points = 30.0
    else:
        points = min(maximum, 30.0 + (maximum - 30.0)
                     * (revenu - 2 * minimum_contributif)
                     / (pass_annuel - 2 * minimum_contributif))
    # « Le nombre de points résultant de l'application des formules énoncées
    # ci-dessus est arrondi au nombre entier le plus proche » (R. 732-71,
    # dernier alinéa ; déjà l'article 8-1 du décret n° 80-808 depuis 1990) :
    # 23 points au plancher de 600 SMIC, et non 22,5.
    return float(math.floor(points + 0.5 + 1e-9))


def points_gratuits(moteur: ScenarioActuel, periode: PeriodeRegime,
                    carriere: Carriere, assurance: dict[str, dict[int, int]],
                    trimestres: int, age_liquidation: float
                    ) -> tuple[float, Fiabilite | None]:
    """Points que ce régime attribue sans cotisation à la liquidation, et
    la fiabilité de la durée requise qui les conditionne.

    La RCO des non-salariés agricoles est née en 2003. Le chef
    d'exploitation qui liquide depuis reçoit « 100 points de retraite
    complémentaire pour chacune des années de chef d'exploitation [...]
    accomplies avant le 1er janvier 2003 », retenues « dans la limite de
    la différence entre trente-sept années et demie et le nombre d'années
    ayant donné lieu à affiliation » à la RCO (D. 732-154). Deux
    conditions, que le III de L. 732-56 prend au 2° de son II : dix-sept
    ans et demi comme chef à la date d'effet, toute la carrière
    (D. 732-151), et le taux plein du régime de base — en réunir la durée
    requise, tous régimes, jusqu'au 31 août 2023 ; l'avoir LIQUIDÉ au taux
    plein depuis, par la durée ou par l'âge (loi n° 2023-270, art. 18, VI).
    Le modèle ne servait aucun de ces points : un chef installé en 1975 et
    parti en 2019 perdait plus de la moitié de sa complémentaire.

    Une année se compte en trimestres validés au régime de base, divisés
    par quatre et bornés aux trimestres civils de l'année. Le modèle ne
    distingue pas l'activité principale de la secondaire : toute année de
    chef compte.
    """
    regle = periode.points_gratuits
    base = moteur.catalogue[regle.regime]
    periode_base = base.periode(
        min(carriere.annee_liquidation, derniere_annee(base)))
    if periode_base is None:
        return 0.0, None

    def valides(code: str, avant: int | None = None) -> int:
        return sum(min(nombre, carriere.plafond_trimestres(annee))
                   for annee, nombre in assurance.get(code, {}).items()
                   if avant is None or annee < avant)

    if valides(regle.regime) < regle.annees_minimum * 4:
        return 0.0, None
    requis, fiabilite = ouvrir.duree_requise(moteur, periode_base, carriere)
    taux_plein = trimestres >= requis
    if (not taux_plein and carriere.date_liquidation.rang
            >= DateMois(*regle.taux_plein_depuis).rang):
        taux_plein = (age_liquidation
                      >= ouvrir.age_taux_plein(moteur, periode_base, carriere))
    if not taux_plein:
        return 0.0, fiabilite
    retenus = min(
        valides(regle.regime, regle.avant),
        max(0.0, regle.annees_maximum * 4 - valides(periode.regime)),
    )
    return regle.points_par_annee * retenus / 4, fiabilite


@dataclass(frozen=True, eq=False)
class Droits:
    """Ce que l'étape écrit. Son schéma :
    ``data/reference/etapes/acquerir_les_droits.yaml``.

    Les crédits de points et de cotisations sont la source ; les comptes par
    régime que la liquidation lit en sont les sommes, faites dans l'ordre des
    crédits, puis réduites par le plafond de la durée, puis augmentées des
    points gratuits.
    """

    carriere: Carriere
    #: Les points crédités, dans l'ordre : régime, année d'acquisition,
    #: points, taux de majoration pour enfants de l'année (ou rien).
    points: tuple[tuple[str, int, float, float | None], ...]
    #: Les cotisations revalorisées : régime, année, montant.
    cotisations: tuple[tuple[str, int, float], ...]
    #: La durée plafonnée : régime, trimestres, ceux d'avant l'âge, retenus.
    plafonds: tuple[tuple[str, float, float, float], ...]
    #: Les points gratuits : par régime, les points et l'année avant laquelle
    #: comptent les années qui les ouvrent.
    gratuits: dict[str, tuple[float, int]]
    #: Les points qui gardent le coefficient d'anticipation pour âge au taux
    #: plein, parmi ceux de ``points`` : régime, année, points. Ce sont ceux
    #: de l'Agirc constitués sur la tranche C jusqu'en 2015
    #: (``PeriodeRegime.points_abattus_a_l_age``).
    abattus: tuple[tuple[str, int, float], ...]
    #: La dernière année qui verse à chaque régime.
    derniere_annee_par_regime: dict[str, int]
    #: La fiabilité des points de chaque régime qui en crédite.
    fiabilite_points: dict[str, Fiabilite]
    #: Les comptes que la liquidation lit.
    points_acquis: dict[str, float]
    majoration_points: dict[str, float]
    points_majores: dict[str, float]
    cumul_cotisations: dict[str, float]
    #: Par régime, la somme de ``abattus``, réduite comme ``points_acquis``
    #: par le plafond de la durée.
    points_abattus: dict[str, float]

    @property
    def codes(self) -> list[str]:
        """Les régimes où un droit est acquis, points ou cotisations."""
        return sorted(set(self.cumul_cotisations) | set(self.points_acquis))

    def donnees(self) -> dict:
        """Les droits, tels que leur schéma les décrit."""
        return {
            "schema_version": SCHEMA_VERSION,
            "personne": self.carriere.personne,
            "regimes": [
                {"regime": code, "derniere_annee": annee,
                 "fiabilite": (self.fiabilite_points[code].name.lower()
                               if code in self.fiabilite_points else None)}
                for code, annee in self.derniere_annee_par_regime.items()],
            "points": [
                {"regime": code, "annee": annee, "points": points, "majoration": taux}
                for code, annee, points, taux in self.points],
            "cotisations": [
                {"regime": code, "annee": annee, "montant": montant}
                for code, annee, montant in self.cotisations],
            "plafonds": [
                {"regime": code, "trimestres": total, "avant_age": avant_age,
                 "retenus": retenus}
                for code, total, avant_age, retenus in self.plafonds],
            "gratuits": [
                {"regime": code, "points": points, "avant": avant}
                for code, (points, avant) in self.gratuits.items()],
            "abattus": [
                {"regime": code, "annee": annee, "points": points}
                for code, annee, points in self.abattus],
        }


def acquerir(moteur: ScenarioActuel, coordination: Coordination, durees: Durees,
             avec_points_gratuits: bool = True) -> Droits:
    """L'étape : les points et les cotisations de chaque année, puis la durée
    qu'un régime plafonne, puis les points attribués sans cotisation.

    ``avec_points_gratuits`` à faux retire ces derniers : la valorisation des
    droits acquis n'en veut pas, puisqu'elle mesure du contributif pur, et la
    cascade des avantages les retire seuls (:meth:`ScenarioActuel.calculer`).
    """
    carriere = coordination.carriere
    annee_liquidation = carriere.annee_liquidation
    age_liquidation = carriere.age_liquidation or 0.0
    # Cotisations cumulées par régime, pour les régimes en points dont on
    # n'a pas le prix d'achat du point ; points acquis pour les autres.
    cotisations: list[tuple[str, int, float]] = []
    # La majoration pour enfants des points de l'Agirc-Arrco dépend de leur
    # année d'ACQUISITION : chaque point y entre avec son taux, et la
    # pension du régime se majore au taux moyen de ses points.
    credits: list[tuple[str, int, float, float | None]] = []
    # Ceux d'entre eux qui gardent le coefficient pour âge au taux plein.
    abattus: list[tuple[str, int, float]] = []

    def crediter(code: str, annee: int, points: float, abattu: bool = False) -> None:
        credits.append((code, annee, points, moteur.majorations_enfants_points.taux(
            code, annee, carriere.nombre_enfants)))
        if abattu:
            abattus.append((code, annee, points))
    fiabilite_points: dict[str, Fiabilite] = {}
    # Trimestres qu'un régime à la durée crédite, et ceux d'entre eux
    # accomplis avant l'âge qui lève son plafond : voir
    # `PeriodeRegime.trimestres_maximum`.
    trimestres_plafonnables: dict[str, list[float]] = {}
    # Dernière année cotisée dans chaque régime : elle désigne, dans une
    # chaîne de succession, la caisse qui liquide.
    derniere_annee_par_regime: dict[str, int] = {}
    # Le chômage aux régimes complémentaires : borne, premier jour validé,
    # taux de la solidarité (`legislation/chomage_complementaires.yaml`).
    chomage = charger_chomage_complementaires(moteur.macro.racine)
    # La date que les lignes ne disent pas : celle de la convention d'une
    # préretraite du FNE, celle de la rupture qui précède une ASS.
    debuts = chomage.debuts(carriere.lignes)
    for ligne, regimes in zip(carriere.lignes, coordination.regimes):
        # Une ligne postérieure à la liquidation décrit une activité
        # exercée APRÈS le départ : elle n'ouvre pas de droits dans la
        # pension qu'on liquide. L'année du départ, elle, ouvre ceux de ses
        # mois qui l'ont précédé — ni zéro ni douze, mais le compte juste.
        part = carriere.part_retenue_ligne(ligne)
        if part <= 0:
            continue
        if not ligne.cotise and not ligne.familles_cotisantes:
            continue
        # Pendant une période indemnisée, seuls les régimes complémentaires
        # encaissent, et sur le salaire d'avant l'interruption.
        base_ligne = ligne.revenu if ligne.cotise else ligne.revenu_reference
        if part < ligne.fraction_annee:
            base_ligne *= part / ligne.fraction_annee
        familles_admises = (
            None if ligne.cotise else set(ligne.familles_cotisantes)
        )
        # Une année de chômage est d'assurance (l'Unédic), de solidarité
        # (l'État) ou de préretraite du FNE (l'État encore) ; ``None`` pour
        # tout le reste, maladie comprise. De 1967 à 1973, une période de
        # moins de trente jours ne se validait pas : le modèle compte en mois,
        # et la règle ne mord que sur une ligne plus courte qu'un mois.
        debut = debuts.get((ligne.annee, ligne.type_periode))
        nature = (None if ligne.cotise
                  else chomage.nature(ligne.type_periode, ligne.annee, debut))
        if nature is not None and not chomage.assez_long(ligne.annee, part):
            continue
        # La préretraite d'une convention conclue depuis le 5 mai 1997 ne
        # vaut des points que sur deux plafonds, la part que l'État finance.
        plafond_fne = chomage.plafond_preretraite(debut) if nature == "fne" else None
        if plafond_fne is not None:
            base_ligne = min(base_ligne, plafond_fne * part
                             * moteur.macro.plafond_securite_sociale(ligne.annee))
        # LES SERVICES PASSÉS : les années d'avant la généralisation de
        # l'Arrco à un statut, que l'institution valide sans cotisation
        # (`Affiliations.services_passes`) — en Nouvelle-Calédonie avant 1995,
        # à Saint-Pierre-et-Miquelon avant 1988. Ils valent les points d'une
        # année cotisée, mais à une pension prise depuis la généralisation
        # seulement : avant, le régime n'existait pas pour ce statut, et le
        # modèle lui servait trente-quatre ans d'Arrco calédonien.
        services, generalisation = moteur.affiliations.services_passes(
            ligne.affiliation, ligne.annee, carriere.date_entree(ligne.affiliation))
        for code in regimes:
            if code not in moteur.catalogue:
                continue
            regime = moteur.catalogue[code]
            if (familles_admises is not None
                    and regime.famille not in familles_admises):
                continue
            if code in services:
                if annee_liquidation < generalisation:
                    continue
                # Le taux de la généralisation, la pesée des anciens salariés
                # et des retraités : rien de cela n'est lu (fiche
                # `services_passes_outre_mer`), les points sont estimés.
                fiabilite_points[code] = min(
                    fiabilite_points.get(code, Fiabilite.CERTIFIEE), Fiabilite.ESTIMEE)
            # LE PREMIER JOUR VALIDÉ. Les complémentaires ne valident le
            # chômage que depuis le 1er octobre 1967, l'Ircantec depuis le
            # 1er août 1977 ; l'année du premier jour n'en compte que les
            # mois qui le suivent. Le modèle n'avait pas de date jusqu'au
            # 3 octobre 2026 : une année chômée valait des points dès 1947 à
            # l'Agirc et dès 1961 à l'Arrco. Le salarié agricole, que
            # l'assurance chômage ne couvre que depuis le 1er avril 1974, n'a
            # rien avant.
            validee = 1.0
            if nature is not None:
                validee = chomage.part_validee(code, ligne.annee, ligne.affiliation)
                if validee <= 0:
                    continue
            derniere_annee_par_regime[code] = max(
                derniere_annee_par_regime.get(code, 0), ligne.annee
            )
            for periode in regime.periodes_actives(ligne.annee):
                # BARÈME D'UN AUTRE RÉGIME : une tranche que tous les
                # affiliés ne cotisent pas forme une fiche à part, dont les
                # points restent ceux du régime d'origine. Voir `points_de`.
                bareme = periode.points_de or code
                # Les bornes d'assiette et le repère en points sont
                # ANNUELS : une année incomplète ne les atteint qu'à
                # proportion de ses mois, comme le plafond lui-même.
                pass_annuel = (
                    moteur.macro.plafond_securite_sociale(ligne.annee) * part
                )
                borne_basse, borne_haute = periode.bornes_assiette_en_euros(
                    moteur.macro.plafond_securite_sociale(ligne.annee)
                )
                if part < 1.0:
                    borne_basse *= part
                    borne_haute = (None if borne_haute is None
                                   else borne_haute * part)
                # Traitement seul, primes seules — celles du RAFP dans la
                # limite de 20 % du traitement : voir `part_du_revenu`.
                base = periode.part_du_revenu(base_ligne, ligne.part_primes)
                if (ligne.revenu_retabli > 0
                        and periode.assiette != "primes_uniquement"):
                    # Une année RÉTABLIE : l'Ircantec valide le
                    # traitement de l'année, les primes restent au RAFP.
                    base = base_ligne * (1.0 - ligne.part_primes)
                # L'assiette de la CAVAMAC est faite des commissions
                # versées par les compagnies, celle de la CPRN des produits
                # de l'office : le facteur les reconstitue depuis le
                # revenu, avant les bornes. Voir `PeriodeRegime`.
                if periode.assiette_facteur_revenu is not None:
                    base *= periode.assiette_facteur_revenu
                # Le marin cotise sur le salaire forfaitaire de sa
                # catégorie : voir `Compte.cotisation_annuelle`.
                if periode.assiette_grille:
                    forfait_grille = moteur.grilles.forfait(
                        periode.assiette_grille, ligne.annee,
                        ligne.revenu_annualise,
                        lambda a: salaire_moyen_annuel(moteur.macro, a),
                    )
                    if forfait_grille is not None:
                        base = forfait_grille[0] * part
                # L'assiette minimale du régime de base d'un libéral :
                # 450 SMIC horaires depuis 2023 (D. 642-4), qui ouvrent
                # les points que ce montant ouvrirait.
                base = max(base, assiette_minimale(moteur, (code,), ligne))
                plafond = base if borne_haute is None else borne_haute
                assiette = max(0.0, min(base, plafond) - borne_basse)
                repere = periode.repere_assiette(
                    pass_annuel, moteur.macro.smic_horaire(ligne.annee)
                ) * (part if periode.assiette_repere_smic is not None else 1.0)
                if periode.assiette_forfaitaire:
                    # Assiette FORFAITAIRE : le régime des cultes cotise sur
                    # un forfait égal au SMIC mensuel, quel que soit le
                    # revenu. Inconditionnel, là où `assiette_plancher` ne
                    # relève que les assiettes trop basses.
                    assiette = repere
                elif periode.assiette_plancher and assiette < repere:
                    # Assiette minimale : la complémentaire agricole cotise
                    # sur 1 820 SMIC même quand le revenu est en dessous,
                    # et ouvre donc ses cent points malgré tout.
                    assiette = repere
                if not periode.assiette_forfaitaire:
                    # Assiette minimale en plafonds : la CARPIMKO appelle
                    # depuis 2026 sa cotisation sur un demi-plafond au
                    # moins, et les points suivent ce qui est appelé. Le
                    # plafond est déjà proratisé sur les mois de l'année.
                    assiette = max(assiette,
                                   periode.assiette_minimale(pass_annuel))
                # La cotisation forfaitaire s'ajoute à la proportionnelle,
                # et elle est due quel que soit le revenu — cf.
                # `Compte._cotisation_forfaitaire`, même convention
                # d'indexation sur les prix.
                forfait = 0.0
                if periode.cotisation_forfaitaire_euros is not None:
                    reference = (periode.cotisation_forfaitaire_annee
                                 or ligne.annee)
                    forfait = (periode.cotisation_forfaitaire_euros
                               * moteur.macro.coefficient_prix(
                                   reference, ligne.annee))
                cotisation = (assiette * periode.taux_cotisation_retraite
                              + forfait)
                # COTISATION PAR CLASSES : la Cipav, avant 2023, appelait
                # le montant du palier où tombait le revenu, et non une
                # fraction d'une assiette. Ce montant achète des points
                # comme n'importe quelle cotisation — « 3 600 € / 47,40 € =
                # 75,9 points », écrit la caisse —, et c'est donc ici, avant
                # la conversion, qu'il se substitue.
                if periode.cotisation_par_classes:
                    millesime = moteur.classes.annee_grille(code, ligne.annee)
                    reference = (
                        0.0 if millesime is None
                        else moteur.macro.plafond_securite_sociale(millesime)
                    )
                    par_classe = (
                        None if reference <= 0
                        else moteur.classes.cotisation(
                            code, ligne.annee, base,
                            moteur.macro.plafond_securite_sociale(ligne.annee)
                            / reference,
                        )
                    )
                    if par_classe is not None:
                        cotisation = par_classe[0] * part
                if periode.bareme_points == "msa_proportionnelle":
                    # BARÈME NOMMÉ : le nombre de points ne se lit ni dans
                    # un prix d'achat ni dans un repère d'assiette, mais
                    # dans un escalier à quatre marches que R. 732-71 écrit
                    # en SMIC, en minimum contributif et en plafond. Voir
                    # `_points_msa`. C'est l'ASSIETTE qui y entre, et non le
                    # revenu : la cotisation qui ouvre ces points est due
                    # sur six cents SMIC horaires au moins (D. 731-120, 2°)
                    # et sur un plafond au plus, et ce sont ces deux bornes
                    # qui font les « 23 à 113 points ».
                    echelle, fiabilite_echelle = moteur.conversions_points.echelle(
                        bareme, ligne.annee, annee_liquidation
                    )
                    crediter(code, ligne.annee, (
                        points_msa(moteur, periode, ligne.annee, assiette)
                        * part * echelle
                    ), periode.points_abattus_a_l_age)
                    fiabilite_points[code] = min(
                        fiabilite_points.get(code, Fiabilite.CERTIFIEE),
                        regime.fiabilite, fiabilite_echelle,
                    )
                    continue
                if periode.points_par_trimestre_valide is not None:
                    # POINTS PAR TRIMESTRE VALIDÉ, sans égard au montant.
                    # Le régime de base des libéraux d'avant 2004 ne servait
                    # pas une pension proportionnelle au revenu mais une
                    # ALLOCATION : un quinzième de l'AVTS par année cotisée,
                    # la même pour le notaire et pour le kinésithérapeute.
                    # La réforme de 2003 l'a convertie en points « à raison
                    # de cent points par trimestre » (D. 643-1), et c'est
                    # cette conversion — non l'assiette, qu'on n'a pas —
                    # qui porte le droit d'avant 2004.
                    echelle, fiabilite_echelle = moteur.conversions_points.echelle(
                        bareme, ligne.annee, annee_liquidation
                    )
                    points = (periode.points_par_trimestre_valide
                              * carriere.trimestres_retenus(ligne))
                    if periode.trimestres_maximum is not None:
                        # Le plafond se lit sur toute la durée : on note ici
                        # les trimestres de la ligne, et ceux d'entre eux
                        # qui précèdent l'âge qui le lève. Ils courent
                        # « jusqu'à ce que cet âge soit atteint » : jusqu'au
                        # mois de l'anniversaire, celui où un métier commence
                        # à l'âge dit : entré à la mine à dix-huit ans, on y
                        # a cent quarante-huit trimestres à cinquante-cinq.
                        suivi = trimestres_plafonnables.setdefault(code, [0.0, 0.0])
                        suivi[0] += carriere.trimestres_retenus(ligne)
                        if periode.trimestres_maximum_leve_avant_age is not None:
                            suivi[1] += compter.trimestres_de_la_ligne_entre(
                                carriere, ligne, DateMois(carriere.annee_naissance, 1),
                                carriere.mois_de_l_anniversaire(
                                    periode.trimestres_maximum_leve_avant_age),
                            )
                    if (periode.points_ajustement_par_forfait is not None
                            and forfait > 0):
                        # Les points d'AJUSTEMENT de l'ASV des médecins :
                        # 18 fois la cotisation proportionnelle sur le
                        # forfait, neuf au plus (décret n° 2011-1644,
                        # art. 3). Ils suivent le revenu, là où les 27
                        # points du forfait ne suivent que la durée.
                        ajustement = (periode.points_ajustement_par_forfait
                                      * assiette
                                      * periode.taux_cotisation_retraite
                                      / forfait)
                        if periode.points_ajustement_maximum is not None:
                            ajustement = min(
                                ajustement,
                                periode.points_ajustement_maximum * part)
                        points += ajustement
                    crediter(code, ligne.annee, points * echelle,
                             periode.points_abattus_a_l_age)
                    fiabilite_points[code] = min(
                        fiabilite_points.get(code, Fiabilite.CERTIFIEE),
                        regime.fiabilite, fiabilite_echelle,
                    )
                    continue
                if periode.points_maximum is not None and repere > 0:
                    # Barème écrit en POINTS et non en prix d'achat : le
                    # régime annonce combien de points ouvre une assiette
                    # donnée — 525 points au plafond pour le régime de base
                    # des libéraux, 100 points pour 1 820 SMIC à la
                    # complémentaire agricole. Le nombre de points ne
                    # dépend alors pas du taux de cotisation, et c'est
                    # heureux : ce sont les barèmes qui sont publiés, pas
                    # les prix d'achat.
                    echelle, fiabilite_echelle = moteur.conversions_points.echelle(
                        bareme, ligne.annee, annee_liquidation
                    )
                    crediter(code, ligne.annee,
                             periode.points_maximum * assiette / repere * echelle,
                             periode.points_abattus_a_l_age)
                    fiabilite_points[code] = min(
                        fiabilite_points.get(code, Fiabilite.CERTIFIEE),
                        regime.fiabilite, fiabilite_echelle,
                    )
                    continue
                # Au-delà du dernier barème publié, le prix que le texte du
                # régime prolonge : la valeur d'achat de l'Agirc-Arrco suit le
                # salaire moyen (`ValeursPoint.achat_prolonge`). Ses années ont
                # des points, et non des cotisations au rendement de 2026, qui
                # faisaient suivre les prix au prix d'achat.
                achat = (moteur.valeurs_point.achat_prolonge(
                             bareme, ligne.annee, moteur.macro)
                         if periode.type_calcul in ("points", "mixte") else None)
                if achat is not None:
                    reference, taux_appel, fiabilite_achat = achat
                    # LA SOLIDARITÉ. L'allocation de solidarité spécifique,
                    # l'allocation équivalent retraite et l'allocation
                    # spéciale du FNE valent des points « du taux de calcul
                    # des points de 4 % » depuis 2019 (accord du 17 novembre
                    # 2017, art. 61 à 63), de 4 % à l'Arrco et de 8 % ou 12 %
                    # sur la tranche B de l'Agirc avant : non le taux d'une
                    # année travaillée, que le modèle leur prêtait jusqu'au
                    # 3 octobre 2026 en ne connaissant que le chômage
                    # d'assurance. Sans garantie minimale de points : le guide
                    # réglementaire l'écrit pour l'allocation spéciale du FNE
                    # (« Ces taux doivent s'entendre, depuis 1989, assortis de
                    # la GMP »), non pour l'ASS, validée « seulement sur la
                    # base du taux de 8 % ou de 12 % » (titre VII.3.1.6.2).
                    # L'allocation spéciale du FNE a donc la garantie de son
                    # taux : 60 points à 8 % quand le forfait en achète 120.
                    taux_solidarite = (
                        chomage.taux_solidarite(code, ligne.annee, points=True,
                                                rupture=debut)
                        if nature in ("solidarite", "fne") else None
                    )
                    if taux_solidarite is None:
                        points_annee = cotisation / (taux_appel * reference)
                    else:
                        points_annee = assiette * taux_solidarite / reference
                    garantie = (None if taux_solidarite is not None
                                and nature != "fne"
                                else moteur.valeurs_point.garantie(
                                    bareme, periode, ligne.annee, part,
                                    ligne.quotite, taux_solidarite))
                    # Une année de CHÔMAGE INDEMNISÉ a sa garantie, comme une
                    # année travaillée : l'Agirc valide la période que l'Unédic
                    # indemnise « sur la base du taux minimum applicable à
                    # chaque exercice, assorti de la GMP (garantie minimale de
                    # points) correspondante » (guide réglementaire
                    # Agirc-Arrco, titre VII.3.1.6.2), et l'Unédic lui versait
                    # des « contributions [...] au titre de la garantie
                    # minimale de points » (protocole du 2 janvier 2004,
                    # art. 3). Le plancher en était retiré du 2 octobre 2026 au
                    # même jour : on avait lu l'article 8 bis, dont les
                    # dispositions « concernent les points en tranche B »,
                    # comme s'il excluait la garantie, qui est l'une des
                    # « Cotisations sur la tranche B » de l'article 6, § 2. Un
                    # arrêt maladie reprend, lui, les points de l'année
                    # précédente (art. 8), garantie comprise : le plancher les
                    # rend aussi.
                    if garantie is not None:
                        # Garantie minimale de points de l'Agirc : tout cadre
                        # cotisant en acquiert au moins ce que le forfait de
                        # l'année achète au taux de son entreprise — 144 points
                        # en 1989 à 16 %, 72 au taux minimal de 8 %, 120 de 1999
                        # à 2018 —, même quand sa tranche B est nulle, c'est-à-dire
                        # même quand son salaire ne dépasse pas le plafond de la
                        # Sécurité sociale. La fiche la déclarait ; le moteur ne
                        # la servait pas, et un cadre payé sous le plafond
                        # n'acquérait rien à l'Agirc là où le droit lui donnait
                        # ces points. Ils ne sont pas gratuits : une cotisation
                        # forfaitaire les achète, que le compte notionnel porte
                        # (`ConstructeurCompte._assiette_garantie`), et ils se
                        # proratisent comme elle, sur la durée de présence et
                        # sur la quotité du temps partiel. Le plancher valait
                        # cent vingt points entiers jusqu'au 2 octobre 2026,
                        # même pour une année d'un mois, et même de 1989 à 1996,
                        # quand le forfait en achetait de 136 à 147.
                        garantis = garantie[0] / (taux_appel * reference)
                        if garantis > points_annee:
                            points_annee = garantis
                            fiabilite_achat = min(fiabilite_achat, garantie[1])
                    # Changement d'unité entre l'achat et le service : les
                    # points Arrco d'avant 1999 sont ceux de l'UNIRS, et
                    # valent 0,387464 point du régime unifié. Sans cette
                    # conversion, cent euros cotisés en 1998 produisaient
                    # 30,31 € de pension quand les mêmes cent euros de 1999
                    # n'en produisaient que 11,15 — un facteur 2,7 en une
                    # année, pour une unification qui était neutre.
                    echelle, fiabilite_echelle = moteur.conversions_points.echelle(
                        bareme, ligne.annee, annee_liquidation
                    )
                    crediter(code, ligne.annee, points_annee * validee * echelle,
                             periode.points_abattus_a_l_age)
                    fiabilite_points[code] = min(
                        fiabilite_points.get(code, Fiabilite.CERTIFIEE),
                        fiabilite_achat, fiabilite_echelle,
                    )
                else:
                    cotisations.append((code, ligne.annee, (
                        cotisation
                        * moteur.macro.coefficient_prix(ligne.annee, annee_liquidation)
                    )))

    points_acquis: dict[str, float] = {}
    majoration_points: dict[str, float] = {}
    points_majores: dict[str, float] = {}
    for code, _, points, taux in credits:
        points_acquis[code] = points_acquis.get(code, 0.0) + points
        if taux is not None:
            majoration_points[code] = majoration_points.get(code, 0.0) + points * taux
            points_majores[code] = points_majores.get(code, 0.0) + points
    points_abattus: dict[str, float] = {}
    for code, _, points in abattus:
        points_abattus[code] = points_abattus.get(code, 0.0) + points
    cumul_cotisations: dict[str, float] = {}
    for code, _, montant in cotisations:
        cumul_cotisations[code] = cumul_cotisations.get(code, 0.0) + montant

    plafonds: list[tuple[str, float, float, float]] = []
    # LE PLAFOND DE LA DURÉE, LEVÉ AVANT UN ÂGE. Cent vingt trimestres au
    # plus aux mines, sauf ceux accomplis avant cinquante-cinq ans (article
    # 136 du décret n° 46-2769, article 147 dans sa rédaction de 1974) : les
    # trimestres retenus valent le plus petit du total et du plus grand du
    # plafond et des trimestres d'avant l'âge. Le modèle les comptait tous,
    # et payait au mineur entré à dix-huit ans et parti à soixante-deux ans
    # sept années que la caisse ne liquide pas.
    for code, (total, avant_age) in trimestres_plafonnables.items():
        regime = moteur.catalogue[code]
        periode = regime.periode(min(annee_liquidation, derniere_annee(regime)))
        if periode is None or periode.trimestres_maximum is None or total <= 0:
            continue
        retenus = min(total, max(float(periode.trimestres_maximum), avant_age))
        plafonds.append((code, total, avant_age, retenus))
        if retenus < total and code in points_acquis:
            rapport = retenus / total
            points_acquis[code] *= rapport
            if code in points_abattus:
                points_abattus[code] *= rapport
            if code in majoration_points:
                majoration_points[code] *= rapport
                points_majores[code] *= rapport

    # POINTS GRATUITS : la RCO agricole attribue à la liquidation des
    # points pour les années de chef d'exploitation d'avant sa création.
    # Ils entrent au compte de points du régime comme des points acquis —
    # un chef parti en janvier 2003 n'a encore rien cotisé à la RCO, et
    # c'est ici qu'elle entre dans les régimes liquidés —, et la cascade
    # les isole. Voir :func:`points_gratuits`.
    #: Points attribués, et année avant laquelle comptent les années.
    gratuits_attribues: dict[str, tuple[float, int]] = {}
    if avec_points_gratuits:
        for base, attribuants in moteur.points_gratuits_par_base.items():
            if base not in durees.par_annee["assurance"]:
                continue
            for code in attribuants:
                regime = moteur.catalogue[code]
                periode = regime.periode(
                    min(annee_liquidation, derniere_annee(regime)))
                if periode is None or periode.points_gratuits is None:
                    continue
                gratuits, fiabilite_duree = points_gratuits(
                    moteur, periode, carriere, durees.par_annee["assurance"],
                    durees.trimestres, age_liquidation,
                )
                if gratuits <= 0:
                    continue
                gratuits_attribues[code] = (
                    gratuits, periode.points_gratuits.avant)
                points_acquis[code] = points_acquis.get(code, 0.0) + gratuits
                fiabilite_points[code] = min(
                    fiabilite_points.get(code, Fiabilite.CERTIFIEE),
                    regime.fiabilite,
                    (Fiabilite.CERTIFIEE if fiabilite_duree is None
                     else fiabilite_duree),
                )
    return Droits(
        carriere=carriere, points=tuple(credits), cotisations=tuple(cotisations),
        plafonds=tuple(plafonds), gratuits=gratuits_attribues, abattus=tuple(abattus),
        derniere_annee_par_regime=derniere_annee_par_regime,
        fiabilite_points=fiabilite_points, points_acquis=points_acquis,
        majoration_points=majoration_points, points_majores=points_majores,
        cumul_cotisations=cumul_cotisations, points_abattus=points_abattus,
    )
