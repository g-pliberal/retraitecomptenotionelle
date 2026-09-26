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
  rendement instantané (``regimes/rendements_points.csv``) les complémentaires
  des sections libérales et de l'IRCEC, dont les caisses publient un rendement
  ou un barème annuel mais aucune série de prix d'achat, quelques petits
  régimes — CAFAT, tranche B de la Polynésie, additionnel des enseignants du
  privé, gérants de débits de tabac, conjoints du bâtiment —, et, pour tous,
  les années postérieures au dernier barème publié ;
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

Où est le calcul
----------------
Ce module garde les TABLES du droit en vigueur, et le moteur qui les tient,
:class:`ScenarioActuel`. Le calcul est dans ``droit/`` (docs/architecture.md,
§ 7.2 et 7.3) : l'acquisition construit le relevé des droits, puis
:func:`~retraite_notionnelle.droit.liquidation.liquider`, une fonction pure,
ouvre le droit, liquide chaque régime et complète tous régimes ; l'ASPA vient
ensuite, de l'étape « foyer et net ». :meth:`ScenarioActuel.calculer` les
enchaîne. Les fiches et leurs versions remplaceront les tables (phase 6).
"""

from __future__ import annotations

import csv
from bisect import bisect_right
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from ..carriere import Affiliations, Carriere
from ..config import Parametres
from ..donnees.chargement import (
    Fiabilite,
    charger_table_par_generation,
    valeur_par_generation,
)
from ..donnees.macro import DonneesMacro
from ..donnees.regimes import CatalogueRegimes, ClassesCotisation, SalairesForfaitaires
from ..droit import coordonner
from ..droit import foyer as _foyer
from ..droit import liquidation as _liquidation
# Ce que les étapes créent, que les appelants du scénario 1 lisent ici.
from ..droit.commun import AvantageApplique, PensionRegime  # noqa: F401
from ..revalorisation import RevalorisationsPensions

if TYPE_CHECKING:
    from ..droit.foyer import Foyer
    from ..droit.liquidation import Liquidation


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


def resultat_actuel(liquidation: Liquidation, foyer: Foyer) -> ResultatActuel:
    """Le scénario 1 à une date d'effet : la liquidation, puis ce que l'étape
    « foyer et net » y ajoute — l'ASPA, qui complète tout le reste,
    majorations comprises, jusqu'au montant du barème."""
    total = liquidation.total
    avantages = list(liquidation.avantages)
    fiabilite = liquidation.fiabilite
    if foyer.minimum_vieillesse > 0:
        total = foyer.plafond
        fiabilite = min(fiabilite, foyer.fiabilite)
        avantages.append(foyer.avantage())
    return ResultatActuel(
        pension_annuelle=max(0.0, total - liquidation.hors_repartition),
        pension_hors_repartition=liquidation.hors_repartition,
        pensions_par_regime=list(liquidation.regimes),
        avantages_appliques=avantages,
        total_contributif=liquidation.total_contributif,
        trimestres_valides=liquidation.releve.durees.trimestres,
        trimestres_requis=liquidation.pensions.requis,
        taux_liquidation=liquidation.pensions.taux,
        minimum_applique=liquidation.complements.minimum_applique,
        age_ouverture_opposable=liquidation.ouverture.age,
        liquidation_ouverte=liquidation.ouverture.ouverte,
        motif_ouverture=liquidation.ouverture.motif,
        fiabilite=fiabilite,
    )


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


class DureesRequisesAvantSuspension(DureesRequises):
    """Durée requise que la suspension de 2026 remplace, pour les pensions
    prenant effet avant le 1er septembre 2026 : 171 trimestres pour les nés en
    1964, 172 pour ceux de 1965 (loi n° 2025-1403, article 105 VI ; circulaire
    Cnav 2026-07, point 2.1). Voir ``duree_requise_avant_suspension.csv``."""

    def __init__(self, racine: Path) -> None:
        TableParGeneration.__init__(
            self, racine, "duree_requise_avant_suspension.csv", "trimestres")


class DureesRequisesAvantReforme2023(DureesRequises):
    """Durée requise que la loi du 14 avril 2023 a relevée, pour les pensions
    prenant effet avant le 1er septembre 2023 : L. 161-17-3 dans sa version du
    22 janvier 2014 — 168 trimestres pour les nés de 1961 à 1963, 169 de 1964
    à 1966 (B du XXX de l'article 10 de la loi n° 2023-270 ; circulaire Cnav
    2023/19, point 2). Voir ``duree_requise_avant_reforme_2023.csv``."""

    def __init__(self, racine: Path) -> None:
        TableParGeneration.__init__(
            self, racine, "duree_requise_avant_reforme_2023.csv", "trimestres")


