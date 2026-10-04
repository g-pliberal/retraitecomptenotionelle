"""Le net d'une pension : la tranche de CSG du foyer, et la cotisation maladie.

Le scénario 1 prélève la CSG, la CRDS et la CASA de la tranche que fixe le
revenu fiscal du foyer — dit, ou présumé fait de ses seules pensions —, et 1 %
de plus sur ce que servent les complémentaires de salariés (L. 131-2, 1° ;
D. 242-8 et 242-9), majoration pour enfants exclue, aux deux derniers taux.
L'allocataire de l'ASPA n'est prélevé de rien. Les cinq scénarios notionnels
gardent le taux qui en résulte pour la même personne : l'hypothèse que la
réforme ne change pas ses prélèvements, décidée par le propriétaire le
4 octobre 2026 (action 138, étapes 2 et 13 ; fiches
``cotisation_maladie_pensions_complementaires`` et
``csg_des_pensions_selon_le_revenu``).
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.contexte import Contexte, Montants, couverture_francaise
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
    """La pension nette du scénario 1 est la brute, moins la CSG, la CRDS et la
    CASA de sa tranche sur le tout, moins 1 % de ce que servent les
    complémentaires. Au salaire moyen, présumée seule ressource, la pension
    tombe au taux médian."""
    comparaison, montants = _simuler(contexte, PRIVE)
    actuel = comparaison.actuel
    assert comparaison.aujourd_hui is None
    complementaire = sum(p.montant for p in actuel.pensions_par_regime
                         if p.regime in pensions.regimes_maladie)
    total = actuel.pension_annuelle
    assert 0 < complementaire < total
    tranche = pensions.tranche(montants.revenu_fiscal, montants.parts)
    assert tranche.libelle == montants.tranche == "taux médian"
    attendu = (total - pensions.taux_de_la_tranche(tranche) * total
               - 0.01 * complementaire)
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
    assert montants.taux_pension == montants.taux_sans_maladie


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


@pytest.mark.parametrize("revenu, parts, tranche", [
    (13048, 1, "exonéré"), (13049, 1, "taux réduit"), (17057, 1, "taux réduit"),
    (17058, 1, "taux médian"), (26471, 1, "taux médian"), (26472, 1, "taux plein"),
    (20016, 2, "exonéré"), (20017, 2, "taux réduit"), (40603, 2, "taux médian"),
    (40604, 2, "taux plein"),
])
def test_les_seuils_de_la_csg_par_parts(pensions, revenu, parts, tranche):
    """L. 136-8 : chaque seuil vaut pour la première part, majoré par
    demi-part ; les deux premiers comprennent leur seuil (« n'excède pas »,
    « inférieurs ou égaux »), le taux médian non (« inférieurs »)."""
    assert pensions.tranche(float(revenu), float(parts)).libelle == tranche


def test_l_abattement_de_10_pour_cent(pensions):
    """CGI, art. 158, 5 a : 10 %, au moins 454 € par pensionné, au plus 4 439 €
    pour le foyer."""
    assert pensions.revenu_fiscal_presume([20000.0]) == pytest.approx(18000.0)
    assert pensions.revenu_fiscal_presume([3000.0]) == pytest.approx(3000.0 - 454.0)
    assert pensions.revenu_fiscal_presume([60000.0]) == pytest.approx(60000.0 - 4439.0)
    assert pensions.revenu_fiscal_presume([20000.0, 15000.0]) == pytest.approx(31500.0)
    assert pensions.revenu_fiscal_presume([300.0]) == pytest.approx(0.0)


def test_un_foyer_au_smic_n_est_pas_preleve(contexte):
    """Au SMIC toute sa vie, la pension, seule ressource présumée, reste sous
    le premier seuil : ni CSG, ni CRDS, ni CASA, ni cotisation maladie."""
    _, montants = _simuler(contexte, {**PRIVE, "salaire": "0.45"})
    assert montants.revenu_presume
    assert montants.tranche == "exonéré"
    assert montants.taux_pension == 0.0
    assert montants.pension(1000.0) == 1000.0


def test_le_revenu_dit_remplace_la_presomption(contexte, pensions):
    """Le revenu fiscal que la personne dit fixe seul la tranche."""
    _, montants = _simuler(contexte, {**PRIVE, "revenu_fiscal": "50000"})
    assert not montants.revenu_presume and montants.revenu_fiscal == 50000.0
    assert montants.tranche == "taux plein"
    assert montants.taux_sans_maladie == pytest.approx(pensions.taux_total)


def test_un_conjoint_donne_deux_parts_et_ses_ressources(contexte, pensions):
    """Avec un conjoint déclaré, le foyer a deux parts, et ses ressources
    entrent dans le revenu présumé."""
    comparaison, montants = _simuler(
        contexte, {**PRIVE, "conjoint": "1986", "ressources_conjoint": "15000"})
    assert montants.parts == 2.0
    pension = comparaison.actuel.pension_annuelle * comparaison.coefficient_euros_constants
    assert montants.revenu_fiscal == pytest.approx(
        pensions.revenu_fiscal_presume([pension, 15000.0]))


def test_l_allocataire_de_l_aspa_n_est_preleve_de_rien(contexte):
    """L. 136-1-2, II 1° et D. 242-9, 2° : le titulaire d'un minimum vieillesse
    est exonéré, et l'ASPA ne l'est jamais."""
    comparaison, montants = _simuler(contexte, {
        "naissance": "1955-01-01", "debut": "1995-01", "liquidation": "2022-01",
        "unite_revenu": "moyen", "salaire": "0.3", "montants": "net"})
    assert comparaison.aujourd_hui.actuel.minimum_vieillesse > 0
    assert montants.aspa and montants.taux_pension == 0.0


@pytest.mark.parametrize("pension, tranche", [
    ("1150", "exonéré"), ("1800", "taux médian"), ("3200", "taux plein"),
])
def test_une_pension_saisie_nette_tombe_dans_sa_tranche(contexte, pension, tranche):
    """La saisie par pension tire la tranche de la pension saisie : remontée
    au brut, son revenu présumé est bien celui de la tranche, et la nette de la
    carrière trouvée vaut ce qu'on a tapé."""
    comparaison, montants = _simuler(contexte, {
        "saisie_par": "pension", "pension": pension, "naissance": "1955-01-01",
        "debut": "1975-01", "liquidation": "2017-01", "montants": "net"})
    assert montants.tranche == tranche
    nette = montants.pension_servie(comparaison.actuel, comparaison.aujourd_hui.actuel)
    assert comparaison.aujourd_hui_en_euros_constants(nette) / 12 == pytest.approx(
        float(pension), abs=1.0)


