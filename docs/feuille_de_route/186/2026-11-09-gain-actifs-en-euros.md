# Le gain des actifs en euros : pourquoi il croît avec le salaire, et trois façons de le rendre

**Reprise, au 13 novembre 2026.** Le propriétaire a tranché le 13 novembre :
le même taux pour tous, 18 %, et un gain qui croît avec le salaire (décisions
108 et 130) ; ni forfait ni franchise. Restent deux questions de détail pour
lui : la part patronale du pilier au SMIC, et le chiffre que le message montre
au SMIC, 91 € ou 39 €.

*Le 9 novembre 2026, action 186, chantier 1. Le constat du chantier 8 : aux
taux de la proposition, le salaire net gagne 39 € par mois au SMIC et 417 €
à cinq SMIC ; l'adversaire dira « un cadeau aux cadres ». Le propriétaire
demande pourquoi le gain est si faible au SMIC, puis trois façons de rendre
aux cotisants leur part, comparées sous les deux lectures de la décision 29,
sans trancher entre elles. Chaque chiffre porte son origine : **(publié)**,
un texte lu ce jour à sa source, par l'index de la DILA ; **(dépôt)**, une
donnée ou un document du dépôt, ou le modèle tel qu'il est, au commit
`1c32439` ; **(calcul)**, un calcul de cette note, posé ici, paramètres du
modèle changés en mémoire compris. Le script est resté dans le brouillon de
la session, hors du dépôt. Un tableau porte sa marque dans son titre.*

## En bref

- **Le gain est faible au SMIC pour trois raisons qui s'empilent.** Une
  baisse de taux donne des euros en proportion du salaire. Au SMIC,
  l'employeur ne verse déjà plus un euro de cotisation de retraite : la
  réduction générale l'efface, il n'y a rien à rendre de ce côté. Et la part
  patronale du pilier capitalisé, hors de cette réduction, devient une charge
  neuve de 66 € par mois, que la convention « à coût du travail constant »
  reprend sur le salaire brut : 91 € deviennent 39 €.
- **Le même montant pour chacun inverse le reproche.** Sous la lecture B, le
  forfait vaut 252 € par mois à tous les salaires, contre 129 € au SMIC et
  597 € à cinq SMIC par la baisse du taux. Sous la lecture A, il ne reste que
  63 € à partager, par tête.
- **Mais sur un compte notionnel, le salaire et la pension sont le même
  argent.** Si le compte n'est crédité que de ce qui est payé, le forfait de
  la lecture B fait tomber la pension du salarié au SMIC au plancher de la
  garantie. S'il est crédité quand même, quelqu'un paie : l'État, 23 Md€ par
  an sous A et 92 Md€ sous B ; ou les autres cotisants, par des cotisations
  sans droits, ce que le programme reproche au système actuel.
- **Au SMIC, le compte est déjà crédité par l'impôt.** Aujourd'hui, 60 % de
  la cotisation de retraite d'un salarié au SMIC est effacée par la réduction
  générale, et ses droits restent entiers ; sous la proposition, ce serait
  64 % (A) à 80 % (B) de ce que son compte reçoit. « Chaque pension vaut ce
  qui a été cotisé » n'y tient que si « cotisé » compte ce que l'impôt verse
  à la place de l'employeur.
- **Un précédent pèse sur la franchise** : le Conseil constitutionnel a
  censuré en 2014 une baisse dégressive des cotisations salariales qui
  laissait les droits inchangés.

## 1. Pourquoi 39 € au SMIC et 417 € à cinq SMIC

### Les textes

- **La réduction générale** (publié, article L. 241-13 du code de la
  sécurité sociale, version en vigueur au 1er janvier 2026,
  LEGIARTI000053280526). Son I : « Font l'objet d'une réduction dégressive
  les cotisations à la charge de l'employeur dues au titre des assurances
  sociales et des allocations familiales, […] les cotisations à la charge de
  l'employeur dues au titre des régimes de retraite complémentaire
  légalement obligatoires mentionnés à l'article L. 921-4 du présent code ou
  créés par la loi ». Son III : « La valeur maximale du coefficient est
  fixée par décret, dans la limite de la somme des taux des cotisations et
  contributions incluses dans le périmètre de la réduction » ; sa valeur
  « devient nulle lorsque la rémunération […] atteint le montant fixé par
  décret prévu au I », montant « compris entre le salaire minimum de
  croissance applicable au 1er janvier 2024 majoré de 200 % et le salaire
  minimum de croissance en vigueur majoré de 200 % » : trois SMIC.
