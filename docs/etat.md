# État du dépôt

*Le tableau de bord (`docs/architecture.md`, § 9.1). Fabriqué par `scripts/tableau_de_bord.py` depuis la carte des règles, la liste de contrôle des textes et les registres qui ne sont pas encore des vues : aucun nombre n'y est écrit à la main. Pour le corriger, on corrige la fiche ou le registre, puis on relance le script ; un test refuse une copie périmée.*

## 1. Où en est-on

**Les régimes.** L'inventaire en compte 91 : 34 modélisés, 40 partiels, 15 hors champ, 2 routages.

Pesés par leurs retraités de droit direct (2024, enquête EACR de la DREES, où un polypensionné compte dans chacune de ses caisses) :

| Couverture | Retraités-caisses | Part |
|---|---|---|
| régime modélisé | 35 010 992 | 88 % |
| régime partiel | 4 354 564 | 11 % |
| sections libérales, couverture mêlée | 424 386 | 1 % |

*Modélisé ne veut pas dire exact* : les 52 règles approchées de la carte touchent aussi des régimes modélisés (section 2).

**La carte des règles** (`data/reference/regles/`) : 131 fiches, dont 1 relation. La veille en est une vue (`python scripts/veille_droit.py`).

| État | Fiches |
|---|---|
| conformes | 47 |
| transcrites | 25 |
| approchées | 52 |
| pas encore modélisées | 3 |
| manquantes | 3 |
| à vérifier | 1 |

- Confrontées à au moins un exemple officiel : **41 sur 131** (110 exemples : 105 reproduits, 5 en écart connu, section 2).
- Citées dans le code par leur identifiant : **40 sur 131**. Le lien entre une règle et le code qui l'applique n'existe pas encore pour les autres.
- Désignées par les interrupteurs des périodes de régime : **42 sur 131**, par 2 273 renvois ; chacune déclare la valeur que le moteur lit (`code.interrupteurs`) et dit ce qu'il en fait.
- Mûres, sans rien qui manque à leur contrat : **21 sur 131**. Une fiche tirée d'un registre ne sait pas encore son domaine, ses régimes, son étape ni ses versions : ce qui lui manque est à faire (section 3).
- Découpées en versions : **21 sur 131**, soit 106 versions, dont 11 supposées ; le partage des versions se contrôle sur chacune.
- Réformes du calendrier : 110, dont 10 déclarées non appliquées.

**La loi, rédaction par rédaction** (`data/reference/textes/`, § 6.6) : 11 617 rédactions d'articles, de 67 textes, lues le 2026-10-01 (index LEGI du dépôt : Freemium_legi_global_20250713-140000.tar.gz, incréments appliqués jusqu'au 20260930-215413). C'est le dénominateur de l'avancement : ce que les fiches ont lu, contre ce que la loi a écrit.

| Statut | Rédactions |
|---|---|
| rattachées à une version | 294 |
| sans effet | 60 |
| à rattacher | 352 |
| à examiner | 770 |
| sans statut | 10 141 |

**La personne** (§ 5) : une chronologie de faits datés, dans un réseau de personnes — aujourd'hui l'assuré, ses enfants et son conjoint —, que le relevé et le parcours déclarent (`src/retraite_notionnelle/chronologie.py`, et son jumeau). La carrière que le moteur liquide en est la vue. Ce que la saisie ne dit pas est présumé : 18 présomptions au vocabulaire, dont 3 posent leur fait dans la chronologie ; les autres s'appliquent dans le code, jusqu'à l'étape qui posera le leur.

