"""Le registre des autres modèles tient sa forme, et ses renvois tiennent.

`data/reference/referents.yaml` est le registre que `docs/architecture.md`
(§ 3.4) prévoit : aucun modèle ne fait autorité sur la loi, chacun confirme ou
contredit sur ce qu'il couvre. Ce n'est pas une bibliographie, et ces tests
exigent ce qui fait la différence. Un modèle dit ce dont il dépend, sinon deux
accords qui n'en font qu'un compteraient pour deux confirmations. Il dit ce
que sa licence permet, sinon un code à réciprocité finirait recopié dans un
dépôt sous Apache. Il dit où il a été lu, et quand, sinon la session suivante
relira tout. Et tout modèle que le dépôt nomme ailleurs, dans une fiche ou au
registre des sources, y a sa ligne : la liste se veut exhaustive.
"""

from __future__ import annotations

import datetime
import re
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[1]
REGISTRE = RACINE / "data" / "reference" / "referents.yaml"

#: Ce que fait le modèle. La différence qui compte est entre ce qui calcule une
#: pension (les trois premières) et ce qui projette des masses ou publie des
#: paramètres : on ne les confronte pas de la même manière.
NATURES = {
    "calculateur", "cas_types", "microsimulation_dynamique",
    "microsimulation_statique", "projection", "parametres", "methode",
}

#: Ce qu'on peut en lire. `documente` : la méthode et les résultats sont
#: publiés, pas le code ; `non_public` : seuls des résultats le sont.
PUBLICATIONS = {"ouvert", "sur_demande", "documente", "non_public"}

#: Ce que sa licence permet au dépôt d'en faire (§ 3.4).
USAGES = {"copier", "executer_a_part", "lire_et_citer", "selon_conditions",
          "resultats_publies"}

#: Ce qu'il confronte : le droit réel du scénario 1, les masses de la page
#: Coût, ou la mécanique des comptes notionnels de la proposition — son
#: arithmétique, jamais ses choix, que le README décide (§ 3.1).
CONFRONTE = {"scenario_1", "cout", "proposition"}

CHAMPS_EXIGES = (
    "id", "nom", "auteur", "nature", "publication", "licence", "usage",
    "confronte", "couvre", "confrontation", "lu_le", "lu_dans",
)
CHAMPS_CONNUS = set(CHAMPS_EXIGES) | {
    "pays", "code", "documentation", "version", "depend_de", "ecarts",
    "manifeste", "sas", "note",
}
CHAMPS_ECART = ("constat", "tranche", "preuve")

#: Les licences à réciprocité : un code qui les porte s'exécute à part, et
#: seules ses sorties entrent au dépôt (§ 3.4).
RECIPROQUES = re.compile(r"\b(A?GPL|LGPL|EUPL|CeCILL(?!-[BC])|BY-SA|ODbL)", re.I)


@pytest.fixture(scope="module")
def referents() -> list[dict]:
    return yaml.safe_load(REGISTRE.read_text(encoding="utf-8"))["referents"]


@pytest.fixture(scope="module")
def par_id(referents) -> dict[str, dict]:
    return {r["id"]: r for r in referents}


def test_chaque_modele_porte_les_champs_exiges(referents):
    for modele in referents:
        manquants = [c for c in CHAMPS_EXIGES if c not in modele]
        assert not manquants, f"{modele.get('id', modele)} : champs manquants {manquants}"
        inconnus = set(modele) - CHAMPS_CONNUS
        assert not inconnus, f"{modele['id']} : champs inconnus {sorted(inconnus)}"


def test_les_identifiants_sont_uniques_et_lisibles(referents):
    identifiants = [r["id"] for r in referents]
    doublons = {i for i in identifiants if identifiants.count(i) > 1}
    assert not doublons, f"identifiants en double : {sorted(doublons)}"
    for identifiant in identifiants:
        assert re.fullmatch(r"[a-z0-9_]+", identifiant), identifiant


def test_les_vocabulaires_sont_ceux_du_registre(referents):
    for modele in referents:
        assert modele["nature"] in NATURES, f"{modele['id']} : nature {modele['nature']}"
        assert modele["publication"] in PUBLICATIONS, (
            f"{modele['id']} : publication {modele['publication']}")
        assert modele["usage"] in USAGES, f"{modele['id']} : usage {modele['usage']}"
        confronte = modele["confronte"]
        assert confronte and set(confronte) <= CONFRONTE, (
            f"{modele['id']} : confronte {confronte}")


def test_un_code_ouvert_a_son_adresse_et_un_modele_ferme_n_en_a_pas(referents):
    """`ouvert` veut dire qu'on peut le lire : l'adresse du code est là."""
    for modele in referents:
        if modele["publication"] in {"ouvert", "sur_demande"}:
            assert str(modele.get("code", "")).startswith("https://"), (
                f"{modele['id']} : code {modele['publication']} sans adresse")
        else:
            assert "code" not in modele, (
                f"{modele['id']} : {modele['publication']}, mais une adresse de code")
            assert modele.get("documentation") or modele.get("manifeste"), (
                f"{modele['id']} : ni code, ni documentation, ni résultat au "
                "manifeste — rien ne dit qu'il existe")


