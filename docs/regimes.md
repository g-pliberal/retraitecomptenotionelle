# Les régimes de retraite français, tous — et ce que le dépôt en calcule

**Le fichier qui fait foi est [`data/reference/regimes/inventaire.yaml`](../data/reference/regimes/inventaire.yaml).**
Ce document en est la lecture commentée — ses tableaux et sa phrase de compte
sont produits par `python scripts/construire_regimes_md.py`, et un test refuse
qu'ils vieillissent ; la page **Données** du site l'affiche
telle qu'elle est, et `tests/test_donnees.py` le tient aligné sur le catalogue :
une fiche de régime sans ligne d'inventaire, ou une ligne qui prétend calculer
ce qu'aucune fiche ne calcule, fait échouer les tests.

Pourquoi ce fichier existe : `docs/limites.md` disait que la liste des régimes
manquants « n'est pas dérivée d'un fichier, et c'est une limite en soi — un
régime peut manquer à la liste des manquants ». L'objectif du dépôt est un
simulateur juste pour tout le monde, quel que soit l'âge : il faut d'abord
savoir de quels régimes on parle, puis, pour chacun, quelles règles il a
appliquées à travers son histoire. Ce document fait la première moitié ; la
seconde est l'étape suivante, esquissée en fin de page.

<!-- compte:debut -->
L'inventaire compte **91 lignes** : 35 régimes modélisés,
39 calculés mais incomplets, 2 affiliations portées par un statut,
15 hors champ — et plus aucune ligne à modéliser.
<!-- compte:fin -->

