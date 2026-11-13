# La réserve personnelle, non transmise aux héritiers : ce qu'elle paie, et ce qu'elle devient au décès

**Reprise, au 13 novembre 2026.** Le propriétaire a tranché : la prime est de
1 % (décision 107) ; ce qui reste au décès va aux retraités de sa génération,
et leur est rendu quand la crise ne peut plus rien leur coûter (décision 133)
; la réserve porte sur toutes les pensions, celles à venir comprises (décision
138). Ce dernier point n'est pas chiffré : une session d'étude le chiffre
d'abord, puis une session du modèle en fait le réglage par défaut de la
proposition.

*Le 8 novembre 2026, action 186, chantier 5. Le propriétaire veut « une
faible contribution durable pour amortir un choc passager », « 1 % tout le
temps », et « une solution où personne ne se sentirait flouée » ; il a
demandé si ce pouvait être « une réserve personnelle en plus du compte
notionnel », puis : « Étudie la réserve personnelle, non transmise aux
héritiers au décès ». Les chiffres sont ceux de `main` au commit `5e14b99`,
pour le seul stock — les pensions servies à la bascule —, de 2026 à 2070,
sous le scénario de référence du COR et les deux chocs de l'étude.*

## Le mécanisme

- Chaque retraité du stock a une réserve à son nom, à côté de sa pension.
  1 % de sa pension y entre chaque année, retenu sur elle (décision 73), et
  la réserve se place au taux de la masse salariale, comme le compte et la
  dette du plancher (décisions 10 et 46).
- Quand la règle de la décision 41 passe sous sa pension, le plancher
  (décision 44) lui sert l'écart, et c'est sa réserve qui le paie. Vide,
  l'écart devient sa dette, reprise sur ses hausses (décisions 46, 49 et
  76), et perdue s'il meurt avant de l'avoir rendue (décision 77).
- À son décès, rien ne va à ses héritiers.

Deux questions restent, que le calcul sépare : **ce que devient ce qui reste
au décès** — aux autres retraités, comme en Suède, ou hors du stock, au
système ; et **si la réserve se rend de son vivant** — son surplus au-delà de
ce que le plancher peut encore lui coûter, versé en supplément de pension
(décision 75), ou jamais.

## Ce que font les textes

- **La Suède redistribue le compte des morts à leur génération.** Le code de
  la sécurité sociale suédois (Socialförsäkringsbalken 2010:110, chapitre
  62, « Pensionsbehållningar för personer som har avlidit (arvsvinster) »,
  § 9) donne le compte d'un assuré mort aux assurés nés la même année, vivants
  à la fin de l'année du décès et titulaires d'une pension de revenu, par un
  recalcul annuel de leurs comptes, au moyen de facteurs (§ 14 à 16), les
  mêmes pour les femmes et les hommes (§ 11). Lu sur riksdagen.se le
  8 novembre 2026, texte à jour de la SFS 2026:1658. Le texte lu ne dit pas
  où le mécanisme s'arrête ; après le départ, la mortalité passe par le
  diviseur de la rente (chapitre 56, chapitre 62 § 28 à 37, non lus). La
  pension par capitalisation (chapitre 64) n'a pas ce mécanisme dans les
  paragraphes lus.
- **En France**, une pension de vieillesse est cessible et saisissable
  « dans les mêmes conditions et limites que les salaires » (CSS, art.
  L. 355-2, lu dans l'index LEGI au 2 novembre 2026) : un revenu, non un
  capital. Une réserve retenue sur la pension et non transmise reste donc
  dans la logique d'une pension ; qu'elle relève de la loi, au titre des
  principes fondamentaux de la sécurité sociale (Constitution, art. 34), est
  écrit de mémoire, non vérifié.
- **Le compte de la proposition**, pour un actif mort, disait « vos
  cotisations restent au système » ; la décision 22 en sert la moitié au
  conjoint.

## Les chiffres

Six variantes : la contribution de 1 %, jamais rendue, ou son surplus rendu
« au seuil » quand la réserve seule dépasse ce que le plancher peut encore
coûter, mesuré sous la crise et l'inflation basse, la crise à ses dates ou
recommencée ; au décès, aux survivants du stock (« en commun ») ou hors du
stock (« à soi »). « Le stock face à α = 1 » : ce que le stock touche de
plus que α = 1 sans plancher sur sa vie, en valeur actuelle. La réserve d'un
retraité vivant, en années de sa pension ; la prime, négative quand la
réserve se rend en supplément.

**Sans choc (COR).**

| Variante | Le stock face à α = 1 | Les cotisants | Réserve d'un retraité, 2040 | 2050 | Prime 2040 | 2050 | 2060 |
|---|---|---|---|---|---|---|---|
| Jamais rendue, en commun | −1,0 % | gagnent 0,03 point de PIB par an | 0,25 | 0,96 | 1,00 | 1,00 | 1,00 |
| Jamais rendue, à soi | −1,0 % | gagnent 0,03 | 0,17 | 0,30 | 1,00 | 1,00 | 1,00 |
| Rendue (crise à ses dates), en commun | 0,0 % | 0 | 0,14 | 0,15 | −1,10 | −2,51 | −4,32 |
| Rendue (crise à ses dates), à soi | −0,4 % | gagnent 0,01 | 0,09 | 0,03 | −0,67 | −0,67 | −0,67 |
| Rendue (crise recommencée), en commun | 0,0 % | 0 | 0,23 | 0,26 | −0,34 | −4,59 | −8,47 |
| Rendue (crise recommencée), à soi | −0,6 % | gagnent 0,02 | 0,17 | 0,11 | 1,00 | −1,30 | −1,42 |

À soi et rendue, la réserve d'un retraité s'épuise s'il vit plus longtemps
que prévu : une dette de 0,7 % d'une année de pension en 2057 (crise à ses
dates), de 1,4 % en 2063 (recommencée), sans choc.