def test_la_licence_decide_de_l_usage(referents):
    """La règle du § 3.4, tenue modèle par modèle.

    Un code sous GPL, EUPL ou AGPL s'exécute à part : le copier ferait passer
    le dépôt sous sa licence. Un code sans licence se lit et se cite, sans se
    copier. D'un modèle non public, on n'a que des résultats publiés.
    """
    for modele in referents:
        licence, usage = str(modele["licence"]), modele["usage"]
        if modele["publication"] == "non_public":
            assert usage == "resultats_publies", f"{modele['id']} : {usage}"
            continue
        if modele["publication"] == "ouvert" and RECIPROQUES.search(licence):
            assert usage == "executer_a_part", (
                f"{modele['id']} : sous {licence}, il s'exécute à part ({usage})")
        if usage == "executer_a_part":
            assert RECIPROQUES.search(licence), (
                f"{modele['id']} : exécuté à part, mais sous « {licence} »")
        if modele["publication"] == "ouvert" and licence == "aucune":
            assert usage == "lire_et_citer", f"{modele['id']} : sans licence, {usage}"


def test_un_modele_dit_ou_et_quand_il_a_ete_lu(referents):
    """« Une mémoire n'est pas une source » (`CLAUDE.md`)."""
    for modele in referents:
        assert isinstance(modele["lu_le"], datetime.date), (
            f"{modele['id']} : lu_le {modele['lu_le']!r} n'est pas une date")
        assert modele["lu_dans"], f"{modele['id']} : lu nulle part"
        for adresse in modele["lu_dans"]:
            assert re.match(r"https?://|data/|docs/|tests/|scripts/", adresse), (
                f"{modele['id']} : {adresse!r} n'est ni une adresse ni un fichier du dépôt")


def test_ce_dont_un_modele_depend_est_au_registre(referents, par_id):
    """Deux modèles qui partagent une source ne comptent que pour une
    confirmation : la source partagée doit donc avoir sa ligne."""
    for modele in referents:
        for source in modele.get("depend_de", []):
            assert source != modele["id"], f"{modele['id']} dépend de lui-même"
            assert source in par_id, f"{modele['id']} : dépend de {source}, absent du registre"


def test_un_ecart_dit_qui_avait_raison_et_sa_preuve(referents):
    """§ 3.3 : un écart se tranche par la preuve, et la fiche garde ce qui a
    tranché. Un écart sans preuve est une opinion."""
    for modele in referents:
        for ecart in modele.get("ecarts", []):
            manquants = [c for c in CHAMPS_ECART if not ecart.get(c)]
            assert not manquants, f"{modele['id']} : écart sans {manquants}"


def test_les_renvois_au_manifeste_et_au_registre_des_sources_existent(referents):
    manifeste = yaml.safe_load(
        (RACINE / "data" / "sources.yaml").read_text(encoding="utf-8"))["institutions"]
    jeux = {jeu["id"] for institution in manifeste.values()
            for jeu in institution.get("jeux", [])}
    sas = yaml.safe_load(
        (RACINE / "data" / "sources_a_explorer.yaml").read_text(encoding="utf-8"))["sources"]
    lignes = {s["id"] for s in sas}
    for modele in referents:
        inconnus = [j for j in modele.get("manifeste", []) if j not in jeux]
        assert not inconnus, f"{modele['id']} : {inconnus} absents de data/sources.yaml"
        inconnues = [s for s in modele.get("sas", []) if s not in lignes]
        assert not inconnues, (
            f"{modele['id']} : {inconnues} absentes de data/sources_a_explorer.yaml")


def test_tout_code_du_registre_des_sources_est_un_modele_du_registre(referents):
    """Le registre des sources range un modèle en `code` ; celui-ci dit ce
    qu'il vaut. Une ligne `code` que personne ne rattache serait un modèle
    sorti de la liste exhaustive."""
    sas = yaml.safe_load(
        (RACINE / "data" / "sources_a_explorer.yaml").read_text(encoding="utf-8"))["sources"]
    rattachees = {s for modele in referents for s in modele.get("sas", [])}
    orphelines = sorted(s["id"] for s in sas
                        if s["nature"] == "code" and s["id"] not in rattachees)
    assert not orphelines, f"modèles du registre des sources sans ligne ici : {orphelines}"


def test_tout_modele_qu_une_fiche_nomme_est_au_registre(par_id):
    """Le champ `referents` d'une fiche dit sa correspondance avec chaque autre
    modèle (contrat de la fiche) : il le nomme par son identifiant d'ici."""
    for chemin in sorted((RACINE / "data" / "reference" / "regles").rglob("*.yaml")):
        fiche = yaml.safe_load(chemin.read_text(encoding="utf-8"))
        if not isinstance(fiche, dict):
            continue
        inconnus = [m for m in fiche.get("referents") or {} if m not in par_id]
        assert not inconnus, (
            f"{chemin.relative_to(RACINE)} : {inconnus} absents de "
            "data/reference/referents.yaml")
