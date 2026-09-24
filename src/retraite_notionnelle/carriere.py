"""Description d'une carrière individuelle.

Objectif : que n'importe qui puisse décrire sa situation, qu'il dispose de son
relevé de carrière année par année ou seulement de grandes lignes. Trois
niveaux d'entrée sont proposés, du plus précis au plus sommaire :

1. :meth:`Carriere.depuis_releve` — une ligne par année, telle qu'on la lit
   sur un relevé de carrière Info-Retraite : c'est le chemin le plus exact, le
   seul qui ne suppose ni profil ni progression (:meth:`Carriere.depuis_lignes`
   en est la forme brute, où l'appelant a déjà construit les années) ;
2. :meth:`Carriere.depuis_parcours` — la suite des métiers exercés, chacun avec
   son statut et son niveau de revenu ;
3. :meth:`Carriere.depuis_profil` — le cas d'un seul métier, exercé de bout en
   bout : c'est :meth:`depuis_parcours` avec un métier unique ;
4. :func:`carriere_type` — cas types prédéfinis (cf. :mod:`castypes`).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from functools import cached_property
from pathlib import Path

from .donnees.chargement import (
    assiette_minimale,
    charger_assiettes_minimales,
    charger_periodes_non_travaillees,
    charger_table_csv,
    charger_yaml,
)
from .donnees.macro import DonneesMacro

#: Le profil que le modèle résout lui-même sur l'affiliation. C'est le défaut,
#: et le seul que le site propose : les autres noms restent pour la grille de
#: cas types et pour qui veut mesurer une variante.
PROFIL_AUTOMATIQUE = "auto"
from .calendrier import (
    MOIS_PAR_AN,
    DateMois,
    en_mois,
    fraction_annee,
    mois_travailles,
    trimestres_civils,
)

#: Périodes non cotisées reconnues par le système actuel. Elles ouvrent des
#: droits gratuits aujourd'hui ; elles n'en ouvrent aucun dans les scénarios
#: notionnels, sauf si des cotisations ont réellement été versées.
PERIODES_NON_COTISEES = {
    "chomage_indemnise",
    "chomage_non_indemnise",
    "maladie",
    "invalidite",
    "maternite",
    "education_enfant",
    "service_militaire",
    "inactivite",
    "etudes",
}


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
    #: Quotité travaillée (1.0 = temps plein).
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
    #: Enveloppe de l'article D. 351-1-2 sous laquelle cette année est RÉPUTÉE
    #: COTISÉE pour la carrière longue, et plafond de cette enveloppe sur toute
    #: la carrière. Enveloppe vide : jamais réputée cotisée. Plafond nul :
    #: réputée cotisée sans limite, ce qui n'est vrai que de la maternité.
    reputes_cotises_enveloppe: str = ""
    reputes_cotises_plafond: int = 0
    #: Salaire porté au compte du régime général quand l'année est RÉTABLIE :
    #: celle d'un fonctionnaire parti sans droit à pension, que L. 65 du code
    #: des pensions rétablit au régime général et à l'Ircantec. C'est le
    #: dernier traitement soumis à retenue, sur la fraction de l'année
    #: (D. 173-16) ; le plafond de l'année s'applique ensuite. Zéro pour toute
    #: autre année : seul le scénario 1 le renseigne, sur sa propre copie de
    #: la carrière (voir `ScenarioActuel._retablie`).
    revenu_retabli: float = 0.0

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
    #: Trimestres validés cette année-là, tels que le relevé les porte.
    #: ``None`` laisse le modèle les recalculer du revenu, comme il le fait
    #: d'une carrière paramétrique.
    trimestres: int | None = None
    #: Nature de la période, au sens de ``PERIODES_NON_COTISEES``.
    type_periode: str = "emploi"


#: Article R. 351-12, 4°, d, du code de la sécurité sociale : le chômage NON
#: indemnisé ne valide que « des périodes postérieures au 31 décembre 1979 »,
#: et dans des limites. La première période, « qu'elle soit continue ou non »,
#: « dans la limite d'un an et demi, sans que plus de six trimestres
#: d'assurance puissent être comptés à ce titre » ; d'un an avant le décret
#: n° 2011-934 du 1er août 2011, dont l'article 2 réserve la nouvelle limite
#: « aux périodes de chômage involontaire non indemnisé postérieures au
#: 31 décembre 2010 ». C'est donc l'année de la PÉRIODE qui choisit la
#: limite, non la date de la pension.
CHOMAGE_NON_INDEMNISE_PREMIERE = {"valide_depuis": 1980, "trimestres": 6,
                                  "trimestres_avant": 4, "periodes_depuis": 2011}
#: « Chaque période ultérieure […] à condition qu'elle succède sans solution
#: de continuité à une période de chômage indemnisé, dans la limite d'un an ;
#: cette dernière limite est portée à cinq ans lorsque l'assuré justifie d'une
#: durée de cotisation d'au moins vingt ans, est âgé d'au moins cinquante-cinq
#: ans […] et ne relève pas à nouveau d'un régime obligatoire ».
CHOMAGE_NON_INDEMNISE_ULTERIEURE = {"trimestres": 4, "trimestres_senior": 20,
                                    "age_senior": 55, "cotises_senior": 80}


def limiter_chomage_non_indemnise(lignes: list[AnneeCarriere], annee_naissance: int,
                                  declarees: frozenset[int] = frozenset()
                                  ) -> list[AnneeCarriere]:
    """Les trimestres que le chômage non indemnisé valide VRAIMENT.

    Le modèle en validait quatre par an, sans limite : huit ans déclarés
    comme tels faisaient trente-deux trimestres, là où le droit en compte six.
    Rien avant 1980. La première période — la première série d'années, et ce
    qui reste de son enveloppe pour une série qui ne suit pas un chômage
    indemnisé — prend l'enveloppe de la première période, quatre trimestres
    pour une année d'avant 2011, six depuis ; une série qui suit une année de
    chômage indemnisé en prend quatre, vingt pour l'assuré de cinquante-cinq
    ans qui a vingt ans de cotisations et ne retravaille pas.

    ``declarees`` : les années dont un relevé porte les trimestres. La caisse
    les a déjà limités, et ce qu'elle a validé fait foi.
    """
    premiere = CHOMAGE_NON_INDEMNISE_PREMIERE
    ulterieure = CHOMAGE_NON_INDEMNISE_ULTERIEURE
    ordre = sorted(range(len(lignes)), key=lambda i: lignes[i].annee)
    resultat = list(lignes)
    cotises = 0
    precedente: AnneeCarriere | None = None
    #: La première période a-t-elle commencé, et combien en a-t-elle pris ?
    premiere_vue = False
    pris_premiere = 0
    reste_serie = 0
    serie_premiere = True
    for rang, indice in enumerate(ordre):
        ligne = lignes[indice]
        if (ligne.type_periode != "chomage_non_indemnise"
                or ligne.annee in declarees):
            if ligne.cotisations_versees:
                cotises += ligne.trimestres_valides
            precedente = ligne
            continue
        debut_serie = (precedente is None
                       or precedente.type_periode != "chomage_non_indemnise"
                       or precedente.annee != ligne.annee - 1)
        if debut_serie:
            suit_indemnise = (precedente is not None
                              and precedente.type_periode == "chomage_indemnise"
                              and precedente.annee == ligne.annee - 1)
            serie_premiere = not premiere_vue or not suit_indemnise
            if not serie_premiere:
                retravaille = any(lignes[j].cotisations_versees
                                  for j in ordre[rang + 1:])
                senior = (ligne.annee - annee_naissance >= ulterieure["age_senior"]
                          and cotises >= ulterieure["cotises_senior"]
                          and not retravaille)
                reste_serie = (ulterieure["trimestres_senior"] if senior
                               else ulterieure["trimestres"])
        if ligne.annee < premiere["valide_depuis"]:
            accordes = 0
        elif serie_premiere:
            premiere_vue = True
            plafond = (premiere["trimestres"]
                       if ligne.annee >= premiere["periodes_depuis"]
                       else premiere["trimestres_avant"])
            accordes = min(ligne.trimestres_valides, max(0, plafond - pris_premiere))
            pris_premiere += accordes
        else:
            accordes = min(ligne.trimestres_valides, reste_serie)
            reste_serie -= accordes
        if accordes != ligne.trimestres_valides:
            resultat[indice] = replace(ligne, trimestres_valides=accordes)
        precedente = ligne
    return resultat


def _ligne_annuelle(
    annee: int,
    revenu: float,
    affiliation: str,
    type_periode: str,
    macro: DonneesMacro,
    motifs: dict,
    part: float,
    part_primes: float,
    trimestres_maximum: int,
    trimestres_declares: int | None = None,
) -> AnneeCarriere:
    """Une année de carrière, une fois connus son revenu et sa nature.

    Les deux constructeurs de :class:`Carriere` y passent : celui qui déduit
    le revenu d'un profil (:meth:`Carriere.depuis_parcours`) et celui qui le
    lit sur un relevé (:meth:`Carriere.depuis_releve`). Ce que le droit fait
    d'une période non cotisée — combien de trimestres elle assimile, si elle
    ouvre des points complémentaires, si la CNAF cotise l'AVPF — ne s'écrit
    donc qu'une fois, et les deux chemins ne peuvent pas en diverger.

    ``trimestres_declares`` est le seul point où ils se séparent : un relevé
    dit combien de trimestres l'année a validés, et ce chiffre-là fait foi ;
    une carrière paramétrique les déduit du montant cotisé.
    """
    cotise = type_periode == "emploi"
    regle = None if cotise else motifs.get(type_periode, motifs.get("sans_activite"))
    # L'ASSIETTE MINIMALE DES INDÉPENDANTS : un artisan qui déclare 3 000 €
    # cotise en 2026 sur 450 SMIC horaires, soit 5 409 €, et valide trois
    # trimestres au lieu d'un. Le revenu de la ligne reste celui qu'il a
    # déclaré : sa complémentaire, le RCI, n'a pas de minimum.
    minimale = 0.0
    if cotise and revenu > 0:
        regle_minimale = assiette_minimale(
            charger_assiettes_minimales(macro.racine), affiliation, annee)
        if regle_minimale is not None:
            minimale = regle_minimale.montant(
                macro.plafond_securite_sociale(annee),
                macro.smic_horaire(annee), part)
    if trimestres_declares is None:
        trimestres = (macro.trimestres_valides(max(revenu, minimale), annee)
                      if cotise
                      else (regle.trimestres_assimiles if regle else 4))
    else:
        trimestres = trimestres_declares
    return AnneeCarriere(
        annee=annee,
        revenu=revenu if cotise else 0.0,
        affiliation=affiliation,
        type_periode=type_periode,
        # Un trimestre s'acquiert par un montant cotisé — 150 fois le SMIC
        # horaire depuis 2014, 200 avant. Une année à temps très partiel en
        # valide donc moins de quatre. Les périodes assimilées, elles, en
        # valident quatre sans condition de montant : c'est tout leur objet.
        # Le montant commande le nombre de trimestres, les mois en commandent
        # le plafond : on ne valide pas quatre trimestres en sept mois, si gros
        # que soit le salaire.
        trimestres_valides=min(trimestres_maximum, trimestres),
        assiette_minimale_base=minimale,
        cotisations_versees=cotise,
        # Pendant une période indemnisée, les régimes complémentaires
        # attribuent des points sur le salaire d'avant. L'Unédic les paie pour
        # le chômage ; l'Agirc-Arrco les donne pour la maladie, sans
        # contrepartie de cotisations. Les deux familles le disent.
        revenu_reference=(
            0.0 if cotise or regle is None
            or not regle.ouvre_droits_complementaires else revenu
        ),
        familles_cotisantes=(
            () if cotise or regle is None
            or not regle.ouvre_droits_complementaires
            else ("complementaire_prive",)
        ),
        familles_financees=(
            ("complementaire_prive",)
            if not cotise and regle is not None
            and regle.ouvre_droits_complementaires
            and regle.cotisations_complementaires_versees
            else ()
        ),
        fraction_annee=part,
        part_primes=part_primes,
        # Assurance vieillesse des parents au foyer : la CNAF cotise au régime
        # général sur une assiette forfaitaire égale au SMIC — 1 820 heures,
        # soit le SMIC mensuel multiplié par douze.
        revenu_avpf=(
            0.0 if cotise or regle is None or not regle.avpf
            else 1820.0 * macro.smic_horaire(annee) * part
        ),
        # Services et durée d'assurance ne sont pas la même case : la première
        # proratise la pension de la fonction publique, la seconde celle du
        # régime général. Une année de chômage indemnisé en valide quatre
        # trimestres à la CNAV et aucun service à l'État.
        services_fonction_publique=(
            cotise or regle is None or regle.services_fonction_publique
        ),
        services_plafond_trimestres_par_enfant=(
            0 if cotise or regle is None
            else regle.services_plafond_trimestres_par_enfant
        ),
        # La carrière longue compte la durée COTISÉE, que D. 351-1-2 complète
        # d'une liste fermée de périodes qu'il répute telles, chacune sous sa
        # limite. Une année cotisée n'a pas à être réputée quoi que ce soit.
        reputes_cotises_enveloppe=(
            "" if cotise or regle is None else regle.reputes_cotises_enveloppe
        ),
        reputes_cotises_plafond=(
            0 if cotise or regle is None else regle.reputes_cotises_plafond
        ),
    )


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
    #: convention qui laisse l'âge entier tomber sur le 1er janvier, et donc
    #: l'année civile coïncider avec l'année de carrière.
    mois_naissance: int = 1
    #: Âge de liquidation effectif (réel pour un retraité, souhaité pour un actif).
    age_liquidation: float | None = None
    #: Nombre d'enfants — sans effet dans les scénarios notionnels, utilisé par
    #: le seul scénario « système actuel » (majorations, MDA).
    nombre_enfants: int = 0
    identifiant: str = "assuré"
    #: Mois d'entrée dans chaque statut, tel que le parcours le date. Les
    #: lignes ne connaissent que l'année, et l'année d'un changement de métier
    #: revient au métier qui en occupe le plus de mois : l'agent recruté à la
    #: RATP en octobre 2022 n'y a sa première LIGNE qu'en 2023, quand le régime
    #: est fermé aux recrutés depuis septembre 2023. C'est la date qui décide
    #: de la clause du grand-père, pas la première ligne.
    dates_entree: dict[str, DateMois] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.sexe not in ("H", "F"):
            raise ValueError(f"sexe attendu 'H' ou 'F', reçu {self.sexe!r}")
        if not 1 <= self.mois_naissance <= 12:
            raise ValueError(
                f"mois de naissance attendu entre 1 et 12, reçu {self.mois_naissance}"
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
        return DateMois(self.annee_naissance, self.mois_naissance)

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

        L'âge de liquidation est compté en mois depuis la date de naissance :
        né en mars 1962, parti à soixante-quatre ans et six mois, l'assuré
        liquide en septembre 2026. Le modèle arrondissait auparavant
        ``naissance + âge`` à l'année la plus proche, ce qui déplaçait la
        liquidation d'un semestre et, l'arrondi étant au pair, la déplaçait
        différemment selon la parité du millésime.
        """
        if self.age_liquidation is None:
            raise ValueError(
                f"{self.identifiant} : âge de liquidation non renseigné"
            )
        return self.date_naissance.plus_mois(en_mois(self.age_liquidation))

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

    # -- agrégats ------------------------------------------------------------

    @cached_property
    def _entrees(self) -> dict[str, int]:
        """Première année de chaque statut dans la carrière.

        C'est elle qui décide de la CLAUSE DU GRAND-PÈRE : un régime fermé aux
        nouveaux entrants reste celui de qui était déjà là. Les lignes étant
        chronologiques, la première rencontre suffit.
        """
        entrees: dict[str, int] = {}
        for ligne in self.lignes:
            entrees.setdefault(ligne.affiliation, ligne.annee)
        return entrees

    def entree(self, affiliation: str) -> int | None:
        """Année d'entrée dans ce statut, ou ``None`` s'il n'y figure pas."""
        return self._entrees.get(affiliation)

    def date_entree(self, affiliation: str) -> DateMois | None:
        """Mois d'entrée dans ce statut, ou ``None`` s'il n'y figure pas.

        Celui que le parcours a daté quand il en vient ; sinon janvier de la
        première ligne, ce qui vaut pour une carrière construite ligne à ligne.
        """
        if affiliation in self.dates_entree:
            return self.dates_entree[affiliation]
        annee = self._entrees.get(affiliation)
        return None if annee is None else DateMois(annee, 1)

    @cached_property
    def annees_cotisees(self) -> tuple[int, ...]:
        # Une année de deux activités reste UNE année cotisée.
        return tuple(dict.fromkeys(
            ligne.annee for ligne in self.lignes if ligne.cotise
        ))

    def _lignes_de_service(self, affiliations: Iterable[str],
                           jusqu_a: int | None = None
                           ) -> list[AnneeCarriere]:
        """Les années effectivement servies dans l'un de ces statuts.

        « Services effectifs » au sens du code des pensions : les années
        travaillées, non les années validées. Une interruption — chômage,
        maladie, éducation d'un enfant — ne sert pas, et ``cotise`` la range
        déjà du bon côté.
        """
        codes = set(affiliations)
        # Une année ne sert qu'une fois, quand deux statuts de la liste s'y
        # cumulent : on garde celui qui en couvre le plus.
        par_annee: dict[int, AnneeCarriere] = {}
        for ligne in self.lignes:
            if (ligne.affiliation in codes and ligne.cotise
                    and (jusqu_a is None or ligne.annee <= jusqu_a)):
                retenue = par_annee.get(ligne.annee)
                if retenue is None or ligne.fraction_annee > retenue.fraction_annee:
                    par_annee[ligne.annee] = ligne
        return [par_annee[annee] for annee in sorted(par_annee)]

    def duree_de_service(self, affiliations: Iterable[str],
                         jusqu_a: int | None = None) -> float:
        """Années de service accomplies dans ces statuts, bornes comprises.

        C'est la grandeur que le code des pensions oppose deux fois : dix-sept
        ans de services ACTIFS pour ouvrir l'âge anticipé de la catégorie
        active (L. 24, I, 1°), dix-sept ou vingt-sept ans de services EFFECTIFS
        pour ouvrir la pension militaire (L. 24, II). Les années tronquées —
        l'entrée dans la vie active, l'année de liquidation — comptent pour ce
        qu'elles couvrent, comme partout ailleurs dans le modèle.
        """
        return sum(ligne.fraction_annee
                   for ligne in self._lignes_de_service(affiliations, jusqu_a))

    def bornes_de_service(self, affiliations: Iterable[str],
                          jusqu_a: int | None = None) -> tuple[int, int] | None:
        """Première et dernière années servies dans ces statuts, ``None`` sans
        aucune.

        Le recrutement et la radiation, à l'année près : ce sont eux que les
        règles des enfants opposent — une majoration « aux femmes ayant
        accouché postérieurement à leur recrutement », une bonification pour
        les enfants nés avant la radiation.
        """
        lignes = self._lignes_de_service(affiliations, jusqu_a)
        if not lignes:
            return None
        return lignes[0].annee, lignes[-1].annee

    def date_de_service(self, affiliations: Iterable[str],
                        annees: float) -> DateMois | None:
        """Mois où la durée de service demandée est atteinte, ``None`` sinon.

        La durée commande un ÂGE — celui auquel le militaire peut liquider —
        et une ANNÉE — celle à laquelle se lit le relèvement de la durée
        requise. Les deux se lisent sur cette date.

        **Convention de placement dans l'année.** Une année pleine sert de
        janvier à décembre ; une année tronquée sert à partir de son mois
        d'entrée quand elle ouvre le statut — c'est le mois que le parcours a
        daté —, et à partir de janvier sinon, l'année de liquidation étant
        tronquée par la fin. Le modèle ne connaît la carrière qu'à l'année :
        cette convention est ce qui en tire un mois, et elle ne peut se
        tromper que sur l'année d'entrée.
        """
        if annees <= 0:
            return None
        lignes = self._lignes_de_service(affiliations)
        if not lignes:
            return None
        premiere = lignes[0].annee
        cumul = 0.0
        for ligne in lignes:
            mois_servis = round(ligne.fraction_annee * MOIS_PAR_AN)
            if mois_servis <= 0:
                continue
            if ligne.annee == premiere and mois_servis < MOIS_PAR_AN:
                entree = self.date_entree(ligne.affiliation)
                debut = entree.mois if entree is not None and entree.annee == ligne.annee \
                    else MOIS_PAR_AN - mois_servis + 1
            else:
                debut = 1
            if cumul + ligne.fraction_annee >= annees - 1e-9:
                manque = max(1, en_mois(annees - cumul))
                return DateMois(ligne.annee, 1).plus_mois(debut - 1 + manque - 1)
            cumul += ligne.fraction_annee
        return None

    def age_de_service(self, affiliations: Iterable[str],
                       annees: float) -> float | None:
        """Âge auquel la durée de service demandée est atteinte."""
        date = self.date_de_service(affiliations, annees)
        if date is None:
            return None
        return (date.rang - self.date_naissance.rang) / MOIS_PAR_AN

    @cached_property
    def trimestres_actuels(self) -> int:
        """Trimestres validés au sens du droit en vigueur, tous régimes.

        Bornés à l'année de liquidation INCLUSE : une ligne postérieure décrit
        une activité exercée APRÈS le départ en retraite, et le droit ne la fait
        pas entrer dans la durée d'assurance qui commande la décote. Compter ces
        années annulait la décote d'un assuré qui, précisément, part tôt.

        L'année de la liquidation, elle, en fait partie : les mois travaillés
        avant le point de départ valident les trimestres qu'ils ont cotisés,
        dans la limite des trimestres civils écoulés. Les exclure retirait
        jusqu'à quatre trimestres à qui part en fin d'année, et c'est la décote
        qu'ils commandent.
        """
        return self.trimestres_cumules(self.lignes)

    def trimestres_par_annee(self, lignes: Iterable[AnneeCarriere]
                             ) -> dict[int, int]:
        """Trimestres que ces lignes font entrer dans une durée, année par année.

        **Quatre au plus par année civile, quel que soit le nombre
        d'activités.** Deux activités exercées la même année valident chacune
        ses trimestres dans son régime, mais la durée d'assurance tous régimes
        n'en compte jamais plus que les trimestres civils écoulés. La limite
        de quatre trimestres par année civile est celle de l'article R. 351-5
        du code de la sécurité sociale ; le 2° de R. 173-4-4-1 l'apprécie sur
        la réunion des régimes alignés (LEGIARTI000053335493), et l'article 20
        du décret n° 2003-1306 l'écrit pour la durée d'assurance tous régimes
        que la CNRACL oppose (LEGIARTI000054590030). Une année d'une seule
        ligne n'est pas touchée : sa ligne ne dépasse déjà pas ce plafond.
        """
        sommes: dict[int, int] = {}
        for ligne in lignes:
            retenus = self.trimestres_retenus(ligne)
            if retenus > 0:
                sommes[ligne.annee] = sommes.get(ligne.annee, 0) + retenus
        plafonds = self._plafonds_trimestres
        return {annee: min(somme, plafonds[annee])
                for annee, somme in sommes.items()}

    def trimestres_cumules(self, lignes: Iterable[AnneeCarriere]) -> int:
        """Somme de :meth:`trimestres_par_annee` : une durée, tous régimes."""
        return sum(self.trimestres_par_annee(lignes).values())

    @cached_property
    def _plafonds_trimestres(self) -> dict[int, int]:
        """Trimestres civils qu'une année peut valider, toutes activités
        confondues : ceux de l'activité qui en couvre le plus."""
        plafonds: dict[int, int] = {}
        for ligne in self.lignes:
            part = self.part_retenue_ligne(ligne)
            plafonds[ligne.annee] = max(
                plafonds.get(ligne.annee, 0),
                trimestres_civils(round(part * 12)) if part > 0 else 0,
            )
        return plafonds

    def plafond_trimestres(self, annee: int) -> int:
        """Trimestres civils que cette année peut valider, toutes activités
        confondues. Quatre pour une année pleine."""
        return self._plafonds_trimestres.get(annee, 4)

    @cached_property
    def _lignes_par_annee(self) -> dict[int, tuple[AnneeCarriere, ...]]:
        par_annee: dict[int, list[AnneeCarriere]] = {}
        for ligne in self.lignes:
            par_annee.setdefault(ligne.annee, []).append(ligne)
        return {annee: tuple(lignes) for annee, lignes in par_annee.items()}

    def lignes_de(self, annee: int) -> tuple[AnneeCarriere, ...]:
        """Toutes les lignes d'une année, l'activité principale en tête."""
        return self._lignes_par_annee.get(annee, ())

    def part_retenue(self, annee: int) -> float:
        """Part de l'année civile qui compte, une fois le départ pris en compte.

        Une ligne de carrière dit ce qui a été perçu dans l'année ; la date de
        liquidation dit jusqu'où l'année compte. Les deux se rencontrent
        l'année du départ, et c'est la plus courte qui l'emporte : un relevé de
        carrière déclare douze mois de 2022, mais qui liquide au 1er juillet
        n'en a travaillé que six avant son point de départ.

        Vaut zéro après l'année de liquidation — on ne cotise pas après être
        parti —, et zéro aussi l'année du départ quand celui-ci tombe au
        1er janvier.
        """
        ligne = self.ligne(annee)
        if ligne is None:
            return 0.0
        return self.part_retenue_ligne(ligne)

    def part_retenue_ligne(self, ligne: AnneeCarriere) -> float:
        """:meth:`part_retenue` d'une ligne précise : deux activités de la même
        année n'en couvrent pas forcément les mêmes mois."""
        annee = ligne.annee
        if self.age_liquidation is None:
            return ligne.fraction_annee
        if annee > self.annee_liquidation:
            return 0.0
        if annee < self.annee_liquidation:
            return ligne.fraction_annee
        return min(ligne.fraction_annee, self.fraction_annee_liquidation)

    def trimestres_retenus(self, ligne: AnneeCarriere) -> int:
        """Trimestres qu'une ligne fait entrer dans la durée d'assurance.

        Plafonnés par les trimestres CIVILS écoulés avant le point de départ :
        l'année de la liquidation en vaut quatre pour qui part en janvier de
        l'année suivante, un seul pour qui part en avril, aucun pour qui part
        en février.
        """
        part = self.part_retenue_ligne(ligne)
        if part <= 0:
            return 0
        return min(ligne.trimestres_valides, trimestres_civils(round(part * 12)))

    def ligne(self, annee: int) -> AnneeCarriere | None:
        """La ligne de l'activité PRINCIPALE de l'année, ``None`` s'il n'y en a
        pas. Les activités cumulées se lisent par :meth:`lignes_de`."""
        lignes = self._lignes_par_annee.get(annee)
        return lignes[0] if lignes else None

    def affiliations_utilisees(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(ligne.affiliation for ligne in self.lignes))

    # -- prolongation --------------------------------------------------------

    def avec_lignes(self, lignes: list[AnneeCarriere]) -> "Carriere":
        """La même carrière, portant d'autres lignes.

        Une carrière ne se modifie pas après son constructeur — ses mémoires en
        dépendent — : qui veut en changer les lignes en construit une autre.
        """
        return Carriere(
            annee_naissance=self.annee_naissance,
            sexe=self.sexe,
            lignes=list(lignes),
            mois_naissance=self.mois_naissance,
            age_liquidation=self.age_liquidation,
            nombre_enfants=self.nombre_enfants,
            identifiant=self.identifiant,
            dates_entree=dict(self.dates_entree),
        )

    def prolongee(self, age_liquidation: float, macro: DonneesMacro,
                  attente_travaillee: bool = True) -> "Carriere":
        """La même carrière, poursuivie jusqu'à un départ à ``age_liquidation``.

        C'est ce que fait l'âge légal de la proposition à qui serait parti plus
        tôt sous le droit en vigueur (``Parametres.age_legal_liberal``) : il
        travaille jusqu'à l'âge légal. Rien de ce qui précède ne bouge ; seules
        s'ajoutent les années — et les mois de l'année du départ initial — que
        le report fait travailler.

        LA CONVENTION, ET IL N'Y EN A QU'UNE : LA DERNIÈRE ANNÉE SE PROLONGE.
        Même statut, même nature de période, même salaire RELATIF — le revenu
        annualisé de la ligne, avancé chaque année au rythme du salaire moyen,
        comme le fait déjà le dénominateur du taux de remplacement. Elle vaut
        pour toutes les carrières, qu'elles viennent d'un profil, d'un parcours
        ou d'un relevé, et c'est pourquoi elle ne relit aucun profil : un relevé
        n'en a pas. Qui finissait sa carrière au chômage la finit donc au
        chômage, trois ans plus tard.

        TOUTE LA DERNIÈRE ANNÉE, et non sa dernière ligne : l'activité
        principale ET chaque activité cumulée qui court encore au départ, à son
        propre revenu. Jusqu'au 23 septembre 2026, seule la dernière ligne se
        prolongeait — celle d'une activité cumulée, puisqu'elle vient après la
        principale : le salarié qui exerçait aussi en libéral ne gardait que son
        revenu libéral pendant les années du report. Une activité cumulée qui
        s'arrête dans la dernière année, avant le départ, ne se prolonge pas :
        elle y couvre moins de mois que l'activité principale alors qu'elle
        courait déjà l'année d'avant.

        ``attente_travaillee=False`` fait l'autre hypothèse : l'attente se passe
        SANS ACTIVITÉ, aucune ligne ne s'ajoute, et le compte n'y est que
        revalorisé jusqu'au départ. C'est ce que la page Coût mêle à la
        première, dans la part ``1 − Parametres.part_reportes_en_emploi``.

        Rend la carrière elle-même, inchangée, quand le départ demandé ne
        tombe pas après celui qu'elle porte.
        """
        if (self.age_liquidation is None
                or en_mois(age_liquidation) <= en_mois(self.age_liquidation)):
            return self
        if not attente_travaillee:
            return Carriere(
                annee_naissance=self.annee_naissance,
                sexe=self.sexe,
                lignes=list(self.lignes),
                mois_naissance=self.mois_naissance,
                age_liquidation=age_liquidation,
                nombre_enfants=self.nombre_enfants,
                identifiant=self.identifiant,
                dates_entree=dict(self.dates_entree),
            )
        initiale = self.date_liquidation
        fin = self.date_naissance.plus_mois(en_mois(age_liquidation))
        motifs = charger_periodes_non_travaillees(macro.racine)
        derniere_annee = self.lignes[-1].annee
        finales = self.lignes_de(derniere_annee)
        principale = finales[0]
        veille = {ligne.affiliation for ligne in self.lignes_de(derniere_annee - 1)}

        def poursuivie(ligne: AnneeCarriere) -> bool:
            """L'activité de cette ligne court-elle encore au départ initial ?"""
            return (ligne is principale
                    or round(ligne.fraction_annee * MOIS_PAR_AN)
                    >= round(principale.fraction_annee * MOIS_PAR_AN)
                    or ligne.affiliation not in veille)

        reference = salaire_moyen_annuel(macro, derniere_annee)

        def ligne(source: AnneeCarriere, annee: int, mois: int) -> AnneeCarriere:
            """``source`` poursuivie ``mois`` mois de ``annee``."""
            # Le revenu annualisé de la ligne : ce qui a été perçu pour une
            # année d'emploi, le salaire de référence pour une interruption.
            percu = (source.revenu if source.type_periode == "emploi"
                     else source.revenu_reference)
            base = percu / source.fraction_annee if source.fraction_annee > 0 else 0.0
            facteur = (salaire_moyen_annuel(macro, annee) / reference
                       if reference > 0 else 1.0)
            return _ligne_annuelle(
                annee=annee,
                revenu=base * facteur * mois / MOIS_PAR_AN,
                affiliation=source.affiliation,
                type_periode=source.type_periode,
                macro=macro,
                motifs=motifs,
                part=mois / MOIS_PAR_AN,
                part_primes=source.part_primes,
                trimestres_maximum=trimestres_civils(mois),
            )

        # Le mois de liquidation n'est pas travaillé : l'année du départ
        # initial s'arrêtait au mois d'avant, et une liquidation de janvier ne
        # lui laissait aucune ligne.
        def fin_travaillee(annee: int, depart: DateMois) -> int:
            """Dernier mois travaillé de ``annee`` avant ``depart``, 0 à 12."""
            if annee < depart.annee:
                return MOIS_PAR_AN
            if annee == depart.annee:
                return depart.mois - 1
            return 0

        # Une carrière qui s'arrêtait AVANT son départ — un relevé dont les
        # dernières années sont vides — finissait sans activité : c'est cette
        # situation-là qui se prolonge, et le report n'ajoute aucune ligne.
        contigue = (derniere_annee == initiale.annee
                    or (derniere_annee == initiale.annee - 1 and initiale.mois == 1))
        lignes = list(self.lignes)
        if contigue:
            sources = [source for source in finales if poursuivie(source)]
            ajoutes = (fin_travaillee(derniere_annee, fin)
                       - fin_travaillee(derniere_annee, initiale))
            if ajoutes > 0:
                for source in sources:
                    mois = round(source.fraction_annee * MOIS_PAR_AN) + ajoutes
                    rang = next(i for i, l in enumerate(lignes) if l is source)
                    lignes[rang] = ligne(source, derniere_annee, min(mois, MOIS_PAR_AN))
            # L'activité principale en tête de chaque année, les cumulées
            # ensuite : l'ordre que le tri stable de la carrière conserve.
            for annee in range(derniere_annee + 1, fin.annee + 1):
                mois = fin_travaillee(annee, fin)
                if mois > 0:
                    lignes.extend(ligne(source, annee, mois) for source in sources)

        return Carriere(
            annee_naissance=self.annee_naissance,
            sexe=self.sexe,
            lignes=lignes,
            mois_naissance=self.mois_naissance,
            age_liquidation=age_liquidation,
            nombre_enfants=self.nombre_enfants,
            identifiant=self.identifiant,
            dates_entree=dict(self.dates_entree),
        )

    # -- constructeurs -------------------------------------------------------

    @classmethod
    def depuis_lignes(cls, annee_naissance: int, sexe: str,
                      lignes: list[AnneeCarriere], **kwargs) -> "Carriere":
        return cls(annee_naissance=annee_naissance, sexe=sexe, lignes=list(lignes), **kwargs)

    @classmethod
    def depuis_releve(
        cls,
        annee_naissance: int,
        sexe: str,
        releve: list[LigneRelevee],
        age_liquidation: float,
        macro: DonneesMacro,
        mois_naissance: int = 1,
        nombre_enfants: int = 0,
        part_primes: float = 0.0,
        identifiant: str = "assuré",
    ) -> "Carriere":
        """Construit une carrière à partir d'un relevé, ligne par ligne.

        C'est le chemin le plus exact, et le seul qui ne suppose rien : les
        deux autres reconstituent un revenu à partir d'un niveau relatif et
        d'un profil de progression, celui-ci le lit. Une ligne par année
        civile — l'unité à laquelle les régimes liquident —, avec son statut,
        son revenu de l'année et les trimestres qu'elle a validés.

        **Ce qui est lu, et ce qui ne l'est pas.** Le relevé donne l'année ; il
        ne donne pas le mois. Chaque ligne vaut donc une année civile PLEINE,
        sauf celle de la liquidation, dont la pension coupe le millésime à une
        date que le modèle, lui, connaît. L'année d'entrée dans la vie active
        reste comptée pour une année entière alors qu'elle est presque toujours
        tronquée : le relevé n'en porte que ce qui a été gagné, et le modèle ne
        peut pas l'annualiser sans savoir en quel mois elle a commencé.

        **Les années non cotisées** — chômage, maladie, éducation d'un enfant —
        se déclarent par ``type_periode``, ligne par ligne, et non par les
        plages d'une carrière paramétrique : le relevé porte des années, pas
        des intervalles. C'est à l'appelant de dire la nature de chacune ; le
        site la lit dans son champ « Interruptions », qui associe justement une
        année à un motif. Le revenu d'une telle ligne n'est plus un revenu
        perçu mais le salaire de référence d'avant l'interruption, celui sur
        lequel les régimes complémentaires continuent d'acquérir des points.
        """
        if not releve:
            raise ValueError("un relevé compte au moins une ligne")

        date_naissance = DateMois(annee_naissance, mois_naissance)
        # La pension prend effet ce mois-là : il n'est plus travaillé.
        fin = date_naissance.plus_mois(en_mois(age_liquidation))
        motifs = charger_periodes_non_travaillees(macro.racine)

        lignes: list[AnneeCarriere] = []
        for ligne in releve:
            mois = MOIS_PAR_AN if ligne.annee < fin.annee else fin.mois - 1
            if ligne.annee > fin.annee or mois <= 0:
                raise ValueError(
                    f"{identifiant} : l'année {ligne.annee} du relevé est "
                    f"postérieure au départ à la retraite ({fin})"
                )
            lignes.append(_ligne_annuelle(
                annee=ligne.annee,
                revenu=ligne.revenu,
                affiliation=ligne.affiliation,
                type_periode=ligne.type_periode,
                macro=macro,
                motifs=motifs,
                part=mois / MOIS_PAR_AN,
                part_primes=part_primes,
                trimestres_maximum=trimestres_civils(mois),
                trimestres_declares=ligne.trimestres,
            ))
        lignes = limiter_chomage_non_indemnise(
            lignes, annee_naissance,
            frozenset(l.annee for l in releve if l.trimestres is not None),
        )

        return cls(
            annee_naissance=annee_naissance,
            sexe=sexe,
            lignes=lignes,
            mois_naissance=mois_naissance,
            age_liquidation=age_liquidation,
            nombre_enfants=nombre_enfants,
            identifiant=identifiant,
        )

    @classmethod
    def depuis_profil(
        cls,
        annee_naissance: int,
        sexe: str,
        affiliation: str,
        age_debut: float,
        age_liquidation: float,
        macro: DonneesMacro,
        mois_naissance: int = 1,
        niveau_salaire: float = 1.0,
        profil_carriere: str = PROFIL_AUTOMATIQUE,
        interruptions: dict[int, str] | None = None,
        nombre_enfants: int = 0,
        part_primes: float = 0.0,
        identifiant: str = "assuré",
    ) -> "Carriere":
        """Carrière d'un seul métier, exercé du premier au dernier jour.

        C'est le cas particulier de :meth:`depuis_parcours` à un métier, et il
        se construit par elle : les deux chemins ne peuvent donc pas diverger.
        """
        return cls.depuis_parcours(
            annee_naissance=annee_naissance,
            sexe=sexe,
            metiers=[Metier(affiliation=affiliation, age_debut=age_debut,
                            niveau_salaire=niveau_salaire)],
            age_liquidation=age_liquidation,
            macro=macro,
            mois_naissance=mois_naissance,
            profil_carriere=profil_carriere,
            interruptions=interruptions,
            nombre_enfants=nombre_enfants,
            part_primes=part_primes,
            identifiant=identifiant,
        )

    @classmethod
    def depuis_parcours(
        cls,
        annee_naissance: int,
        sexe: str,
        metiers: list["Metier"],
        age_liquidation: float,
        macro: DonneesMacro,
        mois_naissance: int = 1,
        profil_carriere: str = PROFIL_AUTOMATIQUE,
        interruptions: dict[int, str] | None = None,
        nombre_enfants: int = 0,
        part_primes: float = 0.0,
        identifiant: str = "assuré",
    ) -> "Carriere":
        """Construit une carrière à partir de la suite des métiers exercés.

        Chaque :class:`Metier` porte un statut d'affiliation, l'âge auquel il
        commence et un niveau de revenu ; il court jusqu'au début du suivant, et
        le dernier jusqu'à la liquidation. Une carrière d'un seul métier est le
        cas particulier auquel se réduisait tout le modèle : on faisait autrefois
        le même métier toute sa vie, c'est devenu l'exception.

        ``niveau_salaire`` s'exprime en multiples du salaire moyen par tête
        BRUT de l'année considérée : 1,0 = salaire moyen, 0,6 ≈ niveau du SMIC,
        3,0 = cadre supérieur. Ce choix d'unité évite d'avoir à convertir des
        francs de 1975 en euros — le site, lui, accepte les deux et fait la
        conversion (voir :func:`salaire_moyen_annuel`). Brut au sens des
        comptes nationaux : avant cotisations salariales, avant CSG et avant
        impôt sur le revenu, cotisations patronales exclues.

        ``profil_carriere`` décrit la déformation du salaire relatif au cours de
        la vie active. Son défaut, ``auto``, la CHOISIT SUR L'AFFILIATION de
        chaque métier : on ne demande pas son profil de carrière à quelqu'un qui
        a déjà dit qu'il était fonctionnaire, et le profil d'un catégorie C
        (×1,11 de 26 à 55 ans) n'est pas celui d'un cadre du privé (×1,86). La
        table est ``PROFIL_PAR_AFFILIATION``, ses valeurs sont lues chez
        l'INSEE, et ``plat`` reste disponible pour la convention qui ne suppose
        rien — une carrière au SMIC, par exemple, dont le salaire ne progresse
        pas avec l'âge.

        Le profil se lit à un ÂGE et à une ANNÉE : changer de métier déplace la
        pente sans rien remettre à zéro, et le niveau de revenu propre à chaque
        métier s'y superpose comme avant.

        ``interruptions`` associe une année à un type de période non cotisée.

        Les deux bords sont des années INCOMPLÈTES et sont construites comme
        telles : celui qui entre en septembre ne travaille que quatre mois de
        son année d'entrée, celui qui part en août n'en travaille que sept de
        son année de départ. Le modèle comptait ces deux années pour zéro ou
        pour une, selon un arrondi — d'où une marche de plusieurs pour cent au
        milieu de l'année.
        """
        if not metiers:
            raise ValueError("une carrière compte au moins un métier")
        if metiers[0].cumul:
            raise ValueError(
                "une activité cumulée s'ajoute à une activité principale : la "
                "carrière ne peut pas commencer par elle"
            )
        cumuls = [metier for metier in metiers if metier.cumul]
        metiers = [metier for metier in metiers if not metier.cumul]

        date_naissance = DateMois(annee_naissance, mois_naissance)
        bornes = [date_naissance.plus_mois(en_mois(metier.age_debut))
                  for metier in metiers]
        debut = bornes[0]
        # La pension prend effet ce mois-là : il n'est plus travaillé, la borne
        # est donc EXCLUE.
        fin = date_naissance.plus_mois(en_mois(age_liquidation))
        if fin.rang <= debut.rang:
            raise ValueError("âge de liquidation antérieur à l'âge de début d'activité")
        # Chaque métier s'arrête où commence le suivant : les périodes se
        # touchent bout à bout et couvrent la carrière exactement une fois. Un
        # métier qui commencerait avant le précédent, ou après la liquidation,
        # laisserait un trou ou un recouvrement — donc des mois comptés deux
        # fois, ou pas du tout.
        for precedente, suivante in zip(bornes, bornes[1:]):
            if suivante.rang <= precedente.rang:
                raise ValueError(
                    "les métiers doivent se suivre : chacun commence après le "
                    "précédent"
                )
        if bornes[-1].rang >= fin.rang:
            raise ValueError("le dernier métier commence après la liquidation")
        periodes = list(zip(metiers, bornes, bornes[1:] + [fin]))

        annee_debut = debut.annee
        annees = [
            annee for annee in range(debut.annee, fin.annee + 1)
            if mois_travailles(annee, debut, fin) > 0
        ]
        annee_fin = annees[-1]

        interruptions = interruptions or {}
        motifs = charger_periodes_non_travaillees(macro.racine)
        # LE PROFIL SE LIT À UN ÂGE ET À UNE ANNÉE, et c'est tout ce dont il
        # dépend. Il valait auparavant trois nombres écrits à la main — 60 % du
        # niveau saisi au premier emploi, 130 % au dernier —, appliqués le long
        # de la carrière de l'assuré. Deux défauts en découlaient, tous deux
        # mesurés le 19 septembre 2026 :
        #
        # 1. le dénominateur étant la carrière de l'assuré, allonger celle-ci
        #    rabaissait le salaire de toutes les années ANTÉRIEURES — de 5,2 %
        #    entre 60 et 67 ans en profil ascendant, 8,4 % en fortement
        #    ascendant —, ce qui surestimait de quatre points le gain à
        #    travailler plus longtemps dans le système actuel, dont le salaire
        #    de référence ne retient que les meilleures années ;
        # 2. la pente elle-même était trop forte d'un tiers, et la même pour
        #    toutes les générations, quand l'INSEE observe ×1,30 de 26 à 55 ans
        #    pour un employé et ×1,86 pour un cadre, et une prime à l'âge qui a
        #    varié de 1,19 en 1962 à 1,47 en 2000.
        #
        # Lire le profil à (âge, année) règle les deux d'un coup : le passé ne
        # peut plus dépendre d'une décision future, et l'effet de génération
        # vient de la série longue au lieu d'être supposé nul.
        salaire_moyen_reference = indice_salaire_moyen(macro, annee_debut, annee_fin)

        lignes: list[AnneeCarriere] = []
        for annee in annees:
            part = fraction_annee(annee, debut, fin)
            trimestres_maximum = trimestres_civils(mois_travailles(annee, debut, fin))
            # Le profil se lit MÉTIER PAR MÉTIER, parce que l'affiliation peut
            # changer en cours de carrière et qu'elle est ce qui le choisit.
            # Rien n'est remis à zéro pour autant : un profil lu à l'âge ne
            # connaît pas la durée déjà parcourue, et passer du privé au public
            # déplace la pente sans effacer ce qui précède.
            age_annee = annee - annee_naissance
            # Ce que chaque métier a occupé de l'année. La somme vaut les mois
            # travaillés de l'année : les périodes la découpent sans reste.
            mois_par_metier = [mois_travailles(annee, ouverture, cloture)
                               for _, ouverture, cloture in periodes]
            revenu = sum(
                metier.niveau_salaire
                * profil_salaire(macro.racine, profil_carriere, age_annee,
                                 annee, metier.affiliation)
                * salaire_moyen_reference[annee] * (mois / MOIS_PAR_AN)
                for (metier, _, _), mois in zip(periodes, mois_par_metier)
                if mois > 0
            )
            # Le moteur ne connaît qu'une ligne, donc qu'un statut, par année
            # civile : les régimes liquident à l'année. L'année d'un changement
            # de métier est donc rattachée à celui qui en occupe le plus de
            # mois — et, à égalité, à celui qui l'ouvre. Le revenu, lui, reste
            # la somme de ce que les deux ont réellement payé.
            affiliation = periodes[
                max(range(len(periodes)), key=mois_par_metier.__getitem__)
            ][0].affiliation

            lignes.append(_ligne_annuelle(
                annee=annee,
                revenu=revenu,
                affiliation=affiliation,
                type_periode=interruptions.get(annee, "emploi"),
                macro=macro,
                motifs=motifs,
                part=part,
                part_primes=part_primes,
                trimestres_maximum=trimestres_maximum,
            ))
        lignes = limiter_chomage_non_indemnise(lignes, annee_naissance)

        # LES ACTIVITÉS CUMULÉES, chacune sur ses propres mois. Elles ne
        # déplacent rien de l'activité principale : elles ajoutent à chaque
        # année qu'elles touchent une ligne de plus, sous leur statut, avec le
        # revenu qu'elles ont payé et les trimestres que ce revenu valide. Une
        # interruption déclarée arrête l'activité principale, pas celle-ci.
        periodes_cumulees = []
        for metier in cumuls:
            ouverture = date_naissance.plus_mois(en_mois(metier.age_debut))
            cloture = (fin if metier.age_fin is None
                       else date_naissance.plus_mois(en_mois(metier.age_fin)))
            if ouverture.rang < debut.rang:
                raise ValueError(
                    "une activité cumulée commence après le début de la "
                    "carrière : elle s'ajoute à une activité déjà là"
                )
            if cloture.rang > fin.rang:
                raise ValueError(
                    "une activité cumulée s'arrête au plus tard à la liquidation"
                )
            if cloture.rang <= ouverture.rang:
                raise ValueError(
                    "une activité cumulée doit s'arrêter après avoir commencé"
                )
            periodes_cumulees.append((metier, ouverture, cloture))
            for annee in range(ouverture.annee, cloture.annee + 1):
                mois = mois_travailles(annee, ouverture, cloture)
                if mois <= 0:
                    continue
                revenu = (metier.niveau_salaire
                          * profil_salaire(macro.racine, profil_carriere,
                                           annee - annee_naissance, annee,
                                           metier.affiliation)
                          * salaire_moyen_reference[annee] * (mois / MOIS_PAR_AN))
                lignes.append(_ligne_annuelle(
                    annee=annee,
                    revenu=revenu,
                    affiliation=metier.affiliation,
                    type_periode="emploi",
                    macro=macro,
                    motifs=motifs,
                    part=fraction_annee(annee, ouverture, cloture),
                    part_primes=part_primes,
                    trimestres_maximum=trimestres_civils(mois),
                ))

        dates_entree: dict[str, DateMois] = {}
        for metier, ouverture, _ in sorted(
                periodes + periodes_cumulees, key=lambda p: p[1].rang):
            dates_entree.setdefault(metier.affiliation, ouverture)

        return cls(
            annee_naissance=annee_naissance,
            sexe=sexe,
            lignes=lignes,
            mois_naissance=mois_naissance,
            age_liquidation=age_liquidation,
            nombre_enfants=nombre_enfants,
            identifiant=identifiant,
            dates_entree=dates_entree,
        )


