# État du dépôt

*Le tableau de bord (`docs/architecture.md`, § 9.1). Fabriqué par `scripts/tableau_de_bord.py` depuis la carte des règles, la liste de contrôle des textes et les registres qui ne sont pas encore des vues : aucun nombre n'y est écrit à la main. Pour le corriger, on corrige la fiche ou le registre, puis on relance le script ; un test refuse une copie périmée.*

## 1. Où en est-on

**Les régimes.** L'inventaire en compte 114 : 36 modélisés, 44 partiels, 23 hors champ, 2 routages.

Pesés par leurs retraités de droit direct (2024, enquête EACR de la DREES, où un polypensionné compte dans chacune de ses caisses) :

| Couverture | Retraités-caisses | Part |
|---|---|---|
| régime modélisé | 35 010 992 | 88 % |
| régime partiel | 4 354 564 | 11 % |
| sections libérales, couverture mêlée | 424 386 | 1 % |

*Modélisé ne veut pas dire exact* : les 140 règles approchées de la carte touchent aussi des régimes modélisés (section 2).

**La carte des règles** (`data/reference/regles/`) : 245 fiches, dont 2 relations. La veille en est une vue (`python scripts/veille_droit.py`).

| État | Fiches |
|---|---|
| conformes | 47 |
| transcrites | 33 |
| approchées | 140 |
| pas encore modélisées | 22 |
| manquantes | 1 |
| à vérifier | 2 |

- Confrontées à au moins un exemple officiel : **58 sur 245** (198 exemples : 188 reproduits, 10 en écart connu, section 2).
- Citées dans le code par leur identifiant : **109 sur 245**. Le lien entre une règle et le code qui l'applique n'existe pas encore pour les autres.
- Désignées par les interrupteurs des périodes de régime : **48 sur 245**, par 2 442 renvois ; chacune déclare la valeur que le moteur lit (`code.interrupteurs`) et dit ce qu'il en fait.
- Mûres, sans rien qui manque à leur contrat : **119 sur 245**. Une fiche tirée d'un registre ne sait pas encore son domaine, ses régimes, son étape ni ses versions : ce qui lui manque est à faire (section 3).
- Découpées en versions : **137 sur 245**, soit 545 versions, dont 91 supposées ; le partage des versions se contrôle sur chacune.
- Réformes du calendrier : 126, dont 10 déclarées non appliquées.

**La loi, rédaction par rédaction** (`data/reference/textes/`, § 6.6) : 15 495 rédactions d'articles, de 203 textes, lues le 2026-10-18 (index LEGI du dépôt : Freemium_legi_global_20250713-140000.tar.gz, incréments appliqués jusqu'au 20261017-211053). C'est le dénominateur de l'avancement : ce que les fiches ont lu, contre ce que la loi a écrit.

| Statut | Rédactions |
|---|---|
| rattachées à une version | 1 280 |
| sans effet | 55 |
| à rattacher | 480 |
| à examiner | 4 001 |
| sans statut | 9 679 |

**La personne** (§ 5) : une chronologie de faits datés, dans un réseau de personnes — aujourd'hui l'assuré, ses enfants et son conjoint —, que le relevé et le parcours déclarent (`src/retraite_notionnelle/chronologie.py`, et son jumeau). La carrière que le moteur liquide en est la vue. Ce que la saisie ne dit pas est présumé : 26 présomptions au vocabulaire, dont 3 posent leur fait dans la chronologie ; les autres s'appliquent dans le code, jusqu'à l'étape qui posera le leur.

