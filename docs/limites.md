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
| Carrière longue | trois étapes, 2004, 2012, 2023 | **certifiée** pour 2023 (L. 351-1-1, D. 351-1-1) ; 2004 et 2012 transcrites |
| Trimestres accordés au titre des enfants | MDA à 4 puis 8 trimestres par enfant (1972, 1975) ; bonification de la fonction publique à 4 puis 2 (2004) | reprise des textes, non recontrôlée |
| Surcote parentale | 1,25 % par trimestre entre 63 ans et l'âge légal, quatre au plus | reprise des textes (L. 351-1-2-1), non recontrôlée |
| Durée requise par génération | table 1934-1975, 151 → 172 trimestres | **certifiée** depuis 1958 (L. 161-17-3) ; 1934-1957 transcrite |
| Durée de proratisation par génération | table 1900-1948, 150 → 160 trimestres | **certifiée** (R. 351-6 II) jusqu'à 1947 ; la ligne 1948 est la jonction avec la durée requise, que l'article ne fixe pas |
| Heures de SMIC pour valider un trimestre | 200 depuis 1972, 150 depuis 2014 | **certifiée** (R. 351-9) |
| Revalorisation des salaires portés au compte | 10 colonnes publiées, effets d'octobre 2017 à janvier 2026 | circulaires de la Cnav ; ailleurs, ancrage sur la plus proche |
| Âge légal par génération | table 1900-1975, 60 → 64 ans | **certifié** (D. 161-2-1-9), recontrôlé à chaque exécution |
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

### Ce qui reste hors du modèle, et pourquoi

Ces lignes ne sont pas des oublis : chacune demande une information que le
modèle n'a pas, ou décrit un dispositif qu'il représenterait faussement.

- **Pension de réversion.** Elle ne concerne pas l'assuré mais son conjoint
  survivant, et suppose de connaître un ménage. Hors périmètre par
  construction : le modèle décrit une carrière, pas une famille.
- **Bonifications de service et catégorie active.** Bonifications de
  dépaysement, de campagne militaire, du cinquième pour les emplois de
  sécurité ; ouverture à 57 ans, voire 52, pour les catégories actives. La
  bonification POUR ENFANTS, elle, est désormais servie : elle ne demande que le
  nombre d'enfants. Les autres supposent de connaître
  le CORPS d'appartenance et le détail des services, que la saisie ne demande
  pas. Conséquence mesurable : un fonctionnaire de catégorie active est traité
  comme un sédentaire, ce qui lui oppose l'âge d'ouverture du sédentaire — la
  décote, elle, est plafonnée à vingt trimestres dans les deux cas, si bien que
  l'écart de pension reste nul dès que la durée manquante dépasse ce plafond.
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
  propres à chacun). Le modèle ne compte que les trimestres réellement cotisés,
  ce qui rend la condition plus dure qu'elle ne l'est : quelques carrières
  hachées sont déclarées non ouvertes alors que le droit les ouvrirait.
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
- **Barème de la surcote entre 2004 et 2008.** Le taux n'était pas plat :
  0,75 % pour les quatre premiers trimestres, 1 % au-delà, 1,25 % pour les
  trimestres accomplis après 65 ans. Le modèle applique 0,75 % à tous, ce qui
  minore la surcote des liquidations de cette période — cinq années.
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

