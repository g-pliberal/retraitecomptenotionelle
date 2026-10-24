"""Le minimum de pension de l'agent de la SNCF (action 138, étape 9).

« Lorsqu'il est procédé à la liquidation de la pension d'ancienneté, le
montant de celle-ci ne peut être inférieur à un montant minimal défini au IV »
(décret n° 2008-639, article 15, I, du 1er juillet 2008) ; aux pensions prenant
effet depuis le 1er janvier 2017 (décret n° 2011-291, article 18, II),
seulement « si le nombre de trimestres de durée d'assurance [...] est égal au
nombre de trimestres nécessaire pour obtenir le pourcentage maximum » ou si
« l'intéressé a atteint l'âge auquel s'annule le coefficient de minoration »,
sauf à l'agent qui avait atteint avant cette date l'âge de liquidation de
l'article 1er de 2008, qui garde l'article 15 d'avant. Le minimum : 3 379,38 €
par trimestre au 1er décembre 2008, 1 215,64 € par mois au 1er octobre 2014
(IV), revalorisés comme les pensions de l'État (article 30).

La pension d'ancienneté est celle de l'agent qui compte vingt-cinq années de
services valables pour la retraite (article 1er, rédaction de 2008), vingt-sept
depuis 2017, abaissées à vingt-cinq ans et quatre mois de plus par année pour
qui les atteint de 2017 à 2021 (article 37-1, I, 3°) ; en deçà, la pension
proportionnelle (article 3), sans minimum.

L'agent, né le 15 janvier, part le 1er du mois qui suit son anniversaire ; le
modèle prête à tout agent de la SNCF l'âge de l'agent de conduite (fiche du
régime), cinquante ans dans la rédaction de 2008.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.droit.commun import date_d_effet
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]

#: Le minimum de l'article 15, IV, par an : 3 379,38 € par trimestre au
#: 1er décembre 2008, 1 215,64 € par mois au 1er octobre 2014.
MINIMUM_2008 = 3379.38 * 4
MINIMUM_2014 = 1215.64 * 12
#: Revalorisé « du taux et à la date prévus pour les fonctionnaires de l'Etat »
#: (article 30) : ceux de L. 161-23-1, 1 % au 1er avril 2009 ; 0,1 % au
#: 1er octobre 2015, 0,8 % au 1er octobre 2017, 0,3 % au 1er janvier 2019, 1 %
#: en 2020 (le taux des pensions de 2 000 € par mois au plus), 0,4 % en 2021,
#: 1,1 % et 4 % en 2022, 0,8 % en 2023, 5,3 % en 2024.
MINIMUM_FEVRIER_2010 = MINIMUM_2008 * 1.01
MINIMUM_FEVRIER_2017 = MINIMUM_2014 * 1.001
MINIMUM_FEVRIER_2019 = MINIMUM_FEVRIER_2017 * 1.008 * 1.003
MINIMUM_FEVRIER_2023 = MINIMUM_FEVRIER_2019 * 1.01 * 1.004 * 1.011 * 1.04 * 1.008
MINIMUM_FEVRIER_2024 = MINIMUM_FEVRIER_2023 * 1.053


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _liquider(simulateur: Simulateur, naissance: int, liquidation: float,
              metiers: list[Metier], enfants: int = 0):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, mois_naissance=1, jour_naissance=15, sexe="H",
        metiers=metiers, age_liquidation=liquidation, macro=simulateur.macro,
        nombre_enfants=enfants)
    resultat = simulateur.scenario_actuel.calculer(carriere)
    minimum = next((a for a in resultat.avantages_appliques
                    if a.code == "minimum_pension_sncf"), None)
    return (carriere, resultat, {p.regime: p for p in resultat.pensions_par_regime},
            minimum)


def _agent(debut: float, salaire: float = 0.3) -> list[Metier]:
    return [Metier(affiliation="agent_sncf", age_debut=debut, niveau_salaire=salaire)]


def test_la_pension_d_anciennete_est_portee_au_minimum(simulateur):
    """Trente-cinq ans de services au tiers du salaire moyen, liquidés à
    cinquante-cinq ans en février 2010 : la pension d'ancienneté est portée au
    minimum, 3 379,38 € par trimestre revalorisés de 1 % au 1er avril 2009."""
    carriere, _, pensions, minimum = _liquider(simulateur, 1955, 55.0, _agent(20.0))
    assert date_d_effet(carriere) == "2010-02-01"
    pension = pensions["sncf"]
    assert pension.montant == pytest.approx(MINIMUM_FEVRIER_2010, abs=0.01)
    assert minimum is not None and minimum.libelle == "Minimum de pension de la SNCF"
    assert 0 < minimum.montant < MINIMUM_FEVRIER_2010
    assert pension.detail.endswith(f", porté au minimum de pension par + "
                                   f"{minimum.montant:,.2f} €")


def test_la_pension_proportionnelle_n_a_pas_de_minimum(simulateur):
    """Vingt-trois ans de services, sous les vingt-cinq de la pension
    d'ancienneté : la pension proportionnelle de l'article 3 reste ce qu'elle
    est."""
    carriere, _, pensions, minimum = _liquider(simulateur, 1955, 55.0, _agent(32.0))
    assert carriere.duree_de_service(["agent_sncf"]) < 25
    assert minimum is None
    assert 0 < pensions["sncf"].montant < MINIMUM_FEVRIER_2010


def test_avant_le_1er_juillet_2008_aucun_minimum_n_est_lu(simulateur):
    """Le règlement de retraites d'avant le décret de 2008, que l'index ne porte
    pas : aucun montant du minimum n'est lu, et le modèle n'en sert pas."""
    carriere, _, pensions, minimum = _liquider(simulateur, 1952, 55.0, _agent(20.0))
    assert date_d_effet(carriere) == "2007-02-01"
    assert minimum is None
    assert pensions["sncf"].montant < MINIMUM_2008


def test_depuis_2017_la_pension_decotee_n_a_pas_de_minimum(simulateur):
    """Né en 1968, l'agent n'a ses cinquante ans qu'en 2018 : parti à cinquante
    et un ans en février 2019, avec trente et un ans de services, sous la durée
    requise et sous l'âge d'annulation de la décote, il n'a pas de minimum."""
    carriere, resultat, pensions, minimum = _liquider(simulateur, 1968, 51.0, _agent(20.0))
    assert date_d_effet(carriere) == "2019-02-01"
    assert resultat.taux_liquidation < 0.75
    assert minimum is None
    assert pensions["sncf"].montant < MINIMUM_FEVRIER_2019


