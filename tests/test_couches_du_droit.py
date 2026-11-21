"""Les deux droits contrefactuels du scénario 1 sont des piles de couches
(note de décision 0009, étape 2, troisième session ; action 191).

« Un scénario qui garde une loi passée est une couche » : chaque couche écarte
une réforme, et garde, dans chaque fiche que cette réforme a réécrite, la
version d'avant, depuis la date d'effet de la réforme (« remplacer une
version », ``docs/architecture.md``, § 4.8 et annexe C.4). La pile se résout
à la fabrication : le paquet porte, sous chaque droit, la fiche résolue.

Les âges attendus sont ceux des textes gardés : « fixé à soixante-deux ans
pour les assurés nés à compter du 1er janvier 1955 » (L. 161-17-2, loi
n° 2011-1906, LEGIARTI000025014605) ; « soixante-quatre ans pour les assurés
nés à compter du 1er janvier 1968 » (loi n° 2023-270, LEGIARTI000047452768).
"""

from __future__ import annotations

import json
import re
from datetime import date

import pytest

import outils_droit_date as outils
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees import droits_contrefactuels as droits
from retraite_notionnelle.donnees import tables_du_droit
from retraite_notionnelle.donnees.tables_du_droit import FichesDatees
from retraite_notionnelle.noyau import carte, univers

AGE_LEGAL = "age_legal_par_generation"
EFFET = "liquidation.date_effet"


def _fiche(versions: list[tuple[str, str | None, str | None]]) -> dict:
    return {"id": "de_poche", "dates_qui_decident": [EFFET],
            "versions": [{"id": nom, "bornes": {EFFET: [debut, fin]}, "exception_de": None,
                          "parametres": {"age": rang}}
                         for rang, (nom, debut, fin) in enumerate(versions)]}


def test_garder_la_version_d_avant_la_prolonge_et_ote_les_suivantes():
    """Une fiche de poche à trois versions : écarter la réforme du 1er
    septembre 2023 garde la deuxième sans fin, et ôte ce qui la suit."""
    fiche = _fiche([("a", None, "2011-07-01"), ("b", "2011-07-01", "2023-09-01"),
                    ("c", "2023-09-01", "2026-09-01"), ("d", "2026-09-01", None)])
    gardee = droits.garder_la_version_d_avant(fiche, date(2023, 9, 1))
    assert [(v["id"], v["bornes"][EFFET]) for v in gardee["versions"]] == [
        ("a", [None, "2011-07-01"]), ("b", ["2011-07-01", None])]
    # La fiche du droit réel reste intacte.
    assert fiche["versions"][1]["bornes"][EFFET] == ["2011-07-01", "2023-09-01"]


def test_une_couche_ne_remplace_que_la_version_d_une_fiche_que_sa_reforme_a_reecrite():
    """Aucune version ne commence à la date de la réforme : la fiche n'a pas
    été réécrite ce jour-là, et la couche qui dit la remplacer se trompe."""
    fiche = _fiche([("a", None, "2011-07-01"), ("b", "2011-07-01", None)])
    with pytest.raises(ValueError, match="de_poche : aucune version ne commence le 2023-09-01"):
        droits.garder_la_version_d_avant(fiche, date(2023, 9, 1))


def test_chaque_droit_contrefactuel_est_une_pile_de_couches_qui_tiennent():
    assert univers.controler() == []
    couches = univers.couches()
    assert set(droits.DROITS) == {"loi_2023_sans_suspension", "au_31_aout_2023"}
    for droit, pile in droits.DROITS.items():
        assert pile and all(nom in couches for nom in pile), droit
    # Le droit au 31 août 2023 écarte aussi la suspension, posée sur la loi de 2023.
    assert droits.DROITS["au_31_aout_2023"][:-1] == droits.DROITS["loi_2023_sans_suspension"]


@pytest.mark.parametrize("couche, reforme, nombre", [
    ("sans_la_reforme_de_2023", "reforme_2023", 19),
    ("sans_la_suspension_de_2026", "lfss_2026_suspension", 12),
])
def test_chaque_fiche_qui_declare_la_reforme_est_gardee_ou_declaree_hors_de_la_couche(
        couche, reforme, nombre):
    """« La liste des fiches se calcule depuis leur champ ``reformes`` :
    chacune est gardée, ou déclarée hors de la couche avec sa raison, pour que
    rien n'y reste par oubli » (second rectificatif de la note 0009)."""
    brute = univers.couches()[couche]
    assert brute["ecarte"] == [reforme]
    declarent = {nom for nom, fiche in carte.fiches().items()
                 if reforme in (fiche.get("reformes") or ())}
    assert len(declarent) == nombre
    assert droits.fiches_sans_decision(brute) == []
    decidees = {o["vise"]: o for o in brute["operations"]}
    assert set(decidees) == declarent, "la couche ne décide que des fiches de sa réforme"
    # L'âge légal, la durée requise, la carrière longue, et sous la loi de 2023
    # l'âge du taux plein qui lit l'âge légal (étape 3 de la note 0009),
    # gardent leur version d'avant ; le reste dit pourquoi.
    gardees = {"sans_la_reforme_de_2023": ["age_annulation_decote", AGE_LEGAL,
                                           "carriere_longue",
                                           "duree_requise_par_generation"],
               "sans_la_suspension_de_2026": [AGE_LEGAL, "carriere_longue",
                                              "duree_requise_par_generation"]}[couche]
    assert sorted(n for n, o in decidees.items()
                  if o["operation"] == "remplacer_une_version") == gardees
    for nom, operation in decidees.items():
        assert operation["operation"] in ("remplacer_une_version", "garder"), nom
        assert len(str(operation.get("motif") or "").split()) >= 5, f"{nom} : sa raison"


