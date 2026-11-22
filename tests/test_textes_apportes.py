"""Les textes apportés : ce que le dépôt garde des sources qu'il ne lit que
depuis un poste (``data/reference/textes/apportes/LISEZ-MOI.md``).

Chaque fichier est une transcription : un en-tête YAML qui dit d'où vient le
texte, quand il a été lu, sous quelle condition il se rediffuse, et
l'empreinte du corps ; puis le corps, le texte lui-même. Le dépôt est public :
un texte dont la rediffusion n'est pas ``libre`` n'y entre pas.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import re
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "data" / "reference" / "textes" / "apportes"
REGLES = RACINE / "data" / "reference" / "regles"
CHAMPS = {"texte", "titre", "publication", "source", "adresse", "vues", "articles",
          "versions", "lu_le", "etabli", "confrontee_a_l_image", "sha256", "rediffusion"}
RELEASE = "https://github.com/g-pliberal/retraitecomptenotionelle/releases/download/documents-apportes/"


def _textes() -> list[Path]:
    return sorted(p for p in DOSSIER.glob("*.md") if p.name != "LISEZ-MOI.md")


def _lire(chemin: Path) -> tuple[dict, str]:
    brut = chemin.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)\Z", brut, re.S)
    assert m, f"{chemin.name} : il manque l'en-tête YAML entre deux lignes ---"
    return yaml.safe_load(m.group(1)), m.group(2)


def test_le_dossier_tient_au_moins_un_texte():
    assert _textes(), f"aucun texte apporté dans {DOSSIER}"


@pytest.mark.parametrize("chemin", _textes(), ids=lambda p: p.stem)
def test_un_texte_apporte_dit_sa_source_et_sa_licence(chemin):
    entete, corps = _lire(chemin)
    assert set(entete) >= CHAMPS, f"champs manquants : {sorted(CHAMPS - set(entete))}"
    assert entete["texte"] == chemin.stem, "le nom du fichier est la clé du texte"
    assert entete["adresse"].startswith("https://"), "l'adresse se suit d'un clic"
    assert isinstance(entete["lu_le"], dt.date), "lu_le est une date AAAA-MM-JJ"
    assert entete["vues"] and entete["articles"], "on dit quelles vues et quels articles"
    assert entete["etabli"].strip(), "on dit comment le texte a été établi"
    assert isinstance(entete["confrontee_a_l_image"], bool), (
        "confrontee_a_l_image dit, vrai ou faux, si la transcription a été relue sur l'image")
    r = entete["rediffusion"]
    assert r["statut"] == "libre", "un texte qui ne se rediffuse pas librement reste hors du dépôt"
    for cle in ("texte", "lu_dans", "mention"):
        assert str(r.get(cle) or "").strip(), f"rediffusion.{cle} manque"
    assert isinstance(r.get("lu_le"), dt.date), "rediffusion.lu_le est une date"


@pytest.mark.parametrize("chemin", _textes(), ids=lambda p: p.stem)
def test_chaque_version_citee_existe(chemin):
    entete, _ = _lire(chemin)
    for cle in entete["versions"]:
        fiche, _, version = cle.partition("#")
        chemin_fiche = REGLES / f"{fiche}.yaml"
        assert chemin_fiche.exists(), f"{cle} : pas de fiche {fiche}"
        ids = {v["id"] for v in yaml.safe_load(chemin_fiche.read_text(encoding="utf-8"))["versions"]}
        assert version in ids, f"{cle} : la fiche {fiche} n'a pas de version {version}"


@pytest.mark.parametrize("chemin", _textes(), ids=lambda p: p.stem)
def test_l_empreinte_est_celle_du_corps(chemin):
    entete, corps = _lire(chemin)
    attendu = hashlib.sha256(corps.encode("utf-8")).hexdigest()
    assert entete["sha256"] == attendu, (
        f"{chemin.name} : le corps a changé sans son empreinte ; si la retouche "
        f"est voulue, sha256: {attendu}")


@pytest.mark.parametrize("chemin", _textes(), ids=lambda p: p.stem)
def test_un_fac_simile_est_sur_la_release_avec_son_empreinte(chemin):
    entete, _ = _lire(chemin)
    pdf = entete.get("pdf")
    if pdf is None:
        return
    assert pdf["miroir"].startswith(RELEASE), "le PDF se dépose sur la release, pas dans git"
    assert re.fullmatch(r"[0-9a-f]{64}", pdf["sha256"]), "pdf.sha256 : 64 chiffres hexadécimaux"
    assert str(pdf.get("mention") or "").strip(), (
        "pdf.mention : la Licence Ouverte exige de citer la source et la date du fac-similé")
