"""Les lectures de la décision 29, la dépense suivant le taux cotisé (action 186, chantier 1).

Un cas posé à la main, sur deux années, où chaque taux se trouve en une
ligne. Le droit en vigueur dépense 14 points de PIB et en encaisse 12, dont
8 de cotisations sur une assiette de 40 : il prélève 20 %. La proposition
dépense 10 points la première année, quel que soit le taux, et
0,07 + 0,2 × taux la seconde, quand les premières pensions cotisées au
nouveau taux sont servies. Rendre aux cotisants coûte (0,20 − taux) × 0,40.

- Tout au déficit, rien n'est rendu : le taux reste 20 %.
- Lecture A, la moitié de l'économie rendue : (0,06 − 0,4 t) + (0,045 − 0,3 t)
  = 0, soit t = 15 %.
- Lecture B, le solde à la moitié du déficit : (−0,05 + 0,4 t) + (−0,02 + 0,2 t)
  = 0, soit t = 7/60.
- Lecture B hors des versements de l'État (3 points) : (−0,065 + 0,4 t)
  + (−0,035 + 0,2 t) = 0, soit t = 1/6.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lectures_decision_29 import Annee, Etude  # noqa: E402


def _etude() -> Etude:
    annees = [Annee(annee=a, depense_actuel=0.14, solde_actuel=-0.02,
                    cotisations_actuel=0.08, assiette=0.40, versements_etat=0.03,
                    pib=2_000_000.0, croissance=0.02, taux_dette=0.03)
              for a in (2026, 2027)]
    depenses = {0.10: {2026: 0.10, 2027: 0.09}, 0.20: {2026: 0.10, 2027: 0.11}}
    return Etude(annees, depenses)


def test_tout_au_deficit_garde_le_taux_du_droit_en_vigueur():
    assert _etude().resoudre("tout") == pytest.approx(0.20, abs=1e-9)


def test_la_lecture_a_rend_la_moitie_de_l_economie():
    assert _etude().resoudre("A") == pytest.approx(0.15, abs=1e-9)


def test_la_lecture_b_divise_le_deficit_par_deux_en_moyenne():
    etude = _etude()
    taux = etude.resoudre("B")
    assert taux == pytest.approx(7 / 60, abs=1e-9)
    soldes = [ligne.solde for ligne in etude.trajectoire(taux)]
    assert soldes == pytest.approx([-1 / 75, -1 / 150])
    assert sum(soldes) / 2 == pytest.approx(-0.02 / 2)


def test_la_lecture_b_hors_des_versements_de_l_etat_divise_un_deficit_plus_grand():
    assert _etude().resoudre("B_hors_etat") == pytest.approx(1 / 6, abs=1e-9)


def test_la_depense_suit_le_taux_entre_les_taux_calcules():
    etude = _etude()
    assert etude.depense(2026, 0.15) == pytest.approx(0.10)
    assert etude.depense(2027, 0.15) == pytest.approx(0.07 + 0.2 * 0.15)
    with pytest.raises(ValueError):
        etude.depense(2027, 0.25)


def test_la_dette_refait_la_recurrence_du_cout():
    lignes = _etude().trajectoire(7 / 60)
    assert [ligne.dette for ligne in lignes] == pytest.approx(
        [1 / 75, (1 / 75) * 1.03 / 1.02 + 1 / 150])
    assert lignes[0].rendu == pytest.approx(1 / 30)
    assert lignes[0].rendu_md == pytest.approx(2000 / 30)
    assert lignes[0].points == pytest.approx(0.20 - 7 / 60)


def test_tenue_une_annee_seule_la_regle_donne_le_taux_de_cette_annee():
    etude = _etude()
    assert etude.resoudre("B", annees=(2026,)) == pytest.approx(0.125, abs=1e-9)
    assert etude.resoudre("B", annees=(2027,)) == pytest.approx(0.10, abs=1e-9)


# -- Les recettes de la page Coût, ou sans les impôts affectés ------------------
#
# Le même cas, avec ce que la page Coût compte : la retraite ne garde, outre
# ses cotisations, qu'un point de PIB (ni impôts affectés, ni versements de
# l'État), et la garantie vieillesse, un point, se compte à part. Recettes
# 0,01 + 0,4 t ; dépense 0,09 la première année, 0,06 + 0,2 t la seconde.
#
# - Tout au déficit : (−0,11 + 0,4 t) × 2 = 0, soit t = 27,5 %.
# - Lecture A : (−0,085 + 0,4 t) + (−0,07 + 0,3 t) = 0, soit t = 31/140.
# - Lecture B : (−0,07 + 0,4 t) + (−0,04 + 0,2 t) = 0, soit t = 11/60.
# - Lecture B, le déficit compté sans les versements de l'État (3 points),
#   qu'elle ne reçoit plus : (−0,055 + 0,4 t) + (−0,025 + 0,2 t) = 0, t = 2/15.
#
# Sans les impôts affectés (2 points), les autres recettes gardées : recettes
# 0,02 + 0,4 t, dépense garantie comprise ; lecture A : (−0,08 + 0,4 t)
# + (−0,065 + 0,3 t) = 0, soit t = 29/140.


def _etude_sous(convention: str) -> Etude:
    annees = [Annee(annee=a, depense_actuel=0.14, solde_actuel=-0.02,
                    cotisations_actuel=0.08, assiette=0.40, versements_etat=0.03,
                    pib=2_000_000.0, croissance=0.02, taux_dette=0.03,
                    impots_affectes=0.02, recettes_proposition=0.01)
              for a in (2026, 2027)]
    depenses = {0.10: {2026: 0.10, 2027: 0.09}, 0.20: {2026: 0.10, 2027: 0.11},
                0.30: {2026: 0.10, 2027: 0.13}}
    garanties = {taux: {2026: 0.01, 2027: 0.01} for taux in depenses}
    return Etude(annees, depenses, garanties=garanties, convention=convention)


def test_sur_la_base_de_la_page_cout_chaque_lecture_demande_plus():
    etude = _etude_sous("page_cout")
    assert etude.resoudre("tout") == pytest.approx(0.275, abs=1e-9)
    assert etude.resoudre("A") == pytest.approx(31 / 140, abs=1e-9)
    assert etude.resoudre("B") == pytest.approx(11 / 60, abs=1e-9)
    assert etude.resoudre("B_hors_etat") == pytest.approx(2 / 15, abs=1e-9)


def test_la_page_cout_compte_la_garantie_a_part():
    lignes = _etude_sous("page_cout").trajectoire(0.20)
    assert [ligne.solde for ligne in lignes] == pytest.approx([-0.08 + 0.08, -0.05 + 0.04])
    assert lignes[0].depense == pytest.approx(0.09)


def test_sans_les_impots_affectes_la_lecture_a_tombe_entre_les_deux():
    assert _etude_sous("impots_supprimes").resoudre("A") == pytest.approx(29 / 140, abs=1e-9)


def test_les_recettes_gardees_restent_la_convention_du_premier_calcul():
    assert _etude_sous("recettes_gardees").resoudre("A") == pytest.approx(0.15, abs=1e-9)


# -- Des recettes nouvelles : la LVT et la part de TVA (décisions 79 et 80) -----
#
# Deux points de PIB de plus chaque année, sur la base de la page Coût :
# solde −0,06 + 0,4 t la première année, −0,03 + 0,2 t la seconde. Lecture A :
# (−0,065 + 0,4 t) + (−0,05 + 0,3 t) = 0, soit t = 23/140 ; le taux baisse.


def test_des_recettes_nouvelles_baissent_le_taux_de_chaque_lecture():
    annees = [Annee(annee=a, depense_actuel=0.14, solde_actuel=-0.02,
                    cotisations_actuel=0.08, assiette=0.40, versements_etat=0.03,
                    pib=2_000_000.0, croissance=0.02, taux_dette=0.03,
                    impots_affectes=0.02, recettes_proposition=0.01)
              for a in (2026, 2027)]
    depenses = {0.10: {2026: 0.10, 2027: 0.09}, 0.20: {2026: 0.10, 2027: 0.11},
                0.30: {2026: 0.10, 2027: 0.13}}
    garanties = {taux: {2026: 0.01, 2027: 0.01} for taux in depenses}
    etude = Etude(annees, depenses, garanties=garanties, convention="page_cout",
                  recettes_en_plus=0.02)
    assert etude.resoudre("A") == pytest.approx(23 / 140, abs=1e-9)
    assert etude.trajectoire(0.20)[0].solde == pytest.approx(-0.06 + 0.08)


# La part de TVA gardée et le point de LVT sont au modèle (décisions 79 à 81) :
# la base de la page Coût les porte déjà dans les recettes de la proposition,
# les deux autres conventions les reçoivent de l'année.


def _annee_avec_recettes(**champs) -> Annee:
    valeurs = dict(annee=2026, depense_actuel=0.14, solde_actuel=-0.02,
                   cotisations_actuel=0.08, assiette=0.40, versements_etat=0.03,
                   pib=2_000_000.0, croissance=0.02, taux_dette=0.03,
                   impots_affectes=0.02, recettes_proposition=0.025,
                   tva_gardee=0.002, lvt=0.013)
    valeurs.update(champs)
    return Annee(**valeurs)


@pytest.mark.parametrize("convention, en_plus", [
    # La page Coût : les recettes de la proposition les contiennent déjà.
    ("page_cout", 0.0),
    # Toutes les recettes du droit en vigueur gardées : la TVA en est, la LVT s'ajoute.
    ("recettes_gardees", 0.013),
    # Les impôts affectés supprimés, sauf la part de TVA gardée : les deux s'ajoutent.
    ("impots_supprimes", 0.015),
])
def test_les_recettes_du_modele_ne_se_comptent_qu_une_fois(convention, en_plus):
    depenses = {0.10: {2026: 0.10}, 0.30: {2026: 0.10}}
    garanties = {taux: {2026: 0.01} for taux in depenses}
    avec = Etude([_annee_avec_recettes()], depenses, garanties, convention)
    sans = Etude([_annee_avec_recettes(tva_gardee=0.0, lvt=0.0)], depenses, garanties, convention)
    assert (avec.trajectoire(0.20)[0].solde - sans.trajectoire(0.20)[0].solde
            == pytest.approx(en_plus))


def test_les_cas_types_passent_par_le_portage_sans_le_moteur_python(monkeypatch):
    """L'option ``--cas-types`` date, bâtit et simule ses cas types par le
    portage (``pont.carrieres_de_la_grille``, ``pont.grille_du_cout``, action
    161, lot B), le taux crédité dans les paramètres de la demande : la
    pension du scénario 6 et celle de l'étalon en euros constants, l'année du
    départ et le revenu de 2026, au bit près de ce que le moteur Python en
    simulait, sous le taux du programme et sous un autre — sans qu'il ne
    calcule rien."""
    import shutil

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne calcule pas ici")
    import lectures_decision_29 as L
    from outils_pont import empecher_les_jumeaux_du_cout
    from retraite_notionnelle.castypes import GRILLE_DU_COUT, carriere_de_la_grille
    from retraite_notionnelle.config import Parametres
    from retraite_notionnelle.simulateur import Simulateur

    def du_moteur_python(taux):
        simulateur = Simulateur(Parametres().avec(taux_cotisation_liberal=taux))
        sortie = {}
        for code in L.CAS_TYPES:
            cas = next(c for c in GRILLE_DU_COUT if c.code == code)
            for generation in L.GENERATIONS:
                carriere = carriere_de_la_grille(simulateur, cas, generation)
                resultat = simulateur.simuler(carriere)
                sortie[(code, generation)] = {
                    "libelle": cas.libelle,
                    "pension": resultat.en_euros_constants(
                        resultat.notionnel_liberal.pension_annuelle, L.LIBERAL),
                    "actuel": resultat.en_euros_constants(resultat.actuel.pension_annuelle),
                    "depart": resultat.carriere_de(L.LIBERAL).annee_liquidation,
                    "revenu_2026": next((ligne.revenu for ligne in carriere.lignes
                                         if ligne.annee == 2026), None),
                }
        return sortie

    taux = (L.TAUX_PROGRAMME, 0.1123)
    attendus = {un: du_moteur_python(un) for un in taux}
    # Le taux crédité fait la pension du scénario 6, et elle seule.
    cle = ("salaire_moyen", 1990)
    assert attendus[0.1123][cle]["pension"] < attendus[L.TAUX_PROGRAMME][cle]["pension"]
    assert attendus[0.1123][cle]["actuel"] == attendus[L.TAUX_PROGRAMME][cle]["actuel"]
    empecher_les_jumeaux_du_cout(monkeypatch)
    for un in taux:
        lues = L.pensions_des_cas_types(un)
        assert lues == attendus[un], un
        assert list(lues) == [(code, generation)
                              for code in L.CAS_TYPES for generation in L.GENERATIONS]
