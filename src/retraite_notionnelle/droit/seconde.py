"""Les droits de l'activité exercée après le départ (docs/architecture.md,
§ 7.4 ; fiches ``droits_apres_la_premiere_pension`` et ``seconde_pension``).

Après une première pension de base, l'activité n'ouvre plus aucun droit à
retraite, de base ni complémentaire : pour qui prend sa première pension
depuis le 1er janvier 2015 (L. 161-22-1 A), puis pour tous sur les périodes
accomplies depuis le 1er janvier 2023 (L. 161-22-1). Avant, aucun texte
général n'éteint rien : l'activité ouvre des droits dans les régimes qui n'ont
pas encore liquidé, selon leurs règles — ce que le modèle ne calcule pas
encore, et qu'il dit.

Depuis 2023, le retraité en cumul intégral se constitue une NOUVELLE pension
dans le régime de base de son activité, liquidée depuis le 1er septembre 2023
(L. 161-22-1-1) : au taux plein, sur les seules périodes cotisées de cumul
intégral accomplies depuis le 1er janvier 2023, sans majoration ni minimum. Son
salaire de base est le salaire mensuel moyen des années qui valident au moins
un trimestre, sur les mois d'assurance de la période (R. 351-29, III) ; elle se
proratise par la durée requise, et ne dépasse pas 5 % du plafond annuel de la
sécurité sociale (D. 161-2-22-1), sauf pour les premières pensions de 2027,
dont la rédaction ne porte plus ce plafond — et qui ne la constituent qu'en
cumul entier, à l'âge du taux plein automatique. La reprise chez le dernier
employeur dans les six mois de la pension n'en ouvre jamais (L. 161-22-1,
2°). L'Agirc-Arrco attribue des points sur la tranche 1 des salaires perçus en
cumul intégral depuis le 1er janvier 2023, qui forment une seconde retraite
complémentaire, sans coefficient.

Le modèle calcule la nouvelle pension du régime général et des salariés
agricoles, et la seconde retraite de l'Agirc-Arrco, au mois qui suit la fin de
l'activité, et au 1er septembre 2023 au plus tôt. Les autres régimes de base —
libéraux, avocats, exploitants agricoles, fonctionnaires, régimes spéciaux —
ne la calculent pas encore, et le résultat les nomme.

Le jumeau de ce module est ``moteur/js/droit/seconde.js``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from . import departs as _departs
from . import liquider as _liquider
from .cumul import FONCTION_PUBLIQUE, Cumul, fonction_publique_quittee, jour

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..scenarios.actuel import ResultatActuel, ScenarioActuel

#: Ce que le droit fait d'un mois d'activité après le départ : il ouvre la
#: nouvelle pension ; il n'ouvre rien ; il n'ouvre rien parce que la reprise
#: chez le dernier employeur a suivi la pension de moins de six mois ; il ouvre
#: des droits dans les régimes qui n'ont pas liquidé — avant 2023 pour une
#: première pension d'avant 2015, toujours pour une pension militaire — ; il
#: n'en ouvre pas dans le régime qui sert déjà sa pension, définitive.
NOUVELLE_PENSION = "nouvelle_pension"
ETEINTS = "eteints"
DERNIER_EMPLOYEUR = "dernier_employeur"
REGIMES_NON_LIQUIDES = "regimes_non_liquides"
REGIME_LIQUIDE = "regime_liquide"
PENSION_MILITAIRE = "pension_militaire"

#: Les versions de la fiche ``droits_apres_la_premiere_pension``.
SANS_REGLE_GENERALE = "sans_regle_generale"
LOI_2014 = "loi_2014"
LOI_2023 = "loi_2023"
LFSS_2026 = "lfss_2026"

#: Les dates qui découpent la règle.
PREMIERE_2015 = DateMois(2015, 1)
DROITS_2023 = DateMois(2023, 1)
LIQUIDATION_2023 = DateMois(2023, 9)
PREMIERE_2027 = DateMois(2027, 1)

#: La nouvelle pension : le taux plein du régime général, le plafond en part du
#: plafond annuel de la sécurité sociale, et les heures de SMIC qui valident un
#: trimestre (R. 351-9).
TAUX_PLEIN = 0.5
PLAFOND_EN_PASS = 0.05
HEURES_PAR_TRIMESTRE = 150
#: Les régimes de base dont le modèle calcule la nouvelle pension.
REGIMES_CALCULES = frozenset({"regime_general", "msa_salaries"})
AGIRC_ARRCO = "agirc_arrco"


@dataclass(frozen=True)
class PeriodeDeDroits:
    """Des mois consécutifs d'activité que le droit traite de même."""

    debut: DateMois
    fin: DateMois
    #: :data:`NOUVELLE_PENSION`, :data:`ETEINTS`, :data:`DERNIER_EMPLOYEUR` ou
    #: :data:`REGIMES_NON_LIQUIDES`.
    motif: str
    #: La version de la fiche ``droits_apres_la_premiere_pension``.
    regle: str

    def donnees(self) -> dict:
        return {"debut": jour(self.debut), "fin": jour(self.fin), "motif": self.motif,
                "regle": self.regle}


