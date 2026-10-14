"""L'effet retour : ce que l'économie des régimes rend, et ce qu'elle coûte ailleurs.

Le coût de la page Coût est celui des RÉGIMES : la dépense de pensions de
chaque système. Une pension plus petite n'est pas une économie publique
entière. Elle paie moins de CSG, de CRDS, de CASA et d'impôt sur le revenu,
et, sous le plafond du minimum vieillesse, elle appelle une ASPA que le fonds
de solidarité vieillesse verse. Jusqu'au 14 octobre 2026, ``cout.py`` tenait
les deux fixes (action 138, étape 5) ; le simulateur de S. Aurain les chiffre,
et l'IPP (Perspectives budgétaires 2027, juin 2026) trouve un gain public
« inférieur d'environ 20 % à 25 % » à l'économie des régimes.

CE QUE LE MODULE RANGE, ET CE QU'IL NE RANGE PAS. Le gain public d'un
scénario des scénarios 2 à 5, une année, est l'économie des régimes, moins
l'ASPA de plus que ses petites pensions déclenchent, moins les prélèvements
que ses pensions ne paient plus. Le scénario 6 n'en est pas : sa garantie
vieillesse, qui remplace l'ASPA, est déjà chiffrée à part
(:class:`~.cout.GarantieDistribution`). Les cotisations, la TVA et ce que les
actifs paient ne bougent pas : l'effet retour est celui des PENSIONS.

LA MÉTHODE est celle de la garantie : la distribution des pensions de droit
direct de l'EIR, déplacée par le rapport de la pension moyenne de la grille
cette année-là à celle du système actuel l'année de l'enquête. Chaque scénario
la déplace de son propre facteur. Sur la distribution déplacée, on calcule :

- l'ASPA, au barème de l'année (personne seule, ou la moitié du plafond du
  couple, mêlés comme pour la garantie), au même taux de recours ;
- les prélèvements de la personne seule qui n'a que sa pension : la tranche
  de CSG que son revenu fiscal présumé lui donne, la CRDS et la CASA qu'elle
  prélève (L. 136-8), et l'impôt sur le revenu de l'année, sur la pension
  nette de la CSG déductible, au barème lu, puis projeté sur les prix.

Ce qui sort, chaque année et pour chaque scénario, n'est pas un montant mais
deux TAUX, rapportés à ce que la distribution perd en masse de pensions : ce
que chaque euro d'économie des régimes coûte en ASPA, et ce qu'il fait perdre
en prélèvements. Ils s'appliquent à l'économie des régimes de la page, celle
de la dépense du COR : la distribution de l'EIR et la dépense publiée ne sont
pas à la même échelle — réversion, résidents à l'étranger, majorations —, et
un taux se transporte d'une échelle à l'autre quand un montant ne le ferait
pas.

LIMITES, déclarées. Le déplacement est uniforme : une pension du bas de la
distribution baisse dans la même proportion que la moyenne, alors qu'un
scénario sans minimum contributif la baisserait davantage ; l'ASPA en est
sous-estimée. Chacun est une personne seule de soixante-dix ans, qui n'a que
sa pension : ni le quotient conjugal, ni les revenus du patrimoine, ni la
cotisation maladie des complémentaires. Le barème de CSG est celui de 2026,
ramené à chaque année sur les prix, et l'effet n'est chiffré qu'à partir de
2019, première année de ce barème à quatre taux.
"""

from __future__ import annotations

import copy
import datetime as dt
from dataclasses import dataclass, field

from .donnees.impot_revenu import charger_baremes_impot_revenu, croissance_macro
from .donnees.prelevements_historiques import charger_prelevements_historiques
from .impot_revenu import Declarant, Foyer, impot_aux_parametres
from .remuneration import charger_prelevements
from .somme import somme_ordonnee

#: Les scénarios dont l'effet retour se chiffre : les quatre comptes
#: notionnels, que l'ASPA complète comme le droit en vigueur. Le scénario 6 a
#: sa garantie vieillesse, chiffrée à part.
SCENARIOS_EFFET_RETOUR: tuple[str, ...] = (
    "notionnel_retroactif",
    "notionnel_prospectif",
    "notionnel_retroactif_employeur",
    "notionnel_prospectif_employeur",
)

#: La première année chiffrée : celle du barème de CSG à quatre taux des
#: pensions (L. 136-8, III bis, en vigueur le 1er janvier 2019), qui est le
#: seul que le module applique. Avant, l'effet retour vaut zéro, faute de
#: barème, et non parce qu'il serait nul.
PREMIERE_ANNEE_EFFET_RETOUR = 2019

#: L'âge que la convention donne à chaque retraité, au 31 décembre de
#: l'année des revenus : au-delà de 65 ans, il ouvre l'abattement des
#: personnes âgées (CGI, art. 157 bis), comme pour la plupart des retraités.
AGE_DECLARE = 70

