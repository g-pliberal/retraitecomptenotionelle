"""La carrière longue lue dans les versions de sa fiche (note de décision 0009,
étape 3, troisième session).

Les versions de `carriere_longue` sont la source : chacune désigne ses portes
dans `legislation/carriere_longue_par_version.csv`, que le récupérateur lit
dans l'index LEGI, rédaction par rédaction, à la date d'effet que sa
disposition d'application écrit, au jour. Ce que D. 351-1-1 écrit par renvoi,
depuis 2023 — « l'âge prévu à l'article L. 161-17-2 minoré de deux ans et six
mois » —, n'est pas une ligne du fichier : la version porte le renvoi, et le
moteur lit l'âge légal de la génération dans la version de la même date.
`carriere_longue.csv`, indexée par une année décimale, n'est plus qu'une vue
fabriquée des versions, que la certification relit contre les textes.
"""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees import droits_contrefactuels, tables_de_version
from retraite_notionnelle.donnees.chargement import charger_yaml
from retraite_notionnelle.donnees.tables_du_droit import FichesDatees

REGLES = RACINE_DONNEES / "reference" / "regles"
LEGISLATION = RACINE_DONNEES / "reference" / "legislation"
COUCHES = RACINE_DONNEES / "reference" / "couches"
FICHE = "carriere_longue"
EFFET = "liquidation.date_effet"


def _fiche() -> dict:
    return charger_yaml(REGLES / f"{FICHE}.yaml")


def _csv(nom: str) -> list[dict]:
    with (LEGISLATION / nom).open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


def test_six_versions_bornees_au_jour_que_les_textes_disent():
    """2004 : décret n° 2003-1036, article 7, « postérieurement au 31 décembre
    2003 » ; 1er juillet 2011 : décret n° 2010-1734, article 11 ; 1er novembre
    2012 : décret n° 2012-847, article 14 ; 1er septembre 2023 : décret
    n° 2023-436, article 9 ; 1er septembre 2026 : décret n° 2026-345, article
    4. Celle du 1er janvier 2026 (décret n° 2025-1410) ne change aucune
    valeur : elle n'ouvre pas de version."""
    fiche = _fiche()
    assert fiche["dates_qui_decident"] == [EFFET]
    versions = [(v["id"], [None if b is None else str(b) for b in v["bornes"][EFFET]])
                for v in fiche["versions"]]
    assert versions == [
        ("avant_la_loi_de_2003", [None, "2004-01-01"]),
        ("loi_de_2003", ["2004-01-01", "2011-07-01"]),
        ("loi_de_2010", ["2011-07-01", "2012-11-01"]),
        ("decret_de_2012", ["2012-11-01", "2023-09-01"]),
        ("decret_de_2023", ["2023-09-01", "2026-09-01"]),
        ("decret_de_2026", ["2026-09-01", None]),
    ]
    assert "LEGIARTI000053356023" in {t["id"] for t in fiche["textes_sans_effet"]}


def test_chaque_version_designe_ses_portes_par_sa_date_au_jour():
    lignes = _csv("carriere_longue_par_version.csv")
    dates = sorted({l["entree_en_vigueur"] for l in lignes})
    assert dates == ["2004-01-01", "2011-07-01", "2012-11-01", "2023-09-01", "2026-09-01"]
    for version in _fiche()["versions"][1:]:
        table = version["contenu"]["table"]
        assert table["fichier"] == "legislation/carriere_longue_par_version.csv"
        assert table["lignes"] == {"entree_en_vigueur": [str(version["bornes"][EFFET][0])]}


def test_le_fichier_n_ecrit_pas_ce_que_le_texte_renvoie_a_l_age_legal():
    """La porte des vingt ans des nés de septembre 1963 à 1968 (2023), de
    septembre à décembre 1963 et de 1966 à 1969 (2026) n'a pas de ligne : son
    âge se lit par le renvoi."""
    par_date: dict[str, list[tuple[str, str]]] = {}
    for ligne in _csv("carriere_longue_par_version.csv"):
        if ligne["age_debut_maximum"] == "20" and ligne["generation"] != "1900":
            par_date.setdefault(ligne["entree_en_vigueur"], []).append(
                (ligne["generation"], ligne["age_depart"]))
    assert par_date["2023-09-01"] == [("1961.667", "60.00"), ("1969", "61.75"),
                                      ("1970", "62.00")]
    assert par_date["2026-09-01"] == [
        ("1961.667", "60.00"), ("1964", "60.50"), ("1965", "60.75"), ("1965.917", "60.67"),
        ("1970", "61.75"), ("1971", "62.00")]


