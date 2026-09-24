"""La pension d'aujourd'hui : ce que devient une pension une fois liquidée.

Le modèle calcule une pension AU JOUR DE LA LIQUIDATION. Pour qui part demain,
c'est la question. Pour qui est parti il y a quinze ans, non : il ne touche pas
sa première pension, il touche ce qu'elle est devenue, date d'effet après date
d'effet. Le simulateur affichait pourtant la première, ramenée en euros
d'aujourd'hui par l'indice des prix — ce qui revenait à supposer qu'elle avait
suivi les prix. Elle ne les a pas suivis. Le régime général a gelé ses pensions
en 2014, les a revalorisées de 0,3 % en 2019, de 0,3 à 1 % en 2020 selon le
montant de la retraite ; l'Agirc-Arrco a laissé son point sans revalorisation
plusieurs années de suite. Ce que le retraité lit sur son relevé bancaire est
donc moins que sa première pension ramenée en euros d'aujourd'hui, et le cas
type de ``tests/test_revalorisation.py`` en refait le compte à la main.

CE MODULE DIT CE QUE LA PENSION EST DEVENUE, régime par régime, dans les textes
qui l'ont revalorisée.

* **Les régimes en points** servent leurs points à la valeur de service de
  l'année : la pension d'aujourd'hui est la pension du départ multipliée par
  le rapport des deux valeurs du point, lues dans ``valeurs_point.csv`` et le
  long des fusions (Agirc et Arrco dans l'Agirc-Arrco). C'est exact par
  construction. Au-delà de la dernière valeur publiée, la règle générale prend
  le relais, et la fiabilité le dit.
* **Le régime général et les régimes alignés** suivent l'article L. 161-23-1 du
  code de la sécurité sociale : les coefficients sont ceux que la Cnav publie
  depuis 1949 (``revalorisation_pensions.csv``), y compris les cinq tranches de
  2020, choisies sur le montant total brut mensuel des retraites de décembre
  2019. Une revalorisation au 1er janvier de l'année du départ n'est pas
  appliquée : les salaires portés au compte l'ont déjà reçue.
* **Les pensions civiles et militaires** suivaient le traitement des actifs —
  la péréquation — jusqu'au 31 décembre 2003, puis un décret par an jusqu'en
  2008, puis l'article L. 161-23-1 (``revalorisation_pensions_fonction_publique.csv``).
  La péréquation est suivie par le point d'indice, sans les tableaux
  d'assimilation qui relevaient les pensions d'un grade réformé.
* **Les régimes spéciaux** suivent le taux des fonctionnaires depuis le
  1er janvier 2009 (décrets n° 2008-47, 2008-48, 2008-69 et suivants). Avant,
  leurs pensions suivaient les salaires de leurs actifs, qu'aucune série ne
  donne : la règle générale en tient lieu, et la fiabilité tombe à ``estimee``.

Pour la fonction publique et les régimes spéciaux, une revalorisation qui
tombe le jour même du départ S'APPLIQUE : leurs textes visent les pensions
« dont la date d'effet est au plus tard » ce jour-là, parce que leur pension se
calcule sur un traitement que personne n'a revalorisé.

LES CINQ SYSTÈMES NOTIONNELS ne sont pas le droit : leur pension servie suit la
règle que le modèle leur prête déjà, celle de la page Coût
(:class:`RevalorisationServie`, déplacée ici pour que le simulateur s'en serve
sans importer la page). Le scénario 6 y ajoute la garantie vieillesse
d'aujourd'hui, qui s'ouvre à 65 ans et regarde la pension d'aujourd'hui.

Tout ce que ce module rend est en euros COURANTS de l'année courante — ceux
du relevé bancaire. Le passage aux euros constants d'une autre année reste
l'affaire de l'appelant.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .config import RevalorisationStock, SituationFoyer
from .donnees.chargement import Fiabilite


# -- ce que le droit a servi depuis la liquidation ---------------------------

#: La péréquation des pensions civiles et militaires cesse à cette date : la
#: rédaction de 2003 de l'article L. 16 leur donne une revalorisation par décret.
FIN_PEREQUATION = date(2004, 1, 1)

#: À compter de cette date, les pensions civiles et militaires suivent l'article
#: L. 161-23-1 (loi n° 2008-1330, art. 79, en vigueur le 19 décembre 2008 ; la
#: première revalorisation qui en relève est celle du 1er avril 2009), et les
#: régimes spéciaux le taux des fonctionnaires (décrets de 2008).
DEBUT_REGLE_GENERALE_PUBLIC = date(2009, 1, 1)

#: Le dernier point d'indice que la péréquation a servi : celui du
#: 1er décembre 2002, resté en vigueur jusqu'au 31 décembre 2003.
DERNIERE_ANNEE_PEREQUATION = 2003

#: Le mois dont le montant total choisit la tranche de 2020 : « le mois
#: précédent celui auquel intervient la revalorisation » (loi n° 2019-1446,
#: art. 81).
MOIS_DES_TRANCHES = date(2019, 12, 31)

#: L'âge de l'ASPA et de la garantie vieillesse — celui de
#: :attr:`MinimumVieillesse.AGE_OUVERTURE`, recopié pour que ce module n'importe
#: pas le scénario 1, qui l'importe.
MINIMUM_VIEILLESSE_AGE = 65

#: Les règles, telles que la page les nomme et que la sortie JSON les écrit.
REGLE_POINT = "point"
REGLE_GENERALE = "regime_general"
REGLE_FONCTION_PUBLIQUE = "fonction_publique"
REGLE_REGIME_SPECIAL = "regime_special"
REGLE_PAR_DEFAUT = "par_defaut"

#: Les régimes que l'article L. 16 du code des pensions civiles et militaires
#: revalorise, directement ou par renvoi : l'État, la CNRACL (décret
#: n° 2003-1306, art. 19) et les ouvriers de l'État (décret n° 2004-1056,
#: art. 15) — les décrets de 2004 à 2007 les nomment tous trois.
REGIMES_FONCTION_PUBLIQUE = frozenset({
    "fonction_publique_etat", "pensions_civiles_1853", "cnracl", "fspoeie",
})

#: Les régimes dont le texte dit qu'ils suivent l'article L. 161-23-1 : le
#: régime général et ceux qui lui sont alignés, les deux régimes agricoles
#: (L. 161-23-1 les nomme depuis 2026, L. 732-24 et L. 742-3 du code rural
#: avant), les régimes de base des indépendants, que la circulaire de la Cnav
#: revalorise elle-même, et Mayotte, qu'elle nomme aussi.
REGIMES_REGLE_GENERALE = frozenset({
    "regime_general", "avts", "assurances_sociales", "msa_salaries",
    "msa_non_salaries", "rsi", "cancava", "organic", "cssm_mayotte",
})


@dataclass(frozen=True)
class Revalorisation:
    """Une date d'effet de revalorisation, et son coefficient."""

    date_effet: date
    coefficient: float
    #: Les tranches de 2020 : bornes du montant total brut MENSUEL des
    #: retraites du mois précédent, la basse exclue, la haute incluse. ``None``
    #: pour toutes les autres lignes.
    superieur_a: float | None
    au_plus: float | None
    reference: str
    fiabilite: Fiabilite

    @property
    def par_tranche(self) -> bool:
        return self.superieur_a is not None or self.au_plus is not None

    def couvre(self, mensuel: float) -> bool:
        """La tranche s'applique-t-elle à ce montant total mensuel ?"""
        return ((self.superieur_a is None or mensuel > self.superieur_a)
                and (self.au_plus is None or mensuel <= self.au_plus))


