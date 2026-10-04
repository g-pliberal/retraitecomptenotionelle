"""Le net d'une pension : la cotisation maladie de 1 % des complémentaires.

Le scénario 1 prélève 9,1 % de CSG, de CRDS et de CASA sur toute pension, et
1 % de plus sur ce que servent les complémentaires de salariés (L. 131-2, 1° ;
D. 242-8), majoration pour enfants exclue. Les cinq scénarios notionnels gardent
le taux qui en résulte pour la même personne : c'est l'hypothèse que la réforme
ne change pas ses prélèvements, décidée par le propriétaire le 4 octobre 2026
(action 138, étape 2 ; fiche ``cotisation_maladie_pensions_complementaires``).
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.contexte import Contexte, Montants
from retraite_notionnelle.remuneration import assiette_maladie, charger_prelevements
from retraite_notionnelle.saisie import Saisie

RACINE = Path(__file__).resolve().parents[1]

PRIVE = {"naissance": "1985-03-01", "sexe": "F", "statut": "salarie_prive_non_cadre",
         "debut": "2007-09-01", "liquidation": "2049-03-01",
         "unite_revenu": "moyen", "salaire": "1", "montants": "net"}


@pytest.fixture(scope="module")
def contexte() -> Contexte:
    return Contexte()


@pytest.fixture(scope="module")
def pensions(contexte):
    return charger_prelevements(contexte.base.racine_donnees).pensions


def _simuler(contexte, requete):
    saisie = Saisie.depuis_requete(requete)
    comparaison = contexte.simuler(saisie)
    return comparaison, Montants.depuis(saisie, contexte.base, comparaison)


def test_le_taux_et_les_regimes_sont_ceux_du_fichier(pensions):
    """1 %, sur des régimes que l'inventaire connaît : un code mal écrit ne
    prélèverait rien, et sans bruit. Ni la base du régime général, que D. 242-8
    excepte, ni un indépendant, que L. 131-2 exclut, ni la fonction publique."""
    assert pensions.maladie_complementaire == pytest.approx(0.01)
    inventaire = yaml.safe_load(
        (RACINE / "data/reference/regimes/inventaire.yaml").read_text(encoding="utf-8"))
    connus = {ligne["code"] for ligne in inventaire["inventaire"]}
    assert pensions.regimes_maladie <= connus, sorted(pensions.regimes_maladie - connus)
    assert {"agirc_arrco", "ircantec"} <= pensions.regimes_maladie
    assert not pensions.regimes_maladie & {
        "regime_general", "msa_salaries", "rci", "fonction_publique_etat", "cnracl",
        "rafp", "cnbf_complementaire"}


def test_le_scenario_1_paie_le_1_pour_cent_sur_sa_complementaire(contexte, pensions):
    """La pension nette du scénario 1 est la brute, moins 9,1 % du tout, moins
    1 % de ce que servent les complémentaires."""
    comparaison, montants = _simuler(contexte, PRIVE)
    actuel = comparaison.actuel
    assert comparaison.aujourd_hui is None
    complementaire = sum(p.montant for p in actuel.pensions_par_regime
                         if p.regime in pensions.regimes_maladie)
    total = actuel.pension_annuelle
    assert 0 < complementaire < total
    attendu = total - pensions.taux_total * total - 0.01 * complementaire
    assert montants.pension(total) == pytest.approx(attendu, rel=1e-12)
    assert montants.pension_servie(actuel) == pytest.approx(attendu, rel=1e-12)
    assert montants.part_maladie == pytest.approx(complementaire / total)


def test_un_retraite_paie_sur_sa_complementaire_d_aujourd_hui(contexte, pensions):
    """Pour qui est déjà parti, la page affiche la pension de cette année : la
    part complémentaire est celle de l'échéance, régime par régime revalorisé."""
    comparaison, montants = _simuler(contexte, {
        "naissance": "1952-06-01", "statut": "salarie_prive_non_cadre",
        "debut": "1972-09", "liquidation": "2014-07",
        "unite_revenu": "moyen", "salaire": "1", "montants": "net"})
    servie = comparaison.aujourd_hui.actuel
    complementaire = sum(r.aujourd_hui for r in servie.regimes
                         if r.regime in pensions.regimes_maladie)
    assert complementaire > 0
    assert montants.part_maladie == pytest.approx(
        complementaire / servie.pension_annuelle)


