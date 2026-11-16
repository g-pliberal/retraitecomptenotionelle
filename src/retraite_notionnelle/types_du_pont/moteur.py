"""Les types du moteur notionnel que le pont échange (action 161, étape 1 du
retrait des règles Python) : écart à l'âge de référence, capitalisation,
compte notionnel, conversion, fusion des régimes, indexation, sans aucun corps
de règle. Les fichiers de ``moteur/`` les réimportent le temps du retrait.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..donnees.chargement import Fiabilite
from ..somme import somme_ordonnee



@dataclass(frozen=True)
class EcartAge:
    """Position d'une liquidation par rapport à l'âge de référence."""

    age_liquidation: float
    age_reference: float
    annee_liquidation: int

    @property
    def ecart(self) -> float:
        """Positif = départ anticipé, négatif = départ différé."""
        return self.age_reference - self.age_liquidation

    @property
    def anticipe(self) -> bool:
        return self.ecart > 0

    def __str__(self) -> str:  # pragma: no cover - affichage
        from ..calendrier import formater_age

        if abs(self.ecart) < 1e-9:
            return (
                "liquidation à l'âge de référence "
                f"({formater_age(self.age_reference)})"
            )
        sens = "anticipation" if self.anticipe else "report"
        return (
            f"{sens} de {formater_age(abs(self.ecart))} "
            f"(liquidation à {formater_age(self.age_liquidation)}, "
            f"référence {formater_age(self.age_reference)})"
        )


@dataclass(frozen=True)
class AnneeCapitalisation:
    """Une année du compte capitalisé, de l'ouverture à la clôture.

    Tout y est en euros courants de l'année : c'est un capital réel, pas un
    solde notionnel, et la page qui l'affiche doit pouvoir montrer la ligne
    d'un relevé.
    """

    annee: int
    age: float
    #: Années restant à courir jusqu'à la liquidation, au moment du versement.
    horizon: int
    assiette: float
    versement_brut: float
    frais_versement: float
    versement_net: float
    encours_ouverture: float
    interets: float
    frais_gestion: float
    #: Encours de clôture, net de tous frais : c'est le capital qui serait
    #: transmis si l'assuré mourait cette année-là.
    encours: float
    #: Taux moyen pondéré des lignes vivantes pendant l'année.
    taux_moyen: float
    #: Répartition du versement de l'année par maturité, en euros.
    placements: tuple[tuple[int, float], ...] = ()
    #: Taux du frais sur versement appliqué au versement de l'année.
    taux_frais_versement: float = 0.0
    #: Taux moyen du frais de gestion prélevé sur l'encours de l'année : la
    #: moyenne des tarifs des cohortes, pondérée par leurs encours.
    taux_frais_gestion: float = 0.0

    @property
    def capital_transmissible(self) -> float:
        return self.encours


@dataclass(frozen=True)
class Capitalisation:
    """Le pilier capitalisé d'une carrière : ce qu'il accumule, sert et transmet."""

    #: Année d'ouverture du pilier — celle de la bascule, ou l'entrée dans la
    #: vie active si elle est postérieure.
    annee_ouverture: int
    annee_liquidation: int
    #: Taux effectivement prélevé, les deux cotisations réunies.
    taux_cotisation: float
    annees: tuple[AnneeCapitalisation, ...]

    #: Capital au départ, net de tous frais.
    capital: float
    #: Le même capital si l'enveloppe ne prélevait rien. L'écart avec le
    #: précédent est le coût complet des frais : les prélèvements eux-mêmes, et
    #: les intérêts qu'ils n'ont pas produits.
    capital_hors_frais: float

    #: Diviseur actuariel de la rente — celui du compte notionnel quand le taux
    #: technique est nul, ce qui est le réglage par défaut.
    conversion: CoefficientConversion
    frais_arrerages: float
    #: Rente viagère annuelle servie, nette des frais sur arrérages.
    rente_annuelle: float

    #: Probabilité de mourir avant d'avoir liquidé, vue de l'ouverture du
    #: pilier, sur la table du modèle.
    probabilite_deces_avant_liquidation: float
    #: Espérance du capital transmis, vue de l'ouverture du pilier : chaque
    #: année de décès possible pèse l'encours de cette année-là.
    esperance_capital_transmis: float

    #: Date de la courbe de taux employée, telle que la BCE la publie. Portée
    #: ici pour que la page qui affiche un capital puisse dire de quel jour
    #: sont les taux qui l'ont produit, sans relire le fichier.
    date_courbe: str = ""

    fiabilite: Fiabilite = Fiabilite.ESTIMEE

    #: Part de :attr:`taux_cotisation` qui vient de la cotisation VOLONTAIRE —
    #: les cinq points que la proposition rend et que l'assuré choisit de
    #: remettre au compte. Zéro quand on la retire.
    taux_cotisation_volontaire: float = 0.0

    #: Frais annuel prélevé sur la RÉSERVE qui porte la rente, l'année de la
    #: liquidation, et facteur par lequel il réduit la rente : à taux technique
    #: nul, un prélèvement de ``f`` par an sur la réserve équivaut à diviser le
    #: capital par ``Σ p_t (1 − f)^(−t)`` au lieu de ``Σ p_t`` — le rapport des
    #: deux est ce facteur, exactement 1 quand le frais est nul.
    frais_encours_rente: float = 0.0
    facteur_encours_rente: float = 1.0

    @property
    def taux_cotisation_obligatoire(self) -> float:
        """Ce que la proposition impose, les points volontaires retirés."""
        return self.taux_cotisation - self.taux_cotisation_volontaire

    @property
    def part_volontaire(self) -> float:
        """Fraction du pilier qui vient du volontaire, entre 0 et 1.

        Le pilier est exactement proportionnel à son taux — aucun seuil, aucun
        frais forfaitaire —, si bien que cette seule fraction partage le
        capital, la rente et le capital transmis sans qu'il faille les
        recalculer. Le docstring du module dit pourquoi, et un test le vérifie.
        """
        if self.taux_cotisation <= 0:
            return 0.0
        return self.taux_cotisation_volontaire / self.taux_cotisation

    @property
    def capital_volontaire(self) -> float:
        return self.capital * self.part_volontaire

    @property
    def capital_obligatoire(self) -> float:
        return self.capital - self.capital_volontaire

    @property
    def rente_volontaire(self) -> float:
        """La part de la rente qui vient des cinq points rendus puis remis."""
        return self.rente_annuelle * self.part_volontaire

    @property
    def rente_volontaire_mensuelle(self) -> float:
        return self.rente_volontaire / 12.0

    @property
    def rente_obligatoire(self) -> float:
        return self.rente_annuelle - self.rente_volontaire

    @property
    def actif(self) -> bool:
        """Le pilier a-t-il seulement reçu quelque chose ?"""
        return self.capital > 0

    @property
    def rente_mensuelle(self) -> float:
        return self.rente_annuelle / 12.0

    @property
    def versements(self) -> float:
        """Somme des versements bruts, en euros courants, sans revalorisation."""
        return somme_ordonnee(a.versement_brut for a in self.annees)

    @property
    def frais_versement(self) -> float:
        return somme_ordonnee(a.frais_versement for a in self.annees)

    @property
    def frais_gestion(self) -> float:
        return somme_ordonnee(a.frais_gestion for a in self.annees)

    @property
    def interets(self) -> float:
        return somme_ordonnee(a.interets for a in self.annees)

    @property
    def frais_preleves(self) -> float:
        """Frais effectivement prélevés, en euros courants cumulés.

        Les frais sur arrérages n'y sont pas : ils seront prélevés sur la
        rente, année après année, et non sur le capital.
        """
        return self.frais_versement + self.frais_gestion

    @property
    def cout_des_frais(self) -> float:
        """Ce que les frais retirent au capital, intérêts perdus compris."""
        return self.capital_hors_frais - self.capital

    @property
    def annees_cotisees(self) -> int:
        return somme_ordonnee(1 for a in self.annees if a.versement_brut > 0)

    @property
    def rendement_cumule(self) -> float:
        """Capital rapporté aux versements bruts."""
        return self.capital / self.versements if self.versements else 0.0

    @property
    def taux_rendement_annuel(self) -> float:
        """Taux de rendement interne du pilier, frais compris.

        C'est le taux constant qui, appliqué aux versements bruts aux mêmes
        dates, donnerait le même capital. Il se lit contre les taux de la
        courbe : l'écart est le prix de l'enveloppe.
        """
        return _taux_interne(
            [(a.annee, a.versement_brut) for a in self.annees if a.versement_brut > 0],
            self.annee_liquidation,
            self.capital,
        )


def _taux_interne(versements: list[tuple[int, float]], annee_finale: int,
                  capital: float, tolerance: float = 1e-10) -> float:
    """Taux constant qui mène des versements au capital, par dichotomie.

    La fonction est strictement croissante en le taux dès qu'un versement est
    positif : la dichotomie converge donc, et sans dérivée. Les bornes sont
    larges — de −99 % à +100 % — parce qu'un pilier ouvert un an avant le
    départ peut afficher un rendement négatif du seul fait des frais.
    """
    if not versements or capital <= 0:
        return 0.0

    def valeur(taux: float) -> float:
        return somme_ordonnee(
            montant * (1.0 + taux) ** (annee_finale - annee)
            for annee, montant in versements
        ) - capital

    bas, haut = -0.99, 1.0
    if valeur(bas) > 0 or valeur(haut) < 0:
        # Un seul cas le produit : tous les versements tombent l'année de la
        # liquidation, où ils ne rapportent rien et où les frais les amputent.
        # Aucun taux ne relie alors les uns à l'autre — l'exposant est nul —, et
        # zéro est rendu plutôt qu'un NaN, qui ne s'écrit pas en JSON et qui
        # n'est égal à rien, pas même à lui-même. La page, elle, ne parle pas
        # de rendement dans ce cas : elle dit que le pilier n'a pas eu d'année
        # pour rapporter.
        return 0.0
    for _ in range(200):
        milieu = 0.5 * (bas + haut)
        if valeur(milieu) < 0:
            bas = milieu
        else:
            haut = milieu
        if haut - bas < tolerance:
            break
    return 0.5 * (bas + haut)


@dataclass(frozen=True)
class CotisationAnnuelle:
    """Détail des cotisations d'une année, régime par régime."""

    annee: int
    revenu: float
    assiette_retenue: float
    cotisation: float
    regimes: tuple[str, ...]
    taux_effectif: float
    hors_repartition: float
    fiabilite: Fiabilite
    #: D'où vient la part employeur PUBLIQUE, cette année-là — celle des
    #: régimes à ``perimetre_taux: agent_seul``, qu'aucune fiche ne porte. Vide
    #: si l'année n'en compte aucun ;
    #: ``appelee`` ou ``implicite`` si la contribution réellement versée a été
    #: trouvée ; ``repli`` si elle ne l'a pas été et que le taux du statut pivot
    #: privé lui a été substitué ; ``retraite_seule`` si c'est la part du taux
    #: de l'État que la Cour des comptes rattache à la retraite de l'agent
    #: (``ContributionEtat.RETRAITE_SEULE``). Ne vaut que dans les scénarios 4
    #: et 5 — ailleurs, la question ne se pose pas.
    origine_part_employeur: str = ""
    #: Part de ``cotisation`` versée par l'employeur, en euros. Nulle sous
    #: ``SALARIALE``, qui ne porte rien de lui au compte, et pour un
    #: non-salarié, qui n'en a pas.
    part_employeur: float = 0.0
    #: ``cotisation``, régime par régime : ce que chacun a encaissé, dans
    #: l'ordre où l'année les rencontre. Deux origines ne sont pas des
    #: régimes : ``regime_unifie``, ce que l'on verse au régime unique après
    #: la bascule, et ``taux_commun``, ce que prélève un taux d'acquisition
    #: commun, qui réunit les assiettes avant de prélever et n'appartient à
    #: aucun. Les régimes provisionnés n'y sont pas : ce qu'ils encaissent
    #: est à ``hors_repartition``.
    par_regime: tuple[tuple[str, float], ...] = ()

    @property
    def nulle(self) -> bool:
        return self.cotisation <= 0