def _reel_ou_rien(texte: str | None) -> float | None:
    return float(texte) if texte else None


def _charger(chemin: Path) -> tuple[Revalorisation, ...]:
    """Les lignes d'un fichier de revalorisations, de la plus ancienne à la plus récente."""
    if not chemin.exists():
        return ()
    with chemin.open(encoding="utf-8") as flux:
        lignes = [l for l in flux if not l.lstrip().startswith("#")]
    revalorisations = [
        Revalorisation(
            date_effet=date.fromisoformat(ligne["date_effet"]),
            coefficient=float(ligne["coefficient"]),
            superieur_a=_reel_ou_rien(ligne.get("mensuel_superieur_a")),
            au_plus=_reel_ou_rien(ligne.get("mensuel_au_plus")),
            reference=ligne["reference"],
            fiabilite=Fiabilite.depuis_texte(ligne["fiabilite"]),
        )
        for ligne in csv.DictReader(lignes)
    ]
    return tuple(sorted(revalorisations,
                        key=lambda r: (r.date_effet, r.superieur_a or 0.0)))


def produit(revalorisations) -> tuple[float, Fiabilite]:
    """Le coefficient cumulé d'une suite de revalorisations, et sa fiabilité."""
    coefficient = 1.0
    fiabilite = Fiabilite.CERTIFIEE
    for revalorisation in revalorisations:
        coefficient *= revalorisation.coefficient
        fiabilite = min(fiabilite, revalorisation.fiabilite)
    return coefficient, fiabilite


class RevalorisationsPensions:
    """Les coefficients qui ont revalorisé les pensions servies, date par date.

    Deux fichiers : celui de l'article L. 161-23-1, que la Cnav publie depuis
    1949, et celui des pensions civiles et militaires de 2004 à 2008, quand
    elles avaient leurs propres décrets.
    """

    def __init__(self, racine: Path) -> None:
        dossier = racine / "reference" / "legislation"
        self.generales = _charger(dossier / "revalorisation_pensions.csv")
        self.fonction_publique = _charger(
            dossier / "revalorisation_pensions_fonction_publique.csv")

    @staticmethod
    def retenues(lignes, depuis: date, jusqu_a: date, inclure_depuis: bool,
                 mensuel_2019: float | None) -> list[Revalorisation]:
        """Celles qu'a reçues une pension prenant effet à ``depuis``, jusqu'à
        ``jusqu_a`` inclus.

        ``inclure_depuis`` dit si une revalorisation tombant le jour même du
        départ s'applique — oui dans la fonction publique et les régimes
        spéciaux, non au régime général, dont les salaires portés au compte
        l'ont déjà reçue. Une tranche de 2020 n'est retenue que si le montant
        mensuel de décembre 2019 y tombe : c'est à l'appelant de le donner, et
        ne pas le faire quand la fenêtre couvre 2020 est une erreur.
        """
        choisies = []
        for ligne in lignes:
            effet = ligne.date_effet
            if effet > jusqu_a or effet < depuis or (effet == depuis and not inclure_depuis):
                continue
            if ligne.par_tranche:
                if mensuel_2019 is None:
                    raise ValueError(
                        f"la revalorisation du {effet} dépend du montant total "
                        "de la retraite du mois précédent, qui n'a pas été donné"
                    )
                if not ligne.couvre(mensuel_2019):
                    continue
            choisies.append(ligne)
        return choisies

    def generale(self, depuis: date, jusqu_a: date, inclure_depuis: bool,
                 mensuel_2019: float | None) -> tuple[float, Fiabilite]:
        """Le coefficient de l'article L. 161-23-1 entre deux dates."""
        return produit(self.retenues(self.generales, depuis, jusqu_a,
                                     inclure_depuis, mensuel_2019))