#: L'année dont le barème de CSG des pensions est lu.
ANNEE_BAREME_CSG = 2026

#: La part déductible de chaque taux de CSG d'une pension (CGI, art. 154
#: quinquies), par le libellé de sa tranche.
_TAUX_DEDUCTIBLES = {"taux réduit": "reduit", "taux médian": "median", "taux plein": "plein"}

#: En deçà de ce déplacement relatif de la masse, un scénario sert ce que sert
#: le système actuel, et ses taux valent zéro : un rapport de deux
#: différences nulles n'est pas un taux.
_ECART_NEGLIGEABLE = 1e-9


@dataclass(frozen=True)
class EffetRetourAnnuel:
    """Les deux taux d'une année, scénario par scénario.

    Chacun est rapporté à l'ÉCONOMIE des régimes : ``aspa[s]`` est l'ASPA de
    plus que chaque euro de pensions en moins appelle, ``prelevements[s]`` ce
    que ce même euro ne paie plus de CSG, de CRDS, de CASA et d'impôt sur le
    revenu. Un scénario qui sert plus que le système actuel a une économie
    négative et les mêmes taux : il rapporte des prélèvements et épargne de
    l'ASPA.
    """

    aspa: dict[str, float] = field(default_factory=dict)
    prelevements: dict[str, float] = field(default_factory=dict)
    #: Le facteur de déplacement de la distribution de chaque système,
    #: système actuel compris : ce que la grille dit de sa pension moyenne.
    facteurs: dict[str, float] = field(default_factory=dict)

    def taux(self, scenario: str) -> float:
        """La part de l'économie des régimes que l'effet retour reprend."""
        return self.aspa.get(scenario, 0.0) + self.prelevements.get(scenario, 0.0)


