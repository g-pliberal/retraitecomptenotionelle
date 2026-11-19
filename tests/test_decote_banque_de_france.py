"""La décote de la Banque de France est celle de son règlement, non celle de
la fonction publique (action 191, relecture des dix renvois sensibles).

Le règlement annexé au décret n° 2007-262 du 27 février 2007 a sa propre
montée en charge, à l'article 70, « par dérogation aux dispositions de
l'article 32 » : aucune décote à l'agent susceptible de liquider sa pension
« jusqu'au 31 décembre 2008 », puis un taux qui monte d'un huitième de point
par an, de 0,125 % en 2009 à 1,25 % en 2018, et un âge d'annulation écrit en
clair, de 61 ans au premier semestre 2009 à 64 ans et 3 trimestres au 30 juin
2022 (rédaction d'origine, LEGIARTI000006778516). Le décret n° 2012-701 du
7 mai 2012 (article 36) récrit le tableau par période de naissance, pour « les
agents nés avant le 1er janvier 1963 », l'âge étant la limite d'âge diminuée
d'un nombre de trimestres (LEGIARTI000025882187). Le dépôt opposait à l'agent
le barème de l'article L. 14 du code des pensions, trois ans en avance sur
celui-ci.

Les valeurs attendues sont lues dans les deux tableaux et posées à la main :
le taux est de 75 %, diminué du coefficient par trimestre qui sépare l'âge de
la liquidation de l'âge d'annulation, la durée manquante étant ici toujours
plus longue (carrière commencée à vingt-huit ans).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.config import RACINE_PROJET

from facade import Simulateur

REGLES = Path(RACINE_PROJET) / "data" / "reference" / "regles"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _taux(simulateur: Simulateur, naissance: int, mois: int, depart: float) -> float:
    carriere = simulateur.carriere_simple(
        annee_naissance=naissance, mois_naissance=mois, sexe="H",
        affiliation="agent_banque_de_france", age_debut=28, age_liquidation=depart)
    return simulateur.scenario_actuel.calculer(carriere).taux_liquidation


@pytest.mark.parametrize("naissance, mois, depart, trimestres, coefficient", [
    # « Jusqu'au 31 décembre 2008. Sans objet » : soixante ans en janvier 2008.
    (1948, 1, 60, 0, 0.0),
    # Et la ligne se lit à la période où l'agent est « susceptible de liquider
    # sa pension (art. 26) », non à son départ : parti en 2010, il n'en a pas.
    (1948, 1, 62, 0, 0.0),
    # « Du 1er janvier 2009 au 30 juin 2009. 0,125 % 61 ans ».
    (1949, 1, 60, 4, 0.00125),
    # Le même, parti à 61 ans en 2010 : l'âge de sa ligne est atteint.
    (1949, 1, 61, 0, 0.0),
    # « Du 1er juillet 2009 au 31 décembre 2009. 0,125 % 61 ans et 1 trimestre ».
    (1949, 7, 60, 5, 0.00125),
    # « Du 1er janvier 2010 au 30 juin 2010. 0,250 % 61 ans et 2 trimestres ».
    (1950, 1, 60, 6, 0.0025),
    # « Du 1er janvier 2011 au 30 juin 2011. 0,375 % 62 ans ».
    (1951, 1, 60, 8, 0.00375),
])
def test_le_tableau_de_2007_se_lit_a_la_periode_ou_le_droit_s_ouvre(
        simulateur, naissance, mois, depart, trimestres, coefficient):
    assert _taux(simulateur, naissance, mois, depart) == pytest.approx(
        0.75 * (1 - trimestres * coefficient))


@pytest.mark.parametrize("naissance, mois, depart, trimestres, coefficient", [
    # « 1er semestre 1952 0,500 % Lim. âge - 4 trimestres » : limite d'âge de
    # 63 ans et 3 mois (statut, article 241), annulation à 62 ans et 3 mois.
    (1952, 1, 61, 5, 0.005),
    # « 1er semestre 1954 0,750 % Lim. âge - 6 trimestres » : 64 ans et 3 mois
    # moins six trimestres, 62 ans et 9 mois.
    (1954, 1, 62, 3, 0.0075),
    # « 1er semestre 1958 1,250 % Lim. âge - 5 trimestres » : 66 ans et 3 mois
    # moins cinq trimestres, 65 ans.
    (1958, 1, 62, 12, 0.0125),
    # « 1er semestre 1962 1,250 % Lim. âge - 1 trimestre » : 66 ans et 9 mois,
    # pour une pension de 2024.
    (1962, 1, 62.5, 17, 0.0125),
    # Né depuis 1963 : l'article 32 seul, 1,25 % jusqu'à la limite d'âge, 67 ans.
    (1964, 1, 63, 16, 0.0125),
])
def test_le_tableau_de_2012_se_lit_a_la_periode_de_naissance(
        simulateur, naissance, mois, depart, trimestres, coefficient):
    assert _taux(simulateur, naissance, mois, depart) == pytest.approx(
        0.75 * (1 - trimestres * coefficient))


def _version(fiche: dict, identifiant: str) -> dict:
    return next(v for v in fiche["versions"] if v["id"] == identifiant)


def test_les_deux_tableaux_disent_le_meme_droit_aux_nes_de_1949_a_1955():
    """Le décret de 2012 récrit le tableau sans changer le droit des agents
    qui avaient soixante ans avant 2016 : pour chaque semestre de naissance de
    1949 à 1955, la limite d'âge du statut diminuée des trimestres du tableau
    de 2012 est l'âge que le tableau de 2007 écrit en clair au semestre des
    soixante ans, et le taux est le même."""
    fiche = yaml.safe_load((REGLES / "decote_banque_de_france.yaml").read_text("utf-8"))
    limite = yaml.safe_load((REGLES / "limite_age_banque_de_france.yaml").read_text("utf-8"))
    de_2007 = _version(fiche, "tableau_par_periode_de_liquidation")["contenu"]["parametres"]
    de_2012 = _version(fiche, "tableau_par_periode_de_naissance")["contenu"]["parametres"]
    statut = _version(limite, "statut_de_2012")["contenu"]["parametres"]

    def ligne(table, jour):
        return [l for l in table if date.fromisoformat(str(l["depuis"])) <= jour][-1]

    compares = 0
    for annee in range(1949, 1956):
        for mois in (1, 7):
            naissance = date(annee, mois, 1)
            limite_en_mois = statut["ecart_de_reference"] * 12 + ligne(
                statut["marche"], naissance)["mois"]
            par_naissance = ligne(de_2012["table"], naissance)
            par_periode = ligne(de_2007["table"], date(annee + 60, mois, 1))
            assert par_naissance["coefficient"] == par_periode["coefficient"]
            assert (limite_en_mois - 3 * par_naissance["trimestres_avant_limite"]
                    == par_periode["age_annulation"] * 12), naissance
            compares += 1
    assert compares == 14
