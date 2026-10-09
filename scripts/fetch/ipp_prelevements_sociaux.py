#!/usr/bin/env python3
"""Les prélèvements sur les pensions et sur les salaires, date par date, chez l'IPP.

    python scripts/fetch/ipp_prelevements_sociaux.py           # réécrit la donnée
    python scripts/fetch/ipp_prelevements_sociaux.py --lister  # imprime, sans écrire

À quoi il sert. Les indicateurs de cycle de vie nets (action 138, étape 9 ;
``retraite_notionnelle/cycle_de_vie.py``) rapportaient une pension nette des
prélèvements de 2026 à un salaire net des prélèvements de 2026, quelle que soit
l'année. Ce script lit chez l'IPP l'histoire de ces prélèvements — la CSG, la
CRDS, la CASA et la cotisation maladie des pensions ; la CSG, la CRDS, la
maladie, le veuvage, l'assurance chômage des salaires du privé, la maladie et
la contribution de solidarité des agents publics — et l'écrit, marche par
marche, dans ``data/reference/legislation/prelevements_historiques.yaml``.

LES CONVENTIONS DE L'IPP. Chaque barème est un CSV daté, du plus récent au plus
ancien, et chaque ligne est une PHOTOGRAPHIE : elle répète tous les taux en
vigueur à sa date — le 0,75 % de la maladie salariale en 2016 et en 2017, le
6,6 % de la CSG des pensions de 2005 à 2017. Une cellule vide après une valeur
dit donc qu'un taux n'est plus en vigueur, même quand la ligne en porte
d'autres : la maladie salariale au 1er janvier 2018 (les cellules de
l'employeur restent pleines), le chômage salarié au 1er octobre 2018, le
veuvage au 1er juillet 2004, la maladie des agents publics et celle des
pensions du régime général au 1er janvier 1998 — le décret n° 97-1252 ne la
fixe plus, quand la CSG des pensions monte des mêmes 2,8 points —, la
contribution de solidarité au 1er janvier 2018. Une cellule vide avant toute
valeur dit qu'un taux n'existe pas encore (le taux médian de CSG avant 2019).

AVANT LA PREMIÈRE MARCHE. La CSG (1991), la CRDS (1996), la CASA (2013), la
maladie des pensions (1980), le veuvage (1981), la solidarité (1982) et
l'assurance chômage (1959) sont nés à leur première marche, et ne prélèvent
rien avant. La maladie des salariés et des agents publics existait avant 1967,
où commencent les barèmes de l'IPP : ses taux de 1967 sont tenus en deçà
(`tenues_avant_leur_premiere_marche`), et le dépôt le dit.

Ce qu'il ne fait pas. L'IPP est une transcription, non une source productrice :
la donnée plafonne à ``haute``. Il n'ancre pas chaque marche au Journal officiel
(``ipp_taux_cotisation.py`` le fait pour la vieillesse) : l'index de la DILA
n'était pas présent quand il a été écrit ; les références que l'IPP cite sont
gardées, marche par marche.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import sys
import urllib.request
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parents[2]
SORTIE = RACINE_DEPOT / "data" / "reference" / "legislation" / "prelevements_historiques.yaml"
RACINE = "https://baremes.ipp.eu/parameters/prelevements-sociaux"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
FRANC = 6.55957

#: Chaque série écrite : son chemin dans la donnée, le barème de l'IPP, et ses
#: colonnes — le nom qu'elles prennent, la colonne de l'IPP.
SERIES = {
    ("pensions", "csg_taux_plein"): (
        "prelevements_sociaux.contributions_sociales.csg.remplacement",
        {"taux": "pensions_retraite_invalidite.taux_plein"}),
    ("pensions", "csg_taux_median"): (
        "prelevements_sociaux.contributions_sociales.csg.remplacement",
        {"taux": "pensions_retraite_invalidite.taux_median"}),
    ("pensions", "csg_taux_reduit"): (
        "prelevements_sociaux.contributions_sociales.csg.remplacement",
        {"taux": "pensions_retraite_invalidite.taux_reduit"}),
    ("pensions", "crds"): (
        "prelevements_sociaux.contributions_sociales.crds",
        {"taux": "prelevements_sociaux.contributions_sociales.crds"}),
    ("pensions", "casa"): (
        "prelevements_sociaux.cotisations_securite_sociale_regime_general.casa",
        {"taux": "pensions_retraite_preretraite_invalidite.0-"}),
    ("pensions", "maladie_regime_general"): (
        "prelevements_sociaux.cotisations_securite_sociale_regime_general.mmid_ret",
        {"taux": "avantages_de_retraite.regime_general"}),
    ("pensions", "maladie_complementaires"): (
        "prelevements_sociaux.cotisations_securite_sociale_regime_general.mmid_ret",
        {"taux": "avantages_de_retraite.regimes_comp"}),
    ("salaires", "csg"): (
        "prelevements_sociaux.contributions_sociales.csg.activite",
        {"taux": "taux_global", "abattement": "abattement.0-",
         "abattement_jusqu_a_quatre_plafonds": "abattement.0-4"}),
    ("salaires", "crds"): (
        "prelevements_sociaux.contributions_sociales.crds",
        {"taux": "prelevements_sociaux.contributions_sociales.crds"}),
    ("salaires", "maladie_prive"): (
        "prelevements_sociaux.cotisations_securite_sociale_regime_general.mmid",
        {"tout_salaire": "salarie.maladie.0-", "sous_plafond": "salarie.maladie.0-1",
         "au_dela_du_plafond": "salarie.maladie.1-"}),
    ("salaires", "veuvage_prive"): (
        "prelevements_sociaux.cotisations_securite_sociale_regime_general.veuvage",
        {"tout_salaire": "salaries.sur_tout_salaire", "sous_plafond": "salaries.sous_plafond"}),
    ("salaires", "chomage_prive"): (
        "prelevements_sociaux.cotisations_regime_assurance_chomage.chomage",
        {"tout_salaire": "salarie.chomage.0-", "sous_plafond": "salarie.chomage.0-1",
         "de_un_a_quatre_plafonds": "salarie.chomage.1-4"}),
    ("salaires", "maladie_etat"): (
        "prelevements_sociaux.cotisations_secteur_public.mmid.etat",
        {"tout_salaire": "tout_traitement.salarie.maladie.0-",
         "sous_plafond": "sous_plafond.salarie.maladie.0-1"}),
    ("salaires", "maladie_collectivites"): (
        "prelevements_sociaux.cotisations_secteur_public.mmid.colloc",
        {"tout_salaire": "tout_traitement.salarie.maladie.0-",
         "sous_plafond": "sous_plafond.salarie.maladie.0-1"}),
    ("salaires", "solidarite_public"): (
        "prelevements_sociaux.cotisations_secteur_public.fds",
        {"taux": "salarie.solidarite.0-4", "seuil_mensuel": "salarie.seuil_d_assujettissement"}),
}

#: Les séries dont l'IPP ne donne pas la naissance : leur première marche est
#: tenue en deçà d'elle, au lieu de zéro.
TENUES_AVANT = ("maladie_prive", "maladie_etat", "maladie_collectivites")


def _telecharger(parametre: str) -> list[dict[str, str]]:
    demande = urllib.request.Request(f"{RACINE}/{parametre}/csv", headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=180) as reponse:
        return list(csv.DictReader(io.StringIO(reponse.read().decode("utf-8"))))


def _nombre(brut: str) -> float | None:
    """« 6,55 % » -> 0.0655 ; « 1 439,35 € » -> 1439.35 ; « 8 157,58 FRF » en
    euros. Une cellule vide rend ``None``."""
    texte = (brut or "").replace(" ", " ").replace("\xa0", " ").strip()
    if not texte:
        return None
    francs = texte.endswith("FRF")
    pourcent = texte.endswith("%")
    nombre = float(texte.replace("%", "").replace("€", "").replace("FRF", "")
                   .replace(" ", "").replace(",", "."))
    if pourcent:
        return round(nombre / 100.0, 8)
    return round(nombre / FRANC, 2) if francs else nombre


def _jour(brut: str) -> str:
    jour, mois, annee = (int(x) for x in brut.split("/"))
    return dt.date(annee, mois, jour).isoformat()


def marches(lignes: list[dict[str, str]], colonnes: dict[str, str]) -> list[dict]:
    """Les marches d'une série, de la plus ancienne à la plus récente : une
    marche par date où ses valeurs changent. Chaque ligne est une photographie
    des taux en vigueur ; une colonne vide après une valeur vaut zéro."""
    lues: list[dict] = []
    for ligne in sorted(lignes, key=lambda l: _jour(l["date"])):
        valeurs = {nom: _nombre(ligne.get(colonne, "")) for nom, colonne in colonnes.items()}
        if not lues and all(v is None for v in valeurs.values()):
            continue
        valeurs = {nom: (0.0 if v is None else v) for nom, v in valeurs.items()}
        if lues and all(lues[-1][nom] == v for nom, v in valeurs.items()):
            continue
        reference = " ".join((ligne.get("reference") or "").split())
        lues.append({"depuis": _jour(ligne["date"]), **valeurs,
                     "texte": reference.split(";")[0].strip() or "IPP, sans référence"})
    # Une colonne qui n'est jamais en vigueur ne s'écrit pas.
    vides = [nom for nom in colonnes if all(m[nom] == 0.0 for m in lues)]
    return [{k: v for k, v in m.items() if k not in vides} for m in lues]


def _yaml(marche: dict) -> str:
    champs = []
    for cle, valeur in marche.items():
        if cle == "texte":
            champs.append(f'texte: "{valeur.replace(chr(34), chr(39))}"')
        elif cle == "depuis":
            champs.append(f'depuis: "{valeur}"')
        else:
            champs.append(f"{cle}: {valeur:g}" if isinstance(valeur, float) else f"{cle}: {valeur}")
    return "    - {" + ", ".join(champs) + "}"


ENTETE = """\
# Les prélèvements sur les pensions et sur les salaires, marche par marche
# -----------------------------------------------------------------------
# source_id: ipp_prelevements_sociaux
#
# ÉCRIT PAR `scripts/fetch/ipp_prelevements_sociaux.py`, jamais à la main : les
# barèmes de l'Institut des politiques publiques, lus le {lu_le}, chacun avec la
# référence que l'IPP cite pour sa marche. Une transcription, non une source
# productrice : `haute` au plus (data/sources.yaml, `ipp`).
#
# QUI LE LIT. Les indicateurs de cycle de vie nets
# (`retraite_notionnelle/cycle_de_vie.py`, action 138, étape 9) : la pension
# nette de chaque année aux taux de son année, le salaire net de chaque année
# aux siens. La fiche de paie du site et la pension nette qu'il affiche restent
# aux taux de l'année courante (`prelevements_remuneration.yaml`), qui doivent
# rendre ceux de la dernière marche de chaque série : un test le tient.
#
# LES SÉRIES. Un taux s'entend en part de son assiette ; chaque marche dit
# tous les taux en vigueur à sa date, zéro compris. Une contribution n'existait
# pas avant sa première marche, sauf celles de `tenues_avant_leur_premiere_marche`,
# la maladie, que les barèmes de l'IPP ne prennent qu'en 1967 : leurs taux de
# 1967 valent en deçà.
#   pensions : la CSG au taux plein, médian, réduit ; la CRDS ; la CASA ; la
#     cotisation maladie des pensions du régime général et celle des
#     complémentaires (les régimes de `maladie_complementaire`).
#   salaires : la CSG et la CRDS d'activité, sur le brut abattu de
#     `abattement` (sans limite) ou de `abattement_jusqu_a_quatre_plafonds`
#     (jusqu'à quatre plafonds, depuis 2011) — l'IPP n'en donne pas avant 1998,
#     et le dépôt n'en retient pas ; la maladie, le veuvage et l'assurance
#     chômage du salarié du privé, `tout_salaire`, `sous_plafond`,
#     `au_dela_du_plafond`, `de_un_a_quatre_plafonds` ; la maladie des agents de
#     l'État et des collectivités ; la contribution exceptionnelle de solidarité
#     des agents publics, au-delà d'un seuil mensuel en euros.
#
# CE QUE L'IPP NE DIT PAS. Le taux de la maladie des pensions des autres régimes
# de base (la fonction publique, les indépendants) : seule celle du régime
# général est écrite ; le dépôt n'en prélève donc aucune ailleurs.
"""


def ecrire(series: dict[tuple[str, str], list[dict]], lu_le: str) -> str:
    lignes = [ENTETE.format(lu_le=lu_le).rstrip("\n"), f'lu_le: "{lu_le}"', "fiabilite: haute",
              f"tenues_avant_leur_premiere_marche: [{', '.join(TENUES_AVANT)}]"]
    for partie in ("pensions", "salaires"):
        lignes += ["", f"{partie}:"]
        for (bloc, nom), marches_lues in series.items():
            if bloc != partie:
                continue
            lignes.append(f"  {nom}:")
            lignes += [_yaml(marche) for marche in marches_lues]
    return "\n".join(lignes) + "\n"


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--lister", action="store_true", help="imprime sans écrire")
    arguments = analyseur.parse_args(argv)
    telecharges: dict[str, list[dict[str, str]]] = {}
    series = {}
    for cle, (parametre, colonnes) in SERIES.items():
        if parametre not in telecharges:
            telecharges[parametre] = _telecharger(parametre)
        series[cle] = marches(telecharges[parametre], colonnes)
    texte = ecrire(series, dt.date.today().isoformat())
    if arguments.lister:
        print(texte)
        return 0
    SORTIE.write_text(texte, encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE_DEPOT)} : {sum(len(m) for m in series.values())} marches")
    return 0


if __name__ == "__main__":
    sys.exit(main())
