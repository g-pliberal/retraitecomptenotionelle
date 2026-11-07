# La baisse des pensions, entre le déficit et les cotisants ; la reprise de la garantie gardée

*Le 7 novembre 2026, le propriétaire répond sur les chantiers 1 et 2 de
l'action 186. Au premier : « Je ne suis pas d'accord, on baisse seulement de
moitié le déficit. C'est ce qu'on avait dit il y a longtemps, je maintiens ce
que j'avais dit il y a longtemps. » Au second : « La reprise sur succession
n'est pas illogique. On reprend seulement sur la valeur de l'aide, pas sur
autre chose. » Ce sont les décisions 29 et 30 de
`docs/feuille_de_route_programme.md`. La première se lisant de deux façons, la
session lui a demandé laquelle ; il a répondu « donne les chiffrages, j'ai
besoin de plus de recul ». Cette note les donne.*

## Ce qui avait été dit « il y a longtemps »

Le 20 septembre 2026, à l'action 59 (archivée) : « Il ne faut pas que ces
baisses d'impôts servent uniquement à combler le déficit. Il faut aussi que
les salaires soient augmentés. » Le partage retenu, pour les impôts que la
proposition n'encaisse plus : la moitié rendue aux salaires, la moitié qui
éteint de la dette (`Parametres.part_rendue_aux_salaires`, `restitution.py`).
La décision 29 porte le même principe à la baisse des pensions. Elle se lit
de deux façons :

- **Lecture A**, le partage du 20 septembre : la moitié de ce que la baisse
  des pensions économise va au déficit, l'autre moitié aux cotisants ;
- **Lecture B**, la lettre de la phrase : le déficit est diminué de moitié,
  sans être effacé, et tout le reste de l'économie va aux cotisants.

## Le calcul

Hors du modèle, sur ses séries, sous les réglages de la page Coût, au commit
`697d1b7`. Pour chaque année de 2026 à 2070, en points de PIB :

- l'économie `S` est la dépense du droit en vigueur (`Solde.depense("actuel")`)
  moins celle de la variante rétroactive, pensions et garantie nette des
  reprises (`Chiffrage.depense`, `scripts/chiffrage_plf.py`) : 4,79 points
  en 2026, 4,16 en 2040, 7,06 en 2070 ;
- le déficit `D` est le solde du droit en vigueur (`Chiffrage.solde_actuel`,
  la colonne « Rappel sc. 1 » du tableau A de `docs/chiffrage_plf.md`) :
  −0,16 en 2026, −0,61 en 2040, −2,39 en 2070 ;
- les recettes restent celles du droit en vigueur : le solde vaut `D` plus ce
  qui va au déficit, et le reste de `S` est rendu aux cotisants ;
- tout au déficit : `D + S` ; lecture A : `D + S/2`, `S/2` rendu ;
  lecture B : `D/2`, `S + D/2` rendu ;
- la dette refait la récurrence de `calculer_dette` (`cout.py`), avec la
  croissance et le taux de chaque année du coût ; elle retrouve les 66,05
  points de 2070 du droit en vigueur ;
- les points de cotisation divisent le rendu par l'assiette de la
  proposition, ses cotisations divisées par 18 % : 42,7 points de PIB en
  2026. Le droit en vigueur y prélève 21,4 % en 2026, 19,7 % en 2070.

Les deux scripts sont restés dans le brouillon de la session, hors du dépôt.

## Les chiffres

Soldes et dette en points de PIB, rendu en milliards d'euros courants et en
points de cotisation.

| Année | Économie | Déficit actuel | Tout au déficit | A : solde | A : rendu | B : solde | B : rendu |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026 | 4,79 | −0,16 | +4,63 | +2,23 | 73 Md€, 5,6 pts | −0,08 | 144 Md€, 11,0 pts |
| 2030 | 4,73 | −0,20 | +4,53 | +2,17 | 81 Md€, 5,5 pts | −0,10 | 159 Md€, 10,7 pts |
| 2040 | 4,16 | −0,61 | +3,55 | +1,47 | 94 Md€, 4,8 pts | −0,30 | 173 Md€, 9,0 pts |
| 2050 | 4,43 | −1,22 | +3,21 | +0,99 | 124 Md€, 5,1 pts | −0,61 | 215 Md€, 8,9 pts |
| 2060 | 5,50 | −1,77 | +3,73 | +0,98 | 189 Md€, 6,4 pts | −0,88 | 318 Md€, 10,7 pts |
| 2070 | 7,06 | −2,39 | +4,67 | +1,14 | 295 Md€, 8,2 pts | −1,19 | 490 Md€, 13,6 pts |

| Sur 2026-2070 | Droit en vigueur | Tout au déficit | Lecture A | Lecture B |
|---|---:|---:|---:|---:|
| Solde moyen | −1,13 | +3,83 | +1,35 | −0,57 |
| Dette en 2030 | +1,0 | −23,6 | −11,3 | +0,5 |
| Dette en 2070 (négative : une réserve) | +66,0 | −255,8 | −94,9 | +33,0 |
| Rendu moyen, en points de cotisation | 0 | 0 | 5,8 | 10,2 |
| Rendu cumulé, Md€ courants | 0 | 0 | 6 366 | 11 084 |

