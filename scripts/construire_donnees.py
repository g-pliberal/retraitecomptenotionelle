#!/usr/bin/env python3
"""Fabrique ce que le site charge : ``moteur/donnees.json`` et ``moteur/style.css``.

Le site s'exécute en JavaScript ; les données, elles, restent écrites en YAML et
en CSV dans ``data/``, où elles sont lisibles, commentées et recontrôlées contre
leurs sources. Ce script fait le pont : il charge les données **par les
chargeurs Python du modèle** — donc avec exactement les mêmes conversions,
valeurs par défaut et niveaux de fiabilité — et les écrit en un seul fichier
JSON que le navigateur récupère en une requête.

Faire passer les données par le modèle Python plutôt que de relire les fichiers
à la main est délibéré : la normalisation (champs absents, ``None``, familles de
régimes, niveaux de fiabilité) n'existe qu'à un seul endroit, et le paquet ne
peut pas diverger de ce que calcule la référence.

La feuille de style suit le même chemin : elle est écrite une seule fois, dans
``web/gabarit.py``, et extraite ici vers ``moteur/style.css`` que la page charge
directement. Le rendu de référence et le site ne peuvent donc pas diverger
d'apparence.

    python scripts/construire_donnees.py            # reconstruit les deux fichiers
    python scripts/construire_donnees.py --verifier # échoue s'ils sont périmés

Ils sont versionnés dans le dépôt, pour que le site n'ait aucune étape de
construction : ouvrir l'adresse suffit. Il faut donc les reconstruire après toute
modification des données ou du style — le test ``test_le_paquet_est_a_jour`` y
veille.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.carriere import Affiliations  # noqa: E402
from retraite_notionnelle.donnees.assiette import POSTES_ASSIETTE  # noqa: E402
from retraite_notionnelle.donnees.chargement import (  # noqa: E402
    SerieAnnuelle,
    charger_serie_annuelle,
    charger_yaml,
    journal_certification,
)
from retraite_notionnelle.donnees.depenses import SYSTEMES  # noqa: E402
from retraite_notionnelle.donnees.equilibre import POSTES, POSTES_TRANSFERTS  # noqa: E402
from retraite_notionnelle.donnees.distribution import (  # noqa: E402
    DistributionPensions,
)
from retraite_notionnelle.avantages import charger_avantages  # noqa: E402
from retraite_notionnelle.donnees.effectifs import EffectifsRetraites  # noqa: E402
from retraite_notionnelle.donnees.frais import FraisEpargneRetraite  # noqa: E402
from retraite_notionnelle.donnees.mortalite import DonneesMortalite  # noqa: E402
from retraite_notionnelle.remuneration import charger_prelevements  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.donnees.taux import CourbeTauxSansRisque  # noqa: E402
from retraite_notionnelle.donnees.regimes import (  # noqa: E402
    CatalogueRegimes,
    charger_inventaire,
)
from retraite_notionnelle.scenarios.actuel import (  # noqa: E402
    AgesAnnulationDecote,
    AgesJouissanceMilitaire,
    AgesOuverture,
    AnneesSalaireReference,
    CoefficientsMinoration,
    DureesProratisation,
    DureesRequises,
    MajorationsPourEnfants,
    Rendements,
    SurcoteParentale,
    ValeursPoint,
)

DONNEES = RACINE / "data"
PAQUET = RACINE / "moteur" / "donnees.json"
STYLE = RACINE / "moteur" / "style.css"

#: Version du format. À incrémenter si la structure du paquet change, pour
#: qu'un site en cache ne lise pas un paquet qu'il ne comprend pas.
VERSION = 14


def _serie(serie: SerieAnnuelle) -> dict:
    """Série annuelle en trois tableaux parallèles — compact et sans ambiguïté."""
    annees = list(serie.annees())
    return {
        "interpolation": serie.interpolation,
        "annees": annees,
        "valeurs": [serie.brut(a).valeur for a in annees],
        "fiabilites": [int(serie.brut(a).fiabilite) for a in annees],
    }


def _series() -> dict:
    macro = DONNEES / "reference" / "macro"
    mortalite = DONNEES / "reference" / "mortalite" / "esperances_vie.csv"
    ages = DONNEES / "reference" / "legislation" / "ages_reference.csv"

    series = {
        "inflation": charger_serie_annuelle(
            macro / "ipc_annuel.csv", "variation", nom="inflation"),
        "salaire_moyen": charger_serie_annuelle(
            macro / "salaire_moyen.csv", "variation_nominale", nom="salaire_moyen_nominal"),
        "masse_salariale": charger_serie_annuelle(
            macro / "masse_salariale.csv", "variation_nominale",
            nom="masse_salariale_nominale"),
        "pib_nominal": charger_serie_annuelle(
            macro / "pib_nominal.csv", "variation_nominale", nom="pib_nominal"),
        "productivite": charger_serie_annuelle(
            macro / "productivite.csv", "variation_reelle", nom="productivite_reelle"),
        "pass": charger_serie_annuelle(
            macro / "plafond_securite_sociale.csv", "pass_eur", nom="pass"),
        "smic_horaire": charger_serie_annuelle(
            macro / "smic_horaire.csv", "smic_horaire", nom="smic_horaire"),
        "heures_par_trimestre": charger_serie_annuelle(
            DONNEES / "reference" / "legislation" / "validation_trimestres.csv",
            "heures", nom="heures_par_trimestre"),
    }
    for sexe in ("H", "F"):
        for mesure in ("e60", "e65"):
            series[f"{mesure}_{sexe}"] = charger_serie_annuelle(
                mortalite, "valeur", nom=f"{mesure}_{sexe}", interpolation="lineaire",
                filtre={"sexe": sexe, "mesure": mesure},
            )
    # Les âges légaux n'ont pas de colonne de fiabilité : le modèle les qualifie
    # de « haute ». On passe par le même chargeur que lui pour ne pas diverger.
    from retraite_notionnelle.moteur.age_reference import _charger_ages

    series["age_taux_plein_legal"] = _charger_ages(ages, "age_taux_plein_legal")
    series["age_reference"] = _charger_ages(ages, "age_reference")

    return {nom: _serie(serie) for nom, serie in sorted(series.items())}


def _depenses() -> dict:
    """Dépenses observées : le total, sa ventilation par système, et le PIB.

    Ces séries ne servent à AUCUN calcul de pension : elles ne portent que la
    page « Coût ». Elles passent quand même par le paquet, et par les mêmes
    chargeurs que le reste, pour la même raison que tout le reste — le site ne
    lit jamais data/ directement.
    """
    macro = DONNEES / "reference" / "macro"
    series = {
        "total": charger_serie_annuelle(
            macro / "depenses_retraite.csv", "depenses_meur",
            nom="depenses_retraite"),
        "pib_courant": charger_serie_annuelle(
            macro / "pib_courant.csv", "pib_meur", nom="pib_courant"),
    }
    for systeme in SYSTEMES:
        series[systeme.code] = charger_serie_annuelle(
            macro / "depenses_retraite_regimes.csv", "depenses_meur",
            nom=f"depenses_{systeme.code}", filtre={"regime": systeme.code})
    return {nom: _serie(serie) for nom, serie in sorted(series.items())}


def _comptes_retraite() -> dict:
    """Le compte du système de retraite : dépenses, ressources, structure.

    Ces séries ne servent à AUCUN calcul de pension non plus. Elles portent la
    section « solde » de la page « Coût », et elles passent par le paquet et par
    les mêmes chargeurs que tout le reste : le site ne lit jamais data/
    directement.
    """
    macro = DONNEES / "reference" / "macro"
    comptes = macro / "comptes_retraite.csv"
    series = {
        poste: charger_serie_annuelle(
            comptes, "part_pib", nom=f"comptes_retraite_{poste}",
            filtre={"poste": poste})
        for poste in ("depenses", "ressources")
    }
    for poste in POSTES:
        series[poste.code] = charger_serie_annuelle(
            macro / "structure_ressources_retraite.csv", "part",
            nom=f"structure_{poste.code}", filtre={"poste": poste.code})
    # Ce que la branche famille et l'assurance chômage versent, en millions
    # d'euros : la ventilation du poste « transferts », lue chez celui qui paie.
    for poste in POSTES_TRANSFERTS:
        series[f"transferts_{poste.code}"] = charger_serie_annuelle(
            macro / "transferts_retraite.csv", "montant_meur",
            nom=f"transferts_{poste.code}", filtre={"poste": poste.code})
    # L'assiette des revenus d'activité, en millions d'euros : ce sur quoi la
    # proposition prélève ses 18 %. Sans elle, un taux affiché ne se convertit
    # pas en recette.
    for code, _ in POSTES_ASSIETTE:
        series[f"assiette_{code}"] = charger_serie_annuelle(
            macro / "assiette_activite.csv", "montant_meur",
            nom=f"assiette_{code}", filtre={"poste": code})
    return {nom: _serie(serie) for nom, serie in sorted(series.items())}


def _effectifs_retraites() -> dict:
    """Retraités de droit direct par caisse — la pondération des cas types.

    Ces séries ne servent à AUCUNE pension : elles ne portent que les agrégats
    de la page « Coût », où elles disent ce que chaque cas type pèse.
    """
    effectifs = EffectifsRetraites(DONNEES)
    return {
        caisse: _serie(effectifs.serie(caisse)) for caisse in effectifs.caisses()
    }


def _distribution_pensions() -> dict:
    """Distribution des pensions : ce qui chiffre un plancher différentiel.

    Les tranches sont écrites en trois tableaux parallèles, comme les séries :
    la borne inférieure, la borne supérieure — ``null`` pour la tranche ouverte
    du haut — et la part des retraités.
    """
    distribution = DistributionPensions(DONNEES)
    return {
        "millesime": distribution.millesime,
        "sexe": distribution.sexe,
        "fiabilite": int(distribution.fiabilite),
        "bornes_inferieures": [t.borne_inferieure for t in distribution.tranches],
        "bornes_superieures": [t.borne_superieure for t in distribution.tranches],
        "parts": [t.part for t in distribution.tranches],
    }


def _population() -> dict:
    """Pyramide des âges : une matrice année × âge, et l'effectif d'âge actif.

    Écrite en trois tableaux parallèles plutôt qu'en dictionnaire de couples :
    six mille effectifs indexés par « 1962|50 » coûteraient trois fois leur
    poids en clés, pour la même information.
    """
    population = Population(DONNEES)
    annees = population.annees()
    ages = list(range(50, population.age_maximal + 1))
    return {
        "annees": annees,
        "ages": ages,
        "effectifs": [
            [population.effectif(age, annee) for age in ages] for annee in annees
        ],
        "fiabilites": [int(population.fiabilite(annee)) for annee in annees],
        "actifs": _serie(population.actifs),
    }


def _quotients() -> dict:
    """Quotients de mortalité observés, indexés « année|sexe » puis par âge."""
    donnees = DonneesMortalite(DONNEES, cache_disque=False)
    observes = donnees._quotients_observes or {}
    return {
        f"{annee}|{sexe}": {str(age): qx for age, qx in sorted(table.items())}
        for (annee, sexe), table in sorted(observes.items())
    }


def _calibrations() -> dict:
    """Paramètres de Makeham pour TOUTES les années utiles, pas seulement celles
    déjà rencontrées.

    Le modèle borne l'année aux extrémités de la série d'espérances de vie : le
    domaine est donc fini et connu. En le calibrant intégralement ici, le
    navigateur n'a plus qu'à lire une table — il ne refait aucune bissection, et
    les deux implémentations partent des mêmes paramètres au bit près.
    """
    donnees = DonneesMortalite(DONNEES)
    for sexe in DonneesMortalite.SEXES:
        serie = donnees._e60[sexe]
        for annee in range(serie.premiere_annee, serie.derniere_annee + 1):
            donnees.loi(annee, sexe)
    donnees.enregistrer_cache()
    return {cle: list(valeur) for cle, valeur in sorted(donnees._cache.items())}


def _regimes() -> list[dict]:
    catalogue = CatalogueRegimes(DONNEES)
    fiches = []
    # Ordre de chargement, et non ordre alphabétique : la fusion des régimes
    # départage les ex æquo par le premier rencontré, et c'est ce régime-là que
    # le rapport de simulation cite comme origine du paramètre retenu.
    for regime in catalogue:
        fiches.append({
            "code": regime.code,
            "nom": regime.nom,
            "famille": regime.famille,
            "source_id": regime.source_id,
            "fiabilite": int(regime.fiabilite),
            "creation": regime.creation,
            "fermeture": regime.fermeture,
            "extinction": regime.extinction,
            "succede_a": list(regime.succede_a),
            "integre_dans": regime.integre_dans,
            "population": regime.population,
            "hors_repartition": regime.hors_repartition,
            "periodes": [
                {
                    "debut": p.debut,
                    "fin": p.fin,
                    "type_calcul": p.type_calcul,
                    "age_ouverture": p.age_ouverture,
                    "age_taux_plein": p.age_taux_plein,
                    "duree_requise_trimestres": p.duree_requise_trimestres,
                    "duree_requise_par_generation": p.duree_requise_par_generation,
                    "duree_proratisation_par_generation":
                        p.duree_proratisation_par_generation,
                    "age_ouverture_par_generation": p.age_ouverture_par_generation,
                    "taux_plein": p.taux_plein,
                    "salaire_reference": p.salaire_reference,
                    "assiette": p.assiette,
                    "taux_cotisation_retraite": p.taux_cotisation_retraite,
                    "taux_cotisation_deplafonnee": p.taux_cotisation_deplafonnee,
                    "part_salariale_deplafonnee": p.part_salariale_deplafonnee,
                    "perimetre_taux": p.perimetre_taux,
                    "part_salariale": p.part_salariale,
                    "age_taux_plein_par_generation": p.age_taux_plein_par_generation,
                    "decote_par_generation": p.decote_par_generation,
                    "salaire_reference_par_generation": p.salaire_reference_par_generation,
                    "decote_par_trimestre": p.decote_par_trimestre,
                    "bareme_decote": p.bareme_decote,
                    "duree_maximum_avant_age": p.duree_maximum_avant_age,
                    "duree_maximum_avant_age_trimestres":
                        p.duree_maximum_avant_age_trimestres,
                    "decote_annulee_par_la_duree": p.decote_annulee_par_la_duree,
                    "decote_trimestres_maximum": p.decote_trimestres_maximum,
                    "surcote_par_trimestre": p.surcote_par_trimestre,
                    "surcote_bareme": p.surcote_bareme,
                    "abattement_points": p.abattement_points,
                    "surcote_points": p.surcote_points,
                    "surcote_age_debut": p.surcote_age_debut,
                    "surcote_age_maximum": p.surcote_age_maximum,
                    "surcote_trimestres_maximum": p.surcote_trimestres_maximum,
                    "surcote_pas_trimestres": p.surcote_pas_trimestres,
                    "surcote_palier_age": p.surcote_palier_age,
                    "surcote_par_trimestre_apres_palier":
                        p.surcote_par_trimestre_apres_palier,
                    "surcote_affiliation_minimale_trimestres":
                        p.surcote_affiliation_minimale_trimestres,
                    "plafond_majoration_enfants": p.plafond_majoration_enfants,
                    "plafond_majoration_annee": p.plafond_majoration_annee,
                    "points_maximum": p.points_maximum,
                    "points_minimum_annuels": p.points_minimum_annuels,
                    "points_par_trimestre_valide": p.points_par_trimestre_valide,
                    "bareme_points": p.bareme_points,
                    "points_de": p.points_de,
                    "valeur_point_euros": p.valeur_point_euros,
                    "valeur_point_annee": p.valeur_point_annee,
                    "borne_basse_euros": p.borne_basse_euros,
                    "borne_haute_euros": p.borne_haute_euros,
                    "pension_forfaitaire_annuelle": p.pension_forfaitaire_annuelle,
                    "pension_forfaitaire_annee": p.pension_forfaitaire_annee,
                    "assiette_repere_smic": p.assiette_repere_smic,
                    "assiette_plancher": p.assiette_plancher,
                    "assiette_forfaitaire": p.assiette_forfaitaire,
                    "cotisation_par_classes": p.cotisation_par_classes,
                    "assiette_grille": p.assiette_grille,
                    "assiette_facteur_revenu": p.assiette_facteur_revenu,
                    "cotisation_forfaitaire_euros": p.cotisation_forfaitaire_euros,
                    "cotisation_forfaitaire_annee": p.cotisation_forfaitaire_annee,
                    "avantages_non_contributifs": list(p.avantages_non_contributifs),
                    "notes": p.notes,
                }
                for p in regime.periodes
            ],
        })
    return fiches


def _affiliations() -> dict:
    affiliations = Affiliations(DONNEES)
    return {
        code: {
            "libelle": affiliations.libelle(code),
            "famille": affiliations.famille(code),
            "sans_employeur": affiliations.sans_employeur(code),
            "categorie_active": affiliations.categorie_active(code),
            "pension_militaire": affiliations.pension_militaire(code),
            "releve_par": affiliations.releve_par(code),
            "periodes": list(affiliations.periodes(code)),
        }
        for code in affiliations.codes
    }


def _valeurs_point() -> dict:
    valeurs = ValeursPoint(DONNEES)
    return {
        f"{regime}|{mesure}": {
            str(annee): [valeur, int(fiabilite)]
            for annee, (valeur, fiabilite) in sorted(table.items())
        }
        for (regime, mesure), table in sorted(valeurs._table.items())
    }


def _classes_cotisation() -> dict:
    """Grilles de cotisation par classes, régime par régime et par millésime.

    Une ligne : borne haute du palier (``null`` pour le dernier, qui n'en a
    pas), montant, fiabilité. Les paliers sont déjà triés à la lecture.
    """
    from retraite_notionnelle.donnees.regimes import ClassesCotisation

    classes = ClassesCotisation(DONNEES)
    return {
        f"{regime}|{annee}": [
            [c.revenu_maximum, c.cotisation, int(c.fiabilite)] for c in grille
        ]
        for regime, grilles in sorted(classes._table.items())
        for annee, grille in sorted(grilles.items())
    }


def _salaires_forfaitaires() -> dict:
    """Grilles de salaires forfaitaires par catégorie : ``regime|annee`` ->
    liste de [catégorie, montant annuel, fiabilité]."""
    from retraite_notionnelle.donnees.regimes import SalairesForfaitaires

    grilles = SalairesForfaitaires(DONNEES)
    return {
        f"{regime}|{annee}": [[c.categorie, c.montant, int(c.fiabilite)] for c in grille]
        for regime, annees in sorted(grilles._table.items())
        for annee, grille in sorted(annees.items())
    }


def _conversions_points() -> list:
    """Coefficients de conversion des points, aux fusions et aux changements
    d'unité. Une ligne : régime, année d'effet, successeur, coefficient,
    fiabilité — le successeur étant vide pour un changement d'échelle interne.
    """
    from retraite_notionnelle.scenarios.actuel import ConversionsPoints

    conversions = ConversionsPoints(DONNEES)
    lignes = [
        [regime, c.annee_effet, successeur, c.coefficient, int(c.fiabilite)]
        for (regime, successeur), c in sorted(conversions._fusions.items())
    ]
    lignes += [
        [regime, c.annee_effet, "", c.coefficient, int(c.fiabilite)]
        for regime, conversions_regime in sorted(conversions._echelles.items())
        for c in conversions_regime
    ]
    return sorted(lignes)


def _rendements() -> list:
    rendements = Rendements(DONNEES)
    return [
        [regime, debut, fin, valeur, int(fiabilite)]
        for regime, debut, fin, valeur, fiabilite in rendements._table
    ]





def _revalorisation_salaires() -> list:
    """Colonnes de revalorisation publiées par la Cnav, par date d'effet.

    Une colonne : année de la date d'effet, drapeau « au 1er janvier », première
    année de perception, puis les coefficients d'affilée — ils courent sans trou,
    si bien qu'un tableau suffit et que le paquet n'a pas à répéter 876 fois une
    clé.
    """
    from retraite_notionnelle.donnees.macro import DonneesMacro

    return [
        [annee, mois, min(table),
         [table[a] for a in range(min(table), max(table) + 1)]]
        for annee, mois, table
        in DonneesMacro(DONNEES).revalorisation_portee_au_compte
    ]


def _contribution_employeur_public() -> dict:
    """Part employeur des régimes publics, indexée « régime|année »."""
    from retraite_notionnelle.donnees.regimes import ContributionsEmployeurPubliques

    table = ContributionsEmployeurPubliques(DONNEES)._table
    return {
        f"{regime}|{annee}": [
            contribution.taux, contribution.nature, int(contribution.fiabilite)
        ]
        for regime, annees in sorted(table.items())
        for annee, contribution in sorted(annees.items())
    }


def _periodes_non_travaillees() -> dict:
    """Ce qu'ouvre chaque motif d'interruption."""
    from retraite_notionnelle.donnees.chargement import charger_periodes_non_travaillees

    return {
        motif: [regle.trimestres_assimiles,
                regle.ouvre_droits_complementaires, int(regle.fiabilite),
                regle.avpf]
        for motif, regle in sorted(charger_periodes_non_travaillees(DONNEES).items())
    }


def _table_par_generation(classe) -> dict:
    """Paramètre législatif indexé sur l'année de naissance."""
    # La clé s'écrit comme JavaScript l'écrirait : « 1951 » et non « 1951.0 »,
    # « 1951.5 » pour une génération que le texte coupe au 1er juillet. Le
    # portage relit ces clés par ``String(Number(cle))``, et une décimale de
    # trop les ferait manquer.
    return {(str(int(generation)) if float(generation).is_integer()
             else str(generation)): [valeur, int(fiabilite)]
            for generation, (valeur, fiabilite) in sorted(classe(DONNEES)._table.items())}


