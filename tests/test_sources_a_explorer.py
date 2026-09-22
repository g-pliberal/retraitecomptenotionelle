"""Le sas des sources repérées tient sa forme, et son avancement se lit.

`data/sources_a_explorer.yaml` est l'inventaire des adresses remises au dépôt
et pas encore dépouillées — l'action 89 de la feuille de route. Ce n'est pas
une bibliographie : c'est un SAS, et ce que ces tests exigent est ce qui fait
la différence. Une ligne nomme le régime qu'elle concerne, par son code de
l'inventaire, sinon personne ne saura quelle fiche elle complète. Elle dit ce
qu'on va y chercher, sinon « explorer » ne veut rien dire. Elle dit ce qu'une
session obtient de l'hôte, mesuré, sinon la session suivante remesurera. Et
une ligne dépouillée porte sa date, sinon le sas se remplit sans jamais se
vider.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[1]
INVENTAIRE = RACINE / "data" / "sources_a_explorer.yaml"
METHODE = RACINE / "docs" / "exploration_sources.md"

#: Ce que porte une adresse. `index` est la plus importante à distinguer : elle
#: ne se lit pas, elle se DÉROULE.
NATURES = {"simulateur", "regle", "bareme", "document", "index", "code"}

#: Ce qu'une session obtient, et qui se mesure au lieu de se supposer. Chaque
#: valeur autre que `session` a sa recette — ou son renoncement motivé — dans
#: docs/exploration_sources.md.
ACCES = {"session", "chaine_incomplete", "navigateur", "git", "refus", "ferme"}

#: L'avancement. `epuise` est l'état terminal : la source a tout rendu, et ce
#: qu'elle a rendu est ailleurs, dans le manifeste ou dans les témoins.
STATUTS = {"a_explorer", "en_cours", "explore", "epuise", "sans_suite"}

CHAMPS_EXIGES = ("id", "url", "nature", "acces", "regimes", "a_en_tirer", "statut")
CHAMPS_CONNUS = set(CHAMPS_EXIGES) | {"note", "explore_le"}


@pytest.fixture(scope="module")
def sources() -> list[dict]:
    return yaml.safe_load(INVENTAIRE.read_text(encoding="utf-8"))["sources"]


@pytest.fixture(scope="module")
def codes_de_regime() -> set[str]:
    inventaire = yaml.safe_load(
        (RACINE / "data" / "reference" / "regimes" / "inventaire.yaml").read_text(
            encoding="utf-8"))
    return {fiche["code"] for fiche in inventaire["inventaire"]}


def test_chaque_ligne_porte_les_champs_exiges(sources):
    for source in sources:
        manquants = [champ for champ in CHAMPS_EXIGES if champ not in source]
        assert not manquants, f"{source.get('id', source)} : champs manquants {manquants}"
        inconnus = set(source) - CHAMPS_CONNUS
        assert not inconnus, f"{source['id']} : champs inconnus {sorted(inconnus)}"


def test_les_identifiants_sont_uniques_et_lisibles(sources):
    identifiants = [source["id"] for source in sources]
    doublons = {i for i in identifiants if identifiants.count(i) > 1}
    assert not doublons, f"identifiants en double : {sorted(doublons)}"
    for identifiant in identifiants:
        assert re.fullmatch(r"[a-z0-9_]+", identifiant), identifiant


def test_les_adresses_sont_uniques(sources):
    """Deux lignes pour une même adresse, c'est le travail fait deux fois."""
    adresses = [source["url"].rstrip("/") for source in sources]
    doublons = {a for a in adresses if adresses.count(a) > 1}
    assert not doublons, f"adresses en double : {sorted(doublons)}"


def test_les_vocabulaires_sont_ceux_que_la_methode_decrit(sources):
    for source in sources:
        assert source["nature"] in NATURES, f"{source['id']} : nature {source['nature']}"
        assert source["acces"] in ACCES, f"{source['id']} : acces {source['acces']}"
        assert source["statut"] in STATUTS, f"{source['id']} : statut {source['statut']}"