def test_les_renvois_nomment_l_age_legal_de_la_generation():
    renvois = {v["id"]: v["contenu"].get("renvois") or [] for v in _fiche()["versions"]}
    attendu = {"fiche": "age_legal_par_generation", "valeur": "age", "de": "assure",
               "date": EFFET, "retranche": {"ans": 2, "mois": 6},
               "ligne": {"age_debut_maximum": 20}}
    assert [({k: r[k] for k in attendu}, [str(b) for b in r["naissance"]])
            for r in renvois["decret_de_2023"]] == [(attendu, ["1963-09-01", "1969-01-01"])]
    assert [({k: r[k] for k in attendu}, [str(b) for b in r["naissance"]])
            for r in renvois["decret_de_2026"]] == [
        (attendu, ["1963-09-01", "1964-01-01"]), (attendu, ["1966-01-01", "1970-01-01"])]
    for identifiant in ("avant_la_loi_de_2003", "loi_de_2003", "loi_de_2010", "decret_de_2012"):
        assert renvois[identifiant] == []


def test_la_table_par_date_decimale_est_la_vue_des_versions():
    """`carriere_longue.csv` se fabrique depuis les versions, chaque renvoi
    résolu contre l'âge légal de la même date : ligne pour ligne ce que le
    récupérateur résolvait déjà."""
    vue = tables_de_version.vue_de_la_carriere_longue()
    colonnes = ("date_effet", "generation", "generation_fin", "age_debut_maximum",
                "trimestres_debut", "age_depart", "trimestres_supplementaires",
                "trimestres_assurance_supplementaires", "fiabilite")
    assert vue == [tuple(l[c] for c in colonnes) for l in _csv("carriere_longue.csv")]


def test_le_paquet_porte_la_fiche_avec_ses_portes_et_ses_renvois():
    fiche = FichesDatees(RACINE_DONNEES).fiches()[FICHE]
    versions = {v["id"]: v for v in fiche["versions"]}
    assert len(versions["loi_de_2003"]["portes"]) == 3
    assert [p[:7] for p in versions["loi_de_2003"]["portes"]] == [
        [1900.0, None, 16, 5, 58.0, 4, 8], [1900.0, None, 16, 5, 56.0, 8, 8],
        [1900.0, None, 17, 5, 59.0, 0, 8]]
    (renvoi,) = versions["decret_de_2023"]["renvois"]
    assert renvoi["generations"] == [1963.667, 1969.0]
    assert renvoi["mois"] == -30 and renvoi["ligne"] == {"age_debut_maximum": 20}


@pytest.mark.parametrize("couche, gardee", [
    ("sans_la_reforme_de_2023", "decret_de_2012"),
    ("sans_la_suspension_de_2026", "decret_de_2023"),
])
def test_les_couches_remplacent_la_fiche(couche, gardee):
    operations = {o["vise"]: o["operation"]
                  for o in charger_yaml(COUCHES / f"{couche}.yaml")["operations"]}
    assert operations[FICHE] == "remplacer_une_version"
    droit = {"sans_la_reforme_de_2023": "au_31_aout_2023",
             "sans_la_suspension_de_2026": "loi_2023_sans_suspension"}[couche]
    resolue = droits_contrefactuels.pour_le_paquet(
        FichesDatees(RACINE_DONNEES).fiches())[droit]["fiches"][FICHE]
    derniere = resolue["versions"][-1]
    assert derniere["id"] == gardee and derniere["bornes"][EFFET][1] is None