def _categorie_active() -> dict:
    """Âges de la catégorie active et de la super-active, par génération."""
    from retraite_notionnelle.scenarios.actuel import AgesCategorieActive

    table = AgesCategorieActive(DONNEES)._table
    return {
        classement: {
            (str(int(generation)) if float(generation).is_integer()
             else str(generation)): [
                derogation.age_ouverture, derogation.age_annulation,
                derogation.services_requis, int(derogation.fiabilite),
            ]
            for generation, derogation in sorted(valeurs.items())
        }
        for classement, valeurs in sorted(table.items())
    }


def _durees_services_militaires() -> dict:
    """Durée qui ouvre la pension militaire, par année d'atteinte."""
    from retraite_notionnelle.scenarios.actuel import DureesServicesMilitaires

    table = DureesServicesMilitaires(DONNEES)._table
    return {
        categorie: {
            (str(int(annee)) if float(annee).is_integer() else str(annee)):
                [annees, int(fiabilite)]
            for annee, (annees, fiabilite) in sorted(valeurs.items())
        }
        for categorie, valeurs in sorted(table.items())
    }


def _minimum_contributif() -> dict:
    """Ancres datées du minimum contributif, de sa majoration et du plafond."""
    from retraite_notionnelle.donnees.macro import DonneesMacro
    from retraite_notionnelle.scenarios.actuel import MinimumContributif

    table = MinimumContributif(DONNEES, DonneesMacro(DONNEES))._table
    return {f"{mesure}|{annee}": [valeur, int(fiabilite)]
            for (mesure, annee), (valeur, fiabilite) in sorted(table.items())}


