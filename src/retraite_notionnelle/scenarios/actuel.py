"""Scénario 1 — le système actuel, tel qu'il est.

Ce scénario sert d'étalon : c'est la pension que l'assuré perçoit ou percevra
en droit constant. Il conserve tout ce que les scénarios notionnels retirent —
minima, majorations, trimestres gratuits, décote et surcote, bonifications.

Portée et limites
-----------------
Reproduire exactement le droit positif de tous les régimes depuis 1930
supposerait un moteur législatif complet, du type de ceux de la DREES
(TRAJECTOiRE) ou de l'Institut des politiques publiques (PENSIPP). Ce module
est une **approximation documentée**, pas un simulateur officiel :

* régimes en annuités — formule ``taux × salaire de référence × durée / durée
  requise``, avec décote et surcote de la période ;
* régimes en points — la pension est calculée **en points**. Deux façons de les
  acquérir, selon ce que la caisse publie : par un PRIX D'ACHAT, la cotisation
  de l'année étant divisée par le salaire de référence de cette année-là
  (``regimes/valeurs_point.csv``) ; ou par un BARÈME EN POINTS, le régime
  annonçant combien de points ouvre une assiette donnée — 525 points au plafond
  au régime de base des libéraux, 100 points pour 1 820 SMIC à la complémentaire
  agricole. Le total est converti en rente par la valeur de service de l'année
  de liquidation. Les points d'un régime fermé sont convertis dans son
  successeur au rapport des deux valeurs de service, comme l'ont fait
  l'unification Arrco de 1999 et la fusion Agirc-Arrco de 2019. Restent au
  rendement instantané (``regimes/rendements_points.csv``) la CNBF, le RCI et le
  RAFP, et les années postérieures au dernier barème publié ;
* trois horloges, comme dans le droit — ce qui s'ACQUIERT est lu à l'année
  travaillée (taux de cotisation, assiette, plafond, prix d'achat du point,
  heures pour valider un trimestre) ; ce qui commande la MONTÉE EN CHARGE des
  réformes est lu à la GÉNÉRATION (durée requise, âge d'ouverture, âge
  d'annulation de la décote, coefficient de minoration, années retenues au
  salaire de référence) ; ce qui LIQUIDE est lu à l'année de liquidation
  (formule du régime, valeur de service du point, barèmes des minima) ;
* avantages datés — la fiche de chaque période dit ce que le régime accordait
  cette année-là, et le moteur ne sert que cela : ni minimum contributif avant
  1983, ni surcote avant 2004, ni trimestres pour enfants avant 1972.

Un écart de quelques pour cent avec la pension réelle est donc attendu.
Ce que le modèle mesure de façon robuste, ce sont les ÉCARTS ENTRE SCÉNARIOS,
tous calculés sur les mêmes carrières et les mêmes séries.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field, replace
from pathlib import Path

from ..calendrier import DateMois, en_mois
from ..carriere import Affiliations, Carriere, salaire_moyen_annuel
from ..config import Parametres
from ..donnees.chargement import (
    Fiabilite,
    charger_table_par_generation,
    valeur_par_generation,
)
from ..donnees.macro import DonneesMacro
from ..donnees.regimes import (CatalogueRegimes, ClassesCotisation, SalairesForfaitaires,
                              PeriodeRegime)


@dataclass(frozen=True)
class PensionRegime:
    """Pension annuelle brute servie par un régime."""

    regime: str
    montant: float
    type_calcul: str
    detail: str
    fiabilite: Fiabilite


@dataclass(frozen=True)
class AvantageApplique:
    """Effet en euros d'un avantage non contributif du droit positif.

    Les trois avantages s'appliquent dans cet ordre, et l'ordre compte : la
    MDA ajoute des trimestres, donc modifie la décote et la proratisation AVANT
    que la majoration ne multiplie, et le minimum ne comble qu'ensuite. Leurs
    effets s'additionnent exactement au total : c'est ce qui rend la cascade
    vérifiable ligne à ligne.
    """

    code: str
    libelle: str
    montant: float
    detail: str = ""


@dataclass(frozen=True)
class _MajorationEnfants:
    """Trimestres dus au titre des enfants, et régime qui les porte."""

    #: Code du régime dans lequel le droit attribue les trimestres.
    regime: str
    #: Dispositif qui les accorde : ``mda`` ou ``bonifications``.
    dispositif: str
    #: Trimestres accordés au total, tous enfants confondus. Ils jouent sur la
    #: durée d'assurance tous régimes, donc sur la décote et la surcote.
    trimestres: int
    #: Ceux d'entre eux qui entrent dans les SERVICES du régime, et relèvent
    #: donc son prorata. Une bonification en est ; une majoration de durée
    #: d'assurance n'en est pas — voir l'en-tête de
    #: `legislation/majoration_duree_assurance.csv`.
    services: int
    fiabilite: Fiabilite


#: Ce que chaque dispositif s'appelle dans la cascade des avantages.
_LIBELLE_MAJORATION = {
    "mda": "Majoration de durée d'assurance",
    "bonifications": "Bonification pour enfants",
}


@dataclass(frozen=True)
class _EligibleMinimum:
    """Régime de base susceptible d'être porté au minimum contributif.

    Quatre grandeurs, et pas une seule, parce que le droit en demande quatre :
    la pension à relever, les deux fractions de durée qui proratisent le
    montant de base et sa majoration, la condition de taux plein qui ouvre le
    droit, et le coefficient de surcote qu'il faut retirer avant de comparer
    au plancher puis rendre après.
    """

    #: Indice de la pension dans ``ResultatActuel.pensions_par_regime``.
    indice: int
    #: Durée d'assurance acquise dans le régime / durée requise, bornée à 1.
    prorata_assurance: float
    #: Durée COTISÉE acquise dans le régime / durée requise, bornée à 1.
    prorata_cotise: float
    #: La pension est-elle liquidée au taux plein dans ce régime ?
    taux_plein: bool
    #: Coefficient de surcote déjà incorporé au montant de la pension.
    surcote: float = 1.0


@dataclass(frozen=True)
class _EligibleMinimumGaranti:
    """Régime de la fonction publique susceptible d'atteindre son plancher."""

    #: Indice de la pension dans ``ResultatActuel.pensions_par_regime``.
    indice: int
    #: Durée de services acquise dans le régime, en trimestres.
    trimestres_services: int
    #: La pension est-elle liquidée au taux plein, ou l'assuré atteignait-il
    #: l'âge d'ouverture de ses droits avant 2011 ?
    ouvert: bool


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

    @property
    def pension_mensuelle(self) -> float:
        return self.pension_annuelle / 12.0


class Rendements:
    """Rendements instantanés des régimes en points."""

    def __init__(self, racine: Path) -> None:
        self._table: list[tuple[str, int, int, float, Fiabilite]] = []
        chemin = racine / "reference" / "regimes" / "rendements_points.csv"
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                self._table.append((
                    ligne["regime"], int(ligne["debut"]), int(ligne["fin"]),
                    float(ligne["rendement"]),
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                ))

    def rendement(self, regime: str, annee: int) -> tuple[float, Fiabilite]:
        for code, debut, fin, valeur, fiabilite in self._table:
            if code == regime and debut <= annee <= fin:
                return valeur, fiabilite
        return 0.0, Fiabilite.ESTIMEE


class TableParGeneration:
    """Paramètre législatif indexé sur l'ANNÉE DE NAISSANCE.

    Depuis la loi du 22 juillet 1993 pour la durée d'assurance, et la loi du
    9 novembre 2010 pour l'âge d'ouverture, les deux paramètres qui commandent
    le taux plein dépendent de la génération et non de l'année de liquidation :
    deux assurés qui liquident le même jour ne se voient pas opposer la même
    exigence. Les lire à l'année de liquidation, comme le faisait ce module,
    opposait aux générations anciennes des règles que la loi ne leur a jamais
    appliquées.

    Lecture en escalier : la valeur d'une génération non renseignée est celle
    de la dernière génération renseignée avant elle, et la dernière valeur du
    fichier vaut pour toutes les générations suivantes — une cible atteinte ne
    bouge plus. En deçà de la première, le paramètre ne dépendait pas encore de
    la génération : on renvoie ``None`` pour que la fiche du régime reprenne la
    main.

    **La génération peut porter des décimales, et le doit.** Deux textes ne
    coupent pas au 1er janvier : la loi du 9 novembre 2010 s'applique aux
    assurés nés À COMPTER DU 1er JUILLET 1951, celle du 14 avril 2023 à ceux
    nés à compter du 1er septembre 1961. Une génération s'écrit donc
    ``1951.5`` ou ``1961.667`` — l'année plus la part écoulée avant le premier
    du mois visé —, et la clé de lecture est construite de la même façon à
    partir du mois de naissance. Le modèle retenait jusqu'ici, pour ces deux
    années, la valeur couvrant le plus de mois : l'approximation valait un
    trimestre, et elle disparaît.
    """

    def __init__(self, racine: Path, fichier: str, colonne: str) -> None:
        # La lecture passe par le chargeur mémorisé, comme les séries
        # annuelles : ces tables sont relues à chaque construction de scénario,
        # et `carriere.py` lit la même durée requise pour l'étalon de son
        # profil salarial. Un seul analyseur, donc, et une seule sémantique.
        self._table, self._generations = charger_table_par_generation(
            racine / "reference" / "legislation" / fichier, colonne
        )

    def valeur(self, generation: float) -> tuple[float, Fiabilite] | None:
        return valeur_par_generation(self._table, self._generations, generation)


class DureesRequises(TableParGeneration):
    """Durée d'assurance requise pour le taux plein, par génération."""

    def __init__(self, racine: Path) -> None:
        super().__init__(racine, "duree_assurance_requise.csv", "trimestres")

    def trimestres(self, generation: float) -> tuple[int, Fiabilite] | None:
        valeur = self.valeur(generation)
        return None if valeur is None else (int(valeur[0]), valeur[1])


class DureesRequisesRegimes:
    """Durée requise propre à un régime spécial, par génération.

    La SNCF, la RATP et les IEG écrivent chacun leur table dans leur décret, et
    la suspension de 2026, qui a abaissé la table commune, ne les a pas
    touchées. La fiche nomme la sienne (`duree_requise_table`) sur ses périodes
    de 2025 et après.

    La table de la SNCF porte en plus ce que le II de l'article 35 du décret
    n° 2008-639 retranche à la durée requise pour compter la décote par la
    durée — jusqu'à dix trimestres pour un agent de conduite né en 1980.
    """

    FICHIER = "duree_requise_regimes_speciaux.csv"

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, dict[float, tuple[int, int, Fiabilite]]] = {}
        chemin = racine / "reference" / "legislation" / self.FICHIER
        if chemin.exists():
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    self._table.setdefault(ligne["table"], {})[
                        float(ligne["generation"])
                    ] = (int(ligne["trimestres"]), int(ligne["retranche_decote"]),
                         Fiabilite.depuis_texte(ligne["fiabilite"]))
        self._generations = {cle: tuple(sorted(valeurs))
                             for cle, valeurs in self._table.items()}

    def ligne(self, table: str,
              generation: float) -> tuple[int, int, Fiabilite] | None:
        """Trimestres requis, trimestres retranchés pour la décote, fiabilité."""
        generations = self._generations.get(table)
        if not generations:
            return None
        return valeur_par_generation(self._table[table], generations, generation)


class DureesRequisesFonctionPublique:
    """Durée de services requise dans la fonction publique, 2004-2008.

    Le II de l'article 66 de la loi du 21 août 2003 fait monter « le nombre
    de trimestres nécessaires pour obtenir le pourcentage maximum de la
    pension » de 150 à 160, deux par an, selon l'ANNÉE OÙ LE DROIT S'OUVRE.
    Ce nombre commande à la fois la proratisation, le décompte de la décote et
    le seuil de la surcote. Avant 2004, la fiche du régime porte 150 ; à
    compter de 2009, l'article L. 13 II renvoie à la durée du régime général,
    lue par génération. La table ne répond donc que pour les années qu'elle
    porte, et rend ``None`` ailleurs.

    Le modèle lisait ces années dans la table du régime général — 160 pour
    toute génération née depuis 1943 —, et c'est la confrontation à
    OpenFisca-France-Pension qui l'a fait voir.
    """

    FICHIER = "duree_requise_fonction_publique.csv"

    def __init__(self, racine: Path) -> None:
        self._table: dict[int, tuple[int, Fiabilite]] = {}
        chemin = racine / "reference" / "legislation" / self.FICHIER
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                self._table[int(ligne["annee_ouverture"])] = (
                    int(ligne["trimestres"]),
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                )

    def trimestres(self, annee_ouverture: int) -> tuple[int, Fiabilite] | None:
        return self._table.get(annee_ouverture)


class DureesProratisation(TableParGeneration):
    """Durée maximale d'assurance prise en compte par la proratisation.

    **Ce n'est pas la durée requise pour le taux plein**, et le module les
    confondait. Le droit en a deux : la durée REQUISE (L. 161-17-3) commande le
    taux, et l'on est décoté en deçà ; la durée maximale prise en compte par la
    PRORATISATION (R. 351-6) est le dénominateur qui réduit la pension d'une
    carrière incomplète. La loi du 22 juillet 1993 a fait monter la première de
    150 à 160 trimestres pour les générations 1934 à 1943, et n'a touché à la
    seconde que pour les générations 1944 à 1948.

    Un assuré né en 1945 ayant validé 156 trimestres se voit donc opposer
    160 trimestres pour le taux — il lui en manque quatre, il est décoté — mais
    154 pour la proratisation : son coefficient vaut 1, pas 156/160.

    **La lecture s'arrête à la dernière génération du fichier**, au lieu de
    prolonger sa dernière valeur comme le font les autres tables par génération.
    C'est voulu : à compter de la génération 1949 il n'y a plus deux paramètres,
    la durée de proratisation rejoint la durée requise, et prolonger 160
    trimestres à des générations qui en doivent 172 rendrait à la proratisation
    l'erreur qu'on vient d'en retirer, dans l'autre sens.
    """

    def __init__(self, racine: Path) -> None:
        super().__init__(racine, "duree_proratisation.csv", "trimestres")

    def trimestres(self, generation: float) -> tuple[int, Fiabilite] | None:
        if not self._table or generation > self._generations[-1]:
            return None
        valeur = self.valeur(generation)
        return None if valeur is None else (int(valeur[0]), valeur[1])


class AgesOuverture(TableParGeneration):
    """Âge légal d'ouverture des droits, par génération.

    C'est lui qui commande la surcote : seuls les trimestres cotisés au-delà de
    cet âge la déclenchent.
    """

    def __init__(self, racine: Path) -> None:
        super().__init__(racine, "age_ouverture_requis.csv", "age")

    def age(self, generation: float) -> tuple[float, Fiabilite] | None:
        return self.valeur(generation)


class AgesAnnulationDecote(TableParGeneration):
    """Âge d'annulation de la décote, par génération.

    C'est lui qui commande la décote de l'assuré parti tôt : 65 ans jusqu'à la
    génération 1950, 67 à partir de 1955. Les fiches de régime portaient l'âge
    CIBLE de la loi de 2010 dès son entrée en vigueur, opposant 67 ans à des
    générations auxquelles la loi n'a jamais demandé plus de 65.
    """

    def __init__(self, racine: Path) -> None:
        super().__init__(racine, "age_annulation_decote.csv", "age")

    def age(self, generation: float) -> tuple[float, Fiabilite] | None:
        return self.valeur(generation)


@dataclass(frozen=True)
class DerogationActive:
    """Ce que le classement d'un emploi déplace, pour une génération."""

    #: Âge anticipé (catégorie active) ou minoré (super-active) : L. 24, I, 1°.
    age_ouverture: float
    #: Âge d'annulation de la décote : limite d'âge du grade jusqu'en 2023,
    #: article L. 14 bis ensuite.
    age_annulation: float
    #: Années de services classés sans lesquelles rien de tout cela ne vaut.
    services_requis: float
    #: Durée de services et bonifications requise, quand le classement en a une
    #: qui lui soit propre — « par dérogation à l'article L. 13 ». ``None``
    #: quand la durée de la génération vaut, ce qui est le cas jusqu'à 1961.
    duree_requise: int | None
    fiabilite: Fiabilite


class AgesCategorieActive:
    """Âges de la catégorie active et de la super-active, par génération.

    Le drapeau ``categorie_active`` existait dans ``config.py`` sans qu'aucun
    statut le porte : le policier et l'aide-soignant étaient calculés comme des
    sédentaires, et l'âge du sédentaire leur était opposé. Cette table porte les
    trois paramètres que le classement déplace — l'âge d'ouverture, l'âge
    d'annulation de la décote, la durée de services classés exigée — pour les
    deux classements, lus en escalier sur la génération comme les autres.

    Le classement vient du STATUT, non du régime : ``affiliations.yaml`` le
    porte, parce qu'aucune donnée de carrière ne permet de le deviner.
    """

    FICHIER = "categorie_active.csv"

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, dict[float, DerogationActive]] = {}
        chemin = racine / "reference" / "legislation" / self.FICHIER
        if not chemin.exists():
            self._generations: dict[str, list[float]] = {}
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                self._table.setdefault(ligne["classement"], {})[
                    float(ligne["generation"])
                ] = DerogationActive(
                    age_ouverture=float(ligne["age_ouverture"]),
                    age_annulation=float(ligne["age_annulation"]),
                    services_requis=float(ligne["services_requis_annees"]),
                    duree_requise=(
                        int(ligne["duree_requise_trimestres"])
                        if ligne.get("duree_requise_trimestres", "").strip()
                        else None
                    ),
                    fiabilite=Fiabilite.depuis_texte(ligne["fiabilite"]),
                )
        self._generations = {classement: sorted(valeurs)
                             for classement, valeurs in self._table.items()}

    @property
    def classements(self) -> tuple[str, ...]:
        return tuple(sorted(self._table))

    def derogation(self, classement: str,
                   generation: float) -> DerogationActive | None:
        generations = self._generations.get(classement)
        if not generations or generation < generations[0]:
            return None
        applicable = generations[0]
        for candidate in generations:
            if candidate > generation:
                break
            applicable = candidate
        return self._table[classement][applicable]


class DureesServicesMilitaires:
    """Durée de services qui ouvre la pension militaire, par année d'atteinte.

    La pension militaire ne s'ouvre pas à un âge mais à une durée : dix-sept ans
    de services effectifs pour un non-officier, vingt-sept pour un officier
    (L. 24, II), quinze et vingt-cinq avant la loi du 9 novembre 2010.

    **La clé n'est pas la génération.** L'article 4 du décret n° 2011-2103
    indexe le relèvement sur « l'année au cours de laquelle sont atteintes les
    limites de durée de services […] antérieurement applicables » : c'est donc
    l'année où le militaire réunit quinze — ou vingt-cinq — ans qui commande la
    durée qu'on lui oppose, et non son année de naissance.
    """

    FICHIER = "duree_services_militaires.csv"

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, dict[float, tuple[float, Fiabilite]]] = {}
        chemin = racine / "reference" / "legislation" / self.FICHIER
        if not chemin.exists():
            self._annees: dict[str, list[float]] = {}
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                self._table.setdefault(ligne["categorie"], {})[
                    float(ligne["annee_atteinte"])
                ] = (float(ligne["annees_requises"]),
                     Fiabilite.depuis_texte(ligne["fiabilite"]))
        self._annees = {categorie: sorted(valeurs)
                        for categorie, valeurs in self._table.items()}

    @property
    def categories(self) -> tuple[str, ...]:
        return tuple(sorted(self._table))

    def duree_de_base(self, categorie: str) -> float | None:
        """Durée d'avant la loi de 2010 — quinze ans, ou vingt-cinq."""
        annees = self._annees.get(categorie)
        if not annees:
            return None
        return self._table[categorie][annees[0]][0]

    def annees_requises(self, categorie: str,
                        annee_atteinte: float) -> tuple[float, Fiabilite] | None:
        annees = self._annees.get(categorie)
        if not annees:
            return None
        applicable = annees[0]
        for candidate in annees:
            if candidate > annee_atteinte:
                break
            applicable = candidate
        return self._table[categorie][applicable]


class AgesJouissanceMilitaire(TableParGeneration):
    """Âge auquel la pension militaire différée entre en jouissance.

    Les 2° à 4° de l'article L. 25 servent une pension au militaire qui part
    avant la durée d'ouverture, à condition qu'il ait quinze ans de services,
    mais à « l'âge défini à l'article L. 161-17-2 […] abaissé de dix années ».
    """

    def __init__(self, racine: Path) -> None:
        super().__init__(racine, "age_jouissance_militaire.csv", "age")

    def age(self, generation: float) -> tuple[float, Fiabilite] | None:
        return self.valeur(generation)


#: Durée minimale de services qui ouvre une pension militaire, même différée :
#: « lorsqu'ils ont accompli […] moins de quinze ans de services effectifs »,
#: dit le 5° de l'article L. 25, la pension n'est due qu'à l'âge légal.
SERVICES_MINIMAUX_MILITAIRES = 15.0

#: Trimestres de services que le II de l'article L. 14 ajoute à la durée
#: d'ouverture pour borner la décote militaire, et plafond de celle-ci.
TRIMESTRES_DECOTE_MILITAIRE = 10


@dataclass(frozen=True)
class _DroitMilitaire:
    """Ce que la pension militaire oppose à un assuré, une fois sa carrière lue."""

    #: Âge auquel la pension s'ouvre : celui où la durée est atteinte, ou l'âge
    #: de jouissance différée de l'article L. 25.
    age_ouverture: float
    #: Trimestres de services militaires accomplis à la liquidation.
    trimestres_servis: int
    #: Durée d'ouverture majorée des dix trimestres du II de l'article L. 14 :
    #: c'est elle, et non l'âge, qui borne la décote d'un militaire.
    trimestres_cible: int
    #: Vrai quand la pension n'est due qu'à l'âge différé, faute de la durée.
    jouissance_differee: bool
    fiabilite: Fiabilite


class CoefficientsMinoration(TableParGeneration):
    """Coefficient de minoration du taux plein par trimestre manquant."""

    def __init__(self, racine: Path) -> None:
        super().__init__(racine, "coefficient_minoration.csv", "coefficient")

    def coefficient(self, generation: float) -> tuple[float, Fiabilite] | None:
        return self.valeur(generation)


class AnneesSalaireReference(TableParGeneration):
    """Nombre d'années retenues au salaire annuel moyen, par génération."""

    def __init__(self, racine: Path) -> None:
        super().__init__(racine, "annees_salaire_reference.csv", "annees")

    def annees(self, generation: int) -> tuple[int, Fiabilite] | None:
        valeur = self.valeur(generation)
        return None if valeur is None else (int(valeur[0]), valeur[1])


#: Coefficients d'anticipation de l'Agirc-Arrco, sous leur forme de barème.
#: Le régime n'applique pas la décote du régime de base : il a ses propres
#: coefficients, publiés en deux tables — l'une indexée sur les trimestres
#: manquants, l'autre sur l'âge — dont il retient la plus favorable.
#:
#: Les deux tables descendent par paliers réguliers, et c'est cette régularité
#: qu'on écrit ici plutôt que quarante lignes de barème : un point de
#: pourcentage par trimestre jusqu'à douze, un point et quart jusqu'à vingt,
#: un point trois quarts au-delà — ce dernier palier n'existant que dans la
#: table des âges, qui descend jusqu'à 0,43 pour dix ans d'anticipation.
_PALIERS_ANTICIPATION: tuple[tuple[int, float], ...] = (
    (12, 0.01), (20, 0.0125), (40, 0.0175),
)

#: Les deux barèmes de minoration des régimes de l'IRCEC (RAAP, RACD, RACL),
#: qui comptent des années manquantes et non des trimestres : voir
#: ``_abattement_ircec``.
_ABATTEMENTS_IRCEC = ("ircec", "ircec_age_seul")

#: Dernière ligne de la table des âges : dix ans d'anticipation. Au-delà, le
#: barème ne descend plus.
_COEFFICIENT_ANTICIPATION_PLANCHER = 0.43

#: Majoration par trimestre ENTIER écoulé entre l'âge du taux plein et la
#: liquidation — le 1° du IV de l'article 16 de l'arrêté du 30 décembre 1970,
#: « 0,75 % par trimestre entier écoulé entre le soixante-cinquième
#: anniversaire de l'assuré et la date d'entrée en jouissance de la pension ».
#: Aucune condition de durée ne s'y attache : c'est le temps qui compte.
_SURCOTE_IRCANTEC_AGE = 0.0075

#: Majoration par trimestre COTISÉ au-delà de la durée requise, entre l'âge
#: légal et l'âge du taux plein — le 2° du même IV, « 0,625 % par trimestre
#: accompli ». Son assiette est celle de la surcote du régime général, bornée
#: en haut par l'âge où le 1° prend le relais : « en aucun cas une même période
#: ne peut donner lieu à la fois à l'attribution de la majoration prévue au 1°
#: et à celle prévue au 2° ».
_SURCOTE_IRCANTEC_DUREE = 0.00625


def _sans_zeros_inutiles(valeur: float, decimales: int) -> str:
    """Un nombre à ``decimales`` chiffres au plus, sans les zéros de fin.

    Certaines valeurs de service sont des barèmes PUBLIÉS à quatre décimales —
    1,8026 € à l'Agirc-Arrco —, d'autres sont CALCULÉES et en portent bien
    davantage. Les tronquer toutes à quatre inventait un écart de vingt-huit
    centimes entre la formule affichée et le montant de la ligne ; les afficher
    toutes à six aurait inventé, à l'inverse, une précision que le barème n'a
    pas. Chacune est donc écrite à la précision qu'elle porte.
    """
    return f"{valeur:.{decimales}f}".rstrip("0").rstrip(".")


def _formule_points(termes: list[str], coefficient: float) -> str:
    """La formule d'un régime en points, telle qu'on doit pouvoir la refaire.

    Le coefficient multiplie la SOMME des termes, il ne s'y ajoute pas : il
    vient donc après, et la somme prend ses parenthèses dès qu'elle en compte
    plusieurs. Sans lui, la formule affichée ne retrouvait pas le montant de la
    ligne — à dix ans d'anticipation elle en donnait 2,3 fois trop, sans que
    rien à l'écran ne dise pourquoi.

    Il se nomme par ce qu'il fait : « coefficient d'anticipation » quand il
    retire, « coefficient de majoration » quand il ajoute. Un seul régime
    ajoute — l'Ircantec, dont le IV de l'article 16 de l'arrêté du 30 décembre
    1970 majore les points d'une liquidation tardive —, et l'appeler
    « anticipation » aurait écrit le contraire de ce qu'il vaut.
    """
    formule = " + ".join(termes) or "aucun droit"
    if coefficient == 1.0 or not termes:
        return formule
    if len(termes) > 1:
        formule = f"({formule})"
    nom = "de majoration" if coefficient > 1.0 else "d'anticipation"
    return f"{formule} × coefficient {nom} {coefficient:.4f}"


