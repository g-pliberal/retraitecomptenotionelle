# État du dépôt

*Le tableau de bord (`docs/architecture.md`, § 9.1). Fabriqué par `scripts/tableau_de_bord.py` depuis les registres d'aujourd'hui : aucun nombre n'y est écrit à la main. Pour le corriger, on corrige le registre, puis on relance le script ; un test refuse une copie périmée.*

## 1. Où en est-on

**Les régimes.** L'inventaire en compte 91 : 35 modélisés, 39 partiels, 15 hors champ, 2 routages.

Pesés par leurs retraités de droit direct (2024, enquête EACR de la DREES, où un polypensionné compte dans chacune de ses caisses) :

| Couverture | Retraités-caisses | Part |
|---|---|---|
| régime modélisé | 35 097 125 | 88 % |
| régime partiel | 4 268 431 | 11 % |
| sections libérales, couverture mêlée | 424 386 | 1 % |

*Modélisé ne veut pas dire exact* : les 25 règles approchées de la veille touchent aussi des régimes modélisés (section 2).

**Les règles suivies en veille** : 98.

| État | Règles |
|---|---|
| conformes | 43 |
| transcrites | 21 |
| approchées | 25 |
| hors modèle | 5 |
| manquantes | 3 |
| à vérifier | 1 |

- Confrontées à au moins un exemple officiel : **22 sur 98** (54 exemples, tous reproduits : le test n'admet pas d'exemple qui échoue).
- Citées dans le code par leur identifiant : **12 sur 98**. Le lien entre une règle et le code qui l'applique n'existe pas encore pour les autres.
- Réformes du calendrier : 109, dont 11 déclarées non appliquées.

**Ce qui est hors du modèle.** La réversion, par exemple, pèse 10,4 % de la masse des prestations en 2024 (COR), et le modèle n'en calcule aucune.

**La feuille de route** compte 131 actions : 123 fait, 6 en cours, 1 archivée, 1 abandonnée. Elle raconte ce qui a été fait ; ce qui reste à faire est ailleurs, dispersé.

## 2. Ce qui ne va pas encore

**Les régimes partiels, du plus peuplé au moins peuplé**

