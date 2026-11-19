"""Les tables du droit en vigueur : les chargeurs du scénario 1.

Ce que ``scenarios/actuel.py`` gardait du droit en vigueur sous forme de
tables — âges, durées requises, décotes et surcotes, minima, majorations,
réversions, conversions et valeurs du point —, et que lisent la fabrique du
paquet (``scripts/construire_donnees.py``) et le coût des avantages. Relogé
ici tel quel, sans changer une donnée (action 161, étape 3 de l'inventaire
du retrait des règles ; note de décision 0006) : le moteur du scénario 1,
``ScenarioActuel`` de ``moteur/js/scenario-actuel.js``, les reprend
d'ici, les mêmes objets, tant qu'il reste. Rien ici n'importe un module de
règles du moteur Python.
"""

from __future__ import annotations

import copy
import csv
from bisect import bisect_right
from datetime import date
from pathlib import Path

from .. import chronologie
from ..calendrier import DateMois
from ..noyau import versions
from ..revalorisation_servie import DEBUT_REGLE_GENERALE_PUBLIC
from ..somme import somme_ordonnee
from ..types_du_pont.droit import ConversionPoint, DerogationActive, TrimestresAccordes
from .chargement import (
    Fiabilite,
    SerieAnnuelle,
    ValeurAnnuelle,
    au_mois,
    charger_accords_internationaux,
    charger_table_par_generation,
    charger_yaml,
    valeur_par_generation,
)
from .macro import DonneesMacro
from .minimum_vieillesse import MinimumVieillesse
from . import tables_de_version
from .revalorisations import RevalorisationsPensions, produit


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

    ET UNE TABLE PEUT SE LIRE À UNE AUTRE GÉNÉRATION QUE CELLE DE L'ASSURÉ
    (colonne `age_de_lecture`). L'article 9-1 de l'annexe 3 des IEG, du
    1er janvier 2017 au 31 décembre 2024, oppose à l'agent qui peut liquider
    avant soixante ans « celle exigée des agents atteignant l'âge de soixante
    ans l'année à compter de laquelle la liquidation peut intervenir » : la
    table de 2014 se lit pour lui à la génération qui atteint soixante ans
    au mois où il réunit les conditions, comme la CNIEG l'écrit (circulaire
    n° 2024/15). Un agent actif né en décembre 1964, dont le droit s'ouvre
    en décembre 2020, doit 167 trimestres, ceux de la génération 1960, et
    non les 169 de la sienne.

    ET UNE TABLE PEUT NE VALOIR QU'À PARTIR D'UN ÂGE (colonne `age_minimum`).
    Le III de l'article 26 du décret n° 2011-1500, depuis 2022, abaisse la
    cible de la décote des navigants nés avant 1971 « lorsque la liquidation
    est effectuée à compter de l'âge de cinquante-cinq ans » : en deçà, la
    table ne répond pas.

    ET UNE TABLE PEUT S'ARRÊTER À UNE GÉNÉRATION (ligne sans trimestres) : à
    compter d'elle, la table ne répond plus, et la table commune reprend. Le
    code rural (R. 732-39) écrit la durée des non-salariés agricoles nés
    avant 1949 et renvoie, pour les suivants, à celle du régime général.
    """

    FICHIER = "duree_requise_regimes_speciaux.csv"

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, dict[float, tuple[int, int, Fiabilite]]] = {}
        self._depuis: dict[str, int] = {}
        self._age_de_lecture: dict[str, float] = {}
        self._age_minimum: dict[str, float] = {}
        chemin = racine / "reference" / "legislation" / self.FICHIER
        if chemin.exists():
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    self._table.setdefault(ligne["table"], {})[
                        float(ligne["generation"])
                    ] = (int(ligne["trimestres"]) if ligne["trimestres"].strip()
                         else None, int(ligne["retranche_decote"]),
                         Fiabilite.depuis_texte(ligne["fiabilite"]))
                    self._depuis[ligne["table"]] = _rang_mois(ligne["depuis"])
                    age = (ligne.get("age_de_lecture") or "").strip()
                    if age:
                        self._age_de_lecture[ligne["table"]] = float(age)
                    minimum = (ligne.get("age_minimum") or "").strip()
                    if minimum:
                        self._age_minimum[ligne["table"]] = float(minimum)
        self._generations = {cle: tuple(sorted(valeurs))
                             for cle, valeurs in self._table.items()}

    def ligne(self, table: str, generation: float, ouverture: int,
              age_liquidation: float | None = None
              ) -> tuple[int, int, Fiabilite] | None:
        """Trimestres requis, trimestres retranchés pour la décote, fiabilité.

        ``ouverture`` est le rang du mois où l'assuré réunit les conditions ;
        avant la date d'effet de la table, elle ne répond pas. Une table qui
        porte un âge de lecture répond, à qui réunit les conditions avant cet
        âge, pour la génération qui l'atteint ce mois-là. Une table qui porte
        un âge minimum ne répond qu'à qui liquide à cet âge ou après.
        """
        generations = self._generations.get(table)
        if not generations or ouverture < self._depuis[table]:
            return None
        minimum = self._age_minimum.get(table)
        if minimum is not None and (age_liquidation is None
                                    or age_liquidation < minimum):
            return None
        age = self._age_de_lecture.get(table)
        if age is not None:
            date = DateMois.depuis_rang(ouverture)
            generation = min(generation,
                             round(date.annee - age + (date.mois - 1) / 12, 3))
        lue = valeur_par_generation(self._table[table], generations, generation)
        return None if lue is None or lue[0] is None else lue


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
    return au_mois(float(texte)) if texte else None


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
        self._surcotes: dict[str, dict[float, float | None]] = {}
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
                    borne = (ligne.get("age_surcote_maximum") or "").strip()
                    self._surcotes.setdefault(ligne["table"], {})[generation] = (
                        au_mois(float(borne)) if borne else None
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


    def age_surcote_maximum(self, table: str, generation: float) -> float | None:
        """Âge au-delà duquel la majoration ne court plus, que la table écrit
        pour cette génération ; ``None`` si la ligne n'en porte pas. La CAVP
        la borne à soixante-cinq, soixante-six, puis soixante-huit ans selon
        la génération (statuts de 2011, annexe à l'article 15)."""
        generations = self._generations.get(table)
        if not generations or generation < generations[0]:
            return None
        cle = generations[bisect_right(generations, generation) - 1]
        return self._surcotes[table].get(cle)


class DureesRequisesFonctionPublique:
    """Durée de services requise dans la fonction publique, 2004-2008.

    Le II de l'article 66 de la loi du 21 août 2003 fait monter « le nombre
    de trimestres nécessaires pour obtenir le pourcentage maximum de la
    pension » de 150 à 160, deux par an, selon l'ANNÉE OÙ LE DROIT S'OUVRE.
    Ce nombre commande à la fois la proratisation, le décompte de la décote et
    le seuil de la surcote. Avant 2004, la fiche du régime porte 150 ; à
    compter de 2009, l'article L. 13 II renvoie à la durée du régime général,
    lue par génération. La table ne répond donc que pour les années qu'elle
    porte, et rend ``None`` ailleurs. Mais « jusqu'en 2003 » se lit à l'année
    d'ouverture comme le reste : le droit ouvert avant la table garde la durée
    de la période où il s'est ouvert, quand même il serait liquidé plus tard
    (:meth:`avant_la_table`, ``ouvrir.duree_requise``).

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

    def avant_la_table(self, annee_ouverture: int) -> bool:
        """Le droit s'est-il ouvert avant la première année de la table ?"""
        return bool(self._table) and annee_ouverture < min(self._table)


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


class AgesOuvertureAvantReforme2023(AgesOuverture):
    """Âge légal que la loi du 14 avril 2023 a relevé : celui du droit en
    vigueur au 31 août 2023, soixante-deux ans dès la génération 1955
    (D. 161-2-1-9, version du 31 décembre 2011). Aucune pension n'a pris effet
    sous lui aux générations qu'il porte : il ne sert qu'au droit
    contrefactuel ``au_31_aout_2023``. Voir
    ``age_ouverture_avant_reforme_2023.csv``."""

    def __init__(self, racine: Path) -> None:
        TableParGeneration.__init__(
            self, racine, "age_ouverture_avant_reforme_2023.csv", "age")


class AgesOuvertureAvantSuspension(AgesOuverture):
    """Âge légal que la suspension de 2026 a abaissé : celui de la loi de 2023,
    soixante-trois ans pour les nés en 1964, soixante-quatre dès 1968
    (D. 161-2-1-9, version du 1er septembre 2023). Il ne sert qu'au droit
    contrefactuel ``loi_2023_sans_suspension``. Voir
    ``age_ouverture_avant_suspension.csv``."""

    def __init__(self, racine: Path) -> None:
        TableParGeneration.__init__(
            self, racine, "age_ouverture_avant_suspension.csv", "age")


class TableRecouverte:
    """Une table par génération qu'une autre recouvre, de sa première
    génération à toutes les suivantes : ce qu'un droit contrefactuel change à
    l'âge légal ou à la durée requise. En deçà, la table du droit en vigueur
    répond. Elle se lit comme les deux tables qu'elle assemble."""

    def __init__(self, dessus: TableParGeneration, dessous: TableParGeneration) -> None:
        self._dessus = dessus
        self._dessous = dessous

    def valeur(self, generation: float) -> tuple[float, Fiabilite] | None:
        lue = self._dessus.valeur(generation)
        return lue if lue is not None else self._dessous.valeur(generation)

    def age(self, generation: float) -> tuple[float, Fiabilite] | None:
        return self.valeur(generation)

    def trimestres(self, generation: float) -> tuple[int, Fiabilite] | None:
        valeur = self.valeur(generation)
        return None if valeur is None else (int(valeur[0]), valeur[1])


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
                    age_ouverture=au_mois(float(ligne["age_ouverture"])),
                    age_annulation=au_mois(float(ligne["age_annulation"])),
                    services_requis=au_mois(float(ligne["services_requis_annees"])),
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
    #: La colonne qui porte la clé de chaque ligne.
    CLE = "categorie"

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, dict[float, tuple[float, Fiabilite]]] = {}
        chemin = racine / "reference" / "legislation" / self.FICHIER
        if not chemin.exists():
            self._annees: dict[str, list[float]] = {}
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                self._table.setdefault(ligne[self.CLE], {})[
                    float(ligne["annee_atteinte"])
                ] = (au_mois(float(ligne["annees_requises"])),
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


class DureesServicesActifs(DureesServicesMilitaires):
    """Durée de services classés qui ouvre l'âge anticipé ou minoré, par année
    d'atteinte.

    Quinze ans de services actifs, vingt-cinq de services super-actifs avant la
    loi du 9 novembre 2010 ; dix-sept et vingt-sept depuis 2015. L'article 6 du
    décret n° 2011-2103 indexe le relèvement, comme l'article 4 celui des
    militaires, sur « l'année au cours de laquelle est atteinte la durée de
    services » antérieure, et non sur la génération : la clé est le classement
    (``active``, ``super_active``).
    """

    FICHIER = "duree_services_actifs.csv"
    CLE = "classement"


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


class AnneesRevenuAnnuelMoyenIndependants(AnneesSalaireReference):
    """Nombre d'années retenues au revenu annuel moyen des artisans et des
    commerçants, par génération (R. 634-1-1) : deux fois plus lent que celui
    des salariés, vingt-cinq années pour les assurés nés après 1952."""

    def __init__(self, racine: Path) -> None:
        TableParGeneration.__init__(
            self, racine, "annees_revenu_annuel_moyen_independants.csv", "annees")


class FichesDatees:
    """Les fiches de ``data/reference/regles/`` dont le moteur lit, à la date
    d'effet d'une pension, les paramètres de la version qui vaut.

    Le salaire annuel moyen du régime général (``salaire_annuel_moyen``) et le
    revenu annuel moyen des artisans et des commerçants
    (``revenu_annuel_moyen_independants``) : quelles années, comment les
    moyenner, lesquelles écarter, et, pour les seconds, quelle table du nombre
    d'années. Une période y renvoie par ``regles_du_salaire_annuel_moyen``.
    Et les bonifications des emplois classés de la fonction publique et celle
    des militaires, que ``compter.trimestres_des_emplois`` lit
    (``compter.FICHES_DES_EMPLOIS``),
    et le départ anticipé des parents de trois enfants, que
    ``ouvrir.depart_parent_trois_enfants`` lit, et le plafond de L. 18, que
    ``completer.plafond_de_l_article_l18`` lit, et la majoration exceptionnelle
    des petites pensions de septembre 2023, que
    ``revalorisation.majorer_les_petites_pensions`` lit, et le relèvement des
    exploitants de la même date, que ``revalorisation.relever_les_exploitants`` lit,
    et les versements uniques des petites pensions, que
    ``completer.verser_en_capital`` lit, et le décompte des services du code
    des pensions au jour, que ``compter.decompte_des_services`` lit, et le
    maximum des pensions du régime général, que ``liquider.pension_maximale``
    lit, et les taux pleins par catégorie de L. 351-8, que
    ``categories.taux_plein_par_categorie`` lit, et l'âge de soixante-cinq ans
    du parent de trois enfants, que ``categories.age_du_parent_de_trois_enfants``
    lit, et la majoration de
    l'Agirc-Arrco pour enfants à charge, que
    ``completer.majoration_pour_enfants_a_charge`` lit, et les régimes de
    l'Agirc-Arrco qui calculent la majoration pour enfants nés ou élevés sans le
    coefficient d'anticipation, que ``completer.regimes_sans_anticipation`` lit
    (fiche ``majoration_enfants_agirc_arrco``), et la majoration pour
    conjoint à charge, que ``completer.majoration_pour_conjoint_a_charge`` lit,
    et les majorations forfaitaires de 1972 à 1982 des pensions prises avant
    1975, que ``revalorisation.majorations_forfaitaires`` lit, et les primes que
    la loi assujettit à la retenue pour pension, que ``primes.prime_de_la_pension``
    lit, et ce qui exonère des coefficients d'anticipation de l'Agirc et de
    l'Arrco, que ``liquider.abattement_points`` lit, et le barème de
    l'Ircantec, que ``liquider.bareme_ircantec`` lit,
    et les plans de revalorisation des retraites agricoles de 1997 à 2008,
    que ``completer.majoration_retraite_proportionnelle`` lit, et la limite
    d'âge des agents publics et ses exceptions, que ``limite_age.radiation``
    lit au jour où la limite est atteinte (date ``age_atteint``,
    ``FICHES`` de ``moteur/js/droit/limite_age.js``), et le minimum de
    pension de la SNCF, que ``liquider.minimum_de_pension_ouvert`` lit, et la
    retraite progressive, que ``progressive.regle`` lit, et la seconde part de
    la cotisation de retraite complémentaire du chef d'exploitation agricole,
    que ``acquerir.seconde_part_de_rco`` lit à l'année de la cotisation, et
    les droits de l'activité exercée après la première pension, que
    ``seconde.versionDesDroits`` lit à la date de cette pension et à celle du
    mois d'activité, et la seconde pension, que
    ``seconde.regleDeLaNouvellePension`` lit à sa date d'effet et à celle de la
    première, et l'âge légal, que ``AgesOuverture`` du portage lit à la date
    d'effet de la pension, la génération y choisissant sa ligne.
    """

    NOMS = ("salaire_annuel_moyen", "revenu_annuel_moyen_independants",
            "bonification_cinquieme_police_penitentiaire",
            "bonification_cinquieme_sapeurs_pompiers",
            "bonification_cinquieme_militaires",
            "majoration_duree_hospitaliers_actifs",
            "depart_anticipe_parents_trois_enfants",
            "majoration_enfants_plafond_fonction_publique",
            "majoration_exceptionnelle_2023", "relevement_des_exploitants_2023",
            "versement_forfaitaire_unique", "versement_unique_agirc_arrco",
            "versement_unique_ircantec", "versement_unique_rci",
            "decompte_des_services_fonction_publique",
            "pension_maximale_regime_general",
            "taux_plein_anciens_deportes_internes", "taux_plein_meres_de_famille_ouvrieres",
            "taux_plein_travailleurs_manuels", "taux_plein_anciens_combattants_prisonniers",
            "taux_plein_a_soixante_cinq_ans",
            "majoration_enfants_a_charge_agirc_arrco", "majoration_enfants_agirc_arrco",
            "majoration_conjoint_a_charge",
            "coefficients_anticipation_agirc_arrco", "coefficient_anticipation_ircantec",
            "majorations_forfaitaires_1972_1982",
            "indemnite_sujetions_speciales_police",
            "prime_speciale_sujetion_aides_soignants",
            "indemnite_de_feu_sapeurs_pompiers", "majoration_retraite_proportionnelle",
            "limite_age_fonction_publique", "limite_age_militaires",
            "recul_limite_age_enfants", "prolongation_activite_carriere_incomplete",
            "prolongation_activite_categorie_active",
            "maintien_en_fonctions_jusqu_a_70_ans",
            "plafond_limite_age_fonction_publique", "limite_age_contractuels",
            "limite_age_ouvriers_etat", "limite_age_sncf_ratp", "limite_age_ieg",
            "limite_age_opera", "limite_age_seita", "limite_age_banque_de_france",
            "limite_age_mines", "apprentissage", "stages_formation_professionnelle",
            "sportifs_haut_niveau", "conge_supplementaire_naissance",
            "minimum_pension_sncf", "retraite_progressive",
            "cotisation_rco_agricole_2026", "decote_banque_de_france",
            "droits_apres_la_premiere_pension", "seconde_pension",
            "surcote_banque_de_france", "age_ouverture_banque_de_france_actifs",
            "age_legal_par_generation")

    def __init__(self, racine: Path) -> None:
        self._fiches: dict[str, dict] = {}
        for nom in self.NOMS:
            chemin = racine / "reference" / "regles" / f"{nom}.yaml"
            if chemin.exists():
                fiche = charger_yaml(chemin)
                self._fiches[nom] = versions.preparer(fiche)
                if nom == tables_de_version.FICHE_DE_L_AGE_LEGAL:
                    # La table de chaque version et son renvoi à sa rédaction
                    # antérieure (note de décision 0009, étape 2).
                    for version in self._fiches[nom]["versions"]:
                        version.update(tables_de_version.pour_le_moteur(
                            fiche, version["id"], racine))

    def fiches(self) -> dict[str, dict]:
        """Les fiches préparées : ce que le paquet du site porte."""
        return self._fiches

    def sans(self, *noms: str) -> FichesDatees:
        """Les mêmes fiches, celles-ci retirées : la contrefactuelle qui mesure
        ce qu'elles servent (:mod:`~retraite_notionnelle.avantages`)."""
        copie = object.__new__(FichesDatees)
        copie._fiches = {nom: fiche for nom, fiche in self._fiches.items()
                         if nom not in noms}
        return copie

    def regle(self, nom: str, date_effet: str) -> dict | None:
        """Les paramètres de la version de ``nom`` qui vaut pour une pension
        prenant effet à ``date_effet`` (AAAA-MM-JJ) ; ``None`` sans fiche ou
        sans version à cette date."""
        version = self.version(nom, date_effet)
        return None if version is None else dict(version["parametres"])

    def version(self, nom: str, date_effet: str) -> dict | None:
        """La version de ``nom`` qui vaut pour une pension prenant effet à
        ``date_effet`` (AAAA-MM-JJ), telle que :func:`versions.preparer` la
        garde — son identifiant, son texte, ses paramètres ; ``None`` sans
        fiche ou sans version à cette date."""
        fiche = self._fiches.get(nom)
        if fiche is None:
            return None
        return versions.applicable(fiche, {"liquidation.date_effet": date_effet})

    def version_aux_dates(self, nom: str, dates: dict[str, str]) -> dict | None:
        """La version de ``nom`` qui vaut à ces dates (AAAA-MM-JJ), parmi
        lesquelles la fiche ne lit que celles qu'elle déclare : une période
        assimilée donne son début et la date d'effet de la pension, que la
        fiche de l'apprentissage ne lit pas. ``None`` sans fiche ou sans
        version à ces dates."""
        fiche = self._fiches.get(nom)
        if fiche is None:
            return None
        return versions.applicable(fiche, {cle: valeur for cle, valeur in dates.items()
                                           if cle in fiche["dates_qui_decident"]})


class MajorationsPourEnfants:
    """Trimestres accordés au titre des enfants, enfant par enfant, lus dans
    les versions des fiches qui les portent (docs/architecture.md, § 4.1).

    Le module en servait huit par enfant, à tout assuré, à toute date et dans
    tout régime. Le droit n'en a jamais servi autant : la majoration de durée
    d'assurance n'existe pas avant 1972, elle vaut un an par enfant jusqu'en
    1974, elle est attribuée à la mère, et la fonction publique ne l'applique
    pas — elle a sa propre bonification, qui vaut un an par enfant né avant
    2004 et deux trimestres pour les enfants nés depuis. Un père de trois
    enfants recevait ainsi douze trimestres que la loi ne lui a jamais donnés,
    de quoi effacer une décote entière.

    Chaque dispositif a sa fiche, et ses versions forment un partage de leurs
    dates qui décident : la date d'effet de la pension et la naissance de
    l'enfant. Le ``dispositif`` est le code que la fiche de régime déclare
    dans ``avantages_non_contributifs`` : c'est elle qui dit quel régime
    accorde quoi, et la fiche combien.
    """

    #: La fiche de chaque dispositif, dans ``data/reference/regles/``.
    FICHES = {
        "mda": "majoration_duree_assurance_enfants",
        "bonifications": "enfants_fonction_publique",
        "enfants_sncf": "enfants_sncf",
        "enfants_ratp": "enfants_ratp",
        "enfants_ieg": "enfants_ieg",
        "enfants_crpcen": "enfants_crpcen",
    }
    #: Les bénéficiaires qu'une version peut désigner.
    BENEFICIAIRES = ("mere",)

    def __init__(self, racine: Path) -> None:
        self._fiches: dict[str, dict] = {}
        for dispositif, nom in self.FICHES.items():
            chemin = racine / "reference" / "regles" / f"{nom}.yaml"
            if chemin.exists():
                self._fiches[dispositif] = versions.preparer(charger_yaml(chemin))

    def fiches(self) -> dict[str, dict]:
        """Les fiches préparées, sous leur nom : ce que le paquet du site porte."""
        return {fiche["id"]: fiche for fiche in self._fiches.values()}

    def par_enfant(self, dispositif: str, sexe: str, naissance: str, date_effet: str,
                   naissances: list[str] | tuple[str, ...]) -> TrimestresAccordes | None:
        """Ce que le dispositif accorde pour un enfant né ce jour (AAAA-MM-JJ),
        à une pension qui prend effet à ``date_effet``.

        ``naissances`` sont celles de tous les enfants de l'assurée nés avant
        la date d'effet : la loi Boulin n'accordait rien à la mère d'un seul
        enfant élevé neuf ans.

        Une version peut exiger un âge de l'enfant à la date d'effet
        (``age_minimum``) : de 1972 à 2003, la majoration va à l'enfant élevé
        neuf ans avant ses seize ans, et celui qui n'a pas neuf ans à la date
        d'effet ne peut pas l'avoir été.

        ``None`` couvre les cinq cas où le droit ne donne rien : le dispositif
        n'existe pas encore à ces dates, il n'a jamais existé dans ce régime,
        l'assurée n'en est pas la bénéficiaire, l'enfant n'a pas l'âge que la
        version exige, ou elle n'a pas le nombre d'enfants qu'elle exige.
        """
        fiche = self._fiches.get(dispositif)
        if fiche is None:
            return None
        situation = {"enfant.naissance": naissance, "liquidation.date_effet": date_effet}
        version = versions.applicable(
            fiche, {nom: situation[nom] for nom in fiche["dates_qui_decident"]})
        if version is None:
            return None
        parametres = version["parametres"]
        age_minimum = parametres.get("age_minimum")

        def eleve(jour: str) -> bool:
            return (age_minimum is None
                    or chronologie.annees_revolues(jour, date_effet) >= int(age_minimum))

        trimestres = int(parametres["trimestres_par_enfant"])
        services = int(parametres["services_par_enfant"])
        if (parametres.get("trimestres_premier_enfant") is not None
                and all(naissance <= jour for jour in naissances)):
            # Le PREMIER ENFANT DE LA FRATRIE a sa part, les suivants la
            # leur : deux trimestres, puis quatre, à la RATP (décret
            # n° 2008-637, article 24 III ; COR, 19 octobre 2023, document 2,
            # note 15).
            trimestres = int(parametres["trimestres_premier_enfant"])
            services = min(services, trimestres)
        if (parametres.get("trimestres_second_de_deux") is not None
                and len(naissances) == 2
                and all(naissance >= jour for jour in naissances)
                and any(jour < naissance for jour in naissances)):
            # LE SECOND D'UNE FRATRIE DE DEUX a sa bonification doublée aux
            # IEG (annexe 3 au statut national, article 12) : la fratrie
            # compte tous les enfants, quelle que soit leur naissance.
            trimestres = int(parametres["trimestres_second_de_deux"])
            services = int(parametres["services_second_de_deux"])
        if parametres.get("par_annee_d_education"):
            # D. 351-1-7 : un trimestre à la naissance, puis un au terme de
            # chaque année d'éducation, dans la limite de la version.
            trimestres = min(trimestres, 1 + chronologie.annees_revolues(naissance, date_effet))
            services = min(services, trimestres)
        if trimestres <= 0 or not eleve(naissance):
            return None
        beneficiaire = parametres["beneficiaire"]
        if beneficiaire not in self.BENEFICIAIRES:
            raise ValueError(f"{fiche['id']}.{version['id']} : bénéficiaire inconnu, "
                             f"{beneficiaire!r}")
        if beneficiaire == "mere" and sexe != "F":
            return None
        if somme_ordonnee(1 for jour in naissances if eleve(jour)) < int(parametres.get("enfants_minimum", 1)):
            return None
        return TrimestresAccordes(
            fiche=fiche["id"], version=version["id"], texte=version["texte"],
            trimestres=trimestres, services=services,
            condition=parametres.get("condition", "tout_enfant"),
            fiabilite=Fiabilite.depuis_texte(parametres["fiabilite"]))


class Reversions:
    """Les fiches de la réversion (domaine « reversion »), dont le moteur lit
    les versions : celle du régime général et des régimes alignés, celle de
    la fonction publique, celles de l'Agirc-Arrco, du RAFP, de l'Ircantec et
    de la complémentaire des indépendants (docs/architecture.md, § 4.1).
    Chaque fiche dit ses régimes (``regimes``) ; les autres n'en ont pas
    encore, et la réversion le dit.
    """

    #: Les fiches de la réversion que le moteur lit, dans cet ordre.
    FICHES = ("reversion", "reversion_fonction_publique", "reversion_agirc_arrco",
              "reversion_rafp", "reversion_ircantec", "reversion_rci",
              "reversion_crpcen", "reversion_ieg", "reversion_sncf",
              "reversion_carcdsf", "reversion_cavamac",
              "majoration_forfaitaire_reversion")

    def __init__(self, racine: Path) -> None:
        self._fiches: dict[str, dict] = {}
        self._par_regime: dict[str, str] = {}
        for nom in self.FICHES:
            chemin = racine / "reference" / "regles" / f"{nom}.yaml"
            if not chemin.exists():
                continue
            brute = charger_yaml(chemin)
            # Ce que le moteur lit d'une fiche, et ses régimes, que la
            # préparation ne garde pas : le paquet du site les porte aussi.
            self._fiches[nom] = versions.preparer(brute) | {
                "regimes": list(brute.get("regimes") or ())}
            for regime in brute.get("regimes") or ():
                self._par_regime.setdefault(regime, nom)
        legislation = racine / "reference" / "legislation"
        #: Le minimum annuel de la réversion du régime général (D. 353-1) et le
        #: plafond trimestriel de sa majoration de 11,1 % (D. 353-4) : une
        #: ancre par année, le montant en vigueur à son 31 décembre.
        self._minimum = MinimumVieillesse._lire(legislation / "minimum_reversion.csv")
        self._plafond_majoration = MinimumVieillesse._lire(
            legislation / "plafond_majoration_reversion.csv")
        #: La limite forfaitaire annuelle de cumul des réversions d'avant
        #: juillet 2004 (D. 355-1), depuis 1974, et la majoration forfaitaire
        #: annuelle par enfant à charge (L. 353-5, R. 353-11), depuis 1988.
        self._limite_cumul = MinimumVieillesse._lire(legislation / "limite_cumul_reversion.csv")
        self._majoration_enfant = MinimumVieillesse._lire(
            legislation / "majoration_forfaitaire_enfant_reversion.csv")
        #: Le minimum de pension de la SNCF (décret n° 2008-639, article 15,
        #: IV), annuel, dont la réversion garde une part (article 18) : les
        #: ancres que le texte écrit, que l'article 30 revalorise entre elles.
        self._minimum_pension_sncf = MinimumVieillesse._lire(
            legislation / "minimum_pension_sncf.csv")

    @staticmethod
    def _en_vigueur(table: dict[int, tuple[float, Fiabilite]],
                    annee: int) -> tuple[float, Fiabilite] | None:
        """L'ancre de l'année, ou la dernière qui la précède ; ``None`` avant la
        première. Les montants d'une réversion sont ceux d'une année passée ou
        de l'année courante : la série n'a pas à se projeter."""
        anterieures = [a for a in table if a <= annee]
        return table[max(anterieures)] if anterieures else None

    def minimum(self, annee: int) -> tuple[float, Fiabilite] | None:
        """Le minimum annuel de la réversion du régime général, en euros de
        l'année ``annee`` ; ``None`` avant la loi du 14 mars 1941."""
        return self._en_vigueur(self._minimum, annee)

    def plafond_majoration(self, annee: int) -> tuple[float, Fiabilite] | None:
        """Le plafond TRIMESTRIEL de la majoration de 11,1 % (L. 353-6), en
        euros de l'année ``annee`` ; ``None`` avant 2010."""
        return self._en_vigueur(self._plafond_majoration, annee)

    def limite_cumul(self, annee: int) -> tuple[float, Fiabilite] | None:
        """La limite forfaitaire ANNUELLE de cumul de D. 355-1, en euros de
        l'année ``annee`` ; ``None`` avant le 1er juillet 1974."""
        return self._en_vigueur(self._limite_cumul, annee)

    def majoration_enfant(self, annee: int) -> tuple[float, Fiabilite] | None:
        """La majoration forfaitaire ANNUELLE par enfant à charge de L. 353-5, en
        euros de l'année ``annee`` ; ``None`` avant 1988."""
        return self._en_vigueur(self._majoration_enfant, annee)

    def minimum_pension_sncf(self, annee: int) -> tuple[int, float, Fiabilite] | None:
        """L'ancre du minimum de pension ANNUEL de la SNCF en vigueur l'année
        ``annee``, ``(son année, montant, fiabilité)``, que l'article 30
        revalorise jusqu'à ``annee`` ; ``None`` avant le 1er juillet 2008."""
        anterieures = [a for a in self._minimum_pension_sncf if a <= annee]
        if not anterieures:
            return None
        ancre = max(anterieures)
        return (ancre, *self._minimum_pension_sncf[ancre])

    def series(self) -> dict[str, dict]:
        """Les séries, sous le nom que le paquet du site leur donne."""
        return {"minimum_reversion": dict(self._minimum),
                "plafond_majoration_reversion": dict(self._plafond_majoration),
                "limite_cumul_reversion": dict(self._limite_cumul),
                "majoration_forfaitaire_enfant_reversion": dict(self._majoration_enfant),
                "minimum_pension_sncf": dict(self._minimum_pension_sncf)}

    def fiches(self) -> dict[str, dict]:
        """Les fiches préparées, sous leur nom : ce que le paquet du site porte."""
        return dict(self._fiches)

    def fiche(self, nom: str) -> dict | None:
        """La fiche préparée ``nom``, ou ``None`` : celle de la majoration
        forfaitaire pour enfant à charge, qui ne sert pas seule."""
        return self._fiches.get(nom)

    def fiche_du_regime(self, regime: str) -> dict | None:
        """La fiche préparée de la réversion d'un régime, ou ``None``."""
        nom = self._par_regime.get(regime)
        return None if nom is None else self._fiches[nom]

    def version(self, fiche: dict, date_effet: str, deces: str) -> dict | None:
        """La version de ``fiche`` pour une réversion qui prend effet à
        ``date_effet``, ouverte par un décès du jour ``deces`` (AAAA-MM-JJ)."""
        situation = {"liquidation.date_effet": date_effet, "conjoint.deces": deces}
        return versions.applicable(
            fiche, {nom: situation[nom] for nom in fiche["dates_qui_decident"]})


class Invalidites:
    """Les fiches de l'invalidité et de l'inaptitude (docs/architecture.md,
    § 11), dont le moteur lit les versions : la pension d'invalidité que la
    pension de vieillesse remplace à l'âge légal (``substitution``),
    l'inaptitude au travail (``inaptitude``), la retraite pour invalidité des
    fonctionnaires (``fonction_publique``), le départ anticipé des assurés
    handicapés (``handicap``). Chaque fiche dit ses régimes : les autres
    n'appliquent pas ses règles, et la fiche le dit en approximation.
    """

    #: Les fiches, sous le nom que le moteur leur donne.
    FICHES = {"substitution": "pension_d_invalidite_substituee",
              "inaptitude": "inaptitude_au_travail",
              "fonction_publique": "retraite_pour_invalidite_fonction_publique",
              "handicap": "retraite_anticipee_handicap"}

    def __init__(self, racine: Path) -> None:
        self._fiches: dict[str, dict] = {}
        for nom in self.FICHES.values():
            chemin = racine / "reference" / "regles" / f"{nom}.yaml"
            if not chemin.exists():
                continue
            brute = charger_yaml(chemin)
            self._fiches[nom] = versions.preparer(brute) | {
                "regimes": list(brute.get("regimes") or ())}

    def fiches(self) -> dict[str, dict]:
        """Les fiches préparées, sous leur nom : ce que le paquet du site porte."""
        return dict(self._fiches)

    def regimes(self, fiche: str) -> frozenset[str]:
        """Les régimes qui appliquent les règles de cette fiche."""
        preparee = self._fiches.get(self.FICHES[fiche])
        return frozenset(preparee["regimes"]) if preparee is not None else frozenset()

    def version(self, fiche: str, date_effet: str) -> dict | None:
        """La version de cette fiche pour une pension qui prend effet à
        ``date_effet`` (AAAA-MM-JJ), ou ``None``."""
        preparee = self._fiches.get(self.FICHES[fiche])
        if preparee is None:
            return None
        return versions.applicable(preparee, {"liquidation.date_effet": date_effet})

    def sans(self, fiche: str) -> Invalidites:
        """Les mêmes fiches, celle-ci retirée : ses régimes n'appliquent plus
        rien de ses règles. C'est ce que la page Avantages mesure en la
        retirant (:mod:`~retraite_notionnelle.avantages`)."""
        copie = object.__new__(Invalidites)
        copie._fiches = {nom: preparee for nom, preparee in self._fiches.items()
                         if nom != self.FICHES[fiche]}
        return copie


class CarrieresHorsDeFrance:
    """Les fiches des carrières hors de France (docs/architecture.md, § 11),
    dont le moteur lit les versions — la totalisation des périodes étrangères
    (``totalisation``), la pension proratisée (``proratisation``), le minimum
    contributif d'une pension proratisée (``minimum``), la résidence de
    l'allocation de solidarité aux personnes âgées (``residence``) —, et le
    tableau des accords, qui dit l'accord en vigueur avec chaque État
    (``data/reference/legislation/accords_internationaux.yaml``)."""

    #: Les fiches, sous le nom que le moteur leur donne.
    FICHES = {"totalisation": "totalisation_des_periodes_etrangeres",
              "proratisation": "pension_proratisee",
              "minimum": "minimum_contributif_international",
              "residence": "residence_et_minimum_vieillesse"}

    def __init__(self, racine: Path) -> None:
        self._fiches: dict[str, dict] = {}
        for nom in self.FICHES.values():
            chemin = racine / "reference" / "regles" / f"{nom}.yaml"
            if not chemin.exists():
                continue
            brute = charger_yaml(chemin)
            self._fiches[nom] = versions.preparer(brute) | {
                "regimes": list(brute.get("regimes") or ())}
        self.accords = charger_accords_internationaux(racine)

    def fiches(self) -> dict[str, dict]:
        """Les fiches préparées, sous leur nom : ce que le paquet du site porte."""
        return dict(self._fiches)

    def regimes(self, fiche: str) -> frozenset[str]:
        """Les régimes qui appliquent les règles de cette fiche."""
        preparee = self._fiches.get(self.FICHES[fiche])
        return frozenset(preparee["regimes"]) if preparee is not None else frozenset()

    def version(self, fiche: str, dates: dict[str, str]) -> dict | None:
        """La version de cette fiche à ces dates qui décident (AAAA-MM-JJ),
        ou ``None``."""
        preparee = self._fiches.get(self.FICHES[fiche])
        return None if preparee is None else versions.applicable(preparee, dates)

    def accord(self, pays: str, date_effet: str) -> dict | None:
        """L'accord que le tableau donne à cet État pour une pension qui prend
        effet à ``date_effet`` (AAAA-MM-JJ) : celui qui est alors en vigueur,
        et qui prend en compte les périodes accomplies avant lui. ``None``
        quand aucun ne l'est, ou que l'État n'est pas au tableau."""
        for accord in (self.accords.get(pays) or {}).get("accords", ()):
            if accord["de"] <= date_effet and (accord.get("a") is None
                                               or date_effet < accord["a"]):
                return accord
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
    tous les points. Les points de l'Agirc d'avant 2012 prennent aussi le
    pourcentage de service de l'année où la majoration est SERVIE (accord du
    9 février 1994, article 2) : 10 à 30 % jusqu'en 1994, 96 % de ce barème en
    1995, 85 % en 1996, 80 % depuis 1997. Voir ``majoration_enfants_points.csv``.
    """

    FICHIER = "majoration_enfants_points.csv"
    #: L'année de service que le barème sert à qui ne la dit pas : la dernière
    #: que la table borne.
    SERVI_DEPUIS_TOUJOURS = 2100

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, list[tuple[int, int, tuple[float, ...], Fiabilite,
                                          int, int]]] = {}
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
                        int(ligne["servi_debut"]), int(ligne["servi_fin"]),
                    ))

    def taux(self, regime: str, annee: int, nombre_enfants: int,
             annee_service: int | None = None) -> float | None:
        """Taux des points que ``regime`` a inscrits en ``annee``, servis en
        ``annee_service`` (la dernière année de la table sans elle) ; ``None``
        quand la table ne dit rien de ce régime ou de cette année."""
        service = self.SERVI_DEPUIS_TOUJOURS if annee_service is None else annee_service
        for debut, fin, bareme, _, servi_debut, servi_fin in self._table.get(regime, ()):
            if debut <= annee <= fin and servi_debut <= service <= servi_fin:
                return bareme[min(nombre_enfants, len(bareme) - 1)]
        return None

    def etapes(self, regime: str, annee: int, nombre_enfants: int,
               annee_service: int) -> list[tuple[int, float]]:
        """Les années de service, après ``annee_service``, où le taux des points
        que ``regime`` a inscrits en ``annee`` change, et le taux de chacune,
        dans l'ordre : le pourcentage de service de l'Agirc, de 1995 à 1997."""
        return sorted(
            (servi_debut, bareme[min(nombre_enfants, len(bareme) - 1)])
            for debut, fin, bareme, _, servi_debut, _fin in self._table.get(regime, ())
            if debut <= annee <= fin and servi_debut > annee_service)


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

    La table, et sa lecture au mois où les conditions sont réunies, sont
    documentées dans ``legislation/decote_regimes_speciaux.csv``.
    """

    FICHIER = "decote_regimes_speciaux.csv"


