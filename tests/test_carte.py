"""La carte des règles : ``data/reference/regles/``, une fiche par dispositif.

``docs/architecture.md``, § 6. Les fiches y suivent le contrat C.2 sans une
erreur ; ce qui leur manque encore pour être mûres se compte, et ne bloque
rien (§ 9.2). Elles ont repris, le 26 septembre 2026, les entrées du registre
de veille, et les exigences de la veille avec elles : chaque règle du
scénario 1 cite ses textes, dit ce qui en a été lu et quand, quand la relire,
et qui elle touche (``docs/veille_droit.md``).
"""

from __future__ import annotations

import re
import shutil
from datetime import date
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.noyau import carte, contrats

RACINE = Path(__file__).resolve().parents[1]
EXEMPLES = RACINE / "tests" / "temoins" / "exemples_officiels.yaml"


@pytest.fixture(scope="module")
def fiches() -> dict[str, dict]:
    return carte.fiches()


@pytest.fixture(scope="module")
def reformes():
    from retraite_notionnelle.donnees.regimes import charger_reformes

    return charger_reformes(RACINE_DONNEES)


def test_la_carte_tient():
    """Chaque fiche porte le nom de son fichier et suit son contrat sans
    erreur ; chaque relation relie des fiches qui existent (§ 6.7)."""
    assert carte.controler() == []


def test_chaque_regle_du_scenario_1_est_lue_et_datee(fiches):
    """Ce que la veille exigeait de chaque ligne, la carte l'exige de chaque
    fiche : un intitulé qui dit la règle, au moins un texte, une lecture datée
    et la date de la prochaine, qui vient après ; une source lue pour ce qui
    est conforme ; des exemples qui existent ; un effet dit."""
    connus = {e["id"] for e in yaml.safe_load(EXEMPLES.read_text(encoding="utf-8"))["exemples"]}
    for nom, fiche in fiches.items():
        assert len(str(fiche["intitule"]).split()) >= 6, nom
        textes = list(fiche.get("textes_a_rattacher") or [])
        textes += [t for v in fiche.get("versions") or [] for t in v.get("textes") or []]
        assert textes, (nom, "aucun texte cité")
        sources = fiche.get("sources") or {}
        lu_le, prochaine = sources.get("lu_le"), sources.get("prochaine_relecture")
        assert lu_le and prochaine, (nom, "lecture ou relecture sans date")
        assert str(prochaine) > str(lu_le), nom
        for lecture in sources.get("lectures") or []:
            assert len(str(lecture["reference"]).split()) >= 2, (nom, lecture)
        if fiche["etat"] == "conforme":
            assert sources.get("lectures"), (nom, "conforme sans source lue")
        inconnus = set(fiche.get("exemples") or []) - connus
        assert not inconnus, (nom, sorted(inconnus))
        assert len(str(fiche.get("effet") or "").split()) >= 3, (nom, "effet non dit")


def test_toute_reforme_recente_a_sa_fiche(fiches, reformes):
    """Une réforme entrée au calendrier depuis 2023 sans fiche qui la couvre
    est une réforme qu'on a portée sans dire où on l'a lue ni quand."""
    couvertes = {code for fiche in fiches.values() for code in fiche.get("reformes") or []}
    recentes = {reforme.code for reforme in reformes if reforme.date >= "2023-01-01"}
    assert not recentes - couvertes, sorted(recentes - couvertes)
    inconnues = couvertes - {reforme.code for reforme in reformes}
    assert not inconnues, sorted(inconnues)


def test_ce_qui_manque_se_compte_fiche_par_fiche(fiches):
    """Un manque nomme un champ que le contrat exige ; une fiche qui n'en a
    pas est mûre, et n'apparaît pas."""
    champs = set(contrats.objets("fiche")["relation"]["champs"])
    manques = carte.manques()
    assert set(manques) <= set(fiches)
    for nom, absents in manques.items():
        assert absents, nom
        assert {re.split(r"[.\[]", a)[0] for a in absents} <= champs, (nom, absents)


def _fiche_de_l_annexe_a() -> dict:
    texte = (RACINE / "docs" / "architecture.md").read_text(encoding="utf-8")
    debut = texte.index("### A.1 ")
    bloc = re.search(r"^```yaml\n(.*?)^```", texte[debut:], re.M | re.S).group(1)
    return yaml.safe_load(bloc)


