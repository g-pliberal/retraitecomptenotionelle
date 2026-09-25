# Limites — les récits

*Archive, gelée.* Ce fichier garde, à l'identique, les sections de récit de
`docs/limites.md` : chacune raconte un défaut trouvé, sa correction, et ce
qu'il valait ce jour-là. La phase 1 de l'architecture les en a retirées le
25 septembre 2026 (`docs/architecture.md`, § 9.3 et annexe B), pour que
`limites.md` ne dise plus que ce qui vaut aujourd'hui. Chaque section est
précédée des titres qui la contenaient, pour qu'on sache où elle était ; ces
titres-là restent aussi dans `limites.md`. Rien ne s'y réécrit, et
`python scripts/conservation.py` vérifie que rien ne s'en perd.

# Limites — à lire avant d'utiliser un chiffre

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

**Onze erreurs de calcul.**

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
  5 % de pension, et le modèle servait zéro. Il l'a ensuite servie sur une
  fenêtre fausse, de 63 ans à l'âge légal, et à la seule condition d'avoir la
  durée requise à 63 ans : zéro trimestre à la génération 1965 née après mars,
  un à 1966, deux à 1967, trois à 1968. Le texte compte les trimestres cotisés
  de l'année qui PRÉCÈDE l'âge légal, au-delà de la durée requise, dès que cet
  âge atteint 63 ans : quatre au plus à chacune de ces générations. Corrigé le
  23 septembre 2026.
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

**Deux activités à la fois : ce que le cumul ne dit pas encore.** Une
activité déclarée cumulée a sa propre ligne, et le scénario 1 la traite
comme le droit : chaque régime sur son revenu, la durée tous régimes bornée à
quatre trimestres par année civile, les régimes alignés réunis sur la somme
de leurs revenus. Trois approximations restent. Le compte notionnel porte la
cotisation de chaque activité sous ses propres bornes, et le plafond global
d'assiette du modèle s'y applique activité par activité, non sur leur somme.
Deux statuts qui versent au même régime complémentaire — deux employeurs, l'un
cadre, l'autre non — y cotisent chacun sous un plafond entier : la règle qui
répartit le plafond entre plusieurs employeurs n'a été ni lue ni modélisée.
Et la fiche de paie de la
page Rémunération ne montre que l'activité principale.

## 1. État de certification des données

### Ce que le recontrôle a trouvé, série par série

Ce qui suit est le registre des recontrôles et des corrections, série par
série, chacun daté : il dit ce qu'une lecture a trouvé le jour où elle a été
faite, et ce qu'elle a déplacé ce jour-là. Le tableau d'en haut dit l'état
d'aujourd'hui.

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
vingt-huit entrées qui suivent, **seize ont été refermées par une source trouvée**, **deux
par la mesure du biais** qu'elles laissent — un biais chiffré n'est plus une
inconnue, il se retranche — et **quatre à moitié** : le plafond ancien, dont
trente et une années sur soixante et onze sont désormais lues dans leur décret ;
la contribution de la SNCF, cinq années sur douze ; celle de la CNRACL d'avant
1993, cinq sur quarante-cinq ; et le minimum vieillesse, neuf ancres sur
quatorze, qui occupe deux entrées — ses montants servis, puis son montant
dans le code. Ces demi-fermetures se ressemblent : la source a été trouvée et lue,
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

## 2. La règle d'indexation domine le scénario rétroactif

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

## 4. Régimes incomplets, et de combien

### Les régimes entrés depuis, et ce que chaque caisse publie

Ce qui suit est le relevé de ce que chaque dépouillement a fait entrer, et de
ce que chaque caisse publiait le jour où elle a été lue : des valeurs datées,
des simulations mesurées le jour où leur fiche est entrée. Les fiches, elles,
portent l'état d'aujourd'hui.

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
caisse. Carrière de 25 à 55 ans, génération 1965, en euros courants, décote
de 2012 comprise (voir « Le navigant n'avait pas de décote », plus bas) :

| Revenu | Pension actuelle | Notionnelle | Part patronale comprise |
|---|---|---|---|
| 2 × salaire moyen | 52 121 € | 9 426 € | 25 944 € |
| 4 × | 98 144 € | 17 492 € | 49 627 € |
| 6 × | 164 598 € | 25 697 € | 73 673 € |

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
6 %), qui sont depuis entrés au catalogue (voir « L'IRCEC compte des
années », plus bas).

**La CARMF publie ses chiffres clés sur deux pages** : 11,8 % des revenus nets
dans la limite de trois plafonds et demi — 19 849 € de cotisation maximale en
2026 —, 11,52 points par an au maximum, valeur de service 77,14 € à 62 ans. Ces
trois chiffres donnent un prix d'achat de 1 723 € et un rendement de 4,48 %.

Ce que la CARMF change à une simulation de médecin est exactement ce que ce
document annonçait sans pouvoir le combler — carrière de 25 à 64 ans, à trois
fois le salaire moyen, mesurée le jour où la fiche est entrée. Ces chiffres ne
se recalculent plus tels quels : `profession_liberale` porte depuis la
complémentaire de la Cipav, et n'est plus la base seule.

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
  une assiette trop basse, il ne l'annule pas).

La série historique de la CARMF manquait aussi : la caisse ne publie que
l'année en cours. Elle a été trouvée depuis, dans sa chronologie, et le
rendement est porté année par année de 1983 à 2026 (voir « Ce que la
chronologie de la CARMF a fini par dire », plus bas).

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
| **CIPAV**, interprofessionnelle | 9 % jusqu'à un plafond et 22 % d'un à trois depuis 2023 ; huit CLASSES avant | 2,89 € (2026) | **47,40 €**, publié — voir la troisième passe ci-dessous. FICHE ÉCRITE |
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
« 63 statuts », « 74 régimes » —, parce que ce sont des chiffres de données et
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

### La garantie du scénario 6, mesure par mesure

Ce qui suit est le journal des mesures qui ont établi la garantie, chacune
datée : ses chiffres sont ceux du jour où elle a été faite, et plusieurs ont
bougé depuis. Ce que la garantie coûte aujourd'hui est au paragraphe
précédent, que la prose recalcule.

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
facteur vaut 0,61 en 2020, parce qu'un compte rétroactif ne rend que ce qui a
été cotisé, et 1,14 en 2070, les pensions montant avec les salaires face à un
plancher indexé sur les prix. L'effectif suit les têtes de 65 ans et plus de la
grille, sur l'échelle des retraités de la DREES. La trajectoire porte
**0,58 % du PIB en 2026** (18 milliards d'euros de 2026, 3,2 millions de
bénéficiaires), décroissant à 0,40 % en 2070 (15 milliards, 2,8 millions),
soit 731 milliards constants cumulés sur la projection ; et le passé, où le
même déplacement est appliqué à rebours, en porte 1 593 depuis 1959.

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
une pension majorée de référence non chiffrée — contre 17,4 milliards de
garantie aux pensions du scénario 6 la même année, à un ayant droit sur deux :
**9,5 milliards de plus pour l'impôt**, borne haute puisque le total remplacé
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

Sept nombres de ce calcul sont des hypothèses sans source, et `Parametres` les
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
Le modèle prend ce poids dans l'effectif de chaque sexe que publie le classeur
de caractéristiques de la même enquête (`CaracteristiquesRetraites.part_femmes`) ;
`donnees.distribution.part_femmes` le retrouve par les moindres carrés et
refuse un fichier dont les trois colonnes ne se répondraient plus ;
`test_les_deux_sexes_recomposent_la_colonne_dont_le_cout_est_tire` tient le
raccord. Ce que cela déplace : la part des femmes parmi les bénéficiaires passe
de 68 à 66 %, la durée d'une avance de 20,5 à 20,4 ans, le nombre d'avances par
succession de 1,28 à 1,29, et la couverture ne bouge pas, 37 % des deux côtés.
**Le COÛT de la garantie dépend de ce poids depuis que chaque sexe est déplacé
du sien** : à `r = 1` et sous un plancher unique, il serait lu directement sur
la colonne « ensemble » ; au rapport mesuré et aux deux planchers mélangés, il
est recomposé des deux colonnes de sexe, pesées par ce poids — lu à 56 % plutôt
qu'à 52,8 %, il monterait de 2,7 %. Une réserve demeure, et elle va dans l'autre
sens : le poids lu est celui de TOUS les retraités de l'enquête, quand les
bénéficiaires ont 65 ans et plus. C'est la convention que le modèle applique
déjà à la FORME de la distribution — « les retraités de moins de 65 ans sont
supposés répartis comme les autres » —, et la tenir aussi sur le sexe est la
seule façon de ne pas mêler deux populations ; une distribution par sexe des
seuls 65 ans et plus ferait bouger les deux ensemble.

Le patrimoine des retraités selon leur PENSION n'est publié nulle part : c'est le
fichier individuel de l'enquête qui le donnerait, et il se commande, action
47. Le réglage `reprise` remplace la part calculée par un nombre. Au réglage
par défaut, en 2070 : 15,4 milliards versés, 8,0 repris, 7,4 nets ; de 2025,
première année projetée, à 2070 : 731 versés, 239 repris, 491 nets. Deux choses que le calcul ne voit
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
proportion, sexe par sexe. *Précisé le 23 septembre 2026* : « seules » veut
dire ici HORS COUPLE, au sens de l'ASPA, dont la personne seule est celle qui
ne vit ni mariée, ni pacsée, ni en concubinage — qu'elle vive ou non avec un
enfant ou un proche. C'est la grandeur que le plancher majoré demande, et celle
que le modèle lit. Celles qui vivent réellement seules dans leur logement sont
moins nombreuses : 41,5 % des femmes et 21,6 % des hommes, sur les mêmes années
et avec la même table. Les deux se composent — les femmes vivent seules
plus souvent ET tombent sous le plancher plus souvent —, si bien qu'un partage
global les manquerait.

