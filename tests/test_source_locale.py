"""Une source qui refuse la session se déclare, et son document s'apporte.

`data/sources.yaml` porte un champ `blocage` sur chaque jeu qu'une session ne
peut pas atteindre ; `scripts/fetch/source_locale.py` en imprime la liste et
donne aux récupérateurs le moyen de lire un document déposé dans `data/brut/`
au lieu de le télécharger. Ces tests tiennent les deux ensemble : les valeurs
du champ sont celles que le module connaît, et le module lit bien le fichier
avant de sortir.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[1]
FETCH = RACINE / "scripts" / "fetch"

#: Les récupérateurs qui lisent un document servi par un site — PDF, classeur —
#: et doivent donc pouvoir le lire depuis `data/brut/` quand le site refuse.
LECTEURS_DE_DOCUMENTS = (
    "agirc_arrco_valeurs_point.py",
    "erafp_valeurs_point.py",
    "cnav_revalorisation_salaires.py",
    "cnbf_baremes.py",
    "cnavpl_recueils.py",
    "insee_projections_mortalite.py",
)


def _module():
    chemin = FETCH / "source_locale.py"
    specification = importlib.util.spec_from_file_location("source_locale", chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules["source_locale"] = module
    specification.loader.exec_module(module)
    return module


def _jeux() -> dict[str, dict]:
    manifeste = yaml.safe_load((RACINE / "data" / "sources.yaml").read_text(encoding="utf-8"))
    return {
        jeu["id"]: jeu
        for institution in manifeste["institutions"].values()
        for jeu in institution.get("jeux", [])
    }


def test_le_manifeste_n_admet_que_les_blocages_connus():
    """Une valeur inventée ne dirait rien à qui voudrait apporter le fichier."""
    module = _module()
    for ident, jeu in _jeux().items():
        if "blocage" not in jeu:
            continue
        assert jeu["blocage"] in module.BLOCAGES, (
            f"{ident} : blocage « {jeu['blocage']} » inconnu de source_locale.BLOCAGES")
        assert str(jeu.get("note", "")).strip(), (
            f"{ident} : un blocage se justifie dans la note — ce qui a été essayé, "
            "et ce qui a répondu")
        if "fichier_local" in jeu:
            assert "/" not in jeu["fichier_local"], (
                f"{ident} : fichier_local est un nom sous data/brut/, pas un chemin")


def test_fichier_local_ne_se_declare_que_sur_un_jeu_bloque():
    """Un nom de dépôt sans blocage serait une promesse que rien n'honore."""
    for ident, jeu in _jeux().items():
        if "fichier_local" in jeu:
            assert "blocage" in jeu, f"{ident} : fichier_local sans blocage"


def test_les_refus_constates_sont_declares():
    """Ce que `docs/limites.md` et les notes racontent doit être dans le champ.

    budget.gouv.fr répond 403 aux adresses de sortie du proxy ; la Banque de
    France refuse ses PDF aux clients non navigateur ; l'EIC est sous convention.
    """
    jeux = _jeux()
    assert jeux["sre_jaune_pensions"]["blocage"] == "refus"
    assert jeux["db_cas_pensions"]["blocage"] == "refus"
    assert jeux["opef_rapport_annuel"]["blocage"] == "refus"
    assert jeux["legifrance_textes"]["blocage"] == "refus"
    assert jeux["drees_eic"]["blocage"] == "convention"


def test_la_liste_des_sources_bloquees_s_imprime(capsys):
    module = _module()
    assert module.main([]) == 0
    sortie = capsys.readouterr().out
    assert "sre_jaune_pensions  [refus]" in sortie
    assert "drees_eic  [convention]" in sortie
    assert "rien à apporter" in sortie
    for nom in module.BLOCAGES:
        assert nom in sortie


