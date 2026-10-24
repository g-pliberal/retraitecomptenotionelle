"""L'âge des retraités de la page Coût, l'âge où ils partent et leurs conditions de départ, contre l'EACR.

    python scripts/controle_eacr.py                  # la grille de la page
    python scripts/controle_eacr.py --population     # et la population de l'étape 14

Ce que la grille de la page Coût compte en 2024, sous le scénario 1, contre
les tables H et C de l'EACR du 26 mai 2026
(``tests/temoins/drees_eacr_tables_2026.json``) : les retraités de droit
direct par tranche d'âge et leur pension, les nouveaux retraités par âge de
liquidation, les départs avec une décote ou une surcote. Le calcul est dans
``retraite_notionnelle.controle_eacr``, qui dit ce que l'écart mesure (action
138, étape 3). ``--population`` mesure de même la population de
``scripts/grille_large.py`` (action 136, étape 6, et 138, étape 14), et la
part de ses retraités du régime général partis avec une décote : plusieurs
minutes, la première fois.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE / "scripts"))

from retraite_notionnelle import controle_eacr as M  # noqa: E402
from retraite_notionnelle.somme import somme_ordonnee  # noqa: E402

TEMOIN = RACINE / "tests" / "temoins" / "drees_eacr_tables_2026.json"
NOMS_CAISSES = {"0015": "Cnav", "0021": "MSA salariés", "0022": "MSA exploitants",
                "0012": "État, civils", "0013": "État, militaires", "5600": "Agirc-Arrco"}

#: Les caisses de la table H qui sont au régime général de la population.
CAISSES_REGIME_GENERAL = ("0015",)


def _pc(part: float | None) -> str:
    return "—" if part is None else f"{100 * part:.1f}".replace(".", ",")


def _rapport(valeur: float | None) -> str:
    return "—" if valeur is None else f"{valeur:.2f}".replace(".", ",")


def mesure(lot: list[M.Cohorte], temoin: dict) -> dict:
    """Les parts et les rapports que les tableaux impriment, la grille ``lot``
    contre la table C."""
    series = temoin["droits_directs_par_age"]["series"]
    stock, publie = M.grille_par_tranche(lot), M.publie_par_tranche(series["ddir"]["ensemble"])
    flux, nouveaux = M.grille_par_age(lot), M.publie_par_depart(series["nl_ddir"]["ensemble"])
    moyenne, moyenne_publiee = M.moyenne(stock), M.moyenne(publie)
    return {
        "stock": {nom: {"grille": M.parts(stock).get(nom), "eacr": M.parts(publie)[nom],
                        "profil_grille": stock[nom][1] / moyenne if nom in stock else None,
                        "profil_eacr": publie[nom][1] / moyenne_publiee}
                  for _, _, nom in M.TRANCHES},
        "pension": {"grille": moyenne, "eacr": moyenne_publiee},
        "flux": {cle: {"grille": M.parts(flux).get(cle, 0.0), "eacr": M.parts(nouveaux)[cle]}
                 for cle in ["moins_60", *map(str, M.AGES_DE_DEPART),
                             f"{M.AGES_DE_DEPART[-1] + 1}_plus"]},
        "age_moyen": {"grille": M.age_moyen(lot),
                      "eacr": M.age_moyen_publie(series["nl_ddir"]["ensemble"])},
        "flux_sur_stock": {"grille": M.moyenne(flux) / moyenne,
                           "eacr": M.moyenne(nouveaux) / moyenne_publiee},
    }


def population(processus: int) -> tuple[list[M.Cohorte], dict[str, float]]:
    """La population de ``grille_large.py`` en 2024, et la part de ses
    retraités du régime général partis avec une décote, en flux et en stock."""
    import grille_large as G
    from retraite_notionnelle.config import Parametres
    from retraite_notionnelle.simulateur import Simulateur

    parametres = Parametres()
    racine = parametres.racine_donnees
    _, valeurs = G.centiles(racine)
    variantes = G.grille("population", Simulateur(parametres).effectifs, G.eir(racine),
                         G.multiplicateurs(valeurs))
    tetes = G.en_tetes(parametres, variantes, processus, alleges=True)
    lot = M.cohortes(tetes.pensionnes, tetes.poids(M.ANNEE_EACR), tetes.population,
                     tetes.revalorisation,
                     tetes.macro.coefficient_prix(tetes.annee_euros, M.ANNEE_EACR))
    par_code = {v.cas.code: v for v in variantes}
    decotes = G.proratisations(
        parametres, {(par_code[c.code].cas, c.generation) for c in lot
                     if par_code[c.code].groupe == "regime_general"}, processus)
    parts = {}
    for champ, garder in (("flux", lambda c: c.nouvelle), ("stock", lambda c: True)):
        membres = [c for c in lot if par_code[c.code].groupe == "regime_general" and garder(c)]
        decotees = [c.tetes for c in membres
                    if decotes.get((c.code, c.generation), (0, False, 0, False))[3]]
        parts[champ] = somme_ordonnee(decotees) / somme_ordonnee(c.tetes for c in membres)
    return lot, parts


def imprimer(mesures: dict[str, dict], temoin: dict, decotes: dict[str, float] | None) -> None:
    noms = list(mesures)
    print(f"Les retraités de droit direct en {M.ANNEE_EACR}, par tranche d'âge : la part de "
          "chacune, puis sa pension rapportée à la moyenne (EACR, table C, tous régimes).")
    print()
    print("| Tranche | " + " | ".join(f"part, {n}" for n in noms) + " | part, EACR | "
          + " | ".join(f"pension, {n}" for n in noms) + " | pension, EACR |")
    print("|---" * (2 * len(noms) + 3) + "|")
    premiere = mesures[noms[0]]
    for nom in premiere["stock"]:
        print(f"| {nom} | " + " | ".join(_pc(mesures[n]["stock"][nom]["grille"]) for n in noms)
              + f" | {_pc(premiere['stock'][nom]['eacr'])} | "
              + " | ".join(_rapport(mesures[n]["stock"][nom]["profil_grille"]) for n in noms)
              + f" | {_rapport(premiere['stock'][nom]['profil_eacr'])} |")
    print()
    print(f"Les nouveaux retraités de {M.ANNEE_EACR}, par âge de liquidation (année moins "
          "génération), en pour cent.")
    print()
    print("| Âge | " + " | ".join(noms) + " | EACR |")
    print("|---" * (len(noms) + 2) + "|")
    for cle in premiere["flux"]:
        print(f"| {cle} | " + " | ".join(_pc(mesures[n]["flux"][cle]["grille"]) for n in noms)
              + f" | {_pc(premiere['flux'][cle]['eacr'])} |")
    for n in noms:
        m = mesures[n]
        print(f"| âge moyen, {n} | {m['age_moyen']['grille']:.2f} contre "
              f"{m['age_moyen']['eacr']:.2f} ; pension des nouveaux sur celle de tous : "
              f"{_rapport(m['flux_sur_stock']['grille'])} contre "
              f"{_rapport(m['flux_sur_stock']['eacr'])} |")
    print()
    print(f"Les conditions de départ en {M.ANNEE_EACR} (EACR, table H), en pour cent : la "
          "grille n'a ni décote ni surcote dans ces caisses.")
    print()
    print("| Caisse | Champ | Taux plein | Décote | Surcote | Décote, population |")
    print("|---|---|---:|---:|---:|---:|")
    for c in M.conditions_publiees(temoin):
        population_ = (_pc(decotes[c.champ]) if decotes and c.caisse in CAISSES_REGIME_GENERAL
                       else "")
        print(f"| {NOMS_CAISSES.get(c.caisse, c.caisse)} | {c.champ} | {_pc(c.taux_plein)} "
              f"| {_pc(c.decote)} | {_pc(c.surcote)} | {population_} |")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--population", action="store_true",
                           help="mesure aussi la population de grille_large.py")
    analyseur.add_argument("--processus", type=int, default=1,
                           help="cœurs de la population")
    analyseur.add_argument("--json", type=Path, help="écrit les mesures dans ce fichier")
    arguments = analyseur.parse_args(argv)

    temoin = json.loads(TEMOIN.read_text(encoding="utf-8"))
    mesures = {"grille": mesure(M.controle(), temoin)}
    decotes = None
    if arguments.population:
        lot, decotes = population(arguments.processus)
        mesures["population"] = mesure(lot, temoin)
    imprimer(mesures, temoin, decotes)
    if arguments.json:
        arguments.json.write_text(json.dumps({"mesures": mesures, "decotes": decotes},
                                             ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
