"""L'inventaire des avantages non contributifs, et son exhaustivité.

Le dépôt portait trois listes partielles et discordantes de ce que le scénario 1
sert au-delà de la cotisation : les champs de ``Neutralisations``, les codes
``avantages_non_contributifs`` des fiches de régime, et les lignes de la cascade
``AvantageApplique``. Aucune ne disait ce que chaque ligne coûte, et aucune ne
contenait les deux autres.

``legislation/avantages_non_contributifs.yaml`` est leur union, complétée de ce
qu'aucune ne portait. Ces tests sont ce qui l'empêche de redevenir partielle :
tout code employé par l'une des trois listes doit avoir sa ligne dans
l'inventaire, sous son code ou sous un alias.
"""

from __future__ import annotations

import re

import pytest
import yaml

from retraite_notionnelle.config import RACINE_DONNEES, Neutralisations

CHEMIN = RACINE_DONNEES / "reference" / "legislation" / "avantages_non_contributifs.yaml"

#: Les quatre états possibles du modèle à l'égard d'un avantage, et les trois
#: façons d'en mesurer le coût. Le vocabulaire est fermé : un cinquième état
#: inventé au fil de l'eau rendrait l'inventaire illisible.
ETATS = {"chiffre", "integre", "declare", "absent"}
MESURES = {"modele", "serie_publiee", "aucune"}


@pytest.fixture(scope="module")
def inventaire() -> dict:
    with CHEMIN.open(encoding="utf-8") as flux:
        return yaml.safe_load(flux)


@pytest.fixture(scope="module")
def par_code(inventaire) -> dict[str, dict]:
    """Chaque avantage sous son code ET sous chacun de ses alias."""
    table: dict[str, dict] = {}
    for avantage in inventaire["avantages"]:
        for nom in [avantage["code"], *avantage.get("alias", [])]:
            assert nom not in table, f"code ou alias en double : {nom}"
            table[nom] = avantage
    return table


def _codes_de_la_cascade() -> set[str]:
    """Les codes que ``ScenarioActuel.calculer`` peut émettre.

    Lus dans la SOURCE plutôt que par une simulation : une cascade ne rend que
    les avantages qu'une carrière donnée déclenche, et aucune carrière ne les
    déclenche tous. La source, elle, les porte tous.
    """
    from retraite_notionnelle.scenarios import actuel

    source = __import__("inspect").getsource(actuel)
    return set(re.findall(r'AvantageApplique\(\s*code="([a-z_]+)"', source))


def test_le_vocabulaire_de_l_inventaire_est_ferme(inventaire):
    familles = set(inventaire["familles"])
    for avantage in inventaire["avantages"]:
        code = avantage["code"]
        assert avantage["famille"] in familles, f"{code} : famille inconnue"
        assert avantage["etat_modele"] in ETATS, f"{code} : état inconnu"
        assert avantage["cout"]["mesurable_par"] in MESURES, f"{code} : mesure inconnue"


def test_une_ligne_de_cascade_est_declaree_si_et_seulement_si_elle_chiffre(inventaire):
    """``ligne_cascade`` et ``etat_modele: chiffre`` disent la même chose.

    Un avantage chiffré est un avantage dont la cascade isole le montant ; il a
    donc une ligne. Un avantage qui n'est pas chiffré n'en a pas, et doit dire
    pourquoi — c'est le champ ``pourquoi_pas_chiffre``, qui est ce qui empêche
    un « non » de passer pour une évidence.
    """
    for avantage in inventaire["avantages"]:
        code, etat = avantage["code"], avantage["etat_modele"]
        if etat == "chiffre":
            assert avantage["ligne_cascade"], f"{code} : chiffré sans ligne de cascade"
        else:
            assert avantage["ligne_cascade"] is None, f"{code} : ligne de cascade sans chiffrage"
            assert avantage.get("pourquoi_pas_chiffre"), f"{code} : non chiffré sans raison écrite"


