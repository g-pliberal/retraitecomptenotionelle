"""Ce que la saisie du portage lit d'une adresse forgée, et ce qu'elle en
réécrit (action 161, étape 6).

La relecture de ``saisie.py`` contre son portage, au retrait du Python, a
laissé au portage deux défauts que ses lectures font voir : une naissance que
le calendrier ne sait pas dater le faisait échouer lui-même, au lieu du refus
que la saisie lui oppose ; l'adresse réécrite ne gardait que six chiffres
significatifs de chaque nombre. Le troisième, ``DEFAUTS.demandes``, que rien
ne gelait, ne se voit que de node (``tests/js/saisie.test.js``).
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.web.site import ErreurSite, disponible, module, site

from outils_pont import refus_de_la_saisie, saisie_du_portage

#: La saisie se lit par node : sans lui, rien ne se lit.
pytestmark = pytest.mark.skipif(not disponible(),
                                reason="node absent : la saisie du portage ne se lit pas sans lui")

#: Ce que le calendrier ne sait pas dater, et le refus que chacun reçoit : une
#: année si grande que ses mois dépassent le plus grand nombre — le rang d'un
#: mois est l'année fois douze —, un mois hors de l'année.
INDATABLES = [
    ({"naissance": "1e308"}, "Année de naissance hors du champ du modèle"),
    ({"naissance": "-1e308"}, "Année de naissance hors du champ du modèle"),
    ({"naissance": "1975", "naissance_mois": "13"}, "Mois de naissance attendu entre 1 et 12"),
    ({"naissance": "1975", "naissance_mois": "0"}, "Mois de naissance attendu entre 1 et 12"),
]


def _lue(requete: dict, tolerante: bool):
    """La saisie lue comme la page la lit : ``tolerante``, sans rien vérifier,
    pour remontrer une saisie refusée."""
    return module("saisie").Saisie.depuis_requete(
        requete, tolerante, site().contexte.paquet.presomptions)


@pytest.mark.parametrize("tolerante", [False, True], ids=["verifiee", "tolerante"])
@pytest.mark.parametrize("requete, refus", INDATABLES)
def test_une_naissance_que_le_calendrier_ne_date_pas_est_refusee(requete, refus, tolerante):
    """« naissance=1e308 » faisait lever au calendrier sa propre erreur, « mois
    attendu entre 1 et 12, reçu NaN », et la page disait « Le calcul a échoué »
    au lieu du refus : l'année, que rien n'avait vérifiée, se datait d'abord ;
    son jour, présumé au 15 (``jour_de_naissance``), compte les âges du mois
    suivant, et le rang de ce mois passait le plus grand nombre. Un mois de
    naissance hors de l'année tombait de même au premier mois daté. Lue sans
    rien vérifier, pour être remontrée, une telle naissance ne se lit pas
    davantage : la page repart alors de ses défauts, sous le refus."""
    with pytest.raises(ErreurSite, match=refus_de_la_saisie(refus)):
        _lue(requete, tolerante)


#: Chaque âge que la saisie lit, et ce qu'il lui faut autour pour se lire.
AGES = {
    "debut": {}, "liquidation": {}, "progressive": {"quotite": "50"},
    "emploi_retraite": {}, "emploi_retraite_fin": {"emploi_retraite": "2040-01"},
    "invalidite": {}, "radiation_invalidite": {}, "handicap": {},
    "demande_regime_general": {},
    "metier2_debut": {"metier2_statut": "salarie_prive_cadre", "metier2_salaire": "3000"},
    "etranger1_debut": {"etranger1_pays": "DE", "etranger1_fin": "2000-01"},
    "pension_etrangere1_debut": {"pension_etrangere1_pays": "DE", "pension_etrangere1": "100"},
}


@pytest.mark.parametrize("valeur", ["1e308", "-1e308"])
@pytest.mark.parametrize("champ", AGES)
def test_un_age_que_le_calendrier_ne_date_pas_est_refuse(champ, valeur):
    """Un âge d'avant le calendrier, en années — « invalidite=1e308 » —, que le
    calendrier ne date pas, faisait lever de même son erreur dans sept champs,
    au mois qu'il en tirait (``dateDe``) avant d'en vérifier les bornes. Il se
    refuse où il entre, en nommant son champ."""
    with pytest.raises(ErreurSite, match=refus_de_la_saisie(
            f"« {champ} » : âge hors du calendrier \\(reçu : {valeur}\\)")):
        saisie_du_portage({"naissance": "1975-03-15", **AGES[champ], champ: valeur})


@pytest.mark.parametrize("annee", ["1e21", "1e23", "1e308"])
def test_l_annee_refusee_se_cite_telle_que_l_adresse_la_porte(annee):
    """« naissance=1e21 » se citait « 1e+21 », l'écriture de JavaScript à
    partir de vingt-deux chiffres. En chiffres, comme le Python citait l'entier
    lu, 1e23 se citerait 99999999999999991611392, le flottant le plus proche,
    et 1e308 de trois cent neuf chiffres : l'année se cite telle qu'elle a été
    écrite."""
    with pytest.raises(ErreurSite, match=refus_de_la_saisie(
            f"hors du champ du modèle : {annee}\\. ")):
        saisie_du_portage({"naissance": annee})