- **Ses paramètres** (dépôt, `legislation/prelevements_remuneration.yaml`,
  d'après les décrets n° 2025-887 du 4 septembre 2025 et n° 2025-1446 du
  31 décembre 2025, que la session n'a pas rouverts) : coefficient maximal
  de 40,21 %, somme exacte des dix taux du périmètre ; plancher de 2 % ;
  extinction à 3 SMIC. La retraite y entre pour 16,67 points : vieillesse
  plafonnée 8,55, déplafonnée 2,11, Agirc-Arrco 4,72, contribution
  d'équilibre général 1,29.
- **Qui paie ce qu'elle efface** (publié, article L. 131-7, version en
  vigueur au 1er janvier 2026, LEGIARTI000051285503). Son I pose que « toute mesure de réduction ou
  d'exonération de cotisations de sécurité sociale […] donne lieu à
  compensation intégrale aux régimes concernés par le budget de l'État » ;
  son II que « le I n'est pas applicable […] à l'article L. 241-13 ». La
  réduction générale n'est donc pas remboursée à l'euro : la sécurité sociale
  reçoit à la place une fraction de la TVA, 28,14 % de la TVA nette prévus
  pour 2025, soit 60,5 Md€, dont de l'ordre de 7 Md€ vont à l'Agirc-Arrco
  (dépôt, `2026-11-07-recettes-tva-lvt.md`). La décision 79 garde cette
  part.

### Le calcul, posé au SMIC

Salarié du privé non cadre, 2026, par mois. Le SMIC : 12,02 € de l'heure
(dépôt) × 1 820 heures ÷ 12 = 1 823,03 € brut (calcul).

*Aujourd'hui* (dépôt, `remuneration.py`) :

- le salarié verse pour la retraite 11,31 % : 206,15 € ;
- l'employeur doit, au barème, 16,67 % : 303,94 € ;
- la réduction générale vaut 40,21 % × 1 823,03 = 733,04 €, dont
  16,67 ÷ 40,21 portent sur la retraite : 303,92 €. **L'employeur verse
  donc 0 € pour la retraite** ;
- net 1 443,15 € ; coût du travail 1 873,68 €.

*Sous la proposition, 18 % et 5 % capitalisés* (dépôt, partage du
20 septembre : l'employeur garde 16,67 points, l'assuré passe à 6,33) :

1. Le salarié verse 6,33 % × 1 823,03 = 115,40 €. Sa fiche gagne
   206,15 − 115,40 = **90,75 €** (calcul).
2. L'employeur doit 13,05 % pour le compte notionnel, 237,83 €, et 3,62 %
   pour le pilier, 66,07 €. Les 13,05 points sont dans le périmètre : le
   coefficient maximal devient 40,21 − 16,67 + 13,05 = 36,59 %, et la
   réduction les efface. Les 3,62 points du pilier n'y sont pas (dépôt,
   `bloc_taux_unique` : le pilier n'est « ni une assurance sociale, ni un
   régime complémentaire légalement obligatoire ») : l'employeur les verse.
   Le coût du travail passe de 1 873,68 à 1 939,71 €, **+66,03 €**, soit
   +3,5 % (calcul).
3. La convention « à coût du travail constant », celle du constat, reprend
   ces 66 € sur le salaire brut. Sous le SMIC, un euro de brut coûte
   1 939,71 ÷ 1 823,03 = 1,0640 € ; le brut qui ramène le coût à 1 873,68 €
   est 1 873,68 ÷ 1,0640 = 1 760,98 €, soit 62,05 € de moins. Un euro de
   brut laisse 1 533,90 ÷ 1 823,03 = 0,8414 € de net : le salarié perd
   62,05 × 0,8414 = 52,21 €. Reste 90,75 − 52,21 = **38,54 €**, les 39 € du
   constat (calcul).
4. Or 1 760,98 € est sous le SMIC, ce que le droit interdit ; le modèle le
   signale (dépôt, `brut_sous_le_smic`). Au SMIC, ce qui se passerait
   vraiment est le point 1 et le point 2 : **+91 € pour le salarié, +66 €
   pour son employeur**, au niveau de salaire où l'emploi est le plus
   sensible à son coût.

*À cinq SMIC*, 9 115,17 € brut (dépôt et calcul) : aucune réduction générale.
Le salarié verse aujourd'hui 982,59 € ; sous la proposition,
6,33 % × 9 115,17 = 576,99 € : +405,60 €. L'employeur verse 1 539,44 € puis
16,67 % × 9 115,17 = 1 519,50 € : 19,94 € de moins, qui remontent dans le
brut à coût constant, d'où 417,33 €.

