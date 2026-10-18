"""Le pont du cycle de vie : les cas types du COR, que le Python bâtit, calculés
par le portage (action 161, étape 5).

``scripts/cycle_de_vie.py`` résout chaque case de la grille — les options de
sa carrière (``CasType.options``), l'âge où le pilote la fait partir — et
``scripts/cycle_de_vie.mjs`` en rend les indicateurs, la pension par étage,
les âges de départ et les âges d'équilibre. La concordance des deux moteurs du cycle de vie se tient
dans ``test_cycle_de_vie_portage.py``, sur des carrières de la saisie ; ici,
ce que seuls les cas types portent — un profil au SMIC, des interruptions,
une part de primes, des enfants — arrive au portage tel que le Python le
calcule, et les âges d'équilibre d'un cas type, que le portage seul calcule
désormais, disent ce qu'ils doivent dire.
"""

from __future__ import annotations

import math
import shutil
import sys
from pathlib import Path

import pytest

from retraite_notionnelle import cycle_de_vie
from retraite_notionnelle.castypes import CAS_TYPES, calculer_cas_types
from retraite_notionnelle.config import RACINE_DONNEES, Parametres
from retraite_notionnelle.simulateur import Simulateur

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import cycle_de_vie as script  # noqa: E402

def _cas(code: str):
    return next(cas for cas in CAS_TYPES if cas.code == code)


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


@pytest.fixture(scope="module")
def portage():
    """Le pont fait tourner node ; sous les présomptions décalées, que le
    Python seul suit, ses tests se taisent comme toute confrontation au
    portage (``tests/conftest.py``)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")


def _ecarts(obtenu: dict, attendu: dict) -> list[str]:
    return [f"{scenario}.{nom} : {obtenu[scenario][nom]!r} au lieu de {valeur!r}"
            for scenario, valeurs in attendu.items() for nom, valeur in valeurs.items()
            if not (valeur == obtenu[scenario][nom] or (
                isinstance(valeur, float) and isinstance(obtenu[scenario][nom], float)
                and math.isclose(valeur, obtenu[scenario][nom], rel_tol=1e-9, abs_tol=1e-9)))]


@pytest.mark.parametrize("cor", (False, True), ids=("depot", "cor"))
def test_chaque_cas_type_arrive_au_portage_tel_que_le_python_le_calcule(portage, simulateur,
                                                                         cor):
    """Les treize cas types, nés en 1960 et en 2000 : leurs indicateurs, que le
    portage calcule des options de leur carrière, sont ceux que le cycle de
    vie Python calcule de la carrière que ``castypes`` bâtit."""
    generations = (1960, 2000)
    grille = calculer_cas_types(simulateur, generations=generations)
    obtenu = script.calculer(simulateur, cor=cor)
    assert len(grille.resultats) == len(CAS_TYPES) * len(generations)
    for (code, generation), comparaison in grille.resultats.items():
        convention = (cycle_de_vie.convention_cor(simulateur, comparaison) if cor
                      else cycle_de_vie.Convention())
        attendu = {scenario: valeurs.dictionnaire() for scenario, valeurs in
                   cycle_de_vie.indicateurs_des_systemes(simulateur, comparaison,
                                                         convention).items()}
        ecarts = _ecarts(obtenu[f"{code}|{generation}"], attendu)
        assert not ecarts, f"{code}, {generation} : " + "; ".join(ecarts[:6])


def _sans_ecart(obtenu, attendu) -> bool:
    if isinstance(attendu, dict):
        return (isinstance(obtenu, dict) and obtenu.keys() == attendu.keys()
                and all(_sans_ecart(obtenu[cle], valeur) for cle, valeur in attendu.items()))
    if isinstance(attendu, float) and isinstance(obtenu, (int, float)):
        return math.isclose(obtenu, attendu, rel_tol=1e-9, abs_tol=1e-9)
    return obtenu == attendu


@pytest.mark.parametrize("impot", (None, "prix"), ids=("avant_impot", "apres_impot"))
def test_la_pension_par_etage_d_un_cas_type_est_celle_du_python(portage, simulateur, impot):
    """Les treize cas types, nés en 1960 et en 2000 : la pension du départ de
    chaque système, étage par étage, et ses trois taux de remplacement, que
    le portage calcule, sont ceux du Python (``pension_par_etage``). Le
    fonctionnaire sédentaire n'a que son régime intégré ; l'artisan, sa base
    et sa complémentaire."""
    generations = (1960, 2000)
    grille = calculer_cas_types(simulateur, generations=generations)
    obtenu = script.etages(simulateur, impot=impot)
    for (code, generation), comparaison in grille.resultats.items():
        systemes = cycle_de_vie.flux_des_systemes(simulateur, comparaison, nets=True,
                                                  impot=impot)
        for scenario in cycle_de_vie.SCENARIOS:
            attendu = cycle_de_vie.pension_par_etage(simulateur, comparaison, scenario,
                                                     systemes).dictionnaire()
            assert _sans_ecart(obtenu[f"{code}|{generation}"][scenario], attendu), (
                code, generation, scenario)
    assert set(obtenu["fonctionnaire_sedentaire|1960"]["actuel"]["etages"]) == {"integre"}
    assert set(obtenu["artisan|1960"]["actuel"]["etages"]) == {"base", "complementaire"}


def test_le_script_imprime_chaque_etage_en_part_du_dernier_revenu(portage, capsys):
    """``--etages`` : pour chaque système, un tableau des cas types sur les
    générations par étage servi, en pour cent du dernier revenu, puis les
    trois taux de remplacement ; un étage qu'un cas type n'a pas y est un
    tiret, et un étage qu'aucun n'a ne s'imprime pas."""
    assert script.main(["--etages", "--impot", "--scenarios", "actuel"]) == 0
    sortie = capsys.readouterr().out
    assert "Étage de base, en part du dernier revenu — 1. Système actuel" in sortie
    assert "Taux de remplacement après impôt" in sortie
    assert "Compte notionnel" not in sortie
    base = sortie.split("Étage de base")[1].split("\n\n")[0]
    ligne = next(ligne for ligne in base.splitlines() if ligne.startswith("Fonctionnaire séd"))
    assert set(ligne[46:].split()) == {"—"}


