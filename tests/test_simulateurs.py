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


def test_la_feuille_ne_repropose_rien_et_s_arrete_au_budget():
    lignes, tous = simulateurs.registre(), simulateurs.exemples()
    adaptateur = simulateurs.ADAPTATEURS["union_retraite_carriere_longue"]
    faites = simulateurs.saisies(adaptateur.simulateur, tous)
    assert len(faites) == 5
    lignes[adaptateur.simulateur]["budget"] = 8
    cas = simulateurs.a_saisir(adaptateur, lignes, tous)
    assert len(cas) == 3
    assert not {c.cle for c in cas} & set(faites)
    lignes[adaptateur.simulateur]["budget"] = 5
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
