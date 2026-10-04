"""La saisie outillée d'un simulateur officiel : le budget, la feuille, la transcription.

`scripts/simulateurs.py` fait tout ce qui entoure une saisie (docs/architecture.md,
§ 3.5) : il choisit les entrées dans le budget, écrit la prédiction du modèle
avant la réponse, et transcrit la réponse en exemple officiel. Ces tests tiennent
les trois promesses qui font qu'on peut s'y fier : il ne propose jamais une
saisie déjà faite ni une de trop ; sa prédiction est ce que `tests/test_oracle.py`
comparera ; et ce qu'il transcrit se lit dans la réponse, passe le contrôle des
sources et se rejoue.
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]


def _module():
    spec = importlib.util.spec_from_file_location(
        "simulateurs_sous_test", RACINE / "scripts" / "simulateurs.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # ses dataclasses s'y cherchent
    spec.loader.exec_module(module)
    return module


simulateurs = _module()


@pytest.fixture(scope="module")
def contexte():
    return simulateurs.Contexte()


def _feuille(cas: list[dict], date: str = "2026-10-04") -> dict:
    return {"simulateur": "union_retraite_age_depart", "saisie_le": date, "cas": cas}


def _vierge() -> tuple[dict, list[dict]]:
    """Le registre et les exemples comme si le simulateur d'âge légal n'avait
    encore rien rendu, son budget porté à toutes ses entrées : les tests de la
    transcription ne dépendent pas des saisies déjà faites."""
    lignes, tous = simulateurs.registre(), simulateurs.exemples()
    adaptateur = simulateurs.ADAPTATEURS["union_retraite_age_depart"]
    lignes[adaptateur.simulateur]["budget"] = adaptateur.espace
    return lignes, [e for e in tous if e["source"].get("simulateur") != adaptateur.simulateur]


def _reponse(age: str, trimestres: int) -> str:
    """Une réponse écrite comme le simulateur d'âge légal l'écrit, lu le
    4 octobre 2026 : la durée n'y suit pas le mot « trimestres », et l'âge du
    taux plein automatique y côtoie l'âge légal."""
    return (f"Votre âge légal de départ* à la retraite est {age}. Cet âge peut être "
            "différent dans certains régimes complémentaires. Le nombre de trimestres "
            f"requis pour votre départ à taux plein est de {trimestres}. Vous aurez "
            "atteint l'âge du taux plein automatique** à 67 ans.")


def test_le_budget_compte_les_saisies_et_non_les_exemples():
    tous = [
        {"id": "a", "source": {"simulateur": "s", "saisie": "1965"}},
        {"id": "b", "source": {"simulateur": "s", "saisie": "1965"}},
        {"id": "c", "source": {"simulateur": "s", "saisie": "1966"}},
        {"id": "d", "source": {"editeur": "Cnav"}},
    ]
    assert simulateurs.saisies("s", tous) == {"1965": ["a", "b"], "1966": ["c"]}
    assert simulateurs.budget_par_defaut(8) == 2
    assert simulateurs.budget_par_defaut(28) == 7
    assert simulateurs.budget_par_defaut(None) == simulateurs.BUDGET_ESPACE_OUVERT


def test_une_saisie_sans_exemple_se_decompte_aussi():
    """Le handicap a été saisi le 4 octobre 2026 sans qu'aucun exemple ne
    rejoue ses réponses : le registre les déclare, et le budget les décompte
    comme les autres, sans quoi on pourrait les refaire. Le RAFP, saisi le
    même jour, ne déclare plus rien : ses dix saisies sont des exemples."""
    faites = {"1965": ["a", "b"]}
    assert simulateurs.decomptees({}, faites) == 1
    assert simulateurs.decomptees({"saisies_hors_exemples": 10}, faites) == 11
    lignes = simulateurs.registre()
    etat = {identifiant: (budget, nombre, reste) for identifiant, budget, nombre, reste
            in simulateurs.etat_des_budgets(lignes, simulateurs.exemples())}
    ligne = lignes["union_retraite_handicap"]
    assert ligne["saisies_hors_exemples"] > 0
    assert etat["union_retraite_handicap"][1] >= ligne["saisies_hors_exemples"]
    assert etat["union_retraite_handicap"][2] >= 0
    assert not lignes["rafp_simulateur_prestation"].get("saisies_hors_exemples")
    assert etat["rafp_simulateur_prestation"] == (10, 10, 0)