La page **Données** du site affiche l'état exact. En résumé :

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
| Minimum vieillesse (ASPA) | ancres 2006, 2009-2012, 2014, 2018-2020 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 815-1` |
| Minimum vieillesse (ASPA) | ancres 2007, 2016, 2017, depuis 2021 | haute / moyenne | publications — l'article n'est pas réécrit à chaque revalorisation |
| Minimum garanti, traitement de référence | 2004 et année courante | **certifiée** | Service des retraites de l'État, sa page du minimum garanti |
| Minimum garanti, traitement de référence | ancres intermédiaires | haute | non publiées : la page ne porte que l'ancre et l'année courante |
| Âge d'ouverture des droits par génération | 1900-1975 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 161-2-1-9` |
| Durée d'assurance requise par génération | 1958-1975 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `L. 161-17-3` |
| Durée d'assurance requise par génération | 1953-1957 | **certifiée** | DILA, base LEGI, décrets d'application des lois de 2003 et de 2010 |
| Durée d'assurance requise par génération | 1934-1942 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-45` II |
| Durée d'assurance requise par génération | 1943-1952 | haute | 160 vient de la règle générale, non d'un alinéa qui les nomme ; les 161-164 sont dans des décrets absents de la base |
| Coefficient de minoration par génération | 1900-1975 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-27` |
| Bornes de la carrière longue | 2023- | **certifiée** | DILA, base LEGI, `L. 351-1-1` et `D. 351-1-1` |
| Bornes de la carrière longue | 2004 et 2012 | moyenne / haute | versions abrogées des mêmes articles, transcrites |
| Durée maximale prise en compte par la proratisation | avant 1944 à 1947 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-6` II |
| Heures de SMIC à cotiser pour valider un trimestre | 1972 et 2014 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-9` |
| Années retenues au salaire annuel moyen, par génération | avant 1934 à 1948 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-29-1` |
| Décote de la fonction publique, coefficient et âge d'annulation | 2006-2019 | **certifiée** | DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 III |
| Barème du minimum garanti, montée en charge | 2004-2013 | **certifiée** | DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 V |
| Âge d'annulation de la décote, régime général | 1930-1955 | haute | calculé — l'âge d'ouverture certifié majoré de cinq ans, comme l'écrit `L. 351-8` ; recontrôlé à chaque exécution |
| Point d'indice de la fonction publique | 1996-2027 | **certifiée** | DILA, base LEGI, décret n° 85-1148 du 24 octobre 1985, article 3 |
| Point d'indice de la fonction publique | 1960-1995 | haute | OpenFisca-France, `point_indice_en_euros` — deux versions manquent au dump avant 1996 |
| SMIC horaire | 1997-2017, sauf 2002 | **certifiée** | DILA, base LEGI, décrets portant relèvement du SMIC |
| SMIC horaire | 1970-1996, 2002 et depuis 2018 | haute | OpenFisca-France, `smic_horaire_brut` |
| Plafond Sécurité sociale | 2002-2025 | **certifiée** | INSEE BDM, idbank 000822494 |
| Plafond Sécurité sociale | 1963, 1965-1981, 1984, 1987, 1988, 1990-1993, 1996-2001 | **certifiée** | DILA, base JORF, décrets portant fixation du plafond |
| Plafond Sécurité sociale | le reste de 1931-2001 | haute | OpenFisca-France, daté décret par décret — la notice ancienne du JORF n'a pas d'écriture stable |
| Revalorisation des salaires portés au compte | 10 colonnes, effets 2017-2026, perceptions depuis 1930 | haute | Cnav, circulaires de revalorisation, recoupées deux à deux |
| Taux de cotisation, régime général | 1967-2026 | moyenne | OpenFisca-France, recoupé à chaque exécution |
| Taux de cotisation, complémentaires du privé | Arrco 1962-2018, Agirc 1981-2018, Agirc-Arrco 2019- | moyenne | OpenFisca-France, taux effectifs par tranche, recoupés à chaque exécution |
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
| Valeur du point et taux, base des professions libérales | 2021-2025 | **certifiée** | CNAVPL, ses recueils statistiques |
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
python scripts/fetch/openfisca_cotisations.py  # taux de cotisation du RG
python scripts/fetch/openfisca_points.py       # valeurs du point, depuis 1947
python scripts/fetch/cdc_ircantec.py           # barèmes Ircantec, par son gestionnaire
python scripts/fetch/cnbf_baremes.py           # valeurs du point des avocats
python scripts/fetch/cnavpl_recueils.py        # valeur du point des professions libérales
python scripts/fetch/dila_legi_msa.py          # point de la complémentaire agricole (lent : 1,1 Go)
python scripts/fetch/dila_legi_minimum_contributif.py  # minimum contributif et plafond (lent aussi)
python scripts/fetch/dila_legi_parametres_retraite.py   # âges, durées, décotes par génération (lent aussi)
python scripts/fetch/openfisca_point_indice.py  # point d'indice et barème du minimum garanti
python scripts/fetch/dila_legi_point_indice.py # point d'indice, dans son décret (lent)
python scripts/fetch/dila_legi_smic.py         # SMIC, dans ses décrets de relèvement (lent)
python scripts/fetch/dila_legi_duree_requise.py # durée requise des générations 1953-1957 (lent)
python scripts/fetch/dila_legi_cnracl.py       # contribution employeur de la CNRACL (lent)
python scripts/fetch/dila_legi_decote_fonction_publique.py  # décote de la fonction publique (lent)
python scripts/fetch/dila_legi_minimum_garanti.py  # barème du minimum garanti (lent)
python scripts/fetch/erafp_valeurs_point.py    # valeurs du point du RAFP, par l'ERAFP
python scripts/fetch/jorf_plafond_securite_sociale.py  # plafond ancien, dans son décret (1,7 Go)
python scripts/fetch/sncf_contribution_employeur.py  # contribution SNCF, deux dumps (2,8 Go)
python scripts/fetch/dila_legi_minimum_vieillesse.py  # montant de l'ASPA, dans le code (lent)
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
d'accès et diffuse, elle, les séries longues — contrairement à l'API Melodi, qui
ne remonte pas avant les années 1990. Le recontrôle a confirmé la plupart des
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

