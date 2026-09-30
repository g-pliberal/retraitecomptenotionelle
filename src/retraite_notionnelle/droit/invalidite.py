"""L'invalidité et l'inaptitude (docs/architecture.md, § 11) : ce que les
étapes du droit lisent des fiches du domaine, que
:class:`~retraite_notionnelle.scenarios.actuel.Invalidites` prépare.

* ``inaptitude_au_travail`` : l'assuré reconnu inapte au travail a le taux
  plein quelle que soit sa durée d'assurance (L. 351-8, 2°), dans les régimes
  de la fiche, à un âge que la version dit — soixante ans, puis l'âge légal
  de sa génération, puis soixante-deux ans depuis le 1er septembre 2023, quand
  l'âge légal monte à soixante-quatre (L. 351-1-5, D. 351-1-14) ; avant le
  1er avril 1983, le taux de soixante-cinq ans dès soixante ans. L'ex-invalide
  en est : la pension qui remplace la sienne est « la pension de vieillesse
  allouée en cas d'inaptitude au travail » (L. 341-15).
* ``pension_d_invalidite_substituee`` : la pension d'invalidité prend fin à
  cet âge, et la pension de vieillesse la remplace d'office, au premier jour
  du mois qui suit (R. 341-22), « quelle que soit la date de dépôt effective
  de la demande » (circulaire Cnav n° 2023-25). Depuis mars 2010, l'invalide
  qui travaille garde sa pension d'invalidité jusqu'à sa demande, au plus
  tard à l'âge du taux plein automatique (L. 341-16) ; depuis septembre
  2017, le demandeur d'emploi indemnisé la garde six mois de plus
  (D. 341-1). Avant 2010, l'invalide qui travaillait pouvait s'opposer à la
  substitution : le modèle présume l'opposition de qui travaille encore.

:mod:`.ouvrir` en tire l'âge d'ouverture de l'inapte, :mod:`.liquider` son
taux plein et celui des complémentaires qui le suivent, :mod:`.departs` la
date où la pension de vieillesse de l'ex-invalide commence.

Son jumeau est ``moteur/js/droit/invalidite.js``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from .commun import date_d_effet

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..scenarios.actuel import ScenarioActuel

#: L'âge d'une version qui le lit à la génération : celui de L. 161-17-2.
AGE_LEGAL_PAR_GENERATION = "age_legal_par_generation"

#: Le régime dont l'Agirc-Arrco et l'Ircantec suivent le taux plein : « le
#: régime général ou le régime des assurances sociales agricoles », dont
#: l'inapte a le taux plein au même âge.
REGIME_DES_SALARIES = "regime_general"

#: Ce que devient la pension d'invalidité de qui travaille à l'âge de la
#: substitution : gardée jusqu'à sa demande (L. 341-16 depuis mars 2010), ou
#: jusqu'à celle-ci aussi quand il s'oppose à la substitution (avant).
MAINTIEN_JUSQU_A_LA_DEMANDE = "maintien_jusqu_a_la_demande"
OPPOSITION = "opposition"

#: Pourquoi la substitution ne se fait pas à l'âge : l'invalide travaille, ou
#: il est demandeur d'emploi indemnisé.
ACTIVITE = "activite"
CHOMAGE = "chomage"


def age_de_la_fiche(moteur: ScenarioActuel, carriere: Carriere, valeur) -> float:
    """Un âge qu'une version écrit : un nombre, ou l'âge légal de la
    génération (``age_legal_par_generation``)."""
    if valeur == AGE_LEGAL_PAR_GENERATION:
        lu = moteur.ages_ouverture.age(carriere.generation)
        return lu[0] if lu is not None else 60.0
    return float(valeur)


def reconnu_inapte(carriere: Carriere) -> bool:
    """L'assuré est-il inapte au sens de L. 351-8, 2° ? Reconnu inapte à sa
    demande, ou ex-invalide, que L. 341-15 range parmi eux."""
    return carriere.inaptitude or carriere.pension_d_invalidite is not None


def age_d_inaptitude(moteur: ScenarioActuel, regime: str,
                     carriere: Carriere) -> float | None:
    """L'âge auquel ce régime ouvre le droit à l'inapte, au taux plein, pour
    une pension qui prend effet à la date de liquidation de ``carriere``
    (fiche ``inaptitude_au_travail``) ; ``None`` quand l'assuré n'est pas
    inapte, que le régime n'applique pas la fiche ou que la carrière n'a pas
    de départ."""
    if not reconnu_inapte(carriere) or regime not in moteur.invalidites.regimes("inaptitude"):
        return None
    date = date_d_effet(carriere)
    version = None if date is None else moteur.invalidites.version("inaptitude", date)
    if version is None:
        return None
    return age_de_la_fiche(moteur, carriere, version["parametres"]["age"])


def taux_plein_de_l_inapte(moteur: ScenarioActuel, regime: str, carriere: Carriere,
                           age_liquidation: float) -> bool:
    """Le taux plein que ce régime sert à l'inapte, quelle que soit sa durée :
    le taux plein depuis le 1er avril 1983, le taux de soixante-cinq ans
    avant — ce que la décote nulle rend dans les deux cas."""
    age = age_d_inaptitude(moteur, regime, carriere)
    return age is not None and age_liquidation + 1e-9 >= age


@dataclass(frozen=True)
class Substitution:
    """La pension de vieillesse qui remplace la pension d'invalidité : le mois
    où elle commence, la version qui la date, et, quand ce n'est pas à l'âge,
    pourquoi (:data:`ACTIVITE`, :data:`CHOMAGE`)."""

    date: DateMois
    version: str
    maintien: str | None = None


def substitution(moteur: ScenarioActuel, carriere: Carriere) -> Substitution | None:
    """Le mois où la pension de vieillesse de l'ex-invalide commence, dans les
    régimes de la fiche ``pension_d_invalidite_substituee``, pour la carrière
    et son départ déclaré ; ``None`` sans pension d'invalidité, ou quand
    l'invalidité est née après l'âge de la substitution.

    La version se lit à la date qu'elle donne elle-même : la première dont
    l'âge tombe entre ses bornes. L'activité et le chômage se lisent sur
    l'année où l'âge est atteint. Le départ déclaré n'avance jamais la
    substitution faite d'office ; il la date quand la pension d'invalidité
    est gardée jusqu'à la demande, sans dépasser l'âge du taux plein
    automatique, ni six mois pour le demandeur d'emploi.
    """
    pension = carriere.pension_d_invalidite
    if pension is None or carriere.age_liquidation is None:
        return None
    preparee = moteur.invalidites.fiches().get(
        moteur.invalidites.FICHES["substitution"])
    if preparee is None:
        return None
    for version in preparee["versions"]:
        age = age_de_la_fiche(moteur, carriere, version["parametres"]["age"])
        date = carriere.date_de_l_age(age)
        debut, fin = version["bornes"]["liquidation.date_effet"]
        jour = f"{date.annee:04d}-{date.mois:02d}-01"
        if (debut is None or debut <= jour) and (fin is None or jour < fin):
            break
    else:
        return None
    if pension.debut >= date:
        return None
    parametres = version["parametres"]
    declare = carriere.date_liquidation
    annee = carriere.mois_de_l_anniversaire(age).annee
    principale = next(iter(carriere.lignes_de(annee)), None)
    nature = principale.type_periode if principale is not None else None
    if (nature == "emploi" and principale.revenu > 0
            and parametres.get("invalide_qui_travaille") in (
                MAINTIEN_JUSQU_A_LA_DEMANDE, OPPOSITION)):
        plus_tard = declare
        if parametres.get("invalide_qui_travaille") == MAINTIEN_JUSQU_A_LA_DEMANDE:
            automatique = moteur.ages_annulation_decote.age(carriere.generation)
            plus_tard = min(declare, carriere.date_de_l_age(
                automatique[0] if automatique is not None else 65.0))
        return Substitution(max(date, plus_tard), version["id"], ACTIVITE)
    mois = parametres.get("maintien_du_demandeur_d_emploi_mois")
    if nature == "chomage_indemnise" and mois:
        return Substitution(max(date, min(declare, date.plus_mois(int(mois)))),
                            version["id"], CHOMAGE)
    return Substitution(date, version["id"])