| | Garantie 2024 | 2026, % du PIB | Cumul 2025-2070 |
|---|---|---|---|
| Plancher majoré pour tous *(jusqu'au 21 septembre 2026)* | 22,0 Md € | 0,74 % | 918 Md € |
| **Pesé par le recensement** | **17,4 Md €** | **0,58 %** | **731 Md €** |
| Plancher de base pour tous | 12,5 Md € | 0,42 % | 526 Md € |

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
2 909 millions en 2020, minimum contributif et minimum garanti réunis. Aucune
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
0,834 à 0,821-0,825. **Ce qu'il ferait au coût reste sous le pour cent** — 17,4
milliards de garantie en 2024 deviennent 17,5, et la part de PIB de
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

### L'IRCEC compte des années, et le modèle lui opposait des trimestres

Les trois fiches de l'IRCEC — le RAAP des artistes-auteurs, le RACD des
auteurs dramatiques, le RACL des compositeurs — renvoyaient toutes à la décote
du régime de base : 1,25 % par trimestre manquant jusqu'à soixante-sept ans.
Le guide 2026 de la caisse ne donne pas de barème, il écrit seulement
« coefficient de minoration éventuel ». Les règlements, eux, en donnent un, et
ce n'est pas celui-là : « 2,5 % par année pour chacune des deux premières
années manquantes ; 5 % par année manquante supplémentaire », ou les
coefficients du régime de base « si cela est plus favorable à l'adhérent ».
Et la pension est servie sans minoration dès l'âge légal si celle du régime
de base l'est au taux plein. À soixante-deux ans, sans la durée, l'IRCEC
retire 20 % ; la fiche en retirait 25.

**Lu au Journal officiel, par l'index du dépôt, et non chez la caisse
seulement.** Le barème vient de l'arrêté du 21 novembre 2013
(JORFARTI000028254004), qui a réécrit les trois règlements au 1er janvier 2014.
Son annexe chiffre la minoration trimestre par trimestre : un à quatre
trimestres valent la première année entière, cinq à huit la deuxième. Une
année entamée compte donc entière, et c'est ce que `_abattement_ircec` fait.
L'arrêté du 17 avril 2024 (JORFARTI000049490796) a supprimé les barèmes par
génération ; celui du 13 mai 2025 (JORFARTI000051592840) a enfin aligné le
RACL, qui jusque-là minorait de 5 % par année sans marche à 2,5 % et sans
renvoi au régime de base, et ne connaissait que l'âge pour le taux plein. Les
fiches sont coupées en conséquence : RAAP et RACD depuis 2014, RACL de 2014 à
2024 puis depuis 2025 (`abattement_points: ircec` et `ircec_age_seul`).

**Ce qui reste hors de la fiche, et pourquoi.**

* *Avant 2014*, le règlement servait le taux plein à soixante-cinq ans et
  minorait l'anticipation selon un tableau que l'arrêté de 2013 remplace sans
  le reproduire. Les périodes antérieures gardent la décote du régime de base,
  faute de lui.
* *Les générations nées avant 1955* avaient de 2014 à 2024 leurs propres
  coefficients : 5 % par année (RAAP) ou 6 % (RACD, RACL) jusqu'à soixante-cinq
  ans pour les générations nées avant 1953, un tableau pour 1953 et 1954. La
  fiche leur applique le barème des générations suivantes. Elles avaient toutes
  soixante-sept ans en 2021 : l'écart ne touche que des départs anticipés
  d'avant cette date.
* *L'annexe de 2013 contredit ses propres articles* pour les générations 1955
  et suivantes : elle donne 5 % dès la première année au RACD, dont l'article
  dit 2,5, et 2,5 % au RACL, dont l'article dit 5. Les deux colonnes semblent
  interverties. La fiche suit les articles, qui sont ce que les arrêtés de
  2024 et 2025 ont gardé.
* *Les plafonds de points* — 120 000 au RACD, 55 000 au RACL, 2 750 par an au
  RACL — et les *minimums de liquidation* (30 points au RAAP, 900 au RACD, 850
  au RACL, en deçà desquels la caisse verse un capital ou rembourse) ne sont
  pas appliqués : le modèle ne compte pas de points pour ces régimes, il
  applique un rendement à la cotisation.
* *Le taux aménagé de 4 % au RAAP* sur les revenus déjà soumis au RACD ou au
  RACL n'est pas appliqué : la carrière ne dit pas quelle part du revenu
  relève de quel régime.

### Ce que la même lecture de l'IRCEC a encore rendu

Une seconde session a lu les mêmes règlements le même jour, sans savoir que
la première les avait lus (action 89). Elle n'y a pas trouvé autre chose que le
barème de minoration ; elle y a trouvé ce qui l'entourait.

**La majoration pour trois enfants n'était servie par aucune des trois
fiches.** L'article 28 du règlement du RAAP, dans la rédaction de l'arrêté du
21 novembre 2013, la pose en une phrase — « il est majoré de 10 % au profit de
l'adhérent ayant eu au moins trois enfants », ou les ayant élevés neuf ans
avant leurs seize ans —, et l'arrêté du 17 avril 2024 a donné la même à
l'article 23 du RACD. Le règlement du RACL n'en porte aucune, et le guide 2026
de la caisse l'écrit en creux : sa formule du RACL est la seule des trois sans
« majoration familiale ». Portée depuis 2014 au RAAP, depuis 2024 au RACD ;
une mère de trois enfants retrouve 10 % de ses pensions d'auteur.

**Le RAAP des auteurs dramatiques et des compositeurs était prélevé au double
du taux.** La section précédente l'écarte — « la carrière ne dit pas quelle part
du revenu relève de quel régime » —, mais le décret ne regarde pas le revenu :
il regarde la personne. Le II de l'article 2 du décret n° 62-420, depuis le
1<sup>er</sup> janvier 2016 : « Pour les personnes tenues de cotiser aux
régimes […] institués par les décrets n° 61-1304 [le RACL] et n° 64-226 [le
RACD], le taux de la cotisation au régime institué par le présent décret est
égal à la moitié de celui prévu au I. » Les statuts `auteur_dramatique` et
`auteur_lyrique` sont exactement ces personnes, et ils portent déjà tout leur
revenu au RACD ou au RACL : ils cotisent désormais au RAAP à 4 %, par une fiche
à part dont les points restent ceux du RAAP. Pour une carrière entière depuis
2016, leur pension du RAAP est la moitié de celle d'un artiste-auteur au même
revenu — ce qu'elle était avant 2016 reste au taux de la fiche.

En chemin, un défaut du moteur : le rendement, qui fait partie du barème du
point, se lisait sous le code de la fiche et non sous celui du régime dont elle
emprunte le barème. Une fiche `points_de` sans valeur du point connue aurait vu
sa pension tomber à zéro sans rien dire ; aucune ne l'était encore.

**Et avant 2016, le RAAP n'était pas un taux mais une classe.** La fiche le
savait — un paragraphe entier y expliquait que la classe était un CHOIX, et
qu'aucun modèle ne devine le choix d'un assuré — et en concluait qu'il fallait
prélever 8 % du revenu, taux qu'aucun texte ne porte. Le même article 2 du
décret n° 62-420 qui crée les classes, en 1981, dit pourtant ce que devient
qui ne choisit pas : « à défaut d'option », il est « inscrit d'office en classe
spéciale », six points par an. C'est la classe que le dépôt sert désormais,
par la règle qu'il applique partout — ne jamais prêter un choix qu'on ne
connaît pas —, et c'est celle de « 80 % des adhérents », selon la caisse. Ses
montants sont au Journal officiel, un décret par exercice : 876 F en 1984,
1 500 F en 2000, 448 € en 2015. Le guide 2026 de l'IRCEC les recoupe sans le
vouloir : Spike, « fidèle de la classe C », a versé 2 694 € en 2016 pour 36
points, six fois les 449 € de la classe spéciale que fixe le décret de cette
année-là. À un revenu moyen, la fiche servait quatre à six fois les points de
la classe d'office ; les témoins des artistes-auteurs perdent de 7 à 27 % au
scénario 1, et leur compte notionnel ce qu'ils n'avaient pas versé.

Ce que la classe laisse approché : de 1981 à mai 2004, les assujettis du b de
l'article 1<sup>er</sup> — sans doute les musiciens et les compositeurs, la
rédaction d'alors n'étant pas dans l'index — étaient inscrits d'office en
classe A, douze points pour le double, et la fiche leur sert la classe
spéciale ; les montants de 1981 à 1983 et de 1989 sont reportés de la grille
voisine ; et avant le 29 mai 2004, le régime ne visait pas encore tous les
artistes-auteurs, quand le modèle y affilie écrivains et photographes dès
1977.

### Les artistes-auteurs n'ont pas d'employeur, et leur compte notionnel en portait un

Les pages de la Sécurité sociale des artistes auteurs, lues le 22 septembre
2026 (action 89), ne changent rien au scénario 1 : le droit du régime général
s'y applique tel quel — cent cinquante SMIC horaires par trimestre, vingt-cinq
meilleures années, les âges d'après la suspension —, et c'est ce que le modèle
fait. Elles changent le compte notionnel.

**Ce que l'auteur et son diffuseur versent.** L'historique des taux que publie
l'organisme, de 1977 à 2024, le dit année par année : l'auteur paie la
cotisation vieillesse du SALARIÉ, au taux du salarié — 6,55 % plafonnée
jusqu'en 2005, 6,65 %, puis 6,75, 6,80, 6,85 et 6,90 % depuis 2016, et la
déplafonnée de 0,10 à 0,40 % —, recoupée point par point avec la part
salariale de la fiche du régime général. Le diffuseur, lui, ne verse qu'une
« contribution diffuseur » de 1 % de la rémunération artistique, pour toutes
les branches, et 0,1 % de formation depuis 2012. Depuis 2019, l'État prend en
charge 0,75 point de la plafonnée et toute la déplafonnée.

**Ce que le compte porte.** Le statut `artiste_auteur` n'est pas marqué
`sans_employeur` — le diffuseur verse bien quelque chose —, et le compte lui
prête donc la part patronale d'un salarié : 8,55 % plafonnée et 2,11 %
déplafonnée en 2026. Sur le témoin de l'artiste-auteur, 199 962 € des
372 038 € portés au compte dans le scénario rétroactif « salariale +
patronale » sont cette part, qu'aucun diffuseur n'a versée : 54 %. Les
scénarios 4 et 5 des trois statuts d'auteur en sont surévalués d'autant ; les
scénarios 2 et 3, qui ne portent que la part de l'assuré, sont justes à
1,15 point près depuis 2019.

**Pourquoi ce n'est pas corrigé dans la même passe.** Le correctif est un
drapeau de statut — la part salariale portée au compte, aucune part patronale
— lu par le compte notionnel et par la fiche de paie, dans les deux moteurs.
Il demande un arbitrage que les pages ne tranchent pas : la contribution de
1 % finance toutes les branches, et rien ne dit quelle part en revient à la
vieillesse. Le compter pour zéro sous-évalue un peu ; le porter en entier
surévalue. C'est une action à part, que la feuille de route nomme.

**Corrigé le 23 septembre 2026.** Le drapeau est posé sur les trois statuts
d'auteur : `part_salariale_seule` dit que l'assuré paie la part salariale et
que personne ne paie l'autre — l'inverse de `sans_employeur`, où il paie les
deux. Le compte ne porte plus que cette part, sous toutes les conventions et
dans les deux moteurs ; les scénarios 4 et 5 des auteurs retombent sur les 2
et 3, comme ceux d'un artisan. Le 1 % du diffuseur y compte pour zéro :
l'article L. 382-4 lui fait assurer « le financement des charges incombant
aux employeurs au titre des assurances sociales et des prestations
familiales » sans dire ce qui revient à la vieillesse, et l'arrêté du 13 avril
1981 qui en fixe le taux ne le dit pas davantage. Le compte en est sous-évalué
d'un point de revenu au plus, si tout le 1 % allait à la vieillesse. Sur le
témoin de l'artiste-auteur, le compte du scénario 4 tombe de 372 038 à
172 076 €, et sa pension de 15 218 à 7 063 € par an ; la proposition, qui ne
lui prêtait la part patronale qu'avant la bascule, passe de 13 057 à 9 147 €,
que la garantie vieillesse complète désormais de 3 736 €. La fiche de paie
n'est plus servie aux auteurs : celle du salarié leur prêtait une assurance
chômage, l'Agirc-Arrco et un employeur payant une quarantaine de points.
Mieux vaut rien qu'un net faux ; un net saisi est lu comme un brut, et le site
le dit sous le formulaire.

### Les sections juridiques écrivaient leurs règles, et les fiches ne les lisaient pas

La passe du 23 septembre 2026 sur les professions juridiques (action 89) a
dépouillé les seize adresses de la CNBF, de la CAVOM et de la CPRN, puis lu au
Journal officiel les textes qu'elles appliquent : les statuts et les
règlements des deux sections, approuvés par arrêté — le dernier le 10 juillet
2026 —, le décret n° 2026-418 qui les a réécrits, et les articles du code de
la sécurité sociale propres aux avocats. Les trois fiches suivaient le régime
général là où les textes ne le suivent pas.

**Les âges n'étaient pas les bons.** La complémentaire de la CAVOM s'ouvre à
60 ans et se sert à taux plein à 65 pour les générations nées avant 1956,
puis monte de six mois par génération jusqu'à 62 et 67 ans ; celle de la
CPRN, de 2014 à 2023, ouvrait à l'âge légal « différé de vingt-quatre mois »
et servait le taux plein cinq ans plus tard — 64 et 69 ans pour les
générations nées depuis 1955. Les fiches lisaient les tables du régime
général. Une table par régime (`legislation/ages_regimes.csv`, champ
`age_table`) les porte maintenant, dans les deux moteurs.

**La durée effaçait des décotes que les textes ne lui laissent pas
effacer.** Les deux complémentaires ne connaissent que l'âge : 5 % par année
manquante « non susceptible de fractionnement » à la CAVOM, 1,25 % par
trimestre « séparant l'âge de l'affilié […] de l'âge du taux plein » à la
CPRN. Les fiches leur opposaient la décote du régime de base, qu'une carrière
complète annule : un officier ministériel ou un notaire parti à l'âge légal
avec sa durée ne perdait rien de sa complémentaire, là où les caisses lui en
retirent 15 %. Les témoins des deux statuts perdent de 6 à 9 % au scénario 1.
Le texte de la CAVOM ne dit pas si l'année entamée compte ; le modèle la
compte, comme l'IRCEC l'écrit pour la même règle.

**Trois autres règles manquaient.** La surcote des avocats passe de 0,75 % à
1,25 % par trimestre au 1er juillet 2010 (R. 653-3), et la fiche servait
0,75 % à tous. La loi du 14 avril 2023 étend la majoration de 10 % pour trois
enfants au régime de base des libéraux et des avocats, et les règlements de
la CPRN et de la complémentaire des avocats l'ont suivie en 2024 : aucune
fiche ne la portait. Le plafond de la CAVOM est monté de quatre à huit
plafonds de 2016 à 2020, avec une assiette minimale ; la fiche portait huit
plafonds dès 2016, et ses officiers ministériels partis avant 2016 ne
recevaient aucune complémentaire, faute de rendement.

**Ce qui reste, et où il est écrit.** La section B de la CPRN, quatre
dixièmes du complémentaire d'un notaire : le décret n° 2026-418 en donne
désormais la règle des bornes — un huitième des notaires en activité par
classe — et la caisse la grille des montants, k fois la classe 1 pour 10 k
points, avec ses valeurs de point dans ses rapports d'activité ; la fiche dit
comment l'estimer. La retraite forfaitaire des avocats, que les barèmes
donnent de 2017 à 2026 et que le modèle ramène de 2026 par les prix — 5 % de
moins pour une liquidation de 2017. Les classes de la CAVOM d'avant 2016,
dont les bornes ne sont dans aucun texte de l'index. La majoration de durée
d'assurance pour enfants et la surcote parentale des libéraux et des
avocats. Les lignes `cavom_ages_minoration`, `cavom_assiette_2016`,
`cprn_ages_decote_enfants`, `cnbf_surcote` et
`majoration_enfants_liberaux_avocats` du registre de veille en tiennent le
détail.

### Les sections de santé minorent à l'âge, et la durée effaçait la minoration

La passe du 23 septembre 2026 sur les professions de santé (action 89) a
dépouillé les vingt et une adresses de la CARMF, de la CARCDSF, de la CAVP, de
la CARPIMKO et de la CARPV — les calculettes de la CARMF lancées sur une
grille de revenus —, puis lu au Journal officiel les statuts et les
règlements des cinq sections, approuvés par arrêté, le dernier le 10 juillet
2026. Les barèmes de cotisation de 2026 étaient justes partout ; les règles
d'âge ne l'étaient nulle part.

**Une durée requise vide ne dit pas « l'âge seul ».** Plusieurs fiches
écrivaient une minoration par trimestre et laissaient
`duree_requise_trimestres` vide, pour dire que la durée n'y jouait aucun
rôle. Le moteur, lui, opposait à un régime en points la durée de la
carrière, qui annulait la minoration : un médecin parti à 64 ans en 2009
avec sa durée, un vétérinaire au même âge, ne perdaient rien de leur
complémentaire. Les statuts disent le contraire — « 0,75 à 60 ans […] 0,95 à
64 ans » à la CARMF jusqu'en 2016, « 1,25 % par trimestre manquant avant
l'âge de soixante-cinq ans » à la CARPV. La règle s'écrit maintenant en
clair, `abattement_points: cavom` ou `decote_annulee_par_la_duree: false`.
La CAVAMAC, la CAVEC et la CPRN d'avant 2014 portent la même forme, et
restent à relire contre leurs statuts.

**Chaque section a sa règle d'âge, et les fiches lisaient celle du régime de
base.** La CARCDSF minore de 5 % par année d'âge manquante sous ses statuts
de 2007, puis, à partir de 2011, par génération — 5 % par année pour les nés
avant juillet 1951, 1,5 % par trimestre pour les nés depuis 1955, un tableau
entre les deux —, dans la limite de 15 % depuis 2024 ; elle majore de 1 %
puis de 1,25 % par trimestre au-delà. La CAVP a ses propres âges du taux
plein, de 65 à 67 ans selon la
génération, et deux pentes : 1,25 % par trimestre jusqu'à 65 ans, 0,5 %
au-delà. La CARPIMKO fait monter le sien de quatre mois par génération, de
65 ans pour les nés en 1955 à 67 ans pour ceux de 1961. Une colonne de
décote s'ajoute à `legislation/ages_regimes.csv`, quatre champs aux
périodes — un palier de décote et sa seconde pente, le taux plein anticipé
des mères et sa limite —, dans les deux moteurs. Et les âges d'ouverture et
du taux plein d'une carrière ne lisent plus les âges propres d'un
complémentaire : la CAVOM ouvrait à 60 ans la carrière d'un officier
ministériel né en 1955, que le calcul refusait ensuite.

**Les mères de la CARCDSF partent plus tôt, et trois enfants majorent
partout.** Une chirurgienne-dentiste ou une sage-femme part sans
minoration un an plus tôt par enfant, cinq au plus : la caisse en publie
l'exemple, deux enfants et le taux plein dès 65 ans, devenu le témoin
`carcdsf_deux_enfants_65_ans`. La majoration de 10 % pour trois enfants
n'était portée par aucune des cinq fiches ; elle l'est à la date où un
texte l'établit — 1964 à la CARMF, 1981 à l'ASV des médecins, 2008 à la
CARCDSF, 2009 à la CAVP, 2022 à la CARPV, 2024 à la CARPIMKO. Au scénario 1,
les témoins — des hommes sans enfant partis à 64 ans avec leur durée —
perdent ce que la caisse leur retire : de 2 à 7 % pour les dentistes, de 3
à 4,5 % pour les pharmaciens, de 2,6 à 3,3 % pour les vétérinaires, 1,4 %
pour le médecin né en 1945.

**Ce qui reste, et où il est écrit.** Le tableau de minoration des dentistes
nés de juillet 1951 à 1954 n'est publié qu'en image (arrêté du 9 juillet
2012), et 1,25 % par trimestre en tient lieu ; leurs aînés, minorés par
année, le sont par trimestre de 2011 à 2016 ; et avant 2008, faute des
statuts publiés au Bulletin officiel, la fiche garde la règle du régime de
base. Les coefficients des pharmaciens nés jusqu'en 1955, « en annexe » des
statuts de 2011, ne sont pas dans l'index, et leur valeur de service n'est
pas affectée du coefficient de 0,96. L'abattement des auxiliaires
médicaux nés avant 1956, de 2016 à 2023 — 4 % par année et 0,25 % par
trimestre —, est remplacé par 1,25 % par trimestre. La règle d'âge de la CARPV n'est lue que depuis 2021 et
supposée la même avant ; le taux de 1964 de la CARMF n'est connu que par le
règlement de 2026. Lus et non portés : les dispenses des premières années,
que l'exemple de la CARMF suppose sans points (une année pour la base, deux
pour la complémentaire) ; la participation de l'assurance maladie à la
cotisation de base des médecins de secteur 1 ; les prestations
complémentaires de vieillesse des dentistes, des sages-femmes, des
auxiliaires médicaux et des biologistes ; la part capitalisée de la CAVP.
Les lignes `carmf_asv_minoration_enfants`, `carcdsf_minoration_age_seul`,
`cavp_minoration_deux_pentes`, `carpimko_ages_2015` et
`carpv_minoration_age_seul` du registre de veille en tiennent le détail.

