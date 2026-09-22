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
    # et un rang désigne l'élément d'un couple : le salaire d'ancrage est
    # ``ANCRAGE_SALAIRE_MOYEN.1``, l'année qui le porte ``.0``.
    for morceau in reglages["nom"].split("."):
        if morceau.isdigit() and isinstance(objet, tuple) and int(morceau) < len(objet):
            objet = objet[int(morceau)]
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
    — les versements de la CNAF, de l'Unédic et du FSV ; ``quoi=impots`` : les
    impôts et taxes affectés ; ``quoi=taux_prelevement`` : ce que le système
    prélève sur l'assiette des revenus d'activité, en %.
    """
    ligne = _solde_annee(reglages)
    quoi = reglages["quoi"]
    if quoi == "retrait":
        return ligne.retrait * 100
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

    L'année de référence ; ``quoi=salarie`` ou ``employeur``, ``systeme=actuel``
    (défaut) ou ``proposition``. Mêmes réglages que ``ecart``.
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


def garantie_complement(**reglages: str) -> float:
    """Ce que la garantie vieillesse sert, par mois, à qui a ``pension=…`` euros."""
    return max(0.0, _parametres().garantie_vieillesse_mensuelle - float(reglages["pension"]))


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
    "avance": avance,
    "profils_oracle": profils_oracle,
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
    "composition_revalorisation": composition_revalorisation,
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
