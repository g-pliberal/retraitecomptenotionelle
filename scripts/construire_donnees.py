#!/usr/bin/env python3
"""Fabrique ce que le site charge : ``moteur/donnees.json`` et ``moteur/style.css``.

Et deux tables que le modèle Python relit comme des données :
``data/derive/equilibre.json``, le bilan figé, et
``data/derive/calibrations_mortalite.json``, les lois de mortalité calibrées.

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
from retraite_notionnelle.donnees.caracteristiques import CaracteristiquesRetraites  # noqa: E402
from retraite_notionnelle.donnees.assiette import POSTES_ASSIETTE  # noqa: E402
from retraite_notionnelle.donnees.chargement import (  # noqa: E402
    SerieAnnuelle,
    charger_serie_annuelle,
    charger_yaml,
    compter_institutions,
    journal_certification,
)
from retraite_notionnelle.donnees.depenses import CATEGORIES_DROITS, SYSTEMES  # noqa: E402
from retraite_notionnelle.donnees.equilibre import (  # noqa: E402
    POSTES,
    POSTES_TRANSFERTS,
    variantes_disponibles,
)
from retraite_notionnelle.donnees.distribution import (  # noqa: E402
    DistributionPensions,
)
from retraite_notionnelle.donnees.patrimoine import PatrimoineMenages  # noqa: E402
from retraite_notionnelle.donnees.vie_en_couple import VieEnCouple  # noqa: E402
from retraite_notionnelle.avantages import charger_avantages  # noqa: E402
from retraite_notionnelle.donnees.cotisants import EffectifsCotisants  # noqa: E402
from retraite_notionnelle.donnees.effectifs import EffectifsRetraites  # noqa: E402
from retraite_notionnelle.donnees.frais import FraisEpargneRetraite  # noqa: E402
from retraite_notionnelle.donnees.mortalite import (  # noqa: E402
    DonneesMortalite,
    serialiser_calibrations,
)
from retraite_notionnelle.remuneration import charger_prelevements  # noqa: E402
from retraite_notionnelle.restitution import POSTES_REMUNERATION  # noqa: E402
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
    AgesSurcoteRegimesSpeciaux,
    AnneesSalaireReference,
    CoefficientsMinoration,
    DureesProratisation,
    DureesRequises,
    DureesRequisesAvantSuspension,
    MajorationsPourEnfants,
    Rendements,
    SurcoteParentale,
    ValeursPoint,
)

DONNEES = RACINE / "data"
PAQUET = RACINE / "moteur" / "donnees.json"
STYLE = RACINE / "moteur" / "style.css"
#: Le bilan des quatre systèmes, figé sous les réglages de référence. Versionné
#: dans ``data/`` parce que le modèle Python le relit comme une donnée — voir
#: ``donnees/bilan.py`` —, et embarqué tel quel dans le paquet du navigateur.
EQUILIBRE = DONNEES / "derive" / "equilibre.json"
#: Les lois de mortalité calibrées, avec l'empreinte de leurs entrées. Écrites
#: ici et nulle part ailleurs : le test de fraîcheur du paquet les vérifie, et
#: une loi calée sur des cibles qui ont changé ne peut plus survivre en silence.
CALIBRATIONS = DONNEES / "derive" / "calibrations_mortalite.json"

#: Version du format. À incrémenter si la structure du paquet change, pour
#: qu'un site en cache ne lise pas un paquet qu'il ne comprend pas.
VERSION = 16


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
        # La croissance de l'emploi projetée par le COR, 2026-2070 : elle
        # compose la masse salariale et le PIB au-delà de la dernière
        # observation, sous la trajectoire `cor_2026`.
        "emploi_projete": charger_serie_annuelle(
            macro / "emploi_projete.csv", "croissance_emploi", nom="croissance_emploi"),
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
        # La réversion, lue et non modélisée : le modèle décrit une carrière,
        # pas un ménage. Elle voyage avec les dépenses parce qu'elle en est une.
        # Le MODE suit celui de `donnees/depenses.py`, et il le faut : le
        # paquet porte l'interpolation de chaque série, et le navigateur
        # l'applique telle quelle. Deux déclarations du même fichier qui ne
        # s'accorderaient pas feraient dire deux choses aux deux portages sur
        # une année absente — et aucun témoin ne le verrait, le site n'en
        # affichant aucune.
        "droits_derives": charger_serie_annuelle(
            macro / "droits_derives.csv", "masse_meur", nom="droits_derives",
            filtre={"caisse": "tous_regimes"}, interpolation="ponctuelle"),
    }
    # Les postes non contributifs des comptes, sous leur propre clé : ils sont
    # LUS dans le fichier et non écrits ici, pour qu'un poste ajouté aux comptes
    # récupérés voyage sans qu'aucune liste ne le répète.
    from retraite_notionnelle.donnees.depenses import _postes_non_contributifs
    chemin = macro / "prestations_non_contributives.csv"
    prestations = {
        poste: charger_serie_annuelle(
            chemin, "montant_meur", nom=f"prestation_{poste}",
            filtre={"poste": poste})
        for poste in (_postes_non_contributifs(chemin) if chemin.exists() else ())
    }
    for systeme in SYSTEMES:
        series[systeme.code] = charger_serie_annuelle(
            macro / "depenses_retraite_regimes.csv", "depenses_meur",
            nom=f"depenses_{systeme.code}", filtre={"regime": systeme.code})
    # La part de RÉVERSION dans la masse versée, et la ventilation de la DREES
    # qui la contrôle. La première sert au calcul — elle dit quel morceau de la
    # base un rapport de droits directs a le droit de multiplier ; la seconde
    # ne sert qu'à la page, qui montre d'où vient la première.
    series["part_droits_derives"] = charger_serie_annuelle(
        macro / "part_droits_derives.csv", "part", nom="part_droits_derives")
    for categorie in CATEGORIES_DROITS:
        series[f"pensions_{categorie}"] = charger_serie_annuelle(
            macro / "pensions_droits.csv", "montant_meur",
            nom=f"pensions_{categorie}", filtre={"categorie": categorie})
    paquet = {nom: _serie(serie) for nom, serie in sorted(series.items())}
    paquet["prestations"] = {
        poste: _serie(serie) for poste, serie in sorted(prestations.items())
    }
    return paquet


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
    # Le MÊME compte sous chaque variante du COR — productivité, chômage —,
    # sur ses seules années projetées. Sans lui, le site lit le scénario de
    # référence quel que soit le scénario demandé : la croissance déplace alors
    # la dépense des systèmes notionnels, qui est calculée, sans déplacer celle
    # du droit en vigueur, qui est empruntée.
    for variante in variantes_disponibles(macro):
        for poste in ("depenses", "ressources"):
            series[f"variante_{variante}_{poste}"] = charger_serie_annuelle(
                macro / "comptes_retraite_variantes.csv", "part_pib",
                nom=f"comptes_variante_{variante}_{poste}",
                filtre={"poste": poste, "variante": variante})
    for poste in POSTES:
        series[poste.code] = charger_serie_annuelle(
            macro / "structure_ressources_retraite.csv", "part",
            nom=f"structure_{poste.code}", filtre={"poste": poste.code})
    # Le taux de prélèvement projeté par le COR, en part des revenus
    # d'activité : ce qui dit que ses ressources reculent en part de PIB parce
    # que le TAUX baisse, et non parce que l'assiette rétrécit. Sans lui, la
    # recette de la proposition perd un demi-point de PIB en 2070.
    series["taux_prelevement"] = charger_serie_annuelle(
        macro / "taux_prelevement_retraite.csv", "taux",
        nom="taux_prelevement_retraite")
    # Les mêmes ressources sous l'autre convention comptable du COR : ce qui
    # permet à la page de dire que sa convention est une hypothèse, et ce
    # qu'elle vaut.
    series["ressources_eec"] = charger_serie_annuelle(
        macro / "ressources_eec_retraite.csv", "part_pib",
        nom="ressources_eec_retraite")
    # Les droits à pension acquis à date : le stock, à côté des flux.
    for regime in ("tous_regimes", "repartition"):
        series[f"engagements_{regime}"] = charger_serie_annuelle(
            macro / "engagements_retraite.csv", "part_pib",
            nom=f"engagements_{regime}", filtre={"regime": regime},
            # Transmis tous les trois ans : deux années sur trois n'ont pas été
            # mesurées. Même mode que `donnees/equilibre.py`.
            interpolation="ponctuelle")
    # Ce que la branche famille et l'assurance chômage versent, en millions
    # d'euros : la ventilation du poste « transferts », lue chez celui qui paie.
    for poste in POSTES_TRANSFERTS:
        series[f"transferts_{poste.code}"] = charger_serie_annuelle(
            macro / "transferts_retraite.csv", "montant_meur",
            nom=f"transferts_{poste.code}", filtre={"poste": poste.code})
    # Les deux impôts du poste « impôts et taxes affectés » qui sont assis sur
    # une rémunération — taxe sur les salaires et forfait social —, en millions
    # d'euros : ce que la proposition SUPPRIME plutôt que de le rendre par la
    # CSG. Voir `restitution.py`.
    for code, _ in POSTES_REMUNERATION:
        series[f"impots_remuneration_{code}"] = charger_serie_annuelle(
            macro / "impots_retraite_remuneration.csv", "montant_meur",
            nom=f"impots_remuneration_{code}", filtre={"poste": code})
    # L'assiette des revenus d'activité, en millions d'euros : ce sur quoi la
    # proposition prélève ses 18 %. Sans elle, un taux affiché ne se convertit
    # pas en recette.
    for code, _ in POSTES_ASSIETTE:
        series[f"assiette_{code}"] = charger_serie_annuelle(
            macro / "assiette_activite.csv", "montant_meur",
            nom=f"assiette_{code}", filtre={"poste": code})
    # La dette de toutes les administrations publiques, en part de PIB : ce
    # que le pays porte déjà, sous quoi la page Coût pose le stock de chaque
    # système. Elle ne sert à aucun calcul.
    series["dette_publique"] = charger_serie_annuelle(
        macro / "dette_publique.csv", "part_pib", nom="dette_publique")
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


def _effectifs_cotisants() -> dict:
    """Cotisants par caisse — la pondération des cas types côté recette.

    Les deux versants de la fonction publique d'État sont déjà partagés par le
    chargeur Python, à la clé qu'il documente : le portage n'a pas à connaître
    cette décision, il reçoit les caisses telles que la grille les nomme.
    """
    cotisants = EffectifsCotisants(DONNEES)
    return {
        caisse: _serie(cotisants.serie(caisse)) for caisse in cotisants.caisses()
    }


def _distribution_pensions() -> dict:
    """Distribution des pensions : ce qui chiffre un plancher différentiel.

    Les tranches sont écrites en trois tableaux parallèles, comme les séries :
    la borne inférieure, la borne supérieure — ``null`` pour la tranche ouverte
    du haut — et la part des retraités.
    """
    # Celle des résidents en France, que la garantie sert : la soustraction est
    # faite ici, une fois, et le site lit son résultat avec la part des
    # résidents qui met l'effectif à l'échelle.
    distribution = DistributionPensions(DONNEES, residence="france")
    return {
        "millesime": distribution.millesime,
        "sexe": distribution.sexe,
        "fiabilite": int(distribution.fiabilite),
        "bornes_inferieures": [t.borne_inferieure for t in distribution.tranches],
        "bornes_superieures": [t.borne_superieure for t in distribution.tranches],
        "parts": [t.part for t in distribution.tranches],
        "part_residents": distribution.part_residents,
        "part_femmes_residents": distribution.part_femmes_residents,
    }


def _vie_en_couple() -> dict:
    """Qui vit en couple après 65 ans : ce qui regroupe deux avances sur une
    succession. Les parts sont écrites sous une clé « âge|sexe|mode »."""
    couple = VieEnCouple(DONNEES)
    return {
        "annee": couple.annee,
        "fiabilite": int(couple.fiabilite),
        "age_minimal": couple.age_minimal,
        "age_maximal": couple.age_maximal,
        "parts": {
            f"{age}|{sexe}|{mode}": couple.part(age, sexe, mode)
            for age in range(couple.age_minimal, couple.age_maximal + 1)
            for sexe in ("F", "H")
            for mode in ("couple", "seul")
        },
    }


def _caracteristiques_retraites() -> dict:
    """Ce que les carrières doivent aux droits non cotisés, par sexe.

    Six indicateurs seulement, mais ce sont eux qui disent de combien le
    scénario 6 déplace les pensions des femmes PLUS que celles des hommes.
    """
    c = CaracteristiquesRetraites(DONNEES)
    return {
        "millesime": c.millesime,
        "fiabilite": int(c.fiabilite),
        "valeurs": {
            f"{indicateur}|{sexe}": c.valeur(indicateur, sexe)
            for indicateur in ("effectifs", "pension_droit_direct",
                               "pension_droit_direct_majorations",
                               "duree_validee_non_cotisee", "duree_validee",
                               "coefficient_proratisation", "part_minimum_pension",
                               "beneficiaires_minimum_pension",
                               "beneficiaires_minimum_regime_principal")
            for sexe in ("F", "H", "ensemble")
        },
    }


def _distribution_pensions_sexes() -> dict:
    """La même distribution, femmes et hommes à part : elle pèse les sexes
    parmi les bénéficiaires de la garantie, dont la mortalité en dépend."""
    return {
        sexe: {
            "millesime": d.millesime,
            "fiabilite": int(d.fiabilite),
            "bornes_inferieures": [t.borne_inferieure for t in d.tranches],
            "bornes_superieures": [t.borne_superieure for t in d.tranches],
            "parts": [t.part for t in d.tranches],
            "part_residents": d.part_residents,
        }
        for sexe in ("F", "H")
        for d in (DistributionPensions(DONNEES, sexe=sexe, residence="france"),)
    }


def _patrimoine_menages() -> dict:
    """Le patrimoine des ménages : par population, ses statistiques publiées."""
    patrimoine = PatrimoineMenages(DONNEES)
    return {
        "patrimoine": patrimoine.patrimoine,
        "populations": {
            population: {
                "annee": patrimoine.annee(population),
                "fiabilite": int(patrimoine.fiabilite(population)),
                "statistiques": patrimoine.statistiques(population),
            }
            for population in patrimoine.populations
        },
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


_TABLE_CALIBRATIONS: dict[str, list] | None = None


def _table_calibrations() -> dict[str, list]:
    """Les lois de toutes les années de la série, avec leur empreinte.

    Relues de ``data/derive/calibrations_mortalite.json`` quand leurs entrées
    n'ont pas changé, recalibrées sinon. Calculées une fois par exécution : le
    paquet et le fichier de calibration en sont deux lectures.
    """
    global _TABLE_CALIBRATIONS
    if _TABLE_CALIBRATIONS is None:
        _TABLE_CALIBRATIONS = DonneesMortalite(DONNEES).table_calibrations()
    return _TABLE_CALIBRATIONS


def _calibrations() -> dict:
    """Paramètres de Makeham pour TOUTES les années utiles, pas seulement celles
    déjà rencontrées.

    Le modèle borne l'année aux extrémités de la série d'espérances de vie : le
    domaine est donc fini et connu. En le calibrant intégralement ici, le
    navigateur n'a plus qu'à lire une table — il ne refait aucune bissection, et
    les deux implémentations partent des mêmes paramètres au bit près.

    Rien n'est écrit ici : le fichier de calibration est une sortie comme les
    autres (:func:`sorties`), et ``--verifier`` ne doit rien écrire.
    """
    return {cle: list(valeur[:2])
            for cle, valeur in sorted(_table_calibrations().items())}


def _populations() -> dict:
    """Les facteurs de mortalité des populations particulières, calibrés une
    fois pour toutes : le navigateur les lit, il ne recalibre rien."""
    donnees = DonneesMortalite(DONNEES, cache_disque=False)
    return {
        "facteurs": donnees.facteurs_populations(),
        "esperances": {
            f"{population}|{sexe}": list(donnees._reference_population(population, sexe))
            for population in donnees.populations
            for sexe in DonneesMortalite.SEXES
            if f"{population}|{sexe}" in donnees.facteurs_populations()
        },
        "niveaux_de_vie": {str(v): n for v, n in sorted(donnees._niveaux_de_vie.items())},
        "annee_niveaux_de_vie": donnees.annee_niveaux_de_vie,
    }


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
                    "duree_requise_table": p.duree_requise_table,
                    "age_surcote_regimes_speciaux": p.age_surcote_regimes_speciaux,
                    "duree_proratisation_par_generation":
                        p.duree_proratisation_par_generation,
                    "age_ouverture_par_generation": p.age_ouverture_par_generation,
                    "taux_plein": p.taux_plein,
                    "taux_maximum_bonifie": p.taux_maximum_bonifie,
                    "salaire_reference": p.salaire_reference,
                    "assiette": p.assiette,
                    "taux_cotisation_retraite": p.taux_cotisation_retraite,
                    "taux_cotisation_deplafonnee": p.taux_cotisation_deplafonnee,
                    "part_salariale_deplafonnee": p.part_salariale_deplafonnee,
                    "perimetre_taux": p.perimetre_taux,
                    "part_salariale": p.part_salariale,
                    "age_taux_plein_par_generation": p.age_taux_plein_par_generation,
                    "age_table": p.age_table,
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
                    "points_ajustement_par_forfait": p.points_ajustement_par_forfait,
                    "points_ajustement_maximum": p.points_ajustement_maximum,
                    "capital_seuil_points": p.capital_seuil_points,
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
                    "assiette_minimale_pass": p.assiette_minimale_pass,
                    "cotisation_par_classes": p.cotisation_par_classes,
                    "assiette_grille": p.assiette_grille,
                    "assiette_facteur_revenu": p.assiette_facteur_revenu,
                    "cotisation_forfaitaire_euros": p.cotisation_forfaitaire_euros,
                    "cotisation_forfaitaire_annee": p.cotisation_forfaitaire_annee,
                    "avantages_non_contributifs": list(p.avantages_non_contributifs),
                    "notes": p.notes,
                    **_regles_des_marins(p),
                    **_regles_des_sections(p),
                    **_plafond_des_primes(p),
                }
                for p in regime.periodes
            ],
        })
    return fiches


def _regles_des_marins(p) -> dict:
    """Les champs que seule la fiche des marins porte, et seulement là.

    Écrits sur chaque période de chaque régime, ils pèseraient 140 Ko de
    ``null`` dans le paquet ; le moteur JavaScript lit leur absence comme leur
    nullité.
    """
    champs = {
        "duree_maximum_levee_age": p.duree_maximum_levee_age,
        "duree_maximum_levee_trimestres": p.duree_maximum_levee_trimestres,
        "age_ouverture_services": p.age_ouverture_services,
        "services_ouverture_annees": p.services_ouverture_annees,
        "pension_speciale_services_annees": p.pension_speciale_services_annees,
        "pension_speciale_age_sans_autre_pension":
            p.pension_speciale_age_sans_autre_pension,
        "taux_majoration_enfants": (list(p.taux_majoration_enfants)
                                    if p.taux_majoration_enfants else None),
    }
    return {cle: valeur for cle, valeur in champs.items() if valeur is not None}


def _regles_des_sections(p) -> dict:
    """Les champs que seules quelques sections libérales portent, et seulement là.

    La décote à deux pentes de la CAVP, le taux plein anticipé des mères de la
    CARCDSF, la surcote par années cotisées de la CAVAMAC : même raison que
    pour les marins, le moteur JavaScript lit leur absence comme leur nullité.
    """
    champs = {
        "decote_palier_age": p.decote_palier_age,
        "decote_par_trimestre_apres_palier": p.decote_par_trimestre_apres_palier,
        "taux_plein_anticipe_par_enfant_annees":
            p.taux_plein_anticipe_par_enfant_annees,
        "taux_plein_anticipe_maximum_annees": p.taux_plein_anticipe_maximum_annees,
        # La surcote de la CAVAMAC depuis 2024, par années COTISÉES.
        "surcote_trimestres_cotises": p.surcote_trimestres_cotises or None,
    }
    return {cle: valeur for cle, valeur in champs.items() if valeur is not None}


def _plafond_des_primes(p) -> dict:
    """Le plafond des primes du RAFP, 20 % du traitement, et seulement là.

    Même raison que pour les marins : le moteur JavaScript lit son absence
    comme sa nullité.
    """
    if p.plafond_primes_traitement is None:
        return {}
    return {"plafond_primes_traitement": p.plafond_primes_traitement}


def _affiliations() -> dict:
    affiliations = Affiliations(DONNEES)
    return {
        code: {
            "libelle": affiliations.libelle(code),
            "famille": affiliations.famille(code),
            "sans_employeur": affiliations.sans_employeur(code),
            "part_salariale_seule": affiliations.part_salariale_seule(code),
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


def _revalorisation_pensions() -> dict:
    """Les revalorisations des pensions servies, date d'effet par date d'effet.

    Une ligne : date ISO, coefficient, bornes mensuelles des tranches de 2020
    (``null`` ailleurs), fiabilité. Les références des textes restent dans les
    fichiers : la page ne les cite pas.
    """
    from retraite_notionnelle.revalorisation import RevalorisationsPensions

    revalorisations = RevalorisationsPensions(DONNEES)

    def lignes(serie):
        return [
            [r.date_effet.isoformat(), r.coefficient, r.superieur_a, r.au_plus,
             int(r.fiabilite)]
            for r in serie
        ]

    return {
        "generales": lignes(revalorisations.generales),
        "fonction_publique": lignes(revalorisations.fonction_publique),
    }


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


def _assiette_minimale_independants() -> list:
    """Assiette minimale du régime de base des indépendants, règle par règle."""
    from retraite_notionnelle.donnees.chargement import charger_assiettes_minimales

    return [
        [sorted(r.statuts), sorted(r.regimes), r.debut, r.fin,
         r.heures_smic, r.part_pass, r.proratise, r.jours_minimum]
        for r in charger_assiettes_minimales(DONNEES)
    ]


def _periodes_non_travaillees() -> dict:
    """Ce qu'ouvre chaque motif d'interruption."""
    from retraite_notionnelle.donnees.chargement import charger_periodes_non_travaillees

    return {
        motif: [regle.trimestres_assimiles,
                regle.ouvre_droits_complementaires, int(regle.fiabilite),
                regle.avpf, regle.services_fonction_publique,
                regle.services_plafond_trimestres_par_enfant,
                regle.reputes_cotises_enveloppe,
                regle.reputes_cotises_plafond,
                regle.cotisations_complementaires_versees]
        for motif, regle in sorted(charger_periodes_non_travaillees(DONNEES).items())
    }


def _profil_salaire(fichier: str, cle: str) -> dict:
    """Profil salarial, groupé par sa première clé puis par tranche d'âge.

    Deux niveaux plutôt qu'une clé composite : JavaScript n'a pas de tuple, et
    une clé « 1962|Y26T30 » se recolle mal. Le portage lit donc
    ``paquet.profil_salaire_age["1962"]["Y26T30"]``.
    """
    from retraite_notionnelle.donnees.chargement import charger_table_csv

    table, _ = charger_table_csv(
        DONNEES / "reference" / "macro" / fichier, (cle, "tranche"),
        "salaire_relatif",
    )
    groupes: dict[str, dict[str, float]] = {}
    for (groupe, tranche), valeur in sorted(table.items()):
        groupes.setdefault(groupe, {})[tranche] = valeur
    return groupes


def _profil_salaire_secteur() -> dict:
    """Profil par secteur, à trois niveaux : section, vague, tranche d'âge."""
    from retraite_notionnelle.donnees.chargement import charger_table_csv

    table, _ = charger_table_csv(
        DONNEES / "reference" / "macro" / "profil_salaire_secteur.csv",
        ("secteur", "vague", "tranche"), "salaire_relatif",
    )
    groupes: dict[str, dict[str, dict[str, float]]] = {}
    for (section, vague, tranche), valeur in sorted(table.items()):
        groupes.setdefault(section, {}).setdefault(vague, {})[tranche] = valeur
    return groupes


