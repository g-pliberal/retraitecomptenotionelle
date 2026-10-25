"""Le retour à la CRPCEN et aux IEG après le 1er septembre 2023.

Les deux caisses ne servent la pension de vieillesse qu'aux clercs et aux
agents « recrutés avant le 1er septembre 2023 et qui remplissent, à compter de
cette date, les conditions d'affiliation » (loi du 12 juillet 1937, art. 1er,
§ 2, LEGIARTI000048701185 ; loi n° 2004-803, art. 16, I, LEGIARTI000048701181).
La loi n° 2023-1250 (art. 15, V, VI et VIII) en a ôté, le 1er janvier 2024,
le « sans aucune interruption » de la loi n° 2023-270, et dit, pour les
congés, les suspensions et les ruptures d'avant comme d'après, quand
l'affiliation se maintient : dix ans au plus après une suspension ou une
rupture antérieure au 1er septembre 2023, « quelle qu'en soit la cause » ;
après une rupture postérieure, un mois ou un an selon qui l'a voulue, et
jusqu'à la reprise d'une activité affiliée à un autre régime si elle vient
avant ; pendant les congés que les décrets n° 2025-799 (CRPCEN) et n° 2025-761
(IEG) énumèrent. La CNIEG l'illustre : parti le 1er mars 2021, réembauché le
1er février 2026, l'agent « bénéficie d'un maintien d'affiliation au régime
spécial des IEG » (« L'affiliation au régime spécial de retraite des IEG »,
cnieg.fr, lu le 25 octobre 2026).

Le modèle ne connaît la carrière qu'à l'année : une année civile entière sans
emploi sous le statut, après une rupture postérieure à la fermeture, dépasse
l'un et l'autre maintien. Le départ se date de la fin de la dernière année
d'emploi, le retour de janvier de l'année qui le rouvre. La carrière se bâtit
ligne à ligne : la naissance, l'année seule, et le sexe n'y comptent pas.
"""

from __future__ import annotations

import shutil

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.config import PartCotisation
from retraite_notionnelle.droit import coordonner
from retraite_notionnelle.moteur.compte import ConstructeurCompte
from retraite_notionnelle.simulateur import Simulateur
from retraite_notionnelle.web.site import module, site

PARAMETRES = Parametres()
REVENU = 40_000.0
PRIVE = "salarie_prive_non_cadre"
NOUVEAUX = {"regime_general", "agirc_arrco"}

#: Chaque cas : le statut, ses segments (première et dernière année, statut —
#: ``None`` pour celui du cas —, nature de la période), l'année lue après le
#: retour, et les régimes que le texte lui donne cette année-là.
CAS = {
    # La demande : rompu fin 2023, salarié du privé en 2024, revenu en 2025.
    "clerc-prive-en-2024": ("clerc_de_notaire", [
        (2010, 2023, None, "emploi"), (2024, 2024, PRIVE, "emploi"),
        (2025, 2029, None, "emploi")], 2026, NOUVEAUX),
    "ieg-prive-en-2024": ("agent_ieg", [
        (2010, 2023, None, "emploi"), (2024, 2024, PRIVE, "emploi"),
        (2025, 2029, None, "emploi")], 2026, NOUVEAUX),
    # L'exemple de la CNIEG : parti en 2021, revenu en 2026.
    "ieg-parti-en-2021": ("agent_ieg", [
        (2005, 2020, None, "emploi"), (2021, 2025, PRIVE, "emploi"),
        (2026, 2029, None, "emploi")], 2027, {"ieg"}),
    # Dix ans au plus : parti fin 2015, revenu en 2025 ; parti fin 2014, non.
    "clerc-dix-ans": ("clerc_de_notaire", [
        (2000, 2015, None, "emploi"), (2016, 2024, PRIVE, "emploi"),
        (2025, 2029, None, "emploi")], 2026, {"crpcen"}),
    "clerc-onze-ans": ("clerc_de_notaire", [
        (2000, 2014, None, "emploi"), (2015, 2024, PRIVE, "emploi"),
        (2025, 2029, None, "emploi")], 2026, NOUVEAUX),
    # Revenu en 2023, il est recruté avant le 1er septembre : il garde le régime.
    "clerc-revenu-en-2023": ("clerc_de_notaire", [
        (2000, 2009, None, "emploi"), (2010, 2022, PRIVE, "emploi"),
        (2023, 2029, None, "emploi")], 2026, {"crpcen"}),
    # Le congé parental, que les deux listes nomment, maintient l'affiliation ;
    # le chômage suit une rupture, que rien ne maintient au-delà d'un an.
    "ieg-conge-parental": ("agent_ieg", [
        (2010, 2023, None, "emploi"), (2024, 2025, None, "education_enfant"),
        (2026, 2029, None, "emploi")], 2027, {"ieg"}),
    "clerc-chomage-en-2024": ("clerc_de_notaire", [
        (2010, 2023, None, "emploi"), (2024, 2024, None, "chomage_indemnise"),
        (2025, 2029, None, "emploi")], 2026, NOUVEAUX),
    # La suspension commencée avant la fermeture : dix ans comptés de son début.
    "ieg-suspendu-depuis-2011": ("agent_ieg", [
        (2000, 2010, None, "emploi"), (2011, 2024, None, "inactivite"),
        (2025, 2029, None, "emploi")], 2026, NOUVEAUX),
    # La RATP garde « les anciens agents du cadre permanent de la régie
    # recrutés avant le 1er septembre 2023 » (décret n° 2008-637, art. 1er, 1°).
    "ratp-prive-en-2024": ("agent_ratp", [
        (2010, 2023, None, "emploi"), (2024, 2024, PRIVE, "emploi"),
        (2025, 2029, None, "emploi")], 2026, {"ratp"}),
}

