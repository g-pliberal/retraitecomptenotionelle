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

#: Les dates qui découpent la règle, au jour.
DEBUT = "1988-05-04"
AGE_ABAISSE = "2014-01-22"
FRACTION_COMPLEMENTAIRE = "2014-12-18"
TOUS_REGIMES = "2023-09-01"
SOIXANTE_ANS = "2025-09-01"
#: Depuis le décret du 8 juin 2006, la pension complète se recalcule.
RECALCUL = "2006-06-08"

#: La durée d'assurance exigée, et depuis quand (R. 351-39).
DUREES = (("1988-05-04", 150), ("1993-08-28", 160), ("2006-06-08", 150))

#: Les régimes de base où l'assuré qui y travaille à temps partiel peut la
#: demander : ceux de la loi de 1988, puis, le 1er septembre 2023, ceux des
#: décrets n° 2023-751 et 2023-753, et les IEG, dont le statut rend la retraite
#: progressive du code applicable à la même date (annexe 3, article 21-1).
REGIMES_1988 = frozenset({
    "regime_general", "msa_salaries", "cancava", "organic", "rsi", "msa_non_salaries",
})
FONCTION_PUBLIQUE = frozenset({"fonction_publique_etat", "cnracl", "fspoeie"})
REGIMES_2023 = REGIMES_1988 | FONCTION_PUBLIQUE | {
    "cnavpl", "cnbf", "crpcen", "opera_de_paris", "mines", "ieg",
}
#: Ceux où elle liquide à titre provisoire avant 2023 : les régimes que nomme
#: L. 351-15, les professions libérales comprises. Depuis, tous les régimes
#: de base (L. 161-22-1-5).
LIQUIDES_1988 = REGIMES_1988 | {"cnavpl"}


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


def age_minimum(moteur: ScenarioActuel, carriere: Carriere, date: DateMois) -> float:
    """L'âge qui ouvre la retraite progressive à cette date."""
    jour, legal = _jour(date), _departs.age_legal(moteur, carriere)
    if jour < AGE_ABAISSE:
        return legal
    if jour < TOUS_REGIMES:
        return max(60.0, legal - 2.0)
    if jour < SOIXANTE_ANS:
        return legal - 2.0
    return 60.0


def duree_requise(date: DateMois) -> int:
    """La durée d'assurance que la retraite progressive demande à cette date."""
    jour = _jour(date)
    requis = DUREES[0][1]
    for depuis, trimestres in DUREES:
        if jour >= depuis:
            requis = trimestres
    return requis


def regimes_ouverts(date: DateMois) -> frozenset[str]:
    """Les régimes de base où l'on peut demander la retraite progressive à
    cette date, en y travaillant à temps partiel."""
    return REGIMES_2023 if _jour(date) >= TOUS_REGIMES else REGIMES_1988


def regimes_liquides(date: DateMois) -> frozenset[str] | None:
    """Les régimes de base où la demande liquide à titre provisoire à cette
    date ; ``None`` : tous."""
    return None if _jour(date) >= TOUS_REGIMES else LIQUIDES_1988


def fraction(date: DateMois, quotite: float, fonctionnaire: bool) -> float | None:
    """La fraction servie pour cette quotité, ou ``None`` si la quotité ne
    l'ouvre pas. Depuis le 18 décembre 2014, la quotité s'arrondit à l'unité,
    la moitié comptée pour un (R. 351-41, R. 161-19-6)."""
    if _jour(date) < FRACTION_COMPLEMENTAIRE:
        if quotite > 0.8 + 1e-9:
            return None
        return 0.3 if quotite >= 0.6 - 1e-9 else 0.5 if quotite >= 0.4 - 1e-9 else 0.7
    points = math.floor(quotite * 100.0 + 0.5 + 1e-9)
    bas, haut = (50, 90) if fonctionnaire else (40, 80)
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
    if _jour(date) < DEBUT:
        return Progressive(date, quotite, AVANT_1988)
    a_la_date = carriere.liquidee_au(date)
    actifs = _departs.regimes_actifs(moteur, a_la_date)
    if not actifs:
        return Progressive(date, quotite, SANS_ACTIVITE)
    ouverts = regimes_ouverts(date)
    if actifs.isdisjoint(ouverts):
        return Progressive(date, quotite, SANS_REGIME)
    bases, suivies = _departs.regimes_de_la_carriere(moteur, a_la_date)
    liquides = regimes_liquides(date)
    retenues = frozenset(code for code in bases if liquides is None or code in liquides)
    if not retenues:
        return Progressive(date, quotite, SANS_REGIME)
    # Les complémentaires qui suivent un régime qui sert la retraite
    # progressive : pas celles des libéraux avant 2023.
    complementaires = frozenset(
        code for code, avec in suivies.items()
        if code != _departs.RAFP and not avec.isdisjoint(retenues & ouverts))
    fonctionnaire = not actifs.isdisjoint(FONCTION_PUBLIQUE)
    servie = fraction(date, quotite, fonctionnaire)
    age = age_minimum(moteur, carriere, date)
    commun = dict(bases=retenues, complementaires=complementaires, age_minimum=age,
                  duree_requise=duree_requise(date))
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


def recalculee(date: DateMois) -> bool:
    """La pension complète qui prend effet à cette date se recalcule-t-elle ?
    Non avant le décret du 8 juin 2006 : elle était la pension provisoire."""
    return _jour(date) >= RECALCUL


def initiales(moteur: ScenarioActuel, progressive: Progressive, provisoire: Liquidation,
              date: DateMois, regimes: frozenset[str] | None = None
              ) -> tuple[tuple[str, float], ...]:
    """La pension provisoire de chaque régime de base de la retraite
    progressive, entière, menée jusqu'à ``date`` : ce que la pension complète
    ne peut descendre sous — hors de la fonction publique, qui n'a pas ce
    plancher. ``regimes`` borne ceux qu'un départ liquide."""
    from ..revalorisation import mener_au_mois

    pensions = [p for p in provisoire.regimes if p.regime in progressive.bases
                and p.regime not in FONCTION_PUBLIQUE
                and (regimes is None or p.regime in regimes)]
    menees = mener_au_mois(moteur, pensions, progressive.date, date)
    return tuple((p.regime, montant) for p, montant in zip(pensions, menees))
