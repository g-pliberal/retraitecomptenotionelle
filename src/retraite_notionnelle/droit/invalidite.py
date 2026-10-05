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
* ``retraite_pour_invalidite_fonction_publique`` : le fonctionnaire radié des
  cadres pour invalidité liquide sa pension à cette date, à tout âge et sans
  condition de durée de services (L. 4, L. 24), sans décote (L. 14), au
  minimum garanti sans condition de taux plein, en quinzièmes sous quinze ans
  (L. 17, c), à 50 % du traitement au moins quand l'invalidité atteint 60 %
  (L. 30), avec une rente viagère d'invalidité quand elle est imputable au
  service (L. 28), le tout sous le traitement (L. 30 ter) ; la CNRACL de même
  (décret n° 2003-1306, articles 22, 30, 34, 36, 37 et 39).
* ``pension_d_invalidite_substituee`` : la pension d'invalidité prend fin à
  cet âge, et la pension de vieillesse la remplace d'office, au premier jour
  du mois qui suit (R. 341-22), « quelle que soit la date de dépôt effective
  de la demande » (circulaire Cnav n° 2023-25). Depuis mars 2010, l'invalide
  qui travaille garde sa pension d'invalidité jusqu'à sa demande, au plus
  tard à l'âge du taux plein automatique (L. 341-16) ; depuis septembre
  2017, le demandeur d'emploi indemnisé la garde six mois de plus
  (D. 341-1). Avant 2010, l'invalide qui travaillait pouvait s'opposer à la
  substitution : le modèle présume l'opposition de qui travaille encore.
* ``retraite_anticipee_handicap`` : l'assuré qui a cotisé, alors que son
  incapacité permanente atteignait le taux de la version, la durée requise
  diminuée de 60 à 100 trimestres part dès cinquante-cinq ans (L. 351-1-3,
  D. 351-1-5 ; L. 24, I, 5°, et R. 37 bis du code des pensions), au taux
  plein (L. 351-8, 4° bis), sa pension majorée du tiers du rapport de cette
  durée à sa durée dans le régime, sous la pension entière ; le
  fonctionnaire handicapé n'a jamais de coefficient de minoration (L. 14, I).
  La concomitance se lit année civile par année civile (circulaire Cnav
  n° 2026-18, 1.1.3.1). Depuis 2015, la même incapacité fait aussi réputer
  inapte (L. 351-8, 1° ter puis 2° ; R. 351-24-3).

:mod:`.ouvrir` en tire l'âge d'ouverture de l'inapte et celui du handicap,
:mod:`.liquider` leur taux plein, la majoration du handicap et le taux plein
des complémentaires qui les suivent, :mod:`.departs` la date où la pension de
vieillesse de l'ex-invalide commence, le scénario 1 et l'échéancier l'âge où
l'allocation de solidarité aux personnes âgées s'ouvre à l'inapte
(:func:`age_de_l_aspa`).

Son jumeau est ``moteur/js/droit/invalidite.js``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..calendrier import DateMois, en_mois
from .commun import date_d_effet, ligne_cotisee

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..scenarios.actuel import ScenarioActuel

#: L'âge d'une version qui le lit à la génération : celui de L. 161-17-2.
AGE_LEGAL_PAR_GENERATION = "age_legal_par_generation"

#: L'âge de l'allocation de solidarité aux personnes âgées de droit commun :
#: celui de :attr:`~retraite_notionnelle.scenarios.actuel.MinimumVieillesse.AGE_OUVERTURE`,
#: recopié pour que ce module n'importe pas le scénario 1, qui l'importe.
AGE_DE_L_ASPA = 65.0

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


def reconnu_inapte(carriere: Carriere, version: dict | None = None) -> bool:
    """L'assuré est-il inapte au sens de L. 351-8, 2° ? Reconnu inapte à sa
    demande, ou ex-invalide, que L. 341-15 range parmi eux ; ou, quand la
    ``version`` de la fiche ``inaptitude_au_travail`` le dit
    (``incapacite_permanente``), l'assuré dont l'incapacité permanente atteint
    ce taux à la date d'effet : le 1° ter de L. 351-8 de 2015 à 2023, le 2°
    depuis (R. 351-24-3)."""
    return (carriere.inaptitude or carriere.pension_d_invalidite is not None
            or incapacite_reconnue(carriere, version, "incapacite_permanente"))


