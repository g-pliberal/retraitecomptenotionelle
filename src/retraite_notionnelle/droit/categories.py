"""Les taux pleins par catégorie de L. 351-8 : ce que les étapes du droit lisent
des fiches qui les datent, que :class:`~retraite_notionnelle.scenarios.actuel.FichesDatees`
prépare.

« Bénéficient du taux plein même s'ils ne justifient pas de la durée requise
d'assurance » (L. 351-8) — avant le 1er avril 1983, du taux de soixante-cinq
ans dès soixante ans :

* ``taux_plein_anciens_deportes_internes`` : l'ancien déporté ou interné,
  titulaire de la carte de déporté ou interné de la Résistance ou politique
  (3°), depuis le 1er mai 1965 (décret n° 65-315) ;
* ``taux_plein_meres_de_famille_ouvrieres`` : la mère de famille salariée qui a
  élevé trois enfants, a trente ans d'assurance au régime général ou chez les
  salariés agricoles, majoration pour enfants comprise, et a exercé un travail
  manuel ouvrier cinq ans au cours des quinze qui précèdent sa demande (4° ;
  R. 351-23), depuis le 1er juillet 1976 (loi n° 75-1279) ;
* ``taux_plein_travailleurs_manuels`` : le travailleur manuel de quarante-trois,
  puis quarante-deux, puis quarante et un ans d'assurance, qui a exercé cinq
  ans au cours des quinze dernières un travail en continu, en semi-continu, à
  la chaîne, au four ou aux intempéries (décret n° 45-0179, article 70-2, a),
  de juillet 1976 à mars 1983, que la règle de 1983 rend sans objet ;
* ``taux_plein_anciens_combattants_prisonniers`` : l'ancien prisonnier de
  guerre ou l'ancien combattant titulaire de la carte du combattant, à un âge
  qui descend avec la durée de sa captivité et de ses services militaires en
  temps de guerre (5° ; D. 351-2), depuis 1974 (loi n° 73-1051).

Les faits — la carte de déporté ou interné, la durée de captivité et de
services de guerre, le travail manuel —, la saisie les déclare
(:meth:`~retraite_notionnelle.carriere.Carriere.titres_au_taux_plein`).
:mod:`.liquider` en tire le taux plein du régime, celui que le minimum
contributif demande et celui que les complémentaires suivent.

Et ``taux_plein_a_soixante_cinq_ans`` : l'âge du 1° de L. 351-8, que « Par
dérogation aux dispositions de l'article L. 351-8 » le IV de l'article 20 de
la loi n° 2010-1330 « fixé à soixante-cinq ans pour les assurés nés entre le
1er juillet 1951 et le 31 décembre 1955 inclus » qui ont eu ou élevé trois
enfants, cessé ou réduit leur activité après la naissance de l'un d'eux, et
travaillé avant elle (décret n° 2011-620, article 2) :
:func:`age_du_parent_de_trois_enfants`, que :func:`.ouvrir.age_taux_plein`
lit.

Son jumeau est ``moteur/js/droit/categories.js``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import chronologie as chrono
from ..somme import somme_ordonnee
from .commun import date_d_effet, ligne_cotisee

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..scenarios.actuel import ScenarioActuel

#: Les fiches des catégories, dans l'ordre où le moteur les essaie.
FICHE_DES_DEPORTES = "taux_plein_anciens_deportes_internes"
FICHE_DES_MERES_OUVRIERES = "taux_plein_meres_de_famille_ouvrieres"
FICHE_DES_TRAVAILLEURS_MANUELS = "taux_plein_travailleurs_manuels"
FICHE_DES_ANCIENS_COMBATTANTS = "taux_plein_anciens_combattants_prisonniers"
FICHES_DES_CATEGORIES = (FICHE_DES_DEPORTES, FICHE_DES_MERES_OUVRIERES,
                         FICHE_DES_TRAVAILLEURS_MANUELS, FICHE_DES_ANCIENS_COMBATTANTS)

#: L'âge qu'une version écrit pour dire l'âge légal de la génération
#: (L. 161-17-2), comme la fiche ``inaptitude_au_travail``.
AGE_LEGAL = "age_legal_par_generation"


def age_legal(moteur: ScenarioActuel, carriere: Carriere) -> float:
    """L'âge de L. 161-17-2 de la génération."""
    lu = moteur.ages_ouverture.age(carriere.generation)
    return lu[0] if lu is not None else 60.0