| Présomption | Valeur | Fiches qui la lisent | Où elle s'applique |
|---|---|---|---|
| `jour_de_naissance` | 15 du mois | `date_effet_mois_suivant` | posée par la chronologie |
| `naissance_des_enfants` | 30 ans | `enfants_fonction_publique`, `majoration_duree_assurance_enfants`, `priorite_majorations_enfants` | posée par la chronologie |
| `radiation_au_1er_janvier_suivant` | le 1er janvier qui suit la dernière année de services, ou le départ s'il part en fonctions | `enfants_fonction_publique`, `pension_differee_fonction_publique`, `priorite_majorations_enfants`, `retablissement_fonction_publique` | droit_a_pension (droit/coordonner.py), et la revalorisation de la pension différée (droit/liquider.py) ; leurs jumeaux JavaScript ; son fait entrera à l'étape `coordonner_les_affiliations` |
| `agent_en_activite` | en activité, avec services effectifs | `services_et_duree_fonction_publique` | _ligne_annuelle, qui fait de toute année d'emploi une année de services (carriere.py, carriere.js) ; son fait entrera à l'étape `compter_les_durees` |
| `pas_d_accord_des_parents` | aucun accord ; le défaut légal les donne à la mère | `majoration_duree_assurance_enfants` | le paramètre beneficiaire des versions de la fiche majoration_duree_assurance_enfants, lu par MajorationsPourEnfants.par_enfant ; son fait entrera à l'étape `compter_les_durees` |
| `enfant_eleve_neuf_ans` | élevé neuf ans | `majoration_duree_assurance_enfants` | les versions mda_1972 et mda_1975 de la fiche majoration_duree_assurance_enfants, qui écartent l'enfant de moins de neuf ans et présument les autres élevés par leur mère ; son fait entrera à l'étape `compter_les_durees` |
| `interruption_d_activite_par_la_mere` | remplie par la mère seule | `enfants_fonction_publique` | le paramètre beneficiaire (mere) des versions de la fiche enfants_fonction_publique, lu par MajorationsPourEnfants.par_enfant ; son fait entrera à l'étape `compter_les_durees` |
| `mariage_des_conjoints` | 27 ans | `reversion`, `reversion_fonction_publique` | posée par la chronologie |
| `ressources_du_survivant` | 0 euros par an | `reversion` | reversion (droit/reversion.py), qui ne compte au plafond du régime général que les réversions des autres régimes de base ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `conjoint_de_l_autre_sexe` | l'autre sexe | `reversion_agirc_arrco`, `reversion_fonction_publique` | la saisie, qui donne au conjoint l'autre sexe quand elle ne le dit pas (saisie.py, saisie.js) ; son fait entrera à l'étape `preparer_la_chronologie` |
| `reversion_demandee_dans_l_annee` | dans l'année | `reversion`, `reversion_agirc_arrco` | la date d'effet de la réversion (droit/reversion.py), au premier jour du mois qui suit le décès, ou qui suit l'âge requis ; son jumeau JavaScript ; son fait entrera à l'étape `liquider_chaque_regime` |
| `deces_apres_le_depart` | au départ | `reversion`, `reversion_agirc_arrco`, `reversion_fonction_publique` | l'échéancier (echeancier.py), qui liquide alors une réversion d'essai, hors du journal ; son jumeau JavaScript ; son fait entrera à l'étape `echeancier` |
| `validation_ircantec_demandee` | demandée | `retablissement_fonction_publique` | retablir (droit/coordonner.py), et l'assiette de l'Ircantec des années rétablies (droit/acquerir.py) ; leurs jumeaux JavaScript ; son fait entrera à l'étape `coordonner_les_affiliations` |
| `depart_de_chaque_regime` | au départ déclaré, à l'ouverture du régime, ou à la sortie de l'armée | `liquidation_regime_par_regime` | departs (droit/departs.py), que l'échéancier et le scénario 1 lisent ; son jumeau JavaScript ; son fait entrera à l'étape `echeancier` |
| `pension_d_invalidite_de_la_periode` | depuis le 1er janvier de la première année de la période d'invalidité finale | `pension_d_invalidite_substituee` | Carriere.pension_d_invalidite (carriere.py), et son jumeau JavaScript ; son fait entrera à l'étape `ouvrir_le_droit` |
| `opposition_a_la_substitution` | opposée, la pension demandée au départ déclaré | `pension_d_invalidite_substituee` | substitution (droit/invalidite.py), et son jumeau JavaScript ; son fait entrera à l'étape `echeancier` |
| `pas_de_pension_etrangere` | aucune | `minimum_contributif_international` | pensions_a_l_ecretement (droit/etranger.py), que l'écrêtement du minimum contributif lit (droit/completer.py) ; leurs jumeaux JavaScript ; son fait entrera à l'étape `preparer_la_chronologie` |
| `residence_en_france` | en France | `residence_et_minimum_vieillesse` | foyer_et_net (droit/foyer.py), qui ne sert l'allocation de solidarité aux personnes âgées qu'à qui réside en France ; son jumeau JavaScript ; son fait entrera à l'étape `preparer_la_chronologie` |

**Le relevé des droits** (§ 7.2 et 7.6) : pour chaque demande, quatre étapes le construisent, une par module dans `src/retraite_notionnelle/droit/` et son jumeau `moteur/js/droit/`, chacune écrivant la donnée que son schéma décrit (`data/reference/etapes/`) ; la liquidation du scénario 1 ne lit que lui. Les relevés des 13 cas types, à chacune de leurs générations — 91 relevés —, comptent 22 789 lignes, dont 733 citent la fiche qui les écrit (3 %) et 14 sa version.

