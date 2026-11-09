# Le rendement net du déficit : ce que chaque génération paie, et ce que la comparaison devient

**Reprise, au 9 novembre 2026.** Le rendement net est chiffré, rien n'est
touché au modèle ni au site. La comparaison ne s'inverse pas : net du
déficit que le COR projette, le droit actuel rend encore plus que la
proposition à chaque cas type du privé, de la génération 1960 à la
génération 2010, sous les conventions du site comme sous celles du COR ; la
caisse de la proposition, telle que le modèle la chiffre, est même plus
déficitaire que le droit actuel jusqu'en 2054. Au propriétaire : les six
questions de la fin (« Ce que le propriétaire tranche »). Rien d'autre à
faire avant ses réponses.

*Le 9 novembre 2026, le propriétaire ouvre la suite du chantier 7 de
l'action 186 : « le rendement des cotisations, net de ce que chaque
génération paie pour combler le déficit ». Le constat de départ est celui des
notes `2026-11-07-chiffres-qui-tiennent.md` (§ 4) et `2026-11-08-site-etude.md`
(§ 3) : pour le salarié moyen né en 2000, l'outil donne 1,3 % réel au droit
actuel et 0,2 % à la proposition. L'argument à éprouver : « le 1,3 % est une
promesse que ses cotisations ne paient pas, et que la même génération paiera
en impôts ou en dette ». La consigne : poser la méthode d'abord, chaque choix
à sa source ; chiffrer au modèle tel qu'il est ; dire si la comparaison ne
s'inverse pas. C'est une étude : ni le modèle ni le site ne sont touchés, le
script est resté hors du dépôt, et chaque calcul est posé ici en entier pour
qu'on le refasse. Ce que la note conclut est une piste : le propriétaire
tranche.*

*Lire les chiffres.* **(publié)** est un chiffre ou un texte lu ce jour dans
sa source, dont l'adresse est donnée. **(dépôt)** est une sortie du modèle au
commit `1c32439` — `scripts/cycle_de_vie.py` pour les carrières, le coût
(`memoire.cout(Parametres())`) pour les comptes — ou une donnée certifiée du
dépôt. **(calcul)** est une opération de la session sur ces chiffres, posée
en entier. Les rendements sont en pour cent par an ; « la proposition » est le
scénario 6 du modèle à ce commit, qui n'est pas encore le programme décidé
(« Limites »).

## L'essentiel

**La comparaison ne s'inverse pas.** Le salarié moyen né en 2000, sous les
conventions du site :

| | Droit actuel | Proposition | Écart |
|---|---:|---:|---:|
| Rendement de l'outil **(dépôt)** | 1,32 | 0,17 | 1,15 |
| Net du déficit, payé chaque année par un impôt sur les salaires **(calcul)** | 1,13 | −0,16 | 1,29 |
| Net du déficit, emprunté jusqu'en 2070 **(calcul)** | 1,32 | 0,17 | 1,15 |
| Net de tout ce qui n'est pas cotisation — impôts affectés, versements de l'État, transferts, déficit **(calcul)** | 0,30 | −0,24 | 0,54 |

Quatre raisons, dans l'ordre de leur poids.

1. **Le déficit du COR est petit devant les cotisations d'une vie.** Payé par
   un impôt sur les salaires, il coûte au salarié moyen né en 2000 46 150 €
   d'aujourd'hui sur sa carrière, 7,7 % de ses cotisations : son rendement
   perd 0,19 point. Pour descendre au niveau de la proposition, il faudrait
   lui prélever 14,8 points de salaire brut de plus chaque année dès 2026 —
   6,4 points de PIB par an, quand le COR en projette 2,4 en 2070.
2. **La caisse de la proposition, au modèle, est plus déficitaire que le
   droit actuel pendant près de trente ans** : 2,19 points de PIB en 2026 contre
   0,16, 1,44 en moyenne de 2026 à 2070 contre 1,13, une dette de 103 points
   de PIB en 2070 contre 66 **(dépôt)**. La même règle, appliquée aux deux
   systèmes, retire donc plus à la proposition (0,33 point) qu'au droit
   actuel (0,19).
3. **« La même génération paiera » dépend de qui paie, et quand.** Si le
   déficit est emprunté, les générations 1960 à 2000 ne paient rien : la
   charge, 3,6 points de PIB par an après 2070, tombe sur celles qui
   travailleront alors, nées après 2010. C'est la convention même d'Auerbach,
   Gokhale et Kotlikoff : les générations vivantes au droit en vigueur, le
   reste aux générations à naître.
4. **Tout compter rapproche les deux systèmes sans les inverser**, sauf pour
   le cadre né à partir de 1990 (−0,75 contre −0,45 pour celui né en 2000).
   Cette convention-là charge au salarié du privé les impôts qui paient les
   pensions des fonctionnaires et la solidarité : elle se discute.

**Ce que le programme peut affirmer** (« 7. ») : non pas qu'il rend plus,
mais que le droit actuel sert un rendement que ses cotisations ne paient
pas — 1,3 % promis, 1,1 % une fois le déficit payé, 0,3 % une fois comptés
les impôts qui le complètent —, que la facture de ce qui n'est pas cotisation
passe au droit actuel de 11,6 à 15,9 points de salaire brut entre 2026 et
2070, et à la proposition de 6,1 à 0,8, et que l'écart de rendement entre le
SMIC et le cadre y est deux fois moindre. La phrase « nous vous servons
0,2 %, payés » de la note du 8 novembre ne tient pas au modèle tel qu'il
est : la caisse de la proposition y est en déficit jusqu'en 2069.