def _rang_mois(texte: str) -> int:
    """« AAAA-MM » -> rang absolu du mois, celui de :class:`DateMois`."""
    annee, mois = texte.strip().split("-")
    return DateMois(int(annee), int(mois)).rang


class DureesRequisesRegimes:
    """Durée requise propre à un régime spécial, par génération.

    La SNCF, la RATP et les IEG écrivent chacune leur table dans leur texte, et
    la suspension de 2026, qui a abaissé la table commune, ne les a pas
    touchées. Une table ne vaut qu'à compter de la date où l'assuré RÉUNIT LES
    CONDITIONS — colonne `depuis` : le 1er juillet 2019 pour les tables de 2014,
    le 1er janvier 2025 pour celles de 2023, dont les décrets gardent « les
    règles applicables avant » à qui les a réunies plus tôt. La fiche nomme les
    siennes (`duree_requise_table`), essayées dans l'ordre.

    La table de la SNCF porte en plus ce que le II de l'article 35 du décret
    n° 2008-639 retranche à la durée requise pour compter la décote par la
    durée — jusqu'à dix trimestres pour un agent de conduite né en 1980.
    """

    FICHIER = "duree_requise_regimes_speciaux.csv"

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, dict[float, tuple[int, int, Fiabilite]]] = {}
        self._depuis: dict[str, int] = {}
        chemin = racine / "reference" / "legislation" / self.FICHIER
        if chemin.exists():
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    self._table.setdefault(ligne["table"], {})[
                        float(ligne["generation"])
                    ] = (int(ligne["trimestres"]), int(ligne["retranche_decote"]),
                         Fiabilite.depuis_texte(ligne["fiabilite"]))
                    self._depuis[ligne["table"]] = _rang_mois(ligne["depuis"])
        self._generations = {cle: tuple(sorted(valeurs))
                             for cle, valeurs in self._table.items()}

    def ligne(self, table: str, generation: float,
              ouverture: int) -> tuple[int, int, Fiabilite] | None:
        """Trimestres requis, trimestres retranchés pour la décote, fiabilité.

        ``ouverture`` est le rang du mois où l'assuré réunit les conditions ;
        avant la date d'effet de la table, elle ne répond pas.
        """
        generations = self._generations.get(table)
        if not generations or ouverture < self._depuis[table]:
            return None
        return valeur_par_generation(self._table[table], generations, generation)


class CalendriersDureeRequise:
    """Durée requise lue à la DATE où l'assuré réunit les conditions.

    La réforme de 2008 des régimes spéciaux ne suit pas la génération : 151
    trimestres pour qui réunit les conditions au second semestre 2008, un de
    plus au 1er janvier et au 1er juillet jusqu'en juillet 2012, un au
    1er décembre 2012, puis un chaque 1er juillet jusqu'à 166 en 2018 ; 150
    avant. C'est le calendrier que les fiches de la SNCF, de la RATP et des IEG
    nomment (`duree_requise_calendrier`), et celui qui vaut pour leurs
    retraités de 2008 à 2024.
    """

    FICHIER = "duree_requise_calendriers.csv"

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, list[tuple[int, int, Fiabilite]]] = {}
        chemin = racine / "reference" / "legislation" / self.FICHIER
        if chemin.exists():
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    self._table.setdefault(ligne["calendrier"], []).append(
                        (_rang_mois(ligne["depuis"]), int(ligne["trimestres"]),
                         Fiabilite.depuis_texte(ligne["fiabilite"])))
        for valeurs in self._table.values():
            valeurs.sort()

    def trimestres(self, calendrier: str,
                   ouverture: int) -> tuple[int, Fiabilite] | None:
        retenue = None
        for depuis, trimestres, fiabilite in self._table.get(calendrier, ()):
            if depuis > ouverture:
                break
            retenue = (trimestres, fiabilite)
        return retenue


def _age_ou_rien(texte: str | None) -> float | None:
    """Un âge de ``ages_regimes.csv``, ou ``None`` quand la case est vide."""
    texte = (texte or "").strip()
    return float(texte) if texte else None


