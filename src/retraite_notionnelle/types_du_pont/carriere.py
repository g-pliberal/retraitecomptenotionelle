"""L'année de carrière que le pont échange (action 161, étape 1 du retrait des
règles Python), que ``carriere.py`` réimporte le temps du retrait, et la carrière nue
(étape 1 bis) : ses champs, sa validation, et ce qui se lit de ses lignes, du
calendrier et de sa chronologie, sans aucune règle du droit. Les règles de la
carrière restent dans ``carriere.py``, sur une classe qui hérite de celle-ci,
le temps du retrait : elle seule remplit la chronologie d'une carrière bâtie
ligne à ligne. Le métier d'une carrière (``Metier``) et les noms de ses profils
de rémunération l'ont rejointe à l'étape 4 : les cas types les donnent au
portage sans charger les règles. Les faits que la carrière lit de sa
chronologie (``PensionDInvalidite``, ``Conjoint``…) l'ont rejointe à leur tour :
la façade des tests les lit au portage sous ces types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property

from .. import chronologie as chrono
from ..calendrier import MOIS_PAR_AN, DateMois, en_mois, origine_des_ages



@dataclass(frozen=True)
class PensionDInvalidite:
    """La pension d'invalidité de la Sécurité sociale qu'une personne touche
    (fiche ``pension_d_invalidite_substituee``)."""

    #: Le mois où elle a commencé.
    debut: DateMois
    #: La présomption qui la pose, quand elle n'est pas déclarée.
    presomption: str | None = None
    #: Les affiliations de l'année où elle commence puis de l'année d'avant,
    #: l'activité principale de chacune en tête : le régime qui la sert est
    #: celui dont la personne relevait quand l'invalidité est survenue.
    affiliations: tuple[str, ...] = ()
    #: Sa catégorie, quand elle se déclare (L. 341-4) ; sinon, le plancher de
    #: la pension substituée la présume (``droit/invalidite.py``).
    categorie: int | None = None


@dataclass(frozen=True)
class RadiationPourInvalidite:
    """La radiation des cadres pour invalidité d'un fonctionnaire (fiche
    ``retraite_pour_invalidite_fonction_publique``)."""

    #: Le mois où elle tombe : celui où la pension prend effet.
    date: DateMois
    #: Les affiliations de l'année où elle tombe puis de l'année d'avant,
    #: l'activité principale de chacune en tête : l'emploi qu'elle clôt est
    #: le premier de fonctionnaire civil qu'elles portent. Radié en juin, et
    #: salarié ensuite, l'emploi clos ne porte plus que l'année d'avant.
    affiliations: tuple[str, ...] = ()
    #: L'invalidité est-elle imputable au service (L. 27, L. 28) ?
    imputable: bool = False
    #: Le taux d'invalidité reconnu, en pour cent, s'il est dit.
    taux: float | None = None


@dataclass(frozen=True)
class IncapacitePermanente:
    """L'incapacité permanente qu'une personne déclare (fiche
    ``retraite_anticipee_handicap``) : réputée continue jusqu'au départ."""

    #: Le mois depuis lequel elle atteint son taux.
    debut: DateMois
    #: Le taux qu'elle atteint au moins, en pour cent.
    taux: int


@dataclass(frozen=True)
class PeriodeALEtranger:
    """Une période passée hors de France (fiche
    ``totalisation_des_periodes_etrangeres``)."""

    #: Le code de l'État, celui du tableau des accords, ou ``autre``.
    pays: str
    #: Le mois où elle commence, et celui où elle finit, exclu.
    debut: DateMois
    fin: DateMois
    #: ``salariee`` ou ``non_salariee`` : une convention ne coordonne souvent
    #: que les salariés.
    activite: str = "salariee"


@dataclass(frozen=True)
class PensionEtrangere:
    """Une pension que le régime d'un autre État sert : une liquidation
    observée (docs/architecture.md, § 5.5 ; fiche
    ``minimum_contributif_international``)."""

    #: Le code de l'État qui la sert, ou ``autre``.
    pays: str
    #: Le mois où elle commence.
    debut: DateMois
    #: Son montant brut mensuel, en euros de ce mois.
    mensuel: float


@dataclass(frozen=True)
class ReversionAgricole:
    """La réversion que le régime des non-salariés agricoles sert à la
    personne, veuve ou veuf d'un de ses assurés (L. 732-41 à L. 732-46) : un
    acte de sa caisse, que la pension majorée de référence lit (D. 732-110,
    II, 2° ; D. 732-112 ; D. 732-114)."""

    #: Le mois où elle commence.
    debut: DateMois
    #: Son montant brut mensuel, en euros de ce mois, nul quand les ressources
    #: l'absorbent.
    mensuel: float


