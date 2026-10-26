"""Les adresses du site, dans un vrai navigateur (action 174, étape 4).

Chaque page a son adresse : sa page dans le chemin (``cout/``), le lecteur —
sa carrière, ses réglages — derrière le ``#``, que le navigateur ne transmet à
aucun serveur. L'ancienne forme, la page derrière le ``#``
(``#/cout?indexation=prix``), est celle des partages publiés avant le
changement, des marque-pages et des liens du site du parti : elle mène, par une
redirection que fait le navigateur, à la nouvelle. Aucune ne doit se perdre.

Les tests de ``test_adresses.py`` disent comment une adresse se lit et s'écrit ;
ceux-ci disent où le lecteur arrive, et ce qu'il y voit : la page, l'adresse
d'arrivée, les réglages, la section ouverte. Chromium sans fenêtre les joue
(``tests/js/ecrans.mjs``), le dépôt servi tel quel ; sans lui, ils sont passés.
"""

from __future__ import annotations

import functools

import pytest

from test_ecrans import REQUETE, jouer

#: Ce que dit la page Coût quand ses réglages ne sont pas ceux par défaut.
REGLAGES_PAR_DEFAUT = "Ces chiffres sont ceux des réglages par défaut, pas des vôtres."

#: Le titre de l'onglet d'une page : son nom, puis celui du site ; l'accueil a le
#: sien, celui qu'un moteur de recherche affiche (action 174).
TITRE = " — Retraite en comptes notionnels"
TITRE_DE_L_ACCUEIL = "Retraite à comptes notionnels — programme et simulateur"


def _onglet(scenario: dict) -> str:
    nom = scenario["titre"]
    return TITRE_DE_L_ACCUEIL if nom == "Programme" else f"{nom}{TITRE}"

#: Chaque scénario : d'où l'on part (``depart``, relatif à la racine du site),
#: ce qu'on fait (``gestes``), où l'on doit arriver (``attend``) et ce que la
#: page doit montrer. ``vers`` d'un geste dit s'il change de page (``page``), la
#: rend de nouveau sur place (``ici``) ou ouvre seulement une section
#: (``section``).
SCENARIOS = [
    # -- l'ancienne forme : la page derrière le `#` ---------------------------
    {"nom": "une ancienne page sous d'autres réglages",
     "depart": "index.html#/cout?indexation=prix",
     "attend": {"chemin": "cout/", "hash": "#indexation=prix"},
     "titre": "Coût", "montre": [REGLAGES_PAR_DEFAUT], "ancienne": True},
    {"nom": "une ancienne simulation",
     "depart": f"index.html#/simuler?{REQUETE}",
     "attend": {"chemin": "simuler/", "hash": f"#{REQUETE}"},
     "titre": "Simuler", "montre": ["Résultats"], "ancienne": True},
    {"nom": "le lien que le site du parti recommandait",
     "depart": "index.html#/simuler",
     "attend": {"chemin": "simuler/", "hash": ""},
     "titre": "Simuler", "ancienne": True},
    {"nom": "l'ancien accueil",
     "depart": "index.html#/",
     "attend": {"chemin": "", "hash": ""},
     "titre": "Programme", "ancienne": True},
    {"nom": "l'ancien accueil sous d'autres réglages",
     "depart": "index.html#/?indexation=prix",
     "attend": {"chemin": "", "hash": "#indexation=prix"},
     "titre": "Programme", "ancienne": True},
    {"nom": "l'ancienne simulation de l'accueil",
     "depart": f"index.html#/?{REQUETE}",
     "attend": {"chemin": "simuler/", "hash": f"#{REQUETE}"},
     "titre": "Simuler", "ancienne": True},
    {"nom": "l'ancien « Cumul versé »",
     "depart": f"index.html#/trajectoire?{REQUETE}",
     "attend": {"chemin": "simuler/", "hash": f"#cumul&{REQUETE}"},
     "titre": "Simuler", "ouvertes": ["cumul"], "ancienne": True},
    {"nom": "les anciennes « Sources »",
     "depart": "index.html#/donnees",
     "attend": {"chemin": "methode/", "hash": "#sources"},
     "titre": "Méthode et sources", "actif": "sources", "ancienne": True},
    {"nom": "une page qui n'existe pas",
     "depart": "index.html#/cuot",
     "attend": {"chemin": "", "hash": ""},
     "titre": "Programme", "ancienne": True},
    # -- la nouvelle forme : la page dans le chemin ---------------------------
    {"nom": "une page sous d'autres réglages",
     "depart": "cout/#indexation=prix",
     "attend": {"chemin": "cout/", "hash": "#indexation=prix"},
     "titre": "Coût", "montre": [REGLAGES_PAR_DEFAUT]},
    {"nom": "une section ouverte par l'adresse",
     "depart": f"simuler/#cumul&{REQUETE}",
     "attend": {"chemin": "simuler/", "hash": f"#cumul&{REQUETE}"},
     "titre": "Simuler", "ouvertes": ["cumul"]},
    {"nom": "chaque page s'ouvre par son dossier",
     "depart": "risque/",
     "attend": {"chemin": "risque/", "hash": ""},
     "titre": "Pourquoi changer"},
    # -- les gestes ------------------------------------------------------------
    {"nom": "un lien du bandeau emporte les réglages",
     "depart": "index.html#indexation=prix",
     "attend": {"chemin": "cout/", "hash": "#indexation=prix"},
     "gestes": [{"cliquer": 'header nav a[href="cout/#indexation=prix"]', "vers": "page"}],
     "titre": "Coût", "montre": [REGLAGES_PAR_DEFAUT]},
    {"nom": "le lien de la page où l'on est ne recharge rien",
     "depart": f"simuler/#{REQUETE}",
     "attend": {"chemin": "simuler/", "hash": ""},
     "gestes": [{"cliquer": 'header nav a[aria-current="page"]', "vers": "ici"}],
     "titre": "Simuler", "meme_document": True},
    {"nom": "calculer depuis l'accueil mène aux résultats, et les retient",
     "depart": "index.html",
     "attend": {"chemin": "simuler/", "hash_commence": "#resultats&naissance="},
     "gestes": [{"cliquer": "form.simulateur-court button[type=submit]", "vers": "page"}],
     "titre": "Simuler", "montre": ["Résultats"], "memoire": "naissance=",
     "actif": "resultats"},
    {"nom": "un renvoi vers la section d'une autre page l'ouvre",
     "depart": "cas-types/",
     "attend": {"chemin": "cout/", "hash": "#cout-equilibre"},
     "gestes": [{"cliquer": 'a[data-vers="cout-equilibre"]', "vers": "page"}],
     "titre": "Coût", "ouvertes": ["cout-equilibre"]},
    {"nom": "un renvoi vers une section de la même page ne change pas l'adresse",
     "depart": "methode/",
     "attend": {"chemin": "methode/", "hash": ""},
     "gestes": [{"cliquer": 'a[data-vers="sources"]', "vers": "section"}],
     "titre": "Méthode et sources", "actif": "sources", "meme_document": True},
]


