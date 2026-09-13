# Les régimes de retraite français, tous — et ce que le dépôt en calcule

**Le fichier qui fait foi est [`data/reference/regimes/inventaire.yaml`](../data/reference/regimes/inventaire.yaml).**
Ce document en est la lecture commentée ; la page **Données** du site l'affiche
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

L'inventaire compte **81 régimes** : 34 modélisés,
20 calculés mais incomplets, 18 à modéliser,
9 hors champ.

| Couverture | Ce que cela veut dire |
|---|---|
| ✅ modélisé | une fiche du catalogue, sur toute l'histoire connue du régime |
| ◐ partiel | une fiche calculée, mais un étage, un barème ou une période manque — la colonne dit lequel |
| ✚ à modéliser | aucune fiche ; la colonne dit ce qui bloque |
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


## Salariés du privé — régimes de base

| Régime | Famille | Période | Couverture | Statuts | Ce qui manque, ou pourquoi |
|---|---|---|---|---|---|
| Retraites ouvrières et paysannes | base, privé | 1911-1930 | ⊘ hors champ | — | Régime en capitalisation, antérieur à 1930, l'année où le modèle commence : aucun assuré vivant n'y a cotisé, et le texte n'est pas dans le dump de la DILA, qui commence en 1947. |
| Assurances sociales (assurance vieillesse) (`assurances_sociales`) | base, privé | 1930-1945 | ✅ modélisé | `salarie_prive_non_cadre`, `salarie_prive_cadre`, `salarie_agricole` |  |
| Régime local d'assurance invalidité-vieillesse d'Alsace-Moselle | base, privé | 1919-1946 | ⊘ hors champ | — | Législation allemande de 1889 et 1911 maintenue après 1918, fondue dans le régime général en 1946 : les droits acquis sous ce régime sont liquidés par le régime général selon les décrets de 1974 à 1977. Aucun assuré vivant n'y a cotisé assez longtemps pour que ses règles pèsent. |
| Allocation aux vieux travailleurs salariés (`avts`) | base, privé | 1941-1945 | ✅ modélisé | — |  |
| Régime général de la Sécurité sociale (Cnav) (`regime_general`) | base, privé | depuis 1945 | ✅ modélisé | `salarie_prive_non_cadre`, `salarie_prive_cadre`, `contractuel_public`, `artisan`, `commercant`, `artiste_auteur`, `personnel_navigant`, `agent_sncf`, `agent_ratp`, `agent_ieg`, `mineur`, `personnel_opera`, `personnel_comedie_francaise`, `agent_seita`, `agent_port_strasbourg`, `agent_chemins_fer_secondaires` |  |
| Assurances sociales agricoles, salariés (MSA) (`msa_salaries`) | agricole | depuis 1930 | ✅ modélisé | `salarie_agricole` |  |
| Régime de retraite des salariés de Mayotte (Caisse de sécurité sociale de Mayotte) | base, privé | depuis 1987 | ✚ à modéliser | — | Droit national, mais paramètres propres — âge, durée, plafond, taux — qui convergent vers ceux du régime général selon un calendrier que le dépôt n'a pas encore lu ; ni statut ni fiche. |
| Régime de retraite de la Caisse de prévoyance sociale de Saint-Pierre-et-Miquelon | base, privé | depuis 1987 | ✚ à modéliser | — | Durée requise et âges propres — 152 trimestres pour la génération 1956 quand le régime général en exige 166, déjà signalé dans docs/limites.md comme un piège des tables par génération ; ni statut ni fiche. |
| Régime de retraite des travailleurs salariés de Polynésie française (CPS) | base, privé | depuis 1968 | ✚ à modéliser | — | Compétence locale : les textes ne sont ni dans le JORF ni dans LEGI, et la source est la caisse elle-même. Rien n'est lu. |
| Régime de retraite des travailleurs salariés de Nouvelle-Calédonie (CAFAT) | base, privé | depuis 1958 | ✚ à modéliser | — | Compétence locale, comme la Polynésie : source chez la caisse, rien n'est lu. |
| Retraite des salariés de Wallis-et-Futuna | base, privé | — | ✚ à modéliser | — | Pas de régime de retraite obligatoire de droit commun recensé par le dépôt ; à établir avant toute fiche. |
| Caisse des Français de l'étranger et assurance volontaire vieillesse | base, privé | depuis 1984 | ⊘ hors champ | — | Adhésion facultative qui ouvre des droits au régime général : ce n'est pas un régime distinct, et le modèle ne décrit que des affiliations obligatoires. |