def test_toute_ligne_de_cascade_a_sa_ligne_d_inventaire(par_code):
    manquants = {
        code for code in _codes_de_la_cascade()
        if code not in par_code and not any(
            a["ligne_cascade"] == code for a in par_code.values()
        )
    }
    assert manquants == set(), (
        "lignes de cascade absentes de l'inventaire : " + ", ".join(sorted(manquants))
    )


def test_toute_ligne_de_cascade_pointe_un_avantage_chiffre(inventaire):
    cascade = _codes_de_la_cascade()
    for avantage in inventaire["avantages"]:
        ligne = avantage["ligne_cascade"]
        if ligne is not None:
            assert ligne in cascade, f"{avantage['code']} : ligne {ligne} inconnue de la cascade"


def test_tout_champ_de_neutralisations_a_sa_ligne_d_inventaire(par_code):
    manquants = {nom for nom in vars(Neutralisations()) if nom not in par_code}
    assert manquants == set(), (
        "champs de Neutralisations absents de l'inventaire : " + ", ".join(sorted(manquants))
    )


def test_tout_code_declare_par_une_fiche_a_sa_ligne_d_inventaire(par_code):
    """Les fiches de régime déclarent, l'inventaire répond.

    C'est le test qui coûte le plus cher à ignorer : une fiche nouvelle peut
    introduire un code d'un trait de plume, et sans ce test personne ne saurait
    que le dépôt prétend servir un avantage qu'il n'a jamais inventorié.
    """
    declares: set[str] = set()
    dossier = RACINE_DONNEES / "reference" / "regimes"
    for chemin in sorted(dossier.glob("*.yaml")):
        with chemin.open(encoding="utf-8") as flux:
            declares |= _codes_declares(yaml.safe_load(flux))
    manquants = declares - set(par_code)
    assert manquants == set(), (
        "codes déclarés par une fiche et absents de l'inventaire : "
        + ", ".join(sorted(manquants))
    )


def _codes_declares(objet) -> set[str]:
    if isinstance(objet, dict):
        codes: set[str] = set()
        for cle, valeur in objet.items():
            if cle == "avantages_non_contributifs" and isinstance(valeur, list):
                codes |= set(valeur)
            else:
                codes |= _codes_declares(valeur)
        return codes
    if isinstance(objet, list):
        return set().union(*(_codes_declares(x) for x in objet)) if objet else set()
    return set()


def test_les_renvois_a_la_veille_existent(inventaire):
    chemin = RACINE_DONNEES / "reference" / "legislation" / "veille.yaml"
    with chemin.open(encoding="utf-8") as flux:
        connues = {entree["id"] for entree in yaml.safe_load(flux)["entrees"]}
    for avantage in inventaire["avantages"]:
        inconnues = set(avantage.get("veille") or ()) - connues
        assert inconnues == set(), (
            f"{avantage['code']} : entrées de veille inconnues — "
            + ", ".join(sorted(inconnues))
        )


def test_les_renvois_au_manifeste_des_sources_existent(inventaire):
    with (RACINE_DONNEES / "sources.yaml").open(encoding="utf-8") as flux:
        connues = _ids(yaml.safe_load(flux))
    for avantage in inventaire["avantages"]:
        source = avantage["cout"].get("source_id")
        if source is not None:
            assert source in connues, f"{avantage['code']} : source_id inconnu — {source}"


def _ids(objet) -> set[str]:
    if isinstance(objet, dict):
        trouves = {objet["id"]} if isinstance(objet.get("id"), str) else set()
        for valeur in objet.values():
            trouves |= _ids(valeur)
        return trouves
    if isinstance(objet, list):
        return set().union(*(_ids(x) for x in objet)) if objet else set()
    return set()


def test_une_source_publiee_nomme_toujours_sa_source(inventaire):
    for avantage in inventaire["avantages"]:
        if avantage["cout"]["mesurable_par"] == "serie_publiee":
            assert avantage["cout"].get("source_id"), (
                f"{avantage['code']} : série publiée annoncée sans source_id"
            )