def age_du_taux_plein(moteur: ScenarioActuel, carriere: Carriere) -> float:
    """L'âge du 1° de L. 351-8, où la décote s'annule, de la génération."""
    lu = moteur.ages_annulation_decote.age(carriere.generation)
    return lu[0] if lu is not None else 65.0


def age_des_anciens_combattants(moteur: ScenarioActuel, regle: dict,
                                carriere: Carriere, mois: int) -> float | None:
    """L'âge dès lequel l'ancien combattant ou prisonnier de guerre a le taux
    plein, selon les mois de sa captivité et de ses services militaires en
    temps de guerre : le palier le plus haut que ses mois atteignent ;
    ``None`` sous le premier, six mois.

    Un palier dit un âge — soixante-quatre ans de six à dix-sept mois, …,
    soixante ans dès cinquante-quatre (décret n° 74-54, D. 351-2 jusqu'en
    juillet 2024) —, ou ce qu'il retranche à l'âge du 1° de L. 351-8 — un, deux,
    trois, quatre ans (D. 351-2 depuis le 8 juillet 2024) —, ou l'âge légal,
    pour les générations qu'il nomme ou pour toutes. ``age_minimum`` borne
    l'âge par en dessous : soixante-trois ans en 1974, la première année.
    ``decalage_age_legal`` ajoute à l'âge l'écart de l'âge légal de la
    génération à soixante ans, deux ans ``au_plus`` : « il était ajouté à
    chaque âge de départ AC/PG prévu à l'article D351-2 CSS deux années de
    plus » depuis la loi de 2010 (circulaire Cnav n° 2024-29).
    """
    retenu = None
    for palier in regle["paliers"]:
        if mois >= int(palier["des_mois"]):
            retenu = palier
    if retenu is None:
        return None
    depuis = retenu.get("age_legal_des_la_generation")
    if retenu.get("age") == AGE_LEGAL or (
            depuis is not None and carriere.annee_naissance >= int(depuis)):
        age = age_legal(moteur, carriere)
    elif retenu.get("age") is not None:
        age = float(retenu["age"])
    else:
        age = age_du_taux_plein(moteur, carriere) - float(retenu["avant_l_age_du_taux_plein"])
    decalage = regle.get("decalage_age_legal")
    if decalage is not None:
        age += max(0.0, min(age_legal(moteur, carriere) - 60.0, float(decalage["au_plus"])))
    return max(age, float(regle.get("age_minimum") or 0.0))


def _age_atteint(moteur: ScenarioActuel, carriere: Carriere, regle: dict,
                 age_liquidation: float) -> bool:
    """La pension prend-elle effet à l'âge que la version écrit, quand elle en
    écrit un ? Sans âge, celui où la pension s'ouvre suffit."""
    age = regle.get("age")
    if age is None:
        return True
    seuil = age_legal(moteur, carriere) if age == AGE_LEGAL else float(age)
    return age_liquidation + 1e-9 >= seuil


def _duree(durees, regle: dict) -> int:
    """La durée d'assurance que la version compte : celle des régimes qu'elle
    nomme, majoration pour enfants comprise."""
    return durees.cumul_plafonne("assurance", tuple(regle["regimes_de_la_duree"]))


def remplit(moteur: ScenarioActuel, nom: str, regle: dict, carriere: Carriere,
            durees, age_liquidation: float) -> bool:
    """L'assuré remplit-il, à la date d'effet, les conditions que la version de
    la fiche ``nom`` écrit ?"""
    if nom == FICHE_DES_DEPORTES:
        return carriere.deporte_ou_interne and _age_atteint(
            moteur, carriere, regle, age_liquidation)
    if nom == FICHE_DES_ANCIENS_COMBATTANTS:
        mois = carriere.mois_de_guerre
        if not mois:
            return False
        age = age_des_anciens_combattants(moteur, regle, carriere, mois)
        return age is not None and age_liquidation + 1e-9 >= age
    travail = carriere.travail_manuel
    if travail is None or travail not in regle["travaux"] or durees is None:
        return False
    if nom == FICHE_DES_MERES_OUVRIERES and (
            carriere.sexe != "F" or carriere.nombre_enfants < int(regle["enfants"])):
        return False
    return (_duree(durees, regle) >= int(regle["trimestres"])
            and _age_atteint(moteur, carriere, regle, age_liquidation))