* *Taux de cotisation d'avant octobre 1967, et des régimes autres que ceux du
  privé* — **la seule limite de cette liste qui reste ouverte**, et la seule
  dont on puisse dire par où elle passe sans pouvoir la refermer. Aucune
  transcription machine n'existe : ces taux viennent des ordonnances de 1945 et
  de leurs modificatifs, saisis à la main. Ont été essayés sans succès, pour
  éviter de refaire le trajet : les barèmes IPP, qui sont la source amont
  d'OpenFisca et ne commencent pas plus tôt que lui pour la CNAV (1967) ; et la
  Banque de données macroéconomiques de l'INSEE, dont la série de taux de
  cotisation vieillesse (idbank 000483633) ne porte que la part salariale et ne
  débute qu'en juillet 1993.

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
  donne les deux taux de cotisation — 8,23 % sur la tranche 1, 1,87 % sur la
  tranche 2. Ces valeurs sont dans le dépôt, certifiées, de 2021 à 2025 ; les
  millésimes antérieurs mettent la valeur dans un graphique et non dans une
  phrase, d'où le début de série.

  **Le moteur s'en sert désormais.** Ce qui bloquait n'était pas la donnée mais
  la forme du barème : le régime n'attribue pas un nombre de points
  proportionnel à la cotisation, mais **525 points au maximum sur la tranche 1
  et 25 sur la tranche 2**, soit 550 depuis 2015 — 450 et 100 avant. Un
  plafonnement en points est une règle de calcul, pas une colonne à ajouter :
  il a fallu l'écrire dans le moteur, sous la forme d'un champ `points_maximum`
  qui dit combien de points ouvre une assiette donnée. La fiche est scindée en
  ses deux tranches, qui se recouvrent depuis 2015 comme le fait la cotisation.
  Le nombre de points ne dépend alors pas du taux de cotisation, ce qui est
  heureux : c'est le barème que la caisse publie, pas le prix d'achat.
  Reste hors du modèle la période 1949-2003, assise sur des classes
  forfaitaires dont la grille n'est pas publiée : ces années restent au
  rendement instantané.

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
  servi à part, à l'identique dans les cinq scénarios : cela ne déplace aucun
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
-90,8 % à -84,6 % pour la génération 1920, de -88,8 % à -86,1 % pour 1930, de
-84,5 % à -84,3 % pour 1945 — et l'écart change de signe pour les carrières
entièrement postérieures à 1987 (-79,9 % à -80,4 % pour 1958), les arrêtés
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
  libérales (525 points au plafond, 25 sur la seconde tranche) et la
  complémentaire agricole (100 points pour 1 820 SMIC). La complémentaire des
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
  agricoles ;
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
- **polypensionnés** — chaque régime liquide désormais sur ses seules années,
  et la durée acquise dans chacun est comptée séparément. Restent hors du
  modèle les règles de COORDINATION interrégimes : proratisation croisée du
  salaire annuel moyen entre régimes alignés, et liquidation unique (LURA).

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

Le résultat, sur dix profils :

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

Trois bornes à connaître, et elles sont étroites :

* **le régime général seul.** L'Arrco du paquet publié est inutilisable : son
  code demande le paramètre `agirc_arrco.salaire_de_reference.salaire_reference_en_euros`,
  que les barèmes livrés ne définissent pas — ils portent
  `salaire_reference_prix_achat_valeur_nominale`. Toute liquidation postérieure
  à 2019 y lève une erreur. Or c'est la complémentaire qui portait les deux plus
  grosses erreurs de ce dépôt ;