def test_tout_regime_cite_existe_a_l_inventaire(sources, codes_de_regime):
    """Une ligne qui nomme un régime nomme une FICHE, celle qu'elle complète."""
    for source in sources:
        inconnus = [c for c in source["regimes"] if c not in codes_de_regime]
        assert not inconnus, (
            f"{source['id']} : {inconnus} absents de "
            "data/reference/regimes/inventaire.yaml")


def test_une_source_dit_ce_qu_on_va_y_chercher(sources):
    """« À explorer » n'est pas une intention : c'est ce qui manque, nommé."""
    for source in sources:
        phrase = source["a_en_tirer"].strip()
        assert len(phrase) > 40, f"{source['id']} : {phrase!r} n'apprend rien"


def test_un_acces_qui_n_est_pas_direct_dit_ce_qu_on_a_rencontre(sources):
    """La règle du manifeste, reprise ici : un blocage sans note ne vaut rien.

    `data/sources.yaml` refuse un `blocage` qui ne dit pas ce qui a été
    essayé, parce que la session suivante recommencerait à l'aveugle. Les
    accès qui demandent un geste particulier — un maillon de certificat, un
    navigateur, un clone — le disent dans la note ou dans la méthode.
    """
    recettes = METHODE.read_text(encoding="utf-8")
    for source in sources:
        if source["acces"] == "session":
            continue
        assert source.get("note") or f"`{source['acces']}`" in recettes, (
            f"{source['id']} : accès « {source['acces']} » sans note ni recette "
            "dans docs/exploration_sources.md")


def test_chaque_acces_du_vocabulaire_a_sa_recette(sources):
    """Le vocabulaire ne s'enrichit pas sans que la méthode suive."""
    recettes = METHODE.read_text(encoding="utf-8")
    for acces in sorted({source["acces"] for source in sources}):
        assert f"`{acces}`" in recettes, (
            f"« {acces} » n'est décrit nulle part dans docs/exploration_sources.md")


def test_une_source_depouillee_porte_sa_date(sources):
    """Sans date, le sas se remplit et ne se vide jamais."""
    for source in sources:
        if source["statut"] in {"explore", "epuise", "sans_suite"}:
            date = str(source.get("explore_le", ""))
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", date), (
                f"{source['id']} : statut « {source['statut']} » sans date de "
                "dépouillement")
            assert source.get("note"), (
                f"{source['id']} : dépouillée sans dire ce qu'elle a donné")


def test_le_sas_se_vide_vers_le_manifeste(sources):
    """Une source épuisée a donné quelque chose, et ce quelque chose est ailleurs.

    Le manifeste `data/sources.yaml` ne porte que les sources dont une valeur
    est ENTRÉE dans le dépôt. Une ligne `epuise` dont la note ne renvoie à
    rien — ni un fichier, ni un témoin, ni un constat — est une ligne qu'on a
    fermée pour s'en débarrasser.
    """
    for source in sources:
        if source["statut"] != "epuise":
            continue
        note = source.get("note", "")
        assert re.search(r"data/|tests/|docs/|\brien\b", note), (
            f"{source['id']} : épuisée sans dire où est passé ce qu'elle portait")


def test_l_inventaire_couvre_les_regimes_les_plus_incomplets(sources, codes_de_regime):
    """Le lot vise bien les fiches partielles, pas les régimes déjà tenus.

    C'est la raison d'être de l'action 89 : les fiches `partiel` le sont
    surtout faute d'un barème lu chez celui qui l'applique. Si l'inventaire
    cessait de les viser, il faudrait le dire dans la feuille de route.
    """
    inventaire = yaml.safe_load(
        (RACINE / "data" / "reference" / "regimes" / "inventaire.yaml").read_text(
            encoding="utf-8"))["inventaire"]
    partielles = {f["code"] for f in inventaire if f["couverture"] == "partiel"}
    visees = {code for source in sources for code in source["regimes"]}
    assert len(partielles & visees) >= 15, (
        f"seules {len(partielles & visees)} fiches partielles sont visées")