def test_la_feuille_ne_repropose_rien_et_s_arrete_au_budget():
    lignes, tous = simulateurs.registre(), simulateurs.exemples()
    adaptateur = simulateurs.ADAPTATEURS["union_retraite_carriere_longue"]
    faites = simulateurs.saisies(adaptateur.simulateur, tous)
    assert len(faites) == 7
    lignes[adaptateur.simulateur]["budget"] = 10
    cas = simulateurs.a_saisir(adaptateur, lignes, tous)
    assert len(cas) == 3
    assert not {c.cle for c in cas} & set(faites)
    lignes[adaptateur.simulateur]["budget"] = 7
    with pytest.raises(simulateurs.Refus, match="épuisé"):
        simulateurs.a_saisir(adaptateur, lignes, tous)
    del lignes[adaptateur.simulateur]["budget"]
    with pytest.raises(simulateurs.Refus, match="7, le quart"):
        simulateurs.a_saisir(adaptateur, lignes, tous)


def test_la_feuille_commence_par_ce_qu_aucun_exemple_ne_couvre():
    lignes, tous = simulateurs.registre(), simulateurs.exemples()
    adaptateur = simulateurs.ADAPTATEURS["union_retraite_age_depart"]
    lignes[adaptateur.simulateur]["budget"] = adaptateur.espace
    ordre = [c.generation for c in simulateurs.a_saisir(adaptateur, lignes, tous)]
    couvertes = adaptateur.couvertes(tous)
    assert {1964, 1965} <= couvertes  # la circulaire Cnav 2026-07
    libres = [g for g in ordre if g not in couvertes]
    assert ordre[:len(libres)] == libres == sorted(libres, reverse=True)


def test_la_prediction_est_ce_que_l_oracle_comparera(contexte):
    """1965 coupé en avril, comme la circulaire Cnav 2026-07 l'écrit : la
    prédiction lit le modèle par les fonctions mêmes de l'oracle."""
    tous = {e["id"]: e for e in simulateurs.exemples()}
    adaptateur = simulateurs.ADAPTATEURS["union_retraite_age_depart"]
    cas = next(c for c in adaptateur.cas() if c.cle == "1965")
    avant, apres = adaptateur.predire(contexte, cas)
    assert (avant["periode"], apres["periode"]) == ("1965-01..1965-03", "1965-04..1965-12")
    for prediction, publie in ((avant, "cnav_2026_07_age_legal_1965_premier_trimestre"),
                               (apres, "cnav_2026_07_age_legal_1965_apres_avril")):
        attendu = tous[publie]["attendu"]
        assert simulateurs.age_lu(prediction["age"]) == (
            int(attendu["age_ouverture"]), round(attendu["age_ouverture"] % 1 * 12))
        assert prediction["trimestres"] == attendu["trimestres_requis"]


def test_une_reponse_devient_un_exemple_source_qui_se_rejoue(contexte, tmp_path):
    lignes, tous = _vierge()
    adaptateur = simulateurs.ADAPTATEURS["union_retraite_age_depart"]
    cas = next(c for c in adaptateur.cas() if c.cle == "1969 et après")
    (prediction,) = adaptateur.predire(contexte, cas)
    reponse = _reponse(prediction["age"], prediction["trimestres"])
    donnees = _feuille([{"saisie": dict(cas.saisie), "prediction": [prediction],
                         "reponse": reponse, "lu": None}])
    (exemple,) = simulateurs.exemples_de_la_feuille(donnees, lignes, tous)
    assert exemple["id"] == "ur_age_legal_1969"
    assert exemple["source"]["simulateur"] == adaptateur.simulateur
    assert exemple["source"]["saisie"] == "1969 et après"
    assert exemple["attendu"]["trimestres_requis"] == prediction["trimestres"]
    # Le contrôle des sources de l'oracle, tel quel.
    source = exemple["source"]
    assert len(source["reference"].split()) >= 4
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", source["verifie_le"])
    assert len(exemple["enonce"].split()) >= 12
    copie = tmp_path / "exemples_officiels.yaml"
    shutil.copy(simulateurs.EXEMPLES, copie)
    simulateurs.ecrire([exemple], copie)
    relu = {e["id"]: e for e in simulateurs.exemples(copie)}["ur_age_legal_1969"]
    assert relu == exemple
    assert copie.read_bytes().count(b"\r") == 0
    assert contexte.confronter(relu) == []