def _durees_requises_fonction_publique() -> dict:
    """Durée de services de la fonction publique, 2004-2008, par année d'ouverture."""
    from retraite_notionnelle.scenarios.actuel import DureesRequisesFonctionPublique

    return {
        str(annee): [trimestres, int(fiabilite)]
        for annee, (trimestres, fiabilite)
        in sorted(DureesRequisesFonctionPublique(DONNEES)._table.items())
    }


def _decote_fonction_publique() -> dict:
    """Barème de décote de l'article L. 14, par année d'ouverture du droit."""
    from retraite_notionnelle.scenarios.actuel import DecoteFonctionPublique

    return {
        str(annee): [trimestres, coefficient, int(fiabilite)]
        for annee, (trimestres, coefficient, fiabilite)
        in sorted(DecoteFonctionPublique(DONNEES)._table.items())
    }


def _decote_regimes_speciaux() -> dict:
    """Barème de décote des régimes spéciaux, par année d'ouverture du droit."""
    from retraite_notionnelle.scenarios.actuel import DecoteRegimesSpeciaux

    return {
        str(annee): [trimestres, coefficient, int(fiabilite)]
        for annee, (trimestres, coefficient, fiabilite)
        in sorted(DecoteRegimesSpeciaux(DONNEES)._table.items())
    }


