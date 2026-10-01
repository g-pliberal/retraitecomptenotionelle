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

from ..calendrier import DateMois, mois_travailles, trimestres_civils
from .commun import date_d_effet

if TYPE_CHECKING:
    from ..carriere import Carriere, PeriodeALEtranger
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
#: Celui qui, seul, coordonne aussi les régimes des fonctionnaires.
REGLEMENTS_EUROPEENS = "reglements_europeens"
#: Les personnes qu'une convention ne vise qu'à moitié : les seuls salariés.
SALARIES = "salaries"
SALARIEE = "salariee"
#: Le code d'une organisation internationale au tableau des accords.
ORGANISATION_INTERNATIONALE = "OI"


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

    def donnees(self) -> dict:
        periode = self.periode
        return {"pays": periode.pays, "debut": _jour(periode.debut),
                "fin": _jour(periode.fin), "activite": periode.activite,
                "titre": self.titre, "instrument": self.instrument,
                "familles": list(self.familles), "version": self.version}


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
        coordonnees.append(PeriodeCoordonnee(
            periode=periode, titre=titre, instrument=instrument, familles=familles,
            version=None if version is None else version["id"], parametres=parametres))
    return tuple(coordonnees)


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

    def trimestres(self, famille: str | None) -> int:
        """Les trimestres que la durée du taux de cette famille retient."""
        return sum((self.pour_le_taux.get(famille) or {}).values())

    def trimestres_cotises(self, famille: str | None) -> int:
        """Ceux d'entre eux qui comptent comme cotisés."""
        return sum((self.cotises.get(famille) or {}).values())

    def donnees(self) -> dict:
        return {
            "famille": self.famille,
            "periodes": [periode.donnees() for periode in self.periodes],
            "trimestres": [
                {"famille": famille, "annee": annee, "trimestres": trimestres,
                 "cotises": self.cotises.get(famille, {}).get(annee, 0)}
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
    qui a assez de trimestres en France (L. 742-2)."""
    francais = carriere.trimestres_par_annee(carriere.lignes)
    depart = carriere.date_liquidation
    candidats: dict[str, dict[int, list[tuple[int, int]]]] = {f: {} for f in FAMILLES}
    for coordonnee in periodes:
        if coordonnee.titre is None:
            continue
        parametres = coordonnee.parametres
        seuil = parametres.get("equivalentes_trimestres_francais_au_moins")
        if (coordonnee.titre == EQUIVALENCE and seuil is not None
                and trimestres_francais < seuil):
            continue
        for annee, trimestres in _trimestres_de(coordonnee, parametres, depart).items():
            for retenante in coordonnee.familles:
                candidats[retenante].setdefault(annee, []).append(
                    (TITRES.index(coordonnee.titre), trimestres))
    pour_le_taux: dict[str, dict[int, int]] = {f: {} for f in FAMILLES}
    cotises: dict[str, dict[int, int]] = {f: {} for f in FAMILLES}
    for retenante, annees in candidats.items():
        for annee in sorted(annees):
            plafond = 4 if annee < depart.annee else trimestres_civils(depart.mois - 1)
            libres = max(0, plafond - francais.get(annee, 0))
            retenus = cotises_annee = 0
            for rang, trimestres in sorted(annees[annee]):
                pris = min(trimestres, libres - retenus)
                retenus += pris
                if TITRES[rang] == ACCORD:
                    cotises_annee += pris
            if retenus:
                pour_le_taux[retenante][annee] = retenus
            if cotises_annee:
                cotises[retenante][annee] = cotises_annee
    return TrimestresEtrangers(pour_le_taux, cotises, periodes, famille)


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
                           {famille: {} for famille in FAMILLES}, ())


def trimestres_etrangers(moteur: ScenarioActuel, carriere: Carriere) -> TrimestresEtrangers:
    """Les deux temps à la suite, pour qui lit les trimestres étrangers hors
    du relevé — la carrière longue d'un autre départ : coordonner les périodes
    de la carrière, puis les compter. Le seuil de l'équivalence se lit sur la
    durée de la carrière française, celle de ses lignes."""
    if not carriere.periodes_a_l_etranger:
        return RIEN
    return compter_les_periodes(carriere, coordonner_les_periodes(moteur, carriere),
                                carriere.trimestres_actuels)
