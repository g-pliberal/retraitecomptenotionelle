# Étape 14 : les salariés agricoles saisonniers — l'écart de durée est réel, aucune source ne dit qui ils sont ; rien ne change

**Le 5 novembre 2026 : les deux études de la MSA, relues à leur empreinte,
contre la population mesurée à leur champ. Le bilan du minimum contributif de
2005 à 2015 ne compte pas la même chose qu'elle : ses trimestres sont ceux du
seul régime agricole, d'avant la liquidation unique. L'étude de la liquidation
unique au 31 décembre 2021 compte la même : 25,7 % des hommes qu'elle liquide
ont moins de 48 trimestres aux régimes alignés, 12,3 % des femmes ; la
population, à son champ, 6,5 % et 0,0 %. L'écart est réel, mais aucune des
deux ne dit qui sont ces carrières courtes ni comment elles cotisent. Rien ne
change de la population.**

Demande : la vague 10 du 5 novembre 2026, tâche I4, « les salariés agricoles
saisonniers dans la population. Mesure d'abord ; correction seulement si une
source la fonde » ; le point 2 de « Ce qui reste » de la note
`2026-10-28-etape-14-independants-et-agricoles.md`, et « les saisonniers
agricoles » du bloc de l'étape.

## Les deux sources, ouvertes pendant la session

Aucune n'était dans le dépôt : `data/sources_a_explorer.yaml` les nommait
(`msa_bilan_minimum_contributif_2018`, `msa_liquidation_unique_2021`), sans
empreinte. Toutes deux téléchargées le 5 novembre 2026 au site de la MSA, et
leur empreinte inscrite à leur fiche :

- MSA, L'Observatoire économique et social, *Synthèses*, janvier 2018, « Le
  bilan du minimum contributif au régime des salariés agricoles entre 2005 et
  2015 », douze pages,
  `https://statistiques.msa.fr/wp-content/uploads/2018/01/Le-minimum-contributif-2005-2015-SA-1.pdf`,
  sha256:7e57b40155d33bf13241184bba10add64033b2fe2b155dd6b96354146348b703.
- MSA, Sylvain Allard, « La liquidation unique des régimes alignés au 31
  décembre 2021 », étude, janvier 2023, dix-huit pages,
  `https://statistiques.msa.fr/wp-content/uploads/2023/01/Etude-Lura-2021.pdf`,
  sha256:3475c325172301e597c3e92dae7f844d782bf710fd2d5995188fefb31ba7f493.

## Ce que chacune compte, et ce que compte la population

La population ne fait pas de carrière agricole propre : elle donne à chaque
carrière du salariat privé une part de salarié agricole, selon le rang de sa
pension par année validée dans l'EIR de 2020, au régime principal
(`grille_large.parts_agricoles`, note du 16 octobre). Cette part est la
carrière entière, liquidée une fois, au même droit que le régime général. Son
salarié agricole est donc le liquidant unique d'une carrière des seuls régimes
alignés.

**Le bilan de 2018 ne compte pas la même chose.** Son champ est celui des
nouveaux pensionnés de droit propre du régime de 2005 à 2015 (hors versement
forfaitaire unique, au graphique 5, p. 5) : avant la liquidation unique,
chaque régime liquide sa part, et ses pensionnés « peuvent avoir tous les
profils de carrière tant qu'ils ont traversé au moins une fois le régime des
salariés agricoles », dit l'étude de 2023 de ceux qui y échappent (p. 13). Ses trimestres
sont ceux du seul régime agricole : « 3 pensionnés sur 4 ont moins de 40
trimestres validés (10 ans) au régime agricole » (p. 9) ; « les pensionnés du
régime sont en très grande majorité polypensionnés (plus de 95 % des
pensionnés en 2015) et présents dans au moins un autre régime aligné (90 % des
pensionnés en 2015 […]) » (p. 9). Un assuré de dix trimestres agricoles et de
cent cinquante au régime général y est un pensionné à dix trimestres ; la
population n'a pas cet objet, et depuis juillet 2017 cet assuré liquide au
régime général si c'est son dernier régime. Ses saisonniers, il les décrit
sans les chiffrer : « Etre polypensionné avec un faible nombre de trimestres
validés au sein du régime des salariés agricole » et « Avoir eu, dans le
régime des salariés agricoles, des salaires peu élevés et non représentatifs
des autres revenus perçus dans la carrière » (p. 8). L'écart de définition se
déclare : il ne se corrige pas.

