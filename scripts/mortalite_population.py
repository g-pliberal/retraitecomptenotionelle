#!/usr/bin/env python3
"""Ce que le diviseur commun transfère à qui vit plus longtemps (action 14).

    python scripts/mortalite_population.py                       # les fonctionnaires civils
    python scripts/mortalite_population.py --generations 1960 1990
    python scripts/mortalite_population.py --cas-type salaire_moyen  # une carrière du privé
                                                                 # sous la même mortalité
    python scripts/mortalite_population.py --niveau-de-vie       # les treize cas types, chacun
                                                                 # au vingtile où son salaire le place
    python scripts/mortalite_population.py --deficit             # ce que le diviseur commun coûte
                                                                 # au régime, en part de PIB
    python scripts/mortalite_population.py --deficit --depuis 2026  # le flux seul, le stock gardé

CE QU'IL MESURE
---------------
Le diviseur de conversion des comptes notionnels est une espérance de vie de
POPULATION GÉNÉRALE : la même pour tout le monde. Une population qui vit plus
longtemps touche donc la même pension annuelle, servie plus d'années. Ce
script mesure ce transfert pour une population dont un régime publie
l'espérance de vie — aujourd'hui les fonctionnaires civils de l'État, par le
Service des retraites de l'État — en refaisant chaque cas type deux fois :
sous la table commune, et sous la table corrigée du facteur que
``DonneesMortalite.facteur_population`` cale sur l'espérance publiée.

Pour chaque scénario, la sortie donne la pension annuelle sous les deux tables,
l'écart, et le TRANSFERT SUR LA VIE : la pension commune multipliée par les
années de rente que la population reçoit en plus de la population générale.
En euros constants, sans actualisation — ce que le diviseur fait lui-même,
puisque la rente est actualisée au taux auquel elle est indexée (§5 de
``docs/methodologie.md``).

L'AXE DU REVENU
---------------
``--niveau-de-vie`` prend les tables de l'INSEE par vingtile de niveau de vie
(``mortalite/esperances_vie_niveau_de_vie.csv``) et rattache chaque cas type
au vingtile où son salaire le place par rapport au salaire moyen — une
convention, écrite dans ``DonneesMortalite.population_niveau_de_vie`` et dans
``docs/methodologie.md`` §5. Le tableau donne alors, pour une génération, les
treize cas types côte à côte : années de rente en plus ou en moins, écart de
pension notionnelle à capital égal, transfert sur la vie sous le système
actuel et sous la proposition. C'est la réponse à l'objection « le notionnel
fait payer les carrières courtes pour la longévité des autres » : le chiffre,
scénario par scénario.

CE QUE LE DIVISEUR COMMUN COÛTE AU RÉGIME
-----------------------------------------
``--deficit`` répond à la question suivante : si chaque assuré recevait le
diviseur de son vingtile, de combien la dépense des scénarios notionnels
baisserait-elle ? Sous un diviseur commun, chacun touche une rente calculée
pour la durée moyenne et servie pendant SA durée ; la masse versée sur la
vie vaut donc capital × (sa durée / durée moyenne), plus grande pour qui vit
longtemps — et qui vit longtemps a les plus gros capitaux. Le diviseur par
vingtile ramène chaque masse à son capital. L'écart est ce que le diviseur
commun coûte, et il se lit sur les têtes de la trajectoire de la page Coût :
les couples (cas type, génération) de sa grille, variantes comprises
(``GRILLE``), les effectifs INSEE par âge, les poids de caisse de sa
dernière année observée, et sa survie. Depuis le 17 octobre 2026, la page
fait vivre chaque cas type au rythme de la population de son diviseur, le
vingtile où le salaire de sa carrière le range, ou de la sienne, pour
l'inapte et l'ex-invalide, à nombre de décès égal : chaque cohorte garde les
survivants de la pyramide, que cette survie répartit entre fortes et faibles
pensions (``cout._survies``, ``_survies_alignees``). Le script prend la même,
par les mêmes fonctions, sur les mêmes vingtiles.

La page ne la compte que sous le diviseur par vingtile, le défaut du site :
l'interrupteur est le même, et sous la table commune, d'où partent les
soldes imprimés ici, elle revient à la pyramide seule. Le premier tableau dit
ce que cette survie déplace à diviseur commun : la masse du système actuel,
et le rapport de masses, seule chose que la page applique à la dépense
observée. Le second, ce que le diviseur par vingtile fait baisser la dépense
à cette survie, et, en regard, à la mortalité générale, comme la page le
comptait jusqu'au 17 octobre : les gros capitaux, que le diviseur baisse, y
sont servis moins longtemps, et la baisse, stock compris, en paraît plus
petite. Le solde « avec le diviseur par vingtile » ajoute cette baisse au
solde de la table commune ; celui du site compte aussi la survie. Aux
scénarios 3 et 5, le rapport des diviseurs ne touche que la part de chaque
pension que porte le compte ouvert à la bascule (``_parts_ouvertes``) : ils
gardent au stock d'avant la bascule le droit en vigueur, et les droits
acquis à la bascule passent par le diviseur de leur vingtile à l'entrée
comme à la sortie. Le scénario 1 n'a pas de diviseur : rien ne bouge.

Jusqu'au 19 octobre 2026, le script disait la page à la mortalité générale,
et ses colonnes « page » l'y mesuraient ; il faisait vivre chaque cas type au
rythme de son vingtile rapporté à la population générale, sans aligner, ne
relisait que les cas types de la page Cas types, sans leurs cinq variantes,
et rangeait chacun au vingtile de son niveau écrit (action 138, étape 7).
Jusqu'au 23 octobre, il appliquait aussi le rapport, aux scénarios 3 et 5, au
stock d'avant la bascule et aux droits acquis : il leur ajoutait 0,33 et 0,39
point de solde moyen de 2026 à 2070, la page 0,02 et 0,09 (même étape, note
« la part ouverte à la bascule »).

LE GARDE-FOU
------------
Le défaut n'appartient pas au notionnel. Toute rente viagère à taux commun le
porte, le scénario 1 le premier : sa pension ne bouge pas d'un euro sous la
table corrigée — aucun diviseur ne l'a calculée —, et c'est précisément
pourquoi le transfert y est du même ordre. Le calcul porte donc sur les six
scénarios, et la colonne « pension population » du scénario 1 dit ce que le
droit en vigueur ferait s'il tenait compte de la longévité : rien.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.somme import somme_ordonnee
from retraite_notionnelle.castypes import CAS_TYPES, GENERATIONS, GRILLE_DU_COUT  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.simulateur import SCENARIOS_NOTIONNELS, Simulateur  # noqa: E402

POPULATION_DEFAUT = "fonctionnaires_civils_etat"

#: La grille que ``--deficit`` relit : celle que la page Coût pèse
#: (``calculer_cout``), les cas types de la page Cas types et leurs variantes.
GRILLE = GRILLE_DU_COUT

#: Les cas types qui APPARTIENNENT à chaque population : ceux dont la caisse
#: est celle que le régime publiant l'espérance de vie sert.
CAISSES_PAR_POPULATION = {
    "fonctionnaires_civils_etat": ("fonction_publique_etat_civile",),
}

SCENARIOS = (("actuel", 1, "Système actuel"), *SCENARIOS_NOTIONNELS)


def cas_types_de(population: str):
    caisses = CAISSES_PAR_POPULATION.get(population, ())
    return [cas for cas in CAS_TYPES if any(c in caisses for c in cas.caisses)]


_SIMULATEURS: dict[str | None, Simulateur] = {}


def _simulateur(population: str | None) -> Simulateur:
    """Un simulateur par population, gardé : ses données se chargent une fois."""
    if population not in _SIMULATEURS:
        _SIMULATEURS[population] = Simulateur(Parametres(population_conversion=population))
    return _SIMULATEURS[population]


def mesurer(population: str, cas_type, generation: int) -> dict | None:
    commun = _simulateur(None)
    corrige = _simulateur(population)
    try:
        carriere = cas_type.construire(commun, generation)
        avec = commun.simuler(carriere)
        sans = corrige.simuler(carriere)
    except (ValueError, KeyError) as erreur:
        return {"erreur": str(erreur)}
    age = carriere.age_liquidation
    date = carriere.annee_liquidation + carriere.fraction_annee_liquidation
    e_commune = commun.mortalite.esperance_residuelle(age, date)
    e_population = commun.mortalite.esperance_residuelle(age, date, population=population)
    lignes = []
    for cle, numero, libelle in SCENARIOS:
        p_commune = avec.en_euros_constants(getattr(avec, cle).pension_annuelle, cle)
        p_population = sans.en_euros_constants(getattr(sans, cle).pension_annuelle, cle)
        # La proposition peut partir plus tard que les autres — son âge légal
        # est de 65 ans — et sa rente se sert alors sur l'espérance de CE
        # départ-là.
        depart = avec.carriere_de(cle)
        if depart is carriere:
            ecart_vie = e_population - e_commune
        else:
            date_s = depart.annee_liquidation + depart.fraction_annee_liquidation
            ecart_vie = (
                commun.mortalite.esperance_residuelle(
                    depart.age_liquidation, date_s, population=population)
                - commun.mortalite.esperance_residuelle(depart.age_liquidation, date_s)
            )
        lignes.append({
            "numero": numero,
            "libelle": libelle.format(bascule=commun.parametres.annee_bascule),
            "pension_commune": p_commune,
            "pension_population": p_population,
            "ecart": (p_population / p_commune - 1.0) if p_commune else 0.0,
            "transfert_vie": p_commune * ecart_vie,
        })
    return {
        "age_liquidation": age,
        "annee_liquidation": carriere.annee_liquidation,
        "esperance_commune": e_commune,
        "esperance_population": e_population,
        "scenarios": lignes,
    }


def _euros(montant: float) -> str:
    return f"{montant:,.0f}".replace(",", "\u202f")


def _rapports(pensionne, mortalite, vingtile: str) -> tuple[float, ...]:
    """Le rapport des diviseurs de chacune des cinq cohortes d'un couple de la
    page Coût, du ``-_DEMI_TRANCHE`` au ``+_DEMI_TRANCHE`` : ce que sa pension
    devient sous le diviseur de son vingtile. Ses deux courbes se prennent à
    l'âge et à l'année où la cohorte part, ceux que le droit de SA génération
    lui donne (``Pensionne.liquidation``), comme la page date sa survie
    (``cout._survies``).

    LES CINQ PARTAIENT AVEC LA GRILLE. Jusqu'au 19 octobre 2026, le script
    les faisait partir à l'âge de la génération que la grille simule, l'année
    décalée d'autant — l'erreur que la page a quittée le 18 octobre —, et
    prenait le rapport et les courbes une fois par couple, à cet âge et à
    cette année (action 138, étape 3). Les courbes lui donnaient aussi sa
    survie, jusqu'au même jour : la page la donne désormais (:func:`_couple`)."""
    from retraite_notionnelle.cout import _DEMI_TRANCHE

    rapports = []
    for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
        depart = pensionne.liquidation(decalage)
        age = depart - pensionne.generation - decalage
        commune = mortalite.courbe(age, float(depart), None, True)
        propre = mortalite.courbe(age, float(depart), None, True, vingtile)
        e_commune = somme_ordonnee(0.5 * (commune[k] + commune[k + 1])
                                   for k in range(len(commune) - 1))
        e_propre = somme_ordonnee(0.5 * (propre[k] + propre[k + 1])
                                  for k in range(len(propre) - 1))
        rapports.append(e_commune / e_propre)
    return tuple(rapports)


