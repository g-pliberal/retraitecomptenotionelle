"""La fiche de paie connaît la date d'entrée dans le statut.

Un régime fermé ne l'est qu'aux nouveaux entrants. L'agent de la SNCF recruté
avant le 1er janvier 2020 (loi du 27 juin 2018), ceux de la RATP, des IEG, de
la CRPCEN et de la Banque de France recrutés avant le 1er septembre 2023 (loi
n° 2023-270, art. 1er, JORFARTI000047445082), le mineur recruté avant le
1er septembre 2010 (décret n° 2010-975), l'agent de la SEITA en fonctions
avant 1981 (loi n° 84-603, art. 6) gardent leur régime jusqu'à leur retraite ;
le libéral non réglementé installé avant le 1er janvier 2019 reste affilié à
la CNAVPL et à la Cipav (loi n° 2017-1836, art. 15, JORFARTI000036339157). Le
compte et le scénario 1 suivent cette clause du grand-père depuis qu'elle est
écrite (``Affiliations.regimes``, ``annee_entree``) ; la fiche de paie lisait
les régimes d'un nouvel entrant, et prélevait à ces assurés, passé la
fermeture, le régime général et l'Agirc-Arrco, ou le RCI — dans les
indicateurs de cycle de vie comme dans la rémunération de la page (action 138,
étape 9).

Les régimes attendus sont ceux que ces textes gardent ; les montants, ce que le
compte reçoit, qui suit la clause, et un net posé à la main : la retenue de la
fiche ``sncf``, 10,85 % du traitement, la CSG, 9,2 % (L. 136-8, I, 1°), et la
CRDS, 0,5 % (ordonnance n° 96-50, art. 19), sur 98,25 % du salaire
(L. 136-1-1, III, 1°).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.config import PartCotisation
from retraite_notionnelle.cycle_de_vie import revenus_nets
from retraite_notionnelle.moteur.compte import ConstructeurCompte
from retraite_notionnelle.remuneration import (
    famille_du_statut, fiche_depuis_brut, profil_de_la_fiche, salaire_brut_depuis_net,
    salaire_net_depuis_brut)
from retraite_notionnelle.simulateur import Simulateur

PARAMETRES = Parametres()
RACINE = Path(__file__).resolve().parents[1]
REVENU = 40_000.0


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(PARAMETRES)


def _fiche(simulateur: Simulateur, statut: str, annee: int, revenu: float,
           entree: int | DateMois | None = None):
    return fiche_depuis_brut(PARAMETRES.racine_donnees, simulateur.macro,
                             simulateur.catalogue, simulateur.affiliations,
                             statut, annee, revenu, annee_entree=entree)


def _regimes(simulateur: Simulateur, fiche) -> set[str]:
    """Les régimes dont la fiche prélève la retraite."""
    return {ligne.code for ligne in fiche.lignes
            if ligne.retraite and ligne.code in simulateur.catalogue}


#: Les statuts fermés : l'entrée d'un assuré qui garde son régime, l'année de
#: la fermeture, une année où il l'a gardé, ses régimes, et ceux du nouvel
#: entrant de la même année.
FERMES = (
    ("agent_sncf", 1996, 2020, 2026, {"sncf"}, {"regime_general", "agirc_arrco"}),
    ("agent_ratp", 1996, 2023, 2026, {"ratp"}, {"regime_general", "agirc_arrco"}),
    ("agent_ieg", DateMois(2023, 8), 2023, 2026, {"ieg"},
     {"regime_general", "agirc_arrco"}),
    ("clerc_de_notaire", 1996, 2023, 2026, {"crpcen"}, {"regime_general", "agirc_arrco"}),
    ("agent_banque_de_france", 1996, 2023, 2026, {"banque_de_france"},
     {"regime_general", "agirc_arrco"}),
    ("mineur", 1985, 2010, 2015, {"mines"}, {"regime_general", "arrco", "arrco_tranche_2"}),
    ("agent_seita", 1970, 1981, 1990, {"seita"},
     {"regime_general", "arrco", "arrco_tranche_2"}),
    ("liberal_non_reglemente", 2005, 2019, 2026, {"cnavpl", "cipav_complementaire"},
     {"regime_general", "rci"}),
)


@pytest.mark.parametrize("statut, entree, fermeture, annee, gardes, nouveaux", FERMES,
                         ids=[cas[0] for cas in FERMES])
def test_la_fiche_preleve_les_regimes_de_la_date_d_entree(
        simulateur, statut, entree, fermeture, annee, gardes, nouveaux):
    """Entré avant la fermeture, l'assuré paie son régime ; sans date
    d'entrée, la fiche reste celle d'un nouvel entrant, la seule que la page
    sache demander tant qu'elle ne lui passe pas l'entrée du métier."""
    assert _regimes(simulateur, _fiche(simulateur, statut, annee, REVENU, entree)) == gardes
    assert _regimes(simulateur, _fiche(simulateur, statut, annee, REVENU)) == nouveaux


@pytest.mark.parametrize("statut, entree, fermeture, annee, gardes, nouveaux", FERMES,
                         ids=[cas[0] for cas in FERMES])
def test_la_fiche_de_qui_garde_son_regime_preleve_ce_que_le_compte_recoit(
        simulateur, statut, entree, fermeture, annee, gardes, nouveaux):
    """Un revenu constant depuis l'entrée : de deux ans avant la fermeture, ou
    de l'entrée, à 2029, chaque ligne de retraite de la fiche vaut ce que le compte reçoit de
    l'assuré pour ce régime. Le relevé de la fiche et du compte, statut par
    statut, n'y laissait que les années d'après la fermeture."""
    debut = entree.annee if isinstance(entree, DateMois) else entree
    carriere = Carriere(
        annee_naissance=debut - 22, sexe="H", age_liquidation=95,
        lignes=[AnneeCarriere(annee=an, affiliation=statut, trimestres_valides=4,
                              revenu=REVENU) for an in range(debut, 2030)],
        dates_entree={statut: entree if isinstance(entree, DateMois)
                      else DateMois(entree, 1)})
    compte = ConstructeurCompte(
        simulateur.macro, simulateur.catalogue, simulateur.affiliations,
        simulateur.indexation, PARAMETRES.avec(part_cotisation=PartCotisation.SALARIALE))
    ecarts = []
    for an in range(max(debut, fermeture - 2), 2030):
        recu = dict(compte.cotisation_annuelle(carriere, an).par_regime)
        preleve = {ligne.code: ligne.salarie
                   for ligne in _fiche(simulateur, statut, an, REVENU,
                                       carriere.date_entree(statut)).lignes
                   if ligne.retraite}
        for code in sorted(set(recu) | set(preleve)):
            if abs(recu.get(code, 0.0) - preleve.get(code, 0.0)) > 0.01:
                ecarts.append((an, code, recu.get(code, 0.0), preleve.get(code, 0.0)))
    assert not ecarts, ecarts[:5]


def test_le_profil_et_la_famille_sont_ceux_du_regime_garde(simulateur):
    """L'agent de la SNCF entré en 1996 garde la fiche d'un régime qui ne
    porte que la retenue de l'agent, celle qu'il avait en 2019 ; le libéral
    installé en 2005, la famille des libéraux de la CNAVPL."""
    affiliations, catalogue = simulateur.affiliations, simulateur.catalogue
    assert profil_de_la_fiche(affiliations, catalogue, "agent_sncf", 2026, 1996) == (
        "agent_seul")
    assert profil_de_la_fiche(affiliations, catalogue, "agent_sncf", 2026) == "salarie_prive"
    assert famille_du_statut(affiliations, "independant", "liberal_non_reglemente",
                             2026, 2005) == "liberal"
    assert famille_du_statut(affiliations, "independant", "liberal_non_reglemente",
                             2026) == "commercant"


def test_l_indemnite_journaliere_du_liberal_installe_avant_2019(simulateur):
    """« 0,30 % pour [les travailleurs indépendants] mentionnés à l'article
    L. 640-1 » (D. 621-3, I) : le libéral resté à la CNAVPL ; 0,50 % au
    nouvel entrant, affilié comme un commerçant."""
    def indemnite(entree):
        return {ligne.code: ligne.salarie for ligne in _fiche(
            simulateur, "liberal_non_reglemente", 2026, 60_000.0, entree).lignes
        }.get("indemnites_journalieres", 0.0)
    assert indemnite(2005) == pytest.approx(0.003 * 60_000.0, abs=0.01)
    assert indemnite(None) == pytest.approx(0.005 * 60_000.0, abs=0.01)


#: Le net de l'agent de la SNCF, à la main : le traitement, moins la retenue
#: de 10,85 %, la CSG et la CRDS sur 98,25 %.
NET_SNCF = REVENU * (1.0 - 0.1085 - (0.092 + 0.005) * 0.9825)


def test_le_net_de_l_agent_de_la_sncf_entre_avant_2020(simulateur):
    """Le net de la fiche, et ses deux conversions, celles de la saisie en net."""
    racine, macro = PARAMETRES.racine_donnees, simulateur.macro
    catalogue, affiliations = simulateur.catalogue, simulateur.affiliations
    assert _fiche(simulateur, "agent_sncf", 2026, REVENU, 1996).net == pytest.approx(
        NET_SNCF, abs=0.01)
    assert salaire_net_depuis_brut(racine, macro, catalogue, affiliations, "agent_sncf",
                                   2026, REVENU, annee_entree=1996) == pytest.approx(
        NET_SNCF, abs=0.01)
    assert salaire_brut_depuis_net(racine, macro, catalogue, affiliations, "agent_sncf",
                                   2026, NET_SNCF, annee_entree=1996) == pytest.approx(
        REVENU, abs=0.01)


def test_les_nets_du_cycle_de_vie_gardent_le_regime(simulateur):
    """L'agent de la SNCF entré en 1996 : de 2020 à 2025, sa paie lui laisse
    ce qu'elle lui laissait en 2019, aux mêmes taux — sa retenue, la CSG et la
    CRDS —, et non la paie d'un salarié du privé."""
    carriere = Carriere(
        annee_naissance=1975, sexe="H", age_liquidation=57,
        lignes=[AnneeCarriere(annee=an, affiliation="agent_sncf", trimestres_valides=4,
                              revenu=REVENU) for an in range(1996, 2032)])
    nets = revenus_nets(simulateur, carriere)
    for an in range(2019, 2026):
        assert nets[an] == pytest.approx(NET_SNCF, abs=0.01), an