def test_la_carriere_d_un_cas_type_se_batit_de_ses_options(simulateur):
    """Une seule source : la carrière que le simulateur bâtit des options est
    celle du cas type."""
    cas = _cas("carriere_interrompue")
    options = script.options(simulateur, cas, 1970, 64.0)
    assert options["interruptions"] == {1999: "education_enfant", 2000: "education_enfant",
                                        2001: "education_enfant", 2002: "education_enfant",
                                        2003: "education_enfant"}
    assert (simulateur.carriere_simple(**options).lignes
            == cas.carriere_a(simulateur, 1970, 64.0).lignes)


def test_les_conventions_de_projection_du_cor_ne_passent_pas():
    """Sous ``conventions_cor``, la carrière d'un cas type se déforme en Python
    (``primes_projetees``) : le pont refuse plutôt que de la perdre."""
    simulateur = Simulateur(Parametres(conventions_cor=True))
    with pytest.raises(ValueError, match="conventions de projection du COR"):
        script.options(simulateur, _cas("fonctionnaire_sedentaire"), 1970, 64.0)


def test_sans_node_le_script_s_arrete(monkeypatch):
    """Aucun moteur périmé ne prend le relais (note 0003, ce que le pont doit tenir)."""
    monkeypatch.setattr(script.shutil, "which", lambda nom: None)
    with pytest.raises(SystemExit, match="node absent"):
        script.portage({"grille": {"cas": [], "cor": False, "impot": None}})


def test_les_hypotheses_de_productivite_sont_les_trois_du_cor():
    assert script.productivites(RACINE_DONNEES) == (
        "cor_productivite_basse", "cor_reference", "cor_productivite_haute")


def test_les_ages_d_un_cas_type_vont_de_l_ouverture_a_l_annulation_de_la_decote(portage):
    """Le salarié au salaire moyen né en 1970, de trimestre en trimestre, de
    64 à 67 ans ; le salarié au SMIC, entré tôt, part plus tôt en carrière
    longue, jusqu'au même âge d'annulation."""
    resultats, _ = script.balayer([_cas("salaire_moyen"), _cas("smic_carriere_complete")],
                                  [1970], ["cor_reference"], cor=False)
    moyen = resultats["salaire_moyen|1970|cor_reference"]
    assert [depart["age"] for depart in moyen] == [64.0 + 0.25 * rang for rang in range(13)]
    longue = [depart["age"] for depart in resultats["smic_carriere_complete|1970|cor_reference"]]
    assert longue[0] < 64.0
    assert longue[-1] == 67.0


def test_les_ages_d_un_cas_type_ne_tiennent_qu_a_sa_mortalite(portage, simulateur):
    """Le cas type n'entre dans ses âges d'équilibre que par la mortalité de
    son diviseur, la population où son salaire le range, et par son sexe pour
    la part de vie : le salarié au SMIC et l'exploitant agricole, du même
    vingtile, ont les mêmes âges, à des âges de départ qu'une année sépare. Le
    fonctionnaire de catégorie active le montrait, du vingtile du salarié au
    salaire moyen et parti cinq ans avant lui, jusqu'à son recalage sur les
    actifs de la CNRACL (action 159, étape 5), qui le range au onzième. Le
    salarié au SMIC, d'un vingtile qui vit moins longtemps, retrouve plus tard
    la référence : de 1961 à 2000, son diviseur à 65 ans gagne 3,58 ans,
    contre 3,38, et il baisse moins vite avec l'âge, de 0,83 an par an, contre
    0,88. Le portage seul les calcule (scripts/cycle_de_vie.mjs) ; le
    diviseur et la part de vie de sa population sont ceux du jumeau Python."""
    ages = script.equilibres(simulateur, (2000,), (2000,))["cas_types"]
    moyen, smic, exploitant = (ages[f"{code}|2000"] for code in (
        "salaire_moyen", "smic_carriere_complete", "exploitant_agricole"))
    assert smic["population"] == exploitant["population"] == "niveau_de_vie_v04"
    assert exploitant["age_de_depart"] - smic["age_de_depart"] == 1.0
    assert ((smic["diviseur"], smic["part_de_vie"])
            == (exploitant["diviseur"], exploitant["part_de_vie"]))
    assert moyen["population"] == "niveau_de_vie_v14"
    for un in (smic, moyen):
        python = cycle_de_vie.age_d_equilibre(simulateur, 2000, "H", un["population"])
        assert un["diviseur"]["age"] == pytest.approx(python.age, rel=1e-12)
        assert un["part_de_vie"] == pytest.approx(cycle_de_vie.age_de_part_de_vie_constante(
            simulateur, 2000, "H", population=un["population"]), rel=1e-12)
    assert smic["diviseur"]["age"] > moyen["diviseur"]["age"]
    assert smic["part_de_vie"] > moyen["part_de_vie"]