def test_un_non_resident_que_la_france_soigne_paie_la_cotisation_maladie(contexte, pensions):
    """L. 136-1 : hors de France, ni CSG, ni CRDS, ni CASA. L. 131-9 et D. 242-8 :
    qui relève de l'assurance maladie française paie 3,2 % sur la base du
    régime général et 4,2 % sur la complémentaire. En Espagne, sans pension
    espagnole, la France est seule compétente (règlement n° 883/2004, art. 24)."""
    _, montants = _simuler(contexte, {**PRIVE, "residence": "ES"})
    assert montants.non_resident and montants.couvert
    assert montants.motif_couverture == "france_competente"
    assert montants.taux_sans_maladie == 0.0
    assert montants.taux_pension == pytest.approx(
        pensions.non_residents_regime_general * montants.part_regime_general
        + pensions.non_residents_complementaires * montants.part_maladie)
    assert montants.pension_du_regime(1000.0, "regime_general") == pytest.approx(968.0)
    assert montants.pension_du_regime(1000.0, "agirc_arrco") == pytest.approx(958.0)
    assert montants.pension_du_regime(1000.0, "fonction_publique_etat") == 1000.0


def test_l_etat_de_residence_qui_sert_une_pension_soigne(contexte):
    """Règlement n° 883/2004, art. 23 : l'État de résidence qui sert une
    pension prend en charge les soins ; la France ne prélève rien."""
    _, montants = _simuler(contexte, {
        **PRIVE, "residence": "ES", "pension_etrangere1_pays": "ES",
        "pension_etrangere1": "300", "pension_etrangere1_debut": "2049-03"})
    assert montants.non_resident and not montants.couvert
    assert montants.motif_couverture == "residence_competente"
    assert montants.taux_pension == 0.0


def test_hors_de_l_union_quinze_ans_d_assurance_francaise(contexte):
    """L. 160-3, b : hors des règlements européens, la France soigne le
    pensionné dont la pension rémunère quinze années d'assurance."""
    _, montants = _simuler(contexte, {**PRIVE, "residence": "MA"})
    assert montants.couvert and montants.motif_couverture == "quinze_ans"


def test_moins_de_quinze_ans_hors_de_l_union_ne_paie_rien():
    """Sous quinze années d'assurance française, hors de l'Union, la France ne
    prend pas en charge les soins : rien n'est prélevé."""
    saisie = Saisie.depuis_requete({**PRIVE, "residence": "MA"})

    class Actuel:
        trimestres_valides = 70
        trimestres_etrangers = 20

    assert couverture_francaise(saisie, Actuel(), False, 60) == (False, "moins_de_quinze_ans")
    Actuel.trimestres_etrangers = 0
    assert couverture_francaise(saisie, Actuel(), False, 60) == (True, "quinze_ans")
