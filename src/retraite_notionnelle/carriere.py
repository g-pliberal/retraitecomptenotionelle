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
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from .donnees.chargement import (
    charger_periodes_non_travaillees,
    charger_table_csv,
    charger_yaml,
)
from .donnees.macro import DonneesMacro
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
    #: complémentaires acquièrent des points sur cette base pendant les
    #: périodes indemnisées, financés par l'UNEDIC ou la Sécurité sociale.
    revenu_reference: float = 0.0
    #: Familles de régimes qui encaissent des cotisations sur
    #: ``revenu_reference`` alors que l'année n'est pas travaillée.
    familles_cotisantes: tuple[str, ...] = ()
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
    """

    #: Statut d'affiliation (clé de ``legislation/affiliations.yaml``).
    affiliation: str
    #: Âge auquel ce métier commence, en années décimales.
    age_debut: float
    #: Niveau de revenu, en multiples du salaire moyen par tête de l'année.
    niveau_salaire: float = 1.0


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
    if trimestres_declares is None:
        trimestres = (macro.trimestres_valides(revenu, annee) if cotise
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
        cotisations_versees=cotise,
        # Pendant une période indemnisée, l'UNEDIC ou la Sécurité sociale
        # versent de vraies cotisations aux régimes complémentaires, assises
        # sur le salaire d'avant.
        revenu_reference=(
            0.0 if cotise or regle is None
            or not regle.ouvre_droits_complementaires else revenu
        ),
        familles_cotisantes=(
            () if cotise or regle is None
            or not regle.ouvre_droits_complementaires
            else ("complementaire_prive",)
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
    )


@dataclass
class Carriere:
    """Carrière complète d'un assuré."""

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
        self.lignes.sort(key=lambda ligne: ligne.annee)

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
        """
        return self.annee_naissance + (self.mois_naissance - 1) / 12

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
        return tuple(ligne.annee for ligne in self.lignes if ligne.cotise)

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
        return [ligne for ligne in self.lignes
                if ligne.affiliation in codes and ligne.cotise
                and (jusqu_a is None or ligne.annee <= jusqu_a)]

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
        return sum(self.trimestres_retenus(ligne) for ligne in self.lignes)

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
        part = self.part_retenue(ligne.annee)
        if part <= 0:
            return 0
        return min(ligne.trimestres_valides, trimestres_civils(round(part * 12)))

    def ligne(self, annee: int) -> AnneeCarriere | None:
        for l in self.lignes:
            if l.annee == annee:
                return l
        return None

    def affiliations_utilisees(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(ligne.affiliation for ligne in self.lignes))

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
        profil_carriere: str = "plat",
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
        profil_carriere: str = "plat",
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
        la vie active, et il vaut pour la carrière ENTIÈRE, changements de métier
        compris — c'est une progression de carrière, pas d'emploi :

        * ``plat`` — le salaire suit exactement le salaire moyen ;
        * ``ascendant`` — le salaire relatif croît de 60 % à 130 % du niveau
          cible (profil ouvrier/employé) ;
        * ``fortement_ascendant`` — de 50 % à 190 % (profil cadre).

        Le niveau de revenu propre à chaque métier se superpose à cette
        déformation : changer de métier déplace le niveau, il ne remet pas la
        progression à zéro.

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
            deformation = profil_salaire(
                macro.racine, profil_carriere,
                annee - annee_naissance, annee,
            )
            # Ce que chaque métier a occupé de l'année. La somme vaut les mois
            # travaillés de l'année : les périodes la découpent sans reste.
            mois_par_metier = [mois_travailles(annee, ouverture, cloture)
                               for _, ouverture, cloture in periodes]
            revenu = sum(
                metier.niveau_salaire * deformation
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

        dates_entree: dict[str, DateMois] = {}
        for metier, ouverture, _ in periodes:
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
}

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


def profil_salaire(racine: Path, profil: str, age: float, annee: int) -> float:
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
    if profil not in PROFILS_CATEGORIE:
        raise ValueError(f"profil de carrière inconnu : {profil!r}")
    categorie = PROFILS_CATEGORIE[profil]
    if categorie is None:
        return 1.0
    table = _table_profil(racine, "profil_salaire_categorie.csv", "categorie")
    forme = _interpole_tranches(table.get(categorie, {}), TRANCHES_CATEGORIE, age)
    return 1.0 + (forme - 1.0) * _modulation_annee(racine, annee)


def bornes_deformation(racine: Path, profil: str) -> tuple[float, float]:
    """Ce que le profil fait du niveau saisi, en début et en fin de carrière.

    Lues à l'année de référence de la forme : ce sont les deux nombres que le
    site affiche sous le menu des profils, et ils doivent donc être ceux d'une
    carrière observée et non d'un bord de table.
    """
    if PROFILS_CATEGORIE.get(profil) is None:
        return 1.0, 1.0
    return (profil_salaire(racine, profil, 25.0, ANNEE_FORME_CATEGORIE),
            profil_salaire(racine, profil, 60.0, ANNEE_FORME_CATEGORIE))


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
