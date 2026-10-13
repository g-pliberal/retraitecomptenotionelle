#!/usr/bin/env python3
"""L'oracle au-delà des carrières simples, première famille (action 153) : le
temps partiel des fonctionnaires et le départ anticipé des parents de trois
enfants, par OpenFisca-France-Pension.

    pip install OpenFisca-France-Pension
    python scripts/fetch/openfisca_temps_partiel_et_parents.py

Le frère de ``openfisca_fonction_publique.py``, qui ne passait à OpenFisca que
des sédentaires sans enfant, à temps plein : ce qui se décrit à l'identique des
deux côtés. OpenFisca calcule pourtant les deux règles que l'action 136 lui
avait prises — la quotité qui réduit les services sans réduire la durée
d'assurance, et le départ du parent de trois enfants qui avait quinze ans de
services —, et le dépôt les a écrites depuis (fiches
``temps_partiel_fonction_publique`` et ``depart_anticipe_parents_trois_enfants``).
Pour les lui confronter, il faut traduire : c'est la convention qui suit, que le
témoin porte aussi (``convention``, et les ``entrees_openfisca`` de chaque
profil), et que ``tests/test_oracle_familles.py`` vérifie avant de comparer.

LA CONVENTION DE TRADUCTION.

* **La carrière**, comme au premier oracle de la fonction publique : née un
  1er janvier, entrée au 1er janvier de ``debut``, à traitement nominal
  constant et sans prime, sédentaire, continue jusqu'à la liquidation, au
  1er janvier de l'année écrite.
* **Le temps partiel** se dit, au dépôt, comme son formulaire le saisit : des
  années entières et leur quotité (``temps_partiel``, « 1995:2004:80 »). Une
  ligne de ces années porte la quotité et le revenu perçu, le traitement réduit
  d'autant ; le modèle compte les services à la quotité, la durée en entier, et
  liquide le traitement à temps plein (L. 15). OpenFisca reçoit, année par
  année, les SERVICES eux-mêmes — quatre trimestres fois la quotité
  (``duree_de_service_cotisee_annuelle``) — et la quotité
  (``quotite_de_travail``), dont il retrouve la durée d'assurance en les
  divisant ; et le traitement à TEMPS PLEIN (``salaire_de_base``), d'où il tire
  l'indice : un traitement réduit lui donnerait un indice réduit, et une
  pension que L. 15 ne liquide pas. Il arrondit les services une fois, à la
  liquidation ; le dépôt les compte au jour et les arrondit une fois (R. 26).
  Des quotités de 50 à 90 % ne laissent jamais un demi-trimestre : l'arrondi
  au pair de numpy ne mord pas.
* **Les enfants** sont, au dépôt, des naissances datées (``naissances``) ;
  OpenFisca n'en lit qu'un nombre (``nombre_enfants``), une seule date
  (``date_naissance_enfant``), celle à laquelle il compte la troisième
  naissance acquise, et le nombre de ceux nés avant 2004
  (``…_nombre_enfants_nes_avant_2004``) : on lui donne la naissance du
  troisième enfant, et ce compte. Le sexe de la mère est son ``sexe`` vrai.
  Toutes les naissances tombent pendant les services : ni la bonification de
  L. 12, b, ni l'interruption d'activité ne dépendent alors d'une période
  hors du code des pensions.
* **Ce qui ne se traduit pas.** OpenFisca ne lit pas l'interruption d'activité
  pour chaque enfant que L. 24, I, 3°, exige depuis la loi du 30 décembre
  2004 : son parent l'a toujours prise. Le dépôt la présume de la mère seule.
  Un père est gardé pour le montrer, et seulement pour cela. La raison du
  départ (``raison_depart_taux_plein_anticipe``) n'est pas déclarée : OpenFisca
  date alors lui-même les conditions réunies, ce que la confrontation
  éprouve ; un profil la déclare « famille », pour montrer ce qu'elle fait.
* **Les dates.** OpenFisca date les quinze ans de services du 1er janvier de
  l'année au cours de laquelle ils s'achèvent, le dépôt du mois : sur des
  carrières entrées un 1er janvier, l'année est la même, et c'est elle que la
  durée et la décote lisent. Seule l'année se compare.

Ce que la confrontation a trouvé, le 13 octobre 2026.

* **Le temps partiel : rien à corriger.** Durée, services, décote, surcote,
  traitement à temps plein et pension tombent au centime sur les six profils ;
  le minimum garanti lit des deux côtés les services réduits.
* **Les parents de trois enfants : quatre écarts, tous chez lui.** La durée
  qui proratise la pension est chez lui celle de la génération, quand
  l'article 66, II, de la loi n° 2003-775, puis son article 5, VI, prennent
  celle de l'année des conditions réunies. Avant juillet 2011, il ferme le
  départ à qui n'atteint pas son âge d'ouverture avant 2016 et n'a pas réuni
  les conditions avant 2003, quand L. 24, I, 3°, l'ouvrait jusqu'au 1er
  juillet 2011 et que l'article 44, IV, 1°, de la loi du 9 novembre 2010
  garde l'ancien calcul aux demandes d'avant 2011. Après juin 2011, il ne le
  sert plus qu'à la raison « famille », qu'il date du départ, quand
  l'article 44, III, garde ce départ et que son IV prend l'année des soixante
  ans. Et il compte les quinze ans sur les services réduits par la quotité,
  que L. 5 compte en entier pour constituer le droit. La décote de l'année des
  conditions, son barème et son âge d'annulation, la bonification de L. 12, b,
  et la majoration de L. 18 concordent.

Ce que ce contrôle ne couvre pas : la surcotisation (L. 11 bis), que le dépôt
n'a pas écrite (action 154) ; les enfants nés hors des services ou après 2004,
les parents de plus de trois enfants, la catégorie active, les régimes
spéciaux qui avaient leur propre départ des parents : d'autres familles.

UN PIÈGE, ET IL EST SILENCIEUX : sans ``simulation.max_spiral_loops``, durée et
pension valent zéro. Le script refuse d'écrire un profil dont la durée ou la
pension serait nulle.

Le fichier produit, ``tests/temoins/openfisca_temps_partiel_et_parents.json``,
est VERSIONNÉ : ``tests/test_oracle_familles.py`` rejoue la confrontation sur un
dépôt fraîchement cloné, sans installer OpenFisca.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

SORTIE = Path("tests/temoins/openfisca_temps_partiel_et_parents.json")

#: Profondeur de récursion et nombre de reprises : voir
#: ``openfisca_regime_general.py``, les raisons sont les mêmes.
RECURSION = 20_000
SPIRALES = 100

#: Ce que le témoin appelle chaque régime, et ce qu'OpenFisca en fait :
#: préfixe de ses variables, catégorie de salarié qu'il attend.
REGIMES = {
    "fonction_publique_etat": ("fonction_publique", "public_titulaire_etat"),
    "cnracl": ("cnracl", "public_titulaire_territoriale"),
}

#: Trimestres de services d'une année entière à temps plein.
SERVICES_PAR_AN = 4
#: Le rang de l'enfant dont la naissance réunit la condition d'enfants.
ENFANTS_DU_DEPART = 3
#: Les enfants nés avant cette date ouvrent la bonification de L. 12, b.
BONIFICATION_AVANT = "2004-01-01"

#: La convention, telle que le témoin la porte : chaque entrée d'OpenFisca, et
#: ce qu'elle reçoit du profil du dépôt.
CONVENTION = {
    "date_de_naissance": "le 1er janvier de `naissance`",
    "sexe": "vrai pour une femme (`sexe` F)",
    "liquidation_date": "le 1er janvier de `liquidation`",
    "salaire_de_base": "le traitement à temps plein, chaque année de `debut` à "
                       "`liquidation` exclue, même à temps partiel (L. 15)",
    "duree_de_service_cotisee_annuelle": "4 trimestres fois la quotité de l'année",
    "quotite_de_travail": "la quotité de l'année, 1 hors de `temps_partiel`",
    "taux_de_prime": "0",
    "nombre_enfants": "le nombre de `naissances`",
    "date_naissance_enfant": "la naissance du troisième enfant",
    "nombre_enfants_nes_avant_2004": "le nombre de `naissances` avant 2004",
    "raison_depart_taux_plein_anticipe": "non déclarée, sauf `raison` au profil",
    "non_traduit": (
        "L'interruption d'activité pour chaque enfant (L. 24, I, 3°, et R. 37) : "
        "OpenFisca ne la lit pas, le dépôt la présume de la mère seule ; la "
        "demande de pension d'avant 2011 (article 44, IV, 1°, de la loi "
        "n° 2010-1330), que le dépôt présume des pensions prenant effet au plus "
        "tard le 1er juillet 2011."
    ),
    "dates": (
        "OpenFisca date les quinze ans de services du 1er janvier de l'année où "
        "ils s'achèvent, le dépôt du mois : seule l'année se compare."
    ),
}

#: Profils confrontés : six temps partiels, sept mères et un père. ``objet``
#: dit ce que chacun éprouve.
PROFILS: tuple[dict, ...] = (
    {"code": "temps_partiel_80_dix_ans_1955", "regle": "temps_partiel",
     "regime": "fonction_publique_etat", "sexe": "H", "naissance": 1955, "debut": 1980,
     "liquidation": 2017, "traitement": 30000.0, "temps_partiel": [[1995, 2004, 0.8]],
     "objet": "dix ans à 80 % au milieu d'une carrière décotée"},
    {"code": "cnracl_mi_temps_cinq_ans_1956", "regle": "temps_partiel",
     "regime": "cnracl", "sexe": "H", "naissance": 1956, "debut": 1982,
     "liquidation": 2018, "traitement": 28000.0, "temps_partiel": [[2000, 2004, 0.5]],
     "objet": "cinq ans à mi-temps, à la CNRACL"},
    {"code": "temps_partiel_70_trois_ans_1952", "regle": "temps_partiel",
     "regime": "fonction_publique_etat", "sexe": "H", "naissance": 1952, "debut": 1976,
     "liquidation": 2014, "traitement": 32000.0, "temps_partiel": [[1990, 1992, 0.7]],
     "objet": "8,4 trimestres de services à temps partiel : arrondis une fois, et non "
              "année par année"},
    {"code": "temps_partiel_jusqu_au_depart_1953", "regle": "temps_partiel",
     "regime": "fonction_publique_etat", "sexe": "H", "naissance": 1953, "debut": 1977,
     "liquidation": 2015, "traitement": 30000.0, "temps_partiel": [[2010, 2014, 0.8]],
     "objet": "à 80 % jusqu'au départ : le traitement de référence à temps plein"},
    {"code": "temps_partiel_minimum_garanti_1946", "regle": "temps_partiel",
     "regime": "fonction_publique_etat", "sexe": "H", "naissance": 1946, "debut": 1980,
     "liquidation": 2010, "traitement": 12000.0, "temps_partiel": [[1990, 1999, 0.5]],
     "objet": "le minimum garanti, sur les services réduits"},
    {"code": "temps_partiel_surcote_1949", "regle": "temps_partiel",
     "regime": "fonction_publique_etat", "sexe": "H", "naissance": 1949, "debut": 1970,
     "liquidation": 2013, "traitement": 31000.0, "temps_partiel": [[2009, 2012, 0.9]],
     "objet": "à 90 % pendant la surcote : la durée reste entière"},
    {"code": "mere_conditions_1992", "regle": "parents_de_trois_enfants",
     "regime": "fonction_publique_etat", "sexe": "F", "naissance": 1953, "debut": 1978,
     "liquidation": 2011, "traitement": 30000.0,
     "naissances": ["1980-03-01", "1982-06-01", "1985-06-01"],
     "objet": "conditions réunies avant 2004 : 150 trimestres, aucune décote"},
    {"code": "cnracl_mere_conditions_2007", "regle": "parents_de_trois_enfants",
     "regime": "cnracl", "sexe": "F", "naissance": 1955, "debut": 1993,
     "liquidation": 2011, "traitement": 27000.0,
     "naissances": ["1994-04-01", "1996-04-01", "1998-04-01"],
     "objet": "conditions de 2007 : 158 trimestres, 0,25 % par trimestre"},
    {"code": "mere_conditions_2009", "regle": "parents_de_trois_enfants",
     "regime": "fonction_publique_etat", "sexe": "F", "naissance": 1955, "debut": 1995,
     "liquidation": 2011, "traitement": 29000.0,
     "naissances": ["1996-02-01", "1998-02-01", "2001-02-01"],
     "objet": "conditions de 2009 : la durée de qui a soixante ans en 2009 "
              "(article 5, VI, de la loi n° 2003-775)"},
    {"code": "mere_temps_partiel_conditions_2004", "regle": "parents_de_trois_enfants",
     "regime": "fonction_publique_etat", "sexe": "F", "naissance": 1955, "debut": 1990,
     "liquidation": 2011, "traitement": 28000.0, "temps_partiel": [[1991, 2000, 0.8]],
     "naissances": ["1991-03-01", "1993-03-01", "1995-03-01"],
     "objet": "dix ans à 80 % avant ses quinze ans, que L. 5 compte en entier"},
    {"code": "cnracl_mere_nee_en_1962", "regle": "parents_de_trois_enfants",
     "regime": "cnracl", "sexe": "F", "naissance": 1962, "debut": 1990,
     "liquidation": 2011, "traitement": 26000.0,
     "naissances": ["1991-05-01", "1993-05-01", "1995-05-01"],
     "objet": "partie avant juillet 2011, son âge d'ouverture tombant après 2016"},
    {"code": "mere_partie_en_2012", "regle": "parents_de_trois_enfants",
     "regime": "fonction_publique_etat", "sexe": "F", "naissance": 1956, "debut": 1980,
     "liquidation": 2012, "traitement": 30000.0,
     "naissances": ["1982-03-01", "1984-03-01", "1986-03-01"],
     "objet": "partie après juin 2011 : l'année de ses soixante ans (article 44, IV, "
              "de la loi n° 2010-1330)"},
    {"code": "mere_partie_en_2012_raison_famille", "regle": "parents_de_trois_enfants",
     "regime": "fonction_publique_etat", "sexe": "F", "naissance": 1956, "debut": 1980,
     "liquidation": 2012, "traitement": 30000.0,
     "naissances": ["1982-03-01", "1984-03-01", "1986-03-01"], "raison": "famille",
     "objet": "la même, la raison « famille » déclarée à OpenFisca"},
    {"code": "pere_conditions_1992", "regle": "parents_de_trois_enfants",
     "regime": "fonction_publique_etat", "sexe": "H", "naissance": 1953, "debut": 1978,
     "liquidation": 2011, "traitement": 30000.0,
     "naissances": ["1980-03-01", "1982-06-01", "1985-06-01"],
     "objet": "le père : l'interruption d'activité, qu'OpenFisca ne lit pas"},
)

#: Grandeurs relevées, et la variable OpenFisca qui les porte (sans préfixe).
GRANDEURS = {
    "duree_assurance": "duree_assurance",
    "services": "duree_de_service_effective",
    "bonification": "bonification_cpcm",
    "coefficient_de_proratisation": "coefficient_de_proratisation",
    "decote_trimestres": "decote_trimestres",
    "coefficient_de_decote": "decote",
    "surcote_trimestres": "surcote_trimestres",
    "taux_de_liquidation": "taux_de_liquidation",
    "traitement_de_reference": "salaire_de_reference",
    "pension_avant_minimum": "pension_avant_minimum_et_plafonnement",
    "minimum_garanti": "minimum_garanti",
    "pension_brute": "pension_brute",
    "majoration_pension": "majoration_pension",
    "pension": "pension",
    "depart_anticipe": "depart_anticipe_trois_enfants",
}

#: Les dates qu'il fixe au départ des parents, relevées en texte.
DATES = {
    "conditions_reunies_le": "date_satisfaction_condition_depart_anticipe_parents_trois_enfants",
    "ouverture_des_droits_le": "ouverture_des_droits_date",
}


def quotites(profil: dict) -> dict[int, float]:
    """La quotité de chaque année à temps partiel du profil."""
    return {annee: quotite for debut, fin, quotite in profil.get("temps_partiel", ())
            for annee in range(debut, fin + 1)}


def entrees(profil: dict) -> dict:
    """La situation qu'OpenFisca reçoit : la convention, appliquée au profil."""
    prefixe, categorie = REGIMES[profil["regime"]]
    annees = [str(a) for a in range(profil["debut"], profil["liquidation"])]
    partiel = quotites(profil)
    naissances = profil.get("naissances", [])
    situation = {
        "date_de_naissance": {"ETERNITY": f"{profil['naissance']}-01-01"},
        "sexe": {"ETERNITY": profil["sexe"] == "F"},
        "nombre_enfants": {"ETERNITY": len(naissances)},
        f"{prefixe}_liquidation_date": {"ETERNITY": f"{profil['liquidation']}-01-01"},
        f"{prefixe}_salaire_de_base": {a: profil["traitement"] for a in annees},
        f"{prefixe}_duree_de_service_cotisee_annuelle": {
            a: SERVICES_PAR_AN * partiel.get(int(a), 1.0) for a in annees},
        f"{prefixe}_quotite_de_travail": {a: partiel.get(int(a), 1.0) for a in annees},
        "taux_de_prime": {a: 0.0 for a in annees},
        "statut_du_cotisant": {a: "emploi" for a in annees},
        "categorie_salarie": {a: categorie for a in annees},
    }
    if naissances:
        situation["date_naissance_enfant"] = {
            "ETERNITY": naissances[ENFANTS_DU_DEPART - 1]}
        situation[f"{prefixe}_nombre_enfants_nes_avant_2004"] = {
            "ETERNITY": sum(n < BONIFICATION_AVANT for n in naissances)}
    if profil.get("raison"):
        situation["raison_depart_taux_plein_anticipe"] = {"ETERNITY": profil["raison"]}
    return situation


