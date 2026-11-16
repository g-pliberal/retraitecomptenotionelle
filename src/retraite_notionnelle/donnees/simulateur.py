"""Le simulateur de données seules : ce que le ``Simulateur`` charge sans
règle (action 161, point 4 du tri des scripts et des modules).

Ses séries, sa mortalité, ses courbes de taux, son catalogue des régimes, ses
effectifs, ses distributions, les revalorisations servies, les univers de la
proposition et les variantes d'une étude, que le pont passe au portage dans
sa demande (:attr:`SimulateurDeDonnees.univers_de_la_demande`). Le coût, ses
études et la façade des tests n'en lisent pas davantage : ils le bâtissent
seul, sans importer un module du moteur Python, que le ``Simulateur``
(``simulateur.py``) prolonge par héritage tant que ses règles restent. Ses
affiliations, logées avec leurs règles de routage dans ``carriere.py``, s'y
lisent à la demande.
"""

from __future__ import annotations

import typing
from functools import cached_property

from ..config import Parametres
from ..noyau import univers as univers_de_droit
from ..noyau.calcul_notionnel import calcul_notionnel
from .caracteristiques import CaracteristiquesRetraites
from .cotisants import EffectifsCotisants
from .distribution import DistributionPensions
from .effectifs import EffectifsRetraites
from .financement_regimes import StructureFinancement
from .macro import DonneesMacro
from .mortalite import DonneesMortalite
from .patrimoine import PatrimoineMenages
from .regimes import CatalogueRegimes
from .revalorisations import RevalorisationsPensions
from .taux import CourbeTauxSansRisque
from .vie_en_couple import VieEnCouple

if typing.TYPE_CHECKING:
    from ..carriere import Affiliations

#: Les données que le simulateur charge, chacune par son chargeur : ce que la
#: façade des tests lit sur lui, et que le ``Simulateur`` ne redéfinit pas.
DONNEES = frozenset({
    "macro", "mortalite", "courbe_taux", "courbe_taux_pilier", "catalogue",
    "effectifs", "cotisants", "distribution", "distributions_par_sexe",
    "caracteristiques", "patrimoine", "vie_en_couple", "financement_regimes",
    "affiliations", "revalorisations"})

#: Les cinq scénarios notionnels, dans l'ordre où ils s'affichent, avec le
#: numéro et le titre sous lesquels le tableau, la page et l'API les citent :
#: les univers de la proposition (``data/reference/univers/``, § 4.8), dont
#: chacun est une pile de couches posée sur le droit réel.
#:
#: Deux paires, puis un sixième. 2 et 3 ne portent au compte que la part
#: SALARIALE de la cotisation, 4 et 5 y ajoutent la couche de la part
#: PATRONALE. À l'intérieur de chaque paire, l'un est rétroactif et l'autre
#: prospectif, par la transition de la bascule. Rien d'autre ne les sépare, et
#: c'est ce qui les rend comparables deux à deux : 4 se lit contre 2, 5 contre
#: 3, et l'écart mesure exactement ce que l'employeur verse. Le 6 se lit contre
#: le 4 : même compte rétroactif, cotisation entière aux taux réels jusqu'à la
#: bascule, puis un taux unique de 18 % pour tous à compter d'elle, et une
#: garantie vieillesse individualisée, financée par l'impôt, par-dessus.
SCENARIOS_NOTIONNELS = tuple((u.id, u.numero, u.nom)
                             for u in univers_de_droit.de_la_proposition())