#: La catégorie socioprofessionnelle dont chaque profil emprunte sa FORME, dans
#: ``profil_salaire_categorie.csv``. ``plat`` n'en emprunte aucune : le revenu
#: saisi vaut pour toutes les années, et c'est la seule convention qui ne
#: suppose rien.
#:
#: Les trois noms restent, parce que le site les affiche et que les fiches de
#: cas types les portent. Ce qu'ils désignent, en revanche, n'est plus une
#: droite inventée mais un profil LU : ×1,30 de 26 à 55 ans pour un employé,
#: ×1,86 pour un cadre, là où les droites d'avant appliquaient ×1,69 et ×2,42 —
#: un tiers de trop, et le même à toutes les générations.
PROFILS_CATEGORIE = {
    "plat": None,
    "ascendant": "employe",
    "fortement_ascendant": "cadre",
    # Les profils lus, sous leur nom de source. Ils se choisissent d'eux-mêmes
    # par l'affiliation (voir ``PROFIL_PAR_AFFILIATION``) et restent nommables
    # pour une grille qui sait mieux — les cas types portent la catégorie du
    # fonctionnaire dans leur commentaire, le formulaire du site ne la demande
    # pas.
    "ouvrier": "ouvrier",
    "employe": "employe",
    "profession_intermediaire": "profession_intermediaire",
    "cadre": "cadre",
    "public_etat": "public_etat",
    "public_territoriale": "public_territoriale",
    "public_hospitaliere": "public_hospitaliere",
    "public_categorie_a": "public_categorie_a",
    "public_categorie_b": "public_categorie_b",
    "public_categorie_c": "public_categorie_c",
    "public_non_titulaire": "public_non_titulaire",
}