| Étape | Module | Ce qu'elle écrit | Fiches qui disent l'appliquer |
|---|---|---|---|
| `preparer_la_chronologie` | `droit/preparer.py` | la chronologie, présomptions posées (contrat C.1) | aucune encore |
| `coordonner_les_affiliations` | `droit/coordonner.py` | les régimes qui reçoivent chaque ligne, les rétablissements, les groupes | `interpenetration_fonction_publique`, `liquidation_unique_regimes_alignes`, `retablissement_fonction_publique`, `totalisation_des_periodes_etrangeres` |
| `compter_les_durees` | `droit/compter.py` | les trimestres de chaque compte, par régime et par année ; ceux des enfants | `enfants_fonction_publique`, `majoration_duree_assurance_enfants`, `priorite_majorations_enfants`, `services_et_duree_fonction_publique` |
| `acquerir_les_droits` | `droit/acquerir.py` | les points et les cotisations, la durée plafonnée, les points gratuits | `assiette_minimale_agricole`, `assiette_minimale_independants`, `asv_medecins_ajustement`, `cotisation_par_classes_liberales`, `droits_apres_la_premiere_pension`, `garantie_minimale_points_agirc`, `rco_points_gratuits`, `retraite_proportionnelle_msa` |

**La liquidation** (§ 7.3, 7.4 et 7.7) : `liquider(demande, état, contexte)`, une fonction pure (`src/retraite_notionnelle/droit/liquidation.py`, et son jumeau), enchaîne l'acquisition et trois étapes, et mesure par des liquidations d'essai ce qu'apporte chaque avantage. L'échéancier (`echeancier.py`) l'appelle au départ, applique à l'échéance les deux étapes qui ne liquident rien, et inscrit tout à son journal (`journal.py`) ; le pilote (`pilote.py`) date les départs des cas types sans rien liquider. Les 689 témoins font chacun de 1 à 12 appels de `liquider`, liquidations d'essai comprises, et au plus 6 par départ ; aucun ne dépasse les 6 par départ que le nombre déclaré accorde (§ 7.8).

| Étape | Module | Ce qu'elle écrit | Fiches qui disent l'appliquer |
|---|---|---|---|
| `ouvrir_le_droit` | `droit/ouvrir.py` | l'âge d'ouverture et son motif, la durée requise, les trimestres cotisés | `age_legal_par_generation`, `carriere_longue`, `duree_requise_par_generation`, `inaptitude_au_travail` |
| `liquider_chaque_regime` | `droit/liquider.py` | la pension de chaque régime et sa formule, les régimes qui portent les minima | `coefficients_anticipation_agirc_arrco`, `decote_avant_1983`, `decote_opera_de_paris`, `decote_regime_general`, `decote_regimes_speciaux`, `majoration_duree_apres_65_ans`, `minoration_racl_2014_2024`, `pension_non_salaries_agricoles_2026`, `pension_proratisee`, `retraite_pour_invalidite_fonction_publique`, `reversion`, `reversion_agirc_arrco`, `reversion_fonction_publique`, `salaire_annuel_moyen`, `seconde_pension`, `surcote_ircantec`, `surcote_par_age_seul`, `surcote_regime_general`, `surcote_regimes_speciaux`, `taux_plein_et_proratisation` |
| `completer_tous_regimes` | `droit/completer.py` | les minima, la surcote parentale, la majoration pour enfants | `majoration_dix_pour_cent`, `minimum_contributif`, `minimum_contributif_international`, `minimum_garanti`, `surcote_parentale` |
| `faire_vivre` | `revalorisation.py` | le coefficient de chaque pension, du départ à l'échéance | `revalorisation_des_pensions` |
| `foyer_et_net` | `droit/foyer.py` | l'ASPA, au départ puis à chaque échéance | `minimum_vieillesse`, `residence_et_minimum_vieillesse` |

**La proposition, en univers de droit** (§ 4.8 et 8) : chaque scénario est une pile de couches posée sur le droit réel, que l'univers déclare (`data/reference/univers/`, `data/reference/couches/`) ; le simulateur en tire ses scénarios, et le paquet du site les porte résolus. 9 fiches de la proposition (`data/reference/regles/proposition/`) décrivent ce que les couches ajoutent, en citant son texte. Les fiches du droit réel qu'aucune couche d'un univers ne garde, ne remplace ni ne neutralise sont ses domaines sans décision (section 3).

| Scénario | Univers | Couches posées sur le droit réel | Fiches ajoutées | Fiches du droit réel sans décision |
|---|---|---|---|---|
| 1 | `actuel` | aucune : c'est l'étalon | 0 | — |
| 2 | `notionnel_retroactif` | `comptes_notionnels` | 5 | 77 sur 131 |
| 3 | `notionnel_prospectif` | `contributif_seul`, `valorisation_des_droits_acquis`, `comptes_notionnels` | 6 | 77 sur 131 |
| 4 | `notionnel_retroactif_employeur` | `comptes_notionnels`, `part_patronale` | 5 | 77 sur 131 |
| 5 | `notionnel_prospectif_employeur` | `contributif_seul`, `valorisation_des_droits_acquis`, `comptes_notionnels`, `part_patronale` | 6 | 77 sur 131 |
| 6 | `notionnel_liberal` | `comptes_notionnels`, `part_patronale`, `taux_unique`, `capitalisation_obligatoire`, `garantie_vieillesse`, `age_legal_de_la_proposition` | 8 | 77 sur 131 |