### Les avocats cotisaient au taux de 2026 depuis 2019

Le complémentaire des avocats est un régime en points à cinq tranches de
revenu, fixées en euros. La fiche portait une seule grille, celle de 2026,
appliquée à tous les revenus depuis 2019 ; avant, un taux moyen de 8 %. Les
barèmes annuels de la caisse, que `scripts/fetch/cnbf_baremes.py` lisait déjà
pour la valeur du point et jamais pour les taux, disent autre chose : le taux
de la première tranche, en classe C1, est passé de 3,20 % en 2016 à 3,80 % en
2019, 5,00 % en 2024 et 7,00 % en 2026. Chaque année de 2016 à 2026 a
maintenant sa grille. Le barème 2024 n'est plus sur le site de la caisse :
il a été lu dans Internet Archive, qui l'a capturé le 15 juillet 2024 à son
adresse d'origine, et ses deux valeurs du point sont certifiées comme les
autres.

Le régime de base a changé de la même façon. Sa pension forfaitaire, la
cotisation forfaitaire et le taux proportionnel étaient ceux de 2026 ramenés
par les prix sur toute la période ; ils sont lus année par année depuis 2016,
et ancrés sur 2016 avant. Le forfait de 2020 est celui du barème révisé,
réduit d'un quart au titre de la crise sanitaire. Les témoins donnent la
mesure : l'avocat né en 1945 voit sa pension de base monter de 15 826 € à
16 830 €, parce que le forfait réel de 2016 dépasse de 6 % celui que les prix
reconstituaient ; celui né en 1965 voit son complémentaire baisser de
11 716 € à 10 472 €, parce que la fiche ne lui prête plus le taux de 2026 sur
ses années 2016 à 2024.

**Ce qui reste hors de la fiche.** La classe est toujours C1, la seule
qu'aucun avocat n'a à choisir. Les cinq premières années de la cotisation
forfaitaire, plus basses, ne sont pas distinguées. Avant 2016, aucun barème
n'est publié : le complémentaire reste au taux moyen de 8 %, qui est celui
d'un revenu élevé et surestime un revenu modeste, et la base porte les
valeurs de 2016 ramenées par les prix. Les barèmes d'une année s'appliquent
aux revenus de la même année, comme partout dans le catalogue, alors que la
caisse appelait avant 2025 ses cotisations sur un revenu antérieur.

### Les dernières sections libérales : l'âge seul, trois enfants, et les trimestres des mères

La passe du 23 septembre 2026 sur les sections libérales restantes (action 89)
a dépouillé les vingt-trois adresses de la CNAVPL, de la Cipav, de la CAVAMAC
et de la CAVEC — le guide 2026 de la caisse nationale en trois parties, les
fiches pratiques et les documents des caisses, la calculette de la CAVEC et le
modèle publicodes de mon-entreprise, interrogé hors navigateur —, puis lu au
Journal officiel les statuts de la CAVAMAC de 2011 et leur réécriture de 2023,
ceux de la CAVEC depuis 2008, et les articles 8, 13, 20 et 21 du décret
n° 2026-418.

**La même forme que chez les dentistes, et la durée l'effaçait encore.** La
CAVAMAC et la CAVEC écrivent une minoration que la durée d'assurance
n'annule pas, et les deux fiches la laissaient annuler. La CAVAMAC : taux
plein à l'âge légal augmenté de cinq ans, 5 % par tranche de douze mois
d'anticipation, jusqu'en 2023 (statuts approuvés le 23 juin 2011, articles
15 et 16) ; 1,25 % par trimestre manquant jusqu'à 67 ans depuis le
1er janvier 2024 (arrêté du 4 août 2023). La CAVEC : « à 65 ans à taux plein ;
entre 60 et 65 ans, avec application d'un abattement définitif de 1,25 % par
trimestre manquant », de 2008 au règlement de 2026, et 65 ans depuis 1983 au
moins, dit son livre des soixante-dix ans. Un agent général ou un
expert-comptable parti à l'âge légal avec sa durée ne perdait rien de sa
complémentaire ; il perd ce que ses statuts lui retirent — de 5 à 15 % pour
les témoins, partis à 64 ans. La note de la fiche de la CAVEC disait la règle
depuis la passe des professions juridiques ; c'est le drapeau qui manquait.
La surcote de la CAVAMAC, 5 % par année pleine au-delà du taux plein, ne
compte depuis 2024 que les années COTISÉES : deux années d'attente après
67 ans ne valent plus rien, et le moteur sait maintenant le dire. La caisse
publie trois exemples chiffrés de ses deux régimes ; ils entrent aux témoins
officiels, et le troisième — une décote de 6,25 % pour cinq trimestres,
durée réunie — est celui que la fiche ne rendait pas.

**Trois enfants, et trois dates.** La complémentaire de la CAVAMAC majore de
10 % les points de qui a eu trois enfants depuis ses statuts de 2011 ; celle
de la Cipav, depuis 2000 au moins — le décret n° 99-913 y promet aux
géomètres « une bonification pour enfants dans les conditions prévues » par
ses statuts, dont la forme n'est lue qu'aujourd'hui ; celle de la CAVEC,
depuis l'arrêté du 4 juillet 2025, que le guide de mars 2026 de la caisse
nationale ignore encore. Aucune des trois fiches ne la portait.