def test_le_nom_du_document_vient_de_l_adresse_quand_elle_en_porte_un():
    module = _module()
    assert module.nom_du_document(
        "https://media.rafp.fr/s3fs-public/2024-02/RAFP-Evolution-valeurs-point.pdf"
    ) == "RAFP-Evolution-valeurs-point.pdf"
    assert module.nom_du_document(
        "https://www.insee.fr/fr/statistiques/fichier/8990899/hyp_mortalite.xlsx"
    ) == "hyp_mortalite.xlsx"
    assert module.nom_du_document("https://site.fr/docs/Bar%C3%A8me%202024.pdf") == "Barème 2024.pdf"
    # Ces adresses servent un fichier sans le nommer : c'est au manifeste ou
    # au récupérateur de le faire.
    assert module.nom_du_document("https://www.budget.gouv.fr/documentation/file-download/31546") is None
    assert module.nom_du_document("https://www.cnavpl.fr/documents/?wpdmdl=263987") is None
    assert module.nom_du_document("https://www.budget.gouv.fr/") is None


def test_lire_ou_telecharger_prefere_le_fichier_puis_data_brut_puis_le_site(tmp_path, monkeypatch):
    module = _module()
    monkeypatch.setattr(module, "BRUT", tmp_path)
    monkeypatch.setattr(module, "RACINE", tmp_path)
    appels: list[str] = []

    def telecharger(url: str) -> bytes:
        appels.append(url)
        return b"du site"

    url = "https://exemple.fr/pub/tableau.pdf"
    # Rien en local : le site.
    assert module.lire_ou_telecharger(url, telecharger) == b"du site"
    assert appels == [url]

    # Le document déposé sous son nom dans data/brut/ : lu, sans requête.
    (tmp_path / "tableau.pdf").write_bytes(b"apporte")
    assert module.lire_ou_telecharger(url, telecharger) == b"apporte"
    assert appels == [url]

    # Un chemin explicite l'emporte sur tout.
    explicite = tmp_path / "ailleurs.pdf"
    explicite.write_bytes(b"explicite")
    assert module.lire_ou_telecharger(url, telecharger, explicite) == b"explicite"
    assert appels == [url]

    # Un chemin explicite qui n'existe pas est une erreur, pas un téléchargement.
    with pytest.raises(OSError):
        module.lire_ou_telecharger(url, telecharger, tmp_path / "absent.pdf")
    assert appels == [url]


def test_une_adresse_sans_nom_telecharge_sauf_nom_local(tmp_path, monkeypatch):
    module = _module()
    monkeypatch.setattr(module, "BRUT", tmp_path)
    monkeypatch.setattr(module, "RACINE", tmp_path)
    appels: list[str] = []

    def telecharger(url: str) -> bytes:
        appels.append(url)
        return b"du site"

    url = "https://www.cnavpl.fr/documents/?wpdmdl=263987"
    (tmp_path / "cnavpl_recueil_2021.pdf").write_bytes(b"recueil")
    # Sans nom local, rien n'est cherché sous data/brut/ : on télécharge.
    assert module.lire_ou_telecharger(url, telecharger) == b"du site"
    # Avec le nom que le récupérateur attend, le dépôt répond.
    assert module.lire_ou_telecharger(url, telecharger, nom_local="cnavpl_recueil_2021.pdf") == b"recueil"
    assert appels == [url]
    with pytest.raises(ValueError):
        module.chemin_local(url, "../ailleurs.pdf")


def test_ou_deposer_suit_le_manifeste():
    module = _module()
    assert module.ou_deposer({"blocage": "convention", "url": "https://x.fr/a.pdf"}) is None
    assert module.ou_deposer({"blocage": "refus", "url": "https://www.budget.gouv.fr/"}) is None
    attendu = module.ou_deposer({"blocage": "refus",
                                 "url": "https://www.budget.gouv.fr/documentation/file-download/31546",
                                 "fichier_local": "Jaune2026_Pensions.pdf"})
    assert attendu == module.BRUT / "Jaune2026_Pensions.pdf"


def test_les_recuperateurs_de_documents_passent_par_le_module():
    """Un récupérateur qui ouvre l'adresse lui-même ne saurait pas lire un fichier apporté."""
    for nom in LECTEURS_DE_DOCUMENTS:
        source = (FETCH / nom).read_text(encoding="utf-8")
        assert "lire_ou_telecharger(" in source, f"{nom} n'appelle pas lire_ou_telecharger"