**L'étude de 2023 compte la même chose, à cinq réserves près.** Son champ :
les nouveaux retraités de droit propre du régime, « en France métropolitaine,
entre le 1er juillet 2017 et le 31 décembre 2021 » (p. 5), « encore présents
au 31 décembre 2021 » (p. 5) ; 69,1 % liquident en Lura (p. 5), 79,3 % des
nés à partir de 1953, seuls concernés (tableau 1, p. 8). Le liquidant Lura a
une pension unique des régimes alignés, liquidée par le dernier : l'objet de
la population. Les réserves : (1) la population donne sa part agricole au
rang de la pension dans l'EIR, au régime principal, et non au dernier
régime ; (2) l'étude ne dit pas si ses « trimestres […] dans les régimes
alignés » comptent les majorations pour enfants : les deux lectures sont
mesurées ; (3) elle ne dit pas si elle compte les retraités qui vivent à
l'étranger : la population les compte ; (4) elle ne compte que les présents
au 31 décembre 2021, la population ne fait mourir personne avant ; (5) ses
montants sont « hors avantages complémentaires », qu'elle ne définit pas, en
euros qu'elle ne date pas.

## La mesure, dans la population

Un pilote hors du dépôt, dans le brouillon de la session : les 17 624
carrières du salariat privé de la population, les seules à part agricole,
simulées au scénario 1 aux générations 1944 à 1963, 352 480 lignes, aucune
refusée (2 493 secondes sur quatre cœurs). Chacune pèse comme dans
`part_minimum_contributif.mesurer` : son poids de 2020, la part de sa
génération, les retraités de l'étranger mêlés aux résidents
(`avec_les_non_residents`), fois sa part agricole (`agricoles`) ; ses douze
mois de naissance étalent sa date d'effet. Le champ de l'étude de 2023 : nés à
partir de 1953, pension prenant effet de juillet 2017 à décembre 2021.

| au champ de 2023 | MSA, Lura | population, avec majorations | sans (16 trim. ôtés aux femmes) |
|---|---|---|---|
| hommes, moins de 48 trimestres | 25,7 % | 6,5 % | 6,5 % |
| femmes, moins de 48 trimestres | 12,3 % | 0,0 % | 0,3 % |
| hommes, plus de 155 | 42,1 % | 62,3 % | 62,3 % |
| femmes, plus de 155 | 47,9 % | 74,3 % | 60,9 % |
| pension mensuelle, hommes | 652 € | 953 € | |
| pension mensuelle, femmes | 613 € | 945 € | |
| pension de moins de 100 €, hommes | 19,8 % | 6,4 % | |
| pension de moins de 100 €, femmes | 9,8 % | 0,5 % | |
| salaire annuel moyen des femmes, sous celui des hommes | 11,3 % | 6,9 % | |
| au minimum contributif, hommes / femmes | non publié | 10,5 / 17,1 % | |

Les chiffres de l'étude, tels quels : « Les hommes ayant liquidé en Lura sont
25,7 % à avoir cumulé moins de 48 trimestres dans les régimes alignés, contre
12,3 % pour les femmes » (p. 13) ; « les femmes étant proportionnellement
plus nombreuses que les hommes à avoir validé plus de 155 trimestres dans les
régimes alignés (47,9 % contre 42,1 %) » (p. 13) ; tableau 4 (p. 12), 652 € et
613 € ; « 19,8 % des nouveaux retraités Lura hommes disposent d'une pension
inférieure à 100 €, contre 9,8 % pour les femmes » (p. 12) ; le salaire
annuel moyen « est inférieur de 11,3 % pour les femmes » (p. 13).

Les calculs posés à la main :

- *Sans les majorations* : la population donne à toute femme deux enfants
  (`grille_large.ENFANTS = 2`), huit trimestres chacun : 16 trimestres ôtés,
  moins de 48 hors majorations veut dire moins de 64 avec.
- *Le salaire* : 23 785 € pour les femmes, 25 545 € pour les hommes, salaire
  annuel moyen lu au détail de la pension, moyenne pesée ;
  23 785 / 25 545 = 0,9311, soit 6,9 % sous les hommes.
