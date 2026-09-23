"""Ce que le modèle calcule, sous un nom que la prose peut citer.

    <!--chiffre:mesure(ecart?scenario=2&generation=1930)-->-83,9<!--/--> %

Les sondes de ``verifier_prose.py`` lisent le dépôt : un fichier, une table,
une cellule. Elles ne savaient pas lire le MODÈLE, et c'était le gros de ce
qui restait : les six résultats du README, le §5 de ``limites.md``, les
sections chiffrées de la méthodologie disent ce que le modèle calcule, un
écart en pourcentage, un coût en milliards, une part de PIB. Ces chiffres-là
ne sont dans aucune table ; ils étaient recopiés d'une exécution, et ils
vieillissaient à chaque changement du modèle sans que rien le dise. Le
18 septembre, le README donnait −81,5 % à la génération 1930 sous la règle
par défaut ; aucune carrière du dépôt ne rendait plus ce chiffre.

Chaque mesure est une fonction nommée, qui prend ses réglages en
``clé=valeur`` et rend UN nombre, dans l'unité où la prose l'écrit : un écart
en pour-cent, un coût en milliards d'euros. Elle est mémorisée pour la durée
du processus, et les objets coûteux — un simulateur par jeu de règles, le coût
agrégé, dix-sept secondes — ne se calculent qu'une fois, quel que soit le
nombre de chiffres qui les citent.

Ajouter une mesure, c'est ajouter une fonction à ``MESURES`` : son nom est ce
que la prose écrit, sa docstring ce que ``--sondes`` imprime.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from functools import lru_cache
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

#: Les scénarios par leur numéro, celui que la prose emploie partout.
SCENARIOS = {
    "1": "actuel",
    "2": "notionnel_retroactif",
    "3": "notionnel_prospectif",
    "4": "notionnel_retroactif_employeur",
    "5": "notionnel_prospectif_employeur",
    "6": "notionnel_liberal",
    "garantie": "garantie_vieillesse_liberal",
}

#: La carrière de référence de la prose : celle du tableau des générations du
#: README, que ``construire_tableaux_md.py`` calcule — un salarié du privé non
#: cadre, entré à vingt ans et parti à soixante-deux. Une mesure qui en veut
#: une autre le dit dans ses réglages.
CARRIERE = {"affiliation": "salarie_prive_non_cadre", "sexe": "H",
            "debut": "20", "depart": "62"}


def _scenario(nom: str) -> str:
    if nom not in SCENARIOS:
        raise ValueError(f"scénario inconnu « {nom} » ; attendu : {', '.join(SCENARIOS)}")
    return SCENARIOS[nom]


@lru_cache(maxsize=None)
def _parametres(indexation: str = "", lissage: str = ""):
    """Les paramètres par défaut, sous la règle et le lissage demandés."""
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.config import ModeIndexation

    parametres = Parametres()
    if indexation:
        parametres = replace(parametres, mode_indexation=ModeIndexation(indexation))
    if lissage:
        parametres = replace(parametres, lissage_indexation=int(lissage))
    return parametres


@lru_cache(maxsize=None)
def _simulateur(parametres):
    from retraite_notionnelle.simulateur import Simulateur

    return Simulateur(parametres)


#: L'exemple du §3 du README : une fonctionnaire d'État née en 1975, vingt pour
#: cent de primes, partie à soixante-quatre ans. ``exemple=fonctionnaire`` le
#: désigne d'un mot, et ``construire_tableaux_md.py`` en écrit la sortie.
EXEMPLES = {
    "fonctionnaire": {"generation": "1975", "sexe": "F",
                      "affiliation": "fonctionnaire_etat", "debut": "22",
                      "depart": "64", "primes": "0.2", "profil": "ascendant"},
    # L'agent de conduite de l'introduction du README, parti à cinquante ans
    # avant la bascule : ses scénarios 3 et 5 sont le système actuel.
    "sncf": {"generation": "1955", "sexe": "H", "affiliation": "agent_sncf",
             "debut": "20", "depart": "50", "niveau": "1.1", "profil": "ascendant"},
    # Deux salariés du privé non cadres, actifs à la bascule, pour la fiche
    # de paie : au salaire moyen, et au SMIC — le niveau et le profil plat du
    # cas type « smic_carriere_complete ».
    "salaire_moyen": {"generation": "1980", "sexe": "H",
                      "affiliation": "salarie_prive_non_cadre", "debut": "22",
                      "depart": "64", "niveau": "1.0", "profil": "plat"},
    # La carrière que `limites.md` §5 quater oppose à la littérature : une
    # carrière ascendante au salaire moyen, entrée à 22 ans, née en 1975,
    # liquidée à 64 ans — dans le privé et à l'État.
    "litterature_prive": {"generation": "1975", "sexe": "H",
                          "affiliation": "salarie_prive_non_cadre", "debut": "22",
                          "depart": "64", "niveau": "1.0", "profil": "ascendant"},
    "litterature_etat": {"generation": "1975", "sexe": "H",
                         "affiliation": "fonctionnaire_etat", "debut": "22",
                         "depart": "64", "niveau": "1.0", "profil": "ascendant"},
    "smic": {"generation": "1980", "sexe": "H",
             "affiliation": "salarie_prive_non_cadre", "debut": "22",
             "depart": "64", "niveau": "0.55", "profil": "plat"},
}


@lru_cache(maxsize=None)
def _comparaison(generation: int, indexation: str, lissage: str,
                 affiliation: str, sexe: str, debut: int, depart: int,
                 primes: float, profil: str, niveau: float):
    simulateur = _simulateur(_parametres(indexation, lissage))
    options = {"part_primes": primes} if primes else {}
    if niveau:
        options["niveau_salaire"] = niveau
    if profil:
        options["profil_carriere"] = profil
    carriere = simulateur.carriere_simple(
        annee_naissance=generation, sexe=sexe, affiliation=affiliation,
        age_debut=debut, age_liquidation=depart, **options)
    return simulateur.simuler(carriere)


def _comparaison_de(reglages: dict[str, str]):
    exemple = reglages.get("exemple")
    if exemple is not None and exemple not in EXEMPLES:
        raise ValueError(f"exemple inconnu « {exemple} » ; il y a {', '.join(EXEMPLES)}")
    voulu = {**CARRIERE, **EXEMPLES.get(exemple, {}), **reglages}
    return _comparaison(int(voulu["generation"]), voulu.get("indexation", ""),
                        voulu.get("lissage", ""), voulu["affiliation"],
                        voulu["sexe"], int(voulu["debut"]), int(voulu["depart"]),
                        float(voulu.get("primes", 0) or 0), voulu.get("profil", ""),
                        float(voulu.get("niveau", 0) or 0))


def ecart(**reglages: str) -> float:
    """Écart d'un scénario au système actuel, en %, sur une carrière.

    ``scenario`` (2 à 6) et ``generation`` sont requis ; ``indexation``,
    ``lissage``, ``affiliation``, ``sexe``, ``debut``, ``depart``, ``primes``
    et ``profil`` changent la règle ou la carrière, qui est sinon celle du
    tableau des générations du README ; ``exemple=…`` en désigne une autre
    d'un mot.
    """
    comparaison = _comparaison_de(reglages)
    return comparaison.variation(_scenario(reglages["scenario"])) * 100


def pension(**reglages: str) -> float:
    """Pension annuelle d'un scénario, en euros courants, sur une carrière.

    Mêmes réglages que ``ecart`` ; ``exemple=fonctionnaire`` pour celle du
    §3 du README. ``part=totale`` y ajoute le pilier capitalisé,
    ``part=capitalisee`` n'en rend que la rente, ``part=obligatoire`` et
    ``part=volontaire`` chacun de ses deux morceaux.
    """
    comparaison = _comparaison_de(reglages)
    scenario = _scenario(reglages["scenario"])
    part = reglages.get("part", "repartition")
    if part == "repartition":
        return getattr(comparaison, scenario).pension_annuelle
    if part == "totale":
        return comparaison.pension_totale(scenario)
    if part == "capitalisee":
        return comparaison.rente_capitalisee(scenario)
    if part == "obligatoire":
        return (comparaison.rente_capitalisee(scenario)
                - comparaison.rente_capitalisee_volontaire(scenario))
    if part == "volontaire":
        return comparaison.rente_capitalisee_volontaire(scenario)
    raise ValueError(f"part inconnue « {part} »")


def aujourd_hui(**reglages: str) -> float:
    """La pension d'aujourd'hui d'un retraité, en écart à sa pension de départ
    ramenée par l'indice des prix, en % — ce que la page lui affichait avant.

    Mêmes réglages de carrière que ``ecart`` : la carrière doit être déjà
    liquidée. ``quoi=coefficient&regime=…`` rend plutôt le coefficient nominal
    que le texte d'un régime a appliqué depuis le départ.
    """
    comparaison = _comparaison_de(reglages)
    if comparaison.aujourd_hui is None:
        raise ValueError("cette carrière n'est pas encore liquidée")
    actuel = comparaison.aujourd_hui.actuel
    quoi = reglages.get("quoi", "ecart_aux_prix")
    if quoi == "coefficient":
        return next(r.coefficient for r in actuel.regimes if r.regime == reglages["regime"])
    if quoi != "ecart_aux_prix":
        raise ValueError(f"quoi inconnu « {quoi} »")
    macro = _simulateur(_parametres(reglages.get("indexation", ""),
                                    reglages.get("lissage", ""))).macro
    par_les_prix = comparaison.actuel.pension_annuelle * macro.coefficient_prix(
        comparaison.carriere.annee_liquidation, comparaison.aujourd_hui.annee)
    return (actuel.pension_annuelle / par_les_prix - 1) * 100


def part_salariale_versee(**reglages: str) -> float:
    """Part de la cotisation totale versée par l'assuré lui-même, en %, sur une carrière."""
    return 100 - part_employeur(**reglages)


