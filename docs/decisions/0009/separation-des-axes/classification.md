# Les 144 champs de période, en quatre familles

Relevé du 22 novembre 2026 sur `main` à 389536e, relu sur Opus. Colonnes : le
nombre de régimes qui portent le champ, et de ceux où il change d'une période à
l'autre ; les lectures du moteur relevées en faisant tourner tous les témoins
avec un moteur instrumenté (« effet » : période choisie à la date d'effet ou
d'un fait de la liquidation ; « année » : période choisie à une année ;
« pont » : le Python qui demande une période à l'année ; entre parenthèses, le
nombre de sites) ; la remarque. Six champs n'ont pas de description dans
`_schema.yaml` (`assiette_grille`, `duree_proratisation_trimestres`,
`perimetre_taux`, `plafond_majoration_annee`, `smic_du_mois`,
`valeur_point_annee`) : leur classement vient du chargeur et du moteur.

## Liquidation (92 champs)

| Champ | Régimes | Où il change | Lectures | Remarque |
|---|---|---|---|---|
| `abattement_points` | 23 | 9 | année (1), effet (5) |  |
| `age_ouverture` | 80 | 28 | année (1), pont, à l'année (1), effet (7) |  |
| `age_ouverture_de_l_inapte` | 1 | 1 | pont, à l'année (1), effet (9) |  |
| `age_ouverture_par_generation` | 49 | 22 | pont, à l'année (1), effet (9) |  |
| `age_ouverture_services` | 2 | 0 | pont, à l'année (1), effet (9) |  |
| `age_sans_coefficient_de_l_inapte` | 5 | 4 | effet (1) |  |
| `age_surcote_regimes_speciaux` | 4 | 4 | effet (1) |  |
| `age_table` | 15 | 13 | pont, à l'année (1), année (3), effet (10) |  |
| `age_taux_plein` | 80 | 36 | année (3), effet (4) |  |
| `age_taux_plein_a_l_ouverture` | 2 | 2 | pont, à l'année (1), année (2), effet (5) |  |
| `age_taux_plein_femmes` | 2 | 2 | effet (1) |  |
| `age_taux_plein_par_generation` | 46 | 26 | pont, à l'année (1), année (2), effet (5) |  |
| `ajournement_par_annee_d_assurance` | 1 | 1 | effet (1) |  |
| `annuites_au_taux_de_leur_annee` | 1 | 0 | effet (1) | **Était à trancher ; recommandé :** l'indicateur reste en liquidation ; le poids de chaque annuité, qui tient à la date du mandat, devient un champ de cotisation propre au CESE (sa durée requise, 142 trimestres jusqu'au 31 août 2004, 149 ensuite) |
| `avantages_non_contributifs` | 80 | 28 | pont, à l'année (1), année (3), effet (16) | **Était à trancher ; recommandé :** liquidation, sans découpage : tout ce que le moteur en exploite passe par la ligne de liquidation ; periodes_assimilees n'a aucun lecteur |
| `bareme_anticipation` | 1 | 1 | effet (1) |  |
| `bareme_decote` | 10 | 10 | pont, à l'année (1), année (3), effet (12) |  |
| `bareme_trimestre` | 1 | 1 | effet (1) |  |
| `calcul_provisoire_non_salaries` | 1 | 1 | effet (1) |  |
| `capital_seuil_points` | 1 | 0 | pont, à l'année (1), effet (1) |  |
| `carriere_longue_minoree_de` | 1 | 1 | effet (1) |  |
| `carriere_longue_minoree_depuis_l_age` | 1 | 1 | effet (1) |  |
| `carriere_longue_minoree_jusqu_au_palier` | 1 | 1 | effet (1) |  |
| `categories_sans_coefficient` | 4 | 3 | effet (1) |  |
| `decote_annulee_par_la_duree` | 16 | 11 | pont, à l'année (1), effet (1) |  |
| `decote_palier_age` | 1 | 1 | effet (1) |  |
| `decote_par_generation` | 14 | 7 | pont, à l'année (1), année (1), effet (1) |  |
| `decote_par_la_duree_seule` | 2 | 2 | pont, à l'année (1), effet (1) |  |
| `decote_par_trimestre` | 80 | 25 | pont, à l'année (1), année (1), effet (1) |  |
| `decote_par_trimestre_apres_palier` | 1 | 1 | effet (1) |  |
| `decote_trimestres_maximum` | 5 | 3 | pont, à l'année (1), effet (1) |  |
| `duree_majoree_apres_taux_plein` | 5 | 4 | effet (1) |  |
| `duree_majoree_bornee_avec` | 3 | 2 | effet (1) |  |
| `duree_majoree_tous_regimes` | 5 | 4 | effet (1) |  |
| `duree_maximum_avant_age` | 1 | 0 | effet (1) |  |
| `duree_maximum_avant_age_trimestres` | 1 | 0 | effet (1) |  |
| `duree_maximum_levee_age` | 1 | 0 | effet (1) |  |
| `duree_maximum_levee_trimestres` | 1 | 0 | effet (1) |  |
| `duree_proratisation_par_generation` | 6 | 4 | pont, à l'année (1), effet (4) |  |
| `duree_proratisation_trimestres` | 1 | 1 | pont, à l'année (1), effet (4) |  |
| `duree_requise_calendrier` | 8 | 8 | pont, à l'année (1), effet (11) |  |
| `duree_requise_par_generation` | 47 | 26 | pont, à l'année (1), effet (11) |  |
| `duree_requise_table` | 12 | 12 | pont, à l'année (1), effet (11) |  |
| `duree_requise_trimestres` | 80 | 31 | année (3), pont, à l'année (1), effet (6) |  |
| `duree_taux_plein_femmes_regimes` | 2 | 2 | effet (1) |  |
| `duree_taux_plein_femmes_trimestres` | 2 | 2 | effet (1) |  |
| `ecretement_salaire_reference` | 1 | 0 | pont, à l'année (1), année (1), effet (1) |  |
| `effet_au_trimestre_civil` | 4 | 4 | effet (1) |  |
| `exercice_minimum_annees` | 1 | 1 | effet (1) |  |
| `fermee_a_la_carriere_longue` | 1 | 1 | effet (1) |  |
| `fractions_des_cultes` | 1 | 0 | effet (1) |  |
| `majoration_d_ajournement` | 2 | 2 | année (1), effet (1) |  |
| `meilleures_annees_non_salaries` | 1 | 1 | effet (2) |  |
| `part_au_dela_du_plafond` | 1 | 0 | effet (1) |  |
| `pension_bornee_au_minimum_avec` | 3 | 2 | effet (1) |  |
| `pension_bornee_au_minimum_entier_avec` | 2 | 2 | effet (1) |  |
| `pension_speciale_age_sans_autre_pension` | 1 | 0 | pont, à l'année (1), effet (9) |  |
| `pension_speciale_services_annees` | 1 | 0 | pont, à l'année (1), effet (9) |  |
| `plafond_en_traitements_de_l_indice_100` | 1 | 0 | effet (1) |  |
| `plafond_majoration_regime` | 7 | 1 | effet (2) |  |
| `points_gratuits` | 1 | 0 | effet (2) |  |
| `regles_du_salaire_annuel_moyen` | 6 | 2 | pont, à l'année (1), année (1), effet (1) |  |
| `salaire_reference` | 80 | 9 | année (2), pont, à l'année (1), effet (1) |  |
| `salaire_reference_par_generation` | 7 | 5 | pont, à l'année (1), effet (1) |  |
| `services_ouverture_annees` | 2 | 0 | effet (3) |  |
| `surcote_affiliation_minimale_trimestres` | 1 | 1 | effet (1) |  |
| `surcote_age_debut` | 4 | 4 | effet (1) |  |
| `surcote_age_legal_de_la_base_jusqu_a_la_generation` | 1 | 1 | effet (1) |  |
| `surcote_age_maximum` | 4 | 4 | effet (1) |  |
| `surcote_bareme` | 11 | 10 | effet (1) |  |
| `surcote_depuis_l_age_legal` | 2 | 2 | effet (1) |  |
| `surcote_depuis_la_duree` | 1 | 1 | effet (1) |  |
| `surcote_du_trimestre_civil_suivant` | 2 | 2 | effet (1) |  |
| `surcote_palier_age` | 2 | 2 | effet (1) |  |
| `surcote_par_trimestre` | 80 | 29 | effet (1) |  |
| `surcote_par_trimestre_apres_palier` | 2 | 2 | effet (1) |  |
| `surcote_par_trimestre_d_avant` | 1 | 1 | effet (1) |  |
| `surcote_par_trimestre_depuis` | 1 | 1 | effet (1) |  |
| `surcote_pas_trimestres` | 3 | 3 | effet (1) |  |
| `surcote_points` | 14 | 13 | effet (1) |  |
| `surcote_premieres_annees` | 1 | 1 | effet (1) |  |
| `surcote_trimestres_civils_d_exercice` | 1 | 1 | effet (1) |  |
| `surcote_trimestres_cotises` | 2 | 2 | effet (1) |  |
| `surcote_trimestres_maximum` | 10 | 10 | effet (1) |  |
| `taux_majoration_enfants` | 10 | 0 | effet (1) |  |
| `taux_maximum_bonifie` | 3 | 2 | effet (1) |  |
| `taux_plein` | 80 | 4 | année (1), effet (2) |  |
| `taux_plein_anticipe_maximum_annees` | 1 | 1 | effet (1) |  |
| `taux_plein_anticipe_par_enfant_annees` | 1 | 1 | effet (1) |  |
| `trimestres_maximum` | 1 | 0 | année (1), effet (1) | **Était à trancher ; recommandé :** liquidation : le plafond s'applique sur la ligne de liquidation (acquerir.js:1146) ; la boucle annuelle ne fait que tester si l'année est plafonnable (acquerir.js:947), ce qu'elle peut lire sur la même ligne ; 120 sur les 22 périodes des mines, l'oracle ne bouge pas |
| `trimestres_maximum_leve_avant_age` | 1 | 0 | année (1) | **Était à trancher ; recommandé :** liquidation, de même (acquerir.js:960) ; 55 ans partout |
| `trimestres_retenus_maximum` | 2 | 2 | effet (1) |  |

