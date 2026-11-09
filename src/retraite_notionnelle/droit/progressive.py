"""La retraite progressive (docs/architecture.md, § 7.4 ; fiche ``retraite_progressive``).

L'assuré qui garde en fin de carrière une activité à temps partiel peut
demander la liquidation PROVISOIRE de ses pensions et le service d'une
fraction de celles-ci : la différence entre 100 % et sa quotité depuis le
18 décembre 2014 (R. 351-41, R. 161-19-6, D. 37-2), 30, 50 ou 70 % selon la
tranche de sa quotité avant. Au départ, la pension complète se liquide dans
les conditions de droit commun, la durée accomplie depuis comprise, et ne
peut être inférieure à la pension provisoire, revalorisée (D. 351-15 depuis
le 8 juin 2006, D. 161-2-24-7) ; avant, elle était la pension provisoire,
servie entière. Le fonctionnaire n'a pas ce plancher : sa pension complète se
liquide aux règles de sa date, ses services à temps partiel compris (D. 37-3,
article 49 sexies du décret n° 2003-1306, article 34 sexies du décret
n° 2004-1056).

La demande est ouverte :

* depuis le 4 mai 1988 (R. 351-39 à R. 351-44) à qui travaille à temps partiel
  dans un régime qui la sert : le régime général et les salariés agricoles
  (L. 351-15), les artisans et les commerçants (L. 634-3-1), les exploitants
  agricoles ; le 1er septembre 2023, les fonctionnaires (L. 89 bis du code des
  pensions, article 49 bis du décret n° 2003-1306, article 34 bis du décret
  n° 2004-1056), les libéraux — L. 643-8-1 ne la leur ouvrait que « dans des
  conditions fixées par décret », jamais paru —, les avocats, les clercs de
  notaire, l'Opéra de Paris et les mines (décrets n° 2023-751 et 2023-753), et
  les IEG (annexe 3 au statut national, article 21-1).
  Elle liquide à titre provisoire les régimes que nomme L. 351-15, professions
  libérales comprises, puis, depuis 2023, tous les régimes de base
  (L. 161-22-1-5) ; les complémentaires qui suivent un régime qui la sert
  servent la même fraction (accord Agirc-Arrco du 17 novembre 2017,
  article 88) ; le RAFP, qui attend l'admission à la retraite, non ;
* à l'âge légal, puis, depuis le 22 janvier 2014, deux ans avant, sans
  descendre sous soixante ans (L. 351-15) ; deux ans avant l'âge légal le
  1er septembre 2023 (D. 161-2-24) ; soixante ans pour les pensions prenant
  effet depuis le 1er septembre 2025 (décret n° 2025-681) ;
* à qui justifie de cent cinquante trimestres, tous régimes — cent soixante
  du 28 août 1993 au 8 juin 2006 (R. 351-39, R. 161-19-5, D. 37-1) ;
* à une quotité de 80 % au plus avant le 18 décembre 2014, de 40 à 80 %
  ensuite, arrondie à l'unité, la moitié comptée pour un (R. 351-41,
  R. 161-19-6), et de 50 à 90 % pour un fonctionnaire, dont c'est le temps
  partiel (L. 612-1 du code général de la fonction publique).

Du 18 décembre 2014 au 1er septembre 2023, la décote de la pension provisoire
ne dépasse pas 25 % (R. 351-41, D. 634-19, D. 732-167) : la retraite
progressive s'ouvrant deux ans avant l'âge légal, le décompte par l'âge
dépasse les vingt trimestres que l'arithmétique des deux âges borne
ailleurs. Aucun code ne l'écrit : chaque régime borne sa décote à vingt
trimestres (``decote_trimestres_maximum``, :func:`~.liquider.trimestres_de_decote`),
et les générations qui pouvaient la demander alors, nées après 1952, perdent
1,25 % par trimestre — vingt trimestres font 25 %, et
``tests/test_retraite_progressive.py`` le vérifie.

Le jumeau de ce module est ``moteur/js/droit/progressive.js``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from . import departs as _departs

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..scenarios.actuel import ScenarioActuel
    from .liquidation import Contexte, Liquidation

#: Ce qui ouvre la demande, ou ce qui la ferme.
OUVERTE = "ouverte"
AVANT_1988 = "avant_1988"
SANS_ACTIVITE = "activite"
SANS_REGIME = "regimes"
QUOTITE = "quotite"
AGE = "age"
DUREE = "duree"

#: La fiche qui porte la règle : ses dates et ses valeurs, version par version.
FICHE = "retraite_progressive"
#: Ce que la fiche dit de l'âge, de la fraction, de la pension complète et des
#: régimes liquidés.
AGE_LEGAL = "age_legal"
AGE_LEGAL_MOINS_DEUX_ANS = "age_legal_moins_deux_ans"
PAR_TRANCHES = "par_tranches"
COMPLEMENT_DE_LA_QUOTITE = "complement_de_la_quotite"
RECALCULEE = "recalculee"
TOUS = "tous"


def _jour(date: DateMois) -> str:
    return f"{date.annee:04d}-{date.mois:02d}-01"


@dataclass(frozen=True)
class Progressive:
    """Une demande de retraite progressive, et ce que le droit en fait."""

    #: Le mois où elle prend effet, et la quotité du temps partiel gardé.
    date: DateMois
    quotite: float
    #: ``ouverte``, ou ce qui la ferme : ``avant_1988``, ``activite``,
    #: ``regimes``, ``quotite``, ``age``, ``duree``.
    motif: str
    #: La fraction servie ; nulle quand la demande n'est pas ouverte.
    fraction: float = 0.0
    #: Les régimes qui liquident à titre provisoire : de base, puis les
    #: complémentaires qui les suivent.
    bases: frozenset[str] = frozenset()
    complementaires: frozenset[str] = frozenset()
    age_minimum: float | None = None
    duree_requise: int | None = None
    trimestres: int | None = None

    @property
    def ouverte(self) -> bool:
        return self.motif == OUVERTE

    @property
    def date_effet(self) -> str:
        return _jour(self.date)

    @property
    def regimes(self) -> frozenset[str]:
        return self.bases | self.complementaires


def regle(moteur: ScenarioActuel, date: DateMois) -> dict:
    """La règle de la retraite progressive pour une pension prenant effet à
    cette date : les paramètres de la version de sa fiche qui vaut ce jour-là
    (``fiches_datees``). Sans version à cette date, aucun droit ; sans la
    fiche, le calcul s'arrête : un droit ne se refuse pas par défaut."""
    if FICHE not in moteur.fiches_datees.fiches():
        raise LookupError(f"{FICHE} : la fiche manque aux fiches datées du moteur")
    return moteur.fiches_datees.regle(FICHE, _jour(date)) or {"existe": False}


