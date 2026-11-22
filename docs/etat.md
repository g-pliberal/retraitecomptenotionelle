# État du dépôt

*Le tableau de bord (`docs/architecture.md`, § 9.1). Fabriqué par `scripts/tableau_de_bord.py` depuis la carte des règles, la liste de contrôle des textes et les registres qui ne sont pas encore des vues : aucun nombre n'y est écrit à la main. Pour le corriger, on corrige la fiche ou le registre, puis on relance le script ; un test refuse une copie périmée.*

## 1. Où en est-on

**Les régimes.** L'inventaire en compte 114 : 36 modélisés, 44 partiels, 22 hors champ, 3 routages.

Pesés par leurs retraités de droit direct (2024, enquête EACR de la DREES, où un polypensionné compte dans chacune de ses caisses) :

| Couverture | Retraités-caisses | Part |
|---|---|---|
| régime modélisé | 35 010 992 | 88 % |
| régime partiel | 4 354 564 | 11 % |
| sections libérales, couverture mêlée | 424 386 | 1 % |

*Modélisé ne veut pas dire exact* : les 186 règles approchées de la carte touchent aussi des régimes modélisés (section 2).

**La carte des règles** (`data/reference/regles/`) : 279 fiches, dont 2 relations. La veille en est une vue (`python scripts/veille_droit.py`).

| État | Fiches |
|---|---|
| conformes | 36 |
| transcrites | 28 |
| approchées | 186 |
| pas encore modélisées | 26 |
| manquantes | 1 |
| à vérifier | 2 |

- Confrontées à au moins un exemple officiel : **69 sur 279** (228 exemples : 220 reproduits, 8 en écart connu, section 2).
- Citées dans le code par leur identifiant : **133 sur 279**. Le lien entre une règle et le code qui l'applique n'existe pas encore pour les autres.
- Désignées par les interrupteurs des périodes de régime : **54 sur 279**, par 2 581 renvois ; chacune déclare la valeur que le moteur lit (`code.interrupteurs`) et dit ce qu'il en fait.
- Mûres, sans rien qui manque à leur contrat : **209 sur 279**. Une fiche tirée d'un registre ne sait pas encore son domaine, ses régimes, son étape ni ses versions : ce qui lui manque est à faire (section 3).
- Découpées en versions : **216 sur 279**, soit 903 versions, dont 165 supposées ; le partage des versions se contrôle sur chacune.
- Réformes du calendrier : 126, dont 10 déclarées non appliquées.

**La carte de justesse** (`src/retraite_notionnelle/noyau/justesse.py`, action 194). L'état de la carte des règles, ci-dessus, est un mot que la fiche déclare ; celui-ci se calcule depuis les preuves, et personne ne l'écrit. Une partie est une règle sur une période : une version de fiche, ou la fiche entière tant qu'elle n'est pas découpée. Elle est prouvée quand son texte est lu avec sa trace et qu'une grille indépendante — des valeurs attendues posées depuis le seul texte, sans lire le code, sur chaque seuil de la règle — est verte ; un exemple officiel, un autre moteur ou le simulateur d'une caisse en sont des témoins, qui ne prouvent pas seuls.

**22 parties prouvées sur 966**, dont 10 avec témoin et 12 au texte seul. 13 fausses (section 2), 646 approchées, 218 non vérifiées, 67 hors champ. Un cliquet tient les parties prouvées (`tests/cliquets_de_justesse/prouvees.yaml`) : aucune ne recule sans le dire.

| Famille de régimes | Parties | Prouvées | Fausses | Approchées | Non vérifiées | Hors champ | Texte tracé | Témoignées par un exemple officiel |
|---|---|---|---|---|---|---|---|---|
| salariés du privé, régimes de base | 318 | 22 | 6 | 181 | 79 | 30 | 104 | 49 |
| salariés du privé, complémentaires | 180 | 13 | 1 | 113 | 46 | 7 | 58 | 24 |
| fonction publique | 225 | 13 | 1 | 121 | 62 | 28 | 39 | 36 |
| artisans, commerçants et autres non-salariés | 235 | 20 | 4 | 151 | 56 | 4 | 85 | 46 |
| régimes agricoles | 284 | 22 | 6 | 174 | 69 | 13 | 117 | 49 |
| libéraux et avocats | 231 | 13 | 0 | 174 | 41 | 3 | 91 | 27 |
| régimes spéciaux | 265 | 22 | 2 | 160 | 59 | 22 | 62 | 33 |
| retraite additionnelle, en capitalisation | 40 | 5 | 3 | 11 | 10 | 11 | 9 | 13 |
| sans famille | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| toute la carte | 966 | 22 | 13 | 646 | 218 | 67 | 285 | 91 |

Une partie compte dans chaque famille de ses régimes, et une fois dans le total. Parmi les 966 parties, 165 sont des versions supposées, qu'aucune grille ne peut prouver tant que leur texte n'est pas retrouvé ; 55 ont un exemple officiel que leur fiche cite sans dire pour quelle version, et qui ne témoigne donc pour aucune. Les confrontations aux autres moteurs que 43 fiches racontent en prose ne valent pas témoin : rien n'y dit, cas par cas, ce qui concorde. La carte ne connaît encore que les règles : les barèmes, les régimes de bout en bout, les cas types et les totaux n'y ont pas leurs preuves (section 4).

**Un autre moteur, quantité par quantité.** TRAJECTOiRE (3.3.2) rejoue 85 carrières (`tests/temoins/trajectoire_3/ecarts.json`, `scripts/confronter_trajectoire.py`) : **541 quantités sur 818** concordent. Un écart n'est pas une erreur du dépôt, seul le texte tranche ; il dit où relire. Chaque cas est une carrière entière, que rien ne rattache encore à une règle : ce tableau ne change l'état d'aucune partie.

| Quantité | Cas | Concordent | En écart |
|---|---|---|---|
| pension_totale | 62 | 5 | 57 |
| fonction_publique | 29 | 4 | 25 |
| points_rafp | 29 | 4 | 25 |
| salaire_annuel_moyen | 31 | 6 | 25 |
| rafp | 29 | 5 | 24 |
| traitement_de_reference | 29 | 6 | 23 |
| regime_general | 31 | 10 | 21 |
| taux | 75 | 63 | 12 |
| trimestres_requis | 75 | 65 | 10 |
| trimestres | 85 | 76 | 9 |
| minimum | 62 | 56 | 6 |
| rafp_en_capital | 29 | 24 | 5 |
| carriere_longue | 85 | 81 | 4 |
| msa_non_salaries | 4 | 0 | 4 |
| msa_rco | 4 | 0 | 4 |
| points_msa_non_salaries | 4 | 0 | 4 |
| points_msa_rco | 4 | 0 | 4 |
| age_ouverture | 68 | 65 | 3 |
| asv_conventionnes | 2 | 0 | 2 |
| carmf_complementaire | 2 | 0 | 2 |
| cnavpl | 2 | 0 | 2 |
| points_asv_conventionnes | 2 | 0 | 2 |
| points_carmf_complementaire | 2 | 0 | 2 |
| points_cnavpl | 2 | 0 | 2 |
| majoration_complementaires | 2 | 2 | 0 |
| majoration_fonction_publique | 1 | 1 | 0 |
| majoration_regime_general | 2 | 2 | 0 |
| points_agirc | 2 | 2 | 0 |
| points_agirc_arrco | 20 | 20 | 0 |
| points_arrco | 11 | 11 | 0 |
| valeur_point_agirc | 2 | 2 | 0 |
| valeur_point_agirc_arrco | 20 | 20 | 0 |
| valeur_point_arrco | 11 | 11 | 0 |

**À quoi la carte se confronte** (action 137). Chaque partie dans le champ a sa référence, la meilleure qu'elle ait : officielle (un exemple publié, une grille posée sans le code, un simulateur de caisse) ; un autre modèle qui lit le droit réel, que sa fiche cite ; une source repérée à rejouer (`a_confronter`) ; ou l'absence, que la fiche dit (`sans_reference`). Le texte reste l'arbitre. Comptées famille par famille, une partie dans chacune des siennes : 430 officielles, 310 par un modèle seul, 611 à confronter, 310 sans référence. Chaque case donne les parties confirmées par une référence officielle, sur celles du domaine et de la famille.

| Domaine | salariés du privé, régimes de base | salariés du privé, complémentaires | fonction publique | artisans, commerçants et autres non-salariés | régimes agricoles | libéraux et avocats | régimes spéciaux | retraite additionnelle, en capitalisation | sans famille |
|---|---|---|---|---|---|---|---|---|---|
| age | 11 sur 37 | 6 sur 17 | 10 sur 49 | 11 sur 31 | 11 sur 31 | 6 sur 11 | 8 sur 46 | 5 sur 8 | — |
| coordination | 4 sur 10 | 1 sur 1 | 4 sur 12 | 4 sur 10 | 4 sur 10 | 2 sur 5 | 1 sur 4 | 1 sur 3 | — |
| cotisations | 0 sur 16 | 0 sur 13 | 0 sur 2 | 0 sur 29 | 0 sur 11 | 1 sur 28 | 0 sur 4 | 0 sur 4 | — |
| cumul | 5 sur 24 | 4 sur 25 | 5 sur 21 | 5 sur 28 | 5 sur 26 | 5 sur 26 | 4 sur 21 | 3 sur 5 | — |
| decote_surcote | 9 sur 31 | 2 sur 27 | 1 sur 5 | 9 sur 23 | 9 sur 31 | 38 sur 77 | 9 sur 29 | — | — |
| depart_anticipe | 4 sur 13 | — | 4 sur 12 | 4 sur 8 | 4 sur 8 | 3 sur 6 | — | — | — |
| duree | 8 sur 11 | 8 sur 8 | 9 sur 31 | 8 sur 11 | 8 sur 11 | 8 sur 8 | 10 sur 31 | — | — |
| enfants | 1 sur 13 | 1 sur 19 | 2 sur 23 | 1 sur 13 | 1 sur 13 | 1 sur 22 | 3 sur 32 | — | — |
| minima | 10 sur 26 | — | — | 10 sur 21 | 10 sur 43 | — | 10 sur 20 | — | — |
| periodes_assimilees | 0 sur 14 | 0 sur 5 | — | — | 0 sur 6 | — | — | — | — |
| points | 0 sur 3 | 4 sur 41 | — | 0 sur 9 | 0 sur 3 | 0 sur 18 | 0 sur 6 | 4 sur 6 | — |
| revalorisation | 0 sur 5 | — | — | — | 0 sur 5 | — | — | — | — |
| reversion | 5 sur 22 | 2 sur 10 | 1 sur 7 | 6 sur 25 | 5 sur 22 | 0 sur 7 | 0 sur 9 | 1 sur 1 | — |
| salaire_de_reference | 7 sur 28 | — | 0 sur 11 | 0 sur 3 | 7 sur 15 | — | 3 sur 19 | — | — |
| sans domaine | 11 sur 35 | 3 sur 7 | 7 sur 24 | 10 sur 20 | 11 sur 36 | 3 sur 20 | 8 sur 22 | 1 sur 2 | 0 sur 1 |

**Les filets de la carte** (`src/retraite_notionnelle/noyau/filets.py`, `scripts/filets.py`, action 194, étape B). Ils ne prouvent rien, et leur section ne change l'état d'aucune partie : ils disent où regarder d'abord.

*Le balayage de cohérence* (2026-11-21) : 528 615 calculs des treize cas types, écrits en part du salaire moyen de chaque année, générations 1940 à 1990, départs par trimestre jusqu'à 70 ans. Cotiser plus ne baisse jamais la pension, sauf baisse qu'une liste rattache à un texte (`tests/cliquets_de_justesse/baisses_legales.yaml`) ; et aucun saut du taux de remplacement entre deux générations voisines au-delà de 1 %, hors des bornes que les tables et les versions du paquet posent, ou d'un trimestre validé de plus. **3052 anomalies à expliquer** : 1974 sauts ; baisses, 691 sous un salaire plus haut une année, 208 sous une année d'activité de plus, 179 sous un départ plus tard. Chacune est une piste, non une erreur établie ; le cliquet (`tests/cliquets_de_justesse/filets.yaml`) n'en laisse pas monter le nombre.

| Sorte | Cas type | Génération | Pensions | Âges | Écart le plus fort |
|---|---|---|---|---|---|
| baisse_a | exploitant_agricole | 1985-01 | 37 | 62,00 à 66,75 | -0,00 % |
| baisse_a | exploitant_agricole | 1986-01 | 37 | 62,00 à 66,75 | -0,00 % |
| saut | agent_sncf_conduite | 1949-10 | 35 | 50,25 à 69,75 | 1,63 % |
| baisse_a | exploitant_agricole | 1959-01 | 33 | 61,00 à 65,75 | -0,00 % |
| baisse_a | exploitant_agricole | 1984-01 | 33 | 63,00 à 66,75 | -0,00 % |
| baisse_a | exploitant_agricole | 1970-01 | 27 | 63,00 à 67,50 | -0,00 % |
| baisse_a | exploitant_agricole | 1972-01 | 27 | 62,00 à 67,50 | -0,00 % |
| baisse_a | exploitant_agricole | 1981-01 | 27 | 62,00 à 66,75 | -0,00 % |
| baisse_a | exploitant_agricole | 1973-01 | 26 | 63,00 à 67,50 | -0,00 % |
| baisse_a | exploitant_agricole | 1979-01 | 25 | 64,00 à 67,00 | -0,00 % |
| baisse_a | exploitant_agricole | 1983-01 | 25 | 62,00 à 66,75 | -0,00 % |
| baisse_a | exploitant_agricole | 1982-01 | 24 | 62,00 à 66,75 | -0,00 % |
| baisse_a | exploitant_agricole | 1958-01 | 23 | 61,00 à 65,50 | -0,00 % |
| baisse_a | exploitant_agricole | 1980-01 | 22 | 63,00 à 67,00 | -0,00 % |
| baisse_a | exploitant_agricole | 1990-01 | 22 | 63,00 à 66,25 | -0,00 % |

