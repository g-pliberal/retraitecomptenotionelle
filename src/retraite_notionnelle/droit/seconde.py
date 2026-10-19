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
un trimestre, sur les mois d'assurance de la période (R. 351-29, III) ; celui
de l'indépendant, le revenu annuel moyen de ces années, l'année de l'effet
comprise (R. 634-1 jusqu'en 2025, D. 634-3 depuis), sur ce que ses cotisations
ont porté, l'assiette minimale de l'artisan et du commerçant comprise
(D. 633-2) ; elle se
proratise par la durée requise, et ne dépasse pas 5 % du plafond annuel de la
sécurité sociale (D. 161-2-22-1), sauf pour les premières pensions de 2027,
dont la rédaction ne porte plus ce plafond — et qui ne la constituent qu'en
cumul entier, à l'âge du taux plein automatique. La reprise chez le dernier
employeur dans les six mois de la pension n'en ouvre jamais (L. 161-22-1,
2°). L'Agirc-Arrco attribue des points sur la tranche 1 des salaires perçus en
cumul intégral depuis le 1er janvier 2023, qui forment une seconde retraite
complémentaire, sans coefficient ; le RCI, sur les périodes de cumul intégral
courant depuis le 1er janvier 2025 (règlement du régime, articles 4 et 27).

Le modèle calcule la nouvelle pension du régime général et des salariés
agricoles, et les secondes retraites de l'Agirc-Arrco et du RCI, au mois qui
suit la fin de l'activité, et au 1er septembre 2023 au plus tôt. Les autres
régimes de base — libéraux, avocats, exploitants agricoles, fonctionnaires,
régimes spéciaux — ne la calculent pas encore, et le résultat les nomme.

Les droits qu'ouvrent les années d'activité dans un régime qui ne sert pas de
pension — avant 2023 pour une première pension d'avant 2015, toujours pour
une pension militaire — se liquident comme toute pension, à la demande
présumée à la fin de l'activité, ou à l'âge d'ouverture du régime s'il vient
après (présomption ``depart_de_chaque_regime``) : sur la carrière prolongée de
ces années, dont la durée tous régimes fait le taux
(:func:`liquider_les_regimes_nouveaux`). Le régime qui sert déjà une pension ne
la révise pas : elle est définitive.

Le jumeau de ce module est ``moteur/js/droit/seconde.js``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from ..carriere import revenu_cotise
from ..donnees.chargement import charger_cotisation_micro, forfait_micro
from . import acquerir as _acquerir
from . import departs as _departs
from . import liquider as _liquider
from .commun import date_d_effet
from .cumul import FONCTION_PUBLIQUE, Cumul, fonction_publique_quittee, jour
from ..somme import somme_ordonnee

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..scenarios.actuel import ResultatActuel, ScenarioActuel
    from .liquidation import Contexte, Liquidation

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
#: La seconde retraite de l'Agirc-Arrco « prend effet, au plus tôt, le 1er
#: janvier 2024 » (accord du 17 novembre 2017, article 91, rédaction de
#: l'avenant n° 16 ; circulaire 2024-04-DRJ).
LIQUIDATION_AGIRC_ARRCO = DateMois(2024, 1)
#: Le RCI n'ouvre de droits au retraité en cumul intégral que depuis le 1er
#: janvier 2025 : son règlement les ouvre par l'article 27, dans la rédaction
#: de l'arrêté du 19 juin 2024, dont l'article 2 met ces alinéas en vigueur à
#: cette date ; avant, ses cotisations « ne sont pas productives de droits »
#: (article 4).
DROITS_RCI = DateMois(2025, 1)
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
RCI = "rci"
#: Le groupe de l'activité des artisans, des commerçants et des
#: micro-entrepreneurs (:func:`.cumul.groupe_de_l_activite`).
INDEPENDANTS = "independants"


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
    #: Les trimestres validés et le salaire mensuel moyen de la période — le
    #: revenu annuel moyen, pour l'indépendant —, en euros de l'année de la
    #: date d'effet ; les points, pour l'Agirc-Arrco.
    trimestres: int
    salaire_mensuel: float
    points: float
    #: Par an, avant le plafond, le plafond, et le montant servi, en euros de
    #: l'année de la date d'effet.
    brute: float
    plafond: float | None
    montant: float
    revenu_annuel_moyen: float = 0.0

    def donnees(self) -> dict:
        return {"regime": self.regime, "date_effet": jour(self.date_effet),
                "trimestres": self.trimestres, "salaire_mensuel": self.salaire_mensuel,
                "revenu_annuel_moyen": self.revenu_annuel_moyen,
                "points": self.points, "brute": self.brute, "plafond": self.plafond,
                "montant": self.montant}