- *Les carrières courtes de la population sont celles de l'étranger* : chez
  les hommes, 23,5 % des retraités de l'étranger ont moins de 48 trimestres,
  1,7 % des résidents ; l'étranger pèse 275 510 / 1 240 567 = 22,2 % des
  hommes agricoles ; 0,222 × 23,5 + 0,778 × 1,7 = 5,2 + 1,3 = 6,5 %.
- *Les non-salariés agricoles de l'étude* : « 20 501 hommes contre 14 711
  femmes au 31 décembre 2021 avec au moins 16 trimestres NSA » (p. 13), sur
  81 244 hommes et 57 669 femmes liquidés en Lura (tableau 1, p. 8) :
  20 501 / 81 244 = 25,2 %, 14 711 / 57 669 = 25,5 %. La même part des deux
  sexes : elle ne dit pas pourquoi les hommes ont plus de carrières courtes.
- *L'âge* : en 2021 seule, la population liquide ses agricoles du champ à
  62,59 ans (hommes), 62,81 (femmes), 62,68 (ensemble) ; l'étude, « 62,3 ans
  (62,1 ans chez les hommes et 62,5 ans chez les femmes) » (p. 5).

Au champ de 2018, pour mémoire, et sous l'écart de définition : parmi les
agricoles de la population partis en 2014, 7,0 % des hommes et 0,0 % des
femmes ont moins de 40 trimestres, pour « 3 pensionnés sur 4 » au seul
régime agricole (p. 9) ; 14,7 % des hommes et 22,4 % des femmes ont le
minimum, quand « 20 % des hommes et 40 % des femmes se voient attribuer le
MICO » (p. 5, partis en 2014, présents au 31 décembre 2015) ; en 2015, 16,3 %,
pour « 26 % » des nouveaux entrants (p. 5).

## Ce que la mesure dit, et pourquoi rien ne change

L'écart est réel au champ de 2023, sous les deux lectures des majorations :
quatre fois moins de carrières courtes chez les hommes (6,5 % pour 25,7), plus
de carrières longues des deux sexes, des pensions plus hautes. Mais la
correction voudrait une source qui dise qui sont ces carrières courtes et
comment elles cotisent. Aucune ne le dit :

- l'étude de 2023 ne les appelle pas saisonnières ; elle ne publie ni leur
  salaire, seulement l'écart de celui des femmes, ni leurs autres périodes —
  l'étranger, le régime des non-salariés agricoles hors des 25 % qui y ont 16
  trimestres, les régimes non alignés ;
- le bilan de 2018 décrit les saisonniers sans chiffrer leur salaire, et ses
  saisonniers polypensionnés liquident depuis juillet 2017 au régime général
  quand il est leur dernier régime : ce ne sont pas, en tout, les liquidants
  de 2023.

Donner la part agricole selon la durée, pour rendre les 25,7 %, défairait sa
part selon le rang, que l'EIR de 2020 fonde, sans source pour le salaire des
carrières ainsi déplacées. Et le droit ne distingue pas le salarié agricole :
sa pension est celle du régime général, au centime (note du 16 octobre) ;
seul le partage entre la Cnav et la MSA salariés de la mesure en bougerait.
La population n'est donc pas changée : ni ses poids, ni ses carrières, ni sa
part agricole. Ce que la source ne tranche pas, ici : si ses trimestres
comptent les majorations pour enfants, si elle compte les retraités de
l'étranger, ce que sont ses « avantages complémentaires » et la date de ses
euros.

- *Ce qui ne bouge pas.* La population ; la page ; aucun moteur, aucun
  témoin, aucun test ; le paquet, qui ne lit pas les sources à explorer.
  Aucune règle du scénario 1 ne change : pas d'entrée au journal de veille.
  Seules changent les deux fiches de `data/sources_a_explorer.yaml`, qui
  portent l'empreinte de leur document.

**Ce qui reste** de ce point : une source qui dise, pour les liquidants de la
MSA salariés depuis la liquidation unique, qui sont les carrières courtes —
l'étranger, les non-salariés agricoles, les saisonniers — et leur salaire ;
sans elle, rien à corriger.