| Couverture | Ce que cela veut dire |
|---|---|
| ✅ modélisé | une fiche du catalogue, sur toute l'histoire connue du régime |
| ◐ partiel | une fiche calculée, mais un étage, un barème ou une période manque — la colonne dit lequel |
| ✚ à modéliser | aucune fiche ; la colonne dit ce qui bloque |
| ↪ portée par un statut | pas un régime mais une affiliation (l'élu local, le micro-social), routée par un statut du catalogue ; la colonne dit ce que le statut ne lit pas |
| ⊘ hors champ | ne sera pas modélisé ; la colonne dit pourquoi |

**D'où vient la liste.** Elle est ancrée sur les textes qui énumèrent les
régimes, lus dans l'index LEGI du dépôt : l'article `R. 711-1` du code de la
sécurité sociale (les régimes spéciaux, dans sa rédaction du 1<sup>er</sup>
septembre 2023), `D. 643-1` (les sections des professions libérales),
`L. 921-1` et `L. 921-4` (les complémentaires obligatoires), et le programme
195 des lois de finances, « Régimes de retraite des mines, de la SEITA et
divers », qui nomme les régimes fermés que l'État finance. Chaque ligne du
fichier cite son texte fondateur et, quand l'index le porte, son identifiant
DILA ; les textes d'avant 1947 et les règlements hors Journal officiel n'en
ont pas, voir « Ce que JORF et LEGI ne contiennent pas » dans
[`limites.md`](limites.md).

**Deux décisions, prises et non déduites.** Les régimes d'outre-mer — Mayotte,
Saint-Pierre-et-Miquelon, Polynésie française, Nouvelle-Calédonie,
Wallis-et-Futuna — et ceux des assemblées — députés, sénateurs, personnels des
assemblées, membres du CESE — sont marqués « à modéliser », non « hors champ »,
même là où leurs textes échappent au Journal officiel. Restent hors champ les
régimes antérieurs à 1930 sans assuré vivant, les adhésions facultatives, les
prestations sans cotisation, et les régimes éteints dont les droits ont été
repris par un autre.


<!-- tableaux:debut -->
## Salariés du privé — régimes de base

| Régime | Famille | Période | Couverture | Statuts | Ce qui manque, ou pourquoi |
|---|---|---|---|---|---|
| Retraites ouvrières et paysannes | base, privé | 1911-1930 | ⊘ hors champ | — | Régime en capitalisation, antérieur à 1930, l'année où le modèle commence : aucun assuré vivant n'y a cotisé, et le texte n'est pas dans le dump de la DILA, qui commence en 1947. |
| Assurances sociales (assurance vieillesse) (`assurances_sociales`) | base, privé | 1930-1945 | ✅ modélisé | `salarie_prive_non_cadre`, `salarie_prive_cadre`, `salarie_agricole`, `salarie_prive_cadre_entreprise_recente`, `salarie_prive_non_cadre_entreprise_recente`, `salarie_regime_professionnel_integre` |  |
| Régime local d'assurance invalidité-vieillesse d'Alsace-Moselle | base, privé | 1919-1946 | ⊘ hors champ | — | Législation allemande de 1889 et 1911 maintenue après 1918, fondue dans le régime général en 1946 : les droits acquis sous ce régime sont liquidés par le régime général selon les décrets de 1974 à 1977. Aucun assuré vivant n'y a cotisé assez longtemps pour que ses règles pèsent. |
| Allocation aux vieux travailleurs salariés (`avts`) | base, privé | 1941-1945 | ✅ modélisé | — |  |
| Régime général de la Sécurité sociale (Cnav) (`regime_general`) | base, privé | depuis 1945 | ✅ modélisé | `salarie_prive_non_cadre`, `salarie_prive_cadre`, `contractuel_public`, `artisan`, `commercant`, `artiste_auteur`, `personnel_navigant`, `agent_sncf`, `agent_ratp`, `agent_ieg`, `mineur`, `clerc_de_notaire`, `agent_banque_de_france`, `agent_seita`, `agent_chemins_fer_secondaires`, `salarie_prive_cadre_entreprise_recente`, `salarie_prive_non_cadre_entreprise_recente`, `maitre_enseignement_prive`, `elu_local`, `auteur_dramatique`, `auteur_lyrique`, `gerant_debit_tabac`, `micro_entrepreneur`, `membre_cese`, `salarie_regime_professionnel_integre`, `liberal_non_reglemente` |  |
| Assurances sociales agricoles, salariés (MSA) (`msa_salaries`) | agricole | depuis 1930 | ✅ modélisé | `salarie_agricole` |  |
| Régime de retraite des salariés de Mayotte (Caisse de sécurité sociale de Mayotte) (`cssm_mayotte`) | base, privé | depuis 1987 | ◐ partiel | `salarie_mayotte` | Le SMIG mahorais, qui valide les trimestres (200 puis 150 heures par trimestre), n'est pas une série du dépôt : la validation se fait au SMIC national. Taux et plafond de la caisse de sécurité sociale de Mayotte, en convergence jusqu'en 2036, remplacés par ceux du régime général. Salaire de référence supposé sur vingt-cinq ans dès 2003. Les non-salariés de Mayotte, affiliés à la même caisse depuis 2012 avec une pension calculée selon les mêmes règles (article 23-4), n'ont aucun statut qui les y route : seul `salarie_mayotte` atteint la fiche, et le chapitre III du décret n° 2003-589, écrit en 2012 pour adapter leur revenu annuel moyen, n'est pas lu. |
| Régime de retraite de la Caisse de prévoyance sociale de Saint-Pierre-et-Miquelon (`cps_saint_pierre_et_miquelon`) | base, privé | depuis 1987 | ◐ partiel | `salarie_saint_pierre_et_miquelon` | Taux de cotisation et plafond de la caisse de prévoyance sociale, fixés localement et absents de l'index : ceux du régime général tiennent lieu. Le régime d'avant août 1987 (ordonnance n° 77-1102) n'est pas porté. La table par génération est lue en dur, année par année, faute d'un drapeau qui la décale de sept ans. |
| Régime de retraite des travailleurs salariés de Polynésie française (CPS) (`cps_polynesie`) | base, privé | depuis 1968 | ◐ partiel | `salarie_polynesie` | Seuls les paramètres de 2026 sont lus, projetés sur toute la période ; le plafond de 269 000 FCFP par mois n'est pas une série du dépôt et le plafond national, plus haut, tient lieu ; la montée en charge de la réforme de 2023 n'est pas lue. |
| Régime de retraite des travailleurs salariés de Polynésie française, tranche B (CPS) (`cps_polynesie_tranche_b`) | base, privé | depuis 1995 | ◐ partiel | `salarie_polynesie` | La tranche 269 000-525 000 FCFP est écrite comme la tranche entre un et deux plafonds nationaux, la borne la plus proche du catalogue ; le barème de 2026 est projeté sur toute la période, depuis la délibération de 1995 qui institue la tranche. |
| Régime de retraite des travailleurs salariés de Nouvelle-Calédonie (CAFAT) (`cafat_nouvelle_caledonie`) | base, privé | depuis 1958 | ◐ partiel | `salarie_nouvelle_caledonie` | La valeur de référence qui convertit les cotisations en points n'est pas publiée : le rendement est estimé ; taux et barème de 2026 projetés sur toute la période ; plafond de 548 600 FCFP remplacé par le plafond national. Les salariés du privé de Nouvelle-Calédonie relèvent aussi, obligatoirement, de l'Agirc-Arrco depuis l'accord territorial de 1994, étendu en 1995 et généralisé au 1er janvier 1995 avec validation des services passés : le statut `salarie_nouvelle_caledonie` ne route pas vers la complémentaire. |
| Retraite des salariés de Wallis-et-Futuna (`wallis_et_futuna`) | base, privé | depuis 1975 | ◐ partiel | `salarie_wallis_et_futuna` | Le régime existe bel et bien, contrairement à ce que l'inventaire disait : 60 ans, quinze ans de cotisation, 2,6 % puis 1,3 % par an sur les quinze meilleures années. Non lus : le plafond, la date de création, le barème d'avant 2009, la réforme en préparation (65 ans). |

## Salariés du privé — complémentaires

| Régime | Famille | Période | Couverture | Statuts | Ce qui manque, ou pourquoi |
|---|---|---|---|---|---|
| Association générale des institutions de retraite des cadres (`agirc`) | complémentaire, privé | 1947-2018 | ✅ modélisé | `salarie_prive_cadre`, `personnel_navigant`, `salarie_prive_cadre_entreprise_recente` |  |
| Union nationale des institutions de retraite des salariés (`unirs`) | complémentaire, privé | 1957-1962 | ◐ partiel | `salarie_prive_non_cadre`, `salarie_prive_non_cadre_entreprise_recente`, `maitre_enseignement_prive`, `agent_chemins_fer_secondaires` | L'UNIRS tient lieu de toutes les institutions fédérées avant 1961 — CRI, CIRCC, CGRCR, IRPSIMMEC, CAPIMMEC et les autres —, dont aucune n'a de fiche propre : chacune avait son barème, et le dépôt n'en connaît qu'un ; et ce barème n'est chiffré nulle part dans l'index (deux occurrences du nom avant 1975, sans taux) : 2,5 % par continuité avec l'Arrco de 1962. |
| Association des régimes de retraite complémentaire des salariés (`arrco`) | complémentaire, privé | 1961-2018 | ◐ partiel | `salarie_prive_non_cadre`, `salarie_prive_cadre`, `salarie_agricole`, `personnel_navigant`, `mineur`, `agent_seita`, `agent_chemins_fer_secondaires`, `salarie_prive_cadre_entreprise_recente`, `salarie_prive_non_cadre_entreprise_recente`, `maitre_enseignement_prive`, `salarie_saint_pierre_et_miquelon`, `salarie_nouvelle_caledonie`, `salarie_regime_professionnel_integre` | Routée à tous les salariés dès 1961, alors que l'affiliation n'est obligatoire pour tous que depuis la loi du 29 décembre 1972 : entre 1961 et 1972 le modèle prête une complémentaire à qui n'en avait pas. |
| Arrco, tranche 2 des non-cadres (`arrco_tranche_2`) | complémentaire, privé | 1961-2018 | ✅ modélisé | `salarie_prive_non_cadre`, `salarie_agricole`, `mineur`, `agent_seita`, `agent_chemins_fer_secondaires`, `maitre_enseignement_prive`, `salarie_saint_pierre_et_miquelon`, `salarie_nouvelle_caledonie`, `salarie_regime_professionnel_integre` |  |
| Retraite complémentaire obligatoire des cultes (Arrco, puis Agirc-Arrco) (`arrco_cultes`) | complémentaire, privé | depuis 2006 | ◐ partiel | `ministre_du_culte` | Le taux de base seul : les huit taux spécifiques de la CAVIMAC, de 11,13 à 21,31 %, ne sont pas portés ; avant 2019, le taux est celui de la tranche 1 de l'Arrco, aucune circulaire antérieure à novembre 2021 n'étant lisible. |
| Agirc, barème des entreprises créées après 1981 (`agirc_entreprises_nouvelles`) | complémentaire, privé | 1981-2018 | ✅ modélisé | `salarie_prive_cadre_entreprise_recente` |  |
| Arrco, tranche 2 des entreprises créées après 1997 (`arrco_tranche_2_entreprises_nouvelles`) | complémentaire, privé | 1997-2018 | ✅ modélisé | `salarie_prive_non_cadre_entreprise_recente` |  |
| Régime unifié Agirc-Arrco (`agirc_arrco`) | complémentaire, privé | depuis 2019 | ✅ modélisé | `salarie_prive_non_cadre`, `salarie_prive_cadre`, `salarie_agricole`, `personnel_navigant`, `agent_sncf`, `agent_ratp`, `agent_ieg`, `mineur`, `clerc_de_notaire`, `agent_banque_de_france`, `agent_seita`, `agent_chemins_fer_secondaires`, `salarie_prive_cadre_entreprise_recente`, `salarie_prive_non_cadre_entreprise_recente`, `maitre_enseignement_prive`, `salarie_saint_pierre_et_miquelon`, `membre_cese`, `salarie_nouvelle_caledonie`, `salarie_regime_professionnel_integre` |  |
| Institution de prévoyance des agents contractuels et temporaires de l'État (`ipacte`) | complémentaire, privé | 1951-1971 | ◐ partiel | `contractuel_public` | Le taux (4,25 % et 8,25 %) est lu dans l'article 7, mais dans une version consolidée unique, et le taux d'appel est celui de l'Ircantec de 1971 prolongé en arrière ; l'âge de liquidation n'est écrit nulle part dans l'index (article 5 absent de LEGI) et prend le barème du successeur. |
| Institution générale de retraite des agents non titulaires de l'État (`igrante`) | complémentaire, privé | 1960-1971 | ◐ partiel | `contractuel_public` | Le taux (1,40 % et 2,10 %) est lu dans l'article 2, version consolidée unique, l'appel est prolongé de l'Ircantec et l'âge prend le barème du successeur (article 5 bis absent de LEGI) ; et la fiche ne porte que la tranche sous le plafond, celle de l'agent qui relève aussi de l'IPACTE — les autres non-titulaires cotisaient jusqu'à trois plafonds, part qu'aucun statut ne distingue. |
| Institution de retraite complémentaire des agents non titulaires de l'État et des collectivités publiques (`ircantec`) | complémentaire, privé | depuis 1971 | ✅ modélisé | `contractuel_public`, `elu_local` |  |
| Affiliation des élus locaux à l'Ircantec | complémentaire, privé | depuis 1973 | ↪ portée par un statut | `elu_local` | Le statut `elu_local` route l'Ircantec depuis 1973 et, depuis 2013, le régime général au-dessus de la moitié du plafond, le seuil de L. 382-31 étant lu année par année sur l'indemnité. Non portés : l'élu qui a cessé toute activité professionnelle, assujetti même sous le seuil ; les régimes de retraite par rente (FONPEL, CAREL), facultatifs. |
| Caisse de retraite du personnel navigant professionnel de l'aéronautique civile, tranche 1 (`crpnpac`) | spécial | depuis 1963 | ◐ partiel | `personnel_navigant` | Le taux d'appel de 1995 à 2011 n'est pas appliqué, ceux de 2016 à 2025 ne sont pas publiés (105 % retenu, 111 % en 2026) ; le dispositif transitoire des navigants nés avant 1971 et les conditions montantes de 2012 à 2021 ne sont pas portés. |
| Caisse de retraite du personnel navigant, tranche 2 (`crpnpac_tranche_2`) | spécial | depuis 1963 | ◐ partiel | `personnel_navigant` | Mêmes limites que la tranche 1 : taux d'appel de 2016 à 2025 non publiés, dispositif transitoire et conditions de 2012 à 2021 non portés. |
| Régime des artistes-auteurs professionnels (IRCEC) (`ircec_raap`) | libéral | depuis 1962 | ◐ partiel | `artiste_auteur`, `auteur_dramatique`, `auteur_lyrique` | De 1981 à 2015 la cotisation est la classe spéciale d'office, six points par an au montant du décret de l'exercice ; les musiciens étaient en classe A d'office jusqu'en 2004, et la forme d'avant 1981 n'est pas connue (8 %). Le seuil d'affiliation de 900 SMIC horaires n'est pas appliqué, ni le minimum de trente points. La minoration de l'IRCEC est lue depuis 2014 ; avant, et pour les générations nées avant 1955 jusqu'en 2024, elle est approchée (voir `docs/limites.md`). |
| RAAP au taux aménagé des auteurs affiliés au RACD ou au RACL (IRCEC) (`ircec_raap_taux_amenage`) | libéral | depuis 2016 | ◐ partiel | `auteur_dramatique`, `auteur_lyrique` | Un barème du RAAP, non un régime : la moitié du taux pour qui cotise au RACD ou au RACL, dont les points sont ceux du RAAP. Il en partage les manques — seuil d'affiliation de 900 SMIC horaires et minimum de trente points non appliqués. |
| Régime des auteurs et compositeurs dramatiques (IRCEC) (`ircec_racd`) | libéral | depuis 1964 | ◐ partiel | `auteur_dramatique` | Le barème du point est celui du seul mémo 2026 de l'IRCEC, appliqué en rendement à toute la carrière ; le plafond de 597 500 € est arrondi à treize plafonds de la Sécurité sociale. La minoration de l'IRCEC est lue depuis 2014 ; avant, et pour les générations nées avant 1955 jusqu'en 2024, elle est approchée (voir `docs/limites.md`). |
| Régime des auteurs et compositeurs lyriques (IRCEC) (`ircec_racl`) | libéral | depuis 1962 | ◐ partiel | `auteur_lyrique` | Le taux de 6,5 % et le barème du point viennent du seul mémo 2026 de l'IRCEC, appliqués à toute la carrière ; le seuil d'affiliation (3 170 €) est ignoré et le plafond de 435 938 € arrondi à huit plafonds de la Sécurité sociale. La minoration de l'IRCEC est lue depuis 2014 ; avant, et pour les générations nées avant 1955 jusqu'en 2024, elle est approchée (voir `docs/limites.md`). |
| Régimes professionnels de salariés intégrés à l'Agirc-Arrco (`regimes_professionnels_integres`) | complémentaire, privé | depuis 1947, fermé en 1993 | ◐ partiel | `salarie_regime_professionnel_integre` | La fiche porte le barème bancaire pour toutes les populations : le complément de 35 % du dernier salaire en 42 ans, la Sécurité sociale déduite, et 16 % de cotisation ; les barèmes propres de la CPPOSS, de la CGRCE, des CCI, de l'IRREP, de la CAMARCA et du personnel au sol d'Air France (règlement de 1956, régime différentiel de 1993), le complément différentiel de 1994 et son rabot, et l'Agirc du cadre bancaire ne le sont pas. |
| Régime additionnel de retraite des enseignants du privé sous contrat (`enseignants_prive_additionnel`) | spécial | depuis 2005 | ✅ modélisé | `maitre_enseignement_prive` |  |

## Fonction publique et assimilés

| Régime | Famille | Période | Couverture | Statuts | Ce qui manque, ou pourquoi |
|---|---|---|---|---|---|
| Pensions civiles et militaires, loi de 1853 (`pensions_civiles_1853`) | fonction publique | 1853-1948 | ✅ modélisé | `fonctionnaire_etat`, `fonctionnaire_etat_actif`, `fonctionnaire_etat_super_actif`, `militaire`, `militaire_officier` |  |
| Pensions civiles et militaires de retraite (Service des retraites de l'État) (`fonction_publique_etat`) | fonction publique | depuis 1948 | ◐ partiel | `fonctionnaire_etat`, `fonctionnaire_etat_actif`, `fonctionnaire_etat_super_actif`, `militaire`, `militaire_officier` | Les bonifications de SERVICE — dépaysement, campagne, cinquième — ne sont pas servies, faute de connaître le corps et le détail des services ; la radiation par limite d'âge de grade, qui ouvre la pension militaire quelle que soit la durée accomplie, ne l'est pas non plus, le grade n'étant pas saisi. Les fonctionnaires de La Poste et d'Orange ont la même pension mais une contribution employeur propre depuis 2006, non distinguée. Le temps partiel ne compte qu'à sa quotité dans les services, et le modèle, qui ne la saisit pas, le compte à temps plein ; ni le rachat d'études ni la surcotisation ne sont servis ; le plafond du dernier traitement de la majoration pour enfants (L. 18, V) et l'écrêtement du minimum garanti par le total des pensions ne sont pas appliqués. |
| Caisse nationale de retraites des agents des collectivités locales (`cnracl`) | fonction publique | depuis 1945 | ✅ modélisé | `fonctionnaire_territorial_hospitalier`, `fonctionnaire_territorial_hospitalier_actif`, `fonctionnaire_territorial_hospitalier_super_actif` |  |
| Caisses communales de retraite et Caisse intercommunale de retraites | fonction publique | 1930-1945 | ⊘ hors champ | — | Fondues dans la CNRACL en 1945, qui a repris leurs droits ; le statut territorial route vers la CNRACL dès 1945 et personne de vivant n'a liquidé sous une caisse communale. |
| Fonds spécial des pensions des ouvriers des établissements industriels de l'État (`fspoeie`) | fonction publique | depuis 1928 | ✅ modélisé | `ouvrier_etat`, `ouvrier_etat_actif` |  |
| Retraite additionnelle de la fonction publique (`rafp`) | additionnel, capitalisé | depuis 2005 | ✅ modélisé | `fonctionnaire_etat`, `fonctionnaire_etat_actif`, `fonctionnaire_etat_super_actif`, `fonctionnaire_territorial_hospitalier`, `fonctionnaire_territorial_hospitalier_actif`, `fonctionnaire_territorial_hospitalier_super_actif`, `militaire`, `militaire_officier`, `ouvrier_etat`, `ouvrier_etat_actif` |  |
| Caisses de retraite des anciens députés, des anciens sénateurs et des personnels des assemblées (`assemblees_parlementaires`) | spécial | depuis 1904 | ◐ partiel | `parlementaire` | La fiche est celle des députés, lue dans le règlement de 2018 ; les sénateurs y sont assimilés faute d'un règlement publié, et les fonctionnaires des assemblées restent hors fiche. La part versée par l'Assemblée n'est pas écrite : seule la retenue du député est portée. La retenue d'avant 2015 est estimée. |
| Caisse de retraite des anciens membres du Conseil économique, social et environnemental (`cese_membres`) | spécial | depuis 1957, fermé en 2023 | ◐ partiel | `membre_cese` | La retenue de 3,42 fois celle de la fonction publique est lue, la contribution du Conseil ne l'est pas ; l'assiette de référence de 2,06 fois la rémunération et le plafond des trois quarts sont écrits comme un taux plein de 154,5 % de l'indemnité. |
| Caisse intercoloniale de retraites, puis Caisse de retraites de la France d'outre-mer (CRFOM) | fonction publique | depuis 1924, fermé en 1976 | ⊘ hors champ | — | Régime des cadres coloniaux fermé par la loi de finances pour 1976 : ses derniers actifs ont été affiliés d'office aux pensions civiles et militaires au 1er janvier 1976, et ses pensions sont servies par l'État. Le statut `fonctionnaire_etat` porte la carrière ; le dépôt n'a pas le règlement du décret du 21 avril 1950. |
| Caisse générale des retraites de l'Algérie, Caisse marocaine des retraites et Société de prévoyance des fonctionnaires tunisiens (pensions garanties) | fonction publique | depuis 1903, fermé en 1962 | ⊘ hors champ | — | Régimes des anciens cadres d'Algérie, du Maroc et de Tunisie, fermés aux Français avec l'indépendance et dont l'État garantit les pensions depuis. La caisse des retraites de l'Algérie, créée par la loi de finances du 30 décembre 1903 et organisée par le décret du 16 juillet 1907, a ses décrets de 1907 à 1937 dans l'index ; ses règles d'après 1947, décisions de l'assemblée algérienne homologuées par décret, et les dahirs marocains et tunisiens n'y sont que par leurs homologations et les règles de coordination (services du 1er avril 1938 au 1er juillet 1962). Aucun cotisant depuis 1962. |
| Caisse de retraite des fonctionnaires et agents des collectivités publiques de Mayotte (CRFM) | fonction publique | depuis 1977, fermé en 2010 | ⊘ hors champ | — | Caisse locale créée en mars 1977 par délibération hors Journal officiel, fermée par l'intégration de ses affiliés dans les fonctions publiques d'État, territoriale et hospitalière au plus tard fin 2010, en liquidation depuis : ses pensions sont versées par la CNRACL ou par l'État, la caisse ne préliquidant plus que la part antérieure. Les statuts de fonctionnaire portent la carrière ; le règlement de la caisse n'est pas dans l'index. |
| Régimes de retraite des élus des assemblées de Polynésie française et de Nouvelle-Calédonie | spécial | — | ⊘ hors champ | — | Régimes fixés par les assemblées elles-mêmes, hors Journal officiel de la République. En Polynésie, les représentants ont un régime par capitalisation auprès d'un assureur privé, exclu des comptes notionnels comme toute capitalisation, et les membres du gouvernement ne cotisent au régime de base de la CPS que depuis le 1er juin 2024 ; en Nouvelle-Calédonie, la loi organique confie au congrès et aux assemblées de province le régime de retraite de leurs membres, et le dépôt n'a lu aucune de leurs délibérations. Aucun barème lu. |
| Caisses de retraite des fonctionnaires de Nouvelle-Calédonie et de Polynésie française (`fonctionnaires_pacifique`) | fonction publique | depuis 1959 | ◐ partiel | `fonctionnaire_pacifique` | La fiche est celle de la Caisse locale de retraites de Nouvelle- Calédonie ; les fonctionnaires de Polynésie relèvent de la CPS, portée par le statut salarié. Les cotisations d'avant 2023 sont projetées ; la durée de services requise et la table exacte de l'âge après 2025 restent à lire dans la loi du pays. |

## Régimes spéciaux de salariés

| Régime | Famille | Période | Couverture | Statuts | Ce qui manque, ou pourquoi |
|---|---|---|---|---|---|
| Régime spécial des agents du cadre permanent de la SNCF (`sncf`) | spécial | depuis 1909, fermé en 2020 | ✅ modélisé | `agent_sncf` |  |
| Régime spécial de retraite du personnel de la RATP (`ratp`) | spécial | depuis 1900, fermé en 2023 | ✅ modélisé | `agent_ratp` |  |
| Régime spécial des industries électriques et gazières (CNIEG) (`ieg`) | spécial | depuis 1946, fermé en 2023 | ✅ modélisé | `agent_ieg` |  |
| Régime des marins (ENIM) (`marins`) | spécial | depuis 1673 | ◐ partiel | `marin` | La grille des vingt catégories est lue au Journal officiel depuis 2008 (`salaires_forfaitaires.csv`, arrêtés annuels) et appliquée : le marin est rangé chaque année dans la catégorie dont le forfait approche le plus son revenu annualisé, convention nommée dans la fiche. Avant 2008, les textes de l'index ne portent pas les montants : la grille de 2008 est ramenée par le salaire moyen, au niveau estimé. Les trois âges sont appliqués depuis le 22 septembre 2026 (ancienneté à cinquante ans pour vingt-cinq ans de services, proportionnelle à cinquante-cinq, spéciale avec l'autre pension ou à soixante ans), comme la levée du plafond de vingt-cinq annuités à cinquante-deux ans et demi et la bonification dès deux enfants. Manquent : la catégorie MOYENNE des trente-six derniers mois (R. 11) et le décompte au semestre (R. 12), le taux de 1 % de la petite pêche outre-mer, la pension d'invalidité, la cessation anticipée amiante. |
| Régime spécial de sécurité sociale dans les mines (CANSSM) (`mines`) | spécial | depuis 1894, fermé en 2010 | ✅ modélisé | `mineur` |  |
| Caisse de retraite et de prévoyance des clercs et employés de notaires (`crpcen`) | spécial | depuis 1937, fermé en 2023 | ◐ partiel | `clerc_de_notaire` | Deux âges avant 2008 — soixante ans, ou cinquante-cinq pour l'assurée justifiant de vingt-cinq années de cotisations — et le moteur n'en porte qu'un : la fiche garde le second. Les décrets de taux (1977, 1979, 1986) donnent la cotisation de tous les risques, pas la part vieillesse. |
| Régime spécial de retraite de la Banque de France (`banque_de_france`) | spécial | depuis 1806, fermé en 2023 | ✅ modélisé | `agent_banque_de_france` |  |
| Régime de retraite du personnel de l'Opéra national de Paris (`opera_de_paris`) | spécial | depuis 1698 | ✅ modélisé | `personnel_opera` |  |
| Régime de retraite du personnel de la Comédie-Française (`comedie_francaise`) | spécial | depuis 1812 | ✅ modélisé | `personnel_comedie_francaise` |  |
| Régime de retraite du personnel du port autonome de Strasbourg (`port_strasbourg`) | spécial | depuis 1926 | ◐ partiel | `agent_port_strasbourg` | Le règlement de retraite est un acte de l'établissement, absent de LEGI et du JORF, qui ne portent que le décret constitutif de 1925 (LEGIARTI000021290664), l'affiliation au régime local d'Alsace-Moselle (L. 325-1, LEGIARTI000006742525), la liste des régimes spéciaux de 2014 (JORFARTI000029964983) et des décrets de compensation : un seul jeu de règles pour 1930-2026, au niveau `estimee`. |
| Régime de retraite du personnel de la SEITA (`seita`) | spécial | depuis 1935, fermé en 1981 | ✅ modélisé | `agent_seita` |  |
| Caisse autonome mutuelle de retraites des chemins de fer secondaires et tramways (CAMR) (`chemins_fer_secondaires`) | spécial | depuis 1922, fermé en 1954 | ◐ partiel | `agent_chemins_fer_secondaires` | Une seule période, au niveau `estimee`, depuis le texte fondateur sans recontrôle. |
| Régime des cultes (CAVIMAC) (`cavimac`) | spécial | depuis 1979 | ✅ modélisé | `ministre_du_culte`, `membre_congregation` |  |
| Régime d'allocation viagère des gérants de débits de tabac (RAVGDT) (`gerants_debits_tabac`) | spécial | depuis 1963 | ◐ partiel | `gerant_debit_tabac` | Le revenu saisi tient lieu de remises sur les tabacs, sans le plafond de remises de l'article 6 ; le barème du point (4,94 € d'achat en 2026, 2,42 € de service en 2025) est celui de la Caisse des dépôts, hors index, appliqué en rendement à toute la carrière ; le taux d'avant 1990 est projeté. |
| Caisse des retraites de l'Imprimerie nationale | spécial | 1927-2013 | ⊘ hors champ | — | Régime éteint : les documents budgétaires du programme 195 comptent dix affiliés en 2007 et constatent l'extinction fin 2013 « avec le décès du dernier pensionné » ; aucun assuré vivant n'y a de droit, il n'y a rien à simuler. |
| Régime spécial de retraite du Crédit foncier de France | spécial | 1930-1988 | ⊘ hors champ | — | Transféré au régime général au 1er janvier 1989, pensions et cotisants compris : les droits acquis sont servis par le régime général et le dépôt n'a pas de source pour le barème d'avant. |
| Régime de retraite des personnels de l'ORTF | spécial | depuis 1964, fermé en 1975 | ⊘ hors champ | — | Régime en extinction dont l'État verse les derniers engagements ; aucun cotisant depuis 1975. |
| Caisse des retraites des régies ferroviaires d'outre-mer et caisses des chemins de fer d'Afrique du Nord | spécial | depuis 1930, fermé en 1962 | ⊘ hors champ | — | Régimes de rapatriés en extinction, gérés par l'État depuis 1993 ; les services sont validés au régime général par les lois de 1964 et 1965 sur les rapatriés. |
| Prestation de fidélisation et de reconnaissance des sapeurs-pompiers volontaires | spécial | depuis 2005 | ⊘ hors champ | — | Une prestation financée par les collectivités, sans cotisation du bénéficiaire : ce n'est pas un régime de retraite au sens du modèle. |

## Non-salariés non agricoles

| Régime | Famille | Période | Couverture | Statuts | Ce qui manque, ou pourquoi |
|---|---|---|---|---|---|
| Caisse autonome nationale de compensation de l'assurance vieillesse artisanale (`cancava`) | non-salariés | 1949-2006 | ✅ modélisé | `artisan` |  |
| Organisation autonome nationale de l'industrie et du commerce (`organic`) | non-salariés | 1949-2006 | ✅ modélisé | `commercant`, `gerant_debit_tabac`, `micro_entrepreneur` |  |
| Régime social des indépendants (`rsi`) | non-salariés | 2006-2020 | ✅ modélisé | `artisan`, `commercant`, `gerant_debit_tabac`, `micro_entrepreneur` |  |
| Régime complémentaire obligatoire des artisans (`rco_artisans`) | non-salariés | 1979-2013 | ✅ modélisé | `artisan` |  |
| Nouveau régime complémentaire des industriels et commerçants (`nric`) | non-salariés | 2004-2013 | ✅ modélisé | `commercant`, `gerant_debit_tabac`, `micro_entrepreneur` |  |
| Régimes complémentaires des conjoints de commerçants et des entrepreneurs du bâtiment (Organic) (`organic_conjoints_batiment`) | non-salariés | 1973-2004 | ◐ partiel | `commercant`, `gerant_debit_tabac`, `micro_entrepreneur` | La fiche porte la cotisation du commerçant, qui entre au compte notionnel, et rien dans le scénario actuel : la pension va au conjoint, droit dérivé que la carrière individuelle ne porte pas. Le volet bâtiment n'a aucun chiffre dans LEGI (articles 2 à 5 du décret n° 50-60 abrogés, point fixé par la caisse) et n'est pas porté ; les taux d'avant 1985 sont projetés. |
| Régime complémentaire des indépendants (`rci`) | non-salariés | depuis 2013 | ✅ modélisé | `artisan`, `commercant`, `gerant_debit_tabac`, `micro_entrepreneur`, `liberal_non_reglemente` |  |
| Régime micro-social des micro-entrepreneurs | non-salariés | depuis 2009 | ↪ portée par un statut | `micro_entrepreneur` | Le statut `micro_entrepreneur` route les régimes du commerçant sur le revenu reconstitué (chiffre d'affaires après abattement) : la cotisation micro-sociale ventilée entre les branches reproduit, par construction, celle du commerçant — 12,3 % du chiffre d'affaires dont 58,3 % pour la retraite, sur 29 % de revenu, font 24,7 % contre 24,75 % —, et les trimestres se valident sur ce revenu depuis 2023. Non portés : les seuils de chiffre d'affaires d'avant 2023, les variantes de l'abattement (50 % services, 34 % libéral). |
| Caisse nationale d'assurance vieillesse des professions libérales, régime de base (`cnavpl`) | libéral | depuis 1949 | ◐ partiel | `profession_liberale`, `liberal_non_reglemente`, `auxiliaire_medical`, `pharmacien`, `expert_comptable`, `agent_general_assurance`, `notaire`, `veterinaire`, `officier_ministeriel`, `chirurgien_dentiste_ou_sage_femme`, `medecin_liberal` | Le libéral non réglementé installé depuis 2019 relève du régime général et du RCI, celui installé avant reste à la CNAVPL et à la Cipav : le statut `liberal_non_reglemente` le route ainsi, à la date d'installation. Le droit d'option de 2019 à 2023, par lequel un affilié d'avant pouvait rejoindre la sécurité sociale des indépendants, n'est pas porté ; ni la cotisation de la CNAVPL sur les revenus d'avant 1949, qui n'existait pas. Les cent points que D. 643-1 attribue au trimestre d'un accouchement ne le sont pas non plus : le modèle ne connaît pas la date de naissance des enfants. |
| Complémentaire des médecins (CARMF) (`carmf_complementaire`) | libéral | depuis 1949 | ✅ modélisé | `medecin_liberal` |  |
| Complémentaire des chirurgiens-dentistes et des sages-femmes (CARCDSF) (`carcdsf_complementaire`) | libéral | depuis 1949 | ◐ partiel | `chirurgien_dentiste_ou_sage_femme` | La CARSAF des sages-femmes, fusionnée dans la CARCDSF en 2009, avait son propre barème avant : les sages-femmes d'avant 2009 reçoivent celui des dentistes. Les statuts d'avant 2007, publiés au Bulletin officiel, ne sont pas lus : avant 2008 la fiche garde la règle d'âge du régime de base. Le tableau de minoration des nés de juillet 1951 à 1954 (arrêté du 9 juillet 2012) n'est publié qu'en image, et 1,25 % par trimestre en tient lieu. |
| Complémentaire des pharmaciens (CAVP) (`cavp_complementaire`) | libéral | depuis 1949 | ◐ partiel | `pharmacien` | Les dix versions de l'article 2 du décret n° 49-580 datent les grilles de classes (option de 1978 à 2015, classes d'office en plafonds depuis 2015, onze classes depuis 2020), mais la cotisation de référence de chaque année n'est pas dans le texte : le forfait indexé sur les prix en tient lieu, et rien n'est consolidé avant 1978 ; le volet en capitalisation par classes n'est pas chiffré. Les coefficients d'anticipation des nés jusqu'en 1955, « en annexe » des statuts de 2011, ne sont pas dans l'index : les deux pentes de la minoration leur sont appliquées depuis leur propre âge du taux plein, et leur valeur de service n'est pas affectée du coefficient de 0,96. |
| Complémentaire des auxiliaires médicaux (CARPIMKO) (`carpimko_complementaire`) | libéral | depuis 1984 | ✅ modélisé | `auxiliaire_medical` |  |
| Complémentaire des vétérinaires (CARPV) (`carpv_complementaire`) | libéral | depuis 1950 | ◐ partiel | `veterinaire` | Dix périodes suivent les onze versions de l'article 2 du décret n° 50-1318 (actes médicaux par âge de 1950 à 1997, classes de revenu en AMV de 1998 à 2014, points depuis 2015), mais aucun montant d'époque n'est dans le texte — la valeur de l'acte et le prix du point sont fixés hors index — : la grille de 2016 indexée sur les prix tient lieu de montant avant 2016. La règle d'âge — taux plein à 65 ans, 1,25 % par trimestre avant, que la durée n'annule pas — et la bonification pour trois enfants ne sont lues que dans les statuts de 2021 : la première est supposée la même avant, la seconde n'est servie que depuis 2022. |
| Complémentaire des agents généraux d'assurance (CAVAMAC) (`cavamac_complementaire`) | libéral | depuis 1968 | ◐ partiel | `agent_general_assurance` | L'assiette est reconstituée par un facteur moyen de commissions, qui ne décrit aucun assuré en particulier. La règle d'âge d'avant 2011, publiée au seul Bulletin officiel, est supposée celle des statuts de 2011 ; la liquidation des carrières longues à 15 % de minoration et le capital unique versé sous 1 500 points ne sont pas portés. |
| Complémentaire des experts-comptables et commissaires aux comptes (CAVEC) (`cavec_complementaire`) | libéral | depuis 1953 | ✅ modélisé | `expert_comptable` |  |
| Complémentaire des officiers ministériels (CAVOM) (`cavom_complementaire`) | libéral | depuis 1979 | ◐ partiel | `officier_ministeriel` | Le régime par classes de 1979 à 2015 (décret n° 79-265, art. 2, trois grilles de points) dépend de bornes de revenu fixées par les statuts, hors index, et de montants par décret annuel : le taux proportionnel de 2016 est projeté en arrière sur ces trente-sept ans au niveau estimé, et le rendement de 2016 avec lui. |
| Complémentaire de la Cipav (`cipav_complementaire`) | libéral | depuis 1979 | ✅ modélisé | `profession_liberale`, `liberal_non_reglemente` |  |
| Complémentaire des notaires (CPRN), section C (`cprn_complementaire`) | libéral | depuis 1949 | ◐ partiel | `notaire` | La section B, par classes, n'est pas modélisée : ses bornes ne sont publiées nulle part, mais le décret n° 2026-418 en écrit la règle — huit classes d'environ un huitième des notaires en activité chacune — et la caisse la grille des montants, k fois la classe 1 pour 10 k points. Les versions de 1983, 2005 et 2014 de l'article 2 du décret n° 49-578 datent la section C à 4,5 % des produits de l'office, mais rien n'est consolidé avant 1983 ; les statuts d'avant 2014 ne sont pas dans l'index. |
| Caisse de retraite de l'enseignement, des arts appliqués, du sport et du tourisme (CREA) | libéral | 1949-2004 | ⊘ hors champ | — | Section de la CNAVPL dès l'organisation de 1949 (professeurs de musique et musiciens, artistes hors L. 631-1), nommée CREA en 1977 et fondue dans la Cipav au 1er janvier 2004, qui a repris ses affiliés et leurs points ; le statut `profession_liberale` route vers la Cipav sur toute la période, et le barème propre de la CREA n'est pas au Journal officiel, qui n'a que l'arrêté de 1952 sur ses taux et les arrêtés d'approbation de ses statuts. |
| Prestations complémentaires de vieillesse des professionnels de santé conventionnés (ASV) (`asv_conventionnes`) | libéral | depuis 1972 | ◐ partiel | `medecin_liberal` | La fiche ne porte que les médecins, et la seule part qu'ils paient : les deux tiers versés par les caisses d'assurance maladie sont décrits, non comptés. Les points d'ajustement sont pris au plafond de neuf par an, atteint dès 68 000 € de revenu. Les chirurgiens-dentistes (décret n° 2007-458 : dix points par forfait, ajustement 1,45 %), les sages-femmes (2017-1812), les auxiliaires médicaux et les directeurs de laboratoire (2007-597) ont chacun leur barème, lu mais non porté ; leurs statuts restent sans ASV. Le tarif de la consultation, base du forfait de 1985 à 2011, n'est pas une série du dépôt. |
| Caisse nationale des barreaux français, régime de base (`cnbf`) | libéral | depuis 1948 | ◐ partiel | `avocat` | La progression de la cotisation forfaitaire sur les cinq premières années et la contribution équivalente aux droits de plaidoirie ne sont pas portées, ni la majoration de durée d'assurance pour enfants, ni la surcote parentale. La retraite forfaitaire et la cotisation de croisière sont celles de chaque barème depuis 2016 ; avant, celles de 2016 ramenées par les prix. |
| Complémentaire des avocats (CNBF) (`cnbf_complementaire`) | libéral | depuis 1979 | ✅ modélisé | `avocat` |  |
| Caisse des Français de l'étranger et assurance volontaire vieillesse | base, privé | depuis 1984 | ⊘ hors champ | — | Adhésion facultative qui ouvre des droits au régime général : ce n'est pas un régime distinct, et le modèle ne décrit que des affiliations obligatoires. |

## Non-salariés agricoles

| Régime | Famille | Période | Couverture | Statuts | Ce qui manque, ou pourquoi |
|---|---|---|---|---|---|
| Assurance vieillesse des non-salariés agricoles (MSA) (`msa_non_salaries`) | agricole | depuis 1952 | ◐ partiel | `exploitant_agricole` | Le barème en points d'avant 1990 n'est pas lu ; la réforme du 28 février 2025, en vigueur depuis 2026, renvoie deux de ses trois paramètres à un décret absent de la base ; conjoints et aides familiaux sont sous-estimés. |
| Retraite complémentaire obligatoire des non-salariés agricoles (`msa_rco`) | agricole | depuis 2003 | ◐ partiel | `exploitant_agricole` | Les points gratuits des chefs d'exploitation pour leurs années d'avant 2003 sont servis ; ceux du V et du VI de L. 732-56 ne le sont pas — 66 par an, dix-sept annuités au plus, pour les années de conjoint, d'aide familial ou de collaborateur d'avant 2011 et pour celles du chef qui n'a pas dix-sept ans et demi comme chef —, le modèle ne connaissant que le statut de chef. |
| Cotisants de solidarité agricoles | agricole | depuis 1980 | ⊘ hors champ | — | La cotisation de solidarité n'ouvre aucun droit à retraite : il n'y a rien à porter au compte. |

<!-- tableaux:fin -->

## Qui équilibre les régimes fermés depuis 2025

Les tableaux disent qui calcule ; ceci dit qui paie, parce que la réponse a
changé et que le dépôt ne le savait pas. Jusqu'en 2024, l'État versait une
subvention d'équilibre au régime de la SNCF, de la RATP, des mines ou de la
SEITA, et `data/reference/regimes/structure_financement.csv` la porte sous
`subventions_equilibre`, sur le millésime du COR de juin 2024. **Depuis le
1<sup>er</sup> janvier 2025, le régime général est l'équilibreur en dernier
ressort des régimes fermés** — SNCF, RATP, mines, SEITA, industries
électriques et gazières, clercs de notaires, Banque de France, CESE, et les
régimes sans plus aucun cotisant (chemins de fer d'Afrique du Nord, régies
ferroviaires d'outre-mer, ORTF, chemins de fer franco-éthiopiens) — en
application du 3° de l'article `L. 134-3` du code de la sécurité sociale, et
l'État compense la CNAV par crédits budgétaires au titre du 8° de l'article
`L. 241-3`. La compensation est calculée sur le besoin de financement du
régime, net de la compensation démographique que le régime aurait reçue — il
est désormais agrégé au régime général pour ce calcul — et des cotisations que
sa fermeture a portées au régime général et à l'Agirc-Arrco. Les marins restent
subventionnés directement par le programme 197, l'Opéra de Paris et la
Comédie-Française par le programme 195 depuis 2024.

Lu dans les projets annuels de performances annexés au PLF 2026 (mission
« Régimes sociaux et de retraite », programmes 195, 197 et 198), apportés par
l'utilisateur le 20 septembre 2026 ; ce qu'ils chiffrent est saisi dans
`data/reference/regimes/pap_regimes_subventionnes.csv`, avec la page de
chaque valeur. Les textes de l'article `L. 134-3` et de l'article `L. 241-3`
n'ont pas été relus dans l'index LEGI : c'est le PAP qui les cite, et la ligne
de veille le dit.

## La liste relue contre l'échantillon interrégimes de cotisants

En septembre 2026, la liste a été relue contre une énumération officielle que
l'inventaire ne citait pas : l'article 2 de l'arrêté du 22 juillet 2003 relatif
à l'échantillon interrégimes de cotisants, qui nomme, version après version
(2003 : `LEGIARTI000006221466`, 2011 : `LEGIARTI000023816206`, 2023 :
`LEGIARTI000047535084`), les organismes gestionnaires de tous les régimes de
retraite obligatoires. Sur les trente-quatre organismes de 2003 et les
trente-et-un de 2023, un seul manquait à l'inventaire : la **CREA**, section
de la CNAVPL fondue dans la Cipav en 2004. La relecture des textes de
coordination a fait remonter trois caisses de fonctionnaires fermées — la
**CRFOM** des cadres coloniaux (loi du 14 avril 1924, article 71 ; loi de
finances pour 1976, article 73), les caisses des fonctionnaires **d'Algérie,
du Maroc et de Tunisie** dont l'État garantit les pensions, et la **CRFM** des
agents publics de Mayotte (loi n° 2001-616, article 64-1) —, toutes hors champ
faute de cotisant vivant ou de règlement publié. Deux régimes existants ont
gagné une population : la caisse de sécurité sociale de Mayotte couvre aussi
les **non-salariés** depuis 2012 (ordonnance n° 2011-1923, article 20), sans
statut qui les y route ; et le **personnel au sol d'Air France** rejoint la
ligne des régimes professionnels intégrés (règlement approuvé par arrêté du
4 mai 1956, régime différentiel depuis l'arrêté du 1er juin 1993).

**Ce qu'une seconde passe a comblé.** La CREA n'est pas née en 1977 : le
décret n° 50-1089 du 2 septembre 1950 nomme déjà, parmi les sections de
l'organisation de 1949, celles des artistes et des professeurs de musique et
musiciens, dont un arrêté de 1952 fixe les taux ; 1977 est l'année du nom.
La CRFM a été créée en mars 1977 (répertoire Sirene, 16 mars 1977), ses
cotisations sont reprises au niveau national depuis 2007 et elle est en
liquidation avec trois agents (Outre-mer La 1ère, septembre 2025). Les caisses
d'Algérie, du Maroc et de Tunisie ont leurs textes de coordination dans
l'index — homologation de décisions de l'assemblée algérienne (1951), lois de
reclassement de 1956 à 1958, décret n° 68-326 validant les services du
1er avril 1938 au 1er juillet 1962 — mais aucun texte fondateur, et leur date
de création reste vide. Le « régime des médecins » de l'Ircantec est une
assiette : les arrêtés du 18 juillet 1983 et du 7 mars 1986 cotisent les
praticiens hospitaliers sur les deux tiers de leurs émoluments, dans le même
régime. Les non-salariés de Mayotte ont leur décret d'application (décret
n° 2012-1168, article 9). En Polynésie, les délibérations fondatrices sont
maintenant citées — n° 67-110 AT du 24 août 1967, n° 87-11 AT du 29 janvier
1987 pour la tranche A, n° 95-180 AT du 26 octobre 1995 pour la tranche B —,
lues dans un rapport de l'assemblée d'août 2025 ; le régime des non-salariés
(RNS) n'a qu'une adhésion volontaire à la tranche A, donc rien à inventorier
(rapport du Conseil d'orientation et de suivi des retraites, 2020). En
Nouvelle-Calédonie, l'Agirc-Arrco est obligatoire pour les salariés du privé
(fiche du CLEISS), ce que la ligne de la CAFAT dit désormais. Enfin les élus
des assemblées du Pacifique ont leur ligne, hors champ : la loi organique de
1999 confie au congrès et aux assemblées de province le régime de retraite
de leurs membres (articles 78 et 163), les représentants polynésiens ont un
régime par capitalisation auprès d'un assureur privé et les membres du
gouvernement polynésien ne cotisent à la CPS que depuis le 1er juin 2024,
d'après la presse locale.

**Ce qu'une troisième passe a trouvé.** La caisse des retraites de l'Algérie
n'était pas sans texte : l'index JORF, qui remonte ici avant 1947, porte le
décret du 16 juillet 1907 sur son fonctionnement, le décret du 2 février 1926
réformant ses pensions et une dizaine de décrets d'affiliation jusqu'en 1937 ;
la création elle-même est dans la loi de finances du 30 décembre 1903, lue
par le Journal officiel sur Gallica (dont le site refuse les lectures
automatiques : la date est reprise du résumé du moteur de recherche, non du
fac-similé). L'Agirc-Arrco de Nouvelle-Calédonie tient à l'accord
interprofessionnel territorial du 29 août 1994, étendu par arrêté du
25 avril 1995 et généralisé au 1er janvier 1995 avec validation des services
passés, publié par la direction du travail de Nouvelle-Calédonie. Pour les
élus polynésiens, Outre-mer La 1ère (30 avril 2024) confirme que
« représentants et ministres souscrivent à des régimes de retraite privés »
et que la cotisation des ministres à la CPS est d'environ 3 % de leurs
indemnités. Reste hors d'atteinte : les délibérations calédoniennes sur la
retraite des membres du congrès (la seule proposition récente, n° 211 de
2026, organise leur protection juridique, non leur retraite), le texte
polynésien fondateur du régime des représentants (Lexpol et le rapport de
l'assemblée sont inaccessibles ou scannés sans texte), et la page de la Cour
des comptes sur la CRFM, qui répond indisponible.

## Ce qui a été cherché sans être trouvé

Pour que personne ne refasse le trajet : ces régimes ont été cherchés dans
l'index JORF et LEGI du dépôt et n'y ont pas laissé de texte propre.

- **Compagnie générale des eaux** : cité de mémoire comme régime spécial fermé ;
  aucun texte de retraite à son nom dans l'index. Non inscrit.
- **Régime professionnel des banques (AFB)** et **CPPOSS** des organismes de
  sécurité sociale : leur intégration à l'Arrco et à l'Agirc en 1994 est un
  accord collectif, absent du JORF ; ils figurent dans la ligne groupée des
  régimes professionnels intégrés, sans identifiant.
- **ASV** des professionnels de santé : les articles `L. 645-1` et suivants ne
  répondent pas à l'expression « avantage social vieillesse », qui est le nom
  d'usage ; la ligne cite le décret de 1972 sans identifiant.
- **Caisse des retraites de l'Imprimerie nationale** : le régime est nommé par
  `R*77` du code des pensions et par `R. 711-1`, mais sa date de fermeture ne
  l'est pas.

## L'étape suivante : les règles à travers l'histoire

Une fois cette liste admise, le travail change de nature. Pour chaque régime
modélisé ou partiel, la carte de couverture de [`limites.md`](limites.md)
(« Le simulateur doit être juste à tout âge ») compte les années par jeu de
règles : un régime dont la fiche n'a qu'une période applique le droit de 2026 à
1950. Il faut confronter cette carte au calendrier des réformes lu dans LEGI,
version par version, et découper les fiches. Puis écrire celles des régimes à
modéliser, par population décroissante : micro-entrepreneurs, militaires,
ASV, enseignants du privé, régimes intégrés à l'Agirc-Arrco, gérants de
débits de tabac, Mayotte et Saint-Pierre-et-Miquelon, élus locaux, assemblées,
Pacifique. Chaque ajout suit la marche existante : une fiche YAML conforme à
`_schema.yaml`, un `source_id`, un routage dans `affiliations.yaml` ou une
raison de ne pas en avoir, une série de points ou un rendement, la
`part_salariale`, le statut dans les témoins, la reconstruction du paquet et
des témoins, et le portage JavaScript si une assiette nouvelle apparaît.


## Journal de la campagne « les règles à travers l'histoire »

Chaque tranche de la campagne laisse ici une ligne par régime : ce qui a été
coupé, d'après quel texte, ce que cela déplace sur les témoins, ce qui reste.
L'outillage qui la porte : `data/reference/legislation/reformes.yaml` (le
calendrier des réformes, avec les régimes que chacune touche),
`data/reference/regimes/pivots.yaml` (les articles dont les versions datent
chaque fiche) et `scripts/calendrier_regimes.py`, qui lit les versions dans
l'index LEGI et dit ce que la fiche ne coupe pas. Un test impose que toute
réforme touchant un régime soit coupée, absorbée par un drapeau par
génération, ou déclarée non appliquée avec sa raison. Les témoins balaient
désormais chaque statut à six générations — 1925, 1935, 1945, 1955, 1965,
1975 —, 324 cas au lieu de 250.

### Tranche B1 — les régimes alignés qui ne suivaient pas leur modèle

| Régime | Ce qui était faux | Ce qui est lu | Ce que ça déplace |
|---|---|---|---|
| `msa_non_salaries` | 65 ans opposés jusqu'en 2002, puis **64 ans, 67 ans et 172 trimestres dès 2003** — le droit de 2023 sur vingt ans ; aucun drapeau par génération | 65 ans jusqu'en 1985 (ancien code rural, art. 1122, `LEGIARTI000006581025`) ; 60 ans depuis la loi du 6 janvier 1986 (`LEGITEXT000006068962`), minoration entre 60 et 65 ans sans la durée tous régimes (L. 732-25, `LEGIARTI000006585545`) ; loi Fillon aux pensions de 2004 (`LEGIARTI000006585546`), durée et coefficient lus à la génération ; loi Woerth aux pensions prenant effet à compter du 1er juillet 2011 (L. 732-18, `LEGIARTI000023030985`), âges lus à la génération, ce qui porte aussi 2014 et 2023 | sept périodes au lieu de cinq ; exploitant né en 1955 : +2,2 % de pension actuelle ; un exploitant liquidant à 60 ou 62 ans entre 1986 et 2010 n'est plus un contrefactuel |
| `rafp` | 62 ans dès 2005 | 60 ans jusqu'au 2 juin 2011 (décret 2004-569, art. 9, `LEGIARTI000006453304`), puis l'âge de L. 161-17-2 lu à la génération (`LEGIARTI000024113145`) | aucun témoin : personne ne liquide entre 60 et 62 ans dans le balayage ; le droit est daté |
| `ircantec` | 62 et 67 ans dès 2009, deux ans avant la loi Woerth ; coefficient de 0,55 % par trimestre, sans source | Arrêté du 30 décembre 1970, art. 16, douze versions (`LEGIARTI000006381606` à `LEGIARTI000048065521`) : 65 ans, anticipation dès 55, coefficient 0,78 à 60 ans — 1,1 % par trimestre — jusqu'au 30 juin 2011 ; ensuite l'âge de L. 351-8 et celui de L. 161-17-2, lus à la génération | 2009-2010 revient à 60/65 ; les âges et la durée se lisent à la génération depuis 2011 ; aucun témoin déplacé (les cas liquident à 64 ans) |
| `rci` | 62, 67 et 172 en dur, y compris pour les générations à 64 ans | Règlement approuvé le 9 février 2012 (`LEGIARTI000025397326`) : âge légal et taux plein du régime de base — drapeaux par génération | aucun témoin déplacé à 64 ans ; un artisan né en 1968 liquidant à 62 ans est maintenant décoté comme le droit le fait |
| `agirc_arrco` | âge d'annulation 67 en dur | L. 351-8 lu à la génération | rien : personne né avant 1955 n'y liquide |
| `carpv_complementaire` | présumé aligné sur l'âge légal | Le règlement approuvé par l'arrêté du 10 juillet 2026 (`LEGIARTI000054437680`) garde le taux plein à 65 ans et l'anticipation dès 60 ans à 1,25 % par trimestre : la section n'a pas suivi la loi, et la fiche avait raison | déclaré `non_appliquee` pour 2010 et 2023 |
| `cancava`, `organic`, `rsi`, `mines`, `seita`, `port_strasbourg`, `sncf`, `ratp`, `ieg`, `opera_de_paris`, `comedie_francaise`, `marins`, `crpnpac`, sections à l'âge seul | — | déclarés `non_appliquee` réforme par réforme, avec la raison : extinction portée par la fiche, régime laissé où il était, règlement hors LEGI, ou lecture à faire en tranche B2 | rien |

Trois témoins bougent sur 250, et 74 nouveaux entrent (générations 1945 et
1965). C'est peu, et c'est attendu : les cas types liquident à 64 ans avec
une carrière complète, là où les âges faux ne mordaient pas ; ils mordaient
sur qui liquidait tôt, que le balayage ne visite que pour le privé.

### Tranche B2 — les régimes spéciaux à longue période fermée

Ce que l'index LEGI porte, et ce qu'il ne porte pas, pour les sept régimes
de la tranche ; ce qui a été lu et découpé ; ce qui reste.

| Régime | Ce qui a été lu | Ce qui change | Ce qui reste |
|---|---|---|---|
| `sncf` | Décret n° 2008-639, article 1 (`LEGIARTI000032935195`) et article 37-1 (`LEGIARTI000023732614`, `LEGIARTI000029165223`) : le relèvement de 2017 est étalé par génération, quatre mois par année de naissance — cinquante ans pour les agents de conduite nés avant 1967, cinquante-deux ans à compter de 1972 ; cinquante-cinq à cinquante-sept ans, générations 1962-1967, pour les autres | la marche d'un coup de 2018 (50 → 52 ans) devient six périodes, 2017 à 2024, qui suivent le calendrier par année de liquidation ; l'âge de référence de la décote suit | avant 2008, LEGI ne porte rien du règlement de retraites de la SNCF (1911, 1954) ; les cinquante ans, 150 trimestres, 75 % et six derniers mois de 1930-2008 restent lus dans le décret de 2008 « avant modification » ; le relèvement de 2023, étalé à compter de 2025, reste à lire |
| `ratp` | Décret n° 2008-637, article 6 (`LEGIARTI000023732842`) et article 51-1 II (`LEGIARTI000023732424`, décret n° 2011-292) : même calendrier que la SNCF, tableau B à cinquante-deux ans pour les agents nés à compter de 1972 | six périodes 2017-2024 au lieu de la marche de 2017 | avant 2008, rien dans LEGI ; le relèvement de 2023 reste à lire |
| `ieg` | Statut national de 1946, annexe 3 (`LEGIARTI000006632496`, version de 1946, puis `LEGIARTI000023733902`, version du 21 mars 2011) ; les décrets de retenue n° 86-874, 87-468, 88-792, 88-1221 et 91-159 art. 6 | **la retenue de l'agent était fausse de 1946 à 1990** : 7,85 % sur toute la période, quand le statut disait 6 % en 1946 et les décrets 7,7 % au 1er août 1986, 7,9 % de juillet 1987, 8,9 % de janvier 1989, 7,85 % seulement depuis février 1991 — cinq périodes de taux ; et six périodes 2017-2024 pour le calendrier 55 → 57 ans des services actifs | le décret n° 84-63 du 27 janvier 1984 a modifié le taux au 1er janvier 1984 mais l'index n'en porte que la clause d'application (`LEGIARTI000006766294`) : 6 % est reconduit jusqu'en 1985, lecture incomplète et nommée ; le relèvement de 2023 reste à lire |
| `crpcen` | Décret n° 51-721, article 27 (`LEGIARTI000006773239`, 1977-1990) ; décret n° 90-1215, article 84 dans ses neuf versions (`LEGIARTI000006775247` à `LEGIARTI000047910068`) ; décrets de taux n° 74-172, 77-44, 79-423, 86-896, 87-467 | **la table du régime général était lue à la place du calendrier propre du régime** : le drapeau `age_ouverture_par_generation` donnait soixante-deux ans à la génération 1955 quand l'article 84 lui donne cinquante-sept ans et trois mois. Quinze périodes suivent maintenant le calendrier de l'article 84 par année de liquidation, 2008 à 2024, puis l'âge légal lu à la génération depuis 2025 ; la fiche passe de « modélisé » à « partiel » | deux âges avant 2008 — soixante ans, ou cinquante-cinq pour l'assurée ayant vingt-cinq années de cotisations —, la fiche garde le second ; les décrets de taux donnent la cotisation de tous les risques (9,90 % en 1977, 10,75 % en 1979, 16,20 % en 1986), pas la part vieillesse : les 11 % de la fiche restent une estimation |
| `marins` | Code des pensions de retraite des marins, L. 14 (`LEGIARTI000006791907`, `LEGIARTI000006791908`) : « le montant des pensions […] est fixé par voie réglementaire sur la base du salaire forfaitaire » ; R. 2, R. 11 et R. 13 à une ou deux versions (1968, 1985) | rien : la formule est stable et déjà lue | la grille des salaires forfaitaires, l'âge des pensions proportionnelles à cinquante ans, et le code des transports depuis 2010 |
| `banque_de_france` | Décret n° 2007-262 : son règlement annexé existe dans LEGI en dix-sept versions, de 2007 à 2025 (`LEGIARTI000006778516` à `LEGIARTI000047909725`) | rien cette fois | lire ces dix-sept versions, notamment celle du décret n° 2012-701 applicable aux pensions de 2016 ; avant 2007, le règlement du 29 mars 1968 n'est pas dans LEGI |
| `port_strasbourg` | rien : LEGI ne porte que des décrets de compensation | rien | le règlement de retraite est un acte de l'établissement ; la seule voie est de le demander |

Dix témoins bougent : l'agent des IEG né en 1925 perd 18 % de compte
notionnel rétroactif — il avait cotisé 6 % et non 7,85 % —, celui né en 1955
1,5 % ; les âges opposables des cheminots, agents RATP et IEG nés en 1955 et
des clercs nés en 1945 et 1955 descendent d'un à quatre ans et demi. Les
pensions actuelles ne bougent pas : les cas types liquident après l'âge.

### Tranche B3 — les complémentaires du privé, les taux de trente ans

Ni le JORF ni LEGI ne chiffrent le barème de l'Agirc et de l'Arrco avant 1980 :
les conventions sont hors Journal officiel et hors KALI, et les notices
d'avant 1990 n'ont pas de corps. La source est OpenFisca-France (transcription
du Barème social périodique, niveau `haute`), récupérée par
`scripts/fetch/openfisca_cotisations.py` sous quatre formes — taux effectif,
taux contractuel, taux d'appel, répartition salarié/employeur — et dans les
deux barèmes d'adhésion qu'elle distingue. Les fiches portent celui des
**entreprises existantes** (adhérentes avant 1981 à l'Agirc, avant 1997 à
l'Arrco), une période par valeur de « contractuel × appel » ; le contrôle de
vraisemblance de `verifier_donnees.py` les confronte à cinq centièmes près, et
la répartition à un centième. Le taux d'appel de `regimes/valeurs_point.csv`,
que le moteur retire pour convertir une cotisation en points, coïncide année
par année avec celui d'OpenFisca : ce que la fiche porte en trop est exactement
ce que le moteur retire.

| Régime | Ce qui était faux | Ce qui est lu | Ce que ça déplace |
|---|---|---|---|
| `agirc` | 8 % pendant trente-quatre ans, puis trois moyennes de période (11,58 %, 14 %, 19,48 %) posées sur huit à vingt-cinq ans, prises dans le barème des entreprises créées après 1981 ; 160 trimestres en dur de 1994 à 2018 ; le taux plein à l'âge seul d'avant 1983 jamais porté | Taux d'appel de 100 % à 78 % (1952), 80, 85, 90, 95 %, 100 % (1966), 103 % (1979), 106, 110, 113,4, 117 % (1990), 121 puis 125 % (1994-1995) ; taux contractuel 8 % jusqu'en 1993, 10 → 16 % de 1994 à 1999 (accord du 9 février 1994, puis du 25 avril 1996), 16,24 % au 1er janvier 2006 (avenant A-222, `JORFARTI000001866147`), 16,34 et 16,44 % en 2014-2015 (accord du 13 mars 2013) ; ASF du 4 février 1983 (durée requise lue à la génération), GMP 1989, tranche C obligatoire en 1991 (accord du 24 mars 1988), âge du taux plein à la génération depuis 2011 | vingt-quatre périodes au lieu de cinq ; le cadre né en 1925 perd 0,6 % de pension actuelle — ses points de 1952 à 1965 étaient achetés au taux effectif de 8 % divisé par un appel de 78 à 95 %, soit plus que le contractuel —, ceux nés en 1935, 1945 et 1955 gagnent 0,6, 1,0 et 0,9 % |
| `arrco` | 4 % effectifs de 1961 à 1995 quand le moteur divisait par un taux d'appel monté à 125 % : jusqu'à un cinquième des points de 1971-1995 perdus ; 7,50 % de 1996 à 2018, valeur de fin de période | 2,5 % (1962-1966), 4 % (1967), dix marches d'appel de 102,5 % (1971) à 125 % (1992), 4,5 → 6 % de 1996 à 1999 (accords du 10 février 1993 et du 25 avril 1996), 6,10 et 6,20 % en 2014-2015 (`JORFARTI000027826484`) ; mêmes coupures d'âge que l'Agirc | dix-huit périodes ; tous les affiliés Arrco nés de 1935 à 1965 gagnent 0,4 à 1,0 % ; le non-cadre né en 1910 (témoin `enfants_avant_1972`) perd 8,9 % : ses années 1957-1966 étaient cotisées à 4 % quand le barème dit 2,5 % |
| `arrco_tranche_2` | créée en 1996 sur la foi d'« avant 1997, l'Arrco ne cotisait pas au-dessus du plafond » — vrai des seules entreprises créées après 1997 ; 19,50 % en moyenne de 1996 à 2018 | la tranche existe dès l'accord de 1961, au taux de la tranche 1, puis 10, 12, 14, 16 % de 2000 à 2005 (accord du 25 avril 1996, article 26) ; les non-cadres, salariés agricoles, agents de la SEITA et des chemins de fer secondaires y sont routés dès 1961 (`affiliations.yaml`) | vingt-deux périodes ; le salarié agricole né en 1925 gagne 1,7 % ; le non-cadre né en 1975 payé huit plafonds perd 2,9 % (sa tranche 2 de 1996 à 2004 était cotisée à 19,5 % au lieu de 7,5 à 17,5 %) |
| `agirc_arrco` | coefficient de solidarité sans fin | avenant n° 17 du 22 novembre 2023 (`JORFARTI000049224707`, arrêté d'extension du 15 avril 2024, `JORFTEXT000049424935`) ; l'ANI lui-même étendu par l'arrêté du 24 avril 2018 (`JORFTEXT000036847920`) | rien : le coefficient est remplacé par la conversion actuarielle dans les scénarios notionnels |
| `unirs` | 4 %, « à certifier » | aucune source ne date le barème ; 2,5 % par continuité avec la première valeur datée de l'Arrco, toujours `estimee` | compris dans les −8,9 % du non-cadre né en 1910 |
| `ipacte` | née en 1959 ; 4 % sur la tranche 1 | décret n° 51-1445 du 12 décembre 1951 (`LEGITEXT000006060604`) : huit ans de plus ; assiette au-dessus du plafond jusqu'à quatre fois, 4,75 dès 1961 (article 7, `LEGIARTI000006368159`) ; salaires de référence 1951-1970 (`LEGIARTI000006381673`), identiques à la série du dépôt sauf 1955 (74 F, soit 0,113 €, contre 0,130) ; ni taux ni âge dans l'index — la fiche passe `partiel` | le contractuel né en 1925 perd 0,4 % : payé sous le plafond, l'année 1959 ne lui ouvre plus de points |
| `igrante` | jamais routée : « le critère qui répartissait un agent entre les deux institutions n'est documenté par aucune source » | décret n° 59-1569, article 2 (`LEGIARTI000006368165`) : toute la rémunération jusqu'à trois plafonds, et sous le plafond seulement pour les affiliés de l'IPACTE ; répartition 40/60 (arrêté du 17 février 1960, article 15, `LEGIARTI000006381706`) ; routée au contractuel de 1960 à 1970 sur la tranche 1, sans recouvrement avec l'IPACTE | rien de visible : même point que l'IPACTE |
| moteur | l'abattement de l'Agirc-Arrco consultait la table par durée sur toute l'histoire | avant l'ASF de 1983, l'âge seul : une période sans durée requise ne consulte que la table par âge (`_abattement_points`, porté dans `moteur/js/`) ; et depuis 2011 l'âge du taux plein des points Arrco et Agirc d'avant 2019 se lit à la génération | le non-cadre né en 1975 liquidant à 57 ans perd 3,0 % : ses points d'avant 2019 sont abattus jusqu'à 67 ans, l'âge de sa génération, et non 65 |

Deux cent six témoins bougent, sur 324. Outre ce qui précède, tous les statuts
publics gagnent 0,4 à 1,8 % sur le scénario libéral et la part employeur des
générations 1925 à 1965 : avant 1995, la contribution de l'employeur public est
estimée par l'effort d'un employeur privé de la même année, qui comprend
désormais la tranche 2 et les marches d'appel de l'Arrco. Aucun âge opposable
ne bouge.

Ce qui reste, et où : le taux et l'âge de l'IPACTE et de l'IGRANTE (Caisse des
dépôts, hors index) ; le barème de l'UNIRS ; le barème des entreprises nouvelles,
récupéré mais prêté à personne ; la série salarié d'OpenFisca en retard d'une
marche d'appel sur la série employeur en 1953 et 1989 (arrondie à un quart) ;
le salaire de référence IPACTE de 1955 dans `valeurs_point.csv`, que la
certification OpenFisca réécrirait.

### Restes de B3 — ce que les mêmes articles disaient encore

| Régime | Ce qui était faux | Ce qui est lu | Ce que ça déplace |
|---|---|---|---|
| `ipacte` | taux 4 % « à certifier », répartition 40/60 prêtée de l'Ircantec | l'article 7 du décret 51-1445 (`LEGIARTI000006368159`), déjà cité pour l'assiette, écrit aussi le taux : « 4,25 p. 100 et 8,25 p. 100 », soit 12,5 % contractuels, 34 % à la charge de l'agent ; l'article 7 du décret 70-1277 (`LEGIARTI000006368121`) reprend ces chiffres mot pour mot au 1er janvier 1971, et l'Ircantec les appelle à 60 % (Caisse des dépôts) : appel prolongé sur 1951-1970 au niveau `estimee`, effectif 7,5 % ; salaire de référence 1955 corrigé à 74 F = 0,112812 € (`LEGIARTI000006381673`, `LEGIARTI000006381707`) ; anticipation abattue comme le successeur — l'escalier de l'article 16 de l'arrêté du 30 décembre 1970, que la fiche approchait par une pente moyenne de 1,1 % par trimestre jusqu'à ce que l'oracle Ircantec le fasse relire | le contractuel né en 1925 et en 1935 : voir le diff des témoins ; fiche `moyenne` (version consolidée unique, décrets modificatifs à titre seul), âge toujours estimé |
| `igrante` | taux 4 % « à certifier » | article 2 du décret 59-1569 (`LEGIARTI000006368165`) : « 1,40 p. 100 et 2,10 p. 100 », 3,5 % contractuels, 40 % agent — le rapport 1,40/3,50 confirme l'article 15 de l'arrêté de 1960 ; appel 60 % prolongé, effectif 2,1 % | idem |
| `unirs` | note parlant d'« arrêtés d'extension » | les deux seules occurrences du nom avant 1975 sont un arrêté d'approbation (`JORFTEXT000000849607`) et un décret de subvention (`JORFTEXT000000875512`), sans chiffre ; LEGI n'en porte rien | rien : 2,5 % `estimee` conservé, inventaire précisé |
| `agirc_entreprises_nouvelles`, `arrco_tranche_2_entreprises_nouvelles` | le barème des entreprises créées après 1981 (Agirc : 12 % dès 1983) et après 1997 (Arrco tranche 2 : 14 % d'emblée) n'était prêté à personne | deux fiches générées de la variante `entreprises_nouvelles` d'OpenFisca (27 et 6 périodes, `points_de` Agirc/Arrco), deux statuts « entreprise créée après 1981 / 1997 » | douze témoins nouveaux (336), identiques aux témoins de droit commun au salaire moyen, qui n'atteint ni le plafond ni la tranche 2 ; à deux plafonds, le cadre né en 1955 d'une entreprise créée après 1981 touche 1,7 % de pension actuelle de plus que celui d'une entreprise ancienne (12 % de points Agirc au lieu de 8 % de 1983 à 1993) |
| outillage | une valeur lue dans un texte était réécrite par la transcription OpenFisca au prochain `--appliquer` | `source_valeurs_point` retire les clés des `COMPLEMENTS` (`openfisca_points.py`) ; nouvelle certification `valeurs_point_estimees` pour les prolongements assumés | le journal de certification distingue « saisi dans le texte » (`moyenne`) et « prolongé » (`estimee`) |

### Restes de B2 — le relèvement de 2023 dans les régimes spéciaux, et deux séries de taux

| Régime | Ce qui était faux | Ce qui est lu | Ce que ça déplace |
|---|---|---|---|
| `sncf` | le relèvement de la loi du 14 avril 2023, déclaré « non lu » ; pivots posés sur les articles 3 (pension proportionnelle) et 17 (entrée en jouissance) | décret n° 2023-967, article 37-1 (`LEGIARTI000048240186`, `LEGIARTI000048896987`) : aux pensions prenant effet dès le 1er janvier 2025, conduite 52 → 54 ans, trois mois par génération 1973-1979 ; sédentaires 57 → 59 ; annulation de la décote 62 → 64 ; pivots refaits sur les articles 37-1 (âges) et 13 (décote) | huit périodes 2025-2034 ; l'âge opposable du cheminot né en 1975 passe de 52 à 54 ans, celui du né en 1965 à 53 ans (calendrier par année de liquidation) ; aucune pension ne bouge, les cas liquident après l'âge |
| `ratp` | idem, pivot sur l'article 13 qui n'a qu'une version | décret n° 2023-690 : article 6 (`LEGIARTI000047913991`, 54/59/64 ans dès 2025) et 51-1 (`LEGIARTI000047914257`, mêmes rampes 1972-1979, 1967-1974, 1962-1969) | mêmes huit périodes, mêmes âges opposables |
| `ieg` | idem ; pivot sur le seul décret n° 2011-290, à une version | décret n° 2023-692 (`JORFTEXT000047903232`) réécrit l'annexe 3 du statut, non consolidée dans LEGI : « l'âge mentionné à l'article L. 161-17-2 » et « cet âge abaissé de cinq ans » aux pensions dès 2025 — 57 → 59 ans des services actifs, générations 1961-1968 ; durée 170-172 (art. 45 I bis, plus exigeante d'un à trois trimestres que la table nationale, non portée) ; pivot sur l'annexe 3 (`LEGIARTI000006632496`, 21 versions) | périodes 2025-2026 (58 ans 9 mois) et 2027- (59 ans) ; l'âge opposable des agents nés en 1965 et 1975 passe de 57 à 59 ans |
| `ieg` 1984 | 6 % de retenue reconduits jusqu'en 1985, le chiffre du décret n° 84-63 manquant à LEGI | la notice du Journal officiel le porte : « art. 24 parag. 2 : 7 %, cotisations à compter du 01-01-1984 » (`JORFTEXT000000885345`) ; les six décrets frères (n° 69-265 à 90-772) touchent le paragraphe 8 de l'article 23, la cotisation aux caisses mutuelles d'action sociale, et non la retraite | période 1984-1985 à 7 % ; le compte notionnel rétroactif de l'agent né en 1925 gagne 2,1 %, celui de 1935 1,0 %, celui de 1955 0,3 % |
| `banque_de_france` | 10,29 % de 2011 à 2022 (le palier de 2019 servi douze ans), 11,10 % dès 2023 ; relèvement à 64 ans coupé au 1er septembre 2023 | les quatorze versions du règlement annexé (`LEGIARTI000006778516` → `LEGIARTI000047909725`) : 7,85 % jusqu'en 2012, 8,12 % (2013), 8,54 % (2014), puis l'échelle définitive 8,86 → 11,10 % de 2015 à 2022 ; la fermeture de 2023 ne relève rien (`LEGIARTI000047909413`), le relèvement date du 1er janvier 2025 (`LEGIARTI000047909725`, table de l'article 72, la même que la table nationale) | seize périodes ; le compte notionnel rétroactif de l'agent né en 1955 perd 5,3 %, celui de 1965 2,8 %, celui de 1975 1,9 % : ils avaient cotisé moins que 10,29 % de 2011 à 2018 |
| `opera_de_paris`, `comedie_francaise` | déclarés « relèvement non lu » | le décret n° 2023-840 (`JORFTEXT000048011057`) ne touche que carrières longues, minimum, retraite progressive et cumul : aucun relèvement d'âge, la fermeture est portée par le routage ; les versions de 1995, 2011 et 2017 lues (`LEGIARTI000006765538`, `LEGIARTI000024468762`, `LEGIARTI000029135161`, `LEGIARTI000029134341`) ne changent rien pour la catégorie modélisée (ballet à 40 ans ; durée par génération identique à la table nationale) | rien ; raisons `non_appliquee` réécrites |
| `marins` | pivots sur L. 14 et R. 13 seuls | R. 2 (`LEGIARTI000006791972` : 55 ans, 50 avec vingt-cinq ans de services), R. 11 (`LEGIARTI000006791987` : salaire forfaitaire de la catégorie des trois dernières années), R. 13 (`LEGIARTI000006791990` : 2 % par annuité, 37,5 annuités) confirment la fiche ; la grille des vingt catégories (décret n° 52-540, art. 1er, huit versions) n'est chiffrée au JORF que depuis 2008 (`JORFARTI000017964781` → `JORFARTI000051452700`) et exige une catégorie que la carrière ne porte pas | rien ; inventaire précisé |
| `port_strasbourg` | — | rien dans les deux index hormis le décret de 1925, l'affiliation au régime local et la liste de 2014 (`LEGIARTI000021290664`, `LEGIARTI000006742525`, `JORFARTI000029964983`) | rien ; inventaire précisé |

### Tranche B4 — les libéraux, décret par décret

Les montants annuels (forfaits, classes, prix du point) de 1998 à 2024 étaient déjà
lus au Journal officiel par `scripts/fetch/jorf_cotisations_liberales.py` ; ce qui
manquait, c'est la STRUCTURE des barèmes avant 1998 et les coupures de droit, que
les décrets consolidés portent version par version. Aucun montant d'époque n'est
dans ces textes — valeur de l'acte médical vétérinaire, cotisation de référence des
pharmaciens, bornes de revenu des classes : fixés par l'ordre, par le conseil
d'administration, par les statuts —, si bien que les périodes nouvelles disent ce
que le droit exigeait, et la grille ou le forfait le plus ancien, indexé sur les
prix, tient lieu de montant.

| Régime | Ce qui était faux | Ce qui est lu | Ce que ça déplace |
|---|---|---|---|
| `carpv_complementaire` | une période 1950-2026 ; pivot mal formé (neuf arrêtés du 10 juillet 2026 pris pour neuf versions) | décret n° 50-1318, art. 2, onze versions (`LEGIARTI000006776818` → `LEGIARTI000054168212`) : actes médicaux par âge (50/80/50 en 1954, 95/152/95 en 1967, 144/228/144 en 1982), classes de revenu en AMV dès le 2 décembre 1997 (B 480, C 600, D 720), points × prix d'achat dès 2015 (16/20/24 PA), assiette de l'année précédente dès 2022 | dix périodes ; rien sur les témoins (la grille de 2016 indexée sert de montant) |
| `cavp_complementaire` | deux périodes 1949-2025 et 2026- | décret n° 49-580, art. 2, dix versions (`LEGIARTI000006770075` → `LEGIARTI000054168167`) : option entre classes 1-9 (× 4 à 12 la référence) en 1978, 1-13 (× 5 à 17) en 1987, 3-13 en 2009, six classes d'office bornées en PASS (2 / 2,75 / 3,5 / 4,25 / 5) en 2015, onze classes dès 2020 | sept périodes ; rien sur les témoins |
| `cipav_complementaire` | 1979-2022 d'un bloc | décret n° 79-262, art. 2 : classes 1-10 de 4 à 40 points (`LEGIARTI000006767473`), refonte A-H de 36 à 468 points au 1er janvier 2013 (`LEGIARTI000026892951`) | deux périodes au lieu d'une ; rien sur les témoins |
| `cprn_complementaire` | 1962-2016 d'un bloc | décret n° 49-578, art. 2 : « 2 % et 2,5 % de la moyenne des produits de l'étude » en 1983 (`LEGIARTI000006763853`, soit les 4,5 % de la fiche), section C à 4,5 % en 2005 (`LEGIARTI000006763855`), taux par décret annuel dès 2014 (`LEGIARTI000028325795`) ; rien avant 1983 | quatre périodes au lieu d'une ; rien sur les témoins |
| `cavom_complementaire` | fiche commençant en 2016 : trente-sept ans sans complémentaire pour l'officier ministériel | décret n° 79-265, art. 2 : classes de points de 1980 (`LEGIARTI000006770098`), 1987 (`…099`), 2013 (`LEGIARTI000026892955`), bornes de revenu dans les statuts, hors index ; plafond transitoire 4 → 7 PASS 2016-2019 (`LEGIARTI000031875318`) | période 1979-2015 au taux de 2016 projeté en arrière, `estimee`, routée ; **l'officier ministériel né en 1955 gagne 71 % de pension actuelle, celui né en 1965 39 %, celui né en 1975 20 %** ; les comptes notionnels des générations 1925-1945 doublent |
| `cnavpl` | — | D. 642-3 en quinze versions : 8,6 %/1,6 % dès 2004 (`LEGIARTI000006738115`), 9,75 %/1,81 % en 2013 et 10,1 %/1,87 % en 2014 (`LEGIARTI000026704782`), 8,23 %/1,87 % dès le 19 juillet 2015 (`LEGIARTI000030910750`), 8,73 % dès 2025 (`LEGIARTI000049904651`) — la fiche coïncidait déjà ; L. 643-3 version de la loi du 30 décembre 2025 (`LEGIARTI000053280388`, pensions dès le 1er septembre 2026) : majoration pour trimestres cotisés avant l'âge légal, non portée | rien |
| `cavamac_complementaire`, `carmf_complementaire` | — | le décret porte un taux contractuel constant (6,30 % ; 14 %) et la fiche les taux appelés : notes de réconciliation | rien |
| `cavec_complementaire`, `carcdsf_complementaire`, `carpimko_complementaire`, `ircec_raap`, `cnbf`, `cnbf_complementaire` | — | hors LEGI ou déjà millésimés par le Journal officiel ; rien à couper | rien |

Ce qui reste : les montants d'avant 1998 (AMV, cotisation de référence, bornes des
classes), fixés hors index ; la section B des notaires ; la majoration de 2026 des
libéraux ; les coupures informatives restantes de la carte (versions de rédaction).

### Tranche B5a — un étage de plus sur des statuts existants

Deux régimes de l'inventaire qui n'étaient prêtés à personne et dont les textes
sont dans LEGI : l'ASV des médecins conventionnés, troisième étage financé aux
deux tiers par l'assurance maladie, et le régime additionnel des maîtres de
l'enseignement privé sous contrat. Le troisième candidat de la tranche, les
complémentaires des conjoints de commerçants et du bâtiment (Organic), reste
`a_modeliser` : la pension du régime des conjoints est un droit DU CONJOINT
(D. 635-35, D. 635-36), que la carrière individuelle du modèle ne porte pas ; la
ligne d'inventaire est réécrite avec les identifiants (décret n° 50-60, art. 2,
`LEGIARTI000006781230` ; D. 635-36 `LEGIARTI000006738096`).

| Régime | Ce qui manquait | Ce qui est lu | Ce que ça déplace |
|---|---|---|---|
| `asv_conventionnes` | aucune fiche : le médecin du modèle n'avait que la CNAVPL et la CARMF, sans le tiers de sa pension que l'ASV représente | décret n° 72-968, art. 2 (`LEGIARTI000024871109`) : 30,16 points par an de 1972 à 1993, 27 depuis, « au prorata du nombre de trimestres cotisés » — d'où `points_par_trimestre_valide` ; D. 645-2, version par version : 30 fois la consultation en 1985 (`LEGIARTI000006738371`), 45 en 1993 (`…373`), 52 en 1995 (`…375`), 60 de 1999 à 2011 (`…376` → `LEGIARTI000023380413`) ; D. 645-3 : part des caisses « au double » (`LEGIARTI000006738166`), égale du 30 mars 1993 au 8 juillet 1994 (`…167`) ; décret n° 2011-1644 : forfait 4 300 → 4 850 € de 2012 à 2016 (art. 1, `LEGIARTI000024853551`), cotisation d'ajustement 0,25 → 3,8 % sous cinq plafonds (art. 2, `LEGIARTI000033090911`), 4 % dès 2026 (`LEGIARTI000052567960`), neuf points d'ajustement au plus (art. 3, `LEGIARTI000024853554`), valeur de service 13 € puis 11,31 € pour les points liquidés dès 2017 et 11,82 € en 2025 (art. 4, `LEGIARTI000024853556`, `LEGIARTI000033090908`, `LEGIARTI000052567955`) | vingt et une périodes, la part du médecin seule (statut sans employeur) ; le médecin né en 1975 au salaire moyen gagne 1 742 € par mois de pension actuelle (+80 % : un régime forfaitaire pèse d'autant plus que le revenu est bas — à 100 000 € il pèserait un tiers), celui né en 1925 448 € ; +6 à +14 % en notionnel rétroactif, par ses propres cotisations. Niveau `estimee` : le tarif C n'est pas une série du dépôt, les points d'ajustement sont pris au plafond de neuf |
| `enseignants_prive_additionnel` | aucune fiche, famille dite `additionnel_capitalise` quand le régime est en répartition ; cotisation dite « 1,5 % partagée » | décret n° 2005-1233, art. 2 (`LEGIARTI000006436188`, rémunération versée par l'État, sans plafond), art. 7 (`LEGIARTI000027090124` : 5, 7, 8 % des pensions de base et complémentaire, puis 8 % × part des services d'après 2005 + 2 % × part d'avant) ; arrêté du 28 juillet 2006, art. 1 : 0,75 % + 0,75 % (`LEGIARTI000006253469`), 1 % + 1 % dès 2013 (`LEGIARTI000027090163`), 1,5 % + 1,5 % dès juin 2024 par paliers de 1,2 à 1,4 % jusqu'en 2026 (`LEGIARTI000049688551`) | six périodes, famille `special`, pension par rendement (0,085 → 0,045 selon l'année de liquidation, `estimee`) faute d'asseoir un régime sur les pensions des autres ; statut nouveau `maitre_enseignement_prive`, six témoins (342) : +236 € par mois de pension actuelle pour le maître né en 1975 par rapport au non-cadre, +15 € pour celui de 1945, rien avant |
| `organic_conjoints_batiment` | identifiant faux (l'art. 16 du décret 70-368 pris pour le régime lui-même) | décret n° 50-60 art. 2, D. 635-35, D. 635-36 (0,50 %/1,82 % 1985-1998, 1,5 %/3,5 % 1998-2003), D. 635-35-1 | rien : droit du conjoint, ligne réécrite |

Ce qui reste de B5a : les barèmes ASV des chirurgiens-dentistes (décret 2007-458 :
dix points par forfait, ajustement 1,45 %), des sages-femmes (2017-1812), des
auxiliaires médicaux et des directeurs de laboratoire (2007-597), lus mais non
portés ; les points d'ajustement proportionnels au revenu sous 68 000 € ; le tarif
de la consultation de 1985 à 2011.

### Tranche B5b — des statuts nouveaux, l'index suffisant

Sept statuts et cinq fiches, tous lus dans LEGI ou, pour les barèmes de points
que les caisses seules publient, sur leurs sites (IRCEC, Caisse des dépôts). Deux
lignes de l'inventaire n'ont pas de fiche parce que ce ne sont pas des régimes :
l'affiliation des élus locaux à l'Ircantec et le micro-social, qui ne sont qu'un
routage ; elles restent `a_modeliser` avec leur statut et ce qui manque.

| Régime | Ce qui manquait | Ce qui est lu | Ce que ça déplace |
|---|---|---|---|
| `cps_saint_pierre_et_miquelon` | aucune fiche | loi n° 87-563, art. 5 (`LEGIARTI000030930361`, `LEGIARTI000054477924`) : durée par génération de 150 (avant 1956) à 172 trimestres (1974), âges décalés de sept générations sur L. 161-17-2 ; décret n° 89-110, art. 9 (`LEGIARTI000006774247`) : 108 trimestres en 1987, plus quatre par an jusqu'à 150 en 1998, taux et coefficient de R. 351-27 ; décret n° 2017-1000, art. 3 (`LEGIARTI000034740766`) : R. 351-29 étendu | trente-deux périodes, taux et plafond prêtés du régime général ; statut `salarie_saint_pierre_et_miquelon` (1987-, Arrco du non-cadre) : même pension actuelle que le non-cadre pour la génération 1975, 41 % de moins pour 1945 (trois années sans régime avant 1987 ne se rattrapent pas) |
| `cssm_mayotte` | aucune fiche | décret n° 87-175, art. 2 (`LEGIARTI000006770150`) : 55 ans et 120 trimestres à titre transitoire ; décret n° 2003-589 : 64 trimestres en 2003 plus quatre par an (`LEGIARTI000006781028`), âge de 55 à 60 ans de 2003 à 2010 (`LEGIARTI000006781021`), âge par génération de 60 à 62 ans (`LEGIARTI000026514429`) puis 63 ans et 9 mois pour 1968-1969 (`LEGIARTI000049915788`, `LEGIARTI000054059636`), durée par génération de 120 à 172 dès 2018 (`LEGIARTI000033155436`), coefficient de 2,5 % à 1,25 % (`LEGIARTI000033155432`), taux plein à l'âge plus cinq ans (`LEGIARTI000026514415`) | trente-quatre périodes ; statut `salarie_mayotte` (1987-, sans complémentaire) : 26 % de moins que le non-cadre pour la génération 1975, faute d'Agirc-Arrco |
| `ircec_racd`, `ircec_racl` | aucune fiche, deux populations confondues avec l'artiste-auteur | décret n° 64-226, art. 2 (`LEGIARTI000006761271`) : 8 % des droits ; décret n° 61-1304, art. 1 (`LEGIARTI000006781613`) ; mémo 2026 de l'IRCEC : 6,5 % au RACL, points à 4,78 € et 0,421 € (RACD), 10,304 € et 0,618 € (RACL) | une période chacune, rendements 8,8 et 6,0 centimes ; statuts `auteur_dramatique` et `auteur_lyrique` : +32 % et +18 % de pension actuelle sur l'artiste-auteur (génération 1975) |
| `gerants_debits_tabac` | aucune fiche | arrêté du 13 novembre 1963, art. 5 (`LEGIARTI000006787840`, participation du fonds au double), art. 5 bis (`LEGIARTI000006787842`, 2 % des remises brutes dès 1990), art. 6 (plafond de remises), art. 17 (`LEGIARTI000006787896`, point à 1 F en 1963) ; Caisse des dépôts : point à 4,94 € d'achat et 2,42 € de service | deux périodes, part du gérant seule, rendement de 49 centimes par euro du gérant (le fonds paie les deux autres tiers) ; statut `gerant_debit_tabac` : +63 % de pension actuelle sur le commerçant pour la génération 1975 — le revenu saisi tient lieu de remises, ce qui surestime un débit qui vend aussi presse ou jeux |
| `elus_locaux_ircantec` | pas de statut | loi n° 72-1201, art. 1 (`LEGIARTI000006338235`), L. 2123-28 (`LEGIARTI000006390053`) | statut `elu_local` : Ircantec seule de 1973 à 2012, régime général en plus depuis 2013 ; 27 % de moins que le contractuel public pour la génération 1975 (quarante ans sans base) ; pas de fiche, la ligne le dit |
| `micro_entrepreneurs` | pas de statut | L. 133-6-8 (`LEGIARTI000033712872`, abattements de 71, 50 et 34 %), D. 131-6-3 (`LEGIARTI000034163578`) | statut `micro_entrepreneur` : les régimes du commerçant sur le revenu reconstitué, témoins identiques à ceux du commerçant ; les seuils de chiffre d'affaires restent à porter |

Ce qui reste de B5b : le seuil de L. 382-31 des élus, le SMIG mahorais et le
plafond local des deux caisses d'outre-mer, les barèmes anciens du RACD, du RACL
et du RAVGDT, la cotisation micro-sociale réellement versée.

### Tranche B5c — les régimes sans texte dans l'index, lus sur les sites des institutions

Huit lignes de l'inventaire n'avaient ni décret ni arrêté dans le JORF ou dans LEGI.
Décision de l'utilisateur : lire les sites. `scripts/fetch/sites_institutionnels.py`
garde la pièce — quatorze pages et PDF dans `data/brut/sites_institutionnels/`, le
texte des PDF extrait à côté —, et chaque fiche cite la phrase qu'elle en tire ;
rien n'est recontrôlé automatiquement, toutes ces fiches sont au niveau `estimee`.
Sept fiches, six statuts ; l'Imprimerie nationale sort du champ (régime éteint fin
2013 au décès du dernier pensionné, dix affiliés en 2007 selon le programme 195) ;
les régimes professionnels intégrés restent `a_modeliser`, la ligne citant l'accord
bancaire du 13 septembre 1993 et le complément différentiel qu'il institue.

| Régime | Ce qui manquait | Ce qui est lu | Ce que ça déplace |
|---|---|---|---|
| `assemblees_parlementaires` | aucune fiche, « ni barème ni règlement » | règlement de la Caisse de pensions des députés au 1er janvier 2018 : retenue sur l'indemnité parlementaire, de résidence et de fonction (art. 5), 64 ans dès la génération 1969 et trois mois par génération depuis 1961 (art. 8), valeur de l'annuité de 2,11 % (jusqu'en 2008) à 1,9628 % (après 2028) et 40 à 43 annuités (art. 21), liquidation aux paramètres du soixante-quatrième anniversaire (art. 21 ter) ; arrêté des Questeurs n° 15-043 : retenue de 9,34 % (2015) à 10,85 % (2020) ; Sénat : 62 à 64 ans et 43 annuités (12 juillet 2023), assimilé | vingt-deux périodes, retenue du député seule (la part de l'Assemblée n'est pas écrite) ; statut `parlementaire` : 84,4 % de l'indemnité pour 43 annuités, 27 % de moins que le fonctionnaire de l'État au même revenu pour la génération 1975 |
| `cese_membres` | aucune fiche | règlement de la caisse au 1er janvier 2025 : retenue « égale à 3,42 fois » celle de L. 61 sur la rémunération de base (art. 4), âge de L. 161-17-2 et cinq ans de mandat (art. 7), 2,11 % puis 1,82 % (dès le 28 octobre 2013) de « 2,06 fois la rémunération » par annuité, plafond des trois quarts (art. 17) ; fermeture aux membres désignés dès le 1er septembre 2023 | treize périodes, le revenu saisi pris pour l'assiette de référence (retenue divisée par 2,06) ; statut `membre_cese` à clause du grand-père (régime général et Arrco pour les désignés depuis 2023) : 75 % de l'indemnité en 41 annuités, 35 % de moins que le fonctionnaire pour la génération 1975 |
| `cps_polynesie`, `cps_polynesie_tranche_b` | aucune fiche, « rien n'est lu » | CLEISS : tranche A « 70 % × salaire mensuel moyen × (nombre de mois cotisés / 456 mois) » sur les 180 meilleurs mois des 240 derniers, 62 ans et 456 mois depuis 2023, 23,53 % (15,69 + 7,84) jusqu'à 269 000 FCFP ; tranche B : 17,43 % entre 269 000 et 525 000 FCFP, points au « salaire minimum horaire de référence (1 024,74 FCFP) » valant « 1 024,74 FCFP par 2 % soit 20,49 FCFP » | deux fiches (assiette nouvelle `tranche_1_2_pass`, moteur Python et JS), rendement de 11,5 centimes pour la tranche B ; statut `salarie_polynesie` : +19 % sur le non-cadre pour la génération 1975 (70 % au lieu de 50 % de base, sans complémentaire) |
| `cafat_nouvelle_caledonie` | aucune fiche | CLEISS et CAFAT : 14 % (9,80 + 4,20) jusqu'à 548 600 FCFP, points par division des cotisations « par une valeur de référence » non publiée, point à 256,09 FCFP, 60 ans et 6 mois en 2023 jusqu'à 62 ans en 2026, 37 années en 2026, décote de 1,5 % par trimestre dans la limite de dix | cinq périodes, rendement estimé à 10 centimes ; statut `salarie_nouvelle_caledonie` (avec l'Arrco du non-cadre) : même pension actuelle que le non-cadre pour la génération 1975 |
| `wallis_et_futuna` | « pas de régime de retraite obligatoire […] recensé » | CPSWF : « salaire moyen des 15 meilleures années multiplié par le taux […] 2,60 % pour les 15 premières années avec 1,30 % par année supplémentaire », 60 ans, quinze ans de cotisation ; cotisation de 17,1 % (2009) à 27 % (2020), part salariale de 3,7 à 7 % | le régime existe ; treize périodes, 58,5 % pour 120 trimestres ; statut `salarie_wallis_et_futuna` : +4 % sur le non-cadre pour la génération 1975, moitié moins pour 1925 (rien avant 1975) ; borne du test des parts salariales abaissée à un cinquième pour cette seule fiche |
| `fonctionnaires_pacifique` | aucune fiche | DRHFP de Nouvelle-Calédonie : « une annuité […] ouvre droit à 2 %, et 40 annuités […] à 80 % du traitement de base », cotisations de 10,8 % (agent) et 25,1 % (employeur) jusqu'en septembre 2023, 13 % et 28,8 % en 2027, minoration « 35 % avant 57 ans […] 10 % entre 59-60 ans », âge « de 60 à 62 ans sur 6 ans » dès 2025 | huit périodes (la fiche est la CLR ; les fonctionnaires de Polynésie relèvent de la CPS) ; statut `fonctionnaire_pacifique` : +7 % sur le fonctionnaire de l'État pour la génération 1975 (80 % au lieu de 75 %) |
| `imprimerie_nationale` | « date de fermeture à confirmer » | programme 195 : dix affiliés en 2007, extinction fin 2013 | ligne passée `hors_champ` : aucun assuré vivant |

Ce qui reste de B5c : la part des assemblées et le règlement du Sénat, la
valeur de référence des points CAFAT, les plafonds locaux du Pacifique (les
plafonds nationaux tiennent lieu), les barèmes d'avant 2009 à Wallis et d'avant
2023 en Nouvelle-Calédonie, la table exacte de l'âge de la CLR, le complément
bancaire des régimes intégrés.

### Tranche B5d — les quatre dernières lignes

| Ligne | Ce qui manquait | Ce qui est lu | Ce que ça déplace |
|---|---|---|---|
| `elus_locaux_ircantec` | le seuil de L. 382-31, « que le statut ne lit pas » | L. 382-31 (`LEGIARTI000026790815`) : l'indemnité n'est « assujettie aux cotisations de sécurité sociale [que] lorsque [son] montant total est supérieur à une fraction, fixée par décret, de la valeur du plafond » — la moitié (D. 382-34, hors index) | le routage sait lire un SEUIL : `seuil_pass: {regime_general: 0.5}` sur la période 2013- du statut, `Affiliations.regimes()` reçoit le revenu et le plafond de l'année (Python et JS, un test dans chaque langue) ; un élu à 16 000 € n'a que l'Ircantec, à 24 000 € le régime général aussi. La ligne devient « portée par un statut », couverture nouvelle `routage` (inventaire, site, tests) |
| `micro_entrepreneurs` | « pas un régime mais une manière de cotiser » | L. 133-6-8 (`LEGIARTI000033712872`), D. 131-6-3 (`LEGIARTI000034163578`) : la cotisation micro-sociale ventilée reproduit celle du commerçant sur le revenu reconstitué (24,7 % contre 24,75 %), les trimestres se valident sur ce revenu depuis 2023 | `routage` : le statut `micro_entrepreneur` porte la ligne ; restent les seuils de chiffre d'affaires d'avant 2023 et les variantes de l'abattement |
| `organic_conjoints_batiment` | aucune fiche ; « droit du conjoint » | D. 635-32 (`LEGIARTI000006738054`), D. 635-34 (`…056`, un droit du conjoint), D. 635-35 (`…057`, cotisation additionnelle de tous les assujettis), D. 635-36 : 0,50 %/1,82 % (`…095`), 1,5 %/3,5 % (`…096`), 2,5 %/3,95 % (`…097`) sur deux tranches au tiers du plafond (assiettes nouvelles `plafonnee_033_pass`, `tranche_033_1_pass`) ; décret n° 50-60 : articles vides, régime fermé le 25 mars 1998 (`LEGIARTI000006781229`) | une COTISATION SANS DROIT PROPRE, huit périodes de 1973 à 2003, rendement nul : le commerçant, le buraliste et le micro-entrepreneur la versent au compte notionnel (+0,9 % de pension rétroactive pour la génération 1975, +8 % pour 1945), le scénario actuel ne leur sert rien ; le volet bâtiment reste hors fiche |
| `regimes_professionnels_integres` | aucune fiche ; « le modèle leur applique l'Arrco et l'Agirc » | IFRAP, « La réforme des retraites des banques » : « 72 à 75 % du dernier salaire pour une carrière complète de 42 ans, c'est-à-dire 1,667 % par année », Sécurité sociale comprise ; « cotisation [de] 12 à 20 % de la masse salariale » ; droits figés au 31 décembre 1993 (accord du 13 septembre 1993) | une fiche 1947-1993 portant le COMPLÉMENT (35 % du dernier salaire en 168 trimestres, 16 % de cotisation, `estimee`) pour toutes les populations intégrées ; statut `salarie_regime_professionnel_integre` (426 témoins) : +49 % de pension actuelle sur le non-cadre pour la génération 1925, +17 % pour 1945, rien pour 1975 (entré après 1993) |

Ce qui reste de B5d : l'élu qui a cessé toute activité (assujetti sous le
seuil), le complément bancaire différentiel et son rabot de 1994, les barèmes
propres de la CPPOSS, de la CGRCE, des CCI, de l'IRREP et de la CAMARCA, la
pension du conjoint comme droit dérivé.

### Feuille de route B5 — ce que le script montre à lire

`python scripts/calendrier_regimes.py --carte` (le tableau est dans
[`limites.md`](limites.md)) compte, pour chaque fiche, les versions d'articles
pivots qui commencent sans qu'une période commence. Ce que ces nombres disent
pour les tranches suivantes :

- **Bruit à connaître.** `msa_rco` (24) et `carmf` (1) : la valeur du point
  change chaque année, c'est `valeurs_point.csv` qui la porte, pas la fiche.
  `regime_general` (14), `cnracl` (17), `fonction_publique_etat` (7),
  `fspoeie` (4), `msa_salaries` (3) : versions de rédaction (renvois,
  codification) d'articles dont les paramètres sont déjà lus à la génération
  par les tables de `legislation/` ; à relire une fois pour le confirmer, sans
  attendre de coupure.
- **Restes de B2.** Le règlement du port autonome de Strasbourg, à demander ;
  la grille des salaires forfaitaires des marins, qui attend une saisie de
  catégorie.
- **Restes de B3.** L'âge de liquidation de l'IPACTE et de l'IGRANTE (articles
  absents de LEGI) et le barème de l'UNIRS restent à demander à la Caisse des
  dépôts et à la fédération.
- **Puis B5**, les dix-huit régimes à modéliser de l'inventaire, par
  population décroissante — B5a à B5d ci-dessus les ont tous portés : plus
  aucune ligne `a_modeliser`, deux lignes « portées par un statut ».
