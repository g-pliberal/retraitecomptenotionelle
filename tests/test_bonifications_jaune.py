"""Les chiffres du jaune pensions : certifiés dans un CSV, et cités sans écart.

`bonifications_jaune.csv` est écrit par `scripts/verifier_donnees.py` depuis
les tableaux que `scripts/fetch/sre_jaune_pensions.py` lit dans le PDF. Les
fiches de `avantages_non_contributifs.yaml` y renvoient par leur champ
`denombrement`. Trois choses à tenir : le fichier ne porte que du certifié, le
champ désigne des lignes qui existent, et chaque chiffre qu'une note cite du
jaune est une valeur de ces lignes-là — la prose ne s'écarte pas du document.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
CSV = RACINE / "data" / "reference" / "legislation" / "bonifications_jaune.csv"
AVANTAGES = RACINE / "data" / "reference" / "legislation" / "avantages_non_contributifs.yaml"

sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
from sre_jaune_pensions import chiffres_cites  # noqa: E402


def _lignes() -> list[dict[str, str]]:
    with CSV.open(encoding="utf-8") as flux:
        return list(csv.DictReader(
            ligne for ligne in flux if not ligne.lstrip().startswith("#")))


def _avantages() -> list[dict]:
    return yaml.safe_load(AVANTAGES.read_text(encoding="utf-8"))["avantages"]


def _formes(valeur: str, mesure: str) -> set[str]:
    """Les écritures qu'une note peut donner d'une valeur du fichier :
    « 1 654 863 », « 27,4 », « 98,4 » pour une proportion de 0,984."""
    nombre = float(valeur)
    formes = {f"{nombre:.1f}".replace(".", ",")}
    if nombre == int(nombre):
        formes.add(f"{int(nombre):,}".replace(",", " "))
        formes.add(str(int(nombre)))
    if mesure == "proportion":
        formes.add(f"{nombre * 100:.1f}".replace(".", ","))
    return formes


def test_le_fichier_ne_porte_que_du_certifie_et_des_cles_uniques():
    lignes = _lignes()
    assert lignes, "bonifications_jaune.csv est vide"
    assert {r["fiabilite"] for r in lignes} == {"certifiee"}
    cles = [(r["tableau"], r["ligne"], r["population"], r["mesure"]) for r in lignes]
    assert len(cles) == len(set(cles)), "deux lignes portent la même clé"
    assert {r["tableau"] for r in lignes} == {"A-7", "50", "B-1"}


def test_les_entiers_et_les_decimaux_ont_chacun_leur_format():
    """Un effectif s'écrit sans décimale, une durée avec trois : deux
    certifications sur le même fichier, et aucune n'écrit dans l'autre."""
    for ligne in _lignes():
        entier = ligne["mesure"] in {"effectif", "beneficiaires", "gain_mensuel_eur", "departs"}
        assert ("." not in ligne["valeur"]) == entier, ligne


def test_le_champ_denombrement_designe_des_lignes_qui_existent():
    lignes = _lignes()
    a7 = {r["ligne"] for r in lignes if r["tableau"] == "A-7"}
    t50 = {r["ligne"] for r in lignes if r["tableau"] == "50"}
    vus = 0
    for avantage in _avantages():
        denombrement = avantage.get("denombrement")
        if not denombrement:
            continue
        vus += 1
        assert denombrement["source_id"] == "sre_jaune_pensions", avantage["code"]
        assert denombrement["tableau_a7"] in a7, (avantage["code"], denombrement)
        assert denombrement["tableau_50"] in t50, (avantage["code"], denombrement)
    assert vus >= 5, "les cinq bonifications que le jaune dénombre portent le champ"


def test_chaque_chiffre_cite_du_jaune_est_une_valeur_certifiee_de_ses_lignes():
    """Une note qui cite le jaune ne peut citer que ce que ses lignes portent :
    ses bonifications dans A-7 et 50, plus l'effectif du régime."""
    lignes = _lignes()
    for avantage in _avantages():
        textes = [avantage.get("sans_chiffre") or "", avantage.get("pourquoi_pas_chiffre") or "",
                  (avantage.get("cout") or {}).get("note") or ""]
        if not any("jaune" in t.lower() for t in textes):
            continue
        denombrement = avantage.get("denombrement")
        assert denombrement, f"{avantage['code']} cite le jaune sans champ denombrement"
        admises: set[str] = set()
        for ligne in lignes:
            sienne = (
                (ligne["tableau"] == "A-7" and ligne["ligne"] in (denombrement["tableau_a7"], "ensemble"))
                or (ligne["tableau"] == "50" and ligne["ligne"] == denombrement["tableau_50"])
            )
            if sienne:
                admises |= _formes(ligne["valeur"], ligne["mesure"])
        for texte in textes:
            if "jaune" not in texte.lower():
                continue
            for chiffre in chiffres_cites(texte):
                assert chiffre in admises, (
                    f"{avantage['code']} cite « {chiffre} » du jaune, qui n'est pas une "
                    f"valeur certifiée de ses lignes ({denombrement['tableau_a7']}, "
                    f"{denombrement['tableau_50']})")


def test_les_deux_sources_du_verificateur_se_partagent_les_mesures(monkeypatch):
    """Sur un JSON simulé : les entiers d'un côté, les décimaux de l'autre, et
    les clés (tableau, ligne, population, mesure) ; « n.d. » n'entre pas."""
    chemin = RACINE / "scripts" / "verifier_donnees.py"
    specification = importlib.util.spec_from_file_location("verifier_donnees", chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules["verifier_donnees"] = module
    specification.loader.exec_module(module)

    simule = {"tables": {
        "A-7": {"effectif": {"fpe_civils": 1654863, "fpt": None},
                "bonifications": {"depaysement": {
                    "beneficiaires": {"fpe_civils": 180010, "fpt": 39933},
                    "duree_trimestres": {"fpe_civils": 17.3, "fpt": 18.7}}}},
        "50": {"proportion": {"fpe_civils": {"depaysement": 0.09, "ensemble": 0.569}},
               "gain_mensuel_eur": {"fpe_civils": {"depaysement": 266, "ensemble": None}}},
        "B-1": {"ensemble_des_dparts": {"libelle": "Ensemble des départs",
                                        "valeurs": {"fpe_civils": 46932}}},
    }}
    monkeypatch.setattr(module, "_lire_json", lambda nom, script: simule)
    entiers = module.source_jaune_effectifs()
    decimaux = module.source_jaune_taux()
    assert entiers == {
        ("50", "depaysement", "fpe_civils", "gain_mensuel_eur"): 266.0,
        ("A-7", "depaysement", "fpe_civils", "beneficiaires"): 180010.0,
        ("A-7", "depaysement", "fpt", "beneficiaires"): 39933.0,
        ("A-7", "ensemble", "fpe_civils", "effectif"): 1654863.0,
        ("B-1", "ensemble_des_dparts", "fpe_civils", "departs"): 46932.0,
    }
    assert decimaux == {
        ("50", "depaysement", "fpe_civils", "proportion"): 0.09,
        ("50", "ensemble", "fpe_civils", "proportion"): 0.569,
        ("A-7", "depaysement", "fpe_civils", "duree_trimestres"): 17.3,
        ("A-7", "depaysement", "fpt", "duree_trimestres"): 18.7,
    }