### Les six niveaux

Par mois, 2026 (dépôt, modèle tel qu'il est ; les pourcentages : calcul).

| Salaire brut | 1 SMIC | 1,2 | 1,5 | 2 | 3 | 5 |
|---|---:|---:|---:|---:|---:|---:|
| Brut, € | 1 823 | 2 188 | 2 735 | 3 646 | 5 469 | 9 115 |
| Aujourd'hui : retenue du salarié pour la retraite | 206 | 247 | 309 | 412 | 609 | 983 |
| Aujourd'hui : cotisation patronale de retraite, au barème | 304 | 365 | 456 | 608 | 923 | 1 539 |
| dont effacée par la réduction générale | 304 | 228 | 151 | 81 | 0 | 0 |
| Retraite réellement versée par l'entreprise et le salarié | 206 | 384 | 614 | 939 | 1 532 | 2 522 |
| en part du brut | 11,3 % | 17,6 % | 22,4 % | 25,7 % | 28,0 % | 27,7 % |
| Proposition : gain net, brut inchangé | +91 | +109 | +136 | +182 | +262 | +406 |
| Proposition : coût du travail, au jour 1 | +66 | +48 | +29 | +12 | −12 | −20 |
| Proposition : gain net, à coût du travail constant | +39 | +87 | +121 | +175 | +269 | +417 |

### Ce que cela dit

1. **Une baisse de taux est proportionnelle.** Cinq points de 1 823 € font
   91 € ; cinq points de 9 115 €, 406 € (un peu moins de cinq fois, la
   retenue d'aujourd'hui étant plus faible au-dessus du plafond). C'est le
   rapport de 1 à 4,5 de la ligne « brut inchangé ».
2. **Au SMIC, la retraite ne pèse déjà que 11,3 % du brut, contre 27,7 % à
   cinq SMIC.** L'employeur n'y verse rien : la réduction générale efface ses
   16,67 points, et c'est la TVA qui les remplace. La réforme ne peut rendre
   au salarié au SMIC une cotisation patronale que personne, dans
   l'entreprise, ne paie.
3. **Le pilier, hors de la réduction, coûte au SMIC.** C'est lui qui fait
   passer le gain de 91 à 39 € dans la convention du constat, et le rapport
   de 1 à 4,5 à un rapport de 1 à 11. L'effet s'éteint avec la réduction :
   22 € à 1,2 SMIC, 7 € à 2 SMIC, rien à 3 SMIC.

Le chiffre de 39 € est donc une convention de long terme que le SMIC rend
impossible ; le chiffre du lendemain de la réforme est 91 €.

## 2. Les trois façons, et ce qui leur est commun

**Le cadre.** Le salarié du privé non cadre de 2026 ; l'employeur garde ses
16,67 points (règle du 20 septembre) ; les cinq points du pilier sont
prélevés. Les taux des lectures sont ceux du chantier 1, avec la part de TVA
et la LVT centrale : **A 21,2 %, B 15,9 %** (dépôt ; refaits ce jour par
`scripts/lectures_decision_29.py` : 21,22 % et 15,94 %). Le taux qui laisse
la fiche d'aujourd'hui où elle est, sous le plafond : 27,98 − 5 =
**22,98 %** (calcul). La baisse à rendre : 22,98 − 21,2 = **1,78 point**
sous A ; 22,98 − 15,9 = **7,08 points** sous B ; 4,98 points aux 18 % du
programme, donnés en repère.

Sans la TVA ni la LVT, le taux de A est 25,3 % (dépôt), au-dessus de
22,98 % : il n'y a rien à rendre, et un forfait y serait un prélèvement par
tête. Tout ce qui suit vaut avec elles.

**1. La baisse uniforme du taux**, la règle d'aujourd'hui. L'assuré verse
le taux de la lecture plus 5, moins 16,67 : 9,53 % du brut sous A, 4,23 %
sous B. Le compte est crédité du taux de la lecture.

**2. Le même montant pour chaque actif.** Chacun verse comme aujourd'hui
(22,98 % et le pilier) et reçoit le même forfait, qui rend la même somme en
tout : la baisse multipliée par le salaire moyen. Le salaire moyen par tête :
41 620,93 € en 2025 (dépôt, comptes nationaux) × 1,0245 (dépôt, projection)
= 42 640,64 € par an, 3 553,39 € par mois (calcul). Le forfait :
1,78 % × 3 553,39 = **63,25 € par mois** sous A ;
7,08 % × 3 553,39 = **251,58 €** sous B ; 176,96 € aux 18 % (calcul).

**3. La franchise.** Sur les premiers euros de son salaire brut du mois,
l'assuré ne verse pas sa part de la cotisation de répartition ; au-delà, il
la verse comme aujourd'hui. Sa part : 22,98 % × 11,31 ÷ 27,98 = 9,289 % du
brut (calcul) ; sa part du pilier, 2,02 %, reste due. Le gain :
9,289 % × le plus petit du salaire et de la franchise. La franchise qui
rend la même somme en tout :

- sous A, 1,78 ÷ 9,289 × 3 553,39 = **681 € par mois** (calcul), sous tout
  salaire à temps plein : chacun gagne 9,289 % × 681 = 63,25 €. **À temps
  plein, la franchise de A est le forfait** ; elle ne s'en sépare que pour
  les temps très partiels ;
- sous B, il faut que le salaire couvert par la franchise fasse, en moyenne,
  7,08 ÷ 9,289 = 76,2 % du salaire moyen. La dispersion des salaires du
  privé à temps complet de 2024 (dépôt, `dispersion_salaires.csv` : centile
  10 à 0,509 salaire moyen, médiane à 0,822, centile 90 à 1,609, centile 99
  à 3,678), interpolée entre ses centiles, donne une franchise de 0,90
  salaire moyen : **3 205 € par mois, 1,76 SMIC** (calcul, ordre de
  grandeur : sans temps partiel). Le gain monte avec le salaire jusque-là,
  puis plafonne à 9,289 % × 3 205 = 298 €.

**Ce qui est commun aux trois.** Deux effets ne dépendent pas de la façon
de rendre. Au-dessus du plafond de la sécurité sociale (4 005 € par mois),
la retenue d'aujourd'hui est inférieure à 11,31 % : le taux unique sans
plafond reprend 10 € à 3 SMIC et 48 € à 5 SMIC (calcul : 11,31 % × 9 115,17
= 1 030,93, contre 982,59). Et la part patronale du pilier, hors de la
réduction générale, coûte à l'employeur 54 à 73 € au SMIC selon le taux,
que la convention « à coût constant » reprend sur le brut.

## 3. Le gain net par mois

En euros par mois, 2026, par rapport à la fiche d'aujourd'hui (calcul :
`remuneration.py`, barèmes changés en mémoire). « Brut inchangé » est le
lendemain de la réforme ; « coût constant », la convention du constat.

**Lecture A, 21,2 %** : 1,78 point à rendre.

| | 1 SMIC | 1,2 | 1,5 | 2 | 3 | 5 |
|---|---:|---:|---:|---:|---:|---:|
| Taux uniforme, brut inchangé | +32 | +39 | +49 | +65 | +87 | +114 |
| Taux uniforme, coût constant | −12 | +20 | +36 | +60 | +94 | +125 |
| Forfait de 63 €, brut inchangé | +63 | +63 | +63 | +63 | +53 | +15 |
| Forfait de 63 €, coût constant | +23 | +46 | +52 | +58 | +60 | +26 |
| Franchise de 681 € | comme le forfait | | | | | |

Posé au SMIC : taux uniforme, 1,78 % × 1 823,03 = 32,45 € ; forfait,
63,25 €. À cinq SMIC : taux uniforme, 1,78 % × 9 115,17 − 48,34 = 113,91 € ;
forfait, 63,25 − 48,34 = 14,91 €.

**Lecture B, 15,9 %** : 7,08 points à rendre.

| | 1 SMIC | 1,2 | 1,5 | 2 | 3 | 5 |
|---|---:|---:|---:|---:|---:|---:|
| Taux uniforme, brut inchangé | +129 | +155 | +194 | +258 | +377 | +597 |
| Taux uniforme, coût constant | +70 | +130 | +177 | +251 | +384 | +609 |
| Forfait de 252 €, brut inchangé | +252 | +252 | +252 | +252 | +242 | +203 |
| Forfait de 252 €, coût constant | +211 | +234 | +240 | +247 | +248 | +214 |
| Franchise de 3 205 €, brut inchangé | +169 | +203 | +254 | +298 | +288 | +249 |
| Franchise de 3 205 €, coût constant | +124 | +184 | +241 | +293 | +294 | +260 |

Posé au SMIC : taux uniforme, 7,08 % × 1 823,03 = 129,07 € ; forfait,
251,58 € ; franchise, 9,289 % × 1 823,03 = 169,34 €. À cinq SMIC : taux
uniforme, 7,08 % × 9 115,17 − 48,34 = 597,01 € ; forfait, 251,58 − 48,34 =
203,24 € ; franchise, 9,289 % × 3 204,57 − 48,34 = 249,33 €.

**En repère, les 18 % du programme** : 4,98 points à rendre.

| | 1 SMIC | 1,2 | 1,5 | 2 | 3 | 5 |
|---|---:|---:|---:|---:|---:|---:|
| Taux uniforme, brut inchangé | +91 | +109 | +136 | +182 | +262 | +406 |
| Taux uniforme, coût constant | +39 | +87 | +121 | +175 | +269 | +417 |
| Forfait de 177 €, brut inchangé | +177 | +177 | +177 | +177 | +167 | +129 |
| Forfait de 177 €, coût constant | +136 | +160 | +165 | +172 | +174 | +140 |
| Franchise de 1 933 € (1,06 SMIC), brut inchangé | +169 | +179 | +179 | +179 | +170 | +131 |
| Franchise de 1 933 €, coût constant | +124 | +162 | +168 | +174 | +176 | +142 |

Trois choses à lire dans ces tableaux.

- **Sous A, à coût constant, le salarié au SMIC perd 12 € par la baisse du
  taux** : la baisse de sa retenue (32 €) ne couvre pas ce que la part
  patronale du pilier reprend sur le brut. Comme les 39 €, ce chiffre
  suppose un brut sous le SMIC ; au lendemain de la réforme, c'est +32 €
  pour lui et +58 € pour son employeur.
- **Le forfait de B bute sur la fiche du SMIC.** Le salarié au SMIC ne verse
  pour la retraite que 206 € par mois (169,34 € de répartition et 36,85 € de
  pilier, calcul) : un forfait de 252 € dépasse toute sa retenue de
  retraite. Les 46 € qui manquent seraient un chèque, ou pris sur une autre
  ligne. Pour un mi-temps au SMIC (912 € brut, 103 € de retenue), 252 € font
  28 % du salaire brut : un forfait par tête paie le temps partiel.
- **La franchise de B n'est plus « le même montant »** : elle monte à
  1,76 SMIC, et le gain croît encore de 169 à 298 € entre 1 et 2 SMIC. Elle
  rend moins que le forfait au SMIC, plus que lui au-dessus de 1,5 SMIC.

Toute combinaison est possible : la moitié de la somme par le taux, la
moitié par le forfait, donne la moyenne des deux lignes.

## 4. Ce que devient la pension : le compte est-il crédité, et par qui ?

### Le point de départ : au SMIC, le compte est déjà crédité par l'impôt

Le modèle crédite le compte du taux plein sur tout le salaire, et compte en
recette « le taux plein sur l'assiette mesurée » (dépôt, `cout.py`), que la
réduction générale ait effacé ou non la part de l'employeur. Au SMIC, par
mois, pour la seule répartition (calcul, sur les fiches du modèle) :

| Au SMIC | Dû au barème, puis crédité au compte | Versé par le salarié | Versé par l'employeur | Effacé par la réduction générale |
|---|---:|---:|---:|---:|
| Aujourd'hui (au barème, 27,98 %) | 510 € | 206 € | 0 € | 304 €, 60 % |
| Programme, 18 % | 328 € | 90 € | 0 € | 238 €, 72 % |
| Lecture A, 21,2 % | 386 € | 141 € | 0 € | 246 €, 64 % |
| Lecture B, 15,9 % | 290 € | 59 € | 0 € | 231 €, 80 % |

Posé pour B : crédité 15,9 % × 1 823,03 = 289,86 € ; part de l'employeur
15,9 × 16,67 ÷ 20,9 = 12,68 %, soit 231,20 €, effacés ; part du salarié
289,86 − 231,20 = 58,66 €. La réponse à « le compte est-il crédité quand
même, et par qui » existe donc déjà pour les bas salaires : oui, et par la
fraction de TVA que la décision 79 garde aux retraites. À 1,5 SMIC, la
réduction efface encore 21 % (A) à 27 % (B) du crédit ; à 3 SMIC, rien.

### Les trois réponses possibles pour le forfait et la franchise

Le taux uniforme ne pose pas la question : le taux cotisé est le taux
crédité, pour tous (`2026-11-07-deux-lectures-au-modele.md`). Le forfait et
la franchise la posent, puisque chacun verse un taux différent selon son
salaire. Trois réponses.

**a. Non : le compte ne reçoit que ce qui est payé.** Le taux crédité
dépend alors du salaire (calcul : 22,98 % moins le gain rapporté au brut ;
au SMIC sous B, 418,93 − 251,58 = 167,35 €, soit 9,18 % de 1 823,03) :

| Taux crédité | 1 SMIC | 1,2 | 1,5 | 2 | 3 | 5 |
|---|---:|---:|---:|---:|---:|---:|
| A, taux uniforme | 21,2 % | 21,2 % | 21,2 % | 21,2 % | 21,2 % | 21,2 % |
| A, forfait ou franchise | 19,5 % | 20,1 % | 20,7 % | 21,2 % | 21,8 % | 22,3 % |
| B, taux uniforme | 15,9 % | 15,9 % | 15,9 % | 15,9 % | 15,9 % | 15,9 % |
| B, forfait | 9,2 % | 11,5 % | 13,8 % | 16,1 % | 18,4 % | 20,2 % |
| B, franchise | 13,7 % | 13,7 % | 13,7 % | 14,8 % | 17,5 % | 19,7 % |

Sous la franchise de B, les 13,7 % crédités au SMIC sont la seule part de
l'employeur, que la réduction générale efface : **ni le salarié ni
l'employeur ne versent plus rien à la répartition, et le compte n'est
crédité que par la TVA.** Sous le forfait de B, c'est pire d'un cran : le
forfait dépasse la part du salarié.

La pension des cas types de la grille du coût, simulée au scénario 6 sous
le taux crédité de chacun, en euros de 2026 par mois (calcul ; le forfait
et la franchise suivent le salaire moyen, le cas type garde son rang) :

| Né en 1990, départ en 2055 | Droit en vigueur | 18 % | A, taux uniforme | A, forfait | B, taux uniforme | B, forfait | B, franchise |
|---|---:|---:|---:|---:|---:|---:|---:|
| SMIC, carrière complète | 1 453 | 975 | 1 063 | 1 018 | 916 | 740 | 855 |
| Salaire moyen | 2 859 | 1 531 | 1 696 | 1 701 | 1 423 | 1 441 | 1 377 |
| Cadre du privé | 5 031 | 3 039 | 3 426 | 3 534 | 2 785 | 3 215 | 3 138 |

Sous le forfait de B, le salarié au SMIC né en 1990 touche 740 € : c'est le
plancher de la garantie vieillesse, que le modèle sert au même montant à
8,7 % et à 9,4 % de taux crédité. Né en 2005, il y tombe aussi (502 €,
contre 744 € par le taux uniforme, et 651 € par la franchise). Il gagne
123 € de net par mois de plus que par le taux uniforme (252 − 129), et sa
cotisation ne lui ouvre plus aucun droit au-dessus de ce que la garantie
lui aurait donné sans cotiser. Le cadre y gagne 430 € de pension par mois.
Sous A, l'écart est petit : 45 € de pension en moins au SMIC, 108 € en plus
pour le cadre.

Les comptes de la caisse sont ceux de la lecture, au premier ordre : elle
encaisse et crédite la même somme. Ce que ce calcul ne mesure pas : la
garantie vieillesse servie à plus de monde, que l'impôt paie.

**b. Oui, au taux plein de 22,98 %, et l'État paie le forfait.** La pension
ne baisse pour personne : 1 112 € au SMIC, 1 788 € au salaire moyen, 3 641 €
pour le cadre, nés en 1990 (calcul), plus que sous A et sous B. Le forfait
est alors une dépense du budget : 30,6 millions de personnes en emploi
(dépôt, emploi intérieur de 2024) × 63,25 € × 12 = **23,2 Md€ par an** sous
A ; × 251,58 € × 12 = **92,4 Md€** sous B (calcul, ordre de grandeur). Le
programme retire à la retraite les 58 Md€ que l'État lui verse (dépôt) :
sous B, l'État en reverserait davantage. Et la caisse n'est plus sous la
lecture A ni sous la lecture B : elle encaisse et crédite 22,98 %, et la
part rendue aux cotisants ne vient plus de la baisse des pensions, mais de
l'impôt.

**c. Oui, au taux de la lecture, et les autres cotisants paient.** Chaque
compte est crédité de 21,2 % ou de 15,9 %, comme par le taux uniforme : les
pensions et les comptes de la caisse sont exactement ceux de la lecture.
Seul le net change. Celui qui gagne plus que le salaire moyen verse alors
plus que ce qui lui est crédité ; celui qui gagne moins est crédité de plus
qu'il ne verse (calcul, par mois ; à cinq SMIC sous B : 7,08 % × 9 115,17 −
251,58 = 393,77 €) :

