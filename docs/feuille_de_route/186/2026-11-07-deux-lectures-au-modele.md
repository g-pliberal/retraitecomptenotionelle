# Les deux lectures de la décision 29, refaites au modèle

*Le 7 novembre 2026, action 186, chantier 1. Le premier chiffrage des deux
lectures (`2026-11-07-deux-lectures-et-reprise.md`) changeait les cotisations
sans changer les pensions qu'elles ouvrent. Le propriétaire l'a vu : « il n'y
a que des avantages à la lecture B, on ne peut pas avoir que des avantages ».
Cette note refait le calcul au modèle : le taux cotisé est le taux crédité aux
comptes, et la dépense suit. Les chiffres sont ceux de `main` au commit
`553e8ca`, qui garde les réversions servies à la bascule (décision 16). Le
choix entre A et B reste au propriétaire.*

*Corrigé le même jour : les chiffres de cette note gardent à la retraite les
impôts affectés et les versements de l'État, que le programme lui retire ;
la page Coût les lui retire. Sur sa base, les taux sont bien plus hauts. Voir
la dernière partie.*

## En bref

En compte notionnel, ce qui est payé ouvre des droits, rien de plus, rien de
moins. Un point de cotisation rendu aux actifs aujourd'hui, c'est donc un
point de pension en moins pour eux demain. Rendre beaucoup, comme le fait la
lecture B, c'est surtout avancer aux actifs une partie de leur propre
retraite.

Chaque lecture a un seul taux, de 2026 à 2070, cotisé et crédité aux comptes.
Le programme prévoit 18 %. Le salarié pris en exemple est au salaire moyen :
3 732 € brut par mois en 2026 pour celui né en 1990.

