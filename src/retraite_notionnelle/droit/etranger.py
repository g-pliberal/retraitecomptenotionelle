"""Les carrières hors de France (docs/architecture.md, § 11) : ce que les
étapes du droit lisent des fiches du domaine et du tableau des accords, que
:class:`~retraite_notionnelle.scenarios.actuel.CarrieresHorsDeFrance` prépare.

* ``totalisation_des_periodes_etrangeres`` : les périodes passées hors de
  France comptent dans la durée qui fixe le taux et ouvre les droits, jamais
  dans celle qui proratise. « Coordonner les affiliations » dit, période par
  période, à quel titre — l'accord en vigueur avec l'État à la date d'effet de
  la pension, une organisation internationale, l'équivalence de l'activité
  d'avant 1983, ou aucun — et pour quels régimes (:func:`coordonner_les_periodes`) ;
  « compter les durées » en fait des trimestres, année par année, sans dépasser
  quatre avec ceux que la carrière valide en France (:func:`compter_les_periodes`).

Deux familles de régimes lisent ces trimestres, chacune les siens : le régime
général et les régimes que la fiche coordonne avec lui, qui retiennent tout
accord ; les trois régimes du code des pensions, que seuls les règlements
européens coordonnent, depuis le 25 octobre 1998, et l'organisation
internationale. Un régime d'aucune des deux n'en retient aucun.

Son jumeau est ``moteur/js/droit/etranger.js``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING

from ..calendrier import MOIS_PAR_AN, DateMois, mois_travailles, trimestres_civils
from .commun import date_d_effet

if TYPE_CHECKING:
    from ..carriere import Carriere, PensionEtrangere, PeriodeALEtranger
    from ..scenarios.actuel import ScenarioActuel

#: Les deux familles de régimes qui lisent les trimestres étrangers : le
#: régime général, et ceux que la fiche coordonne avec lui ; les régimes du
#: code des pensions.
GENERALE, FONCTIONNAIRES = "regime_general", "fonction_publique"
FAMILLES = (GENERALE, FONCTIONNAIRES)

#: Les titres auxquels une période étrangère compte, dans l'ordre où ses
#: trimestres entrent sous le plafond de l'année : ceux d'un accord d'abord,
#: les seuls qui comptent aussi comme cotisés.
ACCORD, ORGANISATION, EQUIVALENCE = "accord", "organisation_internationale", "equivalence"
TITRES = (ACCORD, ORGANISATION, EQUIVALENCE)

#: Les instruments d'un accord qui totalise les périodes (tableau des accords).
INSTRUMENTS_QUI_TOTALISENT = frozenset({
    "reglements_europeens", "accord_de_commerce_et_de_cooperation", "convention"})
#: L'instrument propre à un État : une convention bilatérale.
CONVENTION = "convention"
#: Celui qui, seul, coordonne aussi les régimes des fonctionnaires.
REGLEMENTS_EUROPEENS = "reglements_europeens"
#: Les personnes qu'une convention ne vise qu'à moitié : les seuls salariés.
SALARIES = "salaries"
SALARIEE = "salariee"
#: Le code d'une organisation internationale au tableau des accords.
ORGANISATION_INTERNATIONALE = "OI"
#: Le calcul des règlements européens qui compare la pension nationale à la
#: pension proratisée (paramètre ``reglements_europeens`` de la fiche
#: ``pension_proratisee``), et ceux d'un accord bilatéral qui la comparent ou
#: laissent l'assuré choisir la plus élevée (``calcul`` au tableau des accords).
COMPARAISON = "comparaison"
CALCULS_COMPARES = frozenset({COMPARAISON, "option"})


@dataclass(frozen=True)
class PeriodeCoordonnee:
    """Une période passée hors de France, et ce que la coordination en fait."""

    periode: PeriodeALEtranger
    #: Le titre auquel elle compte (:data:`TITRES`), ou ``None``.
    titre: str | None
    #: L'instrument de l'accord qui la fait compter — celui d'une
    #: organisation internationale pour elle —, ``None`` sans accord.
    instrument: str | None
    #: Les familles de régimes qui la retiennent (:data:`FAMILLES`).
    familles: tuple[str, ...]
    #: La version de la fiche ``totalisation_des_periodes_etrangeres``, et
    #: ses paramètres.
    version: str | None
    parametres: dict = field(default_factory=dict, compare=False, repr=False)
    #: L'accord compare-t-il la pension nationale, qui ignore la période, à
    #: la pension proratisée, qui la compte (fiche ``pension_proratisee``) ?
    comparee: bool = False
    #: Les États tiers dont la convention qui la fait compter totalise aussi
    #: les périodes (tableau des accords) ; aucun pour un autre instrument.
    etats_tiers: tuple[str, ...] = field(default=(), compare=False, repr=False)
    #: L'année d'où ses trimestres réduisent, avec la durée des régimes
    #: alignés, les années du salaire annuel moyen de la pension proratisée :
    #: ceux d'un régime que la Cnav tient pour « équivalant au régime
    #: général » (:func:`_salaire_moyen_depuis`) ; ``None`` pour une autre.
    salaire_moyen_depuis: int | None = None

    def donnees(self) -> dict:
        periode = self.periode
        return {"pays": periode.pays, "debut": _jour(periode.debut),
                "fin": _jour(periode.fin), "activite": periode.activite,
                "titre": self.titre, "instrument": self.instrument,
                "familles": list(self.familles), "version": self.version,
                "comparee": self.comparee,
                "salaire_moyen_depuis": self.salaire_moyen_depuis}


def _jour(mois: DateMois) -> str:
    return f"{mois.annee:04d}-{mois.mois:02d}-01"


def coordonner_les_periodes(moteur: ScenarioActuel,
                            carriere: Carriere) -> tuple[PeriodeCoordonnee, ...]:
    """Chaque période hors de France, et le titre auquel elle compte pour une
    pension qui prend effet à la date de la carrière : l'accord que le tableau
    donne alors à son État, s'il vise l'activité de la période — une
    convention ne vise souvent que les salariés — ; l'organisation
    internationale depuis 2010 ; l'équivalence de l'activité d'avant le
    1er avril 1983 sinon (R. 351-4, 1°), qu'un accord ne fait pas déjà
    compter. Avant le 1er avril 1983, aucun : le taux se lit sur l'âge."""
    effet = date_d_effet(carriere)
    if effet is None or not carriere.periodes_a_l_etranger:
        return ()
    domaine = moteur.carrieres_hors_de_france
    proratisation = domaine.version("proratisation", {
        "liquidation.date_effet": effet,
        "assure.generation": f"{carriere.annee_naissance:04d}-01-01"})
    reglements_compares = (proratisation is not None and proratisation["parametres"].get(
        "reglements_europeens") == COMPARAISON)
    coordonnees = []
    for periode in carriere.periodes_a_l_etranger:
        version = domaine.version("totalisation", {
            "liquidation.date_effet": effet, "periode.debut": _jour(periode.debut),
            "periode.fin": _jour(periode.fin)})
        parametres = {} if version is None else version["parametres"]
        accord = domaine.accord(periode.pays, effet)
        titre, instrument, familles = None, None, ()
        if not parametres.get("compte_pour_le_taux"):
            pass
        elif periode.pays == ORGANISATION_INTERNATIONALE:
            if accord is not None and parametres.get("organisations_internationales"):
                titre, instrument, familles = ORGANISATION, accord["instrument"], FAMILLES
        elif (accord is not None and accord["instrument"] in INSTRUMENTS_QUI_TOTALISENT
              and (accord.get("personnes") != SALARIES or periode.activite == SALARIEE)):
            titre, instrument = ACCORD, accord["instrument"]
            fonctionnaires = parametres.get("fonctionnaires_depuis")
            familles = ((GENERALE, FONCTIONNAIRES)
                        if instrument == REGLEMENTS_EUROPEENS and fonctionnaires is not None
                        and effet >= fonctionnaires else (GENERALE,))
        elif (parametres.get("equivalentes_avant") is not None
              and _jour(periode.debut) < parametres["equivalentes_avant"]):
            titre, familles = EQUIVALENCE, (GENERALE,)
        comparee = titre == ACCORD and (
            reglements_compares if instrument == REGLEMENTS_EUROPEENS
            else accord.get("calcul") in CALCULS_COMPARES)
        coordonnees.append(PeriodeCoordonnee(
            periode=periode, titre=titre, instrument=instrument, familles=familles,
            version=None if version is None else version["id"], parametres=parametres,
            comparee=comparee,
            etats_tiers=tuple(accord.get("etats_tiers") or ()) if titre == ACCORD else (),
            salaire_moyen_depuis=(_salaire_moyen_depuis(domaine, periode, effet)
                                  if comparee and instrument == REGLEMENTS_EUROPEENS
                                  else None)))
    return tuple(coordonnees)