def _couple(pensionne, simulateur, vingtile: str, propre: str = ""):
    """Un couple de la page Coût, tel que le déficit le lit : le couple, sa
    survie posée comme la page la pose sous le diviseur par vingtile, et le
    rapport des diviseurs de ses cinq cohortes (:func:`_rapports`). Sa survie
    est celle de la population de son diviseur, ``vingtile``, ou de la
    sienne, ``propre``, pour l'inapte et l'ex-invalide (``CasType.mortalite``),
    chaque cohorte depuis son départ (``cout._survies``) ; son diviseur reste
    celui de son vingtile."""
    from retraite_notionnelle.cout import _DEMI_TRANCHE, _survies

    departs = tuple(pensionne.liquidation(decalage)
                    for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1))
    survies = _survies(simulateur, vingtile, pensionne.generation, departs, propre)
    return (replace(pensionne, survies=survies),
            _rapports(pensionne, simulateur.mortalite, vingtile))


def _vingtiles(simulateur, cas_types, liquidation: str) -> dict[tuple[str, int], str]:
    """Le vingtile de chaque couple de la grille, celui que le diviseur de la
    page lui donne sous le défaut du site, et sa survie avec lui : où le
    salaire de SA carrière, telle que la page la construit, la place — la
    somme de ses revenus cotisés rapportée à celle des salaires moyens des
    mêmes années (``niveau_relatif``, ``Convertisseur.population_de``).

    LE NIVEAU ÉCRIT. Jusqu'au 19 octobre 2026, le script rangeait chaque cas
    type au vingtile de son niveau écrit (``CasType.niveau_relatif``), quand
    la page range sa carrière : le salarié au salaire moyen au treizième, que
    la page met au quatorzième ou au quinzième, et 189 couples sur 345 dans un
    autre vingtile que celui de la page (action 138, étape 7)."""
    from retraite_notionnelle.castypes import carrieres_de_la_grille
    from retraite_notionnelle.cout import generations
    from retraite_notionnelle.moteur.conversion import niveau_relatif

    projection = simulateur.pour_la_projection()
    carrieres, _ = carrieres_de_la_grille(projection, cas_types, generations(), liquidation)
    return {cle: projection.mortalite.population_niveau_de_vie(
                niveau_relatif(carriere, projection.macro))
            for cle, carriere in carrieres.items()}


