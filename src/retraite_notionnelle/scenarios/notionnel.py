"""Scénarios 2 à 6 — les comptes notionnels.

**Scénario 2, rétroactif.** Le compte notionnel est ouvert à l'entrée dans la
vie active, ou à l'année d'origine de la répartition si la carrière a commencé
avant. Toute la carrière est recalculée : les cotisations réellement versées
alimentent le compte, la revalorisation applique le triple lock inversé année
par année depuis l'origine, et la pension est le solde divisé par le coefficient
de conversion à l'âge effectif de liquidation. Un départ à 55 ans dans un régime
spécial en 1985 est donc traité comme ce qu'il est : douze années de cotisations
en moins et douze années de rente en plus.

**Scénario 3, prospectif.** Les droits acquis jusqu'à l'année de bascule sont
figés selon les règles actuelles, convertis en capital notionnel d'ouverture,
puis le compte fonctionne en notionnel au-delà. C'est la variante qui respecte
les droits acquis — celle qu'une réforme réelle retiendrait.

La conversion des droits acquis pose une question qu'aucune convention ne
tranche seule : à quel capital notionnel correspond une pension annuelle promise
de X euros ? La réponse retenue ici est la seule cohérente avec le reste du
modèle — celle qui inverse la formule de liquidation :

.. math::  K_{\\text{ouverture}} = P_{\\text{acquise}} \\times G(a_c, B)

où :math:`P_{\\text{acquise}}` est la pension de droits figés à l'année de
bascule :math:`B` et :math:`G` le coefficient de conversion à l'âge :math:`a_c`.

Le choix de :math:`a_c` est le seul endroit du modèle où le passage aux comptes
notionnels peut, à lui seul, retirer quelque chose à des droits déjà ouverts. À
l'âge de référence (défaut), un assuré qui liquide avant cet âge voit son
capital d'ouverture minoré du rapport des diviseurs — l'anticipation est payée
une seconde fois, sur le passé. À l'âge effectif de liquidation, la conversion
est neutre. Le paramètre :attr:`Parametres.age_conversion_droits_acquis` permet
de mesurer l'écart entre les deux conventions.

**Scénarios 4 et 5 : les mêmes, part patronale comprise.** Ce sont exactement
les scénarios 2 et 3 — même carrière, même indexation, même liquidation, mêmes
droits acquis figés à la bascule — à une différence près, et une seule : ce qui
alimente le compte.

Les scénarios 2 et 3 n'y portent que la **part salariale** de la cotisation, ce
que l'assuré a supporté lui-même ; les scénarios 4 et 5 y ajoutent la **part
patronale**. Pour le privé, la répartition est dans la fiche du régime
(``part_salariale``) ; pour un agent public, dont la fiche ne porte que sa
retenue, la part patronale vient de
``legislation/contribution_employeur_public.csv`` — taux implicite de l'État de
1995 à 2005, taux appelé par le compte d'affectation spéciale depuis 2006, taux
CNRACL depuis 1948, T1 + T2 de la SNCF de 2007 à 2018 — et, là où aucune série
n'existe, elle est estimée par l'effort d'un salarié du privé de la même année.

Rien d'autre ne bouge, et c'est ce qui les rend lisibles : le 4 se lit contre le
2, le 5 contre le 3, et l'écart mesure une chose à la fois. Pour un non-salarié,
qui n'a pas d'employeur, les quatre scénarios se réduisent à deux.

Après la bascule, le régime unique remplace tous les régimes : la part patronale
y est celle du statut pivot privé, dont il hérite la répartition. Il n'y a donc
plus, après la bascule, de contribution publique à retrouver décret par décret —
la réforme l'a remplacée.

Ce que ces scénarios ne disent PAS. Les taux employeur publics sont des taux
d'ÉQUILIBRE, fixés pour que le compte tombe juste : 82,28 % en 2026 ne signifie
pas qu'un fonctionnaire acquiert 82 % de son traitement en droits nouveaux, mais
qu'il faut aujourd'hui cette contribution pour payer les pensions
d'aujourd'hui. Les porter au compte répond à une question précise — « et si tout
ce qui a été consacré aux pensions avait été porté au compte des actifs ? » — et
à elle seule.

**Scénario 6 : la proposition libérale.** C'est le scénario 4 — compte
rétroactif, cotisation salariale et patronale confondues, mêmes âges de départ,
même indexation, même liquidation — à deux différences près, et ce sont les deux
termes de la proposition du Parti libéral français.

Un **taux unique de 18 % à compter de la bascule**, salariale et patronale
additionnées, le même pour tous les statuts, prélevé une fois sur la
rémunération. Avant la bascule, rien ne change : ce qui a été cotisé sous le
système actuel est porté au compte tel qu'il a été prélevé, aux taux réels de
chaque régime, comme dans le scénario 4 — une personne née en 1975 cotise aux
taux réels de 1996 à 2025, puis à 18 % de 2026 à son départ
(``SourceCotisations.TAUX_HISTORIQUES_PUIS_UNIFORME``). Et une **garantie
vieillesse** qui remplace l'ASPA : allocation
différentielle, financée par l'impôt, qui porte la pension à 800 € par mois,
plus 250 € d'allocation d'isolement pour une personne seule — 1 050 € seul,
800 € par personne à deux. Le plancher est **individualisé** : chacun est
comparé au sien, et la pension du conjoint n'entre jamais dans le calcul. Là où
l'ASPA d'aujourd'hui, qui regarde le foyer, ne sert rien à un couple à 300 € et
1 500 €, la garantie sert 500 € au premier et rien au second.

La garantie garde de l'ASPA son âge — 65 ans — et sa place : une ligne à part,
servie en dernier, après la pension contributive. Elle est portée dans
:class:`GarantieVieillesse`, avec chacune de ses étapes, pour que la page puisse
dire ce qui vient des cotisations et ce qui vient de l'impôt.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..carriere import Carriere
from ..config import AgeConversionDroitsAcquis, Parametres, SituationFoyer
from ..donnees.chargement import Fiabilite
from ..moteur.age_reference import AgeReference, EcartAge
from ..moteur.compte import CompteNotionnel, ConstructeurCompte
from ..moteur.conversion import CoefficientConversion, Convertisseur
from ..moteur.fusion import RegimeFusionne
from .actuel import MinimumVieillesse, ScenarioActuel


@dataclass(frozen=True)
class GarantieVieillesse:
    """La garantie vieillesse du scénario 6, étape par étape.

    Une allocation différentielle : ce qui manque à la pension contributive
    pour atteindre le plancher. Le plancher est en euros de l'année de
    liquidation — les montants de la proposition sont fixés dans les euros
    d'une année et ramenés par l'indice des prix, comme l'ASPA du scénario 1
    entre deux ancres de son barème.
    """

    #: ``seul`` ou ``couple`` : ne joue que sur l'allocation d'isolement.
    situation: str
    #: L'allocation est-elle ouverte à l'âge de liquidation ? Même âge que
    #: l'ASPA : 65 ans, et le modèle ne suit pas l'assuré au-delà du départ.
    age_atteint: bool
    #: Coefficient de passage des euros de la proposition aux euros de la
    #: liquidation.
    coefficient_prix: float
    #: Garantie de base, annuelle, en euros de la liquidation.
    base_annuelle: float
    #: Allocation d'isolement, annuelle — nulle à deux.
    isolement_annuel: float
    #: ``base + isolement`` : le plancher auquel la pension est comparée.
    plancher_annuel: float
    #: La pension issue du compte notionnel seul, avant la garantie.
    pension_contributive: float
    #: Ce que la garantie ajoute : ``max(0, plancher - contributive)`` si l'âge
    #: est atteint, zéro sinon. C'est la part financée par l'impôt.
    complement: float

    @property
    def servie(self) -> bool:
        return self.complement > 0


@dataclass(frozen=True)
class DroitsAcquis:
    """Étapes de la conversion des droits figés en capital d'ouverture.

    Conservées telles quelles pour que la page de simulation puisse afficher la
    cascade complète : sans elles, le capital d'ouverture est un nombre qui
    tombe du ciel.
    """

    #: Pension que la carrière tronquée à la bascule ouvre selon les règles
    #: actuelles, avantages non contributifs retirés — en euros de la bascule.
    pension_figee: float
    #: Âge auquel le diviseur de conversion est pris.
    age_conversion: float
    #: Diviseur correspondant, à l'année de bascule.
    diviseur: float
    #: ``pension_figee × diviseur`` — le capital d'ouverture, en euros de la bascule.
    capital_a_la_bascule: float
    #: Revalorisation du capital d'ouverture, de la bascule à la liquidation.
    coefficient_revalorisation: float
    #: Capital d'ouverture revalorisé, en euros de la liquidation.
    capital: float


@dataclass
class ResultatNotionnel:
    """Pension issue d'un compte notionnel, et tout ce qui l'explique."""

    pension_annuelle: float
    capital_notionnel: float
    capital_droits_acquis: float
    compte: CompteNotionnel
    conversion: CoefficientConversion
    ecart_age: EcartAge
    capital_capitalisation: float
    fiabilite: Fiabilite
    libelle: str
    #: Détail de la conversion des droits figés — seulement en prospectif.
    droits_acquis: DroitsAcquis | None = None
    #: La garantie vieillesse et ses étapes — seulement dans le scénario 6, où
    #: ``pension_annuelle`` la comprend.
    garantie_vieillesse: GarantieVieillesse | None = None

    @property
    def pension_mensuelle(self) -> float:
        return self.pension_annuelle / 12.0

    @property
    def rente_capitalisation_annuelle(self) -> float:
        """Ce que vaudrait le compartiment de capitalisation, POUR MÉMOIRE.

        Le RAFP et les droits des anciennes assurances sociales ne sont pas
        convertis en capital notionnel : ils restent dans un compartiment
        distinct. Cette propriété dit ce qu'il donnerait s'il l'était, au même
        coefficient actuariel.

        **Ce n'est pas ce qui est servi.** Un régime provisionné n'est pas
        atteint par une réforme de la répartition : les six scénarios servent
        sa rente à son propre barème, celui du scénario 1
        (:attr:`ResultatActuel.pension_hors_repartition`), et c'est cette
        valeur-là qui est affichée. Celle-ci ne sert plus qu'à mesurer l'écart
        entre les deux règles.
        """
        if self.conversion.diviseur <= 0:
            return 0.0
        return self.capital_capitalisation / self.conversion.diviseur


class ScenarioNotionnel:
    """Produit les deux variantes de comptes notionnels."""

    def __init__(
        self,
        constructeur: ConstructeurCompte,
        convertisseur: Convertisseur,
        age_reference: AgeReference,
        scenario_actuel: ScenarioActuel,
        parametres: Parametres,
    ) -> None:
        self.constructeur = constructeur
        self.convertisseur = convertisseur
        self.age_reference = age_reference
        self.scenario_actuel = scenario_actuel
        self.parametres = parametres

    def _sexe(self, carriere: Carriere) -> str | None:
        from ..config import TableConversion

        if self.parametres.table_conversion is TableConversion.UNISEXE:
            return None
        return carriere.sexe

    # -- scénario 2 ----------------------------------------------------------

    def retroactif(self, carriere: Carriere,
                   regime_fusionne: RegimeFusionne | None = None,
                   libelle: str = "Comptes notionnels rétroactifs") -> ResultatNotionnel:
        """Comptes notionnels appliqués depuis l'origine de la répartition.

        Les scénarios 4 et 5 empruntent ce même chemin : ce qui les distingue du
        scénario 2 tient entièrement à ce qui alimente le compte, donc aux
        paramètres du constructeur, et non au calcul de la pension. Seul le
        libellé change ici.
        """
        annee_liquidation = carriere.annee_liquidation
        age_liquidation = carriere.age_liquidation or 0.0

        compte = self.constructeur.construire(
            carriere,
            annee_liquidation=annee_liquidation,
            annee_debut=carriere.premiere_annee,
            regime_fusionne=regime_fusionne,
        )
        conversion = self.convertisseur.coefficient(
            age_liquidation, annee_liquidation, self._sexe(carriere),
            carriere.mois_liquidation,
        )
        pension = compte.capital / conversion.diviseur

        return ResultatNotionnel(
            pension_annuelle=pension,
            capital_notionnel=compte.capital,
            capital_droits_acquis=0.0,
            compte=compte,
            conversion=conversion,
            ecart_age=self.age_reference.ecart(age_liquidation, annee_liquidation),
            capital_capitalisation=compte.capital_hors_repartition,
            fiabilite=min(compte.fiabilite, conversion.fiabilite),
            libelle=libelle,
        )

    # -- scénario 6 ----------------------------------------------------------

    def liberal(self, carriere: Carriere,
                regime_fusionne: RegimeFusionne | None = None,
                libelle: str = "Comptes notionnels rétroactifs, taux unique "
                               "dès la bascule et garantie vieillesse") -> ResultatNotionnel:
        """Le scénario 4 jusqu'à la bascule, 18 % ensuite, puis la garantie.

        Le compte est celui de :meth:`retroactif` : ce qui l'alimente — les
        taux réels jusqu'à la bascule, 18 % pour tous à compter d'elle — tient
        aux paramètres du constructeur, comme pour les scénarios 4 et 5. Ce
        que cette méthode ajoute, et elle seule, est la
        garantie : différentielle, individualisée, servie en dernier, et
        gardée à part pour que l'on sache ce qui vient de l'impôt.
        """
        resultat = self.retroactif(carriere, regime_fusionne, libelle=libelle)
        garantie = self._garantie_vieillesse(carriere, resultat.pension_annuelle)
        resultat.pension_annuelle += garantie.complement
        resultat.garantie_vieillesse = garantie
        return resultat

    def _garantie_vieillesse(self, carriere: Carriere,
                             pension_contributive: float) -> GarantieVieillesse:
        """Ce qui manque à la pension contributive pour atteindre le plancher.

        Le plancher d'une personne seule est la garantie de base plus
        l'allocation d'isolement ; celui d'une personne en couple est la
        garantie de base seule, et la pension du conjoint ne compte pas — c'est
        l'individualisation, et c'est ce qui sépare cette garantie de l'ASPA.
        L'âge est celui de l'ASPA, avec la même réserve : le modèle liquide et
        s'arrête, il ne suit pas l'assuré jusqu'à 65 ans.
        """
        parametres = self.parametres
        annee = carriere.annee_liquidation
        coefficient = self.constructeur.macro.coefficient_prix(
            parametres.annee_euros_garantie_vieillesse, annee
        )
        base = parametres.garantie_vieillesse_mensuelle * 12.0 * coefficient
        isolement = (
            parametres.allocation_isolement_mensuelle * 12.0 * coefficient
            if parametres.situation_foyer is SituationFoyer.SEUL else 0.0
        )
        plancher = base + isolement
        age_atteint = (carriere.age_liquidation or 0.0) >= MinimumVieillesse.AGE_OUVERTURE
        complement = (max(0.0, plancher - pension_contributive)
                      if age_atteint else 0.0)
        return GarantieVieillesse(
            situation=parametres.situation_foyer.value,
            age_atteint=age_atteint,
            coefficient_prix=coefficient,
            base_annuelle=base,
            isolement_annuel=isolement,
            plancher_annuel=plancher,
            pension_contributive=pension_contributive,
            complement=complement,
        )

    # -- scénario 3 ----------------------------------------------------------

    def prospectif(
        self, carriere: Carriere, regime_fusionne: RegimeFusionne,
        libelle: str = "Comptes notionnels à compter de la bascule",
    ) -> ResultatNotionnel:
        """Droits figés à la bascule, comptes notionnels au-delà.

        Pour un assuré dont la retraite est déjà liquidée à la bascule, ce
        scénario ne peut rien changer : ses droits sont intégralement acquis.
        La méthode renvoie alors sa pension actuelle, de sorte que le tableau
        comparatif reste lisible — un retraité de 2005 voit bien « aucun effet »
        sur la ligne 3, et non un chiffre recalculé qui n'aurait aucun sens.
        """
        annee_liquidation = carriere.annee_liquidation
        age_liquidation = carriere.age_liquidation or 0.0
        bascule = self.parametres.annee_bascule

        if annee_liquidation <= bascule:
            return self._deja_liquide(carriere)

        droits_acquis = self._droits_acquis(carriere, bascule)
        capital_acquis = droits_acquis.capital if droits_acquis else 0.0

        compte = self.constructeur.construire(
            carriere,
            annee_liquidation=annee_liquidation,
            annee_debut=bascule,
            regime_fusionne=regime_fusionne,
        )
        conversion = self.convertisseur.coefficient(
            age_liquidation, annee_liquidation, self._sexe(carriere),
            carriere.mois_liquidation,
        )
        capital_total = compte.capital + capital_acquis
        pension = capital_total / conversion.diviseur

        return ResultatNotionnel(
            pension_annuelle=pension,
            capital_notionnel=capital_total,
            capital_droits_acquis=capital_acquis,
            compte=compte,
            conversion=conversion,
            ecart_age=self.age_reference.ecart(age_liquidation, annee_liquidation),
            capital_capitalisation=compte.capital_hors_repartition,
            fiabilite=min(compte.fiabilite, conversion.fiabilite),
            libelle=libelle,
            droits_acquis=droits_acquis,
        )

    def _deja_liquide(self, carriere: Carriere) -> ResultatNotionnel:
        """Cas d'un assuré déjà retraité à la bascule : rien ne change."""
        annee_liquidation = carriere.annee_liquidation
        age_liquidation = carriere.age_liquidation or 0.0
        actuel = self.scenario_actuel.calculer(carriere)
        conversion = self.convertisseur.coefficient(
            age_liquidation, annee_liquidation, self._sexe(carriere),
            carriere.mois_liquidation,
        )
        compte = self.constructeur.construire(
            carriere,
            annee_liquidation=annee_liquidation,
            annee_debut=annee_liquidation,  # aucune cotisation postérieure
        )
        return ResultatNotionnel(
            pension_annuelle=actuel.pension_annuelle,
            capital_notionnel=actuel.pension_annuelle * conversion.diviseur,
            capital_droits_acquis=actuel.pension_annuelle * conversion.diviseur,
            compte=compte,
            conversion=conversion,
            ecart_age=self.age_reference.ecart(age_liquidation, annee_liquidation),
            capital_capitalisation=0.0,
            fiabilite=actuel.fiabilite,
            libelle="Retraite déjà liquidée à la bascule — droits inchangés",
        )

    def _droits_acquis(self, carriere: Carriere, bascule: int) -> DroitsAcquis | None:
        """Convertit les droits figés à la bascule en capital notionnel.

        Les droits sont ceux qu'aurait produits la carrière si elle s'était
        arrêtée à la bascule, calculés selon les règles actuelles mais
        DÉBARRASSÉS des avantages non contributifs — conformément au principe
        « seules les cotisations comptent », qui vaut aussi pour le passé.

        La valorisation se fait à l'année de bascule, sans décote ni surcote :
        on mesure des droits déjà ouverts, pas une liquidation anticipée.

        Reste l'âge auquel prendre le diviseur, et c'est le paramètre
        :attr:`Parametres.age_conversion_droits_acquis` qui tranche. Le défaut,
        l'ÂGE DE RÉFÉRENCE, est le seul endroit où l'âge de départ pèse sur les
        droits d'avant la bascule — la pension figée ci-dessus est calculée sans
        décote, il n'y a donc pas de première pénalité que celle-ci
        redoublerait. Prendre au contraire l'âge effectif de liquidation fait
        s'annuler les deux diviseurs et rend la part figée TOTALEMENT insensible
        à la date de départ : mesuré, travailler de 64 à 67 ans rapporte +16,3 %
        à la génération 1963 sous ``REFERENCE`` et seulement +4,3 % sous
        ``LIQUIDATION``. Pour les générations de transition, dont la pension est
        presque entièrement figée, le second réglage revient à ne plus faire
        payer le départ anticipé. Dans les deux cas, l'écart de longévité entre
        la bascule et la liquidation subsiste.
        """
        lignes_avant = [l for l in carriere.lignes if l.annee < bascule]
        if not lignes_avant:
            return None

        carriere_tronquee = Carriere(
            annee_naissance=carriere.annee_naissance,
            sexe=carriere.sexe,
            lignes=list(lignes_avant),
            # L'année de liquidation de cette carrière fictive doit être
            # l'année de bascule : c'est en euros de cette année-là que les
            # droits acquis sont valorisés.
            age_liquidation=float(bascule - carriere.annee_naissance),
            nombre_enfants=0,  # avantages familiaux neutralisés
            identifiant=f"{carriere.identifiant} (droits figés {bascule})",
        )
        droits = self.scenario_actuel.calculer(
            carriere_tronquee,
            ignorer_penalite_age=True,
            avantages_non_contributifs=False,
        )

        if self.parametres.age_conversion_droits_acquis is AgeConversionDroitsAcquis.REFERENCE:
            age_conversion = self.age_reference.age(bascule)
        else:
            age_conversion = carriere.age_liquidation or self.age_reference.age(bascule)
        conversion = self.convertisseur.coefficient(
            age_conversion, bascule, self._sexe(carriere)
        )
        capital_a_la_bascule = droits.pension_annuelle * conversion.diviseur

        # Le capital d'ouverture se revalorise ensuite comme tout compte notionnel.
        coefficient = self.constructeur.indexation.coefficient(
            bascule, carriere.annee_liquidation
        )
        return DroitsAcquis(
            pension_figee=droits.pension_annuelle,
            age_conversion=age_conversion,
            diviseur=conversion.diviseur,
            capital_a_la_bascule=capital_a_la_bascule,
            coefficient_revalorisation=coefficient,
            capital=capital_a_la_bascule * coefficient,
        )