*La neutralisation* (2026-11-21) : chaque partie mutée — ses paramètres, la source que sa fiche nomme, ses interrupteurs —, les 937 témoins de simulation rejoués. Sur 949 parties, **494 gardées**, 192 non gardées (le paquet change, aucun témoin), 263 hors d'atteinte (aucune mutation ne change le paquet). Une partie non gardée n'est pas fausse : elle n'est pas surveillée. Les exemples officiels ne sont pas rejoués : la garde est une borne basse.

| Famille de régimes | Gardées | Non gardées | Hors d'atteinte |
|---|---|---|---|
| retraite additionnelle, en capitalisation | 5 | 0 | 19 |
| régimes agricoles | 24 | 22 | 11 |
| salariés du privé, régimes de base | 74 | 62 | 82 |
| salariés du privé, complémentaires | 94 | 22 | 24 |
| fonction publique | 39 | 37 | 53 |
| libéraux et avocats | 126 | 7 | 17 |
| artisans, commerçants et autres non-salariés | 39 | 10 | 23 |
| sans famille | 1 | 0 | 0 |
| régimes spéciaux | 92 | 32 | 34 |

Non gardées : `complement_differentiel_rco / avant_le_complement`, `complement_differentiel_rco / complement_de_2015`, `complement_differentiel_rco / complement_de_2016`, `complement_differentiel_rco / complement_de_2017`, `complement_differentiel_rco / complement_de_2026`, `complement_differentiel_rco / complement_de_novembre_2021`, `complement_differentiel_rco / complement_de_septembre_2023`, `majoration_retraite_proportionnelle / au_minimum_vieillesse`, `majoration_retraite_proportionnelle / pensions_dues_en_1998`, `majoration_retraite_proportionnelle / pensions_dues_en_1999`, `majoration_retraite_proportionnelle / pensions_dues_en_2000`, `majoration_retraite_proportionnelle / pensions_dues_en_2001`, `majoration_retraite_proportionnelle / pensions_dues_en_2007`, `majoration_retraite_proportionnelle / pensions_dues_en_2008`, `majoration_retraite_proportionnelle / plan_de_1997`, `pension_majoree_reference / pmr_de_2009`, `pension_majoree_reference / pmr_de_2011`, `pension_majoree_reference / pmr_de_2014`, `pension_majoree_reference / pmr_de_2026`, `pension_majoree_reference / pmr_de_septembre_2023`, `pension_majoree_reference / pmr_unique_de_2022`, `relevement_des_exploitants_2023 / pensions_d_avant_septembre_2023`, `carriere_longue_reputes_cotises_autres / deux_trimestres_de_chomage`, `carriere_longue_reputes_cotises_autres / l_assurance_des_parents_au_foyer`, `carriere_longue_reputes_cotises_autres / quatre_de_chomage_et_la_maternite`, `carriere_longue_reputes_cotises_autres / service_national_et_incapacite_temporaire`, `conge_supplementaire_naissance / cinquante_huit_jours`, `inaptitude_au_travail / incapacite_permanente_2015`, `inaptitude_au_travail / ordonnance_1945`, `limite_age_contractuels / code_general_2022`, `limite_age_contractuels / loi_de_1947`, `limite_age_contractuels / loi_de_2010`, `limite_age_contractuels / loi_de_2012`, `limite_age_contractuels / reforme_2023`, `majoration_conjoint_a_charge / decret_du_12_janvier_2007`, `majoration_conjoint_a_charge / loi_du_23_aout_1948`, `majoration_duree_assurance_enfants / sans_droit_avant_1972`, `majorations_forfaitaires_1972_1982 / en_1972`, `majorations_forfaitaires_1972_1982 / en_1973`, `majorations_forfaitaires_1972_1982 / en_1974`, `minimum_contributif / avpf_et_ava_2023`, `minimum_contributif / limitation_du_cumul_1984`, `minimum_contributif / majoration_des_periodes_cotisees_2005`, `minimum_contributif / majoration_sans_distinction_2004`, `minimum_contributif / minimum_de_1983`, `minimum_contributif / pension_minimum_de_1945`, `minimum_contributif / pension_minimum_de_1976`, `minimum_contributif / seuil_de_120_trimestres_2009`, `pension_d_invalidite_substituee / age_legal_2011`, `pension_d_invalidite_substituee / invalide_qui_travaille_2010`, `pension_d_invalidite_substituee / ordonnance_1945`, `pension_d_invalidite_substituee / plancher_avts_1983`, `pension_maximale_regime_general / quarante_pour_cent_du_plafond`, `residence_et_minimum_vieillesse / residence_neuf_mois_2023`, `residence_et_minimum_vieillesse / residence_six_mois_2006`, `retraite_anticipee_handicap / cinquante_pour_cent_2015`, `retraite_anticipee_handicap / decret_2004`, `retraite_anticipee_handicap / duree_cotisee_2023`, `retraite_anticipee_handicap / majoration_2006`, `retraite_anticipee_handicap / travailleurs_handicapes_2011`, `retraite_progressive / deux_ans_avant_2014`, `retraite_progressive / pension_complete_recalculee_2006`, `reversion / age_51_2009`, `reversion / age_55_2009`, `reversion / majoration_2010_age_51`, `reversion / minimum_2012_age_51`, `reversion / minimum_2026_age_51`, `reversion / reforme_2004`, `sportifs_haut_niveau / seize_trimestres`, `sportifs_haut_niveau / trente_deux_trimestres`, `stages_formation_professionnelle / cinquante_jours_depuis_2015`, `stages_formation_professionnelle / tuc_et_stages_d_insertion`, `taux_plein_anciens_combattants_prisonniers / decret_du_23_janvier_1974`, `taux_plein_anciens_combattants_prisonniers / decret_du_7_juillet_2024`, `taux_plein_anciens_combattants_prisonniers / pratique_de_la_caisse_depuis_2011`, `taux_plein_anciens_combattants_prisonniers / premiere_annee_1974`, `taux_plein_anciens_deportes_internes / decret_du_23_avril_1965`, `taux_plein_meres_de_famille_ouvrieres / loi_du_30_decembre_1975`, `taux_plein_travailleurs_manuels / quarante_deux_ans`, `taux_plein_travailleurs_manuels / quarante_trois_ans`, `totalisation_des_periodes_etrangeres / organisations_internationales_2010`, `versement_forfaitaire_unique / code_de_la_securite_sociale`, `versement_forfaitaire_unique / decret_du_24_fevrier_1975`, `versement_forfaitaire_unique / loi_du_20_janvier_2014`, `coefficients_anticipation_agirc_1947 / avant_le_1er_avril_1947`, `coefficients_anticipation_agirc_1947 / convention_du_14_mars_1947`, `coefficients_anticipation_agirc_1947 / table_des_accords_de_1955`, `garantie_minimale_points_agirc / cent_quarante_quatre_points`, `garantie_minimale_points_agirc / cent_vingt_points`, `garantie_minimale_points_agirc / eteinte_avec_la_fusion`, `garantie_minimale_points_agirc / sans_garantie_avant_1989`, `majoration_dix_pour_cent`, `majoration_enfants_a_charge_agirc_arrco / accord_du_18_mars_2011`, `reversion_ircantec / divorces_1980`, `reversion_ircantec / enfant_1994`, `reversion_ircantec / veufs_1976`, `reversion_ircantec / veuves_1971`, `versement_unique_agirc_arrco / accord_du_17_novembre_2017`, `versement_unique_agirc_arrco / dispositif_de_2004`, `versement_unique_agirc_arrco / table_de_2020`, `versement_unique_agirc_arrco / table_de_2023`, `versement_unique_agirc_arrco / table_de_2024`, `versement_unique_agirc_arrco / table_de_2025`, `versement_unique_agirc_arrco / table_de_2026`, `versement_unique_ircantec / arrete_de_1976`, `versement_unique_ircantec / arrete_du_30_decembre_1970`, `bonification_cinquieme_militaires / loi_de_finances_pour_1972`, `bonification_cinquieme_militaires / loi_du_21_aout_2003`, `bonification_cinquieme_police_penitentiaire / loi_de_1957`, `bonification_cinquieme_police_penitentiaire / loi_du_9_novembre_2010`, `bonification_cinquieme_sapeurs_pompiers / decret_de_1986`, `bonification_cinquieme_sapeurs_pompiers / decret_de_2003`, `bonification_cinquieme_sapeurs_pompiers / decret_du_30_decembre_2010`, `bonification_cinquieme_sapeurs_pompiers / decret_du_3_juin_2023`, `decompte_des_services_fonction_publique / code_de_1964`, `depart_anticipe_parents_trois_enfants / avant_1982`, `depart_anticipe_parents_trois_enfants / loi_du_30_decembre_2004`, `enfants_fonction_publique / l12b_2004`, `enfants_fonction_publique / l12b_avant_1964`, `indemnite_de_feu_sapeurs_pompiers / decret_du_30_decembre_2010`, `indemnite_de_feu_sapeurs_pompiers / decret_du_31_decembre_2024`, `indemnite_de_feu_sapeurs_pompiers / loi_du_28_novembre_1990`, `limite_age_fonction_publique / code_general_2022`, `limite_age_fonction_publique / loi_de_1936`, `limite_age_ouvriers_etat / loi_de_2010`, `limite_age_ouvriers_etat / transition_jusqu_en_2012`, `majoration_duree_hospitaliers_actifs / loi_de_2003`, `majoration_duree_hospitaliers_actifs / loi_du_14_avril_2023`, `majoration_duree_hospitaliers_actifs / loi_du_9_novembre_2010`, `plafond_limite_age_fonction_publique / soixante_dix_ans`, `prime_speciale_sujetion_aides_soignants / loi_de_financement_pour_2004`, `prime_speciale_sujetion_aides_soignants / loi_du_9_novembre_2010`, `prolongation_activite_carriere_incomplete / code_general_2022`, `recul_limite_age_enfants / avant_1986`, `recul_limite_age_enfants / code_general_2022`, `recul_limite_age_enfants / plafond_de_2023`, `retraite_pour_invalidite_fonction_publique / avant_1964`, `retraite_pour_invalidite_fonction_publique / code_1964`, `retraite_pour_invalidite_fonction_publique / reforme_2003`, `reversion_fonction_publique / avant_1980`, `reversion_fonction_publique / complement_aspa_2025`, `reversion_fonction_publique / veuves_1980`, `services_et_duree_fonction_publique`, `asv_auxiliaires_medicaux_coefficients_d_age / avant_le_reglement_de_2026`, `asv_auxiliaires_medicaux_coefficients_d_age / reglement_de_2026`, `reversion_carcdsf / reglement_de_2026`, `reversion_carcdsf / statuts_de_2007`, `reversion_carcdsf / statuts_de_2011`, `reversion_cavamac / reglement_de_2026`, `reversion_cavamac / statuts_de_2011`, `carriere_longue_sauvegarde_de_2023 / decret_du_3_juin_2023`, `exoneration_independants_outre_mer`, `points_invalidite_independants / avant_la_rco_des_artisans`, `points_invalidite_independants / rci_deux_points_sans_cotisation`, `points_invalidite_independants / rci_quotient`, `points_invalidite_independants / rco_des_artisans_et_nric`, `reversion_rci / reglement_2013`, `taux_plein_a_soixante_cinq_ans / loi_du_9_novembre_2010`, `versement_unique_rci / reglement_de_2013`, `versement_unique_rci / reglement_de_2024`, `age_ouverture_banque_de_france_actifs / decret_de_2012`, `age_ouverture_banque_de_france_actifs / decret_de_2023`, `age_ouverture_banque_de_france_actifs / reglement_de_2007`, `decote_banque_de_france / tableau_par_periode_de_liquidation`, `enfants_crpcen / annee_par_enfant_1990`, `enfants_crpcen / avant_1990`, `enfants_crpcen / majoration_2006`, `enfants_crpcen / majoration_2008`, `enfants_ieg / avant_juillet_2008`, `enfants_ieg / bonification_2008`, `enfants_ratp / avant_juillet_2008`, `enfants_sncf / avant_juillet_2008`, `limite_age_banque_de_france / statut_de_2012`, `limite_age_ieg / decret_de_2008`, `limite_age_ieg / decret_de_2023`, `limite_age_mines / article_125_de_1993`, `limite_age_mines / decret_de_1954`, `limite_age_opera / decret_de_2008`, `limite_age_sncf_ratp / decret_de_2010`, `limite_age_sncf_ratp / decret_de_2011`, `limite_age_sncf_ratp / reforme_2023`, `marins_bonification_enfants / code_de_1968`, `marins_bonification_enfants / loi_du_12_avril_1941`, `marins_bonification_enfants / neuf_ans_d_education`, `minimum_pension_sncf / anciennete_2008`, `minimum_pension_sncf / taux_plein_2017`, `reversion_crpcen / avant_1990`, `reversion_crpcen / veuves_1990`, `reversion_ieg / veuves_1946`, `reversion_sncf / avant_2008`, `reversion_sncf / minimum_2008`, `reversion_sncf / minimum_2009`.

**La loi, rédaction par rédaction** (`data/reference/textes/`, § 6.6) : 18 012 rédactions d'articles, de 325 textes, lues le 2026-11-16 (index LEGI du dépôt : Freemium_legi_global_20250713-140000.tar.gz, incréments appliqués jusqu'au 20261116-104909). C'est le dénominateur de l'avancement : ce que les fiches ont lu, contre ce que la loi a écrit.

| Statut | Rédactions |
|---|---|
| rattachées à une version | 2 063 |
| sans effet | 152 |
| à rattacher | 627 |
| à examiner | 6 005 |
| sans statut | 9 165 |

**La personne** (§ 5) : une chronologie de faits datés, dans un réseau de personnes — aujourd'hui l'assuré, ses enfants et son conjoint —, que le relevé et le parcours déclarent (`src/retraite_notionnelle/chronologie.py`, et son jumeau). La carrière que le moteur liquide en est la vue. Ce que la saisie ne dit pas est présumé : 33 présomptions au vocabulaire, dont 3 posent leur fait dans la chronologie ; les autres s'appliquent dans le code, jusqu'à l'étape qui posera le leur.