def test_la_remuneration_de_la_carriere_garde_le_regime(simulateur):
    """De la bascule au départ, la fiche d'un agent de la SNCF entré en 2007 :
    le profil de son régime, et sa retenue, chaque année."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1985, sexe="H", affiliation="agent_sncf",
        age_debut=22, age_liquidation=60, niveau_salaire=1.0)
    remuneration = simulateur.simuler(carriere).remuneration
    assert remuneration.profil == "agent_seul"
    for annee in remuneration.annees:
        assert _regimes(simulateur, annee.droit_en_vigueur) == {"sncf"}, annee.annee


# -- le portage JavaScript ----------------------------------------------------

#: Les cas que le jumeau rejoue : chaque statut fermé, entré avant et sans
#: date, l'année où il garde son régime.
CAS = [(statut, [entree.annee, entree.mois] if isinstance(entree, DateMois)
        else [entree, 1], annee) for statut, entree, _, annee, _, _ in FERMES]

_JUMEAU = """
import { readFileSync } from "node:fs";
import { CatalogueRegimes, Affiliations } from "./moteur/js/regimes.js";
import { DonneesMacro } from "./moteur/js/macro.js";
import { DateMois } from "./moteur/js/calendrier.js";
import { BaremePrelevements, ficheDepuisBrut, familleDuStatut, profilDeLaFiche,
  salaireBrutDepuisNet, salaireNetDepuisBrut } from "./moteur/js/remuneration.js";
