"""Le sixième domaine, les périodes assimilées manquantes (action 130),
étape 3 : l'étape « compter les durées » compte les périodes que la
chronologie porte — le complément de l'apprentissage, les jours de stage,
d'inscription des sportifs de haut niveau et de congé supplémentaire de
naissance —, dans les deux moteurs.

Les fiches : ``apprentissage``, ``stages_formation_professionnelle``,
``sportifs_haut_niveau``, ``conge_supplementaire_naissance``
(``data/reference/regles/``).
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
from retraite_notionnelle.carriere import Carriere, LigneRelevee, Metier
from retraite_notionnelle.droit import compter, releve
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
SALARIE = "salarie_prive_non_cadre"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _apprenti(apprentissage: bool = True, niveau: float = 0.05) -> dict:
    """Né en janvier 1998, apprenti à seize ans et demi, à un vingtième du
    salaire moyen, puis salarié à dix-neuf ans ; parti à soixante-quatre."""
    return chronologie.du_parcours(
        annee_naissance=1998, sexe="H", age_liquidation=64.0, metiers=[
            Metier(affiliation=SALARIE, age_debut=16.5, niveau_salaire=niveau,
                   apprentissage=apprentissage),
            Metier(affiliation=SALARIE, age_debut=19.0, niveau_salaire=1.0)])


def _releve(naissance: int, annees: range, revenu: float = 30000.0) -> dict:
    """Un relevé sans trimestres, que le modèle recalcule du revenu."""
    return chronologie.du_releve(
        annee_naissance=naissance, sexe="F", age_liquidation=64.0,
        releve=[LigneRelevee(annee=a, affiliation=SALARIE, revenu=revenu) for a in annees])


def _avec(construite: dict, *periodes: dict) -> dict:
    return chronologie.completer(chronologie.avec_periodes_assimilees(construite, list(periodes)))


#: Les chronologies que les deux moteurs comptent : une par règle, et ce qui
#: l'arrête.
CHRONOLOGIES = {
    "apprenti": chronologie.completer(_apprenti()),
    "apprenti_paye": chronologie.completer(_apprenti(niveau=1.0)),
    "sans_apprentissage": chronologie.completer(_apprenti(apprentissage=False)),
    "tout": _avec(
        _apprenti(),
        {"motif": "stage_de_formation_professionnelle", "debut": "2021-03-01",
         "fin": "2021-09-01", "jours": 120},
        {"motif": "sportif_de_haut_niveau", "debut": "2016", "fin": "2018-07"},
        {"motif": "conge_supplementaire_de_naissance", "debut": "2026-07-14",
         "fin": "2026-09-10"}),
    # Une carrière qui commence à trente ans : les années d'avant sont libres.
    "stages_avant_la_carriere": _avec(
        _releve(1990, range(2020, 2054)),
        {"motif": "stage_de_formation_professionnelle", "debut": "2014-10",
         "fin": "2015-06"},
        {"motif": "stage_de_formation_professionnelle", "debut": "2016-02",
         "fin": "2016-04", "jours": 40},
        {"motif": "stage_de_formation_professionnelle", "debut": "2016-09",
         "fin": "2016-10"}),
    "tuc_apres_septembre_2023": _avec(
        _releve(1966, range(1990, 2030)),
        {"motif": "stage_d_insertion", "dispositif": "tuc", "debut": "1985-02",
         "fin": "1985-11"}),
    "tuc_avant_septembre_2023": _avec(
        _releve(1957, range(1990, 2021)),
        {"motif": "stage_d_insertion", "dispositif": "tuc", "debut": "1985-02",
         "fin": "1985-11"}),
    "formation_de_1985": _avec(
        _releve(1966, range(1990, 2030)),
        {"motif": "stage_de_formation_professionnelle", "debut": "1985-02",
         "fin": "1985-11"}),
    "sportif": _avec(
        _releve(1995, range(2025, 2059), revenu=10000.0),
        {"motif": "sportif_de_haut_niveau", "debut": "2013-06", "fin": "2025-01"}),
    "sportif_aise": _avec(
        _releve(1995, range(2015, 2059), revenu=60000.0),
        {"motif": "sportif_de_haut_niveau", "debut": "2015-06", "fin": "2017-01"}),
}


def _durees(simulateur: Simulateur, nom: str, avantages: bool = True):
    carriere = Carriere.depuis_chronologie(CHRONOLOGIES[nom], simulateur.macro)
    if avantages:
        return releve.construire(simulateur.scenario_actuel, carriere).durees
    from retraite_notionnelle.droit import coordonner

    coordination = coordonner.coordonner(simulateur.scenario_actuel, carriere)
    return compter.compter(simulateur.scenario_actuel, coordination, False)


def _par_annee(durees) -> dict[tuple[str, int], int]:
    return {(a.motif, a.annee): a.trimestres for a in durees.assimilees}


def test_le_contrat_compte_ses_mois_puis_ses_trimestres_civils():
    """D. 373-3 : un mois par mois civil entier, un par trente jours des mois
    incomplets ; un trimestre par trois mois ; chaque trimestre civil entier à
    son année, le reste à l'année où le contrat finit. Du 15 novembre 2014 au
    14 février 2016 : seize et quatorze jours, quatorze mois entiers, quinze
    mois, cinq trimestres — quatre en 2015, un en 2016."""
    jour = datetime.date
    assert compter.trimestres_du_contrat(jour(2014, 11, 15), jour(2016, 2, 15)) == {
        2015: 4, 2016: 1}
    # Deux mois et vingt-neuf jours : deux mois, aucun trimestre.
    assert compter.trimestres_du_contrat(jour(2020, 1, 1), jour(2020, 3, 30)) == {}
    # De septembre à août : un trimestre civil entier en 2019, trois en 2020.
    assert compter.trimestres_du_contrat(jour(2019, 9, 1), jour(2020, 9, 1)) == {
        2019: 1, 2020: 3}


def test_les_jours_declares_se_repartissent_sans_fraction():
    """Cent jours de stage de novembre à février : cinquante et cinquante,
    au prorata des jours de calendrier, et la somme tient."""
    jour = datetime.date
    assert compter.jours_par_annee(jour(2015, 11, 1), jour(2016, 3, 1), 100) == {
        2015: 50, 2016: 50}
    assert compter.jours_par_annee(jour(2015, 11, 1), jour(2016, 3, 1)) == {
        2015: 61, 2016: 60}
    reparti = compter.jours_par_annee(jour(2015, 12, 20), jour(2017, 1, 10), 37)
    assert sum(reparti.values()) == 37


def test_l_apprenti_recoit_la_duree_de_son_contrat(simulateur):
    """Payé un vingtième du salaire moyen, l'apprenti ne valide rien par sa
    rémunération : le complément lui donne la durée de son contrat, de juillet
    2014 à janvier 2017, dix trimestres, à l'assurance du régime général, pas
    aux trimestres cotisés. Payé le salaire moyen, il n'en reçoit aucun."""
    apprenti = _durees(simulateur, "apprenti")
    sans = _durees(simulateur, "sans_apprentissage")
    assert _par_annee(apprenti) == {("apprentissage", 2014): 2, ("apprentissage", 2015): 4,
                                    ("apprentissage", 2016): 4}
    assert {a.regime for a in apprenti.assimilees} == {"regime_general"}
    assert {a.version for a in apprenti.assimilees} == {"duree_du_contrat_depuis_2014"}
    assert apprenti.trimestres == sans.trimestres + 10
    assert (apprenti.trimestres_par_regime["regime_general"]
            == sans.trimestres_par_regime["regime_general"] + 10)
    assert (apprenti.cumul_plafonne("cotises", ("regime_general",))
            == sans.cumul_plafonne("cotises", ("regime_general",)))
    assert _durees(simulateur, "apprenti_paye").assimilees == ()
    # La valorisation des droits acquis ne mesure que du contributif pur.
    assert _durees(simulateur, "apprenti", avantages=False).assimilees == ()