@dataclass(frozen=True)
class Conjoint:
    """Le conjoint d'une personne, tel que la chronologie le porte : ce que la
    réversion lit du survivant (docs/architecture.md, § 5.1)."""

    personne: str
    #: Sa naissance (AAAA-MM-JJ).
    naissance: str
    sexe: str
    #: La date du mariage (AAAA-MM-JJ), déclarée ou présumée.
    mariage: str
    mariage_presume: bool
    #: Ses ressources annuelles, s'il les déclare ; ``None`` laisse la
    #: présomption ``ressources_du_survivant`` s'appliquer.
    ressources: float | None
    #: La date (AAAA-MM-JJ) où son invalidité est reconnue, s'il la déclare :
    #: elle lève l'âge de la réversion de l'Agirc-Arrco (fiche
    #: ``reversion_agirc_arrco``).
    invalidite: str | None = None
    #: La part de ``ressources`` que son activité lui rapporte, s'il la dit :
    #: le plafond de la réversion l'abat après cinquante-cinq ans (R. 353-1).
    revenus_d_activite: float | None = None
    #: Le jour où cette activité cesse (AAAA-MM-JJ), s'il le dit : ses
    #: revenus ne comptent plus, et sa réversion se révise le mois qui suit.
    fin_d_activite: str | None = None
    #: Ses revenus annuels d'activité qui varient ensuite, s'il le dit —
    #: un salaire qui change, une activité reprise, rien quand elle cesse :
    #: ``(jour, montant)`` à partir de chaque jour, dans l'ordre ; sa réversion
    #: se révise le mois qui suit chacun.
    variations_d_activite: tuple[tuple[str, float], ...] = ()
    #: La forme de l'union où il vit après le décès — mariage, pacs ou
    #: concubinage —, et les ressources annuelles que son nouveau conjoint y
    #: apporte, s'il les dit : le plafond de la réversion lit alors le
    #: ménage. ``None`` laisse la présomption ``survivant_seul`` s'appliquer.
    nouvelle_union: str | None = None
    ressources_du_nouveau_conjoint: float | None = None
    #: Le jour où commence ce ménage (AAAA-MM-JJ) : celui qu'il dit, ou le
    #: décès.
    nouvelle_union_depuis: str | None = None
    #: Le jour où il se défait (AAAA-MM-JJ), s'il le dit : il revit seul.
    nouvelle_union_fin: str | None = None
    #: Les ressources annuelles de son nouveau conjoint qui varient pendant
    #: leur union, s'il le dit : ``(jour, montant)`` à partir de chaque jour,
    #: dans l'ordre ; sa réversion se révise le mois qui suit chacun.
    variations_du_nouveau_conjoint: tuple[tuple[str, float], ...] = ()
    #: Le jour où sa propre retraite prend effet (AAAA-MM-JJ), s'il le dit :
    #: ses ressources hors de ses revenus d'activité, que le modèle tient pour
    #: ses retraites personnelles, ne commencent qu'alors. ``None`` laisse la
    #: présomption ``retraites_du_survivant_servies`` les tenir pour servies
    #: dès la date d'effet de la réversion.
    retraite: str | None = None


@dataclass(frozen=True)
class ExConjoint:
    """Un précédent conjoint de la personne, divorcé, tel que la chronologie le
    porte : ce que le partage de la réversion lit (L. 353-3)."""

    personne: str
    #: Le mariage et le divorce qui l'a clos (AAAA-MM-JJ).
    mariage: str
    divorce: str
    #: Son remariage (AAAA-MM-JJ), s'il le dit.
    remariage: str | None = None


