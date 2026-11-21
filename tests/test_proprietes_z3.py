"""Le contrôle Z3 des propriétés du droit (action 194) : ce qu'il trouve, ce
qu'il excuse, et qu'il avertit sans bloquer.

`scripts/proprietes_z3.py` pose à Z3 des questions sur les fiches du droit —
la durée requise, l'âge légal, l'âge du taux plein, la carrière longue, la
pension du régime général avec sa décote, sa proratisation et sa surcote, la
couverture des dates de toutes les fiches datées — et rend, pour chaque
propriété fausse, un cas chiffré. Les baisses que la loi a voulues, lues au
texte, sont déclarées dans `tests/cliquets_de_justesse/proprietes_attendues.yaml`,
chacune avec sa source : le contrôle ne montre que les vraies surprises.

Les règles qu'il interroge sont écrites une fois, en Python, pour deux usages
(`scripts/regles_z3/`) : exécutées, elles sont comparées au moteur ; données à
Z3, elles deviennent des questions. Z3 (`z3-solver`) n'est installé que par le
workflow `.github/workflows/proprietes.yml` (`.[z3]`) : sans lui, les tests qui
l'emploient se sautent, et la suite complète n'en dépend pas.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

ATTENDUS = RACINE / "tests" / "cliquets_de_justesse" / "proprietes_attendues.yaml"
WORKFLOW = RACINE / ".github" / "workflows" / "proprietes.yml"


def _attendus() -> list[dict]:
    return yaml.safe_load(ATTENDUS.read_text(encoding="utf-8"))["attendus"]


@pytest.fixture(scope="module")
def regles():
    """Les modules des règles, Z3 installé ; et ce que le moteur garde au code."""
    pytest.importorskip("z3")
    from regles_z3 import controle, duree, moteur, questions
    extrait = moteur.extraire(RACINE)
    return controle, duree, questions, extrait


# --------------------------------------------------------------- sans Z3
def test_chaque_cas_attendu_dit_sa_propriete_sa_nature_et_sa_source():
    attendus = _attendus()
    for a in attendus:
        assert {"propriete", "nature", "titre", "cas", "source"} <= set(a), a
        assert a["nature"] in {"legal", "ecart_connu"}, a
        assert str(a["source"]).strip(), a
        assert a["cas"], a
    # Les baisses que la loi a voulues, vérifiées au texte (consigne du 21 novembre 2026).
    legaux = " ".join(a["titre"] for a in attendus if a["nature"] == "legal")
    for mot in ("suspension", "décembre 1942", "160 trimestres", "juillet 2011"):
        assert mot in legaux, mot
    # Le 160 opposé aux nés avant 1900 n'est pas le droit : un écart connu, à part.
    connus = [a for a in attendus if a["nature"] == "ecart_connu"]
    assert any("avant 1900" in a["titre"] for a in connus)


def test_le_controle_tourne_a_part_apres_la_suite_et_n_echoue_pas_sur_une_surprise():
    texte = WORKFLOW.read_text(encoding="utf-8")
    flux = yaml.safe_load(texte)
    declencheurs = flux[True]          # « on », que YAML lit comme un booléen
    assert "push" not in declencheurs
    assert declencheurs["workflow_run"]["workflows"] == ["Tests"]
    assert "workflow_dispatch" in declencheurs
    etapes = [e for travail in flux["jobs"].values() for e in travail["steps"]]
    lancer = [e for e in etapes if "scripts/proprietes_z3.py" in e.get("run", "")]
    assert lancer, "le workflow ne lance pas le contrôle"
    # 1, une surprise : un avertissement, la course reste verte ; au-delà, le contrôle a cassé.
    assert '[ "$issue" -le 1 ]' in lancer[0]["run"]
    assert "::warning" in texte or "--github" in lancer[0]["run"]
    assert any("'.[dev,z3]'" in e.get("run", "") for e in etapes)
    # La suite complète n'installe pas Z3 : ses tests s'y sautent.
    assert "z3" not in (RACINE / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")


# --------------------------------------------------------------- avec Z3
def test_une_faute_de_frappe_dans_la_duree_requise_est_une_surprise_chiffree(regles):
    controle, duree, questions, extrait = regles
    versions = duree.lire_versions(RACINE)
    v = next(v for v in versions if v["id"] == "loi_de_2023")
    # 168 au lieu de 170 pour les nés en 1963 : la faute de l'essai du 21 novembre.
    v["table"] = [(a, b, 168 if (a, t) == (1963 * 12, 170) else t) for (a, b, t) in v["table"]]
    props = {p.id: p for p in questions.de_la_duree(versions, extrait["durees_avant_le_decret"])}
    r = controle.verifier(props["duree.naitre_plus_tard"], _attendus())
    assert r.statut == "surprise"
    (cas, *_) = r.surprises
    assert cas["champs"]["ne_apres"].startswith("1963-"), cas
    assert "168" in cas["texte"], cas


def test_un_cas_attendu_n_excuse_que_ses_propres_contre_exemples(regles):
    controle, duree, questions, extrait = regles
    versions = duree.lire_versions(RACINE)
    props = {p.id: p for p in questions.de_la_duree(versions, extrait["durees_avant_le_decret"])}
    prop = props["duree.naitre_plus_tard"]
    attendus = _attendus()
    r = controle.verifier(prop, attendus)
    assert r.statut == "attendue", r.surprises
    exemples = {a["titre"]: ex for a, ex in r.attendus}
    decembre = next(ex for t, ex in exemples.items() if "décembre 1942" in t)
    assert decembre["champs"]["date_effet"] == "2003-01-01"
    assert decembre["champs"]["ne_apres"] == "1942-12"
    # Sans les déclarations, la même propriété est une surprise.
    assert controle.verifier(prop, []).statut == "surprise"
    # Une déclaration que plus rien ne réalise se signale.
    faux = {"propriete": prop.id, "nature": "legal", "titre": "rien", "source": "aucune",
            "cas": {"date_effet": "1990-01-01", "ne_apres": "1950-01"}}
    r = controle.verifier(prop, attendus + [faux])
    assert [a["titre"] for a in r.disparus] == ["rien"]


def test_chaque_cas_attendu_nomme_une_propriete_du_controle_et_s_y_realise(regles):
    controle, _duree, questions, extrait = regles
    props = {p.id: p for p in questions.catalogue(RACINE, extrait)}
    for a in _attendus():
        assert a["propriete"] in props, a["propriete"]
        prop = props[a["propriete"]]
        assert set(a["cas"]) <= set(prop.champs), (a["titre"], sorted(prop.champs))
        assert controle.realise(prop, a) is not None, a["titre"]


def test_la_comparaison_au_moteur_signale_un_ecart(regles):
    controle, duree, _questions, extrait = regles
    from regles_z3.calcul import Py
    rg = duree.regle(duree.lire_versions(RACINE), Py, extrait["durees_avant_le_decret"])
    lignes = [(1960 * 12, 20220101, rg(1960 * 12, 20220101)),
              (1963 * 12, 20250101, rg(1963 * 12, 20250101) + 1)]
    n, ecarts = controle.comparer(lambda g, d: rg(g, d), lignes)
    assert n == 2
    assert ecarts == [((1963 * 12, 20250101), lignes[1][2], lignes[1][2] - 1)]
