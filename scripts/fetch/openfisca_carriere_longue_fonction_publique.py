#!/usr/bin/env python3
"""L'oracle au-delà des carrières simples, quatrième famille (action 153) : la
carrière longue des fonctionnaires — l'âge que L. 25 bis du code des pensions
abaisse à qui a commencé tôt et cotisé longtemps —, par
OpenFisca-France-Pension.

    pip install OpenFisca-France-Pension
    python scripts/fetch/openfisca_carriere_longue_fonction_publique.py

Le frère de ``openfisca_categorie_active.py``, dont il reprend la carrière, les
régimes, les grandeurs relevées et le garde-fou. Les familles d'avant
partaient à l'âge du droit commun ou de l'emploi classé ; celle-ci part
avant, par la carrière longue : la condition d'entrée précoce, la durée
cotisée, l'âge de chaque porte. Sa convention suit ; le témoin la porte
(``convention``, et les ``entrees_openfisca`` de chaque profil), et
``tests/test_oracle_carriere_longue_fonction_publique.py`` la vérifie avant de
comparer.

LA CONVENTION DE TRADUCTION.

* **La carrière** est celle de la première famille : né un 1er janvier,
  entré au 1er janvier de ``debut``, à traitement nominal constant et sans
  prime, à temps plein, continue jusqu'à la liquidation, au 1er janvier de
  l'année écrite ; sédentaire, sans enfant, sans période au régime général.
* **L'entrée précoce.** La carrière commence l'année des quatorze à dix-huit
  ans. Les années d'avant dix-huit ans sont, dans la vie, celles d'un
  apprenti ou d'un auxiliaire, affilié ailleurs ; la convention les range au
  régime de la liquidation, parce qu'OpenFisca ne lit l'entrée précoce que
  dans les services de la fonction publique (``duree_assurance_cotisee_seuil_bas``
  et ``_haut``). Chacun des deux compte alors les mêmes trimestres cotisés :
  quatre par année, cinq exigés à la fin de l'année des seize, dix-sept ou
  vingt ans (L. 25 bis ; D. 16-1).
* **Ce qui se compare** est le droit d'ouvrir la pension au 1er janvier de
  ``liquidation`` : au dépôt, ``liquidation_ouverte`` et le motif
  ``carriere_longue`` ; chez OpenFisca, qui sert la pension même avant l'âge,
  une date d'ouverture des droits (``ouverture_des_droits_date``) au plus tard
  à la liquidation. Et la pension, qui n'en dépend pas chez lui.
* **Rien n'est déclaré** : ni ``raison_depart_taux_plein_anticipe``, qui
  ouvrirait la carrière longue sans condition, ni catégorie, ni enfant.
* **Ce qui ne se traduit pas.** Les périodes réputées cotisées (service
  national, maladie, maternité), que les profils n'ont pas ; la condition de
  durée d'assurance, cent soixante-huit trimestres avant 2012, que les deux
  remplissent dès qu'ils ont la durée cotisée ; les pensions d'après la
  réforme de 2023, au-delà des barèmes d'OpenFisca.

Ce que la confrontation a trouvé, le 16 octobre 2026.

* **Deux erreurs chez nous, corrigées.** La fonction publique n'a eu la
  carrière longue qu'au 1er janvier 2005, et chaque porte à sa date :
  cinquante-neuf ans en 2005, cinquante-huit au 1er juillet 2006,
  cinquante-six au 1er janvier 2008 (L. 25 bis, rédaction du 1er janvier
  2005 ; loi n° 2004-1370, article 57, pour la CNRACL). Le dépôt lui
  ouvrait les trois portes du régime général dès 2004. Et la durée y était
  fixe, cent soixante trimestres et le supplément de chaque porte, jusqu'en
  décembre 2008 ; le dépôt lui opposait celle de l'année d'ouverture, de 152
  à 158 trimestres. OpenFisca, qui ne connaît la carrière longue que par
  génération, refuse ces départs : les deux concordent depuis.
* **Deux erreurs chez OpenFisca.** Il lit la condition d'entrée avant vingt
  ans à la fin de l'année des seize (``duree_assurance_cotisee_seuil_haut``),
  et refuse donc à qui a commencé à dix-huit ans le départ à soixante ans
  que le décret n° 2012-847 lui ouvre. Et il lit, pour la CNRACL, les
  services de la fonction publique de l'État : il ne l'ouvre jamais à un
  fonctionnaire territorial ou hospitalier.
* **Un défaut sans effet sur la pension.** Il date l'ouverture à l'âge de la
  porte, sur la durée cotisée à la liquidation : cinquante-six ans à qui
  n'avait alors que 164 des 174 trimestres exigés. Le dépôt la date au mois
  où la durée est réunie. La pension n'en dépend pas : il proratise sur la
  durée de la génération, et ces carrières l'ont toute.

Le fichier produit, ``tests/temoins/openfisca_carriere_longue_fonction_publique.json``,
est VERSIONNÉ : le test rejoue la confrontation sur un dépôt fraîchement
cloné, sans installer OpenFisca.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import openfisca_temps_partiel_et_parents as frere  # noqa: E402

SORTIE = Path("tests/temoins/openfisca_carriere_longue_fonction_publique.json")

#: La convention, telle que le témoin la porte : chaque entrée d'OpenFisca, et
#: ce qu'elle reçoit du profil du dépôt.
CONVENTION = {
    "date_de_naissance": "le 1er janvier de `naissance`",
    "sexe": "faux (`sexe` H)",
    "liquidation_date": "le 1er janvier de `liquidation`",
    "salaire_de_base": "le traitement, chaque année de `debut` à `liquidation` exclue",
    "duree_de_service_cotisee_annuelle": "4 trimestres chaque année, dès l'année "
                                         "des quatorze à dix-huit ans",
    "quotite_de_travail": "1",
    "taux_de_prime": "0",
    "raison_depart_taux_plein_anticipe": "non déclarée",
    "entree_precoce": (
        "Les années d'avant dix-huit ans, dans la vie celles d'un apprenti ou "
        "d'un auxiliaire, sont rangées au régime de la liquidation : OpenFisca "
        "ne lit l'entrée précoce que dans les services de la fonction publique."
    ),
    "ouverture": (
        "Le dépôt ouvre ou refuse la liquidation ; OpenFisca, qui sert la "
        "pension même avant l'âge, l'ouvre quand sa date d'ouverture des droits "
        "tombe au plus tard le 1er janvier de `liquidation`."
    ),
    "non_traduit": (
        "Les périodes réputées cotisées, que les profils n'ont pas ; la durée "
        "d'assurance de cent soixante-huit trimestres d'avant 2012, que la durée "
        "cotisée emporte ici ; la réforme de 2023, au-delà des barèmes "
        "d'OpenFisca."
    ),
}

#: Profils confrontés. ``regle`` dit ce que chacun éprouve : les portes de la
#: fonction publique avant 2009, l'entrée avant vingt ans (décret
#: n° 2012-847), la CNRACL, la durée cotisée ; ``objet``, en clair.
PROFILS: tuple[dict, ...] = (
    {"code": "etat_1946_debut_15_en_2004", "regle": "portes_avant_2009",
     "regime": "fonction_publique_etat", "naissance": 1946, "debut": 1961,
     "liquidation": 2004, "traitement": 30000.0,
     "objet": "quarante-trois ans cotisés, parti à 58 ans en 2004 : la fonction "
              "publique n'a pas encore la carrière longue"},
    {"code": "etat_1947_debut_15_en_2005", "regle": "portes_avant_2009",
     "regime": "fonction_publique_etat", "naissance": 1947, "debut": 1962,
     "liquidation": 2005, "traitement": 30000.0,
     "objet": "parti à 58 ans en janvier 2005 : seule la porte de 59 ans est "
              "ouverte"},
    {"code": "etat_1950_debut_15_en_2007", "regle": "portes_avant_2009",
     "regime": "fonction_publique_etat", "naissance": 1950, "debut": 1965,
     "liquidation": 2007, "traitement": 30000.0,
     "objet": "parti à 57 ans en 2007 : la porte de 56 ans ne s'ouvre qu'en 2008"},
    {"code": "etat_1949_debut_15_en_2008", "regle": "portes_avant_2009",
     "regime": "fonction_publique_etat", "naissance": 1949, "debut": 1964,
     "liquidation": 2008, "traitement": 30000.0,
     "objet": "parti à 59 ans en 2008, quarante-quatre ans cotisés : ouvert"},
    {"code": "cnracl_1952_debut_14_en_2008", "regle": "cnracl",
     "regime": "cnracl", "naissance": 1952, "debut": 1966, "liquidation": 2008,
     "traitement": 30000.0,
     "objet": "parti à 56 ans en 2008, cent soixante-huit trimestres cotisés : "
              "ouvert par la porte de 56 ans"},
    {"code": "etat_1955_debut_18_en_2015", "regle": "entree_avant_vingt_ans",
     "regime": "fonction_publique_etat", "naissance": 1955, "debut": 1973,
     "liquidation": 2015, "traitement": 30000.0,
     "objet": "entré à 18 ans, parti à 60 ans avec 168 trimestres cotisés, sa "
              "génération en devant 166"},
    {"code": "cnracl_1958_debut_18_en_2018", "regle": "entree_avant_vingt_ans",
     "regime": "cnracl", "naissance": 1958, "debut": 1976, "liquidation": 2018,
     "traitement": 27000.0,
     "objet": "entrée à 18 ans, partie à 60 ans avec 168 trimestres cotisés, sa "
              "génération en devant 167"},
    {"code": "cnracl_1955_debut_15_en_2014", "regle": "cnracl",
     "regime": "cnracl", "naissance": 1955, "debut": 1970, "liquidation": 2014,
     "traitement": 30000.0,
     "objet": "entré à 15 ans, parti à 59 ans avec 176 trimestres cotisés"},
    {"code": "etat_1955_debut_15_en_2014", "regle": "duree_cotisee",
     "regime": "fonction_publique_etat", "naissance": 1955, "debut": 1970,
     "liquidation": 2014, "traitement": 30000.0,
     "objet": "le même à l'État : la porte de 56 ans exige 174 trimestres, "
              "réunis à 58 ans et demi"},
    {"code": "etat_1960_debut_15_en_2019", "regle": "duree_cotisee",
     "regime": "fonction_publique_etat", "naissance": 1960, "debut": 1975,
     "liquidation": 2019, "traitement": 30000.0,
     "objet": "entré à 15 ans, parti à 59 ans avec 176 trimestres cotisés"},
    {"code": "etat_1953_debut_14_en_2010", "regle": "duree_cotisee",
     "regime": "fonction_publique_etat", "naissance": 1953, "debut": 1967,
     "liquidation": 2010, "traitement": 30000.0,
     "objet": "parti à 57 ans avec 172 trimestres cotisés, quand la porte de "
              "56 ans en exige 173 : refusé"},
    {"code": "etat_1954_debut_14_en_2011", "regle": "duree_cotisee",
     "regime": "fonction_publique_etat", "naissance": 1954, "debut": 1968,
     "liquidation": 2011, "traitement": 30000.0,
     "objet": "le même un an plus tard : refusé"},
)

#: Grandeurs relevées : celles de la première famille, et ce que la carrière
#: longue déplace.
GRANDEURS = {
    **{nom: variable for nom, variable in frere.GRANDEURS.items()
       if nom != "depart_anticipe"},
    "carriere_longue": "carriere_longue",
    "porte": "carriere_longue_seuil_determine_aod",
    "cotises_a_la_porte_basse": "duree_assurance_cotisee_seuil_bas",
    "cotises_a_la_porte_haute": "duree_assurance_cotisee_seuil_haut",
}

#: Les dates qu'il fixe, relevées en texte.
DATES = {
    "ouverture_des_droits_le": "ouverture_des_droits_date",
    "ouverture_carriere_longue_le": "ouverture_des_droits_carriere_longue_date",
}


def entrees(profil: dict) -> dict:
    """La situation qu'OpenFisca reçoit : la carrière de la première famille,
    sans enfant ni raison."""
    return frere.entrees({**profil, "sexe": "H", "naissances": []})


def calculer(profil: dict, tbs) -> dict:
    """Relève les grandeurs de la pension civile pour un profil."""
    from openfisca_core.simulation_builder import SimulationBuilder

    prefixe, _ = frere.REGIMES[profil["regime"]]
    simulation = SimulationBuilder().build_from_entities(
        tbs, {"persons": {"assure": entrees(profil)}})
    simulation.max_spiral_loops = frere.SPIRALES
    annee = profil["liquidation"]
    mesures: dict = {
        nom: float(simulation.calculate(f"{prefixe}_{variable}", annee)[0])
        for nom, variable in GRANDEURS.items()
    }
    for nom, variable in DATES.items():
        mesures[nom] = str(simulation.calculate(f"{prefixe}_{variable}", annee)[0])
    mesures["cotises_tous_regimes"] = float(
        simulation.calculate("duree_assurance_cotisee_tous_regimes", annee)[0])
    # Ce qu'il lit pour l'entrée précoce, la fin de l'année des seize ans, et
    # ce qu'il aurait dû lire pour l'entrée avant vingt ans, dans les services
    # de l'État quel que soit le régime, et dans ceux du régime.
    for age in (16, 20):
        for lu in ("fonction_publique", prefixe):
            mesures[f"services_{lu}_a_{age}_ans"] = float(simulation.calculate(
                f"{lu}_duree_de_service_effective", profil["naissance"] + age)[0])
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
        print(f"{profil['code']:<30} carrière longue {mesures['carriere_longue']:.0f}  "
              f"porte {mesures['porte']:>4.0f}  "
              f"ouverture {mesures['ouverture_des_droits_le']}  "
              f"cotisés {mesures['cotises_tous_regimes']:>4.0f}  "
              f"pension {mesures['pension']:>10.2f} €")

    from importlib.metadata import PackageNotFoundError, version

    try:
        publiee = version("OpenFisca-France-Pension")
    except PackageNotFoundError:  # pragma: no cover - paquet posé à la main
        publiee = "inconnue"

    document = {
        "source": "OpenFisca-France-Pension",
        "version": publiee,
        "recupere_le": date.today().isoformat(),
        "famille": "la carrière longue des fonctionnaires : l'entrée précoce, la "
                   "durée cotisée, l'âge de chaque porte",
        "avertissement": (
            "Deuxième implémentation, pas une source officielle. Il lit l'entrée "
            "avant vingt ans à la fin de l'année des seize, et les services de "
            "l'État pour la CNRACL : il refuse la carrière longue à qui a commencé "
            "à dix-huit ans, et à tout fonctionnaire territorial ou hospitalier. "
            "Il date l'ouverture à l'âge de la porte, sur la durée cotisée à la "
            "liquidation."
        ),
        "perimetre": (
            "Fonction publique de l'État et CNRACL, sédentaires, sans prime ni "
            "enfant, à temps plein, carrières continues entrées de quatorze à "
            "dix-huit ans, à traitement nominal constant, liquidations de 2004 à "
            "2019 : quatre aux portes d'avant 2009, deux entrés à dix-huit ans, "
            "deux à la CNRACL entrés plus tôt, quatre à l'État sur la durée cotisée."
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