#: Les groupes lus dans le fichier du PUBLIC plutôt que dans celui du privé.
GROUPES_PUBLIC = frozenset(
    cle for cle in PROFILS_CATEGORIE if str(cle).startswith("public_")
)

#: LE PROFIL SE CHOISIT SUR L'AFFILIATION, et non sur un réglage saisi : on ne
#: demande pas son profil de carrière à quelqu'un qui a déjà dit qu'il était
#: fonctionnaire. La table ne porte que les écarts au défaut.
#:
#: Les affiliations publiques prennent le profil de leur VERSANT et non d'une
#: catégorie : aucune d'elles ne porte le A, le B ou le C, et le profil du
#: versant pondère déjà les catégories par leurs effectifs réels. Deviner la
#: catégorie de chacune serait réinventer ce que la lecture vient remplacer.
#:
#: Les militaires prennent celui de l'État, faute de source : aucun jeu de
#: l'INSEE ne porte la solde indiciaire par âge.
PROFIL_PAR_AFFILIATION = {
    "salarie_prive_cadre": "cadre",
    "salarie_prive_cadre_entreprise_recente": "cadre",
    "fonctionnaire_etat": "public_etat",
    "fonctionnaire_etat_actif": "public_etat",
    "fonctionnaire_etat_super_actif": "public_etat",
    "fonctionnaire_pacifique": "public_etat",
    "ouvrier_etat": "public_etat",
    "ouvrier_etat_actif": "public_etat",
    "militaire": "public_etat",
    "militaire_officier": "public_etat",
    "fonctionnaire_territorial_hospitalier": "public_territoriale",
    "fonctionnaire_territorial_hospitalier_actif": "public_territoriale",
    "fonctionnaire_territorial_hospitalier_super_actif": "public_territoriale",
    "contractuel_public": "public_non_titulaire",
    "maitre_enseignement_prive": "public_non_titulaire",
    # Les professions libérales réglementées progressent comme des cadres :
    # c'est le profil que la grille leur donnait déjà, et le seul des quatre
    # du privé qui ait la forme d'une carrière indépendante.
    "profession_liberale": "cadre",
    "liberal_non_reglemente": "cadre",
    "avocat": "cadre",
    "notaire": "cadre",
    "medecin_liberal": "cadre",
    "chirurgien_dentiste_ou_sage_femme": "cadre",
    "pharmacien": "cadre",
    "veterinaire": "cadre",
    "expert_comptable": "cadre",
    "auxiliaire_medical": "profession_intermediaire",
    "officier_ministeriel": "cadre",
}

