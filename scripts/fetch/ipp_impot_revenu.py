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
- la fin de la prime pour l'emploi, aux revenus de 2014 : la loi de finances
  rectificative pour 2014 (art. 28) abroge l'article 200 sexies dès
  l'imposition des revenus de 2015 (BOI-IR-RICI-310-10-30-20150515), où la
  note de l'IPP la fait durer jusqu'à la prime d'activité du 1er janvier
  2016, et où sa photographie de 2016 garde quelques cellules pleines ;
- la limite d'exonération (``exo_ir`` de l'IPP, de 1977 à 2013 : l'article 5,
  2° bis, du code) avant 1977 : les lois de finances pour 1974 à 1977 en
  fixent une pour qui vit « principalement de traitements, salaires et
  pensions », une autre pour les autres ; et ses trois années sans montant
  (1982, 1983, 1989), par la règle d'indexation de la loi de finances pour
  1982 (art. 12, III, 3), qui retrouve les valeurs publiées de 1984 et de
  1990 — ``origine: loi`` ou ``indexation`` ;
- ce que les lois de finances pour 1974 à 1981 écrivent autrement que l'IPP,
  lues au texte définitif que le Sénat a adopté (``LOIS_DE_FINANCES``) : trois
  seuils du barème (5 550 F et 22 950 F en 1974, 37 940 F en 1980) ; les
  pensions, sans l'abattement de 10 % que la loi de finances pour 1978
  institue ; l'abattement des personnes âgées de 1973 à 1976, que l'IPP ne
  fait naître qu'en 1977 ; le minimum des frais professionnels de 1975 et
  de 1976 ; la limite des 20 % de 1975 et de 1976 (350 000 F, non
  340 000 F) ; les parts des enfants de 1979 et de 1980 ; le minimum de
  200 F de la majoration de 1980 ; le seuil de recouvrement de 1978, que la
  loi chiffre — ``origine: loi`` ;
- ce que les lois de finances pour 1970 à 1973 écrivent des revenus de 1969
  à 1972 (``LOIS_DE_FINANCES``, et, pour celle de 1972, que le Sénat a
  rejetée, le texte voté par l'Assemblée nationale que reproduit le rapport
  général de sa commission des finances, ``LOI_DE_FINANCES_POUR_1972``) : le
  barème, dont l'IPP porte, jusqu'en 1971, les taux diminués des points que
  la réduction de l'article 198 rend aux seuls salaires et pensions, et 25 %
  au lieu de 20 % à sa quatrième tranche ; cette réduction, et celle des
  contribuables âgés ; les limites de l'exonération et de la décote de
  l'article 198 ter ; les minorations et les majorations de 1969, par
  paliers ; le minimum des frais professionnels de 1970 à 1974 ; la déduction
  de 500 F des personnes âgées et l'exonération des salariés de 1972 —
  ``origine: loi``, ou ``rapport`` pour ce que seul le rapport chiffre ;
- ce que la loi n° 59-1472 du 28 décembre 1959 et les lois de finances pour
  1961 à 1969 écrivent des revenus de 1960 à 1968 (``TEXTES_DU_SENAT``, et,
  pour une loi que le Sénat a rejetée, le texte de l'Assemblée nationale que
  reproduit le rapport de sa commission des finances, ``RAPPORTS_DES_ANNEES_1960``) :
  le barème, aux taux de la loi et non des salariés, et 20 % au lieu de 25 %
  à sa quatrième tranche ; la réduction de 5 % des salaires et des pensions ;
  la décote de l'article 198 ter, par part, et ses limites pour le foyer et
  pour les âgés ; le demi-décime de 1962, par part ; les réductions de 1966 et
  de 1967, par tranche de revenu ; la majoration de 1967 et ses décotes ; la
  table de 1968 ;
- la taxe complémentaire, que l'IPP ne porte pas, de sa création par la loi
  n° 59-1472 à sa suppression par la loi de finances pour 1970
  (``TAXE_COMPLEMENTAIRE``) : ses taux, celui des artisans, ses abattements à
  la base — ``origine: loi``, ou ``rapport`` pour le taux de 1961, que la
  loi de finances pour 1962 écrit dans un texte définitif qui n'est pas lu ;
- l'exonération de l'article 5, 2°, que l'IPP ne porte pas
  (``MINIMUM_GARANTI``) : le montant annuel du minimum garanti, sous lequel
  qui vit principalement de salaires, de pensions et de rentes viagères n'est
  pas imposé, que chiffrent, pour 1971, le rapport général du Sénat sur la loi
  de finances pour 1973, de 1993 à 1998 la documentation de base 5 B 131, de
  1999 à 2010 l'instruction qui commente chaque année les limites
  d'exonération, et les notes du code pour 2000 et 2001 — ``origine:
  rapport``, ``doctrine`` ou ``legi`` ; les autres années de 1960 à 2013, une
  marche sans montant.

Ce qu'il écarte (``ECARTEES``) : la ligne de la décote datée de 1959 (7 000 F
et 14 000 F), en anciens francs que l'IPP écrit en francs — la loi n° 59-1472
dit « 7.000 francs par part entière de revenu » et 14 000 francs par part,
70 F et 140 F, que la marche de 1960 reprend ; celle de 1962 (80 F et 240 F),
que la loi de finances pour 1965 ne fixe que pour les revenus de 1964.

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
    "exoneration": (
        "impot_revenu.calcul_revenus_imposables.exo_ir",
        {"limite": "conditions_ressources_exoneration_ir.moins_de_65_ans",
         "limite_plus_de_65_ans": "conditions_ressources_exoneration_ir.plus_de_65_ans"}),
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
    "prime_pour_l_emploi": (2015, "BOI-IR-RICI-310-10-30-20150515 : ses commentaires « ne "
                                  "trouvent plus à s'appliquer à compter de l'imposition des "
                                  "revenus de 2015, compte tenu des dispositions de l'article "
                                  "28 de la loi n° 2014-1655 du 29 décembre 2014 de finances "
                                  "rectificative pour 2014 qui abroge l'article 200 sexies » ; "
                                  "sa dernière rédaction finit le 30 décembre 2014 "
                                  "(LEGIARTI000029042107) ; l'IPP la fait durer jusqu'au 1er "
                                  "janvier 2016"),
}

#: Les lignes de l'IPP que le script ne reprend pas, et pourquoi (en-tête).
ECARTEES = {
    ("decote", 1959): "7 000 et 14 000 anciens francs par part, écrits en francs",
    ("decote", 1962): "80 F et 240 F, que la loi n° 64-1279 (art. 2, II) ne fixe qu'en 1964",
}