def incapacite_reconnue(carriere: Carriere, version: dict | None, cle: str) -> bool:
    """L'incapacité permanente que la carrière déclare atteint-elle le taux que
    ``version`` exige sous ``cle``, et la date d'effet de la pension la
    trouve-t-elle reconnue ? Faux sans l'une ou l'autre."""
    incapacite = carriere.incapacite_permanente
    if version is None or incapacite is None or carriere.age_liquidation is None:
        return False
    exige = version["parametres"].get(cle)
    return (exige is not None and incapacite.taux >= float(exige)
            and incapacite.debut.rang <= carriere.date_liquidation.rang)


def age_d_inaptitude(moteur: ScenarioActuel, regime: str,
                     carriere: Carriere) -> float | None:
    """L'âge auquel ce régime ouvre le droit à l'inapte, au taux plein, pour
    une pension qui prend effet à la date de liquidation de ``carriere``
    (fiche ``inaptitude_au_travail``) ; ``None`` quand l'assuré n'est pas
    inapte, que le régime n'applique pas la fiche ou que la carrière n'a pas
    de départ."""
    if regime not in moteur.invalidites.regimes("inaptitude"):
        return None
    date = date_d_effet(carriere)
    version = None if date is None else moteur.invalidites.version("inaptitude", date)
    if version is None or not reconnu_inapte(carriere, version):
        return None
    return age_de_la_fiche(moteur, carriere, version["parametres"]["age"])


def taux_plein_de_l_inapte(moteur: ScenarioActuel, regime: str, carriere: Carriere,
                           age_liquidation: float) -> bool:
    """Le taux plein que ce régime sert à l'inapte, quelle que soit sa durée :
    le taux plein depuis le 1er avril 1983, le taux de soixante-cinq ans
    avant — ce que la décote nulle rend dans les deux cas."""
    age = age_d_inaptitude(moteur, regime, carriere)
    return age is not None and age_liquidation + 1e-9 >= age


def age_de_l_aspa(moteur: ScenarioActuel, carriere: Carriere) -> float:
    """L'âge où l'allocation de solidarité aux personnes âgées s'ouvre à cet
    assuré : soixante-cinq ans, « abaissé à l'âge prévu à l'article L. 351-1-5
    pour les personnes mentionnées aux 2° à 5° de l'article L. 351-8 »
    (R. 815-1) — l'inapte et l'ex-invalide en sont —, à l'âge légal de 2011 à
    2023, à soixante ans avant : le paramètre ``age_aspa`` de la version de la
    fiche ``inaptitude_au_travail`` à la date de liquidation. Depuis 2015,
    l'assuré dont l'incapacité permanente atteint 50 % en est aussi (le 1° ter
    de L. 351-8, puis son 2°)."""
    date = date_d_effet(carriere)
    version = None if date is None else moteur.invalidites.version("inaptitude", date)
    if not reconnu_inapte(carriere, version):
        return AGE_DE_L_ASPA
    valeur = None if version is None else version["parametres"].get("age_aspa")
    if valeur is None:
        return AGE_DE_L_ASPA
    return min(AGE_DE_L_ASPA, age_de_la_fiche(moteur, carriere, valeur))


def radiation_du_regime(moteur: ScenarioActuel, regime: str, carriere: Carriere):
    """La radiation des cadres pour invalidité qui liquide la pension de ce
    régime : celle de la carrière, quand le régime est l'un des trois du code
    des pensions que la fiche ``retraite_pour_invalidite_fonction_publique``
    nomme ; ``None`` sinon."""
    radiation = carriere.radiation_pour_invalidite
    if radiation is None or regime not in moteur.invalidites.regimes("fonction_publique"):
        return None
    return radiation