## Salariés du privé — complémentaires et régimes additionnels

| Régime | Famille | Période | Couverture | Statuts | Ce qui manque, ou pourquoi |
|---|---|---|---|---|---|
| Association générale des institutions de retraite des cadres (`agirc`) | complémentaire, privé | 1947-2018 | ✅ modélisé | `salarie_prive_cadre`, `personnel_navigant` |  |
| Union nationale des institutions de retraite des salariés (`unirs`) | complémentaire, privé | 1957-1962 | ◐ partiel | `salarie_prive_non_cadre` | L'UNIRS tient lieu de toutes les institutions fédérées avant 1961 — CRI, CIRCC, CGRCR, IRPSIMMEC, CAPIMMEC et les autres —, dont aucune n'a de fiche propre : chacune avait son barème, et le dépôt n'en connaît qu'un. |
| Association des régimes de retraite complémentaire des salariés (`arrco`) | complémentaire, privé | 1961-2018 | ◐ partiel | `salarie_prive_non_cadre`, `salarie_prive_cadre`, `salarie_agricole`, `personnel_navigant`, `mineur`, `agent_seita`, `agent_chemins_fer_secondaires` | Routée à tous les salariés dès 1961, alors que l'affiliation n'est obligatoire pour tous que depuis la loi du 29 décembre 1972 : entre 1961 et 1972 le modèle prête une complémentaire à qui n'en avait pas. |
| Arrco, tranche 2 des non-cadres (`arrco_tranche_2`) | complémentaire, privé | 1996-2018 | ✅ modélisé | `salarie_prive_non_cadre`, `salarie_agricole`, `mineur`, `agent_seita`, `agent_chemins_fer_secondaires` |  |
| Régime unifié Agirc-Arrco (`agirc_arrco`) | complémentaire, privé | depuis 2019 | ✅ modélisé | `salarie_prive_non_cadre`, `salarie_prive_cadre`, `salarie_agricole`, `personnel_navigant`, `agent_sncf`, `agent_ratp`, `agent_ieg`, `mineur`, `personnel_opera`, `personnel_comedie_francaise`, `agent_seita`, `agent_port_strasbourg`, `agent_chemins_fer_secondaires` |  |
| Institution de prévoyance des agents contractuels et temporaires de l'État (`ipacte`) | complémentaire, privé | 1959-1971 | ✅ modélisé | `contractuel_public` |  |
| Institution générale de retraite des agents non titulaires de l'État (`igrante`) | complémentaire, privé | 1959-1971 | ✅ modélisé | — |  |
| Institution de retraite complémentaire des agents non titulaires de l'État et des collectivités publiques (`ircantec`) | complémentaire, privé | depuis 1971 | ✅ modélisé | `contractuel_public` |  |
| Affiliation des élus locaux à l'Ircantec | complémentaire, privé | depuis 1973 | ✚ à modéliser | — | Un statut à part : l'indemnité de fonction ouvre des points Ircantec sans régime de base, et depuis 2013 elle est aussi soumise aux cotisations du régime général au-delà d'un seuil. Le régime existe au catalogue, pas le statut qui y route une indemnité. |
| Caisse de retraite du personnel navigant professionnel de l'aéronautique civile, tranche 1 (`crpnpac`) | spécial | depuis 1963 | ◐ partiel | `personnel_navigant` | Les fiches s'arrêtent à l'état de 2023, quand le régime est passé du code de l'aviation civile au code des transports ; le taux d'appel de 1995 à 2011 n'est pas appliqué. |
| Caisse de retraite du personnel navigant, tranche 2 (`crpnpac_tranche_2`) | spécial | depuis 1963 | ◐ partiel | `personnel_navigant` | Même limite que la tranche 1 : état de 2023. |
| Régime des artistes-auteurs professionnels (IRCEC) (`ircec_raap`) | libéral | depuis 1962 | ◐ partiel | `artiste_auteur` | Avant 2017 la cotisation était optionnelle, choisie par classe sans lien avec le revenu ; le seuil d'affiliation de 900 SMIC horaires n'est pas appliqué. |
| Régime des auteurs et compositeurs dramatiques (IRCEC) | libéral | depuis 1964 | ✚ à modéliser | — | Second étage obligatoire pour une partie des artistes-auteurs, en plus du RAAP ; le mémo annuel de l'IRCEC en publie le barème (4,78 € d'achat, 0,421 € de service en 2026) mais aucun statut ne distingue ces auteurs. |
| Régime des auteurs et compositeurs lyriques (IRCEC) | libéral | depuis 1962 | ✚ à modéliser | — | Même situation que le RACD : barème publié par la caisse (10,304 € et 0,618 € en 2026), pas de statut. |
| Régimes professionnels de salariés intégrés à l'Agirc-Arrco | complémentaire, privé | depuis 1947, fermé en 2000 | ✚ à modéliser | — | Régimes à prestations définies, chacun avec son barème, servis jusqu'à leur intégration à l'Arrco et à l'Agirc, dont les affiliés d'avant sont encore vivants ; le modèle leur applique l'Arrco et l'Agirc de droit commun sur toute la période. |
| Régime additionnel de retraite des enseignants du privé sous contrat | additionnel, capitalisé | depuis 2005 | ✚ à modéliser | — | Un troisième étage en répartition, financé par une cotisation de 1,5 % partagée, qui s'ajoute au régime général et à l'Agirc-Arrco des maîtres du privé ; pas de statut. |