**Sous un choc**, la plus forte dette d'un retraité du stock, en part d'une
année de pension. Rendue ou non, c'est la même : la réserve ne dépasse jamais
ce que le plancher peut encore coûter.

| Choc | En commun | À soi | Le stock face à α = 1 | Les cotisants |
|---|---|---|---|---|
| Inflation durable de 0,5 % | 41 % (2070) | 100 % (2070) | 0,0 % | 0 |
| Crise de l'emploi | 54 % (2057) | 57 % (2057) | +1,2 % | paient 0,03 point de PIB par an |

## Ce que le calcul apprend

1. **Jamais rendue, la réserve est une baisse de 1 %.** Sans choc, le stock
   perd 1 % de sa pension sa vie durant, que personne ne lui rend : les
   cotisants en gagnent 0,03 point de PIB par an. C'est le sentiment d'être
   floué que le propriétaire veut éviter.
2. **Rendue de son vivant, et ce que laissent les morts aux survivants,
   personne ne perd en moyenne.** Sans choc, le stock retrouve sur sa vie
   tout ce qu'il a versé : chacun reçoit, en espérance, ce qu'il a payé. Ceux
   qui meurent tôt laissent à ceux qui vivent longtemps : c'est le principe
   d'une pension viagère, et celui de la Suède pour les comptes des morts
   avant leur départ.
3. **Rendue de son vivant sans mise en commun, elle laisse chacun face au
   risque de vivre longtemps.** Ce que laissent les morts sort du stock (il
   perd 0,4 à 0,6 % sur sa vie, au profit des cotisants), et un supplément
   calculé sur l'espérance de vie s'épuise chez ceux qui la dépassent. Une
   réserve à soi ne se rend sans risque que lentement, en supposant chacun
   centenaire : il reste alors beaucoup au décès, qui sort du stock.
4. **Contre un choc commun, la mise en commun aide peu, et 1 % ne suffit
   pas.** La même règle vaut pour tout le stock : un choc le frappe tout
   entier, et les réserves des morts ne compensent qu'en partie (54 % contre
   57 % d'une année de pension sous la crise). Sous un choc durable, elles
   comptent davantage (41 % contre 100 %). Sous la crise étudiée, la dette du
   stock monte à la moitié d'une année de pension, et les cotisants paient
   0,03 point de PIB par an de dettes perdues ; la prime de 2,15 % la couvrait
   (note `2026-11-08-indexation-voie-1-au-modele.md`).
5. **Le modèle met en commun le stock entier**, toutes générations, ses
   pensions suivant toutes la même règle ; la Suède met en commun par année de
   naissance. Une mise en commun par génération n'est pas chiffrée.

## Ce qui revient au propriétaire

1. **Ce qui reste au décès** : aux autres retraités — de sa génération,
   comme en Suède, ou du stock entier —, ou hors du stock, au système.
2. **La réserve rendue de son vivant ou non** ; rendue, quand : quand la
   crise assurée, à ses dates ou recommencée, ne peut plus rien lui coûter.
3. **Le taux** : 1 % ne couvre pas la crise étudiée ; 2,15 % la couvrait.
4. **L'assiette** : le stock seul, ou aussi les pensions nouvelles, dont le
   plancher se paie aujourd'hui par leur dette (décision 46) ; pas chiffré.

## Ce qui reste à faire

- Écrire ses réponses en décisions, sous le chantier 5, après relecture
  d'`origin/main` pour le numéro.
- Au modèle, selon ses réponses : la mise en commun par génération, les
  pensions nouvelles, puis le défaut du scénario 6 et la page Coût.
- Lire, en Suède, ce que deviennent les gains de mortalité après le départ
  (chapitre 56 ; chapitre 62, § 28 à 37).