def part_employeur(**reglages: str) -> float:
    """Part de la cotisation totale versée par l'employeur, en %, sur une carrière."""
    return _comparaison_de(reglages).contribution_employeur.part * 100


def cumul_indexation(**reglages: str) -> float:
    """Ce qu'une règle d'indexation fait d'un euro, de ``de`` à ``a``.

    ``regle`` est un mode d'indexation (``pib_nominal``, ``prix``…) ;
    ``lissage`` au besoin. Rend le coefficient, « ×5,44 ».
    """
    from retraite_notionnelle.moteur.indexation import Indexation

    parametres = _parametres(reglages.get("regle", ""), reglages.get("lissage", ""))
    simulateur = _simulateur(parametres)
    return Indexation(simulateur.macro, parametres).coefficient(
        int(reglages["de"]), int(reglages["a"]))


def conserve(**reglages: str) -> float:
    """Pouvoir d'achat qu'une règle conserve de 1940 à 2025, en %.

    La colonne du tableau des règles d'indexation, celle que le site affiche.
    """
    from retraite_notionnelle.web.pages import (ANNEE_ARRIVEE_COMPAREE,
                                                ANNEE_VERSEMENT_COMPARE)

    bornes = {"de": str(ANNEE_VERSEMENT_COMPARE), "a": str(ANNEE_ARRIVEE_COMPAREE)}
    regle = cumul_indexation(**{**reglages, **bornes})
    prix = cumul_indexation(regle="prix", **bornes)
    return regle / prix * 100


def fois_prix(**reglages: str) -> float:
    """Combien de fois les prix une règle rend de 1940 à 2025 — « onze fois »."""
    return conserve(**reglages) / 100


@lru_cache(maxsize=None)
def _cout(ponderation: str = "effectifs"):
    """Le coût agrégé, sous les règles par défaut — celui de la page Coût."""
    from retraite_notionnelle import cout as C
    from retraite_notionnelle.donnees.assiette import AssietteActivite
    from retraite_notionnelle.donnees.depenses import DepensesRetraite
    from retraite_notionnelle.donnees.equilibre import ComptesRetraite
    from retraite_notionnelle.donnees.population import Population

    parametres = _parametres()
    racine = parametres.racine_donnees
    return C.calculer_cout(
        _simulateur(parametres), DepensesRetraite(racine), Population(racine),
        ComptesRetraite(racine), assiette=AssietteActivite(racine),
        ponderation=ponderation)


def _cout_de(reglages: dict[str, str]):
    return _cout(reglages.get("ponderation", "effectifs"))


def cumul_passe(**reglages: str) -> float:
    """Cumul du coût d'un système sur les années observées, en Md€ constants.

    ``scenario`` : 1 à 6. ``ponderation=egale`` pour l'ancienne convention.
    """
    return _cout_de(reglages).cumul(_scenario(reglages["scenario"])) / 1000


def ecart_passe(**reglages: str) -> float:
    """Écart du cumul observé d'un système à celui du système actuel, en %."""
    cout = _cout_de(reglages)
    return (cout.cumul(_scenario(reglages["scenario"])) / cout.cumul("actuel") - 1) * 100


def _avenir(reglages: dict[str, str]):
    ligne = _cout_de(reglages).avenir.annee(int(reglages["annee"]))
    if ligne is None:
        raise ValueError(f"l'année {reglages['annee']} n'est pas dans la trajectoire")
    return ligne


def cout_annee(**reglages: str) -> float:
    """Coût d'un système une année de la trajectoire, en Md€ constants."""
    return _avenir(reglages).cout_constants(_scenario(reglages["scenario"])) / 1000


def part_pib(**reglages: str) -> float:
    """Coût d'un système une année, en % du PIB de cette année."""
    return _avenir(reglages).part_pib(_scenario(reglages["scenario"])) * 100


def cumul_avenir(**reglages: str) -> float:
    """Cumul d'un système sur les années projetées, en Md€ constants."""
    return _cout_de(reglages).avenir.cumul(_scenario(reglages["scenario"])) / 1000


def ecart_avenir(**reglages: str) -> float:
    """Écart du cumul projeté d'un système à celui du système actuel, en %."""
    avenir = _cout_de(reglages).avenir
    return (avenir.cumul(_scenario(reglages["scenario"])) / avenir.cumul("actuel") - 1) * 100


def economie_pib(**reglages: str) -> float:
    """Ce qu'un système fait économiser une année, en points de PIB.

    La différence des parts de PIB du système actuel et du système désigné ;
    ``moins=5`` retranche l'économie d'un second système, pour dire de combien
    l'un économise plus que l'autre.
    """
    ligne = _avenir(reglages)
    economie = ligne.part_pib("actuel") - ligne.part_pib(_scenario(reglages["scenario"]))
    if "moins" in reglages:
        economie -= ligne.part_pib("actuel") - ligne.part_pib(_scenario(reglages["moins"]))
    return economie * 100


def emploi_projete(**_: str) -> float:
    """Ce que l'emploi projeté par le COR fait de 2026 à l'horizon, en %.

    La croissance de l'emploi composée année par année, sur la série que lisent
    la masse salariale et le PIB projetés.
    """
    cumul = 1.0
    for ligne in _csv("emploi_projete.csv"):
        cumul *= 1 + float(ligne["croissance_emploi"])
    return (cumul - 1) * 100


def dependance(**reglages: str) -> float:
    """Rapport de dépendance démographique d'une année : 65 ans et plus sur 20-64 ans."""
    return _avenir(reglages).dependance


def fusion(**reglages: str) -> float:
    """Un champ du régime unique qui naît à la bascule — ``champ=…``.

    Un taux (``taux_cotisation_retraite``, ``taux_cotisation_salarie``) se lit
    en %, le reste dans son unité : ``duree_requise`` en trimestres,
    ``age_ouverture`` en années.

    ``critere=le_plus_eleve`` (ou toute autre valeur de ``CritereTaux``)
    refait la fusion sous une autre règle de taux — la méthodologie dit
    pourquoi elle écarte le maximum, et il faut pouvoir dire ce qu'il vaut.
    ``pivot=regime_general`` rend plutôt, en %, ce que ce régime pivot apporte
    à la somme : la tranche 1, cotisation déplafonnée comprise, comme la
    fusion la compte.
    """
    from retraite_notionnelle.moteur.fusion import (CritereTaux, RegleFusion,
                                                    _taux_total, fusionner)

    simulateur = _simulateur(_parametres())
    fusionne = simulateur.regime_fusionne
    if "pivot" in reglages:
        actives = simulateur.catalogue[reglages["pivot"]].periodes_actives(
            fusionne.annee_bascule)
        if not actives:
            raise ValueError(f"« {reglages['pivot']} » n'a pas de période active")
        tranche_1 = min(actives, key=lambda p: p.bornes_assiette_en_pass()[0])
        return _taux_total(tranche_1) * 100
    if "critere" in reglages:
        fusionne = fusionner(simulateur.catalogue, fusionne.annee_bascule,
                             RegleFusion(critere_taux=CritereTaux(reglages["critere"])))
    champ = reglages["champ"]
    if not hasattr(fusionne, champ):
        raise ValueError(f"le régime unique n'a pas de champ « {champ} »")
    valeur = float(getattr(fusionne, champ))
    return valeur * 100 if champ.startswith("taux") else valeur