#: Les régimes que le statut garde, lus l'année qui précède la fermeture.
GARDES = {"clerc_de_notaire": {"crpcen"}, "agent_ieg": {"ieg"}, "agent_ratp": {"ratp"}}


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(PARAMETRES)


def _lignes(statut: str, segments) -> list[dict]:
    """Une ligne par année : l'emploi au revenu constant, l'interruption sans
    revenu ni cotisation."""
    lignes = []
    for premiere, derniere, autre, nature in segments:
        for annee in range(premiere, derniere + 1):
            emploi = nature == "emploi"
            lignes.append({"annee": annee, "affiliation": autre or statut,
                           "trimestres_valides": 4, "revenu": REVENU if emploi else 0.0,
                           "type_periode": nature, "cotisations_versees": emploi})
    return lignes


def _carriere(statut: str, segments) -> Carriere:
    lignes = _lignes(statut, segments)
    return Carriere(annee_naissance=lignes[0]["annee"] - 22, sexe="H", age_liquidation=95,
                    lignes=[AnneeCarriere(**ligne) for ligne in lignes])


def _routes(simulateur: Simulateur, carriere: Carriere, annee: int) -> tuple[set, set]:
    """Les régimes que le compte reçoit cette année-là, et ceux où le scénario 1
    la range (l'étape « coordonner les affiliations »)."""
    compte = ConstructeurCompte(
        simulateur.macro, simulateur.catalogue, simulateur.affiliations,
        simulateur.indexation, PARAMETRES.avec(part_cotisation=PartCotisation.SALARIALE))
    recus = set(dict(compte.cotisation_annuelle(carriere, annee).par_regime))
    coordination = coordonner.coordonner(simulateur.scenario_actuel, carriere)
    ranges = {code for ligne, regimes in zip(coordination.carriere.lignes,
                                              coordination.regimes)
              if ligne.annee == annee for code in regimes}
    return recus, ranges


@pytest.mark.parametrize("nom", CAS)
def test_le_retour_garde_le_regime_que_le_maintien_couvre(simulateur, nom):
    """Avant la fermeture, chaque carrière cotise au régime spécial ; après le
    retour, au régime que le texte lui donne, dans le compte comme dans le
    scénario 1."""
    statut, segments, annee, attendus = CAS[nom]
    carriere = _carriere(statut, segments)
    assert _routes(simulateur, carriere, segments[0][0]) == (GARDES[statut],) * 2
    assert _routes(simulateur, carriere, annee) == (attendus, attendus)


def test_l_entree_est_celle_du_retour_que_rien_ne_maintient(simulateur):
    """La date d'entrée qui décide du régime : le premier recrutement tant que
    l'affiliation dure, le retour qui la rouvre quand elle s'est rompue."""
    affiliations = simulateur.affiliations
    statut, segments, _, _ = CAS["clerc-prive-en-2024"]
    carriere = _carriere(statut, segments)
    assert affiliations.date_entree(carriere, statut, 2023) == DateMois(2010, 1)
    assert affiliations.date_entree(carriere, statut, 2026) == DateMois(2025, 1)
    statut, segments, _, _ = CAS["ieg-parti-en-2021"]
    carriere = _carriere(statut, segments)
    assert affiliations.date_entree(carriere, statut, 2027) == DateMois(2005, 1)


def test_seules_la_crpcen_et_les_ieg_ne_gardent_que_leurs_anciens_restes_affilies(simulateur):
    """La condition d'affiliation n'est que dans la loi de 1937 et la loi
    n° 2004-803 : elle accompagne la borne du grand-père, et le maintien se
    compte en années. La RATP, la Banque de France et la SNCF ne disent que
    « recrutés avant »."""
    affiliations = simulateur.affiliations
    porteurs = {}
    for statut in affiliations.codes:
        for periode in affiliations.periodes(statut):
            if "maintien" in periode:
                assert periode.get("entres_avant") is not None, statut
                assert isinstance(periode["maintien"], int) and periode["maintien"] > 0, statut
                porteurs[statut] = affiliations.maintien(statut)
    assert porteurs == {"clerc_de_notaire": (DateMois(2023, 9), 10),
                        "agent_ieg": (DateMois(2023, 9), 10)}


@pytest.mark.parametrize("nom", CAS)
def test_le_portage_route_le_retour_comme_le_texte(nom):
    """Le scénario 1 du portage range l'année du retour où le texte la met."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    statut, segments, annee, attendus = CAS[nom]
    portage = module("carriere")
    lignes = _lignes(statut, segments)
    carriere = portage.Carriere({
        "annee_naissance": lignes[0]["annee"] - 22, "sexe": "H", "age_liquidation": 95,
        "jour_naissance": 15, "lignes": [portage.AnneeCarriere(ligne) for ligne in lignes]})
    moteur = site().contexte.simulateur().scenario_actuel
    coordination = module("droit/coordonner").coordonner(moteur, carriere)
    regimes = coordination.regimes
    premiere = lignes[0]["annee"]
    assert set(regimes[0]) == GARDES[statut]
    assert set(regimes[annee - premiere]) == attendus