const [cas, revenu] = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("./moteur/donnees.json", "utf8"));
const bareme = new BaremePrelevements(paquet.prelevements_remuneration);
const macro = new DonneesMacro(paquet);
const catalogue = new CatalogueRegimes(paquet);
const affiliations = new Affiliations(paquet);
const fiche = (statut, annee, entree) => {
  const f = ficheDepuisBrut(bareme, macro, catalogue, affiliations, statut, annee, revenu,
    0, null, entree);
  return {
    net: f.net,
    lignes: Object.fromEntries(f.lignes.map((l) => [l.code, [l.salarie, l.employeur]])),
  };
};
const sortie = cas.map(([statut, [annee_, mois], annee]) => {
  const entree = new DateMois(annee_, mois);
  const profil = profilDeLaFiche(affiliations, catalogue, statut, annee, entree);
  return {
    garde: fiche(statut, annee, entree),
    nouveau: fiche(statut, annee, null),
    profil,
    famille: familleDuStatut(affiliations, profil, statut, annee, entree),
    net: salaireNetDepuisBrut(bareme, macro, catalogue, affiliations, statut, annee,
      revenu, 0, entree),
    brut: salaireBrutDepuisNet(bareme, macro, catalogue, affiliations, statut, annee,
      revenu * 0.75, 0, entree),
  };
});
process.stdout.write(JSON.stringify(sortie));
"""


def _comme_le_jumeau(fiche) -> dict:
    return {"net": fiche.net,
            "lignes": {ligne.code: [ligne.salarie, ligne.employeur] for ligne in fiche.lignes}}


def test_le_portage_javascript_lit_la_date_d_entree(simulateur):
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _JUMEAU, json.dumps([CAS, REVENU])],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    racine, macro = PARAMETRES.racine_donnees, simulateur.macro
    catalogue, affiliations = simulateur.catalogue, simulateur.affiliations
    for (statut, (annee_entree, mois), annee), obtenu in zip(
            CAS, json.loads(execution.stdout)):
        entree = DateMois(annee_entree, mois)
        profil = profil_de_la_fiche(affiliations, catalogue, statut, annee, entree)
        attendu = {
            "garde": _comme_le_jumeau(_fiche(simulateur, statut, annee, REVENU, entree)),
            "nouveau": _comme_le_jumeau(_fiche(simulateur, statut, annee, REVENU)),
            "profil": profil,
            "famille": famille_du_statut(affiliations, profil, statut, annee, entree),
            "net": salaire_net_depuis_brut(racine, macro, catalogue, affiliations, statut,
                                           annee, REVENU, annee_entree=entree),
            "brut": salaire_brut_depuis_net(racine, macro, catalogue, affiliations, statut,
                                            annee, REVENU * 0.75, annee_entree=entree),
        }
        assert obtenu["profil"] == attendu["profil"], statut
        assert obtenu["famille"] == attendu["famille"], statut
        assert obtenu["net"] == pytest.approx(attendu["net"], abs=1e-6), statut
        assert obtenu["brut"] == pytest.approx(attendu["brut"], abs=1e-6), statut
        for cle in ("garde", "nouveau"):
            assert set(obtenu[cle]["lignes"]) == set(attendu[cle]["lignes"]), (statut, cle)
            for code, (salarie, employeur) in attendu[cle]["lignes"].items():
                assert obtenu[cle]["lignes"][code] == [
                    pytest.approx(salarie, abs=1e-6), pytest.approx(employeur, abs=1e-6)], (
                    statut, cle, code)
            assert obtenu[cle]["net"] == pytest.approx(attendu[cle]["net"], abs=1e-6), (
                statut, cle)