**Les trimestres des mères, et un moteur qui ne les cherchait pas là.**
L. 643-1-1 rend aux libérales la majoration de durée d'assurance de L. 351-4
pour les pensions prenant effet depuis le 1er avril 2010, et la surcote
parentale depuis septembre 2023. La fiche de la CNAVPL les disait « non
portées », et le moteur ne les aurait pas servies : il ne cherchait la
majoration que dans les régimes en annuités. Une majoration de durée ne joue
pourtant que sur la durée d'assurance, qu'un régime en points oppose aussi ;
`mda` est désormais lu dans toute fiche qui le porte — et seulement `mda`,
les bonifications, qui entrent aux services, restant aux annuités. Une
libérale née en 1964, mère de deux enfants, entrée à 24 ans et partie à l'âge
légal, ne perd plus que ce que la loi lui retire : ses seize trimestres
portent sa durée à 171, et sa décote de 18,75 % tombe à zéro, à la CNAVPL
comme à la Cipav qui la suit.

**Une valeur de service que la caisse publiait, et que le dépôt déduisait.**
La CNAVPL imprime dans sa page « Cotiser pour sa retraite » la valeur de son
point depuis 2004, chaque valeur avec sa date d'effet ; le dépôt ne la lisait
que dans les recueils statistiques, depuis 2021, et ramenait la valeur de
2021 vers le passé par les prix. Les pensions de base liquidées de 1989 à 2019
en sortaient trop basses de 1,4 à 5 %. `scripts/fetch/cnavpl_valeur_service.py`
lit la série, retient la valeur en vigueur au 31 décembre — 0,6027 € en 2022,
année de deux revalorisations, là où le dépôt portait celle du 1er janvier —,
et ne l'écrit qu'après l'avoir confrontée à D. 643-1 pour 2004 et 2005 et aux
cinq recueils : la série est certifiée de 2004 à 2026. Elle stagne en 2014,
en 2016 et en 2018, les trois années où le régime général n'a pas revalorisé
non plus.

**Deux défauts dans la carrière elle-même.** Un revenu qui tombe pile sur le
seuil d'un trimestre ne le validait pas toujours : 450 SMIC horaires font
trois seuils de 150, mais la division en virgule flottante rendait 2,999… en
2025, et deux trimestres au lieu des trois que la CNAVPL et la CAVAMAC
écrivent pour la cotisation minimale ; corrigé dans les deux moteurs. Et
l'âge du taux plein des générations d'avant 1930, que la table du 1° de
L. 351-8 ne porte pas, retombait sur les 67 ans de la fiche de la CAVAMAC :
la fiche dit 65.

**Ce qui reste, et où il est écrit.** Avant 2011 pour la CAVAMAC, avant 2008
pour la CAVEC, les statuts ne sont publiés qu'au Bulletin officiel : leur
règle d'âge est supposée la même, et le taux d'abattement de la CAVEC d'avant
2008 n'est pas connu. Lus et non portés : le capital unique que la CAVAMAC
verse sous 1 500 points (dix-huit fois la pension annuelle) et la CAVEC sous
500 (quinze fois), la pension restant servie en rente ; la majoration de 5 %
de la CAVAMAC par enfant ouvrant droit à l'allocation d'éducation de l'enfant
handicapé ; son départ anticipé des carrières longues, à 62 ou 63 ans avec
15 % de minoration, là où le modèle oppose la minoration ordinaire ; les cent
points que la CNAVPL attribue au trimestre d'un accouchement (D. 643-1), que
le modèle ne sait pas dater, faute de la date de naissance des enfants ;
l'option pour la classe supérieure à la CAVEC et les rachats partout. La
Cipav ne majore un départ différé que pour qui compte trente années
d'affiliation, et sur les seuls points de ces trente années ; le modèle les
majore tous. Les lignes `cavamac_minoration_age_seul`,
`cavec_minoration_age_seul`, `sections_liberales_majoration_enfants`,
`cnavpl_majoration_duree_assurance`, `cnavpl_valeur_service` et
`decret_2026_418_liberaux` du registre de veille en tiennent le détail.

**Ce que les caisses publient de travers.** Le dépôt n'a pas été le seul à
se tromper. La fiche pratique 2026 de la Cipav applique à son régime de base
8,23 % et un point pour 89,71 € de revenu — le taux et le barème d'avant 2025,
posés sur le plafond de 2025 —, quand D. 642-3 écrit 8,73 % depuis le
1er janvier 2025, et à sa complémentaire 9 et 22 % jusqu'à trois plafonds,
quand le décret dit 11 et 21 % jusqu'à quatre ; son exemple de 40 000 € rend
450,1 et 75,9 points là où le droit en ouvre 467,8 et 92,8. Sa page des âges
donne 171 trimestres à la génération 1964, que la suspension a ramenée à 170.
La calculette de la CAVEC ne connaît que huit classes quand la grille de 2026
en compte neuf, et facture 25 627 € au-delà de 181 208 € de revenu au lieu de
30 616 € ; elle oublie l'option pour la classe supérieure dans l'une d'elles,
et calcule le conjoint collaborateur aux taux de 2004 à 2011. Le tableau de
paramètres de la CAVAMAC fait régulariser 2025 à 8,23 % quand D. 642-3 écrit
8,73 % pour les périodes courant depuis le 1er janvier 2025. Et le paquet
`modele-social` que l'Urssaf publie sur npm, dans sa version du 16 juillet
2026, porte encore 8,23 % et 525 points ; le site mon-entreprise, lui, charge
un second modèle, `modele-ti`, qui a suivi la réforme, et dont les points
tombent sur ceux du dépôt au dixième près sur une grille de quatorze revenus,
de 2024 à 2026.

### Le RAFP prenait toutes les primes, et le décret s'arrête à 20 % du traitement

La fiche du RAFP l'écrivait depuis sa création — « 5 % agent + 5 % employeur
sur les primes, dans la limite de 20 % du traitement indiciaire » —, et aucun
des deux moteurs ne le lisait : l'assiette était le revenu multiplié par la
part des primes, sans borne. L'article 2 du décret n° 2004-569 porte pourtant
la limite dans ses six versions, de la première (LEGIARTI000006453300) à celle
en vigueur depuis le 17 avril 2024 (LEGIARTI000049424057) : les primes
cotisent « dans la limite de 20 % du traitement indiciaire brut total ou de la
solde brute totale perçus au cours de l'année considérée ». L'ERAFP le redit
en tête de sa page sur les cotisations, lue le 23 septembre 2026, et précise
que le plafond s'apprécie sur l'année, en cumul depuis janvier — la
granularité même de la carrière du modèle.

**Ce que cela déplaçait.** Des primes qui font 22 % de la rémunération valent
28 % du traitement : l'agent n'en cotise que 20, soit 15,6 % de sa
rémunération, et le moteur lui faisait cotiser les 22 — une retraite
additionnelle trop haute de 41 %. Les trois cas types publics, à 18, 22 et
25 % de primes, cotisaient sur une assiette trop forte de 10, 41 et 67 %. Un
champ de période, `plafond_primes_traitement`, porte la limite, et
`PeriodeRegime.part_du_revenu`, en Python comme en JavaScript, fait désormais
le découpage — traitement seul, primes seules — que le scénario 1 et le compte
notionnel recopiaient chacun de leur côté. Deux témoins bougent sur 505, les
deux carrières de fonctionnaire à 22 % de primes : leur RAFP baisse de 29 %,
au scénario 1 comme dans les compartiments de capitalisation des comptes
notionnels. Le RAFP étant servi à l'identique partout, aucun écart entre
scénarios ne bouge.

**Ce qui reste.** Les deux exceptions que l'ERAFP nomme : la garantie
individuelle du pouvoir d'achat, cotisée sans plafond, et les jours de compte
épargne-temps convertis en points. La cotisation volontaire des agents de
l'État en poste dans quatre collectivités d'outre-mer, ouverte le 1er avril
2024. Et le taux unique des comptes notionnels, qui porte sur toute la
rémunération quand la capitalisation n'est pas isolée : le plafond, règle du
RAFP, n'y a pas cours. La ligne `rafp_assiette_plafond` du registre de veille
en tient le détail.

### La RCO ne servait que les points cotisés, et le code rural en donne cent par année de chef d'avant 2003