class AgesRegimes:
    """Âges PROPRES à un régime, par génération : ouverture et taux plein.

    Le règlement d'une section libérale écrit souvent ses âges en toutes
    lettres, génération par génération, et ce ne sont pas ceux du régime
    général. Celui de la CAVOM (arrêté du 10 juillet 2026) ouvre la retraite
    complémentaire à soixante ans aux nés avant 1956 et la sert à taux plein à
    soixante-cinq, monte de six mois par génération jusqu'à 62 et 67 ans pour
    celle de 1959, puis de six mois encore de 1965 à 1968 — sans rien devoir
    à la suspension de 2026. La fiche nomme sa table (``age_table``) ; la
    lecture est en escalier, comme celle des tables communes.

    **La table peut aussi porter le coefficient de minoration**, quand le
    règlement le fait dépendre de la génération : la CARCDSF minorait de
    1,50 % par trimestre les nés depuis 1955 et de 5 % par année ceux d'avant
    juillet 1951 (statuts approuvés le 13 avril 2011, bornes de l'arrêté du
    9 juillet 2012). Colonne vide : le taux de la fiche.
    """

    FICHIER = "ages_regimes.csv"

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, dict[float, tuple[float, float, Fiabilite]]] = {}
        self._decotes: dict[str, dict[float, float | None]] = {}
        chemin = racine / "reference" / "legislation" / self.FICHIER
        if chemin.exists():
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    generation = float(ligne["generation"])
                    self._table.setdefault(ligne["table"], {})[generation] = (
                        _age_ou_rien(ligne["age_ouverture"]),
                        _age_ou_rien(ligne["age_taux_plein"]),
                        Fiabilite.depuis_texte(ligne["fiabilite"]),
                    )
                    decote = (ligne.get("decote_par_trimestre") or "").strip()
                    self._decotes.setdefault(ligne["table"], {})[generation] = (
                        float(decote) if decote else None
                    )
        self._generations = {cle: tuple(sorted(valeurs))
                             for cle, valeurs in self._table.items()}

    def ages(self, table: str, generation: float
             ) -> tuple[float | None, float | None, Fiabilite] | None:
        """Âge d'ouverture, âge du taux plein, fiabilité ; ``None`` hors table.

        Un âge laissé vide dans la table vaut ``None`` : le règlement renvoie
        alors à l'âge de droit commun, que les tables communes portent déjà —
        la CAVP ouvre sa complémentaire à l'âge de L. 161-17-2 et n'écrit en
        propre que l'âge de son taux plein.
        """
        generations = self._generations.get(table)
        if not generations:
            return None
        return valeur_par_generation(self._table[table], generations, generation)

    def decote(self, table: str,
               generation: float) -> tuple[float, Fiabilite] | None:
        """Coefficient de minoration par trimestre que la table écrit pour
        cette génération, et sa fiabilité ; ``None`` si la ligne n'en porte
        pas, et la fiche garde alors le sien."""
        generations = self._generations.get(table)
        if not generations or generation < generations[0]:
            return None
        rang = bisect_right(generations, generation)
        cle = generations[rang - 1]
        decote = self._decotes[table].get(cle)
        if decote is None:
            return None
        return decote, self._table[table][cle][2]


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


class DureesRequisesAvantSoixanteAns:
    """Durée requise d'un fonctionnaire dont le droit s'ouvre avant 60 ans.

    Ce n'est pas celle de sa génération mais celle « exigée des fonctionnaires
    atteignant [soixante ans] l'année à compter de laquelle la liquidation peut
    intervenir » : article 5, VI, de la loi du 21 août 2003, puis article
    L. 13, III, du code des pensions, que le XXIV de l'article 10 de la loi du
    14 avril 2023 garde en vigueur par renvoi. Deux règles, que la table
    distingue :

    * ``l13_iii`` — la clé est l'ANNÉE d'ouverture, de 2009 à 2033 ; au-delà,
      la dernière ligne vaut. Avant 2009, la fiche et la table de 2004-2008
      répondent, et celle-ci rend ``None`` ;
    * ``xxiv_c`` — les militaires qui peuvent liquider à compter du
      1er septembre 2023 (XXIV, C, 2°) : une marche par date d'ouverture.

    Le tableau n° 20 du rapport de la Cour des comptes de septembre 2026 sur
    les retraites des fonctionnaires de l'État rejoue la première règle.
    """

    FICHIER = "duree_requise_avant_soixante_ans.csv"

    def __init__(self, racine: Path) -> None:
        # Clé : le rang du mois (``DateMois.rang``), pour qu'une année
        # décimale écrite au millième — 2023.667, septembre — ne tombe pas à
        # côté de la date qu'elle nomme.
        self._table: dict[str, dict[int, tuple[int, Fiabilite]]] = {}
        chemin = racine / "reference" / "legislation" / self.FICHIER
        if chemin.exists():
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    self._table.setdefault(ligne["regle"], {})[
                        round(float(ligne["annee_ouverture"]) * 12)
                    ] = (int(ligne["trimestres"]),
                         Fiabilite.depuis_texte(ligne["fiabilite"]))
        self._cles = {regle: sorted(valeurs)
                      for regle, valeurs in self._table.items()}

    def _marche(self, regle: str, rang: int) -> tuple[int, Fiabilite] | None:
        cles = self._cles.get(regle)
        if not cles or rang < cles[0]:
            return None
        retenue = cles[0]
        for candidate in cles:
            if candidate > rang:
                break
            retenue = candidate
        return self._table[regle][retenue]

    def par_annee(self, annee_ouverture: int) -> tuple[int, Fiabilite] | None:
        """Règle de L. 13, III : la génération qui a soixante ans cette année."""
        return self._marche("l13_iii", DateMois(annee_ouverture, 1).rang)

    def depuis_2023(self, ouverture: DateMois) -> tuple[int, Fiabilite] | None:
        """Règle du XXIV, C, 2° : ``None`` avant le 1er septembre 2023."""
        return self._marche("xxiv_c", ouverture.rang)


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


