"""Le personnel de direction de la Banque de France, du quatrième au septième
degré, né avant 1956 (action 191 ; deuxième des trois approximations de
`decote_banque_de_france`).

Le statut du personnel lui donne une limite d'âge plus haute que celle des
autres agents (article 241, récrit par l'arrêté n° A-2012-02 du conseil
général du 1er juin 2012, article 1er, 24°, Registre de publication officiel
du 26 juillet 2012) : le tableau a trois colonnes de plus, « Agents des 4e et
5e degrés », « Agents du 6e degré », « Agents du 7e degré ». Le né au premier
semestre 1950 y lit « 62 ans 3 mois », « 63 ans 3 mois », « 65 ans » et « 65
ans » ; celui du premier semestre 1949, « 61 ans 9 mois », « 62 ans 9 mois »,
« 64 ans 9 mois » et « 65 ans » ; toutes les colonnes se rejoignent au premier
semestre 1956, « 65 ans 3 mois ». L'arrêté n° 2018-02 du 12 mars 2018, en
vigueur le 1er janvier 2019, garde le tableau depuis le premier semestre 1950,
sous deux colonnes, « Agents des niveaux 5 et 6 » et « Agents des niveaux 7
et 8 ».

Sa décote ne change pas. L'article 70 du règlement annexé au décret n°
2007-262, dans sa rédaction du 9 mai 2012 (LEGIARTI000025882187), lui donne un
second tableau, « pour les personnels de direction à partir du quatrième
degré nés avant le 1er janvier 1956 » : né au premier semestre 1949, « Lim.
âge - 7 trimestres », « Lim. âge - 15 trimestres », « Lim. âge - 16
trimestres » ; né au premier semestre 1952, huit, onze et onze ; né au second
semestre 1955, sept partout. Sa limite d'âge diminuée de ces trimestres est,
à chaque ligne, l'âge de l'agent de droit commun.

Les valeurs attendues sont lues dans ces deux textes et posées à la main.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.config import RACINE_PROJET
from retraite_notionnelle.web.site import rendre

from facade import Simulateur, limite_age
from outils_pont import saisie_du_portage

REGLES = Path(RACINE_PROJET) / "data" / "reference" / "regles"
DEGRES = ("direction_4_5", "direction_6", "direction_7")


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur, naissance, mois, depart, emploi, debut=22):
    return simulateur.carriere_simple(
        annee_naissance=naissance, mois_naissance=mois, jour_naissance=15, sexe="H",
        affiliation="agent_banque_de_france", age_debut=debut, age_liquidation=depart,
        invalidite={"banque": emploi} if emploi else None)


# -- la limite d'âge ------------------------------------------------------------

@pytest.mark.parametrize("naissance, mois, emploi, limite, version", [
    # « 1er semestre 1950 62 ans 3 mois 63 ans 3 mois 65 ans 65 ans ».
    (1950, 1, "direction_4_5", 63.25, "statut_de_2012"),
    (1950, 1, "direction_6", 65.0, "statut_de_2012"),
    (1950, 1, "direction_7", 65.0, "statut_de_2012"),
    # « 1er semestre 1949 61 ans 9 mois 62 ans 9 mois 64 ans 9 mois 65 ans ».
    (1949, 1, "direction_6", 64.75, "statut_de_2012"),
    (1949, 1, "direction_7", 65.0, "statut_de_2012"),
    # « 2e semestre 1951 63 ans 64 ans 65 ans 65 ans ».
    (1951, 7, "direction_4_5", 64.0, "statut_de_2012"),
    # « 1er semestre 1954 64 ans 3 mois 65 ans 65 ans » : atteints en janvier
    # 2019, sous l'arrêté de 2018, « Agents des niveaux 5 et 6 ».
    (1954, 1, "direction_4_5", 65.0, "statut_de_2019"),
    (1954, 1, "direction_7", 65.0, "statut_de_2019"),
    # « 1er semestre 1956 65 ans 3 mois » dans toutes les colonnes.
    (1956, 1, "direction_6", 65.25, "statut_de_2019"),
])
def test_la_direction_prend_sa_retraite_a_la_limite_de_sa_colonne(
        simulateur, naissance, mois, emploi, limite, version):
    radiation = limite_age.radiation(
        simulateur.scenario_actuel, _carriere(simulateur, naissance, mois, 72, emploi))
    assert (radiation.limite, radiation.version) == (limite, version)


def test_l_agent_du_sixieme_degre_sert_au_dela_de_la_limite_commune(simulateur):
    """Né le 15 janvier 1950, parti à 64 ans et demi : l'agent de droit commun
    avait passé ses 62 ans et 3 mois quand l'article est né, et prend sa
    retraite le 26 juillet 2012 ; celui du sixième degré, dont la limite est
    de 65 ans, sert jusqu'à son départ."""
    moteur = simulateur.scenario_actuel
    assert limite_age.radiation(moteur, _carriere(simulateur, 1950, 1, 64.5, None)) is not None
    assert limite_age.radiation(
        moteur, _carriere(simulateur, 1950, 1, 64.5, "direction_6")) is None