def _table_par_generation(classe) -> dict:
    """Paramètre législatif indexé sur l'année de naissance."""
    # La clé s'écrit comme JavaScript l'écrirait : « 1951 » et non « 1951.0 »,
    # « 1951.5 » pour une génération que le texte coupe au 1er juillet. Le
    # portage relit ces clés par ``String(Number(cle))``, et une décimale de
    # trop les ferait manquer.
    return {(str(int(generation)) if float(generation).is_integer()
             else str(generation)): [valeur, int(fiabilite)]
            for generation, (valeur, fiabilite) in sorted(classe(DONNEES)._table.items())}


def _ages_regimes() -> dict:
    """Âges propres à un régime, par génération : ouverture, taux plein,
    fiabilité et, quand la table en écrit un, coefficient de minoration."""
    from retraite_notionnelle.scenarios.actuel import AgesRegimes

    ages = AgesRegimes(DONNEES)
    return {
        table: {
            (str(int(generation)) if float(generation).is_integer()
             else str(generation)): [ouverture, taux_plein, int(fiabilite),
                                     ages._decotes[table].get(generation)]
            for generation, (ouverture, taux_plein, fiabilite)
            in sorted(lignes.items())
        }
        for table, lignes in sorted(ages._table.items())
    }


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
                derogation.duree_requise,
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