def _salaire_moyen_depuis(domaine, periode: PeriodeALEtranger, effet: str) -> int | None:
    """L'année d'où les trimestres d'une période que les règlements européens
    totalisent comptent, avec la durée des régimes alignés, pour réduire les
    années du salaire annuel moyen de la pension proratisée : celle de son
    début, ou celle d'où le régime de son État est « équivalent » ; ``None``
    quand il ne l'est pas pour son activité, ou pas encore à la date d'effet
    de la pension. Le régime « équivalant au régime général et aux régimes
    alignés » calcule sa pension sur les salaires, les revenus ou les
    cotisations d'au moins quinze ans (circulaire ministérielle du 3 juillet
    2008) ; le tableau des accords dit, État par État, les activités dont la
    Cnav l'a reconnu (``salaire_moyen`` ; circulaires Cnav n° 2012/26 et
    2013/56). Le modèle présume la période accomplie au régime des salariés ou
    des non-salariés de l'État, jamais à celui de ses fonctionnaires, que le
    tableau exclut presque partout."""
    equivalence = (domaine.accords.get(periode.pays) or {}).get("salaire_moyen")
    if (equivalence is None or periode.activite not in equivalence["activites"]
            or effet < (equivalence.get("pensions_depuis") or "")):
        return None
    depuis = equivalence.get("periodes_depuis")
    return periode.debut.annee if depuis is None else max(periode.debut.annee,
                                                           int(depuis[:4]))


