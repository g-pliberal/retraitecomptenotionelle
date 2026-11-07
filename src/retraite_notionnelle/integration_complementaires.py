"""Les complémentaires sous les décisions 36 à 48 : vivre de ses réserves, puis rejoindre le régime général.

LES DÉCISIONS (``docs/feuille_de_route_programme.md``, action 186, chantier 6).
La CEG et la CET sont supprimées dès maintenant (36). Une complémentaire garde
ses autres cotisations jusqu'à son intégration (40, 48), et ses réserves
paient les recettes qu'elle perd (38). Elle rejoint le régime général l'année
où elles s'épuisent, pas avant, « dans l'ordre mathématique démontré par notre
modèle » (37) : mise en résolution, elle voit ses pensions garanties par le
régime général, qui reprend ses cotisants et ses retraités (39). Elle ne vit
que de ses cotisations, ni impôt affecté ni argent de l'État (12), sauf la
compensation des allègements de l'Agirc-Arrco, que la loi en vigueur garde
(47) ; ses pensions suivent ses règles jusque-là (43).

CE QUE CE MODULE CALCULE. Pour chaque caisse, de l'année de la bascule à 2070,
ses réserves en fin d'année, en part de PIB, et l'année où elles passent sous
zéro : celle de son intégration. Il part de la trajectoire que le COR projette
à législation inchangée (``comptes_complementaires.csv``, juin 2024), et en
retire ce que les décisions coupent :

- à l'Agirc-Arrco, la CEG et la CET, une part fixe de ses cotisations
  (:func:`contributions_supprimees_agirc_arrco`), appliquée à ce qu'elle reçoit
  au titre des salaires — cotisations, compensation des allègements, transferts
  de l'Unédic et du FSV, qui paient aussi la CEG ; la compensation, gardée
  (décision 47), perd ainsi la part qui couvrait la CEG ;
- aux autres, les impôts et taxes affectés : les droits sur les alcools de la
  complémentaire agricole (décision 12).

Les réserves de départ sont celles de fin 2025, en valeur de marché (COR,
juin 2026, tableau 2.3 : ``reserves_regimes.csv``), rapportées au PIB de 2025.

LA RÈGLE DES RÉSERVES, CELLE DU COR. Dans son classeur, les réserves d'une
année sont celles de la précédente, multipliées par un facteur que le classeur
ne nomme pas (un à partir de 2028 : les réserves gardent leur part de PIB), plus
le solde élargi, produits financiers compris. La projection garde cette règle,
et suit l'ÉCART à la trajectoire du COR : il croît du même facteur et du
rendement que le COR prête aux réserves — ses produits de gestion et
financiers rapportés aux réserves de l'année précédente, au plus 5 % —, et
perd chaque année les recettes coupées. Les parts de financement du COR ne sont
publiées qu'en 2023, 2030, 2040, 2050 et 2070 : entre deux, elles s'interpolent
en ligne droite, une hypothèse de ce module que ``StructureFinancement`` refuse
de faire pour qui la lit.

TROIS CAISSES À PART.
- La CNBF : le COR la projette d'un seul tenant, base et complémentaire. La
  complémentaire en prend la part de ses prestations, que le tableau 2.3 du COR
  donne par ses réserves et leurs mois de prestations (55 %), sans les droits de
  plaidoirie, qui financent la base (L. 723-3 du code de la sécurité sociale).
- Les dix sections complémentaires des libéraux : consolidées, comme le COR les
  projette.
- Le RAFP n'est pas projeté : provisionné à 146 % de ses engagements en valeur
  de marché fin 2025 (COR, juin 2026, § 3.4), il ne vit pas de répartition, et
  ses réserves ne s'épuisent pas.
"""
from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

from .contributions_equilibre import charger_contributions_equilibre
from .donnees.chargement import charger_serie_annuelle, charger_yaml
from .donnees.financement_regimes import StructureFinancement
from .somme import somme_ordonnee

#: La dernière année projetée : celle du classeur du COR.
FIN = 2070

#: Le rendement des réserves au-delà duquel le poste « produits de gestion,
#: financiers » du COR trahit des produits de gestion : la complémentaire
#: agricole y porterait 25 % de ses réserves en 2026.
RENDEMENT_MAXIMAL = 0.05

#: L'année des assiettes de l'Agirc-Arrco sur lesquelles se chiffrent la CEG et
#: la CET : la dernière que le Chiffr'Agirc-Arrco 2026 publie.
ANNEE_DES_ASSIETTES = 2024