def test_depuis_2017_l_age_d_annulation_de_la_decote_ouvre_le_minimum(simulateur):
    """Le même agent parti à cinquante-six ans, en février 2024, au-delà de l'âge
    d'annulation de la décote : sa pension est portée au minimum."""
    carriere, _, pensions, minimum = _liquider(simulateur, 1968, 56.0, _agent(20.0))
    assert date_d_effet(carriere) == "2024-02-01"
    assert minimum is not None
    assert pensions["sncf"].montant == pytest.approx(MINIMUM_FEVRIER_2024, abs=0.01)


def test_l_agent_qui_avait_l_age_avant_2017_garde_le_minimum_sans_le_taux_plein(
        simulateur):
    """Né en 1966, l'agent a eu cinquante ans en janvier 2016, avant le
    1er janvier 2017 : parti décoté à cinquante et un ans en février 2017, il
    garde l'article 15 d'avant 2011, et le minimum sans le taux plein (décret
    n° 2011-291, article 18, II)."""
    carriere, resultat, pensions, minimum = _liquider(simulateur, 1966, 51.0, _agent(20.0))
    assert date_d_effet(carriere) == "2017-02-01"
    assert resultat.taux_liquidation < 0.75
    assert minimum is not None
    assert pensions["sncf"].montant == pytest.approx(MINIMUM_FEVRIER_2017, abs=0.01)


@pytest.mark.parametrize("prive_depuis, porte", [
    # La SNCF jusqu'en 2020 : vingt-six ans et six mois de services.
    (53.0 + 7 / 12, True),
    # La SNCF jusqu'en 2019 : vingt-cinq ans et six mois.
    (53.0 + 5 / 12, False),
])
def test_vingt_cinq_ans_atteints_en_2019_demandent_vingt_six_ans(simulateur, prive_depuis,
                                                                 porte):
    """Entré en juillet 1994, l'agent a vingt-cinq ans de services en juin 2019 :
    la durée de vingt-sept ans de la pension d'ancienneté est « abaissée [...] à
    vingt-six ans pour les agents qui atteignent la durée de services de
    vingt-cinq ans [...] en 2019 » (article 37-1, I, 3°). Il quitte la SNCF
    pour le privé, et liquide à cinquante-six ans, en février 2023, au-delà de
    l'âge d'annulation de la décote : vingt-six ans et six mois de services
    ouvrent le minimum, vingt-cinq ans et six mois non."""
    metiers = [Metier(affiliation="agent_sncf", age_debut=27.5, niveau_salaire=0.3),
               Metier(affiliation="salarie_prive_non_cadre", age_debut=prive_depuis,
                      niveau_salaire=0.3)]
    carriere, _, pensions, minimum = _liquider(simulateur, 1967, 56.0, metiers)
    assert date_d_effet(carriere) == "2023-02-01"
    assert carriere.date_de_service(["agent_sncf"], 25.0) == DateMois(2019, 6)
    assert carriere.duree_de_service(["agent_sncf"]) == pytest.approx(
        26.5 if porte else 25.5)
    assert (minimum is not None) == porte
    if porte:
        assert pensions["sncf"].montant == pytest.approx(MINIMUM_FEVRIER_2023, abs=0.01)
    else:
        assert pensions["sncf"].montant < MINIMUM_FEVRIER_2023


