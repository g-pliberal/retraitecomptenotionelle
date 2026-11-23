"""La part salariale de l'Agirc-Arrco est celle que le régime publie.

Depuis 2019, l'Agirc-Arrco appelle 7,87 % sur la tranche 1 et 21,59 % sur la
tranche 2, que le salarié paie à 3,15 % et à 8,64 %, l'employeur à 4,72 % et à
12,95 % : la répartition à 40 et 60 % de l'ANI du 17 novembre 2017, arrondie
par le régime au centième de point, comme le publient l'Agirc-Arrco et le
simulateur de l'Urssaf, et comme la fiche de paie l'applique. Une part
salariale de 40 % du taux appelé donnait 3,148 % et 8,636 % : cinq centimes de
moins par mois à 2 500 €, vingt-quatre à 8 000 €. Les montants attendus sont ceux de l'API de mon-entreprise (Urssaf)
au 1er juillet 2026, posés à la main : 2 500 × 3,15 % = 78,75 € ;
4 005 × 3,15 % + 3 995 × 8,64 % = 471,3255 €, le plafond mensuel étant de
4 005 €.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.donnees.macro import DonneesMacro
from retraite_notionnelle.donnees.regimes import CatalogueRegimes, lire_fiche_de_regime
from retraite_notionnelle.remuneration import (
    ConstructeurFiche,
    bloc_droit_en_vigueur,
    charger_prelevements,
    smic_annuel,
)

from facade import Simulateur
from outils_fiches import periodes_ecrites

PARAMETRES = Parametres()
ANNEE = 2026


@pytest.fixture(scope="module")
def pieces():
    macro = DonneesMacro(PARAMETRES.racine_donnees, PARAMETRES.scenario_projection)
    return {
        "catalogue": CatalogueRegimes(PARAMETRES.racine_donnees),
        "affiliations": Simulateur(PARAMETRES).affiliations,
        "bareme": charger_prelevements(PARAMETRES.racine_donnees).profil("salarie_prive"),
        "plafond": macro.plafond_securite_sociale(ANNEE),
        "smic": smic_annuel(macro, ANNEE),
    }


@pytest.mark.parametrize("statut, brut_mensuel, attendu", [
    ("salarie_prive_non_cadre", 2500, 78.75),
    ("salarie_prive_cadre", 2500, 78.75),
    ("salarie_prive_non_cadre", 8000, 471.3255),
    ("salarie_prive_cadre", 8000, 471.3255),
])
def test_la_ligne_agirc_arrco_du_salarie_est_celle_du_bareme_publie(
        pieces, statut, brut_mensuel, attendu):
    bloc = bloc_droit_en_vigueur(
        pieces["catalogue"], pieces["affiliations"], statut, ANNEE)
    fiche = ConstructeurFiche(pieces["bareme"]).fiche(
        ANNEE, brut_mensuel * 12, pieces["plafond"], pieces["smic"], bloc)
    ligne = next(l for l in fiche.lignes if l.code == "agirc_arrco")
    assert ligne.salarie / 12 == pytest.approx(attendu, abs=1e-6)


@pytest.mark.parametrize("annee", [2019, 2024])
@pytest.mark.parametrize("regime, assiette, salarie", [
    ("agirc_arrco", "tranche_1", 0.0315),
    ("agirc_arrco", "tranche_2", 0.0864),
    # La CAVIMAC, qui recouvre pour les cultes, met 4,01 % à la charge de
    # l'assuré sur son taux de base de 10,02 % (circulaire n° 2026/03 du
    # 27 mai 2026) : 3,15 % d'Agirc-Arrco et 0,86 % de contribution d'équilibre.
    ("arrco_cultes", "tranche_1", 0.0315),
])
def test_le_taux_salarial_de_chaque_tranche_est_celui_que_le_regime_publie(
        annee, regime, assiette, salarie):
    fiche = lire_fiche_de_regime(PARAMETRES.racine_donnees / "reference" / "regimes"
                                 / f"{regime}.yaml")
    periodes = [p for p in periodes_ecrites(fiche)
                if p["assiette"] == assiette and p["debut"] == annee]
    assert len(periodes) == 1
    periode = periodes[0]
    assert periode["taux_cotisation_retraite"] * periode["part_salariale"] == pytest.approx(
        salarie, abs=1e-12)