@dataclass(frozen=True)
class Caisse:
    """Une complémentaire, son code au classeur du COR, et ce qui la distingue."""

    code: str
    libelle: str
    cor: str
    #: Les impôts du compte du COR vont au régime de base de la même caisse,
    #: non à la complémentaire : la CNBF, dont le COR consolide les deux.
    impots_au_regime_de_base: bool = False
    #: Le code de son régime de base dans ``reserves_regimes.csv``, quand le COR
    #: les projette ensemble : la complémentaire en prend sa part.
    base: str | None = None


CAISSES: tuple[Caisse, ...] = (
    Caisse("msa_exploitants_complementaire",
           "Complémentaire des exploitants agricoles (RCO)",
           "msa_exploitants_complementaire"),
    Caisse("agirc_arrco", "Agirc-Arrco", "agirc_arrco"),
    Caisse("ircantec", "Ircantec", "ircantec"),
    Caisse("cnbf_complementaire", "Complémentaire des avocats (CNBF)", "cnbf",
           impots_au_regime_de_base=True, base="cnbf"),
    Caisse("rci_complementaire", "Complémentaire des indépendants (RCI)",
           "rci_complementaire"),
    Caisse("cnavpl_complementaire",
           "Sections complémentaires des libéraux (dix, consolidées)",
           "cnavpl_complementaire"),
    Caisse("crpnpac", "Personnel navigant de l'aviation civile (CRPNPAC)", "crpnpac"),
)

#: Les codes du classeur du COR que la projection lit.
CAISSES_DU_COR: tuple[str, ...] = tuple(c.cor for c in CAISSES)


def _lignes(chemin: Path) -> list[dict[str, str]]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


# --- Ce que la décision 36 retire à l'Agirc-Arrco -------------------------


@dataclass(frozen=True)
class ContributionsSupprimees:
    """La CEG, la CET et les cotisations de l'Agirc-Arrco, sur les assiettes
    d'une année, en millions d'euros."""

    annee: int
    ceg_meur: float
    cet_meur: float
    cotisations_meur: float

    @property
    def part(self) -> float:
        """La part de ce que l'Agirc-Arrco prélève sur les salaires que la CEG
        et la CET font, et que leur suppression retire."""
        retire = self.ceg_meur + self.cet_meur
        return retire / (self.cotisations_meur + retire)


def _taux_agirc_arrco(racine: Path, annee: int) -> dict[str, float]:
    """Le taux prélevé de chaque tranche, majoration d'appel comprise."""
    fiche = charger_yaml(racine / "reference" / "regimes" / "agirc_arrco.yaml")
    taux = {}
    for periode in fiche["periodes"]:
        fin = periode.get("fin")
        if periode["debut"] <= annee and (fin is None or annee <= fin):
            taux[periode["assiette"]] = float(periode["taux_cotisation_retraite"])
    return taux


def contributions_supprimees_agirc_arrco(
        racine: Path, annee: int = ANNEE_DES_ASSIETTES) -> ContributionsSupprimees:
    """La CEG et la CET de l'année, à leurs taux, sur les assiettes de
    l'Agirc-Arrco, IEG comprises.

    La CEG prélève 2,15 % de la tranche 1 et 2,70 % de la tranche 2. La CET,
    0,35 % des tranches 1 et 2 des seuls salariés au-dessus du plafond : leur
    tranche 2 est toute la tranche 2, leur tranche 1 un plafond chacun, leur
    nombre la part des cotisants en équivalent temps plein au-dessus du plafond,
    rapportée à la masse divisée par le salaire moyen.
    """
    valeurs = {(l["perimetre"], l["poste"]): float(l["valeur"])
               for l in _lignes(racine / "reference" / "regimes" / "assiettes_agirc_arrco.csv")
               if int(l["annee"]) == annee}
    tranche_1 = valeurs[("ieg_compris", "tranche_1")]
    tranche_2 = valeurs[("ieg_compris", "tranche_2")]
    total = valeurs[("ieg_compris", "total")]
    plafond = charger_serie_annuelle(
        racine / "reference" / "macro" / "plafond_securite_sociale.csv", "pass_eur",
        nom="pass_eur")(annee)
    au_dessus = 1.0 - valeurs[("cotisants", "part_eqtp_sous_le_plafond")]
    cotisants_eqtp = total * 1e6 / valeurs[("cotisants", "salaire_moyen_eqtp")]
    tranche_1_au_dessus = au_dessus * cotisants_eqtp * plafond / 1e6

    contributions = charger_contributions_equilibre(racine)
    jour = dt.date(annee, 1, 1)
    ceg_t1, ceg_t2 = (t.taux for t in contributions["ceg"].bareme(jour).tranches(False))
    (cet,) = (t.taux for t in contributions["cet"].bareme(jour).tranches(False))
    taux = _taux_agirc_arrco(racine, annee)
    return ContributionsSupprimees(
        annee=annee,
        ceg_meur=ceg_t1 * tranche_1 + ceg_t2 * tranche_2,
        cet_meur=cet * (tranche_1_au_dessus + tranche_2),
        cotisations_meur=taux["tranche_1"] * tranche_1 + taux["tranche_2"] * tranche_2,
    )