@dataclass(frozen=True)
class TrimestresEtrangers:
    """Ce que les périodes hors de France apportent aux durées, famille par
    famille de régimes et année par année, le plafond de l'année fait."""

    #: Par famille, par année : les trimestres que la durée du taux retient.
    pour_le_taux: dict[str, dict[int, int]]
    #: Par famille, par année : ceux d'entre eux qui comptent comme cotisés,
    #: ceux d'un accord — la carrière longue, la surcote, la majoration du
    #: minimum contributif les lisent.
    cotises: dict[str, dict[int, int]]
    #: Les périodes, et ce que la coordination en a fait.
    periodes: tuple[PeriodeCoordonnee, ...]
    #: La famille des régimes de la carrière (:func:`famille_des_regimes`) :
    #: celle dont la durée tous régimes du résultat se lit.
    famille: str = GENERALE
    #: Par famille, par année : les trimestres que la durée du taux de la
    #: pension NATIONALE retient, sans ceux des périodes qu'un accord compare
    #: (:attr:`PeriodeCoordonnee.comparee`).
    nationaux: dict[str, dict[int, int]] = field(default_factory=dict)
    #: Par famille, par année : ceux que la durée du taux retient des régimes
    #: étrangers « équivalant au régime général »
    #: (:attr:`PeriodeCoordonnee.salaire_moyen_depuis`), qui réduisent avec la
    #: durée des régimes alignés les années du salaire annuel moyen de la
    #: pension proratisée (fiche ``pension_proratisee``).
    au_salaire_moyen: dict[str, dict[int, int]] = field(default_factory=dict)

    def trimestres(self, famille: str | None, nationale: bool = False) -> int:
        """Les trimestres que la durée du taux de cette famille retient — de
        sa pension nationale, avec ``nationale``."""
        table = self.nationaux if nationale else self.pour_le_taux
        return sum((table.get(famille) or {}).values())

    def compare(self, famille: str | None) -> bool:
        """Un accord compare-t-il, pour cette famille, une pension nationale
        à la pension proratisée ?"""
        return self.trimestres(famille) != self.trimestres(famille, nationale=True)

    def trimestres_cotises(self, famille: str | None) -> int:
        """Ceux d'entre eux qui comptent comme cotisés."""
        return sum((self.cotises.get(famille) or {}).values())

    def trimestres_au_salaire_moyen(self, famille: str | None) -> int:
        """Ceux d'entre eux qui réduisent les années du salaire annuel moyen
        de la pension proratisée."""
        return sum((self.au_salaire_moyen.get(famille) or {}).values())

    def donnees(self) -> dict:
        return {
            "famille": self.famille,
            "periodes": [periode.donnees() for periode in self.periodes],
            "trimestres": [
                {"famille": famille, "annee": annee, "trimestres": trimestres,
                 "cotises": self.cotises.get(famille, {}).get(annee, 0),
                 "nationaux": self.nationaux.get(famille, {}).get(annee, 0),
                 "au_salaire_moyen": self.au_salaire_moyen.get(famille, {}).get(annee, 0)}
                for famille in FAMILLES
                for annee, trimestres in sorted(self.pour_le_taux.get(famille, {}).items())],
        }