class MaximumDesCultes:
    """Le maximum de la pension du régime des cultes, l'année demandée.

    La fraction de pension des périodes d'avant 1998 ne dépend d'aucun
    salaire : c'est ce maximum, au prorata de la durée (D. 721-7 du code de
    1985 ; fiche ``cultes_fractions_de_pension``). Des arrêtés le fixent
    chaque année de 1979 à 1997 ; depuis, il suit les revalorisations des
    pensions du régime général (L. 382-27 ; décret n° 2006-1325, art. 2,
    VIII), jusqu'au montant que la caisse publie pour 2026, puis les prix.
    Le fichier en garde les ancres : ``legislation/cultes_maximum_pension.csv``.
    """

    #: La dernière année qu'un arrêté fixe.
    DERNIER_ARRETE = 1997

    def __init__(self, racine: Path, macro: DonneesMacro,
                 revalorisations: RevalorisationsPensions) -> None:
        self.macro = macro
        self.revalorisations = revalorisations
        self._table: dict[int, tuple[float, Fiabilite]] = {}
        chemin = racine / "reference" / "legislation" / "cultes_maximum_pension.csv"
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                self._table[int(ligne["annee"])] = (
                    float(ligne["valeur"]),
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                )

    def valeur(self, annee: int) -> tuple[float, Fiabilite] | None:
        """Le montant annuel en vigueur au 1er janvier de l'année, ou ``None``
        avant la création du régime.

        Une ancre passe avant tout calcul. Entre le dernier arrêté et l'ancre
        suivante, le montant de 1997 suit les coefficients de L. 161-23-1 —
        en 2020, celui des retraites de moins de 2 000 € par mois, que le
        maximum n'a jamais approchées — ; après la dernière ancre, les prix.
        """
        if annee in self._table:
            return self._table[annee]
        anterieures = [a for a in self._table if a < annee]
        if not anterieures:
            return None
        ancre = max(anterieures)
        valeur, fiabilite = self._table[ancre]
        if ancre <= self.DERNIER_ARRETE:
            coefficient, fiabilite_revalorisations = self.revalorisations.generale(
                date(ancre, 1, 1), date(annee, 1, 1), False, valeur / 12)
            return valeur * coefficient, min(fiabilite, fiabilite_revalorisations)
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

    La table seule : ses règles — les portes opposables, la durée réputée
    cotisée, l'âge ouvert ou proposé — en sont détachées, sous
    ``droit/carriere_longue.py`` (action 161, étape 3).
    """

    #: Génération de la règle générale, celle qui vaut à défaut d'une ligne
    #: plus précise.
    GENERATION_GENERALE = 1900.0

    #: Les rédactions de D. 351-1-2, une version par rédaction qui change ce
    #: qu'il répute cotisé : ses natures et leurs limites, à la date d'effet.
    FICHE_DES_REPUTES = "carriere_longue_reputes_cotises_autres"

    def __init__(self, racine: Path) -> None:
        fiche = racine / "reference" / "regles" / f"{self.FICHE_DES_REPUTES}.yaml"
        self._reputes = versions.preparer(charger_yaml(fiche)) if fiche.exists() else None
        self._table: dict[float, list[tuple[float, float, int, int, float, int, int | None,
                                            Fiabilite]]] = {}
        chemin = racine / "reference" / "legislation" / "carriere_longue.csv"
        if not chemin.exists():
            self._dates: list[float] = []
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                assurance = ligne["trimestres_assurance_supplementaires"].strip()
                self._table.setdefault(float(ligne["date_effet"]), []).append((
                    float(ligne["generation"]),
                    float(ligne["generation_fin"]),
                    int(ligne["age_debut_maximum"]),
                    int(ligne["trimestres_debut"]),
                    au_mois(float(ligne["age_depart"])),
                    int(ligne["trimestres_supplementaires"]),
                    int(assurance) if assurance else None,
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                ))
        self._dates = sorted(self._table)

    def fiches(self) -> dict[str, dict]:
        """La fiche préparée des périodes réputées cotisées, sous son nom : ce
        que le paquet du site porte."""
        return {} if self._reputes is None else {self._reputes["id"]: self._reputes}

    def avant(self, date: DateMois) -> CarriereLongue:
        """La même table, sans les textes qui prennent effet à compter de
        ``date`` : la carrière longue d'un droit contrefactuel. Au droit du
        31 août 2023, les portes du décret du 2 juillet 2012 valent à toute
        date d'effet ; à la loi de 2023 sans la suspension, celles du décret
        du 3 juin 2023."""
        copie = copy.copy(self)
        limite = self._annee_decimale(date)
        copie._table = {effet: portes for effet, portes in self._table.items()
                        if effet < limite - 1e-9}
        copie._dates = sorted(copie._table)
        return copie

    @staticmethod
    def _annee_decimale(date: DateMois) -> float:
        """L'année décimale d'une date d'effet, à la précision de la table.

        La table écrit le 1er septembre 2026 `2026.667`, quand huit douzièmes
        valent 2026,666 666… : sans l'arrondi, le premier mois d'un décret de
        septembre lisait encore le décret d'avant, et l'assuré né en décembre
        1965 partait au 1er octobre 2026 et non au 1er septembre (exemple
        `ur_racl_1965_decembre`). C'est le trou que ``Carriere.generation``
        referme déjà pour les générations.
        """
        return round(date.annee + (date.mois - 1) / 12.0, 3)


class SurcoteBaremes:
    """Barème DATÉ de la surcote — article D. 351-1-4 du code de la sécurité
    sociale, article L. 14 III du code des pensions.

    Chaque trimestre de surcote garde le taux en vigueur à la date où il a été
    ACCOMPLI, et, de 2004 à 2008, à la date d'effet de la pension : 0,75 %
    pour une pension prenant effet avant 2007 ; à compter de 2007 (décret
    n° 2006-1611, articles 1er et 3), 0,75 % pour les quatre premiers
    trimestres accomplis depuis 2004, 1 % à compter du cinquième et 1,25 %
    pour les trimestres postérieurs au soixante-cinquième anniversaire ;
    1,25 % pour tout trimestre accompli depuis le 1er janvier 2009. La fonction publique
    servait 0,75 % dans la limite de vingt trimestres jusqu'en 2008. Le
    modèle appliquait à tous les trimestres le taux de l'année du départ,
    ce qui servait 1,25 % à des trimestres de 2005 et 0,75 % à un cinquième
    trimestre de 2008. La circulaire Cnav 2018-04 (point 3) en donne trois
    exemples, que ``tests/temoins/exemples_officiels.yaml`` rejoue.
    """

    def __init__(self, racine: Path) -> None:
        self._lignes: list[tuple[str, float, float, int, bool, float,
                                 int | None, Fiabilite, float | None]] = []
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
                    float(ligne["effet_depuis"]) if ligne["effet_depuis"].strip() else None,
                ))

    def connait(self, bareme: str) -> bool:
        return any(ligne[0] == bareme for ligne in self._lignes)

    def coefficient(self, bareme: str, trimestres: list[tuple[DateMois, bool]],
                    effet: DateMois | None = None) -> tuple[float, Fiabilite | None]:
        """Coefficient de majoration pour ces trimestres de surcote, datés.

        ``trimestres`` donne, dans l'ordre chronologique, le premier mois de
        chaque trimestre civil de surcote et s'il est postérieur au
        soixante-cinquième anniversaire. Pour chaque trimestre, la ligne la
        plus favorable qui lui convient l'emporte, sous le plafond de
        trimestres qu'elle porte le cas échéant. Une ligne qui porte une date
        d'effet ne vaut que pour une pension ``effet`` prenant effet depuis.
        """
        au = None if effet is None else effet.annee + (effet.mois - 1) / 12.0
        servis: dict[int, int] = {}
        total = 0.0
        fiabilite: Fiabilite | None = None
        for rang, (date, apres_65) in enumerate(trimestres, start=1):
            valeur = date.annee + (date.mois - 1) / 12.0
            meilleure = None
            for indice, (code, debut, fin, rang_minimum, condition_65, taux,
                         maximum, fiab, depuis) in enumerate(self._lignes):
                if code != bareme or not debut - 1e-9 <= valeur <= fin + 1e-9:
                    continue
                if depuis is not None and (au is None or au < depuis - 1e-9):
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
    revalorisé depuis comme les pensions civiles. Une durée de quinze ans en ouvre 57,5 %,
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
    #: Année à partir de laquelle la référence est gelée, puis revalorisée
    #: comme les pensions civiles, au lieu de suivre le point d'indice.
    ANNEE_GEL = 2004

    def __init__(self, racine: Path, macro: DonneesMacro) -> None:
        self.macro = macro
        # Les revalorisations des pensions civiles, que la référence suit
        # depuis 2004 : les décrets jusqu'en 2008, l'article L. 161-23-1
        # ensuite (L. 16).
        revalorisations = RevalorisationsPensions(racine)
        self._revalorisations = tuple(
            [r for r in revalorisations.fonction_publique
             if r.date_effet < DEBUT_REGLE_GENERALE_PUBLIC]
            + [r for r in revalorisations.generales
               if r.date_effet >= DEBUT_REGLE_GENERALE_PUBLIC])
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
        # L'indice majoré dont le traitement est celui de l'indice 100 (article
        # 7 du décret n° 85-1148), par date d'effet : (année, mois, jour,
        # indice, fiabilité), dans l'ordre.
        self._indice_100: list[tuple[int, int, int, int, Fiabilite]] = []
        chemin = dossier / "indice_100_fonction_publique.csv"
        if chemin.exists():
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    annee, mois, jour = (int(x) for x in ligne["date_effet"].split("-"))
                    self._indice_100.append((annee, mois, jour, int(ligne["indice_majore"]),
                                             Fiabilite.depuis_texte(ligne["fiabilite"])))
            self._indice_100.sort()

    def traitement_de_l_indice_100(self, annee: int, mois: int
                                   ) -> tuple[float, Fiabilite] | None:
        """Le traitement brut annuel de l'indice 100 de la fonction publique au
        premier jour de ``mois`` : celui de l'indice majoré que l'article 7 du
        décret n° 85-1148 lui fait correspondre ce jour-là, au point de l'année
        (au 1er janvier ; le dernier connu au-delà de la série). ``None`` avant
        la rédaction d'origine de l'article, le 5 novembre 1985, ou sans point."""
        applicable = None
        for debut_annee, debut_mois, debut_jour, indice, fiabilite in self._indice_100:
            if (debut_annee, debut_mois, debut_jour) <= (annee, mois, 1):
                applicable = (indice, fiabilite)
        point = self._point_indice(annee)
        if applicable is None or point is None:
            return None
        return applicable[0] * point[0], min(applicable[1], point[1])

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

    def reference(self, annee_liquidation: int, mois: int = 1
                  ) -> tuple[float, Fiabilite] | None:
        """Montant plein du minimum garanti, quarante ans de services, pour
        une pension prenant effet au premier jour de ``mois``.

        Deux cas :

        * **depuis 2004**, la référence est la valeur de l'indice majoré 227
          au 1er janvier 2004, « revalorisé dans les conditions prévues à
          l'article L. 16 » (L. 17) : comme les pensions civiles — les décrets
          jusqu'en 2008, l'article L. 161-23-1 ensuite —, de revalorisation en
          revalorisation jusqu'à la date d'effet. La chaîne part du montant
          publié le plus récent (``minimum_garanti_montants.csv``, un 1er
          janvier), qu'elle redonne au centime ; au-delà de la dernière
          revalorisation connue, elle se projette sur les prix. Le modèle la
          projetait sur les prix entre deux montants publiés, à l'année : 2,9 %
          de trop en 2019, 4,6 % en janvier 2022, qui recevait dès janvier le
          +4 % de juillet ;
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
        anterieures = [a for a in self._annees_montants if a <= annee_liquidation]
        ancre = max(anterieures) if anterieures else self._annees_montants[0]
        valeur, fiabilite = self._montants[ancre]
        coefficient, fiabilite_chaine = self.revalorisation(
            date(ancre, 1, 1), date(annee_liquidation, mois, 1))
        valeur *= coefficient
        derniere = self._revalorisations[-1].date_effet.year if self._revalorisations else ancre
        if annee_liquidation > max(derniere, ancre):
            valeur *= self.macro.coefficient_prix(max(derniere, ancre), annee_liquidation)
        return (valeur * indice / self.INDICE_REFERENCE,
                min(fiabilite_bareme, fiabilite, fiabilite_chaine))

    def revalorisation(self, depuis: date, jusqu_a: date) -> tuple[float, Fiabilite]:
        """Le coefficient des revalorisations des pensions civiles qui tombent
        après ``depuis`` et au plus tard à ``jusqu_a``, et sa fiabilité.

        En 2020, le coefficient de l'article L. 161-25, 1 %, et non la
        dérogation de 0,3 % des pensions de plus de 2 000 € : c'est celui que
        la chaîne des montants publiés depuis porte — 1 187,26 € par mois en
        2021, 1 248,33 € en juillet 2022, 16 396,19 € par an au 1er janvier
        2026, que le service des retraites de l'État publie. Avec 0,3 %, elle
        en manquait 0,69 %, comme le montant de 2020 que le dépôt portait.
        """
        return produit(RevalorisationsPensions.retenues(
            self._revalorisations, depuis, jusqu_a, False, 0.0))

    def valeur_d_un_indice(self, indice: int, annee: int) -> tuple[float, Fiabilite] | None:
        """Ce que vaut un indice majoré l'année demandée, revalorisé comme la
        référence du minimum garanti depuis le 1er janvier 2004 : la rente
        viagère d'invalidité lit l'indice 681 (L. 28), trois fois le 227.
        Avant 2004, le traitement de l'indice au point de l'année."""
        reference = self.reference(annee)
        bareme = self.bareme(annee)
        if reference is None or bareme is None:
            return None
        return reference[0] * indice / bareme[0], reference[1]

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
                duree_maximum: int | None = None, mois: int = 1
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
        reference = self.reference(annee_liquidation, mois)
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
    comme les années postérieures au dernier barème publié — sauf pour un régime
    dont ``prolongement_points.csv`` dit ce que suit le prix d'achat
    (:meth:`achat_prolonge`). Ceux dont la caisse publie un barème EN POINTS
    plutôt qu'un prix d'achat — le régime de base des libéraux, la
    complémentaire agricole — n'en ont pas besoin : leur fiche porte
    ``points_maximum``, et seule la valeur de service est lue ici.

    La valeur de service d'une année est celle du 31 décembre ; celle d'un
    JOUR, que la liquidation sert, se lit dans ``valeurs_service_datees.csv``
    (:meth:`service_au`).
    """

    #: Les indices qu'un prix d'achat peut suivre au-delà du dernier barème.
    INDICES_DU_PROLONGEMENT = ("salaire_moyen",)
    #: Ceux qu'une convention de projection peut faire suivre à une valeur du
    #: point (``conventions_points`` de ``macro/hypotheses_projection.yaml``).
    INDICES_DES_CONVENTIONS = ("prix", "salaire_moyen")

    def __init__(self, racine: Path, conventions: bool = False) -> None:
        self._table: dict[tuple[str, str], dict[int, tuple[float, Fiabilite]]] = {}
        #: Ce que suit le prix d'achat au-delà du dernier barème publié :
        #: régime -> (indice, décalage en années, fiabilité du prix prolongé).
        self._prolongements: dict[str, tuple[str, int, Fiabilite]] = {}
        #: La valeur de service au jour où elle prend effet : régime ->
        #: (dates (année, mois), valeurs et fiabilités), dans l'ordre des dates.
        self._datees: dict[str, tuple[list[tuple[int, int]],
                                      list[tuple[float, Fiabilite]]]] = {}
        #: Ce que le COR suppose d'une valeur du point au-delà du dernier
        #: barème : (régime, mesure) -> lignes (depuis, indice, écart,
        #: décalage), dans l'ordre. Voir :meth:`indice_convenu`. Vide sans
        #: ``conventions`` : ce que lit le simulateur individuel
        #: (``Parametres.conventions_cor``).
        self._conventions: dict[tuple[str, str], list[tuple[int, str, float, int]]] = {}
        hypotheses = racine / "reference" / "macro" / "hypotheses_projection.yaml"
        if conventions and hypotheses.exists():
            conventions = charger_yaml(hypotheses).get("conventions_points") or {}
            for regime, mesures in conventions.items():
                for mesure, lignes in mesures.items():
                    for ligne in lignes:
                        if ligne["suit"] not in self.INDICES_DES_CONVENTIONS:
                            raise ValueError(
                                f"hypotheses_projection.yaml : la {mesure} de "
                                f"{regime} suit {ligne['suit']!r}, que le moteur "
                                f"ne sait pas prolonger")
                    self._conventions[(regime, mesure)] = sorted(
                        (int(l["depuis"]), l["suit"], float(l["ecart"]),
                         int(l["decalage"])) for l in lignes)
        dossier = racine / "reference" / "regimes"
        chemin = dossier / "valeurs_service_datees.csv"
        if chemin.exists():
            lues: dict[str, list[tuple[tuple[int, int], float, Fiabilite]]] = {}
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    annee, mois, jour = (int(n) for n in ligne["date_effet"].split("-"))
                    if jour != 1:
                        raise ValueError(
                            f"valeurs_service_datees.csv : {ligne['regime']} "
                            f"{ligne['date_effet']}, une valeur prend effet le 1er du mois")
                    lues.setdefault(ligne["regime"], []).append(
                        ((annee, mois), float(ligne["valeur"]),
                         Fiabilite.depuis_texte(ligne["fiabilite"])))
            for regime, datees in lues.items():
                datees.sort(key=lambda d: d[0])
                self._datees[regime] = ([d for d, _, _ in datees],
                                        [(v, f) for _, v, f in datees])
        chemin = dossier / "valeurs_point.csv"
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
        chemin = dossier / "prolongement_points.csv"
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                if ligne["suit"] not in self.INDICES_DU_PROLONGEMENT:
                    raise ValueError(
                        f"prolongement_points.csv : le prix d'achat de "
                        f"{ligne['regime']} suit {ligne['suit']!r}, que le moteur "
                        f"ne sait pas prolonger")
                self._prolongements[ligne["regime"]] = (
                    ligne["suit"], int(ligne["decalage"]),
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
        retombent sur le rendement instantané, qui, lui, s'assume approximatif,
        ou sur le prolongement que le texte du régime écrit
        (:meth:`achat_prolonge`).
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

    def achat_prolonge(self, regime: str, annee: int,
                       macro: DonneesMacro) -> tuple[float, float, Fiabilite] | None:
        """Prix d'achat d'un point, publié ou, au-delà du dernier barème,
        prolongé comme ``regimes/prolongement_points.csv`` le dit du régime.

        Ce n'est pas un gel : le dernier salaire de référence publié suit
        l'indice que son texte nomme, au dernier taux d'appel. La valeur d'achat
        de l'Agirc-Arrco « évolue au premier janvier de chaque année [...] comme
        le salaire annuel moyen des ressortissants du régime tel qu'estimé pour
        l'exercice précédent » (accords du 10 mai 2019, article 2, et du 5
        octobre 2023, article 5.1), et l'accord qui institue le régime la
        détermine « en fonction du taux d'évolution du salaire moyen des
        ressortissants du régime » (17 novembre 2017, article 28) : au-delà de
        2026, le salaire moyen du modèle la porte, avec un an de retard (fiche
        ``agirc_arrco_valeur_achat``). Les points de ces années s'achètent donc
        plus cher que les prix ne le feraient, et la valeur de service, qui les
        sert, suit les prix (``valeurDuPoint`` de ``moteur/js/droit/liquider.js``).
        Un régime sans prolongement n'a pas de prix au-delà de son dernier
        barème : ses cotisations passent par le rendement instantané.
        """
        achat = self.achat(regime, annee)
        if achat is not None:
            return achat
        regle = self._prolongements.get(regime)
        publiees = self._table.get((regime, "salaire_reference"))
        if regle is None or not publiees or annee <= max(publiees):
            return None
        derniere = max(publiees)
        dernier = self.achat(regime, derniere)
        if dernier is None:
            return None
        suit, decalage, fiabilite = regle
        reference, taux_appel, fiabilite_achat = dernier
        return (
            reference * self.indice_convenu(regime, "valeur_achat", derniere,
                                            annee, macro, (suit, decalage)),
            taux_appel, min(fiabilite_achat, fiabilite),
        )

    def indice_convenu(self, regime: str, mesure: str, depuis: int, jusqu_a: int,
                       macro: DonneesMacro, defaut: tuple[str, int]) -> float:
        """Ce dont une valeur du point (``valeur_service`` ou ``valeur_achat``)
        croît de ``depuis`` à ``jusqu_a``, au-delà du dernier barème publié.

        Chaque année prend la ligne de ``conventions_points``
        (``macro/hypotheses_projection.yaml``) en vigueur — l'indice qu'elle
        suit, le point qu'elle en retranche, l'année de l'indice —, ou, avant
        la première, l'indice ``defaut`` (indice, décalage), sans écart : ce
        que le modèle faisait avant de suivre le COR. Le COR fait suivre à
        l'Agirc-Arrco le salaire moyen moins 1,16 point de 2027 à 2037, moins
        0,86 ensuite, pour les deux valeurs dès 2038 (rapport annuel de juin
        2026, encadré « Le pilotage de l'Agirc-Arrco ») : une hypothèse de
        projection, et non du droit.
        """
        lignes = self._conventions.get((regime, mesure), ())
        coefficient = 1.0
        for annee in range(depuis + 1, jusqu_a + 1):
            suit, decalage = defaut
            ecart = 0.0
            for debut, indice, retranche, retard in lignes:
                if debut <= annee:
                    suit, ecart, decalage = indice, retranche, retard
            if suit == "prix":
                croissance = macro.coefficient_prix(annee - decalage - 1, annee - decalage)
            else:
                croissance = macro.coefficient_salaire_moyen(annee - decalage - 1,
                                                             annee - decalage)
            coefficient *= croissance + ecart
        return coefficient

    def regimes_convenus(self, mesure: str) -> tuple[str, ...]:
        """Les régimes dont le COR suppose la trajectoire de cette valeur."""
        return tuple(sorted(r for r, m in self._conventions if m == mesure))

    def a_une_convention(self, regime: str, mesure: str) -> bool:
        """Le COR suppose-t-il une trajectoire à cette valeur du point ?"""
        return (regime, mesure) in self._conventions

    #: Taux contractuel de tranche B auquel la garantie est écrite : « 144
    #: points pour un taux contractuel de 16 % » (accord du 8 décembre 1988,
    #: selon G. Briens, 1990, n° 219), « 120 points pour un taux de cotisation
    #: de 16 % » (accord du 25 avril 1996, art. 7), « taux unique 16 % »
    #: (circulaire Agirc 2003-9-DRE). Le forfait publié est celui de ce taux.
    TAUX_DE_LA_GARANTIE = 0.16

    def garantie(self, regime: str, periode, annee: int, part: float,
                 quotite: float, taux_contractuel: float | None = None
                 ) -> tuple[float, Fiabilite] | None:
        """Cotisation de la garantie minimale de points d'une ligne de l'année,
        taux d'appel compris, et sa fiabilité ; ``None`` si la période n'a pas
        de garantie ou si le point n'a pas de prix cette année-là.

        C'est le FORFAIT PUBLIÉ (``cotisation_garantie``) : 2 843 F en 1989,
        872,52 € en 2018. Il achète ses points au prix de l'année, comme toute
        cotisation — 144 points en 1989 au taux de 16 %, 120 en 2018, et 136
        seulement en 1996, quand l'accord du 25 avril 1996 majora le salaire de
        référence d'un forfait déjà fixé. La garantie est une ASSIETTE minimale
        de tranche B, que le taux de l'entreprise fait cotiser : « un nombre de
        points proportionnel au taux de cotisations de l'entreprise sur
        tranche B », 72 points à 8 %, 108 à 12 %, 144 à 16 % (G. Briens, 1990).
        Au taux de la période, le forfait en vaut donc la part, jusqu'à ce que
        le taux minimal atteigne 16 %, en 1999. Il se proratise comme ses
        points, sur la durée de présence et sur la quotité du temps partiel
        (:meth:`PeriodeRegime.points_garantis`). Une année sans forfait publié
        retombe sur les points de la fiche, au prix de l'année. Le scénario 1
        en tire les points, le compte notionnel l'assiette qui la prélève.

        ``taux_contractuel`` remplace le taux de la période : l'allocation
        spéciale du FNE valide la tranche B à 8 % ou 12 %, « assortis de la
        GMP correspondante » (guide réglementaire Agirc-Arrco, VII.3.1.6.2).
        """
        points = periode.points_garantis(part, quotite)
        if points is None:
            return None
        achat = self.achat(regime, annee)
        if achat is None:
            return None
        reference, taux_appel, fiabilite = achat
        if taux_contractuel is None:
            taux_contractuel = periode.taux_cotisation_retraite / taux_appel
        proportion = min(1.0, taux_contractuel / self.TAUX_DE_LA_GARANTIE)
        forfaits = self._table.get((regime, "cotisation_garantie"))
        if forfaits and min(forfaits) <= annee <= max(forfaits):
            forfait, fiabilite_forfait = self._en_vigueur(
                regime, "cotisation_garantie", annee)
            return forfait * proportion * part * quotite, fiabilite_forfait
        return points * proportion * reference * taux_appel, fiabilite

    def derniere_annee_servie(self, regime: str) -> int | None:
        valeurs = self._table.get((regime, "valeur_service"))
        return max(valeurs) if valeurs else None

    def derniere_annee_achetee(self, regime: str) -> int | None:
        """La dernière année dont le salaire de référence est publié."""
        valeurs = self._table.get((regime, "salaire_reference"))
        return max(valeurs) if valeurs else None

    def premiere_annee_servie(self, regime: str) -> int | None:
        valeurs = self._table.get((regime, "valeur_service"))
        return min(valeurs) if valeurs else None

    def service(self, regime: str, annee: int) -> tuple[float, Fiabilite] | None:
        return self._en_vigueur(regime, "valeur_service", annee)

    def service_au(self, regime: str, annee: int,
                   mois: int) -> tuple[float, Fiabilite] | None:
        """La valeur de service en vigueur le 1er du mois ``mois`` de ``annee``.

        Une pension se liquide à SA date d'effet, « par la valeur de service du
        point de retraite du régime à cette même date » (circulaire Agirc-Arrco
        2020-02-DRJ, sur l'article 92 de l'accord du 17 novembre 2017). La
        valeur du 31 décembre servait par avance à un départ de janvier 2022 le
        relèvement de novembre : 5,12 % de trop. ``valeurs_service_datees.csv``
        date chaque valeur au jour de son effet, jusqu'à la dernière décision
        publiée ; au-delà, le régime se relève une fois l'an, au mois de cette
        décision (:meth:`millesime`). Un régime que le fichier ne date pas, ou
        une date antérieure à sa première ligne, garde la valeur du 31 décembre
        de l'année.
        """
        datees = self._datees.get(regime)
        if datees is None or (annee, mois) < datees[0][0]:
            return self.service(regime, annee)
        dates, valeurs = datees
        derniere, releve = dates[-1]
        if (annee, mois) < (derniere + 1, releve):
            return valeurs[bisect_right(dates, (annee, mois)) - 1]
        return self.service(regime, self.millesime(regime, annee, mois))

    def millesime(self, regime: str, annee: int, mois: int) -> int:
        """L'année dont la valeur du 31 décembre est en vigueur le 1er du mois
        ``mois`` de ``annee`` : ``annee`` dès le relèvement de l'année, la
        précédente avant lui. Le relèvement tombe au mois de la dernière
        décision datée du régime — le 1er novembre à l'Agirc-Arrco, « chaque
        année » (accord du 17 novembre 2017, article 27) ; un régime que
        ``valeurs_service_datees.csv`` ne date pas se relève au 1er janvier."""
        datees = self._datees.get(regime)
        if datees is None:
            return annee
        return annee if mois >= datees[0][-1][1] else annee - 1


#: La règle du minimum contributif quand la fiche manque : celle du droit en
#: vigueur (version ``avpf_et_ava_2023`` de la fiche ``minimum_contributif``).
#: La série de la pension minimum d'avant le 1er avril 1983 parmi les montants
#: datés du minimum (:meth:`MinimumContributif.pension_minimum`).
PENSION_MINIMUM = "pension_minimum"

REGLE_DU_MINIMUM_EN_VIGUEUR = {
    "existe": True,
    "majoration": "periodes_cotisees",
    "seuil_trimestres_cotises": 120,
    "plafond_avpf": 24,
    "ecretement": True,
    "cumul_des_minima": False,
    "duree_tous_regimes": True,
}


class MinimumContributif:
    """Minimum contributif, minimum majoré et plafond d'écrêtement, et la règle
    que leur applique la date d'effet de la pension.

    Trois grandeurs, et pas une seule :

    * le **minimum**, auquel est portée la pension de base d'un assuré au taux
      plein, au prorata de sa durée dans le régime ;
    * le **minimum majoré**, créé au 1er janvier 2004, servi à sa place au
      titre des périodes COTISÉES — près d'un cinquième au-dessus du premier ;
    * le **plafond d'écrêtement** de l'article L. 173-2, pour les pensions qui
      prennent effet depuis le 1er janvier 2012 : le complément est rogné dès
      que l'ensemble des pensions dépasse ce total.

    **Des montants datés, et non des ancres.** Le fichier porte chaque date de
    revalorisation depuis le 1er avril 1983 : les ancres du code (R. 351-25,
    D. 351-2-1, D. 173-21-0-0-1), certifiées, et entre elles ce que la Cnav a
    servi, transcrit de son barème. Le modèle lit le montant EN VIGUEUR le
    premier jour du mois de la date d'effet. Il reliait jusqu'au 4 octobre
    2026 six ancres par les prix : le majoré de 2004 sortait 7,9 % trop haut,
    celui de 2019 4,7 %, et la première ancre, « 2007 », était le montant du
    1er janvier 2008. Au-delà du dernier montant publié, il revalorise sur le
    SMIC, comme la loi le fait depuis 2023 pour les minima (L. 351-10) et
    depuis 2012 pour le plafond (D. 173-21-0-0-1).

    **La règle**, elle, est celle de la fiche ``minimum_contributif``, dont le
    moteur lit la version qui vaut à la date d'effet : pas de minimum avant le
    1er avril 1983, pas de majoration avant 2004, puis une majoration sans
    distinction des périodes jusqu'en juin 2005, le seuil de 120 trimestres
    cotisés depuis avril 2009, l'écrêtement depuis 2012, l'AVPF depuis
    septembre 2023.
    """

    def __init__(self, racine: Path, macro: DonneesMacro) -> None:
        self.macro = macro
        self._table: dict[str, tuple[tuple[str, float, Fiabilite], ...]] = {}
        chemin = racine / "reference" / "legislation" / "minimum_contributif.csv"
        if chemin.exists():
            lues: dict[str, list[tuple[str, float, Fiabilite]]] = {}
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    lues.setdefault(ligne["mesure"], []).append((
                        ligne["date"], float(ligne["valeur"]),
                        Fiabilite.depuis_texte(ligne["fiabilite"])))
            self._table = {mesure: tuple(sorted(datees))
                           for mesure, datees in lues.items()}
        #: Avant le 1er avril 1983, la pension minimum de L. 345, au montant de
        #: l'allocation aux vieux travailleurs salariés, à chaque date depuis
        #: 1945 (action 138, étape 6).
        avant_1983 = racine / "reference" / "legislation" / "pension_minimum_avant_1983.csv"
        if avant_1983.exists():
            with avant_1983.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                self._table[PENSION_MINIMUM] = tuple(sorted(
                    (ligne["date"], float(ligne["valeur"]),
                     Fiabilite.depuis_texte(ligne["fiabilite"]))
                    for ligne in csv.DictReader(lignes)))
        fiche = racine / "reference" / "regles" / "minimum_contributif.yaml"
        self._fiche = versions.preparer(charger_yaml(fiche)) if fiche.exists() else None

    def fiche(self) -> dict | None:
        """La fiche préparée : ce que le paquet du site porte."""
        return self._fiche

    def regle(self, date_effet: str) -> dict:
        """Les paramètres de la version qui vaut pour une pension prenant effet
        à ``date_effet`` (AAAA-MM-JJ) : ``existe``, ``majoration`` (« aucune »,
        « sans_distinction », « periodes_cotisees »),
        ``seuil_trimestres_cotises``, ``plafond_avpf``, ``ecretement``,
        ``cumul_des_minima``, ``duree_tous_regimes``."""
        if self._fiche is None:
            return dict(REGLE_DU_MINIMUM_EN_VIGUEUR)
        version = versions.applicable(self._fiche, {"liquidation.date_effet": date_effet})
        return dict(REGLE_DU_MINIMUM_EN_VIGUEUR if version is None
                    else version["parametres"])

    def _en_vigueur(self, mesure: str, annee: int, mois: int, sur_les_prix: bool = False
                    ) -> tuple[float, Fiabilite] | None:
        """Le montant en vigueur le premier jour de ce mois, ``None`` avant le
        premier : un montant connu, ou, au-delà du dernier, ce dernier
        revalorisé sur le SMIC de chaque année traversée, ou sur les prix."""
        datees = self._table.get(mesure)
        if not datees:
            return None
        jour = f"{annee:04d}-{mois:02d}-01"
        rang = bisect_right(datees, (jour, float("inf")))
        if rang == 0:
            return None
        date_valeur, valeur, fiabilite = datees[rang - 1]
        derniere = int(datees[-1][0][:4])
        if rang == len(datees) and annee > derniere:
            valeur *= (self.macro.coefficient_prix(derniere, annee) if sur_les_prix
                       else self.macro.coefficient_smic(derniere, annee))
        return valeur, fiabilite

    def avts(self, annee: int, mois: int = 1) -> tuple[float, Fiabilite] | None:
        """L'allocation aux vieux travailleurs salariés en vigueur le premier
        jour du mois, en euros par an : la série de la pension minimum, que les
        mêmes textes fixent jusqu'en 1983, et que le barème de la Cnav prolonge
        jusqu'en 2026 ; au-delà, revalorisée sur les prix. ``None`` avant 1945.
        Le maximum des points de retraite proportionnelle agricole la lit
        (R. 732-70)."""
        return self._en_vigueur(PENSION_MINIMUM, annee, mois, sur_les_prix=True)

    def pension_minimum(self, annee: int, mois: int = 1) -> tuple[float, Fiabilite]:
        """La pension minimum d'avant le 1er avril 1983 en vigueur le premier
        jour du mois, en euros par an : le montant de l'allocation aux vieux
        travailleurs salariés, que les mêmes textes fixent (fiche
        ``minimum_contributif``, versions ``pension_minimum_de_*``). Zéro avant
        1945 ; le dernier montant, celui du 1er janvier 1983, n'est lu que
        jusqu'au 31 mars 1983, la règle de la date d'effet l'arrêtant là."""
        lu = self._en_vigueur(PENSION_MINIMUM, annee, mois)
        return (0.0, Fiabilite.CERTIFIEE) if lu is None else lu

    def valeurs(self, annee: int, mois: int = 1) -> tuple[float, float, float, Fiabilite]:
        """Montant de base, montant majoré et plafond d'écrêtement en vigueur le
        premier jour du mois, en euros par an.

        Les deux montants sont rendus ensemble parce que le droit les additionne
        plutôt qu'il ne choisit entre eux : la pension est portée au montant de
        BASE au prorata de la durée d'assurance acquise dans le régime, puis
        l'écart entre le majoré et le base s'y ajoute au prorata de la seule
        durée COTISÉE. Avant le 1er avril 1983, il n'y a pas de minimum : tout
        vaut zéro ; avant 2004, pas de majoration : le majoré vaut le minimum ;
        avant 2012, pas d'écrêtement : le plafond vaut zéro, et la règle de la
        date d'effet (:meth:`regle`) ne le lit pas.
        """
        if not self._table:
            return 0.0, 0.0, 0.0, Fiabilite.ESTIMEE
        base = self._en_vigueur("montant_base", annee, mois)
        if base is None:
            return 0.0, 0.0, 0.0, Fiabilite.CERTIFIEE
        majore = self._en_vigueur("montant_majore", annee, mois) or base
        plafond = self._en_vigueur("plafond_ecretement", annee, mois)
        fiabilite = min(base[1], majore[1], *(() if plafond is None else (plafond[1],)))
        return base[0], majore[0], 0.0 if plafond is None else plafond[0], fiabilite


#: La règle de la pension majorée de référence quand sa fiche manque : aucune
#: majoration.
SANS_PENSION_MAJOREE = {
    "existe": False, "duree_minimale": None, "montant": None, "montant_reduit": None,
    "seuil_chef": None, "plafond": None, "majorations_de_duree": False,
}

#: Les mesures que leur texte revalorise comme les pensions de base : la PMR
#: et le plafond des pensions prises avant septembre 2023 (D. 732-111,
#: D. 732-113, I) ; au-delà du dernier barème, sur les prix, comme elles.
PMR_SUR_LES_PRIX = frozenset({"pmr_chef", "pmr_conjoint", "plafond"})


class PensionMajoreeReference:
    """La pension majorée de référence des non-salariés agricoles (PMR), le
    plafond de son écrêtement, et la règle que leur applique la date d'effet.

    **Des montants datés** (``legislation/pension_majoree_reference.csv``),
    une série par mesure : la PMR des chefs d'exploitation puis la PMR unique
    (``pmr_chef``), celle des autres périodes jusqu'en 2021 (``pmr_conjoint``),
    celle des pensions de septembre 2023 (``pmr_depuis_septembre_2023``), et
    les plafonds. Les ancres de D. 732-111 et D. 732-113, et entre elles ce
    que la revalorisation de l'article L. 161-23-1 en fait : aucune caisse
    n'en publie la série (``scripts/fetch/dila_legi_pension_majoree.py``).

    **La règle** est celle de la fiche ``pension_majoree_reference``, dont le
    moteur lit la version de la date d'effet : rien avant 2009, deux montants
    et une durée minimale jusqu'en 2021, un seul depuis, relevé de cent euros
    par mois en septembre 2023, et le plafond de l'article L. 173-2 depuis
    2026 (``pensionMajoree`` de ``moteur/js/droit/completer.js``).
    """

    def __init__(self, racine: Path, macro: DonneesMacro) -> None:
        self.macro = macro
        self._table: dict[str, tuple[tuple[str, float, Fiabilite], ...]] = {}
        chemin = racine / "reference" / "legislation" / "pension_majoree_reference.csv"
        if chemin.exists():
            lues: dict[str, list[tuple[str, float, Fiabilite]]] = {}
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    lues.setdefault(ligne["mesure"], []).append((
                        ligne["date"], float(ligne["valeur"]),
                        Fiabilite.depuis_texte(ligne["fiabilite"])))
            self._table = {mesure: tuple(sorted(datees))
                           for mesure, datees in lues.items()}
        fiche = racine / "reference" / "regles" / "pension_majoree_reference.yaml"
        self._fiche = versions.preparer(charger_yaml(fiche)) if fiche.exists() else None

    def fiche(self) -> dict | None:
        """La fiche préparée : ce que le paquet du site porte."""
        return self._fiche

    def regle(self, date_effet: str) -> dict:
        """Les paramètres de la version qui vaut pour une pension prenant effet
        à ``date_effet`` (AAAA-MM-JJ) : ``existe``, ``duree_minimale`` (en
        trimestres non salariés agricoles), ``montant`` et ``montant_reduit``
        (les séries de la PMR entière et de celle de qui n'a pas ``seuil_chef``
        trimestres de chef), ``plafond`` (une série, ou
        ``minimum_contributif`` : celui de l'article L. 173-2),
        ``majorations_de_duree``."""
        if self._fiche is None:
            return dict(SANS_PENSION_MAJOREE)
        version = versions.applicable(self._fiche, {"liquidation.date_effet": date_effet})
        return dict(SANS_PENSION_MAJOREE if version is None else version["parametres"])

    def montant(self, mesure: str, annee: int, mois: int = 1
                ) -> tuple[float, Fiabilite] | None:
        """Le montant de la mesure en vigueur le premier jour du mois, en euros
        par an ; ``None`` pour une mesure inconnue. Un mois qui précède la
        série lit son premier montant — la PMR des pensions de septembre 2023
        que le complément de la RCO lit au 1er janvier 2023 ; au-delà du
        dernier, ce dernier revalorisé sur les prix pour une mesure qui suit
        les pensions de base (``PMR_SUR_LES_PRIX``), sur le SMIC pour les
        autres, comme le minimum contributif et le plafond de L. 173-2."""
        datees = self._table.get(mesure)
        if not datees:
            return None
        jour = f"{annee:04d}-{mois:02d}-01"
        rang = max(1, bisect_right(datees, (jour, float("inf"))))
        _, valeur, fiabilite = datees[rang - 1]
        derniere = int(datees[-1][0][:4])
        if rang == len(datees) and annee > derniere:
            valeur *= (self.macro.coefficient_prix(derniere, annee) if mesure in PMR_SUR_LES_PRIX
                       else self.macro.coefficient_smic(derniere, annee))
            fiabilite = min(fiabilite, Fiabilite.ESTIMEE)
        return valeur, fiabilite


#: La règle du complément différentiel de la RCO quand sa fiche manque : aucun
#: complément.
SANS_COMPLEMENT_DIFFERENTIEL = {
    "existe": False, "pourcentage": None, "formule": None, "condition": None,
    "seuil_chef": None, "plafond_tous_regimes": False, "pmr_au_mois": None,
    "majorations_de_duree": False,
}


class ComplementDifferentielRco:
    """Le complément différentiel de points de la retraite complémentaire des
    non-salariés agricoles (L. 732-63) : le SMIC net agricole horaire de
    chaque 1er janvier, et la règle que la date d'effet lui applique.

    **Le SMIC net agricole** (``legislation/complement_differentiel_rco.csv``)
    se tire des montants que la MSA, ou un rapport parlementaire, publient ;
    les autres années, du SMIC brut moins les taux salariaux d'un non cadre
    de la production agricole, que ``scripts/fetch/msa_smic_net_agricole.py``
    refait et confronte à ces montants. Au-delà de la dernière, il suit le
    SMIC brut du modèle.

    **La règle** est celle de la fiche ``complement_differentiel_rco`` : rien
    avant 2015, 73, 74 puis 75 % d'une carrière complète, 85 % et un plafond
    tous régimes depuis novembre 2021, le taux plein suffisant depuis
    septembre 2023 (``complementDifferentiel`` de ``moteur/js/droit/completer.js``).
    """

    def __init__(self, racine: Path, macro: DonneesMacro) -> None:
        self.macro = macro
        self._smic: dict[int, tuple[float, Fiabilite]] = {}
        chemin = racine / "reference" / "legislation" / "complement_differentiel_rco.csv"
        if chemin.exists():
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    self._smic[int(ligne["annee"])] = (
                        float(ligne["smic_net_horaire"]),
                        Fiabilite.depuis_texte(ligne["fiabilite"]))
        fiche = racine / "reference" / "regles" / "complement_differentiel_rco.yaml"
        self._fiche = versions.preparer(charger_yaml(fiche)) if fiche.exists() else None

    def fiche(self) -> dict | None:
        """La fiche préparée : ce que le paquet du site porte."""
        return self._fiche

    def table(self) -> dict[int, tuple[float, Fiabilite]]:
        """Le SMIC net agricole horaire, par année : ce que le paquet porte."""
        return dict(self._smic)

    def regle(self, date_effet: str) -> dict:
        """Les paramètres de la version qui vaut pour une pension prenant effet
        à ``date_effet`` (AAAA-MM-JJ) : ``existe``, ``pourcentage``,
        ``formule`` (« carriere_complete » jusqu'en octobre 2021,
        « differentielle » depuis), ``condition`` (« duree_requise » ou
        « taux_plein »), ``seuil_chef``, ``plafond_tous_regimes``,
        ``pmr_au_mois`` (le mois où la PMR de la formule se lit),
        ``majorations_de_duree``."""
        if self._fiche is None:
            return dict(SANS_COMPLEMENT_DIFFERENTIEL)
        version = versions.applicable(self._fiche, {"liquidation.date_effet": date_effet})
        return dict(SANS_COMPLEMENT_DIFFERENTIEL if version is None
                    else version["parametres"])

    def smic_net(self, annee: int) -> tuple[float, Fiabilite] | None:
        """Le SMIC net agricole horaire du 1er janvier de l'année ; ``None``
        avant la première ; au-delà de la dernière, celle-ci revalorisée sur
        le SMIC brut, estimée."""
        if not self._smic or annee < min(self._smic):
            return None
        if annee in self._smic:
            return self._smic[annee]
        derniere = max(self._smic)
        valeur, fiabilite = self._smic[derniere]
        return (valeur * self.macro.coefficient_smic(derniere, annee),
                min(fiabilite, Fiabilite.ESTIMEE))


def charger_ages(chemin: Path, colonne: str) -> SerieAnnuelle:
    """Charge une colonne d'âges du fichier législatif.

    Le fichier ne comporte pas de colonne ``fiabilite`` : les âges légaux sont
    des données de droit, lues dans les textes. On les qualifie donc de
    ``haute`` — « certifiée » reste réservé à ce qui a été recontrôlé
    automatiquement contre la source.

    Logé ici depuis ``moteur/age_reference.py`` (action 161, étape 3 de
    l'inventaire du retrait des règles) : la fabrique du paquet le lit, et
    l'âge de référence du moteur Python le reprend.
    """
    valeurs = {}
    with chemin.open(encoding="utf-8") as flux:
        lignes = (l for l in flux if not l.lstrip().startswith("#"))
        for ligne in csv.DictReader(lignes):
            annee = int(ligne["annee"])
            valeurs[annee] = _age_de_haute_fiabilite(annee, float(ligne[colonne]))
    return SerieAnnuelle(valeurs, f"{colonne}", interpolation="escalier")


def _age_de_haute_fiabilite(annee: int, valeur: float) -> ValeurAnnuelle:
    return ValeurAnnuelle(annee=annee, valeur=valeur, fiabilite=Fiabilite.HAUTE)