La complémentaire des non-salariés agricoles est née le 1er janvier 2003. Le
chef d'exploitation qui liquide depuis n'y a cotisé qu'une partie de sa
carrière, et le droit lui reconstitue le reste : « 100 points de retraite
complémentaire pour chacune des années de chef d'exploitation ou d'entreprise
agricole à titre exclusif ou principal accomplies avant le 1er janvier 2003 »,
retenues « dans la limite de la différence entre trente-sept années et demie
et le nombre d'années ayant donné lieu à affiliation » à la RCO (D. 732-154 du
code rural, dans ses trois versions depuis 2005). Deux conditions : dix-sept
ans et demi d'assurance comme chef à la date d'effet (D. 732-151), et le taux
plein de la retraite de base — en réunir la durée requise jusqu'au 31 août
2023, l'avoir liquidée au taux plein, par la durée ou par l'âge, depuis
(L. 732-56, II, 2°, modifié par l'article 18 de la loi du 14 avril 2023). La
fiche le taisait, et aucun des deux moteurs ne servait ces points. La page de
la MSA, lue le 23 septembre 2026, écrit la règle des cent points à l'identique ;
elle décrit encore la condition de durée d'avant 2023, et c'est le code rural
qui fait foi.

**Ce que cela déplaçait.** Pour qui s'est installé jeune et a liquidé tôt, les
points gratuits font plus de la moitié de la complémentaire : un chef né en
1955, installé en 1975 et parti en 2019 à la moitié du salaire moyen, reçoit
2 150 points gratuits pour 1 708 points cotisés — 729 € par an sur une RCO de
1 309 €. Quatre témoins bougent sur 509, les quatre chefs d'exploitation du
simulateur, au salaire moyen : leur pension du scénario 1 monte de 7,5 % pour
la génération 1945, 4,3 % pour 1955, 2,1 % pour 1965, et de 0,25 % pour 1975,
qui n'a que sept années d'avant 2003. Les comptes notionnels rétroactifs ne
servent que ce qui a été cotisé, et l'écart qui les sépare du scénario 1 se
creuse d'autant ; le prospectif garde leur pension aux générations déjà
parties et ne compte pas ces points dans les droits acquis des autres. La page
Avantages chiffre la ligne à 0,64 Md € en 2024. Un champ de période,
`points_gratuits`, porte la règle, que `_points_gratuits` lit en Python comme
en JavaScript ; la cascade l'isole sous la ligne `points_gratuits_rco`, mesurée
comme l'AVPF, par un second calcul de la même carrière sans eux.

**Ce qui reste.** Les points gratuits du V et du VI de L. 732-56 — 66 par an,
dix-sept annuités au plus — pour les années de conjoint, d'aide familial ou de
collaborateur d'avant 2011, et pour celles du chef qui n'a pas dix-sept ans et
demi comme chef : il lui faut alors dix-sept ans et demi d'activité non
salariée agricole à quelque titre que ce soit, que le modèle, qui ne connaît
que le statut de chef, ne peut réunir sans que la règle des cent points
s'applique d'abord. Les majorations de durée d'assurance que D. 732-151 compte
dans les dix-sept ans et demi depuis 2026, quand la fiche du régime de base
n'en déclare aucune. La révision des pensions prises avant le 1er septembre
2023, que la loi fait aussi bénéficier de la nouvelle condition pour leurs
arrérages suivants. La ligne `rco_points_gratuits` du registre de veille en
tient le détail.

### Le ministre du culte n'avait pas d'Arrco, et L. 921-1 la lui donne depuis 2006

Le statut du simulateur confondait deux populations que la loi sépare.
L'article 75 de la loi de financement de la sécurité sociale pour 2006 a
complété L. 921-1 : l'affiliation obligatoire à une institution de retraite
complémentaire est « applicable aux personnes mentionnées à l'article L. 382-15
qui bénéficient d'un revenu d'activité perçu individuellement ». Le ministre
rémunéré par son diocèse, son association ou sa communauté cotise donc à
l'Arrco depuis le 1er janvier 2006, puis à l'Agirc-Arrco ; le religieux qui vit
de sa congrégation, non. Le modèle ne routait l'Arrco ni à l'un ni à l'autre.

La cotisation ne porte pas sur le revenu. Les circulaires de la CAVIMAC, qui
la recouvre, en donnent l'assiette et le taux : la n° 2026/03 du 27 mai 2026
porte au SMIC mensuel, 1 867 €, « les assiettes forfaitaires respectives des
cotisations [...] vieillesse et retraite complémentaire obligatoire des
cultes », et cote la ligne « RCO — Tous cultes - taux de base » à 10,02 %,
dont 6,01 % pour la collectivité et 4,01 % pour l'assuré — les 7,87 % de
l'Agirc-Arrco et ses 2,15 % de contribution d'équilibre générale. Les
circulaires lisibles, depuis novembre 2021, disent toutes la même chose.

**Ce que cela déplace.** Le statut est scindé : `ministre_du_culte` garde son
code et reçoit l'Arrco depuis 2006, `membre_congregation` n'a que la CAVIMAC.
Une fiche `arrco_cultes` porte les points de l'Arrco puis de l'Agirc-Arrco sur
le forfait, comme la tranche 2 de l'Arrco emprunte les siens. Le ministre du
simulateur né en 1975 gagne 14 % de pension au scénario 1, celui né en 1955
6,2 %. Six témoins s'ajoutent, ceux du nouveau statut ; quatre changent de
pension, les ministres des générations 1945 à 1975, et la liste des régimes
que fusionne le système unique gagne une ligne dans tous.

**Ce qui reste.** Les huit taux spécifiques que la CAVIMAC énumère, de 11,13 à
21,31 % ; le taux d'avant 2019, repris de l'Arrco faute de circulaire plus
ancienne lisible ; le texte de l'avenant n° 25 à l'accord Agirc-Arrco, qui
touche en 2024 à son annexe B pour les affiliés de la CAVIMAC. Le lecteur de
relevé rattache toute ligne de la CAVIMAC au ministre rémunéré : c'est au
formulaire de corriger. La ligne `cultes_retraite_complementaire` du registre
de veille en tient le détail.

### Le ministre du culte liquidait sur son revenu, et la caisse liquide sur le SMIC

Le régime des cultes cotise sur un forfait, le SMIC mensuel (R. 382-89 et
R. 382-90), et liquide aux règles du régime général (L. 382-27) : son salaire
annuel moyen est fait des salaires qui ont porté cotisation, c'est-à-dire du
forfait. La page de la CAVIMAC sur la retraite de base, lue le 23 septembre
2026, l'écrit sans détour : « le salaire annuel est égal à la moyenne des
salaires des 25 meilleures années. Ces salaires correspondent à une base SMIC
pour tous les assurés cultuels. » Le moteur, lui, prélevait bien la cotisation
sur le forfait, mais calculait la pension sur le revenu saisi.

**Ce que cela déplaçait.** Tout, sauf pour qui déclarait un revenu voisin du
SMIC. Le ministre né en 1965, parti à 65 ans, se voyait servir une pension de
base de 20 771 € par an s'il avait déclaré une fois et demie le salaire moyen,
de 9 988 € à la moitié ; elle est désormais de 9 554 € dans les deux cas, sur
un salaire annuel moyen de 22 557 €. Le forfait qu'on retient est celui de
l'année — 169 heures mensuelles avant 2002, 151,67 ensuite —, lu dans la fiche
de l'année et non dans celle de la liquidation. Les comptes notionnels ne
bougent pas : ils ne lisaient déjà que la cotisation.

**Ce qui reste.** La même page décrit une pension en trois fractions : les
années d'avant 1979, validées gratuitement, que le modèle ne compte pas ; celles
de 1979 à 1997, cotisées au forfait mais liquidées à leurs règles propres,
portées au minimum contributif ou au maximum de la pension « Cavimac » ; celles
d'après 1998 seules suivent le régime général. La ligne
`cultes_salaire_annuel_moyen` du registre de veille en tient le détail.

### Les navigants décotaient jusqu'à soixante-cinq ans, et la loi dit soixante

La caisse des navigants de l'aviation civile (CRPN) écarte la décote « à
compter d'un âge au moins égal à celui mentionné au premier alinéa de
l'article L. 6521-4 du code des transports » (R. 426-12, puis R. 6527-23). La
fiche en avait fait soixante-cinq ans, la limite d'âge de vol. L. 6521-4, lu
sur Légifrance, dit autre chose : l'activité de pilote « ne peut être exercée
dans le transport aérien public au-delà de l'âge de soixante ans ».
Soixante-cinq ans n'est que la borne des prolongations annuelles, au
troisième alinéa. Les notices de la caisse le confirment : « droit à pension
différé à 60 ans » de 2012 à 2021, « pension à 60 ans sans décote » depuis
2023. Toutes les périodes depuis 2012 portent maintenant soixante ans.

**Depuis 2022, la durée seule.** « Une décote égale à 5 % par annuité
manquante » sous trente annuités (R. 6527-22), sans condition d'âge. Le moteur
prenait partout le plus petit des deux manques, âge et durée, et décotait donc
trop peu un navigant proche de soixante ans à la carrière courte : 15 % au lieu
de 25 % à cinquante-sept ans avec vingt-cinq annuités. Un champ nouveau,
`decote_par_la_duree_seule`, compte la durée seule dans les deux moteurs.

**Le taux d'appel de 2026 est de 111 %**, soit 23,64 % au lieu des 22,37 % que
la fiche portait depuis 2016. Les taux des années 2016 à 2025 ne sont pas
publiés là où une session les trouve : ces années gardent 105 %.

**Ce qui reste approché.** Le dispositif transitoire des navigants nés avant
1971 — taux plein à cinquante-cinq ans avec 21 annuités pour la génération
1962, une de plus par génération jusqu'à 29 pour 1970 — n'est pas porté. Les
conditions de 2012 à 2021, qui montaient chaque année (âge de 50 à 55 ans,
« couple » âge plus annuités de 76 à 80), non plus. La caisse compte les
annuités au jour près ; le modèle, au trimestre.

### La fonction publique de l'État : le minimum de l'invalidité servi à tous, et la surcote des classés attendue trop tard

Le lot de la fonction publique de l'État (action 89, 24 septembre 2026) :
treize pages du Service des retraites de l'État, deux fiches de
service-public.gouv.fr, la FAQ de la DGAFP sur la retraite progressive et
trois calculettes, puis les textes qu'elles appliquent, lus dans les index
LEGI et JORF. Les pages confirment l'essentiel de la fiche — durées par
génération avec la suspension, décote, surcote, carrière longue, retenue de
2015 à 2026, barème du minimum garanti au centime — et deux exemples y
entrent aux témoins officiels. Trois règles ne l'étaient pas.

**Sous quinze ans, le minimum garanti de l'invalidité.** L'article L. 17 a
deux règles pour une pension de moins de quinze ans de services : le c, un
quinzième de 57,5 % de la référence par année, et le d, la référence
rapportée, par année de services, à la durée qui ouvre le pourcentage
maximum. La loi du 9 novembre 2010 (article 53, V) a réservé le c à la
pension liquidée pour invalidité, et le d sert toutes les autres. Le modèle
servait le c à tous, et le minimum d'une pension de treize ans valait
680,90 € par mois en 2026 au lieu de 417,94 € — l'exemple de la fiche F21142,
et la colonne « cas général » de la table du SRE, qui divise par 170. C'est
63 % de trop, pour les fonctionnaires entrés tard ou sortis tôt, que leurs
autres régimes portent au taux plein. Le c reste servi à qui avait atteint
l'âge d'ouverture de ses droits avant 2011, comme le V de l'article 45 de la
même loi le lui conserve ; la Banque de France, qui a son propre d depuis
son décret de 2012, garde le c faute d'une fiche qui le date.

**L'âge qui ouvre le minimum sans la durée était trop tardif.** Le IV de
l'article 45 de la loi de 2010 minore l'âge d'annulation de la décote, pour
l'ouverture du minimum garanti, d'un nombre de trimestres que l'article 3 du
décret n° 2010-1744 fixe selon l'année où l'âge d'ouverture est atteint :
neuf en 2011, sept, cinq, trois, un en 2015. Le modèle attendait l'âge
d'annulation entier, et refusait le minimum à un sédentaire né en août 1951
parti à soixante-trois ans avec une décote.

**L'emploi classé surcote à l'âge anticipé majoré de cinq ans.** Le D du
XXIV de l'article 10 de la loi du 14 avril 2023 déroge au III de L. 14 :
l'actif né à compter du 1er septembre 1966 surcote à son âge anticipé majoré
de cinq années, le super-actif né à compter du 1er septembre 1971 à son âge
minoré majoré de dix, et les générations d'avant à soixante-deux ans. Le
décret n° 2026-344 l'écrit pour la CNRACL en toutes lettres : soixante-deux
ans et neuf mois pour les actifs nés de 1968 à mars 1970, soixante-quatre ans
à partir de 1974. Le modèle opposait l'âge légal de LEUR génération, en
croyant — une docstring le disait — que l'âge anticipé majoré de cinq ans y
revenait : il revient à celui de la génération née cinq ans plus tôt. Un
fonctionnaire de catégorie active né en 1969 attendait soixante-quatre ans
une surcote que la loi lui ouvre à soixante-deux ans et neuf mois. Quatre
témoins bougent, les super-actifs d'État et hospitaliers nés en 1965 et en
1975 partis à soixante-quatre ans : +2,4 et +2,5 %. Le SRE, lui, écrit
« + 5 ans » et « + 10 ans » sans dire qu'avant les marches de 2023 c'est
soixante-deux ans.

**Ce que les pages du SRE écrivent de travers.** L'exemple de la formule de
calcul oppose 168 trimestres à un fonctionnaire né en 1958, quand la table
de la même page et L. 161-17-3 en donnent 167 : dix euros de pension par
mois. L'exemple du minimum garanti multiplie par douze ANNÉES un montant
calculé par trimestre et divise par 168 quand la table divise par 170. Celui
des militaires ouvre un droit en 2020 avec dix-sept ans de services puis en
compte dix-huit et deux mois en 2024, et lui oppose 172 trimestres. La page
de la retraite anticipée compte en réputés cotisés, pour la carrière longue,
toutes les bonifications et majorations pour enfants, quand D. 16-2, I, 4°,
dans la version du décret n° 2026-700, dit « dans la limite de deux
trimestres » : le modèle suit le décret. Et la surcote de Brigitte S. n'est
de six trimestres que si la pension prend effet le premier du mois qui suit
la cessation — la règle de la fonction publique depuis 2011 —, ce que
l'exemple de sa décote dit en passant (« 62 ans 6 mois 11 jours ») : datée
au mois de la cessation, le décompte au trimestre civil n'en donnerait que
cinq.

**Ce que les calculettes appliquent de travers.** La calculette du rachat
d'études de l'ENSAP, anonyme, calcule dans le navigateur, et son barème est
dans son script : c'est celui du décret n° 2003-1310, abrogé au 1er janvier
2026 par le décret n° 2025-1340, qui l'a remplacé par D. 7-1 du code des
pensions — plus bas, et étendu jusqu'à soixante-six ans. En septembre 2026,
elle facture un trimestre racheté pour la liquidation et la durée 9,5 % du
traitement annuel à vingt ans au lieu de 8,83 %, 20,6 % à quarante ans au
lieu de 19,80 %, et décrit l'abattement d'avant, dix ans après les études, au
lieu de l'année des quarante ans. La page « Comment améliorer ma retraite »
du SRE retarde de même. La calculette de surcotisation de l'académie
d'Aix-Marseille applique la bonne formule — la retenue sur la quotité
travaillée, plus 80 % de la retenue et du taux employeur de la CNRACL sur la
quotité non travaillée (décret n° 2004-678) — avec le taux employeur de
2025, 34,65 %, quand les taux que le SRE publie pour 2026 supposent 37,65 % :
16,20 % au lieu de 16,68 % à 80 %. Aucune des deux ne touche le scénario 1,
qui ne rachète ni ne surcotise.

**Ce qui reste.** Le temps partiel (voir « Ce qui reste hors du modèle »),
le plafond du dernier traitement de la majoration pour enfants (L. 18, V),
qui ne mord qu'à sept enfants, l'écrêtement du minimum garanti par le total
des pensions, dont le décret n'a pas été trouvé, la décote « carrière
longue » des militaires, et la confrontation du barème du rachat à la
neutralité actuarielle du compte notionnel — la même grandeur, calculée par
deux mains. Le registre de veille en porte les lignes
(`minimum_garanti`, `surcote_fonction_publique`,
`temps_partiel_fonction_publique`, `majoration_enfants_plafond_fonction_publique`,
`rachats_et_versements`).

### La pension du mineur : le coefficient de majoration manquait, et la valeur du trimestre suivait les prix

Le lot de la Caisse des dépôts (action 89, 24 septembre 2026) a lu la page
« Droits directs » de la retraite des mines, les tableaux « Barèmes et
revalorisations » que la caisse publie depuis 2024 et la fiche du régime que
le COR a jointe à son rapport de juin 2024, puis le décret n° 46-2769 dans
l'index LEGI — articles 125, 127, 131, 131-1, 131-2, 136, 139 et 181 —, le
décret n° 2002-800 et les arrêtés annuels du coefficient. La correction de
2026, qui avait fait de la pension minière un forfait par trimestre, était
juste dans son principe ; il lui manquait un facteur sur trois, et la fiche
indexait le deuxième de travers.

**Le coefficient de majoration de la durée.** L'article 131-1, créé par le
décret n° 2002-800 du 3 mai 2002 au terme d'un protocole de rattrapage,
affecte la durée de services « d'un coefficient de majoration déterminé en
fonction de la date de prise d'effet de la pension » : un arrêté le fixe
depuis 2003 — 1,194 cette année-là, 1,319 en 2013, 1,446 de 2022 à 2024,
1,473 en 2026. Le modèle ne le connaissait pas. Trente ans de mine liquidés
en 2024 valent 120 × 1,446 × 94,21 € = 16 347 € par an, le produit des deux
paramètres que publie le COR, qui l'arrondit à 16 300 € ; l'exemple est
désormais rejoué parmi les témoins officiels, et le modèle en servait
11 974.

**La valeur du trimestre suit les pensions, non les prix.** L'article 181
revalorise les pensions minières comme celles du régime général, et la valeur
du trimestre avec elles. La fiche la portait par l'indice des prix depuis ses
ancres de 1992, 2002 et 2013, et lui donnait 102,49 € en 2026 quand la caisse
en publie 97,15. La table `legislation/bareme_trimestre_mines.csv` la porte
maintenant date par date : la chaîne des coefficients de revalorisation de la
Cnav, partie des 382,08 F de 1992, retombe au centime sur les sept valeurs que
les textes et la caisse publient de 2001 à 2026 — à condition de n'arrondir
qu'à la fin. Arrondie à chaque marche, elle donne 89,46 € en 2023, et la
caisse en publie 89,47. Avec le coefficient et la bonne valeur, trente ans
liquidés en 2026 valent 17 172 € par an, pour 12 299 servis jusqu'ici.

**Cent vingt trimestres au plus, sauf ceux d'avant cinquante-cinq ans.**
L'article 136 plafonne la durée liquidée à cent vingt trimestres, et ne
compte au-delà que ceux accomplis avant cinquante-cinq ans. Le modèle les
comptait tous : un mineur entré à vingt et un ans et parti à soixante-quatre
recevait quarante-trois années, et la caisse en liquide trente-quatre.

**L'âge est cinquante-cinq ans, et cinquante à trente années de services.**
L'article 125 ouvre la pension à cinquante-cinq ans ; l'article 127 abaisse
cet âge d'un an par tranche de quatre années au fond, jusqu'à cinquante ans,
pour qui compte trente années d'affiliation. La fiche ouvrait la pension à
cinquante ans à tous, même au mineur de dix ans de services.

**Ce que les témoins disent.** Le mineur né en 1975, entré à vingt et un ans
et parti à soixante-quatre, gagne 20,7 % : la liquidation de 2039 reçoit le
coefficient et la valeur que la loi projette. Ceux de 1925 et de 1935
perdent 20,9 et 20,5 % : leur liquidation précède le coefficient, et le
plafond leur retire neuf années. Ceux de 1945, 1955 et 1965 gagnent 0,4, 4,9
et 12,7 %, le coefficient l'emportant sur le plafond à mesure qu'il monte.

**Ce qui reste.** Le moteur ne sait pas où le mineur a travaillé : à trente
années de services, il lui prête l'âge du fond et ne sert pas la
bonification de 0,15 % par trimestre au fond de l'article 138. Les
majorations de 0,5 à 14 % que l'article 131-2 accorde aux pensions liquidées
de 1987 à 2000 ne s'appliquent qu'à compter de 2001 : elles relèvent de la
pension d'aujourd'hui, que le modèle reconstitue par la règle générale, et
non de la liquidation. Aucun arrêté n'a été trouvé pour 2002, 2005, 2014,
2016 et 2018 : le coefficient précédent reste en vigueur, et 2002 porte le
plancher de 1,17 au niveau `estimee`. Avant juillet 1992, la valeur reste
celle de la fiche, interpolée entre les ancres de 1974 et 1992 ; le plafond
de cent vingt trimestres y est supposé le même qu'en 1974. Au-delà de 2026, la
valeur suit les prix de l'année écoulée et le coefficient le quotient de
l'article 131-1, salaire moyen sur prix, jamais moins que un. Enfin le
tableau de la Caisse des dépôts daté de juin 2026 écrit encore 1,454 « au
1er janvier 2025 » quand l'arrêté du 9 février 2026 a fixé 1,473 : c'est
l'arrêté qui fait foi. Le registre de veille porte la ligne
`pension_mines`.

### La CNRACL : la carrière longue lit sa durée à l'ouverture, et la surcote se compte en durée

Le même lot a lu les pages de la CNRACL, sa base juridique
(juris-cnracl.retraites.fr), les pages du FSPOEIE à la Caisse des dépôts et
quatre calculettes — le simulateur de 2010, le rachat des études, le cumul
emploi-retraite, le convertisseur de validation —, puis les textes qu'elles
appliquent : le décret n° 2003-1306, L. 13, L. 14 et D. 16-1 du code des
pensions, le XXIV de l'article 10 de la loi du 14 avril 2023. Les pages
confirment la fiche pour l'essentiel. Deux règles communes aux trois régimes
du code des pensions — l'État, la CNRACL, le FSPOEIE — ne l'étaient pas, et
trois exemples de la caisse entrent aux témoins officiels.

**La carrière longue ouverte avant soixante ans lit sa durée à l'ouverture.**
Le C du XXIV vise « les fonctionnaires civils, autres que ceux mentionnés aux
A et B du présent XXIV, et les militaires remplissant les conditions de
liquidation de la pension avant l'âge de soixante ans » : 169 trimestres pour
qui peut liquider à compter du 1er septembre 2023, un de plus en 2025 et en
2027, la durée de sa génération à compter de 2028. Avant cette date, L. 13,
III, opposait la durée des fonctionnaires ayant soixante ans l'année de
l'ouverture. Le modèle ne l'opposait qu'au militaire. La caisse l'écrit pour la
carrière longue, l'invalidité, le handicap et les parents de trois enfants —
« un fonctionnaire né en 1967 qui a un droit ouvert à 58 ans au titre des
carrières longues en 2025 aura une durée d'assurance requise de 170 trimestres
(au lieu de 172 trimestres en fonction de sa génération) » — ; de ces
départs, le modèle ne connaît que la carrière longue. La condition de la
carrière longue, elle, reste la durée de la génération : D. 16-1, dans la
rédaction du décret n° 2026-345, demande une durée cotisée « au moins égale à
la durée mentionnée à l'article L. 161-17-3 ». La pension n'en bouge que si
les services n'atteignent pas la durée — une carrière commencée ailleurs. La
Banque de France, qui emprunte le barème de décote de la fonction publique
sans relever du code des pensions, garde la durée de sa génération.

**La surcote de la fonction publique se compte en durée.** L. 14, III, retient
« le nombre de trimestres d'assurance effectués » au-delà de l'âge légal et de
la durée, et la caisse les décompte « à partir du moment où les trois
conditions cumulatives […] sont remplies », en ne gardant « que les
trimestres entiers ». Le modèle appliquait la règle que la circulaire Cnav
2018-04 donne au régime général — des trimestres civils, à compter de celui
qui suit l'âge —, et une fonctionnaire à l'âge légal à la mi-octobre 2024,
partie en février 2026, avait quatre trimestres de surcote au lieu de cinq.
Le modèle datant au mois, la période s'ouvre maintenant le premier du mois qui
suit l'âge : c'est exact pour toute naissance après le premier du mois, et
c'est ainsi que service-public.gouv.fr date le taux plein d'un fonctionnaire
né le 9 octobre 1964, « 62 ans et 9 mois (1er août 2027) ». L'exemple 3 de la
CNRACL — un agent né un 1er janvier, six trimestres depuis le 1er juillet
2024 — en a un de plus que le modèle ne lui en compte, et n'est pas transcrit.
Chaque trimestre de durée prend le taux de son dernier mois : celui de
novembre 2008 à janvier 2009 est au 1,25 % de la loi de financement pour 2009.
Aucun témoin ne bouge, leurs fonctionnaires partant à un anniversaire de
janvier, où les deux décomptes coïncident.

**Ce que les exemples et les calculettes disent encore.** Les deux exemples
de décote de la caisse — une active née en 1967 partie à soixante ans, un
sédentaire né en 1957 parti à soixante-six ans sous l'ancienne règle — sont
reproduits au taux près. Ses exemples de surcote pour les générations 1963 à
1966 datent d'avant la suspension de 2026 : leurs âges et leurs durées ne
sont plus ceux du droit, et ils ne sont pas transcrits. La calculette du
rachat des études applique, à chacun des quarante-sept âges, le barème de
D. 7-1 en vigueur depuis le 1er janvier 2026, quand celle de l'ENSAP garde le
précédent. Le convertisseur de validation de la Caisse des dépôts retrouve à
2 % près les seuils du modèle de 1972 à 2020 ; avant 1972, il en porte que le
modèle n'applique pas, validant quatre trimestres à toute année travaillée.

**Ce qui reste.** L'interpénétration : un fonctionnaire passé de l'État à la
CNRACL ou au FSPOEIE reçoit une seule pension, liquidée par le dernier
régime sur l'ensemble des services, quand le modèle en liquide une par
régime. Le rétablissement au régime général et à l'Ircantec de qui quitte la
fonction publique avant la durée minimale — quinze ans avant 2011, deux ans
depuis. La montée de quinze à dix-sept ans des services actifs, et les règles
des emplois insalubres et des réseaux souterrains de la CNRACL. Et, trouvée
en chemin, une erreur qui déborde la fonction publique, corrigée le même
jour : voir la section suivante. Le registre de veille porte les lignes
`duree_requise_carriere_longue_fonction_publique` et
`surcote_fonction_publique`.

### Les générations de 1961 à 1965 parties avant septembre 2023 devaient la durée de 2014

La loi du 14 avril 2023 a accéléré la montée de la durée requise pour les
assurés nés à compter du 1er septembre 1961 — 169 trimestres jusqu'à la fin de
1962, 170 pour 1963, 171 pour 1964, 172 à partir de 1965 —, mais le B du XXX
de son article 10 la réserve « aux pensions prenant effet à compter du
1er septembre 2023 ». Avant, L. 161-17-3 dans sa version du 22 janvier 2014
demeure : 168 trimestres de 1961 à 1963, 169 de 1964 à 1966. La circulaire
Cnav 2023-19 le dit, et son exemple de réversion oppose 169 trimestres à un
assuré né en 1965 dont la pension aurait pris effet avant cette date. Le
modèle lisait la table de 2023 quelle que soit la date d'effet — la même
erreur que celle que la suspension de 2026 avait fait corriger à l'autre
bout, en sens inverse. Ceux qu'elle touchait sont partis par un départ
anticipé, carrière longue surtout, de un à trois trimestres de trop : le
salarié né en 1962 parti en janvier 2022 doit 168 trimestres, et non 169.
Deux exemples de la circulaire entrent aux témoins officiels, et la table
`legislation/duree_requise_avant_reforme_2023.csv` s'applique dans les deux
moteurs, avant celle de la suspension. Reste la clause de sauvegarde de
l'article 8 du décret n° 2023-436 : les nés de septembre 1961 à 1963 qui
avaient leur durée cotisée avant septembre 2023 partent en carrière longue
aux conditions d'avant, avec une pension proratisée sur la durée nouvelle ;
le modèle ne la connaît pas.

### La pension différée d'un fonctionnaire suivait le point d'indice, et la loi la fait suivre les pensions

Le fonctionnaire qui quitte la fonction publique avant de pouvoir liquider —
parti au privé, au chômage, ou nulle part — touche sa pension des années plus
tard, calculée sur le traitement de l'indice qu'il détenait en partant. Le
modèle portait ce traitement jusqu'à la liquidation par le point d'indice des
actifs, comme s'il était resté en poste. La loi dit autre chose : « Le
traitement ou la solde mentionnés à l'article L. 15 sont revalorisés pendant
la période comprise entre la radiation des cadres et la mise en paiement de la
pension, conformément aux dispositions de l'article L. 16 » (L. 25 du code des
pensions, depuis le 1er janvier 2004), et la même phrase est à l'article 26 du
décret n° 2003-1306 pour la CNRACL et à l'article 22 du décret n° 2004-1056
pour les ouvriers de l'État. Ce sont donc les revalorisations des pensions
civiles — les décrets de 2004 à 2008, l'article L. 161-23-1 ensuite — qui
portent le traitement, et non le point, resté gelé de 2010 à 2016 : de 2012 à
2026, les unes font 22,2 %, l'autre 6,3 %. Un fonctionnaire de l'État entré à
vingt-deux ans, parti au privé à cinquante fin 2011 et liquidant en janvier
2026, avait un traitement de référence de 34 739 € ; il est de 39 913 €,
14,9 % de plus, et sa pension civile avec lui.