@dataclass(frozen=True)
class NouvellePension:
    """La nouvelle pension d'un régime, ou la seconde retraite complémentaire."""

    regime: str
    date_effet: DateMois
    #: Les trimestres validés et le salaire mensuel moyen de la période, en
    #: euros de l'année de la date d'effet ; les points, pour l'Agirc-Arrco.
    trimestres: int
    salaire_mensuel: float
    points: float
    #: Par an, avant le plafond, le plafond, et le montant servi, en euros de
    #: l'année de la date d'effet.
    brute: float
    plafond: float | None
    montant: float

    def donnees(self) -> dict:
        return {"regime": self.regime, "date_effet": jour(self.date_effet),
                "trimestres": self.trimestres, "salaire_mensuel": self.salaire_mensuel,
                "points": self.points, "brute": self.brute, "plafond": self.plafond,
                "montant": self.montant}


@dataclass(frozen=True)
class DroitsApresDepart:
    """Ce que l'activité après le départ ouvre de droits, mois par mois, et
    les pensions nouvelles qu'elle constitue."""

    periodes: tuple[PeriodeDeDroits, ...]
    pensions: tuple[NouvellePension, ...]
    #: Les régimes de base de l'activité dont le modèle ne calcule pas la
    #: nouvelle pension.
    non_calcules: tuple[str, ...]

    @property
    def montant(self) -> float:
        return sum(p.montant for p in self.pensions)

    def donnees(self) -> dict:
        return {"periodes": [p.donnees() for p in self.periodes],
                "pensions": [p.donnees() for p in self.pensions],
                "non_calcules": list(self.non_calcules), "montant": self.montant}


def _motif(mois: DateMois, premiere: DateMois, integral: DateMois | None,
           six_mois: bool, militaire: bool, nouveaux: bool) -> tuple[str, str]:
    """Ce que le droit fait d'un mois d'activité, et la version qui le dit."""
    if militaire:
        # L. 84 du code des pensions retire au titulaire d'une pension
        # militaire L. 161-22-1 A, puis L. 161-22-1 : ses droits continuent.
        return PENSION_MILITAIRE, LOI_2014 if mois < DROITS_2023 else LOI_2023
    if mois < DROITS_2023:
        if premiere >= PREMIERE_2015:
            return ETEINTS, LOI_2014
        return (REGIMES_NON_LIQUIDES if nouveaux else REGIME_LIQUIDE), SANS_REGLE_GENERALE
    regle = LFSS_2026 if premiere >= PREMIERE_2027 else LOI_2023
    if six_mois:
        return DERNIER_EMPLOYEUR, regle
    if integral is not None and mois >= integral:
        return NOUVELLE_PENSION, regle
    return ETEINTS, regle


