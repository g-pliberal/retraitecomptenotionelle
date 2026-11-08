# La voie 1 au modèle : la prime rendue en route, et la dette de la réserve qui manque

*Le 8 novembre 2026, action 186, chantier 5. Les décisions 73 à 77 ont pris
la voie 1 (note `2026-11-07-indexation-scenario-6.md`) : une prime de 2,15 %
sur les pensions du stock, mise en réserve, qui paie son plancher. Restaient
à écrire au modèle la règle qui baisse la prime (décision 75) et la dette du
stock quand la réserve manque (décision 76). Les chiffres sont ceux de `main`
au commit `df6ca19`, sous le scénario de référence du COR et les deux chocs
de l'étude, de 2026 à 2070.*

## Ce qui est écrit au modèle

- **La règle, en une fonction** (`assurer`, testée sur des cas posés à la
  main). Chaque année, la règle de la décision 41 joue ; la pension ne baisse
  pas en euros. La réserve, placée au taux de la masse salariale, reçoit la
  prime et paie ce que le plancher sert au-dessus de la règle. Si elle
  touche zéro, ce qui manque devient la dette de chaque euro du stock encore
  vivant, au taux de la masse salariale, reprise sur les hausses suivantes,
  au besoin toutes (décisions 46, 49 et 76) ; celle des morts est perdue
  (décision 77). Puis la prime se révise : celle qui, avec la réserve,
  couvre ce que le plancher peut encore coûter, si elle est plus basse. Elle
  ne remonte jamais, sans quoi la pension baisserait en euros (promesse 4) ;
  sous zéro, elle devient un supplément, qui rend la réserve au stock.
- **Ce que le plancher peut encore coûter** se mesure chaque année, sur ce
  qui reste du stock, depuis ce que sa pension et sa règle valent ce
  jour-là, sous chaque risque assuré, le plus coûteux l'emportant, actualisé
  au taux de la masse salariale.
- **La masse du stock** entre dans le calcul : une réserve se compte sur un
  groupe, et le stock fond (86 % de sa masse de 2026 en 2030, 51 % en 2040,
  19 % en 2050, 2 % en 2060). Le coût la donne, sous les prix ; elle est la
  même sous les trois trajectoires, qui ne touchent pas les retraités. Le
  coût la reçoit par `IndexationLiberale(masses_stock=…)`.
- **Les données** : deux voies de plus dans
  `data/reference/etudes/indexation_scenario_6.yaml`,
  `voie_1_crise_a_ses_dates` et `voie_1_crise_recommencee`, avec leurs
  options (`crise_assuree`, `retour`, `reserve_manquante`). La voie 1 de
  l'étude, sa prime jamais rendue et sa réserve à la charge des cotisants,
  reste telle quelle : ses chiffres n'ont pas bougé.

## Les trois façons de lire la décision 75

1. **La crise à ses dates, ou recommencée.** À ses dates, la crise assurée
   reste celle de 2030 à 2039 : une fois passée sans venir, elle ne coûte
   plus rien, et la réserve revient. Recommencée, elle reste toujours à
   quatre ans, pour dix ans, telle qu'on l'assure à la bascule. Les deux se
   confondent en 2026. Commencer la crise l'année suivante a été essayé et
   écarté : une crise de 2027 à 2036 coûte moins qu'une de 2030 à 2039 (le
   nombre de retraités par cotisant monte plus vite après 2040), et la prime
   tomberait à 1,70 % dès 2027, contre la décision 74.
2. **La crise seule, ou l'inflation basse avec.** La décision 74 dit que la
   prime de 2,15 % « couvre aussi une inflation durable de 0,5 % » ; mesurée
   sous la seule crise, qui a 1 % d'inflation, la prime ne la couvre plus une
   fois la réserve rendue.
3. **Dès que la réserve et les primes à venir suffisent, ou au seuil.** La
   prime se recalcule chaque année, et baisse dès que la réserve est en
   avance ; ou, à la lettre, elle reste entière tant que la réserve seule ne
   couvre pas tout, puis devient d'un coup un supplément.

## Les chiffres

