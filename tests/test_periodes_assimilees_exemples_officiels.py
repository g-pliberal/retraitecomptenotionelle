"""Le sixième domaine, les périodes assimilées manquantes (action 130),
étape 4 : les exemples que la Cnav publie, rejoués dans les deux moteurs.

- Circulaire Cnav n° 2016-41 du 17 octobre 2016, « Droits à la retraite des
  apprentis à compter du 1er janvier 2014 », annexe, exemples 1 à 4 : les
  trimestres garantis d'un contrat (D. 373-3), puis le complément que
  D. 373-4 ajoute aux trimestres que les salaires valident.
- Circulaire Cnav n° 2024-18 du 11 avril 2024, « Stage de la formation
  professionnelle continue à compter du 1er septembre 2023 », point 3.2.2,
  exemples 1 à 4 : cinquante jours de stage dans l'année civile valent un
  trimestre assimilé, sans report, quatre trimestres au plus par année.

Chaque exemple est recopié de sa source, à ses dates et à ses euros. Les
deux moteurs comptent les mêmes chronologies, par un seul appel à node
(``tests/js/comparer-assimilees.mjs``), et les trimestres qu'ils écrivent
sont confrontés à ceux que la circulaire publie. Fiches :
``apprentissage``, ``stages_formation_professionnelle``.
"""

from __future__ import annotations

import datetime
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle import chronologie
from retraite_notionnelle.carriere import Carriere, LigneRelevee
from retraite_notionnelle.droit import compter, releve
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
SALARIE = "salarie_prive_non_cadre"
REGIME = ("regime_general",)


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _apprenti(debut: str, fin: str, salaires: dict[int, float]) -> dict:
    """Un apprenti né en 1998, payé ``salaires`` les années de son contrat,
    du ``debut`` à la ``fin`` exclue, puis salarié de 2020 à son départ. Le
    relevé porte les euros, sans trimestres : le modèle les valide du
    salaire, comme la caisse (R. 351-9)."""
    lignes = [LigneRelevee(annee=a, affiliation=SALARIE, revenu=r)
              for a, r in sorted(salaires.items())]
    lignes += [LigneRelevee(annee=a, affiliation=SALARIE, revenu=30000.0)
               for a in range(2020, 2062)]
    construite = chronologie.du_releve(annee_naissance=1998, sexe="H",
                                       age_liquidation=64.0, releve=lignes)
    premiere, derniere = min(salaires), max(salaires)
    for fait in construite["faits"]:
        if not fait["id"].startswith("releve_"):
            continue
        annee = int(fait["debut"][:4])
        if annee not in salaires:
            continue
        fait["attributs"]["apprentissage"] = True
        if annee == premiere:
            fait["debut"] = debut
        if annee == derniere:
            fait["fin"] = fin
    return chronologie.completer(construite)


def _stagiaire(stages: list[dict], salaires: dict[int, float] | None = None) -> dict:
    """Un stagiaire né en 1990, que le relevé dit salarié de 2020 à son
    départ, et payé ``salaires`` (l'assiette forfaitaire du stage) avant."""
    lignes = [LigneRelevee(annee=a, affiliation=SALARIE, revenu=r)
              for a, r in sorted((salaires or {}).items())]
    lignes += [LigneRelevee(annee=a, affiliation=SALARIE, revenu=30000.0)
               for a in range(2020, 2054)]
    construite = chronologie.du_releve(annee_naissance=1990, sexe="F",
                                       age_liquidation=64.0, releve=lignes)
    periodes = [{"motif": "stage_de_formation_professionnelle", **stage} for stage in stages]
    return chronologie.completer(chronologie.avec_periodes_assimilees(construite, periodes))


#: Un salaire d'apprenti qui ne valide aucun trimestre : les exemples 1 à 3
#: de la 2016-41 ne disent que la durée du contrat, que le complément donne
#: alors en entier.
PEU = 100.0