def parametre(**reglages: str) -> float:
    """Un paramètre par défaut du modèle : ``nom=taux_cotisation_liberal``.

    Un taux, une part, un frais ou une prime se lit en %, le reste dans son
    unité — ``annee_bascule``, ``age_reference`` ; un rang désigne l'élément
    d'un tuple, ``frais_gestion_paliers.3.1`` le taux du quatrième palier et
    ``.3.0`` son année. C'est le réglage que le site prend quand on ne lui dit
    rien, et celui que la prose décrit. Plusieurs noms joints par ``+``
    s'additionnent : « 18 + 5 = 23 % » est une somme de deux paramètres, et
    la prose l'écrit.
    """
    if "+" in reglages["nom"]:
        return sum(parametre(**{**reglages, "nom": nom})
                   for nom in reglages["nom"].split("+"))
    parametres = _parametres()
    nom, *rangs = reglages["nom"].split(".")
    if not hasattr(parametres, nom):
        raise ValueError(f"les paramètres n'ont pas de champ « {nom} »")
    objet = getattr(parametres, nom)
    # Un rang désigne l'élément d'un tuple : les paliers de frais sont des
    # couples (année, taux), et ``frais_gestion_paliers.3.1`` est le taux du
    # quatrième.
    for rang in rangs:
        objet = objet[int(rang)]
    valeur = float(objet)
    en_pour_cent = (nom.startswith(("taux", "part", "frais", "prime"))
                    and not (rangs and rangs[-1] == "0"))
    return (valeur * 100 if en_pour_cent else valeur) * float(reglages.get("echelle", 1))


def constante(**reglages: str) -> float:
    """Une constante du modèle : ``de=module&nom=CONSTANTE``, ``echelle=100`` au besoin.

    Pour les bornes que le code fixe et que la prose annonce — la fenêtre de
    lissage la plus longue, l'âge d'entrée de la carrière de référence. Le
    module se nomme depuis ``src/`` (``retraite_notionnelle.web.pages``) ou
    depuis ``scripts/`` (``construire_tableaux_md``).
    """
    import importlib

    sys.path.insert(0, str(RACINE / "scripts"))
    objet = importlib.import_module(reglages["de"])
    # Une constante de classe se nomme par son chemin : l'âge d'ouverture de
    # l'ASPA est ``MinimumVieillesse.AGE_OUVERTURE``.
    # un rang désigne l'élément d'un couple — le salaire d'ancrage est
    # ``ANCRAGE_SALAIRE_MOYEN.1``, l'année qui le porte ``.0`` —, et une clé
    # l'entrée d'une table : ``TRANCHES_CATEGORIE.Y_LT30``.
    for morceau in reglages["nom"].split("."):
        if morceau.isdigit() and isinstance(objet, tuple) and int(morceau) < len(objet):
            objet = objet[int(morceau)]
        elif isinstance(objet, dict) and morceau in objet:
            objet = objet[morceau]
        elif isinstance(objet, dict) and morceau in objet:
            # Une entrée de dictionnaire, comme l'âge de départ d'un exemple :
            # ``EXEMPLES.sncf.depart``.
            objet = objet[morceau]
        elif hasattr(objet, morceau):
            objet = getattr(objet, morceau)
        else:
            raise ValueError(f"{reglages['de']} n'a pas de « {reglages['nom']} »")
    return float(objet) * float(reglages.get("echelle", 1))


def poids_trimestre(**reglages: str) -> float:
    """Ce qu'un trimestre pèse dans une pension proratisée, en % : ``generation=1965``.

    L'inverse de la durée requise de la génération, lue dans sa table.
    """
    import csv

    chemin = RACINE / "data/reference/legislation/duree_assurance_requise.csv"
    with chemin.open(encoding="utf-8") as flux:
        lignes = [l for l in csv.DictReader(r for r in flux if not r.startswith("#"))
                  if l["generation"] == reglages["generation"]]
    if len(lignes) != 1:
        raise ValueError(f"la génération {reglages['generation']} a {len(lignes)} lignes")
    return 100 / float(lignes[0]["trimestres"])


def taux_indexation(**reglages: str) -> float:
    """Ce qu'une règle accorde une seule année, en % : ``regle=prix&annee=1981``.

    La méthodologie oppose, année par année, ce que le compte reçoit et ce que
    les prix prennent ; ``cumul_indexation`` ne disait que le produit.
    """
    annee = int(reglages["annee"])
    return (cumul_indexation(**{**reglages, "de": str(annee - 1), "a": str(annee)}) - 1) * 100


def anticipation(**reglages: str) -> float:
    """Ce que coûte un départ anticipé à capital donné, en % de la pension.

    ``avance`` (les années d'anticipation), ``annee``, et au besoin
    ``reference`` — l'âge dont on s'écarte, l'âge de référence par défaut, si
    bien que la prose suit ce paramètre quand il bouge : le seul allongement
    du diviseur. Avec
    ``carriere=42``, les années non cotisées s'y ajoutent au prorata — l'ordre
    de grandeur que la méthodologie donne, qui ignore que les dernières
    cotisations pèsent plus que les premières. ``quoi=esperance`` rend plutôt
    les années d'espérance de vie que l'anticipation ajoute au diviseur.
    """
    parametres = _parametres()
    convertisseur = _simulateur(parametres).convertisseur
    reference = float(reglages.get("reference", parametres.age_reference_fixe))
    age = reference - float(reglages["avance"])
    annee = int(reglages["annee"])
    if reglages.get("quoi") == "esperance":
        return (convertisseur.coefficient(age, annee).esperance_residuelle
                - convertisseur.coefficient(reference, annee).esperance_residuelle)
    garde = convertisseur.effet_anticipation(age, reference, annee)
    if "carriere" in reglages:
        duree = float(reglages["carriere"])
        garde *= (duree - (reference - age)) / duree
    return (1 - garde) * 100


def age_reference(**reglages: str) -> float:
    """L'âge de référence d'une liquidation de l'année ``annee``, en années.

    Avec ``depart=60``, l'anticipation qu'un départ à cet âge représente —
    la grandeur que la méthodologie illustre sur trois métiers.
    """
    age = _simulateur(_parametres()).age_reference.age(int(reglages["annee"]))
    return age - float(reglages["depart"]) if "depart" in reglages else age


@lru_cache(maxsize=None)
def _prospectif(conversion: str, generation: int, debut: int, depart: int):
    """Le scénario 3 d'un salarié du privé, sous une convention de conversion."""
    from retraite_notionnelle.config import AgeConversionDroitsAcquis

    parametres = _parametres()
    if conversion:
        parametres = replace(parametres,
                             age_conversion_droits_acquis=AgeConversionDroitsAcquis(conversion))
    simulateur = _simulateur(parametres)
    carriere = simulateur.carriere_simple(
        annee_naissance=generation, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=debut, age_liquidation=depart)
    return simulateur.simuler(carriere).notionnel_prospectif


def droits_acquis(**reglages: str) -> float:
    """Ce que deviennent les droits d'avant la bascule, dans le scénario 3.

    ``generation``, ``debut``, ``depart`` ; ``conversion=liquidation`` pour la
    variante. ``quoi`` : ``pot`` (le capital constitué à la bascule, en €),
    ``figee`` (la pension figée qu'il convertit, en € par an), ``pension`` (la
    pension du scénario, en € par an), ``capital`` (le capital total à la
    liquidation, en €), ``diviseur_conversion`` et ``diviseur_service`` (les
    deux diviseurs, en années), ``age_conversion``.
    """
    resultat = _prospectif(reglages.get("conversion", ""), int(reglages["generation"]),
                           int(reglages["debut"]), int(reglages["depart"]))
    acquis = resultat.droits_acquis
    valeurs = {
        "pot": lambda: acquis.capital_a_la_bascule,
        "figee": lambda: acquis.pension_figee,
        "pension": lambda: resultat.pension_annuelle,
        "capital": lambda: resultat.capital_notionnel,
        "diviseur_conversion": lambda: acquis.diviseur,
        "diviseur_service": lambda: resultat.conversion.diviseur,
        "age_conversion": lambda: acquis.age_conversion,
        # Ce que la conversion à l'âge de référence retire d'un droit ouvert
        # quand on part avant : le rapport des deux diviseurs, en %.
        "ecart_diviseurs": lambda: (resultat.conversion.diviseur / acquis.diviseur - 1) * 100,
    }
    quoi = reglages["quoi"]
    if quoi not in valeurs:
        raise ValueError(f"« {quoi} » n'est pas mesuré ; il y a {', '.join(valeurs)}")
    return valeurs[quoi]()