## 1. La méthode, chaque choix à sa source

### 1.1. Le cadre : les comptes de génération

Auerbach, Gokhale et Kotlikoff (1991) remplacent le déficit d'une année par
la contrainte budgétaire de l'État sur toute sa durée : la somme des comptes
de toutes les générations, vivantes et à naître, et du patrimoine net de
l'État doit suffire à payer la valeur actuelle de sa consommation présente
et future — « sufficient to finance the present value of current and future
government consumption » **(publié)**. Le compte d'une génération est la
valeur actuelle de ce qu'elle paiera, net de ce qu'elle recevra. Leur
convention de bouclage : les générations vivantes paient ce que le droit en
vigueur leur demande, rien de plus — « if the fiscal burden on current
generations is not increased relative to that projected from current
policy » —, et ce qui manque est mis à la charge des générations à naître,
traitées également « except for an adjustment for growth » **(publié)**, au
résumé du chapitre. L'article de 1994 en donne l'usage : dire ce qu'une
politique « will ultimately require future generations to bear »
**(publié)**.

Cette note garde le cadre et en change deux choses, qu'il faut dire. Elle ne
tient que le compte des retraites — cotisations et impôts versés pour elles,
pensions reçues —, non celui de toutes les finances publiques. Et elle
exprime le résultat en rendement interne, celui de l'outil, plutôt qu'en
valeur actuelle : le compte d'une génération est nul au taux qui est son
rendement net.

### 1.2. Quel déficit

**Pour le droit actuel, la projection du COR**, rapport de juin 2026,
scénario de référence, convention du COR — où la contribution de l'État
équilibre le régime de ses fonctionnaires. Le dépôt en tient les comptes
certifiés (`data/reference/macro/comptes_retraite.csv`, source
`cor_comptes_systeme_retraite`), et le coût du scénario 1 les suit : un solde
de −0,16 point de PIB en 2026, −0,20 en 2030, −0,89 en 2045, −1,22 en 2050,
−2,39 en 2070 **(dépôt)** ; le site écrit « −0,2 point de PIB en 2030, −0,9
en 2045 et −2,4 » en 2070.

**Pour la proposition, le solde de sa caisse au modèle**, comme la page
Coût : ses cotisations à 18 %, sans impôts affectés ni versements de l'État,
contre ses pensions ; −2,19 points en 2026, −1,77 en 2050, +0,05 en 2070
**(dépôt)**. La garantie vieillesse, que l'impôt paie et que l'outil ne
compte pas dans ce qui est reçu, reste à part (0,45 point de PIB en 2026,
0,17 en 2070, nette des reprises) ; une variante l'ajoute.

**Une seconde définition, plus large**, parce que le déficit dépend de la
convention qui range les recettes — la note du 7 novembre l'a montré pour la
décision 29 : tout ce que la retraite dépense et que les cotisations ne
paient pas, soit dépenses moins cotisations. Au droit actuel, 4,96 points de
PIB en 2026 : les impôts et taxes affectés (2,14), la contribution et les
subventions d'équilibre de l'État (1,88), les transferts (0,54), les autres
produits (0,23), le déficit (0,16) **(dépôt)**. À la proposition, 2,60 :
transferts (0,17), autres produits (0,23), déficit (2,19). C'est la seule
définition symétrique : la proposition a renoncé à 4,4 points de PIB de
recettes que le contribuable du droit actuel continue de payer, et la
première définition ne lui en fait pas crédit.

**L'année de départ est 2026**, comme les comptes de génération partent
d'une année de base : aucun déficit passé n'est réparti. **Au-delà de 2070**,
l'horizon du coût (`cout.HORIZON`), chaque grandeur garde sa part de PIB de
2070 ; c'est une convention de la session, favorable au droit actuel, dont le
déficit se creuse encore de 0,06 point par an en 2070 quand celui de la
proposition se referme de 0,1.

### 1.3. Qui le paie : l'impôt ou la dette

Trois bouclages, du plus dur pour les générations étudiées au plus doux.

- **L'impôt de l'année** (le calcul central). Le déficit de chaque année est
  payé cette année-là par ceux qui ont alors un revenu. C'est le levier que
  le COR chiffre lui-même en taux de prélèvement, et c'est ce que la
  proposition fait de son côté en affectant un point de LVT aux retraites
  (décision 80). Il met toute la charge sur les générations au travail entre
  2026 et 2070 : celles de l'étude.
- **L'impôt lissé.** Un prélèvement constant en part de PIB de 2026 à 2070,
  de même valeur actuelle que les déficits, au taux et à la croissance du
  coût : 0,99 point de PIB pour le droit actuel, 1,55 pour la proposition
  **(calcul)**. C'est la logique des indicateurs de soutenabilité, qui
  demandent un ajustement immédiat et permanent à tous (non relu ce jour,
  « Ce qui n'a pas été vérifié »).
- **La dette.** Tout est emprunté jusqu'en 2070, par la récurrence du coût
  (`cout.calculer_dette` : stock(t) = stock(t−1) × (1 + taux) ÷ (1 +
  croissance) − solde(t), de zéro fin 2025) : 66,0 points de PIB pour le
  droit actuel, 102,8 pour la proposition **(dépôt, refait)**. Après 2070,
  l'impôt stabilise la dette en part de PIB : stock × (taux − croissance) ÷
  (1 + croissance), plus le déficit de l'année, soit 66,0 × (3,82 % −
  1,94 %) ÷ 1,0194 + 2,39 = 3,61 points de PIB par an pour le droit actuel,
  et 102,8 × 1,844 % − 0,05 = 1,85 pour la proposition **(calcul)**. C'est le
  bouclage d'Auerbach, Gokhale et Kotlikoff, à ceci près qu'ils reportent
  tout sur les générations à naître.