Les bornes sont celles que la CNRACL écrit : la revalorisation du jour de la
mise en paiement est due au traitement — « si la pension est due à compter de
la date de revalorisation, le traitement servant au calcul de la pension
bénéficie de la revalorisation des pensions » —, celle du jour de la
radiation ne l'est pas, pas plus qu'à la pension d'un agent radié le
1er janvier. Avant 2004, la péréquation faisait déjà suivre le point à toute
pension civile, différée ou non, et rien ne change. En 2020, le traitement
reçoit le coefficient de L. 161-25, 1 % : la dérogation de 0,3 % de l'article
81 de la loi de financement pour 2020 ne vise que « les montants des
prestations et pensions servies », et un traitement qui attend sa pension
n'en est pas une — la Cnav a revalorisé de même, cette année-là, les salaires
portés au compte. Le modèle date la radiation au 1er janvier qui suit la
dernière année de service, faute du mois. Aucun témoin existant ne bouge,
aucun cas type ne quittant la fonction publique avant de liquider ; deux
parcours entrent aux témoins pour que les deux moteurs rejouent la règle. La
Banque de France, dont le règlement n'écrit pas la phrase, garde la
revalorisation des salaires. Le registre de veille porte la ligne
`pension_differee_fonction_publique`.

### Les trimestres des enfants : un seul régime les accorde, et R. 173-15 dit lequel