def coefficient_traitement_differe(revalorisations: RevalorisationsPensions,
                                   ratio_point_indice, perception: int,
                                   radiation: date, paiement: date) -> float | None:
    """Ce qui porte le dernier traitement d'une pension DIFFÉRÉE jusqu'à sa
    mise en paiement, ou ``None`` si la série du point ne couvre pas l'année.

    Le fonctionnaire radié des cadres avant de pouvoir liquider touche sa
    pension des années plus tard, calculée sur le traitement qu'il détenait en
    partant. Ce traitement ne reste pas figé, et ne suit pas davantage le
    point d'indice des actifs : « Le traitement ou la solde mentionnés à
    l'article L. 15 sont revalorisés pendant la période comprise entre la
    radiation des cadres et la mise en paiement de la pension, conformément
    aux dispositions de l'article L. 16 » (L. 25 du code des pensions, depuis
    le 1er janvier 2004). La même phrase est à l'article 26 du décret
    n° 2003-1306 pour la CNRACL et à l'article 22 du décret n° 2004-1056 pour
    les ouvriers de l'État. Ce sont donc les revalorisations des PENSIONS
    civiles — la péréquation, qui suivait le point, jusqu'en 2003, les décrets
    de 2004 à 2008, l'article L. 161-23-1 ensuite —, depuis le traitement de
    l'année ``perception`` porté au point jusqu'à la radiation.

    Les bornes sont celles de la CNRACL : une revalorisation tombant le jour
    de la radiation n'est pas due — la pension d'un agent radié le 1er janvier
    ne l'est pas davantage —, celle du jour de la mise en paiement l'est :
    « si la pension est due à compter de la date de revalorisation, le
    traitement servant au calcul de la pension bénéficie de la revalorisation
    des pensions ».

    En 2020, le coefficient de l'article L. 161-25, 1 % : la dérogation de
    0,3 % de l'article 81 de la loi n° 2019-1446 ne vise que « les montants
    des prestations et pensions servies », et un traitement qui attend sa
    pension n'en est pas une — la Cnav a revalorisé de même, cette année-là,
    les salaires portés au compte.
    """
    fin_point = (radiation.year if radiation >= FIN_PEREQUATION
                 else min(paiement.year, DERNIERE_ANNEE_PEREQUATION))
    point = ratio_point_indice(perception, fin_point)
    if point is None:
        return None
    decrets, _ = produit(RevalorisationsPensions.retenues(
        revalorisations.fonction_publique, max(radiation, FIN_PEREQUATION),
        min(paiement, DEBUT_REGLE_GENERALE_PUBLIC), radiation < FIN_PEREQUATION, None))
    generale, _ = revalorisations.generale(
        max(radiation, DEBUT_REGLE_GENERALE_PUBLIC), paiement,
        radiation < DEBUT_REGLE_GENERALE_PUBLIC, 0.0)
    return point * decrets * generale


@dataclass(frozen=True)
class RegimeServi:
    """La pension d'un régime, de la liquidation à aujourd'hui."""

    regime: str
    #: Montant annuel brut à la liquidation, en euros de l'année de
    #: liquidation : celui que le scénario 1 calcule.
    au_depart: float
    #: Le coefficient NOMINAL qui le mène à aujourd'hui.
    coefficient: float
    #: La règle suivie — voir les constantes ``REGLE_*``.
    regle: str
    fiabilite: Fiabilite
    #: Régime provisionné (RAFP) : servi à part, hors des totaux de la
    #: répartition, comme à la liquidation.
    hors_repartition: bool = False

    @property
    def aujourd_hui(self) -> float:
        return self.au_depart * self.coefficient