### 1.4. Sur quelle assiette

- **Les salaires bruts** (le calcul central). Le COR rapporte lui-même les
  ressources de la retraite aux revenus d'activité : son taux de prélèvement
  est de 32,3 % en 2026 et de 30,0 % en 2070 **(dépôt,
  `taux_prelevement_retraite.csv`)**. L'assiette est celle sur laquelle la
  proposition prélève ses 18 % : 42,7 % du PIB en 2026, 43,0 % en 2070
  **(dépôt)**. Le déficit du COR y pèse 0,16 ÷ 42,74 = 0,38 point de salaire
  brut en 2026, 1,42 en 2040, 2,83 en 2050, 4,11 en 2060, 5,55 en 2070
  **(calcul)** ; celui de la caisse de la proposition, 5,13 points en 2026,
  4,47 en 2040, 4,11 en 2050, 2,26 en 2060, −0,11 en 2070. Les retraités ne
  paient rien.
- **Les salaires et les pensions**, comme la CSG : l'assiette est celle des
  salaires plus les pensions du système, 56,9 % du PIB en 2026 au droit
  actuel. Chacun paie le même taux sur son salaire puis sur sa pension ; les
  retraités de 2026 paient aussi.
- **Ce qui manque** : le profil par âge de chaque impôt, que les comptes de
  génération tirent d'enquêtes, et l'assiette foncière de la LVT, qui pèse
  sur ceux qui possèdent, plus âgés que la moyenne. Les deux assiettes
  retenues encadrent le salarié sans patrimoine ; elles ne disent rien du
  propriétaire.

### 1.5. Le calcul, posé

Pour une carrière, un système s et une convention, l'outil rend deux
chroniques en euros courants : les cotisations C(t), datées du milieu de
l'année, et les pensions espérées P(t), pondérées par la survie
(`fluxDesSystemes`, `pensionsEsperees`, `moteur/js/cycle-de-vie.js`). Son
rendement est le taux ρ qui annule Σ [P(t) − C(t)] ÷ I(t) × (1 + ρ)^−(t − t₀),
I étant l'indice des prix (rendement réel) ou du salaire moyen (rendement
relatif).

Le rendement net ajoute à ce que la carrière verse sa part de ce que les
contribuables paient pour le système s :

    T(t) = τ_s(t) × W(t)                 sur les salaires
    T(t) = τ_s(t) × [W(t) + P_brute(t)]  sur les salaires et les pensions
    τ_s(t) = payé_s(t) ÷ assiette_s(t)

où W(t) est le revenu d'activité brut de l'année (`Flux.revenus`), payé_s(t)
ce que le bouclage fait payer l'année t en part de PIB, et l'assiette, en
part de PIB aussi, celle du § 1.4. Le rendement net est le taux qui annule
Σ [P(t) − C(t) − T(t)] ÷ I(t) × (1 + ρ)^−(t − t₀). Comme les cotisations,
l'impôt des années de carrière n'est pas pondéré par la survie ; celui des
années de retraite l'est, comme la pension. Sans impôt, le calcul retrouve
l'outil à 10⁻¹² près sur les 72 chroniques de l'étude, en réel comme en
relatif.

Les carrières sont celles de la grille (`castypes.py`) : le SMIC à carrière
complète, le salaire moyen, le cadre, nés en 1960, 1970, 1980, 1990, 2000 et
2010, chacun à l'âge où le pilote le fait partir — 2064 au droit actuel et
2065 à la proposition pour le salarié moyen né en 2000. Les deux
conventions sont celles de `scripts/cycle_de_vie.py` : **celle du site** —
flux déflatés des prix, survie de la génération, pension brute — et **celle
du COR** (`--cor`) — flux rapportés au salaire moyen, deux sexes réunis,
décès à 60 ans plus l'espérance de vie à 60 ans, pension nette de ses
prélèvements.

## 2. Les comptes des deux systèmes

En points de PIB **(dépôt)**, sauf la dernière ligne **(calcul)**.

| | 2026 | 2030 | 2040 | 2050 | 2060 | 2070 | Moyenne 2026-2070 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Droit actuel : dépenses | 14,13 | 14,07 | 14,04 | 14,37 | 14,74 | 15,30 | |
| Droit actuel : déficit (COR) | 0,16 | 0,20 | 0,61 | 1,22 | 1,77 | 2,39 | 1,13 |
| Droit actuel : tout ce qui n'est pas cotisation | 4,96 | 4,97 | 5,23 | 5,74 | 6,23 | 6,83 | 5,71 |
| Proposition : dépenses | 10,29 | 10,00 | 10,06 | 9,90 | 9,09 | 8,07 | |
| Proposition : déficit de la caisse | 2,19 | 1,80 | 1,92 | 1,77 | 0,97 | −0,05 | 1,44 |
| Proposition : garantie vieillesse, nette | 0,45 | 0,40 | 0,27 | 0,18 | 0,17 | 0,17 | 0,25 |
| Proposition : tout ce qui n'est pas cotisation | 2,60 | 2,20 | 2,31 | 2,15 | 1,35 | 0,33 | 1,83 |
| Assiette des salaires bruts | 42,74 | 43,31 | 43,02 | 43,06 | 43,02 | 43,03 | |
| Tout ce qui n'est pas cotisation, en points de salaire brut : droit actuel, puis proposition | 11,61 ; 6,07 | 11,48 ; 5,08 | 12,15 ; 5,37 | 13,33 ; 4,99 | 14,48 ; 3,13 | 15,87 ; 0,76 | |