def droits_acquis_variation(**reglages: str) -> float:
    """Ce qu'une grandeur de ``droits_acquis`` gagne d'un âge de départ à l'autre, en %.

    Mêmes réglages, sauf ``depart`` : ``de=60&a=67``. C'est le « 28 %
    d'écart pour un passé identique » et le gain en capital de sept années de
    travail, que la méthodologie oppose d'une convention à l'autre.
    """
    communs = {c: v for c, v in reglages.items() if c not in ("de", "a")}
    depart = droits_acquis(**communs, depart=reglages["de"])
    arrivee = droits_acquis(**communs, depart=reglages["a"])
    return (arrivee / depart - 1) * 100


def approximation_revalorisation(**reglages: str) -> float:
    """Ce que l'ancienne approximation — « les salaires jusqu'en 1986, les prix
    depuis » — ajoute aux coefficients des arrêtés, de ``de`` à ``a``, en %.

    Elle reste le repli du moteur hors des colonnes publiées : ce qu'elle
    coûte n'est donc pas de l'histoire.
    """
    macro = _simulateur(_parametres()).macro
    de, a = int(reglages["de"]), int(reglages["a"])
    return (macro.coefficient_revalorisation_salaires(de, a)
            / macro.coefficient_revalorisation_portee_au_compte(de, a) - 1) * 100


def ecart_colonnes(**reglages: str) -> float:
    """Le plus petit écart entre deux colonnes publiées de revalorisation, en %.

    ``de=2022-01-01&a=2022-07-01`` : deux circulaires de la même année, sur
    toutes les années de perception qu'elles portent l'une et l'autre.
    """
    import csv

    chemin = RACINE / "data/reference/legislation/revalorisation_salaires.csv"
    colonnes: dict[str, dict[str, float]] = {}
    with chemin.open(encoding="utf-8") as flux:
        for ligne in csv.DictReader(r for r in flux if not r.startswith("#")):
            colonnes.setdefault(ligne["date_effet"], {})[ligne["annee_perception"]] = float(
                ligne["coefficient"])
    de, a = colonnes[reglages["de"]], colonnes[reglages["a"]]
    return (min(a[annee] / de[annee] for annee in de if annee in a) - 1) * 100


def derive_revalorisation(**reglages: str) -> float:
    """Ce que coûte de reconstruire une colonne de revalorisation depuis une autre, en %.

    L'écart relatif entre la colonne publiée de l'année ``annee`` et celle
    qu'on en reconstruit, par rapport de deux valeurs, depuis ``ancre`` : une
    année, ``recente`` (la dernière colonne publiée) ou ``voisine`` (la
    suivante, la seule qui porte l'année reconstruite parmi ses perceptions).
    ``stat=mediane`` (défaut), ``moyenne`` ou ``max`` sur les années de
    perception — la médiane et le maximum sont ce que le récupérateur des
    circulaires tabule ; sans ``annee``, le pire de toutes les colonnes. Ce
    sont les colonnes de janvier, comme dans
    ``test_la_reconstruction_entre_colonnes_reste_dans_sa_derive``.
    """
    import csv
    from statistics import median

    chemin = RACINE / "data/reference/legislation/revalorisation_salaires.csv"
    tables: dict[int, dict[int, float]] = {}
    with chemin.open(encoding="utf-8") as flux:
        for ligne in csv.DictReader(r for r in flux if not r.startswith("#")):
            if ligne["date_effet"].endswith("-01-01"):
                tables.setdefault(int(ligne["date_effet"][:4]), {})[
                    int(ligne["annee_perception"])] = float(ligne["coefficient"])

    def derive(annee: int) -> float:
        ancre = reglages.get("ancre", "voisine")
        if ancre == "voisine":
            suivantes = [a for a in tables if a > annee and annee in tables[a]]
            if not suivantes:
                raise ValueError(f"aucune colonne après {annee} ne porte cette année")
            ancre = min(suivantes)
        else:
            ancre = max(tables) if ancre == "recente" else int(ancre)
        if ancre == annee or annee not in tables.get(ancre, {}):
            raise ValueError(f"la colonne {ancre} ne reconstruit pas {annee}")
        diviseur = tables[ancre][annee]
        ecarts = [abs(tables[ancre][perception] / diviseur - publie) / publie
                  for perception, publie in tables[annee].items()
                  if perception < annee and perception in tables[ancre]]
        stat = reglages.get("stat", "mediane")
        if stat == "max":
            return max(ecarts) * 100
        if stat == "moyenne":
            return sum(ecarts) / len(ecarts) * 100
        if stat == "mediane":
            return median(ecarts) * 100
        raise ValueError(f"stat inconnue « {stat} »")

    if "annee" in reglages:
        return derive(int(reglages["annee"]))
    return max(derive(annee) for annee in tables if annee < max(tables))


def taux_statut(**reglages: str) -> float:
    """Ce que prélèvent ensemble des régimes une année, en % : ``regimes=a|b&annee=2023``.

    Tranche 1 de chacun, cotisation déplafonnée comprise — la grandeur que la
    fusion additionne pour son statut pivot, mais à l'année qu'on désigne.
    """
    from retraite_notionnelle.moteur.fusion import _taux_total

    catalogue = _simulateur(_parametres()).catalogue
    annee, total = int(reglages["annee"]), 0.0
    for code in reglages["regimes"].split("|"):
        actives = catalogue[code].periodes_actives(annee)
        if not actives:
            raise ValueError(f"« {code} » n'a pas de période active en {annee}")
        total += _taux_total(min(actives, key=lambda p: p.bornes_assiette_en_pass()[0]))
    return total * 100


@lru_cache(maxsize=None)
def _mortalite_population(population: str, cas: str, generation: int):
    import mortalite_population
    from retraite_notionnelle.castypes import CAS_TYPES

    cas_type = next((c for c in CAS_TYPES if c.code == cas), None)
    if cas_type is None:
        raise ValueError(f"cas type inconnu « {cas} »")
    if population == "vingtile":
        mortalite = mortalite_population._simulateur(None).mortalite
        population = mortalite.population_niveau_de_vie(cas_type.niveau_salaire)
    resultat = mortalite_population.mesurer(population, cas_type, generation)
    if resultat is None or "erreur" in resultat:
        raise ValueError(f"{cas} ne se mesure pas : {resultat}")
    return resultat


def mortalite_population(**reglages: str) -> float:
    """Ce que change une table de mortalité propre à une population, à capital égal.

    ``population`` (``fonctionnaires_civils_etat``, ou ``vingtile`` pour celui
    où le salaire du cas type le place), ``cas`` (code d'un cas type),
    ``generation``. ``quoi`` : ``annees`` (années de rente en plus, en moins
    si négatif), ``ecart`` (écart de pension du scénario ``scenario``, 4 par
    défaut, en %), ``transfert`` (sur la vie, en euros constants, scénario 1
    par défaut). ``abs=1`` rend la valeur sans son signe. C'est
    ``scripts/mortalite_population.py``, cellule par cellule.
    """
    resultat = _mortalite_population(reglages["population"], reglages["cas"],
                                     int(reglages["generation"]))
    quoi = reglages["quoi"]
    defaut = "4" if quoi == "ecart" else "1"
    ligne = next(l for l in resultat["scenarios"]
                 if l["numero"] == int(reglages.get("scenario", defaut)))
    valeurs = {
        "annees": lambda: resultat["esperance_population"] - resultat["esperance_commune"],
        "ecart": lambda: ligne["ecart"] * 100,
        "transfert": lambda: ligne["transfert_vie"],
    }
    if quoi not in valeurs:
        raise ValueError(f"« {quoi} » n'est pas mesuré ; il y a {', '.join(valeurs)}")
    # La prose dit le sens en mots — « 3,0 ans de MOINS », « retirés » — et
    # le nombre sans signe : ``abs=1`` le lui rend ainsi.
    valeur = valeurs[quoi]()
    return abs(valeur) if reglages.get("abs") else valeur


def table_mortalite(**reglages: str) -> float:
    """Ce que change le choix de la table, à ``age`` et à la date ``annee``.

    ``quoi=moment`` : les années d'espérance de vie qu'une table du moment
    retire à la table de génération ; ``quoi=sexe`` : ce qu'une table sexuée
    retirerait à la pension d'une femme face à la table unisexe, en %.
    Population générale dans les deux cas.
    """
    mortalite = _simulateur(_parametres()).mortalite
    age, annee = float(reglages["age"]), float(reglages["annee"])
    generation = mortalite.esperance_residuelle(age, annee, None, True)
    if reglages["quoi"] == "moment":
        return generation - mortalite.esperance_residuelle(age, annee, None, False)
    if reglages["quoi"] == "sexe":
        return (1 - generation / mortalite.esperance_residuelle(age, annee, "F", True)) * 100
    raise ValueError(f"« {reglages['quoi']} » n'est pas mesuré ; il y a moment, sexe")