* **les liquidations antérieures à 2025.** Ses barèmes s'arrêtent : valeur du
  point Agirc-Arrco en novembre 2024, revalorisations CNAV en 2023. Cinq des
  sept générations de la grille de cas types sont hors de portée ;
* **il rend zéro sans se plaindre.** Sans `simulation.max_spiral_loops`, la
  durée d'assurance, le coefficient de proratisation et la pension valent tous
  zéro, sans qu'aucune exception ne soit levée. Un oracle silencieusement nul
  valide tout : le récupérateur refuse donc d'écrire un profil dont la durée ou
  la pension serait nulle, et le test le revérifie.

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
l'atteint pas. Les cinq scénarios le servent donc à l'identique, à son propre
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
second, et le dépôt perdrait un de ses cinq résultats.

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

Un régime « incomplet » n'est pas un régime absent : les 53 fiches du catalogue
calculent toutes une pension. Ce qui manque est, chaque fois, un ÉTAGE ou un
BARÈME qu'aucune source publique ne donne en série. Le tableau dit lequel, ce
qui le remplace, et **dans quel sens** l'approximation joue — car un modèle dont
on ignore le sens de l'erreur ne se corrige pas dans la tête du lecteur.

| Régime | Ce qui manque | Ce qui le remplace | Sens et ordre de grandeur |
|---|---|---|---|
| Professions libérales (CNAVPL) | la SECTION B du complémentaire des notaires, dont les bornes de classes ne sont publiées nulle part ; le volet CAPITALISÉ de la CAVP ; le complémentaire de la CAVOM d'avant 2016, qui prélevait par classes et dont la grille n'est nulle part ; la grille des classes de cotisation du régime de BASE d'avant 2004 | le régime de base, en points plafonnés à 550, PLUS le complémentaire de la section : les DIX sections en ont un maintenant — CARMF, CARCDSF, CNBF, CAVEC, CAVP (volet réparti), CARPIMKO, CARPV, CAVOM (depuis 2016), CAVAMAC, CPRN (section C), et la Cipav pour le statut générique | **sous-estime** la pension d'un notaire de près de quatre dixièmes de son complémentaire, et celle d'un officier ministériel de tout son complémentaire d'avant 2016. Pour la CAVAMAC et la CPRN, l'assiette elle-même est reconstituée par un FACTEUR moyen — commissions, produits de l'office — et ne décrit aucun assuré en particulier |
| Marins (ENIM) | la grille des salaires forfaitaires par catégorie et par année, qui est l'assiette réelle du régime | le revenu déclaré, plafonné comme au régime général | **indéterminé** : la grille est plus favorable que le salaire réel aux bas revenus, moins au-delà. L'écart porte sur l'assiette, donc sur la pension ET sur le compte notionnel, en partie compensé |
| Avocats (CNBF) | la cotisation forfaitaire de base, de 363 à 1 988 €/an selon l'ancienneté ; les tranches de la grille complémentaire d'avant 2019 | seule la cotisation proportionnelle de 3,20 % alimente le compte ; les années d'avant 2019 restent au rendement instantané | **sous-estime le flux versé**, donc la pension notionnelle, sans toucher à la pension actuelle — qui est forfaitaire et ne dépend pas de la cotisation. L'écart joue donc contre les scénarios notionnels |
| Non-salariés agricoles | le barème de points du régime de base (23 à 113 points par tranche de revenu), que personne ne publie ; les points gratuits de la RCO — 66 par an aux conjoints et aides familiaux avant 2011, dans la limite de 17 ans | la retraite forfaitaire et la RCO, dont le barème en points est public | **sous-estime** la pension des carrières de conjoint et d'aide familial, qui sont précisément les plus modestes du régime |
| Régimes spéciaux résiduels | des paramètres certifiés : les taux et les âges sont saisis au niveau `estimee`, caisse par caisse | les textes fondateurs, sans recontrôle | **indéterminé**, et c'est le seul cas où le dépôt ne sait pas dire le sens. Ces régimes portent peu d'assurés ; leur poids dans les agrégats est faible |