def _parts_ouvertes(simulateur, cas_types, liquidation: str,
                    ) -> dict[tuple[str, int], dict[str, float]]:
    """La part de la pension de chaque couple de la grille que porte, sous
    chaque scénario notionnel, le compte ouvert à la bascule : la seule que le
    diviseur de son vingtile touche (:func:`_masses`). Elle se lit sur la
    simulation de la carrière que la page construit, sous les conventions de
    sa projection : un, moins la part de son capital que portent les droits
    acquis à la bascule (``capital_droits_acquis``, ``capital_notionnel``).

    Aux scénarios 3 et 5, zéro pour qui part au plus tard l'année de la
    bascule, à qui ils gardent la pension du droit en vigueur
    (``ScenarioNotionnel._deja_liquide``) ; ensuite, les droits acquis à la
    bascule entrent au compte par le diviseur de leur vingtile et en sortent
    par lui (``_droits_acquis``), et seul le compte ouvert à la bascule le
    sent, pour l'essentiel. Un aux scénarios 2, 4 et 6, qui n'ont pas de
    droits acquis. La grille de la page ne garde pas ces capitaux : le moteur
    Python resimule ses carrières, sans les couples qu'il refuse, que la page
    ne pèse pas."""
    from retraite_notionnelle.castypes import carrieres_de_la_grille
    from retraite_notionnelle.cout import generations

    projection = simulateur.pour_la_projection()
    carrieres, _ = carrieres_de_la_grille(projection, cas_types, generations(), liquidation)
    parts = {}
    for cle, carriere in carrieres.items():
        try:
            comparaison = projection.simuler(carriere)
        except (ValueError, KeyError):
            continue
        parts[cle] = {}
        for scenario, _, _ in SCENARIOS_NOTIONNELS:
            resultat = getattr(comparaison, scenario)
            parts[cle][scenario] = (
                1.0 - resultat.capital_droits_acquis / resultat.capital_notionnel
                if resultat.capital_notionnel > 0.0 else 1.0)
    return parts