Le déficit de la caisse de la proposition dépasse celui du droit actuel
jusqu'en 2054 (1,54 contre 1,49 ; 1,46 contre 1,54 en 2055), et sa moyenne
sur 2026-2070 aussi. La feuille de route du programme le disait déjà au
chantier 1 : « le stock de dette qu'elle accumule d'ici 2070 dépasse celui
du système actuel ».

## 3. Un calcul en entier : le salarié moyen né en 2000, conventions du site

**Au droit actuel.** Ses cotisations de 2021 à 2064 valent 599 956 € de 2026,
ses pensions espérées 943 874 € **(dépôt)** : rendement 1,32 %. L'impôt du
déficit, de 2026 à 2064 : en 2040, 0,61 ÷ 43,02 = 1,42 % d'un salaire brut de
63 788 € courants, 904 € ; en 2060, 4,11 % de 109 823 €, 4 515 €. En tout,
46 150 € de 2026, soit 46 150 ÷ 599 956 = 7,7 % de ses cotisations
**(calcul)**. Rendement net : 1,13 %. Le contrôle de tête : alourdir la mise
de 7,7 % quand une quarantaine d'années séparent en moyenne une cotisation
de la pension qu'elle paie retire ln(1,077) ÷ 39 ≈ 0,19 point.

**À la proposition.** Cotisations 617 185 € de 2026, pilier compris ;
pensions espérées, rente du pilier comprise, 654 475 € **(dépôt)** :
rendement 0,17 %. L'impôt du déficit de la caisse, de 2026 à 2065 : 5,13 % du
brut en 2026, 4,47 % en 2040 (2 853 €), 2,26 % en 2060 (2 481 €) ; en tout
74 709 € de 2026, 12,1 % des cotisations **(calcul)**. Rendement net :
−0,16 %.

**Tout ce qui n'est pas cotisation.** Au droit actuel, 11,61 % du brut en
2026, 12,15 % en 2040, 14,48 % en 2060 : 254 996 € de 2026, 42,5 % des
cotisations ; rendement 0,30 %. À la proposition, 6,07 %, 5,37 % et 3,13 % :
92 792 €, 15,0 % ; rendement −0,24 % **(calcul)**.

**Le seuil.** Pour ramener son rendement au droit actuel à celui de la
proposition, il faudrait un prélèvement constant sur son salaire brut, dès
2026, de 14,8 points (6,4 points de PIB par an) si l'on vise le rendement de
l'outil, 0,17 %, et de 20,2 points (8,7 points de PIB) si l'on vise le
rendement net de la proposition, −0,16 % **(calcul)**. Le déficit du COR
culmine à 5,55 points de salaire en 2070.

## 4. Les résultats sous les conventions du site

Rendement réel, en pour cent par an. « Net » : déficit du COR pour le droit
actuel, de la caisse pour la proposition, payé chaque année par un impôt sur
les salaires bruts. Lignes « de l'outil » **(dépôt)**, les autres **(calcul)**.

| Né en | 1960 | 1970 | 1980 | 1990 | 2000 | 2010 |
|---|---:|---:|---:|---:|---:|---:|
| Au SMIC, droit actuel, de l'outil | 1,95 | 1,44 | 1,39 | 1,40 | 1,44 | 1,47 |
| Au SMIC, droit actuel, net | 1,95 | 1,43 | 1,36 | 1,33 | 1,29 | 1,22 |
| Au SMIC, proposition, de l'outil | 0,90 | 0,90 | 0,67 | 0,55 | 0,54 | 0,62 |
| Au SMIC, proposition, net | 0,90 | 0,82 | 0,50 | 0,29 | 0,24 | 0,35 |
| **Au SMIC, écart net** | **1,05** | **0,62** | **0,87** | **1,04** | **1,04** | **0,87** |
| Salaire moyen, droit actuel, de l'outil | 1,62 | 1,27 | 1,27 | 1,29 | 1,32 | 1,35 |
| Salaire moyen, droit actuel, net | 1,62 | 1,26 | 1,22 | 1,19 | 1,13 | 1,05 |
| Salaire moyen, proposition, de l'outil | 0,36 | 0,42 | 0,23 | 0,15 | 0,17 | 0,27 |
| Salaire moyen, proposition, net | 0,36 | 0,31 | 0,00 | −0,17 | −0,16 | 0,01 |
| **Salaire moyen, écart net** | **1,26** | **0,96** | **1,22** | **1,36** | **1,29** | **1,04** |
| Cadre, droit actuel, de l'outil | 0,83 | 0,52 | 0,48 | 0,47 | 0,46 | 0,44 |
| Cadre, droit actuel, net | 0,83 | 0,49 | 0,41 | 0,31 | 0,19 | 0,04 |
| Cadre, proposition, de l'outil | −0,10 | 0,09 | −0,04 | −0,08 | −0,01 | 0,10 |
| Cadre, proposition, net | −0,10 | −0,08 | −0,34 | −0,45 | −0,36 | −0,15 |
| **Cadre, écart net** | **0,93** | **0,57** | **0,75** | **0,76** | **0,55** | **0,19** |

L'écart ne se referme nulle part ; il se creuse là où la proposition paie
son propre déficit en pleine carrière, pour les générations 1970 à 2000. Il
ne se réduit que pour le salarié moyen et le cadre nés en 2010, qui
travaillent quand le déficit du COR est le plus haut et celui de la caisse
presque éteint : le cadre né en 2010 est à 0,19 point de l'inversion.