def entrees_notables(situation: dict) -> dict:
    """Ce que le témoin garde de la situation : les entrées de la convention
    propres au profil — ses enfants, sa raison, ses années à temps partiel —,
    sans les années que rien ne distingue d'un temps plein."""
    notables = {}
    for nom, valeurs in situation.items():
        if nom.endswith(("quotite_de_travail", "duree_de_service_cotisee_annuelle")):
            partielles = {a: v for a, v in valeurs.items()
                          if v != (1.0 if nom.endswith("quotite_de_travail")
                                   else SERVICES_PAR_AN)}
            if partielles:
                notables[nom] = partielles
        elif nom in ("sexe", "nombre_enfants", "date_naissance_enfant",
                     "raison_depart_taux_plein_anticipe") or nom.endswith(
                         "_nombre_enfants_nes_avant_2004"):
            notables[nom] = valeurs["ETERNITY"]
    return notables


def calculer(profil: dict, tbs) -> dict:
    """Relève les grandeurs de la pension civile pour un profil."""
    import numpy as np
    from openfisca_core.simulation_builder import SimulationBuilder

    prefixe, _ = REGIMES[profil["regime"]]
    simulation = SimulationBuilder().build_from_entities(
        tbs, {"persons": {"assure": entrees(profil)}})
    simulation.max_spiral_loops = SPIRALES
    mesures: dict = {
        nom: float(simulation.calculate(f"{prefixe}_{variable}", profil["liquidation"])[0])
        for nom, variable in GRANDEURS.items()
    }
    if profil.get("naissances"):
        for nom, variable in DATES.items():
            mesures[nom] = str(simulation.calculate(
                f"{prefixe}_{variable}", profil["liquidation"])[0])
    # La durée qui proratise sa pension : celle de la génération, qu'il lit
    # dans ses barèmes à la date de liquidation.
    table = tbs.parameters(f"{profil['liquidation']}-01-01").retraites.secteur_public \
        .pension_civile.trimtp.nombre_trimestres_cibles_taux_plein_par_generation
    mesures["duree_requise_de_la_generation"] = float(
        table[np.array([f"{profil['naissance']}-01-01"], dtype="datetime64[D]")][0])
    return mesures


