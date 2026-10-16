#!/usr/bin/env python3
"""L'oracle au-delà des carrières simples, cinquième famille (action 153) : les
minima — le minimum garanti de la pension civile (L. 17 du code des pensions)
et le minimum contributif du régime général (L. 351-10 du code de la sécurité
sociale) —, par OpenFisca-France-Pension.

    pip install OpenFisca-France-Pension
    python scripts/fetch/openfisca_minima.py

Le frère de ``openfisca_carriere_longue_fonction_publique.py``, dont il
reprend la carrière des fonctionnaires, et de ``openfisca_regime_general.py``,
dont il reprend celle des salariés. ``tests/test_oracle.py`` confrontait déjà
le minimum garanti de l'État sur des carrières entières, à la référence près ;
celle-ci éprouve ce qu'il ne voyait pas : la CNRACL, le barème sous quinze ans,
la condition de taux plein depuis 2011 et sa minoration transitoire, et le
minimum contributif, que l'oracle ne confrontait qu'en barème
(``openfisca_minimum_contributif.py``). Sa convention suit ; le témoin la
porte, et ``tests/test_oracle_minima.py`` la vérifie avant de comparer.

LA CONVENTION DE TRADUCTION.

* **Les fonctionnaires** ont la carrière des familles d'avant : nés un
  1er janvier, entrés au 1er janvier de ``debut``, à traitement nominal
  constant et sans prime, à temps plein, continus jusqu'à la liquidation, au
  1er janvier de l'année écrite ; sédentaires, sans enfant, sans période au
  régime général. Le traitement est bas, pour que le minimum joue.
* **Les salariés** ont celle de ``openfisca_regime_general.py`` : non-cadres,
  à salaire nominal constant, quatre trimestres par an, sans enfant ; la
  carrière commence tard et la liquidation tombe à l'âge du taux plein, pour
  que la pension, proratisée, passe sous le minimum.
* **Ce qui se compare.** Le minimum garanti se lit dans sa forme, le barème :
  le rapport du minimum à sa référence, celle du dépôt — l'indice majoré gelé
  au 1er janvier 2004, revalorisé comme les pensions (L. 17) — et celle
  d'OpenFisca — l'indice au point de l'année, un écart déjà tranché
  (``tests/test_oracle.py``). Le minimum contributif se compare au centime.
* **Ce qui ne se traduit pas.** Le plafond de ressources du minimum garanti
  (L. 17, depuis le 1er juillet 2012), que la CNRACL n'applique pas faute de
  décret et qu'aucun des deux ne porte ; l'écrêtement du minimum contributif
  sur l'ensemble des pensions (L. 173-2), qu'aucun profil n'atteint ; la
  surcote du minimum contributif, déjà tranchée au registre.

Ce que la confrontation a trouvé, le 16 octobre 2026 : quatre erreurs chez
OpenFisca, aucune chez nous.

* **La CNRACL.** Son minimum garanti lit les services de la fonction publique
  de l'État (``fonction_publique_duree_de_service_effective``, écrit en dur
  dans ``cnracl_minimum_garanti``) : zéro, et aucun fonctionnaire territorial
  ou hospitalier n'a de minimum chez lui. Le décret n° 2003-1306, article 22,
  le lui sert comme à l'État.
* **L'ancien droit sous quinze ans.** Il sert à toute pension de moins de
  quinze ans le d de L. 17, la référence rapportée à la durée de la
  génération. La loi n° 2010-1330, article 45, V, garde à qui avait atteint
  l'âge d'ouverture avant 2011 l'article L. 17 « dans [sa] rédaction
  antérieure » : le c, un quinzième de 57,5 % par année.
* **La minoration transitoire.** Il n'ouvre le minimum, depuis 2011, qu'à la
  durée ou sans décote. L'âge d'annulation qui l'ouvre est minoré de neuf
  trimestres pour qui atteint l'âge d'ouverture en 2011, de sept, cinq, trois
  et un ensuite (loi n° 2010-1330, article 45, IV ; décret n° 2010-1744,
  article 3).
* **La durée corrigée.** Il proratise le minimum contributif sur la durée
  accomplie, sans la majoration de 2,5 % par trimestre d'ajournement au-delà
  de l'âge du taux plein (R. 351-7), que la Cnav y retient : « la durée
  d'assurance retenue par le régime général pour le calcul de la pension
  c'est-à-dire y compris, la durée d'assurance corrigée » (circulaire n° 8/89,
  point 3).

Le fichier produit, ``tests/temoins/openfisca_minima.json``, est VERSIONNÉ :
le test rejoue la confrontation sur un dépôt fraîchement cloné, sans
installer OpenFisca.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import openfisca_temps_partiel_et_parents as frere  # noqa: E402

SORTIE = Path("tests/temoins/openfisca_minima.json")

REGIME_GENERAL = "regime_general"

#: La convention, telle que le témoin la porte : chaque entrée d'OpenFisca, et
#: ce qu'elle reçoit du profil du dépôt.
CONVENTION = {
    "date_de_naissance": "le 1er janvier de `naissance`",
    "sexe": "faux (`sexe` H)",
    "liquidation_date": "le 1er janvier de `liquidation`, dans le régime du profil",
    "salaire_de_base": "le traitement ou le salaire, chaque année de `debut` à "
                       "`liquidation` exclue",
    "duree_de_service_cotisee_annuelle": "4 trimestres chaque année, aux "
                                         "fonctionnaires",
    "categorie_salarie": "titulaire de l'État ou de la territoriale, ou "
                         "non-cadre du privé",
    "taux_de_prime": "0",
    "nombre_enfants": "0",
    "reference": (
        "Le minimum garanti se compare rapporté à sa référence : chez OpenFisca, "
        "l'indice majoré de l'année au point d'indice du 1er janvier de "
        "`liquidation` ; au dépôt, l'indice majoré 227 au 1er janvier 2004, "
        "revalorisé comme les pensions."
    ),
    "non_traduit": (
        "Le plafond de ressources du minimum garanti, que ni l'un ni l'autre ne "
        "porte ; l'écrêtement du minimum contributif sur l'ensemble des "
        "pensions, qu'aucun profil n'atteint ; la surcote du minimum contributif, "
        "tranchée au registre."
    ),
}

#: Profils confrontés. ``regle`` dit ce que chacun éprouve ; ``objet``, en clair.
PROFILS: tuple[dict, ...] = (
    {"code": "etat_1948_vingt_ans_en_2008", "regle": "bareme",
     "regime": "fonction_publique_etat", "naissance": 1948, "debut": 1988,
     "liquidation": 2008, "traitement": 12000.0,
     "objet": "vingt ans de services, une décote, avant 2011 : le minimum sans "
              "condition"},
    {"code": "etat_1953_dix_huit_ans_en_2019", "regle": "bareme",
     "regime": "fonction_publique_etat", "naissance": 1953, "debut": 2001,
     "liquidation": 2019, "traitement": 15000.0,
     "objet": "dix-huit ans, parti à 66 ans sans décote : la marche de quinze "
              "à trente ans"},
    {"code": "etat_1952_quarante_ans_en_2017", "regle": "bareme",
     "regime": "fonction_publique_etat", "naissance": 1952, "debut": 1977,
     "liquidation": 2017, "traitement": 14000.0,
     "objet": "quarante ans de services : la référence entière"},
    {"code": "etat_1955_treize_ans_en_2022", "regle": "moins_de_quinze_ans",
     "regime": "fonction_publique_etat", "naissance": 1955, "debut": 2009,
     "liquidation": 2022, "traitement": 15000.0,
     "objet": "treize ans, l'âge d'ouverture atteint en 2017 : le d de L. 17, "
              "52 trimestres sur 166"},
    {"code": "cnracl_1948_vingt_ans_en_2008", "regle": "cnracl",
     "regime": "cnracl", "naissance": 1948, "debut": 1988, "liquidation": 2008,
     "traitement": 12000.0,
     "objet": "le premier profil, à la CNRACL"},
    {"code": "cnracl_1953_dix_huit_ans_en_2019", "regle": "cnracl",
     "regime": "cnracl", "naissance": 1953, "debut": 2001, "liquidation": 2019,
     "traitement": 15000.0,
     "objet": "le deuxième, à la CNRACL"},
    {"code": "cnracl_1952_quarante_ans_en_2017", "regle": "cnracl",
     "regime": "cnracl", "naissance": 1952, "debut": 1977, "liquidation": 2017,
     "traitement": 14000.0,
     "objet": "le troisième, à la CNRACL"},
    {"code": "etat_1950_treize_ans_en_2013", "regle": "ancien_droit",
     "regime": "fonction_publique_etat", "naissance": 1950, "debut": 2000,
     "liquidation": 2013, "traitement": 15000.0,
     "objet": "treize ans, l'âge d'ouverture atteint en 2010 : le c de L. 17, "
              "dans sa rédaction d'avant 2011"},
    {"code": "etat_1951_minoration_en_2012", "regle": "minoration",
     "regime": "fonction_publique_etat", "naissance": 1951, "debut": 1980,
     "liquidation": 2012, "traitement": 13000.0,
     "objet": "trente-deux ans, sept trimestres de décote, l'âge d'ouverture "
              "atteint en 2011 : l'âge d'annulation minoré de neuf trimestres"},
    {"code": "etat_1955_decote_en_2017", "regle": "condition",
     "regime": "fonction_publique_etat", "naissance": 1955, "debut": 1980,
     "liquidation": 2017, "traitement": 13000.0,
     "objet": "trente-sept ans, dix-sept trimestres de décote, l'âge d'ouverture "
              "atteint en 2017 : aucun minimum"},
    {"code": "salarie_1944_trente_ans_en_2009", "regle": "minimum_contributif",
     "regime": REGIME_GENERAL, "naissance": 1944, "debut": 1979,
     "liquidation": 2009, "salaire": 9000.0,
     "objet": "cent vingt trimestres cotisés, parti à 65 ans en janvier 2009 : "
              "le minimum majoré, sans condition de durée cotisée"},
    {"code": "salarie_1945_vingt_ans_en_2010", "regle": "minimum_contributif",
     "regime": REGIME_GENERAL, "naissance": 1945, "debut": 1990,
     "liquidation": 2010, "salaire": 9000.0,
     "objet": "quatre-vingts trimestres, après avril 2009 : le minimum seul, "
              "sans la majoration"},
    {"code": "salarie_1946_en_2011", "regle": "minimum_contributif",
     "regime": REGIME_GENERAL, "naissance": 1946, "debut": 1980,
     "liquidation": 2011, "salaire": 9000.0,
     "objet": "cent vingt-quatre trimestres cotisés : la majoration ouverte"},
    {"code": "salarie_1948_en_2013", "regle": "minimum_contributif",
     "regime": REGIME_GENERAL, "naissance": 1948, "debut": 1982,
     "liquidation": 2013, "salaire": 9000.0,
     "objet": "le même en 2013, sous le plafond de l'écrêtement"},
    {"code": "salarie_1949_en_2014", "regle": "minimum_contributif",
     "regime": REGIME_GENERAL, "naissance": 1949, "debut": 1990,
     "liquidation": 2014, "salaire": 10000.0,
     "objet": "quatre-vingt-seize trimestres : le minimum seul"},
    {"code": "salarie_1951_ajourne_en_2017", "regle": "duree_corrigee",
     "regime": REGIME_GENERAL, "naissance": 1951, "debut": 1986,
     "liquidation": 2017, "salaire": 10000.0,
     "objet": "parti à 66 ans, un an après l'âge du taux plein, avec 124 "
              "trimestres : la durée corrigée de 10 %"},
)

#: Grandeurs relevées dans la pension civile : celles de la première famille,
#: sans le départ des parents.
GRANDEURS_PUBLIQUES = {nom: variable for nom, variable in frere.GRANDEURS.items()
                       if nom != "depart_anticipe"}

#: Grandeurs relevées au régime général.
GRANDEURS_GENERALES = {
    "duree_assurance": "duree_assurance",
    "duree_cotisee": "duree_assurance_personnellement_cotisee",
    "salaire_de_reference": "salaire_de_reference",
    "coefficient_de_proratisation": "coefficient_de_proratisation",
    "decote_trimestres": "decote_trimestres",
    "taux_de_liquidation": "taux_de_liquidation",
    "pension_avant_minimum": "pension_avant_minimum_et_plafonnement",
    "minimum_contributif": "pension_minimale",
    "pension_brute": "pension_brute",
}


def entrees(profil: dict) -> dict:
    """La situation qu'OpenFisca reçoit."""
    if profil["regime"] != REGIME_GENERAL:
        return frere.entrees({**profil, "sexe": "H", "naissances": []})
    annees = [str(a) for a in range(profil["debut"], profil["liquidation"])]
    return {
        "date_de_naissance": {"ETERNITY": f"{profil['naissance']}-01-01"},
        "sexe": {"ETERNITY": False},
        "nombre_enfants": {"ETERNITY": 0},
        "regime_general_cnav_liquidation_date": {
            "ETERNITY": f"{profil['liquidation']}-01-01"},
        "regime_general_cnav_salaire_de_base": {a: profil["salaire"] for a in annees},
        "statut_du_cotisant": {a: "emploi" for a in annees},
        "categorie_salarie": {a: "prive_non_cadre" for a in annees},
    }