def test_une_annee_pleine_ne_recoit_rien_de_plus(simulateur):
    """Le stage, l'inscription du sportif et le congé de naissance comptent,
    mais l'année que les salaires valident déjà en entier n'en garde rien :
    quatre trimestres au plus par année civile."""
    tout = _durees(simulateur, "tout")
    assert _par_annee(tout) == {
        ("apprentissage", 2014): 2, ("apprentissage", 2015): 4, ("apprentissage", 2016): 4,
        ("stage_de_formation_professionnelle", 2021): 2,
        ("conge_supplementaire_de_naissance", 2026): 1,
        ("sportif_de_haut_niveau", 2018): 1}
    assert tout.trimestres == _durees(simulateur, "apprenti").trimestres


def test_les_stages_comptent_cinquante_jours_par_trimestre(simulateur):
    """Le 8° de L. 351-3 depuis 2015 : le stage commencé en octobre 2014 ne
    compte que ses jours de 2015, cent cinquante et un, trois trimestres ; en
    2016, quarante jours déclarés et trente de calendrier, soixante-dix, un
    seul : les jours s'additionnent dans l'année, sans report. Une carrière
    qui commence en 2020 laisse ces années libres."""
    stages = _durees(simulateur, "stages_avant_la_carriere")
    assert _par_annee(stages) == {("stage_de_formation_professionnelle", 2015): 3,
                                  ("stage_de_formation_professionnelle", 2016): 1}
    sans = Carriere.depuis_chronologie(chronologie.completer(_releve(1990, range(2020, 2054))),
                                       simulateur.macro)
    assert stages.trimestres == sans.trimestres_actuels + 4