@dataclass(frozen=True)
class PensionDeRegimeNouveau:
    """La pension d'un régime que l'activité après le départ ouvre, liquidée à
    sa date : par an, en euros de cette date."""

    regime: str
    date_effet: DateMois
    montant: float
    detail: str

    def donnees(self) -> dict:
        return {"regime": self.regime, "date_effet": jour(self.date_effet),
                "montant": self.montant, "detail": self.detail}


@dataclass(frozen=True)
class DroitsApresDepart:
    """Ce que l'activité après le départ ouvre de droits, mois par mois, et
    les pensions nouvelles qu'elle constitue."""

    periodes: tuple[PeriodeDeDroits, ...]
    pensions: tuple[NouvellePension, ...]
    #: Les régimes de base de l'activité dont le modèle ne calcule pas la
    #: nouvelle pension.
    non_calcules: tuple[str, ...]
    #: Les pensions des régimes qui n'en servaient pas, que l'activité ouvre
    #: (:func:`liquider_les_regimes_nouveaux`).
    regimes_nouveaux: tuple[PensionDeRegimeNouveau, ...] = ()

    @property
    def montant(self) -> float:
        return somme_ordonnee(p.montant for p in self.pensions)

    def donnees(self) -> dict:
        return {"periodes": [p.donnees() for p in self.periodes],
                "pensions": [p.donnees() for p in self.pensions],
                "non_calcules": list(self.non_calcules), "montant": self.montant,
                "regimes_nouveaux": [p.donnees() for p in self.regimes_nouveaux]}


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
        lignes = carriere.lignes_apres_depart
        activite: dict[int, int] = {}
        for rang in range(cumul.debut.rang, cumul.fin.rang):
            annee = DateMois.depuis_rang(rang).annee
            activite[annee] = activite.get(annee, 0) + 1
        periode: dict[int, int] = {}
        for mois in ouverts:
            periode[mois.annee] = periode.get(mois.annee, 0) + 1

        def salaires(code: str | None = None) -> dict[int, float]:
            """Le salaire de chaque année, sur ses seuls mois de la période :
            celui que ``code`` cotise (:func:`_revenus`)."""
            revenus = _revenus(moteur, lignes, code)
            return {annee: revenus.get(annee, 0.0) / activite[annee] * mois
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
            pension = _nouvelle_pension(moteur, code, salaires(code), periode, date_effet,
                                        resultat.trimestres_requis,
                                        premiere < PREMIERE_2027,
                                        annuel=cumul.groupe == INDEPENDANTS)
            if pension is not None:
                pensions.append(pension)
        if AGIRC_ARRCO in regimes:
            pension = _seconde_retraite_complementaire(
                moteur, salaires(), periode, max(date_effet, LIQUIDATION_AGIRC_ARRCO))
            if pension is not None:
                pensions.append(pension)
        if RCI in regimes:
            pension = _seconde_retraite_rci(moteur, lignes, activite, periode,
                                            max(date_effet, DROITS_RCI))
            if pension is not None:
                pensions.append(pension)
    return DroitsApresDepart(periodes=tuple(periodes), pensions=tuple(pensions),
                             non_calcules=tuple(sorted(non_calcules)))


def _revenus(moteur: ScenarioActuel, lignes, code: str | None = None) -> dict[int, float]:
    """Le revenu de chaque année de l'activité, que la ligne déclare ; celui du
    micro-entrepreneur, que son forfait cotise, et non son revenu abattu : celui
    de ses trimestres et de son revenu annuel moyen (:func:`revenu_cotise`).

    Avec ``code``, celui sur lequel ce régime de base a cotisé : l'artisan ou le
    commerçant qui déclare peu cotise sur l'assiette minimale (D. 633-2), dont
    rien ne dispense le pensionné, et sa nouvelle pension « correspond aux
    cotisations versées » (R. 634-1 ; R. 351-29, I, B, par D. 634-3) : en 2024,
    450 SMIC horaires, 5 242,50 €, qui valident trois trimestres là où 2 000 €
    déclarés en valident un (:func:`.acquerir.assiette_minimale`)."""
    revenus: dict[int, float] = {}
    for ligne in lignes:
        if ligne.micro:
            revenu = revenu_cotise(moteur.macro, ligne.revenu, ligne.micro, ligne.annee,
                                   ligne.fraction_annee)
        elif code is None:
            revenu = ligne.revenu
        else:
            revenu = max(ligne.revenu, _acquerir.assiette_minimale(moteur, (code,), ligne))
        revenus[ligne.annee] = revenus.get(ligne.annee, 0.0) + revenu
    return revenus


def _nouvelle_pension(moteur: ScenarioActuel, code: str, salaires: dict[int, float],
                      periode: dict[int, int], date_effet: DateMois, requis: int,
                      plafonnee: bool, annuel: bool = False) -> NouvellePension | None:
    """La nouvelle pension d'un régime aligné : le salaire mensuel moyen des
    années qui valident un trimestre (R. 351-29, III), revalorisé et écrêté au
    plafond, au taux plein, proratisé par la durée requise.

    ``annuel`` : celle de l'indépendant, sur le revenu annuel moyen de ces
    années. De 2023 à 2025, D. 634-1 écarte R. 351-29, et R. 634-1 fait la
    moyenne des revenus cotisés des années civiles qui valident un trimestre :
    « il est tenu compte du revenu annuel de l'année durant laquelle la pension
    mentionnée à l'article L. 161-22-1-1 prend effet ». Depuis 2026, D. 634-3
    applique R. 351-29, mais « Les III et IV ne sont pas applicables », et
    l'année de l'entrée en jouissance y reste (5°). Une année entamée y pèse
    de ses seuls mois, comme une année entière : les trente mois d'un cumul de
    février 2023 à juillet 2025, sur trois années civiles, font une moyenne de
    dix fois le salaire mensuel, et non de douze. La période ne passe pas
    vingt-cinq années avant 2048 : toutes entrent dans la moyenne."""
    macro = moteur.macro
    trimestres = 0
    total = 0.0
    mois = 0
    annees = 0
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
        annees += 1
    if trimestres == 0 or mois == 0 or requis <= 0:
        return None
    salaire_mensuel = 0.0 if annuel else total / mois
    revenu_annuel_moyen = total / annees if annuel else 0.0
    base = revenu_annuel_moyen if annuel else salaire_mensuel * 12.0
    brute = base * TAUX_PLEIN * min(1.0, trimestres / requis)
    plafond = (PLAFOND_EN_PASS * macro.plafond_securite_sociale(date_effet.annee)
               if plafonnee else None)
    montant = brute if plafond is None else min(brute, plafond)
    return NouvellePension(regime=code, date_effet=date_effet, trimestres=trimestres,
                           salaire_mensuel=salaire_mensuel, points=0.0, brute=brute,
                           plafond=plafond, montant=montant,
                           revenu_annuel_moyen=revenu_annuel_moyen)


def _prix_du_point(moteur: ScenarioActuel, annee: int) -> tuple[float, float] | None:
    """Le prix d'achat d'un point de l'Agirc-Arrco : le salaire de référence et
    le taux d'appel de l'année ; au-delà du dernier publié, celui que le texte
    prolonge sur le salaire moyen, comme pour la première pension
    (`ValeursPoint.achat_prolonge`). Le salaire de référence suivait ici le
    plafond de la sécurité sociale, qui suit lui-même le salaire moyen au-delà
    du dernier publié : les mêmes valeurs, à l'arrondi près, par une seconde
    règle."""
    achat = moteur.valeurs_point.achat_prolonge(AGIRC_ARRCO, annee, moteur.macro)
    if achat is None:
        return None
    reference, taux_appel, _ = achat
    return reference, taux_appel


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
             if p.bornes_assiette_en_euros(plafond, annee)[0] == 0), None)
        prix = _prix_du_point(moteur, annee)
        if tranche_1 is None or prix is None:
            continue
        reference, taux_appel = prix
        assiette = min(salaire, plafond * periode[annee] / 12.0)
        # Au taux de calcul des points, 6,20 %, comme la première pension
        # (`PeriodeRegime.taux_calcul_points`), et non à la cotisation appelée
        # divisée par le taux d'appel.
        points += (assiette * tranche_1.taux_calcul_points / reference
                   if tranche_1.taux_calcul_points is not None
                   else assiette * tranche_1.taux_cotisation_retraite / (taux_appel * reference))
    valeur = _liquider.valeur_du_point(moteur, AGIRC_ARRCO, date_effet)
    if points <= 0 or valeur is None:
        return None
    montant = points * valeur[0]
    return NouvellePension(regime=AGIRC_ARRCO, date_effet=date_effet, trimestres=0,
                           salaire_mensuel=0.0, points=points, brute=montant,
                           plafond=None, montant=montant)