@dataclass(frozen=True)
class AnneeCarriere:
    """Une année de carrière."""

    annee: int
    #: Revenu d'activité brut de l'année, EN EUROS COURANTS DE CETTE ANNÉE-LÀ.
    revenu: float
    #: Statut d'affiliation (clé de ``legislation/affiliations.yaml``).
    affiliation: str
    #: Nature de la période.
    type_periode: str = "emploi"
    #: Quotité travaillée (1.0 = temps plein) : celle des mois de retraite
    #: progressive, en moyenne sur l'année. Les services de la fonction
    #: publique la comptent pour leur durée réelle, et le traitement de
    #: référence se lit à temps plein (``droit/progressive.py``).
    quotite: float = 1.0
    #: Trimestres validés au sens du système ACTUEL (utilisé par le seul
    #: scénario « système actuel »).
    trimestres_valides: int = 4
    #: Des cotisations retraite ont-elles réellement été versées ?
    #: C'est le seul critère qui compte pour les comptes notionnels.
    cotisations_versees: bool = True
    #: Salaire de référence d'avant l'interruption. Les régimes
    #: complémentaires attribuent des points sur cette base pendant les
    #: périodes indemnisées : payés par l'Unédic pour le chômage, attribués
    #: « sans contrepartie de cotisations » pour la maladie, la maternité,
    #: l'invalidité et l'accident du travail.
    revenu_reference: float = 0.0
    #: Familles de régimes qui attribuent des points sur ``revenu_reference``
    #: alors que l'année n'est pas travaillée : ce que le scénario 1 sert.
    familles_cotisantes: tuple[str, ...] = ()
    #: Celles d'entre elles qui ENCAISSENT de vraies cotisations pendant
    #: l'année, versées par un tiers : l'Agirc-Arrco pendant un chômage
    #: indemnisé, que l'Unédic paie. C'est ce que le compte notionnel porte,
    #: lui qui ne porte que ce qui a été versé. Vide pour la maladie : ses
    #: points sont gratuits, et le compte les portait comme payés jusqu'au
    #: 23 septembre 2026.
    familles_financees: tuple[str, ...] = ()
    #: Part de primes dans le revenu (fonction publique) : assiette du RAFP.
    part_primes: float = 0.0
    #: Part de l'année civile réellement couverte par la carrière. Vaut un
    #: partout, sauf aux deux bords : l'année d'entrée dans la vie active et
    #: celle de la liquidation sont incomplètes, et ``revenu`` ne porte alors
    #: que ce qui a été perçu pendant ces mois-là. Le plafond de la Sécurité
    #: sociale se proratise sur cette même fraction, comme le veut l'article
    #: R. 242-2 : une demi-année de travail n'ouvre qu'un demi-plafond.
    fraction_annee: float = 1.0
    #: Salaire forfaitaire porté au compte du régime de base au titre de
    #: l'assurance vieillesse des parents au foyer. Ce n'est pas un revenu
    #: d'activité — l'année n'est pas cotisée par l'assuré — mais la CNAF
    #: cotise pour lui sur cette assiette, et le salaire entre dans le salaire
    #: annuel moyen. Une période assimilée, elle, n'y entre jamais.
    revenu_avpf: float = 0.0
    #: ASSIETTE MINIMALE du régime de base d'un indépendant, en euros de
    #: l'année : l'artisan, le commerçant ou le libéral qui déclare moins
    #: cotise quand même sur ce montant (D. 633-2, D. 642-4), qui valide ses
    #: trimestres et entre dans son salaire annuel moyen ou ses points. Nulle
    #: pour tout autre statut. Voir `legislation/assiette_minimale_independants.csv`.
    assiette_minimale_base: float = 0.0
    #: Le motif qui DISPENSE la ligne de l'assiette minimale, quand le texte
    #: l'en dispense cette année-là (L. 613-11, D. 642-4 ;
    #: ``legislation/dispenses_assiette_minimale.yaml``) : le RSA, la prime
    #: d'activité, l'activité accessoire saisonnière… Vide sinon.
    #: ``assiette_minimale_base`` est alors nulle, et celle des complémentaires
    #: des libéraux tombe aussi quand le motif les couvre.
    dispense_assiette_minimale: str = ""
    #: Le barème de la Lodeom de l'employeur d'outre-mer, que la fiche de paie
    #: met à la place de la réduction générale (L. 752-3-2) ; vide sinon, et
    #: sur une année non cotisée. Il ne change aucun droit.
    lodeom: str = ""
    #: Le DÉPARTEMENT D'OUTRE-MER où l'assuré a travaillé dans l'année — une
    #: clef de :data:`~retraite_notionnelle.donnees.macro.DEPARTEMENTS_D_OUTRE_MER` —,
    #: qui donne à ses trimestres leur seuil (R. 753-21, R. 351-9) ; vide en
    #: métropole, et sur une année non cotisée.
    outre_mer: str = ""
    #: Cette année entre-t-elle dans les SERVICES d'un régime de la fonction
    #: publique ? Ce régime-là ne proratise pas sur la durée d'assurance mais
    #: sur les services et bonifications (L. 13 du code des pensions), et
    #: l'article L. 9 écarte le temps passé dans une position statutaire sans
    #: services effectifs, hors la liste qu'il énumère. Une année d'emploi en
    #: est toujours ; une année de chômage n'en est jamais — un fonctionnaire
    #: au chômage n'est d'ailleurs plus fonctionnaire.
    services_fonction_publique: bool = True
    #: Limite, en trimestres PAR ENFANT, des services que cette année ouvre.
    #: Zéro quand il n'y en a pas. Le 1° de L. 9 excepte le congé parental
    #: « dans la limite de trois ans par enfant » : le décompte se fait donc
    #: sur toute la carrière, pas année par année, et c'est le scénario qui
    #: tient le budget.
    services_plafond_trimestres_par_enfant: int = 0
    #: Nature de cette année au sens de l'article D. 351-1-2, qui la RÉPUTE
    #: COTISÉE pour la carrière longue sous la limite que sa rédaction à la
    #: date d'effet fixe (``CarriereLongue`` de ``moteur/js/scenario-actuel.js``).
    #: Vide : jamais réputée cotisée.
    reputes_cotises_nature: str = ""
    #: Salaire porté au compte du régime général quand l'année est RÉTABLIE :
    #: celle d'un fonctionnaire parti sans droit à pension, que L. 65 du code
    #: des pensions rétablit au régime général et à l'Ircantec. C'est le
    #: dernier traitement soumis à retenue, sur la fraction de l'année
    #: (D. 173-16) ; le plafond de l'année s'applique ensuite. Zéro pour toute
    #: autre année : seul le scénario 1 le renseigne, sur sa propre copie de
    #: la carrière (voir `droit.coordonner.retablir`).
    revenu_retabli: float = 0.0
    #: Les jours de services que le RELEVÉ porte pour l'année : ses trimestres,
    #: fractions comprises, à quatre-vingt-dix jours le trimestre. Le code des
    #: pensions compte ses services au jour et ne les arrondit qu'au décompte
    #: final (R. 26) : « 3.33 » dit dix mois. ``None`` hors d'un relevé qui
    #: les déclare : les mois de la ligne font alors ses jours
    #: (``joursDeLaLigne`` de ``moteur/js/droit/compter.js``).
    jours_de_services: int | None = None
    #: L'activité du MICRO-ENTREPRENEUR dont la ligne lit le revenu abattu
    #: (``saisie.ACTIVITES_MICRO``) ; vide hors du micro-social. Ses trimestres
    #: se valident sur le revenu que sa cotisation achète, non sur le revenu
    #: abattu (``legislation/micro_social.yaml``), et ce revenu cotisé est celui
    #: de son revenu annuel moyen (:func:`revenu_cotise`) ; l'assiette minimale
    #: ne le touche pas.
    micro: str = ""
    #: La ligne d'un CONJOINT COLLABORATEUR cotise-t-elle sur le forfait du
    #: tiers du plafond, faute d'assiette saisie (D. 633-19-2, 1° ;
    #: :func:`assiette_du_conjoint_collaborateur`) ? Sa complémentaire n'est
    #: assise sur l'avant-dernière année qu'à l'option, une fraction du revenu
    #: du chef (D. 635-10-2 ; ``revenuALOption`` de ``moteur/js/droit/acquerir.js``).
    forfait_conjoint: bool = False
    #: La ligne d'une activité que l'assuré déclare CUMULÉE à l'activité
    #: principale de l'année (:attr:`Metier.cumul`), que bâtit
    #: :func:`_lignes_du_parcours` ; faux pour l'activité principale, et sur un
    #: relevé, qui ne le dit pas : ce que la caisse y a reporté fait foi.
    cumulee: bool = False
    #: L'ACTIVITÉ ACCESSOIRE DE L'AGENT D'UN RÉGIME SPÉCIAL, de 1981 à 2014 :
    #: elle n'ouvre aucun droit au régime général (D. 171-4, rédaction du
    #: 21 décembre 1985). Faux partout ailleurs : seul le scénario 1 la marque,
    #: sur sa propre copie de la carrière
    #: (``ecarterLesAccessoires`` de ``moteur/js/droit/coordonner.js``).
    accessoire_d_un_regime_special: bool = False

    @property
    def cotise(self) -> bool:
        return self.cotisations_versees and self.revenu > 0

    @property
    def revenu_annualise(self) -> float:
        """Revenu ramené à l'année pleine.

        C'est le traitement en vigueur, celui que liquident les régimes servant
        sur le dernier traitement ou les six derniers mois de service — et non
        la somme réellement perçue pendant une année tronquée.
        """
        if self.fraction_annee <= 0:
            return 0.0
        return self.revenu / self.fraction_annee