@dataclass(frozen=True)
class ActuelAujourdhui:
    """Le système 1 aujourd'hui : ce que le droit sert, régime par régime."""

    #: L'année courante, dont les euros sont ceux de tous les montants rendus.
    annee: int
    regimes: tuple[RegimeServi, ...]
    #: La majoration pour enfants, à la liquidation. Elle suit les régimes
    #: qui la portent, chaque part au coefficient du sien : c'est le
    #: coefficient qu'on lit ici, pondéré par les parts.
    majoration_enfants: float
    coefficient_majoration: float
    #: L'ASPA à la liquidation, puis celle d'aujourd'hui : un montant
    #: différentiel, recalculé sur le barème de l'année et sur les pensions
    #: d'aujourd'hui, et ouvert à 65 ans même si le départ a eu lieu avant.
    minimum_vieillesse_au_depart: float
    minimum_vieillesse: float
    #: Le montant total brut mensuel de décembre 2019 qui a choisi la tranche
    #: de 2020, ou ``None`` quand la pension n'a pas traversé cette date. Nul
    #: pour une pension prise en janvier 2020, qui n'était pas encore servie.
    mensuel_decembre_2019: float | None
    fiabilite: Fiabilite

    @property
    def pension_annuelle(self) -> float:
        """La répartition, comme :attr:`ResultatActuel.pension_annuelle`."""
        return (sum(r.aujourd_hui for r in self.regimes if not r.hors_repartition)
                + self.majoration_enfants * self.coefficient_majoration
                + self.minimum_vieillesse)

    @property
    def pension_hors_repartition(self) -> float:
        return sum(r.aujourd_hui for r in self.regimes if r.hors_repartition)


@dataclass(frozen=True)
class PensionAujourdhui:
    """Ce qu'un retraité touche aujourd'hui, dans chacun des six systèmes.

    En euros COURANTS de :attr:`annee` — ceux du relevé bancaire.
    """

    annee: int
    actuel: ActuelAujourdhui
    #: La pension annuelle d'aujourd'hui des cinq scénarios notionnels, au sens
    #: de ``pension_annuelle`` : la répartition, garantie vieillesse comprise
    #: pour le 6, rente capitalisée à part.
    notionnels: dict[str, float]
    #: Ce que la règle d'indexation a fait de la pension depuis le départ, en
    #: termes RÉELS, scénario par scénario : un coefficient au-dessus de un
    #: veut dire que la pension a battu les prix.
    coefficients_notionnels: dict[str, float]
    #: Scénario 6 : la garantie d'aujourd'hui, et la rente du pilier capitalisé
    #: — qui garde son pouvoir d'achat —, dont sa part volontaire.
    garantie_vieillesse: float
    rente_capitalisee: float
    rente_capitalisee_volontaire: float
    #: Les deux termes de la garantie d'aujourd'hui : le plancher de l'année,
    #: et ce qu'il regarde — la pension obligatoire, répartition et rente
    #: capitalisée. ``garantie_ouverte`` dit si les 65 ans sont atteints.
    garantie_ouverte: bool = False
    plancher_garantie: float = 0.0
    ressources_garantie: float = 0.0

    def pension(self, scenario: str) -> float:
        """La pension annuelle d'aujourd'hui d'un des six scénarios."""
        if scenario == "actuel":
            return self.actuel.pension_annuelle
        return self.notionnels[scenario]

    def pension_totale(self, scenario: str) -> float:
        """Répartition et capitalisation réunies — seul le 6 a la seconde."""
        if scenario == "notionnel_liberal":
            return self.notionnels[scenario] + self.rente_capitalisee
        return self.pension(scenario)


def _derniere_valeur_publiee(actuel, code: str) -> int | None:
    """Dernière année dont la valeur de service est publiée, au bout de la
    chaîne des fusions que :meth:`ScenarioActuel.valeur_du_point` remonte."""
    courant = code
    for _ in range(len(actuel.catalogue) + 1):  # garde-fou : jamais de boucle
        derniere = actuel.valeurs_point.derniere_annee_servie(courant)
        if derniere is None:
            return None
        successeur = (actuel.catalogue[courant].integre_dans
                      if courant in actuel.catalogue else None)
        reprise = (actuel.conversions_points.fusion(courant, successeur)
                   if successeur else None)
        if reprise is None:
            return derniere
        courant = successeur
    return None  # pragma: no cover - chaîne de successions cyclique


def _derniere_annee(regime) -> int:
    annees = [p.fin if p.fin is not None else 9999 for p in regime.periodes]
    return min(max(annees), 2100) if annees else 2100