def part_pensions_sous(**reglages: str) -> float:
    """La part des retraités dont la pension brute mensuelle est sous ``borne``, en %.

    ``annee`` : le millésime de la distribution de la DREES
    (``macro/distribution_pensions.csv``), tous sexes.
    """
    import csv

    chemin = RACINE / "data/reference/macro/distribution_pensions.csv"
    with chemin.open(encoding="utf-8") as flux:
        lignes = [l for l in csv.DictReader(r for r in flux if not r.startswith("#"))
                  if l["annee"] == reglages["annee"] and l["sexe"] == "ensemble"]
    if not lignes:
        raise ValueError(f"pas de distribution pour {reglages['annee']}")
    return sum(float(l["part_pct"]) for l in lignes
               if float(l["borne_mensuelle"]) < float(reglages["borne"]))


def fiche_regime(**reglages: str) -> float:
    """Un champ des périodes d'une fiche de régime, telle qu'elle est écrite.

    ``fichier=base_prive&regime=regime_general&champ=part_salariale`` ;
    ``de`` et ``a`` bornent l'année de DÉBUT des périodes retenues (``a``
    vaut ``de`` si on l'omet), tout autre réglage filtre sur un champ de la
    période (``assiette=tranche_b``). ``stat=min`` ou ``stat=max`` quand
    plusieurs périodes répondent, sinon elles doivent toutes s'accorder.
    Un champ dont le nom commence par ``part`` ou ``taux`` se lit en %.

    La fiche ÉCRITE, et non le catalogue chargé : le régime général y reçoit
    ses taux année par année, et la méthodologie dit précisément ce que les
    fiches portent avant ce découpage.
    """
    from retraite_notionnelle.donnees.chargement import charger_yaml

    speciaux = {"fichier", "regime", "champ", "de", "a", "stat"}
    donnees = charger_yaml(RACINE / "data/reference/regimes" / f"{reglages['fichier']}.yaml")
    regime = next((r for r in donnees["regimes"] if r["code"] == reglages["regime"]), None)
    if regime is None:
        raise ValueError(f"{reglages['fichier']} n'a pas de régime « {reglages['regime']} »")
    de = int(reglages.get("de", 0))
    a = int(reglages.get("a", reglages.get("de", 9999)))
    filtres = {c: v for c, v in reglages.items() if c not in speciaux}
    champ = reglages["champ"]
    valeurs = [float(p[champ]) for p in regime["periodes"]
               if de <= int(p["debut"]) <= a and p.get(champ) is not None
               and all(str(p.get(c)) == v for c, v in filtres.items())]
    if not valeurs:
        raise ValueError(f"aucune période de {reglages['regime']} ne répond")
    stat = reglages.get("stat")
    if stat == "min":
        valeur = min(valeurs)
    elif stat == "max":
        valeur = max(valeurs)
    elif len(set(valeurs)) == 1:
        valeur = valeurs[0]
    else:
        raise ValueError(f"{len(set(valeurs))} valeurs différentes ; préciser stat=min ou max")
    return valeur * 100 if champ.startswith(("part", "taux")) else valeur


@lru_cache(maxsize=None)
def _sous_projection(projection: str, generation: int, debut: int, depart: int):
    """La carrière de référence, sous un scénario de projection du COR."""
    parametres = replace(_parametres(), scenario_projection=projection)
    simulateur = _simulateur(parametres)
    carriere = simulateur.carriere_simple(
        annee_naissance=generation, sexe=CARRIERE["sexe"],
        affiliation=CARRIERE["affiliation"], age_debut=debut, age_liquidation=depart)
    return simulateur.simuler(carriere)


def fourchette(**reglages: str) -> float:
    """Le bloc « Ce que l'hypothèse pèse » du site, sur la carrière de référence.

    ``generation``, ``depart`` et au besoin ``debut``. ``quoi`` : ``basse`` et ``haute`` (la
    pension mensuelle du scénario 2 sous les deux variantes de productivité,
    en euros constants), ``amplitude`` (leur écart, en %), ``projetees`` et
    ``annees`` (les années du compte après la dernière observation, et en
    tout), ``part`` (la part projetée du calcul, en %).
    """
    generation, depart = int(reglages["generation"]), int(reglages["depart"])
    debut = int(reglages.get("debut", CARRIERE["debut"]))
    quoi = reglages["quoi"]

    def mensuelle(projection: str) -> float:
        comparaison = _sous_projection(projection, generation, debut, depart)
        return comparaison.en_euros_constants(
            comparaison.notionnel_retroactif.pension_annuelle) / 12

    if quoi in ("basse", "haute"):
        return mensuelle(f"cor_productivite_{quoi}")
    if quoi == "amplitude":
        return (mensuelle("cor_productivite_haute") / mensuelle("cor_productivite_basse") - 1) * 100
    comparaison = _sous_projection("cor_reference", generation, debut, depart)
    carriere = comparaison.carriere
    derniere = _simulateur(_parametres()).macro.derniere_annee_observee
    premiere = min(carriere.annees_cotisees, default=carriere.annee_liquidation)
    annees = carriere.annee_liquidation - premiere + 1
    projetees = max(0, carriere.annee_liquidation - max(premiere - 1, derniere))
    valeurs = {"annees": annees, "projetees": projetees, "part": projetees / annees * 100}
    if quoi not in valeurs:
        raise ValueError(f"« {quoi} » n'est pas mesuré")
    return valeurs[quoi]


def composition_revalorisation(**reglages: str) -> float:
    """Ce que composer année par année les coefficients des arrêtés fait
    perdre, en % et en valeur absolue, face au coefficient lu d'un bloc.

    ``de`` et ``a`` : 1940 et 2025 pour la méthodologie. La caisse arrondit
    ses colonnes au millième ; le moteur, qui compose tous ses modes de la
    même façon, en hérite un écart que la prose chiffre.
    """
    de, a = reglages["de"], reglages["a"]
    compose = cumul_indexation(regle="revalorisation_portee_au_compte", de=de, a=a)
    lu = _simulateur(_parametres()).macro.coefficient_revalorisation_portee_au_compte(
        int(de), int(a))
    return abs(compose / lu - 1) * 100


def millieme_salaire(**_: str) -> float:
    """Un millième du salaire moyen, en euros par mois, l'année du modèle.

    Le pas auquel le site écrit un multiple : c'est lui qui borne ce qu'un
    aller-retour entre euros et multiple peut déplacer.
    """
    from retraite_notionnelle.carriere import salaire_moyen_annuel

    parametres = _parametres()
    macro = _simulateur(parametres).macro
    return salaire_moyen_annuel(macro, parametres.annee_courante) / 12 / 1000


@lru_cache(maxsize=None)
def _depenses():
    from retraite_notionnelle.donnees.depenses import DepensesRetraite

    return DepensesRetraite(_parametres().racine_donnees)


def depense(**reglages: str) -> float:
    """La dépense OBSERVÉE d'une année, en Md€ courants — la DREES, pas le modèle.

    ``quoi=totale`` (défaut), ``repartition`` pour la seule répartition
    obligatoire, ``hors_repartition`` pour le reste — capitalisation,
    dépendance, minimum vieillesse —, ``part_pib`` pour la totale en % du PIB,
    ``part_pib_repartition`` pour la seule répartition, et ``ecart_cor`` pour
    ce qui sépare de celle-ci le compte du COR, en points de PIB.
    """
    from retraite_notionnelle.donnees.depenses import SYSTEMES

    depenses, annee = _depenses(), int(reglages["annee"])
    quoi = reglages.get("quoi", "totale")
    if quoi == "totale":
        return depenses.depense(annee) / 1000
    if quoi == "part_pib":
        return depenses.part_pib(annee) * 100
    if quoi in ("part_pib_repartition", "ecart_cor"):
        repartition = sum(depenses.depense_systeme(s.code, annee) for s in SYSTEMES
                          if s.repartition) / depenses.pib(annee) * 100
        if quoi == "part_pib_repartition":
            return repartition
        cor = next(float(l["part_pib"]) for l in _csv("comptes_retraite.csv")
                   if l["annee"] == str(annee) and l["poste"] == "depenses")
        return cor * 100 - repartition
    if quoi in ("repartition", "hors_repartition"):
        voulu = quoi == "repartition"
        return sum(depenses.depense_systeme(s.code, annee) for s in SYSTEMES
                   if s.repartition == voulu) / 1000
    raise ValueError(f"quoi inconnu « {quoi} »")


