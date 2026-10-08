"""Le plafond de L. 18 : la pension majorée pour enfants bornée au traitement.

Action 138, étape 17 : Destinie 2 borne la majoration pour enfants de la
pension civile au salaire de référence (``src/DroitsRetr.cpp:877-878``,
``min(0.1+0.05*(n-3), sr_fp/pension_fp-1)``) ; le dépôt la servait sans borne
(registre, 138.17). Fiche ``majoration_enfants_plafond_fonction_publique``.

Le code des pensions majore la pension de 10 % pour trois enfants et de 5 % par
enfant au-delà, « sans que le montant de la pension majorée puisse excéder le
montant du traitement ou de la solde mentionné à l'article L. 15 » (L. 18, V),
et les décrets de la CNRACL et du FSPOEIE de même. Le Conseil d'État juge le
plafond conforme en lui-même, mais discriminatoire quand c'est la surcote,
déplafonnée en 2010, qui le fait mordre (29 décembre 2020, n° 428626) : depuis,
la pension se compare au traitement sans sa surcote, servie au-delà.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import completer, liquidation
from retraite_notionnelle.noyau import contrats
from retraite_notionnelle.scenarios.actuel import ScenarioActuel
from retraite_notionnelle.simulateur import Simulateur

ETAT = "fonction_publique_etat"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _liquider(simulateur: Simulateur, naissance: int, debut: float, depart: float,
              enfants: int, sexe: str = "F", statut: str = "fonctionnaire_etat",
              moteur=None) -> liquidation.Liquidation:
    """La liquidation d'une carrière entière dans un statut, les enfants nés
    tous les deux ans depuis les vingt-deux ans du parent."""
    simulateur_moteur = moteur or simulateur.scenario_actuel
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, sexe=sexe, metiers=[Metier(statut, debut, 1.0)],
        age_liquidation=depart, macro=simulateur.macro, mois_naissance=1,
        part_primes=0.15, nombre_enfants=enfants,
        naissances_enfants=tuple(str(naissance + 22 + 2 * rang) for rang in range(enfants)))
    return liquidation.liquider(liquidation.demande_de_depart(carriere),
                                liquidation.Etat(carriere),
                                liquidation.Contexte(simulateur_moteur, frozenset()))


def _mesure(liquidee: liquidation.Liquidation, regime: str = ETAT):
    """La pension du régime, sa majoration pour enfants, le traitement qui l'a
    liquidée et ce que la surcote lui ajoute."""
    indice, pension = next((i, p) for i, p in enumerate(liquidee.complements.regimes)
                           if p.regime == regime)
    eligible = next(e for e in liquidee.pensions.plafonds if e.indice == indice)
    majoration = sum(part for avantage in liquidee.complements.avantages
                     if avantage.code == "majoration_enfants"
                     for code, part in avantage.par_regime if code == regime)
    return pension.montant, majoration, eligible.traitement, eligible.surcote


def test_huit_enfants_au_taux_de_80_pour_cent_sont_bornes_au_traitement(simulateur):
    """Née en 1955, fonctionnaire de l'État de vingt-deux à soixante-deux ans,
    en 2017 : la bonification de ses huit enfants porte son taux à 80 %, et la
    majoration de 35 % le porterait à 108 % du traitement. La pension majorée
    est ramenée au traitement ; la pension, elle, reste entière. Sept enfants,
    104 %, de même."""
    for enfants in (7, 8):
        liquidee = _liquider(simulateur, 1955, 22.0, 62.0, enfants)
        pension, majoration, traitement, surcote = _mesure(liquidee)
        assert surcote == 0.0
        assert pension == pytest.approx(0.80 * traitement)
        assert pension + majoration == pytest.approx(traitement)
        avantage = next(a for a in liquidee.complements.avantages
                        if a.code == "majoration_enfants")
        assert "bornée au traitement dans la fonction publique" in avantage.detail
        assert avantage.montant == pytest.approx(majoration)


def test_trois_enfants_ne_sont_pas_bornes(simulateur):
    """La même carrière, trois enfants : 88 % du traitement, la majoration
    entière, et le détail n'en dit rien."""
    liquidee = _liquider(simulateur, 1955, 22.0, 62.0, 3)
    pension, majoration, traitement, _ = _mesure(liquidee)
    assert majoration == pytest.approx(0.10 * pension)
    avantage = next(a for a in liquidee.complements.avantages if a.code == "majoration_enfants")
    assert "bornée" not in avantage.detail