| Régime | Retraités | Ce qui manque |
|---|---|---|
| Pensions civiles et militaires de retraite (Service des retraites de l'État) | 2 018 190 | Les bonifications de SERVICE — dépaysement, campagne, cinquième — ne sont pas servies, faute de connaître le corps et le détail des services |
| Assurance vieillesse des non-salariés agricoles (MSA) | 1 023 064 | Le barème en points d'avant 1990 n'est pas lu |
| Retraite complémentaire obligatoire des non-salariés agricoles | 616 621 | Les points gratuits des chefs d'exploitation pour leurs années d'avant 2003 sont servis |
| Caisse nationale d'assurance vieillesse des professions libérales, régime de base | 460 991 | Le libéral non réglementé installé depuis 2019 relève du régime général et du RCI, celui installé avant reste à la CNAVPL et à la Cipav : le statut `liberal_non_reglemen… |
| Caisse de retraite et de prévoyance des clercs et employés de notaires | 70 377 | Deux âges avant 2008 — soixante ans, ou cinquante-cinq pour l'assurée justifiant de vingt-cinq années de cotisations — et le moteur n'en porte qu'un : la fiche garde le… |
| Régime des marins (ENIM) | 62 598 | La grille des vingt catégories est lue au Journal officiel depuis 2008 (`salaires_forfaitaires.csv`, arrêtés annuels) et appliquée : le marin est rangé chaque année dans… |
| Caisse nationale des barreaux français, régime de base | 16 590 | La progression de la cotisation forfaitaire sur les cinq premières années et la contribution équivalente aux droits de plaidoirie ne sont pas portées, ni la majoration d… |

Et 32 régimes partiels sans effectif dans l'enquête (outre-mer, sections libérales, régimes fermés…).

**Les règles approchées, absentes ou à vérifier**, avec ce que le registre dit de leur effet :

| Règle | État | Qui est touché |
|---|---|---|
| `majoration_enfants_plafond_fonction_publique` | manque | Ne mord qu'à partir de sept enfants au taux de 80 %, ou de six avec une surcote que la caisse excepte : quelques familles, que le modèle ma… |
| `rci_seuil_premiere_tranche` | manque | Artisans et commerçants au-dessus du seuil, de 2014 à 2024 : la fiche coupe la première tranche au plafond de chaque année (46 368 € en 202… |
| `temps_partiel_fonction_publique` | manque | Tout fonctionnaire qui a travaillé à temps partiel sans surcotiser : le modèle compte chaque année à temps plein, aucune saisie ne portant… |
| `cumul_emploi_retraite_et_retraite_progressive` | hors_modele | Le modèle liquide une fois, à une date |
| `inaptitude_invalidite_penibilite_amiante` | hors_modele | Assurés concernés déclarés non ouverts ou décotés à tort. |
| `rachats_et_versements` | hors_modele | Non saisissables dans le simulateur. |
| `retraite_anticipee_handicap` | hors_modele | Demande une information médicale que le modèle ne collecte pas : l'assuré est déclaré non ouvert. |
| `reversion` | hors_modele | Le modèle décrit une carrière, pas un ménage. |
| `fin_de_la_suspension_2028` | a_verifier | Tout changement de calendrier touche les générations 1965 et suivantes. |
| `assiette_minimale_independants` | approximation | Un indépendant à 3 000 € validait un trimestre au lieu de trois et n'avait ni le salaire ni les points du minimum. |
| `asv_medecins_ajustement` | approximation | La fiche servait 36 points à tout médecin, soit jusqu'à 7,75 points de trop sous 70 000 €. |
| `carcdsf_minoration_age_seul` | approximation | La fiche lisait 62 et 67 ans et la décote du régime de base, que la durée annule : un dentiste parti à 64 ans avec sa durée ne perdait rien… |
| `carmf_asv_minoration_enfants` | approximation | De 2000 à 2016, la fiche disait l'âge seul sans que le moteur le lise : un médecin parti à 64 ans avec sa durée n'était pas minoré. |
| `carpimko_ages_2015` | approximation | La fiche lisait 67 ans dès la génération 1955 |
| `carpimko_assiette_2026` | approximation | La fiche retranchait un demi-plafond de tout revenu et reconduisait le rendement de 2025, 7,36 % : un tiers de points de trop au-dessus d'u… |
| `carpv_minoration_age_seul` | approximation | La fiche écrivait la règle d'âge en laissant sa durée requise vide |
| `cavamac_minoration_age_seul` | approximation | La fiche opposait la décote du régime de base, que la durée annule : un agent général parti à l'âge légal avec sa durée ne perdait rien de… |
| `cavec_minoration_age_seul` | approximation | La note de la fiche disait la règle, mais la période laissait la durée annuler la minoration, et lisait avant 2008 les âges du régime génér… |
| `cavom_ages_minoration` | approximation | La fiche lisait les tables du régime général et la décote du régime de base, que la durée annule : un officier ministériel parti à l'âge lé… |
| `cavp_minoration_deux_pentes` | approximation | La fiche lisait la décote du régime de base, que la durée annule : un pharmacien parti à 64 ans avec sa durée ne perdait rien de sa complém… |
| `cnavpl_majoration_duree_assurance` | approximation | La fiche les disait non portés, et le moteur ne cherchait la majoration de durée que dans les régimes en annuités : une libérale qui n'avai… |
| `cultes_salaire_annuel_moyen` | approximation | Le salaire annuel moyen est désormais fait du forfait de chaque année, dans les deux moteurs (`_assiette_de_reference`) : le ministre décla… |
| `date_effet_mois_suivant` | approximation | Le modèle liquide au mois de l'anniversaire : un mois d'écart, visible là où un texte coupe au mois (nés en décembre 1965, carrière longue). |
| `decote_crpn` | approximation | L'âge d'annulation passe de 65 à 60 ans pour toute liquidation depuis 2012, et la décote se compte sur la durée seule depuis 2022. |
| `majoration_duree_assurance_enfants` | approximation | Le modèle sert d'un coup les huit trimestres par enfant que le décret de 2003 attribue un par un, de la naissance au septième anniversaire. |
| `majoration_enfants_liberaux_avocats` | approximation | Les fiches de la CNAVPL, de la CNBF et de sa complémentaire ne la portaient pas : 10 % de pension en moins pour tout parent de trois enfant… |
| `marins_salaire_de_reference` | approximation | Le modèle prend la catégorie de la DERNIÈRE année, rangée par le revenu, et compte les services au trimestre |
| `minimum_vieillesse` | approximation | Les plus petites pensions |
| `minoration_ircec` | approximation | Tout départ anticipé d'un artiste-auteur, d'un auteur dramatique ou d'un compositeur qui n'a pas sa durée : à soixante-deux ans, 20 % de mi… |
| `pension_mines` | approximation | Mineurs. |
| `raap_classe_speciale` | approximation | La fiche prélevait 8 % du revenu avant 2016 — un taux qu'aucun texte ne porte — et servait donc, à un revenu moyen, quatre à six fois les p… |
| `rafp_majoration_capital` | approximation | Le modèle servait la valeur de service nue à tout âge : 22 % de moins à 67 ans. |
| `sections_liberales_majoration_enfants` | approximation | Aucune des trois fiches ne la portait : 10 % de complémentaire en moins pour tout parent de trois enfants. |
| `un_statut_par_annee` | approximation | DEPUIS LE 22 SEPTEMBRE 2026, DEUX ACTIVITÉS À LA FOIS se décrivent, dans les deux moteurs : chacune verse à son régime, sur son revenu, et… |

**Un état peut-être périmé.** Pour 17 des 25 règles approchées, l'effet raconte à l'imparfait l'erreur qui a été corrigée, sans dire ce qui reste. Le tableau ne peut pas savoir si elles sont encore approchées : la fiche séparera l'effet actuel de l'historique.

## 3. Ce qui reste à faire, et par quoi commencer

- **Les 6 actions en cours** de la feuille de route :
  - 47. La garantie vieillesse est une avance : la reprise sur succession, sa règle et son chiffrage
  - 89. Dépouiller les 260 sources officielles remises le 22 septembre 2026
  - 119. Les complémentaires relues : le plafond du RAFP, les points gratuits de la RCO, l'Arrco des cultes, et trois trous que rien ne disait
  - 121. Le droit de chacun, et non celui de la génération de l'année : toutes les personnes vivantes
  - 129. Le taux de l'État ramené à sa part « retraite seule » : un réglage, puis le défaut
  - 130. L'architecture du dépôt : décidée, la phase 0 faite, la phase 1 à lancer
- **Les sources à exploiter** : 114 à explorer sur 260 (58 explorées, 88 épuisées). 9 d'entre elles visent un régime partiel, et pourraient le compléter :
  - Association des régimes de retraite complémentaire des salariés : 3 source(s) (agirc_arrco_majorations_enfants, agirc_arrco_textes_de_reference, agirc_arrco_parametres_statistiques)
  - Caisse de retraite et de prévoyance des clercs et employés de notaires : 2 source(s) (crpcen_montant_pension, crpcen_rachat_etudes)
  - Régime des artistes-auteurs professionnels (IRCEC) : 2 source(s) (cnav_arrierees_artiste_auteur, mon_entreprise_artiste_auteur)
  - Caisse nationale d'assurance vieillesse des professions libérales, régime de base : 1 source(s) (mon_entreprise_comparaison_ei)
  - Régime des auteurs et compositeurs dramatiques (IRCEC) : 1 source(s) (mon_entreprise_artiste_auteur)
  - Régime des auteurs et compositeurs lyriques (IRCEC) : 1 source(s) (mon_entreprise_artiste_auteur)
  - Assurance vieillesse des non-salariés agricoles (MSA) : 1 source(s) (msa_reforme_25_meilleures_annees)
  - et 20 sources sans régime désigné.
- **Les règles sans exemple officiel** : 76.
- **Les régimes hors champ** : 15, chacun avec sa raison dans l'inventaire.

## 4. Ce que ce tableau ne sait pas encore dire

- **L'effet chiffré de chaque limite.** Les registres le disent en mots. Le pilote le mesurera, en neutralisant la règle sur les cas types pondérés.
- **La part des pensions qui ne passent que par des règles conformes.** Il faut pour cela que chaque ligne du relevé cite sa fiche, ce que l'architecture prévoit aux phases 4 et 5.
- **Ce que personne n'a encore noté.** Le dénominateur est aujourd'hui la mémoire des registres ; la liste de contrôle des textes (phase 2) en fera la loi elle-même.
- **La réorganisation.** Les règles du code qui ont leur fiche, et les registres devenus des vues, se compteront quand la carte existera (phase 2).
- **Les limites propres à une simulation.** Le site les montrera avec chaque résultat.
- **Le coût du travail** se relève sur l'historique git, et change à chaque commit : il s'affiche à la demande, par `python scripts/tableau_de_bord.py --cout`.