def age_minimum(moteur: ScenarioActuel, carriere: Carriere, date: DateMois) -> float | None:
    """L'âge qui ouvre la retraite progressive à cette date ; ``None`` sans
    droit."""
    lue = regle(moteur, date)
    age, plancher = lue.get("age"), lue.get("age_plancher")
    if age is None:
        return None
    if age == AGE_LEGAL:
        ouvre = _departs.age_legal(moteur, carriere)
    elif age == AGE_LEGAL_MOINS_DEUX_ANS:
        ouvre = _departs.age_legal(moteur, carriere) - 2.0
    elif isinstance(age, (int, float)) and not isinstance(age, bool):
        ouvre = float(age)
    else:
        raise ValueError(f"{FICHE} : âge « {age} » inconnu du moteur")
    return ouvre if plancher is None else max(float(plancher), ouvre)


def duree_requise(moteur: ScenarioActuel, date: DateMois) -> int | None:
    """La durée d'assurance que la retraite progressive demande à cette date ;
    ``None`` sans droit."""
    return regle(moteur, date).get("duree_requise")


def regimes_ouverts(moteur: ScenarioActuel, date: DateMois) -> frozenset[str]:
    """Les régimes de base où l'on peut demander la retraite progressive à
    cette date, en y travaillant à temps partiel."""
    return frozenset(regle(moteur, date).get("regimes_ouverts") or ())


def regimes_liquides(moteur: ScenarioActuel, date: DateMois) -> frozenset[str] | None:
    """Les régimes de base où la demande liquide à titre provisoire à cette
    date ; ``None`` : tous."""
    liquides = regle(moteur, date).get("regimes_liquides") or ()
    if liquides == TOUS:
        return None
    if not isinstance(liquides, (list, tuple)):
        raise ValueError(f"{FICHE} : régimes liquidés « {liquides} » inconnus du moteur")
    return frozenset(liquides)


def fraction(moteur: ScenarioActuel, date: DateMois, quotite: float,
             fonctionnaire: bool) -> float | None:
    """La fraction servie pour cette quotité, ou ``None`` si la quotité ne
    l'ouvre pas : par tranches de quotité, puis, depuis le 18 décembre 2014,
    ce qui manque à la quotité pour faire 100 %, la quotité arrondie à
    l'unité, la moitié comptée pour un (R. 351-41, R. 161-19-6). La fiche dit
    laquelle, ses tranches et ses bornes, celles du fonctionnaire à part."""
    lue = regle(moteur, date)
    if lue.get("fraction") == PAR_TRANCHES:
        if quotite > lue["quotite_maximum"] + 1e-9:
            return None
        for seuil, servie in lue["tranches"]:
            if quotite >= seuil - 1e-9:
                return servie
        return None
    if lue.get("fraction") != COMPLEMENT_DE_LA_QUOTITE:
        if lue.get("existe"):
            raise ValueError(f"{FICHE} : fraction « {lue.get('fraction')} » inconnue du moteur")
        return None
    points = math.floor(quotite * 100.0 + 0.5 + 1e-9)
    bornes = (lue["quotite_des_fonctionnaires"] if fonctionnaire
              else {"minimum": lue["quotite_minimum"], "maximum": lue["quotite_maximum"]})
    bas, haut = round(bornes["minimum"] * 100.0), round(bornes["maximum"] * 100.0)
    if not bas <= points <= haut:
        return None
    return (100 - points) / 100.0


