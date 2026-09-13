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

L'inventaire compte **81 régimes** : 33 modélisés,
21 calculés mais incomplets, 18 à modéliser,
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
| Arrco, tranche 2 des non-cadres (`arrco_tranche_2`) | complémentaire, privé | 1961-2018 | ✅ modélisé | `salarie_prive_non_cadre`, `salarie_agricole`, `mineur`, `agent_seita`, `agent_chemins_fer_secondaires` |  |
| Régime unifié Agirc-Arrco (`agirc_arrco`) | complémentaire, privé | depuis 2019 | ✅ modélisé | `salarie_prive_non_cadre`, `salarie_prive_cadre`, `salarie_agricole`, `personnel_navigant`, `agent_sncf`, `agent_ratp`, `agent_ieg`, `mineur`, `personnel_opera`, `personnel_comedie_francaise`, `agent_seita`, `agent_port_strasbourg`, `agent_chemins_fer_secondaires` |  |
| Institution de prévoyance des agents contractuels et temporaires de l'État (`ipacte`) | complémentaire, privé | 1951-1971 | ◐ partiel | `contractuel_public` | LEGI ne conserve du décret que l'assiette (article 7) : le taux de cotisation et l'âge de liquidation ne sont écrits nulle part dans l'index, et la fiche les estime — 4 %, 60 et 65 ans. |
| Institution générale de retraite des agents non titulaires de l'État (`igrante`) | complémentaire, privé | 1960-1971 | ◐ partiel | `contractuel_public` | Comme l'IPACTE, taux et âge estimés faute d'article ; et la fiche ne porte que la tranche sous le plafond, celle de l'agent qui relève aussi de l'IPACTE — les autres non-titulaires cotisaient jusqu'à trois plafonds, part qu'aucun statut ne distingue. |
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
| Caisse de retraite et de prévoyance des clercs et employés de notaires (`crpcen`) | spécial | depuis 1937 | ◐ partiel | `clerc_de_notaire` | Deux âges avant 2008 — soixante ans, ou cinquante-cinq pour l'assurée justifiant de vingt-cinq années de cotisations — et le moteur n'en porte qu'un : la fiche garde le second. Les décrets de taux (1977, 1979, 1986) donnent la cotisation de tous les risques, pas la part vieillesse. |
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
| `ipacte` | taux 4 % « à certifier », répartition 40/60 prêtée de l'Ircantec | l'article 7 du décret 51-1445 (`LEGIARTI000006368159`), déjà cité pour l'assiette, écrit aussi le taux : « 4,25 p. 100 et 8,25 p. 100 », soit 12,5 % contractuels, 34 % à la charge de l'agent ; l'article 7 du décret 70-1277 (`LEGIARTI000006368121`) reprend ces chiffres mot pour mot au 1er janvier 1971, et l'Ircantec les appelle à 60 % (Caisse des dépôts) : appel prolongé sur 1951-1970 au niveau `estimee`, effectif 7,5 % ; salaire de référence 1955 corrigé à 74 F = 0,112812 € (`LEGIARTI000006381673`, `LEGIARTI000006381707`) ; anticipation abattue de 1,1 % par trimestre comme le successeur | le contractuel né en 1925 et en 1935 : voir le diff des témoins ; fiche `moyenne` (version consolidée unique, décrets modificatifs à titre seul), âge toujours estimé |
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
  population décroissante.