def test_un_ecart_se_dit_a_la_transcription(contexte):
    lignes, tous = _vierge()
    donnees = _feuille([{"saisie": {"Votre année de naissance": "1968"},
                         "reponse": _reponse("62 ans", 168),
                         "lu": None}])
    (exemple,) = simulateurs.exemples_de_la_feuille(donnees, lignes, tous)
    assert contexte.confronter(exemple)


def test_une_lecture_ne_s_invente_pas():
    lignes, tous = _vierge()
    plusieurs = _feuille([{"saisie": {"Votre année de naissance": "1966"},
                           "reponse": _reponse("63 ans", 172) + " "
                           + _reponse("63 ans et 3 mois", 172),
                           "lu": None}])
    with pytest.raises(simulateurs.Refus, match="écrire `lu`"):
        simulateurs.exemples_de_la_feuille(plusieurs, lignes, tous)
    inventee = _feuille([{"saisie": {"Votre année de naissance": "1966"},
                          "reponse": _reponse("63 ans et 3 mois", 172),
                          "lu": [{"periode": "1966", "age": "64 ans"}]}])
    with pytest.raises(simulateurs.Refus, match="n'est pas dans la réponse"):
        simulateurs.exemples_de_la_feuille(inventee, lignes, tous)
    sans_date = _feuille([], date=None)
    with pytest.raises(simulateurs.Refus, match="saisie_le"):
        simulateurs.exemples_de_la_feuille(sans_date, lignes, tous)


def test_la_reponse_du_simulateur_se_lit_seule():
    adaptateur = simulateurs.ADAPTATEURS["union_retraite_age_depart"]
    cas = next(c for c in adaptateur.cas() if c.cle == "1968")
    assert adaptateur.lire(cas, _reponse("63 ans et 9 mois", 172)) == [
        {"periode": "1968", "age": "63 ans et 9 mois", "trimestres": 172}]


def test_une_saisie_de_trop_est_refusee():
    lignes, tous = _vierge()
    lignes["union_retraite_age_depart"]["budget"] = 1
    donnees = _feuille([
        {"saisie": {"Votre année de naissance": annee},
         "reponse": _reponse("63 ans et 3 mois", 172), "lu": None}
        for annee in ("1966", "1967")])
    with pytest.raises(simulateurs.Refus, match="dépasseraient le budget"):
        simulateurs.exemples_de_la_feuille(donnees, lignes, tous)


# -- le simulateur de prestation de l'ERAFP ------------------------------------

def _vierge_rafp() -> tuple[dict, list[dict]]:
    """Le registre et les exemples comme si l'ERAFP n'avait rien rendu."""
    lignes, tous = simulateurs.registre(), simulateurs.exemples()
    adaptateur = simulateurs.ADAPTATEURS["rafp_simulateur_prestation"]
    lignes[adaptateur.simulateur]["budget"] = 10
    return lignes, [e for e in tous if e["source"].get("simulateur") != adaptateur.simulateur]


