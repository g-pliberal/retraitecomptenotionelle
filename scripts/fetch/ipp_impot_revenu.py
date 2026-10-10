#!/usr/bin/env python3
"""L'impôt sur le revenu, de son barème à ses corrections, année par année, chez l'IPP.

    python scripts/fetch/ipp_impot_revenu.py           # réécrit la donnée
    python scripts/fetch/ipp_impot_revenu.py --lister  # imprime, sans écrire

À quoi il sert. Le dépôt ne calculait aucun impôt sur le revenu : le site
affiche un net « avant impôt sur le revenu », les indicateurs de cycle de vie
s'arrêtent aux prélèvements sociaux, et la page Coût n'a pas d'effet retour par
l'impôt (action 138, étape 5). Ce script lit chez l'IPP les barèmes qui le
calculent, des revenus de 1960 à ceux de 2023, et les écrit, marche par
marche, dans ``data/reference/legislation/impot_revenu.yaml`` :

- le barème (``impot_revenu.bareme_ir_depuis_1945.bareme``) ;
- le quotient familial, son plafonnement, la décote et la réduction sous
  condition de revenus (``calcul_impot_revenu.plaf_qf``), le seuil de mise en
  recouvrement (``calcul_impot_revenu.recouvrement``) ;
- les abattements de 10 % des salaires et des pensions, celui de 20 % d'avant
  2006 (``calcul_revenus_imposables.deductions``), celui des personnes âgées ou
  invalides (``abat_rni.contribuable_age_invalide``) et ses deux compléments
  de 1978 (``abat_exceptionnel``) ;
- les majorations et minorations exceptionnelles
  (``contributions_exceptionnelles``), la réduction exceptionnelle de 2013
  (``calcul_reductions_impots.reduction_impot_exceptionnelle``) et la prime
  pour l'emploi (``credits_impots.ppe``).

LES CONVENTIONS DE L'IPP. Chaque barème est un CSV daté du 1er janvier de
l'ANNÉE DES REVENUS : sa ligne du 1er janvier 2023 est celle de la loi de
finances pour 2024. Chaque ligne est une PHOTOGRAPHIE : elle répète toutes les
valeurs en vigueur, et une cellule vide après une valeur dit qu'elle ne l'est
plus. Le script garde cette lecture : une marche ne porte que ce qui est en
vigueur, et une clé absente d'une marche n'est pas en vigueur à sa date.

LES MONNAIES. L'IPP écrit chaque montant dans sa monnaie : anciens francs
(« AFRF ») jusqu'aux revenus de 1958, francs (« FRF ») jusqu'à ceux de 2000,
euros ensuite. Le script NE CONVERTIT PAS : l'impôt d'une année en francs se
calcule en francs, arrondis compris, et chaque marche dit sa monnaie. Les
lignes en anciens francs, d'avant 1960, ne sont pas reprises ; le dépôt
commence aux revenus de 1960.

CE QUE L'IPP NE DIT PAS, OU DIT MAL, et que ce script complète, chaque fois
avec sa source (``origine`` de la marche) :

- les revenus de 2024 et de 2025 : le barème de 2024 et tout 2025 manquent à
  l'IPP. Ils sont lus dans les rédactions de l'article 197 du code général des
  impôts que les lois de finances pour 2025 et 2026 ont écrites, et dans
  celles des articles 83, 158 et 157 bis, par l'index LEGI de la DILA
  (``docs/veille_droit.md``) — ``origine: legi`` ;
- quatre erreurs : l'abattement des personnes âgées de 2024 vaut 2 796 €
  (article 157 bis, LEGIARTI000051765211), non 2 795 € ; la réduction
  complémentaire de la demi-part d'un invalide vaut 5 380 F, 5 410 F et
  4 260 F de 1998 à 2000 (article 197), non 4 336 F ; et la décote de 2000 est
  la différence entre 2 450 F et la MOITIÉ de l'impôt, un taux que l'IPP ne
  donne pas (``CORRECTIONS``) ;
- trois trous : la table des personnes âgées n'a pas de montant pour 1982,
  1983 et 1989. Ils sont calculés par la règle d'indexation que l'article
  157 bis écrit (« relevés chaque année dans la même proportion que la limite
  supérieure de la première tranche du barème », arrondis à la dizaine de
  francs supérieure, à la centaine pour les plafonds) ; celle-ci retrouve la
  valeur publiée de 1984 à partir de 1981 — ``origine: indexation`` ;
- le nombre de parts des enfants : l'IPP date de 1995 la part entière du
  troisième enfant, qui n'est que la date de la rédaction de l'article 194 que
  LEGI conserve. Ses propres notes la datent des revenus de 1980 (loi du
  30 décembre 1980), celle du cinquième des revenus de 1979 (loi du
  18 janvier 1980), et de 1986 la part entière de chaque enfant après le
  troisième (loi du 30 décembre 1986) — ``origine: note_ipp`` ;
- le seuil de mise en recouvrement avant 2002, que l'IPP ne porte pas : les
  rédactions de l'article 1657 du code (150 F pour les revenus de 1977,
  185 F à 320 F de 1979 à 1984, 440 F et 460 F en 1991 et 1992, 400 F de
  1993 à 2000, 61 € ensuite) ; 1978 et 1985 à 1990, que le code ne chiffre
  pas, par sa règle d'indexation, qui retrouve les valeurs publiées de 1979,
  de 1991 et de 1992 — ``origine: legi`` ou ``indexation`` ;
- la majoration de la prime pour l'emploi du premier enfant d'un parent
  isolé, le double de celle des autres enfants depuis la première rédaction
  de l'article 200 sexies (LEGIARTI000006303351), que l'IPP ne porte qu'à
  partir de 2007 ;
- la part du veuf ayant un enfant à charge, que l'IPP ne fait naître qu'en
  2008, et que la rédaction de l'article 194 de 1996 donne déjà (« Marié ou
  veuf ayant un enfant à charge = 2,5 ») : elle vaut dès 1960 ;
- la fin de la prime pour l'emploi, remplacée par la prime d'activité au
  1er janvier 2016 (note de l'IPP), que la photographie de 2016 ne dit pas,
  quelques cellules y restant pleines.

Ce qu'il écarte : la ligne de la décote datée de 1959 (7 000 F et 14 000 F),
que l'IPP ne commente pas et qui ne peut être une décote d'impôt — elle
effacerait tout impôt de 1960 inférieur à 7 000 F ; la décote commence donc
avec les revenus de 1961.

Ce qu'il ne fait pas. L'IPP est une transcription, non une source productrice :
la donnée plafonne à ``haute``. Il n'ancre pas chaque marche au Journal
officiel ; la référence que l'IPP cite est gardée, marche par marche, et un
test relit dans l'index LEGI, quand il est là, les valeurs que le script y a
lues.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import math
import sys
import urllib.request
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parents[2]
SORTIE = RACINE_DEPOT / "data" / "reference" / "legislation" / "impot_revenu.yaml"
RACINE = "https://baremes.ipp.eu/parameters/impot-sur-le-revenu"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Les revenus les plus anciens que le dépôt reprend : le barème de l'IPP passe
#: des anciens aux nouveaux francs en 1960, après six années sans barème.
PREMIERE_ANNEE = 1960

#: Chaque série : son nom dans la donnée, le paramètre de l'IPP, et ses
#: colonnes — le nom qu'elles prennent, la colonne de l'IPP.
SERIES: dict[str, tuple[str, dict[str, str]]] = {
    "quotient_familial": (
        "impot_revenu.calcul_impot_revenu.plaf_qf.quotient_familial",
        {"conjoint": "cas_general.conj", "veuf_avec_enfant": "cas_general.veuf",
         "parent_isole": "couple_ou_pers_a_charge.isol",
         "invalide": "couple_ou_pers_a_charge.inv1"}),
    "plafonds_quotient_familial": (
        "impot_revenu.calcul_impot_revenu.plaf_qf.plafond_avantages_procures_par_demi_part",
        {"general": "general", "parent_isole_premier_enfant": "celib_enf",
         "vivant_seul_ayant_eu_un_enfant": "celib",
         "reduction_complementaire_invalide": "reduc_postplafond",
         "reduction_complementaire_veuf": "reduc_postplafond_veuf"}),
    "decote": (
        "impot_revenu.calcul_impot_revenu.plaf_qf.decote",
        {"taux": "taux", "seuil": "seuil", "seuil_celibataire": "seuil_celib",
         "seuil_couple": "seuil_couple", "seuil_une_part": "seuil_1_part",
         "seuil_une_part_et_demie": "seuil_15_part",
         "seuil_1_faible_nombre_de_parts": "seuil_1_faible_nombre_part",
         "seuil_2_faible_nombre_de_parts": "seuil_2_faible_nombre_part",
         "nombre_de_parts_limite": "nombre_part_limite"}),
    "reduction_sous_condition_de_revenus": (
        "impot_revenu.calcul_impot_revenu.plaf_qf.reduction_ss_condition_revenus",
        {"taux": "taux", "seuil_bas": "plafond_rfr_celib", "seuil_haut": "plafond_rfr_couple",
         "majoration_par_demi_part": "majoration_plafond_par_demi_parts_supp"}),
    "recouvrement": (
        "impot_revenu.calcul_impot_revenu.recouvrement",
        {"seuil": "min_avant_credits_impots", "seuil_apres_credits": "min_apres_credits_impots"}),
    "deductions": (
        "impot_revenu.calcul_revenus_imposables.deductions",
        {"frais_professionnels_taux": "abatpro.taux",
         "frais_professionnels_minimum": "abatpro.min",
         "frais_professionnels_maximum": "abatpro.max",
         "pensions_taux": "abatpen.taux", "pensions_minimum": "abatpen.min",
         "pensions_maximum": "abatpen.max",
         "vingt_pour_cent_taux": "abat_supp.taux",
         "vingt_pour_cent_maximum": "abat_supp.max",
         "vingt_pour_cent_plafond": "abat_supp.salaire_plafond"}),
    "abattement_age_invalidite": (
        "impot_revenu.calcul_revenus_imposables.abat_rni.contribuable_age_invalide",
        {"abattement_plein": "0.amount", "seuil_plein": "1.threshold",
         "abattement_reduit": "1.amount", "seuil_reduit": "2.threshold"}),
    "abattement_exceptionnel_ages_invalides": (
        "impot_revenu.calcul_revenus_imposables.abat_exceptionnel.en_faveur_personnes_agees_invalides_2",
        {"abattement_plein": "abattement_1", "seuil_plein": "seuil_1_revenu_net_global",
         "abattement_reduit": "abattement_2", "seuil_reduit": "seuil_2_revenu_net_global"}),
    "abattement_exceptionnel_personnes_seules": (
        "impot_revenu.calcul_revenus_imposables.abat_exceptionnel.en_faveur_certains_contribuables_seuls_1",
        {"abattement": "abattement", "revenu_net_global_maximum": "maximum_revenu_net_global"}),
    "majorations_exceptionnelles": (
        "impot_revenu.contributions_exceptionnelles.majorations_exceptionnelles",
        {"seuil_revenu": "seuil_revenu", "seuil_1": "seuil_1", "seuil_2": "seuil_2",
         "seuil_3": "seuil_3_superieur", "taux_1": "taux_1", "taux_2": "taux_2",
         "taux_3": "taux_3_superieur"}),
    "minorations_exceptionnelles": (
        "impot_revenu.contributions_exceptionnelles.minorations_exceptionnelles",
        {"taux_1": "taux_1", "taux_3": "taux_3", "taux_5": "taux_5",
         "seuil_impot_1": "seuil_impot_1", "seuil_impot_2": "seuil_impot_2",
         "seuil_impot_3": "seuil_impot_3", "seuil_impot_4": "seuil_impot_4",
         "seuil_impot_5": "seuil_impot_5",
         "revenu_par_part_maximum": "seuil_superieur_revenu_imposable_par_part",
         "taux_formule": "formule_calcul_taux_en_impot",
         "formule_seuil_2": "formule_calcul_seuil_2",
         "formule_seuil_4": "formule_calcul_seuil_4"}),
    "reduction_exceptionnelle": (
        "impot_revenu.calcul_reductions_impots.reduction_impot_exceptionnelle",
        {"seuil": "seuil", "majoration_par_demi_part": "majoration_seuil",
         "montant": "montant_plafond"}),
    "prime_pour_l_emploi": (
        "impot_revenu.credits_impots.ppe",
        {"revenu_minimum": "seuils_revenu_activite.minimum",
         "revenu_taux_plein": "seuils_revenu_activite.pour_taux_plein_cas_general",
         "revenu_maximum": "seuils_revenu_activite.maximum_cas_general",
         "revenu_taux_plein_mono_emploi": "seuils_revenu_activite.pour_taux_plein_couples_mono_revenus",
         "revenu_maximum_mono_emploi": "seuils_revenu_activite.max_couples_mono_emploi_parents_isoles",
         "rfr_personne_seule": "seuils_rfr_eligibilite.personne_seule",
         "rfr_couple": "seuils_rfr_eligibilite.couple_marie_pacse",
         "rfr_par_demi_part": "seuils_rfr_eligibilite.increment_par_demi_part",
         "taux_entree": "taux.phase_in", "taux_sortie": "taux.phase_out_cas_general",
         "taux_sortie_mono_emploi": "taux.phase_out_couples_mono_emploi",
         "majoration_mono_emploi": "supplements.couples_mono_emploi",
         "majoration_parent_isole": "supplements.mono_pac",
         "majoration_par_personne_a_charge": "supplements.par_personne_charge",
         "montant_minimum": "montant_minimum"}),
}

#: Le barème, lu à part : ses colonnes sont des tranches.
BAREME = "impot_revenu.bareme_ir_depuis_1945.bareme"

#: Les mesures que la photographie de l'IPP fait durer au-delà de leur fin :
#: l'année de revenus où elles ne sont plus, et pourquoi.
FINS = {
    "prime_pour_l_emploi": (2016, "IPP, note : « À compter du 1er janvier 2016, la PPE "
                                  "est remplacée par la prime d'activité » "
                                  "(décrets n° 2015-1709 et 2015-1710)"),
}

#: Les lignes de l'IPP que le script ne reprend pas, et pourquoi (en-tête).
ECARTEES = {("decote", 1959)}

#: Les parts de chaque rang d'enfant à charge, que le tableau de l'IPP date
#: mal (voir l'en-tête) : à chaque marche, la part du premier, du deuxième…
#: enfant, la dernière valant pour tous les suivants.
PARTS_PAR_RANG_D_ENFANT = (
    (PREMIERE_ANNEE, (0.5,), "CGI, art. 194, I (IPP, table du quotient familial)"),
    (1979, (0.5, 0.5, 0.5, 0.5, 1.0),
     "Loi n° 80-30 du 18 janvier 1980 (LF pour 1980) : une part entière pour le "
     "cinquième enfant, sur les revenus de 1979 (IPP, note des plafonds de 1979)"),
    (1980, (0.5, 0.5, 1.0, 0.5, 1.0),
     "Loi n° 80-1094 du 30 décembre 1980 (LF pour 1981) : une part entière pour le "
     "troisième enfant, sur les revenus de 1980 (IPP, note des plafonds de 1979)"),
    (1986, (0.5, 0.5, 1.0),
     "Loi n° 86-1317 du 30 décembre 1986 (LF pour 1987) : une part entière pour "
     "chaque enfant après le troisième (IPP, note de la décote de 1986) ; CGI, "
     "art. 194, LEGIARTI000006308279 : « en augmentant d'une part par enfant à charge »"),
)

#: Ce que les lois de finances pour 2025 et 2026, et le code qu'elles ont
#: écrit, ajoutent à l'IPP. Une valeur par clé, telle que l'index LEGI la
#: donne ; ``tests/test_impot_revenu.py`` la relit dans l'index quand il est là.
LEGI_2024 = "CGI, art. 197, I, LEGIARTI000051212954 (loi n° 2025-127 du 14 février 2025, art. 2)"
LEGI_2025 = "CGI, art. 197, I, LEGIARTI000053542636 (loi n° 2026-103 du 19 février 2026, art. 4)"
COMPLEMENTS: dict[str, list[dict]] = {
    "bareme": [
        {"annee": 2024, "monnaie": "EUR", "seuils": [0, 11497, 29315, 83823, 180294],
         "taux": [0.0, 0.11, 0.30, 0.41, 0.45], "texte": LEGI_2024, "origine": "legi"},
        {"annee": 2025, "monnaie": "EUR", "seuils": [0, 11600, 29579, 84577, 181917],
         "taux": [0.0, 0.11, 0.30, 0.41, 0.45], "texte": LEGI_2025, "origine": "legi"},
    ],
    "plafonds_quotient_familial": [
        {"annee": 2024, "monnaie": "EUR", "general": 1791, "parent_isole_premier_enfant": 4224,
         "vivant_seul_ayant_eu_un_enfant": 1069, "reduction_complementaire_invalide": 1785,
         "reduction_complementaire_veuf": 1993, "texte": LEGI_2024, "origine": "legi"},
        {"annee": 2025, "monnaie": "EUR", "general": 1807, "parent_isole_premier_enfant": 4262,
         "vivant_seul_ayant_eu_un_enfant": 1079, "reduction_complementaire_invalide": 1801,
         "reduction_complementaire_veuf": 2011, "texte": LEGI_2025, "origine": "legi"},
    ],
    "decote": [
        {"annee": 2024, "monnaie": "EUR", "taux": 0.4525, "seuil_celibataire": 889,
         "seuil_couple": 1470, "texte": LEGI_2024, "origine": "legi"},
        {"annee": 2025, "monnaie": "EUR", "taux": 0.4525, "seuil_celibataire": 897,
         "seuil_couple": 1483, "texte": LEGI_2025, "origine": "legi"},
    ],
    "deductions": [
        {"annee": 2024, "monnaie": "EUR", "frais_professionnels_taux": 0.10,
         "frais_professionnels_minimum": 504, "frais_professionnels_maximum": 14426,
         "pensions_taux": 0.10, "pensions_minimum": 450, "pensions_maximum": 4399,
         "texte": "CGI, art. 83, 3°, LEGIARTI000051765287, et art. 158, 5, a, "
                  "LEGIARTI000051765203 (loi n° 2025-127 du 14 février 2025, art. 2)",
         "origine": "legi"},
        {"annee": 2025, "monnaie": "EUR", "frais_professionnels_taux": 0.10,
         "frais_professionnels_minimum": 509, "frais_professionnels_maximum": 14555,
         "pensions_taux": 0.10, "pensions_minimum": 454, "pensions_maximum": 4439,
         "texte": "CGI, art. 83, 3°, LEGIARTI000054373766, et art. 158, 5, a, "
                  "LEGIARTI000054373673 (loi n° 2026-103 du 19 février 2026, art. 4)",
         "origine": "legi"},
    ],
    "abattement_age_invalidite": [
        {"annee": 2024, "monnaie": "EUR", "abattement_plein": 2796, "seuil_plein": 17510,
         "abattement_reduit": 1398, "seuil_reduit": 28170,
         "texte": "CGI, art. 157 bis, LEGIARTI000051765211 (loi n° 2025-127, art. 2) : "
                  "2 796 €, et non les 2 795 € de l'IPP", "origine": "legi"},
        {"annee": 2025, "monnaie": "EUR", "abattement_plein": 2822, "seuil_plein": 17670,
         "abattement_reduit": 1411, "seuil_reduit": 28430,
         "texte": "CGI, art. 157 bis, LEGIARTI000054373677 (loi n° 2026-103, art. 4)",
         "origine": "legi"},
    ],
}

#: Les valeurs de l'IPP que le code dément, corrigées clé par clé : la série,
#: l'année, les valeurs lues, et la rédaction qui les porte.
CORRECTIONS: dict[tuple[str, int], tuple[dict, str]] = {
    ("plafonds_quotient_familial", 1998): (
        {"reduction_complementaire_invalide": 5380},
        "CGI, art. 197, I, 2, LEGIARTI000006308341 : « 5 380 F pour chacune de ces demi-parts » ; "
        "l'IPP porte 4 336 F de 1998 à 2000"),
    ("plafonds_quotient_familial", 1999): (
        {"reduction_complementaire_invalide": 5410},
        "CGI, art. 197, I, 2, LEGIARTI000006308342 : « 5 410 F pour chacune de ces demi-parts »"),
    ("plafonds_quotient_familial", 2000): (
        {"reduction_complementaire_invalide": 4260},
        "CGI, art. 197, I, 2, LEGIARTI000006308344 : « 4 260 F pour chacune de ces demi-parts »"),
    ("decote", 2000): (
        {"taux": 0.5},
        "CGI, art. 197, I, 4, LEGIARTI000006308344 : « la différence entre 2 450 F et la moitié "
        "de son montant » ; l'IPP n'en donne pas le taux"),
}

#: Le seuil de mise en recouvrement avant que l'IPP ne le porte (2002), lu dans
#: les rédactions de l'article 1657 du code que l'index LEGI conserve ; une
#: année que le code ne chiffre pas suit sa règle d'indexation (voir
#: :func:`_recouvrement_avant_2002`).
RECOUVREMENT_LU = (
    (1970, 100, None, "CGI, art. 1657, 2, LEGIARTI000049223975 : « les cotisations d'un "
                      "montant inférieur à 100 francs ne sont pas mises en recouvrement »"),
    (1977, 150, None, "CGI, art. 1657, 1 bis, LEGIARTI000006312651, note (1) : 150 F pour "
                      "les revenus de 1977"),
    (1979, 185, None, "LEGIARTI000006312651, note (2)"),
    (1980, 210, None, "LEGIARTI000006312651, note (2)"),
    (1981, 240, None, "LEGIARTI000006312651, note (2)"),
    (1982, 270, None, "LEGIARTI000006312651, note (2)"),
    (1983, 295, None, "LEGIARTI000006312651, note (2)"),
    (1984, 320, None, "LEGIARTI000006312651, note (2)"),
    (1991, 440, 80, "CGI, art. 1657, LEGIARTI000006312652, note (1) ; 80 F après crédits (2.)"),
    (1992, 460, 80, "LEGIARTI000006312652, note (1)"),
    (1993, 400, 80, "LEGIARTI000006312652, note (1) : loi n° 93-1352, art. 2 V"),
    (2001, 61, 12, "CGI, art. 1657, 1 bis et 2, LEGIARTI000006312658 : 61 € et 12 € ; la "
                   "loi de finances pour 2001 a rendu 400 F aux revenus de 2000, "
                   "LEGIARTI000006312657"),
)


def _telecharger(parametre: str) -> list[dict[str, str]]:
    demande = urllib.request.Request(f"{RACINE}/{parametre}/csv", headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=180) as reponse:
        return list(csv.DictReader(io.StringIO(reponse.read().decode("utf-8"))))


def _valeur(brut: str) -> tuple[float | None, str | None]:
    """« 6,55 % » -> (0.0655, "%") ; « 1 439 € » -> (1439, "EUR") ;
    « 8 157 FRF » -> (8157, "FRF") ; « 0,5 parts » -> (0.5, None). Une cellule
    vide rend ``(None, None)``. Les montants restent dans leur monnaie."""
    texte = (brut or "").replace(" ", " ").replace("\xa0", " ").strip()
    if not texte:
        return None, None
    unite = None
    for suffixe, nom in (("AFRF", "AFRF"), ("FRF", "FRF"), ("€", "EUR"), ("%", "%"),
                         ("parts", None)):
        if texte.endswith(suffixe):
            unite, texte = nom, texte[: -len(suffixe)]
            break
    nombre = float(texte.replace(" ", "").replace(",", "."))
    if unite == "%":
        return round(nombre / 100.0, 8), "%"
    return (int(nombre) if nombre == int(nombre) else nombre), unite


def _annee(brut: str) -> int:
    return int(brut.split("/")[2])


def _reference(ligne: dict[str, str]) -> str:
    reference = " ".join((ligne.get("reference") or "").split())
    return reference.split(";")[0].strip() or "IPP, sans référence"


def _monnaie(unites: set[str | None]) -> str | None:
    monnaies = unites & {"AFRF", "FRF", "EUR"}
    if len(monnaies) > 1:
        raise ValueError(f"une marche en plusieurs monnaies : {sorted(monnaies)}")
    return next(iter(monnaies), None)


def marches(lignes: list[dict[str, str]], colonnes: dict[str, str],
            nom: str = "") -> list[dict]:
    """Les marches d'une série, de la plus ancienne à la plus récente, à partir
    des revenus de :data:`PREMIERE_ANNEE`. Chaque ligne est une photographie :
    une marche ne porte que les valeurs en vigueur, et une marche identique à
    la précédente ne s'écrit pas. Deux lignes de la même année : la plus tardive
    l'emporte (l'IPP en a une au 1er juillet 1979)."""
    par_annee: dict[int, dict] = {}
    for ligne in sorted(lignes, key=lambda l: tuple(reversed(l["date"].split("/")))):
        if (nom, _annee(ligne["date"])) in ECARTEES:
            continue
        valeurs, unites = {}, set()
        for cle, colonne in colonnes.items():
            nombre, unite = _valeur(ligne.get(colonne, ""))
            if nombre is not None:
                valeurs[cle] = nombre
                unites.add(unite)
        marche = {"annee": _annee(ligne["date"])}
        monnaie = _monnaie(unites)
        if monnaie:
            marche["monnaie"] = monnaie
        marche.update(valeurs)
        marche["texte"] = _reference(ligne)
        note = " ".join((ligne.get("notes") or "").split())
        if note:
            marche["note"] = note
        par_annee[marche["annee"]] = marche
    lues: list[dict] = []
    avant = [m for a, m in sorted(par_annee.items()) if a < PREMIERE_ANNEE]
    if (avant and avant[-1].get("monnaie") != "AFRF" and len(avant[-1]) > 2
            and PREMIERE_ANNEE not in par_annee):
        # La marche en vigueur au 1er janvier 1960, si elle ne porte aucun
        # montant en anciens francs : elle vaut pour les revenus de 1960.
        lues.append({**avant[-1], "annee": PREMIERE_ANNEE})
    for annee, marche in sorted(par_annee.items()):
        if annee < PREMIERE_ANNEE:
            continue
        if marche.get("monnaie") == "AFRF":
            raise ValueError(f"un montant en anciens francs après 1960 : {marche}")
        lues.append(marche)
    gardees: list[dict] = []
    for marche in lues:
        valeurs = {k: v for k, v in marche.items() if k not in ("annee", "texte", "note", "origine")}
        if gardees:
            precedentes = {k: v for k, v in gardees[-1].items()
                           if k not in ("annee", "texte", "note", "origine")}
            if valeurs == precedentes:
                continue
        if not gardees and not {k for k in valeurs if k != "monnaie"}:
            continue
        gardees.append(marche)
    return gardees


def marches_du_bareme(lignes: list[dict[str, str]]) -> list[dict]:
    """Le barème : à chaque marche, les seuils de ses tranches et leurs taux."""
    lues = []
    for ligne in sorted(lignes, key=lambda l: tuple(reversed(l["date"].split("/")))):
        seuils, taux, unites = [], [], set()
        for rang in range(20):
            seuil, unite = _valeur(ligne.get(f"{rang}.threshold", ""))
            valeur, _ = _valeur(ligne.get(f"{rang}.rate", ""))
            if seuil is None:
                continue
            seuils.append(seuil)
            taux.append(valeur or 0.0)
            unites.add(unite)
        annee = _annee(ligne["date"])
        if annee < PREMIERE_ANNEE or not seuils:
            continue
        marche = {"annee": annee, "monnaie": _monnaie(unites), "seuils": seuils,
                  "taux": [float(t) for t in taux], "texte": _reference(ligne)}
        note = " ".join((ligne.get("notes") or "").split())
        if note:
            marche["note"] = note
        lues.append(marche)
    return lues


def _arrondi_superieur(valeur: float, pas: int) -> int:
    return int(math.ceil(round(valeur / pas, 9)) * pas)


def _limite_premiere_tranche(bareme: list[dict], annee: int) -> float:
    """La limite supérieure de la tranche à taux nul du barème de l'année."""
    marche = [m for m in bareme if m["annee"] <= annee][-1]
    return float(marche["seuils"][1])