def calculer(profil: dict, tbs) -> dict:
    """Relève les grandeurs de la pension pour un profil."""
    import numpy as np
    from openfisca_core.simulation_builder import SimulationBuilder

    simulation = SimulationBuilder().build_from_entities(
        tbs, {"persons": {"assure": entrees(profil)}})
    simulation.max_spiral_loops = frere.SPIRALES
    annee = profil["liquidation"]
    if profil["regime"] == REGIME_GENERAL:
        return {nom: float(simulation.calculate(f"regime_general_cnav_{variable}", annee)[0])
                for nom, variable in GRANDEURS_GENERALES.items()}
    prefixe, _ = frere.REGIMES[profil["regime"]]
    mesures: dict = {
        nom: float(simulation.calculate(f"{prefixe}_{variable}", annee)[0])
        for nom, variable in GRANDEURS_PUBLIQUES.items()
    }
    mesures["ouverture_des_droits_le"] = str(
        simulation.calculate(f"{prefixe}_ouverture_des_droits_date", annee)[0])
    # Ce que son minimum lit : les services de l'État, quel que soit le régime.
    mesures["services_fonction_publique"] = float(
        simulation.calculate("fonction_publique_duree_de_service_effective", annee)[0])
    # Sa référence : l'indice majoré de l'année au point du 1er janvier.
    jour = np.array([f"{annee}-01-01"], dtype="datetime64[D]")
    parametres = tbs.parameters(f"{annee}-01-01")
    pension_civile = parametres.retraites.secteur_public.pension_civile
    mesures["reference_du_minimum"] = float(
        pension_civile.minimum_garanti.valeur_indice_maj[jour][0]
        * parametres.marche_travail.remuneration_dans_fonction_publique.indicefp
        .point_indice_en_euros)
    mesures["duree_requise_de_la_generation"] = float(
        pension_civile.trimtp.nombre_trimestres_cibles_taux_plein_par_generation[
            np.array([f"{profil['naissance']}-01-01"], dtype="datetime64[D]")][0])
    return mesures