class SimulateurDeDonnees:
    """Charge les données du simulateur une fois, sans règle."""

    def __init__(self, parametres: Parametres | None = None,
                 variantes: dict[str, univers_de_droit.Univers] | None = None) -> None:
        self.parametres = parametres or Parametres()
        racine = self.parametres.racine_donnees
        if not racine.exists():
            raise FileNotFoundError(
                f"répertoire de données introuvable : {racine}. "
                "Lancer le simulateur depuis la racine du dépôt, ou renseigner "
                "Parametres(racine_donnees=...)."
            )
        #: Les univers d'une étude (``data/reference/variantes/``), chacun à la
        #: place de l'univers de la proposition dont il porte la clé : le
        #: paquet ne les porte pas, et le pont passe leur calcul au portage
        #: dans la demande (:attr:`univers_de_la_demande`, action 161).
        self.variantes: dict[str, univers_de_droit.Univers] = dict(variantes or {})

    # -- données -------------------------------------------------------------

    @cached_property
    def macro(self) -> DonneesMacro:
        return DonneesMacro(
            self.parametres.racine_donnees,
            scenario_projection=self.parametres.scenario_projection,
            trajectoire_emploi=self.parametres.trajectoire_emploi,
        )

    @cached_property
    def mortalite(self) -> DonneesMortalite:
        return DonneesMortalite(self.parametres.racine_donnees,
                                hypothese=self.parametres.hypothese_esperance_vie)

    @cached_property
    def courbe_taux(self) -> CourbeTauxSansRisque:
        """La courbe sans risque telle que la BCE la publie, sans retouche.

        C'est elle que lit le TAUX D'EMPRUNT du chiffrage : la dette de la page
        Coût se finance au forward à un an, déflaté. Elle ne porte donc aucune
        prime de terme, quel que soit le réglage — voir
        :attr:`courbe_taux_pilier`, qui dit pourquoi les deux sont séparées.
        """
        return CourbeTauxSansRisque(self.parametres.racine_donnees)

    @cached_property
    def courbe_taux_pilier(self) -> CourbeTauxSansRisque:
        """La même courbe, sous le réglage des taux du PILIER capitalisé.

        ``prime_terme_trente_ans`` ne traverse que celle-ci. La séparation est
        volontaire, et elle corrige une erreur : la prime portée sur la courbe
        commune déplaçait aussi le taux d'emprunt de la dette, donc le stock
        accumulé par TOUS les systèmes — jusqu'à dix points de PIB sur le
        système actuel, qui n'a pas de pilier capitalisé et que le réglage
        annonçait pourtant ne pas toucher.

        Le coût de rouler une dette courte est une question réelle, et elle se
        pose dans les mêmes termes ; mais c'est une AUTRE question, qui a ses
        propres réserves dans ``docs/limites.md``, et un réglage nommé « taux
        futurs du pilier capitalisé » n'est pas l'endroit d'où la trancher.
        À zéro, le réglage publié, les deux courbes sont le même objet à un
        identifiant près.
        """
        return CourbeTauxSansRisque(
            self.parametres.racine_donnees,
            self.parametres.prime_terme_trente_ans,
        )

    @cached_property
    def catalogue(self) -> CatalogueRegimes:
        # Sous les conventions du COR, l'Agirc-Arrco cotise et acquiert ses
        # points au taux moyen des entreprises, comme ses cas types.
        return CatalogueRegimes(self.parametres.racine_donnees,
                                taux_moyens=self.parametres.conventions_cor)

    @cached_property
    def effectifs(self) -> EffectifsRetraites:
        """Effectifs de retraités par caisse — la pondération des cas types.

        Aucune pension n'en dépend : ils ne servent qu'aux AGRÉGATS, où ils
        disent ce que chaque configuration de carrière pèse réellement.
        """
        return EffectifsRetraites(self.parametres.racine_donnees)

    @cached_property
    def cotisants(self) -> EffectifsCotisants:
        """Effectifs de cotisants par caisse — la pondération côté RECETTE.

        Le pendant de ``effectifs`` pour une masse de cotisations : un cas type
        y pèse les cotisants de sa caisse, et non plus ses retraités. Aucune
        pension n'en dépend davantage.
        """
        return EffectifsCotisants(self.parametres.racine_donnees)

    @cached_property
    def distribution(self) -> DistributionPensions:
        """La distribution des pensions — elle seule chiffre un plancher.

        Aucune pension n'en dépend. Elle ne sert qu'à la garantie vieillesse de
        la page « Coût », qui est une allocation différentielle et ne se lit
        pas sur treize carrières. Celle des retraités qui RÉSIDENT en France :
        la garantie, comme l'ASPA qu'elle remplace, ne sert qu'eux.
        """
        return DistributionPensions(self.parametres.racine_donnees, residence="france")

    @cached_property
    def distributions_par_sexe(self) -> dict[str, DistributionPensions]:
        """La même distribution, femmes et hommes à part.

        L'enquête les publie séparément, et c'est ce qui permet de déplacer
        chaque sexe de son propre facteur au lieu de déplacer l'ensemble du
        même : le scénario 6 retire des droits non cotisés que les femmes
        détiennent plus souvent.
        """
        return {
            sexe: DistributionPensions(self.parametres.racine_donnees, sexe=sexe,
                                       residence="france")
            for sexe in ("F", "H")
        }

    @cached_property
    def caracteristiques(self) -> CaracteristiquesRetraites:
        """Ce que les carrières doivent aux droits non cotisés, par sexe.

        Elle ne sert, elle non plus, qu'à la garantie : c'est d'elle que vient
        le rapport des deux facteurs de déplacement, et le poids des deux sexes
        parmi les retraités.
        """
        return CaracteristiquesRetraites(self.parametres.racine_donnees)

    @cached_property
    def patrimoine(self) -> PatrimoineMenages:
        """Le patrimoine des ménages retraités — ce qu'une succession couvre.

        Aucune pension n'en dépend. Il ne sert qu'à la reprise sur succession
        de la garantie vieillesse, sur la page « Coût ».
        """
        return PatrimoineMenages(self.parametres.racine_donnees)

    @cached_property
    def vie_en_couple(self) -> VieEnCouple:
        """Qui vit en couple après 65 ans — ce qui regroupe deux avances sur
        une succession. Aucune pension n'en dépend."""
        return VieEnCouple(self.parametres.racine_donnees)

    @cached_property
    def financement_regimes(self) -> StructureFinancement:
        """Qui finance chaque régime : ses cotisants, l'État, ou personne.

        Aucune pension n'en dépend non plus. Elle sert à dire ce qu'une réforme
        déplace ENTRE FINANCEURS, ce que le coefficient d'équilibre agrégé ne
        distingue pas : 86 % de la fonction publique d'État viennent de la
        contribution de ses employeurs, dont 74 points de l'État lui-même, et
        49 % de la CNRACL de 2070 ne viennent de personne.
        """
        return StructureFinancement(self.parametres.racine_donnees)

    @cached_property
    def affiliations(self) -> Affiliations:
        """Le routage des statuts, logé avec ses règles dans ``carriere.py`` :
        le lire importe ce module, que le coût n'atteint pas."""
        from ..carriere import Affiliations

        return Affiliations(self.parametres.racine_donnees)

    @cached_property
    def revalorisations(self) -> RevalorisationsPensions:
        """Ce que le droit a servi aux pensions liquidées, date d'effet par date d'effet."""
        return RevalorisationsPensions(self.parametres.racine_donnees)

    # -- les univers de la proposition ---------------------------------------

    @cached_property
    def univers(self) -> dict[str, univers_de_droit.Univers]:
        """Les six scénarios, chacun un univers de droit (docs/architecture.md,
        § 4.8), lus sous la racine des données du simulateur ; une variante
        d'une étude à la place de celui qu'elle remplace, sous sa clé."""
        reference = self.parametres.racine_donnees / "reference"
        lus = univers_de_droit.charger(reference / "univers", reference / "couches",
                                       reference / "regles")
        for cle in self.variantes:
            if cle not in lus or lus[cle].est_le_droit_reel:
                raise ValueError(f"la variante {self.variantes[cle].id} ne remplace aucun "
                                 f"univers de la proposition : {cle}")
        return {cle: self.variantes.get(cle, u) for cle, u in lus.items()}

    @property
    def univers_de_la_demande(self) -> dict[str, dict]:
        """Ce que le pont passe au portage, à la place du calcul que le paquet
        porte sous la même clé : le calcul de chaque variante, tel que la
        fabrication le résout (``CalculNotionnel.donnees``, la forme du
        paquet)."""
        return {cle: calcul_notionnel(u, None).donnees() for cle, u in self.variantes.items()}

    # -- usage ---------------------------------------------------------------

    def pour_la_projection(self) -> "SimulateurDeDonnees":
        """Le même simulateur, sous les conventions de projection du COR
        (``Parametres.conventions_cor``), et sans le minimum vieillesse au
        scénario 1 (``Parametres.minimum_vieillesse_dans_le_scenario_actuel``) :
        celui de la page Coût, dont la dépense ne compte pas l'ASPA. Construit
        une fois, puis gardé.

        Il garde les variantes d'une étude (:attr:`variantes`), et
        l'hypothèse d'espérance de vie des paramètres : sous la basse
        ou la haute, la page Coût compte ses retraités dans la pyramide de la
        même hypothèse, ce que ``calculer_cout`` vérifie
        (``Population.verifier_hypothese``, action 138, étape 7)."""
        if (self.parametres.conventions_cor
                and not self.parametres.minimum_vieillesse_dans_le_scenario_actuel):
            return self
        jumeau = self.__dict__.get("_projection")
        if jumeau is None:
            from dataclasses import replace

            jumeau = type(self)(replace(self.parametres, conventions_cor=True,
                                        minimum_vieillesse_dans_le_scenario_actuel=False),
                                variantes=self.variantes)
            self.__dict__["_projection"] = jumeau
        return jumeau