| | Tout au déficit | Lecture A | Lecture B |
|---|---:|---:|---:|
| Taux cotisé et crédité | 20,3 % | 14,5 % | 8,4 % |
| Retraités d'aujourd'hui | −104 Md€ en 2026 | pareil | pareil |
| Salarié né en 1990 : son net chaque mois, par rapport aux 18 % | −84 € | +132 € | +357 € |
| Sa pension en 2055, par rapport aux 18 % | +8 % | −12 % | −32 % |
| Né en 2005 : sa pension en 2070, par rapport aux 18 % | +12 % | −20 % | −53 % |
| Solde de la retraite en 2026, en points de PIB (aujourd'hui : −0,16) | +2,7 | +0,2 | −2,3 |
| Dette de la retraite en 2070, en points de PIB (droit en vigueur : +66) | réserve de 210 | réserve de 80 | dette de 55 |
| Ce que l'État verse encore en 2026 | 58 Md€ | 58 Md€ | 58 Md€ |

Compté sans les versements de l'État, le déficit à diviser par deux est plus
grand : la lecture B prend alors un taux de 11,2 %, entre A et B.

## Avantages et inconvénients, lecture par lecture

### Ce qui est commun aux trois

Les retraités d'aujourd'hui perdent la même chose dans les trois : 104 Md€ en
2026, près du quart de la dépense de retraite, réversions servies gardées. La
dépense de 2026 ne dépend pas du taux, puisque personne n'a encore cotisé au
nouveau taux. Les lectures ne se séparent que sur ce que l'on fait de cette
économie, et sur la pension de ceux qui travaillent.

Les trois gardent les recettes du droit en vigueur, sauf les cotisations : les
impôts affectés restent, et l'État verse encore sa contribution et ses
subventions d'équilibre, 58 Md€ en 2026 et 146 Md€ en 2070.

### Tout au déficit, 20,3 %

- **Avantages.** Les comptes se redressent tout de suite : la retraite passe
  de −0,16 à +2,7 points de PIB en 2026. Les actifs paient environ ce que le
  système prélève en moyenne aujourd'hui, et leur pension monte un peu
  au-dessus de celle des 18 % (+8 % pour le salarié né en 1990).
- **Inconvénients.** Les actifs ne gagnent rien sur leur salaire : 84 € de
  moins par mois que sous les 18 % du programme. La réserve devient
  démesurée : 210 points de PIB en 2070, près de deux fois la dette publique
  de 2025 (116 %). Personne ne garderait une telle règle quarante ans.
- **Devant les juges** (à faire vérifier par un juriste) : toute la baisse
  des pensions sert à redresser les comptes, le motif d'intérêt général est
  le plus net ; mais une réserve qui dépasse de loin le besoin peut faire
  juger la baisse plus forte que nécessaire.

### Lecture A, 14,5 %

- **Avantages.** Les actifs gagnent tout de suite : 132 € de plus par mois
  pour le salarié né en 1990, par rapport aux 18 %. Les comptes restent en
  excédent chaque année, et la réserve atteint 80 points de PIB en 2070, plus
  des deux tiers de la dette publique de 2025.
- **Inconvénients.** L'excédent est mince pendant quinze ans : +0,2 point
  en 2026, +0,7 en 2040. La pension des actifs baisse : −12 % pour le
  salarié né en 1990, −20 % pour celui né en 2005, par rapport aux 18 %.
  Avec un taux fixe, la règle ne tient qu'en moyenne : la première année,
  la lecture A rend aux actifs 88 % de l'économie, pas la moitié ; en 2070,
  28 %.
- **Devant les juges** (à faire vérifier par un juriste) : la retraite passe
  en excédent, l'urgence se plaide ; le juge pourra demander pourquoi la
  moitié rendue aux actifs n'a pas plutôt allégé la baisse des pensions.

### Lecture B, 8,4 %

- **Avantages.** Les actifs gagnent beaucoup tout de suite : 357 € de plus
  par mois pour le salarié né en 1990, par rapport aux 18 %. La dette de la
  retraite en 2070 (55 points) reste sous celle du droit en vigueur
  (66 points).
- **Inconvénients.** Le déficit de la retraite se creuse au lieu de baisser :
  −2,3 points de PIB en 2026, quinze fois celui d'aujourd'hui, et un déficit
  chaque année jusqu'en 2056 ; la dette culmine à 62 points en 2062. Les
  actifs reçoivent plus que ce que perdent les retraités (1,6 fois en
  2026) : la différence est empruntée. Leur pension
  s'effondre : −32 % pour le salarié né en 1990, −53 % pour celui né en 2005,
  par rapport aux 18 %. Et la règle ne s'arrête pas d'elle-même : chaque
  point rendu baisse les pensions futures, donc grossit l'« économie », donc
  ce qu'il faut rendre. Tenue chaque année et non en moyenne, elle
  demanderait en 2070 de rendre toutes les cotisations.
- **Devant les juges** (à faire vérifier par un juriste) : baisser les
  pensions en cours pendant que le déficit grossit trente ans, pour baisser
  des cotisations rend l'argument d'urgence de la décision 6 très difficile
  à tenir.

### Lecture B, le déficit compté sans les versements de l'État, 11,2 %

Le déficit à diviser est plus grand (−2,05 points de PIB en 2026 au lieu de
−0,16), donc il reste moins à rendre. Le salarié né en 1990 gagne 253 € par
mois, et sa pension baisse de 23 % par rapport aux 18 % ; celui né en 2005,
de 38 %. Le déficit se creuse encore, chaque année jusqu'en 2049 (−1,1 point en
2026), puis la retraite finit en léger excédent (réserve de 7 points en
2070). Les inconvénients de B s'y retrouvent, moins forts.

## La méthode

- **Les recettes** sont celles du droit en vigueur, impôts affectés et
  versements de l'État compris, comme au premier chiffrage, sauf les
  cotisations. Le droit en vigueur prélève 21,4 % de l'assiette de la
  proposition en 2026, 19,7 % en 2070 ; la variante prélève son taux sur la
  même assiette. Ce qui est rendu aux cotisants est l'écart des deux.