def _ecrire(dossier: Path, fiche: dict) -> None:
    (dossier / f"{fiche['id']}.yaml").write_text(
        yaml.safe_dump(fiche, allow_unicode=True, sort_keys=False), encoding="utf-8")


def test_une_fiche_complete_est_mure(tmp_path):
    """La fiche A.1 de l'architecture, posée seule dans une carte : ni erreur,
    ni manque."""
    _ecrire(tmp_path, _fiche_de_l_annexe_a())
    assert carte.controler(tmp_path) == []
    assert carte.manques(tmp_path) == {}


def test_le_controle_dit_ce_qui_ne_tient_pas(tmp_path):
    """Une fiche qui ne porte pas le nom de son fichier, une relation vers une
    fiche absente ou vers elle-même, un renvoi à une fiche qui n'existe pas."""
    shutil.copy(carte.REGLES / "reversion.yaml", tmp_path / "reversion.yaml")
    shutil.copy(carte.REGLES / "reversion.yaml", tmp_path / "mal_nommee.yaml")
    relation = yaml.safe_load((carte.REGLES / "priorite_majorations_enfants.yaml")
                              .read_text(encoding="utf-8"))
    relation["fiches"] = [{"fiche": "licorne", "role": "absente de la carte"},
                          {"fiche": relation["id"], "role": "elle-même"}]
    relation["remplacee_par"] = "chimere"
    _ecrire(tmp_path, relation)
    erreurs = carte.controler(tmp_path)
    assert any(e.startswith("mal_nommee :") for e in erreurs), erreurs
    assert any("« licorne »" in e for e in erreurs), erreurs
    assert any(f"« {relation['id']} »" in e for e in erreurs), erreurs
    assert any("« chimere »" in e for e in erreurs), erreurs


def test_la_veille_est_une_vue_de_la_carte(tmp_path):
    """Ce qu'il faut relire se lit sur les fiches : l'état, l'âge de la
    dernière lecture, la date de relecture prévue."""
    fiche = yaml.safe_load((carte.REGLES / "reversion.yaml").read_text(encoding="utf-8"))
    fiche["id"], fiche["etat"] = "a_relire", "a_verifier"
    fiche["sources"]["lu_le"] = date(2026, 1, 1)
    fiche["sources"]["prochaine_relecture"] = date(2026, 6, 30)
    _ecrire(tmp_path, fiche)
    fraiche = {**fiche, "id": "fraiche", "etat": "conforme",
               "sources": {**fiche["sources"], "lu_le": date(2026, 9, 1),
                           "prochaine_relecture": date(2027, 3, 31)}}
    _ecrire(tmp_path, fraiche)
    vue = carte.a_relire(date(2026, 9, 26), jours=120, dossier=tmp_path)
    assert [f["id"] for f, _ in vue] == ["a_relire"]
    raisons = vue[0][1]
    assert raisons[0] == "a_verifier"
    assert any("268 jours" in r for r in raisons), raisons
    assert any("2026-06-30" in r for r in raisons), raisons


def test_une_fiche_ne_lit_que_des_presomptions_nommees(tmp_path):
    """Le champ `presomptions` d'une fiche nomme les présomptions qu'elle lit,
    sous leur nom au vocabulaire (§ 5.6) : un nom inconnu est refusé."""
    import shutil

    shutil.copytree(carte.REGLES, tmp_path, dirs_exist_ok=True)
    chemin = tmp_path / "pension_differee_fonction_publique.yaml"
    fiche = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    fiche["presomptions"]["intuition"] = "ce que la fiche devine"
    chemin.write_text(yaml.safe_dump(fiche, allow_unicode=True), encoding="utf-8")
    erreurs = carte.controler(tmp_path)
    assert any("« intuition »" in e for e in erreurs), erreurs


def test_chaque_presomption_est_lue_par_une_fiche():
    """Une présomption que nulle fiche ne lit serait une valeur par défaut
    sans règle : chacune dit, par ses fiches, ce qu'elle décide."""
    from retraite_notionnelle.noyau import vocabulaire

    lecteurs = carte.lecteurs_des_presomptions()
    orphelines = sorted(set(vocabulaire.presomptions()) - set(lecteurs))
    assert not orphelines, orphelines