def examiner(moteur: ScenarioActuel, carriere: Carriere) -> Progressive | None:
    """La retraite progressive que ``carriere`` demande, ouverte ou non ;
    ``None`` sans demande. La durée d'assurance se lit sur sa liquidation
    (:func:`avec_la_duree`)."""
    demande = carriere.retraite_progressive
    if demande is None:
        return None
    date, quotite = demande
    lue = regle(moteur, date)
    if not lue.get("existe"):
        return Progressive(date, quotite, AVANT_1988)
    a_la_date = carriere.liquidee_au(date)
    actifs = _departs.regimes_actifs(moteur, a_la_date)
    if not actifs:
        return Progressive(date, quotite, SANS_ACTIVITE)
    ouverts = regimes_ouverts(moteur, date)
    if actifs.isdisjoint(ouverts):
        return Progressive(date, quotite, SANS_REGIME)
    bases, suivies = _departs.regimes_de_la_carriere(moteur, a_la_date)
    liquides = regimes_liquides(moteur, date)
    retenues = frozenset(code for code in bases if liquides is None or code in liquides)
    if not retenues:
        return Progressive(date, quotite, SANS_REGIME)
    # Les complémentaires qui suivent un régime qui sert la retraite
    # progressive : pas celles des libéraux avant 2023.
    complementaires = frozenset(
        code for code, avec in suivies.items()
        if code != _departs.RAFP and not avec.isdisjoint(retenues & ouverts))
    fonctionnaires = frozenset(
        (lue.get("quotite_des_fonctionnaires") or {}).get("regimes") or ())
    fonctionnaire = not actifs.isdisjoint(fonctionnaires)
    servie = fraction(moteur, date, quotite, fonctionnaire)
    age = age_minimum(moteur, carriere, date)
    commun = dict(bases=retenues, complementaires=complementaires, age_minimum=age,
                  duree_requise=duree_requise(moteur, date))
    if servie is None:
        return Progressive(date, quotite, QUOTITE, **commun)
    if carriere.age_au(date) + 1e-9 < age:
        return Progressive(date, quotite, AGE, **commun)
    return Progressive(date, quotite, OUVERTE, fraction=servie, **commun)


def liquider(moteur: ScenarioActuel, carriere: Carriere, contexte: Contexte,
             progressive: Progressive, journal: object | None = None) -> Liquidation:
    """La liquidation provisoire des régimes de la retraite progressive, sur
    la carrière arrêtée à sa date."""
    from . import liquidation as _liquidation

    demande = _liquidation.Demande(
        personne=carriere.personne, date_effet=progressive.date_effet,
        evenement="retraite_progressive", date_evenement=progressive.date_effet,
        nature="provisoire", regimes=tuple(sorted(progressive.regimes)))
    return _liquidation.liquider(
        demande, _liquidation.Etat(carriere.liquidee_au(progressive.date), journal),
        contexte)


def avec_la_duree(progressive: Progressive, provisoire: Liquidation) -> Progressive:
    """La demande, sa durée d'assurance lue : fermée sous la durée requise."""
    from dataclasses import replace

    trimestres = provisoire.releve.durees.trimestres
    motif = (progressive.motif if not progressive.ouverte
             or trimestres >= (progressive.duree_requise or 0) else DUREE)
    return replace(progressive, trimestres=trimestres, motif=motif,
                   fraction=progressive.fraction if motif == OUVERTE else 0.0)


def recalculee(moteur: ScenarioActuel, date: DateMois) -> bool:
    """La pension complète qui prend effet à cette date se recalcule-t-elle ?
    Non avant le décret du 8 juin 2006 : elle était la pension provisoire."""
    return regle(moteur, date).get("pension_complete") == RECALCULEE


def initiales(moteur: ScenarioActuel, progressive: Progressive, provisoire: Liquidation,
              date: DateMois, regimes: frozenset[str] | None = None
              ) -> tuple[tuple[str, float], ...]:
    """La pension provisoire de chaque régime de base de la retraite
    progressive, entière, menée jusqu'à ``date`` : ce que la pension complète
    ne peut descendre sous — hors des régimes que la fiche dit sans plancher
    à cette date, ceux de la fonction publique. ``regimes`` borne ceux qu'un
    départ liquide."""
    from ..revalorisation import mener_au_mois

    sans_plancher = frozenset(
        regle(moteur, date).get("pension_complete_sans_plancher") or ())
    pensions = [p for p in provisoire.regimes if p.regime in progressive.bases
                and p.regime not in sans_plancher
                and (regimes is None or p.regime in regimes)]
    menees = mener_au_mois(moteur, pensions, progressive.date, date)
    return tuple((p.regime, montant) for p, montant in zip(pensions, menees))