def test_une_fiche_qui_declare_la_reforme_sans_etre_decidee_fait_echouer():
    brute = univers.couches()["sans_la_reforme_de_2023"]
    amputee = {**brute, "operations": [o for o in brute["operations"]
                                       if o["vise"] != "surcote_parentale"]}
    assert droits.fiches_sans_decision(amputee) == ["surcote_parentale"]


def test_la_date_de_chaque_couche_est_celle_que_le_moteur_ecarte():
    """Le portage nomme chaque droit contrefactuel avec la date de la couche
    du haut de sa pile (``DROITS_CONTREFACTUELS``) ; la carrière longue n'y
    lit plus rien depuis l'étape 3 de la note 0009 : sa couche la remplace."""
    source = (outils.RACINE / "moteur" / "js" / "scenario-actuel.js").read_text(encoding="utf-8")
    for droit, pile in droits.DROITS.items():
        depuis = univers.couches()[pile[-1]]["depuis"]
        assert depuis["date"] == EFFET
        annee, mois = re.search(rf"{droit}: \[(\d+), (\d+)\]", source).groups()
        assert depuis["valeur"] == date(int(annee), int(mois), 1)


def _age(fiche: dict, jour: str, generation: float) -> float | None:
    """L'âge de la version qui vaut ce jour-là, lu à la main dans la fiche
    préparée : la ligne de la génération."""
    for version in fiche["versions"]:
        debut, fin = version["bornes"][EFFET]
        if (debut is None or debut <= jour) and (fin is None or jour < fin):
            for bas, haut, age, _ in version.get("table") or ():
                if generation >= bas and (haut is None or generation < haut):
                    return age
            return version["parametres"].get("age")
    return None


def test_le_paquet_porte_l_age_legal_resolu_sous_chaque_droit():
    paquet = droits.pour_le_paquet(FichesDatees(RACINE_DONNEES).fiches())
    au_31_aout = paquet["au_31_aout_2023"]["fiches"][AGE_LEGAL]
    sans_suspension = paquet["loi_2023_sans_suspension"]["fiches"][AGE_LEGAL]
    assert [v["id"] for v in au_31_aout["versions"]][-1] == "loi_de_2011"
    assert au_31_aout["versions"][-1]["bornes"][EFFET] == ["2011-12-23", None]
    assert [v["id"] for v in sans_suspension["versions"]][-1] == "loi_de_2023"
    assert sans_suspension["versions"][-1]["bornes"][EFFET] == ["2023-09-01", None]
    # Soixante-deux ans dès 1955, soixante-quatre dès 1968 : les textes gardés.
    assert _age(au_31_aout, "2030-01-01", 1968.0) == 62.0
    assert _age(au_31_aout, "2030-01-01", 1955.0) == 62.0
    assert _age(sans_suspension, "2032-01-01", 1968.0) == 64.0
    assert _age(sans_suspension, "2027-01-01", 1964.0) == 63.0
    assert paquet["au_31_aout_2023"]["couches"] == list(droits.DROITS["au_31_aout_2023"])


def test_les_deux_copies_de_l_age_legal_sont_parties():
    legislation = RACINE_DONNEES / "reference" / "legislation"
    assert not (legislation / "age_ouverture_avant_reforme_2023.csv").exists()
    assert not (legislation / "age_ouverture_avant_suspension.csv").exists()
    assert not hasattr(tables_du_droit, "AgesOuvertureAvantReforme2023")
    assert not hasattr(tables_du_droit, "AgesOuvertureAvantSuspension")
    paquet = json.loads((outils.RACINE / "moteur" / "donnees.json").read_text(encoding="utf-8"))
    assert "ages_ouverture_avant_reforme_2023" not in paquet
    assert "ages_ouverture_avant_suspension" not in paquet
    assert set(paquet["droits_contrefactuels"]) == set(droits.DROITS)