def _durees_requises_regimes() -> dict:
    """Durée requise propre à un régime spécial, par table et par génération."""
    from retraite_notionnelle.scenarios.actuel import DureesRequisesRegimes

    return {
        table: {
            (str(int(generation)) if float(generation).is_integer()
             else str(generation)): [trimestres, retranche, int(fiabilite)]
            for generation, (trimestres, retranche, fiabilite)
            in sorted(valeurs.items())
        }
        for table, valeurs in sorted(DureesRequisesRegimes(DONNEES)._table.items())
    }


def _durees_requises_fonction_publique() -> dict:
    """Durée de services de la fonction publique, 2004-2008, par année d'ouverture."""
    from retraite_notionnelle.scenarios.actuel import DureesRequisesFonctionPublique

    return {
        str(annee): [trimestres, int(fiabilite)]
        for annee, (trimestres, fiabilite)
        in sorted(DureesRequisesFonctionPublique(DONNEES)._table.items())
    }


def _durees_requises_avant_soixante_ans() -> dict:
    """Durée des droits ouverts avant soixante ans, par règle et rang de mois."""
    from retraite_notionnelle.scenarios.actuel import DureesRequisesAvantSoixanteAns

    return {
        regle: {str(rang): [trimestres, int(fiabilite)]
                for rang, (trimestres, fiabilite) in sorted(valeurs.items())}
        for regle, valeurs
        in sorted(DureesRequisesAvantSoixanteAns(DONNEES)._table.items())
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
        [dispositif, reference, debut, fin, trimestres, services, services_depuis,
         enfants_minimum, beneficiaire, int(fiabilite)]
        for dispositif, reference, debut, fin, trimestres, services,
        services_depuis, enfants_minimum, beneficiaire, fiabilite
        in MajorationsPourEnfants(DONNEES)._table
    ]