| Versé sans droit (+), crédité sans versement (−) | 1 SMIC | 1,2 | 1,5 | 2 | 3 | 5 |
|---|---:|---:|---:|---:|---:|---:|
| A, forfait | −31 | −24 | −15 | +2 | +34 | +99 |
| B, forfait | −123 | −97 | −58 | +7 | +136 | +394 |
| B, franchise | −40 | −48 | −60 | −40 | +90 | +348 |

En tout, pour le forfait, d'après la dispersion du dépôt, la part des
salaires qui dépasse la moyenne vaut 20,0 % de la masse : 1,78 × 0,200 = 0,36 point de
cotisation sans droit sous A, 7,08 × 0,200 = 1,42 point sous B, soit, sur
1 306 Md€ de salaires (30,6 millions × 42 641 €), **4,6 Md€ et 18,5 Md€ par
an** (calcul, ordre de grandeur). La cotisation déplafonnée d'aujourd'hui,
que le programme range au musée des horreurs, fait 17,9 Md€ sans droits en
2025 (dépôt).

## 5. Le conflit avec « Chaque pension vaut ce qui a été cotisé » (décision 90)

| | La phrase tient-elle ? | Ce qui casse |
|---|---|---|
| Taux uniforme | Oui, pour le salarié et son compte. | Au SMIC, 64 à 80 % de ce qui est crédité vient de la TVA : la phrase ne tient que si « cotisé » compte ce que l'impôt verse à la place de l'employeur. C'est déjà vrai aujourd'hui (60 %), et la décision 79 l'assume. |
| Forfait ou franchise, a : crédité du payé | Oui, à la lettre. | Le gain en salaire est repris sur la pension, d'abord aux bas salaires. Sous B, le salarié au SMIC cotise pour une pension égale au plancher : « chaque euro cotisé ouvre des droits » y devient faux, comme sous le minimum d'aujourd'hui. Le reproche change de camp : non plus « un cadeau aux cadres », mais « la retraite des smicards ». |
| b : crédité par l'État | Seulement si « cotisé » compte ce que l'État verse pour vous. | Le programme retire l'État de la retraite (58 Md€) ; il y reviendrait pour 23 ou 92 Md€. La baisse des pensions ne finance plus la part des cotisants. |
| c : crédité par les autres cotisants | Non. | La pension des uns vaut plus que ce qu'ils ont versé, celle des autres moins : des cotisations sans droits, 4,6 à 18,5 Md€, ce que le programme reproche au système actuel. C'est un impôt sur le revenu logé dans la cotisation. |