class PensionServie:
    """La règle de chaque régime, appliquée d'une date à une autre."""

    def __init__(self, simulateur) -> None:
        self.actuel = simulateur.scenario_actuel
        self.catalogue = simulateur.catalogue
        self.revalorisations = simulateur.revalorisations

    def coefficient(self, pension, annee_liquidation: int, depart: date,
                    jusqu_a: date, mensuel_2019: float | None
                    ) -> tuple[float, str, Fiabilite]:
        """Coefficient nominal d'une pension de régime, de ``depart`` à ``jusqu_a``."""
        code = pension.regime
        regime = self.catalogue[code]
        debut_annee = date(annee_liquidation, 1, 1)
        if pension.type_calcul in ("points", "mixte"):
            periode = regime.periode(min(annee_liquidation, _derniere_annee(regime)))
            bareme = (periode.points_de if periode is not None else None) or code
            au_depart = self.actuel.valeur_du_point(bareme, annee_liquidation)
            publiee = _derniere_valeur_publiee(self.actuel, bareme)
            if au_depart is not None and au_depart[0] > 0 and publiee is not None:
                # Au-delà de la dernière valeur publiée, la règle générale
                # prend le relais : c'est celle du régime de base des
                # libéraux, dont la série s'arrête en 2025.
                ancre = min(jusqu_a.year, publiee)
                a_l_ancre = self.actuel.valeur_du_point(bareme, ancre)
                # Un CHANGEMENT D'ÉCHELLE survenu depuis le départ convertit
                # les points déjà servis : l'Arrco de 1999 a fait de chaque
                # point de l'ancienne unité 0,387464 point de la nouvelle.
                # Lire la valeur de 2026 sans lui servait à un retraité de 1990
                # 2,6 fois sa pension.
                echelle, fiabilite_echelle = self.actuel.conversions_points.echelle(
                    bareme, annee_liquidation, ancre)
                suite, fiabilite_suite = self.revalorisations.generale(
                    date(ancre, 12, 31), jusqu_a, False, mensuel_2019)
                fiabilite = min(au_depart[1], a_l_ancre[1], fiabilite_echelle)
                if ancre < jusqu_a.year:
                    fiabilite = min(fiabilite, fiabilite_suite, Fiabilite.MOYENNE)
                return (echelle * a_l_ancre[0] / au_depart[0] * suite, REGLE_POINT,
                        fiabilite)
            # Sans valeur de service publiée, un régime en points suit la règle
            # de son régime — la valeur écrite dans la fiche est revalorisée
            # « comme la loi le prescrit (L. 161-23-1) ».
        if code in REGIMES_FONCTION_PUBLIQUE:
            return self._fonction_publique(annee_liquidation, depart, jusqu_a,
                                           mensuel_2019)
        if regime.famille == "special":
            coefficient, fiabilite = self.revalorisations.generale(
                depart, jusqu_a, True, mensuel_2019)
            if depart < DEBUT_REGLE_GENERALE_PUBLIC:
                fiabilite = Fiabilite.ESTIMEE
            return coefficient, REGLE_REGIME_SPECIAL, fiabilite
        coefficient, fiabilite = self.revalorisations.generale(
            debut_annee, jusqu_a, False, mensuel_2019)
        if code in REGIMES_REGLE_GENERALE:
            return coefficient, REGLE_GENERALE, fiabilite
        return coefficient, REGLE_PAR_DEFAUT, min(fiabilite, Fiabilite.MOYENNE)

    def _fonction_publique(self, annee_liquidation: int, depart: date,
                           jusqu_a: date, mensuel_2019: float | None
                           ) -> tuple[float, str, Fiabilite]:
        """Péréquation, décrets, puis article L. 161-23-1 — dans cet ordre."""
        coefficient = 1.0
        fiabilite = Fiabilite.CERTIFIEE
        if depart < FIN_PEREQUATION:
            fin = min(jusqu_a.year, DERNIERE_ANNEE_PEREQUATION)
            ratio = self.actuel.minimum_garanti.ratio_point_indice(
                annee_liquidation, fin)
            if ratio is not None:
                coefficient *= ratio
            # Les tableaux d'assimilation ne sont pas suivis : le point
            # d'indice dit le traitement d'un indice, pas celui d'un grade.
            fiabilite = Fiabilite.MOYENNE
        decrets, fiabilite_decrets = produit(self.revalorisations.retenues(
            self.revalorisations.fonction_publique, max(depart, FIN_PEREQUATION),
            min(jusqu_a, DEBUT_REGLE_GENERALE_PUBLIC), True, None))
        generale, fiabilite_generale = self.revalorisations.generale(
            max(depart, DEBUT_REGLE_GENERALE_PUBLIC), jusqu_a, True, mensuel_2019)
        return (coefficient * decrets * generale, REGLE_FONCTION_PUBLIQUE,
                min(fiabilite, fiabilite_decrets, fiabilite_generale))


