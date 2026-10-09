"""Le scénario 1 confronté à Destinie 2, le modèle de l'INSEE, exécuté à part.

Destinie 2 est la seconde implémentation du droit la plus indépendante du
registre (`data/reference/referents.yaml`, `destinie_2`) : écrite par l'INSEE,
paramétrée sur ses propres feuilles, la seule qui porte la réversion du régime
général entière. Son code est sous GPL : il s'exécute À PART, dans R
(`scripts/fetch/destinie_2.py` et `destinie_2.R`), et seules ses sorties
entrent au dépôt, figées dans `tests/temoins/destinie_2.json` avec leur
origine, leur licence, le commit et la législation retenue — la plus récente
qu'il porte, la loi du 14 avril 2023, sans celle du 30 décembre 2025.

**Ce test n'exécute pas Destinie.** Il rejoue chaque cas du témoin dans le
scénario 1 — la requête du simulateur est dans le témoin, carrière en euros de
chaque année, enfants, conjoint, décès —, et confronte, régime par régime : la
durée d'assurance, majoration pour enfants comprise ; le taux ; la pension de
droit direct ; les majorations de 10 % pour trois enfants ; la réversion servie
l'année du décès. Le seul test qui exige R, `test_destinie_rejoue_le_temoin`,
se saute sans lui.

Chaque quantité concorde à sa tolérance, ou son écart est DÉCLARÉ, cas par
cas, avec sa cause et sa borne (`ECARTS`) : un écart inexpliqué fait échouer
le test, un écart déclaré qui bouge aussi, et un écart déclaré qui n'en est
plus un également. Ce que la première exécution a montré, le 5 octobre 2026 :

* **Concordent** — les durées, la majoration de durée d'assurance de la mère
  (vingt-quatre trimestres pour trois enfants, rien au père) et la
  bonification de la mère fonctionnaire, qui compte à la liquidation ; le
  taux plein à l'âge d'ouverture, sous la loi de 2023 aussi ; la pension du
  régime général à 0,2 % près, la pension civile à 0,6 % ; le minimum
  contributif daté de l'étape 15 de l'action 138, au centime pour le majoré
  de 2018 (le dépôt le servait 3,9 % trop haut la veille de cette étape) ; les
  majorations de 10 % du régime général et de la pension civile ; la
  réversion de 54 % au régime général et de 50 % dans la fonction publique ;
  la réversion de 60 % de l'Agirc-Arrco, sur les points de chacun.
* **Contre le dépôt** — le minimum de réversion, la majoration de 11,1 % et
  celle de 10 % de la survivante de trois enfants, que la fiche `reversion`
  déclare et n'applique pas ; la réversion de l'Agirc-Arrco attend
  cinquante-cinq ans quand deux enfants à charge la doivent dès le décès,
  écart que la fiche déclare.
* **Contre Destinie** — sa chaîne de coefficients de revalorisation des
  salaires est décalée d'un an (SAM de 2024 trop haut de 3,75 %) ; il prête
  trois trimestres de surcote au né d'octobre, avant son âge d'ouverture ; il
  compte la réversion de l'Agirc-Arrco dans les ressources sous le plafond ;
  il lève l'âge de cinquante-cinq ans au régime général pour deux enfants à
  charge ; sa valeur du point de 2024 est une projection ; il sert la valeur
  du point du 31 décembre de l'année du départ, et le dépôt celle du jour
  depuis l'étape 20 de l'action 138 (−0,6 % en février 2018).
* **Une convention, à trancher** — Destinie acquiert les points de l'Arrco et
  de l'Agirc aux taux contractuels MOYENS des entreprises, le dépôt aux taux
  minimaux obligatoires : 15 à 26 % de points de plus chez lui. La série des
  valeurs du point, elle, est la même des deux côtés.
* **Ouvert** — Destinie reverse la majoration pour enfants de l'Agirc-Arrco du
  défunt avec sa retraite, le dépôt non ; l'accord reste à lire sur ce point.

Le 7 octobre 2026 (action 138, étape 4), le scénario 1 sert le minimum de
réversion, la majoration de 11,1 % et celle de 10 % de la survivante de trois
enfants : les deux premiers concordent au centime, la troisième à l'écart près
de la base que Destinie réverse (−0,6 %, déclaré).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path

import pytest

from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.saisie import Saisie

RACINE = Path(__file__).resolve().parents[1]
TEMOIN = RACINE / "tests" / "temoins" / "destinie_2.json"
SCRIPT = RACINE / "scripts" / "fetch" / "destinie_2.py"

#: Les familles de l'Agirc-Arrco : ce que le dépôt sert en régimes distincts,
#: et ce que Destinie écrit en pension et en points.
COMPLEMENTAIRES = {
    "arrco": (("arrco", "arrco_tranche_2"), "pension_ar", "points_arrco"),
    "agirc": (("agirc", "agirc_tranche_c"), "pension_ag", "points_agirc"),
    "agirc_arrco": (("agirc_arrco", "agirc_arrco_tranche_2"), "pension_ag_ar",
                    "points_agirc_arrco"),
}
REGIMES_COMPLEMENTAIRES = {r for regimes, _, _ in COMPLEMENTAIRES.values() for r in regimes}
POINTS = re.compile(r"([\d,]+(?:\.\d+)?) points × valeur de service")

#: La tolérance de chaque quantité, relative (sauf les trimestres et le taux,
#: qui se comptent).
#:
#: * Le régime général, 0,5 % : le dépôt sert la colonne de coefficients de
#:   la Cnav, Destinie les enchaîne de ses paramètres ; 0,16 % pour un départ
#:   de 2018. La majoration de 10 % suit la pension.
#: * La pension civile, 1 % : le dépôt ramène le revenu de la dernière année
#:   au départ par le point d'indice du 1er janvier de cette année-là, Destinie
#:   par celui de la fin d'année ; un point relevé en février 2017 fait 0,6 %
#:   entre les deux, pour un départ de 2018.
#: * La valeur du point de l'Agirc-Arrco, 0,1 % : la même série des deux
#:   côtés, que Destinie lit au 31 décembre et le dépôt au jour du départ
#:   (VALEUR_DU_JOUR, déclarée cas par cas).
#: * La réversion du régime général, 0,5 % : 54 % de la même pension, menée au
#:   décès par des revalorisations voisines (celle de 2020 est une moyenne chez
#:   Destinie).
TOLERANCES = {
    "trimestres": 0.0,
    "taux": 1e-9,
    "regime_general": 0.005,
    "majoration_regime_general": 0.005,
    "fonction_publique": 0.01,
    "majoration_fonction_publique": 0.01,
    "valeur_point_arrco": 0.001,
    "valeur_point_agirc": 0.001,
    "valeur_point_agirc_arrco": 0.001,
    # Le taux de majoration pour enfants de l'Agirc-Arrco, rapporté à la
    # retraite de chacun : deux dixièmes de point.
    "majoration_complementaires": 0.002,
    "reversion_regime_general": 0.005,
    "reversion_fonction_publique": 0.01,
    # La réversion de 60 % se compare à la retraite du défunt : leurs écarts
    # au dépôt sont les mêmes à 0,5 % près.
    "reversion_complementaires_sur_retraite": 0.005,
}

#: Les taux contractuels : Destinie acquiert les points aux taux moyens des
#: entreprises (`ParamRetrComp` : 5,42 % à l'Arrco de 1970 à 1990, 13,9 % à
#: l'Agirc vers 1980, 6,61 % depuis 2015, même à l'Agirc-Arrco unifiée), le
#: dépôt aux taux minimaux obligatoires (4 %, 8 %, 6,2 % ; fiches `arrco` et
#: `agirc`). Une convention de cas type, que le propriétaire tranchera
#: (registre, `destinie_2`) ; l'écart des points se borne par famille.
TAUX_CONTRACTUELS = ("Destinie acquiert les points aux taux contractuels moyens des "
                     "entreprises, le dépôt aux taux minimaux obligatoires")
ECARTS_DES_POINTS = {
    "arrco": (-0.30, -0.10),
    "agirc": (-0.30, -0.15),
    "agirc_arrco": (-0.10, -0.03),
}

#: Les écarts déclarés : (cas, quantité) → (bas, haut, cause). L'écart est
#: relatif, (dépôt − Destinie) / Destinie, sauf pour la majoration de
#: l'Agirc-Arrco, où c'est la différence des taux de majoration (dépôt moins
#: Destinie, chacun rapporté à sa propre retraite).
SAM_2024 = ("Destinie décale d'un an la chaîne des coefficients de revalorisation des "
            "salaires (`DroitsRetr::SalBase` part du coefficient de l'année du départ) : "
            "son SAM de 2024 dépasse de 3,75 % la colonne de la Cnav du 1er janvier 2024")
POINT_2024 = ("la valeur du point de 2024 de Destinie (1,4463 €) est une projection des "
              "hypothèses du COR de 2023, quand la caisse a fixé 1,4386 €")
VALEUR_DU_JOUR = ("Destinie sert la valeur de service du 31 décembre de l'année du départ, "
                  "sa série annuelle ; la caisse — et le dépôt depuis l'étape 20 de "
                  "l'action 138 — celle du jour, « à cette même date » (circulaire "
                  "Agirc-Arrco 2020-02-DRJ, sur l'article 92 de l'accord du 17 novembre "
                  "2017) : 1,2513 € et non 1,2588 € à l'Arrco pour un départ de février "
                  "2018, 0,4352 € et non 0,4378 € à l'Agirc, 1,4159 € avant novembre 2024 ; "
                  "l'écart est celui de Destinie (registre)")
REVERSION_DU_JOUR = ("la retraite du défunt, liquidée à la valeur du jour (−0,6 %, "
                     + VALEUR_DU_JOUR + "), quand sa réversion part de la même valeur "
                     "des deux côtés, celle de l'année du décès")
MAJORATION_ARRCO = ("les points de l'Arrco d'avant 1999 valent 10 % au dépôt (accord du 17 "
                    "novembre 2017, art. 94, fiche majoration_enfants_agirc_arrco), 5 % chez "
                    "Destinie, qui sert 5 % à tous les points d'avant 2012")
ECARTS = {
    ("loi_2023_salaire_moyen", "regime_general"): (-0.040, -0.032, SAM_2024),
    ("rg_ne_en_octobre", "regime_general"): (-0.076, -0.066, SAM_2024 + ", et trois "
                                             "trimestres de surcote (voir le taux)"),
    ("rg_ne_en_octobre", "taux"): (
        -0.0362, -0.0360,
        "Destinie compte la surcote de l'année civile où tombe l'âge d'ouverture sans "
        "regarder le mois de naissance (`DroitsRetr::DecoteSurcote`) : trois trimestres "
        "pour le né d'octobre parti à 62 ans et 3 mois, qu'aucun trimestre ne suit "
        "(L. 351-1-2 : des trimestres « accomplis après l'âge »)"),
    ("loi_2023_salaire_moyen", "valeur_point_arrco"): (
        -0.0213, -0.0207, POINT_2024 + " ; et " + VALEUR_DU_JOUR),
    ("loi_2023_salaire_moyen", "valeur_point_agirc_arrco"): (
        -0.0213, -0.0207, POINT_2024 + " ; et " + VALEUR_DU_JOUR),
    ("rg_ne_en_octobre", "valeur_point_arrco"): (
        -0.0213, -0.0207, POINT_2024 + " ; et " + VALEUR_DU_JOUR),
    ("rg_ne_en_octobre", "valeur_point_agirc_arrco"): (
        -0.0213, -0.0207, POINT_2024 + " ; et " + VALEUR_DU_JOUR),
    **{(cas, "valeur_point_arrco"): (-0.0062, -0.0058, VALEUR_DU_JOUR) for cas in (
        "rg_bas_salaire", "rg_cadre", "rg_mere_trois_enfants", "rg_pere_trois_enfants",
        "rg_salaire_moyen", "reversion_rg", "reversion_plafond", "reversion_trois_enfants",
        "reversion_jeune_deux_enfants")},
    ("rg_cadre", "valeur_point_agirc"): (-0.0062, -0.0058, VALEUR_DU_JOUR),
    **{(cas, "reversion_complementaires_sur_retraite"): (0.0058, 0.0062, REVERSION_DU_JOUR)
       for cas in ("reversion_rg", "reversion_plafond", "reversion_jeune_deux_enfants")},
    ("rg_mere_trois_enfants", "majoration_complementaires"): (0.015, 0.030, MAJORATION_ARRCO),
    ("rg_pere_trois_enfants", "majoration_complementaires"): (0.015, 0.030, MAJORATION_ARRCO),
    ("reversion_trois_enfants", "majoration_complementaires"): (0.015, 0.030,
                                                                MAJORATION_ARRCO),
    ("reversion_jeune_deux_enfants", "majoration_complementaires"): (
        0.099, 0.101,
        "le défunt part en 2018 avec deux enfants de moins de dix-huit ans : l'Arrco et "
        "l'Agirc majorent ses droits de 5 % par enfant à charge (annexe A, article 17, et "
        "annexe I, article 6 bis ; fiche majoration_enfants_a_charge_agirc_arrco), que "
        "Destinie ne sert pas ; la réversion, elle, ne la reprend pas (article 109 de "
        "l'accord du 17 novembre 2017)"),
    ("reversion_fonctionnaire", "reversion_fonction_publique"): (
        0.007, 0.013,
        "la pension civile du défunt (+0,6 %, le point d'indice du 1er janvier) et sa "
        "revalorisation de 2020, de 1 % pour une pension de moins de 2 000 € par mois "
        "au dépôt, de 0,58 % en moyenne chez Destinie"),
    ("reversion_trois_enfants", "reversion_regime_general"): (
        -0.0070, -0.0045,
        "la base de la réversion : Destinie la prend sur la pension du défunt "
        "revalorisée, moins sa majoration pour enfants NON revalorisée (`src/Reversion.cpp`, "
        "`pension_rg - liq->majo_3enf_rg`), qui excède de 0,6 % en cinq ans celle du "
        "dépôt, la pension sans sa majoration, revalorisée ; la majoration de 10 % de la "
        "survivante de trois enfants (L. 353-1, R. 353-2), elle, concorde depuis le "
        "7 octobre 2026 ; l'écart est celui de Destinie (registre)"),
    ("reversion_plafond", "reversion_regime_general"): (
        0.13, 0.17,
        "Destinie compte la réversion de l'Agirc-Arrco dans les ressources sous le "
        "plafond, que R. 353-1 exclut, et écrête ; le dépôt ne l'y compte pas"),
    ("reversion_jeune_deux_enfants", "reversion_regime_general"): (
        -1.0, -1.0,
        "Destinie sert la réversion du régime général à 48 ans pour deux enfants à "
        "charge ; R. 353-1 attend cinquante-cinq ans, et le dépôt aussi : l'écart est "
        "celui de Destinie (registre)"),
    ("reversion_trois_enfants", "reversion_complementaires_sur_retraite"): (
        0.065, 0.085,
        "Destinie reverse la majoration pour enfants du défunt avec sa retraite "
        "Agirc-Arrco, au taux de 60 % ; l'accord du 17 novembre 2017 la dit "
        "« réversible au taux de 100% » (article 109), et le dépôt le suit depuis le "
        "5 octobre 2026 : l'écart est celui de Destinie (registre)"),
}


# ---------------------------------------------------------------------------
# Les mesures des deux côtés
# ---------------------------------------------------------------------------

def _points(detail: str) -> float:
    trouve = POINTS.search(detail)
    return float(trouve.group(1).replace(",", "")) if trouve else 0.0


def mesures_du_depot(contexte: Contexte, requete: dict) -> dict[str, float]:
    """Ce que le scénario 1 sert à la requête du témoin : brut annuel, en euros de
    la liquidation ; la réversion, en euros de l'année du décès, quand sa date
    d'effet tombe cette année-là."""
    comparaison = contexte.simuler(Saisie.depuis_requete(requete))
    actuel = comparaison.actuel
    par_regime: dict[str, float] = {}
    points: dict[str, float] = {}
    for pension in actuel.pensions_par_regime:
        par_regime[pension.regime] = par_regime.get(pension.regime, 0.0) + pension.montant
        points[pension.regime] = points.get(pension.regime, 0.0) + _points(pension.detail)
    majorations: dict[str, float] = {}
    for avantage in actuel.avantages_appliques:
        if avantage.code == "majoration_enfants":
            for regime, part in avantage.par_regime:
                majorations[regime] = majorations.get(regime, 0.0) + part

    def somme(table, regimes):
        return sum(v for k, v in table.items() if k in regimes)

    fonction_publique = {k for k in par_regime if k.startswith("fonction_publique")}
    mesures = {
        "trimestres": float(actuel.trimestres_valides),
        "taux": actuel.taux_liquidation,
        "regime_general": par_regime.get("regime_general", 0.0),
        "majoration_regime_general": majorations.get("regime_general", 0.0),
        "fonction_publique": somme(par_regime, fonction_publique),
        "majoration_fonction_publique": somme(majorations, {
            k for k in majorations if k.startswith("fonction_publique")}),
        "complementaires": somme(par_regime, REGIMES_COMPLEMENTAIRES),
        "majoration_complementaires": somme(majorations, REGIMES_COMPLEMENTAIRES),
    }
    for famille, (regimes, _, _) in COMPLEMENTAIRES.items():
        mesures[f"retraite_{famille}"] = somme(par_regime, regimes)
        mesures[f"points_{famille}"] = somme(points, regimes)
    reversion = comparaison.reversion
    if reversion is not None:
        servies = [ligne for ligne in reversion.regimes
                   if ligne.date_effet and int(ligne.date_effet[:4]) <= reversion.annee]
        mesures["reversion_regime_general"] = sum(
            l.montant for l in servies if l.regime == "regime_general")
        mesures["reversion_complementaires"] = sum(
            l.montant for l in servies if l.regime in REGIMES_COMPLEMENTAIRES)
        mesures["reversion_fonction_publique"] = sum(
            l.montant for l in servies if l.regime.startswith("fonction_publique"))
    return mesures