class AgesSurcoteRegimesSpeciaux(TableParGeneration):
    """Âge d'où la SNCF et la RATP comptent la surcote, par génération.

    Ce n'est ni leur âge d'ouverture ni l'âge légal du régime général : c'est
    l'âge légal décalé de cinq générations, soixante-quatre ans à compter de la
    génération 1970 (décret n° 2008-639, article 37-1, IV ; décret
    n° 2008-637, article 51-1, II, 3°).
    """

    def __init__(self, racine: Path) -> None:
        super().__init__(racine, "age_surcote_regimes_speciaux.csv", "age")

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
    #: avant les marches de 2023 (septembre 1966, septembre 1971) : la durée
    #: est alors celle de l'année d'ouverture du droit, que
    #: ``DureesRequisesAvantSoixanteAns`` porte.
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

    def par_enfant(self, dispositif: str, sexe: str, naissance_des_enfants: int,
                   annee_liquidation: int,
                   nombre_enfants: int) -> tuple[int, int, Fiabilite] | None:
        """Trimestres accordés PAR ENFANT, dont ceux qui comptent en SERVICES.

        ``naissance_des_enfants`` est l'année où ils naissent, telle que la
        chronologie la porte (:attr:`Carriere.annee_naissance_des_enfants`) :
        présumée aux trente ans de la mère tant que rien n'est déclaré.

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
                     else naissance_des_enfants)
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


class ServicesOuvrantPension:
    """La durée de services qui ouvre une pension dans chaque régime spécial.

    C'est la condition dont l'article R. 173-15 du code de la sécurité sociale
    fait dépendre la priorité du régime spécial pour les trimestres des
    enfants : il les accorde « si celui-ci est susceptible d'accorder en vertu
    de ses propres règles une pension à l'intéressé ». Quinze ans partout,
    jusqu'aux réformes qui l'ont ramenée à un an ou deux pour les agents radiés
    après leur date d'effet ; les textes, régime par régime, sont dans
    l'en-tête de ``legislation/services_ouvrant_pension.csv``.
    """

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, list[tuple[str, float, float | None, Fiabilite]]] = {}
        chemin = racine / "reference" / "legislation" / "services_ouvrant_pension.csv"
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                en_fonctions = (ligne["annees_en_fonctions"] or "").strip()
                self._table.setdefault(ligne["regime"], []).append((
                    ligne["radiation_depuis"],
                    float(ligne["annees"]),
                    float(en_fonctions) if en_fonctions else None,
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                ))
        for regles in self._table.values():
            regles.sort(key=lambda regle: regle[0])

    def annees(self, regime: str, radiation: str,
               en_fonctions: bool) -> tuple[float, Fiabilite] | None:
        """Années de services exigées de l'agent radié à cette date (ISO), et
        la fiabilité de la ligne ; ``None`` pour un régime que la table ne
        porte pas. La clé des militaires se lit, elle, à la date du premier
        engagement.

        ``en_fonctions`` dit que l'agent part en fonctions, sa radiation ne
        précédant pas son départ : la SEITA n'exige alors plus rien
        (article 110 du décret n° 62-766).
        """
        retenue = None
        for depuis, annees, annees_en_fonctions, fiabilite in self._table.get(regime, ()):
            if depuis > radiation:
                break
            exigees = (annees_en_fonctions
                       if en_fonctions and annees_en_fonctions is not None else annees)
            retenue = (exigees, fiabilite)
        return retenue


class SurcoteParentale:
    """Surcote parentale — article L. 351-1-2-1 du code de la sécurité sociale.

    Le dernier avantage familial créé par le droit, et la contrepartie directe
    du recul de l'âge légal : un assuré qui avait sa durée requise un an avant
    l'âge légal s'est vu imposer par la loi du 14 avril 2023 une année de
    travail de plus qui ne lui rapportait rien, la surcote ordinaire ne
    récompensant que les trimestres accomplis APRÈS l'âge légal. La loi comble
    ce trou pour les seuls parents : 1,25 % par trimestre acquis dans l'année qui précède
    l'âge légal, quatre trimestres au plus, dès que cet âge atteint 63 ans, à
    qui détient au moins un trimestre de majoration de durée d'assurance au
    titre des enfants.

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
        """Âge légal minimal, taux par trimestre, plafond et fiabilité.

        L'âge est celui que l'âge légal doit atteindre pour que la surcote
        parentale existe — 63 ans — et non le début de la fenêtre, qui est
        l'âge légal moins un an.
        """
        for debut, fin, age, taux, maximum, fiabilite in self._table:
            if debut <= annee_liquidation <= fin:
                return age, taux, maximum, fiabilite
        return None