def actuel_aujourd_hui(simulateur, carriere, resultat,
                       annee: int | None = None) -> ActuelAujourdhui:
    """Le système 1 servi en ``annee`` — l'année courante par défaut.

    ``resultat`` est le scénario 1 de ``carriere`` à la liquidation. Rien n'est
    recalculé de la carrière : seuls les montants de chaque régime sont
    revalorisés, selon la règle de leur texte.
    """
    parametres = simulateur.parametres
    annee = parametres.annee_courante if annee is None else annee
    servie = PensionServie(simulateur)
    liquidation = carriere.annee_liquidation
    depart = date(liquidation, carriere.date_liquidation.mois, 1)
    fin = date(annee, 12, 31)
    isoler = parametres.isoler_capitalisation
    pensions = list(resultat.pensions_par_regime)
    majoration = sum(a.montant for a in resultat.avantages_appliques
                     if a.code == "majoration_enfants")
    aspa_au_depart = sum(a.montant for a in resultat.avantages_appliques
                         if a.code == "minimum_vieillesse")

    #: La part de chaque régime dans la majoration pour enfants, plafond
    #: compris (``AvantageApplique.par_regime``).
    parts_majoration = [part for a in resultat.avantages_appliques
                        if a.code == "majoration_enfants" for part in a.par_regime]

    def coefficient_moyen(coefficients: list[float]) -> float:
        repartition = [(p.montant, c) for p, c in zip(pensions, coefficients)
                       if not (isoler and simulateur.catalogue[p.regime].hors_repartition)]
        masse = sum(montant for montant, _ in repartition)
        if masse <= 0:
            return 1.0
        return sum(montant * c for montant, c in repartition) / masse

    def coefficient_de_la_majoration(coefficients: list[float]) -> float:
        """Chaque part suit le régime qui la porte : la base ses coefficients,
        la complémentaire la valeur de son point — comme son plafond, que le
        scénario 1 revalorise ainsi. Sans parts, la moyenne des régimes."""
        masse = sum(part for _, part in parts_majoration)
        if masse <= 0:
            return coefficient_moyen(coefficients)
        par_regime = {p.regime: c for p, c in zip(pensions, coefficients)}
        return sum(part * par_regime.get(code, 1.0)
                   for code, part in parts_majoration) / masse

    # LA TRANCHE DE 2020 se choisit sur le montant total de décembre 2019 :
    # toutes les retraites, de base, complémentaires et additionnelles,
    # majorations comprises. Il faut donc d'abord mener chaque pension
    # jusque-là — ce qui ne demande aucune tranche, puisque 2020 n'y est pas.
    # Une pension qui prend effet en janvier 2020 n'était pas servie en
    # décembre : l'article 81 regarde le montant « reçu […] le mois précédent
    # celui auquel intervient la revalorisation », et il était nul.
    mensuel_2019 = None
    if depart <= date(2020, 1, 1) <= fin:
        jusqu_2019 = [
            servie.coefficient(p, liquidation, depart, MOIS_DES_TRANCHES, None)[0]
            if depart <= MOIS_DES_TRANCHES else 0.0
            for p in pensions
        ]
        mensuel_2019 = (
            sum(p.montant * c for p, c in zip(pensions, jusqu_2019))
            + majoration * coefficient_de_la_majoration(jusqu_2019)
        ) / 12.0

    regimes = []
    coefficients = []
    fiabilite = Fiabilite.CERTIFIEE
    for pension in pensions:
        coefficient, regle, fiabilite_regime = servie.coefficient(
            pension, liquidation, depart, fin, mensuel_2019)
        coefficients.append(coefficient)
        fiabilite = min(fiabilite, fiabilite_regime)
        regimes.append(RegimeServi(
            regime=pension.regime,
            au_depart=pension.montant,
            coefficient=coefficient,
            regle=regle,
            fiabilite=fiabilite_regime,
            hors_repartition=isoler and simulateur.catalogue[pension.regime].hors_repartition,
        ))
    coefficient_majoration = coefficient_de_la_majoration(coefficients)

    # L'ASPA D'AUJOURD'HUI, comme à la liquidation : différentielle, sur
    # TOUTES les pensions — le RAFP compris —, et à 65 ans révolus dans
    # l'année. Qui est parti à 62 ans l'a peut-être gagnée depuis.
    aspa = 0.0
    if (parametres.minimum_vieillesse_dans_le_scenario_actuel
            and annee >= carriere.annee_naissance + MINIMUM_VIEILLESSE_AGE):
        bareme = simulateur.scenario_actuel.minimum_vieillesse.plafond(annee)
        if bareme is not None:
            ressources = (sum(r.aujourd_hui for r in regimes)
                          + majoration * coefficient_majoration)
            aspa = max(0.0, bareme[0] - ressources)
            if aspa > 0:
                fiabilite = min(fiabilite, bareme[1])

    return ActuelAujourdhui(
        annee=annee,
        regimes=tuple(regimes),
        majoration_enfants=majoration,
        coefficient_majoration=coefficient_majoration,
        minimum_vieillesse_au_depart=aspa_au_depart,
        minimum_vieillesse=aspa,
        mensuel_decembre_2019=mensuel_2019,
        fiabilite=fiabilite,
    )