**Le précédent de 2014** (publié, décision n° 2014-698 DC du 6 août 2014,
considérant 13). Le législateur avait voté « une réduction dégressive des
cotisations salariales de sécurité sociale » entre 1 et 1,3 SMIC, « aux
fins d'augmenter le pouvoir d'achat des salariés dont la rémunération est
modeste », en gardant les droits inchangés. Le Conseil l'a censurée : « un
même régime de sécurité sociale continuerait […] à financer, pour
l'ensemble de ses assurés, les mêmes prestations malgré l'absence de
versement, par près d'un tiers de ceux-ci, de la totalité des cotisations
salariales ouvrant droit aux prestations servies par ce régime », d'où
« une différence de traitement, qui ne repose pas sur une différence de
situation entre les assurés d'un même régime de sécurité sociale »,
contraire au principe d'égalité. La réduction générale, elle, porte sur des cotisations
patronales. Ce que la session en comprend, à faire vérifier par un
juriste : les réponses b et c, qui gardent les droits en baissant la part
du salarié selon son salaire, sont du côté de ce qui a été censuré ; la
réponse a, où le droit suit le versement, n'y est pas ; un forfait
identique pour tous n'est pas une réduction réservée à quelques-uns, et la
question reste ouverte pour lui.

## Ce que ce calcul ne dit pas

