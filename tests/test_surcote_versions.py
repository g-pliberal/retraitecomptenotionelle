"""La surcote du régime général lue dans les versions de sa fiche.

Note de décision 0009, étape 3, quatrième session. La date d'effet de la
pension choisit la version de D. 351-1-4, la date de chaque trimestre sa
ligne. Les taux attendus viennent du texte, rédaction par rédaction :

- décret n° 2004-156, article 1er : « La majoration prévue à l'article
  L. 351-1-2 est égale à 0,75 % par trimestre » ; la circulaire Cnav 2004/37,
  point 41 : « 5 x 0,75 % = 0,0375 » ;
- décret n° 2006-1611, article 1er : « 1° 0,75 % du premier au quatrième
  trimestre ; 2° 1 % au-delà du quatrième trimestre ; 3° ou, quel que soit
  son rang, 1,25 % pour chaque trimestre accompli après le soixante-cinquième
  anniversaire », et article 3 : « applicables aux pensions prenant effet à
  compter du 1er janvier 2007 » ;
- décret n° 2008-1509, article 5 : « La majoration est égale à 1, 25 % pour
  chaque trimestre accompli à compter du 1er janvier 2009 », en vigueur le
  lendemain de sa publication au Journal officiel du 31 décembre 2008 (son
  article 8 ne diffère que les articles 6 et 7, au 1er avril 2009).
"""

from __future__ import annotations

import csv

import pytest

from facade import Simulateur
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees.chargement import charger_yaml

FICHE = RACINE_DONNEES / "reference" / "regles" / "surcote_regime_general.yaml"
BAREME = RACINE_DONNEES / "reference" / "legislation" / "surcote_baremes.csv"


@pytest.fixture(scope="module")
def baremes():
    return Simulateur().scenario_actuel.surcote_baremes


def test_la_fiche_a_quatre_versions_choisies_a_la_date_d_effet():
    fiche = charger_yaml(FICHE)
    assert fiche["dates_qui_decident"] == ["liquidation.date_effet"]
    bornes = [(v["id"], [None if b is None else str(b) for b in v["bornes"]["liquidation.date_effet"]])
              for v in fiche["versions"]]
    assert bornes == [
        ("sans_surcote", [None, "2004-01-01"]),
        ("loi_de_2003", ["2004-01-01", "2007-01-01"]),
        ("decret_de_2006", ["2007-01-01", "2009-01-01"]),
        ("lfss_2009", ["2009-01-01", None]),
    ]


def test_le_bareme_date_n_a_plus_de_ligne_du_regime_general():
    with BAREME.open(encoding="utf-8") as flux:
        lignes = list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))
    assert [l for l in lignes if l["bareme"] == "regime_general"] == []
    assert {l["bareme"] for l in lignes} == {"fonction_publique", "cnbf", "cnavpl"}


def _trimestres(annee, mois, nombre, apres_65=False):
    date, dates = DateMois(annee, mois), []
    for _ in range(nombre):
        dates.append((date, apres_65))
        date = date.plus_mois(3)
    return dates


@pytest.mark.parametrize("trimestres, effet, attendu", [
    # Circulaire Cnav 2004/37, point 41.
    (_trimestres(2004, 1, 5), DateMois(2005, 7), 1.0375),
    # Né le 15/01/1944, six trimestres en 2004-2005 avant 65 ans.
    (_trimestres(2004, 4, 6), DateMois(2006, 1), 1.045),
    (_trimestres(2004, 4, 6), DateMois(2007, 1), 1.05),
    # Né le 15/01/1940, quatre trimestres après 65 ans.
    (_trimestres(2005, 4, 4, True), DateMois(2006, 7), 1.03),
    (_trimestres(2005, 4, 4, True), DateMois(2007, 1), 1.05),
    # Né le 15/01/1948, quatre trimestres en 2008, quatre en 2009.
    (_trimestres(2008, 1, 8), DateMois(2010, 1), 1.08),
])
def test_chaque_trimestre_au_taux_de_sa_date_dans_la_version_de_la_date_d_effet(
        baremes, trimestres, effet, attendu):
    coefficient, _ = baremes.coefficient("regime_general", trimestres, effet)
    assert coefficient == pytest.approx(attendu)