def pension_aujourd_hui(simulateur, comparaison) -> PensionAujourdhui:
    """Les six systèmes servis l'année courante, pour qui a déjà liquidé.

    Le système 1 suit le droit (:func:`actuel_aujourd_hui`). Les deux
    systèmes prospectifs, pour qui a liquidé avant la bascule, SONT le système
    1 jusqu'à elle : même pension, mêmes revalorisations, puis la règle du
    stock que ``revalorisation_stock`` choisit. Les trois rétroactifs suivent
    la règle du compte jusqu'à la bascule, puis celle du stock — la même
    convention que la page Coût.
    """
    parametres = simulateur.parametres
    carriere = comparaison.carriere
    annee = parametres.annee_courante
    liquidation = carriere.annee_liquidation
    bascule = parametres.annee_bascule
    macro = simulateur.macro
    revalorisation = simulateur.revalorisation_servie
    vers_aujourd_hui = macro.coefficient_prix(liquidation, annee)

    actuel = actuel_aujourd_hui(simulateur, carriere, comparaison.actuel, annee)
    coefficient_actuel = (actuel.pension_annuelle / comparaison.actuel.pension_annuelle
                          if comparaison.actuel.pension_annuelle > 0 else 1.0)

    notionnels: dict[str, float] = {}
    coefficients: dict[str, float] = {}
    for cle in ("notionnel_retroactif", "notionnel_prospectif",
                "notionnel_retroactif_employeur", "notionnel_prospectif_employeur"):
        pension = getattr(comparaison, cle).pension_annuelle
        prospectif = cle.startswith("notionnel_prospectif")
        if prospectif and liquidation <= bascule:
            # Déjà liquidé à la bascule : la pension est celle du système 1,
            # et elle a reçu ce que le droit lui a donné jusqu'à la bascule.
            if annee <= bascule:
                notionnels[cle] = actuel.pension_annuelle
                coefficients[cle] = coefficient_actuel / vers_aujourd_hui
                continue
            jusqu_bascule = actuel_aujourd_hui(
                simulateur, carriere, comparaison.actuel, bascule).pension_annuelle
            reel = (revalorisation.coefficient(bascule, annee)
                    if parametres.revalorisation_stock is RevalorisationStock.REINDEXE
                    else 1.0)
            notionnels[cle] = (jusqu_bascule * macro.coefficient_prix(bascule, annee)
                               * reel)
            coefficients[cle] = (notionnels[cle] / pension / vers_aujourd_hui
                                 if pension > 0 else 1.0)
            continue
        reel = revalorisation.coefficient_stock(liquidation, annee, prospectif)
        notionnels[cle] = pension * vers_aujourd_hui * reel
        coefficients[cle] = reel

    # LE SYSTÈME 6 : le compte suit sa règle comme le 4, puis la garantie se
    # calcule AUJOURD'HUI — sur le plancher de l'année et la pension d'aujourd'hui
    # — et non l'année des 65 ans, qui peut être loin derrière.
    liberal = comparaison.notionnel_liberal
    garantie = liberal.garantie_vieillesse
    contributive = (garantie.pension_contributive if garantie is not None
                    else liberal.pension_annuelle)
    reel = revalorisation.coefficient_stock(liquidation, annee, False)
    contributive_aujourd_hui = contributive * vers_aujourd_hui * reel
    # La rente du pilier est NOMINALE et constante : elle vaut aujourd'hui,
    # en euros d'aujourd'hui, exactement ce qu'elle valait à la liquidation.
    # La porter sur les prix, comme ce calcul le faisait jusqu'au 23 septembre
    # 2026, lui donnait une indexation que le contrat ne prévoit pas.
    rente = liberal.rente_capitalisation_obligatoire
    volontaire = liberal.rente_capitalisation_volontaire
    plancher = parametres.garantie_vieillesse_mensuelle
    if parametres.situation_foyer is SituationFoyer.SEUL:
        plancher += parametres.allocation_isolement_mensuelle
    plancher *= 12.0 * macro.coefficient_prix(
        parametres.annee_euros_garantie_vieillesse, annee)
    ouverte = annee >= carriere.annee_naissance + MINIMUM_VIEILLESSE_AGE
    complement = (max(0.0, plancher - contributive_aujourd_hui - rente)
                  if ouverte else 0.0)
    notionnels["notionnel_liberal"] = contributive_aujourd_hui + complement
    coefficients["notionnel_liberal"] = reel

    return PensionAujourdhui(
        annee=annee,
        actuel=actuel,
        notionnels=notionnels,
        coefficients_notionnels=coefficients,
        garantie_vieillesse=complement,
        rente_capitalisee=rente,
        rente_capitalisee_volontaire=volontaire,
        garantie_ouverte=ouverte,
        plancher_garantie=plancher,
        ressources_garantie=contributive_aujourd_hui + rente,
    )


# -- la règle des systèmes notionnels -----------------------------------------


