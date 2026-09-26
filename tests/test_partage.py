"""Le partage des versions d'une fiche, à chaque date d'observation.

``docs/architecture.md``, § 4.1 et § 6.7 : les versions d'une fiche forment un
partage de ses dates qui décident, aux « sans droit » et exceptions déclarés
près, et chaque borne produit deux cas de bascule. Le contrôle vient de l'outil
laissé par la note 0001 pour la phase 2 ; ce test le rejoue sur les deux fiches
de l'annexe A, puis lui fait trouver ce qu'il doit trouver.
"""

from __future__ import annotations

import copy
import re
from datetime import date
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.noyau import carte, partage

RACINE = Path(__file__).resolve().parents[1]


def _fiches_de_l_annexe_a() -> dict[str, dict]:
    texte = (RACINE / "docs" / "architecture.md").read_text(encoding="utf-8")
    debut = texte.index("## Annexe A")
    fin = texte.index("## Annexe B", debut)
    blocs = re.findall(r"^```yaml\n(.*?)^```", texte[debut:fin], re.M | re.S)
    return {fiche["id"]: fiche for fiche in map(yaml.safe_load, blocs)}


@pytest.fixture
def fonction_publique() -> dict:
    return copy.deepcopy(_fiches_de_l_annexe_a()["enfants_fonction_publique"])


@pytest.mark.parametrize("nom", ["enfants_fonction_publique", "mda_regime_general"])
def test_les_fiches_de_l_annexe_a_forment_un_partage(nom):
    """À chaque date où une version devient connue, et une fois toutes
    connues : ni trou, ni chevauchement."""
    fiche = _fiches_de_l_annexe_a()[nom]
    assert partage.controler(fiche) == []
    observations = partage.observations(fiche)
    assert len(observations) >= 2 and observations[-1] == partage.HAUT
    for observation in observations:
        verdict = partage.verifier(fiche, observation)
        assert verdict.situations > 0 and verdict.versions > 0, observation


def test_chaque_borne_donne_deux_cas_de_bascule(fonction_publique):
    """La veille et le jour de chaque borne : c'est là qu'une erreur de date
    se voit (§ 6.7)."""
    bascules = partage.bascules(fonction_publique)
    bornes = {(nom, date.fromisoformat(str(x)))
              for v in fonction_publique["versions"]
              for nom, intervalle in v["bornes"].items() for x in intervalle if x is not None}
    assert {(nom, jour) for nom, _, jour in bascules} == bornes
    assert all((jour - veille).days == 1 for _, veille, jour in bascules)
    assert ("enfant.naissance", date(2003, 12, 31), date(2004, 1, 1)) in bascules


def test_un_trou_se_voit(fonction_publique):
    """Retirer une version laisse des situations sans règle."""
    versions = fonction_publique["versions"]
    retiree = next(v for v in versions if v["bornes"].get("enfant.naissance"))
    versions.remove(retiree)
    erreurs = partage.controler(fonction_publique)
    assert erreurs and all("aucune version" in e for e in erreurs), erreurs


def test_un_chevauchement_se_voit_et_une_exception_le_leve(fonction_publique):
    """Deux versions qui valent ensemble se chevauchent, sauf quand l'une se
    déclare l'exception de l'autre."""
    versions = fonction_publique["versions"]
    doublon = copy.deepcopy(versions[-1])
    doublon["id"] = "doublon"
    versions.append(doublon)
    erreurs = partage.controler(fonction_publique)
    assert any("se chevauchent" in e and "doublon" in e for e in erreurs), erreurs
    doublon["exception_de"] = versions[-2]["id"]
    assert partage.controler(fonction_publique) == []


def test_une_combinaison_impossible_ne_demande_pas_de_version():
    """Un enfant né après la date d'effet de la pension n'a pas à trouver de
    version : le vocabulaire des dates déclare la combinaison impossible."""
    fiche = {
        "id": "exemple", "dates_qui_decident": ["liquidation.date_effet", "enfant.naissance"],
        "versions": [{"id": "seule", "bornes": {"liquidation.date_effet": [None, None],
                                                "enfant.naissance": [None, "2004-01-01"]}},
                     {"id": "apres", "bornes": {"liquidation.date_effet": ["2004-01-01", None],
                                                "enfant.naissance": ["2004-01-01", None]}}],
    }
    assert partage.controler(fiche) == []
    sans_vocabulaire = partage.verifier(fiche, partage.HAUT, combinaisons=[])
    assert sans_vocabulaire.trous, "sans la combinaison impossible, il y aurait des trous"


def test_une_borne_ne_vaut_qu_une_fois_connue_sa_suivante():
    """Avant la publication du texte qui la ferme, une version vaut sans fin :
    le partage tient à chaque date d'observation."""
    fiche = {
        "id": "exemple", "dates_qui_decident": ["liquidation.date_effet"],
        "versions": [{"id": "ancienne", "bornes": {"liquidation.date_effet": [None, "2020-01-01"]}},
                     {"id": "nouvelle", "textes": [{"id": "JORFTEXT000000000001",
                                                    "publie_le": "2019-06-01"}],
                      "bornes": {"liquidation.date_effet": ["2020-01-01", None]}}],
    }
    assert partage.observations(fiche) == [date(2019, 6, 1), partage.HAUT]
    avant = partage.verifier(fiche, date(2019, 5, 31))
    assert avant.versions == 1 and not avant.trous
    assert partage.controler(fiche) == []


def test_les_renvois_d_une_version_existent(fonction_publique):
    version = fonction_publique["versions"][0]
    version["fermee_par"] = {"liquidation.date_effet": "fantome"}
    version["exception_de"] = "chimere"
    erreurs = partage.controler(fonction_publique)
    assert any("« fantome »" in e for e in erreurs), erreurs
    assert any("« chimere »" in e for e in erreurs), erreurs


def test_la_carte_refuse_un_partage_qui_ne_tient_pas(tmp_path, fonction_publique):
    """Le contrôle de la carte joue le partage de chaque fiche que son contrat
    accepte."""
    fonction_publique["versions"].pop()
    (tmp_path / f"{fonction_publique['id']}.yaml").write_text(
        yaml.safe_dump(fonction_publique, allow_unicode=True, sort_keys=False), encoding="utf-8")
    erreurs = carte.controler(tmp_path)
    assert erreurs and all("aucune version" in e for e in erreurs), erreurs