def retraite_pour_invalidite(moteur: ScenarioActuel, regime: str,
                             carriere: Carriere) -> dict | None:
    """La version de la fiche ``retraite_pour_invalidite_fonction_publique``
    qui s'applique à la pension de ce régime liquidée à la date de
    ``carriere``, quand elle l'est pour invalidité ; ``None`` sinon."""
    if radiation_du_regime(moteur, regime, carriere) is None:
        return None
    date = date_d_effet(carriere)
    return None if date is None else moteur.invalidites.version("fonction_publique", date)


#: L'indice majoré dont la valeur au 1er janvier 2004, revalorisée, borne la
#: part du traitement que la rente viagère d'invalidité compte entière (L. 28).
INDICE_DE_LA_RENTE = 681


def rente_viagere_d_invalidite(traitement: float, taux: float, seuil: float) -> float:
    """La rente viagère d'invalidité de L. 28 (article 37 du décret de la
    CNRACL) : « la fraction du traitement [...] égale au pourcentage
    d'invalidité » ; au-delà du seuil, « la fraction dépassant cette limite
    n'est comptée que pour le tiers », et « il n'est pas tenu compte de la
    fraction excédant dix fois ce montant »."""
    compte = min(traitement, seuil) + max(0.0, min(traitement, 10.0 * seuil) - seuil) / 3.0
    return taux * compte


def pension_du_fonctionnaire_invalide(moteur: ScenarioActuel, carriere: Carriere,
                                      version: dict, pension: float, traitement: float,
                                      annee: int) -> tuple[float, str]:
    """La pension du fonctionnaire radié pour invalidité, rente comprise, et ce
    que le détail en dit : la pension rémunérant les services, portée à la
    part du traitement que la version dit quand le taux d'invalidité atteint
    son seuil (L. 30) ; la rente viagère d'invalidité en sus, quand
    l'invalidité est imputable au service (L. 28) ; le total sous le
    traitement, chaque prestation réduite à due proportion (L. 30 ter), ou
    sous les émoluments de base avant 2014."""
    parametres = version["parametres"]
    radiation = carriere.radiation_pour_invalidite
    taux = (radiation.taux or 0.0) / 100.0
    details = []
    plancher = float(parametres.get("plancher_part_du_traitement") or 0.0) * traitement
    if (taux + 1e-9 >= float(parametres.get("plancher_taux_invalidite") or 1.0)
            and pension < plancher):
        pension = plancher
        details.append(f"portée à {plancher:,.2f} €, la moitié du traitement (L. 30)")
    rente = 0.0
    if radiation.imputable and taux > 0:
        valeur = moteur.minimum_garanti.valeur_d_un_indice(INDICE_DE_LA_RENTE, annee)
        seuil = valeur[0] if valeur is not None else traitement
        rente = rente_viagere_d_invalidite(traitement, taux, seuil)
    total = pension + rente
    if parametres.get("plafond_total") and traitement > 0 and total > traitement:
        reduction = traitement / total
        pension, rente = pension * reduction, rente * reduction
        details.append("réduite au traitement (L. 30 ter)")
    if rente > 0:
        details.append(f"rente viagère d'invalidité de {rente:,.2f} € à "
                       f"{radiation.taux:g} % (L. 28)")
    return pension + rente, " ; ".join(details)


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


# LE DÉPART ANTICIPÉ DES ASSURÉS HANDICAPÉS (fiche ``retraite_anticipee_handicap``)

#: La famille des régimes du code des pensions, dont le fonctionnaire
#: handicapé n'a pas de coefficient de minoration (L. 14, I) et dont la
#: majoration se compte sur les services (R. 33 bis).
FONCTION_PUBLIQUE = "fonction_publique"


def version_du_handicap(moteur: ScenarioActuel, carriere: Carriere) -> dict | None:
    """La version de la fiche ``retraite_anticipee_handicap`` pour une pension
    qui prend effet à la date de liquidation de ``carriere``, ou ``None``."""
    date = date_d_effet(carriere)
    return None if date is None else moteur.invalidites.version("handicap", date)