@dataclass
class Carriere:
    """Carrière complète d'un assuré.

    **Une ligne par année ET PAR ACTIVITÉ.** Une année ne porte d'ordinaire
    qu'une ligne ; celle où l'assuré a exercé deux activités à la fois en porte
    une par statut, et deux lignes de la même année ne partagent jamais leur
    statut. La première ligne d'une année est l'activité PRINCIPALE — celle du
    parcours, ou la première du relevé —, et c'est elle que :meth:`ligne` rend.
    Ce que le droit compte par régime se lit ligne par ligne ; ce qu'il compte
    TOUS RÉGIMES — la durée d'assurance, la durée cotisée — ne dépasse jamais
    quatre trimestres par année civile, et se lit par :meth:`trimestres_cumules`.
    """

    annee_naissance: int
    sexe: str  # "H" ou "F"
    lignes: list[AnneeCarriere] = field(default_factory=list)
    #: Mois de naissance, 1 à 12. Le droit coupe deux générations en cours
    #: d'année — au 1er juillet 1951 et au 1er septembre 1961 — et l'âge à la
    #: liquidation ne se lit qu'à partir de lui. Janvier par défaut : c'est la
    #: convention qui fait commencer l'année de carrière avec l'année civile.
    #: L'âge entier ne tombe au 1er janvier que pour qui est né le 1er : sans
    #: jour dit, présumé le 15, on part au 1er février (R. 351-37).
    mois_naissance: int = 1
    #: Âge de liquidation effectif (réel pour un retraité, souhaité pour un actif).
    age_liquidation: float | None = None
    #: Jour de naissance déclaré, 1 à 31 ; ``None`` quand la saisie ne le dit
    #: pas, et la chronologie le présume (``jour_de_naissance``, § 5.6). Il
    #: décide du mois d'où les âges se comptent (:attr:`origine_des_ages`),
    #: jamais de la génération. Le jour qui compte est celui de la chronologie :
    #: :attr:`jour_de_naissance`.
    jour_naissance: int | None = None
    #: Nombre d'enfants — sans effet dans les scénarios notionnels, utilisé par
    #: le seul scénario « système actuel » (majorations, MDA).
    nombre_enfants: int = 0
    #: Les naissances déclarées des premiers enfants, dans l'ordre (AAAA,
    #: AAAA-MM ou AAAA-MM-JJ) : celles des autres sont présumées. Elles
    #: n'entrent que dans la chronologie qu'une carrière construite ligne à
    #: ligne reçoit ; une carrière tirée d'une chronologie les y lit.
    naissances_enfants: tuple[str, ...] = ()
    identifiant: str = "assuré"
    #: Mois d'entrée dans chaque statut, tel que le parcours le date. Les
    #: lignes ne connaissent que l'année, et l'année d'un changement de métier
    #: revient au métier qui en occupe le plus de mois : l'agent recruté à la
    #: RATP en octobre 2022 n'y a sa première LIGNE qu'en 2023, quand le régime
    #: est fermé aux recrutés depuis septembre 2023. C'est la date qui décide
    #: de la clause du grand-père, pas la première ligne.
    dates_entree: dict[str, DateMois] = field(default_factory=dict)
    #: La chronologie dont la carrière est la vue, complétée par les
    #: présomptions (:mod:`chronologie`). Une carrière construite ligne à ligne
    #: en reçoit une, tirée de ses champs : sa naissance, ses enfants et son
    #: départ. Une copie de travail — rétablie, prolongée — garde celle dont
    #: elle vient : ce que le moteur en fait n'est pas un fait de la personne.
    chronologie: dict | None = field(default=None, compare=False, repr=False)
    #: La personne de la chronologie dont la carrière est la vue.
    personne: str = field(default=chrono.ASSURE, compare=False, repr=False)
    #: Les années de l'activité exercée APRÈS le départ, le cumul
    #: emploi-retraite (:attr:`emploi_retraite`) : hors des lignes, que le
    #: départ arrête et que la première liquidation lit toutes. Ce que le
    #: droit en fait — la pension servie pendant qu'elle dure, les droits
    #: qu'elle ouvre ou non —, c'est ``moteur/js/droit/cumul.js``
    #: qui le dit.
    lignes_apres_depart: tuple = ()
    #: La carrière arrêtée au décès de la personne, pour la pension qu'elle
    #: « eût obtenue » et que sa réversion lit quand elle meurt avant son
    #: départ (:meth:`arretee_au_deces`) : aucun régime ne lui oppose de décote
    #: ni de coefficient d'anticipation — le régime général la calcule au taux
    #: de l'inaptitude, quel que soit l'âge au décès (R. 353-6), le code des
    #: pensions et les régimes spéciaux sans « coefficient de minoration »
    #: (L. 14, I), les complémentaires sur les points acquis.
    au_deces: bool = False

    def __post_init__(self) -> None:
        if self.sexe not in ("H", "F"):
            raise ValueError(f"sexe attendu 'H' ou 'F', reçu {self.sexe!r}")
        if not 1 <= self.mois_naissance <= 12:
            raise ValueError(
                f"mois de naissance attendu entre 1 et 12, reçu {self.mois_naissance}"
            )
        if self.jour_naissance is not None and not 1 <= self.jour_naissance <= 31:
            raise ValueError(
                f"jour de naissance attendu entre 1 et 31, reçu {self.jour_naissance}"
            )
        # Tri STABLE : l'activité principale, donnée la première, le reste.
        self.lignes.sort(key=lambda ligne: ligne.annee)
        vues: set[tuple[int, str]] = set()
        for ligne in self.lignes:
            cle = (ligne.annee, ligne.affiliation)
            if cle in vues:
                raise ValueError(
                    f"{self.identifiant} : deux lignes de {ligne.annee} sous le "
                    f"même statut {ligne.affiliation!r} — deux emplois du même "
                    "statut font une seule ligne, dont le revenu est la somme"
                )
            vues.add(cle)

    # -- dates ---------------------------------------------------------------

    @property
    def premiere_annee(self) -> int:
        return min(ligne.annee for ligne in self.lignes)

    @property
    def derniere_annee(self) -> int:
        return max(ligne.annee for ligne in self.lignes)

    # Mémorisées : la construction des témoins appelait `date_liquidation` un
    # million trois cent mille fois pour recalculer la même date. Les champs
    # dont elles dépendent ne sont jamais réaffectés après le constructeur —
    # la classe s'appuie déjà sur ce contrat pour ses autres `cached_property`.
    @cached_property
    def date_naissance(self) -> DateMois:
        """Le mois de naissance, tel que l'état civil le porte."""
        return DateMois(self.annee_naissance, self.mois_naissance)

    @cached_property
    def jour_de_naissance(self) -> int:
        """Le jour de naissance que la chronologie porte : déclaré, ou posé par
        la présomption ``jour_de_naissance``."""
        return chrono.jour_de(chrono.naissance(self.chronologie, self.personne)["debut"])

    @cached_property
    def origine_des_ages(self) -> DateMois:
        """Le mois d'où les âges se comptent (:func:`origine_des_ages`).

        **Trois lectures de la naissance, et il ne faut pas les confondre.**
        La GÉNÉRATION se lit au vrai mois (:attr:`generation`) : la loi coupe
        au 1er juillet 1951 et au 1er septembre 1961 des assurés nés avant ou
        après. L'ANNIVERSAIRE tombe dans le mois de naissance
        (:meth:`mois_de_l_anniversaire`) : c'est lui qu'une coupure au premier
        d'un mois départage, et c'est dans ce mois qu'un métier commence à
        l'âge dit. L'ÂGE RÉVOLU se compte d'ici (:meth:`date_de_l_age`,
        :meth:`age_au`) : une date d'effet, un décompte de trimestres après un
        âge, l'âge à une date.
        """
        return origine_des_ages(self.date_naissance, self.jour_de_naissance)

    def date_de_l_age(self, age: float) -> DateMois:
        """Le premier mois au premier jour duquel l'assuré a cet âge : la date
        d'effet au plus tôt d'une pension ouverte à cet âge, et le premier mois
        entier vécu au-delà."""
        return self.origine_des_ages.plus_mois(en_mois(age))

    def mois_de_l_anniversaire(self, age: float) -> DateMois:
        """Le mois où tombe l'anniversaire de cet âge.

        C'est lui, et non :meth:`date_de_l_age`, qui se compare à une coupure
        tombant un premier du mois — l'assuré né le 15 juin 1957 a soixante ans
        avant le 1er juillet 2017 —, qui donne l'année où l'âge est atteint, et
        où tombe un début d'activité dit par un âge.
        """
        return self.date_naissance.plus_mois(en_mois(age))

    def age_au(self, date: DateMois) -> float:
        """L'âge, en mois révolus, au premier jour de ce mois."""
        return (date.rang - self.origine_des_ages.rang) / MOIS_PAR_AN

    @property
    def generation(self) -> float:
        """Génération, mois compris — la clé des tables par génération.

        Deux textes ne coupent pas au 1er janvier : la loi du 9 novembre 2010
        vise les assurés nés à compter du 1er juillet 1951, celle du 14 avril
        2023 ceux nés à compter du 1er septembre 1961. Une génération s'écrit
        donc en années décimales, et le mois de naissance décide de quel côté
        de la coupure l'assuré tombe.

        **L'ARRONDI À TROIS DÉCIMALES N'EST PAS COSMÉTIQUE, et son absence
        coûtait un mois entier de chaque coupure de septembre.** Les tables
        écrivent le 1er septembre `1961.667` — trois décimales, comme le veut
        leur convention —, quand huit douzièmes valent 1961,666 666… Le premier
        étant plus grand que le second, la lecture en escalier rendait à
        l'assuré né en SEPTEMBRE 1961 la marche d'août : 168 trimestres au lieu
        de 169, et un âge d'ouverture de 62 ans au lieu de 62 ans et trois mois,
        pour le mois-même que la loi du 14 avril 2023 désigne. Le même trou
        s'ouvrait sur `1963.667`, `1966.667` et `1971.667`. Lire la génération à
        la précision où la table est écrite le referme.
        """
        return round(self.annee_naissance + (self.mois_naissance - 1) / 12, 3)

    @cached_property
    def date_liquidation(self) -> DateMois:
        """Mois où la pension prend effet.

        L'âge de liquidation est compté en mois depuis le mois d'où les âges
        se comptent (:attr:`origine_des_ages`) : né en mars 1962, parti à
        soixante-quatre ans et six mois, l'assuré liquide en septembre 2026.
        Le modèle arrondissait auparavant ``naissance + âge`` à l'année la plus
        proche, ce qui déplaçait la liquidation d'un semestre et, l'arrondi
        étant au pair, la déplaçait différemment selon la parité du millésime.
        """
        if self.age_liquidation is None:
            raise ValueError(
                f"{self.identifiant} : âge de liquidation non renseigné"
            )
        return self.date_de_l_age(self.age_liquidation)

    @property
    def annee_liquidation(self) -> int:
        """Année civile où la pension prend effet."""
        return self.date_liquidation.annee

    @property
    def mois_liquidation(self) -> int:
        return self.date_liquidation.mois

    @property
    def fraction_annee_liquidation(self) -> float:
        """Part de l'année de liquidation qui précède le point de départ."""
        return (self.mois_liquidation - 1) / 12

    @cached_property
    def annees_cotisees(self) -> tuple[int, ...]:
        # Une année de deux activités reste UNE année cotisée.
        return tuple(dict.fromkeys(
            ligne.annee for ligne in self.lignes if ligne.cotise
        ))

    @cached_property
    def _lignes_par_annee(self) -> dict[int, tuple[AnneeCarriere, ...]]:
        par_annee: dict[int, list[AnneeCarriere]] = {}
        for ligne in self.lignes:
            par_annee.setdefault(ligne.annee, []).append(ligne)
        return {annee: tuple(lignes) for annee, lignes in par_annee.items()}

    def lignes_de(self, annee: int) -> tuple[AnneeCarriere, ...]:
        """Toutes les lignes d'une année, l'activité principale en tête."""
        return self._lignes_par_annee.get(annee, ())

    def ligne(self, annee: int) -> AnneeCarriere | None:
        """La ligne de l'activité PRINCIPALE de l'année, ``None`` s'il n'y en a
        pas. Les activités cumulées se lisent par :meth:`lignes_de`."""
        lignes = self._lignes_par_annee.get(annee)
        return lignes[0] if lignes else None

    def affiliations_utilisees(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(ligne.affiliation for ligne in self.lignes))