def _masses(couples, poids: dict[str, float], population, annee: int, cles: list[str],
            depuis: int | None = None,
            ouvertes: dict[tuple[str, int], dict[str, float]] | None = None,
            ) -> dict[str, dict[str, float]]:
    """Masses par scénario, sous le diviseur commun et sous le diviseur
    propre, à deux survies : celle de la page (``vrai_``), et la mortalité
    générale (``generale_``), que la page comptait jusqu'au 17 octobre 2026 et
    compte encore sous la table commune. ``couples`` sont les couples de la
    page et les rapports des diviseurs de leurs cohortes (:func:`_couple`) :
    chaque cohorte compte depuis l'année où elle part, et garde les survivants
    de la pyramide, que la survie de leur population répartit entre ses cas
    types, pesés par ``poids`` (``cout._survies_alignees``) ; ``depuis``
    choisit le flux sur son départ à elle. Le rapport ne touche que la part de
    chaque pension que ``ouvertes`` donne au compte ouvert à la bascule, par
    couple et par scénario (:func:`_parts_ouvertes`) ; un scénario qu'il ne
    nomme pas le sent sur toute la pension.

    LE RAPPORT TOUCHAIT TOUTE LA PENSION. Jusqu'au 23 octobre 2026, il
    s'appliquait aussi, aux scénarios 3 et 5, au stock d'avant la bascule et
    aux droits acquis à la bascule, et grossissait leur baisse (action 138,
    étape 7, note « la part ouverte à la bascule »).

    LA SURVIE N'ÉTAIT PAS ALIGNÉE. Jusqu'au 19 octobre 2026, la survie vraie
    était celle du vingtile rapportée à la population générale, et la grille,
    qui n'est pas une population, n'y gardait pas le nombre des décès ; les
    clés ``page_`` disaient la page à la mortalité générale (action 138,
    étape 7)."""
    from retraite_notionnelle.cout import _DEMI_TRANCHE, _survies_alignees

    total = {s: {"generale_commun": 0.0, "generale_propre": 0.0,
                 "vrai_commun": 0.0, "vrai_propre": 0.0} for s in cles}
    alignees = _survies_alignees([pensionne for pensionne, _ in couples], poids, annee)
    for pensionne, rapports in couples:
        part = poids.get(pensionne.code, 0.0)
        if part <= 0.0:
            continue
        compte = (ouvertes or {}).get((pensionne.code, pensionne.generation), {})
        for decalage, rapport in zip(range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1), rapports):
            liquidation = pensionne.liquidation(decalage)
            if annee < liquidation:
                continue
            effectif = population.effectif(annee - pensionne.generation - decalage, annee)
            survie = alignees.get((pensionne.code, pensionne.generation, decalage), 1.0)
            flux = depuis is None or liquidation >= depuis
            for s in cles:
                ouverte = compte.get(s, 1.0)
                applique = ouverte * rapport + (1.0 - ouverte) if flux else 1.0
                base = part * effectif * pensionne.pensions.get(s, 0.0)
                total[s]["generale_commun"] += base
                total[s]["generale_propre"] += base * applique
                total[s]["vrai_commun"] += base * survie
                total[s]["vrai_propre"] += base * survie * applique
    return total


