"""La chronologie datée et le réseau de personnes : ``chronologie.py``.

``docs/architecture.md``, § 5 et contrat C.1. Ce que la personne déclare
devient des faits datés ; les présomptions posent ce qu'elle ne dit pas, en
leur nom (§ 5.6) ; la carrière du moteur en est la vue. Ce test tient les
trois temps, et le contrat sur des chronologies de chaque sorte de saisie.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle import chronologie
from retraite_notionnelle.carriere import LigneRelevee, Metier
from retraite_notionnelle.noyau import vocabulaire

PARCOURS = dict(
    annee_naissance=1965, sexe="F", mois_naissance=3, age_liquidation=64.25,
    metiers=[Metier("salarie_prive", 22.5, 0.9),
             Metier("fonctionnaire_etat", 30.0, 1.1),
             Metier("profession_liberale", 40.0, 0.3, cumul=True, age_fin=45.0)],
    interruptions={1996: "chomage_indemnise", 1992: "maternite"},
    nombre_enfants=2, part_primes=0.2,
)


def _complete(**modifications) -> dict:
    return chronologie.completer(chronologie.du_parcours(**{**PARCOURS, **modifications}))


def test_un_parcours_devient_des_faits_dates():
    """Un fait par métier, daté au mois et borné [début, fin) ; les métiers
    principaux bout à bout jusqu'au départ, l'activité cumulée à côté ; une
    année d'interruption par motif ; la naissance et le départ déclarés."""
    brute = chronologie.du_parcours(**PARCOURS)
    faits = {f["id"]: f for f in brute["faits"]}
    assert faits["naissance_assure"]["debut"] == "1965-03-01"
    assert faits["naissance_assure"]["attributs"] == {"sexe": "F", "precision": "mois"}
    assert (faits["emploi_1"]["debut"], faits["emploi_1"]["fin"]) == ("1987-09-01", "1995-03-01")
    assert (faits["emploi_2"]["debut"], faits["emploi_2"]["fin"]) == ("1995-03-01", "2029-06-01")
    assert (faits["cumul_1"]["debut"], faits["cumul_1"]["fin"]) == ("2005-03-01", "2010-03-01")
    assert faits["cumul_1"]["attributs"]["cumul"] is True
    assert [f["id"] for f in brute["faits"] if f["sorte"] == "periode_d_interruption"] == [
        "interruption_1992", "interruption_1996"]
    assert faits["depart_assure"]["debut"] == "2029-06-01"
    assert faits["depart_assure"]["attributs"]["age"] == 64.25
    assert all(f["origine"] == "declare" for f in brute["faits"])


def test_les_enfants_sont_des_personnes_liees():
    """Chaque enfant déclaré est une personne du réseau, reliée à l'assurée
    par une filiation ; sa date, inconnue, attend la présomption."""
    brute = chronologie.du_parcours(**PARCOURS)
    assert chronologie.enfants(brute, "assure") == ["enfant_1", "enfant_2"]
    filiation = brute["liens"][0]
    assert filiation["roles"] == {"assure": "mere", "enfant_1": "enfant"}
    assert filiation["debut"] is None
    assert chronologie.naissance(brute, "enfant_1") is None


def test_la_presomption_pose_la_naissance_des_enfants_en_son_nom():
    """Aux trente ans de l'assurée — la valeur du vocabulaire —, chaque
    enfant dont la date n'est pas déclarée ; la filiation commence là. Le
    fait présumé nomme sa présomption, et la chronologie la liste."""
    complete = _complete()
    age = vocabulaire.presomptions()["naissance_des_enfants"]["valeur"]
    assert age == 30
    for enfant in ("enfant_1", "enfant_2"):
        ne = chronologie.naissance(complete, enfant)
        assert ne["debut"] == "1995-03-01"
        assert (ne["origine"], ne["presomption"], ne["fiabilite"]) == (
            "presume", "naissance_des_enfants", "estimee")
    assert all(l["debut"] == "1995-03-01" for l in complete["liens"])
    assert chronologie.presomptions_employees(complete) == ["naissance_des_enfants"]
    assert chronologie.presomptions_employees(_complete(nombre_enfants=0)) == []


