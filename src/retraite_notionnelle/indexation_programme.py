"""L'indexation des pensions servies du programme, pour le seul scénario 6.

Action 186, chantier 5. Le propriétaire a décidé (``docs/feuille_de_route_programme.md``) :

- **41** : α = 1, les retraités portent toute la hausse du nombre de retraités
  par cotisant. Les pensions nouvelles suivent la masse salariale par
  retraité ; celles servies à la bascule, le STOCK, les prix moins cette
  hausse ;
- **44** : un plancher en euros avec rattrapage ;
- **46** : le plancher est une assurance que les retraités paient : ce qu'il
  sert au-dessus de la règle devient une DETTE, portée au taux de la masse
  salariale, reprise sur les hausses suivantes sans jamais faire baisser une
  pension en euros ;
- **49** : la dette se rend le plus vite possible, sur toute la hausse au
  besoin ;
- **28** : ces règles ne valent que pour le scénario 6.

Le nœud : la règle du stock baisse en euros dès que l'inflation reste sous la
hausse du nombre de retraités par cotisant, et sa dette ne se rend pas. Trois
voies neuves sont à chiffrer au modèle, avec la règle d'avant pour comparer.
Elles sont écrites en données (``data/reference/etudes/indexation_scenario_6.yaml``) ;
ce module en fait des coefficients, et ``cout.calculer_cout`` les reçoit par
son option ``indexation_liberale``, sans quoi rien ne change : le défaut du
scénario 6 reste la règle d'avant tant que le propriétaire n'a pas choisi.

CE QUE LE MODULE CHANGE, ET RIEN D'AUTRE. Le coefficient de revalorisation des
pensions du scénario 6 (:meth:`RevalorisationServie.coefficient_stock`, celui de
la proposition), à compter de la bascule : le compte, sa conversion et la
pension de liquidation restent ceux du modèle. Le plancher des COMPTES
(décision 44) n'y est pas : la masse salariale, sa règle, ne baisse en euros
sous aucune des trajectoires étudiées.

LE RAPPORT DES RETRAITÉS AUX COTISANTS est celui du COR, l'ensemble des
régimes, en cotisants par retraité de droit direct
(``decomposition_depense_retraite.csv``, que la décomposition de la page Coût
lit déjà, ``DecompositionDepense``), observé jusqu'en 2024 et projeté par le
scénario de référence jusqu'en 2070. Une crise de l'emploi le dégrade de ce
qu'elle retire aux cotisants ; elle ne touche pas les retraités.

LES EUROS. Le coût compte en euros constants ; le plancher se compte en
euros courants. La trajectoire dit l'inflation sous laquelle le plancher
joue ; la croissance réelle du salaire moyen reste celle des hypothèses, et
une inflation plus basse ne change que ce qui se compte en euros courants.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable, Mapping, Sequence

from .config import RACINE_DONNEES
from .donnees.chargement import charger_yaml
from .donnees.population import Population
from .somme import somme_ordonnee

#: Le fichier des voies et des trajectoires, sous ``data/``.
FICHIER = Path("reference") / "etudes" / "indexation_scenario_6.yaml"

BASES = ("prix", "masse_salariale", "masse_salariale_par_retraite")
PLANCHERS = ("aucun", "sans_rattrapage", "dette", "reserve")
#: Les calibrages que l'étude calcule, et qui ne se calculent pas tels quels.
A_CALIBRER = ("effort_demographique", "calibree")
#: La première année qu'un choc d'inflation touche : la première projetée.
PREMIERE_ANNEE_DES_CHOCS = 2026
GROUPES = ("stock", "nouvelles")


# -- le plancher ----------------------------------------------------------------


@dataclass(frozen=True)
class Chemin:
    """Une pension, année après année, en euros COURANTS, un au départ.

    ``regle`` : ce que la règle seule aurait servi ; ``servi`` : ce que le
    plancher sert ; ``dette`` : ce que le pensionné doit encore, en fraction
    d'une année de sa pension de départ (décision 46) ; ``au_dessus`` : ce que
    le plancher sert au-dessus de la règle, ou en dessous quand la dette se
    rend."""

    regle: tuple[float, ...]
    servi: tuple[float, ...]
    dette: tuple[float, ...]
    au_dessus: tuple[float, ...]


def suivre(hausses_regle: Sequence[float], hausses_masse: Sequence[float],
           plancher: str, reprise: float = 1.0) -> Chemin:
    """La pension sous la règle et son plancher, année après année.

    ``hausses_regle`` et ``hausses_masse`` : ce que la règle et la masse
    salariale font chaque année, en euros courants (−0,02 pour −2 %).

    - ``aucun`` : la pension suit la règle ;
    - ``sans_rattrapage`` : L. 161-25, « si ce coefficient est inférieur à un,
      il est porté à cette valeur » : chaque hausse de la règle s'applique à
      la pension servie, chaque baisse est ignorée et jamais reprise ;
    - ``reserve`` : la pension ne baisse jamais, et retrouve la règle dès que
      la règle repasse au-dessus d'elle ; ce qu'elle sert au-dessus, une
      réserve le paie (voie 1) ;
    - ``dette`` : décisions 44, 46 et 49. Quand la règle passe sous la pension
      servie, la pension est gelée, et l'écart entre dans la dette. La dette
      porte intérêt au taux de la masse salariale. Quand la règle remonte, la
      dette se reprend sur la hausse, au plus ``reprise`` de celle-ci (un :
      toute la hausse au besoin), sans faire baisser la pension en euros.
    """
    if plancher not in PLANCHERS:
        raise ValueError(f"plancher inconnu : {plancher!r} (attendu : {PLANCHERS})")
    if len(hausses_regle) != len(hausses_masse):
        raise ValueError("autant de hausses de la masse salariale que de la règle")
    regle = servi = 1.0
    dette = 0.0
    regles: list[float] = []
    servis: list[float] = []
    dettes: list[float] = []
    au_dessus: list[float] = []
    for hausse, masse in zip(hausses_regle, hausses_masse):
        regle *= 1.0 + hausse
        if plancher == "aucun":
            servi = regle
        elif plancher == "sans_rattrapage":
            servi *= max(1.0, 1.0 + hausse)
        elif plancher == "reserve":
            servi = max(servi, regle)
        else:
            dette *= 1.0 + masse
            if regle < servi:
                dette += servi - regle
            else:
                rendu = min(dette, reprise * (regle - servi))
                servi = regle - rendu
                dette -= rendu
        regles.append(regle)
        servis.append(servi)
        dettes.append(dette)
        au_dessus.append(servi - regle)
    return Chemin(tuple(regles), tuple(servis), tuple(dettes), tuple(au_dessus))


# -- les calibrages -------------------------------------------------------------


def _actualisations(annees: Sequence[int], croissance_masse: Mapping[int, float]
                    ) -> dict[int, float]:
    """Un la première année, puis divisé chaque année par la croissance de la
    masse salariale : le taux du compte, celui de la dette (décision 46)."""
    facteurs: dict[int, float] = {}
    facteur = 1.0
    for rang, annee in enumerate(annees):
        if rang:
            facteur /= croissance_masse[annee]
        facteurs[annee] = facteur
    return facteurs


def baisse_d_effort(masses: Mapping[int, float], regle: Mapping[int, float],
                    croissance_masse: Mapping[int, float]) -> float:
    """La baisse, à la bascule, qui retire au stock ce que la règle lui
    retirerait sur toute sa vie (voie 2).

    ``masses`` : la masse du stock chaque année, sous les prix ; ``regle`` :
    ce que la règle fait d'un euro de la bascule, en euros constants ;
    ``croissance_masse`` : la croissance réelle de la masse salariale, qui
    actualise. La baisse ``c`` égalise les deux valeurs actuelles :
    ``(1 − c) Σ δ M = Σ δ M r``."""
    annees = sorted(masses)
    delta = _actualisations(annees, croissance_masse)
    prix = somme_ordonnee(delta[a] * masses[a] for a in annees)
    sous_la_regle = somme_ordonnee(delta[a] * masses[a] * regle[a] for a in annees)
    return 1.0 - sous_la_regle / prix


def prime_d_equilibre(regle: Mapping[int, float], plancher: Mapping[int, float],
                      croissance_masse: Mapping[int, float]) -> float:
    """La prime qui finance exactement le plancher du stock (voie 1).

    ``regle`` : la masse du stock sous la règle ; ``plancher`` : sous la règle
    et son plancher, sans prime. La répartition paie la règle ; le stock
    touche le plancher diminué de la prime ; la réserve reçoit l'écart, placé
    au taux de la masse salariale. Elle finit à zéro quand
    ``Σ δ (R − (1 − p) F) = 0``."""
    annees = sorted(regle)
    delta = _actualisations(annees, croissance_masse)
    return 1.0 - (somme_ordonnee(delta[a] * regle[a] for a in annees)
                  / somme_ordonnee(delta[a] * plancher[a] for a in annees))


# -- les voies et les trajectoires ----------------------------------------------


@dataclass(frozen=True)
class Regle:
    """La règle d'un groupe de pensions : le stock, ou les nouvelles."""

    base: str
    facteur_demographique: float = 0.0
    plancher: str = "sans_rattrapage"
    reprise: float = 1.0
    #: Une baisse à la bascule, ou ``effort_demographique`` avant calibrage.
    baisse_transition: float | str = 0.0
    #: Une prime à la bascule, mise en réserve, ou ``calibree`` avant calibrage.
    prime: float | str = 0.0

    def __post_init__(self) -> None:
        if self.base not in BASES:
            raise ValueError(f"base inconnue : {self.base!r} (attendu : {BASES})")
        if self.plancher not in PLANCHERS:
            raise ValueError(f"plancher inconnu : {self.plancher!r} (attendu : {PLANCHERS})")
        for nom in ("baisse_transition", "prime"):
            valeur = getattr(self, nom)
            if isinstance(valeur, str) and valeur not in A_CALIBRER:
                raise ValueError(f"{nom} : {valeur!r} n'est pas un calibrage connu")

    @property
    def calibree(self) -> bool:
        return not isinstance(self.baisse_transition, str) and not isinstance(self.prime, str)

    @property
    def niveau_de_bascule(self) -> float:
        """Ce qu'il reste d'un euro du stock à la bascule, après la baisse et
        la prime."""
        return (1.0 - float(self.baisse_transition)) * (1.0 - float(self.prime))