@functools.lru_cache(maxsize=None)
def _etats() -> dict:
    """Chaque scénario joué, dans un navigateur : ce qu'il a vu à l'arrivée."""
    resultat = jouer({"ecrans": [], "chargements": [], "routes": [], "adresses": SCENARIOS})
    return {etat["nom"]: etat for etat in resultat["adresses"]}


def _ou(etat: dict) -> str:
    return f"{etat['chemin']!r} {etat['hash']!r}"


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda s: s["nom"])
def test_une_adresse_mene_ou_le_lecteur_l_attend(scenario):
    """La page ouverte, son adresse d'arrivée, son titre et ce qu'elle montre."""
    etat = _etats()[scenario["nom"]]
    attendu = scenario["attend"]
    assert not etat["delai"], (
        f"{scenario['depart']} : la page ne s'est pas rendue à {attendu} — "
        f"elle est restée à {_ou(etat)}")
    assert etat["chemin"] == attendu["chemin"], f"{scenario['depart']} arrive à {_ou(etat)}"
    if "hash_commence" in attendu:
        assert etat["hash"].startswith(attendu["hash_commence"]), (
            f"{scenario['depart']} arrive à {_ou(etat)}")
    else:
        assert etat["hash"] == attendu["hash"], f"{scenario['depart']} arrive à {_ou(etat)}"
    assert etat["titre"] == _onglet(scenario)
    for texte in scenario.get("montre", []):
        assert etat["montre"][texte], f"{scenario['depart']} : la page ne dit pas « {texte} »"
    for identifiant in scenario.get("ouvertes", []):
        assert identifiant in etat["ouvertes"], (
            f"{scenario['depart']} : la section {identifiant!r} n'est pas ouverte "
            f"({etat['ouvertes']})")
    if "actif" in scenario:
        assert etat["actif"] == scenario["actif"]
    if "memoire" in scenario:
        assert scenario["memoire"] in (etat["memoire"] or ""), (
            "le calcul n'a pas été retenu : le lecteur ne retrouvera pas sa carrière")
    assert etat["meme_document"] is scenario.get("meme_document", False), (
        "la page " + ("a été rechargée" if scenario.get("meme_document") else "n'a pas changé"))


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda s: s["nom"])
def test_aucune_page_ne_charge_une_ressource_qui_manque(scenario):
    """Un chemin relatif faux dans le dossier d'une page ne charge rien : le
    pilote compte toute ressource en erreur, et toute exception de la page."""
    etat = _etats()[scenario["nom"]]
    assert etat["ressources"] == [], etat["ressources"]
    assert etat["erreurs"] == [], etat["erreurs"]


@pytest.mark.parametrize("scenario", [s for s in SCENARIOS if s.get("ancienne")],
                         ids=lambda s: s["nom"])
def test_une_ancienne_adresse_est_remplacee_et_non_empilee(scenario):
    """« Précédent » ne ramène pas à l'ancienne adresse, qui renverrait aussitôt
    à la nouvelle : l'ouverture n'ajoute qu'une entrée à l'historique, celle de
    la page d'arrivée."""
    assert _etats()[scenario["nom"]]["historique"] == 1