def _limite_premiere_tranche_imposee(bareme: list[dict], annee: int) -> float:
    """La limite supérieure de la première tranche imposée (5 % de 1974 à 1992)."""
    marche = [m for m in bareme if m["annee"] <= annee][-1]
    return float(marche["seuils"][2])


def _indexer_age_invalidite(serie: list[dict], bareme: list[dict]) -> list[dict]:
    """Comble les années sans montant de la table des personnes âgées par la
    règle de l'article 157 bis (LEGIARTI000006307952 : « relevés chaque année
    dans la même proportion que la limite supérieure de la première tranche
    du barème ; arrondis à la dizaine de francs supérieure en ce qui concerne
    les abattements et à la centaine de francs supérieure en ce qui concerne
    les plafonds »). Partie de 1981, elle retrouve la valeur publiée de 1984."""
    par_annee = {m["annee"]: m for m in serie}
    sortie = []
    for marche in serie:
        sortie.append(marche)
    trous = [a for a, m in par_annee.items() if "abattement_plein" not in m]
    for annee in sorted(set(trous) | ({1983} if 1982 in trous else set())):
        precedente = [m for m in sortie if m["annee"] < annee and "abattement_plein" in m][-1]
        rapport = (_limite_premiere_tranche(bareme, annee)
                   / _limite_premiere_tranche(bareme, precedente["annee"]))
        calculee = {
            "annee": annee, "monnaie": precedente["monnaie"],
            "abattement_plein": _arrondi_superieur(precedente["abattement_plein"] * rapport, 10),
            "seuil_plein": _arrondi_superieur(precedente["seuil_plein"] * rapport, 100),
            "abattement_reduit": _arrondi_superieur(precedente["abattement_reduit"] * rapport, 10),
            "seuil_reduit": _arrondi_superieur(precedente["seuil_reduit"] * rapport, 100),
            "texte": ("CGI, art. 157 bis, LEGIARTI000006307952 : règle d'indexation "
                      f"appliquée aux montants de {precedente['annee']} ; l'IPP n'en a pas"),
            "origine": "indexation",
        }
        sortie = [m for m in sortie if m["annee"] != annee] + [calculee]
        sortie.sort(key=lambda m: m["annee"])
    return sortie