## Cotisation (39 champs)

| Champ | Régimes | Où il change | Lectures | Remarque |
|---|---|---|---|---|
| `assiette` | 80 | 15 | pont, à l'année (2), année (10), effet (1) |  |
| `assiette_annee_de_revenu` | 2 | 2 | année (1) |  |
| `assiette_de_debut` | 1 | 1 | année (1) |  |
| `assiette_de_debut_en_bases_mensuelles` | 1 | 1 | année (1) |  |
| `assiette_facteur_revenu` | 3 | 0 | année (3) |  |
| `assiette_forfaitaire` | 3 | 1 | année (4), pont, à l'année (1), effet (1) |  |
| `assiette_grille` | 1 | 0 | année (3), pont, à l'année (1), effet (1) |  |
| `assiette_minimale_pass` | 2 | 2 | année (2) |  |
| `assiette_plancher` | 2 | 1 | année (2) |  |
| `assiette_repere_smic` | 5 | 4 | année (3), effet (1) |  |
| `bareme_points` | 1 | 1 | année (1), effet (1) | barème d'acquisition des points MSA ; lu aussi sur la ligne de liquidation pour le coefficient 37,5 / durée requise (liquider.js:371, 456) : lecture croisée |
| `borne_basse_euros` | 2 | 2 | année (6), pont, à l'année (1), effet (1) |  |
| `borne_basse_par_annee` | 2 | 2 | année (6), pont, à l'année (1), effet (1) |  |
| `borne_haute_euros` | 2 | 2 | année (6), pont, à l'année (1), effet (1) |  |
| `borne_haute_par_annee` | 2 | 2 | année (6), pont, à l'année (1), effet (1) |  |
| `cotisation_forfaitaire_annee` | 10 | 10 | année (3) |  |
| `cotisation_forfaitaire_euros` | 10 | 10 | année (3) |  |
| `cotisation_par_classes` | 4 | 2 | année (3) |  |
| `dispense_de_debut` | 2 | 2 | année (2) |  |
| `exemption_passe_l_age` | 1 | 1 | année (2) |  |
| `part_assurance_maladie_forfait` | 5 | 1 | année (3) |  |
| `part_assurance_maladie_taux` | 4 | 1 | année (3) |  |
| `part_salariale` | 31 | 13 | année (6) |  |
| `part_salariale_deplafonnee` | 5 | 5 | année (4) |  |
| `perimetre_taux` | 16 | 0 | année (3) | qualifie le taux (agent seul) |
| `plafond_primes_traitement` | 1 | 0 | année (4) |  |
| `points_abattus_a_l_age` | 1 | 1 | année (1) | marque les points ACQUIS dans la période (tranche C de l'Agirc jusqu'en 2015) |
| `points_ajustement_au_plafond` | 2 | 2 | année (1) |  |
| `points_ajustement_maximum` | 1 | 1 | année (1) |  |
| `points_ajustement_par_forfait` | 2 | 2 | année (1) |  |
| `points_au_prorata_des_cotisations` | 1 | 1 | année (1) |  |
| `points_invalidite` | 3 | 2 | année (1) | points d'une année d'invalidité, acquis l'année |
| `points_maximum` | 5 | 5 | année (1) |  |
| `points_minimum_annuels` | 2 | 2 | année (2) |  |
| `points_par_trimestre_valide` | 7 | 3 | année (1) |  |
| `smic_du_mois` | 2 | 1 | année (3) |  |
| `taux_calcul_points` | 2 | 2 | année (2) |  |
| `taux_cotisation_deplafonnee` | 5 | 5 | pont, à l'année (1), année (5) |  |
| `taux_cotisation_retraite` | 80 | 55 | pont, à l'année (1), année (8) |  |

