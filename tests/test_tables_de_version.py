"""La table d'une version, et les vues qu'on en fabrique : l'âge légal.

Note de décision 0009, étape 2, première session. Les versions de la fiche
``age_legal_par_generation`` sont la source de l'âge légal : chacune désigne
ses lignes dans ``legislation/age_legal_par_version.csv``, que le récupérateur
lit dans LEGI rédaction par rédaction, et la dernière renvoie à sa rédaction
antérieure pour les assurés nés avant le 1er septembre 1961. La table du droit
en vigueur (``age_ouverture_requis.csv``) et les deux copies d'avant réforme
deviennent des vues fabriquées depuis elles, aux mêmes valeurs.

Les âges attendus des versions sont posés ici depuis les textes, lus dans
l'index LEGI le 19 novembre 2026 : D. 161-2-1-9 dans ses trois rédactions
(LEGIARTI000023388636, LEGIARTI000025089933, LEGIARTI000047634502) et
L. 161-17-2 dans celle de la loi n° 2025-1403 (LEGIARTI000053280889). Les
trois vues, elles, se comparent aux fichiers tels qu'ils étaient avant la
fabrication : rien n'y bouge.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees import tables_de_version
from retraite_notionnelle.noyau import carte

LEGISLATION = RACINE_DONNEES / "reference" / "legislation"


def _lignes(nom: str) -> list[tuple[str, str]]:
    with (LEGISLATION / nom).open(encoding="utf-8") as flux:
        return [(l["generation"], l["age"]) for l in csv.DictReader(
            ligne for ligne in flux if not ligne.lstrip().startswith("#"))]


def _ecrire(dossier: Path, lignes: list[tuple]) -> None:
    chemin = dossier / "reference" / "legislation" / "ages.csv"
    chemin.parent.mkdir(parents=True)
    chemin.write_text("entree_en_vigueur,article,generation,generation_fin,age,fiabilite\n"
                      + "".join(",".join(map(str, l)) + ",certifiee\n" for l in lignes),
                      encoding="utf-8")


def _version(identifiant: str, *effets: str, **contenu) -> dict:
    return {"id": identifiant, "contenu": {
        "table": {"fichier": "legislation/ages.csv",
                  "lignes": {"entree_en_vigueur": list(effets)},
                  "cle": "generation", "valeur": "age"}, **contenu}}


@pytest.fixture
def poche(tmp_path):
    """Deux versions de poche : un décret complet, puis une loi qui n'écrit
    que les assurés nés à compter du 1er septembre 1961."""
    _ecrire(tmp_path, [
        ("2023-09-01", "L", 1968, 2100, 64), ("2023-09-01", "D", 1900, 1961.667, 62),
        ("2023-09-01", "D", 1961.667, 1968, 63), ("2023-09-01", "D", 1968, 2100, 64),
        ("2026-09-01", "L", 1961.667, 1965.25, 62.75), ("2026-09-01", "L", 1965.25, 2100, 64),
    ])
    fiche = {"id": "ages", "versions": [
        _version("decret", "2023-09-01"),
        _version("loi", "2026-09-01",
                 redaction_anterieure={"version": "decret", "naissance": [None, "1961-09-01"]})]}
    return fiche, tmp_path


def test_une_version_lit_ses_lignes_et_sa_redaction_anterieure(poche):
    """La loi écrit les nés à compter du 1er septembre 1961 ; avant, la
    rédaction antérieure répond, et seulement avant : ses 63 ans de 1964,
    que la loi dément, ne remontent pas."""
    fiche, racine = poche
    loi = tables_de_version.par_mois(fiche, "loi", racine)
    assert loi[tables_de_version.rang(1961.667) - 1] == 62      # août 1961, au décret
    assert loi[tables_de_version.rang(1961.667)] == 62.75       # septembre 1961, à la loi
    assert loi[tables_de_version.rang(1964)] == 62.75
    assert loi[tables_de_version.rang(1965.25)] == 64
    decret = tables_de_version.par_mois(fiche, "decret", racine)
    assert decret[tables_de_version.rang(1964)] == 63
    # La table court de la première à la dernière génération du modèle.
    assert min(loi) == tables_de_version.rang(1900)
    assert max(loi) == tables_de_version.rang(1976) - 1


def test_deux_textes_d_une_version_qui_se_contredisent_arretent_la_fabrication(poche):
    fiche, racine = poche
    with (racine / "reference" / "legislation" / "ages.csv").open("a", encoding="utf-8") as flux:
        flux.write("2023-09-01,L,1964,1965,62.75,certifiee\n")
    with pytest.raises(ValueError, match="decret.*1964"):
        tables_de_version.par_mois(fiche, "decret", racine)


def test_une_version_n_ecrit_pas_ce_qu_elle_renvoie(poche):
    """Ce que le texte laisse à sa rédaction antérieure, la version ne l'écrit
    pas : les deux ensemble arrêtent la fabrication."""
    fiche, racine = poche
    fiche["versions"][1]["contenu"]["redaction_anterieure"]["naissance"] = [None, "1962-01-01"]
    with pytest.raises(ValueError, match="loi.*1961"):
        tables_de_version.par_mois(fiche, "loi", racine)


def test_une_version_sans_ligne_arrete_la_fabrication(poche):
    fiche, racine = poche
    fiche["versions"][0]["contenu"]["table"]["lignes"]["entree_en_vigueur"] = ["2024-01-01"]
    with pytest.raises(ValueError, match="decret.*aucune ligne"):
        tables_de_version.par_mois(fiche, "decret", racine)


def test_la_vue_par_generation_ouvre_une_ligne_par_an_et_par_coupure(poche):
    fiche, racine = poche
    vue = dict(tables_de_version.vue_par_generation(
        tables_de_version.par_mois(fiche, "loi", racine)))
    assert list(vue)[:2] == ["1900", "1901"] and list(vue)[-1] == "1975"
    assert [c for c in vue if c.startswith("1961")] == ["1961", "1961.667"]
    assert [c for c in vue if c.startswith("1965")] == ["1965", "1965.25"]
    assert (vue["1961"], vue["1961.667"], vue["1965"], vue["1965.25"]) == (62, 62.75, 62.75, 64)


def test_un_renvoi_qui_ne_tient_pas_arrete_la_fabrication_des_vues(poche, monkeypatch):
    """Un renvoi se contrôle à la fabrication (note 0009, second
    rectificatif) : la fiche de l'âge légal qui lirait une fiche que la carte
    n'a pas ne fabrique aucune table, et dit le renvoi qui manque de cible."""
    import yaml
    monkeypatch.setattr(tables_de_version, "VUES_DE_L_AGE_LEGAL",
                        {"age_ouverture_requis.csv": None})
    fiche, racine = poche
    fiche = {**fiche, "id": tables_de_version.FICHE_DE_L_AGE_LEGAL,
             "dates_qui_decident": ["liquidation.date_effet"]}
    fiche["versions"][0]["bornes"] = {"liquidation.date_effet": [None, "2026-09-01"]}
    fiche["versions"][1]["bornes"] = {"liquidation.date_effet": ["2026-09-01", None]}
    regles = racine / "reference" / "regles"
    regles.mkdir()
    chemin = regles / f"{tables_de_version.FICHE_DE_L_AGE_LEGAL}.yaml"
    chemin.write_text(yaml.safe_dump(fiche, allow_unicode=True), encoding="utf-8")
    assert tables_de_version.vues_de_l_age_legal(racine)["age_ouverture_requis.csv"]

    fiche["versions"][1]["contenu"]["renvois"] = [
        {"fiche": "fiche_absente", "valeur": "age", "de": "assure",
         "date": "liquidation.date_effet"}]
    chemin.write_text(yaml.safe_dump(fiche, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="loi.*renvoie à « fiche_absente »"):
        tables_de_version.vues_de_l_age_legal(racine)


# --- L'âge légal du dépôt ---------------------------------------------------

#: Ce que chaque version donne à un assuré, lu dans son texte : (version,
#: naissance en année et mois, âge en années et mois).
AGES_LUS = [
    ("loi_de_2010", (1951, 6), (60, 0)), ("loi_de_2010", (1951, 7), (60, 4)),
    ("loi_de_2010", (1952, 3), (60, 8)), ("loi_de_2010", (1953, 1), (61, 0)),
    ("loi_de_2010", (1954, 12), (61, 4)), ("loi_de_2010", (1955, 5), (61, 8)),
    ("loi_de_2010", (1956, 1), (62, 0)),
    ("loi_de_2011", (1951, 7), (60, 4)), ("loi_de_2011", (1952, 3), (60, 9)),
    ("loi_de_2011", (1953, 1), (61, 2)), ("loi_de_2011", (1954, 12), (61, 7)),
    ("loi_de_2011", (1955, 1), (62, 0)), ("loi_de_2011", (1964, 6), (62, 0)),
    ("loi_de_2023", (1961, 8), (62, 0)), ("loi_de_2023", (1961, 9), (62, 3)),
    ("loi_de_2023", (1962, 6), (62, 6)), ("loi_de_2023", (1963, 6), (62, 9)),
    ("loi_de_2023", (1964, 6), (63, 0)), ("loi_de_2023", (1965, 2), (63, 3)),
    ("loi_de_2023", (1966, 1), (63, 6)), ("loi_de_2023", (1967, 1), (63, 9)),
    ("loi_de_2023", (1968, 1), (64, 0)), ("loi_de_2023", (1953, 1), (61, 2)),
    ("suspension_de_2025", (1961, 8), (62, 0)), ("suspension_de_2025", (1961, 9), (62, 3)),
    ("suspension_de_2025", (1962, 6), (62, 6)), ("suspension_de_2025", (1963, 1), (62, 9)),
    ("suspension_de_2025", (1964, 6), (62, 9)), ("suspension_de_2025", (1965, 3), (62, 9)),
    ("suspension_de_2025", (1965, 4), (63, 0)), ("suspension_de_2025", (1966, 1), (63, 3)),
    ("suspension_de_2025", (1967, 1), (63, 6)), ("suspension_de_2025", (1968, 12), (63, 9)),
    ("suspension_de_2025", (1969, 1), (64, 0)), ("suspension_de_2025", (1951, 6), (60, 0)),
    ("suspension_de_2025", (1953, 1), (61, 2)),
]


@pytest.fixture(scope="module")
def age_legal() -> dict:
    return carte.fiches()[tables_de_version.FICHE_DE_L_AGE_LEGAL]


@pytest.mark.parametrize("version, naissance, age", AGES_LUS)
def test_chaque_version_de_l_age_legal_donne_l_age_de_son_texte(age_legal, version,
                                                               naissance, age):
    table = tables_de_version.par_mois(age_legal, version)
    annee, mois = naissance
    assert table[annee * 12 + mois - 1] == round(age[0] + age[1] / 12, 2)


def test_les_versions_de_l_age_legal_commencent_a_la_date_de_leur_texte(age_legal):
    """Les bornes se lisent dans la disposition d'application : « aux pensions
    prenant effet à compter du » 1er juillet 2011 (loi n° 2010-1330, article
    118, II), du 1er septembre 2023 (loi n° 2023-270, article 10, XXX, B), du
    1er septembre 2026 (loi n° 2025-1403, article 105, VI) ; la rédaction du
    23 décembre 2011 n'en porte pas, et vaut à son entrée en vigueur."""
    debuts = {v["id"]: str(v["bornes"]["liquidation.date_effet"][0])
              for v in age_legal["versions"]}
    assert debuts == {
        "avant_la_codification_de_1985": "None", "soixante_ans": "1985-12-21",
        "loi_de_2010": "2011-07-01", "loi_de_2011": "2011-12-23",
        "loi_de_2023": "2023-09-01", "suspension_de_2025": "2026-09-01"}
    for identifiant in ("avant_la_codification_de_1985", "soixante_ans"):
        version = next(v for v in age_legal["versions"] if v["id"] == identifiant)
        assert version["contenu"]["parametres"] == {"age": 60}


@pytest.mark.parametrize("nom", list(tables_de_version.VUES_DE_L_AGE_LEGAL))
def test_la_table_de_l_age_legal_est_la_vue_de_ses_versions(nom):
    """La table du droit en vigueur est celle de la dernière version. Les deux
    copies d'avant réforme sont parties : un droit contrefactuel garde la
    version d'avant dans une couche (``tests/test_couches_du_droit.py``)."""
    vue = tables_de_version.vues_de_l_age_legal()[nom]
    assert [(cle, f"{age:.2f}") for cle, age in vue] == _lignes(nom)


def test_la_table_du_droit_en_vigueur_garde_ses_soixante_dix_neuf_lignes():
    """Posé à la main sur le fichier d'avant la fabrication : 79 lignes, de la
    génération 1900 à la génération 1975, coupées au 1er juillet 1951, au
    1er septembre 1961 et au 1er avril 1965."""
    vue = tables_de_version.vues_de_l_age_legal()["age_ouverture_requis.csv"]
    assert len(vue) == 79 and vue[0] == ("1900", 60.0) and vue[-1] == ("1975", 64.0)
    assert [cle for cle, _ in vue if "." in cle] == ["1951.5", "1961.667", "1965.25"]


# --- Ce que le paquet du moteur en porte (deuxième session) ------------------


def test_la_version_preparee_porte_ses_propres_lignes_et_son_renvoi(poche):
    """Le moteur lit la version à la date d'effet, et la génération y choisit
    sa ligne : la version préparée porte ses seules lignes, en étendues de
    générations, et ce qu'elle laisse à sa rédaction antérieure reste un
    renvoi, que le moteur suit. La loi de poche n'écrit que les nés à compter
    du 1er septembre 1961."""
    fiche, racine = poche
    decret, loi = (tables_de_version.pour_le_moteur(fiche, v, racine) for v in ("decret", "loi"))
    assert decret == {"table": [[1900.0, 1961.667, 62.0, 3], [1961.667, 1968.0, 63.0, 3],
                                [1968.0, None, 64.0, 3]]}
    assert loi == {"table": [[1961.667, 1965.25, 62.75, 3], [1965.25, None, 64.0, 3]],
                   "redaction_anterieure": {"version": "decret",
                                            "generations": [None, 1961.667]}}


def test_la_version_preparee_refuse_deux_textes_qui_se_contredisent(poche):
    fiche, racine = poche
    with (racine / "reference" / "legislation" / "ages.csv").open("a", encoding="utf-8") as flux:
        flux.write("2023-09-01,L,1964,1965,62.75,certifiee\n")
    with pytest.raises(ValueError, match="decret.*1964"):
        tables_de_version.pour_le_moteur(fiche, "decret", racine)


def test_le_paquet_porte_les_six_versions_de_l_age_legal():
    """Les fiches que le moteur lit comptent celle de l'âge légal
    (``FichesDatees``), ses six versions choisies à la date d'effet. Les âges
    viennent des textes : soixante ans jusqu'au 30 juin 2011 (R. 351-2) ;
    soixante ans et neuf mois pour les nés en 1952 (D. 161-2-1-9, rédaction du
    31 décembre 2011) ; soixante-deux ans et neuf mois pour les nés du
    1er janvier 1963 au 31 mars 1965 (L. 161-17-2, loi n° 2025-1403), qui
    renvoie les nés avant le 1er septembre 1961 à sa rédaction antérieure."""
    from retraite_notionnelle.donnees.tables_du_droit import FichesDatees

    fiche = FichesDatees(RACINE_DONNEES).fiches()[tables_de_version.FICHE_DE_L_AGE_LEGAL]
    versions = {v["id"]: v for v in fiche["versions"]}
    assert list(versions) == ["avant_la_codification_de_1985", "soixante_ans", "loi_de_2010",
                              "loi_de_2011", "loi_de_2023", "suspension_de_2025"]
    assert versions["soixante_ans"]["parametres"] == {"age": 60}
    assert "table" not in versions["soixante_ans"]
    # Lue à la main, non recontrôlée par un récupérateur : `haute` ; la version
    # supposée dit la sienne.
    assert versions["soixante_ans"]["fiabilite"] == 2
    assert versions["avant_la_codification_de_1985"]["fiabilite"] == 1
    assert [1952.0, 1953.0, 60.75, 3] in versions["loi_de_2011"]["table"]
    # Un âge se lit au mois exact : soixante et un ans et deux mois pour 1953,
    # que le fichier écrit 61.17.
    assert [1953.0, 1954.0, 61 + 2 / 12, 3] in versions["loi_de_2011"]["table"]
    assert versions["loi_de_2011"]["table"][-1] == [1955.0, None, 62.0, 3]
    suspension = versions["suspension_de_2025"]
    assert suspension["table"][0][0] == 1961.667
    assert [1963.0, 1965.25, 62.75, 3] in suspension["table"]
    assert suspension["redaction_anterieure"] == {"version": "loi_de_2023",
                                                  "generations": [None, 1961.667]}