| Présomption | Valeur | Fiches qui la lisent | Où elle s'applique |
|---|---|---|---|
| `jour_de_naissance` | 15 du mois | `date_effet_mois_suivant`, `sam_indemnites_de_maternite` | posée par la chronologie |
| `naissance_des_enfants` | 30 ans | `depart_anticipe_parents_trois_enfants`, `enfants_crpcen`, `enfants_fonction_publique`, `enfants_ieg`, `enfants_ratp`, `enfants_sncf`, `majoration_duree_assurance_enfants`, `priorite_majorations_enfants`, `reversion_ircantec`, `sam_indemnites_de_maternite` | posée par la chronologie |
| `radiation_au_1er_janvier_suivant` | le 1er janvier qui suit la dernière année de services, ou le départ s'il part en fonctions | `enfants_fonction_publique`, `pension_differee_fonction_publique`, `priorite_majorations_enfants`, `retablissement_fonction_publique` | droit_a_pension (droit/coordonner.py), et la revalorisation de la pension différée (droit/liquider.py) ; leurs jumeaux JavaScript ; son fait entrera à l'étape `coordonner_les_affiliations` |
| `agent_en_activite` | en activité, avec services effectifs | `services_et_duree_fonction_publique` | _ligne_annuelle, qui fait de toute année d'emploi une année de services (carriere.py, carriere.js) ; son fait entrera à l'étape `compter_les_durees` |
| `pas_d_accord_des_parents` | aucun accord ; le défaut légal les donne à la mère | `majoration_duree_assurance_enfants` | le paramètre beneficiaire des versions de la fiche majoration_duree_assurance_enfants, lu par MajorationsPourEnfants.par_enfant ; son fait entrera à l'étape `compter_les_durees` |
| `enfant_eleve_neuf_ans` | élevé neuf ans | `majoration_duree_assurance_enfants` | les versions mda_1972 et mda_1975 de la fiche majoration_duree_assurance_enfants, qui écartent l'enfant de moins de neuf ans et présument les autres élevés par leur mère ; son fait entrera à l'étape `compter_les_durees` |
| `interruption_d_activite_par_la_mere` | remplie par la mère seule | `depart_anticipe_parents_trois_enfants`, `enfants_crpcen`, `enfants_fonction_publique`, `enfants_ieg`, `enfants_ratp` | le paramètre beneficiaire (mere) des versions de la fiche enfants_fonction_publique, lu par MajorationsPourEnfants.par_enfant, et de la fiche depart_anticipe_parents_trois_enfants, lu par depart_parent_trois_enfants (droit/ouvrir.py, ouvrir.js) ; son fait entrera à l'étape `compter_les_durees` |
| `demande_de_pension_avant_2011` | demandée avant le 1er janvier 2011 | `depart_anticipe_parents_trois_enfants` | le paramètre ancien_calcul_jusqu_a de la version loi_du_9_novembre_2010 de la fiche depart_anticipe_parents_trois_enfants, lu par depart_parent_trois_enfants (droit/ouvrir.py, ouvrir.js) ; son fait entrera à l'étape `ouvrir_le_droit` |
| `mariage_des_conjoints` | 27 ans | `reversion`, `reversion_crpcen`, `reversion_fonction_publique`, `reversion_fspoeie`, `reversion_ieg`, `reversion_ircantec`, `reversion_sncf` | posée par la chronologie |
| `ressources_du_survivant` | 0 euros par an | `reversion`, `reversion_rci` | reversion (droit/reversion.py), qui ne compte au plafond du régime général, et à celui de la complémentaire des indépendants, que les réversions des autres régimes de base ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `survivant_seul` | seul | `reversion`, `reversion_rci`, `reversion_sncf` | reversion (droit/reversion.py), qui compare ses seules ressources au plafond d'une personne seule, au régime général et à la complémentaire des indépendants ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `retraites_du_survivant_servies` | dès la date d'effet | `majoration_forfaitaire_reversion`, `reversion` | reversion (droit/reversion.py), qui y applique la limite de cumul d'avant juillet 2004, compte ces retraites aux ressources depuis, refuse la majoration pour enfant à charge, et tient la réversion attribuée depuis pour non révisable dès sa date d'effet (_derniere_revision) ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `survivant_sans_droit_propre` | aucune retraite personnelle | `reversion` | _derniere_revision (droit/reversion.py), qui ne révise plus sa réversion du régime général à partir du premier jour du mois qui suit son âge légal (R. 353-1-1, b) ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `charge_jusqu_a_l_age_limite` | l'âge limite | `majoration_forfaitaire_reversion` | _jours_a_charge (droit/reversion.py), qui ne prolonge la charge que des périodes d'études, d'apprentissage et d'infirmité que la chronologie porte ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `majoration_demandee_des_sa_condition` | le premier jour du mois qui suit | `majoration_forfaitaire_reversion` | _parts_de_l_enfant (droit/reversion.py), qui la sert le premier jour du mois qui suit le jour où l'enfant naît ou redevient à charge ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `ressources_du_conjoint` | 0 euros par an | `minimum_vieillesse` | foyer_et_net (droit/foyer.py), qui compte au plafond de l'allocation de solidarité aux personnes âgées du couple les ressources que la saisie prête au conjoint, et aucune sinon ; son jumeau JavaScript ; son fait entrera à l'étape `foyer_et_net` |
| `domicile_fiscal_au_pays_de_residence` | le pays de résidence que la saisie dit | `cotisation_maladie_des_non_residents` | le net (moteur/js/contexte.js, Montants.duFoyer), qui ne prélève alors ni CSG, ni CRDS, ni CASA (L. 136-1) ; son fait entrera à l'étape `foyer_et_net` |
| `aucun_autre_revenu_que_ses_pensions` | la pension du système 1, et les ressources du conjoint déclaré, abattues de 10 % | `csg_des_pensions_selon_le_revenu` | le net (moteur/js/contexte.js, Montants.duFoyer), quand la saisie ne dit pas le revenu fiscal ; son fait entrera à l'étape `foyer_et_net` |
| `conjoint_de_l_autre_sexe` | l'autre sexe | `reversion_agirc_arrco`, `reversion_crpcen`, `reversion_fonction_publique`, `reversion_fspoeie`, `reversion_ieg`, `reversion_ircantec` | la saisie, qui donne au conjoint l'autre sexe quand elle ne le dit pas (moteur/js/saisie.js, Saisie.conjointDeclare) ; son fait entrera à l'étape `preparer_la_chronologie` |
| `reversion_demandee_dans_l_annee` | dans l'année | `majoration_forfaitaire_reversion`, `reversion`, `reversion_agirc_arrco`, `reversion_carcdsf`, `reversion_cavamac`, `reversion_ircantec`, `reversion_rafp`, `reversion_rci` | la date d'effet de la réversion (droit/reversion.py), au premier jour du mois qui suit le décès, ou qui suit l'âge requis ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `paye_dans_l_etat_de_residence` | la résidence que la saisie dit, la France sinon | `reversion_agirc_arrco` | la date d'effet de la réversion de l'Agirc-Arrco (moteur/js/droit/reversion.js, periodeSuivante), au premier jour du trimestre civil qui suit le décès d'un défunt payé au trimestre ; son fait entrera à l'étape `liquider_chaque_regime` |
| `reversion_demandee_le_mois_avant_sa_date_d_effet` | le mois qui précède la date d'effet | `reversion` | _ressources_a_la_date_d_effet (droit/reversion.py), qui examine les ressources d'une réversion du régime général d'avant juillet 2004 sur les trois ou douze mois civils qui précèdent ce mois, puis, la condition non remplie, sur ceux qui précèdent le décès (R. 353-1) ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `deces_apres_le_depart` | au départ | `reversion`, `reversion_agirc_arrco`, `reversion_carcdsf`, `reversion_cavamac`, `reversion_crpcen`, `reversion_fonction_publique`, `reversion_fspoeie`, `reversion_ieg`, `reversion_ircantec`, `reversion_rafp`, `reversion_rci`, `reversion_sncf` | l'échéancier (echeancier.py), qui liquide alors une réversion d'essai, hors du journal ; son jumeau JavaScript ; son fait entrera à l'étape `echeancier` |
| `validation_ircantec_demandee` | demandée | `retablissement_fonction_publique` | retablir (droit/coordonner.py), et l'assiette de l'Ircantec des années rétablies (droit/acquerir.py) ; leurs jumeaux JavaScript ; son fait entrera à l'étape `coordonner_les_affiliations` |
| `depart_de_chaque_regime` | au départ déclaré, à l'ouverture du régime, ou à la sortie de l'armée | `liquidation_regime_par_regime` | departs (droit/departs.py), que l'échéancier et le scénario 1 lisent ; son jumeau JavaScript ; son fait entrera à l'étape `echeancier` |
| `exceptions_a_la_limite_d_age` | demandées et accordées autant que le départ saisi le demande | `limite_age_banque_de_france`, `limite_age_contractuels`, `limite_age_fonction_publique`, `limite_age_ieg`, `limite_age_militaires`, `limite_age_mines`, `limite_age_opera`, `limite_age_ouvriers_etat`, `limite_age_seita`, `limite_age_sncf_ratp`, `maintien_en_fonctions_jusqu_a_70_ans`, `prolongation_activite_carriere_incomplete`, `prolongation_activite_categorie_active` | radiation (droit/limite_age.py), que les départs, l'échéancier et le scénario 1 lisent ; son jumeau JavaScript ; son fait entrera à l'étape `echeancier` |
| `pension_d_invalidite_de_la_periode` | depuis le 1er janvier de la première année de la période d'invalidité finale | `pension_d_invalidite_substituee` | Carriere.pension_d_invalidite (carriere.py), et son jumeau JavaScript ; son fait entrera à l'étape `ouvrir_le_droit` |
| `categorie_de_la_pension_d_invalidite` | la première à qui travaille à l'âge de la substitution, la deuxième sinon | `pension_d_invalidite_substituee` | categorie_de_la_pension (droit/invalidite.py), que le plancher de la pension substituée lit (droit/completer.py) ; leurs jumeaux JavaScript ; son fait entrera à l'étape `completer_tous_regimes` |
| `opposition_a_la_substitution` | opposée, la pension demandée au départ déclaré | `pension_d_invalidite_substituee` | substitution (droit/invalidite.py), et son jumeau JavaScript ; son fait entrera à l'étape `echeancier` |
| `pas_de_pension_etrangere` | aucune | `minimum_contributif_international` | pensions_a_l_ecretement (droit/etranger.py), que l'écrêtement du minimum contributif lit (droit/completer.py) ; leurs jumeaux JavaScript ; son fait entrera à l'étape `preparer_la_chronologie` |
| `pas_de_reversion_agricole` | aucune | `majoration_retraite_proportionnelle`, `pension_majoree_reference` | reversion_agricole_servie (droit/completer.py), que la pension majorée de référence lit, et les plans de revalorisation de 1997 à 2008 (majoration_retraite_proportionnelle, _points_des_conjoints, _minimum_du_veuf) ; leurs jumeaux JavaScript ; son fait entrera à l'étape `preparer_la_chronologie` |
| `pas_de_periode_assimilee` | aucune | `apprentissage`, `conge_supplementaire_naissance`, `sportifs_haut_niveau`, `stages_formation_professionnelle` | aucune étape encore : les fiches apprentissage, stages_formation_professionnelle, sportifs_haut_niveau et conge_supplementaire_naissance sont pas_encore_modelisee, et le moteur compte comme aujourd'hui. Une période déclarée (chronologie.avec_periodes_assimilees, et son jumeau JavaScript) ou un emploi en apprentissage (l'attribut apprentissage d'un métier) prend la place de la présomption ; son fait entrera à l'étape `compter_les_durees` |
| `residence_en_france` | en France | `residence_et_minimum_vieillesse` | foyer_et_net (droit/foyer.py), qui ne sert l'allocation de solidarité aux personnes âgées qu'à qui réside en France ; son jumeau JavaScript ; son fait entrera à l'étape `preparer_la_chronologie` |

**Le relevé des droits** (§ 7.2 et 7.6) : pour chaque demande, quatre étapes le construisent, une par module dans `moteur/js/droit/`, chacune écrivant la donnée que son schéma décrit (`data/reference/etapes/`) ; la liquidation du scénario 1 ne lit que lui. Les relevés des 13 cas types, à chacune de leurs générations — 91 relevés —, comptent 23 101 lignes, dont 782 citent la fiche qui les écrit (3 %) et 14 sa version.