def _seconde_retraite_rci(moteur: ScenarioActuel, lignes, activite: dict[int, int],
                          periode: dict[int, int],
                          date_effet: DateMois) -> NouvellePension | None:
    """La seconde retraite du RCI : les points que les cotisations des mois de
    cumul intégral achètent depuis le 1er janvier 2025 (:data:`DROITS_RCI`),
    servis sans coefficient.

    « Lorsque les conditions mentionnées aux alinéas 3 à 6 de l'article
    L. 634-6 du code de la sécurité sociale sont réunies, l'assuré se constitue
    de nouveaux droits à pension au titre du présent régime », et « La seconde
    pension de vieillesse est calculée, liquidée et servie dans les conditions
    applicables à la pension de vieillesse du présent régime », demandée « en
    même temps que celle du régime de base » (règlement du RCI, article 27) :
    à la date de la nouvelle pension de base, au taux plein, donc entière. Ses
    points sont ceux de la première pension (:func:`.acquerir.acquerir`) : le
    revenu déclaré, sans l'assiette minimale, que le RCI n'a pas, au taux de
    chaque tranche sur ses bornes réduites aux mois de la période (D. 635-7) ;
    pour le micro-entrepreneur, la part complémentaire de son forfait
    (D. 613-6) ; au prix d'achat de l'année."""
    macro = moteur.macro
    table = charger_cotisation_micro(macro.racine)
    points = 0.0
    for ligne in lignes:
        annee = ligne.annee
        if annee < DROITS_RCI.annee or annee not in periode:
            continue
        achat = moteur.valeurs_point.achat_prolonge(RCI, annee, macro)
        if achat is None:
            continue
        reference, taux_appel, _ = achat
        # La part de l'année que la période garde, et le revenu de ses mois.
        part = periode[annee] / activite[annee]
        forfait = forfait_micro(table, ligne.micro, annee) if ligne.micro else None
        if forfait is not None:
            (_, complementaire), (_, taux_complementaire, _) = forfait
            cotisation = (ligne.revenu * taux_complementaire * part
                          if complementaire == RCI else 0.0)
        else:
            plafond = macro.plafond_securite_sociale(annee)
            fraction = periode[annee] / 12.0
            revenu = ligne.revenu * part
            cotisation = 0.0
            for tranche in moteur.catalogue[RCI].periodes_actives(annee):
                basse, haute = tranche.bornes_assiette_en_euros(plafond, annee)
                plafonne = revenu if haute is None else min(revenu, haute * fraction)
                cotisation += (max(0.0, plafonne - basse * fraction)
                               * tranche.taux_cotisation_retraite)
        points += cotisation / (taux_appel * reference)
    valeur = _liquider.valeur_du_point(moteur, RCI, date_effet)
    if points <= 0 or valeur is None:
        return None
    montant = points * valeur[0]
    return NouvellePension(regime=RCI, date_effet=date_effet, trimestres=0,
                           salaire_mensuel=0.0, points=points, brute=montant,
                           plafond=None, montant=montant)