def main(argv: list[str] | None = None) -> int:
    sys.setrecursionlimit(RECURSION)
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
        print(f"{profil['code']:<38} durée {mesures['duree_assurance']:>5.0f}  "
              f"services {mesures['services']:>5.0f}  "
              f"taux {mesures['taux_de_liquidation']:.4%}  "
              f"pension {mesures['pension_brute']:>10.2f} €")

    from importlib.metadata import PackageNotFoundError, version

    try:
        publiee = version("OpenFisca-France-Pension")
    except PackageNotFoundError:  # pragma: no cover - paquet posé à la main
        publiee = "inconnue"

    document = {
        "source": "OpenFisca-France-Pension",
        "version": publiee,
        "recupere_le": date.today().isoformat(),
        "famille": "le temps partiel des fonctionnaires et le départ anticipé des "
                   "parents de trois enfants",
        "avertissement": (
            "Deuxième implémentation, pas une source officielle. Pour les parents "
            "de trois enfants, sa durée requise est celle de la génération et non "
            "de l'année des conditions ; il ferme le départ, avant juillet 2011, à "
            "qui n'atteint pas son âge d'ouverture avant 2016 et n'a pas réuni les "
            "conditions avant 2003, et après juin 2011 à qui ne lui déclare pas la "
            "raison « famille » ; il compte les quinze ans sur les services réduits "
            "par la quotité. Son minimum garanti suit le point d'indice de l'année "
            "de liquidation."
        ),
        "perimetre": (
            "Fonction publique de l'État et CNRACL, sédentaires sans prime, "
            "carrières continues à traitement nominal constant, liquidations de "
            "2010 à 2018 : six temps partiels sans enfant, sept mères de trois "
            "enfants nés pendant les services, et un père."
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