La prime, en % de la pension du stock (négative : un supplément) ; la plus
forte dette d'un retraité du stock, en part d'une année de sa pension ; un
euro du stock en euros constants de la bascule, en 2050 (α = 1 sans
plancher : 0,875 sous le COR et l'inflation basse, 0,791 sous la crise).
« Dès que suffisent » sauf mention.

**Sous le COR.** Le plancher ne joue jamais ; toutes les lectures rendent
toute la réserve, et les cotisants ne paient ni ne gagnent rien (écart à
α = 1 nul). Ce qui change, c'est à qui et quand.

| Lecture | Prime 2030 | 2035 | 2040 | 2050 | 2060 | Un euro, 2050 |
|---|---|---|---|---|---|---|
| À ses dates | 2,15 | −0,55 | −2,66 | −2,66 | −2,66 | 0,898 |
| À ses dates, et l'inflation basse | 2,15 | −0,55 | −2,09 | −3,51 | −5,34 | 0,906 |
| Recommencée (avec ou sans l'inflation basse) | 2,15 | 0,04 | −1,11 | −5,39 | −9,30 | 0,922 |
| À ses dates, au seuil | 2,15 | −0,88 | −3,00 | −3,00 | −3,00 | 0,901 |
| Recommencée, au seuil | 2,15 | −0,37 | −1,53 | −5,83 | −9,75 | 0,926 |

La voie 1 de l'étude, sa prime jamais rendue, gardait 2,5 points de PIB de
réserve en 2070, un stock éteint, et les cotisants en gagnaient 0,06 point
par an ; la voie décidée les rend au stock.

**Sous une inflation durable de 0,5 %.**

| Lecture | Prime 2040 | 2050 | Dette d'un retraité, max | Un euro, 2050 | Pour les cotisants |
|---|---|---|---|---|---|
| À ses dates, la crise seule | −1,82 | −1,82 | 175 % (2070) | 0,919 | +0,02 point de PIB par an |
| À ses dates, et l'inflation basse | −0,08 | −0,08 | 0 | 0,903 | 0 |
| Recommencée, la crise seule | 0,13 | −0,49 | 62 % (2070) | 0,907 | 0 |
| Recommencée, et l'inflation basse | 0,13 | −0,35 | 0 | 0,906 | 0 |

**Sous la crise de l'emploi**, celle que la prime assure.

| Lecture | Prime 2035 | 2040 | 2050 | 2060 | Dette d'un retraité, max | Un euro, 2050 |
|---|---|---|---|---|---|---|
| À ses dates, la crise seule | 2,15 | 2,15 | 1,12 | 0,04 | 10 % (2056) | 0,798 |
| À ses dates, et l'inflation basse | 2,15 | 2,15 | 2,15 | −1,25 | 3,8 % (2056) | 0,790 |
| Recommencée (avec ou sans) | 1,46 | 1,46 | 1,46 | −0,80 | 24,5 % (2056) | 0,795 |
| Toutes, au seuil | 2,15 | 2,15 | 2,15 | −0,4 à −2,6 | 3,6 à 3,7 % (2055-2056) | 0,790 |

La dépense du scénario 6, en moyenne de 2026 à 2070, reste celle de α = 1
sans plancher, à un centième de point de PIB près : 9,13 points sous le COR
et sous l'inflation basse, 9,27 sous la crise, la dette du système en 2070
à 74,0 ou 74,1 points sous le COR, 84,9 à 85,0 sous la crise. Deux
exceptions : à ses dates, la crise seule, sous l'inflation basse (9,15 ;
dette 75,2) ; recommencée, sous la crise (9,28 ; dette 85,8), où les
cotisants paient 0,01 point par an.

## Ce que le calcul apprend

- **La prime de 2,15 % équilibre la réserve sur l'horizon, non à chaque
  date.** Sous la crise même qu'elle assure, la réserve passe sous zéro vers
  2049 (le calcul de l'étude laissait les cotisants l'avancer). Sous la
  décision 76, ce creux devient une dette du stock, de 4 à 10 % d'une année
  de pension vers 2056, rendue avant 2070 ; ce que la prime a mis de trop
  revient ensuite.
- **Mesurée sous la seule crise, la prime ne couvre plus l'inflation
  basse une fois la réserve rendue.** À ses dates, la réserve revient au
  stock dès 2035 ; si l'inflation reste à 0,5 %, le plancher joue chaque
  année, sans réserve, et la dette de chaque retraité du stock monte à 1,75
  année de pension en 2070. Elle ne se rend jamais : les morts l'emportent
  (décision 77), et les cotisants paient 0,02 point de PIB par an. Mesurée
  sous les deux risques, il n'y a pas de dette.
- **Recommencée, la mesure ne voit pas une crise en cours.** Pendant la
  crise de 2030 à 2039, elle suppose la suivante dans quatre ans : la prime
  tombe à 1,46 % en pleine crise, et la dette monte à 24,5 %. Sous le COR,
  elle garde la réserve plus longtemps et la rend à moins de monde : un
  supplément de 9,3 % en 2060, au dernier vingtième du stock.
- **Au seuil, la prime tient pendant la crise** (dette au plus 3,7 %), mais
  ne rend rien avant que la réserve seule suffise.

## Ce qui revenait au propriétaire

1. **La crise à ses dates, ou recommencée** ;
2. **La crise seule, ou l'inflation basse avec** ;
3. **La prime qui baisse dès que la réserve et les primes à venir suffisent,
   ou seulement quand la réserve seule suffit (au seuil).**

## Ce que le propriétaire a répondu

Le même jour, aux trois questions : sans préférence. À la proposition de
mesurer sous la crise à ses dates et l'inflation basse, la prime baissant
dès que la réserve et les primes suffisent : « On fait un système avec une
faible contribution durable pour amortir un choc passager ». À la lecture
qui en était tirée (la crise recommencée, au seuil) : « Contribution de 1%
tout le temps ». À la question de son assiette et du sort de la réserve
inutilisée : « Quelle différence entre le stock seul et toutes les
pensions ? » ; « Je ne sais pas. Il faut une solution où personne ne se
sentirait flouée. C'est le problème avec les contributions actuelles. Tout
le monde se sent floué. Est-ce que cela pourrait être une réserve
personnelle en plus du compte notionnel ? »

Rien n'est écrit en décision : la contribution de 1 % est sa direction, son
assiette et le sort de sa réserve restent ouverts. Les décisions 74 et 75
(2,15 %, rendus en route) tiennent tant qu'il ne les a pas remplacées.

**Une contribution de 1 % du stock, mise en commun, jamais rendue**
(`v1_un_pour_cent`).

| Trajectoire | Réserve max, point de PIB | Dette d'un retraité, max | Un euro, 2050 | Pour les cotisants |
|---|---|---|---|---|
| COR | 1,18 (2070, jamais servie) | 0 | 0,866 | −0,03 point de PIB par an |
| Inflation durable de 0,5 % | 0,58 | 41 % (2070) | 0,893 | 0 |
| Crise de l'emploi | 0,45 | 54 % (2057) | 0,799 | +0,03 point par an |

Sans choc, le stock paie 1 % de sa pension toute sa vie, et la réserve,
jamais servie, reste au système quand il s'éteint : les cotisants la
gagnent. Sous un choc, 1 % ne suffit pas, et la dette d'un retraité monte à
la moitié d'une année de pension.

**La même contribution dans une réserve à soi** (la survie à un : rien ne
passe des morts aux vivants), en années de la pension servie :

| Trajectoire | Réserve 2030 | 2040 | 2050 | Dette 2040 | 2050 |
|---|---|---|---|---|---|
| COR | 0,05 | 0,17 | 0,30 | 0 | 0 |
| Inflation durable de 0,5 % | 0,05 | 0,05 | 0 | 0 | 0,08 |
| Crise de l'emploi | 0,05 | 0 | 0 | 0,21 | 0,51 |

*Ce que les deux tableaux disent.* Le risque du plancher est commun : la
même règle vaut pour tout le stock, et un choc le frappe tout entier à la
fois. Mettre les réserves en commun n'assure donc presque rien de plus
qu'une réserve à soi (une dette de 54 % au plus contre 51 % en 2050 sous la
crise) ; elle ne fait que passer aux survivants les primes des morts — ce
qui fait qu'on s'y sent floué. Une réserve à soi garde ce que chacun a payé
(0,30 année de pension en 2050 sans choc) ; reste à dire ce qu'elle devient
au décès (les héritiers, le conjoint, ou une rente), que le coût ne compte
pas encore.

