"""Tables de mortalité : chargement, calibration, tables de génération.

Trois sources, dans cet ordre de priorité, arbitrées **couple par couple**
(année, sexe, âge) et non en bloc :

1. ``data/reference/mortalite/quotients_periode.csv`` (colonnes
   ``annee,sexe,age,qx``) — les quotients réellement observés. Ils couvrent
   1899-2024, jusqu'à 104 ans avant 1998, puis 98 ans ;
2. ``data/reference/mortalite/quotients_projetes.csv`` — les quotients que
   l'INSEE projette, hypothèse centrale de ses projections de population 2026,
   convertis à l'âge exact : de 2026 à 2125, de 0 à 120 ans. Au-delà de 2125,
   ceux de 2125. Sous l'hypothèse d'espérance de vie basse ou haute
   (``Parametres.hypothese_esperance_vie``), les siens,
   ``quotients_projetes_basse.csv`` ou ``quotients_projetes_haute.csv`` ;
3. partout ailleurs — au-delà du dernier âge observé, et en 2025, que ni
   l'observation ni la projection ne couvrent — une table paramétrique de
   **Gompertz-Makeham**, dont la forme est calée sur les espérances de vie
   publiées à 60 et 65 ans, et le niveau raccordé au dernier quotient observé
   de l'année quand elle en a.

Le point 3 est une approximation assumée : elle donne la bonne espérance de vie
aux âges qui comptent pour la retraite (celle qui pilote le diviseur), mais elle
ne prétend pas décrire la mortalité aux âges jeunes, ni la FORME de la
mortalité aux grands âges. Elle servait aussi aux années projetées jusqu'au
7 octobre 2026 : calée sur deux espérances, elle faisait vivre les très vieux
trop longtemps, de 0,6 à 1,0 an d'espérance de trop à 85 ans, et le point 2 l'y
a remplacée (action 138, étape 7).

**La loi prolonge la table, elle ne la corrige pas.** Ajustée sur elle-même,
elle donnait une queue trop généreuse, et la table raccordée — quotients
observés jusqu'à 84 ans pour les millésimes 1998-2013, loi au-delà — rendait
une espérance à 60 ans jusqu'à 2,5 ans supérieure à celle que publie l'INSEE ;
le diviseur de conversion s'en trouvait surestimé de 5 %. Son niveau s'est
ensuite recalé pour que la table raccordée reproduise l'espérance publiée.
Depuis le 18 octobre 2026, les quotients observés vont jusqu'à 98 ans, la
queue ne pèse presque plus rien, et le recalage poussait le niveau à
l'absurde : son niveau se raccorde désormais au dernier quotient observé, et
la table rend seule l'espérance publiée, à 0,12 an près de 1986 à 2024 — la
différence des deux chaînes de production, l'INSEE arrondissant au dixième
(:func:`_calibrer`).

Force de mortalité retenue :  μ(x) = A + B · exp(k · (x − 60))
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .chargement import Fiabilite, SerieAnnuelle, charger_serie_annuelle
from ..somme import somme_ordonnee

#: Mortalité « accidentelle », indépendante de l'âge (terme de Makeham).
MORTALITE_ACCIDENTELLE = 0.0005

#: Version de la méthode de calibration, qui entre dans l'empreinte de chaque
#: loi mémorisée : la changer invalide toute la mémoire d'un coup. La 3 raccorde
#: le niveau de la loi au dernier quotient observé (18 octobre 2026).
VERSION_CALIBRATION = 3

#: Pas d'intégration numérique, en années. 0,25 an suffit : l'écart avec un pas
#: mensuel est inférieur à 0,01 an sur les espérances calculées, très en deçà de
#: l'incertitude des données d'entrée.
PAS = 0.25

#: Âge terminal des tables.
AGE_TERMINAL = 120.0

#: Les hypothèses d'espérance de vie des projections de population 2026 de
#: l'INSEE, et le fichier des quotients projetés de chacune
#: (``Parametres.hypothese_esperance_vie``). Elles ne diffèrent qu'à partir
#: de 2026 : l'observé est le même sous toutes.
QUOTIENTS_PROJETES = {
    "centrale": "quotients_projetes.csv",
    "basse": "quotients_projetes_basse.csv",
    "haute": "quotients_projetes_haute.csv",
}


@dataclass(frozen=True)
class LoiMortalite:
    """Paramètres de Makeham pour une année et un sexe donnés."""

    a: float
    b: float
    k: float
    annee: int
    sexe: str
    fiabilite: Fiabilite

    def force(self, age: float) -> float:
        return self.a + self.b * math.exp(self.k * (age - 60.0))

    def survie(self, age_debut: float, duree: float) -> float:
        """Probabilité de survivre ``duree`` années à partir de ``age_debut``."""
        if duree <= 0:
            return 1.0
        u = math.exp(self.k * (age_debut - 60.0))
        integrale = self.a * duree + (self.b / self.k) * u * (math.exp(self.k * duree) - 1.0)
        return math.exp(-integrale)

    def esperance(self, age: float) -> float:
        """Espérance de vie résiduelle complète à ``age``, table du moment.

        Intégration incrémentale : la survie cumulée est propagée d'un pas à
        l'autre, ce qui coûte une exponentielle par pas au lieu de deux.
        """
        return _esperance_makeham(self.a, self.b, self.k, age)


def _esperance_makeham(a: float, b: float, k: float, age: float) -> float:
    total = 0.0
    survie = 1.0
    u = math.exp(k * (age - 60.0))
    facteur_pas = math.exp(k * PAS)
    borne = int((AGE_TERMINAL - age) / PAS)
    for _ in range(max(borne, 0)):
        prochaine = survie * math.exp(-(a * PAS + (b / k) * u * (facteur_pas - 1.0)))
        total += 0.5 * (survie + prochaine) * PAS
        survie = prochaine
        u *= facteur_pas
        if survie < 1e-12:
            break
    return total


def _survie_makeham_un_an(a: float, b: float, k: float, age: float) -> float:
    """Probabilité de passer de ``age`` à ``age + 1`` sous la loi paramétrique."""
    u = math.exp(k * (age - 60.0))
    return math.exp(-(a + (b / k) * u * (math.exp(k) - 1.0)))


def _esperance_raccordee(a: float, b: float, k: float, age: float,
                         quotients: dict[int, float] | None) -> float:
    """Espérance de vie du moment de la table RACCORDÉE, année par année.

    C'est exactement ce que rend le modèle : les quotients observés là où ils
    existent, la loi paramétrique partout ailleurs. Sans ``quotients``, elle se
    réduit à l'espérance de la loi seule, au pas d'un an.
    """
    total = 0.0
    survie = 1.0
    courant = float(age)
    while courant < AGE_TERMINAL and survie > 1e-12:
        quotient = quotients.get(int(courant)) if quotients else None
        facteur = ((1.0 - quotient) if quotient is not None
                   else _survie_makeham_un_an(a, b, k, courant))
        prochaine = survie * facteur
        total += 0.5 * (survie + prochaine)
        survie = prochaine
        courant += 1.0
    return total


def _calibrer(e60_cible: float, e65_cible: float, annee: int, sexe: str,
              fiabilite: Fiabilite,
              quotients: dict[int, float] | None = None) -> LoiMortalite:
    """Ajuste (b, k) : la forme sur les espérances publiées, le niveau sur la
    table que la loi prolonge.

    Deux temps. La FORME de la queue — le paramètre k — vient de la calibration
    classique sur la loi seule, où e60 et e65 portent sur toute la plage d'âges
    et le déterminent sans ambiguïté. Sans table observée — en 2025 —, son
    NIVEAU — le paramètre b — en vient aussi. Avec une table, la loi n'en
    prolonge que la queue, au-delà de son dernier âge, et son niveau s'y
    RACCORDE : son quotient au dernier âge observé est celui de la table
    (:func:`_niveau_raccorde`).

    Les deux bissections portent sur des fonctions monotones : à k fixé,
    l'espérance décroît quand b croît ; une fois b calé sur e60, le rapport
    e65/e60 décroît quand k croît.

    **Pourquoi raccorder.** Calibrée sur elle-même, la loi produisait une queue
    trop généreuse — 11,3 ans d'espérance résiduelle à 85 ans pour une femme
    en 2010, là où la cible en implique 7,5 —, et la table que le modèle lit,
    qui s'arrêtait alors à 84 ans de 1998 à 2013, rendait une espérance à
    60 ans de 2,5 ans au-dessus de celle de l'INSEE. Son niveau s'est d'abord
    recalé pour que la table raccordée rende l'espérance publiée. Depuis que
    la table va jusqu'à 98 ans, et 104 avant 1998, la queue ne pèse presque
    plus sur l'espérance à 60 ans : pour en gagner quelques centièmes — que
    l'INSEE arrondit au dixième —, le recalage poussait le niveau à l'absurde,
    multiplié par 700, et tous mouraient à 99 ans, ou ramené à zéro, et plus
    personne ne mourait. Raccordée, la queue s'en tient à ce que la table
    observe, et la table rend seule l'espérance publiée, à 0,12 an près de
    1986 à 2024 (action 138, étape 7). Elle surestime de 5 % en moyenne les
    quotients de 99 à 104 ans que l'INED observe de 1986 à 1997 : une loi de
    Gompertz ne ralentit pas.
    """

    def b_pour(k: float, cible: float) -> float:
        bas, haut = 1e-9, 5.0
        for _ in range(50):
            milieu = math.sqrt(bas * haut)
            if _esperance_raccordee(MORTALITE_ACCIDENTELLE, milieu, k, 60.0,
                                    None) > cible:
                bas = milieu
            else:
                haut = milieu
        return math.sqrt(bas * haut)

    # 1. La FORME de la queue vient de la calibration classique, sur la loi
    #    seule : e60 et e65 y portent sur toute la plage d'âges, et déterminent
    #    k sans ambiguïté.
    ratio_cible = e65_cible / e60_cible
    bas_k, haut_k = 0.02, 0.30
    for _ in range(30):
        k = 0.5 * (bas_k + haut_k)
        b = b_pour(k, e60_cible)
        e60 = _esperance_makeham(MORTALITE_ACCIDENTELLE, b, k, 60.0)
        e65 = _esperance_makeham(MORTALITE_ACCIDENTELLE, b, k, 65.0)
        if e65 / e60 > ratio_cible:
            bas_k = k
        else:
            haut_k = k
    k = 0.5 * (bas_k + haut_k)
    b = b_pour(k, e60_cible)

    # 2. Le NIVEAU de la queue se raccorde à la table qu'elle prolonge, quand
    #    il y en a une.
    raccorde = _niveau_raccorde(k, quotients) if quotients else None
    if raccorde is not None:
        b = raccorde

    return LoiMortalite(MORTALITE_ACCIDENTELLE, b, k, annee, sexe, fiabilite)


def _niveau_raccorde(k: float, quotients: dict[int, float]) -> float | None:
    """Le niveau b dont la loi de pente ``k`` rend, au dernier âge de la table
    dont le quotient ne vaut ni zéro ni un, ce quotient-là ; ``None`` si aucun
    ne s'y prête.

    La survie d'un an de la loi depuis l'âge x vaut
    exp(−A − (b/k)·exp(k(x − 60))·(exp(k) − 1)), qu'on pose égale à 1 − q(x).
    Un quotient de un éteint la table, et la queue n'y sert plus ; un quotient
    sous la mortalité accidentelle ne donnerait pas de niveau positif.
    """
    raccordables = [age for age, quotient in quotients.items() if 0.0 < quotient < 1.0]
    if not raccordables:
        return None
    dernier = max(raccordables)
    force = -math.log(1.0 - quotients[dernier]) - MORTALITE_ACCIDENTELLE
    if force <= 0.0:
        return None
    return force * k / (math.exp(k * (dernier - 60.0)) * (math.exp(k) - 1.0))


def empreinte_calibration(e60: float, e65: float,
                          quotients: dict[int, float] | None) -> str:
    """Ce dont une loi calibrée dépend, résumé en seize caractères.

    Les deux cibles, les quotients observés de l'année — la loi se raccorde à
    leur dernier — et les constantes de la méthode. Une loi n'est
    reprise de la mémoire que si son empreinte est celle que les données
    d'aujourd'hui donneraient.
    """
    contenu = json.dumps(
        [VERSION_CALIBRATION, MORTALITE_ACCIDENTELLE, PAS,
         AGE_TERMINAL, repr(float(e60)), repr(float(e65)),
         sorted((int(age), repr(float(q))) for age, q in (quotients or {}).items())],
        separators=(",", ":"),
    )
    return hashlib.sha256(contenu.encode("utf-8")).hexdigest()[:16]


def serialiser_calibrations(table: dict[str, list]) -> str:
    """Le fichier ``calibrations_mortalite.json``, octet pour octet.

    Un seul format pour ses deux écrivains — ``scripts/construire_donnees.py``
    et :meth:`DonneesMortalite.enregistrer_cache` —, faute de quoi le test de
    fraîcheur du paquet verrait un fichier « périmé » qui ne diffère que par
    ses blancs.
    """
    return json.dumps(table, indent=0, sort_keys=True)


_QUOTIENTS_EN_CACHE: dict[tuple[str, int, int], dict | None] = {}


def _facteur_de_l_age(facteurs: tuple[tuple[int, float], ...], age: int) -> float:
    """Le facteur de la tranche où tombe ``age``, dans des facteurs par
    tranche d'âge ``((âge, facteur), …)`` : celui du dernier âge de début qui
    ne le dépasse pas, le premier en deçà."""
    retenu = facteurs[0][1]
    for debut, facteur in facteurs[1:]:
        if age < debut:
            break
        retenu = facteur
    return retenu


class DonneesMortalite:
    """Tables du moment et tables de génération pour les deux sexes."""

    SEXES = ("H", "F")

    def __init__(self, racine: Path, poids_unisexe: tuple[float, float] = (0.5, 0.5),
                 cache_disque: bool = True, hypothese: str = "centrale") -> None:
        if hypothese not in QUOTIENTS_PROJETES:
            raise ValueError(
                f"hypothèse d'espérance de vie inconnue : {hypothese!r} "
                f"(connues : {', '.join(QUOTIENTS_PROJETES)})")
        self.racine = racine
        self.poids_unisexe = poids_unisexe
        #: L'hypothèse d'espérance de vie des années projetées.
        self.hypothese = hypothese
        self._chemin_cache = racine / "derive" / "calibrations_mortalite.json"
        self._cache_disque = cache_disque
        self._cache: dict[str, list[float]] = {}
        self._cache_modifie = False
        if cache_disque and self._chemin_cache.exists():
            try:
                self._cache = json.loads(self._chemin_cache.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._cache = {}
        chemin = racine / "reference" / "mortalite" / "esperances_vie.csv"
        self._e60: dict[str, SerieAnnuelle] = {}
        self._e65: dict[str, SerieAnnuelle] = {}
        for sexe in self.SEXES:
            self._e60[sexe] = charger_serie_annuelle(
                chemin, "valeur", nom=f"e60_{sexe}", interpolation="lineaire",
                filtre={"sexe": sexe, "mesure": "e60"},
            )
            self._e65[sexe] = charger_serie_annuelle(
                chemin, "valeur", nom=f"e65_{sexe}", interpolation="lineaire",
                filtre={"sexe": sexe, "mesure": "e65"},
            )
        self._quotients_observes = self._charger_quotients("quotients_periode.csv")
        self._quotients_projetes = self._charger_quotients(QUOTIENTS_PROJETES[hypothese])
        if self._quotients_projetes is None and hypothese != "centrale":
            # Sans sa table, une variante retomberait sur la loi, calée sur les
            # espérances de la centrale : la centrale, sous un autre nom.
            raise FileNotFoundError(
                f"{QUOTIENTS_PROJETES[hypothese]} absent de "
                f"{racine / 'reference' / 'mortalite'} : l'hypothèse "
                f"d'espérance de vie {hypothese} n'a pas de table")
        annees_projetees = sorted({annee for annee, _ in self._quotients_projetes or {}})
        #: Les années que couvrent les quotients projetés ; au-delà de la
        #: dernière, ce sont les siens qui servent, comme la loi paramétrique
        #: s'en tient aux espérances de la dernière année de sa série.
        self.annees_projetees: tuple[int, int] | None = (
            (annees_projetees[0], annees_projetees[-1]) if annees_projetees else None)
        self._populations = self._charger_populations()
        self._facteurs: dict[tuple[str, str], float] = {}
        self._facteurs_par_age: dict[tuple[str, str], tuple[tuple[int, float], ...]] = {}

    # -- populations particulières ------------------------------------------

    def _charger_populations(self) -> dict[str, dict[str, tuple[int, float, float | None]]]:
        """Les espérances de vie à 65 ans publiées pour des populations
        particulières : ``{population: {sexe: (annee, e65, e65_ensemble)}}``.

        Trois fichiers. ``esperances_vie_populations.csv`` porte ce qu'un
        régime publie pour ses pensionnés, sans ensemble de référence : la
        valeur est calée telle quelle sur la table générale de l'année.
        ``esperances_vie_pensions_cnav.csv`` fait de même des retraités du
        régime général par type de pension — normale, pour inaptitude,
        d'ex-invalide —, que la Cnav publie de 62 à 85 ans : chaque âge
        publié y cale sa tranche (:meth:`facteurs_par_age`), et l'espérance à
        65 ans reste celle que rend :meth:`esperance_publiee`.
        ``esperances_vie_niveau_de_vie.csv`` porte les vingtiles de niveau de
        vie de l'INSEE, avec l'« ensemble » de la même étude : un vingtile
        est calé sur son RAPPORT à cet ensemble, appliqué à la table
        générale, parce que l'ensemble de l'étude vit un à trois dixièmes
        de moins que la population générale certifiée (champ et méthode de
        l'échantillon démographique permanent). Seule la dernière période
        publiée sert de population.
        """
        table: dict[str, dict[str, tuple[int, float, float | None]]] = {}
        par_age: dict[tuple[str, str, int], dict[int, float]] = {}
        for nom in ("esperances_vie_populations.csv", "esperances_vie_pensions_cnav.csv"):
            chemin = self.racine / "reference" / "mortalite" / nom
            if not chemin.exists():
                continue
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    par_age.setdefault(
                        (ligne["population"], ligne["sexe"], int(ligne["annee"])), {},
                    )[int(ligne["mesure"].removeprefix("e"))] = float(ligne["valeur"])
                    if ligne["mesure"] != "e65":
                        continue
                    table.setdefault(ligne["population"], {})[ligne["sexe"]] = (
                        int(ligne["annee"]), float(ligne["valeur"]), None,
                    )
        #: Les populations publiées à plusieurs âges, l'année de leur espérance
        #: à 65 ans : ``{population: {sexe: (annee, {âge: espérance})}}``.
        self._esperances_par_age: dict[str, dict[str, tuple[int, dict[int, float]]]] = {}
        for population, sexes in table.items():
            for sexe, (annee, _, _) in sexes.items():
                esperances = par_age[(population, sexe, annee)]
                if len(esperances) > 1:
                    self._esperances_par_age.setdefault(population, {})[sexe] = (
                        annee, esperances)
        chemin = self.racine / "reference" / "mortalite" / "esperances_vie_niveau_de_vie.csv"
        self._niveaux_de_vie: dict[int, float] = {}
        if chemin.exists():
            lues: list[dict] = []
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                lues = [l for l in csv.DictReader(lignes) if l["mesure"] == "e65"]
            if lues:
                derniere = max(int(l["annee"]) for l in lues)
                recentes = [l for l in lues if int(l["annee"]) == derniere]
                ensemble = {l["sexe"]: float(l["valeur"]) for l in recentes
                            if int(l["vingtile"]) == 0}
                for l in recentes:
                    vingtile = int(l["vingtile"])
                    if vingtile == 0:
                        continue
                    table.setdefault(f"niveau_de_vie_v{vingtile:02d}", {})[l["sexe"]] = (
                        derniere, float(l["valeur"]), ensemble[l["sexe"]],
                    )
                    if l["niveau_de_vie_mensuel"]:
                        self._niveaux_de_vie[vingtile] = float(l["niveau_de_vie_mensuel"])
                self._annee_niveaux_de_vie = derniere
        return table

    @property
    def annee_niveaux_de_vie(self) -> int | None:
        """L'année dont les niveaux de vie des vingtiles sont les euros."""
        return getattr(self, "_annee_niveaux_de_vie", None)

    def population_niveau_de_vie_euros(self, montant_mensuel: float) -> str | None:
        """Le vingtile dont le niveau de vie mensuel moyen publié est le plus
        proche d'un montant, en euros de :attr:`annee_niveaux_de_vie`."""
        if not self._niveaux_de_vie:
            return None
        vingtile = min(self._niveaux_de_vie,
                       key=lambda v: abs(self._niveaux_de_vie[v] - montant_mensuel))
        return f"niveau_de_vie_v{vingtile:02d}"

    @property
    def populations(self) -> tuple[str, ...]:
        """Les populations dont une espérance de vie est publiée."""
        return tuple(sorted(self._populations))

    def esperance_publiee(self, population: str, sexe: str) -> tuple[int, float]:
        """L'année d'observation et l'espérance à 65 ans publiées pour une
        population et un sexe."""
        annee, valeur, _ = self._reference_population(population, sexe)
        return annee, valeur

    def _reference_population(self, population: str, sexe: str) -> tuple[int, float, float | None]:
        try:
            return self._populations[population][sexe]
        except KeyError:
            raise KeyError(
                f"population inconnue : {population!r} pour le sexe {sexe!r} "
                f"(connues : {self.populations})"
            ) from None

    def cible_population(self, population: str, sexe: str) -> tuple[int, float]:
        """L'espérance à 65 ans que le facteur doit reproduire sur la table
        générale de l'année : la valeur publiée telle quelle, ou, quand
        l'étude publie son propre ensemble, la valeur publiée dans le rapport
        où elle est à cet ensemble."""
        annee, valeur, ensemble = self._reference_population(population, sexe)
        if ensemble is None:
            return annee, valeur
        generale = self._courbe_brute(65.0, float(annee), sexe, False, 1.0)
        e65 = somme_ordonnee(0.5 * (generale[t] + generale[t + 1]) for t in range(len(generale) - 1))
        return annee, valeur * e65 / ensemble

    def population_niveau_de_vie(self, rapport_au_moyen: float) -> str | None:
        """Le vingtile de niveau de vie où un rapport au niveau moyen place
        quelqu'un — la convention qui rattache un cas type par son salaire.

        Le cas type est placé au rang où son SALAIRE le place par rapport au
        salaire moyen : son niveau de vie est supposé valoir ce rapport fois
        le niveau de vie moyen (la moyenne des vingt vingtiles), et il reçoit
        le vingtile dont le niveau de vie moyen publié est le plus proche.
        C'est une convention, écrite dans docs/methodologie.md §5, pas une
        mesure : le niveau de vie est celui d'un ménage, par unité de
        consommation, et un salaire n'en dit qu'une partie.
        """
        if not self._niveaux_de_vie:
            return None
        moyen = somme_ordonnee(self._niveaux_de_vie.values()) / len(self._niveaux_de_vie)
        return self.population_niveau_de_vie_euros(rapport_au_moyen * moyen)

    def facteur_population(self, population: str, sexe: str) -> float:
        """Le facteur sur la force de mortalité qui donne à cette population
        son espérance de vie publiée.

        La survie de chaque cellule (âge, année) de la table générale est
        élevée à cette puissance : un facteur inférieur à un allonge la vie.
        Il est calé sur la table DU MOMENT de l'année observée, telle que le
        modèle la lit — quotients observés compris —, pour que l'espérance à
        65 ans de la table corrigée soit celle que le régime publie ; puis il
        est tenu constant sur toutes les années, faute d'observation
        ailleurs. La calibration est une bissection sur une fonction
        monotone : plus le facteur est petit, plus on vit longtemps.

        Une population publiée à plusieurs âges n'a pas de facteur unique :
        elle en a un par tranche d'âge (:meth:`facteurs_par_age`).
        """
        cle = (population, sexe)
        memorise = self._facteurs.get(cle)
        if memorise is not None:
            return memorise
        if self._publiee_par_age(population, sexe):
            raise ValueError(
                f"population {population!r} publiée à plusieurs âges pour le sexe "
                f"{sexe!r} : ses facteurs sont par tranche d'âge (facteurs_par_age)")
        annee, cible = self.cible_population(population, sexe)
        facteur = self._caler(65.0, annee, sexe, cible)
        self._facteurs[cle] = facteur
        return facteur

    def _publiee_par_age(self, population: str, sexe: str) -> bool:
        return sexe in self._esperances_par_age.get(population, {})

    def _caler(self, age: float, annee: int, sexe: str, cible: float,
               plus_ages: tuple[tuple[int, float], ...] = ()) -> float:
        """Le facteur qui rend ``cible`` comme espérance à ``age`` sur la table
        du moment de ``annee`` : dès ``age``, ou jusqu'à la première tranche de
        ``plus_ages``, déjà calées. Une bissection sur une fonction monotone :
        plus le facteur est petit, plus on vit longtemps."""
        def esperance(facteur: float) -> float:
            facteurs = ((0, facteur), *plus_ages) if plus_ages else facteur
            courbe = self._courbe_brute(age, float(annee), sexe, False, facteurs)
            return somme_ordonnee(0.5 * (courbe[t] + courbe[t + 1]) for t in range(len(courbe) - 1))

        bas, haut = 0.05, 8.0
        for _ in range(60):
            milieu = math.sqrt(bas * haut)
            if esperance(milieu) > cible:
                bas = milieu
            else:
                haut = milieu
        return math.sqrt(bas * haut)

    def facteurs_par_age(self, population: str, sexe: str) -> tuple[tuple[int, float], ...]:
        """Les facteurs sur la force de mortalité d'une population, par tranche
        d'âge : ``((âge, facteur), …)``, chacun valant de son âge au suivant,
        le premier dès la naissance, le dernier jusqu'au bout de la table.

        Une population publiée au seul âge de 65 ans n'a qu'une tranche, son
        facteur (:meth:`facteur_population`). Une population publiée à
        plusieurs âges — les types de pension de la Cnav, de 62 à 85 ans — a
        une tranche par âge publié : de 62 à 65 ans, la première, prolongée
        avant 62 ; à partir de 85, la dernière. Elles se calent de la plus
        âgée à la plus jeune, chacune sur l'espérance publiée à son âge, sur la
        table du moment de l'année observée, les plus âgées étant déjà calées :
        la table corrigée rend chaque espérance publiée. Puis elles sont tenues
        constantes sur toutes les années, comme le facteur unique.

        LE FACTEUR UNIQUE NE SUIVAIT PAS L'ÂGE (action 138, étape 7). Calé à
        65 ans, il rendait l'espérance des inaptes de la Cnav à 62 ans à quatre
        dixièmes près ; mais leur surmortalité s'éteint avec l'âge, et il les
        faisait mourir trop vite au-delà de 80 ans, où la Cnav les voit
        rejoindre la population générale : 4,8 ans à 85 ans pour les hommes,
        quand elle en mesure 6,3. Prisme leur applique des quotients à chaque
        âge ; la Cnav n'en publie que six espérances, et la tranche n'en
        suppose pas davantage.
        """
        cle = (population, sexe)
        memorises = self._facteurs_par_age.get(cle)
        if memorises is not None:
            return memorises
        if not self._publiee_par_age(population, sexe):
            facteurs: tuple[tuple[int, float], ...] = (
                (0, self.facteur_population(population, sexe)),)
        else:
            annee, esperances = self._esperances_par_age[population][sexe]
            ages = sorted(esperances)
            facteurs = ()
            for rang in range(len(ages) - 1, -1, -1):
                age = ages[rang]
                facteur = self._caler(float(age), annee, sexe, esperances[age], facteurs)
                facteurs = ((0 if rang == 0 else age, facteur), *facteurs)
        self._facteurs_par_age[cle] = facteurs
        return facteurs

    def facteurs_populations(self) -> dict[str, float]:
        """Tous les facteurs uniques, sous la clé ``population|sexe`` — ce que
        le paquet de données transporte pour que le navigateur ne recalibre
        rien. Les populations publiées à plusieurs âges n'y sont pas : le
        portage ne sert qu'un facteur par population, celui du diviseur, et
        seul le coût, que le navigateur ne calcule pas, fait vivre les types de
        pension de la Cnav (``CasType.mortalite``)."""
        return {
            f"{population}|{sexe}": self.facteur_population(population, sexe)
            for population in self.populations
            for sexe in self.SEXES
            if sexe in self._populations[population]
            and not self._publiee_par_age(population, sexe)
        }

    # -- tables réelles, si présentes ---------------------------------------

    def _charger_quotients(self, nom: str) -> dict[tuple[int, str], dict[int, float]] | None:
        """Une table de quotients ``(annee, sexe) -> age -> qx``, observée ou
        projetée, ou ``None`` si le fichier manque."""
        chemin = self.racine / "reference" / "mortalite" / nom
        if not chemin.exists():
            return None
        # Ces fichiers font vingt-cinq mille lignes chacun et se relisaient une
        # fois par jeu de données reconstruit — trente-cinq fois pour les seuls
        # témoins. La table est partagée, non copiée : tout ce qui la touche la
        # lit (`in`, `.get`), ici comme dans `LoiMortalite`.
        etat = chemin.stat()
        cle_fichier = (str(chemin), etat.st_mtime_ns, etat.st_size)
        if cle_fichier in _QUOTIENTS_EN_CACHE:
            return _QUOTIENTS_EN_CACHE[cle_fichier]
        table: dict[tuple[int, str], dict[int, float]] = {}
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                cle = (int(ligne["annee"]), ligne["sexe"])
                table.setdefault(cle, {})[int(ligne["age"])] = float(ligne["qx"])
        resultat = table or None
        _QUOTIENTS_EN_CACHE[cle_fichier] = resultat
        return resultat

    @property
    def utilise_tables_reelles(self) -> bool:
        return self._quotients_observes is not None

    # -- tables du moment ----------------------------------------------------

    @lru_cache(maxsize=None)
    def loi(self, annee: int, sexe: str) -> LoiMortalite:
        """Loi de mortalité du moment pour une année civile et un sexe.

        Les paramètres calibrés sont mémorisés sur disque
        (``data/derive/calibrations_mortalite.json``) : la calibration est
        déterministe, la refaire à chaque exécution ne coûterait que du temps.
        Chaque loi y porte l'empreinte de ses entrées (:func:`empreinte_calibration`),
        et n'est reprise que si ces entrées n'ont pas changé.
        """
        annee_bornee = max(
            self._e60[sexe].premiere_annee,
            min(annee, self._e60[sexe].derniere_annee),
        )
        e60 = self._e60[sexe].brut(annee_bornee)
        e65 = self._e65[sexe].brut(annee_bornee)
        fiabilite = min(e60.fiabilite, e65.fiabilite)
        if annee != annee_bornee:
            fiabilite = Fiabilite.ESTIMEE

        cle = f"{annee_bornee}|{sexe}"
        quotients = (self._quotients_observes or {}).get((annee_bornee, sexe))
        empreinte = empreinte_calibration(e60.valeur, e65.valeur, quotients)
        memorise = self._cache.get(cle)
        # UNE LOI MÉMORISÉE NE VAUT QUE POUR LES DONNÉES DONT ELLE EST TIRÉE.
        # La mémoire était indexée sur la seule clé « année|sexe » : quand les
        # espérances de vie projetées ont été remplacées par celles de l'INSEE,
        # les lois de 2025 à 2080 sont restées calées sur les anciennes cibles
        # — jusqu'à 1,1 an d'espérance à 65 ans de trop —, et le modèle comme le
        # site s'en sont servis sans que rien le dise, les tests construisant
        # leur table sans cette mémoire. Chaque loi porte désormais l'empreinte
        # de ses entrées, et une empreinte qui ne correspond plus la périme.
        if memorise is not None and len(memorise) == 3 and memorise[2] == empreinte:
            b, k, _ = memorise
            return LoiMortalite(MORTALITE_ACCIDENTELLE, b, k, annee, sexe, fiabilite)

        loi = _calibrer(
            e60.valeur, e65.valeur, annee, sexe, fiabilite, quotients=quotients,
        )
        self._cache[cle] = [loi.b, loi.k, empreinte]
        self._cache_modifie = True
        return loi

    def empreinte(self, annee: int, sexe: str) -> str:
        """L'empreinte des entrées de la calibration d'une année et d'un sexe."""
        annee_bornee = max(
            self._e60[sexe].premiere_annee,
            min(annee, self._e60[sexe].derniere_annee),
        )
        return empreinte_calibration(
            self._e60[sexe].brut(annee_bornee).valeur,
            self._e65[sexe].brut(annee_bornee).valeur,
            (self._quotients_observes or {}).get((annee_bornee, sexe)),
        )

    def table_calibrations(self) -> dict[str, list]:
        """Les lois de toutes les années de la série, calibrées ou relues.

        C'est le contenu de ``data/derive/calibrations_mortalite.json`` tel que
        ``scripts/construire_donnees.py`` l'écrit : une entrée par année de la
        série d'espérances de vie et par sexe, et rien d'autre — une entrée
        orpheline d'une série plus longue ne survit pas à la reconstruction.
        """
        table: dict[str, list] = {}
        for sexe in self.SEXES:
            serie = self._e60[sexe]
            for annee in range(serie.premiere_annee, serie.derniere_annee + 1):
                self.loi(annee, sexe)
                cle = f"{annee}|{sexe}"
                table[cle] = list(self._cache[cle])
        return table

    def enregistrer_cache(self) -> None:
        """Écrit les calibrations sur disque. Sans effet si rien n'a changé."""
        if not (self._cache_disque and self._cache_modifie):
            return
        self._chemin_cache.parent.mkdir(parents=True, exist_ok=True)
        self._chemin_cache.write_text(serialiser_calibrations(self._cache),
                                      encoding="utf-8")
        self._cache_modifie = False

    def _survie_cellule(self, age: int, annee: int, sexe: str) -> float:
        """Survie d'un âge ENTIER au suivant : quotient observé s'il existe,
        sinon quotient projeté, sinon loi paramétrique.

        Au-delà de la dernière année projetée, les quotients de cette année-là :
        la projection de l'INSEE s'arrête en 2125, et la loi paramétrique, qui
        prenait la main, s'en tenait déjà aux espérances de 2125.
        """
        if self._quotients_observes is not None:
            cle = (annee, sexe)
            if cle in self._quotients_observes:
                qx = self._quotients_observes[cle].get(age)
                if qx is not None:
                    return 1.0 - qx
        if self.annees_projetees is not None and annee >= self.annees_projetees[0]:
            table = self._quotients_projetes.get((min(annee, self.annees_projetees[1]), sexe))
            if table is not None:
                qx = table.get(age)
                if qx is not None:
                    return 1.0 - qx
        return self.loi(annee, sexe).survie(float(age), 1.0)

    def survie_annuelle(self, age: float, annee: float, sexe: str,
                        facteur: float | tuple[tuple[int, float], ...] = 1.0) -> float:
        """Probabilité de survivre un an à partir de ``age`` en ``annee``.

        ``facteur`` multiplie la force de mortalité de chaque cellule — la
        survie est élevée à cette puissance. Il vaut un pour la population
        générale ; voir :meth:`facteur_population`. Par tranche d'âge
        (:meth:`facteurs_par_age`), chaque cellule reçoit celui de son âge.

        **L'âge et la date sont fractionnaires, et tous deux comptent.** La
        méthode lisait ``quotients[int(age)]`` : la part OBSERVÉE de la table —
        1986-2024 — était aveugle aux mois, et le diviseur d'un départ à 60 ans
        et onze mois était celui d'un départ à 60 ans tout rond. La sanction du
        départ anticipé, qui est la moitié du modèle, s'appliquait par marches
        d'un an : 1,7 % de pension d'un coup à chaque anniversaire, et rien
        entre deux.

        **La force de mortalité est supposée constante dans chaque cellule**
        (âge entier × millésime) — l'hypothèse actuarielle usuelle, et la seule
        qui rende la survie continue. Un assuré parti en juillet 2038 à 63 ans
        et 4 mois passe son année de rente dans quatre cellules successives : il
        franchit son anniversaire, puis le 1er janvier. Le trajet est donc
        découpé à ces deux franchissements, et chaque tronçon reçoit la force de
        la cellule qu'il traverse.

        Ce n'est pas lisser entre deux millésimes : c'est répartir l'EXPOSITION
        entre eux. Une table de mortalité reste publiée par millésime, et aucune
        tendance infra-annuelle n'est inventée — on dit seulement combien de
        mois de l'année le cohorte a vécus sous chacune. Sans ce découpage,
        l'année civile sautait d'un bloc au 1er janvier quand l'âge, lui,
        avançait mois par mois : le diviseur REMONTAIT à cette date, et partir
        un mois plus tard rallongeait la durée de service attendue.
        """
        age_entier, part_age = math.floor(age), age - math.floor(age)
        annee_entiere, part_annee = math.floor(annee), annee - math.floor(annee)
        par_age = isinstance(facteur, tuple)
        if part_age <= 1e-9 and part_annee <= 1e-9:
            cellule = self._survie_cellule(int(age_entier), int(annee_entiere), sexe)
            if par_age:
                facteur = _facteur_de_l_age(facteur, int(age_entier))
            return cellule if facteur == 1.0 else cellule ** facteur

        # Les deux coordonnées avancent à la même vitesse : le trajet franchit
        # l'âge entier suivant en ``1 - part_age`` et le 1er janvier suivant en
        # ``1 - part_annee``. D'où deux coupures au plus, et trois tronçons.
        coupures = sorted(
            {borne for borne in (1.0 - part_age, 1.0 - part_annee)
             if 1e-9 < borne < 1.0 - 1e-9}
        )
        bornes = [0.0, *coupures, 1.0]
        cumul = 0.0
        for debut, fin in zip(bornes, bornes[1:]):
            milieu = 0.5 * (debut + fin)
            age_cellule = int(age_entier + math.floor(part_age + milieu))
            cellule = self._survie_cellule(
                age_cellule,
                int(annee_entiere + math.floor(part_annee + milieu)),
                sexe,
            )
            # Force de mortalité de la cellule, appliquée sur la durée du
            # tronçon : -ln p, puis somme, puis exponentielle. Par tranche
            # d'âge, chaque tronçon reçoit le facteur de la sienne.
            force = (fin - debut) * -math.log(max(cellule, 1e-300))
            cumul += force * _facteur_de_l_age(facteur, age_cellule) if par_age else force
        return math.exp(-cumul) if par_age else math.exp(-cumul * facteur)

    # -- tables de génération ------------------------------------------------

    @lru_cache(maxsize=4096)
    def courbe_survie(self, age_debut: float, annee_debut: float, sexe: str,
                      generation: bool = True,
                      population: str | None = None) -> tuple[float, ...]:
        """Survie cumulée année par année à partir de ``age_debut``.

        ``population`` désigne une population particulière de
        ``esperances_vie_populations.csv`` : sa courbe est celle de la
        population générale, corrigée du facteur que :meth:`facteur_population`
        lui cale, ou, publiée à plusieurs âges, de ceux que
        :meth:`facteurs_par_age` lui cale par tranche. ``None`` est la
        population générale.

        ``annee_debut`` peut porter une fraction : c'est la position de la
        liquidation dans son année civile, ``(mois - 1) / 12``. Elle dit sous
        quel millésime le rentier passe chaque tronçon de son année de rente.

        L'élément d'indice ``t`` est la probabilité d'être encore en vie
        ``t`` années après la liquidation. En table de génération, chaque année
        vécue se voit appliquer la mortalité de l'année civile correspondante,
        et non celle de l'année de liquidation — c'est la définition même d'une
        table de génération. L'ignorer surestime la pension des générations
        récentes, dont la longévité continue de progresser.
        """
        if population is None:
            facteur: float | tuple[tuple[int, float], ...] = 1.0
        elif self._publiee_par_age(population, sexe):
            facteur = self.facteurs_par_age(population, sexe)
        else:
            facteur = self.facteur_population(population, sexe)
        return self._courbe_brute(age_debut, annee_debut, sexe, generation, facteur)

    def _courbe_brute(self, age_debut: float, annee_debut: float, sexe: str,
                      generation: bool,
                      facteur: float | tuple[tuple[int, float], ...]) -> tuple[float, ...]:
        probabilites = [1.0]
        courante = 1.0
        duree = 0
        while age_debut + duree < AGE_TERMINAL and courante > 1e-10:
            # Table du moment : la mortalité de l'année de liquidation est
            # appliquée à tous les âges. Table de génération : chaque année
            # vécue reçoit celle de l'année civile correspondante. Dans les
            # deux cas les quotients OBSERVÉS priment là où ils existent — la
            # table du moment les ignorait, si bien qu'elle ne décrivait pas la
            # même mortalité que celle du calcul par défaut, et qu'un test
            # censé confronter les deux chaînes comparait la calibration à sa
            # propre cible.
            annee = annee_debut + duree if generation else annee_debut
            courante *= self.survie_annuelle(age_debut + duree, annee, sexe, facteur)
            probabilites.append(courante)
            duree += 1
        return tuple(probabilites)

    def courbe_survie_unisexe(self, age_debut: float, annee_debut: float,
                              generation: bool = True,
                              population: str | None = None) -> tuple[float, ...]:
        """Courbe de survie moyenne pondérée des deux sexes.

        On moyenne les FONCTIONS DE SURVIE, pas les espérances : c'est la
        pondération correcte pour une rente servie indifféremment aux hommes et
        aux femmes à partir d'un même capital notionnel.
        """
        poids_h, poids_f = self.poids_unisexe
        ch = self.courbe_survie(age_debut, annee_debut, "H", generation, population)
        cf = self.courbe_survie(age_debut, annee_debut, "F", generation, population)
        longueur = max(len(ch), len(cf))
        return tuple(
            poids_h * (ch[t] if t < len(ch) else 0.0)
            + poids_f * (cf[t] if t < len(cf) else 0.0)
            for t in range(longueur)
        )

    def courbe(self, age_debut: float, annee_debut: float, sexe: str | None,
               generation: bool = True,
               population: str | None = None) -> tuple[float, ...]:
        """Courbe de survie, unisexe si ``sexe`` vaut ``None``, population
        générale si ``population`` vaut ``None``."""
        if sexe is None:
            return self.courbe_survie_unisexe(age_debut, annee_debut, generation, population)
        return self.courbe_survie(age_debut, annee_debut, sexe, generation, population)

    def survie(self, age_debut: float, annee_debut: int, duree: int, sexe: str,
               generation: bool = True) -> float:
        courbe = self.courbe_survie(age_debut, annee_debut, sexe, generation)
        return courbe[duree] if duree < len(courbe) else 0.0

    def esperance_residuelle(self, age: float, annee: float, sexe: str | None = None,
                             generation: bool = True,
                             population: str | None = None) -> float:
        """Espérance de vie résiduelle en années, table de génération par défaut."""
        courbe = self.courbe(age, annee, sexe, generation, population)
        return somme_ordonnee(0.5 * (courbe[t] + courbe[t + 1]) for t in range(len(courbe) - 1))

    def fiabilite(self, annee: float) -> Fiabilite:
        millesime = int(math.floor(annee))
        return min(self.loi(millesime, "H").fiabilite,
                   self.loi(millesime, "F").fiabilite)