def droits(moteur: ScenarioActuel, carriere: Carriere, resultat: ResultatActuel,
           cumul: Cumul | None) -> DroitsApresDepart | None:
    """Les droits de l'activité que ``carriere`` exerce après son départ, ou
    ``None`` sans elle. ``cumul`` est ce que le cumul emploi-retraite en fait
    (:mod:`.cumul`) : son premier mois de cumul intégral ouvre la nouvelle
    pension."""
    if cumul is None or resultat is None:
        return None
    premiere = carriere.date_liquidation
    six_mois = (cumul.employeur == "dernier"
                and cumul.debut < premiere.plus_mois(6))
    # La première pension est-elle militaire ? Ses seules pensions de base
    # sont alors celles du code des pensions, et l'emploi quitté, militaire.
    bases = [p.regime for p in resultat.pensions_par_regime
             if moteur.catalogue[p.regime].etage in _departs.ETAGES_DES_UNITES]
    militaire = (fonction_publique_quittee(moteur, carriere)[0] and bool(bases)
                 and all(code in FONCTION_PUBLIQUE for code in bases))
    liquides = {p.regime for p in resultat.pensions_par_regime}

    def nouveaux(annee: int) -> bool:
        """L'activité de cette année relève-t-elle d'un régime de base qui n'a
        pas liquidé ?"""
        return any(code not in liquides
                   for code in moteur.affiliations.regimes(cumul.affiliation, annee)
                   if moteur.catalogue[code].etage in _departs.ETAGES_DES_UNITES)
    periodes: list[PeriodeDeDroits] = []
    ouverts: list[DateMois] = []
    for rang in range(cumul.debut.rang, cumul.fin.rang):
        mois = DateMois.depuis_rang(rang)
        motif, regle = _motif(mois, premiere, cumul.integral_depuis, six_mois, militaire,
                              nouveaux(mois.annee))
        if motif == NOUVELLE_PENSION:
            ouverts.append(mois)
        derniere = periodes[-1] if periodes else None
        if derniere is not None and (derniere.motif, derniere.regle) == (motif, regle):
            periodes[-1] = PeriodeDeDroits(derniere.debut, mois.plus_mois(1), motif, regle)
        else:
            periodes.append(PeriodeDeDroits(mois, mois.plus_mois(1), motif, regle))
    pensions: list[NouvellePension] = []
    non_calcules: set[str] = set()
    if ouverts:
        date_effet = max(cumul.fin, LIQUIDATION_2023)
        revenus: dict[int, float] = {}
        for ligne in carriere.lignes_apres_depart:
            revenus[ligne.annee] = revenus.get(ligne.annee, 0.0) + ligne.revenu
        activite: dict[int, int] = {}
        for rang in range(cumul.debut.rang, cumul.fin.rang):
            annee = DateMois.depuis_rang(rang).annee
            activite[annee] = activite.get(annee, 0) + 1
        periode: dict[int, int] = {}
        for mois in ouverts:
            periode[mois.annee] = periode.get(mois.annee, 0) + 1
        # Le salaire de chaque année, sur ses seuls mois de la période.
        salaires = {annee: revenus.get(annee, 0.0) / activite[annee] * mois
                    for annee, mois in sorted(periode.items())}
        regimes = set()
        for annee in periode:
            regimes |= set(moteur.affiliations.regimes(cumul.affiliation, annee))
        bases = {code for code in regimes
                 if moteur.catalogue[code].etage in _departs.ETAGES_DES_UNITES}
        for code in sorted(bases):
            if code not in REGIMES_CALCULES:
                non_calcules.add(code)
                continue
            pension = _nouvelle_pension(moteur, code, salaires, periode, date_effet,
                                        resultat.trimestres_requis,
                                        premiere < PREMIERE_2027)
            if pension is not None:
                pensions.append(pension)
        if AGIRC_ARRCO in regimes:
            pension = _seconde_retraite_complementaire(moteur, salaires, periode,
                                                       date_effet)
            if pension is not None:
                pensions.append(pension)
    return DroitsApresDepart(periodes=tuple(periodes), pensions=tuple(pensions),
                             non_calcules=tuple(sorted(non_calcules)))