class RevalorisationServie:
    """Ce que devient une pension DÉJÀ LIQUIDÉE, année après année.

    UN SYSTÈME NOTIONNEL A DEUX RÈGLES D'INDEXATION, ET NON UNE. La première
    fait grossir le compte pendant la carrière ; la seconde revalorise la
    pension une fois qu'elle est servie. Les pays qui ont fait ce système les
    règlent séparément : la Suède revalorise le compte sur l'indice des
    salaires et la pension liquidée sur ce même indice diminué de 1,6 point ;
    l'Italie revalorise le compte sur le PIB et la pension liquidée sur les
    prix.

    Le dépôt n'en portait qu'une. Les masses de la page « Coût » figeaient la
    pension en euros constants pour toute la retraite, ce qui est une
    indexation sur les PRIX qui ne disait pas son nom — correcte pour le
    scénario 1, où c'est la loi, fausse pour les cinq autres. Car la seconde
    règle est déjà écrite ailleurs dans le modèle, et depuis toujours : le
    diviseur de conversion vaut l'espérance de vie résiduelle parce que
    ``taux_anticipe_conversion`` est nul, et il ne la vaut QUE si la rente est
    ensuite revalorisée au taux auquel le compte l'a été. Le modèle promettait
    donc une rente indexée sur la masse salariale et en servait une indexée sur
    les prix ; il payait moins que son propre contrat.

    CE QUE REND CETTE CLASSE est le coefficient qui corrige l'écart, en euros
    CONSTANTS puisque c'est l'unité des masses : le produit des taux
    d'indexation depuis la liquidation, déflaté des prix de la même période. Il
    vaut 1 l'année de la liquidation, ×1,15 au bout de vingt ans de projection
    — 2,45 % contre 1,75 % —, et jusqu'à ×3 pour les vingt années qui suivent
    une liquidation de 1960, où la masse salariale progressait de cinq points
    par an au-dessus des prix.

    CE QU'ELLE N'EST PAS. Elle ne choisit pas la règle : elle applique celle
    que ``mode_indexation`` porte déjà, quelle qu'elle soit. Sous le triple
    lock inversé, qui passe sous les prix la plupart des années, son
    coefficient descend en dessous de 1 et la correction joue à la baisse.
    C'est la conséquence logique de la règle, et non un défaut.
    """

    def __init__(self, simulateur: Simulateur,
                 premiere_annee: int, derniere_annee: int) -> None:
        macro = simulateur.macro
        indexation = simulateur.indexation
        #: Les prix, pour ce qui n'est revalorisé sur RIEN : voir
        #: :meth:`coefficient_nominal`.
        self._macro = macro
        #: L'année à partir de laquelle une réforme PROSPECTIVE revalorise ce
        #: qu'elle sert : voir :data:`CLES_PROSPECTIVES`.
        self.annee_bascule = simulateur.parametres.annee_bascule
        #: Le stock à la bascule garde-t-il les prix ? Voir :meth:`coefficient_stock`.
        self.stock_sur_les_prix = (
            simulateur.parametres.revalorisation_stock is RevalorisationStock.PRIX
        )
        self.premiere_annee = premiere_annee
        self.derniere_annee = max(derniere_annee, premiere_annee)
        index = 1.0
        self._index: dict[int, float] = {self.premiere_annee: index}
        for annee in range(self.premiere_annee + 1, self.derniere_annee + 1):
            # Le taux d'indexation est NOMINAL, les masses sont en euros
            # constants : on le déflate année par année, et non en bloc. Un
            # produit de taux nominaux divisé par une inflation cumulée serait
            # la même chose ici, mais cesserait de l'être dès qu'un plancher ou
            # un lissage s'appliquerait à l'un des deux — et il y en a un.
            index *= (1.0 + indexation.taux(annee).taux) * macro.coefficient_prix(
                annee, annee - 1
            )
            self._index[annee] = index

    def _valeur(self, annee: int) -> float:
        borne = min(max(annee, self.premiere_annee), self.derniere_annee)
        return self._index[borne]

    def coefficient(self, annee_liquidation: int, annee: int) -> float:
        """Ce que vaut en ``annee``, en euros constants, un euro de pension
        liquidé en ``annee_liquidation``.

        Vaut exactement 1 l'année de la liquidation et avant elle : une pension
        qui n'est pas encore servie ne se revalorise pas.
        """
        if annee <= annee_liquidation:
            return 1.0
        depart = self._valeur(annee_liquidation)
        return self._valeur(annee) / depart if depart else 1.0

    def coefficient_nominal(self, annee_liquidation: int, annee: int) -> float:
        """Ce que vaut en ``annee``, en euros constants, un euro de rente
        NOMINALE et constante liquidé en ``annee_liquidation``.

        C'est la rente du pilier capitalisé : un contrat à taux technique nul,
        que rien ne revalorise. Les prix seuls la déprécient, et ce coefficient
        est leur rapport — un l'année de la liquidation, moins ensuite. Le
        compte des flux du pilier la sert ainsi ; la garantie, qui la regarde,
        la revalorisait jusqu'au 23 septembre 2026 comme une pension
        notionnelle, sur la masse salariale.
        """
        if annee <= annee_liquidation:
            return 1.0
        return self._macro.coefficient_prix(annee, annee_liquidation)

    def coefficient_stock(self, annee_liquidation: int, annee: int,
                          prospectif: bool) -> float:
        """Le même coefficient, avec la règle du STOCK à la bascule.

        Une pension liquidée à compter de la bascule suit la règle du compte
        depuis sa liquidation, dans tous les cas. Une pension liquidée AVANT :

        - sous ``PRIX``, elle garde les prix — coefficient 1 en euros
          constants — à compter de la bascule. Pour une réforme prospective,
          qui n'existait pas avant, c'est 1 depuis toujours ; pour une réforme
          rétroactive, dont le compte fictif a été revalorisé sur sa règle
          jusqu'à la bascule, le coefficient est gelé à sa valeur de la
          bascule ;
        - sous ``REINDEXE``, la réforme prospective la prend à sa règle le jour
          de la bascule (``max(liquidation, bascule)``), et la rétroactive
          l'a toujours revalorisée sur la sienne.
        """
        bascule = self.annee_bascule
        if annee_liquidation >= bascule:
            return self.coefficient(annee_liquidation, annee)
        if self.stock_sur_les_prix:
            if prospectif:
                return 1.0
            return self.coefficient(annee_liquidation, min(annee, bascule))
        if prospectif:
            return self.coefficient(bascule, annee)
        return self.coefficient(annee_liquidation, annee)
