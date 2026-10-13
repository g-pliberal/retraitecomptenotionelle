"""Les artisans et les commerçants, caisse par caisse (action 138, étape 18).

Le plafond propre du RCI : de 2013 à 2024, la première tranche de la
complémentaire des indépendants (7 %) s'arrête à un plafond que la caisse
publie chaque année, et non au plafond de la sécurité sociale ; la seconde
(8 %) part de lui (D. 635-7, fiche ``rci_seuil_premiere_tranche``). Depuis
2025, le texte coupe au plafond de la sécurité sociale.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees import regimes
from retraite_notionnelle.donnees.regimes import CatalogueRegimes
from retraite_notionnelle.remuneration import (
    ConstructeurFiche, bloc_droit_en_vigueur, charger_prelevements, smic_annuel)
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]

#: Le plafond de cotisation RCI que la caisse a publié chaque année : circulaires
#: Cnav 2020-42 à 2023-33 de 2021 à 2024, publications du RSI puis de la
#: Sécurité sociale des indépendants avant (fiche ``rci_seuil_premiere_tranche``).
PLAFOND_RCI = {
    2013: 37_032, 2014: 37_513, 2015: 37_513, 2016: 37_546, 2017: 37_546,
    2018: 37_846, 2019: 37_960, 2020: 38_340, 2021: 38_493, 2022: 38_916,
    2023: 40_784, 2024: 42_946,
}


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _tranches(catalogue, annee: int):
    premiere, seconde = sorted(catalogue["rci"].periodes_actives(annee),
                               key=lambda p: p.taux_cotisation_retraite)
    return premiere, seconde


def test_le_plafond_du_rci_est_celui_que_la_caisse_publie(simulateur):
    """Chaque année de 2013 à 2024, la première tranche s'arrête au plafond
    publié et la seconde part de lui, jusqu'à quatre plafonds de la sécurité
    sociale de l'année ; en 2013, il vaut le plafond de la sécurité sociale."""
    catalogue = CatalogueRegimes(RACINE_DONNEES)
    for annee, plafond_rci in PLAFOND_RCI.items():
        pss = simulateur.macro.plafond_securite_sociale(annee)
        premiere, seconde = _tranches(catalogue, annee)
        assert premiere.bornes_assiette_en_euros(pss, annee) == (0.0, plafond_rci)
        assert seconde.bornes_assiette_en_euros(pss, annee) == (plafond_rci, 4 * pss)
    assert PLAFOND_RCI[2013] == simulateur.macro.plafond_securite_sociale(2013)


def test_chaque_annee_d_une_periode_a_bornes_annuelles_a_sa_borne():
    """Une année sans montant retomberait sans bruit sur le plafond de la
    sécurité sociale : toute période qui en porte les couvre toutes."""
    for regime in CatalogueRegimes(RACINE_DONNEES):
        for periode in regime.periodes:
            for bornes in (periode.borne_basse_par_annee, periode.borne_haute_par_annee):
                if not bornes:
                    continue
                assert periode.fin is not None, (regime.code, periode.debut)
                assert [annee for annee, _ in bornes] == list(
                    range(periode.debut, periode.fin + 1)), (regime.code, periode.debut)


def test_depuis_2025_la_premiere_tranche_s_arrete_au_plafond_de_la_securite_sociale(
        simulateur):
    """D. 635-7 dans sa rédaction du 7 juillet 2024, pour les périodes courant
    à compter du 1er janvier 2025 : 8,1 % jusqu'au plafond annuel, 9,1 % au-delà."""
    catalogue = CatalogueRegimes(RACINE_DONNEES)
    for annee in (2025, 2026):
        pss = simulateur.macro.plafond_securite_sociale(annee)
        premiere, seconde = _tranches(catalogue, annee)
        assert (premiere.taux_cotisation_retraite, seconde.taux_cotisation_retraite) == (
            pytest.approx(0.081), pytest.approx(0.091))
        assert premiere.bornes_assiette_en_euros(pss, annee) == (0.0, pss)
        assert seconde.bornes_assiette_en_euros(pss, annee) == (pss, 4 * pss)


def test_une_borne_annuelle_exige_l_annee():
    """Sans l'année, la borne propre ne peut pas se lire : le moteur refuse
    plutôt que de couper au plafond de la sécurité sociale."""
    premiere, _ = _tranches(CatalogueRegimes(RACINE_DONNEES), 2019)
    with pytest.raises(ValueError, match="année par année"):
        premiere.bornes_assiette_en_euros(40_524)