*Le stock seul, ou toutes les pensions.* Le stock, ce sont les pensions
servies à la bascule : leur règle, les prix moins la hausse du nombre de
retraités par cotisant, baisse en euros dès que l'inflation est basse, et
leur plancher joue souvent ; la contribution s'éteint avec elles, vers 2070.
Les pensions nouvelles suivent la masse salariale par retraité : elles ne
baissent en euros que dans une vraie crise de l'emploi, et leur plancher se
paie déjà par leur propre dette (décision 46), presque toujours rendue
(0,01 point de PIB perdu en 2070). Une contribution sur toutes les pensions
durerait pour toutes les générations, et s'accumulerait presque sans
servir — sauf à être personnelle.

## Ce qui reste à faire

- Étudier la réserve personnelle (la question du propriétaire) : ce qu'elle
  paie, comment elle se place (au taux du compte), ce qu'elle devient au
  décès, pour le stock seul ou pour toutes les pensions, et ce qu'en dit le
  droit ; le coût ne sait pas encore compter ce qui sort au décès.
- Écrire ses réponses en décisions, sous le chantier 5, après relecture
  d'`origin/main` pour le numéro, et dans les données.
- **Faire de la voie 1 le défaut du scénario 6.** Le coût, aujourd'hui, ne
  reçoit la voie que par son option `indexation_liberale`, et la masse du
  stock que par elle. Pour le défaut, il lui faut cette masse sans qu'on la
  lui donne : un premier passage du coût, le stock seul sous les prix, qui
  double à peu près son temps, ou la masse figée dans les données, que la
  suite confronte au coût. Puis `python scripts/regenerer.py` : les témoins,
  le paquet, les chiffres ancrés du scénario 6 bougent tous.
- **La page Coût** montre la prime, la réserve et ce que le stock en
  retrouve, après une vérification qu'aucune autre session n'est sur les
  pages.
- Le plancher des comptes (décision 44) ne joue toujours sous aucune
  trajectoire : il n'est pas écrit.