class EffetRetour:
    """L'effet retour, chiffré sur la distribution que la garantie a calée.

    ``garantie`` est la :class:`~.cout.GarantieDistribution` de la page : sa
    distribution, sa pension de référence, son échelle, son recours et son
    mélange des planchers servent tels quels. ``moyenne_publiee`` est la
    pension moyenne de droit direct, majorations comprises, que la DREES
    publie l'année de l'enquête : elle donne sa valeur à la tranche ouverte de
    la distribution, que la garantie, qui ne regarde que le bas, laisse à sa
    borne inférieure, mais que l'impôt, qui regarde le haut, ne peut pas.
    """

    def __init__(self, simulateur, garantie, moyenne_publiee: float | None = None,
                 derniere: int = 2070) -> None:
        parametres = simulateur.parametres
        racine = parametres.racine_donnees
        self.macro = simulateur.macro
        self.garantie = garantie
        self.distribution = garantie.distribution
        self.millesime = self.distribution.millesime
        self.minimum_vieillesse = simulateur.scenario_actuel.minimum_vieillesse
        self.prelevements = charger_prelevements(racine).pensions
        self.historiques = charger_prelevements_historiques(racine)
        baremes = charger_baremes_impot_revenu(racine)
        self.baremes = baremes.chronique(derniere, "prix", croissance_macro(self.macro, "prix"))
        self.points = _points(self.distribution, moyenne_publiee)
        self._impots: dict[tuple[int, float], float] = {}

    # -- la distribution ---------------------------------------------------

    def _masse(self, facteur: float) -> float:
        """La pension moyenne de la distribution déplacée, en euros mensuels
        de l'enquête."""
        return somme_ordonnee(part * milieu * facteur for milieu, part in self.points)

    def _aspa(self, annee: int, facteur: float) -> float:
        """L'ASPA moyenne par retraité de la distribution déplacée, en euros
        mensuels de l'enquête, recours compris : le barème de l'année, ramené
        aux euros de l'enquête sur les prix, mêlé comme la garantie mêle ses
        deux planchers."""
        seule = self.minimum_vieillesse.plafond(annee)
        couple = self.minimum_vieillesse.plafond_couple(annee)
        if seule is None or couple is None:
            return 0.0
        vers = self.macro.coefficient_prix(annee, self.millesime)
        bareme = copy.copy(self.garantie)
        bareme.plancher_mensuel = couple[0] / 2.0 / 12.0 * vers
        if bareme.plancher_majore is not None:
            bareme.plancher_majore = seule[0] / 12.0 * vers
        # Un effectif de un million : le coût, en millions par an, est alors
        # ce que verse en moyenne une tête, par an.
        chiffre = bareme.chiffrer_distribution(1e6, facteur)
        return chiffre.cout_annuel_meur / 12.0 * self.garantie.taux_recours

    def _prelevements(self, annee: int, facteur: float) -> float:
        """Les prélèvements moyens par retraité de la distribution déplacée,
        en euros mensuels de l'enquête."""
        vers_bareme = self.macro.coefficient_prix(self.millesime, ANNEE_BAREME_CSG)
        return somme_ordonnee(
            part * self._preleve(annee, 12.0 * milieu * facteur * vers_bareme)
            / vers_bareme / 12.0
            for milieu, part in self.points
        )

    def _preleve(self, annee: int, pension: float) -> float:
        """Ce que paie une personne seule qui n'a que ``pension``, annuelle et
        brute, en euros du barème de CSG : la CSG, la CRDS et la CASA de sa
        tranche, et l'impôt sur le revenu de l'année ``annee``, sur sa pension
        de l'année nette de la CSG déductible, ramené aux mêmes euros."""
        cle = (annee, round(pension, 2))
        if cle in self._impots:
            return self._impots[cle]
        p = self.prelevements
        tranche = p.tranche(p.revenu_fiscal_presume([pension]), 1.0)
        sociaux = pension * p.taux_de_la_tranche(tranche)
        cle_deductible = _TAUX_DEDUCTIBLES.get(tranche.libelle)
        deductible = (0.0 if cle_deductible is None else
                      self.historiques.csg_deductible_pension(
                          dt.date(ANNEE_BAREME_CSG, 7, 1), cle_deductible))
        impot = 0.0
        parametres = self.baremes.get(annee)
        if parametres is not None:
            vers_annee = self.macro.coefficient_prix(ANNEE_BAREME_CSG, annee)
            imposable = pension * (1.0 - deductible) * vers_annee
            foyer = Foyer(declarants=(Declarant(pensions=imposable, age=AGE_DECLARE),))
            impot = impot_aux_parametres(foyer, parametres).impot / vers_annee
        self._impots[cle] = sociaux + impot
        return sociaux + impot

    # -- l'année -----------------------------------------------------------

    def facteur(self, masse: float, tetes: float) -> float:
        """Le déplacement de la distribution qu'une masse de la grille dit :
        sa pension par tête sur celle du système actuel l'année de l'enquête."""
        reference = self.garantie.pension_reference
        if tetes <= 0.0 or reference <= 0.0:
            return 0.0
        return masse / tetes / reference

    def chiffrer(self, annee: int, masses: dict[str, float], tetes: float,
                 part_ouverte: float = 1.0) -> EffetRetourAnnuel:
        """Les deux taux de l'année, d'après les masses et les têtes de la
        grille. ``part_ouverte`` est la part de ces têtes qui a l'âge de
        l'ASPA, 65 ans : la distribution ne le dit pas, et l'ASPA de qui
        l'attend est nulle. Vide avant :data:`PREMIERE_ANNEE_EFFET_RETOUR`."""
        if annee < PREMIERE_ANNEE_EFFET_RETOUR:
            return EffetRetourAnnuel()
        facteurs = {cle: self.facteur(masses[cle], tetes)
                    for cle in ("actuel", *SCENARIOS_EFFET_RETOUR)}
        reference = facteurs["actuel"]
        if reference <= 0.0:
            return EffetRetourAnnuel(facteurs=facteurs)
        masse_actuelle = self._masse(reference)
        aspa_actuelle = self._aspa(annee, reference)
        preleve_actuel = self._prelevements(annee, reference)
        aspa, prelevements = {}, {}
        for scenario in SCENARIOS_EFFET_RETOUR:
            facteur = facteurs[scenario]
            economie = masse_actuelle - self._masse(facteur)
            if facteur <= 0.0 or abs(economie) <= _ECART_NEGLIGEABLE * masse_actuelle:
                aspa[scenario] = prelevements[scenario] = 0.0
                continue
            aspa[scenario] = (part_ouverte * (self._aspa(annee, facteur) - aspa_actuelle)
                              / economie)
            prelevements[scenario] = (
                preleve_actuel - self._prelevements(annee, facteur)) / economie
        return EffetRetourAnnuel(aspa=aspa, prelevements=prelevements, facteurs=facteurs)


def _points(distribution, moyenne_publiee: float | None) -> tuple[tuple[float, float], ...]:
    """Chaque tranche de la distribution, en son milieu, et sa part. La
    tranche ouverte reçoit la valeur qui redonne la moyenne publiée ; sans
    elle, ou si elle ne laisse rien au-dessus de la borne, une fois et demie
    sa borne inférieure."""
    fermees = [(0.5 * (t.borne_inferieure + t.borne_superieure), t.part)
               for t in distribution.tranches if t.borne_superieure is not None]
    ouvertes = [t for t in distribution.tranches if t.borne_superieure is None]
    points = list(fermees)
    total = somme_ordonnee(part for _, part in fermees) + somme_ordonnee(
        t.part for t in ouvertes)
    for tranche in ouvertes:
        valeur = 1.5 * tranche.borne_inferieure
        if moyenne_publiee is not None and tranche.part > 0.0:
            reste = moyenne_publiee * total - somme_ordonnee(m * p for m, p in fermees)
            calee = reste / tranche.part
            if calee > tranche.borne_inferieure:
                valeur = calee
        points.append((valeur, tranche.part))
    return tuple(points)