- **La dépense** est celle du scénario 6 calculée par le modèle sous ce taux
  (`Parametres.taux_cotisation_liberal`, au portage), pensions et garantie
  vieillesse nette des reprises sur succession. L'économie est la dépense du
  droit en vigueur moins celle-là. Elle dépend du taux : un taux plus bas
  fait des pensions futures plus basses, donc une économie plus grande. Le
  taux de chaque lecture est un point fixe.
- **Un taux constant de 2026 à 2070**, trouvé pour que la règle tienne en
  moyenne simple des parts de PIB sur ces années, la convention du solde
  moyen du dépôt. Le modèle ne sait pas faire varier le taux d'une année à
  l'autre. Année par année, la règle ne tient donc pas. Tenue la seule année
  2026, elle donnerait 17,5 % (A), 13,7 % (B) et 15,9 % (B hors versements de
  l'État) ; tenue la seule année 2040, 16,1 %, 12,0 % et 14,3 %. Une règle
  tenue chaque année demanderait un taux qui baisse avec le temps, que le
  modèle ne sait pas encore calculer.
- **Le déficit de la lecture B** est celui du COR, versements de l'État
  compris ; la variante « hors versements de l'État » divise par deux le
  déficit compté sans eux (−2,05 points en 2026), ces versements restant
  encaissés.
- **La dette** refait la récurrence de `calculer_dette` (`cout.py`), avec la
  croissance et le taux de chaque année du coût, à partir de zéro fin 2025 :
  elle retrouve les 66,0 points de 2070 du droit en vigueur.
- **Les cas types** sont simulés au scénario 6 sous chaque taux ; le portage
  et le jumeau Python donnent la même pension (vérifié sur le salarié au
  salaire moyen né en 1990, à 18 % et à 13,97 %).

Le calcul est versé : `python scripts/lectures_decision_29.py --cas-types`
le refait en quelques minutes, et ses règles sont tenues par
`tests/test_lectures_decision_29.py`, sur un cas posé à la main.

## Les chiffres

Au commit `553e8ca` de `main`. Soldes et dette en points de PIB.

| | Tout au déficit | A | B | B hors État | 18 % | Droit en vigueur |
|---|---:|---:|---:|---:|---:|---:|
| Taux cotisé et crédité | 20,25 % | 14,45 % | 8,43 % | 11,23 % | 18 % | 21,44 % en 2026 |
| Solde 2026 | +2,71 | +0,24 | −2,34 | −1,14 | +1,75 | −0,16 |
| Solde 2040 | +2,91 | +0,66 | −1,68 | −0,60 | +2,04 | −0,61 |
| Solde 2070 | +4,28 | +3,40 | +2,46 | +2,90 | +3,94 | −2,39 |
| Solde moyen 2026-2070 | +3,22 | +1,36 | −0,57 | +0,33 | +2,50 | −1,13 |
| Dette 2030 | −15,3 | −2,7 | +10,3 | +4,3 | −10,4 | |
| Dette 2050 | −89,9 | −20,7 | +51,2 | +17,8 | −63,1 | |
| Dette 2070 (négative : une réserve) | −209,8 | −79,7 | +55,5 | −7,4 | −159,4 | +66,0 |
| Rendu en 2026, Md€ et points de cotisation | 16, 1,2 | 92, 7,0 | 170, 13,0 | 134, 10,2 | 45, 3,4 | |
| Rendu en 2070, Md€ et points de cotisation | −20, −0,6 | 188, 5,2 | 405, 11,3 | 304, 8,5 | 61, 1,7 | |
| Rendu cumulé 2026-2070, Md€ courants | −144 | 6 029 | 12 435 | 9 456 | 2 251 | |

Ce qui est rendu, rapporté à l'économie, année par année :

| | 2026 | 2030 | 2040 | 2050 | 2060 | 2070 |
|---|---:|---:|---:|---:|---:|---:|
| Économie (A), points de PIB | 3,38 | 3,69 | 3,86 | 4,67 | 6,18 | 8,04 |
| Lecture A : rendu / économie | 0,88 | 0,77 | 0,67 | 0,51 | 0,37 | 0,28 |
| Lecture B : rendu / économie | 1,64 | 1,47 | 1,26 | 0,94 | 0,66 | 0,50 |
| Lecture B : solde | −2,34 | −1,93 | −1,68 | −0,88 | +0,70 | +2,46 |
| Lecture B : dette | +2,3 | +10,3 | +31,0 | +51,2 | +61,2 | +55,5 |

La pension des cas types, en euros de 2026 par mois, et son écart à celle des
18 % :

| Cas type | Départ | Droit en vigueur | 18 % | Tout au déficit | A | B | B hors État |
|---|---:|---:|---:|---:|---:|---:|---:|
| SMIC, carrière complète, né en 1975 | 2040 | 1 334 | 1 125 | 1 155 (+3 %) | 1 077 (−4 %) | 996 (−11 %) | 1 034 (−8 %) |
| SMIC, carrière complète, né en 1990 | 2055 | 1 453 | 975 | 1 037 (+6 %) | 876 (−10 %) | 740 (−24 %) | 787 (−19 %) |
| SMIC, carrière complète, né en 2005 | 2070 | 1 572 | 832 | 927 (+11 %) | 683 (−18 %) | 502 (−40 %) | 547 (−34 %) |
| Salaire moyen, né en 1975 | 2040 | 2 646 | 1 766 | 1 823 (+3 %) | 1 676 (−5 %) | 1 524 (−14 %) | 1 595 (−10 %) |
| Salaire moyen, né en 1990 | 2055 | 2 859 | 1 531 | 1 647 (+8 %) | 1 348 (−12 %) | 1 038 (−32 %) | 1 182 (−23 %) |
| Salaire moyen, né en 2005 | 2070 | 3 099 | 1 347 | 1 515 (+12 %) | 1 081 (−20 %) | 631 (−53 %) | 840 (−38 %) |
| Cadre du privé, né en 1975 | 2041 | 4 767 | 3 435 | 3 583 (+4 %) | 3 201 (−7 %) | 2 806 (−18 %) | 2 990 (−13 %) |
| Cadre du privé, né en 1990 | 2056 | 5 031 | 3 039 | 3 311 (+9 %) | 2 610 (−14 %) | 1 882 (−38 %) | 2 220 (−27 %) |
| Cadre du privé, né en 2005 | 2071 | 5 326 | 2 850 | 3 206 (+12 %) | 2 288 (−20 %) | 1 335 (−53 %) | 1 778 (−38 %) |

Plus on est jeune, plus le taux pèse : celui qui part en 2040 a cotisé l'essentiel
de sa carrière avant la bascule, celui qui part en 2070 presque toute après.
Au salaire moyen, le scénario 6 sert déjà, à 18 %, bien moins que le droit en
vigueur aux générations jeunes (1 531 € contre 2 859 € pour celui né en
1990) ; ce n'est pas l'objet de cette note, mais chaque lecture part de là.
Au SMIC, né en 2005, la lecture B tombe sur le plancher de la garantie
vieillesse (502 €).

## Ce que la correction change, et ce qui déplace encore ces chiffres

- **Par rapport au premier chiffrage.** La première année, rien ne change :
  la dépense de 2026 ne dépend pas du taux. Mais un taux fixé en 2026 vaut
  pour des décennies, et il baisse les pensions de ceux qui le cotisent. La
  lecture B, qui semblait garder le déficit à −0,08 point en 2026 et une
  dette de 33 points en 2070, le creuse à −2,3 points et finit à 55 points.
- **La décision 16**, portée au scénario 6 par `553e8ca` : les réversions
  servies à la bascule sont gardées, 1,41 point de PIB en 2026. L'économie de
  2026 tombe de 4,79 à 3,38 points, et chaque taux remonte. Au commit
  `e4f308a`, sans elle, les taux étaient de 20,25 % (tout au déficit),
  13,97 % (A), 7,30 % (B) et 10,09 % (B hors versements de l'État).
- **Les autres décisions de la réversion** (17 à 28), que la session du
  modèle porte : la rente sur deux têtes est payée par le couple, mais la
  pension du conjoint d'un actif mort (décision 22) et la garantie servie
  d'office (décision 20) coûteront, et réduiront encore l'économie.
- **La convergence en cinq ans** (décision 3) : le modèle bascule d'un coup
  en 2026.
- **Le pilier capitalisé** n'est pas compté. La règle du 20 septembre (la
  part patronale ne bouge pas, toute la baisse va au salarié) suppose que
  l'employeur paie encore ses 16,67 points : avec les cinq points du pilier,
  le taux total vaut 19,5 % sous A, 16,2 % sous B hors versements de l'État
  et 13,4 % sous B ; seule A la respecte. Sous B, la part patronale baisse
  aussi, et l'action 56 a montré qu'une baisse patronale va d'abord à
  l'employeur.
- **Ni comportement, ni recettes du chantier 4** (TVA, LVT).
- **La réserve** d'« tout au déficit » et de A pourrait aussi revenir à
  l'État, en baissant ses versements : c'est un choix à faire, pas un calcul.

## Corrigé le même jour : la page Coût ne compte pas les mêmes recettes

Le propriétaire, devant les chiffres : « tu pourrais faire des courbes ?
c'est un peu bizarre, ce n'est pas la simulation qui est déjà présente sur le
site dans la page coût ; j'ai l'impression qu'on fait une connerie ». Il avait
raison. Le calcul ci-dessus suit le premier chiffrage sur un point qu'il
fallait mettre en avant : **la retraite y garde toutes les recettes du droit
en vigueur, sauf ses cotisations.** La page Coût, comme le programme depuis
le 19 septembre, lui retire les impôts affectés, les versements de l'État et
les transferts pour les droits non contributifs. En 2026, au taux du
programme :

| En 2026, au taux de 18 % | Md€ |
|---|---:|
| Solde de la retraite, recettes gardées (le calcul ci-dessus) | +54 |
| Impôts affectés (CSG, taxes) que la retraite ne reçoit plus | −66 |
| Contribution d'équilibre que l'État ne verse plus | −50 |
| Subventions d'équilibre que l'État ne verse plus | −8 |
| Transferts pour les droits non contributifs (CNAF, FSV) | −11 |
| Garantie vieillesse, que la page Coût compte à part | +14 |
| Solde de la page Coût | −67 |

Les pensions et la méthode ne sont pas en cause : sur la base de la page
Coût, le calcul retrouve sa courbe à 18 % (solde de −2,19 points de PIB en
2026, dette de 102,8 points en 2070). Ce sont les recettes. Et elles se
comptent de trois façons, selon le déficit dont parle la décision 29 :

| Le déficit | Tout au déficit | Lecture A | Lecture B | B, hors versements de l'État |
|---|---:|---:|---:|---:|
| Celui de la caisse de retraite, comme la page Coût | 30,0 % | 25,3 % | 20,8 % | 17,9 % |
| La retraite et l'État ensemble, impôts affectés supprimés | 25,0 % | 19,9 % | 14,8 % | 17,6 % |
| La retraite et l'État ensemble, impôts affectés gardés (le calcul ci-dessus) | 20,3 % | 14,5 % | 8,4 % | 11,2 % |

Compter la retraite et l'État ensemble a un sens : sur les 135 Md€, les
58 Md€ que l'État cesse de verser restent dans son budget, et les 11 Md€ des
transferts, à la CNAF et au fonds de solidarité vieillesse. Les 66 Md€
d'impôts affectés, le programme ne dit pas s'ils sont supprimés, une baisse
d'impôt, ou gardés par l'État.

**Sur la base de la page Coût, tout s'inverse.** Le programme à 18 % y creuse
déjà le déficit : −2,2 points de PIB en 2026, contre −0,16 aujourd'hui. La
décision 29 y demande de cotiser plus que 18 %, et la pension des actifs
monte. Le salarié au salaire moyen, comme plus haut :

| Sur la base de la page Coût | Tout au déficit | Lecture A | Lecture B |
|---|---:|---:|---:|
| Taux cotisé et crédité | 30,0 % | 25,3 % | 20,8 % |
| Né en 1990 : son net chaque mois, par rapport aux 18 % | −447 € | −273 € | −103 € |
| Sa pension en 2055, par rapport aux 18 % | +40 % | +25 % | +9 % |
| Né en 2005 : sa pension en 2070, par rapport aux 18 % | +67 % | +41 % | +15 % |
| Solde de la caisse en 2026 (aujourd'hui : −0,16 ; à 18 % : −2,2) | +2,9 | +0,9 | −1,0 |
| Dette de la caisse en 2070 (droit en vigueur : +66 ; à 18 % : +103) | réserve de 164 | réserve de 60 | dette de 41 |

Les 18 % du programme y correspondent à peu près à la lecture B, le déficit
compté sans les versements de l'État que la caisse ne reçoit plus (17,9 %).
Un salarié du privé paie aujourd'hui 27,98 %, parts salariale et patronale
additionnées (`Parametres.part_salariale_taux_unique`) : la lecture A le laisse
un peu en dessous, « tout au déficit » au-dessus, sans compter les cinq
points du pilier.

Ce que le propriétaire tranche, avant A ou B : **de quel déficit parle la
décision 29**, celui de la caisse de retraite ou celui de la retraite et de
l'État ensemble ; **et le sort des impôts affectés**, supprimés ou gardés par
l'État. Le reste de la note, ses avantages et inconvénients compris, ne vaut
que pour la dernière ligne du tableau des taux.

Le script compte désormais les trois façons
(`python scripts/lectures_decision_29.py`, `--convention`), tenues par
`tests/test_lectures_decision_29.py`. Les courbes montrées au propriétaire
(solde, dette, pension selon le taux, sous les deux bases extrêmes) en sortent ;
elles sont restées hors du dépôt.

## Les deux lectures, sur la base de la page Coût

Le propriétaire : « cela ne règle toujours pas nos problèmes, on change de
sujet, on peut revenir au sujet initial avec des bons chiffres ? » Les voici,
sur la base de la page Coût, celle de la simulation du site, que le calcul
retrouve à 18 %. Deux choses y sont communes aux quatre colonnes et ne les
départagent pas : l'État garde les 58 Md€ (2026) qu'il ne verse plus à la
retraite, et les 66 Md€ d'impôts affectés suivent le partage du 20 septembre,
la moitié rendue aux salaires, la moitié à la dette (`restitution.py`). La
question « de quel déficit » posée plus haut est donc réglée : c'est celui de
la caisse, comme sur la page.

Le salarié est au salaire moyen ; ce qu'il paie se compare à aujourd'hui,
27,98 % pour un salarié du privé, pilier de cinq points compris, la part
patronale ne bougeant pas (règle du 20 septembre).

| | Programme, 18 % | Tout au déficit | Lecture A | Lecture B |
|---|---:|---:|---:|---:|
| Taux cotisé et crédité | 18 % | 30,0 % | 25,3 % | 20,8 % |
| Retraités d'aujourd'hui, en 2026 | −118 Md€ | pareil | pareil | pareil |
| Né en 1990 : son net par mois, par rapport à aujourd'hui | +186 € | −261 € | −87 € | +83 € |
| Né en 1990 : sa pension en 2055 (droit en vigueur : 2 859 €) | 1 531 € | 2 149 € | 1 908 € | 1 674 € |
| Né en 2005 : sa pension en 2070 (droit en vigueur : 3 099 €) | 1 347 € | 2 243 € | 1 894 € | 1 553 € |
| Solde de la caisse en 2026, points de PIB (aujourd'hui : −0,16) | −2,2 | +2,9 | +0,9 | −1,0 |
| Années de déficit | 2026 à 2069 | aucune | aucune | 2026 à 2064 |
| Dette de la caisse en 2070, points de PIB (droit en vigueur : 66) | 103 | réserve de 164 | réserve de 60 | 41 |

**Le programme à 18 %** est ce que montre la page Coût : les actifs paient
cinq points de moins qu'aujourd'hui, mais la caisse est en déficit chaque
année jusqu'en 2069, plus qu'aujourd'hui, et finit avec plus de dette que le
droit en vigueur. L'économie sur les pensions est rendue tout entière, et
au-delà : par les impôts affectés, l'argent de l'État, et la baisse des
cotisations. C'est ce que la décision 29 refuse.

**Tout au déficit**, écarté par la décision 29, reste en référence : les
actifs paient sept points de plus qu'aujourd'hui, et la caisse accumule une
réserve démesurée.

**Lecture A, 25,3 %.**
- *Avantages.* La caisse est en excédent dès 2026 et chaque année ; la
  réserve atteint 60 points de PIB en 2070. Les actifs se constituent une
  pension plus haute : +25 % pour le salarié né en 1990, +41 % pour celui né
  en 2005, par rapport aux 18 %. En compte notionnel, ce qu'ils cotisent de
  plus leur revient.
- *Inconvénients.* Les actifs paient plus qu'aujourd'hui : 87 € de moins par
  mois pour le salarié né en 1990, au lieu de 186 € de plus sous le
  programme. Le message « le parti des cotisants » s'en trouve affaibli.
- *Devant les juges* (à faire vérifier par un juriste) : la caisse passe en
  excédent tout de suite, l'urgence se plaide ; mais le juge pourra demander
  pourquoi on baisse les pensions quand on pouvait moins relever les
  cotisations.

**Lecture B, 20,8 %.**
- *Avantages.* Les actifs paient un peu moins qu'aujourd'hui (83 € de plus
  par mois pour le salarié né en 1990) et leur pension monte un peu par
  rapport aux 18 % (+9 %, +15 % pour celui né en 2005). La dette de la caisse
  en 2070 (41 points) reste sous celle du droit en vigueur (66) et du
  programme (103).
- *Inconvénients.* La caisse reste en déficit jusqu'en 2064 : −1,0 point de
  PIB en 2026, six fois celui d'aujourd'hui. Le déficit est divisé par deux en
  moyenne sur 45 ans, pas chaque année.
- *Devant les juges* (à faire vérifier par un juriste) : baisser les pensions
  pendant que la caisse reste en déficit près de quarante ans rend l'argument
  d'urgence de la décision 6 difficile à tenir.

Dans les quatre colonnes, la pension des générations jeunes reste bien sous
celle du droit en vigueur : −33 % sous A, −41 % sous B pour le salarié né en
1990. Le taux est constant de 2026 à 2070, la règle tenue en moyenne. Au
commit `4a68fc7` ; `python scripts/lectures_decision_29.py --cas-types`, la
page Coût étant sa convention par défaut.

**La taxe sur la valeur du terrain change l'ordre.** La décision 80, prise le
même soir, donne aux retraites un point de LVT, 1,2 à 1,4 point de PIB par
an avant tout abattement (`2026-11-07-recettes-tva-lvt.md`) ; elle n'est pas
au modèle. Comptée à 1,3 point de PIB chaque année, à côté du modèle, elle
baisse chaque taux de trois à quatre points : tout au déficit 27,0 %,
lecture A 21,8 %, lecture B 16,7 %. Les 18 % du programme tombent alors entre
A et B : la caisse y perd encore 0,9 point de PIB en 2026, mais son solde
moyen (−0,14) est meilleur que celui de B (−0,57), et sa dette de 2070 tombe
à 17 points. B, sous 18 %, reste en déficit jusqu'en 2059. L'abattement, le
plafonnement et l'année de la LVT restent à fixer, et déplaceront ces taux.

