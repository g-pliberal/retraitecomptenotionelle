# Le facteur démographique et le plancher, chiffrés au modèle pour le scénario 6 : les trois voies du stock

**Reprise, au 7 novembre 2026.** Les trois voies du stock sont chiffrées
au modèle, en variante, avec la règle d'avant et α = 1, sous le COR, une
inflation de 0,5 % et une crise de l'emploi
(`python scripts/indexation_scenario_6.py`, `--annees`, `--csv`). Le défaut
du scénario 6 n'a pas changé. Au propriétaire : sa voie, et les questions de
fin de note. Puis une session du modèle fait de la voie choisie le défaut du
scénario 6 (l'option `indexation_liberale` du coût devient sa règle), et la
page Coût la montre ; le plancher des comptes ne s'écrit que s'il doit jouer.

*Le 7 novembre 2026, le propriétaire écarte les trois issues proposées pour
le plancher du stock (décision 49) et demande trois voies neuves, chiffrées au
modèle pour le seul scénario 6, de 2026 à 2070, sous le scénario de
référence du COR et sous deux chocs : la dépense, le solde, les pensions du
stock et des nouvelles année par année, la dette ou la réserve, et ce que
chaque voie laisse aux cotisants, avec la règle d'avant pour comparer. Ce
qui suit est le calcul du modèle, non plus un calcul à côté. La page « Le
plancher et sa dette » (https://claude.ai/artifact/7R8FRCKLEQoqK1jKCnfa2c)
reste un outil pour comprendre.*

## Ce qui est chiffré, et comment

*Le moteur.* Le coût du dépôt reçoit une option, `indexation_liberale`
(`src/retraite_notionnelle/indexation_programme.py`), qui revalorise les
seules pensions du scénario 6, à compter de la bascule, sous une voie écrite
en données (`data/reference/etudes/indexation_scenario_6.yaml`). Sans elle,
rien ne bouge : un test vérifie que la règle d'avant redonne le coût du
modèle à 10⁻⁹ près. Tout le reste du coût joue : la garantie vieillesse, que
des pensions plus basses font monter ; le solde ; la dette. Les exemples du
propriétaire sont des tests : la reprise au plus de la moitié de la hausse
sert 1,000, puis 1,0145, puis 1,053, et laisse une dette de 2,00 %, puis
0,67 %, puis 0 ; sur toute la hausse au besoin (décision 49), la deuxième
année sert 1,0078.

*Les six règles comparées.*

| Règle | Pensions nouvelles | Stock (servi à la bascule) |
|---|---|---|
| La règle d'avant | masse salariale | prix |
| α = 1 sans plancher, l'étalon | masse salariale par retraité | prix moins la hausse du nombre de retraités par cotisant |
| α = 1, plancher et dette pour tous (décisions 41, 44, 46, 49) | la même, plancher et dette | la même, plancher et dette |
| Voie 1 | la même, plancher et dette | une prime de plus à la bascule, mise en réserve ; α = 1 ; la réserve paie le plancher |
| Voie 2 | la même, plancher et dette | une baisse de plus à la bascule, l'effort de α = 1 sur toute sa vie ; puis les prix, et le plancher du droit actuel (L. 161-25) |
| Voie 3 | la même, plancher et dette | la même règle que les nouvelles : masse salariale par retraité, plancher et dette |

*Le nombre de retraités par cotisant* est celui du COR, l'ensemble des
régimes, en cotisants par retraité de droit direct
(`decomposition_depense_retraite.csv`, que la décomposition de la page Coût
lit déjà) : 1,77 en 2025, 1,30 en 2070. Il monte de 0,50 % par an de 2027 à
2040, puis de 0,77 % par an jusqu'en 2070. La note d'étude avait pris les
retraités et les cotisants de la Cnav (0,65 point par an).

*Les trois trajectoires.* Le COR : 1,75 % d'inflation, 0,7 % de
productivité. Une inflation durable de 0,5 % : la croissance réelle reste
celle du COR, et seul ce qui se compte en euros courants change, le
plancher. La crise de l'emploi : l'emploi perd 1 % par an face au COR de
2030 à 2039, et ne le regagne pas, avec 1 % d'inflation. Elle passe par la
variante d'emploi que la page Coût sait déjà faire (action 138, étape 7) : le
PIB, la masse salariale, les comptes et les recettes la suivent, les
retraités non.

*Les conventions.* L'étalon est α = 1 sans plancher : ce que les retraités
doivent porter (décision 41). Ce qu'une voie dépense de plus, les cotisants
le paient ; de moins, les retraités paient plus que la règle. Les moyennes
de part de PIB sont simples, de 2026 à 2070, comme le solde moyen du dépôt ;
les valeurs actuelles s'actualisent au taux de la masse salariale. La dette
du plancher est celle du groupe : ce que le plancher a servi au-dessus de la
règle, porté au taux de la masse salariale, moins ce que les hausses ont
repris — y compris la dette des retraités morts avant de l'avoir rendue, que
personne ne rendra. La prime de la voie 1 se calibre sur un choc, tour à tour
sur chacun des deux. La baisse de la voie 2 se calcule sous le COR, au jour
de la bascule, et ne se révise pas.

*Le plancher des comptes* (décision 44) ne joue sous aucune des trois
trajectoires : la masse salariale y monte d'au moins 0,65 % par an en euros
courants. Il n'est pas écrit.

## Ce que le modèle corrige dans le calcul à côté

- **Le stock vit surtout quand le nombre de retraités par cotisant monte
  lentement.** Il fait 99 % des pensions de droit direct du scénario 6 en
  2026, 81 % en 2030, 40 % en 2040, 14 % en 2050, 2 % en 2060. L'effort que
  α = 1 lui demande sur sa vie vaut donc une baisse de **4,3 %** à la
  bascule, et non 7,5 % (la note d'étude) ni 6,9 % (la page interactive).
- **Sous la voie 3, le stock ne perd rien face aux prix : il gagne.** La
  masse salariale par retraité monte de 0,2 % par an en euros constants
  jusqu'en 2040 (le salaire moyen +0,69 %, le nombre de retraités par
  cotisant +0,50 %). Un euro du stock vaut 1,023 en 2030, 1,032 en 2050 ;
  sur sa vie, le stock touche 6,7 % de plus que sous α = 1, et environ 2 %
  de plus que sous les prix. La note d'étude écrivait −2,2 %.
- **La prime de la voie 1 est petite, mais permanente** : une baisse de
  **1,0 %** à la bascule couvre une inflation durable de 0,5 % ;
  **2,15 %** couvre la crise de l'emploi. Sous le COR, il n'en faut aucune.

## Les résultats

Parts de PIB : moyenne de 2026 à 2070 pour la dépense (les pensions du
scénario 6, réversion gardée comprise), la garantie et le solde ; dette du
système en 2070 ; « écart à α = 1 », ce que la voie dépense de plus que
l'étalon, en moyenne. Un dixième de point de PIB vaut environ 3 Md€ de 2026.

**Sous le COR.**

| Règle | Dépense | Garantie | Solde | Dette 2070 | Écart à α = 1 | dont stock | Dette du plancher, 2070 | Réserve, 2070 |
|---|---|---|---|---|---|---|---|---|
| La règle d'avant | 9,58 | 0,24 | −1,44 | 102,8 | +0,45 | +0,12 | 0 | — |
| α = 1 sans plancher | 9,13 | 0,26 | −1,00 | 74,5 | 0 | 0 | 0 | — |
| α = 1, plancher et dette | 9,13 | 0,26 | −1,00 | 74,5 | 0 | 0 | 0 | — |
| Voie 1, prime de 1,0 % | 9,11 | 0,26 | −0,97 | 72,4 | −0,03 | −0,03 | 0 | 1,19 |
| Voie 1, prime de 2,15 % | 9,08 | 0,26 | −0,94 | 70,0 | −0,06 | −0,06 | 0 | 2,54 |
| Voie 2 | 9,13 | 0,26 | −1,00 | 73,6 | 0 | 0 | 0 | — |
| Voie 3 | 9,31 | 0,25 | −1,17 | 87,3 | +0,18 | +0,18 | 0 | — |

**Sous une inflation durable de 0,5 %.**

| Règle | Dépense | Solde | Dette 2070 | Écart à α = 1 | Dette du plancher, 2070 | Réserve, 2070 |
|---|---|---|---|---|---|---|
| La règle d'avant | 9,58 | −1,44 | 102,8 | +0,45 | 0 | — |
| α = 1 sans plancher | 9,13 | −1,00 | 74,5 | 0 | 0 | — |
| α = 1, plancher et dette | 9,16 | −1,03 | 76,4 | +0,03 | 1,21 | — |
| Voie 1, prime de 1,0 % | 9,13 | −1,00 | 74,3 | 0 | 0,01 | 0 |
| Voie 1, prime de 2,15 % | 9,10 | −0,97 | 71,9 | −0,03 | 0,01 | 1,37 |
| Voie 2 | 9,13 | −1,00 | 73,6 | 0 | 0,01 | — |
| Voie 3 | 9,31 | −1,17 | 87,3 | +0,18 | 0,01 | — |

**Sous la crise de l'emploi, avec 1 % d'inflation.**

| Règle | Dépense | Solde | Dette 2070 | Écart à α = 1 | Dette du plancher, 2070 | Réserve, 2070 |
|---|---|---|---|---|---|---|
| La règle d'avant | 9,87 | −1,73 | 124,9 | +0,60 | 0 | — |
| α = 1 sans plancher | 9,27 | −1,14 | 85,2 | 0 | 0 | — |
| α = 1, plancher et dette | 9,33 | −1,19 | 89,7 | +0,06 | 2,59 | — |
| Voie 1, prime de 1,0 % | 9,30 | −1,17 | 87,4 | +0,03 | 0,01 | −1,38 |
| Voie 1, prime de 2,15 % | 9,27 | −1,14 | 84,9 | 0 | 0,01 | 0 |
| Voie 2 | 9,41 | −1,28 | 94,5 | +0,14 | 0,01 | — |
| Voie 3 | 9,45 | −1,31 | 98,5 | +0,18 | 0,07 | — |

La dette du plancher qui reste en 2070 est celle du stock, à 0,01 point
près : les pensions nouvelles rendent la leur dans les trois trajectoires, à
ce que doivent leurs morts près.

**Un euro de pension du stock**, en euros constants de la bascule, après la
baisse des décisions 2 et 3 :

| Règle | COR, 2030 | 2040 | 2050 | 0,5 %, 2050 | années sans hausse | crise, 2040 | 2050 | années sans hausse |
|---|---|---|---|---|---|---|---|---|
| La règle d'avant | 1,000 | 1,000 | 1,000 | 1,000 | 0 | 1,000 | 1,000 | 0 |
| α = 1 sans plancher | 0,995 | 0,932 | 0,875 | 0,875 | (35 de baisse) | 0,843 | 0,791 | (16 de baisse) |
| α = 1, plancher et dette | 0,995 | 0,932 | 0,875 | 0,902 | 38 | 0,892 | 0,807 | 40 |
| Voie 1, prime de 1,0 % | 0,985 | 0,923 | 0,866 | 0,893 | 38 | 0,883 | 0,799 | 33 |
| Voie 1, prime de 2,15 % | 0,974 | 0,912 | 0,856 | 0,883 | 38 | 0,873 | 0,790 | 33 |
| Voie 2 | 0,957 | 0,957 | 0,957 | 0,957 | 0 | 0,957 | 0,957 | 0 |
| Voie 3 | 1,023 | 1,026 | 1,032 | 1,032 | 3 | 0,922 | 0,933 | 9 |

Sous α = 1 avec plancher et dette, la dette d'un retraité du stock atteint
11 % d'une année de sa pension en 2040 et 37 % en 2050 sous l'inflation à
0,5 %, 37 % et 80 % sous la crise : elle ne se rend pas. Une pension liquidée
en 2030 vaut, en 2050, 1,159 sous la règle d'avant et 1,009 sous α = 1
(COR) ; 0,921 sous la crise.

*Année par année*, la dépense du scénario 6, en part de PIB, sous la crise
de l'emploi (les deux autres trajectoires : `--annees`) :

| Année | Avant | α = 1 | α = 1, plancher et dette | Voie 1 (1,0 %) | Voie 1 (2,15 %) | Voie 2 | Voie 3 |
|---|---|---|---|---|---|---|---|
| 2026 | 10,29 | 10,29 | 10,29 | 10,20 | 10,10 | 9,91 | 10,29 |
| 2030 | 10,08 | 9,96 | 9,96 | 9,89 | 9,81 | 9,75 | 10,16 |
| 2035 | 10,37 | 9,66 | 9,87 | 9,82 | 9,75 | 9,99 | 10,05 |
| 2040 | 10,53 | 9,56 | 9,75 | 9,71 | 9,67 | 10,03 | 9,88 |
| 2050 | 10,16 | 9,36 | 9,38 | 9,37 | 9,36 | 9,61 | 9,57 |
| 2060 | 9,34 | 8,89 | 8,89 | 8,89 | 8,88 | 8,92 | 8,92 |
| 2070 | 8,47 | 7,98 | 7,98 | 7,98 | 7,98 | 7,98 | 7,98 |

## Ce que chaque voie coûte, et à qui

- **α = 1 tel que décidé, sans voie pour le stock.** Sous le COR, rien : le
  plancher ne joue jamais. Sous une inflation basse ou une crise, le stock
  reste gelé en euros 38 à 40 ans sur 44, sa dette grossit sans se rendre,
  et les cotisants paient 0,03 à 0,06 point de PIB par an : 1,2 à 2,6 points
  de PIB de dette perdue en 2070, 37 à 80 Md€ à l'échelle du PIB de 2026.
- **Voie 1, la prime.** Le stock paie d'avance, toujours : 1,0 % ou 2,15 %
  de sa pension dès la bascule, même quand le choc ne vient pas. Sous le
  COR, la réserve finit pleine, 1,2 ou 2,5 points de PIB en 2070, quand le
  stock est éteint. Bien calibrée, elle ne laisse rien aux cotisants. Mal
  calibrée — une prime pour l'inflation basse, puis une crise de l'emploi —
  elle manque de 1,4 point de PIB. La prime de 2,15 % couvre les deux chocs
  étudiés. Le stock reste gelé en euros dans les années basses, comme sous
  le plancher : la réserve paie le gel, elle ne l'évite pas.
- **Voie 2, l'effort d'avance.** Le stock perd 4,3 % de plus à la bascule,
  puis suit les prix : sa pension ne baisse plus jamais en pouvoir d'achat,
  ni en euros, et n'est jamais gelée tant que les prix montent. Sous le COR
  et sous l'inflation basse, les cotisants ne paient rien. Sous la crise de
  l'emploi, ils paient 0,14 point de PIB par an : l'effort que α = 1 aurait
  demandé de plus au stock n'est pas demandé. Une révision à date fixe le
  reprendrait.
- **Voie 3, la même règle pour toutes.** Rien de plus à la bascule ; le
  stock partage la crise de l'emploi (−9 % en euros constants de 2030 à
  2040), et son plancher se rend presque tout. Mais il reçoit une part des
  gains de productivité qu'il n'a pas cotisés : les cotisants paient
  0,18 point de PIB par an, environ 5,5 Md€ de 2026, sous toutes les
  trajectoires, et la dette de 2070 monte de 13 points de PIB face à α = 1.
  Elle change la base que la décision 41 a fixée au stock (les prix, action
  48).
- **La règle d'avant**, pour mémoire : α = 1 épargne aux cotisants
  0,45 point de PIB par an sous le COR (0,12 sur le stock, 0,33 sur les
  nouvelles), 0,60 sous la crise, et 28 à 40 points de dette en 2070.

## Ce qui reste au propriétaire

1. **La voie** : 1, 2 ou 3, ou α = 1 tel quel.
2. **Pour la voie 1** : la crise qu'on assure, donc la prime (1,0 % pour une
   inflation durable de 0,5 % ; 2,15 % pour la crise de l'emploi, qui couvre
   aussi la première) ; ce que devient la réserve qui reste, et qui paie celle
   qui manque.