#: Ce que prend toute affiliation que la table ne nomme pas : le profil des
#: employés du privé. C'est le groupe le plus nombreux, et le plus proche d'une
#: carrière ordinaire — les régimes spéciaux, les indépendants et les
#: non-salariés n'ont aucun profil publié par âge.
PROFIL_PAR_DEFAUT = "employe"

#: LA SECTION D'ACTIVITÉ dont chaque affiliation emprunte son facteur de pente,
#: dans ``profil_salaire_secteur.csv``. Elle ne sert QUE pour les régimes dont
#: aucune source française ne dit le profil salarial : les régimes spéciaux.
#:
#: Deux sections tombent sur le périmètre d'un régime plutôt qu'à côté : ``D``,
#: électricité et gaz, est le champ du statut des IEG ; ``H``, transports et
#: entreposage, est plus large que la SNCF et la RATP mais c'est là qu'elles
#: sont. ``K`` couvre la Banque de France.
#:
#: NE FIGURENT QUE LES SECTIONS STABLES d'une vague à l'autre — le critère est
#: dix pour cent d'écart entre 2018 et 2022. Les mines passent de 0,93 à 1,19 et
#: les spectacles de 0,83 à 1,08 : ce sont de petits secteurs, leur facteur
#: n'est que du bruit, et leurs régimes gardent donc le profil du privé sans
#: correction.
PROFIL_SECTEUR_PAR_AFFILIATION = {
    "agent_ieg": "D",
    "agent_sncf": "H",
    "agent_ratp": "H",
    "agent_chemins_fer_secondaires": "H",
    "agent_port_strasbourg": "H",
    "marin": "H",
    "personnel_navigant": "H",
    "agent_banque_de_france": "K",
}