| Présomption | Valeur | Fiches qui la lisent | Où elle s'applique |
|---|---|---|---|
| `jour_de_naissance` | 15 du mois | `date_effet_mois_suivant` | posée par la chronologie |
| `naissance_des_enfants` | 30 ans | `depart_anticipe_parents_trois_enfants`, `enfants_crpcen`, `enfants_fonction_publique`, `enfants_ieg`, `enfants_ratp`, `enfants_sncf`, `majoration_duree_assurance_enfants`, `priorite_majorations_enfants`, `reversion_ircantec` | posée par la chronologie |
| `radiation_au_1er_janvier_suivant` | le 1er janvier qui suit la dernière année de services, ou le départ s'il part en fonctions | `enfants_fonction_publique`, `pension_differee_fonction_publique`, `priorite_majorations_enfants`, `retablissement_fonction_publique` | droit_a_pension (droit/coordonner.py), et la revalorisation de la pension différée (droit/liquider.py) ; leurs jumeaux JavaScript ; son fait entrera à l'étape `coordonner_les_affiliations` |
| `agent_en_activite` | en activité, avec services effectifs | `services_et_duree_fonction_publique` | _ligne_annuelle, qui fait de toute année d'emploi une année de services (carriere.py, carriere.js) ; son fait entrera à l'étape `compter_les_durees` |
| `pas_d_accord_des_parents` | aucun accord ; le défaut légal les donne à la mère | `majoration_duree_assurance_enfants` | le paramètre beneficiaire des versions de la fiche majoration_duree_assurance_enfants, lu par MajorationsPourEnfants.par_enfant ; son fait entrera à l'étape `compter_les_durees` |
| `enfant_eleve_neuf_ans` | élevé neuf ans | `majoration_duree_assurance_enfants` | les versions mda_1972 et mda_1975 de la fiche majoration_duree_assurance_enfants, qui écartent l'enfant de moins de neuf ans et présument les autres élevés par leur mère ; son fait entrera à l'étape `compter_les_durees` |
| `interruption_d_activite_par_la_mere` | remplie par la mère seule | `depart_anticipe_parents_trois_enfants`, `enfants_crpcen`, `enfants_fonction_publique`, `enfants_ieg`, `enfants_ratp` | le paramètre beneficiaire (mere) des versions de la fiche enfants_fonction_publique, lu par MajorationsPourEnfants.par_enfant, et de la fiche depart_anticipe_parents_trois_enfants, lu par depart_parent_trois_enfants (droit/ouvrir.py, ouvrir.js) ; son fait entrera à l'étape `compter_les_durees` |
| `demande_de_pension_avant_2011` | demandée avant le 1er janvier 2011 | `depart_anticipe_parents_trois_enfants` | le paramètre ancien_calcul_jusqu_a de la version loi_du_9_novembre_2010 de la fiche depart_anticipe_parents_trois_enfants, lu par depart_parent_trois_enfants (droit/ouvrir.py, ouvrir.js) ; son fait entrera à l'étape `ouvrir_le_droit` |
| `mariage_des_conjoints` | 27 ans | `reversion`, `reversion_crpcen`, `reversion_fonction_publique`, `reversion_ieg`, `reversion_ircantec`, `reversion_sncf` | posée par la chronologie |
| `ressources_du_survivant` | 0 euros par an | `reversion`, `reversion_rci` | reversion (droit/reversion.py), qui ne compte au plafond du régime général, et à celui de la complémentaire des indépendants, que les réversions des autres régimes de base ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `survivant_seul` | seul | `reversion`, `reversion_rci`, `reversion_sncf` | reversion (droit/reversion.py), qui compare ses seules ressources au plafond d'une personne seule, au régime général et à la complémentaire des indépendants ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `retraites_du_survivant_servies` | dès la date d'effet | `majoration_forfaitaire_reversion`, `reversion` | reversion (droit/reversion.py), qui y applique la limite de cumul d'avant juillet 2004, compte ces retraites aux ressources depuis, et refuse la majoration pour enfant à charge ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `ressources_du_conjoint` | 0 euros par an | `minimum_vieillesse` | foyer_et_net (droit/foyer.py), qui compte au plafond de l'allocation de solidarité aux personnes âgées du couple les ressources que la saisie prête au conjoint, et aucune sinon ; son jumeau JavaScript ; son fait entrera à l'étape `foyer_et_net` |
| `domicile_fiscal_au_pays_de_residence` | le pays de résidence que la saisie dit | `cotisation_maladie_des_non_residents` | le net (contexte.py, Montants.du_foyer, et son jumeau JavaScript), qui ne prélève alors ni CSG, ni CRDS, ni CASA (L. 136-1) ; son fait entrera à l'étape `foyer_et_net` |
| `aucun_autre_revenu_que_ses_pensions` | la pension du système 1, et les ressources du conjoint déclaré, abattues de 10 % | `csg_des_pensions_selon_le_revenu` | le net (contexte.py, Montants.du_foyer, et son jumeau JavaScript), quand la saisie ne dit pas le revenu fiscal ; son fait entrera à l'étape `foyer_et_net` |
| `conjoint_de_l_autre_sexe` | l'autre sexe | `reversion_agirc_arrco`, `reversion_crpcen`, `reversion_fonction_publique`, `reversion_ieg`, `reversion_ircantec` | la saisie, qui donne au conjoint l'autre sexe quand elle ne le dit pas (saisie.py, saisie.js) ; son fait entrera à l'étape `preparer_la_chronologie` |
| `reversion_demandee_dans_l_annee` | dans l'année | `majoration_forfaitaire_reversion`, `reversion`, `reversion_agirc_arrco`, `reversion_ircantec`, `reversion_rafp`, `reversion_rci` | la date d'effet de la réversion (droit/reversion.py), au premier jour du mois qui suit le décès, ou qui suit l'âge requis ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `deces_apres_le_depart` | au départ | `reversion`, `reversion_agirc_arrco`, `reversion_crpcen`, `reversion_fonction_publique`, `reversion_ieg`, `reversion_ircantec`, `reversion_rafp`, `reversion_rci`, `reversion_sncf` | l'échéancier (echeancier.py), qui liquide alors une réversion d'essai, hors du journal ; son jumeau JavaScript ; son fait entrera à l'étape `echeancier` |
| `validation_ircantec_demandee` | demandée | `retablissement_fonction_publique` | retablir (droit/coordonner.py), et l'assiette de l'Ircantec des années rétablies (droit/acquerir.py) ; leurs jumeaux JavaScript ; son fait entrera à l'étape `coordonner_les_affiliations` |
| `depart_de_chaque_regime` | au départ déclaré, à l'ouverture du régime, ou à la sortie de l'armée | `liquidation_regime_par_regime` | departs (droit/departs.py), que l'échéancier et le scénario 1 lisent ; son jumeau JavaScript ; son fait entrera à l'étape `echeancier` |
| `exceptions_a_la_limite_d_age` | demandées et accordées autant que le départ saisi le demande | `limite_age_banque_de_france`, `limite_age_contractuels`, `limite_age_fonction_publique`, `limite_age_ieg`, `limite_age_militaires`, `limite_age_mines`, `limite_age_opera`, `limite_age_ouvriers_etat`, `limite_age_seita`, `limite_age_sncf_ratp`, `maintien_en_fonctions_jusqu_a_70_ans`, `prolongation_activite_carriere_incomplete`, `prolongation_activite_categorie_active` | radiation (droit/limite_age.py), que les départs, l'échéancier et le scénario 1 lisent ; son jumeau JavaScript ; son fait entrera à l'étape `echeancier` |
| `pension_d_invalidite_de_la_periode` | depuis le 1er janvier de la première année de la période d'invalidité finale | `pension_d_invalidite_substituee` | Carriere.pension_d_invalidite (carriere.py), et son jumeau JavaScript ; son fait entrera à l'étape `ouvrir_le_droit` |
| `opposition_a_la_substitution` | opposée, la pension demandée au départ déclaré | `pension_d_invalidite_substituee` | substitution (droit/invalidite.py), et son jumeau JavaScript ; son fait entrera à l'étape `echeancier` |
| `pas_de_pension_etrangere` | aucune | `minimum_contributif_international` | pensions_a_l_ecretement (droit/etranger.py), que l'écrêtement du minimum contributif lit (droit/completer.py) ; leurs jumeaux JavaScript ; son fait entrera à l'étape `preparer_la_chronologie` |
| `pas_de_periode_assimilee` | aucune | `apprentissage`, `conge_supplementaire_naissance`, `sportifs_haut_niveau`, `stages_formation_professionnelle` | aucune étape encore : les fiches apprentissage, stages_formation_professionnelle, sportifs_haut_niveau et conge_supplementaire_naissance sont pas_encore_modelisee, et le moteur compte comme aujourd'hui. Une période déclarée (chronologie.avec_periodes_assimilees, et son jumeau JavaScript) ou un emploi en apprentissage (l'attribut apprentissage d'un métier) prend la place de la présomption ; son fait entrera à l'étape `compter_les_durees` |
| `residence_en_france` | en France | `residence_et_minimum_vieillesse` | foyer_et_net (droit/foyer.py), qui ne sert l'allocation de solidarité aux personnes âgées qu'à qui réside en France ; son jumeau JavaScript ; son fait entrera à l'étape `preparer_la_chronologie` |

**Le relevé des droits** (§ 7.2 et 7.6) : pour chaque demande, quatre étapes le construisent, une par module dans `src/retraite_notionnelle/droit/` et son jumeau `moteur/js/droit/`, chacune écrivant la donnée que son schéma décrit (`data/reference/etapes/`) ; la liquidation du scénario 1 ne lit que lui. Les relevés des 13 cas types, à chacune de leurs générations — 91 relevés —, comptent 23 126 lignes, dont 782 citent la fiche qui les écrit (3 %) et 14 sa version.

