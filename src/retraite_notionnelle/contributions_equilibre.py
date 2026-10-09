"""Les contributions d'équilibre de l'Agirc-Arrco : prélevées pour la retraite, sans points.

Le salarié du privé et son employeur ne versent pas à la retraite
complémentaire que des cotisations. Ils versent aussi, depuis 1984, des
contributions qu'aucun point n'achète : l'ASF jusqu'au 31 mars 2001, l'AGFF qui
s'y substitue jusqu'en 2018, la contribution exceptionnelle et temporaire de
l'Agirc de 1997 à 2018, et depuis 2019 la contribution d'équilibre général et
la contribution d'équilibre technique. Leurs barèmes, leurs textes et ce que le
dépôt en sait sont dans ``legislation/contributions_equilibre_agirc_arrco.yaml``.

CE QUI LES LIT, ET CE QUI NE LES LIT PAS. Les indicateurs de cycle de vie
(:mod:`~retraite_notionnelle.cycle_de_vie`) comptent ce que la paie supporte
pour la retraite : ils les ajoutent à ce qu'une carrière verse. Le compte
notionnel ne les porte pas, par la décision du 2 octobre 2026 — ce sont des
contributions, et non des cotisations —, ni le scénario 1, qu'elles
n'ouvrent à aucun droit.

Ce que verse une carrière se lit ligne à ligne, comme le compte le lit
(:class:`~retraite_notionnelle.moteur.compte.ConstructeurCompte`) : sur le
revenu d'une année travaillée, tronqué l'année du départ, sous un plafond
proratisé sur les mois de l'activité, pour les régimes que le statut de la
ligne rend dus cette année-là, ses services passés retirés. Une année de
chômage n'en verse aucune : l'assurance chômage paie à l'Agirc-Arrco des
cotisations, que le compte porte, et la paie n'existe pas.
"""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass
from pathlib import Path

from .donnees.chargement import Fiabilite, charger_yaml, une_fois_par_instantane
from .somme import somme_ordonnee

#: Le fichier des barèmes, sous la racine des données.
FICHIER = Path("reference") / "legislation" / "contributions_equilibre_agirc_arrco.yaml"


@dataclass(frozen=True)
class Tranche:
    """Une tranche d'un barème : sa borne haute, en plafonds de la sécurité
    sociale (``None`` : sans limite), et les deux taux qui la prélèvent."""

    jusqu_en_plafonds: float | None
    salarie: float
    employeur: float

    @property
    def taux(self) -> float:
        return self.salarie + self.employeur


@dataclass(frozen=True)
class Bareme:
    """Les tranches d'une contribution à compter de ``debut``, pour les cadres
    et pour les autres."""

    debut: dt.date
    cadres: tuple[Tranche, ...]
    non_cadres: tuple[Tranche, ...]
    fiabilite: Fiabilite
    texte: str = ""

    def tranches(self, cadre: bool) -> tuple[Tranche, ...]:
        return self.cadres if cadre else self.non_cadres


def prelevement(tranches: tuple[Tranche, ...], assiette: float, plafond: float) -> float:
    """Ce que ``tranches`` prélèvent sur ``assiette``, sous un plafond de la
    sécurité sociale de ``plafond`` euros : chaque tranche va de la borne de
    la précédente à la sienne."""
    total = 0.0
    bas = 0.0
    for tranche in tranches:
        haut = (math.inf if tranche.jusqu_en_plafonds is None
                else tranche.jusqu_en_plafonds * plafond)
        if assiette > bas and haut > bas:
            total += (min(assiette, haut) - bas) * tranche.taux
        bas = max(bas, haut)
    return total


@dataclass(frozen=True)
class Contribution:
    """Une contribution d'équilibre, ses barèmes successifs et ceux qui la
    doivent."""

    code: str
    libelle: str
    #: Les régimes dont l'affiliation, une année donnée, la rend due.
    regimes: frozenset[str]
    baremes: tuple[Bareme, ...]
    #: Son dernier jour ; ``None`` tant qu'elle court.
    jusqu_au: dt.date | None = None
    #: Les statuts que son texte écarte.
    statuts_exclus: frozenset[str] = frozenset()
    #: Due seulement quand la rémunération dépasse ce nombre de plafonds, mais
    #: assise alors sur toutes ses tranches : la CET depuis 2019.
    due_au_dela_de_plafonds: float | None = None

    def bareme(self, jour: dt.date) -> Bareme | None:
        """Le barème en vigueur le ``jour``, ``None`` hors de sa vie."""
        if self.jusqu_au is not None and jour > self.jusqu_au:
            return None
        retenu = None
        for bareme in self.baremes:
            if bareme.debut <= jour:
                retenu = bareme
        return retenu

    def due_pour(self, statut: str, regimes: frozenset[str]) -> bool:
        return bool(regimes & self.regimes) and statut not in self.statuts_exclus

    def montant(self, annee: int, assiette: float, plafond: float, cadre: bool) -> float:
        """Ce qu'elle prélève sur ``assiette``, revenu d'une activité de
        l'année ``annee``, sous le plafond ``plafond`` proratisé sur les mêmes
        mois : la moyenne de ce que prélève le barème de chacun des douze
        mois, l'assiette répartie également sur eux."""
        if (self.due_au_dela_de_plafonds is not None
                and assiette <= self.due_au_dela_de_plafonds * plafond):
            return 0.0
        mois = []
        for rang in range(1, 13):
            bareme = self.bareme(dt.date(annee, rang, 1))
            mois.append(0.0 if bareme is None
                        else prelevement(bareme.tranches(cadre), assiette, plafond))
        return somme_ordonnee(mois) / 12.0