def famille_du_regime(moteur: ScenarioActuel, code: str) -> str | None:
    """La famille dont un régime lit les trimestres étrangers : celle des
    fonctionnaires pour un régime de la fonction publique que la fiche
    coordonne, la générale pour les autres qu'elle coordonne et pour les
    régimes en points, dont le taux plein suit celui du régime général ;
    aucune pour un autre régime en annuités, que la fiche ne coordonne pas."""
    regime = moteur.catalogue[code] if code in moteur.catalogue else None
    if code in moteur.carrieres_hors_de_france.regimes("totalisation"):
        return (FONCTIONNAIRES if regime is not None and regime.famille == "fonction_publique"
                else GENERALE)
    if regime is not None and any(periode.type_calcul in ("points", "mixte")
                                  for periode in regime.periodes):
        return GENERALE
    return None


def famille_des_regimes(moteur: ScenarioActuel, codes) -> str:
    """La famille dont une condition commune à plusieurs régimes lit les
    trimestres étrangers — la carrière longue, la majoration du minimum, la
    durée tous régimes du résultat : celle des fonctionnaires quand tous les
    régimes de la carrière que la fiche coordonne en sont, la générale sinon.
    Les régimes en points, qui suivent un régime de base, n'en décident
    pas."""
    coordonnes = moteur.carrieres_hors_de_france.regimes("totalisation")
    familles = {famille_du_regime(moteur, code) for code in codes if code in coordonnes}
    return FONCTIONNAIRES if familles == {FONCTIONNAIRES} else GENERALE