def _minimum_garanti() -> dict:
    """Barème de l'article L. 17, point d'indice et montants servis."""
    from retraite_notionnelle.donnees.macro import DonneesMacro
    from retraite_notionnelle.scenarios.actuel import MinimumGaranti

    minimum = MinimumGaranti(DONNEES, DonneesMacro(DONNEES))
    return {
        "bareme": {
            str(annee): [indice, part, bas, haut, seuil, int(fiabilite)]
            for annee, (indice, part, bas, haut, seuil, fiabilite)
            in sorted(minimum._bareme.items())
        },
        "point_indice": {str(annee): [valeur, int(fiabilite)]
                         for annee, (valeur, fiabilite)
                         in sorted(minimum._point.items())},
        "montants": {str(annee): [valeur, int(fiabilite)]
                     for annee, (valeur, fiabilite)
                     in sorted(minimum._montants.items())},
    }


def _minimum_vieillesse() -> dict:
    """Barème de l'ASPA, personne seule, par année."""
    from retraite_notionnelle.donnees.macro import DonneesMacro
    from retraite_notionnelle.scenarios.actuel import MinimumVieillesse

    table = MinimumVieillesse(DONNEES, DonneesMacro(DONNEES))._table
    return {str(annee): [valeur, int(fiabilite)]
            for annee, (valeur, fiabilite) in sorted(table.items())}