#: Le profil que le modèle résout lui-même sur l'affiliation. C'est le défaut,
#: et le seul que le site propose : les autres noms restent pour la grille de
#: cas types et pour qui veut mesurer une variante.
PROFIL_AUTOMATIQUE = "auto"

#: Le profil du salarié payé au SMIC : son revenu est le salaire minimum de
#: chaque année, à temps complet
#: (:meth:`~retraite_notionnelle.donnees.macro.DonneesMacro.smic_annuel`), et
#: son niveau en est un MULTIPLE, non un multiple du salaire moyen. Le cas
#: type au SMIC s'écrivait 0,55 fois le salaire moyen à toutes les années,
#: quand le minimum en a valu 0,40 en 1970 et 0,52 en 2024 (action 147,
#: étape 16). Le site ne le propose pas : on y saisit son salaire.
PROFIL_SMIC = "smic"


@dataclass(frozen=True)
class Metier:
    """Un métier de la carrière : un statut, un niveau de revenu, une date.

    On faisait autrefois le même métier toute sa vie, et le modèle n'a longtemps
    su décrire que celui-là. Aujourd'hui la carrière se compose : un salarié
    devient artisan, un contractuel passe fonctionnaire, un indépendant revient
    au salariat. Chaque changement fait basculer l'assuré d'un régime à un autre,
    donc d'un taux de cotisation et d'un barème à un autre — c'est exactement ce
    que les comptes notionnels mesurent.

    Le métier court de ``age_debut`` jusqu'au début du suivant ; le dernier
    jusqu'à la liquidation.

    **Une activité CUMULÉE ne remplace pas, elle s'ajoute.** Le salarié qui
    ouvre un cabinet le soir, le fonctionnaire qui a une activité accessoire,
    le médecin hospitalier qui consulte en libéral : deux statuts à la fois,
    deux régimes qui encaissent chacun sur leur revenu. ``cumul`` le dit, et
    c'est à l'assuré de le dire — le modèle ne le devine jamais, et un métier
    qui ne le déclare pas succède au précédent comme il l'a toujours fait. Une
    activité cumulée court de ``age_debut`` à ``age_fin``, ou jusqu'à la
    liquidation si ``age_fin`` est absent ; elle ne touche pas à la suite des
    métiers principaux, qui continuent de couvrir la carrière bout à bout.
    """

    #: Statut d'affiliation (clé de ``legislation/affiliations.yaml``).
    affiliation: str
    #: Âge auquel ce métier commence, en années décimales.
    age_debut: float
    #: Niveau de revenu, en multiples du salaire moyen par tête de l'année.
    niveau_salaire: float = 1.0
    #: Vrai si ce métier s'AJOUTE à l'activité principale au lieu de lui
    #: succéder. Faux par défaut : rien n'est supposé.
    cumul: bool = False
    #: Âge auquel une activité cumulée s'arrête ; ``None`` la mène jusqu'à la
    #: liquidation. Sans objet pour un métier principal, que le suivant clôt.
    age_fin: float | None = None
    #: L'activité du micro-entrepreneur dont le niveau est le revenu abattu
    #: (``saisie.ACTIVITES_MICRO``), qui valide ses trimestres sur le revenu
    #: que sa cotisation achète ; vide sinon.
    micro: str = ""
    #: Vrai si ce micro-entrepreneur ne relève pas de la maladie du RSI, ou en
    #: relève mais touche le RSA socle : en 2014 et en 2015, il valide son
    #: premier trimestre plus tôt (circulaire RSI n° 2016/010, point 1 ;
    #: ``seuils_hors_maladie_rsi``). Faux par défaut : le modèle le présume au
    #: RSI, comme la caisse le cas le plus courant.
    maladie_hors_rsi: bool = False
    #: Vrai si ce métier est un contrat d'apprentissage, de ses dates de début
    #: et de fin : un emploi salarié, que la chronologie porte comme tel
    #: (attribut ``apprentissage``), et non une période assimilée. Faux par
    #: défaut (présomption ``pas_de_periode_assimilee``) ; aucune étape ne le
    #: lit encore (action 130, sixième domaine).
    apprentissage: bool = False
    #: Le barème de la Lodeom de l'employeur d'outre-mer
    #: (``saisie.BAREMES_LODEOM``), que la chronologie porte (attribut
    #: ``lodeom``) et que seule la fiche de paie lit ; vide sinon.
    lodeom: str = ""