class MajorationsEnfantsPoints:
    """Majoration pour enfants de l'Agirc-Arrco, par période d'ACQUISITION.

    Le taux ne dépend pas du départ mais de l'année où chaque point a été
    inscrit, et du régime qui l'a inscrit (accord du 17 novembre 2017,
    article 94) : 10 à 30 % pour l'Arrco d'avant 1999, 5 % de 1999 à 2011,
    8 à 24 % pour l'Agirc d'avant 2012, 10 % depuis. Le modèle servait 10 % à
    tous les points. Voir ``majoration_enfants_points.csv``.
    """

    FICHIER = "majoration_enfants_points.csv"

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, list[tuple[int, int, tuple[float, ...], Fiabilite]]] = {}
        chemin = racine / "reference" / "legislation" / self.FICHIER
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                bareme = tuple(float(t) for t in ligne["bareme"].split())
                for code in ligne["regimes"].split():
                    self._table.setdefault(code, []).append((
                        int(ligne["acquis_debut"]), int(ligne["acquis_fin"]),
                        bareme, Fiabilite.depuis_texte(ligne["fiabilite"]),
                    ))

    def taux(self, regime: str, annee: int, nombre_enfants: int) -> float | None:
        """Taux des points que ``regime`` a inscrits en ``annee`` ; ``None``
        quand la table ne dit rien de ce régime ou de cette année."""
        for debut, fin, bareme, _ in self._table.get(regime, ()):
            if debut <= annee <= fin:
                return bareme[min(nombre_enfants, len(bareme) - 1)]
        return None


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
        self._table = self._lire(racine / "reference" / "legislation"
                                 / "minimum_vieillesse.csv")
        self._annees = sorted(self._table)
        #: Le barème d'un couple dont les deux membres sont allocataires :
        #: l'accueil seul s'en sert, pour comparer un foyer.
        self._table_couple = self._lire(racine / "reference" / "legislation"
                                        / "minimum_vieillesse_couple.csv")

    @staticmethod
    def _lire(chemin: Path) -> dict[int, tuple[float, Fiabilite]]:
        table: dict[int, tuple[float, Fiabilite]] = {}
        if not chemin.exists():
            return table
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                table[int(ligne["annee"])] = (
                    float(ligne["valeur"]),
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                )
        return table

    def _en_vigueur(self, table: dict[int, tuple[float, Fiabilite]],
                    annee: int) -> tuple[float, Fiabilite] | None:
        if not table:
            return None
        if annee in table:
            return table[annee]
        annees = sorted(table)
        anterieures = [a for a in annees if a < annee]
        ancre = max(anterieures) if anterieures else annees[0]
        valeur, fiabilite = table[ancre]
        return valeur * self.macro.coefficient_prix(ancre, annee), fiabilite

    def plafond(self, annee: int) -> tuple[float, Fiabilite] | None:
        """Montant maximal d'une personne seule, l'année demandée."""
        return self._en_vigueur(self._table, annee)

    def plafond_couple(self, annee: int) -> tuple[float, Fiabilite] | None:
        """Montant maximal d'un couple d'allocataires, l'année demandée."""
        return self._en_vigueur(self._table_couple, annee)


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
        par_annee: dict[int, int] = {}
        for ligne in carriere.lignes:
            if (ligne.cotise
                    and ligne.annee <= carriere.annee_naissance + age_max
                    and ligne.annee < annee_liquidation):
                par_annee[ligne.annee] = (par_annee.get(ligne.annee, 0)
                                          + ligne.trimestres_valides)
        acquis = sum(min(4, trimestres) for trimestres in par_annee.values())
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

    def montant(self, annee_liquidation: int, trimestres_services: int,
                duree_maximum: int | None = None
                ) -> tuple[float, Fiabilite] | None:
        """Plancher opposable pour une durée de services donnée.

        **Sous quinze ans, deux règles, et le module n'en servait qu'une.** Le
        c de L. 17 donne un quinzième de 57,5 % par année de services ; depuis
        la loi du 9 novembre 2010 (article 53, V), il ne vaut plus que pour la
        pension liquidée pour INVALIDITÉ, et le d sert toute autre pension :
        « par année de services effectifs, [le montant plein] rapporté à la
        durée des services et bonifications nécessaire pour obtenir le
        pourcentage maximum ». Treize ans pour un sédentaire né en 1964 donnent
        52/170 de la référence — 417,94 € par mois en 2026, l'exemple de
        service-public.gouv.fr (fiche F21142) et la table du Service des
        retraites de l'État —, et non les 680,90 € du c, que le modèle servait
        à tous. ``duree_maximum`` est ce dénominateur ; ``None`` garde le c,
        droit de qui avait atteint l'âge d'ouverture de ses droits avant 2011
        (article 45, V, de la même loi) et de l'invalidité, que le modèle ne
        sert pas.
        """
        bareme = self.bareme(annee_liquidation)
        reference = self.reference(annee_liquidation)
        if bareme is None or reference is None:
            return None
        _, part, points_bas, points_haut, seuil, _ = bareme
        duree = max(0, min(trimestres_services, self.SEUIL_HAUT))
        if duree <= 0:
            return None
        if duree < self.SEUIL_BAS and duree_maximum:
            taux = duree / duree_maximum
        elif duree < self.SEUIL_BAS:
            taux = part * duree / self.SEUIL_BAS
        elif duree >= self.SEUIL_HAUT:
            taux = 1.0
        elif duree < seuil:
            taux = part + (duree - self.SEUIL_BAS) * points_bas
        else:
            taux = (part + (seuil - self.SEUIL_BAS) * points_bas
                    + (duree - seuil) * points_haut)
        return reference[0] * taux, reference[1]