def test_les_tuc_ne_comptent_que_pour_les_pensions_de_septembre_2023(simulateur):
    """Le 9° de L. 351-3, pour les pensions qui prennent effet depuis le
    1er septembre 2023 : neuf mois de TUC en 1985, deux cent soixante-treize
    jours, cinq trimestres, quatre dans l'année. Partie en 2021, la même
    assurée n'en reçoit aucun ; un stage de formation de 1985 n'est pas un
    stage d'insertion, et n'en reçoit pas davantage."""
    apres = _durees(simulateur, "tuc_apres_septembre_2023")
    assert _par_annee(apres) == {("stage_d_insertion", 1985): 5}
    assert apres.assimilees[0].version == "tuc_et_stages_d_insertion"
    assert apres.trimestres_par_regime["regime_general"] == 4 * 40 + 4
    assert _durees(simulateur, "tuc_avant_septembre_2023").assimilees == ()
    assert _durees(simulateur, "formation_de_1985").assimilees == ()


def test_le_sportif_compte_ses_periodes_de_quatre_vingt_dix_jours(simulateur):
    """Inscrit de juin 2013 à décembre 2024, le sportif né en janvier 1995 ne
    compte qu'à partir de ses vingt ans, par tranches continues de
    quatre-vingt-dix jours, jusqu'à trente-deux trimestres pour une pension
    d'après septembre 2023 ; aisé, il n'en compte aucun."""
    sportif = _durees(simulateur, "sportif")
    annees = [a.annee for a in sportif.assimilees]
    assert min(annees) == 2015
    assert sum(a.trimestres for a in sportif.assimilees) == 32
    assert {a.version for a in sportif.assimilees} == {"trente_deux_trimestres"}
    assert _durees(simulateur, "sportif_aise").assimilees == ()


def test_les_durees_suivent_leur_schema(simulateur):
    """Ce que l'étape écrit, périodes assimilées comprises, suit son schéma."""
    from retraite_notionnelle.noyau import contrats

    schema = contrats.Validateur("compter_les_durees", contrats.ETAPES)
    for nom in CHRONOLOGIES:
        constats = schema.valider(_durees(simulateur, nom).donnees(), "durees")
        assert [str(c) for c in constats if c.genre == "erreur"] == [], nom


def test_le_portage_compte_les_memes_periodes(simulateur):
    """Les deux moteurs écrivent les mêmes durées pour chaque chronologie."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    # Le paquet est un fichier fabriqué, que GitHub refait après l'envoi : entre
    # l'envoi des fiches et sa fabrication, il ne les porte pas encore.
    paquet = json.loads((RACINE / "moteur" / "donnees.json").read_text(encoding="utf-8"))
    if not set(compter.FICHES_DES_ASSIMILEES.values()) <= set(paquet.get("fiches_datees") or {}):
        pytest.skip("le paquet du site ne porte pas encore les fiches : "
                    "python scripts/regenerer.py")
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(list(CHRONOLOGIES.values()), fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-assimilees.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    obtenus = json.loads(execution.stdout)
    for nom, obtenu in zip(CHRONOLOGIES, obtenus):
        attendu = json.loads(json.dumps(_durees(simulateur, nom).donnees()))
        assert obtenu == attendu, nom