**Ce qui a été refermé depuis la version précédente de ce tableau.** Le régime
de base des avocats était rangé ici comme « à scinder » : il l'est, et sa
pension ne dépend plus du revenu. La complémentaire agricole y figurait sans
valeur de point : elle en a une, certifiée de 2005 à 2024, tirée du code rural.
Le régime de base des professions libérales y figurait sans barème : il a le
sien, plafonné en points comme la caisse le publie.

**Pourquoi ce qui reste ne se referme pas de la même façon.** Les limites
refermées cette année l'ont toutes été par un changement de CLÉ D'ENTRÉE — un
numéro d'article plutôt qu'un mot, un IDBANK plutôt qu'une page, un lecteur de
format écrit à la main. Ce qui subsiste ci-dessus n'est pas d'une autre
difficulté technique : ce sont des barèmes que personne ne publie sous aucune
forme, ni en série, ni en texte réglementaire, ni en PDF. Les chercher encore
supposerait de les reconstituer à partir de cas individuels, ce qui produirait
un chiffre plus précis d'apparence et pas davantage de vérité.

Le catalogue compte **53 régimes**, actuels et disparus. Il est structurellement
extensible : ajouter un régime consiste à écrire une fiche YAML conforme à
`data/reference/regimes/_schema.yaml`, sans toucher au moteur.

### Les régimes qui manquent encore, et ce qui bloque chacun

**Cette liste n'est pas dérivée d'un fichier, et c'est une limite en soi.**
Aucune source du dépôt n'énumère les régimes français : la série DREES agrège
en treize systèmes, le panorama du COR est un document saisi à la main, et les
portails officiels ne servent pas de liste exploitable. Ce qui suit vient donc
de la connaissance du domaine, non d'un inventaire vérifiable — un régime peut
manquer à cette liste des manquants.

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

**Les trois autres, et le mur devant chacun :**

| Régime | Population | Ce qui bloque |
|---|---|---|

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
| **CARPV**, vétérinaires | quatre classes, de 10 234 à 16 856 € en 2026 | 39,54 € (2026) | **602,00 €**, déduit : chacune des quatre classes divise exactement par ses points en ce montant, et le décret annuel fixe ce prix depuis 2016. FICHE ÉCRITE |
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

Ce qui reste au volet capitalisé de la CAVP : sa grille de classes, composée
dans une police sans table de correspondance. Ce n'est pas de la répartition, et
le dépôt saurait le dire avec `hors_repartition` — mais pas le chiffrer.

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
« 37 statuts », « 53 régimes » —, parce que ce sont des chiffres de données et
non de prose, et que le dépôt s'est déjà fait prendre à en laisser dériver un.

### Les deux dernières sections que le décret annuel débloquait

Huit des dix sections libérales ont maintenant leur fiche. Les deux qui
manquaient encore — vétérinaires et officiers ministériels — sont tombées pour
des raisons opposées : la première publiait tout sans qu'on l'ait lue, la
seconde ne publie qu'une moitié de son histoire.

**La CARPV publie sa grille en clair, et l'arithmétique y ajoute le prix du
point.** Le tableau HTML de la caisse donne quatre classes, leurs bornes de
revenus, leur cotisation ET les points qu'elles ouvrent : 10 234 € pour 17
points jusqu'à 76 994 € de revenus, puis 12 642 € pour 21, 15 050 € pour 25 et
16 856 € pour 28. Ces quatre quotients valent tous **602,00 €** — la valeur
d'achat du point, que la caisse n'écrit nulle part et que le décret annuel fixe
pour cette section depuis 2016. Avec la valeur de service de 39,54 €, le
rendement vaut 6,5681 % sur les quatre classes à la fois, au dix-millième près.

Cette identité vaut mieux qu'un contrôle : elle permet de reconstruire les
grilles de 2016 à 2024 en multipliant les points de chaque classe par le prix
du point de l'année — 446 € en 2016, 570,26 € en 2024. Reporter la grille de
2026 par le plafond, comme le fait la Cipav faute de mieux, aurait surestimé la
cotisation de 2016 de 8,5 %. Ce que cette reconstruction suppose, et qu'il faut
dire : que les quatre classes ouvraient déjà 17, 21, 25 et 28 points. Le décret
publie le prix, jamais le nombre.