#: Chaque exemple : sa chronologie, les trimestres assimilés que la
#: circulaire publie par année, et les trimestres d'assurance de l'année au
#: régime général, après le plafond de quatre, quand elle les publie.
EXEMPLES = {
    # « Contrat d'apprentissage du 1er septembre 2014 au 31 août 2016 » :
    # 1 trimestre en 2014, 4 en 2015, 3 en 2016.
    "cnav_2016_41_exemple_1": (
        _apprenti("2014-09-01", "2016-09-01", {2014: PEU, 2015: PEU, 2016: PEU}),
        {2014: 1, 2015: 4, 2016: 3}, None),
    # « du 15 septembre 2014 au 14 septembre 2016 » : 23 mois civils et
    # 30 jours, 24 mois, les mêmes trimestres.
    "cnav_2016_41_exemple_2": (
        _apprenti("2014-09-15", "2016-09-15", {2014: PEU, 2015: PEU, 2016: PEU}),
        {2014: 1, 2015: 4, 2016: 3}, None),
    # « du 15 novembre 2014 au 14 février 2015 », compté sur trois années et
    # quinze mois : le contrat finit le 14 février 2016, que l'exemple
    # décompte. 0 trimestre en 2014, 4 en 2015, 1 en 2016.
    "cnav_2016_41_exemple_3": (
        _apprenti("2014-11-15", "2016-02-15", {2014: PEU, 2015: PEU, 2016: PEU}),
        {2015: 4, 2016: 1}, None),
    # Du 1er octobre 2014 au 30 septembre 2016, 1 110, 4 950 et 4 860 euros
    # reportés : 0, 3 et 3 trimestres validés par les salaires ; la validation
    # définitive, 1 (0 cotisé et 1 complémentaire), 4 (3 et 1), 3 (3 et 0).
    "cnav_2016_41_exemple_4": (
        _apprenti("2014-10-01", "2016-10-01", {2014: 1110.0, 2015: 4950.0, 2016: 4860.0}),
        {2014: 1, 2015: 1}, {2014: 1, 2015: 4, 2016: 3}),
    # « du 01/01/2015 au 28/03/2015 [...] 88 jours » : un trimestre. Le
    # calendrier en compte 87, 31, 28 et 28 ; la chronologie refuse plus de
    # jours que la période n'en a, et l'exemple se rejoue sur ses dates.
    "cnav_2024_18_exemple_1": (
        _stagiaire([{"debut": "2015-01-01", "fin": "2015-03-29"}]),
        {2015: 1}, {2015: 1}),
    # 46 jours du 1er janvier au 15 février, puis 34 jours du 27 avril au
    # 30 mai 2015 : 80 jours, 1,6, un trimestre.
    "cnav_2024_18_exemple_2": (
        _stagiaire([{"debut": "2015-01-01", "fin": "2015-02-16"},
                    {"debut": "2015-04-27", "fin": "2015-05-31"}]),
        {2015: 1}, {2015: 1}),
    # Du 1er octobre 2014 au 31 mars 2015, l'assiette forfaitaire de 572,40
    # puis de 579,60 euros ne valide rien : en 2014, « dispositif non entré en
    # vigueur », 0 ; en 2015, 90 jours, 1 trimestre.
    "cnav_2024_18_exemple_3": (
        _stagiaire([{"debut": "2014-10-01", "fin": "2015-04-01"}],
                   {2014: 572.40, 2015: 579.60}),
        {2015: 1}, {2014: 0, 2015: 1}),
    # Toute l'année 2015, l'assiette de 3 220 euros : 2 trimestres de salaire ;
    # 365 jours, 7 trimestres « ramenés à 2 » ; 4 validés.
    "cnav_2024_18_exemple_4": (
        _stagiaire([{"debut": "2015-01-01", "fin": "2016-01-01"}], {2015: 3220.0}),
        {2015: 7}, {2015: 4}),
}


def _durees(simulateur: Simulateur, nom: str):
    carriere = Carriere.depuis_chronologie(EXEMPLES[nom][0], simulateur.macro)
    return releve.construire(simulateur.scenario_actuel, carriere).durees


def _assimilees(donnees: dict) -> dict[int, int]:
    """Les trimestres assimilés que les durées écrites portent, par année."""
    return {a["annee"]: a["trimestres"] for a in donnees["assimilees"]}


def test_les_trimestres_garantis_du_contrat_sont_ceux_de_la_circulaire_2016_41():
    """D. 373-3, annexe de la circulaire 2016-41 : les exemples 1 à 3 donnent
    la durée du contrat, année par année ; le quatrième, du 1er octobre 2014
    au 30 septembre 2016, en tient huit aussi, 1, 4 et 3."""
    jour = datetime.date
    assert compter.trimestres_du_contrat(jour(2014, 9, 1), jour(2016, 9, 1)) == {
        2014: 1, 2015: 4, 2016: 3}
    assert compter.trimestres_du_contrat(jour(2014, 9, 15), jour(2016, 9, 15)) == {
        2014: 1, 2015: 4, 2016: 3}
    assert compter.trimestres_du_contrat(jour(2014, 11, 15), jour(2016, 2, 15)) == {
        2015: 4, 2016: 1}
    assert compter.trimestres_du_contrat(jour(2014, 10, 1), jour(2016, 10, 1)) == {
        2014: 1, 2015: 4, 2016: 3}


@pytest.mark.parametrize("nom", list(EXEMPLES))
def test_l_exemple_publie_est_reproduit(simulateur, nom):
    """Les trimestres assimilés de chaque année, et ce que l'année valide en
    tout au régime général après le plafond de quatre, sont ceux de la
    circulaire."""
    _, assimiles, valides = EXEMPLES[nom]
    durees = _durees(simulateur, nom)
    assert _assimilees(durees.donnees()) == assimiles
    for annee, attendu in (valides or {}).items():
        assert durees.cumul_plafonne("assurance", REGIME,
                                     lambda a, annee=annee: a == annee) == attendu, annee


def test_le_complement_de_l_apprenti_n_est_pas_cotise(simulateur):
    """Exemple 4 de la 2016-41 : « 0 cotisé et 1 complémentaire », « 3 cotisés
    et 1 complémentaire », « 3 cotisés et 0 complémentaire »."""
    durees = _durees(simulateur, "cnav_2016_41_exemple_4")
    cotises = {annee: durees.cumul_plafonne("cotises", REGIME,
                                            lambda a, annee=annee: a == annee)
               for annee in (2014, 2015, 2016)}
    assert cotises == {2014: 0, 2015: 3, 2016: 3}


def test_le_portage_rejoue_les_memes_exemples(simulateur):
    """Le portage écrit, pour chaque exemple, les durées du Python, et donc
    les trimestres de la circulaire."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    paquet = json.loads((RACINE / "moteur" / "donnees.json").read_text(encoding="utf-8"))
    if not set(compter.FICHES_DES_ASSIMILEES.values()) <= set(paquet.get("fiches_datees") or {}):
        pytest.skip("le paquet du site ne porte pas encore les fiches : "
                    "python scripts/regenerer.py")
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump([chronologie for chronologie, _, _ in EXEMPLES.values()], fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-assimilees.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    for (nom, (_, assimiles, _)), obtenu in zip(EXEMPLES.items(),
                                                 json.loads(execution.stdout)):
        assert "erreur" not in obtenu, (nom, obtenu)
        assert _assimilees(obtenu) == assimiles, nom
        attendu = json.loads(json.dumps(_durees(simulateur, nom).donnees()))
        assert obtenu == attendu, nom
