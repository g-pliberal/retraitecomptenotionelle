"""La chronologie datée et le réseau de personnes : ``chronologie.py``.

``docs/architecture.md``, § 5 et contrat C.1. Ce que la personne déclare
devient des faits datés ; les présomptions posent ce qu'elle ne dit pas, en
leur nom (§ 5.6) ; la carrière du moteur en est la vue. Ce test tient les
trois temps, et le contrat sur des chronologies de chaque sorte de saisie.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle import chronologie
from retraite_notionnelle.carriere import Carriere, LigneRelevee, Metier
from retraite_notionnelle.droit import compter
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
    année d'interruption par motif ; le départ déclaré, et la naissance
    déclarée au mois, dont la présomption pose le jour. Née le 15 mars 1965,
    l'assurée commence ses métiers dans le mois de ses âges, et part au premier
    mois où elle a 64 ans et 3 mois révolus : juillet 2029."""
    brute = chronologie.du_parcours(**PARCOURS)
    faits = {f["id"]: f for f in brute["faits"]}
    assert faits["naissance_assure"]["debut"] == "1965-03-15"
    assert faits["naissance_assure"]["attributs"] == {"sexe": "F", "precision": "mois"}
    assert (faits["emploi_1"]["debut"], faits["emploi_1"]["fin"]) == ("1987-09-01", "1995-03-01")
    assert (faits["emploi_2"]["debut"], faits["emploi_2"]["fin"]) == ("1995-03-01", "2029-07-01")
    assert (faits["cumul_1"]["debut"], faits["cumul_1"]["fin"]) == ("2005-03-01", "2010-03-01")
    assert faits["cumul_1"]["attributs"]["cumul"] is True
    assert [f["id"] for f in brute["faits"] if f["sorte"] == "periode_d_interruption"] == [
        "interruption_1992", "interruption_1996"]
    assert faits["depart_assure"]["debut"] == "2029-07-01"
    assert faits["depart_assure"]["attributs"]["age"] == 64.25
    assert all(f["origine"] == "declare" for f in brute["faits"]
               if f["id"] != "naissance_assure")
    assert faits["naissance_assure"]["presomption"] == "jour_de_naissance"


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
    fait présumé nomme sa présomption, et la chronologie la liste. L'assurée,
    dont le jour est présumé le 15, a ses enfants le 15."""
    complete = _complete()
    age = vocabulaire.presomptions()["naissance_des_enfants"]["valeur"]
    assert age == 30
    for enfant in ("enfant_1", "enfant_2"):
        ne = chronologie.naissance(complete, enfant)
        assert ne["debut"] == "1995-03-15"
        assert (ne["origine"], ne["presomption"], ne["fiabilite"]) == (
            "presume", "naissance_des_enfants", "estimee")
    assert all(l["debut"] == "1995-03-15" for l in complete["liens"])
    assert chronologie.presomptions_employees(complete) == [
        "jour_de_naissance", "naissance_des_enfants"]
    assert chronologie.presomptions_employees(_complete(nombre_enfants=0)) == [
        "jour_de_naissance"]
    assert chronologie.presomptions_employees(
        _complete(nombre_enfants=0, jour_naissance=15)) == []


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


def test_le_conjoint_et_le_deces_suivent_le_contrat():
    """Le conjoint est une personne, née, que le mariage relie à l'assuré ; le
    décès de l'assuré clôt ce mariage. Sans date déclarée, le mariage est
    présumé aux vingt-sept ans de l'assuré, au nom de sa présomption — au jour
    de son anniversaire, le 15 faute de jour dit."""
    brute = chronologie.du_resume(
        1960, "H", 5, 64.0, 0, conjoint={"naissance": "1962-03", "sexe": "F",
                                         "mariage": None, "ressources": 9000.0},
        deces="2031-10")
    complete = chronologie.completer(brute)
    assert chronologie.controler(complete) == []
    union = chronologie.union(complete, chronologie.ASSURE)
    assert (union["forme"], union["debut"], union["fin"]) == (
        "mariage", "1987-05-15", {"date": "2031-10-01", "cause": "deces"})
    assert union["presomption"] == "mariage_des_conjoints"
    assert chronologie.conjoint(complete, chronologie.ASSURE) == chronologie.CONJOINT
    assert chronologie.deces(complete, chronologie.ASSURE)["debut"] == "2031-10-01"
    assert chronologie.ressources(complete, chronologie.CONJOINT) == 9000.0
    assert chronologie.presomptions_employees(complete) == [
        "jour_de_naissance", "mariage_des_conjoints"]


def test_le_menage_du_survivant_est_un_fait_de_ses_ressources():
    """Ce que le plafond de la réversion lit du survivant : la part de ses
    ressources que lui rapporte son activité, et le ménage où il vit après le
    décès — la forme de son union, une du vocabulaire, et ce que son nouveau
    conjoint y apporte, quand il le dit. Ce sont des faits de ses ressources, à
    la date du décès comme elles ; ni l'un ni l'autre ne se présume."""
    from retraite_notionnelle.noyau import vocabulaire

    assert set(chronologie.FORMES_D_UNION) == vocabulaire.liste("formes_d_union")
    conjoint = {"naissance": "1962-03", "sexe": "F", "mariage": None,
                "ressources": 15000.0, "revenus_d_activite": 10000.0,
                "nouvelle_union": "pacs", "ressources_du_nouveau_conjoint": 12000.0}
    complete = chronologie.completer(chronologie.du_resume(
        1960, "H", 5, 64.0, 0, conjoint=conjoint, deces="2031-10"))
    assert chronologie.controler(complete) == []
    assert (chronologie.ressources(complete, chronologie.CONJOINT),
            chronologie.revenus_d_activite(complete, chronologie.CONJOINT),
            chronologie.menage(complete, chronologie.CONJOINT)) == (
        15000.0, 10000.0, ("pacs", 12000.0))
    seul = chronologie.completer(chronologie.du_resume(
        1960, "H", 5, 64.0, 0, conjoint={**conjoint, "nouvelle_union": None,
                                         "ressources_du_nouveau_conjoint": None}))
    assert chronologie.menage(seul, chronologie.CONJOINT) is None
    sans_apport = chronologie.completer(chronologie.du_resume(
        1960, "H", 5, 64.0, 0, conjoint={**conjoint, "ressources_du_nouveau_conjoint": None}))
    assert chronologie.menage(sans_apport, chronologie.CONJOINT) == ("pacs", None)
    with pytest.raises(ValueError, match="mariage, pacs ou concubinage"):
        chronologie.du_resume(1960, "H", 5, 64.0, 0,
                              conjoint={**conjoint, "nouvelle_union": "veuvage"})


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


# -- la carrière, vue de la chronologie ------------------------------------------

@pytest.fixture(scope="module")
def macro():
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.donnees.macro import DonneesMacro

    return DonneesMacro(RACINE_DONNEES)


def test_la_carriere_porte_la_chronologie_dont_elle_est_la_vue(macro):
    """Le parcours passe par la chronologie : la carrière la garde, complétée,
    et en tire sa naissance, son départ et ses enfants."""
    carriere = Carriere.depuis_parcours(macro=macro, **PARCOURS)
    assert carriere.chronologie == _complete()
    assert (carriere.annee_naissance, carriere.mois_naissance, carriere.sexe) == (1965, 3, "F")
    assert (carriere.age_liquidation, carriere.nombre_enfants) == (64.25, 2)
    assert carriere.naissances_des_enfants == (("enfant_1", "1995-03-15"),
                                               ("enfant_2", "1995-03-15"))
    assert carriere.date_entree("fonctionnaire_etat").mois == 3


def test_une_carriere_construite_ligne_a_ligne_recoit_sa_chronologie():
    """Sans périodes : sa naissance, ses enfants et son départ, et les
    présomptions qui les complètent."""
    carriere = Carriere(annee_naissance=1980, sexe="F", nombre_enfants=3, age_liquidation=64.0)
    assert chronologie.enfants(carriere.chronologie, "assure") == ["enfant_1", "enfant_2", "enfant_3"]
    assert {naissance for _, naissance in carriere.naissances_des_enfants} == {"2010-01-15"}
    assert Carriere(annee_naissance=1980, sexe="H").naissances_des_enfants == ()


def test_une_naissance_declaree_remplace_la_presomption(macro):
    """La présomption n'est qu'un défaut : une naissance déclarée prend sa
    place, et le moteur la lit."""
    brute = chronologie.du_parcours(**PARCOURS)
    for enfant in ("enfant_1", "enfant_2"):
        brute["faits"].append(chronologie.fait(f"naissance_{enfant}", enfant, "naissance",
                                               "2002-05-01"))
    carriere = Carriere.depuis_chronologie(chronologie.completer(brute), macro)
    assert carriere.naissances_des_enfants == (("enfant_1", "2002-05-01"),
                                               ("enfant_2", "2002-05-01"))
    assert chronologie.presomptions_employees(carriere.chronologie) == ["jour_de_naissance"]


def test_chaque_enfant_garde_sa_date(macro):
    """Une naissance déclarée, une présumée, à des années différentes : le
    moteur lit chacune, et n'en choisit aucune pour tous (domaine « les dates
    des enfants », § 11)."""
    brute = chronologie.du_parcours(**PARCOURS)
    brute["faits"].append(chronologie.fait("naissance_enfant_1", "enfant_1", "naissance",
                                           "1993-07-14"))
    carriere = Carriere.depuis_chronologie(chronologie.completer(brute), macro)
    assert carriere.naissances_des_enfants == (("enfant_1", "1993-07-14"),
                                               ("enfant_2", "1995-03-15"))
    assert chronologie.presomptions_employees(carriere.chronologie) == [
        "jour_de_naissance", "naissance_des_enfants"]


def test_la_saisie_declare_la_naissance_des_premiers_enfants(macro):
    """Une année, un mois ou un jour, pour les premiers enfants dans l'ordre ;
    le fait dit sa précision, la filiation commence avec lui, et la
    présomption ne pose que les naissances qui manquent. La carrière les
    retrouve, et les copies de travail les gardent."""
    brute = chronologie.du_parcours(**{**PARCOURS, "nombre_enfants": 3},
                                    naissances_enfants=["1990", "1993-06"])
    faits = {f["id"]: f for f in brute["faits"]}
    assert (faits["naissance_enfant_1"]["debut"],
            faits["naissance_enfant_1"]["attributs"]) == ("1990-01-01", {"precision": "annee"})
    assert (faits["naissance_enfant_2"]["debut"],
            faits["naissance_enfant_2"]["attributs"]) == ("1993-06-01", {"precision": "mois"})
    assert "naissance_enfant_3" not in faits
    assert [l["debut"] for l in brute["liens"]] == ["1990-01-01", "1993-06-01", None]
    complete = chronologie.completer(brute)
    assert chronologie.controler(complete) == []
    carriere = Carriere.depuis_parcours(macro=macro, **{**PARCOURS, "nombre_enfants": 3},
                                        naissances_enfants=["1990", "1993-06"])
    assert carriere.naissances_des_enfants == (
        ("enfant_1", "1990-01-01"), ("enfant_2", "1993-06-01"), ("enfant_3", "1995-03-15"))
    assert carriere.naissances_enfants == ("1990-01-01", "1993-06-01")
    assert carriere.avec_lignes(carriere.lignes).naissances_des_enfants == carriere.naissances_des_enfants
    ligne_a_ligne = Carriere(annee_naissance=1965, sexe="F", nombre_enfants=2,
                             naissances_enfants=("1991-02-03",), age_liquidation=64.0)
    assert ligne_a_ligne.naissances_des_enfants == (("enfant_1", "1991-02-03"),
                                                    ("enfant_2", "1995-01-15"))


@pytest.mark.parametrize("naissances, message", [
    (["95"], "attendue en AAAA, AAAA-MM ou AAAA-MM-JJ"),
    (["1995-6"], "attendue en AAAA, AAAA-MM ou AAAA-MM-JJ"),
    (["1995-13"], "impossible"),
    (["1987-02-29"], "impossible"),
    (["1990", "1991", "1992"], "3 naissances d'enfants déclarées pour 2 enfants"),
    (["1960"], "avant son parent"),
])
def test_une_naissance_mal_declaree_est_refusee(naissances, message):
    with pytest.raises(ValueError, match=message):
        chronologie.du_parcours(**PARCOURS, naissances_enfants=naissances)


def test_les_copies_de_travail_gardent_leur_chronologie(macro):
    carriere = Carriere.depuis_parcours(macro=macro, **PARCOURS)
    assert carriere.avec_lignes(carriere.lignes).chronologie is carriere.chronologie
    assert carriere.prolongee(66.0, macro).chronologie is carriere.chronologie


def test_un_releve_et_un_parcours_ne_se_melent_pas(macro):
    brute = chronologie.du_parcours(**PARCOURS)
    brute["faits"].insert(1, chronologie.fait("releve_1", "assure", "periode_d_activite",
                                              "1985-01-01", "1986-01-01",
                                              {"affiliation": "salarie_prive", "revenu": 1.0,
                                               "trimestres": None, "part_primes": 0.0}))
    with pytest.raises(ValueError, match="mêle un relevé et un parcours"):
        Carriere.depuis_chronologie(chronologie.completer(brute), macro)


# -- le jour de naissance de l'assuré ----------------------------------------------

def test_le_jour_declare_se_pose_au_jour():
    """Déclaré, le jour de naissance de l'assuré est un fait au jour
    (``precision: jour``), que rien ne présume."""
    faits = {f["id"]: f for f in chronologie.du_parcours(**PARCOURS, jour_naissance=15)["faits"]}
    naissance = faits["naissance_assure"]
    assert naissance["debut"] == "1965-03-15"
    assert naissance["attributs"] == {"sexe": "F", "precision": "jour"}
    assert (naissance["origine"], naissance["fiabilite"]) == ("declare", "haute")
    assert "presomption" not in naissance


def test_le_jour_tu_est_presume_en_son_nom():
    """Tu, il est posé dès la construction par la présomption
    ``jour_de_naissance``, à la valeur du vocabulaire — ou de la table
    qu'on lui donne, celle du paquet côté site ; le fait garde la précision
    de ce qui est déclaré, le mois."""
    valeur = vocabulaire.presomptions()["jour_de_naissance"]["valeur"]
    naissance = chronologie.naissance(chronologie.du_parcours(**PARCOURS), "assure")
    assert naissance["debut"] == f"1965-03-{valeur:02d}"
    assert naissance["attributs"] == {"sexe": "F", "precision": "mois"}
    assert (naissance["origine"], naissance["presomption"], naissance["fiabilite"]) == (
        "presume", "jour_de_naissance", "estimee")
    autre = chronologie.du_parcours(**PARCOURS, presomptions={"jour_de_naissance": {"valeur": 20}})
    assert chronologie.naissance(autre, "assure")["debut"] == "1965-03-20"


def test_un_jour_qui_n_existe_pas_est_refuse():
    with pytest.raises(ValueError, match="naissance impossible : le 30 du mois 2 de 1965"):
        chronologie.du_parcours(**{**PARCOURS, "mois_naissance": 2}, jour_naissance=30)


def test_la_carriere_lit_le_jour_que_la_chronologie_porte(macro):
    """Le jour déclaré revient à la carrière tiré de sa chronologie ; le jour
    présumé n'y est pas déclaré, mais la carrière le lit quand même, et ses
    copies de travail le gardent."""
    declare = Carriere.depuis_parcours(macro=macro, **PARCOURS, jour_naissance=15)
    assert (declare.jour_naissance, declare.jour_de_naissance) == (15, 15)
    assert declare.avec_lignes(declare.lignes).jour_de_naissance == 15
    presume = Carriere.depuis_parcours(macro=macro, **PARCOURS)
    valeur = vocabulaire.presomptions()["jour_de_naissance"]["valeur"]
    assert (presume.jour_naissance, presume.jour_de_naissance) == (None, valeur)
    assert presume.prolongee(66.0, macro).jour_de_naissance == valeur
    ligne_a_ligne = Carriere(annee_naissance=1980, sexe="F", jour_naissance=31)
    assert ligne_a_ligne.jour_de_naissance == 31
    with pytest.raises(ValueError, match="jour de naissance attendu entre 1 et 31"):
        Carriere(annee_naissance=1980, sexe="F", jour_naissance=32)


# -- le portage ------------------------------------------------------------------

SAISIES = [
    {"parcours": {**PARCOURS, "metiers": [
        {"affiliation": m.affiliation, "age_debut": m.age_debut,
         "niveau_salaire": m.niveau_salaire, "cumul": m.cumul, "age_fin": m.age_fin}
        for m in PARCOURS["metiers"]]}},
    {"parcours": {"annee_naissance": 1958, "sexe": "H", "age_liquidation": 62.0,
                  "metiers": [{"affiliation": "agent_sncf", "age_debut": 19.0,
                               "niveau_salaire": 1.0, "cumul": False, "age_fin": None}]}},
    {"parcours": {"annee_naissance": 1990, "sexe": "F", "mois_naissance": 2,
                  "age_liquidation": 64.0, "nombre_enfants": 3,
                  "metiers": [{"affiliation": "salarie_prive", "age_debut": 23.0,
                               "niveau_salaire": 1.0, "cumul": False, "age_fin": None}]}},
    {"parcours": {"annee_naissance": 1970, "sexe": "F", "age_liquidation": 64.0,
                  "metiers": [{"affiliation": "artisan", "age_debut": 20.0,
                               "niveau_salaire": 1.0, "cumul": True, "age_fin": None}]}},
    {"releve": {"annee_naissance": 1962, "sexe": "H", "age_liquidation": 63.0,
                "nombre_enfants": 1, "part_primes": 0.1,
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"},
                           {"annee": 1985, "affiliation": "salarie_prive", "revenu": 3000.0,
                            "trimestres": None, "type_periode": "chomage_indemnise"}]}},
    {"releve": {"annee_naissance": 1962, "sexe": "H", "age_liquidation": 63.0, "releve": []}},
    {"parcours": {"annee_naissance": 1972, "sexe": "F", "age_liquidation": 64.0,
                  "nombre_enfants": 3, "naissances_enfants": ["1999", "2004-11"],
                  "metiers": [{"affiliation": "fonctionnaire_etat", "age_debut": 23.0,
                               "niveau_salaire": 1.0, "cumul": False, "age_fin": None}]}},
    {"releve": {"annee_naissance": 1962, "sexe": "F", "age_liquidation": 63.0,
                "nombre_enfants": 1, "naissances_enfants": ["1990-05-17"],
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"parcours": {"annee_naissance": 1972, "sexe": "F", "age_liquidation": 64.0,
                  "nombre_enfants": 1, "naissances_enfants": ["1999-6"],
                  "metiers": [{"affiliation": "salarie_prive", "age_debut": 23.0,
                               "niveau_salaire": 1.0, "cumul": False, "age_fin": None}]}},
    {"parcours": {"annee_naissance": 1972, "sexe": "F", "age_liquidation": 64.0,
                  "nombre_enfants": 1, "naissances_enfants": ["1999", "2001"],
                  "metiers": [{"affiliation": "salarie_prive", "age_debut": 23.0,
                               "niveau_salaire": 1.0, "cumul": False, "age_fin": None}]}},
    {"releve": {"annee_naissance": 1962, "sexe": "F", "age_liquidation": 63.0,
                "nombre_enfants": 1, "naissances_enfants": ["1987-02-29"],
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"releve": {"annee_naissance": 1962, "sexe": "F", "age_liquidation": 63.0,
                "nombre_enfants": 1, "naissances_enfants": ["1961"],
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    # Le jour de naissance de l'assuré, déclaré : un 15, un 1er, et un 29
    # février qui n'existe pas.
    {"parcours": {"annee_naissance": 1964, "sexe": "H", "mois_naissance": 5,
                  "jour_naissance": 16, "age_liquidation": 62.75,
                  "metiers": [{"affiliation": "salarie_prive", "age_debut": 22.0,
                               "niveau_salaire": 1.0, "cumul": False, "age_fin": None}]}},
    {"releve": {"annee_naissance": 1962, "sexe": "F", "mois_naissance": 1,
                "jour_naissance": 1, "age_liquidation": 63.0,
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"parcours": {"annee_naissance": 1963, "sexe": "H", "mois_naissance": 2,
                  "jour_naissance": 29, "age_liquidation": 64.0,
                  "metiers": [{"affiliation": "salarie_prive", "age_debut": 22.0,
                               "niveau_salaire": 1.0, "cumul": False, "age_fin": None}]}},
    # Le conjoint et le décès, qui ouvrent la réversion : un mariage présumé,
    # puis un mariage déclaré et des ressources, leur part d'activité et le
    # ménage du survivant ; et ce qui ne tient pas.
    {"parcours": {"annee_naissance": 1960, "sexe": "H", "age_liquidation": 64.0,
                  "conjoint": {"naissance": "1962-03", "sexe": "F", "mariage": None,
                               "ressources": None},
                  "deces": "2031-10",
                  "metiers": [{"affiliation": "salarie_prive", "age_debut": 21.0,
                               "niveau_salaire": 1.0, "cumul": False, "age_fin": None}]}},
    {"releve": {"annee_naissance": 1958, "sexe": "F", "age_liquidation": 62.0,
                "nombre_enfants": 1, "naissances_enfants": ["1986"],
                "conjoint": {"naissance": "1955", "sexe": "H", "mariage": "1984-06-16",
                             "ressources": 12000, "revenus_d_activite": 8000,
                             "nouvelle_union": "pacs",
                             "ressources_du_nouveau_conjoint": 15000},
                "deces": "2024-02-11",
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"releve": {"annee_naissance": 1958, "sexe": "F", "age_liquidation": 62.0,
                "conjoint": {"naissance": "1960", "sexe": "H", "mariage": "1959",
                             "ressources": None},
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"releve": {"annee_naissance": 1958, "sexe": "F", "age_liquidation": 62.0,
                "conjoint": {"naissance": "1960", "sexe": "X", "mariage": None,
                             "ressources": None},
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"releve": {"annee_naissance": 1958, "sexe": "F", "age_liquidation": 62.0,
                "conjoint": {"naissance": "1960", "sexe": "H", "mariage": None,
                             "ressources": None, "nouvelle_union": "concubinage"},
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"releve": {"annee_naissance": 1958, "sexe": "F", "age_liquidation": 62.0,
                "conjoint": {"naissance": "1960", "sexe": "H", "mariage": None,
                             "ressources": None, "nouvelle_union": "veuvage"},
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"releve": {"annee_naissance": 1958, "sexe": "F", "age_liquidation": 62.0,
                "conjoint": {"naissance": "1960", "sexe": "H", "mariage": "1990",
                             "ressources": None},
                "deces": "1989-05",
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"releve": {"annee_naissance": 1958, "sexe": "F", "age_liquidation": 62.0,
                "deces": "2024-13",
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    # L'invalidité et l'inaptitude : une pension d'invalidité, l'inaptitude,
    # la radiation pour invalidité d'une fonctionnaire ; et ce qui ne tient pas.
    {"parcours": {"annee_naissance": 1965, "sexe": "H", "age_liquidation": 62.0,
                  "invalidite": {"pension": 55.25, "inaptitude": True, "radiation": None},
                  "interruptions": {str(a): "invalidite" for a in range(2020, 2028)},
                  "metiers": [{"affiliation": "salarie_prive", "age_debut": 21.0,
                               "niveau_salaire": 1.0, "cumul": False, "age_fin": None}]}},
    {"parcours": {"annee_naissance": 1970, "sexe": "F", "mois_naissance": 4,
                  "age_liquidation": 62.0,
                  "invalidite": {"pension": None, "inaptitude": False,
                                 "radiation": {"age": 48.5, "imputable": True, "taux": 65}},
                  "metiers": [{"affiliation": "fonctionnaire_territorial_hospitalier",
                               "age_debut": 22.0, "niveau_salaire": 1.0, "cumul": False,
                               "age_fin": None},
                              {"affiliation": "sans_activite", "age_debut": 48.5,
                               "niveau_salaire": 1.0, "cumul": False, "age_fin": None}]}},
    {"releve": {"annee_naissance": 1962, "sexe": "F", "age_liquidation": 63.0,
                "invalidite": {"pension": 70.0, "inaptitude": False, "radiation": None},
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"releve": {"annee_naissance": 1962, "sexe": "F", "age_liquidation": 63.0,
                "invalidite": {"pension": None, "inaptitude": False,
                               "radiation": {"age": 40.0, "imputable": False, "taux": 120}},
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    # Les carrières hors de France : des périodes, une pension étrangère, la
    # résidence après le départ ; et ce qui ne tient pas.
    {"parcours": {"annee_naissance": 1965, "sexe": "H", "mois_naissance": 6,
                  "age_liquidation": 64.0,
                  "etranger": {"periodes": [{"pays": "MA", "debut": 15.0, "fin": 21.0,
                                             "activite": "salariee"},
                                            {"pays": "OI", "debut": 33.5, "fin": 36.5,
                                             "activite": "non_salariee"}],
                               "pensions": [{"pays": "MA", "age": 67.25, "mensuel": 263.5}],
                               "residence": "PT"},
                  "interruptions": {str(a): "sans_activite" for a in range(1999, 2002)},
                  "metiers": [{"affiliation": "salarie_prive", "age_debut": 21.0,
                               "niveau_salaire": 1.0, "cumul": False, "age_fin": None}]}},
    {"releve": {"annee_naissance": 1962, "sexe": "F", "age_liquidation": 63.0,
                "etranger": {"periodes": [], "pensions": [], "residence": "autre"},
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"releve": {"annee_naissance": 1962, "sexe": "F", "age_liquidation": 63.0,
                "etranger": {"periodes": [{"pays": "DE", "debut": 30.0, "fin": 35.0,
                                           "activite": "salariee"},
                                          {"pays": "AT", "debut": 20.0, "fin": 30.5,
                                           "activite": "salariee"}]},
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"releve": {"annee_naissance": 1962, "sexe": "F", "age_liquidation": 63.0,
                "etranger": {"periodes": [{"pays": "DE", "debut": 30.0, "fin": 35.0,
                                           "activite": None}]},
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"releve": {"annee_naissance": 1962, "sexe": "F", "age_liquidation": 63.0,
                "etranger": {"pensions": [{"pays": None, "age": 66.0, "mensuel": 100}]},
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
    {"releve": {"annee_naissance": 1962, "sexe": "F", "age_liquidation": 63.0,
                "etranger": {"residence": "FR"},
                "releve": [{"annee": 1984, "affiliation": "salarie_prive", "revenu": 9000.0,
                            "trimestres": 4, "type_periode": "emploi"}]}},
]


def _python(saisie: dict) -> dict:
    try:
        if "parcours" in saisie:
            options = dict(saisie["parcours"])
            options["metiers"] = [Metier(**m) for m in options["metiers"]]
            if options.get("interruptions"):
                options["interruptions"] = {int(a): m for a, m in options["interruptions"].items()}
            return {"chronologie": chronologie.completer(chronologie.du_parcours(**options))}
        options = dict(saisie["releve"])
        options["releve"] = [LigneRelevee(**l) for l in options["releve"]]
        return {"chronologie": chronologie.completer(chronologie.du_releve(**options))}
    except ValueError as erreur:
        return {"erreur": str(erreur)}


def test_le_portage_construit_la_meme_chronologie():
    """Les deux moteurs échangent la même donnée (§ 7.1) : pour chaque saisie,
    le JavaScript rend, au JSON près, la chronologie du Python — et refuse ce
    qu'il refuse, avec les mêmes mots."""
    import json
    import shutil
    import subprocess
    import tempfile
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")

    racine = Path(__file__).resolve().parents[1]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(SAISIES, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(racine / "tests" / "js" / "comparer-chronologie.mjs"), chemin],
            cwd=racine, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr
    obtenus = json.loads(execution.stdout)
    attendus = [json.loads(json.dumps(_python(saisie))) for saisie in SAISIES]
    assert len(obtenus) == len(attendus)
    for numero, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        assert obtenu == attendu, f"saisie {numero}"