def mesures_de_destinie(cas: dict) -> dict[str, float]:
    """Les mêmes quantités, lues dans les sorties figées de Destinie : la pension
    hors majoration, la majoration à part — celle de l'Agirc-Arrco unifiée, que
    Destinie n'écrit pas, par l'exécution sans majorations."""
    liquidation = cas["destinie"]["liquidation"]
    sans = cas["destinie"]["sans_majoration"]
    complementaires = sum(liquidation[p] for _, p, _ in COMPLEMENTAIRES.values())
    sans_majoration = sum(sans[p] for _, p, _ in COMPLEMENTAIRES.values())
    regime_fp = liquidation["duree_fp"] > 0
    mesures = {
        "trimestres": round(liquidation["duree_tot_maj"] * 4),
        "taux": (0.75 * liquidation["tauxliq_fp"] if regime_fp
                 else 0.5 * liquidation["tauxliq_rg"]),
        "regime_general": liquidation["pension_rg"] - liquidation["majo_3enf_rg"],
        "majoration_regime_general": liquidation["majo_3enf_rg"],
        "fonction_publique": liquidation["pension_fp"] - liquidation["majo_3enf_fp"],
        "majoration_fonction_publique": liquidation["majo_3enf_fp"],
        "complementaires": sans_majoration,
        "majoration_complementaires": complementaires - sans_majoration,
    }
    for famille, (_, pension, points) in COMPLEMENTAIRES.items():
        mesures[f"retraite_{famille}"] = sans[pension]
        mesures[f"points_{famille}"] = liquidation[points]
    if "survivant" in cas["destinie"]:
        servie = cas["destinie"]["survivant"] or {}
        mesures["reversion_regime_general"] = servie.get("rev_rg", 0.0)
        mesures["reversion_complementaires"] = sum(
            servie.get(c, 0.0) for c in ("rev_ar", "rev_ag", "rev_ag_ar"))
        mesures["reversion_fonction_publique"] = servie.get("rev_fp", 0.0)
    return mesures


