"""Simulateur : assemble les données, le moteur et les six scénarios.

C'est le point d'entrée unique. Une seule instance charge les données une fois
et peut ensuite simuler autant de carrières que voulu :

    >>> from retraite_notionnelle import Parametres
    >>> from retraite_notionnelle.simulateur import Simulateur
    >>> simulateur = Simulateur(Parametres())
    >>> carriere = simulateur.carriere_simple(
    ...     annee_naissance=1960, sexe="H",
    ...     affiliation="salarie_prive_non_cadre",
    ...     age_debut=20, age_liquidation=60)
    >>> comparaison = simulateur.simuler(carriere)
    >>> print(comparaison.tableau())     # doctest: +SKIP
"""

from __future__ import annotations

from dataclasses import fields
from functools import cached_property

from .carriere import (
    Carriere,
    LigneRelevee,
    Metier,
    salaire_moyen_annuel,
)
from .config import ContributionEtat, Parametres, PartCotisation
from .donnees.chargement import DonneeInsuffisante, Fiabilite, dans_un_instantane
from .donnees.macro import DonneesMacro
from .donnees.simulateur import SCENARIOS_NOTIONNELS, SimulateurDeDonnees  # noqa: F401
from .droit.ouvrir import indemnisation_bornee
from .echeancier import Echeancier
from .moteur.age_reference import AgeReference
from .moteur.capitalisation import ConstructeurCapitalisation
from .moteur.compte import ConstructeurCompte
from .moteur.conversion import Convertisseur
from .moteur.fusion import RegimeFusionne, fusionner
from .moteur.indexation import Indexation
from .remuneration import remuneration_de_la_carriere
from .revalorisation import pension_aujourd_hui
from .revalorisation_servie import RevalorisationServie
from .noyau import univers as univers_de_droit
from .scenarios.actuel import ScenarioActuel
from .scenarios.notionnel import ResultatNotionnel, ScenarioNotionnel
from .noyau.calcul_notionnel import CalculNotionnel, calcul_notionnel
from .somme import somme_ordonnee
from .types_du_pont.comparaison import (  # noqa: F401  (types du pont, action 161)
    Comparaison, ContributionEmployeur)




#: Les résultats notionnels qu'une comparaison sait porter : un univers de la
#: proposition de plus demande de savoir l'afficher.
_CHAMPS_NOTIONNELS = frozenset(champ.name for champ in fields(Comparaison)
                               if champ.type == "ResultatNotionnel")




def _dernier_revenu_annualise(carriere: Carriere, macro: DonneesMacro) -> float:
    """Dénominateur du taux de remplacement, à la DATE du départ.

    Deux corrections y sont faites, chacune pour une raison distincte.

    L'année du départ est incomplète — six mois de salaire pour qui liquide au
    1er juillet —, et la rapporter telle quelle doublait le taux. Le revenu est
    donc ramené à l'année pleine.

    Il est ensuite ramené à l'ANNÉE DE LIQUIDATION. Qui part le 1er janvier n'a
    travaillé aucun mois de cette année-là : sa dernière année cotisée est la
    précédente, et le taux rapportait alors une pension en euros de l'année du
    départ à un salaire en euros de l'année d'avant. Deux millésimes pour un
    seul rapport, et un décrochement de 1,84 point entre un départ en janvier
    et un départ en février — la marche la plus grosse de toute l'année, alors
    qu'un mois seulement les sépare. Le salaire est donc avancé jusqu'à l'année
    du départ par l'indice du salaire moyen, celui-là même dont la carrière est
    tirée. Il reste une marche de 0,58 point, du même ordre que celles des
    frontières de trimestre : celle-là mesure un mois de cotisation en moins,
    et non un changement d'unité.
    """
    derniers = [l for l in carriere.lignes if l.cotise]
    if not derniers:
        return 0.0
    # Toutes les activités de la dernière année cotisée : c'est le revenu
    # d'activité que la pension remplace, et non celui d'une seule d'entre elles.
    annee = derniers[-1].annee
    revenu = somme_ordonnee(l.revenu_annualise for l in derniers if l.annee == annee)
    reference = salaire_moyen_annuel(macro, annee)
    if reference <= 0:
        return revenu
    facteur = salaire_moyen_annuel(macro, carriere.annee_liquidation) / reference
    return revenu * facteur