def _au_trimestre_superieur(trimestres: float) -> int:
    """Nombre de trimestres arrondi à l'entier supérieur, jamais négatif.

    C'est la règle de l'article R. 351-27 pour la décote, et celle que la
    caisse illustre dans son exemple pour les coefficients d'anticipation : un
    assuré à qui il manque trois ans et dix mois se voit opposer seize
    trimestres, pas quinze. La tolérance de 10⁻³ évite qu'un flottant tout juste
    au-dessus d'un entier n'en fasse compter un de plus.
    """
    return max(0, -(-int(round(trimestres * 1000)) // 1000))


def _coefficient_anticipation(trimestres_manquants: float,
                              maximum: int) -> float | None:
    """Coefficient d'anticipation Agirc-Arrco pour un nombre de trimestres.

    ``maximum`` est la dernière ligne du barème : vingt trimestres pour la
    table des trimestres manquants, quarante pour celle des âges. Au-delà, la
    table ne dit rien et ``None`` est renvoyé — la prolonger reviendrait à
    inventer un coefficient plus favorable que celui de l'autre table, alors
    que le régime retient la plus avantageuse des deux.

    Les trimestres sont comptés en ENTIERS ARRONDIS AU SUPÉRIEUR : le barème
    est un escalier, et un assuré à qui il manque trois ans et dix mois se voit
    opposer seize trimestres, pas quinze. C'est la lecture que la caisse
    illustre elle-même dans son exemple.
    """
    manquants = _au_trimestre_superieur(trimestres_manquants)
    if manquants <= 0:
        return 1.0
    if manquants > maximum:
        return None
    coefficient = 1.0
    precedent = 0
    for borne, pas in _PALIERS_ANTICIPATION:
        tranche = min(manquants, borne) - precedent
        if tranche > 0:
            coefficient -= tranche * pas
        precedent = borne
        if manquants <= borne:
            break
    return max(0.0, coefficient)


class MajorationsPourEnfants:
    """Trimestres accordés au titre des enfants, dispositif par dispositif.

    Le module en servait huit par enfant, à tout assuré, à toute date et dans
    tout régime. Le droit n'en a jamais servi autant : la majoration de durée
    d'assurance n'existe pas avant 1972, elle vaut un an par enfant jusqu'en
    1974, elle est attribuée à la mère, et la fonction publique ne l'applique
    pas — elle a sa propre bonification, qui vaut un an par enfant né avant
    2004 et deux trimestres pour les enfants nés depuis. Un père de trois
    enfants recevait ainsi douze trimestres que la loi ne lui a jamais donnés,
    de quoi effacer une décote entière.

    Le fichier ``legislation/majoration_duree_assurance.csv`` porte ces règles
    et leurs dates ; le ``dispositif`` de chaque ligne reprend le code que la
    fiche de régime déclare dans ``avantages_non_contributifs``, de sorte que
    c'est la fiche qui dit quel régime accorde quoi, et la table combien.

    Deux horloges, et la distinction est dans les textes : la MDA se lit à
    l'ANNÉE DE LIQUIDATION, puisque c'est le droit en vigueur au départ qui la
    sert ; la bonification se lit à l'ANNÉE DE NAISSANCE DE L'ENFANT, que
    l'article désigne expressément.
    """

    #: Âge présumé de la mère à la naissance de ses enfants. Le modèle ne
    #: collecte pas leur date de naissance ; il la déduit de cette convention,
    #: qui est l'âge moyen des mères à l'accouchement (vingt-huit ans dans les
    #: années 1980, trente et un aujourd'hui — INSEE, état civil). Elle ne
    #: commande qu'une bascule, celle des quatre trimestres aux deux
    #: trimestres de la fonction publique, et c'est pourquoi les lignes qui en
    #: dépendent sont au niveau « moyenne ».
    AGE_PRESUME_A_LA_NAISSANCE = 30

    def __init__(self, racine: Path) -> None:
        self._table: list[
            tuple[str, str, int, int, int, int, int | None, int, str, Fiabilite]
        ] = []
        chemin = (racine / "reference" / "legislation"
                  / "majoration_duree_assurance.csv")
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                depuis = (ligne["services_depuis"] or "").strip()
                self._table.append((
                    ligne["dispositif"],
                    ligne["reference"],
                    int(ligne["debut"]),
                    int(ligne["fin"]),
                    int(ligne["trimestres_par_enfant"]),
                    int(ligne["services_par_enfant"]),
                    int(depuis) if depuis else None,
                    int(ligne["enfants_minimum"]),
                    ligne["beneficiaire"],
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                ))

    def par_enfant(self, dispositif: str, sexe: str, annee_naissance: int,
                   annee_liquidation: int,
                   nombre_enfants: int) -> tuple[int, int, Fiabilite] | None:
        """Trimestres accordés PAR ENFANT, dont ceux qui comptent en SERVICES.

        Rend ``(trimestres, services, fiabilite)``. Les premiers jouent sur la
        durée d'assurance, les seconds — qui en sont un sous-ensemble — sur le
        prorata du régime. Ils ne coïncident que là où le droit accorde une
        bonification ; une majoration de durée d'assurance rend ``services``
        nul, et c'est tout l'objet de cette distinction.

        ``None`` couvre les quatre cas où le droit ne donne rien : le
        dispositif n'existe pas encore à la date qui le commande, il n'a jamais
        existé dans ce régime, l'assuré n'en est pas le bénéficiaire, ou il n'a
        pas élevé le nombre d'enfants que la ligne exige — la loi Boulin
        demandait deux enfants là où les suivantes se contentent d'un.
        """
        for (code, reference, debut, fin, trimestres, services, services_depuis,
             enfants_minimum, beneficiaire, fiabilite) in self._table:
            if code != dispositif:
                continue
            annee = (annee_liquidation if reference == "liquidation"
                     else annee_naissance + self.AGE_PRESUME_A_LA_NAISSANCE)
            if not debut <= annee <= fin:
                continue
            if beneficiaire == "mere" and sexe != "F":
                return None
            if nombre_enfants < enfants_minimum:
                return None
            # La part qui compte en services peut n'entrer en vigueur qu'à une
            # SECONDE date, celle de la liquidation, quand la première est
            # celle de la naissance de l'enfant. C'est le cas du b ter de
            # L. 12, qui convertit un trimestre de majoration en bonification
            # pour les pensions prenant effet à compter de septembre 2026.
            if services_depuis is not None and annee_liquidation < services_depuis:
                services = 0
            return trimestres, services, fiabilite
        return None


class SurcoteParentale:
    """Surcote parentale — article L. 351-1-2-1 du code de la sécurité sociale.

    Le dernier avantage familial créé par le droit, et la contrepartie directe
    du recul de l'âge légal : un assuré qui avait sa durée requise à 63 ans
    s'est vu imposer par la loi du 14 avril 2023 une année de travail de plus
    qui ne lui rapportait rien, la surcote ordinaire ne récompensant que les
    trimestres accomplis APRÈS l'âge légal. La loi comble ce trou pour les
    seuls parents : 1,25 % par trimestre acquis entre 63 ans et l'âge légal,
    quatre trimestres au plus, à qui détient au moins un trimestre de
    majoration de durée d'assurance au titre des enfants.

    C'est ce trimestre-là qui ouvre le droit, et non le sexe : un père qui
    détient des trimestres pour enfants y a droit comme la mère.
    """

    def __init__(self, racine: Path) -> None:
        self._table: list[tuple[int, int, float, float, int, Fiabilite]] = []
        chemin = racine / "reference" / "legislation" / "surcote_parentale.csv"
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                self._table.append((
                    int(ligne["debut"]),
                    int(ligne["fin"]),
                    float(ligne["age_ouverture"]),
                    float(ligne["taux_par_trimestre"]),
                    int(ligne["trimestres_maximum"]),
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                ))

    def parametres(self, annee_liquidation: int
                   ) -> tuple[float, float, int, Fiabilite] | None:
        """Âge d'ouverture, taux par trimestre, plafond et fiabilité."""
        for debut, fin, age, taux, maximum, fiabilite in self._table:
            if debut <= annee_liquidation <= fin:
                return age, taux, maximum, fiabilite
        return None


#: Barèmes de décote lus dans une table, et non dans la fiche du régime : le
#: coefficient et l'âge d'annulation y montent en charge à l'année de
#: liquidation. ``regimes_speciaux_age_fixe`` prend le coefficient de la table
#: des régimes spéciaux mais garde l'âge d'annulation écrit dans la fiche.
_BAREMES_DECOTE_EN_TABLE = frozenset(
    {"fonction_publique", "regimes_speciaux", "regimes_speciaux_age_fixe"}
)


class DecoteFonctionPublique:
    """Barème de décote de l'article L. 14 du code des pensions.

    Deux paramètres, lus à l'ANNÉE OÙ LES CONDITIONS D'OUVERTURE DU DROIT SONT
    RÉUNIES — le millésime où l'assuré atteint l'âge d'ouverture, ou celui de
    la liquidation s'il part avant — parce que c'est ainsi que le III de
    l'article 66 de la loi du 21 août 2003 titre sa colonne : « Année au cours
    de laquelle sont réunies les conditions mentionnées au I et au II de
    l'article L. 24 ». Le modèle la lisait à l'année de liquidation, et c'est
    la confrontation à OpenFisca-France-Pension qui l'a fait voir : un
    sédentaire né en 1948, dont le droit s'ouvre en 2008, garde le barème de
    2008 — 0,375 % et limite d'âge moins douze trimestres — quelle que soit
    l'année où il part. La montée en charge est calendaire et non
    générationnelle, mais le calendrier est celui de l'ouverture du droit :

    * le **coefficient** de minoration par trimestre, d'un huitième de point
      par an de 0,125 % en 2006 à 1,25 % en 2015 ;
    * le nombre de **trimestres retranchés à la limite d'âge** pour obtenir
      l'âge d'annulation de la décote, de seize en 2006 à zéro en 2020.

    Rien avant 2006 : la décote n'existait pas dans la fonction publique.
    """

    #: Table lue par cette classe, dans ``data/reference/legislation/``.
    FICHIER = "decote_fonction_publique.csv"

    def __init__(self, racine: Path) -> None:
        self._table: dict[int, tuple[int, float, Fiabilite]] = {}
        chemin = racine / "reference" / "legislation" / self.FICHIER
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                self._table[int(ligne["annee"])] = (
                    int(ligne["trimestres_avant_limite"]),
                    float(ligne["coefficient"]),
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                )
        self._annees = sorted(self._table)

    def parametres(self, annee: int) -> tuple[int, float, Fiabilite] | None:
        """Barème en vigueur l'année demandée, ou ``None`` avant sa création."""
        if not self._table or annee < self._annees[0]:
            return None
        applicable = self._annees[0]
        for candidate in self._annees:
            if candidate > annee:
                break
            applicable = candidate
        return self._table[applicable]


class DecoteRegimesSpeciaux(DecoteFonctionPublique):
    """Barème de décote des régimes spéciaux, réforme de 2008.

    **Les régimes spéciaux n'ont pas décoté de 1,25 % dès 2009**, et le modèle
    le leur faisait faire. La réforme de 2008 leur donne la décote de la
    fonction publique AVEC QUATRE ANS DE RETARD : rien avant le 1er juillet
    2010, puis un dixième du taux plein, et un dixième de plus chaque
    1er juillet jusqu'à 1,25 % en 2019. Opposer 1,25 % à un cheminot parti en
    2011, c'est décoter dix fois trop — et, la décote étant plafonnée à vingt
    trimestres, lui retirer 25 % de sa pension là où le droit lui en retirait
    2,5 %.

    L'âge d'annulation suit le même retard : c'est l'âge de référence du régime
    — l'âge d'ouverture du droit majoré de cinq ans, non la limite d'âge du
    grade — diminué de seize trimestres en 2010, de rien à partir de 2024.

    La table et sa lecture au millésime sont documentées dans
    ``legislation/decote_regimes_speciaux.csv``.
    """

    FICHIER = "decote_regimes_speciaux.csv"


class MinimumVieillesse:
    """Allocation de solidarité aux personnes âgées (ASPA).

    Le dernier plancher du système actuel, et le seul qui ne suppose aucune
    cotisation : une allocation DIFFÉRENTIELLE qui porte les ressources au
    montant du barème. Ce n'est pas une pension — elle est soumise à condition
    d'âge, de ressources du foyer et de demande, et récupérable sur les
    successions —, d'où la ligne séparée dans la cascade et le paramètre qui
    permet de la retirer.
    """

    #: Âge d'ouverture de droit commun. L'âge légal suffit en cas d'inaptitude,
    #: que le modèle ne connaît pas.
    AGE_OUVERTURE = 65

    def __init__(self, racine: Path, macro: DonneesMacro) -> None:
        self.macro = macro
        self._table: dict[int, tuple[float, Fiabilite]] = {}
        chemin = racine / "reference" / "legislation" / "minimum_vieillesse.csv"
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                self._table[int(ligne["annee"])] = (
                    float(ligne["valeur"]),
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                )
        self._annees = sorted(self._table)

    def plafond(self, annee: int) -> tuple[float, Fiabilite] | None:
        """Montant maximal d'une personne seule, l'année demandée."""
        if not self._table:
            return None
        if annee in self._table:
            return self._table[annee]
        anterieures = [a for a in self._annees if a < annee]
        ancre = max(anterieures) if anterieures else self._annees[0]
        valeur, fiabilite = self._table[ancre]
        return valeur * self.macro.coefficient_prix(ancre, annee), fiabilite


class CarriereLongue:
    """Départ anticipé pour carrière longue — article L. 351-1-1.

    La principale porte d'entrée avant l'âge légal, et la seule qui se déduise
    de la carrière elle-même : la pénibilité, l'invalidité et l'inaptitude
    demandent des informations que le modèle n'a pas.

    **Les portes se lisent à la DATE D'EFFET de la pension, et par
    GÉNÉRATION.** Le décret du 2 juillet 2012 vaut pour les pensions prenant
    effet à compter du 1er novembre 2012, celui du 3 juin 2023 à compter du
    1er septembre 2023, celui du 7 mai 2026 à compter du 1er septembre 2026 :
    la table porte l'année décimale du premier mois d'application. Et depuis
    2023 la borne des vingt ans monte avec l'âge légal de la génération
    (D. 351-1-1, II) : soixante ans pour les nés d'avant septembre 1963, puis
    l'âge légal diminué de deux ans et six mois, jusqu'à soixante-deux ans.
    Le modèle lisait la règle générale seule et opposait soixante-deux ans à
    une génération 1965 à qui le droit ouvre soixante ans et neuf mois.
    """

    #: Premier mois du dernier trimestre civil : qui est né à compter de lui
    #: doit un trimestre de moins à la condition d'entrée précoce.
    MOIS_DERNIER_TRIMESTRE = 10

    #: Génération de la règle générale, celle qui vaut à défaut d'une ligne
    #: plus précise.
    GENERATION_GENERALE = 1900.0

    #: Depuis les pensions prenant effet au 1er septembre 2026, les majorations
    #: de durée d'assurance pour enfants — maternité, adoption, éducation, congé
    #: parental — et les bonifications de la fonction publique sont réputées
    #: cotisées pour la carrière longue, dans la limite de DEUX trimestres sur
    #: l'ensemble de la carrière : 3° de l'article L. 351-1-1 (article 104 de
    #: la loi n° 2025-1403 du 30 décembre 2025), article D. 351-1-2-1 créé par
    #: le décret n° 2026-700 du 29 juillet 2026 ; circulaire Cnav 2026-29 du
    #: 4 septembre 2026, point 1.2.3.8 et annexe 4. La majoration pour enfant
    #: handicapé, que le modèle ne sert pas, en est exclue.
    ENFANTS_REPUTES_COTISES_DEPUIS = DateMois(2026, 9)
    ENFANTS_REPUTES_COTISES_MAXIMUM = 2

    def __init__(self, racine: Path) -> None:
        self._table: dict[float, list[tuple[float, int, int, float, int, Fiabilite]]] = {}
        chemin = racine / "reference" / "legislation" / "carriere_longue.csv"
        if not chemin.exists():
            self._dates: list[float] = []
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                self._table.setdefault(float(ligne["date_effet"]), []).append((
                    float(ligne["generation"]),
                    int(ligne["age_debut_maximum"]),
                    int(ligne["trimestres_debut"]),
                    float(ligne["age_depart"]),
                    int(ligne["trimestres_supplementaires"]),
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                ))
        self._dates = sorted(self._table)

    @staticmethod
    def _annee_decimale(date: DateMois) -> float:
        return date.annee + (date.mois - 1) / 12.0

    def _portes(self, carriere: Carriere
                ) -> list[tuple[int, int, float, int, Fiabilite]] | None:
        """Les portes opposables à cette carrière : celles du texte en vigueur
        à sa date d'effet, et pour chaque porte — borne d'entrée ET supplément
        de trimestres — la ligne de la plus haute génération qui ne dépasse
        pas la sienne.

        Une borne d'entrée peut ouvrir DEUX portes : avant 2023, qui avait
        débuté avant seize ans partait à cinquante-six ans avec huit
        trimestres cotisés de plus que la durée requise, ou à cinquante-huit
        avec quatre. Retenir une ligne par borne d'entrée en perdait une, au
        hasard de l'ordre du fichier ; c'est le couple (borne, supplément)
        qui identifie une porte.
        """
        if not self._dates:
            return None
        effet = self._annee_decimale(carriere.date_liquidation)
        if effet < self._dates[0]:
            return None
        applicable = self._dates[0]
        for candidate in self._dates:
            if candidate > effet + 1e-9:
                break
            applicable = candidate
        generation = carriere.generation
        retenues: dict[tuple[int, int],
                       tuple[float, tuple[int, int, float, int, Fiabilite]]] = {}
        for gen, age_max, trimestres_debut, age_depart, supplement, fiabilite in \
                self._table[applicable]:
            if gen > generation + 1e-9:
                continue
            actuelle = retenues.get((age_max, supplement))
            if actuelle is None or gen > actuelle[0]:
                retenues[(age_max, supplement)] = (
                    gen, (age_max, trimestres_debut, age_depart, supplement, fiabilite)
                )
        return [porte for _, porte in sorted(retenues.values())]

    def _entree_precoce(self, carriere: Carriere, annee_liquidation: int,
                        age_max: int, trimestres_debut: int) -> bool:
        """La condition d'entrée précoce est-elle remplie pour cette porte ?

        Elle se lit sur les trimestres COTISÉS validés avant la fin de l'année
        civile des seize, dix-huit, vingt ou vingt et un ans. L'article
        D. 351-1-1 en demande cinq, **ou quatre à qui est né au cours du
        dernier trimestre de l'année civile** : né en novembre, on n'a pu
        travailler que deux mois de l'année de ses seize ans, et le texte en
        tient compte. Le modèle retenait cinq pour tout le monde tant qu'il ne
        connaissait que l'année de naissance ; il lit le mois depuis.
        """
        if carriere.mois_naissance >= self.MOIS_DERNIER_TRIMESTRE:
            trimestres_debut -= 1
        acquis = sum(
            ligne.trimestres_valides for ligne in carriere.lignes
            if ligne.cotise
            and ligne.annee <= carriere.annee_naissance + age_max
            and ligne.annee < annee_liquidation
        )
        return acquis >= trimestres_debut

    def cotises_reputes(self, carriere: Carriere, trimestres_cotises: int,
                        trimestres_enfants: int) -> int:
        """La durée cotisée que le dispositif oppose, périodes réputées comprises.

        Les trimestres réellement cotisés, plus deux listes fermées que le droit
        RÉPUTE cotisées. L'article D. 351-1-2 porte la première — service
        national, incapacité temporaire, chômage indemnisé, maternité,
        invalidité, assurance vieillesse des parents au foyer —, chacune sous sa
        propre limite, comptée sur toute la carrière ; c'est
        :meth:`_reputes_assimiles` qui la tient, sur la table des motifs. Et
        l'article D. 351-1-2-1 porte la seconde, pour les pensions prenant effet
        depuis le 1er septembre 2026 : jusqu'à deux trimestres de la majoration
        pour enfants.

        Le modèle ne comptait que les trimestres réellement cotisés, ce qui
        rendait la condition plus dure qu'elle ne l'est et déclarait non
        ouvertes des carrières hachées que le droit ouvre.
        """
        cotises = trimestres_cotises + self._reputes_assimiles(carriere)
        if trimestres_enfants <= 0 or carriere.age_liquidation is None:
            return cotises
        if carriere.date_liquidation.rang < self.ENFANTS_REPUTES_COTISES_DEPUIS.rang:
            return cotises
        return cotises + min(
            self.ENFANTS_REPUTES_COTISES_MAXIMUM, trimestres_enfants
        )

    @staticmethod
    def _reputes_assimiles(carriere: Carriere) -> int:
        """Ce que les périodes assimilées ajoutent à la durée cotisée.

        Chaque enveloppe de l'article D. 351-1-2 a son plafond, et deux motifs
        qui la partagent le partagent : maladie et accident du travail tiennent
        ensemble dans quatre trimestres, parce que le 2° vise l'incapacité
        temporaire et non l'une ou l'autre. Le budget se consomme dans l'ordre
        de la carrière, et une enveloppe sans plafond — la maternité — n'en
        consomme aucun.

        Le plafond annuel de quatre trimestres que l'article pose par ailleurs
        est tenu d'avance : une année ne porte ici qu'un statut, et
        :meth:`Carriere.trimestres_retenus` n'en rend jamais plus de quatre.
        """
        annee_liquidation = carriere.annee_liquidation
        budgets: dict[str, int] = {}
        reputes = 0
        for ligne in carriere.lignes:
            if ligne.cotise or not ligne.reputes_cotises_enveloppe:
                continue
            if ligne.annee > annee_liquidation:
                continue
            retenus = carriere.trimestres_retenus(ligne)
            if retenus <= 0:
                continue
            plafond = ligne.reputes_cotises_plafond
            if not plafond:
                reputes += retenus
                continue
            restant = budgets.setdefault(ligne.reputes_cotises_enveloppe, plafond)
            pris = min(retenus, restant)
            budgets[ligne.reputes_cotises_enveloppe] = restant - pris
            reputes += pris
        return reputes

    def age_de_depart(self, carriere: Carriere, annee_liquidation: int,
                      trimestres_cotises: int,
                      requis: int) -> tuple[float, Fiabilite] | None:
        """Âge le plus précoce ouvert par le dispositif, ou ``None``.

        La condition d'entrée précoce se lit sur les trimestres COTISÉS validés
        avant la fin de l'année civile des seize, dix-huit, vingt ou vingt et un
        ans. La condition de durée porte, elle aussi, sur les seuls trimestres
        cotisés — c'est ce qui distingue ce dispositif de la durée d'assurance
        qui commande la décote. ``trimestres_cotises`` est la durée que
        :meth:`cotises_reputes` a déjà complétée.
        """
        portes = self._portes(carriere)
        if portes is None:
            return None
        ouvertures = []
        for age_max, trimestres_debut, age_depart, supplement, fiabilite in portes:
            if not self._entree_precoce(
                    carriere, annee_liquidation, age_max, trimestres_debut):
                continue
            if trimestres_cotises < requis + supplement:
                continue
            ouvertures.append((age_depart, fiabilite))
        return min(ouvertures) if ouvertures else None

    def age_propose(self, carriere: Carriere, annee_liquidation: int,
                    trimestres_cotises: int, requis: int,
                    age_liquidation: float) -> float | None:
        """Âge le plus précoce que le dispositif ouvrirait à qui continue de
        cotiser jusqu'à son départ, ou ``None``.

        :meth:`age_de_depart` répond à une liquidation DATÉE : le droit
        ouvre-t-il ce départ-là ? Ici la question est celle qui date un cas
        type — à quel âge partir ? — et elle se pose avant que la carrière ne
        soit arrêtée. La condition d'entrée précoce se lit telle quelle, elle
        ne dépend que du début de la carrière. La condition de durée, elle, se
        projette : il manque ``requis + supplément − cotisés`` trimestres, et
        une année de cotisation en rend quatre, la soustraction étant signée.
        Chaque porte ouvre donc au plus tardif de son âge et de l'âge où la
        durée cotisée est réunie, et la plus précoce l'emporte.
        """
        portes = self._portes(carriere)
        if portes is None:
            return None
        candidats = []
        for age_max, trimestres_debut, age_depart, supplement, _ in portes:
            if not self._entree_precoce(
                    carriere, annee_liquidation, age_max, trimestres_debut):
                continue
            atteint = age_liquidation + (requis + supplement - trimestres_cotises) / 4.0
            candidats.append(max(age_depart, atteint))
        return min(candidats) if candidats else None


class SurcoteBaremes:
    """Barème DATÉ de la surcote — article D. 351-1-4 du code de la sécurité
    sociale, article L. 14 III du code des pensions.

    Chaque trimestre de surcote garde le taux en vigueur à la date où il a été
    ACCOMPLI : 0,75 % de 2004 à 2006 ; en 2007 et 2008, 0,75 % pour les
    quatre premiers trimestres, 1 % à compter du cinquième et 1,25 % pour les
    trimestres postérieurs au soixante-cinquième anniversaire ; 1,25 % pour
    tout trimestre accompli depuis le 1er janvier 2009. La fonction publique
    servait 0,75 % dans la limite de vingt trimestres jusqu'en 2008. Le
    modèle appliquait à tous les trimestres le taux de l'année du départ,
    ce qui servait 1,25 % à des trimestres de 2005 et 0,75 % à un cinquième
    trimestre de 2008. La circulaire Cnav 2018-04 (point 3) en donne trois
    exemples, que ``tests/temoins/exemples_officiels.yaml`` rejoue.
    """

    def __init__(self, racine: Path) -> None:
        self._lignes: list[tuple[str, float, float, int, bool, float,
                                 int | None, Fiabilite]] = []
        chemin = racine / "reference" / "legislation" / "surcote_baremes.csv"
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                self._lignes.append((
                    ligne["bareme"],
                    float(ligne["debut"]),
                    float(ligne["fin"]),
                    int(ligne["rang_minimum"]),
                    ligne["apres_65_ans"].strip() in ("1", "true", "oui"),
                    float(ligne["taux"]),
                    int(ligne["trimestres_maximum"]) if ligne["trimestres_maximum"].strip() else None,
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                ))

    def connait(self, bareme: str) -> bool:
        return any(ligne[0] == bareme for ligne in self._lignes)

    def coefficient(self, bareme: str,
                    trimestres: list[tuple[DateMois, bool]]) -> tuple[float, Fiabilite | None]:
        """Coefficient de majoration pour ces trimestres de surcote, datés.

        ``trimestres`` donne, dans l'ordre chronologique, le premier mois de
        chaque trimestre civil de surcote et s'il est postérieur au
        soixante-cinquième anniversaire. Pour chaque trimestre, la ligne la
        plus favorable qui lui convient l'emporte, sous le plafond de
        trimestres qu'elle porte le cas échéant.
        """
        servis: dict[int, int] = {}
        total = 0.0
        fiabilite: Fiabilite | None = None
        for rang, (date, apres_65) in enumerate(trimestres, start=1):
            valeur = date.annee + (date.mois - 1) / 12.0
            meilleure = None
            for indice, (code, debut, fin, rang_minimum, condition_65, taux,
                         maximum, fiab) in enumerate(self._lignes):
                if code != bareme or not debut - 1e-9 <= valeur <= fin + 1e-9:
                    continue
                if rang < rang_minimum or (condition_65 and not apres_65):
                    continue
                if maximum is not None and servis.get(indice, 0) >= maximum:
                    continue
                if meilleure is None or taux > meilleure[1]:
                    meilleure = (indice, taux, fiab)
            if meilleure is None:
                continue
            servis[meilleure[0]] = servis.get(meilleure[0], 0) + 1
            total += meilleure[1]
            fiabilite = (meilleure[2] if fiabilite is None
                         else min(fiabilite, meilleure[2]))
        return 1.0 + total, fiabilite


class MinimumGaranti:
    """Minimum garanti de la fonction publique — article L. 17 du code des
    pensions civiles et militaires de retraite.

    Le pendant, dans la fonction publique, du minimum contributif du privé. Il
    n'en a ni la forme ni la logique : ce n'est pas un plancher proratisé, mais
    un BARÈME EN ESCALIER sur la durée de services, rapporté à un traitement de
    référence gelé — celui de l'indice majoré 227 au 1er janvier 2004,
    revalorisé sur les prix depuis. Une durée de quinze ans en ouvre 57,5 %,
    trente ans 95 %, quarante ans la totalité.

    Le module ne le servait pas, alors que les fiches de régime le déclarent et
    que les Neutralisations annoncent le retirer dans les scénarios notionnels.
    On ne retire pas ce qui n'a jamais été mis : le fonctionnaire à carrière
    courte était servi sans plancher, et l'étalon sous-estimait le système
    actuel là même où il protège le plus.
    """

    #: Quinze ans de services, en trimestres : première marche du barème.
    SEUIL_BAS = 60
    #: Quarante ans de services : au-delà, la référence est servie en entier.
    SEUIL_HAUT = 160
    #: Année à partir de laquelle la référence est gelée puis indexée sur les
    #: prix, au lieu de suivre le point d'indice.
    ANNEE_GEL = 2004

    def __init__(self, racine: Path, macro: DonneesMacro) -> None:
        self.macro = macro
        self._bareme: dict[int, tuple[int, float, float, float, int, Fiabilite]] = {}
        self._point: dict[int, tuple[float, Fiabilite]] = {}
        self._montants: dict[int, tuple[float, Fiabilite]] = {}
        dossier = racine / "reference" / "legislation"
        chemin = dossier / "minimum_garanti.csv"
        if chemin.exists():
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    self._bareme[int(ligne["annee"])] = (
                        int(ligne["indice_majore"]),
                        float(ligne["part_15_ans"]),
                        float(ligne["points_15_30"]),
                        float(ligne["points_30_40"]),
                        int(ligne["trimestres_seuil"]),
                        Fiabilite.depuis_texte(ligne["fiabilite"]),
                    )
        for fichier, table in (("point_indice_fonction_publique.csv", self._point),
                               ("minimum_garanti_montants.csv", self._montants)):
            chemin = dossier / fichier
            if not chemin.exists():
                continue
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    table[int(ligne["annee"])] = (
                        float(ligne["valeur"]),
                        Fiabilite.depuis_texte(ligne["fiabilite"]),
                    )
        self._annees_bareme = sorted(self._bareme)
        self._annees_montants = sorted(self._montants)

    def ratio_point_indice(self, depart: int, arrivee: int) -> float | None:
        """Ce que devient un traitement indiciaire entre deux années.

        Un fonctionnaire garde son indice : son traitement suit le point, et
        c'est le point qui dit ce que vaut, l'année du départ, le traitement
        perçu l'année d'avant. ``None`` quand la série ne couvre pas les deux
        années, et le modèle retombe alors sur les prix.
        """
        de, a = self._point_indice(depart), self._point_indice(arrivee)
        if de is None or a is None or de[0] <= 0:
            return None
        return a[0] / de[0]

    def _point_indice(self, annee: int) -> tuple[float, Fiabilite] | None:
        """Traitement annuel d'un point d'indice majoré, l'année demandée."""
        if not self._point:
            return None
        anterieures = [a for a in self._point if a <= annee]
        return self._point[max(anterieures)] if anterieures else None

    #: Indice majoré auquel se rapportent les montants transcrits.
    INDICE_REFERENCE = 227

    def reference(self, annee_liquidation: int) -> tuple[float, Fiabilite] | None:
        """Montant plein du minimum garanti, quarante ans de services.

        Trois cas, et dans cet ordre :

        * **un montant servi est connu** pour l'année — il prime sur tout
          calcul, comme pour le minimum contributif, et pour la même raison :
          la revalorisation des pensions à laquelle l'article renvoie a été
          gelée en 2014 et sous-indexée depuis, si bien qu'une projection sur
          les prix dépasse de plusieurs points ce qui a été payé ;
        * **après 2004**, la référence est le traitement gelé de l'indice
          majoré 227 au 1er janvier 2004, projeté sur les prix depuis l'ancre
          en vigueur ;
        * **avant 2004**, le gel n'existe pas : c'est le traitement de l'indice
          majoré de l'année, au point d'indice de cette année-là.

        Le montant est ensuite ramené à l'indice majoré de l'année de
        liquidation, qui monte de 217 en 2004 à 227 en 2013.
        """
        bareme = self.bareme(annee_liquidation)
        if bareme is None:
            return None
        indice, _, _, _, _, fiabilite_bareme = bareme

        if annee_liquidation <= self.ANNEE_GEL and annee_liquidation not in self._montants:
            point = self._point_indice(annee_liquidation)
            if point is None:
                return None
            return indice * point[0], min(fiabilite_bareme, point[1])

        if not self._annees_montants:
            return None
        if annee_liquidation in self._montants:
            valeur, fiabilite = self._montants[annee_liquidation]
        else:
            anterieures = [a for a in self._annees_montants if a < annee_liquidation]
            ancre = max(anterieures) if anterieures else self._annees_montants[0]
            valeur, fiabilite = self._montants[ancre]
            valeur *= self.macro.coefficient_prix(ancre, annee_liquidation)
        return (valeur * indice / self.INDICE_REFERENCE,
                min(fiabilite_bareme, fiabilite))

    def bareme(self, annee_liquidation: int):
        """Paramètres en vigueur l'année de liquidation, ou ``None`` avant 1976."""
        if not self._bareme or annee_liquidation < self._annees_bareme[0]:
            return None
        applicable = self._annees_bareme[0]
        for candidate in self._annees_bareme:
            if candidate > annee_liquidation:
                break
            applicable = candidate
        return self._bareme[applicable]

    def montant(self, annee_liquidation: int,
                trimestres_services: int) -> tuple[float, Fiabilite] | None:
        """Plancher opposable pour une durée de services donnée."""
        bareme = self.bareme(annee_liquidation)
        reference = self.reference(annee_liquidation)
        if bareme is None or reference is None:
            return None
        _, part, points_bas, points_haut, seuil, _ = bareme
        duree = max(0, min(trimestres_services, self.SEUIL_HAUT))
        if duree <= 0:
            return None
        if duree < self.SEUIL_BAS:
            taux = part * duree / self.SEUIL_BAS
        elif duree >= self.SEUIL_HAUT:
            taux = 1.0
        elif duree < seuil:
            taux = part + (duree - self.SEUIL_BAS) * points_bas
        else:
            taux = (part + (seuil - self.SEUIL_BAS) * points_bas
                    + (duree - seuil) * points_haut)
        return reference[0] * taux, reference[1]


@dataclass(frozen=True)
class ConversionPoint:
    """Ce que devient un point à une fusion, ou à un changement d'unité."""

    annee_effet: int
    #: Régime qui reprend les points, ou ``None`` pour un changement d'échelle
    #: interne au régime lui-même.
    successeur: str | None
    #: Un point d'origine vaut ce nombre de points d'arrivée.
    coefficient: float
    fiabilite: Fiabilite


class ConversionsPoints:
    """Coefficients de conversion des points, lus et non devinés.

    Un point n'est pas une grandeur universelle : c'est l'unité de compte d'un
    régime, et elle change quand le régime change. Le moteur déduisait ces
    coefficients du RAPPORT de deux valeurs de service prises aux bornes des
    séries publiées, ce qui a produit deux erreurs distinctes.

    La première tenait à la date : la valeur du successeur était lue à sa
    PREMIÈRE année publiée. Or les séries ``arrco`` et ``ircantec`` sont
    rétro-remplies bien avant leur fusion — la première depuis 1957 avec les
    valeurs de l'UNIRS, la seconde depuis 1949 avec celles de l'IPACTE. Le
    rapport comparait alors deux valeurs distantes de quarante ou soixante-dix
    ans : le point UNIRS ressortait quinze fois trop cher pour toute
    liquidation postérieure à 1998, le point IPACTE cinquante fois trop cher
    au-delà de 2022, et jusqu'à 35 % de la pension du scénario 1 n'avait aucune
    existence.

    La seconde tenait au jour : la valeur du successeur était prise au
    31 décembre de l'année de fusion quand la conversion s'opère au 1er
    janvier — un pour cent d'écart sur tous les points d'avant 2019.

    Une troisième erreur n'était pas une conversion mal faite mais une
    conversion ABSENTE : l'unification de l'Arrco au 1er janvier 1999 change
    l'unité sans changer le code du régime. C'est ce que décrivent les lignes
    dont le ``successeur`` est vide.
    """

    def __init__(self, racine: Path) -> None:
        self._fusions: dict[tuple[str, str], ConversionPoint] = {}
        self._echelles: dict[str, list[ConversionPoint]] = {}
        chemin = racine / "reference" / "regimes" / "conversions_points.csv"
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                conversion = ConversionPoint(
                    annee_effet=int(ligne["annee_effet"]),
                    successeur=ligne["successeur"] or None,
                    coefficient=float(ligne["coefficient"]),
                    fiabilite=Fiabilite.depuis_texte(ligne["fiabilite"]),
                )
                if conversion.successeur is not None:
                    self._fusions[(ligne["regime"], conversion.successeur)] = conversion
                else:
                    self._echelles.setdefault(ligne["regime"], []).append(conversion)
        for conversions in self._echelles.values():
            conversions.sort(key=lambda c: c.annee_effet)

    def fusion(self, regime: str, successeur: str) -> ConversionPoint | None:
        """Coefficient de reprise des points de ``regime`` par ``successeur``."""
        return self._fusions.get((regime, successeur))

    def echelle(self, regime: str, annee_acquisition: int,
                annee_liquidation: int) -> tuple[float, Fiabilite]:
        """Facteur d'unité entre l'année d'acquisition et celle de liquidation.

        Un point acheté au prix de 1998 et servi à la valeur de 2029 n'est pas
        la même unité : l'Arrco a changé d'échelle entre-temps. Le facteur
        n'intervient que si le changement tombe APRÈS l'acquisition et AVANT ou
        À la liquidation — une liquidation de 1995 lit une valeur de service de
        l'ancienne échelle, et n'a rien à convertir.
        """
        facteur = 1.0
        fiabilite = Fiabilite.CERTIFIEE
        for conversion in self._echelles.get(regime, ()):
            if annee_acquisition < conversion.annee_effet <= annee_liquidation:
                facteur *= conversion.coefficient
                fiabilite = min(fiabilite, conversion.fiabilite)
        return facteur, fiabilite


class ValeursPoint:
    """Prix d'achat et valeur de service du point, régime par régime et année.

    Trois grandeurs suffisent à reconstituer exactement une pension en points :

    * le **salaire de référence**, prix d'achat du point l'année de la cotisation ;
    * le **taux d'appel**, qui dit quelle part de la cotisation ouvre des droits —
      depuis 1995, cotiser 125 € n'en acquiert que 100 ;
    * la **valeur de service**, qui convertit les points en rente à la liquidation.

    Les régimes que ce fichier ne couvre pas retombent sur le rendement
    instantané de :class:`Rendements`, qui reste l'approximation d'origine, tout
    comme les années postérieures au dernier barème publié. Ceux dont la caisse
    publie un barème EN POINTS plutôt qu'un prix d'achat — le régime de base des
    libéraux, la complémentaire agricole — n'en ont pas besoin : leur fiche
    porte ``points_maximum``, et seule la valeur de service est lue ici.
    """

    def __init__(self, racine: Path) -> None:
        self._table: dict[tuple[str, str], dict[int, tuple[float, Fiabilite]]] = {}
        chemin = racine / "reference" / "regimes" / "valeurs_point.csv"
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                cle = (ligne["regime"], ligne["mesure"])
                self._table.setdefault(cle, {})[int(ligne["annee"])] = (
                    float(ligne["valeur"]),
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                )

    def _en_vigueur(self, regime: str, mesure: str,
                    annee: int) -> tuple[float, Fiabilite] | None:
        """Dernière valeur publiée à l'année demandée, ou avant elle.

        Une valeur reste en vigueur jusqu'à sa modification : c'est la règle de
        lecture d'un barème, et la seule qui ait un sens ici. Rien n'est renvoyé
        pour les années antérieures à la première publication.
        """
        valeurs = self._table.get((regime, mesure))
        if not valeurs:
            return None
        anterieures = [a for a in valeurs if a <= annee]
        return valeurs[max(anterieures)] if anterieures else None

    def achat(self, regime: str, annee: int) -> tuple[float, float, Fiabilite] | None:
        """Prix d'achat effectif d'un point : (salaire de référence, taux d'appel).

        Rien n'est renvoyé au-delà de la dernière année publiée. Prolonger le
        dernier prix connu reviendrait à supposer un barème gelé : les points
        seraient achetés trop bon marché et la pension surestimée. Ces années
        retombent sur le rendement instantané, qui, lui, s'assume approximatif.
        """
        derniere = self._table.get((regime, "salaire_reference"))
        if not derniere or annee > max(derniere):
            return None
        reference = self._en_vigueur(regime, "salaire_reference", annee)
        if reference is None or reference[0] <= 0:
            return None
        appel = self._en_vigueur(regime, "taux_appel", annee)
        taux, fiabilite_appel = appel if appel else (1.0, Fiabilite.MOYENNE)
        return reference[0], taux, min(reference[1], fiabilite_appel)

    def derniere_annee_servie(self, regime: str) -> int | None:
        valeurs = self._table.get((regime, "valeur_service"))
        return max(valeurs) if valeurs else None

    def premiere_annee_servie(self, regime: str) -> int | None:
        valeurs = self._table.get((regime, "valeur_service"))
        return min(valeurs) if valeurs else None

    def service(self, regime: str, annee: int) -> tuple[float, Fiabilite] | None:
        return self._en_vigueur(regime, "valeur_service", annee)


class ScenarioActuel:
    """Calcule la pension servie par le système en vigueur."""

    def __init__(self, macro: DonneesMacro, catalogue: CatalogueRegimes,
                 affiliations: Affiliations, parametres: Parametres) -> None:
        self.macro = macro
        self.catalogue = catalogue
        self.affiliations = affiliations
        self.parametres = parametres
        self.rendements = Rendements(parametres.racine_donnees)
        self.valeurs_point = ValeursPoint(parametres.racine_donnees)
        self.conversions_points = ConversionsPoints(parametres.racine_donnees)
        self.classes = ClassesCotisation(parametres.racine_donnees)
        self.grilles = SalairesForfaitaires(parametres.racine_donnees)
        self.durees_requises = DureesRequises(parametres.racine_donnees)
        self.durees_requises_regimes = DureesRequisesRegimes(parametres.racine_donnees)
        self.durees_proratisation = DureesProratisation(parametres.racine_donnees)
        self.ages_ouverture = AgesOuverture(parametres.racine_donnees)
        self.ages_annulation_decote = AgesAnnulationDecote(parametres.racine_donnees)
        self.ages_categorie_active = AgesCategorieActive(parametres.racine_donnees)
        self.durees_services_militaires = DureesServicesMilitaires(
            parametres.racine_donnees
        )
        self.ages_jouissance_militaire = AgesJouissanceMilitaire(
            parametres.racine_donnees
        )
        self.coefficients_minoration = CoefficientsMinoration(parametres.racine_donnees)
        self.annees_salaire_reference = AnneesSalaireReference(parametres.racine_donnees)
        self.majorations_enfants = MajorationsPourEnfants(parametres.racine_donnees)
        self.surcote_parentale = SurcoteParentale(parametres.racine_donnees)
        self.durees_requises_fonction_publique = DureesRequisesFonctionPublique(
            parametres.racine_donnees
        )
        self.decote_fonction_publique = DecoteFonctionPublique(
            parametres.racine_donnees
        )
        self.decote_regimes_speciaux = DecoteRegimesSpeciaux(
            parametres.racine_donnees
        )
        self.minimum_contributif = MinimumContributif(parametres.racine_donnees, macro)
        self.minimum_garanti = MinimumGaranti(parametres.racine_donnees, macro)
        self.carriere_longue = CarriereLongue(parametres.racine_donnees)
        self.surcote_baremes = SurcoteBaremes(parametres.racine_donnees)
        self.minimum_vieillesse = MinimumVieillesse(parametres.racine_donnees, macro)

    # -- valorisation des points ---------------------------------------------

    def valeur_du_point(self, code: str,
                        annee_liquidation: int) -> tuple[float, Fiabilite] | None:
        """Ce que vaut, à la liquidation, un point acquis dans ``code``.

        Un régime fermé ne sert plus ses points : ils ont été convertis dans son
        successeur, au coefficient que l'accord de fusion a fixé. La méthode
        remonte la chaîne des successions (UNIRS -> Arrco -> Agirc-Arrco,
        Agirc -> Agirc-Arrco, IPACTE et IGRANTE -> Ircantec) en cumulant ces
        coefficients, qui sont LUS dans ``regimes/conversions_points.csv`` et
        non plus déduits d'un rapport de valeurs de service.

        **Les déduire coûtait cher.** Le rapport était pris entre la dernière
        valeur publiée du régime d'origine et la PREMIÈRE du successeur ; or les
        séries ``arrco`` et ``ircantec`` sont rétro-remplies bien avant leur
        fusion, si bien qu'on comparait deux valeurs distantes de quarante ou
        soixante-dix ans. Le point UNIRS ressortait quinze fois trop cher pour
        toute liquidation postérieure à 1998, le point IPACTE cinquante fois
        trop cher au-delà de 2022. Et là même où les deux bornes tombaient
        juste, la valeur du successeur était celle du 31 décembre quand la
        conversion s'opère au 1er janvier : un pour cent de trop peu sur tous
        les points d'avant 2019.

        Quand la chaîne s'arrête — plus de successeur, ou aucun coefficient
        déclaré — la dernière valeur publiée est ramenée en euros de la
        liquidation par l'indice des prix. C'est une approximation, signalée
        comme telle par la fiabilité renvoyée ; c'est surtout un aveu
        d'ignorance, préférable à un coefficient inventé.
        """
        conversion = 1.0
        courant = code
        fiabilite = Fiabilite.CERTIFIEE
        for _ in range(len(self.catalogue) + 1):  # garde-fou : jamais de boucle
            derniere = self.valeurs_point.derniere_annee_servie(courant)
            if derniere is None:
                return None
            if annee_liquidation <= derniere:
                valeur = self.valeurs_point.service(courant, annee_liquidation)
                if valeur is None:
                    # Liquidation antérieure au premier barème publié. Symétrique
                    # du cas ci-dessous : la première valeur connue est ramenée
                    # en euros de la liquidation par l'indice des prix, et la
                    # fiabilité tombe pour le dire.
                    premiere_connue = self.valeurs_point.premiere_annee_servie(courant)
                    ancienne = self.valeurs_point.service(courant, premiere_connue)
                    return (
                        conversion * ancienne[0]
                        * self.macro.coefficient_prix(premiere_connue, annee_liquidation),
                        min(fiabilite, ancienne[1], Fiabilite.MOYENNE),
                    )
                return conversion * valeur[0], min(fiabilite, valeur[1])

            successeur = (self.catalogue[courant].integre_dans
                          if courant in self.catalogue else None)
            reprise = (self.conversions_points.fusion(courant, successeur)
                       if successeur else None)
            if reprise is None:
                ancienne = self.valeurs_point.service(courant, derniere)
                return (
                    conversion * ancienne[0]
                    * self.macro.coefficient_prix(derniere, annee_liquidation),
                    min(fiabilite, ancienne[1], Fiabilite.MOYENNE),
                )

            conversion *= reprise.coefficient
            fiabilite = min(fiabilite, reprise.fiabilite)
            courant = successeur
        return None  # pragma: no cover - chaîne de successions cyclique

    # -- salaire de référence ------------------------------------------------

    def _assiette_de_reference(self, periode: PeriodeRegime, ligne) -> float:
        """La rémunération que ce régime liquide : voir la fonction du même
        nom, et, pour un régime à grille, le salaire forfaitaire de la
        catégorie — le marin liquide « sur le salaire forfaitaire de la
        catégorie dans laquelle il a été classé » (R. 11), non sur sa paie.
        Le forfait est proratisé sur les mois de l'année, comme le revenu.
        """
        if periode.assiette_grille:
            forfait_grille = self.grilles.forfait(
                periode.assiette_grille, ligne.annee, ligne.revenu_annualise,
                lambda a: salaire_moyen_annuel(self.macro, a),
            )
            if forfait_grille is not None:
                return forfait_grille[0] * ligne.fraction_annee
        return _assiette_de_reference(periode, ligne)

    #: Pensions à compter desquelles le salaire annuel moyen des parents porte
    #: sur vingt-quatre ou vingt-trois années au lieu de vingt-cinq.
    PARENTS_MEILLEURES_ANNEES_DEPUIS = DateMois(2026, 9)

    def salaire_de_reference(self, code: str, carriere: Carriere,
                             periode: PeriodeRegime,
                             annee_liquidation: int, plafonner: bool,
                             generation: int | None = None,
                             avpf: bool = True,
                             membres: tuple[str, ...] | None = None,
                             enfants_majores: int = 0) -> float:
        """Salaire de référence, exprimé en euros de l'année de liquidation.

        **Il porte sur les seules années passées DANS CE régime** — ou dans
        l'un des ``membres`` de sa chaîne de succession, quand ``code`` liquide
        pour un régime qu'il a absorbé : les années CANCAVA d'un artisan sont
        des années du RSI, puis du régime général, et n'entrent qu'une fois
        dans un seul salaire annuel moyen. Voir :meth:`_groupes_de_succession`.

        Un régime ne
        liquide que ce qui lui a été déclaré : la pension civile se calcule sur
        le traitement des six derniers mois de service, pas sur le dernier
        salaire d'une carrière poursuivie ailleurs, et le salaire annuel moyen
        du régime général ne retient que les salaires portés à son compte. Sans
        cette condition, un polypensionné passé de la fonction publique au privé
        liquidait sa pension civile sur son salaire privé de fin de carrière —
        et le prorata de durée, lui, restait celui du régime : le modèle
        rapportait une part de carrière publique à une assiette qui ne l'était
        pas.

        Trois autres règles de droit commandent ce calcul, et le modèle les
        applique toutes.

        La première est la **revalorisation des salaires portés au compte** :
        les salaires anciens sont réévalués par les coefficients annuels que
        fixe l'arrêté, et le modèle les LIT au lieu de les reconstituer. Il les
        approchait par « les salaires jusqu'en 1986, les prix depuis », ce qui
        décrit les arrêtés dans les grandes lignes mais ignore leurs
        revalorisations semestrielles, leurs gels, leurs revalorisations
        exceptionnelles et leurs changements de DÉLAI d'application : cette
        approximation sur-revalorisait les salaires anciens de 12 % sur
        quarante ans. La grandeur commande le salaire de référence deux fois
        plutôt qu'une, puisque la moyenne porte sur les N MEILLEURES années et
        que « meilleures » se juge sur des salaires revalorisés.

        La seconde est le **nombre d'années retenues**, que la loi du 22 juillet
        1993 fait passer de dix à vingt-cinq à raison d'une par génération. Le
        lire à l'année de liquidation opposait vingt-cinq années à des assurés
        auxquels la loi n'en a jamais demandé plus de dix — et étendre la
        moyenne aux années les plus faibles ne peut que l'abaisser.

        Le salaire retenu est celui de l'assiette du régime, et pas la
        rémunération entière : la pension civile porte sur le seul traitement
        indiciaire, primes exclues. C'est le paramètre qui commande le taux de
        remplacement d'un fonctionnaire, puisque les primes n'ouvrent de droit
        qu'au RAFP.
        """
        avpf_ouvert = (
            avpf and "avpf" in periode.avantages_non_contributifs
        )
        # Les coefficients des arrêtés ne valent que pour un salaire PORTÉ AU
        # COMPTE. Un régime qui liquide sur le dernier traitement ne porte rien
        # à un compte : lui appliquer les coefficients du régime général serait
        # une erreur de catégorie. Le traitement d'un FONCTIONNAIRE suit le
        # point d'indice — l'agent garde son indice, et c'est le point de
        # l'année du départ qui dit ce que vaut son traitement de l'année
        # d'avant — ; les autres régimes à dernier salaire restent sur les
        # prix, avec la réserve que `docs/limites.md` leur attache.
        porte_au_compte = periode.salaire_reference not in (
            "derniers_6_mois", "dernier_salaire"
        )
        suit_le_point = (
            not porte_au_compte
            and self.catalogue[code].famille == "fonction_publique"
        )
        # Le MOIS de la liquidation désigne la circulaire applicable : les
        # arrêtés ne prennent pas tous effet au 1er janvier, et deux d'entre
        # eux portent l'année 2022. Le mois ne vaut que si l'année passée est
        # bien celle de la liquidation — certains appels bornent l'année à la
        # dernière que porte la fiche du régime.
        mois_liquidation = (
            carriere.mois_liquidation
            if (carriere.age_liquidation is not None
                and annee_liquidation == carriere.annee_liquidation)
            else 1
        )

        def revaloriser(perception: int, arrivee: int) -> float:
            if not porte_au_compte:
                if suit_le_point:
                    ratio = self.minimum_garanti.ratio_point_indice(perception, arrivee)
                    if ratio is not None:
                        return ratio
                return self.macro.coefficient_revalorisation_salaires(
                    perception, arrivee
                )
            return self.macro.coefficient_revalorisation_portee_au_compte(
                perception, arrivee, mois_liquidation
            )
        codes_admis = frozenset(membres) if membres else frozenset((code,))
        revenus: list[float] = []
        for ligne in carriere.lignes:
            if ligne.annee >= annee_liquidation:
                continue
            if codes_admis.isdisjoint(self.affiliations.regimes(
                    ligne.affiliation, ligne.annee,
                    carriere.date_entree(ligne.affiliation),
                    revenu=ligne.revenu if ligne.cotise else ligne.revenu_reference,
                    plafond=self.macro.plafond_securite_sociale(ligne.annee))):
                continue
            if not ligne.cotise:
                # Assurance vieillesse des parents au foyer : la CNAF cotise
                # sur une assiette forfaitaire égale au SMIC, et ce salaire est
                # PORTÉ AU COMPTE. C'est ce qui la distingue d'une période
                # assimilée, laquelle valide des trimestres sans jamais ajouter
                # de salaire — et c'est ce que le modèle ne faisait pas, alors
                # que le cas type « carrière interrompue » l'annonçait.
                if not (avpf_ouvert and ligne.revenu_avpf > 0):
                    continue
                revenu = ligne.revenu_avpf
            else:
                revenu = self._assiette_de_reference(periode, ligne)
            # TRANCHE DE SALAIRE. Un régime qui liquide TRANCHE PAR TRANCHE —
            # le personnel navigant, dont l'article R. 426-16-1 attribue
            # 1,85 % par annuité à la première et 1,4 % à la seconde — a
            # besoin que son salaire de référence soit celui de SA tranche, et
            # non le salaire entier. Sans quoi les deux périodes simultanées
            # calculeraient le même salaire moyen et la seconde paierait une
            # deuxième fois sur la première.
            #
            # Le découpage ne s'applique qu'aux assiettes dont la borne basse
            # n'est pas nulle : `plafonnee`, `tranche_1` et `tranche_a` partent
            # de zéro et continuent de passer par `plafonner` ci-dessous,
            # exactement comme avant. Aucun régime en annuités du catalogue
            # n'utilisait de tranche à borne basse avant celui-ci : ce bloc ne
            # déplace donc aucun chiffre existant.
            borne_basse, borne_haute = periode.bornes_assiette_en_euros(
                self.macro.plafond_securite_sociale(ligne.annee)
                * ligne.fraction_annee
            )
            if borne_basse > 0:
                revenu = max(0.0, min(revenu, borne_haute or revenu) - borne_basse)
            if plafonner:
                # Le plafond se proratise sur les mois travaillés : l'année
                # d'entrée dans la vie active n'est pas pleine, et un plafond
                # de douze mois y laisserait passer un salaire qu'il aurait
                # écrêté.
                revenu = min(
                    revenu,
                    self.macro.plafond_securite_sociale(ligne.annee)
                    * ligne.fraction_annee,
                )
            revenus.append(revenu * revaloriser(ligne.annee, annee_liquidation))

        if not revenus:
            return 0.0

        reference = periode.salaire_reference
        if reference in ("25_meilleures_annees", "10_meilleures_annees"):
            annees = 25 if reference == "25_meilleures_annees" else 10
            if periode.salaire_reference_par_generation and generation is not None:
                par_generation = self.annees_salaire_reference.annees(generation)
                if par_generation is not None:
                    annees = par_generation[0]
                # LES PARENTS : vingt-quatre années pour qui bénéficie d'une
                # majoration ou d'une bonification au titre d'un enfant,
                # vingt-trois pour deux enfants et plus, pour les pensions
                # prenant effet à compter du 1er septembre 2026 (article
                # R. 173-3-2, décret n° 2026-699 du 29 juillet 2026, pris pour
                # l'article 103 de la loi de financement pour 2026). La moyenne
                # porte sur moins d'années, donc sur de meilleures : c'est la
                # mesure « mères de famille » de cette loi, et elle vaut à qui
                # détient les trimestres, la mère par défaut dans ce modèle.
                if (enfants_majores > 0 and carriere.age_liquidation is not None
                        and carriere.date_liquidation.rang
                        >= self.PARENTS_MEILLEURES_ANNEES_DEPUIS.rang):
                    annees = max(1, annees - (1 if enfants_majores == 1 else 2))
            retenus = sorted(revenus, reverse=True)[:annees]
        elif reference in ("derniers_6_mois", "dernier_salaire"):
            # Le traitement des six derniers mois est celui EN VIGUEUR au
            # départ. L'année de la liquidation est incomplète — l'assuré n'y a
            # travaillé que quelques mois —, mais c'est bien son traitement que
            # liquide le régime : on l'annualise plutôt que de reculer d'un an.
            derniere = carriere.ligne(annee_liquidation)
            if (derniere is not None and derniere.cotise
                    and derniere.fraction_annee > 0
                    and not codes_admis.isdisjoint(self.affiliations.regimes(
                        derniere.affiliation, annee_liquidation,
                        carriere.date_entree(derniere.affiliation),
                        revenu=derniere.revenu,
                        plafond=self.macro.plafond_securite_sociale(annee_liquidation)))):
                traitement = (self._assiette_de_reference(periode, derniere)
                              / derniere.fraction_annee)
                if plafonner:
                    traitement = min(
                        traitement,
                        self.macro.plafond_securite_sociale(annee_liquidation),
                    )
                return traitement
            return revenus[-1]
        elif reference == "carriere_entiere":
            retenus = revenus
        else:
            retenus = revenus
        return sum(retenus) / len(retenus)

    def _duree_requise(self, periode: PeriodeRegime,
                       carriere: Carriere) -> tuple[int, Fiabilite | None]:
        """Durée requise opposable à cet assuré dans ce régime.

        La fonction publique a sa propre montée en charge, 2004-2008, lue à
        l'année d'ouverture du droit ; elle passe avant la table par
        génération, qui ne vaut pour elle qu'à compter de 2009.

        ET UN EMPLOI CLASSÉ N'A PAS LA DURÉE DE SA GÉNÉRATION. Le XXIV, B de
        l'article 10 de la loi du 14 avril 2023 pour l'État, et le II, B de
        l'article 13 du décret n° 2023-435 pour la CNRACL et le FSPOEIE, fixent
        « par dérogation à l'article L. 13 » une durée propre aux catégories
        active et super-active — 169 trimestres des nés de septembre 1966 à
        1967, 172 dès 1971, et les mêmes marches cinq ans plus tard pour la
        super-active. Le modèle leur opposait celle des sédentaires, soit
        jusqu'à trois trimestres de trop.
        """
        requis = periode.duree_requise_trimestres or 160
        if periode.bareme_decote == "fonction_publique":
            transitoire = self.durees_requises_fonction_publique.trimestres(
                self._annee_ouverture_des_droits(
                    periode, carriere,
                    carriere.annee_liquidation
                    if carriere.age_liquidation is not None else 9999,
                )
            )
            if transitoire is not None:
                return transitoire
        derogation = self._derogation_active(periode, carriere)
        if derogation is not None and derogation.duree_requise is not None:
            return derogation.duree_requise, derogation.fiabilite
        if periode.duree_requise_par_generation:
            par_generation = self.durees_requises.trimestres(carriere.generation)
            if par_generation is not None:
                return par_generation
        return requis, None

    def _duree_proratisation(self, periode: PeriodeRegime, carriere: Carriere,
                             requis: int) -> tuple[int, Fiabilite | None]:
        """Dénominateur du coefficient de proratisation, dans ce régime.

        Il vaut la durée requise partout, sauf pour les générations 1944 à 1948
        et celles qui les précèdent, auxquelles l'article R. 351-6 oppose une
        durée maximale plus courte — 150 trimestres avant 1944, puis 152, 154,
        156, 158 et 160. La table ne répond que là ; ailleurs, c'est la durée
        requise qui fait office, comme le droit le veut depuis 1949.

        **La table est celle du code de la sécurité sociale**, et la fiche dit
        qui la suit : le régime général et les régimes alignés. La fonction
        publique et les régimes spéciaux ont la leur, calendaire et non
        générationnelle (article L. 13 du code des pensions) ; elle n'est pas
        modélisée, et leur durée requise continue d'y faire office. Leur
        appliquer la table du privé remplacerait une approximation par une
        autre, sans que rien ne l'établisse.

        Et la durée de proratisation ne dépasse jamais la durée requise : les
        périodes anciennes, dont la durée maximale est plus courte que
        150 trimestres — 120 sous les ordonnances de 1945 —, gardent la leur.
        """
        if not periode.duree_proratisation_par_generation:
            return requis, None
        par_generation = self.durees_proratisation.trimestres(carriere.generation)
        if par_generation is None:
            return requis, None
        return min(par_generation[0], requis), par_generation[1]

    def _tete_de_succession(self, code: str, annee_liquidation: int) -> str:
        """Le régime au bout de la chaîne d'absorption de ``code``, tant que
        la chaîne reste en annuités : ``cancava`` et ``rsi`` rendent
        ``regime_general``, ``pensions_civiles_1853`` rend
        ``fonction_publique_etat``. Un régime en points au bout de la chaîne
        l'arrête — les annuités des régimes professionnels intégrés ne se
        fondent pas dans les points de l'Agirc-Arrco —, et un régime en points
        n'y entre jamais : ses points se convertissent et s'additionnent déjà
        (voir :meth:`valeur_du_point`).

        L'absorption ne se suit qu'à partir de l'année où le régime FERME à
        ses affiliés — celle où l'absorbant commence à recevoir leurs années.
        Avant, ce sont deux régimes distincts, et un polypensionné en a deux :
        un salarié devenu artisan qui liquide en 2010 a une pension du régime
        général et une du RSI, comme le droit d'alors ; s'il liquide en 2020,
        le RSI est le régime général, et il n'en a qu'une.
        """
        vu = {code}
        courant = code
        while True:
            regime = self.catalogue[courant]
            suivant = regime.integre_dans
            borne = (regime.fermeture if regime.fermeture is not None
                     else regime.extinction)
            if (suivant is None or borne is None or annee_liquidation < borne
                    or suivant not in self.catalogue or suivant in vu):
                return courant
            absorbant = self.catalogue[suivant]
            periode = absorbant.periode(
                min(annee_liquidation, _derniere_annee(absorbant))
            )
            if periode is None or periode.type_calcul != "annuites":
                return courant
            vu.add(suivant)
            courant = suivant

    #: Les trois régimes que la liquidation unique des régimes alignés réunit
    #: — le régime général, les salariés agricoles et la sécurité sociale des
    #: indépendants, sous ses trois noms successifs. Les exploitants agricoles
    #: n'en sont pas : la LURA ne vise que les SALARIÉS agricoles.
    REGIMES_ALIGNES = frozenset({
        "regime_general", "msa_salaries", "cancava", "organic", "rsi",
    })
    #: La LURA ne vaut que pour les assurés nés à compter de 1953 (article 51
    #: de la loi n° 2015-1702 de financement pour 2016) et pour les pensions
    #: prenant effet à compter du 1er juillet 2017 (article 4 du décret
    #: n° 2017-737 du 3 mai 2017).
    LURA_PREMIERE_GENERATION = 1953
    LURA_DATE_EFFET = DateMois(2017, 7)
    #: La clé sous laquelle les régimes alignés se réunissent quand la LURA
    #: s'applique : ce n'est pas un régime, c'est un groupe.
    REGIMES_ALIGNES_TETE = "regimes_alignes"

    def _lura_applicable(self, carriere: Carriere) -> bool:
        """La liquidation unique vaut-elle pour cette carrière ?

        Deux conditions, et le modèle les porte toutes les deux : la
        génération, et la date d'effet au mois près. Une troisième reste hors
        du modèle — la LURA ne s'applique pas à qui avait déjà obtenu, avant
        le 1er juillet 2017, une retraite de même nature dans l'un des trois
        régimes —, parce qu'une carrière du dépôt liquide tout à la fois.
        """
        return (carriere.generation >= self.LURA_PREMIERE_GENERATION
                and carriere.date_liquidation.rang >= self.LURA_DATE_EFFET.rang)

    def _groupes_de_succession(
            self, codes: list[str], annee_liquidation: int,
            derniere_annee_par_regime: dict[str, int],
            carriere: Carriere | None = None,
    ) -> dict[str, tuple[str, ...]]:
        """Les régimes d'annuités que la carrière a traversés, groupés par
        chaîne de succession : pour chaque code d'un groupe d'au moins deux,
        les membres du groupe, LE PREMIER ÉTANT CELUI QUI LIQUIDE.

        **Un régime et celui qui lui succède ne sont pas deux régimes.** La
        CANCAVA, le RSI et le régime général sont trois NOMS du même droit
        pour un artisan : sa caisse calcule un seul salaire annuel moyen sur
        toute la carrière et un seul coefficient de proratisation, et le
        catalogue le sait, puisqu'il porte ``succede_a`` et ``integre_dans``.
        Liquider chaque nom sur ses seules années — ce que le modèle faisait,
        et qui est juste d'un polypensionné passé d'un régime à un AUTRE —
        calculait deux salaires de référence là où la caisse n'en calcule
        qu'un : un artisan payé 60 000 € de 1976 à 2015 recevait
        « 30 077 € × 120/165 » plus « 36 778 € × 40/165 » au lieu de
        « 34 152 € × 160/165 ». Mesuré contre l'oracle du régime général,
        l'écart allait de −7,2 % à +0,3 %, dans les deux sens, les meilleures
        années de chaque morceau pouvant être meilleures que celles de la
        carrière entière.

        Le groupe est liquidé par le membre de la DERNIÈRE période active de
        la carrière — à égalité, par l'absorbant —, dont la fiche donne les
        règles : c'est la caisse qui aurait le dossier, et c'est aussi ce que
        la LURA prescrit (« le montant de la retraite unique est déterminé en
        fonction des règles applicables au régime liquidateur »). Un assuré
        qui n'a connu qu'un seul nom n'est pas touché.

        **ET LES RÉGIMES ALIGNÉS DISTINCTS SE RÉUNISSENT AUSSI, DEPUIS 2017.**
        La liquidation unique des régimes alignés (`L. 173-1-2` CSS) donne une
        seule retraite à qui a cotisé à deux des trois régimes alignés : un
        revenu annuel moyen formé de la somme des salaires et revenus d'une
        même année, écrêtée au plafond, sur les vingt-cinq meilleures années,
        et une proratisation qui tient compte de tous les trimestres des trois
        régimes (`R. 173-4-4-1`, 1° et 4°, circulaire Cnav 2017/27). Le modèle
        y arrivait déjà pour le couple régime général / indépendants, mais par
        la chaîne d'absorption, qui ne ferme le RSI qu'en 2018 : une carrière
        liquidée entre juillet 2017 et l'absorption était coupée en deux. Et
        il ne le faisait pas du tout pour les salariés agricoles, dont le
        régime existe toujours — « SR 41 499 € × 88/167 » plus
        « SR 29 069 € × 80/167 » là où la caisse calcule un seul salaire de
        référence. Les deux conditions de la loi sont opposées :
        :meth:`_lura_applicable`.
        """
        par_tete: dict[str, list[str]] = {}
        lura = carriere is not None and self._lura_applicable(carriere)
        for code in codes:
            regime = self.catalogue[code]
            periode = regime.periode(min(annee_liquidation, _derniere_annee(regime)))
            if periode is None or periode.type_calcul != "annuites":
                continue
            tete = (self.REGIMES_ALIGNES_TETE if lura and code in self.REGIMES_ALIGNES
                    else self._tete_de_succession(code, annee_liquidation))
            par_tete.setdefault(tete, []).append(code)
        groupes: dict[str, tuple[str, ...]] = {}
        for membres in par_tete.values():
            if len(membres) < 2:
                continue
            rang = {code: i for i, code in enumerate(self._chaine_depuis(membres))}
            liquidateur = max(
                membres,
                key=lambda code: (derniere_annee_par_regime.get(code, 0), rang[code]),
            )
            ordonnes = (liquidateur,) + tuple(
                code for code in sorted(membres, key=rang.get) if code != liquidateur
            )
            for code in membres:
                groupes[code] = ordonnes
        return groupes

    def _chaine_depuis(self, membres: list[str]) -> list[str]:
        """Les membres dans l'ordre de la chaîne, du plus ancien à l'absorbant."""
        restants = set(membres)
        ordre: list[str] = []
        for depart in sorted(membres):
            courant = depart
            chaine = []
            while courant in restants and courant not in ordre:
                chaine.append(courant)
                courant = self.catalogue[courant].integre_dans
            if len(chaine) > len(ordre):
                ordre = chaine
        return ordre + sorted(restants - set(ordre))

    # -- catégorie active et pension militaire -------------------------------

    def _statut_dominant(self, carriere: Carriere,
                         classements: dict[str, str]) -> str | None:
        """Le classement que la carrière a exercé le plus longtemps.

        La règle est celle du code : quand plusieurs emplois classés se
        succèdent, « la catégorie applicable pour bénéficier de l'âge de départ
        minoré est celle associée à l'emploi que le fonctionnaire a occupé le
        plus longtemps » (L. 24, I, 1°). À égalité, le classement le plus
        favorable — la super-active — l'emporte, parce que la durée qu'elle
        exige est la plus longue : l'assuré qui la remplit remplit l'autre.
        """
        durees: dict[str, float] = {}
        borne = self._borne_carriere(carriere)
        for statut, classement in classements.items():
            duree = carriere.duree_de_service((statut,), borne)
            if duree > 0:
                durees[classement] = durees.get(classement, 0.0) + duree
        if not durees:
            return None
        return max(durees, key=lambda cle: (durees[cle], cle == "super_active",
                                            cle == "officier"))

    def _derogation_active(self, periode: PeriodeRegime,
                           carriere: Carriere) -> DerogationActive | None:
        """L'âge anticipé que le classement de l'emploi ouvre, ou ``None``.

        Quatre conditions, et la fiche en porte une : le régime doit servir la
        catégorie active — l'avoir dans ses ``avantages_non_contributifs`` ; le
        statut déclaré doit être classé ; le régime doit être l'un de ceux que
        ce statut route, sans quoi la dérogation déborderait sur un régime
        spécial que la même carrière traverserait (cf. :meth:`_regimes_routes`) ;
        et la carrière doit porter la durée de services classés que l'article
        L. 24 exige — dix-sept ans, vingt-sept pour la super-active. Sans cette
        dernière, l'assuré reste au droit commun, ce qui est exactement ce que
        le texte dit : la faculté « est ouverte à la condition que le
        fonctionnaire puisse se prévaloir, au total, d'au moins dix-sept ans de
        services accomplis […] dits services actifs ».
        """
        if "categorie_active" not in periode.avantages_non_contributifs:
            return None
        classements = self.affiliations.classements_actifs
        if not classements:
            return None
        classement = self._statut_dominant(carriere, classements)
        if classement is None:
            return None
        derogation = self.ages_categorie_active.derogation(
            classement, carriere.generation
        )
        if derogation is None:
            return None
        statuts = [code for code, valeur in classements.items()
                   if valeur == classement]
        if periode.regime not in self._regimes_routes(statuts):
            return None
        servies = carriere.duree_de_service(statuts, self._borne_carriere(carriere))
        if servies + 1e-9 < derogation.services_requis:
            return None
        return derogation

    def _droit_militaire(self, periode: PeriodeRegime,
                         carriere: Carriere) -> "_DroitMilitaire | None":
        """Ce que la pension militaire oppose à cet assuré, ou ``None``.

        Elle ne s'ouvre pas à un âge mais à une DURÉE — dix-sept ans de services
        effectifs pour un non-officier, vingt-sept pour un officier (L. 24, II).
        Qui la réunit liquide aussitôt, à trente-cinq ans s'il s'est engagé à
        dix-huit ; qui ne la réunit pas mais a quinze ans de services attend
        l'âge de jouissance différée de l'article L. 25 ; qui a moins de quinze
        ans n'a pas de pension militaire, et c'est l'âge légal qui vaut.

        La durée opposée dépend de l'ANNÉE où l'ancienne durée — quinze ou
        vingt-cinq ans — a été atteinte, et non de la génération : c'est la clé
        que le décret n° 2011-2103 a choisie.
        """
        if "categorie_active" not in periode.avantages_non_contributifs:
            return None
        categories = self.affiliations.categories_militaires
        if not categories:
            return None
        categorie = self._statut_dominant(carriere, categories)
        if categorie is None:
            return None
        statuts = [code for code, valeur in categories.items()
                   if valeur == categorie]
        if periode.regime not in self._regimes_routes(statuts):
            return None
        base = self.durees_services_militaires.duree_de_base(categorie)
        if base is None:
            return None
        date_base = carriere.date_de_service(statuts, base)
        annee_base = (9999.0 if date_base is None
                      else date_base.annee + (date_base.mois - 1) / 12)
        requises = self.durees_services_militaires.annees_requises(
            categorie, annee_base
        )
        if requises is None:
            return None
        annees_requises, fiabilite = requises
        servies = carriere.duree_de_service(statuts, self._borne_carriere(carriere))
        age_requis = carriere.age_de_service(statuts, annees_requises)
        if servies + 1e-9 >= annees_requises and age_requis is not None:
            age_ouverture, differee = age_requis, False
        elif servies + 1e-9 >= SERVICES_MINIMAUX_MILITAIRES:
            par_generation = self.ages_jouissance_militaire.age(carriere.generation)
            if par_generation is None:
                return None
            age_ouverture, differee = par_generation[0], True
            fiabilite = min(fiabilite, par_generation[1])
        else:
            return None
        return _DroitMilitaire(
            age_ouverture=age_ouverture,
            trimestres_servis=round(servies * 4),
            trimestres_cible=round(annees_requises * 4) + TRIMESTRES_DECOTE_MILITAIRE,
            jouissance_differee=differee,
            fiabilite=fiabilite,
        )

    def _regimes_routes(self, statuts: list[str]) -> frozenset[str]:
        """Les régimes que ces statuts atteignent, une année au moins.

        C'est la seconde garde du droit dérogatoire, et elle n'est pas de
        confort. Plusieurs régimes SPÉCIAUX servent eux aussi une catégorie
        active — leur fiche le déclare, et c'est exact : la SNCF a ses agents
        de conduite. Mais la catégorie active de la fonction publique n'a rien
        à y voir : sans cette garde, un assuré ayant fait vingt ans d'emploi
        classé après une carrière à la SNCF aurait vu son régime SNCF liquidé à
        l'âge de la fonction publique, et décoté sur la limite d'âge d'un grade
        qu'il n'a jamais eu.
        """
        return frozenset(
            code
            for statut in statuts
            for periode in self.affiliations.periodes(statut)
            for code in (periode.get("regimes") or ())
        )

    @staticmethod
    def _borne_carriere(carriere: Carriere) -> int | None:
        """Dernière année à compter dans les services, ``None`` si sans objet."""
        return (carriere.annee_liquidation
                if carriere.age_liquidation is not None else None)

    def _age_ouverture(self, periode: PeriodeRegime, carriere: Carriere) -> float:
        """Âge légal opposable à cet assuré dans ce régime.

        Trois droits se superposent, du plus particulier au plus général : la
        pension militaire, qui s'ouvre à une durée de services ; la catégorie
        active, qui avance l'âge de cinq ou de dix années ; le droit commun,
        lu à la génération ou dans la fiche.
        """
        militaire = self._droit_militaire(periode, carriere)
        if militaire is not None:
            return militaire.age_ouverture
        derogation = self._derogation_active(periode, carriere)
        if derogation is not None:
            return derogation.age_ouverture
        commun = self._age_ouverture_commun(periode, carriere)
        speciale = self._ouverture_pension_speciale(periode, carriere)
        if speciale is not None:
            return speciale
        par_services = self._ouverture_par_services(periode, carriere)
        if par_services is not None and par_services < commun:
            return par_services
        return commun

    def _services_dans_le_regime(self, periode: PeriodeRegime,
                                 carriere: Carriere) -> tuple[list[str], float]:
        """Les statuts que le régime route, et les années servies dans ceux-ci
        jusqu'à la liquidation."""
        statuts = [code for code in self.affiliations.codes
                   if periode.regime in self._regimes_routes([code])]
        return statuts, carriere.duree_de_service(
            statuts, self._borne_carriere(carriere))

    def _ouverture_pension_speciale(self, periode: PeriodeRegime,
                                    carriere: Carriere) -> float | None:
        """L'âge de la pension SPÉCIALE des marins, ou ``None`` si l'assuré a
        les quinze ans de services qui ouvrent une autre pension.

        Moins de quinze ans de services n'ouvrent ni la pension d'ancienneté
        ni la proportionnelle, mais une pension spéciale (L. 5552-11 du code
        des transports), dont « la concession et l'entrée en jouissance […]
        interviennent au moment de l'entrée en jouissance de la pension de
        retraite servie par l'Etat ou un régime légal de sécurité sociale,
        sous réserve que l'intéressé ait atteint » cinquante-cinq ans, et à
        défaut d'une telle pension à soixante ans (L. 5552-12 ; R. 5 du code
        des pensions de retraite des marins).

        Le modèle liquide tous les régimes à la même date : la pension
        spéciale suit donc le plus précoce des AUTRES régimes de base que la
        carrière traverse, jamais avant l'âge de la fiche ; sans autre régime
        de base, c'est l'âge de la fiche sans autre pension. La page de l'ENIM
        écrit « l'âge légal […] du régime général » dans son texte et
        « 60 ans » dans son exemple : c'est R. 5 qui fait foi.
        """
        seuil = periode.pension_speciale_services_annees
        isole = periode.pension_speciale_age_sans_autre_pension
        if seuil is None or isole is None:
            return None
        _, servies = self._services_dans_le_regime(periode, carriere)
        if servies + 1e-9 >= seuil:
            return None
        annuites, autres = self._periodes_parcourues(carriere)
        bases = [p for code, p in annuites + self._periodes_opposant_une_duree(autres)
                 if code != periode.regime]
        if not bases:
            return isole
        return max(periode.age_ouverture,
                   min(self._age_ouverture(p, carriere) for p in bases))

    def _ouverture_par_services(self, periode: PeriodeRegime,
                                carriere: Carriere) -> float | None:
        """L'âge que la durée de services dans le régime ouvre, ou ``None``.

        Les marins acquièrent la pension d'ancienneté « lorsque se trouve
        remplie la double condition de cinquante ans d'âge et de vingt-cinq
        années de services » (R. 2 de leur code). Les cinquante-cinq ans que
        le même article fixe ensuite ne sont que la borne de l'entrée en
        jouissance de celui qui CONTINUE à naviguer (L. 5552-5 du code des
        transports) : qui cesse à cinquante ans avec vingt-cinq ans de mer
        liquide, et l'ENIM l'écrit — « Gaspard, marin, a 50 ans et réunit
        25 ans de services […] Il peut prétendre au versement d'une pension
        d'ancienneté ». Le plafond de vingt-cinq annuités de R. 13 n'avait
        pas d'autre objet que ce départ-là.

        Les services sont ceux des statuts que le régime route, comptés
        jusqu'à la liquidation ; l'âge est le plus tardif de l'âge écrit et de
        celui où la durée est atteinte.
        """
        if (periode.age_ouverture_services is None
                or periode.services_ouverture_annees is None):
            return None
        statuts, servies = self._services_dans_le_regime(periode, carriere)
        requis = periode.services_ouverture_annees
        if servies + 1e-9 < requis:
            return None
        atteint = carriere.age_de_service(statuts, requis)
        if atteint is None:
            return None
        return max(periode.age_ouverture_services, atteint)

    def _age_ouverture_commun(self, periode: PeriodeRegime,
                              carriere: Carriere) -> float:
        """L'âge légal de droit commun, sans égard au classement de l'emploi.

        C'est lui, et non l'âge anticipé, qui commande la SURCOTE : le III de
        l'article L. 14 ne la donne qu'« au-delà de l'âge mentionné à l'article
        L. 161-17-2 », et le D du XXIV de l'article 10 de la loi du 14 avril
        2023 le confirme pour les emplois classés — l'âge anticipé majoré de
        cinq années, l'âge minoré majoré de dix, c'est-à-dire l'âge légal dans
        les deux cas. Compter la surcote depuis cinquante-sept ans aurait payé
        deux fois l'avantage du classement.
        """
        if periode.age_ouverture_par_generation:
            par_generation = self.ages_ouverture.age(carriere.generation)
            if par_generation is not None:
                return par_generation[0]
        return periode.age_ouverture

    def _periodes_parcourues(
            self, carriere: Carriere
    ) -> tuple[list[tuple[str, PeriodeRegime]], list[tuple[str, PeriodeRegime]]]:
        """Les régimes que cette carrière traverse, séparés en deux paquets.

        Le premier est celui des régimes en ANNUITÉS, qui commandent le taux
        plein et l'ouverture du droit ; le second recueille les autres. C'est
        la même énumération que celle de :meth:`calculer`, mais tirée de la
        seule carrière : elle répond donc AVANT que la pension ne soit
        calculée, ce qu'il faut pour dater un départ. Chaque entrée porte le
        code du régime avec sa période, parce que la majoration pour enfants
        se demande à un régime nommé.
        """
        annee_liquidation = carriere.annee_liquidation
        codes: set[str] = set()
        for ligne in carriere.lignes:
            if ligne.annee > annee_liquidation:
                continue
            codes.update(self.affiliations.regimes(
                ligne.affiliation, ligne.annee,
                carriere.date_entree(ligne.affiliation),
                revenu=ligne.revenu if ligne.cotise else ligne.revenu_reference,
                plafond=self.macro.plafond_securite_sociale(ligne.annee),
            ))
        annuites: list[tuple[str, PeriodeRegime]] = []
        autres: list[tuple[str, PeriodeRegime]] = []
        for code in sorted(codes):
            if code not in self.catalogue:
                continue
            regime = self.catalogue[code]
            periode = regime.periode(min(annee_liquidation, _derniere_annee(regime)))
            if periode is None:
                continue
            (annuites if periode.type_calcul == "annuites" else autres).append(
                (code, periode)
            )
        return annuites, autres

    def age_ouverture_droit(self, carriere: Carriere) -> float | None:
        """L'âge auquel le droit OUVRE la liquidation de cette carrière.

        C'est la même question que celle posée dans :meth:`calculer` — le plus
        précoce des régimes de base parcourus, chacun lisant l'âge que sa
        génération lui oppose —, mais posée AVANT la pension et sans la
        calculer. Elle a un usage propre : dater le départ d'un cas type. Une
        grille qui fait partir toutes les générations au même âge fait partir
        celle de 1940 à un âge que la loi de 2023 lui opposera soixante ans
        plus tard ; c'est par cette méthode-ci qu'elle cesse de le faire.

        Ce sont les régimes en ANNUITÉS qui commandent, comme dans la
        liquidation. Quand la carrière n'en a aucun — le libéral, dont le
        régime de base est en points —, les autres répondent : sans cela la
        question resterait sans réponse pour lui seul, et il serait le seul à
        garder un âge écrit à la main.

        ``None`` quand aucun régime connu n'est parcouru, ce qui arrive avant
        que le premier ne soit créé. L'appelant décide alors : il n'y a pas
        d'âge à proposer, et non un âge de zéro.
        """
        annuites, autres = self._periodes_parcourues(carriere)
        retenues = annuites or autres
        if not retenues:
            return None
        ouverture = min(self._age_ouverture(periode, carriere)
                        for _, periode in retenues)
        anticipe = self._age_carriere_longue(
            carriere, annuites or self._periodes_opposant_une_duree(autres))
        if anticipe is not None and anticipe < ouverture:
            return anticipe
        return ouverture

    def _age_carriere_longue(self, carriere: Carriere,
                             periodes: list[tuple[str, PeriodeRegime]]
                             ) -> float | None:
        """L'âge que le départ anticipé pour carrière longue proposerait à
        cette carrière, ou ``None`` s'il ne lui ouvre rien.

        C'est la seule porte avant l'âge légal qui se déduise de la carrière
        elle-même, et :meth:`calculer` la connaissait déjà — mais comme une
        dérogation qu'on lui demande à un âge donné, pas comme un âge qu'il
        propose. Un salarié entré à dix-huit ans et né en 1965 partait donc, en
        cas type, à soixante-trois ans et trois mois, quand le droit lui ouvre
        soixante-deux ans au taux plein : la grille faisait attendre l'âge
        légal à ceux-là mêmes que la loi en dispense. La durée requise et les
        trimestres cotisés sont ceux que :meth:`calculer` oppose au même
        départ.

        ``periodes`` sont celles qui OPPOSENT une durée, et non les seules
        périodes en annuités : **les deux régimes de base en points ouvrent la
        carrière longue**, et le lire ailleurs serait une lecture de travers.
        L'article L. 732-18-1 du code rural la donne aux non-salariés agricoles
        — « l'âge prévu à l'article L. 732-18 est abaissé pour les personnes
        ayant exercé une activité non salariée agricole qui ont commencé leur
        activité avant un des quatre âges, dont le plus élevé ne peut excéder
        vingt et un ans » —, et le II de l'article L. 643-3 du code de la
        sécurité sociale la donne aux professions libérales par renvoi à
        L. 351-1-1, « les références au régime général […] étant remplacées par
        celles au régime d'assurance vieillesse de base des professions
        libérales ».

        Les deux règles d'âge doivent la lire sur la MÊME liste. Ne l'ouvrir
        qu'au taux plein faisait rendre à celui-ci un âge antérieur à celui que
        :meth:`age_ouverture_droit` accordait — soixante-trois ans contre
        soixante-quatre pour un chef d'exploitation né en 2000 —, c'est-à-dire
        deux règles du même droit qui se contredisent.
        """
        if not periodes:
            return None
        requis = max(self._duree_requise(periode, carriere)[0]
                     for _, periode in periodes) or 160
        annee_liquidation = carriere.annee_liquidation
        cotises = sum(
            carriere.trimestres_retenus(ligne) for ligne in carriere.lignes
            if ligne.cotise and ligne.annee <= annee_liquidation
        )
        majoration = self._majoration_pour_enfants(
            carriere, {code: cotises for code, _ in periodes}, annee_liquidation
        )
        cotises = self.carriere_longue.cotises_reputes(
            carriere, cotises, majoration.trimestres if majoration is not None else 0
        )
        return self.carriere_longue.age_propose(
            carriere, annee_liquidation, cotises, requis, carriere.age_liquidation
        )

    def age_taux_plein_droit(self, carriere: Carriere) -> float | None:
        """L'âge auquel cette carrière obtient le TAUX PLEIN, et non seulement
        le droit de partir.

        Les deux âges ne se confondent pas, et l'écart entre eux est l'un des
        ressorts du système : la loi ouvre le droit à soixante-quatre ans, mais
        elle ne le sert entier qu'à qui a la durée requise — cent soixante-douze
        trimestres pour les générations d'après 1964. Un cadre entré à
        vingt-trois ans ne les a pas à soixante-quatre : partir là serait partir
        avec une décote de huit trimestres, ce que personne ne fait. Les cas
        types partent donc au taux plein, comme ceux du Conseil d'orientation
        des retraites.

        Trois termes, et le plus tardif des deux premiers l'emporte, sous le
        plafond du troisième :

        * l'âge d'ouverture, qui n'ouvre rien avant lui ;
        * l'âge auquel la DURÉE requise est atteinte. Il se déduit sans
          simuler : il manque à cette carrière ``requis - acquis`` trimestres,
          et une année pleine en rend quatre. La soustraction est signée — une
          carrière qui a déjà trop de trimestres l'avait donc atteinte plus
          tôt, et la règle le lit dans le même calcul ;
        * l'âge d'annulation de la décote, qui donne le taux plein sans
          condition de durée. C'est lui qui borne : au-delà, attendre ne
          rapporte plus de taux, et les cas types ne surcotent pas.

        La durée acquise compte les trimestres que le droit accorde au titre
        des enfants — majoration de durée d'assurance du régime général,
        bonification de la fonction publique —, lus au régime qui les porte
        comme :meth:`calculer` le fait. Sans eux, une mère de deux enfants
        était datée trois ans après l'âge où sa pension est entière, et partait
        en surcote quand le droit la servait déjà en entier.

        Et le départ anticipé pour carrière longue passe avant les trois
        termes : il n'ouvre qu'à qui a sa durée COTISÉE, donc au taux plein.

        ``None`` dans le même cas que :meth:`age_ouverture_droit`.
        """
        annuites, autres = self._periodes_parcourues(carriere)
        retenues = annuites or autres
        if not retenues:
            return None
        ouverture = min(self._age_ouverture(periode, carriere)
                        for _, periode in retenues)
        opposent = annuites or self._periodes_opposant_une_duree(autres)
        if not opposent:
            return ouverture
        annulation = min(self._age_taux_plein(periode, carriere)
                         for _, periode in retenues)
        requis = max(self._duree_requise(periode, carriere)[0]
                     for _, periode in opposent)
        if not requis:
            return ouverture
        annee_liquidation = carriere.annee_liquidation
        acquis = sum(
            carriere.trimestres_retenus(ligne) for ligne in carriere.lignes
            if ligne.annee <= annee_liquidation
        )
        majoration = self._majoration_pour_enfants(
            carriere, {code: acquis for code, _ in opposent}, annee_liquidation
        )
        if majoration is not None:
            acquis += majoration.trimestres
        duree = carriere.age_liquidation + (requis - acquis) / 4.0
        taux_plein = min(annulation, max(ouverture, duree))
        anticipe = self._age_carriere_longue(carriere, opposent)
        if anticipe is not None and anticipe < taux_plein:
            return anticipe
        return taux_plein

    @staticmethod
    def _periodes_opposant_une_duree(
            periodes: list[tuple[str, PeriodeRegime]],
    ) -> list[tuple[str, PeriodeRegime]]:
        """Parmi des périodes NON annuitaires, celles qui opposent une durée.

        Une carrière entière en points n'a aucune période en annuités, et la
        règle du taux plein rendait alors l'âge d'OUVERTURE — c'est-à-dire
        qu'elle faisait liquider au premier âge permis, sans regarder la durée.
        La pension, elle, était bien abattue : ``_abattement_points`` lit la
        décote de la fiche. Le modèle faisait donc partir au taux plein des
        carrières que le même modèle servait minorées. Le libéral né en 1955
        partait à soixante-quatre ans avec cent quarante-huit trimestres sur
        cent soixante-six requis, soit dix-huit trimestres de réduction que la
        règle disait inexistants.

        Le droit oppose bien cette durée aux régimes en points : l'article
        L. 643-3 du code de la sécurité sociale la pose pour les professions
        libérales — « lorsque l'intéressé a accompli la durée d'assurance fixée
        en application du deuxième alinéa de l'article L. 351-1 dans le présent
        régime et dans un ou plusieurs autres régimes », sinon « coefficients de
        réduction […] en fonction de l'âge […] et de la durée d'assurance » —,
        et le II de l'article L. 732-24 du code rural pour les non-salariés
        agricoles.

        Deux familles sont écartées, et c'est le sens de cette fonction.
        L'Agirc-Arrco et l'Ircantec n'opposent PAS la durée du régime de base :
        elles ont leurs propres coefficients d'anticipation, en deux tables
        dont ``_abattement_points`` retient la plus avantageuse. Elles ne sont
        de toute façon jamais seules — ce sont des complémentaires, et la
        carrière qui les porte a des périodes en annuités.
        """
        return [(code, periode) for code, periode in periodes
                if periode.abattement_points not in ("agirc_arrco", "ircantec")]

    def _age_taux_plein(self, periode: PeriodeRegime, carriere: Carriere) -> float:
        """Âge d'annulation de la décote opposable à cet assuré.

        Pour un emploi classé, ce n'est pas soixante-sept ans mais la limite
        d'âge du grade — soixante-deux ans en catégorie active, cinquante-sept
        en super-active — puis, depuis la réforme de 2023, l'âge que l'article
        L. 14 bis attache au classement. Le barème de la fonction publique en
        retranche ensuite les trimestres de sa propre montée en charge.
        """
        derogation = self._derogation_active(periode, carriere)
        if derogation is not None:
            return derogation.age_annulation
        if periode.age_taux_plein_par_generation:
            par_generation = self.ages_annulation_decote.age(carriere.generation)
            if par_generation is not None:
                return par_generation[0]
        return periode.age_taux_plein

    def _decote(self, periode: PeriodeRegime, carriere: Carriere,
                annee_liquidation: int
                ) -> tuple[float | None, float, Fiabilite | None]:
        """Décote opposable : coefficient, âge d'annulation, fiabilité.

        Un régime sans décote — fonction publique avant 2006, régimes spéciaux
        avant 2008 — n'en acquiert pas une parce que la table en porte une :
        ``None`` dans la fiche reste ``None`` ici, et le coefficient renvoyé
        est ``None``.

        **Les barèmes en table se lisent à l'année d'ouverture du droit, pas à
        celle de la liquidation.** Le III de l'article 66 de la loi du 21 août
        2003 titre sa colonne « Année au cours de laquelle sont réunies les
        conditions mentionnées au I et au II de l'article L. 24 », et les
        décrets de 2008 des régimes spéciaux visent « les personnes remplissant
        les conditions définies à l'article 6 » entre deux dates. Un
        fonctionnaire dont le droit s'ouvre en 2008 garde donc 0,375 % et
        « limite d'âge moins douze trimestres » quelle que soit l'année de son
        départ ; qui part avant l'âge d'ouverture réunit les conditions à la
        liquidation, et c'est ce millésime-là qui vaut. Le modèle lisait le
        barème à l'année de liquidation, et c'est la confrontation à
        OpenFisca-France-Pension qui l'a fait voir : deux trimestres de décote
        de trop pour un sédentaire né en 1948 parti à soixante-deux ans.

        **La fonction publique n'a pas la décote du régime général.** L'article
        L. 14 du code des pensions lui donne la sienne, montée en charge de
        2006 à 2020, et surtout un âge d'annulation qui n'est pas un âge en
        propre : c'est la LIMITE D'ÂGE du grade, diminuée d'un nombre de
        trimestres décroissant. Un sédentaire liquidant en 2012 voyait sa
        décote s'annuler à 63 ans, pas à 67 — et chaque trimestre manquant lui
        coûtait 0,875 %, pas 1,25 %. Lui opposer le barème du privé retirait
        jusqu'à un sixième de sa pension.

        **Et les régimes spéciaux ont ce barème avec quatre ans de retard.**
        La réforme de 2008 ne leur applique aucune décote avant le 1er juillet
        2010, puis un dixième du taux plein, un dixième de plus chaque année
        jusqu'à 1,25 % en 2019 : un cheminot parti en 2011 décotait de 0,125 %
        par trimestre manquant, non de 1,25 %.
        """
        age_annulation = self._age_taux_plein(periode, carriere)
        if periode.bareme_decote in _BAREMES_DECOTE_EN_TABLE:
            table = (self.decote_fonction_publique
                     if periode.bareme_decote == "fonction_publique"
                     else self.decote_regimes_speciaux)
            parametres = table.parametres(
                self._annee_ouverture_des_droits(periode, carriere, annee_liquidation)
            )
            if parametres is None:
                return None, age_annulation, None
            trimestres_avant, coefficient, fiabilite = parametres
            if periode.bareme_decote == "regimes_speciaux_age_fixe":
                # Les catégories d'âge atypique — artistes du ballet, musiciens
                # de l'orchestre — n'ont pas l'âge de référence de droit
                # commun : le V de l'article 14 leur donne « l'âge minimum
                # d'ouverture du droit à pension qui leur est applicable majoré
                # de […] huit trimestres », un âge fixe que la montée en charge
                # ne recule pas. La fiche le porte tel quel.
                return coefficient, age_annulation, fiabilite
            return coefficient, age_annulation - trimestres_avant / 4.0, fiabilite
        if periode.decote_par_trimestre is None:
            return None, age_annulation, None
        if periode.decote_par_generation:
            par_generation = self.coefficients_minoration.coefficient(
                carriere.generation
            )
            if par_generation is not None:
                return par_generation[0], age_annulation, par_generation[1]
        return periode.decote_par_trimestre, age_annulation, None

    def _annee_ouverture_des_droits(self, periode: PeriodeRegime,
                                    carriere: Carriere,
                                    annee_liquidation: int) -> int:
        """Année où les conditions d'ouverture du droit sont réunies.

        C'est le millésime auquel se lisent les barèmes de décote en table —
        celui de la fonction publique (loi du 21 août 2003, article 66 III)
        comme celui des régimes spéciaux (décrets de 2008). L'assuré les réunit
        quand il atteint l'âge d'ouverture de son régime, au mois près ; s'il
        liquide avant — carrière longue, catégorie active —, il les réunit au
        plus tôt à la liquidation, et c'est cette année-là qui vaut.
        """
        ouverture = carriere.date_naissance.plus_mois(
            en_mois(self._age_ouverture(periode, carriere))
        ).annee
        return min(annee_liquidation, ouverture)

    def _trimestres_de_decote(self, periode: PeriodeRegime, carriere: Carriere,
                              trimestres: int,
                              requis: int, age_liquidation: float,
                              age_annulation: float) -> float:
        """Trimestres de décote opposables, plafond compris.

        **Le militaire a le sien, et il ne compte pas des âges.** Le II de
        l'article L. 14 lui oppose, non la distance à un âge d'annulation, mais
        « le nombre de trimestres manquants […] pour atteindre […] la durée de
        services militaires effectifs nécessaire pour pouvoir bénéficier d'une
        liquidation de la pension […] augmentée d'une durée de services
        effectifs de dix trimestres » — dans la limite de dix trimestres, et non
        de vingt. Un sous-officier parti à quarante ans avec dix-sept ans de
        services ne perd donc que les deux trimestres et demi qui le séparent de
        dix-neuf ans et demi, quand le barème des civils lui aurait retiré le
        quart de sa pension pour être parti vingt-deux ans avant l'âge légal.

        Le décompte retient le plus favorable des deux : trimestres manquants
        pour la durée requise, ou trimestres manquants jusqu'à l'âge
        d'annulation de la décote.

        **Le plafond de vingt trimestres n'est pas une règle de plus : c'est
        l'arithmétique des deux âges.** Il est écrit là où le droit a voulu
        l'écrire — R. 643-7 pour les professions libérales, R. 723-38 pour les
        avocats, le I de L. 14 pour la fonction publique — et absent de
        R. 351-27 2° comme de R. 732-61, qui ne s'en sont jamais souciés. La
        raison est mesurable dans les tables du dépôt : l'écart entre l'âge
        d'ouverture et l'âge d'annulation vaut EXACTEMENT vingt trimestres pour
        les générations 1930 à 1961, puis descend à dix-huit, quinze, treize et
        douze à mesure que les réformes relèvent le premier sans toucher au
        second. Sur toute liquidation que le droit ouvre, le décompte par l'âge
        est donc au plus de vingt par construction, et le plafond ne mord
        jamais — ``tests/test_moteur.py`` le vérifie sur toute la grille.

        Il ne mordrait que sur une liquidation ANTÉRIEURE à l'âge d'ouverture,
        que le modèle refuse depuis qu'il sait opposer un âge à toutes les
        carrières. Le garder ne coûte donc rien et protège d'un changement
        d'âges qui casserait l'identité ; le retirer demanderait de vérifier
        les trois textes qui l'écrivent. On le garde, et cette phrase dit
        pourquoi il ne se voit pas.

        Le décompte par l'ÂGE est arrondi à l'entier supérieur, comme le veut
        l'article R. 351-27. Les âges d'annulation des générations 1951 à 1954
        valent 65,33, 65,75, 66,17 et 66,58 ans : sans cet arrondi, on opposait
        13,32 trimestres à un assuré né en 1951 parti à 62 ans, quand le droit
        lui en oppose 14. Le barème d'anticipation de l'Agirc-Arrco, lui,
        arrondissait déjà — les deux décomptes suivent maintenant la même règle.
        """
        militaire = self._droit_militaire(periode, carriere)
        if militaire is not None:
            manquants_services = max(
                0, militaire.trimestres_cible - militaire.trimestres_servis
            )
            manquants_duree = max(0, requis - trimestres)
            return float(min(manquants_services, manquants_duree,
                             TRIMESTRES_DECOTE_MILITAIRE))
        manquants_age = float(_au_trimestre_superieur(
            (age_annulation - age_liquidation) * 4
        ))
        if periode.decote_annulee_par_la_duree:
            trimestres_decote = min(max(0, requis - trimestres), manquants_age)
        else:
            # Avant l'ordonnance du 26 mars 1982, le taux ne dépendait QUE de
            # l'âge : le régime général servait 20 % à 60 ans, majorés de
            # 4 points par année différée, puis — loi Boulin — 50 % à 65 ans,
            # diminués de 5 points par année anticipée. Aucune durée, si longue
            # fût-elle, n'ouvrait le taux plein avant l'âge. Annuler la décote
            # par la durée, comme le fait le droit d'après 1982, servait le taux
            # plein à 60 ans à des générations auxquelles la loi ne l'a jamais
            # donné.
            trimestres_decote = manquants_age
        if trimestres_decote <= 0:
            return 0.0
        if periode.decote_trimestres_maximum is not None:
            trimestres_decote = min(trimestres_decote, periode.decote_trimestres_maximum)
        return trimestres_decote

    def _valeur_point_fiche(self, periode: PeriodeRegime, annee: int) -> float:
        """Valeur de service du point écrite dans la fiche, à l'année demandée.

        La MSA est seule à publier celle de sa retraite proportionnelle — ni le
        code rural, ni les barèmes IPP, ni OpenFisca ne la portent —, et elle le
        fait dans un communiqué annuel. Une ancre datée suffit : la loi
        (L. 161-23-1) revalorise cette valeur sur les prix, et c'est donc l'index
        des prix qui la porte d'une année à l'autre.
        """
        if periode.valeur_point_euros is None:
            return 0.0
        return periode.valeur_point_euros * self.macro.coefficient_prix(
            periode.valeur_point_annee or annee, annee
        )

    def _points_msa(self, periode: PeriodeRegime, annee: int,
                    revenu: float) -> float:
        """Points de retraite proportionnelle agricole d'une année (R. 732-71).

        Le barème est un escalier à quatre marches, et chacune de ses bornes est
        une grandeur que le modèle connaît déjà :

        * jusqu'à **400 SMIC horaires**, quinze points, quel que soit le revenu ;
        * de 400 à **800 SMIC**, une pente de quinze à trente points ;
        * de 800 SMIC à **deux fois le minimum contributif** non majoré, trente
          points, et le barème ne bouge pas sur toute cette plage ;
        * au-delà, une pente de trente points au maximum **M** de l'année, que
          l'article R. 732-70 définit par ``M = (PM − AVTS) / (37,5 × VP)`` —
          PM étant la pension maximale du régime général, c'est-à-dire la moitié
          du plafond, AVTS l'allocation aux vieux travailleurs salariés et VP la
          valeur du point. Le plafond de revenu de cette dernière marche est le
          plafond de la Sécurité sociale lui-même.

        **Le barème s'auto-vérifie.** Au minimum d'assiette du chef
        d'exploitation — six cents fois le SMIC horaire, D. 731-120 —, la deuxième marche
        donne 22,5 points, et au plafond la quatrième en donne 113,4 en 2025 :
        ce sont les « 23 à 113 points » que la MSA et le ministère annoncent
        sans jamais publier la formule. Et la pension maximale qui en résulte
        pour une carrière pleine vaut exactement ``PM − AVTS``, la valeur du
        point s'annulant : le forfait complète la proportionnelle jusqu'à la
        pension maximale du régime général, ce qui est bien la construction du
        régime.
        """
        smic = self.macro.smic_horaire(annee)
        pass_annuel = self.macro.plafond_securite_sociale(annee)
        valeur_point = self._valeur_point_fiche(periode, annee)
        if smic <= 0 or pass_annuel <= 0 or valeur_point <= 0:
            return 0.0
        # L'AVTS est le montant de la retraite forfaitaire elle-même : la loi
        # les a égalés jusqu'en 2014 (L. 732-24), puis a figé le forfait sur
        # l'AVTS de cette année-là. Les deux ont depuis divergé — 4 023,51 €
        # d'AVTS au 1er janvier 2025 contre 3 850 € environ de forfait —, ce qui
        # porte M à 115,1 points au lieu de 113,4 : un pour cent et demi de trop
        # sur la marche la plus haute du barème. La fiche ne porte qu'un
        # montant, et c'est celui-là ; le jour où l'AVTS entrera dans le dépôt,
        # c'est ici qu'elle se substituera.
        avts = (periode.pension_forfaitaire_annuelle or 0.0) * self.macro.coefficient_prix(
            periode.pension_forfaitaire_annee or annee, annee
        )
        minimum_contributif, _, _, _ = self.minimum_contributif.valeurs(annee)
        maximum = (0.5 * pass_annuel - avts) / (37.5 * valeur_point)
        if revenu <= 400 * smic:
            return 15.0
        if revenu <= 800 * smic:
            return min(30.0, 15.0 + 15.0 * (revenu - 400 * smic) / (400 * smic))
        if revenu <= 2 * minimum_contributif or pass_annuel <= 2 * minimum_contributif:
            return 30.0
        return min(maximum, 30.0 + (maximum - 30.0)
                   * (revenu - 2 * minimum_contributif)
                   / (pass_annuel - 2 * minimum_contributif))

    def _abattement_points(self, periode: PeriodeRegime, carriere: Carriere,
                           trimestres: int, requis: int,
                           age_liquidation: float,
                           annee_liquidation: int,
                           trimestres_regime: int = 0) -> float:
        """Coefficient d'un régime en points : abattu avant le taux plein,
        majoré après.

        Il ne dépassait jamais un, et c'était un droit manquant : voir
        :meth:`_surcote_points`, qui rend la majoration que la fiche écrit
        quand l'abattement est revenu à un. ``trimestres_regime`` est la durée
        d'affiliation à ce régime-là, que la CIPAV oppose à sa surcote.

        « Avant le taux plein » est une condition de DURÉE autant que d'âge :
        une complémentaire est servie sans abattement dès que l'assuré a le
        taux plein au régime de base, même s'il liquide avant l'âge d'annulation
        de la décote.

        L'Agirc-Arrco ne reprend pas la décote du régime de base : elle publie
        ses propres COEFFICIENTS D'ANTICIPATION, en deux tables — l'une indexée
        sur les trimestres manquants, l'autre sur l'âge — et retient la plus
        avantageuse pour l'assuré. Les deux ne se recoupent pas : douze
        trimestres manquants valent 0,88, quand la décote du régime de base
        n'en donnerait que 0,85 ; mais dix ans d'anticipation valent 0,43, là
        où elle en donnerait 0,50.

        **L'Ircantec a le même barème, et son texte l'écrit.** L'article 16 de
        l'arrêté du 30 décembre 1970 donne le coefficient 0,43 dix ans avant
        l'âge normal, « majoré de 0,017 5 par trimestre » jusqu'à cinq ans
        avant, de 0,012 5 par trimestre sur les deux suivantes et de 0,01 par
        trimestre sur les trois dernières : ce sont, marche pour marche, les
        paliers de l'Agirc-Arrco. Son paragraphe 2 est la seconde table —
        l'assuré qui n'a pas la durée requise se voit appliquer le même
        escalier « en assimilant à l'âge de soixante-cinq ans l'âge auquel
        [il] aurait effectivement accompli la durée d'assurance », sans
        pouvoir descendre sous le coefficient de son âge, ce qui est
        exactement « la plus avantageuse des deux ». Le modèle lui opposait
        1,1 % par trimestre, taux moyen qui tombe juste aux deux extrémités du
        barème — 0,78 à cinq ans, 1,00 à zéro — et nulle part entre les deux :
        à douze trimestres il retirait 13,2 % là où l'arrêté en retire 12.
        """
        if periode.abattement_points in ("agirc_arrco", "ircantec"):
            # AVANT L'ASF, L'ÂGE SEUL. Jusqu'à l'accord du 4 février 1983,
            # l'Agirc et l'Arrco servaient le taux plein à soixante-cinq ans et
            # abattaient toute anticipation, quelle que soit la durée : c'est
            # l'ASF qui a financé la retraite à soixante ans sans abattement
            # pour qui avait le taux plein au régime de base. Une période sans
            # durée requise — ni en dur, ni lue à la génération — porte ce
            # droit-là, et la table par durée ne s'y consulte pas.
            par_age_seul = (
                periode.duree_requise_trimestres is None
                and not periode.duree_requise_par_generation
            )
            if not par_age_seul and trimestres >= requis:
                abattement = 1.0
            else:
                par_duree = (
                    None if par_age_seul
                    else _coefficient_anticipation(requis - trimestres, 20)
                )
                ecart_age = max(
                    0.0,
                    (self._age_taux_plein(periode, carriere) - age_liquidation) * 4,
                )
                par_age = _coefficient_anticipation(ecart_age, 40)
                if par_age is None:
                    par_age = _COEFFICIENT_ANTICIPATION_PLANCHER
                candidats = [c for c in (par_duree, par_age) if c is not None]
                abattement = max(candidats) if candidats else 1.0
        elif periode.abattement_points in _ABATTEMENTS_IRCEC:
            abattement = self._abattement_ircec(
                periode, carriere, trimestres, requis,
                age_liquidation, annee_liquidation,
            )
        else:
            abattement = self._abattement_regime_de_base(
                periode, carriere, trimestres, requis,
                age_liquidation, annee_liquidation,
            )

        if abattement < 1.0:
            # ABATTU ET MAJORÉ NE SE RENCONTRENT PAS. Les deux majorations de
            # l'arrêté supposent l'une l'âge du taux plein dépassé, l'autre la
            # durée requise dépassée — c'est-à-dire, dans les deux cas, un
            # coefficient d'anticipation déjà revenu à 1. L'écrire coûte une
            # ligne et dispense de s'en convaincre à chaque lecture.
            return abattement
        return self._surcote_points(
            periode, carriere, trimestres, requis,
            age_liquidation, annee_liquidation, trimestres_regime,
        )

    def _abattement_regime_de_base(self, periode: PeriodeRegime,
                                   carriere: Carriere, trimestres: int,
                                   requis: int, age_liquidation: float,
                                   annee_liquidation: int) -> float:
        """Coefficient qui reprend la décote du régime de base : un taux par
        trimestre manquant, au plus favorable de l'âge et de la durée."""
        decote, age_annulation, _ = self._decote(
            periode, carriere, annee_liquidation
        )
        if decote is None:
            return 1.0
        trimestres_decote = self._trimestres_de_decote(
            periode, carriere, trimestres, requis, age_liquidation,
            age_annulation
        )
        return max(0.0, 1.0 - decote * trimestres_decote)

    def _abattement_ircec(self, periode: PeriodeRegime, carriere: Carriere,
                          trimestres: int, requis: int,
                          age_liquidation: float,
                          annee_liquidation: int) -> float:
        """Coefficient de minoration des trois régimes de l'IRCEC.

        Les règlements du RAAP (art. 27), du RACD (art. 21) et du RACL
        (art. 21) ne reprennent pas la décote du régime de base : ils comptent
        des ANNÉES manquantes jusqu'à l'âge du taux plein — celui du 1° de
        l'article L. 351-8 —, « 2,5 % par année pour chacune des deux premières
        années manquantes ; 5 % par année manquante supplémentaire ». Une
        année entamée compte entière : l'annexe de l'arrêté du 21 novembre
        2013 le chiffre trimestre par trimestre, un à quatre trimestres
        d'anticipation valant 2,5 %, cinq à huit 5 %, neuf à douze 10 %.

        « Toutefois, si cela est plus favorable à l'adhérent », les mêmes
        coefficients que ceux du régime de base : c'est la décote de la fiche,
        et le coefficient retenu est le plus haut des deux. La pension est
        servie sans minoration dès l'âge légal si celle du régime de base
        l'est au taux plein, c'est-à-dire dès que la durée requise est réunie.

        ``ircec_age_seul`` est le RACL de 2014 à 2024 : « 5 % par année
        manquante », sans marche à 2,5 %, sans renvoi au régime de base, et un
        taux plein que la durée n'ouvrait pas — il fallait l'âge. L'arrêté du
        13 mai 2025 l'a aligné sur les deux autres. Le modèle leur opposait à
        tous trois 1,25 % par trimestre depuis soixante-sept ans : vingt-cinq
        pour cent à soixante-deux ans pour qui n'a pas sa durée, là où l'IRCEC
        en retire vingt.
        """
        age_taux_plein = self._age_taux_plein(periode, carriere)
        age_seul = periode.abattement_points == "ircec_age_seul"
        if age_liquidation >= age_taux_plein - 1e-9:
            return 1.0
        if not age_seul and trimestres >= requis:
            return 1.0
        annees = -(-_au_trimestre_superieur(
            (age_taux_plein - age_liquidation) * 4) // 4)
        if age_seul:
            propre = 1.0 - 0.05 * annees
        else:
            propre = 1.0 - 0.025 * min(annees, 2) - 0.05 * max(0, annees - 2)
        propre = max(0.0, propre)
        if age_seul:
            return propre
        return max(propre, self._abattement_regime_de_base(
            periode, carriere, trimestres, requis,
            age_liquidation, annee_liquidation,
        ))

    #: Premier trimestre que la surcote puisse compter : les dispositions de
    #: la loi du 21 août 2003 valent pour les périodes cotisées accomplies à
    #: compter du 1er janvier 2004.
    SURCOTE_DEPUIS = DateMois(2004, 1)
    #: Âge au-delà duquel le barème de 2007-2008 sert 1,25 %.
    SURCOTE_AGE_MAJORE = 65

    def _coefficient_surcote_datee(self, periode: PeriodeRegime, carriere: Carriere,
                                   trimestres: int, requis: int,
                                   supplementaires: int, age_ouverture: float
                                   ) -> tuple[float, Fiabilite | None]:
        """Coefficient de surcote, trimestre civil par trimestre civil.

        La règle est celle de la circulaire Cnav 2018-04 (point 2), que le
        modèle suivait à l'année près : la PÉRIODE DE RÉFÉRENCE commence au
        plus tard des trois — le premier jour du trimestre civil qui suit
        l'âge légal, le premier jour du mois qui suit l'acquisition de la
        durée requise, le 1er janvier 2004 — et s'achève au dernier jour du
        trimestre civil qui précède la date d'effet. Chaque trimestre civil de
        cette période compte, dans la limite des trimestres cotisés reportés
        au compte pour l'année, et au plus ``supplementaires`` en tout ; puis
        chacun prend le taux du barème à sa date. Un assuré né le 15 avril, à
        l'âge légal en avril, ne surcote qu'à partir de juillet : le modèle
        comptait avril, et servait un trimestre de trop.

        La durée acquise se lit dans l'ordre des années. Les trimestres qui ne
        tiennent à aucune année — la majoration pour enfants — sont réputés
        acquis d'emblée : ils sont dus quelle que soit la date du départ, et la
        caisse ne les date pas davantage.
        """
        annee_liquidation = carriere.annee_liquidation
        date_legal = carriere.date_naissance.plus_mois(en_mois(age_ouverture))
        trimestre_legal = (date_legal.mois - 1) // 3
        debut_age = DateMois(date_legal.annee, 1).plus_mois(3 * (trimestre_legal + 1))

        par_annee = {
            ligne.annee: carriere.trimestres_retenus(ligne)
            for ligne in carriere.lignes if ligne.annee <= annee_liquidation
        }
        cotises_par_annee = {
            ligne.annee: carriere.trimestres_retenus(ligne)
            for ligne in carriere.lignes
            if ligne.cotise and ligne.annee <= annee_liquidation
        }
        acquis = trimestres - sum(par_annee.values())
        debut_duree = None
        if acquis >= requis:
            debut_duree = self.SURCOTE_DEPUIS
        for annee in sorted(par_annee):
            if debut_duree is not None:
                break
            valides = par_annee[annee]
            if acquis + valides >= requis:
                manquants = requis - acquis
                debut_duree = DateMois(annee, 1).plus_mois(3 * manquants)
            acquis += valides
        if debut_duree is None:
            return 1.0, None
        debut = DateMois.depuis_rang(max(
            debut_age.rang, debut_duree.rang, self.SURCOTE_DEPUIS.rang
        ))
        # Le trimestre de départ est ramené au trimestre civil qui le
        # contient s'il commence en cours de trimestre : la durée acquise au
        # 30 juin ouvre la période au 1er juillet, celle acquise au 31 mai
        # l'ouvre au 1er juin, mais un trimestre civil ne se compte qu'entier.
        if (debut.mois - 1) % 3:
            debut = DateMois(debut.annee, 1).plus_mois(3 * ((debut.mois - 1) // 3 + 1))
        fin = carriere.date_liquidation
        date_65 = carriere.date_naissance.plus_mois(12 * self.SURCOTE_AGE_MAJORE)
        trimestre_65 = (date_65.annee, (date_65.mois - 1) // 3)

        dates: list[tuple[DateMois, bool]] = []
        restants_par_annee = dict(cotises_par_annee)
        courant = debut
        while courant.rang + 2 < fin.rang and len(dates) < supplementaires:
            if restants_par_annee.get(courant.annee, 0) > 0:
                restants_par_annee[courant.annee] -= 1
                apres_65 = (courant.annee, (courant.mois - 1) // 3) > trimestre_65
                dates.append((courant, apres_65))
            courant = courant.plus_mois(3)
        if not dates:
            return 1.0, None
        if not self.surcote_baremes.connait(periode.surcote_bareme or ""):
            return 1.0 + (periode.surcote_par_trimestre or 0.0) * len(dates), None
        return self.surcote_baremes.coefficient(periode.surcote_bareme, dates)

    def _surcote_points(self, periode: PeriodeRegime, carriere: Carriere,
                        trimestres: int, requis: int,
                        age_liquidation: float,
                        annee_liquidation: int,
                        trimestres_regime: int = 0) -> float:
        """Majoration d'un régime en points liquidé APRÈS le taux plein.

        Trois façons de compter, parce que les textes en écrivent trois, et la
        fiche dit laquelle par ``surcote_points`` :

        ``regime_general`` — la règle de l'article L. 351-1-2, mot pour mot
        celle que la branche en annuités sert : trimestres COTISÉS « après
        l'âge prévu au premier alinéa de l'article L. 351-1 et au-delà de la
        limite mentionnée au deuxième alinéa du même article ». C'est celle du
        régime de base des professions libérales — R. 643-8, 0,75 % par
        trimestre depuis 2004, 1,25 % pour les trimestres accomplis à compter
        du 1er septembre 2023 — et celle des exploitants agricoles (D. 732-42).
        Le militaire n'en a aucune, et le décompte part de l'âge légal de droit
        commun, comme là-bas.

        ``par_age_seul`` — les statuts des sections libérales ne comptent ni
        durée ni cotisation, seulement le TEMPS : « 1,25 % par trimestre
        séparant le premier jour du trimestre civil suivant celui où le médecin
        atteint cet âge de la date d'effet de la retraite » (CARMF, art. 15),
        « par trimestre civil entier d'ajournement postérieur à l'âge du taux
        plein dans la limite de vingt trimestres » (CARPIMKO, art. 12 ter),
        « par trimestre plein de prorogation au-delà de cet âge, dans la limite
        maximale de 25 % » (CAVEC, art. 13). Le décompte part de
        ``surcote_age_debut``, ou de l'âge du taux plein lu à la génération ;
        il s'arrête à ``surcote_age_maximum`` — le soixante-dixième
        anniversaire, chez les médecins et les notaires — et à
        ``surcote_trimestres_maximum`` ; il ne retient que des multiples de
        ``surcote_pas_trimestres`` quand le texte dit « par année pleine » ;
        il change de taux à ``surcote_palier_age`` — 0,75 % au lieu de 1,25 %
        après soixante-cinq ans, à la CARMF et à l'ASV — ; et il n'est dû
        qu'au-delà de ``surcote_affiliation_minimale_trimestres`` d'affiliation
        au régime, « si, à 67 ans, vous réunissez 30 années d'affiliation à la
        Cipav ».

        ``ircantec`` — le IV de l'article 16 de l'arrêté du 30 décembre 1970,
        paragraphe 4 dans la version que le décret du 23 septembre 2008 a
        introduite « à compter du 1er janvier 2010 », majore le total des
        points de DEUX façons qui ne se recouvrent pas : 1° « 0,75 % par
        trimestre entier écoulé entre le soixante-cinquième anniversaire de
        l'assuré et la date d'entrée en jouissance de la pension » — du temps
        écoulé, comme ``par_age_seul`` ; 2° « 0,625 % par trimestre accompli »
        de durée cotisée au-delà de l'âge légal et de la durée requise, en deçà
        de ce même âge — l'assiette de ``regime_general``, bornée en haut par
        l'âge où le 1° prend le relais, car « en aucun cas une même période ne
        peut donner lieu à la fois » aux deux.

        Le modèle ne servait que la troisième : la branche en points ne lisait
        pas ``surcote_par_trimestre``, et neuf fiches de non-salariés en
        écrivaient une pour rien.
        """
        mode = periode.surcote_points
        if mode == "aucune":
            return 1.0
        if mode == "ircantec":
            return self._surcote_ircantec(
                periode, carriere, trimestres, requis,
                age_liquidation, annee_liquidation,
            )
        taux = periode.surcote_par_trimestre
        if not taux:
            return 1.0
        if mode == "regime_general":
            supplementaires = max(0, trimestres - requis)
            age_ouverture = self._age_ouverture_commun(periode, carriere)
            if (supplementaires <= 0 or age_liquidation < age_ouverture
                    or self._droit_militaire(periode, carriere) is not None):
                return 1.0
            supplementaires = min(
                supplementaires,
                _trimestres_cotises_apres(carriere, age_ouverture, annee_liquidation),
            )
            return 1.0 + taux * supplementaires
        if mode != "par_age_seul":
            raise ValueError(f"surcote_points inconnu : {mode!r}")

        minimum = periode.surcote_affiliation_minimale_trimestres
        if minimum is not None and trimestres_regime < minimum:
            return 1.0
        debut = periode.surcote_age_debut
        if debut is None:
            debut = self._age_taux_plein(periode, carriere)
        fin = age_liquidation
        if periode.surcote_age_maximum is not None:
            fin = min(fin, periode.surcote_age_maximum)
        # Des trimestres civils ENTIERS : deux mois de plus ne valent rien.
        ecoules = int((max(0.0, fin - debut) + 1e-9) * 4)
        if periode.surcote_trimestres_maximum is not None:
            ecoules = min(ecoules, periode.surcote_trimestres_maximum)
        pas = max(1, periode.surcote_pas_trimestres)
        ecoules -= ecoules % pas
        if ecoules <= 0:
            return 1.0
        palier = periode.surcote_palier_age
        if palier is None or periode.surcote_par_trimestre_apres_palier is None:
            return 1.0 + taux * ecoules
        avant_palier = min(ecoules, max(0, int((palier - debut + 1e-9) * 4)))
        return (1.0
                + taux * avant_palier
                + periode.surcote_par_trimestre_apres_palier
                * (ecoules - avant_palier))

    def _surcote_ircantec(self, periode: PeriodeRegime, carriere: Carriere,
                          trimestres: int, requis: int,
                          age_liquidation: float,
                          annee_liquidation: int) -> float:
        """Les deux taux du IV de l'article 16 — voir :meth:`_surcote_points`."""
        age_taux_plein = self._age_taux_plein(periode, carriere)

        # 1° — LE TEMPS ÉCOULÉ, en trimestres ENTIERS : l'arrêté le dit, et
        # deux mois de plus ne valent rien.
        ecoules = int((max(0.0, age_liquidation - age_taux_plein) + 1e-9) * 4)

        # 2° — LA DURÉE COTISÉE EN DEÇÀ. Les trimestres au-delà de la durée
        # requise sont les DERNIERS de la carrière : les compter ici suppose
        # donc que la durée requise était déjà atteinte avant l'âge du taux
        # plein, sans quoi ils tombent dans la fenêtre du 1° et y sont déjà
        # payés.
        supplementaires = 0
        age_ouverture = self._age_ouverture_commun(periode, carriere)
        if age_liquidation >= age_ouverture:
            avant = min(
                trimestres,
                _trimestres_valides_avant(
                    carriere, age_taux_plein, annee_liquidation
                ),
            )
            supplementaires = max(0, avant - requis)
            if supplementaires > 0:
                supplementaires = min(
                    supplementaires,
                    _trimestres_cotises_entre(
                        carriere, age_ouverture, age_taux_plein,
                        annee_liquidation,
                    ),
                )
        return (1.0
                + _SURCOTE_IRCANTEC_AGE * ecoules
                + _SURCOTE_IRCANTEC_DUREE * supplementaires)

    def _plafond_majoration(self, code: str, periode: PeriodeRegime,
                            carriere: Carriere,
                            annee_liquidation: int) -> float | None:
        """Plafond en euros de la majoration pour enfants, ou ``None``.

        Les régimes de base servent 10 % sans plafond ; l'Agirc-Arrco, elle,
        borne la majoration en euros — 2 367 € par an pour les pensions servies
        depuis le 1er novembre 2025 — et le plafond est revalorisé comme la
        valeur de service du point, à laquelle il est donc rapporté ici. Sans
        lui, les familles très nombreuses de salariés du privé étaient
        surestimées.

        Le plafond ne s'oppose qu'aux assurés nés à compter du 2 août 1951 : le
        modèle ne connaît que l'année de naissance et retient les générations à
        partir de 1952, comme il le fait des autres bornes coupées en cours
        d'année.
        """
        if periode.plafond_majoration_enfants is None:
            return None
        if carriere.annee_naissance < 1952:
            return None
        plafond = periode.plafond_majoration_enfants
        annee_reference = periode.plafond_majoration_annee
        if annee_reference is None or annee_reference == annee_liquidation:
            return plafond
        servie = self.valeur_du_point(code, annee_liquidation)
        publiee = self.valeur_du_point(code, annee_reference)
        if servie is None or publiee is None or publiee[0] <= 0:
            return plafond * self.macro.coefficient_prix(
                annee_reference, annee_liquidation
            )
        return plafond * servie[0] / publiee[0]

    def _majoration_pour_enfants(self, carriere: Carriere,
                                 trimestres_par_regime: dict[str, int],
                                 annee_liquidation: int
                                 ) -> _MajorationEnfants | None:
        """Trimestres dus au titre des enfants, et régime qui les porte.

        Le droit n'attribue pas ces trimestres au-dessus des régimes : il les
        donne DANS un régime. Ce qu'ils y font dépend de leur nature — une
        bonification entre aux services et relève donc la proratisation, une
        majoration de durée d'assurance ne joue que sur la décote tous régimes
        confondus. C'est le champ `services` du résultat qui les sépare, et
        c'est lui, non `trimestres`, que l'appelant ajoute au compte du régime.
        On retient donc, parmi les régimes en annuités dont la fiche de
        l'année de liquidation porte un dispositif que la table sert, celui
        qui accorde le plus ; à égalité, celui où l'assuré a validé le plus de
        trimestres ; à égalité encore, le dernier code par ordre alphabétique,
        pour que le résultat ne dépende pas de l'ordre d'un dictionnaire.

        Renvoie ``None`` quand rien n'est dû : pas d'enfant, aucun régime
        porteur, dispositif pas encore né, ou assuré qui n'en est pas le
        bénéficiaire.
        """
        if carriere.nombre_enfants <= 0:
            return None
        candidats: list[tuple[int, int, str, str, Fiabilite]] = []
        for code, valides in trimestres_par_regime.items():
            if code not in self.catalogue:
                continue
            regime = self.catalogue[code]
            periode = regime.periode(min(annee_liquidation, _derniere_annee(regime)))
            if periode is None or periode.type_calcul != "annuites":
                continue
            for dispositif in periode.avantages_non_contributifs:
                accorde = self.majorations_enfants.par_enfant(
                    dispositif, carriere.sexe, carriere.annee_naissance,
                    annee_liquidation, carriere.nombre_enfants,
                )
                if accorde is None:
                    continue
                trimestres, services, fiabilite = accorde
                candidats.append((
                    trimestres * carriere.nombre_enfants, valides, dispositif,
                    code, services * carriere.nombre_enfants, fiabilite,
                ))
        if not candidats:
            return None
        trimestres, _, dispositif, code, services, fiabilite = max(
            candidats, key=lambda c: (c[0], c[1], c[3])
        )
        return _MajorationEnfants(
            regime=code, dispositif=dispositif, trimestres=trimestres,
            services=services, fiabilite=fiabilite,
        )

    # -- calcul --------------------------------------------------------------

    def calculer(self, carriere: Carriere,
                 ignorer_penalite_age: bool = False,
                 avantages_non_contributifs: bool = True,
                 avpf: bool = True,
                 liquider_successions: bool = True) -> ResultatActuel:
        """Pension servie par le système en vigueur.

        ``ignorer_penalite_age`` neutralise la décote et la surcote liées à
        l'âge. On ne l'utilise que pour VALORISER DES DROITS ACQUIS à une date
        donnée — la question n'est alors pas « que toucherait cet assuré s'il
        liquidait aujourd'hui à 40 ans », qui n'a pas de sens, mais « quels
        droits sa carrière lui a-t-elle déjà ouverts ». La proratisation par la
        durée, elle, continue de s'appliquer : une carrière courte ouvre bien
        des droits proportionnellement plus faibles.

        ``avantages_non_contributifs`` commande le minimum contributif, la
        majoration pour trois enfants et la majoration de durée d'assurance.
        Il vaut VRAI par défaut, et il doit le rester : ce scénario décrit le
        droit positif, il sert d'étalon, et un étalon amputé de ses minima
        sous-estime le système actuel là où il protège le plus — petites
        pensions et carrières de mères de famille. Seule la valorisation des
        droits acquis du scénario prospectif le met à faux, parce qu'elle
        mesure du contributif pur.

        Les drapeaux :class:`Neutralisations` ne sont PAS lus ici : ils
        décrivent ce que les scénarios notionnels retirent, pas ce que le droit
        en vigueur accorde.

        ``liquider_successions`` fait liquider ensemble un régime d'annuités et
        celui qui lui succède (voir :meth:`_groupes_de_succession`). C'est le
        droit, et le défaut ; à FAUX, chaque nom de caisse est liquidé sur ses
        seules années, comme le modèle le faisait, et la variante ne sert qu'à
        mesurer ce que la correction déplace.
        """
        annee_liquidation = carriere.annee_liquidation
        age_liquidation = carriere.age_liquidation or 0.0

        trimestres = carriere.trimestres_actuels

        pensions: list[PensionRegime] = []
        fiabilite_globale = Fiabilite.CERTIFIEE
        trimestres_requis = 0
        taux_retenu = 0.0

        #: Régimes de base qui portent le minimum contributif : indice dans
        #: ``pensions``, prorata de durée d'assurance, prorata de durée
        #: COTISÉE, et condition de taux plein remplie ou non.
        eligibles_minimum: list[_EligibleMinimum] = []
        #: Régimes de la fonction publique qui portent le minimum garanti.
        eligibles_garanti: list[_EligibleMinimumGaranti] = []

        # Cotisations cumulées par régime, pour les régimes en points dont on
        # n'a pas le prix d'achat du point ; points acquis pour les autres.
        cumul_cotisations: dict[str, float] = {}
        points_acquis: dict[str, float] = {}
        fiabilite_points: dict[str, Fiabilite] = {}
        # Durée d'assurance validée dans chaque régime, PÉRIODES ASSIMILÉES
        # COMPRISES : le coefficient de proratisation du régime général porte
        # sur la durée d'assurance, pas sur les seules années cotisées. Une
        # année de chômage indemnisé ne verse rien au compte mais compte bien
        # dans le rapport durée acquise / durée requise.
        trimestres_par_regime: dict[str, int] = {}
        # SERVICES accomplis dans chaque régime. La fonction publique ne
        # proratise pas sa pension sur la durée d'assurance mais sur les
        # services et bonifications (L. 13 du code des pensions), et l'article
        # L. 9 écarte « le temps passé dans une position statutaire ne
        # comportant pas l'accomplissement de services effectifs au sens de
        # l'article L. 5 », hors la liste fermée qu'il énumère. Le moteur
        # créditait ce prorata de TOUTE période validée : une carrière de
        # fonctionnaire coupée de cinq ans de chômage servait exactement la
        # même pension qu'une carrière pleine.
        services_par_regime: dict[str, int] = {}
        # Ce qui reste du budget de services que L. 9 ouvre dans une limite —
        # trois ans par enfant pour le congé parental. Il se tient sur toute la
        # carrière, et non année par année : deux congés de deux ans pour un
        # seul enfant n'ouvrent que trois ans de services.
        budget_services_plafonnes: dict[int, int] = {}
        # Durée COTISÉE dans chaque régime : c'est elle, et non la durée
        # d'assurance, qui proratise la majoration du minimum contributif au
        # titre des périodes cotisées (D. 351-2-2).
        trimestres_cotises_par_regime: dict[str, int] = {}
        # Dernière année cotisée dans chaque régime : elle désigne, dans une
        # chaîne de succession, la caisse qui liquide.
        derniere_annee_par_regime: dict[str, int] = {}

        for ligne in carriere.lignes:
            retenus_ligne = carriere.trimestres_retenus(ligne)
            if retenus_ligne <= 0:
                continue
            services_ligne = (
                retenus_ligne if ligne.services_fonction_publique else 0
            )
            plafond = ligne.services_plafond_trimestres_par_enfant
            if services_ligne and plafond:
                restant = budget_services_plafonnes.setdefault(
                    plafond, plafond * carriere.nombre_enfants
                )
                services_ligne = min(services_ligne, restant)
                budget_services_plafonnes[plafond] = restant - services_ligne
            for code in self.affiliations.regimes(
                    ligne.affiliation, ligne.annee,
                    carriere.date_entree(ligne.affiliation),
                    revenu=ligne.revenu if ligne.cotise else ligne.revenu_reference,
                    plafond=self.macro.plafond_securite_sociale(ligne.annee)):
                if code not in self.catalogue:
                    continue
                trimestres_par_regime[code] = (
                    trimestres_par_regime.get(code, 0) + retenus_ligne
                )
                if services_ligne:
                    services_par_regime[code] = (
                        services_par_regime.get(code, 0) + services_ligne
                    )
                if ligne.cotise:
                    trimestres_cotises_par_regime[code] = (
                        trimestres_cotises_par_regime.get(code, 0) + retenus_ligne
                    )

        # Les trimestres accordés au titre des enfants ne flottent pas au-dessus
        # des régimes : le droit les attribue DANS un régime, et ils comptent
        # donc aussi dans sa proratisation, pas seulement dans la décote tous
        # régimes confondus. Les ignorer là amputait la pension d'une mère de
        # famille de la part que la majoration est censée lui rendre. Le régime
        # retenu est celui qui accorde le plus — exact pour une carrière
        # mono-affiliée, qui est le cas ordinaire, approché pour un
        # polypensionné, à qui le droit ferait porter la majoration par chacun
        # de ses régimes.
        majoration_enfants = (
            self._majoration_pour_enfants(
                carriere, trimestres_par_regime, annee_liquidation
            ) if avantages_non_contributifs else None
        )
        if majoration_enfants is not None:
            # LA DURÉE ET LES SERVICES NE SONT PAS LA MÊME CASE, et la
            # majoration se range dans les deux : tout ce qui est accordé joue
            # sur la durée d'assurance — tous régimes, donc la décote, et celle
            # du régime, donc sa proratisation — quand la seule part `services`
            # entre aux services, qui proratisent la pension de la fonction
            # publique. Ce module les confondait, et sur-créditait les mères
            # fonctionnaires de deux trimestres de services par enfant né depuis
            # 2004, là où L. 12 bis n'accorde qu'une majoration de durée.
            trimestres += majoration_enfants.trimestres
            trimestres_par_regime[majoration_enfants.regime] += (
                majoration_enfants.trimestres
            )
            services_par_regime[majoration_enfants.regime] = (
                services_par_regime.get(majoration_enfants.regime, 0)
                + majoration_enfants.services
            )
            fiabilite_globale = min(fiabilite_globale, majoration_enfants.fiabilite)

        for ligne in carriere.lignes:
            # Une ligne postérieure à la liquidation décrit une activité
            # exercée APRÈS le départ : elle n'ouvre pas de droits dans la
            # pension qu'on liquide. L'année du départ, elle, ouvre ceux de ses
            # mois qui l'ont précédé — ni zéro ni douze, mais le compte juste.
            part = carriere.part_retenue(ligne.annee)
            if part <= 0:
                continue
            if not ligne.cotise and not ligne.familles_cotisantes:
                continue
            # Pendant une période indemnisée, seuls les régimes complémentaires
            # encaissent, et sur le salaire d'avant l'interruption.
            base_ligne = ligne.revenu if ligne.cotise else ligne.revenu_reference
            if part < ligne.fraction_annee:
                base_ligne *= part / ligne.fraction_annee
            familles_admises = (
                None if ligne.cotise else set(ligne.familles_cotisantes)
            )
            for code in self.affiliations.regimes(
                    ligne.affiliation, ligne.annee,
                    carriere.date_entree(ligne.affiliation),
                    revenu=ligne.revenu if ligne.cotise else ligne.revenu_reference,
                    plafond=self.macro.plafond_securite_sociale(ligne.annee)):
                if code not in self.catalogue:
                    continue
                regime = self.catalogue[code]
                if (familles_admises is not None
                        and regime.famille not in familles_admises):
                    continue
                derniere_annee_par_regime[code] = max(
                    derniere_annee_par_regime.get(code, 0), ligne.annee
                )
                for periode in regime.periodes_actives(ligne.annee):
                    # BARÈME D'UN AUTRE RÉGIME : une tranche que tous les
                    # affiliés ne cotisent pas forme une fiche à part, dont les
                    # points restent ceux du régime d'origine. Voir `points_de`.
                    bareme = periode.points_de or code
                    # Les bornes d'assiette et le repère en points sont
                    # ANNUELS : une année incomplète ne les atteint qu'à
                    # proportion de ses mois, comme le plafond lui-même.
                    pass_annuel = (
                        self.macro.plafond_securite_sociale(ligne.annee) * part
                    )
                    borne_basse, borne_haute = periode.bornes_assiette_en_euros(
                        self.macro.plafond_securite_sociale(ligne.annee)
                    )
                    if part < 1.0:
                        borne_basse *= part
                        borne_haute = (None if borne_haute is None
                                       else borne_haute * part)
                    base = base_ligne
                    if periode.assiette == "primes_uniquement":
                        base = base_ligne * ligne.part_primes
                    elif periode.assiette == "hors_primes":
                        base = base_ligne * (1.0 - ligne.part_primes)
                    # L'assiette de la CAVAMAC est faite des commissions
                    # versées par les compagnies, celle de la CPRN des produits
                    # de l'office : le facteur les reconstitue depuis le
                    # revenu, avant les bornes. Voir `PeriodeRegime`.
                    if periode.assiette_facteur_revenu is not None:
                        base *= periode.assiette_facteur_revenu
                    # Le marin cotise sur le salaire forfaitaire de sa
                    # catégorie : voir `Compte.cotisation_annuelle`.
                    if periode.assiette_grille:
                        forfait_grille = self.grilles.forfait(
                            periode.assiette_grille, ligne.annee,
                            ligne.revenu_annualise,
                            lambda a: salaire_moyen_annuel(self.macro, a),
                        )
                        if forfait_grille is not None:
                            base = forfait_grille[0] * part
                    plafond = base if borne_haute is None else borne_haute
                    assiette = max(0.0, min(base, plafond) - borne_basse)
                    repere = periode.repere_assiette(
                        pass_annuel, self.macro.smic_horaire(ligne.annee)
                    ) * (part if periode.assiette_repere_smic is not None else 1.0)
                    if periode.assiette_forfaitaire:
                        # Assiette FORFAITAIRE : le régime des cultes cotise sur
                        # un forfait égal au SMIC mensuel, quel que soit le
                        # revenu. Inconditionnel, là où `assiette_plancher` ne
                        # relève que les assiettes trop basses.
                        assiette = repere
                    elif periode.assiette_plancher and assiette < repere:
                        # Assiette minimale : la complémentaire agricole cotise
                        # sur 1 820 SMIC même quand le revenu est en dessous,
                        # et ouvre donc ses cent points malgré tout.
                        assiette = repere
                    # La cotisation forfaitaire s'ajoute à la proportionnelle,
                    # et elle est due quel que soit le revenu — cf.
                    # `Compte._cotisation_forfaitaire`, même convention
                    # d'indexation sur les prix.
                    forfait = 0.0
                    if periode.cotisation_forfaitaire_euros is not None:
                        reference = (periode.cotisation_forfaitaire_annee
                                     or ligne.annee)
                        forfait = (periode.cotisation_forfaitaire_euros
                                   * self.macro.coefficient_prix(
                                       reference, ligne.annee))
                    cotisation = (assiette * periode.taux_cotisation_retraite
                                  + forfait)
                    # COTISATION PAR CLASSES : la Cipav, avant 2023, appelait
                    # le montant du palier où tombait le revenu, et non une
                    # fraction d'une assiette. Ce montant achète des points
                    # comme n'importe quelle cotisation — « 3 600 € / 47,40 € =
                    # 75,9 points », écrit la caisse —, et c'est donc ici, avant
                    # la conversion, qu'il se substitue.
                    if periode.cotisation_par_classes:
                        millesime = self.classes.annee_grille(code, ligne.annee)
                        reference = (
                            0.0 if millesime is None
                            else self.macro.plafond_securite_sociale(millesime)
                        )
                        par_classe = (
                            None if reference <= 0
                            else self.classes.cotisation(
                                code, ligne.annee, base,
                                self.macro.plafond_securite_sociale(ligne.annee)
                                / reference,
                            )
                        )
                        if par_classe is not None:
                            cotisation = par_classe[0] * part
                    if periode.bareme_points == "msa_proportionnelle":
                        # BARÈME NOMMÉ : le nombre de points ne se lit ni dans
                        # un prix d'achat ni dans un repère d'assiette, mais
                        # dans un escalier à quatre marches que R. 732-71 écrit
                        # en SMIC, en minimum contributif et en plafond. Voir
                        # `_points_msa`. C'est l'ASSIETTE qui y entre, et non le
                        # revenu : la cotisation qui ouvre ces points est due
                        # sur six cents SMIC horaires au moins (D. 731-120, 2°)
                        # et sur un plafond au plus, et ce sont ces deux bornes
                        # qui font les « 23 à 113 points ».
                        echelle, fiabilite_echelle = self.conversions_points.echelle(
                            bareme, ligne.annee, annee_liquidation
                        )
                        points_acquis[code] = points_acquis.get(code, 0.0) + (
                            self._points_msa(periode, ligne.annee, assiette)
                            * part * echelle
                        )
                        fiabilite_points[code] = min(
                            fiabilite_points.get(code, Fiabilite.CERTIFIEE),
                            regime.fiabilite, fiabilite_echelle,
                        )
                        continue
                    if periode.points_par_trimestre_valide is not None:
                        # POINTS PAR TRIMESTRE VALIDÉ, sans égard au montant.
                        # Le régime de base des libéraux d'avant 2004 ne servait
                        # pas une pension proportionnelle au revenu mais une
                        # ALLOCATION : un quinzième de l'AVTS par année cotisée,
                        # la même pour le notaire et pour le kinésithérapeute.
                        # La réforme de 2003 l'a convertie en points « à raison
                        # de cent points par trimestre » (D. 643-1), et c'est
                        # cette conversion — non l'assiette, qu'on n'a pas —
                        # qui porte le droit d'avant 2004.
                        echelle, fiabilite_echelle = self.conversions_points.echelle(
                            bareme, ligne.annee, annee_liquidation
                        )
                        points_acquis[code] = points_acquis.get(code, 0.0) + (
                            periode.points_par_trimestre_valide
                            * carriere.trimestres_retenus(ligne) * echelle
                        )
                        fiabilite_points[code] = min(
                            fiabilite_points.get(code, Fiabilite.CERTIFIEE),
                            regime.fiabilite, fiabilite_echelle,
                        )
                        continue
                    if periode.points_maximum is not None and repere > 0:
                        # Barème écrit en POINTS et non en prix d'achat : le
                        # régime annonce combien de points ouvre une assiette
                        # donnée — 525 points au plafond pour le régime de base
                        # des libéraux, 100 points pour 1 820 SMIC à la
                        # complémentaire agricole. Le nombre de points ne
                        # dépend alors pas du taux de cotisation, et c'est
                        # heureux : ce sont les barèmes qui sont publiés, pas
                        # les prix d'achat.
                        echelle, fiabilite_echelle = self.conversions_points.echelle(
                            bareme, ligne.annee, annee_liquidation
                        )
                        points_acquis[code] = points_acquis.get(code, 0.0) + (
                            periode.points_maximum * assiette / repere * echelle
                        )
                        fiabilite_points[code] = min(
                            fiabilite_points.get(code, Fiabilite.CERTIFIEE),
                            regime.fiabilite, fiabilite_echelle,
                        )
                        continue
                    achat = (self.valeurs_point.achat(bareme, ligne.annee)
                             if periode.type_calcul in ("points", "mixte") else None)
                    if achat is not None:
                        reference, taux_appel, fiabilite_achat = achat
                        points_annee = cotisation / (taux_appel * reference)
                        if periode.points_minimum_annuels is not None:
                            # Garantie minimale de points de l'Agirc : tout
                            # cadre cotisant en acquiert au moins 120 par an de
                            # 1989 à 2018, même quand sa tranche B est nulle,
                            # c'est-à-dire même quand son salaire ne dépasse pas
                            # le plafond de la Sécurité sociale. La fiche la
                            # déclarait ; le moteur ne la servait pas, et un
                            # cadre payé sous le plafond n'acquérait rien à
                            # l'Agirc là où le droit lui donnait ces points.
                            points_annee = max(
                                points_annee, periode.points_minimum_annuels
                            )
                        # Changement d'unité entre l'achat et le service : les
                        # points Arrco d'avant 1999 sont ceux de l'UNIRS, et
                        # valent 0,387464 point du régime unifié. Sans cette
                        # conversion, cent euros cotisés en 1998 produisaient
                        # 30,31 € de pension quand les mêmes cent euros de 1999
                        # n'en produisaient que 11,15 — un facteur 2,7 en une
                        # année, pour une unification qui était neutre.
                        echelle, fiabilite_echelle = self.conversions_points.echelle(
                            bareme, ligne.annee, annee_liquidation
                        )
                        points_acquis[code] = (
                            points_acquis.get(code, 0.0) + points_annee * echelle
                        )
                        fiabilite_points[code] = min(
                            fiabilite_points.get(code, Fiabilite.CERTIFIEE),
                            fiabilite_achat, fiabilite_echelle,
                        )
                    else:
                        cumul_cotisations[code] = cumul_cotisations.get(code, 0.0) + (
                            cotisation
                            * self.macro.coefficient_prix(ligne.annee, annee_liquidation)
                        )

        # Durée requise de référence : celle du régime de base. C'est elle qui
        # commande le taux plein, donc aussi l'abattement des complémentaires —
        # un assuré au taux plein liquide sa complémentaire sans abattement,
        # quel que soit son âge.
        requis_reference = 0
        #: Âge d'ouverture des droits le plus précoce parmi les régimes de base
        #: de la carrière. Un polypensionné liquide en réalité chaque pension à
        #: l'âge de son régime ; le modèle liquide tout à la fois, et retient
        #: donc l'âge du régime le plus précoce — celui d'un régime spécial,
        #: quand il y en a un.
        age_ouverture_reference: float | None = None
        codes = sorted(set(cumul_cotisations) | set(points_acquis))
        # Un régime et celui qui lui succède liquident ensemble, sous les règles
        # de la caisse qui aurait le dossier : les autres membres du groupe
        # sont sautés partout où un régime liquide.
        groupes = (
            self._groupes_de_succession(
                codes, annee_liquidation, derniere_annee_par_regime, carriere
            ) if liquider_successions else {}
        )
        # DEUX PASSES, ET LA SECONDE NE SERT QU'À QUI N'A QUE DES POINTS.
        # Les régimes en ANNUITÉS commandent, comme partout ailleurs. Mais une
        # carrière entière en points n'en a aucun, et la boucle laissait alors
        # `age_ouverture_reference` à ``None`` : aucun âge ne lui était opposé,
        # et un chef d'exploitation pouvait liquider à cinquante ans sans que
        # rien ne le refuse, quand l'artisan de la grille se le voyait refuser
        # à la même page. `requis_reference` retombait de son côté sur 160,
        # c'est-à-dire sur une durée que plus aucune génération ne doit — et
        # c'est cette durée-là que l'abattement du régime en points opposait.
        #
        # La seconde passe ne s'ouvre donc que si la première n'a rien trouvé,
        # et les comportements des carrières en annuités ne bougent pas d'un
        # trimestre. L'Agirc-Arrco et l'Ircantec en sont écartées comme
        # ailleurs : elles n'opposent pas la durée du régime de base, et ne
        # sont jamais seules sur une carrière.
        for calculs in (("annuites",), ("points", "mixte")):
            for code in codes:
                if groupes.get(code, (code,))[0] != code:
                    continue
                regime = self.catalogue[code]
                periode = regime.periode(
                    min(annee_liquidation, _derniere_annee(regime)))
                if periode is None or periode.type_calcul not in calculs:
                    continue
                if periode.abattement_points in ("agirc_arrco", "ircantec"):
                    continue
                requis_reference = max(
                    requis_reference, self._duree_requise(periode, carriere)[0]
                )
                age_regime = self._age_ouverture(periode, carriere)
                age_ouverture_reference = (
                    age_regime if age_ouverture_reference is None
                    else min(age_ouverture_reference, age_regime)
                )
            if age_ouverture_reference is not None:
                break
        requis_reference = requis_reference or 160

        # Trimestres réellement COTISÉS, tous régimes : ils commandent la
        # carrière longue et la majoration du minimum contributif.
        trimestres_cotises = sum(
            carriere.trimestres_retenus(ligne) for ligne in carriere.lignes
            if ligne.cotise and ligne.annee <= annee_liquidation
        )

        # Le droit ouvre-t-il cette liquidation à cet âge ? La question n'était
        # pas posée : le modèle servait une pension décotée à qui ne pouvait
        # pas encore liquider, ce qui n'est ni le droit ni un contrefactuel
        # utile. Elle l'est maintenant, et la réponse accompagne le montant.
        motif_ouverture = "age_legal"
        liquidation_ouverte = True
        if age_ouverture_reference is not None and age_liquidation < age_ouverture_reference:
            anticipe = self.carriere_longue.age_de_depart(
                carriere, annee_liquidation,
                self.carriere_longue.cotises_reputes(
                    carriere, trimestres_cotises,
                    majoration_enfants.trimestres if majoration_enfants is not None else 0,
                ),
                requis_reference,
            )
            if anticipe is not None and age_liquidation >= anticipe[0]:
                motif_ouverture = "carriere_longue"
                age_ouverture_reference = anticipe[0]
                fiabilite_globale = min(fiabilite_globale, anticipe[1])
            else:
                motif_ouverture = "non_ouverte"
                liquidation_ouverte = False

        for code in codes:
            cumul = cumul_cotisations.get(code, 0.0)
            regime = self.catalogue[code]
            periode = regime.periode(min(annee_liquidation, _derniere_annee(regime)))
            if periode is None:
                continue
            fiabilite_globale = min(fiabilite_globale, regime.fiabilite)
            membres = groupes.get(code, (code,))
            if membres[0] != code:
                # Liquidé par le régime qui lui a succédé.
                continue

            if periode.type_calcul in ("points", "mixte"):
                montant = 0.0
                fiabilite_regime = regime.fiabilite
                details = []

                points = points_acquis.get(code, 0.0)
                if points:
                    valeur = self.valeur_du_point(
                        periode.points_de or code, annee_liquidation
                    )
                    if valeur is None and periode.valeur_point_euros is not None:
                        # Valeur de service écrite dans la fiche : le régime
                        # dont la caisse est seule à la publier n'a rien de
                        # certifiable dans `valeurs_point.csv`, et retombait
                        # donc sur le rendement instantané.
                        valeur = (
                            self._valeur_point_fiche(periode, annee_liquidation),
                            Fiabilite.MOYENNE,
                        )
                    if valeur is not None:
                        service, fiabilite_service = valeur
                        # COEFFICIENT DE DURÉE de la proportionnelle agricole :
                        # la pension vaut « points × valeur du point × 37,5 /
                        # durée requise en années ». Il est neutre pour les
                        # générations qui devaient 37,5 ans, et retire un
                        # huitième à celles qui en doivent 43 — sans lui, le
                        # maximum du barème cesse de valoir ce que le code lui
                        # fait valoir.
                        coefficient_duree = 1.0
                        if periode.bareme_points == "msa_proportionnelle":
                            requis, fiabilite_duree = self._duree_requise(
                                periode, carriere
                            )
                            if fiabilite_duree is not None:
                                fiabilite_regime = min(
                                    fiabilite_regime, fiabilite_duree
                                )
                            if requis > 0:
                                coefficient_duree = 37.5 / (requis / 4.0)
                        montant += points * service * coefficient_duree
                        fiabilite_regime = min(
                            fiabilite_regime, fiabilite_service, fiabilite_points[code]
                        )
                        details.append(
                            f"{points:,.2f} points × valeur de service "
                            f"{_sans_zeros_inutiles(service, 6)} €"
                            + ("" if coefficient_duree == 1.0
                               else f" × {coefficient_duree:.4f}")
                        )

                # RÉGIME MIXTE : une part forfaitaire s'ajoute aux points. Le
                # régime agricole en est le seul exemple — sa retraite
                # forfaitaire vaut l'allocation aux vieux travailleurs salariés
                # pour une carrière complète, et se proratise sur la durée
                # (L. 732-24). Le moteur traitait `mixte` comme un synonyme de
                # `points` et ne la servait pas du tout.
                if (periode.type_calcul == "mixte"
                        and periode.pension_forfaitaire_annuelle is not None):
                    requis, _ = self._duree_requise(periode, carriere)
                    proratisation, fiabilite_prorata = self._duree_proratisation(
                        periode, carriere, requis
                    )
                    if fiabilite_prorata is not None:
                        fiabilite_regime = min(fiabilite_regime, fiabilite_prorata)
                    acquis = min(trimestres_par_regime.get(code, 0), proratisation)
                    if proratisation > 0 and acquis > 0:
                        forfait = (
                            periode.pension_forfaitaire_annuelle
                            * self.macro.coefficient_prix(
                                periode.pension_forfaitaire_annee or annee_liquidation,
                                annee_liquidation,
                            )
                            * acquis / proratisation
                        )
                        montant += forfait
                        details.append(
                            f"forfait {forfait:,.2f} € ({acquis}/{proratisation})"
                        )

                # Années sans prix d'achat connu : le rendement instantané prend
                # le relais, régime par régime et année par année.
                if cumul:
                    rendement, fiabilite_rendement = self.rendements.rendement(
                        code, min(annee_liquidation, _derniere_annee(regime))
                    )
                    montant += cumul * rendement
                    fiabilite_regime = min(fiabilite_regime, fiabilite_rendement)
                    details.append(
                        f"cotisations revalorisées {cumul:,.0f} € "
                        f"× rendement {rendement:.2%}"
                    )

                fiabilite_globale = min(fiabilite_globale, fiabilite_regime)
                abattement = 1.0
                if not ignorer_penalite_age:
                    # Le coefficient d'anticipation multiplie le montant : sans
                    # lui, la formule affichée ne le retrouve pas — à dix ans
                    # d'anticipation elle en donnait deux fois trop, sans que
                    # rien à l'écran ne dise pourquoi.
                    abattement = self._abattement_points(
                        periode, carriere, trimestres, requis_reference,
                        age_liquidation, annee_liquidation,
                        trimestres_par_regime.get(code, 0),
                    )
                    montant *= abattement
                pensions.append(PensionRegime(
                    regime=code, montant=montant, type_calcul=periode.type_calcul,
                    detail=_formule_points(details, abattement),
                    fiabilite=fiabilite_regime,
                ))
                continue

            # Régimes en annuités — et régimes FORFAITAIRES, dont la pension ne
            # dépend pas du revenu mais de la seule durée. Le second cas se
            # traite comme le premier en remplaçant le salaire de référence par
            # le montant forfaitaire : c'est bien un `montant × taux × durée /
            # durée requise`, à ceci près que le montant est le même pour tous.
            # Faute de ce montant, la fiche retombait sur la moyenne des
            # revenus, c'est-à-dire sur un taux de remplacement de 100 %.
            plafonner = periode.assiette in ("plafonnee", "tranche_1", "tranche_a")
            if periode.pension_forfaitaire_annuelle is not None:
                salaire_reference = (
                    periode.pension_forfaitaire_annuelle
                    * self.macro.coefficient_prix(
                        periode.pension_forfaitaire_annee or annee_liquidation,
                        annee_liquidation,
                    )
                )
            else:
                salaire_reference = self.salaire_de_reference(
                    code, carriere, periode, annee_liquidation, plafonner,
                    carriere.annee_naissance, avpf, membres,
                    enfants_majores=(carriere.nombre_enfants
                                     if majoration_enfants is not None else 0),
                )
            requis, fiabilite_duree = self._duree_requise(periode, carriere)
            if fiabilite_duree is not None:
                fiabilite_globale = min(fiabilite_globale, fiabilite_duree)
            trimestres_requis = max(trimestres_requis, requis)
            # Le dénominateur de la PRORATISATION n'est pas la durée requise :
            # l'article R. 351-6 en fixe une autre, plus courte pour les
            # générations d'avant 1949. Confondre les deux retirait à un assuré
            # né en 1945 avec 156 trimestres les 2,5 % que 156/160 lui coûte,
            # là où 156/154 lui donne le coefficient plein.
            proratisation, fiabilite_proratisation = self._duree_proratisation(
                periode, carriere, requis
            )
            if fiabilite_proratisation is not None:
                fiabilite_globale = min(fiabilite_globale, fiabilite_proratisation)
            # Le numérateur n'est pas le même selon le régime : services et
            # bonifications dans la fonction publique (L. 13), durée
            # d'assurance partout ailleurs (R. 351-1).
            acquis_par_regime = (
                services_par_regime
                if self.catalogue[code].famille == "fonction_publique"
                else trimestres_par_regime
            )
            trimestres_regime = min(
                sum(acquis_par_regime.get(m, 0) for m in membres), proratisation
            )
            if (periode.duree_maximum_avant_age is not None
                    and periode.duree_maximum_avant_age_trimestres is not None
                    and age_liquidation < periode.duree_maximum_avant_age):
                # DURÉE LIQUIDABLE PLAFONNÉE PAR L'ÂGE. L'article R. 13 du code
                # des pensions de retraite des marins : « le maximum des
                # annuités liquidables dans les pensions d'ancienneté dont la
                # liquidation est demandée avant cinquante-cinq ans est fixé à
                # vingt-cinq annuités ». Un marin parti à cinquante ans avec
                # trente ans de mer touche 50 % du salaire forfaitaire, non
                # 60 %. C'est la seule règle du catalogue où l'ÂGE borne la
                # durée, et non l'inverse.
                # Levé « au profit d'un marin âgé d'au moins cinquante-deux ans
                # et demi, réunissant trente-sept annuités et demie de
                # services » : le même alinéa, b).
                levee = (periode.duree_maximum_levee_age is not None
                         and periode.duree_maximum_levee_trimestres is not None
                         and age_liquidation >= periode.duree_maximum_levee_age
                         and trimestres_regime
                         >= periode.duree_maximum_levee_trimestres)
                if not levee:
                    trimestres_regime = min(
                        trimestres_regime,
                        periode.duree_maximum_avant_age_trimestres,
                    )

            taux = periode.taux_plein or 0.5
            #: Part du taux qui vient de la surcote. Le minimum contributif se
            #: compare à la pension AVANT surcote : il faut donc pouvoir la
            #: retirer, puis la rendre.
            coefficient_surcote = 1.0
            #: Trimestres de décote effectivement retenus : la condition
            #: d'ouverture du minimum garanti en dépend.
            trimestres_decote = 0.0
            if not ignorer_penalite_age:
                decote, age_annulation, fiabilite_decote = self._decote(
                    periode, carriere, annee_liquidation
                )
                trimestres_decote = self._trimestres_de_decote(
                    periode, carriere, trimestres, requis, age_liquidation,
                    age_annulation
                )
                if decote and trimestres_decote > 0:
                    # Les régimes sans décote (fonction publique avant 2004,
                    # régimes spéciaux avant 2008) ne subissent que la
                    # proratisation : leur `decote_par_trimestre` est nul.
                    if fiabilite_decote is not None:
                        fiabilite_globale = min(fiabilite_globale, fiabilite_decote)
                    taux *= max(0.0, 1.0 - decote * trimestres_decote)
                # La surcote ne récompense que les trimestres COTISÉS APRÈS
                # l'âge légal ET au-delà de la durée requise. Les compter tous
                # majorait la pension de qui a commencé tôt sans jamais
                # travailler au-delà de l'âge d'ouverture.
                supplementaires = max(0, trimestres - requis)
                # La surcote se compte depuis l'âge légal DE DROIT COMMUN, même
                # pour un emploi classé, et le militaire n'en a aucune : le III
                # de l'article L. 14 ne la donne qu'au « fonctionnaire civil ».
                age_ouverture = self._age_ouverture_commun(periode, carriere)
                if (periode.surcote_par_trimestre and supplementaires > 0
                        and age_liquidation >= age_ouverture
                        and self._droit_militaire(periode, carriere) is None):
                    if periode.surcote_bareme:
                        # Barème DATÉ : chaque trimestre civil de surcote au
                        # taux en vigueur quand il a été accompli, depuis le
                        # trimestre qui suit l'âge légal (D. 351-1-4).
                        coefficient_surcote, fiabilite_surcote = (
                            self._coefficient_surcote_datee(
                                periode, carriere, trimestres, requis,
                                supplementaires, age_ouverture,
                            )
                        )
                        if fiabilite_surcote is not None:
                            fiabilite_globale = min(fiabilite_globale, fiabilite_surcote)
                    else:
                        supplementaires = min(
                            supplementaires,
                            _trimestres_cotises_apres(
                                carriere, age_ouverture, annee_liquidation
                            ),
                        )
                        if supplementaires > 0:
                            coefficient_surcote = (
                                1.0 + periode.surcote_par_trimestre * supplementaires
                            )
                    taux *= coefficient_surcote

            taux_retenu = max(taux_retenu, taux)
            montant = salaire_reference * taux * (trimestres_regime / proratisation)
            if "minimum_contributif" in periode.avantages_non_contributifs:
                # Le minimum ne relève que les régimes de base qui le portent,
                # et au prorata de la durée acquise DANS CE régime — durée
                # d'assurance pour le montant de base, durée COTISÉE pour la
                # majoration au titre des périodes cotisées.
                #
                # Et il ne relève que les pensions LIQUIDÉES AU TAUX PLEIN
                # (L. 351-10) : durée requise atteinte, ou âge d'annulation de
                # la décote atteint. Le servir à un assuré décoté, comme le
                # faisait ce module, revenait à faire garantir par le système
                # actuel un départ que le droit sanctionne — et gonflait
                # l'étalon de 20 % sur les petites pensions parties tôt.
                # Le minimum se proratise « dans les mêmes conditions que la
                # pension » : c'est donc la durée de proratisation, et non la
                # durée requise, qui fait office ici aussi.
                cotises_regime = min(
                    sum(trimestres_cotises_par_regime.get(m, 0) for m in membres),
                    proratisation,
                )
                eligibles_minimum.append(_EligibleMinimum(
                    indice=len(pensions),
                    prorata_assurance=trimestres_regime / proratisation,
                    prorata_cotise=cotises_regime / proratisation,
                    taux_plein=(
                        trimestres >= requis
                        or age_liquidation >= self._age_taux_plein(periode, carriere)
                    ),
                    surcote=coefficient_surcote,
                ))
            if "minimum_garanti" in periode.avantages_non_contributifs:
                # Depuis la loi du 9 novembre 2010, le minimum garanti n'est dû
                # qu'au taux plein — décote nulle, ou durée requise atteinte.
                # Les assurés qui atteignaient l'âge d'ouverture de leurs
                # droits avant 2011 gardent le droit inconditionnel.
                age_ouverture = self._age_ouverture(periode, carriere)
                eligibles_garanti.append(_EligibleMinimumGaranti(
                    indice=len(pensions),
                    trimestres_services=sum(
                        services_par_regime.get(m, 0) for m in membres
                    ),
                    ouvert=(
                        carriere.annee_naissance + age_ouverture < 2011
                        or trimestres_decote <= 0
                        or trimestres >= requis
                    ),
                ))
            pensions.append(PensionRegime(
                regime=code, montant=montant, type_calcul="annuites",
                detail=(
                    f"{'forfait' if periode.pension_forfaitaire_annuelle is not None else 'SR'} "
                    # Salaire de référence au centime et taux au millième : à
                    # l'euro et au centième, refaire « SR × taux × durée »
                    # ratait le montant de 1,20 € sur un régime spécial, le
                    # taux arrondi pesant à lui seul 0,89 €.
                    f"{salaire_reference:,.2f} € × taux {taux:.3%} "
                    f"× {trimestres_regime}/{proratisation}"
                    # La succession est DITE : sans elle, le lecteur cherche
                    # la ligne de la CANCAVA et ne la trouve pas.
                    + ("" if len(membres) == 1 else
                       f", {len(membres)} caisses liquidées ensemble "
                       f"({', '.join(membres[1:])} puis {membres[0]})")
                ),
                fiabilite=min(self.catalogue[m].fiabilite for m in membres),
            ))

        total = sum(p.montant for p in pensions)

        # CE QUI N'EST PAS DE LA RÉPARTITION EST SERVI À PART. Le RAFP et les
        # anciennes assurances sociales sont des régimes PROVISIONNÉS : leur
        # rente sort d'un placement, pas de la cotisation des actifs. Une
        # réforme qui remplace la répartition par des comptes notionnels ne les
        # atteint pas, et les scénarios notionnels les isolent déjà. Les laisser
        # dans le total du scénario 1 revenait donc à comparer un total qui les
        # contient à quatre totaux qui ne les contiennent pas.
        #
        # Le calcul lui-même n'est pas touché : l'écrêtement du minimum
        # contributif et l'ASPA continuent de regarder TOUTES les pensions,
        # comme le fait le droit. Seul le total rendu est celui de la
        # répartition, et la part écartée est rendue à côté.
        hors_repartition = (
            sum(p.montant for p in pensions
                if self.catalogue[p.regime].hors_repartition)
            if self.parametres.isoler_capitalisation else 0.0
        )
        total_contributif = total - hors_repartition
        avantages: list[AvantageApplique] = []

        # Avantages non contributifs du droit positif, DANS L'ORDRE OÙ LE DROIT
        # LES APPLIQUE, et l'ordre commande le résultat : la majoration de durée
        # d'assurance et l'AVPF d'abord, qui déplacent la décote, la
        # proratisation et le salaire annuel moyen ; puis les deux minima, qui
        # portent la pension de base à son plancher ; puis seulement la
        # majoration pour enfants, qui se calcule SUR CE plancher ; l'ASPA
        # enfin, qui est différentielle et complète tout le reste.
        #
        # Ce module prenait le minimum et la majoration dans l'autre sens : les
        # 10 % portaient sur une pension que le minimum n'avait pas encore
        # relevée, et l'écrêtement du minimum comparait au plafond un total qui
        # incluait déjà la majoration, alors que l'article L. 173-2 ne retient
        # que les pensions personnelles.
        minimum_applique = False

        if avantages_non_contributifs and majoration_enfants is not None:
            # Effet des trimestres accordés au titre des enfants : la même
            # carrière sans eux, tout le reste égal. C'est la seule façon
            # d'isoler un avantage qui agit sur la décote et sur la
            # proratisation.
            sans_mda = self.calculer(
                carriere, ignorer_penalite_age, avantages_non_contributifs=False,
                avpf=avpf, liquider_successions=liquider_successions,
            )
            # Les deux termes doivent porter sur le même périmètre : celui
            # d'en face est déjà net de la capitalisation.
            effet = (total - hors_repartition) - sans_mda.total_contributif
            # Ces trimestres sont déjà incorporés aux pensions de régime : la
            # base contributive de la cascade est celle d'AVANT, sans quoi leur
            # effet serait compté deux fois.
            total_contributif = sans_mda.total_contributif
            if abs(effet) > 1e-9:
                avantages.append(AvantageApplique(
                    code="majoration_duree_assurance",
                    libelle=_LIBELLE_MAJORATION[majoration_enfants.dispositif],
                    montant=effet,
                    detail=f"{majoration_enfants.trimestres} trimestres pour "
                           f"{carriere.nombre_enfants} enfant"
                           f"{'s' if carriere.nombre_enfants > 1 else ''}, "
                           f"au titre du régime « {majoration_enfants.regime} »",
                ))

        if (avantages_non_contributifs and avpf
                and any(ligne.revenu_avpf > 0 for ligne in carriere.lignes)):
            # Effet de l'AVPF, mesuré comme celui de la MDA : la même carrière
            # sans le salaire forfaitaire porté au compte. Il joue en amont de
            # tout le reste, puisqu'il déplace le salaire annuel moyen — et il
            # peut jouer dans les deux sens : il relève une carrière longue à
            # bas salaire, il abaisse la moyenne d'une carrière courte et bien
            # payée, où les années au SMIC viennent s'ajouter aux années
            # retenues au lieu de les remplacer.
            sans_avpf = self.calculer(
                carriere, ignorer_penalite_age,
                avantages_non_contributifs=False, avpf=False,
                liquider_successions=liquider_successions,
            )
            effet_avpf = total_contributif - sans_avpf.total_contributif
            total_contributif = sans_avpf.total_contributif
            if abs(effet_avpf) > 1e-9:
                avantages.insert(0, AvantageApplique(
                    code="avpf",
                    libelle="Assurance vieillesse des parents au foyer",
                    montant=effet_avpf,
                    detail="salaire forfaitaire au SMIC porté au compte",
                ))

        if avantages_non_contributifs and eligibles_minimum:
            # Le minimum contributif ne relève que les pensions liquidées AU
            # TAUX PLEIN (L. 351-10). Sa majoration au titre des périodes
            # cotisées demande en outre 120 trimestres cotisés tous régimes ;
            # elle se proratise sur la durée COTISÉE dans le régime, quand le
            # montant de base se proratise sur sa durée d'assurance
            # (D. 351-2-2). Ce n'est pas la même fraction : une carrière
            # entrecoupée de chômage indemnisé valide sa durée d'assurance
            # sans cotiser, et n'a donc droit qu'à une part de la majoration.
            montant_base, montant_majore, plafond, fiabilite_minimum = (
                self.minimum_contributif.valeurs(annee_liquidation)
            )
            majoration_ouverte = (
                trimestres_cotises >= TRIMESTRES_COTISES_MINIMUM_MAJORE
            )
            #: Complément dû à chaque régime, avant écrêtement.
            complements: dict[int, float] = {}
            for eligible in eligibles_minimum:
                if not eligible.taux_plein:
                    continue
                pension = pensions[eligible.indice]
                # Le minimum se compare à la pension AVANT surcote : le droit
                # porte la pension au plancher, puis applique la surcote au
                # montant relevé. Comparer une pension déjà surcotée au
                # plancher refusait le minimum à qui a travaillé plus
                # longtemps que la durée requise pour un salaire minime.
                nue = pension.montant / eligible.surcote
                plancher = montant_base * min(1.0, eligible.prorata_assurance)
                if majoration_ouverte:
                    plancher += (montant_majore - montant_base) * min(
                        1.0, eligible.prorata_cotise
                    )
                if 0 < nue < plancher:
                    complements[eligible.indice] = (
                        (plancher - nue) * eligible.surcote
                    )
            releve = sum(complements.values())
            if releve > 0:
                # Écrêtement de l'article L. 173-2 : le complément est rogné de
                # ce qui dépasse le plafond, tous régimes confondus, et jamais
                # au-delà. La comparaison porte sur les pensions PERSONNELLES,
                # majorations pour enfants exclues — raison de plus pour que
                # celles-ci se calculent après, sur le montant relevé.
                admissible = max(0.0, min(releve, plafond - total))
                if admissible < releve:
                    facteur = admissible / releve
                    complements = {
                        indice: complement * facteur
                        for indice, complement in complements.items()
                    }
                releve = admissible
            if releve > 0:
                for indice, complement in complements.items():
                    # Le complément est DIT, pas seulement annoncé : sans lui,
                    # refaire la formule donnait la pension d'avant le minimum
                    # et l'écart restait inexpliqué — deux mille euros par an
                    # sur une petite retraite, ce qui n'est pas un détail.
                    pensions[indice] = replace(
                        pensions[indice],
                        montant=pensions[indice].montant + complement,
                        detail=(
                            f"{pensions[indice].detail} = "
                            f"{pensions[indice].montant:,.2f} €, porté au minimum "
                            f"contributif par + {complement:,.2f} €"
                        ),
                    )
                total += releve
                minimum_applique = True
                fiabilite_globale = min(fiabilite_globale, fiabilite_minimum)
                avantages.append(AvantageApplique(
                    code="minimum_contributif",
                    libelle="Minimum contributif",
                    montant=releve,
                    detail=(
                        "porté au plancher, au prorata de la durée acquise"
                        + (", majoration des périodes cotisées comprise"
                           if majoration_ouverte else "")
                    ),
                ))

        if avantages_non_contributifs and eligibles_garanti:
            # Le minimum garanti n'est pas un minimum proratisé mais un BARÈME
            # sur la durée de services : quinze ans en ouvrent 57,5 % de la
            # référence, trente ans 95 %, quarante ans la totalité. Il ne
            # s'ajoute pas à la pension, il s'y substitue quand il lui est
            # supérieur.
            releve_garanti = 0.0
            for eligible in eligibles_garanti:
                if not eligible.ouvert:
                    continue
                plancher = self.minimum_garanti.montant(
                    annee_liquidation, eligible.trimestres_services
                )
                if plancher is None:
                    continue
                pension = pensions[eligible.indice]
                if 0 < pension.montant < plancher[0]:
                    complement = plancher[0] - pension.montant
                    releve_garanti += complement
                    fiabilite_globale = min(fiabilite_globale, plancher[1])
                    # Le complément est DIT, comme pour le minimum contributif :
                    # sans lui, refaire la formule donnait la pension d'avant le
                    # plancher, et l'écart restait sans explication.
                    pensions[eligible.indice] = replace(
                        pension,
                        montant=plancher[0],
                        detail=(f"{pension.detail} = {pension.montant:,.2f} €, "
                                f"porté au minimum garanti par + {complement:,.2f} €"),
                    )
            if releve_garanti > 0:
                total += releve_garanti
                avantages.append(AvantageApplique(
                    code="minimum_garanti",
                    libelle="Minimum garanti de la fonction publique",
                    montant=releve_garanti,
                    detail="barème de l'article L. 17, sur la durée de services",
                ))

        # Surcote parentale (L. 351-1-2-1) : elle vient APRÈS les minima,
        # comme la surcote ordinaire, et AVANT la majoration pour enfants, qui
        # se calcule sur la pension surcotée. Elle ne récompense pas les mêmes
        # trimestres que la surcote ordinaire — celle-ci ne compte qu'au-delà
        # de l'âge légal, celle-là entre 63 ans et l'âge légal — et les deux se
        # cumulent donc sans se recouvrir.
        parametres_parentale = (
            self.surcote_parentale.parametres(annee_liquidation)
            if (avantages_non_contributifs and majoration_enfants is not None
                and not ignorer_penalite_age)
            else None
        )
        if parametres_parentale is not None:
            age_parental, taux_parental, maximum, fiabilite_parentale = (
                parametres_parentale
            )
            gain_parental = 0.0
            trimestres_parentaux = 0
            for indice, pension in enumerate(pensions):
                regime = self.catalogue[pension.regime]
                periode = regime.periode(
                    min(annee_liquidation, _derniere_annee(regime))
                )
                if (periode is None or "surcote_parentale"
                        not in periode.avantages_non_contributifs):
                    continue
                age_legal = self._age_ouverture(periode, carriere)
                requis = self._duree_requise(periode, carriere)[0]
                # La durée s'apprécie À 63 ANS, trimestres pour enfants
                # compris : c'est bien la durée qu'oppose la loi, et l'assuré
                # les détient déjà à cet âge.
                acquis = majoration_enfants.trimestres + _trimestres_valides_avant(
                    carriere, age_parental, annee_liquidation
                )
                if requis <= 0 or acquis < requis:
                    continue
                # La fenêtre ne dure quatre trimestres que si l'âge légal est
                # de 64 ans : la génération 1965, dont l'âge légal est de
                # 63 ans et trois mois, n'en a qu'un à faire valoir. Le modèle
                # ne date pas les trimestres au jour, et lui en compterait
                # quatre — d'où ce plafond, qui est la largeur de la fenêtre.
                fenetre = round((age_legal - age_parental) * 4)
                # Surtout pas `trimestres` : c'est la durée d'assurance tous
                # régimes, et l'écraser ici la faisait tomber à quatre.
                acquis_parentaux = min(maximum, fenetre, _trimestres_cotises_entre(
                    carriere, age_parental, age_legal, annee_liquidation
                ))
                if acquis_parentaux <= 0:
                    continue
                supplement = pension.montant * taux_parental * acquis_parentaux
                pensions[indice] = replace(
                    pension,
                    montant=pension.montant + supplement,
                    detail=(pension.detail + ", surcote parentale "
                            f"{taux_parental * acquis_parentaux:.2%}"),
                )
                gain_parental += supplement
                trimestres_parentaux = max(trimestres_parentaux, acquis_parentaux)
            if gain_parental > 0:
                total += gain_parental
                fiabilite_globale = min(fiabilite_globale, fiabilite_parentale)
                avantages.append(AvantageApplique(
                    code="surcote_parentale",
                    libelle="Surcote parentale",
                    montant=gain_parental,
                    detail=(f"{taux_parental * trimestres_parentaux:.2%} pour "
                            f"{trimestres_parentaux} trimestre"
                            f"{'s' if trimestres_parentaux > 1 else ''} entre "
                            f"{age_parental:g} ans et l'âge légal"),
                ))

        if avantages_non_contributifs and carriere.nombre_enfants >= 2:
            majoration = 0.0
            taux_cite = 0.0
            # Le plafond de l'Agirc-Arrco s'oppose à la majoration de LA
            # complémentaire, pas à celle de chacune de ses fiches : les points
            # d'un salarié du privé sont répartis entre l'Agirc, l'Arrco et le
            # régime unifié, et plafonner chacun séparément reviendrait à
            # tripler le plafond. On les met donc dans un même seau.
            majoration_plafonnee = 0.0
            plafond_commun: float | None = None
            for pension in pensions:
                regime = self.catalogue[pension.regime]
                periode = regime.periode(min(annee_liquidation, _derniere_annee(regime)))
                if periode is None:
                    continue
                if "majoration_enfants" not in periode.avantages_non_contributifs:
                    continue
                taux = _taux_majoration_enfants(regime, carriere.nombre_enfants,
                                                periode)
                if taux <= 0:
                    continue
                part = pension.montant * taux
                plafond = self._plafond_majoration(
                    pension.regime, periode, carriere, annee_liquidation
                )
                if plafond is None:
                    majoration += part
                else:
                    majoration_plafonnee += part
                    plafond_commun = (plafond if plafond_commun is None
                                      else max(plafond_commun, plafond))
                taux_cite = max(taux_cite, taux)
            plafonnee = plafond_commun is not None
            if plafond_commun is not None:
                majoration += min(majoration_plafonnee, plafond_commun)
            if majoration > 0:
                total += majoration
                detail = f"jusqu'à {taux_cite:.0%} selon le régime"
                if plafonnee:
                    detail += ", plafonnée en euros à la complémentaire"
                avantages.append(AvantageApplique(
                    code="majoration_enfants",
                    libelle=("Majoration pour trois enfants et plus"
                             if carriere.nombre_enfants >= 3
                             else "Bonification pour deux enfants"),
                    montant=majoration,
                    detail=detail,
                ))

        if (avantages_non_contributifs
                and self.parametres.minimum_vieillesse_dans_le_scenario_actuel
                and age_liquidation >= MinimumVieillesse.AGE_OUVERTURE):
            # L'ASPA vient en DERNIER, et pour cause : elle est différentielle.
            # Elle complète tout le reste, majorations comprises, jusqu'au
            # montant du barème — c'est la seule prestation du système actuel
            # qui ne suppose aucune cotisation, et donc celle qui creuse le
            # plus l'écart avec un compte notionnel.
            barème = self.minimum_vieillesse.plafond(annee_liquidation)
            if barème is not None and total < barème[0]:
                complement = barème[0] - total
                total = barème[0]
                fiabilite_globale = min(fiabilite_globale, barème[1])
                avantages.append(AvantageApplique(
                    code="minimum_vieillesse",
                    libelle="Minimum vieillesse (ASPA)",
                    montant=complement,
                    detail="allocation différentielle, barème d'une personne seule",
                ))

        return ResultatActuel(
            pension_annuelle=max(0.0, total - hors_repartition),
            pension_hors_repartition=hors_repartition,
            pensions_par_regime=pensions,
            avantages_appliques=avantages,
            total_contributif=total_contributif,
            trimestres_valides=trimestres,
            trimestres_requis=trimestres_requis,
            taux_liquidation=taux_retenu,
            minimum_applique=minimum_applique,
            age_ouverture_opposable=age_ouverture_reference,
            liquidation_ouverte=liquidation_ouverte,
            motif_ouverture=motif_ouverture,
            fiabilite=fiabilite_globale,
        )


def _taux_majoration_enfants(regime, nombre_enfants: int,
                             periode: PeriodeRegime | None = None) -> float:
    """Taux de majoration pour enfants, régime par régime.

    Le régime général et les régimes spéciaux servent 10 % à partir de trois
    enfants. La fonction publique y ajoute 5 % par enfant au-delà du troisième.
    Les complémentaires servent 10 % aussi, mais plafonnés en euros : le taux
    est le même, c'est :meth:`ScenarioActuel._plafond_majoration` qui borne.
    Une fiche qui porte son propre barème — les marins, qui bonifient dès deux
    enfants — l'emporte.
    """
    if periode is not None and periode.taux_majoration_enfants:
        bareme = periode.taux_majoration_enfants
        return bareme[min(nombre_enfants, len(bareme) - 1)]
    if nombre_enfants < 3:
        return 0.0
    if regime.famille == "fonction_publique":
        return 0.10 + 0.05 * (nombre_enfants - 3)
    return 0.10


def _trimestres_cotises_apres(carriere: Carriere, age: float,
                              annee_liquidation: int) -> int:
    """Trimestres cotisés à partir de l'année où l'assuré atteint ``age``.

    Seuls ceux-là ouvrent droit à la surcote : c'est une récompense du travail
    prolongé, pas de l'entrée précoce dans la vie active.
    """
    return sum(
        carriere.trimestres_retenus(ligne)
        for ligne in carriere.lignes
        if ligne.cotise
        and ligne.annee <= annee_liquidation
        and ligne.annee - carriere.annee_naissance >= age
    )


def _trimestres_valides_avant(carriere: Carriere, age: float,
                              annee_liquidation: int) -> int:
    """Durée d'assurance acquise avant l'année où l'assuré atteint ``age``.

    Périodes assimilées comprises : c'est la durée d'assurance qu'oppose la
    condition de taux plein, et non la seule durée cotisée.
    """
    return sum(
        carriere.trimestres_retenus(ligne)
        for ligne in carriere.lignes
        if ligne.annee <= annee_liquidation
        and ligne.annee - carriere.annee_naissance < age
    )


def _trimestres_cotises_entre(carriere: Carriere, age_bas: float, age_haut: float,
                              annee_liquidation: int) -> int:
    """Trimestres cotisés entre deux âges — bas inclus, haut exclu.

    C'est la fenêtre qu'ouvre la surcote parentale : entre 63 ans et l'âge
    légal, là où la surcote ordinaire ne compte encore rien.
    """
    return sum(
        carriere.trimestres_retenus(ligne)
        for ligne in carriere.lignes
        if ligne.cotise
        and ligne.annee <= annee_liquidation
        and age_bas <= ligne.annee - carriere.annee_naissance < age_haut
    )


def _assiette_de_reference(periode: PeriodeRegime, ligne) -> float:
    """Part de la rémunération que ce régime prend en compte.

    Même découpage que dans la boucle de cotisation : un régime qui ne cotise
    que sur le traitement indiciaire ne peut pas liquider sur la rémunération
    primes comprises, sans quoi les primes ouvriraient deux fois des droits —
    au RAFP et à la pension civile — alors qu'elles n'en ouvrent qu'au RAFP.
    """
    if periode.assiette == "primes_uniquement":
        return ligne.revenu * ligne.part_primes
    if periode.assiette == "hors_primes":
        return ligne.revenu * (1.0 - ligne.part_primes)
    return ligne.revenu


def _derniere_annee(regime) -> int:
    """Dernière année pour laquelle le régime a des paramètres."""
    annees = [p.fin if p.fin is not None else 9999 for p in regime.periodes]
    return min(max(annees), 2100) if annees else 2100


#: Durée cotisée, tous régimes, qui ouvre la majoration du minimum contributif
#: au titre des périodes cotisées (article L. 351-10 du code de la sécurité
#: sociale). En deçà, seul le montant de base est dû.
TRIMESTRES_COTISES_MINIMUM_MAJORE = 120

#: Année à partir de laquelle chaque montant suit le SMIC et non plus les prix.
#: Le plafond d'écrêtement bascule avec le décret du 14 février 2014, qui le
#: revalorise « aux mêmes dates et dans les mêmes proportions que le salaire
#: minimum de croissance » (D. 173-21-0-0-1) ; les deux minima basculent avec
#: la réforme du 14 avril 2023. Avant ces dates, ils suivaient les prix, comme
#: les pensions.
INDEXATION_SUR_LE_SMIC = {
    "montant_base": 2023,
    "montant_majore": 2023,
    "plafond_ecretement": 2014,
}


class MinimumContributif:
    """Minimum contributif, minimum majoré et plafond d'écrêtement.

    Trois grandeurs, et pas une seule :

    * le **minimum**, auquel est portée la pension de base d'un assuré au taux
      plein, au prorata de sa durée dans le régime ;
    * le **minimum majoré**, servi à sa place quand la durée COTISÉE atteint la
      durée requise — près d'un cinquième au-dessus du premier ;
    * le **plafond d'écrêtement** de l'article L. 173-2 : le complément est
      rogné dès que l'ensemble des pensions dépasse ce total. Sans cette
      condition, le modèle servait le minimum à des assurés que leurs régimes
      complémentaires placent déjà bien au-dessus.

    Les trois sont des **ancres datées**, lues dans le code de la sécurité
    sociale (D. 351-2-1 et D. 173-21-0-0-1) et non dans une série annuelle : le
    code n'est pas modifié chaque année, les montants sont revalorisés par
    l'effet de la loi. C'est donc au modèle de le faire, et sur le bon index —
    **le SMIC** à partir de la date d'effet, les prix avant elle. Les
    revaloriser sur les prix comme le faisait ce module les décrochait d'autant
    que le SMIC a progressé plus vite.
    """

    def __init__(self, racine: Path, macro: DonneesMacro) -> None:
        self.macro = macro
        self._table: dict[tuple[str, int], tuple[float, Fiabilite]] = {}
        chemin = racine / "reference" / "legislation" / "minimum_contributif.csv"
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                self._table[(ligne["mesure"], int(ligne["annee"]))] = (
                    float(ligne["valeur"]),
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                )

    def _revalorise(self, mesure: str, annee: int) -> tuple[float, Fiabilite]:
        """Ancre de la mesure, portée à l'année demandée.

        **Un montant connu passe avant tout calcul.** Quand l'année demandée
        figure au fichier, on la sert telle quelle : c'est ce que les caisses
        ont payé, et aucune projection ne vaut mieux que cela.

        Sinon, on projette depuis la valeur EN VIGUEUR à cette date — la
        dernière fixée avant elle, jamais une postérieure. Ramener une valeur
        postérieure en arrière ferait glisser dans le passé les marches que la
        loi a créées : la réforme de 2023 a relevé le minimum majoré de plus de
        30 %, et l'appliquer à 2020 le surestimait de 7,6 % par rapport au
        montant que l'État a lui-même rappelé.

        L'index de la projection ne dépend pas de l'ancre mais de l'ANNÉE
        TRAVERSÉE : les prix jusqu'à la bascule que la loi a fixée pour cette
        grandeur, le SMIC ensuite. Un montant ancré en 2007 et lu en 2015 se
        revalorise donc sur les prix, règle d'alors, quand le même ancré en
        2023 et lu en 2025 se revalorise sur le SMIC.
        """
        ancres = sorted(a for (m, a) in self._table if m == mesure)
        if not ancres:
            return 0.0, Fiabilite.ESTIMEE
        if annee in ancres:
            return self._table[(mesure, annee)]
        anterieures = [a for a in ancres if a < annee]
        reference = max(anterieures) if anterieures else ancres[0]
        valeur, fiabilite = self._table[(mesure, reference)]

        bascule = INDEXATION_SUR_LE_SMIC[mesure]
        pivot = min(max(reference, bascule), annee)
        coefficient = (self.macro.coefficient_prix(reference, pivot)
                       * self.macro.coefficient_smic(pivot, annee))
        return valeur * coefficient, fiabilite

    def valeurs(self, annee: int) -> tuple[float, float, float, Fiabilite]:
        """Montant de base, montant majoré et plafond d'écrêtement de l'année.

        Les deux montants sont rendus ensemble parce que le droit les additionne
        plutôt qu'il ne choisit entre eux : la pension est portée au montant de
        BASE au prorata de la durée d'assurance acquise dans le régime, puis
        l'écart entre le majoré et le base s'y ajoute au prorata de la seule
        durée COTISÉE. Servir l'un OU l'autre, comme le faisait ce module,
        donnait le montant plein de la majoration à qui n'a cotisé qu'une part
        de sa durée, et rien du tout à qui lui manque un trimestre.
        """
        if not self._table:
            return 0.0, 0.0, 0.0, Fiabilite.ESTIMEE
        base, fiabilite_base = self._revalorise("montant_base", annee)
        majore, fiabilite_majore = self._revalorise("montant_majore", annee)
        plafond, fiabilite_plafond = self._revalorise("plafond_ecretement", annee)
        return base, majore, plafond, min(
            fiabilite_base, fiabilite_majore, fiabilite_plafond
        )