def _majorations_enfants() -> list:
    """Trimestres accordés au titre des enfants, dispositif par dispositif."""
    return [
        [dispositif, reference, debut, fin, trimestres, enfants_minimum,
         beneficiaire, int(fiabilite)]
        for dispositif, reference, debut, fin, trimestres, enfants_minimum,
        beneficiaire, fiabilite in MajorationsPourEnfants(DONNEES)._table
    ]


def _surcote_parentale() -> list:
    """Surcote parentale : âge d'ouverture, taux, plafond, par période."""
    return [
        [debut, fin, age, taux, maximum, int(fiabilite)]
        for debut, fin, age, taux, maximum, fiabilite
        in SurcoteParentale(DONNEES)._table
    ]


def _carriere_longue() -> dict:
    """Portes du départ anticipé pour carrière longue, par date d'effet.

    La clé est l'année décimale du premier mois d'application ; chaque porte
    porte la génération à partir de laquelle elle vaut, ``1900`` pour la
    règle générale.
    """
    from retraite_notionnelle.scenarios.actuel import CarriereLongue

    return {
        _sans_zeros(date_effet): [
            [generation, age_max, trimestres, age_depart, supplement, int(fiabilite)]
            for generation, age_max, trimestres, age_depart, supplement, fiabilite
            in portes
        ]
        for date_effet, portes in sorted(CarriereLongue(DONNEES)._table.items())
    }