def test_sans_complementaire_le_taux_est_celui_d_une_pension_de_base(contexte, pensions):
    """Un fonctionnaire de l'État n'a pas de complémentaire qui la prélève."""
    _, montants = _simuler(contexte, {**PRIVE, "statut": "fonctionnaire_etat"})
    assert montants.part_maladie == 0.0
    assert montants.taux_pension == pensions.taux_total


def test_les_cinq_autres_gardent_le_taux_de_la_personne(contexte):
    """Le net de chaque scénario garde le rapport de son brut à celui du
    scénario 1 : seul le calcul de la pension les sépare, et non une
    cotisation que le compte notionnel aurait perdue."""
    comparaison, montants = _simuler(contexte, PRIVE)
    actuel = comparaison.actuel.pension_annuelle
    for resultat in (comparaison.notionnel_retroactif, comparaison.notionnel_prospectif,
                     comparaison.notionnel_retroactif_employeur,
                     comparaison.notionnel_prospectif_employeur,
                     comparaison.notionnel_liberal):
        brut = resultat.pension_annuelle
        assert montants.pension(brut) / montants.pension(actuel) == pytest.approx(
            brut / actuel, rel=1e-12)


def test_la_majoration_pour_enfants_reste_hors_de_l_assiette(contexte, pensions):
    """L. 131-2, 1° exclut de l'assiette « les bonifications ou majorations pour
    enfants » : la majoration de l'Agirc-Arrco ne paie pas le 1 %. Le moteur la
    compte à côté des lignes des régimes, que l'assiette seule additionne."""
    comparaison, _ = _simuler(contexte, {**PRIVE, "enfants": "3"})
    actuel = comparaison.actuel
    majorations = [a for a in actuel.avantages_appliques if a.code == "majoration_enfants"]
    assert sum(part for a in majorations for code, part in a.par_regime
               if code in pensions.regimes_maladie) > 0
    assiette, total = assiette_maladie(pensions.regimes_maladie, actuel)
    assert assiette == pytest.approx(sum(
        p.montant for p in actuel.pensions_par_regime if p.regime in pensions.regimes_maladie))
    assert sum(p.montant for p in actuel.pensions_par_regime) + sum(
        a.montant for a in majorations) == pytest.approx(total)


def test_une_ligne_paie_le_taux_de_son_regime(pensions):
    """Une ligne de réversion, un étage : 10,1 % pour une complémentaire qui
    prélève la cotisation, 9,1 % sinon ; rien en brut."""
    montants = Montants(net=True, taux_pension=pensions.taux_total + 0.0025,
                        taux_sans_maladie=pensions.taux_total, taux_maladie=0.01,
                        part_maladie=0.25, regimes_maladie=pensions.regimes_maladie)
    assert montants.pension_du_regime(1000.0, "agirc_arrco") == pytest.approx(
        1000.0 * (1 - pensions.taux_total - 0.01))
    assert montants.pension_du_regime(1000.0, "regime_general") == pytest.approx(
        1000.0 * (1 - pensions.taux_total))
    assert dataclasses.replace(montants, net=False).pension_du_regime(
        1000.0, "agirc_arrco") == 1000.0


@pytest.mark.parametrize("requete", [
    {"saisie_par": "pension", "pension": "1800", "naissance": "1955-01-01",
     "debut": "1975-01", "liquidation": "2017-01", "montants": "net"},
    {"saisie_par": "pension", "pension": "1800", "naissance": "1975-01-01",
     "debut": "1996-01", "liquidation": "2039-01", "montants": "net"},
], ids=["retraite", "actif"])
def test_une_pension_saisie_nette_se_retrouve(contexte, requete):
    """La saisie par pension compare des nets : le taux qui sépare une pension
    de sa nette dépend de sa part complémentaire, donc du niveau cherché, et la
    nette de la carrière trouvée vaut ce qu'on a tapé."""
    comparaison, montants = _simuler(contexte, requete)
    if comparaison.aujourd_hui is not None:
        nette = montants.pension_servie(comparaison.actuel, comparaison.aujourd_hui.actuel)
        mensuelle = comparaison.aujourd_hui_en_euros_constants(nette) / 12
    else:
        nette = montants.pension_servie(comparaison.actuel)
        mensuelle = nette * comparaison.coefficient_euros_constants / 12
    assert montants.part_maladie > 0
    assert mensuelle == pytest.approx(1800.0, abs=1.0)