| Étape | Module | Ce qu'elle écrit | Fiches qui disent l'appliquer |
|---|---|---|---|
| `preparer_la_chronologie` | `droit/preparer.py` | la chronologie, présomptions posées (contrat C.1) | `conjoint_collaborateur_independants`, `limite_age_banque_de_france`, `limite_age_contractuels`, `limite_age_fonction_publique`, `limite_age_ieg`, `limite_age_militaires`, `limite_age_mines`, `limite_age_opera`, `limite_age_ouvriers_etat`, `limite_age_seita`, `limite_age_sncf_ratp`, `maintien_en_fonctions_jusqu_a_70_ans`, `maintiens_en_fonctions_de_certains_corps`, `plafond_limite_age_fonction_publique`, `prolongation_activite_carriere_incomplete`, `prolongation_activite_categorie_active`, `recul_limite_age_enfants` |
| `coordonner_les_affiliations` | `droit/coordonner.py` | les régimes qui reçoivent chaque ligne, les rétablissements, les groupes | `cci_paris_transfert_2006`, `cci_roubaix_transfert_1998`, `compagnie_generale_eaux_transfert_1991`, `credit_foncier_transfert_1989`, `crfm_mayotte_pension_unique`, `crfom_regime_du_decret_1950`, `elus_nouvelle_caledonie_cafat`, `interpenetration_fonction_publique`, `liquidation_unique_regimes_alignes`, `parlement_europeen_affiliation`, `regies_ferroviaires_pensions_en_extinction`, `retablissement_fonction_publique`, `totalisation_des_periodes_etrangeres` |
| `compter_les_durees` | `droit/compter.py` | les trimestres de chaque compte, par régime et par année ; ceux des enfants | `apprentissage`, `bonification_cinquieme_militaires`, `bonification_cinquieme_police_penitentiaire`, `bonification_cinquieme_sapeurs_pompiers`, `conge_supplementaire_naissance`, `enfants_crpcen`, `enfants_fonction_publique`, `enfants_ieg`, `enfants_ratp`, `enfants_sncf`, `fin_indemnisation_chomage`, `majoration_duree_assurance_enfants`, `majoration_duree_hospitaliers_actifs`, `priorite_majorations_enfants`, `services_et_duree_fonction_publique`, `sportifs_haut_niveau`, `stages_formation_professionnelle` |
| `acquerir_les_droits` | `droit/acquerir.py` | les points et les cotisations, la durée plafonnée, les points gratuits | `agirc_arrco_valeur_achat`, `assiette_minimale_agricole`, `assiette_minimale_independants`, `asv_autres_professions_de_sante`, `asv_medecins_ajustement`, `asv_medecins_points`, `chomage_retraite_complementaire`, `cotisation_par_classes_liberales`, `cultes_retraite_complementaire_taux_specifiques`, `droits_apres_la_premiere_pension`, `financement_chomage_complementaire`, `garantie_minimale_points_agirc`, `igrante_points`, `ipacte_points`, `ircantec_valeurs_point`, `micro_social_abattement`, `organic_conjoints_de_commercants`, `points_au_prorata_des_cotisations`, `points_invalidite_independants`, `rafp_compte_epargne_temps`, `rafp_cotisation_volontaire_outre_mer`, `rafp_gipa_hors_plafond`, `ravgdt_allocation_viagere`, `rci_seuil_premiere_tranche`, `rco_points_gratuits`, `rco_points_gratuits_66`, `retraite_proportionnelle_msa`, `services_passes_outre_mer` |

**La liquidation** (§ 7.3, 7.4 et 7.7) : `liquider(demande, état, contexte)`, une fonction pure (`src/retraite_notionnelle/droit/liquidation.py`, et son jumeau), enchaîne l'acquisition et trois étapes, et mesure par des liquidations d'essai ce qu'apporte chaque avantage. L'échéancier (`echeancier.py`) l'appelle au départ, applique à l'échéance les deux étapes qui ne liquident rien, et inscrit tout à son journal (`journal.py`) ; le pilote (`pilote.py`) date les départs des cas types sans rien liquider. Les 883 témoins font chacun de 1 à 12 appels de `liquider`, liquidations d'essai comprises, et au plus 6 par départ ; aucun ne dépasse les 6 par départ que le nombre déclaré accorde (§ 7.8).

| Étape | Module | Ce qu'elle écrit | Fiches qui disent l'appliquer |
|---|---|---|---|
| `ouvrir_le_droit` | `droit/ouvrir.py` | l'âge d'ouverture et son motif, la durée requise, les trimestres cotisés | `age_legal_par_generation`, `carriere_longue`, `depart_anticipe_parents_trois_enfants`, `duree_requise_par_generation`, `inaptitude_au_travail`, `ortf_position_speciale_1974`, `retraite_anticipee_handicap` |
| `liquider_chaque_regime` | `droit/liquider.py` | la pension de chaque régime et sa formule, les régimes qui portent les minima | `agirc_arrco_valeur_service`, `atc_icna_allocation`, `cafat_pension_de_base`, `cese_pension_des_membres`, `clr_nouvelle_caledonie_pension_des_fonctionnaires`, `coefficients_anticipation_agirc_1947`, `coefficients_anticipation_agirc_arrco`, `cps_polynesie_pension_des_salaries`, `crpn_pension_des_navigants`, `cultes_alsace_moselle_pension`, `cultes_fractions_de_pension`, `decompte_des_services_fonction_publique`, `decote_avant_1983`, `decote_opera_de_paris`, `decote_regime_general`, `decote_regimes_speciaux`, `deputes_pension_des_anciens_deputes`, `entrepreneurs_du_batiment_complementaire`, `indemnite_de_feu_sapeurs_pompiers`, `indemnite_sujetions_speciales_police`, `majoration_duree_apres_65_ans`, `majoration_forfaitaire_reversion`, `mayotte_pension_de_base`, `minoration_racl_2014_2024`, `pension_maximale_regime_general`, `pension_non_salaries_agricoles_2026`, `pension_proratisee`, `points_avant_1973_independants`, `prime_speciale_sujetion_aides_soignants`, `rafp_garantie_outre_mer`, `retraite_pour_invalidite_fonction_publique`, `retrep_avantages_temporaires`, `revenu_annuel_moyen_independants`, `reversion`, `reversion_agirc_arrco`, `reversion_crpcen`, `reversion_fonction_publique`, `reversion_ieg`, `reversion_ircantec`, `reversion_rafp`, `reversion_rci`, `reversion_sncf`, `saint_pierre_et_miquelon_pension_de_base`, `salaire_annuel_moyen`, `seconde_pension`, `surcote_ircantec`, `surcote_par_age_seul`, `surcote_regime_general`, `surcote_regimes_speciaux`, `taux_plein_anciens_combattants_prisonniers`, `taux_plein_anciens_deportes_internes`, `taux_plein_et_proratisation`, `taux_plein_meres_de_famille_ouvrieres`, `taux_plein_travailleurs_manuels`, `wallis_et_futuna_pension_des_salaries` |
| `completer_tous_regimes` | `droit/completer.py` | les minima, la surcote parentale, la majoration pour enfants | `complement_differentiel_rco`, `ircantec_majoration_enfants`, `majoration_conjoint_a_charge`, `majoration_dix_pour_cent`, `majoration_enfants_a_charge_agirc_arrco`, `majoration_enfants_plafond_fonction_publique`, `majoration_retraite_proportionnelle`, `minimum_contributif`, `minimum_contributif_international`, `minimum_garanti`, `minimum_pension_ieg`, `pension_majoree_reference`, `surcote_parentale`, `versement_forfaitaire_unique`, `versement_unique_agirc_arrco`, `versement_unique_ircantec` |
| `faire_vivre` | `revalorisation.py` | le coefficient de chaque pension, du départ à l'échéance | `majoration_exceptionnelle_2023`, `majorations_forfaitaires_1972_1982`, `relevement_des_exploitants_2023`, `revalorisation_des_pensions` |
| `foyer_et_net` | `droit/foyer.py` | l'ASPA, au départ puis à chaque échéance | `assiette_sociale_independants`, `cotisation_maladie_des_non_residents`, `cotisation_maladie_pensions_complementaires`, `cotisation_vieillesse_independants`, `csg_des_pensions_selon_le_revenu`, `minimum_vieillesse`, `residence_et_minimum_vieillesse` |