def _regle(donnees: Mapping) -> Regle:
    nombres = {cle: float(valeur) if isinstance(valeur, (int, float)) else valeur
               for cle, valeur in donnees.items()}
    return Regle(**nombres)


@dataclass(frozen=True)
class Voie:
    id: str
    libelle: str
    nouvelles: Regle
    stock: Regle
    note: str = ""

    def calibree(self, baisse: float | None = None, prime: float | None = None) -> "Voie":
        """La même voie, ses calibrages remplacés par ces nombres."""
        stock = self.stock
        if baisse is not None:
            stock = replace(stock, baisse_transition=float(baisse))
        if prime is not None:
            stock = replace(stock, prime=float(prime))
        return replace(self, stock=stock)


@dataclass(frozen=True)
class Trajectoire:
    id: str
    libelle: str
    #: L'inflation de chaque année à compter de 2026 ; ``None`` : celle des
    #: hypothèses de projection.
    inflation: float | None = None
    #: ``(première année, dernière année, taux)`` : l'emploi perd ``taux``
    #: chaque année face au COR, et ne le regagne pas.
    emploi: tuple[int, int, float] | None = None
    note: str = ""

    def facteur_emploi(self, annee: int) -> float:
        """L'emploi de l'année rapporté à celui du COR."""
        if self.emploi is None:
            return 1.0
        debut, fin, taux = self.emploi
        annees = max(0, min(annee, fin) - debut + 1)
        return (1.0 + taux) ** annees

    def inflation_de(self, annee: int, macro) -> float:
        if self.inflation is not None and annee >= PREMIERE_ANNEE_DES_CHOCS:
            return self.inflation
        return macro.inflation(annee)

    @property
    def variante(self) -> str:
        """Le nom de la variante d'emploi, pour ``Population.variante``."""
        return "centrale" if self.emploi is None else f"emploi_{self.id}"


