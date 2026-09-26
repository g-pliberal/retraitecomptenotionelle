# État du dépôt

*Le tableau de bord (`docs/architecture.md`, § 9.1). Fabriqué par `scripts/tableau_de_bord.py` depuis la carte des règles, la liste de contrôle des textes et les registres qui ne sont pas encore des vues : aucun nombre n'y est écrit à la main. Pour le corriger, on corrige la fiche ou le registre, puis on relance le script ; un test refuse une copie périmée.*

## 1. Où en est-on

**Les régimes.** L'inventaire en compte 91 : 35 modélisés, 39 partiels, 15 hors champ, 2 routages.

Pesés par leurs retraités de droit direct (2024, enquête EACR de la DREES, où un polypensionné compte dans chacune de ses caisses) :

| Couverture | Retraités-caisses | Part |
|---|---|---|
| régime modélisé | 35 097 125 | 88 % |
| régime partiel | 4 268 431 | 11 % |
| sections libérales, couverture mêlée | 424 386 | 1 % |

*Modélisé ne veut pas dire exact* : les 25 règles approchées de la carte touchent aussi des régimes modélisés (section 2).

**La carte des règles** (`data/reference/regles/`) : 98 fiches, dont 1 relation. La veille en est une vue (`python scripts/veille_droit.py`).

| État | Fiches |
|---|---|
| conformes | 43 |
| transcrites | 21 |
| approchées | 25 |
| pas encore modélisées | 5 |
| manquantes | 3 |
| à vérifier | 1 |

- Confrontées à au moins un exemple officiel : **22 sur 98** (54 exemples : 54 reproduits, aucun en écart connu).
- Citées dans le code par leur identifiant : **16 sur 98**. Le lien entre une règle et le code qui l'applique n'existe pas encore pour les autres.
- Mûres, sans rien qui manque à leur contrat : **0 sur 98**. Une fiche tirée d'un registre ne sait pas encore son domaine, ses régimes, son étape ni ses versions : ce qui lui manque est à faire (section 3).
- Découpées en versions : **aucune sur 98** ; le partage des versions, qui se contrôle sur chaque fiche, n'a encore rien à contrôler.
- Réformes du calendrier : 109, dont 11 déclarées non appliquées.

**La loi, rédaction par rédaction** (`data/reference/textes/`, § 6.6) : 10 738 rédactions d'articles, de 33 textes, lues le 2026-09-26 (index LEGI du dépôt : Freemium_legi_global_20250713-140000.tar.gz, incréments appliqués jusqu'au 20260925-214830). C'est le dénominateur de l'avancement : ce que les fiches ont lu, contre ce que la loi a écrit.

| Statut | Rédactions |
|---|---|
| rattachées à une version | 0 |
| sans effet | 0 |
| à rattacher | 189 |
| à examiner | 0 |
| sans statut | 10 549 |

**La personne** (§ 5) : une chronologie de faits datés, dans un réseau de personnes — aujourd'hui l'assuré et ses enfants —, que le relevé et le parcours déclarent (`src/retraite_notionnelle/chronologie.py`, et son jumeau). La carrière que le moteur liquide en est la vue. Ce que la saisie ne dit pas est présumé : 7 présomptions au vocabulaire, dont 1 pose son fait dans la chronologie ; les autres s'appliquent dans le code, jusqu'à l'étape qui posera le leur.

| Présomption | Valeur | Fiches qui la lisent | Où elle s'applique |
|---|---|---|---|
| `naissance_des_enfants` | 30 ans | `majoration_duree_assurance_enfants`, `priorite_majorations_enfants` | posée par la chronologie |
| `radiation_au_1er_janvier_suivant` | le 1er janvier qui suit la dernière année de services, ou le départ s'il part en fonctions | `pension_differee_fonction_publique`, `priorite_majorations_enfants`, `retablissement_fonction_publique` | droit_a_pension (droit/coordonner.py), et la revalorisation de la pension différée (scenarios/actuel.py) ; leurs jumeaux JavaScript ; son fait entrera à l'étape `coordonner_les_affiliations` |
| `agent_en_activite` | en activité, avec services effectifs | `services_et_duree_fonction_publique` | _ligne_annuelle, qui fait de toute année d'emploi une année de services (carriere.py, carriere.js) ; son fait entrera à l'étape `compter_les_durees` |
| `pas_d_accord_des_parents` | aucun accord ; le défaut légal les donne à la mère | `majoration_duree_assurance_enfants` | la colonne beneficiaire de majoration_duree_assurance.csv, lue par MajorationsPourEnfants.par_enfant ; son fait entrera à l'étape `compter_les_durees` |
| `enfant_eleve_neuf_ans` | élevé neuf ans | `majoration_duree_assurance_enfants` | les lignes mda de majoration_duree_assurance.csv, qui servent la majoration sans condition de durée d'éducation ; son fait entrera à l'étape `compter_les_durees` |
| `interruption_d_activite_par_la_mere` | remplie par la mère seule | `majoration_duree_assurance_enfants` | la colonne beneficiaire (mere) des lignes bonifications de majoration_duree_assurance.csv, lue par MajorationsPourEnfants.par_enfant ; son fait entrera à l'étape `compter_les_durees` |
| `validation_ircantec_demandee` | demandée | `retablissement_fonction_publique` | retablir (droit/coordonner.py), et l'assiette de l'Ircantec des années rétablies (droit/acquerir.py) ; leurs jumeaux JavaScript ; son fait entrera à l'étape `coordonner_les_affiliations` |