**Tout ce qui n'est pas cotisation**, impôt de l'année sur les salaires
**(calcul)** :

| Né en | 1960 | 1970 | 1980 | 1990 | 2000 | 2010 |
|---|---:|---:|---:|---:|---:|---:|
| Au SMIC, droit actuel | 1,95 | 1,30 | 1,00 | 0,78 | 0,57 | 0,41 |
| Au SMIC, proposition | 0,90 | 0,80 | 0,46 | 0,24 | 0,18 | 0,28 |
| **Au SMIC, écart** | **1,05** | **0,50** | **0,54** | **0,54** | **0,39** | **0,13** |
| Salaire moyen, droit actuel | 1,62 | 1,03 | 0,74 | 0,50 | 0,30 | 0,19 |
| Salaire moyen, proposition | 0,36 | 0,28 | −0,05 | −0,23 | −0,24 | −0,07 |
| **Salaire moyen, écart** | **1,26** | **0,74** | **0,79** | **0,73** | **0,54** | **0,27** |
| Cadre, droit actuel | 0,83 | 0,07 | −0,28 | −0,55 | −0,75 | −0,87 |
| Cadre, proposition | −0,10 | −0,12 | −0,40 | −0,53 | −0,45 | −0,23 |
| **Cadre, écart** | **0,93** | **0,19** | **0,12** | **−0,02** | **−0,30** | **−0,63** |

Ici seulement, la comparaison s'inverse, pour le cadre né à partir de 1990.
Le salarié moyen et le salarié au SMIC gardent un rendement plus haut au
droit actuel, de 0,4 à 0,5 point pour ceux nés en 2000, de 0,1 à 0,3 pour
ceux nés en 2010. Le salarié moyen né en 2000 y tombe à 0,30 % : c'est,
à l'arrondi, ce que la note du 8 novembre lisait au système 3 du site, le
compte notionnel qui crédite les cotisations du droit actuel (0,3 %). Les
deux chemins se rejoignent : ce que les cotisations paient, sans impôt ni
dette, est de cet ordre.

## 5. Les résultats sous les conventions du COR

Rendement relatif au salaire moyen, en pour cent par an ; mêmes lignes.

| Né en | 1960 | 1970 | 1980 | 1990 | 2000 | 2010 |
|---|---:|---:|---:|---:|---:|---:|
| Au SMIC, droit actuel, de l'outil | 1,27 | 0,69 | 0,61 | 0,60 | 0,59 | 0,61 |
| Au SMIC, droit actuel, net | 1,27 | 0,68 | 0,58 | 0,52 | 0,44 | 0,36 |
| Au SMIC, proposition, de l'outil | 0,21 | 0,06 | −0,19 | −0,34 | −0,37 | −0,28 |
| Au SMIC, proposition, net | 0,21 | −0,03 | −0,38 | −0,61 | −0,67 | −0,56 |
| **Au SMIC, écart net** | **1,07** | **0,71** | **0,96** | **1,13** | **1,11** | **0,91** |
| Salaire moyen, droit actuel, de l'outil | 0,88 | 0,47 | 0,45 | 0,44 | 0,44 | 0,47 |
| Salaire moyen, droit actuel, net | 0,88 | 0,46 | 0,40 | 0,33 | 0,24 | 0,15 |
| Salaire moyen, proposition, de l'outil | −0,42 | −0,45 | −0,66 | −0,78 | −0,76 | −0,66 |
| Salaire moyen, proposition, net | −0,42 | −0,58 | −0,91 | −1,11 | −1,11 | −0,93 |
| **Salaire moyen, écart net** | **1,30** | **1,04** | **1,31** | **1,44** | **1,35** | **1,08** |
| Cadre, droit actuel, de l'outil | −0,01 | −0,41 | −0,45 | −0,49 | −0,51 | −0,53 |
| Cadre, droit actuel, net | −0,01 | −0,43 | −0,53 | −0,66 | −0,80 | −0,95 |
| Cadre, proposition, de l'outil | −0,99 | −0,86 | −1,01 | −1,07 | −1,00 | −0,89 |
| Cadre, proposition, net | −0,99 | −1,06 | −1,35 | −1,48 | −1,37 | −1,14 |
| **Cadre, écart net** | **0,98** | **0,63** | **0,81** | **0,82** | **0,57** | **0,19** |

**Tout ce qui n'est pas cotisation**, impôt de l'année sur les salaires
**(calcul)** :

| Né en | 1960 | 1970 | 1980 | 1990 | 2000 | 2010 |
|---|---:|---:|---:|---:|---:|---:|
| Au SMIC, droit actuel | 1,27 | 0,53 | 0,20 | −0,06 | −0,30 | −0,47 |
| Au SMIC, proposition | 0,21 | −0,05 | −0,42 | −0,67 | −0,74 | −0,63 |
| **Au SMIC, écart** | **1,07** | **0,59** | **0,62** | **0,61** | **0,44** | **0,16** |
| Salaire moyen, droit actuel | 0,88 | 0,21 | −0,12 | −0,40 | −0,62 | −0,73 |
| Salaire moyen, proposition | −0,42 | −0,60 | −0,96 | −1,18 | −1,19 | −1,01 |
| **Salaire moyen, écart** | **1,30** | **0,81** | **0,85** | **0,79** | **0,57** | **0,29** |
| Cadre, droit actuel | −0,01 | −0,90 | −1,30 | −1,59 | −1,79 | −1,90 |
| Cadre, proposition | −0,99 | −1,10 | −1,41 | −1,56 | −1,46 | −1,23 |
| **Cadre, écart** | **0,98** | **0,20** | **0,12** | **−0,03** | **−0,32** | **−0,68** |