- **Un seul statut** : le salarié du privé non cadre. Ni le fonctionnaire,
  ni l'indépendant, dont la fiche suit d'autres règles (`remuneration.py`,
  « quatre profils »). Le forfait par tête est pourtant calculé sur le
  salaire moyen de toute l'économie.
- **Les taux de A et de B** supposent la LVT centrale, sans abattement, et
  la seule part de TVA de l'Agirc-Arrco ; ils sont constants de 2026 à 2070.
- **La dispersion** est celle des salaires nets du privé à temps complet :
  sans le temps partiel, 17,7 % des personnes en emploi en 2025 (dépôt), qui
  étirerait le bas et relèverait la franchise de B.
- **Les pensions** supposent un cas type qui garde son rang toute sa
  carrière et un forfait qui suit le salaire moyen. Le coût agrégé n'a pas
  été refait : le modèle ne sait pas créditer un taux qui dépend du salaire.
- **Aucun comportement** : ni l'emploi au SMIC quand son coût monte de
  3,5 %, ni le temps partiel qu'un forfait par tête encourage.
- **La CSG rendue** par le partage des impôts affectés (`restitution.py`)
  n'est pas dans ces gains, comme dans le constat.
- **À vérifier par la session du modèle** : le coût compte déjà en recette
  le taux plein sur toute l'assiette, cotisations effacées par la réduction
  générale comprises ; la part de TVA que le script des lectures ajoute
  (0,23 point de PIB) pourrait y être comptée deux fois.