3. **Pour la voie 2** : une baisse fixée une fois pour toutes, les cotisants
   portant l'écart si la démographie dérive, ou révisée à date fixe ; elle
   s'ajoute à la baisse des décisions 2 et 3.
4. **Pour la voie 3** : accepter que le stock touche une part de la
   productivité, au prix de 0,18 point de PIB par an pour les cotisants, et
   revenir sur la base de la décision 41 pour le stock.
5. **Pour toutes** : la dette des retraités morts avant de l'avoir rendue,
   petite pour les pensions nouvelles (0,01 point de PIB en 2070), se perd ou
   se reprend sur la succession, comme la garantie (décision 30).

## Ce que le calcul ne dit pas

- La règle d'avant reste le défaut du scénario 6 : la page Coût, le site et
  les chiffres ancrés n'ont pas bougé.
- Une inflation basse ne change ici que le plancher : les recettes, le
  système actuel et ses règles en euros courants (la valeur de service de
  l'Agirc-Arrco) gardent la croissance réelle du COR.
- La crise de l'emploi ne change ni les départs, ni la mortalité, ni le
  nombre de retraités ; elle ne dure que dix ans et ne se rattrape pas.
- La baisse de la voie 2 et les primes de la voie 1 dépendent de la série du
  nombre de retraités par cotisant : celle de la Cnav, qui monte plus vite
  au début, donnerait davantage.