class Simulateur(SimulateurDeDonnees):
    """Façade : charge les données une fois (:class:`SimulateurDeDonnees`, dont
    il hérite), simule autant de carrières que voulu."""

    def __init__(self, parametres: Parametres | None = None,
                 variantes: dict[str, univers_de_droit.Univers] | None = None) -> None:
        super().__init__(parametres, variantes)
        #: Les comptes et les scénarios de la proposition, un par jeu de
        #: paramètres que les couches changent : deux univers qui changent les
        #: mêmes partagent les mêmes, comme 2 et 3, ou 4 et 5.
        self._constructeurs: dict[tuple, ConstructeurCompte] = {}
        self._scenarios: dict[tuple, ScenarioNotionnel] = {}

    # -- moteur --------------------------------------------------------------

    @cached_property
    def indexation(self) -> Indexation:
        return Indexation(self.macro, self.parametres)

    @cached_property
    def revalorisation_servie(self) -> RevalorisationServie:
        """La règle que les systèmes notionnels prêtent aux pensions servies.

        La même que celle de la page Coût, de la première année de la
        répartition à l'année courante : le simulateur n'en lit que ce qui va
        du départ à aujourd'hui.
        """
        return RevalorisationServie(self, self.parametres.annee_debut_repartition,
                                    self.parametres.annee_courante)

    def echeancier(self, carriere: Carriere) -> Echeancier:
        """L'échéancier du scénario 1 parcouru pour ``carriere`` : son départ,
        puis, pour qui a liquidé avant l'année courante, l'échéance de cette
        année-là."""
        echeancier = Echeancier(self)
        echeancier.parcourir(carriere, echeance=(
            self.parametres.annee_courante
            if carriere.annee_liquidation < self.parametres.annee_courante else None))
        return echeancier

    @cached_property
    def convertisseur(self) -> Convertisseur:
        return Convertisseur(self.mortalite, self.parametres, self.macro,
                             self.distribution)

    @cached_property
    def age_reference(self) -> AgeReference:
        return AgeReference(self.parametres.racine_donnees, self.parametres, self.mortalite)

    @cached_property
    def constructeur(self) -> ConstructeurCompte:
        return ConstructeurCompte(
            self.macro, self.catalogue, self.affiliations,
            self.indexation, self.parametres,
        )

    def _constructeur_variante(self, **modifications) -> ConstructeurCompte:
        """Constructeur identique, sauf sur ce qui alimente le compte.

        Les scénarios 4 et 5 ne diffèrent du scénario 2 que par leur flux de
        cotisations : mêmes données, même indexation, même liquidation. Ils se
        construisent donc en dérivant les paramètres, ce qui garantit qu'aucune
        autre différence ne peut s'y glisser à l'insu du lecteur.
        """
        return ConstructeurCompte(
            self.macro, self.catalogue, self.affiliations,
            self.indexation, self.parametres.avec(**modifications),
        )

    # -- les univers de la proposition ---------------------------------------

    @cached_property
    def calculs(self) -> dict[str, CalculNotionnel]:
        """Ce que le moteur fait de chaque univers de la proposition, dans
        l'ordre de leurs numéros : ce qu'il ne sait pas faire l'arrête ici."""
        return {cle: calcul_notionnel(u, self.parametres)
                for cle, u in self.univers.items() if not u.est_le_droit_reel}

    def constructeur_de(self, calcul: CalculNotionnel) -> ConstructeurCompte:
        """Le compte d'un univers : celui du simulateur, sous les paramètres
        que ses couches changent. Ils ne diffèrent que par ce qui alimente le
        compte, ce qui garantit qu'aucune autre différence ne peut s'y glisser à
        l'insu du lecteur."""
        if not calcul.modifications:
            return self.constructeur
        if calcul.modifications not in self._constructeurs:
            self._constructeurs[calcul.modifications] = self._constructeur_variante(
                **dict(calcul.modifications))
        return self._constructeurs[calcul.modifications]

    def scenario_de(self, calcul: CalculNotionnel) -> ScenarioNotionnel:
        """Le scénario notionnel d'un univers. Le pilier capitalisé n'est
        construit que pour l'univers qui l'ajoute : les autres ne le reçoivent
        pas, et ne peuvent donc pas le servir par inadvertance."""
        cle = (calcul.modifications, calcul.capitalisation)
        if cle not in self._scenarios:
            self._scenarios[cle] = ScenarioNotionnel(
                self.constructeur_de(calcul), self.convertisseur, self.age_reference,
                self.scenario_actuel, self.parametres,
                capitalisation=(self.constructeur_capitalisation
                                if calcul.capitalisation else None),
            )
        return self._scenarios[cle]

    @dans_un_instantane
    def calculer_univers(self, univers: str, carriere: Carriere) -> ResultatNotionnel:
        """Un univers de la proposition sur cette carrière, telle quelle :
        l'âge légal que l'univers ajoute, c'est à :meth:`carriere_proposition`
        de l'appliquer.

        Une transition ouvre le compte à la bascule, sur les droits acquis que
        sa liquidation fictive valorise, et sur le régime unique toujours ; la
        garantie vieillesse se sert après le compte et son pilier, qu'il soit
        rétroactif ou ouvert à la bascule (la proposition prospective, action
        161) ; sinon, le compte rétroactif, sur le régime unique si le réglage
        le garde (``fusion_au_plus_defavorable``).
        """
        calcul = self.calculs[univers]
        scenario = self.scenario_de(calcul)
        fusionne = self.regime_fusionne if self.parametres.fusion_au_plus_defavorable else None
        if calcul.prospectif:
            compte = scenario.prospectif(carriere, self.regime_fusionne, libelle=calcul.libelle,
                                         neutralisations=calcul.neutralisations)
            return (scenario.avec_le_pilier_et_la_garantie(carriere, compte)
                    if calcul.garantie else compte)
        if calcul.garantie:
            return scenario.liberal(carriere, fusionne, libelle=calcul.libelle)
        return scenario.retroactif(carriere, fusionne, libelle=calcul.libelle)

    @cached_property
    def constructeur_employeur(self) -> ConstructeurCompte:
        """Le constructeur des scénarios 4 et 5 : un seul, pour les deux.

        Il ne diffère de celui des scénarios 2 et 3 que par un paramètre, que
        la couche ``part_patronale`` change : la part de la cotisation portée
        au compte.
        """
        return self.constructeur_de(self.calculs["notionnel_retroactif_employeur"])

    @cached_property
    def constructeur_prelevement(self) -> ConstructeurCompte:
        """Ce que le droit en vigueur PRÉLÈVE, salariale et patronale : le
        dénominateur du rapport de recettes de la page Coût (``cout.TAUX_REELS``).

        C'est le constructeur des scénarios 4 et 5 tant que ce qu'ils portent
        au compte est ce que l'employeur verse. Sous
        ``ContributionEtat.RETRAITE_SEULE``, le défaut, ce n'est plus vrai pour
        l'État : le compte d'un de ses agents ne reçoit que la part de son taux
        que la Cour des comptes rattache à sa retraite, mais l'État verse le
        taux entier, et c'est ce taux qui finance le système. Le réglage change
        ce qui est PORTÉ AU COMPTE, non ce qui est PRÉLEVÉ ; le confondre
        gonflait de près de moitié la recette que la proposition garde des
        agents de l'État.
        """
        if self.parametres.contribution_etat is ContributionEtat.ENTIERE:
            return self.constructeur_employeur
        return self._constructeur_variante(
            part_cotisation=PartCotisation.TOTALE,
            contribution_etat=ContributionEtat.ENTIERE,
        )

    @cached_property
    def constructeur_liberal(self) -> ConstructeurCompte:
        """Le constructeur du scénario 6 : le scénario 4 jusqu'à la bascule,
        le taux unique de la proposition ensuite.

        Il ne diffère de celui du scénario 4 que par ce qui alimente le compte
        À COMPTER DE LA BASCULE, que la couche ``taux_unique`` change : un taux
        d'acquisition commun, prélevé une fois sur la rémunération, à la place
        des taux du régime unique. Avant la bascule, ce qui a été cotisé sous
        le système actuel est porté tel qu'il a été prélevé, aux taux réels de
        chaque régime, salariale et patronale confondues — exactement le
        scénario 4. La part de cotisation reste donc ``TOTALE``.
        """
        return self.constructeur_de(self.calculs["notionnel_liberal"])

    @cached_property
    def scenario_actuel(self) -> ScenarioActuel:
        return ScenarioActuel(
            self.macro, self.catalogue, self.affiliations, self.parametres
        )

    @cached_property
    def scenario_notionnel(self) -> ScenarioNotionnel:
        """Scénarios 2 et 3 : le même objet sert aux deux."""
        return self.scenario_de(self.calculs["notionnel_retroactif"])

    @cached_property
    def scenario_employeur(self) -> ScenarioNotionnel:
        """Scénarios 4 et 5 : le scénario notionnel, part patronale comprise.

        Le même objet sert aux deux, comme :attr:`scenario_notionnel` sert aux
        scénarios 2 et 3 : c'est le point de départ du compte — origine de la
        répartition ou année de bascule — qui les distingue, pas le calcul.
        """
        return self.scenario_de(self.calculs["notionnel_retroactif_employeur"])

    @cached_property
    def convertisseur_rente_capitalisee(self) -> Convertisseur:
        """Le convertisseur de la rente du PER : même table, taux technique propre.

        Il ne diffère de celui de la pension notionnelle que par le taux
        d'actualisation incorporé au diviseur — nul de part et d'autre au
        réglage par défaut, si bien que les deux diviseurs sont alors le même
        nombre. Les séparer coûte une ligne et garantit qu'un taux technique
        donné au PER ne déplacera jamais la pension de répartition.
        """
        return Convertisseur(
            self.mortalite,
            self.parametres.avec(
                taux_anticipe_conversion=(
                    self.parametres.taux_technique_rente_capitalisation
                )
            ),
            self.macro,
            self.distribution,
        )

    @cached_property
    def constructeur_capitalisation(self) -> ConstructeurCapitalisation:
        """Le pilier obligatoire de la proposition — et d'elle seule."""
        return ConstructeurCapitalisation(
            self.courbe_taux_pilier, self.mortalite,
            self.convertisseur_rente_capitalisee, self.parametres,
        )

    @cached_property
    def scenario_liberal(self) -> ScenarioNotionnel:
        """Scénario 6 : le scénario 4 jusqu'à la bascule, 18 % pour tous ensuite,
        la garantie vieillesse et le pilier de capitalisation obligatoire."""
        return self.scenario_de(self.calculs["notionnel_liberal"])

    @cached_property
    def regime_fusionne(self) -> RegimeFusionne:
        return fusionner(self.catalogue, self.parametres.annee_bascule)

    # -- usage ---------------------------------------------------------------

    def carriere_simple(self, annee_naissance: int, sexe: str, affiliation: str,
                        age_debut: float, age_liquidation: float, **kwargs) -> Carriere:
        """Construit une carrière d'un seul métier, à partir de cinq informations.

        C'est le chemin le plus court pour qu'un assuré se simule sans rien
        connaître de la mécanique des régimes. Pour une carrière qui en compte
        plusieurs, voir :meth:`carriere_parcours`.
        """
        self._verifier_affiliation(affiliation)
        return Carriere.depuis_profil(
            annee_naissance=annee_naissance,
            sexe=sexe,
            affiliation=affiliation,
            age_debut=age_debut,
            age_liquidation=age_liquidation,
            macro=self.macro,
            **kwargs,
        )

    def carriere_parcours(self, annee_naissance: int, sexe: str,
                          metiers: list[Metier], age_liquidation: float,
                          **kwargs) -> Carriere:
        """Construit une carrière à partir de la suite des métiers exercés.

        Un métier après l'autre, chacun avec son statut et son niveau de revenu :
        c'est la forme générale, dont :meth:`carriere_simple` est le cas à un
        métier.
        """
        for metier in metiers:
            self._verifier_affiliation(metier.affiliation)
        return Carriere.depuis_parcours(
            annee_naissance=annee_naissance,
            sexe=sexe,
            metiers=list(metiers),
            age_liquidation=age_liquidation,
            macro=self.macro,
            **kwargs,
        )

    def carriere_releve(self, annee_naissance: int, sexe: str,
                        releve: list[LigneRelevee], age_liquidation: float,
                        **kwargs) -> Carriere:
        """Construit une carrière lue sur un relevé, année par année.

        La forme la plus exacte : rien n'y est reconstitué, ni le revenu de
        chaque année ni les trimestres qu'elle a validés — l'assuré les recopie
        de son relevé.
        """
        for ligne in releve:
            self._verifier_affiliation(ligne.affiliation)
        return Carriere.depuis_releve(
            annee_naissance=annee_naissance,
            sexe=sexe,
            releve=list(releve),
            age_liquidation=age_liquidation,
            macro=self.macro,
            **kwargs,
        )

    def _verifier_affiliation(self, affiliation: str) -> None:
        if affiliation not in self.affiliations:
            raise KeyError(
                f"affiliation inconnue : {affiliation!r}. Disponibles : "
                + ", ".join(self.affiliations.codes)
            )

    def carriere_proposition(self, carriere: Carriere) -> Carriere:
        """La carrière que la proposition fait liquider : la même, sauf l'âge.

        L'âge légal de la proposition (``Parametres.age_legal_liberal``, 65 ans)
        ne s'applique qu'aux départs qu'elle régit, ceux qui prennent effet à
        compter du 1er janvier de la bascule : qui a liquidé avant est parti
        sous le droit en vigueur. Un départ plus précoce est reporté à l'âge
        légal, et la carrière poursuivie jusque-là (:meth:`Carriere.prolongee`).
        Rend la carrière elle-même dans tous les autres cas.
        """
        age_legal = self.parametres.age_legal_liberal
        if age_legal is None or carriere.age_liquidation is None:
            return carriere
        if carriere.date_liquidation.annee < self.parametres.annee_bascule:
            return carriere
        return carriere.prolongee(age_legal, self.macro)

    def proposition(self, carriere: Carriere) -> ResultatNotionnel:
        """Le scénario 6 sur cette carrière-là, telle quelle.

        Sans âge légal : c'est à :meth:`carriere_proposition` de dire à quel
        âge la proposition fait partir. La page Coût s'en sert pour les
        cohortes que la bascule sépare de leur génération de la grille.
        """
        return self.calculer_univers("notionnel_liberal", carriere)

    @dans_un_instantane
    def simuler(self, carriere: Carriere) -> Comparaison:
        """Calcule les six scénarios pour une carrière."""
        self._verifier_fiabilite(carriere)
        # LE CHÔMAGE CESSE D'ÊTRE INDEMNISÉ AU TAUX PLEIN (L. 5421-4 du code du
        # travail) : les comptes notionnels portent ce que l'Unédic a vraiment
        # versé, et la proposition prolonge la carrière ainsi bornée. Le
        # scénario 1 borne la sienne à son relevé
        # (`droit.ouvrir.indemnisation_bornee`).
        bornee = indemnisation_bornee(self.scenario_actuel, carriere)
        proposition = self.carriere_proposition(bornee)
        reporte = proposition is not bornee
        if reporte:
            # Les années que le report fait travailler entrent dans le calcul :
            # elles ont à tenir la même exigence que les autres.
            self._verifier_fiabilite(proposition)

        # LE SCÉNARIO 1 PASSE PAR L'ÉCHÉANCIER (docs/architecture.md, § 7.4) :
        # le départ appelle la liquidation, puis l'ASPA du jour ; l'échéance,
        # pour qui a liquidé avant l'année courante, fait vivre les pensions
        # jusque-là. Tout s'inscrit à son journal.
        echeancier = self.echeancier(carriere)
        actuel = echeancier.au_depart
        # Les cinq autres sont les univers de la proposition, dans l'ordre de
        # leurs numéros ; celui qui ajoute l'âge légal part à cet âge.
        notionnels = {
            cle: self.calculer_univers(cle, proposition if calcul.age_legal else bornee)
            for cle, calcul in self.calculs.items()
        }
        inconnus = sorted(set(notionnels) - _CHAMPS_NOTIONNELS)
        if inconnus:
            raise ValueError(f"univers {', '.join(inconnus)} : la comparaison ne connaît que "
                             f"{', '.join(sorted(_CHAMPS_NOTIONNELS))}, et ne sait pas "
                             "encore en afficher un autre")

        # La mémoire des calibrations n'est plus écrite ici : c'est un fichier
        # versionné, dont `scripts/construire_donnees.py` est le seul écrivain.
        comparaison = Comparaison(
            carriere=carriere,
            trimestres_actuels=carriere.trimestres_actuels,
            actuel=actuel,
            **notionnels,
            regime_fusionne=self.regime_fusionne,
            parametres=self.parametres,
            coefficient_euros_constants=self.macro.coefficient_prix(
                carriere.annee_liquidation, self.parametres.annee_euros_constants
            ),
            dernier_revenu_annualise=_dernier_revenu_annualise(carriere, self.macro),
            remuneration=remuneration_de_la_carriere(
                carriere, self.macro, self.catalogue, self.affiliations,
                self.parametres,
            ),
            carriere_liberal=proposition if reporte else None,
            coefficient_euros_constants_liberal=(
                self.macro.coefficient_prix(
                    proposition.annee_liquidation,
                    self.parametres.annee_euros_constants,
                ) if reporte else None
            ),
            dernier_revenu_annualise_liberal=(
                _dernier_revenu_annualise(proposition, self.macro)
                if reporte else None
            ),
        )
        comparaison.journal = echeancier.journal
        comparaison.reversion = echeancier.reversion
        if carriere.annee_liquidation < self.parametres.annee_courante:
            comparaison.aujourd_hui = pension_aujourd_hui(self, comparaison,
                                                          echeancier.aujourd_hui)
            comparaison.coefficient_euros_aujourd_hui = self.macro.coefficient_prix(
                self.parametres.annee_courante, self.parametres.annee_euros_constants
            )
        return comparaison

    def _verifier_fiabilite(self, carriere: Carriere) -> None:
        exigee = Fiabilite.depuis_texte(self.parametres.fiabilite_minimale)
        if exigee == Fiabilite.ESTIMEE:
            return
        disponible = self.macro.fiabilite_sur(
            carriere.premiere_annee, carriere.annee_liquidation
        )
        if disponible < exigee:
            raise DonneeInsuffisante(
                f"les séries macroéconomiques couvrant "
                f"{carriere.premiere_annee}-{carriere.annee_liquidation} sont de "
                f"fiabilité « {disponible} », inférieure au minimum exigé "
                f"« {exigee} ». Certifier les données ou abaisser "
                "Parametres.fiabilite_minimale."
            )