def _relatif(depot: float, destinie: float) -> float:
    if destinie == 0:
        return 0.0 if depot == 0 else float("inf")
    return (depot - destinie) / destinie


def ecarts_du_cas(depot: dict, destinie: dict) -> dict[str, float]:
    """Chaque quantité confrontée, et son écart : relatif, sauf les trimestres
    (une différence) et la majoration de l'Agirc-Arrco (des taux)."""
    ecarts = {"trimestres": depot["trimestres"] - destinie["trimestres"],
              "taux": _relatif(depot["taux"], destinie["taux"])}
    for quantite in ("regime_general", "majoration_regime_general", "fonction_publique",
                     "majoration_fonction_publique"):
        if depot[quantite] or destinie[quantite]:
            ecarts[quantite] = _relatif(depot[quantite], destinie[quantite])
    for famille in COMPLEMENTAIRES:
        points_depot, points_destinie = depot[f"points_{famille}"], destinie[f"points_{famille}"]
        if points_depot and points_destinie:
            ecarts[f"valeur_point_{famille}"] = _relatif(
                depot[f"retraite_{famille}"] / points_depot,
                destinie[f"retraite_{famille}"] / points_destinie)
            ecarts[f"points_{famille}"] = _relatif(points_depot, points_destinie)
    if depot["majoration_complementaires"] or destinie["majoration_complementaires"]:
        ecarts["majoration_complementaires"] = (
            depot["majoration_complementaires"] / depot["complementaires"]
            - destinie["majoration_complementaires"] / destinie["complementaires"])
    if "reversion_regime_general" in destinie:
        for quantite in ("reversion_regime_general", "reversion_fonction_publique"):
            if depot.get(quantite) or destinie[quantite]:
                ecarts[quantite] = _relatif(depot.get(quantite, 0.0), destinie[quantite])
        if depot.get("reversion_complementaires") or destinie["reversion_complementaires"]:
            # La réversion de 60 % : son écart, rapporté à celui de la retraite du
            # défunt, ne garde que la règle — les points de chacun s'en vont.
            retraite = 1 + _relatif(depot["complementaires"], destinie["complementaires"])
            ecarts["reversion_complementaires_sur_retraite"] = (
                (1 + _relatif(depot.get("reversion_complementaires", 0.0),
                              destinie["reversion_complementaires"])) / retraite - 1)
    return ecarts