def _nouvelle_pension(moteur: ScenarioActuel, code: str, salaires: dict[int, float],
                      periode: dict[int, int], date_effet: DateMois, requis: int,
                      plafonnee: bool) -> NouvellePension | None:
    """La nouvelle pension d'un régime aligné : le salaire mensuel moyen des
    années qui valident un trimestre (R. 351-29, III), revalorisé et écrêté au
    plafond, au taux plein, proratisé par la durée requise."""
    macro = moteur.macro
    trimestres = 0
    total = 0.0
    mois = 0
    for annee, salaire in salaires.items():
        valides = min(4, math.floor(
            salaire / (HEURES_PAR_TRIMESTRE * macro.smic_horaire(annee)) + 1e-9))
        if valides < 1:
            continue
        trimestres += valides
        plafonne = min(salaire, macro.plafond_securite_sociale(annee) * periode[annee] / 12.0)
        total += plafonne * macro.coefficient_revalorisation_portee_au_compte(
            annee, date_effet.annee, date_effet.mois)
        mois += periode[annee]
    if trimestres == 0 or mois == 0 or requis <= 0:
        return None
    salaire_mensuel = total / mois
    brute = salaire_mensuel * 12.0 * TAUX_PLEIN * min(1.0, trimestres / requis)
    plafond = (PLAFOND_EN_PASS * macro.plafond_securite_sociale(date_effet.annee)
               if plafonnee else None)
    montant = brute if plafond is None else min(brute, plafond)
    return NouvellePension(regime=code, date_effet=date_effet, trimestres=trimestres,
                           salaire_mensuel=salaire_mensuel, points=0.0, brute=brute,
                           plafond=plafond, montant=montant)


def _prix_du_point(moteur: ScenarioActuel, annee: int) -> tuple[float, float] | None:
    """Le prix d'achat d'un point de l'Agirc-Arrco : le salaire de référence et
    le taux d'appel de l'année ; au-delà du dernier publié, le salaire de
    référence suit le plafond de la sécurité sociale."""
    connu = annee
    while connu >= 2019:
        achat = moteur.valeurs_point.achat(AGIRC_ARRCO, connu)
        if achat is not None:
            reference, taux_appel, _ = achat
            macro = moteur.macro
            return (reference * macro.plafond_securite_sociale(annee)
                    / macro.plafond_securite_sociale(connu), taux_appel)
        connu -= 1
    return None


def _seconde_retraite_complementaire(moteur: ScenarioActuel, salaires: dict[int, float],
                                     periode: dict[int, int],
                                     date_effet: DateMois) -> NouvellePension | None:
    """Les points de la tranche 1 acquis en cumul intégral depuis 2023, et la
    seconde retraite qu'ils servent, sans coefficient."""
    macro = moteur.macro
    points = 0.0
    for annee, salaire in salaires.items():
        plafond = macro.plafond_securite_sociale(annee)
        tranche_1 = next(
            (p for p in moteur.catalogue[AGIRC_ARRCO].periodes_actives(annee)
             if p.bornes_assiette_en_euros(plafond)[0] == 0), None)
        prix = _prix_du_point(moteur, annee)
        if tranche_1 is None or prix is None:
            continue
        reference, taux_appel = prix
        assiette = min(salaire, plafond * periode[annee] / 12.0)
        points += assiette * tranche_1.taux_cotisation_retraite / (taux_appel * reference)
    valeur = _liquider.valeur_du_point(moteur, AGIRC_ARRCO, date_effet.annee)
    if points <= 0 or valeur is None:
        return None
    montant = points * valeur[0]
    return NouvellePension(regime=AGIRC_ARRCO, date_effet=date_effet, trimestres=0,
                           salaire_mensuel=0.0, points=points, brute=montant,
                           plafond=None, montant=montant)