@dataclass(frozen=True)
class LigneRelevee:
    """Une ligne de relevé de carrière, telle que l'assuré la recopie.

    C'est la saisie la plus exacte que le modèle accepte : elle ne suppose
    aucun profil de rémunération, aucune progression, aucun niveau de revenu
    relatif. L'assuré dit ce qu'il a gagné, année par année, et sous quel
    statut ; le modèle n'a plus rien à deviner.

    Le revenu est celui de l'année, EN EUROS COURANTS DE CETTE ANNÉE-LÀ —
    l'unité du relevé, et celle d':class:`AnneeCarriere`. Sur une année non
    cotisée, il ne s'agit plus d'un revenu perçu mais du salaire de référence
    d'avant l'interruption, sur lequel les régimes complémentaires continuent
    d'acquérir des points : la ligne elle-même ne cotise rien.
    """

    annee: int
    affiliation: str
    revenu: float
    #: Trimestres validés cette année-là, tels que le relevé les porte : ceux
    #: de la fonction publique, qui compte ses services au jour, avec leur
    #: fraction (« 3.33 » pour dix mois). ``None`` laisse le modèle les
    #: recalculer du revenu, comme il le fait d'une carrière paramétrique.
    trimestres: int | float | None = None
    #: Nature de la période, au sens de ``PERIODES_NON_COTISEES``.
    type_periode: str = "emploi"
    #: La quotité de l'année travaillée à temps partiel, entre zéro et un : le
    #: revenu que porte la ligne en est déjà réduit (fiche
    #: ``temps_partiel_fonction_publique``).
    quotite: float = 1.0
    #: Le motif qui dispense l'indépendant de l'assiette minimale cette année :
    #: ``rsa``, ``prime_activite``, ``activite_saisonniere``,
    #: ``activite_non_principale``, ``pensionne``
    #: (``legislation/dispenses_assiette_minimale.yaml``). Vide : aucun.
    dispense_assiette_minimale: str = ""
    #: Le barème de la Lodeom de l'employeur, en Guadeloupe, en Guyane, en
    #: Martinique ou à La Réunion : ``competitivite``,
    #: ``competitivite_renforcee``, ``innovation_et_croissance``
    #: (``legislation/prelevements_remuneration.yaml``). Vide : la réduction
    #: générale. Seule la fiche de paie le lit.
    lodeom: str = ""
    #: Le département d'outre-mer où l'assuré a travaillé cette année :
    #: ``guadeloupe``, ``guyane``, ``martinique``, ``reunion``. Vide : la
    #: métropole. Il donne leur seuil aux trimestres que la ligne ne déclare
    #: pas (R. 753-21, R. 351-9).
    outre_mer: str = ""