def charger(racine: Path = RACINE_DONNEES) -> tuple[dict[str, Voie], dict[str, Trajectoire]]:
    """Les voies et les trajectoires de l'étude, dans l'ordre du fichier."""
    donnees = charger_yaml(Path(racine) / FICHIER)
    voies = {
        nom: Voie(id=nom, libelle=voie["libelle"], note=voie.get("note", ""),
                  nouvelles=_regle(voie["nouvelles"]), stock=_regle(voie["stock"]))
        for nom, voie in donnees["voies"].items()
    }
    trajectoires = {}
    for nom, trajectoire in donnees["trajectoires"].items():
        emploi = trajectoire.get("emploi")
        trajectoires[nom] = Trajectoire(
            id=nom, libelle=trajectoire["libelle"], note=trajectoire.get("note", ""),
            inflation=(float(trajectoire["inflation"])
                       if trajectoire.get("inflation") is not None else None),
            emploi=(int(emploi["debut"]), int(emploi["fin"]), float(emploi["taux"]))
            if emploi else None)
    return voies, trajectoires


class PopulationSousChoc(Population):
    """La pyramide centrale, et l'emploi d'une trajectoire : ce que la page
    Coût fait d'une variante démographique (action 138, étape 7), le PIB, le
    compte et l'indexation de la proposition suivant ses actifs
    (:meth:`Population.facteur_actifs`), appliqué à une crise de l'emploi. Les
    retraités et la pyramide restent ceux du central."""

    def __init__(self, racine: Path, trajectoire: Trajectoire,
                 hypothese_esperance_vie: str = "centrale") -> None:
        super().__init__(racine, hypothese_esperance_vie)
        self.trajectoire = trajectoire

    @property
    def variante(self) -> str:
        return self.trajectoire.variante

    def facteur_actifs(self, annee: int) -> float:
        return self.trajectoire.facteur_emploi(annee)