@pytest.mark.parametrize(("enfants", "bornee"), [(7, False), (8, True)])
def test_au_taux_de_75_pour_cent_le_plafond_mord_a_huit_enfants(simulateur, enfants, bornee):
    """Le père, sans bonification, entré à vingt ans et parti à soixante-deux
    en 2017, a 75 % : sept enfants le portent à 97,5 % du traitement, huit à
    101,25 %, ramenés à 100 %."""
    liquidee = _liquider(simulateur, 1955, 20.0, 62.0, enfants, sexe="H")
    pension, majoration, traitement, _ = _mesure(liquidee)
    assert pension == pytest.approx(0.75 * traitement)
    attendu = traitement if bornee else pension * (1.10 + 0.05 * (enfants - 3))
    assert pension + majoration == pytest.approx(attendu)


def test_avant_la_decision_la_surcote_portee_au_plafond_perd_la_majoration(simulateur):
    """Née en 1950, partie à soixante-sept ans en 2017, trois enfants : sa
    surcote de 35 % porte sa pension à 108 % du traitement. Comme l'inspectrice
    générale de la décision du Conseil d'État, partie la même année à 104 %, la
    majoration ne lui est pas servie, et sa pension n'est pas réduite."""
    liquidee = _liquider(simulateur, 1950, 22.0, 67.0, 3)
    pension, majoration, traitement, surcote = _mesure(liquidee)
    assert pension == pytest.approx(1.08 * traitement)
    assert surcote == pytest.approx(pension - 0.80 * traitement)
    assert majoration == 0.0
    assert not any(a.code == "majoration_enfants" for a in liquidee.complements.avantages)


def test_depuis_la_decision_la_surcote_reste_hors_du_plafond(simulateur):
    """Née en 1954, partie à soixante-sept ans en 2021 : sa surcote porte sa
    pension à 101 % du traitement, et la majoration de 10 % lui est servie
    entière, la pension sans sa surcote, majorée, restant sous le traitement."""
    liquidee = _liquider(simulateur, 1954, 22.0, 67.0, 3)
    pension, majoration, traitement, surcote = _mesure(liquidee)
    assert pension > traitement
    assert surcote > 0.0
    assert majoration == pytest.approx(0.10 * pension)


def test_huit_enfants_et_une_surcote_le_traitement_puis_la_surcote(simulateur):
    """Née en 1955, partie à soixante-sept ans en 2022, huit enfants : sans sa
    surcote, sa pension majorée dépasserait déjà le traitement. La pension et la
    majoration y sont bornées, la surcote servie au-delà : 100 % et 20 % de
    surcote, 120 % du traitement (« Pension + ME = 100 % ; surcote servie sans
    plafond », CNRACL)."""
    liquidee = _liquider(simulateur, 1955, 22.0, 67.0, 8)
    pension, majoration, traitement, surcote = _mesure(liquidee)
    assert surcote == pytest.approx(0.20 * traitement)
    assert pension + majoration == pytest.approx(traitement + surcote)


def test_le_cas_du_conseil_d_etat():
    """Une surcote de 30 % qui porte à 104 % du traitement une pension de
    80 %, une majoration de 10 % (point 11) : refusée avant la décision,
    servie entière depuis, 114,4 % du traitement."""
    traitement, pension = 100.0, 104.0
    surcote = pension - 80.0
    majoration = 0.10 * pension
    assert completer.majoration_sous_le_traitement(
        pension, majoration, traitement, surcote, hors_du_plafond=False) == 0.0
    assert completer.majoration_sous_le_traitement(
        pension, majoration, traitement, surcote, hors_du_plafond=True) == pytest.approx(10.4)


@pytest.mark.parametrize(("naissance", "depart", "enfants"),
                         [(1955, 62.0, 8), (1955, 62.0, 3), (1950, 67.0, 3)])