Une mère passée par deux régimes ne reçoit pas deux fois les trimestres de ses
enfants, ni ceux du régime qui en accorde le plus : l'article R. 173-15 du code
de la sécurité sociale désigne le régime qui les accorde. Le modèle retenait le
plus favorable — seize trimestres du régime général pour deux enfants, contre
huit de bonification à l'État — et servait donc à la fonctionnaire passée par
le privé les trimestres du régime général. Le droit suit un ordre, le même
depuis la version de 1985 : le régime spécial accorde « en priorité […] si
celui-ci est susceptible d'accorder en vertu de ses propres règles une pension
à l'intéressé » ; sinon le régime général, prioritaire parmi les régimes
alignés ; sans lui, le régime de la dernière affiliation. La CNRACL l'écrit,
jugement à l'appui : l'agent ne peut pas renoncer à la bonification qu'elle
sert pour la faire servir par un autre régime (TA Amiens, 2 juin 2017).

Pouvoir servir une pension, c'est avoir servi la durée que le régime exige, et
le modèle ne la connaissait nulle part. Elle est dans
`services_ouvrant_pension.csv`, lue régime par régime. Quinze ans partout
avant les réformes ; deux ans pour les fonctionnaires radiés depuis 2011
(R. 4-1 du code des pensions) ; un an pour les agents partis de la SNCF, de
la RATP, des IEG et de l'Opéra depuis le 1er juillet 2008. Aucune durée à la
Banque de France depuis 2012, à la Comédie-Française depuis 2008, ni pour la
pension spéciale des marins. À la SEITA, quinze ans pour qui part avant
l'âge, aucune durée pour qui l'atteint en fonctions. Les règlements de la
SNCF et de la RATP d'avant 2008 ne sont pas dans l'index : leurs quinze ans
viennent des fiches du COR, au niveau `moyenne`.

Et le droit doit être ouvert, ce qui se lit sur la date de naissance des
enfants, que le modèle fixe aux trente ans de la mère. Pour un enfant né
depuis 2004, L. 12 bis ne sert que les femmes « ayant accouché postérieurement
à leur recrutement ». Pour un enfant né avant, R. 13 sert tout enfant jusqu'en
2003, l'enfant né en service de 2004 à 2010, et, depuis 2011, l'enfant né
avant la radiation, le congé de maternité du code de la sécurité sociale
suffisant. Une femme recrutée à quarante ans après des enfants nés en 2010
reçoit donc la majoration du régime général ; si ses enfants sont nés en
1992, elle reçoit la bonification de l'État.

Moins de trimestres ne veut pas toujours dire moins de pension. Prenons une
fonctionnaire de l'État entrée à vingt-deux ans, passée au privé à cinquante
et liquidant en 2026, mère de deux enfants : elle perd huit trimestres et
755 € par an, de 34 147 à 33 392 €. Une salariée du privé recrutée par
l'État à quarante ans, du même âge et mère de deux enfants nés avant son
recrutement, gagne au contraire 407 €, de 33 603 à 34 011 € : huit trimestres
au prorata d'une pension civile à 79,7 % du dernier traitement valent plus
que seize au prorata d'une pension du régime général calculée sur un salaire
annuel moyen plus bas. Parmi les régimes alignés, la priorité
du régime général déplace aussi la majoration d'une artisane passée au
salariat avant la liquidation unique : de 21 091 à 21 526 €.

Ce que le modèle ne fait pas, et le dit. Il applique à tous les régimes
spéciaux les conditions de la fonction publique, comme il leur applique déjà
sa table des bonifications. Il ne distingue pas les militaires, qui ont gardé
quinze ans jusqu'en 2014. Il présume pouvoir pensionner, au niveau
`estimee`, les régimes dont aucun texte n'est dans l'index : le port de
Strasbourg, la caisse de Nouvelle-Calédonie, les chemins de fer secondaires,
les pensions d'avant 1948. Il ne rétablit pas au régime général l'agent qui
n'a pas la durée : faute de régime aligné pour la recevoir, sa majoration
reste donc au régime spécial. Et trois cas restent hors du modèle :
l'exception de la CRPCEN, dont la fiche ne déclare pas de bonification ; la
pension statutaire liquidée avant la naissance ; l'enfant handicapé. Le
registre de veille porte la ligne `priorite_majorations_enfants`.

### L'État, la CNRACL et le FSPOEIE ne servent qu'une pension : celle du dernier régime

Les trois régimes du code des pensions sont interpénétrés. L'État compte et
liquide les services accomplis « par les fonctionnaires titulaires et
stagiaires mentionnés à l'article 2 de la loi n° 83-634 » — ceux des trois
fonctions publiques — et ceux des ouvriers de ses établissements industriels
(L. 5 et L. 11 du code des pensions). La CNRACL compte « les services de
titulaire ou de stagiaire accomplis dans la fonction publique d'État » et ceux
des affiliés du FSPOEIE (articles 8 et 13 du décret n° 2003-1306). Le FSPOEIE
compte les services de L. 5 (articles 4 et 10 du décret n° 2004-1056). Le
régime de la dernière affiliation sert donc une pension unique, qui
« rémunère l'ensemble de sa carrière » (juris-cnracl). Elle est calculée sur
un seul traitement, celui des six derniers mois de la carrière publique, et
proratisée sur tous ses services. La règle est ancienne : L. 5 comptait déjà
en 1964 les « services accomplis dans les cadres permanents des
administrations des départements, des communes », et l'article 8 du décret
CNRACL de 1965 les services de l'État.

Le modèle liquidait chaque régime sur ses seules années et sur son propre
traitement. Prenons un fonctionnaire de l'État entré à vingt-deux ans, devenu
territorial à quarante et liquidant en 2026. Il touchait deux pensions : une
de l'État, calculée sur son traitement de 2001, et une de la CNRACL, au
prorata de ses vingt-quatre dernières années. Soit 28 123 € par an, quand la
pension unique en vaut 32 731 : 14,1 % de moins.
Dans l'autre sens, un territorial devenu fonctionnaire de l'État perdait
15,8 %, et un ouvrier de l'État devenu fonctionnaire 16,3 %. Le passage par
le privé ne défait rien. Une fonctionnaire partie de l'État après huit ans,
restée quinze ans au privé puis revenue à l'hôpital, liquide ses vingt-sept
ans de services publics à la CNRACL, et sa pension totale gagne 10,6 %.
Partie en 1992 sans ses quinze ans, elle aurait été rétablie au régime
général ; l'article 64 du décret n° 2003-1306 annule ce rétablissement à son
retour.

Le moteur avait déjà l'outil. Ses groupes de succession liquidaient ensemble
un régime et celui qui lui a succédé, sur un salaire de référence et une
proratisation communs, sous les règles du dernier. Les trois régimes y
entrent sous une même clé, comme les régimes alignés de la liquidation
unique. La priorité des trimestres d'enfants suit : la durée qui ouvre une
pension et les dates de recrutement et de radiation se lisent désormais sur
les trois régimes ensemble. Les services actifs se comptaient déjà
« indifféremment » dans les trois (L. 24, article 25 du décret
n° 2003-1306).

Deux limites. Le militaire titulaire d'une pension militaire la garde, et n'y
renonce pour une pension unique que par un choix exprès (L. 77) : le modèle
laisse donc à part une carrière d'État seulement militaire. Mais il ne scinde
pas la pension de l'État entre services civils et militaires : un militaire
devenu fonctionnaire civil reçoit une pension unique, comme s'il avait
renoncé à la sienne. Par ailleurs, les lignes du modèle ne sont pas datées au
mois : quand deux régimes du groupe finissent la même année, il retient
celui que désigne la chaîne des successions. Aucun exemple chiffré publié n'a
été trouvé. Le registre de veille porte la ligne
`interpenetration_fonction_publique`.

### Le fonctionnaire parti sans droit à pension n'en a pas : il est rétabli au régime général

