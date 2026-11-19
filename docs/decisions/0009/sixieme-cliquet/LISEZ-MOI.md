# Le sixième cliquet de la note 0009 : ses comptes

L'amendement du 19 novembre 2026, à la fin de la note de décision 0009, ajoute
un sixième cliquet : l'alarme « loi modifiée », et la version que doit avoir
chaque réforme qu'une fiche déclare. `mesures.py` refait ses comptes, sur la
carte des règles et la liste de contrôle des textes, sans rien modifier :

    python docs/decisions/0009/sixieme-cliquet/mesures.py 2026-11-19

Un couple « sans réponse » est celui d'une fiche et d'une rédaction en vigueur
ou à venir d'un article qu'elle cite, que la fiche ne compte dans aucune de
ses versions et ne déclare pas sans effet. La liste bouge chaque lundi, quand
GitHub y inscrit les rédactions nouvelles de l'index LEGI : l'étape qui pose
le cliquet refait les comptes ce jour-là.

Sa sortie du 19 novembre 2026, sur la liste lue dans l'index le 16 :

```
Au 2026-11-19 : 267 fiches, dont 70 sans version.
Liste : 18012 rédactions, {'a_examiner': 6015, 'a_rattacher': 655, 'rattachee': 1974, None: 9223, 'sans_effet': 145}

1. Couples sans réponse : 518, pour 146 fiches et 362 rédactions.
   La fiche cite la rédaction sans l'avoir coupée en version : 435 (dont dans une fiche sans version : 269).
   La fiche n'en dit rien : 83, pour 51 fiches et 48 rédactions ; qu'une autre fiche a rattachée : 82.
   Parmi elles, rédactions qui commencent en 2026 ou après : 18, pour 32 couples.
     rural L732-63, du 2026-01-01 (LEGIARTI000053280353) : relevement_des_exploitants_2023
     rural D732-111, du 2026-01-01 (LEGIARTI000053365711) : relevement_des_exploitants_2023
     rural D731-121, du 2026-01-01 (LEGIARTI000053296666) : pension_non_salaries_agricoles_2026
     rural D732-114, du 2026-01-01 (LEGIARTI000053365740) : majoration_retraite_proportionnelle
     rural L732-56, du 2026-01-01 (LEGIARTI000051289591) : relevement_des_exploitants_2023
     decret_79_262 2, du 2026-07-01 (LEGIARTI000054168526) : cotisation_par_classes_liberales
     css R351-27, du 2026-08-01 (LEGIARTI000054589995) : cultes_fractions_de_pension, duree_requise_par_generation, taux_plein_a_soixante_cinq_ans
     css D351-2-2, du 2026-08-01 (LEGIARTI000054589231) : cultes_fractions_de_pension
     decret_2003_1306 20, du 2026-08-01 (LEGIARTI000054590030) : retraite_anticipee_handicap, retraite_pour_invalidite_fonction_publique, reversion_fonction_publique
     decret_2003_1306 15, du 2026-10-14 (LEGIARTI000054978195) : bonification_cinquieme_sapeurs_pompiers, majoration_duree_sapeurs_pompiers_volontaires, taux_maximum_fonction_publique
     decret_2004_1056 12, du 2026-10-14 (LEGIARTI000054978200) : enfants_fonction_publique, majoration_duree_sapeurs_pompiers_volontaires, taux_maximum_fonction_publique
     marins R8-1, du 2026-10-14 (LEGIARTI000054978160) : majoration_duree_sapeurs_pompiers_volontaires
     rural R732-61, du 2026-10-14 (LEGIARTI000054978170) : bareme_minoration_regimes_en_points, majoration_duree_sapeurs_pompiers_volontaires, pension_non_salaries_agricoles_2026, retraite_proportionnelle_msa
     decret_2017_1000 3, du 2026-10-14 (LEGIARTI000054978205) : majoration_duree_sapeurs_pompiers_volontaires
     css R351-12, du 2026-11-01 (LEGIARTI000054425288) : conge_supplementaire_naissance, sportifs_haut_niveau, taux_plein_a_soixante_cinq_ans
     arrete_2012_02_09 27, du 2027-01-01 (LEGIARTI000054908896) : versement_unique_rci
     arrete_2012_02_09 39, du 2027-01-01 (LEGIARTI000054908885) : seconde_pension
     arrete_2012_02_09 41, du 2027-01-01 (LEGIARTI000054908882) : organic_conjoints_de_commercants, reversion_rci
   La veille d'aujourd'hui en montre : 1 fiche(s).
   Rédactions d'articles cités, par mois de début : {'2026-01': 104, '2026-02': 2, '2026-05': 9, '2026-06': 3, '2026-07': 37, '2026-08': 17, '2026-09': 5, '2026-10': 8, '2026-11': 6, '2027-01': 11, '2028-01': 3, '2999-01': 3}

2. 65 fiches déclarent 136 couples fiche-réforme (23 de ces fiches sans version).
     49  la fiche n'a pas de version
           age_annulation_decote / reforme_2023 (2023-09-01) ; versions : aucune
           age_legal_par_generation / reforme_2023 (2023-09-01) ; versions : aucune
           age_legal_par_generation / lfss_2026_suspension (2026-09-01) ; versions : aucune
     40  une version commence à la date
           age_ouverture_ieg_actifs / regimes_speciaux_2008 (2008-07-01) ; versions : 2008-07-01, 2011-03-21, 2025-01-01
           age_reference_decote_sncf_ratp / regimes_speciaux_2008 (2008-07-01) ; versions : 2008-07-01, 2010-07-01, 2025-01-01
           age_surcote_sncf_ratp / regimes_speciaux_2008 (2008-07-01) ; versions : 2008-07-01, 2011-03-21, 2025-01-01
     30  aucune version ne commence cette année-là
           age_ouverture_ieg_actifs / speciaux_bornes_2017 (2017-01-01) ; versions : 2008-07-01, 2011-03-21, 2025-01-01
           age_ouverture_ieg_actifs / reforme_2023 (2023-09-01) ; versions : 2008-07-01, 2011-03-21, 2025-01-01
           age_ouverture_ieg_actifs / lfss_2026_suspension (2026-09-01) ; versions : 2008-07-01, 2011-03-21, 2025-01-01
     17  une version commence la même année, un autre jour
           age_surcote_sncf_ratp / woerth_2010 (2011-07-01) ; versions : 2008-07-01, 2011-03-21, 2025-01-01
           asv_medecins_points / asv_1972 (1972-10-27) ; versions : 1994-01-01, 2012-01-01, 2026-01-01
           carcdsf_minoration_age_seul / carcdsf_statuts_2007 (2007-10-10) ; versions : 2017-12-25, 2024-01-10, 2026-07-18
```