def _deficit(depuis: int | None = None) -> int:
    """Ce que le diviseur commun coûte au régime, sur la trajectoire de la page Coût.

    ``depuis`` restreint la mesure au FLUX : seules les pensions liquidées à
    compter de cette année reçoivent le diviseur de leur vingtile, le stock
    gardant le diviseur commun — c'est ainsi qu'une réforme s'appliquerait.
    Sans lui, tout le monde est recalculé, stock compris : c'est le coût du
    diviseur commun en régime permanent.
    """
    from retraite_notionnelle.cout import _pensionnes, calculer_cout
    from retraite_notionnelle.donnees.assiette import AssietteActivite
    from retraite_notionnelle.donnees.depenses import DepensesRetraite
    from retraite_notionnelle.donnees.equilibre import ComptesRetraite
    from retraite_notionnelle.donnees.population import Population

    simulateur = _simulateur(None)
    racine = simulateur.parametres.racine_donnees
    population = Population(racine)
    cout = calculer_cout(simulateur, DepensesRetraite(racine), population,
                         ComptesRetraite(racine), cas_types=GRILLE,
                         assiette=AssietteActivite(racine))
    pensionnes, _ = _pensionnes(simulateur, GRILLE, cout.liquidation)
    vingtiles = _vingtiles(simulateur, GRILLE, cout.liquidation)
    ouvertes = _parts_ouvertes(simulateur, GRILLE, cout.liquidation)
    propres = {cas.code: cas.mortalite for cas in GRILLE}
    # La survie se prend sous les conventions de la page, comme sa grille.
    projection = simulateur.pour_la_projection()
    couples = [_couple(pensionne, projection, vingtiles[pensionne.code, pensionne.generation],
                       propres[pensionne.code])
               for pensionne in pensionnes]
    scenarios = [cle for cle, _, _ in SCENARIOS_NOTIONNELS]

    def masses(annee: int, avec_actuel: bool = False) -> dict[str, dict[str, float]]:
        cles = ["actuel", *scenarios] if avec_actuel else scenarios
        return _masses(couples, cout.poids, population, annee, cles, depuis, ouvertes)

    print("Chaque cas type au vingtile où le salaire de sa carrière le place, et à la survie "
          "que la page Coût lui donne ; les têtes, les poids et les pensions sont ceux de sa "
          "trajectoire, sous la table commune.")
    print("Le diviseur par vingtile s'applique "
          + (f"aux seules pensions liquidées à compter de {depuis} ; le stock garde le "
             "diviseur commun." if depuis else "à toutes les pensions, stock compris.")
          + "\n")

    # D'abord ce que la survie de la page déplace, à diviseur commun : la
    # masse du système actuel, et le RAPPORT de masses, seule chose que la
    # page applique à la dépense observée. La page la compte sous le diviseur
    # par vingtile ; sous la table commune, elle revient à la pyramide.
    print("Ce que la survie de la page, chaque cas type au rythme de sa population et à "
          "nombre de décès égal, déplace à diviseur commun, contre la mortalité générale :\n")
    print("| Année | Masse à la survie de la page / à la mortalité générale, système actuel | "
          "Rapport de masses, à la survie de la page / à la mortalité générale, scénario 2 | "
          "scénario 4 | scénario 6 |")
    print("|---:|---:|---:|---:|---:|")
    for annee in (2030, 2050, 2070):
        m = masses(annee, avec_actuel=True)
        survie = {s: m[s]["vrai_commun"] / m[s]["generale_commun"] - 1.0
                  for s in m if m[s]["generale_commun"] > 0}
        rapports = {s: (1.0 + survie[s]) / (1.0 + survie["actuel"]) - 1.0
                    for s in scenarios if s in survie}
        print(f"| {annee} | {survie['actuel']:+.1%} | {rapports['notionnel_retroactif']:+.1%} | "
              f"{rapports['notionnel_retroactif_employeur']:+.1%} | "
              f"{rapports['notionnel_liberal']:+.1%} |")
    print()
    print("| Scénario | Année | Baisse de la dépense, à la survie de la page | Baisse à la "
          "mortalité générale, comme la page la comptait jusqu'au 17 octobre 2026 | Solde sous "
          "la table commune, part de PIB | Solde avec le diviseur par vingtile |")
    print("|---|---:|---:|---:|---:|---:|")
    cumul = {s: [] for s in scenarios}
    for ligne in cout.solde.projetees():
        m = masses(ligne.annee)
        for s in scenarios:
            if m[s]["vrai_commun"] <= 0.0:
                continue
            vraie = 1.0 - m[s]["vrai_propre"] / m[s]["vrai_commun"]
            generale = 1.0 - m[s]["generale_propre"] / m[s]["generale_commun"]
            gain = ligne.depense(s) * vraie
            cumul[s].append((ligne.annee, vraie, generale, ligne.solde(s),
                             ligne.solde(s) + gain))
    libelles = {cle: f"{n} · {lib}" for cle, n, lib in SCENARIOS_NOTIONNELS}
    for s in scenarios:
        for annee, vraie, generale, avant, apres in cumul[s]:
            if annee in (2030, 2050, 2070):
                print(f"| {libelles[s].format(bascule=simulateur.parametres.annee_bascule)} | "
                      f"{annee} | {vraie:.1%} | {generale:.1%} | {avant:+.2%} | {apres:+.2%} |")
        moyen_avant = somme_ordonnee(l[3] for l in cumul[s]) / len(cumul[s])
        moyen_apres = somme_ordonnee(l[4] for l in cumul[s]) / len(cumul[s])
        print(f"| {libelles[s].format(bascule=simulateur.parametres.annee_bascule)} | "
              f"moyenne {cumul[s][0][0]}-{cumul[s][-1][0]} | | | {moyen_avant:+.2%} | {moyen_apres:+.2%} |")
    point = _point_de_pib(cout.solde.annees)
    if point:
        print(f"\n{point}")
    return 0