def test_le_moteur_lit_la_naissance_que_la_chronologie_porte():
    """Pour une fonctionnaire née en 1975, la présomption place ses enfants
    en 2005, sous L. 12 bis : deux trimestres chacun, dont un de services
    depuis le b ter. Déclarés nés en 2002, ils tombent sous L. 12 b : quatre
    chacun, tous de services. Le moteur lit la chronologie, et rien
    d'autre."""
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur()
    actuel = simulateur.scenario_actuel

    def trimestres(chronologie_complete: dict) -> tuple[int, int]:
        carriere = Carriere.depuis_chronologie(chronologie_complete, simulateur.macro)
        regimes = {"fonction_publique_etat": 4 * len(carriere.annees_cotisees)}
        majoration = compter.majoration_pour_enfants(actuel, carriere, regimes,
                                                     carriere.annee_liquidation)
        return majoration.trimestres, majoration.services

    brute = chronologie.du_parcours(1975, "F", [Metier("fonctionnaire_etat", 22.0)],
                                    age_liquidation=62.0, nombre_enfants=2)
    assert trimestres(chronologie.completer(brute)) == (4, 2)
    for enfant in ("enfant_1", "enfant_2"):
        brute["faits"].append(chronologie.fait(f"naissance_{enfant}", enfant, "naissance",
                                               "2002-03-01"))
    assert trimestres(chronologie.completer(brute)) == (8, 8)
    # Un enfant de chaque côté de 2004 : chacun reçoit ce que sa version
    # accorde, quatre et quatre de services, puis deux dont un de services.
    deux_dates = chronologie.du_parcours(1975, "F", [Metier("fonctionnaire_etat", 22.0)],
                                         age_liquidation=62.0, nombre_enfants=2,
                                         naissances_enfants=["2002-03", "2006-09"])
    assert trimestres(chronologie.completer(deux_dates)) == (6, 5)