Qui quitte la fonction publique avant la durée qui ouvre une pension — quinze
ans de services pour qui est radié avant 2011, deux depuis (R. 4-1 du code des
pensions) — n'a pas de pension de son régime. Il est « rétabli, en ce qui
concerne l'assurance vieillesse, dans la situation qu'il aurait eue s'il avait
été affilié au régime général des assurances sociales et à [l'Ircantec]
pendant la période où il a été soumis au présent régime » (L. 65 du code des
pensions ; article 64 du décret n° 2003-1306 pour la CNRACL ; D. 173-15 et
D. 173-16 du code de la sécurité sociale, qui nomment aussi les ouvriers de
l'État et la SEITA). Le modèle lui servait une pension de son régime au
prorata de ses années, comme s'il y avait eu droit, et le régime général ne
voyait pas ces années.

Deux assiettes, que les textes séparent. Le régime général porte au compte
« des salaires reconstitués à partir des cotisations rétroactives calculées
sur la base des derniers émoluments ou de la dernière solde soumis à retenues
pour pension [...], dans la limite du plafond en vigueur » (circulaire Cnav
2011/38) : le dernier traitement, pour toutes les années, écrêté au plafond de
chacune. La période « entre en compte, quel qu'ait été le montant de sa
rémunération » (D. 173-16). L'Ircantec valide « suivant sa propre
réglementation » (article 9 du décret n° 70-1277), et le modèle y porte le
traitement de chaque année. Les primes restent au RAFP, que le rétablissement
ne touche pas. Le tout pour qui a quitté son régime après le 28 janvier 1950,
date que la Cnav tient du décret n° 50-133, dont D. 173-16 est issu.

Prenons un agent hospitalier entré à vingt-deux ans, parti au privé à
trente-cinq, en 1997, et liquidant en 2026 : sans ses quinze ans, la CNRACL
ne lui doit rien. Le modèle lui servait 6 171 € de la CNRACL, et un régime
général proratisé sur ses seules années de privé. Rétabli, il reçoit 20 916 €
du régime général, qui compte désormais ses treize années, et 2 103 € de
l'Ircantec : sa pension passe de 26 312 à 28 718 €. Dix ans sous l'uniforme
de 1980 à 1989 déplacent 2,0 %. Le sens peut s'inverser. La mère de deux
enfants passée un an par l'État en 1984, qui a déjà sa durée au régime
général, ne gagne rien au régime général et perd les 423 € de pension civile
que le modèle lui servait sans qu'ils lui soient dus ; l'Ircantec lui en rend
130.

Le retour dans l'un des trois régimes interpénétrés annule le rétablissement
(article 64, II, du décret n° 2003-1306) : c'est la même lecture des services
des trois régimes ensemble, faite pour la pension unique, qui en décide. Les
trimestres des enfants suivent R. 173-15 : la mère rétablie les reçoit du
régime général. Et la lecture des textes a corrigé la durée des militaires,
que le modèle ne distinguait pas des civils : ils ont gardé quinze ans, et la
loi n° 2014-40 ne leur donne les deux ans de R. 4-1 que s'ils se sont engagés
à compter du 1er janvier 2014 (article 42, II). Un militaire engagé en 2012 et
parti en 2016 est donc rétabli.

Ce que le modèle ne fait pas, et le dit. Le militaire reçoit au régime général
sa dernière solde, et non les salaires forfaitaires par catégorie que la Cnav
reporte (D. 173-17). L'Ircantec ne prend pas la NBI, qu'elle retient pourtant.
Sa validation, faite sur demande pour qui a été radié avant 1990, est présumée
demandée. Les services d'avant le 1er juillet 1930, que D. 173-16 exclut, sont
rétablis comme les autres. L'agent parti avant le 29 janvier 1950 garde la
pension au prorata que le modèle lui servait, le droit d'alors n'ayant pas été
lu. Et les régimes spéciaux qui ont leur propre coordination — la pension de
sécurité sociale de coordination de la RATP, de la SNCF, des IEG, la Banque de
France — restent hors du modèle. Aucun exemple chiffré publié n'a été trouvé.
Le registre de veille porte la ligne `retablissement_fonction_publique`.

---

## 5. Ce que le modèle ne calcule pas, et pourquoi

### La recette du scénario 6 : la variante `rapport`, et les décisions du 19 septembre 2026

Ce qui suit raconte comment la recette du scénario 6 a été établie, mesure
par mesure et décision par décision. Ses chiffres sont ceux du jour de chaque
mesure, et plusieurs ont bougé depuis ; ce que le solde et le coefficient
valent aujourd'hui est au §6 du README, que la prose recalcule.

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
  | Scénario 6, convention `assiette` (affichée) | **−1,22 % du PIB** | **0,83** | jamais |
  | Scénario 6, convention `rapport` | −0,53 % | 0,91 | 2026 |
  | Système actuel | −1,13 % | — | jamais |

  Deux effets de sens contraire séparent ces deux lignes, et il faut les
  compter séparément. Le taux plein rapporte PLUS que le rapport de taux
  légaux ne le disait — 18 % d'assiette au lieu de 15,5, soit deux points et
  demi d'assiette gagnés. Mais la convention du programme ne fait pas que poser
  un taux : elle RETIRE aussi les trois postes qui n'acquièrent de droits à
  personne, et ce second effet l'emporte largement sur le premier. **Sous sa
  propre convention, la proposition est donc plus déficitaire que le système
  qu'elle remplace**, d'un dixième de point de PIB en moyenne — d'un point encore
  avant le recalcul du 22 septembre, les niveaux ayant bougé depuis (voir la
  table ci-dessous) —, là où l'ancienne la donnait au-dessus de lui. C'est le chiffre d'un système qui ne vit que de ses
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
  ni l'autre** : ils ne valident aucun trimestre pour une année non
  travaillée, et la garantie vieillesse qui remplace le minimum vieillesse est
  financée à part, par l'impôt, hors du compte des cotisants. C'est mot pour
  mot la règle que le dépôt applique déjà à la CNAF — LA RECETTE SUIT LE
  DROIT —, et le Fonds de solidarité vieillesse y échappait parce que sa
  recette entre dans les comptes sous un autre nom. Le reste du poste — taxe
  sur les salaires, forfait social, contribution sociale de solidarité des
  sociétés, et les taxes des régimes agricoles — finance des pensions
  ordinaires, et rien ne justifie de l'ôter.

  *Ce que cela donne, et c'est fait.* Le fonds est entré dans le retrait le
  19 septembre 2026, avec sa série certifiée, à côté de la branche famille et
  de l'assurance chômage — laquelle en est sortie le 23 septembre, voir
  plus bas : ce qu'il VERSE — 15,2 Md€ de cotisations prises en
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
  scénario 6 passe de +0,17 % du PIB, poste reconduit, à **−1,22 %**, contre
  −1,13 % pour le système actuel : il est désormais plus déficitaire que lui
  dans 29 des 45 années, et ne revient à l'équilibre sur aucune. Son
  coefficient d'équilibre de 2040 — ce que le système peut servir rapporté à ce
  qu'il promet — descend de 0,98 à **0,83**.

  *Et ce coût est le seul chiffre de ce paragraphe qui n'ait jamais bougé.* Les
  NIVEAUX, eux, ont changé trois fois depuis la décision, chaque fois pour une
  raison qui n'a rien à voir avec l'impôt :

  | Mesuré le | Poste reconduit | Poste sorti | Coût |
  |---|---|---|---|
  | 19 septembre au soir, à la décision | −1,12 % | −2,51 % | 1,395 |
  | après que la réversion eut quitté les cinq scénarios notionnels | −0,28 % | −1,67 % | 1,395 |
  | après que le profil de carrière fut lu chez l'INSEE | −0,76 % | −2,16 % | 1,395 |
  | recalculé le 22 septembre 2026 | +0,17 % | −1,22 % | 1,395 |

  Quatre mesures, quatre niveaux, un seul coût. C'est ce qu'on attend d'une
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
  scénarios notionnels suppriment les premiers droits ; ils comptaient
  pourtant ces recettes, auxquelles s'ajoute depuis le 19 septembre 2026 le
  fonds de solidarité vieillesse, 0,67 point de plus. La série
  `transferts_retraite.csv` les lit chez celui qui paie, dans les rapports à
  la Commission des comptes de la Sécurité sociale, de 2013 à 2024 (l'Unédic)
  ou 2025 (la CNAF) ; les rapports d'avant 2013 sont chiffrés ou compressés
  d'une façon que le lecteur PDF du dépôt n'ouvre pas. Le coefficient
  d'équilibre des scénarios notionnels les RETIRE : année par année là où on
  les connaît, à part constante des ressources avant 2013 et sur tout
  l'horizon projeté — personne ne projette ce que la CNAF versera en 2070, et
  une part constante est l'hypothèse qui n'en ajoute aucune autre. Le jour où
  il est entré, cela ramenait le scénario 3 en 2070 de 1,94 à 1,87 et le
  scénario 5 de 1,17 à 1,13. **Deux choses y étaient fausses, et le sont
  restées jusqu'au 23 septembre 2026.** L'Unédic était retirée au motif que
  les scénarios notionnels ne portaient rien au compte pendant une année de
  chômage : ils y portaient, depuis toujours, les cotisations complémentaires
  qu'elle verse. Sa recette leur est rendue, et le retrait ne compte plus que
  la branche famille et le fonds. Et le retrait frappait les scénarios 3 et 5
  dès 2013, ce qui les mettait en déficit en 2025, où ils servent encore les
  pensions du système actuel : avant la bascule, ils SONT ce système, et en
  encaissent toutes les recettes. Le système actuel encaisse tout et garde le
  solde du COR.
  Le coefficient n'est toujours pas appliqué, et ce que la branche famille
  ferait de ce qu'elle cesserait de verser est une décision de programme, pas
  un résultat du modèle. Depuis le 18 septembre 2026, ce retrait n'est plus la
  seule réaction des recettes : voir le point précédent.

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
| Système actuel, convention du COR | **<!--chiffre:mesure(engagement)-->520<!--/--> %** |
| — dont retraités (pension entière acquise) | <!--chiffre:mesure(engagement?quoi=retraites)-->196<!--/--> % |
| — dont actifs, au prorata de la carrière faite | <!--chiffre:mesure(engagement?quoi=actifs)-->324<!--/--> % |
| Proposition (système 6) | <!--chiffre:mesure(engagement?scenario=6)-->363<!--/--> % |
| Notionnel part salariale (système 2) | <!--chiffre:mesure(engagement?scenario=2)-->167<!--/--> % |
| Publié par Eurostat, tableau 29 | <!--chiffre:mesure(engagement?quoi=publie)-->397<!--/--> % |

La proposition doit moins parce qu'elle promet moins : c'est la même règle qui
fait baisser ses pensions et son engagement, et le rapport des deux est à peu
près celui des masses.

Chaque système y revalorise ce qu'il sert selon SA règle, celle de ses masses :
les prix pour le système actuel, que l'article L. 161-23-1 du code de la
sécurité sociale y indexe, la règle du compte pour les systèmes notionnels.
Jusqu'au 23 septembre 2026, l'engagement revalorisait aussi le système actuel
sur la règle notionnelle, plus rapide que les prix, et le trouvait d'un dixième
plus haut ; un test double désormais la règle notionnelle et vérifie que
l'engagement du système actuel ne bouge pas.

**L'écart avec le chiffre publié est un TAUX, pas un droit.** Les mêmes droits,
actualisés **<!--chiffre:mesure(engagement?quoi=ecart)-->1,3<!--/--> point de plus par an**, valent exactement les
<!--chiffre:mesure(engagement?quoi=publie)-->397<!--/--> % d'Eurostat. Ni l'un ni l'autre n'est faux : un engagement acquis n'a pas de
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
**<!--chiffre:mesure(engagement?quoi=hors_projection)-->29<!--/--> points sur <!--chiffre:mesure(engagement)-->520<!--/-->** : le résultat ne dit donc pas d'abord
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

### L'écart au COR, et ce que chaque correction en a appris

Ce qui suit est une chronique, datée action par action : chaque paragraphe
dit ce qu'une correction a déplacé le jour où elle a été faite, et ses
chiffres sont ceux de ce jour-là. La trajectoire d'aujourd'hui est celle du
paragraphe précédent.

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

**Les cinq scénarios notionnels bougent cinq fois moins que le système
actuel** : de −0,10 à −0,03 point de PIB en 2070, mesuré le 23 septembre 2026
(le 21, de −0,03 à +0,03). L'erreur d'âge leur est presque invisible, et la
raison est dans le mécanisme — dans un compte notionnel, partir plus tôt
allonge le diviseur autant que la carrière raccourcie retire au capital, et les
deux termes se répondent. C'est la raison chiffrée de ne réécrire aucune fiche
pour ce que le site argumente.

**Le système actuel bouge, et dans le mauvais sens** : 18,26 % du PIB en 2070
sous les fiches, 18,77 % sous le contrefactuel, mesuré le 23 septembre 2026.
L'écart avec la projection du COR de juin 2026, 15,3 %, passe de 2,96 à 3,47
points — corriger les âges ÉLOIGNE le modèle du COR au lieu de l'en
rapprocher. **L'âge de départ n'explique donc pas l'écart que
cette section laisse ouvert**, et la piste du taux de remplacement reste
entière. Une réserve sur ce +0,51 point : déplacer l'âge d'entrée déplace aussi
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