def test_la_majoration_pour_enfants_se_calcule_sur_le_minimum(simulateur):
    """« Les pensionnés ayant élevé trois enfants [...] bénéficient d'une
    majoration de 10 % de leur pension » (article 16) : de la pension portée au
    minimum."""
    _, resultat, _, minimum = _liquider(simulateur, 1955, 55.0, _agent(20.0), enfants=3)
    assert minimum is not None
    majoration = next(a for a in resultat.avantages_appliques
                      if a.code == "majoration_enfants")
    assert dict(majoration.par_regime)["sncf"] == pytest.approx(
        0.10 * MINIMUM_FEVRIER_2010, abs=0.01)


#: Les mêmes carrières, au formulaire : l'agent présumé né le 15 du mois.
REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "20", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "interruptions": "", "liquidation": "55", "naissance": "1955", "naissance_mois": "1",
    "primes": "0", "profil": "plat", "projection": "cor_reference", "salaire": "0.3",
    "sexe": "H", "statut": "agent_sncf", "stock": "prix", "table": "unisexe",
}
CAS = [
    {},
    {"debut": "32"},
    {"naissance": "1952"},
    {"naissance": "1968", "liquidation": "51"},
    {"naissance": "1968", "liquidation": "56"},
    {"naissance": "1966", "liquidation": "51"},
    {"enfants": "3"},
    # Vingt-cinq ans de services atteints en 2019, puis le privé.
    {"naissance": "1967", "liquidation": "56", "debut": "27", "debut_mois": "6",
     "metier2_debut": "53", "metier2_debut_mois": "7",
     "metier2_statut": "salarie_prive_non_cadre", "metier2_salaire": "0.3"},
    {"naissance": "1967", "liquidation": "56", "debut": "27", "debut_mois": "6",
     "metier2_debut": "53", "metier2_debut_mois": "5",
     "metier2_statut": "salarie_prive_non_cadre", "metier2_salaire": "0.3"},
    # La réversion de la pension portée au minimum, au journal du décès.
    {"conjoint": "1957", "mariage": "1980-06", "deces": "2023-05"},
]


def test_la_reversion_d_une_pension_portee_au_minimum_en_garde_54_pour_cent():
    """« Lorsque la pension de l'agent a été portée au montant du minimum de
    pension prévu à l'article 15, la pension de réversion est portée à [...]
    54 % de ce montant » (article 18). L'agent parti en février 2010 meurt en
    mai 2023 : sa réversion est 54 % du minimum de 2023, quand même sa pension,
    revalorisée comme les pensions depuis 2010, reste 0,3 % sous le minimum que
    le décret de 2015 écrit au 1er octobre 2014."""
    from outils_pont import Saisies

    sortie = Saisies().simuler({
        **REQUETE, "conjoint": "1957", "mariage": "1980-06", "deces": "2023-05",
    }).dictionnaire()["reversion"]
    ligne, = [ligne for ligne in sortie["regimes"] if ligne["regime"] == "sncf"]
    assert ligne["base"] < MINIMUM_FEVRIER_2023
    assert (ligne["motif"], ligne["montant"]) == (
        "minimum", pytest.approx(0.54 * MINIMUM_FEVRIER_2023, abs=0.01))


def test_les_deux_moteurs_servent_le_meme_minimum_de_pension():
    """Chaque étape de la liquidation écrit la même donnée en Python et en
    JavaScript, le minimum de pension de la SNCF compris."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    from test_liquidation import _ecarts, _python

    requetes = [{**REQUETE, **cas} for cas in CAS]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(requetes, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-liquidation.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    obtenus, attendus = json.loads(execution.stdout), _python(requetes)
    assert not any("erreur" in attendu for attendu in attendus), attendus
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
    portees = [rang for rang, attendu in enumerate(attendus)
               if "porté au minimum de pension" in json.dumps(attendu, ensure_ascii=False)]
    assert portees == [0, 4, 5, 6, 7, 9], portees
    reversion = json.dumps(attendus[9], ensure_ascii=False)
    assert '"motif": "minimum"' in reversion, "la réversion n'est pas portée au minimum"