Le scénario 6 tel que le dépôt le chiffre, garantie comprise : solde de
−1,24 en 2026, −0,12 en 2070, −1,32 en moyenne, dette de 91 points en 2070
(74 sans la garantie, le chiffre du § F). Il retire 5,87 points de recettes en
2026 contre 4,79 d'économie : il rend aux cotisants et aux payeurs publics
plus que l'économie, et n'est ni A ni B.

## Corrigé le même jour : ce que le calcul oublie

Le propriétaire, à la lecture : « j'ai du mal à comprendre. Il n'y a que des
avantages à la lecture B, on ne peut pas avoir que des avantages. Il faut
aussi des inconvénients. Il y a un souci, non ? » Il y en a trois.

- **Le calcul est faux sur un point de méthode.** Il change les cotisations
  sans changer les pensions qu'elles ouvrent : la dépense reste celle du
  scénario 6, qui crédite aux comptes 18 % à compter de la bascule
  (`Parametres.taux_cotisation_liberal`). Or, en compte notionnel, la
  cotisation d'aujourd'hui est la pension de demain. Sous la lecture B, un
  taux vers 10 % baisse presque de moitié la part de pension que les actifs
  acquièrent après 2026 ; ou bien les comptes gardent 18 %, et ce sont des
  droits que personne n'a payés, une dette que la ligne « dette en 2070 »
  ne compte pas. Les 144 Md€ « rendus » sont en bonne partie une avance sur
  la retraite de ceux qui les reçoivent. Sous la lecture A et « tout au
  déficit », l'erreur va dans l'autre sens : 21,4 % prélevés pour 18 %
  crédités, des cotisations sans droits, ce qui contredit « chaque euro
  cotisé ouvre des droits », et gonfle la réserve.
- **Le coût commun ne se voyait pas.** Les trois colonnes baissent les
  pensions servies d'un tiers, 147 Md€ en 2026 ; le tableau ne montrait que
  ce qui les sépare.
- **La lecture B ne répare presque pas les comptes.** Le déficit de la
  retraite passe de 5 à 2,5 Md€ en 2026, l'État continue de verser ses
  58 Md€, la dette atteint 33 points de PIB en 2070 : les pensions baissent
  d'un tiers, et l'argent va des retraités aux actifs. L'argument d'urgence
  de la décision 6, sur lequel la défense devant le Conseil constitutionnel
  et la CEDH s'appuie, s'en affaiblit (à faire vérifier, chantier 2). La
  lecture A a l'inconvénient inverse : moins rendu aux cotisants, et une
  réserve qui s'accumule.

Ce qui reste à faire : refaire les deux lectures au modèle, la dépense
suivant le taux réellement cotisé, ce que le réglage du taux unique permet.
Jusque-là, les tableaux ci-dessus ne départagent pas A et B.

## Ce qui déplace ces chiffres

- **Le déficit de la lecture B.** Celui du COR compte en recettes les
  versements de l'État (contribution d'équilibre et subventions, 1,88 point
  de PIB en 2026), qui équilibrent les régimes de fonctionnaires : d'où un
  déficit de 0,16 point seulement en 2026. Compté sans eux, il vaut
  −2,05 points en 2026 et −4,13 en 2070 ; la lecture B en rend alors
  116 Md€ en 2026 (8,8 points de cotisation), 133 en 2040, 417 en 2070, et
  laisse une réserve de 26,9 points en 2070 (8 883 Md€ rendus en tout). La
  lecture B dépend d'abord du déficit que l'on divise ; c'est la convention
  que le chantier 7 demande d'annoncer.
- **La convergence.** Le modèle bascule d'un coup en 2026. Par cinquièmes
  (un cinquième de l'économie en 2026, la totalité en 2030), la lecture A
  rend 15, 31, 49 et 65 Md€ de 2026 à 2029 et finit avec une réserve de
  85,5 points ; tout au déficit, de 237,1 ; la lecture B ne bouge pas, son
  besoin étant couvert dès le premier cinquième.
- **Ce que le rendu devient.** En points de cotisation, la lecture A rend
  environ 5,6 points sur 21,4, soit un taux vers 16 %, sous les 18 % du
  programme ; la lecture B, environ 11 points, un taux vers 10 %. Ni l'un ni
  l'autre n'est le taux de la proposition, qui retire aussi les impôts
  affectés et les versements de l'État, et prélève cinq points pour le
  pilier.
- **Ce que le calcul ignore** : tout comportement, le pilier capitalisé, les
  recettes du chantier 4 (TVA, LVT), la décision 16 (les réversions servies
  gardées), que la session du modèle porte au scénario 6 et qui réduira
  l'économie.

## La reprise sur succession (décision 30)

La phrase du propriétaire lève l'incohérence que le chantier 2 relevait. La
reprise reste telle que l'action 47 l'écrit : la garantie est une avance, qui
porte intérêt au taux auquel l'État emprunte, reprise sur ce que la succession
contient et jamais au-delà, les donations réintégrées. Elle ne reprend que la
valeur de l'aide ; la décision 5 écarte l'impôt sur l'héritage, pas le
remboursement d'une avance. Les 220 Md€ de reprises de la variante
rétroactive restent au chiffrage. Le recours, que le modèle suppose de 50 %,
monte avec la garantie servie d'office (décision 20) : c'est au portage de la
session du modèle.