def _sans_zeros(valeur: float) -> str:
    texte = f"{valeur:.3f}".rstrip("0").rstrip(".")
    return texte


def _surcote_baremes() -> list:
    """Barème daté de la surcote : une ligne par taux, par barème."""
    from retraite_notionnelle.scenarios.actuel import SurcoteBaremes

    return [
        [bareme, debut, fin, rang, int(apres_65), taux, maximum, int(fiabilite)]
        for bareme, debut, fin, rang, apres_65, taux, maximum, fiabilite
        in SurcoteBaremes(DONNEES)._lignes
    ]


def _hypotheses() -> dict:
    contenu = charger_yaml(DONNEES / "reference" / "macro" / "hypotheses_projection.yaml")
    return {
        "annee_fin_projection": int(contenu.get("annee_fin_projection", 2100)),
        "scenario_par_defaut": contenu.get("scenario_par_defaut"),
        "plafond_suit_salaire_moyen": bool(contenu.get("plafond_suit_salaire_moyen", True)),
        "scenarios": contenu.get("scenarios", {}),
    }


def _courbe_taux_sans_risque() -> dict:
    """La dernière courbe publiée, telle que le pilier capitalisé la lit.

    Une seule date — la plus récente : le paquet sert le calcul, pas l'archive.
    Les courbes antérieures restent dans le fichier de référence, pour qui veut
    refaire un chiffre tel qu'il a été publié.
    """
    courbe = CourbeTauxSansRisque(DONNEES)
    return {
        "date": courbe.date,
        "maturites": list(courbe.maturites),
        "taux_continus": [courbe.zero_continu(m) for m in courbe.maturites],
        "fiabilite": int(courbe.fiabilite_publiee),
    }