def _point_de_pib(annees) -> str:
    """Ce que vaut un point de PIB, au dernier PIB publié des ``annees`` du
    solde, en millions d'euros courants ; vide sans PIB publié. Jusqu'au
    19 octobre 2026, la phrase donnait le PIB entier pour un point."""
    publiee = next((ligne for ligne in reversed(annees) if ligne.pib > 0), None)
    if publiee is None:
        return ""
    milliards = publiee.pib / 100 / 1000
    return f"Un point de PIB vaut {_euros(milliards)} Md€ au PIB de {publiee.annee}."


def _par_niveau_de_vie(mortalite, generations: list[int]) -> int:
    """Les treize cas types, chacun sous la mortalité de son vingtile."""
    for sexe in mortalite.SEXES:
        bas = mortalite.esperance_publiee("niveau_de_vie_v01", sexe)[1]
        haut = mortalite.esperance_publiee("niveau_de_vie_v20", sexe)[1]
        print(f"INSEE 2020-2024, {sexe} : e65 de {bas:.2f} ans (5 % les plus modestes) "
              f"à {haut:.2f} ans (5 % les plus aisés)")
    for generation in generations:
        print(f"\n## Génération {generation}, chaque cas type au vingtile où son salaire le place")
        print("  | Cas type | Salaire | Vingtile | Rente, table commune | Rente, son vingtile | Écart | "
              "Pension notionnelle | Transfert, système actuel | Transfert, scénario 6 |")
        print("  |---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for cas in CAS_TYPES:
            niveau = cas.niveau_relatif(_simulateur(None), generation)
            population = mortalite.population_niveau_de_vie(niveau)
            resultat = mesurer(population, cas, generation)
            if resultat is None or "erreur" in resultat:
                print(f"  | {cas.libelle} | {niveau:.2f} | {population[-2:]} | écarté |||||||")
                continue
            par_numero = {l["numero"]: l for l in resultat["scenarios"]}
            print(f"  | {cas.libelle} | ×{niveau:.2f} | {int(population[-2:])} | "
                  f"{resultat['esperance_commune']:.1f} ans | {resultat['esperance_population']:.1f} ans | "
                  f"{resultat['esperance_population'] - resultat['esperance_commune']:+.1f} an | "
                  f"{par_numero[4]['ecart']:+.1%} | {_euros(par_numero[1]['transfert_vie'])} € | "
                  f"{_euros(par_numero[6]['transfert_vie'])} € |")
    print("\nLa colonne « Pension notionnelle » est l'écart de pension du scénario 4 sous la "
          "table du vingtile, à capital égal ; les transferts sont la pension sous la table "
          "commune multipliée par les années de rente en plus ou en moins, en euros constants.")
    return 0


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parseur.add_argument("--population", default=POPULATION_DEFAUT)
    parseur.add_argument("--cas-type", action="append", dest="cas_types",
                         help="code de cas type ; par défaut ceux de la population")
    parseur.add_argument("--generations", nargs="*", type=int, default=list(GENERATIONS))
    parseur.add_argument("--niveau-de-vie", action="store_true",
                         help="les treize cas types, chacun au vingtile de niveau de vie "
                              "où son salaire le place")
    parseur.add_argument("--deficit", action="store_true",
                         help="ce que le diviseur commun coûte au régime, sur la trajectoire "
                              "de la page Coût")
    parseur.add_argument("--depuis", type=int, default=None,
                         help="avec --deficit : n'appliquer le diviseur par vingtile qu'aux "
                              "pensions liquidées à compter de cette année (le flux), le stock "
                              "gardant le diviseur commun")
    args = parseur.parse_args()

    if args.deficit:
        return _deficit(args.depuis)
    mortalite = _simulateur(None).mortalite
    if args.niveau_de_vie:
        return _par_niveau_de_vie(mortalite, args.generations or [1975])
    if args.population not in mortalite.populations:
        parseur.error(f"population inconnue : {args.population} "
                      f"(connues : {mortalite.populations})")
    for sexe in mortalite.SEXES:
        annee, publiee = mortalite.esperance_publiee(args.population, sexe)
        generale = mortalite.esperance_residuelle(65, annee, sexe, generation=False)
        print(f"{args.population}, {sexe} : e65 publiée {publiee:.2f} en {annee}, "
              f"population générale {generale:.2f}, facteur sur la force de mortalité "
              f"{mortalite.facteur_population(args.population, sexe):.4f}")

    if args.cas_types:
        cas_types = [cas for cas in CAS_TYPES if cas.code in args.cas_types]
    else:
        cas_types = cas_types_de(args.population)
    if not cas_types:
        parseur.error("aucun cas type pour cette population")

    for cas in cas_types:
        for generation in args.generations:
            resultat = mesurer(args.population, cas, generation)
            print(f"\n## {cas.libelle} (`{cas.code}`), génération {generation}")
            if resultat is None or "erreur" in resultat:
                print(f"  écarté : {resultat['erreur'] if resultat else 'sans résultat'}")
                continue
            print(f"  liquidation à {resultat['age_liquidation']:.2f} ans en "
                  f"{resultat['annee_liquidation']} ; espérance résiduelle "
                  f"{resultat['esperance_commune']:.2f} ans (table commune), "
                  f"{resultat['esperance_population']:.2f} ans (population), "
                  f"soit {resultat['esperance_population'] - resultat['esperance_commune']:+.2f} an")
            print("  | # | Scénario | Pension, table commune | Pension, table population | Écart | Transfert sur la vie |")
            print("  |---|---|---:|---:|---:|---:|")
            for ligne in resultat["scenarios"]:
                print(f"  | {ligne['numero']} | {ligne['libelle']} | "
                      f"{_euros(ligne['pension_commune'])} €/an | "
                      f"{_euros(ligne['pension_population'])} €/an | "
                      f"{ligne['ecart']:+.1%} | {_euros(ligne['transfert_vie'])} € |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
