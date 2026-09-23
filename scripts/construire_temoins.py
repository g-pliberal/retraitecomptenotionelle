#!/usr/bin/env python3
"""Fabrique les cas-témoins qui contrôlent le portage JavaScript.

Le modèle Python reste la **référence** : c'est lui qui a été écrit contre les
sources, testé et documenté. Le moteur JavaScript qui fait tourner le site doit
en reproduire les chiffres, pas les réinventer. Ce script fige donc, depuis le
Python, ce que le JavaScript doit retrouver :

* ``tests/temoins/simulations.json`` — un jeu de carrières et de réglages, avec
  la sortie complète de ``Comparaison.dictionnaire()`` pour chacun ;
* ``tests/temoins/pages.json`` — le HTML rendu de chaque page du site.

Les deux fichiers sont versionnés : une différence de chiffre entre les deux
implémentations apparaît alors dans ``node --test``, et une modification voulue
du modèle apparaît en diff dans le dépôt, chiffre par chiffre. C'est ce qui
rend le portage vérifiable plutôt que crédible.

    python scripts/construire_temoins.py            # régénère les témoins
    python scripts/construire_temoins.py --verifier # échoue s'ils sont périmés
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.carriere import Affiliations  # noqa: E402
from retraite_notionnelle.config import RACINE_DONNEES  # noqa: E402
from retraite_notionnelle.web.pages import (  # noqa: E402
    AGE_DEBUT_MINIMAL,
    Contexte,
    Saisie,
    rendre,
)

DOSSIER = RACINE / "tests" / "temoins"
SIMULATIONS = DOSSIER / "simulations.json"
PAGES = DOSSIER / "pages.json"

#: Réglages du cas de base. Chaque cas ci-dessous en dérive.
BASE = {
    "naissance": "1975", "sexe": "H", "statut": "salarie_prive_non_cadre",
    "debut": "21", "liquidation": "64", "salaire": "1", "profil": "ascendant",
    "primes": "0", "enfants": "0", "interruptions": "",
    "indexation": "triple_lock_inverse", "age_reference": "fixe_apres_bascule",
    "table": "unisexe", "conversion_acquis": "reference",
    "projection": "cor_reference", "emploi": "cor_2026", "stock": "prix",
    "bascule": "2026", "euros": "2026",
}

#: Statuts couverts par le balayage « un statut, une génération ». LA LISTE EST
#: EXHAUSTIVE, et un test l'y oblige : un statut absent d'ici n'est comparé à
#: rien: le portage JavaScript peut alors s'écarter du modèle Python sans que
#: rien ne le dise. C'est exactement ce qui est arrivé à `tranche_1_3_pass`,
#: ajoutée d'un seul côté — seul le témoin d'un statut qui l'empruntait l'a
#: montrée, et treize statuts n'en avaient aucun.
#: Les générations auxquelles chaque statut est simulé, en plus du cas de
#: base né en 1975 ; un test exige qu'il y en ait au moins cinq, dont une
#: née avant 1934 et une après 1961.
GENERATIONS_BALAYEES = (1925, 1935, 1945, 1955, 1965)

STATUTS = (
    "salarie_prive_non_cadre", "salarie_prive_cadre", "fonctionnaire_etat",
    "fonctionnaire_etat_actif", "fonctionnaire_etat_super_actif",
    "fonctionnaire_territorial_hospitalier",
    "fonctionnaire_territorial_hospitalier_actif",
    "fonctionnaire_territorial_hospitalier_super_actif",
    "ouvrier_etat_actif", "militaire", "militaire_officier",
    "contractuel_public", "agent_sncf",
    "agent_ratp", "agent_ieg", "artisan", "commercant", "profession_liberale",
    "liberal_non_reglemente",
    "exploitant_agricole", "salarie_agricole", "avocat", "marin",
    "agent_banque_de_france", "clerc_de_notaire", "mineur", "ouvrier_etat",
    "personnel_opera", "personnel_comedie_francaise", "sans_activite",
    "maitre_enseignement_prive", "medecin_liberal", "elu_local",
    "salarie_saint_pierre_et_miquelon", "salarie_mayotte", "auteur_dramatique",
    "auteur_lyrique", "gerant_debit_tabac", "micro_entrepreneur", "parlementaire",
    "membre_cese", "salarie_polynesie", "salarie_nouvelle_caledonie",
    "salarie_wallis_et_futuna", "fonctionnaire_pacifique",
    "salarie_regime_professionnel_integre", "chirurgien_dentiste_ou_sage_femme", "expert_comptable",
    "pharmacien", "auxiliaire_medical", "veterinaire", "officier_ministeriel",
    "artiste_auteur", "ministre_du_culte", "membre_congregation",
    "personnel_navigant",
    "agent_general_assurance", "notaire",
    "agent_seita", "agent_port_strasbourg", "agent_chemins_fer_secondaires",
    "salarie_prive_non_cadre_entreprise_recente", "salarie_prive_cadre_entreprise_recente",
)


def debut_admissible(statut: str, naissance: int,
                     affiliations: Affiliations | None = None) -> int | None:
    """L'âge de début du cas de base, ou le plus tardif que la fermeture admet.

    Un statut fermé aux nouveaux entrants — les mines depuis septembre 2010,
    la SEITA depuis 1981 — ne se déclare qu'à qui y est entré avant, et le
    formulaire refuse les autres. Le balayage entre donc dans ces statuts
    l'année qui précède la fermeture quand vingt et un ans est trop tard, et
    renonce à la génération qui ne peut plus y entrer à quatorze ans : un
    agent des chemins de fer secondaires né en 1975 n'est qu'un salarié du
    privé, et son témoin ne comparerait rien.
    """
    affiliations = affiliations or Affiliations(RACINE_DONNEES)
    debut = int(BASE["debut"])
    fermeture = affiliations.fermeture_entrants(statut)
    if fermeture is None:
        return debut
    dernier = fermeture.annee - 1 - naissance
    if dernier < AGE_DEBUT_MINIMAL:
        return None
    return min(debut, dernier)


def lignes_releve(premiere: int, derniere: int, statut: str, revenu: float,
                  progression: float = 1.025,
                  trimestres: int | None = 4) -> str:
    """Un relevé de carrière écrit ligne à ligne, dans le format du formulaire.

    Les montants sont ceux de CHAQUE ANNÉE, en euros de cette année-là : c'est
    l'unité du relevé, et la seule du modèle qui ne passe par aucune conversion.
    La progression géométrique n'imite aucune carrière réelle — elle fabrique
    des montants distincts d'une année à l'autre, ce qu'il faut pour que le
    témoin voie bouger un salaire annuel moyen.
    """
    lignes = []
    for rang, annee in enumerate(range(premiere, derniere + 1)):
        montant = round(revenu * progression ** rang)
        suffixe = "" if trimestres is None else f":{trimestres}"
        lignes.append(f"{annee}:{statut}:{montant}{suffixe}")
    return ",".join(lignes)


def _cas_releve() -> list[tuple[str, dict]]:
    """Les carrières LUES, celles que le relevé décrit au lieu de les déduire.

    Ce chemin ne partage avec la carrière paramétrique que la construction de
    l'année — ``_ligne_annuelle`` — et tout le reste lui est propre : le format
    du relevé, ses refus, la fraction de l'année du départ, les trimestres
    déclarés qui l'emportent sur ceux que le montant commanderait. Sans ces cas,
    le portage JavaScript de tout cela ne serait comparé à rien.
    """
    prive = lignes_releve(1998, 2038, "salarie_prive_non_cadre", 14000)
    return [
        # Le cas nu : quarante et une années pleines, quatre trimestres chacune.
        ("releve_prive", {"releve": prive}),
        # Sans les trimestres : le modèle les déduit du montant cotisé, comme
        # il le fait d'une carrière paramétrique.
        ("releve_sans_trimestres", {
            "releve": lignes_releve(1998, 2038, "salarie_prive_non_cadre",
                                    14000, trimestres=None),
        }),
        # Les trimestres DÉCLARÉS l'emportent : deux par an sur un salaire qui
        # en vaudrait quatre, c'est le temps partiel qu'aucun montant ne dit.
        ("releve_trimestres_declares", {
            "releve": lignes_releve(1998, 2038, "salarie_prive_non_cadre",
                                    14000, trimestres=2),
        }),
        # Deux régimes dans une vie, la coupure au 1er janvier : le relevé ne
        # connaît que l'année, il n'a donc pas d'année partagée.
        ("releve_deux_statuts", {
            "releve": lignes_releve(1998, 2015, "salarie_prive_non_cadre", 14000)
            + "," + lignes_releve(2016, 2038, "fonctionnaire_etat", 26000),
        }),
        # Le champ « Interruptions » reste lu : il donne à l'année son motif, ce
        # que le relevé ne sait pas dire. Le revenu de la ligne devient alors le
        # salaire de référence des régimes complémentaires.
        ("releve_avec_interruption", {
            "releve": prive, "interruptions": "2005:2008:chomage_indemnise",
        }),
        # L'année du départ, tronquée par la date de liquidation : sept mois
        # travaillés, deux trimestres civils au plus, et un revenu que la
        # fraction annualise.
        ("releve_annee_du_depart_tronquee", {
            "releve": lignes_releve(1998, 2039, "salarie_prive_non_cadre", 14000),
            "liquidation": "64", "liquidation_mois": "8",
        }),
        # La fonction publique et son assiette de primes, qui ne se lit sur
        # aucun relevé et reste donc un paramètre.
        ("releve_fonction_publique", {
            "releve": lignes_releve(1998, 2038, "fonctionnaire_etat", 22000),
            "primes": "0.22",
        }),
        # Une carrière achevée, en euros d'avant l'euro : le relevé d'un assuré
        # né en 1950 porte des montants de 1970, et le modèle ne les convertit
        # pas — il les prend pour ce qu'ils sont, les euros de leur année.
        ("releve_generation_1950", {
            "naissance": "1950", "liquidation": "60",
            "releve": lignes_releve(1970, 2009, "salarie_prive_cadre", 3500),
        }),
        # Un trou dans la carrière : le relevé saute les années où rien n'a été
        # gagné, et rien ne les remplace — c'est ce qu'un relevé fait.
        ("releve_annees_manquantes", {
            "releve": lignes_releve(1998, 2010, "salarie_prive_non_cadre", 14000)
            + "," + lignes_releve(2018, 2038, "artisan", 25000),
        }),
    ]


def _cas() -> list[dict]:
    """Jeu de cas couvrant chaque branche du moteur au moins une fois."""
    cas: list[tuple[str, dict]] = [("base", {})]
    affiliations = Affiliations(RACINE_DONNEES)

    def cas_statut(nom: str, statut: str, naissance: int) -> None:
        debut = debut_admissible(statut, naissance, affiliations)
        if debut is None:
            return
        modifications = {"statut": statut, "naissance": str(naissance)}
        if debut != int(BASE["debut"]):
            modifications["debut"] = str(debut)
        cas.append((nom, modifications))

    # Un statut d'affiliation après l'autre : c'est le catalogue des régimes,
    # les assiettes à tranches et les régimes en points qui sont balayés ici.
    for statut in STATUTS:
        cas_statut(f"statut_{statut}", statut, int(BASE["naissance"]))

    # Générations : la même carrière déplacée dans le temps traverse toutes les
    # ruptures législatives, et l'écart d'indexation entre époques.
    for naissance in (1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2005):
        cas.append((f"generation_{naissance}", {"naissance": str(naissance)}))

    # CHAQUE STATUT À DEUX ÂGES DE PLUS, et c'est le balayage qui manquait. Le
    # balayage par statut ci-dessus ne connaît qu'une génération, née en 1975 :
    # il ne visite donc que les périodes RÉCENTES de chaque fiche de régime, et
    # un régime qui appliquerait le droit de 2023 à toute son histoire y passe
    # invisible. C'est ce qui est arrivé au régime des salariés agricoles, qui
    # portait une seule période de 1930 à aujourd'hui : la corriger n'a déplacé
    # aucun témoin.
    # Une carrière née en 1935 liquide vers 1999 — avant la réforme de 2003,
    # sous la durée requise de 150 ou 160 trimestres et les dix meilleures
    # années ; une carrière née en 1955 liquide vers 2019, entre Balladur et la
    # réforme de 2023.
    # UNE QUATRIÈME GÉNÉRATION, NÉE EN 1925, parce que les tables par génération
    # ne répondent pas toutes en deçà de 1934 : la durée requise n'y répondait
    # pas, et chaque fiche retombait sur la sienne — celle d'aujourd'hui. La
    # correction n'a déplacé aucun témoin, faute d'un cas assez vieux pour la
    # voir. Celle-ci liquide vers 1990.
    # DEUX GÉNÉRATIONS DE PLUS, NÉES EN 1945 ET 1965 : la première liquide
    # entre 2005 et 2010, sous la loi Fillon et avant la loi Woerth, la seconde
    # après 2027, à soixante-quatre ans et cent soixante-douze trimestres.
    # Aucune des quatre autres ne visitait ces deux états du droit.
    for naissance in GENERATIONS_BALAYEES:
        for statut in STATUTS:
            cas_statut(f"statut_{statut}_{naissance}", statut, naissance)

    # Âges de liquidation : départ très anticipé, à l'heure, très différé.
    for age in ("52", "57", "60", "62", "64", "67", "70"):
        cas.append((f"liquidation_{age}", {"liquidation": age}))
    cas.append(("liquidation_demi", {"liquidation": "64.5", "debut": "20.5"}))
    # LE PLAFOND D'ÂGE DES MARINS : vingt-cinq annuités au plus si la pension
    # est demandée avant cinquante-cinq ans (R. 13 de leur code). Aucun témoin
    # ne visitait cette branche — celui-ci part à cinquante ans après une
    # carrière commencée à vingt, quand le régime plafonne à cent trimestres.
    cas.append(("marin_avant_cinquante_cinq", {
        "statut": "marin", "debut": "20", "liquidation": "50",
    }))

    # LE MOIS. Douze départs séparés d'un mois, pour que le diff montre ce que
    # chaque mois déplace — et surtout qu'il ne montre plus la marche de six à
    # sept pour cent que l'arrondi à l'année creusait au milieu de celle-ci.
    for mois in range(12):
        cas.append((f"liquidation_mois_{mois:02d}", {
            "liquidation": "64", "liquidation_mois": str(mois),
        }))
    # Une année d'entrée elle aussi incomplète, et un mois de naissance qui
    # décale tout : la carrière ne commence ni ne finit au 1er janvier. La
    # requête est écrite à l'ancienne — un âge, un mois —, et c'est ce qui la
    # rend utile : toute adresse partagée avant le calendrier doit continuer de
    # donner les mêmes chiffres.
    cas.append(("mois_carriere_decalee", {
        "naissance_mois": "9", "debut": "22", "debut_mois": "3",
        "liquidation": "64", "liquidation_mois": "7",
    }))
    # La même carrière, écrite comme le formulaire l'écrit désormais : des
    # dates. Née en septembre 1975, entrée en décembre 1997, partie en avril
    # 2040 — soit vingt-deux ans et trois mois, puis soixante-quatre et sept.
    # Les deux témoins doivent porter les mêmes chiffres.
    cas.append(("mois_carriere_decalee_au_calendrier", {
        "naissance": "1975-09-01", "debut": "1997-12", "liquidation": "2040-04",
    }))
    # LA FIN D'ACTIVITÉ. Le formulaire supposait qu'on travaillait jusqu'au
    # mois du départ : une ligne sans emploi dit l'inverse, et c'est là que
    # l'écart se mesure. Trois façons de ne pas travailler, qui n'ouvrent pas
    # les mêmes droits — le chômage indemnisé valide des trimestres et fait
    # cotiser l'UNEDIC aux complémentaires, l'inactivité n'ouvre rien.
    for motif in ("sans_activite", "chomage_indemnise", "chomage_non_indemnise"):
        cas.append((f"fin_activite_{motif}", {
            "naissance": "1962-03-15", "debut": "1984-09",
            "liquidation": "2026-07", "metier2_debut": "2019-04",
            "metier2_statut": motif,
        }))
    # Un creux AU MILIEU, entre deux métiers : les années qu'il couvre ne
    # cotisent pas, mais le métier d'avant continue de les affilier — c'est à
    # son régime complémentaire que l'UNEDIC verse.
    cas.append(("creux_en_milieu_de_carriere", {
        "naissance": "1962-03-15", "debut": "1984-09", "liquidation": "2026-07",
        "metier2_debut": "2000-02", "metier2_statut": "chomage_indemnise",
        "metier3_debut": "2003-09", "metier3_statut": "artisan",
        "metier3_salaire": "1.2",
    }))
    # Un changement de métier daté au mois : ce que les âges entiers ne
    # savaient pas dire, et que le calendrier donne sans un champ de plus.
    cas.append(("metier_change_en_cours_d_annee", {
        "naissance": "1975-03-15", "debut": "1996-10", "liquidation": "2040-06",
        "metier2_debut": "2011-05", "metier2_statut": "artisan",
        "metier2_salaire": "1.4",
    }))
    # Les deux générations que les textes coupent en cours d'année, de part et
    # d'autre de la coupure : 1er juillet 1951, 1er septembre 1961.
    for mois, cote in (("6", "avant"), ("8", "apres")):
        cas.append((f"generation_coupee_1951_{cote}", {
            "naissance": "1951", "naissance_mois": mois, "liquidation": "62",
        }))
    for mois, cote in (("8", "avant"), ("10", "apres")):
        cas.append((f"generation_coupee_1961_{cote}", {
            "naissance": "1961", "naissance_mois": mois, "liquidation": "62",
        }))
    # La revalorisation exceptionnelle du 1er juillet 2022 : deux liquidations
    # de la même année, de part et d'autre de la circulaire.
    for mois, cote in (("2", "avant"), ("8", "apres")):
        cas.append((f"revalorisation_juillet_2022_{cote}", {
            "naissance": "1958", "liquidation": "64", "liquidation_mois": mois,
        }))
    # LE CAS TYPE D'UN RETRAITÉ, que tests/test_revalorisation.py refait à la
    # main : un non-cadre né en janvier 1950, parti en janvier 2012 à 62 ans.
    # Sa pension de 2026 — celle du départ menée par les treize revalorisations
    # du régime général et la valeur du point Agirc-Arrco — tient ainsi le
    # portage JavaScript au chiffre refait sans le moteur.
    cas.append(("retraite_cas_type_2012", {
        "naissance": "1950", "debut": "20", "liquidation": "62",
        "salaire": "0.8", "unite_revenu": "moyen",
    }))

    # Règles de modélisation, une par une.
    for mode in ("triple_lock_inverse", "triple_lock_inverse_nominal",
                 "mediane_trois_taux", "moyenne_trois_taux",
                 "revalorisation_portee_au_compte", "pib_nominal",
                 "prix", "salaires"):
        cas.append((f"indexation_{mode}", {"indexation": mode}))
    # Le lissage est orthogonal à la règle : on fige les deux fenêtres offertes
    # sur le défaut, et la règle italienne — PIB nominal lissé sur cinq ans —
    # qui est la raison d'être du paramètre.
    for fenetre in ("2", "5", "17"):
        cas.append((f"lissage_{fenetre}", {"lissage": fenetre}))
    cas.append(("lissage_regle_italienne",
                {"indexation": "pib_nominal", "lissage": "5"}))
    # Le cas de base porte le DÉFAUT — 64 ans à partir de la bascule. Les trois
    # variantes sont balayées ici, le cliquet compris : c'est lui qui a été le
    # défaut jusqu'en septembre 2026, et le laisser hors du balayage aurait
    # retiré du portage la règle que quatre-vingts ans de liquidations
    # antérieures à la bascule continuent d'utiliser.
    for mode in ("cliquet_legal", "cliquet_puis_esperance_vie", "legal_sans_cliquet"):
        cas.append((f"age_reference_{mode}", {"age_reference": mode}))
    cas.append(("table_par_sexe", {"table": "par_sexe"}))
    # Conversion des droits acquis : à l'âge de référence (défaut) ou à l'âge de
    # départ effectif, seul endroit du modèle où le passage aux comptes
    # notionnels peut retirer quelque chose à des droits déjà ouverts.
    cas.append(("conversion_acquis_liquidation", {"conversion_acquis": "liquidation"}))
    cas.append(("conversion_acquis_liquidation_tardive", {
        "conversion_acquis": "liquidation", "liquidation": "70",
    }))
    cas.append(("table_par_sexe_femme", {"table": "par_sexe", "sexe": "F"}))
    # La population de la table : la mortalité des fonctionnaires civils de
    # l'État, telle que leur régime la publie, à la place de celle de la
    # population générale — sur la carrière qu'elle décrit, et croisée avec
    # la table par sexe, puisque le facteur est calé sexe par sexe.
    cas.append(("population_fonctionnaires_civils", {
        "population": "fonctionnaires_civils_etat", "statut": "fonctionnaire_etat",
    }))
    cas.append(("population_fonctionnaires_civils_femme_par_sexe", {
        "population": "fonctionnaires_civils_etat", "statut": "fonctionnaire_etat",
        "table": "par_sexe", "sexe": "F",
    }))
    # Le vingtile de niveau de vie de l'INSEE : les 5 % les plus modestes, dont
    # le facteur est calé sur le rapport à l'ensemble de l'étude — le seul
    # chemin de calibration qui passe par cette règle.
    cas.append(("population_niveau_de_vie_modeste", {"population": "niveau_de_vie_v01"}))
    # Le rattachement par la pension : circulaire sous un compte notionnel, et
    # résolu par point fixe — le chemin que le témoin doit tenir des deux côtés.
    cas.append(("rattachement_pension", {"rattachement": "pension"}))
    cas.append(("rattachement_pension_smic", {"rattachement": "pension", "salaire": "0.55"}))
    for projection in ("cor_productivite_basse", "cor_productivite_haute"):
        cas.append((f"projection_{projection}", {"projection": projection}))
    # L'emploi constant après 2025 : la convention d'avant la trajectoire du
    # COR, qui ne déplace que les systèmes 2 à 6, par l'indexation.
    cas.append(("emploi_constant", {"emploi": "constant"}))
    for bascule in ("1980", "2000", "2026", "2040", "2060"):
        cas.append((f"bascule_{bascule}", {"bascule": bascule, "naissance": "1990"}))
    for euros in ("1980", "2000", "2050"):
        cas.append((f"euros_{euros}", {"euros": euros}))

    # Profils de rémunération et niveaux de revenu, y compris au-dessus du
    # plafond de la Sécurité sociale et sous le SMIC.
    for profil in ("plat", "fortement_ascendant"):
        cas.append((f"profil_{profil}", {"profil": profil}))
    # « 10 » est le maximum du formulaire, et il est là pour une raison précise :
    # c'est le seul niveau qui franchisse les huit plafonds de la Sécurité
    # sociale que le modèle posait jusqu'au 20 septembre 2026 par-dessus le
    # régime fusionné. Le plafond levé, l'assiette y vaut le revenu entier, et
    # ce témoin est ce qui tient les deux moteurs d'accord là-dessus.
    for salaire in ("0.2", "0.55", "1.5", "3", "8", "10"):
        cas.append((f"salaire_{salaire}", {"salaire": salaire}))

    # Le salaire saisi en euros : la division qui le ramène au multiple du
    # salaire moyen est le seul endroit où l'euro entre dans le modèle, et elle
    # doit donner le même chiffre des deux côtés du portage.
    cas.append(("revenu_en_euros", {
        "unite_revenu": "euros_mois", "salaire": "2500",
    }))
    cas.append(("revenu_en_euros_par_metier", {
        "unite_revenu": "euros_mois", "salaire": "2000",
        "metier2_debut": "38", "metier2_statut": "salarie_prive_cadre",
        "metier2_salaire": "4500",
    }))

    # Plusieurs métiers dans une vie. Ce qui est balayé ici, c'est le découpage
    # de la carrière entre statuts : le changement au 1er janvier, le changement
    # en cours d'année — avec l'égalité six mois contre six mois —, et la
    # traversée de régimes qui n'ont ni le même taux ni le même barème.
    cas.append(("metiers_prive_puis_fonctionnaire", {
        "metier2_debut": "42", "metier2_statut": "fonctionnaire_etat",
    }))
    cas.append(("metiers_prive_puis_independant", {
        "metier2_debut": "35", "metier2_statut": "artisan", "metier2_salaire": "1.6",
    }))
    cas.append(("metiers_trois_statuts", {
        "metier2_debut": "33", "metier2_statut": "contractuel_public",
        "metier2_salaire": "0.8",
        "metier3_debut": "48", "metier3_statut": "fonctionnaire_etat",
        "metier3_salaire": "1.3",
    }))
    # Six métiers : le maximum du formulaire, et cinq changements rapprochés —
    # une année entière ne revient alors à aucun métier en totalité.
    cas.append(("metiers_maximum", {
        "naissance": "1960", "liquidation": "62",
        "metier2_debut": "40", "metier2_statut": "agent_sncf",
        "metier3_debut": "43", "metier3_statut": "avocat",
        "metier4_debut": "46", "metier4_statut": "marin",
        "metier5_debut": "49", "metier5_statut": "exploitant_agricole",
        "metier6_debut": "52", "metier6_statut": "salarie_prive_cadre",
    }))
    # Le changement tombe en cours d'année, et le mois de naissance décide
    # duquel des deux métiers l'année relève : juillet donne six mois contre
    # six — l'égalité revient au métier qui ouvre l'année.
    for mois, cote in (("5", "avant"), ("7", "egalite"), ("10", "apres")):
        cas.append((f"metiers_changement_en_cours_d_annee_{cote}", {
            "naissance_mois": mois, "metier2_debut": "42",
            "metier2_statut": "artisan", "metier2_salaire": "3",
        }))
    # Deux activités À LA FOIS, déclarées comme telles : la seconde s'ajoute à
    # la première au lieu de la remplacer. Un régime distinct qui sert sa
    # pension en plus, puis deux régimes alignés que la liquidation unique
    # réunit, sur une période bornée qui commence et finit en cours d'année —
    # là où le plafond de quatre trimestres et la somme des revenus d'une même
    # année se voient.
    cas.append(("cumul_salarie_et_liberal", {
        "metier2_debut": "35", "metier2_statut": "medecin_liberal",
        "metier2_salaire": "0.8", "metier2_cumul": "oui",
    }))
    cas.append(("cumul_salarie_et_artisan_borne", {
        "naissance_mois": "5", "salaire": "2",
        "metier2_debut": "40.25", "metier2_statut": "artisan",
        "metier2_salaire": "0.5", "metier2_cumul": "oui", "metier2_fin": "52.5",
    }))
    # Une interruption qui tombe sur le changement de métier : l'année n'est pas
    # cotisée, mais elle relève quand même d'un statut, et d'un seul.
    cas.append(("metiers_avec_interruption", {
        "naissance": "1970", "metier2_debut": "40", "metier2_statut": "artisan",
        "interruptions": "2008:2012:chomage_indemnise",
    }))

    # Interruptions de carrière, primes, enfants — ce que les scénarios
    # notionnels neutralisent.
    cas.append(("interruption_simple", {"interruptions": "2000:2004:education_enfant"}))
    cas.append(("interruption_multiple", {
        "interruptions": "1999:2001:chomage_indemnise, 2008:2009:maladie",
        "naissance": "1970",
    }))
    # DEUX CASES QU'AUCUN CAS TYPE N'EXERÇAIT. Un fonctionnaire interrompu :
    # la pension de l'État se proratise sur les SERVICES, dont L. 9 écarte le
    # chômage. Et une carrière longue hachée : le départ anticipé compte la
    # durée COTISÉE, que D. 351-1-2 complète d'une liste fermée de périodes
    # réputées telles, chacune sous sa limite. Les deux règles ne tenaient
    # qu'aux tests Python, le portage ne leur était comparé sur rien.
    cas.append(("fonctionnaire_interrompu", {
        "statut": "fonctionnaire_etat", "sexe": "F", "enfants": "2",
        "interruptions": "2000:2004:chomage_indemnise",
    }))
    cas.append(("carriere_longue_hachee", {
        "naissance": "1965", "debut": "17", "liquidation": "60",
        "salaire": "0.8", "profil": "plat",
        "interruptions": "1990:1990:chomage_indemnise, 1995:1997:maternite",
    }))
    cas.append(("primes_fonction_publique", {
        "statut": "fonctionnaire_etat", "primes": "0.22",
    }))
    # Les trois régimes de l'IRCEC ont leur propre barème de minoration — 2,5 %
    # pour chacune des deux premières années manquantes, 5 % ensuite, ou le
    # coefficient du régime de base s'il est plus favorable — et le RAAP comme
    # le RACD majorent de 10 % la pension de qui a eu trois enfants. Les
    # témoins des statuts d'auteur ont tous une carrière complète et aucun
    # enfant : ni le barème ni la majoration n'étaient comparés au portage. Une
    # autrice dramatique entrée à quarante ans, mère de trois enfants, les fait
    # jouer tous les deux, au RAAP comme au RACD.
    cas.append(("auteur_dramatique_carriere_courte", {
        "statut": "auteur_dramatique", "naissance": "1970", "debut": "40",
        "enfants": "3", "sexe": "F",
    }))
    cas.append(("enfants", {"enfants": "3", "sexe": "F"}))

    # Les trimestres accordés au titre des enfants ne dépendent pas du seul
    # nombre d'enfants : la MDA n'existe pas avant 1972, elle vaut un an par
    # enfant jusqu'en 1974, elle va à la mère, et la fonction publique sert sa
    # propre bonification — un an par enfant né avant 2004, deux trimestres
    # ensuite. Un cas par branche, pour que la table se lise dans les témoins.
    # La carrière commence à trente ans : une carrière complète est au taux
    # plein et proratisée à un, et ces trimestres n'y déplacent rien — ils ne se
    # voient que sur une carrière incomplète, qui est aussi le cas où le droit
    # les a voulus.
    enfants = {"enfants": "3", "sexe": "F", "debut": "30"}
    cas.append(("enfants_carriere_incomplete", dict(enfants)))
    cas.append(("enfants_pere", {**enfants, "sexe": "H"}))
    cas.append(("enfants_avant_1972", {
        **enfants, "naissance": "1910", "liquidation": "60",
    }))
    cas.append(("enfants_loi_boulin", {
        **enfants, "naissance": "1913", "liquidation": "60",
    }))
    cas.append(("enfants_fonction_publique_nes_avant_2004", {
        **enfants, "statut": "fonctionnaire_etat", "naissance": "1960",
    }))
    cas.append(("enfants_fonction_publique_nes_depuis_2004", {
        **enfants, "statut": "fonctionnaire_etat", "naissance": "1985",
    }))
    # Artisane liquidant avant l'absorption du RSI par la CNAV : c'est bien son
    # régime aligné qui porte les trimestres, comme l'article L. 634-2 le veut.
    cas.append(("enfants_regime_aligne", {
        **enfants, "statut": "artisan", "naissance": "1950",
    }))
    # La loi Boulin ne visait que les mères d'AU MOINS DEUX enfants : le même
    # départ, avec un enfant, ne donne rien.
    cas.append(("enfants_loi_boulin_enfant_unique", {
        **enfants, "enfants": "1", "naissance": "1913", "liquidation": "60",
    }))
    # Une libérale : la CNAVPL rend aux mères la majoration de durée depuis le
    # 1er avril 2010 (L. 643-1-1), et c'est un régime EN POINTS qui la porte.
    # Deux enfants lui valent seize trimestres, et sa décote tombe à zéro.
    cas.append(("enfants_liberale", {
        **enfants, "statut": "profession_liberale", "enfants": "2",
        "naissance": "1964", "debut": "24", "liquidation": "62.75",
    }))
    # La CAVAMAC ne majore depuis 2024 que les années COTISÉES au-delà de
    # 67 ans : deux années de travail valent 10 %, deux années d'attente rien.
    agent_general = {"statut": "agent_general_assurance", "naissance": "1960",
                     "liquidation": "69"}
    cas.append(("agent_general_surcote_cotisee", dict(agent_general)))
    cas.append(("agent_general_surcote_sans_cotiser", {
        **agent_general, "interruptions": "2027:2028:sans_activite",
    }))

    # Surcote parentale : durée requise atteinte à 63 ans, trimestres pour
    # enfants, et une année de travail de plus que la loi de 2023 a imposée.
    parentale = {"enfants": "2", "sexe": "F", "debut": "18",
                 "naissance": "1968", "liquidation": "64"}
    cas.append(("surcote_parentale", dict(parentale)))
    cas.append(("surcote_parentale_pere", {**parentale, "sexe": "H"}))
    cas.append(("surcote_parentale_duree_incomplete", {**parentale, "debut": "30"}))
    cas.append(("surcote_parentale_fonction_publique", {
        **parentale, "statut": "fonctionnaire_etat",
    }))
    cas.append(("surcote_parentale_avec_surcote_ordinaire", {
        **parentale, "liquidation": "67",
    }))

    # La SNCF et la RATP ont leur table de durée requise, leur âge de référence
    # de la décote fixé à cinquante-sept ans et leur âge de surcote : trois
    # branches que le cas de base, né en 1975 et parti à soixante-quatre ans
    # avec 172 trimestres, ne visite pas.
    for nom, statut, naissance, liquidation in (
        ("sncf_depart_a_l_ouverture", "agent_sncf", 1980, "54"),
        ("ratp_duree_propre", "agent_ratp", 1966, "60"),
        ("sncf_surcote_apres_soixante_quatre_ans", "agent_sncf", 1975, "66"),
        ("ieg_duree_par_anciennete_active", "agent_ieg", 1968, "60"),
        ("ieg_depart_a_l_ouverture", "agent_ieg", 1968, "57.25"),
        # Des RETRAITÉS : la durée se lit au mois où ils ont réuni les
        # conditions (calendrier de 2008, table de 2014), l'âge à leur
        # génération — et non à l'année où ils sont partis.
        ("sncf_retraite_de_2010", "agent_sncf", 1960, "50"),
        ("ieg_generation_1965_partie_en_2025", "agent_ieg", 1965, "60"),
        ("ratp_generation_1970", "agent_ratp", 1970, "56"),
    ):
        cas_statut(nom, statut, naissance)
        assert cas[-1][0] == nom, f"{nom} : aucun âge d'entrée admissible"
        cas[-1][1]["liquidation"] = liquidation

    # Les carrières LUES sur un relevé, plutôt que reconstituées.
    cas.extend(_cas_releve())

    # Retraité de longue date : la bascule est postérieure à sa liquidation.
    cas.append(("deja_liquide", {"naissance": "1935", "liquidation": "60"}))
    cas.append(("liquidation_a_la_bascule", {"naissance": "1962", "liquidation": "64"}))

    return [{"nom": nom, "requete": {**BASE, **modifications}}
            for nom, modifications in cas]


def _fini(valeur):
    """Remplace NaN et les infinis par ``null``.

    ``json.dumps`` les écrit ``NaN`` et ``Infinity``, que la norme JSON ignore
    et que ``JSON.parse`` refuse. Le modèle en produit — l'écart au système
    actuel n'est pas défini quand ce système ne verse rien — et le témoin doit
    rester lisible des deux côtés.
    """
    if isinstance(valeur, float) and (valeur != valeur or valeur in (float("inf"), float("-inf"))):
        return None
    if isinstance(valeur, dict):
        return {cle: _fini(v) for cle, v in valeur.items()}
    if isinstance(valeur, list):
        return [_fini(v) for v in valeur]
    return valeur


def _simulations(contexte: Contexte) -> dict:
    resultats = {}
    for cas in _cas():
        saisie = Saisie.depuis_requete(cas["requete"])
        resultats[cas["nom"]] = {
            "requete": cas["requete"],
            "resultat": _fini(contexte.simuler(saisie).dictionnaire()),
        }
    return resultats


#: Le bloc JSON de la page reprend les mêmes chiffres que les témoins
#: numériques, mais formatés par ``json.dumps`` : sa comparaison ne dirait rien
#: du rendu et ne ferait que constater que Python et JavaScript n'écrivent pas
#: les flottants de la même façon. On le retire des deux côtés.
_BLOC_JSON = re.compile(r'(<pre class="json">).*?(</pre>)', re.DOTALL)


def sans_bloc_json(html: str) -> str:
    return _BLOC_JSON.sub(r"\1\2", html)


#: Un jeu de règles qui n'est pas celui par défaut, pour les trois pages qui
#: agrègent : l'indexation sur les prix au lieu de la masse salariale, la
#: bascule décalée de quatre ans, et la part patronale portée au compte.
REGLES_AUTRES = {
    "indexation": "prix", "bascule": "2030", "part_cotisation": "totale",
    # Et le stock réindexé à la bascule : la convention d'avant le
    # 20 septembre 2026, qui ne touche que la page Coût.
    "stock": "reindexe",
}


def _pages(contexte: Contexte) -> dict:
    demandes = [
        ("simuler", "/simuler", {}),
        ("simuler_calcul", "/simuler", BASE),
        ("simuler_femme_interrompue", "/simuler", {
            **BASE, "sexe": "F", "naissance": "1968", "statut": "salarie_prive_non_cadre",
            "interruptions": "1995:1999:education_enfant", "enfants": "2",
            "salaire": "0.9",
        }),
        ("simuler_regime_special", "/simuler", {
            **BASE, "statut": "agent_sncf", "naissance": "1960", "liquidation": "52",
        }),
        # Le quatrième profil de fiche de paie — celui d'un agent public non
        # titulaire, qui relève du régime général et de l'Ircantec. Les trois
        # autres sont déjà couverts : le salarié du privé par `simuler_calcul`,
        # le fonctionnaire par `simuler_rafp`, l'indépendant par
        # `simuler_notionnel_plus_genereux`. Sans ce cas, le portage du bloc
        # « Et pendant que vous cotisez » n'était comparé que sur trois d'entre
        # eux, et c'est le genre de trou qui se voit six mois plus tard.
        ("simuler_agent_non_titulaire", "/simuler", {
            **BASE, "statut": "contractuel_public",
        }),
        ("simuler_indexation_prix", "/simuler", {**BASE, "indexation": "prix"}),
        ("simuler_conversion_acquis", "/simuler", {
            **BASE, "conversion_acquis": "liquidation",
        }),
        # Carrière entièrement interrompue : capital notionnel nul, donc aucune
        # cascade à afficher — et surtout aucune division par zéro.
        ("simuler_carriere_vide", "/simuler", {
            **BASE, "interruptions": "1996:2038:chomage_indemnise",
        }),
        # La saisie PAR LA PENSION, et les trois refus qu'elle peut rendre.
        # L'inversion est une dichotomie de dix-huit coupes : c'est la seule
        # boucle du site dont le résultat dépend de l'ordre des opérations
        # flottantes, et ces quatre témoins sont ce qui garantit que les deux
        # moteurs la parcourent pas pour pas.
        # Le chemin réel : on se déclare retraité, et la saisie suit. Les
        # dates de BASE étant celles d'un actif, ce témoin fige aussi la phrase
        # du désaccord — le premier clic de qui vient pour sa pension.
        ("simuler_par_pension", "/simuler", {
            **BASE, "situation": "retraite", "pension": "1500",
        }),
        # Une situation de retraité COHÉRENTE avec ses dates : aucune phrase de
        # désaccord, et la date de départ dit « effectif » et non « souhaité ».
        ("simuler_retraite_coherent", "/simuler", {
            **BASE, "situation": "retraite", "pension": "1500",
            "naissance": "1955", "debut": "20", "liquidation": "62",
        }),
        # Et le retraité qui préfère donner ce qu'il gagnait : l'échappatoire.
        ("simuler_retraite_par_revenu", "/simuler", {
            **BASE, "situation": "retraite", "saisie_par": "revenu",
            "naissance": "1955", "debut": "20", "liquidation": "62",
        }),
        ("simuler_par_pension_brute", "/simuler", {
            **BASE, "saisie_par": "pension", "pension": "2400",
            "montants": "brut",
        }),
        # Au-dessus de ce que le statut peut acquérir : le plafond de tranche.
        ("simuler_pension_trop_haute", "/simuler", {
            **BASE, "saisie_par": "pension", "pension": "9000",
        }),
        # Au-dessous du minimum contributif et de l'ASPA : le plancher.
        ("simuler_pension_trop_basse", "/simuler", {
            **BASE, "saisie_par": "pension", "pension": "1",
        }),
        ("simuler_saisie_refusee", "/simuler", {**BASE, "liquidation": "12"}),
        # Un refus alors qu'on saisissait en multiples : le formulaire repart de
        # ses valeurs par défaut, mais dans l'unité où l'on travaillait.
        ("simuler_saisie_refusee_en_multiples", "/simuler", {
            **BASE, "liquidation": "12", "unite_revenu": "moyen", "salaire": "1.2",
        }),
        # Bornes que seul le formulaire opposait autrefois : une adresse forgée
        # à la main les franchissait, et la page affichait sans broncher des
        # pensions à soixante chiffres. Les trois cas figent, côté Python
        # comme côté JavaScript, le refus qui les arrête.
        ("simuler_euros_hors_bornes", "/simuler", {**BASE, "euros": "9999"}),
        ("simuler_bascule_hors_bornes", "/simuler", {**BASE, "bascule": "1900"}),
        ("simuler_enfants_hors_bornes", "/simuler", {**BASE, "enfants": "999"}),
        # Ni la bascule ni l'année des euros ne valent leur défaut : c'est le
        # cas qui débusque un texte citant une année écrite en dur — le chapeau
        # annonçait « à compter de 2026 » quand le scénario 3 partait de 2035.
        # Le scénario 2 AU-DESSUS du scénario 1 : la trajectoire annonçait
        # « l'écart se creuse » en affichant un montant négatif.
        ("simuler_notionnel_plus_genereux", "/simuler", {
            **BASE, "statut": "profession_liberale", "liquidation": "70",
            "salaire": "4", "unite_revenu": "moyen",
        }),
        # Liquidation en cours d'année : la trajectoire ne doit rien tracer
        # avant le départ, quand elle partait de l'âge entier précédent.
        ("simuler_depart_en_cours_d_annee", "/simuler", {
            **BASE, "liquidation_mois": "6",
        }),
        ("simuler_annees_deplacees", "/simuler", {
            **BASE, "bascule": "2035", "euros": "2000",
        }),
        # Départ dans l'année de référence : les deux unités se confondent et
        # chaque scénario n'affiche qu'un chiffre. C'est la branche que les
        # textes d'unité doivent traiter à part.
        ("simuler_depart_annee_reference", "/simuler", {
            **BASE, "naissance": "1962", "liquidation": "64", "euros": "2026",
        }),
        # Une carrière en trois métiers : le formulaire porte alors trois lignes
        # remplies et une quatrième vide, et la page récapitule le parcours.
        ("simuler_plusieurs_metiers", "/simuler", {
            **BASE, "naissance": "1968", "liquidation": "64",
            "metier2_debut": "34", "metier2_statut": "contractuel_public",
            "metier2_salaire": "0.8",
            "metier3_debut": "47", "metier3_statut": "artisan",
            "metier3_salaire": "1.5",
        }),
        # Une ligne qui n'est pas un métier : la légende la nomme « période,
        # sans emploi », le champ de revenu disparaît, et le résumé dit à quel
        # âge l'activité s'arrête.
        ("simuler_periode_sans_emploi", "/simuler", {
            **BASE, "naissance": "1962-03-15", "debut": "1984-09",
            "liquidation": "2026-07", "metier2_debut": "2019-04",
            "metier2_statut": "chomage_indemnise",
        }),
        # Le même départ, mais au travail jusqu'au bout : le pilier reçoit un
        # seul versement, l'année de la bascule, et n'a pas un an pour
        # rapporter. Sans emploi, il ne recevait rien — la page le dit. Née
        # en 1961 et partie à 65 ans passés : l'âge légal de la proposition ne
        # reporte pas ce départ.
        ("simuler_depart_l_annee_de_la_bascule", "/simuler", {
            **BASE, "naissance": "1961-03-15", "debut": "1984-09",
            "liquidation": "2026-07",
        }),
        # Une activité AJOUTÉE à celle en cours : la légende dit « en plus »,
        # sa date de fin est remplie, et le résumé dit les deux activités côte
        # à côte au lieu de l'une après l'autre.
        ("simuler_cumul", "/simuler", {
            **BASE, "naissance": "1968", "liquidation": "64",
            "metier2_debut": "36", "metier2_statut": "medecin_liberal",
            "metier2_salaire": "0.6", "metier2_cumul": "oui", "metier2_fin": "58",
        }),
        # Une date de fin sans que l'activité se déclare ajoutée : rien n'est
        # deviné, la saisie est refusée.
        ("simuler_cumul_non_declare", "/simuler", {
            **BASE, "metier2_debut": "40", "metier2_statut": "artisan",
            "metier2_salaire": "1", "metier2_fin": "50",
        }),
        # Une ligne de métier laissée à moitié remplie : la page doit le dire,
        # et dire ce qui manque.
        ("simuler_metier_incomplet", "/simuler", {**BASE, "metier2_debut": "40"}),
        # Une carrière LUE sur un relevé : le dépliant s'ouvre, la zone de
        # saisie porte les lignes, et le récapitulatif dit que les métiers du
        # formulaire n'ont pas servi.
        ("simuler_releve", "/simuler", {
            **BASE, "releve": lignes_releve(1998, 2038,
                                            "salarie_prive_non_cadre", 14000),
        }),
        # Un relevé refusé : la phrase cite la ligne fautive, et le formulaire
        # doit repartir sans elle.
        ("simuler_releve_refuse", "/simuler", {
            **BASE, "releve": "2005:salarie_prive_non_cadre:24000:9",
        }),
        # Quatre blocs de la page de résultats qu'aucun témoin n'atteignait —
        # le portage y était comparé par le seul tirage au hasard, qui ne dit
        # pas en diff ce qu'un changement déplace. Le tableau des indexations
        # ne paraît que sur la règle par défaut, la rente RAFP que pour un
        # fonctionnaire à primes, le minimum contributif que sous son plafond,
        # et l'avertissement d'ouverture que sur un départ que le droit refuse.
        ("simuler_indexation_par_defaut", "/simuler", {**BASE, "indexation": "masse_salariale"}),
        ("simuler_rafp", "/simuler", {
            **BASE, "statut": "fonctionnaire_etat", "primes": "0.2",
        }),
        ("simuler_minimum_contributif", "/simuler", {
            **BASE, "salaire": "0.35", "debut": "20", "liquidation": "67",
        }),
        ("simuler_liquidation_non_ouverte", "/simuler", {
            **BASE, "liquidation": "55", "debut": "30",
        }),
        # Le salaire saisi en euros : le formulaire change de libellé et donne
        # l'échelle chiffrée, au lieu du multiple que personne ne connaît.
        ("simuler_revenu_en_euros", "/simuler", {
            **BASE, "unite_revenu": "euros_mois", "salaire": "2500",
        }),
        # Un salaire qui, converti, sort des bornes du modèle : le refus doit
        # redire ces bornes en euros, pas en multiples du salaire moyen.
        ("simuler_revenu_hors_bornes", "/simuler", {
            **BASE, "unite_revenu": "euros_mois", "salaire": "200",
        }),
        # L'autre unité : libellés, aide et lien de bascule changent tous les
        # trois, et le lien doit porter les montants déjà convertis.
        ("simuler_revenu_en_multiples", "/simuler", {
            **BASE, "unite_revenu": "moyen", "salaire": "1.2",
        }),
        # La bascule avec plusieurs métiers : le lien convertit chacun d'eux,
        # et c'est le seul endroit du site qui écrive une adresse complète.
        ("simuler_bascule_plusieurs_metiers", "/simuler", {
            **BASE, "unite_revenu": "euros_mois", "salaire": "2900",
            "metier2_debut": "40", "metier2_statut": "artisan",
            "metier2_salaire": "4200",
        }),
        ("programme", "/", {}),
        # La page « Cumul versé » n'est plus : son adresse rend les résultats
        # du simulateur, que les témoins ci-dessus couvrent, et
        # `ANCIENNES_ROUTES` le tient. Même chose pour « Sources », plus bas.
        ("cas_types", "/cas-types", {}),
        ("cout", "/cout", {}),
        ("avantages", "/avantages", {}),
        # Les trois pages agrégées sous d'autres règles que celles par défaut.
        # C'est le seul témoin qui compare les deux portages sur un AGRÉGAT
        # recalculé : l'avertissement, le bloc de réglages, les liens qui
        # portent la requête, et surtout les chiffres, qui bougent tous.
        # Trois réglages, choisis pour toucher trois mécanismes distincts —
        # la revalorisation des comptes, la date du changement de régime, et
        # ce que la cotisation porte au compte.
        # Une adresse qui ne porte QUE des réglages : le formulaire s'affiche
        # réglé, et aucun résultat n'est calculé — c'est ce qui permet aux
        # liens du site d'emporter les réglages jusqu'au simulateur sans y
        # déclencher le calcul d'une carrière que personne n'a saisie.
        ("simuler_regles_seules", "/simuler", REGLES_AUTRES),
        ("cas_types_regles", "/cas-types", REGLES_AUTRES),
        ("cout_regles", "/cout", REGLES_AUTRES),
        # La cascade posée sur l'horizon : le seul témoin qui emprunte l'autre
        # branche du sélecteur d'année, celle où le PIB n'est plus publié mais
        # projeté, où la cotisation unique pèse enfin, et où les reprises sur
        # successions ont une marche. Sans lui, le portage du sélecteur n'était
        # comparé que sur son année par défaut — c'est-à-dire sur la seule
        # branche où la moitié du code ne passe pas.
        ("cout_cascade_horizon", "/cout", {"cascade": "2070"}),
        # Les schémas des flux sur l'horizon, la cascade ailleurs : le seul
        # témoin où les successions paient une vraie part de la garantie, et
        # où chacun des deux sélecteurs doit garder dans ses liens l'année que
        # l'autre a posée.
        ("cout_flux_horizon", "/cout", {"flux": "2070", "cascade": "2040"}),
        # Et une année refusée : elle doit retomber sur l'année mesurée, des
        # deux côtés du portage, plutôt que lever quoi que ce soit. Celle des
        # schémas retombe sur la bascule : 2025 est une année de la cascade,
        # pas des schémas, qui ne dessinent pas une caisse qui n'existe pas.
        ("cout_cascade_hors_liste", "/cout", {"cascade": "1999", "flux": "2025"}),
        # La page Coût sous une VARIANTE DE COMPTE, et c'est le seul témoin qui
        # emprunte ce chemin. Depuis le 21 septembre 2026, le scénario demandé
        # ne déplace plus seulement ce que le modèle calcule : il choisit aussi
        # la colonne du COR que la section « solde » lit — dépense et ressource
        # du système, sous la variante correspondante de ses figures de
        # sensibilité. Sans ce témoin, les deux portages pouvaient diverger sur
        # la moitié du bilan qui est empruntée, et rien ne l'aurait dit.
        ("cout_variante_productivite", "/cout",
         {"projection": "cor_productivite_haute"}),
        ("avantages_regles", "/avantages", REGLES_AUTRES),
        ("methode", "/methode", {}),
        ("risque", "/risque", {}),
        ("partager", "/partager", {}),
    ]
    pages = {}
    for nom, chemin, parametres in demandes:
        titre, corps = rendre(contexte, chemin, parametres)
        pages[nom] = {
            "chemin": chemin,
            "parametres": parametres,
            "titre": titre,
            "corps": sans_bloc_json(corps),
        }
    return pages


def construire() -> dict[Path, bytes]:
    contexte = Contexte()
    fichiers = {
        SIMULATIONS: _simulations(contexte),
        PAGES: _pages(contexte),
    }
    return {
        chemin: (json.dumps(contenu, ensure_ascii=False, sort_keys=True, indent=1) + "\n")
        .encode("utf-8")
        for chemin, contenu in fichiers.items()
    }


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument(
        "--verifier", action="store_true",
        help="ne rien écrire ; échouer si les témoins versionnés sont périmés",
    )
    arguments = analyseur.parse_args(argv)

    attendus = construire()

    if arguments.verifier:
        for chemin, contenu in attendus.items():
            if not chemin.exists() or chemin.read_bytes() != contenu:
                print(f"{chemin.relative_to(RACINE)} est périmé — lancer "
                      "python scripts/construire_temoins.py", file=sys.stderr)
                return 1
        print("témoins à jour")
        return 0

    DOSSIER.mkdir(parents=True, exist_ok=True)
    for chemin, contenu in attendus.items():
        chemin.write_bytes(contenu)
        print(f"{chemin.relative_to(RACINE)} : {len(contenu) / 1024:.0f} Ko")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