## Fonction publique et assimilés

| Régime | Famille | Période | Couverture | Statuts | Ce qui manque, ou pourquoi |
|---|---|---|---|---|---|
| Pensions civiles et militaires, loi de 1853 (`pensions_civiles_1853`) | fonction publique | 1853-1948 | ✅ modélisé | `fonctionnaire_etat` |  |
| Pensions civiles et militaires de retraite (Service des retraites de l'État) (`fonction_publique_etat`) | fonction publique | depuis 1948 | ◐ partiel | `fonctionnaire_etat` | Les militaires sont routés comme des civils : pension après quinze ou dix-sept ans de services, limites d'âge de grade, bonifications de campagne et du cinquième ne sont pas modélisées — un statut `militaire` manque. Les fonctionnaires de La Poste et d'Orange ont la même pension mais une contribution employeur propre depuis 2006, non distinguée. |
| Caisse nationale de retraites des agents des collectivités locales (`cnracl`) | fonction publique | depuis 1945 | ✅ modélisé | `fonctionnaire_territorial_hospitalier` |  |
| Caisses communales de retraite et Caisse intercommunale de retraites | fonction publique | 1930-1945 | ⊘ hors champ | — | Fondues dans la CNRACL en 1945, qui a repris leurs droits ; le statut territorial route vers la CNRACL dès 1945 et personne de vivant n'a liquidé sous une caisse communale. |
| Fonds spécial des pensions des ouvriers des établissements industriels de l'État (`fspoeie`) | fonction publique | depuis 1928 | ✅ modélisé | `ouvrier_etat` |  |
| Retraite additionnelle de la fonction publique (`rafp`) | additionnel, capitalisé | depuis 2005 | ✅ modélisé | `fonctionnaire_etat`, `fonctionnaire_territorial_hospitalier`, `ouvrier_etat` |  |
| Caisses de retraite des anciens députés, des anciens sénateurs et des personnels des assemblées | spécial | depuis 1904 | ✚ à modéliser | — | Régimes autonomes fixés par les bureaux des assemblées et non publiés au Journal officiel ; le dépôt n'a lu ni barème ni règlement. À modéliser par décision, avec les rapports publics des assemblées pour source. |
| Caisse de retraite des anciens membres du Conseil économique, social et environnemental | spécial | depuis 1957 | ✚ à modéliser | — | Même situation que les assemblées parlementaires, pour quelques centaines de personnes. |
| Caisses de retraite des fonctionnaires de Nouvelle-Calédonie et de Polynésie française | fonction publique | depuis 1959 | ✚ à modéliser | — | Compétence locale ; la Caisse locale de retraites de Nouvelle-Calédonie et la CPS polynésienne publient leurs propres règlements, non lus. |

## Régimes spéciaux de salariés

| Régime | Famille | Période | Couverture | Statuts | Ce qui manque, ou pourquoi |
|---|---|---|---|---|---|
| Régime spécial des agents du cadre permanent de la SNCF (`sncf`) | spécial | depuis 1909, fermé en 2020 | ✅ modélisé | `agent_sncf` |  |
| Régime spécial de retraite du personnel de la RATP (`ratp`) | spécial | depuis 1900, fermé en 2023 | ✅ modélisé | `agent_ratp` |  |
| Régime spécial des industries électriques et gazières (CNIEG) (`ieg`) | spécial | depuis 1946, fermé en 2023 | ✅ modélisé | `agent_ieg` |  |
| Régime des marins (ENIM) (`marins`) | spécial | depuis 1673 | ◐ partiel | `marin` | La grille des salaires forfaitaires par catégorie, que le décret renvoie à un arrêté, est introuvable, et la catégorie du marin n'est pas dans la carrière saisie ; un seul jeu de règles pour 1930-2026. |
| Régime spécial de sécurité sociale dans les mines (CANSSM) (`mines`) | spécial | depuis 1894, fermé en 2010 | ✅ modélisé | `mineur` |  |
| Caisse de retraite et de prévoyance des clercs et employés de notaires (`crpcen`) | spécial | depuis 1937 | ✅ modélisé | `clerc_de_notaire` |  |
| Régime spécial de retraite de la Banque de France (`banque_de_france`) | spécial | depuis 1806, fermé en 2007 | ✅ modélisé | `agent_banque_de_france` |  |
| Régime de retraite du personnel de l'Opéra national de Paris (`opera_de_paris`) | spécial | depuis 1698, fermé en 2023 | ✅ modélisé | `personnel_opera` |  |
| Régime de retraite du personnel de la Comédie-Française (`comedie_francaise`) | spécial | depuis 1812, fermé en 2023 | ✅ modélisé | `personnel_comedie_francaise` |  |
| Régime de retraite du personnel du port autonome de Strasbourg (`port_strasbourg`) | spécial | depuis 1926, fermé en 2023 | ◐ partiel | `agent_port_strasbourg` | Le règlement de retraite est un acte de l'établissement, absent de LEGI, qui ne porte que des décrets de compensation : un seul jeu de règles pour 1930-2026, au niveau `estimee`. |
| Régime de retraite du personnel de la SEITA (`seita`) | spécial | depuis 1935, fermé en 1981 | ✅ modélisé | `agent_seita` |  |
| Caisse autonome mutuelle de retraites des chemins de fer secondaires et tramways (CAMR) (`chemins_fer_secondaires`) | spécial | depuis 1922, fermé en 1954 | ◐ partiel | `agent_chemins_fer_secondaires` | Une seule période, au niveau `estimee`, depuis le texte fondateur sans recontrôle. |
| Régime des cultes (CAVIMAC) (`cavimac`) | spécial | depuis 1979 | ✅ modélisé | `ministre_du_culte` |  |
| Régime d'allocation viagère des gérants de débits de tabac (RAVGDT) | spécial | depuis 1963 | ✚ à modéliser | — | Régime obligatoire en points géré par la Caisse des dépôts, qui s'ajoute au régime des commerçants du gérant ; cotisation sur les remises, avec une participation du fonds des redevances égale au double. Ni statut ni fiche. |
| Caisse des retraites de l'Imprimerie nationale | spécial | depuis 1927, fermé en 1994 | ✚ à modéliser | — | Régime fermé, financé par l'État au programme 195 ; ses paramètres ne sont pas lus et la date de fermeture est à confirmer dans les textes de transformation de l'Imprimerie nationale en société (1993-1994). |
| Régime spécial de retraite du Crédit foncier de France | spécial | 1930-1988 | ⊘ hors champ | — | Transféré au régime général au 1er janvier 1989, pensions et cotisants compris : les droits acquis sont servis par le régime général et le dépôt n'a pas de source pour le barème d'avant. |
| Régime de retraite des personnels de l'ORTF | spécial | depuis 1964, fermé en 1975 | ⊘ hors champ | — | Régime en extinction dont l'État verse les derniers engagements ; aucun cotisant depuis 1975. |
| Caisse des retraites des régies ferroviaires d'outre-mer et caisses des chemins de fer d'Afrique du Nord | spécial | depuis 1930, fermé en 1962 | ⊘ hors champ | — | Régimes de rapatriés en extinction, gérés par l'État depuis 1993 ; les services sont validés au régime général par les lois de 1964 et 1965 sur les rapatriés. |
| Prestation de fidélisation et de reconnaissance des sapeurs-pompiers volontaires | spécial | depuis 2005 | ⊘ hors champ | — | Une prestation financée par les collectivités, sans cotisation du bénéficiaire : ce n'est pas un régime de retraite au sens du modèle. |

## Non-salariés non agricoles

| Régime | Famille | Période | Couverture | Statuts | Ce qui manque, ou pourquoi |
|---|---|---|---|---|---|
| Caisse autonome nationale de compensation de l'assurance vieillesse artisanale (`cancava`) | non-salariés | 1949-2006 | ✅ modélisé | `artisan` |  |
| Organisation autonome nationale de l'industrie et du commerce (`organic`) | non-salariés | 1949-2006 | ✅ modélisé | `commercant` |  |
| Régime social des indépendants (`rsi`) | non-salariés | 2006-2020 | ✅ modélisé | `artisan`, `commercant` |  |
| Régime complémentaire obligatoire des artisans (`rco_artisans`) | non-salariés | 1979-2013 | ✅ modélisé | `artisan` |  |
| Nouveau régime complémentaire des industriels et commerçants (`nric`) | non-salariés | 2004-2013 | ✅ modélisé | `commercant` |  |
| Régimes complémentaires des conjoints de commerçants et des entrepreneurs du bâtiment (Organic) | non-salariés | 1970-2004 | ✚ à modéliser | — | Deux complémentaires obligatoires d'avant le NRIC, dont les points ont été repris par le RCI : le commerçant d'avant 2004 du modèle n'a aucune complémentaire, alors que le conjoint collaborateur et l'entrepreneur du bâtiment en avaient une. |
| Régime complémentaire des indépendants (`rci`) | non-salariés | depuis 2013 | ✅ modélisé | `artisan`, `commercant` |  |
| Régime micro-social des micro-entrepreneurs | non-salariés | depuis 2009 | ✚ à modéliser | — | Pas un régime mais une manière de cotiser : un pourcentage du chiffre d'affaires, dont une fraction va au régime de base et à la complémentaire, et des trimestres validés par le chiffre d'affaires. Le modèle ne sait décrire qu'un revenu, pas un chiffre d'affaires ; c'est la population non salariée la plus nombreuse aujourd'hui. |
| Caisse nationale d'assurance vieillesse des professions libérales, régime de base (`cnavpl`) | libéral | depuis 1949 | ◐ partiel | `profession_liberale`, `auxiliaire_medical`, `pharmacien`, `expert_comptable`, `agent_general_assurance`, `notaire`, `veterinaire`, `officier_ministeriel`, `chirurgien_dentiste_ou_sage_femme`, `medecin_liberal` | Les libéraux non réglementés qui créent leur activité depuis 2018 relèvent du régime général et du RCI, non de la CNAVPL et de la Cipav : le routage du statut générique devrait dépendre de l'année d'entrée, et ne le fait pas. |
| Complémentaire des médecins (CARMF) (`carmf_complementaire`) | libéral | depuis 1949 | ◐ partiel | `medecin_liberal` | La caisse ne publie que l'année en cours : les chiffres de 2026 sont appliqués à toute la période. |
| Complémentaire des chirurgiens-dentistes et des sages-femmes (CARCDSF) (`carcdsf_complementaire`) | libéral | depuis 1949 | ◐ partiel | `chirurgien_dentiste_ou_sage_femme` | La CARSAF des sages-femmes, fusionnée dans la CARCDSF en 2009, avait son propre barème avant : les sages-femmes d'avant 2009 reçoivent celui des dentistes. |
| Complémentaire des pharmaciens (CAVP) (`cavp_complementaire`) | libéral | depuis 1949 | ◐ partiel | `pharmacien` | Le volet en capitalisation par classes n'est pas chiffré ; seule la part forfaitaire en répartition l'est. |
| Complémentaire des auxiliaires médicaux (CARPIMKO) (`carpimko_complementaire`) | libéral | depuis 1984 | ✅ modélisé | `auxiliaire_medical` |  |
| Complémentaire des vétérinaires (CARPV) (`carpv_complementaire`) | libéral | depuis 1950 | ◐ partiel | `veterinaire` | Un seul jeu de règles pour 1950-2026 : les classes d'avant 2016 ne sont pas datées. |
| Complémentaire des agents généraux d'assurance (CAVAMAC) (`cavamac_complementaire`) | libéral | depuis 1968 | ◐ partiel | `agent_general_assurance` | L'assiette est reconstituée par un facteur moyen de commissions, qui ne décrit aucun assuré en particulier. |
| Complémentaire des experts-comptables et commissaires aux comptes (CAVEC) (`cavec_complementaire`) | libéral | depuis 1953 | ✅ modélisé | `expert_comptable` |  |
| Complémentaire des officiers ministériels (CAVOM) (`cavom_complementaire`) | libéral | depuis 1979 | ◐ partiel | `officier_ministeriel` | Fiche écrite à partir de 2016 seulement : le régime par classes de 1979 à 2015 n'a pas de grille publiée. |
| Complémentaire de la Cipav (`cipav_complementaire`) | libéral | depuis 1979 | ✅ modélisé | `profession_liberale` |  |
| Complémentaire des notaires (CPRN), section C (`cprn_complementaire`) | libéral | depuis 1949 | ◐ partiel | `notaire` | La section B, par classes, dont les bornes ne sont publiées nulle part, n'est pas portée : près de quatre dixièmes du complémentaire d'un notaire. |
| Prestations complémentaires de vieillesse des professionnels de santé conventionnés (ASV) | libéral | depuis 1972 | ✚ à modéliser | — | Un troisième étage obligatoire pour les professionnels de santé conventionnés, financé aux deux tiers par l'assurance maladie, qui pèse près du tiers de la pension d'un médecin de secteur 1 ; aucun des statuts de santé ne le porte. |
| Caisse nationale des barreaux français, régime de base (`cnbf`) | libéral | depuis 1948 | ◐ partiel | `avocat` | La progression de la cotisation forfaitaire sur les cinq premières années et la contribution équivalente aux droits de plaidoirie ne sont pas portées. |
| Complémentaire des avocats (CNBF) (`cnbf_complementaire`) | libéral | depuis 1979 | ✅ modélisé | `avocat` |  |

## Non-salariés agricoles

| Régime | Famille | Période | Couverture | Statuts | Ce qui manque, ou pourquoi |
|---|---|---|---|---|---|
| Assurance vieillesse des non-salariés agricoles (MSA) (`msa_non_salaries`) | agricole | depuis 1952 | ◐ partiel | `exploitant_agricole` | Le barème en points d'avant 1990 n'est pas lu ; la réforme du 28 février 2025, en vigueur depuis 2026, renvoie deux de ses trois paramètres à un décret absent de la base ; conjoints et aides familiaux sont sous-estimés. |
| Retraite complémentaire obligatoire des non-salariés agricoles (`msa_rco`) | agricole | depuis 2003 | ◐ partiel | `exploitant_agricole` | Les points gratuits attribués aux conjoints et aides familiaux — 66 par an dans la limite de 17 ans — ne sont pas portés. |
| Cotisants de solidarité agricoles | agricole | depuis 1980 | ⊘ hors champ | — | La cotisation de solidarité n'ouvre aucun droit à retraite : il n'y a rien à porter au compte. |

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
