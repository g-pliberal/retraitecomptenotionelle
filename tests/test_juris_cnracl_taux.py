"""Le tableau des taux de la CNRACL, opposé aux deux séries du dépôt.

La documentation juridique de la CNRACL — `juris-cnracl.retraites.fr`, que la
Caisse des dépôts tient pour les employeurs territoriaux et hospitaliers —
publie l'historique des taux par période, du 19 septembre 1947 à 2026. La
Caisse GÈRE le régime : c'est le producteur, et c'est à ce titre que
`scripts/fetch/juris_cnracl_taux.py` a relevé au niveau `certifiee` les
quarante années de contribution employeur qu'OpenFisca ne pouvait que
transcrire.

Les quarante-neuf périodes sont transcrites ici, telles que la page les
imprime, pour que la confrontation tienne sans réseau — c'est la règle des
témoins du dépôt. Elles portent sur DEUX séries de nature différente, et c'est
le principal intérêt de la source : la retenue de l'agent, qui est dans la
fiche du régime, et la contribution de l'employeur, qui est dans
`legislation/contribution_employeur_public.csv` parce que les fiches publiques
s'arrêtent à la retenue.

Le 22 septembre 2026, jour de la lecture, les deux séries du dépôt
s'accordaient avec le tableau sur les soixante-dix-neuf années, sans un seul
écart. Ce test est ce qui rend cet accord vérifiable — et ce qui le fera savoir
s'il cesse.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[1]

#: Les quarante-neuf périodes du tableau : date d'effet, retenue de l'agent,
#: contribution de l'employeur, toutes deux en pourcentage. Transcrites le
#: 22 septembre 2026.
PERIODES: tuple[tuple[str, float, float], ...] = (
    ("1947-09-19", 6, 12),      ("1951-01-01", 6, 18),
    ("1954-04-01", 6, 21),      ("1955-04-01", 6, 18),
    ("1961-01-01", 6, 20),      ("1962-01-01", 6, 18),
    ("1964-07-01", 6, 18),      ("1967-05-01", 6, 18),
    ("1970-08-01", 6, 18.2),    ("1972-10-01", 6, 18.2),
    ("1974-01-01", 6, 19.6),    ("1977-01-01", 6, 18),
    ("1980-07-01", 6, 6),       ("1981-01-01", 6, 13),
    ("1982-01-01", 6, 13),      ("1982-04-01", 6, 12.5),
    ("1983-01-25", 6, 10.7),    ("1984-01-01", 7, 10.2),
    ("1986-08-01", 7.7, 10.2),  ("1987-01-01", 7.7, 15.2),
    ("1987-07-01", 7.9, 15.2),  ("1988-01-01", 7.9, 18.2),
    ("1989-01-01", 8.9, 19.7),  ("1991-02-01", 7.85, 21.3),
    ("1995-01-01", 7.85, 25.1), ("1999-01-01", 7.85, 25.1),
    ("2000-01-01", 7.85, 25.6), ("2001-01-01", 7.85, 26.1),
    ("2002-01-01", 7.85, 26.1), ("2003-01-01", 7.85, 26.5),
    ("2004-01-01", 7.85, 26.9), ("2005-01-01", 7.85, 27.3),
    ("2011-01-01", 8.12, 27.3), ("2012-01-01", 8.39, 27.3),
    ("2012-11-01", 8.49, 27.4), ("2013-01-01", 8.76, 28.85),
    ("2014-01-01", 9.14, 30.4), ("2015-01-01", 9.54, 30.5),
    ("2016-01-01", 9.94, 30.6), ("2017-01-01", 10.29, 30.65),
    ("2018-01-01", 10.56, 30.65), ("2019-01-01", 10.83, 30.65),
    ("2020-01-01", 11.1, 30.65), ("2021-01-01", 11.1, 30.65),
    ("2022-01-01", 11.1, 30.65), ("2023-01-01", 11.1, 30.65),
    ("2024-01-01", 11.1, 31.65), ("2025-01-01", 11.1, 34.65),
    ("2026-01-01", 11.1, 37.65),
)

#: Les dix années dont un taux a changé EN COURS DE ROUTE. La convention du
#: dépôt — le taux en vigueur au 1er janvier vaut pour l'année — les rend
#: toutes par leur premier taux, et c'est une approximation qu'on préfère
#: nommer. La plus grosse est 1980 : la contribution tombe de 18 % à 6 % au
#: 1er juillet, de sorte que l'employeur a versé, cette année-là, la moitié de
#: ce que le dépôt lui compte.
ANNEES_A_DEUX_TAUX = (1954, 1955, 1970, 1980, 1982, 1983, 1986, 1987, 1991, 2012)

PREMIERE, DERNIERE = 1948, 2026


def _au_premier_janvier(champ: int) -> dict[int, float]:
    """Le taux en vigueur au 1er janvier de chaque année, en fraction."""
    serie = {}
    for annee in range(PREMIERE, DERNIERE + 1):
        borne = f"{annee}-01-01"
        applicables = [p for p in PERIODES if p[0] <= borne]
        serie[annee] = applicables[-1][champ] / 100.0
    return serie


@pytest.fixture(scope="module")
def retenues_fiche() -> dict[int, float]:
    fiches = yaml.safe_load(
        (RACINE / "data" / "reference" / "regimes" / "fonction_publique.yaml")
        .read_text(encoding="utf-8"))
    fiche = next(r for r in fiches["regimes"] if r["code"] == "cnracl")
    serie = {}
    for periode in fiche["periodes"]:
        fin = periode["fin"] or DERNIERE
        for annee in range(max(periode["debut"], PREMIERE), min(fin, DERNIERE) + 1):
            serie[annee] = periode["taux_cotisation_retraite"]
    return serie


@pytest.fixture(scope="module")
def contributions_depot() -> dict[int, float]:
    chemin = (RACINE / "data" / "reference" / "legislation"
              / "contribution_employeur_public.csv")
    lignes = [l for l in chemin.read_text(encoding="utf-8").splitlines()
              if not l.startswith("#")]
    return {
        int(ligne["annee"]): float(ligne["taux"])
        for ligne in csv.DictReader(lignes)
        if ligne["regime"] == "cnracl" and PREMIERE <= int(ligne["annee"]) <= DERNIERE
    }


def test_le_tableau_couvre_toute_la_vie_de_la_caisse():
    """De la création, le 19 septembre 1947, à l'année en cours."""
    assert len(PERIODES) == 49
    assert PERIODES == tuple(sorted(PERIODES))
    assert PERIODES[0][0] == "1947-09-19"