Ce qui manque encore chez elle : les BORNES de revenus d'avant 2026, reportées
par le plafond, et toute grille d'avant 2016 — le décret ne fixait alors pas un
prix du point mais un **taux d'appel**, monté de 78,5 % en 2002 à 104 % en 2015,
appliqué à des montants que rien ne publie. Une cotisation de 2002 est donc
surestimée d'un quart environ. Les livrets annuels de la caisse porteraient ces
bornes, mais ils sont composés dans une police sans table de correspondance.

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
apporte 2,50 points sur les 7,66 appelés en 2026. Les compagnies ne sont pas
l'employeur d'un agent général ; le statut reste marqué `sans_employeur`, et le
moteur porte donc cette part au compte de l'agent. La fiche porte le partage
exact — 5,16 / 7,66 —, et un test l'y oblige, mais les scénarios 2 et 3 prêtent
encore à l'agent un effort qu'il n'a pas fourni.

**La CPRN, elle, était bien bloquée par son assiette** — les produits de
l'office, pas le revenu du notaire — et c'est un rapport d'inspection, non la
caisse, qui a fourni la clé. L'IGAS (rapport n° 2012-110P) décrit la règle qui
fixe le prix du point de la section C :

> « Cette valeur d'acquisition est calculée de façon à ajuster le nombre de
> points attribué à chaque notaire de façon à ce que la moyenne sur l'ensemble
> des notaires soit toujours égale à 900 points. »

Avec le prix que publie le décret annuel — 17,69 € — et le taux — 4,10 % —, les
produits moyens d'un office valent 900 × 17,69 / 0,041 = **388 317 €**. Le
revenu moyen s'obtient par l'autre bout, en retranchant de la cotisation moyenne
que publie la caisse (32 864 €, tous régimes) la section C (15 921 €) et une
section B de classe 3 (9 515 €) : il reste 7 428 € de régime de base, que son
barème renvoie à **190 000 €** de revenu. D'où un facteur de **2,04**, borné par
un contrôle indépendant — le Conseil supérieur du notariat publie 9,0 milliards
d'euros de produits pour 17 305 notaires, soit 520 000 € par notaire, du même
ordre. C'est une convention, la fiche le dit, et elle porte `fiabilite: estimee`
pour cette raison.

**La moitié forfaitaire du régime reste dehors, et pour une raison de
principe.** La section B a huit classes, de 10 à 80 points, et sa cotisation
vaut « le nombre de points de la classe multiplié par 115 % du coût
d'acquisition du point B » — tout est publié sauf une chose : les bornes de
produits qui rangent un notaire dans sa classe, « déterminées par le conseil
d'administration chaque année par référence à la moyenne des produits de base du
notariat ». Et avant 2014 il n'y avait pas de bornes du tout : la section était
« en partie facultative », écrit l'IGAS, le notaire y choisissait sa classe.
Le dépôt ne prête jamais à personne un choix qu'il ne peut pas connaître — même
règle que pour les classes du RAAP d'avant 2017. Ce qui manque se chiffre :
environ 9 500 € pour le notaire moyen en 2025, contre 15 900 € de section C.

**Un mécanisme de plus dans le moteur, et le troisième cette année.** Après la
cotisation par classes et la cotisation forfaitaire qui s'ajoute à un taux,
voici l'assiette qui n'est pas le revenu. Le champ est porté des deux côtés du
portage, et le fichier de schéma le documente. Il ne sert qu'à ces deux
sections, et il faut espérer qu'il n'en serve jamais davantage : un facteur
moyen est une approximation grossière, et la seule chose qui la rende acceptable
est qu'elle remplace une absence.

### La part patronale du public, et ce qu'on n'en sait pas

Les scénarios 4 et 5 ajoutent à la part salariale ce que verse l'employeur. Pour
un salarié du privé, la fiche du régime le porte — `part_salariale` en donne la
répartition, recoupée à OpenFisca année par année. Pour un agent public, elle
n'est dans aucune fiche : le modèle la lit dans
`legislation/contribution_employeur_public.csv`, qui ne couvre que trois régimes
et pas sur toute leur durée. Partout ailleurs, la part patronale est **estimée**
par l'effort d'un salarié du privé de la même année — jamais laissée à zéro, qui
ferait retomber les scénarios 4 et 5 sur les 2 et 3 sans le dire — la fiabilité
de l'année retombe à `estimee`, et le nombre d'années concernées est affiché
sous la simulation.

