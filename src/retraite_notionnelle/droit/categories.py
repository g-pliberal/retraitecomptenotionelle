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

Son jumeau est ``moteur/js/droit/categories.js``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .commun import date_d_effet

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
