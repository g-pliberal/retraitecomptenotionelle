"""Liquider : ``liquider(demande, état, contexte)`` (docs/architecture.md, § 7.3).

Une FONCTION PURE, qui ne lit rien d'autre que ses trois entrées :

* LA DEMANDE (:class:`Demande`) dit la personne, la date d'effet,
  l'événement qui l'appelle, le motif et la nature ;
* L'ÉTAT (:class:`Etat`) est la chronologie du réseau, lue par sa vue, la
  carrière, et le journal de l'échéancier ;
* LE CONTEXTE (:class:`Contexte`) dit l'univers — aujourd'hui le droit réel,
  dont le moteur du scénario 1 tient les tables — et ce que le calcul
  neutralise : une couche d'un seul calcul (§ 4.8).

Pour une demande, elle fait l'acquisition — les quatre étapes du relevé des
droits, :mod:`.releve` —, puis les trois étapes de la liquidation :
:mod:`.ouvrir`, :mod:`.liquider`, :mod:`.completer`. Entre les deux
dernières, elle MESURE ce qu'apportent les trimestres des enfants, l'AVPF et
les points gratuits, par des liquidations d'essai, chacune sous une
neutralisation de plus : c'est ainsi que la cascade des avantages isole un
avantage qui agit sur la décote et la proratisation (§ 6.4). Une liquidation
d'essai ne va pas au journal.

L'ASPA n'est pas de la liquidation : elle regarde toutes les ressources, et
c'est l'étape « foyer et net » (:mod:`.foyer`) que l'échéancier applique
ensuite.

Ce qu'elle rend, :class:`Liquidation`, suit le contrat C.6
(``data/reference/contrats/liquidation.yaml``). Chaque appel est compté,
liquidations d'essai comprises (:func:`appels`) : le budget de calcul les
borne (§ 7.8). Son jumeau est ``moteur/js/droit/liquidation.js``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from ..donnees.chargement import Fiabilite
from . import completer as _completer
from . import liquider as _liquider
from . import ouvrir as _ouvrir
from . import releve as _releve
from .commun import AvantageApplique, PensionRegime, date_d_effet

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..scenarios.actuel import ScenarioActuel
    from .completer import Complements
    from .liquider import Pensions
    from .ouvrir import Ouverture
    from .releve import Releve

#: La version du contrat C.6 que :meth:`Liquidation.donnees` suit.
SCHEMA_VERSION = 1

#: Ce qu'un calcul peut neutraliser : la liste ``neutralisations`` du
#: vocabulaire, que le contexte refuse de dépasser.
NEUTRALISATIONS = frozenset({"avantages_non_contributifs", "avpf", "points_gratuits",
                             "decote_surcote", "successions"})

#: Ce que chaque dispositif s'appelle dans la cascade des avantages.
_LIBELLE_MAJORATION = {
    "mda": "Majoration de durée d'assurance",
    "bonifications": "Bonification pour enfants",
}

#: Ce que chaque mesure de la cascade neutralise de plus que la précédente.
NEUTRALISATION_MESUREE = {
    "majoration_duree_assurance": "avantages_non_contributifs",
    "avpf": "avpf",
    "points_gratuits_rco": "points_gratuits",
}


@dataclass(frozen=True)
class Demande:
    """La demande (contrat C.6, ``demande``)."""

    personne: str
    #: La date d'effet (AAAA-MM-JJ) ; ``None`` pour une carrière sans départ.
    date_effet: str | None
    #: L'événement qui l'appelle — sa sorte au vocabulaire — et sa date.
    evenement: str = "depart"
    date_evenement: str | None = None
    motif: str = "vieillesse"
    nature: str = "definitive"
    #: Les régimes que la demande vise ; aucun : tous ceux où un droit est
    #: acquis, comme le modèle liquide tout à la fois.
    regimes: tuple[str, ...] = ()

    def donnees(self) -> dict:
        """La demande, telle que le contrat C.6 la décrit. Les régimes qu'elle
        ne nomme pas encore sont un manque, que le tableau de bord compte."""
        donnee = {"personne": self.personne, "date_effet": self.date_effet,
                  "evenement": {"sorte": self.evenement,
                                "date": self.date_evenement or self.date_effet},
                  "motif": self.motif, "nature": self.nature}
        if self.regimes:
            donnee["regimes"] = list(self.regimes)
        return donnee


def demande_de_depart(carriere: Carriere, nature: str = "definitive") -> Demande:
    """La demande qu'un départ en retraite appelle : celui de la carrière, à
    sa date d'effet, pour une pension de vieillesse."""
    date = date_d_effet(carriere)
    return Demande(personne=carriere.personne, date_effet=date, date_evenement=date,
                   nature=nature)


@dataclass(frozen=True)
class Etat:
    """L'état que la liquidation lit : la chronologie du réseau, par sa vue,
    la carrière, et le journal de l'échéancier (§ 7.4)."""

    carriere: Carriere
    journal: object | None = None


