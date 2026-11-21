"""La décote du régime général découpée en versions de sa fiche.

Action 194 : la carte ne prouve qu'une fiche découpée. Le découpage est un
rangement : le moteur lit toujours le coefficient à la génération
(`legislation/coefficient_minoration.csv`), et ces tests disent que chaque
version dit ce que la table donne aux générations qu'elle atteint. Les valeurs
attendues viennent du texte, rédaction par rédaction de R. 351-27 :

- rédactions du 21 décembre 1985 et du 28 août 1993 : « Pour chaque trimestre
  ainsi retenu, le coefficient de minoration à appliquer au " taux plein " est
  2,5 p. 100 » ;
- rédaction du décret n° 2004-144 : « II. - En ce qui concerne les pensions
  prenant effet postérieurement au 31 décembre 2003, le coefficient […] est
  fixé à : 2,5 % pour l'assuré né avant le 1er janvier 1944 ; 2,375 % pour
  l'assuré né en 1944 ; […] 1,375 % pour l'assuré né en 1952 ; 1,25 % pour
  l'assuré né après 1952 » ;
- décret n° 2025-1409, article 2, I, 29°, e : « Le II est abrogé », pour les
  pensions prenant effet à compter du 1er janvier 2026 (son II) ; la caisse
  applique 1,25 % (circulaire Cnav 2026-07, point 4.1.1) ;
- décret n° 2026-699, article 1er, 3° : « 1,25 % », dès le 1er août 2026.
"""

from __future__ import annotations

import csv

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees.chargement import charger_yaml

FICHE = RACINE_DONNEES / "reference" / "regles" / "decote_regime_general.yaml"
TABLE = RACINE_DONNEES / "reference" / "legislation" / "coefficient_minoration.csv"

#: Le II de R. 351-27 (décret n° 2004-144), génération par génération.
II_DE_2004 = {1944: 0.02375, 1945: 0.0225, 1946: 0.02125, 1947: 0.02, 1948: 0.01875,
              1949: 0.0175, 1950: 0.01625, 1951: 0.015, 1952: 0.01375}


def _table() -> dict[int, float]:
    with TABLE.open(encoding="utf-8") as flux:
        lignes = csv.DictReader(l for l in flux if not l.lstrip().startswith("#"))
        return {int(l["generation"]): float(l["coefficient"]) for l in lignes}


def _versions() -> dict[str, dict]:
    return {v["id"]: v for v in charger_yaml(FICHE)["versions"]}


def test_la_fiche_a_cinq_versions_choisies_a_la_date_d_effet():
    fiche = charger_yaml(FICHE)
    assert fiche["dates_qui_decident"] == ["liquidation.date_effet"]
    bornes = [(v["id"], [None if b is None else str(b) for b in v["bornes"]["liquidation.date_effet"]])
              for v in fiche["versions"]]
    assert bornes == [
        ("avant_l_ordonnance_de_1982", [None, "1983-04-01"]),
        ("ordonnance_de_1982", ["1983-04-01", "2004-01-01"]),
        ("loi_de_2003", ["2004-01-01", "2026-01-01"]),
        ("decret_de_2025", ["2026-01-01", "2026-08-01"]),
        ("decret_de_2026", ["2026-08-01", None]),
    ]


def test_avant_2004_la_table_donne_2_5_pour_cent_a_toute_generation_qui_a_pu_partir():
    # Une pension prise de 1983 à 2003 à soixante ans au moins : générations
    # 1918 (soixante-cinq ans en 1983) à 1943.
    table = _table()
    assert _versions()["ordonnance_de_1982"]["contenu"]["parametres"]["coefficient"] == 0.025
    assert {table[g] for g in range(1918, 1944)} == {0.025}


def test_de_2004_a_2025_la_table_est_le_ii_de_2004():
    table = _table()
    version = _versions()["loi_de_2003"]
    assert version["contenu"]["table"]["fichier"] == "legislation/coefficient_minoration.csv"
    for generation in range(1900, 1976):
        attendu = 0.025 if generation < 1944 else II_DE_2004.get(generation, 0.0125)
        assert table[generation] == attendu, generation


def test_depuis_2026_la_table_donne_1_25_pour_cent_a_toute_generation_qu_une_decote_atteint():
    # En 2026, l'âge d'annulation (soixante-sept ans dès la génération 1955)
    # n'est plus devant que les générations nées après 1958.
    table = _table()
    for nom in ("decret_de_2025", "decret_de_2026"):
        assert _versions()[nom]["contenu"]["parametres"]["coefficient"] == 0.0125
    assert {table[g] for g in range(1953, 1976)} == {0.0125}