Les niveaux sont plus bas de 0,7 à 1,0 point, les écarts sont les mêmes à
quelques centièmes : la convention déplace les deux systèmes ensemble. Net
du déficit, la proposition est sous zéro pour les trois carrières dès la
génération 1970, et le droit actuel pour le seul cadre. En réel sous les
mêmes conventions, le salarié moyen né en 2000 passe de 1,13 à 0,93 % au
droit actuel et de −0,08 à −0,43 % à la proposition **(calcul)**.

## 6. Les variantes : qui paie, sur quoi

Le salarié moyen, droit actuel puis proposition **(calcul)** ; les
conventions du site d'abord, celles du COR ensuite.

| Conventions du site, réel | 1960 | 1970 | 1980 | 1990 | 2000 | 2010 |
|---|---:|---:|---:|---:|---:|---:|
| L'outil, sans impôt | 1,62 ; 0,36 | 1,27 ; 0,42 | 1,27 ; 0,23 | 1,29 ; 0,15 | 1,32 ; 0,17 | 1,35 ; 0,27 |
| Impôt de l'année, sur les salaires (central) | 1,62 ; 0,36 | 1,26 ; 0,31 | 1,22 ; 0,00 | 1,19 ; −0,17 | 1,13 ; −0,16 | 1,05 ; 0,01 |
| Impôt de l'année, sur les salaires et les pensions | 1,59 ; 0,26 | 1,21 ; 0,23 | 1,15 ; −0,02 | 1,11 ; −0,13 | 1,05 ; −0,10 | 1,00 ; 0,06 |
| Impôt lissé, sur les salaires | 1,62 ; 0,36 | 1,23 ; 0,33 | 1,16 ; 0,04 | 1,14 ; −0,12 | 1,12 ; −0,16 | 1,10 ; −0,04 |
| Impôt lissé, sur les salaires et les pensions | 1,57 ; 0,28 | 1,18 ; 0,25 | 1,13 ; −0,00 | 1,10 ; −0,12 | 1,06 ; −0,12 | 1,04 ; 0,02 |
| Dette jusqu'en 2070, puis impôt sur les salaires | 1,62 ; 0,36 | 1,27 ; 0,42 | 1,27 ; 0,23 | 1,29 ; 0,15 | 1,32 ; 0,17 | 1,29 ; 0,22 |
| Dette jusqu'en 2070, puis impôt sur les salaires et les pensions | 1,62 ; 0,36 | 1,27 ; 0,42 | 1,25 ; 0,22 | 1,23 ; 0,11 | 1,19 ; 0,09 | 1,12 ; 0,12 |
| Impôt de l'année sur les salaires, garantie comptée | 1,62 ; 0,36 | 1,26 ; 0,28 | 1,22 ; −0,04 | 1,19 ; −0,21 | 1,13 ; −0,21 | 1,05 ; −0,04 |
| Tout ce qui n'est pas cotisation, sur les salaires | 1,62 ; 0,36 | 1,03 ; 0,28 | 0,74 ; −0,05 | 0,50 ; −0,23 | 0,30 ; −0,24 | 0,19 ; −0,07 |
| Tout ce qui n'est pas cotisation, sur les salaires et les pensions | 1,37 ; 0,24 | 0,76 ; 0,19 | 0,52 ; −0,08 | 0,32 ; −0,21 | 0,16 ; −0,19 | 0,09 ; −0,03 |

| Conventions du COR, relatif au salaire moyen | 1960 | 1970 | 1980 | 1990 | 2000 | 2010 |
|---|---:|---:|---:|---:|---:|---:|
| L'outil, sans impôt | 0,88 ; −0,42 | 0,47 ; −0,45 | 0,45 ; −0,66 | 0,44 ; −0,78 | 0,44 ; −0,76 | 0,47 ; −0,66 |
| Impôt de l'année, sur les salaires (central) | 0,88 ; −0,42 | 0,46 ; −0,58 | 0,40 ; −0,91 | 0,33 ; −1,11 | 0,24 ; −1,11 | 0,15 ; −0,93 |
| Impôt de l'année, sur les salaires et les pensions | 0,86 ; −0,54 | 0,41 ; −0,68 | 0,32 ; −0,95 | 0,23 ; −1,08 | 0,15 ; −1,05 | 0,09 ; −0,88 |
| Impôt lissé, sur les salaires | 0,88 ; −0,42 | 0,42 ; −0,55 | 0,33 ; −0,87 | 0,27 ; −1,06 | 0,23 ; −1,11 | 0,21 ; −0,98 |
| Impôt lissé, sur les salaires et les pensions | 0,83 ; −0,52 | 0,37 ; −0,64 | 0,30 ; −0,94 | 0,23 ; −1,08 | 0,17 ; −1,07 | 0,14 ; −0,92 |
| Dette jusqu'en 2070, puis impôt sur les salaires | 0,88 ; −0,42 | 0,47 ; −0,45 | 0,45 ; −0,66 | 0,44 ; −0,78 | 0,44 ; −0,76 | 0,40 ; −0,71 |
| Dette jusqu'en 2070, puis impôt sur les salaires et les pensions | 0,88 ; −0,42 | 0,47 ; −0,45 | 0,45 ; −0,66 | 0,37 ; −0,82 | 0,29 ; −0,86 | 0,21 ; −0,83 |
| Impôt de l'année sur les salaires, garantie comptée | 0,88 ; −0,42 | 0,46 ; −0,60 | 0,40 ; −0,95 | 0,33 ; −1,16 | 0,24 ; −1,16 | 0,15 ; −0,98 |
| Tout ce qui n'est pas cotisation, sur les salaires | 0,88 ; −0,42 | 0,21 ; −0,60 | −0,12 ; −0,96 | −0,40 ; −1,18 | −0,62 ; −1,19 | −0,73 ; −1,01 |
| Tout ce qui n'est pas cotisation, sur les salaires et les pensions | 0,59 ; −0,56 | −0,10 ; −0,73 | −0,38 ; −1,02 | −0,63 ; −1,16 | −0,81 ; −1,14 | −0,88 ; −0,97 |