#: La section de référence : elle vaut un, et chaque secteur s'y rapporte.
SECTION_ENSEMBLE = "B-S"

#: Les deux tranches dont le rapport mesure la pente d'un secteur.
TRANCHE_SECTEUR_JEUNE, TRANCHE_SECTEUR_AGEE = "Y_LT30", "Y_GE50"


def _facteur_secteur(racine: Path, affiliation: str) -> float:
    """De combien la pente d'un secteur s'écarte de celle de l'économie.

    C'est la seule chose que l'enquête européenne puisse dire des régimes
    spéciaux, et elle ne la dit qu'en AGRÉGÉ : un profil par secteur mélange
    l'effet d'âge et un effet de composition, et aucune source ne croise l'âge,
    le secteur et la profession — vérifié chez Eurostat comme chez l'INSEE.

    On n'en prend donc qu'un RAPPORT, secteur sur ensemble, que l'on applique à
    la forme intra-catégorie. **Cela suppose ce rapport identique à l'intérieur
    des catégories et en agrégé**, ce que rien ne démontre : c'est l'hypothèse
    la plus forte du profil salarial, elle est assumée, et ``docs/limites.md``
    la nomme. Sans elle, ces régimes n'auraient rien du tout.

    Les deux vagues sont moyennées : elles ne servent pas à dater le facteur —
    quatre ans ne déplacent pas une structure de carrière — mais à écarter le
    bruit des petits secteurs, ce que fait déjà
    ``PROFIL_SECTEUR_PAR_AFFILIATION``.
    """
    section = PROFIL_SECTEUR_PAR_AFFILIATION.get(affiliation)
    if section is None:
        return 1.0
    table, _ = charger_table_csv(
        racine / "reference" / "macro" / "profil_salaire_secteur.csv",
        ("secteur", "vague", "tranche"), "salaire_relatif",
    )
    vagues = sorted({cle[1] for cle in table})

    def pente(nom: str, vague: str) -> float | None:
        jeune = table.get((nom, vague, TRANCHE_SECTEUR_JEUNE))
        agee = table.get((nom, vague, TRANCHE_SECTEUR_AGEE))
        return agee / jeune if jeune and agee else None

    facteurs = []
    for vague in vagues:
        secteur, ensemble = pente(section, vague), pente(SECTION_ENSEMBLE, vague)
        if secteur and ensemble:
            facteurs.append(secteur / ensemble)
    return sum(facteurs) / len(facteurs) if facteurs else 1.0