def cotisants_par_retraite(racine: Path = RACINE_DONNEES) -> Callable[[int], float]:
    """Les cotisants par retraité de droit direct du COR, l'ensemble des régimes."""
    from .donnees.equilibre import DecompositionDepense

    decomposition = DecompositionDepense(Path(racine) / "reference" / "macro")

    def valeur(annee: int) -> float:
        lue = decomposition.valeur("cotisants_par_retraite", "ensemble", annee)
        if lue is None:
            raise ValueError(f"le COR ne publie pas de cotisants par retraité en {annee}")
        return lue

    return valeur


# -- les coefficients -----------------------------------------------------------


@dataclass(frozen=True)
class Detail:
    """Un euro de pension de départ, année après année : ce qu'il sert en
    euros constants (``servi``), ce que la règle seule aurait servi
    (``regle``), et la dette du plancher, en euros COURANTS de pension de
    départ (``dette``)."""

    servi: dict[int, float] = field(default_factory=dict)
    regle: dict[int, float] = field(default_factory=dict)
    dette: dict[int, float] = field(default_factory=dict)


@dataclass(frozen=True)
class IndexationLiberale:
    """Ce que ``calculer_cout`` reçoit : une voie calibrée, la trajectoire
    sous laquelle son plancher joue, et, pour mesurer un groupe seul, celui
    qu'on garde (``seulement``, ``stock`` ou ``nouvelles``)."""

    voie: Voie
    trajectoire: Trajectoire
    seulement: str | None = None

    def __post_init__(self) -> None:
        if not (self.voie.stock.calibree and self.voie.nouvelles.calibree):
            raise ValueError(
                f"la voie {self.voie.id!r} est à calibrer : "
                f"Voie.calibree(baisse=…, prime=…) d'abord")
        if self.seulement not in (None, *GROUPES):
            raise ValueError(f"groupe inconnu : {self.seulement!r} (attendu : {GROUPES})")

    def verifier(self, population: Population) -> None:
        """Refuse une pyramide dont l'emploi n'est pas celui de la trajectoire :
        la masse salariale du compte en suivrait une, la règle une autre."""
        if population.variante != self.trajectoire.variante:
            raise ValueError(
                f"population {population.variante!r}, trajectoire "
                f"{self.trajectoire.id!r} : construire la population par "
                f"PopulationSousChoc(racine, trajectoire)")

    def appliquer(self, revalorisation, simulateur):
        """Une copie de ``revalorisation`` dont la proposition se revalorise
        sous cette voie ; les autres systèmes gardent la leur. Le même geste
        que :meth:`RevalorisationServie.pour_la_proposition`, qui pose la
        proposition à part."""
        centrale = copy.copy(revalorisation)
        centrale._proposition = PensionsDuProgramme(
            revalorisation.proposition, self, simulateur.macro,
            simulateur.parametres.taux_anticipe_conversion,
            cotisants_par_retraite(simulateur.parametres.racine_donnees))
        return centrale