Ce que les variantes montrent.

- **L'assiette compte peu** : élargie aux pensions, elle retire 0,05 à
  0,08 point de plus au droit actuel des générations jeunes, et fait payer
  les retraités d'aujourd'hui (la génération 1960 perd 0,03 point au droit
  actuel, 0,10 à la proposition, dont le déficit est immédiat).
- **Le lissage déplace la charge vers les générations 1970 à 1990**, sans
  changer l'ordre.
- **La dette efface tout pour les générations étudiées.** Sur les salaires,
  aucune de celles nées de 1960 à 2000 ne paie ; celle de 2010 paie quatre
  à cinq ans. La phrase « la même génération paiera » est donc fausse si le déficit
  s'emprunte : ce sont les suivantes qui paient, 3,61 points de PIB par an au
  droit actuel, 1,85 à la proposition telle que le modèle la chiffre.
- **Compter la garantie** au déficit de la proposition lui retire encore
  0,03 à 0,05 point.

## 7. Ce que le programme peut affirmer sans être démenti

**Ce qui ne tient pas.**

- « Net du déficit, la proposition rend plus que le droit actuel » : faux
  pour les trois carrières et les six générations, sous les deux
  conventions, avec le déficit du COR.
- « Le 1,3 % est une promesse que la même génération paiera » : vrai pour un
  cinquième de point seulement si elle le paie en impôt (1,32 → 1,13), et
  faux si le déficit s'emprunte.
- « Nous vous servons 0,2 %, payés » (option A de la note du 8 novembre) :
  la caisse de la proposition, au modèle, est en déficit de 2026 à 2069. Ses
  0,2 % ne sont « payés » qu'avec la LVT et la part de TVA des décisions 79 à
  81, qui ne sont pas au modèle — et la LVT est un impôt, que les mêmes
  générations paient selon ce qu'elles possèdent.

**Ce qui tient**, chaque phrase avec sa convention.

1. *La promesse non financée, à sa mesure.* « Le système actuel promet à un
   salarié moyen né en 2000 un rendement de 1,3 % par an au-dessus de
   l'inflation. Le COR projette qu'il manquera 2,4 points de PIB par an en
   2070 pour le servir. Si ce salarié le paie par ses impôts, il lui en
   coûtera 46 000 € d'aujourd'hui sur sa carrière, et son rendement tombe à
   1,1 %. » (dépôt et calcul, conventions du site, impôt de l'année sur les
   salaires.)
2. *Ce que les cotisations paient vraiment.* « Plus du tiers de ce que
   la retraite dépense n'est pas payé par les cotisations : 5 points de PIB
   en 2026, près de 7 en 2070. Comptés dans la mise, ces impôts ramènent le
   rendement du même salarié à 0,3 %, et celui d'un cadre sous zéro. »
   (4,96 ÷ 14,13 = 35 % ; 6,83 ÷ 15,30 = 45 % en 2070.) La convention est à
   dire : elle met à la charge du salarié du privé des impôts qui paient
   aussi les pensions des fonctionnaires et la solidarité.
3. *La facture hors cotisations, et sa pente.* « Au droit actuel, ce qui
   n'est pas cotisation coûte l'équivalent de 11,6 points de salaire brut en
   2026 et de 15,9 en 2070. À la proposition, 6,1 puis 0,8. » C'est
   l'affirmation la plus solide : elle ne dépend ni du rendement, ni de la
   survie, ni du bouclage, seulement des comptes du COR et de la page Coût.
4. *La dette, à condition de la LVT.* « Emprunté, le déficit des retraites
   fait 66 points de PIB de dette en 2070 ; il en coûtera ensuite 3,6 points
   de PIB par an à ceux qui travailleront. » Mais le modèle donne 103 points
   à la proposition sans la LVT : la phrase ne se dit qu'une fois la LVT et
   la TVA au modèle (1 point de dette en 2070 selon le chiffrage du
   8 novembre, hors modèle).
5. *L'écart entre carrières.* Entre le SMIC et le cadre nés en 2000, l'outil
   donne 0,97 point d'écart au droit actuel et 0,54 à la proposition
   (dépôt) ; net du déficit, 1,10 et 0,61 (calcul). C'est le fil de
   l'option B de la note du 8 novembre, et le déficit le renforce.
6. *Le cadre, tout compté.* « Pour un cadre né après 1990, tout compté, la
   proposition rend plus que le droit actuel. » Vrai sous la seule
   convention large (−0,75 contre −0,45 pour celui né en 2000) ; les deux
   rendements y sont négatifs.

**Pour le chantier 9.** L'option C de la note du 8 novembre, « compter
l'impôt dans la mise », est maintenant chiffrée pour les trois carrières du
privé, et elle ne sauve pas la comparaison des niveaux. La piste de cette
note-là — B en tête, A où les niveaux se comparent — tient donc, avec trois
corrections à A : « promis 1,3 % ; 1,1 % une fois le déficit payé ; 0,3 %
une fois comptés les impôts » remplace « ses cotisations en paient 0,3 % » ;
« le reste viendra de vos impôts ou de vos enfants » devient exact, les
impôts pour la part déjà payée, les enfants pour le déficit s'il
s'emprunte ; et « payés » attend la LVT.