def _fiche_rci(simulateur, annee: int, revenu: float) -> float:
    bloc = bloc_droit_en_vigueur(simulateur.catalogue, simulateur.affiliations,
                                 "artisan", annee)
    profil = charger_prelevements(RACINE_DONNEES).profil("independant")
    fiche = ConstructeurFiche(profil).fiche(
        annee, revenu, simulateur.macro.plafond_securite_sociale(annee),
        smic_annuel(simulateur.macro, annee), bloc)
    return next(ligne.salarie for ligne in fiche.lignes if ligne.code == "rci")


def test_la_fiche_de_paie_preleve_au_plafond_propre(simulateur):
    """60 000 € de revenu en 2019 : 7 % de 37 960 €, 8 % de 22 040 €."""
    assert _fiche_rci(simulateur, 2019, 60_000.0) == pytest.approx(
        0.07 * 37_960 + 0.08 * (60_000 - 37_960))


def _pension_rci(simulateur, niveau: float) -> float:
    carriere = Carriere.depuis_parcours(
        annee_naissance=1960, sexe="H",
        metiers=[Metier(affiliation="artisan", age_debut=21.0, niveau_salaire=niveau)],
        age_liquidation=64.0, macro=simulateur.macro)
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return {p.regime: p for p in resultat.pensions_par_regime}["rci"].montant


def test_les_points_du_rci_suivent_le_plafond_propre(simulateur, monkeypatch):
    """Au-dessus du plafond propre, le point de cotisation de plus achète des
    points : la pension RCI d'un artisan né en 1960 gagne quelques millièmes ;
    sous lui, rien ne bouge."""
    propre = {niveau: _pension_rci(simulateur, niveau) for niveau in (0.8, 2.0)}
    monkeypatch.setattr(regimes.PeriodeRegime, "bornes_de_l_annee",
                        lambda self, annee: (None, None))
    au_plafond = {niveau: _pension_rci(Simulateur(), niveau) for niveau in (0.8, 2.0)}
    assert propre[0.8] == pytest.approx(au_plafond[0.8])
    assert 1.001 < propre[2.0] / au_plafond[2.0] < 1.01


#: Le jumeau JavaScript : les mêmes bornes et la même ligne de fiche de paie.
_JUMEAU = """
import { readFileSync } from "node:fs";
import { CatalogueRegimes, Affiliations } from "./moteur/js/regimes.js";
import { BaremePrelevements, ConstructeurFiche, blocDroitEnVigueur }
  from "./moteur/js/remuneration.js";
const { annees, pss, fiche } = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("./moteur/donnees.json", "utf8"));
const catalogue = new CatalogueRegimes(paquet);
const bornes = annees.map((annee, rang) => catalogue.obtenir("rci").periodesActives(annee)
  .map((p) => p.bornesAssietteEnEuros(pss[rang], annee)));
const bloc = blocDroitEnVigueur(catalogue, new Affiliations(paquet), "artisan", fiche.annee);
const profil = new BaremePrelevements(paquet.prelevements_remuneration).profil("independant");
const lignes = new ConstructeurFiche(profil).fiche(
  fiche.annee, fiche.revenu, fiche.pss, fiche.smic, bloc).lignes;
process.stdout.write(JSON.stringify({
  bornes, rci: lignes.find((ligne) => ligne.code === "rci").salarie,
}));
"""


def test_le_portage_javascript_coupe_au_meme_plafond(simulateur):
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    catalogue = simulateur.catalogue
    annees = [*PLAFOND_RCI, 2025, 2026]
    pss = [simulateur.macro.plafond_securite_sociale(annee) for annee in annees]
    fiche = {"annee": 2019, "revenu": 60_000.0, "pss": pss[annees.index(2019)],
             "smic": smic_annuel(simulateur.macro, 2019)}
    attendu = {
        "bornes": [[list(p.bornes_assiette_en_euros(plafond, annee))
                    for p in catalogue["rci"].periodes_actives(annee)]
                   for annee, plafond in zip(annees, pss)],
        "rci": _fiche_rci(simulateur, 2019, 60_000.0),
    }
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _JUMEAU,
         json.dumps({"annees": annees, "pss": pss, "fiche": fiche})],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    obtenu = json.loads(execution.stdout)
    assert obtenu["bornes"] == attendu["bornes"]
    assert obtenu["rci"] == pytest.approx(attendu["rci"], abs=1e-9)
