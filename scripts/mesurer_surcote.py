"""La surcote de la population, sous une version de ``grille_large.py`` et sans elle.

    python scripts/mesurer_surcote.py --processus 4 --json mesure.json
    python scripts/mesurer_surcote.py --grille reference --processus 1

POURQUOI CE SCRIPT. La note de la trente-septième version (action 138, étape
14, ``docs/feuille_de_route/138/2026-11-03-etape-14-surcote-du-salariat-selon-la-generation.md``)
tirait ses mesures d'un pilote resté hors du dépôt, qu'on ne pouvait refaire
(relecture R-I, point 4.4). Ce script les refait, telles que la note les
décrit : il construit la population, la constante ``--constante`` allumée
(« version ») puis éteinte (« éteinte »), vérifie que l'une et l'autre ont
les mêmes cas types aux mêmes poids, la simule une fois
(``grille_large.en_tetes``), et pèse chacune de ses parts des générations
(``GrilleEnTetes.parts``) :

* les départs des générations 1950 et 1955 de la grille, contre les nés en
  1950 et en 1953 de l'EIR (``grille_large.departs``) : la génération 1955,
  que l'enquête ne voit pas, se juge sur les nés en 1953
  (``GENERATIONS_DES_DEPARTS``) ;
* les fonctionnaires civils de l'État et de la CNRACL : leurs retraités de
  2024 et leurs liquidants de chaque année de 2020 à 2025 ;
* le régime général (le groupe ``regime_general`` de la population, celui de
  ``scripts/controle_eacr.py``) : ses liquidants et ses retraités de 2024, et
  la décote de ses liquidants ;
* les retraités de 2020, sexe par sexe, ceux de 70 à 74 ans, et la part des
  fonctionnaires civils parmi ceux qui ont surcoté ;
* l'âge des liquidants de 2024, contre la table C de l'EACR
  (``controle_eacr.mesure``), et ceux du régime général, âge par âge ;
* la distribution des pensions de 2020, contre l'EIR (``grille_large.confronter``).

DEUX FAÇONS DE COMPTER UNE SURCOTE. Au drapeau : la cohorte d'une jumelle qui
surcote (``Variante.surcote``), d'une génération simulée qui atteint son âge
légal depuis que la surcote existe (``CasTypeLarge._attente_du_depart``, la
règle même de son départ) ; c'est ainsi que se comptent les stocks. À la
condition de son départ (``grille_large.condition_au_depart``) : partie après
l'âge légal et après l'âge de son taux plein ; c'est ainsi que se comptent les
liquidants, parmi ceux dont la condition se lit. Une jumelle dont l'attente
ne mène pas au-delà de son taux plein part sans surcote ; une carrière qui
n'est pas jumelle peut partir après son taux plein. Le script donne l'une et
l'autre part des liquidants, et leur croisement.

Sur la population, la simulation dure près de deux heures sur quatre cœurs ;
la mémoire des calculs en garde les morceaux (``memoire.py``), et la refaire
sur le même modèle ne coûte que les pesées. ``--grille reference`` mesure la
grille de la page, ses 18 cas types, en quelques minutes : le cas court du
test.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE / "scripts"))

import controle_eacr as E  # noqa: E402
import grille_large as G  # noqa: E402
from retraite_notionnelle import controle_eacr as M  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402
from retraite_notionnelle.somme import somme_ordonnee  # noqa: E402

#: Les affiliations des fonctionnaires civils de chaque caisse du jaune
#: (``grille_large.CAISSES_DU_JAUNE``) : l'État, la CNRACL.
CAISSES = {"etat": tuple(a for a, c in G.CAISSES_DU_JAUNE.items() if c == "fpe_civils"),
           "cnracl": tuple(a for a, c in G.CAISSES_DU_JAUNE.items() if c == "cnracl_total")}
FONCTIONNAIRES_CIVILS = CAISSES["etat"] + CAISSES["cnracl"]

#: Les années dont la mesure compte les liquidants des fonctionnaires civils :
#: celles que la note met en regard des départs de 2025 du jaune.
ANNEES_DES_LIQUIDANTS = tuple(range(2020, 2026))

#: L'année du stock que l'EIR voit (« CondLiquidation », résidents), et la
#: tranche d'âge que la note en suit.
ANNEE_DU_STOCK = 2020
TRANCHE_DU_STOCK = (70, 74)

#: Le groupe de la population que la mesure range au régime général, et la
#: caisse de l'EACR qui le juge.
REGIME_GENERAL = "regime_general"
CNAV = "0015"
ETAT = "0012"


def surcotee(v: G.Variante, generation: int) -> bool:
    """Vrai pour une cohorte de ``v``, de la génération simulée ``generation``,
    comptée au drapeau : une jumelle qui surcote, dont la génération atteint
    son âge légal depuis que la surcote existe — la règle de son départ
    (``CasTypeLarge._attente_du_depart``, ``ANNEE_DE_LA_SURCOTE``)."""
    attente = getattr(v.cas, "_attente_du_depart", None)
    return bool(v.surcote) and attente is not None and attente(generation) is not None


def part(lot, garder, compter) -> float | None:
    """Les têtes des cohortes de ``lot`` que ``garder`` retient et que
    ``compter`` compte, sur celles que ``garder`` retient ; ``None`` sans elles."""
    gardees = [c for c in lot if garder(c)]
    total = somme_ordonnee(c.tetes for c in gardees)
    if not total:
        return None
    return somme_ordonnee(c.tetes for c in gardees if compter(c)) / total


def parts_des_liquidants(lot, garder, par_code: dict, conditions: dict) -> dict:
    """Les liquidants de l'année que ``garder`` retient : la part qui surcote au
    drapeau (:func:`surcotee`), celle qui part avec une surcote parmi ceux dont
    la condition se lit (``conditions``, clé ``(code, génération)``), et la
    part de ceux dont elle ne se lit pas."""
    membres = [c for c in lot if c.nouvelle and garder(c)]
    connus = [c for c in membres if (c.code, c.generation) in conditions]
    return {
        "drapeau": part(membres, lambda c: True,
                        lambda c: surcotee(par_code[c.code], c.generation)),
        "condition": part(connus, lambda c: True,
                          lambda c: conditions[(c.code, c.generation)][1] == "surcote"),
        "inconnues": part(membres, lambda c: True,
                          lambda c: (c.code, c.generation) not in conditions),
    }


def croisement(lot, garder, par_code: dict, conditions: dict) -> dict:
    """Les liquidants de l'année que ``garder`` retient et dont la condition se
    lit, en part de tous ceux-là : ceux qui surcotent au drapeau, puis les
    autres, chacun selon la classe de sa condition."""
    connus = [c for c in lot if c.nouvelle and garder(c) and (c.code, c.generation) in conditions]
    total = somme_ordonnee(c.tetes for c in connus)
    sortie: dict = {"drapeau": {}, "sans_drapeau": {}}
    if not total:
        return sortie
    for c in connus:
        cote = "drapeau" if surcotee(par_code[c.code], c.generation) else "sans_drapeau"
        classe = conditions[(c.code, c.generation)][1]
        sortie[cote][classe] = sortie[cote].get(classe, 0.0) + c.tetes / total
    return sortie


def parts_de_la_pesee(lots: dict, par_code: dict, conditions: dict, decotes: dict) -> dict:
    """Ce que la mesure compte d'une pesée, ses cohortes de chaque année dans
    ``lots`` (``controle_eacr.Cohorte``) : les retraités de 2024 et les
    liquidants de chaque année de l'État et de la CNRACL, et la moyenne de
    leurs parts à la condition ; les liquidants et les retraités de 2024 du
    régime général, et la décote de ses liquidants (``decotes``, celles de
    ``grille_large.proratisations``, comme ``controle_eacr.population``) ; les
    retraités de 2020, sexe par sexe."""
    def affiliation(c) -> str:
        return par_code[c.code].cas.affiliation

    def drapeau(c) -> bool:
        return surcotee(par_code[c.code], c.generation)

    du_flux = lots.get(M.ANNEE_EACR, [])
    sortie: dict = {}
    for nom, affiliations in CAISSES.items():
        def siennes(c, affiliations=affiliations) -> bool:
            return affiliation(c) in affiliations

        liquidants = {str(annee): parts_des_liquidants(lot, siennes, par_code, conditions)
                      for annee, lot in sorted(lots.items()) if annee in ANNEES_DES_LIQUIDANTS}
        valeurs = [p["condition"] for p in liquidants.values() if p["condition"] is not None]
        sortie[nom] = {
            "retraites_2024": part(du_flux, siennes, drapeau),
            "liquidants": liquidants,
            "liquidants_moyenne": somme_ordonnee(valeurs) / len(valeurs) if valeurs else None,
        }

    def du_regime_general(c) -> bool:
        return par_code[c.code].groupe == REGIME_GENERAL

    sortie["regime_general"] = {
        "liquidants_2024": parts_des_liquidants(du_flux, du_regime_general, par_code,
                                                conditions),
        "croisement_2024": croisement(du_flux, du_regime_general, par_code, conditions),
        "retraites_2024": part(du_flux, du_regime_general, drapeau),
        "decote_liquidants_2024": part(
            du_flux, lambda c: c.nouvelle and du_regime_general(c),
            lambda c: decotes.get((c.code, c.generation), (0, False, 0, False))[3]),
    }
    stock = lots.get(ANNEE_DU_STOCK, [])
    debut, fin = TRANCHE_DU_STOCK
    sexes = {}
    for sexe in ("F", "H"):
        def du_sexe(c, sexe=sexe) -> bool:
            return par_code[c.code].cas.sexe == sexe

        sexes[sexe] = {
            "surcote": part(stock, du_sexe, drapeau),
            f"{debut}_{fin}": part(stock, lambda c: du_sexe(c) and debut <= c.age <= fin,
                                   drapeau),
            "fonctionnaires_parmi_surcotes": part(
                stock, lambda c: du_sexe(c) and drapeau(c),
                lambda c: affiliation(c) in FONCTIONNAIRES_CIVILS),
        }
    sortie[f"retraites_{ANNEE_DU_STOCK}"] = sexes
    return sortie


def sources(temoin: dict) -> dict:
    """Ce que l'EACR publie en regard (``tests/temoins/drees_eacr_tables_2026.json``) :
    la part des liquidants et des retraités de la Cnav et des civils de l'État
    partis avec une surcote (table H), celle des liquidants de la Cnav de plus
    de 67 ans (table B)."""
    def de_la_table_h(caisse: str, champ: str, annee: int, condition: str = "surcote"):
        for c in M.conditions_publiees(temoin, annee):
            if (c.caisse, c.champ) == (caisse, champ):
                return getattr(c, condition)
        return None

    par_age = temoin["liquidants_par_age"]["series"][CNAV]
    apres_67 = [effectif for age, effectif in par_age.items()
                if age.startswith(">") or (age.isdigit() and int(age) > 67)]
    return {
        "cnav": {"liquidants_2024": de_la_table_h(CNAV, "flux", M.ANNEE_EACR),
                 "retraites_2024": de_la_table_h(CNAV, "stock", M.ANNEE_EACR),
                 "decote_liquidants_2024": de_la_table_h(CNAV, "flux", M.ANNEE_EACR, "decote"),
                 "liquidants_2024_de_68_ans_et_plus":
                     somme_ordonnee(apres_67) / par_age["Ensemble"]},
        "etat": {"retraites_2024": de_la_table_h(ETAT, "stock", M.ANNEE_EACR),
                 "liquidants": {str(annee): de_la_table_h(ETAT, "flux", annee)
                                for annee in ANNEES_DES_LIQUIDANTS}},
    }


@contextmanager
def constante_posee(nom: str, valeur: bool):
    """La constante ``nom`` de ``grille_large.py`` posée à ``valeur`` le temps du
    bloc, puis rendue."""
    ancienne = getattr(G, nom)
    if not isinstance(ancienne, bool):
        raise ValueError(f"{nom} n'est pas une constante vraie ou fausse de grille_large.py")
    setattr(G, nom, valeur)
    try:
        yield
    finally:
        setattr(G, nom, ancienne)


def construire(grille: str, parametres: Parametres, constante: str,
               allumee: bool) -> list[G.Variante]:
    """La grille ``grille`` — la population, comme ``grille_large.mesurer`` la
    construit, ou celle de la page —, la constante allumée ou éteinte."""
    with constante_posee(constante, allumee):
        if grille == "reference":
            return G.reference()
        racine = parametres.racine_donnees
        _, valeurs = G.centiles(racine)
        return G.grille("population", Simulateur(parametres).effectifs, G.eir(racine),
                        G.multiplicateurs(valeurs))


def cohortes_brutes(tetes: G.GrilleEnTetes, annee: int) -> list[M.Cohorte]:
    """Les cohortes de la grille en ``annee`` (``controle_eacr.cohortes``), sans
    les parts des générations, que chaque pesée leur donne."""
    return M.cohortes(tetes.pensionnes, tetes.poids(annee), tetes.population,
                      tetes.revalorisation,
                      tetes.macro.coefficient_prix(tetes.annee_euros, annee), annee)


def pesees(lot: list[M.Cohorte], tetes: G.GrilleEnTetes, annee: int) -> list[M.Cohorte]:
    """Les cohortes, chacune pesée de ce que son année de naissance donne au
    poids de son cas type (``GrilleEnTetes.part_de``), comme
    ``controle_eacr.cohortes_de_la_population``."""
    return [replace(c, tetes=c.tetes * tetes.part_de(c.code, annee - c.age)) for c in lot]


def mesurer(grille: str = "population", constante: str = "SURCOTE_SELON_LA_GENERATION",
            processus: int = 1, parametres: Parametres | None = None) -> dict:
    """La mesure entière : les deux pesées d'une même simulation, et les
    sources en regard."""
    debut = time.time()
    parametres = parametres if parametres is not None else Parametres()
    racine = parametres.racine_donnees
    grilles = {"version": construire(grille, parametres, constante, True),
               "eteinte": construire(grille, parametres, constante, False)}
    version = grilles["version"]
    if ([v.cas for v in grilles["eteinte"]] != [v.cas for v in version]
            or [v.retraites for v in grilles["eteinte"]] != [v.retraites for v in version]):
        raise ValueError(f"{constante} change les cas types ou leurs poids : une même "
                         "simulation ne sert pas les deux pesées")
    tetes = G.en_tetes(parametres, version, processus, alleges=True)
    par_code = {v.cas.code: v for v in version}

    def gardee(annee: int, c: M.Cohorte) -> bool:
        if annee in (ANNEE_DU_STOCK, M.ANNEE_EACR):
            return True
        return c.nouvelle and par_code[c.code].cas.affiliation in FONCTIONNAIRES_CIVILS

    annees = sorted({ANNEE_DU_STOCK, M.ANNEE_EACR, *ANNEES_DES_LIQUIDANTS})
    brutes = {annee: [c for c in cohortes_brutes(tetes, annee) if gardee(annee, c)]
              for annee in annees}
    cas_par_code = {cas.code: cas for cas in tetes.cas_types}
    couples = {(cas_par_code[c.code], c.generation)
               for annee, lot in brutes.items() for c in lot if c.nouvelle
               and (par_code[c.code].cas.affiliation in FONCTIONNAIRES_CIVILS
                    or (annee == M.ANNEE_EACR and par_code[c.code].groupe == REGIME_GENERAL))}
    conditions = {(code, generation): (age, condition) for code, generation, age, condition
                  in G._par_morceaux(G._conditions, parametres, couples, processus)}
    decotes = G.proratisations(
        parametres, {(par_code[c.code].cas, c.generation) for c in brutes[M.ANNEE_EACR]
                     if par_code[c.code].groupe == REGIME_GENERAL}, processus)
    temoin = json.loads(E.TEMOIN.read_text(encoding="utf-8"))
    publies = G.departs_publies(racine)
    source = G.eir(racine)
    residence = G.ResidenceRetraites(racine, source.millesime)
    distributions = {sexe: G.DistributionPensions(racine, sexe, source.millesime, "france")
                     for sexe in G.SEXES}
    resultat: dict = {"grille": grille, "constante": constante, "cas_types": len(version),
                      "couples": len(tetes.pensionnes), "echecs": dict(tetes.echecs),
                      "conditions": {"couples": len(couples), "lues": len(conditions)},
                      "sources": sources(temoin), "pesees": {}}
    for nom, variantes in grilles.items():
        pesee = replace(tetes, parts={v.cas.code: v.parts_des_generations for v in variantes
                                      if v.parts_des_generations})
        lots = {annee: pesees(lot, pesee, annee) for annee, lot in brutes.items()}
        mesure = parts_de_la_pesee(lots, par_code, conditions, decotes)
        eacr = E.mesure(lots[M.ANNEE_EACR], temoin)
        mesure["liquidants_2024"] = {
            "par_age": {cle: valeurs["grille"] for cle, valeurs in eacr["flux"].items()},
            "age_moyen": eacr["age_moyen"]["grille"]}
        du_regime_general = [c for c in lots[M.ANNEE_EACR]
                             if par_code[c.code].groupe == REGIME_GENERAL]
        mesure["regime_general"]["liquidants_2024_par_age"] = M.parts(
            M.grille_par_age(du_regime_general))
        mesure["departs"] = G.departs(parametres, pesee, publies, processus)
        mesure["distribution_2020"] = G.confronter(pesee.pensions(source.millesime), residence,
                                                   distributions)
        resultat["pesees"][nom] = mesure
        if nom == "version":
            resultat["sources"]["eacr_tous_regimes"] = {
                "liquidants_2024_par_age": {cle: valeurs["eacr"]
                                            for cle, valeurs in eacr["flux"].items()},
                "age_moyen": eacr["age_moyen"]["eacr"]}
    resultat["secondes"] = round(time.time() - debut, 1)
    return resultat


# -- l'impression ----------------------------------------------------------------

def _pc(valeur: float | None) -> str:
    return "—" if valeur is None else f"{100 * valeur:.2f}".replace(".", ",")


def _virgule(valeur: float, decimales: int) -> str:
    return f"{valeur:.{decimales}f}".replace(".", ",")


def _ligne(intitule: str, source: float | None, eteinte, version) -> str:
    return f"| {intitule} | {_pc(source)} | {_pc(eteinte)} | {_pc(version)} |"


def imprimer(resultat: dict) -> None:
    eteinte, version = resultat["pesees"]["eteinte"], resultat["pesees"]["version"]
    sources_ = resultat["sources"]
    print(f"Grille « {resultat['grille']} », {resultat['cas_types']} cas types, "
          f"{resultat['couples']} couples, échecs {resultat['echecs']} ; constante "
          f"{resultat['constante']} ; {resultat['secondes']} s.")
    print()
    print("Les départs, en part des départs déjà pris à l'âge où l'enquête voit sa "
          "génération ; la génération 1955 de la grille jugée sur les nés en 1953 de l'EIR.")
    print()
    print("| | EIR | éteinte | version |")
    print("|---|---|---|---|")
    for generation in ("1955", "1950"):
        for sexe in ("ensemble", "F", "H"):
            if sexe not in version["departs"].get(generation, {}):
                continue
            e, v = eteinte["departs"][generation][sexe], version["departs"][generation][sexe]
            print(_ligne(f"{sexe}, {generation}, surcote", v["conditions"]["surcote"][1],
                         e["conditions"]["surcote"][0], v["conditions"]["surcote"][0]))
        for sexe in ("ensemble", "F"):
            if sexe not in version["departs"].get(generation, {}):
                continue
            e, v = eteinte["departs"][generation][sexe], version["departs"][generation][sexe]
            for place in ("age_legal", "entre"):
                print(_ligne(f"{sexe}, {generation}, {place}", v["positions"][place][1],
                             e["positions"][place][0], v["positions"][place][0]))
    print()
    print("Les fonctionnaires civils, le régime général et les retraités : la source est "
          "l'EACR (tables H, B et C), « — » où le script n'en lit pas.")
    print()
    print("| | source | éteinte | version |")
    print("|---|---|---|---|")
    for nom, intitule in (("etat", "État"), ("cnracl", "CNRACL")):
        e, v = eteinte[nom], version[nom]
        for annee in map(str, ANNEES_DES_LIQUIDANTS):
            publie = sources_["etat"]["liquidants"][annee] if nom == "etat" else None
            print(_ligne(f"{intitule}, liquidants de {annee}, à la condition", publie,
                         e["liquidants"][annee]["condition"],
                         v["liquidants"][annee]["condition"]))
            print(_ligne(f"{intitule}, liquidants de {annee}, au drapeau", None,
                         e["liquidants"][annee]["drapeau"], v["liquidants"][annee]["drapeau"]))
        print(_ligne(f"{intitule}, liquidants, moyenne de 2020 à 2025", None,
                     e["liquidants_moyenne"], v["liquidants_moyenne"]))
        print(_ligne(f"{intitule}, retraités de 2024", sources_["etat"]["retraites_2024"]
                     if nom == "etat" else None, e["retraites_2024"], v["retraites_2024"]))
    e, v = eteinte["regime_general"], version["regime_general"]
    for compte in ("condition", "drapeau", "inconnues"):
        print(_ligne(f"régime général, liquidants de 2024, {compte}",
                     sources_["cnav"]["liquidants_2024"] if compte != "inconnues" else None,
                     e["liquidants_2024"][compte], v["liquidants_2024"][compte]))
    print(_ligne("régime général, retraités de 2024", sources_["cnav"]["retraites_2024"],
                 e["retraites_2024"], v["retraites_2024"]))
    print(_ligne("régime général, liquidants de 2024, décote",
                 sources_["cnav"]["decote_liquidants_2024"], e["decote_liquidants_2024"],
                 v["decote_liquidants_2024"]))
    print(_ligne("régime général, liquidants de 2024 de 68 ans et plus",
                 sources_["cnav"]["liquidants_2024_de_68_ans_et_plus"],
                 e["liquidants_2024_par_age"].get("68_plus", 0.0),
                 v["liquidants_2024_par_age"].get("68_plus", 0.0)))
    for cote in ("drapeau", "sans_drapeau"):
        for classe in sorted(set(e["croisement_2024"][cote]) | set(v["croisement_2024"][cote])):
            print(_ligne(f"régime général, liquidants de 2024, {cote}, {classe}", None,
                         e["croisement_2024"][cote].get(classe),
                         v["croisement_2024"][cote].get(classe)))
    stock = f"retraites_{ANNEE_DU_STOCK}"
    debut, fin = TRANCHE_DU_STOCK
    for sexe in ("F", "H"):
        e, v = eteinte[stock][sexe], version[stock][sexe]
        for cle, intitule in (("surcote", "surcote"),
                              (f"{debut}_{fin}", f"de {debut} à {fin} ans"),
                              ("fonctionnaires_parmi_surcotes",
                               "fonctionnaires civils parmi les surcotés")):
            print(_ligne(f"retraités de {ANNEE_DU_STOCK}, {sexe}, {intitule}", None,
                         e[cle], v[cle]))
    publie = sources_["eacr_tous_regimes"]
    e, v = eteinte["liquidants_2024"], version["liquidants_2024"]
    for cle, intitule in (("62", "à 62 ans"), ("67", "à 67 ans"),
                          ("68_plus", "à 68 ans et plus")):
        print(_ligne(f"liquidants de 2024 partis {intitule}",
                     publie["liquidants_2024_par_age"][cle], e["par_age"].get(cle),
                     v["par_age"].get(cle)))
    print(f"| âge moyen des liquidants de 2024 | {_virgule(publie['age_moyen'], 2)} | "
          f"{_virgule(e['age_moyen'], 2)} | {_virgule(v['age_moyen'], 2)} |")
    for sexe in ("F", "H"):
        e = eteinte["distribution_2020"].get(sexe)
        v = version["distribution_2020"].get(sexe)
        if not (e and v):
            continue
        print(f"| pension moyenne de {ANNEE_DU_STOCK}, {sexe}, € par mois | "
              f"{v['moyenne_eir']:.0f} | {e['moyenne']:.0f} | {v['moyenne']:.0f} |")
        print(f"| écart de Kolmogorov, {sexe}, points, à la borne | — | "
              f"{_virgule(100 * e['kolmogorov'], 1)} à {e['borne_kolmogorov']:.0f} | "
              f"{_virgule(100 * v['kolmogorov'], 1)} à {v['borne_kolmogorov']:.0f} |")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--grille", choices=("population", "reference"), default="population",
                           help="la population (défaut), ou la grille de la page, cas court")
    analyseur.add_argument("--constante", default="SURCOTE_SELON_LA_GENERATION",
                           help="la constante de grille_large.py qui sépare les deux pesées")
    analyseur.add_argument("--processus", type=int, default=G.processus_par_defaut(),
                           help="cœurs sur lesquels simuler la grille")
    analyseur.add_argument("--json", type=Path, help="écrit la mesure dans ce fichier")
    arguments = analyseur.parse_args(argv)

    resultat = mesurer(arguments.grille, arguments.constante, arguments.processus)
    imprimer(resultat)
    if arguments.json:
        arguments.json.write_text(json.dumps(resultat, ensure_ascii=False, indent=1),
                                  encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