def _recouvrement_avant_2002(bareme: list[dict]) -> list[dict]:
    """Le seuil de mise en recouvrement de 1970 à 2001. Les années que le code
    ne chiffre pas suivent sa règle : « relevée chaque année dans la même
    proportion que la première tranche du barème » (LEGIARTI000006312651),
    la première tranche imposée, arrondie aux 5 F supérieurs jusqu'en 1984 et
    aux 10 F ensuite : ainsi se retrouvent les valeurs publiées de 1979 (185 F),
    de 1991 (440 F) et de 1992 (460 F)."""
    lus = {annee: (seuil, apres, texte) for annee, seuil, apres, texte in RECOUVREMENT_LU}
    sortie = []
    for annee in range(1970, 2002):
        if annee in lus:
            seuil, apres, texte = lus[annee]
            marche = {"annee": annee, "monnaie": "EUR" if annee >= 2001 else "FRF",
                      "seuil": seuil, "texte": texte, "origine": "legi"}
            if apres is not None:
                marche["seuil_apres_credits"] = apres
            sortie.append(marche)
        elif annee in (1978,) or 1985 <= annee <= 1990:
            precedente = sortie[-1]
            rapport = (_limite_premiere_tranche_imposee(bareme, annee)
                       / _limite_premiere_tranche_imposee(bareme, annee - 1))
            pas = 5 if annee < 1985 else 10
            sortie.append({"annee": annee, "monnaie": "FRF",
                           "seuil": _arrondi_superieur(precedente["seuil"] * rapport, pas),
                           "texte": ("CGI, art. 1657, 1 bis, LEGIARTI000006312651 : règle "
                                     "d'indexation, le code ne chiffrant pas l'année"),
                           "origine": "indexation"})
    return sortie