**La proposition, en univers de droit** (§ 4.8 et 8) : chaque scénario est une pile de couches posée sur le droit réel, que l'univers déclare (`data/reference/univers/`, `data/reference/couches/`) ; le simulateur en tire ses scénarios, et le paquet du site les porte résolus. 9 fiches de la proposition (`data/reference/regles/proposition/`) décrivent ce que les couches ajoutent, en citant son texte. Les fiches du droit réel qu'aucune couche d'un univers ne garde, ne remplace ni ne neutralise sont ses domaines sans décision (section 3).

| Scénario | Univers | Couches posées sur le droit réel | Fiches ajoutées | Fiches du droit réel sans décision |
|---|---|---|---|---|
| 1 | `actuel` | aucune : c'est l'étalon | 0 | — |
| 2 | `notionnel_retroactif` | `comptes_notionnels` | 5 | 130 sur 245 |
| 3 | `notionnel_prospectif` | `contributif_seul`, `valorisation_des_droits_acquis`, `comptes_notionnels` | 6 | 130 sur 245 |
| 4 | `notionnel_retroactif_employeur` | `comptes_notionnels`, `part_patronale` | 5 | 130 sur 245 |
| 5 | `notionnel_prospectif_employeur` | `contributif_seul`, `valorisation_des_droits_acquis`, `comptes_notionnels`, `part_patronale` | 6 | 130 sur 245 |
| 6 | `notionnel_liberal` | `comptes_notionnels`, `part_patronale`, `taux_unique`, `capitalisation_obligatoire`, `garantie_vieillesse`, `age_legal_de_la_proposition` | 8 | 130 sur 245 |

**La réorganisation** (§ 6.5, § 11). Les registres devenus des vues de la carte : la veille. Restent des registres : la frontière contributive, l'inventaire des régimes.

**Ce qui est hors de la page Coût.** La réversion, par exemple, pèse 10,4 % de la masse des prestations en 2024 (COR) : le modèle en calcule une pour une personne (scénario 1), mais la page Coût n'en connaît que cette part publiée, qu'elle ne calcule pas.

**La feuille de route** compte 164 actions : 135 fait, 18 en cours, 7 à faire, 2 archivée, 2 abandonnée. Les closes sont dans son archive, `docs/archives/feuille_de_route.md` ; ce qui reste à faire est ailleurs, dispersé.

## 2. Ce qui ne va pas encore

**Les régimes partiels, du plus peuplé au moins peuplé**