def profil_de_l_affiliation(affiliation: str) -> str:
    """Le groupe salarial que le modèle prête à une affiliation."""
    return PROFIL_PAR_AFFILIATION.get(affiliation, PROFIL_PAR_DEFAUT)

#: Le milieu qu'on prête à chaque tranche des deux fichiers. Un profil de
#: carrière se lit à un ÂGE, pas à une tranche : il faut donc un point par
#: tranche, et c'est ce point qui décide de la pente. Les bornes ouvertes
#: prennent le milieu de leur population d'emploi et non celui de leur
#: intervalle, qui serait absurde — on n'entre pas dans la vie active à quinze
#: ans, on n'y reste pas jusqu'à cent. Ces deux tables sont le reflet de
#: ``TRANCHES_AGE_SERIES`` et ``TRANCHES_AGE_CATEGORIES`` de
#: ``scripts/verifier_donnees.py``, et un test les tient identiques.
TRANCHES_SERIE = {
    "Y_LT26": 23.0, "Y26T30": 28.0, "Y31T40": 35.5,
    "Y41T50": 45.5, "Y51T60": 55.5, "Y_GT60": 62.0,
}
TRANCHES_CATEGORIE = {
    "Y_LT30": 26.0, "Y30T39": 34.5, "Y40T49": 44.5,
    "Y50T59": 54.5, "Y_GE60": 62.0,
}