@dataclass(frozen=True)
class Contexte:
    """Le contexte d'une liquidation (§ 7.3) : l'univers, la date
    d'observation, l'hypothèse, et ce qu'une couche d'un seul calcul
    neutralise (liste ``neutralisations`` du vocabulaire)."""

    #: L'univers : aujourd'hui le droit réel, dont le moteur du scénario 1
    #: tient les tables, jusqu'aux fiches (phase 6).
    univers: ScenarioActuel
    neutralisations: frozenset[str] = frozenset()
    #: La date d'observation : ``None``, celle de la fabrication des données.
    observation: str | None = None
    hypothese: object | None = None

    def __post_init__(self) -> None:
        inconnues = self.neutralisations - NEUTRALISATIONS
        if inconnues:
            raise ValueError(f"neutralisations inconnues du vocabulaire : {sorted(inconnues)}")

    def neutralise(self, nom: str) -> bool:
        return nom in self.neutralisations

    def neutralisant(self, *noms: str) -> Contexte:
        """Le même contexte, qui neutralise aussi ``noms`` : celui d'une
        liquidation d'essai."""
        return replace(self, neutralisations=self.neutralisations | frozenset(noms))

    def donnees(self) -> dict:
        return {"univers": "droit_reel", "observation": self.observation,
                "hypothese": self.hypothese,
                "neutralisations": sorted(self.neutralisations)}


@dataclass(frozen=True)
class Mesure:
    """Ce qu'une liquidation d'essai mesure (contrat C.6, ``mesure``)."""

    code: str
    neutralisation: str
    montant: float


@dataclass(frozen=True, eq=False)
class Liquidation:
    """Ce que :func:`liquider` rend (contrat C.6)."""

    demande: Demande
    contexte: Contexte
    releve: Releve
    ouverture: Ouverture
    pensions: Pensions
    complements: Complements
    #: Ce qu'apportent les avantages que la cascade mesure.
    mesures: tuple[Mesure, ...]
    #: Les avantages non contributifs appliqués, dans l'ordre où le droit les
    #: applique : ceux que la cascade mesure, puis ceux qui complètent.
    avantages: tuple[AvantageApplique, ...]
    #: Le total des pensions, complété.
    total: float
    #: La rente des régimes provisionnés, servie à part.
    hors_repartition: float
    #: Le total d'avant tout avantage non contributif, capitalisation déduite.
    total_contributif: float
    fiabilite: Fiabilite

    @property
    def carriere(self) -> Carriere:
        return self.releve.carriere

    @property
    def regimes(self) -> tuple[PensionRegime, ...]:
        """Les pensions de régime, complétées."""
        return self.complements.regimes

    def donnees(self) -> dict:
        """La liquidation, telle que le contrat C.6 la décrit : ses
        composantes — la pension de chaque régime, puis la majoration pour
        enfants —, les lignes du relevé qu'elle a lues, et ses mesures."""
        catalogue = self.contexte.univers.catalogue
        isoler = self.contexte.univers.parametres.isoler_capitalisation
        debut = self.demande.date_effet
        composantes = [{
            "id": f"pension_{p.regime}", "beneficiaire": self.demande.personne,
            "montant": {"annuel": p.montant, "monnaie": "EUR"}, "debut": debut,
            "regime": p.regime, "detail": p.detail,
            "hors_repartition": bool(isoler and catalogue[p.regime].hors_repartition),
        } for p in self.regimes]
        for avantage in self.complements.avantages:
            if avantage.code == "majoration_enfants":
                composantes.append({
                    "id": "majoration_enfants", "fiche": _completer.FICHES[avantage.code],
                    "beneficiaire": self.demande.personne,
                    "montant": {"annuel": avantage.montant, "monnaie": "EUR"},
                    "debut": debut, "detail": avantage.detail})
        return {
            "schema_version": SCHEMA_VERSION,
            "demande": self.demande.donnees(),
            "contexte": self.contexte.donnees(),
            "composantes": composantes,
            "lignes_consommees": [ligne["id"] for ligne in self.releve.lignes()],
            "origine": "calculee",
            "mesures": [{"code": m.code, "neutralisation": m.neutralisation,
                         "montant": m.montant} for m in self.mesures],
        }


#: Le nombre d'appels de :func:`liquider`, liquidations d'essai comprises.
_appels = 0


def appels() -> int:
    """Combien de liquidations ont été calculées depuis le lancement : le
    budget de calcul les compte, témoin par témoin (§ 7.8)."""
    return _appels