def rapport_depenses(**reglages: str) -> float:
    """La dépense observée d'une année rapportée à celle d'une autre, en euros courants, en %."""
    depenses = _depenses()
    return depenses.depense(int(reglages["de"])) / depenses.depense(int(reglages["a"])) * 100


def prelevement_pension(**_: str) -> float:
    """CSG au taux plein, CRDS et CASA sur une pension, en % : ce que le site retient."""
    import yaml

    chemin = RACINE / "data" / "reference" / "legislation" / "prelevements_remuneration.yaml"
    pensions = yaml.safe_load(chemin.read_text(encoding="utf-8"))["pensions"]
    return (pensions["csg_taux_plein"] + pensions["crds"] + pensions["casa"]) * 100


def surcout_passe(**reglages: str) -> float:
    """De combien le cumul observé d'un système dépasse celui d'un autre, en %.

    ``scenario`` et ``base`` : « le scénario 4 coûte 132 % de plus que le 2 ».
    """
    cout = _cout_de(reglages)
    return (cout.cumul(_scenario(reglages["scenario"]))
            / cout.cumul(_scenario(reglages["base"])) - 1) * 100


def poids(**reglages: str) -> float:
    """Ce que pèsent un ou plusieurs cas types dans les masses, en %.

    ``cas=cadre|artisan`` additionne ; la dernière année observée, celle que
    la page Coût affiche. ``ponderation=egale`` rend l'ancienne convention.
    """
    cout = _cout_de(reglages)
    codes = reglages["cas"].split("|")
    inconnus = [c for c in codes if c not in cout.poids]
    if inconnus:
        raise ValueError(f"cas types inconnus : {', '.join(inconnus)}")
    return sum(cout.poids[c] for c in codes) * 100


def grille(**reglages: str) -> float:
    """La taille des grilles : ``quoi=cas_types``, ``generations`` (celles de la
    page Coût) ou ``generations_cas_types`` (celles de la page Cas types)."""
    from retraite_notionnelle import cout as C
    from retraite_notionnelle.castypes import CAS_TYPES

    quoi = reglages["quoi"]
    if quoi == "cas_types":
        return len(CAS_TYPES)
    if quoi == "generations_cas_types":
        from retraite_notionnelle.castypes import GENERATIONS

        return len(GENERATIONS)
    if quoi == "generations":
        return len(C.generations())
    raise ValueError(f"quoi inconnu « {quoi} »")


def garantie(**reglages: str) -> float:
    """La garantie vieillesse d'une année de la trajectoire : ``quoi=facteur``.

    Le facteur par lequel la distribution des pensions est déplacée ; ou
    ``beneficiaires`` et ``ayants_droit``, en millions.
    """
    ligne = _avenir(reglages)
    if ligne.garantie is None:
        raise ValueError(f"pas de garantie en {reglages['annee']}")
    quoi = reglages["quoi"]
    if quoi == "facteur":
        return ligne.garantie.facteur
    if quoi in ("beneficiaires", "ayants_droit"):
        return getattr(ligne.garantie, quoi) / 1e6
    raise ValueError(f"quoi inconnu « {quoi} »")


@lru_cache(maxsize=None)
def _avantages():
    """Ce que les avantages non contributifs coûtent — celui de la page Avantages."""
    from retraite_notionnelle.avantages import calculer_avantages
    from retraite_notionnelle.donnees.population import Population

    parametres = _parametres()
    return calculer_avantages(_simulateur(parametres), _depenses(),
                              Population(parametres.racine_donnees))


def avantages(**reglages: str) -> float:
    """Le coût des avantages non contributifs d'une année, en Md€ courants.

    ``quoi=total`` (défaut), ``lues`` pour les lignes qu'un producteur publie,
    ``calculees`` pour les autres, ``part_lue`` pour la part des premières
    dans le total, en %, ``part_depense`` pour le total en % de la dépense
    observée ; ``quoi=ligne&cle=…`` une ligne, ``quoi=anticipees`` les
    pensions servies avant l'âge légal, ``&motif=…`` pour l'un des trois. ``annee`` : la dernière année de la série si on l'omet.
    """
    from retraite_notionnelle.avantages import LIGNES_LUES

    cout = _avantages()
    if "annee" in reglages:
        ligne = next((l for l in cout.annees if l.annee == int(reglages["annee"])), None)
        if ligne is None:
            raise ValueError(f"l'année {reglages['annee']} n'est pas dans la série")
    else:
        ligne = cout.derniere
    lues = sum(v for k, v in ligne.lignes.items() if k in LIGNES_LUES)
    quoi = reglages.get("quoi", "total")
    if quoi == "ligne":
        if reglages["cle"] not in ligne.lignes:
            raise ValueError(f"« {reglages['cle']} » n'est pas une ligne chiffrée")
        return ligne.lignes[reglages["cle"]] / 1000
    if quoi == "anticipees":
        motif = reglages.get("motif")
        return (ligne.anticipees[motif] if motif else ligne.anticipee) / 1000
    valeurs = {"total": ligne.gratuit / 1000, "lues": lues / 1000,
               "calculees": (ligne.gratuit - lues) / 1000,
               "part_lue": lues / ligne.gratuit * 100,
               "part_depense": ligne.gratuit / ligne.observee * 100}
    if quoi not in valeurs:
        raise ValueError(f"quoi inconnu « {quoi} »")
    return valeurs[quoi]


def _solde_annee(reglages: dict[str, str]):
    solde = _cout_de(reglages).solde
    annee = int(reglages["annee"]) if "annee" in reglages else solde.derniere_annee
    ligne = solde.annee(annee)
    if ligne is None:
        raise ValueError(f"l'année {annee} n'est pas dans le bilan")
    return ligne


def solde(**reglages: str) -> float:
    """Solde d'un système une année, en % du PIB ; ``en=milliards`` en Md€ courants."""
    ligne = _solde_annee(reglages)
    scenario = _scenario(reglages["scenario"])
    if reglages.get("en") == "milliards":
        return ligne.solde_meur(scenario) / 1000
    return ligne.solde(scenario) * 100


def solde_moyen(**reglages: str) -> float:
    """Solde moyen d'un système sur les années projetées, en % du PIB.

    La fenêtre de la page Coût : de la première année projetée à l'horizon.
    """
    solde = _cout_de(reglages).solde
    return solde.solde_moyen(_scenario(reglages["scenario"]),
                             solde.premiere_annee_projetee, solde.derniere_annee) * 100


def coefficient(**reglages: str) -> float:
    """Coefficient d'équilibre d'un système une année — l'horizon si on l'omet.

    ``quoi=minimum`` rend le plus bas des années projetées, ``quoi=annee_minimum``
    l'année où il est atteint, ``quoi=economie`` ce qu'on lirait à tort comme
    une économie, ``1 − 1/c``, en %.
    """
    scenario = _scenario(reglages["scenario"])
    quoi = reglages.get("quoi", "valeur")
    if quoi in ("minimum", "annee_minimum"):
        lignes = _cout_de(reglages).solde.projetees()
        plus_bas = min(lignes, key=lambda l: l.coefficient(scenario))
        return plus_bas.coefficient(scenario) if quoi == "minimum" else plus_bas.annee
    valeur = _solde_annee(reglages).coefficient(scenario)
    if quoi == "economie":
        return (1 - 1 / valeur) * 100
    return valeur


def annees_equilibrees(**reglages: str) -> float:
    """Combien d'années projetées un système finit à l'équilibre ou en excédent."""
    scenario = _scenario(reglages["scenario"])
    return sum(1 for l in _cout_de(reglages).solde.projetees() if l.solde(scenario) >= 0)


def dette(**reglages: str) -> float:
    """Le stock que les soldes accumulent, en % du PIB, une année — l'horizon si on l'omet."""
    dette = _cout_de(reglages).dette
    annee = int(reglages.get("annee", dette.derniere_annee))
    return dette.stock(_scenario(reglages["scenario"]), annee) * 100