@dataclass(frozen=True)
class ContributionsEquilibre:
    """Les contributions d'équilibre, dans l'ordre du fichier."""

    contributions: tuple[Contribution, ...] = ()
    #: Avant 2019, est cadre l'année qu'un de ces régimes compte.
    regimes_cadres: frozenset[str] = frozenset()

    @property
    def regimes(self) -> frozenset[str]:
        """Tous les régimes qui en rendent une due."""
        return frozenset().union(*(c.regimes for c in self.contributions))

    def __getitem__(self, code: str) -> Contribution:
        for contribution in self.contributions:
            if contribution.code == code:
                return contribution
        raise KeyError(code)


def _tranches(lignes) -> tuple[Tranche, ...]:
    return tuple(Tranche(
        jusqu_en_plafonds=(None if ligne.get("jusqu_en_plafonds") is None
                           else float(ligne["jusqu_en_plafonds"])),
        salarie=float(ligne["salarie"]),
        employeur=float(ligne["employeur"]),
    ) for ligne in lignes or ())


def _bareme(brut: dict) -> Bareme:
    if "tous" in brut:
        cadres = non_cadres = _tranches(brut["tous"])
    else:
        cadres, non_cadres = _tranches(brut["cadres"]), _tranches(brut["non_cadres"])
    return Bareme(debut=brut["debut"], cadres=cadres, non_cadres=non_cadres,
                  fiabilite=Fiabilite.depuis_texte(brut["fiabilite"]),
                  texte=str(brut.get("texte") or "").strip())


_REGLES: dict[tuple[str, int, int], ContributionsEquilibre] = {}


@une_fois_par_instantane
def charger_contributions_equilibre(racine: Path) -> ContributionsEquilibre:
    """Les contributions de ``racine`` (la racine des données), gardées comme
    les autres points de passage du disque, indexées sur la signature du
    fichier ; sans fichier, aucune."""
    chemin = racine / FICHIER
    if not chemin.exists():
        return ContributionsEquilibre()
    etat = chemin.stat()
    cle = (str(chemin), etat.st_mtime_ns, etat.st_size)
    if cle in _REGLES:
        return _REGLES[cle]
    brut = charger_yaml(chemin)
    contributions = []
    for entree in brut.get("contributions") or ():
        seuil = entree.get("due_au_dela_de_plafonds")
        contributions.append(Contribution(
            code=entree["code"],
            libelle=entree["libelle"],
            regimes=frozenset(entree["regimes"]),
            baremes=tuple(sorted((_bareme(b) for b in entree["baremes"]),
                                 key=lambda b: b.debut)),
            jusqu_au=entree.get("jusqu_au"),
            statuts_exclus=frozenset(entree.get("statuts_exclus") or {}),
            due_au_dela_de_plafonds=None if seuil is None else float(seuil),
        ))
    regles = ContributionsEquilibre(
        contributions=tuple(contributions),
        regimes_cadres=frozenset(brut.get("regimes_cadres") or ()),
    )
    _REGLES[cle] = regles
    return regles


def _forfait(catalogue, regimes: frozenset[str], annee: int, macro, part: float) -> float | None:
    """Le forfait sur lequel l'un de ``regimes`` prélève, l'année ``annee`` —
    le SMIC des cultes —, proratisé sur ``part`` ; ``None`` sans forfait."""
    for code in sorted(regimes):
        periode = catalogue[code].periode(annee) if code in catalogue else None
        if periode is not None and periode.assiette_forfaitaire:
            return periode.repere_assiette(macro.plafond_securite_sociale(annee),
                                           macro.smic_horaire(annee)) * part
    return None


def contributions_d_une_carriere(simulateur, carriere) -> dict[int, float]:
    """Les contributions d'équilibre que la paie de ``carriere`` a supportées,
    année par année, en euros courants, la part du salarié et celle de
    l'employeur réunies. Une année qui n'en verse aucune n'y est pas."""
    regles = charger_contributions_equilibre(simulateur.parametres.racine_donnees)
    if not regles.contributions:
        return {}
    affiliations = simulateur.affiliations
    macro = simulateur.macro
    catalogue = simulateur.catalogue
    sommes: dict[int, float] = {}
    for ligne in carriere.lignes:
        if not ligne.cotise:
            continue
        part = carriere.part_retenue_ligne(ligne)
        if part <= 0 or ligne.fraction_annee <= 0:
            continue
        annee = ligne.annee
        entree = carriere.date_entree(ligne.affiliation)
        plafond_annuel = macro.plafond_securite_sociale(annee)
        codes = frozenset(affiliations.regimes(ligne.affiliation, annee, entree,
                                               revenu=ligne.revenu, plafond=plafond_annuel))
        services, _ = affiliations.services_passes(ligne.affiliation, annee, entree)
        codes -= services
        if not codes & regles.regimes:
            continue
        # Comme au compte : l'année du départ ne porte que les mois qui le
        # précèdent, et le plafond se proratise sur les mêmes mois.
        assiette = ligne.revenu * min(1.0, part / ligne.fraction_annee)
        plafond = plafond_annuel * part
        cadre = bool(codes & regles.regimes_cadres)
        montants = []
        for contribution in regles.contributions:
            if not contribution.due_pour(ligne.affiliation, codes):
                continue
            forfait = _forfait(catalogue, codes & contribution.regimes, annee, macro, part)
            base = assiette if forfait is None else forfait
            montants.append(contribution.montant(annee, base, plafond, cadre))
        montant = somme_ordonnee(montants)
        if montant > 0.0:
            sommes[annee] = sommes.get(annee, 0.0) + montant
    return sommes
