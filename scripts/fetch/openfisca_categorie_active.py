#!/usr/bin/env python3
"""L'oracle au-delà des carrières simples, troisième famille (action 153) : la
catégorie active des fonctionnaires — l'âge anticipé, la durée de services
actifs qui l'ouvre, la durée requise, la décote et la limite d'âge des emplois
classés —, par OpenFisca-France-Pension.

    pip install OpenFisca-France-Pension
    python scripts/fetch/openfisca_categorie_active.py

Le frère de ``openfisca_temps_partiel_et_parents.py``, dont il reprend la
carrière, les régimes, les grandeurs relevées et le garde-fou ; les familles
d'avant ne donnaient à OpenFisca que des sédentaires. Celle-ci éprouve ce qu'il
fait d'un emploi classé : l'âge d'ouverture, les quinze à dix-sept ans de
services actifs qui l'ouvrent, la durée requise « par dérogation à l'article
L. 13 », l'âge d'annulation de la décote et la super-active. Sa convention
suit ; le témoin la porte (``convention``, et les ``entrees_openfisca`` de
chaque profil), et ``tests/test_oracle_categorie_active.py`` la vérifie avant
de comparer.

LA CONVENTION DE TRADUCTION.

* **La carrière** est celle de la première famille : né un 1er janvier, entré
  au 1er janvier de ``debut``, à traitement nominal constant et sans prime, à
  temps plein, continue jusqu'à la liquidation, au 1er janvier de l'année
  écrite ; sans enfant, sans période au régime général.
* **L'emploi classé** se dit, au dépôt, par le statut de chaque année : un
  statut classé (``statut_actif``, l'un des trois qui ne portent que le
  classement)
  aux années ``actif`` — une seule plage, de son début à sa fin incluse —, le
  statut sédentaire du régime aux autres. OpenFisca lit la catégorie de chaque
  année (``categorie_activite``) : ``actif`` aux années classées en catégorie
  active, ``super_actif`` aux années super-actives, ``sedentaire`` aux autres.
  Il compte lui-même les années actives et date l'atteinte des quinze ans ;
  il ne compte pas les années super-actives, et ne sait de la super-active
  que ce qu'on lui déclare à la liquidation (``super_actif_a_la_liquidation``)
  : on le lui déclare vrai quand le dépôt ouvre l'âge minoré.
* **Les dates.** OpenFisca date l'atteinte des quinze ans du 1er janvier de
  l'année où ils s'achèvent, le dépôt du mois où ils s'achèvent : sur des
  plages entrées un 1er janvier, l'année est la même, et c'est elle que le
  décret n° 2011-2103 lit. Aucune plage n'achève ses quinze ans en 2011,
  coupée par le décret au 1er juillet.
* **Les statuts du dépôt** sont les trois qui ne portent que le
  classement : ``fonctionnaire_territorial_hospitalier_actif`` à la CNRACL,
  ``fonctionnaire_etat_actif`` et ``fonctionnaire_etat_super_actif`` à
  l'État. Les statuts de corps y ajoutent ce qu'OpenFisca n'écrit pas :
  l'aide-soignant sa prime spéciale de sujétion et la majoration de durée
  des hospitaliers, le policier son indemnité de sujétions spéciales et la
  bonification du cinquième (son ``super_actif`` vaut ``False`` dans la
  proratisation).
* **Ce qui ne se traduit pas.** Le corps d'appartenance, dont dépendent
  quelques durées propres (les ingénieurs du contrôle aérien, les égoutiers) :
  ni l'un ni l'autre ne le lit. L'intégration dans un corps
  sédentaire après les quinze ans (article 35, III, de la loi n° 2010-1330)
  : les profils mixtes la vivent, et les deux modèles la lisent par l'année
  d'atteinte.

Ce que la confrontation a trouvé, le 14 octobre 2026.

* **L'âge anticipé, la décote et la limite d'âge : rien à corriger.** Sept
  actifs, de 2009 à 2020 : l'âge d'ouverture au mois, la limite d'âge, les
  trimestres de décote, le taux et le traitement concordent ; la durée
  qu'OpenFisca oppose à la décote des actifs est celle de L. 13, III.
* **La durée de services actifs : un écart, chez nous, corrigé.** Le dépôt
  exigeait dix-sept ans de toute génération née depuis le 1er juillet 1956 ;
  l'article 6 du décret n° 2011-2103 les relève selon l'année où les quinze
  ans sont atteints, comme OpenFisca le lit. Le dépôt refusait l'âge anticipé
  à qui avait seize ans actifs achevant leurs quinze avant 2013 ; il porte
  depuis ``duree_services_actifs.csv``.
* **Deux écarts chez OpenFisca.** Il proratise la pension des actifs sur la
  durée de leur génération, quand L. 13, III, prend celle de l'année
  d'ouverture du droit — celle qu'il oppose à la décote : de un à trois
  trimestres de trop, autant de pension en moins. Et il ne connaît pas la
  super-active : il ne compte pas ses années, lui oppose l'âge du sédentaire,
  et ne sert pas la bonification du cinquième.

Ce que ce contrôle ne couvre pas : les militaires, dont la pension s'ouvre à
une durée ; les ouvriers de l'État ; les infirmiers et les aides-soignants qui
ont opté pour la catégorie sédentaire en 2010 ; la majoration de durée des
hospitaliers actifs ; les pensions d'après la réforme de 2023, au-delà des
barèmes d'OpenFisca.

Le fichier produit, ``tests/temoins/openfisca_categorie_active.json``, est
VERSIONNÉ : le test rejoue la confrontation sur un dépôt fraîchement cloné,
sans installer OpenFisca.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import openfisca_temps_partiel_et_parents as frere  # noqa: E402

SORTIE = Path("tests/temoins/openfisca_categorie_active.json")

#: La catégorie qu'OpenFisca lit aux années classées, selon le classement que
#: le dépôt lit au statut.
CATEGORIES = {"active": "actif", "super_active": "super_actif"}

#: La convention, telle que le témoin la porte : chaque entrée d'OpenFisca, et
#: ce qu'elle reçoit du profil du dépôt.
CONVENTION = {
    "date_de_naissance": "le 1er janvier de `naissance`",
    "sexe": "faux (`sexe` H)",
    "liquidation_date": "le 1er janvier de `liquidation`",
    "salaire_de_base": "le traitement, chaque année de `debut` à `liquidation` exclue",
    "duree_de_service_cotisee_annuelle": "4 trimestres chaque année",
    "quotite_de_travail": "1",
    "taux_de_prime": "0",
    "categorie_activite": "`actif` ou `super_actif` aux années de la plage `actif`, "
                          "selon le `classement` ; `sedentaire` aux autres",
    "super_actif_a_la_liquidation": "vrai au super-actif dont le dépôt ouvre l'âge "
                                    "minoré, non déclaré sinon",
    "non_traduit": (
        "Le corps d'appartenance, dont quelques durées dépendent (contrôle "
        "aérien, égoutiers), que ni l'un ni l'autre ne lit ; les primes et "
        "bonifications des statuts de corps (aide-soignant, policier), que "
        "les profils n'empruntent pas ; les années super-actives, qu'OpenFisca "
        "ne compte pas."
    ),
    "dates": (
        "OpenFisca date l'atteinte des quinze ans de services actifs du "
        "1er janvier de l'année où ils s'achèvent, le dépôt du mois : seule "
        "l'année se compare, et aucune plage ne les achève en 2011."
    ),
}

#: Profils confrontés. ``actif`` est la plage des années classées ;
#: ``statut_actif``, le statut qu'elles ont au dépôt ; ``objet``, ce que
#: chacun éprouve.
PROFILS: tuple[dict, ...] = (
    {"code": "cnracl_actif_1954", "regle": "age_anticipe",
     "regime": "cnracl", "statut_actif": "fonctionnaire_territorial_hospitalier_actif", "classement": "active",
     "naissance": 1954, "debut": 1976, "liquidation": 2009, "actif": [1976, 2008],
     "traitement": 26000.0,
     "objet": "toute la carrière classée, partie à 55 ans en 2009"},
    {"code": "etat_actif_1956", "regle": "age_anticipe",
     "regime": "fonction_publique_etat", "statut_actif": "fonctionnaire_etat_actif",
     "classement": "active", "naissance": 1956, "debut": 1978, "liquidation": 2011,
     "actif": [1978, 2010], "traitement": 30000.0,
     "objet": "née au premier semestre 1956, partie à 55 ans au 1er janvier 2011"},
    {"code": "etat_actif_1957", "regle": "age_anticipe",
     "regime": "fonction_publique_etat", "statut_actif": "fonctionnaire_etat_actif",
     "classement": "active", "naissance": 1957, "debut": 1979, "liquidation": 2014,
     "actif": [1979, 2013], "traitement": 30000.0,
     "objet": "l'âge relevé de neuf mois, partie à 57 ans"},
    {"code": "cnracl_actif_1960", "regle": "age_anticipe",
     "regime": "cnracl", "statut_actif": "fonctionnaire_territorial_hospitalier_actif", "classement": "active",
     "naissance": 1960, "debut": 1982, "liquidation": 2018, "actif": [1982, 2017],
     "traitement": 27000.0,
     "objet": "l'âge de 57 ans, partie à 58"},
    {"code": "cnracl_actif_entre_tard_1958", "regle": "age_anticipe",
     "regime": "cnracl", "statut_actif": "fonctionnaire_territorial_hospitalier_actif", "classement": "active",
     "naissance": 1958, "debut": 1990, "liquidation": 2020, "actif": [1990, 2019],
     "traitement": 27000.0,
     "objet": "entrée tard, partie à 62 ans : la limite d'âge annule la décote"},
    {"code": "cnracl_actif_seize_ans_avant_2011", "regle": "duree_de_services_actifs",
     "regime": "cnracl", "statut_actif": "fonctionnaire_territorial_hospitalier_actif", "classement": "active",
     "naissance": 1958, "debut": 1980, "liquidation": 2016, "actif": [1980, 1995],
     "traitement": 26000.0,
     "objet": "seize ans actifs, achevant les quinze en 1994, puis sédentaire : "
              "quinze ans suffisent (décret n° 2011-2103, article 6)"},
    {"code": "etat_actif_seize_ans_en_2012", "regle": "duree_de_services_actifs",
     "regime": "fonction_publique_etat", "statut_actif": "fonctionnaire_etat_actif",
     "classement": "active", "naissance": 1960, "debut": 1985, "liquidation": 2018,
     "actif": [1998, 2013], "traitement": 29000.0,
     "objet": "seize ans actifs, achevant les quinze en 2012 : quinze ans et neuf "
              "mois suffisent"},
    {"code": "etat_actif_seize_ans_en_2013", "regle": "duree_de_services_actifs",
     "regime": "fonction_publique_etat", "statut_actif": "fonctionnaire_etat_actif",
     "classement": "active", "naissance": 1960, "debut": 1985, "liquidation": 2018,
     "actif": [1999, 2014], "traitement": 29000.0,
     "objet": "seize ans actifs, achevant les quinze en 2013 : il en faut seize et "
              "deux mois, l'âge anticipé ne s'ouvre pas"},
    {"code": "etat_super_actif_1962", "regle": "super_active",
     "regime": "fonction_publique_etat", "statut_actif": "fonctionnaire_etat_super_actif",
     "classement": "super_active", "naissance": 1962, "debut": 1983,
     "liquidation": 2014, "actif": [1983, 2013], "traitement": 32000.0,
     "objet": "trente et un ans super-actifs, parti à 52 ans"},
    {"code": "etat_super_actif_vingt_six_ans_avant_2011", "regle": "super_active",
     "regime": "fonction_publique_etat", "statut_actif": "fonctionnaire_etat_super_actif",
     "classement": "super_active", "naissance": 1962, "debut": 1984,
     "liquidation": 2016, "actif": [1984, 2009], "traitement": 31000.0,
     "objet": "vingt-six ans super-actifs, achevant les vingt-cinq en 2008, puis "
              "sédentaire, parti à 54 ans : vingt-cinq ans suffisent"},
)

#: Grandeurs relevées : celles de la première famille, et ce que le classement
#: déplace.
GRANDEURS = {
    **{nom: variable for nom, variable in frere.GRANDEURS.items()
       if nom != "depart_anticipe"},
    "actif_a_la_liquidation": "actif_a_la_liquidation",
    "annees_actives": "nombre_annees_actif",
    "limite_d_age": "limite_d_age",
}

#: Les dates qu'il fixe, relevées en texte.
DATES = {
    "quinze_ans_actifs_le": "date_quinze_ans_actif",
    "ouverture_des_droits_le": "ouverture_des_droits_date",
}


def classees(profil: dict) -> range:
    """Les années de la plage classée."""
    debut, fin = profil["actif"]
    return range(debut, fin + 1)


def entrees(profil: dict) -> dict:
    """La situation qu'OpenFisca reçoit : la carrière de la première famille,
    puis la catégorie de chaque année."""
    situation = frere.entrees({**profil, "sexe": "H", "naissances": []})
    prefixe, _ = frere.REGIMES[profil["regime"]]
    actives = set(classees(profil))
    categorie = CATEGORIES[profil["classement"]]
    situation[f"{prefixe}_categorie_activite"] = {
        str(a): categorie if a in actives else "sedentaire"
        for a in range(profil["debut"], profil["liquidation"])}
    if profil["classement"] == "super_active":
        situation[f"{prefixe}_super_actif_a_la_liquidation"] = {
            str(profil["liquidation"]): True}
    return situation


def entrees_notables(situation: dict) -> dict:
    """Ce que le témoin garde : les entrées de la première famille, et les
    années que la catégorie distingue du sédentaire."""
    notables = frere.entrees_notables(situation)
    for nom, valeurs in situation.items():
        if nom.endswith("_categorie_activite"):
            notables[nom] = {a: v for a, v in valeurs.items() if v != "sedentaire"}
        elif nom.endswith("_super_actif_a_la_liquidation"):
            notables[nom] = valeurs
    return notables


def calculer(profil: dict, tbs) -> dict:
    """Relève les grandeurs de la pension civile pour un profil."""
    import numpy as np
    from openfisca_core.simulation_builder import SimulationBuilder

    prefixe, _ = frere.REGIMES[profil["regime"]]
    simulation = SimulationBuilder().build_from_entities(
        tbs, {"persons": {"assure": entrees(profil)}})
    simulation.max_spiral_loops = frere.SPIRALES
    mesures: dict = {
        nom: float(simulation.calculate(f"{prefixe}_{variable}", profil["liquidation"])[0])
        for nom, variable in GRANDEURS.items()
    }
    for nom, variable in DATES.items():
        mesures[nom] = str(simulation.calculate(
            f"{prefixe}_{variable}", profil["liquidation"])[0])
    bareme = tbs.parameters(f"{profil['liquidation']}-01-01").retraites.secteur_public \
        .pension_civile
    naissance = np.array([f"{profil['naissance']}-01-01"], dtype="datetime64[D]")
    # La durée qui proratise sa pension, celle de la génération, et celle
    # qu'il oppose à la décote des actifs.
    mesures["duree_requise_de_la_generation"] = float(
        bareme.trimtp.nombre_trimestres_cibles_taux_plein_par_generation[naissance][0])
    mesures["duree_requise_des_actifs"] = float(
        bareme.trimtp_a.nombre_trimestres_cibles_taux_plein_par_generation_actifs[
            naissance][0])
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
            "entrees_openfisca": entrees_notables(entrees(profil)),
            "openfisca": mesures,
        }
        print(f"{profil['code']:<36} actif {mesures['actif_a_la_liquidation']:.0f}  "
              f"ouverture {mesures['ouverture_des_droits_le']}  "
              f"durée {mesures['duree_assurance']:>4.0f}  "
              f"décote {mesures['decote_trimestres']:>3.0f}  "
              f"prorat. {mesures['coefficient_de_proratisation']:.4f}  "
              f"taux {mesures['taux_de_liquidation']:.4%}  "
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
        "famille": "la catégorie active des fonctionnaires : l'âge anticipé, la "
                   "durée de services actifs, la durée requise, la décote, la "
                   "super-active",
        "avertissement": (
            "Deuxième implémentation, pas une source officielle. Il proratise la "
            "pension des actifs sur la durée de leur génération, et non sur celle "
            "de l'année d'ouverture du droit (L. 13, III), qu'il oppose pourtant à "
            "leur décote ; il ne compte pas les années super-actives, oppose au "
            "super-actif l'âge du sédentaire et ne sert pas la bonification du "
            "cinquième."
        ),
        "perimetre": (
            "Fonction publique de l'État et CNRACL, statuts qui ne portent que le "
            "classement, sans prime ni enfant, à temps plein, carrières continues à "
            "traitement nominal constant, liquidations de 2009 à 2020 : cinq actifs "
            "de toute leur carrière, trois de seize ans achevant leurs quinze en "
            "1994, 2012 et 2013, et deux super-actifs."
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