def main(argv: list[str] | None = None) -> int:
    sys.setrecursionlimit(frere.RECURSION)
    try:
        from openfisca_france_pension import CountryTaxBenefitSystem
    except ImportError:
        print(
            "OpenFisca-France-Pension n'est pas installé.\n"
            "    pip install OpenFisca-France-Pension\n"
            "Il n'est PAS une dépendance du dépôt : le témoin qu'il produit est "
            "versionné, et les tests s'en contentent.",
            file=sys.stderr,
        )
        return 1

    tbs = CountryTaxBenefitSystem()
    releves = {}
    for profil in PROFILS:
        mesures = calculer(profil, tbs)
        if mesures["duree_assurance"] <= 0 or mesures["pension_brute"] <= 0:
            print(
                f"{profil['code']} : OpenFisca rend une durée ou une pension "
                "nulle — le déroulage récursif n'a pas eu lieu. Rien n'est écrit.",
                file=sys.stderr,
            )
            return 1
        releves[profil["code"]] = {
            "profil": profil,
            "entrees_openfisca": frere.entrees_notables(entrees(profil)),
            "openfisca": mesures,
        }
        minimum = mesures.get("minimum_garanti", mesures.get("minimum_contributif"))
        print(f"{profil['code']:<34} avant {mesures['pension_avant_minimum']:>9.2f}  "
              f"minimum {minimum:>9.2f}  pension {mesures['pension_brute']:>9.2f} €")

    from importlib.metadata import PackageNotFoundError, version

    try:
        publiee = version("OpenFisca-France-Pension")
    except PackageNotFoundError:  # pragma: no cover - paquet posé à la main
        publiee = "inconnue"

    document = {
        "source": "OpenFisca-France-Pension",
        "version": publiee,
        "recupere_le": date.today().isoformat(),
        "famille": "les minima : le minimum garanti de la pension civile, à l'État "
                   "et à la CNRACL, et le minimum contributif du régime général",
        "avertissement": (
            "Deuxième implémentation, pas une source officielle. Son minimum "
            "garanti de la CNRACL lit les services de l'État, et vaut zéro ; il "
            "sert le d de L. 17 à qui l'avait perdu, et ne minore pas l'âge "
            "d'annulation qui l'ouvre de 2011 à 2015. Son minimum contributif ne "
            "lit pas la durée corrigée après l'âge du taux plein."
        ),
        "perimetre": (
            "Fonction publique de l'État et CNRACL, sédentaires, sans prime ni "
            "enfant, à temps plein, à traitement nominal constant et bas, "
            "liquidations de 2008 à 2022 ; salariés non-cadres du régime général, "
            "à salaire nominal constant, entrés tard, liquidations de 2009 à 2017."
        ),
        "convention": CONVENTION,
        "profils": releves,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"{SORTIE} : {len(releves)} profils")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