@dataclass
class CompteNotionnel:
    """Résultat de l'accumulation sur une carrière."""

    capital: float
    capital_hors_repartition: float
    annee_liquidation: int
    cotisations: list[CotisationAnnuelle] = field(default_factory=list)
    fiabilite: Fiabilite = Fiabilite.ESTIMEE
    #: ``capital``, par origine des cotisations — les régimes et les deux
    #: origines de :attr:`CotisationAnnuelle.par_regime` —, chaque versement
    #: revalorisé comme dans ``capital``. La pension qu'une origine achète est
    #: sa part du capital, divisée par le même coefficient de conversion.
    capital_par_regime: dict[str, float] = field(default_factory=dict)

    @property
    def cotisations_versees(self) -> float:
        """Somme des cotisations en euros courants, sans revalorisation."""
        return somme_ordonnee(c.cotisation for c in self.cotisations)

    @property
    def annees_cotisees(self) -> int:
        return somme_ordonnee(1 for c in self.cotisations if not c.nulle)

    @property
    def rendement_cumule(self) -> float:
        """Rapport entre capital revalorisé et cotisations versées."""
        versees = self.cotisations_versees
        return self.capital / versees if versees else 0.0

    @property
    def cotisations_employeur(self) -> float:
        """Part des cotisations versée par l'employeur, en euros courants."""
        return somme_ordonnee(c.part_employeur for c in self.cotisations)

    @property
    def annees_part_employeur(self) -> dict[str, int]:
        """Nombre d'années par origine de la part employeur publique.

        Ce que les scénarios 4 et 5 doivent dire d'eux-mêmes : sur combien
        d'années la contribution réellement versée a été trouvée, et sur combien
        il a fallu l'estimer, faute de série.
        """
        decompte: dict[str, int] = {}
        for cotisation in self.cotisations:
            if cotisation.origine_part_employeur and not cotisation.nulle:
                origine = cotisation.origine_part_employeur
                decompte[origine] = decompte.get(origine, 0) + 1
        return decompte


