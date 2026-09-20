#!/usr/bin/env python3
"""Ce que le diviseur commun transfère à qui vit plus longtemps (action 14).

    python scripts/mortalite_population.py                       # les fonctionnaires civils
    python scripts/mortalite_population.py --generations 1960 1990
    python scripts/mortalite_population.py --cas-type salaire_moyen  # une carrière du privé
                                                                 # sous la même mortalité

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


def mesurer(population: str, cas_type, generation: int) -> dict | None:
    commun = Simulateur(Parametres())
    corrige = Simulateur(Parametres(population_conversion=population))
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


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parseur.add_argument("--population", default=POPULATION_DEFAUT)
    parseur.add_argument("--cas-type", action="append", dest="cas_types",
                         help="code de cas type ; par défaut ceux de la population")
    parseur.add_argument("--generations", nargs="*", type=int, default=list(GENERATIONS))
    args = parseur.parse_args()

    mortalite = Simulateur(Parametres()).mortalite
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