## Montant servi (6 champs)

| Champ | Régimes | Où il change | Lectures | Remarque |
|---|---|---|---|---|
| `pension_forfaitaire_annee` | 2 | 2 | effet (3) | son millésime |
| `pension_forfaitaire_annuelle` | 2 | 2 | effet (3) | forfait servi, en euros de pension_forfaitaire_annee |
| `plafond_majoration_annee` | 8 | 1 | effet (2) | son millésime |
| `plafond_majoration_enfants` | 8 | 1 | effet (2) | plafond en euros, qui suit la valeur de service du point |
| `valeur_point_annee` | 8 | 3 | année (1), effet (3) | son millésime |
| `valeur_point_euros` | 8 | 3 | année (1), effet (3) | valeur de service, en euros de valeur_point_annee, revalorisée ensuite |

## Structure (7 champs)

| Champ | Régimes | Où il change | Lectures | Remarque |
|---|---|---|---|---|
| `date_effet` | 21 | 21 | jamais lu sous son nom | borne au jour des pensions ; devient la borne des lignes de liquidation |
| `debut` | 80 | 70 | année (1), effet (6) | borne d'années ; remplacée par les bornes propres à chaque axe |
| `fin` | 80 | 70 | effet (2) | idem |
| `notes` | 80 | 69 | jamais lu sous son nom | commentaire ; suit la ligne qu'il commente |
| `points_de` | 5 | 1 | année (3), effet (4) | le barème du point emprunté ; ne change que dans arrco_cultes (arrco, puis agirc_arrco en 2019) : structure datée |
| `textes_des_renvois` | 11 | 11 | jamais lu sous son nom | sources des renvois ; suit la ligne qui ouvre le renvoi, de liquidation ou de cotisation (six renvois de cotisation, dont bareme_points à la MSA) |
| `type_calcul` | 80 | 0 | année (3), effet (5) | constant dans chacun des 80 régimes |
