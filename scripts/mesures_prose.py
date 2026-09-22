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
}


@lru_cache(maxsize=None)
def _comparaison(generation: int, indexation: str, lissage: str,
                 affiliation: str, sexe: str, debut: int, depart: int,
                 primes: float, profil: str):
    simulateur = _simulateur(_parametres(indexation, lissage))
    options = {"part_primes": primes} if primes else {}
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
                        float(voulu.get("primes", 0) or 0), voulu.get("profil", ""))


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


def dependance(**reglages: str) -> float:
    """Rapport de dépendance démographique d'une année : 65 ans et plus sur 20-64 ans."""
    return _avenir(reglages).dependance


def fusion(**reglages: str) -> float:
    """Un champ du régime unique qui naît à la bascule — ``champ=…``.

    Un taux (``taux_cotisation_retraite``, ``taux_cotisation_salarie``) se lit
    en %, le reste dans son unité : ``duree_requise`` en trimestres,
    ``age_ouverture`` en années.
    """
    fusionne = _simulateur(_parametres()).regime_fusionne
    champ = reglages["champ"]
    if not hasattr(fusionne, champ):
        raise ValueError(f"le régime unique n'a pas de champ « {champ} »")
    valeur = float(getattr(fusionne, champ))
    return valeur * 100 if champ.startswith("taux") else valeur


def parametre(**reglages: str) -> float:
    """Un paramètre par défaut du modèle : ``nom=taux_cotisation_liberal``.

    Un taux se lit en %, le reste dans son unité — ``annee_bascule``,
    ``age_reference``. C'est le réglage que le site prend quand on ne lui dit
    rien, et celui que la prose décrit.
    """
    parametres = _parametres()
    nom = reglages["nom"]
    if not hasattr(parametres, nom):
        raise ValueError(f"les paramètres n'ont pas de champ « {nom} »")
    valeur = float(getattr(parametres, nom))
    return valeur * 100 if nom.startswith("taux") or nom.startswith("part") else valeur


def constante(**reglages: str) -> float:
    """Une constante du modèle : ``de=module&nom=CONSTANTE``.

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
    # et un rang désigne l'élément d'un couple : le salaire d'ancrage est
    # ``ANCRAGE_SALAIRE_MOYEN.1``, l'année qui le porte ``.0``.
    for morceau in reglages["nom"].split("."):
        if morceau.isdigit() and isinstance(objet, tuple) and int(morceau) < len(objet):
            objet = objet[int(morceau)]
        elif hasattr(objet, morceau):
            objet = getattr(objet, morceau)
        else:
            raise ValueError(f"{reglages['de']} n'a pas de « {reglages['nom']} »")
    return float(objet)


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
    dépendance, minimum vieillesse —, ``part_pib`` pour la totale en % du PIB.
    """
    from retraite_notionnelle.donnees.depenses import SYSTEMES

    depenses, annee = _depenses(), int(reglages["annee"])
    quoi = reglages.get("quoi", "totale")
    if quoi == "totale":
        return depenses.depense(annee) / 1000
    if quoi == "part_pib":
        return depenses.part_pib(annee) * 100
    if quoi in ("repartition", "hors_repartition"):
        voulu = quoi == "repartition"
        return sum(depenses.depense_systeme(s.code, annee) for s in SYSTEMES
                   if s.repartition == voulu) / 1000
    raise ValueError(f"quoi inconnu « {quoi} »")


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
    """La taille de la grille du coût : ``quoi=cas_types`` ou ``generations``."""
    from retraite_notionnelle import cout as C
    from retraite_notionnelle.castypes import CAS_TYPES

    quoi = reglages["quoi"]
    if quoi == "cas_types":
        return len(CAS_TYPES)
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
    observée. ``annee`` : la dernière année de la série si on l'omet.
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
    valeurs = {"total": ligne.gratuit / 1000, "lues": lues / 1000,
               "calculees": (ligne.gratuit - lues) / 1000,
               "part_lue": lues / ligne.gratuit * 100,
               "part_depense": ligne.gratuit / ligne.observee * 100}
    if quoi not in valeurs:
        raise ValueError(f"quoi inconnu « {quoi} »")
    return valeurs[quoi]


MESURES = {
    "avantages": avantages,
    "depense": depense,
    "surcout_passe": surcout_passe,
    "poids": poids,
    "grille": grille,
    "garantie": garantie,
    "fusion": fusion,
    "constante": constante,
    "parametre": parametre,
    "ecart": ecart,
    "pension": pension,
    "part_employeur": part_employeur,
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