def compter_les_periodes(carriere: Carriere, periodes: tuple[PeriodeCoordonnee, ...],
                         trimestres_francais: int,
                         famille: str = GENERALE) -> TrimestresEtrangers:
    """Les trimestres que chaque période coordonnée apporte, année par année :
    trois mois en font un, la fraction arrondie au trimestre supérieur, pour un
    accord ou une équivalence (R. 351-5, règlement 987/2009, article 13) ; de
    date à date, une fois par quatre-vingt-dix jours, pour une organisation
    internationale (R. 161-16-1). Chaque famille les retient sans que l'année
    dépasse quatre trimestres avec ceux que la carrière valide en France
    (R. 351-5), ni, l'année du départ, les trimestres civils écoulés avant
    lui ; ceux d'un accord d'abord. L'équivalence ne vaut depuis 2011 qu'à
    qui a assez de trimestres en France (L. 742-2).

    UN SEUL ACCORD À LA FOIS : la caisse ne totalise que les périodes d'un
    instrument — les règlements européens, l'accord avec le Royaume-Uni, ou
    une convention avec les États tiers qu'elle fait compter (CLEISS ;
    exposés de la Cnav) —, et chaque famille retient celui qui lui apporte le
    plus de trimestres ; ceux que le droit français fait compter —
    organisation internationale, équivalence — s'y ajoutent toujours. La
    pension nationale en retient de même tout ce que cet accord ne compare
    pas (:func:`_groupes`)."""
    francais = carriere.trimestres_par_annee(carriere.lignes)
    depart = carriere.date_liquidation
    candidats: list[tuple[PeriodeCoordonnee, int, int]] = []
    for coordonnee in periodes:
        if coordonnee.titre is None:
            continue
        parametres = coordonnee.parametres
        seuil = parametres.get("equivalentes_trimestres_francais_au_moins")
        if (coordonnee.titre == EQUIVALENCE and seuil is not None
                and trimestres_francais < seuil):
            continue
        for annee, trimestres in _trimestres_de(coordonnee, parametres, depart).items():
            candidats.append((coordonnee, annee, trimestres))
    calculs = []
    for groupe, compare in _groupes(candidats):
        pour_le_taux, cotises, au_salaire_moyen = _retenir(groupe, francais, depart)
        nationaux, _, _ = _retenir(
            [c for c in groupe if not compare or _accord_de(c[0]) is None], francais, depart)
        calculs.append((pour_le_taux, cotises, nationaux, au_salaire_moyen))
    retenus: tuple[dict[str, dict[int, int]], ...] = ({}, {}, {}, {})
    for retenante in FAMILLES:
        # Le premier des accords qui en apportent le plus, dans l'ordre des
        # périodes.
        meilleur = max(calculs, key=lambda calcul: sum(calcul[0][retenante].values()))
        for table, retenue in zip(retenus, meilleur):
            table[retenante] = retenue[retenante]
    return TrimestresEtrangers(retenus[0], retenus[1], periodes, famille, retenus[2],
                               retenus[3])


def _accord_de(coordonnee: PeriodeCoordonnee) -> str | None:
    """L'accord qui fait compter la période : son instrument, ou l'État de sa
    convention ; ``None`` pour une période que le droit français fait compter."""
    if coordonnee.titre != ACCORD:
        return None
    return coordonnee.periode.pays if coordonnee.instrument == CONVENTION else coordonnee.instrument


def _groupes(candidats: list[tuple[PeriodeCoordonnee, int, int]]
             ) -> list[tuple[list[tuple[PeriodeCoordonnee, int, int]], bool]]:
    """Les trimestres que chaque accord ferait totaliser, dans l'ordre des
    périodes : les siens, ceux des États tiers que sa convention fait compter,
    et ceux que le droit français fait compter ; et si l'accord compare la
    pension nationale à la pension proratisée. Sans accord, ces derniers
    seuls."""
    accords: dict[str, tuple[set[str], bool]] = {}
    for coordonnee, _, _ in candidats:
        cle = _accord_de(coordonnee)
        if cle is not None:
            tiers, compare = accords.get(cle, (set(), False))
            accords[cle] = (tiers | set(coordonnee.etats_tiers), compare or coordonnee.comparee)
    if not accords:
        return [(candidats, False)]
    return [([c for c in candidats if (accord := _accord_de(c[0])) is None or accord == cle
              or c[0].periode.pays in tiers], compare)
            for cle, (tiers, compare) in accords.items()]