def annee_en_situation_de_handicap(carriere: Carriere, annee: int) -> bool:
    """L'année civile compte-t-elle en situation de handicap ? Dès que
    l'incapacité est justifiée « à un moment quelconque au cours d'une année
    civile d'assurance, il y a lieu d'admettre la concomitance entre cette
    situation et chacun des trimestres d'assurance cotisés reportés au compte
    carrière au titre de l'année en cause », celle de la reconnaissance
    comprise ; et pour l'année du départ, « la concomitance n'est établie que
    dans la mesure où la situation de handicap est justifiée pour des périodes
    situées avant la date d'arrêt du compte » (circulaire Cnav n° 2026-18,
    1.1.3.1), le dernier jour du trimestre civil qui précède la date d'effet.
    L'incapacité est réputée continue jusqu'au départ."""
    incapacite = carriere.incapacite_permanente
    if incapacite is None or carriere.age_liquidation is None:
        return False
    depart = carriere.date_liquidation
    if annee < incapacite.debut.annee or annee > depart.annee:
        return False
    if annee < depart.annee:
        return True
    arret = DateMois(depart.annee, 3 * ((depart.mois - 1) // 3) + 1)
    return incapacite.debut.rang < arret.rang


def trimestres_en_situation_de_handicap(moteur: ScenarioActuel, carriere: Carriere,
                                        cotises: bool = True,
                                        etrangers: dict[int, int] | None = None) -> int:
    """Les trimestres que la carrière a accomplis en situation de handicap,
    tous régimes, quatre au plus par année (D. 171-11-1) : les seuls cotisés —
    « une durée d'assurance ayant donné lieu à cotisations à leur charge » —,
    ou tous ceux de la durée d'assurance, que la version de 2015 exige aussi
    (« une durée d'assurance ou de périodes reconnues équivalentes »).
    ``etrangers`` sont ceux des périodes hors de France, année par année, que
    la famille des régimes retient — cotisés, ou pour le taux —, comptés
    « dans les mêmes conditions » que les autres (annexe 1 de la circulaire)."""
    if carriere.incapacite_permanente is None or carriere.age_liquidation is None:
        return 0
    lignes = (ligne for ligne in carriere.lignes
              if annee_en_situation_de_handicap(carriere, ligne.annee)
              and (not cotises or ligne_cotisee(moteur, carriere, ligne)))
    total = carriere.trimestres_cumules(lignes)
    if etrangers:
        total += sum(nombre for annee, nombre in etrangers.items()
                     if annee_en_situation_de_handicap(carriere, annee))
    return total


def _duree_limite(moteur: ScenarioActuel, carriere: Carriere, parametres: dict,
                  requis: int) -> int:
    """La durée dont la version retranche les trimestres : la durée requise de
    la génération (« la limite fixée en vertu du deuxième alinéa de l'article
    L. 351-1 », « le nombre de trimestres fixé à l'article L. 13 »), moins ce
    que la version retranche en plus à certaines générations (I bis de 2023) ;
    pour les nés avant la génération que ``duree_d_avant_2023_jusqu_a`` dit,
    « la durée d'assurance prévue à l'article L. 161-17-3 dans sa rédaction
    antérieure à la loi n° 2023-270 » (D. 351-1-5 de septembre 2026)."""
    limite = requis
    jusqu_a = parametres.get("duree_d_avant_2023_jusqu_a")
    if jusqu_a is not None and carriere.generation < float(jusqu_a):
        avant = (moteur.durees_requises_avant_reforme_2023.trimestres(carriere.generation)
                 or moteur.durees_requises.trimestres(carriere.generation))
        if avant is not None:
            limite = avant[0]
    for debut, fin, plus in parametres.get("retranches_en_plus") or ():
        if ((debut is None or carriere.generation >= float(debut))
                and (fin is None or carriere.generation < float(fin))):
            limite -= int(plus)
    return limite


def exigences_du_handicap(moteur: ScenarioActuel, carriere: Carriere, requis: int,
                          age: float | None = None) -> tuple[float, int, int | None] | None:
    """Ce que la version de la date d'effet exige pour partir à ``age`` — celui
    de la liquidation par défaut — au titre du handicap : l'âge abaissé dont
    l'âge relève, la durée cotisée en situation de handicap et, quand la
    version l'exige, la durée validée. ``requis`` est la durée requise que
    l'ouverture oppose. ``None`` sans version, ou sous le premier âge.

    Les âges abaissés sont des seuils : qui part entre cinquante-six et
    cinquante-sept ans relève de l'âge de cinquante-six ans, et « entre
    cinquante-neuf ans et l'âge prévu à l'article L. 161-17-2 », de celui de
    cinquante-neuf."""
    version = version_du_handicap(moteur, carriere)
    if version is None or not version["parametres"].get("ages"):
        return None
    parametres = version["parametres"]
    age = carriere.age_liquidation if age is None else age
    ages = [float(a) for a in parametres["ages"]]
    rang = None
    for i, seuil in enumerate(ages):
        if en_mois(age) >= en_mois(seuil):
            rang = i
    if rang is None:
        return None
    limite = _duree_limite(moteur, carriere, parametres, requis)
    validees = parametres.get("validees_retranchees")
    return (ages[rang], limite - int(parametres["cotisees_retranchees"][rang]),
            None if validees is None else limite - int(validees[rang]))


def _regimes_du_handicap(moteur: ScenarioActuel, regimes) -> bool:
    """La demande vise-t-elle un régime de base que la fiche nomme ? Les
    autres n'appliquent pas le départ anticipé, faute d'en avoir lu les
    textes, et la fiche le dit en approximation."""
    nommes = moteur.invalidites.regimes("handicap")
    return any(code in nommes for code in regimes)


def age_du_handicap(moteur: ScenarioActuel, carriere: Carriere, requis: int,
                    regimes, etrangers: tuple[dict[int, int], dict[int, int]] | None = None
                    ) -> float | None:
    """L'âge le plus précoce auquel le départ anticipé des assurés handicapés
    ouvre CETTE liquidation, sur la durée accomplie à sa date d'effet, ou
    ``None`` : la version n'exige pas un taux que la saisie établit, l'âge
    précède le premier âge abaissé, la durée cotisée — et la durée validée,
    quand la version l'exige — manque. ``regimes`` sont les régimes de base
    que la demande vise ; ``etrangers``, les trimestres hors de France cotisés
    puis validés, année par année. C'est le plus bas des âges abaissés que la
    durée accomplie atteint, pourvu qu'il ne suive pas le départ."""
    if not _regimes_du_handicap(moteur, regimes):
        return None
    version = version_du_handicap(moteur, carriere)
    if version is None or not incapacite_reconnue(carriere, version, "taux_incapacite"):
        return None
    parametres = version["parametres"]
    age = carriere.age_liquidation
    limite = _duree_limite(moteur, carriere, parametres, requis)
    cotises = trimestres_en_situation_de_handicap(
        moteur, carriere, True, None if etrangers is None else etrangers[0])
    validees = parametres.get("validees_retranchees")
    valides = (None if validees is None else trimestres_en_situation_de_handicap(
        moteur, carriere, False, None if etrangers is None else etrangers[1]))
    for i, seuil in enumerate(float(a) for a in parametres["ages"]):
        if en_mois(seuil) > en_mois(age):
            break
        if cotises < limite - int(parametres["cotisees_retranchees"][i]):
            continue
        if validees is not None and valides < limite - int(validees[i]):
            continue
        return seuil
    return None


def age_propose_du_handicap(moteur: ScenarioActuel, carriere: Carriere, requis: int,
                            regimes, etrangers: tuple[dict[int, int], dict[int, int]] | None = None
                            ) -> float | None:
    """L'âge le plus précoce que le départ anticipé des assurés handicapés
    ouvrirait à qui continue de cotiser en situation de handicap, ou ``None`` —
    la même projection que :meth:`~retraite_notionnelle.scenarios.actuel.CarriereLongue.age_propose` :
    il manque à chaque âge abaissé ``exigé − accompli`` trimestres, qu'une
    année de cotisation réduit de quatre, la soustraction étant signée, à
    compter du départ, ou de la reconnaissance de l'incapacité quand elle le
    suit. Chaque âge ouvre au plus tardif de lui-même et de l'âge où la durée
    est réunie ; le plus précoce l'emporte. L'appelant le compare à l'âge
    légal, qui l'emporte quand il vient plus tôt."""
    if not _regimes_du_handicap(moteur, regimes):
        return None
    version = version_du_handicap(moteur, carriere)
    incapacite = carriere.incapacite_permanente
    exige = None if version is None else version["parametres"].get("taux_incapacite")
    if (exige is None or incapacite is None or carriere.age_liquidation is None
            or incapacite.taux < float(exige)):
        return None
    parametres = version["parametres"]
    age = carriere.age_liquidation
    depuis = max(age, carriere.age_au(incapacite.debut))
    limite = _duree_limite(moteur, carriere, parametres, requis)
    cotises = trimestres_en_situation_de_handicap(
        moteur, carriere, True, None if etrangers is None else etrangers[0])
    validees = parametres.get("validees_retranchees")
    valides = (0 if validees is None else trimestres_en_situation_de_handicap(
        moteur, carriere, False, None if etrangers is None else etrangers[1]))
    candidats = []
    for i, seuil in enumerate(float(a) for a in parametres["ages"]):
        atteint = depuis + (limite - int(parametres["cotisees_retranchees"][i]) - cotises) / 4.0
        if validees is not None:
            atteint = max(atteint, depuis + (limite - int(validees[i]) - valides) / 4.0)
        candidats.append(max(seuil, atteint))
    return min(candidats) if candidats else None


def sans_decote_du_fonctionnaire(moteur: ScenarioActuel, regime: str,
                                 carriere: Carriere) -> bool:
    """« Le coefficient de minoration n'est pas applicable aux fonctionnaires
    handicapés dont l'incapacité permanente est au moins égale à un taux fixé
    par décret » (L. 14, I, du code des pensions ; D. 14 : 50 % ; décret
    n° 2003-1306, article 20, III ; décret n° 2004-1056, article 16, III), à
    tout âge : dans les régimes du code des pensions que la fiche nomme, quand
    la version le dit et que l'incapacité atteint son taux à la date d'effet."""
    if (regime not in moteur.invalidites.regimes("handicap")
            or regime not in moteur.catalogue
            or moteur.catalogue[regime].famille != FONCTION_PUBLIQUE):
        return False
    version = version_du_handicap(moteur, carriere)
    return (version is not None
            and bool(version["parametres"].get("fonctionnaire_sans_decote"))
            and incapacite_reconnue(carriere, version, "taux_incapacite"))


def coefficient_de_majoration(version: dict, en_situation: int, duree: int) -> float:
    """Le coefficient de la majoration de pension : « un nombre égal au tiers
    du quotient formé par la durée d'assurance dans le régime accomplie alors
    que l'assuré justifiait du taux [...] et ayant donné lieu à cotisations à
    sa charge, d'une part, et la durée d'assurance accomplie dans le régime
    [...], d'autre part. Ce nombre est arrondi, le cas échéant, au centième le
    plus proche » (D. 351-1-5, II) — au centième supérieur dès la troisième
    décimale à cinq (circulaire Cnav n° 2026-18, 3.1) ; au fonctionnaire, les
    services accomplis en situation de handicap sur les services et
    bonifications admis en liquidation (R. 33 bis). Zéro sans majoration."""
    majoration = version["parametres"].get("majoration")
    if not majoration or duree <= 0 or en_situation <= 0:
        return 0.0
    brut = float(majoration["fraction"]) * en_situation / duree
    pas = round(1.0 / float(majoration["arrondi"]))
    return math.floor(brut * pas + 0.5 + 1e-9) / pas