**La réorganisation** (§ 6.5, § 11). Les registres devenus des vues de la carte : la veille. Restent des registres : la frontière contributive, l'inventaire des régimes.

**Ce qui est hors de la page Coût.** La réversion, par exemple, pèse 10,4 % de la masse des prestations en 2024 (COR) : le modèle en calcule une pour une personne (scénario 1), mais la page Coût n'en connaît que cette part publiée, qu'elle ne calcule pas.

**La feuille de route** compte 141 actions : 125 fait, 11 en cours, 3 à faire, 1 archivée, 1 abandonnée. Les closes sont dans son archive, `docs/archives/feuille_de_route.md` ; ce qui reste à faire est ailleurs, dispersé.

## 2. Ce qui ne va pas encore

**Les régimes partiels, du plus peuplé au moins peuplé**

| Régime | Retraités | Ce qui manque |
|---|---|---|
| Pensions civiles et militaires de retraite (Service des retraites de l'État) | 2 018 190 | Les bonifications de SERVICE — dépaysement, campagne, cinquième — ne sont pas servies, faute de connaître le corps et le détail des services |
| Assurance vieillesse des non-salariés agricoles (MSA) | 1 023 064 | Le barème en points d'avant 1990 n'est pas lu, et ses années entrent dans la moyenne de la réforme de 2026 par les points que vaut leur rendement |
| Retraite complémentaire obligatoire des non-salariés agricoles | 616 621 | Les points gratuits des chefs d'exploitation pour leurs années d'avant 2003 sont servis |
| Caisse nationale d'assurance vieillesse des professions libérales, régime de base | 460 991 | Le libéral non réglementé installé depuis 2019 relève du régime général et du RCI, celui installé avant reste à la CNAVPL et à la Cipav : le statut `liberal_non_reglemen… |
| Régime spécial de sécurité sociale dans les mines (CANSSM) | 86 133 | La complémentaire des mineurs n'est pas routée : le statut `mineur` ne cotise qu'au régime des mines. |
| Caisse de retraite et de prévoyance des clercs et employés de notaires | 70 377 | Deux âges avant 2008 — soixante ans, ou cinquante-cinq pour l'assurée justifiant de vingt-cinq années de cotisations — et le moteur n'en porte qu'un : la fiche garde le… |
| Régime des marins (ENIM) | 62 598 | La grille des vingt catégories est lue au Journal officiel depuis 2008 (`salaires_forfaitaires.csv`, arrêtés annuels) et appliquée : le marin est rangé chaque année dans… |
| Caisse nationale des barreaux français, régime de base | 16 590 | La progression de la cotisation forfaitaire sur les cinq premières années et la contribution équivalente aux droits de plaidoirie ne sont pas portées, ni la majoration d… |

Et 32 régimes partiels sans effectif dans l'enquête (outre-mer, sections libérales, régimes fermés…).

**Les règles approchées, absentes ou à vérifier**, avec ce que leur fiche dit de leur effet :

| Règle | État | Qui est touché |
|---|---|---|
| `majoration_enfants_plafond_fonction_publique` | manquante | Ne mord qu'à partir de sept enfants au taux de 80 %, ou de six avec une surcote que la caisse excepte : quelques familles, que le modèle ma… |
| `rci_seuil_premiere_tranche` | manquante | Artisans et commerçants au-dessus du seuil, de 2014 à 2024 : la fiche coupe la première tranche au plafond de chaque année (46 368 € en 202… |
| `temps_partiel_fonction_publique` | manquante | Tout fonctionnaire qui a travaillé à temps partiel sans surcotiser : le modèle compte chaque année à temps plein, aucune saisie ne portant… |
| `inaptitude_invalidite_penibilite_amiante` | pas_encore_modelisee | Assurés concernés déclarés non ouverts ou décotés à tort. |
| `rachats_et_versements` | pas_encore_modelisee | Non saisissables dans le simulateur. |
| `retraite_anticipee_handicap` | pas_encore_modelisee | Demande une information médicale que le modèle ne collecte pas : l'assuré est déclaré non ouvert. |
| `fin_de_la_suspension_2028` | a_verifier | Tout changement de calendrier touche les générations 1965 et suivantes. |
| `assiette_minimale_agricole` | approchee | Les chefs d'exploitation aux revenus faibles, et, à la complémentaire, tous les chefs qui cotisent depuis 2017. |
| `assiette_minimale_independants` | approchee | Un indépendant à 3 000 € validait un trimestre au lieu de trois et n'avait ni le salaire ni les points du minimum. |
| `asv_medecins_ajustement` | approchee | La fiche servait 36 points à tout médecin, soit jusqu'à 7,75 points de trop sous 70 000 €. |
| `carcdsf_minoration_age_seul` | approchee | La fiche lisait 62 et 67 ans et la décote du régime de base, que la durée annule : un dentiste parti à 64 ans avec sa durée ne perdait rien… |
| `carmf_asv_minoration_enfants` | approchee | De 2000 à 2016, la fiche disait l'âge seul sans que le moteur le lise : un médecin parti à 64 ans avec sa durée n'était pas minoré. |
| `carpimko_ages_2015` | approchee | La fiche lisait 67 ans dès la génération 1955 |
| `carpimko_assiette_2026` | approchee | La fiche retranchait un demi-plafond de tout revenu et reconduisait le rendement de 2025, 7,36 % : un tiers de points de trop au-dessus d'u… |
| `carpv_minoration_age_seul` | approchee | La fiche écrivait la règle d'âge en laissant sa durée requise vide |
| `cavamac_minoration_age_seul` | approchee | La fiche opposait la décote du régime de base, que la durée annule : un agent général parti à l'âge légal avec sa durée ne perdait rien de… |
| `cavec_minoration_age_seul` | approchee | La note de la fiche disait la règle, mais la période laissait la durée annuler la minoration, et lisait avant 2008 les âges du régime génér… |
| `cavom_ages_minoration` | approchee | La fiche lisait les tables du régime général et la décote du régime de base, que la durée annule : un officier ministériel parti à l'âge lé… |
| `cavp_minoration_deux_pentes` | approchee | La fiche lisait la décote du régime de base, que la durée annule : un pharmacien parti à 64 ans avec sa durée ne perdait rien de sa complém… |
| `cnavpl_majoration_duree_assurance` | approchee | La fiche les disait non portés, et le moteur ne cherchait la majoration de durée que dans les régimes en annuités : une libérale qui n'avai… |
| `coefficients_anticipation_agirc_arrco` | approchee | Toute liquidation anticipée d'une complémentaire des salariés du privé : 1 % à 22 % de moins sur vingt trimestres, jusqu'à 57 % dix ans ava… |
| `cotisation_par_classes_liberales` | approchee | Les vétérinaires, les experts-comptables et commissaires aux comptes, et les affiliés de la Cipav jusqu'en 2022. |
| `cultes_salaire_annuel_moyen` | approchee | Le salaire annuel moyen est désormais fait du forfait de chaque année, dans les deux moteurs (`_assiette_de_reference`) : le ministre décla… |
| `cumul_emploi_retraite_et_retraite_progressive` | approchee | Le retraité qui travaille avant le taux plein : la salariée née en 1960, partie à 62 ans en 2022 sans la durée requise, qui reprend un empl… |
| `cumul_emploi_retraite_fonction_publique` | approchee | Le fonctionnaire retraité qui travaille avant le taux plein : payé par un employeur public, ou par tout employeur s'il est civil et parti d… |
| `decote_avant_1983` | approchee | Les pensions du régime général et des salariés agricoles liquidées avant 1983, et celles des artisans et commerçants de 1973 à 1982. |
| `decote_crpn` | approchee | L'âge d'annulation passe de 65 à 60 ans pour toute liquidation depuis 2012, et la décote se compte sur la durée seule depuis 2022. |
| `droits_apres_la_premiere_pension` | approchee | Toute personne qui travaille après sa première pension, dans le même régime ou dans un autre : le fonctionnaire de catégorie active parti à… |
| `enfants_fonction_publique` | approchee | Toute mère fonctionnaire ou agente d'un régime spécial : quatre trimestres par enfant né avant 2004, en services, donc au prorata de la pen… |
| `garantie_minimale_points_agirc` | approchee | Tout cadre payé sous le salaire charnière entre 1989 et 2018 — 1,11 plafond en 2018 —, surtout en début de carrière. |
| `inaptitude_au_travail` | approchee | Les retraités partis au taux plein pour inaptitude : 1,36 million fin 2016 (DREES, EIR), et avec les ex-invalides 19 % des nouveaux retrait… |
| `liquidation_regime_par_regime` | approchee | Tout polypensionné dont les régimes n'ouvrent pas au même âge : le fonctionnaire de catégorie active ou le militaire qui a aussi travaillé… |
| `majoration_duree_apres_65_ans` | approchee | Les assurés du régime général, des salariés agricoles et des artisans et commerçants qui liquident après l'âge du taux plein sans la durée… |
| `majoration_duree_assurance_enfants` | approchee | Toute mère affiliée au régime général ou à un régime aligné : la règle commande la décote, la proratisation, la surcote parentale et le sal… |
| `majoration_enfants_liberaux_avocats` | approchee | Les fiches de la CNAVPL, de la CNBF et de sa complémentaire ne la portaient pas : 10 % de pension en moins pour tout parent de trois enfant… |
| `marins_salaire_de_reference` | approchee | Le modèle prend la catégorie de la DERNIÈRE année, rangée par le revenu, et compte les services au trimestre |
| `minimum_contributif_international` | approchee | Les petites pensions françaises des carrières internationales, au taux plein par la totalisation : le minimum de la pension proratisée se r… |
| `minimum_vieillesse` | approchee | Les plus petites pensions |
| `minoration_ircec` | approchee | Tout départ anticipé d'un artiste-auteur, d'un auteur dramatique ou d'un compositeur qui n'a pas sa durée : à soixante-deux ans, 20 % de mi… |
| `minoration_racl_2014_2024` | approchee | Les auteurs et compositeurs lyriques partis avant l'âge du taux plein, de 2014 à mai 2025. |
| `pension_d_invalidite_substituee` | approchee | Les titulaires d'une pension d'invalidité à l'âge légal : 0,90 million de retraités partis au taux plein à ce titre fin 2016 (DREES, EIR). |
| `pension_mines` | approchee | Mineurs. |
| `pension_non_salaries_agricoles_2026` | approchee | Les chefs d'exploitation dont la pension prend effet depuis le 1er janvier 2026, et le salaire annuel moyen de leurs régimes alignés quand… |
| `pension_proratisee` | approchee | Toute pension française d'une carrière passée aussi par un État lié à la France par un accord qui compare : la pension proratisée, au taux… |
| `priorite_majorations_enfants` | approchee | Toute mère passée par un régime spécial et par un régime aligné. |
| `raap_classe_speciale` | approchee | La fiche prélevait 8 % du revenu avant 2016 — un taux qu'aucun texte ne porte — et servait donc, à un revenu moyen, quatre à six fois les p… |
| `rafp_majoration_capital` | approchee | Le modèle servait la valeur de service nue à tout âge : 22 % de moins à 67 ans. |
| `residence_et_minimum_vieillesse` | approchee | Les retraités qui vivent hors de France : 1,28 million fin 2024 (DREES, enquête annuelle auprès des caisses). |
| `retraite_pour_invalidite_fonction_publique` | approchee | Les fonctionnaires radiés des cadres pour invalidité, à tout âge. |
| `retraite_progressive` | approchee | Les salariés, les indépendants et, depuis 2023, les fonctionnaires, les libéraux et les avocats qui passent à temps partiel en fin de carri… |
| `retraite_proportionnelle_msa` | approchee | Les chefs d'exploitation, pour leurs années depuis 1990. |
| `reversion` | approchee | Tout conjoint, ou ex-conjoint, d'un assuré du régime général ou d'un régime aligné qui décède : 4,41 millions de bénéficiaires d'un droit d… |
| `reversion_agirc_arrco` | approchee | Tout conjoint, ou ex-conjoint marié, d'un salarié ou ancien salarié du privé qui décède. |
| `reversion_fonction_publique` | approchee | Tout conjoint, ou ex-conjoint, d'un fonctionnaire de l'État ou d'un agent des collectivités qui décède. |
| `seconde_pension` | approchee | Les retraités en cumul intégral depuis 2023 : leurs cotisations, jusque-là à fonds perdus, leur ouvrent une seconde pension, au plus 5 % du… |
| `sections_liberales_majoration_enfants` | approchee | Aucune des trois fiches ne la portait : 10 % de complémentaire en moins pour tout parent de trois enfants. |
| `surcote_par_age_seul` | approchee | Les complémentaires de la CARMF, de la CARPIMKO, de la CAVEC, de la CAVP, de la Cipav et de la CPRN, et l'ASV des médecins, dont les périod… |
| `totalisation_des_periodes_etrangeres` | approchee | Toute personne qui a travaillé hors de France : 1,28 million de retraités résidaient à l'étranger fin 2024 (DREES, enquête annuelle auprès… |
| `un_statut_par_annee` | approchee | DEPUIS LE 22 SEPTEMBRE 2026, DEUX ACTIVITÉS À LA FOIS se décrivent, dans les deux moteurs : chacune verse à son régime, sur son revenu, et… |

**Un état peut-être périmé.** Pour 17 des 52 règles approchées, l'effet raconte à l'imparfait l'erreur qui a été corrigée, sans dire ce qui reste. Le tableau ne peut pas savoir si elles sont encore approchées : leur fiche le dira quand elle mûrira, l'écart actuel dans ses approximations, le récit dans son historique.

**Des approximations non déclarées.** 32 des 52 fiches approchées ne déclarent encore ses approximations, chacune avec son effet ou « non mesuré » : l'effet n'en est dit qu'en mots.

**Les exemples officiels que le modèle ne reproduit pas**, entrés en écart connu, avec la règle qui le déclare :

| Exemple | Grandeur | Publié | Modèle | Règle |
|---|---|---|---|---|
| `cnav_22_83_taux_acquis_117_trimestres` | taux_liquidation | 0,55 | 0,5 | `decote_avant_1983` |
| `cnav_22_83_taux_acquis_117_trimestres` | pension_base_sur_sam | 0,429 | 0,44 | `decote_avant_1983` |
| `aa_reversion_francois` | dates_d_effet_de_la_reversion | arrco 2025-01-01 | arrco 2024-12-01 | `reversion_agirc_arrco` |
| `aa_reversion_david` | dates_d_effet_de_la_reversion | arrco 2024-10-01 | arrco 2024-08-01 | `reversion_agirc_arrco` |
| `aa_reversion_simone` | dates_d_effet_de_la_reversion | arrco 2025-01-01 | arrco 2024-03-01 | `reversion_agirc_arrco` |
| `ur_reversion_prive_50_ans_deux_enfants` | dates_d_effet_de_la_reversion | agirc_arrco 2026-09-01, arrco 2026-09-01, regime_general 2031-04-01 | agirc_arrco 2031-04-01, arrco 2031-04-01, regime_general 2031-04-01 | `reversion_agirc_arrco` |

## 3. Ce qui reste à faire, et par quoi commencer

- **Les 11 actions en cours** de la feuille de route :
  - 47. La garantie vieillesse est une avance : la reprise sur succession, sa règle et son chiffrage
  - 89. Dépouiller les 260 sources officielles remises le 22 septembre 2026
  - 119. Les complémentaires relues : le plafond du RAFP, les points gratuits de la RCO, l'Arrco des cultes, et trois trous que rien ne disait
  - 121. Le droit de chacun, et non celui de la génération de l'année : toutes les personnes vivantes
  - 129. Le taux de l'État ramené à sa part « retraite seule » : un réglage, puis le défaut
  - 130. L'architecture du dépôt : décidée, les phases 0 à 8 faites, les domaines à ouvrir
  - 131. Les dix fiches nées à la phase 6, relues à la source : les écarts qu'elles montrent, à corriger
  - 133. La retraite de base et ses complémentaires, sous le montant du système 1
  - 135. Aller plus vite sans rien céder : l'outillage d'un changement de résultats
  - 137. Les autres modèles publics : le registre exhaustif, puis leur confrontation
  - 138. Meilleur en tous points : ce que les autres modèles font mieux, vérifié, puis repris
- **Les sources à exploiter** : 150 à explorer sur 301 (63 explorées, 88 épuisées). 9 d'entre elles visent un régime partiel, et pourraient le compléter :
  - Association des régimes de retraite complémentaire des salariés : 3 source(s) (agirc_arrco_majorations_enfants, agirc_arrco_textes_de_reference, agirc_arrco_parametres_statistiques)
  - Caisse de retraite et de prévoyance des clercs et employés de notaires : 2 source(s) (crpcen_montant_pension, crpcen_rachat_etudes)
  - Régime des artistes-auteurs professionnels (IRCEC) : 2 source(s) (cnav_arrierees_artiste_auteur, mon_entreprise_artiste_auteur)
  - Caisse nationale d'assurance vieillesse des professions libérales, régime de base : 1 source(s) (mon_entreprise_comparaison_ei)
  - Régime des auteurs et compositeurs dramatiques (IRCEC) : 1 source(s) (mon_entreprise_artiste_auteur)
  - Régime des auteurs et compositeurs lyriques (IRCEC) : 1 source(s) (mon_entreprise_artiste_auteur)
  - Assurance vieillesse des non-salariés agricoles (MSA) : 1 source(s) (msa_reforme_25_meilleures_annees)
  - et 56 sources sans régime désigné.
- **Les autres modèles** (§ 3.4) : 69 au registre (`data/reference/referents.yaml`) : 32 au code ouvert, 1 sur demande, 13 documenté(s) sans leur code, 23 non public(s). 10 ont déjà été confrontés au dépôt ou lui donnent des valeurs (Barèmes IPP, OpenFisca-France, OpenFisca-France-Pension, TRAJECTOiRE, ANCETRE, Maquette globale de projection du COR, Maquette simplifiée du secrétariat général du COR, PRISME (Projection des Retraites, Simulations, Modélisation et Évaluations), modele-ti, modele-social), et 42 écarts y ont été trouvés. 16 sont à confronter au scénario 1 en premier, parce que leur code est ouvert, qu'ils ne l'ont jamais été et qu'ils ne dépendent d'aucune autre source du registre ; dans l'ordre du registre, qui range les administrations d'abord : `destinie_2`, `ines`, `legiretraite`, `edifis`, `saphir`, `modele_as`, et 10 autres.
- **Ce que les autres modèles font mieux** (action 138) : 94 points, lus chez 52 modèles : 82 à reprendre, 9 à trancher par le propriétaire (des choix du programme), 2 repris, 1 écarté. Les points à reprendre, par chantier de la feuille de route : 136.2 (1), 136.3 (2), 136.4 (5), 136.5 (1), 136.6 (1), 138.2 (11), 138.3 (16), 138.4 (2), 138.5 (2), 138.6 (3), 138.7 (4), 138.8 (2), 138.9 (6), 138.10 (5), 138.11 (11), 138.12 (6), 138.14 (4).
- **Les fiches sans exemple officiel** : 90.
- **Les domaines sans décision** (§ 8) : 77 fiches du droit réel qu'aucun des 5 univers de la proposition ne décide. 15 disent leur étape, et c'est une décision qui manque : `assiette_minimale_independants`, `asv_medecins_ajustement`, `cumul_emploi_retraite_et_retraite_progressive`, `cumul_emploi_retraite_fonction_publique`, `droits_apres_la_premiere_pension`, `interpenetration_fonction_publique`, `liquidation_regime_par_regime`, `liquidation_unique_regimes_alignes`, `pension_d_invalidite_substituee`, `rafp_age_d_ouverture`, `residence_et_minimum_vieillesse`, `retablissement_fonction_publique`, `retraite_progressive`, `retraite_proportionnelle_msa`, `totalisation_des_periodes_etrangeres`. Les 62 autres ne disent pas encore leur étape, et une couche ne les atteint que par leur nom : la plupart sont des règles de la liquidation, que le compte notionnel remplace, et leur étape les rangera.
- **Faire mûrir la carte** : 832 champs obligatoires manquent, à 110 fiches. Par champ :

  | Champ | Fiches à qui il manque |
  |---|---|
  | `dates_qui_decident` | 110 |
  | `domaine` | 110 |
  | `ecrit` | 110 |
  | `lit` | 110 |
  | `regimes` | 110 |
  | `versions` | 110 |
  | `etape` | 77 |
  | `code` | 63 |
  | `approximations` | 32 |

- **Les textes** : 352 rédactions à rattacher à une version de la fiche qui les cite, 770 à examiner, et 10 141 sans statut, que le cliquet tient à 10 141 au plus. Les textes qui en ont le plus : `css` 5 167, `rural` 968, `decret_46_2769` 946, `cpcmr` 633, `decret_90_1215` 335 (`python scripts/textes.py`).
- **Les relectures prévues les plus proches** : 2026-11-30 (`majoration_dix_pour_cent`) ; 2026-12-31 (`age_legal_par_generation`) ; 2026-12-31 (`carriere_longue`) ; 2026-12-31 (`certification_legi_perimee`) ; 2026-12-31 (`coefficients_anticipation_agirc_arrco`).
- **Les régimes hors champ** : 15, chacun avec sa raison dans l'inventaire.

## 4. Ce que ce tableau ne sait pas encore dire

- **L'effet chiffré de chaque limite.** Les fiches le disent en mots. Le pilote le mesurera, en neutralisant la règle sur les cas types pondérés.
- **La part des pensions qui ne passent que par des règles conformes.** Il faut pour cela que chaque ligne du relevé cite sa fiche, ce que l'architecture prévoit aux phases 4 et 5.
- **Ce que personne n'a encore noté, hors des articles.** Pour les articles, le dénominateur est la loi (section 1). Les situations des fiches service-public et des circulaires, les accords Agirc-Arrco et les statuts des caisses n'ont pas encore de liste.
- **Les règles du code qui ont leur fiche.** Une fiche dira son code. Celles que les interrupteurs des régimes désignent disent la valeur qu'elles y posent ; aucune ne nomme encore sa fonction, et le tableau compte en attendant les identifiants que le code cite.
- **Les limites propres à une simulation.** Le site les montrera avec chaque résultat, et les présomptions qu'elle emploie : la chronologie les liste, le site ne les affiche pas encore.
- **Le coût du travail** se relève sur l'historique git, et change à chaque commit : il s'affiche à la demande, par `python scripts/tableau_de_bord.py --cout`, avec la taille du dépôt — ses lignes, ses tests —, que la prose ne porte plus.