## La piste de la session

Une proposition, pas une décision. Les trois réponses à « qui crédite » ont
chacune un prix que le programme refuse ailleurs : la pension des bas
salaires (a), l'État de retour dans la retraite (b), des cotisations sans
droits (c). La baisse uniforme est la seule qui laisse le compte dire vrai.
D'où trois gestes, dans l'ordre :

1. **Garder le taux uniforme pour la retraite**, et dire les deux chiffres
   ensemble : ce que le salaire gagne, ce que le compte reçoit.
2. **Montrer au SMIC le chiffre du lendemain**, 91 € aux 18 %, et non les
   39 € d'une convention que le SMIC interdit ; et dire ce qu'il en coûte à
   l'employeur.
3. **Si le propriétaire veut les mêmes euros pour tous, les donner hors de
   la cotisation de retraite**, par une des « petites baisses » de la
   décision 89, sur un prélèvement qui n'ouvre aucun droit : le compte n'est
   pas touché, et la question « qui crédite » ne se pose pas. Laquelle, et
   payée par quoi, reste à étudier ; le précédent de 2014 vaut aussi pour
   elle.

Et une question qui vise le SMIC plus droit que les trois façons : la part
patronale du pilier. Placée par la loi de la réforme dans le périmètre de
la réduction générale (l'article L. 241-13 vise les régimes complémentaires
obligatoires « ou créés par la loi »), elle ne coûterait plus rien à
l'employeur au SMIC : le gain y serait de 91 € dans les deux conventions,
au prix de 66 € par mois et par salarié au SMIC pour la TVA, dégressifs
jusqu'à 3 SMIC (calcul, aux 18 %).