| Régime | Couvert | Découvert | Ce qui manque |
|---|---|---|---|
| Fonction publique d'État | 1995-2026 | 1930-1994 | rien à retrouver : l'État ne versait aucune cotisation, les pensions étaient payées sur crédits budgétaires, et le plus ancien chiffrage a posteriori — le jaune « pensions » — s'arrête à 1995 |
| CNRACL | 1948-2025 | 1945-1947 | le décret fondateur date du 19 septembre 1947 ; la convention « taux au 1er janvier » fait donc commencer la série en 1948 |
| SNCF | 2007-2018 | 1930-2006, 2019- | les composantes T1 et T2 datent du décret du 28 juin 2007 ; OpenFisca cesse de les suivre après la fermeture du régime aux nouveaux entrants |
| FSPOEIE, RATP, IEG, marins, mines, CRPCEN, Banque de France, Opéra, Comédie-Française, port de Strasbourg, SEITA, chemins de fer secondaires | rien | tout | aucune série de taux employeur publiée sous une forme exploitable. Pour ces douze régimes, la part patronale des scénarios 4 et 5 est celle d'un salarié du privé de la même année, et le modèle le dit |

Deux conséquences à garder en tête.

**Plus une carrière publique est ancienne, moins le scénario 4 s'écarte du
scénario 2** — non parce que le financement d'alors ressemblait à celui du
privé, mais parce qu'on ne le connaît pas.

**Le scénario 5 ne voit presque jamais la contribution publique.** Il n'ouvre
son compte qu'à la bascule, et à compter de la bascule le régime unique remplace
tous les régimes : la part patronale y est celle du statut pivot privé, pas
celle d'un employeur public. Ce que le scénario 5 mesure après 2026 est donc la
répartition du régime unique, non le financement de la fonction publique — qui,
par construction, n'existe plus.

---

## 5. Ce que le modèle ne calcule pas, et pourquoi

Ce qui suit n'est pas une liste de manques mais un **périmètre**, et chaque
ligne dit ce qu'elle coûte et dans quel sens. Une limite qu'on sait mesurer
n'est plus une limite : c'est un paramètre connu du résultat.

- **L'équilibre financier du système.** Le modèle calcule des droits
  individuels. Il ne vérifie pas que la somme des pensions servies égale la
  somme des cotisations encaissées. Il porte désormais une pyramide des âges —
  celle de l'INSEE, observée puis projetée —, ce qui lui permet de dire ce que
  chaque système COÛTERAIT ; il lui manque encore, pour un solde, l'assiette des
  cotisations et une règle de pilotage. Un système notionnel réel
  exige en outre un **coefficient d'équilibre** et un fonds de réserve, qui
  ajusteraient à la baisse ou à la hausse toutes les pensions du scénario 2 par
  un même facteur. Ce facteur étant commun, il déplacerait les niveaux sans
  toucher aux ÉCARTS ENTRE CARRIÈRES, qui sont l'objet du modèle.
  La page **Coût** donne le premier terme de ce bilan — ce qui a été VERSÉ,
  observé et certifié de 1959 à 2024 — et jamais le second. Un coût n'est pas
  un solde : un système qui coûterait quatre fois moins servirait quatre fois
  moins, ce qui est une autre affaire.

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

- **Les carrières réelles.** Les carrières sont reconstituées à partir d'un
  profil paramétrique. Une simulation à partir d'un relevé de carrière réel est
  possible par `Carriere.depuis_lignes`, et c'est le chemin le plus exact ; mais
  l'IMPORT AUTOMATIQUE du relevé Info-Retraite n'est pas implémenté, et ne peut
  pas l'être : le répertoire de gestion des carrières uniques n'est pas ouvert
  au public, et son accès passe par une authentification personnelle qu'un
  script ne saurait porter sans détenir les identifiants de l'assuré.

- **La coordination interrégimes.** Chaque régime liquide sur ses seules
  années, et la durée acquise dans chacun est comptée séparément — c'est le
  droit. Restent dehors la **proratisation croisée** du salaire annuel moyen
  entre régimes alignés et la **liquidation unique** (LURA), qui, depuis 2017,
  fait calculer par une seule caisse la retraite d'un polypensionné des trois
  régimes alignés. L'effet est de second ordre pour une carrière
  mono-affiliée — le cas ordinaire — et joue plutôt à la hausse pour un
  polypensionné, dont le salaire annuel moyen unique est calculé sur les
  meilleures années tous régimes confondus.

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
de chaque génération dans la masse de l'année. Ce rapport porte trois
approximations, énoncées sur la page :

