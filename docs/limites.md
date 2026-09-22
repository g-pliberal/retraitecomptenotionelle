# Limites — à lire avant d'utiliser un chiffre

Ce modèle est une charpente complète et fonctionnelle. Ses séries
macroéconomiques sont **certifiées de 1950 à 2025**, ses tables de mortalité sont
celles réellement observées depuis 1899, son plafond de la Sécurité sociale
remonte à 1931 daté décret par décret, et les tables par génération qui
commandent la décote — âge d'ouverture, durée requise, coefficient de
minoration — sont **lues dans le texte des articles du code** : le tout
recontrôlé automatiquement contre les sources, à chaque exécution. Ce qui
précède 1950 pour le salaire et la productivité, et les barèmes propres à
certains régimes, restent saisis à la main. Ce document dit exactement où passe
la frontière, pour qu'aucun résultat ne soit cité sans savoir sur quoi il
repose.

---

## Paramètres du scénario 1, et ce qu'ils valent

Le scénario 1 sert d'étalon : ce qui n'y est pas sourcé fragilise tout le reste.
Ce qui suit est le recensement complet de ses paramètres et de leur état.

| Paramètre | Valeur retenue | État |
|---|---|---|
| Minimum contributif | ancres du code 2007 et 2023 ; montants servis 2020, 2024-2026 | **certifié** (D. 351-2-1) et transcrit |
| Minimum contributif majoré | idem, <!--chiffre:cellule(data/reference/legislation/minimum_contributif.csv:valeur?mesure=montant_majore&annee=2007)-->7 603,41<!--/--> → <!--chiffre:cellule(data/reference/legislation/minimum_contributif.csv:valeur?mesure=montant_majore&annee=2023)-->10 170,86<!--/--> €/an | **certifié**, même article |
| Plafond d'écrêtement du minimum | ancres 2012 et 2014 ; montants servis 2020, 2024-2026 | **certifié** (D. 173-21-0-0-1) et transcrit |
| Minimum garanti, barème | montée en charge 2004-2013, indice 216 → 227 | **certifié** (loi de 2003, article 66 V) ; la ligne 1976 décrit le droit antérieur et reste transcrite |
| Minimum garanti, référence | <!--chiffre:cellule(data/reference/legislation/minimum_garanti_montants.csv:valeur/12?annee=2004)-->997,96<!--/--> €/mois au 1er janvier 2004 ; montants servis 2020, 2023-2025 | transcrit ; l'ancre de 2004 est recoupée à chaque exécution au point d'indice certifié — 227 × 52,7558 = <!--chiffre:cellule(data/reference/legislation/minimum_garanti_montants.csv:valeur?annee=2004)-->11 975,57<!--/--> € |
| Point d'indice de la fonction publique | série datée 1960-2027 | OpenFisca-France, **recontrôlé à chaque exécution** |
| Minimum vieillesse (ASPA) | montants servis 2007, 2010, 2016-2026 | transcrit des publications |
| Décote de la fonction publique | article L. 14, montée en charge 2006-2020 | **certifiée** (loi de 2003, article 66 III) jusqu'à 2019 ; la ligne 2020 est la jonction avec L. 14 |
| Carrière longue | quatre étapes datées au mois, 2004, novembre 2012, septembre 2023, septembre 2026 ; la borne des vingt ans par génération | **certifiée** pour la règle générale de 2023 (L. 351-1-1, D. 351-1-1) ; les lignes par génération et celles de 2026 transcrites du II de l'article et de la circulaire Cnav 2026-17 |
| Trimestres accordés au titre des enfants | MDA à <!--chiffre:cellule(data/reference/legislation/majoration_duree_assurance.csv:trimestres_par_enfant?dispositif=mda&debut=1972)-->4<!--/--> puis <!--chiffre:cellule(data/reference/legislation/majoration_duree_assurance.csv:trimestres_par_enfant?dispositif=mda&debut=1975)-->8<!--/--> trimestres par enfant (1972, 1975) ; bonification de la fonction publique à <!--chiffre:cellule(data/reference/legislation/majoration_duree_assurance.csv:trimestres_par_enfant?dispositif=bonifications&debut=1900)-->4<!--/--> puis <!--chiffre:cellule(data/reference/legislation/majoration_duree_assurance.csv:trimestres_par_enfant?dispositif=bonifications&debut=2004)-->2<!--/--> (2004) | reprise des textes, non recontrôlée |
| Surcote parentale | <!--chiffre:cellule(data/reference/legislation/surcote_parentale.csv:taux_par_trimestre*100?debut=2023)-->1,25<!--/--> % par trimestre entre <!--chiffre:cellule(data/reference/legislation/surcote_parentale.csv:age_ouverture?debut=2023)-->63<!--/--> ans et l'âge légal, <!--chiffre:cellule(data/reference/legislation/surcote_parentale.csv:trimestres_maximum?debut=2023)-->4<!--/--> au plus | reprise des textes (L. 351-1-2-1), non recontrôlée |
| Durée requise par génération | table 1934-1975, <!--chiffre:cellule(data/reference/legislation/duree_assurance_requise.csv:trimestres?generation=1934)-->151<!--/--> → <!--chiffre:maximum(data/reference/legislation/duree_assurance_requise.csv:trimestres)-->172<!--/--> trimestres, suspension de 2026 comprise (<!--chiffre:cellule(data/reference/legislation/duree_assurance_requise.csv:trimestres?generation=1965)-->170<!--/--> pour 1964 et le premier trimestre 1965, <!--chiffre:cellule(data/reference/legislation/duree_assurance_requise.csv:trimestres?generation=1965.25)-->171<!--/--> jusqu'à fin 1965, <!--chiffre:cellule(data/reference/legislation/duree_assurance_requise.csv:trimestres?generation=1966)-->172<!--/--> dès 1966) | **certifiée** depuis 1953 (L. 161-17-3 réécrit par la loi de financement pour 2026, relu dans l'index LEGI à jour ; décrets pour 1953-1957) et pour 1934-1942 (R. 351-45) ; 1943-1952 transcrite |
| Durée de proratisation par génération | table 1900-1948, <!--chiffre:minimum(data/reference/legislation/duree_proratisation.csv:trimestres)-->150<!--/--> → <!--chiffre:maximum(data/reference/legislation/duree_proratisation.csv:trimestres)-->160<!--/--> trimestres | **certifiée** (R. 351-6 II) jusqu'à 1947 ; la ligne 1948 est la jonction avec la durée requise, que l'article ne fixe pas |
| Heures de SMIC pour valider un trimestre | <!--chiffre:cellule(data/reference/legislation/validation_trimestres.csv:heures?annee=1972)-->200<!--/--> depuis 1972, <!--chiffre:cellule(data/reference/legislation/validation_trimestres.csv:heures?annee=2014)-->150<!--/--> depuis 2014 | **certifiée** (R. 351-9) |
| Revalorisation des salaires portés au compte | <!--chiffre:distinctes(data/reference/legislation/revalorisation_salaires.csv:date_effet)-->10<!--/--> colonnes publiées, effets d'octobre 2017 à janvier 2026 | circulaires de la Cnav ; ailleurs, ancrage sur la plus proche |
| Âge légal par génération | table 1900-1975, <!--chiffre:minimum(data/reference/legislation/age_ouverture_requis.csv:age)-->60<!--/--> → <!--chiffre:maximum(data/reference/legislation/age_ouverture_requis.csv:age)-->64<!--/--> ans, suspension de 2026 comprise (<!--chiffre:cellule(data/reference/legislation/age_ouverture_requis.csv:age?generation=1965)-->62,75<!--/--> ans, soit neuf mois de plus que 62, de 1963 au premier trimestre 1965, un trimestre par génération ensuite, <!--chiffre:cellule(data/reference/legislation/age_ouverture_requis.csv:age?generation=1969)-->64<!--/--> ans dès 1969) | **certifié** (L. 161-17-2, qui porte la table depuis la loi de financement pour 2026, et D. 161-2-1-9 pour les générations qu'elle renvoie à sa rédaction antérieure), recontrôlé à chaque exécution sur l'index LEGI du dépôt, à jour des incréments quotidiens de la DILA |
| Surcote | barème daté trimestre par trimestre : <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=regime_general&debut=2004&rang_minimum=1)-->0,75<!--/--> % (2004-2006), <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=regime_general&debut=2007&rang_minimum=1&apres_65_ans=0)-->0,75<!--/--> % puis <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=regime_general&debut=2007&rang_minimum=5)-->1<!--/--> % à compter du cinquième et <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=regime_general&debut=2007&apres_65_ans=1)-->1,25<!--/--> % après <!--chiffre:tenu(test_le_bareme_2007_de_la_surcote_majore_au_dela_de_65_ans)-->65<!--/--> ans (2007-2008), <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=regime_general&debut=2009)-->1,25<!--/--> % (depuis 2009) ; fonction publique <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=fonction_publique&debut=2004)-->0,75<!--/--> % plafonné à <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:trimestres_maximum?bareme=fonction_publique&debut=2004)-->20<!--/--> trimestres puis <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=fonction_publique&debut=2009)-->1,25<!--/--> % ; période de référence au trimestre civil | transcrit de D. 351-1-4 et de L. 14 III, rejoué contre les trois exemples de la circulaire Cnav 2018-04 et deux fiches de service-public |
| Salaire annuel moyen des parents | 24 meilleures années pour un enfant, 23 pour deux et plus, pensions dès septembre 2026 | transcrit de R. 173-3-2 (décret n° 2026-699), non recontrôlé |
| Âge d'annulation de la décote par génération | table 1930-1955, <!--chiffre:minimum(data/reference/legislation/age_annulation_decote.csv:age)-->65<!--/--> → <!--chiffre:maximum(data/reference/legislation/age_annulation_decote.csv:age)-->67<!--/--> ans | calculée depuis l'âge d'ouverture certifié, selon la règle de `L. 351-8` ; recontrôlée à chaque exécution |
| Coefficient de minoration par génération | table 1900-1975, <!--chiffre:maximum(data/reference/legislation/coefficient_minoration.csv:coefficient*100)-->2,5<!--/--> → <!--chiffre:minimum(data/reference/legislation/coefficient_minoration.csv:coefficient*100)-->1,25<!--/--> % | **certifié** (R. 351-27 II), recoupé à la DREES |
| Années retenues au salaire de référence | table 1934-1948, <!--chiffre:minimum(data/reference/legislation/annees_salaire_reference.csv:annees)-->10<!--/--> → <!--chiffre:maximum(data/reference/legislation/annees_salaire_reference.csv:annees)-->25<!--/--> années | **certifiée** (R. 351-29-1) |
| Coefficients d'anticipation Agirc-Arrco | deux tables, 1 → 0,78 et 1 → 0,43 | barème publié par la caisse, saisi |
| Plafond de la majoration familiale Agirc-Arrco | <!--chiffre:partout(data/reference/regimes/complementaires_prive.yaml:regimes.*.periodes.*.plafond_majoration_enfants)-->2 367<!--/--> €/an (novembre 2025) | publié par la caisse, saisi |
| Garantie minimale de points de l'Agirc | <!--chiffre:partout(data/reference/regimes/complementaires_prive.yaml:regimes.*.periodes.*.points_minimum_annuels)-->120<!--/--> points par an, 1989-2018 | accord du 9 février 1988, saisi |
| Assiette de l'AVPF | SMIC annuel, <!--chiffre:tenu(test_l_avpf_porte_un_salaire_au_compte)-->1 820<!--/--> heures | principe sourcé, assiette déduite du SMIC |
| Droits ouverts par motif d'interruption | <!--chiffre:lignes_csv(data/reference/legislation/periodes_non_travaillees.csv)-->9<!--/--> motifs | principe sourcé, fractions non recontrôlées |

**Une règle a été appliquée partout : le montant SERVI prime sur la projection.**
Le minimum contributif, le minimum garanti et le minimum vieillesse sont trois
grandeurs que la loi ne fixe pas chaque année — elle les revalorise « comme les
pensions », c'est-à-dire selon une décision annuelle qui a été gelée en 2014 et
sous-indexée plusieurs fois depuis. Projeter une ancre sur l'indice des prix
donne donc, pour le minimum garanti de 2024, un montant supérieur de <!--chiffre:tenu(test_le_minimum_garanti_servi_est_sous_sa_projection)-->4,6<!--/--> % à
celui que l'État a payé. Les montants transcrits de leur publication, moins bien
sourcés, l'emportent sur les valeurs calculées depuis une ancre certifiée —
parce que les premiers disent ce qui a été payé et les seconds ce qui aurait dû
l'être.

## Écarts avec le droit positif dans le scénario 1

### Ce qui vient d'être refermé

**La liquidation unique des régimes alignés, servie depuis le 22 septembre
2026.** Depuis le 1er juillet 2017, un assuré né à compter de 1953 qui a
cotisé à deux des trois régimes alignés — régime général, salariés agricoles,
sécurité sociale des indépendants — reçoit UNE retraite de base : un revenu
annuel moyen formé de la somme des salaires et revenus d'une même année
civile, écrêtée au plafond, sur les vingt-cinq meilleures années, et une
proratisation qui tient compte de tous les trimestres des trois régimes
(`L. 173-1-2` et `R. 173-4-4-1`, 1° et 4°, CSS ; circulaire Cnav 2017/27 du
21 juillet 2017). Le modèle y arrivait à moitié, et par un autre chemin : il
réunit un régime et celui qui l'a ABSORBÉ, si bien que la CANCAVA, le RSI puis
le régime général ne faisaient qu'un pour un artisan, mais que les salariés
agricoles — dont le régime existe toujours — restaient à part. Une carrière
moitié privée moitié agricole, née en 1960 et partie à 64 ans, recevait deux
pensions de base, « SR 41 499 € × 88/167 » et « SR 29 069 € × 80/167 », là où
la caisse en calcule une seule : elle en reçoit maintenant une, « SR 40 749 €
× 167/167 », soit **20 629 € au lieu de 18 121 €** pour cette carrière-là. Et
la chaîne d'absorption datait le regroupement du régime général et des
indépendants de 2018, quand la loi le date du 1er juillet 2017 : une carrière
liquidée entre les deux était coupée en deux. Les deux conditions de la loi
sont désormais opposées, la seconde au MOIS près — une pension prenant effet
en janvier 2017 n'y a pas droit, celle de septembre oui. Aucun témoin n'a
bougé : la grille de cas types n'exerce qu'un statut à la fois, et la LURA ne
se voit que sur un polypensionné.

**Dix erreurs de calcul.**

- **Les trimestres pour enfants étaient servis huit par enfant, à tout le
  monde et de tout temps.** Le droit n'en a jamais servi autant. La majoration
  de durée d'assurance naît avec la loi du 31 décembre 1971, vaut un an par
  enfant jusqu'en 1974, deux ans ensuite, et va à la mère ; la fonction publique
  ne l'applique pas mais sert sa bonification, un an par enfant né avant 2004 et
  deux trimestres pour les enfants nés depuis. Trois conséquences chiffrées : un
  assuré liquidant en 1965 se voyait créditer de trimestres que la loi ne
  connaissait pas encore, un père de trois enfants recevait trois ans de durée
  d'assurance qui ne lui étaient pas dus — de quoi effacer une décote entière —,
  et une fonctionnaire mère de trois enfants en recevait vingt-quatre au lieu de
  douze. Les règles et leurs dates sont désormais dans
  `legislation/majoration_duree_assurance.csv`.
- **La surcote parentale n'existait pas dans le modèle.** C'est pourtant le
  dernier avantage familial créé par le droit, et la contrepartie directe du
  recul de l'âge légal : la loi du 14 avril 2023 a imposé une année de travail
  de plus à qui avait déjà sa durée requise à 63 ans, année que la surcote
  ordinaire ne récompense pas puisqu'elle ne compte qu'au-delà de l'âge légal.
  L'article L. 351-1-2-1 la paie 1,25 % par trimestre, quatre au plus, à qui
  détient au moins un trimestre de majoration pour enfants. Elle vaut jusqu'à
  5 % de pension, et le modèle servait zéro. Sa montée en charge suit l'âge
  légal de la génération : rien jusqu'à la génération 1964, un trimestre pour
  1965, quatre à partir de 1968.
- **La surcote était restée à 0,75 % jusqu'en 2010.** La loi de financement de
  la sécurité sociale pour 2009 l'a portée à 1,25 % par trimestre au 1er janvier
  2009 — deux années de liquidations recevaient donc une surcote deux tiers trop
  faible, au régime général comme dans la fonction publique. Le RSI, lui, servait
  1,25 % dès 2006, deux ans trop tôt.
- **La majoration de la loi Boulin était servie aux mères d'un enfant unique.**
  Le seuil de trois enfants du projet avait été abaissé à deux au cours du débat
  parlementaire, pas à un : jusqu'en 1974, une mère d'un enfant n'avait droit à
  rien.
- **Les régimes alignés n'appliquaient pas les règles familiales du régime
  général.** L'article L. 634-2 les leur donne depuis l'alignement de 1973 :
  une artisane, une commerçante n'avaient ni majoration de durée d'assurance ni
  majoration pour trois enfants.
- **Le salaire de référence ne portait pas sur les bonnes années.** Il balayait
  TOUTE la carrière, régimes confondus : un polypensionné passé de la fonction
  publique au privé liquidait sa pension civile sur son dernier salaire privé,
  pendant que le prorata de durée restait celui du régime. Sur un cas type
  d'agent SNCF passé au régime général, vingt pour cent de pension en trop.
  Chaque régime ne retient plus que les années qui lui ont été déclarées.
- **Les années postérieures à la liquidation cotisaient encore.** Huit années
  ajoutées après le départ faisaient passer une pension de 21 812 à 28 583 € et
  annulaient jusqu'à la décote de qui, précisément, part tôt.
- **Le minimum contributif était servi à des pensions décotées**, que l'article
  L. 351-10 réserve au taux plein. Il gonflait l'étalon de 20 % sur les petites
  pensions parties tôt — le segment même où se mesure l'écart avec le notionnel.
  Et sa majoration au titre des périodes cotisées était servie en tout ou rien,
  alors que le droit la proratise par la durée COTISÉE dans le régime quand le
  montant de base suit la durée d'assurance.
- **La cascade prenait le minimum et la majoration pour enfants à l'envers.**
  Les 10 % portaient sur une pension que le minimum n'avait pas encore relevée,
  et l'écrêtement de l'article L. 173-2 comparait au plafond un total qui
  incluait déjà la majoration, alors que le texte ne retient que les pensions
  personnelles.
- **La fonction publique subissait la décote du privé.** L'article L. 14 lui
  donne la sienne, et rien n'y coïncide : elle n'existe qu'à compter de 2006,
  son coefficient monte d'un huitième de point par an jusqu'en 2015, et son âge
  d'annulation n'est pas un âge en propre mais la limite d'âge du grade,
  diminuée d'un nombre de trimestres décroissant jusqu'en 2020. Un sédentaire
  liquidant en 2012 voyait sa décote s'annuler à 63 ans, pas à 67, et chaque
  trimestre manquant lui coûtait 0,875 %, pas 1,25 %.
- **Le taux plein par la durée est une création de 1982**, et le modèle
  l'appliquait depuis 1945. Le régime général servait 20 % à 60 ans majorés de
  quatre points par année différée, puis — loi Boulin — 25 % à 60 ans et 50 % à
  65 : aucune durée n'ouvrait le taux plein avant l'âge. La fiche ne portait
  d'ailleurs aucune minoration, et 40 % étaient servis à tout âge.

**Treize erreurs d'histoire**, trouvées en relisant les décrets de chaque
régime version par version dans la base LEGI, et en balayant le catalogue à
six générations. Chacune est racontée en détail au §4.

- **Le marin cotisait sur sa paie.** Le régime ne connaît que vingt salaires
  forfaitaires, un par catégorie de fonction à bord, publiés chaque année par
  arrêté : ils sont lus au Journal officiel depuis 2008, et le marin est rangé
  dans la catégorie la plus proche de son revenu, sur laquelle il cotise et
  liquide.
- **Avant 1967, le régime général cotisait 8,6 % sans texte.** La cotisation
  des assurances sociales est datée d'après le COR (6 + 6 en 1945, 6 + 10 en
  1947, 6 + 15 en 1966) et sa part vieillesse est la convention de 8,5/21 de
  l'ordonnance de 1967, nommée et marquée estimée.
- **La retenue des fonctionnaires passait à 8,9 % en 1990.** L'article 23 de
  la loi n° 89-18 la majore d'un point pour les traitements perçus après le
  31 décembre 1988.
- **Les points CARMF d'avant 1991 étaient servis un tiers trop bas.** Les
  statuts les affectent d'un coefficient de 1,33, que le moteur applique par
  une ligne d'échelle.

- **Trois régimes étaient fermés qui ne le sont pas, deux étaient ouverts qui
  ne le sont plus.** L'article 1<sup>er</sup> de la loi n° 2023-270 ferme aux
  recrutés du 1<sup>er</sup> septembre 2023 la RATP, les IEG, les clercs de
  notaires, la Banque de France et le CESE — et eux seuls. Le dépôt y ajoutait
  l'Opéra de Paris, la Comédie-Française et le port de Strasbourg, et laissait
  les clercs et la Banque de France ouverts. Un clerc entré en 2024 est un
  salarié du privé ; un danseur entré en 2024 est à la caisse de l'Opéra.
- **Le compte notionnel recevait une cotisation que personne n'a payée une
  seule année.** Les fiches du régime général, des salariés agricoles et des
  non-salariés portaient une moyenne par période législative — 11,19 % de 1972
  à 1982 — quand le droit cotisait 8,75 % en 1972 et 12,9 % en 1979. Le taux de
  chaque année est lu depuis 1967 dans `taux_cotisation_annuels.csv`.

- **Les régimes spéciaux décotaient de 1,25 % dès 2009.** Leur réforme de 2008
  ne donne aucune décote avant le 1<sup>er</sup> juillet 2010, puis un dixième du
  taux plein, et 1,25 % seulement en 2019. Un cheminot parti en 2011 perdait un
  quart de sa pension au lieu d'un quarantième.
- **La pension du mineur était de 75 % de son dernier salaire.** C'est un forfait
  par trimestre de service, le même pour l'abatteur et pour l'ingénieur : le
  modèle la doublait.
- **L'avocat d'avant 2004 recevait cent pour cent de son revenu moyen**, faute
  d'un montant forfaitaire dans la période, là où sa retraite de base est la même
  pour tous.
- **Le personnel navigant n'avait pas de décote**, alors que son code lui en
  donne une de 5 % par annuité manquante depuis 2012.
- **Le fonctionnaire cotisait à 7 % jusqu'en 2003.** L'article L. 61 porte 7,85 %
  depuis février 1991 et 8,9 % en 1989 et 1990 : un huitième de cotisation oublié pendant
  treize ans dans les comptes notionnels.
- **Le ministre du culte recevait une surcote depuis 1979**, vingt-cinq ans avant
  que la loi ne la crée.
- **Les assurés nés avant 1934 devaient 172 trimestres.** La table des durées
  requises commence à la génération 1934 et ne répondait pas en deçà : chaque
  fiche retombait alors sur sa durée d'aujourd'hui.

**Et trois régimes ont retrouvé leur histoire** : l'Opéra de Paris passe d'une
période à quatre — l'âge de la danse dépendait du sexe jusqu'en 2002, l'âge de
référence du ballet est de 42 ans —, la SEITA de une à huit, les mines de une à
vingt-deux.

**Cinq dispositifs déclarés mais jamais appliqués.** Les fiches de régime les
listaient et les *Neutralisations* annonçaient que les scénarios notionnels les
retiraient. On ne retire pas ce qui n'a jamais été mis.

- **Le minimum garanti** de l'article L. 17, plancher de la fonction publique.
- **Le minimum vieillesse**, dernier plancher du système et le seul qui ne
  suppose aucune cotisation.
- **L'AVPF**, qui distingue une période assimilée d'une période où la CNAF
  cotise : la première ne porte aucun salaire au compte, la seconde y porte le
  SMIC.
- **La garantie minimale de points** de l'Agirc, 120 points par an de 1989 à
  2018 même quand la tranche B est nulle.
- **Le départ anticipé pour carrière longue**, qui sert ici à répondre à une
  question que le modèle ne posait pas : le droit ouvre-t-il cette liquidation ?

**Et une question qui n'était pas posée.** Le modèle calculait une pension à
n'importe quel âge sans jamais dire si la loi ouvrait ce départ-là. Un salarié
né en 1965 y liquidait à 58 ans une pension décotée que le droit ne lui aurait
pas servie du tout. Le montant reste calculé — il faut comparer les trois
scénarios sur la même carrière — mais le résultat porte désormais un drapeau
`liquidation_ouverte`, et la restitution dit que ce montant ne décrit aucune
pension servie.

**Et trois choses que la datation des cas types ne lisait pas.** Un cas type
part à l'âge que sa règle propose (§5 ter), et la règle lisait le droit à
moitié. Elle comptait la durée sans les trimestres pour enfants : la mère de
deux enfants, qui a sa durée dès l'âge légal grâce à la majoration, était datée
jusqu'à un an et demi plus tard et partait en surcote — 61 ans et 6 mois pour la
génération 1950, 64 ans pour 1965, quand le droit sert la pension entière à 60
ans et à 63 ans et 3 mois. Elle ignorait la carrière longue, que le moteur
savait calculer comme une dérogation qu'on lui demande et non comme un âge
qu'il propose : le salarié au SMIC entré à dix-huit ans attendait l'âge légal —
62 ans pour 1955, 63 ans et 3 mois pour 1965 — alors que la loi lui ouvre 60
puis 62 ans au taux plein. Et la condition d'entrée précoce de la carrière
longue demandait cinq trimestres à tout le monde, quand l'article D. 351-1-1
n'en demande que quatre à qui est né au dernier trimestre de l'année civile :
le modèle ne connaissait que l'année de naissance quand la table a été écrite,
il lit le mois depuis. Les deux premières ne touchent que la datation, donc les
pages Cas types et Coût ; la troisième touche `motif_ouverture` lui-même, mais
aucun des 484 témoins de simulation ne porte une carrière née d'octobre à
décembre dont la porte en dépende. Ce que ça déplace : le SMIC part à 60 ans
pour les générations 1950 à 1960 et à 62 ans à partir de 1962, la carrière
interrompue à l'âge légal de sa génération, l'agent de conduite né en 2000 —
rendu au régime général par la fermeture du statut — à 63 ans par la porte des
vingt et un ans ; la trajectoire du système actuel en 2070 passe de 19,3 % à
19,5 % du PIB, l'écart avec le COR de 5,1 à 5,3 points — puis à 19,4 % et
5,2 points une fois la suspension de 2026 portée, ci-dessous.

**Et ce que les exemples publiés par les caisses ont fait voir, le même
jour.** L'action 26 de la feuille de route rejoue contre le scénario 1 les
exemples chiffrés que service-public.gouv.fr et les circulaires de la Cnav
publient — la seule confrontation qui soit officielle et reproductible,
puisqu'aucun simulateur officiel ne se laisse interroger sans FranceConnect.
Le premier exemple lu disait « né en 1964, 62 ans et 9 mois, 170 trimestres »
là où les tables du dépôt, certifiées sur le dump LEGI du 13 juillet 2025,
portaient 63 ans et 171. Cinq écarts, tous refermés :

- **La suspension de la réforme de 2023** (loi n° 2025-1403 du 30 décembre
  2025, article 105, décrets n° 2026-344 et n° 2026-345 du 7 mai 2026,
  pensions prenant effet à compter du 1er septembre 2026) manquait : 62 ans et
  9 mois et 170 trimestres des nés du 1er janvier 1963 au 31 mars 1965, puis
  un trimestre de moins que la loi de 2023 pour chaque génération jusqu'à
  64 ans à compter de 1969 et 172 trimestres à compter de 1966. C'est le
  droit de tous ceux qui simulent aujourd'hui leur départ. Les âges de la
  catégorie active et de la super-active suivent (décret n° 2026-344,
  article 3, D), comme la carrière longue.
- **La carrière longue se lisait à l'année et à la règle générale.** La borne
  des vingt ans monte par génération depuis 2023 (D. 351-1-1, II) — 60 ans
  et 9 mois pour la génération 1965, non 62 —, et chaque décret s'applique
  aux pensions prenant effet à compter d'une date, novembre 2012, septembre
  2023, septembre 2026 : la table porte maintenant la date et la génération.
  Et depuis septembre 2026 deux trimestres de majoration pour enfants sont
  réputés cotisés (3° de l'article L. 351-1-1, article 104 de la même loi,
  décret n° 2026-700 du 29 juillet 2026, circulaire Cnav 2026-29).
- **Le salaire annuel moyen des parents** porte sur les vingt-quatre
  meilleures années pour un enfant, vingt-trois pour deux et plus (R. 173-3-2,
  décret n° 2026-699 du 29 juillet 2026, pensions dès septembre 2026). Le
  modèle en prenait vingt-cinq à tout le monde.
- **La surcote était servie au taux de l'année du départ, à tous les
  trimestres, et comptée à l'année.** Le droit donne à chaque trimestre le
  taux en vigueur quand il a été accompli — 0,75 % de 2004 à 2006, 0,75 %
  puis 1 % à compter du cinquième et 1,25 % après soixante-cinq ans en 2007
  et 2008, 1,25 % depuis 2009 (D. 351-1-4 ; fonction publique : 0,75 % dans la
  limite de vingt trimestres puis 1,25 %, L. 14 III) —, et il ne compte que
  les trimestres civils entiers depuis celui qui suit l'âge légal (circulaire
  Cnav 2018-04, point 2). Né le 15 avril, à l'âge légal en avril, on ne
  surcote qu'à partir de juillet : le modèle comptait avril, et servait un
  trimestre de trop à qui n'est pas né le premier jour d'un trimestre. Le
  barème vit dans `legislation/surcote_baremes.csv`.
- **Le même jour, la datation des cas types ignorait encore la génération
  de la carrière longue** : c'est la table ci-dessus qui la lui donne.

Vingt-deux exemples sont rejoués à l'identique par `tests/test_oracle.py`
depuis `tests/temoins/exemples_officiels.yaml` : décote, surcote, taux plein
et proratisation, minimum contributif de 2026, âges légaux et durées de la
circulaire Cnav 2026-07, carrière longue de la circulaire 2026-17, les trois
barèmes de surcote de la circulaire 2018-04, dans le privé comme dans la
fonction publique. Ce que ça déplace, et pourquoi, est au § 3, « Ce que disent
les exemples publiés par les caisses ».

### Le mois, là où le droit le date

Le modèle travaillait à l'année, et arrondissait l'âge de liquidation à l'année
civile la plus proche. Ce n'était pas une imprécision de détail.

**Ce que l'arrondi coûtait.** Cadre du privé né en 1962, entré à 22 ans, payé
1,5 fois le salaire moyen : entre un départ à 64 ans et 5 mois et un départ à
64 ans et 7 mois, la pension du scénario 1 sautait de 39 265 € à 41 826 €
(**+6,5 %**) et celle du scénario 3 tombait de 39 265 € à 36 479 €
(**−7,1 %**). Deux mois d'écart, sept points de pension, dans les deux sens
selon le scénario — et davantage que la plupart des effets que ce document
mesure au centième. À l'intérieur de chaque demi-année, à l'inverse, le
scénario 1 ne bougeait pas d'un centime : il ignorait le mois quand le
scénario 2 y répondait par son diviseur, si bien que les comparer à 64 ans et
3 mois confrontait une pension calculée *comme si* 64 ans à une pension calculée
à 64,25. L'arrondi de Python étant AU PAIR, il dépendait de surcroît de la
parité du millésime : deux assurés déclarant « soixante-quatre ans et six mois »
étaient traités différemment selon leur génération.

**Où le mois entre désormais.** Là, et seulement là, où le réel porte une date.

| | Ce que le mois change |
|---|---|
| Date de liquidation | `naissance + âge` se compte en mois : né en mars 1962, parti à 64 ans et 6 mois, on liquide en septembre 2026 |
| Année du départ | Elle est portée au compte **au prorata de ses mois**, plafond de la Sécurité sociale proratisé comme le veut R. 242-2. Elle valait zéro ou douze mois selon l'arrondi |
| Trimestres de cette année-là | Plafonnés aux trimestres **civils écoulés** avant le point de départ (R. 351-9) : trois mois de travail n'en valident qu'un |
| Année d'entrée dans la vie active | Incomplète elle aussi, et traitée de même |
| Diviseur actuariel | Lu à la DATE exacte — âge et millésime —, force de mortalité supposée constante dans chaque cellule (âge entier × millésime). Il ne lisait que l'âge entier là où les quotients sont observés : **1,7 % de pension d'un coup à chaque anniversaire**, et rien entre deux |
| Taux de remplacement | Rapporté au dernier revenu **annualisé** : l'année du départ ne porte que ses mois, et la rapporter telle quelle doublait le taux |
| Revalorisation des salaires portés au compte | La circulaire applicable est celle en vigueur **à la date** de liquidation — 3,9 % d'écart au second semestre 2022 |
| Générations coupées par un texte | 1<sup>er</sup> juillet 1951, 1<sup>er</sup> septembre 1961 : les tables portent deux lignes, lues au mois de naissance |
| Traitement des six derniers mois | Celui **en vigueur au départ**, annualisé, et non celui de la dernière année pleine |

**Et la coupure de septembre tombait à côté d'un mois, sans que rien ne le
dise.** Une génération s'écrit ici en années décimales, et les tables écrivent
le 1<sup>er</sup> septembre `1961.667` — trois décimales, comme le veut leur
convention. Huit douzièmes valent 1961,666 666… Le premier étant plus grand que
le second, la lecture en escalier rendait à l'assuré né en SEPTEMBRE 1961 la
marche d'août : **168 trimestres au lieu de 169, et un âge d'ouverture de
62 ans au lieu de 62 ans et trois mois** — pour le mois-même que la loi du
14 avril 2023 désigne, et pour un douzième de la génération. Le même trou
s'ouvrait sur `1963.667` de la carrière longue, sur `1966.667` et `1971.667` de
la catégorie active, et sur `1971.667` de la jouissance militaire. La
génération est désormais lue à la précision où les tables sont écrites, ce qui
le referme des deux côtés du portage. Corrigé le 22 septembre 2026.

**Une exposition n'est pas une interpolation.** Le diviseur mélange deux
dimensions — l'âge et le millésime de la table —, et la seconde a d'abord été
laissée en escalier, au motif qu'une table de mortalité est publiée par année
civile. C'était une erreur, et elle se voyait : l'âge avançait mois par mois
quand l'année sautait d'un bloc au 1<sup>er</sup> janvier, si bien que le
diviseur **remontait** à cette date et que partir un mois plus tard rallongeait
la durée de service attendue. Le rentier parti en juillet 2038 ne passe pas son
année de rente sous le seul millésime 2038 : il en passe la moitié sous 2039.
Découper son trajet à ses deux franchissements — son anniversaire, puis le
1<sup>er</sup> janvier — et donner à chaque tronçon la force de mortalité de la
cellule qu'il traverse, ce n'est pas inventer une tendance infra-annuelle :
c'est répartir l'EXPOSITION entre deux tables publiées. Le diviseur décroît
depuis lors de mois en mois, sans marche ni remontée.

**Ce qui reste annuel, et doit le rester.** Le pas du moteur n'a pas changé,
parce que les données ne l'ont pas. Un salaire est déclaré à l'année, le salaire
moyen par tête est une moyenne annuelle, l'indice des prix retenu est annuel, le
plafond est fixé pour l'année, un quotient de mortalité est publié par âge
entier et par millésime. Découper ces grandeurs en douze demanderait de
supposer une répartition — uniforme, faute de mieux —, et cette supposition
**redonne exactement le total annuel** : le résultat serait identique au
centime, sauf aux bords, c'est-à-dire là où le mois entre déjà. Le seul effet
d'un pas mensuel généralisé serait donc d'afficher des décimales que la source
ne porte pas, et de faire descendre au niveau `estimee` des séries aujourd'hui
certifiées. C'est la règle du dépôt : **interpoler ce que le réel a de continu,
laisser en escalier ce qu'il a de daté.** L'âge au décès est continu — on
l'interpole. Une circulaire prend effet à une date — on la lit à sa date. Un
salaire annuel est un total — on ne le découpe pas.

**Une marche demeure, et elle est dans la loi.** L'article R. 351-29 écarte du
salaire annuel moyen les salaires de l'année du point de départ. Qui part en
décembre perd donc onze mois de salaire de son SAM, quand celui qui part au
1<sup>er</sup> janvier suivant les y fait entrer en entier : sur le cas ci-dessus,
**+2,9 % en un mois**. Ce n'est pas un artefact du modèle — c'est le droit, et c'est
la raison pour laquelle les caisses conseillent de liquider au 1<sup>er</sup>
janvier. Les trimestres de cette même année, eux, comptent bien : ce sont deux
règles distinctes, et le modèle les applique séparément.

**L'année du changement de métier relève d'un seul régime.** Une carrière se
décrit comme une suite de métiers, et la maille annuelle vaut ici comme
ailleurs : le moteur ne connaît qu'une ligne, donc **un statut**, par année
civile. L'année d'un changement revient donc au métier qui en occupe le plus de
mois — à égalité, à celui qui l'ouvre —, et ses cotisations sont calculées au
barème de ce seul régime plutôt qu'au barème partagé des deux. Le **revenu**,
lui, reste la somme de ce que les deux métiers ont réellement payé, au prorata
de leurs mois : c'est le montant porté au compte qui est juste, c'est le taux
qui lui est appliqué qui est approché. L'écart ne porte que sur une année par
changement, et il est nul quand le changement tombe au 1<sup>er</sup> janvier —
c'est-à-dire quand l'assuré est né en janvier et change à un âge entier. Le
séparer demanderait de scinder l'année en deux lignes, ce que le reste du
modèle — salaire de référence, plafond, trimestres, proratisation — ne sait pas
lire, et ce que le relevé de carrière lui-même ne porte pas.

**L'année où l'activité s'arrête relève de la même convention.** Une carrière
ne s'arrête pas toujours au mois du départ : on peut cesser de travailler à
58 ans et liquider à 64. Le formulaire le dit par une ligne de carrière qui
n'est pas un emploi — chômage indemnisé ou non, maladie, invalidité, élever un
enfant, service militaire, inactivité —, bornée au mois comme les autres. Le
moteur, lui, ne connaît qu'un statut par année civile : l'année où l'activité
s'arrête revient donc à ce qui en occupe le plus de mois, et à égalité elle
reste travaillée. Une interruption de moins de la moitié d'une année civile
n'est ainsi pas vue si elle ne déborde pas sur la suivante ; le champ
« Interruptions » des options de modélisation, qui désigne les années une à
une, reste l'outil fin, et il garde le dernier mot sur les lignes.

### Ce qui reste hors du modèle, et pourquoi

Ces lignes ne sont pas des oublis : chacune demande une information que le
modèle n'a pas, ou décrit un dispositif qu'il représenterait faussement.

- **Pension de réversion.** Elle ne concerne pas l'assuré mais son conjoint
  survivant, et suppose de connaître un ménage. Hors périmètre par
  construction : le modèle décrit une carrière, pas une famille.
- **Les revalorisations servies APRÈS la liquidation.** Le moteur s'arrête au
  jour du départ : il calcule la pension du premier mois et ne suit aucune des
  revalorisations qu'un retraité a reçues depuis. La page l'exprime en euros
  constants de l'année de référence, ce qui rend le montant comparable aux prix
  d'aujourd'hui — mais par le CHEMIN DES PRIX, non par celui des arrêtés. Or le
  droit indexe les pensions servies sur les prix : les deux chemins coïncident,
  à ceci près que plusieurs années ont été sous-indexées par décision expresse
  — gels et revalorisations partielles —, et le modèle ne les reprend pas. La
  conséquence se voit sur la saisie par la pension, où c'est cette convention
  qui autorise un retraité à taper le montant qu'il touche aujourd'hui. Ce
  montant est un peu plus bas que sa première pension revalorisée sur les prix,
  puisque les pensions ont décroché des prix ces années-là ; la page vise donc
  une cible un peu trop basse, et le revenu d'activité qu'elle en déduit est
  un peu plus bas que celui qui a réellement été gagné. Servir la vraie trajectoire
  demanderait la série des coefficients réellement appliqués aux pensions,
  lue dans les arrêtés ; le dépôt porte celle des salaires portés au compte,
  qui n'est pas la même chose.
- **La troisième condition de la liquidation unique des régimes alignés.** La
  LURA elle-même est servie depuis le 22 septembre 2026 — voir plus bas —, et
  ses deux premières conditions sont opposées : la génération, la date d'effet
  au mois près. La troisième ne l'est pas : la loi écarte la LURA de qui avait
  DÉJÀ obtenu, avant le 1er juillet 2017, une retraite de même nature dans
  l'un des trois régimes. Une carrière du dépôt liquide tout à la fois, et ne
  peut donc pas porter ce cas. De même, le revenu annuel moyen de la LURA
  additionne les salaires et revenus d'une MÊME année civile avant de les
  écrêter au plafond : une carrière du dépôt n'exerce qu'un métier à la fois,
  et la somme n'a jamais lieu.
- **Bonifications de service.** Bonifications de dépaysement, de campagne
  militaire, du cinquième pour les emplois de sécurité. La bonification POUR
  ENFANTS, elle, est servie : elle ne demande que le nombre d'enfants. Les
  autres supposent de connaître le CORPS d'appartenance et le détail des
  services, que la saisie ne demande pas.
- **Catégorie active : servie, mais sur un classement déclaré.** L'âge anticipé
  de l'article L. 24 — 57 ans, 52 pour la super-active, 59 et 54 après la
  réforme de 2023 — est désormais opposé, ainsi que l'âge d'annulation de décote
  propre au classement (62 et 57 ans), la condition de durée de services
  classés (17 et 27 ans) et, depuis le 22 septembre 2026, la DURÉE REQUISE
  propre aux emplois classés : l'accélération de 2023 ne s'y applique pas à la
  date où elle s'applique aux autres, et le B du XXIV de l'article 10 de la loi
  n° 2023-270 leur oppose 169 trimestres des nés du 1er septembre 1966 à 1967
  contre 172 en droit commun, 170 jusqu'au 31 mars 1970, 171 jusqu'à la fin de
  1970, 172 ensuite — cinq ans plus tard pour la super-active. Ce qui reste hors
  du modèle est le CLASSEMENT lui-même : il tient à l'emploi occupé, qu'aucune donnée de carrière ne révèle,
  et c'est donc l'assuré qui le déclare en choisissant l'un des cinq statuts
  classés. Qui se trompe de statut se trompe d'âge. La table ne porte par
  ailleurs qu'une durée par classement — 17 ans en active, 27 en super-active :
  les 17 années des ingénieurs du contrôle de la navigation aérienne et les 32
  des égoutiers et des identificateurs de l'institut médico-légal ne sont pas
  distinguées, faute d'un corps déclaré.
- **Pension militaire : la durée est servie, le grade ne l'est pas.** Les deux
  statuts militaires opposent la durée de services qui ouvre la pension —
  17 ans pour un non-officier, 27 pour un officier, 15 et 25 avant la loi du
  9 novembre 2010 —, l'âge de jouissance différée de l'article L. 25 et la
  décote propre du II de l'article L. 14, plafonnée à dix trimestres. Restent
  dehors : la LIMITE D'ÂGE DE GRADE, qui ouvre la pension quelle que soit la
  durée accomplie et qui sert d'âge d'annulation de la décote au militaire
  liquidant à 52 ans ou plus (L. 14 bis, 4°) — le modèle ne connaît pas le
  grade et applique donc à tous le barème du II —, et la limite de durée de
  services, qui l'ouvre de la même façon. Conséquence : un officier supérieur
  radié par limite d'âge peut être déclaré non ouvert quand le droit l'ouvre, et
  la décote d'un militaire parti très tôt est au plus de 12,5 %, jamais de 25 %.
- **Pension majorée de référence (PMR)** du régime des non-salariés agricoles.
  Le régime agricole est déjà le plus approché du catalogue — sa part
  forfaitaire, sa complémentaire obligatoire et ses valeurs de point ne sont que
  partiellement sourcées. Ajouter la PMR sur ce socle donnerait un chiffre plus
  précis d'apparence et pas davantage de vérité.
- **Coefficients de solidarité et majorants de l'Agirc-Arrco.** Le malus de
  10 % pendant trois ans, et le bonus de 10, 20 ou 30 % pendant un an, ne
  s'appliquent qu'aux pensions prenant effet entre le 1er janvier 2019 et le
  30 novembre 2023 : le dispositif est éteint. Surtout, leur effet est
  TEMPORAIRE, quand le modèle ne calcule qu'une pension annuelle unique.
  L'appliquer à titre permanent créerait une erreur nouvelle, plus grande que
  celle qu'il corrigerait.
- **Pénibilité, invalidité, inaptitude, handicap.** Quatre autres portes du
  départ anticipé, qui demandent des informations médicales ou
  professionnelles que le modèle ne collecte pas. Un assuré qui en relèverait
  est ici déclaré « non ouvert » alors que le droit l'ouvrirait, et subit une
  décote dont le droit le dispenserait.
- **Trimestres « réputés cotisés » de la carrière longue : deux cas sur sept.**
  Les six enveloppes de l'article D. 351-1-2 sont servies depuis le
  22 septembre 2026 — service national, incapacité temporaire, chômage
  indemnisé, maternité, invalidité, assurance vieillesse des parents au foyer —,
  chacune sous sa limite. Restent dehors le 6° du I, majoration de durée
  d'assurance du compte professionnel de prévention, que le modèle ne calcule
  pas, et la part du 7° qui vise les fonctionnaires affiliés à un régime spécial
  tout en remplissant les conditions de L. 381-1, qu'il ne distingue pas. Reste
  aussi une lecture qui manque : l'article D. 351-1-3 pose la condition de DÉBUT
  d'activité sur une « durée d'assurance » de cinq trimestres, quand le modèle
  n'y compte que les trimestres cotisés — plus dur que la lettre du décret, en
  attendant la circulaire qui l'applique.
- **La date d'effet est le mois de l'anniversaire.** Le modèle liquide au mois
  où l'âge demandé est atteint ; la caisse fait prendre effet la pension le
  premier jour du mois SUIVANT, sauf pour qui est né un premier. Un mois
  d'écart, qui se voit là où un texte coupe au mois : la borne de la carrière
  longue des nés en décembre 1965, fixée à 60 ans et 8 mois pour que la
  pension prenne effet le 1er septembre 2026, tombe ici en août 2026, sous le
  décret précédent, qui demande 60 ans et 9 mois.
- **La durée requise des emplois classés : servie, sauf le C.** Le XXIV, B de
  l'article 10 de la loi du 14 avril 2023 pour l'État, et le II, B de l'article
  13 du décret n° 2023-435 pour la CNRACL et le FSPOEIE, donnent aux catégories
  actives leur propre calendrier de durée — 169 trimestres des nés de septembre
  1966 à 1967, 172 dès 1971, les mêmes marches cinq ans plus tard pour la
  super-active —, et `categorie_active.csv` le porte depuis le 22 septembre
  2026, ancienne table comprise pour les générations d'avant. Reste dehors le C
  du même XXIV : la durée des fonctionnaires civils et des militaires qui
  liquident avant soixante ans SANS être classés, 169 trimestres puis un de plus
  au 1er janvier 2025 et au 1er janvier 2027. Ceux-là se voient encore opposer
  la durée de leur génération.
- **Ce qui compte en services dans les régimes spéciaux.** La pension des
  dix-huit régimes spéciaux du catalogue se proratise, comme celle de la
  fonction publique, sur des services et non sur une durée d'assurance ; mais
  ce que chacun retient comme service tient à son propre règlement, et aucun
  n'a été lu. La règle tirée des articles L. 5 et L. 9 du code des pensions —
  le chômage n'ouvre aucun service, les congés de maladie et de maternité en
  ouvrent, le congé parental dans la limite de trois ans par enfant — ne
  s'applique donc qu'à la famille `fonction_publique`. Partout ailleurs, une
  interruption qui valide des trimestres continue d'entrer au prorata, ce qui
  surestime la pension d'un agent de régime spécial à carrière hachée.
- **Montée en charge propre aux régimes spéciaux.** La décote créée par la
  réforme de 2008 y monte en charge comme celle de la fonction publique, mais
  selon un calendrier qui lui est propre, régime par régime. Le modèle applique
  d'emblée le coefficient plein à partir de la date d'entrée en vigueur portée
  par chaque fiche.
- **Année de naissance des enfants.** Le modèle ne la collecte pas : il présume
  les enfants nés aux trente ans de leur mère, l'âge moyen des mères à
  l'accouchement. La convention ne déplace qu'une chose, la bascule des quatre
  aux deux trimestres de la fonction publique, qui tombe ainsi sur les
  générations nées à partir de 1974. Elle ne peut pas non plus savoir si les
  parents ont attribué au père les quatre trimestres d'éducation ouverts en
  2010, ni si un père fonctionnaire a interrompu son activité les deux mois
  qu'exige la bonification depuis 2003 : dans les deux cas le modèle retient
  l'attribution par défaut, celle de la mère.
- **Montée en charge des bonifications dans les régimes spéciaux.** Ils suivent
  ici le calendrier de la fonction publique — un an par enfant né avant 2004 —
  quand leurs propres réformes sont de 2008. La documentation de la CNRACL
  donne, pour la RATP, une bonification d'un an jusqu'aux enfants nés le
  30 juin 2008 puis deux trimestres, et pour la SNCF deux trimestres depuis le
  décret du 30 juin 2008 ; pour les IEG, la bascule est en revanche datée de
  2004 comme dans la fonction publique. Trois calendriers pour trois régimes,
  qu'aucune source ne donne en série : le modèle retient le seul qui soit
  documenté article par article, celui de la fonction publique.
- **Majorations pour enfants des non-salariés agricoles.** La MSA sert bien une
  majoration de durée d'assurance à ses non-salariés, mais elle s'y convertit en
  POINTS et non en trimestres, selon une règle qui change au 1er janvier 2026.
  Le régime des exploitants étant déjà le plus approché du catalogue, la porter
  ici donnerait un chiffre plus précis d'apparence et pas davantage de vérité.
- **Un ménage, un patrimoine, des ressources.** Le minimum vieillesse est servi
  sous le barème d'une personne seule sans autre ressource — le cas le plus
  favorable — et à tous, alors que la DREES estime le non-recours à la moitié
  des ayants droit. C'est pourquoi il apparaît toujours comme une ligne séparée
  de la cascade, et pourquoi un paramètre le retire d'un seul geste.

## 1. État de certification des données

La page **Données** du site affiche l'état exact, et date chaque série du jour
où elle a été relue contre sa source (`verifiee_le` dans le journal, §6). En
résumé :

| Donnée | Période | Niveau | Source |
|---|---|---|---|
| Inflation (IPC) | <!--chiffre:minimum(data/reference/macro/ipc_annuel.csv:annee?fiabilite=certifiee)-->1950<!--/-->-<!--chiffre:maximum(data/reference/macro/ipc_annuel.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, idbanks 000008965 et 001764363 |
| Inflation | <!--chiffre:minimum(data/reference/macro/ipc_annuel.csv:annee?fiabilite=estimee)-->1930<!--/-->-<!--chiffre:maximum(data/reference/macro/ipc_annuel.csv:annee?fiabilite=estimee)-->1949<!--/--> | estimée | reconstitution, dérive cumulée recoupée à l'INSEE idbank 010605954 (1901-) |
| Salaire moyen par tête | <!--chiffre:minimum(data/reference/macro/salaire_moyen.csv:annee?fiabilite=certifiee)-->1950<!--/-->-<!--chiffre:maximum(data/reference/macro/salaire_moyen.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, idbanks 011785411 et 011793486 |
| Salaire moyen par tête | <!--chiffre:minimum(data/reference/macro/salaire_moyen.csv:annee?fiabilite=estimee)-->1930<!--/-->-<!--chiffre:maximum(data/reference/macro/salaire_moyen.csv:annee?fiabilite=estimee)-->1949<!--/--> | estimée | reconstitution |
| Productivité réelle | <!--chiffre:minimum(data/reference/macro/productivite.csv:annee?fiabilite=certifiee)-->1950<!--/-->-<!--chiffre:maximum(data/reference/macro/productivite.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, idbanks 011785223 et 011793334 |
| Productivité réelle | <!--chiffre:minimum(data/reference/macro/productivite.csv:annee?fiabilite=estimee)-->1930<!--/-->-<!--chiffre:maximum(data/reference/macro/productivite.csv:annee?fiabilite=estimee)-->1949<!--/--> | estimée | reconstitution |
| Produit intérieur brut, en niveau | <!--chiffre:minimum(data/reference/macro/pib_courant.csv:annee?fiabilite=certifiee)-->1949<!--/-->-<!--chiffre:maximum(data/reference/macro/pib_courant.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, idbank 011779992 |
| Profil de salaire par tranche d'âge | <!--chiffre:minimum(data/reference/macro/profil_salaire_age.csv:annee?fiabilite=certifiee)-->1962<!--/-->-<!--chiffre:maximum(data/reference/macro/profil_salaire_age.csv:annee?fiabilite=certifiee)-->2024<!--/--> | **certifiée** | INSEE Melodi, DS_DERA_PRIVE_SERIES_LONGUES |
| Profil de salaire par âge et catégorie | 2024 | **certifiée** | INSEE Melodi, DS_DERA_PRIVE_ANNUEL |
| Profil de salaire public par âge et statut | 2023 | **certifiée** | INSEE Melodi, DS_DERA_PUBLIC_ANNUEL |
| Profil de salaire par âge et secteur | 2018, 2022 | **certifiée** | Eurostat, enquête sur la structure des salaires |
| Population par âge, 50 ans et plus | <!--chiffre:minimum(data/reference/macro/population_par_age.csv:annee?fiabilite=certifiee)-->1962<!--/-->-<!--chiffre:maximum(data/reference/macro/population_par_age.csv:annee?fiabilite=certifiee)-->2023<!--/--> | **certifiée** | INSEE, estimations de population (classeur des projections 2026) |
| Population par âge, 50 ans et plus | <!--chiffre:minimum(data/reference/macro/population_par_age.csv:annee?fiabilite=projetee)-->2024<!--/-->-<!--chiffre:maximum(data/reference/macro/population_par_age.csv:annee?fiabilite=projetee)-->2070<!--/--> | projetée | INSEE, projections de population 2026, scénario central |
| Population des 20-64 ans | 1962-2023 / 2024-2070 | **certifiée** / projetée | mêmes sources |
| Dépenses de vieillesse-survie, tous régimes | <!--chiffre:minimum(data/reference/macro/depenses_retraite.csv:annee?fiabilite=certifiee)-->1959<!--/-->-<!--chiffre:maximum(data/reference/macro/depenses_retraite.csv:annee?fiabilite=certifiee)-->2024<!--/--> | **certifiée** | DREES, Comptes de la protection sociale, poste E11-2 |
| Dépenses de vieillesse-survie, par système | <!--chiffre:minimum(data/reference/macro/depenses_retraite_regimes.csv:annee?fiabilite=certifiee)-->1990<!--/-->-<!--chiffre:maximum(data/reference/macro/depenses_retraite_regimes.csv:annee?fiabilite=certifiee)-->2024<!--/--> | **certifiée** | DREES, mêmes comptes, ventilation par organisme |
| Dépenses de vieillesse-survie, par système | 1981-1989 | absentes | nomenclature d'alors sans raccord publié — voir §5 bis |
| Retraités de droit direct, par caisse | 2004-2024, 28 caisses | **certifiée** | DREES, enquête annuelle auprès des caisses de retraite, fichier diffusé |
| Retraités de droit direct, par caisse | hors 2004-2024 | estimée | la répartition du bord est reconduite — voir §5 bis |
| Distribution des pensions mensuelles brutes de droit direct | fin 2020, 46 tranches | **certifiée** | DREES, échantillon interrégimes de retraités 2020, tableau 1 |
| Patrimoine des ménages : déciles, moyennes et médianes par âge | début 2021 et début 2024 | **haute** | INSEE, enquête Histoire de vie et Patrimoine, Insee Focus n° 287 et page « Distribution du patrimoine des ménages », classeurs lus par script |
| Mode de résidence après 65 ans, par âge et par sexe | 2021, 36 âges | **haute** | INSEE, recensement 2021, *Insee Première* n° 2040, figure 2, classeur lu par script |
| Patrimoine des ménages retraités selon leur revenu disponible | 2018, six valeurs | **saisie** | COR, « Le patrimoine des retraités », séance du 16 décembre 2021, sur l'enquête Patrimoine 2018 — les graphiques du PDF ne se lisent pas |
| Hypothèses de projection | 2026-2100 | **saisie** | COR, rapport annuel de juin 2025, jeu reconduit en juin 2026 |
| Emploi projeté (croissance de l'emploi, dérivée) | 2026-2070 | **saisie** | COR, rapport annuel de juin 2026, données de la partie 1 : population active et chômage du scénario de référence |
| Espérance de vie à 0 et 60 ans | <!--chiffre:minimum(data/reference/mortalite/esperances_vie.csv:annee?mesure=e0&fiabilite=certifiee)-->1946<!--/-->-<!--chiffre:maximum(data/reference/mortalite/esperances_vie.csv:annee?mesure=e0&fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, quatre idbanks, annuel par sexe |
| Espérance de vie à 65 ans | 1960-2024 | **certifiée** | OCDE `DSD_HEALTH_STAT@DF_LE` |
| Espérance de vie à 65 ans | 1946-1959 | haute | **dérivée** des quotients INED, recalculée à chaque exécution |
| Espérances de vie e0, e60, e65 | 2026-2125 | projetée | **dérivée** des quotients projetés par l'INSEE, projections 2026 |
| Espérance de vie par vingtile de niveau de vie, e0, e60, e65 | 2012-2016 et 2020-2024 | haute | INSEE, tables de mortalité par niveau de vie (Insee Résultats 2025), lues telles quelles, l'ensemble contrôlé contre la série certifiée |
| Espérance de vie à 65 ans des fonctionnaires civils de l'État | 2024 | **saisie** | Service des retraites de l'État, PAP 741 du PLF 2026, apporté par l'utilisateur |
| Quotients de mortalité par âge | 1986-2024 | **certifiée** | Eurostat `demo_mlifetable`, âges 0-94 |
| Quotients de mortalité par âge | 1899-1985 | **certifiée** | INED, tables de Vallin et Meslé, âges 0-104 |
| Quotients de mortalité par âge | 1986-1997, 95 à 104 ans | **certifiée** | INED, là où Eurostat s'arrête |
| Quotients de mortalité par âge | après 1997, au-delà de 94 ans | absents | calibration paramétrique, dont le biais est mesuré |
| Minimum contributif et plafond d'écrêtement | ancres de 2007 à 2014 | **certifiée** | DILA, base LEGI, code de la sécurité sociale |
| Minimum contributif, minimum majoré et plafond | montants servis 2020 | haute | transcrits d'une réponse ministérielle, recoupés à chaque exécution contre les circulaires Cnav que transcrit OpenFisca-France-Pension — sa série s'arrête en 2023, les montants postérieurs restent sans recoupement |
| Minimum vieillesse (ASPA) | ancres 2006, 2009-2012, 2014, 2018-2020 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 815-1` |
| Minimum vieillesse (ASPA) | ancres 2007, 2016, 2017, depuis 2021 | haute / moyenne | publications — l'article n'est pas réécrit à chaque revalorisation |
| Minimum garanti, traitement de référence | 2004 et année courante | **certifiée** | Service des retraites de l'État, sa page du minimum garanti |
| Minimum garanti, traitement de référence | ancres intermédiaires | haute | non publiées : la page ne porte que l'ancre et l'année courante |
| Âge d'ouverture des droits par génération | <!--chiffre:minimum(data/reference/legislation/age_ouverture_requis.csv:generation?fiabilite=certifiee)-->1900<!--/-->-<!--chiffre:maximum(data/reference/legislation/age_ouverture_requis.csv:generation?fiabilite=certifiee)-->1975<!--/--> | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 161-2-1-9` |
| Durée d'assurance requise par génération | 1958-1975 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `L. 161-17-3` |
| Durée d'assurance requise par génération | 1953-1957 | **certifiée** | DILA, base LEGI, décrets d'application des lois de 2003 et de 2010 |
| Durée d'assurance requise par génération | 1934-1942 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-45` II |
| Durée d'assurance requise par génération | 1943-1952 | haute | 160 vient de la règle générale, non d'un alinéa qui les nomme ; les 161-164 sont dans des décrets absents de la base — recoupées à chaque exécution contre la table d'OpenFisca-France-Pension |
| Durée de services de la fonction publique, droits ouverts 2004-2008 | 152 à 160 trimestres | haute | loi n° 2003-775, article 66 II, lu dans la base LEGI et mis en table ; recoupé contre OpenFisca-France-Pension |
| Coefficient de minoration par génération | <!--chiffre:minimum(data/reference/legislation/coefficient_minoration.csv:generation?fiabilite=certifiee)-->1900<!--/-->-<!--chiffre:maximum(data/reference/legislation/coefficient_minoration.csv:generation?fiabilite=certifiee)-->1975<!--/--> | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-27` |
| Bornes de la carrière longue | 2023-, règle générale et borne des vingt ans par génération | **certifiée** | DILA, base LEGI, `L. 351-1-1` et `D. 351-1-1` (I et II, versions de 2023 et de 2026, lues à leur date d'effet) |
| Bornes de la carrière longue | 2004, 2011 et 2012, par génération | **certifiée** | DILA, base LEGI, versions abrogées de `D. 351-1-1` que l'index expose |
| Durée maximale prise en compte par la proratisation | avant 1944 à 1947 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-6` II |
| Heures de SMIC à cotiser pour valider un trimestre | 1972 et 2014 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-9` |
| Années retenues au salaire annuel moyen, par génération | avant 1934 à 1948 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-29-1` |
| Décote de la fonction publique, coefficient et âge d'annulation | <!--chiffre:minimum(data/reference/legislation/decote_fonction_publique.csv:annee?fiabilite=certifiee)-->2006<!--/-->-<!--chiffre:maximum(data/reference/legislation/decote_fonction_publique.csv:annee?fiabilite=certifiee)-->2019<!--/--> | **certifiée** | DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 III |
| Barème du minimum garanti, montée en charge | <!--chiffre:minimum(data/reference/legislation/minimum_garanti.csv:annee?fiabilite=certifiee)-->2004<!--/-->-<!--chiffre:maximum(data/reference/legislation/minimum_garanti.csv:annee?fiabilite=certifiee)-->2013<!--/--> | **certifiée** | DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 V |
| Âge d'annulation de la décote, régime général | 1930-1955 | haute | calculé — l'âge d'ouverture certifié majoré de cinq ans, comme l'écrit `L. 351-8` ; recontrôlé à chaque exécution, et recoupé contre la table transcrite d'OpenFisca-France-Pension |
| Point d'indice de la fonction publique | <!--chiffre:minimum(data/reference/legislation/point_indice_fonction_publique.csv:annee?fiabilite=certifiee)-->1996<!--/-->-<!--chiffre:maximum(data/reference/legislation/point_indice_fonction_publique.csv:annee?fiabilite=certifiee)-->2027<!--/--> | **certifiée** | DILA, base LEGI, décret n° 85-1148 du 24 octobre 1985, article 3 |
| Point d'indice de la fonction publique | <!--chiffre:minimum(data/reference/legislation/point_indice_fonction_publique.csv:annee?fiabilite=haute)-->1960<!--/-->-<!--chiffre:maximum(data/reference/legislation/point_indice_fonction_publique.csv:annee?fiabilite=haute)-->1995<!--/--> | haute | OpenFisca-France, `point_indice_en_euros` — deux versions manquent au dump avant 1996 |
| SMIC horaire | 1997-2017, sauf 2002 | **certifiée** | DILA, base LEGI, décrets portant relèvement du SMIC |
| SMIC horaire | 1970-1996, 2002 et depuis 2018 | haute | OpenFisca-France, `smic_horaire_brut` |
| Plafond Sécurité sociale | 2002-2025 | **certifiée** | INSEE BDM, idbank 000822494 |
| Plafond Sécurité sociale | 1963, 1965-1981, 1984, 1987, 1988, 1990-1993, 1996-2001 | **certifiée** | DILA, base JORF, décrets portant fixation du plafond |
| Plafond Sécurité sociale | le reste de 1931-2001 | haute | OpenFisca-France, daté décret par décret — la notice ancienne du JORF n'a pas d'écriture stable |
| Revalorisation des salaires portés au compte | 10 colonnes, effets 2017-2026, perceptions depuis 1930 | haute | Cnav, circulaires de revalorisation, recoupées deux à deux |
| Taux de cotisation, régime général | <!--chiffre:minimum(data/reference/regimes/taux_cotisation_annuels.csv:annee?regime=regime_general&fiabilite=certifiee)-->1982<!--/-->-<!--chiffre:maximum(data/reference/regimes/taux_cotisation_annuels.csv:annee?regime=regime_general&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 242-4` et décret n° 81-1013 du 13 novembre 1981, article 2 ; la hausse temporaire de 1987-1988, qui n'a pas réécrit l'article, est lue dans la base JORF |
| Taux de cotisation, régime général | 1967-1979 | haute | OpenFisca-France, transcrit des barèmes IPP — l'article 3 du décret n° 67-803 n'a qu'une version dans LEGI, datée de 1967 et portant l'état de 1979. Chaque marche est **ancrée** à son décret, retrouvé au JORF au numéro et à la date que l'IPP annonce (35 sur 36 ; le n° 70-680 manque à l'index) |
| Taux de cotisation, régime général | 1980 et 1981 | haute, **comme leurs voisines** | le décret n° 79-650 du 30 juillet 1979 a relevé des taux « à titre exceptionnel » du 1er août 1979 au 31 janvier 1981 : c'est le point du plan Barrot, porté par la seule cotisation MALADIE du salarié, et la vieillesse n'y est pas — voir plus bas |
| Taux de cotisation, salariés agricoles | <!--chiffre:minimum(data/reference/regimes/taux_cotisation_annuels.csv:annee?regime=msa_salaries&fiabilite=certifiee)-->1980<!--/-->-<!--chiffre:maximum(data/reference/regimes/taux_cotisation_annuels.csv:annee?regime=msa_salaries&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | DILA, base LEGI, décret n° 50-444 du 20 avril 1950, article 2, puis code rural `D. 741-35`, qui renvoie à `D. 242-4` depuis 2014 |
| Taux de cotisation, salariés agricoles | 1967-1979 | moyenne | la série du régime général tenant lieu, faute d'une version antérieure de l'article 2 |
| Taux de cotisation, cultes, Mayotte, Saint-Pierre-et-Miquelon | depuis 1979 et 1987 | haute | la série du régime général du dépôt, que ces trois régimes portent faute d'un barème propre : la valeur est certifiée, la substitution est une décision de modélisation |
| Taux de cotisation, complémentaires du privé | Arrco 1962-2018, Agirc 1981-2018, Agirc-Arrco 2019- | moyenne | OpenFisca-France, taux effectifs par tranche, recoupés à chaque exécution. **Ne se certifieront pas** : ces taux sont fixés par accord collectif, l'IPP — source amont d'OpenFisca — laisse lui-même la colonne du *Journal officiel* vide pour chacune de leurs 25 marches, et le JO ne publie que l'avis d'extension, qui renvoie au Bulletin officiel sans écrire le chiffre |
| Retenue pour pension, État, CNRACL, ouvriers de l'État | 1948-2026, une période par taux | moyenne | OpenFisca-France, article L. 61 et barème de la caisse, recoupés à chaque exécution |
| Cotisation vieillesse de base des artisans et commerçants | 1973-2018, moyennes par période | moyenne | OpenFisca-France, décrets d'application de la loi du 3 juillet 1972, recoupés à chaque exécution |
| Taux de cotisation, autres régimes | tous | moyenne / estimée | Comptes de la Sécurité sociale |
| Répartition salarié/employeur, régime général | 1968-2026 | haute | OpenFisca-France, recoupée à chaque exécution |
| Répartition salarié/employeur, autres régimes de salariés | toutes | moyenne / estimée | OpenFisca et textes ; règle 40-60 pour les complémentaires |
| Contribution employeur, État | <!--chiffre:minimum(data/reference/legislation/contribution_employeur_public.csv:annee?regime=fonction_publique_etat&fiabilite=certifiee)-->2006<!--/-->-<!--chiffre:maximum(data/reference/legislation/contribution_employeur_public.csv:annee?regime=fonction_publique_etat&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | Service des retraites de l'État, fiche « Historique des taux de cotisations » |
| Contribution employeur, État (implicite) | 1995-2005 | haute | OpenFisca-France, jaune « pensions » du PLF 2011 — reconstitution dont le producteur refuse les requêtes automatisées |
| Contribution employeur, CNRACL | 1993-2028 | **certifiée** | DILA, base LEGI, décret n° 91-613 du 28 juin 1991, article 5 II |
| Contribution employeur, CNRACL | 1984-1988 | **certifiée** | DILA, base LEGI, décret n° 47-1846 du 19 septembre 1947, article 3 |
| Contribution employeur, CNRACL | 1948-1983, 1989-1992 | haute | OpenFisca-France — la chaîne des versions de l'article 3 est trouée, et la base le démontre |
| Contribution employeur, SNCF (T1 + T2) | 2007-2011 | **certifiée** | DILA, arrêtés annuels du taux T1 (base JORF) et décret n° 2007-1056, article 2 IV (base LEGI) |
| Contribution employeur, SNCF (T1 + T2) | 2012-2018 | haute | OpenFisca-France — le décret cesse de chiffrer T2 après 2011 et le fait évoluer par formule |
| Valeurs d'achat et de service du point, Ircantec | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=ircantec&fiabilite=certifiee)-->1971<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=ircantec&fiabilite=certifiee)-->2021<!--/--> | **certifiée** | Caisse des dépôts, qui gère le régime |
| Valeurs d'achat et de service du point, Agirc | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=agirc&fiabilite=certifiee)-->1947<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=agirc&fiabilite=certifiee)-->2018<!--/--> | **certifiée** | Fédération Agirc-Arrco, sa compilation des valeurs de point |
| Valeurs d'achat et de service du point, Arrco | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=arrco&fiabilite=certifiee)-->1999<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=arrco&fiabilite=certifiee)-->2018<!--/--> | **certifiée** | Fédération Agirc-Arrco, la même compilation |
| Valeurs d'achat et de service du point, UNIRS | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=unirs&fiabilite=certifiee)-->1961<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=unirs&fiabilite=certifiee)-->1998<!--/--> | **certifiée** | Fédération Agirc-Arrco, la même compilation |
| Valeurs du point, Arrco avant 1999 | 1949-1998 | moyenne | l'UNIRS tenant lieu d'Arrco : la valeur est certifiée, la substitution reste une décision du dépôt |
| Valeurs d'acquisition et de service du point, RAFP | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=rafp&fiabilite=certifiee)-->2005<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=rafp&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | ERAFP, dont le conseil d'administration les fixe |
| Valeurs d'achat et de service du point, autres | RCI 2013-2023, IGRANTE et IPACTE 1947-2022 | haute | OpenFisca-France-Pension |
| Valeurs du point, complémentaire des avocats | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=cnbf_complementaire&fiabilite=certifiee)-->2017<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=cnbf_complementaire&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | CNBF, ses barèmes annuels |
| Valeur du point, base des professions libérales | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=cnavpl&mesure=valeur_service&fiabilite=certifiee)-->2021<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=cnavpl&mesure=valeur_service&fiabilite=certifiee)-->2025<!--/--> | **certifiée** | CNAVPL, ses recueils statistiques |
| Taux des deux tranches, base des professions libérales | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=cnavpl&mesure=taux_t1&fiabilite=certifiee)-->2020<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=cnavpl&mesure=taux_t1&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | CNAVPL, le tableau des cotisations de ses recueils, exercice par exercice |
| Valeur de service du point, complémentaire agricole | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=msa_rco&fiabilite=certifiee)-->2005<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=msa_rco&fiabilite=certifiee)-->2025<!--/--> | **certifiée** | DILA, base LEGI, code rural `D. 732-166` |
| Valeur du point, base agricole et valeurs d'achat RCO | — | absentes | hors du code ; voir plus bas |

**Comment la certification fonctionne.** Une valeur n'est `certifiee` que si
elle a été confrontée à un fichier téléchargé depuis le producteur. Le circuit
est le même pour toutes les séries : récupérer, puis confronter.

```bash
python scripts/fetch/insee_bdm.py              # séries longues INSEE
python scripts/fetch/oecd_esperance_vie.py     # espérance de vie à 65 ans
python scripts/fetch/eurostat_mortalite.py     # tables de mortalité par âge
python scripts/fetch/openfisca_plafond.py      # plafond ancien
python scripts/fetch/openfisca_cotisations.py  # taux de cotisation du RG, du public, des non-salariés
python scripts/fetch/openfisca_minimum_contributif.py  # montants du minimum contributif
python scripts/fetch/openfisca_parametres_generation.py  # durée requise, âge d'annulation, par génération
python scripts/fetch/openfisca_points.py       # valeurs du point, depuis 1947
python scripts/fetch/cdc_ircantec.py           # barèmes Ircantec, par son gestionnaire
python scripts/fetch/cnbf_baremes.py           # valeurs du point des avocats
python scripts/fetch/cnavpl_recueils.py        # valeur du point des professions libérales
python scripts/fetch/dila_legi_msa.py          # point de la complémentaire agricole (index LEGI)
python scripts/fetch/dila_legi_minimum_contributif.py  # minimum contributif et plafond (index LEGI)
python scripts/fetch/dila_legi_parametres_retraite.py   # âges, durées, décotes par génération : lit l'index LEGI, en secondes
python scripts/fetch/openfisca_point_indice.py  # point d'indice et barème du minimum garanti
python scripts/fetch/dila_legi_point_indice.py # point d'indice, dans son décret (index LEGI)
python scripts/fetch/dila_legi_smic.py         # SMIC, dans ses décrets de relèvement (index LEGI)
python scripts/fetch/dila_legi_duree_requise.py # durée requise des générations 1953-1957 (index LEGI)
python scripts/fetch/dila_legi_cnracl.py       # contribution employeur de la CNRACL (index LEGI)
python scripts/fetch/dila_legi_contribution_employeur.py  # part patronale de six régimes spéciaux (index, rapide)
python scripts/fetch/dila_legi_decote_fonction_publique.py  # décote de la fonction publique (index LEGI)
python scripts/fetch/dila_legi_minimum_garanti.py  # barème du minimum garanti (index LEGI)
python scripts/fetch/erafp_valeurs_point.py    # valeurs du point du RAFP, par l'ERAFP
python scripts/fetch/jorf_plafond_securite_sociale.py  # plafond ancien, dans ses décrets (index JORF)
python scripts/fetch/sncf_contribution_employeur.py  # contribution SNCF, dans les deux index
python scripts/fetch/dila_legi_minimum_vieillesse.py  # montant de l'ASPA, dans le code (index LEGI)
python scripts/fetch/sre_minimum_garanti.py     # référence du minimum garanti, par le service qui la sert
python scripts/fetch/ined_vallin_mesle.py      # quotients de mortalité d'avant 1986
python scripts/fetch/insee_projections_mortalite.py  # espérances de vie projetées, jusqu'en 2125
python scripts/fetch/eurostat_hicp.py          # contrôle croisé de l'inflation

python scripts/verifier_donnees.py             # confronte, sans rien écrire
python scripts/verifier_donnees.py --appliquer # aligne sur la source et certifie
```

`data/brut/` n'est pas versionné : c'est `data/derive/certification.json` qui
garde la trace du dernier recontrôle — quelle source, quel jour, combien de
valeurs, à quel niveau, et une empreinte de la série reconstruite.

**Les hypothèses de projection ne sont pas certifiables par script, et il faut
le dire.** `verifier_donnees.py` confronte des séries à un producteur ; une
hypothèse de long terme n'a pas de producteur, elle a un auteur. Le fichier
`data/reference/macro/hypotheses_projection.yaml` transcrit donc le jeu du COR
— référence 0,7 %, variantes 0,4 % et 1,0 % de croissance annuelle de la
productivité — en nommant son millésime, et rien ne garantit qu'il suive le
prochain rapport autrement qu'à la main. Deux réserves s'y ajoutent : le taux
est appliqué dès 2026 quand le COR ne l'atteint qu'en 2040, et l'inflation de
1,75 % est une convention reconduite de ses rapports antérieurs, que les
documents publics de juin 2025 et de juin 2026 ne restatent pas.

**Ce que le scénario de projection déplace dans le BILAN, depuis le
21 septembre 2026.** Jusqu'à cette date, `comptes_retraite.csv` ne portait que
la colonne « Sc. Ref » du COR, et le dépôt la lisait quel que soit le scénario
demandé. Le défaut n'était pas qu'un chiffre manquât : c'est que la croissance
traversait une moitié du bilan et pas l'autre. La dépense des systèmes
notionnels est CALCULÉE, et elle réagissait ; celle du droit en vigueur est
EMPRUNTÉE au COR, et elle ne réagissait pas. Le rapport des deux montait à
juste titre — un compte indexé sur la masse salariale profite moins de la
croissance qu'une pension indexée sur les prix — mais il était appliqué à un
niveau gelé, et comptait donc deux fois dans le même sens. Le solde de la
proposition en 2070 allait de +0,42 à −0,72 point de PIB entre les variantes
basse et haute de productivité : **la croissance lui coûtait 1,14 point sans
qu'aucun mécanisme économique le justifie.**

Le COR publie la réponse, sous la même convention et le même champ : ses
figures de sensibilité — 2.22 pour la productivité, 2.21 pour le chômage dans
le rapport de juin 2026 — republient la dépense et le solde du système,
variante par variante. `comptes_retraite_variantes.csv` les porte, et
`ComptesRetraite` lit celle du scénario demandé. La ressource n'y est pas
publiée : elle est la somme des deux, et `verifier_donnees.py` contrôle cette
dérivation sur la ligne de référence de chaque figure avant d'écrire quoi que
ce soit — elle redonne le compte certifié au millionième. **Le scénario de
référence ne bouge pas d'un centime** : c'était déjà la colonne lue.

Ce que la correction laisse, et qui est un résultat et non un artefact :
l'amplitude résiduelle du solde de la proposition, 0,45 point au lieu de 1,14,
et **dans le même sens**. Un compte notionnel indexé sur la masse salariale est
neutre à la croissance en part de PIB ; le droit en vigueur, indexé sur les
prix, en profite. La proposition gagne donc moins que le droit constant à ce
que la croissance soit forte. Une part de ce résidu tient aussi à ce que la
grille de cas types réagit plus fort à la croissance que le modèle de
population du COR — c'est le même écart de méthode que le § 5 ter chiffre à
trois points à l'horizon.

**L'axe de la carte du solde est figé, et il a fallu regarder le dessin pour
s'en apercevoir.** Les chiffres étaient justes dès la mise en place des
variantes ; le tracé, non. L'axe de la carte « La retraite coûte-t-elle plus
qu'elle ne rapporte ? » suivait ses données — 20 % du PIB sous la référence,
15 % sous la variante haute de productivité —, si bien que l'écart de 2070
perdait 29 % de sa valeur d'un tracé à l'autre (2,39 point contre 1,69) et
5 % seulement de sa hauteur à l'écran. Un lecteur qui bascule d'un scénario à
l'autre voyait une bande rouge presque inchangée alors que le déficit avait
fondu d'un quart. C'est la seule carte du site qu'un réglage redessine ET
qu'on lit en comparant deux réglages : l'écart entre les deux courbes est son
sujet. Elle porte donc désormais le sommet de la variante la plus dépensière,
commun à tous les scénarios — et ce sommet est LU sur les variantes
(`depense_maximale_toutes_variantes`), pas écrit : un 20 % figé tiendrait
jusqu'au prochain rapport du COR, puis mentirait en silence. Les autres
graphiques gardent l'axe qui suit leurs données, qui est le bon défaut tant
qu'on ne compare pas deux tracés du même graphique.

**Ce que la variante ne déplace pas, et qu'il faut savoir avant de lire un
coefficient.** Quatre séries restent celles du scénario de référence, parce que
le COR ne les publie que là : le TAUX DE PRÉLÈVEMENT (figure 2.9), donc le
profil qu'emprunte l'assiette de la proposition ; la STRUCTURE des ressources,
donc la part contributive et les parts de postes ; les ressources sous
convention EEC, dont le bloc ne porte que la dimension de productivité ; et les
TRANSFERTS, que personne ne projette dans aucun scénario. Les quatre empruntent
à la référence des FORMES et jamais des niveaux — ce sont des rapports, et
c'est ce qui les rend transportables —, mais c'est une hypothèse, et elle est
ici plutôt qu'ailleurs.

**Le chômage est une autre dimension, et il n'a pas de bouton.** On attend
volontiers d'une croissance plus forte qu'elle apporte moins de chômage : le
COR ne le suppose pas, et ses trois variantes de productivité tiennent toutes
le chômage à 7 % à partir de 2040. Le dépôt porte désormais ses deux variantes
de chômage — 5 % et 10 % en 2040 —, et le compte sait les lire, mais **le
formulaire du site ne les propose pas** : il n'offre que les trois scénarios de
productivité. `python scripts/sensibilite_comptes.py` imprime les six
variantes, les deux dimensions séparées. Ce qu'elles disent est contre-intuitif
et vaut d'être lu : moins de chômage donne MOINS de recettes en part de PIB —
12,86 % contre 12,91 % en 2070 —, et c'est la dépense qui recule, de
15,30 % à 15,02 %. En part de PIB, une assiette plus large ne rapporte pas
davantage : elle monte en même temps que son dénominateur.

**Ce que l'emploi projeté déplace.** Depuis le 20 septembre 2026, l'emploi
au-delà de la dernière observation n'est plus supposé constant : il suit, par
défaut, le scénario de référence du rapport annuel du COR de juin 2026, lu
dans le classeur publié avec le rapport (`Données_RA2026_P1.xlsx`, figures
1.6 et 1.11). La croissance de l'emploi est **dérivée** de deux séries
publiées — la croissance de la population active, calculée par la DG Trésor
sur les projections de population 2026 de l'INSEE, et le taux de chômage,
ramené de 7,7 % à 7,0 % en 2040 —, et elle est recoupée sur le rapport
lui-même, qui compte 30,6 millions de cotisants en 2025 et 28,9 millions en
2070. La série dérivée donne −6,0 % là où le rapport donne −5,6 % : l'écart est
un écart de champ, dit dans l'en-tête de `emploi_projete.csv`. Ce que la
trajectoire touche est étroit et voulu : elle compose la masse salariale et le
PIB projetés, que seule l'indexation des comptes notionnels lit. **Le système
1 ne bouge donc pas d'un centime**, il revalorise sur les prix ; les systèmes
2 à 6 montent pour qui liquide dans la bosse d'emploi des années 2030-2040 et
baissent pour qui liquide après le recul. Mesuré le jour de la mise en place,
sur un salarié non cadre entré à 22 ans et parti à 64 ou 65 ans : +3,7 % pour
la génération 1975, −1,0 % pour 1990, −5,2 % pour 2000, sur les trois
systèmes réformés. C'est le contraire d'un choc favorable de long terme : la
population active du COR recule à partir de 2040, et la trajectoire le
transmet aux comptes. La convention d'avant reste une variante du formulaire
(« Emploi projeté : constant »), et la page de résultats dit ce que l'une
vaut contre l'autre. Le PIB de la page Coût, lui, ne lit pas encore cette
trajectoire : il suit la population des 20-64 ans, ce qui est dit au § 5 ter.

**Deux niveaux, deux exigences.** `certifiee` suppose que la source soit le
**producteur** de la donnée : INSEE, Eurostat, OCDE. Une transcription tierce,
même sourcée et reprise automatiquement, plafonne à `haute` — c'est le cas des
années du plafond ancien dont le décret n'a pas été lu, et qui viennent
d'OpenFisca-France. La distinction n'est pas cosmétique : elle dit ce qu'on
saurait vérifier soi-même en remontant d'un cran. Et le plafond montre à quoi
elle sert : sur les trente et une années où les deux chemins existent — la
transcription et le *Journal officiel* —, ils donnent le même chiffre à l'euro
près, ce qui certifie ces trente et une-là et rend les autres un peu moins
incertaines sans les certifier.

**Ce que l'automatisation a corrigé.** L'API SDMX de la Banque de données
macroéconomiques de l'INSEE (`api.insee.fr/series/BDM/V1`) est ouverte sans clé
d'accès et diffuse, elle, les séries longues — là où l'API Melodi, pour les
jeux dont ce dépôt avait alors besoin, ne remontait pas avant les années 1990.
*Nuance ajoutée le 19 septembre 2026 : cette phrase était trop générale.* Melodi
expose aussi des jeux qui remontent à 1949, dont le tableau économique
d'ensemble des comptes nationaux, et c'est lui qui a fini par donner le revenu
mixte des ménages que la banque de données ne publie pas. La règle à retenir
n'est donc pas « Melodi est courte » mais « les deux portes n'ouvrent pas sur
les mêmes pièces, et il faut essayer les deux ». Le recontrôle a confirmé la plupart des
valeurs saisies mais en a corrigé beaucoup : 28 années d'inflation, 72 de
salaire moyen et 70 de productivité s'écartaient de plus de 0,05 point. Comme
l'indexation retient le **minimum** de ces trois taux, une erreur sur l'un
d'entre eux ne se compense pas : elle se transmet telle quelle au résultat.

**Deux corrections que le recoupement a révélées.**

* *Le plafond de la Sécurité sociale était décalé d'un an sur 1968-2001* : la
  valeur inscrite à l'année N était celle de N−1. L'erreur a été trouvée en
  confrontant la série saisie à celle d'OpenFisca, puis confirmée par la série
  mensuelle de l'INSEE. Elle déplaçait d'un cran, pendant trente-quatre ans, la
  frontière entre droits de base et droits complémentaires. Les plafonds de
  1931 à 1967, jusque-là rétropolés en indexant 1968 sur le salaire moyen,
  étaient quant à eux sous-estimés d'un facteur 2,5 en 1945.
* *Les taux de cotisation du régime général sous-estimaient la cotisation
  réelle* de 0,2 à 0,8 point selon les périodes, la période 1972-1982 étant la
  plus fausse (10,40 % au lieu de 11,19 %). Le taux de cotisation est ce qui
  alimente le compte notionnel : un écart de cette taille sur onze ans se lit
  directement dans le capital accumulé.
* *Les rendements des régimes en points étaient estimés très en dessous du
  réel*, l'Ircantec des années 1970 à 11 % quand ses barèmes en donnent 22,8 %,
  l'Agirc des années 1980 à 9,8 % contre 11,8 %. Le scénario « système actuel »
  servant de référence aux deux autres, il les sous-estimait tous les trois :
  la retraite complémentaire d'un salarié du privé à carrière complète monte
  d'environ un tiers.

**Et une confirmation, qui compte autant.** Les barèmes de l'Agirc et de
l'Arrco pèsent, dans la pension d'un salarié du privé, plus lourd que tous les
autres réunis, et leur seule source était OpenFisca — c'est-à-dire une
transcription qu'on ne savait pas vérifier. L'INSEE, lui, diffuse la valeur de
service du point depuis 2001, mensuelle, sous trois idbanks (`000849395` pour
l'Arrco, `000822495` pour l'Agirc, `010593202` pour l'Agirc-Arrco). **Sur les 42
années où les deux se recouvrent, elles ne divergent pas une fois.** Deux
transcriptions ne font pas un producteur : ce recoupement ne certifiait rien, et
son accord reste recontrôlé à chaque exécution. Il a en outre comblé un trou :
la valeur de service 2025 de l'Agirc-Arrco manquait, la transcription s'arrêtant
à 2024, si bien qu'une liquidation de 2025 convertissait ses points au barème de
l'année précédente.

**Le producteur, lui, publiait bien une série — et cette page disait le
contraire.** Elle écrivait « la caisse ne publiant pas de série », et le
récupérateur du régime unifié ajoutait que les barèmes d'avant la fusion étaient
« sous une présentation différente et avec des conventions de date qui leur sont
propres ». La fédération publie chaque automne, dans un seul document, ses
valeurs de point et salaires de référence depuis 1947 : le régime unifié, l'Agirc,
l'Arrco, et les cinquante caisses qu'elle a fédérées — dont l'UNIRS, dont le
barème tient lieu de point Arrco avant l'unification de 1999. Les 260 valeurs qui
venaient d'OpenFisca sont désormais lues là, et **elles s'y retrouvent toutes** :
l'écart maximal est de 5 · 10⁻⁵ €, et il tient à ce que la transcription
arrondissait la conversion en euros à quatre décimales quand le document donne le
franc exact. Ce qui change n'est donc pas un chiffre mais son statut — et le fait
qu'une refonte du barème sera désormais vue. Mesuré sur les témoins : 2 209 des
10 438 nombres figés bougent, d'au plus **2,3 · 10⁻⁷ en relatif**, soit un
centime sur quarante mille euros de pension.

Deux contrôles autorisent cette lecture, et ils ne coûtent rien puisque le
document les porte lui-même : en regard de chaque valeur, il publie son
évolution en pourcentage. Le récupérateur la recalcule depuis ce qu'il vient de
lire — le salaire de référence d'une année sur l'autre, chaque valeur de point
sur la précédente — et refuse d'écrire si l'écart dépasse un dixième de point.
Le contrôle vaut jusque sur les changements de monnaie : 142,00 anciens francs
en 1959 et 1,52 nouveau franc en 1960 donnent les 7,04 % publiés, ce qu'une
conversion fautive ne rendrait pas.

Ce que cette source ne donne pas : les valeurs de l'Arrco d'avant 1961 — sa
table de caisse s'ouvre là où le dépôt remonte à 1949 —, et la **série
reconstituée du salaire de référence Arrco depuis 1948**, que la fédération
publie mais qu'on ne peut pas utiliser : elle ne porte que le salaire de
référence, sans la valeur de service correspondante, et un rendement ne se
calcule pas avec deux barèmes qui ne parlent pas du même point (68,11 F en 1998
pour l'Arrco reconstituée, 26,43 F pour l'UNIRS).

**Ce qui reste hors de portée, et pourquoi.** La liste vaut recensement de ce
qui a été cherché, pour éviter de le rechercher deux fois — et elle est tenue
dans les deux sens : une limite qui se referme n'est pas effacée, elle est
réécrite avec ce qui l'a levée et ce qu'elle a fini par coûter. Sur les
vingt-cinq entrées qui suivent, **douze ont été refermées par une source trouvée**, **deux
par la mesure du biais** qu'elles laissent — un biais chiffré n'est plus une
inconnue, il se retranche — et **quatre à moitié** : le plafond ancien, dont
trente et une années sur soixante et onze sont désormais lues dans leur décret ;
la contribution de la SNCF, cinq années sur douze ; celle de la CNRACL d'avant
1993, cinq sur quarante-cinq ; et le minimum vieillesse, neuf ancres sur
quatorze. Ces demi-fermetures se ressemblent : la source a été trouvée et lue,
et ce qui reste tient à la RÉDACTION des textes ou aux LACUNES de la base — un
décret qui ne nomme pas l'année qu'il commande, un taux que le décret fait
évoluer par renvoi au lieu de l'écrire, un article qu'on ne réécrit pas à chaque
revalorisation, une version qui a avalé un décret perdu.
Deux de plus sont refermées par la mesure, et dans l'autre sens : la table de
revalorisation des salaires et les valeurs du point du RCI ont été cherchées au
*Journal officiel* et n'y sont pas — la première parce que l'arrêté ne fixe
qu'un coefficient annuel quand la caisse seule publie la table cumulée, la
seconde parce que le règlement du régime renvoie la fixation à son conseil
d'administration. Deux autres se ferment de la même façon : le taux d'appel de
l'Agirc, cherché par quatre portes — la compilation de la fédération, son site,
la base KALI des conventions collectives, le *Journal officiel* — et qui n'est
derrière aucune, parce qu'une convention collective ne paraît au *JO* que le
jour où l'État l'étend ; et le taux implicite de l'État, dont le seul producteur
refuse les requêtes automatisées et dont les reprises disponibles sont des
tiers. Une impasse démontrée vaut une impasse fermée : on ne les rouvrira pas.
**Il n'en reste qu'une** — la ligne qui mêle un nombre de la loi et une
convention de modélisation, et que la source ne suffirait donc pas à certifier.
Les
phrases qui déclaraient ces limites inaccessibles sont citées telles quelles,
parce qu'une conclusion fausse tirée de prémisses vraies est ce qui se répète le
plus volontiers.

* *Inflation d'avant 1950* — **l'adresse a été trouvée, et elle ne suffit
  pas.** Cette page écrivait : « ce n'est plus le format qui bloque, c'est
  l'adresse : la page de l'INSEE qui porte ce tableau ne sert qu'un
  convertisseur, sans lien de téléchargement. Le jour où l'adresse est connue,
  le chemin est court. » L'adresse n'est pas une page mais un IDBANK —
  **`010605954`**, le coefficient de transformation du franc et de l'euro, que
  la Banque de données macroéconomiques sert **depuis 1901** par la même API
  que tout le reste, sans clé.

  Le chemin était court, en effet. Mais la série ne remplace pas ce qu'elle
  devait remplacer, et c'est maintenant mesuré plutôt que supposé : publiée à
  deux décimales sur une base 100 en 2015, elle vaut **0,20 en 1935**. Un
  centième y pèse cinq points de taux. Les variations annuelles qu'on en
  tirerait seraient du bruit — elle donne +3,9 % pour 1930 quand le dépôt porte
  −2,5 %, et 0,0 % pour 1934 quand il porte −5,7 %.

  Ce qu'elle permet, en revanche, c'est de **valider la dérive cumulée**, et le
  contrôle est désormais dans `verifier_donnees.py` :

  | Période | Dépôt | INSEE 010605954 | Écart |
  |---|---|---|---|
  | 1930-1949, reconstituée | ×19,23 | ×18,41 | +4,5 % |
  | 1949-2025, certifiée | ×23,76 | ×24,34 | −2,4 % |

  La seconde ligne est l'étalon de la première : sur la période où le dépôt est
  certifié contre la série mensuelle de l'INSEE, la série des coefficients
  s'écarte déjà de 2,4 %. Un écart de 4,5 % sur vingt ans de reconstitution ne
  dit donc rien d'autre que la précision de l'instrument. **La reconstitution
  d'avant 1950 n'est pas fausse** — elle n'est simplement pas certifiable au
  sens du dépôt, et l'on sait maintenant de combien.

  Restent hors de portée le SALAIRE MOYEN et la PRODUCTIVITÉ d'avant 1949 : les
  comptes nationaux ne remontent pas plus haut, et aucune série de coefficients
  ne leur correspond. Ont été essayés sans succès, pour éviter de refaire le
  trajet : la BDM (comptes nationaux depuis 1949), les longues séries de prix de
  la BRI (1951), Eurostat (1996), la Banque mondiale (1960).
* *Quotients de mortalité par âge d'avant 1986* — **trouvés.** Cette page
  écrivait que la Human Mortality Database était « seule à couvrir la France
  depuis 1816 » et que son inscription obligatoire la mettait hors de portée
  d'un script. Elle n'est pas seule : Jacques Vallin et France Meslé ont
  reconstitué les tables françaises de 1806 à 1997, l'INED les a publiées en
  2001, et l'INED en sert librement le contenu du cédérom. Le tableau II-B-1
  donne exactement ce qui manquait — « quotients du moment par année d'âge, de
  0 à 104 ans » — pour les deux sexes.

  Le dépôt en reprend **1899-1985**, soit 18 226 quotients, et laisse à
  Eurostat, producteur de la donnée observée, tout ce qui suit. Les deux
  sources se recouvrent en fait de 1986 à 1997 : sur ces douze années et
  85 âges, elles concordent à un écart médian de 0,4 à 0,7 %. C'est ce
  recoupement qui autorise à les aboucher.

  Le fichier est un classeur Excel 97, format que la bibliothèque standard ne
  sait pas ouvrir. Comme pour les PDF de la CNBF, on a donc écrit le lecteur :
  `scripts/fetch/lecture_xls.py` extrait les nombres d'un fichier composite
  OLE2, en quatre types d'enregistrements BIFF et sans dépendance.

* *Espérance de vie à 65 ans d'avant 1960* — **réglée, en la calculant.**
  L'INSEE publie e0, e1, e20, e40 et e60, jamais e65 ; ni l'OCDE (1960) ni
  Eurostat (1986) ne remontent plus haut. Ces quatorze années étaient donc
  saisies — quatre valeurs prises aux tables TD/TV, pour 1946 et 1950 — et les
  treize autres simplement INTERPOLÉES entre elles.

  Il n'y avait plus lieu de les saisir depuis que le dépôt porte les quotients
  du moment de Vallin et Meslé : une espérance de vie n'est rien d'autre que
  leur somme cumulée. Les vingt-huit valeurs sont désormais dérivées, et
  RECALCULÉES à chaque exécution de `verifier_donnees.py` depuis un fichier
  certifié — ce qu'aucune saisie ne peut offrir. Elles restent au niveau
  `haute`, parce qu'elles sont calculées et non confrontées à une publication.

  La méthode se contrôle d'elle-même, et c'est ce contrôle qui l'autorise :
  appliquée à e60, que l'INSEE publie et que le dépôt certifie, elle retrouve
  la valeur publiée à moins d'un dixième d'année sur toute la période ;
  appliquée à e65 après 1960, elle retrouve l'OCDE dans la même marge. Deux des
  quatre valeurs saisies s'en écartaient — 1946 pour les deux sexes, d'un
  demi-an chez les hommes — et l'interpolation effaçait les creux réels de 1949
  et de 1951, deux années de surmortalité.

* *Espérances de vie projetées* — **dérivées, et poussées jusqu'en 2125.**
  Elles étaient saisies à la main, aux six années rondes de 2030 à 2080, depuis
  les projections de population 2021-2070 — dont 2080 dépassait l'horizon tout
  en s'en réclamant. Au-delà, la série était **gelée** : l'espérance de vie
  cessait de progresser vingt ans avant la fin de la projection, dans un modèle
  qui liquide jusqu'en 2100.

  Les projections de population **2026** de l'INSEE publient les quotients de
  mortalité par âge et par année, de 0 à 120 ans et jusqu'en 2125. Le dépôt en
  dérive e0, e60 et e65 année par année, par la méthode qui sert déjà aux années
  d'avant 1960 — y compris e65, que l'INSEE ne publie jamais. Plus
  d'interpolation entre années rondes, plus d'extrapolation muette, plus de gel.

  **Le contrôle qui autorise la méthode porte sur la convention d'âge.** Ce
  classeur indexe ses quotients par âge atteint dans l'année, non par âge exact :
  le demi-an que la formule usuelle ajoute y est déjà compris. Deux mesures le
  établissent, et le récupérateur les refait à chaque exécution — la somme des
  survies retrouve l'espérance de vie à la naissance que l'INSEE publie pour
  2070, 89,5 ans et 86,7 ans, au centième ; et la série projetée rejoint
  l'observée sans marche, 85,90 an certifié en 2025 contre 85,93 dérivé en 2026.

  **Ce que le nouveau millésime déplace.** L'INSEE révise l'espérance de vie à
  la baisse : le diviseur de conversion recule de 0,6 % en médiane sur les cas
  témoins, jusqu'à 4,3 % pour la génération 2000, et les pensions notionnelles
  montent d'autant — jusqu'à +4,5 %. Le scénario « système actuel » ne bouge
  pas d'un centime : il n'utilise pas de table de mortalité, et c'est un
  contrôle de plus.

* *Quotients de mortalité au-delà de 94 ans* — **complétés jusqu'en 1997, et
  mesurés au-delà.** Eurostat s'arrête à 94 ans et ses classes ouvertes (85 et
  plus, 95 et plus) ne sont pas des quotients à un âge donné. L'INED, lui, va
  jusqu'à 104 ans et couvre 1986-1997 : ces dix âges-là sont désormais repris.
  Ce n'est pas panacher deux sources sur une même donnée — c'est en ajouter une
  là où l'autre se tait.

  **Ces 240 valeurs ne déplacent aucune simulation, et c'est justement ce qui
  les rend précieuses.** Une liquidation de 2004 ou plus tard ne traverse les
  âges de 95 ans et plus qu'après 2035, années où aucune observation n'existera
  jamais : la loi de Gompertz-Makeham y reprend forcément la main. Les douze
  années observées sont donc le seul endroit où l'on puisse CONFRONTER cette
  loi à la réalité — et le verdict était net, toujours dans le même sens :

  > la loi sous-estimait la mortalité au-delà de 94 ans de **22 % en moyenne**.

  **La cause en est trouvée, et corrigée.** La loi était calibrée sur
  *elle-même* : on ajustait ses deux paramètres pour que l'espérance de la loi
  PURE reproduise e60 et e65. Rien ne l'obligeait alors à rendre la queue que la
  cible implique, et elle rendait 11,3 ans d'espérance résiduelle à 85 ans pour
  une femme en 2010, là où la cible en implique 7,5. La table telle que le
  modèle la LIT — quotients observés jusqu'au dernier âge publié, loi au-delà —
  débordait en conséquence l'espérance publiée par l'INSEE de jusqu'à 2,5 ans.

  La calibration se fait désormais en deux temps : la FORME de la queue vient
  toujours de l'ajustement classique sur la loi seule, où e60 et e65 portent sur
  toute la plage d'âges et déterminent le paramètre sans ambiguïté ; son NIVEAU
  est ensuite recalé, à forme constante, pour que la table raccordée reproduise
  l'espérance publiée. Là où la queue n'a pas prise sur la cible — millésimes
  dont les quotients vont jusqu'à 104 ans, où les données décident seules —, le
  recalage est abandonné plutôt que forcé.

  Le biais résiduel aux grands âges tombe de 22 % à **moins de 3 %**, et il est
  toujours figé par un test (`test_la_loi_parametrique_sous_estime_la_
  mortalite_des_grands_ages`), pour qu'il ne dérive pas en silence. Un second
  test, qui prétendait confronter les deux chaînes, ne confrontait rien : il
  passait par `esperance_residuelle(..., generation=False)`, branche qui ne
  consultait aucun quotient observé et comparait donc la calibration à sa propre
  cible. Cette branche lit maintenant les quotients comme l'autre, et le test
  passe par `survie_annuelle`, seul chemin que le moteur emprunte réellement.

  Ce que cela déplace : peu de chose sur les résultats par défaut, et c'est à
  dire. En table de GÉNÉRATION — le réglage par défaut — une liquidation à 60
  ans en 2005 traverse les âges de 85 ans et plus en 2030 et au-delà, années
  sans observation où la loi régnait déjà seule ; le raccord à l'intérieur d'un
  même millésime n'y est presque jamais franchi. C'est la table du MOMENT, et la
  cohérence de la queue avec l'espérance publiée, qui étaient fausses.

* *Taux de cotisation des COMPLÉMENTAIRES du privé* — **trouvés, et deux
  erreurs avec eux.** Cette page rangeait ces taux avec ceux d'avant 1967, au
  motif qu'« aucune transcription machine n'existe ». C'était vrai du régime
  général d'avant 1967 et faux des complémentaires : OpenFisca-France porte
  leurs **taux effectifs par tranche**, datés depuis 1962 pour l'Arrco et 1981
  pour l'Agirc, sous
  `prelevements_sociaux/regimes_complementaires_retraite_secteur_prive`. Ce
  sont les taux réellement prélevés, taux d'appel compris — la même grandeur
  que celle des fiches du dépôt, donc directement comparable.

  Le contrôle de vraisemblance qui en découle a trouvé deux écarts, l'un et
  l'autre corrigés :

  * l'Agirc portait **8 %** sur toute la période 1947-1988, soit le taux
    contractuel d'origine appliqué à quarante-deux ans, quand le taux effectif
    était de 8,24 % en 1981 et de 12 % en 1988. La période est coupée à 1981 —
    date où commence la transcription — et les huit dernières années portent
    désormais 11,58 % ;
  * l'Agirc portait **20,43 %** sur 1994-2018, valeur de fin de période, là où
    la moyenne effective est de 19,48 %.

  Et le recoupement a révélé un manque plus grave qu'un taux : **la tranche 2 de
  l'Arrco n'existait pas dans le modèle.** Tous les salariés du privé cotisent
  à l'Arrco sur la tranche 1, mais seuls les non-cadres cotisent sur la
  tranche 2 — la part de salaire comprise entre un et trois plafonds, à près
  d'un cinquième. La fiche n'ayant que la tranche 1, un non-cadre payé au-dessus
  du plafond n'acquérait aucun droit complémentaire sur ce qui dépassait, alors
  que son régime y prélevait. La tranche est ajoutée, avec sa borne propre :
  trois plafonds, et non huit comme dans le régime unifié d'après 2019.

* *Taux de cotisation du régime général et des salariés agricoles depuis 1982*
  — **lus dans les textes qui les fixent, et certifiés.** Ces taux venaient
  d'OpenFisca-France, transcription tierce plafonnée à `haute` ; ils sont
  désormais lus dans l'article D. 242-4 du code de la sécurité sociale et dans
  l'article D. 741-35 du code rural, avec leurs rédactions successives, par
  `scripts/fetch/dila_legi_taux_cotisation.py`. Ce que la lecture a déplacé est
  sous « La lecture des taux de cotisation » plus bas.

* *Taux de cotisation d'avant 1982, et des régimes autres que ceux du privé* —
  **la seule limite de cette liste qui reste ouverte**, et la seule dont on
  puisse dire par où elle passe sans pouvoir la refermer. Pour 1967-1981, ce
  n'est plus faute d'article : l'article 3 du décret n° 67-803 est dans la base
  LEGI, mais avec UNE seule version, datée du 1er octobre 1967 et valable
  jusqu'au 14 novembre 1981, portant 12,9 % — l'état de 1979, alors que le taux
  valait 8,5 % en 1967. La base a gardé la photographie finale et non le film,
  comme pour la CNRACL ; les décrets modificatifs sont bien au *Journal
  officiel* — 73-1209, 75-1273, 76-894, 78-1213 — mais la base JORF n'en garde
  avant 1990 que la notice, et aucune de ces notices n'écrit de taux. Avant
  1967, aucune transcription machine n'existe : ces taux viennent des
  ordonnances de 1945 et de leurs modificatifs, saisis à la main. Ont été
  essayés sans succès, pour éviter de refaire le trajet : la Banque de données
  macroéconomiques de l'INSEE, dont la série de taux de cotisation vieillesse
  (idbank 000483633) ne porte que la part salariale et ne débute qu'en juillet
  1993 ; et une lecture EXHAUSTIVE de la base JORF, de 1967 à 1982, de tout
  document dont le texte ou le titre porte un pourcentage à moins de cent
  vingt caractères du mot « vieillesse » — sept documents, dont un seul écrit
  un taux du régime général, et c'est celui de novembre 1981. Ce que ces
  quinze années valent malgré tout est dit plus bas, « Ce que vaut une série
  qu'on ne peut pas certifier ».

  **Ce que cette incertitude déplace, et de combien.** Un taux de cotisation
  n'entre nulle part dans le calcul d'une pension du système ACTUEL : les
  annuités se calculent sur un salaire de référence, les régimes en points sur
  un prix d'achat. Il n'alimente que le COMPTE NOTIONNEL. Une erreur de taux ne
  fausse donc pas l'étalon, elle fausse les deux scénarios comparés — dans un
  seul sens, et de façon mesurable. En surévaluant d'un point entier les taux
  d'avant 1967 du régime général, soit davantage que la plus grosse erreur
  jamais trouvée sur les taux postérieurs (0,8 point), la pension notionnelle
  rétroactive d'un salarié du privé monte de :

  | Génération | Pension actuelle | Notionnel rétroactif | Effet de +1 point avant 1967 |
  |---|---|---|---|
  | 1930 | inchangée | 3 409 € | **+0,75 %** |
  | 1940 | inchangée | 6 105 € | **+0,25 %** |
  | 1950 | inchangée | 9 210 € | **+0,03 %** |

  L'effet s'éteint avec la part de carrière antérieure à 1967, et il est déjà
  inférieur au pour cent pour la génération 1930 — la plus ancienne que le
  modèle simule couramment. Ce n'est pas ce qui explique les écarts, qui se
  comptent en dizaines de pour cent.

  Pour les **régimes autres que le privé**, l'incertitude porte sur toute la
  période, et non sur les seules années d'avant 1967 : elle serait donc bien
  plus lourde. Elle est neutralisée par un choix de modélisation, non par une
  source : le réglage par défaut aligne la cotisation portée au compte notionnel
  d'un fonctionnaire sur le TAUX DU PRIVÉ, précisément parce qu'une comparaison
  entre systèmes ne peut pas reposer sur une retenue dont le sens historique
  diffère. Sous ce réglage, majorer d'un point tous les taux des fiches de la
  fonction publique ne déplace **aucun** chiffre. Le réglage « retenue de
  l'agent seule », lui, y est très sensible — +11 à +14 % sur la pension
  notionnelle des générations 1940 et 1960 pour ce même point — ce qui est une
  raison de plus de ne pas en faire le défaut, et de lire ses résultats en
  sachant sur quoi ils reposent. Depuis que les fiches portent leur
  `part_salariale`, ce réglage n'est plus le défaut d'aucun scénario : les
  scénarios 2 et 3 comparent la part salariale de chacun, sans emprunt, et les
  scénarios 4 et 5 y ajoutent une part patronale lue dans la fiche pour le privé
  et datée décret par décret pour le public. L'incertitude des taux publics ne
  pèse plus, dans les scénarios 4 et 5, que pour un dixième du taux total.
* *Valeur du point de la MSA* — **trouvée, après huit sources infructueuses.**
  Ont été essayés sans succès : OpenFisca-France-Pension (ne modélise pas ce
  régime), les barèmes IPP (même périmètre — c'est la source amont d'OpenFisca,
  ses quarante-cinq feuilles couvrent l'Arrco, l'Agirc, l'UNIRS, PRO-BTP,
  l'Ircantec, la CANCAVA et l'ORGANIC), l'open data de la DREES (cinquante et un
  jeux « retraite », tous des résultats statistiques), le portail open data de la
  Caisse des dépôts (effectifs seulement), data.gouv.fr (les jeux de la MSA sont
  des effectifs de retraités et d'exploitants), la BDM de l'INSEE — qui porte le
  point de l'Agirc et de l'Arrco mais aucun point agricole — les « Chiffres
  utiles » de la MSA, publiés chaque année depuis 2005 mais qui sont un annuaire
  d'effectifs et non un barème, et le site de la caisse, dont les pages de
  barèmes sont construites en JavaScript.

  Elle était pourtant écrite, chaque année depuis 2005, dans le **code rural**,
  à l'article `D. 732-166` :

  > « La valeur de service du point de retraite complémentaire obligatoire
  > mentionnée à l'article L. 732-60 est fixée pour l'année 2013 à
  > 0,336 2 euros. »

  Ce qui manquait n'était pas la donnée mais un **chemin reproductible** vers
  elle : Légifrance sert cet article mais refuse les requêtes automatisées — 403
  sur toute requête non navigateur — et son API demande une clé. La base **LEGI**
  de la DILA, elle, est en accès libre et garde chaque version datée de chaque
  article codifié. `scripts/fetch/dila_legi_msa.py` la lit en flux, sans écriture
  disque, et n'en retient que les dix-neuf versions de cet article. La série
  couvre **2005-2024**, sans trou, et le niveau est celui du producteur : c'est
  la publication officielle, non une transcription.

  Trois pièges de lecture, notés pour qui reprendra le fil : le *Journal
  officiel* aère les décimales par groupes de trois (« 0,336 2 », parfois même
  « 0, 311 9 ») ; la rédaction change trois fois de forme en vingt ans ; et un
  même décret peut fixer deux années d'un coup — c'est ainsi que 2019 et 2021
  entrent dans la série, aucun texte ne leur étant propre. L'année 2022 a reçu
  deux valeurs successives, revalorisée en cours d'année : la convention du
  dépôt retenant le 31 décembre, c'est la seconde qui compte.

  **Ce qui reste ouvert, et une correction.** Cette page a d'abord écrit que la
  RCO ne pouvait pas avoir de prix d'achat, ses points étant attribués par la
  formule `revenus × 100 ÷ (1 820 × SMIC)`. C'est faux : l'article `L. 732-60`
  dispose que « le nombre annuel de points est déterminé en fonction de
  l'assiette […] et des **valeurs d'achat** fixées par l'arrêté mentionné à
  l'article L. 732-60-1 ». La formule était la règle ancienne ; depuis la loi
  d'avenir agricole de 2014, un plan triennal fixe conjointement valeurs de
  service, valeurs d'achat et taux de cotisation. Ces valeurs d'achat ne sont pas
  dans le code — l'arrêté ne le modifie pas — et restent à trouver.

  Le régime de **base** reste lui aussi sans série. Sa retraite proportionnelle
  est en points, dont la valeur n'est entrée dans le code qu'en 2025
  (`R. 732-66`, 4,589 € au 1er janvier 2025 ; le COR donne 4,264 € pour 2023),
  et ses points sont attribués par un barème annuel par tranche de revenu — de
  23 à 113 points — que personne ne publie en série.

  **Le moteur utilise désormais ces valeurs.** La fiche a été scindée : la RCO
  a la sienne, `msa_rco`, et la base garde `msa_non_salaries`. Ce qui a
  débloqué le calcul n'est pas le prix d'achat introuvable mais, là encore, le
  BARÈME EN POINTS, qui est public : cotiser sur l'assiette minimale de
  1 820 SMIC ouvre 100 points, et les points sont proportionnels au-delà, sans
  plafond. Le nombre de points ne dépend donc pas du taux de cotisation, et
  l'absence de série historique de ce taux ne déplace que le flux versé au
  compte notionnel. Restent hors du modèle les points **gratuits** — 66 par an
  aux conjoints et aides familiaux pour les périodes antérieures à 2011, dans
  la limite de 17 années — et le barème du régime de base.

  **La voie légale mène quelque part, mais pas partout.** Les bases ouvertes
  de la DILA ont été dépouillées en flux, sans écriture disque : 12,4 Go de JORF
  puis 9,1 Go de LEGI, quatre passes en tout — deux ciblées, deux larges gardant
  tout article codifié portant une valeur de point, pour ne pas manquer un renvoi
  du type « la valeur mentionnée à l'article L. 643-1 ». Une cinquième passe,
  cette fois indexée non sur le texte mais sur le **numéro d'article**, a fini
  par livrer la série agricole : c'est ce que fait aujourd'hui
  `scripts/fetch/dila_legi_msa.py`. Le bilan, pour ne pas refaire le trajet :

  * la valeur de service du point de la **retraite complémentaire obligatoire
    agricole** est portée par l'article `D. 732-166` du code rural, dont LEGI
    garde les dix-neuf versions datées. C'est une série complète de 2005 à 2024,
    désormais dans le dépôt et certifiée. Chercher le *texte* ne suffisait pas —
    les premières passes n'en avaient tiré que quatre valeurs éparses ; chercher
    le *numéro d'article* les donne toutes, parce que LEGI est organisée par
    version d'article et non par thème ;
  * la **CNAVPL** n'apparaît dans aucun article codifié portant une valeur de
    point, et la passe large n'en trouve pas davantage : la législation
    consolidée ne contient, sous ce libellé, que le point d'indice des pensions
    militaires d'invalidité et celui de la fonction publique. Côté *Journal
    officiel*, la passe large remonte 104 textes portant une valeur de point,
    dont aucun ne mentionne le mot « libérale ». L'explication n'est pas que la
    recherche ait été trop étroite, mais que la donnée cherchée n'y est pas :
    **le décret annuel fixe un coefficient de revalorisation, non un montant.**
    La valeur qui en résulte n'est publiée que par la caisse.

  La leçon vaut d'être retenue : *une base peut contenir la donnée sans que le
  mot cherché y figure*. Ce qui a débloqué la MSA n'est pas une source nouvelle,
  c'est un changement de clé d'entrée.

  *La CNBF et la CNAVPL ont fini par livrer les leurs* — non par la loi, mais
  l'une par ses barèmes annuels, l'autre par ses recueils statistiques. Voir les
  deux limites suivantes.

* *Régime de base des avocats* — **scindé, et le moteur s'en sert.** La CNBF
  publie chaque janvier un barème en PDF qui donne le coût d'acquisition et la
  valeur de service du point de son régime complémentaire. Ces valeurs étaient
  dans le dépôt depuis un moment, certifiées de 2017 à 2026, et le moteur ne les
  utilisait pas : la fiche `cnbf` agrégeait en un seul taux, calculé au
  rendement instantané, un régime de base FORFAITAIRE et un complémentaire en
  points. La pension d'un avocat y était donc intégralement proportionnelle à
  son revenu — exactement l'inverse de la règle du régime de base.

  Cette page tenait la scission pour bloquée par « deux décisions de
  modélisation ». En regardant le barème d'assez près, l'une s'est révélée
  facile et l'autre n'était pas une décision :

  * **la classe** — trois coexistent (C1, C2, C2+), et rien ne permet de deviner
    celle d'un avocat donné. C1 est celle qui s'applique SANS option, et le
    modèle ne prête jamais à personne un avantage facultatif : c'est la même
    règle que pour les minima sous condition de demande. Décision prise, et
    écrite dans la fiche ;
  * **les tranches en euros** — la question n'était pas « comment exprimer des
    tranches en euros dans un moteur dont les assiettes sont en plafonds », mais
    « ces tranches suivent-elles le plafond ? ». Elles ne le suivent pas :
    **42 507 € en 2023, en 2025 et en 2026**, quand le plafond de la Sécurité
    sociale passait de 43 992 à 48 060 €. Les exprimer en plafonds les ferait
    donc dériver d'année en année. Il ne fallait pas arbitrer, il fallait un
    champ de bornes EN EUROS — écrit pour ce régime, et utilisable par tout
    autre qui fixerait son assiette de la même façon.

  La fiche est donc scindée : `cnbf` porte la base, avec sa pension forfaitaire
  de 19 154 € par an au taux plein proratisée par la durée, et
  `cnbf_complementaire` porte les points, avec les cinq tranches de la classe C1
  et le prix d'achat publié. Un avocat modeste et un avocat aisé touchent
  désormais la même retraite de base, ce qui est la règle.

  Ce qu'il reste : la cotisation FORFAITAIRE de base — 363 € la première année,
  1 988 € à partir de la sixième — n'est pas modélisée. Elle ne dépend pas du
  revenu, quand le compte notionnel ne sait porter qu'une fraction d'assiette ;
  le taux inscrit à la fiche est celui de la seule cotisation proportionnelle,
  3,20 %. Et les tranches d'avant 2019 ne sont pas connues : ces années restent
  au rendement instantané.

  Au passage, le barème éclaire l'estimation qu'il remplace : un rendement
  agrégé de 6,5 % pour l'ensemble base + complémentaire était cohérent avec un
  complémentaire à 8,2 % et une base forfaitaire moins rentable. L'estimation
  n'était pas absurde, ce que rien ne permettait de dire jusqu'ici.

  **Un piège de lecture, découvert en recontrôlant.** Les barèmes de 2017 à
  2025 écrivent leurs chiffres dans une police dont la table `/ToUnicode` les
  déclare caractères grecs : « 11,1654 € » y est encodé `ϭϭ͕ϭϲϱϰΦ`. Le document
  est parfaitement lisible à l'écran, et illisible pour un programme — les huit
  barèmes antérieurs à 2026 étaient ignorés en silence, la série tombant de
  dix-huit valeurs à deux, sans qu'aucune erreur ne soit signalée. Les dix
  chiffres étant contigus à partir de U+03EC, la table se répare. On ne la
  devine pas pour autant : le barème 2023 ainsi décodé donne 11,1654 € et
  0,9815 €, valeurs déjà certifiées quand la caisse servait ces PDF dans une
  police saine, et le garde-fou du récupérateur refuse toute série qui ne serait
  pas monotone en coût, en valeur de service et en rendement. **Une source qui
  se tait est plus dangereuse qu'une source qui manque** : c'est le journal de
  certification, qui compte les valeurs versées, qui a rendu la chute visible.

* *Régime de base des professions libérales* — la CNAVPL ne publie sa valeur de
  point nulle part ailleurs que dans son **recueil statistique**, un annuaire
  d'une soixantaine de pages paru chaque année, sous une phrase invariable :
  « La valeur du point est fixée à 0,6540 au 1er janvier 2025. » Le même recueil
  donne les deux taux de cotisation, dans un tableau qui les chiffre exercice
  par exercice — 8,23 % sur la tranche 1 jusqu'en 2024, 8,73 % depuis 2025,
  1,87 % sur la tranche 2. Ces valeurs sont dans le dépôt, certifiées : la
  valeur du point de 2021 à 2025, les taux de 2020 à 2026. Les millésimes
  antérieurs mettent la valeur dans un graphique et non dans une phrase, d'où
  le début de série. Pour les années d'avant, ce n'est pas la caisse qui dit le
  taux mais le code : `D. 642-3`, dont les versions successives donnent 8,6 %
  de 2004 à 2011, 8,63 % en 2012, 9,75 % en 2013 et 10,1 % en 2014 sur la
  première tranche, 1,6 % puis 1,81 % puis 1,87 % sur la seconde.

  **Le moteur s'en sert désormais.** Ce qui bloquait n'était pas la donnée mais
  la forme du barème : le régime n'attribue pas un nombre de points
  proportionnel à la cotisation, mais **525 points au maximum sur la tranche 1
  et 25 sur la tranche 2**, soit 550 de 2015 à 2024 — 450 et 100 avant, 557 et
  25 depuis 2025, le barème suivant la hausse du taux de T1. Un
  plafonnement en points est une règle de calcul, pas une colonne à ajouter :
  il a fallu l'écrire dans le moteur, sous la forme d'un champ `points_maximum`
  qui dit combien de points ouvre une assiette donnée. La fiche est scindée en
  ses deux tranches, qui se recouvrent depuis 2015 comme le fait la cotisation.
  Le nombre de points ne dépend alors pas du taux de cotisation, ce qui est
  heureux : c'est le barème que la caisse publie, pas le prix d'achat.
  La période 1949-2003 obéit à une troisième règle, et c'est celle qui
  manquait : « les trimestres validés avant le 1er janvier 2004 sont convertis
  en points à raison de 100 points par trimestre ». La grille des classes
  forfaitaires qu'on cherchait pour ces années ne commandait pas la pension —
  elle ne commande que la cotisation.

* *Âges, durées requises, décotes* — **certifiés, par la même clé que la MSA.**
  Cette page écrivait : « ils viennent de lois, pas de séries statistiques.
  Légifrance expose une API, mais elle demande une clé et renvoie du texte
  juridique, non des paramètres. » Les deux moitiés de la phrase étaient vraies
  et la conclusion fausse. La base LEGI de la DILA est ouverte, elle garde
  chaque version datée de chaque article — et **le texte juridique EST la
  table** :

  > « Soixante-deux ans et trois mois pour les assurés nés entre le
  > 1er septembre 1961 et le 31 décembre 1961 inclus. »

  Trois articles du code de la sécurité sociale portent, en toutes lettres, les
  trois tables par génération dont le scénario 1 dépend le plus :
  `D. 161-2-1-9` pour l'âge d'ouverture des droits, `L. 161-17-3` pour la durée
  d'assurance requise, `R. 351-27` pour le coefficient de minoration. Deux
  autres, `L. 351-1-1` et `D. 351-1-1`, portent les bornes de la carrière
  longue. `scripts/fetch/dila_legi_parametres_retraite.py` les lit dans le même
  flux de 9 Go que la RCO agricole et le minimum contributif, et en reconstitue
  la table année de naissance par année de naissance.

  **Ce que la confrontation a donné : aucune correction.** Les trente-cinq
  valeurs saisies à la main — seize âges, huit durées, onze coefficients — se
  sont retrouvées identiques au texte, au centième d'année et au millionième de
  point près. C'est le seul recontrôle du dépôt qui n'ait rien corrigé, et
  c'était le plus attendu : ces tables commandent la décote, la surcote et
  l'ouverture des droits, c'est-à-dire l'essentiel de l'écart entre une pension
  à 62 ans et la même à 64. Ce qu'il apporte n'est donc pas une correction mais
  une **preuve**, et cent trente-cinq générations que la saisie laissait
  implicites : toutes celles d'avant 1951 et d'après 1968 pour l'âge, d'après
  1965 pour la durée, hors de la fenêtre 1944-1953 pour le coefficient. Une
  simulation portant sur la génération 1972 lisait jusqu'ici la dernière ligne
  de la table ; elle lit désormais une ligne écrite pour elle.

  Trois difficultés de lecture, notées pour qui reprendra le fil :

  * **les versions d'un article ne sont pas simultanées.** Les fusionner donne
    un résultat faux et vraisemblable : la version de 2011, qui fixe 62 ans « à
    compter du 1er janvier 1955 », recouvrait la table de 2023. Les versions
    sont donc appliquées dans l'ordre chronologique, la plus récente l'emportant
    — comme le fait le droit lui-même ;
  * **les nombres sont en toutes lettres**, et les bornes s'écrivent de six
    façons (« avant le », « entre le … et le », « nés en », « à compter du »,
    « après le 31 décembre »). Le récupérateur les convertit en MOIS COUVERTS.
    Il attribuait ensuite chaque génération à la valeur qui en couvrait le
    plus — la plus exigeante en cas d'égalité —, ce qui valait un trimestre
    d'âge légal à qui naissait du mauvais côté d'une coupure. **Il rend
    désormais un segment par valeur** : la clé porte le mois, `1951.5` pour le
    1er juillet 1951, `1961.667` pour le 1er septembre 1961, et le modèle lit
    ces tables au mois de naissance. L'approximation est levée, et la passe du
    3 septembre 2026 sur le dump LEGI du 13 juillet 2025 l'établit : **78
    segments d'âge d'ouverture et 19 de durée requise, tous identiques** aux
    lignes du dépôt — aucune correction, aucun ajout. Les trois lignes qui
    portaient une coupure sont donc `certifiee` comme les autres. Le
    coefficient de minoration, lui, ne porte AUCUN segment décimal : l'article
    R. 351-27 ne coupe pas ces générations, et le modèle ne l'invente pas ;
  * **le texte peut être fautif.** Le décret du 3 juin 2023 écrit « A
    soixante-deux pour les assurés » — le mot « ans » manque. Une expression
    régulière trop stricte perd la borne des 20 ans de la carrière longue, et
    l'on ne s'en aperçoit pas, puisqu'il en reste trois.

  Ce que cette voie ne donne pas, et qui reste transcrit : les générations 1934
  à 1952 de la durée requise, fixées par les lois de 1993 et de 2003, dont les
  tableaux ne sont pas des textes consolidés séparés — celles de 1953 à 1957,
  elles, ont été retrouvées dans leurs décrets, par la phrase et non par le
  numéro ; l'âge d'annulation de la décote ; et les portes de carrière longue de
  2004 et de 2012, qui sont dans des versions abrogées. Le nombre d'années retenues au salaire annuel moyen y
  figurait aussi, à tort : l'article R. 351-29-1 le porte, génération par
  génération, et il est désormais lu comme les autres.

* *Durée de proratisation, assiette du trimestre, années du salaire de
  référence* — **certifiées, par la même clé encore.** Ces trois tables étaient
  saisies, et cette page les rangeait parmi les paramètres « repris des textes,
  non recontrôlés » : elles ne ressemblent pas à des tables par génération, et
  l'on n'était pas allé les chercher. Elles sont pourtant écrites en toutes
  lettres, dans trois articles que le même flux de 9 Go traverse :

  > « 152 trimestres pour les assurés nés en 1944 » (`R. 351-6` II)
  >
  > « […] calculé sur la base de 200 heures » (`R. 351-9`)
  >
  > « Vingt et une années pour l'assuré né en 1944 » (`R. 351-29-1` II)

  La première commande le DÉNOMINATEUR de toute carrière incomplète des
  générations 1944 à 1948 — la confondre avec la durée requise retire 2,5 % de
  pension à qui est né en 1945 —, la seconde le nombre de trimestres que valide
  une année de petit salaire, la troisième le nombre d'années sur lesquelles se
  calcule le salaire annuel moyen — dix jusqu'à la génération 1933,
  vingt-cinq à partir de 1948. Les vingt-trois valeurs saisies s'y sont
  retrouvées identiques. L'article de proratisation s'arrête à la génération
  1947 et renvoie au-delà à la durée requise : la ligne 1948 de cette table-là
  est cette jonction, et reste hors de la certification — elle n'est pas dans le
  texte.

* *Montants servis du minimum vieillesse* — **cherchés dans le code, et le code
  ne les porte plus.** L'article `D. 815-1` fixe bien le montant maximum de
  l'ASPA, et la base LEGI en garde huit versions datées : 7 323,48 € au
  1er janvier 2006, 8 125,59 € au 1er avril 2009, puis un calendrier jusqu'à
  10 838,40 € au 1er janvier 2020. Les trois dernières valeurs sont exactement
  celles que le dépôt porte pour 2018, 2019 et 2020.

  **Et l'article n'a pas bougé depuis.** La revalorisation de l'ASPA est devenue
  automatique — l'article `L. 816-2` la lie à celle des pensions —, si bien que
  le texte du code a cessé de suivre le montant réellement servi : il resterait à
  9 600 € en 2016 quand la caisse en payait 9 609,60, et à 10 838,40 € en 2026
  quand elle en paie 12 523,08. Certifier depuis `D. 815-1` reviendrait donc à
  remplacer un montant servi par un montant périmé, ce que la règle du dépôt
  interdit : **le montant SERVI prime sur toute autre source.** Les treize
  valeurs restent des transcriptions de publications, et c'est ici le bon
  niveau. La même remarque vaut pour le minimum garanti de la fonction publique,
  dont l'article `L. 17` ne fixe qu'une référence de 2004.

* *SMIC et point d'indice* — **lus dans leurs décrets, là où la base les
  porte.** Cette page les rangeait tous deux parmi les transcriptions
  d'OpenFisca, au motif qu'ils ne sont fixés par aucun article de code. C'est
  vrai, et cela ne suffisait pas : le SMIC est relevé par un décret annuel, le
  point d'indice par l'article 3 du décret du 24 octobre 1985, et la base LEGI
  garde les uns et l'autre, datés.

  > « A compter du 1er juillet 1997 […] le montant du salaire minimum de
  > croissance est porté à 39,43 F de l'heure en métropole »
  >
  > « La valeur annuelle du traitement […] afférents à l'indice 100 majoré […]
  > est fixée à 5 907,34 € »

  Cinquante-deux valeurs passent ainsi de la transcription au *Journal
  officiel*, et la confrontation n'a corrigé que deux arrondis — celui de 2002
  pour le point d'indice, que le décret de bascule fixe à 5 181,75 € quand la
  conversion des 33 990 F donne 5 181,74 €.

  **Ce qui n'a pas été certifié l'a été délibérément**, et c'est ici le plus
  instructif : une chaîne de décrets ne se devine pas. Trois trous sont
  mesurés plutôt que comblés.

  * *le SMIC de 2002*. Le dernier décret en vigueur au 1er janvier est en
    francs — 43,72 F, soit 6,6651 € —, mais le SMIC opposable cette année-là
    est de 6,67 €, arrondi fixé par un texte de conversion que le dump ne porte
    pas. Le récupérateur écarte donc toute année dont le décret commandant est
    encore en francs ;
  * *le SMIC depuis 2018*. La base garde les textes consolidés, et les décrets
    de relèvement postérieurs à celui du 1er janvier 2017 n'y sont pas entrés.
    Une année dont le décret a plus de trois cent soixante-cinq jours signale un
    texte absent, l'article L. 3231-5 imposant un relèvement au moins annuel :
    elle n'est pas écrite ;
  * *le point d'indice d'avant 1996*. Deux relèvements manquent, celui du
    1er novembre 1991 et celui du 1er janvier 1994, tous deux pris par un décret
    qui en portait deux d'un coup. La série qu'on en tirerait serait plate là où
    le point a monté — fausse de 1,0 % en 1992 — et rien ne le dirait. C'est la
    confrontation à la transcription, année par année, qui l'a établi : les deux
    séries ne se séparent que là.

* *Valeurs du point du RAFP* — **trouvées chez celui qui les fixe, avec une
  erreur dedans.** Ces barèmes venaient d'OpenFisca. Or l'ERAFP publie le
  tableau complet depuis la création du régime, et le document le dit
  lui-même : « La valeur d'acquisition et la valeur de service du point RAFP
  sont fixées chaque année par le conseil d'administration de l'ERAFP. »

  La transcription **répétait en 2021 la valeur d'acquisition de 2020** —
  1,2452 € au lieu de 1,2502 €. Une valeur d'acquisition trop basse achète trop
  de points : les droits acquis cette année-là étaient majorés de 0,4 %.
  L'erreur s'est vue toute seule, le tableau publiant en regard de chaque valeur
  son évolution — et + 0,4 % ne mène pas de 1,2452 à 1,2452.

  Elle s'arrêtait en outre à 2021, quand l'établissement publie jusqu'en 2026 :
  les cinq années manquantes étaient prolongées par les prix, alors que la
  valeur de service a monté de 5,7 % en 2023 et de 6,8 % en 2024. Le RAFP est
  servi à part, à l'identique dans les six scénarios : cela ne déplace aucun
  écart, seulement le montant affiché à un fonctionnaire.

* *Durée requise des générations 1953-1957, et contribution employeur de la
  CNRACL* — **trouvées par la phrase, faute de numéro d'article.** Ces deux
  séries étaient rangées ici comme inaccessibles, et pour la même raison : ce
  qui les porte n'est pas un article de code. Cette page écrivait des
  générations 1934-1957 que « leur durée a été fixée par des décrets pris sous
  l'ancien article L. 351-1, textes abrogés ou non codifiés que la base LEGI
  n'expose pas sous un numéro d'article unique. La voie automatisable s'arrête
  là. » Elle s'arrête en effet — si l'on cherche par numéro. Ces décrets n'ont
  pas de numéro utile, mais ils ont une phrase :

  > « […] sont fixées à 166 trimestres pour les assurés nés en 1955. »

  Quatre décrets couvrent les générations 1953 à 1957, cinq valeurs de moins
  dans la colonne des transcriptions. Restent les générations 1934 à 1952 :
  leur montée en charge vient des lois de 1993 et de 2003, dont les tableaux ne
  sont pas des textes consolidés séparés.

  **Un piège, et il est gros** : Saint-Pierre-et-Miquelon a son propre régime,
  et sa loi du 17 juillet 1987 écrit sa table de durées dans les mêmes termes —
  152 trimestres pour la génération 1956, quand le régime général en exige 166.
  Un dépouillement qui ne l'écarterait pas remplacerait la table du modèle par
  celle d'un archipel de six mille habitants.

  **La contribution employeur de la CNRACL**, elle, est dans l'article 5 du
  décret n° 91-613 du 28 juin 1991, dont la base garde vingt versions datées.
  Trente-six valeurs, de 1993 à 2028, toutes identiques à la transcription — et
  parmi elles les trois marches de 2026, 2027 et 2028 que le dépôt tenait pour
  une saisie « non recoupée », alors qu'elles sont au *Journal officiel* depuis
  janvier 2025. C'est le plus gros bloc du fichier : pour un agent territorial,
  cette contribution vaut aujourd'hui trois fois sa retenue, et c'est elle qui
  décide de ce que les scénarios 4 et 5 lui portent au compte.

  Trois difficultés de lecture, notées pour qui reprendra le fil : le même
  article fixe d'abord la retenue de l'agent, ensuite la contribution de
  l'employeur, et une contribution supplémentaire après — trois taux dans le
  même texte ; une version en porte plusieurs, chacun daté par ce qui le SUIT
  (« 30,40 % pour l'année 2014 ; b) 30,45 % pour l'année 2015 »), si bien que
  lire la première date rencontrée décale toute la table d'un cran ; et le
  décret de relèvement paraît fin janvier avec effet au 1er janvier, quand la
  version consolidée s'ouvre au 1er février — sans quoi 2024 porterait le taux
  de 2023.

* *Part patronale de six régimes spéciaux* — **cherchée chez le producteur,
  écrite au Journal officiel.** Cette page rangeait douze régimes sous une
  seule ligne du tableau de la part patronale : « rien / tout — aucune série de
  taux employeur publiée sous une forme exploitable ». C'était vrai des sources
  qu'on avait interrogées, et faux des textes. Six d'entre eux sont tombés en
  une session, et sans télécharger un seul dump :

  > « Le taux définitif de la cotisation à la charge de la Régie autonome des
  > transports parisiens […] est fixé à 19,43 % pour l'exercice 2024. »

  **163 valeurs, toutes certifiées** : la RATP de 2007 à 2025, les IEG de 2005
  à 2020, la SNCF de 1992 à 2006, les mines de 1984 à 2026, l'Opéra de Paris et
  la Comédie-Française de 1992 à 2026.

  **Ce que la recherche avait manqué, c'est qu'il y a deux formes de texte.**
  La RATP et les IEG ont été adossés au régime général en 2005-2006 : depuis,
  l'employeur y verse ce que les mêmes salariés coûteraient à la CNAV et à
  l'Agirc-Arrco, et un ARRÊTÉ ANNUEL l'arrête, exactement comme la composante
  T1 de la SNCF que le dépôt lisait déjà. Les quatre autres sont dans la
  VERSION DATÉE d'un article, comme la CNRACL : le II de l'article 8 du décret
  n° 91-613 pour la SNCF d'avant 2007, l'article 52 puis l'article 90 du décret
  de 1946 pour les mines, les articles 6 et 7 du décret de 1991 pour les deux
  théâtres. Aucune de ces deux mécaniques n'était nouvelle pour le dépôt ; ce
  qui manquait, c'était de les chercher ailleurs que là où elles avaient déjà
  servi.

  **Deux pièges, et ils se ressemblent.** Un arrêté porte DEUX taux, le
  provisionnel appelé d'avance et le définitif arrêté après coup, souvent dans
  la même phrase ; un article en porte TROIS, le total, la part de l'employeur
  et celle de l'agent — « à hauteur de 15,60 %, soit 7,75 % à la charge des
  employeurs et 7,85 % à la charge des salariés ». Dans les deux cas, prendre
  le premier nombre venu donne une valeur plausible et fausse. Les deux erreurs
  ont été commises en écrivant le récupérateur, et un test porte désormais un
  repère de chaque série pour qu'elles ne reviennent pas.

  **Un troisième, plus discret** : un arrêté en corrige parfois un autre. Celui
  du 23 juin 2020 ramène le taux 2019 de la RATP de 19,20 % à 19,18 %. C'est le
  texte le plus récent qui l'emporte, et l'écart est conservé au fichier brut.

  **Ce que cela ne donne pas.** Les IEG s'arrêtent en 2020 et la SNCF en 2018,
  pour la même raison : le texte cesse de chiffrer et renvoie à une formule que
  la caisse applique sans la publier. Un taux qui évolue par renvoi n'est écrit
  nulle part, et le calculer serait le reconstituer. Sept régimes restent sans
  série — FSPOEIE, marins, CRPCEN, Banque de France, port de Strasbourg, SEITA,
  chemins de fer secondaires. Pour le dernier, la lecture est faite et
  inutilisable : l'article 12 du même décret de 1991 donne 14,60 % à la charge
  des exploitants, mais la fiche du régime s'arrête en 1954 et aucune année ne
  se rencontrerait.

  **Ce que cela a déplacé.** Trente cas de témoin sur 427, et pas un de plus :
  les six régimes, et eux seuls. L'écart va dans les deux sens, ce qui est la
  vraie leçon. Un agent des IEG voit la part patronale de sa carrière passer de
  224 000 à 316 000 €, soit **+41 %** — le repli lui prêtait 27,75 % quand
  l'employeur en verse 29,70 ; un mineur la voit tomber de 247 000 à
  177 000 €, soit **−28 %**, parce que l'exploitant ne verse que 7,75 %. Un
  agent de l'Opéra en perd 17 %, un agent SNCF en gagne 6 %, et une génération
  plus ancienne bouge davantage : un cheminot né en 1935 passe de 51 000 à
  77 000 €, ses années 1992-2006 ayant quitté le repli. Sur la page Coût,
  l'effet est petit — deux cas
  types sur douze sont concernés, et de faible poids : le cumul du scénario 4
  passe de −51,9 % à −51,8 %, celui du 6 de −51,7 % à −51,6 % (la lecture des
  taux de cotisation les a ensuite ramenés à −51,9 % et −51,7 %, la catégorie
  active et la pension militaire à −52,6 % et −52,4 %, et l'âge de liquidation
  par génération à −56,0 % et −51,8 %).

  **L'index a remplacé le dump, et il était meilleur.** Les récupérateurs
  `dila_legi_*` plus anciens retéléchargeaient le dump global de la DILA — un
  quart d'heure pour LEGI, une heure pour les deux bases — jusqu'au
  17 septembre 2026, où tous sont passés à l'index. Celui-ci a lu l'index
  publié par le dépôt, en quelques secondes, et il y trouve plus : le dump n'a
  pas été régénéré depuis juillet 2025, quand l'index reçoit les incréments
  quotidiens. L'arrêté RATP du 13 mars 2026, qui porte l'année 2025, n'est que
  là.

* *Décote de la fonction publique, et âge d'annulation de la décote* — **l'une
  lue dans la loi, l'autre calculée et désormais recontrôlée.** Ces deux tables
  figuraient au tableau des paramètres du scénario 1 avec la même mention :
  « reprise des textes, non recontrôlée ». Elles ne sont pourtant pas de même
  nature, et c'est ce que la recherche a établi.

  **La décote de la fonction publique est écrite, et dans un seul tableau** :
  le III de l'article 66 de la loi du 21 août 2003, que la base garde comme
  texte consolidé et que le dépouillement rend à plat, ligne à ligne :

  > « I : 2006 II : 0,125 % III : Limite d'âge moins 16 trimestres »

  Quatorze années, deux colonnes — le coefficient par trimestre et le nombre de
  trimestres retranchés à la limite d'âge —, vingt-huit valeurs identiques à la
  saisie. Le tableau s'arrête à 2019, la dérogation courant « jusqu'au
  31 décembre 2019 » : la ligne 2020 du dépôt est la jonction avec l'article
  L. 14, qui s'applique en plein ensuite, et reste `haute`.

  **L'âge d'annulation du régime général, lui, n'est écrit nulle part**
  génération par génération, et il n'y a rien à chercher de plus : ce que le
  code écrit est une RÈGLE. L'article `L. 351-8` 1° donne « l'âge prévu à
  l'article L. 161-17-2 augmenté de cinq années », devenu trois années quand la
  réforme de 2023 a porté l'âge d'ouverture à 64 ans — la cible restant 67. La
  table du dépôt est donc la table certifiée des âges d'ouverture, décalée et
  plafonnée.

  Elle reste au niveau `haute` : une valeur calculée n'est pas une valeur
  confrontée, et c'est la règle que le dépôt applique déjà à l'espérance de vie
  dérivée. Mais elle est désormais RECALCULÉE à chaque exécution depuis la table
  certifiée — si une réforme déplaçait l'âge d'ouverture sans que celui-ci
  suive, l'écart se verrait là plutôt que dans une pension.

  **Le même article 66 porte un troisième tableau**, à son V : la montée en
  charge du barème du MINIMUM GARANTI, de 2004 à 2013. Ses cinq colonnes sont
  celles du fichier du dépôt — la fraction servie à quinze ans de services,
  l'indice majoré de référence, les points gagnés par année supplémentaire, la
  borne où la pente s'infléchit, les points au-delà :

  > « I : 2004 II : 59,7 % III : 217 IV : 3,8 points V : Vingt-cinq ans et demi
  > VI : 0,04 point »

  Cinquante valeurs, toutes identiques à la transcription. La ligne 1976 du
  dépôt, elle, n'est pas dans le tableau : celui-ci s'ouvre sur une ligne
  « 2003 » qui décrit le droit antérieur — 60 %, indice 216, quatre points,
  vingt-cinq ans —, que le dépôt date de 1976, année où le barème a pris cette
  forme. Mêmes valeurs, autre clé : elle reste transcrite.

  **Et la RÉFÉRENCE du minimum garanti se recoupe désormais toute seule.**
  L'article L. 17 la définit comme le traitement de l'indice majoré 227 au
  1er janvier 2004 ; le point d'indice de cette année-là est lu dans son décret
  depuis la passe précédente. Les deux chemins se rejoignent au centime :
  227 × 52,7558 = 11 975,57 €, soit les 997,96 € par mois que publie l'État. Le
  montant reste `haute` — il est transcrit d'une publication —, mais l'écart
  entre les deux chemins est désormais contrôlé.

* *Trimestres pour enfants, et surcote parentale* — **cherchés, et ce n'est pas
  la source qui manque.** L'article `L. 351-4` porte bien les huit trimestres de
  majoration de durée d'assurance — quatre au titre de la maternité, quatre au
  titre de l'éducation — et l'article `L. 351-1-2-1` portait, dans sa rédaction
  de 2023, les 1,25 % par trimestre de la surcote parentale. Mais les lignes du
  dépôt ne portent pas que ces nombres : elles portent aussi `beneficiaire`,
  `enfants_minimum`, et l'attribution par défaut à la mère faute de connaître
  l'accord des parents — des CONVENTIONS DE MODÉLISATION qu'aucun texte
  n'écrit. Certifier la ligne parce que l'un de ses nombres est dans la loi
  reviendrait à certifier les autres, et le niveau de fiabilité porte sur la
  ligne entière. Elles restent donc `haute` et `moyenne`, et c'est la borne
  basse qui a raison.

  S'y ajoute, pour la surcote parentale, que la loi du 28 février 2025 a réécrit
  l'article : il n'énonce plus un taux mais un abaissement d'un an de l'âge de
  la surcote ordinaire. Certifier la ligne du dépôt contre une rédaction abrogée
  serait le contraire d'une certification.

* *Plafond de la Sécurité sociale d'avant 2002* — **cherché, et trente et une
  années sur soixante et onze sont rentrées.** Cette page écrivait : « l'INSEE
  ne publie le plafond mensuel qu'à partir de 2001 et l'Urssaf ne diffuse aucun
  historique en accès ouvert. La seule série machine des plafonds anciens est
  celle d'OpenFisca-France. » Les deux premières phrases sont vraies, la
  troisième ne l'est pas, et l'erreur est de catégorie : **le plafond n'est pas
  une statistique, c'est un décret.** Le chercher chez les diffuseurs de séries
  était chercher au mauvais endroit ; il est chez son producteur, le *Journal
  officiel*, dont la DILA ouvre le dump.

  Les années **1963, 1965-1981, 1984, 1987, 1988, 1990-1993 et 1996-2001** sont
  désormais lues dans le décret qui les fixe. Elles se sont trouvées
  **identiques à l'euro près** à ce que portait la transcription — le contrôle
  n'a rien corrigé, et c'est ce qu'on attend d'une certification qui arrive
  après un recoupement déjà fait deux fois.

  **LA CHAÎNE DES DÉCRETS EST COMPLÈTE DEPUIS 1963** : un texte par année,
  aucun ne manque. Ce qui reste dehors ne tient donc pas à l'accès mais à la
  RÉDACTION, et cela se dit année par année :

  | Années | Ce qui manque |
  |---|---|
  | avant 1963 | le décret ne nomme pas l'année qu'il commande — « LE PLAFOND ANNUEL […] EST FIXE A 11 400 FRS », et rien d'autre. Le dater de sa publication serait une inférence, non une lecture |
  | 1982, 1983 | le plafond y devient semestriel avant que la notice ne s'y mette : les décrets de juillet renvoient aux « SOMMES FIXEES PAR CE DECRET » sans les écrire |
  | 1985, 1986 | la base n'en garde que le titre et les mots-clés, sans notice |
  | 1989 | le décret de juillet n'annonce qu'un taux — « REVALORISATION DE 1,9% » — et non un montant. L'appliquer au plafond de janvier serait un calcul, et un calcul ne se certifie pas |
  | 1994, 1995 | l'article renvoie à une image : « Vous pouvez consulter le tableau dans le JO no 0301 du 29/12/94 Page 18669 a 18670 » |

  **ET UN PIÈGE, QUI A ÉTÉ MESURÉ AVANT D'ÊTRE ÉVITÉ.** Le titre des décrets
  d'avant 1982 porte le montant ANNUEL et l'année : « PORTANT FIXATION POUR
  L'ANNEE 1969 DU PLAFOND DES COTISATIONS DE SECURITE SOCIALE A 16 320 FRS ».
  Une autre écriture lui ressemble et ne dit pas la même chose — « A COMPTER DU
  01-01-1982 […] (GAIN OU REMUNERATION ANNUEL : 79 080 FRS) » —, car un décret
  de juin 1982 a relevé le plafond au 1er juillet : lire les deux de la même
  façon donne 1982 à **−3,6 %**. La distinction est dans le texte, et le
  récupérateur la respecte ; il refuse en outre un titre annuel pour toute année
  dont un relèvement en cours d'année a été lu, pour ne pas dépendre d'une date
  charnière supposée.

* *Taux d'appel de l'Agirc, 1948-1995* — **cherché par quatre portes, et il
  n'est derrière aucune.** Le taux d'appel est l'écart entre ce qui est prélevé
  et ce qui ouvre des droits : cotiser 125 € n'en acquiert que 100. Quarante-huit
  valeurs en dépendent, et elles venaient d'OpenFisca.

  | Porte | Ce qu'on y a trouvé |
  |---|---|
  | La compilation historique de la fédération | Lue page par page : soixante pages de valeurs de service et de salaires de référence, et rien d'autre. Le mot « appel » y paraît sept fois, toutes dans « rappel » |
  | Le site de la fédération | Un antibot rejette son API de médias ; seule l'adresse connue du PDF répond. On ne peut pas énumérer ce qu'il publie |
  | **KALI**, la base des conventions collectives de la DILA | 173 Mo, 7 632 textes lus. La convention du 14 mars 1947 n'y est PAS : ce n'est pas une convention de branche déposée mais un accord national interprofessionnel, et la base n'en garde que l'accord de 1986 sur ses *seuils d'accès*. 1 754 textes la citent ; aucun n'est elle |
  | Le **JORF** | 1 219 textes lus. Les avis d'extension des accords « fixant le pourcentage d'appel » existent bien — mais à partir des années 2000 seulement, la procédure des articles L. 911-3 et L. 911-4 étant ce qui les y amène. Avant 1995, le seul taux d'appel trouvé est celui de l'**accord national interprofessionnel du 8 décembre 1961** — 110 % pour les exercices 1979 à 1982 —, c'est-à-dire l'Arrco, un autre régime |

  **La raison est de nature, non de recherche.** Ce taux est fixé par les
  avenants d'une convention collective que ses signataires publient eux-mêmes ;
  il n'entre au *Journal officiel* que le jour où l'État l'étend, et cette
  procédure est récente. Ces quarante-huit valeurs resteront `haute`.

  **Une chose en est tout de même sortie.** Le dépôt arrête la série en 1995 à
  1,25 et la prolonge en escalier ; le *Journal officiel* confirme ce chiffre —
  « le pourcentage d'appel […] est maintenu à 125 % pour l'année 2008 », « il
  maintient le pourcentage d'appel des cotisations pour les exercices 2011 à
  2015 inclus à 125 % ». Ce que le modèle extrapolait est désormais recoupé.

* *Taux implicite de l'État, 1995-2005* — **fermée, et pas par le réseau.**
  Ces onze taux sont une RECONSTITUTION : l'État n'appelait aucune cotisation
  avant 2006, les pensions étaient payées sur crédits budgétaires, et l'annexe
  « pensions » au projet de loi de finances pour 2011 en a simulé un a
  posteriori. Le producteur de cette reconstitution est donc la direction du
  Budget, et elle seule.

  Quatre portes ont été essayées. `budget.gouv.fr`, le site du producteur,
  **répond 403 aux requêtes automatisées** — trois fois sur trois, et l'on ne
  cherche pas à forcer un refus. Son miroir `performance-publique.budget.gouv.fr`
  n'est pas joignable depuis l'environnement où ce dépôt est construit ; c'est
  une limite de la machine, pas de la source, et elle est notée comme telle.
  La base **RAPPORTS_PUBLICS** de la DILA — 19 558 rapports indexés — ne porte
  aucun jaune budgétaire : les jaunes sont des annexes au projet de loi de
  finances transmises au Parlement, pas des rapports publics, et les trois
  titres qui contiennent le mot « jaune » parlent de gilets et d'un mur.
  `data.gouv.fr` ne connaît pas le compte d'affectation spéciale « Pensions ».

  **Et surtout : une porte ouverte n'aurait pas suffi.** Les deux documents qui
  reprennent cette série sont dans l'index de la DILA — le rapport de la Cour
  des comptes de 2016 et celui de la commission des finances du Sénat de 2012 —
  et ce sont des TIERS. Une transcription de transcription ne monte pas au-dessus
  de `haute`, quel que soit le réseau. C'est ce qui referme l'entrée : il ne
  s'agit plus d'un accès à trouver mais d'une source qui, seule, certifierait,
  et qui ne se laisse pas lire par un script.

* *Revalorisation des salaires portés au compte* — **cherchée au Journal
  officiel, et elle n'y est pas.** C'est le plus gros bloc non certifié du dépôt
  — 876 valeurs, dix colonnes de coefficients — et il tient à une distinction
  qu'il valait la peine de vérifier plutôt que de supposer. Le modèle lit ces
  coefficients dans la CIRCULAIRE de la Cnav, qui « transcrit l'arrêté et
  l'instruction interministérielle qu'elle cite » : une transcription plafonne à
  `haute`. Restait à savoir si l'arrêté, lui, publiait la même table.

  **Il ne la publie pas.** Six cent soixante-treize textes du dump JORF portant
  les mots « revalorisation des salaires », « coefficient de revalorisation » ou
  « servant de base au calcul des pensions » ont été lus : **aucun ne porte plus
  de trois couples (année, coefficient)**, et ces trois-là sont des coefficients
  de revalorisation de PENSIONS d'autres régimes. Les arrêtés anciens — « 19 avril
  1950, REVALORISATION DES SALAIRES ENTRANT EN COMPTE DANS LE CALCUL DES
  PENSIONS » — ne sont dans la base que par leur titre.

  La raison est structurelle et non documentaire : **l'arrêté fixe UN coefficient
  annuel**, applicable à tous les salaires déjà portés au compte ; la table
  cumulée par année de perception en est le produit, et c'est la caisse qui la
  calcule, l'arrondit à trois décimales et la publie. Reconstruire la table
  depuis les coefficients annuels ne redonnerait pas la table publiée — le dépôt
  a déjà mesuré cette dérive entre ses propres colonnes. Ces 876 valeurs
  resteront `haute` tant que la circulaire sera le seul document à porter la
  table, et ce n'est pas une lacune de la recherche.

* *Valeurs du point du RCI* — **cherchée, et aucun texte ne la porte.** Le
  règlement du régime est pourtant dans la base : l'arrêté du 9 février 2012 qui
  l'approuve y figure avec ses versions, jusqu'à celle du 1er janvier 2025. Il
  parle bien de « la valeur de service de ces points » et de « la valeur du
  point cotisé RCO artisan au 31 décembre 2012 » — mais il ne les chiffre pas :
  il en renvoie la fixation au conseil d'administration. La question de doctrine
  que cette page laissait ouverte se referme donc d'elle-même : il n'y a pas de
  texte à préférer aux circulaires, ces vingt-deux valeurs restent `haute`.

* *Contribution employeur de la SNCF* — **lue, et la moitié en est
  certifiable.** Cette page écrivait : « Douze lignes y gagneraient leur
  certification et cinq années s'y ajouteraient ; le travail est écrit ici
  plutôt que fait, faute d'avoir tranché la convention de date. » Le travail a
  été fait, la convention tranchée, et le compte était optimiste — voici
  pourquoi, et c'est instructif.

  Le taux est la somme de deux composantes que l'article 2 du **décret
  n° 2007-1056 du 28 juin 2007** définit. Chacune est dans un texte différent,
  et les deux ont été lues :

  * **T1** est arrêté chaque année et publié au *Journal officiel* — « le taux
    T1 définitif […] est fixé à 23,81 % pour l'année 2022 ». Dix-huit arrêtés,
    de 2008 à 2023, donnent **T1 de 2007 à 2022** ;
  * **T2** est au IV du même article, dont la base LEGI garde seize versions
    datées.

  **LA CONVENTION DE DATE, ET C'ÉTAIT ELLE QUI BLOQUAIT.** Chaque arrêté porte
  DEUX taux T1 : le définitif de l'année écoulée et le provisionnel de l'année
  qui vient. Le taux d'une année est le définitif — celui qui est dû, arrêté une
  fois l'exercice connu. Ce n'est pas un détail : 23,87 % et 23,25 % pour 2018,
  six dixièmes de point, et c'est le provisionnel que la transcription
  d'OpenFisca avait retenu pour cette année-là.

  **CE QUI LIMITE À CINQ ANNÉES, ET CE N'EST PAS T1.** La somme n'est lisible
  que là où ses deux termes le sont, et le décret ne chiffre T2 que jusqu'en
  2011 : « Après le 31 décembre 2011, le taux T2 évolue au 1er janvier de chaque
  année comme le rapport […] entre le montant des cotisations d'assurance
  vieillesse assis sur le montant maximum des rémunérations […] ». **Un taux qui
  évolue par renvoi n'est écrit nulle part** ; le calculer serait le
  reconstituer, non le lire, et une reconstitution ne se certifie pas. La
  réécriture de 2017 — « A partir du 1er mai 2017, le taux T2 est fixé à
  13,85 % » — ne rouvre pas la série : elle donne une valeur à une date, que la
  même formule fait dériver dès le 1er janvier suivant.

  **2007-2011 se certifient donc**, et les cinq valeurs se sont trouvées
  identiques au centième de point à la transcription. 2012-2018 restent `haute`,
  et l'on sait exactement ce qui manque : non pas une source, mais un texte qui
  chiffre T2. Un piège au passage — l'arrêté fondateur du 6 mai 2008, le seul à
  porter l'année 2007, écrit « le taux définitif T1 » quand tous les autres
  écrivent « le taux T1 définitif ». Ne lire que la rédaction moderne coûtait la
  première année de la série.

* *Contribution employeur de la CNRACL d'avant 1993* — **cherchée au mauvais
  endroit, puis trouvée, et la chaîne reste trouée là où la base l'est.** Cette
  page écrivait : « ceux d'avant sont dans les décrets que ce dernier a
  remplacés, et la base ne les garde pas tous : sur les six textes que l'article
  consolidé cite en note, un seul porte encore sa phrase. » La prémisse était
  vraie et le raisonnement faux, d'une faute qu'il vaut la peine de nommer :
  **un décret modificatif ne porte pas le taux, il porte un REMPLACEMENT.** Le
  taux, lui, est dans l'article modifié — l'**article 3 du décret n° 47-1846 du
  19 septembre 1947** —, dont la base garde quinze versions datées au jour.

  **MAIS LA CONTIGUÏTÉ N'EST PAS LA COMPLÉTUDE**, et c'est la vraie leçon.
  Quand un décret manque à la base, la version qu'il aurait coupée court sans
  coupure : la chaîne paraît pleine et saute une valeur, sans que rien ne le
  dise. Ce n'est pas une conjecture — la base se contredit elle-même : le décret
  n° 83-36 du 24 janvier 1983 y figure et déclare remplacer « 13 p. 100 », quand
  la version qu'il modifie se lit « 18 p. 100 ». Entre 1977 et 1983, un décret a
  fait passer le taux de 18 à 13 % et la base ne l'a pas gardé.

  Deux garde-fous en découlent, et aucun ne repose sur une date supposée : la
  **contradiction** — une version qu'un décret modificatif dément est refusée
  avec toute sa période — et la **longévité** — une version de plus de quatre
  ans est refusée, ce taux ayant bougé tous les un à trois ans sur toute la
  période documentée. La version de 1962 à 1977, quinze ans sur un seul chiffre,
  tombe par le second ; celle de 1977 à 1983 par les deux.

  Il en reste **1984 à 1988**, cinq années aux versions courtes que rien ne
  contredit, et qui se sont trouvées identiques au centième de point à la
  transcription. Les quarante autres restent `haute` — non plus faute de source,
  mais parce que la base est trouée, et l'on sait désormais où.

* *Montant du minimum vieillesse* — **il était dans le code, et personne n'y
  avait regardé.** Ces montants venaient d'une saisie sur Légifrance
  (`source_id: legifrance_textes`), c'est-à-dire d'une lecture humaine et non
  d'un fichier confronté au producteur. Or l'**article D. 815-1 du code de la
  sécurité sociale** les porte, datés, et la base LEGI en garde les versions :
  neuf ancres, de 2006 à 2020, dont cinq que le dépôt n'avait pas.

  **Et la lecture a corrigé un chiffre.** Le dépôt portait le montant MENSUEL
  maximal multiplié par douze — 708,95 × 12 = 8 507,40 € pour 2010 —, quand
  l'article fixe **8 507,49 € par an**, dont le mensuel arrondi se déduit. Neuf
  centimes, et le sens de la dérivation rétabli : le texte fixe l'annuel.

  Ce que l'article tait reste `haute`, et il en tait la moitié : il n'est pas
  réécrit à chaque revalorisation. Sa version d'octobre 2014 tient jusqu'en
  avril 2018 sur un seul montant, alors que l'allocation a monté en 2016 et en
  2017 ; et il s'arrête en 2020. Les ancres de 2007, 2016, 2017 et d'après 2020
  disent donc ce que le code ne dit pas.

**Ce que cela veut dire concrètement.** Les carrières entamées après 1950 —
c'est-à-dire les générations nées à partir de 1930 environ, soit la quasi-totalité
des cas simulés — reposent désormais sur des séries recontrôlées. Les **écarts
entre les trois scénarios** restent plus robustes encore que les niveaux : ils
sont calculés sur les mêmes carrières, avec les mêmes séries, et une erreur
résiduelle se propage dans le même sens aux trois scénarios.

---

## 2. La règle d'indexation domine le scénario rétroactif

Le modèle revalorise par défaut sur la croissance de la masse salariale — le
taux d'équilibre de la répartition. Ce qui suit décrit la règle demandée, le
triple lock inversé (`indexation=triple_lock_inverse`), parce que c'est elle
qui porte les écarts les plus lourds ; les limites propres à la règle par défaut
sont énoncées à la fin de cette section.

Le triple lock inversé, pris à la lettre, retient le minimum entre deux taux
**nominaux** (inflation, salaire moyen) et un taux **réel** (productivité). Dès
que l'inflation dépasse la croissance de la productivité, c'est cette dernière
qui l'emporte.

Sur 1941-2025, les comptes sont revalorisés ×4,9 quand les prix sont multipliés
par 322,2 : **une cotisation de 1950 conserve 1,5 % de sa valeur réelle.**

Conséquence : dans le scénario rétroactif, l'essentiel de la baisse affichée
vient de la règle d'indexation, pas du passage aux comptes notionnels. Les deux
effets ne sont pas séparables par lecture directe du tableau.

Pour les distinguer :

Comparer, sur la même carrière, la règle « triple lock inversé, tout en
nominal » et la règle « revalorisation portée au compte » — le sélecteur
d'indexation du formulaire, ou `mode_indexation` en Python.

La variante nominale conserve 69 % du pouvoir d'achat sur la même période, tout
en restant plus sévère que l'indexation sur les prix. C'est probablement ce que
vise l'intention d'une règle d'indexation prudente ; le choix reste ouvert.

### Les DEUX règles d'indexation, et celle qui manquait

*Corrigé le 19 septembre 2026, sur une question du Parti libéral français : « la
pension à compte notionnel est indexée sur la masse salariale alors que la
garantie vieillesse reste indexée comme l'ASPA ; c'est bien avec l'inflation
qu'est indexée l'ASPA ? »*

Oui — article `L. 816-2` du code de la sécurité sociale, version en vigueur
depuis le 31 décembre 2018 (`LEGIARTI000036393188`) : les montants de
l'allocation et ses plafonds de ressources « sont revalorisés au 1er janvier de
chaque année par application du coefficient mentionné à l'article `L. 161-25` ».
Et `L. 161-25` (`LEGIARTI000031781092`, en vigueur depuis le 1er janvier 2016)
fixe ce coefficient à « l'évolution de la moyenne annuelle des prix à la
consommation, hors tabac, calculée sur les douze derniers indices mensuels […]
publiés par l'INSEE l'avant-dernier mois qui précède la date de
revalorisation », avec un plancher à un : l'ASPA ne baisse jamais en euros
courants. C'est la règle des pensions du régime général (`L. 161-23-1`), et
c'est pourquoi `D. 815-1` a cessé de suivre le montant servi (voir plus haut).

**Mais la question en cachait une autre, et celle-là portait un défaut.** Un
système à comptes notionnels a DEUX règles d'indexation : celle qui fait
grossir le compte pendant la carrière, et celle qui revalorise la pension une
fois qu'elle est servie. Les pays qui ont fait ce système les règlent
séparément — la Suède revalorise le compte sur l'indice des salaires et la
pension liquidée sur ce même indice diminué de 1,6 point ; l'Italie revalorise
le compte sur le PIB et la pension liquidée sur les prix.

Le dépôt n'en portait qu'une. Le moteur calcule une pension AU MOMENT DE LA
LIQUIDATION et s'arrête là, et les masses de la page « Coût » figeaient cette
pension en euros constants pour toute la retraite. C'est une indexation sur les
PRIX qui ne disait pas son nom. Elle est juste pour le scénario 1, où c'est la
loi, et pour la garantie vieillesse, que `L. 816-2` y renvoie. Elle est fausse
pour les cinq scénarios notionnels, dont le contrat promet autre chose — et le
modèle le savait déjà, ailleurs : le diviseur de conversion vaut l'espérance de
vie résiduelle parce que `taux_anticipe_conversion` est nul, et il ne la vaut
QUE si la rente est ensuite revalorisée au taux qui a fait grossir le compte.
**Le modèle promettait une rente indexée sur la masse salariale et en servait
une indexée sur les prix.** Il payait moins que son propre contrat, et l'écart
ne se simplifiait pas dans le rapport au scénario 1, puisque celui-là, lui,
était correct.

**Et le stock, le jour de la bascule.** La seconde règle pose une question de
plus pour les réformes qui ne commencent qu'à une date : que deviennent les
pensions déjà servies ce jour-là ? Jusqu'au 20 septembre 2026, le modèle les
faisait toutes passer à la règle du compte, la masse salariale, au motif que
c'est ce que les réformes réelles ont fait pour les prix en 1987. C'était
offrir aux retraités de 2026 un demi-point par an pendant quinze ans, que
personne n'avait cotisé, et c'est ce qui dessinait sur la page Coût une bosse
de dépense de 2026 à 2040 — jusqu'à 7,5 % au-dessus du système actuel en 2039
pour le système 5, avec la trajectoire d'emploi du COR. Depuis cette date, le
défaut est l'inverse, et il est celui du droit : une pension liquidée sous le
système actuel garde l'indice des prix de l'article L. 161-23-1 jusqu'à son
extinction, et seuls les comptes ouverts sous le nouveau régime suivent sa
règle (`Parametres.revalorisation_stock`, réglage « Pensions en cours à la
bascule » du formulaire). Mesuré le jour du changement, trajectoire du COR : le
système 3 ne dépasse plus jamais le système actuel, le 5 culmine à 1,1 % en
2039 au lieu de 7,5 %, et le solde de 2039 s'améliore de 0,6 à 0,8 point de PIB
selon le système ; en 2070, rien ne bouge, le stock étant éteint. Pour la
proposition, dont le compte est rétroactif, le stock fictif est revalorisé sur
sa règle jusqu'à la bascule puis gelé : c'est une convention, dite ici. La
réindexation reste une variante, mesurée par un témoin.

L'écart vaut 0,69 point par an en projection — 2,45 % de masse salariale contre
1,75 % de prix —, soit ×1,15 sur vingt ans de retraite et jusqu'à ×2,96 pour
les vingt années qui suivent une liquidation de 1960. `RevalorisationServie`
l'applique désormais, et l'applique à la règle en vigueur quelle qu'elle soit :
sous le triple lock inversé, qui passe sous les prix la plupart des années, son
coefficient descend en dessous de un et la correction joue à la baisse.

| Solde moyen 2026-2070 | avant | après |
|---|---|---|
| 1. Système actuel | −1,13 % | −1,13 % |
| 2. Notionnel rétroactif, part salariale | +7,92 % | +7,49 % |
| 3. Notionnel dès 2026, part salariale | +1,79 % | +1,01 % |
| 4. Notionnel rétroactif, salariale + patronale | +2,06 % | +1,00 % |
| 5. Notionnel dès 2026, salariale + patronale | −0,04 % | **−0,93 %** |
| 6. Notionnel rétroactif, 18 % dès 2026, garantie | +0,12 % | **−0,88 %** |

Le scénario 6 perd un point de PIB de solde moyen et passe sous zéro ; le
scénario 5 perd son année d'équilibre, qu'il atteignait en 2047. Le scénario 1
ne bouge pas d'un millième, ce qui est le contrôle de la correction : c'est le
seul dont la règle n'a pas changé.

**Ce que la correction fait aux scénarios PROSPECTIFS, et qui se voit.** Les
scénarios 3 et 5 changent la règle à compter de la bascule, pour tout le stock
des pensions en cours — c'est ce que font les réformes réelles, et c'est le
choix du programme. Une réforme prospective fait donc DEUX choses le même
jour : elle ferme l'ancien barème aux nouveaux liquidants, ce qui joue à la
baisse et met une génération à peser, et elle fait passer les retraités déjà
là à une indexation plus généreuse que les prix, ce qui joue à la hausse et se
voit tout de suite. Le rapport au système actuel monte donc d'abord — jusqu'à
dépasser 1 pour le scénario 5, qui porte le plus de droits — avant de tomber.
**Les premières années d'une réforme prospective coûtent plus cher que le
système qu'elle remplace, et non moins.** Ce premier temps dure cinq ans, qui
sont le pas de la grille de générations : passé lui, la décroissance est
stricte jusqu'à l'horizon.

Ce qui ne change pas : la pension INDIVIDUELLE affichée par la page de
simulation, qui est celle de la liquidation et ne l'a jamais été d'une autre
année. La correction ne porte que sur les masses.

**Ce document, le README et le site ont longtemps désigné `indexation=prix`
comme la règle qui neutralise l'indexation.** C'était faux, et l'erreur n'était
pas petite : le régime général ne revalorise les salaires portés au compte sur
les PRIX que depuis 1987 ; auparavant, les arrêtés suivaient les SALAIRES. Sur
1941-2025, le coefficient réellement appliqué vaut ×1 538 quand les prix font
×322,2 — un facteur cinq. Comparer le compte notionnel à une indexation sur les
prix, ce n'était donc pas le comparer au droit positif, c'était le comparer à
une troisième règle qui n'a jamais existé, et attribuer aux comptes notionnels
un écart qui venait encore de l'indexation. Le mode
`revalorisation_portee_au_compte` sert désormais les coefficients des arrêtés
eux-mêmes — ceux que le scénario 1 applique déjà pour son salaire de référence —
et c'est lui, et lui seul, qui isole l'effet propre des comptes notionnels.

Ce que la correction déplace reste modeste, et il faut le dire aussi : les
cotisations se concentrent sur les dernières années d'une carrière, où les deux
règles coïncident. La ligne de référence du scénario rétroactif passe de
-89,9 % à -84,7 % pour la génération 1920, de -89,0 % à -87,5 % pour 1930, et
ne bouge pas pour 1945 (-85,1 %) — et l'écart change de signe pour les carrières
entièrement postérieures à 1987 (-81,0 % à -81,4 % pour 1958), les arrêtés
ayant depuis 1990 revalorisé un peu moins vite que les prix. L'erreur portait
sur l'indice cumulé et sur ce qu'on en disait, pas sur l'ordre de grandeur des
résultats.

Deux autres variantes gardent les mêmes trois termes et ne changent que la
statistique — `indexation=mediane_trois_taux` et
`indexation=moyenne_trois_taux`. Elles ont leurs propres limites, symétriques
de celle ci-dessus :

- la **médiane** cesse d'être une règle d'austérité. Sur 1941-2025 elle revalorise
  les comptes ×397,6 quand les prix font ×322,2 : elle rend le scénario
  rétroactif un peu plus généreux que l'indexation sur les prix. Ce n'est pas un
  défaut de calcul, c'est ce que produit le fait de retenir, trois années sur
  quatre, un terme nominal ;
- la **moyenne** hérite du mélange nominal/réel de façon permanente : chaque
  année, un tiers du taux est un taux réel. Sa sévérité (×175,7, soit 54,5 % du
  pouvoir d'achat) ne mesure donc pas une intention de prudence mais un artefact
  de construction, et le taux obtenu n'est celui d'aucun agrégat publié. À lire
  comme un contrefactuel, pas comme une règle candidate.

La règle d'équilibre — `indexation=masse_salariale`, la croissance de
l'assiette des cotisations — a elle aussi ses limites, et elles ne sont pas du
même ordre :

- **périmètre.** Le taux d'équilibre est celui du système entier ; les scénarios
  2 et 3 ne portent au compte que la part salariale. Leur adosser ce rendement
  mélange deux périmètres, et flatte le résultat. Les scénarios 4 et 5, qui
  portent la cotisation entière, sont les seuls auxquels cette règle se compare
  sans biais ;
- **1930-1949 est estimé.** Les comptes nationaux ne remontent pas avant 1949 et
  aucune série d'emploi salarié ne couvre la guerre : ces vingt années supposent
  l'emploi salarié constant. L'hypothèse est fausse — l'emploi s'est effondré
  puis reconstitué — et elle porte sur les années les plus lourdes du scénario
  rétroactif ;
- **la projection ne reconduit pas la croissance passée de l'emploi.** Au-delà
  de 2025, l'emploi suit par défaut le scénario de référence du COR de juin
  2026 — +4,7 % cumulés en 2040, −6,0 % en 2070 —, et non plus l'emploi
  constant d'avant le 20 septembre 2026, gardé en variante. Ni l'un ni l'autre
  ne reconduit le point de croissance annuelle de 1950-2025 : le rendement
  projeté reste celui du salaire moyen, à quelques dixièmes près, et la règle
  est nettement moins généreuse en projection qu'en rétrospective. L'écart
  entre générations anciennes et récentes en vient pour partie de là, non d'un
  effet de la réforme simulée.

Le **lissage pluriannuel** (`lissage=N`) s'applique à n'importe laquelle des
neuf règles, et appelle deux réserves distinctes :

- **sur les cumuls longs, une moyenne glissante n'est pas neutre.** Le produit
  des moyennes revient à mesurer la croissance depuis une base reculée d'environ
  la moitié de la fenêtre, ce qui gonfle d'une vingtaine de pour cent le
  coefficient affiché sur 1941-2025 à cinq ans — sans qu'aucune série ait
  changé. Les tableaux de cumul lissé se lisent avec cette précaution ; sur une
  carrière, l'effet retombe à un ou deux points ;
- **la règle italienne n'est reprise que par son taux.**
  `indexation=pib_nominal&lissage=5` est bien la formule de revalorisation des
  comptes notionnels italiens, mais le modèle n'en reprend ni le décalage de publication
  de deux ans, ni les coefficients de transformation, ni les planchers. C'est
  une indication, pas une reproduction du système italien.

---

## 3. Le scénario « système actuel » est une approximation

Reproduire exactement le droit positif de tous les régimes depuis 1930 suppose
un moteur législatif complet, du type de ceux de la DREES (TRAJECTOiRE) ou de
l'Institut des politiques publiques (PENSIPP). Écarts connus :

- **régimes en points** — la pension est calculée en points, sur l'historique
  réel des valeurs d'achat et de service (Agirc depuis 1947, Arrco depuis 1949,
  Ircantec depuis 1949), avec conversion des points aux fusions. S'y ajoutent
  depuis peu deux régimes dont le barème n'est pas un prix d'achat mais un
  NOMBRE DE POINTS par tranche d'assiette : le régime de base des professions
  libérales (525 points au plafond jusqu'en 2024, 557 depuis 2025, 25 sur la
  seconde tranche) et la complémentaire agricole (100 points pour 1 820 SMIC).
  Le même régime de base en connaît une troisième forme pour ce qui précède
  2004 : CENT POINTS PAR TRIMESTRE VALIDÉ, sans égard au montant cotisé. La complémentaire des
  avocats les a rejoints, avec le prix d'achat publié par la CNBF et les cinq
  tranches en euros de la classe C1, depuis 2019 seulement — les tranches
  antérieures ne sont pas publiées. Restent au rendement instantané le RCI et le
  RAFP, faute d'un prix d'achat publié ;
- **montée en charge des réformes** — le modèle a trois horloges, comme le
  droit. Ce qui s'ACQUIERT est lu à l'année travaillée : taux de cotisation,
  assiette et ses bornes, plafond de la Sécurité sociale, prix d'achat du point,
  heures de SMIC pour valider un trimestre. Ce qui commande la MONTÉE EN CHARGE
  est lu à la génération : durée requise, âge d'ouverture, âge d'annulation de
  la décote, coefficient de minoration et nombre d'années retenues au salaire de
  référence — quatre de ces cinq tables sont lues dans le texte même des
  articles du code, et recontrôlées à chaque exécution. Ce qui LIQUIDE est lu à l'année
  de liquidation : formule du régime, valeur de service du point, décote de la
  fonction publique et barème du minimum garanti, comme leurs articles
  l'écrivent. Reste approchée la montée en charge propre à chaque régime
  spécial ;
- **avantages datés** — la fiche de chaque période dit ce que le régime
  accordait cette année-là, et le moteur ne sert que cela : ni minimum
  contributif avant 1983, ni surcote avant 2004, ni trimestres pour enfants
  avant 1972. Restent hors du modèle les avantages familiaux des régimes que
  leur fiche ne déclare pas, faute de barème sourcé : le régime de base des
  professions libérales, celui des avocats, et celui des exploitants
  agricoles. La SURCOTE de l'Ircantec, elle, en est sortie : le IV de
  l'article 16 de l'arrêté du 30 décembre 1970 est servi depuis le
  1er janvier 2010, à ses deux taux — 0,75 % par trimestre entier écoulé
  au-delà de l'âge du taux plein, 0,625 % par trimestre cotisé au-delà de la
  durée requise en deçà de cet âge —, et le coefficient d'un régime en points
  peut désormais dépasser un, des deux côtés du portage. Les neuf autres
  régimes en points dont la fiche écrit une surcote la servent aussi depuis
  l'action 22, chacun à sa règle, lue dans son texte : la CNAVPL et la MSA des
  non-salariés à celle du régime général — trimestres cotisés au-delà de l'âge
  légal et de la durée requise, R. 643-8 et D. 732-42 —, les sept
  complémentaires de sections libérales À L'ÂGE SEUL, en trimestres civils
  entiers écoulés depuis l'âge que leurs statuts nomment — soixante-deux ans à
  la CARMF et à l'ASV, soixante-cinq à la CAVEC, l'âge du taux plein à la
  CARPIMKO, à la CAVP, à la CPRN et à la CIPAV —, et bornés comme ils le
  sont : soixante-dix ans chez les médecins et, jusqu'en 2023, les notaires,
  vingt trimestres à la CAVEC et à la CARPIMKO, douze à la CAVP, années
  pleines seulement à la CIPAV et à la CARMF d'avant 2017. Rien n'est servi
  avant le texte qui date chaque règle, et les taux que les fiches
  reportaient en arrière sans texte — 0,75 % à la CARPIMKO, 1 % à la CPRN —
  sont ceux des arrêtés. Ce que la fiche ne porte pas est dit dans ses
  notes : la CIPAV ne majore que les points des trente premières années, la
  CAVP borne les générations 1951 à 1955 à un ou deux ans, la CNAVPL sert
  1,25 % aux liquidations de 2024 et non aux trimestres accomplis depuis
  septembre 2023, la MSA ramène à 0,75 % l'escalier de 3, 4 et 5 % d'avant
  2009 ;
- **revalorisation des salaires portés au compte** — le modèle ne les
  reconstitue plus, il les LIT dans la circulaire annuelle de la Cnav
  (`legislation/revalorisation_salaires.csv`, perceptions 1930-2025). Il les
  approchait par « les salaires jusqu'en 1986, les prix depuis » ; cette
  approximation sur-revalorise les salaires anciens de 12,1 % sur 1970-2018.
  Dix colonnes publiées sont dans le dépôt ; hors d'elles, le coefficient est
  ancré sur la plus proche, et l'approximation ne reprend toute la main
  qu'avant 1930, où elle joue À LA HAUSSE ;
- **départs anticipés** — la carrière longue est modélisée, et sert à dire si le
  droit ouvre la liquidation demandée. La pénibilité, l'invalidité, l'inaptitude
  et le handicap ne le sont pas : ils demandent des informations médicales ou
  professionnelles que le modèle ne collecte pas ;
- **polypensionnés** — chaque régime liquide sur ses seules années, et la
  durée acquise dans chacun est comptée séparément ; mais un régime et celui
  qui lui succède ne sont pas deux régimes, et liquident ensemble (voir « Les
  régimes alignés » ci-dessous). Restent hors du modèle les règles de
  COORDINATION entre régimes alignés DISTINCTS : proratisation croisée du
  salaire annuel moyen, et liquidation unique (LURA).

Un écart de quelques pour cent avec la pension réelle est attendu.

### Le profil de carrière, et les trois choses qu'il suppose

Le modèle ne connaît pas la carrière de celui qui se simule : il en construit
une à partir d'un niveau de revenu et d'un PROFIL, qui dit comment ce revenu se
déforme avec l'âge. **Ce profil valait trois nombres écrits à la main** — 60 %
du niveau saisi au premier emploi, 130 % au dernier, 190 % pour un cadre —,
sans source, dans un dépôt dont la règle est qu'une valeur non lue à la source
n'entre pas. Il pèse pourtant lourd : à salaires cumulés identiques, passer du
profil plat au profil ascendant déplaçait de **sept points** l'écart affiché
entre le système actuel et la proposition, parce que le premier ne retient que
les vingt-cinq meilleures années et se trouve donc flatté par un profil montant,
là où un compte notionnel compte toutes les années.

Il est lu depuis le 19 septembre 2026, et sa pente était **trop forte d'un
tiers** : ×1,69 de 26 à 55 ans contre ×1,30 observé pour un employé, ×2,42
contre ×1,86 pour un cadre. Trois réserves restent, et aucune n'est comblable
par une donnée qui existe :

- **Avant 1962, rien.** L'INSEE ne ventile pas le salaire par âge plus tôt, et
  le modèle liquide depuis 1941 : les carrières commencées dans les années 1920
  à 1950 n'ont aucun profil observé. La valeur de 1962 y est reconduite, comme
  le dépôt le fait pour toute série bornée.
- **Les deux bords d'âge avant 1996.** Les tranches « moins de 26 ans » et
  « plus de 60 ans » ne sont ventilées que depuis 1996. Elles ne servent qu'à
  l'interpolation aux extrémités, et le profil y est reconduit à plat plutôt que
  prolongé — prolonger la pente inventerait des salaires que personne n'a
  observés.
- **L'écart entre catégories n'est observé qu'en 2024.** C'est le seul jeu de
  l'INSEE à croiser l'âge et la catégorie socioprofessionnelle — vérifié : ni la
  série longue du privé ni celle du public ne le font. Le supposer stable dans
  le temps est une hypothèse. Elle est raisonnable, la hiérarchie cadre/ouvrier
  ne se renversant pas, mais rien ne la démontre.

**Le public a depuis son propre profil, et il en avait besoin.** Le jeu annuel
détaillé de la fonction publique croise l'âge et le statut — le seul des trois
à le faire —, et les pentes y sont très éloignées de celle du privé qu'on leur
appliquait : ×1,11 de 26 à 55 ans pour un catégorie C, ×1,22 pour un catégorie
B, ×1,56 pour un catégorie A, contre ×1,30 servi à tous. Le profil se choisit
désormais sur l'AFFILIATION, et les affiliations publiques prennent celui de
leur versant — ×1,60 pour l'État, ×1,27 pour la territoriale, ×1,32 pour
l'hospitalière —, parce qu'aucune ne porte le A, le B ou le C et que le profil
du versant pondère déjà les catégories par leurs effectifs réels. Deviner la
catégorie de chaque affiliation aurait été réinventer ce que la lecture vient
de retirer.

**Les militaires n'ont aucun profil publié** : le code `PM` de ce jeu désigne
les personnels MÉDICAUX de l'hospitalière, à 6 765 € nets par mois, et non des
militaires — aucun jeu de l'INSEE ne porte la solde indiciaire par âge. Les cas
types militaires prennent donc le profil de l'État.

**Les régimes spéciaux portent une correction, et c'est l'hypothèse la plus
forte du modèle.** Aucune source française ne ventile leur salaire par âge —
sept pistes ont été parcourues et fermées, le relevé est sous l'action
correspondante de la feuille de route. L'enquête européenne sur la structure
des salaires, elle, ventile par âge et par SECTION d'activité, et deux sections
tombent sur un périmètre de régime plutôt qu'à côté : `D`, électricité et gaz,
est le champ du statut des IEG ; `H`, transports et entreposage, est plus large
que la SNCF et la RATP mais c'est là qu'elles sont.

Cette source est **agrégée par secteur**, donc impropre à décrire une carrière :
elle mélange l'effet d'âge et un effet de composition, et aucune source ne
croise les trois dimensions — vérifié chez Eurostat comme chez l'INSEE. Le
modèle n'en prend donc qu'un RAPPORT de pentes, secteur sur ensemble de
l'économie : ×1,38 pour l'électricité-gaz, ×0,93 pour les transports, ×1,40
pour la finance. **Cela suppose que ce rapport est le même à l'intérieur des
catégories qu'en agrégé, et rien ne le démontre.** C'est un choix assumé :
sans lui, ces régimes n'auraient aucune correction du tout.

Deux garde-fous. Les facteurs ne sont retenus que s'ils tiennent d'une vague à
l'autre — dix pour cent d'écart entre 2018 et 2022 : les **mines** passent de
0,93 à 1,19 et les **spectacles** de 0,83 à 1,08, ce sont de petits secteurs,
leur facteur n'est que du bruit, et leurs régimes gardent le profil du privé
sans correction. Et la France ne publie que trois tranches d'âge à ce niveau,
ce qui borne la finesse de la pente.

### Ce que dit la confrontation à une seconde implémentation

Le scénario 1 est l'étalon : tous les écarts affichés se mesurent par rapport à
lui, et il n'avait aucune contre-expertise. Aucun simulateur officiel n'est
automatisable — M@rel exige FranceConnect et le relevé de carrière réel, sans
mode anonyme ni API — et relire deux fois le même code ne prouve rien : une
réimplémentation écrite par la même main hérite des mêmes hypothèses.

**OpenFisca-France-Pension** comble ce trou. Ce n'est pas une source officielle,
c'est un autre MODÈLE — le module « retraites » de l'écosystème OpenFisca — mais
il est écrit par d'autres à partir des mêmes textes.
`scripts/fetch/openfisca_regime_general.py` y calcule dix profils à salaire
nominal constant et fige le relevé dans `tests/temoins/`, que `tests/test_oracle.py`
rejoue sans avoir à installer le paquet.

**Cinq familles de régimes y passent aujourd'hui**, et c'est tout ce
qu'OpenFisca expose : le régime général, la pension civile (État et CNRACL),
l'Arrco d'avant 2019, l'Agirc des cadres et l'Ircantec des agents non
titulaires — cinquante-huit profils en tout. Les régimes alignés — MSA des
salariés agricoles, artisans, commerçants — n'ont chez lui aucun module, et
n'en ont pas besoin : la loi les calcule comme le régime général, et c'est à
l'oracle du régime général qu'ils se confrontent. Restent hors de portée le
régime unifié Agirc-Arrco, dont son code lève une exception, et tout ce qui
n'est ni salarié ni fonctionnaire : les régimes spéciaux, les libéraux, les
exploitants agricoles, que personne d'autre ne modélise. Les exploitants sont
le seul trou qui porte plus d'un million d'assurés — 1 023 064 retraités de
droit direct en 2024 —, et il ne se comblera pas par cette voie : leur régime
est MIXTE, une retraite forfaitaire plus une proportionnelle en points, sans
équivalent au régime général auquel l'opposer.

Le résultat, sur dix profils — et les régimes alignés le partagent, puisque
leur pension est celle du régime général :

| Grandeur | Accord |
|---|---|
| Durée d'assurance | **exacte** sur les dix |
| Trimestres de décote | **exacts** sur les dix |
| Taux de liquidation | **exact** sur les dix |
| Coefficient de proratisation | **exact** sur les dix |
| Salaire annuel moyen | jusqu'à 2,35 %, **et c'est OpenFisca qui s'écarte de la source** |
| Pension de base | l'écart du salaire annuel moyen, et rien d'autre |

Le décompte des trimestres de décote est le contrôle le plus exigeant du lot :
il met en jeu la durée requise par génération, l'âge d'annulation par
génération, la règle du minimum entre les deux décomptes, le plafond de vingt
trimestres et l'arrondi à l'entier supérieur. Cinq tables et trois règles
tombent juste ensemble, dix fois.

Le salaire de référence, lui, a divergé — et l'enquête qu'il a déclenchée a
trouvé une erreur de chaque côté, la nôtre d'abord.

Il s'écartait de +0,30 % à +7,55 %, toujours dans le même sens, parce que le
modèle APPROCHAIT les coefficients de revalorisation des salaires portés au
compte : « les salaires jusqu'en 1986, les prix depuis ». Mesurée sur les
coefficients réels, cette approximation sur-revalorise les salaires anciens de
**12,1 % sur 1970-2018** et de **13,6 % sur 1980-2018**. L'erreur comptait
double, parce que la grandeur compte double : le salaire de référence retient
les N MEILLEURES années, et « meilleures » se juge sur des salaires revalorisés
— changer les coefficients ne déplace pas seulement le niveau de chaque année,
cela change lesquelles sont retenues.

Le dépôt a d'abord repris la table cumulée d'OpenFisca, faute d'avoir cherché
plus haut. **C'était une erreur de méthode, et elle a duré un commit.** Une
seconde implémentation est une contre-expertise ; ce n'est pas une source. La
source existe : la Cnav publie chaque année, dans sa circulaire de
revalorisation, la table entière des coefficients qu'elle applique. Confrontée à
celle du 9 janvier 2023, la table d'OpenFisca s'en écarte :

- de **−3 % à −5,5 %** sur toutes les perceptions postérieures à 1990, un
  déficit à peu près uniforme — c'est la revalorisation exceptionnelle de 4 % du
  1<sup>er</sup> juillet 2022 (loi « pouvoir d'achat ») qui lui manque ;
- de **−17 % à +10 %**, sans régularité, sur les années 1949-1962.

Le modèle lit donc la circulaire, et le désaccord résiduel avec OpenFisca —
jusqu'à 2,35 %, toujours dans le même sens — n'est plus le nôtre.

**Le coefficient se lit dans une colonne, par rapport de deux de ses valeurs.**
L'arrêté annuel applique un coefficient unique à tous les salaires déjà portés
au compte, quelle que soit leur année de perception : une colonne suffit donc,
en théorie, à en reconstruire toutes les autres.

En pratique, non — et c'est mesuré. La caisse arrondit sa table publiée à trois
décimales et repart chaque année de la précédente : les arrondis s'accumulent, et
reconstruire une colonne depuis une autre dérive avec la distance.

| Colonne reconstruite | depuis 2026 | depuis la colonne voisine |
|---|---|---|
| 2024 (2 ans) | 0,02 % | 0,02 % |
| 2023 (3 ans) | 0,07 % | 0,01 % |
| 2022 (4 ans) | 0,10 % | 0,03 % |
| 2021 (5 ans) | 0,13 % | 0,01 % |
| 2020 (6 ans) | 0,14 % | 0,01 % |
| 2019 (7 ans) | 0,16 % | 0,01 % |

Le dépôt n'a d'abord gardé que la colonne la plus récente, en annonçant 0,13 %
sur la foi d'un seul recoupement. **Dix colonnes sont maintenant dans le dépôt**,
de 2017 à 2026 : le modèle sert la colonne publiée quand elle existe — l'écart
est alors nul, pas petit — et ancre sinon sur la plus proche, ce qui divise la
dérive par dix. Le récupérateur recoupe chaque colonne contre chacune des autres
à chaque exécution et refuse d'écrire si l'une s'écarte, et deux tests rejouent
les colonnes figées dans `tests/temoins/`.

Ce document a un temps affirmé qu'« aucune formule ne reproduit les arrêtés,
une série d'ancrages fuit de 20 % ». Cette mesure portait sur la table
d'OpenFisca : ce sont ses incohérences qu'elle mesurait, pas celles du droit.

Ce que cela ne referme pas, et les trois bornes sont différentes.

- **Avant 2017**, aucune circulaire n'est accessible en ligne : les liquidations
  antérieures sont reconstruites depuis la colonne d'octobre 2017, la plus
  proche, et la dérive y est **invérifiable**. Extrapolée depuis le profil
  mesuré ci-dessus, elle croît d'environ trois centièmes de pour cent par année
  d'écart.
- **Après 2026**, le coefficient est ancré sur la dernière colonne et
  l'approximation ne couvre que les dernières années ; avant 1930, il n'y a rien
  sur quoi ancrer et elle reprend toute la main, à la hausse.
- **Le mois existe désormais, et il désigne la colonne applicable.** Le modèle
  retenait l'état au 1<sup>er</sup> janvier : la revalorisation s'étant
  appliquée au 1<sup>er</sup> avril de 2009 à 2013, puis au 1<sup>er</sup>
  octobre jusqu'en 2017, une liquidation de cette période était lue avant la
  revalorisation de son année — **0,52 % en médiane, 0,93 % au maximum**,
  toujours à la baisse. Le cas le plus lourd n'était pas celui-là : la
  **revalorisation exceptionnelle du 1<sup>er</sup> juillet 2022** dépasse celle
  du 1<sup>er</sup> janvier de **3,9 %**, et toutes les liquidations du second
  semestre 2022 lisaient la colonne de janvier. La colonne retenue est
  maintenant la plus récente dont la date d'effet n'est pas postérieure à la
  liquidation, ce que le mois suffit à trancher. Ce qui reste : les années
  qu'aucune circulaire ne couvre, où le modèle passe par la colonne la plus
  proche et son rapport de deux valeurs — le mois n'y change rien, faute de
  colonne à désigner.

Les régimes qui liquident sur le dernier traitement ou les six derniers mois ne
portent aucun salaire à un compte : les coefficients de la Cnav ne leur sont pas
appliqués.

Trois désaccords sont sortis de la confrontation, **et pas tous du même côté**.
Chez nous : la durée de proratisation, confondue avec la durée requise, et les
coefficients de revalorisation, approchés au lieu d'être lus — corrigés tous
deux, et ce sont les paragraphes précédents. Chez lui, deux fois. Sa table de
revalorisation, à laquelle il manque la revalorisation exceptionnelle de juillet
2022 — c'est le paragraphe précédent. Et : une table de durée requise
antérieure à la réforme du 14 avril 2023, qui oppose 169 trimestres à la
génération 1965 là où l'article L. 161-17-3, lu dans la base LEGI, en donne 172.
**Un désaccord ne désigne donc pas d'office le coupable.**

Quatre bornes à connaître, et elles sont étroites :

* **le régime unifié Agirc-Arrco est hors de portée.** Son code demande le
  paramètre `agirc_arrco.salaire_de_reference.salaire_reference_en_euros`, que
  les barèmes livrés ne définissent pas — ils portent
  `salaire_reference_prix_achat_valeur_nominale`. Toute liquidation postérieure
  à 2019 y lève une erreur. L'Arrco d'avant, lui, se confronte : voir plus bas ;
* **les liquidations antérieures à 2025.** Ses barèmes s'arrêtent : valeur du
  point Agirc-Arrco en novembre 2024, revalorisations CNAV en 2023. Cinq des
  sept générations de la grille de cas types sont hors de portée ;
* **il rend zéro sans se plaindre.** Sans `simulation.max_spiral_loops`, la
  durée d'assurance, le coefficient de proratisation et la pension valent tous
  zéro, sans qu'aucune exception ne soit levée. Un oracle silencieusement nul
  valide tout : le récupérateur refuse donc d'écrire un profil dont la durée ou
  la pension serait nulle, et le test le revérifie ;
* **et ce même réglage a une borne HAUTE**, découverte en écrivant les oracles
  de l'Agirc et de l'Ircantec. Le total de points d'un régime en points lit le
  total de l'année précédente et remonte ainsi jusqu'à ce que
  `max_spiral_loops` l'arrête. Laissé à cent, il atteint 1947 à l'Agirc, dont
  la formule de points commence au 1<sup>er</sup> janvier quand son prix
  d'achat commence au 1<sup>er</sup> avril, et 1910 à l'Ircantec, dont la
  cotisation lit un plafond de la Sécurité sociale qu'OpenFisca ne définit pas
  avant 1931 : `ParameterNotFoundError` dans les deux cas. Le nombre de
  reprises est donc calculé pour que la remontée s'arrête à la première année
  sûre, et le récupérateur vérifie qu'il couvre encore la carrière. Trop peu de
  reprises tronque la carrière en silence, trop lève une exception : la fenêtre
  est étroite des deux côtés.

#### La pension civile : deux erreurs chez nous, une transcription chez lui

`scripts/fetch/openfisca_fonction_publique.py` rejoue dix profils de
sédentaires — huit à l'État, deux à la CNRACL —, sans enfant ni prime, liquidés
de 2009 à 2020, et `tests/test_oracle.py` les rejoue à son tour. La première
passe s'est écartée sur quatre profils, et l'enquête a trouvé, comme pour le
régime général, des torts des deux côtés — les nôtres d'abord, et il y en avait
deux.

**Le barème de décote de l'article L. 14 était lu à l'année de liquidation.**
Le III de l'article 66 de la loi du 21 août 2003 titre pourtant sa colonne
« Année au cours de laquelle sont réunies les conditions mentionnées au I et au
II de l'article L. 24 » — l'année où le droit s'ouvre, non celle du départ. Un
sédentaire né en 1948 réunit ces conditions en 2008 et garde 0,375 % par
trimestre et « limite d'âge moins douze trimestres » quelle que soit l'année où
il part ; parti en 2010 à soixante-deux ans, il n'a aucun trimestre de décote.
Le modèle lui opposait le barème de 2010 — 0,625 % et limite d'âge moins dix
trimestres — et deux trimestres de décote que le droit ne lui retire pas. Les
décrets de 2008 des régimes spéciaux sont écrits de même, « pour les personnes
remplissant les conditions » entre deux dates : la correction vaut pour les
deux barèmes en table, et `ScenarioActuel._annee_ouverture_des_droits` dit
désormais quel millésime se lit.

**La montée en charge 2004-2008 de la durée de services était ignorée.** Le II
du même article 66 fait monter « le nombre de trimestres nécessaires pour
obtenir le pourcentage maximum » de 150 à 160, deux par an, de 2004 à 2008 —
là encore selon l'année où le droit s'ouvre. Le modèle lisait pour ces années
la table du régime général, qui donne 160 à toute génération née depuis 1943 :
un fonctionnaire dont le droit s'ouvrait en 2007 se voyait diviser ses services
par 160 au lieu de 158, et opposer deux trimestres de décote de trop. La table
est désormais `legislation/duree_requise_fonction_publique.csv`, lue avant la
table par génération, qui ne vaut pour la fonction publique qu'à compter de
2009 ; OpenFisca la recoupe.

**Et le traitement de l'année d'avant le départ était ramené au départ par les
prix.** Un fonctionnaire garde son indice : son traitement suit le POINT, et
c'est ce que fait OpenFisca. L'écart valait de 0,5 à 0,8 % — tout ce que le
point avait fait de moins que les prix, gel de 2010-2016 compris. Le modèle
suit maintenant le point (`MinimumGaranti.ratio_point_indice`), et les régimes
spéciaux à dernier salaire restent sur les prix, avec la réserve d'avant.

**Chez lui, une transcription.** Son barème de décote porte 0,65 % pour un
droit ouvert en 2010, là où la loi écrit 0,625 % — le cinquième des huit
huitièmes de point. Le profil est gardé, et le test vérifie que chacun des deux
modèles rend exactement le taux que son coefficient commande. Sa table de durée
de services porte aussi, pour les générations 1944 à 1948, une seconde valeur
datée de 2014 — 151 à 155 trimestres — qui contredit sa propre colonne de 2003
et le texte : les profils évitent ces générations après 2013, et le
récupérateur des paramètres lit la colonne de 2003.

Le résultat, après corrections, sur dix profils :

| Grandeur | Accord |
|---|---|
| Durée de services | **exacte** sur les dix |
| Trimestres de décote | **exacts** sur les dix |
| Taux de liquidation, surcote comprise | **exact** sur neuf ; le dixième est le 0,65 % de 2010, et il se retrouve en substituant son coefficient au nôtre |
| Coefficient de proratisation | **exact** sur les dix |
| Traitement de référence | **au centime** sur les dix |
| Pension avant minimum garanti | **au centime** sur neuf, même réserve sur le dixième |
| Minimum garanti | de 4,7 à 8,5 % au-dessus de lui, toujours dans le même sens |

Le minimum garanti est le seul poste où l'écart demeure, et il est le sien :
OpenFisca le calcule au point d'indice de l'année de liquidation, quand
l'article L. 17 fige la référence au 1<sup>er</sup> janvier 2004 et la
revalorise comme les pensions — sur les prix, qui ont fait plus que le point.
Le test le borne à dix pour cent sans l'effacer.

#### L'Arrco de 1999 à 2018 : rien à corriger, et c'est le résultat

`scripts/fetch/openfisca_arrco.py` rejoue sept carrières de non-cadres qui
commencent en 1999 au plus tôt et liquident en 2018 au plus tard. Les deux
bornes sont les siennes : avant 1999, OpenFisca ne convertit pas les points de
l'UNIRS — ses prix d'achat sont en unité ancienne, ses points valorisés à la
valeur du point unifié, un facteur quatre sur toute la période — ; après 2018,
son régime unifié lève une exception. Entre les deux, vingt ans de barèmes
rejoués d'un bloc par un autre moteur : taux effectif par tranche, prix d'achat
du point, taux d'appel, valeur de service.

| Grandeur | Accord |
|---|---|
| Points acquis, tranche 2 comprise | **au millième** sur les sept |
| Valeur de service | **à la quatrième décimale**, à une convention près : le dépôt retient la valeur au 31 décembre, OpenFisca celle du 1<sup>er</sup> janvier de la liquidation, qui est la nôtre de l'année d'avant |
| Trimestres de décote du régime général, qui commandent l'abattement | **exacts** sur les sept |
| Coefficient d'anticipation | **exact** quand l'anticipation tombe sur des années pleines ; ailleurs OpenFisca tronque à l'année, et ne peut que servir plus |

Deux pièges de sa mécanique, à connaître pour choisir les profils : il ne lit
son barème d'anticipation que par année entière, en tronquant les trimestres,
quand l'Arrco l'écrit par trimestre ; et il compte l'âge à la liquidation en
convertissant des jours en mois par une durée moyenne du mois, si bien qu'un
assuré né le 1<sup>er</sup> janvier 1945 parti le 1<sup>er</sup> janvier 2007 a
chez lui « 61 ans et 11 mois » et treize trimestres de décote au lieu de douze
— un écart de soixante-deux ans traverse quinze années bissextiles quand il
part d'une année impaire, seize quand il part d'une année bissextile. Les
profils partent d'années bissextiles.

#### L'Agirc des cadres, 1983-2012 : trois écarts, tous chez lui

`scripts/fetch/openfisca_agirc.py` rejoue dix carrières de cadres. L'Agirc n'a
pas la mécanique de l'Arrco : elle ne cotise qu'**au-dessus du plafond** de la
Sécurité sociale — la tranche B, d'un à quatre plafonds —, y ajoute la
tranche C au-dessus de quatre plafonds à compter de 1991, et garantit depuis
1989 un nombre minimal de points à tout cadre cotisant. Trois règles que la
confrontation précédente ne mettait pas à l'épreuve.

Le témoin porte les points de **chaque année**, et le test les oppose un à un.
C'est ce qui permet de ne pas s'arrêter à « les deux modèles s'écartent de
0,06 % » : sur la carrière la plus longue du lot, ils s'accordent sur
dix-huit années sur vingt, et les deux qui manquent ont un nom.

| Grandeur | Accord |
|---|---|
| Prix d'achat du point et taux d'appel, année par année | **exacts** jusqu'en 2003, puis un millésime de retard chez lui |
| Cotisation de la tranche B, année par année | **exacte**, sauf 1989 et 1994 |
| Tranche C avant 1991 | il la cotise, l'Agirc non |
| Trimestres de décote du régime général | **exacts** sur les dix |
| Coefficient d'anticipation | **exact** sur les dix |
| Valeur de service | **exacte**, à la date de revalorisation près |

**Son barème salarié saute deux marches.** En 1989, le taux d'appel de l'Agirc
passe à 1,134 : son barème employeur suit — 6 % × 1,134 = 6,804 % — et son
barème salarié reste à 2,2 %, la valeur de 1987, au lieu de 2,268 %. En 1994,
son couple 8,43 / 3,63 donne 12,06 % là où le contractuel de 10 % appelé à 1,21
en fait 12,10. Le test substitue ces deux taux et l'accord redevient exact.

**Sa tranche C est cotisée par le salarié dès 1948**, quarante-trois ans avant
que l'Agirc ne l'ouvre. La cause est une case vide : son fichier de barème
EMPLOYEUR écrit `0` sur la tranche 4-8 plafonds avant 1991, son fichier SALARIÉ
y écrit `null`. OpenFisca lit le premier comme un taux nul et le second comme
une tranche ABSENTE — le taux de la tranche B s'étend alors jusqu'à huit
plafonds. Un cadre payé 150 000 € en 1983 y verse une cotisation salariale sur
une assiette que le régime n'appelle pas, et reçoit un tiers de points de trop.
Un profil est gardé pour le montrer, et le test reconstitue exactement cette
cotisation fantôme.

**Son prix d'achat se lit trois mois trop tôt.** L'Agirc a déplacé la
revalorisation de sa valeur de service du 1<sup>er</sup> janvier au
1<sup>er</sup> avril en 2001, et celle de son salaire de référence en 2004. Le
dépôt retient la valeur en vigueur au 31 décembre — celle qui vaut pour les
salaires de l'année —, OpenFisca lit le paramètre au 1<sup>er</sup> janvier,
donc le millésime précédent. C'est la même convention de date que la valeur de
service de l'Arrco, déjà documentée ; ici elle joue sur l'ACQUISITION, et donne
de 1,3 à 3,7 % de points de trop par année. Les profils s'arrêtent donc en
2003, sauf un, gardé pour la montrer.

#### L'Ircantec : deux corrections chez nous, deux transcriptions chez lui

`scripts/fetch/openfisca_ircantec.py` rejoue onze carrières d'agents non
titulaires. C'est le premier oracle du dépôt sur le secteur public
contractuel — 2 108 941 retraités de droit direct en 2024, la série certifiée
du dépôt —, et il a trouvé chez
nous deux règles que personne ne relisait. Les deux se lisent dans les textes,
que l'index LEGI rend accessibles en quelques secondes.

**L'assiette de la tranche B allait de un à huit plafonds depuis 1971.**
L'article 7 du décret n° 70-1277 écrit l'inverse : « l'assiette de cotisation
ainsi déterminée est toutefois limitée à **4,75 fois le plafond** fixé pour les
cotisations de retraite du régime général ». C'est le décret n° 2008-996 du
23 septembre 2008 qui la porte à huit — et la limite de 4,75 est plus vieille
que l'Ircantec elle-même : l'article 7 du décret n° 51-1445 la fixe déjà pour
l'IPACTE, à compter du 1<sup>er</sup> janvier 1961. Le modèle donnait donc des
points sur une assiette que le régime n'appelait pas, à tout contractuel payé
plus de 4,75 plafonds avant 2009. L'assiette `tranche_2_ircantec` porte
désormais cette borne, et les fiches la prennent jusqu'en 2008.

**Le coefficient d'anticipation était linéaire.** La fiche abattait 1,1 % par
trimestre. L'article 16 de l'arrêté du 30 décembre 1970 écrit un ESCALIER :
coefficient 0,43 dix ans avant l'âge normal, « majoré de 0,017 5 par trimestre »
jusqu'à cinq ans avant, de 0,012 5 par trimestre sur les deux années suivantes,
de 0,01 par trimestre sur les trois dernières. Ce sont, marche pour marche, les
paliers de l'Agirc-Arrco — et son paragraphe 2 est la seconde table de
l'Agirc-Arrco, qui applique le même escalier « en assimilant à l'âge de
soixante-cinq ans l'âge auquel [l'assuré] aurait effectivement accompli la durée
d'assurance », sans pouvoir descendre sous le coefficient de son âge : c'est
mot pour mot « la plus avantageuse des deux ». Le taux moyen de 1,1 % tombait
juste aux deux bouts du barème — 0,78 à cinq ans d'anticipation, 1,00 à zéro —
et nulle part entre les deux : à douze trimestres il retirait 13,2 % quand
l'arrêté en retire 12, et il ne descendait jamais à 0,43. La fiche porte
maintenant `abattement_points: ircantec`, qui est le barème de l'Agirc-Arrco
sous un autre nom, et l'exonération au taux plein que le 6° c) de l'article
accorde « à compter du 1<sup>er</sup> avril 1983 » — la date de l'ASF, la même
réforme.

Chez lui, deux transcriptions qui comptent, et deux arrondis qui ne comptent
pas.

| Grandeur | Accord |
|---|---|
| Salaire de référence et taux d'appel, année par année | **exacts**, sauf le taux d'appel de 1991 |
| Cotisation des deux tranches | **exacte** à l'arrondi du producteur près |
| Assiette de la tranche B | 4,75 plafonds chez nous et dans le décret, huit chez lui à partir de 1992 |
| Coefficient d'anticipation | **exact** sur les onze, escalier compris |
| Surcote | 7,5 % par trimestre chez lui, 0,75 % dans l'arrêté et chez nous |

**Sa tranche B passe à huit plafonds en 1992**, seize ans avant le décret qui
l'y porte. Le test reconstitue exactement ce qu'il cotise en trop, et vérifie
qu'avant 1992 et depuis 2009 les deux barèmes tombent d'accord au centime.

**Sa surcote est dix fois trop forte.** Le paragraphe 4 de l'article 16 majore
le total des points « de 0,75 % par trimestre entier écoulé entre le
soixante-cinquième anniversaire de l'assuré et la date d'entrée en jouissance » ;
son paramètre porte 0,075. Une année de surcote y vaut +30 % de pension, deux
ans +60 %. **Le modèle, lui, n'en servait aucune, et sert maintenant
l'arrêté** — c'est l'action 9 de la feuille de route, faite. La fiche porte
`surcote_points: ircantec` à partir de 2010, et le coefficient d'un régime en
points, qui ne pouvait pas dépasser un, le peut désormais : 0,75 % par
trimestre ENTIER écoulé au-delà de l'âge du taux plein — l'âge de l'article
L. 351-8, lu à la génération, et non soixante-cinq ans en dur depuis 2011 —,
et 0,625 % par trimestre COTISÉ au-delà de la durée requise entre l'âge légal
et cet âge, sans qu'une même période soit payée deux fois. Sur le seul profil
surcoté du témoin, un agent né en 1945 parti à soixante-sept ans, il servait
1,00 et sert 1,06 ; OpenFisca lui sert 1,30.

Les deux lectures ne comptent d'ailleurs pas les mêmes trimestres. OpenFisca
reprend ceux de la surcote du régime général — cotisés, au-delà de la durée
requise —, et leur applique son taux ; l'arrêté paie d'abord le TEMPS écoulé,
que ni cotisation ni durée ne conditionnent, et ne réserve l'assiette du
régime général qu'à son 2°, moins bien payé. Un agent qui cesse de travailler
à l'âge du taux plein et ne liquide que deux ans plus tard ne reçoit rien chez
lui et huit trimestres de majoration ici.

Le reste de l'écart tient à un arrondi, et il est du côté du producteur : la
Caisse des dépôts publie le taux appelé arrondi au dix-millième — 5,63 % de
1992 à 2010 —, OpenFisca sert le produit exact du contractuel par le taux
d'appel, 4,5 % × 1,25 = 5,625 %. Cinq cent-millièmes de taux, un millième et
demi de cotisation. Une seule année échappe à cette règle : **1991**, où sa
table prolonge les taux de 1989 quand la Caisse des dépôts donne 5,28 % et
16,42 %, et où son taux d'appel vaut 1,09 contre 1,173 — le désaccord que
`scripts/fetch/cdc_ircantec.py` avait déjà relevé, et que le producteur tranche.

**Ce que ces deux corrections déplacent : rien, et c'est mesuré.** Aucun des
427 témoins ne porte un contractuel payé plus de 4,75 plafonds, ni une
liquidation Ircantec avec décote. Elles ne changent donc aucun chiffre publié ;
elles changent ce que le simulateur servira à qui saisira l'une ou l'autre de
ces situations.

**Une troisième correction est sortie de là, et celle-là déplace des témoins.**
Le barème d'anticipation de l'Agirc-Arrco, comme celui de l'Ircantec, ne
s'applique « à l'âge seul » que jusqu'à l'ASF de 1983 : après, qui a le taux
plein au régime de base est exonéré. Le moteur lit cette règle dans la période
du régime **à l'année de liquidation** — ce qui est juste tant que le régime
est ouvert, et faux dès qu'il est fermé : la dernière période de l'UNIRS est
celle de 1957-1961, de l'IPACTE celle de 1951-1970, et toutes deux sont
antérieures à 1983, alors qu'aucune de leurs pensions n'a été liquidée avant.
Un salarié du privé au taux plein se voyait donc abattre sa ligne UNIRS de 4 à
22 %. Les trois fiches fermées portent désormais la lecture par génération, et
douze témoins remontent — de +4,2 % à +28,2 % sur la ligne du régime fermé,
soit +0,02 % à +0,16 % sur la pension totale, la ligne étant petite.

#### Les régimes alignés : la MSA passe, et les indépendants depuis qu'ils ne sont plus coupés en deux

OpenFisca-France-Pension n'a **aucun module** pour les régimes alignés : ni MSA,
ni artisans, ni commerçants. Il n'en a pas besoin, et le dépôt non plus :
« aligné » n'est pas une image, c'est un RENVOI d'article à article. L'article
L. 742-3 du code rural rend au régime des assurances sociales agricoles « le
titre V du livre III du code de la sécurité sociale », qui est l'assurance
vieillesse du régime général ; l'article L. 634-2 du code de la sécurité
sociale calcule, liquide et sert les pensions des artisans et des commerçants
« dans les conditions définies […] du premier au quatrième alinéas de l'article
L. 351-1 », et énumère ensuite les quinze articles du régime général qui les
gouvernent. Leur pension se confronte donc à l'oracle du régime général, sur la
même carrière, et c'est l'alignement lui-même qui est mis à l'épreuve.

Rien ne garantissait qu'il fût dans le modèle : l'action 3 de la feuille de
route a montré que les TAUX DE COTISATION agricoles, eux, n'ont été alignés
qu'en 2014, alors que le dépôt les croyait alignés depuis toujours.

**La MSA des salariés agricoles passe.** Sur les dix profils de l'oracle, elle
rend exactement la pension du régime général — même salaire de référence, même
taux, même coefficient de proratisation. Sa confrontation à OpenFisca est celle
du régime général, à la virgule près : 1 678 770 retraités de droit direct en
2024 entrent dans le périmètre contrôlé sans qu'aucun module n'existe pour eux.

**L'artisan et le commerçant passent aussi, depuis l'action 10 de la feuille
de route — et ce qui les faisait échouer n'était pas le barème.** Le taux de
liquidation et le décompte des trimestres tombaient juste ; ce qui ne tombait
pas juste, c'était le salaire de référence, parce que la carrière était coupée
à chaque changement de CAISSE. La CANCAVA devient le RSI en 2006, le RSI est
absorbé par le régime général en 2018 : le modèle liquidait ces trois régimes
séparément, chacun sur ses seules années, et calculait donc deux salaires
annuels moyens là où la caisse n'en calcule qu'un. Un artisan payé 60 000 € de
1976 à 2015 recevait « 30 077 € × 120/165 » plus « 36 778 € × 40/165 » au lieu
de « 34 152 € × 160/165 ».

La césure jouait dans les deux sens — les vingt-cinq meilleures années de
chaque morceau peuvent être meilleures que celles de la carrière entière — et
l'écart mesuré allait de **−7,2 % à +0,3 %** sur les dix profils (de −7,2 % à
+6,7 % depuis que la surcote est datée : coupé, le morceau CANCAVA d'un artisan
parti tard servait le taux plat de sa fiche de 2006 à des trimestres de 2011 à
2015, et cette erreur en compensait une autre). Ce n'était
pas la limite « coordination interrégimes » ci-dessus, mais quelque chose de
plus large qu'un polypensionnat : **un régime et celui qui lui succède ne sont
pas deux régimes**, et le catalogue le savait déjà, puisqu'il porte
`succede_a` et `integre_dans`.

Le moteur groupe maintenant les régimes d'ANNUITÉS par chaîne d'absorption
avant de liquider : un seul salaire de référence sur les années de tous les
membres, une seule proratisation, une seule ligne, sous le nom de la caisse de
la dernière période active — celle qui aurait le dossier —, dont la fiche donne
les règles. La chaîne ne se suit qu'à partir de l'année où le régime absorbé
FERME à ses affiliés : avant 2018, le régime général et le RSI sont deux
régimes, et un salarié devenu artisan qui liquide en 2010 a bien deux
pensions ; en 2020, il n'en a qu'une. Les régimes en points n'entrent pas dans
un groupe — leurs points se convertissent et s'additionnent déjà — et la
carrière qui traverse 1948 dans la fonction publique est l'autre chaîne
touchée. Sur les dix profils de l'oracle, l'artisan et le commerçant rendent
désormais exactement la pension du régime général, comme la MSA. Le
découpage d'avant reste disponible comme variante
(`calculer(..., liquider_successions=False)`), et un test le garde mesuré :
c'est de là que viennent les −7,2 % et +0,3 %.

### Ce que disent les exemples publiés par les caisses

OpenFisca est un autre modèle ; les caisses, elles, publient des EXEMPLES —
une carrière de trois lignes dont la réponse est écrite par l'organisme qui
applique la règle. `tests/temoins/exemples_officiels.yaml` en transcrit
vingt-huit, chacun avec sa source et sa date de vérification, et
`tests/test_oracle.py` les rejoue : le test construit la carrière — une
affiliation, un salaire constant, le nombre de trimestres de l'exemple, l'âge
d'entrée cherché au mois près — et compare la grandeur que l'exemple nomme.

| Source | Ce qu'elle fait rejouer | Accord |
|---|---|---|
| service-public.gouv.fr, fiches F19666 et F20349 | décote du privé et de la fonction publique, né en 1964, 159 trimestres sur 170 : taux 43,125 %, réduction de 13,75 % | **exact** |
| fiches F19643 et F16494 | surcote du privé et de la fonction publique, 4 trimestres civils après l'âge légal : +5 % | **exact**, une fois la période de référence comptée au trimestre civil |
| fiches F21552 et F36464 | taux plein à 170, taux plein à 67 ans avec 158, taux minoré à 65 ans (45 %), proratisation 158/170 | **exact** |
| actualité A15703 | minimum contributif 2026 : 170 trimestres dont 135 cotisés, 873,53 € par mois | **exact** au centime |
| circulaire Cnav 2026-07 | âges légaux et durées de la suspension pour trois dates de naissance, décote d'un né en novembre 1961 (44,375 %) | **exact**, une fois les tables réécrites |
| circulaire Cnav 2026-29 | carrière longue par génération, 1964 à 1971, ouverte à la borne et refusée un trimestre plus tôt | **exact**, une fois la borne lue par génération |
| circulaire Cnav 2018-04 | surcote à un, deux et trois taux (2,5 %, 4,75 %, 10,25 %) | **exact**, une fois le barème daté |
| fiche F16336 et circulaire carrière Cnav 2017-01, fiche 6.2b | huit trimestres par enfant au régime général — quatre de maternité, quatre d'éducation | **exact** |
| fiche F37311 | bonification de la fonction publique : quatre trimestres par enfant né avant 2004, deux pour ceux nés depuis | **exact** |
| circulaire Cnav 2022-26 | assiette de la majoration pour trois enfants : 10 % de la retraite telle qu'elle est servie, surcotée, décotée ou pile au taux plein | **exact** |

**Ce que la confrontation a trouvé, dans l'ordre.** Le premier exemple lu
contredisait les tables certifiées du dépôt : non que le récupérateur se soit
trompé, mais parce que le droit avait changé depuis le dump qu'il avait lu —
la suspension de la réforme est de décembre 2025, ses décrets de mai 2026, et
le dump LEGI du dépôt de juillet 2025. Une table certifiée est certifiée à une
date ; c'est pourquoi les lignes réécrites sont redescendues au niveau
`moyenne` plutôt que de porter un `certifiee` que rien ne soutient plus, et
pourquoi ce niveau remonte jusqu'au résultat affiché à qui est né de 1964 à
1968 — jusqu'à ce que l'action 27, le même jour, fasse relire les articles
réécrits au récupérateur dans l'index LEGI du dépôt, qui porte les
incréments quotidiens de la DILA : toutes les lignes sont redevenues
`certifiee`, sans qu'un chiffre bouge. Puis la surcote : 5 % dans les deux fiches quand le modèle en servait
6,25, parce qu'il comptait le trimestre de l'anniversaire ; et les trois
exemples de 2018, qui ne se rejouent qu'avec le taux de chaque trimestre à sa
date. Puis la carrière longue, dont la borne des vingt ans n'avait jamais été
lue par génération. Le minimum contributif, la décote, la proratisation, le
taux plein sont tombés justes du premier coup — c'est aussi un résultat.

**Six exemples de plus, le 21 septembre 2026, et ce qu'ils ont demandé de
neuf.** Les enfants n'avaient aucun témoin — ni les trimestres qu'ils
accordent, ni la majoration de 10 % —, et pour une raison de forme : aucune
caisse ne publie une carrière entière dont elle donne la durée d'assurance.
Ce qu'elle publie, c'est **le nombre de trimestres ajoutés par enfant**, et
**le taux de la majoration**. Deux grandeurs neuves ont donc été ajoutées au
banc, qui se mesurent l'une et l'autre sans rien recalculer du modèle :
`trimestres_de_majoration_enfants` rejoue LA MÊME carrière sans enfant et
compare les deux durées — l'écart, lui, ne dépend ni de l'âge d'entrée ni de
la durée requise de la génération ; `majoration_enfants_sur_pensions` rapporte
la majoration servie à la somme des pensions de régime. Les six exemples
tombent justes : 16 trimestres pour deux enfants au régime général, 24 pour
trois, 8 pour deux enfants nés avant 2004 dans la fonction publique et 4 pour
deux enfants nés depuis — et 10 % exactement dans les trois cas, sur une
carrière surcotée à 58,125 %, au taux plein, et minorée à 41,25 %.

Ce dernier point est ce que la circulaire 2022-26 tient à dire et que le
modèle aurait pu manquer : « la surcote majore la retraite et fait partie
intégrante de l'avantage de base », si bien que la majoration pour enfants
« est donc calculée sur la base du montant annuel de la retraite, majorée par
la surcote ». Son exemple le chiffre — 10 % × (600 + 22,50) = 62,25 — et
c'est un ordre d'opérations, pas un barème : appliquer les 10 % à la pension
d'AVANT la surcote rendrait 9,52 % de celle d'après, et le témoin le verrait.

**Une circulaire annulée ne certifie plus rien.** Les six témoins de carrière
longue citaient la circulaire Cnav 2026-17 du 12 juin 2026, que la 2026-29 du
4 septembre a annulée et remplacée. Ses âges et ses durées ont été relus ligne
à ligne dans la circulaire en vigueur : aucun n'a bougé — 60 ans et 6 mois et
170 trimestres pour 1964, 60 ans et 9 mois pour 1965, deux ans et six mois
avant l'âge légal de 1966 à 1969 — mais les témoins citent désormais celle qui
fait foi. C'est la même leçon qu'en juillet, d'un cran plus loin : une table
certifiée l'est à une date, et une SOURCE aussi.

**Ce que les exemples ne couvrent pas.** Ils restent courts par construction :
une affiliation, pas de polypension, pas de carrière hachée. Les vingt-quatre
et vingt-trois années des parents, les âges des catégories actives et leur
durée requise propre n'ont pas d'exemple publié que le dépôt ait trouvé : ils
sont transcrits du texte, et attendent le leur. Les trimestres réputés cotisés
de la carrière longue en ont un, maintenant lu — les trois exemples du point
1.2 de la circulaire 2026-29 —, mais il ne se rejoue pas : il arbitre entre
des périodes assimilées de nature différente, maladie, chômage, service
national, invalidité, maternité, que le modèle ne distingue pas dans une
carrière qu'il synthétise. Le rejouer demanderait d'abord de porter ces
natures, ce que l'entrée `carriere_longue_reputes_cotises_autres` du registre
de veille dit toujours.

**Ce que cette source vaut, et ce qu'elle ne vaut pas.** Un exemple de
circulaire est antérieur à la règle qui le suit — ceux de 2018 valent pour le
droit de 2018 — et une fiche de service-public est réécrite sans que son
exemple le soit toujours : chaque désaccord se tranche par le texte, jamais
par l'exemple seul. Mais quand les vingt-huit tombent justes ensemble, sur
dix sources et sept règles, c'est le droit que le modèle applique, et non une
lecture qu'il aurait de lui.

### La cotisation déplafonnée est portée au compte

C'était le dernier arbitrage de modélisation laissé ouvert. Il est tranché :
**chaque euro cotisé va à la retraite notionnelle**, y compris celui qui, dans
le droit positif, n'ouvre aucun droit.

Le régime général prélève deux cotisations retraite : l'une **plafonnée**, qui
s'arrête au plafond de la Sécurité sociale et ouvre des droits, l'autre
**déplafonnée** — 2,41 % depuis 2023 — qui porte sur la totalité du salaire et
n'en ouvre aucun : elle finance la solidarité. Le scénario 1 a raison de
l'ignorer, et continue de l'ignorer : il doit coller à la loi.

La fiche du régime général confondait les deux en un seul taux — 17,86 % pour
2023-2026 — appliqué à l'assiette **plafonnée**. En dessous du plafond, les deux
écritures donnent le même chiffre au centime près ; au-dessus, la déplafonnée
s'arrêtait au plafond alors que la loi la lève sur tout le salaire, et une part
de ce qui avait été réellement payé ne se retrouvait nulle part.

Les deux taux sont désormais saisis séparément — `taux_cotisation_retraite` et
`taux_cotisation_deplafonnee`, chacun avec sa part salariale, la déplafonnée
étant très majoritairement patronale (0 % de part salariale jusqu'en 2003,
16,6 % depuis 2023). Le contrôle de vraisemblance les confronte à OpenFisca
**un par un** plutôt que par leur somme : deux erreurs de sens contraire qui se
compensaient passeraient sur le total, pas sur le détail. Les huit périodes du
régime général y passent sans écart au-delà du seuil.

Un champ plutôt qu'une seconde période d'assiette déplafonnée : une période
supplémentaire serait entrée dans le calcul du scénario 1, qui parcourt toutes
les périodes actives d'un régime — et le scénario 1 doit rester la loi.

**Ce que ça déplace, mesuré sur les 86 témoins.** Le scénario 1 ne bouge sur
aucun, comme attendu. Les scénarios notionnels ne bougent pas non plus tant que
le salaire reste sous le plafond : l'écart médian des témoins déplacés est de
+0,01 %. Il ne se voit que sur les hauts salaires, et croît avec eux — sur le
témoin `salaire_8`, **+14 250 € de capital notionnel (+1,29 %)** en part
salariale, **+122 643 € (+4,48 %)** part employeur comprise, soit +1,29 % et
+4,48 % de pension. Aucune pension ne baisse.

### Trois valeurs de 2026 disponibles et non intégrées

Cet écart-là a été laissé ouvert un temps, au motif que « ces trois valeurs
relèvent des récupérateurs, qui demandent le réseau ». L'excuse ne tenait plus,
et les trois sont refermées :

* le **plafond de la Sécurité sociale 2026** était juste (48 060 €) mais marqué
  `estimee`, et cette fiabilité sous-évaluée se propageait à tout résultat qui
  touche au plafond. La source exigeait douze mois publiés quand l'INSEE n'en
  avait que neuf ; or le plafond est fixé par arrêté pour l'ANNÉE CIVILE, et la
  dernière année à en avoir connu plusieurs est 1961. Trois mois concordants
  suffisent désormais, à condition que la série couvre l'année depuis janvier —
  garde-fou qui n'est pas de principe : la série mensuelle commence en août
  2001, et retenir cette année-là sur ses cinq derniers mois donnait 27 348 €
  contre les 27 349 € du décret ;

* les **barèmes Agirc-Arrco de 2026** manquaient, si bien que les cotisations
  de 2026 retombaient sur le rendement instantané. Pire : faute de valeur de
  service, le modèle prolongeait celle de 2025 **par les prix** et servait
  1,46378 €, c'est-à-dire une revalorisation de +1,75 % que personne n'a
  décidée, là où la fédération publie un gel à 1,4386 € jusqu'au 1<sup>er</sup>
  novembre 2026. Un récupérateur lit maintenant la fédération elle-même —
  le PRODUCTEUR, là où le dépôt se contentait d'une transcription : les valeurs
  de 2019 à 2025 passent de `haute` à `certifiee`, celle d'achat de 2026 est
  ajoutée au même niveau, et la valeur de service en vigueur en 2026 est
  reconduite au niveau `haute`, puisque la décision de novembre peut encore la
  déplacer avant le 31 décembre. Mesuré : **−1,72 % sur la pension Agirc-Arrco
  et −0,59 % sur le total** d'une liquidation en 2026 ;

* la **CNRACL n'avait pas de ligne 2026**, son taux 2025 étant prolongé en
  `estimee`. Le décret n° 2025-86 du 30 janvier 2025 programme pourtant quatre
  marches de trois points — 34,65 % en 2025, puis 37,65 %, 40,65 % et 43,65 % —
  dont la transcription d'OpenFisca ne porte que la première. Les trois autres
  sont saisies depuis le texte, au niveau `moyenne`.

Sur les 86 témoins, ces corrections déplacent 174 pensions, **toutes à la
baisse**, de 0,01 % à 0,99 %.

Deux constats en sont sortis, qui valent au-delà de ces trois valeurs. La
règle « le producteur l'emporte sur la transcription » n'était appliquée qu'à
l'Ircantec : elle vaut maintenant aussi pour l'Agirc-Arrco, et l'INSEE — qui
n'est pas producteur de ces barèmes — leur cède la place. Et
`scripts/verifier_donnees.py --appliquer` lancé sur un `data/brut/`
incomplet **dégradait en silence** une valeur certifiée : faute du fichier de
la Caisse des dépôts, la transcription d'OpenFisca reprenait les lignes de
l'Ircantec et proposait de réécrire le taux d'appel de 1991, de 1,173 à 1,200.
Rien ne l'empêche encore : il faut lancer les récupérateurs des producteurs
avant d'appliquer.

### Ce qui n'est pas de la répartition est sorti de la comparaison

Le scénario 1 incluait le RAFP dans son total ; les scénarios 2 à 5 l'excluaient
et l'affichaient « servi à part ». L'écart annoncé comparait donc un total qui
le contient à quatre totaux qui ne le contiennent pas.

**Ce n'est plus le cas.** Un régime PROVISIONNÉ — le RAFP, les anciennes
assurances sociales de 1930 — sert une rente issue d'un placement, non de la
cotisation des actifs. Remplacer la répartition par des comptes notionnels ne
l'atteint pas. Les six scénarios le servent donc à l'identique, à son propre
barème, et il est retiré des cinq totaux.

Le CALCUL du scénario 1 n'est pas touché pour autant : l'écrêtement du minimum
contributif et l'ASPA continuent de regarder toutes les pensions, comme le fait
le droit. Seul le total RENDU est celui de la répartition, et la part écartée
est affichée juste à côté — sur la page comme dans le tableau — pour que
personne ne cherche où elle est passée.

Deux cas types sont concernés : le fonctionnaire sédentaire, dont 1 214 € de
RAFP sortent d'un total de 43 087 € (2,8 %), et le fonctionnaire de catégorie
active, 1 060 € sur 23 491 € (4,5 %). Aucun salarié du privé n'est touché.

**Une double comptabilisation disparaît au passage.** Les droits figés à la
bascule du scénario 3 étaient calculés sur la pension du scénario 1, RAFP
compris, puis convertis en capital notionnel — pendant que le compartiment de
capitalisation servait ces mêmes droits une seconde fois. Ils ne le sont plus.

Reste une grandeur qui n'est plus servie nulle part : ce que vaudrait le
compartiment s'il était converti au coefficient notionnel. Elle demeure calculée,
et le code dit désormais qu'elle est là **pour mémoire** — c'est la règle propre
du régime qui est affichée, pas celle-là.

### La marche à l'année de bascule est voulue, et voici ce qu'elle vaut

Ce document a longtemps rangé cette marche parmi les écarts à arbitrer. C'était
une erreur de lecture : **c'est la frontière de la réforme simulée**, et c'est
elle qui sépare le scénario 3 du scénario 2.

Un salarié qui liquide en 2026 voit son scénario 3 égal au scénario 1 ; celui
qui liquide en 2027, à carrière identique, le voit à **−15,0 % au salaire moyen
et à −16,9 % au SMIC**. Deux mécanismes s'additionnent, et il vaut la peine de
les distinguer parce qu'on les confond facilement.

**L'exemption, d'abord**, et c'est l'essentiel. Qui liquide à la bascule ou
avant garde le système actuel intégralement : `prospectif` bascule alors sur
`_deja_liquide`, qui ne convertit rien. Déplacer la bascule d'un an suffit à le
montrer — la génération 1962 passe de +0,0 % à **−13,7 %**, c'est-à-dire au
niveau de sa voisine. Les quatorze points ne sont donc pas une pénalité infligée
à 1963 : c'est une exemption accordée à 1962.

Cette exemption n'est pas un défaut à corriger. **C'est exactement ce qui
distingue le scénario 3 du scénario 2** : le prospectif respecte les droits
liquidés et accepte donc les « passagers clandestins » ; le rétroactif ne
respecte rien et n'en laisse aucun — un retraité de 2010 y passe de 20 211 € à
3 048 €. Supprimer l'exemption ferait fondre le troisième scénario dans le
second, et le dépôt perdrait un de ses six résultats.

**La conversion des droits figés, ensuite.** Ils sont valorisés au diviseur de
l'ÂGE DE RÉFÉRENCE, pas de l'âge réel de départ. Pour un départ à 64 ans en
2027 : pension figée 26 910,58 €, convertie au diviseur de 67 ans (22,03), soit
592 802 € de capital, puis servie au diviseur de 64 ans (24,68) — 24 490,90 €.

C'est délibéré, et le contraire de ce que ce document a écrit. La pension figée
est calculée SANS décote (`ignorer_penalite_age=True`) : cette conversion est
donc le SEUL endroit où l'âge de départ pèse sur les droits d'avant la bascule.
Basculer sur `--conversion-acquis liquidation` ne « rend pas la conversion
neutre » au sens innocent du terme — cela supprime toute pénalité de départ
anticipé sur la part figée, qui est l'essentiel de la pension des générations de
transition. Mesuré : travailler de 64 à 67 ans rapporte **+16,3 %** à la
génération 1963 sous `reference`, et seulement **+4,3 %** sous `liquidation`.
Le défaut `REFERENCE` est donc celui qui empêche qu'on gagne à partir tôt.

**Ce que ce n'est pas.** Le retrait des avantages non contributifs des droits
figés, longtemps donné ici comme la cause, ne pèse presque rien : mesuré sur les
droits figés à 2026, **0,0 % au salaire moyen** et 2,2 % au SMIC. Les cas types
qui montrent la marche n'ont d'ailleurs aucun enfant.

**Ce qui n'est pas modélisé**, et c'est un choix : aucune montée en charge. Une
réforme réelle lisserait la frontière sur plusieurs générations. Le modèle
tranche net, et la grille de cas types le montre tel quel.

---

## 4. Régimes incomplets, et de combien

Un régime « incomplet » n’est pas un régime absent : les 72 fiches du catalogue
calculent toutes une pension. Ce qui manque est, chaque fois, un ÉTAGE ou un
BARÈME qu'aucune source publique ne donne en série. Le tableau dit lequel, ce
qui le remplace, et **dans quel sens** l'approximation joue — car un modèle dont
on ignore le sens de l'erreur ne se corrige pas dans la tête du lecteur.

| Régime | Ce qui manque | Ce qui le remplace | Sens et ordre de grandeur |
|---|---|---|---|
| Professions libérales (CNAVPL) | la SECTION B du complémentaire des notaires, dont les bornes de classes ne sont publiées nulle part ; le volet CAPITALISÉ de la CAVP ; le complémentaire de la CAVOM d'avant 2016, qui prélevait par classes et dont la grille n'est nulle part ; le montant de la cotisation FORFAITAIRE du régime de base d'avant 2004 — qui ne commande plus la pension, seulement le flux versé au compte notionnel | le régime de base, en points plafonnés à 550, PLUS le complémentaire de la section : les DIX sections en ont un maintenant — CARMF, CARCDSF, CNBF, CAVEC, CAVP (volet réparti), CARPIMKO, CARPV, CAVOM (depuis 2016), CAVAMAC, CPRN (section C), et la Cipav pour le statut générique | **sous-estime** la pension d'un notaire de près de quatre dixièmes de son complémentaire, et celle d'un officier ministériel de tout son complémentaire d'avant 2016. Pour la CAVAMAC et la CPRN, l'assiette elle-même est reconstituée par un FACTEUR moyen — commissions, produits de l'office — et ne décrit aucun assuré en particulier |
| Marins (ENIM) | les salaires forfaitaires d'avant 2008, que les textes de l'index ne chiffrent pas ; la CATÉGORIE du marin, que le décret définit par le métier et qu'une carrière saisie ne porte pas ; les deux exceptions au plafond de vingt-cinq annuités, l'invalidité et le marin de cinquante-deux ans et demi réunissant trente-sept annuités et demie | la grille des vingt forfaits lue au Journal officiel depuis 2008, la catégorie la plus proche du revenu — convention nommée —, et la grille de 2008 ramenée par le salaire moyen avant ; le plafond de vingt-cinq annuités avant cinquante-cinq ans est porté | **estimé** avant 2008, la grille de 2008 étant ramenée par le salaire moyen ; **sous-estime** la pension du marin embarqué très jeune, à qui le plafond est opposé alors que le texte l'en dispense |
| Avocats (CNBF) | la progression de la cotisation forfaitaire sur les cinq premières années (363 € la première, 1 988 € à partir de la sixième) ; la contribution équivalente aux droits de plaidoirie ; les tranches de la grille complémentaire d'avant 2019 | la cotisation proportionnelle de 3,20 % ET le forfait à sa valeur de croisière, 1 988 € ; les années d'avant 2019 restent au rendement instantané | **surestime de 4 586 € sur une carrière** le flux des cinq premières années, contre 70 000 € qui manquaient quand le forfait n'était pas porté du tout. Sans effet sur la pension actuelle, qui est forfaitaire |
| Non-salariés agricoles | les points gratuits de la RCO — 66 par an aux conjoints et aides familiaux avant 2011, dans la limite de 17 ans ; le barème de points du régime de base AVANT 1990, l'article qui l'écrit ne l'ouvrant qu'à cette date ; la réforme du 28 février 2025, EN VIGUEUR depuis le 1er janvier 2026 et non calculable : deux de ses trois paramètres sont renvoyés à un décret que la base ne porte pas | le barème en points de 1990 à aujourd'hui, la retraite forfaitaire et la RCO, tous trois lus dans le code rural ; le rendement instantané pour les années d'avant 1990 ; la formule d'avant la réforme pour les liquidations de 2026 et au-delà, seule dont les paramètres existent | **sous-estime** la pension des carrières de conjoint et d'aide familial, qui sont précisément les plus modestes du régime |
| Régimes spéciaux résiduels | des paramètres certifiés — mais plus des textes : l'Opéra, la Comédie-Française, la SEITA, les clercs de notaires, la Banque de France, le fonds spécial des ouvriers de l'État et le personnel navigant ont leurs décrets lus VERSION PAR VERSION dans la base LEGI, et passent au niveau `moyenne`. Restent au niveau `estimee` les mines — dont dix-huit millésimes sont interpolés entre deux valeurs sourcées —, les marins, le port autonome de Strasbourg et les chemins de fer secondaires | pour les quatre derniers, les textes fondateurs sans recontrôle ; le port de Strasbourg n'a rien dans LEGI que des décrets de compensation, son règlement de retraite étant un acte de l'établissement | **indéterminé** pour ces quatre-là, et c'est le seul cas où le dépôt ne sait pas dire le sens. Ces régimes portent peu d'assurés ; leur poids dans les agrégats est faible |

**Ce qui a été refermé depuis la version précédente de ce tableau.** Le régime
de base des avocats était rangé ici comme « à scinder » : il l'est, et sa
pension ne dépend plus du revenu. La complémentaire agricole y figurait sans
valeur de point : elle en a une, certifiée de 2005 à 2024, tirée du code rural.
Le régime de base des professions libérales y figurait sans barème : il a le
sien, plafonné en points comme la caisse le publie. La grille des classes de
son étage d'avant 2004 y figurait aussi : **elle n'était pas la bonne
question** — la pension d'avant 2004 ne dépend d'aucune classe, et la section
« Cent points par trimestre » plus bas dit pourquoi.

**Pourquoi ce qui reste ne se referme pas de la même façon.** Les limites
refermées cette année l'ont toutes été par un changement de CLÉ D'ENTRÉE — un
numéro d'article plutôt qu'un mot, un IDBANK plutôt qu'une page, un lecteur de
format écrit à la main. Ce qui subsiste ci-dessus n'est pas d'une autre
difficulté technique : ce sont des barèmes que personne ne publie sous aucune
forme, ni en série, ni en texte réglementaire, ni en PDF. Les chercher encore
supposerait de les reconstituer à partir de cas individuels, ce qui produirait
un chiffre plus précis d'apparence et pas davantage de vérité.

Le catalogue compte **72 régimes**, actuels et disparus. Il est structurellement
extensible : ajouter un régime consiste à écrire une fiche YAML conforme à
`data/reference/regimes/_schema.yaml`, sans toucher au moteur.

### Les régimes qui manquent encore, et ce qui bloque chacun

**Cette liste est désormais dérivée d'un fichier.** Elle ne l'était pas, et
c'était une limite en soi : aucune source du dépôt n'énumérait les régimes
français — la série DREES agrège en treize systèmes, le panorama du COR est un
document saisi à la main, et les portails officiels ne servent pas de liste
exploitable —, si bien qu'un régime pouvait manquer à la liste des manquants.
[`data/reference/regimes/inventaire.yaml`](../data/reference/regimes/inventaire.yaml)
énumère maintenant TOUS les régimes obligatoires, vivants, disparus ou hors
champ — 89 lignes, ancrées sur `R. 711-1`, `D. 643-1`, `L. 921-1` et le
programme 195 des lois de finances, chacune avec son texte fondateur et, quand
l'index DILA du dépôt le porte, son identifiant —, et dit pour chacun s'il est
modélisé, partiel, à modéliser ou hors champ. `tests/test_donnees.py` impose
que l'inventaire et le catalogue coïncident sur les régimes calculés ; la page
« Données » du site l'affiche ; [`docs/regimes.md`](regimes.md) le commente,
famille par famille. Ce qui suit est l'histoire de la façon dont les fiches
sont entrées, et reste vrai ; la liste à jour de ce qui manque est là-bas.

**Ce que l'inventaire a fait apparaître**, que la liste de mémoire ne portait
pas : le régime d'allocation viagère des gérants de débits de tabac (décret
du 30 octobre 1963, géré par la Caisse des dépôts), le régime additionnel des
enseignants du privé sous contrat (décret n° 2005-1233), les deux
complémentaires d'Organic d'avant le NRIC — conjoints de commerçants
(`D. 635-35-1`) et entrepreneurs du bâtiment (loi n° 70-13) —, les régimes
RACD et RACL de l'IRCEC, les régimes professionnels intégrés à l'Agirc-Arrco
(banques, organismes de sécurité sociale, caisses d'épargne, CCI, CAMARCA),
l'affiliation des élus locaux à l'Ircantec dès 1973 (loi n° 72-1201) et non
1992, le régime micro-social, l'ASV des conventionnés, et cinq régimes
d'outre-mer. Et trois régimes fermés dont on ne savait plus s'ils avaient
existé, retrouvés dans l'index : le régime spécial du Crédit foncier de France
(transféré au régime général au 1er janvier 1989, décret n° 89-157), la caisse
des régies ferroviaires d'outre-mer (décret n° 58-1090, puis transfert à
l'État en 1993), et le régime de l'ORTF. Une relecture de septembre 2026
contre l'arrêté du 22 juillet 2003 relatif à l'échantillon interrégimes de
cotisants, qui énumère les organismes de tous les régimes obligatoires, a
ajouté quatre caisses fermées — la CREA des professions de l'enseignement
fondue dans la Cipav en 2004, la Caisse de retraites de la France d'outre-mer,
les caisses des fonctionnaires d'Algérie, du Maroc et de Tunisie, la CRFM des
agents publics de Mayotte —, les non-salariés de Mayotte à la caisse de
sécurité sociale de Mayotte et le personnel au sol d'Air France aux régimes
professionnels intégrés, puis une ligne pour les élus des assemblées de
Polynésie française et de Nouvelle-Calédonie, dont la loi organique de 1999
confie le régime de retraite aux assemblées elles-mêmes ; voir
[`docs/regimes.md`](regimes.md).

#### Ce que JORF et LEGI ne contiennent pas

Le dépôt embarque, par l'index de `scripts/fetch/dila_index.py`, deux bases de
la DILA filtrées sur le champ social. Pour l'histoire des règles de chaque
régime — l'étape qui suit l'inventaire —, il faut savoir ce qu'elles ne
donnent pas, afin de ne pas le chercher deux fois :

1. **Tout ce qui précède 1947.** Le dump JORF commence en 1947. Les lois de
   1910, de 1928 et 1930, de 1941, les ordonnances de 1945, la loi de 1909 sur
   les retraites des cheminots, celle de 1894 sur les mines et celle de 1937
   sur les clercs de notaires ne s'y trouvent que par les textes postérieurs
   qui les citent. Elles sont sur Gallica, en images.
2. **De 1947 à 1989, le texte intégral manque souvent.** Le JORF ancien n'est
   dans le dump que par sa notice ou son titre — constaté sur 1950 et sur
   1985-1986 —, et certains tableaux ne sont que des images (1994-1995). C'est
   la période où les règles des régimes se sont fixées : 1945, 1971, 1982,
   1983. Le « JO numérisé » en fac-similé de Légifrance n'est pas en open
   data.
3. **LEGI ne remonte pas avant la codification de 1985** pour les états
   datés des articles ; les versions antérieures des décrets des régimes
   spéciaux — statut des IEG de 1946, règlement SNCF de 1954 — n'y sont pas.
4. **Les accords de l'Agirc et de l'Arrco** — 1947, 1961, 2017 — et leurs
   annexes ne sont ni dans le JORF, qui n'a les avis d'extension que depuis
   les années 2000, ni dans KALI. La fédération est la seule source.
5. **Les règlements des caisses** — sections de la CNAVPL, CNBF, IRCEC, CRPN,
   port autonome de Strasbourg, Banque de France, CCI — : le JORF porte
   l'arrêté d'approbation, rarement son annexe.
6. **Les circulaires** de la Cnav et le BOSS ne sont pas dans JORF ni LEGI ;
   celles de la revalorisation des salaires sont récupérées à part.
7. **Les régimes des assemblées et des collectivités du Pacifique** relèvent
   de textes qui ne paraissent pas au Journal officiel.

Ce qu'il ne manque pas : le filtre thématique de l'index est assez large —
« retrait », « pension », « cotis », « invalidit »… — pour retenir les textes de
tous les régimes de l'inventaire ; les recherches qui ont établi la liste y
ont trouvé le décret du Crédit foncier, celui de Mayotte, l'arrêté des débits
de tabac, la loi des maires et adjoints, sans reconstruire l'index.

**Le régime des cultes, lui, est entré**, et c'est le seul du lot que le code
spécifie entièrement — sans lui donner un seul chiffre propre :

* l'**assiette** : R. 382-89 et R. 382-90 égalent la base forfaitaire, pour
  l'assuré comme pour sa congrégation, à « la valeur horaire du salaire
  minimum de croissance en vigueur, multipliée par le nombre légal d'heures de
  travail mensuel » ;
* les **taux** : les mêmes articles les égalent à ceux du régime général,
  respectivement part salarié et part employeur ;
* la **pension** : L. 382-27 la sert « dans les conditions définies aux
  articles L. 351-1 à L. 351-1-3 […] L. 351-8 à L. 351-13 », c'est-à-dire aux
  règles du régime général.

La fiche ne porte donc aucune valeur qui lui soit propre, et un test relit les
deux fiches année par année pour interdire qu'elle dérive de celle du régime
général. Il a fallu un drapeau au moteur, `assiette_forfaitaire` : un ministre
du culte n'a pas de salaire dont on prélèverait une fraction, l'assiette EST le
forfait, là où `assiette_plancher` ne relevait que les assiettes trop basses.

**Ce que la fiche des cultes approxime.** Deux choses, et dans le même sens.
Le passage du forfait de 169 à 151,67 heures mensuelles est daté de 2002, ce
que la clause transitoire de R. 382-89 rend probable sans l'écrire ; et la
garantie mensuelle de rémunération qui, du 1<sup>er</sup> janvier 2002 au
30 juin 2005, s'ajoutait à cette base n'est pas modélisée — ces quatre années
sous-estiment donc la cotisation. Enfin, L. 382-27 réserve les périodes
antérieures au 1<sup>er</sup> janvier 1998 aux règles d'avant, forfaitaires :
le modèle applique les règles du régime général sur toute la durée. Cela ne
touche que le scénario 1 ; les comptes notionnels, eux, ne lisent que des
cotisations, et celles-là sont sourcées de bout en bout.

**Les autres, et le mur devant chacun** : voir la couverture « à modéliser »
de l'inventaire, qui porte pour chacun ce qui bloque.

**Le personnel navigant est entré, et il a fallu deux choses pour cela.**

D'abord trouver ses paramètres : ils ne sont pas dans le code de la sécurité
sociale mais dans le **code de l'aviation civile**, et deux dépouillements les
ont manqués pour cette seule raison — le filtre exigeait une mention de la
sécurité sociale. Le troisième les donne tous : cotisations de 6 % et 12 %
jusqu'en 2011, de 7,668 % et 13,632 % ensuite (R. 426-6, R. 426-7), taux
d'appel (R. 426-8), barème de **1,85 % et 1,4 % de taux de pension par annuité
selon la tranche** (R. 426-16-1), bornes des tranches à quatre et huit plafonds
(R. 426-16-1-1), assiette de cotisation plafonnée au sommet de la seconde
tranche (R. 426-5 a), âge d'ouverture à cinquante ans (R. 426-11).

Ensuite apprendre au moteur à **liquider tranche par tranche**, ce qu'il ne
savait pas faire : le salaire de référence ignorait les bornes d'assiette, si
bien que deux tranches auraient calculé l'une et l'autre le salaire moyen
entier. En revanche le taux PAR ANNUITÉ, que ce document donnait aussi pour
inexprimable, l'était déjà : `taux_plein / durée_requise` est un taux par
trimestre, et 1,85 % par annuité s'écrit `taux_plein = 1,85 % × 30 annuités`.

**Pourquoi deux fiches pour une seule caisse.** Le calcul de pension ne retient
qu'UNE période active par régime : deux tranches simultanées dans la même fiche
verraient la seconde ignorée en silence. Plutôt que de refondre cette boucle,
le dépôt fait ce qu'il fait déjà pour la CNBF et sa complémentaire, et pour le
régime agricole et sa RCO — deux codes pour deux étages.

**Trois choses que le code ne donne pas**, et qui sont écrites dans les notes
des fiches : le taux d'appel de 1995 à 2011, dont la formule dépend de la
valeur N du fonds de retraite, et qui n'est donc pas appliqué — ce qui
sous-estime la cotisation ; l'**indice de variation des salaires**, fixé chaque
année par le conseil d'administration (R. 426-5 b), auquel la revalorisation de
salaires du dépôt tient lieu ; et les bornes des tranches d'avant 2012, que ce
même indice portait avant que le décret n° 2011-1500 ne les fixe en plafonds.
Depuis le 1<sup>er</sup> novembre 2023 ces articles sont abrogés et le régime
est passé au **code des transports** : les fiches s'arrêtent à l'état de 2023.

Un navigant est le seul assuré du catalogue à cotiser à **quatre régimes
simultanément** — régime général, Agirc-Arrco, et les deux tranches de sa
caisse. Carrière de 25 à 55 ans, génération 1965 :

| Revenu | Pension actuelle | Notionnelle | Part patronale comprise |
|---|---|---|---|
| 2 × salaire moyen | 53 755 € | 11 647 € | 31 667 € |
| 4 × | 104 566 € | 23 650 € | 65 508 € |
| 6 × | 159 865 € | 29 646 € | 83 581 € |

C'est le cas type qui montre le plus nettement ce que mesure ce dépôt : partir
à 55 ans coûte deux fois, et un régime spécial à départ précoce est ce qu'un
compte notionnel défait le plus violemment.

**Le mur du règlement de caisse a cédé, pour deux régimes sur onze.** Ni le
RAAP ni les sections libérales ne sont dans le code : L. 382-12 renvoie les
complémentaires des artistes-auteurs à L. 644-1, et leur barème au règlement de
la caisse. Mais ce que le code tait, la caisse le publie parfois — et deux le
publient bien.

**L'IRCEC publie un « mémo des valeurs » par an, en HTML**, qui donne le taux,
le seuil, le plafond, la valeur d'achat, la valeur de service ET le rendement.
Trois années relevées : 2023 (83,03 € d'achat, 9,05 € de service, rendement
10,9 %), 2024 (87,60 / 9,55 / 10,9 %), 2026 (90,30 / 9,75 / 10,8 %). Le mémo
2026 donne aussi le RACD (4,78 / 0,421 / 8,8 %) et le RACL (10,304 / 0,618 /
6 %), qui restent hors catalogue faute d'un statut qui les distingue.

**La CARMF publie ses chiffres clés sur deux pages** : 11,8 % des revenus nets
dans la limite de trois plafonds et demi — 19 849 € de cotisation maximale en
2026 —, 11,52 points par an au maximum, valeur de service 77,14 € à 62 ans. Ces
trois chiffres donnent un prix d'achat de 1 723 € et un rendement de 4,48 %.

Ce que la CARMF change à une simulation de médecin est exactement ce que ce
document annonçait sans pouvoir le combler — carrière de 25 à 64 ans, à trois
fois le salaire moyen :

| Statut | Pension actuelle | Notionnelle |
|---|---|---|
| `profession_liberale`, base seule | 16 176 € | 17 898 € |
| `medecin_liberal`, base + CARMF | **39 552 €** | **44 076 €** |

**Pourquoi ces valeurs ne sont pas dans `valeurs_point.csv`.** Ce fichier
appartient aux contrôles de `scripts/verifier_donnees.py` : le journal de
certification compte ses lignes par niveau de fiabilité, et toute ligne saisie
à la main le désaccorde — un test le vérifie, et c'est lui qui a refusé la
première écriture. Les deux fiches passent donc par le **rendement instantané**
de `regimes/rendements_points.csv`, qui est le filet de sécurité prévu pour
cela. Pour le RAAP ce n'est même pas une approximation : le rendement est
publié tel quel par la caisse.

**Ce qui manque encore à ces deux fiches**, et il faut le dire franchement :

* le **lien entre revenu et cotisation au RAAP d'avant la réforme** — et non,
  comme on l'a longtemps écrit ici, la table de ses classes. Le communiqué de
  l'IRCEC du 27 janvier 2016 tranche : le système était « OPTIONNEL —
  l'adhérent choisissait un montant » —, et « déconnecté des revenus
  artistiques perçus ». Le mécanisme de classes du dépôt, qui range l'assuré
  d'après son REVENU, ne peut donc rien ici : même publiée, la table ne dirait
  pas quelle classe un assuré avait choisie. La fiche applique les 8 % en
  amont, et la caisse donne l'ordre de grandeur de ce que cela coûte :
  « jusqu'à présent, 80 % des adhérents cotisent sur la base » la plus basse ;
* le **seuil d'affiliation** du RAAP — 900 SMIC horaires, 10 692 € en 2026 —
  en dessous duquel aucune cotisation n'est due : le modèle prélève quand même,
  n'ayant pas de mécanisme de seuil d'exonération (`assiette_plancher` relève
  une assiette trop basse, il ne l'annule pas) ;
* **toute série historique pour la CARMF** : la caisse ne publie que l'année en
  cours, et les chiffres de 2026 sont appliqués à toute la période.

**Les autres sections ont été relevées une par une, et le mur est toujours le
même.** Il ne tient pas au taux — presque toutes le publient — mais au **PRIX
D'ACHAT DU POINT**, sans lequel une cotisation ne devient pas une pension. Voici
ce que chaque caisse donne, pour que personne n'ait à refaire le trajet :

| Caisse | Taux du complémentaire | Valeur de service | Prix d'achat |
|---|---|---|---|
| **CARMF**, médecins | 11,8 % jusqu'à 3,5 plafonds | 77,14 € (2026) | déduit : 11,52 points pour 19 849 € → **1 723 €**. FICHE ÉCRITE |
| **IRCEC**, artistes-auteurs | 8 % jusqu'à 3 plafonds | 9,75 € (2026) | **90,30 €**, publié. FICHE ÉCRITE |
| **CAVAMAC**, agents d'assurance | 6,30 % créateur de droits, taux d'appel 121,6 % → 7,66 % effectif, dont 2,50 points versés par les compagnies mandantes | 0,4123 € (2026) | **8,1806 €**, publié — non par le Journal officiel, qui renvoie au conseil d'administration, mais par la délibération de ce conseil que la caisse met en ligne. Rendement 5,04 %. FICHE ÉCRITE |
| **CARPIMKO**, auxiliaires médicaux | forfait + 3 % de 1996 à 2025, 8,70 % entre un demi et trois plafonds depuis 2026 — série complète au Journal officiel | 18,08 € (2010) à 21,48 € (2026), publiée par la caisse | sans objet : le rendement se déduit des 8 points du forfait. FICHE ÉCRITE |
| **CAVP**, pharmaciens | régime MIXTE : part en répartition FORFAITAIRE de 7 657 € (taux d'appel 105,4 % en 2026), identique dans toutes les classes ; part en CAPITALISATION de 2 906 à 17 436 € selon la classe | annuité de 320,75 € (2024), 328,80 € (2026) | sans objet : le régime compte en annuités. FICHE ÉCRITE pour le volet réparti |
| **CAVOM**, officiers ministériels | 12,50 % jusqu'à huit plafonds depuis 2016, six CLASSES avant | 3,3745 € (2026) | **55,1390 €**, publié par le guide de la caisse, qui donne aussi le rendement : 6,12 %. FICHE ÉCRITE à partir de 2016 |
| **CIPAV**, interprofessionnelle | 9 % jusqu'à un plafond et 22 % d'un à trois depuis 2023 ; huit CLASSES avant | 2,89 € (2026) | **47,40 €**, publié — voir la troisième passe ci-dessous |
| **CAVEC**, experts-comptables | neuf classes, de 898 € à 30 616 € | 1,3850 € (2026) | rendement 8,33 %, vérifié sur les neuf classes. FICHE ÉCRITE |
| **CARPV**, vétérinaires | trois classes jusqu'en 2025 (16, 20 et 24 points), quatre depuis 2026 (17, 21, 25 et 28) | 37,79 € (2023) à 39,54 € (2026) | **602,00 €** en 2026, 570,26 € en 2024 : le décret annuel le fixe depuis 2016, et chaque classe divise exactement par ses points en ce montant. FICHE ÉCRITE |
| **CPRN**, notaires | section C : 4,10 % des produits de l'office ; section B : huit classes de 10 à 80 points | section B 17,7710 €, section C 0,9422 € (2026) | section B 279,12 € × 115 %, section C **17,69 €**, tous deux publiés par le guide de la caisse. FICHE ÉCRITE pour la section C |
| CARCDSF | abouti : fiche écrite | — | — |

Deux remarques que ce relevé impose. La première : **la CAVP n'est pas un régime
en répartition pure**, son étage complémentaire mêle une part répartie et une
part capitalisée par classes — le dépôt saurait le dire, avec son drapeau
`hors_repartition`, mais pas le chiffrer. La seconde : les notices PDF, qui
semblaient la piste la plus prometteuse, ne portent pas davantage le prix
d'achat — celle de la CAVP, dix-neuf mille caractères, dit seulement que « les
points acquis dans ce régime varient selon le montant des cotisations versées ».

Ce qui distingue la CARMF et l'IRCEC des autres n'est donc pas la transparence
en général, mais un fait précis : elles publient de quoi RECONSTITUER le prix du
point — la première en donnant le nombre maximal de points et la cotisation qui
les ouvre, la seconde en donnant directement l'achat, le service ET le
rendement.

### Une seconde passe, et trois choses qu'elle a corrigées

Le relevé ci-dessus a été refait avec un lecteur de pages qui rend le texte là
où une simple requête ne voyait rien. Il n'en sort **aucune fiche de plus**,
mais trois constats qui changent la carte.

**Le RENDEMENT est souvent publié là où le prix du point ne l'est pas.** La
CAVEC écrit que « 1 000 € de cotisations génèrent environ 83 € de pension
annuelle » — un rendement technique de **8,33 %**, c'est-à-dire exactement la
grandeur que `regimes/rendements_points.csv` consomme. L'IRCEC fait de même. La
prochaine tentative doit donc chercher le rendement d'abord, et le prix du
point seulement ensuite : c'est l'inverse de l'ordre suivi ici.

**Plusieurs sections ne sont pas proportionnelles mais PAR CLASSES**, et c'est
un obstacle d'une autre nature qu'une donnée manquante : il n'y a pas de taux à
écrire dans une fiche. La CAVEC a neuf classes depuis 2026, jusqu'à 1 841 points
par an, point à 1,3850 € ; la CAVP mêle des classes à une part capitalisée.
C'est la même forme que le RAAP d'avant 2017, et le dépôt ne sait pas encore
l'exprimer.

**Et un chiffre manquait parce qu'il n'existe pas encore.** La CARPIMKO est
passée au 1<sup>er</sup> janvier 2026 à un complémentaire entièrement
proportionnel — 8,70 % entre un demi et trois plafonds, valeur de service
21,48 € — mais le taux de conversion des cotisations en points n'est pas publié.
Interrogée, la Fédération nationale des orthophonistes répond : « nous
reviendrons vers vous dès que les textes définitifs seront publiés ». Ce n'est
donc pas une donnée introuvable, c'est une donnée **à attendre**, et elle
débloquera la plus grosse population libérale encore absente.

### Une troisième passe, par le *Journal officiel*, et la carte change

Les deux passes précédentes avaient interrogé les caisses. Celle-ci interroge
l'ÉTAT : les statuts de chaque régime complémentaire de section libérale sont
approuvés **par arrêté publié au Journal officiel**, et le JO publie l'annexe en
entier. Le dump global de la DILA — 1,67 Go, lu en flux — en rend 236 textes.
Le trajet est reproductible : `https://echanges.dila.gouv.fr/OPENDATA/JORF/`,
fichier `Freemium_jorf_global_*.tar.gz`, puis les incréments quotidiens pour
l'année en cours. (Légifrance lui-même refuse les requêtes : 403.)

**Ce que le JO donne, et ce qu'il ne donnera jamais.** Il donne la RÈGLE
d'acquisition des points, article par article. Il ne donne pas les VALEURS
annuelles, et l'arrêté CAVAMAC du 23 juin 2011 dit pourquoi en toutes lettres :

> « Article 10. Acquisition de points de retraite. Le versement de la cotisation
> donne lieu à l'inscription au compte de droits de l'adhérent d'un nombre de
> points de retraite P, donné par la formule : P = CA/CR […] CR désigne la
> valeur du coefficient de référence, c'est-à-dire le prix d'achat du point de
> retraite complémentaire, **fixée annuellement par le conseil
> d'administration**. »

Le prix d'achat de la CAVAMAC n'est donc pas introuvable par accident : aucun
texte réglementaire ne le porte, par construction. Le chercher au JO est un
trajet à ne pas refaire.

*(Et la conclusion qu'on en avait tirée — que ce prix était hors d'atteinte —
était fausse : le conseil d'administration délibère et LA CAISSE PUBLIE SA
DÉLIBÉRATION. Voir « Les deux dernières sections » plus bas. Ce qui est écrit
ci-dessus reste vrai du Journal officiel, et faux de tout le reste.)*

**La CARPIMKO n'est pas bloquée par ce qu'on croyait.** L'arrêté du 14 novembre
2025 (JORFTEXT000052604983) publie ses statuts modifiés, et son article 8 dit
combien de points ouvrait chaque cotisation :

> « 1) Pour les périodes comprises entre le 1er janvier 1996 et le 31 décembre
> 2025, les affiliés ont acquis, annuellement […] 8 points au titre de la
> cotisation forfaitaire ; 22 points maximum au titre de la cotisation
> proportionnelle. »

C'est un barème ÉCRIT EN POINTS, exactement la forme que le dépôt sait déjà
exprimer (`points_maximum`, celle du régime de base des libéraux et de la
complémentaire agricole) : le prix d'achat n'est pas nécessaire pour 1996-2025.
Il ne l'est que depuis 2026, où le même arrêté rend la cotisation entièrement
proportionnelle — « un nombre de points obtenu en divisant le montant de cette
cotisation par le coût d'acquisition d'un point de retraite » —, et ce coût
n'est toujours pas publié. Restent à trouver, pour écrire la fiche : le montant
de la cotisation forfaitaire année par année, les bornes de l'assiette, et la
série de la valeur de service (21,28 € en 2025, 21,48 € en 2026).

**La CIPAV, donnée pour « non aboutie », est entièrement documentée.** Ses
fiches pratiques portent tout, et l'obstacle est ailleurs — dans le moteur.

* Depuis 2023 le régime est **proportionnel** : « les cotisations de retraite
  complémentaire ne sont plus forfaitaires mais proportionnelles au revenu »,
  9 % de 0 à un plafond, 22 % d'un à trois plafonds.
* Les points s'achètent : « 3 600 € / 47,40 € (valeur d'achat du point en 2026)
  = 75,9 points », et se servent à 2,89 € en 2026. La caisse publie les trois
  grandeurs — achat, service, rendement : 42,43 € / 2,63 € en 2022, 45,30 € /
  2,77 € et 6,10 % en 2023, 47,40 € / 2,89 € en 2026.
* Avant 2023 la cotisation était **par classes**, et la fiche pratique 2022 en
  donne la grille complète : 1 527 € jusqu'à 26 580 € de revenus, 3 055 €
  jusqu'à 49 280 €, 4 582 €, 7 637 €, 10 692 €, 16 802 €, 18 329 €, et 19 857 €
  au-delà de 123 300 €. **La classe est déterminée par le revenu**, elle n'est
  pas choisie — contrairement à celle du régime invalidité-décès, que le même
  document présente juste à côté comme une option.

Une grille de ce genre est une FONCTION EN ESCALIER du revenu, et c'était le
seul obstacle qui restait : une fiche ne savait porter qu'un taux et un
forfait. **Elle sait désormais porter une grille** — `classes_cotisation.csv`,
le drapeau `cotisation_par_classes`, et la lecture dans les deux moteurs —, et
la Cipav est entrée au catalogue.

La grille est INDEXÉE SUR LE PLAFOND et non sur les prix, et c'est son
arithmétique qui l'impose : rapportées au plafond de 2022, ses sept bornes
valent 0,646, 1,198, 1,406, 1,614, 2,019, 2,508 et 2,997 — soit 0,65, 1,2,
1,4, 1,6, 2, 2,5 et 3 plafonds —, et ses huit montants sont 1, 2, 3, 5, 7, 11,
12 et 13 fois une même unité de 1 527 €, qui vaut elle-même 3,71 % du plafond.
Sept bornes sur sept à un demi-pour-cent d'un multiple rond : la grille est
écrite en plafonds, et l'indexer sur les prix la déformerait.

**La CAVEC a suivi**, et son guide annuel donnait plus que la grille : en
regard de chaque classe, LE NOMBRE DE POINTS QU'ELLE OUVRE. Avec la valeur de
service de 1,3850 €, le rendement se vérifie ligne à ligne — 498 points pour
8 282 € en classe D, soit 8,33 %, et les huit autres classes donnent le même à
un dix-millième près. Les statuts approuvés par l'arrêté du 4 juillet 2025
ajoutent un chiffre qu'aucune caisse ne publie d'ordinaire : une CIBLE de
rendement, « 8,25 % à échéance de l'année 2027 ».

Chez elle l'indexation de la grille sur le plafond est un CHOIX et non une
démonstration : ses neuf bornes valent 0,31, 0,66, 0,93, 1,36, 1,69, 2,08,
2,81 et 3,77 plafonds de 2026, et rien n'y est rond. Le plafond reste la
meilleure échelle pour une grille assise sur des revenus, mais soixante-dix ans
reportés depuis un seul millésime, c'est la limite de cette fiche, et elle est
grande.

**Le RAAP, lui, sort de cette liste, et pour une raison de fond.** Ses classes
d'avant 2016 étaient CHOISIES, pas subies : « un système optionnel — l'adhérent
choisissait un montant », « déconnecté des revenus artistiques perçus », écrit
la caisse. Le mécanisme range l'assuré d'après son revenu ; il ne sait pas
deviner un choix. Ce n'était donc pas une table qui manquait.

La passe a tout de même corrigé sa fiche sur un autre point : le décret du
30 décembre 2015 fait MONTER LE TAUX EN CHARGE sur quatre ans — 5 % sur les
revenus de 2016, 6 % sur ceux de 2017, 7 % sur ceux de 2018, 8 % à partir de
2019 —, et la fiche appliquait 8 % dès l'origine de la réforme.

**La CAVP n'avait même pas besoin du mécanisme**, et c'est son mémento qui le
dit : le tableau aligne les classes 3 à 13 en colonnes, et la ligne « Part gérée
par répartition » y porte le même montant partout. Le volet réparti est un pur
FORFAIT — 6 880 € en 2024, quel que soit le revenu ; seul le volet CAPITALISÉ
est par classes, et il n'est pas de la répartition.

Le même mémento donne la formule : « nombre d'années validées × 320,75 ». Le
régime compte en ANNUITÉS, et 320,75 / 6 880 = 4,66 % — le rendement du dépôt
reproduit la formule exactement, la cotisation étant constante. En 2026 elle
passe à 7 657 €, mais « intègre un taux d'appel de 105,4 % qui ne produira aucun
droit » : un compte notionnel porte ce qui est versé, et le rendement tombe à
4,29 %.

Ce qui reste au volet capitalisé de la CAVP n'est pas ce qu'on croyait. **Sa
grille de classes se lit** — déclarée illisible parce que le lecteur de PDF du
dépôt en sortait des glyphes, elle s'ouvre avec pypdf, et son arithmétique la
résume en une ligne : la part capitalisée vaut (classe − 1) fois une cotisation
de référence de 1 453 € en 2026, soit 2 906 € en classe 3 et 17 436 € en
classe 13, et la classe se lit sur un revenu de référence qui commence à
85 369 € et monte par paliers de 17 662 €. Ce qui manque est la **conversion** :
« à chaque âge de départ, le coefficient de conversion du capital en rente
viagère tient compte de l'espérance de vie pour chaque génération, d'un
rendement financier précompté et du choix ou non de la réversion » — et ni ces
coefficients ni le rendement du plan ne sont publiés. Ce n'est de toute façon
pas de la répartition : le dépôt le dirait avec `hors_repartition`, hors
comparaison.

### La source que deux passes avaient manquée : le décret annuel

Les deux relevés précédents interrogeaient les CAISSES, et concluaient à chaque
fois la même chose : elles ne publient que l'année en cours, et leurs statuts
renvoient les montants au conseil d'administration. Les deux constats sont
vrais. Ils ne concluent rien.

**Un décret par an fixe ces montants pour les neuf sections à la fois**, et le
Journal officiel le publie depuis 2001 :

> « 5° Section professionnelle des auxiliaires médicaux : cotisation
> forfaitaire : 1 648 euros ; taux de la cotisation proportionnelle : 3 % ;
> limites de l'assiette de la cotisation proportionnelle : seuil : 25 246
> euros ; plafond : 176 313 euros. »

Vingt-quatre décrets, 335 valeurs, lus par `scripts/fetch/jorf_cotisations_liberales.py`.
Ils donnent la série de la CARPIMKO — dont la fiche est écrite —, la valeur
d'achat du point de la CAVOM et de la CARPV depuis 2016 — dont les fiches sont
écrites, et dont la seconde reconstitue ses grilles de 2016 à 2024 en
multipliant ce prix par le nombre de points de chaque classe —, le montant de la
première classe de la CAVEC et de la Cipav année par année, et la section C des
notaires. Ils RECOUPENT au passage tout ce que les caisses publiaient : le
forfait et le taux de la CARCDSF, le taux de la CARMF, la grille 2022 de la
Cipav, tous identiques.

**Et ils corrigent une caisse contre elle-même.** Le décret n° 2025-1076 du
10 novembre 2025 fixe pour la Cipav « 11 % » en première tranche et « 21 % » en
seconde ; la fiche pratique 2026 de la caisse imprime encore 9 % et 22 % — les
taux de 2023 — et les applique dans son exemple chiffré. Le décret fait foi, et
la fiche du dépôt a été corrigée.

### Un rendement unique là où il faudrait une série

La fiche CARPIMKO met en lumière une approximation qui vaut pour TOUS les
régimes convertis par `rendements_points.csv` : le moteur applique **un seul
rendement, celui de l'année de liquidation**, aux cotisations revalorisées de
toute la carrière. Or le rendement de la CARPIMKO tombe de 13,10 % en 2010 à
7,36 % en 2025. Une infirmière qui liquide en 2027 voit donc ses cotisations de
2010 converties à 7,36 % au lieu de 13,10 % : sa complémentaire ressort à
3 683 € là où l'accumulation année par année en donnerait environ 5 600 €, soit
un tiers de moins.

Le chemin exact existe déjà dans le moteur — `valeurs_point.csv`, qui accumule
des points année par année —, et la CARPIMKO a de quoi l'emprunter : son prix
du point implicite est le forfait divisé par 8, et il donne les mêmes points que
la part proportionnelle divisée par 22. Ce qui manque n'est pas la donnée mais
le raccordement : `valeurs_point.csv` est un fichier CERTIFIÉ, dont le journal
verrouille le nombre de lignes par niveau, et y verser des valeurs demande un
contrôle dans `verifier_donnees.py` — donc un récupérateur pour la valeur de
service, que la caisse publie en PDF depuis 2010.

UN PIÈGE DÉCOUVERT EN CHEMIN, et refermé par un test. La table des tranches
d'assiette existe DEUX FOIS — `BORNES_ASSIETTE` dans `donnees/regimes.py` et
dans `moteur/js/regimes.js` —, parce que le portage ne lit pas le Python. La
tranche `tranche_1_3_pass` ajoutée pour la Cipav n'avait été écrite que d'un
côté : le JavaScript retombait sur `[0, null]`, c'est-à-dire SANS PLAFOND, et
cotisait 39 146 € là où le modèle en cotisait 19 356. Aucune erreur n'était
levée ; seule la comparaison des témoins l'a vu. Un test compare désormais les
deux tables.

### Le lecteur de PDF empilait les pages

Trois documents avaient été déclarés illisibles — le recueil de la CNAVPL, la
chronologie de la CARMF, le guide de l'IRCEC — et le dépôt en avait tiré une
règle : « reconstituer les lignes de ce document n'a pas de sens ». La règle
était fausse. `scripts/fetch/lecture_pdf.py` regroupait ses fragments sur la
**seule ordonnée**, en ignorant la page d'où ils venaient.

Or chaque page d'un PDF a son propre repère : l'ordonnée 700 désigne le même
endroit de la feuille, page 1 comme page 60. Le lecteur collait donc bout à
bout la ligne du haut de CHAQUE page — un titre de la page 1, un chiffre de la
page 40, une note de la page 97, dans une même chaîne. Sur un document d'une
page le défaut est invisible, et c'est pourquoi il a survécu : les barèmes de
la CNBF, pour lesquels le lecteur a été écrit, tiennent sur une page.

Le numéro de flux entre dans la clé de regroupement, et le même code rend :

| Document | Avant | Après |
|---|---|---|
| Chronologie de la CARMF | 8 lignes | **842** |
| Recueil de la CNAVPL | 4 lignes | **2 645** |
| Guide de l'IRCEC | 19 lignes | **956** |

La chronologie de la CARMF livre alors ce qu'elle contenait depuis le début :
la valeur du point du régime complémentaire **année par année depuis 1949** —
1,77 € en 1949, 74,47 € en 1988, 69,00 € en 2004, 77,14 € en 2026 —, les
allocations du régime de base depuis 1949, l'évolution de la lettre « C »
depuis 1967, et les décrets qui fixent les cotisations.

**Et un second défaut, sous le premier.** `Tm` ne pose pas une position mais un
REPÈRE : « 9 0 0 9 82.97 723.62 Tm » place le curseur ET multiplie par neuf
tout ce qui suit. Les décalages `Td` qui viennent ensuite sont exprimés dans ce
repère, pas en points de la page ; les additionner tels quels écrasait les
interlignes d'un facteur neuf. Des lignes distantes de 14,4 points sur la
feuille se retrouvaient à 1,6 l'une de l'autre — sous la tolérance de
regroupement, donc fondues. Les deux corrections ensemble portent la
chronologie de la CARMF de 8 lignes à **4 424**, et ses tableaux se lisent
ligne par ligne.

**Ce qui reste pour en tirer des séries.** Les colonnes se séparent très bien
par l'abscisse — encore faut-il, DANS une cellule, conserver l'ordre
d'ÉMISSION : tous les glyphes d'un nombre y partagent la même abscisse, et un
tri par x rend « 74,47 » sous la forme « ,4477 ». Cela fait, la table des
valeurs du point de la CARMF se lit : 1988 → 74,47 € pour le médecin et 44,74 €
pour le conjoint survivant, 1998 → 68,91 et 41,34, 2003 → 68,00 et 40,80.

### Ce que la chronologie de la CARMF a fini par dire

De 1991 à 1997 sa table porte **deux valeurs de point par année** — 1991 :
61,40 et 84,30 — sans que la géométrie dise laquelle est laquelle. Un écart de
trente-sept pour cent ne se devine pas. Trois recoupements l'ont levé :

* les **statuts du régime** affectent d'un coefficient de **1,33** les points
  acquis avant le 1<sup>er</sup> janvier 1991 ;
* le **rapport des deux séries** vaut 1,3333 à quatre millièmes près sur cinq
  des sept années — 81,87 / 61,40, 84,30 / 63,23, 86,90 / 65,17… ;
* les **raccords tiennent aux deux bouts** : la série haute prolonge la valeur
  unique de 1990 (78,97 → 81,87, soit +3,7 %), et la série basse rejoint la
  valeur unique de 1998 (68,68 → 68,91).

La série basse est donc le point NOUVEAU, celui que le modèle doit porter ; la
série haute est le point ancien, servi majoré d'un tiers jusqu'à extinction.

**Deux autres pièges, dans le même document.** La valeur publiée est celle
« à 65 ans » jusqu'en 2016 et « à 62 ans » depuis 2017 : la chute apparente de
78,55 à 68,30 est un changement de référence, pas une baisse. Et le régime
n'est « totalement proportionnel aux revenus » que depuis 1996, écrit la caisse
en note de bas de page ; avant, une part forfaitaire coexistait, dont les
points ne sont pas publiés.

**Ce que cela corrige, et c'est lourd.** La fiche portait un taux unique de
11,8 % et un rendement unique de 4,48 % — les chiffres de 2026 — sur toute la
période depuis 1949. Les deux sont désormais lus année par année :

| | Taux de cotisation | Rendement |
|---|---|---|
| 1983 | 2 % | 14,35 % |
| 1991 | 5 % | 13,11 % |
| 1996 | 7,5 % | 9,99 % |
| 2004 | 9 % | 7,47 % |
| 2016 | 9,6 % | 6,05 % |
| 2026 | 11,8 % | 4,48 % |

Les deux erreurs jouaient en sens inverse — un taux trop élevé, un rendement
trop faible — et se compensaient à moitié. Sur un médecin né en 1965 gagnant
trois fois le salaire moyen, la pension du scénario 1 passe de 39 552 € à
**33 708 €**, soit quinze pour cent de moins. Le dépôt annonçait cette fiche
comme portant « la limite la plus lourde » de ses deux fiches libérales ; elle
est levée.

**Ce qui reste.** Avant 1983, la table des cotisations proportionnelles ne
commence pas : le taux et le rendement de 1983 y sont prolongés. Et la part
FORFAITAIRE d'avant 1996 n'est pas modélisée, faute de connaître les points
qu'elle ouvrait — ce qui SOUS-ESTIME les droits acquis avant cette date.

### La troisième passe : une forme de plus, et un dentiste

Le mécanisme qui manquait n'était pas celui des classes mais celui de la
**cotisation forfaitaire qui s'ajoute à un taux**. Le complémentaire des
chirurgiens-dentistes et des sages-femmes appelle 3 210,60 € en 2026, qui
ouvrent six points, PLUS 11,35 % du revenu entre 0,65 et 5 plafonds. Ni un taux,
ni un forfait : les deux. Le moteur et son portage le savent maintenant, avec
`cotisation_forfaitaire_euros` — indexée sur les prix, comme la pension
forfaitaire, faute de série publiée.

**Où la phrase décisive se cachait.** Aucune page HTML de la caisse ne dit
combien de points le forfait attribue. Sa notice d'affiliation le dit, mais
elle est composée dans une police dont la table ToUnicode ne se lit pas : le
texte sort en glyphes. La substitution étant régulière et les chiffres passant
en clair, elle se décode — et donne « Cotisation forfaitaire : 3 178,80 en
2025, **attribuant 6 points** ». D'où 535,10 € le point en 2026, servi 31,82 €,
soit un **rendement de 5,95 %**. Une source tierce annonçait un tout autre
barème — 0,375 % et un point maximum — qui est un état ancien : c'est la notice
de la caisse qui tranche.

Ce que le complémentaire change pour un dentiste, carrière de 25 à 64 ans :

| Revenu | Base seule | Avec la CARCDSF | Notionnel |
|---|---|---|---|
| 1 × salaire moyen | 10 075 € | 17 930 € | 14 523 € |
| 2 × | 13 465 € | **30 809 €** | 27 614 € |
| 4 × | 18 888 € | **55 258 €** | 53 281 € |

**Ce que la fiche suppose, et qu'il faut dire** : que la part proportionnelle
achète ses points au même prix que la part forfaitaire. La caisse ne publie le
nombre de points que pour le forfait. C'est la seule hypothèse de cette fiche —
et c'est ce qu'un régime en points fait d'ordinaire. S'y ajoutent deux réserves
mineures : les chiffres de 2025 valent pour toute la période antérieure, et la
part proportionnelle n'est due qu'à partir de la troisième année d'activité,
ce que le modèle n'exprime pas.

**Restent donc trois formes et non plus une.** Proportionnelle pure — CARMF,
IRCEC, CARPIMKO depuis 2026, CAVOM depuis 2016 — que le dépôt sait exprimer.
Forfait plus taux — CARCDSF, CARPIMKO avant 2026 — qu'il sait exprimer depuis
cette passe. Et **par classes** — Cipav d'avant 2023, CAVEC, CARPV —, qui
restait alors dehors : il n'y a pas de taux à écrire, et la table des classes
est à relever caisse par caisse. C'est ce que les passes suivantes ont fait,
avec `classes_cotisation.csv`.

Ce que la seconde passe a rapporté de chiffré, pour que la troisième reparte de
là : CARPIMKO 8,70 % et 21,48 € de valeur de service ; CAVEC rendement 8,33 %,
point à 1,3850 €, 1 841 points maximum sur neuf classes ; CAVAMAC valeur de
service 0,4082 € au 1<sup>er</sup> janvier 2025.

**Le recueil statistique de la CNAVPL a été rouvert.** Il nomme les dix sections
et porte une table « Valeur de service du point ». Il en ressortait quatre
lignes pour cent soixante-seize mille caractères, ce dont ce document concluait
que sa mise en page « ne se reconstituait pas ». **C'était faux, et le défaut
était chez nous** : voir ci-dessous.

**Et ceux qu'on n'a pas cherchés** : régimes des élus locaux, de l'Assemblée
nationale et du Sénat, des chambres de commerce, et les régimes en extinction
d'outre-mer. Populations très petites, aucun barème en accès ouvert, et aucune
demande : ils sont nommés ici pour que leur absence soit un choix visible
plutôt qu'un oubli.

### Le catalogue et le routage ne se parlaient pas

Un régime n'existe pour le modèle que si un STATUT y conduit. Ce sont deux
fichiers séparés — `regimes/*.yaml` dit ce qu'est un régime,
`legislation/affiliations.yaml` dit qui y cotise — et rien ne les confrontait.
Trois désaccords y vivaient, dont un qui coûtait des années entières de
cotisation.

**Des années routées vers un régime qui ne tournait pas encore.**
`Compte.taux_effectif` parcourt `regime.periodes_actives(annee)` ; quand ce
parcours est vide, la boucle n'ajoute rien. L'année ne porte alors AUCUNE
cotisation au compte notionnel — sans exception, sans avertissement, sans trace
dans le journal de fiabilité. Trois routages faisaient exactement cela :

| Statut | Régime visé | Années perdues | Pourquoi |
|---|---|---|---|
| Artisan | `rci` | 1979-2005 | le RCI est né en 2013 ; la fiche n'a pas de période avant |
| Commerçant | `rci` | 2004-2005 | idem |
| Mineur passé au privé | `agirc_arrco` | 2011-2018 | le régime unifié est né en 2019 ; c'est l'Arrco qui couvre ces années |

Le mineur est corrigé par le routage seul — l'Arrco existe au catalogue et
couvre la période. Les deux autres appelaient les fiches manquantes, que le
RCI nommait déjà dans son propre `succede_a` sans que le catalogue les porte.

**Et il a fallu aller chercher leurs taux.** Aucune source ouverte ne les porte
en série : OpenFisca-France-Pension ne modélise les indépendants qu'à partir du
RCI de 2013, et les barèmes IPP, sa source amont, couvrent la CANCAVA et
l'ORGANIC — les régimes de BASE — mais pas leur étage complémentaire. Ils sont
pourtant écrits, décret par décret, dans le code de la sécurité sociale, et la
base LEGI en garde chaque version datée. `scripts/fetch/dila_legi_rci.py` la
lit en flux, comme celui de la MSA, et retient quatre articles : **D. 635-6**
puis **D. 635-7** pour les artisans, **D. 635-10** pour les commerçants, et
**D. 635-4** pour l'assiette d'avant 2004 — trois fois le plafond, sans quoi
les taux porteraient sur la mauvaise borne.

| | Artisans (D. 635-6, puis D. 635-7) | Commerçants (D. 635-10) |
|---|---|---|
| 1985-1996 | 4,50 % (4,40 + 0,10 additionnelle) | — |
| 1997 / 1998 / 1999 | 4,90 % / 5,30 % / 5,70 % | — |
| 2000-2002 | 6,00 % | — |
| 2003 / 2004 | 6,20 % / 6,70 % | 4,00 % en 2004 |
| 2005-2007 | 7,00 %, assiette portée à 4 plafonds | 6,50 % |
| 2008-2012 | 7,20 % sous le plafond, 7,60 % au-delà | 6,50 % |

Trois rédactions coexistent et il faut les trois : le taux unique, le taux
augmenté d'une **cotisation additionnelle** — l'état de 1985 pose 4,40 % puis
0,10 % en sus, et les deux lignes se cumulent —, et le découpage en **deux
tranches** de 2008, dont l'article fixe la borne à 33 276 € pour cette
année-là : c'est exactement le plafond de la Sécurité sociale de 2008, d'où une
borne exprimée en plafonds comme les autres. Une quatrième forme n'apparaît
qu'une fois : 2004 est écrite en demi-exercices pour les commerçants — 3,5 %
puis 4,5 % —, ramenés à 4 % sur l'année, la convention du dépôt étant un taux
annuel.

Trois assiettes ont dû être ajoutées au moteur, qui n'en connaissait aucune
au-delà d'un plafond pour ce type de régime : `plafonnee_3_pass`,
`plafonnee_4_pass` et `tranche_1_4_pass`.

**Le RCI lui-même y a gagné deux tranches et une hausse.** Sa fiche portait une
seule période, 7 % arrêtés au plafond de la Sécurité sociale, et annonçait en
note « 7 % sous plafond, 8 % au-delà » — mais la seconde tranche n'était portée
par aucune période et ne prélevait donc rien. Tout revenu d'indépendant
au-dessus du plafond échappait à la complémentaire. Le même dépouillement la
rétablit, et ajoute la hausse de 2025 : **8,1 %** et **9,1 %**.

| | Sous le plafond | Au-delà, jusqu'à 4 plafonds |
|---|---|---|
| 2013-2024 | 7,0 % | 8,0 % |
| 2025- | 8,1 % | 9,1 % |

**Et la date d'un état n'est pas celle de son effet.** L'état qui porte 8,1 % et
9,1 % entre en vigueur le 7 juillet 2024, mais précise que, conformément à
l'article 6 du décret n° 2024-688 du 5 juillet 2024, ces dispositions
s'appliquent aux cotisations « dues au titre des périodes courant à compter du
1<sup>er</sup> janvier 2025 ». Se fier à la date de version, comme le faisait
d'abord le récupérateur, prélevait ce taux un an trop tôt. C'est la seule
clause de ce genre parmi les états lus des quatre articles, et elle suffit à
interdire la date de version comme repère.

Ce que la seconde tranche déplace, artisan né en 1975, carrière de 25 à 64 ans :

| Revenu | Pension actuelle | Pension notionnelle |
|---|---|---|
| 1 × salaire moyen | 27 532 -> 28 011 € (+1,7 %) | 22 711 -> 22 735 € |
| 1,5 × | 32 712 -> 35 534 € (+8,6 %) | 29 803 -> 30 656 € (+2,9 %) |
| 2,5 × | 35 134 -> 44 583 € (**+26,9 %**) | 39 889 -> 43 205 € (+8,3 %) |

**Les six années 1979-1984, et pourquoi LEGI ne suffisait pas.** Le plus ancien
état de D. 635-6 est du 21 décembre 1985 — c'est la date à laquelle le décret
n° 85-1354 crée la partie réglementaire du code. Avant elle, le régime existait
mais n'était pas codifié : LEGI, qui n'est qu'une base d'ARTICLES, n'en sait
rien. Le **JORF** porte les décrets eux-mêmes, et deux passes y établissent la
chaîne complète :

| Texte | Ce qu'il fait |
|---|---|
| Décret n° **78-351** du 14 mars 1978 | institue le régime ; son article 12 date les cotisations du **1<sup>er</sup> janvier 1979** et les prestations du 1<sup>er</sup> avril |
| Décret n° **81-407** du 23 avril 1981 | répartit les biens de l'organisation autonome et fixe le versement du complémentaire au régime de base — **ne touche pas aux cotisations** |
| Décret n° **84-1064** du 30 novembre 1984 | « INSTITUTION D'UNE COTISATION ADDITIONNELLE FIXEE A 0,10% DU REVENU », applicable au 1<sup>er</sup> janvier 1985 |
| Décret n° **85-1354** du 17 décembre 1985 | codifie, et l'article porte dès lors 4,40 % + 0,10 % |

Onze textes seulement, dans tout le dump, concernent ce régime avant 1987, et
**aucun entre 1979 et 1983**. La date de création que portait la fiche, 1979,
est donc juste : le décret est de 1978, les cotisations de 1979.

**Et ce que le JORF ne donne pas.** Le texte intégral de l'article 5 du décret
de 1978. Les textes de cette époque n'y sont que par leur NOTICE, en capitales
et sans accents, qui énumère les intitulés d'articles — « ART. 5 : TAUX DES
COTISATIONS » — sans leur valeur. Les 4,40 % de 1979-1984 restent donc une
**déduction** : le taux figé à la codification, plus l'absence de tout texte
modificatif entre les deux. La chaîne est sans trou, ce qui n'est pas la même
chose qu'une lecture directe, et la fiche le dit à cet endroit précis.

**Ce qui reste ouvert.** Les taux, s'ils viennent du texte officiel, sont
saisis au niveau `haute` et non `certifiee` : rien ne les recontrôle
automatiquement, faute d'entrée dans `controle_vraisemblance_cotisations`.

**Cinq fiches qu'aucun statut n'atteignait.** L'AVTS, l'IGRANTE, la SEITA, le
port de Strasbourg et les chemins de fer secondaires étaient au catalogue,
comptés dans les trente-sept, et inatteignables : jamais calculés. Les trois
derniers ont reçu leur statut. Les deux premiers n'en recevront pas, et le
fichier de routage porte désormais la raison plutôt que le silence, sous
`regimes_sans_affiliation` :

* l'**AVTS** est une allocation sous condition de ressources, non contributive,
  et sa fiche porte les 8 % des assurances sociales qui la financent — la
  router à côté de `assurances_sociales` compterait deux fois la même
  cotisation. Elle reste au catalogue parce qu'elle date le premier mécanisme
  en répartition, ce dont `annee_debut_repartition` se sert ;
* l'**IGRANTE** est la jumelle de l'IPACTE : même population, mêmes paramètres,
  et une série de points qui est celle de l'Ircantec rétro-remplie pour les
  deux — 98 valeurs, dont une seule diffère. Le critère qui répartissait un
  agent entre les deux institutions n'est documenté par aucune source du
  dépôt ; inventer un statut pour le poser donnerait un choix sans conséquence
  chiffrée et sans fondement.

**Ce qui empêche la récidive.** Trois tests confrontent désormais les deux
fichiers : toute année routée doit trouver une période de régime, tout régime
du catalogue doit être routé ou nommé avec sa raison, toute succession
(`succede_a`, `integre_dans`) doit désigner un régime qui existe. Un quatrième
rattache aux données les nombres que le README et ce document annoncent —
« 62 statuts », « 72 régimes » —, parce que ce sont des chiffres de données et
non de prose, et que le dépôt s'est déjà fait prendre à en laisser dériver un.

### Les deux dernières sections que le décret annuel débloquait

Huit des dix sections libérales ont maintenant leur fiche. Les deux qui
manquaient encore — vétérinaires et officiers ministériels — sont tombées pour
des raisons opposées : la première publiait tout sans qu'on l'ait lue, la
seconde ne publie qu'une moitié de son histoire.

**La CARPV publie sa grille en clair, et l'arithmétique y ajoute le prix du
point.** Le tableau de la caisse donne les classes, leurs bornes de revenus,
leur cotisation ET les points qu'elles ouvrent. Chaque cotisation divise
exactement par ses points en la **valeur d'achat du point** que le décret annuel
fixe pour cette section depuis 2016 : 9 124,16 € pour 16 points en 2024, soit
570,26 € ; 10 234 € pour 17 points en 2026, soit 602,00 €. Le rendement est donc
le simple rapport de la valeur de service à la valeur d'achat, identique sur
toutes les classes.

**Et la grille a changé de forme en 2026 — ce qu'une première version de cette
fiche n'avait pas vu.** Les livrets annuels, longtemps réputés illisibles, se
lisent avec pypdf : jusqu'en 2025 la section ne comptait que **trois** classes,
à 16, 20 et 24 points. Le rapport annuel 2024 annonce la réforme — « un point
supplémentaire pour les classes B, C et D qui passent respectivement de 16 à 17
points, de 20 à 21 points et de 24 à 25 points, ainsi que la création d'une
classe E à 28 points ». La fiche avait reporté la grille de 2026 vers l'amont :
elle prêtait à 2016 une quatrième classe qui n'existait pas.

Les livrets donnent désormais la grille entière — bornes, montants et points —
pour 2024, 2025 et 2026, saisis tels quels. Pour 2016 à 2023, les montants sont
le produit des points par le prix du point de l'année (446 € en 2016, 539 € en
2023) et les bornes celles de 2024 indexées sur le plafond. Les trois millésimes
publiés disent ce que vaut cette convention : les bornes ont monté de 1,68 %
entre 2024 et 2025 quand le plafond montait de 1,58 %.

**Le rendement, lui, baisse régulièrement**, et la caisse en publie les deux
termes : 37,79 / 539 en 2023, 39,42 / 570,26 en 2024, 39,50 / 591,36 en 2025,
39,54 / 602 en 2026 — soit 7,01 %, 6,91 %, 6,68 % et 6,57 %. Le rapport annuel
confirme le troisième au centième. Avant 2023 la valeur de service n'est pas
publiée : c'est le plus ancien rapport connu qui est reconduit, et comme la
pente descend, il s'agit d'un plancher.

Ce qui manque encore : les bornes d'avant 2024 et toute grille d'avant 2016 — le
décret ne fixait alors pas un prix du point mais un **taux d'appel**, monté de
78,5 % en 2002 à 104 % en 2015, appliqué à des montants que rien ne publie. Une
cotisation de 2002 est donc surestimée d'un quart environ.

**La CAVOM donne trois grandeurs qui se referment l'une sur l'autre.** Son guide
2026 publie la valeur d'achat du point (55,1390 €), la valeur de service
(3,3745 €) et le rendement — « le taux de rendement du régime complémentaire est
de 6,12 % » —, et 3,3745 / 55,1390 = 6,1200 %. Il imprime aussi les points
qu'ouvre le plafond, 871,62, et ceux de la cotisation minimale, 20,70 : huit
plafonds et 19 % d'un plafond, tous deux à 12,5 %, divisés par le prix du point.
Le taux, l'assiette et le prix disent la même chose trois fois.

**Mais la fiche ne commence qu'en 2016**, et c'est la plus grosse lacune du
catalogue libéral. Avant la réforme, le régime prélevait par CLASSES — six,
déterminées par le revenu de l'année N-2, plus une classe spéciale — et cette
grille n'est publiée nulle part. Le décret annuel ne chiffre que la classe
spéciale (284 € en 2002, 694 € en 2015) ; la seule autre valeur retrouvée est
la sixième classe, 13 886 € en 2015 dès deux plafonds de revenus. Deux
extrémités ne font pas une grille de six classes. Un officier ministériel simulé
ici est donc sous-estimé de tout son complémentaire d'avant 2016, et la fiche le
dit.

**Restent deux sections sur dix**, et la passe suivante les a prises toutes les
deux — voir plus bas. La CAVAMAC, dont aucun texte RÉGLEMENTAIRE ne publie le
prix du point (ses arrêtés renvoient au conseil d'administration, mais la caisse
publie la délibération de ce conseil), et la CPRN, bloquée non par un barème
manquant mais par son ASSIETTE : la cotisation d'un notaire est assise sur les
produits de son office, une grandeur que le modèle ne connaît pas et que la
carrière saisie ne porte pas. S'y ajoute, chez une section déjà écrite, le volet
CAPITALISÉ de la CAVP, qui n'est pas de la répartition.

**Un trou de couverture refermé au passage.** Le balayage « un statut, une
génération » des témoins — le SEUL dispositif qui confronte le portage
JavaScript au modèle Python — se voulait le catalogue entier et en oubliait
treize, dont les huit sections libérales écrites cette année. La divergence de
`tranche_1_3_pass` n'avait été prise que parce qu'un statut du balayage
l'empruntait ; la même faute sur une borne que seul un officier ministériel
traverse serait passée sans bruit. Les treize sont entrés, et un test oblige
désormais la liste à rester complète.

### Les deux dernières sections, et le mur qui n'était pas celui qu'on croyait

Les dix sections libérales ont maintenant leur fiche. Les deux dernières —
agents généraux d'assurance et notaires — étaient rangées ici comme bloquées,
l'une faute de prix du point, l'autre faute d'assiette. Le premier diagnostic
était faux ; le second était juste, et il a fallu lui trouver un contournement.

**La CAVAMAC ne publiait pas son prix du point — au Journal officiel.** Ce
document concluait, arrêté du 23 juin 2011 à l'appui, que ce prix n'était « pas
introuvable par accident : aucun texte réglementaire ne le porte, par
construction », et que le chercher au JO était « un trajet à ne pas refaire ».
Les deux phrases restent vraies. Elles regardaient simplement au mauvais
endroit : **le conseil d'administration délibère, et la caisse publie sa
délibération dans ses actualités**, avec le chiffre :

> « Le coefficient de référence, correspondant au prix d'achat d'un point de
> retraite : fixé à 8,1806 €, maintenant ainsi le taux de rendement du régime à
> 5,04 %. »

Trois exercices sont ainsi documentés — 7,597 € en 2023, 7,9246 € en 2024,
8,1806 € en 2026 — et le rendement s'y vérifie à chaque fois : 0,3829 / 7,597,
0,3994 / 7,9246, 0,4123 / 8,1806 font 5,04 % les trois fois. La caisse pilote ce
rendement et le dit.

**Et le taux d'appel de cette section est le plus lourd du catalogue.** Le taux
statutaire n'a pas bougé depuis 1971 — 6,30 % — mais ce qui est appelé, oui :
100 % jusqu'en 1992, 110 % en 1993, 127,5 % en 1998, 129,5 % en 2001, **142,86 %
de 2004 à 2018**, 129,5 % ensuite, 121,6 % en 2026. Le décret de 1992 dit ce que
cela signifie : « la majoration de cotisation afférente à la fraction du taux
d'appel excédant 100 % n'ouvre pas de droit supplémentaire ». Quinze ans durant,
un agent général a versé sept euros pour cinq euros de droits, et le rendement
de ce qu'il versait est tombé à 3,53 % — le plus bas du catalogue libéral.

**L'assiette, elle, n'est pas le revenu, et c'était le vrai mur.** Les
cotisations de ce régime « sont calculées sur la base de vos COMMISSIONS ET
RÉMUNÉRATIONS BRUTES », écrit la caisse, celles que les compagnies versent avant
que l'agent n'ait payé un loyer ou un salarié. Une carrière saisie dans ce
simulateur ne porte pas cette grandeur. La caisse la donne pourtant, sur la même
page de statistiques que le revenu :

> « La commission moyenne plafonnée augmente de 5,0 %, passant de 275 525 € à
> 286 168 €. […] Le revenu moyen déclaré en 2024 par les agents s'élève à
> 115 443 euros. »

Le rapport vaut **2,387**, et c'est ce que porte le nouveau champ
`assiette_facteur_revenu` : l'assiette du régime est le revenu multiplié par ce
facteur, avant application des bornes. C'est une moyenne de section — deux
agents à même revenu n'ont pas les mêmes commissions — mais l'ignorer se
tromperait d'un facteur deux et demi, ce qui est pire.

**Une dernière singularité : un tiers de la cotisation est payé par
quelqu'un d'autre.** Le « concours conventionnel des compagnies mandantes »
apporte 2,50 points sur les 7,66 appelés en 2026, et la fiche des taux de la
caisse l'énumère comme une ligne à part entière. Le gouvernement en a donné
l'ancienneté et le poids au Sénat en 2021 : « depuis 1952, des accords
conventionnels successifs » font financer le régime en partie par les
compagnies, pour « environ 90 millions d'euros, soit plus du tiers des
ressources du régime » — la proportion d'aujourd'hui.

**L'agent général est donc le seul libéral du catalogue qui ne cotise pas
seul**, et son statut n'est pas marqué `sans_employeur`. Les compagnies ne sont
pas son employeur ; elles paient pourtant, et le modèle n'a pas d'autre façon de
le dire. Les scénarios 2 et 3 ne portent à son compte que les 5,16 points qu'il
supporte, les scénarios 4 et 5 les 7,66 entiers — sur une carrière au revenu
moyen de la section, 15 147 € contre 22 486 € par an. Son régime de BASE reste
intégralement à sa charge, la fiche de la CNAVPL ne portant aucun partage.

**La CPRN, elle, était bien bloquée par son assiette** — les produits de
l'office, pas le revenu du notaire — et c'est un rapport d'inspection, non la
caisse, qui a fourni la clé. L'IGAS (rapport n° 2012-110P) décrit la règle qui
fixe le prix du point de la section C :

> « Cette valeur d'acquisition est calculée de façon à ajuster le nombre de
> points attribué à chaque notaire de façon à ce que la moyenne sur l'ensemble
> des notaires soit toujours égale à 900 points. »

Avec le prix que publie le décret annuel — 17,69 € — et le taux — 4,10 % —, les
produits moyens d'un office valent 900 × 17,69 / 0,041 = **388 317 €**.

**Le rendement d'avant 2013 est publié, année par année.** Le même rapport de
l'IGAS donne les deux séries de la section C de 2004 à 2012 — coût d'acquisition
du point de 12,95 € à 16,64 €, valeur de service de 0,5816 € à 0,6848 € —, et
leur rapport recoupe le texte du rapport au millième près. Il montre surtout que
**le rendement n'a pas baissé régulièrement : il a fait un creux**, de 4,49 % en
2004 à 3,47 % en 2009, avant de remonter à 4,12 % en 2012. C'est le mécanisme
même du régime, celui des 900 points : le prix du point monte quand les produits
des études montent. L'actuaire de la caisse appelle cela « procyclique » — le
rendement s'élève au moment où les ressources se réduisent. La fiche porte donc
neuf lignes au lieu d'une, et reconduit la plus ancienne vers l'amont faute de
mieux.

**Le revenu moyen, lui, se mesure** — et c'est le recueil statistique de la
CNAVPL qui le permet, une fois relu avec un lecteur de PDF capable de ses
polices. Il publie, section par section, les cotisations du régime de base
encaissées sur CHACUNE DES DEUX TRANCHES : pour les notaires en 2024, 43 405 k€
sur la tranche 1 et 27 195 k€ sur la tranche 2, pour 12 096 cotisants. Divisées
par leurs taux — 8,23 % et 1,87 % —, ces deux sommes donnent deux **moments
écrêtés** de la distribution des revenus : 43 601 € en moyenne sous un plafond,
120 228 € sous cinq. Deux moments suffisent à caler une log-normale, dont la
moyenne entière vaut **152 097 €**.

**La méthode se vérifie sur une autre section.** Appliquée à la CAVAMAC, dont la
caisse publie de son côté le revenu moyen déclaré, elle donne 116 579 € contre
115 443 € publiés — **1 % d'écart**. C'est ce contrôle qui autorise à s'en
servir là où personne ne publie le revenu moyen.

D'où un facteur de **2,553** : le notaire garde 39 % des produits de son office,
le reste payant les collaborateurs et l'étude — le notariat compte 55 556
collaborateurs pour 17 305 notaires. Et ces « produits » ne sont pas le chiffre
d'affaires brut : la caisse précise qu'ils « correspondent à la part du notaire
dans les émoluments de l'office, APRÈS DÉDUCTION DE CERTAINES CHARGES
professionnelles ». C'est ce qui réconcilie les 388 317 € avec les 520 000 € par
notaire que publie le Conseil supérieur du notariat, lesquels incluent les taxes
et déboursés encaissés pour le compte d'autrui. Un second calcul recoupe la chaîne : la
cotisation moyenne que publie la caisse (32 864 €, tous régimes) moins la part
du régime de base que donne le recueil (5 837 €) laisse 27 027 € pour les deux
sections, dont 15 921 € de section C laissent 11 106 € de section B — soit la
classe 3,5, au milieu d'une grille qui en compte huit. La fiche porte
`fiabilite: estimee` parce qu'une chaîne reste une chaîne.

**La moitié forfaitaire du régime reste dehors, et la raison n'est pas celle
qu'on croirait.** Ce n'est pas une grille introuvable : **de 1962 à 2013, il n'y en a pas eu**. L'IGAS décrit le régime tel qu'il fonctionnait encore
en 2012 — sept classes numérotées 0, 1, 2, 3, 4, 6 et 8 :

> « L'inscription dans une des classes de cette section est obligatoire pour les
> notaires en exercice ; LE CHOIX DE LA CLASSE ELLE-MÊME ÉTANT LAISSÉ À
> L'APPRÉCIATION DU NOTAIRE. […] En l'absence d'indication, le cotisant est
> affilié en classe 1. »

Créée en 1962 pour « répondre aux vœux du notariat qui souhaitait une cotisation
INDÉPENDANTE DES PRODUITS réalisés par l'office », la section B était un
supplément facultatif, et le dépôt ne prête jamais à personne un choix qu'il ne
peut pas connaître — même règle que pour les classes du RAAP d'avant 2017. Le
même rapport montre ce que ce choix donnait : en 2011, sur 8 356 cotisants,
1 587 étaient en classe 0 et 2 593 en classe 1, pour une moyenne de 23,8 points
par an — la classe 2,4.

**Depuis 2014 la classe se détermine par les produits — et le décret qui
l'institue délègue ses bornes dans la même phrase.** Le décret n° 2013-1157 du
13 décembre 2013 :

> « Les bornes de chaque classe de cotisation de la section B sont déterminées
> PAR LE CONSEIL D'ADMINISTRATION de la Caisse de retraite des notaires pour une
> période de trois ans par référence à la moyenne des produits de base du
> notariat au titre des trois années précédentes. »

Ces bornes ne sont donc pas introuvables par accident : **aucun texte
réglementaire ne les porte, par construction** — exactement comme le prix du
point de la CAVAMAC, à ceci près que la CAVAMAC publie la délibération de son
conseil et que la CPRN ne publie pas la sienne. Une passe entière du *Journal
officiel* sur les textes qui parlent à la fois des notaires, de classes de
cotisation et de produits n'en a rien tiré. Et la bascule n'est pas achevée :
« à partir du 1er janvier 2029, le notaire sera systématiquement inscrit pour
l'exercice n dans la classe de cotisation correspondant aux produits de son
étude » ; jusque-là, un notaire assermenté avant 2014 ne monte que d'une classe
par an et ne descend jamais d'office, et les nouveaux gardent six ans la
classe 1.

Ce qui manque se chiffre : environ 11 100 € pour le notaire moyen en 2025,
contre 15 900 € de section C. Et le jour où la caisse publiera ses bornes, la
fiche se complètera en une demi-heure : la cotisation vaut « le nombre de points
de la classe multiplié par 115 % du coût d'acquisition du point B » pour tout
notaire assermenté depuis 2014, les classes ouvrent 10 à 80 points, et le
rendement de la section se calcule comme celui de la C — 9,50 % en 2004, 7,79 %
en 2012, 5,54 % en 2026.

**Un mécanisme de plus dans le moteur, et le troisième cette année.** Après la
cotisation par classes et la cotisation forfaitaire qui s'ajoute à un taux,
voici l'assiette qui n'est pas le revenu. Le champ est porté des deux côtés du
portage, et le fichier de schéma le documente. Il ne sert qu'à ces deux
sections, et il faut espérer qu'il n'en serve jamais davantage : un facteur
moyen est une approximation grossière, et la seule chose qui la rende acceptable
est qu'elle remplace une absence.

### Ce que le lecteur de PDF du dépôt ne lit pas, et ce que cela avait coûté

`scripts/fetch/lecture_pdf.py` est écrit à la main, sans dépendance : le dépôt
n'en a qu'une, PyYAML, et cette règle vaut mieux qu'un lecteur parfait. Mais
elle a un prix, et il s'est chiffré. Ce lecteur ne sait pas décoder les polices
qui n'embarquent pas de table `/ToUnicode` — il en sort des glyphes —, et
**quatre conclusions de ce document reposaient sur ce silence** :

| Document | Ce qu'on en concluait | Ce qu'il contenait |
|---|---|---|
| Recueil statistique de la CNAVPL | « la valeur du point, et rien d'autre » | les cotisations du régime de base **par section et par tranche**, d'où le revenu moyen de chaque section |
| Livrets annuels de la CARPV | « les bornes y seraient, mais illisibles » | la grille entière de 2024 et 2025 — et **trois classes**, non quatre |
| Mémento de la CAVP | « la grille du volet capitalisé est illisible » | (classe − 1) × 1 453 €, par paliers de revenu de 17 662 € |
| Rapport de l'IGAS sur la CRN | « chiffré, donc fermé » | la règle des 900 points, le rendement 2004-2012, la nature facultative de la section B |

Les trois premiers se lisent avec **pypdf**, le quatrième aussi une fois
déchiffré (AES-128, mot de passe vide). Aucun n'entre pour autant dans les
récupérateurs du dépôt : ce serait une dépendance de plus, et les valeurs qui en
viennent sont saisies à la main, avec leur source, comme tout ce qui n'est pas
automatisé.

**La leçon n'est pas « il faut un meilleur lecteur ».** C'est que l'expression
« ce document est illisible » doit toujours se lire « ce document est illisible
PAR NOTRE OUTIL » — et qu'une limite ainsi formulée cache une question qu'on
n'a pas posée. Trois des quatre lignes ci-dessus avaient été écrites comme des
limites de la SOURCE ; elles étaient des limites du LECTEUR.

### Cent points par trimestre, et la pension que le moteur inventait

Le régime de base des professions libérales couvre soixante-quinze ans, et le
modèle n'en paramétrait vraiment que les vingt derniers. Pour tout ce qui
précède 2004, sa fiche portait `assiette: forfaitaire` — un mot que le moteur ne
connaît pas, et qu'il lisait donc comme « le revenu entier, sans plafond ». Il
prélevait là-dessus 8,5 %, capitalisait au rendement de 8 %, et servait une
pension de base **proportionnelle au revenu** : trente ans à 200 000 € y
ouvraient 40 000 € par an. Le régime, la même année, servait une pension moyenne
de **3 809 €** (recueil statistique de la CNAVPL, exercice 2003 ; 4 948 € en
2024).

L'écart n'est pas une imprécision de barème, c'est une erreur de NATURE. Le
régime d'avant 2004 ne servait pas une pension proportionnelle, mais une
ALLOCATION VIEILLESSE, la même pour le notaire et pour le kinésithérapeute : la
moitié de l'AVTS à l'origine, son montant entier depuis le décret n° 62-439 du
14 avril 1962, puis, au 1er janvier 1983, « 1/15e d'AVTS par année cotisée »,
la condition de quinze années d'activité étant supprimée — les années au-delà de
quinze comptant depuis le 1er juillet 1978. La réforme du 21 août 2003 a
converti ce droit en points, et la règle de conversion tient en une ligne :

> Les trimestres validés avant le 1er janvier 2004 sont convertis en points à
> raison de 100 points par trimestre.

C'est la fiche du recueil pour l'article `D. 643-1`. Quatre cents points par
année pleine, au point de 2025, font 261,60 € : quarante ans de carrière
antérieure à la réforme ne peuvent pas dépasser 10 500 €, et le revenu n'entre
dans ce compte que par les trimestres qu'il valide — 150 heures de SMIC chacun,
200 avant 2014, quatre par an au plus.

**L'erreur ne jouait pas toujours dans le même sens**, et c'est ce qui la
rendait indétectable à l'œil. Le point de bascule est à 38 000 € environ de
revenu annuel, en euros de la liquidation — c'est le revenu où 8,5 % capitalisés
à 8 % valent les 400 points de l'année : au-dessus, l'ancien calcul servait plus
que le régime ; en dessous, moins. Les dix carrières témoins de statut libéral,
qui commencent modestement, gagnent toutes 1 828 € par an à la correction ;
trente années d'avant 2004 à 200 000 € en perdent plus de trente mille.

Le moteur a donc un mécanisme de plus, `points_par_trimestre_valide`, porté des
deux côtés du portage et documenté au schéma. Il ne sert qu'à ce régime, et il
est la forme la plus simple qu'un droit à retraite puisse prendre : un nombre de
points par trimestre, sans assiette.

**Ce qui reste conventionnel n'est plus la pension, mais la cotisation.** La
cotisation de base était forfaitaire jusqu'en 1992 ; le 1er janvier 1993 (loi
n° 91-73 du 18 janvier 1991), « une fraction de la cotisation du régime de base
est devenue proportionnelle aux revenus, dans la limite de 5 fois le plafond de
la sécurité sociale ». La série des forfaits n'est nulle part — ni au recueil,
qui ne donne de cotisations qu'en agrégats d'un exercice, ni dans les tableaux
de compensation démographique, qui portent une tout autre « cotisation de
référence ». Le compte notionnel prélève donc 8,5 % du revenu **borné à cinq
plafonds**, le plafond que le régime s'est lui-même donné en 1993. C'est une
convention, elle est nommée dans la fiche, et elle ne touche plus que les
scénarios notionnels.

**La phrase citée n'est pas dans la loi consolidée, et l'article qu'elle cite
dit autre chose.** Le dépouillement complet du dump LEGI — 5 253 903 fichiers —
ne trouve « cent points par trimestre » ni « 100 points par trimestre » nulle
part, sous aucune graphie. Les sept versions de `D. 643-1` y sont pourtant : la
plus ancienne, en vigueur de 1985 à 2004, traite de l'âge des anciens
combattants ; toutes les suivantes portent le barème en points du régime
d'après la réforme — 450 points au plafond de la première tranche en 2004, 525
en 2015, 557 depuis le décret n° 2024-688 du 5 juillet 2024. La conversion des
trimestres d'avant 2004 n'y figure dans aucune. Elle est donnée par la caisse,
qui la rattache à cet article, et recoupée par les guides de retraite ; elle est
saisie à ce titre, sur la foi du producteur, comme la valeur du point du même
régime — que la loi ne porte pas davantage, le décret annuel ne fixant qu'un
coefficient de revalorisation.

### Le simulateur doit être juste à tout âge : où il ne l'est pas encore

Une fiche de régime porte des PÉRIODES, et chaque période un jeu de règles. Un
régime dont la fiche n'a qu'une période applique donc les mêmes règles à toute
son histoire — et comme les fiches sont écrites à partir des paramètres
d'aujourd'hui, c'est le droit de 2026 qu'elles appliquent à 1950. Le tableau
ci-dessous compte, pour chaque régime, le nombre d'ANNÉES par jeu de règles
distinct. Plus le nombre est grand, moins l'histoire du régime est dans le
modèle :

| Régime | Couverture | Jeux de règles | Années par jeu | Coupures de texte non reflétées | Réformes non portées |
|---|---|---|---|---|---|
| `port_strasbourg` | 1930-2026 | 1 | 97 | 0 | 0 |
| `marins` | 1930-2026 | 1 | 97 | 2 | 0 |
| `sncf` | 1930-2033 | 16 | 79 | 1 | 0 |
| `ratp` | 1930-2033 | 16 | 79 | 3 | 0 |
| `assemblees_parlementaires` | 1930-2030 | 22 | 79 | 0 | 0 |
| `banque_de_france` | 1930-2026 | 16 | 78 | 0 | 0 |
| `cavec_complementaire` | 1953-2026 | 2 | 74 | 0 | 0 |
| `opera_de_paris` | 1930-2026 | 4 | 72 | 4 | 0 |
| `crpcen` | 1937-2026 | 16 | 71 | 0 | 0 |
| `ircec_racl` | 1962-2026 | 1 | 65 | 1 | 0 |
| `fonctionnaires_pacifique` | 1959-2029 | 8 | 65 | 0 | 0 |
| `cafat_nouvelle_caledonie` | 1958-2026 | 5 | 65 | 0 | 0 |
| `ircec_racd` | 1964-2026 | 1 | 63 | 2 | 0 |
| `comedie_francaise` | 1930-2026 | 4 | 63 | 1 | 0 |
| `cnbf` | 1948-2026 | 2 | 56 | 2 | 0 |
| `cps_polynesie` | 1968-2026 | 2 | 55 | 0 | 0 |
| `cnavpl` | 1949-2026 | 7 | 55 | 9 | 0 |
| `ircec_raap` | 1962-2026 | 5 | 54 | 2 | 0 |
| `seita` | 1935-2026 | 8 | 49 | 0 | 0 |
| `cese_membres` | 1957-2026 | 14 | 48 | 0 | 0 |
| `carcdsf_complementaire` | 1949-2026 | 22 | 48 | 0 | 0 |
| `regimes_professionnels_integres` | 1947-1993 | 1 | 47 | 0 | 0 |
| `cnracl` | 1945-2026 | 7 | 45 | 17 | 0 |
| `mines` | 1930-2026 | 22 | 44 | 1 | 0 |
| `cnbf_complementaire` | 1979-2026 | 2 | 40 | 0 | 0 |
| `ieg` | 1946-2026 | 15 | 38 | 3 | 0 |
| `gerants_debits_tabac` | 1963-2026 | 2 | 37 | 10 | 0 |
| `cavom_complementaire` | 1979-2026 | 2 | 37 | 5 | 0 |
| `wallis_et_futuna` | 1975-2026 | 13 | 34 | 0 | 0 |
| `msa_non_salaries` | 1952-2026 | 7 | 34 | 13 | 0 |
| `cipav_complementaire` | 1979-2026 | 4 | 34 | 1 | 0 |
| `crpnpac_tranche_2` | 1963-2026 | 4 | 32 | 0 | 0 |
| `crpnpac` | 1963-2026 | 4 | 32 | 5 | 0 |
| `cps_polynesie_tranche_b` | 1995-2026 | 1 | 32 | 0 | 0 |
| `cavp_complementaire` | 1949-2026 | 7 | 29 | 2 | 0 |
| `regime_general` | 1945-2026 | 8 | 27 | 14 | 0 |
| `msa_salaries` | 1945-2026 | 8 | 27 | 3 | 0 |
| `fspoeie` | 1930-2026 | 9 | 26 | 4 | 0 |
| `fonction_publique_etat` | 1948-2026 | 8 | 26 | 7 | 0 |
| `chemins_fer_secondaires` | 1930-1954 | 1 | 25 | 0 | 0 |
| `organic` | 1949-2006 | 5 | 24 | 3 | 0 |
| `msa_rco` | 2003-2026 | 1 | 24 | 24 | 0 |
| `cancava` | 1949-2006 | 5 | 24 | 3 | 0 |
| `cprn_complementaire` | 1949-2026 | 9 | 22 | 2 | 0 |
| `cavamac_complementaire` | 1968-2026 | 8 | 22 | 5 | 0 |
| `ipacte` | 1951-1970 | 1 | 20 | 0 | 0 |
| `pensions_civiles_1853` | 1930-1948 | 1 | 19 | 0 | 0 |
| `ircantec` | 1971-2026 | 15 | 17 | 6 | 0 |
| `rafp` | 2005-2026 | 2 | 16 | 6 | 0 |
| `cssm_mayotte` | 1987-2036 | 34 | 16 | 0 | 0 |
| `assurances_sociales` | 1930-1945 | 1 | 16 | 0 | 0 |
| `carpv_complementaire` | 1950-2026 | 10 | 15 | 0 | 0 |
| `organic_conjoints_batiment` | 1973-2003 | 4 | 13 | 0 | 0 |
| `cps_saint_pierre_et_miquelon` | 1987-2037 | 32 | 13 | 0 | 0 |
| `asv_conventionnes` | 1972-2026 | 21 | 13 | 10 | 0 |
| `agirc` | 1947-2018 | 24 | 13 | 0 | 0 |
| `rco_artisans` | 1979-2012 | 10 | 12 | 2 | 0 |
| `rci` | 2013-2026 | 2 | 12 | 2 | 0 |
| `cavimac` | 1979-2026 | 8 | 12 | 0 | 0 |
| `carpimko_complementaire` | 1984-2026 | 27 | 12 | 0 | 0 |
| `arrco` | 1961-2018 | 18 | 12 | 1 | 0 |
| `igrante` | 1960-1970 | 1 | 11 | 0 | 0 |
| `enseignants_prive_additionnel` | 2005-2026 | 6 | 11 | 1 | 0 |
| `arrco_tranche_2_entreprises_nouvelles` | 1997-2018 | 6 | 11 | 0 | 0 |
| `rsi` | 2006-2018 | 2 | 10 | 4 | 0 |
| `arrco_tranche_2` | 1961-2018 | 22 | 9 | 0 | 0 |
| `nric` | 2004-2012 | 2 | 8 | 3 | 0 |
| `carmf_complementaire` | 1949-2026 | 62 | 8 | 1 | 0 |
| `agirc_entreprises_nouvelles` | 1981-2018 | 17 | 7 | 0 | 0 |
| `unirs` | 1957-1961 | 1 | 5 | 0 | 0 |
| `avts` | 1941-1945 | 1 | 5 | 0 | 0 |
| `agirc_arrco` | 2019-2026 | 2 | 5 | 0 | 0 |

**Ce tableau n'est plus écrit à la main** : c'est la sortie de
`python scripts/calendrier_regimes.py --carte`, relevée après les tranches B1
à B5d de la campagne « les règles à travers l'histoire » (voir
[`regimes.md`](regimes.md), journal de la campagne). Les deux dernières
colonnes viennent de l'index LEGI et du calendrier des réformes
(`legislation/reformes.yaml`) : une « coupure de texte non reflétée » est une
version d'un article pivot (`regimes/pivots.yaml`) qui commence une année où
aucune période de la fiche ne commence — un endroit où lire, pas un verdict,
car beaucoup de versions ne changent qu'un renvoi ; une « réforme non portée »
est un manque, et le test `test_toute_reforme_est_coupee_absorbee_ou_declaree`
impose qu'il n'y en ait aucune. Les deux premières lignes restent ce qui
résiste : le port autonome de Strasbourg, dont le règlement de retraite est un
acte de l'établissement et non un texte publié, et les marins, dont la formule
est stable depuis 1968 — vérifiée article par article — mais dont la grille des
salaires forfaitaires reste introuvable.

Le nombre n'est pas à lui seul un verdict : un régime dont les règles n'ont pas
bougé mérite une seule période, et c'est le cas des trois complémentaires
libérales de la liste, qui prélèvent par classes depuis leur création. Mais il
dit où chercher, et ce qu'on y trouve est parfois gros : le régime des salariés
agricoles portait une période pour quatre-vingt-seize ans, avec les paramètres de
2023 — un salarié agricole parti en 1980 se voyait opposer 172 trimestres au lieu
de 150 et calculer sur ses vingt-cinq meilleures années au lieu de dix.

**Les témoins ne le voyaient pas, et c'est le second enseignement.** Le balayage
par statut ne connaissait qu'une génération, née en 1975 : il ne visitait que les
périodes RÉCENTES de chaque fiche. Corriger le régime agricole n'a déplacé aucun
témoin. Chaque statut est donc désormais simulé à QUATRE générations — née en
1925, qui liquide vers 1990 ; née en 1935, qui liquide vers 1999, sous la durée
requise de 150 ou 160 trimestres et les dix meilleures années ; née en 1955, qui
liquide vers 2019 ; née en 1975, qui liquide après la réforme de 2023. Le fichier
de témoins passe de 138 à 250 cas, et une correction d'histoire s'y voit
maintenant. La génération 1925 est la dernière venue, et pour une raison
précise : les tables par génération ne répondent pas toutes en deçà de 1934, et
le défaut que cela cachait est raconté plus bas.

Ce qui a été refermé de cette façon jusqu'ici : le régime des salariés agricoles
(aligné sur le régime général, ses huit périodes reprises une à une), les régimes
alignés des artisans et des commerçants depuis 1973, le fonds spécial des
ouvriers de l'État (aligné sur le code des pensions, six périodes), la Banque de
France (alignée depuis 2007, quatre périodes) et la caisse des clercs de notaire
(trois périodes au lieu d'une depuis 2009, et le barème de décote de la fonction
publique que son décret lui donne) ; la durée requise de l'Opéra et de la
Comédie-Française ; les bornes d'âge de la RATP et des IEG, qui étaient celles de
2017 dès 2009 ; et la clause du grand-père des régimes fermés.

**Trois manières de se tromper, et elles reviennent.** La première est la fiche
d'un régime ALIGNÉ qui ne suit pas l'histoire de son modèle : on la corrige en
recopiant les périodes du régime général ou du code des pensions, ce qui est sûr
parce que l'alignement est une règle de droit. La deuxième est la période
OUVERTE — `fin: null` — qui porte les paramètres du jour : elle applique le droit
d'aujourd'hui à toute la période qu'elle couvre, et c'est ainsi qu'un agent de la
Banque de France parti en 2009 se voyait opposer l'âge de 2023. La troisième est
la réforme qui ne touche pas tout en même temps : celle de 2008 ne relève les
bornes d'âge des régimes spéciaux qu'à partir de 2017, et sa décote n'existe pas
avant le 1er juillet 2010 — elle monte ensuite en charge jusqu'en 2024, quand les
fiches la servaient pleine dès 2009.

### La retenue de 8,9 % datait de 1990, et la loi la fait partir de 1989

L'article 23 de la loi n° 89-18 du 13 janvier 1989 — absente de l'index
thématique, lue sur Légifrance (`JORFTEXT000000321867`) — dispose que « le
taux de la retenue prévu à l'article L. 61 […] est majoré d'un point », pour
les traitements « perçus au titre de la période postérieure au 31 décembre
1988 ». La retenue passe donc de 7,9 % à 8,9 % au 1<sup>er</sup> janvier 1989,
comme OpenFisca la date ; les trois fiches — État, CNRACL, ouvriers de
l'État — la faisaient partir de 1990, date de la version de L. 61 que la base
LEGI consolide, et servaient 7,9 % un an de trop. Le contrôle de vraisemblance
ne signale plus d'écart.

### La clause du grand-père : six régimes fermés l'étaient pour tout le monde

Le régime de la SNCF est fermé aux agents **recrutés** depuis le 1er janvier
2020 ; celui de la RATP, des IEG, des clercs et employés de notaires, de la
Banque de France et des membres du CESE depuis le 1er septembre 2023 — les cinq
que nomme l'article 1er de la loi n° 2023-270 (`JORFARTI000047445082`), et
eux seuls : le dépôt a longtemps cru fermés l'Opéra de Paris, la
Comédie-Française et le port autonome de Strasbourg, que l'article ne nomme
pas, et laissait ouverts les clercs de notaires et la Banque de France, qu'il
nomme ; celui des mines depuis le 1er septembre 2010 ; celui de la SEITA depuis
1981. Dans tous ces cas, la fermeture ne vaut que pour les nouveaux entrants : **celui qui était déjà là
garde son régime jusqu'à sa retraite.** C'est la clause du grand-père, et les
fiches la nommaient — « Régime fermé aux agents recrutés depuis le 1er janvier
2020 », disait le routage de la SNCF.

Le routage, lui, ne connaissait que l'ANNÉE. À la date de fermeture, il faisait
basculer au régime général **tout le monde**, y compris l'agent entré vingt ans
plus tôt. Un cheminot né en 1975, entré en 1996, perdait ainsi vingt années de
régime spécial : sa pension passait de 55 319 € à 39 967 €, **trente-huit pour
cent de moins**. Un agent des IEG ou de la RATP en perdait trente-quatre, un
mineur dix-neuf.

Le routage apprend donc une seconde dimension. Une période d'affiliation peut
porter `entres_avant` ou `entres_depuis`, et la carrière fournit l'année
d'entrée dans le statut — sa première année, les lignes étant chronologiques.
Sans cette année, on suppose une entrée l'année demandée : c'est le comportement
d'avant, et il reste juste pour qui commence sa carrière cette année-là.

**Deux fiches ont dû s'allonger pour que le routage tienne.** Celle des mines
s'arrêtait en 2010 et celle de la SEITA en 1981 — leur année de fermeture. Or
un régime fermé aux nouveaux entrants continue d'accueillir ceux qui y sont :
leurs périodes courent donc jusqu'à aujourd'hui, aux mêmes paramètres, parce que
ces deux régimes sont en EXTINCTION et que les réformes de 2010, 2014 et 2023
les ont laissés où ils étaient — le programme 195 du budget de l'État les
finance à ce titre. Un test l'a imposé : il refuse qu'un statut route vers un
régime dont la fiche ne porte aucune période cette année-là.

### Le compte notionnel recevait une moyenne de période, et le droit changeait le taux chaque année

La fiche du régime général porte huit périodes de 1945 à aujourd'hui et, dans
chacune, un taux de cotisation qui est une **moyenne** — « moyenne OpenFisca sur
la période », disait le commentaire, et la note de 1945 avouait « une moyenne
de période, à affiner ». Or le droit a changé ce taux presque chaque année :
8,5 % en 1967, 8,75 % en 1970, 10,25 % en 1974, 12,9 % en 1979, 13,9 % en 1984,
15,8 % en 1989, 16,35 % en 1991, 17,87 % en 2024. La moyenne 1972-1982, à
11,19 %, prêtait à 1972 deux points et demi de plus qu'il n'en cotisait, et à
1982 un point et demi de moins ; celle de 1983-1993 portait un vingt-troisième
de déplafonnée à des années qui n'en avaient pas. C'est la cotisation qui
alimente le compte notionnel : les scénarios 2 à 6 recevaient un taux que
personne n'a payé une seule année.

`data/reference/regimes/taux_cotisation_annuels.csv` porte désormais, année par
année depuis 1967, le taux plafonné, sa part salariale, le taux déplafonné et
sa part, lus dans les barèmes datés d'OpenFisca-France — 1 074 valeurs, niveau
`haute`, écrites par `verifier_donnees.py --appliquer` depuis
`data/brut/openfisca_cotisations.json`. Le régime général et les salariés
agricoles y sont, les artisans, les commerçants et le RSI depuis l'alignement
de 1973, et les trois fiches qui recopiaient les moyennes du régime général
— les cultes, dont R. 382-89 et R. 382-90 fixent la cotisation à celle du
régime général, Mayotte et Saint-Pierre-et-Miquelon, dont les taux propres ne
sont pas dans l'index : un test relisait déjà la CAVIMAC année par année
contre le régime général, et c'est lui qui a exigé qu'elle suive la même
série. Le chargeur des fiches découpe chaque période
`plafonnee` de ces régimes selon la table, refond les années consécutives
identiques et garde la borne de la fiche : le régime général passe de huit
périodes chargées à vingt-six, sans qu'une ligne de liquidation change — la
durée, le salaire de référence, la décote sont recopiés tels quels, seule la
cotisation se date. Le portage JavaScript reçoit les périodes découpées dans
le paquet de données et n'a rien à refaire. La moyenne reste écrite dans la
fiche : elle sert aux années que la table ne couvre pas — avant 1967 au régime
général, où « le taux de cotisation vieillesse évolue de 8 % (1946) à environ
8,75 % (1971) » et où aucune transcription n'existe — et au contrôle de
vraisemblance, qui la confronte à la même série.

Ce que cela déplace se lit dans les témoins : moins d'un pour cent de capital
notionnel pour les carrières balayées, dans un sens ou dans l'autre selon que
leurs années fortes tombaient au-dessus ou au-dessous de la moyenne — un
salarié né en 1935 gagne un pour cent au scénario 2 ; le scénario 1 ne bouge
pas, puisqu'il liquide sur les trimestres et le salaire de référence, non sur
la cotisation.

### La lecture des taux de cotisation, et les quatre choses qu'elle a trouvées

La table annuelle ci-dessus venait d'OpenFisca-France : une transcription, et
donc `haute` au mieux. Un taux de cotisation n'est pourtant pas une
statistique, c'est un article de code, et la base LEGI en garde les rédactions
successives. `scripts/fetch/dila_legi_taux_cotisation.py` les lit : article 2
du décret n° 81-1013 du 13 novembre 1981 puis article **D. 242-4** du code de
la sécurité sociale pour le régime général, article 2 du décret n° 50-444 du
20 avril 1950 puis article **D. 741-35** du code rural pour les salariés
agricoles. **368 valeurs certifiées** — 45 années pour le premier (1982-2026),
47 pour le second (1980-2026), quatre mesures chacune —, dont **112 corrigeaient
la transcription**.

**1. La règle du 1er janvier n'était pas appliquée.** Le dépôt retient, pour
une année, le taux en vigueur au 1er JANVIER ; `docs/methodologie.md` l'écrit,
et le récupérateur d'OpenFisca le disait dans sa propre docstring. Son filtre
comparait pourtant les ANNÉES et non les dates : un relèvement du 1er juillet
commandait l'année entière, et c'était donc le taux du 31 décembre qui sortait.
Six années du régime général en portaient la marque — 1970, 1976, 1986, 1987,
1991 et 2012. 1986 recevait les 14,6 % du 30 juillet au lieu de 13,9 %, 1976
les 11,15 % d'octobre au lieu de 10,75 %,
et surtout **1991 recevait la réforme du 1er février** — 14,75 % plafonné plus
1,60 % déplafonné — quand le 1er janvier de cette année-là le régime prélevait
encore 15,8 % sous le seul plafond. Le même filtre datait la retenue des
fonctionnaires, et les fiches de la fonction publique s'étaient alignées sur
lui : leur note disait « le millésime porte le taux en vigueur en fin d'année,
comme les autres séries de taux du dépôt », ce qui était faux du dépôt et vrai
seulement du filtre. Les deux sont corrigés ensemble ; la retenue de l'agent
vaut 7 % en 1986, 7,7 % en 1987, 8,9 % en 1991, et ne tombe à 7,85 % qu'en 1992.

**2. Un taux que l'article ne portait pas.** Lire la seule chaîne des versions
donnerait 6,40 % de part salariale au 1er janvier 1988 : c'est ce que D. 242-4
disait alors. Le *Journal officiel* dit 6,60 %. Le décret n° 87-453 du 29 juin
1987 avait relevé la cotisation salariale de 0,2 point « à titre exceptionnel
et temporaire » du 1er juillet 1987 au 30 juin 1988 **sans réécrire l'article**,
que le décret du 22 juin 1988 n'a rattrapé qu'en pérennisant la hausse. Un
article codifié ne dit donc pas tout, et le récupérateur ne s'en remet pas à
lui seul : il interroge la base JORF pour tout décret publié depuis 1982 qui
annonce dans son titre des taux de cotisation de ces régimes, et **arrête la
certification** si l'un d'eux n'est expliqué ni par une version de la chaîne,
ni par une surcharge déclarée, ni par une ligne qui dit pourquoi il ne touche
pas à ce taux. La surcharge de 1987 est elle-même relue à chaque exécution —
période et taux dans la notice, corroboration par la version qui pérennise.

**3. Les salariés agricoles n'avaient pas les taux du régime général.** Le
dépôt leur donnait sa série, et écrivait que « L. 741-9 renvoie aux taux du
régime général ». C'est vrai depuis le 1er janvier 2014, où le II de l'article
D. 741-35 dispose que leur taux « est fixé selon les dispositions prévues à
l'article D. 242-4 » ; c'est faux avant. De 1980 à 2013, **l'employeur agricole
a payé un point de moins** que celui du privé — 7,20 % contre 8,20 % de 1980 à
2005, 7,30 puis 7,31 et 7,41 % contre 8,30, 8,40 et 8,45 % ensuite — quand la
part du salarié, elle, était la même. Un salarié agricole né en 1945 voit donc
la part patronale de sa carrière tomber de 87 276 à 79 909 €, et sa pension du
scénario 4 de **5 %**. C'est le plus gros déplacement de cette lecture, et il
ne concerne qu'un régime : les quatre carrières du privé bougent de deux
dixièmes de pour cent.

**4. Ce que la base ne permet pas de dater, et comment elle le dit.** Avant
1982, l'article 3 du décret n° 67-803 est bien dans LEGI, avec ses quatre
composantes en toutes lettres — mais avec UNE version, du 1er octobre 1967 au
14 novembre 1981, portant 12,9 %, c'est-à-dire l'état de 1979. Le récupérateur
lit cet article comme les autres et le refuse par une règle écrite : un article
qui n'a qu'une version et couvre plus de dix ans n'a pas de chronologie. Ces
quinze années restent transcrites d'OpenFisca, au niveau `haute`.

Une dernière chose, trouvée par un contrôle et laissée telle quelle : l'article
D. 741-35, dans sa rédaction du 22 avril 2005, annonce 15,15 % puis détaille
7,20 + 6,55 + 1,40 + 0,10, soit 15,25 %. La recodification a gardé le total
d'avant 2004, quand il ne comptait pas encore la part salariale déplafonnée.
Ce sont les composantes qui sont écrites et le dépôt les retient ; l'écart est
signalé à chaque exécution plutôt que corrigé en silence.

**Ce que tout cela déplace.** 287 cas de témoin sur 427, et la page Coût à
peine : le cumul 1959-2024 du scénario 4 passe de −51,8 % à **−51,9 %**, celui
du scénario 6 de −51,6 % à **−51,7 %**, celui du 2 reste à −79,5 % — trois
chiffres d'alors, que la catégorie active et la pension militaire ont portés à
−52,6 %, −52,4 % et −79,8 %, puis l'âge de liquidation par génération à
−56,0 %, −51,8 % et −81,0 %. Le scénario
1 ne bouge nulle part, puisqu'il liquide sur les trimestres et le salaire de
référence, non sur la cotisation.

### Ce que vaut une série qu'on ne peut pas certifier

Deux séries de taux ne se certifieront pas, et il fallait dire mieux que « pas
certifiées ». Le régime général d'avant 1982, que la base LEGI ne date pas ; et
les complémentaires du privé, dont les taux ne sont dans aucun texte
réglementaire. Les deux venaient d'OpenFisca-France.

**OpenFisca n'est pas la source.** Il transcrit les barèmes de l'Institut des
politiques publiques, qui sont l'amont — la page qui précède l'écrivait déjà,
pour dire que l'IPP « ne commence pas plus tôt que lui ». C'était vrai, et à
côté de la question : ce que l'IPP a et qu'OpenFisca perd en route, ce sont deux
colonnes. `reference` nomme le texte de chaque marche ; `official_journal_date`
donne sa publication. `scripts/fetch/ipp_taux_cotisation.py` les lit, et
`verifier_donnees.py` en tire trois constats à chaque exécution.

**Un : la confrontation vérifie une copie, pas une lecture.** Les soixante
années du régime général sont confrontées à l'IPP, et un écart y est une erreur
de recopie d'OpenFisca — non un désaccord entre deux témoins. Le contrôle le dit
dans ses propres mots, pour que personne ne prenne son « OK » pour une seconde
source. Il en a déjà trouvé une : OpenFisca servait 0,1 % de part salariale
déplafonnée **dès le 1er janvier 2004** quand elle naît le 1er juillet. La cause
était la même que celle du filtre de l'année, et au même endroit : l'exception
« année d'ouverture » s'appliquait à chaque composante au lieu de la seule année
où la série commence.

**Deux : la chronologie, elle, se vérifie.** Pour chaque marche, le récupérateur
cherche dans l'index JORF le texte que l'IPP nomme, au numéro et à la date
annoncés. **Trente-cinq des trente-six marches de la CNAV y sont** ; la seule qui
manque est le décret n° 70-680 du 30 juillet 1970, absent de l'index. Une valeur
transcrite reste une valeur transcrite, mais la DATE de chaque marche est
désormais vérifiée contre le *Journal officiel* — et c'est la date dont dépend
la règle du 1er janvier, celle qui déplaçait six années à elle seule.

**Trois : les complémentaires ne se certifieront pas, et c'est l'IPP qui le
dit.** Pour l'Agirc, l'Arrco et le régime unifié, il laisse lui-même la colonne
du *Journal officiel* VIDE sur ses vingt-cinq marches, et cite « Convention
AGIRC du 14 mars 1947 », « Accords ARRCO du 12 novembre 1986 »,
« Lettre-circulaire ARRCO 82-28 ». Ces taux sont fixés par accord collectif ; le
*Journal officiel* n'en publie que l'**avis d'extension**, qui renvoie au
Bulletin officiel Conventions collectives sans jamais écrire le chiffre — on
peut le lire dans la base, avis par avis, de 2006 à 2015. La fédération
Agirc-Arrco publie la compilation de ses valeurs de point, que le dépôt lit déjà,
mais aucun historique de taux : sa page « Paramètres » n'affiche que l'année
courante, et ses circulaires ne remontent qu'à 2003. La démonstration est
mécanique, et c'est ce qui la rend utile : si l'IPP se met un jour à remplir
cette colonne, le contrôle le dira.

**Et il a trouvé ce que personne ne cherchait.** Sur 1967-1981, le récupérateur
demande au JORF les décrets qui annoncent dans leur titre des taux de cotisation
du régime général, et compte ceux qu'aucune marche ne rejoint. Il en reste **un**,
et il est lourd : le **décret n° 79-650 du 30 juillet 1979** a relevé « à titre
exceptionnel, par dérogation aux dispositions du décret n° 78-1213 » les taux du
régime général « du 01-08 au 31-12-1979 et du 01-01-1980 au 31-01-1981 ». La
fenêtre couvre **deux premiers janvier**, 1980 et 1981. Ni l'IPP ni OpenFisca ne
la portent, et le dépôt en a conclu que les taux servis pour ces deux années
étaient **trop bas**, d'un montant que la notice n'écrit pas — elle ne nomme
même aucun risque, et le décret lui-même a disparu de LEGI avec sa date
d'expiration.

#### Ils ne sont pas trop bas : ce décret ne touche pas la vieillesse

*Établi le 21 septembre 2026, après une recherche qui n'avait pas été faite.*
Le raisonnement précédent tenait à une lecture du seul TITRE du décret —
« augmentation du taux des cotisations d'assurances sociales et des allocations
familiales » —, où « assurances sociales » couvre en principe la vieillesse
comme la maladie. Trois lectures le démentent, et elles convergent.

**Le recueil statistique de la Cnav**, titre II « Les cotisations et les
cotisants », tableau T2-2, écrit la série complète des taux par branche et par
date d'effet. Elle donne, pour le salarié : maladie **3,50 % au 1er janvier
1979, 4,50 % au 1er août 1979**, et retour à **4,50 % au 1er février 1981** —
la fenêtre exacte du décret, dix-huit mois — pendant que la colonne vieillesse
reste à **4,70 %** d'un bout à l'autre. Du côté employeur, rien ne bouge : 8,95
en maladie plafonnée et 8,20 en vieillesse, du 1er janvier 1979 au 13 novembre
1981. Le texte du même recueil le dit en toutes lettres : « pour l'assurance
vieillesse, le taux de cotisation sur le salaire plafonné de 12,90 % au
1er janvier 1979 est passé à 13,90 % au 1er janvier 1984 » — sans marche
entre-temps.

**La chaîne des versions dans LEGI** dit la même chose par son silence. Le
décret n° 67-803 porte les taux du régime général jusqu'en 1981 : son article
premier (maladie) et son article 2 (la répartition plafonné/déplafonné de la
maladie) ont une version qui s'ouvre au **1er janvier 1980**, c'est-à-dire à la
seconde fenêtre du décret exceptionnel ; son **article 3, qui est celui de la
vieillesse, n'en a aucune** — sa rédaction unique porte 12,90 %, soit 8,20 %
employeur et 4,70 % salarié, jusqu'à son abrogation du 13 novembre 1981.

**Et la mesure elle-même est documentée** : c'est le plan Barrot, présenté trois
semaines après l'arrivée de Jacques Barrot au ministère, dont la pièce
principale est une cotisation exceptionnelle d'un point à la charge des seuls
salariés, pour dix-huit mois, décidée devant le dérapage des dépenses
d'ASSURANCE MALADIE.

**Ce qui change dans le dépôt.** Les taux de 1980 et 1981 restent ce qu'ils
sont, et leur niveau `haute` est celui qu'ils méritent : ils ne sont ni faux ni
plus incertains que leurs voisins. Le décret rejoint, dans
`ipp_taux_cotisation.py`, la liste des textes que la série ignore À BON DROIT,
avec sa raison écrite — il n'y a plus, sur 1967-1981, un seul décret de taux du
régime général que personne n'ait expliqué.

**Et une leçon, qui vaut plus que le chiffre.** Le contrôle qui a trouvé ce
décret était juste ; c'est la conclusion qu'on en avait tirée qui ne l'était
pas. « Un décret que la série ignore » ne veut pas dire « les années qu'il
couvre sont fausses » : il veut dire que personne n'a encore dit ce que ce
texte fait à ces années. Le message du contrôle disait la première phrase ; il
dit maintenant la seconde.

C'est de là que vient une règle du récupérateur qui lit les textes : son
garde-fou **n'exige pas le mot « vieillesse »**. Un décret de la forme du
n° 79-650 ne doit pas pouvoir traverser la période certifiée sans être vu.

**Une corroboration, et ce qu'elle ne prouve pas.** La notice du décret
n° 81-1013 du 13 novembre 1981 est la seule du JORF ancien à porter les chiffres
— « VIEILLESSE : 12,9 % (8,2 % POUR L'EMPLOYEUR, 4,7 % POUR LES SALARIES) » —
et le récupérateur vérifie qu'ils sont ceux que la série porte à cette date. Ils
le sont. Ce n'est pas une certification : un décret dit ce qui vaut à partir de
sa publication, non ce qui valait avant. Il confirme le niveau qu'il trouve, et
rien de plus.

### Avant 1967, la cotisation vieillesse n'existait pas séparément — et le dépôt lui prêtait 8,6 %

La fiche du régime général portait, de 1945 à 1966, une moyenne de 8,6 % sans
texte : avant l'ordonnance du 21 août 1967, la cotisation des assurances
sociales couvrait maladie, maternité, invalidité, vieillesse et décès d'un
seul taux, et aucun texte n'en isolait la part vieillesse. Le tableau « Taux
de cotisation vieillesse des assurances sociales (maladie et vieillesse) du
régime général (1945-1967) » du document du COR *L'évolution des paramètres du
régime de la CNAV* (d'après la Cnav, lu par `sites_institutionnels.py`) date
chaque taux et son texte : 6 % salarié et 6 % employeur au 1<sup>er</sup>
janvier 1945 (ordonnance du 30 décembre 1944), 10 % employeur en 1947, 12,5 %
en 1959, 13,5 % en 1961, 14,25 % en 1962, 15 % au 1<sup>er</sup> septembre 1966.

La part vieillesse est une **convention, nommée et unique** : celle que
l'ordonnance de 1967 a donnée à la vieillesse en séparant les branches, 8,5
points sur 21 (3 + 5,5 pour la vieillesse, 6 + 15 en tout, décret n° 67-803).
Elle vaut 4,86 % en 1945, 6,48 % de 1947 à 1958, 7,49 % en 1959, 7,89 % en
1961, 8,20 % en 1962, 8,50 % en 1966 — et 1966 retrouve exactement le taux du
1<sup>er</sup> octobre 1967, ce qui est le signe que la convention ne fait
pas violence à la série. La Cnav, elle, retient « un taux de 9 % » pour les
périodes antérieures au 1<sup>er</sup> octobre 1967 dans ses calculs de
validation. Ces 132 valeurs sont au niveau `estimee`, parce que la convention
n'est pas un texte ; les taux globaux, eux, sont datés. Un salarié né en 1925
gagne quelques pour cent de capital notionnel sur ses années 1945-1958, à
6,5 % au lieu de 8,6 %.

### Le marin cotisait sur sa paie, et le régime ne connaît que vingt forfaits

Le régime des marins ne cotise ni ne liquide sur le salaire réel mais sur un
**salaire forfaitaire par catégorie de fonction à bord** — vingt catégories,
de l'apprenti à la vingtième —, dont « le montant est fixé par arrêté »
(décret n° 2020-649). La fiche s'en tenait au revenu déclaré, au motif que la
grille n'était pas chiffrée au Journal officiel et qu'une convention manquait
pour l'appliquer à un revenu. La première raison est tombée : les arrêtés
annuels « portant majoration des salaires forfaitaires » publient les vingt
montants depuis 2008, et l'index JORF du dépôt les porte tous
(`JORFARTI000017964781` en 2008 … `JORFARTI000053743024` en 2026) ;
`scripts/fetch/jorf_salaires_forfaitaires_marins.py` les lit, et
`verifier_donnees.py --appliquer` en fait `salaires_forfaitaires.csv`, 380
montants au niveau `certifiee`, grille en vigueur au 1<sup>er</sup> juillet de
chaque année.

La seconde raison est une **convention, nommée** : le moteur range le marin,
chaque année, dans la catégorie dont le forfait est le plus proche de son
revenu annualisé (`assiette_grille: marins`, dans les deux moteurs), et cotise
comme il liquide sur ce forfait — le salaire de référence est le forfait de la
catégorie de la dernière année, ce que R. 11 demande. Un marin à 40 000 € en
2024 est de treizième catégorie (41 468 €) ; à 20 000 €, de troisième
(21 504 €) ; au-delà de 75 000 €, de vingtième. Avant 2008, les textes de
l'index ne portent que le titre ou le visa (décrets de 1956 à 1961, arrêtés de
1991 à 2006) : la grille de 2008 est ramenée par le salaire moyen, et ces
années sont marquées estimées.

### Le marin de cinquante ans, et ce que la caisse applique que le modèle n'applique pas

Le 22 septembre 2026, les six pages que l'ENIM consacre à la retraite ont été
lues (action 89), puis confrontées au code des pensions de retraite des marins
dans l'index LEGI. Deux règles manquaient au modèle, et le texte comme la
caisse les écrivent.

**Le départ à cinquante ans était refusé.** L'article R. 2 acquiert la pension
d'ancienneté « lorsque se trouve remplie la double condition de cinquante ans
d'âge et de vingt-cinq années de services » ; les cinquante-cinq ans qu'il
fixe ensuite ne bornent que l'entrée en jouissance de celui qui continue à
naviguer (L. 5552-5 du code des transports). La fiche avait pris cette borne
pour l'âge d'ouverture, et refusait donc le départ même que le plafond de
vingt-cinq annuités de R. 13 organise. L'ENIM le décrit en une phrase —
« Gaspard, marin, a 50 ans et réunit 25 ans de services […] Il peut prétendre
au versement d'une pension d'ancienneté » —, qui est désormais un témoin. Le
plafond est aussi levé à cinquante-deux ans et demi pour trente-sept annuités
et demie, comme le même article le veut.

**La bonification pour enfants n'était pas servie.** R. 14 : « 5 % de son
montant pour deux enfants, 10 % pour trois enfants et 15 % au-delà ». La fiche
ne déclarait aucune majoration ; elle en porte désormais le barème propre, le
seul du catalogue qui commence à deux enfants. L'exemple de l'ENIM — 870,79 €
par mois, plus 43,54 € pour deux enfants — est rejoué.

**Ce qui reste, et que la caisse applique.**

- La pension SPÉCIALE, moins de quinze ans de services, entre en jouissance
  avec l'autre pension de base, jamais avant cinquante-cinq ans, et à soixante
  ans sans autre pension (L. 5552-12, R. 5). Le modèle l'ouvrait à
  cinquante-cinq ans dans tous les cas — et faisait liquider à cet âge toute
  la carrière d'un polypensionné passé dix ans par la mer, régime général
  compris. C'est corrigé le même jour. La page de l'ENIM se contredit : son
  texte renvoie à l'âge légal du régime général, soixante-quatre ans pour les
  générations 1968 et suivantes, et l'exemple qui suit fait partir Henry « à
  60 ans ». C'est R. 5 qui fait foi.
- Le salaire de référence est le forfait de la catégorie MOYENNE des
  trente-six derniers mois, ou d'une catégorie supérieure tenue cinq ans
  (R. 11) ; le modèle prend celle de la dernière année. Les services se
  décomptent au semestre (R. 12), le modèle au trimestre. L'écart tient à une
  catégorie et à un trimestre au plus.
- Le taux réduit de 1 % par annuité des services de petite pêche et de pêche
  côtière outre-mer, le partage des droits du conjoint collaborateur, la
  réversion à 54 % de la pension et des bonifications, et la cessation
  anticipée des marins exposés à l'amiante — dès cinquante ans, à soixante ans
  moins le tiers des services à la machine — ne sont pas modélisés.

La grille des salaires forfaitaires, elle, est exacte : les vingt montants
publiés par l'ENIM au 1<sup>er</sup> avril 2026 sont ceux du dépôt, au centime.

### Un jeune d'aujourd'hui pouvait se déclarer mineur, et la page le laissait croire

Le routage savait qu'un mineur recruté après septembre 2010 relève du régime
général : il l'y envoyait, en silence, et la page affichait « Mineur » au-dessus
d'une pension de salarié du privé. Trois choses changent.

**Le formulaire date chaque statut**, dans le libellé même du menu — « Artiste-auteur
(depuis 1977) », « Mineur (recrutés avant septembre 2010) » — et grise ceux que
l'entrée saisie ferme, dès que l'année de naissance ou l'âge de début change.
L'option déjà choisie n'est jamais désactivée, parce qu'un navigateur n'envoie
pas la valeur d'une option désactivée et que la saisie repartirait sur le statut
par défaut sans que rien ne le dise : c'est **le calcul qui refuse**, en nommant
la date d'entrée, la date de fermeture, et le statut de droit commun qui porte
le même calcul — un test impose que ce statut route exactement les mêmes
régimes, sans quoi le conseil enverrait vers un autre chiffre. Le statut
fermé se lit dans le routage lui-même (`entres_avant`), et `releve_par` nomme
le relais ; rien n'est écrit deux fois.

**La fermeture se lit au mois.** Les bornes du routage s'écrivaient en années,
et deux conventions y cohabitaient : `2011` pour les mines, fermées au
1<sup>er</sup> septembre 2010 — le recruté d'octobre 2010 recevait le régime —,
`2023` pour la RATP, fermée au 1<sup>er</sup> septembre 2023 — le recruté de
mars 2023 le perdait. Elles s'écrivent désormais `2010-09` et `2023-09`, et se
comparent à la **date d'entrée dans le statut**, que la carrière porte depuis
que le parcours la date. Ce n'est pas un raffinement : l'année d'un changement
de métier revient au métier qui en occupe le plus de mois, si bien qu'un agent
entré à la RATP en octobre 2022 n'y avait sa première ligne qu'en 2023 — et
était traité comme recruté après la fermeture. La SEITA, elle, était bornée à
`1982` quand la loi n° 84-603 maintient le régime « pour les personnels
titulaires en fonctions à la date d'entrée en vigueur de la loi du 2 juillet
1980 » : la borne est ramenée à 1981, l'année que la fiche retient.

**Un statut peut changer de régimes sans se fermer.** Le libéral non
réglementé — consultant, formateur, coach, développeur — est à la CNAVPL et à
la Cipav s'il s'est installé avant 2019, au régime général et au RCI depuis :
l'article L. 640-1 (rédaction du 1<sup>er</sup> janvier 2018,
`LEGIARTI000036391511`) n'énumère plus que les professions que la Cipav
conserve, l'article 50 X de la loi n° 2016-1827 l'applique aux créations
d'activité « au plus tard le 1<sup>er</sup> janvier 2019 » hors micro-social,
et l'article 15 de la loi n° 2017-1836 (`JORFARTI000036339157`) laisse les
affiliés d'avant là où ils étaient. L'inventaire le signalait comme ce que
« le routage du statut générique devrait » faire ; le statut
`liberal_non_reglemente` le fait, par les mêmes bornes `entres_avant` et
`entres_depuis` que la clause du grand-père — sans `releve_par`, parce que le
métier ne cesse pas d'exister : le formulaire le propose à toute date, et un
test exige qu'un tel statut route encore quelque chose à qui entre après la
borne. Le statut `profession_liberale` reste celui des professions de la
liste.

**Le balayage des témoins entre dans les régimes fermés avant leur
fermeture** — à dix-neuf ans pour l'agent des chemins de fer secondaires né en
1935 —, et renonce aux générations qui ne peuvent plus y entrer : leur témoin
n'aurait comparé qu'un salarié du privé.

### L'Ircantec n'avait pas de tranche B, et ses taux étaient ceux de 2008

Le catalogue décrivait l'Ircantec par deux périodes et une seule assiette : la
tranche A, de zéro au plafond de la Sécurité sociale. Le régime en a deux. La
**tranche B** court du plafond à huit fois le plafond, à un taux appelé de
19,50 % — près de trois fois celui de la tranche A. Un contractuel payé trois
fois le salaire moyen versait donc 14 600 € par an à un régime qui ne lui
portait aucun point : sa pension Ircantec ne dépassait celle d'un agent payé au
plafond que de quinze pour cent, quand le droit la lui triple.

Les taux de la tranche A étaient faux aussi, et depuis l'origine : la fiche
portait **5,75 % sur toute la période 1971-2008**, quand le taux appelé valait
2,10 % jusqu'en 1982, 2,80 % jusqu'en 1987, et n'a atteint 5,63 % qu'en 1992.
Le régime achetant ses points avec la cotisation — `points = cotisation /
(taux d'appel × salaire de référence)` —, un agent des années 1970 recevait
**deux fois et demie** les points que le barème lui donnait. La fiche portait en
outre 7,03 % pour l'après-2008 ; le taux appelé est de 7,00 % depuis 2017, et
7,11 % depuis le 1er janvier 2026.

**La série était déjà dans le dépôt, ou presque.** Le récupérateur de la Caisse
des dépôts — qui GÈRE l'Ircantec, et en est donc le producteur — télécharge
depuis le début le fichier `IRC_BAR_01_txcotis.csv`, qui porte cinq colonnes :
taux théoriques et appelés des deux tranches, et taux d'appel. Il n'en gardait
qu'une, le taux d'appel. Les quatre autres étaient téléchargées puis jetées, à
chaque exécution, depuis que le script existe. Il les consigne désormais.

**Le contrôle est un régime voisin.** Un contractuel du public à trois fois le
salaire moyen, carrière complète, obtient maintenant 81 799 € de pension totale.
Un cadre du privé au même salaire et à la même carrière en obtient 83 678 € par
une mécanique entièrement différente — Agirc, Arrco, Agirc-Arrco et régime
général. Deux pour cent d'écart entre deux structures qui n'ont rien en commun :
c'est le meilleur contrôle disponible, et il ne valait rien avant, le
contractuel ressortant quarante pour cent en dessous.

La répartition entre l'agent et l'employeur — 40 % / 60 % sur la tranche A,
35,64 % / 64,36 % sur la tranche B — est celle des barèmes 2025 et 2026 (2,80 %
et 4,20 %, 6,95 % et 12,55 % en 2025 ; 2,84 % et 4,27 %, 7,06 % et 12,75 % en
2026, recoupés par plusieurs centres de gestion), reportée sur les années
antérieures faute d'une série publiée. Elle ne touche que les scénarios 4 et 5.
Le salaire de référence et la valeur du point, eux, s'arrêtent en 2022 chez le
producteur comme chez OpenFisca : les années suivantes sont ramenées sur les
prix, et les arrêtés annuels qui les fixent restent à dépouiller.

### La tranche 2 de l'Arrco était servie aux cadres, qui n'y cotisent pas

La même vérification, poussée jusqu'au bout, retourne l'erreur. La tranche 2 de
l'Arrco — d'un à trois plafonds — avait été ajoutée au catalogue parce qu'elle
manquait aux non-cadres ; elle avait été ajoutée à la fiche `arrco`, que
l'affiliation donne AUSSI aux cadres. Or un cadre ne cotise pas la tranche 2 de
l'Arrco : au-dessus du plafond, c'est l'Agirc qui prend le relais. Le modèle lui
servait donc DEUX PENSIONS SUR LA MÊME PART DE SALAIRE. À deux plafonds de
rémunération, cela lui prêtait 8 374 € par an qu'aucun régime ne lui devait —
un cinquième de sa pension totale.

Une tranche que tous les affiliés d'un régime ne cotisent pas ne peut pas vivre
dans la fiche de ce régime : c'est l'AFFILIATION qui doit la donner aux uns et
pas aux autres. La tranche 2 de l'Arrco devient donc une fiche à part
(`arrco_tranche_2`), attribuée aux cinq statuts non cadres — salarié du privé,
salarié agricole, mineur d'après 2011, agent de la SEITA, agent des chemins de
fer secondaires — et à eux seuls. Le catalogue passe de cinquante-trois à cinquante-quatre fiches sans
qu'aucun régime nouveau n'existe : c'est un découpage, pas une découverte.

**Et elle existe depuis 1961, pas depuis 1996.** La fiche affirmait qu'« avant
1997, l'Arrco ne cotisait pas au-dessus du plafond ». C'est vrai des seules
entreprises créées à compter du 1er janvier 1997, dont le barème commence à
14 % ; l'accord du 8 décembre 1961 asseyait déjà la cotisation des non-cadres
sur la totalité du salaire jusqu'à trois plafonds, au taux de la tranche 1, et
OpenFisca-France en porte la série dans son barème des entreprises adhérentes
avant 1997. La tranche B3 de la campagne (voir [`regimes.md`](regimes.md)) a
retenu ce barème-là, pour l'Arrco comme pour l'Agirc (entreprises adhérentes
avant 1981) : c'est la population la plus nombreuse, et la carrière saisie ne
dit pas la date de création de l'employeur. Le barème des entreprises nouvelles
— 12 % à l'Agirc dès 1983, 14 % sur la tranche 2 dès 1997 — est porté par deux
fiches parallèles (`agirc_entreprises_nouvelles`, `arrco_tranche_2_entreprises_nouvelles`,
points Agirc et Arrco par `points_de`) et par deux statuts, « cadre, entreprise
créée après 1981 » et « non cadre, entreprise créée après 1997 » : c'est à
l'utilisateur de dire dans quelle entreprise il a travaillé, et le modèle ne
choisit plus pour lui. Les deux barèmes se rejoignent en 1996 à l'Agirc et en
2005 à l'Arrco.

Les points, eux, restent des POINTS ARRCO. Le moteur apprend pour cela un champ
`points_de`, qui dit de quel régime une période emprunte le barème — prix
d'achat, valeur de service, échelle de conversion aux fusions. Sans lui, la
tranche 2 aurait eu besoin d'une copie de la série Arrco sous son propre code,
et deux séries identiques finissent toujours par diverger.

Le contrôle : la pension du non-cadre ne bouge pas d'un euro — 6 445 € de
tranche 1 plus 8 374 € de tranche 2, exactement ce que la fiche unique donnait —
et celle du cadre perd les 8 374 € qu'elle ne devait pas avoir.

### Et l'Agirc n'avait pas de tranche C

Le même contrôle, passé sur tout le catalogue, en trouve une seconde. L'Agirc
cotisait sur DEUX tranches — B, d'un à quatre plafonds, et C, de quatre à
huit —, et la fiche le disait en toutes lettres : « régime par points sur les
tranches B et C ». Elle ne portait que la tranche B. Un cadre payé au-dessus de
quatre plafonds voyait donc sa pension Agirc **saturer** : 54 442 € à six fois
le salaire moyen comme à huit, alors que le régime lui en sert 70 773 € et
95 108 €. C'est un tiers puis trois quarts de pension Agirc effacés.

Trois choses rendaient la correction sûre. Le taux d'abord : le barème
d'OpenFisca-France, qui transcrit le Barème social périodique, porte le **même
taux sur les deux tranches**, année par année, de 1948 à la fusion de 2019 — la
tranche C n'a donc pas de série propre à retrouver. La date ensuite : la
cotisation sur la tranche C n'est obligatoire que « depuis le 01/01/88 pour les
entreprises affiliées à CCSBTP, IRCASUP et IRICASE ; au 01/01/91 pour toutes les
entreprises », et la fiche commence donc en **1991** — avant, elle dépendait de
l'entreprise, c'est-à-dire d'un choix que la carrière saisie ne porte pas et que
le modèle ne prête à personne. La répartition enfin : elle est LIBRE sur la
tranche C, fixée par accord d'entreprise, et la documentation d'OpenFisca
conseille elle-même d'y appliquer celle de la tranche B.

La garantie minimale de points reste sur la seule tranche B : la porter aussi
sur la C donnerait 240 points par an au cadre qui dépasse quatre plafonds, quand
l'accord de 1988 lui en garantit 120.

Aucune des cent trente-huit carrières témoins ne dépasse quatre plafonds : la
correction ne déplace aucun témoin, et c'est précisément pourquoi elle avait pu
rester invisible.

### « De 23 à 113 points » : le barème que personne ne publiait est dans le code

La MSA, le ministère de l'agriculture et tous les guides de retraite écrivent la
même phrase : le nombre de points de la retraite proportionnelle des chefs
d'exploitation « varie de 23 à 113 selon le barème ». Aucun ne donne le barème,
et ce document l'a longtemps rangé parmi les paramètres que personne ne publie.
Il est dans le **code rural**, en deux articles, et il n'y est pas caché :

* `R. 732-71` écrit un escalier à quatre marches — quinze points jusqu'à
  **400 SMIC horaires** ; une pente de quinze à trente entre 400 et
  **800 SMIC** ; trente points de là jusqu'à **deux fois le minimum
  contributif** ; puis une pente de trente au maximum de l'année jusqu'au
  **plafond de la Sécurité sociale** ;
* `R. 732-70` définit ce maximum : `M = (PM − AVTS) / (37,5 × VP)`, où PM est la
  pension maximale du régime général — la moitié du plafond —, AVTS
  l'allocation aux vieux travailleurs salariés et VP la valeur du point.

**Le barème se vérifie sur ses propres bornes.** La cotisation qui ouvre ces
points est due sur six cents SMIC horaires au moins (`D. 731-120`, 2°, et le
décret n° 2001-584 du 4 juillet 2001 avant lui) : la deuxième marche y donne
**22,5 points**, ce qui s'annonce 23. Au plafond, en 2025, la quatrième en donne **113,4**. Les deux nombres que
tout le monde cite sortent de la formule que personne ne cite.

Mieux : la construction du régime apparaît en résolvant le maximum. Pour une
carrière pleine au plafond, la pension proportionnelle vaut
`M × VP × 37,5 = PM − AVTS` — la valeur du point s'annule. La retraite
forfaitaire, qui vaut l'AVTS (`L. 732-24`), la complète donc exactement jusqu'à
la pension maximale du régime général. Un régime qu'on croyait bricolé est un
régime construit.

**Trois choses entrent donc dans le moteur en même temps.** Le barème lui-même,
sous la forme d'un `bareme_points: msa_proportionnelle` — une règle NOMMÉE dont
la formule vit dans le code, comme l'abattement Agirc-Arrco, parce qu'elle ne
s'écrit pas en colonnes. Le coefficient de durée `37,5 / durée requise`, qui
retire un huitième aux générations qui doivent 43 ans. Et la **part
forfaitaire**, que le moteur ne servait pas du tout : `mixte` y était un
synonyme de `points`, si bien que la retraite forfaitaire — 3 628,98 € au
1er janvier 2023 pour une carrière complète — n'existait nulle part.

Ce qui manquait vraiment n'était donc pas le barème mais **la valeur du point**,
que le code rural ne porte que depuis 2025 (`R. 732-66`, 4,589 €) ; le
communiqué de la MSA du 14 février 2023 et le COR en donnent 4,264 € pour 2023,
et les deux concordent à un dixième de pour cent une fois la revalorisation
appliquée. La fiche porte l'ancre de 2025 et le moteur la ramène sur les prix,
comme la loi le prescrit (`L. 161-23-1`).

**Ce que le modèle ne fait toujours pas.** L'AVTS elle-même n'est dans aucune
série du dépôt : le moteur lui substitue le montant de la retraite forfaitaire,
que la loi lui avait égalé jusqu'en 2014 avant de les laisser diverger. Le
maximum ressort à 115,1 points au lieu de 113,4 — un pour cent et demi de trop
sur la marche la plus haute, et rien ailleurs. Les années d'avant 1990 restent
au rendement instantané : `R. 732-70` n'ouvre le barème qu'« à compter du
1er janvier 1990 ».

### La réforme agricole de 2026 n'est pas modélisée, et il faut le dire

L'article 87 de la loi n° 2025-199 du 28 février 2025 de financement de la
sécurité sociale réécrit `L. 732-24` : pour les pensions prenant effet à compter
du **1er janvier 2026**, la retraite de base des non-salariés agricoles n'est
plus la somme d'un forfait et de points de carrière entière, mais un calcul sur
les **vingt-cinq meilleures années** — de revenus à partir de 2016, de points
avant, les revenus n'étant pas connus plus tôt. Un dispositif transitoire
recalcule en 2028 les pensions liquidées en 2026 et 2027, au bénéfice de
l'assuré.

Le modèle sert encore la formule d'avant. C'est une limite DATÉE, et la seule de
ce document qui se périme d'elle-même : elle porte sur les liquidations
postérieures à 2025, c'est-à-dire sur la moitié des simulations que le site
propose. La modéliser demande une mécanique que le régime agricole n'a jamais
eue — un salaire annuel moyen sur vingt-cinq années, greffé sur un compte en
points — et c'est pourquoi elle n'est pas faite ici plutôt que faite à moitié.

### Le taux de la première tranche a changé, et la phrase qui le portait mentait

Le récupérateur du recueil lisait les taux des deux tranches dans une phrase de
l'historique : « le taux de la première tranche est de 8,23 %, celui de la
seconde tranche est de 1,87 % ». Elle est exacte — mais elle décrit la réforme
DE 2015, et le script l'estampillait de l'année du recueil. Tant que le taux
n'a pas bougé, personne ne pouvait s'en apercevoir. Il a bougé : la réforme de
l'assiette des indépendants (article 18 de la loi n° 2023-1250 du 26 décembre
2023) porte T1 à **8,73 % dès l'exercice 2025**, et le barème en points suit —
**557 points** au plafond au lieu de 525, soit exactement le rapport des deux
taux, le prix d'achat d'un point ne bougeant pas.

**Une assiette minimale, que la fiche ne porte pas.** Le même dépouillement
donne la série complète de l'assiette minimale de la cotisation libérale
(`D. 642-4`) : 200 fois le SMIC horaire de 2004 à 2011, 5,25 % du plafond de
2012 à 2014, 7,70 % en 2015, 11,5 % de 2016 à 2023, 450 fois le SMIC horaire
depuis 2024. Elle ne mord que sous 5 400 € de revenu environ, et la porter
demanderait un plancher d'assiette INDÉPENDANT du repère en points — le seul
plancher que le moteur connaisse est celui qui se confond avec ce repère, et il
relèverait ici toute assiette au plafond entier. La série est donc écrite dans
la fiche, en attendant le mécanisme.

**Et le taux n'était pas faux que depuis 2025.** La même phrase servait pour
2004-2014, faute de série antérieure — la fiche le disait. `D. 642-3` la donne,
version par version : 8,6 % de 2004 à 2011, **8,63 % en 2012, 9,75 % en 2013,
10,1 % en 2014**, avant que la réforme de 2015 ne ramène le taux à 8,23 % en
élargissant la tranche de 0,85 plafond au plafond entier. La seconde tranche
suit le même chemin : 1,6 % jusqu'en 2012, 1,81 % en 2013, 1,87 % depuis. Le
compte notionnel d'un libéral était donc sous-alimenté de près d'un cinquième
sur l'année 2014, et d'un dixième en moyenne sur la décennie. Les points, eux,
ne bougent pas : ils ne dépendent pas du taux.

Le bon endroit pour l'année en cours est le TABLEAU DES COTISATIONS, que chaque
recueil donne sur trois exercices. Il passait pour illisible, et il l'était pour les montants :
les polices qui les portent n'exposent pas de table `ToUnicode`. Les taux et les
nombres de points, eux, se relisent. Les cinq recueils en ligne se recouvrent
sur quinze lectures, de 2020 à 2026, et concordent toutes — ce recouvrement est
désormais le contrôle du récupérateur, qui s'arrête si deux millésimes se
contredisent.

### La part patronale du public, et ce qu'on n'en sait pas

Les scénarios 4 et 5 ajoutent à la part salariale ce que verse l'employeur. Pour
un salarié du privé, la fiche du régime le porte — `part_salariale` en donne la
répartition, recoupée à OpenFisca année par année. Pour un agent public, elle
n'est dans aucune fiche : le modèle la lit dans
`legislation/contribution_employeur_public.csv`, qui couvre aujourd'hui neuf
régimes, mais aucun sur toute sa durée. Partout ailleurs, la part patronale est
**estimée** par l'effort d'un salarié du privé de la même année — jamais laissée
à zéro, qui ferait retomber les scénarios 4 et 5 sur les 2 et 3 sans le dire —
la fiabilité de l'année retombe à `estimee`, et le nombre d'années concernées
est affiché sous la simulation.

| Régime | Couvert | Découvert | Ce qui manque |
|---|---|---|---|
| Fonction publique d'État | 1995-2026 | 1930-1994 | rien à retrouver : l'État ne versait aucune cotisation, les pensions étaient payées sur crédits budgétaires, et le plus ancien chiffrage a posteriori — le jaune « pensions » — s'arrête à 1995 |
| CNRACL | 1948-2025 | 1945-1947 | le décret fondateur date du 19 septembre 1947 ; la convention « taux au 1er janvier » fait donc commencer la série en 1948 |
| SNCF | 1992-2018 | 1930-1991, 2019- | avant 1992, aucun texte de la base LEGI ne porte le taux ; après 2018, le décret cesse de chiffrer la composante T2, qui évolue par formule |
| RATP | 2007-2025 | 1930-2006 | rien à retrouver : avant l'adossement de 2006, la RATP payait les pensions sans qu'aucun texte fixe un taux, exactement comme l'État avant son compte d'affectation spéciale |
| IEG | 2005-2020 | 1946-2004, 2021- | avant 2005, EDF et GDF payaient les pensions directement ; après 2020, l'arrêté du 29 décembre 2021 remplace la fixation annuelle par une formule que la caisse applique sans la publier |
| Mines | 1984-2026 | 1930-1983 | la base LEGI ne garde aucune version de l'article 52 du décret de 1946 avant le 1er janvier 1984 |
| Opéra de Paris, Comédie-Française | 1992-2026 | 1930-1991 | même mur : les versions datées du décret qui fixe ces taux commencent au 1er juillet 1991 |
| FSPOEIE, marins, CRPCEN, Banque de France, port de Strasbourg, SEITA, chemins de fer secondaires | rien | tout | aucune série de taux employeur trouvée sous une forme exploitable. Pour ces sept régimes, la part patronale des scénarios 4 et 5 est celle d'un salarié du privé de la même année, et le modèle le dit |

**Ces taux sont ceux de l'employeur, non ceux de l'équilibre**, et c'est une
convention qui se défend mais qui se paie. Trois de ces régimes reçoivent aussi
de l'État une contribution que la série ne porte pas, parce qu'elle n'est pas
une cotisation d'employeur : les droits spécifiques de la RATP jusqu'à 45 000
agents, « une cotisation correspondant à 22 % des salaires » plus un complément
d'équilibre pour les mines — près de trois fois ce que verse l'exploitant —, la
subvention de l'Opéra. Pour la SNCF d'après 2007, la somme T1 + T2 laisse de
même dehors la subvention d'équilibre. La ligne de l'État est la seule exception
du tableau : son taux EST un taux d'équilibre. Un agent minier et un
fonctionnaire d'État ne sont donc pas mesurés à la même aune, et la différence
joue contre le mineur.

**Ce que les documents budgétaires ajoutent, et ce qu'ils n'ajoutent pas.** Les
projets annuels de performances annexés au PLF 2026 — programmes 195, 197 et
198 —, lus le 20 septembre 2026 et saisis dans
`regimes/pap_regimes_subventionnes.csv`, donnent ce taux d'équilibre que la
série laisse dehors : la subvention rapportée aux pensions servies vaut 0,60 à
0,64 à la SNCF et 0,58 à 0,62 à la RATP, chaque année de 2012 à 2023 ; pour les
marins, la subvention inscrite pour 2026 couvre les trois quarts de la dépense
de pensions prévue. Ils ne donnent en revanche aucun TAUX employeur : les
cotisations reçues de la RATP y sont en millions d'euros, salariés et
employeur confondus, et l'ENIM n'y a que sa subvention. Le tableau ci-dessus
ne bouge donc pas — il compte des séries de taux —, et la ligne « rien /
tout » des sept régimes non plus. Depuis le 1er janvier 2025, ces crédits ne
vont d'ailleurs plus aux régimes : la CNAV les équilibre en dernier ressort et
l'État la compense, net de la compensation démographique et des cotisations
que la fermeture a portées au régime général et à l'Agirc-Arrco, si bien que
les crédits 2026 ne se comparent pas à la subvention d'avant.

Trois conséquences à garder en tête.

**Plus une carrière publique est ancienne, moins le scénario 4 s'écarte du
scénario 2** — non parce que le financement d'alors ressemblait à celui du
privé, mais parce qu'on ne le connaît pas.

**Le repli n'est pas neutre, et il ne l'était pas dans le sens qu'on croyait.**
Là où la série manquait, le modèle prêtait au régime l'effort d'un salarié du
privé — de l'ordre de 27,75 % en 2026. Les taux lus sont tantôt plus élevés (la
RATP et ses 12,29 % de retenue portent le total à près de 32 %), tantôt bien
plus bas (les mines et leurs 7,75 %, l'Opéra et ses 9,56 %). Le repli
surestimait donc la part patronale des régimes à faible cotisation d'employeur
et la sous-estimait pour les régimes adossés : ce n'était ni un plancher ni un
plafond, mais un brouillage.

**Le scénario 5 ne voit presque jamais la contribution publique.** Il n'ouvre
son compte qu'à la bascule, et à compter de la bascule le régime unique remplace
tous les régimes : la part patronale y est celle du statut pivot privé, pas
celle d'un employeur public. Ce que le scénario 5 mesure après 2026 est donc la
répartition du régime unique, non le financement de la fonction publique — qui,
par construction, n'existe plus.

### Le scénario 6, et ce que sa garantie ne voit pas

Le scénario 6 — le scénario 4 jusqu'à la bascule, puis un taux unique de 18 %
pour tous, plus une garantie vieillesse individualisée, financée par l'impôt —
hérite des limites du scénario 4, part patronale inconnue du public comprise :
ce qui a été cotisé avant la bascule y est porté aux mêmes taux, et estimé là
où le 4 l'estime. Il en ajoute trois.

**La garantie est ouverte à 65 ans, et le modèle sert désormais ce qu'elle
doit à qui est parti plus tôt.** *Corrigé le 19 septembre 2026.* Avant 65 ans
on ne touche pas le minimum vieillesse ; à partir de 65 ans on le touche, même
si l'on a liquidé à 62. Le complément est donc CALCULÉ dans tous les cas, et il
n'entre dans la pension affichée que lorsqu'il est dû dès le départ ; la page
de simulation dit l'année où il s'ouvre, et le montant qu'il vaudra.

**Ce montant n'est pas celui du départ, et ce document a dit le contraire.**
Il affirmait l'égalité exacte entre le complément calculé à la liquidation et
celui servi trois ans plus tard, « le plancher et la pension étant tous deux
indexés sur les prix ». C'était vrai du modèle, qui figeait alors les pensions
en euros constants, et faux de la proposition : le plancher suit les prix comme
l'ASPA — article `L. 816-2`, qui renvoie au coefficient de `L. 161-25` —, la
pension notionnelle suit la masse salariale, et l'écart entre les deux se
referme de 0,7 point par an. Un départ à 62 ans voit donc sa pension gagner
deux points sur le plancher avant l'ouverture, et le complément diminuer
d'autant. Il est désormais calculé POUR l'année d'ouverture, et la cascade de
la page montre la ligne `f′` qui porte ce passage. La trajectoire de la
garantie y perd un neuvième : **0,80 % du PIB en 2026** au lieu de 0,91 %, et
**616 milliards** cumulés au lieu de 696.

**La garantie regarde l'ENSEMBLE de la pension obligatoire.** *Tranché le
19 septembre 2026 par le programme.* Les 18 % de répartition et les 5 %
capitalisés sont comparés ensemble au plancher : une allocation différentielle
compte les ressources, non leur origine. La rente du pilier réduit donc le
complément euro pour euro, et c'est ce qui coûte le moins à l'impôt. Le modèle
laissait jusque-là cette rente hors du calcul, faute que la question — de
droit, pas de modèle — ait été tranchée.

**Les montants sont des euros de 2026, déflatés par les prix.** 800 € et 250 €
sont ceux de la proposition ; une liquidation de 1995 les reçoit ramenés par
l'indice des prix, comme l'ASPA entre deux ancres de son barème. Ce n'est
qu'une convention : rien ne dit qu'une garantie créée en 2026 aurait été
indexée sur les prix depuis 1941.

**La masse de la trajectoire n'est plus vue par treize carrières : elle est
lue sur la distribution des pensions, depuis le 20 septembre 2026.** Une
allocation DIFFÉRENTIELLE ne se chiffre pas sur treize carrières, parce que
son coût est tout entier celui de la queue basse de la distribution, et que
treize carrières choisies pour couvrir les configurations du système n'en ont
pas. L'histoire de ce chiffre le montre : le 18 septembre 2026, le rapport de
masse de la garantie valait zéro de 2030 à 2070, les deux seuls cas types sous
le plancher liquidant avant 65 ans ; servir la garantie à 65 ans à qui est
parti plus tôt l'a porté à 0,80 % du PIB en 2026 et 0,20 % en 2070 — un ordre
de grandeur, pas une solution. Le barème est désormais appliqué, année par
année, à la distribution de l'EIR 2020 décrite plus bas, et la grille ne sert
plus qu'à dire de combien cette distribution BOUGE : la pension moyenne que la
garantie regarde — compte notionnel et rente du pilier capitalisé, à partir de
65 ans, revalorisés — rapportée à la pension moyenne du système actuel en
2020, l'une et l'autre par tête et en euros constants, lues sur la même grille
(`GarantieDistribution` dans `cout.py`, porté dans `moteur/js/cout.js`). Ce
facteur vaut 0,64 en 2020, parce qu'un compte rétroactif ne rend que ce qui a
été cotisé, et 1,26 en 2070, les pensions montant avec les salaires face à un
plancher indexé sur les prix. L'effectif suit les têtes de 65 ans et plus de la
grille, sur l'échelle des retraités de la DREES. La trajectoire porte
**1,30 % du PIB en 2026** (40 milliards d'euros de 2026, 6,8 millions de
bénéficiaires), décroissant à 0,86 % en 2070 (32 milliards, 5,1 millions),
soit 1 621 milliards constants cumulés sur la projection ; et le passé, où le
même déplacement est appliqué à rebours, en porte 3 757 depuis 1959.

Ce que cette méthode suppose, et qui reste une limite : la FORME de la
distribution est celle de 2020, déplacée sans être déformée, le passé comme
l'avenir ; le déplacement est proportionnel et uniforme, quand le scénario ne
déplace pas toutes les carrières du même rapport ; et les retraités de moins
de 65 ans, qui attendent la garantie, sont supposés répartis comme les autres.
Une seule méthode sur toute la série, plutôt qu'une falaise entre deux.

**Ce que la garantie n'est plus : une dépense du compte des cotisants.** Elle
est financée par l'impôt, et elle a donc quitté la masse contributive du
scénario 6, où elle était comptée jusqu'ici. C'est la symétrie de ce que la
recette fait déjà — la CSG de solidarité sort des ressources —, et sans elle la
garantie aurait été payée deux fois : une fois par les cotisations, une fois
par le contribuable.

La page porte aussi, à la date de l'enquête, le barème appliqué à la
distribution des pensions brutes de droit direct que publie l'échantillon
interrégimes de retraités de la DREES (fin 2020, tranches de cent euros), à
tous les retraités et non aux seuls 65 ans et plus. Quatre chiffres, parce que
deux questions et deux planchers :

| Assiette | Plancher | Sous le plancher | Bénéficiaires | Coût annuel, euros de 2026 |
|---|---|---|---|---|
| Pensions de 2020 | 800 € | 22,8 %, soit 3,8 M | 1,9 M | **9,2 Md €** |
| Pensions de 2020 | 1 050 € | 32,7 %, soit 5,5 M | 2,7 M | **16,1 Md €** |
| Pensions du scénario 6 en 2020 | 800 € | 42,7 %, soit 7,1 M | 3,6 M | **15,9 Md €** |
| Pensions du scénario 6 en 2020 | 1 050 € | 58,0 %, soit 9,7 M | 4,8 M | **28,5 Md €** |

*Deux colonnes, parce que deux populations : tous ceux que leur pension met
sous le plancher, et ceux qui réclament — un ayant droit sur deux, le recours
que la DREES mesure sur l'ASPA. Le coût est celui des seconds, comme partout
ailleurs sur la page. Les quatre lignes ont donc DOUBLÉ jusqu'au 20 septembre
2026, où le recours est entré dans le calcul ; les deux dernières disaient en
outre 35,9 et 64,2 milliards jusqu'à ce jour-là, la page déplaçant alors la
distribution du rapport contributif du scénario 6 MOINS celui de la garantie —
une soustraction juste tant que la garantie était dans la masse contributive et
fausse depuis qu'elle l'a quittée, la veille. Le facteur est désormais celui de
la trajectoire, 0,61 à la date de l'enquête.*

**Ce qu'elle remplace, et ce que l'impôt paierait en plus.** La garantie est
le SEUL plancher du scénario 6 : elle succède à l'ASPA, et le minimum
contributif, le minimum garanti de la fonction publique et la pension majorée
de référence disparaissent avec elle. En 2024, ces quatre minima coûtent
7,8 milliards — 4,94 de minimum vieillesse lus dans les comptes de la
protection sociale, 2,18 de minimum contributif et 0,72 de minimum garanti
calculés sur la grille, qui n'est pas une population et les sous-estime, et
une pension majorée de référence non chiffrée — contre 20,7 milliards de
garantie aux pensions du scénario 6 la même année, à un ayant droit sur deux :
**12,9 milliards de plus pour l'impôt**, borne haute puisque le total remplacé
est une borne basse. *Le 20 septembre 2026, le minimum garanti est sorti de ce
tableau au motif que les régimes de la fonction publique le servent dans leur
dépense de pensions, et il y a été remis le même jour : le programme le
supprime comme les trois autres, et le tableau montre le système actuel
plancher par plancher. Qui paie aujourd'hui ne change pas ce que le lecteur
veut savoir, qui est ce que l'ensemble coûte avant et après ; et le motif
valait d'ailleurs pour le minimum contributif, que les régimes servent aussi.*
Deux corrections se présentent, et une seule est dans le
tableau. Une personne seule éligible sur deux ne réclame pas l'ASPA — 321 200
personnes fin 2016, 790 millions non versés, 59 % des sommes servies (DREES,
*Les dossiers de la DREES* n° 97, mai 2022) —, et le programme retient depuis
le 20 septembre 2026 le même recours pour la garantie, un sur deux
(`taux_recours_garantie`), parce qu'une avance reprise sur la succession ne se
réclame pas plus que l'ASPA : la page compte les bénéficiaires et le coût
ainsi, et donne à côté tous ceux qui sont sous le plancher. L'autre correction
y est aussi, depuis le même jour : la garantie est une avance reprise sur la
succession dès le premier euro et avec intérêts, là où l'ASPA n'est récupérée
qu'au-delà d'un seuil d'actif net et a rendu 108,7 millions au Fonds de
solidarité vieillesse en 2024 (rapport d'activité 2024), deux pour cent de ce
qu'elle verse. La trajectoire suit ces avances par âge à compter de la
bascule, au taux réel lu sur la courbe des taux, les libère au décès avec la
mortalité du vingtile de niveau de vie où la pension moyenne des
bénéficiaires les place — le premier —, les deux sexes pesés comme ils le
sont sous le plancher, 75 % de femmes, dont la longévité fait durer une avance
20,8 ans, et les successions en rendent une part CALCULÉE sur le patrimoine
des ménages retraités selon leur revenu (COR, enquête Histoire de vie et
Patrimoine 2018, `donnees/patrimoine.py`) : 39 % au réglage par défaut, les plus petites
pensions rattachées au quart des ménages retraités le plus modeste (médiane
36 800 €), les autres à l'ensemble (médiane 190 200 €), et 1,21 avance par
succession — la règle reporte la reprise au décès du conjoint survivant, et
deux bénéficiaires qui vivent ensemble en laissent deux sur la même
succession, presque toujours celle de la femme (INSEE, recensement 2021, part
en couple par âge et par sexe, croisée avec la part de chaque sexe sous le
plancher, les pensions du couple étant supposées indépendantes — elles ne le
sont pas, et la corrélation rendrait ce nombre plus grand).

**Les trois règles qui protègent la reprise sont comptées depuis le
22 septembre 2026** (`cout._recouvrement`, `recouvrement` dans `cout.js`). La
couverture était l'espérance de `min(créance, patrimoine)` ; elle se calcule
désormais sur mille rangs de chaque distribution, parce que chaque règle ne
joue que sur une partie du patrimoine. *Le logement attend le conjoint
survivant* : 35 % des décès de bénéficiaires surviennent en couple (recensement
2021, âge par âge, sur les courbes de décès du premier vingtile), la créance
est alors prise sur ce qui n'est pas le logement et le reste attend
11 ans — ce que le survivant vit encore, 11,1 ans, l'écart d'âge entre
conjoints étant de 2,6 ans —, grossi de 25 % d'intérêts, sur le seul
logement. *Les donations de la fenêtre sont réintégrées* : 7,0 % des ménages
retraités les moins dotés et 15,8 % de l'ensemble ont déjà donné (COR,
document n° 7 du 16 décembre 2021, tableau 1). *L'assurance-vie est hors
succession*, et le calcul d'avant la comptait tout entière comme saisissable :
elle fait 10 % du patrimoine des ménages les moins dotés (Banque de France,
comptes distributionnels, 2023), et la règle n'en reprend que les primes
versées dans la même fenêtre que les donations. Cette fenêtre a été alignée le
même jour : la règle écrite ne reprenait que les primes versées après 65 ans,
ce qui laissait placer son épargne à 60 ans hors d'atteinte ; `L. 132-8` CASF
(LEGIARTI000031728913, en vigueur depuis le 30 décembre 2015), pour l'aide
sociale, ne reprend que les primes versées après 70 ans.

Ce que cela déplace, au réglage par défaut : la couverture reste à 39 %, dont
35 % rendus au décès et le reste par le logement des couples ; les reprises de
2070 passent de 7,8 à 8,0 milliards d'euros 2026, leur cumul de 2026 à 2070 de
243 à 239. Règle par règle, chacune seule contre le calcul d'avant : le report
du logement porte 2070 à 7,85 mais retire 8 milliards au cumul, parce qu'il
décale les reprises de onze ans pendant la montée en charge ; les donations
portent 2070 à 8,1 et le cumul à 252 ; l'assurance-vie hors succession ramène
2070 à 7,4, et sa règle le remonte à 7,6. Tout pèse peu parce que la
couverture est saturée : une avance libérée vaut 150 000 € en moyenne en 2070,
face à une médiane de 36 800 € pour le quart modeste. Les règles valent
surtout pour ce qu'elles ferment : sans celle des donations, que 30 % des
propriétaires donnent leur logement retirerait de l'ordre de 0,8 milliard par an à
l'horizon (calcul hors modèle du 22 septembre 2026, que le modèle ne refait
pas : il ne connaît pas de donation faite pour échapper à la reprise).

Six nombres de ce calcul sont des hypothèses sans source, et `Parametres` les
porte avec leur motif : la part du logement dans le patrimoine d'un
propriétaire (75 %), le patrimoine à partir duquel un ménage est propriétaire
(80 000 € de 2018, qui laisse 30 % de locataires parmi les ménages retraités
quand le COR en compte 30,5 %), ce qu'un ménage donateur a donné (60 000 € et
100 000 €), la part des donations que la règle atteint (85 % dans la fenêtre,
80 % connues de l'administration) et la part du capital d'assurance-vie que
les primes de la fenêtre représentent (60 %). Les faire varier ensemble de
bas en haut laisse les reprises de 2070 entre 7,5 et 9,1 milliards. Le report
suppose le logement pris sur la succession du survivant comme sur celle d'un
ménage, patrimoine constant en euros constants, et une seule durée de veuvage
pour tous : la distribution de ces durées ne changerait pas le régime
permanent, seulement la montée en charge.

**Le poids des deux sexes est celui de l'enquête, et il ne se devinait
pas.** Le dépôt ne porte aucun effectif de retraités par sexe : ni la pyramide
des âges de l'INSEE, qui ignore la retraite, ni les effectifs de la DREES, qui
ignorent le sexe. Le modèle prenait donc, jusqu'au 21 septembre 2026, la part
des femmes parmi les 65 ans et plus que ses courbes de survie donnent en
population stationnaire, 56,0 %. Ce poids était pourtant DANS le fichier :
l'EIR publie trois colonnes — les femmes, les hommes, l'ensemble —, et la
troisième est le mélange des deux premières. Il existe un poids, et un seul,
tel que `w·F + (1−w)·H` redonne l'ensemble ; les quarante-six tranches de 2020
le donnent toutes entre 0,52 et 0,53, l'écart étant celui de l'arrondi au
centième de point, et les moindres carrés le fixent à **52,8 %**. L'écart
comptait : à 56,0 %, recomposer les deux sexes donnait 58,99 % de retraités
sous le plancher majoré aux pensions du scénario 6, quand la colonne
« ensemble » — celle dont le COÛT est tiré — en donne 58,03 %. Le modèle
décrivait deux populations différentes dans le même calcul.
`donnees.distribution.part_femmes` lit ce poids sur le fichier et refuse un
fichier dont les trois colonnes ne se répondraient plus ;
`test_les_deux_sexes_recomposent_la_colonne_dont_le_cout_est_tire` tient le
raccord. Ce que cela déplace : la part des femmes parmi les bénéficiaires passe
de 68 à 66 %, la durée d'une avance de 20,5 à 20,4 ans, le nombre d'avances par
succession de 1,28 à 1,29, et la couverture ne bouge pas, 37 % des deux côtés.
**Le COÛT de la garantie ne dépend pas de ce poids** : il est lu directement
sur la colonne « ensemble ». Une réserve demeure, et elle va dans l'autre
sens : le poids lu est celui de TOUS les retraités de l'enquête, quand les
bénéficiaires ont 65 ans et plus. C'est la convention que le modèle applique
déjà à la FORME de la distribution — « les retraités de moins de 65 ans sont
supposés répartis comme les autres » —, et la tenir aussi sur le sexe est la
seule façon de ne pas mêler deux populations ; une distribution par sexe des
seuls 65 ans et plus ferait bouger les deux ensemble.

Le patrimoine des retraités selon leur PENSION n'est publié nulle part : c'est le
fichier individuel de l'enquête qui le donnerait, et il se commande, action
47. Le réglage `reprise` remplace la part calculée par un nombre. Au réglage
par défaut, en 2070 : 15,3 milliards versés, 7,7 repris, 7,6 nets ; de 2026 à
2070 : 729 versés, 243 repris, 486 nets. Deux choses que le calcul ne voit
toujours pas, et qui vont en sens inverse l'une de l'autre : les femmes sous
le plancher vivent souvent dans un ménage moins pauvre que leur pension — le
calcul le sait pour leur espérance de vie, non pour leur patrimoine —, et deux
concubins que le recensement compte en couple ne se succèdent pas l'un à
l'autre. La ligne « s'ajoute au système 4 » reste
brute ; les lignes « dont reprises » et « garantie nette » disent le reste
(action 47 de la feuille de route).

**Le plancher d'une population n'est pas celui d'une personne.** C'était la
plus grosse convention du chiffrage, et elle a tenu jusqu'au 21 septembre 2026 :
la trajectoire servait le plancher MAJORÉ — 1 050 €, celui de qui vit seul — à
la population entière, parce que l'enquête sur les pensions ne dit pas avec qui
l'on vit. Le recensement le dit, lui, âge par âge et par sexe, et le dépôt le
lisait DÉJÀ pour les reprises sur succession. Il le lit désormais ici aussi :
pesé sur les années vécues après 65 ans, **57,9 % des femmes vivent seules
contre 30,0 % des hommes**, et les deux planchers se mélangent dans cette
proportion, sexe par sexe. Les deux se composent — les femmes vivent seules
plus souvent ET tombent sous le plancher plus souvent —, si bien qu'un partage
global les manquerait.

| | Garantie 2024 | 2026, % du PIB | Cumul 2026-2070 |
|---|---|---|---|
| Plancher majoré pour tous *(jusqu'au 21 septembre 2026)* | 22,0 Md € | 0,74 % | 918 Md € |
| **Pesé par le recensement** | **17,4 Md €** | **0,58 %** | **729 Md €** |
| Plancher de base pour tous | 12,5 Md € | 0,42 % | 525 Md € |

La convention d'avant surestimait donc la garantie de **plus d'un cinquième**,
et ce n'était pas une prudence assumée : c'était une borne haute faute d'avoir
cherché la source. `situation_foyer` reste ce qu'il a toujours été pour une
CARRIÈRE — le simulateur demande la vôtre, et un individu a une situation — et
ne décide plus pour tous.

**La table qui pèse les années vécues est celle des BÉNÉFICIAIRES**, et ce
n'est pas un détail : qui vit seul dépend de l'âge, et combien d'années on
passe à chaque âge dépend de la mortalité. Les plus modestes meurent plus tôt,
pèsent donc moins les grands âges — ceux où l'on vit seul —, et le recensement
ne dit pas la même chose selon la table qui le pèse : 61,8 % de femmes seules
sous la table générale contre 57,9 % sous celle du premier vingtile, qui est
celui des bénéficiaires. Le vingtile est calculé une fois, dans le calage, sur
la pension moyenne de ceux que le plancher majoré concerne — le plus large des
deux —, et les REPRISES lisent la même : une population décrite deux fois
différemment dans le même calcul est exactement ce que ce module passe son
temps à corriger.

Ce que chaque ligne suppose. **Les deux planchers** sont donnés parce que
l'enquête dit la pension et non avec qui l'on vit : ils ENCADRENT le coût, la
garantie de base valant pour qui vit à deux et la majorée pour qui vit seul. **Les deux assiettes** ne répondent pas à la même question : à pensions
inchangées, c'est ce que la garantie coûterait en remplacement de l'ASPA, et ce
calcul-là ne doit rien au modèle ; aux pensions du scénario 6, toute la
distribution est déplacée du rapport que le modèle donne à la part contributive
de ce scénario — un déplacement *proportionnel et uniforme*, alors que le
scénario ne déplace pas toutes les carrières du même rapport. Les deux dernières
lignes sont donc un ordre de grandeur là où les deux premières sont un calcul.
**Deux conventions de lecture** enfin : les pensions d'une tranche de cent euros
sont supposées y être réparties uniformément, et la tranche ouverte du haut est
traitée comme une masse ponctuelle — elle est de toute façon au-dessus de tout
plancher. **Une réserve sans remède dans cette source** : le tableau de l'EIR
comprend la majoration pour trois enfants, que les scénarios notionnels ne
servent pas.

**Le déplacement uniforme est une borne basse, et le rapport est MESURÉ depuis
le 21 septembre 2026.** Le scénario 6 retire les droits non cotisés, et les
femmes en détiennent plus souvent : leurs pensions tombent plus que la moyenne.
Le dépôt le disait, et ne le chiffrait pas — faute d'une ventilation par sexe.

*Le chemin direct restait fermé* : un facteur par sexe se tire de la grille
comme le facteur d'ensemble s'en tire, et **un seul des treize cas types est
une femme**. Mais l'échantillon qui porte la distribution porte aussi, dans un
autre classeur du même millésime, les caractéristiques des retraités par sexe
(`data/reference/macro/caracteristiques_retraites.csv`). Deux d'entre elles
suffisent, et elles ne jouent pas dans le même sens.

| | Femmes | Hommes | Ce que cela fait au rapport |
|---|---|---|---|
| Durée validée **non cotisée** | 26,0 % | 10,9 % | 0,740 / 0,891 = **0,831** |
| Majoration pour enfants, en part de la pension | 2,60 % | 3,04 % | 0,974 / 0,970 = **1,005** |
| | | | **r = 0,834** |

**La durée non cotisée domine.** Un compte notionnel ne crédite que ce qui a
été cotisé : une année validée sans cotisation n'y porte RIEN, qu'elle vienne
de l'assurance vieillesse des parents au foyer, du chômage, de la maladie ou
d'une majoration de durée. Le capital est donc proportionnel à la part cotisée
de la carrière, et c'est le gros du déplacement différentiel.

**La majoration pour enfants joue à l'envers, et de peu.** Elle vaut dix pour
cent de la pension pour trois enfants, donc davantage d'euros à qui a la
pension la plus haute : 3,0 % de celle des hommes contre 2,6 % de celle des
femmes. La retirer coûte un peu plus aux hommes, et corrige le premier terme de
moins d'un demi-point. C'est le genre de terme qu'on aurait supposé dans le
mauvais sens, et c'est pourquoi il vaut mieux le lire.

**Ce que la mesure déplace.** Le modèle applique désormais `r = 0,834` au lieu
de 1 ; `Parametres.rapport_deplacement_sexe` le règle, et 1 restitue l'ancienne
convention. La garantie de 2024 passe de 20,7 à **22,0 milliards**, celle de
2026 de 0,69 à **0,74 % du PIB**, le versé de 2070 de 17,7 à **19,2
milliards**, le cumulé 2026-2070 de 849 à **918**. La part des femmes parmi les
bénéficiaires monte de 66 à **70 %**. Au barème appliqué à la distribution de
l'enquête, plancher majoré, le coût passe de 28,5 à **29,9 milliards** : la
convention uniforme sous-estimait de **5 %**.

**Ce que les minima apportent, mesuré à son tour, et pourquoi il reste
dehors.** C'était le troisième terme, nommé et non chiffré. Il l'est depuis le
21 septembre 2026, et il ne vient pas de la même étagère que les deux autres :
les EFFECTIFS de bénéficiaires sont lus sur l'enquête, la MASSE est prise au
modèle, qui l'isole carrière par carrière dans la cascade du scénario 1 —
2 912 millions en 2020, minimum contributif et minimum garanti réunis. Aucune
série ne la publie, et le dépôt dit lui-même que cette masse est une borne
basse : la grille n'est pas une population, et le minimum contributif est
réclamé par des carrières courtes qu'elle ne compte guère.

Le partage suppose alors une chose, et une seule : que le minimum apporte
autant à un bénéficiaire qu'à un autre, quel que soit son sexe. L'enquête
suggère que c'est prudent — sur le minimum vieillesse, qu'elle chiffre, les
hommes touchent DAVANTAGE, 18 € par mois en moyenne contre 13, parce qu'ils
tombent sous le plancher par carrière très courte.

| Qui l'on compte | Bénéficiaires | dont femmes | Par mois | Part de la pension, F / H | × r |
|---|---|---|---|---|---|
| Au minimum de leur régime principal | 4,33 M | 78 % | 56 € | 1,92 % / 0,39 % | **0,985** |
| Tous régimes confondus | 6,10 M | 67 % | 40 € | 1,65 % / 0,58 % | **0,989** |

Le terme va donc dans le même sens que les deux autres, et il mènerait `r` de
0,834 à 0,821-0,825. **Ce qu'il ferait au coût reste sous le pour cent** — 22,0
milliards de garantie en 2024 deviennent 22,1 ou 22,2, et la part de PIB de
2026 ne bouge pas au centième. C'est la raison de ne pas le retenir dans `r` :
un terme dont le montant est pris au modèle là où les deux autres sont lus, et
qui vaut moins d'un pour cent, coûterait plus en couplage — la garantie
dépendrait du chiffrage des avantages — qu'il ne rapporte en justesse.
`scripts/garantie_par_sexe.py` l'imprime, la page Coût l'affiche, et
`test_les_minima_pesent_sur_les_femmes_et_restent_sous_le_pour_cent` le tient.

**Le minimum vieillesse, lui, est hors de l'assiette**, et il fallait le
vérifier plutôt que le supposer : l'enquête le publie sur une ligne SÉPARÉE de
la pension de droit direct, qui est l'assiette de la distribution. Il n'est
donc pas dans les pensions que le barème déplace, et ne peut rien faire à `r`.
Une réserve qui se dissout par une lecture.

**Ce qui reste**, et c'est tout : le rapport suppose le salaire porté au compte
constant d'une année cotisée à l'autre, faute de quoi la part cotisée de la
carrière ne serait pas celle du capital.

`scripts/garantie_par_sexe.py` imprime la sensibilité entière, le rapport
mesuré à son rang ; `tests/test_garantie_par_sexe.py` tient les deux raccords :
la ligne mesurée redonne le coût de la page, et la ligne `r = 1` redonne ce que
le modèle donnait avant.

Et le modèle ne dit rien de l'impôt lui-même : il compte ce qui est versé,
jamais ce qui est prélevé.

### La décote des régimes spéciaux avait quatre ans d'avance

La réforme de 2008 donne aux régimes spéciaux la décote de la fonction publique.
Les fiches en avaient tiré un coefficient plat de 1,25 % par trimestre manquant à
partir de 2009 — et c'est la seule chose que le droit n'écrit nulle part. Le V
des décrets de réforme porte un calendrier, et il est écrit MOT POUR MOT À
L'IDENTIQUE dans les six textes concernés :

> « Le coefficient de minoration prévu au II ci-dessus n'est applicable qu'aux
> personnes remplissant les conditions définies à l'article 6 à compter du
> 1er juillet 2010. Pour les personnes remplissant les conditions définies à
> l'article 6 entre le 1er juillet 2010 et le 30 juin 2011 inclus, il est fixé
> par trimestre manquant à un dixième du taux prévu au premier alinéa du II
> ci-dessus. Pour les personnes remplissant les conditions définies audit
> article postérieurement au 30 juin 2011, ce taux augmente du même montant au
> 1er juillet de chaque année jusqu'à égaler le taux prévu au premier alinéa du
> II ci-dessus. L'âge auquel le coefficient de minoration s'annule correspond,
> pour la période comprise entre le 1er juillet 2010 et le 30 juin 2011 inclus, à
> l'âge de référence mentionné au 1° du II diminué de seize trimestres. Pour les
> périodes postérieures au 30 juin 2011, cette diminution est réduite de deux
> trimestres au 1er juillet de chaque année jusqu'au 30 juin 2013 inclus puis
> d'un trimestre au 1er juillet de chaque année jusqu'au 30 juin 2024 inclus. »

C'est le calendrier de la fonction publique — la loi du 21 août 2003, dix
huitièmes de point par an et seize trimestres qui s'effacent — DÉCALÉ DE QUATRE
ANS. Une passe sur la base LEGI, cherchant la phrase « un dixième du taux
prévu », rend exactement six textes : le statut national des IEG (décret n°
46-1541), la Comédie-Française (décret n° 68-960), l'Opéra (décret n° 68-382),
la SNCF (décret n° 2008-639), la RATP (décrets n° 2008-48 et n° 2008-637) et les
clercs de notaires (décret n° 90-1215). Ni les mines, ni les marins, ni le port
autonome de Strasbourg, ni la SEITA : ces régimes-là n'ont pas eu de décote.

**Ce que cela déplaçait.** Un cheminot parti en 2011 à cinquante-cinq ans avec
vingt trimestres manquants perdait un quart de sa pension dans le modèle ; le
droit lui en retirait un quarantième — 0,125 % par trimestre, non 1,25 %. Et la
caisse des clercs de notaires était branchée sur le barème de la fonction
publique, en avance de quatre ans sur le sien : 0,875 % par trimestre en 2012
au lieu de 0,375 %. Le barème est désormais une table à part,
`legislation/decote_regimes_speciaux.csv`, branchée par
`bareme_decote: regimes_speciaux` ; les marches tombant au 1er juillet et le
modèle lisant un millésime, chaque ligne porte la règle du 1er juillet de
l'année précédente — la lecture qui n'oppose jamais à l'assuré plus que le droit.

### L'Opéra de Paris : un âge pour tout le monde, et quarante-deux ans pour le ballet

La fiche de l'Opéra portait une période de 1930 à aujourd'hui, avec l'âge de
quarante ans et aucune décote. Quatre périodes la remplacent, et chacune corrige
quelque chose.

**L'âge de la danse a dépendu du sexe jusqu'en 2002.** L'article 6 du décret
n° 68-382 ouvrait le droit « à quarante ans d'âge, pour le personnel féminin de
la danse ; à quarante-cinq ans d'âge, pour le personnel masculin de la danse »,
puis cinquante ans pour le chant et les chœurs, cinquante-cinq pour les emplois à
fatigues exceptionnelles, soixante pour les autres. C'est en 2002 que le texte
devient « à quarante ans d'âge pour les artistes du ballet », sans distinction.
Le moteur ne porte qu'un âge par période : comme à la Comédie-Française, c'est
celui des hommes qui est retenu avant 2002, et une danseuse partie en 1970 se
voit donc opposer cinq ans de plus que son droit.

**Quarante-deux ans, et non quarante-cinq.** La réforme de 2008 donne à chaque
catégorie un âge de référence pour la décote — l'âge d'ouverture majoré de cinq
ans —, et y déroge pour deux d'entre elles : « toutefois, pour les artistes du
ballet, l'âge de référence est fixé à 42 ans et, pour les musiciens de
l'orchestre, les chefs de chant et les pianistes, il est fixé à 62 ans ». Un
danseur qui part à quarante ans se voit donc opposer huit trimestres de décote,
non vingt : le maximum du régime, pour lui, vaut deux ans. C'est le seul âge de
référence du modèle qui ne se déduise pas de l'âge d'ouverture, d'où le barème
`regimes_speciaux_age_fixe`, qui prend le coefficient de la table des régimes
spéciaux et garde l'âge d'annulation écrit dans la fiche.

**Cent soixante-douze trimestres depuis 2014.** L'article 14 fixait « cent
soixante » trimestres en 2008, évoluant « comme la durée des services et
bonifications exigée des fonctionnaires de l'État », puis « cent soixante-douze »
en toutes lettres depuis le 26 juin 2014. La fiche en portait 150 pour toute
l'histoire du régime : un danseur né en 1975 voyait sa pension proratisée sur
cent cinquante trimestres au lieu de cent soixante-douze.

**Ce que la fiche ne porte toujours pas.** Un seul âge d'ouverture par période, là
où l'article 6 en compte cinq depuis 2011 — quarante ans pour le ballet,
cinquante-sept pour les chœurs et les emplois à fatigues exceptionnelles,
soixante pour les musiciens, chefs de chant et pianistes accompagnateurs,
soixante-deux pour les autres. C'est l'âge du ballet qui est retenu, celui pour
lequel ce régime est connu et le plus bas du système français : un musicien de
l'orchestre se voit donc offrir une liquidation à quarante ans que son statut ne
lui ouvre qu'à soixante.

### La réforme agricole de 2026 est en vigueur, et elle n'est pas calculable

Le tableau des manques disait « la réforme du 28 février 2025 n'est pas
modélisée ». La lecture du code rural dans la base LEGI dit quelque chose de plus
précis, et de plus gênant.

**La loi est bien en vigueur.** L'article L. 732-24 a été entièrement réécrit au
1<sup>er</sup> janvier 2026 par la loi n° 2025-199 du 28 février 2025, et
l'article L. 732-24-1 — celui qui fixait l'objectif à la Nation depuis 2023 — a
été abrogé le même jour, son objet étant atteint. La pension « cumule » désormais
une part calculée sur les seuls revenus postérieurs à 2016 et une part reprenant
les droits d'avant 2016.

**Mais deux de ses trois paramètres n'existent pas.** Le texte les renvoie
ailleurs, mot pour mot : la part forfaitaire d'avant 2016 est « d'une part dont
le montant maximal attribué pour une durée minimale d'assurance **est prévu par
décret** » ; la part proportionnelle d'avant 2016 se calcule « en retenant un
nombre d'années sélectionnées **dans des conditions fixées par voie
réglementaire** » ; et son IV ajoute « les modalités d'application du présent
article sont définies par **décret en Conseil d'État** ».

Ce décret n'est pas dans la base. Un dépouillement de toute la législation
consolidée ne rend, pour le 1<sup>er</sup> janvier 2026, que des articles
LÉGISLATIFS — L. 732-21, L. 732-24, L. 732-35, L. 732-60 du code rural, et trois
articles du code de la sécurité sociale — et aucun article réglementaire nouveau.
Les articles R. 732-60, R. 732-63 et R. 732-66, qui décrivent le calcul en
points, courent toujours jusqu'à 2999.

**Ce que le modèle fait, et pourquoi c'est le moins faux.** Il sert la formule
d'avant — retraite forfaitaire plus retraite proportionnelle en points —, qui est
la seule dont les paramètres soient publiés, et dont la partie réglementaire est
toujours en vigueur. Inventer les deux paramètres manquants reviendrait à écrire
le décret à la place du Conseil d'État. C'est écrit dans les trois périodes
concernées de la fiche, et c'est la seule limite du dépôt qui tienne à un texte
que le Gouvernement n'a pas encore pris.

### Cent soixante-douze trimestres demandés aux assurés nés avant 1934

Le même balayage par génération, une fois la CAVIMAC corrigée, laissait un saut
de 53 % entre les générations 1933 et 1934 du ministre du culte. La cause n'est
pas dans une fiche : elle est dans une TABLE.

`legislation/duree_assurance_requise.csv` commence à la génération 1934, parce
que c'est là que commence le tableau de la loi du 22 juillet 1993. Une table par
génération ne répond pas en deçà de sa première ligne — et le moteur, faute de
réponse, retombait alors sur la durée écrite dans la fiche du régime, c'est-à-dire
celle d'aujourd'hui. Un assuré né en 1933 se voyait donc demander **172
trimestres**, et son cadet d'un an 151.

Le défaut touchait tout ce qui lit cette table : le régime général et les régimes
alignés dans leur période 1994-2003, la MSA, la CAVIMAC, et les dix
complémentaires libérales dont les fiches portent 172 trimestres. Toutes les
générations nées avant 1934 — celles qui ont liquidé avant 1999 — étaient
concernées.

La table porte désormais une ligne `1900,150` : la durée de la loi du 31 décembre
1971, celle que la réforme de 1993 relève **à partir de** la génération 1934.
Niveau `haute`, parce que c'est la lecture en creux d'un tableau qui nomme les
générations suivantes, non une ligne écrite. Ce qu'elle ne dit toujours pas : les
assurés qui ont liquidé avant 1972 devaient trente années, soit 120 trimestres —
une borne calendaire, que les périodes du régime général portent et qu'une table
par génération ne peut pas exprimer.

Les six autres tables par génération du dépôt — âge d'ouverture, coefficient de
minoration, durée de proratisation, années de salaire de référence — commencent
toutes à 1900. Celle-là était la seule à ne pas le faire.

**Et aucun témoin ne l'a vue**, parce que le balayage s'arrêtait à la génération
1935. C'est la seconde fois que ce diagnostic tombe ; le balayage a donc une
quatrième génération, née en 1925, et le fichier de témoins passe de 212 à 250
cas.

### Une surcote servie vingt-cinq ans avant sa création

Un second balayage, après celui des taux de remplacement : la même carrière
déplacée d'une génération à l'autre, de 1920 à 1980, et le rapport de la pension
au dernier salaire pour chacune. Ce que cette courbe montre, ce sont les SAUTS —
là où une année de naissance de plus change la pension de plus d'un dixième.

Le ministre du culte en avait un de 68 % entre les générations 1933 et 1934. La
cause : la fiche de la CAVIMAC portait `surcote_par_trimestre: 0,0125` sur toutes
ses périodes depuis 1979. Or ce régime reprend les règles du régime général — sa
propre note le dit pour les taux de cotisation, que R. 382-89 et R. 382-90
alignent sur ceux des salariés — et **le régime général n'a de surcote que depuis
la loi du 21 août 2003**, appliquée aux liquidations de 2004 : 0,75 % par
trimestre jusqu'en 2008, 1,25 % ensuite. Un ministre du culte parti en 1996 avec
plus que la durée requise voyait donc sa pension majorée de dix pour cent que
personne ne lui devait.

La même vérification, passée sur tout le catalogue, montre que le régime général
lui-même, la fonction publique, les régimes alignés et la MSA salariés ont la
bonne chronologie. Deux fiches ne l'avaient pas : la CAVIMAC, corrigée ici, et la
MSA non-salariés, dont la période ouverte en 2003 servait 1,25 % dès sa première
année — elle est scindée en trois pour porter la montée en charge. Restent quatre
complémentaires libérales — CARMF, CARPIMKO, CAVEC, CIPAV et la caisse des
notaires — dont la majoration pour âge est une règle PROPRE, fixée par leurs
statuts et non par la loi de 2003 : elles peuvent légitimement en avoir servi une
avant 2004, et le dépôt n'a pas de quoi le vérifier.

### Sept pour cent jusqu'en 2003 : le taux de retenue du fonctionnaire était faux depuis 1991

Trouvé par la bande, en cherchant à quel taux la SEITA cotisait : son article 108
renvoie, depuis 1995, « au taux de la retenue pour pension définie à l'article
L. 61 du code des pensions civiles et militaires de retraite ». Il fallait donc
lire L. 61 — et la base LEGI n'en garde que deux versions chiffrées, parce que
l'article cesse d'écrire un taux au 1er janvier 2006 et renvoie au décret :

> « Les agents visés à l'article L. 2 supportent une retenue de **8,9 %** sur les
> sommes payées à titre de traitement ou de solde. » (30 décembre 1989)
>
> « […] une retenue de **7,85 %** […] » (1er février 1991, jusqu'au 1er janvier
> 2006)

Les fiches de la fonction publique d'État, de la CNRACL et du fonds spécial des
ouvriers de l'État portaient 7 % jusqu'en 2003. C'est un huitième de cotisation
oublié pendant treize ans, plus l'année 1990 à 8,9 %. Le scénario 1 n'en dépend
pas — la pension du fonctionnaire ne se calcule pas sur ses cotisations — mais le
compte notionnel en dépend entièrement : le témoin du fonctionnaire né en 1935
gagne 6,2 % de pension notionnelle rétroactive, celui né en 1955 3,4 %.

### Six pour cent jusqu'en 1983, et une marche par an depuis 2011 : la retenue lue chez OpenFisca

La lecture de L. 61 avait ramené le 7 % de 2003 à 1989 ; elle n'avait pas
regardé plus haut. OpenFisca-France transcrit la retenue pour pension depuis
1925, datée loi par loi (`cotisations_secteur_public/retraite/pension/salarie`),
et le barème de la CNRACL depuis 1947 : **6 % jusqu'à la loi de finances pour
1984**, 7 % ensuite, 7,7 % en août 1986, 7,9 % en juillet 1987, 8,9 % en 1989,
7,85 % en février 1991 — puis, de 2011 à 2020, une marche par an de 8,12 % à
11,10 %. Les fiches de l'État, de la CNRACL et des ouvriers de l'État
portaient 7 % dès 1964 — dès 1945 pour la CNRACL — et 10,29 %, le taux de 2017,
sur toute la période 2011-2022 : un point de trop pendant vingt ans, deux de
trop en 2011, un de moins en 2020.

Le récupérateur `openfisca_cotisations.py` lit maintenant ces séries, avec la
cotisation de base des artisans et des commerçants depuis l'alignement de 1973,
leurs complémentaires, le RAFP et le régime de base des professions libérales ;
`verifier_donnees.py` les confronte aux fiches, période par période, comme il
le fait pour le régime général. Les fiches ont été alignées : une période par
taux pour la retenue de l'agent, et, pour la CANCAVA, l'ORGANIC et le RSI, la
moyenne des taux datés sur chaque période législative — 11,43 % de 1973 à 1982
là où la fiche portait 16,55 %, un chiffre de synthèse qui surcomptait de cinq
points la cotisation des années 1970. Le scénario 1 n'en dépend pas ; le compte
notionnel d'un fonctionnaire ou d'un artisan en dépend entièrement.

Ce que le contrôle signale encore, et pourquoi on le laisse : le taux 2025 de
la première tranche de la CNAVPL, 8,73 % chez le producteur, qu'OpenFisca n'a
pas encore. Deux écarts qu'il signalait sont refermés : la marche de 8,9 % de
la retenue des fonctionnaires, que la loi n° 89-18 fait bien partir du
1<sup>er</sup> janvier 1989 (voir plus bas), et la CANCAVA de 1973 à 1982, dont
la moyenne recouvre une montée de 8,75 % à 12,9 % que
`taux_cotisation_annuels.csv` porte désormais année par année.

### La SEITA partait à cinquante-cinq ans, et son décret dit soixante

Le régime des tabacs est fermé depuis 1981 et n'a jamais été réformé : ses
articles courent sans modification jusqu'à aujourd'hui. C'est justement ce qui
permet de les lire une fois pour toute l'histoire du régime — et trois d'entre
eux disent autre chose que la fiche.

**L'âge.** Article 110 : « les agents peuvent prétendre à pension dès qu'ils
atteignent l'âge de soixante ans. Toutefois, les agents féminins occupant un
emploi d'ouvrière (catégories A, B, C, D et E) peuvent prétendre à pension à
partir de l'âge de cinquante-cinq ans dès qu'ils réunissent un minimum de trente
années de services ». La fiche servait à tous l'âge des ouvrières.

**La majoration pour enfants.** Article 118 : « pour les titulaires ayant élevé
au moins trois enfants jusqu'à l'âge de seize ans, la pension est majorée de 10 %
pour les trois premiers enfants et de 5 % par enfant au-delà du troisième ». La
fiche ne la portait pas.

**Le taux de retenue.** Article 108 : 7,7 % au 1er janvier 1984, 7,9 % au
1er juillet 1987, 8,9 % au 30 décembre 1988, puis le taux de la fonction publique
depuis le 2 février 1995. La fiche en portait un seul, 7 %, pour quatre-vingt-dix
ans : le compte notionnel rétroactif de l'agent né en 1955 gagne 24 %.

Reste hors du modèle l'article 117, qui définit les émoluments de base comme
« une fraction du traitement statutaire LE PLUS ÉLEVÉ acquis par l'agent au cours
d'une durée consécutive de trois ans » : le moteur ne sait pas exprimer cette
règle et lui oppose celle de la fonction publique, proche et légèrement plus
favorable.

### Le navigant n'avait pas de décote, et son régime en a une depuis 2012

Trouvée en balayant les taux de remplacement de tous les statuts à six
générations : le personnel navigant ressortait à plus de cent pour cent du
dernier salaire, seul de la liste. Une partie de cet écart tient au cas type —
quarante-trois ans de carrière dans un régime dont les annuités plafonnent à
trente —, mais la lecture du code de l'aviation civile a montré autre chose : la
CRPN a une décote, et la fiche n'en portait aucune.

> « La pension est dite à taux plein si l'affilié réunit cumulativement […] 1°
> avoir atteint l'âge de cinquante-cinq ans ou justifier de trente annuités […]
> 2° la somme de l'âge et du nombre d'annuités […] est supérieure ou égale à 80.
> Lorsque l'affilié ne remplit pas les conditions de liquidation des droits à
> pension à taux plein, il est appliqué à la pension une décote égale à 5 % par
> année manquante. »
> — article R. 426-11 du code de l'aviation civile, rédaction du 1er janvier 2012

Depuis le 1er janvier 2022, la condition d'âge disparaît et seule la durée
compte. Cinq pour cent par année manquante, c'est 1,25 % par trimestre, et cette
décote **s'ajoute à la proportionnalité** : un navigant parti avec vingt-cinq
annuités touche 25/30 du taux plein, puis un quart de moins. Le modèle le fait
désormais — 41,6 % au lieu de 55,5 % pour ce cas, et 27,8 % pour vingt annuités,
où le plafond de quarante trimestres joue.

**Trois écarts, nommés dans la fiche.** Le droit prend le PLUS GRAND des deux
manques — âge et durée — quand l'affilié a moins de cinquante-cinq ans, quand le
moteur prend le plus petit : la fiche décote alors moins que le droit. L'âge
d'annulation retenu, soixante-cinq ans, est celui de l'article R. 426-12, qui
écarte la décote pour la pension prenant effet à la limite d'âge de vol. Et le
maximum de quarante trimestres n'est pas écrit dans le texte : il se déduit de ce
que la liquidation n'est pas ouverte avant vingt annuités et que le taux plein en
demande trente.

### L'avocat d'avant 2004 recevait cent pour cent de son revenu

Même forme d'erreur, trouvée en cherchant la précédente. La retraite de base des
avocats est FORFAITAIRE — 19 154 € par an au taux plein en 2026, quel que soit le
revenu —, et la fiche le disait pour la période ouverte en 2004 seulement. La
période 1948-2003 portait `salaire_reference: sans_objet` sans qu'aucun montant
ne prenne le relais : lue en annuités, elle servait la moyenne des revenus. Un
avocat né en 1935, liquidant en 2000, recevait 18 499 € — cent pour cent de son
revenu moyen, quand le régime sert à tous le même montant.

La période porte désormais le forfait, à la valeur de 2026 ramenée par l'indice
des prix, et le cas type perd 29 %. **C'est une convention, et elle est nommée :**
le montant de la retraite de base des avocats n'est pas dans le code — l'article
R. 723-43 y renvoie à une décision de l'assemblée générale de la caisse — et
aucune série historique n'en est publiée. Le report par les prix suppose que le
forfait les a suivis, ce qui est vrai depuis les années 2000 et l'est moins
avant.

### La pension du mineur ne dépend pas de son salaire, et le modèle la doublait

C'est la plus grosse erreur que cette campagne ait trouvée, et elle tenait à une
seule ligne de fiche : `type_calcul: annuites`, `taux_plein: 0.75`,
`salaire_reference: dernier_salaire`. Le régime minier ne calcule rien de tel.

> « Le montant annuel de la pension de vieillesse est proportionnel à la durée de
> service ; il est égal au produit du montant de pension pour un trimestre de
> services et du nombre de trimestres de services effectués. »
> — article 131 du décret n° 46-2769 du 27 novembre 1946

La pension du mineur est un **forfait par trimestre de service**, le même pour
l'abatteur et pour l'ingénieur. Le décret en porte la valeur, et la base LEGI en
garde quatre états :

| En vigueur | Valeur du trimestre | Article |
|---|---|---|
| 1er avril 1974 | 74,26 F (11,32 €) | art. 147 |
| 1er juillet 1992 | 382,08 F (58,25 €) | art. 131 |
| 1er janvier 2002 | 69,22 € | art. 131 |
| 1er avril 2013 | 82,83 € | art. 131 |

Trente ans de mine valent donc 9 940 € par an aujourd'hui, quarante ans
13 253 € — quand la fiche en servait 75 % du dernier salaire, soit le double.
Les trois cas types du balayage perdent de 43 % à 55 % de leur pension, et c'est
la correction qui les rapproche du droit.

**Deux contrôles internes.** Le premier vient du décret lui-même : l'article 147
fixe « 8 911,20 F pour […] trente années de service » et l'article 148 « 4 455,60
F pour 60 trimestres », soit exactement la moitié pour la moitié des trimestres,
et 8 911,20 / 120 = 74,26. Le second vient du modèle : la période 2001-2012,
ancrée sur la valeur de 2002 et portée par les prix, donne 79,18 € en 2010 ; la
valeur que le décret fixe au 1er avril 2013 est 82,83 €, soit 79,3 € ramenés à
2010. Deux ancres indépendantes à deux pour mille l'une de l'autre.

**Entre 1974 et 1992, la valeur est RECONSTITUÉE, et voici pourquoi.** Porter
celle de 1974 par l'indice des prix la laissait 32 % sous celle de 1992 : la
pension d'un mineur liquidant en 1991 bondissait de 47 % l'année suivante, ce qui
n'était certainement pas le droit. Le balayage par génération l'a signalé comme
le plus gros saut du catalogue. Ni les prix ni les salaires ne reproduisent la
hausse réelle — le forfait a été multiplié par 5,15 quand les prix l'étaient par
3,57 et les salaires par 4,20 —, et le décret n° 2002-800 dit pourquoi : il est
pris après un protocole « relatif aux mesures de revalorisation et de rattrapage
des avantages miniers du fait de leur **décrochage** par rapport aux pensions de
vieillesse du régime général ». Ce forfait n'a suivi aucun indice : il a décroché,
puis rattrapé. Entre deux points connus, la fiche interpole donc
géométriquement — 9,9 % l'an, une période par millésime —, ce qui est la chose
la moins fausse qu'on puisse dire, et ce qui est écrit dans chacune de ces
dix-huit périodes. Les revalorisations intermédiaires sont des arrêtés annuels,
que la version consolidée du décret ne garde pas et qu'un dépouillement du
*Journal officiel* n'a pas retrouvés. Avant 1974, la base ne porte aucune
version : la valeur de 1974 est reportée en arrière par les prix, et une
liquidation des années 1950 est incertaine dans les deux sens. Enfin l'âge de
cinquante ans que la fiche oppose est l'âge ANTICIPÉ, celui du fond — l'article
125 garantit la pension « aux affiliés âgés de cinquante-cinq ans au moins », et
l'abaissement se gagne « à raison d'un an par tranche de quatre années de service
au fond ». Le moteur ne sait pas où un mineur a travaillé, et lui donne l'âge du
fond.

### Le Journal officiel en une requête, et non plus en une demi-heure

Chaque passe par les bases de la DILA racontée plus haut a coûté la même
chose : le dump global du JORF, 1,67 Go, ou celui de LEGI, 1,1 Go, retéléchargé
et dépouillé en flux par un script écrit pour la question du jour. Mesuré
depuis une session de travail : 21 minutes de téléchargement à 1,3 Mo/s, puis
7 minutes de décompression et de filtre — pour un dump global que la DILA n'a
pas régénéré depuis le 13 juillet 2025. Quatorze scripts de `scripts/fetch/`
font ce trajet, chacun avec son propre filtre, et celui du plafond imprime
jusqu'à 12 000 caractères par texte retenu : 800 Ko pour une passe, qu'il
fallait lire pour y trouver trois lignes.

**Ce qui a changé.** `scripts/fetch/dila_index.py` lit le dump UNE fois — gardé
en cache sur disque —, puis les incréments quotidiens (cent à deux cents Ko
chacun, plus de sept cents depuis juillet 2025, qui portent tout ce que le
dump global ignore, dont l'arrêté du plafond 2026), et verse le tout dans une
base SQLite FTS5 : une ligne par texte et par article, avec identifiant,
dates, nature, titre et texte sans balises ; un incrément qui republie un
document le remplace, une liste de suppression le retire. La construction
complète a pris une heure et demie pour le JORF (421 160 documents gardés sur
3 978 789, 1,9 Go en SQLite, 650 Mo compressés) et une heure pour LEGI
(245 498 sur 1 894 969, 1,3 Go, 380 Mo compressés). La base se dépose sur la
release `index-dila` du dépôt par `--publier`, d'où `--recuperer` la rapatrie
en une minute (36 secondes mesurées pour LEGI). Il y faut un jeton ayant le
droit d'écrire les releases : celui d'une session Claude Code ne l'a pas —
GitHub répond que la création de releases n'est pas permise à ce type de
session, et refuse de même l'ajout d'un fichier à une release existante —,
celui d'un workflow GitHub Actions l'a. C'est donc le workflow
`.github/workflows/index-dila.yml` qui construit et publie, sur les machines
de GitHub : la première fois depuis le dump, puis chaque lundi par les seuls
incréments, en quelques minutes. `dila_cherche.py` l'interroge en syntaxe FTS5 —
phrases, `OR`, `NEAR`, filtres par années, nature et numéro d'article — et
rend, par document, une ligne d'identification et un extrait de quatorze mots
entre crochets ; le texte entier ne s'imprime qu'à la demande, et `--motif`
n'en imprime que les fenêtres utiles. Une recherche prend de deux à
soixante-quinze millisecondes.

**Ce que l'index ne contient pas, et qu'il faut savoir avant de conclure.**
Tout le JORF fait quatre millions de documents et 6,5 Go en SQLite : trop pour
être publié. La base ne garde que les documents dont le titre ou le texte
touche au champ social — retraite, pension, cotisation, Sécurité sociale,
plafond, SMIC, point d'indice, minima, régimes, sections professionnelles…,
le motif exact est inscrit dans sa table `meta` — soit un quart d'entre eux.
Ne rien y trouver ne dit rien du reste du Journal officiel.

**Depuis le 17 septembre 2026, la certification lit l'index aussi.** Les
scripts `jorf_*`, `dila_legi_*` et `sncf_contribution_employeur.py`
retéléchargeaient le dump global — celui de juillet 2025, que la DILA n'a
pas régénéré depuis —, et c'est ainsi que les âges légaux certifiés sont
restés ceux d'avant la suspension de la réforme. Chacun lit désormais
l'index par défaut, et son propre filtre, écrit pour le dump, est rejoué tel
quel sur un flux qui en reprend la forme (`dila_index.filtrer_index`) ;
`--dump` garde l'ancienne voie. Le fichier de sortie et le journal de
certification disent jusqu'à quel incrément l'index était à jour. Ce que la
relecture a rendu, à valeurs identiques partout ailleurs : la valeur du point
agricole de 2025, le décret des cotisations libérales pour 2026 — dont la
refonte de la CARPIMKO —, la contribution employeur de la CNRACL jusqu'en
2028, et les portes de carrière longue de 2004, 2011 et 2012 lues par
génération dans les versions abrogées de D. 351-1-1.

---

## 5. Ce que le modèle ne calcule pas, et pourquoi

Ce qui suit n'est pas une liste de manques mais un **périmètre**, et chaque
ligne dit ce qu'elle coûte et dans quel sens. Une limite qu'on sait mesurer
n'est plus une limite : c'est un paramètre connu du résultat.

- **La grille de cas types ne sait pas compter le coût d'un avantage non
  contributif, et le sens de l'erreur est connu : elle n'a pas d'enfants.** Un
  seul des treize cas types en a — `carriere_interrompue`, deux enfants —, si
  bien que la majoration de pension pour trois enfants et plus valait **zéro
  toutes les années de la série**, et que la surcote parentale vaut zéro pour
  la même raison. La grille est faite pour comparer des systèmes sur une même
  carrière, où les erreurs de niveau s'annulent au dénominateur ; le coût d'un
  avantage est un compte de POPULATION. C'est l'erreur déjà rencontrée sur la
  garantie vieillesse — les 93 milliards tirés des cas types étaient faux, le
  barème appliqué à la distribution DREES donne 18,4 milliards.

  **La limite tient toujours, mais elle ne mord plus sur le chiffre publié**,
  parce que le chiffre publié n'est plus calculé. Les avantages non contributifs
  valent 95,2 milliards en 2024, soit 22,3 % de la dépense, et **86 % de ce
  total est LU** : la réversion dans l'enquête de la DREES auprès des caisses,
  et sept autres lignes dans les sous-postes des Comptes de la protection
  sociale, dont la majoration pour enfants à 7,8 milliards — que le modèle
  chiffrait à zéro. Le COR chiffre l'ensemble des droits de solidarité à « de
  l'ordre d'un cinquième » : on y est. Ce que le modèle apporte n'est donc pas
  le chiffre mais la LISTE, et les 13,1 milliards qu'il calcule encore lui-même
  restent soumis à cette limite. Vingt-quatre dispositifs sur quarante-deux ne
  portent aucun chiffre, chacun avec sa raison écrite.

  **Une seconde limite, découverte en réparant la première : les deux mesures
  n'ont pas la même fenêtre.** Les sous-postes des comptes ne sont publiés que
  depuis 2020, la réversion depuis 2004, et le modèle calcule depuis 1959. Une
  ligne ne mélange donc jamais les deux périmètres — la règle a été posée après
  qu'un minimum vieillesse eut valu 0,02 milliard en 2019 par le modèle et 4,01
  en 2020 par les comptes, dans la même série. Le site porte en conséquence
  deux tracés qui ne s'additionnent pas : le NIVEAU sur cinq ans, la FORME sur
  soixante-six. Voir `docs/avantages_non_contributifs.md`.

- **Le diviseur est le même pour tout le monde, et il transfère à qui vit
  plus longtemps — le système actuel autant que les autres.** L'espérance de
  vie du §5 de `methodologie.md` est celle de la population générale. Les
  pensionnés civils de l'État vivent un an de plus à 65 ans, d'après leur
  propre régime ; les 5 % d'hommes les plus aisés vivent sept ans de plus à
  65 ans que les 5 % les plus modestes, d'après l'INSEE. Depuis le
  20 septembre 2026, les deux écarts sont MESURÉS
  (`scripts/mortalite_population.py`, action 14) — et, depuis le
  21 septembre 2026, le diviseur par vingtile de niveau de vie est le DÉFAUT
  du modèle, stock compris, sur tous les chiffres du site ;
  `population_conversion=None` rend la table commune, et les chiffres
  ci-dessous sont mesurés contre elle. Pour le fonctionnaire sédentaire né en 1975, la
  table de sa population lui donne 1,5 an de rente de plus que la table
  commune, soit 5,7 % de pension notionnelle à capital égal et 54 000 € sur
  la vie sous le système actuel, dont la pension ne bouge pas d'un euro parce
  qu'aucun diviseur ne l'a calculée. Par le revenu, chaque cas type rattaché
  au vingtile de niveau de vie où son salaire le place : le salarié au SMIC a
  3,0 ans de rente de moins que la table commune ne lui en compte et
  l'exploitant agricole 3,7 de moins, le cadre 2,7 de plus et le libéral 3,2
  de plus — 49 000 € retirés au premier, 173 000 € ajoutés au dernier, sur la
  vie et sous le système actuel. Le diviseur commun transfère donc des
  modestes vers les aisés, dans le sens qu'on craignait, puisque qui vit
  longtemps est aussi qui a le plus cotisé ; et ce n'est pas un défaut du
  notionnel, toute rente viagère à taux commun le porte, le droit en vigueur
  le premier. Ce que la mesure suppose est écrit avec elle : un rattachement
  par le salaire là où l'INSEE mesure un niveau de vie de ménage, un facteur
  constant dans le temps, une espérance de stock appliquée à des liquidants
  futurs, et une grille de cas types qui n'est pas une population. Ce que
  ce transfert coûte au régime se mesure aussi (`--deficit`) : un diviseur
  par vingtile baisserait la dépense des scénarios notionnels de 3,6 à
  4,3 %, quatre à cinq dixièmes de point de PIB, parce que les gros capitaux
  sont servis le plus longtemps. La page
  Coût l'applique depuis lors par les pensions de ses cas types, mais compte
  encore tout le monde à la mortalité générale : ce sous-compte déplace son
  rapport de masses de moins de 1 %, un dixième de point de PIB au plus en
  2070, et ne se corrigerait proprement qu'avec la distribution des pensions
  par niveau de vie.

- **La décote surpunit l'anticipation ordinaire et sous-punit l'extrême.**
  Mesuré en comparant ce que coûte une année d'anticipation sous le droit en
  vigueur et sous le coefficient de conversion notionnel, sur un fonctionnaire
  sédentaire de la génération 1965 : partir deux ans plus tôt laisse 81,7 % de
  la pension sous le droit actuel contre 84,0 % sous le notionnel — le droit est
  PLUS DUR de 2,3 points ; à cinq ans d'avance, plus dur de 6,4 points. Puis la
  décote bute sur son plafond de vingt trimestres et le rapport s'inverse : à
  huit ans d'avance le droit est plus doux de 1,5 point, à dix ans de 5,1, à
  douze ans de 7,6. Or l'anticipation extrême est exactement celle de la
  catégorie active, de la super-active, de la conduite SNCF et des militaires :
  le barème est le plus clément là où il devrait l'être le moins. Voir
  `docs/avantages_non_contributifs.md` §4 ter.

- **Une décote plafonnée ne sait pas dire qui part trop tôt, et le modèle en
  hérite.** L'article L. 14 borne la décote à vingt trimestres : un agent de
  catégorie active parti à 57 ans et un agent sédentaire parti le même jour
  butent tous deux sur le même plafond, et leurs pensions ne diffèrent que de
  825 € par an pour la génération 1960 — le chiffre de 868 € que cette page et
  le site portaient en dur avait dérivé sans que rien ne le dise, et il est
  désormais celui du modèle. Pour la génération 1965 l'écart tombe à 102 €, le
  classement abaissant par ailleurs la durée requise d'un trimestre. Mesurer la
  valeur d'un avantage d'ÂGE par l'écart de MONTANT à date de départ fixe donne
  donc un chiffre petit — 0,5 milliard en 2024 pour la catégorie active — et ce
  chiffre n'est pas faux, il est incomplet ; il est de surcroît désormais
  REFUSÉ sur les cas types dont le retrait du classement déplace la durée
  requise, le contrôle d'isolement de `avantages.py` n'acceptant pas un écart
  qui mêlerait les deux effets. Ce que l'avantage coûte, ce sont les annuités
  servies avant l'âge légal, que nulle décote ne rattrape. Elles valent **13,7 milliards en 2024**, dont 7,5 pour le
  classement, 2,4 pour les régimes spéciaux et 3,8 pour la carrière longue
  (`scripts/cout_avantages.py --duree`). Ce sont des annuités anticipées et non
  un surcoût net — partir tôt, c'est aussi cotiser moins et mourir plus tôt en
  moyenne ; c'est exactement l'arbitrage qu'un coefficient de conversion
  notionnel rend automatique et que le droit actuel ne rend nulle part.

- **Le pilotage, et non plus le solde.** Le modèle calcule des droits
  individuels ; il porte une pyramide des âges, qui lui dit ce que chaque
  système COÛTERAIT ; il porte depuis peu les RESSOURCES, et donc le solde et le
  **coefficient d'équilibre** de chaque système, année par année, de 2002 à
  2070. Ce qui lui manque encore est le cran suivant : APPLIQUER ce
  coefficient. Un système notionnel réel ne laisse pas dormir un excédent — il
  relève les pensions jusqu'à l'équilibre, ou les abaisse, par un fonds de
  réserve et un facteur commun à toutes les pensions de l'année. Le modèle
  calcule ce facteur et ne l'applique jamais : toutes les courbes de coût de la
  page **Coût** sont celles d'un système qui ne se pilote pas. Le facteur étant
  commun, l'appliquer déplacerait les niveaux sans toucher aux ÉCARTS ENTRE
  CARRIÈRES, qui sont l'objet du modèle — mais il déplacerait bel et bien les
  niveaux, et un coefficient de 1,62 en 2070 pour le scénario 3 ne se lit donc
  pas comme une économie de 38 % : il se lit comme la marge dont ce système
  disposerait pour servir davantage à prélèvement inchangé.

- **Les ressources ne sont pas celles du risque vieillesse, et ne peuvent pas
  l'être.** Les Comptes de la protection sociale, d'où vient toute la dépense du
  dépôt, NE VENTILENT PAS LEURS RESSOURCES PAR RISQUE : ils publient la dépense
  risque par risque et le financement de l'ensemble, maladie et famille
  comprises. Une « recette du risque vieillesse » n'a pas de définition
  comptable, les cotisations d'un régime polyvalent n'étant affectées à aucun
  risque. Le solde vient donc d'un autre compte et d'un autre périmètre : celui
  du COR — régimes légalement obligatoires, FSV compris, RAFP exclu —, dont on
  prend les DEUX colonnes, dépenses et ressources, pour ne pas soustraire deux
  périmètres. Les deux se recoupent à moins de trois dixièmes de point de PIB
  (13,86 % contre 13,59 % en 2024), ce qui vaut contrôle et non identité ; seul
  le RAPPORT des masses, qui est sans dimension, passe de l'une à l'autre. Ce
  compte vaut `haute` et jamais `certifiee` : le COR consolide des comptes
  produits par les régimes, c'est le critère 1 du manifeste des sources.

- **Les recettes réagissent sur deux points, et sur deux seulement.** Le
  premier est le droit (voir ci-dessous). Le second est le TAUX, et il ne
  concerne que le scénario 6 : il remplace tous les taux de cotisation par un
  seul, 18 %, parts salariale et patronale additionnées, et sa part cotisée des
  ressources est donc multipliée par le rapport de ce que ce taux prélève sur
  les carrières de la grille à ce que le droit en vigueur y prélève. Ce rapport
  vaut **0,64** une fois la bascule passée, c'est-à-dire un taux moyen de
  **28 %** aujourd'hui. Le contrôle externe est le meilleur dont cette page
  dispose : le COR publie, dans son rapport annuel, le taux de cotisation
  retraite d'un salarié non cadre du privé sous le plafond, parts salariale et
  employeur — 27,9 % en 2025 —, et le modèle le retrouve à trois dixièmes de
  point près sur une grille qui mêle à ce salarié des fonctionnaires, dont
  l'employeur verse 74,28 % du traitement, et des non-salariés, qui cotisent
  moins. Le scénario 6 passe ainsi d'un solde moyen de +3,75 % du PIB à
  +0,12 %, et son coefficient de 2070 de 1,53 à 1,10.

  Le calcul est tenu au niveau du SEUL rapport, comme celui des masses de
  pension, et il suppose trois choses. Que l'assiette ne bouge pas : un taux
  plus bas déforme l'offre de travail et la structure des rémunérations, et
  aucune élasticité n'est posée ici. Que les ressources non cotisées — le quart
  du total — sont reconduites telles quelles, faute que le programme dise ce
  qu'il en ferait ; c'est l'hypothèse la plus favorable au scénario. Et que le
  poids d'un cas type parmi les COTISANTS est celui de sa caisse dans le
  classeur par régime du COR (`cotisants.csv`, 2010-2070, millésime de juin
  2024), la fonction publique d'État y étant partagée entre civils et
  militaires à la clé du jaune budgétaire « Pensions », tenue constante.
  Jusqu'au 20 septembre 2026, c'étaient les RETRAITÉS de la caisse qui
  servaient des deux côtés, faute d'une série de cotisants ; cette
  approximation surreprésentait les régimes qui s'éteignent, dont les taux sont
  parmi les plus élevés, et poussait le rapport vers le bas — 0,61, soit un
  taux implicite de 29,5 %, contre 27,9 % chez le COR. Les cotisants le
  ramènent à 0,64 et 28 %, et rendent 0,28 point de solde moyen au scénario 6
  sous la variante `rapport` ; sous la convention `assiette`, celle de la page,
  ils ne déplacent rien.

  **Une réserve de sens opposé, qui ne vaut QUE pour la variante
  `rapport`.** Ce rapport compare des taux qui ACQUIÈRENT des droits, et ce
  n'est pas tout ce qui rentre : la contribution d'équilibre général et la
  contribution d'équilibre technique de l'Agirc-Arrco n'ouvrent aucun droit et
  sont pourtant encaissées. Sous le plafond, la première seule s'applique, à
  2,15 % : et c'est exactement ce qui manque au modèle, dont le taux de 25,83 %
  plus ces 2,15 donnent 27,98 quand le COR publie 27,89 pour le même salarié.
  La seconde, 0,35 %, n'est due que par ceux dont la rémunération dépasse le
  plafond. Les compter abaisserait le rapport, donc la recette qu'il prête au
  scénario 6.

  **La convention affichée, elle, n'a pas cette réserve, et elle supprime ces
  deux contributions sans qu'on ait à le demander.** Son dénominateur est le
  taux de prélèvement OBSERVÉ — les ressources du COR rapportées à l'assiette,
  32,8 % —, qui compte tout ce qui rentre, contributions d'équilibre
  comprises. Et son numérateur est un taux unique de 18 % qui remplace TOUTES
  les cotisations : sous le scénario 6, il n'y a plus ni contribution
  d'équilibre général, ni contribution d'équilibre technique, ni taux d'appel,
  ni tranche. Ce que le modèle ne crédite pas au compte, le scénario ne
  l'encaisse pas davantage — la symétrie est complète, et elle est obtenue par
  construction plutôt que par une correction.

  **Et une fourchette, mesurée le 19 septembre 2026, qui est plus large que
  tout le reste de cette page.** Le rapport compare des taux LÉGAUX, puis il est
  appliqué aux ressources OBSERVÉES : cela revient à prêter au taux de 18 % la
  même déperdition qu'au système actuel. Or cette déperdition est connue. Sur
  l'assiette des revenus d'activité — 1 249 Md€ en 2024, soit 42,6 % du PIB,
  certifiée dans `assiette_activite.csv` et établie par deux routes
  indépendantes qui s'écartent de 3,9 % : les salaires et traitements bruts de
  l'INSEE plus le revenu mixte des ménages d'un côté, l'inversion du
  tableau 2.11 du COR de l'autre — le système encaisse 32,4
  points de ressources, dont 24,9 de cotisations, là où le taux légal d'un
  salarié type est de 28 à 29 %. Les quatre points d'écart ont deux causes, et
  le dépôt ne sait pas encore les départager. La première est l'ALLÈGEMENT
  GÉNÉRAL, décrit ci-dessous : l'employeur ne verse pas le taux légal, et ce
  que la retraite y perd lui revient par une voie que le dépôt n'a pas
  établie — **pas par ses 4,6 points d'impôts et taxes affectés**, où cette
  ligne l'a longtemps logé à tort ; le compte de la CNAV ne porte aucune ligne
  de TVA, et c'est par la TVA que l'État compense. La seconde est la COMPOSITION de la
  grille : ses cas types sont pondérés par les retraités de leur caisse, ce qui
  surreprésente la fonction publique et les régimes spéciaux, dont les taux
  sont les plus élevés, et gonfle donc le taux légal moyen qu'on lui fait
  dire. C'est le point 3 du volet A qui refermerait celle-là. Le modèle fait donc rentrer **15,5 % de l'assiette
  là où la proposition en affiche 18**. Trois lectures se défendent, et elles
  encadrent l'affichage : à exonérations inchangées, ce qui est affiché, 22,94
  points d'assiette ; 18 % prélevés à plat sans exonération et impôts affectés
  conservés, 25,48 ; 18 % à plat et suppression des impôts qui compensaient ces
  exonérations, 20,92. De 64 % à 79 % des ressources d'aujourd'hui, le chiffre
  affiché étant à 71 %. En solde moyen, cela fait environ un point de PIB de
  part et d'autre. Le départage n'appartient pas au modèle : c'est une
  décision de programme.

  **CE QU'EST L'ALLÈGEMENT GÉNÉRAL, ET CE QU'IL PREND À LA RETRAITE.** Lu
  dans l'article L. 241-13 du code de la sécurité sociale, version en vigueur
  du 1<sup>er</sup> janvier 2026 (LEGIARTI000053280526, issue de la loi
  n° 2025-199 du 28 février 2025 et de la loi n° 2025-1403 du 30 décembre
  2025), et dans l'article D. 241-7 qui le chiffre (LEGIARTI000054252241,
  décret n° 2026-509 du 12 juin 2026). Ce n'est pas une exonération de
  cotisation retraite : c'est une réduction UNIQUE, dégressive, calculée sur un
  périmètre de huit prélèvements patronaux, puis répartie entre les caisses au
  prorata de leurs taux.

  Le périmètre, dans l'ordre du I de l'article : les cotisations patronales
  d'assurances sociales — maladie, maternité, invalidité, décès et
  **vieillesse** — et d'allocations familiales ; les cotisations
  accidents du travail, à hauteur du seul taux fixé par arrêté ; la
  contribution au Fonds national d'aide au logement ; **les cotisations
  patronales de retraite complémentaire légalement obligatoire**, c'est-à-dire
  l'Agirc-Arrco ; la contribution de solidarité pour l'autonomie ; et les
  contributions patronales d'assurance chômage.

  Le barème. La réduction ne vaut que pour les rémunérations INFÉRIEURES à
  trois fois le SMIC — c'était 1,6 SMIC avant que la réforme de 2025-2026 ne
  fonde en un seul dispositif la réduction générale et les deux « bandeaux »
  maladie et famille. Son coefficient vaut, au plus,
  `Tmin + Tdelta` = **39,81 %** de la rémunération brute, ou 40,21 % selon le
  taux de FNAL dû par l'employeur : c'est la somme des taux du périmètre, et
  c'est donc au niveau du SMIC que la quasi-totalité des cotisations patronales
  disparaît. Il décroît ensuite selon une puissance 1,75 du rapport au SMIC,
  jusqu'à un plancher `Tmin` de 2 % atteint à trois SMIC.

  Ce que la retraite y perd. Les cotisations patronales de vieillesse de base
  valent 10,66 % de la rémunération en 2026 (15,45 % plafonné et 2,51 %
  déplafonné, dont le dépôt certifie les parts salariales), et la part
  patronale de l'Agirc-Arrco sous le plafond 4,72 % : **15,38 %** de
  rémunération, soit **38 % du périmètre de la réduction**. En y ajoutant les
  deux contributions d'équilibre de l'Agirc-Arrco, que le dépôt ne porte pas
  (voir la réserve ci-dessus), on approche 42 %. **Deux euros sur cinq de tout
  allègement général sont donc de l'argent de retraite**, et ce n'est pas une
  déduction : le VII de l'article L. 241-13 et le VI de l'article D. 241-7
  disent que le montant de la réduction s'impute sur les cotisations déclarées
  aux Urssaf ET sur celles déclarées aux institutions de retraite
  complémentaire, au prorata de leurs taux dans le coefficient maximal.

  **LA CONVENTION DU PROGRAMME, ET CE QU'ELLE COÛTE À LA PROPOSITION.** Le
  19 septembre 2026, le Parti libéral français a tranché la question que la
  fourchette ci-dessus laissait ouverte, et il l'a tranchée contre lui-même.
  Sa position tient en deux phrases. Les employeurs versent la cotisation
  ENTIÈRE ; l'État leur rembourse ensuite l'allègement par l'impôt, et ce
  remboursement est une aide à l'activité économique, non une recette de
  retraite — pas plus que le minimum vieillesse n'est une dépense de
  répartition. Un système qui n'exonère personne n'a donc rien à se faire
  compenser : il encaisse son taux plein, et ne reçoit aucun impôt affecté.

  Le modèle sait calculer les deux. `convention_recette="assiette"` applique
  les 18 % à l'assiette mesurée et retire les impôts et taxes affectés ;
  `"rapport"` est l'ancienne, qui multipliait la part cotisée des ressources
  observées par un rapport de taux légaux. L'écart n'est pas un détail :

  | | Solde moyen 2026-2070 | Coefficient 2040 | Équilibre atteint |
  |---|---|---|---|
  | Scénario 6, convention `assiette` (affichée) | **−2,16 % du PIB** | **0,76** | jamais |
  | Scénario 6, convention `rapport` | −1,47 % | 0,82 | 2026 |
  | Système actuel | −1,13 % | — | jamais |

  Deux effets de sens contraire séparent ces deux lignes, et il faut les
  compter séparément. Le taux plein rapporte PLUS que le rapport de taux
  légaux ne le disait — 18 % d'assiette au lieu de 15,5, soit deux points et
  demi d'assiette gagnés. Mais la convention du programme ne fait pas que poser
  un taux : elle RETIRE aussi les trois postes qui n'acquièrent de droits à
  personne, et ce second effet l'emporte largement sur le premier. **Sous sa
  propre convention, la proposition est donc plus déficitaire que le système
  qu'elle remplace**, d'un demi-point de PIB en moyenne, là où l'ancienne la
  donnait au-dessus de lui. C'est le chiffre d'un système qui ne vit que de ses
  cotisations, et c'est celui que le dépôt affiche.

  *Cette ligne a changé deux fois, et les deux mouvements valent d'être dits.*
  Elle a d'abord été calculée à −1,28 %, en retirant tout le poste des impôts
  et taxes affectés au motif qu'il compensait les allègements. Il ne les
  compense pas — voir ci-dessous —, et cette raison-là est tombée : le poste a
  été rendu au scénario 6, qui est remonté à +0,12 %. Il en est ressorti pour
  de bon le soir du 19 septembre 2026, **par l'argument des 18 % et non par
  celui des allègements** : un compte notionnel ne crédite que ce qui est assis
  sur un revenu d'activité. Le poste est donc sorti EN ENTIER, une fois, et
  pour une raison qui tient.

  **CE QUE CE POSTE CONTIENT VRAIMENT, ET IL NE CONTIENT PAS CE QU'ON
  CROYAIT.** Lu le 19 septembre 2026 dans le rapport à la Commission des
  comptes de la Sécurité sociale d'octobre 2025, compte de la CNAV et compte
  du Fonds de solidarité vieillesse. Deux choses en sortent, et la première
  démolit l'argument par lequel on avait commencé.

  *La compensation des allègements n'est pas dans ce poste.* Le compte de la
  CNAV ne porte AUCUNE ligne de TVA, et c'est par la TVA que l'État compense
  les allègements généraux — elle en ferait 20 % des produits nets de la
  branche MALADIE en 2025. Ce que la retraite perd à l'allègement lui revient
  donc par une autre voie que ses impôts affectés, probablement par la
  répartition des ressources entre branches, et retirer ce poste au nom de la
  compensation serait retirer la mauvaise somme pour la bonne raison.

  *Ce que le poste porte, en revanche, est de la CSG de solidarité.* Les
  impôts et taxes affectés au système de retraite valent 57,1 Md€ en 2024, et
  **21,7 d'entre eux — 38 % — sont les ressources du Fonds de solidarité
  vieillesse**, c'est-à-dire de la CSG. Ce fonds ne sert qu'à deux choses : il
  prend en charge des cotisations pour des périodes non travaillées — 15,7 Md€
  en 2024, dont 13,0 au titre du chômage et 2,4 au titre de la maladie — et il
  paie le minimum vieillesse, 4,2 Md€. **Aucun scénario notionnel ne sert l'un
  ni l'autre** : ils ne portent rien au compte pendant une année de chômage, et
  la garantie vieillesse qui remplace le minimum vieillesse est financée à
  part, par l'impôt, hors du compte des cotisants. C'est mot pour mot la règle
  que le dépôt applique déjà à la CNAF et à l'Unédic — LA RECETTE SUIT LE
  DROIT —, et le Fonds de solidarité vieillesse y échappait parce que sa
  recette entre dans les comptes sous un autre nom. Le reste du poste — taxe
  sur les salaires, forfait social, contribution sociale de solidarité des
  sociétés, et les taxes des régimes agricoles — finance des pensions
  ordinaires, et rien ne justifie de l'ôter.

  *Ce que cela donne, et c'est fait.* Le fonds est entré dans le retrait le
  19 septembre 2026, avec sa série certifiée, à côté de la branche famille et
  de l'assurance chômage : ce qu'il VERSE — 15,2 Md€ de cotisations prises en
  charge et 4,3 de minimum vieillesse en 2024 — est retiré des ressources des
  cinq scénarios notionnels. Le retrait total passe d'un demi-point de PIB à
  **1,17 %**, et coûte 0,64 point de solde moyen à chacun d'eux.

  *Et le poste entier est sorti du scénario 6 le soir même.* Décision du Parti
  libéral, 19 septembre 2026, prise APRÈS la lecture ci-dessus et contre
  l'argument qu'elle démolit : ce n'est pas parce qu'il compenserait les
  allègements que ce poste s'en va, c'est parce qu'un impôt affecté n'ouvre de
  droit à personne. C'est l'argument qui vaut déjà pour les 18 % : un compte
  notionnel ne crédite que ce qui est assis sur un revenu d'activité. Les
  57,1 Md€ ne sont donc pas reconduits, et le scénario 6 rejoint sur ce point
  les deux autres postes sortis le même jour, la contribution d'équilibre de
  l'État et les subventions aux régimes en extinction.

  **Il fallait ne le retirer qu'une fois.** La CSG du fonds est DANS ce poste
  et son versement est DANS le retrait : sortir le poste en entier sans
  toucher au retrait aurait fait sortir la même somme deux fois. Le retrait du
  scénario 6 rend donc au compte ce que le fonds verse — 19,6 des 57,1 Md€ de
  2024 —, et ne retire plus que la branche famille et l'assurance chômage,
  dont la recette passe, elle, par le poste « transferts », qui reste. Les
  quatre autres scénarios notionnels, qui encaissent toujours les impôts
  affectés, gardent le retrait entier. C'est `retrait_par_impot` dans
  `cout.py`, et deux tests le tiennent.

  *Ce que la sortie coûte* : **1,395 point de solde moyen**. Sur 2026-2070, le
  scénario 6 passe de −0,76 % du PIB, poste reconduit, à **−2,16 %**, contre
  −1,13 % pour le système actuel : il est désormais plus déficitaire que lui
  dans 38 des 45 années, et ne revient à l'équilibre sur aucune. Son
  coefficient d'équilibre de 2040 — ce que le système peut servir rapporté à ce
  qu'il promet — descend de 0,90 à **0,76**.

  *Et ce coût est le seul chiffre de ce paragraphe qui n'ait jamais bougé.* Les
  NIVEAUX, eux, ont changé deux fois depuis la décision, chaque fois pour une
  raison qui n'a rien à voir avec l'impôt :

  | Mesuré le | Poste reconduit | Poste sorti | Coût |
  |---|---|---|---|
  | 19 septembre au soir, à la décision | −1,12 % | −2,51 % | 1,395 |
  | après que la réversion eut quitté les cinq scénarios notionnels | −0,28 % | −1,67 % | 1,395 |
  | après que le profil de carrière fut lu chez l'INSEE | −0,76 % | −2,16 % | 1,395 |

  Trois mesures, trois niveaux, un seul coût. C'est ce qu'on attend d'une
  grandeur qui est une PART des ressources : elle ne dépend pas de ce que les
  pensions coûtent. Que la table ci-dessus existe est aussi un aveu — ces
  niveaux sont restés faux dans ce fichier entre chaque déplacement du modèle
  et la passe qui l'a rattrapé, et c'est la faute que ce dépôt commet le plus
  souvent. Les
  trois décisions du 19 septembre, prises ensemble, retirent au scénario 6 les
  27 % de ressources qui n'acquièrent de droits à personne, et le chiffre qui
  reste est celui d'un système qui ne vit que de ses cotisations.

  *Une date à retenir pour cette série.* Le Fonds de solidarité vieillesse est
  SUPPRIMÉ au 1er janvier 2026 par l'article 24 de la loi de financement de la
  sécurité sociale pour 2025 ; ses missions et son financement passent à la
  CNAV, dont le compte porte depuis lors la CSG directement. La série devra
  donc raccorder deux périmètres, comme elle le fait déjà pour les caisses que
  la DREES renumérote.

  **Ce que la page affiche.** La convention du programme, depuis le
  19 septembre 2026. L'autre reste calculable — `convention_recette="rapport"`
  —, comme `ponderation="egale"` garde l'ancienne pondération des cas types :
  on ne discute pas d'une convention qu'on ne sait pas chiffrer.

  Les réserves financières des régimes, que le COR chiffre à part, ne sont
  toujours pas comptées : le solde dit le flux, jamais le stock.

  Une part de ces recettes est désormais NOMMÉE, et c'est la moins défendable :
  le poste « transferts d'organismes extérieurs » du COR contient ce que la
  branche famille verse pour l'assurance vieillesse des parents au foyer et les
  majorations pour enfants — 10,9 milliards en 2024 — et ce que l'Unédic verse
  pour les points de retraite complémentaire des chômeurs — 3,9 milliards. Les
  scénarios notionnels suppriment les premiers droits et ne portent rien au
  compte pendant une année de chômage ; ils comptent pourtant ces recettes,
  0,50 % du PIB et 3,7 % des ressources en 2024 — auxquels s'ajoute depuis le
  19 septembre 2026 le fonds de solidarité vieillesse, 0,67 point de plus. La
  série
  `transferts_retraite.csv` les lit chez celui qui paie, dans les rapports à
  la Commission des comptes de la Sécurité sociale, de 2013 à 2024 (l'Unédic)
  ou 2025 (la CNAF) ; les rapports d'avant 2013 sont chiffrés ou compressés
  d'une façon que le lecteur PDF du dépôt n'ouvre pas. Le coefficient
  d'équilibre des scénarios notionnels les RETIRE : année par année là où on
  les connaît, à part constante des ressources avant 2013 et sur tout
  l'horizon projeté — personne ne projette ce que la CNAF versera en 2070, et
  une part constante est l'hypothèse qui n'en ajoute aucune autre. Cela
  ramène le scénario 3 en 2070 de 1,94 à 1,87, le scénario 5 de 1,17 à 1,13,
  et met les deux en déficit dès 2025, où ils servent encore les pensions du
  système actuel. Le système actuel encaisse tout et garde le solde du COR.
  Le coefficient n'est toujours pas appliqué, et ce que la branche famille
  ferait de ce qu'elle cesserait de verser est une décision de programme, pas
  un résultat du modèle. Depuis le 18 septembre 2026, ce retrait n'est plus la
  seule réaction des recettes : voir le point précédent.

- **L'horizon de la projection.** La dépense observée s'arrête à 2024,
  dernière année publiée par la DREES ; la trajectoire projetée s'arrête à
  2070, dernière année des projections de population de l'INSEE. Ni l'une ni
  l'autre de ces bornes n'est une décision du dépôt : ce sont celles des
  sources. Au-delà de 2070, le dépôt ne dit rien, et le COR non plus.

- **Les comportements.** Les âges de liquidation sont ceux que l'utilisateur
  déclare. Or une réforme qui pénalise fortement les départs précoces conduit à
  les décaler. Le sens du biais est connu : les écarts affichés sont des effets
  **à comportement inchangé**, et ils surestiment donc la perte réelle — un
  assuré qui, dans un système notionnel, travaillerait deux ans de plus
  récupérerait à la fois des cotisations et un diviseur plus favorable.

- **Le net.** Tous les montants sont **bruts**. Une pension supporte la CSG, la
  CRDS et la CASA, dont les taux dépendent du revenu fiscal de référence du
  FOYER — que le modèle ne connaît pas, puisqu'il décrit une carrière et non un
  ménage. Le passage au net retrancherait, pour un retraité au taux normal,
  environ 9,1 % de la pension. Ce prélèvement étant proportionnel et identique
  dans les trois scénarios, il ne déplacerait aucun des écarts affichés : c'est
  la raison pour laquelle le brut suffit ici.
  La règle vaut aussi à l'entrée : le revenu d'activité se saisit en brut, et le
  simulateur ne propose pas de le saisir en net. Il faudrait pour cela une série
  de taux de prélèvement salarial par statut et par année, du même niveau de
  preuve que le reste du dépôt, qui n'y est pas. Le champ le dit donc
  explicitement — « avant cotisations et impôt ; pour un salarié, la ligne brut
  de la fiche de paie » — et donne l'échelle chiffrée, SMIC, salaire moyen et
  plafond, plutôt que de la laisser deviner.

- **L'arrondi des revenus portés au compte.** L'article L. 133-10 du code de
  la sécurité sociale arrondit à l'euro le plus proche « le montant des
  cotisations et contributions sociales et de leurs assiettes » — donc les
  revenus inscrits au compte, la fraction de 0,50 € étant comptée pour 1. Le
  modèle ne l'applique pas : il porte au compte des revenus reconstitués, au
  centime. L'écart est borné et il est petit — chaque année retenue s'écarte de
  0,50 € au plus, donc leur moyenne aussi, donc la pension de **0,25 € par an**,
  soit **0,02 € par mois**, quel que soit le niveau de revenu. À comparer aux
  8,5 % d'amplitude qu'ouvre le seul choix d'hypothèse de productivité. Deux
  raisons de ne pas l'appliquer aujourd'hui : la règle vise des assiettes
  DÉCLARÉES, que le modèle n'a pas — il synthétise ses revenus depuis un profil
  —, et la doctrine ne dit pas si l'arrondi précède ou suit la revalorisation,
  ce qui n'a aucun effet sur le résultat mais en aurait un sur ce qu'on pourrait
  affirmer. Le reste de la chaîne, lui, est conforme : les trimestres sont
  arrondis à l'entier supérieur (R. 351-27), et la pension n'est pas arrondie du
  tout — voir `methodologie.md`.

- **La capitalisation.** Le compartiment RAFP est isolé et converti au même
  coefficient actuariel que le reste, mais son **rendement financier propre**
  n'est pas modélisé : ses points sont valorisés au barème publié par l'ERAFP,
  non par le rendement de son portefeuille. C'est le traitement demandé — seule
  la répartition est en cause — et il rend le RAFP comparable au reste plutôt
  que de le faire dépendre d'hypothèses de marché.

- **Les carrières réelles.** Une carrière se décrit de deux façons, et la
  seconde n'est plus réservée au Python : le **profil paramétrique** — des
  métiers, un niveau de revenu relatif, une progression —, ou le **relevé**
  saisi année par année dans le champ prévu du simulateur, qui n'en reconstitue
  rien. Il reste à ce chemin une approximation et une impossibilité.

  L'approximation est le MOIS. Un relevé donne l'année, jamais le mois : chaque
  ligne vaut donc une année civile pleine, sauf celle du départ, que la date de
  liquidation tronque parce que le modèle la connaît. L'année d'entrée dans la
  vie active reste comptée pour une année entière alors qu'elle est presque
  toujours partielle — son revenu est celui des mois travaillés, et le modèle ne
  peut pas l'annualiser sans savoir lesquels. Un régime liquidant sur les six
  derniers mois de service n'en souffre pas, cette année-là n'étant pas la
  dernière ; un régime qui prend les vingt-cinq meilleures années y voit une
  année faible de plus, exactement comme le droit.

  L'impossibilité reste l'INTERROGATION AUTOMATIQUE du répertoire de gestion
  des carrières uniques : il n'est pas ouvert au public, et son accès passe par
  une authentification personnelle qu'un script ne saurait porter sans détenir
  les identifiants de l'assuré. Ce qui a cédé, en revanche, c'est la recopie à
  la main : **le relevé se dépose maintenant en PDF sur le simulateur**, qui le
  lit dans le navigateur — il est téléchargé par l'assuré sur son compte
  retraite, et le fichier ne quitte pas la page. `moteur/js/lecture-pdf.js` en
  tire les lignes de texte, `moteur/js/releve-lu.js` la carrière, et le champ
  `releve` reçoit ce que l'un et l'autre ont compris. Restent quatre choses que
  le document lui-même ne donne pas, et que le site dit à qui le dépose :

  - **Le revenu est plafonné.** Le régime général ne reporte au compte que la
    part du salaire brut qui tombe sous le plafond de la Sécurité sociale :
    au-delà, le relevé n'affiche pas le salaire en entier, et la simulation lit
    donc un revenu tronqué. La carrière paramétrique, elle, ne l'est pas.
  - **Un régime qui compte en points ne porte aucun revenu.** Les professions
    libérales depuis 2004, les exploitants agricoles : leur relevé donne des
    points et des trimestres. La lecture prend les années et les trimestres,
    laisse le revenu à zéro et le dit — déduire un revenu du barème de la
    caisse serait écrire un chiffre que le document ne porte pas.
  - **Un état de services couvrant plusieurs années n'est pas réparti.** « Du
    01/09/1996 au 31/08/2001 », tel que la fonction publique l'écrit, ne dit ni
    le revenu de chaque année ni leur partage : la ligne ressort telle quelle
    et reste à saisir.
  - **Le document doit se reconnaître.** Un fichier qui ne porte ni le titre
    d'un relevé ni l'en-tête de la colonne des trimestres n'est pas lu du tout.
    C'est un vrai document qui l'a imposé : le rapport de l'OPEF sur les frais
    de l'épargne retraite, cent pages sans le moindre relevé, rendait
    vingt-deux « années de carrière » qui n'avaient jamais existé.

  Et un PDF qui n'est qu'une image — un scan, une photographie, une capture
  d'écran — ne porte aucun texte : rien ne s'y lit, et la page le dit plutôt
  que de rendre une carrière vide sans explication.

- **La coordination interrégimes.** Chaque régime liquide sur ses seules
  années, et la durée acquise dans chacun est comptée séparément — c'est le
  droit, et un régime et celui qui lui succède comptent pour un seul (voir
  §3). Restent dehors la **proratisation croisée** du salaire annuel moyen
  entre régimes alignés et la **liquidation unique** (LURA), qui, depuis 2017,
  fait calculer par une seule caisse la retraite d'un polypensionné des trois
  régimes alignés. L'effet est de second ordre pour une carrière
  mono-affiliée — le cas ordinaire — et joue plutôt à la hausse pour un
  polypensionné, dont le salaire annuel moyen unique est calculé sur les
  meilleures années tous régimes confondus.

---

## 5 ante. Le pilier capitalisé : ce que sa rente suppose

Le compartiment de capitalisation obligatoire du scénario 6 est le seul endroit
du modèle où de l'argent est placé, et il porte donc des incertitudes que le
reste n'a pas. Six, et la première est de loin la plus lourde.

**1. La prime de terme n'est pas retirée des forwards.** Les versements futurs
se placent aux taux forward implicites de la courbe du jour. Sous l'hypothèse
des anticipations pures, le forward est le taux futur attendu ; en pratique, il
le dépasse d'une prime de terme que la littérature situe entre 0,3 et 1 point
sur les maturités longues quand la courbe est ascendante. **Le pilier est donc
flatté**, et d'autant plus que la carrière est longue. L'alternative — retirer
une prime estimée — supposerait davantage et se vérifierait moins ; le choix
est dit plutôt que corrigé. Ordre de grandeur : un demi-point de rendement sur
quarante ans vaut une dizaine de pour cent de capital final.

Depuis septembre 2026, le modèle **sait** la retirer :
`Parametres.prime_terme_trente_ans` décompose le taux observé en une moyenne de
taux courts attendus et une prime proportionnelle à la maturité, calcule les
forwards sur la première et rajoute la seconde à la maturité achetée — de sorte
qu'un placement comptant rend toujours le taux coté du jour. **Le paramètre vaut
zéro, et le site publie à zéro** : la réserve ci-dessus tient donc entière, et
ce qui change est qu'elle est désormais mesurable plutôt que seulement dite. À
0,005 — le milieu de la fourchette — le capital d'une carrière de trente-six ans
partant en 2060 recule de 4,8 %, et la rente de 23 € par mois.

Il ne porte que sur le **pilier**, et c'est une correction : portée sur la
courbe commune, la prime déplaçait aussi le taux auquel la page Coût finance
les déficits, donc le stock de dette de TOUS les systèmes — jusqu'à dix points
de PIB sur le système actuel, qui n'a pas de pilier capitalisé. Le coût de
rouler une dette courte se pose dans les mêmes termes et reste une question
ouverte, mais c'en est une autre, et un réglage du pilier n'est pas l'endroit
d'où la trancher. Un test tient la séparation.

Depuis, il est un **réglage du site** : « Taux futurs du pilier capitalisé »,
à côté de celui des frais, avec trois positions — les taux à terme de la
courbe (défaut), la prime retirée au milieu de la fourchette (0,50 point à
trente ans), la prime retirée au haut (1 point). Une réserve qu'un lecteur peut
chiffrer lui-même cesse d'être une réserve qu'on lui demande de croire, et le
choix de publier sous les anticipations pures redevient ce qu'il est : un
choix, pas un impensé.

Cette réserve en portait une autre, restée invisible tant qu'elle n'était pas
chiffrée : **sous les anticipations pures, l'allocation des maturités n'a
aucune conséquence.** C'est une identité, pas une approximation — découper un
horizon en un trente ans, en trois dix ans ou en quinze deux ans accumule
exactement la même chose, parce que c'est ce que l'arbitrage impose au forward,
et les frais annuels n'y changent rien. L'échelle glissante 2/10/30 que le
pilier pratiquait jusque-là était donc un paramètre libre sans effet ; elle a
été remplacée par l'adossement à l'horizon, qui est la bonne règle pour une
autre raison — l'actif sans risque d'une dette datée est le titre qui tombe ce
jour-là — et dont le changement n'a pas déplacé un centime de capital ni de
rente. Voir `docs/methodologie.md`.

**2. La courbe est celle d'un jour.** Elle est datée, publiée, recontrôlée,
mais elle est un instantané : le 17 septembre 2026 et non un mois plus tôt. Un
déplacement général de la courbe déplace tout le pilier, et rien dans le modèle
ne lisse cette dépendance. C'est assumé — une moyenne de courbes n'est la
courbe de personne — et c'est la raison pour laquelle le fichier de référence
garde les courbes successives : un chiffre publié doit pouvoir être refait tel
qu'il a été publié.

**3. Les frais sont ceux du marché, et leur baisse est une hypothèse.** Le
pilier supporte quatre frais, aux vraies moyennes du marché du PER individuel
en 2025, lues sur le rapport de l'OPEF (tableau T7) et sur celui du CCSF de
2021 : 1,09 % sur versement et 0,76 % par an sur encours, moyennes pondérées
par les primes et par l'encours ; 0,99 % sur arrérages, moyenne sur les vingt
assureurs déclarants et non sur les seuls neuf qui facturent (2,20 %) ; et
0,52 % par an sur la réserve de la rente, que l'OPEF ne mesure pas et que le
CCSF relevait sur 22 contrats sur 34, de 0,60 à 1 % par an, estimé au milieu
de la fourchette sur la part des contrats qui facturent. Ce dernier frais pèse
plus que les arrérages : 8 % de rente au diviseur du modèle. Trois choses que
ces sources disent sur ce que les moyennes sont :

- Le frais sur versement du PER (1,09 %) est le double de celui de
  l'assurance-vie (0,55 %) et six fois celui du contrat de capitalisation
  (0,19 %), pour les mêmes assureurs et les mêmes fonds en euros. L'OPEF
  l'explique par des frais fixes qui pèsent sur des primes petites. Une
  cotisation prélevée sur chaque paie n'a pas cette structure de coût.
- La moyenne des frais sur arrérages publiée est **non pondérée** et ne porte
  que sur les 9 organismes, sur 20, qui les facturent : onze assureurs sur
  vingt ne prélèvent rien sur la rente. Le 2,20 % est la moyenne de ceux qui
  facturent, le 0,99 % celle du marché, et la médiane est nulle.
- Le frais de gestion du fonds en euros est le poste qui compte, parce qu'il
  s'applique chaque année à tout l'encours, et c'est celui qu'un régime
  obligatoire fait le plus baisser : la prime de pension suédoise, seul pilier
  obligatoire capitalisé adossé à un compte notionnel, coûte 0,11 % des
  encours en frais de fonds après remise et 0,024 % d'administration ; le
  Fonds de réserve pour les retraites, 0,41 % toutes charges comprises, dont
  8,6 points de base de coûts fixes, en gérant des actions ; l'ERAFP
  provisionne « au moins 0,2 % des encours ». Aucun ne prélève sur les
  versements ni sur les arrérages.

**Ce que ces moyennes sont, et ce qu'on sait des médianes.** Les frais sur
versement et de gestion de l'OPEF sont des moyennes **pondérées** de tout le
marché remis à l'ACPR, par les primes pour le premier, par l'encours moyen pour
le second : un euro versé ou placé y pèse un euro, ce sont les vraies moyennes
de ce qui est payé. Aucune source publique ne donne de médiane pour ces deux
postes ; la seule autre mesure du même marché est le rapport du CCSF de
juillet 2021, sur 34 PER assurance et leurs tarifs affichés, en moyennes
arithmétiques non pondérées. Ce que l'on a, le 20 septembre 2026 :

| Poste | OPEF 2025, marché | Sur tous les déclarants | Médiane | CCSF 2021, 34 contrats affichés |
|---|---|---|---|---|
| Versement | 1,09 %, pondéré par les primes | idem | non publiée | maximum affiché 3,18 % en moyenne, 0 à 5 %, courtiers en ligne à 0 |
| Gestion, fonds en euros | 0,76 %, pondéré par l'encours | idem | non publiée, entre 0,75 et 0,90 % à en juger par la dispersion | 0,87 % en moyenne, 0,60 à 1 % hors un fonds à 2 %, 0,66 à 0,93 % par catégorie |
| Arrérages | 2,20 %, non pondéré, 9 facturants sur 20 | 0,99 % | nulle, onze déclarants sur vingt à zéro | 1,18 % zéros compris sur 30 contrats, 0 à 3 %, onze à zéro, 0,60 % (banques) à 2,30 % (mutuelles) |
| Réserve de rente | non mesuré | non mesuré | non publiée | 22 contrats sur 34 facturent, de 0,60 à 1 % par an |

**La baisse des frais, et ce qu'elle suppose.** Le modèle fait baisser chaque
poste par paliers (`Parametres.frais_*_paliers`), parce que c'est ainsi que
les frais ont bougé partout où une épargne retraite obligatoire a mis les
gérants sous plafond ou en concurrence, et les sources de chaque marche sont
des jeux `controle` du manifeste :

| Marché | Mécanisme | Ce qui s'est passé |
|---|---|---|
| Royaume-Uni | plafond de 0,75 % sur les fonds par défaut, avril 2015 | 0,48 % en moyenne en 2020 sur les régimes concernés, 0,29 % dans les régimes fiduciaires ; les régimes hors plafond passent de 0,79 % à 0,53 % |
| Chili | adjudication des nouveaux entrants tous les deux ans, depuis 2010 | commission du gagnant : 1,14 %, 0,77 %, 0,47 %, 0,41 %, puis 0,69 % en 2018, 0,58 %, 0,49 %, 0,46 % en 2025 ; 1,36 % avant ; un gagnant a remonté de 0,47 à 1,16 % une fois libre |
| Suède | remise imposée aux gérants de la prime de pension, plafonds en 2015 et 2021 | frais moyen net de 0,31 % en 2013, 0,21 % en 2020, 0,13 % en 2022, 0,11 % en 2026 ; 0,45 % sans la remise |
| États-Unis | concurrence seule | fonds actions, pondérés par les encours : 1,04 % en 1996, 0,40 % en 2025, 3,3 % de baisse par an ; plans 401(k) : 0,76 % en 2000, 0,26 % en 2024 |
| Australie | produit par défaut MySuper, 2014 ; test de performance, 2021 | frais MySuper de 1,05 % à 1,00 % en 2023, « la plus forte baisse depuis 2014 » ; plus lent que les autres |
| France | concurrence des courtiers en ligne, transfert des PER | frais sur versement, mesuré sur les primes de l'année : PER 1,20 % → 1,09 %, assurance-vie 0,75 % → 0,55 % en deux ans ; frais de gestion, mesuré sur tout l'encours : 0,73, 0,77, 0,76 % |

Trois leçons, et le modèle les tient. **La baisse va par à-coups**, une
décision puis un plateau, d'où des paliers plutôt qu'une pente : le frais de
gestion suit le rythme américain, le seul observé sur trente ans, par marches
de dix ans (0,76, 0,54, 0,39, 0,28, 0,20 % en 2066, le plancher de l'ERAFP) ;
le frais sur versement rejoint l'assurance-vie de 2025 en 2031, le contrat de
capitalisation en 2036, zéro en 2046 ; le frais sur arrérages, dont la médiane
est déjà nulle, s'éteint en 2046 ; le frais sur la réserve suit le rythme de
la gestion. **Elle porte sur les nouveaux dépôts, et un peu sur le stock** :
un frais de gestion est contractuel, l'OPEF le montre en deux ans, et les
lignes de l'échelle portent le tarif de leur cohorte, qui ne referme chaque
année que 10 % de son écart avec le tarif du jour, la moitié en sept ans,
entre le contrat privé qu'on ne renégocie pas (0) et le plafond qui touche
tout le stock d'un coup (1), comme au Royaume-Uni et en Suède. **Elle n'est
pas acquise** : le Chili a vu la commission d'une caisse remonter de 0,47 % à
1,16 % dès qu'elle a cessé d'être adjudicataire, et le modèle ne fait jamais
remonter un frais. Les paliers sont une hypothèse, datée et sourcée, pas une
mesure ; leurs années et leurs niveaux se changent en un endroit.

**Ce que chaque hypothèse déplace.** Rente mensuelle du pilier, les deux
cotisations réunies, pour un non-cadre né en 2004 qui cotise de 22 à 64 ans,
donc toute sa carrière après la bascule (le 20 septembre 2026, courbe du 17,
diviseur par niveau de vie) :

| Réglage | Rente | Écart |
|---|---|---|
| retenu : moyennes 2025 du marché, paliers, convergence 0,10 | 1 800 € | référence |
| PER 2025 tel que vendu, figé, sans frais de réserve, l'ancien réglage : 1,09 / 0,76 / 2,20 | 1 665 € | − 8 % |
| moyennes 2025 du marché figées, aucune baisse | 1 553 € | − 14 % |
| paliers, mais le stock garde son tarif, convergence 0 | 1 750 € | − 3 % |
| paliers, et tout le stock suit, convergence 1 | 1 832 € | + 2 % |
| retenu, sans frais sur la réserve de rente | 1 839 € | + 2 % |
| aucun frais | 2 035 € | + 13 % |

Pour un assuré né en 1985, qui liquide en 2049, les paliers ne sont encore
qu'à moitié parcourus : les moyennes figées lui coûtent 7 %, et le frais sur
la réserve, encore à 0,27 %, 4 %. Pour un assuré né en 1970, qui liquide en
2034, aucun palier n'est atteint, et le nouveau réglage sert 7 % de moins que
l'ancien, parce que le frais sur la réserve de rente (8 %) pèse plus que la
baisse des arrérages ne rend. Sur le total servi par le scénario 6, dont le
pilier pèse au plus deux cinquièmes, chaque hypothèse déplace donc de un à six
points. Le sens de chacune est connu, la taille est encadrée, et le choix
reste celui du paramètre.

**4. Aucun risque n'est simulé.** Le pilier est sans risque par construction,
et c'est un choix de proposition autant que de modèle : un régime obligatoire
qui promet une rente ne peut pas la gager sur des actions. Mais le modèle ne
dit rien de ce qu'un panachage aurait donné, ni de la volatilité qu'il aurait
fallu accepter pour cela. Il ne dit rien non plus du risque de crédit : la
courbe retenue est celle des souverains les mieux notés, pas celle de la dette
française, qui rendait 51 points de base de plus au dix ans.

**5. Aucune fiscalité.** Les versements au PER sont déductibles du revenu
imposable, la rente est imposable à la sortie, et le capital transmis au décès
relève d'un régime successoral propre. Tous les montants du dépôt sont bruts,
et l'avantage fiscal à l'entrée — qui est une part réelle du rendement d'un PER
pour un contribuable imposé — n'est pas compté. Il joue en sens inverse des
points 1 et 2 : il minore la rente affichée.

**6. La garantie vieillesse ignore la rente capitalisée.** Elle est servie sur
la seule pension contributive de répartition. Si le droit décidait de compter
la rente du pilier dans les ressources examinées, la garantie coûterait moins
et servirait moins ; le modèle ne tranche pas une question qui n'est pas la
sienne, et la page Coût chiffre la garantie sans ce pilier.

Une dernière chose, qui n'est pas une limite mais une convention à connaître :
**l'espérance de capital transmis n'est pas conditionnée à la survie**. Elle se
lit de l'ouverture du pilier, et se rapporte donc à quelqu'un qui peut mourir
avant son départ, quand la rente affichée, elle, suppose qu'il l'atteint. Les
deux chiffres décrivent deux futurs, et leur somme n'a pas de sens.

---

## 5 ante bis. La fiche de paie : neuf réserves, dont trois décisives, et deux que la restitution ajoute

Le site affiche, sous les quatre pensions, ce qu'un actif touche PENDANT qu'il
cotise : coût du travail, revenu brut, revenu net, sous le droit en vigueur et
sous la proposition. C'est la seule grandeur du dépôt qui ne soit pas une
pension, et elle porte ses incertitudes propres. Trois d'entre elles — la 1, la
2 et la 5 — commandent le SIGNE du résultat, et pas seulement sa taille.

**1. L'incidence est supposée intégrale, et c'est une hypothèse.** Le coût du
travail est tenu fixe, et le salaire brut est celui qui l'épuise sous les
nouveaux taux : ce que l'employeur ne verse plus en cotisations, il le verse en
salaire. C'est la lecture que fait l'économie du travail à long terme — une
cotisation patronale est du salaire différé —, et c'est la plus favorable à une
baisse de cotisation. Rien n'oblige un employeur à rendre son économie du jour
au lendemain, et la lecture prudente, où seule la part salariale bouge, donne
environ la moitié du gain : c'est `Incidence.ASSIETTE` dans `remuneration.py`,
et la réserve 5 dit pour quels statuts c'est la seule lecture disponible.

**2. Le partage salarial/patronal du taux unique n'est pas neutre, et la
proposition ne le fixait pas.** Elle dit « 18 %, salariale et patronale
additionnées ». Le dépôt a partagé moitié-moitié jusqu'au 20 septembre 2026,
faute d'avoir mesuré ; **le programme a tranché ce jour-là, sur la mesure : la
part patronale ne bouge pas — 16,67 points, ce qu'elle vaut aujourd'hui — et la
part salariale tombe de 11,31 à 6,33.** On croirait ce choix sans effet sous
l'incidence intégrale ; il ne l'est pas, pour deux raisons distinctes : la CSG
et la CRDS sont assises sur le BRUT, que le partage déplace ; et la réduction
générale n'efface que des cotisations PATRONALES. À deux fois le SMIC, le gain net
mensuel du partage retenu vaut **+182 € dès le premier mois et +175 € une fois
le brut stabilisé** ; il valait −7 puis +81 sous le moitié-moitié, −426 puis
−141 si les 23 points étaient entièrement salariaux, +412 puis +286 s'ils
étaient entièrement patronaux. Ces quatre lectures isolent le partage : elles
neutralisent la restitution aux salaires décidée le même jour, qui s'ajoute à
toutes et que les réserves 8 et 9 de ce bloc décrivent. Le paramètre pèse donc toujours plus que la
baisse de taux elle-même, et c'est ce qui rend son arbitrage politique.

**Ce que le choix retenu achète, et ce qu'il coûte**, mesuré par
`scripts/partage_taux_unique.py` et détaillé à l'action 56 de la feuille de
route. Il achète l'immédiateté : la baisse est sur la fiche le lendemain de la
réforme, sans hypothèse d'incidence, et elle ne fuit pas, le brut ne bougeant
pas pour grossir l'assiette de la CSG et des autres branches. Il coûte le
brut : celui-ci ne monte pas, donc ni les droits qui en dépendent, ni le crédit
au compte notionnel. Le partage inverse ferait monter le brut de 2,9 %, mais
des années plus tard, amputé du quart en chemin, et de rien du tout au SMIC.
C'est la réserve la plus lourde de ce bloc, et elle n'a pas disparu en étant
tranchée : elle a changé de nature, d'un paramètre non mesuré à un arbitrage
entre le net d'aujourd'hui et le brut de demain.

**3. Le résultat au voisinage du SMIC était négatif, et ne l'est plus.** Il
l'était sous le moitié-moitié, pour une raison qui tient et qu'il faut garder
en tête : la réduction générale dégressive unique efface depuis 2026 la
totalité des cotisations patronales de son périmètre au niveau du SMIC — son
coefficient maximal, 40,21 %, est exactement leur somme —, si bien qu'un
salarié au SMIC ne supporte aujourd'hui que ses 11,3 points salariaux, et que
baisser la part patronale ne lui rend rien. Le partage retenu ne touche pas à
cette part : il ramène la retenue de l'assuré à 6,33 points, et le gain au SMIC
est de **+91 € par mois le premier mois, +39 € une fois le brut stabilisé**.

**Deux réserves subsistent au SMIC, et elles sont de sens opposé.** Le coût du
travail y monte de **66 € par mois**, seul niveau de salaire où il bouge : la
part patronale du pilier capitalisé est hors du périmètre de la réduction
générale, donc l'employeur la verse pour de bon, là où la réduction absorbait
ce que le régime général lui prenait. Et la lecture de long terme y est
impossible en droit, comme la réserve 4 le dit : elle supposerait un brut
inférieur au salaire minimum.

**4. L'incidence intégrale n'est pas praticable au SMIC.** Elle y supposerait un
salaire brut inférieur au salaire minimum, ce que la loi interdit. Dans la
réalité, c'est le coût du travail qui monterait. Le site pose un avertissement
quand le cas se produit ; le modèle, lui, ne recalcule pas la variante « coût du
travail en hausse », qui supposerait de décider ce que l'employeur en fait.

**5. Le gain d'un fonctionnaire et celui d'un salarié du privé ne se comparent
pas terme à terme.** Le site couvre désormais quatre profils, et le découpage
n'est pas celui des familles de statut : c'est celui de ce que l'on sait de
l'employeur. Quand il verse des taux de DROIT COMMUN — un salarié du privé, un
agent d'un régime spécial que la fermeture de 2023 a versé au régime général, un
agent public non titulaire —, le site affiche un coût du travail et le tient
fixe : l'incidence est intégrale. Quand ce qu'il verse est un taux
d'ÉQUILIBRE — 82,28 % du traitement pour l'État en 2026, 37,65 % pour la
CNRACL —, **le site n'affiche pas de coût du travail** : ce taux est fixé pour
que le compte d'affectation spéciale « Pensions » tombe juste, non parce que
l'agent acquerrait 82 % de son traitement en droits nouveaux, et poser dessus
l'incidence intégrale afficherait une hausse de salaire de soixante-dix points
qui n'existe pas — la dette de pensions qu'il finance, elle, reste à payer. Pour
ces statuts, le traitement indiciaire brut est tenu fixe et seule la retenue de
l'agent bouge : c'est la lecture prudente. Le gain affiché vaut donc **environ
la moitié** de ce qu'une lecture intégrale donnerait, et le mettre en regard de
celui d'un salarié du privé compare deux hypothèses et non deux statuts. La page
le dit à l'endroit où elle affiche le chiffre. Un indépendant tient lui aussi
son revenu fixe, mais là ce n'est pas une hypothèse : il n'a pas d'employeur,
donc rien à répercuter.

**5 bis. Quatre familles de statut ne reçoivent toujours aucune fiche de paie.**
Les salariés et exploitants agricoles — la MSA a ses propres taux hors
retraite —, l'outre-mer, dont chaque collectivité a sa caisse, les élus, dont
l'indemnité de fonction n'est pas un salaire, et qui n'a pas d'emploi. Mieux
vaut rien qu'un net faux, et c'est un test qui le tient.

**5 ter. Ce que chaque profil laisse dehors.** Pour un fonctionnaire, la
retraite additionnelle de la fonction publique (RAFP), assise sur les PRIMES que
l'assiette du dépôt — traitement indiciaire brut et NBI — exclut par
construction : un agent dont les primes pèsent lourd ne voit ici qu'une fraction
de sa feuille de paie. Pour un indépendant, la contribution à la formation
professionnelle (un forfait de 0,25 % du plafond, et non un taux, laissé dehors
par symétrie avec les taxes sur salaires du privé) et l'assiette minimale que la
loi impose aux très bas revenus, faute de savoir si l'assuré relève d'une de ses
exonérations : le net affiché en bas de barème est un plafond. Ses cotisations
de retraite sont par ailleurs celles des fiches de régime, qui alignent
l'artisan et le commerçant sur le régime général — 15,45 % sous le plafond et
2,51 % déplafonnés plutôt que 17,15 % et 0,72 % : c'est la convention du modèle
entier, et la fiche de paie ne peut pas en diverger sans que le compte notionnel
et elle cessent de dire la même chose. Enfin, pour un agent public non
titulaire, le coefficient maximal de la réduction générale reste celui du décret
— un chiffre national bâti sur les taux du privé —, alors que le périmètre de
son employeur est plus étroit de la CEG et plus large de l'Ircantec ; ce qui
borne la réduction est alors la règle générale, qui interdit d'effacer plus que
ce qui est dû.

**6. Le coût du travail affiché est un plancher.** Ne sont comptées ni la taxe
d'apprentissage, ni la contribution à la formation, ni la participation à la
construction, ni le versement mobilité, ni la prévoyance et la mutuelle
d'entreprise. Aucune ne bouge d'un système à l'autre, et plusieurs dépendent de
la commune ou de la taille de l'entreprise ; les porter demanderait de choisir
un employeur type de plus. L'employeur retenu est une entreprise de cinquante
salariés et plus ; sous le seuil, le FNAL et le coefficient de la réduction
générale valent 0,40 point de moins. Le taux d'accidents du travail est le taux
moyen d'OpenFisca (3,00 %), au-dessus du taux net moyen national ; il ne déplace
aucun écart entre systèmes, seulement le niveau du coût affiché.

**7. Les taux sont ceux d'un millésime, appliqués aux années à venir.** Le
barème est celui en vigueur au 1er janvier 2026, reconduit tel quel jusqu'au
départ : le modèle ne prévoit pas la prochaine loi de financement. Les salaires,
le plafond et le SMIC, eux, suivent les séries projetées, si bien que le rapport
du salaire au SMIC — ce qui commande la réduction générale — reste stable. Les
taux viennent d'OpenFisca-France, transcription tierce du Journal officiel :
fiabilité `haute`, jamais `certifiee`. Quatre barèmes ont en revanche été lus à
la source dans l'index LEGI : la réduction générale (L. 241-13, version du
1er janvier 2026, LEGIARTI000053280526) et les trois barèmes d'indépendant que
la réforme de l'assiette unique de 2024 a réécrits et dont OpenFisca porte
encore la rédaction de 2018 — maladie et maternité (D. 621-1 et D. 621-2),
allocations familiales (D. 613-1) et indemnités journalières (D. 621-3). C'est
la réserve à surveiller en sens inverse : là où OpenFisca a du retard, le dépôt
ne le voit que s'il va lire.

**8. La suppression de la taxe sur les salaires ne se voit sur aucune fiche de
paie du modèle, et c'est un manque, pas un oubli.** Depuis le 20 septembre
2026, la proposition supprime les deux impôts du poste « impôts et taxes
affectés » qui sortent d'une rémunération — la taxe sur les salaires, dont
58,35 % va à la branche vieillesse (L. 131-8, 1°), et le forfait social, qui
lui va en entier (L. 241-3, 1°). Or la taxe sur les salaires n'est due que par
les employeurs NON assujettis à la TVA — hôpitaux, banques, assurances,
associations —, et le profil d'employeur du dépôt est une entreprise de
cinquante salariés et plus assujettie à la TVA : la ligne n'y est pas, et sa
suppression n'y rend donc rien. Un salarié d'hôpital ou d'association verrait,
lui, son coût du travail baisser d'autant, et sous l'hypothèse d'incidence du
module cela remonterait dans son salaire. Le dépôt COMPTE cette suppression
dans l'enveloppe rendue — c'est ce que la page Coût chiffre —, mais ne la
RÉPARTIT sur personne. Le corriger demanderait un cinquième profil, celui de
l'employeur non assujetti, et le barème de la taxe, qui est progressif par
tranches. Même remarque pour le forfait social, assis sur l'intéressement et la
participation, que la fiche du dépôt ne porte pas davantage.

**9. La pension est calculée sur le revenu de la carrière, pas sur le brut que
la fiche affiche.** C'est vrai depuis toujours et cela ne pesait presque rien :
sous l'incidence intégrale, le brut d'un salarié du privé monte de quelques
pour cent, et la pension calculée sur l'ancien brut est sous-estimée d'autant.
Depuis que la contribution d'équilibre d'un employeur public est partagée, cela
pèse beaucoup plus : le traitement d'un fonctionnaire d'État monte d'un tiers
sur la fiche, et sa pension continue d'être calculée sur le traitement
d'avant. **Le dépôt sous-estime donc la pension de la proposition pour les
agents publics**, et l'écart est du même ordre que la hausse du traitement. Le
corriger demanderait de reboucler la fiche de paie sur la carrière — le brut
sous la proposition devenant l'assiette de la cotisation —, ce qui est une
boucle de point fixe et non un calcul de plus. La fiche de paie et la pension
restent, pour l'instant, deux lectures d'un même monde qui ne se parlent pas.

Rien de tout cela ne touche une pension : retiré, le modèle calcule exactement
les mêmes six scénarios.

---

## 5 ante ter. Le net et le brut : ce que la bascule suppose

Le simulateur se lit entièrement en net ou entièrement en brut, saisie comprise.
Quatre réserves, dont la première commande tout le reste.

**1. Le taux de CSG sur les pensions est celui du TAUX PLEIN, pour tout le
monde.** L'article L. 136-8 le fait dépendre du revenu fiscal de référence du
foyer, perçu l'avant-dernière année, et en tire quatre cas pour une part de
quotient familial (montants 2026, revalorisés chaque année sur les prix) :
exonéré jusqu'à 11 128 €, 3,80 % jusqu'à 14 548 €, 6,60 % jusqu'à 22 580 %,
8,30 % au-delà. Le simulateur ne demande ni la composition du foyer, ni les
autres ressources, ni un revenu d'il y a deux ans : il applique donc 8,30 %,
plus 0,50 % de CRDS et 0,30 % de CASA, soit **9,10 %**.

La convention SURESTIME le prélèvement sur les petites pensions — et ce sont
justement celles des scénarios notionnels. Une pension de 660 € par mois
placerait son titulaire, s'il vivait seul et n'avait rien d'autre, sous le
premier seuil : il serait exonéré des trois, et son net vaudrait son brut. Le
site lui retire 9,1 %. L'écart entre systèmes affiché en net est donc un peu
RESSERRÉ pour les petites pensions, et exact pour les grandes. La page le dit
sous la clé de lecture.

**2. La cotisation maladie de 1 % sur la retraite complémentaire n'est pas
comptée.** Elle ne porte que sur une partie de la pension, et les cinq scénarios
notionnels ne distinguent pas base et complémentaire — leur compte est unique.
L'appliquer aux uns et pas aux autres fabriquerait un écart qui ne viendrait
d'aucune règle. Le net d'un retraité du privé est donc, de ce fait, très
légèrement surestimé.

**3. La rente du pilier capitalisé suit le barème des pensions**, et c'est une
convention : le dépôt la traite en rente viagère à titre GRATUIT, ce qu'elle est
quand la cotisation qui l'a constituée a été prélevée à la source et déduite —
le cas d'une cotisation obligatoire. Une rente à titre onéreux relèverait des
prélèvements sur revenus du patrimoine, à 17,2 % sur une fraction du montant qui
dépend de l'âge. La proposition ne tranche pas.

**3 bis. Le taux de remplacement suit le mode, et il MONTE en net.** Le modèle
le calcule brut sur brut. En mode net, le site le convertit — pension nette
rapportée au dernier revenu net —, sans quoi il serait le seul chiffre de la
page à parler l'autre langue. Le taux net dépasse alors le taux brut de
plusieurs points : 44,7 % devient 51,4 % sur la carrière témoin. Ce n'est pas
un artefact, c'est un fait du système français — une pension est prélevée de
9,1 %, un salaire d'une vingtaine de points — et il est rarement montré. La
conversion emprunte le rapport net/brut de la DERNIÈRE fiche de paie de la
carrière, celle de l'année du départ, qui est l'année du dénominateur ; pour un
statut sans fiche de paie, le taux reste brut faute de pouvoir le netter
honnêtement.

**4. Ce qui reste brut, et le restera.** Un CAPITAL notionnel et une ASSIETTE de
cotisation n'ont pas de net : on ne « nette » pas un capital. Les tableaux de
détail — décomposition par régime, capital, cotisations versées, contribution de
l'employeur — restent donc en brut dans les deux modes, et c'est leur seule
lecture possible. La bascule ne gouverne que ce qu'on TOUCHE : le salaire et la
pension.

**Et un mot sur la saisie.** En mode net, le nombre tapé est un net mensuel que
le modèle convertit en brut en résolvant la fiche de paie du statut — ce n'est
pas une estimation, c'est l'inverse exact du calcul qui produit le net. Les
statuts que le modèle ne sait pas décrire — exploitant agricole, élu,
collectivités d'outre-mer — font exception : leur montant est lu tel quel, et le
formulaire l'affiche plutôt que de le taire.

---

## 5 ante quater. Le partage « moitié aux salaires, moitié à la dette » : ce qu'il affirme et ce que rien ne vérifie

La proposition ne reconduit pas les impôts et taxes affectés ni la contribution
d'équilibre de l'État. Le dépôt ne disait pas ce que ces recettes devenaient,
ce qui revenait à les laisser au budget. Depuis le 20 septembre 2026, il le
dit : **la moitié est rendue aux salaires, la moitié éteint de la dette.**
Cinq réserves, et la dernière est la plus importante.

**1. La moitié qui « éteint de la dette » n'est vérifiée par rien.** Le dépôt
ne modélise aucun budget de l'État et aucune trajectoire de dette publique : il
porte la dette de toutes les administrations en part de PIB, mais comme un
décor, pas comme un compte. Que 32 Md€ par an aillent effectivement à
l'amortissement plutôt qu'à autre chose est une AFFIRMATION du programme, pas
un résultat du modèle. Rien, dans le dépôt, ne tomberait en défaut si elle
était fausse.

**1 bis. Le partage est un ÉTAT D'ARRIVÉE, pas un calendrier.** La moitié
rendue aux salaires ne l'est pas le lendemain de la bascule. Une baisse de CSG
salariale, elle, tombe sur le net immédiatement ; mais la suppression d'un
impôt payé par l'employeur — la taxe sur les salaires, le forfait social — ne
remonte dans les salaires que par la négociation, au fil des années, et c'est
la même hypothèse d'incidence de long terme que le module de la fiche de paie
assume déjà pour les cotisations patronales (§ 5 ante bis, réserve 1). Le
modèle montre donc le RÉGIME PERMANENT : ce que la fiche de paie vaut une fois
la répercussion faite. Rien dans le dépôt ne dit en combien d'années, et rien
ne le mesure : le chiffre affiché est un point d'arrivée, et le chemin n'est
pas modélisé.

**2. Le partage ne change aucun solde du système de retraite.** Ces recettes
étaient déjà sorties de son compte, et les rendre aux salaires ou les garder ne
déplace pas un centime du solde de la proposition. Ce qui bouge est la fiche de
paie, et le budget de l'État — que le dépôt ne tient pas.

**3. La part du poste assise sur une rémunération est mesurée de 2019 à 2025,
et reconduite ensuite.** Les deux impôts sont lus dans la section CNAV de la
fiche « contributions sociales et recettes fiscales brutes » des rapports à la
Commission des comptes de la Sécurité sociale. La série commence en 2019 parce
que le fonds de solidarité vieillesse recevait jusque-là sa propre fraction de
ces deux impôts, et que la seule section CNAV aurait sous-estimé le total sans
le dire ; depuis le 1er janvier 2019, l'article L. 135-3 ne laisse au fonds que
de la CSG. Au-delà de 2025, c'est la PART DU POSTE qui est reconduite et non le
montant : elle tient entre 26,6 et 28,9 % depuis 2019, mais rien ne garantit
qu'une loi de financement ne la déplace pas — elle a bougé de 63,25 à 58,35 %
pour la seule taxe sur les salaires entre 2025 et 2026.

**4. La baisse de CSG d'activité est une décision politique, pas une
restitution.** Il faut le dire dans ces termes parce que l'intuition dit le
contraire. **La CSG sur les revenus d'activité ne finance aujourd'hui aucune
retraite** : ses 9,20 points vont à la CNAF (0,95), aux régimes obligatoires
d'assurance maladie (4,25), à la CADES (0,45), à l'Unédic (1,47) et à la CNSA
(2,08) — 9,20 exactement, article L. 131-8, 3° du code de la sécurité sociale,
version en vigueur au 1er février 2026. Ce que la branche vieillesse encaisse
en CSG est assis sur le capital (6,67 points sur 10,6) et sur les pensions
(2,94 points). Baisser la CSG d'activité, c'est donc dépenser au profit des
salariés une recette que la retraite abandonne, et non leur rendre ce qu'on
leur prenait. Le choix de ce canal plutôt qu'un autre — une baisse de
cotisation maladie, un crédit d'impôt — n'est motivé par rien d'autre que sa
simplicité et son assiette, la plus large qui porte sur le travail.

---

## 5 bis. Le coût agrégé : ce qui est observé, ce qui est estimé

La page **Coût** superpose deux natures de chiffres, et il faut les séparer pour
la lire.

**La dépense observée n'est pas modélisée.** Elle vient des Comptes de la
protection sociale de la DREES, risque vieillesse-survie, poste `E11-2`, et elle
est **certifiée** : recontrôlée contre l'API du producteur à chaque exécution,
1959 à 2024 pour le total, 1990 à 2024 pour la ventilation par système. Deux
réserves de PÉRIMÈTRE, et non de fiabilité :

- le risque vieillesse-survie est plus large que « les retraites » : il porte
  aussi le minimum vieillesse, la dépendance des personnes âgées et la retraite
  supplémentaire par capitalisation, soit 27,9 milliards sur 426,7 en 2024. La
  ventilation permet de les retrancher, et la page affiche les deux grandeurs ;
- la ventilation ne commence qu'en 1990. De 1981 à 1989 la DREES en publie une
  autre, dont les périmètres ne se raccordent pas — « Régime général de la
  Sécurité sociale » y recouvre ce qui est aujourd'hui réparti entre la Cnav et
  d'autres organismes. Personne n'a publié le raccord : c'est une impasse
  démontrée, et non un oubli.

Le découpage lui-même est celui de la **comptabilité nationale**, par secteur
institutionnel et non par caisse. Deux conséquences qu'il faut connaître :
« régimes spéciaux » réunit la CNRACL — donc la fonction publique territoriale
et hospitalière —, la SNCF, la RATP et les IEG ; et « régime général » absorbe à
compter de 2020 les artisans et les commerçants, dont le régime a été adossé à
la Cnav. La marche de 2020 est une réorganisation, pas une dépense nouvelle.

**Le coût des quatre autres systèmes est estimé, et ne peut pas être autre
chose.** Il est obtenu en multipliant la dépense observée par le rapport des
masses de pension — la moyenne des écarts entre systèmes, pondérée par le poids
de chaque génération dans la masse de l'année. Ce rapport porte quatre
approximations, énoncées sur la page — la quatrième ayant cessé d'en être une
le 19 septembre 2026 :

1. **Les effectifs de génération ne sont plus supposés.** Cette page a d'abord
   pesé toutes les générations à égalité, faute de pyramide des âges ; elle
   porte désormais celle de l'INSEE, observée jusqu'en 2023. On sait donc
   maintenant ce que valait l'hypothèse levée : elle déplaçait l'écart cumulé du
   scénario 2 de six dixièmes de point sur soixante-six ans (−77,3 % contre
   −77,9 %). C'était peu, et c'est désormais mesuré plutôt qu'argumenté.
2. **Les treize cas types ne pèsent plus d'un poids égal.** Ils ont longtemps
   pesé ainsi, faute de source, et cette page affirmait qu'« aucune source ne
   fixerait » la pondération. C'était faux : l'enquête annuelle auprès des
   caisses de retraite dénombre les retraités caisse par caisse et année par
   année depuis 2004. Chaque cas type porte désormais l'effectif de sa caisse ;
   l'agent de conduite pèse 0,7 % et non 7,7 %, et les quatre carrières du
   privé 63 % à elles quatre.

   Ce que l'ancienne convention valait est donc mesuré plutôt qu'argumenté, et
   **le sens du biais annoncé n'était juste qu'à moitié**. On disait le rapport
   affiché « plutôt un plancher », les départs très précoces que le notionnel
   pénalise le plus étant surreprésentés. C'est vrai des scénarios qui portent
   la part patronale — le scénario 4 passe de −59,8 % à −56,0 % — et faux du
   scénario 2, qui passe de −78,3 % à −81,0 % : la pondération donne aux
   carrières du privé, que le compte salarial seul pénalise davantage encore,
   les deux tiers du poids. C'était un plancher pour les uns, un plafond pour
   l'autre.

   Trois réserves subsistent, et elles sont de nature différente de la
   précédente. **Un effectif de caisse n'est pas un effectif de personnes** :
   un polypensionné compte dans chacune des siennes, et la somme des caisses
   dépasse d'un tiers la ligne « tous régimes » ; le poids des régimes dont les
   affiliés ont typiquement aussi une carrière au régime général — Ircantec,
   MSA salariés — en est gonflé. **Une caisse réclamée par plusieurs cas types
   se partage également entre eux** : la Cnav est celle des quatre carrières du
   privé, et aucune source ne dit combien de ses retraités ont été cadres ;
   c'est la seule part de convention égalitaire qui subsiste, et elle ne joue
   plus qu'à l'intérieur du salariat privé. **Hors de 2004-2024, la répartition
   du bord est reconduite** : la France de 1960 comptait plus d'exploitants
   agricoles que ces poids ne le disent, et la série tombe au niveau `estimee`
   pour le dire.
3. **Avant 1975, la reconstitution est mince.** La répartition ne commence
   qu'en 1941 : les générations antérieures à 1880 n'ont, dans ce modèle,
   aucune pension, et plusieurs régimes n'existaient pas encore. Les premières
   années reposent sur deux ou trois générations et la moitié des cas types.
   Elles pèsent peu dans le cumul — la dépense de 1959 vaut 0,5 % de celle de
   2024 en euros courants — mais leur rapport ne vaut pas ce que valent ceux
   d'après 1980.

4. **Le rapport ne multiplie plus la réversion, et c'est le volet C.** Il
   décrit les droits DIRECTS et eux seuls : il est le quotient de deux masses
   calculées sur treize cas types, qui n'ont ni conjoint ni survivant, et la
   réversion figure depuis toujours parmi les droits que même l'étalon ne sert
   pas. La base à laquelle on l'appliquait, elle, porte les deux. Un scénario
   notionnel réduisait donc la réversion dans la même proportion que les
   pensions propres, **sans que rien ne l'ait décidé** — et il l'a fait
   jusqu'au 19 septembre 2026.

   La base est désormais ventilée. `part_droits_derives.csv` dit quelle
   fraction de la masse versée est une pension de réversion : 12,4 % en 2010,
   10,4 % en 2024, 9,5 % en 2040, 5,7 % en 2070 — la réversion recule dans la
   projection du COR, les carrières des femmes se rapprochant de celles des
   hommes. Le rapport ne multiplie plus que le reste.

   **Ce que le scénario fait de la réversion est maintenant une décision, et
   elle est écrite : seul le scénario 1 la sert.** Décision du Parti libéral,
   19 septembre 2026, et elle ne fait qu'appliquer à cette ligne la règle des
   trente-huit autres. Les scénarios 2 à 6 retirent tous les avantages non
   contributifs, et l'inventaire du dépôt range la réversion parmi eux depuis
   toujours : « non contributive au sens strict, la cotisation de l'assuré
   ayant déjà été rendue par sa propre pension », et « de très loin la
   PREMIÈRE dépense non contributive du système ». La servir dans un compte
   notionnel était l'exception non écrite, pas la règle ; ces cinq scénarios
   mesurent ce qu'une retraite composée uniquement de part contributive
   représente, et une réversion n'en est pas. C'est le chemin de la Suède, où
   un compte notionnel ne verse qu'à son titulaire. Celui de l'Italie, qui
   partage le capital du défunt, reste calculable sous
   `convention_reversion="servie"`.

   **Les cinq la retirent à tout le monde, et du même jour.** Les scénarios
   RÉTROACTIFS (2, 4, 6) recalculent toutes les pensions depuis 1941 : ils n'en
   servent jamais un euro. Les scénarios PROSPECTIFS (3, 5) sont, par
   construction, le système actuel jusqu'à leur bascule — ils y recopient ses
   pensions, et un test tient l'égalité de leurs courbes à l'euro près —, si
   bien qu'ils y servent sa réversion comme le reste ; à compter de la bascule
   ils ne la servent plus, aux veuves d'avant comme à celles d'après.
   `reforme_en_vigueur` porte ce seul basculement.

   Ce n'est pas le traitement que le modèle réserve aux autres avantages non
   contributifs dans les scénarios prospectifs : un minimum contributif servi à
   qui a liquidé en 2010 lui reste acquis pour toujours, parce que sa pension
   entière est recopiée. La réversion fait exception, et par décision : le
   programme a voulu qu'aucun scénario notionnel n'en verse à compter du jour
   où il s'applique.

   Ce que la décision rend : **+1,19 point de solde moyen 2026-2070 à chacun
   des cinq**, exactement le même chiffre. Ce n'est pas une coïncidence — la
   réversion retirée est une part de la BASE, qui ne dépend d'aucun rapport de
   masses, et les cinq la retirent sur la même fenêtre, celle qui commence à la
   bascule. Le scénario 1 ne bouge pas d'un iota, son
   rapport valant un, et un test l'exige. Le scénario 5 retrouve au passage
   l'équilibre dès la bascule et repasse au-dessus du système actuel, sa
   moyenne restant néanmoins négative.

   **Et la part est contrôlée chez un autre producteur.** Elle est construite à
   partir du classeur du COR, où douze des vingt-deux régimes publient leur
   droit dérivé à part — pour les dix autres, dont la fonction publique d'État
   et la CNRACL, c'est la différence entre la masse de prestations et le droit
   direct. La DREES, elle, ventile ses propres comptes en droit direct
   (`E11-21.1`) et droit dérivé (`E11-22.1`) depuis 2020. Deux enquêtes, deux
   périmètres, deux nomenclatures, cinq années communes : les parts s'écartent
   de **0,06 point au plus**, et de 0,01 point deux fois. C'est le seul
   contrôle externe dont cette série dispose, et il est bon.

   Ce qui reste : la part est très légèrement SURESTIMÉE pour les dix régimes
   sans bloc dédié, la différence prestations moins direct portant aussi un
   petit résidu de prestations qui n'est ni l'un ni l'autre — 0,3 % des
   prestations là où on peut le mesurer. Et hors de 2010-2070, la valeur de
   bord est reconduite au niveau `estimee` : la dépense observée remonte à
   1959, cette ventilation non.

5. **La grille ne monte pas au-delà de 2,5 fois le salaire moyen.** Le plus
   haut des treize cas types est la profession libérale, à 2,5 ; le
   simulateur, lui, accepte jusqu'à dix fois le salaire moyen. Toute règle qui
   ne mord qu'aux hauts revenus est donc INVISIBLE dans l'agrégat, et cela
   vaut dans les deux sens : ni la pension qu'elle ouvre, ni la cotisation
   qu'elle appelle. Le déplafonnement de l'assiette, décidé le 20 septembre
   2026 (action 61), en est la démonstration : il change la pension du
   simulateur de +12 à +14 % au-delà de neuf fois le salaire moyen, et il ne
   déplace ni le coût, ni le solde, ni un coefficient d'équilibre — mesuré à
   l'identique, au centime, sur les quatre systèmes et tout l'horizon. Ce
   n'est pas une propriété du déplafonnement : c'est que personne, dans la
   grille, ne gagne assez pour être concerné. La recette supplémentaire qu'un
   vrai déplafonnement apporterait n'est donc pas chiffrée ici, et la dépense
   supplémentaire non plus.

**Ce qui, en revanche, n'est pas une approximation** : l'égalité des scénarios
3 et 5 avec le système actuel sur toute la période observée. Elle est EXACTE, et
au sens strict — le scénario prospectif recopie la pension du scénario actuel
pour qui a liquidé avant la bascule. La page ne l'écrit pas en dur : elle teste
l'identité des courbes année par année, et les séparerait si la bascule était
avancée avant la dernière année publiée.

### Le troisième chiffre du simulateur : ce qu'il dit, et les quatre choses qu'il suppose

Depuis le 20 septembre 2026, chaque montant du simulateur porte à côté de lui
ce que les recettes du système en PAIENT, quand elles en paient moins que la
règle n'en promet. Le montant affiché reste celui de la règle — le scénario 1
est le droit en vigueur et rien d'autre, c'est sa définition —, et le troisième
chiffre est le même montant multiplié par le coefficient d'équilibre du
système, moyenné sur les années où la pension est servie et pondéré par la
survie. Sous lui, le manque EN EUROS : « il manque 393 € par mois » se compare
à un loyer là où « 87 % » ne se compare à rien.

Le dépliant qui l'explique a été écrit deux fois le même jour. La première
version ouvrait sur le coefficient d'équilibre et deux tableaux de nombres sans
dimension — 0,90 puis 0,87, des points d'assiette, des parts de PIB. Tout y
était vrai et rien n'y était lisible. Les trois leviers sont donc donnés dans
les unités où on les vit : rogner de 10 %, ou prélever 122 € de plus chaque
mois sur un salaire moyen, ou emprunter 44 milliards par an — et chacun est
présenté par QUI paie. Le tableau des coefficients est descendu d'un cran, sous
un dépliant, pour qui veut refaire le calcul. La conversion en euros suppose
deux choses, toutes deux écrites sur la page : le salaire moyen brut
d'aujourd'hui comme étalon de la hausse de cotisation — exact, le prélèvement
étant proportionnel —, et le PIB de la dernière année publiée pour dire un
manque de 2054 en milliards, parce qu'un PIB de 2054 serait une hypothèse de
croissance déguisée en observation.

Quatre choses s'y supposent, et aucune ne va de soi.

**Un facteur commun appliqué à toutes les pensions est UNE façon d'équilibrer
une année, pas une prévision.** Le Parlement peut aussi lever des cotisations,
reculer l'âge, ou laisser courir le déficit. Le dépliant chiffre les deux
premières branches à côté de la troisième, et le simulateur mesure la
quatrième : il suffit de changer l'âge de départ. Ce que les trois chiffres
disent ensemble, et qui est le seul fait, est la TAILLE de l'écart.

**La pondération par la survie n'est pas neutre, et elle joue dans le sens
doux.** Le manque grandit avec les années ; les années lointaines sont celles
où il reste le moins de monde pour le subir. Une moyenne pondérée par la survie
est donc plus haute qu'une moyenne simple, et un test le mesure plutôt que de
l'affirmer.

**Les comptes s'arrêtent en 2070, et le coefficient y baissait encore.** Pour
qui part après 2040, une partie du service n'est pas couverte — 40 % de la
rente pour un départ en 2054. Ces années-là ne sont pas prolongées : elles
sortent de la moyenne, la page dit quelle part elles pèsent, et la moyenne
affichée est donc un PLAFOND, les années écartées étant celles où le manque
serait le plus grand.

**La table est figée sous les réglages de référence.** Le coefficient est un
rapport de masses : le calculer suppose la grille des cas types simulée sous
chaque système, année par année, soit dix-huit secondes — ce que la page
d'entrée du site ne peut pas payer chez le lecteur. Elle lit donc une table
écrite une fois par `scripts/construire_donnees.py`, versionnée dans
`data/derive/equilibre.json` et embarquée dans le paquet du navigateur. Pour le
système actuel, cela ne coûte rien : son coefficient est le rapport des
ressources aux dépenses que le COR publie, et aucun réglage ne le déplace. Pour
les trois autres, la dépense est une masse de pensions notionnelles, qui bouge
avec la règle d'indexation ou la table de mortalité : les coefficients affichés
sous le simulateur sont ceux des réglages de référence, la page le dit, et la
page Coût les recalcule sous les réglages qu'on lui demande.

**Enfin, un coefficient supérieur à un n'est jamais converti en euros.** Les
systèmes 2 et 3 encaissent deux à trois fois ce qu'ils versent, parce qu'ils ne
versent presque rien : écrire « vraiment payé : 927 € » sous une pension de
265 € ferait promettre au lecteur une pension que personne n'a décidé de
servir. La marge est dite en toutes lettres — « les recettes couvrent ce
montant 2,6 fois » —, jamais chiffrée en montant.

**Une difficulté tenue plutôt que masquée**, la même écriture l'ayant fait
apparaître : les trois leviers sont chiffrés à l'année du départ, où ils
partagent un dénominateur et se déduisent l'un de l'autre, quand le troisième
chiffre moyenne toute la durée de la retraite et se trouve donc plus sévère —
13 % là où l'année du départ en donne 10. La page l'écrit, et ne donne le
manque en euros qu'à un seul endroit, sous le chiffre, pour que deux sommes
voisines ne se disputent pas le même rôle.

---

### Le stock : ce que le dépôt en montre, et ce qu'il ne calcule pas

Tout ce que le site montre du système de retraite est un **flux** : ce qui
rentre et ce qui sort dans l'année, rapporté au PIB de l'année. C'est la moitié
d'un compte. L'autre moitié est ce que le système **doit déjà**, au titre des
droits que les vivants ont acquis — et elle manquait, ce qui est le comble pour
un modèle en comptes notionnels, où ce stock est par définition la somme des
capitaux virtuels.

**Ce qui est publié.** Le règlement (UE) n° 549/2013 fait transmettre, tous les
trois ans, un tableau supplémentaire sur les retraites. Son poste central est
`F63_LE`, les droits à pension dans le bilan de clôture. Pour la France :
**368 % du PIB en 2015, 431 % en 2018, 397 % en 2021**, presque intégralement
par répartition. `engagements_retraite.csv` les porte depuis le 20 septembre
2026, et la page Coût les affiche à côté de ses flux.

**Ce qu'on en retient, et rien de plus.** L'ordre de grandeur : près de quatre
années de production d'engagement, contre quatorze pour-cent de PIB de dépense
annuelle. Un système de retraite porte environ trente fois son flux d'une année.
C'est ce qui rend absurde l'idée qu'un tel système se solde comme un budget
annuel, dans les deux sens : on ne peut ni l'éteindre par une économie de flux,
ni le déclarer insoutenable parce qu'un flux manque.

**Et l'écart entre les trois transmissions est la seconde information.**
Soixante-trois points de PIB en trois ans, puis trente-quatre dans l'autre sens.
Ce ne sont pas des droits qui apparaissent et disparaissent : un droit acquis à
date est une somme **actualisée**, et son niveau dépend d'un taux
d'actualisation et d'hypothèses de revalorisation qui bougent d'un exercice à
l'autre bien plus que les droits eux-mêmes. C'est la faiblesse connue de cet
exercice, la raison pour laquelle le tableau est publié **à part** des comptes
principaux, et pourquoi personne ne le porte au bilan des administrations. Le
dépôt le montre pour dire que le stock existe et qu'il est grand ; jamais comme
une dette.

**Et le dépôt calcule le sien, depuis le 20 septembre 2026.** Le taux
d'actualisation n'avait pas à être décidé : **le COR en publie un**. La note de
sa figure du solde moyen — celle que le décret n° 2014-654 relatif au Comité de
suivi des retraites encadre — dit que « le taux d'actualisation est supposé égal
chaque année à la croissance annuelle du PIB ». Or actualiser au rythme du PIB
revient à **sommer les flux exprimés en part de PIB** : le facteur
d'actualisation et le dénominateur se simplifient exactement. L'unité de tout le
dépôt portait donc déjà l'actualisation, et l'engagement est la somme, année par
année, de ce que les droits acquis feront verser, chacun rapporté au PIB de son
année.

**Ce que le modèle trouve**, à la dernière date qu'Eurostat transmette :

| | Part du PIB en 2021 |
|---|---|
| Système actuel, convention du COR | **579 %** |
| — dont retraités (pension entière acquise) | 231 % |
| — dont actifs, au prorata de la carrière faite | 347 % |
| Proposition (système 6) | 370 % |
| Notionnel part salariale (système 2) | 162 % |
| Publié par Eurostat, tableau 29 | 397 % |

La proposition doit moins parce qu'elle promet moins : c'est la même règle qui
fait baisser ses pensions et son engagement, et le rapport des deux est à peu
près celui des masses.

**L'écart avec le chiffre publié est un TAUX, pas un droit.** Les mêmes droits,
actualisés **deux points de plus par an**, valent exactement les 397 %
d'Eurostat. Ni l'un ni l'autre n'est faux : un engagement acquis n'a pas de
niveau propre, il a un taux. C'est la même démonstration que les soixante points
d'écart entre deux transmissions, faite cette fois de l'intérieur, et c'est
pourquoi la page affiche les deux sans choisir.

**Trois conventions à connaître.** Le **prorata temporis** : un actif qui a fait
les trois quarts de sa carrière a acquis les trois quarts de sa pension. C'est
celle du tableau 29 pour les régimes à prestations définies, et surtout c'est UNE
convention appliquée aux six systèmes, ce qui est la condition pour que leurs
engagements se comparent. Un compte notionnel donnerait la sienne sans
approximation — le capital virtuel EST le droit acquis — mais elle ne vaudrait
que pour cinq des six, et l'étalon serait hors du tableau. Ensuite,
l'**extrapolation au-delà de 2070** : l'INSEE ne projette pas la pyramide plus
loin, et les cohortes déjà nées y sont prolongées par la table de mortalité du
dépôt, la même qui sert de diviseur aux comptes notionnels. Elle ne porte que
**35 points sur 579**, soit six pour cent : le résultat ne dit donc pas d'abord
une table de mortalité, et un test borne cette part. Enfin, la table est **figée
sous les réglages de référence**, comme le reste du bilan, parce que sommer
quatre-vingts années de flux ne peut pas se faire chez le lecteur.

**Ce qui reste.** L'engagement du dépôt hérite de tout ce que sa trajectoire
suppose — treize carrières, une grille de générations au pas de cinq ans, et une
dépense projetée plus haute que celle du COR (§ 5 ter). Il ne remplace pas le
tableau 29 : il dit ce que le modèle doit, sous une convention nommée, et ce que
cette convention vaut.

**Et ce n'est pas la dette que la page montre déjà.** `Dette` accumule les
SOLDES À VENIR, avec intérêts, à partir de zéro : ce que les déficits
projetés ajouteraient. Les droits acquis à date sont autre chose — ce qui est
dû aujourd'hui pour le passé, indépendamment de ce que l'avenir cotisera. Les
deux grandeurs répondent à deux questions, et les additionner n'aurait aucun
sens.

### Le compte est en brut, et une part de sa recette sort de sa dépense

Deux choses que la page Coût affichait sans les dire, et qui ne se voient pas
en lisant « dépenses » et « ressources ».

**Le compte est en BRUT, des deux côtés.** Les pensions comptées sont celles
qui sont versées, avant contribution sociale généralisée, CRDS et CASA. Au taux
plein, ces trois-là prélèvent 9,1 % : la masse des pensions vaut 13,68 % du PIB
en 2024 en brut, et **au plus 12,43 % en net**. « Au plus » est la seule forme
honnête : l'article L. 136-8 exonère les pensions modestes et en soumet d'autres
à un taux réduit, selon le revenu fiscal de référence du foyer, que personne ne
publie par tranche de pension. Le dépôt applique déjà le taux plein à tout le
monde dans le simulateur, et dit ce que cette convention coûte (§ 5 ante ter) ;
à l'échelle du compte, elle ne peut donner qu'une borne.

Cela n'affecte pas le SOLDE, dépenses et ressources étant l'une et l'autre
brutes, mais cela affecte la comparaison : « 13,9 % du PIB » se compare souvent,
dans le débat, à des dépenses publiques nettes, et n'est pas la même grandeur.

**Et une part de la recette est prélevée sur la dépense.** L'article L. 131-8,
3° e affecte 2,94 des 8,30 points de CSG d'une pension à la branche vieillesse :
**un tiers de ce qu'une pension paie revient au système qui la verse**. Au taux
plein, cela fait au plus 11,8 Md€ en 2024, soit 0,40 point de PIB et le
cinquième des impôts et taxes affectés que le compte encaisse. Le COR ne se
trompe pas en portant les deux flux — un compte d'encaissements le doit, et la
comptabilité nationale aussi — mais qui lit les deux colonnes comme deux
grandeurs indépendantes se trompe de cette somme.

Ce que cela vaut pour les scénarios notionnels : ils retirent les impôts et
taxes affectés en entier (§ 5 bis), donc cette CSG avec, et la circularité
disparaît avec elle. C'est cohérent, et ce n'est pas un hasard : un compte
notionnel ne crédite que ce qui est assis sur un revenu d'activité, et une CSG
sur pension n'en est pas un.

**Ce qui reste hors de portée.** La borne est haute des deux côtés parce que le
taux plein est appliqué à toute la masse. La chiffrer juste demanderait la
distribution des pensions CROISÉE avec le revenu fiscal du foyer : la DREES
publie la première (`distribution_pensions.csv`, déjà dans le dépôt), personne
ne publie le croisement. Une enquête Revenus fiscaux et sociaux le permettrait,
et elle n'est pas ici.

### La convention comptable : le déficit affiché est d'APRÈS bouclage

Le compte du COR est tenu sous une convention, et le dépôt la stockait depuis
toujours dans l'en-tête de `comptes_retraite.csv` sans jamais la dire au
lecteur. Elle décide pourtant de ce que « déficit » veut dire.

**Ce que la convention EPR fait.** Sous « équilibre permanent des régimes », les
contributions et subventions d'équilibre « évoluent de manière à équilibrer
chaque année le solde » des régimes de fonctionnaires et des régimes spéciaux
— c'est la note du COR, mot pour mot. Ces régimes ne montrent donc **jamais**
de déficit : l'État y verse exactement ce qu'il faut, par construction. Le
−2,4 points de PIB que le site affiche pour 2070 est le déficit de ce qui
RESTE, une fois la fonction publique et les régimes spéciaux bouclés. Ce n'est
pas un artefact, c'est une convention, et le COR la retient parce que c'est sous
elle qu'il suit son objectif de pérennité financière. Mais un lecteur qui ne
la connaît pas lit le chiffre pour ce qu'il n'est pas.

**Ce que l'autre convention donne, et pourquoi elle surprend.** Le COR publie
aussi l'« effort de l'État constant » (EEC), où sa contribution est figée en
part de PIB, en données complémentaires de la figure des ressources
(`ressources_eec_retraite.csv` depuis le 20 septembre 2026). On s'attend à ce
qu'une hypothèse nommée « effort constant » soit plus sévère. Elle ne l'est pas,
et pas non plus l'inverse : **l'écart change de signe.** L'assiette de cotisation
des trois fonctions publiques recule de 10,4 % du PIB à 8,9 % sur l'horizon —
moins de fonctionnaires, et des primes qui montent plus vite que le traitement
indiciaire — si bien que le besoin de ces régimes recule aussi. L'effort figé
est donc SOUS le besoin tant qu'ils pèsent, et au-dessus ensuite :

| | EPR (ce que le site calcule) | EEC | écart |
|---|---|---|---|
| 2028 | −0,24 % du PIB | −0,91 % | −0,67 pt |
| 2047 | croisement | | 0,00 pt |
| 2069 | −2,35 % | −1,86 % | +0,49 pt |

Sur 2026-2069, les deux moyennes ne diffèrent pas de deux centièmes de point.
**Aucune des deux ne flatte** : l'une creuse le déficit de demain, l'autre celui
d'après-demain, et l'État n'a promis ni l'une ni l'autre. Le dépliant « D'où
viennent ces chiffres » de la page Coût le dit maintenant, chiffres compris, et
un contrôle du catalogue des affirmations tient les trois nombres ainsi que
l'année de croisement, qui est calculée et non écrite.

**Ce que ça ne règle pas.** Le dépôt CALCULE toujours sous EPR, et les scénarios
notionnels héritent donc de ressources dont une part est un solde endogène :
la contribution d'équilibre de l'État vaut 11,7 % des ressources, et les
scénarios 2 à 5 la reconduisent telle quelle alors qu'elle n'existe que pour
boucler un régime qu'ils remplacent. Le scénario 6, lui, la supprime et la
remplace par ses 18 % sur les traitements (§ 5 bis, `ressources_de`). Rendre les
quatre autres cohérents demanderait de décider ce que l'État verserait sous
chacun, ce que le programme ne dit pas.

### L'assiette projetée : une déduction que le COR démentait, et un demi-point de PIB

La recette de la proposition est un taux appliqué à une assiette : 18 % des
revenus d'activité. Sur les années où l'assiette est publiée, c'est une mesure.
Au-delà, il faut dire ce que l'assiette devient, et la réponse n'est pas mince —
elle vaut, à l'horizon, un demi-point de PIB de recette.

**Ce que le dépôt supposait, et pourquoi c'était faux.** Les ressources que le
COR projette reculent en part de PIB : 13,95 % en 2025, 12,91 % en 2070. Ce
recul se partage entre un taux de prélèvement qui baisse et une assiette qui
rétrécit, et les deux colonnes du compte ne disent pas lequel. Jusqu'au
20 septembre 2026, le dépôt reconduisait le taux du bord et faisait donc porter
tout le recul à l'assiette, qui tombait de 42,5 % du PIB à **39,3 %** en 2070.
Il s'en justifiait ainsi : « c'est le COR qui tranche : ses ressources reculent
en part de PIB parce que l'assiette y progresse moins vite que le PIB, et non
parce qu'il baisserait les taux ».

C'était une déduction tirée du TOTAL de ses ressources, et non une lecture de sa
projection. Deux choses la démentaient, dont une dans le dépôt même :
`hypotheses_projection.yaml` écrit que le PIB projeté suit la masse salariale,
« supposer autre chose reviendrait à projeter une déformation du partage de la
valeur ajoutée, ce qu'aucun des scénarios retenus ne fait » — et une assiette qui
passe de 42,5 à 39,3 % du PIB est exactement cette déformation, de 7,4 %. Le
dépôt se contredisait d'un fichier à l'autre.

**Ce que le COR publie.** La figure « Les déterminants de l'évolution des
ressources du système de retraite », partie 2 du rapport annuel, porte le taux de
prélèvement en part des revenus d'activité, observé de 2002 à 2025 et projeté
jusqu'en 2070. Il **baisse** : 32,14 % en 2025, 30,05 % en 2070. C'est donc le
taux qui explique le recul des ressources, et l'assiette tient sa part de PIB à un
point près. La série est lue depuis le 20 septembre 2026
(`taux_prelevement_retraite.csv`), et un test refuse désormais que l'assiette
implicite s'écarte de plus d'un point et demi de PIB de sa dernière mesure.

**Le profil, jamais le niveau.** « Revenus d'activité » chez le COR n'est pas
tout à fait l'assiette d'`assiette_activite.csv` — salaires et traitements bruts
plus revenu mixte des ménages —, et les deux taux diffèrent de 2 % en 2025 :
32,14 % contre 32,84 % mesuré ici. Le dépôt garde sa mesure pour l'année
d'ancrage, la seule qu'il certifie, et n'emprunte au COR que le RAPPORT d'une
année projetée à celle-là. Emprunter le niveau aurait déplacé la recette de 2 %
sans que rien ne le dise.

**Ce que la correction déplace.** Le solde de la proposition gagne **0,49 point
de PIB en 2070** et 0,28 en moyenne sur 2026-2070 : le solde moyen projeté passe
de −1,52 à −1,24 point, et l'année 2070 de −0,63 à −0,14, son coefficient
d'équilibre de 0,92 à 0,98. Les années proches bougent à peine, et l'une d'elles
dans l'autre sens — le COR fait légèrement MONTER son taux jusqu'en 2030, et la
recette de 2030 baisse donc de trois millièmes de point. C'est ce qu'il faut
attendre d'une série lue plutôt que supposée : elle ne va pas toujours dans le
sens qui arrange. Aucune pension ne bouge, les 469 témoins de simulation sont
identiques au bit près ; ce qui bouge est la part de ces pensions que les
recettes financent.

**Ce qui reste.** Le taux du COR est projeté sous SA convention EPR et sous son
scénario de référence : c'est un cadre, pas une prévision. Et il décrit le
système ACTUEL — un système à 18 % n'aurait pas la même assiette, les
exonérations, les plafonds et les tranches qu'il supprime déplaçant ce sur quoi
l'on prélève. Le dépôt emprunte la forme de la trajectoire à défaut de savoir
produire la sienne, et c'est une hypothèse de plus, énoncée ici.

---

## 5 ter. La trajectoire projetée : ce qu'elle suppose, et ce qu'elle vaut

La seconde moitié de la page **Coût** projette les six systèmes de 2025 à 2070.
Rien n'y est certifié, rien ne peut l'être, et le lecteur doit savoir sur quoi
chaque chiffre repose.

**Ce qui n'est pas de nous.** La démographie est celle du scénario central des
projections de population 2026 de l'INSEE : effectifs par âge de 1962 à 2070,
observés jusqu'en 2023. C'est cette source qui fixe l'horizon de la page — 2070
et pas 2080 — et non une préférence du dépôt. L'INSEE publie seize autres
scénarios ; leur écart mesurerait l'incertitude démographique, que cette page ne
montre pas. Les hypothèses macroéconomiques sont celles du COR, déjà décrites
dans `data/reference/macro/hypotheses_projection.yaml`.

**Ce qui est de nous, et qui se discute.** Le PIB projeté suit le rythme nominal
du COR — 2,45 % par an dans le scénario de référence — **composé avec sa
trajectoire d'emploi**, qui recule de 6 % d'ici 2070. C'est la convention que
`hypotheses_projection.yaml` énonce pour tout le dépôt (« le PIB nominal suit la
même convention que la masse salariale »), et c'est la même série que lit
l'indexation des comptes : la page n'a plus de PIB à elle.

Elle en avait un jusqu'au 20 septembre 2026, et c'était le paramètre le plus
discutable de la section : le rythme du COR corrigé par la **population des
20-64 ans**, qui recule de 10 % là où son emploi recule de 6 %. Ce proxy avait
été posé contre une hypothèse d'emploi constant, qui aurait prêté à la France de
2070 douze pour cent d'actifs qu'aucune projection ne lui donne ; l'hypothèse a
disparu le même mois (action 46), le proxy lui a survécu quelques jours, et le
dépôt a porté pendant ce temps TROIS PIB projetés — celui-ci, celui de
l'indexation, et celui qu'implique le compte du COR. Une part de PIB dont le
dénominateur n'est pas celui du reste du dépôt ne se compare à rien. La
substitution rend 1,05 point : la trajectoire 2070 passe de 19,4 à **18,35 %**,
et c'est du dénominateur seul — aucune pension ne bouge.

**Ce que la substitution laisse ouvert.** Le PIB reste UNIQUE PAR ANNÉE, commun
aux six systèmes. C'est ce qui rend les six courbes comparables, et c'est aussi
une hypothèse : la trajectoire d'emploi ne s'applique qu'aux systèmes 2 à 6
(action 46, « un emploi qui bouge sous la réforme, pas sous le droit constant »),
alors que le PIB qu'elle produit sert de dénominateur aux six. Un système qui
déplacerait réellement l'emploi déplacerait son propre dénominateur, et la page
ne sait pas le montrer.

**Ce qui n'est pas modélisé.** Le taux de couverture est supposé constant : le
modèle compte des générations, non des cotisants, et suppose que la même
proportion de chacune perçoit une pension et que la carrière type ne change pas.
Un recul de l'âge effectif de départ, une carrière plus longue ou plus hachée
déplaceraient la trajectoire. Aucune règle de pilotage n'est appliquée non plus :
un système notionnel réel porte un coefficient d'équilibre qui ajusterait toutes
ses pensions par un même facteur — commun, donc sans effet sur les écarts entre
carrières, mais avec effet sur les courbes de cette page. Ce coefficient est
désormais CALCULÉ, section « Le solde, et non le coût » de la même page, à
partir des ressources que le COR publie ; il n'est toujours pas appliqué, et le
§ 5 dit ce que cette distinction coûte.

**Ce que le pas de la grille laisse passer.** Une génération sur cinq est
simulée, et chacune représente les cinq classes d'âge qui l'entourent, décalées
d'un an à deux ans, chacune liquidant sa propre année. Une cohorte qui part
juste avant la bascule est donc représentée par une génération qui part juste
après, et hérite de son traitement : les courbes prospectives s'écartent de la
courbe actuelle d'un à deux dixièmes de pour cent avant même la bascule. Le
résidu est mesuré et un test le borne à un demi-point. Le pas commande le temps
de calcul de la page ; il ne doit pas commander la forme du résultat, et c'est
pourquoi les cinq cohortes ne basculent pas le même jour — sans quoi la
trajectoire avancerait par marches de cinq ans.

**Le contrôle externe, et ce qu'il dit.** Le COR projette la même grandeur avec
un modèle de population complet et une méthode qui n'a rien de commun avec
celle-ci : il trouve 13,9 % du PIB en 2024 et **15,3 % en 2070** (rapport annuel
de juin 2026, champ « ensemble des régimes légalement obligatoires, y compris
FSV, hors RAFP »). Le dépôt trouve 13,6 % et **18,35 %**. Trois dixièmes de point
d'écart au départ — l'affaire du périmètre, la répartition obligatoire des
Comptes de la protection sociale n'étant pas exactement celle du COR — et **trois
points à l'arrivée**.

Cet écart d'arrivée valait cinq points jusqu'au 20 septembre 2026 ; un point en
était un effet de DÉNOMINATEUR, et non de dépense — la page rapportait sa
dépense à un PIB qu'elle se fabriquait, plus petit que celui du COR de 4 % en
2070. Ce qui suit décrit les quatre points qui restaient alors, et dont trois
restent.

L'écart d'arrivée a une histoire, et elle vaut d'être lue dans l'ordre : deux
points tant que les cas types pesaient d'un poids égal, quatre quand chacun a
reçu l'effectif de sa caisse, cinq depuis que chacun liquide à l'âge de sa
génération. Il s'est creusé deux fois en corrigeant deux défauts, et les deux
fois pour la même raison de fond : une erreur en cachait une autre.

**Ce que la pondération a retiré.** Une COMPENSATION ACCIDENTELLE. L'ancienne
convention égalitaire donnait un sixième du poids à des carrières qui liquident
à 52 et 57 ans — SNCF, catégorie active —, si bien que le stock de retraités du
modèle vieillissait moins vite que la seule population des 64 ans et plus,
laquelle croît de 41 % d'ici 2070 quand celle des 52 ans et plus ne croît que de
25 %. En rendant à chaque carrière son poids réel, on a rendu visible ce que le
modèle faisait depuis toujours : il faisait liquider chaque cas type à l'âge
légal d'aujourd'hui, quelle que soit sa génération.

**Ce que l'âge de liquidation a retiré, et le diagnostic qu'il a démenti.** Ce
défaut-là est corrigé : un cas type ne porte plus un âge mais une RÈGLE, et
chaque génération liquide sous le droit qui était le sien — au taux plein pour
la plupart, à l'âge que leur statut ouvre pour la catégorie active, l'agent de
conduite et l'agent des IEG, à une durée de services pour le militaire. Une
génération née en 1940 ne part plus à 64 ans en 2004 : le salarié au salaire
moyen part à 60 ans et 3 mois, le cadre à 62 ans et 3 mois, l'agent de conduite
à 50 ans — et la génération 2000, embauchée après la fermeture du statut SNCF,
part à 64 ans au régime général comme le droit l'y oblige.

**La feuille de route tenait ce défaut pour la principale cause des quatre
points d'écart. La mesure dit le contraire, et c'est le résultat de l'action.**
Le diagnostic était juste sur le défaut et faux sur son SENS : la trajectoire
2070 passe de 18,3 à 19,3 % au lieu de redescendre vers 14,2. La raison est
lisible dans la grille des âges : les générations d'après 1970 liquidaient DÉJÀ,
sous l'ancienne convention, à peu près à l'âge que le droit leur ouvre —
soixante-quatre ans est l'âge de la loi de 2023, écrit dans la grille parce
qu'il est celui d'aujourd'hui. La correction a donc surtout déplacé les
générations ANCIENNES, celles qui font 2024, et à peine celles qui font 2070.
Elle fait même monter ces dernières, parce que les cas types dont un statut
commande le départ partent plus tard qu'avant à mesure que les réformes relèvent
leur âge — cinquante-neuf ans en catégorie active, cinquante-quatre à la
conduite — et qu'une carrière plus longue donne une pension plus forte.

**Ce qui reste, et où chercher.** Ce n'est donc pas l'âge de départ. Le candidat
que le dépôt peut MESURER chez lui est le taux de remplacement : celui du
salarié au salaire moyen, à sa liquidation, vaut 51,3 % pour la génération 1970
et 50,9 % pour celle de 2000 — il ne bouge pas. Le COR, lui, projette un recul
sensible du rapport entre la pension moyenne et le revenu d'activité moyen, que
produisent l'indexation des pensions sur les prix et celle des salaires portés
au compte. Un modèle dont le taux de remplacement ne recule pas dépense
mécaniquement plus, à démographie identique. C'est une piste et non une
conclusion : la vérifier demanderait de confronter la pension moyenne du modèle
à celle que le COR projette, série contre série, ce que cette section ne fait
pas.

La concordance ne vaut de toute façon que ce que vaut une concordance : elle
rend une erreur grossière improbable, elle ne rend juste aucun des deux modèles.
Un test borne la trajectoire à la fourchette 10-20 % du PIB. Cette borne n'a pas
bougé — elle avait été élargie de 18 à 20 % lors de la pondération, et les
19,4 % y tiennent encore de six dixièmes de point.

**Ce que la règle d'âge a déplacé ailleurs.** Deux choses, et toutes deux
attendues une fois qu'on sait que les cas types partent plus tard. La garantie
vieillesse du scénario 6, servie à 65 ans, n'était vue que par un cas type sur
treize ; elle l'est maintenant par cinq aux générations récentes, et la masse
que la grille en tire passe de 0,5 à 9,4 milliards par an — toujours la moitié
de ce que le barème coûte sur la vraie distribution, et le § « Le scénario 6, et
ce que sa garantie ne voit pas » dit pourquoi cet écart-là ne se comblera pas.
Et les 469 témoins de simulation n'ont pas bougé d'un bit : la règle date un
départ, elle ne touche à aucune formule de pension.

**Ce que la règle a appris depuis, et ce qu'elle ne sait toujours pas faire.**
Elle connaît maintenant la carrière longue — le salarié au SMIC, entré à
dix-huit ans, part à 60 ans pour les générations 1955 et 1960 et à 62 ans
depuis la loi de 2023, et le moteur confirme le motif — et les trimestres pour
enfants, qui datent la carrière interrompue à l'âge légal de sa génération au
lieu d'un départ en surcote (§ « Écarts avec le droit positif »). La
trajectoire 2070 en est montée de 19,3 à 19,5 % : deux cas types partent plus
tôt, et c'est le droit. La suspension de 2026 la ramène ensuite à 19,4 % : les
générations 1964 à 1970 partent un trimestre plus tôt, avec un ou deux
trimestres de moins à réunir. Ce qu'elle ne sait toujours pas faire : les âges
d'entrée des cas types restent ceux de la grille — vingt-quatre ans pour
l'artisan, vingt-sept pour le libéral —, ce qui suffit à les faire partir à
soixante-sept ans une fois la durée requise opposée. On en déduisait que la
grille partait, en moyenne, un peu plus tard que la France réelle, et que
l'âge conjoncturel de départ publié par la DREES permettrait de le chiffrer.

**Il est maintenant dans le dépôt, et la déduction était fausse.**
`data/reference/macro/age_conjoncturel_depart.csv` porte la série de la DREES,
2004 à 2022, par sexe — l'indicateur synthétique, les taux de liquidation par
âge de l'année appliqués à une génération fictive, donc indépendant de la
pyramide des âges, ce qui est la seule raison pour laquelle il se compare à une
grille. `scripts/age_conjoncturel.py` fait la comparaison : pour chaque année,
l'âge auquel chaque cas type part, interpolé entre les points de la grille, et
les treize pesés par les effectifs de caisse de la page « Coût ».

**La grille suit l'âge réel à moins d'une demi-année sur dix-neuf ans**, et
l'écart moyen est de −0,02 an — elle part un peu plus TÔT, non plus tard. Ce
n'est pas une validation de la grille comme échantillon, qu'elle n'est pas :
c'est que ses départs, pris ensemble et pesés, tombent où tombent ceux de la
France réelle. Le tableau complet est celui que le script imprime ; ses deux
bords disent l'essentiel : +0,30 an en 2010, −0,45 an en 2022.

**Le défaut que la mesure trouve n'est donc pas celui qu'on cherchait.** Il est
dans la PENTE des années récentes : jusqu'au début des années 2010 la grille
partait plutôt plus tard, et depuis 2015 l'âge réel monte plus vite qu'elle —
+2,09 ans de 2004 à 2022 pour la DREES, +2,00 pour la grille, et tout l'écart
se creuse après 2015. La grille ne connaît que ce que le droit ouvre ; la
montée récente doit une part au comportement, qu'aucun cas type ne choisit.
C'est une piste pour la trajectoire, et non une conclusion : une demi-année de
départ plus tard ne referme pas quatre points de PIB.

Quatre réserves tiennent la mesure, écrites en tête de `age_conjoncturel.py` :
les poids sont des stocks de retraités et non des flux de liquidation, faute
que le dépôt ait les seconds ; la grille reste treize configurations et non une
population ; l'âge de la DREES est un comportement sous contrainte quand celui
de la grille est mécanique ; et le sexe n'est pas comparé, la grille ne
distinguant pas ses cas types par sexe.

**La cinquième réserve a été levée, et c'est elle qui comptait : une
concordance d'ensemble ne juge que la somme.** Treize cas types dont l'un
partirait deux ans trop tard et l'autre deux ans trop tôt la donneraient tout
aussi bien. La DREES publie le même indicateur ventilé par catégorie
socioprofessionnelle — `data/reference/macro/age_depart_csp.csv`, 2013 à 2020,
six groupes plus la ligne « toutes CSP » —, et
`data/reference/macro/cas_types_csp.yaml` écrit, cas type par cas type, à
quels groupes il se compare et pourquoi. `scripts/age_depart_csp.py` fait la
confrontation.

**Les écarts individuels valent 1,17 an, et ils se compensent.** Pesés comme
sur la page « Coût », les huit cas types comparables s'écartent de 1,17 an en
valeur absolue et de +0,46 an seulement en signé, là où le tous régimes donne
−0,02 an sur la même fenêtre. La concordance d'ensemble n'était donc pas un
accord cas par cas : c'est une compensation, à laquelle s'ajoutent les quatre
cas types laissés hors champ — militaire, agent de conduite, agent des IEG,
catégorie active —, qui pèsent 8,3 % de la grille et partent entre 44,0 et
56,6 ans.

| Cas type | Grille | Couloir des catégories | Écart |
|---|---:|---:|---:|
| Agent contractuel de la fonction publique | 64,92 | 61,24 – 62,59 | **+2,34** |
| Artisan | 64,92 | 62,84 | **+2,09** |
| Fonctionnaire sédentaire (catégorie B) | 63,21 | 61,24 | **+1,97** |
| Salarié au SMIC, carrière complète | 60,00 | 61,59 – 61,95 | **−1,59** |
| Cadre du privé | 64,07 | 62,59 | +1,48 |
| Chef d'exploitation agricole | 61,73 | 62,85 | −1,12 |
| Salarié au salaire moyen | 62,33 | 61,24 – 61,95 | +0,38 |
| Carrière interrompue | 61,64 | 61,24 – 61,95 | 0,00 |

Un seul cas type sur huit tombe dans son couloir. **Le sens des écarts est
cohérent, et il désigne l'âge d'entrée** : les trois qui partent le plus tard —
le contractuel et l'artisan entrent à vingt-quatre ans, le cadre à
vingt-trois — sont ceux dont la fiche impose une entrée tardive, et qui doivent
donc attendre la durée requise ; le salarié au SMIC, entré à dix-huit ans, part
au contraire à soixante ans tout du long, plus tôt que n'importe quel groupe.
C'est exactement le mécanisme que la section supposait, et il est bien là : il
ne se voyait pas parce qu'il se compense.

**Ce que cette erreur coûte : rien, sur ce que le site compare.**
`scripts/cout_age_depart.py` fait le contrefactuel. Pour chacun des neuf cas
types comparables, il cherche l'âge d'entrée qui rapproche le plus son départ
du couloir de sa catégorie — l'âge d'entrée, parce que c'est la cause que
cette section désigne —, rebâtit la grille avec ces âges-là et relance le
calcul du coût. Six cas types se déplacent ; l'artisan entre à 21,5 ans au
lieu de 24, le contractuel à 21 au lieu de 24, le salarié au SMIC à 20 au lieu
de 18.

**Les cinq scénarios notionnels ne bougent pas** : moins d'un dixième de point
de PIB en 2070, de −0,03 à +0,03. L'erreur d'âge leur est invisible, et la
raison est dans le mécanisme — dans un compte notionnel, partir plus tôt
allonge le diviseur autant que la carrière raccourcie retire au capital, et les
deux termes se répondent. C'est la raison chiffrée de ne réécrire aucune fiche
pour ce que le site argumente.

**Le système actuel bouge, et dans le mauvais sens** : 18,35 % du PIB en 2070
sous les fiches, 18,96 % sous le contrefactuel. L'écart avec la projection du
COR passe de 4,15 à 4,76 points — corriger les âges ÉLOIGNE le modèle du COR
au lieu de l'en rapprocher. **L'âge de départ n'explique donc pas l'écart que
cette section laisse ouvert**, et la piste du taux de remplacement reste
entière. Une réserve sur ce +0,61 point : déplacer l'âge d'entrée déplace aussi
la DURÉE de carrière, et le chiffre mêle les deux effets — c'est d'ailleurs la
durée qui domine, puisque cinq des sept cas types déplacés entrent PLUS TÔT.

**Et les deux critères d'âge tirent en sens contraire.** Sous la grille
corrigée, l'écart à l'âge conjoncturel tous régimes passe de −0,07 à −0,55 an :
rapprocher chaque cas type de SA catégorie éloigne leur SOMME. Les deux ne
peuvent pas être satisfaits ensemble. Le suspect est le groupe des quatre cas
types hors champ — un douzième de la grille, à des âges de 44,0 à 56,6 ans —,
dont le poids ou l'âge devrait alors être faux ; mais la mesure tient le
constat et ne tranche pas son explication, les deux sources ne décrivant pas la
même population.

**Deux raisons font de ce contrefactuel une borne basse**, écrites en tête du
script. Les quatre cas types hors champ ne sont pas touchés ; et un couloir
réduit à une seule catégorie est un POINT, qu'un pas d'une demi-année n'atteint
pas — le résidu subsiste, de 0,12 à 0,30 an pour trois cas types. Elles étaient
TROIS jusqu'au 21 septembre 2026, la troisième disant que deux cas types ne
répondaient pas à leur âge d'entrée ; c'était un défaut du moteur, et il est
corrigé — les huit cas types comparables y répondent tous.

**Une carrière tout en points ne se voyait rien opposer.** C'est ce que la
recherche d'âge d'entrée a fait voir, et le défaut avait trois faces. Toutes
trois ont la même cause : le moteur ne lisait la durée requise, l'âge
d'ouverture opposable et la carrière longue que sur les périodes en ANNUITÉS,
et une carrière entière en points n'en a aucune. Les deux cas types concernés
sont le chef d'exploitation agricole (MSA non-salariés, RCO) et la profession
libérale (CNAVPL, Cipav).

**Première face : le taux plein sans l'avoir.** Elle était plus précise que
« la décote manque » : le coefficient de réduction était DÉJÀ appliqué —
`_abattement_points` lit la décote de la fiche —, mais la règle qui DATE le
départ ne le voyait pas. `age_taux_plein_droit` rendait l'âge d'ouverture dès
que la carrière n'avait aucune période en annuités, si bien que le modèle
faisait liquider « au taux plein » des carrières qu'il servait minorées : le
libéral né en 1955 partait à soixante-quatre ans avec cent quarante-huit
trimestres sur cent soixante-six requis, soit dix-huit trimestres de réduction
que la règle disait inexistants.

Le droit oppose bien cette durée aux régimes en points, et les deux articles le
disent : **L. 643-3 I du code de la sécurité sociale** pour les professions
libérales — la pension vaut « le produit de la valeur du point par le nombre de
points acquis » quand l'assuré a « la durée d'assurance fixée en application du
deuxième alinéa de l'article L. 351-1 dans le présent régime et dans un ou
plusieurs autres régimes », et un décret « fixe les coefficients de réduction
[…] lorsque l'intéressé ne justifie pas de la durée » — et **le II de l'article
L. 732-24 du code rural** pour les non-salariés agricoles. La règle les suit
depuis le 21 septembre 2026 ; sa ligne est dans
`data/reference/legislation/veille.yaml`.

**Le barème de ce coefficient est celui du régime général, et l'article le
dit.** R. 643-7 du code de la sécurité sociale, dans sa version du 1er
septembre 2023 : la réduction est fonction « soit du nombre de trimestres
correspondant à la durée séparant l'âge auquel la pension de retraite prend
effet du soixante-cinquième anniversaire […] ou, dans le cas contraire, de
l'âge prévu au 1° de l'article L. 351-8, soit du nombre de trimestres
supplémentaires qui serait nécessaire […] pour relever du deuxième alinéa du I
de l'article L. 643-3 », « le plus petit de ces deux nombres est pris en
considération », arrondi au chiffre supérieur, et « le coefficient de
minoration est égal à 1,25 % par trimestre manquant dans la limite de vingt
trimestres ». C'est mot pour mot ce que `_trimestres_de_decote` fait déjà — le
plus petit des deux décomptes, l'arrondi de R. 351-27, le plafond de vingt — et
ce que la fiche `cnavpl` portait : 1,25 % par trimestre. **La transcription est
donc confirmée par le texte.** Côté agricole, R. 732-39 du code rural pose la
même CONDITION — coefficient de minoration si l'assuré liquide avant l'âge du
taux plein et sans la durée de L. 351-1 —, mais l'article qui en donne le TAUX
n'est pas dans le champ social de l'index LEGI du dépôt : la fiche
`msa_non_salaries` garde son 1,25 % sans l'avoir lu, et la ligne de veille le
dit.

**Deuxième face : aucun âge n'était opposé, et c'est la plus visible.**
`calculer` ne lisait l'âge d'ouverture opposable que sur les périodes en
annuités. Un chef d'exploitation ou un libéral pouvait donc liquider **à
cinquante ans** sans que rien ne le refuse, quand l'artisan de la page voisine
se le voyait refuser. Ce n'était pas qu'un défaut de cas type : c'est ce que le
simulateur du site répondait à qui se déclarait exploitant agricole et
demandait sa pension à cinquante ans. Au passage, `requis_reference` retombait
pour eux sur 160 trimestres — une durée que plus aucune génération ne doit —,
et c'est cette durée-là que leur abattement opposait.

**Troisième face : la carrière longue leur était fermée.** Elle leur est
pourtant ouverte : **L. 732-18-1 du code rural** abaisse l'âge « pour les
personnes ayant exercé une activité non salariée agricole qui ont commencé leur
activité avant un des quatre âges, dont le plus élevé ne peut excéder vingt et
un ans », et **le II de L. 643-3** renvoie les professions libérales à
L. 351-1-1, « les références au régime général […] étant remplacées par celles
au régime d'assurance vieillesse de base des professions libérales ». Les deux
règles d'âge du modèle la lisent désormais sur la même liste : ne l'ouvrir
qu'au taux plein faisait rendre à celui-ci un âge ANTÉRIEUR à celui que
l'ouverture accordait — soixante-trois ans contre soixante-quatre pour un chef
d'exploitation né en 2000 —, c'est-à-dire deux règles du même droit qui se
contredisent.

**Ce que la correction a déplacé, et ce qu'elle a exposé.** Rien sur les
agrégats : la trajectoire 2070 reste à 18,35 % du PIB et l'écart moyen à l'âge
conjoncturel tous régimes à −0,02 an. Les témoins de SIMULATION, eux, bougent —
ce sont les carrières tout en points, qui voient maintenant un âge, une durée
et une carrière longue —, et l'exploitant agricole passe de 61,64 à 61,73 ans
de moyenne sur 2013-2020, partant à soixante-trois ans au titre de la carrière
longue pour les générations récentes au lieu de soixante-quatre. Mais elle a rendu FAUSSE une phrase de la fiche du libéral. Celle-ci
disait « seul cas type à partir APRÈS l'âge d'ouverture : deux ans » et portait
`regle_liquidation: taux_plein` — ce qui ne donnait « ouverture + deux ans »
que par le défaut qu'on vient de corriger. La règle du taux plein, appliquée
pour de bon, la faisait attendre l'annulation de la décote et partir à
soixante-neuf ans : entrée à vingt-sept ans sans carrière antérieure, elle
n'atteint la durée requise à aucun âge. La fiche porte donc désormais
`regle_liquidation: ouverture`, ce que sa propre phrase disait depuis toujours,
et la DREES tranche dans le même sens — les professions libérales partent à
62,6 ans en moyenne de 2013 à 2020, non à soixante-sept. **Le défaut en
masquait un second** : un libéral réel a des années salariées avant son
installation, et ce cas type n'en a aucune.

**Un groupe de la nomenclature n'est pas toujours la bonne référence, et le
libéral l'a montré.** Il y figurait, au groupe 3, « cadres et professions
intellectuelles supérieures » — c'est bien là que la nomenclature met les
professions libérales, et non au groupe 2 avec les indépendants. Mais ce groupe
est dominé par les cadres SALARIÉS, et sa moyenne ne décrit pas les libéraux :
**la CNAVPL publie l'âge moyen à la liquidation de ses propres titulaires**, et
il vaut 64,81 ans en 2018 et 66,11 en 2025, contre 62,59 pour le groupe 3 tout
entier. Trois ans et demi d'écart. Confronté au chiffre de sa caisse plutôt
qu'à celui de son groupe, le cas type ne tombe plus du même côté. Il est donc
sorti du champ de cette confrontation-là, avec sa raison écrite dans
`cas_types_csp.yaml`, et huit cas types y restent.

C'est aussi la correction d'une phrase que ce dépôt a portée une journée : « la
DREES observe les professions libérales partir à 62,6 ans en moyenne » disait
le groupe 3, pas les libéraux.

**Et le COR publie mieux qu'une moyenne de groupe : un cas type de libéral.**
Le rapport annuel de juin 2026 ajoute, sous le n° 13, un médecin généraliste
conventionné de secteur 1 né en 1960. Il « peut prétendre à un départ à
62 ans » et « atteint le taux plein à 66 ans et 9 mois ». La fiche du dépôt,
pour la même génération, donne **62,00 et 67,00** : trois mois d'écart sur le
second, aucun sur le premier. C'est la première confrontation du dépôt à un cas
type libéral publié, et elle vaut mieux que l'âge d'un groupe ou celui d'une
caisse — les deux nombres sont construits sous la MÊME convention, on part au
taux plein, là où l'enquête Emploi et le recueil de la CNAVPL mesurent un
comportement.

**Ce que cette confrontation a tranché.** La fiche portait une règle à elle —
« ouverture plus deux ans » — qui n'était qu'un contournement : le moteur ne
savait pas opposer de durée à une carrière tout en points, et le taux plein lui
rendait donc l'âge d'ouverture. Le défaut corrigé, le contournement n'avait
plus de cause, et sa constante de deux ans ne s'appuyait sur aucune source.
**La fiche est rendue à la règle ordinaire**, `taux_plein` sans décalage, et
`ecart_liquidation` n'a plus qu'un usager, le militaire, dont il porte la durée
de services. Ce que cela déplace : le libéral part à 67 ans dans toutes les
générations au lieu de 64 puis 66 ; la trajectoire 2070 passe de 18,35 à
18,34 % du PIB ; et la concordance d'ensemble à l'âge conjoncturel tous régimes
s'améliore, de −0,07 à −0,02 an.

Contre l'âge OBSERVÉ de sa caisse, la fiche passe de 1,24 an trop tôt à 1,42 an
trop tard. Les deux conventions manquent donc la moyenne réelle d'à peu près
autant, en sens contraire, et le choix ne se fait pas sur l'ajustement : il se
fait sur la règle, et la règle ordinaire est celle du COR.

**Ce que le couloir vaut, et ce qu'il ne vaut pas.** La nomenclature classe des
professions, la grille décrit des carrières par leur régime et leur niveau de
revenu : un cas type déclare donc tous les groupes où il peut tomber, et
l'écart est nul dès qu'il y tombe. Déclarer large affaiblit le constat sans le
fausser — le contractuel, qui réclame les quatre groupes salariés, sort quand
même de plus de deux ans. Et la source est un SONDAGE, l'enquête Emploi, dont
la DREES avertit que les indicateurs par catégorie sont bruités : la
comparaison se fait sur la moyenne 2013-2020, jamais sur une année. Les deux
sources se recoupent là où elles se recouvrent — écart de −0,04 à +0,14 an sur
la ligne « toutes CSP » —, ce qu'un test tient.

---

## 5 quater. Comparaison à la littérature : pourquoi les écarts d'ici sont plus grands

Trois travaux français ont simulé le passage des retraites aux comptes
notionnels, et **aucun ne trouve ce que trouve ce dépôt**. Un lecteur qui les
connaît arrive ici avec une objection d'une ligne — « la CNAV dit −7 %, vous
dites −73 % » — et cette page lui doit une réponse chiffrée. La voici.

### Ce que la littérature trouve

| Travail | Ce qu'il simule | Résultat |
|---|---|---|
| **CNAV, Albert & Oliveau, nov. 2009** (modèle PRISME, régime général, euros 2004) | bascule au prorata des générations 1952-1961, taux réel de la CNAV, **droits non contributifs conservés** | masses de prestations **−7 % en 2050** (hommes −10,5 %, femmes −3,4 %) ; besoin de financement 36 Md€ contre 49 Md€ |
| **COR, 7e rapport, janv. 2010** | l'expertise demandée par le Parlement ; pas de chiffrage central | les dispositifs de solidarité valent **« de l'ordre d'un cinquième des retraites tous régimes »** |
| **CEPII, Lettre n° 297, avril 2010** (OLGAMAP, équilibre général) | régime unique, **taux unique ~22 %**, transition 2015-2030 | besoin de financement **−0,7 pt de PIB** en 2050 ; en variante à actualisation nulle, **−3,2 pts** et système excédentaire |

Et ce que trouve ce dépôt, pour une carrière ascendante au salaire moyen,
entrée à 22 ans, née en 1975, liquidée à 64 ans :

| | Salarié du privé non cadre | Fonctionnaire d'État |
|---|---:|---:|
| 2. Notionnel rétroactif, part salariale | **−73,1 %** | **−82,1 %** |
| 3. Notionnel dès 2026, part salariale | −37,4 % | −41,1 % |
| 4. Notionnel rétroactif, salariale + patronale | −33,5 % | **+4,5 %** |
| 5. Notionnel dès 2026, salariale + patronale | −22,4 % | −30,5 % |
| 6. Proposition libérale (18 % dès 2026) | −41,1 % | −0,9 % |

### Ce n'est pas une contradiction : c'est la somme de quatre choix

L'écart ne vient pas d'un désaccord de calcul. Il vient de quatre décisions
prises ici et pas là-bas, et chacune est chiffrée ou chiffrable.

1. **La rétroactivité.** La CNAV bascule en 1961, le CEPII entre 2015 et 2030,
   et l'un comme l'autre **conservent les droits déjà acquis**. Les scénarios 2
   et 4 recalculent la carrière ENTIÈRE depuis 1941. Le dépôt publie lui-même
   la mesure de ce choix : les scénarios 3 et 5, qui figent les droits acquis
   comme le fait la littérature, ramènent l'écart de −73,1 % à −37,4 % pour le
   salarié du privé. **La moitié de l'écart est de la rétroactivité, rien
   d'autre.**
2. **Les droits non contributifs.** La CNAV les CONSERVE et les convertit en
   cotisations fictives ; son tableau 2.1 en donne la part dans le capital
   porté au compte — **hommes 16 % en 2020 et 13 % en 2050, femmes 36 % et
   31 %**. Le COR donne le même ordre de grandeur tous régimes, un cinquième.
   Le §6 de `methodologie.md` les supprime tous. C'est, à soi seul, dix à
   trente-cinq points de capital en moins selon le sexe — et c'est aussi
   pourquoi les écarts de ce dépôt sont, à carrière égale, plus durs pour les
   femmes.
3. **Le périmètre de la cotisation.** Les scénarios 2 et 3 ne portent au compte
   que la part SALARIALE, soit 40 % du total versé pour le salarié du privé et
   19 % pour le fonctionnaire. La littérature raisonne toujours sur la
   cotisation entière. Le scénario 4 est la comparaison honnête, et il donne
   −33,5 % pour le privé et **+4,5 %** pour le fonctionnaire.
4. **L'âge de liquidation.** La CNAV suppose les âges de départ INCHANGÉS, et
   observe malgré tout que ses perdants partent à 60 ans et ses gagnants à 65.
   Ici, le diviseur est la seule sanction du départ précoce, et il n'est pas
   amorti par une décote plafonnée.

Additionnés, ces quatre écarts rendent compte de la distance entre −7 % et
−73 % sans qu'aucun chiffre ait besoin d'être révisé de part ou d'autre. Ce
qu'il faut en retenir : **les résultats de ce dépôt ne mesurent pas « le
notionnel » en général, mais une version précise et volontairement dure du
notionnel**, et la littérature en mesure une autre, volontairement douce.

### Ce que la comparaison valide

Quatre choix du modèle sont confirmés par des sources qui ne le connaissent
pas :

- **La table de génération** (§5). La CNAV calcule sur des tables
  transversales et écrit ce que cela lui coûte : sa mortalité PRISME étant
  longitudinale, « les pensions sont par conséquent plus élevées que celles qui
  permettraient d'épuiser le capital notionnel ». Le biais que le dépôt évite,
  constaté par un praticien sur son propre calcul.
- **La table unisexe** (§5), qui est aussi celle de la CNAV.
- **L'indexation sur la masse salariale** (§3). La maquette du secrétariat
  général du COR : « l'équilibre à chaque date est assuré par construction […]
  dans la mesure où le taux de revalorisation est ici supposé égal au taux de
  croissance de la masse salariale ». Avec sa limite, en note : ce n'est pas le
  choix suédois, qui indexe sur les salaires et non sur la masse.
- **La part patronale de l'État en 2008.** Le CEPII écrit 55,7 % ; la ligne
  certifiée du dépôt porte 55,71 %. Deux chaînes sans rapport, le même chiffre.

### Ce qu'elle ne valide pas, et qui reste assumé

- **Le bouclage macroéconomique.** Le CEPII calcule en équilibre général : ses
  réformes déplacent le taux d'intérêt, l'emploi et la croissance, qui
  rétroagissent sur l'équilibre des régimes. Le dépôt est comptable de bout en
  bout. Ses trajectoires agrégées (§5 bis, §5 ter) ne doivent donc pas être
  lues comme des projections d'économiste.
- **Le pilotage.** Aucun des trois travaux ne laisse dormir un excédent ; le
  dépôt, lui, calcule un coefficient d'équilibre sans l'appliquer. C'est la
  limite déjà nommée au §5 bis.

### Les limites de la comparaison elle-même

Ces travaux datent de 2009 et 2010, **d'avant les réformes de 2010, 2014 et
2023** : leur contrefactuel « système actuel » n'est plus le droit en vigueur,
leurs montants sont en euros 2004, et la CNAV ne couvre que le régime général.
Ils ne sont donc pas des étalons, et **aucun n'alimente une seule valeur de
`data/reference/`** : ils figurent au manifeste en `controle`, statut réservé
aux sources qui n'apportent aucun chiffre mais en contrôlent un autre. Ce qu'ils
apportent, c'est une méthode déjà éprouvée et des ordres de grandeur — pas des
barèmes.

---

## 6. Reproductibilité

- Aucune dépendance hors PyYAML ; tous les calculs sont déterministes.
- La calibration des tables de mortalité est mémorisée dans
  `data/derive/calibrations_mortalite.json`, régénérable en supprimant le fichier.
- La certification des séries est tracée dans `data/derive/certification.json`,
  que `scripts/verifier_donnees.py --appliquer` COMPLÈTE au lieu de le
  remplacer : les récupérateurs sont indépendants et lents, on ne lance
  presque jamais les dix-sept d'un coup, et réécrire le journal à partir des
  seules sources présentes ce jour-là effaçait la trace de toutes les autres.
  Chaque fiche de série porte `verifiee_le`, le jour où elle a été relue contre
  sa source, valeurs changées ou non ; `dernier_passage_le` n'est que la date
  du dernier `--appliquer`, fût-il partiel. La page Données dit le minimum des
  dates de fiche, seule affirmation que le journal soutient, et un test refuse
  une fiche sans date. Les dates antérieures au 17 septembre 2026 ont été
  rétablies depuis l'historique du dépôt — le dernier commit où chaque fiche a
  changé —, ce qui est une borne basse : une série relue sans changement avant
  cette date n'a laissé aucune trace.
- <!--chiffre:tests()-->2088<!--/--> tests couvrent le chargement, la fiabilité, la règle de certification, la
  concordance des tables de mortalité observées avec les espérances publiées, les
  propriétés du moteur et le comportement des scénarios : `python -m pytest tests`.
  Aucun test n'accède au réseau : les sources sont simulées.
- Les bases JORF et LEGI de la DILA sont interrogeables sans retélécharger
  leurs dumps : `python scripts/fetch/dila_index.py jorf --recuperer` rapatrie
  l'index plein texte publié sur la release `index-dila` du dépôt,
  `--mettre-a-jour` y applique les incréments quotidiens parus depuis, et
  `dila_cherche.py` l'interroge. L'index se reconstruit depuis le dump par
  `dila_index.py jorf` (une demi-heure, dump gardé en cache dans `data/brut/dila/`).
