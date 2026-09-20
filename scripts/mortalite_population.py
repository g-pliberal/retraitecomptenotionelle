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
les mêmes couples (cas type, génération), les mêmes effectifs INSEE par âge,
les mêmes poids de caisse — la survie de chaque cas type étant corrigée de
celle de son vingtile, ce que la page ne fait pas. La page compte tout le
monde à la mortalité générale ; appliquer les diviseurs sans corriger la
survie donnerait un chiffre plus grand et faux, imprimé ici en regard pour
qu'on voie l'écart. Le scénario 1 n'a pas de diviseur : rien ne bouge.

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
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.castypes import CAS_TYPES, GENERATIONS  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.simulateur import SCENARIOS_NOTIONNELS, Simulateur  # noqa: E402

POPULATION_DEFAUT = "fonctionnaires_civils_etat"

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
        p_commune = avec.en_euros_constants(getattr(avec, cle).pension_annuelle)
        p_population = sans.en_euros_constants(getattr(sans, cle).pension_annuelle)
        lignes.append({
            "numero": numero,
            "libelle": libelle.format(bascule=commun.parametres.annee_bascule),
            "pension_commune": p_commune,
            "pension_population": p_population,
            "ecart": (p_population / p_commune - 1.0) if p_commune else 0.0,
            "transfert_vie": p_commune * (e_population - e_commune),
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


def _deficit(mortalite) -> int:
    """Ce que le diviseur commun coûte au régime, sur la trajectoire de la page Coût."""
    from retraite_notionnelle.cout import _pensionnes, calculer_cout
    from retraite_notionnelle.donnees.assiette import AssietteActivite
    from retraite_notionnelle.donnees.depenses import DepensesRetraite
    from retraite_notionnelle.donnees.equilibre import ComptesRetraite
    from retraite_notionnelle.donnees.population import Population

    simulateur = _simulateur(None)
    racine = simulateur.parametres.racine_donnees
    population = Population(racine)
    cout = calculer_cout(simulateur, DepensesRetraite(racine), population,
                         ComptesRetraite(racine), assiette=AssietteActivite(racine))
    pensionnes, _ = _pensionnes(simulateur, CAS_TYPES, cout.liquidation)
    par_code = {cas.code: cas for cas in CAS_TYPES}
    vingtiles = {cas.code: mortalite.population_niveau_de_vie(cas.niveau_salaire)
                 for cas in CAS_TYPES}
    scenarios = [cle for cle, _, _ in SCENARIOS_NOTIONNELS]

    # Pour chaque couple : le rapport des diviseurs (ce que la pension devient
    # sous le diviseur du vingtile) et les deux courbes de survie.
    couples = []
    for pensionne in pensionnes:
        age = pensionne.annee_liquidation - pensionne.generation
        commune = mortalite.courbe(age, float(pensionne.annee_liquidation), None, True)
        propre = mortalite.courbe(age, float(pensionne.annee_liquidation), None, True,
                                  vingtiles[pensionne.code])
        e_commune = sum(0.5 * (commune[k] + commune[k + 1]) for k in range(len(commune) - 1))
        e_propre = sum(0.5 * (propre[k] + propre[k + 1]) for k in range(len(propre) - 1))
        couples.append((pensionne, e_commune / e_propre, commune, propre))

    def masses(annee: int, avec_actuel: bool = False) -> dict[str, dict[str, float]]:
        """Masses par scénario : page (survie générale) et vraies (survie du
        vingtile), sous le diviseur commun et sous le diviseur propre."""
        cles = ["actuel", *scenarios] if avec_actuel else scenarios
        total = {s: {"page_commun": 0.0, "page_propre": 0.0,
                     "vrai_commun": 0.0, "vrai_propre": 0.0} for s in cles}
        for pensionne, rapport, commune, propre in couples:
            part = cout.poids.get(pensionne.code, 0.0)
            if part <= 0.0:
                continue
            for decalage in range(-2, 3):
                liquidation = pensionne.annee_liquidation + decalage
                if annee < liquidation:
                    continue
                effectif = population.effectif(annee - pensionne.generation - decalage, annee)
                duree = annee - liquidation
                survie = (propre[duree] / commune[duree]
                          if duree < min(len(commune), len(propre)) and commune[duree] > 0
                          else 0.0)
                for s in cles:
                    pension = pensionne.pensions.get(s, 0.0)
                    base = part * effectif * pension
                    total[s]["page_commun"] += base
                    total[s]["page_propre"] += base * rapport
                    total[s]["vrai_commun"] += base * survie
                    total[s]["vrai_propre"] += base * survie * rapport
        return total

    print("Chaque cas type au vingtile où son salaire le place ; les têtes, les poids et les "
          "pensions sont ceux de la trajectoire de la page Coût.\n")

    # D'abord le biais de la page elle-même : elle compte tout le monde à la
    # mortalité générale. Sous les règles actuelles (diviseur commun), de
    # combien la masse vraie — survie du vingtile — dépasse-t-elle la masse
    # comptée, et de combien le RAPPORT de masses, seule chose que la page
    # applique à la dépense observée, en est-il déplacé ?
    print("Ce que la page sous-compte en comptant tout le monde à la mortalité générale :\n")
    print("| Année | Masse vraie / masse comptée, système actuel | Rapport de masses corrigé / "
          "rapport de la page, scénario 2 | scénario 4 | scénario 6 |")
    print("|---:|---:|---:|---:|---:|")
    for annee in (2030, 2050, 2070):
        m = masses(annee, avec_actuel=True)
        biais = {s: m[s]["vrai_commun"] / m[s]["page_commun"] - 1.0
                 for s in m if m[s]["page_commun"] > 0}
        rapports = {s: (1.0 + biais[s]) / (1.0 + biais["actuel"]) - 1.0
                    for s in scenarios if s in biais}
        print(f"| {annee} | {biais['actuel']:+.1%} | {rapports['notionnel_retroactif']:+.1%} | "
              f"{rapports['notionnel_retroactif_employeur']:+.1%} | "
              f"{rapports['notionnel_liberal']:+.1%} |")
    print()
    print("| Scénario | Année | Baisse de la dépense, survie du vingtile | Baisse si la page "
          "l'appliquait sans corriger la survie | Solde, part de PIB | Solde avec le diviseur "
          "par vingtile |")
    print("|---|---:|---:|---:|---:|---:|")
    cumul = {s: [] for s in scenarios}
    for ligne in cout.solde.projetees():
        m = masses(ligne.annee)
        for s in scenarios:
            if m[s]["vrai_commun"] <= 0.0:
                continue
            vraie = 1.0 - m[s]["vrai_propre"] / m[s]["vrai_commun"]
            page = 1.0 - m[s]["page_propre"] / m[s]["page_commun"]
            gain = ligne.depense(s) * vraie
            cumul[s].append((ligne.annee, vraie, page, ligne.solde(s), ligne.solde(s) + gain))
    libelles = {cle: f"{n} · {lib}" for cle, n, lib in SCENARIOS_NOTIONNELS}
    for s in scenarios:
        for annee, vraie, page, avant, apres in cumul[s]:
            if annee in (2030, 2050, 2070):
                print(f"| {libelles[s].format(bascule=simulateur.parametres.annee_bascule)} | "
                      f"{annee} | {vraie:.1%} | {page:.1%} | {avant:+.2%} | {apres:+.2%} |")
        moyen_avant = sum(l[3] for l in cumul[s]) / len(cumul[s])
        moyen_apres = sum(l[4] for l in cumul[s]) / len(cumul[s])
        print(f"| {libelles[s].format(bascule=simulateur.parametres.annee_bascule)} | "
              f"moyenne {cumul[s][0][0]}-{cumul[s][-1][0]} | | | {moyen_avant:+.2%} | {moyen_apres:+.2%} |")
    pib = next((l.pib for l in reversed(cout.solde.annees) if l.pib > 0), 0.0)
    annee_pib = next((l.annee for l in reversed(cout.solde.annees) if l.pib > 0), 0)
    if pib:
        print(f"\nUn point de PIB vaut {_euros(pib / 1000)} Md€ au PIB de {annee_pib}.")
    return 0


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
            population = mortalite.population_niveau_de_vie(cas.niveau_salaire)
            resultat = mesurer(population, cas, generation)
            if resultat is None or "erreur" in resultat:
                print(f"  | {cas.libelle} | {cas.niveau_salaire:.2f} | {population[-2:]} | écarté |||||||")
                continue
            par_numero = {l["numero"]: l for l in resultat["scenarios"]}
            print(f"  | {cas.libelle} | ×{cas.niveau_salaire:.2f} | {int(population[-2:])} | "
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
    args = parseur.parse_args()

    mortalite = _simulateur(None).mortalite
    if args.deficit:
        return _deficit(mortalite)
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
