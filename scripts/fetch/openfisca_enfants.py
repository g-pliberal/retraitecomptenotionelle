#!/usr/bin/env python3
"""L'oracle au-delà des carrières simples, deuxième famille (action 153) : les
enfants des fonctionnaires — la bonification de L. 12, b, et la majoration de
durée de L. 12 bis, au-delà de trois enfants, pour des enfants nés après 2004
ou hors des services —, par OpenFisca-France-Pension.

    pip install OpenFisca-France-Pension
    python scripts/fetch/openfisca_enfants.py

Le frère de ``openfisca_temps_partiel_et_parents.py``, dont il reprend la
carrière, les régimes, les grandeurs relevées et le garde-fou : la première
famille ne donnait à OpenFisca que trois enfants nés avant 2004, pendant les
services. Celle-ci éprouve ce qu'il lit d'un nombre d'enfants et d'un compte
de ceux nés avant 2004, là où le dépôt lit des naissances datées : quatre,
cinq ou sept enfants, des enfants nés depuis 2004, et des enfants nés avant le
recrutement. Sa convention suit ; le témoin la porte (``convention``, et les
``entrees_openfisca`` de chaque profil), et ``tests/test_oracle_enfants.py``
la vérifie avant de comparer.

LA CONVENTION DE TRADUCTION.

* **La carrière** est celle de la première famille : née un 1er janvier,
  entrée au 1er janvier de ``debut``, à traitement nominal constant et sans
  prime, sédentaire, à temps plein, continue jusqu'à la liquidation, au
  1er janvier de l'année écrite. Aucune période au régime général : la
  priorité entre régimes (R. 173-15) ne se pose pas.
* **Les enfants** sont, au dépôt, des naissances datées (``naissances``).
  OpenFisca en lit le nombre (``nombre_enfants``) et le compte de ceux nés
  avant 2004 (``…_nombre_enfants_nes_avant_2004``) : ceux-là ont la
  bonification de L. 12, b, les autres la majoration de L. 12 bis. Il ne lit
  ni le recrutement ni la radiation, auxquels le dépôt compare chaque
  naissance. Au parent de trois enfants au moins, la naissance du troisième
  (``date_naissance_enfant``), comme à la première famille ; aux autres,
  rien. Le sexe de la mère est son ``sexe`` vrai.
* **La date de liquidation au régime général** n'est pas déclarée : OpenFisca
  n'accorde la bonification et la majoration qu'au fonctionnaire qui liquide
  sa pension civile avant celle du régime général, et la laisse sinon au
  31 décembre 2250, ce qui les accorde.
* **Ce qui ne se traduit pas.** L'interruption ou la réduction d'activité que
  L. 12, b, exige depuis 2004, que le dépôt présume de la mère seule et
  qu'OpenFisca ne lit pas : ses mères l'ont prise, ses pères non. La
  bonification de L. 12, b bis, aux femmes qui ont accouché pendant leurs
  études, recrutées dans les deux ans de leur diplôme : ni l'un ni l'autre ne
  la lit, le dépôt ne l'a pas écrite. Les conditions de L. 18 sur les enfants
  élevés neuf ans, que le dépôt présume remplies et qu'OpenFisca ne lit pas.
* **Le départ des parents de trois enfants** est l'objet de la première
  famille : ici, chaque parent de trois enfants les a eus après ses quinze ans
  de services révolus, de sorte qu'il ne réunit pas les conditions avant
  2012, ou les réunit sans que la confrontation dépende du départ — ce que le
  test vérifie.

Ce que ce contrôle ne couvre pas : l'adoption, que le dépôt ne porte pas ; la
majoration de L. 12 ter (l'enfant handicapé) ; le b ter de L. 12, en vigueur
aux pensions de septembre 2026, au-delà des barèmes d'OpenFisca ; les enfants
d'un parent qui a aussi cotisé au régime général ; la catégorie active.

Le fichier produit, ``tests/temoins/openfisca_enfants.json``, est VERSIONNÉ :
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

SORTIE = Path("tests/temoins/openfisca_enfants.json")

#: Les enfants nés avant cette date ouvrent la bonification de L. 12, b, les
#: autres la majoration de L. 12 bis.
BONIFICATION_AVANT = frere.BONIFICATION_AVANT

#: La convention, telle que le témoin la porte : chaque entrée d'OpenFisca, et
#: ce qu'elle reçoit du profil du dépôt.
CONVENTION = {
    "date_de_naissance": "le 1er janvier de `naissance`",
    "sexe": "vrai pour une femme (`sexe` F)",
    "liquidation_date": "le 1er janvier de `liquidation`",
    "salaire_de_base": "le traitement, chaque année de `debut` à `liquidation` exclue",
    "duree_de_service_cotisee_annuelle": "4 trimestres chaque année",
    "quotite_de_travail": "1",
    "taux_de_prime": "0",
    "nombre_enfants": "le nombre de `naissances`",
    "nombre_enfants_nes_avant_2004": "le nombre de `naissances` avant 2004, "
                                     "nés pendant les services ou non",
    "date_naissance_enfant": "la naissance du troisième enfant, s'il y en a trois",
    "regime_general_cnav_liquidation_date": "non déclarée (le 31 décembre 2250)",
    "non_traduit": (
        "Le recrutement et la radiation, auxquels le dépôt compare chaque "
        "naissance (R. 13, L. 12 bis) ; l'interruption ou la réduction "
        "d'activité de L. 12, b, que le dépôt présume de la mère seule ; la "
        "bonification de L. 12, b bis, aux femmes qui ont accouché pendant "
        "leurs études, que ni l'un ni l'autre ne lit ; les conditions "
        "d'éducation de L. 18, que le dépôt présume remplies."
    ),
}

#: Profils confrontés. ``objet`` dit ce que chacun éprouve ; ``hors_services``,
#: qu'un enfant au moins naît avant le recrutement.
PROFILS: tuple[dict, ...] = (
    {"code": "mere_quatre_enfants_2018", "regle": "au_dela_de_trois",
     "regime": "fonction_publique_etat", "sexe": "F", "naissance": 1956, "debut": 1998,
     "liquidation": 2018, "traitement": 40000.0,
     "naissances": ["1998-06-01", "2000-03-01", "2001-09-01", "2003-06-01"],
     "objet": "quatre enfants nés avant 2004 : seize trimestres, 15 % de majoration"},
    {"code": "cnracl_mere_cinq_enfants_2018", "regle": "au_dela_de_trois",
     "regime": "cnracl", "sexe": "F", "naissance": 1956, "debut": 1998,
     "liquidation": 2018, "traitement": 36000.0,
     "naissances": ["1998-05-01", "1999-09-01", "2001-01-01", "2002-05-01",
                    "2003-09-01"],
     "objet": "cinq enfants, à la CNRACL : vingt trimestres, 20 % de majoration"},
    {"code": "mere_sept_enfants_plafond_2014", "regle": "au_dela_de_trois",
     "regime": "fonction_publique_etat", "sexe": "F", "naissance": 1952, "debut": 1972,
     "liquidation": 2014, "traitement": 30000.0,
     "naissances": ["1988-02-01", "1989-04-01", "1990-06-01", "1991-08-01",
                    "1993-02-01", "1995-02-01", "1997-02-01"],
     "objet": "sept enfants : le pourcentage porté à 80 %, puis 30 % de majoration, "
              "que le traitement plafonne (L. 18)"},
    {"code": "pere_quatre_enfants_2018", "regle": "au_dela_de_trois",
     "regime": "fonction_publique_etat", "sexe": "H", "naissance": 1956, "debut": 1998,
     "liquidation": 2018, "traitement": 40000.0,
     "naissances": ["1998-06-01", "2000-03-01", "2001-09-01", "2003-06-01"],
     "objet": "le père de quatre enfants : aucune bonification, 15 % de majoration"},
    {"code": "mere_deux_enfants_apres_2004_2020", "regle": "nes_apres_2004",
     "regime": "fonction_publique_etat", "sexe": "F", "naissance": 1958, "debut": 1984,
     "liquidation": 2020, "traitement": 30000.0,
     "naissances": ["2004-06-01", "2007-06-01"],
     "objet": "deux enfants nés depuis 2004 : quatre trimestres de durée, "
              "aucun de services (L. 12 bis)"},
    {"code": "cnracl_mere_deux_enfants_apres_2004_2020", "regle": "nes_apres_2004",
     "regime": "cnracl", "sexe": "F", "naissance": 1958, "debut": 1984,
     "liquidation": 2020, "traitement": 27000.0,
     "naissances": ["2004-06-01", "2007-06-01"],
     "objet": "la même, à la CNRACL"},
    {"code": "mere_de_part_et_d_autre_de_2004_2020", "regle": "nes_apres_2004",
     "regime": "fonction_publique_etat", "sexe": "F", "naissance": 1958, "debut": 1984,
     "liquidation": 2020, "traitement": 30000.0,
     "naissances": ["2002-06-01", "2005-06-01"],
     "objet": "un enfant de chaque côté de 2004 : quatre trimestres de "
              "bonification, deux de majoration"},
    {"code": "mere_enfants_avant_recrutement_2009", "regle": "hors_services",
     "regime": "fonction_publique_etat", "sexe": "F", "naissance": 1949, "debut": 1985,
     "liquidation": 2009, "traitement": 30000.0, "hors_services": True,
     "naissances": ["1978-03-01", "1980-03-01"],
     "objet": "deux enfants nés avant le recrutement, pension de 2009 : R. 13 "
              "exige alors une interruption dans un congé du statut"},
    {"code": "mere_enfants_avant_recrutement_2015", "regle": "hors_services",
     "regime": "fonction_publique_etat", "sexe": "F", "naissance": 1953, "debut": 1985,
     "liquidation": 2015, "traitement": 30000.0, "hors_services": True,
     "naissances": ["1978-03-01", "1980-03-01"],
     "objet": "les mêmes, pension de 2015 : R. 13 admet depuis 2011 l'enfant "
              "né avant la radiation"},
    {"code": "mere_accouchement_avant_recrutement_2020", "regle": "hors_services",
     "regime": "fonction_publique_etat", "sexe": "F", "naissance": 1958, "debut": 2006,
     "liquidation": 2020, "traitement": 40000.0, "hors_services": True,
     "naissances": ["2005-06-01"],
     "objet": "un enfant né en 2005, avant le recrutement : L. 12 bis ne va qu'à "
              "la femme qui accouche après"},
)

#: Grandeurs relevées : celles de la première famille, et le détail de ce que
#: les enfants ajoutent.
GRANDEURS = {
    **frere.GRANDEURS,
    "bonification_enfants": "bonification_cpcm_enfant",
    "majoration_duree_enfants": "majoration_duree_assurance_enfant",
    "majoration_duree": "majoration_duree_assurance",
}


def entrees(profil: dict) -> dict:
    """La situation qu'OpenFisca reçoit : la carrière de la première famille,
    sans ses enfants, puis les enfants de cette convention."""
    situation = frere.entrees({**profil, "naissances": []})
    naissances = sorted(profil.get("naissances", []))
    situation["nombre_enfants"] = {"ETERNITY": len(naissances)}
    prefixe, _ = frere.REGIMES[profil["regime"]]
    situation[f"{prefixe}_nombre_enfants_nes_avant_2004"] = {
        "ETERNITY": sum(n < BONIFICATION_AVANT for n in naissances)}
    if len(naissances) >= frere.ENFANTS_DU_DEPART:
        situation["date_naissance_enfant"] = {
            "ETERNITY": naissances[frere.ENFANTS_DU_DEPART - 1]}
    return situation


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
    table = tbs.parameters(f"{profil['liquidation']}-01-01").retraites.secteur_public \
        .pension_civile.trimtp.nombre_trimestres_cibles_taux_plein_par_generation
    mesures["duree_requise_de_la_generation"] = float(
        table[np.array([f"{profil['naissance']}-01-01"], dtype="datetime64[D]")][0])
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
        print(f"{profil['code']:<42} durée {mesures['duree_assurance']:>5.0f}  "
              f"services {mesures['services']:>5.0f}  "
              f"bonif. {mesures['bonification_enfants']:>3.0f}  "
              f"maj. {mesures['majoration_duree_enfants']:>3.0f}  "
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
        "famille": "les enfants des fonctionnaires : bonification, majoration de "
                   "durée et majoration de pension, au-delà de trois enfants, nés "
                   "après 2004 ou hors des services",
        "avertissement": (
            "Deuxième implémentation, pas une source officielle. Il ne lit ni le "
            "recrutement ni la radiation : il accorde la bonification de L. 12, b, "
            "à l'enfant né avant le recrutement d'une pension d'avant 2011, et la "
            "majoration de L. 12 bis à la femme qui a accouché avant le sien ; à "
            "la CNRACL, sa majoration de L. 12 bis lit la date de liquidation de "
            "l'État, et n'est jamais servie."
        ),
        "perimetre": (
            "Fonction publique de l'État et CNRACL, sédentaires sans prime, à temps "
            "plein, carrières continues à traitement nominal constant, liquidations "
            "de 2009 à 2020 : quatre parents de quatre à sept enfants, trois mères "
            "d'enfants nés depuis 2004, trois mères d'enfants nés avant leur "
            "recrutement."
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