def test_la_retenue_de_la_fiche_est_celle_du_gestionnaire(retenues_fiche):
    """Ce que l'agent territorial verse, année par année, depuis 1948."""
    attendu = _au_premier_janvier(1)
    ecarts = {a: (retenues_fiche[a], attendu[a]) for a in attendu
              if a in retenues_fiche and abs(retenues_fiche[a] - attendu[a]) > 5e-7}
    assert not ecarts, f"retenue : {ecarts}"


def test_la_contribution_du_depot_est_celle_du_gestionnaire(contributions_depot):
    """Et ce que verse son employeur, qui en est le triple aujourd'hui."""
    attendu = _au_premier_janvier(2)
    ecarts = {a: (contributions_depot[a], attendu[a]) for a in attendu
              if a in contributions_depot
              and abs(contributions_depot[a] - attendu[a]) > 5e-7}
    assert not ecarts, f"contribution : {ecarts}"


def test_toutes_les_annees_sont_couvertes(retenues_fiche, contributions_depot):
    """Une série trouée passerait les deux tests ci-dessus sans rien prouver."""
    annees = set(range(PREMIERE, DERNIERE + 1))
    assert not annees - set(retenues_fiche), "retenue : années manquantes"
    assert not annees - set(contributions_depot), "contribution : années manquantes"


def test_la_serie_employeur_de_la_cnracl_est_entierement_certifiee():
    """Ce que la lecture du 22 septembre 2026 a changé, et qui doit tenir.

    Quarante années venaient d'OpenFisca-France, transcription tierce plafonnée
    au niveau `haute`. Le tableau du gestionnaire les a relevées. Si une seule
    redescend, c'est que la source a cessé d'être lue.
    """
    chemin = (RACINE / "data" / "reference" / "legislation"
              / "contribution_employeur_public.csv")
    lignes = [l for l in chemin.read_text(encoding="utf-8").splitlines()
              if not l.startswith("#")]
    niveaux = {ligne["fiabilite"] for ligne in csv.DictReader(lignes)
               if ligne["regime"] == "cnracl"}
    assert niveaux == {"certifiee"}, niveaux


def _annees_ou_un_taux_bouge() -> set[int]:
    """Les années où un taux CHANGE après le 1er janvier.

    Toute période commencée en cours d'année n'y suffit pas : le tableau se
    découpe aussi sur les deux autres cotisations qu'il porte — l'ATIACL et le
    fonds pour l'emploi hospitalier —, et 1964, 1967 et 1972 ouvrent ainsi une
    période sans que la retenue ni la contribution bougent d'un centième.
    """
    bouge = set()
    for precedente, suivante in zip(PERIODES, PERIODES[1:]):
        annee = int(suivante[0][:4])
        if suivante[0].endswith("-01-01"):
            continue
        if suivante[1:] != precedente[1:]:
            bouge.add(annee)
    # Une période peut aussi commencer un 1er janvier et être suivie, la même
    # année, d'une autre : 1982 et 2012.
    for annee in range(PREMIERE, DERNIERE + 1):
        taux = [p[1:] for p in PERIODES if p[0].startswith(f"{annee}-")]
        if len(taux) > 1 and len(set(taux)) > 1:
            bouge.add(annee)
    return bouge


@pytest.mark.parametrize("annee", ANNEES_A_DEUX_TAUX)
def test_les_annees_a_deux_taux_sont_bien_celles_qu_on_a_nommees(annee):
    """La convention annuelle a un prix, et on sait où il se paie."""
    assert annee in _annees_ou_un_taux_bouge()


def test_aucune_autre_annee_ne_change_de_taux_en_cours_de_route():
    """Le pendant du test ci-dessus : la liste est exhaustive."""
    assert _annees_ou_un_taux_bouge() == set(ANNEES_A_DEUX_TAUX)