@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ecarts(temoin) -> dict[str, dict[str, float]]:
    contexte = Contexte()
    return {code: ecarts_du_cas(mesures_du_depot(contexte, cas["requete"]),
                                mesures_de_destinie(cas))
            for code, cas in temoin["cas"].items()}


# ---------------------------------------------------------------------------
# Le témoin
# ---------------------------------------------------------------------------

def test_le_temoin_dit_son_origine_sa_licence_et_sa_legislation(temoin):
    """Des sorties d'un code sous GPL n'entrent au dépôt qu'avec leur origine et
    leur licence (docs/architecture.md, § 3.4) ; une législation sans sa date
    ne dirait pas ce qu'on confronte."""
    assert temoin["code"] == "https://github.com/InseeFr/Destinie-2"
    assert re.fullmatch(r"[0-9a-f]{40}", temoin["commit"])
    assert "GPL-3.0" in temoin["licence"] and "ODbL" in temoin["licence"]
    assert "n'entre pas au dépôt" in temoin["origine"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", temoin["execute_le"])
    assert temoin["legislation"]["anLeg"] == 2023
    assert "30 décembre 2025" in temoin["legislation"]["dit"]
    assert temoin["environnement"]["destinie"] == temoin["version"]


def test_les_scripts_appellent_destinie_sans_le_recopier():
    """Le script R du dépôt charge le paquet installé à part et n'appelle que ses
    fonctions exportées : aucune ligne de Destinie, dont chaque fichier porte
    l'en-tête de l'INSEE, n'y entre."""
    for chemin in (SCRIPT, SCRIPT.with_suffix(".R")):
        texte = chemin.read_text(encoding="utf-8")
        assert "Institut national de la statistique et des" not in texte, chemin.name
    assert "library(destinie)" in SCRIPT.with_suffix(".R").read_text(encoding="utf-8")


def test_chaque_cas_liquide_l_annee_de_sa_requete(temoin):
    """Les deux modèles partent la même année : Destinie au taux plein, que chaque
    carrière atteint à son âge d'ouverture, le dépôt à la date de la requête."""
    for code, cas in temoin["cas"].items():
        liquidation = cas["destinie"]["liquidation"]
        assert liquidation is not None, f"{code} : Destinie n'a pas liquidé"
        assert liquidation["annee"] == int(cas["requete"]["liquidation"][:4]), code


# ---------------------------------------------------------------------------
# La confrontation
# ---------------------------------------------------------------------------

def _hors_de(quantite: str, ecart: float) -> bool:
    if quantite.startswith("points_"):
        bas, haut = ECARTS_DES_POINTS[quantite.removeprefix("points_")]
        return not bas <= ecart <= haut
    return abs(ecart) > TOLERANCES[quantite]


def test_le_scenario_1_concorde_avec_destinie_ou_son_ecart_est_explique(ecarts):
    """Chaque quantité de chaque cas : à sa tolérance, ou dans la borne de son
    écart déclaré. Les points de l'Agirc-Arrco se bornent par famille
    (`ECARTS_DES_POINTS`, les taux contractuels)."""
    ecarts_hors = []
    for code, mesures in ecarts.items():
        for quantite, ecart in mesures.items():
            declare = ECARTS.get((code, quantite))
            if declare is not None:
                bas, haut, cause = declare
                if not bas - 1e-9 <= ecart <= haut + 1e-9:
                    ecarts_hors.append(f"{code}, {quantite} : {ecart:+.4f} hors de "
                                       f"[{bas:+.4f}, {haut:+.4f}] — {cause}")
            elif quantite.startswith("points_") and _hors_de(quantite, ecart):
                bas, haut = ECARTS_DES_POINTS[quantite.removeprefix("points_")]
                ecarts_hors.append(f"{code}, {quantite} : {ecart:+.4f} hors de "
                                   f"[{bas:+.4f}, {haut:+.4f}] — {TAUX_CONTRACTUELS}")
            elif _hors_de(quantite, ecart):
                ecarts_hors.append(f"{code}, {quantite} : {ecart:+.4f}, écart non déclaré")
    assert not ecarts_hors, "\n".join(ecarts_hors)


def test_un_ecart_declare_en_est_un(ecarts):
    """Un écart déclaré qui rentre dans la tolérance n'en est plus un : la
    déclaration se retire, sans quoi elle couvrirait le prochain."""
    for (code, quantite), (_, _, cause) in ECARTS.items():
        assert code in ecarts, f"{code} : cas absent du témoin"
        assert quantite in ecarts[code], f"{code}, {quantite} : quantité non mesurée"
        assert _hors_de(quantite, ecarts[code][quantite]), (
            f"{code}, {quantite} : {ecarts[code][quantite]:+.4f}, dans la tolérance — "
            f"retirer la déclaration ({cause})")


def test_les_durees_et_les_enfants_concordent(ecarts):
    """La majoration de durée d'assurance de la mère et la bonification de la
    mère fonctionnaire, au trimestre près : les deux fiches qui attendaient
    Destinie (`majoration_duree_assurance_enfants`, `enfants_fonction_publique`)."""
    for code in ("rg_mere_trois_enfants", "rg_pere_trois_enfants", "fp_mere_deux_enfants"):
        assert ecarts[code]["trimestres"] == 0, code


# ---------------------------------------------------------------------------
# Destinie rejoué, seulement sur demande
# ---------------------------------------------------------------------------

def test_destinie_rejoue_le_temoin(temoin, tmp_path):
    """Le témoin est ce que Destinie produit : rejoué si R et Destinie 2 sont
    installés et que `DESTINIE_2` le demande (« Ubuntu » : par la WSL, « r » :
    Rscript du système). Les sorties figées suffisent à la confrontation."""
    demande = os.environ.get("DESTINIE_2")
    if not demande:
        pytest.skip("les sorties figées suffisent : Destinie 2 ne se rejoue que sur "
                    "demande (DESTINIE_2=Ubuntu ou DESTINIE_2=r), R installé")
    distribution = None if demande.lower() == "r" else demande
    if shutil.which("wsl" if distribution else "Rscript") is None:
        pytest.skip("R introuvable sur ce poste")
    sys.path.insert(0, str(SCRIPT.parent))
    import destinie_2 as script  # noqa: E402

    sortie = tmp_path / "destinie_2.json"
    script.SORTIE = sortie
    assert script.main(["--wsl", distribution or "aucune"]) == 0
    rejoue = json.loads(sortie.read_text(encoding="utf-8"))
    sans_date = lambda document: {k: v for k, v in document.items() if k != "execute_le"}
    assert sans_date(rejoue) == sans_date(temoin)
