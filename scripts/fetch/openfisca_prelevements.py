#!/usr/bin/env python3
"""Récupération des prélèvements sur salaire AUTRES que la retraite.

    python scripts/fetch/openfisca_prelevements.py

Le modèle sait, depuis toujours, ce qui est prélevé pour la RETRAITE : c'est
la grandeur qui alimente le compte notionnel, et les fiches de régime la
portent régime par régime. Il ne savait rien du reste, et le reste est ce qui
sépare un salaire brut d'un salaire net : maladie, famille, chômage, accidents
du travail, CSG, CRDS. Sans lui, on ne peut ni écrire un salaire net, ni dire
de combien une réforme des retraites le déplace.

Ce récupérateur va chercher ces taux dans **OpenFisca-France**, comme
``openfisca_cotisations.py`` va chercher les taux vieillesse : c'est la seule
transcription machine complète et datée des décrets, et elle cite ses
références. La fiabilité est donc plafonnée à ``haute`` — OpenFisca transcrit
le Journal officiel, il ne le produit pas.

CINQ FAMILLES SONT RÉCUPÉRÉES
-----------------------------
1. **Cotisations de sécurité sociale** hors vieillesse : maladie-maternité-
   invalidité-décès, allocations familiales, accidents du travail et maladies
   professionnelles, contribution de solidarité pour l'autonomie.
2. **Assurance chômage** : la contribution de l'employeur et la cotisation AGS
   (la part salariale est nulle depuis le 1er octobre 2018).
3. **Contributions sociales** : CSG déductible, CSG imposable, CRDS, et
   l'abattement d'assiette pour frais professionnels qui leur est commun.
4. **Retraite complémentaire du privé, ce qui n'ouvre AUCUN droit** : la
   contribution d'équilibre général (CEG), la contribution d'équilibre
   technique (CET) et la cotisation APEC des cadres. Les fiches de régime ne
   les portent pas — et c'est correct, puisqu'elles n'acquièrent pas de point —
   mais elles sont prélevées, donc elles creusent l'écart entre le brut et le
   net. Les ignorer sous-estimait de 0,86 point le prélèvement retraite
   salarial d'un salarié du privé.
5. **Réduction générale dégressive unique** (RGDU), qui depuis le 1er janvier
   2026 remplace la réduction Fillon et les deux « bandeaux » maladie et
   famille : ses quatre paramètres, et la liste des taux dont la somme fait
   son coefficient maximal.

CE QUI N'EST PAS RÉCUPÉRÉ, ET POURQUOI
--------------------------------------
Les taxes assises sur les salaires qui ne financent aucune assurance sociale —
apprentissage, formation professionnelle, participation à la construction,
versement mobilité. Elles pèsent sur le coût du travail, mais le versement
mobilité dépend de la commune et les autres de la taille de l'entreprise :
les porter demanderait de choisir un employeur type, et elles ne bougent
d'aucun scénario de retraite. ``docs/limites.md`` le dit.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RACINE = ("https://raw.githubusercontent.com/openfisca/openfisca-france/master/"
          "openfisca_france/parameters/prelevements_sociaux")
SORTIE = Path("data/brut/openfisca_prelevements.json")

#: Paramètres SIMPLES — un taux, daté. Nom retenu -> chemin sous RACINE.
VALEURS = {
    "csg_deductible": "contributions_sociales/csg/activite/deductible.yaml",
    "csg_imposable": "contributions_sociales/csg/activite/imposable.yaml",
    "crds": "contributions_sociales/crds.yaml",
    "accidents_travail_moyen": (
        "cotisations_securite_sociale_regime_general/accidents/taux/moyen.yaml"),
    "maladie_employeur_taux_normal": (
        "cotisations_securite_sociale_regime_general/mmid/tx_normal.yaml"),
    "maladie_employeur_taux_reduit": (
        "cotisations_securite_sociale_regime_general/mmid/tx_red.yaml"),
    "famille_employeur_taux_reduit": (
        "cotisations_securite_sociale_regime_general/famille/taux_reduit.yaml"),
    "rgdu_plafond_smic": (
        "reductions_cotisations_sociales/allegement_general/"
        "ensemble_des_entreprises/plafond.yaml"),
    "rgdu_puissance": (
        "reductions_cotisations_sociales/allegement_general/"
        "ensemble_des_entreprises/puissance.yaml"),
    "rgdu_taux_minimum": (
        "reductions_cotisations_sociales/allegement_general/"
        "ensemble_des_entreprises/t_min.yaml"),
    "rgdu_taux_delta_grandes": (
        "reductions_cotisations_sociales/allegement_general/"
        "ensemble_des_entreprises/t_delta_grandes_entreprises.yaml"),
    "rgdu_taux_delta_petites": (
        "reductions_cotisations_sociales/allegement_general/"
        "ensemble_des_entreprises/t_delta_petites_entreprises.yaml"),
    "rgdu_seuil_effectif": (
        "reductions_cotisations_sociales/allegement_general/"
        "ensemble_des_entreprises/seuil_taille_entreprise.yaml"),
}

#: Paramètres à TRANCHES — un taux par tranche de plafond de sécurité sociale.
BAREMES = {
    "maladie_salarie": (
        "cotisations_securite_sociale_regime_general/mmid/salarie/maladie.yaml"),
    "maladie_employeur": (
        "cotisations_securite_sociale_regime_general/mmid/employeur/maladie.yaml"),
    "famille_employeur": (
        "cotisations_securite_sociale_regime_general/famille/employeur/famille.yaml"),
    "csa_employeur": (
        "cotisations_securite_sociale_regime_general/csa/employeur/csa.yaml"),
    "chomage_salarie": (
        "cotisations_regime_assurance_chomage/chomage/salarie/chomage.yaml"),
    "chomage_employeur": (
        "cotisations_regime_assurance_chomage/chomage/employeur/chomage.yaml"),
    "ags_employeur": "cotisations_regime_assurance_chomage/ags/employeur/ags.yaml",
    "fnal_moins_de_50": (
        "autres_taxes_participations_assises_salaires/fnal/"
        "contribution_moins_de_50_salaries.yaml"),
    "fnal_50_et_plus": (
        "autres_taxes_participations_assises_salaires/fnal/"
        "contribution_plus_de_50_salaries.yaml"),
    "dialogue_social_employeur": (
        "autres_taxes_participations_assises_salaires/fin_syndic/"
        "financement_organisations_syndicales.yaml"),
    "csg_abattement": "contributions_sociales/csg/activite/abattement.yaml",
    "ceg_salarie": "regimes_complementaires_retraite_secteur_prive/ceg/salarie/ceg.yaml",
    "ceg_employeur": (
        "regimes_complementaires_retraite_secteur_prive/ceg/employeur/ceg.yaml"),
    "cet_salarie": (
        "regimes_complementaires_retraite_secteur_prive/cet2019/salarie/cet2019.yaml"),
    "cet_employeur": (
        "regimes_complementaires_retraite_secteur_prive/cet2019/employeur/"
        "cet2019.yaml"),
    "apec_salarie": (
        "regimes_complementaires_retraite_secteur_prive/apec/salarie/apec.yaml"),
    "apec_employeur": (
        "regimes_complementaires_retraite_secteur_prive/apec/employeur/apec.yaml"),
    "agirc_arrco_salarie": (
        "regimes_complementaires_retraite_secteur_prive/agirc_arrco/salarie/"
        "agirc_arrco.yaml"),
    "agirc_arrco_employeur": (
        "regimes_complementaires_retraite_secteur_prive/agirc_arrco/employeur/"
        "agirc_arrco.yaml"),
}


def _telecharger(chemin: str) -> dict:
    import yaml  # PyYAML est la seule dépendance du modèle

    url = f"{RACINE}/{chemin}"
    with urllib.request.urlopen(url, timeout=60) as reponse:
        return yaml.safe_load(reponse.read().decode("utf-8"))


def _dates_valeurs(bloc: dict) -> list[tuple[str, float | None]]:
    """Les couples (date d'effet, valeur) d'un paramètre simple, triés."""
    return [
        (str(quand), (valeur or {}).get("value"))
        for quand, valeur in sorted((bloc or {}).items())
    ]


def _valeur_a(couples: list[tuple[str, float | None]], jour: str) -> float | None:
    applicables = [valeur for quand, valeur in couples if quand <= jour]
    return applicables[-1] if applicables else None


def _bareme_a(document: dict, jour: str) -> list[dict]:
    """Les tranches d'un barème à une date : seuil en plafonds, et taux."""
    tranches = []
    for tranche in document.get("brackets", []):
        seuil = _valeur_a(_dates_valeurs(tranche.get("threshold", {})), jour)
        taux = _valeur_a(_dates_valeurs(tranche.get("rate", {})), jour)
        if seuil is None or taux is None:
            continue
        tranches.append({"seuil_en_plafonds": seuil, "taux": taux})
    return sorted(tranches, key=lambda t: t["seuil_en_plafonds"])


def _references(document: dict) -> list[str]:
    """Les textes cités par OpenFisca, à plat, pour que la fiche les porte."""
    metadonnees = document.get("metadata", {}) or {}
    titres: list[str] = []
    for entrees in (metadonnees.get("reference", {}) or {}).values():
        if isinstance(entrees, dict):
            entrees = [entrees]
        for entree in entrees or []:
            titre = (entree or {}).get("title")
            if titre and titre not in titres:
                titres.append(titre)
    return titres


def main() -> int:
    jour = f"{date.today().year}-01-01"
    recueil: dict[str, dict] = {}
    try:
        for nom, chemin in sorted(VALEURS.items()):
            document = _telecharger(chemin)
            couples = _dates_valeurs(document.get("values", {}))
            recueil[nom] = {
                "chemin": chemin,
                "description": document.get("description", ""),
                "valeur_au_1er_janvier": _valeur_a(couples, jour),
                "historique": [
                    {"a_compter_du": quand, "valeur": valeur}
                    for quand, valeur in couples
                ],
                "textes": _references(document),
                "derniere_verification_openfisca":
                    (document.get("metadata", {}) or {}).get(
                        "last_value_still_valid_on"),
            }
        for nom, chemin in sorted(BAREMES.items()):
            document = _telecharger(chemin)
            recueil[nom] = {
                "chemin": chemin,
                "description": document.get("description", ""),
                "tranches_au_1er_janvier": _bareme_a(document, jour),
                "textes": _references(document),
                "derniere_verification_openfisca":
                    (document.get("metadata", {}) or {}).get(
                        "last_value_still_valid_on"),
            }
    except (urllib.error.URLError, urllib.error.HTTPError) as erreur:
        print(f"échec du téléchargement : {erreur}", file=sys.stderr)
        return 1

    document = {
        "source": RACINE,
        "recupere_le": date.today().isoformat(),
        "valeurs_au": jour,
        "avertissement": (
            "Transcription tierce du Journal officiel : fiabilité plafonnée à "
            "« haute », jamais « certifiee ». Les taux sont ceux EN VIGUEUR AU "
            "1er JANVIER de l'année courante, comme partout dans le dépôt."
        ),
        "parametres": recueil,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"{SORTIE} : {len(recueil)} paramètres, au {jour}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