#: Année de référence de la forme intra-catégorie, celle que porte le jeu
#: détaillé de l'INSEE. La modulation dans le temps y vaut un.
ANNEE_FORME_CATEGORIE = 2024

#: Les deux tranches dont l'écart mesure la pente d'une carrière. Renseignées
#: depuis 1962, quand les deux bords ne le sont que depuis 1996 : ce sont elles
#: qui fixent la profondeur de la modulation.
TRANCHE_JEUNE, TRANCHE_AGEE = "Y26T30", "Y51T60"


def _table_profil(racine: Path, fichier: str,
                  cle: str) -> dict[str, dict[str, float]]:
    """Un des deux fichiers de profil, groupé par sa première clé."""
    table, _ = charger_table_csv(
        racine / "reference" / "macro" / fichier, (cle, "tranche"),
        "salaire_relatif",
    )
    groupes: dict[str, dict[str, float]] = {}
    for (groupe, tranche), valeur in table.items():
        groupes.setdefault(groupe, {})[tranche] = valeur
    return groupes


def _interpole_tranches(profil: dict[str, float], milieux: dict[str, float],
                        age: float) -> float:
    """Valeur du profil à un âge, interpolée entre les milieux de tranche.

    Au-delà du premier et du dernier milieu, la valeur du bord est reconduite :
    l'INSEE ne dit rien au-delà, et y prolonger la pente inventerait des
    salaires que personne n'a observés.
    """
    points = sorted((milieux[t], v) for t, v in profil.items() if t in milieux)
    if not points:
        return 1.0
    if age <= points[0][0]:
        return points[0][1]
    if age >= points[-1][0]:
        return points[-1][1]
    for (age_bas, bas), (age_haut, haut) in zip(points, points[1:]):
        if age_bas <= age <= age_haut:
            return bas + (haut - bas) * (age - age_bas) / (age_haut - age_bas)
    return points[-1][1]


def _modulation_annee(racine: Path, annee: int) -> float:
    """Pente de carrière de l'année, rapportée à celle de l'année de référence.

    C'est ici que se loge l'effet de génération, et il est observé : la prime à
    l'âge valait 1,19 entre les 51-60 ans et les 26-30 ans en 1962, 1,47 en
    2000, 1,35 en 2024. Celui qui est né en 1940 est entré dans la vie active
    au salaire moyen de son temps, celui qui est né en 1960 à 86 % du sien.

    Hors de la fenêtre observée — avant 1962, après 2024 — la valeur du bord
    est reconduite, convention du dépôt pour toute série bornée.
    """
    table = _table_profil(racine, "profil_salaire_age.csv", "annee")
    annees = sorted(int(a) for a in table)
    if not annees:
        return 1.0

    def ecart(millesime: int) -> float:
        profil = table.get(str(millesime), {})
        jeune, agee = profil.get(TRANCHE_JEUNE), profil.get(TRANCHE_AGEE)
        return agee - jeune if jeune is not None and agee is not None else 0.0

    reference = ecart(ANNEE_FORME_CATEGORIE)
    borne = min(max(annee, annees[0]), annees[-1])
    return ecart(borne) / reference if reference else 1.0


def profil_salaire(racine: Path, profil: str, age: float, annee: int,
                   affiliation: str | None = None) -> float:
    """Ce que le profil fait du niveau saisi, à cet âge et cette année-là.

    Deux sources, parce qu'aucune ne suffit seule. La FORME vient du profil
    intra-catégorie de 2024, seul jeu de l'INSEE qui croise l'âge et la
    catégorie — et seul profil qui décrive une CARRIÈRE, un profil agrégé
    mélangeant l'effet d'âge et un effet de composition. L'ÉVOLUTION vient de
    la série longue, qui dit comment la prime à l'âge s'est déplacée depuis
    1962.

    On module l'écart à la moyenne et non la valeur elle-même :
    ``1 + (forme − 1) × modulation`` laisse le profil centré quoi qu'il arrive,
    de sorte que le niveau de revenu saisi garde son sens.
    """
    if profil == PROFIL_AUTOMATIQUE:
        categorie = profil_de_l_affiliation(affiliation or "")
    elif profil in PROFILS_CATEGORIE:
        categorie = PROFILS_CATEGORIE[profil]
    else:
        raise ValueError(f"profil de carrière inconnu : {profil!r}")
    if categorie is None:
        return 1.0
    fichier = ("profil_salaire_statut_public.csv" if categorie in GROUPES_PUBLIC
               else "profil_salaire_categorie.csv")
    cle = "statut" if categorie in GROUPES_PUBLIC else "categorie"
    table = _table_profil(racine, fichier, cle)
    forme = _interpole_tranches(table.get(categorie, {}), TRANCHES_CATEGORIE, age)
    facteur = _facteur_secteur(racine, affiliation or "")
    return 1.0 + (forme - 1.0) * _modulation_annee(racine, annee) * facteur


def bornes_deformation(racine: Path, profil: str,
                       affiliation: str | None = None) -> tuple[float, float]:
    """Ce que le profil fait du niveau saisi, en début et en fin de carrière.

    Lues à l'année de référence de la forme : ce sont les deux nombres que le
    site affiche sous le menu des profils, et ils doivent donc être ceux d'une
    carrière observée et non d'un bord de table.
    """
    if profil != PROFIL_AUTOMATIQUE and PROFILS_CATEGORIE.get(profil) is None:
        return 1.0, 1.0
    return (profil_salaire(racine, profil, 25.0, ANNEE_FORME_CATEGORIE, affiliation),
            profil_salaire(racine, profil, 60.0, ANNEE_FORME_CATEGORIE, affiliation))


#: Point d'ancrage du salaire moyen par tête, en euros bruts annuels courants.
#: Les comptes nationaux ne publient que des taux de croissance ; il faut un
#: niveau pour les cumuler. Il est ici, en un seul endroit, parce que le site
#: l'affiche désormais — dire « 1 = salaire moyen » sans dire combien cela fait
#: d'euros laissait toute la saisie dans le flou.
ANCRAGE_SALAIRE_MOYEN = (2024, 40_000.0)


def salaire_moyen_annuel(macro: DonneesMacro, annee: int) -> float:
    """Salaire moyen par tête d'une année, en euros BRUTS courants de cette année."""
    return indice_salaire_moyen(macro, annee, annee)[annee]


def indice_salaire_moyen(macro: DonneesMacro, debut: int, fin: int) -> dict[int, float]:
    """Salaire moyen par tête reconstitué en euros courants de chaque année.

    Le montant est un salaire **BRUT** : la série de comptes nationaux dont il
    dérive est celle des salaires et traitements bruts (D11) rapportés à
    l'emploi salarié, c'est-à-dire avant cotisations salariales, avant CSG et
    avant impôt sur le revenu, cotisations patronales exclues. C'est la même
    assiette que celle sur laquelle les régimes appellent leurs cotisations :
    le niveau de revenu saisi, les cotisations versées et les pensions
    calculées sont donc tous bruts, et se comparent directement.

    La série de comptes nationaux ne donne que des TAUX DE CROISSANCE. On les
    cumule à partir d'un point d'ancrage : le salaire moyen par tête du secteur
    privé en 2024, arrondi à 40 000 € bruts annuels. Ce point d'ancrage est un
    paramètre documenté, pas une donnée certifiée — il déplace proportionnellement
    tous les revenus reconstitués, donc toutes les pensions, mais il est sans
    effet sur les RAPPORTS entre scénarios, qui sont l'objet du modèle.
    """
    ancrage_annee, ancrage_valeur = ANCRAGE_SALAIRE_MOYEN
    valeurs = {ancrage_annee: ancrage_valeur}

    borne_haute = max(fin, ancrage_annee)
    for annee in range(ancrage_annee + 1, borne_haute + 1):
        valeurs[annee] = valeurs[annee - 1] * (1 + macro.salaire_moyen(annee))

    borne_basse = min(debut, ancrage_annee)
    for annee in range(ancrage_annee - 1, borne_basse - 1, -1):
        valeurs[annee] = valeurs[annee + 1] / (1 + macro.salaire_moyen(annee + 1))

    return valeurs


def rang_borne(borne: int | str) -> int:
    """Une borne d'entrée du routage, en rang de mois.

    ``2020`` se lit janvier 2020 ; ``"2023-09"`` septembre 2023. Le YAML garde
    les deux écritures parce que la loi ferme un régime « aux agents recrutés à
    compter du 1er septembre 2023 », et non à compter d'une année.
    """
    if isinstance(borne, int):
        return DateMois(borne, 1).rang
    annee, mois = str(borne).split("-")
    return DateMois(int(annee), int(mois)).rang


def formater_borne(borne: DateMois) -> str:
    """« 2020 » pour un 1er janvier, « septembre 2023 » sinon."""
    return str(borne.annee) if borne.mois == 1 else str(borne)


#: Les familles de statuts, dans l'ordre où le menu du simulateur les range :
#: code du YAML -> libellé du groupe. Sept groupes de deux à seize statuts se
#: parcourent ; soixante-deux à la file ne se parcouraient pas. L'ordre va du
#: plus commun au plus rare, et « hors emploi » ferme la marche.
FAMILLES_STATUT: dict[str, str] = {
    "prive": "Salariés du privé",
    "public": "Fonction publique et militaires",
    "independant": "Indépendants et professions libérales",
    "agricole": "Agriculture",
    "special": "Régimes spéciaux",
    "outre_mer": "Outre-mer",
    "elus": "Élus et assemblées",
    "hors_emploi": "Hors emploi",
}