def _retenir(candidats: list[tuple[PeriodeCoordonnee, int, int]], francais: dict[int, int],
             depart: DateMois) -> tuple[dict[str, dict[int, int]], ...]:
    """Ce que chaque famille retient de ces trimestres, année par année, sous
    le plafond de l'année : ceux d'un accord d'abord, les seuls cotisés ; et
    ceux des régimes étrangers équivalents, à égalité les derniers."""
    offres: dict[str, dict[int, list[tuple[int, int, int]]]] = {f: {} for f in FAMILLES}
    for coordonnee, annee, trimestres in candidats:
        depuis = coordonnee.salaire_moyen_depuis
        equivalent = int(depuis is not None and annee >= depuis)
        for retenante in coordonnee.familles:
            offres[retenante].setdefault(annee, []).append(
                (TITRES.index(coordonnee.titre), trimestres, equivalent))
    pour_le_taux: dict[str, dict[int, int]] = {f: {} for f in FAMILLES}
    cotises: dict[str, dict[int, int]] = {f: {} for f in FAMILLES}
    au_salaire_moyen: dict[str, dict[int, int]] = {f: {} for f in FAMILLES}
    for retenante, annees in offres.items():
        for annee in sorted(annees):
            plafond = 4 if annee < depart.annee else trimestres_civils(depart.mois - 1)
            libres = max(0, plafond - francais.get(annee, 0))
            retenus = cotises_annee = equivalents = 0
            for rang, trimestres, equivalent in sorted(annees[annee]):
                pris = min(trimestres, libres - retenus)
                retenus += pris
                if TITRES[rang] == ACCORD:
                    cotises_annee += pris
                if equivalent:
                    equivalents += pris
            if retenus:
                pour_le_taux[retenante][annee] = retenus
            if cotises_annee:
                cotises[retenante][annee] = cotises_annee
            if equivalents:
                au_salaire_moyen[retenante][annee] = equivalents
    return pour_le_taux, cotises, au_salaire_moyen


