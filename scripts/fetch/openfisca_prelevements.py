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

SEPT FAMILLES SONT RÉCUPÉRÉES
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
6. **Secteur public** : la retenue pour pension du titulaire, la contribution
   de son employeur — un taux d'ÉQUILIBRE, que la fiche de paie n'affiche pas,
   et qui n'est récupéré ici que pour qu'on puisse le lire —, la cotisation
   maladie de l'État et des collectivités, la contribution exceptionnelle de
   solidarité (nulle depuis 2018), le RAFP et l'Ircantec.
7. **Travailleurs indépendants** : maladie-maternité, indemnités journalières,
   invalidité-décès, allocations familiales, retraite de base et RCI, formation
   professionnelle.

CE QU'OPENFISCA NE SAIT PLUS, ET QU'IL A FALLU LIRE À LA SOURCE
----------------------------------------------------------------
Les deux barèmes PROGRESSIFS des indépendants — maladie et maternité,
allocations familiales — sont dans OpenFisca dans leur rédaction de 2018, que
la réforme de l'assiette unique de 2024 a remplacée : le fichier de données les
porte donc dans la version lue dans l'index LEGI du dépôt (D. 621-1, D. 621-2 et
D. 613-1, en vigueur), et ce récupérateur ne sert plus, pour eux, qu'à voir si
OpenFisca rattrape son retard. `derniere_verification_openfisca` le dit poste
par poste.

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
    # -- indépendants : les taux qui ne dépendent pas du niveau de revenu ----
    "independant_invalidite_deces_artisans": (
        "cotisations_taxes_independants_artisans_commercants/deces_ac/"
        "artisans/sous_pss.yaml"),
    "independant_invalidite_deces_commercants": (
        "cotisations_taxes_independants_artisans_commercants/deces_ac/"
        "commercants_industriels/apres_2004/sous_pss.yaml"),
    "independant_famille_seuil_bas": (
        "cotisations_taxes_independants_artisans_commercants/famille/"
        "famille_ind/si_revenu_d_activite_110_pss.yaml"),
    "independant_famille_seuil_haut": (
        "cotisations_taxes_independants_artisans_commercants/famille/"
        "famille_ind/si_revenu_d_activite_140_pss.yaml"),
    "independant_maladie_entre_1_1_et_5_pss": (
        "cotisations_taxes_independants_artisans_commercants/mmid/mmid_ac/"
        "assures_actifs/entre_11_5_pss_2.yaml"),
    "independant_maladie_au_dela_de_5_pss": (
        "cotisations_taxes_independants_artisans_commercants/mmid/mmid_ac/"
        "assures_actifs/dela_5_pss.yaml"),
    "independant_retraite_base_sous_pss": (
        "cotisations_taxes_independants_artisans_commercants/ret_ac/"
        "artisans/sous_pss.yaml"),
    "independant_retraite_base_deplafonnee": (
        "cotisations_taxes_independants_artisans_commercants/ret_ac/"
        "tous_independants/tout_salaire.yaml"),
    "independant_rci_sous_plafond": (
        "cotisations_taxes_independants_artisans_commercants/ret_comp_ac/"
        "art_ind_com/sous_plafond_rci.yaml"),
    "independant_rci_au_dela_du_plafond": (
        "cotisations_taxes_independants_artisans_commercants/ret_comp_ac/"
        "art_ind_com/entre_1_plafond_rci_et_4_plafonds_pss.yaml"),
    "independant_plafond_rci": (
        "cotisations_taxes_independants_artisans_commercants/ret_comp_ac/"
        "art_ind_com/montant_du_plafond_rci.yaml"),
    "independant_formation_artisans": (
        "cotisations_taxes_independants_artisans_commercants/formation_ac/"
        "artisans/sous_pss.yaml"),
    "independant_formation_commercants": (
        "cotisations_taxes_independants_artisans_commercants/formation_ac/"
        "commercants_industriels/sous_pss.yaml"),
    # -- secteur public : la SNCF, dont le taux salarié est une valeur simple -
    "sncf_cotisation_salarie": (
        "cotisations_secteur_public/sncf/regime_de_retraite/"
        "cotisations_employes.yaml"),
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
    # -- secteur public -----------------------------------------------------
    # La retenue de l'agent est la seule de ces lignes qui entre dans la fiche
    # de paie. Les trois contributions d'employeur sont récupérées pour être
    # LUES, non pour être affichées : ce sont des taux d'équilibre, et le
    # docstring de `remuneration.py` dit pourquoi le site refuse de les
    # présenter comme un coût du travail.
    "pension_civile_salarie": (
        "cotisations_secteur_public/retraite/pension/salarie/pension.yaml"),
    "pension_civile_employeur": (
        "cotisations_secteur_public/retraite/pension/employeur/civils/"
        "pension.yaml"),
    "pension_militaire_employeur": (
        "cotisations_secteur_public/retraite/pension/employeur/militaires/"
        "pension.yaml"),
    "cnracl_salarie": "cotisations_secteur_public/cnracl/salarie/cnracl_s_ti.yaml",
    "cnracl_employeur": "cotisations_secteur_public/cnracl/employeur/cnracl.yaml",
    # Les deux suivantes disent que le salarial public est nul : c'est le
    # RÉSULTAT qui autorise la liste de postes vide du profil `agent_seul`.
    "maladie_etat_salarie": (
        "cotisations_secteur_public/mmid/etat/tout_traitement/salarie/"
        "maladie.yaml"),
    "maladie_etat_employeur": (
        "cotisations_secteur_public/mmid/etat/tout_traitement/employeur/"
        "maladie.yaml"),
    "maladie_collectivites_salarie": (
        "cotisations_secteur_public/mmid/colloc/tout_traitement/salarie/"
        "maladie.yaml"),
    "maladie_collectivites_employeur": (
        "cotisations_secteur_public/mmid/colloc/tout_traitement/employeur/"
        "maladie.yaml"),
    "solidarite_fonction_publique": (
        "cotisations_secteur_public/fds/salarie/solidarite.yaml"),
    "rafp_salarie": "cotisations_secteur_public/rafp/salarie/rafp.yaml",
    "rafp_employeur": "cotisations_secteur_public/rafp/employeur/rafp.yaml",
    "ircantec_salarie": (
        "cotisations_secteur_public/ircantec/taux_cotisations_appeles/salarie/"
        "ircantec.yaml"),
    "ircantec_employeur": (
        "cotisations_secteur_public/ircantec/taux_cotisations_appeles/"
        "employeur/ircantec.yaml"),
    # -- indépendants : les barèmes par tranche -----------------------------
    "independant_indemnites_journalieres_artisans": (
        "cotisations_taxes_independants_artisans_commercants/mmid/arti/"
        "indjour.yaml"),
    "independant_indemnites_journalieres_commercants": (
        "cotisations_taxes_independants_artisans_commercants/mmid/comind/"
        "indjour.yaml"),
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