class Affiliations:
    """Correspondance statut -> régimes, année par année."""

    def __init__(self, racine: Path) -> None:
        contenu = charger_yaml(racine / "reference" / "legislation" / "affiliations.yaml")
        self._profils: dict[str, dict] = contenu.get("affiliations", {})
        if not self._profils:
            raise ValueError("aucun profil d'affiliation chargé")
        for code, profil in self._profils.items():
            if profil.get("famille") not in FAMILLES_STATUT:
                raise ValueError(
                    f"affiliations.yaml / {code} : famille manquante ou inconnue "
                    f"{profil.get('famille')!r} — attendue parmi "
                    f"{sorted(FAMILLES_STATUT)}"
                )
        #: Régimes du catalogue que le fichier déclare volontairement hors
        #: routage, avec leur raison. Le moteur ne s'en sert pas ; la cohérence
        #: entre catalogue et routage, si — cf. `tests/test_donnees.py`.
        self._hors_routage: dict[str, str] = contenu.get(
            "regimes_sans_affiliation", {}
        )

    def __contains__(self, code: str) -> bool:
        return code in self._profils

    @property
    def codes(self) -> tuple[str, ...]:
        return tuple(sorted(self._profils))

    def libelle(self, code: str) -> str:
        return self._profils[code].get("libelle", code)

    def famille(self, code: str) -> str:
        """Le groupe du menu où ce statut se range — une clé de FAMILLES_STATUT."""
        return self._profils[code]["famille"]

    def periodes(self, affiliation: str) -> tuple[dict, ...]:
        """Les tranches temporelles déclarées par ce statut, telles qu'écrites."""
        return tuple(self._profils[affiliation].get("periodes", []))

    def ouverture(self, affiliation: str) -> int:
        """Première année que le statut route — l'année où son régime naît."""
        return min(periode["debut"] for periode in self.periodes(affiliation))

    def fermeture_entrants(self, affiliation: str) -> DateMois | None:
        """Mois depuis lequel le statut est fermé aux nouveaux entrants.

        C'est la clause du grand-père lue depuis le routage lui-même : la plus
        ancienne borne ``entres_avant`` de ses périodes, POUR UN STATUT QUI
        DÉCLARE ``releve_par`` — celui dont le nom même cesse de convenir
        après la date : un jeune d'aujourd'hui ne peut pas se déclarer mineur,
        le régime des mines est fermé aux recrutés depuis septembre 2010, et
        c'est cette date que le formulaire lui oppose. ``None`` pour un statut
        ouvert, et aussi pour un statut dont les régimes changent pour les
        nouveaux entrants sans qu'il cesse d'exister — le libéral non
        réglementé est à la Cipav s'il y était avant 2019, au régime général
        et au RCI sinon, et reste un libéral non réglementé.
        """
        if self.releve_par(affiliation) is None:
            return None
        bornes = [periode["entres_avant"] for periode in self.periodes(affiliation)
                  if periode.get("entres_avant") is not None]
        if not bornes:
            return None
        return DateMois.depuis_rang(min(rang_borne(borne) for borne in bornes))

    def releve_par(self, affiliation: str) -> str | None:
        """Le statut de droit commun dont relève qui entre après la fermeture."""
        return self._profils[affiliation].get("releve_par")

    @property
    def hors_routage(self) -> dict[str, str]:
        """Régimes qu'aucune affiliation ne route, et la raison déclarée."""
        return dict(self._hors_routage)

    def sans_employeur(self, affiliation: str) -> bool:
        """Ce statut cotise-t-il sans employeur ?

        Vrai pour les non-salariés : leur cotisation est intégralement
        personnelle. Le drapeau est porté par le STATUT et non par le régime,
        parce qu'un non-salarié relève souvent d'un régime partagé avec des
        salariés — un artisan cotise au régime général, dont la fiche porte la
        répartition d'un salarié. Le taux y est le bon ; la répartition, non.
        """
        return bool(self._profils.get(affiliation, {}).get("sans_employeur", False))

    def part_salariale_seule(self, affiliation: str) -> bool:
        """Ce statut ne paie-t-il que la part salariale, sans part patronale ?

        Vrai pour les trois statuts d'auteur : l'auteur paie la cotisation du
        salarié, à son taux, et personne ne paie celle de l'employeur — le
        diffuseur ne verse qu'une contribution de 1 %, toutes branches
        confondues. C'est l'inverse de ``sans_employeur``, où l'assuré paie
        les deux ; dans les deux cas, le compte ne porte aucune part patronale.
        """
        return bool(self._profils.get(affiliation, {}).get(
            "part_salariale_seule", False))

    def categorie_active(self, affiliation: str) -> str | None:
        """Classement de l'emploi : ``active``, ``super_active`` ou rien.

        Le classement tient à l'EMPLOI, pas à la personne ni au régime : un
        aide-soignant et un rédacteur territorial cotisent à la même CNRACL, et
        l'un liquide cinq ans avant l'autre. Aucune donnée de carrière — revenu,
        régime, âge — ne permet de le deviner ; c'est donc le statut déclaré qui
        le porte, comme il porte déjà l'absence d'employeur.
        """
        classement = self._profils.get(affiliation, {}).get("categorie_active")
        if classement is None:
            return None
        if classement not in ("active", "super_active"):
            raise ValueError(
                f"{affiliation} : classement inconnu {classement!r} "
                "(attendu 'active' ou 'super_active')"
            )
        return classement

    def pension_militaire(self, affiliation: str) -> str | None:
        """Catégorie militaire : ``non_officier``, ``officier`` ou rien.

        Les militaires relèvent du même régime que les fonctionnaires civils de
        l'État — le code s'appelle « des pensions civiles ET MILITAIRES » — mais
        leur pension ne s'ouvre pas à un âge : elle s'ouvre à une durée de
        services, différente selon qu'ils sont officiers ou non.
        """
        categorie = self._profils.get(affiliation, {}).get("pension_militaire")
        if categorie is None:
            return None
        if categorie not in ("non_officier", "officier"):
            raise ValueError(
                f"{affiliation} : catégorie militaire inconnue {categorie!r} "
                "(attendu 'non_officier' ou 'officier')"
            )
        return categorie

    @property
    def classements_actifs(self) -> dict[str, str]:
        """Statuts classés en catégorie active, et leur classement."""
        return {code: self.categorie_active(code) for code in self.codes
                if self.categorie_active(code) is not None}

    @property
    def categories_militaires(self) -> dict[str, str]:
        """Statuts militaires, et leur catégorie."""
        return {code: self.pension_militaire(code) for code in self.codes
                if self.pension_militaire(code) is not None}

    def regimes(self, affiliation: str, annee: int,
                annee_entree: int | DateMois | None = None,
                revenu: float | None = None,
                plafond: float | None = None) -> tuple[str, ...]:
        """Régimes applicables à ce statut cette année-là.

        **La fermeture d'un régime ne vaut que pour les nouveaux entrants.**
        Le régime de la SNCF est fermé aux agents recrutés depuis le 1er janvier
        2020, celui de la RATP et celui des IEG depuis le 1er septembre 2023 :
        un agent recruté avant garde le sien jusqu'à sa retraite, et c'est la
        « clause du grand-père ». Le routage par la seule ANNÉE faisait basculer
        tout le monde à la date de fermeture, y compris l'agent entré vingt ans
        plus tôt : un cheminot né en 1975, entré en 1996, perdait vingt années
        de régime spécial et vingt points de taux de remplacement.

        Une période peut donc porter `entres_avant` ou `entres_depuis`, et
        ``annee_entree`` — l'entrée dans le statut, une année ou un mois
        (:class:`DateMois`) — dit laquelle s'applique. Les bornes s'écrivent
        au mois quand la loi le fait — « recrutés à compter du 1er septembre
        2023 » — et une année vaut son 1er janvier. Sans entrée, on suppose
        une entrée en janvier de l'année demandée : c'est le comportement
        d'avant, et il reste juste pour qui commence sa carrière cette
        année-là.

        **Un régime peut n'être dû qu'au-delà d'un seuil de revenu.** L'élu
        local n'est assujetti au régime général que « lorsque le montant
        total [de ses indemnités] est supérieur à une fraction, fixée par
        décret, de la valeur du plafond » (L. 382-31) — la moitié. Une
        période porte alors ``seuil_pass: {regime: fraction}`` ; quand
        ``revenu`` et ``plafond`` (de l'année) sont fournis, les régimes dont
        le seuil n'est pas atteint sont retirés. Sans eux, la période est
        rendue telle quelle : c'est la liste des régimes POSSIBLES, celle
        que l'inventaire et les tests de cohérence attendent.
        """
        if affiliation not in self._profils:
            raise KeyError(
                f"affiliation inconnue : {affiliation!r}. Disponibles : "
                + ", ".join(self.codes)
            )
        if annee_entree is None:
            entree = DateMois(annee, 1).rang
        elif isinstance(annee_entree, DateMois):
            entree = annee_entree.rang
        else:
            entree = DateMois(int(annee_entree), 1).rang
        for periode in self._profils[affiliation].get("periodes", []):
            fin = periode.get("fin")
            if not (periode["debut"] <= annee and (fin is None or annee <= fin)):
                continue
            avant, depuis = periode.get("entres_avant"), periode.get("entres_depuis")
            if avant is not None and entree >= rang_borne(avant):
                continue
            if depuis is not None and entree < rang_borne(depuis):
                continue
            regimes = tuple(periode.get("regimes") or ())
            seuils = periode.get("seuil_pass") or {}
            if seuils and revenu is not None and plafond is not None:
                regimes = tuple(
                    code for code in regimes
                    if revenu >= float(seuils.get(code, 0.0)) * plafond
                )
            return regimes
        return ()