def recette(**reglages: str) -> float:
    """Ce qui entre dans le compte du système actuel une année, en % du PIB.

    ``quoi=retrait`` : ce que les scénarios notionnels ne peuvent pas compter
    — les versements de la CNAF, de l'Unédic et du FSV ; ``payeurs=famille|chomage``
    n'en garde que ceux-là, et ``sur=ressources`` le rapporte aux ressources
    de l'année plutôt qu'au PIB. ``quoi=impots`` : les impôts et taxes
    affectés ; ``quoi=taux_prelevement`` : ce que le système prélève sur
    l'assiette des revenus d'activité, en %.
    """
    ligne = _solde_annee(reglages)
    quoi = reglages["quoi"]
    if quoi == "retrait":
        retrait = ligne.retrait
        if "payeurs" in reglages:
            payeurs = reglages["payeurs"].split("|")
            inconnus = [p for p in payeurs if p not in ligne.retraits]
            if inconnus:
                raise ValueError(f"payeurs inconnus : {', '.join(inconnus)} ; "
                                 f"il y a {', '.join(ligne.retraits)}")
            retrait = sum(ligne.retraits[p] for p in payeurs)
        if reglages.get("sur") == "ressources":
            return retrait / ligne.ressources * 100
        return retrait * 100
    if quoi == "impots":
        return ligne.ressources * ligne.part_impots * 100
    if quoi == "impots_milliards":
        # Le bilan met le PIB à zéro hors de la fenêtre publiée, à dessein : les
        # euros d'une année projetée se lisent au PIB PROJETÉ de la trajectoire.
        pib = _cout_de(reglages).avenir.annee(ligne.annee).pib
        return ligne.ressources * ligne.part_impots * pib / 1000
    if quoi == "taux_prelevement":
        return ligne.taux_prelevement * 100
    raise ValueError(f"quoi inconnu « {quoi} »")


def _csv(nom: str) -> list[dict]:
    import csv

    chemin = RACINE / "data" / "reference" / "macro" / nom
    with chemin.open(encoding="utf-8") as fichier:
        return list(csv.DictReader(l for l in fichier if not l.startswith("#")))


def somme_postes(**reglages: str) -> float:
    """La somme de postes d'une série macro une année : ``serie=…&postes=a|b``.

    ``structure_ressources_retraite.csv`` rend une part des ressources, en % ;
    ``transferts_retraite.csv``, ``assiette_activite.csv`` et
    ``impots_retraite_remuneration.csv`` un montant, en Md€.
    """
    serie, annee = reglages["serie"], reglages["annee"]
    postes = set(reglages["postes"].split("|"))
    lignes = [l for l in _csv(serie) if l["annee"] == annee and l["poste"] in postes]
    trouves = {l["poste"] for l in lignes}
    if trouves != postes:
        raise ValueError(f"{serie} n'a pas {', '.join(sorted(postes - trouves))} en {annee}")
    if "part" in lignes[0]:
        return sum(float(l["part"]) for l in lignes) * 100
    return sum(float(l["montant_meur"]) for l in lignes) / 1000


def restitution(**reglages: str) -> float:
    """Le partage de ce que la proposition n'encaisse plus, une année.

    ``quoi=part_du_poste`` : la part des impôts affectés qui est assise sur une
    rémunération, en % ; ``quoi=points_csg`` : les points de CSG d'activité
    rendus.
    """
    from retraite_notionnelle.restitution import Restitution

    parametres = _parametres()
    partage = Restitution(parametres.racine_donnees, parametres.part_rendue_aux_salaires)
    annee = int(reglages["annee"])
    quoi = reglages["quoi"]
    if quoi == "part_du_poste":
        return partage.part_du_poste(annee) * 100
    if quoi == "points_csg":
        return partage.annuelle(annee).points_csg * 100
    raise ValueError(f"quoi inconnu « {quoi} »")


def gain_net(**reglages: str) -> float:
    """Ce que la proposition ajoute au revenu net d'un actif, en %, sur une carrière.

    L'année de référence de la fiche de paie — la première année pleine sous
    le nouveau système. Mêmes réglages que ``ecart`` ; ``en=mensuel`` rend le
    gain en euros par mois plutôt qu'en pour-cent du net.
    """
    reference = _comparaison_de(reglages).remuneration.reference
    if reglages.get("en") == "mensuel":
        return reference.gain_net / 12
    return reference.gain_net / reference.droit_en_vigueur.net * 100


def fiche(**reglages: str) -> float:
    """Les cotisations retraite de la fiche de paie, en points du brut.

    L'année de référence ; ``quoi=salarie``, ``employeur`` ou ``total``,
    ``systeme=actuel`` (défaut) ou ``proposition``. Mêmes réglages que ``ecart``.
    """
    reference = _comparaison_de(reglages).remuneration.reference
    fiche = (reference.proposition if reglages.get("systeme") == "proposition"
             else reference.droit_en_vigueur)
    quoi = reglages["quoi"]
    montants = {"salarie": fiche.retraite_salarie, "employeur": fiche.retraite_employeur,
                "total": fiche.retraite_salarie + fiche.retraite_employeur}
    if quoi not in montants:
        raise ValueError(f"quoi inconnu « {quoi} »")
    return montants[quoi] / fiche.brut * 100


def avance(**reglages: str) -> float:
    """Les années d'anticipation d'un départ sur l'âge de référence, sur une carrière."""
    ecart = _comparaison_de(reglages).notionnel_retroactif.ecart_age
    return ecart.age_reference - ecart.age_liquidation


def profils_oracle(**_: str) -> float:
    """Le nombre de profils rejoués par OpenFisca-France-Pension, toutes familles."""
    import json

    return sum(len(json.loads(chemin.read_text(encoding="utf-8"))["profils"])
               for chemin in (RACINE / "tests" / "temoins").glob("openfisca_*.json"))


def ecart_openfisca(**reglages: str) -> float:
    """L'écart du salaire annuel moyen au régime général d'OpenFisca, en %.

    Les dix profils de ``tests/temoins/openfisca_regime_general.json``, rejoués
    comme ``tests/test_oracle.py`` les rejoue ; ``stat=max`` (défaut) ou
    ``min`` de l'écart relatif, OpenFisca au-dessus.
    """
    import json

    from retraite_notionnelle.carriere import AnneeCarriere, Carriere

    simulateur = _simulateur(_parametres())
    scenario = simulateur.scenario_actuel
    temoin = json.loads((RACINE / "tests" / "temoins" / "openfisca_regime_general.json")
                        .read_text(encoding="utf-8"))
    ecarts = []
    for entree in temoin["profils"].values():
        profil = entree["profil"]
        carriere = Carriere(
            annee_naissance=profil["naissance"], sexe="H",
            lignes=[AnneeCarriere(annee=annee, revenu=profil["salaire"],
                                  affiliation="salarie_prive_non_cadre",
                                  trimestres_valides=4)
                    for annee in range(profil["debut"], profil["liquidation"])],
            age_liquidation=float(profil["liquidation"] - profil["naissance"]),
            identifiant=profil["code"])
        periode = simulateur.catalogue["regime_general"].periode(profil["liquidation"])
        nous = scenario.salaire_de_reference(
            "regime_general", carriere, periode, profil["liquidation"],
            True, profil["naissance"], True)
        ecarts.append(entree["openfisca"]["salaire_de_reference"] / nous - 1)
    return (min(ecarts) if reglages.get("stat") == "min" else max(ecarts)) * 100


def garantie_complement(**reglages: str) -> float:
    """Ce que la garantie vieillesse sert, par mois, à qui a ``pension=…`` euros."""
    return max(0.0, _parametres().garantie_vieillesse_mensuelle - float(reglages["pension"]))


@lru_cache(maxsize=None)
def _garantie_mensuelle(pension: float, situation: str):
    """La garantie que le moteur sert à une pension mensuelle, dans une situation.

    Sur une liquidation de l'année des euros de la garantie, à soixante-six
    ans : ni prix à déflater, ni ouverture à attendre — la carrière de
    ``test_la_garantie_reproduit_le_tableau_de_la_proposition``.
    """
    from retraite_notionnelle.config import SituationFoyer

    parametres = replace(_parametres(), situation_foyer=SituationFoyer(situation))
    simulateur = _simulateur(parametres)
    carriere = simulateur.carriere_simple(
        annee_naissance=parametres.annee_euros_garantie_vieillesse - 66, sexe="H",
        affiliation="salarie_prive_non_cadre", age_debut=20, age_liquidation=66)
    return simulateur.scenario_liberal._garantie_vieillesse(carriere, pension * 12.0)