#: Les parts de chaque rang d'enfant à charge, que le tableau de l'IPP date
#: mal (voir l'en-tête) : à chaque marche, la part du premier, du deuxième…
#: enfant, la dernière valant pour tous les suivants ; le texte, et son origine.
PARTS_PAR_RANG_D_ENFANT = (
    (PREMIERE_ANNEE, (0.5,), "CGI, art. 194, I (IPP, table du quotient familial)", "note_ipp"),
    (1979, (0.5, 0.5, 0.5, 0.5, 1.0, 0.5),
     "Loi n° 80-30 du 18 janvier 1980 (LF pour 1980), art. 4, I, texte définitif adopté par "
     "le Sénat le 17 janvier 1980 : « marié ou veuf ayant cinq enfants à charge 5 [...] et "
     "ainsi de suite, en augmentant d'une demi-part par enfant à charge » : une part "
     "entière pour le cinquième enfant seul, sur les revenus de 1979", "loi"),
    (1980, (0.5, 0.5, 1.0, 0.5),
     "Loi n° 80-1094 du 30 décembre 1980 (LF pour 1981), art. 3, I, texte définitif adopté "
     "par le Sénat : « Les contribuables qui ont au moins trois enfants à charge "
     "bénéficient d'une demi-part supplémentaire de quotient familial. Cette disposition se "
     "substitue à l'article 4-1 de la loi de finances pour 1980 », sur les revenus de 1980",
     "loi"),
    (1986, (0.5, 0.5, 1.0),
     "Loi n° 86-1317 du 30 décembre 1986 (LF pour 1987) : une part entière pour "
     "chaque enfant après le troisième (IPP, note de la décote de 1986) ; CGI, "
     "art. 194, LEGIARTI000006308279 : « en augmentant d'une part par enfant à charge »",
     "note_ipp"),
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
#: l'année, les valeurs lues, le texte qui les porte et son origine — `legi`,
#: une rédaction du code que l'index LEGI conserve ; `doctrine`, une
#: publication de l'administration, quand aucun des deux index n'a la loi de
#: finances de l'année.
CORRECTIONS: dict[tuple[str, int], tuple[dict, str, str]] = {
    ("bareme", 1994): (
        {"seuils": [0, 22210, 48570, 85480, 138410, 225210, 277730]},
        "DB 5 B 321 du 23 juin 2000, annexe I, « revenus de l'année 1994 (loi de finances pour "
        "1995 n° 94-1162 du 29 décembre 1994) », image db5b321.057 : « 22 210 et 48 570 [...] "
        "48 570 et 85 480 » ; l'IPP porte 48 750 F",
        "doctrine"),
    ("abattement_age_invalidite", 1993): (
        {"seuil_plein": 57500},
        "DB 5 B 25 du 1er septembre 1999, image db5b25.025 : « 1993 [...] R ≤ 57 500 [...] "
        "9 300 » ; l'IPP porte 57 000 F",
        "doctrine"),
    ("plafonds_quotient_familial", 1998): (
        {"reduction_complementaire_invalide": 5380},
        "CGI, art. 197, I, 2, LEGIARTI000006308341 : « 5 380 F pour chacune de ces demi-parts » ; "
        "l'IPP porte 4 336 F de 1998 à 2000",
        "legi"),
    ("plafonds_quotient_familial", 1999): (
        {"reduction_complementaire_invalide": 5410},
        "CGI, art. 197, I, 2, LEGIARTI000006308342 : « 5 410 F pour chacune de ces demi-parts »",
        "legi"),
    ("plafonds_quotient_familial", 2000): (
        {"reduction_complementaire_invalide": 4260},
        "CGI, art. 197, I, 2, LEGIARTI000006308344 : « 4 260 F pour chacune de ces demi-parts »",
        "legi"),
    ("plafonds_quotient_familial", 2009): (
        {"reduction_complementaire_invalide": 651},
        "CGI, art. 197, I, 2, LEGIARTI000021625085 : « une réduction d'impôt égale à 651 euros "
        "pour chacune de ces demi-parts » ; l'IPP porte 661 €, le montant des revenus de 2010",
        "legi"),
    ("decote", 2000): (
        {"taux": 0.5},
        "CGI, art. 197, I, 4, LEGIARTI000006308344 : « la différence entre 2 450 F et la moitié "
        "de son montant » ; l'IPP n'en donne pas le taux",
        "legi"),
    ("prime_pour_l_emploi", 2005): (
        {"taux_entree": 0.06, "taux_sortie": 0.15},
        "CGI, art. 200 sexies, I, A, 1°, LEGIARTI000006303356 : « 4,6 % (1) 6,0 % (2) 6,8 % (3) "
        "[...] 11,5 % (1) 15,0 % (2) 17,0 % (3) [...] (2) applicable aux revenus 2005 » ; l'IPP "
        "porte aux revenus de 2005 les taux que la loi de finances pour 2006 donnait à ceux de "
        "2006",
        "legi"),
}

#: Les lois de finances pour 1970 à 1981, sauf celle de 1972, lues au texte
#: définitif que le Sénat a adopté et publie : pour l'année des revenus
#: qu'elle impose, son intitulé, la date de ce texte et son fichier sous
#: senat.fr/leg/. L'index du JORF n'en a que la notice ; l'index LEGI, de
#: quelques articles, une rédaction consolidée, qui peut porter les montants
#: d'une loi postérieure (son article 12 de la loi de finances pour 1982 porte
#: la décote de 1982).
LOIS_DE_FINANCES = {
    1969: ("Loi n° 69-1161 du 24 décembre 1969 (LF pour 1970)", "16 décembre 1969",
           "1969-1970/ta1969_1970_0055.pdf"),
    1970: ("Loi n° 70-1199 du 21 décembre 1970 (LF pour 1971)", "9 décembre 1970",
           "1970-1971/ta1970_1971_0028.pdf"),
    1972: ("Loi n° 72-1121 du 20 décembre 1972 (LF pour 1973)", "15 décembre 1972",
           "1972-1973/ta1972_1973_0048.pdf"),
    1973: ("Loi n° 73-1150 du 27 décembre 1973 (LF pour 1974)", "18 décembre 1973",
           "1973-1974/ta1973_1974_0031.pdf"),
    1974: ("Loi n° 74-1129 du 30 décembre 1974 (LF pour 1975)", "19 décembre 1974",
           "1974-1975/ta1974_1975_0067.pdf"),
    1975: ("Loi n° 75-1278 du 30 décembre 1975 (LF pour 1976)", "17 décembre 1975",
           "1975-1976/ta1975_1976_0056.pdf"),
    1976: ("Loi n° 76-1232 du 29 décembre 1976 (LF pour 1977)", "16 décembre 1976",
           "1976-1977/ta1976_1977_0048.pdf"),
    1977: ("Loi n° 77-1467 du 30 décembre 1977 (LF pour 1978)", "16 décembre 1977",
           "1977-1978/ta1977_1978_0053.pdf"),
    1978: ("Loi n° 78-1239 du 29 décembre 1978 (LF pour 1979)", "14 décembre 1978",
           "1978-1979/ta1978_1979_0030.pdf"),
    1979: ("Loi n° 80-30 du 18 janvier 1980 (LF pour 1980)", "17 janvier 1980",
           "1979-1980/ta1979_1980_0049.pdf"),
    1980: ("Loi n° 80-1094 du 30 décembre 1980 (LF pour 1981)", "17 décembre 1980",
           "1980-1981/ta1980_1981_0039.pdf"),
}


def _loi(annee: int, article: str, citation: str = "") -> str:
    """La référence de l'article de la loi de finances qui impose les revenus
    d'``annee``, et ce qu'il dit."""
    intitule, adoptee, fichier = LOIS_DE_FINANCES[annee]
    reference = (f"{intitule}, {article}, texte définitif adopté par le Sénat le {adoptee} "
                 f"(senat.fr/leg/{fichier})")
    return f"{reference} : {citation}" if citation else reference


#: La loi de finances pour 1972, que le Sénat a rejetée, en commission mixte
#: paritaire puis en nouvelle lecture (senat.fr/leg/1971-1972/ta1971_1972_0031.pdf
#: et _0042.pdf, qui n'en portent pas la teneur), et que l'Assemblée nationale a
#: adoptée en lecture définitive : son texte se lit au rapport général de la
#: commission des finances du Sénat, qui reproduit celui que l'Assemblée a voté
#: en première lecture, et que confirme le rapport général sur la loi de
#: finances pour 1973 (:data:`RAPPORTS`). L'IPP en écrit le numéro 71-1161.
LOI_DE_FINANCES_POUR_1972 = (
    "Loi n° 71-1061 du 29 décembre 1971 (LF pour 1972), JORFTEXT000000687436, que le Sénat a "
    "rejetée et que l'Assemblée nationale a adoptée en lecture définitive")
RAPPORT_SUR_1972 = ("rapport général du Sénat n° 27 (1971-1972), tome II "
                    "(senat.fr/rap/1971-1972/i1971_1972_0027_02.pdf)")

#: Les rapports généraux de la commission des finances du Sénat qui disent ce
#: que les lois de finances ne chiffrent pas, ou ne citent que du code : la
#: réduction de l'article 198, la table des minorations et des majorations.
RAPPORTS = {
    1969: "rapport général du Sénat n° 56 (1969-1970), tome III "
          "(senat.fr/rap/1969-1970/i1969_1970_0056_03.pdf)",
    1970: "rapport général du Sénat n° 54 (1970-1971), tome II "
          "(senat.fr/rap/1970-1971/i1970_1971_0054_02.pdf)",
    1972: "rapport général du Sénat n° 66 (1972-1973), tome II "
          "(senat.fr/rap/1972-1973/i1972_1973_0066_02.pdf)",
}


def _loi_de_1972(article: str, citation: str = "") -> str:
    """La référence d'un article de la loi de finances pour 1972, au texte que
    l'Assemblée nationale a voté et que reproduit le rapport du Sénat."""
    reference = (f"{LOI_DE_FINANCES_POUR_1972}, {article}, texte voté par l'Assemblée "
                 f"nationale en première lecture, que reproduit le {RAPPORT_SUR_1972}")
    return f"{reference} : {citation}" if citation else reference


#: Ce que ces lois écrivent autrement que l'IPP, ou que l'IPP porte sans
#: référence : corrigé, ou daté de son texte, clé par clé (voir l'en-tête).
INTEGRATION_AU_BAREME = _loi(
    1973, "art. 2", "« Les franchises et les décotes prévues à l'article 198 ter du Code général "
    "des impôts, ainsi que les minorations dégressives visées à l'article 199 bis du même Code, "
    "sont intégrées au barème »")
CORRECTIONS.update({
    ("bareme", 1974): (
        {"seuils": [0, 5550, 5825, 7000, 11100, 15050, 19000, 22950, 26475, 45825, 64900,
                    84000, 103150]},
        _loi(1974, "art. 2, I", "« 11 100 F à 11 650 F : 5 % », « 45 900 F à 52 950 F : 35 % », "
             "pour deux parts ; l'IPP porte 5 500 F et 24 450 F par part"),
        "loi"),
    ("bareme", 1980): (
        {"seuils": [0, 9890, 10340, 12270, 19410, 24950, 31360, 37940, 43770, 72940, 100320,
                    118660, 135000]},
        _loi(1980, "art. 2, I", "« De 62 720 F à 75 880 F : 30 % », pour deux parts, lu à "
             "l'image du texte ; l'IPP porte 37 970 F par part"),
        "loi"),
    ("deductions", 1975): (
        {"frais_professionnels_minimum": 1200, "vingt_pour_cent_maximum": 70000,
         "vingt_pour_cent_plafond": 350000},
        _loi(1976, "art. 2, IV", "le minimum des frais professionnels « est porté de 1 200 F "
             "à 1 500 F » ; la limite des 20 % est « une fois et demie la limite de la dernière "
             "tranche du barème correspondant à deux parts, ce chiffre étant arrondi à la "
             "dizaine de milliers de francs supérieure » (loi n° 73-1150, art. 5), 1,5 fois "
             "226 900 F (loi n° 75-1278, art. 2, I), 340 350 F, soit 350 000 F ; l'IPP porte "
             "340 000 F"),
        "loi"),
    ("decote", 1973): ({}, INTEGRATION_AU_BAREME, "loi"),
    ("minorations_exceptionnelles", 1973): ({}, INTEGRATION_AU_BAREME, "loi"),
    ("majorations_exceptionnelles", 1980): (
        {"minimum": 200},
        "Loi n° 81-734 du 3 août 1981 (LFR pour 1981), art. 1er, que l'index n'a qu'en "
        "notice, lu aux textes que le Sénat a modifiés en première et en nouvelle lecture "
        "(24 et 30 juillet 1981, senat.fr/leg/1980-1981/ta1980_1981_0086.pdf et _0094.pdf), "
        "dont les deux rédactions portent : « La partie supérieure à 100.000 F de l'impôt sur "
        "le revenu, dû au titre de l'année 1980 [...] est majorée de 25 % [...] La "
        "majoration n'est pas due si elle est inférieure à 200 F »",
        "loi"),
    ("exoneration", 1977): (
        {"limite": 15200, "limite_plus_de_65_ans": 16600},
        _loi(1977, "art. 2, II", "« n'excède pas 15 200 F ou 16 600 F s'ils sont âgés de plus "
             "de soixante-cinq ans [...] Ces limites sont identiques quelle que soit la nature "
             "des revenus perçus » ; LEGIARTI000006317059"),
        "loi"),
    ("exoneration", 1978): (
        {"limite": 16800, "limite_plus_de_65_ans": 18300},
        _loi(1978, "art. 2, II") + " ; CGI, art. 5, 2° bis, LEGIARTI000006307017", "loi"),
    ("exoneration", 1979): (
        {"limite": 18600, "limite_plus_de_65_ans": 20300},
        _loi(1979, "art. 3, II") + " ; CGI, art. 5, LEGIARTI000006307018, note (1)", "loi"),
    ("exoneration", 1980): (
        {"limite": 21100, "limite_plus_de_65_ans": 23000},
        _loi(1980, "art. 2, III, 1") + " ; CGI, art. 5, 2° bis, LEGIARTI000006307018", "loi"),
    ("abattement_age_invalidite", 1977): (
        {"abattement_plein": 3400, "seuil_plein": 21000, "abattement_reduit": 1700,
         "seuil_reduit": 34000},
        _loi(1977, "art. 3, II") + " ; LEGIARTI000006317060", "loi"),
    ("abattement_age_invalidite", 1978): (
        {"abattement_plein": 3720, "seuil_plein": 23000, "abattement_reduit": 1860,
         "seuil_reduit": 37200},
        _loi(1978, "art. 2, III") + " ; CGI, art. 157 bis, LEGIARTI000006307950", "loi"),
    ("abattement_age_invalidite", 1979): (
        {"abattement_plein": 4080, "seuil_plein": 25200, "abattement_reduit": 2040,
         "seuil_reduit": 40800},
        _loi(1979, "art. 3, III") + " ; CGI, art. 157 bis, LEGIARTI000006307951, note (1)", "loi"),
    ("abattement_age_invalidite", 1980): (
        {"abattement_plein": 4630, "seuil_plein": 28600, "abattement_reduit": 2315,
         "seuil_reduit": 46300},
        _loi(1980, "art. 2, III, 2") + " ; CGI, art. 157 bis, LEGIARTI000006307951", "loi"),
})
COMPLEMENTS["exoneration"] = [
    {"annee": 1973, "monnaie": "FRF", "limite": 10000, "limite_autres": 8000, "origine": "loi",
     "texte": _loi(1973, "art. 4", "« Les personnes physiques qui bénéficient principalement de "
                   "traitements, salaires et pensions sont exonérées de l'impôt sur le revenu, "
                   "lorsque leur revenu, net de frais professionnels, n'excède pas 10 000 F » ; "
                   "« Pour les autres personnes physiques, la limite d'exonération est fixée à "
                   "8 000 F » ; LEGIARTI000006316777")},
    {"annee": 1974, "monnaie": "FRF", "limite": 11400, "limite_plus_de_65_ans": 12500,
     "limite_autres": 10000, "origine": "loi",
     "texte": _loi(1974, "art. 2, II") + " ; LEGIARTI000006272925"},
    {"annee": 1975, "monnaie": "FRF", "limite": 12600, "limite_plus_de_65_ans": 13800,
     "limite_autres": 11200, "origine": "loi",
     "texte": _loi(1975, "art. 2, II") + " ; LEGIARTI000006316887"},
    {"annee": 1976, "monnaie": "FRF", "limite": 13800, "limite_plus_de_65_ans": 15100,
     "limite_autres": 13100, "origine": "loi",
     "texte": _loi(1976, "art. 2, II") + " ; LEGIARTI000006316960"},
]
COMPLEMENTS["abattement_age_invalidite"] = [
    {"annee": 1973, "monnaie": "FRF", "abattement_plein": 2000, "seuil_plein": 12000,
     "abattement_reduit": 1000, "seuil_reduit": 20000, "origine": "loi",
     "texte": _loi(1973, "art. 3", "« La déduction de 500 F dont les personnes âgées de plus de "
                   "soixante-cinq ans ou invalides bénéficient [...] est portée à 2 000 F pour "
                   "celles dont le revenu net global n'excède pas 12 000 F et 1 000 F pour celles "
                   "dont le revenu net global est compris entre 12 000 F et 20 000 F »")},
    {"annee": 1974, "monnaie": "FRF", "abattement_plein": 2300, "seuil_plein": 14000,
     "abattement_reduit": 1150, "seuil_reduit": 23000, "origine": "loi",
     "texte": _loi(1974, "art. 6")},
    {"annee": 1975, "monnaie": "FRF", "abattement_plein": 2800, "seuil_plein": 17000,
     "abattement_reduit": 1400, "seuil_reduit": 28000, "origine": "loi",
     "texte": _loi(1975, "art. 2, III") + " ; LEGIARTI000006316887"},
    {"annee": 1976, "monnaie": "FRF", "abattement_plein": 3100, "seuil_plein": 19000,
     "abattement_reduit": 1550, "seuil_reduit": 31000, "origine": "loi",
     "texte": _loi(1976, "art. 2, III") + " ; LEGIARTI000006316960"},
    *COMPLEMENTS["abattement_age_invalidite"],
]
COMPLEMENTS["deductions"] = [
    {"annee": 1976, "monnaie": "FRF", "frais_professionnels_taux": 0.1,
     "frais_professionnels_minimum": 1500, "vingt_pour_cent_taux": 0.2,
     "vingt_pour_cent_maximum": 70000, "vingt_pour_cent_plafond": 350000, "origine": "loi",
     "texte": _loi(1976, "art. 2, IV", "« Le montant minimal de la déduction forfaitaire pour "
                   "frais professionnels accordée aux salariés est porté de 1 200 F à 1 500 F »")},
    *COMPLEMENTS["deductions"],
]

# -- Les revenus de 1969 à 1972 : les lois de finances pour 1970 à 1973 ----------
#
# Le barème de la loi porte, jusqu'en 1971, des points de plus que celui des
# salariés : la réduction de l'article 198 les rend aux salaires et aux
# pensions (:data:`REDUCTION_DES_SALAIRES`). L'IPP ne donne que les taux des
# salariés, et 25 % au lieu de 20 % à la quatrième tranche, de 1960 à 1972.
MINIMUM_DE_1970 = _loi(
    1970, "art. 4", "« le montant de la ou des déductions forfaitaires pour frais "
    "professionnels ne peut être inférieur à 1.200 F, sans pouvoir excéder le montant brut de "
    "ces traitements et salaires » ; porté « de 1 200 F à 1 500 F » pour les revenus de 1976 "
    "(loi n° 76-1232, art. 2, IV)")
CORRECTIONS.update({
    ("bareme", 1969): (
        {"taux": [0.05, 0.15, 0.2, 0.25, 0.35, 0.45, 0.55, 0.65]},
        _loi(1969, "art. 3, I", "« Il est fait application du taux de : 5 % à la fraction du "
             "revenu qui n'excède pas 5.400 F ; 15 % à la fraction du revenu comprise entre "
             "5.400 F et 9.600 F [...] 65 % à la fraction du revenu supérieure à 152.800 F », "
             "un barème « pour deux parts » (" + RAPPORTS[1970] + ", p. 79) ; l'IPP porte ces "
             "taux diminués des 5 points que la réduction de l'article 198 rend aux salaires et "
             "aux pensions, et 25 % à la quatrième tranche"),
        "loi"),
    ("bareme", 1970): (
        {"taux": [0.03, 0.13, 0.18, 0.23, 0.33, 0.43, 0.53, 0.63]},
        _loi(1970, "art. 2, II", "« N'excédant pas 5.800 F : 3 [...] Supérieure à 160.400 F : "
             "63 », pour les revenus de 1970 ; l'IPP porte les taux de 1971 et des années "
             "suivantes, de trois points plus bas, et 25 % à la quatrième tranche"),
        "loi"),
    ("bareme", 1971): (
        {"taux": [0.03, 0.13, 0.18, 0.23, 0.33, 0.43, 0.53, 0.63]},
        _loi_de_1972("art. 2, I", "« N'excédant pas 6.200 F : 3 [...] Supérieure à 168.400 F : "
                     "63 », pour les revenus de 1971, que rappelle le " + RAPPORTS[1972]
                     + ", p. 9 ; l'IPP porte les taux de 1972, de trois points plus bas, et "
                     "25 % à la quatrième tranche"),
        "rapport"),
    ("bareme", 1972): (
        {"taux": [0.0, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6]},
        _loi(1972, "art. 2", "« Comprise entre 19.000 F et 28.100 F : 20 », pour deux parts, lu "
             "à l'image du texte ; l'IPP porte 25 %"),
        "loi"),
    ("majorations_exceptionnelles", 1970): (
        {},
        _loi(1970, "art. 2, IX", "« cotisations comprises entre 10.001 F et 15.000 F : 1 % ; "
             "cotisations comprises entre 15.001 F et 20.000 F : 2 % ; cotisations supérieures à "
             "20.000 F : 3 % »"),
        "loi"),
    ("majorations_exceptionnelles", 1971): (
        {},
        _loi_de_1972("art. 2, III", "« cotisations comprises entre 15.001 et 20.000 F : 1 % ; "
                     "cotisations supérieures à 20.000 F : 2 % »"),
        "rapport"),
    ("deductions", 1973): ({"frais_professionnels_minimum": 1200}, MINIMUM_DE_1970, "loi"),
    ("deductions", 1974): ({"frais_professionnels_minimum": 1200}, MINIMUM_DE_1970, "loi"),
})
COMPLEMENTS["deductions"] = [
    {"annee": 1970, "monnaie": "FRF", "frais_professionnels_taux": 0.1,
     "frais_professionnels_minimum": 1200, "vingt_pour_cent_taux": 0.2, "origine": "loi",
     "texte": f"{MINIMUM_DE_1970} ; les 10 % et les 20 % de l'IPP, sans référence"},
    *COMPLEMENTS["deductions"],
]
#: Les limites de l'exonération et de la décote de l'article 198 ter, en impôt :
#: ``franchise`` et ``limite`` pour le foyer jusqu'à ``parts_forfait`` parts,
#: ``franchise_par_part`` et ``limite_par_part`` au-delà ; celles du foyer dont
#: un déclarant a ``age_majore`` ans — ou est invalide, si
#: ``invalides_majores`` —, suffixées de ``_majoree``. La décote, entre les
#: deux, suit la formule continue de l'IPP : l'article 198 ter n'est pas lu.
COMPLEMENTS["decote"] = [
    {"annee": 1969, "monnaie": "FRF", "franchise": 230, "limite": 690, "parts_forfait": 2,
     "franchise_par_part": 100, "limite_par_part": 300, "age_majore": 70,
     "franchise_majoree": 300, "limite_majoree": 900, "parts_forfait_majore": 1.5,
     "franchise_majoree_par_part": 180, "limite_majoree_par_part": 540, "origine": "loi",
     "texte": _loi(1969, "art. 4, I", "« Les limites respectives d'application de "
                   "l'exonération et de la décote prévues à l'article 198 ter [...] sont fixées "
                   "comme suit : 230 F et 690 F pour les contribuables qui ont droit à une part, "
                   "à une part et demie ou à deux parts [...] ; 100 F et 300 F par part pour les "
                   "autres contribuables. Toutefois, ces limites sont portées à : 300 F et 900 F "
                   "pour les contribuables âgés de plus de 70 ans [...] qui ont droit à une part "
                   "ou à une part et demie [...] ; 180 F et 540 F par part pour les autres "
                   "contribuables âgés de plus de 70 ans »")},
    {"annee": 1970, "monnaie": "FRF", "franchise": 230, "limite": 690, "parts_forfait": 2,
     "franchise_par_part": 100, "limite_par_part": 300, "age_majore": 65,
     "invalides_majores": True, "franchise_majoree": 380, "limite_majoree": 1140,
     "parts_forfait_majore": 1.5, "franchise_majoree_par_part": 230,
     "limite_majoree_par_part": 690, "origine": "loi",
     "texte": _loi(1970, "art. 2, V et VI", "pour les contribuables âgés de plus de 65 ans, "
                   "« 380 F et 1.140 F pour les contribuables qui ont droit à une part ou à une "
                   "part et demie ; 230 F et 690 F par part pour les autres contribuables », "
                   "limites qui « s'appliquent aux contribuables invalides » ; les autres, "
                   "celles de la loi n° 69-1161, art. 4, I")},
    *COMPLEMENTS["decote"],
]
#: Les minorations et les majorations par paliers : jusqu'à quelle cotisation
#: chaque taux vaut, et, pour les majorations, le taux au-delà.
COMPLEMENTS["minorations_exceptionnelles"] = [
    {"annee": 1969, "monnaie": "FRF",
     "paliers": [[1000, 0.15], [1500, 0.12], [2000, 0.1], [2500, 0.08], [3000, 0.06],
                 [3500, 0.04], [5000, 0.02]], "origine": "rapport",
     "texte": _loi(1969, "art. 3, II", "« Les minorations des cotisations prévues par le 1-2 de "
                   "l'article 2 de la loi n° 68-1172 du 27 décembre 1968 sont maintenues en "
                   "vigueur » ; leur table, « sans changement » : « Cotisations n'excédant pas "
                   "1.000 F : — 15 % ; Cotisations comprises entre 1.001 F et 1.500 F : — 12 % "
                   "[...] Cotisations comprises entre 3.501 F et 5.000 F : — 2 % » ("
                   + RAPPORTS[1969] + ", p. 11), qui « restent, par contre, en vigueur » pour "
                   "les revenus de 1972 (" + RAPPORTS[1972] + ", p. 9) ; la note de l'IPP la "
                   "fait décroître en ligne droite de 1 000 F à 3 500 F")},
]
COMPLEMENTS["majorations_exceptionnelles"] = [
    {"annee": 1969, "monnaie": "FRF",
     "paliers": [[7000, 0.0], [8000, 0.02], [9000, 0.03], [10000, 0.04], [10500, 0.05],
                 [12000, 0.06], [14000, 0.07]], "taux_au_dela": 0.075, "origine": "rapport",
     "texte": _loi(1969, "art. 3, V", "« leurs taux sont réduits de moitié et aucune majoration "
                   "n'est applicable aux cotisations comprises entre 6.001 F et 7.000 F » ; leur "
                   "table : « 7.001 et 8.000 F : + 2 % [...] 10.001 et 10.500 F : + 5 % ; "
                   "10.501 et 12.000 F : + 6 % ; 12.001 et 14.000 F : + 7 % ; Cotisations "
                   "supérieures à : 14.000 F : + 7,5 % » (" + RAPPORTS[1969] + ", p. 11) ; la "
                   "note de l'IPP les fait aller par paliers de 1 000 F, 5 % jusqu'à 11 000 F")},
]
COMPLEMENTS["exoneration"].insert(0, {
    "annee": 1972, "monnaie": "FRF", "limite_revenu_brut_des_salaries": 9500, "origine": "loi",
    "texte": _loi(1972, "art. 4", "« Les personnes physiques qui bénéficient principalement de "
                  "traitements et salaires sont exonérées de l'impôt sur le revenu lorsque leur "
                  "revenu brut n'excède pas 9.500 F » ; principalement, quand « les salaires "
                  "atteignent (après déduction des frais professionnels) au moins la moitié du "
                  "revenu net » (" + RAPPORTS[1972] + ", p. 11)")})
COMPLEMENTS["abattement_age_invalidite"].insert(0, {
    "annee": 1972, "monnaie": "FRF", "abattement_plein": 500, "seuil_plein": 12000,
    "seuil_plein_exclu": True, "origine": "loi",
    "texte": _loi(1972, "art. 3", "« Les contribuables âgés de plus de soixante-cinq ans au 31 "
                  "décembre de l'année d'imposition, ou remplissant l'une des conditions "
                  "d'invalidité mentionnées à l'article 195 du Code général des impôts, et dont "
                  "le revenu net global est inférieur à 12.000 F, peuvent déduire de ce revenu "
                  "une somme de 500 F. Ils peuvent opérer une déduction identique au titre de "
                  "leur conjoint »")})
#: La réduction d'impôt des salaires et des pensions (art. 198), jusqu'aux
#: revenus de 1971 : ``taux`` de leur montant net imposable, et, en 1971, des
#: autres revenus qui n'excèdent pas ``autres_revenus_maximum`` ; ou, si elle est
#: plus forte, celle des contribuables âgés (loi de finances pour 1970, art. 4,
#: II) : ``taux_agees`` de leur revenu imposable, au plus ``plafond_agees``, dès
#: ``age_agees`` ans.
REDUCTION_DES_SALAIRES = [
    {"annee": 1969, "monnaie": "FRF", "taux": 0.05, "age_agees": 75, "taux_agees": 0.05,
     "plafond_agees": 270, "origine": "rapport",
     "texte": "CGI, art. 198, non lu : « tous les contribuables percevant des salaires ou des "
              "pensions bénéficient d'une réduction d'impôt égale à 5 % du montant net "
              "imposable de ces salaires ou pensions » (" + RAPPORTS[1969] + ", p. 14), « ce "
              "qui aboutit par conséquent à diminuer de 5 points le jeu du barème » ("
              + RAPPORTS[1970] + ", p. 77) ; " + _loi(
                  1969, "art. 4, II", "« Les contribuables âgés de plus de 75 ans [...] "
                  "bénéficient, dans la limite de 270 F, d'une réduction d'impôt égale à 5 % de "
                  "leurs revenus effectivement soumis à l'impôt [...] Elle ne se cumule pas avec "
                  "la réduction d'impôt visée à l'article 198 du même code, la réduction dont le "
                  "montant est le plus élevé étant seule retenue »")},
    {"annee": 1970, "monnaie": "FRF", "taux": 0.03, "age_agees": 70, "taux_agees": 0.03,
     "plafond_agees": 170, "origine": "loi",
     "texte": _loi(1970, "art. 2, III et VII, et art. 3, I", "« Les réductions d'impôts "
                   "prévues à l'article 198 [...] et au paragraphe II de l'article 4 de la loi "
                   "de finances pour 1970 sont supprimées pour l'imposition des revenus des "
                   "années 1971 et suivantes. Leur taux est fixé à 3 % pour l'imposition des "
                   "revenus de l'année 1970 » ; la seconde « ne peut excéder 170 F » et « est "
                   "étendue aux personnes âgées de plus de 70 ans » ; la première, « à "
                   "l'ensemble des salaires, pensions et rentes viagères »")},
    {"annee": 1971, "monnaie": "FRF", "taux": 0.03, "autres_revenus_maximum": 15000,
     "age_agees": 70, "taux_agees": 0.03, "plafond_agees": 180, "origine": "rapport",
     "texte": _loi_de_1972("art. 2, II", "« 1° Pour l'imposition des revenus de l'année 1971, "
                           "la réduction d'impôt prévue à l'article 198 [...] est maintenue et "
                           "étendue aux revenus autres que les traitements, salaires, pensions "
                           "et rentes viagères lorsqu'ils n'excèdent pas 15.000 F par "
                           "contribuable. 2° La réduction d'impôt prévue à l'article 4-II de la "
                           "loi de finances pour 1970 est maintenue pour l'imposition des "
                           "revenus de l'année 1971. Les plafonds de cette réduction sont fixés "
                           "à 180 F pour la Métropole »")},
    {"annee": 1972, "supprimee": True,
     "texte": _loi(1972, "art. 2") + " : la réduction de 3 % « est maintenant totalement "
              "intégrée au barème » (" + RAPPORTS[1972] + ", p. 8) ; celle des contribuables "
              "âgés, supprimée dès 1971 (loi n° 70-1199, art. 2, III, 1), n'a été maintenue "
              "que pour 1971"},
]

# -- Les revenus de 1960 à 1968 : la loi de 1959 et les lois de finances pour 1961
# à 1969 --------------------------------------------------------------------------
#
# Le barème de la loi porte, depuis la réforme de 1959, cinq points de plus que
# celui des salariés, que la réduction de l'article 198 leur rend ; l'IPP n'en
# donne que les taux des salariés, et 25 % au lieu de 20 % à la quatrième
# tranche. Les textes : ceux que le Sénat publie, définitifs, ou de première
# lecture quand les deux assemblées y ont voté l'article dans les mêmes termes ;
# pour une loi qu'il a rejetée, le texte de l'Assemblée nationale que reproduit
# le rapport de sa commission des finances.

#: Les lois dont le Sénat publie le texte : leur intitulé, ce qu'il en a adopté
#: et quand, son fichier sous senat.fr/leg/.
TEXTES_DU_SENAT = {
    "59-1472": ("Loi n° 59-1472 du 28 décembre 1959 portant réforme du contentieux fiscal et "
                "divers aménagements fiscaux", "texte adopté par le Sénat en première lecture "
                "le 24 novembre 1959, qu'il dit conforme en deuxième lecture le 17 décembre "
                "(ta1959_1960_0016.pdf)", "1959-1960/ta1959_1960_0002.pdf"),
    "60-1384": ("Loi n° 60-1384 du 23 décembre 1960 (LF pour 1961)", "texte définitif adopté "
                "par le Sénat le 13 décembre 1960", "1960-1961/ta1960_1961_0044.pdf"),
    "63-1241": ("Loi n° 63-1241 du 19 décembre 1963 (LF pour 1964)", "texte définitif adopté "
                "par le Sénat le 6 décembre 1963", "1963-1964/ta1963_1964_0026.pdf"),
    "64-1279": ("Loi n° 64-1279 du 23 décembre 1964 (LF pour 1965)", "texte adopté par le "
                "Sénat en première lecture le 26 novembre 1964, conforme sur ce point à celui "
                "de l'Assemblée nationale", "1964-1965/ta1964_1965_0014.pdf"),
    "65-997": ("Loi n° 65-997 du 29 novembre 1965 (LF pour 1966)", "texte adopté par le Sénat "
               "en première lecture le 15 novembre 1965, conforme sur ce point à celui de "
               "l'Assemblée nationale", "1965-1966/ta1965_1966_0014.pdf"),
    "66-935": ("Loi n° 66-935 du 17 décembre 1966 (LF pour 1967)", "texte définitif adopté par "
               "le Sénat le 7 décembre 1966", "1966-1967/ta1966_1967_0023.pdf"),
    "68-695": ("Loi n° 68-695 du 31 juillet 1968 (LFR pour 1968)", "texte définitif adopté par "
               "le Sénat le 25 juillet 1968", "1967-1968/ta1967_1968_0094.pdf"),
}


def _texte(loi: str, article: str, citation: str = "") -> str:
    """La référence d'un article d'une loi de :data:`TEXTES_DU_SENAT`, et ce
    qu'il dit."""
    intitule, adopte, fichier = TEXTES_DU_SENAT[loi]
    reference = f"{intitule}, {article}, {adopte} (senat.fr/leg/{fichier})"
    return f"{reference} : {citation}" if citation else reference


#: Les rapports de la commission des finances du Sénat qui reproduisent le
#: texte de l'Assemblée nationale d'une loi qu'il a rejetée ou votée conforme,
#: ou disent ce qu'aucun texte lu ne chiffre.
RAPPORTS_DES_ANNEES_1960 = {
    "1959-1960/24": "rapport du Sénat n° 24 (1959-1960) "
                    "(senat.fr/rap/1959-1960/i1959_1960_0024.pdf)",
    "1961-1962/53": "rapport général du Sénat n° 53 (1961-1962), tome II "
                    "(senat.fr/rap/1961-1962/i1961_1962_0053_02.pdf)",
    "1962-1963/106": "rapport du Sénat n° 106 (1962-1963) "
                     "(senat.fr/rap/1962-1963/i1962_1963_0106.pdf)",
    "1963-1964/23": "rapport général du Sénat n° 23 (1963-1964), tome II "
                    "(senat.fr/rap/1963-1964/i1963_1964_0023_02.pdf)",
    "1964-1965/23": "rapport général du Sénat n° 23 (1964-1965), tome II "
                    "(senat.fr/rap/1964-1965/i1964_1965_0023_02.pdf)",
    "1965-1966/31": "rapport général du Sénat n° 31 (1965-1966), tome II "
                    "(senat.fr/rap/1965-1966/i1965_1966_0031_02.pdf)",
    "1966-1967/25": "rapport général du Sénat n° 25 (1966-1967), tome II "
                    "(senat.fr/rap/1966-1967/i1966_1967_0025_02.pdf)",
    "1967-1968/16": "rapport général du Sénat n° 16 (1967-1968), tome II "
                    "(senat.fr/rap/1967-1968/i1967_1968_0016_02.pdf)",
    "1967-1968/168": "rapport du Sénat n° 168 (1967-1968) "
                     "(senat.fr/rap/1967-1968/i1967_1968_0168.pdf)",
    "1968-1969/40": "rapport général du Sénat n° 40 (1968-1969), tome II "
                    "(senat.fr/rap/1968-1969/i1968_1969_0040_02.pdf)",
}
_R = RAPPORTS_DES_ANNEES_1960

#: La loi de finances pour 1969, que le Sénat a rejetée en nouvelle lecture le
#: 17 décembre 1968 (senat.fr/leg/1968-1969/ta1968_1969_0040.pdf), lue au texte
#: de l'Assemblée nationale que reproduit son rapport général.
LOI_POUR_1969 = (
    "Loi n° 68-1172 du 27 décembre 1968 (LF pour 1969), art. 2, I, 2, au texte de l'Assemblée "
    "nationale que reproduit le " + _R["1968-1969/40"] + ", p. 68 et 69, et que le Sénat avait "
    "adopté en première lecture le 5 décembre 1968 (senat.fr/leg/1968-1969/ta1968_1969_0023.pdf)"
    " : « Après application, le cas échéant, de la réduction d'impôt et de la décote prévues "
    "respectivement aux articles 198 et 198 ter du Code général des impôts, les cotisations sont "
    "minorées ou majorées dans les conditions suivantes »")
TAUX_DE_LA_LOI = [0.05, 0.15, 0.2, 0.25, 0.35, 0.45, 0.55, 0.65]
SALARIES_DE_L_IPP = ("l'IPP porte ces taux diminués des 5 points que la réduction de l'article "
                     "198 rend aux salaires et aux pensions, et 25 % à la quatrième tranche")
BAREME_DE_1965_RECONDUIT = _texte(
    "66-935", "art. 2, IV", "« Le barème retenu pour l'imposition des revenus de l'année 1965 "
    "est applicable pour l'imposition des revenus des années 1966 et 1967. Toutefois, les taux "
    "de 55 % et de 65 % applicables aux tranches supérieures du barème sont portés "
    "respectivement à 60 % et à 70 % pour l'imposition des revenus de l'année 1966 »")
CORRECTIONS.update({
    ("bareme", 1960): (
        {"taux": TAUX_DE_LA_LOI},
        _texte("60-1384", "art. 2, I", "« En ce qui concerne les contribuables mariés sans "
               "enfant à charge [...] l'impôt sur le revenu des personnes physiques est [...] "
               "calculé en appliquant le taux de : 5 % à la fraction du revenu qui n'excède pas "
               "4.600 NF ; 15 % à la fraction comprise entre 4.600 et 7.500 NF [...] 65 % à la "
               "fraction supérieure à 128.000 NF » ; " + SALARIES_DE_L_IPP),
        "loi"),
    ("bareme", 1961): (
        {"taux": TAUX_DE_LA_LOI},
        _texte("60-1384", "art. 2, II", "« Les chiffres de 7.500, 13.000 et 19.500 NF figurant "
               "au barème visé au paragraphe I ci-dessus sont portés respectivement à 8.000, "
               "13.500 et 20.000 NF » pour les revenus de 1961 ; " + SALARIES_DE_L_IPP),
        "loi"),
    ("bareme", 1962): (
        {"taux": TAUX_DE_LA_LOI},
        _texte("60-1384", "art. 2, III", "« le chiffre de 4.600 NF figurant au barème visé au "
               "paragraphe I ci-dessus est porté à 4.800 NF » pour les revenus de 1962 ; "
               + SALARIES_DE_L_IPP),
        "loi"),
    ("bareme", 1963): (
        {"taux": [0.05, 0.15, 0.2, 0.25, 0.35, 0.45, 0.55, 0.665]},
        _texte("63-1241", "art. 2, 1°", "« Le taux de 65 % figurant à la dernière ligne du "
               "barème prévu à l'article 197 du Code général des impôts est porté à 66,5 % » "
               "pour les revenus de 1963 ; la suite des barèmes depuis 1959 au "
               + _R["1964-1965/23"] + ", p. 59 ; " + SALARIES_DE_L_IPP),
        "loi"),
    ("bareme", 1964): (
        {"taux": TAUX_DE_LA_LOI},
        _texte("64-1279", "art. 2, I", "« Fraction du revenu qui n'excède pas 4.800 F : 5 % "
               "[...] Fraction du revenu comprise entre 14.700 F et 21.700 F : 25 % [...] "
               "Fraction du revenu supérieure à 140.000 F : 65 % » ; " + SALARIES_DE_L_IPP),
        "loi"),
    ("bareme", 1965): (
        {"taux": TAUX_DE_LA_LOI},
        _texte("64-1279", "art. 2, III", "« les chiffres de 8.800 F, 14.700 F, 21.700 F, "
               "35.000 F, 70.000 F et 140.000 F [...] sont portés respectivement à 9.000 F, "
               "15.200 F, 22.500 F, 36.000 F, 72.000 F et 144.000 F » pour les revenus de 1965")
        + " ; " + _texte("65-997", "art. 2, I", "« La limite supérieure de la première tranche "
                         "du barème [...] est portée de 4.800 F à 5.000 F » ; " + SALARIES_DE_L_IPP),
        "loi"),
    ("bareme", 1966): (
        {"taux": [0.05, 0.15, 0.2, 0.25, 0.35, 0.45, 0.6, 0.7]},
        BAREME_DE_1965_RECONDUIT + " ; " + SALARIES_DE_L_IPP, "loi"),
    ("bareme", 1967): (
        {"taux": TAUX_DE_LA_LOI},
        BAREME_DE_1965_RECONDUIT + " ; pour les revenus de 1968, « le tarif prévu à l'article "
        "197-1 du Code général des impôts » (loi n° 68-1172, art. 2, I, 1, " + _R["1968-1969/40"]
        + ", p. 68) ; " + SALARIES_DE_L_IPP,
        "loi"),
    ("majorations_exceptionnelles", 1960): (
        {},
        "« l'article 1er du décret n° 56-665 du 6 juillet 1956 avait institué [...] une majoration "
        "d'un décime (10 %) sur le montant de l'impôt progressif dû par les personnes physiques. "
        "Cette majoration ne s'appliquait qu'aux contribuables ayant un revenu net supérieur à "
        "6.000 F, sans application du quotient familial » (" + _R["1962-1963/106"] + ", p. 84) ; "
        "CGI, art. 199 bis, 2°",
        "rapport"),
    ("majorations_exceptionnelles", 1961): (
        {},
        _texte("60-1384", "art. 2, II", "« Pour l'imposition des revenus de l'année 1961, la "
               "majoration d'un décime prévue à l'article 199 bis, 2°, du Code général des "
               "impôts est réduite de moitié »"),
        "loi"),
    ("majorations_exceptionnelles", 1963): (
        {},
        _texte("63-1241", "art. 2, 2°", "« Les cotisations établies par voie de rôles sont "
               "majorées de 5 % lorsque le revenu servant de base à l'imposition est supérieur à "
               "36.000 F. Cette majoration est calculée après application, le cas échéant, de la "
               "réduction d'impôt et de la décote visées respectivement aux articles 198 et 198 "
               "ter »"),
        "loi"),
    ("majorations_exceptionnelles", 1964): (
        {},
        _texte("64-1279", "art. 2, IV", "« La majoration de 5 % visée à l'article 2, 2° de la "
               "loi n° 63-1241 du 19 décembre 1963 est applicable aux cotisations [...] établies "
               "par voie de rôles au titre de l'année 1964 lorsque le revenu servant de base à "
               "l'imposition est supérieur à 45.000 F »"),
        "loi"),
    ("majorations_exceptionnelles", 1965): (
        {},
        "Loi n° 65-997 du 29 novembre 1965 (LF pour 1966), art. 2, IV, que le Sénat a rejetée, au "
        "texte de l'Assemblée nationale que reproduit le " + _R["1965-1966/31"] + ", p. 56 : « La "
        "majoration de 5 % visée à l'article 2-IV de la loi n° 64-1279 du 23 décembre 1964 est "
        "applicable aux cotisations [...] établies par voie de rôles au titre de l'année 1965 "
        "lorsque le revenu servant de base à l'imposition est supérieur à 50.000 F » ; les "
        "contribuables « dont les revenus déclarés sont supérieurs à 50.000 F » l'ont payée ("
        + _R["1966-1967/25"] + ", p. 79)",
        "rapport"),
    ("majorations_exceptionnelles", 1967): (
        {"decotes": [[500, 700], [2000, 2500], [5000, 5300]]},
        _texte("68-695", "art. 15", "« Les cotisations des contribuables soumis à l'impôt sur le "
               "revenu des personnes physiques au titre des revenus de 1967 sont majorées de 10 % "
               "quand leur montant est supérieur à 5.000 F [...] Cette majoration est portée à "
               "20 % quand la cotisation [...] est supérieure à 10.000 F et à 25 % quand cette "
               "cotisation est supérieure à 20.000 F. Lorsque la majoration est comprise entre "
               "500 F et 700 F elle est établie sous déduction d'une décote égale à la différence "
               "entre 700 F et son montant théorique » ; de même entre 2 000 F et 2 500 F, et "
               "entre 5 000 F et 5 300 F, lu à l'image du texte"),
        "loi"),
})
#: La réduction des salaires et des pensions, dès la réforme de 1959.
REDUCTION_DES_SALAIRES.insert(0, {
    "annee": 1960, "monnaie": "FRF", "taux": 0.05, "origine": "loi",
    "texte": _texte("59-1472", "art. 12 du texte du Sénat", "« Le montant de l'impôt sur le "
                    "revenu des personnes physiques [...] est, en ce qui concerne les "
                    "bénéficiaires de traitements, salaires et pensions, réduit d'une somme égale "
                    "à 5 % des sommes effectivement soumises à l'impôt sur le revenu des "
                    "personnes physiques au titre de ces traitements, salaires et pensions "
                    "lorsque ces rémunérations entrent dans le champ d'application du versement "
                    "forfaitaire prévu par l'article 231 du Code général des impôts ou sont "
                    "exonérés de ce versement » ; codifié à l'article 198, et étendu aux pensions "
                    "et rentes d'invalidité de la sécurité sociale pour les revenus de 1967 (loi n° "
                    "67-1114, art. 3)")})
#: Les limites de l'article 198 ter de 1960 à 1968 (voir celles de 1969) : sans
#: ``parts_forfait``, par part dès la première.
COMPLEMENTS["decote"] = [
    {"annee": 1960, "monnaie": "FRF", "franchise_par_part": 70, "limite_par_part": 140,
     "origine": "loi",
     "texte": _texte("59-1472", "art. 13 du texte du Sénat", "« Lorsque le montant de l'impôt "
                     "[...] après application éventuelle de la réduction de 5 % prévue à "
                     "l'article 12, n'excède pas 7.000 francs par part entière de revenu, la "
                     "cotisation correspondante n'est pas perçue. Lorsque ce montant est compris "
                     "entre 7.000 francs par part et 14.000 francs par part, la cotisation "
                     "correspondante est établie sous déduction d'une décote égale à la "
                     "différence existant entre le chiffre obtenu en multipliant le nombre de "
                     "parts par 14.000 francs et ledit montant », soit 70 F et 140 F ; codifié à "
                     "l'article 198 ter ; l'IPP en porte la ligne en 1959, en francs au lieu "
                     "d'anciens francs")},
    {"annee": 1961, "monnaie": "FRF", "franchise_par_part": 70, "limite_par_part": 210,
     "origine": "rapport",
     "texte": "« lorsque le montant de l'impôt sur le revenu n'excède pas 70 F par part entière "
              "de revenu (après application éventuelle de la réduction de 5 % pour les salaires "
              "et pensions et du crédit d'impôt), la cotisation correspondante n'est pas perçue. "
              "Lorsque le montant de l'impôt est compris entre 70 F et 210 F, la cotisation "
              "correspondante est établie sous déduction d'une décote égale à la moitié de la "
              "différence existant entre le chiffre obtenu en multipliant le nombre de parts par "
              "210 F et le montant de l'impôt » (" + _R["1964-1965/23"] + ", p. 60), « à "
              "l'heure actuelle » ; l'IPP la date des revenus de 1961, et de 1962 les 80 F et "
              "240 F de 1964 ; la loi qui l'écrit n'est pas lue"},
    {"annee": 1964, "monnaie": "FRF", "franchise": 120, "limite": 240, "parts_forfait": 1,
     "franchise_par_part": 80, "limite_par_part": 240, "age_majore": 75,
     "franchise_majoree_par_part": 150, "limite_majoree_par_part": 450, "origine": "loi",
     "texte": _texte("64-1279", "art. 2, II", "« Les limites de 70 F et 210 F prévues à "
                     "l'article 198 ter du Code général des impôts sont portées respectivement à "
                     "80 F et 240 F. Toutefois, la limite de 80 F visée à l'alinéa ci-dessus est "
                     "portée à 120 F lorsque le redevable a droit pour le calcul de l'impôt sur "
                     "le revenu des personnes physiques à une part. Lorsque la cotisation due par "
                     "un contribuable bénéficiant d'une part est comprise entre 120 et 240 F, "
                     "elle est établie sous déduction d'une décote égale à la différence "
                     "existant entre 240 F et ledit montant » ; art. 4, I, que le Sénat a voté "
                     "conforme, au texte que reproduit le " + _R["1964-1965/23"] + ", p. 65 : "
                     "« Les limites prévues au II de l'article 2 de la présente loi sont portées "
                     "respectivement à 150 F et 450 F en ce qui concerne les contribuables âgés "
                     "de plus de 75 ans au 31 décembre de l'année de l'imposition »")},
    {"annee": 1965, "monnaie": "FRF", "franchise": 160, "limite": 480, "parts_forfait": 1.5,
     "franchise_par_part": 80, "limite_par_part": 240, "age_majore": 75,
     "franchise_majoree": 250, "limite_majoree": 750, "parts_forfait_majore": 1.5,
     "franchise_majoree_par_part": 150, "limite_majoree_par_part": 450, "origine": "loi",
     "texte": _texte("65-997", "art. 2, II", "« Les cotisations dues par les contribuables qui "
                     "ont droit à une part ou à une part et demie ne sont pas perçues lorsque "
                     "leur montant n'excède pas 160 F. Lorsque ce montant est compris entre 160 F "
                     "et 480 F, la cotisation correspondante est établie sous déduction d'une "
                     "décote égale à la moitié de la différence existant entre 480 F et ledit "
                     "montant » ; art. 3, I, voté conforme : celles des plus de 75 ans « portées "
                     "respectivement à 250 F et 750 F pour les contribuables qui ont droit à une "
                     "part ou à une part et demie », 150 F et 450 F par part pour les autres ("
                     + _R["1966-1967/25"] + ", p. 79)")},
    {"annee": 1966, "monnaie": "FRF", "franchise": 190, "limite": 570, "parts_forfait": 2,
     "franchise_par_part": 80, "limite_par_part": 240, "age_majore": 75,
     "franchise_majoree": 250, "limite_majoree": 750, "parts_forfait_majore": 1.5,
     "franchise_majoree_par_part": 150, "limite_majoree_par_part": 450, "origine": "loi",
     "texte": _texte("66-935", "art. 2, II", "« Les limites d'exonération et de décote fixées à "
                     "160 F et 480 F par l'article 2-II de la loi n° 65-997 du 29 novembre 1965 "
                     "sont portées respectivement à 190 F et 570 F. Elles s'appliquent aux "
                     "contribuables qui ont droit à une part, une part et demie ou deux parts » ; "
                     "les autres, sans changement (" + _R["1967-1968/16"] + ", p. 66)")},
    {"annee": 1967, "monnaie": "FRF", "franchise": 190, "limite": 570, "parts_forfait": 2,
     "franchise_par_part": 80, "limite_par_part": 240, "age_majore": 70,
     "franchise_majoree": 250, "limite_majoree": 750, "parts_forfait_majore": 1.5,
     "franchise_majoree_par_part": 150, "limite_majoree_par_part": 450, "origine": "rapport",
     "texte": "Loi n° 67-1114 du 21 décembre 1967 (LF pour 1968), art. 2, que le Sénat a voté "
              "conforme en première lecture (senat.fr/leg/1967-1968/ta1967_1968_0005.pdf), au "
              "texte que reproduit le " + _R["1967-1968/16"] + ", p. 66, avec la table des "
              "limites : « Les limites d'exonération et de décote prévues en faveur des personnes "
              "âgées à l'article 198 ter du code général des impôts, sont applicables aux "
              "contribuables âgés de plus de 70 ans au 31 décembre de l'année d'imposition » ; "
              "inchangées pour les revenus de 1968 (" + RAPPORTS[1969] + ", p. 14)"},
    *COMPLEMENTS["decote"],
]
#: Les réductions de 1966 et de 1967, par tranche du revenu imposable du foyer
#: (``paliers_de_revenu``), sans limite au-delà de ``parts_sans_limite`` parts ;
#: la table de 1968, par tranche de la cotisation.
COMPLEMENTS["minorations_exceptionnelles"] = [
    {"annee": 1966, "monnaie": "FRF", "paliers_de_revenu": [[45000, 0.05], [50000, 0.04],
                                                           [55000, 0.02]],
     "origine": "rapport",
     "texte": _texte("66-935", "art. 2, I", "« Le montant de l'impôt sur le revenu des personnes "
                     "physiques dû par les contribuables dont le revenu imposable n'est pas "
                     "supérieur à 55.000 F sera réduit dans des conditions qui seront fixées par "
                     "décret, sans que cette réduction puisse être inférieure à 5 % pour un "
                     "revenu n'excédant pas 45.000 F. Cette réduction est calculée après "
                     "application, s'il y a lieu, de la réduction d'impôt visée à l'article 198 "
                     "du Code général des impôts et de la décote » ; le décret du 27 décembre "
                     "1966 : « 5 % pour les revenus inférieurs à 45.000 F ; 4 % pour les revenus "
                     "compris entre 45.000 et 50.000 F ; 2 % pour les revenus compris entre "
                     "50.000 et 55.000 F » (" + _R["1967-1968/168"] + ", p. 102) ; l'IPP les fait "
                     "décroître en ligne droite")},
    {"annee": 1967, "monnaie": "FRF", "paliers_de_revenu": [[45000, 0.1], [50000, 0.08],
                                                           [55000, 0.05]],
     "parts_sans_limite": 3, "origine": "rapport",
     "texte": "Loi de finances rectificative pour 1968, art. 1er, que le Sénat a voté conforme en "
              "première lecture le 21 mai 1968 (senat.fr/leg/1967-1968/ta1967_1968_0068.pdf), au "
              "texte de l'Assemblée nationale que reproduit le " + _R["1967-1968/168"] + ", p. "
              "102 : « La réduction d'impôt prévue à l'article 2-1 de la loi de finances pour "
              "1967 [...] est portée à : 10 % pour les contribuables dont le revenu imposable "
              "n'excède pas 45.000 F ; 8 % pour les contribuables dont le revenu imposable est "
              "supérieur à 45.000 F mais n'excède pas 50.000 F ; 5 % pour les contribuables dont "
              "le revenu imposable est supérieur à 50.000 F mais n'excède pas 55.000 F. La limite "
              "de 55.000 F prévue ci-dessus n'est pas applicable aux contribuables qui ont droit, "
              "pour le calcul de leur impôt, à un nombre de parts supérieur à trois » ; l'IPP les "
              "fait décroître en ligne droite, sans cette limite"},
    {"annee": 1968, "monnaie": "FRF",
     "paliers": [[1000, 0.15], [1500, 0.12], [2000, 0.1], [2500, 0.08], [3000, 0.06],
                 [3500, 0.04], [5000, 0.02]], "origine": "rapport",
     "texte": LOI_POUR_1969 + " : « cotisations n'excédant pas 1.000 F : — 15 % ; cotisations "
              "comprises entre 1.001 F et 1.500 F : — 12 % [...] 3.501 F et 5.000 F : — 2 % ; "
              "5.001 F et 6.000 F : 0 » ; l'IPP les fait décroître en ligne droite"},
    *COMPLEMENTS["minorations_exceptionnelles"],
]
#: Le demi-décime de 1962, au-delà d'un revenu par part ; la table de 1968.
COMPLEMENTS["majorations_exceptionnelles"] = [
    {"annee": 1962, "monnaie": "FRF", "seuil_revenu_par_part": 8000, "taux_1": 0.05,
     "origine": "rapport",
     "texte": "Loi n° 63-628 du 2 juillet 1963 (LFR pour 1963), que le Sénat a rejetée, au texte "
              "de l'Assemblée nationale que reproduit le " + _R["1962-1963/106"] + ", p. 84 : "
              "« Les cotisations comprises dans les rôles de l'impôt sur le revenu des personnes "
              "physiques émis ou à émettre au titre de l'année 1962 sont majorées de 5 % lorsque "
              "le revenu servant de base à l'imposition est supérieur à 8.000 F par part de "
              "revenu » ; elle « a rétabli cette imposition au taux réduit de 5 points et pour "
              "les seuls contribuables dont le revenu dépasse 8.000 F par part » ("
              + _R["1963-1964/23"] + ", p. 66) ; l'IPP l'applique au revenu entier"},
    {"annee": 1968, "monnaie": "FRF",
     "paliers": [[6000, 0.0], [7000, 0.02], [8000, 0.04], [9000, 0.06], [10000, 0.08],
                 [10500, 0.1], [12000, 0.12], [14000, 0.14]], "taux_au_dela": 0.15,
     "origine": "rapport",
     "texte": LOI_POUR_1969 + " : « cotisations comprises entre 6.001 F et 7.000 F : + 2 % [...] "
              "10.001 F et 10.500 F : + 10 % ; 10.501 F et 12.000 F : + 12 % ; 12.001 F et "
              "14.000 F : + 14 % ; cotisations supérieures à 14.000 F : + 15 % » ; la note de "
              "l'IPP les fait aller par paliers de 1 000 F, 10 % jusqu'à 11 000 F"},
    *COMPLEMENTS["majorations_exceptionnelles"],
]

#: LA TAXE COMPLÉMENTAIRE, que l'IPP ne porte pas : un impôt « à titre
#: temporaire » sur les revenus autres que les salaires et les pensions, dû
#: avec l'impôt sur le revenu et déductible de son revenu global (loi n°
#: 59-1472, art. 18 du texte du Sénat), des revenus de 1959 à ceux de 1969.
#: Chaque marche porte son taux, celui des artisans (``taux_artisans``) quand
#: il diffère, les abattements à la base des bénéfices industriels,
#: commerciaux et agricoles (``abattement``), de ceux des artisans et des
#: professions non commerciales (``abattement_bnc_et_artisans``), et ce que
#: les deux exonèrent au plus pour un même contribuable
#: (``abattement_maximum``). La marche de 1959, en francs de 1960 (cent
#: anciens francs, ordonnance n° 58-1341 du 27 décembre 1958), sert la taxe que
#: le contribuable paie en 1960 et déduit de ses revenus de 1960.
ABATTEMENTS_DE_1959 = ("« La taxe ne porte que sur la partie des revenus imposables qui dépasse "
                       "300.000 francs ou 440.000 francs suivant les distinctions afférentes aux "
                       "diverses catégories de revenus actuellement prévues, pour l'application du "
                       "taux réduit de la taxe proportionnelle, à l'article premier du décret n° "
                       "55-466 du 30 avril 1955 » (art. 18, 2) : « 300.000 francs en ce qui "
                       "concerne les revenus fonciers, les bénéfices des professions industrielles "
                       "et commerciales, les produits des charges et offices, les bénéfices de "
                       "l'exploitation agricole » et les rémunérations de certains gérants, "
                       "« 440.000 francs en ce qui concerne les bénéfices des artisans ainsi que "
                       "les bénéfices des professions non commerciales à l'exception des charges "
                       "et offices. En aucun cas, le montant total des revenus exonérés du fait de "
                       "l'abattement à la base ne pourra être supérieur à 440.000 francs pour un "
                       "même contribuable » (" + _R["1959-1960/24"] + ", p. 86)")
TAXE_COMPLEMENTAIRE = [
    {"annee": 1959, "monnaie": "FRF", "taux": 0.09, "abattement": 3000,
     "abattement_bnc_et_artisans": 4400, "abattement_maximum": 4400, "origine": "loi",
     "texte": _texte("59-1472", "art. 18 et 22 du texte du Sénat", "« il est établi, à compter "
                     "du 1er janvier 1960 et au plus tard jusqu'au 1er janvier 1962, une taxe "
                     "complémentaire qui frappe les revenus des personnes physiques autres que : "
                     "1° Les traitements, salaires, indemnités, émoluments, pensions et rentes "
                     "viagères » (art. 18, 1) ; " + ABATTEMENTS_DE_1959 + " ; « en ce qui "
                     "concerne les revenus des personnes physiques de l'année 1959, [...] le taux "
                     "de la taxe visée à l'article 19 [est porté] de 8 à 9 % » (art. 22, que le "
                     "Sénat vote conforme, au texte de l'Assemblée nationale que reproduit le "
                     "même rapport, p. 89)")},
    {"annee": 1960, "monnaie": "FRF", "taux": 0.08, "abattement": 3000,
     "abattement_bnc_et_artisans": 4400, "abattement_maximum": 4400, "origine": "loi",
     "texte": _texte("59-1472", "art. 19 du texte du Sénat", "« La taxe visée à l'article "
                     "précédent est calculée au taux de 8 % » ; codifié à l'article 204 sexies, "
                     "et les abattements de l'article 18, 2, à l'article 204 bis")},
    {"annee": 1961, "monnaie": "FRF", "taux": 0.06, "abattement": 3000,
     "abattement_bnc_et_artisans": 4400, "abattement_maximum": 4400, "origine": "rapport",
     "texte": "Loi n° 61-1396 du 21 décembre 1961 (LF pour 1962), dont le texte définitif n'est "
              "pas lu, art. 18 bis du texte de l'Assemblée nationale, que reproduit le "
              + _R["1961-1962/53"] + ", p. 102, et dont la commission des finances du Sénat "
              "propose la suppression (p. 82) : « Le taux de la taxe complémentaire sur le "
              "revenu des personnes physiques, provisoirement maintenue, est ramené de 8 à 6 %. "
              "Le nouveau taux s'appliquera aux bénéfices et revenus réalisés à compter du 1er "
              "janvier 1961 » ; le budget de 1962 en compte l'allègement (« Taxe complémentaire "
              "ramenée de 8 à 6 % », p. 24), « Actuellement le taux de la taxe complémentaire "
              "étant de 6 % » (" + _R["1962-1963/106"] + ", p. 77)"},
    {"annee": 1964, "monnaie": "FRF", "taux": 0.06, "taux_artisans": 0.03, "abattement": 3000,
     "abattement_bnc_et_artisans": 4400, "abattement_maximum": 4400, "origine": "loi",
     "texte": _texte("64-1279", "art. 3, voté conforme (« Art. 3 à 5. Conformes »), au texte de "
                     "l'Assemblée nationale que reproduit le " + _R["1964-1965/23"] + ", p. 64",
                     "« Le taux de 6 % prévu à l'article 204 sexies du Code général des impôts "
                     "est ramené à 3 % en ce qui concerne les bénéfices réalisés par les artisans "
                     "visés à l'article 1649 quater A du même Code. Le nouveau taux trouve sa "
                     "première application pour l'imposition des bénéfices de l'année 1964 »")},
    {"annee": 1965, "monnaie": "FRF", "taux": 0.06, "taux_artisans": 0.0, "abattement": 3000,
     "abattement_bnc_et_artisans": 4400, "abattement_maximum": 4400, "origine": "loi",
     "texte": _texte("65-997", "art. 4, voté conforme (« Art. 3 et 4. Conformes »), au texte de "
                     "l'Assemblée nationale que reproduit le " + _R["1965-1966/31"] + ", p. 60 "
                     "et 95", "« La taxe complémentaire cesse de s'appliquer aux bénéfices "
                     "réalisés par les contribuables considérés comme artisans pour l'application "
                     "de la législation fiscale [...] pour l'imposition des bénéfices de l'année "
                     "1965 »")},
    {"annee": 1968, "monnaie": "FRF", "taux": 0.06, "taux_artisans": 0.0, "abattement": 4000,
     "abattement_bnc_et_artisans": 4400, "abattement_maximum": 4400, "origine": "loi",
     "texte": "Loi n° 68-1172 du 27 décembre 1968 (LF pour 1969), art. 3, que le Sénat vote "
              "conforme en première lecture le 5 décembre 1968 (« Art. 3 et 4. Conformes », "
              "senat.fr/leg/1968-1969/ta1968_1969_0023.pdf), au texte de l'Assemblée nationale "
              "que reproduit le " + _R["1968-1969/40"] + ", p. 127 : « En ce qui concerne les "
              "bénéfices industriels et commerciaux, les bénéfices de l'exploitation agricole, "
              "les produits des charges et offices, les rémunérations des dirigeants de sociétés "
              "visées à l'article 62 du Code général des impôts et les revenus fonciers, la taxe "
              "complémentaire ne porte que sur la partie du revenu imposable qui dépasse "
              "4.000 F » ; l'abattement « de 4.400 F pour les bénéfices des professions non "
              "commerciales » reste (p. 73), et la moins-value se compte au budget de 1969, sur "
              "les revenus de 1968 (p. 29)"},
    {"annee": 1969, "monnaie": "FRF", "taux": 0.06, "taux_artisans": 0.0, "abattement": 30000,
     "abattement_bnc_et_artisans": 30000, "abattement_maximum": 30000, "origine": "loi",
     "texte": _loi(1969, "art. 5, II", "« Pour l'imposition des revenus de l'année 1969, la taxe "
                   "ne frappe que la fraction des revenus qui excède 30.000 F »")},
    {"annee": 1970, "supprimee": True,
     "texte": _loi(1969, "art. 5, I", "« La taxe complémentaire est supprimée à compter de "
                   "l'imposition des revenus de l'année 1970 »")},
]

#: L'instruction qui commente chaque année les limites d'exonération, et dit
#: que le 2° de l'article 5 ne trouvera pas à s'appliquer, le minimum garanti
#: étant sous elles : pour l'année des revenus, sa référence, son numéro, son
#: document aux archives du BOFiP (bofip-archives.impots.gouv.fr) et le montant
#: qu'elle écrit.
INSTRUCTIONS_DU_MINIMUM_GARANTI = {
    1999: ("BOI 5 B-5-00 (B.O.I. n° 11 du 17 janvier 2000)", 7, 20154, 38320, "38 320 F"),
    2000: ("BOI 5 B-9-01 (B.O.I. n° 44 du 2 mars 2001)", 9, 20135, 38650, "38 650 F"),
    2001: ("BOI 5 B-3-02 (B.O.I. n° 18 du 25 janvier 2002)", 9, 20104, 5994.55, "5 994,55 €"),
    2002: ("BOI 5 B-6-03 (B.O.I. n° 16 du 27 janvier 2003)", 9, 20063, 6094, "6 094 €"),
    2003: ("BOI 5 B-8-04 (B.O.I. n° 37 du 25 février 2004)", 8, 20036, 6187.88, "6 187,88 €"),
    2004: ("BOI 5 B-9-05 (B.O.I. n° 33 du 18 février 2005)", 7, 20005, 6302.28, "6 302,28 €"),
    2005: ("BOI 5 B-6-06 (B.O.I. n° 8 du 18 janvier 2006)", 7, 19924, 6416.68, "6 416,68 €"),
    2006: ("B.O.I. n° 47 du 29 mars 2007", 57, 19821, 6531, "6 531 €"),
    2007: ("BOI 5 B-11-08 (B.O.I. n° 28 du 4 mars 2008)", 7, 19764, 6635, "6 635 €"),
    2008: ("BOI 5 B-9-09 (B.O.I. n° 35 du 31 mars 2009)", 7, 19717, 6805, "6 805 €"),
    2009: ("BOI 5 B-13-10 (B.O.I. n° 22 du 16 février 2010)", 7, 19600, 6885, "6 885 €"),
    2010: ("BOI 5 B-7-11 (B.O.I. n° 26 du 28 mars 2011)", 8, 19562, 6885, "6 885 €"),
}


#: Les notes du code qui chiffrent le minimum garanti de 2000 et de 2001.
NOTES_DU_MINIMUM_GARANTI = {
    2000: "CGI, art. 5, 2°, LEGIARTI000006307020, note (1) : « Au titre de 2000, le montant "
          "s'élève à 38 650 F »",
    2001: "CGI, art. 5, 2°, LEGIARTI000006307021, note : « Au titre de 2001, le montant du "
          "minimum garanti s'élève à 5 994,55 euros »",
}


def _minimum_de_l_instruction(annee: int) -> dict:
    """La marche du minimum garanti qu'une instruction chiffre, et la note du
    code qui le chiffre aussi."""
    reference, numero, document, montant, ecrit = INSTRUCTIONS_DU_MINIMUM_GARANTI[annee]
    instruction = (f"{reference}, n° {numero} (bofip-archives, document {document}) : « le 2° "
                   f"de l'article 5 ne trouvera pas à s'appliquer pour l'imposition des revenus "
                   f"de {annee} [...] le montant du minimum garanti pour {annee} ({ecrit}) est "
                   f"inférieur aux [...] limites d'exonération »")
    note = NOTES_DU_MINIMUM_GARANTI.get(annee)
    return {"annee": annee, "monnaie": "FRF" if annee <= 2000 else "EUR", "montant": montant,
            "origine": "legi" if note else "doctrine",
            "texte": f"{note} ; {instruction}" if note else instruction}


#: Le minimum garanti de la documentation de base, pour les revenus de 1993 à
#: 1998.
DB_5_B_131 = {1993: 35400, 1994: 35990, 1995: 36520, 1996: 37520, 1997: 37770, 1998: 38080}


def _minimum_de_la_documentation(annee: int) -> dict:
    """La marche du minimum garanti que la documentation de base chiffre."""
    ecrit = f"{DB_5_B_131[annee]:,}".replace(",", " ")
    return {"annee": annee, "monnaie": "FRF", "montant": DB_5_B_131[annee], "origine": "doctrine",
            "texte": "DB 5 B 131 du 1er septembre 1999, n° 2 (bofip-archives, document 27837) : "
                     "« le montant annuel du “minimum garanti” auquel doit être comparé le revenu "
                     f"global du contribuable s'élève à : [...] {ecrit} F pour les revenus "
                     f"imposables au titre de {annee} »"}

#: L'exonération de l'article 5, 2°, du code, que l'IPP ne porte pas : qui vit
#: principalement de salaires, de pensions et de rentes viagères n'est pas
#: imposé si son revenu global n'excède pas le montant annuel du minimum
#: garanti. Une marche porte ce ``montant`` quand un texte lu le chiffre ; une
#: marche sans montant est une année où l'exonération vaut sans que son montant
#: soit lu.
MINIMUM_GARANTI = [
    {"annee": 1960, "origine": "loi",
     "texte": _texte("59-1472", "art. 13 du texte du Sénat, dernier alinéa", "« Les "
                     "contribuables salariés dont l'unique revenu n'est pas supérieur au salaire "
                     "minimum interprofessionnel garanti ne sont pas assujettis à l'impôt sur le "
                     "revenu des personnes physiques » ; ni le montant annuel de ce salaire, ni "
                     "le texte qui étend l'exonération aux pensions et aux rentes viagères, au "
                     "2° de l'article 5 du code, ne sont lus")},
    {"annee": 1971, "monnaie": "FRF", "montant": 7440, "origine": "rapport",
     "texte": RAPPORTS[1972] + ", p. 11 : « conformément aux dispositions de l'article 5-2° du "
              "Code général des Impôts, les contribuables dont le revenu, constitué "
              "principalement par des salaires, pensions ou rentes viagères, n'est pas supérieur "
              "au S. M. I. C., sont exonérés d'impôt sur le revenu. C'est ainsi que pour l'année "
              "1971 le seuil d'imposition a été, par application de cette disposition, fixé à "
              "7.440 F »"},
    {"annee": 1972, "origine": "legi",
     "texte": "CGI, art. 5, 2°, dans ses rédactions de 1979 à 2002, LEGIARTI000006307017 à "
              "LEGIARTI000006307020 : « Les personnes "
              "physiques qui bénéficient principalement de traitements, salaires, pensions et "
              "rentes viagères et dont le revenu global n'est pas supérieur au montant du "
              "minimum garanti prévu à l'article L 141-8 du code du travail » — qui remplace le "
              "SMIG dans toutes les dispositions qui s'y réfèrent depuis la loi n° 70-7 du "
              "2 janvier 1970 (LEGIARTI000006646471) ; le montant des revenus de 1972 à 1992 "
              "n'est pas lu"},
    *[_minimum_de_la_documentation(annee) for annee in DB_5_B_131],
    *[_minimum_de_l_instruction(annee) for annee in INSTRUCTIONS_DU_MINIMUM_GARANTI],
    {"annee": 2011, "origine": "legi",
     "texte": "CGI, art. 5, 2°, LEGIARTI000024189626 à LEGIARTI000029042469 : le montant des "
              "revenus de 2011 à 2013 n'est pas lu"},
    {"annee": 2014, "supprimee": True,
     "texte": "la dernière rédaction de l'article 5 qui porte le 2°, LEGIARTI000029042469, est "
              "close le 1er janvier 2015, et l'index LEGI n'a pas la suivante ; l'IPP fait finir "
              "le 2° bis avec les revenus de 2013, par la loi n° 2014-1654 du 29 décembre 2014 "
              "(LF pour 2015), art. 2, qu'aucun des deux index n'a"},
]

#: L'abattement de 10 % des pensions naît des revenus de 1977 : avant, une
#: pension n'a que les 20 % (voir :func:`_pensions_avant_1977`).
PREMIERE_ANNEE_ABATTEMENT_DES_PENSIONS = 1977
PENSIONS_AVANT_1977 = (
    "sans l'abattement de 10 % des pensions, que la loi de finances pour 1979 (art. 4) dit "
    "« institué par l'article 3-1 de la loi n° 77-1467 du 30 décembre 1977 » pour les revenus "
    "de 1977 : « Les contribuables titulaires de pensions ou de retraites sont autorisés à "
    "pratiquer [...] un abattement de 10 % » (" + _loi(1977, "art. 3, I") + ")")

#: Les années de la limite d'exonération que l'IPP ne chiffre pas, comblées
#: par la règle d'indexation de la loi de finances pour 1982 (art. 12, III, 3,
#: LEGIARTI000006273482).
ANNEES_D_EXONERATION_INDEXEES = (1982, 1983, 1989)

#: Le seuil de mise en recouvrement que la loi chiffre, quand le code ne le
#: fait pas.
RECOUVREMENT_DES_LOIS = {
    1978: (165, _loi(1978, "art. 2, VI, 1", "« Pour les cotisations perçues en 1979, cette "
                     "somme est fixée à 165 F »")),
}

#: Deux mesures d'une seule année que l'IPP ne porte pas, lues dans le
#: commentaire de l'administration, qui cite la loi : aucun des deux index n'a
#: l'article de loi de finances rectificative qui les crée.
REDUCTION_PROPORTIONNELLE = [
    {"annee": 2001, "monnaie": "EUR", "taux": 0.05, "origine": "doctrine",
     "texte": "Loi n° 2002-1050 du 6 août 2002 (LFR pour 2002), art. 1 ; BOI 5 B-6-03, n° 1 : "
              "« Une réduction de 5 % de l'impôt sur le revenu au titre des revenus 2001, "
              "pratiquée sur les droits bruts après application des effets du plafonnement du "
              "quotient familial et de la décote mais avant imputation des réductions et "
              "crédits d'impôt, de la prime pour l'emploi et de l'avoir fiscal »"},
    {"annee": 2002, "supprimee": True,
     "texte": "BOI 5 B-6-03, n° 1 : une réduction « au titre des revenus 2001 »"},
]
CREDIT_EXCEPTIONNEL = [
    {"annee": 2008, "monnaie": "EUR", "taux": 2 / 3, "revenu_par_part_plein": 11673,
     "revenu_par_part_maximum": 12475, "origine": "doctrine",
     "texte": "Loi n° 2009-431 du 20 avril 2009 (LFR pour 2009), art. 1, reproduit à l'annexe 1 "
              "du BOI 5 B-25-09 : « dont le revenu imposable par part [...] est inférieur à "
              "12 475 € [...] aux deux tiers de l'impôt calculé conformément aux 1 à 4 du I de "
              "l'article 197 [...] pour les contribuables dont le revenu net imposable par part "
              "n'excède pas 11 673 € [...] décroissant linéairement [...] S'il excède l'impôt "
              "dû, l'excédent est restitué »"},
    {"annee": 2009, "supprimee": True,
     "texte": "BOI 5 B-25-09, n° 2 : « limité à l'imposition des revenus de 2008 »"},
]

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


def _pensions_avant_1977(serie: list[dict]) -> list[dict]:
    """Les déductions des revenus d'avant 1977 sans l'abattement de 10 % des
    pensions, que l'IPP leur donne dès 1960 (:data:`PENSIONS_AVANT_1977`)."""
    sortie = []
    for marche in serie:
        if marche["annee"] < PREMIERE_ANNEE_ABATTEMENT_DES_PENSIONS and "pensions_taux" in marche:
            marche = {cle: valeur for cle, valeur in marche.items() if cle != "pensions_taux"}
            marche.update(origine="loi", texte=f"{marche['texte']} ; {PENSIONS_AVANT_1977}")
        sortie.append(marche)
    return sortie


def _indexer_exoneration(serie: list[dict], bareme: list[dict]) -> list[dict]:
    """Comble les années de la limite d'exonération que l'IPP ne chiffre pas
    (:data:`ANNEES_D_EXONERATION_INDEXEES`) par la règle de la loi de finances
    pour 1982 (art. 12, III, 3 : « relevés chaque année dans la même proportion
    que la limite supérieure de la première tranche du barème [...] arrondis
    [...] à la centaine de francs supérieure en ce qui concerne les plafonds de
    ressources »). Partie de 1981, elle retrouve les 31 800 F et 34 700 F de
    1984 ; partie de 1988, les 39 300 F et 42 800 F de 1990."""
    sortie = list(serie)
    for annee in ANNEES_D_EXONERATION_INDEXEES:
        precedente = [m for m in sortie if m["annee"] < annee and "limite" in m][-1]
        rapport = (_limite_premiere_tranche(bareme, annee)
                   / _limite_premiere_tranche(bareme, precedente["annee"]))
        calculee = {
            "annee": annee, "monnaie": precedente["monnaie"],
            "limite": _arrondi_superieur(precedente["limite"] * rapport, 100),
            "limite_plus_de_65_ans": _arrondi_superieur(
                precedente["limite_plus_de_65_ans"] * rapport, 100),
            "texte": ("Loi n° 81-1160 du 30 décembre 1981 (LF pour 1982), art. 12, III, 3, "
                      "LEGIARTI000006273482 : règle d'indexation appliquée aux limites de "
                      f"{precedente['annee']} ; l'IPP n'en a pas"),
            "origine": "indexation",
        }
        sortie = sorted([m for m in sortie if m["annee"] != annee] + [calculee],
                        key=lambda m: m["annee"])
    return sortie


def _recouvrement_avant_2002(bareme: list[dict]) -> list[dict]:
    """Le seuil de mise en recouvrement de 1970 à 2001. Les années que le code
    ne chiffre pas suivent la loi de finances qui le fait (1978), ou sa règle :
    « relevée chaque année dans la même proportion que la première tranche du
    barème » (LEGIARTI000006312651), la première tranche imposée, arrondie aux
    5 F supérieurs jusqu'en 1984 et aux 10 F ensuite : ainsi se retrouvent les
    valeurs publiées de 1991 (440 F) et de 1992 (460 F)."""
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
        elif annee in RECOUVREMENT_DES_LOIS:
            seuil, texte = RECOUVREMENT_DES_LOIS[annee]
            sortie.append({"annee": annee, "monnaie": "FRF", "seuil": seuil, "texte": texte,
                           "origine": "loi"})
        elif 1985 <= annee <= 1990:
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
    for (nom, annee), (valeurs, texte, origine) in CORRECTIONS.items():
        marche = next(m for m in series[nom] if m["annee"] == annee)
        marche.update(valeurs)
        marche["origine"] = origine
        marche["texte"] = f"{marche['texte']} ; {texte}"
    series["reduction_proportionnelle"] = [dict(m) for m in REDUCTION_PROPORTIONNELLE]
    series["credit_exceptionnel"] = [dict(m) for m in CREDIT_EXCEPTIONNEL]
    series["reduction_des_salaires"] = [dict(m) for m in REDUCTION_DES_SALAIRES]
    series["taxe_complementaire"] = [dict(m) for m in TAXE_COMPLEMENTAIRE]
    series["minimum_garanti"] = [dict(m) for m in MINIMUM_GARANTI]
    for nom, complements in COMPLEMENTS.items():
        annees = {m["annee"] for m in complements}
        series[nom] = sorted([m for m in series[nom] if m["annee"] not in annees] + complements,
                             key=lambda m: m["annee"])
    series["abattement_age_invalidite"] = _indexer_age_invalidite(
        series["abattement_age_invalidite"], bareme)
    series["exoneration"] = _indexer_exoneration(series["exoneration"], bareme)
    series["deductions"] = _pensions_avant_1977(series["deductions"])
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
        {"annee": annee, "parts": list(parts), "texte": texte, "origine": origine}
        for annee, parts, texte, origine in PARTS_PAR_RANG_D_ENFANT]
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
# qu'il écrit, `note_ipp` pour une règle que seules les notes de l'IPP datent,
# `doctrine` pour une valeur que l'administration publie (documentation de
# base, Bulletin officiel des impôts) quand aucun des index de la DILA n'a la
# loi de finances qui la porte, `loi` pour une valeur lue au texte définitif
# d'une loi que le Sénat a adopté (senat.fr/leg/), ou à celui de sa première
# lecture quand les deux assemblées y ont voté l'article dans les mêmes termes,
# quand l'index LEGI n'en garde pas la rédaction d'origine, `rapport` pour une
# valeur que seul un rapport de la commission des finances du Sénat chiffre
# (senat.fr/rap/) : la loi qu'il a rejetée, la table que la loi « maintient »,
# le décret qu'une loi annonce.
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
#   reduction_des_salaires : des revenus de 1960 à ceux de 1971, la réduction
#     d'impôt des salaires et des pensions (art. 198), `taux` de leur montant
#     net imposable — le barème porte autant de points de plus —, et, de 1969
#     à 1971, celle des contribuables âgés, `taux_agees` de leur revenu
#     imposable, au plus `plafond_agees` ; la plus forte des deux est seule
#     retenue.
#   decote : son taux et ses seuils, dont le sens a changé six fois (le module
#     dit lequel vaut à chaque époque) ; de 1960 à 1972, les limites de
#     l'exonération et de la décote de l'article 198 ter, en impôt, pour le
#     foyer (`franchise`, `limite`) jusqu'à `parts_forfait` parts, par part
#     au-delà (`_par_part`) — dès la première part, sans `parts_forfait` —, et
#     celles des contribuables âgés ou invalides (`_majoree`).
#   reduction_sous_condition_de_revenus : de 2016 à 2019.
#   recouvrement : le seuil de mise en recouvrement, avant et après crédits.
#   exoneration : la limite d'exonération, de 1973 à 2013, sous laquelle le
#     revenu du foyer, net de frais professionnels, n'est pas imposé : la
#     limite, celle des plus de 65 ans ; de 1973 à 1976, `limite` ne vaut que
#     pour qui vit principalement de salaires et de pensions, `limite_autres`
#     pour les autres ; en 1972, celle de qui vit principalement de salaires,
#     sur son revenu brut.
#   minimum_garanti : le montant annuel du minimum garanti de l'article 5, 2°,
#     sous lequel le revenu global de qui vit principalement de salaires, de
#     pensions et de rentes viagères n'est pas imposé (`montant`) ; une marche
#     sans montant, une année où l'exonération vaut sans que son montant soit
#     lu : de 1960 à 1970, sous le salaire minimum de la loi n° 59-1472, de
#     1972 à 1992, de 2011 à 2013.
#   deductions : les 10 % des salaires et des pensions, les 20 % d'avant 2006.
#   abattement_age_invalidite : celui de l'article 157 bis, plein sous le
#     premier seuil de revenu net global, réduit sous le second ; en 1972, la
#     déduction de 500 F, sous un revenu « inférieur » au seuil
#     (`seuil_plein_exclu`).
#   abattement_exceptionnel_* : les deux compléments de 1978.
#   majorations_exceptionnelles, minorations_exceptionnelles : leurs seuils et
#     leurs taux, et la note de l'IPP qui dit comment ils s'appliquent ; ou,
#     dès 1968, leurs `paliers` : la cotisation jusqu'à laquelle chaque
#     taux vaut, et le `taux_au_dela` des majorations ; les réductions de 1966
#     et de 1967, par tranche du revenu imposable (`paliers_de_revenu`), sans
#     limite au-delà de `parts_sans_limite` parts ; le demi-décime de 1962,
#     au-delà d'un revenu par part (`seuil_revenu_par_part`) ; les `decotes` de
#     la majoration de 1967 : comprise entre deux montants, elle est réduite de
#     la différence entre le second et elle.
#   reduction_exceptionnelle : celle des revenus de 2013.
#   reduction_proportionnelle : les 5 % retranchés de l'impôt des revenus de
#     2001, après la décote, avant les crédits d'impôt.
#   prime_pour_l_emploi : de 2000 à 2014.
#   credit_exceptionnel : celui des revenus de 2008, les deux tiers de l'impôt
#     sous le premier seuil de revenu par part, dégressif jusqu'au second.
#   taxe_complementaire : des revenus de 1959 à ceux de 1969, la taxe des
#     revenus autres que les salaires et les pensions : son `taux`, celui des
#     artisans (`taux_artisans`) quand il diffère, l'abattement à la base des
#     bénéfices industriels, commerciaux et agricoles (`abattement`), celui des
#     artisans et des professions non commerciales
#     (`abattement_bnc_et_artisans`), et ce que les deux exonèrent au plus pour
#     un même contribuable (`abattement_maximum`) ; la marche de 1959, en
#     francs de 1960, sert la taxe payée en 1960, que le revenu de 1960 déduit.
"""

ORDRE = ("bareme", "quotient_familial", "parts_par_rang_d_enfant",
         "plafonds_quotient_familial", "reduction_des_salaires", "decote",
         "reduction_sous_condition_de_revenus",
         "recouvrement", "exoneration", "minimum_garanti", "deductions",
         "abattement_age_invalidite",
         "abattement_exceptionnel_ages_invalides", "abattement_exceptionnel_personnes_seules",
         "majorations_exceptionnelles", "minorations_exceptionnelles",
         "reduction_exceptionnelle", "reduction_proportionnelle", "prime_pour_l_emploi",
         "credit_exceptionnel", "taxe_complementaire")


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
