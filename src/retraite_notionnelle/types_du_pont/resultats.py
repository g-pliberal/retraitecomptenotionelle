"""Les résultats des scénarios que le pont échange (action 161, étape 1 du
retrait des règles Python) : celui du scénario 1 et celui d'un univers
notionnel, la garantie vieillesse de la proposition, sans aucun corps de
règle. Les fichiers de ``scenarios/`` les réimportent le temps du retrait.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..donnees.chargement import Fiabilite
from .droit import (OUVERTE, AvantageApplique, ChefDExploitation, Cumul, DemandeExaminee,
                    DroitsApresDepart, ExploitantAgricole, MinimumEcrete, PensionRegime,
                    PetitePension)
from .moteur import Capitalisation, CoefficientConversion, CompteNotionnel, EcartAge


@dataclass(frozen=True)
class DepartServi:
    """Ce qu'un départ fait servir, quand les régimes liquident à des dates
    différentes (:mod:`~retraite_notionnelle.droit.departs`)."""

    #: La date d'effet (AAAA-MM-JJ), et ce qui la date : ``depart``,
    #: ``ouverture``, ``sortie`` ou ``demande``.
    date_effet: str
    motif: str
    regimes: tuple[str, ...]
    #: Ce que ses pensions servent par an, majoration pour enfants comprise :
    #: en euros du départ déclaré, puis à sa date d'effet, dans ses euros.
    montant: float
    montant_a_l_effet: float

    def donnees(self) -> dict:
        return {"date_effet": self.date_effet, "motif": self.motif,
                "regimes": list(self.regimes), "montant": self.montant,
                "montant_a_l_effet": self.montant_a_l_effet}


@dataclass(frozen=True)
class ProgressiveServie:
    """Ce qu'une retraite progressive sert avant le départ
    (:mod:`~retraite_notionnelle.droit.progressive`), ou ce qui la ferme."""

    #: La date d'effet (AAAA-MM-JJ) et la quotité du temps partiel.
    date_effet: str
    quotite: float
    #: ``ouverte``, ou ce qui la ferme : ``avant_1988``, ``activite``,
    #: ``regimes``, ``quotite``, ``age``, ``duree``.
    motif: str
    #: La fraction servie, nulle quand la demande n'est pas ouverte.
    fraction: float
    regimes: tuple[str, ...]
    #: La pension provisoire entière, et la fraction servie, par an, à sa
    #: date d'effet et dans ses euros.
    montant_provisoire: float
    montant_servi: float
    age_minimum: float | None
    duree_requise: int | None
    #: La durée d'assurance à sa date d'effet, tous régimes.
    trimestres: int | None
    #: La pension complète se recalcule-t-elle au départ ? Non avant le décret
    #: du 8 juin 2006 : elle était la pension provisoire.
    recalculee: bool = True

    @property
    def ouverte(self) -> bool:
        return self.motif == OUVERTE

    def donnees(self) -> dict:
        return {"date_effet": self.date_effet, "quotite": self.quotite,
                "motif": self.motif, "fraction": self.fraction,
                "regimes": list(self.regimes),
                "montant_provisoire": self.montant_provisoire,
                "montant_servi": self.montant_servi,
                "age_minimum": self.age_minimum, "duree_requise": self.duree_requise,
                "trimestres": self.trimestres, "recalculee": self.recalculee}


@dataclass
class ResultatActuel:
    pension_annuelle: float
    pensions_par_regime: list[PensionRegime] = field(default_factory=list)
    #: Avantages non contributifs effectivement appliqués, et leur effet.
    avantages_appliques: list[AvantageApplique] = field(default_factory=list)
    #: Total des pensions de régime avant tout avantage non contributif,
    #: capitalisation déduite comme dans :attr:`pension_annuelle`.
    total_contributif: float = 0.0
    #: Rente des régimes PROVISIONNÉS — RAFP, anciennes assurances sociales —
    #: retirée de :attr:`pension_annuelle` et servie à part. Ils ne relèvent pas
    #: de la répartition : la réforme simulée ne les atteint pas, et les cinq
    #: scénarios les servent donc à l'identique, hors comparaison.
    pension_hors_repartition: float = 0.0
    trimestres_valides: int = 0
    #: Ceux d'entre eux que des périodes hors de France apportent, pour le
    #: taux seulement (fiche ``totalisation_des_periodes_etrangeres``).
    trimestres_etrangers: int = 0
    trimestres_requis: int = 0
    taux_liquidation: float = 0.0
    minimum_applique: bool = False
    #: Âge le plus précoce auquel le droit ouvre cette liquidation, tous
    #: dispositifs compris. ``None`` quand aucun régime en annuités n'en fixe.
    age_ouverture_opposable: float | None = None
    #: La liquidation demandée est-elle ouverte par le droit à cet âge ?
    #: Quand elle ne l'est pas, le montant reste calculé — il faut bien
    #: comparer les scénarios sur la même carrière — mais il ne décrit aucune
    #: pension que le système actuel servirait. C'est un contrefactuel, et le
    #: modèle le dit maintenant au lieu de le laisser croire.
    liquidation_ouverte: bool = True
    #: Ce qui ouvre la liquidation : ``age_legal``, ``carriere_longue``, ou
    #: ``non_ouverte``.
    motif_ouverture: str = "age_legal"
    fiabilite: Fiabilite = Fiabilite.ESTIMEE
    #: Les départs, quand les régimes liquident à des dates différentes
    #: (:func:`resultat_des_departs`) ; vide pour un départ unique. Les
    #: montants du résultat sont alors ceux du départ déclaré : la pension
    #: complète, chaque pension y étant menée ou ramenée.
    departs: tuple[DepartServi, ...] = ()
    #: Les pensions dont la carrière dit la date de demande, et la date où
    #: chacune est servie (:class:`~retraite_notionnelle.droit.departs.DemandeExaminee`) ;
    #: vide quand elle n'en dit aucune.
    demandes: tuple[DemandeExaminee, ...] = ()
    #: La retraite progressive que la carrière demande, ouverte ou non
    #: (:class:`ProgressiveServie`) ; ``None`` sans demande. La pension du
    #: résultat reste la pension complète, au départ.
    retraite_progressive: ProgressiveServie | None = None
    #: L'activité exercée après le départ, et ce que chaque pension en garde
    #: pendant qu'elle dure (:mod:`~retraite_notionnelle.droit.cumul`) ;
    #: ``None`` sans elle. La pension du résultat reste celle du départ,
    #: entière : le cumul dit ce qui n'en est pas servi, et quand.
    cumul: Cumul | None = None
    #: Les droits que cette activité ouvre, ou non, et la nouvelle pension
    #: qu'elle constitue (:mod:`~retraite_notionnelle.droit.seconde`) ; hors
    #: de la pension du résultat, qui reste celle du départ.
    droits_apres_depart: DroitsApresDepart | None = None
    #: Le minimum contributif servi au départ, et ce que sa révision relit
    #: quand une pension étrangère commence après lui (R. 173-8,
    #: :func:`~retraite_notionnelle.revalorisation.faire_vivre`) ; ``None``
    #: sans lui, ou quand les régimes liquident à des dates différentes.
    minimum_ecrete: MinimumEcrete | None = None
    #: Ce que la majoration exceptionnelle de septembre 2023 relit des
    #: pensions que le minimum contributif regarde, celles de chaque départ
    #: (:func:`~retraite_notionnelle.revalorisation.majorer_les_petites_pensions`).
    petites_pensions: tuple[PetitePension, ...] = ()
    #: Ce que le relèvement des exploitants de septembre 2023 relit
    #: (:func:`~retraite_notionnelle.revalorisation.relever_les_exploitants`) ;
    #: ``None`` sans RCO.
    chef_d_exploitation: ChefDExploitation | None = None
    #: Ce que la révision des pensions agricoles déjà liquidées relit
    #: (:func:`~retraite_notionnelle.revalorisation.reviser_les_exploitants`) ;
    #: ``None`` sans pension de base agricole.
    exploitant_agricole: ExploitantAgricole | None = None

    @property
    def pension_mensuelle(self) -> float:
        return self.pension_annuelle / 12.0


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
    #: L'allocation est-elle ouverte DÈS LA LIQUIDATION ? Même âge que l'ASPA :
    #: 65 ans. Faux pour qui part plus tôt, sans que cela lui retire rien : la
    #: garantie s'ouvre alors à 65 ans, et ``annee_ouverture`` dit quand.
    age_atteint: bool
    #: Année où l'allocation s'ouvre : celle de la liquidation si elle a lieu à
    #: 65 ans ou plus, celle des 65 ans sinon.
    annee_ouverture: int
    #: Coefficient de passage des euros de la proposition aux euros de la
    #: liquidation.
    coefficient_prix: float
    #: Garantie de base, annuelle, en euros de la liquidation.
    base_annuelle: float
    #: Allocation d'isolement, annuelle — nulle à deux.
    isolement_annuel: float
    #: ``base + isolement`` : le plancher auquel les ressources sont comparées.
    plancher_annuel: float
    #: La pension issue du compte notionnel seul, avant la garantie.
    pension_contributive: float
    #: La rente du pilier capitalisé obligatoire, nulle avant la bascule ou si
    #: le pilier est désactivé.
    rente_capitalisee: float
    #: ``pension_contributive + rente_capitalisee + pensions_etrangeres`` :
    #: l'ENSEMBLE des retraites obligatoires, les 18 % de répartition, les 5 %
    #: capitalisés, et ce qu'un autre État sert. C'est cela que le plancher
    #: regarde, et non la seule répartition : toutes sont obligatoires, et une
    #: allocation sous condition de ressources les compte toutes.
    ressources: float
    #: Ce que la PENSION CONTRIBUTIVE gagne, EN TERMES RÉELS, entre la
    #: liquidation et l'ouverture de la garantie. Vaut 1 quand les deux
    #: coïncident. La rente du pilier n'en gagne rien : voir ``erosion_rente``.
    #:
    #: Ce coefficient existe parce que les deux termes de la comparaison ne
    #: suivent pas la même règle : la pension notionnelle est revalorisée sur
    #: la masse salariale, le plancher sur les prix comme l'ASPA — article
    #: L. 816-2 du code de la sécurité sociale, qui renvoie au coefficient de
    #: l'article L. 161-25. Leur écart n'est donc PAS invariant entre 62 et
    #: 65 ans : la pension monte d'environ sept dixièmes de point par an
    #: au-dessus du plancher, et le complément dû à 65 ans est plus petit que
    #: celui qu'on calculerait au départ. Le modèle l'a longtemps affirmé
    #: invariant ; c'était vrai du modèle, qui figeait alors les pensions en
    #: euros constants, et faux de la proposition.
    revalorisation_differee: float
    #: ``pension_contributive × revalorisation_differee + rente_capitalisee ×
    #: erosion_rente + pensions_etrangeres`` : ce dont la personne dispose
    #: l'année où la garantie s'ouvre, dans les euros de la liquidation.
    ressources_a_l_ouverture: float
    #: Ce que la garantie ajoute à compter de ``annee_ouverture`` : le barème
    #: dégressif (``garantie.complement_garantie``) appliqué au plancher et à
    #: ``ressources_a_l_ouverture``. C'est la part financée par l'impôt. Nulle
    #: pour qui réside hors de France.
    complement: float
    #: Ce que la rente du pilier, NOMINALE et constante, perd en termes réels
    #: entre la liquidation et l'ouverture : le seul rapport des prix. Vaut 1
    #: quand les deux coïncident.
    erosion_rente: float = 1.0
    #: L'État où la personne réside hors de France, si elle le déclare : la
    #: garantie ne s'y sert pas, comme l'ASPA qu'elle remplace (fiche
    #: ``garantie_vieillesse``).
    residence: str | None = None
    #: Les pensions qu'un autre État sert à l'ouverture, en euros de la
    #: liquidation : des retraites obligatoires elles aussi, que la garantie
    #: compte comme l'ASPA qu'elle remplace (fiche ``garantie_vieillesse``).
    pensions_etrangeres: float = 0.0
    #: La condition de résidence de l'ASPA, que la garantie garde, à
    #: l'ouverture : fausse pour qui réside hors de France, ou n'y passe pas
    #: assez de mois par an.
    condition_de_residence: bool = True

    @property
    def servie(self) -> bool:
        """La garantie sert-elle quelque chose, au plus tard à 65 ans ?"""
        return self.complement > 0

    @property
    def servie_a_la_liquidation(self) -> bool:
        """Et le sert-elle DÈS le départ, ou seulement à 65 ans ?

        C'est cette propriété, et non :attr:`servie`, qui décide si le montant
        entre dans la pension affichée : avant 65 ans, on ne touche pas le
        minimum vieillesse.
        """
        return self.age_atteint and self.complement > 0

    @property
    def differee(self) -> bool:
        """La garantie est-elle due, mais plus tard ?"""
        return self.servie and not self.age_atteint


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
    #: Le pilier capitalisé — seulement dans le scénario 6, et il porte les
    #: deux cotisations : les 5 % obligatoires et les 5 % volontaires.
    #: ``pension_annuelle`` ne le comprend PAS : la rente qu'il sert n'est pas
    #: une pension de répartition, elle ne se revalorise pas comme elle, elle
    #: se transmet là où l'autre ne se transmet pas, et les confondre ferait
    #: passer pour un rendement de la répartition ce qui vient d'un marché
    #: obligataire. Le total est à :attr:`pension_totale`, et il est toujours
    #: affiché comme une somme de deux lignes nommées.
    capitalisation: Capitalisation | None = None

    @property
    def pension_mensuelle(self) -> float:
        return self.pension_annuelle / 12.0

    @property
    def rente_capitalisation_obligatoire(self) -> float:
        """Rente annuelle servie par le pilier capitalisé, nulle sans lui.

        Les deux cotisations réunies, l'obligatoire et la volontaire : c'est ce
        que le pilier sert, et le nom de la propriété est resté celui qu'il
        avait quand il n'y en avait qu'une. Les deux parts se lisent à
        :attr:`rente_capitalisation_volontaire` et à sa complémentaire.
        """
        return self.capitalisation.rente_annuelle if self.capitalisation else 0.0

    @property
    def rente_capitalisation_volontaire(self) -> float:
        """Ce que servent les cinq points rendus par la proposition, puis remis.

        C'est la ligne qui rend la comparaison honnête : sans elle, le scénario
        6 est servi par 23 points quand le scénario 1 l'est par 28.
        """
        return self.capitalisation.rente_volontaire if self.capitalisation else 0.0

    @property
    def pension_totale(self) -> float:
        """Répartition et capitalisation réunies — les deux lignes du scénario.

        À n'employer que là où le total a un sens, et jamais sans dire de quoi
        il est fait : l'une des deux lignes est une pension mutualisée qu'aucun
        héritier ne touchera, l'autre une rente issue d'un capital qui, lui, se
        serait transmis.
        """
        return self.pension_annuelle + self.rente_capitalisation_obligatoire

    @property
    def pension_totale_mensuelle(self) -> float:
        return self.pension_totale / 12.0

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