def test_les_dix_saisies_de_l_erafp_sont_des_exemples_du_lot():
    """Chaque exemple `erafp_…` est une saisie de l'adaptateur, et le lot du 4
    octobre 2026 est entier : la feuille suivante ne propose que les bornes
    qu'il n'a pas touchées. Les exemples que l'ERAFP publie couvrent la
    génération 1960 : la plus jeune, 1966, passe en tête."""
    adaptateur = simulateurs.ADAPTATEURS["rafp_simulateur_prestation"]
    tous = simulateurs.exemples()
    faites = simulateurs.saisies(adaptateur.simulateur, tous)
    lot = [c.cle for c in adaptateur.cas()]
    assert len(faites) == 10 and set(faites) == set(lot[:10])
    assert all(e["source"]["editeur"] == "ERAFP" for e in tous
               if e["source"].get("simulateur") == adaptateur.simulateur)
    lignes = simulateurs.registre()
    lignes[adaptateur.simulateur]["budget"] = 12
    proposees = simulateurs.a_saisir(adaptateur, lignes, tous)
    assert 1960 in adaptateur.couvertes(tous)
    assert [c.cle for c in proposees] == lot[10:12]


def test_une_reponse_de_l_erafp_devient_un_exemple_qui_se_rejoue(contexte, tmp_path):
    """La prédiction du modèle, recopiée comme réponse : l'exemple qu'elle
    donne passe le contrôle des sources et concorde. 4 900 points en 2031 se
    versent en deux fois, quatre mois de rente d'abord."""
    lignes, tous = _vierge_rafp()
    adaptateur = simulateurs.ADAPTATEURS["rafp_simulateur_prestation"]
    cas = next(c for c in adaptateur.cas() if c.cle == "15/06/1966 ; 01/01/2031 ; 4900")
    (lu,) = adaptateur.predire(contexte, cas)
    assert lu["forme"] == "capital_fractionne" and lu["age_legal"] == "63 ans et 3 mois"
    assert lu["coefficient"] == 1.1
    reponse = (f"Âge légal {lu['age_legal']} ; coefficient de majoration 1,10 ; capital "
               f"fractionné, première fraction de {str(lu['premiere_fraction']).replace('.', ',')} €.")
    lu = {cle: lu[cle] for cle in ("forme", "age_legal", "coefficient", "premiere_fraction")}
    donnees = {"simulateur": adaptateur.simulateur, "saisie_le": "2026-10-05",
               "cas": [{"saisie": dict(cas.saisie), "reponse": reponse, "lu": [lu]}]}
    (exemple,) = simulateurs.exemples_de_la_feuille(donnees, lignes, tous)
    assert exemple["id"] == "erafp_1966_effet_2031_01_4900_points"
    assert exemple["source"]["editeur"] == "ERAFP"
    assert exemple["carriere"]["points_rafp"] == 4900
    assert exemple["attendu"]["prestation_rafp"]["age_legal"] == 63.25
    assert len(exemple["enonce"].split()) >= 12
    copie = tmp_path / "exemples_officiels.yaml"
    shutil.copy(simulateurs.EXEMPLES, copie)
    simulateurs.ecrire([exemple], copie)
    relu = {e["id"]: e for e in simulateurs.exemples(copie)}[exemple["id"]]
    assert relu == exemple
    assert contexte.confronter(relu) == []


def test_une_lecture_de_l_erafp_ne_s_invente_pas():
    lignes, tous = _vierge_rafp()
    adaptateur = simulateurs.ADAPTATEURS["rafp_simulateur_prestation"]
    cas = adaptateur.cas()[0]
    reponse = "Âge légal 62 ans et 9 mois ; coefficient de majoration 1,03 ; rente de 29,21 €."
    for lu, motif in (({"forme": "rente", "coefficient": 1.04}, "coefficient lu"),
                      ({"forme": "rente", "age_legal": "63 ans"}, "âge légal lu"),
                      ({"forme": "viagere"}, "forme lue")):
        donnees = {"simulateur": adaptateur.simulateur, "saisie_le": "2026-10-04",
                   "cas": [{"saisie": dict(cas.saisie), "reponse": reponse, "lu": [lu]}]}
        with pytest.raises(simulateurs.Refus, match=motif):
            simulateurs.exemples_de_la_feuille(donnees, lignes, tous)
    sans_lecture = {"simulateur": adaptateur.simulateur, "saisie_le": "2026-10-04",
                    "cas": [{"saisie": dict(cas.saisie), "reponse": reponse, "lu": None}]}
    with pytest.raises(simulateurs.Refus, match="écrire `lu`"):
        simulateurs.exemples_de_la_feuille(sans_lecture, lignes, tous)