class BaremesTrimestre:
    """Valeur du trimestre et coefficient de majoration, par date d'effet.

    La pension minière n'est pas un salaire de référence multiplié par un taux,
    mais une DURÉE multipliée par une valeur : « le produit de la durée de
    services par la valeur du trimestre de services de l'année de leur prise
    d'effet » (article 131 du décret n° 46-2769). Depuis le décret n° 2002-800,
    cette durée est « affectée d'un coefficient de majoration déterminé en
    fonction de la date de prise d'effet de la pension » (article 131-1) : 1,473
    en 2026. La fiche du régime ne portait ni le coefficient, ni la bonne
    indexation de la valeur — les pensions, et non les prix —, et servait en
    2026 28 % de moins que ce que la caisse liquide.

    Les deux grandeurs sont lues À LA DATE de la liquidation, au mois près : la
    valeur change avec la revalorisation des pensions, le coefficient avec son
    arrêté, et l'une et l'autre en cours d'année jusqu'en 2019. Au-delà de la
    dernière ligne, la valeur suit les prix de l'année écoulée, comme la
    revalorisation du 1er janvier ; le coefficient, le quotient de la loi — le
    salaire moyen de l'année écoulée sur ses prix, jamais moins que un.
    """

    def __init__(self, racine: Path, macro: DonneesMacro) -> None:
        self.macro = macro
        self._tables: dict[str, list[tuple[int, float, float, Fiabilite]]] = {}
        dossier = racine / "reference" / "legislation"
        for chemin in sorted(dossier.glob("bareme_trimestre_*.csv")):
            nom = chemin.stem.removeprefix("bareme_trimestre_")
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                table = []
                for ligne in csv.DictReader(lignes):
                    annee, mois, _ = (int(x) for x in ligne["date_effet"].split("-"))
                    table.append((
                        DateMois(annee, mois).rang,
                        float(ligne["valeur_trimestre"]),
                        float(ligne["coefficient"]),
                        Fiabilite.depuis_texte(ligne["fiabilite"]),
                    ))
            self._tables[nom] = sorted(table)

    def noms(self) -> tuple[str, ...]:
        return tuple(sorted(self._tables))

    def lignes(self, nom: str) -> list[tuple[int, float, float, Fiabilite]]:
        return list(self._tables.get(nom, ()))

    def valeurs(self, nom: str,
                date: DateMois) -> tuple[float, float, Fiabilite] | None:
        """``(valeur du trimestre, coefficient, fiabilité)`` en vigueur à la
        date, ou ``None`` avant la première ligne — la fiche reprend alors."""
        table = self._tables.get(nom)
        if not table or date.rang < table[0][0]:
            return None
        retenue = table[0]
        for ligne in table:
            if ligne[0] > date.rang:
                break
            retenue = ligne
        rang, valeur, coefficient, fiabilite = retenue
        if retenue is not table[-1]:
            return valeur, coefficient, fiabilite
        derniere = DateMois.depuis_rang(rang).annee
        if date.annee <= derniere:
            return valeur, coefficient, fiabilite
        # AU-DELÀ DE LA DERNIÈRE LIGNE : la valeur suit les prix de l'année
        # écoulée, le coefficient le quotient de l'article 131-1.
        valeur *= self.macro.coefficient_prix(derniere - 1, date.annee - 1)
        for annee in range(derniere + 1, date.annee + 1):
            coefficient *= max(
                1.0,
                (1.0 + self.macro.salaire_moyen(annee - 1))
                / (1.0 + self.macro.inflation(annee - 1)),
            )
        return valeur, coefficient, Fiabilite.ESTIMEE


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
    """Le moteur du scénario 1 : les tables du droit en vigueur, que les
    étapes de ``droit/`` lisent, et :meth:`calculer`, qui les enchaîne."""

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
        self.durees_requises_avant_reforme_2023 = DureesRequisesAvantReforme2023(
            parametres.racine_donnees)
        self.durees_requises_avant_suspension = DureesRequisesAvantSuspension(
            parametres.racine_donnees)
        self.durees_requises_regimes = DureesRequisesRegimes(parametres.racine_donnees)
        self.calendriers_duree_requise = CalendriersDureeRequise(
            parametres.racine_donnees
        )
        self.durees_proratisation = DureesProratisation(parametres.racine_donnees)
        self.ages_ouverture = AgesOuverture(parametres.racine_donnees)
        self.ages_surcote_regimes_speciaux = AgesSurcoteRegimesSpeciaux(
            parametres.racine_donnees
        )
        self.ages_annulation_decote = AgesAnnulationDecote(parametres.racine_donnees)
        self.ages_regimes = AgesRegimes(parametres.racine_donnees)
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
        self.services_ouvrant_pension = ServicesOuvrantPension(parametres.racine_donnees)
        self.surcote_parentale = SurcoteParentale(parametres.racine_donnees)
        self.majorations_enfants_points = MajorationsEnfantsPoints(
            parametres.racine_donnees)
        self.durees_requises_fonction_publique = DureesRequisesFonctionPublique(
            parametres.racine_donnees
        )
        self.durees_requises_avant_soixante_ans = DureesRequisesAvantSoixanteAns(
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
        self.baremes_trimestre = BaremesTrimestre(parametres.racine_donnees, macro)
        #: Les revalorisations des pensions servies, qui portent aussi le
        #: traitement d'une pension différée : voir
        #: :func:`~retraite_notionnelle.revalorisation.coefficient_traitement_differe`.
        self.revalorisations_pensions = RevalorisationsPensions(parametres.racine_donnees)
        self.carriere_longue = CarriereLongue(parametres.racine_donnees)
        #: Vrai pendant que :func:`~retraite_notionnelle.droit.ouvrir.ouverture_carriere_longue` date le droit :
        #: la condition de durée qu'elle lit est celle de la génération, et non
        #: celle que ce droit fait ensuite opposer au taux plein.
        self._ouverture_carriere_longue_en_cours = False
        self.surcote_baremes = SurcoteBaremes(parametres.racine_donnees)
        self.minimum_vieillesse = MinimumVieillesse(parametres.racine_donnees, macro)
        #: Les régimes qui attribuent des POINTS GRATUITS, rangés sous le régime
        #: de base dont les années les ouvrent : une carrière qui n'a validé
        #: aucun trimestre dans ce dernier n'a rien à chercher. Voir
        #: :func:`~retraite_notionnelle.droit.acquerir.points_gratuits`.
        self.points_gratuits_par_base: dict[str, tuple[str, ...]] = {}
        for regime in catalogue:
            for periode in regime.periodes:
                if periode.points_gratuits is None:
                    continue
                base = periode.points_gratuits.regime
                attribuants = self.points_gratuits_par_base.get(base, ())
                if regime.code not in attribuants:
                    self.points_gratuits_par_base[base] = (*attribuants, regime.code)

    # -- ce que les étapes lisent sur le moteur ------------------------------
    #
    # Les étapes de ``droit/`` lisent ces constantes sur le moteur qu'on leur
    # passe, et non dans leur module : ce sont des paramètres du droit réel,
    # qu'une variante change pour un seul calcul — la cascade des avantages
    # repousse ainsi la date du salaire annuel moyen des parents.

    #: Pensions à compter desquelles le salaire annuel moyen des parents porte
    #: sur vingt-quatre ou vingt-trois années au lieu de vingt-cinq.
    PARENTS_MEILLEURES_ANNEES_DEPUIS = DateMois(2026, 9)

    #: L'âge avant lequel un droit ouvert fait lire la durée à l'année
    #: d'ouverture plutôt qu'à la génération : « avant l'âge de soixante
    #: ans » (L. 13, III ; article 5, VI, de la loi du 21 août 2003).
    AGE_DUREE_A_L_OUVERTURE = 60.0
    #: Le XXIV, C, de l'article 10 de la loi du 14 avril 2023 ne vise que ceux
    #: qui peuvent liquider à compter de ce mois.
    DUREE_XXIV_C_DEPUIS = DateMois(2023, 9)
    #: Les régimes que L. 13 du code des pensions et le XXIV visent : voir
    #: :data:`~retraite_notionnelle.droit.coordonner.REGIMES_CODE_DES_PENSIONS`.
    REGIMES_CODE_DES_PENSIONS = coordonner.REGIMES_CODE_DES_PENSIONS

    #: Dernière année à compter dans les services : voir
    #: :func:`~retraite_notionnelle.droit.coordonner.borne_carriere`.
    _borne_carriere = staticmethod(coordonner.borne_carriere)

    #: Premier trimestre que la surcote puisse compter : les dispositions de
    #: la loi du 21 août 2003 valent pour les périodes cotisées accomplies à
    #: compter du 1er janvier 2004.
    SURCOTE_DEPUIS = DateMois(2004, 1)
    #: Âge au-delà duquel le barème de 2007-2008 sert 1,25 %.
    SURCOTE_AGE_MAJORE = 65

    # -- calcul --------------------------------------------------------------

    def calculer(self, carriere: Carriere,
                 ignorer_penalite_age: bool = False,
                 avantages_non_contributifs: bool = True,
                 avpf: bool = True,
                 liquider_successions: bool = True,
                 points_gratuits: bool | None = None,
                 nature: str = "definitive") -> ResultatActuel:
        """Pension servie par le système en vigueur, à la date d'effet.

        La liquidation est :func:`~retraite_notionnelle.droit.liquidation.liquider`,
        une fonction pure : elle fait l'acquisition, ouvre le droit, liquide
        chaque régime et complète tous régimes. L'ASPA, qui regarde toutes
        les ressources, vient ensuite, de l'étape « foyer et net »
        (:mod:`~retraite_notionnelle.droit.foyer`). Les drapeaux sont ce
        qu'une couche d'un seul calcul neutralise (docs/architecture.md,
        § 4.8 et 6.4) : le contexte de la liquidation les porte. ``nature``
        est celle de la demande — ``fictive`` pour la valorisation des droits
        acquis.

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
        celui qui lui succède (voir
        :func:`~retraite_notionnelle.droit.coordonner.groupes_de_succession`). C'est le
        droit, et le défaut ; à FAUX, chaque nom de caisse est liquidé sur ses
        seules années, comme le modèle le faisait, et la variante ne sert qu'à
        mesurer ce que la correction déplace.

        ``points_gratuits`` commande les points que la RCO agricole attribue
        sans cotisation (:func:`~retraite_notionnelle.droit.acquerir.points_gratuits`).
        ``None`` suit
        ``avantages_non_contributifs`` : la valorisation des droits acquis n'en
        veut pas, puisqu'elle mesure du contributif pur. Les recalculs de la
        cascade le fixent, eux, pour que chaque avantage soit retiré seul.

        L'agent parti de la fonction publique sans droit à pension y est
        RÉTABLI au régime général et à l'Ircantec
        (:func:`~retraite_notionnelle.droit.coordonner.retablir`).
        """
        if points_gratuits is None:
            points_gratuits = avantages_non_contributifs
        neutralisations = frozenset(nom for nom, neutre in (
            ("avantages_non_contributifs", not avantages_non_contributifs),
            ("avpf", not avpf),
            ("points_gratuits", not points_gratuits),
            ("decote_surcote", ignorer_penalite_age),
            ("successions", not liquider_successions),
        ) if neutre)
        contexte = _liquidation.Contexte(self, neutralisations)
        liquidation = _liquidation.liquider(
            _liquidation.demande_de_depart(carriere, nature),
            _liquidation.Etat(carriere), contexte)
        carriere = liquidation.carriere
        foyer = _foyer.foyer_et_net(
            self, carriere.personne, liquidation.demande.date_effet,
            carriere.annee_liquidation, liquidation.total,
            (carriere.age_liquidation or 0.0) >= MinimumVieillesse.AGE_OUVERTURE,
            contexte)
        return resultat_actuel(liquidation, foyer)


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