# --- La projection --------------------------------------------------------


@dataclass(frozen=True)
class Projection:
    """Une caisse sous les décisions, en part de PIB, année par année."""

    caisse: Caisse
    #: Ses réserves en fin d'année, de la veille de la bascule à son
    #: intégration (la première année sous zéro comprise) ou à 2070.
    reserves: dict[int, float]
    #: Ses dépenses, ses recettes sous les décisions, et ce que les décisions
    #: lui retirent, de la bascule à son intégration ou à 2070.
    depenses: dict[int, float] = field(default_factory=dict)
    recettes: dict[int, float] = field(default_factory=dict)
    pertes: dict[int, float] = field(default_factory=dict)
    #: L'année où ses réserves passent sous zéro, et où elle rejoint le régime
    #: général ; ``None`` si elle tient jusqu'en 2070.
    annee_integration: int | None = None


class _Parts:
    """Les parts de financement d'une caisse, interpolées entre les années
    publiées."""

    def __init__(self, structure: StructureFinancement, regime: str) -> None:
        self._structure = structure
        self._regime = regime
        self._annees = structure.annees(regime)

    def __call__(self, poste: str, annee: int) -> float:
        annees = self._annees
        if annee <= annees[0]:
            return self._structure.part(self._regime, poste, annees[0])
        if annee >= annees[-1]:
            return self._structure.part(self._regime, poste, annees[-1])
        apres = next(a for a in annees if a >= annee)
        avant = max(a for a in annees if a <= annee)
        if apres == avant:
            return self._structure.part(self._regime, poste, annee)
        poids = (annee - avant) / (apres - avant)
        return ((1.0 - poids) * self._structure.part(self._regime, poste, avant)
                + poids * self._structure.part(self._regime, poste, apres))


def _comptes(racine: Path) -> dict[tuple[str, str], dict[int, float]]:
    comptes: dict[tuple[str, str], dict[int, float]] = {}
    for ligne in _lignes(racine / "reference" / "regimes" / "comptes_complementaires.csv"):
        comptes.setdefault((ligne["regime"], ligne["poste"]), {})[int(ligne["annee"])] = \
            float(ligne["part_pib"])
    return comptes


def _reserves_2025(racine: Path) -> dict[tuple[str, str], tuple[float, float | None]]:
    return {(l["regime"], l["poste"]): (float(l["montant_md"]),
                                        float(l["mois_prestations"]) if l["mois_prestations"] else None)
            for l in _lignes(racine / "reference" / "regimes" / "reserves_regimes.csv")}


def _part_de_la_complementaire(caisse: Caisse, reserves) -> float:
    """La part de la complémentaire dans les prestations de sa caisse, quand le
    COR la projette avec sa base : les réserves de chacune divisées par leurs
    mois de prestations."""
    if caisse.base is None:
        return 1.0
    montant, mois = reserves[(caisse.code, "reserves")]
    montant_base, mois_base = reserves[(caisse.base, "reserves")]
    complementaire = montant / mois
    return complementaire / (complementaire + montant_base / mois_base)


def _trajectoire_du_cor(comptes, regime: str) -> tuple[dict[int, float], dict[int, float]]:
    """Les réserves du COR, prolongées sous zéro par ses soldes une fois qu'il
    les a épuisées, et le facteur de sa règle, année par année."""
    reserves_cor = comptes[(regime, "reserves")]
    soldes = comptes[(regime, "solde_elargi")]
    annees = sorted(reserves_cor)
    trajectoire = {annees[0]: reserves_cor[annees[0]]}
    facteurs: dict[int, float] = {}
    for annee in annees[1:]:
        precedente = reserves_cor[annee - 1]
        if precedente > 0 and reserves_cor[annee] > 0:
            facteurs[annee] = (reserves_cor[annee] - soldes[annee]) / precedente
            trajectoire[annee] = reserves_cor[annee]
        else:
            facteurs[annee] = 1.0
            trajectoire[annee] = trajectoire[annee - 1] + soldes[annee]
    return trajectoire, facteurs


