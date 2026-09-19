"""Ce que la retraite a coûté : les dépenses réellement versées, depuis 1959.

Le reste du modèle calcule des DROITS — ce qu'une carrière ouvre. Ce module
porte la grandeur inverse et complémentaire : ce que la collectivité a
effectivement payé, année par année, système par système. Les deux ne se
déduisent pas l'une de l'autre, et c'est bien pourquoi il faut les deux.

La source est unique : les Comptes de la protection sociale de la DREES, risque
vieillesse-survie. C'est la seule série longue française de dépenses de retraite
publiée par son producteur, et le critère 1 du manifeste des sources — le
producteur prime sur le repreneur — la désigne sans hésitation.

Deux couvertures, et il faut les distinguer pour lire quoi que ce soit :

* le **total tous régimes** court de 1959 à 2024, sans trou ;
* la **ventilation par système** ne commence qu'en 1990, parce que la
  nomenclature d'avant ne se raccorde pas à celle d'après.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .chargement import Fiabilite, SerieAnnuelle, charger_serie_annuelle


#: Les deux catégories de la ventilation d'une masse de pensions, du vocabulaire
#: du COR comme de celui de la DREES : ce qu'un assuré s'est ouvert par sa
#: propre carrière, et ce qu'un conjoint survivant reçoit de celle d'un autre.
CATEGORIES_DROITS: tuple[str, ...] = ("direct", "derive")


@dataclass(frozen=True)
class Systeme:
    """Un système de retraite, au découpage des Comptes de la protection sociale.

    ``repartition`` dit si le système relève de la RÉPARTITION OBLIGATOIRE. Ce
    n'est pas une nuance : le risque vieillesse-survie porte aussi la
    capitalisation, l'aide sociale aux personnes âgées et le minimum vieillesse,
    et l'on ne compare pas des comptes notionnels à une allocation
    personnalisée d'autonomie.
    """

    code: str
    libelle: str
    glose: str
    repartition: bool


#: Les treize postes de la ventilation, dans l'ordre d'affichage : la
#: répartition obligatoire d'abord, par masse décroissante en 2024, puis ce qui
#: n'en relève pas. Les codes sont ceux qu'écrit ``scripts/verifier_donnees.py``
#: depuis les organismes de la DREES ; le test ``test_les_systemes_couvrent_la
#: _ventilation`` vérifie que les deux listes ne divergent pas.
SYSTEMES: tuple[Systeme, ...] = (
    Systeme(
        "regime_general", "Régime général (Cnav)",
        "Le socle des salariés du privé. Il absorbe depuis 2020 les artisans et "
        "les commerçants, dont le régime a été adossé à la Cnav : la marche de "
        "cette année-là est une réorganisation, pas une dépense nouvelle.",
        True,
    ),
    Systeme(
        "agirc_arrco", "Agirc-Arrco",
        "Les complémentaires des salariés du privé, deux caisses jusqu'en 2018 "
        "et une seule depuis. À elles seules, un quart de la dépense.",
        True,
    ),
    Systeme(
        "fonction_publique_etat", "Fonction publique d'État",
        "Les pensions civiles et militaires de l'État, versées par le compte "
        "d'affectation spéciale « Pensions ». La territoriale et l'hospitalière "
        "n'y sont pas : la DREES les range avec les régimes spéciaux.",
        True,
    ),
    Systeme(
        "regimes_speciaux", "Régimes spéciaux",
        "La CNRACL — fonction publique territoriale et hospitalière —, la SNCF, "
        "la RATP, les industries électriques et gazières et les autres, réunies "
        "par la comptabilité nationale sous un seul poste.",
        True,
    ),
    Systeme(
        "exploitants_agricoles", "Exploitants agricoles",
        "Le régime des chefs d'exploitation, dont la dépense recule en euros "
        "constants depuis trente ans : ses cotisants ont disparu avant ses "
        "pensionnés.",
        True,
    ),
    Systeme(
        "professions_liberales", "Professions libérales (CNAVPL)",
        "Base et complémentaires des sections professionnelles.",
        True,
    ),
    Systeme(
        "salaries_agricoles", "Salariés agricoles",
        "Le régime aligné de la MSA.",
        True,
    ),
    Systeme(
        "ircantec", "Ircantec",
        "La complémentaire des agents non titulaires de l'État et des "
        "collectivités.",
        True,
    ),
    Systeme(
        "non_salaries_autres", "Autres régimes de non-salariés",
        "Ce qui reste des régimes de non-salariés une fois les exploitants "
        "agricoles et les professions libérales mis à part — la part la plus "
        "réduite depuis l'adossement du RSI à la Cnav.",
        True,
    ),
    Systeme(
        "repartition_autres", "Autres régimes par répartition",
        "Fonds spéciaux, régimes résiduels, prestations vieillesse versées par "
        "les branches maladie et famille.",
        True,
    ),
    Systeme(
        "solidarite_etat", "Solidarité de l'État",
        "Minimum vieillesse et crédits d'impôt liés à l'âge. Non contributif : "
        "aucun compte notionnel ne le porterait, et c'est précisément ce que "
        "les scénarios notionnels retirent.",
        False,
    ),
    Systeme(
        "aide_sociale_locale", "Aide sociale des collectivités",
        "Allocation personnalisée d'autonomie, hébergement des personnes âgées "
        "dépendantes. De la dépendance plutôt que de la retraite, mais le risque vieillesse-survie les loge au même endroit.",
        False,
    ),
    Systeme(
        "supplementaire", "Retraite supplémentaire",
        "Capitalisation : RAFP, contrats collectifs d'assurance, de prévoyance "
        "et de mutuelle, régimes d'entreprise. Un capital est placé : c'est ce qui la sépare de tout le reste de ce tableau.",
        False,
    ),
)

CODES_SYSTEMES = tuple(systeme.code for systeme in SYSTEMES)


def _postes_non_contributifs(chemin) -> tuple[str, ...]:
    """Les postes présents dans le fichier, dans l'ordre alphabétique.

    Ils sont LUS et non écrits : ajouter un poste aux comptes récupérés doit
    suffire à le faire apparaître, sans qu'aucune liste du modèle ne le répète.
    """
    import csv

    with chemin.open(encoding="utf-8") as flux:
        lignes = (l for l in flux if not l.lstrip().startswith("#"))
        return tuple(sorted({ligne["poste"] for ligne in csv.DictReader(lignes)}))


class DepensesRetraite:
    """Les dépenses observées, avec leur ventilation et le PIB qui les rapporte."""

    def __init__(self, racine: Path) -> None:
        macro = racine / "reference" / "macro"
        self.total = charger_serie_annuelle(
            macro / "depenses_retraite.csv", "depenses_meur", nom="depenses_retraite"
        )
        self.pib = charger_serie_annuelle(
            macro / "pib_courant.csv", "pib_meur", nom="pib_courant"
        )
        # La réversion, lue et non modélisée : le modèle décrit une carrière,
        # pas un ménage. C'est la seule dépense non contributive dont le montant
        # vienne d'une publication plutôt que d'un calcul.
        self.droits_derives = charger_serie_annuelle(
            macro / "droits_derives.csv", "masse_meur", nom="droits_derives",
            filtre={"caisse": "tous_regimes"},
        )
        # Les prestations non contributives que les comptes isolent, poste par
        # poste, depuis 2020. Elles ne complètent pas le modèle : elles le
        # REMPLACENT là où elles existent, le producteur primant sur le calcul.
        self.prestations: dict[str, SerieAnnuelle] = {}
        chemin = macro / "prestations_non_contributives.csv"
        if chemin.exists():
            for poste in _postes_non_contributifs(chemin):
                self.prestations[poste] = charger_serie_annuelle(
                    chemin, "montant_meur", nom=f"prestation_{poste}",
                    filtre={"poste": poste},
                )
        self.systemes: dict[str, SerieAnnuelle] = {}
        for systeme in SYSTEMES:
            self.systemes[systeme.code] = charger_serie_annuelle(
                macro / "depenses_retraite_regimes.csv", "depenses_meur",
                nom=f"depenses_{systeme.code}", filtre={"regime": systeme.code},
            )
        self.part_derives = charger_serie_annuelle(
            macro / "part_droits_derives.csv", "part", nom="part_droits_derives"
        )
        self.pensions_droits: dict[str, SerieAnnuelle] = {
            categorie: charger_serie_annuelle(
                macro / "pensions_droits.csv", "montant_meur",
                nom=f"pensions_{categorie}", filtre={"categorie": categorie},
            )
            for categorie in CATEGORIES_DROITS
        }

    # -- bornes --------------------------------------------------------------

    @property
    def premiere_annee(self) -> int:
        return self.total.premiere_annee

    @property
    def derniere_annee(self) -> int:
        return self.total.derniere_annee

    @property
    def premiere_annee_ventilee(self) -> int:
        return max(serie.premiere_annee for serie in self.systemes.values())

    def annees(self) -> list[int]:
        return list(range(self.premiere_annee, self.derniere_annee + 1))

    def annees_ventilees(self) -> list[int]:
        return list(range(self.premiere_annee_ventilee, self.derniere_annee + 1))

    # -- lectures ------------------------------------------------------------

    def depense(self, annee: int) -> float:
        """Dépense totale du risque vieillesse-survie, en millions d'euros courants."""
        return self.total(annee)

    def depense_systeme(self, code: str, annee: int) -> float:
        return self.systemes[code](annee)

    def reversion(self, annee: int) -> float | None:
        """Masse des pensions de réversion de l'année, en millions d'euros courants.

        ``None`` hors de la fenêtre que la DREES publie : cette grandeur ne
        s'extrapole pas. Elle ne se calcule pas non plus — le modèle n'a ni
        conjoint, ni date de décès, ni ressources du survivant —, et c'est
        précisément pourquoi elle est lue.
        """
        if not (self.droits_derives.premiere_annee <= annee
                <= self.droits_derives.derniere_annee):
            return None
        return self.droits_derives(annee)

    def prestation(self, poste: str, annee: int) -> float | None:
        """Un poste non contributif des comptes, en millions d'euros courants.

        ``None`` hors de la fenêtre publiée. La DREES ne donne ce grain qu'à
        partir de 2020, quand le total du risque remonte à 1959 : cinq années ne
        font pas une tendance, elles font un ordre de grandeur.
        """
        serie = self.prestations.get(poste)
        if serie is None:
            return None
        if not serie.premiere_annee <= annee <= serie.derniere_annee:
            return None
        return serie(annee)

    def part_pib(self, annee: int) -> float:
        """Part de la dépense dans le produit intérieur brut de la même année."""
        return self.total(annee) / self.pib(annee)

    def part_droits_derives(self, annee: int) -> float:
        """Quelle fraction de la masse versée est une pension de RÉVERSION.

        Un huitième en 2010, un dixième en 2024, un dix-huitième en 2070 : la
        réversion recule dans la projection du COR, parce que les carrières des
        femmes se rapprochent de celles des hommes et qu'une pension
        différentielle s'éteint à mesure que la pension propre du survivant
        monte.

        Elle sert à une chose, et ``cout.py`` la dit : le rapport de masses par
        lequel un scénario notionnel fait réagir la dépense est celui des
        droits DIRECTS des cas types. Sans cette part, il s'appliquait aussi à
        la réversion, que le modèle ne calcule pas — un scénario la réduisait
        donc dans la même proportion que les pensions propres, sans que rien ne
        l'ait décidé.
        """
        return self.part_derives(annee)

    def pensions_droit(self, categorie: str, annee: int) -> float:
        """Pensions de droit direct ou de droit dérivé, en millions d'euros.

        La ventilation de la DREES, 2020-2024. Courte par construction, elle ne
        fait pas série : elle CONTRÔLE ``part_droits_derives``, qui vient du COR
        et couvre 2010-2070. Sur les cinq années communes, les deux parts
        s'écartent de six centièmes de point au plus.
        """
        return self.pensions_droits[categorie](annee)

    def repartition(self, annee: int) -> float:
        """Ce que coûte la seule répartition obligatoire, ventilation à l'appui.

        Le total publié est plus large : il porte aussi la capitalisation,
        l'aide sociale aux personnes âgées et le minimum vieillesse. Cette
        somme les retranche — et n'est donc disponible que sur les années
        ventilées.
        """
        return sum(
            self.systemes[systeme.code](annee)
            for systeme in SYSTEMES if systeme.repartition
        )

    def fiabilite(self, annee: int) -> Fiabilite:
        return min(self.total.fiabilite(annee), self.pib.fiabilite(annee))
