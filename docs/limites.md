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
| Minimum contributif majoré | idem, 7 603,41 → 10 170,86 €/an | **certifié**, même article |
| Plafond d'écrêtement du minimum | ancres 2012 et 2014 ; montants servis 2020, 2024-2026 | **certifié** (D. 173-21-0-0-1) et transcrit |
| Minimum garanti, barème | montée en charge 2004-2013, indice 216 → 227 | **certifié** (loi de 2003, article 66 V) ; la ligne 1976 décrit le droit antérieur et reste transcrite |
| Minimum garanti, référence | 997,96 €/mois au 1er janvier 2004 ; montants servis 2020, 2023-2025 | transcrit ; l'ancre de 2004 est recoupée à chaque exécution au point d'indice certifié — 227 × 52,7558 = 11 975,57 € |
| Point d'indice de la fonction publique | série datée 1960-2027 | OpenFisca-France, **recontrôlé à chaque exécution** |
| Minimum vieillesse (ASPA) | montants servis 2007, 2010, 2016-2026 | transcrit des publications |
| Décote de la fonction publique | article L. 14, montée en charge 2006-2020 | **certifiée** (loi de 2003, article 66 III) jusqu'à 2019 ; la ligne 2020 est la jonction avec L. 14 |
| Carrière longue | quatre étapes datées au mois, 2004, novembre 2012, septembre 2023, septembre 2026 ; la borne des vingt ans par génération | **certifiée** pour la règle générale de 2023 (L. 351-1-1, D. 351-1-1) ; les lignes par génération et celles de 2026 transcrites du II de l'article et de la circulaire Cnav 2026-17 |
| Trimestres accordés au titre des enfants | MDA à 4 puis 8 trimestres par enfant (1972, 1975) ; bonification de la fonction publique à 4 puis 2 (2004) | reprise des textes, non recontrôlée |
| Surcote parentale | 1,25 % par trimestre entre 63 ans et l'âge légal, quatre au plus | reprise des textes (L. 351-1-2-1), non recontrôlée |
| Durée requise par génération | table 1934-1975, 151 → 172 trimestres, suspension de 2026 comprise (170 pour 1964 et le premier trimestre 1965, 171 jusqu'à fin 1965, 172 dès 1966) | **certifiée** depuis 1953 (L. 161-17-3 réécrit par la loi de financement pour 2026, relu dans l'index LEGI à jour ; décrets pour 1953-1957) et pour 1934-1942 (R. 351-45) ; 1943-1952 transcrite |
| Durée de proratisation par génération | table 1900-1948, 150 → 160 trimestres | **certifiée** (R. 351-6 II) jusqu'à 1947 ; la ligne 1948 est la jonction avec la durée requise, que l'article ne fixe pas |
| Heures de SMIC pour valider un trimestre | 200 depuis 1972, 150 depuis 2014 | **certifiée** (R. 351-9) |
| Revalorisation des salaires portés au compte | 10 colonnes publiées, effets d'octobre 2017 à janvier 2026 | circulaires de la Cnav ; ailleurs, ancrage sur la plus proche |
| Âge légal par génération | table 1900-1975, 60 → 64 ans, suspension de 2026 comprise (62 ans et 9 mois de 1963 au premier trimestre 1965, un trimestre par génération ensuite, 64 ans dès 1969) | **certifié** (L. 161-17-2, qui porte la table depuis la loi de financement pour 2026, et D. 161-2-1-9 pour les générations qu'elle renvoie à sa rédaction antérieure), recontrôlé à chaque exécution sur l'index LEGI du dépôt, à jour des incréments quotidiens de la DILA |
| Surcote | barème daté trimestre par trimestre : 0,75 % (2004-2006), 0,75 % puis 1 % à compter du cinquième et 1,25 % après 65 ans (2007-2008), 1,25 % (depuis 2009) ; fonction publique 0,75 % plafonné à vingt trimestres puis 1,25 % ; période de référence au trimestre civil | transcrit de D. 351-1-4 et de L. 14 III, rejoué contre les trois exemples de la circulaire Cnav 2018-04 et deux fiches de service-public |
| Salaire annuel moyen des parents | 24 meilleures années pour un enfant, 23 pour deux et plus, pensions dès septembre 2026 | transcrit de R. 173-3-2 (décret n° 2026-699), non recontrôlé |
| Âge d'annulation de la décote par génération | table 1930-1955, 65 → 67 ans | calculée depuis l'âge d'ouverture certifié, selon la règle de `L. 351-8` ; recontrôlée à chaque exécution |
| Coefficient de minoration par génération | table 1900-1975, 2,5 → 1,25 % | **certifié** (R. 351-27 II), recoupé à la DREES |
| Années retenues au salaire de référence | table 1934-1948, 10 → 25 années | **certifiée** (R. 351-29-1) |
| Coefficients d'anticipation Agirc-Arrco | deux tables, 1 → 0,78 et 1 → 0,43 | barème publié par la caisse, saisi |
| Plafond de la majoration familiale Agirc-Arrco | 2 367 €/an (novembre 2025) | publié par la caisse, saisi |
| Garantie minimale de points de l'Agirc | 120 points par an, 1989-2018 | accord du 9 février 1988, saisi |
| Assiette de l'AVPF | SMIC annuel, 1 820 heures | principe sourcé, assiette déduite du SMIC |
| Droits ouverts par motif d'interruption | 9 motifs | principe sourcé, fractions non recontrôlées |

**Une règle a été appliquée partout : le montant SERVI prime sur la projection.**
Le minimum contributif, le minimum garanti et le minimum vieillesse sont trois
grandeurs que la loi ne fixe pas chaque année — elle les revalorise « comme les
pensions », c'est-à-dire selon une décision annuelle qui a été gelée en 2014 et
sous-indexée plusieurs fois depuis. Projeter une ancre sur l'indice des prix
donne donc, pour le minimum garanti de 2024, un montant supérieur de 4,6 % à
celui que l'État a payé. Les montants transcrits de leur publication, moins bien
sourcés, l'emportent sur les valeurs calculées depuis une ancre certifiée —
parce que les premiers disent ce qui a été payé et les seconds ce qui aurait dû
l'être.

## Écarts avec le droit positif dans le scénario 1

### Ce qui vient d'être refermé

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
- **Bonifications de service.** Bonifications de dépaysement, de campagne
  militaire, du cinquième pour les emplois de sécurité. La bonification POUR
  ENFANTS, elle, est servie : elle ne demande que le nombre d'enfants. Les
  autres supposent de connaître le CORPS d'appartenance et le détail des
  services, que la saisie ne demande pas.
- **Catégorie active : servie, mais sur un classement déclaré.** L'âge anticipé
  de l'article L. 24 — 57 ans, 52 pour la super-active, 59 et 54 après la
  réforme de 2023 — est désormais opposé, ainsi que l'âge d'annulation de décote
  propre au classement (62 et 57 ans) et la condition de durée de services
  classés (17 et 27 ans). Ce qui reste hors du modèle est le CLASSEMENT
  lui-même : il tient à l'emploi occupé, qu'aucune donnée de carrière ne révèle,
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
- **Trimestres « réputés cotisés » de la carrière longue.** La loi du 20 janvier
  2014 en a élargi la liste (chômage, maladie, maternité, dans des limites
  propres à chacun). Le modèle ne compte que les trimestres réellement cotisés
  — et, depuis les pensions de septembre 2026, les deux trimestres de
  majoration pour enfants que la loi de financement pour 2026 répute cotisés —,
  ce qui rend la condition plus dure qu'elle ne l'est : quelques carrières
  hachées sont déclarées non ouvertes alors que le droit les ouvrirait.
- **La date d'effet est le mois de l'anniversaire.** Le modèle liquide au mois
  où l'âge demandé est atteint ; la caisse fait prendre effet la pension le
  premier jour du mois SUIVANT, sauf pour qui est né un premier. Un mois
  d'écart, qui se voit là où un texte coupe au mois : la borne de la carrière
  longue des nés en décembre 1965, fixée à 60 ans et 8 mois pour que la
  pension prenne effet le 1er septembre 2026, tombe ici en août 2026, sous le
  décret précédent, qui demande 60 ans et 9 mois.
- **La durée requise des emplois classés.** Le décret n° 2026-344 (article 3,
  B) donne aux catégories actives leur propre calendrier de durée — 169
  trimestres des nés de septembre 1966 à 1967, 172 dès 1971 —, l'âge anticipé
  ayant cinq ans d'avance sur l'âge légal ; le modèle leur oppose la durée de
  leur génération, comme aux sédentaires. Les âges eux-mêmes sont lus alinéa
  par alinéa dans le D du même article.
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
| Inflation (IPC) | 1950-2025 | **certifiée** | INSEE BDM, idbanks 000008965 et 001764363 |
| Inflation | 1930-1949 | estimée | reconstitution, dérive cumulée recoupée à l'INSEE idbank 010605954 (1901-) |
| Salaire moyen par tête | 1950-2025 | **certifiée** | INSEE BDM, idbanks 011785411 et 011793486 |
| Salaire moyen par tête | 1930-1949 | estimée | reconstitution |
| Productivité réelle | 1950-2025 | **certifiée** | INSEE BDM, idbanks 011785223 et 011793334 |
| Productivité réelle | 1930-1949 | estimée | reconstitution |
| Produit intérieur brut, en niveau | 1949-2025 | **certifiée** | INSEE BDM, idbank 011779992 |
| Population par âge, 50 ans et plus | 1962-2023 | **certifiée** | INSEE, estimations de population (classeur des projections 2026) |
| Population par âge, 50 ans et plus | 2024-2070 | projetée | INSEE, projections de population 2026, scénario central |
| Population des 20-64 ans | 1962-2023 / 2024-2070 | **certifiée** / projetée | mêmes sources |
| Dépenses de vieillesse-survie, tous régimes | 1959-2024 | **certifiée** | DREES, Comptes de la protection sociale, poste E11-2 |
| Dépenses de vieillesse-survie, par système | 1990-2024 | **certifiée** | DREES, mêmes comptes, ventilation par organisme |
| Dépenses de vieillesse-survie, par système | 1981-1989 | absentes | nomenclature d'alors sans raccord publié — voir §5 bis |
| Retraités de droit direct, par caisse | 2004-2024, 28 caisses | **certifiée** | DREES, enquête annuelle auprès des caisses de retraite, fichier diffusé |
| Retraités de droit direct, par caisse | hors 2004-2024 | estimée | la répartition du bord est reconduite — voir §5 bis |
| Distribution des pensions mensuelles brutes de droit direct | fin 2020, 46 tranches | **certifiée** | DREES, échantillon interrégimes de retraités 2020, tableau 1 |
| Hypothèses de projection | 2026-2100 | **saisie** | COR, rapport annuel de juin 2025, jeu reconduit en juin 2026 |
| Espérance de vie à 0 et 60 ans | 1946-2025 | **certifiée** | INSEE BDM, quatre idbanks, annuel par sexe |
| Espérance de vie à 65 ans | 1960-2024 | **certifiée** | OCDE `DSD_HEALTH_STAT@DF_LE` |
| Espérance de vie à 65 ans | 1946-1959 | haute | **dérivée** des quotients INED, recalculée à chaque exécution |
| Espérances de vie e0, e60, e65 | 2026-2125 | projetée | **dérivée** des quotients projetés par l'INSEE, projections 2026 |
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
| Âge d'ouverture des droits par génération | 1900-1975 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 161-2-1-9` |
| Durée d'assurance requise par génération | 1958-1975 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `L. 161-17-3` |
| Durée d'assurance requise par génération | 1953-1957 | **certifiée** | DILA, base LEGI, décrets d'application des lois de 2003 et de 2010 |
| Durée d'assurance requise par génération | 1934-1942 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-45` II |
| Durée d'assurance requise par génération | 1943-1952 | haute | 160 vient de la règle générale, non d'un alinéa qui les nomme ; les 161-164 sont dans des décrets absents de la base — recoupées à chaque exécution contre la table d'OpenFisca-France-Pension |
| Durée de services de la fonction publique, droits ouverts 2004-2008 | 152 à 160 trimestres | haute | loi n° 2003-775, article 66 II, lu dans la base LEGI et mis en table ; recoupé contre OpenFisca-France-Pension |
| Coefficient de minoration par génération | 1900-1975 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-27` |
| Bornes de la carrière longue | 2023-, règle générale et borne des vingt ans par génération | **certifiée** | DILA, base LEGI, `L. 351-1-1` et `D. 351-1-1` (I et II, versions de 2023 et de 2026, lues à leur date d'effet) |
| Bornes de la carrière longue | 2004, 2011 et 2012, par génération | **certifiée** | DILA, base LEGI, versions abrogées de `D. 351-1-1` que l'index expose |
| Durée maximale prise en compte par la proratisation | avant 1944 à 1947 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-6` II |
| Heures de SMIC à cotiser pour valider un trimestre | 1972 et 2014 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-9` |
| Années retenues au salaire annuel moyen, par génération | avant 1934 à 1948 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-29-1` |
| Décote de la fonction publique, coefficient et âge d'annulation | 2006-2019 | **certifiée** | DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 III |
| Barème du minimum garanti, montée en charge | 2004-2013 | **certifiée** | DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 V |
| Âge d'annulation de la décote, régime général | 1930-1955 | haute | calculé — l'âge d'ouverture certifié majoré de cinq ans, comme l'écrit `L. 351-8` ; recontrôlé à chaque exécution, et recoupé contre la table transcrite d'OpenFisca-France-Pension |
| Point d'indice de la fonction publique | 1996-2027 | **certifiée** | DILA, base LEGI, décret n° 85-1148 du 24 octobre 1985, article 3 |
| Point d'indice de la fonction publique | 1960-1995 | haute | OpenFisca-France, `point_indice_en_euros` — deux versions manquent au dump avant 1996 |
| SMIC horaire | 1997-2017, sauf 2002 | **certifiée** | DILA, base LEGI, décrets portant relèvement du SMIC |
| SMIC horaire | 1970-1996, 2002 et depuis 2018 | haute | OpenFisca-France, `smic_horaire_brut` |
| Plafond Sécurité sociale | 2002-2025 | **certifiée** | INSEE BDM, idbank 000822494 |
| Plafond Sécurité sociale | 1963, 1965-1981, 1984, 1987, 1988, 1990-1993, 1996-2001 | **certifiée** | DILA, base JORF, décrets portant fixation du plafond |
| Plafond Sécurité sociale | le reste de 1931-2001 | haute | OpenFisca-France, daté décret par décret — la notice ancienne du JORF n'a pas d'écriture stable |
| Revalorisation des salaires portés au compte | 10 colonnes, effets 2017-2026, perceptions depuis 1930 | haute | Cnav, circulaires de revalorisation, recoupées deux à deux |
| Taux de cotisation, régime général | 1982-2026 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 242-4` et décret n° 81-1013 du 13 novembre 1981, article 2 ; la hausse temporaire de 1987-1988, qui n'a pas réécrit l'article, est lue dans la base JORF |
| Taux de cotisation, régime général | 1967-1979 | haute | OpenFisca-France, transcrit des barèmes IPP — l'article 3 du décret n° 67-803 n'a qu'une version dans LEGI, datée de 1967 et portant l'état de 1979. Chaque marche est **ancrée** à son décret, retrouvé au JORF au numéro et à la date que l'IPP annonce (35 sur 36 ; le n° 70-680 manque à l'index) |
| Taux de cotisation, régime général | 1980 et 1981 | **fausses** | le décret n° 79-650 du 30 juillet 1979 a relevé ces taux « à titre exceptionnel » du 1er août 1979 au 31 janvier 1981, sans qu'aucune source ne porte la hausse et sans que sa notice l'écrive |
| Taux de cotisation, salariés agricoles | 1980-2026 | **certifiée** | DILA, base LEGI, décret n° 50-444 du 20 avril 1950, article 2, puis code rural `D. 741-35`, qui renvoie à `D. 242-4` depuis 2014 |
| Taux de cotisation, salariés agricoles | 1967-1979 | moyenne | la série du régime général tenant lieu, faute d'une version antérieure de l'article 2 |
| Taux de cotisation, cultes, Mayotte, Saint-Pierre-et-Miquelon | depuis 1979 et 1987 | haute | la série du régime général du dépôt, que ces trois régimes portent faute d'un barème propre : la valeur est certifiée, la substitution est une décision de modélisation |
| Taux de cotisation, complémentaires du privé | Arrco 1962-2018, Agirc 1981-2018, Agirc-Arrco 2019- | moyenne | OpenFisca-France, taux effectifs par tranche, recoupés à chaque exécution. **Ne se certifieront pas** : ces taux sont fixés par accord collectif, l'IPP — source amont d'OpenFisca — laisse lui-même la colonne du *Journal officiel* vide pour chacune de leurs 25 marches, et le JO ne publie que l'avis d'extension, qui renvoie au Bulletin officiel sans écrire le chiffre |
| Retenue pour pension, État, CNRACL, ouvriers de l'État | 1948-2026, une période par taux | moyenne | OpenFisca-France, article L. 61 et barème de la caisse, recoupés à chaque exécution |
| Cotisation vieillesse de base des artisans et commerçants | 1973-2018, moyennes par période | moyenne | OpenFisca-France, décrets d'application de la loi du 3 juillet 1972, recoupés à chaque exécution |
| Taux de cotisation, autres régimes | tous | moyenne / estimée | Comptes de la Sécurité sociale |
| Répartition salarié/employeur, régime général | 1968-2026 | haute | OpenFisca-France, recoupée à chaque exécution |
| Répartition salarié/employeur, autres régimes de salariés | toutes | moyenne / estimée | OpenFisca et textes ; règle 40-60 pour les complémentaires |
| Contribution employeur, État | 2006-2026 | **certifiée** | Service des retraites de l'État, fiche « Historique des taux de cotisations » |
| Contribution employeur, État (implicite) | 1995-2005 | haute | OpenFisca-France, jaune « pensions » du PLF 2011 — reconstitution dont le producteur refuse les requêtes automatisées |
| Contribution employeur, CNRACL | 1993-2028 | **certifiée** | DILA, base LEGI, décret n° 91-613 du 28 juin 1991, article 5 II |
| Contribution employeur, CNRACL | 1984-1988 | **certifiée** | DILA, base LEGI, décret n° 47-1846 du 19 septembre 1947, article 3 |
| Contribution employeur, CNRACL | 1948-1983, 1989-1992 | haute | OpenFisca-France — la chaîne des versions de l'article 3 est trouée, et la base le démontre |
| Contribution employeur, SNCF (T1 + T2) | 2007-2011 | **certifiée** | DILA, arrêtés annuels du taux T1 (base JORF) et décret n° 2007-1056, article 2 IV (base LEGI) |
| Contribution employeur, SNCF (T1 + T2) | 2012-2018 | haute | OpenFisca-France — le décret cesse de chiffrer T2 après 2011 et le fait évoluer par formule |
| Valeurs d'achat et de service du point, Ircantec | 1971-2021 | **certifiée** | Caisse des dépôts, qui gère le régime |
| Valeurs d'achat et de service du point, Agirc | 1947-2018 | **certifiée** | Fédération Agirc-Arrco, sa compilation des valeurs de point |
| Valeurs d'achat et de service du point, Arrco | 1999-2018 | **certifiée** | Fédération Agirc-Arrco, la même compilation |
| Valeurs d'achat et de service du point, UNIRS | 1961-1998 | **certifiée** | Fédération Agirc-Arrco, la même compilation |
| Valeurs du point, Arrco avant 1999 | 1949-1998 | moyenne | l'UNIRS tenant lieu d'Arrco : la valeur est certifiée, la substitution reste une décision du dépôt |
| Valeurs d'acquisition et de service du point, RAFP | 2005-2026 | **certifiée** | ERAFP, dont le conseil d'administration les fixe |
| Valeurs d'achat et de service du point, autres | RCI 2013-2023, IGRANTE et IPACTE 1947-2022 | haute | OpenFisca-France-Pension |
| Valeurs du point, complémentaire des avocats | 2017-2026 | **certifiée** | CNBF, ses barèmes annuels |
| Valeur du point, base des professions libérales | 2021-2025 | **certifiée** | CNAVPL, ses recueils statistiques |
| Taux des deux tranches, base des professions libérales | 2020-2026 | **certifiée** | CNAVPL, le tableau des cotisations de ses recueils, exercice par exercice |
| Valeur de service du point, complémentaire agricole | 2005-2024 | **certifiée** | DILA, base LEGI, code rural `D. 732-166` |
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
- **la projection ne reconduit pas la croissance de l'emploi.** Au-delà de 2025,
  l'emploi salarié est supposé constant. Le rendement projeté est donc celui du
  seul salaire moyen : la règle est nettement moins généreuse en projection
  qu'en rétrospective, et l'écart entre générations anciennes et récentes en
  vient pour partie de là, non d'un effet de la réforme simulée.

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
vingt-deux, chacun avec sa source et sa date de vérification, et
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
| circulaire Cnav 2026-17 | carrière longue par génération, 1964 à 1971, ouverte à la borne et refusée un trimestre plus tôt | **exact**, une fois la borne lue par génération |
| circulaire Cnav 2018-04 | surcote à un, deux et trois taux (2,5 %, 4,75 %, 10,25 %) | **exact**, une fois le barème daté |

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

**Ce que les exemples ne couvrent pas.** Ils sont courts par construction :
une affiliation, pas de polypension, pas d'enfant sauf pour le minimum, pas
de carrière hachée. Les vingt-quatre et vingt-trois années des parents, les
deux trimestres d'enfants réputés cotisés, les âges des catégories actives
n'ont pas d'exemple publié que le dépôt ait trouvé : ils sont transcrits du
texte, et attendent le leur.

**Ce que cette source vaut, et ce qu'elle ne vaut pas.** Un exemple de
circulaire est antérieur à la règle qui le suit — ceux de 2018 valent pour le
droit de 2018 — et une fiche de service-public est réécrite sans que son
exemple le soit toujours : chaque désaccord se tranche par le texte, jamais
par l'exemple seul. Mais quand les vingt-deux tombent justes ensemble, sur
sept sources et cinq règles, c'est le droit que le modèle applique, et non une
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
la portent : les taux que le dépôt sert pour ces deux années sont donc **trop
bas**, d'un montant que la notice n'écrit pas — elle ne nomme même aucun risque,
et le décret lui-même a disparu de LEGI avec sa date d'expiration. Le tableau de
certification porte ces deux années comme *fausses* et non comme incertaines.

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

**La masse que produisent les cas types était nulle sur toute la projection,
et elle ne l'est plus.** Le 18 septembre 2026, le rapport de masse de la
garantie valait 8,8 · 10⁻⁶ en 2024 et zéro de 2030 à 2070 : la trajectoire du
scénario 6 ne portait AUCUNE des dépenses que l'impôt financerait. Le motif
n'était pas l'âge de l'allocation mais le NIVEAU des pensions de la grille —
les deux seuls cas types qui tombent sous le plancher, l'exploitant agricole à
674 € par mois et le carrière complète au SMIC à 797 €, liquident à 64 et
62 ans, et les cinq qui partent à 65 ans ou plus sont tous au-dessus. Servir la
garantie à 65 ans à qui est parti plus tôt a refermé ce zéro : la trajectoire
porte désormais **0,80 % du PIB en 2026**, décroissant à 0,20 % en 2070 à
mesure que les pensions montent face à un plancher indexé sur les prix, soit
616 milliards d'euros constants cumulés sur la projection.

**Elle reste une masse vue par treize carrières, et c'est la limite qui ne se
refermera pas ainsi.** Une allocation DIFFÉRENTIELLE ne se chiffre pas sur
treize carrières, parce que son coût est tout entier celui de la queue basse de
la distribution, et que treize carrières choisies pour couvrir les
configurations du système n'en ont pas. Le chiffre est maintenant du bon ordre
de grandeur — de l'ordre des trois quarts de ce que le barème appliqué à la
distribution réelle donne aux pensions d'aujourd'hui — au lieu d'être nul, ce
qui est un progrès et non une solution.

**Ce que la garantie n'est plus : une dépense du compte des cotisants.** Elle
est financée par l'impôt, et elle a donc quitté la masse contributive du
scénario 6, où elle était comptée jusqu'ici. C'est la symétrie de ce que la
recette fait déjà — la CSG de solidarité sort des ressources —, et sans elle la
garantie aurait été payée deux fois : une fois par les cotisations, une fois
par le contribuable.

La page porte donc, à côté, le barème appliqué à la distribution des pensions
brutes de droit direct que publie l'échantillon interrégimes de retraités de la
DREES (fin 2020, tranches de cent euros). Quatre chiffres, parce que deux
questions et deux planchers :

| Assiette | Plancher | Retraités concernés | Coût annuel, euros de 2026 |
|---|---|---|---|
| Pensions de 2020 | 800 € | 22,8 %, soit 3,8 M | **18,4 Md €** |
| Pensions de 2020 | 1 050 € | 32,7 %, soit 5,5 M | **32,2 Md €** |
| Pensions du scénario 6 | 800 € | 48,0 %, soit 8,0 M | **35,9 Md €** |
| Pensions du scénario 6 | 1 050 € | 64,7 %, soit 10,8 M | **64,2 Md €** |

Ce que chaque ligne suppose. **Les deux planchers** sont donnés parce que
l'enquête dit la pension et non avec qui l'on vit : la garantie de base vaut
pour qui vit à deux, la majorée pour qui vit seul, et le coût réel est entre les
deux. **Les deux assiettes** ne répondent pas à la même question : à pensions
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
  bien que la majoration de pension pour trois enfants et plus vaut **zéro
  toutes les années de la série** quand la CNAF en rembourse 5,9 milliards en
  2025, et que la surcote parentale vaut zéro pour la même raison. La grille est
  faite pour comparer des systèmes sur une même carrière, où les erreurs de
  niveau s'annulent au dénominateur ; le coût d'un avantage est un compte de
  POPULATION, et il lui faut une structure de population. C'est la correction
  déjà faite pour la garantie vieillesse — les 93 milliards tirés des cas types
  étaient faux, le barème appliqué à la distribution DREES donne 18,4 milliards
  — et elle est due ici pour les mêmes raisons. Mesuré :
  `scripts/cout_avantages.py` trouve 12,6 milliards d'avantages gratuits en 2024,
  soit 3,0 % de la dépense ; la réversion, qui se LIT dans les séries de la
  DREES au lieu de se calculer, y ajoute 38,3 milliards, ce qui porte le total
  chiffré à 50,9 milliards, soit 11,9 %. Le COR chiffre l'ensemble des droits de
  solidarité à « de l'ordre d'un cinquième », soit 85 milliards : on en tient
  les trois cinquièmes. Les vingt-neuf dispositifs non chiffrés expliquent
  la plus grande part de l'écart, l'absence d'enfants le reste. Voir
  `docs/avantages_non_contributifs.md`.

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
  868 € par an. Mesurer la valeur d'un avantage d'ÂGE par l'écart de MONTANT
  à date de départ fixe donne donc un chiffre petit — 0,6 milliard en 2024 pour
  la catégorie active — et ce chiffre n'est pas faux, il est incomplet : ce que
  l'avantage coûte, ce sont les annuités servies avant l'âge légal, que nulle
  décote ne rattrape. Elles valent **13,7 milliards en 2024**, dont 7,5 pour le
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
  vaut **0,63** une fois la bascule passée, c'est-à-dire un taux moyen de
  **28,7 %** aujourd'hui. Le contrôle externe est le meilleur dont cette page
  dispose : le COR publie, dans son rapport annuel, le taux de cotisation
  retraite d'un salarié non cadre du privé sous le plafond, parts salariale et
  employeur — 27,9 % en 2025 —, et le modèle le retrouve à huit dixièmes de
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
  poids d'un cas type parmi les COTISANTS est celui qu'il a parmi les
  retraités de sa caisse, faute d'une série de cotisants : cette approximation
  surreprésente les régimes qui s'éteignent, dont les taux sont parmi les plus
  élevés, et pousse donc le rapport vers le bas.

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
  GÉNÉRAL, décrit ci-dessous, que l'impôt compense et qui reparaît dans les
  4,6 points d'impôts et taxes affectés. La seconde est la COMPOSITION de la
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
  | Scénario 6, convention `assiette` (affichée) | **+0,12 % du PIB** | **0,97** | 2026 |
  | Scénario 6, convention `rapport` | −0,73 % | 0,88 | 2026 |
  | Système actuel | −1,13 % | — | jamais |

Le taux plein rapporte PLUS que le rapport de taux légaux ne le disait :
  18 % d'assiette au lieu de 15,5, soit deux points et demi d'assiette gagnés,
  et c'est ce qui sépare les deux lignes. **Sous sa propre convention, la
  proposition est donc légèrement excédentaire, là où l'affichage la donne en
  léger déficit ; dans les deux cas elle fait mieux que le système qu'elle
  remplace.** *Cette ligne a d'abord été calculée à −1,28 % : on retirait alors
  tout le poste des impôts et taxes affectés, au motif qu'il compensait les
  allègements. Il ne les compense pas — voir ci-dessous —, et seule la CSG de
  solidarité en sort, par le retrait.*

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

  *Ce que la sortie coûte.* Le solde moyen du scénario 6 sur 2026-2070 passe
  de −1,12 % du PIB à **−2,51 %**, contre −1,14 % pour le système actuel : il
  est désormais plus déficitaire que lui dans 38 des 45 années, et ne revient
  à l'équilibre sur aucune. Son coefficient d'équilibre — ce que le système
  peut servir rapporté à ce qu'il promet — descend de 0,97 à **0,82**. Les
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

  L'impossibilité est l'IMPORT AUTOMATIQUE du relevé Info-Retraite, qui n'est
  pas implémenté et ne peut pas l'être : le répertoire de gestion des carrières
  uniques n'est pas ouvert au public, et son accès passe par une
  authentification personnelle qu'un script ne saurait porter sans détenir les
  identifiants de l'assuré. Le relevé se recopie donc à la main, dans un format
  d'une ligne par année — `année:régime:revenu:trimestres`.

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

**2. La courbe est celle d'un jour.** Elle est datée, publiée, recontrôlée,
mais elle est un instantané : le 17 septembre 2026 et non un mois plus tôt. Un
déplacement général de la courbe déplace tout le pilier, et rien dans le modèle
ne lisse cette dépendance. C'est assumé — une moyenne de courbes n'est la
courbe de personne — et c'est la raison pour laquelle le fichier de référence
garde les courbes successives : un chiffre publié doit pouvoir être refait tel
qu'il a été publié.

**3. Les frais sont ceux d'un produit vendu à des volontaires.** 1,09 % sur
versement, 0,76 % par an sur encours, 2,20 % sur arrérages : ce sont les
moyennes du PER individuel tel qu'il est commercialisé, et la commission du
réseau distributeur en est l'essentiel. Une cotisation obligatoire n'a pas de
réseau à rémunérer, et les frais d'un pilier obligatoire seraient
vraisemblablement inférieurs. Le modèle retient donc une **borne haute**, qui
sous-estime la rente. Le sens du biais est connu, sa taille ne l'est pas : à
titre de repère, ramener les frais de gestion à 0,20 % relèverait le capital
d'environ 10 % sur une carrière complète.

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

## 5 ante bis. La fiche de paie : neuf réserves, dont trois décisives

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
proposition ne le fixe pas.** Elle dit « 18 %, salariale et patronale
additionnées ». Le dépôt partage moitié-moitié. On croirait ce choix sans effet
sous l'incidence intégrale ; il ne l'est pas, pour deux raisons distinctes : la
CSG et la CRDS sont assises sur le BRUT, que le partage déplace ; et la
réduction générale n'efface que des cotisations PATRONALES. Le gain net mensuel
au salaire moyen vaut **−144 € si les 23 points sont entièrement salariaux,
+73 € moitié-moitié, +275 € s'ils sont entièrement patronaux**. Le paramètre
laissé ouvert par la proposition pèse donc plus que la baisse de taux elle-même.
C'est la réserve la plus lourde de ce bloc.

**3. Le résultat au voisinage du SMIC est négatif, et il est juste.** La
réduction générale dégressive unique efface depuis 2026 la totalité des
cotisations patronales de son périmètre au niveau du SMIC — son coefficient
maximal, 40,21 %, est exactement leur somme. Un salarié au SMIC ne supporte donc
aujourd'hui que les 11,3 points salariaux. La proposition en prélève 23, dont 9
seulement sont effacés : elle prélève **plus**. Le croisement se fait un peu
au-dessus de 1,2 SMIC. Les cinq points capitalisés font à eux seuls la bascule —
sans eux le gain est positif à tous les niveaux de salaire —, et ils ne sont pas
perdus : ce compte reste au nom de l'assuré et se transmet.

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

Rien de tout cela ne touche une pension : retiré, le modèle calcule exactement
les mêmes six scénarios.

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
   elle est écrite.** Le dépôt la SERT, comme l'Italie, où le capital notionnel
   du défunt se partage : la part dérivée est reconduite telle quelle. L'autre
   chemin — la Suède, où un compte notionnel ne verse qu'à son titulaire —
   reste calculable sous `convention_reversion="supprimee"`, et il n'est pas le
   défaut parce qu'il est le plus flatteur : il rendrait 1,19 point de PIB au
   scénario 6, et de 0,4 à 1,2 point à chacun des autres.

   Ce que la correction coûte, par scénario, en point de solde moyen
   2026-2070 : scénario 2, −0,81 ; scénario 3, −0,23 ; scénario 4, −0,27 ;
   scénario 5, −0,09 ; scénario 6, −0,35. Le scénario 1 ne bouge pas d'un
   iota, son rapport valant un.

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

**Ce qui, en revanche, n'est pas une approximation** : l'égalité des scénarios
3 et 5 avec le système actuel sur toute la période observée. Elle est EXACTE, et
au sens strict — le scénario prospectif recopie la pension du scénario actuel
pour qui a liquidé avant la bascule. La page ne l'écrit pas en dur : elle teste
l'identité des courbes année par année, et les séparerait si la bascule était
avancée avant la dernière année publiée.

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
du COR — 2,45 % par an dans le scénario de référence — **corrigé de l'évolution
de la population d'âge actif**, qui recule de 10 % d'ici 2070. Cette correction
est un écart assumé avec le fichier d'hypothèses, qui suppose l'emploi salarié
constant au-delà de la dernière année observée. L'hypothèse d'emploi constant
est effectivement neutre pour l'indexation des comptes, qui ne dépend que d'un
taux de croissance ; elle ne l'est pas du tout pour une dépense rapportée au
PIB, où elle prêterait à la France de 2070 douze pour cent d'actifs qu'aucune
projection ne lui donne, et rendrait toutes les parts de PIB de la page
flatteuses d'un point. C'est le paramètre le plus discutable de la section, et
il joue dans un sens connu : le COR, lui, fait remonter les taux d'emploi, ce
qui explique une partie de l'écart entre ses 14,2 % et les nôtres en 2070 —
chiffrés plus bas, au paragraphe « Le contrôle externe ».

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
celle-ci : il trouve 13,9 % du PIB en 2024 et **14,2 % en 2070** (rapport annuel
de juin 2025, champ « ensemble des régimes légalement obligatoires, y compris
FSV, hors RAFP »). Le dépôt trouve 13,6 % et **19,4 %**. Trois dixièmes de point
d'écart au départ — l'affaire du périmètre, la répartition obligatoire des
Comptes de la protection sociale n'étant pas exactement celle du COR — et **cinq
points à l'arrivée**.

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
soixante-sept ans une fois la durée requise opposée. La grille part donc, en
moyenne, un peu plus tard que la France réelle ; l'âge conjoncturel de départ
que publie la DREES permettrait de le chiffrer, et il n'est pas dans le dépôt.

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
- 1037 tests couvrent le chargement, la fiabilité, la règle de certification, la
  concordance des tables de mortalité observées avec les espérances publiées, les
  propriétés du moteur et le comportement des scénarios : `python -m pytest tests`.
  Aucun test n'accède au réseau : les sources sont simulées.
- Les bases JORF et LEGI de la DILA sont interrogeables sans retélécharger
  leurs dumps : `python scripts/fetch/dila_index.py jorf --recuperer` rapatrie
  l'index plein texte publié sur la release `index-dila` du dépôt,
  `--mettre-a-jour` y applique les incréments quotidiens parus depuis, et
  `dila_cherche.py` l'interroge. L'index se reconstruit depuis le dump par
  `dila_index.py jorf` (une demi-heure, dump gardé en cache dans `data/brut/dila/`).