def test_un_fait_declare_n_est_jamais_remplace():
    """Une naissance déclarée reste la sienne ; compléter deux fois ne
    change rien."""
    brute = chronologie.du_parcours(**PARCOURS)
    brute["faits"].append(chronologie.fait("naissance_enfant_1", "enfant_1", "naissance",
                                           "1993-07-14"))
    complete = chronologie.completer(brute)
    assert chronologie.naissance(complete, "enfant_1")["origine"] == "declare"
    assert complete["liens"][0]["debut"] == "1993-07-14"
    assert chronologie.naissance(complete, "enfant_2")["origine"] == "presume"
    assert chronologie.completer(complete) == complete


def test_completer_ne_touche_pas_a_la_chronologie_declaree():
    brute = chronologie.du_parcours(**PARCOURS)
    avant = repr(brute)
    chronologie.completer(brute)
    assert repr(brute) == avant


@pytest.mark.parametrize("saisie", ["parcours", "releve", "resume"])
def test_chaque_saisie_donne_une_chronologie_qui_suit_le_contrat(saisie):
    """Complétée, une chronologie n'a ni erreur ni manque au contrat C.1, et
    tient ses liens : une naissance par personne liée, une filiation qui
    commence à la naissance de l'enfant."""
    if saisie == "parcours":
        brute = chronologie.du_parcours(**PARCOURS)
    elif saisie == "releve":
        brute = chronologie.du_releve(
            1962, "H", [LigneRelevee(1984, "salarie_prive", 9000.0, 4),
                        LigneRelevee(1985, "salarie_prive", 3000.0, None, "chomage_indemnise"),
                        LigneRelevee(1985, "artisan", 2000.0)],
            age_liquidation=63.0, nombre_enfants=1)
    else:
        brute = chronologie.du_resume(1970, "F", 6, None, 3)
    assert chronologie.controler(chronologie.completer(brute)) == []


def test_le_releve_garde_ses_lignes_et_leur_ordre():
    """Une ligne, un fait d'une année civile ; une interruption garde son
    statut, son revenu de référence et son motif ; les trimestres portés
    font foi, et leur absence se dit."""
    brute = chronologie.du_releve(
        1962, "H", [LigneRelevee(1984, "salarie_prive", 9000.0, 4),
                    LigneRelevee(1985, "salarie_prive", 3000.0, None, "chomage_indemnise")],
        age_liquidation=63.0)
    lignes = chronologie.periodes(brute, "assure")
    assert [(l["sorte"], l["debut"], l["fin"]) for l in lignes] == [
        ("periode_d_activite", "1984-01-01", "1985-01-01"),
        ("periode_d_interruption", "1985-01-01", "1986-01-01")]
    assert lignes[0]["attributs"]["trimestres"] == 4
    assert lignes[1]["attributs"] == {"affiliation": "salarie_prive", "revenu": 3000.0,
                                      "trimestres": None, "part_primes": 0.0,
                                      "motif": "chomage_indemnise"}


def test_les_controles_du_parcours_passent_a_la_chronologie():
    """Les métiers se suivent, le premier n'est pas cumulé, rien ne dépasse
    le départ : les mêmes refus, avec les mêmes mots."""
    with pytest.raises(ValueError, match="au moins un métier"):
        chronologie.du_parcours(**{**PARCOURS, "metiers": []})
    with pytest.raises(ValueError, match="ne peut pas commencer par elle"):
        chronologie.du_parcours(**{**PARCOURS, "metiers": [Metier("artisan", 20, cumul=True)]})
    with pytest.raises(ValueError, match="doivent se suivre"):
        chronologie.du_parcours(**{**PARCOURS, "metiers": [Metier("artisan", 30),
                                                           Metier("salarie_prive", 25)]})
    with pytest.raises(ValueError, match="au plus tard à la liquidation"):
        chronologie.du_parcours(**{**PARCOURS, "metiers": [
            Metier("salarie_prive", 22), Metier("artisan", 40, cumul=True, age_fin=70)]})


def test_le_controle_trouve_ce_qui_ne_tient_pas():
    complete = _complete()
    complete["faits"].append(dict(complete["faits"][0]))
    complete["liens"][0]["debut"] = "2001-01-01"
    complete["liens"].append(chronologie.lien("filiation_x", "assure", "inconnu", "filiation",
                                              {"assure": "mere", "inconnu": "enfant"},
                                              "2001-01-01"))
    erreurs = chronologie.controler(complete)
    assert any("deux faits portent l'identifiant naissance_assure" in e for e in erreurs), erreurs
    assert any("filiation_enfant_1 : la filiation commence" in e for e in erreurs), erreurs
    assert any("inconnu n'a pas de naissance" in e for e in erreurs), erreurs