#: La fiche de l'âge de soixante-cinq ans du parent de trois enfants.
FICHE_DES_SOIXANTE_CINQ_ANS = "taux_plein_a_soixante_cinq_ans"

#: Ce que le décret n° 2011-620, article 2, 1°, écarte des années qui suivent
#: la naissance : la pension d'invalidité et l'accident du travail (R. 351-12,
#: 3° et 5°) ; l'AVPF (L. 381-1) se reconnaît au salaire que la ligne porte.
_ECARTEES_APRES = frozenset({"invalidite", "accident_travail"})

#: Ce qu'il compte dans les deux années qui la précèdent : « les trimestres
#: validés en contrepartie de cotisations à la charge de l'assuré ou au titre
#: de périodes d'arrêt maladie, de maternité, de chômage ». L'emploi n'y entre
#: que cotisé (:func:`.commun.ligne_cotisee`) : l'activité cultuelle d'avant
#: 1979, que D. 721-11 du code de 1985 prend en compte (« sont prises en compte
#: pour l'ouverture du droit et le calcul de la pension »), dont la CAVIMAC
#: dit les trimestres « validés à titre gratuit » (sa page « Demander ma
#: retraite de base »), n'en est pas.
_RETENUES_AVANT = frozenset({"emploi", "maladie", "maternite", "chomage_indemnise",
                             "chomage_solidarite", "chomage_non_indemnise",
                             "preretraite_fne"})


