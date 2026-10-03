"""Les services passés de l'outre-mer : les années d'avant la généralisation
de l'Arrco, que l'institution valide sans cotisation — en Nouvelle-Calédonie
avant 1995, à Saint-Pierre-et-Miquelon avant 1988. Le scénario 1 en sert les
points à une pension prise depuis ; le compte notionnel n'en porte rien. La
règle est dans `legislation/affiliations.yaml` (`services_passes`), la fiche
dans `regles/services_passes_outre_mer.yaml` ; les témoins
`chomage_et_services_passes_caledoniens` et `chomage_saint_pierre_et_miquelon`
confrontent les deux moteurs."""

from __future__ import annotations

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.config import PartCotisation
from retraite_notionnelle.droit import releve as _releve
from retraite_notionnelle.moteur.compte import ConstructeurCompte
from retraite_notionnelle.simulateur import Simulateur

CALEDONIEN = "salarie_nouvelle_caledonie"
SAINT_PIERRAIS = "salarie_saint_pierre_et_miquelon"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def _carriere(simulateur, affiliation, naissance):
    return simulateur.carriere_simple(
        annee_naissance=naissance, sexe="F", affiliation=affiliation, mois_naissance=1,
        age_debut=21, age_liquidation=64, niveau_salaire=1.0, profil_carriere="plat")


def _points(simulateur, carriere) -> dict[tuple[str, int], float]:
    droits = _releve.construire(simulateur.scenario_actuel, carriere).droits
    return {(code, annee): points for code, annee, points, _ in droits.points}


def test_les_services_passes_se_lisent(simulateur):
    """Ce que les périodes des deux statuts disent, année par année."""
    affiliations = simulateur.affiliations
    assert affiliations.services_passes(CALEDONIEN, 1959) == (frozenset({"unirs"}), 1995)
    assert affiliations.services_passes(CALEDONIEN, 1994) == (
        frozenset({"arrco", "arrco_tranche_2"}), 1995)
    assert affiliations.services_passes(CALEDONIEN, 1995) == (frozenset(), 0)
    assert affiliations.services_passes(SAINT_PIERRAIS, 1987) == (
        frozenset({"arrco", "arrco_tranche_2"}), 1988)
    assert affiliations.services_passes(SAINT_PIERRAIS, 1988) == (frozenset(), 0)
    assert affiliations.services_passes("salarie_prive_non_cadre", 1980) == (frozenset(), 0)


def test_un_service_passe_precede_la_generalisation(simulateur):
    """Un service passé est un régime de sa période, et sa période finit avant
    l'année d'où une pension le sert : sans quoi une année serait à la fois
    cotisée et validée sans cotisation."""
    affiliations = simulateur.affiliations
    vus = 0
    for statut in affiliations.codes:
        for periode in affiliations.periodes(statut):
            regle = periode.get("services_passes")
            if not regle:
                continue
            vus += 1
            assert set(regle["regimes"]) <= set(periode["regimes"]), (statut, periode)
            assert periode["fin"] is not None, (statut, periode)
            assert periode["fin"] < int(regle["pension_depuis"]), (statut, periode)
    assert vus == 3


def test_le_compte_ne_porte_pas_les_services_passes(simulateur):
    """Personne n'a cotisé à l'Arrco calédonien avant 1995, ni à celui de
    Saint-Pierre-et-Miquelon en 1987 : le compte notionnel n'en porte que la
    caisse locale ; il porte l'Arrco dès la généralisation."""
    constructeur = ConstructeurCompte(
        simulateur.macro, simulateur.catalogue, simulateur.affiliations,
        simulateur.indexation, simulateur.parametres.avec(part_cotisation=PartCotisation.TOTALE))
    caledonienne = _carriere(simulateur, CALEDONIEN, 1935)
    assert constructeur.cotisation_annuelle(caledonienne, 1959).regimes == (
        "cafat_nouvelle_caledonie",)
    assert constructeur.cotisation_annuelle(caledonienne, 1990).regimes == (
        "cafat_nouvelle_caledonie",)
    assert "arrco" in constructeur.cotisation_annuelle(caledonienne, 1995).regimes
    saint_pierraise = _carriere(simulateur, SAINT_PIERRAIS, 1960)
    assert constructeur.cotisation_annuelle(saint_pierraise, 1987).regimes == (
        "cps_saint_pierre_et_miquelon",)
    assert "arrco" in constructeur.cotisation_annuelle(saint_pierraise, 1988).regimes


def test_les_services_passes_valent_une_annee_cotisee(simulateur):
    """À une pension prise depuis 1995, l'année calédonienne de 1980 vaut les
    points de la même année cotisée en métropole, et 1958 ceux de l'UNIRS ;
    leurs points sont estimés."""
    caledonienne = _points(simulateur, _carriere(simulateur, CALEDONIEN, 1937))
    metropole = _points(simulateur, _carriere(simulateur, "salarie_prive_non_cadre", 1937))
    assert caledonienne[("arrco", 1980)] == pytest.approx(metropole[("arrco", 1980)])
    assert caledonienne[("unirs", 1958)] == pytest.approx(metropole[("unirs", 1958)])
    resultat = simulateur.scenario_actuel.calculer(_carriere(simulateur, CALEDONIEN, 1937))
    arrco = {p.regime: p for p in resultat.pensions_par_regime}["arrco"]
    assert arrco.fiabilite.name == "ESTIMEE"


def test_une_pension_d_avant_la_generalisation_n_a_pas_d_arrco(simulateur):
    """Une pension calédonienne prise en 1989 est servie sous le droit de
    1989 : la CAFAT seule, sans l'Arrco que le modèle lui prêtait depuis
    1961. Prise en 1999, elle a ses services passés."""
    avant = simulateur.scenario_actuel.calculer(_carriere(simulateur, CALEDONIEN, 1925))
    assert {p.regime for p in avant.pensions_par_regime if p.montant > 0} == {
        "cafat_nouvelle_caledonie"}
    apres = simulateur.scenario_actuel.calculer(_carriere(simulateur, CALEDONIEN, 1935))
    assert {"arrco", "unirs"} <= {p.regime for p in apres.pensions_par_regime if p.montant > 0}