## Limites

- **La proposition est le scénario 6 du modèle**, à 18 % dès 2026, pilier de
  dix points, sans la LVT ni la part de TVA (décisions 79 à 81), sans le
  choix entre les lectures A et B de la décision 29, sans la baisse par
  cinquièmes. Chacune change le déficit de sa caisse, donc son rendement
  net.
- **Trois carrières du privé**, à carrière complète. Ni fonctionnaire, ni
  indépendant, ni carrière heurtée : le rendement net d'un fonctionnaire,
  dont l'État paie la surcotisation, serait un autre calcul.
- **L'incidence** : l'impôt est proportionnel au salaire brut, ou au salaire
  et à la pension. Aucun profil par âge, aucune assiette foncière.
- **Le SMIC, sous la convention large**, est compté deux fois pour une
  part : l'outil lui prête des cotisations au taux plein (27,9 % du brut),
  alors que les allègements en retirent une partie que des impôts affectés
  compensent, comptés à nouveau dans « ce qui n'est pas cotisation ».
- **Après 2070**, tout est tenu à sa part de PIB de 2070 ; un excédent de la
  caisse y devient un impôt négatif (−0,05 point de PIB).
- **Le minimum vieillesse et la garantie** ne sont pas dans ce qui est reçu ;
  le minimum vieillesse est dans les comptes du COR, la garantie à part.
- **Aucun comportement ne change**, et les taux d'intérêt et de croissance
  sont ceux du coût (3,82 % et 1,94 % en 2070).

## Ce qui n'a pas été vérifié

- Le corps du chapitre de 1991 n'a pas pu être lu (PDF en images) : seuls
  son résumé et celui de l'article de 1994 l'ont été. Ses pages (55-110, de
  mémoire) et son hypothèse d'incidence — chaque impôt porté par qui le
  verse — restent à relire.
- La variante où l'ajustement pèse tout de suite sur toutes les générations,
  vivantes comprises (Raffelhüschen, 1999, *American Economic Review* 89(2) ;
  Commission européenne, *Generational accounting in Europe*, 1999), et
  l'indicateur S2 de la Commission : cités de mémoire, non atteints ce jour.
- Le texte du rapport du COR sur ses leviers d'équilibre : seules ses séries,
  certifiées au dépôt, ont servi.
- Aucune des générations d'après 2010, ni l'au-delà de 2070 : le coût
  s'arrête là.

## Sources lues ce jour

- A. Auerbach, J. Gokhale et L. Kotlikoff, « Generational Accounts: A
  Meaningful Alternative to Deficit Accounting », dans D. Bradford (dir.),
  *Tax Policy and the Economy*, vol. 5, MIT Press, 1991, chap. 3 (NBER
  Working Paper 3589, janvier 1991), résumé :
  https://www.nber.org/books-and-chapters/tax-policy-and-economy-volume-5/generational-accounts-meaningful-alternative-deficit-accounting
  et https://www.nber.org/papers/w3589
- Les mêmes, « Generational Accounting: A Meaningful Way to Evaluate Fiscal
  Policy », *Journal of Economic Perspectives*, vol. 8, n° 1, hiver 1994,
  p. 73-94, résumé : https://www.aeaweb.org/articles?id=10.1257/jep.8.1.73
- Au dépôt, sans relecture de la source ce jour : COR, rapport annuel de
  juin 2026, classeurs de données (`data/sources.yaml`,
  `cor_comptes_systeme_retraite`) ; `docs/feuille_de_route_programme.md`,
  chantier 1 ; les notes `2026-11-07-chiffres-qui-tiennent.md`,
  `2026-11-07-deux-lectures-au-modele.md` et `2026-11-08-site-etude.md`.

## Ce que le propriétaire tranche

1. **L'argument.** Renoncer à « net du déficit, la proposition rend plus » :
   il est faux au modèle, sous les deux conventions. La note le propose.
2. **La phrase sur la promesse non financée.** La mesure courte (« 1,3 %
   promis, 1,1 % une fois le déficit payé »), la mesure large (« 0,3 % une
   fois comptés les impôts »), ou les trois nombres ensemble — ce que la
   note propose, avec la convention large dite pour ce qu'elle est.
3. **L'affirmation de tête.** La facture hors cotisations, 11,6 points de
   salaire brut aujourd'hui et 15,9 en 2070 contre 6,1 puis 0,8, peut-elle
   prendre la place du rendement dans le message ? Elle tient sans
   convention de rendement, mais elle compte comme une charge des impôts que
   le programme garde en partie (la TVA, décision 79).
4. **Le déficit de la proposition.** Tant que la LVT et la TVA ne sont pas
   au modèle, sa caisse y emprunte plus que le droit actuel, et aucun
   « payé » ne se dit. Faut-il une session du modèle sur ces recettes avant
   toute page sur le rendement ?
5. **Le chantier 9.** L'option C est chiffrée et ne change pas l'ordre :
   garder B en tête et A corrigée (« 7. »), ou une autre voie ?
6. **La suite du calcul.** Le garder comme une étude, ou en faire un script
   du dépôt, testé, dont la convention se publie à la page Méthode
   (décision 84) — et l'étendre alors aux fonctionnaires, aux générations
   d'après 2010 et à l'au-delà de 2070, ce qui demande d'allonger le coût ?