def _surcote_parentale() -> list:
    """Surcote parentale : âge d'ouverture, taux, plafond, par période."""
    return [
        [debut, fin, age, taux, maximum, int(fiabilite)]
        for debut, fin, age, taux, maximum, fiabilite
        in SurcoteParentale(DONNEES)._table
    ]


def _majoration_enfants_points() -> dict:
    """Majoration pour enfants des points, par régime et période d'acquisition."""
    from retraite_notionnelle.scenarios.actuel import MajorationsEnfantsPoints

    return {
        code: [[debut, fin, list(bareme), int(fiabilite)]
               for debut, fin, bareme, fiabilite in lignes]
        for code, lignes in sorted(MajorationsEnfantsPoints(DONNEES)._table.items())
    }


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
        # La première année projetée en dépend : c'est là que l'emploi entre.
        "annee_derniere_observation": int(contenu["annee_derniere_observation"]),
        "scenario_par_defaut": contenu.get("scenario_par_defaut"),
        "plafond_suit_salaire_moyen": bool(contenu.get("plafond_suit_salaire_moyen", True)),
        "scenarios": contenu.get("scenarios", {}),
        "trajectoire_emploi_par_defaut": contenu.get(
            "trajectoire_emploi_par_defaut", "constant"),
        "trajectoires_emploi": contenu.get("trajectoires_emploi", {}),
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
                "valeur_retenue": poste.valeur_retenue,
                "paliers": [list(palier) for palier in poste.paliers],
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
    autrement. Le paquet porte les QUATRE PROFILS, le portage choisissant le
    sien comme le modèle choisit le sien.
    """
    prelevements = charger_prelevements(DONNEES)

    def segments(suite) -> list:
        return [{"bas": s.bas_en_plafonds, "haut": s.haut_en_plafonds,
                 "taux": s.taux} for s in suite]

    def progressif(bareme) -> dict | None:
        if bareme is None:
            return None
        return {
            "jusqu_en_plafonds": bareme.jusqu_en_plafonds,
            "paliers": [{"en_plafonds": seuil, "taux": taux}
                        for seuil, taux in bareme.paliers],
        }

    def reduction(bareme) -> dict | None:
        if bareme is None:
            return None
        return {
            "libelle": bareme.libelle,
            "plafond_en_smic": bareme.plafond_en_smic,
            "puissance": bareme.puissance,
            "taux_minimum": bareme.taux_minimum,
            "coefficient_maximal": bareme.coefficient_maximal,
            "composantes": dict(sorted(bareme.composantes.items())),
            "composantes_retraite": list(bareme.composantes_retraite),
        }

    def profil(fiche) -> dict:
        return {
            "code": fiche.code,
            "libelle": fiche.libelle,
            "libelle_assiette": fiche.libelle_assiette,
            "libelle_net": fiche.libelle_net,
            "cout_du_travail": fiche.cout_du_travail,
            "incidence": fiche.incidence.value,
            "annee": fiche.annee,
            "fiabilite": int(fiche.fiabilite),
            "csg_deductible": fiche.csg_deductible,
            "csg_imposable": fiche.csg_imposable,
            "crds": fiche.crds,
            "abattement_frais": segments(fiche.abattement_frais),
            "postes": [
                {
                    "code": poste.code,
                    "libelle": poste.libelle,
                    "retraite": poste.retraite,
                    "dans_la_reduction_generale": poste.dans_la_reduction_generale,
                    "taux_dans_la_reduction": poste.taux_dans_la_reduction,
                    "cadres_seulement": poste.cadres_seulement,
                    "due_au_dela_de_un_plafond": poste.due_au_dela_de_un_plafond,
                    "progressif": progressif(poste.progressif),
                    "salarie": segments(poste.salarie),
                    "employeur": segments(poste.employeur),
                }
                for poste in fiche.postes
            ],
            "reduction_generale": reduction(fiche.reduction_generale),
        }

    return {
        "annee": prelevements.annee,
        "fiabilite": int(prelevements.fiabilite),
        "profils": {code: profil(fiche)
                    for code, fiche in sorted(prelevements.profils.items())},
        # Ce qu'on paie une fois retraité, et non plus en travaillant : c'est
        # lui qui permet au site d'écrire une pension NETTE, donc de la
        # comparer à un salaire net plutôt qu'à côté de lui.
        "pensions": {
            "csg_taux_plein": prelevements.pensions.csg_taux_plein,
            "crds": prelevements.pensions.crds,
            "casa": prelevements.pensions.casa,
            "csg_affectee_vieillesse":
                prelevements.pensions.csg_affectee_vieillesse,
            "bareme_csg": [
                {"libelle": tranche.libelle, "taux": tranche.taux,
                 "revenu_fiscal_maximum": tranche.revenu_fiscal_maximum}
                for tranche in prelevements.pensions.bareme_csg
            ],
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



def _frontiere() -> dict:
    """Le versant `cotisation` de la frontière — chiffré une fois, ici.

    C'est une DÉRIVÉE, non une donnée brute : le produit du taux déplafonné par
    l'assiette de l'Urssaf. Le portage la relit au lieu de la recalculer, et un
    témoin vérifie que les deux disent la même chose. C'est la règle du dépôt —
    un chiffre qui dépend de la porte par laquelle on entre n'est pas un
    chiffre —, appliquée au moins cher : il n'y a ici aucun modèle à porter,
    seulement un produit déjà fait.
    """
    from retraite_notionnelle.frontiere import charger_frontiere

    return charger_frontiere(DONNEES).dictionnaire()


def _bilan(contexte=None) -> dict:
    """Le bilan des quatre systèmes comparés, année par année, en part de PIB.

    C'est la seule entrée du paquet qui coûte un calcul complet — dix-huit
    secondes : le coefficient d'équilibre d'un système est un rapport de
    masses, et une masse suppose la grille des cas types simulée sous chaque
    système et pondérée par les effectifs. La page des résultats en a besoin
    pour dire ce que les comptes financent de la pension qu'elle affiche, et
    elle ne peut pas le calculer chez le lecteur : d'où cette table.

    Elle est calculée sous les réglages de RÉFÉRENCE, et ``donnees/bilan.py``
    dit ce que ce figeage coûte et ce qu'il ne coûte pas.
    """
    from retraite_notionnelle.web.pages import Contexte, SCENARIOS_COMPARES

    # ``contexte`` n'est pas une option de commodité : c'est ce qui permet au
    # test du paquet de réutiliser le coût que d'autres tests du même module
    # ont déjà calculé, au lieu de payer les dix-huit secondes une seconde
    # fois. Il doit porter les réglages de RÉFÉRENCE, comme celui-ci.
    contexte = contexte or Contexte()
    solde = contexte.cout().solde
    assiette = contexte.assiette()
    scenarios = [scenario for scenario, _ in SCENARIOS_COMPARES]
    # Le PIB de la dernière année PUBLIÉE, et elle seule : au-delà, un montant
    # en milliards ne serait qu'une hypothèse de croissance déguisée en
    # observation. C'est ce qui permet à la page de dire un manque de 2070 en
    # euros — « au PIB d'aujourd'hui », et elle l'écrit.
    publiees = [ligne for ligne in solde.annees if ligne.pib > 0.0]
    # L'ENGAGEMENT ACQUIS, à la dernière date qu'Eurostat transmette : c'est
    # par elle que le chiffre du dépôt et celui du tableau 29 se comparent, et
    # la choisir ailleurs comparerait deux millésimes. Douze secondes de plus,
    # pour la même raison que le reste de cette table : la page ne peut pas
    # sommer quatre-vingts années de flux chez le lecteur.
    from retraite_notionnelle.cout import calculer_engagements

    comptes = contexte.comptes()
    annee_engagement = comptes.annees_engagements()[-1]
    engagement = calculer_engagements(
        contexte.simulateur(), contexte.depenses(), contexte.population(),
        annee_engagement, scenarios)
    # LES ÉCARTS MÉDIANS DE LA GRILLE, que l'accueil écrit en réponse à « ma
    # retraite va-t-elle baisser ? ». Cinq secondes de plus, et pour la même
    # raison : l'accueil ne simule rien, et il se rend toujours sous les
    # réglages de référence, ceux de cette table.
    from dataclasses import asdict

    from retraite_notionnelle.castypes import calculer_cas_types, ecarts_medians

    ecarts = ecarts_medians(calculer_cas_types(contexte.simulateur()))
    return {
        "ecarts_medians": asdict(ecarts),
        "engagements": {
            "annee": engagement.annee,
            "horizon": engagement.horizon,
            "scenarios": {s: engagement.part_pib(s) for s in scenarios},
            "retraites": engagement.retraites,
            "actifs": engagement.actifs,
            "hors_projection": engagement.hors_projection,
            "sensibilite": [{"ecart": ecart, "part_pib": part}
                            for ecart, part in engagement.sensibilite()],
            "publie": comptes.engagements(annee_engagement),
        },
        "premiere_annee_projetee": solde.premiere_annee_projetee,
        "annee_assiette": assiette.derniere_annee,
        "part_pib_assiette": assiette.part_pib(assiette.derniere_annee),
        "annee_pib": publiees[-1].annee if publiees else 0,
        "pib": publiees[-1].pib if publiees else 0.0,
        "annees": [
            {
                "annee": ligne.annee,
                "projete": ligne.projete,
                "part_contributive": ligne.part_contributive,
                "coefficients": {s: ligne.coefficient(s) for s in scenarios},
                "soldes": {s: ligne.solde(s) for s in scenarios},
                "ressources": {s: ligne.ressources_de(s) for s in scenarios},
            }
            for ligne in solde.annees
        ],
    }


def construire_bilan(contexte=None) -> bytes:
    """La table figée, écrite dans ``data/derive/`` et relue par le modèle."""
    texte = json.dumps(_bilan(contexte), ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"))
    return (texte + "\n").encode("utf-8")

def construire(bilan: bytes) -> bytes:
    """Paquet complet, à contenu identique pour des données identiques.

    ``bilan`` est le contenu de ``data/derive/equilibre.json``, passé plutôt
    que relu : ``--verifier`` ne doit rien écrire, et les deux fichiers
    doivent porter les mêmes octets.
    """
    paquet = {
        "version": VERSION,
        "series": _series(),
        "hypotheses": _hypotheses(),
        "courbe_taux_sans_risque": _courbe_taux_sans_risque(),
        "frais_epargne_retraite": _frais_epargne_retraite(),
        "prelevements_remuneration": _prelevements_remuneration(),
        "quotients": _quotients(),
        "calibrations": _calibrations(),
        "populations": _populations(),
        "regimes": _regimes(),
        "inventaire": _inventaire(),
        "frontiere": _frontiere(),
        "avantages": _avantages(),
        "affiliations": _affiliations(),
        "valeurs_point": _valeurs_point(),
        "rendements_points": _rendements(),
        "conversions_points": _conversions_points(),
        "classes_cotisation": _classes_cotisation(),
        "salaires_forfaitaires": _salaires_forfaitaires(),
        "durees_requises": _table_par_generation(DureesRequises),
        "durees_requises_avant_suspension": _table_par_generation(
            DureesRequisesAvantSuspension),
        "durees_requises_regimes": _durees_requises_regimes(),
        "durees_proratisation": _table_par_generation(DureesProratisation),
        "revalorisation_salaires": _revalorisation_salaires(),
        "revalorisation_pensions": _revalorisation_pensions(),
        "ages_ouverture": _table_par_generation(AgesOuverture),
        "ages_surcote_regimes_speciaux": _table_par_generation(AgesSurcoteRegimesSpeciaux),
        "ages_annulation_decote": _table_par_generation(AgesAnnulationDecote),
        "ages_regimes": _ages_regimes(),
        "categorie_active": _categorie_active(),
        "durees_services_militaires": _durees_services_militaires(),
        "ages_jouissance_militaire": _table_par_generation(AgesJouissanceMilitaire),
        "coefficients_minoration": _table_par_generation(CoefficientsMinoration),
        "annees_salaire_reference": _table_par_generation(AnneesSalaireReference),
        "periodes_non_travaillees": _periodes_non_travaillees(),
        "assiette_minimale_independants": _assiette_minimale_independants(),
        "profil_salaire_age": _profil_salaire("profil_salaire_age.csv", "annee"),
        "profil_salaire_categorie": _profil_salaire(
            "profil_salaire_categorie.csv", "categorie"),
        "profil_salaire_statut_public": _profil_salaire(
            "profil_salaire_statut_public.csv", "statut"),
        "profil_salaire_secteur": _profil_salaire_secteur(),
        "contribution_employeur_public": _contribution_employeur_public(),
        "minimum_contributif": _minimum_contributif(),
        "minimum_garanti": _minimum_garanti(),
        "minimum_vieillesse": _minimum_vieillesse(),
        "durees_requises_fonction_publique": _durees_requises_fonction_publique(),
        "durees_requises_avant_soixante_ans": _durees_requises_avant_soixante_ans(),
        "decote_fonction_publique": _decote_fonction_publique(),
        "decote_regimes_speciaux": _decote_regimes_speciaux(),
        "carriere_longue": _carriere_longue(),
        "majorations_enfants": _majorations_enfants(),
        "surcote_parentale": _surcote_parentale(),
        "majoration_enfants_points": _majoration_enfants_points(),
        "surcote_baremes": _surcote_baremes(),
        "depenses": _depenses(),
        "comptes_retraite": _comptes_retraite(),
        "population": _population(),
        "effectifs_retraites": _effectifs_retraites(),
        "effectifs_cotisants": _effectifs_cotisants(),
        "distribution_pensions": _distribution_pensions(),
        "patrimoine_menages": _patrimoine_menages(),
        "distribution_pensions_sexes": _distribution_pensions_sexes(),
        "caracteristiques_retraites": _caracteristiques_retraites(),
        "vie_en_couple": _vie_en_couple(),
        "certification": journal_certification(DONNEES),
        # Le manifeste des sources n'entre pas dans le paquet — le site n'en
        # affiche pas le détail —, mais son COMPTE est un repère de la page
        # Données, et il était écrit en dur dans les deux portages.
        "institutions_citees": compter_institutions(DONNEES),
        # Le bilan tel que ``data/derive/equilibre.json`` le porte, jamais
        # recalculé ici : les deux côtés du portage lisent alors les mêmes
        # octets, et un écart de la table au modèle se voit à un seul
        # endroit — le diff de ce fichier.
        "bilan_equilibre": json.loads(bilan.decode("utf-8")),
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


def sorties(contexte=None) -> dict[Path, bytes]:
    """Les quatre fichiers versionnés, dans l'ordre où ils se construisent.

    Le bilan vient d'abord, et le paquet reçoit ses octets plutôt que de le
    recalculer : la table de ``data/`` et celle du navigateur ne peuvent alors
    pas diverger d'un chiffre.
    """
    bilan = construire_bilan(contexte)
    return {EQUILIBRE: bilan, PAQUET: construire(bilan),
            STYLE: construire_style(),
            CALIBRATIONS: serialiser_calibrations(_table_calibrations()).encode("utf-8")}


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