| Régime | Retraités | Ce qui manque |
|---|---|---|
| Pensions civiles et militaires de retraite (Service des retraites de l'État) | 2 018 190 | Les bonifications de SERVICE — dépaysement, campagne, services aériens — ne sont pas servies, faute de connaître le corps et le détail des services |
| Assurance vieillesse des non-salariés agricoles (MSA) | 1 023 064 | Le barème en points d'avant 1990 n'est pas lu, et ses années entrent dans la moyenne de la réforme de 2026 par les points que vaut leur rendement |
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
| `cultes_retraite_complementaire_taux_specifiques` | a_verifier | Le ministre dont la collectivité applique un taux spécifique cotise de 11 à 113 % de plus qu'au taux de base, et le modèle ne lui compte qu… |
| `fin_de_la_suspension_2028` | a_verifier | Tout changement de calendrier touche les générations 1965 et suivantes. |
| `abattement_rci` | approchee | Toute retraite du RCI liquidée avant le taux plein du régime de base. |
| `agirc_arrco_valeur_achat` | approchee | Toute carrière qui cotise à l'Agirc-Arrco après 2026 : ses points de ces années coûtent le salaire moyen et non les prix, environ 0,7 % de… |
| `agirc_arrco_valeur_service` | approchee | Tout départ antérieur au relèvement de son année : la complémentaire baisse de 4,87 % pour un départ de janvier à octobre 2022, de 4,67 % a… |
| `apprentissage` | approchee | Les apprentis depuis 2014 : 878 871 contrats commencés en 2024 (DARES). |
| `assiette_minimale_agricole` | approchee | Les chefs d'exploitation aux revenus faibles, et, à la complémentaire, tous les chefs qui cotisent depuis 2017. |
| `assiette_minimale_independants` | approchee | Un indépendant à 3 000 € validait un trimestre au lieu de trois et n'avait ni le salaire ni les points du minimum. |
| `assiette_sociale_independants` | approchee | Les indépendants non agricoles, pour leurs revenus depuis 2025 : rien sur leurs droits, que la caisse calcule sur l'assiette que la carrièr… |
| `asv_autres_professions_de_sante` | approchee | Un infirmier né en 1960, au salaire moyen de 25 à 65 ans : ses PCV valent 1 642 € par an, un dixième de sa pension, qui les ignorait |
| `asv_medecins_ajustement` | approchee | La fiche servait 36 points à tout médecin, soit jusqu'à 7,75 points de trop sous 70 000 €. |
| `asv_medecins_points` | approchee | Les médecins libéraux conventionnés : près du tiers de la pension d'un médecin de secteur 1 |
| `baremes_cnbf` | approchee | Tout avocat. |
| `bonification_cinquieme_militaires` | approchee | Le militaire qui réunit dix-sept ans de services, quinze avant juillet 2011 : vingt trimestres à qui en a servi vingt-cinq, soit un cinquiè… |
| `bonification_cinquieme_police_penitentiaire` | approchee | Le policier ou le surveillant qui réunit la durée de l'âge minoré : vingt trimestres de services à qui en a servi vingt-cinq, soit jusqu'à… |
| `bonification_cinquieme_sapeurs_pompiers` | approchee | Le sapeur-pompier professionnel qui réunit ses durées : vingt trimestres à qui a servi vingt-cinq ans en cette qualité, sous le maximum de… |
| `cafat_pension_de_base` | approchee | Les salariés de Nouvelle-Calédonie : leur pension est simulée en points au bon âge de liquidation, mais à un rendement trop haut depuis 202… |
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
| `clr_nouvelle_caledonie_pension_des_fonctionnaires` | approchee | Les fonctionnaires de Nouvelle-Calédonie : leur pension est simulée au bon âge et au bon taux par annuité, mais sans minoration ni réductio… |
| `cnavpl_majoration_duree_assurance` | approchee | La fiche les disait non portés, et le moteur ne cherchait la majoration de durée que dans les régimes en annuités : une libérale qui n'avai… |
| `coefficients_anticipation_agirc_1947` | approchee | Le cadre dont la pension de l'Agirc prend effet avant 1955 : 0,72 au lieu de 0,78 à soixante ans, 0,93 au lieu de 0,96 à soixante-quatre, e… |
| `coefficients_anticipation_agirc_arrco` | approchee | Toute liquidation anticipée d'une complémentaire des salariés du privé : 1 % à 22 % de moins sur vingt trimestres, jusqu'à 57 % dix ans ava… |
| `complement_differentiel_rco` | approchee | Les chefs d'exploitation de dix-sept ans et demi liquidant au taux plein depuis 2015 : le moteur servait leurs points de RCO seuls |
| `conge_supplementaire_naissance` | approchee | Les parents qui prennent le congé supplémentaire de naissance depuis le 1er juillet 2026 : un trimestre par cinquante-huit jours, que le mo… |
| `cotisation_maladie_des_non_residents` | approchee | Tout retraité qui déclare résider hors de France : plus de CSG ni de CRDS ni de CASA |
| `cotisation_maladie_pensions_complementaires` | approchee | Tout salarié ou contractuel dont la pension du système actuel comprend une complémentaire : sa pension nette baisse de 1 % de cette part, s… |
| `cotisation_par_classes_liberales` | approchee | Les vétérinaires, les experts-comptables et commissaires aux comptes, et les affiliés de la Cipav jusqu'en 2022. |
| `cps_polynesie_pension_des_salaries` | approchee | Les salariés de Polynésie française : leur pension de tranche A est simulée au bon âge et à la bonne durée, mais sur un salaire de référenc… |
| `crpn_pension_des_navigants` | approchee | Les navigants de l'aéronautique civile : leur pension de la caisse est simulée sans la majoration temporaire de cinquante-cinq ans à l'âge… |
| `csg_des_pensions_selon_le_revenu` | approchee | Tout retraité en mode net : un foyer d'une part sous 13 048 € de revenu fiscal n'est plus prélevé |
| `cultes_fractions_de_pension` | approchee | Les ministres des cultes et les membres des congrégations, au scénario 1, partis à soixante-quatre ans : + 98 % nés en 1925, + 30 % en 1945… |
| `cumul_emploi_retraite_et_retraite_progressive` | approchee | Le retraité qui travaille avant le taux plein : la salariée née en 1960, partie à 62 ans en 2022 sans la durée requise, qui reprend un empl… |
| `cumul_emploi_retraite_fonction_publique` | approchee | Le fonctionnaire retraité qui travaille avant le taux plein : payé par un employeur public, ou par tout employeur s'il est civil et parti d… |
| `decompte_des_services_fonction_publique` | approchee | Les fonctionnaires dont l'année d'entrée et celle du départ sont entamées : la fraction qu'elles laissent fait un trimestre de plus au déco… |
| `decote_avant_1983` | approchee | Les pensions du régime général et des salariés agricoles qui prennent effet avant le 1er avril 1983, et celles des artisans et commerçants… |
| `decote_crpn` | approchee | L'âge d'annulation passe de 65 à 60 ans pour toute liquidation depuis 2012, et la décote se compte sur la durée seule depuis 2022, sur 21 à… |
| `depart_anticipe_parents_trois_enfants` | approchee | La mère de trois enfants fonctionnaire qui avait quinze ans de services avant 2012 : son droit s'ouvre à la date où elle réunit les conditi… |
| `deputes_pension_des_anciens_deputes` | approchee | Les anciens députés et, par assimilation, les anciens sénateurs : leur pension est simulée au droit lu |
| `droits_apres_la_premiere_pension` | approchee | Toute personne qui travaille après sa première pension, dans le même régime ou dans un autre : le fonctionnaire de catégorie active parti à… |
| `enfants_crpcen` | approchee | Toute mère clerc ou employée de notaire : quatre trimestres au taux par enfant né avant le 1er juillet 2006 |
| `enfants_fonction_publique` | approchee | Toute mère fonctionnaire ou agente d'un régime spécial : quatre trimestres par enfant né avant 2004, en services, donc au prorata de la pen… |
| `enfants_ieg` | approchee | Toute mère agente des IEG : quatre trimestres de services par enfant né avant le 1er juillet 2008, et non avant 2004, huit pour le second d… |
| `enfants_ratp` | approchee | Toute mère agente de la RATP : quatre trimestres de services par enfant né avant le 1er juillet 2008, et non avant 2004 |
| `enfants_sncf` | approchee | Toute mère agente de la SNCF : deux trimestres de durée par enfant né après son recrutement, et plus aucun trimestre de services |
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
| `majoration_conjoint_a_charge` | approchee | Le retraité du régime général parti avant 2011, dont le conjoint sans pension a eu soixante-cinq ans avant 2011, reçoit 609,80 € par an au… |
| `majoration_duree_apres_65_ans` | approchee | Les assurés du régime général, des salariés agricoles et des artisans et commerçants qui liquident après l'âge du taux plein sans la durée… |
| `majoration_duree_assurance_enfants` | approchee | Toute mère affiliée au régime général ou à un régime aligné : la règle commande la décote, la proratisation, la surcote parentale et le sal… |
| `majoration_duree_hospitaliers_actifs` | approchee | L'aide-soignant ou l'agent hospitalier actif : quinze trimestres pour trente-sept ans et demi de services, qui effacent la décote de qui pa… |
| `majoration_enfants_a_charge_agirc_arrco` | approchee | Le salarié du privé qui part avec un enfant de moins de dix-huit ans voit sa complémentaire majorée de 5 % par enfant, au lieu de la majora… |
| `majoration_enfants_liberaux_avocats` | approchee | Les fiches de la CNAVPL, de la CNBF et de sa complémentaire ne la portaient pas : 10 % de pension en moins pour tout parent de trois enfant… |
| `majoration_enfants_plafond_fonction_publique` | approchee | Les pensions du code des pensions que la majoration pour enfants porterait au-delà du traitement : sans surcote, à partir de sept enfants a… |
| `majoration_exceptionnelle_2023` | approchee | Les retraités du régime général, des indépendants, des salariés agricoles et des cultes partis avant le 1er septembre 2023 au taux plein av… |
| `majoration_retraite_proportionnelle` | approchee | Les chefs partis avant 1997, de 1997 à 2008 : une carrière complète à faible revenu partie en 1995 reçoit 2 036 € de plus en 2008. |
| `marins_salaire_de_reference` | approchee | Le modèle prend la catégorie de la DERNIÈRE année, rangée par le revenu, et compte les services au trimestre |
| `mayotte_pension_de_base` | approchee | Les salariés de Mayotte : leur pension est simulée au droit depuis 2003, à leur salaire moyen près pour les nés avant 1965 |
| `micro_social_abattement` | approchee | Le micro-entrepreneur saisit son chiffre d'affaires mensuel et son activité (champ « micro »), que la saisie abat avant de le donner au mod… |
| `minimum_contributif` | approchee | Petites pensions au taux plein. |
| `minimum_contributif_international` | approchee | Les petites pensions françaises des carrières internationales, au taux plein par la totalisation : le minimum de la pension proratisée se r… |
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
| `points_avant_1973_independants` | approchee | Les artisans et commerçants en activité avant 1973, nés avant 1958 environ. |
| `priorite_majorations_enfants` | approchee | Toute mère passée par un régime spécial et par un régime aligné. |
| `prolongation_activite_carriere_incomplete` | approchee | Le fonctionnaire civil dont le départ saisi passe sa limite d'âge sans la durée du taux maximum est maintenu, depuis 2004, jusqu'à cette du… |
| `prolongation_activite_categorie_active` | approchee | Le fonctionnaire actif dont le départ saisi passe sa limite d'âge est maintenu, depuis 2010, jusqu'à la limite des sédentaires de sa généra… |
| `raap_classe_speciale` | approchee | La fiche prélevait 8 % du revenu avant 2016 — un taux qu'aucun texte ne porte — et servait donc, à un revenu moyen, quatre à six fois les p… |
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
| `reversion_crpcen` | approchee | Tout conjoint d'un clerc ou employé de notaire : la moitié de sa pension, sans âge ni ressources, dès que le mariage remplit la condition d… |
| `reversion_fonction_publique` | approchee | Tout conjoint, ou ex-conjoint, d'un fonctionnaire de l'État ou d'un agent des collectivités qui décède. |
| `reversion_ieg` | approchee | Tout conjoint d'un agent des IEG : la moitié de sa pension, majoration pour enfants comprise, sans âge ni ressources, partagée avec les ex-… |
| `reversion_ircantec` | approchee | Tout conjoint, ou ex-conjoint, d'un agent contractuel de l'État, des collectivités ou des hôpitaux, ou d'un élu local, qui décède. |
| `reversion_rafp` | approchee | Tout conjoint, ou ex-conjoint, d'un fonctionnaire de l'État ou d'un agent des collectivités et des hôpitaux qui décède. |
| `reversion_rci` | approchee | Tout conjoint, ou ex-conjoint, d'un artisan, d'un commerçant ou d'un industriel qui décède depuis 2013. |
| `reversion_sncf` | approchee | Tout conjoint d'un agent de la SNCF : la moitié de sa pension, majorée pour enfants, sans âge ni ressources, dès que le mariage remplit la… |
| `saint_pierre_et_miquelon_pension_de_base` | approchee | Les assurés de Saint-Pierre-et-Miquelon : leur pension est simulée au droit pour l'âge et la durée, mais sur un revenu moyen de trop peu d'… |
| `salaire_annuel_moyen` | approchee | Toute pension en annuités du régime général et des salariés agricoles. |
| `seconde_pension` | approchee | Les retraités en cumul intégral depuis 2023 : leurs cotisations, jusque-là à fonds perdus, leur ouvrent une seconde pension, au plus 5 % du… |
| `sections_liberales_majoration_enfants` | approchee | Aucune des trois fiches ne la portait : 10 % de complémentaire en moins pour tout parent de trois enfants. |
| `services_passes_outre_mer` | approchee | Les salariés de Nouvelle-Calédonie, et d'un an ceux de Saint-Pierre-et-Miquelon. |
| `sportifs_haut_niveau` | approchee | Les sportifs inscrits sur la liste de haut niveau depuis 2012, à faibles ressources : jusqu'à quatre trimestres par an, trente-deux en tout… |
| `stages_formation_professionnelle` | approchee | Les stagiaires de la formation professionnelle depuis 2015, et les anciens des TUC et des stages d'insertion des années 1977 à 1992 partis… |
| `surcote_par_age_seul` | approchee | Les complémentaires de la CARMF, de la CARPIMKO, de la CAVEC, de la CAVP, de la Cipav et de la CPRN, et l'ASV des médecins, dont les périod… |
| `taux_plein_anciens_combattants_prisonniers` | approchee | L'ancien prisonnier ou combattant qui n'a pas la durée requise reçoit le taux plein avant l'âge du taux plein, d'autant plus tôt que sa cap… |
| `taux_plein_anciens_deportes_internes` | approchee | L'ancien déporté ou interné qui n'a pas la durée requise reçoit le taux plein, sans décote, au régime général, chez les salariés agricoles,… |
| `taux_plein_meres_de_famille_ouvrieres` | approchee | La mère de trois enfants qui a trente ans d'assurance, majoration comprise, et a été ouvrière cinq des quinze dernières années, a le taux p… |
| `taux_plein_travailleurs_manuels` | approchee | Le travailleur manuel parti de 1976 à 1983, entre soixante et soixante-cinq ans, avec quarante et un à quarante-trois ans d'assurance, assu… |
| `temps_partiel_fonction_publique` | approchee | Tout fonctionnaire qui a travaillé à temps partiel. |
| `totalisation_des_periodes_etrangeres` | approchee | Toute personne qui a travaillé hors de France : 1,28 million de retraités résidaient à l'étranger fin 2024 (DREES, enquête annuelle auprès… |
| `trimestres_avant_1972` | approchee | Les années travaillées de 1946 à 1971 dont le salaire n'atteint pas quatre fois le seuil : 9 à 14 % du salaire moyen pour quatre trimestres… |
| `un_statut_par_annee` | approchee | DEPUIS LE 22 SEPTEMBRE 2026, DEUX ACTIVITÉS À LA FOIS se décrivent, dans les deux moteurs : chacune verse à son régime, sur son revenu, et… |
| `versement_forfaitaire_unique` | approchee | L'assuré du régime général dont la pension annuelle, majoration pour enfants comprise, passe sous le seuil — 26,68 € en 1974, 156,24 € en 2… |
| `versement_unique_agirc_arrco` | approchee | Le salarié dont l'allocation de l'Agirc-Arrco n'excède pas cent points — 143,86 € par an en 2026 — reçoit sa valeur viagère en une fois : 3… |
| `versement_unique_ircantec` | approchee | Le contractuel de la fonction publique qui a moins de 300 points de l'Ircantec reçoit ses points au salaire de référence de l'année précéde… |
| `wallis_et_futuna_pension_des_salaries` | approchee | Les salariés de Wallis-et-Futuna : leur pension est simulée à 60 ans au barème jusqu'à trente ans, mais leur cotisation au taux total de la… |

**Un état peut-être périmé.** Pour 20 des 140 règles approchées, l'effet raconte à l'imparfait l'erreur qui a été corrigée, sans dire ce qui reste. Le tableau ne peut pas savoir si elles sont encore approchées : leur fiche le dira quand elle mûrira, l'écart actuel dans ses approximations, le récit dans son historique.

**Des approximations non déclarées.** 40 des 140 fiches approchées ne déclarent encore ses approximations, chacune avec son effet ou « non mesuré » : l'effet n'en est dit qu'en mots.

**Les exemples officiels que le modèle ne reproduit pas**, entrés en écart connu, avec la règle qui le déclare :

| Exemple | Grandeur | Publié | Modèle | Règle |
|---|---|---|---|---|
| `cnav_22_83_taux_acquis_117_trimestres` | taux_liquidation | 0,55 | 0,5 | `decote_avant_1983` |
| `cnav_22_83_taux_acquis_117_trimestres` | pension_base_sur_sam | 0,429 | 0,44 | `decote_avant_1983` |
| `ircantec_minoration_age_avant_l_age_legal` | coefficients_des_regimes | ircantec 0,7625 | ircantec 0,9 | `liquidation_regime_par_regime` |
| `aa_reversion_francois` | dates_d_effet_de_la_reversion | arrco 2025-01-01 | arrco 2024-12-01 | `reversion_agirc_arrco` |
| `aa_reversion_david` | dates_d_effet_de_la_reversion | arrco 2024-10-01 | arrco 2024-08-01 | `reversion_agirc_arrco` |
| `aa_reversion_simone` | dates_d_effet_de_la_reversion | arrco 2025-01-01 | arrco 2024-03-01 | `reversion_agirc_arrco` |
| `ur_reversion_etat_mariage_3_ans_et_demi` | reversions_mensuelles | fonction_publique_etat 0, rafp 0 | fonction_publique_etat 0, rafp 50 | `reversion_rafp` |
| `ur_reversion_prive_ressources_plafond_2024` | reversions_mensuelles | regime_general 0, agirc_arrco 420 | regime_general 33,47, agirc_arrco 420 | `reversion` |
| `erafp_1958_effet_2026_11_8000_points` | prestation_rafp | forme rente, age_legal 64, coefficient 1,3, rente_mensuelle 49,15 | forme rente, age_legal 62, coefficient 1,29667, rente_mensuelle 49,02 | `rafp_majoration_capital` |
| `erafp_1963_effet_2026_11_5000_points` | prestation_rafp | forme capital_fractionne, age_legal 62,75, coefficient 1,05, premiere_fraction 99,24 | forme capital_fractionne, age_legal 62,75, coefficient 1,05333, premiere_fraction 99,56 | `rafp_majoration_capital` |
| `erafp_ra2012_jean_capital_62_ans` | prestation_rafp | forme capital, coefficient 1,08, conversion 24,62, capital 4030,38 | forme capital, coefficient 1,08, conversion 24,62, capital 4030,88 | `rafp_majoration_capital` |

## 3. Ce qui reste à faire, et par quoi commencer

- **Les 18 actions en cours** de la feuille de route :
  - 47. La garantie vieillesse est une avance : la reprise sur succession, sa règle et son chiffrage
  - 89. Dépouiller les 260 sources officielles remises le 22 septembre 2026
  - 129. Le taux de l'État ramené à sa part « retraite seule » : un réglage, puis le défaut
  - 130. L'architecture du dépôt : décidée, les phases 0 à 8 faites, les domaines à ouvrir
  - 131. Les dix fiches nées à la phase 6, relues à la source : les écarts qu'elles montrent, à corriger
  - 133. La retraite de base et ses complémentaires, sous le montant du système 1
  - 135. Aller plus vite sans rien céder : l'outillage d'un changement de résultats
  - 137. Les autres modèles publics : le registre exhaustif, puis leur confrontation
  - 138. Meilleur en tous points : ce que les autres modèles font mieux, vérifié, puis repris
  - 145. Les régimes que l'inventaire ne nommait pas : documentés, non calculés
  - 151. Partir très tard : le départ jusqu'au bout des tables de mortalité, puis la limite d'âge des fonctionnaires et ses exceptions
  - 152. Les cas types statutaires et non salariés à leur place dans l'EIR : le niveau et la carrière de chacun
  - 153. L'oracle au-delà des carrières simples : ce qu'OpenFisca calcule et que le dépôt ne lui confronte pas
  - 158. Les grilles indiciaires de la fonction publique : la carrière d'un fonctionnaire pré-remplie depuis son corps, plutôt que de mémoire
  - 159. Le jaune pensions du PLF 2027, exploité en entier : rangé, puis chaque tableau à sa place dans le dépôt
  - 161. Un seul exemplaire du code : les doublons entre le Python et le JavaScript retirés une paire à la fois, chaque retrait relu
  - 162. Le test d'abord : le développement piloté par les tests, sur tout le dépôt
  - 163. Ce que la revue de code d'Anthropic apprend au dépôt : le site en ligne au vert, les rouges classés, puis un relecteur
- **Les sources à exploiter** : 34 à explorer sur 324 (121 explorées, 169 épuisées). 0 d'entre elles visent un régime partiel, et pourraient le compléter :
  - et 30 sources sans régime désigné.
- **Les autres modèles** (§ 3.4) : 70 au registre (`data/reference/referents.yaml`) : 32 au code ouvert, 1 sur demande, 13 documenté(s) sans leur code, 24 non public(s). 15 ont déjà été confrontés au dépôt ou lui donnent des valeurs (Barèmes IPP, OpenFisca-France, OpenFisca-France-Pension, Destinie 2, Ines, TRAJECTOiRE, ANCETRE, legiretraite (paquet R), Maquette globale de projection du COR, Maquette simplifiée du secrétariat général du COR, PRISME (Projection des Retraites, Simulations, Modélisation et Évaluations), modele-ti, modele-social, Les modèles de pension de l'OCDE, Ageing Report et ses fiches pays), et 205 écarts y ont été trouvés. 13 sont à confronter au scénario 1 en premier, parce que leur code est ouvert, qu'ils ne l'ont jamais été et qu'ils ne dépendent d'aucune autre source du registre ; dans l'ordre du registre, qui range les administrations d'abord : `edifis`, `saphir`, `modele_as`, `catala`, `ir_catala`, `euromod`, et 7 autres.
- **Ce que les autres modèles font mieux** (action 138) : 287 points, lus chez 66 modèles : 58 à reprendre, 47 à trancher par le propriétaire (des choix du programme), 133 repris, 10 écartés, 39 coupés (léger ou nul, déclaré sans être fait). Les points à reprendre, par chantier de la feuille de route : 138.2 (1), 138.3 (10), 138.5 (5), 138.7 (3), 138.8 (1), 138.10 (10), 138.11 (1), 138.12 (1), 138.14 (13), 138.18 (5), 138.19 (1), 155.1 (1), 155.2 (1), 155.3 (3), 156.1 (1), 157.1 (1).
- **Les fiches sans exemple officiel** : 187.
- **Les domaines sans décision** (§ 8) : 130 fiches du droit réel qu'aucun des 5 univers de la proposition ne décide. 69 disent leur étape, et c'est une décision qui manque : `agirc_arrco_valeur_achat`, `assiette_minimale_independants`, `assiette_sociale_independants`, `asv_autres_professions_de_sante`, `asv_medecins_ajustement`, `asv_medecins_points`, `cci_paris_transfert_2006`, `cci_roubaix_transfert_1998`, `chomage_retraite_complementaire`, `compagnie_generale_eaux_transfert_1991`, `conjoint_collaborateur_independants`, `cotisation_maladie_des_non_residents`, `cotisation_maladie_pensions_complementaires`, `cotisation_vieillesse_independants`, `credit_foncier_transfert_1989`, `crfm_mayotte_pension_unique`, `crfom_regime_du_decret_1950`, `csg_des_pensions_selon_le_revenu`, `cultes_retraite_complementaire_taux_specifiques`, `cumul_emploi_retraite_et_retraite_progressive`, `cumul_emploi_retraite_fonction_publique`, `droits_apres_la_premiere_pension`, `elus_nouvelle_caledonie_cafat`, `financement_chomage_complementaire`, `igrante_points`, `interpenetration_fonction_publique`, `ipacte_points`, `ircantec_valeurs_point`, `limite_age_banque_de_france`, `limite_age_contractuels`, `limite_age_fonction_publique`, `limite_age_ieg`, `limite_age_militaires`, `limite_age_mines`, `limite_age_opera`, `limite_age_ouvriers_etat`, `limite_age_seita`, `limite_age_sncf_ratp`, `liquidation_regime_par_regime`, `liquidation_unique_regimes_alignes`, `maintien_en_fonctions_jusqu_a_70_ans`, `maintiens_en_fonctions_de_certains_corps`, `majoration_exceptionnelle_2023`, `majorations_forfaitaires_1972_1982`, `micro_social_abattement`, `organic_conjoints_de_commercants`, `parlement_europeen_affiliation`, `pension_d_invalidite_substituee`, `plafond_limite_age_fonction_publique`, `points_au_prorata_des_cotisations`, `points_invalidite_independants`, `prolongation_activite_carriere_incomplete`, `prolongation_activite_categorie_active`, `rafp_age_d_ouverture`, `rafp_compte_epargne_temps`, `rafp_cotisation_volontaire_outre_mer`, `rafp_gipa_hors_plafond`, `ravgdt_allocation_viagere`, `rci_seuil_premiere_tranche`, `rco_points_gratuits_66`, `recul_limite_age_enfants`, `regies_ferroviaires_pensions_en_extinction`, `relevement_des_exploitants_2023`, `residence_et_minimum_vieillesse`, `retablissement_fonction_publique`, `retraite_progressive`, `retraite_proportionnelle_msa`, `services_passes_outre_mer`, `totalisation_des_periodes_etrangeres`. Les 61 autres ne disent pas encore leur étape, et une couche ne les atteint que par leur nom : la plupart sont des règles de la liquidation, que le compte notionnel remplace, et leur étape les rangera.
- **Faire mûrir la carte** : 834 champs obligatoires manquent, à 126 fiches. Par champ :

  | Champ | Fiches à qui il manque |
  |---|---|
  | `versions` | 108 |
  | `dates_qui_decident` | 107 |
  | `domaine` | 107 |
  | `ecrit` | 107 |
  | `lit` | 107 |
  | `regimes` | 107 |
  | `code` | 76 |
  | `etape` | 75 |
  | `approximations` | 40 |

- **Les textes** : 480 rédactions à rattacher à une version de la fiche qui les cite, 4 001 à examiner, et 9 679 sans statut, que le cliquet tient à 9 679 au plus. Les textes qui en ont le plus : `css` 5 016, `decret_46_2769` 938, `rural` 891, `cpcmr` 574, `decret_90_1215` 325 (`python scripts/textes.py`).
- **Les relectures prévues les plus proches** : 2026-10-31 (`agirc_arrco_valeur_achat`) ; 2026-11-15 (`agirc_arrco_valeur_service`) ; 2026-11-30 (`majoration_dix_pour_cent`) ; 2026-12-31 (`age_legal_par_generation`) ; 2026-12-31 (`carriere_longue`).
- **Les régimes hors champ** : 23, chacun avec sa raison dans l'inventaire.

## 4. Ce que ce tableau ne sait pas encore dire

- **L'effet chiffré de chaque limite.** Les fiches le disent en mots. Le pilote le mesurera, en neutralisant la règle sur les cas types pondérés.
- **La part des pensions qui ne passent que par des règles conformes.** Il faut pour cela que chaque ligne du relevé cite sa fiche, ce que l'architecture prévoit aux phases 4 et 5.
- **Ce que personne n'a encore noté, hors des articles.** Pour les articles, le dénominateur est la loi (section 1). Les situations des fiches service-public et des circulaires, les accords Agirc-Arrco et les statuts des caisses n'ont pas encore de liste.
- **Les règles du code qui ont leur fiche.** Une fiche dira son code. Celles que les interrupteurs des régimes désignent disent la valeur qu'elles y posent ; aucune ne nomme encore sa fonction, et le tableau compte en attendant les identifiants que le code cite.
- **Les limites propres à une simulation.** Le site les montrera avec chaque résultat, et les présomptions qu'elle emploie : la chronologie les liste, le site ne les affiche pas encore.
- **Le coût du travail** se relève sur l'historique git, et change à chaque commit : il s'affiche à la demande, par `python scripts/tableau_de_bord.py --cout`, avec les rouges de la suite sur `main` et la taille du dépôt — ses lignes, ses tests —, que la prose ne porte plus.