# -- la décote ------------------------------------------------------------------

def _version(fiche: dict, identifiant: str) -> dict:
    return next(v for v in fiche["versions"] if v["id"] == identifiant)


def _ligne(table, jour):
    return [l for l in table if date.fromisoformat(str(l["depuis"])) <= jour][-1]


@pytest.mark.parametrize("statut", ["statut_de_2012", "statut_de_2019"])
def test_le_second_tableau_de_l_article_70_rend_l_age_de_la_colonne_commune(statut):
    """Pour chaque semestre de naissance de 1949 à 1955 et chaque colonne, la
    limite d'âge de la direction diminuée des trimestres du second tableau est
    la limite commune diminuée de ceux du premier."""
    fiche = yaml.safe_load((REGLES / "decote_banque_de_france.yaml").read_text("utf-8"))
    limite = yaml.safe_load((REGLES / "limite_age_banque_de_france.yaml").read_text("utf-8"))
    table = _version(fiche, "tableau_par_periode_de_naissance")["contenu"]["parametres"]["table"]
    du_statut = _version(limite, statut)["contenu"]["parametres"]
    compares = 0
    for annee in range(1949, 1956):
        for mois in (1, 7):
            naissance = date(annee, mois, 1)
            commune = du_statut["ecart_de_reference"] * 12 + _ligne(
                du_statut["marche"], naissance)["mois"]
            ligne = _ligne(table, naissance)
            for degre in DEGRES:
                colonne = _ligne(du_statut["colonnes"][degre], naissance)["age"] * 12
                trimestres = ligne["trimestres_avant_limite_de_la_direction"][degre]
                assert (colonne - 3 * trimestres
                        == commune - 3 * ligne["trimestres_avant_limite"]), (naissance, degre)
                compares += 1
    assert compares == 42


def test_le_second_tableau_est_celui_de_l_article_70():
    """Trois lignes relues au texte : premier semestre 1949, « Lim. âge - 7 »,
    « - 15 », « - 16 » ; premier semestre 1952, huit, onze, onze ; second
    semestre 1955, sept partout. Rien pour les nés depuis 1956."""
    fiche = yaml.safe_load((REGLES / "decote_banque_de_france.yaml").read_text("utf-8"))
    table = _version(fiche, "tableau_par_periode_de_naissance")["contenu"]["parametres"]["table"]

    def lue(jour):
        return _ligne(table, jour).get("trimestres_avant_limite_de_la_direction")

    assert lue(date(1949, 1, 1)) == {"direction_4_5": 7, "direction_6": 15, "direction_7": 16}
    assert lue(date(1952, 1, 1)) == {"direction_4_5": 8, "direction_6": 11, "direction_7": 11}
    assert lue(date(1955, 7, 1)) == {"direction_4_5": 7, "direction_6": 7, "direction_7": 7}
    assert lue(date(1956, 1, 1)) is None


@pytest.mark.parametrize("naissance, mois, depart, trimestres, coefficient", [
    # « 1er semestre 1952 0,500 % » : 62 ans et 3 mois, soit 63 ans et 3 mois
    # moins quatre trimestres, 64 ans et 3 mois moins huit, 65 ans moins onze.
    (1952, 1, 61, 5, 0.005),
    # « 1er semestre 1954 0,750 % » : 62 ans et 9 mois, soit 65 ans moins neuf.
    (1954, 1, 62, 3, 0.0075),
    # « 1er semestre 1958 1,250 % Lim. âge - 5 trimestres » : né depuis 1956,
    # le premier tableau seul, 65 ans.
    (1958, 1, 62, 12, 0.0125),
])
def test_la_decote_de_la_direction_est_celle_de_l_agent_de_droit_commun(
        simulateur, naissance, mois, depart, trimestres, coefficient):
    for emploi in DEGRES:
        carriere = _carriere(simulateur, naissance, mois, depart, emploi, debut=28)
        assert simulateur.scenario_actuel.calculer(carriere).taux_liquidation == pytest.approx(
            0.75 * (1 - trimestres * coefficient)), emploi


# -- la saisie et le formulaire -------------------------------------------------

_AGENT = {"naissance": "1950", "debut": "28", "liquidation": "64",
          "statut": "agent_banque_de_france"}


@pytest.mark.parametrize("emploi", DEGRES)
def test_la_saisie_porte_le_degre_et_le_reecrit(emploi):
    saisie = saisie_du_portage({**_AGENT, "banque": emploi})
    assert saisie.banque == emploi
    assert f"banque={emploi}" in saisie.requete().split("&")
    assert saisie.invalidite_declaree()["banque"] == emploi


def test_le_menu_propose_les_trois_colonnes_de_la_direction():
    corps = rendre("/simuler", _AGENT)[1]
    for emploi in DEGRES:
        assert f'value="{emploi}"' in corps
    assert "Saisie refusée" not in rendre("/simuler", {**_AGENT, "banque": "direction_6"})[1]