@dataclass(frozen=True)
class CoefficientConversion:
    """Diviseur annuitaire et éléments qui l'expliquent."""

    diviseur: float
    age_liquidation: float
    annee_liquidation: int
    esperance_residuelle: float
    table: str
    taux_anticipe: float
    fiabilite: Fiabilite

    @property
    def taux_de_rente(self) -> float:
        """Fraction du capital notionnel servie chaque année."""
        return 1.0 / self.diviseur if self.diviseur else 0.0


@dataclass(frozen=True)
class RegimeFusionne:
    """Régime unique issu de la fusion, et traçabilité de chaque paramètre."""

    annee_bascule: int
    age_ouverture: float
    age_taux_plein: float
    duree_requise_trimestres: int
    salaire_reference: str
    assiette: str
    taux_cotisation_retraite: float
    #: Part de ce taux supportée par l'assuré lui-même. Le régime unique hérite
    #: de la répartition salarié/employeur de ses régimes pivots : elle n'est pas
    #: une décision de la fusion, mais la conséquence de ce qui la compose.
    taux_cotisation_salarie: float
    avantages_non_contributifs: tuple[str, ...]
    origines: dict[str, str]
    regimes_fusionnes: tuple[str, ...]
    fiabilite: Fiabilite

    def resume(self) -> str:
        lignes = [
            f"Régime unique à compter de {self.annee_bascule}",
            f"  {len(self.regimes_fusionnes)} régimes fusionnés",
            f"  âge d'ouverture     : {self.age_ouverture:g} ans   (le plus élevé — {self.origines['age_ouverture']})",
            f"  âge du taux plein   : {self.age_taux_plein:g} ans   (le plus élevé — {self.origines['age_taux_plein']})",
            f"  durée requise       : {self.duree_requise_trimestres} trimestres   ({self.origines['duree_requise_trimestres']})",
            f"  salaire de référence: {self.salaire_reference}   ({self.origines['salaire_reference']})",
            f"  assiette            : {self.assiette}",
            f"  taux de cotisation  : {self.taux_cotisation_retraite:.2%}   ({self.origines['taux_cotisation_retraite']})",
            f"  dont part salariale : {self.taux_cotisation_salarie:.2%}",
            f"  avantages non contributifs : aucun",
        ]
        return "\n".join(lignes)


@dataclass(frozen=True)
class TauxIndexation:
    """Taux retenu pour une année, avec le terme qui l'a emporté."""

    annee: int
    taux: float
    terme_retenu: str
    inflation: float
    salaire_moyen: float
    productivite: float
    fiabilite: Fiabilite

    @property
    def taux_reel(self) -> float:
        """Taux d'indexation net d'inflation."""
        return (1 + self.taux) / (1 + self.inflation) - 1