def _frais_epargne_retraite() -> dict:
    """Le barème de frais du PER, avec de quoi le citer sur la page Données."""
    frais = FraisEpargneRetraite(DONNEES)
    return {
        "annee_reference": frais.annee_reference,
        "publication": frais.publication,
        "fiabilite": int(frais.fiabilite),
        "postes": {
            cle: {
                "valeur": poste.valeur,
                "assiette": poste.assiette,
                "libelle": poste.libelle,
                "note": poste.note,
            }
            for cle, poste in sorted(frais.postes.items())
        },
    }


def _prelevements_remuneration() -> dict:
    """Les prélèvements hors retraite — ce qui sépare un brut d'un net.

    Passe par le chargeur du modèle, comme tout le reste : les segments y sont
    déjà développés depuis la forme cumulative du fichier, si bien que le
    portage n'a pas à refaire cette conversion — donc pas à la refaire
    autrement.
    """
    bareme = charger_prelevements(DONNEES)

    def segments(suite) -> list:
        return [{"bas": s.bas_en_plafonds, "haut": s.haut_en_plafonds,
                 "taux": s.taux} for s in suite]

    reduction = bareme.reduction_generale
    return {
        "annee": bareme.annee,
        "fiabilite": int(bareme.fiabilite),
        "csg_deductible": bareme.csg_deductible,
        "csg_imposable": bareme.csg_imposable,
        "crds": bareme.crds,
        "abattement_frais": segments(bareme.abattement_frais),
        "postes": [
            {
                "code": poste.code,
                "libelle": poste.libelle,
                "retraite": poste.retraite,
                "dans_la_reduction_generale": poste.dans_la_reduction_generale,
                "taux_dans_la_reduction": poste.taux_dans_la_reduction,
                "cadres_seulement": poste.cadres_seulement,
                "due_au_dela_de_un_plafond": poste.due_au_dela_de_un_plafond,
                "salarie": segments(poste.salarie),
                "employeur": segments(poste.employeur),
            }
            for poste in bareme.postes
        ],
        "reduction_generale": {
            "libelle": reduction.libelle,
            "plafond_en_smic": reduction.plafond_en_smic,
            "puissance": reduction.puissance,
            "taux_minimum": reduction.taux_minimum,
            "coefficient_maximal": reduction.coefficient_maximal,
            "composantes": dict(sorted(reduction.composantes.items())),
            "composantes_retraite": list(reduction.composantes_retraite),
        },
    }


def _inventaire() -> list:
    """Tous les régimes, calculés ou non, tels que la page « Données » les liste."""
    return [ligne.dictionnaire() for ligne in charger_inventaire(DONNEES)]