| Étape | Module | Ce qu'elle écrit | Fiches qui disent l'appliquer |
|---|---|---|---|
| `preparer_la_chronologie` | `droit/preparer.js` | la chronologie, présomptions posées (contrat C.1) | `conjoint_collaborateur_independants`, `limite_age_banque_de_france`, `limite_age_contractuels`, `limite_age_fonction_publique`, `limite_age_ieg`, `limite_age_militaires`, `limite_age_mines`, `limite_age_opera`, `limite_age_ouvriers_etat`, `limite_age_seita`, `limite_age_sncf_ratp`, `maintien_en_fonctions_jusqu_a_70_ans`, `maintiens_en_fonctions_de_certains_corps`, `plafond_limite_age_fonction_publique`, `prolongation_activite_carriere_incomplete`, `prolongation_activite_categorie_active`, `recul_limite_age_enfants` |
| `coordonner_les_affiliations` | `droit/coordonner.js` | les régimes qui reçoivent chaque ligne, les rétablissements, les groupes | `cci_paris_transfert_2006`, `cci_roubaix_transfert_1998`, `compagnie_generale_eaux_transfert_1991`, `credit_foncier_transfert_1989`, `crfm_mayotte_pension_unique`, `crfom_regime_du_decret_1950`, `elus_nouvelle_caledonie_cafat`, `interpenetration_fonction_publique`, `liquidation_unique_regimes_alignes`, `maintien_affiliation_crpcen_ieg`, `parlement_europeen_affiliation`, `rafp_beneficiaires`, `regies_ferroviaires_pensions_en_extinction`, `retablissement_fonction_publique`, `totalisation_des_periodes_etrangeres`, `un_statut_par_annee` |
| `compter_les_durees` | `droit/compter.js` | les trimestres de chaque compte, par régime et par année ; ceux des enfants | `accident_du_travail_periodes_assimilees`, `apprentissage`, `bonification_cinquieme_militaires`, `bonification_cinquieme_police_penitentiaire`, `bonification_cinquieme_sapeurs_pompiers`, `cnavpl_majoration_duree_assurance`, `conge_supplementaire_naissance`, `enfants_crpcen`, `enfants_fonction_publique`, `enfants_ieg`, `enfants_ratp`, `enfants_sncf`, `fin_indemnisation_chomage`, `majoration_duree_assurance_enfants`, `majoration_duree_elus_locaux`, `majoration_duree_hospitaliers_actifs`, `majoration_duree_sapeurs_pompiers_volontaires`, `priorite_majorations_enfants`, `service_civique`, `services_et_duree_fonction_publique`, `sportifs_haut_niveau`, `stages_formation_professionnelle`, `trimestres_au_revenu`, `volontariat_civil_et_international` |
| `acquerir_les_droits` | `droit/acquerir.js` | les points et les cotisations, la durée plafonnée, les points gratuits | `agirc_arrco_valeur_achat`, `assiette_minimale_agricole`, `assiette_minimale_independants`, `assiette_rco_independants`, `asv_autres_professions_de_sante`, `asv_medecins_ajustement`, `asv_medecins_points`, `carpimko_assiette_2026`, `cavom_assiette_2016`, `chomage_retraite_complementaire`, `cipav_seconde_tranche`, `cotisation_agricole_de_1952`, `cotisation_par_classes_liberales`, `cotisation_rco_agricole_2026`, `cotisation_vieillesse_agricole_avant_2003`, `cultes_retraite_complementaire`, `cultes_retraite_complementaire_taux_specifiques`, `cultes_salaire_annuel_moyen`, `droits_apres_la_premiere_pension`, `exoneration_independants_outre_mer`, `financement_chomage_complementaire`, `garantie_minimale_points_agirc`, `igrante_points`, `ipacte_points`, `ircantec_valeurs_point`, `micro_social_abattement`, `organic_conjoints_de_commercants`, `points_agricoles_au_revenu_cadastral`, `points_au_prorata_des_cotisations`, `points_invalidite_independants`, `rafp_assiette_plafond`, `rafp_compte_epargne_temps`, `rafp_cotisation_volontaire_outre_mer`, `rafp_gipa_hors_plafond`, `ravgdt_allocation_viagere`, `rci_seuil_premiere_tranche`, `rco_points_gratuits`, `rco_points_gratuits_66`, `retraite_proportionnelle_msa`, `services_passes_outre_mer` |

**La liquidation** (§ 7.3, 7.4 et 7.7) : `liquider(demande, état, contexte)`, une fonction pure (`moteur/js/droit/liquidation.js`), enchaîne l'acquisition et trois étapes, et mesure par des liquidations d'essai ce qu'apporte chaque avantage. L'échéancier (`moteur/js/echeancier.js`) l'appelle au départ, applique à l'échéance les deux étapes qui ne liquident rien, et inscrit tout à son journal (`journal.js`) ; le pilote (`pilote.js`) date les départs des cas types sans rien liquider. Les 935 témoins font chacun de 1 à 12 appels de `liquider`, liquidations d'essai comprises, et au plus 6 par départ ; aucun ne dépasse les 6 par départ que le nombre déclaré accorde (§ 7.8).

| Étape | Module | Ce qu'elle écrit | Fiches qui disent l'appliquer |
|---|---|---|---|
| `ouvrir_le_droit` | `droit/ouvrir.js` | l'âge d'ouverture et son motif, la durée requise, les trimestres cotisés | `age_annulation_decote`, `age_legal_par_generation`, `age_ouverture_banque_de_france_actifs`, `age_ouverture_ieg_actifs`, `carriere_longue`, `carriere_longue_reputes_cotises_autres`, `carriere_longue_sauvegarde_de_2023`, `depart_anticipe_parents_trois_enfants`, `duree_requise_ieg`, `duree_requise_par_generation`, `duree_requise_sncf_ratp`, `inaptitude_au_travail`, `marins_ouverture_cinquante_ans`, `ortf_position_speciale_1974`, `retraite_anticipee_handicap` |
| `liquider_chaque_regime` | `droit/liquider.js` | la pension de chaque régime et sa formule, les régimes qui portent les minima | `age_reference_decote_ieg`, `age_reference_decote_sncf_ratp`, `age_surcote_sncf_ratp`, `agirc_arrco_valeur_service`, `asv_auxiliaires_medicaux_coefficients_d_age`, `atc_icna_allocation`, `cafat_pension_de_base`, `carcdsf_minoration_age_seul`, `carmf_asv_minoration_enfants`, `carpimko_ages_2015`, `carpv_minoration_age_seul`, `cavamac_minoration_age_seul`, `cavec_minoration_age_seul`, `cavom_ages_minoration`, `cavp_minoration_deux_pentes`, `cese_pension_des_membres`, `clr_nouvelle_caledonie_pension_des_fonctionnaires`, `cnavpl_allocation_avant_2004`, `cnavpl_valeur_service`, `coefficient_anticipation_ircantec`, `coefficients_anticipation_agirc_1947`, `coefficients_anticipation_agirc_arrco`, `cprn_ages_decote_enfants`, `cps_polynesie_pension_des_salaries`, `crpn_pension_des_navigants`, `cultes_alsace_moselle_pension`, `cultes_fractions_de_pension`, `decompte_des_services_fonction_publique`, `decompte_des_services_regimes_speciaux`, `decote_avant_1983`, `decote_banque_de_france`, `decote_opera_de_paris`, `decote_regime_general`, `decote_regimes_speciaux`, `deputes_pension_des_anciens_deputes`, `entrepreneurs_du_batiment_complementaire`, `indemnite_de_feu_sapeurs_pompiers`, `indemnite_sujetions_speciales_police`, `majoration_duree_apres_65_ans`, `majoration_forfaitaire_reversion`, `marins_salaire_de_reference`, `mayotte_pension_de_base`, `minoration_racl_2014_2024`, `pension_maximale_regime_general`, `pension_non_salaries_agricoles_2026`, `pension_proratisee`, `points_avant_1973_independants`, `prime_speciale_sujetion_aides_soignants`, `rafp_garantie_outre_mer`, `rafp_majoration_capital`, `retraite_pour_invalidite_fonction_publique`, `retrep_avantages_temporaires`, `revenu_annuel_moyen_independants`, `reversion`, `reversion_agirc_arrco`, `reversion_carcdsf`, `reversion_cavamac`, `reversion_crpcen`, `reversion_fonction_publique`, `reversion_fspoeie`, `reversion_ieg`, `reversion_ircantec`, `reversion_rafp`, `reversion_rci`, `reversion_sncf`, `saint_pierre_et_miquelon_pension_de_base`, `salaire_annuel_moyen`, `sam_annees_d_avant_1947`, `sam_indemnites_de_maternite`, `seconde_pension`, `surcote_banque_de_france`, `surcote_ircantec`, `surcote_par_age_seul`, `surcote_regime_general`, `surcote_regimes_speciaux`, `taux_plein_a_soixante_cinq_ans`, `taux_plein_anciens_combattants_prisonniers`, `taux_plein_anciens_deportes_internes`, `taux_plein_carriere_longue`, `taux_plein_et_proratisation`, `taux_plein_meres_de_famille_ouvrieres`, `taux_plein_travailleurs_manuels`, `wallis_et_futuna_pension_des_salaries` |
| `completer_tous_regimes` | `droit/completer.js` | les minima, la surcote parentale, la majoration pour enfants | `complement_differentiel_rco`, `ircantec_majoration_enfants`, `majoration_conjoint_a_charge`, `majoration_dix_pour_cent`, `majoration_enfants_a_charge_agirc_arrco`, `majoration_enfants_agirc_arrco`, `majoration_enfants_plafond_fonction_publique`, `majoration_retraite_proportionnelle`, `marins_bonification_enfants`, `minimum_contributif`, `minimum_contributif_international`, `minimum_garanti`, `minimum_pension_ieg`, `minimum_pension_sncf`, `pension_majoree_reference`, `sections_liberales_majoration_enfants`, `surcote_parentale`, `versement_forfaitaire_unique`, `versement_unique_agirc_arrco`, `versement_unique_ircantec`, `versement_unique_rci` |
| `faire_vivre` | `revalorisation.js` | le coefficient de chaque pension, du départ à l'échéance | `majoration_exceptionnelle_2023`, `majorations_forfaitaires_1972_1982`, `relevement_des_exploitants_2023`, `revalorisation_des_pensions` |
| `foyer_et_net` | `droit/foyer.js` | l'ASPA, au départ puis à chaque échéance | `assiette_sociale_independants`, `cotisation_maladie_des_non_residents`, `cotisation_maladie_pensions_complementaires`, `cotisation_vieillesse_independants`, `cotisation_vieillesse_independants_mayotte`, `csg_des_pensions_selon_le_revenu`, `minimum_vieillesse`, `residence_et_minimum_vieillesse` |

**La proposition, en univers de droit** (§ 4.8 et 8) : chaque scénario est une pile de couches posée sur le droit réel, que l'univers déclare (`data/reference/univers/`, `data/reference/couches/`) ; le simulateur en tire ses scénarios, et le paquet du site les porte résolus. 9 fiches de la proposition (`data/reference/regles/proposition/`) décrivent ce que les couches ajoutent, en citant son texte. Les fiches du droit réel qu'aucune couche d'un univers ne garde, ne remplace ni ne neutralise sont ses domaines sans décision (section 3).

| Scénario | Univers | Couches posées sur le droit réel | Fiches ajoutées | Fiches du droit réel sans décision |
|---|---|---|---|---|
| 1 | `actuel` | aucune : c'est l'étalon | 0 | — |
| 2 | `notionnel_retroactif` | `comptes_notionnels` | 5 | 120 sur 279 |
| 3 | `notionnel_prospectif` | `contributif_seul`, `valorisation_des_droits_acquis`, `comptes_notionnels` | 6 | 120 sur 279 |
| 4 | `notionnel_retroactif_employeur` | `comptes_notionnels`, `part_patronale` | 5 | 120 sur 279 |
| 5 | `notionnel_prospectif_employeur` | `contributif_seul`, `valorisation_des_droits_acquis`, `comptes_notionnels`, `part_patronale` | 6 | 120 sur 279 |
| 6 | `notionnel_liberal` | `comptes_notionnels`, `part_patronale`, `taux_unique`, `capitalisation_obligatoire`, `garantie_vieillesse`, `age_legal_de_la_proposition` | 8 | 120 sur 279 |

**La réorganisation** (§ 6.5, § 11). Les registres devenus des vues de la carte : la veille. Restent des registres : la frontière contributive, l'inventaire des régimes.

**Ce qui est hors de la page Coût.** La réversion, par exemple, pèse 10,4 % de la masse des prestations en 2024 (COR) : le modèle en calcule une pour une personne (scénario 1), mais la page Coût n'en connaît que cette part publiée, qu'elle ne calcule pas.

**La feuille de route** compte 196 actions : 140 fait, 30 en cours, 22 à faire, 2 archivée, 2 abandonnée. Les closes sont dans son archive, `docs/archives/feuille_de_route.md` ; ce qui reste à faire est ailleurs, dispersé.

## 2. Ce qui ne va pas encore

**Les régimes partiels, du plus peuplé au moins peuplé**