def _trimestres_de(coordonnee: PeriodeCoordonnee, parametres: dict,
                   depart: DateMois) -> dict[int, int]:
    """Les trimestres qu'une période apporte, année par année, avant le
    plafond de l'année : jusqu'au départ, quand elle le dépasse — celui d'une
    pension qui s'ouvre plus tôt que le départ déclaré."""
    periode = coordonnee.periode
    au_plus = parametres["trimestres_par_annee_au_plus"]
    fin = depart if depart.rang < periode.fin.rang else periode.fin
    if coordonnee.titre == ORGANISATION:
        jours = parametres["jours_par_trimestre_organisations_internationales"]
        resultat = {}
        for annee in range(periode.debut.annee, fin.annee + 1):
            ouverture = max(date(periode.debut.annee, periode.debut.mois, 1), date(annee, 1, 1))
            cloture = min(date(fin.annee, fin.mois, 1), date(annee + 1, 1, 1))
            if cloture > ouverture and (cloture - ouverture).days >= jours:
                resultat[annee] = min(au_plus, (cloture - ouverture).days // jours)
        return resultat
    if coordonnee.titre == EQUIVALENCE:
        avant = parametres["equivalentes_avant"]
        limite = DateMois(int(avant[:4]), int(avant[5:7]))
        fin = limite if limite.rang < fin.rang else fin
    par_trimestre = parametres["mois_par_trimestre"]
    resultat = {}
    for annee in range(periode.debut.annee, fin.annee + 1):
        mois = mois_travailles(annee, periode.debut, fin)
        if mois > 0:
            resultat[annee] = min(au_plus, -(-mois // par_trimestre))
    return resultat


#: Ce que des périodes hors de France n'apportent pas, faute d'en avoir.
RIEN = TrimestresEtrangers({famille: {} for famille in FAMILLES},
                           {famille: {} for famille in FAMILLES}, (), GENERALE,
                           {famille: {} for famille in FAMILLES},
                           {famille: {} for famille in FAMILLES})


def trimestres_etrangers(moteur: ScenarioActuel, carriere: Carriere) -> TrimestresEtrangers:
    """Les deux temps à la suite, pour qui lit les trimestres étrangers hors
    du relevé — la carrière longue d'un autre départ : coordonner les périodes
    de la carrière, puis les compter. Le seuil de l'équivalence se lit sur la
    durée de la carrière française, celle de ses lignes."""
    if not carriere.periodes_a_l_etranger:
        return RIEN
    return compter_les_periodes(carriere, coordonner_les_periodes(moteur, carriere),
                                carriere.trimestres_actuels)


def pensions_a_l_ecretement(moteur: ScenarioActuel, carriere: Carriere,
                            depuis: DateMois | None = None,
                            jusqu_au: DateMois | None = None,
                            annee: int | None = None) -> float:
    """Ce que les pensions étrangères ajoutent, par an, aux pensions que
    l'écrêtement du minimum contributif compte depuis 2012 (L. 173-2, fiche
    ``minimum_contributif_international``) : celles qui ont commencé au plus
    tard le mois de la date d'effet, au montant de ce mois (R. 173-7) — leur
    montant de départ, suivi sur les prix —, hors celles que calculent les
    règlements européens, l'accord avec le Royaume-Uni et six conventions.
    Rien avant 2012, et rien pour qui n'en déclare pas (présomption
    ``pas_de_pension_etrangere``). Avec ``depuis``, ``jusqu_au`` et ``annee`` :
    celles qui ont commencé après le premier mois et au plus tard le second,
    en euros de l'année — ce qui révise le minimum après le départ
    (R. 173-8)."""
    effet = date_d_effet(carriere)
    if effet is None or not carriere.pensions_etrangeres:
        return 0.0
    jusqu_au = carriere.date_liquidation if jusqu_au is None else jusqu_au
    annee = carriere.annee_liquidation if annee is None else annee
    domaine = moteur.carrieres_hors_de_france
    version = domaine.version("minimum", {"liquidation.date_effet": effet})
    if version is None or not version["parametres"].get("ecretement_pensions_etrangeres"):
        return 0.0
    exclues = set(version["parametres"].get("pensions_hors_ecretement") or ())
    total = 0.0
    for pension in carriere.pensions_etrangeres:
        if (pension.debut.rang > jusqu_au.rang or pension.pays in exclues
                or (depuis is not None and pension.debut.rang <= depuis.rang)):
            continue
        accord = domaine.accord(pension.pays, _jour(pension.debut))
        if accord is not None and accord["instrument"] in exclues:
            continue
        total += pension_etrangere_annuelle(moteur.macro, pension, annee)
    return total


def pension_etrangere_annuelle(macro, pension: PensionEtrangere, annee: int) -> float:
    """Ce qu'une pension étrangère sert par an, en euros de ``annee`` : son
    montant de départ, déclaré, suivi sur les prix — la caisse revalorise
    « tous les avantages viagers [...] dans les mêmes conditions que ceux du
    régime général » (exposé de la Cnav « Evaluation des ressources - Aspa »),
    sur les prix depuis 2004 (L. 161-23-1)."""
    return pension.mensuel * MOIS_PAR_AN * macro.coefficient_prix(pension.debut.annee, annee)


def pensions_etrangeres_servies(macro, carriere: Carriere, mois: DateMois,
                                annee: int | None = None) -> float:
    """Ce que les pensions étrangères déclarées servent par an au mois
    ``mois`` — celles qui ont commencé au plus tard ce mois —, en euros de
    ``annee``, celle du mois par défaut. Des ressources : l'ASPA compte « tous
    les avantages d'invalidité et de vieillesse dont bénéficie l'intéressé »
    (R. 815-22), et la garantie de la proposition, qui la remplace, toutes
    les retraites obligatoires. Rien pour qui n'en déclare pas (présomption
    ``pas_de_pension_etrangere``)."""
    annee = mois.annee if annee is None else annee
    return sum(pension_etrangere_annuelle(macro, pension, annee)
               for pension in carriere.pensions_etrangeres if pension.debut.rang <= mois.rang)