def _remplit_pour_l_enfant(moteur: ScenarioActuel, carriere: Carriere, parents: dict,
                           naissance: dict) -> bool:
    """L'assuré remplit-il, pour l'enfant né à ``naissance`` (un fait déclaré de
    la chronologie), les deux conditions du décret n° 2011-620, article 2 ?

    « au plus huit trimestres au titre de l'année civile de la naissance [...] et
    des deux années civiles suivantes ou, si l'enfant est né [...] au cours d'un
    second semestre, au titre des trois années civiles suivant celle de cette
    naissance », sans l'AVPF, l'invalidité ni l'accident du travail ; « au titre
    des deux années précédant l'année de la naissance [...], un nombre de
    trimestres égal ou supérieur à huit », cotisés ou de maladie, de maternité,
    de chômage ; et « huit trimestres » d'activité avant elle, que la caisse
    compte jusqu'au « dernier jour du trimestre civil précédant la date de la
    naissance » (circulaire Cnav n° 2014-64, point 2.2.2) : l'emploi seul, et,
    l'année de la naissance, les trimestres civils écoulés avant le sien. Dite à
    l'année seule, la naissance n'ouvre le droit que si les conditions tiennent
    quel que soit son mois : les deux fenêtres, et l'activité des seules années
    qui la précèdent.
    """
    annee = chrono.annee_de(naissance["debut"])
    au_mois = ((naissance.get("attributs") or {}).get("precision") or "jour") != "annee"
    mois = chrono.mois_de(naissance["debut"]).mois if au_mois else 1

    def par_annee(garder) -> dict[int, int]:
        return carriere.trimestres_par_annee([l for l in carriere.lignes if garder(l)])

    def somme(table: dict[int, int], debut: int, nombre: int) -> int:
        return somme_ordonnee(table.get(debut + rang, 0) for rang in range(nombre))

    avant = par_annee(lambda ligne: ligne.type_periode in _RETENUES_AVANT
                      and not ligne.revenu_avpf > 0
                      and (ligne.type_periode != "emploi"
                           or ligne_cotisee(moteur, carriere, ligne)))
    if somme(avant, annee - 2, 2) < int(parents["avant_au_moins"]):
        return False
    apres = par_annee(lambda ligne: ligne.type_periode not in _ECARTEES_APRES
                      and not ligne.revenu_avpf > 0)
    debuts = [annee if mois <= 6 else annee + 1] if au_mois else [annee, annee + 1]
    if any(somme(apres, debut, 3) > int(parents["apres_au_plus"]) for debut in debuts):
        return False
    activite = par_annee(lambda ligne: ligne.type_periode == "emploi")
    anterieure = min(activite.get(annee, 0), (mois - 1) // 3)
    anterieure += somme_ordonnee(trimestres for an, trimestres in activite.items() if an < annee)
    return anterieure >= int(parents["activite_au_moins"])


def age_du_parent_de_trois_enfants(moteur: ScenarioActuel, regime: str,
                                   carriere: Carriere) -> float | None:
    """L'âge du 1° de L. 351-8 que la fiche ``taux_plein_a_soixante_cinq_ans``
    fixe à l'assuré dans ``regime``, à la date d'effet de sa pension, quand il
    remplit les conditions du parent de trois enfants — né dans les générations
    de la version, ayant eu ou élevé ses enfants, comptés comme pour la
    majoration de 10 % (circulaire Cnav n° 2014-64, point 2.1), et, pour l'un
    d'eux dont la saisie déclare la naissance, :func:`_remplit_pour_l_enfant`
    — ; ``None`` sinon. Une naissance présumée ne dit rien de l'interruption
    qui la suit."""
    regle = _regle_du_parent(moteur, carriere)
    if regle is None or regime not in regle["regimes"]:
        return None
    parents = regle["parents_de_trois_enfants"]
    return (float(regle["age"]) if _pour_un_enfant_declare(
        carriere, lambda naissance: _remplit_pour_l_enfant(moteur, carriere, parents,
                                                           naissance))
        else None)


def _regle_du_parent(moteur: ScenarioActuel, carriere: Carriere) -> dict | None:
    """La version de la fiche ``taux_plein_a_soixante_cinq_ans`` à la date
    d'effet de la pension, quand l'assuré est né dans ses générations et a ses
    enfants ; ``None`` sinon."""
    date = date_d_effet(carriere)
    if date is None:
        return None
    regle = moteur.fiches_datees.regle(FICHE_DES_SOIXANTE_CINQ_ANS, date)
    parents = (regle or {}).get("parents_de_trois_enfants")
    if not regle or not regle.get("existe") or parents is None:
        return None
    rang = carriere.annee_naissance * 12 + carriere.mois_naissance
    annee_du, mois_du = parents["nes_du"]
    annee_au, mois_au = parents["nes_au"]
    if (rang < annee_du * 12 + mois_du or rang > annee_au * 12 + mois_au
            or carriere.nombre_enfants < int(parents["enfants"])):
        return None
    return regle


def _pour_un_enfant_declare(carriere: Carriere, remplit) -> bool:
    """L'un des enfants dont la saisie déclare la naissance la fait-il remplir ?"""
    for enfant in chrono.enfants(carriere.chronologie, carriere.personne):
        naissance = chrono.naissance(carriere.chronologie, enfant)
        if naissance is not None and naissance.get("origine") == "declare" and remplit(naissance):
            return True
    return False


def _remplit_pour_l_enfant_fonctionnaire(carriere: Carriere, conditions: dict,
                                         naissance: dict) -> bool:
    """Le fonctionnaire remplit-il, pour l'enfant né à ``naissance``, les
    conditions de R. 26 ter, I, du code des pensions (loi n° 2010-1330, article
    28, III) ?

    Une interruption « pendant une durée d'au moins une année » l'année de la
    naissance et les deux suivantes, ou les trois suivantes pour l'enfant né au
    second semestre, « dans le cadre des congés ou de la disponibilité
    mentionnés au 1° de l'article R. 13 » : les années dont la ligne porte l'un
    des motifs ``interruptions`` ; « au titre des deux années précédant l'année
    de la naissance [...], une durée d'assurance, telle que définie à l'article
    L. 14, égale ou supérieure à huit trimestres », tous régimes ; et huit
    trimestres « à raison de l'exercice d'une activité professionnelle,
    préalablement à l'interruption » : l'emploi des années qui précèdent la
    première année de l'interruption dans la fenêtre. Dite à l'année seule, la
    naissance n'en ouvre le droit que si les deux fenêtres le donnent. La
    réduction d'activité (2°) n'est pas lue : le temps partiel saisi ne dit pas
    son motif.
    """
    annee = chrono.annee_de(naissance["debut"])
    au_mois = ((naissance.get("attributs") or {}).get("precision") or "jour") != "annee"
    mois = chrono.mois_de(naissance["debut"]).mois if au_mois else 1
    assurance = carriere.trimestres_par_annee(carriere.lignes)
    avant = assurance.get(annee - 2, 0) + assurance.get(annee - 1, 0)
    if avant < int(conditions["avant_au_moins"]):
        return False
    motifs = frozenset(conditions["interruptions"])
    conges: dict[int, float] = {}
    for ligne in carriere.lignes:
        if ligne.type_periode in motifs:
            conges[ligne.annee] = min(1.0, conges.get(ligne.annee, 0.0) + ligne.fraction_annee)
    activite = carriere.trimestres_par_annee(
        [ligne for ligne in carriere.lignes if ligne.type_periode == "emploi"])
    debuts = [annee if mois <= 6 else annee + 1] if au_mois else [annee, annee + 1]
    for debut in debuts:
        duree = 0.0
        premiere = None
        for an in range(debut, debut + 3):
            part = conges.get(an, 0.0)
            if part > 0:
                duree += part
                premiere = an if premiere is None else premiere
        if (premiere is None
                or duree + 1e-9 < float(conditions["interruption_au_moins_annees"])):
            return False
        anterieure = somme_ordonnee(trimestres for an, trimestres in activite.items()
                                    if an < premiere)
        if anterieure < int(conditions["activite_au_moins"]):
            return False
    return True


def age_du_fonctionnaire_parent_de_trois_enfants(moteur: ScenarioActuel, regime: str,
                                                 carriere: Carriere) -> float | None:
    """L'âge que la loi n° 2010-1330, article 28, III, donne pour borne à l'âge
    d'annulation de la décote du fonctionnaire de ``regime`` — « ne peut être
    supérieur à soixante-cinq ans » — quand il est né du 1er juillet 1951 au 31
    décembre 1955, a ses trois enfants et, pour l'un d'eux dont la naissance est
    déclarée, :func:`_remplit_pour_l_enfant_fonctionnaire` ; la CNRACL et les
    ouvriers de l'État de même (décret n° 2003-1306, article 65-3 ; décret
    n° 2004-1056, article 50-3). ``None`` sinon. Que sa limite d'âge ait été de
    soixante-cinq ans, l'appelant le dit (``liquider.decote_opposable``)."""
    regle = _regle_du_parent(moteur, carriere)
    conditions = (regle or {}).get("fonctionnaires")
    if conditions is None or regime not in conditions["regimes"]:
        return None
    return (float(regle["age"]) if _pour_un_enfant_declare(
        carriere, lambda naissance: _remplit_pour_l_enfant_fonctionnaire(
            carriere, conditions, naissance))
        else None)


def taux_plein_par_categorie(moteur: ScenarioActuel, regime: str, carriere: Carriere,
                             durees, age_liquidation: float) -> str | None:
    """La fiche de la catégorie de L. 351-8 qui donne à l'assuré le taux plein
    dans ``regime``, à la date d'effet de sa pension — le taux de soixante-cinq
    ans avant le 1er avril 1983, ce que la décote nulle rend dans les deux cas
    —, ou ``None``. ``durees`` est la durée que le relevé compte
    (:class:`~.compter.Durees`)."""
    date = date_d_effet(carriere)
    if date is None or not carriere.titres_au_taux_plein:
        return None
    for nom in FICHES_DES_CATEGORIES:
        regle = moteur.fiches_datees.regle(nom, date)
        if (regle and regle.get("existe") and regime in regle["regimes"]
                and remplit(moteur, nom, regle, carriere, durees, age_liquidation)):
            return nom
    return None