def _recuperateur():
    chemin = Path(__file__).resolve().parents[1] / "scripts" / "fetch" \
        / "dila_legi_parametres_retraite.py"
    spec = importlib.util.spec_from_file_location("dila_legi_parametres_retraite", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: Le II de D. 351-1-1, rédaction du 1er septembre 2023 (LEGIARTI000047634571).
II_DE_2023 = (
    "Conformément à l'article 9 du décret n° 2023-436 du 3 juin 2023, ces dispositions "
    "s'appliquent aux pensions prenant effet à compter du 1er septembre 2023. I.-Pour les "
    "assurés qui justifient d'une durée d'assurance cotisée, entendue comme la durée "
    "d'assurance accomplie dans le régime général et, le cas échéant, dans un ou plusieurs "
    "autres régimes obligatoires ayant donné lieu à cotisations à leur charge au moins égale "
    "à celle prévue au deuxième alinéa de l'article L. 351-1, l'âge prévu au premier alinéa "
    "de l'article L. 351-1 est abaissé, en application de l'article L. 351-1-1 : 1° A "
    "cinquante-huit ans pour les assurés qui ont débuté leur activité avant l'âge de seize "
    "ans ; 2° A soixante ans pour les assurés qui ont débuté leur activité avant l'âge de "
    "dix-huit ans ; 3° A soixante-deux pour les assurés qui ont débuté leur activité avant "
    "l'âge de vingt ans ; 4° A soixante-trois ans pour les assurés qui ont débuté leur "
    "activité avant l'âge de vingt-et-un ans. II.-Les dispositions du 3° du I s'appliquent "
    "aux assurés nés entre le 1er septembre 1961 et le 31 décembre 1969 sous réserve des "
    "adaptations suivantes : 1° Pour les assurés nés entre le 1er septembre 1961 et 31 août "
    "1963 inclus, le nombre : “ soixante-deux ” est remplacé par le nombre : “ soixante ” ; "
    "2° Pour les assurés nés entre le 1er septembre 1963 et le 31 décembre 1968 inclus, les "
    "mots : “ soixante-deux ans ” sont remplacés par les mots : “ l'âge prévu à l'article L. "
    "161-17-2 minoré de deux ans et six mois ” ; 3° Pour les assurés nés en 1969, les mots : "
    "“ soixante-deux ans ” sont remplacés par les mots : “ soixante-et-un ans et neuf mois ”.")


def test_le_recuperateur_garde_le_renvoi_au_lieu_de_le_resoudre():
    lignes, renvois = _recuperateur().carriere_longue_par_version(
        [("2023-09-01", II_DE_2023)])
    vingt = [(l["generation"], l["generation_fin"], l["age_depart"])
             for l in lignes if l["age_debut_maximum"] == 20]
    assert vingt == [(1900, 2100, 62.0), (1961.667, 1963.667, 60.0), (1969, 1970, 61.75),
                     (1970, 2100, 62.0)]
    assert renvois == [{"entree_en_vigueur": "2023-09-01", "age_debut_maximum": 20,
                        "generation": 1963.667, "generation_fin": 1969,
                        "retranche": {"ans": 2, "mois": 6}}]


def test_la_sauvegarde_de_2023_nomme_la_redaction_qu_elle_garde():
    """Décret n° 2023-436, article 8 : D. 351-1-1 « dans [sa] rédaction
    antérieure à l'entrée en vigueur du présent décret ». La clause nomme la
    version de la carrière longue qu'elle garde par son identifiant, et la
    durée s'acquiert avant le jour où cette version cesse de valoir."""
    sauvegarde = charger_yaml(REGLES / "carriere_longue_sauvegarde_de_2023.yaml")
    version = next(v for v in sauvegarde["versions"] if v["id"] == "decret_du_3_juin_2023")
    parametres = version["contenu"]["parametres"]
    assert parametres["redactions_anterieures"] == {FICHE: "decret_de_2012"}
    gardee = next(v for v in _fiche()["versions"] if v["id"] == "decret_de_2012")
    annee, mois = parametres["duree_acquise_avant"]
    assert str(gardee["bornes"][EFFET][1]) == f"{annee:04d}-{mois:02d}-01"