1. **Les effectifs de génération ne sont plus supposés.** Cette page a d'abord
   pesé toutes les générations à égalité, faute de pyramide des âges ; elle
   porte désormais celle de l'INSEE, observée jusqu'en 2023. On sait donc
   maintenant ce que valait l'hypothèse levée : elle déplaçait l'écart cumulé du
   scénario 2 de six dixièmes de point sur soixante-six ans (−77,3 % contre
   −77,9 %). C'était peu, et c'est désormais mesuré plutôt qu'argumenté.
2. **Les douze cas types pèsent d'un poids égal.** Ils ne décrivent pas la
   population active : il y a moins d'agents de conduite que de salariés au
   salaire moyen. C'est la convention de la grille des cas types, reconduite
   ici plutôt que remplacée par une pondération qu'aucune source ne fixerait.
   Le sens du biais est connu : les cas types à départ très précoce — SNCF,
   catégorie active — sont ceux que le notionnel pénalise le plus, et ils sont
   surreprésentés. Le rapport affiché est donc plutôt un PLANCHER.
3. **Avant 1975, la reconstitution est mince.** La répartition ne commence
   qu'en 1941 : les générations antérieures à 1880 n'ont, dans ce modèle,
   aucune pension, et plusieurs régimes n'existaient pas encore. Les premières
   années reposent sur deux ou trois générations et la moitié des cas types.
   Elles pèsent peu dans le cumul — la dépense de 1959 vaut 0,5 % de celle de
   2024 en euros courants — mais leur rapport ne vaut pas ce que valent ceux
   d'après 1980.

**Ce qui, en revanche, n'est pas une approximation** : l'égalité des scénarios
3 et 5 avec le système actuel sur toute la période observée. Elle est EXACTE, et
au sens strict — le scénario prospectif recopie la pension du scénario actuel
pour qui a liquidé avant la bascule. La page ne l'écrit pas en dur : elle teste
l'identité des courbes année par année, et les séparerait si la bascule était
avancée avant la dernière année publiée.

---

## 5 ter. La trajectoire projetée : ce qu'elle suppose, et ce qu'elle vaut

La seconde moitié de la page **Coût** projette les cinq systèmes de 2025 à 2070.
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
qui explique une partie de l'écart entre ses 14,2 % et nos 14,8 % en 2070.

**Ce qui n'est pas modélisé.** Le taux de couverture est supposé constant : le
modèle compte des générations, non des cotisants, et suppose que la même
proportion de chacune perçoit une pension et que la carrière type ne change pas.
Un recul de l'âge effectif de départ, une carrière plus longue ou plus hachée
déplaceraient la trajectoire. Aucune règle de pilotage n'est appliquée non plus :
un système notionnel réel porte un coefficient d'équilibre qui ajusterait toutes
ses pensions par un même facteur — commun, donc sans effet sur les écarts entre
carrières, mais avec effet sur les courbes de cette page.

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

**Le contrôle externe.** Le COR projette la même grandeur avec un modèle de
population complet et une méthode qui n'a rien de commun avec celle-ci : il
trouve 13,9 % du PIB en 2024 et **14,2 % en 2070** (rapport annuel de juin 2025,
champ « ensemble des régimes légalement obligatoires, y compris FSV, hors
RAFP »). Le dépôt trouve 13,6 % et 14,8 %. Trois dixièmes de point d'écart au
départ — l'affaire du périmètre, la répartition obligatoire des Comptes de la
protection sociale n'étant pas exactement celle du COR — et six dixièmes à
l'arrivée. Deux modèles indépendants à un demi-point l'un de l'autre : c'est le
meilleur contrôle dont cette page dispose, et il ne vaut que ce que vaut une
concordance — elle rend une erreur grossière improbable, elle ne rend juste
aucun des deux.

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
- 529 tests couvrent le chargement, la fiabilité, la règle de certification, la
  concordance des tables de mortalité observées avec les espérances publiées, les
  propriétés du moteur et le comportement des scénarios : `python -m pytest tests`.
  Aucun test n'accède au réseau : les sources sont simulées.