def corriger(series: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """Ajoute à l'IPP ce que l'en-tête dit qu'il ne porte pas, ou porte mal."""
    bareme = series["bareme"]
    for (nom, annee), (valeurs, texte) in CORRECTIONS.items():
        marche = next(m for m in series[nom] if m["annee"] == annee)
        marche.update(valeurs)
        marche["origine"] = "legi"
        marche["texte"] = f"{marche['texte']} ; {texte}"
    for nom, complements in COMPLEMENTS.items():
        annees = {m["annee"] for m in complements}
        series[nom] = sorted([m for m in series[nom] if m["annee"] not in annees] + complements,
                             key=lambda m: m["annee"])
    series["abattement_age_invalidite"] = _indexer_age_invalidite(
        series["abattement_age_invalidite"], bareme)
    series["recouvrement"] = _recouvrement_avant_2002(bareme) + [
        m for m in series["recouvrement"] if m["annee"] >= 2002]
    for nom, (annee, texte) in FINS.items():
        series[nom] = [m for m in series[nom] if m["annee"] < annee] + [
            {"annee": annee, "supprimee": True, "texte": texte}]
    parent_isole = ("CGI, art. 200 sexies, II, B, depuis sa première rédaction "
                    "(LEGIARTI000006303351 : « la majoration de 200 F est portée à 400 F pour le "
                    "premier enfant à charge ») ; l'IPP ne la porte qu'à partir de 2007")
    series["prime_pour_l_emploi"] = [
        marche if marche.get("supprimee") or "majoration_parent_isole" in marche else
        {**marche, "majoration_parent_isole": 2 * marche["majoration_par_personne_a_charge"],
         "origine": "legi", "texte": f"{marche['texte']} ; {parent_isole}"}
        for marche in series["prime_pour_l_emploi"]]
    veuf = ("CGI, art. 194, I, LEGIARTI000006308279 : « Marié ou veuf ayant un enfant à "
            "charge = 2,5 » ; l'IPP ne la porte qu'à partir de 2008")
    series["quotient_familial"] = [
        marche if "veuf_avec_enfant" in marche else
        {**marche, "veuf_avec_enfant": 1, "origine": "legi",
         "texte": f"{marche['texte']} ; {veuf}"}
        for marche in series["quotient_familial"]]
    series["parts_par_rang_d_enfant"] = [
        {"annee": annee, "parts": list(parts), "texte": texte, "origine": "note_ipp"}
        for annee, parts, texte in PARTS_PAR_RANG_D_ENFANT]
    return series


def _scalaire(valeur) -> str:
    if isinstance(valeur, bool):
        return "true" if valeur else "false"
    if isinstance(valeur, (int, float)):
        return repr(float(valeur)) if isinstance(valeur, float) else str(valeur)
    if isinstance(valeur, list):
        return "[" + ", ".join(_scalaire(v) for v in valeur) + "]"
    texte = str(valeur).replace("\\", "/").replace('"', "'")
    return f'"{texte}"'


def _yaml(marche: dict) -> str:
    ordre = ["annee", "monnaie"] + [k for k in marche if k not in
                                   ("annee", "monnaie", "texte", "note", "origine")]
    ordre += [k for k in ("origine", "texte", "note") if k in marche]
    return "    - {" + ", ".join(f"{cle}: {_scalaire(marche[cle])}" for cle in ordre
                               if cle in marche) + "}"


ENTETE = """\
# L'impôt sur le revenu d'un foyer, de son barème à ses corrections, marche par marche
# ----------------------------------------------------------------------------------
# source_id: ipp_impot_revenu
#
# ÉCRIT PAR `scripts/fetch/ipp_impot_revenu.py`, jamais à la main : les barèmes
# de l'Institut des politiques publiques, lus le {lu_le}, chacun avec la
# référence que l'IPP cite pour sa marche, et ce que le script y ajoute, chaque
# fois avec sa source (`origine`) : `legi` pour une valeur lue dans une
# rédaction du code général des impôts que l'index LEGI de la DILA conserve,
# `indexation` pour une année que le code ne chiffre pas, calculée par la règle
# qu'il écrit, `note_ipp` pour une règle que seules les notes de l'IPP datent.
# Une transcription, non une source productrice : `haute` au plus
# (data/sources.yaml, `ipp_impot_revenu`).
#
# QUI LE LIT. `retraite_notionnelle/donnees/impot_revenu.py`, qui rend les
# paramètres d'une année de revenus, et les projette au-delà de la dernière ;
# `retraite_notionnelle/impot_revenu.py`, qui calcule l'impôt d'un foyer et son
# revenu fiscal de référence (action 138, étape 5). Rien d'autre encore.
#
# LES CONVENTIONS. Chaque marche vaut pour les revenus de son `annee` et des
# suivantes, jusqu'à la marche d'après ; elle porte tout ce qui est en vigueur,
# et une clé absente n'est pas en vigueur — un maximum absent n'est pas un
# maximum nul, c'est l'absence de maximum. Un taux s'entend en part de son
# assiette, un montant dans la `monnaie` de sa marche, francs jusqu'aux revenus
# de 2000, euros ensuite : le dépôt calcule l'impôt d'une année dans sa monnaie.
#
# LES SÉRIES.
#   bareme : les seuils des tranches, par part, et leurs taux.
#   quotient_familial : la part du conjoint, celle du veuf ayant un enfant à
#     charge, la demi-part du parent isolé (case T) et de l'invalide.
#   parts_par_rang_d_enfant : la part du premier enfant à charge, du deuxième…,
#     la dernière valant pour les suivants.
#   plafonds_quotient_familial : l'avantage maximal d'une demi-part (`general`),
#     de la part du premier enfant d'un parent isolé, de la demi-part de qui vit
#     seul et a eu un enfant (case L, que le dépôt ne calcule pas) ; les
#     réductions complémentaires de l'invalide et du veuf.
#   decote : son taux et ses seuils, dont le sens a changé six fois (le module
#     dit lequel vaut à chaque époque).
#   reduction_sous_condition_de_revenus : de 2016 à 2019.
#   recouvrement : le seuil de mise en recouvrement, avant et après crédits.
#   deductions : les 10 % des salaires et des pensions, les 20 % d'avant 2006.
#   abattement_age_invalidite : celui de l'article 157 bis, plein sous le
#     premier seuil de revenu net global, réduit sous le second.
#   abattement_exceptionnel_* : les deux compléments de 1978.
#   majorations_exceptionnelles, minorations_exceptionnelles : leurs seuils et
#     leurs taux, et la note de l'IPP qui dit comment ils s'appliquent.
#   reduction_exceptionnelle : celle des revenus de 2013.
#   prime_pour_l_emploi : de 2000 à 2015.
"""

ORDRE = ("bareme", "quotient_familial", "parts_par_rang_d_enfant",
         "plafonds_quotient_familial", "decote", "reduction_sous_condition_de_revenus",
         "recouvrement", "deductions", "abattement_age_invalidite",
         "abattement_exceptionnel_ages_invalides", "abattement_exceptionnel_personnes_seules",
         "majorations_exceptionnelles", "minorations_exceptionnelles",
         "reduction_exceptionnelle", "prime_pour_l_emploi")


def ecrire(series: dict[str, list[dict]], lu_le: str) -> str:
    lignes = [ENTETE.format(lu_le=lu_le).rstrip("\n"), f'lu_le: "{lu_le}"', "fiabilite: haute",
              f"premiere_annee: {PREMIERE_ANNEE}", "", "series:"]
    for nom in ORDRE:
        lignes.append(f"  {nom}:")
        lignes += [_yaml(marche) for marche in series[nom]]
    return "\n".join(lignes) + "\n"


def lire() -> dict[str, list[dict]]:
    series = {"bareme": marches_du_bareme(_telecharger(BAREME))}
    telecharges: dict[str, list[dict[str, str]]] = {}
    for nom, (parametre, colonnes) in SERIES.items():
        if parametre not in telecharges:
            telecharges[parametre] = _telecharger(parametre)
        series[nom] = marches(telecharges[parametre], colonnes, nom)
    return corriger(series)


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--lister", action="store_true", help="imprime sans écrire")
    arguments = analyseur.parse_args(argv)
    texte = ecrire(lire(), dt.date.today().isoformat())
    if arguments.lister:
        print(texte)
        return 0
    SORTIE.write_text(texte, encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE_DEPOT)} écrit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