def garantie_foyer(**reglages: str) -> float:
    """Ce que la garantie sert à un foyer, par mois, en euros : ``pension=300&conjoint=1500``.

    Sans ``conjoint``, une personne seule ; avec, un couple, où chacun est
    comparé à son propre plancher — la règle du moteur, ``_garantie_vieillesse``.
    ``base=foyer`` compare plutôt les ressources du couple à la somme des deux
    planchers : la même garantie si elle regardait le ménage comme l'ASPA,
    c'est-à-dire ce que l'individualisation change à montants égaux.
    ``quoi=plancher`` rend le plancher du foyer, ``personnes=1`` ou ``2``
    tenant lieu de pensions. Pas de liste « a|b » : ces ancres vivent dans
    des tableaux, où le trait vertical couperait la cellule.
    """
    if "pension" in reglages:
        pensions = [float(reglages["pension"])]
        if "conjoint" in reglages:
            pensions.append(float(reglages["conjoint"]))
    else:
        pensions = [0.0] * int(reglages["personnes"])
    if len(pensions) not in (1, 2):
        raise ValueError("un foyer compte une ou deux personnes")
    situation = "seul" if len(pensions) == 1 else "couple"
    garanties = [_garantie_mensuelle(p, situation) for p in pensions]
    plancher = sum(g.plancher_annuel for g in garanties) / 12
    if reglages.get("quoi") == "plancher":
        return plancher
    if reglages.get("base") == "foyer":
        return max(0.0, plancher - sum(pensions))
    return sum(g.complement for g in garanties) / 12


def frais_reserve(**reglages: str) -> float:
    """Ce qu'un frais annuel sur la réserve de la rente lui retire, en % de rente.

    ``age`` et ``annee`` de la liquidation ; ``frais``, en fraction, vaut par
    défaut celui des paramètres, le marché de 2025. Sur la courbe de survie
    du modèle, population générale : ``_facteur_encours_rente``.
    """
    parametres = _parametres()
    frais = float(reglages.get("frais", parametres.frais_encours_rente_capitalisation))
    facteur = _simulateur(parametres).constructeur_capitalisation._facteur_encours_rente(
        frais, float(reglages["age"]), int(reglages["annee"]), None, None)
    return (1 - facteur) * 100


def _echelle_glissante(horizon: int) -> tuple[tuple[int, float], ...]:
    """L'échelle 2/10/30 que le pilier pratiquait jusqu'en septembre 2026.

    Reconstituée comme les deux tests de ``test_capitalisation.py`` la
    reconstituent, pour ne pas avoir à la garder dans le moteur.
    """
    if horizon <= 0:
        return ()
    borner = lambda v: min(1.0, max(0.0, v))  # noqa: E731
    longue = 0.75 * borner((horizon - 10) / 20)
    courte = 0.75 * borner((10 - horizon) / 8)
    cumul: dict[int, float] = {}
    for maturite, part in zip((2, 10, 30), (courte, 1.0 - courte - longue, longue)):
        if part > 0:
            effective = min(maturite, horizon)
            cumul[effective] = cumul.get(effective, 0.0) + part
    return tuple(sorted(cumul.items()))


def _roulement(horizon: int) -> tuple[tuple[int, float], ...]:
    """Un placement à un an, renouvelé jusqu'au départ."""
    return ((1, 1.0),) if horizon > 0 else ()


@lru_cache(maxsize=None)
def _pilier_alloue(regle: str, prime: float):
    """Le pilier de la carrière témoin, sous une règle d'allocation et une prime.

    La carrière de ``test_avec_une_prime_de_terme_l_adossement_domine`` : une
    assiette de 30 000 € par an à partir de 2030, née en 1996, partie à
    64 ans en 2060. La règle s'échange le temps du calcul, comme le test
    l'échange : le moteur n'en porte qu'une, l'adossement.
    """
    from retraite_notionnelle.donnees.taux import CourbeTauxSansRisque
    from retraite_notionnelle.moteur import capitalisation as module
    from retraite_notionnelle.moteur.conversion import Convertisseur

    regles = {"adosse": module.repartition, "echelle": _echelle_glissante,
              "roule": _roulement}
    if regle not in regles:
        raise ValueError(f"règle inconnue « {regle} » ; il y a {', '.join(regles)}")
    parametres = replace(_parametres(), prime_terme_trente_ans=prime)
    mortalite = _simulateur(_parametres()).mortalite
    constructeur = module.ConstructeurCapitalisation(
        CourbeTauxSansRisque(parametres.racine_donnees, prime), mortalite,
        Convertisseur(mortalite, parametres), parametres)
    ancienne = module.repartition
    module.repartition = regles[regle]
    try:
        return constructeur.construire(
            {annee: 30_000.0 for annee in range(2030, 2066)}, 1996, 64.0, 2060)
    finally:
        module.repartition = ancienne


def allocation(**reglages: str) -> float:
    """Ce que l'adossement rapporte face à une autre allocation, sous une prime de terme.

    ``contre=echelle`` (l'échelle glissante d'avant septembre 2026) ou
    ``contre=roule`` (un roulement à un an) ; ``prime``, en fraction, vaut par
    défaut le milieu de la fourchette. ``quoi=capital`` : l'écart de capital,
    en % ; ``quoi=rente`` : l'écart de rente mensuelle, en euros ;
    ``quoi=annees`` : les années de versement de la carrière témoin.
    """
    from retraite_notionnelle.config import PRIME_TERME_MILIEU

    prime = float(reglages.get("prime", PRIME_TERME_MILIEU))
    adosse = _pilier_alloue("adosse", prime)
    quoi = reglages.get("quoi", "capital")
    if quoi == "annees":
        return adosse.annees_cotisees
    autre = _pilier_alloue(reglages["contre"], prime)
    if quoi == "capital":
        return (adosse.capital / autre.capital - 1) * 100
    if quoi == "rente":
        return adosse.rente_mensuelle - autre.rente_mensuelle
    raise ValueError(f"quoi inconnu « {quoi} »")


MESURES = {
    "solde": solde,
    "solde_moyen": solde_moyen,
    "coefficient": coefficient,
    "annees_equilibrees": annees_equilibrees,
    "dette": dette,
    "recette": recette,
    "somme_postes": somme_postes,
    "restitution": restitution,
    "gain_net": gain_net,
    "fiche": fiche,
    "garantie_complement": garantie_complement,
    "garantie_foyer": garantie_foyer,
    "frais_reserve": frais_reserve,
    "allocation": allocation,
    "avance": avance,
    "profils_oracle": profils_oracle,
    "ecart_openfisca": ecart_openfisca,
    "avantages": avantages,
    "depense": depense,
    "surcout_passe": surcout_passe,
    "rapport_depenses": rapport_depenses,
    "prelevement_pension": prelevement_pension,
    "poids": poids,
    "grille": grille,
    "garantie": garantie,
    "fusion": fusion,
    "constante": constante,
    "parametre": parametre,
    "ecart": ecart,
    "pension": pension,
    "aujourd_hui": aujourd_hui,
    "part_employeur": part_employeur,
    "part_salariale_versee": part_salariale_versee,
    "cumul_indexation": cumul_indexation,
    "conserve": conserve,
    "fois_prix": fois_prix,
    "cumul_passe": cumul_passe,
    "ecart_passe": ecart_passe,
    "cout_annee": cout_annee,
    "part_pib": part_pib,
    "cumul_avenir": cumul_avenir,
    "ecart_avenir": ecart_avenir,
    "economie_pib": economie_pib,
    "taux_indexation": taux_indexation,
    "anticipation": anticipation,
    "millieme_salaire": millieme_salaire,
    "poids_trimestre": poids_trimestre,
    "dependance": dependance,
    "emploi_projete": emploi_projete,
    "composition_revalorisation": composition_revalorisation,
    "age_reference": age_reference,
    "droits_acquis": droits_acquis,
    "droits_acquis_variation": droits_acquis_variation,
    "approximation_revalorisation": approximation_revalorisation,
    "ecart_colonnes": ecart_colonnes,
    "derive_revalorisation": derive_revalorisation,
    "taux_statut": taux_statut,
    "mortalite_population": mortalite_population,
    "table_mortalite": table_mortalite,
    "part_pensions_sous": part_pensions_sous,
    "fiche_regime": fiche_regime,
    "fourchette": fourchette,
}


def mesurer(argument: str) -> float:
    """``nom?clé=valeur&clé=valeur`` : la mesure, sous ces réglages."""
    nom, _, condition = argument.partition("?")
    if nom not in MESURES:
        raise ValueError(f"mesure inconnue « {nom} » ; il y a {', '.join(sorted(MESURES))}")
    reglages = {}
    for critere in filter(None, condition.split("&")):
        cle, egal, valeur = critere.partition("=")
        if not egal:
            raise ValueError(f"« {critere} » n'est pas un réglage « clé=valeur »")
        reglages[cle] = valeur
    try:
        return float(MESURES[nom](**reglages))
    except KeyError as manque:
        raise ValueError(f"la mesure « {nom} » demande le réglage {manque}") from None