class PensionsDuProgramme:
    """La revalorisation des pensions du scénario 6 sous une voie.

    Tout ce qu'elle ne redéfinit pas est celui de la revalorisation de la
    proposition qu'elle prolonge (``base``) : avant la bascule, rien ne change.
    """

    def __init__(self, base, indexation: IndexationLiberale, macro,
                 prefinancement: float, cotisants: Callable[[int], float]) -> None:
        self._base = base
        self._indexation = indexation
        self._macro = macro
        self._prefinancement = 1.0 + prefinancement
        self._cotisants = cotisants
        self._chemins: dict[tuple[str, int], Detail] = {}

    def __getattr__(self, nom: str):
        return getattr(self._base, nom)

    @property
    def proposition(self) -> "PensionsDuProgramme":
        return self

    # -- les croissances de l'année, d'un an sur l'autre -----------------------

    def _emploi(self, annee: int) -> float:
        trajectoire = self._indexation.trajectoire
        return trajectoire.facteur_emploi(annee) / trajectoire.facteur_emploi(annee - 1)

    def demographie(self, annee: int) -> float:
        """La croissance du nombre de retraités par cotisant : celle du COR,
        et ce que la trajectoire retire aux cotisants."""
        return self._cotisants(annee - 1) / self._cotisants(annee) / self._emploi(annee)

    def masse(self, annee: int) -> float:
        """La croissance réelle de la masse salariale qui revalorise la
        proposition, celle de son compte."""
        return self._base.coefficient(annee - 1, annee)

    def inflation(self, annee: int) -> float:
        return self._indexation.trajectoire.inflation_de(annee, self._macro)

    def croissance(self, regle: Regle, annee: int) -> float:
        """Ce que la règle fait d'un euro constant, d'un an sur l'autre."""
        if regle.base == "prix":
            croissance = 1.0
        elif regle.base == "masse_salariale":
            croissance = self.masse(annee)
        else:
            # Le salaire moyen, divisé par le nombre de retraités par
            # cotisant : la masse salariale par retraité. Le diviseur qui sert
            # un rendement d'avance le reprend ici comme sur la masse.
            salaire = (1.0 + self._macro.salaire_moyen(annee)) * self._macro.coefficient_prix(
                annee, annee - 1)
            croissance = salaire / self.demographie(annee) / self._prefinancement
        if regle.facteur_demographique:
            croissance /= self.demographie(annee) ** regle.facteur_demographique
        return croissance

    # -- les chemins ------------------------------------------------------------

    def _chemin(self, groupe: str, depuis: int) -> Detail:
        cle = (groupe, depuis)
        if cle in self._chemins:
            return self._chemins[cle]
        regle = getattr(self._indexation.voie, groupe)
        niveau = regle.niveau_de_bascule if groupe == "stock" else 1.0
        annees = range(depuis + 1, self._base.derniere_annee + 1)
        hausses = [self.croissance(regle, a) * (1.0 + self.inflation(a)) - 1.0 for a in annees]
        masses = [self.masse(a) * (1.0 + self.inflation(a)) - 1.0 for a in annees]
        chemin = suivre(hausses, masses, regle.plancher, regle.reprise)
        detail = Detail({depuis: niveau}, {depuis: niveau}, {depuis: 0.0})
        prix = 1.0
        for rang, annee in enumerate(annees):
            prix *= 1.0 + self.inflation(annee)
            detail.servi[annee] = niveau * chemin.servi[rang] / prix
            detail.regle[annee] = niveau * chemin.regle[rang] / prix
            detail.dette[annee] = niveau * chemin.dette[rang]
        self._chemins[cle] = detail
        return detail

    def detail_stock(self) -> Detail:
        """Un euro du stock à la bascule, de la bascule à l'horizon."""
        return self._chemin("stock", self._base.annee_bascule)

    def detail_nouvelle(self, liquidation: int) -> Detail:
        """Un euro d'une pension liquidée en ``liquidation``, après la bascule."""
        return self._chemin("nouvelles", max(liquidation, self._base.annee_bascule))

    def coefficient_stock(self, annee_liquidation: int, annee: int,
                          prospectif: bool) -> float:
        """Ce que vaut en ``annee``, en euros constants, un euro de pension du
        scénario 6 liquidé en ``annee_liquidation``.

        Avant la bascule, celui du modèle. Le stock — liquidé avant la
        bascule — garde ce que le modèle l'a revalorisé jusqu'à elle, puis
        suit la règle de la voie ; une pension liquidée après suit la règle
        des nouvelles depuis sa liquidation."""
        bascule = self._base.annee_bascule
        seulement = self._indexation.seulement
        stock = annee_liquidation < bascule
        if (seulement == "stock" and not stock) or (seulement == "nouvelles" and stock):
            return 0.0
        if annee < bascule:
            return self._base.coefficient_stock(annee_liquidation, annee, prospectif)
        if stock:
            borne = min(annee, self._base.derniere_annee)
            return (self._base.coefficient_stock(annee_liquidation, bascule, prospectif)
                    * self.detail_stock().servi[borne])
        if annee <= annee_liquidation:
            return 1.0
        borne = min(annee, self._base.derniere_annee)
        return self.detail_nouvelle(annee_liquidation).servi[borne]