def liquider(demande: Demande, etat: Etat, contexte: Contexte) -> Liquidation:
    """La liquidation de ``demande``, dans ``etat``, sous ``contexte``."""
    global _appels
    _appels += 1
    moteur = contexte.univers
    avantages_non_contributifs = not contexte.neutralise("avantages_non_contributifs")
    avpf = not contexte.neutralise("avpf")
    points_gratuits = not contexte.neutralise("points_gratuits")
    releve = _releve.construire(
        moteur, etat.carriere, avantages_non_contributifs=avantages_non_contributifs,
        points_gratuits=points_gratuits,
        liquider_successions=not contexte.neutralise("successions"))
    carriere = releve.carriere
    majoration_enfants = releve.durees.enfants
    gratuits_attribues = releve.droits.gratuits
    fiabilite = Fiabilite.CERTIFIEE
    if majoration_enfants is not None:
        fiabilite = min(fiabilite, majoration_enfants.fiabilite)

    ouverture = _ouvrir.ouvrir(moteur, releve)
    liquidees = _liquider.liquider_chaque_regime(moteur, releve, ouverture, contexte)
    pensions = list(liquidees.regimes)

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
            if moteur.catalogue[p.regime].hors_repartition)
        if moteur.parametres.isoler_capitalisation else 0.0
    )
    total_contributif = total - hors_repartition
    avantages: list[AvantageApplique] = []

    # Avantages non contributifs du droit positif, DANS L'ORDRE OÙ LE DROIT
    # LES APPLIQUE, et l'ordre commande le résultat : la majoration de durée
    # d'assurance, l'AVPF et les points gratuits de la RCO d'abord, qui
    # déplacent la décote, la proratisation, le salaire annuel moyen ou le
    # compte de points ; puis les deux minima, qui
    # portent la pension de base à son plancher ; puis seulement la
    # majoration pour enfants, qui se calcule SUR CE plancher ; l'ASPA
    # enfin, qui est différentielle et complète tout le reste.
    #
    # Ce module prenait le minimum et la majoration dans l'autre sens : les
    # 10 % portaient sur une pension que le minimum n'avait pas encore
    # relevée, et l'écrêtement du minimum comparait au plafond un total qui
    # incluait déjà la majoration, alors que l'article L. 173-2 ne retient
    # que les pensions personnelles.

    if avantages_non_contributifs and majoration_enfants is not None:
        # Effet des trimestres accordés au titre des enfants : la même
        # carrière sans eux, tout le reste égal. C'est la seule façon
        # d'isoler un avantage qui agit sur la décote et sur la
        # proratisation.
        sans_mda = liquider(demande, Etat(carriere),
                            contexte.neutralisant("avantages_non_contributifs"))
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
        sans_avpf = liquider(demande, Etat(carriere),
                             contexte.neutralisant("avantages_non_contributifs", "avpf"))
        effet_avpf = total_contributif - sans_avpf.total_contributif
        total_contributif = sans_avpf.total_contributif
        if abs(effet_avpf) > 1e-9:
            avantages.insert(0, AvantageApplique(
                code="avpf",
                libelle="Assurance vieillesse des parents au foyer",
                montant=effet_avpf,
                detail="salaire forfaitaire au SMIC porté au compte",
            ))

    if avantages_non_contributifs and points_gratuits and gratuits_attribues:
        # Effet des POINTS GRATUITS de la RCO agricole, mesuré comme celui
        # de l'AVPF : la même carrière sans eux, la MDA et l'AVPF déjà
        # retirées. Ils ne tiennent qu'à la durée et à l'âge : retirer
        # l'AVPF ne les touche pas, retirer la MDA peut les faire tomber —
        # leur effet est alors compté dans celui de la MDA, qui les a
        # ouverts, et le recalcul ci-dessous n'en trouve plus rien.
        sans_gratuits = liquider(demande, Etat(carriere), contexte.neutralisant(
            "avantages_non_contributifs", "avpf", "points_gratuits"))
        effet_gratuits = total_contributif - sans_gratuits.total_contributif
        total_contributif = sans_gratuits.total_contributif
        if abs(effet_gratuits) > 1e-9:
            points_cites = sum(p for p, _ in gratuits_attribues.values())
            avant = min(a for _, a in gratuits_attribues.values())
            avantages.insert(0, AvantageApplique(
                code="points_gratuits_rco",
                libelle="Points gratuits de la complémentaire agricole",
                montant=effet_gratuits,
                detail=(f"{points_cites:,.2f} points pour les années de chef "
                        f"d'exploitation d'avant {avant}"),
            ))

    complements = _completer.completer(moteur, releve, ouverture, liquidees, contexte)
    return Liquidation(
        demande=demande,
        contexte=contexte,
        releve=releve,
        ouverture=ouverture,
        pensions=liquidees,
        complements=complements,
        mesures=tuple(Mesure(a.code, NEUTRALISATION_MESUREE[a.code], a.montant)
                      for code in NEUTRALISATION_MESUREE for a in avantages
                      if a.code == code),
        avantages=tuple(avantages) + complements.avantages,
        total=complements.total,
        hors_repartition=hors_repartition,
        total_contributif=total_contributif,
        fiabilite=min(fiabilite, ouverture.fiabilite, liquidees.fiabilite,
                      complements.fiabilite),
    )