**La réorganisation** (§ 6.5, § 11). Les registres devenus des vues de la carte : la veille. Restent des registres : la frontière contributive, l'inventaire des régimes.

**Ce qui est hors du modèle.** La réversion, par exemple, pèse 10,4 % de la masse des prestations en 2024 (COR), et le modèle n'en calcule aucune.

**La feuille de route** compte 131 actions : 123 fait, 6 en cours, 1 archivée, 1 abandonnée. Les closes sont dans son archive, `docs/archives/feuille_de_route.md` ; ce qui reste à faire est ailleurs, dispersé.

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

**Les règles approchées, absentes ou à vérifier**, avec ce que leur fiche dit de leur effet :

| Règle | État | Qui est touché |
|---|---|---|
| `majoration_enfants_plafond_fonction_publique` | manquante | Ne mord qu'à partir de sept enfants au taux de 80 %, ou de six avec une surcote que la caisse excepte : quelques familles, que le modèle ma… |
| `rci_seuil_premiere_tranche` | manquante | Artisans et commerçants au-dessus du seuil, de 2014 à 2024 : la fiche coupe la première tranche au plafond de chaque année (46 368 € en 202… |
| `temps_partiel_fonction_publique` | manquante | Tout fonctionnaire qui a travaillé à temps partiel sans surcotiser : le modèle compte chaque année à temps plein, aucune saisie ne portant… |
| `cumul_emploi_retraite_et_retraite_progressive` | pas_encore_modelisee | Le modèle liquide une fois, à une date |
| `inaptitude_invalidite_penibilite_amiante` | pas_encore_modelisee | Assurés concernés déclarés non ouverts ou décotés à tort. |
| `rachats_et_versements` | pas_encore_modelisee | Non saisissables dans le simulateur. |
| `retraite_anticipee_handicap` | pas_encore_modelisee | Demande une information médicale que le modèle ne collecte pas : l'assuré est déclaré non ouvert. |
| `reversion` | pas_encore_modelisee | Le modèle décrit une carrière, pas un ménage. |
| `fin_de_la_suspension_2028` | a_verifier | Tout changement de calendrier touche les générations 1965 et suivantes. |
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
| `cultes_salaire_annuel_moyen` | approchee | Le salaire annuel moyen est désormais fait du forfait de chaque année, dans les deux moteurs (`_assiette_de_reference`) : le ministre décla… |
| `date_effet_mois_suivant` | approchee | Le modèle liquide au mois de l'anniversaire : un mois d'écart, visible là où un texte coupe au mois (nés en décembre 1965, carrière longue). |
| `decote_crpn` | approchee | L'âge d'annulation passe de 65 à 60 ans pour toute liquidation depuis 2012, et la décote se compte sur la durée seule depuis 2022. |
| `majoration_duree_assurance_enfants` | approchee | Le modèle sert d'un coup les huit trimestres par enfant que le décret de 2003 attribue un par un, de la naissance au septième anniversaire. |
| `majoration_enfants_liberaux_avocats` | approchee | Les fiches de la CNAVPL, de la CNBF et de sa complémentaire ne la portaient pas : 10 % de pension en moins pour tout parent de trois enfant… |
| `marins_salaire_de_reference` | approchee | Le modèle prend la catégorie de la DERNIÈRE année, rangée par le revenu, et compte les services au trimestre |
| `minimum_vieillesse` | approchee | Les plus petites pensions |
| `minoration_ircec` | approchee | Tout départ anticipé d'un artiste-auteur, d'un auteur dramatique ou d'un compositeur qui n'a pas sa durée : à soixante-deux ans, 20 % de mi… |
| `pension_mines` | approchee | Mineurs. |
| `raap_classe_speciale` | approchee | La fiche prélevait 8 % du revenu avant 2016 — un taux qu'aucun texte ne porte — et servait donc, à un revenu moyen, quatre à six fois les p… |
| `rafp_majoration_capital` | approchee | Le modèle servait la valeur de service nue à tout âge : 22 % de moins à 67 ans. |
| `sections_liberales_majoration_enfants` | approchee | Aucune des trois fiches ne la portait : 10 % de complémentaire en moins pour tout parent de trois enfants. |
| `un_statut_par_annee` | approchee | DEPUIS LE 22 SEPTEMBRE 2026, DEUX ACTIVITÉS À LA FOIS se décrivent, dans les deux moteurs : chacune verse à son régime, sur son revenu, et… |

**Un état peut-être périmé.** Pour 17 des 25 règles approchées, l'effet raconte à l'imparfait l'erreur qui a été corrigée, sans dire ce qui reste. Le tableau ne peut pas savoir si elles sont encore approchées : leur fiche le dira quand elle mûrira, l'écart actuel dans ses approximations, le récit dans son historique.

**Des approximations non déclarées.** Aucune des 25 fiches approchées ne déclare encore ses approximations, chacune avec son effet ou « non mesuré » : l'effet n'en est dit qu'en mots.

**Aucun exemple officiel en écart connu** : le modèle reproduit tous ceux que le dépôt a transcrits. Un exemple qu'il ne reproduirait pas entrerait quand même, et se lirait ici.

## 3. Ce qui reste à faire, et par quoi commencer

- **Les 6 actions en cours** de la feuille de route :
  - 47. La garantie vieillesse est une avance : la reprise sur succession, sa règle et son chiffrage
  - 89. Dépouiller les 260 sources officielles remises le 22 septembre 2026
  - 119. Les complémentaires relues : le plafond du RAFP, les points gratuits de la RCO, l'Arrco des cultes, et trois trous que rien ne disait
  - 121. Le droit de chacun, et non celui de la génération de l'année : toutes les personnes vivantes
  - 129. Le taux de l'État ramené à sa part « retraite seule » : un réglage, puis le défaut
  - 130. L'architecture du dépôt : décidée, les phases 0 à 3 faites, la phase 4 à lancer
- **Les sources à exploiter** : 114 à explorer sur 260 (58 explorées, 88 épuisées). 9 d'entre elles visent un régime partiel, et pourraient le compléter :
  - Association des régimes de retraite complémentaire des salariés : 3 source(s) (agirc_arrco_majorations_enfants, agirc_arrco_textes_de_reference, agirc_arrco_parametres_statistiques)
  - Caisse de retraite et de prévoyance des clercs et employés de notaires : 2 source(s) (crpcen_montant_pension, crpcen_rachat_etudes)
  - Régime des artistes-auteurs professionnels (IRCEC) : 2 source(s) (cnav_arrierees_artiste_auteur, mon_entreprise_artiste_auteur)
  - Caisse nationale d'assurance vieillesse des professions libérales, régime de base : 1 source(s) (mon_entreprise_comparaison_ei)
  - Régime des auteurs et compositeurs dramatiques (IRCEC) : 1 source(s) (mon_entreprise_artiste_auteur)
  - Régime des auteurs et compositeurs lyriques (IRCEC) : 1 source(s) (mon_entreprise_artiste_auteur)
  - Assurance vieillesse des non-salariés agricoles (MSA) : 1 source(s) (msa_reforme_25_meilleures_annees)
  - et 20 sources sans régime désigné.
- **Les fiches sans exemple officiel** : 76.
- **Faire mûrir la carte** : 805 champs obligatoires manquent, à 98 fiches. Par champ :

  | Champ | Fiches à qui il manque |
  |---|---|
  | `dates_qui_decident` | 98 |
  | `domaine` | 98 |
  | `ecrit` | 98 |
  | `etape` | 98 |
  | `lit` | 98 |
  | `regimes` | 98 |
  | `versions` | 98 |
  | `code` | 93 |
  | `approximations` | 25 |
  | `rang` | 1 |

- **Les textes** : 189 rédactions à rattacher à une version de la fiche qui les cite, 0 à examiner, et 10 549 sans statut, que le cliquet tient à 10 549 au plus. Les textes qui en ont le plus : `css` 5 367, `rural` 1 000, `decret_46_2769` 946, `cpcmr` 696, `decret_90_1215` 350 (`python scripts/textes.py`).
- **Les relectures prévues les plus proches** : 2026-11-30 (`majoration_dix_pour_cent`) ; 2026-12-31 (`age_legal_par_generation`) ; 2026-12-31 (`carriere_longue`) ; 2026-12-31 (`certification_legi_perimee`) ; 2026-12-31 (`duree_requise_par_generation`).
- **Les régimes hors champ** : 15, chacun avec sa raison dans l'inventaire.

## 4. Ce que ce tableau ne sait pas encore dire

- **L'effet chiffré de chaque limite.** Les fiches le disent en mots. Le pilote le mesurera, en neutralisant la règle sur les cas types pondérés.
- **La part des pensions qui ne passent que par des règles conformes.** Il faut pour cela que chaque ligne du relevé cite sa fiche, ce que l'architecture prévoit aux phases 4 et 5.
- **Ce que personne n'a encore noté, hors des articles.** Pour les articles, le dénominateur est la loi (section 1). Les situations des fiches service-public et des circulaires, les accords Agirc-Arrco et les statuts des caisses n'ont pas encore de liste.
- **Les règles du code qui ont leur fiche.** Une fiche dira son code ; aucune ne le dit encore, et le tableau compte en attendant les identifiants que le code cite.
- **Les limites propres à une simulation.** Le site les montrera avec chaque résultat, et les présomptions qu'elle emploie : la chronologie les liste, le site ne les affiche pas encore.
- **Le coût du travail** se relève sur l'historique git, et change à chaque commit : il s'affiche à la demande, par `python scripts/tableau_de_bord.py --cout`, avec la taille du dépôt — ses lignes, ses tests —, que la prose ne porte plus.