#: Ce qui ouvre des droits dans les régimes qui ne servent pas de pension.
OUVRANTS = frozenset({REGIMES_NON_LIQUIDES, PENSION_MILITAIRE})


def liquider_les_regimes_nouveaux(moteur: ScenarioActuel, carriere: Carriere,
                                  resultat: ResultatActuel, droits: DroitsApresDepart | None,
                                  cumul: Cumul | None, contexte: Contexte,
                                  journal: object | None = None
                                  ) -> tuple[tuple[DateMois, Liquidation], ...]:
    """Les pensions que les années d'activité ouvrent dans les régimes qui n'en
    servent pas encore, liquidées à leur date : chaque départ, et sa
    liquidation.

    La carrière se prolonge des seules années dont les mois ouvrent des droits
    (:data:`OUVRANTS`) ; elle se liquide à la fin de l'activité, et chaque
    régime nouveau à cette date, ou à son âge d'ouverture s'il vient après
    (:func:`~.departs.departs`). La liquidation voit servies les pensions du
    départ, menées au mois de sa date d'effet.
    """
    from ..revalorisation import mener_au_mois
    from . import liquidation as _liquidation

    if droits is None or cumul is None:
        return ()
    annees = {DateMois.depuis_rang(rang).annee
              for periode in droits.periodes if periode.motif in OUVRANTS
              for rang in range(periode.debut.rang, periode.fin.rang)}
    lignes = [ligne for ligne in carriere.lignes_apres_depart if ligne.annee in annees]
    if not lignes:
        return ()
    etendue = carriere.avec_lignes(
        sorted([*carriere.lignes, *lignes], key=lambda ligne: ligne.annee)
    ).liquidee_au(cumul.fin)
    liquides = {p.regime for p in resultat.pensions_par_regime}
    bases, suivies = _departs.regimes_de_la_carriere(moteur, etendue)
    nouveaux = (set(bases) | set(suivies)) - liquides
    if not nouveaux:
        return ()
    par_date: dict[DateMois, set[str]] = {}
    for depart in _departs.departs(moteur, etendue):
        ici = nouveaux if depart.unique else set(depart.regimes) & nouveaux
        if ici:
            par_date.setdefault(depart.date, set()).update(ici)
    liquidations = []
    for date in sorted(par_date):
        servies = tuple(
            _departs.PensionServie(pension.regime, montant,
                                   pension.date_effet or date_d_effet(carriere))
            for pension, montant in zip(resultat.pensions_par_regime, mener_au_mois(
                moteur, resultat.pensions_par_regime, carriere.date_liquidation, date)))
        demande = _liquidation.Demande(
            personne=carriere.personne, date_effet=jour(date), date_evenement=jour(date),
            regimes=tuple(sorted(par_date[date])))
        etat = _liquidation.Etat(etendue.liquidee_au(date), journal, servies)
        liquidations.append((date, _liquidation.liquider(demande, etat, contexte)))
    return tuple(liquidations)