def _projeter(caisse: Caisse, comptes, structure, reserves_2025, pib_2025: float,
              debut: int, part_supprimee: float, reserves_techniques: bool,
              impots_affectes_gardes: bool) -> Projection:
    parts = _Parts(structure, caisse.cor)
    echelle = _part_de_la_complementaire(caisse, reserves_2025)
    trajectoire, facteurs = _trajectoire_du_cor(comptes, caisse.cor)
    ressources = comptes[(caisse.cor, "ressources")]
    depenses = comptes[(caisse.cor, "depenses")]

    def montant(poste: str, annee: int) -> float:
        """Un poste de financement en part de PIB : sa part, rapportée au
        financement total, que le besoin de financement complète."""
        financement = ressources[annee] / (1.0 - parts("besoin_de_financement", annee))
        return parts(poste, annee) * financement

    def perte(annee: int) -> float:
        if caisse.code == "agirc_arrco":
            salaires = somme_ordonnee(montant(p, annee) for p in (
                "cotisations", "impots_et_taxes", "transferts"))
            return part_supprimee * salaires
        if caisse.impots_au_regime_de_base or not impots_affectes_gardes:
            return montant("impots_et_taxes", annee)
        return 0.0

    poste = "reserves_techniques" if (reserves_techniques and caisse.code == "agirc_arrco") \
        else "reserves"
    depart = reserves_2025[(caisse.code, poste)][0] / pib_2025
    ecart = depart - echelle * trajectoire[debut - 1]
    projection = Projection(caisse=caisse, reserves={debut - 1: depart})
    for annee in range(debut, FIN + 1):
        rendement = 0.0
        if trajectoire[annee - 1] > 0 and comptes[(caisse.cor, "reserves")][annee] > 0:
            rendement = min(RENDEMENT_MAXIMAL,
                            montant("autres_produits", annee) / trajectoire[annee - 1])
        pertes = echelle * perte(annee)
        # Les recettes : celles du COR, moins ce que les décisions coupent,
        # plus ou moins ce que rapporte l'écart de réserves à sa trajectoire.
        projection.recettes[annee] = (echelle * ressources[annee] - pertes
                                      + rendement * ecart)
        ecart = (facteurs[annee] + rendement) * ecart - pertes
        reserves = echelle * trajectoire[annee] + ecart
        projection.reserves[annee] = reserves
        projection.depenses[annee] = echelle * depenses[annee]
        projection.pertes[annee] = pertes
        if reserves < 0:
            return Projection(caisse=caisse, reserves=projection.reserves,
                              depenses=projection.depenses, recettes=projection.recettes,
                              pertes=projection.pertes, annee_integration=annee)
    return projection


def projeter_les_caisses(racine: Path, *, debut: int | None = None,
                         reserves_techniques: bool = False,
                         impots_affectes_gardes: bool = False) -> dict[str, Projection]:
    """Chaque complémentaire sous les décisions 36 à 48, de la bascule à 2070.

    ``reserves_techniques`` part des seules réserves techniques de
    l'Agirc-Arrco, son fonds de roulement mis à part. ``impots_affectes_gardes``
    lit la décision 48 à la lettre — une complémentaire « ne perd que la CEG et
    la CET » — et laisse ses impôts à la complémentaire agricole.
    """
    if debut is None:
        from .config import Parametres
        debut = Parametres().annee_bascule
    comptes = _comptes(racine)
    structure = StructureFinancement(racine)
    reserves_2025 = _reserves_2025(racine)
    pib = charger_serie_annuelle(racine / "reference" / "macro" / "pib_courant.csv",
                                 "pib_meur", nom="pib_courant")(debut - 1) / 1e3
    part_supprimee = contributions_supprimees_agirc_arrco(racine).part
    return {caisse.code: _projeter(caisse, comptes, structure, reserves_2025, pib, debut,
                                   part_supprimee, reserves_techniques, impots_affectes_gardes)
            for caisse in CAISSES}


def ordre_d_integration(projections: dict[str, Projection]) -> list[tuple[str, int | None]]:
    """Les caisses dans l'ordre où elles rejoignent le régime général ; celles
    qui tiennent jusqu'en 2070 à la fin."""
    return sorted(((code, p.annee_integration) for code, p in projections.items()),
                  key=lambda paire: (paire[1] is None, paire[1] or 0))