## Ce que le propriétaire tranche

Ni A ni B : les deux restent ouvertes, et chaque question vaut sous l'une
comme sous l'autre.

1. **Le but.** Le même taux pour tous, et un gain qui croît avec le
   salaire ; ou les mêmes euros pour tous. Sous A, il y a 63 € par tête à
   partager ; sous B, 252 €.
2. **Si ce sont les mêmes euros : qui crédite le compte.** Personne, et la
   pension du salarié au SMIC tombe au plancher sous B (a) ; l'État, 23 à
   92 Md€ par an (b) ; les autres cotisants, par 4,6 à 18,5 Md€ de
   cotisations sans droits (c) ; ou les euros se donnent hors de la retraite
   (la piste).
3. **Forfait par tête ou franchise.** Le forfait paie le temps partiel et
   dépasse la retenue du SMIC sous B ; la franchise suit le salaire sous le
   seuil, et sous B elle monte à 1,76 SMIC.
4. **La part patronale du pilier** : dans la réduction générale, payée par
   la TVA, ou hors d'elle, payée par l'employeur du SMIC.
5. **Le chiffre du message au SMIC** : 91 € au lendemain, ou 39 € à coût
   constant, que le SMIC interdit.
6. **La phrase de la décision 90 au SMIC.** « Cotisé » compte-t-il ce que
   la TVA verse à la place de l'employeur ? Aujourd'hui 60 % de la
   cotisation d'un salarié au SMIC, demain 64 à 80 % de ce que son compte
   reçoit.
7. **Le droit** : faire relire par un juriste la décision de 2014 avant
   toute baisse de la part salariale qui ne serait pas la même pour tous.