| Régime | Retraités | Ce qui manque |
|---|---|---|
| Pensions civiles et militaires de retraite (Service des retraites de l'État) | 2 018 190 | Les bonifications de SERVICE — dépaysement, campagne, services aériens — ne sont pas servies, faute de connaître le corps et le détail des services |
| Assurance vieillesse des non-salariés agricoles (MSA) | 1 023 064 | Le barème en points de 1981 à 1989 se lit sur un revenu cadastral que le modèle n'a pas, et déduit du revenu par convention |
| Retraite complémentaire obligatoire des non-salariés agricoles | 616 621 | Les points gratuits des chefs d'exploitation pour leurs années d'avant 2003 sont servis |
| Caisse nationale d'assurance vieillesse des professions libérales, régime de base | 460 991 | Le libéral non réglementé installé depuis 2019 relève du régime général et du RCI, celui installé avant reste à la CNAVPL et à la Cipav : le statut `liberal_non_reglemen… |
| Régime spécial de sécurité sociale dans les mines (CANSSM) | 86 133 | La complémentaire des mineurs n'est pas routée : le statut `mineur` ne cotise qu'au régime des mines. |
| Caisse de retraite et de prévoyance des clercs et employés de notaires | 70 377 | Deux âges avant 2008 — soixante ans, ou cinquante-cinq pour l'assurée justifiant de vingt-cinq années de cotisations — et le moteur n'en porte qu'un : la fiche garde le… |
| Régime des marins (ENIM) | 62 598 | La grille des vingt catégories est lue au Journal officiel depuis 2008 (`salaires_forfaitaires.csv`, arrêtés annuels) et appliquée : le marin est rangé chaque année dans… |
| Caisse nationale des barreaux français, régime de base | 16 590 | La progression de la cotisation forfaitaire sur les cinq premières années et la contribution équivalente aux droits de plaidoirie ne sont pas portées, ni la majoration d… |

Et 36 régimes partiels sans effectif dans l'enquête (outre-mer, sections libérales, régimes fermés…).

**Les règles approchées, absentes ou à vérifier**, avec ce que leur fiche dit de leur effet :

| Règle | État | Qui est touché |
|---|---|---|
| `minimum_pension_ieg` | manquante | Les petites pensions des IEG — une courte carrière dans la branche, une réversion — sous le plafond de ressources : le modèle ne les relève… |
| `atc_icna_allocation` | pas_encore_modelisee | Les ingénieurs du contrôle de la navigation aérienne radiés depuis 1998 : jusqu'à treize ans d'une allocation de 64 à 150 % de l'indemnité… |
| `cci_paris_transfert_2006` | pas_encore_modelisee | Les agents titulaires de la chambre partis avant 2006 touchent depuis leur pension en deux parts, une rente du régime général et ce que la… |
| `cci_roubaix_transfert_1998` | pas_encore_modelisee | Les salariés de l'ancienne chambre de Roubaix entrés avant 1998 : leurs années d'avant 1998 valent une rente forfaitaire du régime général,… |
| `compagnie_generale_eaux_transfert_1991` | pas_encore_modelisee | Les salariés de la compagnie entrés avant 1991, partis depuis : leurs années d'avant 1991 valent une rente forfaitaire du régime général, e… |
| `credit_foncier_transfert_1989` | pas_encore_modelisee | Les anciens agents du Crédit foncier entrés avant 1989, nés avant 1929 pour les pensionnés et jusqu'aux générations des années 1960 pour le… |
| `crfm_mayotte_pension_unique` | pas_encore_modelisee | Les agents publics de Mayotte titulaires avant 2003, nés pour la plupart de 1945 à 1985 : le modèle simule leur carrière aux règles du régi… |
| `crfom_regime_du_decret_1950` | pas_encore_modelisee | Les fonctionnaires des anciens cadres de la France d'outre-mer encore en activité en 1976, nés pour la plupart de 1915 à 1945 : le modèle s… |
| `cultes_alsace_moselle_pension` | pas_encore_modelisee | Les quelque 1 400 ministres et employés des cultes rémunérés par l'État en Alsace-Moselle : le modèle n'a ni leur statut ni leur pension d'… |
| `elus_nouvelle_caledonie_cafat` | pas_encore_modelisee | Les élus calédoniens qui n'ont pas d'autre activité : le modèle ne simule pas leurs mandats, quand ils valent des points de la CAFAT depuis… |
| `entrepreneurs_du_batiment_complementaire` | pas_encore_modelisee | Les entrepreneurs du bâtiment affiliés avant 1998 et leurs ayants droit : une pension complémentaire en points, que le modèle ne sert pas,… |
| `inaptitude_invalidite_penibilite_amiante` | pas_encore_modelisee | Assurés concernés déclarés non ouverts ou décotés à tort. |
| `maintiens_en_fonctions_de_certains_corps` | pas_encore_modelisee | Les membres de ces corps, que le simulateur ne distingue pas : il les simule comme tout fonctionnaire de l'État, sans limite d'âge. |
| `majoration_duree_elus_locaux` | pas_encore_modelisee | Les anciens et actuels élus exécutifs locaux — maires, adjoints, présidents et vice-présidents de départements, de régions et d'intercommun… |
| `majoration_duree_sapeurs_pompiers_volontaires` | pas_encore_modelisee | Tout assuré qui a été sapeur-pompier volontaire au moins dix ans et liquide depuis le 1er juillet 2026 : un à trois trimestres de durée d'a… |
| `ortf_position_speciale_1974` | pas_encore_modelisee | Les agents de l'Office nés en 1919 ou avant, mis en position spéciale de 1975 à leur limite d'âge, et leurs conjoints survivants : quelques… |
| `parlement_europeen_affiliation` | pas_encore_modelisee | Les représentants français au Parlement européen de 1979 à 2009 qui n'étaient pas parlementaires nationaux : leurs années de mandat ouvrent… |
| `rachats_et_versements` | pas_encore_modelisee | Non saisissables dans le simulateur. |
| `rafp_compte_epargne_temps` | pas_encore_modelisee | Les fonctionnaires qui ont versé des jours de compte épargne-temps au RAFP ont des points que le modèle ne compte pas : quinze jours en cat… |
| `rafp_cotisation_volontaire_outre_mer` | pas_encore_modelisee | Les agents de l'État affectés depuis avril 2024 à Wallis-et-Futuna, en Polynésie, à Saint-Pierre-et-Miquelon ou en Nouvelle-Calédonie, qui… |
| `rafp_garantie_outre_mer` | pas_encore_modelisee | Les agents de l'État partis depuis 2024 qui vivent à Wallis-et-Futuna, en Polynésie, à Saint-Pierre-et-Miquelon ou en Nouvelle-Calédonie :… |
| `rafp_gipa_hors_plafond` | pas_encore_modelisee | Les fonctionnaires qui ont touché la GIPA ont, pour la part qui dépasse le plafond de leurs primes, des points RAFP que le modèle ne compte… |
| `rco_points_gratuits_66` | pas_encore_modelisee | Les conjoints, aides familiaux et collaborateurs d'exploitation d'avant 2011 — près de 450 000 retraités en 2017, sept sur dix des femmes —… |
| `regies_ferroviaires_pensions_en_extinction` | pas_encore_modelisee | Les anciens agents des chemins de fer d'outre-mer et d'Afrique du Nord, nés pour la plupart avant 1940 : le modèle ne simule pas leurs serv… |
| `retrep_avantages_temporaires` | pas_encore_modelisee | Tous les maîtres et documentalistes du privé sous contrat qui partent aux âges des enseignants publics : ceux qui avaient quinze ans d'éche… |
| `service_civique` | pas_encore_modelisee | Tout assuré qui a accompli un service civique en France depuis le 14 mai 2010 : un contrat de six à douze mois valide aujourd'hui autant de… |
| `volontariat_civil_et_international` | pas_encore_modelisee | Tout assuré qui a accompli un volontariat civil, depuis le 15 mars 2000, ou un volontariat international en entreprise ou en administration… |
| `cultes_retraite_complementaire_taux_specifiques` | a_verifier | Le ministre dont la collectivité applique un taux spécifique cotise de 11 à 113 % de plus qu'au taux de base, et le modèle ne lui compte qu… |
| `fin_de_la_suspension_2028` | a_verifier | Tout changement de calendrier touche les générations 1965 et suivantes. |
| `abattement_rci` | approchee | Toute retraite du RCI liquidée avant le taux plein du régime de base. |
| `accident_du_travail_periodes_assimilees` | approchee | Carrières coupées d'un accident du travail ou d'une maladie professionnelle. |
| `age_ouverture_banque_de_france_actifs` | approchee | L'agent qui déclare un emploi de ces catégories liquide sa pension de la Banque dès son départ, cinq ans avant les autres : né en janvier 1… |
| `age_ouverture_ieg_actifs` | approchee | LA SUSPENSION NE CHANGE RIEN, MAIS LA FICHE ÉTAIT FAUSSE. |
| `age_reference_decote_ieg` | approchee | La fiche portait l'âge d'ouverture majoré de CINQ ans — 63,75 ans pour les liquidations de 2025-2026, 64 ans ensuite —, règle d'avant la ré… |
| `age_reference_decote_sncf_ratp` | approchee | Les deux fiches faisaient monter l'âge de référence avec l'âge d'ouverture, cinq ans au-dessus : 57,25 ans pour les liquidations de 2025, j… |
| `age_surcote_sncf_ratp` | approchee | Le modèle comptait la surcote depuis l'âge d'ouverture de la fiche — cinquante-quatre ans pour un agent de conduite né en 1980. |
| `agirc_arrco_valeur_achat` | approchee | Toute carrière qui cotise à l'Agirc-Arrco après 2026 : ses points de ces années coûtent le salaire moyen et non les prix, environ 0,7 % de… |
| `agirc_arrco_valeur_service` | approchee | Tout départ antérieur au relèvement de son année : la complémentaire baisse de 4,87 % pour un départ de janvier à octobre 2022, de 4,67 % a… |
| `apprentissage` | approchee | Les apprentis depuis 2014 : 878 871 contrats commencés en 2024 (DARES). |
| `assiette_minimale_agricole` | approchee | Les chefs d'exploitation aux revenus faibles, et, à la complémentaire, tous les chefs qui cotisent depuis 2017. |
| `assiette_minimale_independants` | approchee | Un indépendant à 3 000 € validait un trimestre au lieu de trois et n'avait ni le salaire ni les points du minimum. |
| `assiette_rco_independants` | approchee | Les artisans de 1979 à 2012 et les commerçants de 2004 à 2012. |
| `assiette_sociale_independants` | approchee | Les indépendants non agricoles, pour leurs revenus depuis 2025 : rien sur leurs droits, que la caisse calcule sur l'assiette que la carrièr… |
| `asv_autres_professions_de_sante` | approchee | Un infirmier né en 1960, au salaire moyen de 25 à 65 ans : ses PCV valent 1 642 € par an, un dixième de sa pension, qui les ignorait |
| `asv_medecins_ajustement` | approchee | La fiche servait 36 points à tout médecin, soit jusqu'à 7,75 points de trop sous 70 000 €. |
| `asv_medecins_points` | approchee | Les médecins libéraux conventionnés : près du tiers de la pension d'un médecin de secteur 1 |
| `baremes_cnbf` | approchee | Tout avocat. |
| `bonification_cinquieme_militaires` | approchee | Le militaire qui réunit dix-sept ans de services, quinze avant juillet 2011 : vingt trimestres à qui en a servi vingt-cinq, soit un cinquiè… |
| `bonification_cinquieme_police_penitentiaire` | approchee | Le policier ou le surveillant qui réunit la durée de l'âge minoré : vingt trimestres de services à qui en a servi vingt-cinq, soit jusqu'à… |
| `bonification_cinquieme_sapeurs_pompiers` | approchee | Le sapeur-pompier professionnel qui réunit ses durées : vingt trimestres à qui a servi vingt-cinq ans en cette qualité, sous le maximum de… |
| `cafat_pension_de_base` | approchee | Les salariés de Nouvelle-Calédonie : leur pension est simulée en points au bon âge de liquidation et au rendement de l'année de leur départ… |
| `carcdsf_minoration_age_seul` | approchee | La fiche lisait 62 et 67 ans et la décote du régime de base, que la durée annule : un dentiste parti à 64 ans avec sa durée ne perdait rien… |
| `carmf_asv_minoration_enfants` | approchee | De 2000 à 2016, la fiche disait l'âge seul sans que le moteur le lise : un médecin parti à 64 ans avec sa durée n'était pas minoré. |
| `carpimko_ages_2015` | approchee | La fiche lisait 67 ans dès la génération 1955 |
| `carpimko_assiette_2026` | approchee | La fiche retranchait un demi-plafond de tout revenu et reconduisait le rendement de 2025, 7,36 % : un tiers de points de trop au-dessus d'u… |
| `carpv_minoration_age_seul` | approchee | La fiche écrivait la règle d'âge en laissant sa durée requise vide |
| `cavamac_minoration_age_seul` | approchee | La fiche opposait la décote du régime de base, que la durée annule : un agent général parti à l'âge légal avec sa durée ne perdait rien de… |
| `cavec_minoration_age_seul` | approchee | La note de la fiche disait la règle, mais la période laissait la durée annuler la minoration, et lisait avant 2008 les âges du régime génér… |
| `cavom_ages_minoration` | approchee | La fiche lisait les tables du régime général et la décote du régime de base, que la durée annule : un officier ministériel parti à l'âge lé… |
| `cavp_minoration_deux_pentes` | approchee | La fiche lisait la décote du régime de base, que la durée annule : un pharmacien parti à 64 ans avec sa durée ne perdait rien de sa complém… |
| `cese_pension_des_membres` | approchee | Les anciens membres du CESE désignés avant le 1er septembre 2023 : leurs annuités d'avant 2014 se liquident désormais à leur pourcentage, a… |
| `chomage_retraite_complementaire` | approchee | Une année de solidarité vaut, depuis 2019, un tiers de points de moins sur la tranche 1 et les trois quarts de moins sur la tranche 2 qu'un… |
| `cipav_seconde_tranche` | approchee | Un libéral de la Cipav au-delà de trois plafonds achetait trop peu de points depuis 2024 : la fiche coupait la seconde tranche à trois. |
| `clr_nouvelle_caledonie_pension_des_fonctionnaires` | approchee | Les fonctionnaires de Nouvelle-Calédonie : leur pension est simulée au bon âge et au bon taux par annuité, mais sans minoration ni réductio… |
| `cnavpl_allocation_avant_2004` | approchee | Tout libéral parti de 60 à 64 ans avant 2004 : le modèle le disait non ouvert à la base, qu'il n'ouvrait qu'à 65 ans, et la lui servait pou… |
| `cnavpl_majoration_duree_assurance` | approchee | La fiche les disait non portés, et le moteur ne cherchait la majoration de durée que dans les régimes en annuités : une libérale qui n'avai… |
| `cnavpl_valeur_service` | approchee | Le dépôt ne lisait la valeur que dans les recueils, depuis 2021, et ramenait celle de 2021 vers le passé par les prix : les pensions de bas… |
| `coefficient_anticipation_ircantec` | approchee | Toute liquidation anticipée de l'Ircantec, et des points de l'IPACTE et de l'IGRANTE qu'elle a repris. |
| `coefficients_anticipation_agirc_1947` | approchee | Le cadre dont la pension de l'Agirc prend effet avant 1955 : 0,72 au lieu de 0,78 à soixante ans, 0,93 au lieu de 0,96 à soixante-quatre, e… |
| `coefficients_anticipation_agirc_arrco` | approchee | Toute liquidation anticipée d'une complémentaire des salariés du privé : 1 % à 22 % de moins sur vingt trimestres, jusqu'à 57 % dix ans ava… |
| `complement_differentiel_rco` | approchee | Les chefs d'exploitation de dix-sept ans et demi liquidant au taux plein depuis 2015 : le moteur servait leurs points de RCO seuls |
| `conge_supplementaire_naissance` | approchee | Les parents qui prennent le congé supplémentaire de naissance depuis le 1er juillet 2026 : un trimestre par cinquante-huit jours, que le mo… |
| `cotisation_maladie_des_non_residents` | approchee | Tout retraité qui déclare résider hors de France : plus de CSG ni de CRDS ni de CASA |
| `cotisation_maladie_pensions_complementaires` | approchee | Tout salarié ou contractuel dont la pension du système actuel comprend une complémentaire : sa pension nette baisse de 1 % de cette part, s… |
| `cotisation_par_classes_liberales` | approchee | Les vétérinaires, les experts-comptables et commissaires aux comptes, et les affiliés de la Cipav jusqu'en 2022. |
| `cotisation_rco_agricole_2026` | approchee | Tous les chefs d'exploitation qui cotisent depuis 2026. |
| `cotisation_vieillesse_agricole_avant_2003` | approchee | Les chefs d'exploitation et les membres de leur famille qui ont cotisé avant 2003. |
| `cotisation_vieillesse_independants` | approchee | Artisans, commerçants et libéraux non réglementés, depuis 2018 : sous le plafond, presque rien (17,75 % des deux côtés jusqu'en 2023, 0,12… |
| `cotisation_vieillesse_independants_mayotte` | approchee | L'artisane de Mayotte à 10 000 € par an cotise 585 € en 2019, au lieu de 1 775 €, et 935 € en 2024 |
| `cprn_ages_decote_enfants` | approchee | La fiche lisait les âges du régime général et laissait la durée annuler la décote : un notaire parti à l'âge légal avec sa durée ne perdait… |
| `cps_polynesie_pension_des_salaries` | approchee | Les salariés de Polynésie française : leur pension de tranche A est simulée au bon âge et à la bonne durée, mais sur un salaire de référenc… |
| `crpn_pension_des_navigants` | approchee | Les navigants de l'aéronautique civile : leur pension de la caisse est simulée sans la majoration temporaire de cinquante-cinq ans à l'âge… |
| `csg_des_pensions_selon_le_revenu` | approchee | Tout retraité en mode net : un foyer d'une part sous 13 048 € de revenu fiscal n'est plus prélevé |
| `cultes_fractions_de_pension` | approchee | Les ministres des cultes et les membres des congrégations, au scénario 1, partis à soixante-quatre ans : + 98 % nés en 1925, + 30 % en 1945… |
| `cultes_retraite_complementaire` | approchee | Ministres des cultes rémunérés, depuis 2006 : le modèle ne leur routait que la CAVIMAC. |
| `cultes_salaire_annuel_moyen` | approchee | Le salaire annuel moyen est fait du forfait de chaque année, dans les deux moteurs (`assiette_de_reference`) : le ministre déclaré à une fo… |
| `cumul_emploi_retraite_complementaire_des_independants` | approchee | L'artisan ou le commerçant qui travaille avant le taux plein : sa complémentaire, que le modèle servait entière, est suspendue avec sa base… |
| `cumul_emploi_retraite_complementaires_des_liberaux` | approchee | Le libéral qui reprend une activité libérale avant le taux plein, au-delà du plafond de la sécurité sociale : la dentiste partie avant 2015… |
| `cumul_emploi_retraite_et_retraite_progressive` | approchee | Le retraité qui travaille avant le taux plein : la salariée née en 1960, partie à 62 ans en 2022 sans la durée requise, qui reprend un empl… |
| `cumul_emploi_retraite_fonction_publique` | approchee | Le fonctionnaire retraité qui travaille avant le taux plein : payé par un employeur public, ou par tout employeur s'il est civil et parti d… |
| `cumul_emploi_retraite_ircantec` | approchee | L'agent contractuel qui reprend un emploi de contractuel public avant le taux plein : de 2004 à 2020, son allocation, que le modèle servait… |
| `cumul_emploi_retraite_rco_agricole` | approchee | L'exploitant qui reprend une activité agricole non salariée : sa complémentaire, comme sa base, est servie entière, le résultat disant que… |
| `decompte_des_services_fonction_publique` | approchee | Les fonctionnaires dont l'année d'entrée et celle du départ sont entamées : la fraction qu'elles laissent fait un trimestre de plus au déco… |
| `decompte_des_services_regimes_speciaux` | approchee | Les agents dont l'année d'entrée et celle du départ sont entamées : un trimestre liquidable de plus, et un trimestre de décote de moins ou… |
| `decote_avant_1983` | approchee | Les pensions du régime général et des salariés agricoles qui prennent effet avant le 1er avril 1983, et celles des artisans et commerçants… |
| `decote_banque_de_france` | approchee | Le dépôt opposait à l'agent le barème de l'article L. |
| `decote_crpn` | approchee | L'âge d'annulation passe de 65 à 60 ans pour toute liquidation depuis 2012, et la décote se compte sur la durée seule depuis 2022, sur 21 à… |
| `depart_anticipe_parents_trois_enfants` | approchee | La mère de trois enfants fonctionnaire qui avait quinze ans de services avant 2012 : son droit s'ouvre à la date où elle réunit les conditi… |
| `deputes_pension_des_anciens_deputes` | approchee | Les anciens députés et, par assimilation, les anciens sénateurs : leur pension est simulée au droit lu |
| `droits_apres_la_premiere_pension` | approchee | Toute personne qui travaille après sa première pension, dans le même régime ou dans un autre : le fonctionnaire de catégorie active parti à… |
| `duree_requise_ieg` | approchee | La fiche lisait la table commune, suspension de 2026 comprise. |
| `duree_requise_sncf_ratp` | approchee | Les deux fiches lisaient la table commune, suspension de 2026 comprise. |
| `enfants_crpcen` | approchee | Toute mère clerc ou employée de notaire : quatre trimestres au taux par enfant né avant le 1er juillet 2006 |
| `enfants_fonction_publique` | approchee | Toute mère fonctionnaire ou agente d'un régime spécial : quatre trimestres par enfant né avant 2004, en services, donc au prorata de la pen… |
| `enfants_ieg` | approchee | Toute mère agente des IEG : quatre trimestres de services par enfant né avant le 1er juillet 2008, et non avant 2004, huit pour le second d… |
| `enfants_ratp` | approchee | Toute mère agente de la RATP : quatre trimestres de services par enfant né avant le 1er juillet 2008, et non avant 2004 |
| `enfants_sncf` | approchee | Toute mère agente de la SNCF : deux trimestres de durée par enfant né après son recrutement, et plus aucun trimestre de services |
| `exoneration_independants_outre_mer` | approchee | Un artisan de La Réunion qui déclare 300 € en 2010 validait un trimestre sur l'assiette minimale, 200 SMIC horaires (1 772 €), portée à son… |
| `fin_indemnisation_chomage` | approchee | Les carrières qui finissent au chômage après le taux plein : jusqu'au 3 octobre 2026, le modèle servait l'allocation jusqu'au départ, si ta… |
| `financement_chomage_complementaire` | approchee | Le compte d'une année chômée descend, aux scénarios 2, 4 et 6, de la cotisation entière à ce que l'Unédic ou l'État versait : treize témoin… |
| `garantie_minimale_points_agirc` | approchee | Tout cadre payé sous le salaire charnière entre 1989 et 2018 — 1,11 plafond en 2018 —, surtout en début de carrière. |
| `igrante_points` | approchee | Les agents non titulaires de l'État et des collectivités de 1960 à 1970, et ceux qui ont validé des services antérieurs : leurs points IGRA… |
| `inaptitude_au_travail` | approchee | Les retraités partis au taux plein pour inaptitude : 1,36 million fin 2016 (DREES, EIR), et avec les ex-invalides 19 % des nouveaux retrait… |
| `indemnite_de_feu_sapeurs_pompiers` | approchee | Le sapeur-pompier professionnel : sa pension se liquide sur son traitement majoré de l'indemnité au prorata de ses années de sapeur-pompier |
| `indemnite_sujetions_speciales_police` | approchee | Le policier : sa retenue pour pension passe de 11,10 à 13,30 % de son traitement et de son indemnité |
| `ipacte_points` | approchee | Les agents contractuels de l'État et des collectivités payés au-dessus du plafond de 1951 à 1970, aujourd'hui nés avant 1950 environ : leur… |
| `ircantec_valeurs_point` | approchee | Toute pension Ircantec qui compte des cotisations postérieures au dernier barème : elles donnent, au rendement de 7,63 %, ce qu'achèterait… |
| `limite_age_banque_de_france` | approchee | Tout agent titulaire de la Banque de France, affilié au régime spécial, dont le départ saisi passe sa limite depuis le 26 juillet 2012 — so… |
| `limite_age_contractuels` | approchee | Tout agent contractuel dont le départ saisi passe soixante-sept ans (soixante-cinq avant le 1er juillet 2011, relevés de quatre mois à deux… |
| `limite_age_fonction_publique` | approchee | Tout fonctionnaire civil dont le départ saisi passe sa limite d'âge est radié des cadres à la limite reculée et prolongée par les exception… |
| `limite_age_ieg` | approchee | Tout agent des industries électriques et gazières, affilié au régime spécial, dont le départ saisi passe sa limite est mis en inactivité à… |
| `limite_age_militaires` | approchee | Tout militaire dont le départ saisi passe la limite la plus haute de sa catégorie — cinquante-neuf ans pour le non-officier, soixante-six p… |
| `limite_age_mines` | approchee | Tout mineur affilié au régime spécial dont le départ saisi passe cinquante-cinq ans, depuis le 18 janvier 1954, a passé sa limite d'âge, et… |
| `limite_age_opera` | approchee | Tout agent de l'Opéra national de Paris, affilié au régime spécial, dont le départ saisi passe soixante-cinq ans depuis le 1er juillet 2008… |
| `limite_age_ouvriers_etat` | approchee | Tout ouvrier de l'État dont le départ saisi passe sa limite — soixante-sept ans pour les générations nées depuis 1955, soixante-deux pour l… |
| `limite_age_seita` | approchee | Tout agent de la SEITA, affilié au régime spécial, dont le départ saisi passe soixante-cinq ans est mis à la retraite à cette limite, et sa… |
| `limite_age_sncf_ratp` | approchee | Tout agent de la SNCF ou de la RATP, affilié au régime spécial, dont le départ saisi passe soixante-cinq ans depuis 2010 — soixante-sept po… |
| `liquidation_regime_par_regime` | approchee | Tout polypensionné dont les régimes n'ouvrent pas au même âge : le fonctionnaire de catégorie active ou le militaire qui a aussi travaillé… |
| `maintien_affiliation_crpcen_ieg` | approchee | Les clercs et les agents des IEG recrutés avant le 1er septembre 2023 qui quittent le statut et y reviennent : le retour que rien ne mainti… |
| `majoration_conjoint_a_charge` | approchee | Le retraité du régime général parti avant 2011, dont le conjoint sans pension a eu soixante-cinq ans avant 2011, reçoit 609,80 € par an au… |
| `majoration_duree_apres_65_ans` | approchee | Les assurés du régime général, des salariés agricoles et des artisans et commerçants qui liquident après l'âge du taux plein sans la durée… |
| `majoration_duree_assurance_enfants` | approchee | Toute mère affiliée au régime général ou à un régime aligné : la règle commande la décote, la proratisation, la surcote parentale et le sal… |
| `majoration_duree_hospitaliers_actifs` | approchee | L'aide-soignant ou l'agent hospitalier actif : quinze trimestres pour trente-sept ans et demi de services, qui effacent la décote de qui pa… |
| `majoration_enfants_a_charge_agirc_arrco` | approchee | Le salarié du privé qui part avec un enfant de moins de dix-huit ans voit sa complémentaire majorée de 5 % par enfant, au lieu de la majora… |
| `majoration_enfants_agirc_arrco` | approchee | Parents de trois enfants salariés du privé avant 2019. |
| `majoration_enfants_liberaux_avocats` | approchee | Les fiches de la CNAVPL, de la CNBF et de sa complémentaire ne la portaient pas : 10 % de pension en moins pour tout parent de trois enfant… |
| `majoration_enfants_plafond_fonction_publique` | approchee | Les pensions du code des pensions que la majoration pour enfants porterait au-delà du traitement : sans surcote, à partir de sept enfants a… |
| `majoration_exceptionnelle_2023` | approchee | Les retraités du régime général, des indépendants, des salariés agricoles et des cultes partis avant le 1er septembre 2023 au taux plein av… |
| `majoration_retraite_proportionnelle` | approchee | Les chefs partis avant 1997, de 1997 à 2008 : une carrière complète à faible revenu partie en 1995 reçoit 2 036 € de plus en 2008. |
| `marins_bonification_enfants` | approchee | La fiche ne déclarait aucune majoration pour enfants : un marin père de deux enfants perdait 5 % de pension, de trois enfants 10 %. |
| `marins_ouverture_cinquante_ans` | approchee | La fiche opposait cinquante-cinq ans à tout marin : c'est l'âge qui borne l'entrée en jouissance de celui qui CONTINUE à naviguer (L. |
| `marins_salaire_de_reference` | approchee | Le modèle prend la catégorie de la DERNIÈRE année, rangée par le revenu, et compte les services au trimestre |
| `mayotte_pension_de_base` | approchee | Les salariés de Mayotte : leur pension est simulée au droit depuis 2003, à leur salaire moyen près pour les nés avant 1965, et à leurs trim… |
| `micro_social_abattement` | approchee | Le micro-entrepreneur saisit son chiffre d'affaires mensuel et son activité (champ « micro »), que la saisie abat avant de le donner au mod… |
| `minimum_contributif` | approchee | Petites pensions au taux plein. |
| `minimum_contributif_international` | approchee | Les petites pensions françaises des carrières internationales, au taux plein par la totalisation : le minimum de la pension proratisée se r… |
| `minimum_pension_sncf` | approchee | Les petites pensions d'ancienneté de la SNCF — l'agent à 30 % du salaire moyen parti à cinquante-cinq ans en 2010 passe de 6 461 € à 13 653… |
| `minimum_vieillesse` | approchee | Les plus petites pensions. |
| `minoration_ircec` | approchee | Tout départ anticipé d'un artiste-auteur, d'un auteur dramatique ou d'un compositeur qui n'a pas sa durée : à soixante-deux ans, 20 % de mi… |
| `minoration_racl_2014_2024` | approchee | Les auteurs et compositeurs lyriques partis avant l'âge du taux plein, de 2014 à mai 2025. |
| `organic_conjoints_de_commercants` | approchee | Les industriels et commerçants qui ont cotisé de 1973 à 2003, et leurs conjoints : la cotisation additionnelle est portée, mais pas les poi… |
| `pension_d_invalidite_substituee` | approchee | Les titulaires d'une pension d'invalidité à l'âge légal : 0,90 million de retraités partis au taux plein à ce titre fin 2016 (DREES, EIR). |
| `pension_majoree_reference` | approchee | Les petites pensions de base des chefs d'exploitation liquidées au taux plein depuis 2009 : le moteur ne servait que le calcul contributif,… |
| `pension_maximale_regime_general` | approchee | L'assuré du régime général dont la pension calculée passe la moitié du plafond — un salaire annuel moyen au-dessus du plafond de l'année, q… |
| `pension_mines` | approchee | Mineurs. |
| `pension_non_salaries_agricoles_2026` | approchee | Les chefs d'exploitation dont la pension prend effet depuis le 1er janvier 2026, et le salaire annuel moyen de leurs régimes alignés quand… |
| `pension_proratisee` | approchee | Toute pension française d'une carrière passée aussi par un État lié à la France par un accord qui compare : la pension proratisée, au taux… |
| `points_agricoles_au_revenu_cadastral` | approchee | Jusqu'au 20 novembre 2026, le moteur ne donnait aucun point aux années d'avant 1990 : il les servait par le rendement de leurs cotisations,… |
| `points_au_prorata_des_cotisations` | approchee | Les libéraux dont une année est incomplète au régime de base de la CNAVPL : le début d'activité, l'année du départ. |
| `points_avant_1973_independants` | approchee | Les artisans et commerçants en activité avant 1973, nés avant 1958 environ. |
| `priorite_majorations_enfants` | approchee | Toute mère passée par un régime spécial et par un régime aligné. |
| `prolongation_activite_carriere_incomplete` | approchee | Le fonctionnaire civil dont le départ saisi passe sa limite d'âge sans la durée du taux maximum est maintenu, depuis 2004, jusqu'à cette du… |
| `prolongation_activite_categorie_active` | approchee | Le fonctionnaire actif dont le départ saisi passe sa limite d'âge est maintenu, depuis 2010, jusqu'à la limite des sédentaires de sa généra… |
| `raap_classe_speciale` | approchee | La fiche prélevait 8 % du revenu avant 2016 — un taux qu'aucun texte ne porte — et servait donc, à un revenu moyen, quatre à six fois les p… |
| `rafp_beneficiaires` | approchee | Les deux statuts d'ouvrier de l'État, que le routage affiliait au RAFP de 2005 au 28 septembre 2026 : ils n'y cotisent plus, et la rente se… |
| `rafp_majoration_capital` | approchee | Tout fonctionnaire qui touche son RAFP hors d'un âge entier, ou avant mars 2015 : jusqu'à 5,4 % de plus qu'au barème par âge entier, à 74 a… |
| `ravgdt_allocation_viagere` | approchee | Les gérants de débits de tabac et leurs conjoints : leur allocation viagère, que le modèle sert à soixante-cinq ans, et sans doute à un ren… |
| `recul_limite_age_enfants` | approchee | Le fonctionnaire civil dont le départ saisi passe sa limite d'âge y gagne un an par enfant de moins de vingt ans quand il l'atteint, trois… |
| `relevement_des_exploitants_2023` | approchee | Les chefs d'exploitation partis avant le 1er septembre 2023 au taux plein par l'âge ou l'inaptitude, sans la durée requise tous régimes : l… |
| `residence_et_minimum_vieillesse` | approchee | Les retraités qui vivent hors de France : 1,28 million fin 2024 (DREES, enquête annuelle auprès des caisses). |
| `retraite_anticipee_handicap` | approchee | Les assurés qui ont cotisé en situation de handicap, depuis 2015 : le modèle leur ouvre ce départ à leur âge, au taux plein, leur pension m… |
| `retraite_pour_invalidite_fonction_publique` | approchee | Les fonctionnaires radiés des cadres pour invalidité, à tout âge. |
| `retraite_progressive` | approchee | Les salariés, les indépendants et, depuis 2023, les fonctionnaires, les libéraux et les avocats qui passent à temps partiel en fin de carri… |
| `retraite_proportionnelle_msa` | approchee | Les chefs d'exploitation, pour leurs années depuis 1990. |
| `revenu_annuel_moyen_independants` | approchee | Artisans et commerçants nés de 1935 à 1952, partis avant 2026 : leur revenu moyen porte sur une à cinq meilleures années de moins que celui… |
| `reversion` | approchee | Tout conjoint, ou ex-conjoint, d'un assuré du régime général ou d'un régime aligné qui décède : 4,41 millions de bénéficiaires d'un droit d… |
| `reversion_agirc_arrco` | approchee | Tout conjoint, ou ex-conjoint marié, d'un salarié ou ancien salarié du privé qui décède. |
| `reversion_carcdsf` | approchee | Tout conjoint, ou ex-conjoint non remarié, d'un chirurgien-dentiste ou d'une sage-femme qui décède depuis le 11 octobre 2007. |
| `reversion_cavamac` | approchee | Tout conjoint, ou conjoint divorcé, d'un agent général d'assurance qui décède depuis le 1er juillet 2011. |
| `reversion_crpcen` | approchee | Tout conjoint d'un clerc ou employé de notaire : la moitié de sa pension, sans âge ni ressources, dès que le mariage remplit la condition d… |
| `reversion_fonction_publique` | approchee | Tout conjoint, ou ex-conjoint, d'un fonctionnaire de l'État ou d'un agent des collectivités qui décède. |
| `reversion_fspoeie` | approchee | Tout conjoint, ou ex-conjoint, d'un ouvrier de l'État qui décède : la moitié de sa pension, sans âge ni ressources, dès que le mariage remp… |
| `reversion_ieg` | approchee | Tout conjoint d'un agent des IEG : la moitié de sa pension, majoration pour enfants comprise, sans âge ni ressources, partagée avec les ex-… |
| `reversion_ircantec` | approchee | Tout conjoint, ou ex-conjoint, d'un agent contractuel de l'État, des collectivités ou des hôpitaux, ou d'un élu local, qui décède. |
| `reversion_rafp` | approchee | Tout conjoint, ou ex-conjoint, d'un fonctionnaire de l'État ou d'un agent des collectivités et des hôpitaux qui décède. |
| `reversion_rci` | approchee | Tout conjoint, ou ex-conjoint, d'un artisan, d'un commerçant ou d'un industriel qui décède depuis 2013. |
| `reversion_sncf` | approchee | Tout conjoint d'un agent de la SNCF : la moitié de sa pension, majorée pour enfants, sans âge ni ressources, dès que le mariage remplit la… |
| `saint_pierre_et_miquelon_pension_de_base` | approchee | Les assurés de Saint-Pierre-et-Miquelon : leur pension est simulée au droit pour l'âge et la durée, mais sur un revenu moyen de trop peu d'… |
| `salaire_annuel_moyen` | approchee | Toute pension en annuités du régime général et des salariés agricoles. |
| `sam_annees_d_avant_1947` | approchee | Les assurés qui ont cotisé avant 1947 et comptent, après, moins d'années que le nombre retenu : nés avant 1933 pour l'essentiel. |
| `sam_indemnites_de_maternite` | approchee | Les mères salariées. |
| `sam_parents_24_23` | approchee | Mères (par défaut dans le modèle) liquidant depuis septembre 2026 : +1 à +2 % de salaire de référence. |
| `seconde_pension` | approchee | Les retraités en cumul intégral depuis 2023 : leurs cotisations, jusque-là à fonds perdus, leur ouvrent une seconde pension, au plus 5 % du… |
| `sections_liberales_majoration_enfants` | approchee | Aucune des trois fiches ne la portait avant le 23 septembre 2026 : 10 % de complémentaire en moins pour tout parent de trois enfants. |
| `services_passes_outre_mer` | approchee | Les salariés de Nouvelle-Calédonie, et d'un an ceux de Saint-Pierre-et-Miquelon. |
| `sportifs_haut_niveau` | approchee | Les sportifs inscrits sur la liste de haut niveau depuis 2012, à faibles ressources : jusqu'à quatre trimestres par an, trente-deux en tout… |
| `stages_formation_professionnelle` | approchee | Les stagiaires de la formation professionnelle depuis 2015, et les anciens des TUC et des stages d'insertion des années 1977 à 1992 partis… |
| `surcote_banque_de_france` | approchee | Le dépôt servait à tous les trimestres accomplis depuis l'âge d'ouverture le taux de l'année du départ : 0,75 % en 2008, 1,25 % depuis 2009… |
| `surcote_ircantec` | approchee | Les affiliés de l'Ircantec qui cotisent après l'âge légal au-delà de la durée requise, ou qui liquident après l'âge du taux plein automatiq… |
| `surcote_par_age_seul` | approchee | Les complémentaires de la CARMF, de la CARPIMKO, de la CAVEC, de la CAVP, de la Cipav et de la CPRN, et l'ASV des médecins, dont les périod… |
| `taux_plein_a_soixante_cinq_ans` | approchee | Les parents de trois enfants nés de juillet 1951 à décembre 1955 qui ont cessé ou réduit leur activité après une naissance, et que la saisi… |
| `taux_plein_anciens_combattants_prisonniers` | approchee | L'ancien prisonnier ou combattant qui n'a pas la durée requise reçoit le taux plein avant l'âge du taux plein, d'autant plus tôt que sa cap… |
| `taux_plein_anciens_deportes_internes` | approchee | L'ancien déporté ou interné qui n'a pas la durée requise reçoit le taux plein, sans décote, au régime général, chez les salariés agricoles,… |
| `taux_plein_meres_de_famille_ouvrieres` | approchee | La mère de trois enfants qui a trente ans d'assurance, majoration comprise, et a été ouvrière cinq des quinze dernières années, a le taux p… |
| `taux_plein_travailleurs_manuels` | approchee | Le travailleur manuel parti de 1976 à 1983, entre soixante et soixante-cinq ans, avec quarante et un à quarante-trois ans d'assurance, assu… |
| `temps_partiel_fonction_publique` | approchee | Tout fonctionnaire qui a travaillé à temps partiel. |
| `totalisation_des_periodes_etrangeres` | approchee | Toute personne qui a travaillé hors de France : 1,28 million de retraités résidaient à l'étranger fin 2024 (DREES, enquête annuelle auprès… |
| `trimestres_au_revenu` | approchee | L'année d'entrée, ou de retour, d'un salarié, d'un artisan ou d'un commerçant. |
| `trimestres_avant_1972` | approchee | Les années travaillées de 1946 à 1971 dont le salaire n'atteint pas quatre fois le seuil : 9 à 14 % du salaire moyen pour quatre trimestres… |
| `un_statut_par_annee` | approchee | DEPUIS LE 22 SEPTEMBRE 2026, DEUX ACTIVITÉS À LA FOIS se décrivent, dans les deux moteurs : chacune verse à son régime, sur son revenu, et… |
| `versement_forfaitaire_unique` | approchee | L'assuré du régime général dont la pension annuelle, majoration pour enfants comprise, passe sous le seuil — 26,68 € en 1974, 156,24 € en 2… |
| `versement_unique_agirc_arrco` | approchee | Le salarié dont l'allocation de l'Agirc-Arrco n'excède pas cent points — 143,86 € par an en 2026 — reçoit sa valeur viagère en une fois : 3… |
| `versement_unique_ircantec` | approchee | Le contractuel de la fonction publique qui a moins de 300 points de l'Ircantec reçoit ses points au salaire de référence de l'année précéde… |
| `versement_unique_rci` | approchee | L'artisane de 2020 qui a déclaré 4 000 € : 15,83 points, servis 19,33 € par an |
| `wallis_et_futuna_pension_des_salaries` | approchee | Les salariés de Wallis-et-Futuna : leur pension est simulée à 60 ans au barème jusqu'à trente ans, et leur cotisation au taux de la retraite |

**Un état peut-être périmé.** Pour 36 des 186 règles approchées, l'effet raconte à l'imparfait l'erreur qui a été corrigée, sans dire ce qui reste. Le tableau ne peut pas savoir si elles sont encore approchées : leur fiche le dira quand elle mûrira, l'écart actuel dans ses approximations, le récit dans son historique.

**Des approximations non déclarées.** 13 des 186 fiches approchées ne déclarent encore ses approximations, chacune avec son effet ou « non mesuré » : l'effet n'en est dit qu'en mots.

**Les exemples officiels que le modèle ne reproduit pas**, entrés en écart connu, avec la règle qui le déclare :

| Exemple | Grandeur | Publié | Modèle | Règle |
|---|---|---|---|---|
| `cnav_22_83_taux_acquis_117_trimestres` | taux_liquidation | 0,55 | 0,5 | `decote_avant_1983` |
| `cnav_22_83_taux_acquis_117_trimestres` | pension_base_sur_sam | 0,429 | 0,44 | `decote_avant_1983` |
| `cnav_2005_17_derniere_revision_sans_droit_propre` | dates_de_derniere_revision_de_la_reversion | regime_general 2013-09-01 | regime_general 2014-11-01 | `reversion` |
| `cnav_2006_37_revision_au_constat` | dates_de_revision_de_la_reversion | regime_general 2007-03-01 | regime_general 2007-02-01 | `reversion` |
| `ur_reversion_etat_mariage_3_ans_et_demi` | reversions_mensuelles | fonction_publique_etat 0, rafp 0 | fonction_publique_etat 0, rafp 50 | `reversion_rafp` |
| `ur_reversion_prive_ressources_plafond_2024` | reversions_mensuelles | regime_general 0, agirc_arrco 420 | regime_general 33,47, agirc_arrco 420 | `reversion` |
| `erafp_1958_effet_2026_11_8000_points` | prestation_rafp | forme rente, age_legal 64, coefficient 1,3, rente_mensuelle 49,15 | forme rente, age_legal 62, coefficient 1,29667, rente_mensuelle 49,02 | `rafp_majoration_capital` |
| `erafp_1963_effet_2026_11_5000_points` | prestation_rafp | forme capital_fractionne, age_legal 62,75, coefficient 1,05, premiere_fraction 99,24 | forme capital_fractionne, age_legal 62,75, coefficient 1,05333, premiere_fraction 99,56 | `rafp_majoration_capital` |
| `erafp_ra2012_jean_capital_62_ans` | prestation_rafp | forme capital, coefficient 1,08, conversion 24,62, capital 4030,38 | forme capital, coefficient 1,08, conversion 24,62, capital 4030,88 | `rafp_majoration_capital` |

**Les parties que la carte de justesse calcule fausses** (section 1) : un écart y est établi. Chacune attend le numéro de l'action qui la corrige, qu'une preuve nomme (`data/reference/preuves/`) ; un écart né d'un exemple officiel n'en porte pas encore.

- `decote_avant_1983` : en écart avec `cnav_22_83_taux_acquis_117_trimestres` ; aucune action nommée par une preuve.
- `minimum_pension_ieg / assiette_minimale_avant_2008`, `minimum_pension_ieg / minimum_2008` : règle connue, absente du modèle ; aucune action nommée par une preuve.
- `pension_maximale_regime_general / cinquante_pour_cent_du_plafond` : en écart avec `cnav_22_83_taux_acquis_117_trimestres` ; aucune action nommée par une preuve.
- `rafp_majoration_capital / deliberation_2005`, `rafp_majoration_capital / fractionnement_2024` : en écart avec `erafp_1958_effet_2026_11_8000_points`, `erafp_1963_effet_2026_11_5000_points`, `erafp_ra2012_jean_capital_62_ans` ; aucune action nommée par une preuve.
- `reversion / abattement_2005`, `reversion / age_52`, `reversion / minimum_2026` : en écart avec `cnav_2005_17_derniere_revision_sans_droit_propre`, `cnav_2006_37_revision_au_constat`, `ur_reversion_prive_ressources_plafond_2024` ; aucune action nommée par une preuve.
- `reversion_agirc_arrco / accord_2017` : en écart avec `ur_reversion_prive_ressources_plafond_2024` ; aucune action nommée par une preuve.
- `reversion_fonction_publique / complement_aspa_2025` : en écart avec `ur_reversion_etat_mariage_3_ans_et_demi` ; aucune action nommée par une preuve.
- `reversion_rafp / decret_2004` : en écart avec `ur_reversion_etat_mariage_3_ans_et_demi` ; aucune action nommée par une preuve.
- `sam_indemnites_de_maternite / forfait_des_conges_d_avant_2012` : en écart avec `grille_sam_maternite_forfait_2023` ; action 194.

## 3. Ce qui reste à faire, et par quoi commencer

- **Les 30 actions en cours** de la feuille de route :
  - 47. La garantie vieillesse est une avance : la reprise sur succession, sa règle et son chiffrage
  - 89. Dépouiller les 260 sources officielles remises le 22 septembre 2026
  - 129. Le taux de l'État ramené à sa part « retraite seule » : un réglage, puis le défaut
  - 130. L'architecture du dépôt : décidée, les phases 0 à 8 faites, les domaines à ouvrir
  - 131. Les dix fiches nées à la phase 6, relues à la source : les écarts qu'elles montrent, à corriger
  - 133. La retraite de base et ses complémentaires, sous le montant du système 1
  - 135. Aller plus vite sans rien céder : l'outillage d'un changement de résultats
  - 137. Les autres modèles publics : le registre exhaustif, puis leur confrontation
  - 138. Meilleur en tous points : ce que les autres modèles font mieux, vérifié, puis repris
  - 151. Partir très tard : le départ jusqu'au bout des tables de mortalité, puis la limite d'âge des fonctionnaires et ses exceptions
  - 152. Les cas types statutaires et non salariés à leur place dans l'EIR : le niveau et la carrière de chacun
  - 153. L'oracle au-delà des carrières simples : ce qu'OpenFisca calcule et que le dépôt ne lui confronte pas
  - 158. Les grilles indiciaires de la fonction publique : la carrière d'un fonctionnaire pré-remplie depuis son corps, plutôt que de mémoire
  - 159. Le jaune pensions du PLF 2027, exploité en entier : rangé, puis chaque tableau à sa place dans le dépôt
  - 161. Un seul exemplaire du code : les doublons entre le Python et le JavaScript retirés une paire à la fois, chaque retrait relu
  - 162. Le test d'abord : le développement piloté par les tests, sur tout le dépôt
  - 163. Ce que la revue de code d'Anthropic apprend au dépôt : le site en ligne au vert, les rouges classés, puis un relecteur
  - 174. Les notes Lighthouse au maximum, sur toutes les pages du site
  - 175. La base de législation de la Cnav, exploitée en entier par son API : chaque barème, exposé et circulaire à sa place dans le dépôt, puis tenue à jour
  - 176. Le portail statistique de la Cnav, exploité en entier : chaque série, recueil et étude à sa place dans le dépôt
  - 177. Les écarts que les barèmes de la Cnav ont trouvés au modèle : chacun corrigé dans les deux moteurs, ou sa limite dite
  - 178. Le panorama « Les retraités et les retraites » de la DREES, édition 2026, exploité en entier : chaque fiche à sa place dans le dépôt
  - 184. L'histoire d'un article de loi, lue dans l'index de la DILA : ce que le dépôt lexifina/global-law fait mieux, repris, et ce qu'il fait mal, écarté
  - 186. Le programme du parti sur les retraites : chaque grande idée étudiée à fond, aux sources, puis le modèle et le site qui la montrent
  - 187. Le moteur à part du site : le calcul d'une carrière en bibliothèque, que d'autres peuvent appeler, séparé commit après commit
  - 189. Le site à la charte du parti, puis lisible par l'électeur
  - 191. Les fiches de la carte, exécutables : le moteur lit chaque règle dans les versions de sa fiche, domaine par domaine
  - 192. Ce que la passe de lecture du 12 novembre a trouvé dans le modèle : chaque point lu, vérifié, puis écrit ou dit
  - 193. Les caisses de retraite, une par une, sur le site : comment chacune marche
  - 194. La carte de justesse : l'état de chaque partie du simulateur calculé depuis ses preuves, puis prouvé régime par régime
- **Les sources à exploiter** : 6 à explorer sur 332 (127 explorées, 198 épuisées). 0 d'entre elles visent un régime partiel, et pourraient le compléter :
  - et 4 sources sans régime désigné.
- **Les autres modèles** (§ 3.4) : 71 au registre (`data/reference/referents.yaml`) : 33 au code ouvert, 1 sur demande, 13 documenté(s) sans leur code, 24 non public(s). 29 ont déjà été confrontés au dépôt ou lui donnent des valeurs (Barèmes IPP, OpenFisca-France, OpenFisca-France-Pension, Destinie 2, Ines, TRAJECTOiRE, ANCETRE, legiretraite (paquet R), EDIFIS, Maquette globale de projection du COR, Maquette simplifiée du secrétariat général du COR, PRISME (Projection des Retraites, Simulations, Modélisation et Évaluations), Saphir, modele-ti, modele-social, modele-as, Catala (catala-examples), ir-catala, Calculette de l'impôt sur le revenu (code M), EUROMOD (France), Retraites 2027, Simulateur de dépense publique, volet retraites, « Quand pourrai-je partir à la retraite ? », Simulateur de SUD éducation, devcrafting/retraites, calcul-verification-pension-retraite, Simulateur de cas types de Nos Retraites, Les modèles de pension de l'OCDE, Ageing Report et ses fiches pays) ; le registre compte 243 écarts, dont 211 chez eux. Aucun n'est plus à confronter au scénario 1 en premier : tous ceux dont le code est ouvert et qui ne dépendent d'aucune autre source du registre l'ont été.
- **Ce que les autres modèles font mieux** (action 138) : 291 points, lus chez 66 modèles : 44 à reprendre, 48 à trancher par le propriétaire (des choix du programme), 150 repris, 10 écartés, 39 coupés (léger ou nul, déclaré sans être fait). Les points à reprendre, par chantier de la feuille de route : 138.2 (1), 138.3 (8), 138.5 (5), 138.7 (2), 138.8 (1), 138.11 (1), 138.12 (1), 138.14 (12), 138.18 (4), 138.19 (2), 155.1 (1), 155.2 (1), 155.3 (3), 156.1 (1), 157.1 (1).
- **Les fiches sans exemple officiel** : 210.
- **Les domaines sans décision** (§ 8) : 120 fiches du droit réel qu'aucun des 5 univers de la proposition ne décide. 86 disent leur étape, et c'est une décision qui manque : `agirc_arrco_valeur_achat`, `assiette_minimale_independants`, `assiette_rco_independants`, `assiette_sociale_independants`, `asv_autres_professions_de_sante`, `asv_medecins_ajustement`, `asv_medecins_points`, `carpimko_assiette_2026`, `cavom_assiette_2016`, `cci_paris_transfert_2006`, `cci_roubaix_transfert_1998`, `chomage_retraite_complementaire`, `cipav_seconde_tranche`, `compagnie_generale_eaux_transfert_1991`, `conjoint_collaborateur_independants`, `cotisation_agricole_de_1952`, `cotisation_maladie_des_non_residents`, `cotisation_maladie_pensions_complementaires`, `cotisation_rco_agricole_2026`, `cotisation_vieillesse_agricole_avant_2003`, `cotisation_vieillesse_independants`, `cotisation_vieillesse_independants_mayotte`, `credit_foncier_transfert_1989`, `crfm_mayotte_pension_unique`, `crfom_regime_du_decret_1950`, `csg_des_pensions_selon_le_revenu`, `cultes_retraite_complementaire_taux_specifiques`, `cumul_emploi_retraite_complementaire_des_independants`, `cumul_emploi_retraite_complementaires_des_liberaux`, `cumul_emploi_retraite_et_retraite_progressive`, `cumul_emploi_retraite_fonction_publique`, `cumul_emploi_retraite_ircantec`, `cumul_emploi_retraite_rco_agricole`, `droits_apres_la_premiere_pension`, `elus_nouvelle_caledonie_cafat`, `exoneration_independants_outre_mer`, `financement_chomage_complementaire`, `igrante_points`, `interpenetration_fonction_publique`, `ipacte_points`, `ircantec_valeurs_point`, `limite_age_banque_de_france`, `limite_age_contractuels`, `limite_age_fonction_publique`, `limite_age_ieg`, `limite_age_militaires`, `limite_age_mines`, `limite_age_opera`, `limite_age_ouvriers_etat`, `limite_age_seita`, `limite_age_sncf_ratp`, `liquidation_regime_par_regime`, `liquidation_unique_regimes_alignes`, `maintien_affiliation_crpcen_ieg`, `maintien_en_fonctions_jusqu_a_70_ans`, `maintiens_en_fonctions_de_certains_corps`, `majoration_exceptionnelle_2023`, `majorations_forfaitaires_1972_1982`, `micro_social_abattement`, `organic_conjoints_de_commercants`, `parlement_europeen_affiliation`, `pension_d_invalidite_substituee`, `plafond_limite_age_fonction_publique`, `points_agricoles_au_revenu_cadastral`, `points_au_prorata_des_cotisations`, `points_invalidite_independants`, `prolongation_activite_carriere_incomplete`, `prolongation_activite_categorie_active`, `rafp_age_d_ouverture`, `rafp_beneficiaires`, `rafp_compte_epargne_temps`, `rafp_cotisation_volontaire_outre_mer`, `rafp_gipa_hors_plafond`, `ravgdt_allocation_viagere`, `rci_seuil_premiere_tranche`, `rco_points_gratuits_66`, `recul_limite_age_enfants`, `regies_ferroviaires_pensions_en_extinction`, `relevement_des_exploitants_2023`, `residence_et_minimum_vieillesse`, `retablissement_fonction_publique`, `retraite_progressive`, `retraite_proportionnelle_msa`, `services_passes_outre_mer`, `totalisation_des_periodes_etrangeres`, `un_statut_par_annee`. Les 34 autres ne disent pas encore leur étape, et une couche ne les atteint que par leur nom : la plupart sont des règles de la liquidation, que le compte notionnel remplace, et leur étape les rangera.
- **Faire mûrir la carte** : 382 champs obligatoires manquent, à 70 fiches. Par champ :

  | Champ | Fiches à qui il manque |
  |---|---|
  | `versions` | 68 |
  | `domaine` | 65 |
  | `ecrit` | 64 |
  | `lit` | 64 |
  | `dates_qui_decident` | 63 |
  | `etape` | 41 |
  | `approximations` | 15 |
  | `code` | 1 |
  | `regimes` | 1 |

- **Les textes** : 627 rédactions à rattacher à une version de la fiche qui les cite, 6 005 à examiner, et 9 165 sans statut, que le cliquet tient à 9 165 au plus. Les textes qui en ont le plus : `css` 4 717, `decret_46_2769` 938, `rural` 834, `cpcmr` 561, `decret_90_1215` 319 (`python scripts/textes.py`).
- **La loi modifiée** (note de décision 0009, sixième cliquet) : aucune rédaction inscrite depuis la pose n'attend la réponse d'une fiche ; et, d'avant la pose, 0 dont la fiche ne dit rien et 429 qu'elle cite sans y répondre, que le cliquet tient à 0 et 429 au plus (`python scripts/textes.py --sans-reponse`).
- **Les relectures prévues les plus proches** : 2026-11-30 (`majoration_dix_pour_cent`) ; 2026-12-31 (`age_legal_par_generation`) ; 2026-12-31 (`agirc_arrco_valeur_achat`) ; 2026-12-31 (`carriere_longue`) ; 2026-12-31 (`certification_legi_perimee`).
- **Les régimes hors champ** : 22, chacun avec sa raison dans l'inventaire.

## 4. Ce que ce tableau ne sait pas encore dire

- **L'effet chiffré de chaque limite.** Les fiches le disent en mots. Le pilote le mesurera, en neutralisant la règle sur les cas types pondérés.
- **La part des pensions qui ne passent que par des règles conformes.** Il faut pour cela que chaque ligne du relevé cite sa fiche, ce que l'architecture prévoit aux phases 4 et 5.
- **Ce que personne n'a encore noté, hors des articles.** Pour les articles, le dénominateur est la loi (section 1). Les situations des fiches service-public et des circulaires, les accords Agirc-Arrco et les statuts des caisses n'ont pas encore de liste.
- **Les règles du code qui ont leur fiche.** Une fiche dira son code. Celles que les interrupteurs des régimes désignent disent la valeur qu'elles y posent ; aucune ne nomme encore sa fonction, et le tableau compte en attendant les identifiants que le code cite.
- **Les limites propres à une simulation.** Le site les montrera avec chaque résultat, et les présomptions qu'elle emploie : la chronologie les liste, le site ne les affiche pas encore.
- **La justesse au-delà des règles.** La carte de justesse (section 1) ne calcule l'état que des règles. Les barèmes (chaque valeur lue à deux sources), les régimes de bout en bout (une carrière complète retrouvée, par époque), les cas types et les totaux (contre les statistiques) n'y ont pas encore leurs preuves ; une erreur connue que sa fiche déclare en approximation y reste « approchée », non « fausse ».
- **Le coût du travail** se relève sur l'historique git, et change à chaque commit : il s'affiche à la demande, par `python scripts/tableau_de_bord.py --cout`, avec les rouges de la suite sur `main` et la taille du dépôt — ses lignes, ses tests —, que la prose ne porte plus.
