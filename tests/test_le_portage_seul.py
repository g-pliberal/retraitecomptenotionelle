"""La grille ne se date et ne se bâtit plus qu'au portage (action 161, point 3
du tri des scripts et des modules) : les replis « le moteur Python sinon » de
``castypes``, du coût, de la décomposition des avantages et des départs de
``facteurs_depense`` sont retirés. Un cas type que le portage ne date pas
(``castypes.decrit_au_portage``) y est refusé, au lieu de se dater, de se
bâtir ou de se liquider au moteur Python ; et l'âge légal que
``facteurs_depense.dates_a_l_age_legal`` oppose aux cohortes se lit au
portage."""

from __future__ import annotations

import shutil
import sys
from dataclasses import fields
from pathlib import Path

import pytest

from retraite_notionnelle import avantages, castypes, cout, facteurs_depense
from retraite_notionnelle.castypes import GRILLE_DU_COUT, CasType
from retraite_notionnelle.config import Parametres
from facade import Simulateur

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class Recrite(CasType):
    """Un cas type qui récrit sa carrière sans récrire ce qu'il passe au
    portage : le portage ne le date pas."""

    def _carriere(self, simulateur, generation, age_liquidation):
        return super()._carriere(simulateur, generation, age_liquidation)


def _recrit() -> Recrite:
    modele = GRILLE_DU_COUT[0]
    return Recrite(**{f.name: getattr(modele, f.name) for f in fields(CasType) if f.init})


def test_le_cas_type_recrit_n_est_pas_decrit_au_portage():
    assert not castypes.decrit_au_portage(Recrite)
    assert castypes.decrit_au_portage(CasType)


def test_les_cases_et_les_ages_de_la_grille_refusent_un_cas_type_hors_du_portage():
    simulateur = Simulateur(Parametres())
    with pytest.raises(ValueError, match="portage"):
        castypes.cases_de_la_grille(simulateur, (_recrit(),), (1960,))
    with pytest.raises(ValueError, match="portage"):
        castypes.ages_de_la_grille(simulateur, (_recrit(),), (1960,))


def test_la_grille_du_cout_refuse_un_cas_type_hors_du_portage():
    projection = Simulateur(Parametres()).pour_la_projection()
    with pytest.raises(ValueError, match="portage"):
        cout._grille_batie(projection, (_recrit(),), "droit")


def test_les_departs_des_cohortes_refusent_un_cas_type_hors_du_portage():
    with pytest.raises(ValueError, match="portage"):
        facteurs_depense.dates_des_departs(Parametres(), cas_types=(_recrit(),),
                                           generations=(1960,))


def test_la_decomposition_des_avantages_refuse_un_cas_type_hors_du_portage(monkeypatch):
    monkeypatch.setattr(avantages, "CAS_TYPES", (_recrit(),))
    simulateur = Simulateur(Parametres())
    with pytest.raises(ValueError, match="portage"):
        avantages.decomposer(simulateur)
    with pytest.raises(ValueError, match="portage"):
        avantages.ages_legaux(simulateur, [])


def test_l_age_legal_des_departs_decotes_se_lit_au_portage():
    """``dates_a_l_age_legal`` n'exécute aucune règle du moteur Python (la
    sonde du retrait), et oppose l'âge légal de la loi de 2010 : le salarié né
    en janvier 1960, au taux plein après 62 ans, part à 62 ans, sa pension
    prenant effet le premier jour du mois qui suit (février 2022)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    import sonde_moteur_python as sonde

    salarie = next(cas for cas in GRILLE_DU_COUT if cas.code == "salaire_moyen")
    lues = {}
    assert sonde.sonder(lambda: lues.update(facteurs_depense.dates_a_l_age_legal(
        Parametres(), cas_types=(salarie,), generations=(1960,)))) == []
    date = lues[("salaire_moyen", 1960, 0)]
    assert (date.annee, date.mois) == (2022, 2)