def test_avant_2021_le_modele_rejoue_destinie_2(simulateur, naissance, depart, enfants):
    """Jusqu'à la décision, le modèle rejoue la formule de Destinie 2 :
    ``tauxmajo_fp = max(0, min(0,1 + 0,05 (n − 3), sr_fp/pension_fp − 1))``,
    la surcote comprise."""
    pension, majoration, traitement, _ = _mesure(_liquider(simulateur, naissance, 22.0,
                                                           depart, enfants))
    taux = max(0.0, min(0.10 + 0.05 * (enfants - 3), traitement / pension - 1.0))
    assert majoration == pytest.approx(taux * pension)


def test_le_minimum_garanti_efface_la_surcote_et_la_surcote_parentale_s_y_ajoute():
    """La pension que le minimum garanti remplace n'a plus de surcote ; la
    fonction se lit sur la part de la surcote que l'étape lui passe : nulle, la
    pension entière se compare au traitement."""
    assert completer.majoration_sous_le_traitement(
        95.0, 9.5, 100.0, 0.0, hors_du_plafond=True) == pytest.approx(5.0)
    assert completer.majoration_sous_le_traitement(
        95.0, 9.5, 100.0, 15.0, hors_du_plafond=True) == pytest.approx(9.5)


@pytest.mark.parametrize(("date_effet", "version"), [
    ("1963-12-01", "avant_le_code_de_1964"), ("1964-01-01", "code_de_1964"),
    ("1982-08-01", "code_de_1982"), ("2012-01-01", "loi_de_finances_pour_2012"),
    ("2020-12-01", "loi_de_finances_pour_2012"),
    ("2021-01-01", "conseil_d_etat_du_29_decembre_2020")])
def test_les_versions_se_lisent_a_la_date_d_effet(simulateur, date_effet, version):
    """Avant le code de 1964, non lu, aucun plafond ; la surcote hors du plafond
    pour les pensions qui prennent effet depuis la décision."""
    lue = simulateur.scenario_actuel.fiches_datees.version(completer.FICHE_DU_PLAFOND_L18,
                                                          date_effet)
    assert lue["id"] == version
    parametres = lue["parametres"]
    assert parametres["existe"] is (version != "avant_le_code_de_1964")
    if parametres["existe"]:
        assert parametres["surcote"] == ("hors_du_plafond" if date_effet >= "2021"
                                         else "dans_le_plafond")


def test_sans_la_fiche_la_majoration_n_est_pas_bornee(simulateur):
    """Retirer la fiche (la contrefactuelle du module des avantages) rend la
    majoration entière : 108 % du traitement pour huit enfants."""
    sans = ScenarioActuel(simulateur.macro, simulateur.catalogue,
                          simulateur.affiliations, simulateur.parametres)
    sans.fiches_datees = sans.fiches_datees.sans(completer.FICHE_DU_PLAFOND_L18)
    liquidee = _liquider(simulateur, 1955, 22.0, 62.0, 8, moteur=sans)
    pension, majoration, traitement, _ = _mesure(liquidee)
    assert pension + majoration == pytest.approx(1.08 * traitement)


def test_un_plafond_inconnu_arrete_le_calcul(simulateur, monkeypatch):
    """Un plafond ou une surcote que le moteur ne connaît pas l'arrête."""
    actuel = simulateur.scenario_actuel
    fiche = actuel.fiches_datees.fiches()[completer.FICHE_DU_PLAFOND_L18]
    derniere = fiche["versions"][-1]
    monkeypatch.setitem(derniere, "parametres", {**derniere["parametres"], "surcote": "moitie"})
    with pytest.raises(ValueError, match="surcote inconnue"):
        _liquider(simulateur, 1955, 22.0, 67.0, 8)


def test_la_liquidation_ecrit_le_traitement_dans_son_schema(simulateur):
    """Ce que le plafond lit, l'étape de la liquidation l'écrit sous son
    schéma : le traitement de la pension civile et ce que la surcote y
    ajoute ; le RAFP, qui n'est pas du code des pensions, n'en porte pas."""
    liquidee = _liquider(simulateur, 1955, 22.0, 67.0, 8)
    donnees = liquidee.pensions.donnees()
    validateur = contrats.Validateur("liquider_chaque_regime", contrats.ETAPES)
    assert [str(c) for c in validateur.valider(donnees, "pensions")
            if c.genre == "erreur"] == []
    portes = {p["regime"]: p.get("plafond_enfants") for p in donnees["regimes"]}
    assert portes[ETAT]["traitement"] > 0 and portes[ETAT]["surcote"] > 0
    assert portes["rafp"] is None