def _avantages() -> dict:
    """Les trente-neuf avantages non contributifs, et les familles qui les rangent.

    C'est une DONNÉE et non un résultat : la frise de la page « Avantages » ne
    suppose aucun calcul, et c'est ce qui la rend sûre là où les masses de la
    même page sont des planchers. Le portage la relit telle quelle.
    """
    inventaire = charger_avantages(DONNEES)
    return {
        "familles": [
            {"code": famille.code, "libelle": famille.libelle, "quoi": famille.quoi}
            for famille in inventaire.familles
        ],
        "avantages": [avantage.dictionnaire() for avantage in inventaire.avantages],
    }


def construire() -> bytes:
    """Paquet complet, à contenu identique pour des données identiques."""
    paquet = {
        "version": VERSION,
        "series": _series(),
        "hypotheses": _hypotheses(),
        "courbe_taux_sans_risque": _courbe_taux_sans_risque(),
        "frais_epargne_retraite": _frais_epargne_retraite(),
        "prelevements_remuneration": _prelevements_remuneration(),
        "quotients": _quotients(),
        "calibrations": _calibrations(),
        "regimes": _regimes(),
        "inventaire": _inventaire(),
        "avantages": _avantages(),
        "affiliations": _affiliations(),
        "valeurs_point": _valeurs_point(),
        "rendements_points": _rendements(),
        "conversions_points": _conversions_points(),
        "classes_cotisation": _classes_cotisation(),
        "salaires_forfaitaires": _salaires_forfaitaires(),
        "durees_requises": _table_par_generation(DureesRequises),
        "durees_proratisation": _table_par_generation(DureesProratisation),
        "revalorisation_salaires": _revalorisation_salaires(),
        "ages_ouverture": _table_par_generation(AgesOuverture),
        "ages_annulation_decote": _table_par_generation(AgesAnnulationDecote),
        "categorie_active": _categorie_active(),
        "durees_services_militaires": _durees_services_militaires(),
        "ages_jouissance_militaire": _table_par_generation(AgesJouissanceMilitaire),
        "coefficients_minoration": _table_par_generation(CoefficientsMinoration),
        "annees_salaire_reference": _table_par_generation(AnneesSalaireReference),
        "periodes_non_travaillees": _periodes_non_travaillees(),
        "contribution_employeur_public": _contribution_employeur_public(),
        "minimum_contributif": _minimum_contributif(),
        "minimum_garanti": _minimum_garanti(),
        "minimum_vieillesse": _minimum_vieillesse(),
        "durees_requises_fonction_publique": _durees_requises_fonction_publique(),
        "decote_fonction_publique": _decote_fonction_publique(),
        "decote_regimes_speciaux": _decote_regimes_speciaux(),
        "carriere_longue": _carriere_longue(),
        "majorations_enfants": _majorations_enfants(),
        "surcote_parentale": _surcote_parentale(),
        "surcote_baremes": _surcote_baremes(),
        "depenses": _depenses(),
        "comptes_retraite": _comptes_retraite(),
        "population": _population(),
        "effectifs_retraites": _effectifs_retraites(),
        "distribution_pensions": _distribution_pensions(),
        "certification": journal_certification(DONNEES),
    }
    texte = json.dumps(paquet, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"))
    return (texte + "\n").encode("utf-8")


def construire_style() -> bytes:
    """Feuille de style extraite du module Python, seule source du style."""
    from retraite_notionnelle.web import gabarit

    entete = (
        "/* Extrait de src/retraite_notionnelle/web/gabarit.py par\n"
        "   scripts/construire_donnees.py — ne pas modifier ici. */\n"
    )
    return (entete + gabarit.FEUILLE_DE_STYLE.lstrip("\n")).encode("utf-8")


def sorties() -> dict[Path, bytes]:
    return {PAQUET: construire(), STYLE: construire_style()}


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument(
        "--verifier", action="store_true",
        help="ne rien écrire ; échouer si les fichiers versionnés sont périmés",
    )
    arguments = analyseur.parse_args(argv)

    attendus = sorties()

    if arguments.verifier:
        for chemin, contenu in attendus.items():
            if not chemin.exists():
                print(f"{chemin.relative_to(RACINE)} est absent — lancer "
                      "python scripts/construire_donnees.py", file=sys.stderr)
                return 1
            if chemin.read_bytes() != contenu:
                print(f"{chemin.relative_to(RACINE)} est périmé — lancer "
                      "python scripts/construire_donnees.py", file=sys.stderr)
                return 1
        print("paquet et feuille de style à jour")
        return 0

    for chemin, contenu in attendus.items():
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_bytes(contenu)
        print(f"{chemin.relative_to(RACINE)} : {len(contenu) / 1024:.0f} Ko")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
