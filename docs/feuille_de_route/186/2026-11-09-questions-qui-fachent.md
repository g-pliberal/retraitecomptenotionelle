# Les questions qui fâchent : dix réponses proposées, et ce que chacune a de faible

*Le 9 novembre 2026, le propriétaire demande, pour la version publique du
programme (action 186, chantier 9), les questions qu'un adversaire ou un
journaliste posera, rédigées avant lui : la réponse en cinq lignes au plus,
chaque chiffre renvoyé à sa source dans le dépôt, et une ligne quand la
réponse est faible. Il en nomme neuf ; la note en propose une dixième, sur
les mères. Aucune page n'est touchée : une session du site y travaille
(action 189). Le texte est ici, il se propose, et le propriétaire tranche.*

Les réponses sont écrites pour l'électeur, à la deuxième personne, comme le
site. Les sources, elles, sont pour qui relira : une décision se cite par son
numéro (`docs/feuille_de_route_programme.md`, « Ce qui est décidé »), une
note par son fichier sous `docs/feuille_de_route/186/`.

## Ce que le site a déjà

La page « Les questions qui fâchent », prévue le 6 novembre et reprise par
l'étude du site (`2026-11-08-site-etude.md`, « 2. »), n'existe pas. L'accueil
porte une section « Vos questions », de treize questions dépliables
(`index.html`, sous `<h2>Vos questions</h2>`). Quatre recoupent celles-ci :

- « Ma retraite va-t-elle baisser ? », où la décision 90 envoie dire la
  baisse. Sa réponse d'aujourd'hui : « de l'ordre d'un quart », 26 % en
  médiane pour qui n'est pas à la retraite, 14 % s'il place les 5 %, 28 %
  pour un retraité, sur les treize carrières types ;
- « À quel âge pourrai-je partir ? » : « C'est vous qui choisissez, à partir
  de 65 ans », ce que la décision 68 ne veut plus dire (« le message est
  celui de 65 ans, pas la liberté de l'âge ») ;
- « Mon argent sera-t-il placé en Bourse ? » : « Non », en titres d'État ;
- « Combien cela coûte-t-il, et qui paie ? », qui renvoie à la page Coût.

Les six autres n'ont de réponse nulle part sur le site : le rendement des
jeunes, la maison, le juge, les cadres, la Pologne, les mères. La reprise sur
la succession y est dite en une phrase, à deux endroits, sans sa règle.

## Les dix questions

### 1. Ma retraite va-t-elle baisser ?

> Oui, le plus souvent. Chaque pension vaut ce qui a été cotisé : ce que le
> système ajoutait sans cotisation n'est plus servi. Sur nos treize carrières
> types, la pension d'un retraité baisse de 28 % en médiane, par cinquièmes
> de 2026 à 2030. Personne ne vit sous 1 050 € par mois à 65 ans (800 €
> chacun en couple), et les réversions déjà servies sont gardées.

- La phrase et la règle : décisions 90, 1 et 2. Le calendrier, « un
  cinquième en 2026, la baisse entière en 2030 » : décisions 3 et 87.
- 28 % : `index.html`, « Ma retraite va-t-elle baisser ? » (« 28 % sur la
  pension d'un retraité d'aujourd'hui, garantie vieillesse comprise »).
- 1 050 € et 800 € : décision 65. Les réversions : décision 16 (4,4 millions
  de survivants, `2026-11-07-message-etude.md`, « Les retraités »).

**Au propriétaire : la réponse est faible.** Les 28 % viennent de treize cas
et d'une grille « qui ne suit pas encore toutes les décisions »
(décision 90), pas d'un compte des retraités : qui perd, et combien, par tranche de pension, reste à
mesurer (chantier 2), comme le nombre de pensions qui montent (décision 90).
Et la quatrième promesse, « votre pension ne baissera jamais en euros »
(décision 45), se lira contre cette réponse si elle ne dit pas « une fois
recalculée ».

### 2. Pourquoi 65 ans ?

> Parce que c'est à cet âge que la réforme se paie. Laisser partir à 62 ans
> coûterait 0,22 point de PIB de plus chaque année jusqu'en 2070 ; à 64 ans,
> 0,13 ; et la caisse ne retrouve l'équilibre en 2070 qu'à 65 ans. C'est le
> même âge pour tous, sans régime à part. Qui est invalide touche la garantie
> sans attendre 65 ans.

- 0,22, 0,13 et l'équilibre de 2070 : `2026-11-07-age-plancher.md`, le
  tableau et le paragraphe qui le suit (modèle, variante rétroactive).
- L'âge et le message : décision 68. L'invalidité : décision 78, dont la
  vérification caisse par caisse n'est pas close.

**Au propriétaire : la réponse est faible.** Elle est budgétaire, et ne dit
rien à celui qu'elle touche : le salarié au SMIC en carrière longue, qui part
aujourd'hui à 61 ans ¾ ou 62 ans et attendrait trois ans (même note, « Ce qui
fait l'écart »), sans critère de pénibilité (décision 8). La seule réponse de
justice que le dépôt tienne est la table de mortalité par niveau de vie
(question 6), qui n'avance pas son départ.

### 3. Les jeunes y perdent-ils ?

> En apparence, oui : au salarié moyen né en 2000, le système actuel promet
> 1,3 % par an au-dessus des prix, et nous 0,2 %. Mais ses cotisations n'en
> paient que 0,3 % : le reste est une promesse sans recettes, un déficit de
> 2,4 points de PIB en 2070. Ce que nous servons est payé. Et le salarié
> moyen né en 1990 gagne 186 € nets par mois dès la bascule.

- 1,3 %, 0,2 %, 0,3 % et les 2,4 points : `2026-11-08-site-etude.md`,
  « 3. », le tableau et « D'où vient l'écart » (modèle,
  `python scripts/cycle_de_vie.py --indicateurs rendement_reel`).
- 186 € : programme, chantier 1, « Le 7 novembre 2026, les deux lectures sur
  la base de la page Coût », colonne « Programme, 18 % ».

**Au propriétaire : la réponse est faible.** Sous les conventions du COR, la
proposition rend −0,1 % au salarié moyen né en 1990 ou 2000 (même note) : le
« TRI négatif » que la décision 84 retire au droit actuel se retourne contre
nous. Le même tableau qui donne les 186 € donne la pension de 2055, 1 531 €
contre 2 859 € promis ; et « payé » repose sur une convention du site. Des
quatre façons de montrer le rendement, aucune n'est choisie.

### 4. L'État reprend-il ma maison ?

> Non : il n'y a aucun impôt nouveau sur l'héritage. Seule la garantie
> vieillesse se rembourse, parce que c'est une avance. Au décès, l'État
> reprend ce qu'il a versé, avec intérêts, sur ce que la succession contient,
> et jamais au-delà : les héritiers ne paient rien de leur poche. Qui n'a pas
> touché la garantie ne doit rien.

- L'héritage : décision 5. L'avance et sa limite : décision 30 ;
  `2026-11-07-deux-lectures-et-reprise.md`, « La reprise sur succession » ;
  `docs/methodologie.md`, « La seconde chose qu'elle change : c'est une
  avance ».

**Au propriétaire : la réponse est faible.** Pour un petit propriétaire qui a
touché la garantie, la réponse vraie est « oui, en partie ». La reprise est
plus dure que celle de l'ASPA : dès le premier euro et avec intérêts, quand
l'ASPA ne reprend qu'au-delà de 108 585,14 € d'actif net en 2026 et dans la
limite de 8 463,42 € par année servie
(`data/reference/regles/minimum_vieillesse.yaml`, « approximations ») ; sans
rien épargner (décision 66) ; et sur une garantie servie d'office
(décision 20), donc sans que l'intéressé l'ait demandée. 220 Md€ repris de
2026 à 2070 (`docs/chiffrage_plf.md`).

### 5. Une loi rétroactive est-elle constitutionnelle ?

> Nul ne peut le promettre : le Conseil constitutionnel n'a jamais jugé une
> baisse en euros de pensions déjà liquidées. La Cour européenne en a admis en
> Grèce et au Portugal, en 2013, tant que la subsistance n'est pas menacée.
> La nôtre ne retire que la part non cotisée, en cinq ans, avec un plancher
> de 1 050 €. Nous la défendrons devant les deux juges.

- Le Conseil constitutionnel (2014-698 DC et 2019-795 DC, des
  sous-revalorisations d'un an) : `2026-11-07-indexation-etude.md`, « Le
  droit ».
- La CEDH (*Koufaki et Adedy*, 7 mai 2013 ; *Da Conceição Mateus*, 8 octobre
  2013) : `2026-11-07-chiffres-qui-tiennent.md`, « 3. ».
- La part non cotisée, les cinq ans, le plancher, les deux juges :
  décisions 2, 3, 6, 7, 65 et 87.

**Au propriétaire : la réponse est faible.** Aucun précédent ne couvre une
baisse durable de pensions liquidées, et ceux du chantier 2 sont « cités de
mémoire et à vérifier », sans relecture d'un spécialiste de droit public. La
CEDH a condamné en 2016 la suppression d'une pension d'invalidité sans
« mesures transitoires adaptées » (*Béláné Nagy*,
`2026-11-07-planchers-etude.md`), et la décision 63 refuse toute transition
à qui part dans les cinq ans. Que rien de déjà versé ne soit réclamé n'est
écrit nulle part au dépôt.

### 6. Est-ce un cadeau aux cadres ?

> Non : c'est au cadre que la proposition rend le moins. Né en 2000, ses
> cotisations lui rapportent 0,0 % par an au-dessus des prix, contre 0,2 % au
> salarié moyen et 0,5 % au SMIC. Il cotise au même taux que tous, sur tout
> son salaire, et sa pension se calcule sur l'espérance de vie de son niveau
> de vie, plus longue : elle est plus basse par euro cotisé.

- Les rendements : `2026-11-08-site-etude.md`, « 3. », le tableau.
- La table de mortalité : `docs/methodologie.md`, « Table par niveau de
  vie », le défaut depuis le 21 septembre 2026.
- Le taux et l'assiette : `index.html`, « Comment passe-t-on d'un système à
  l'autre ? » (« assiette déplafonnée, même taux pour tous »).

**Au propriétaire : la réponse est faible.** Le même tableau dit que le
rendement du SMIC perd 0,9 point (de 1,4 à 0,5 %) quand celui du cadre en
perd 0,5 (de 0,5 à −0,0 %). Et sur la fiche de paie, le gain net va de 39 €
par mois au SMIC à 417 € à cinq SMIC (`2026-11-07-message-etude.md`, « Les
actifs »), soit 2,1 % puis 4,6 % du brut (calcul de cette note, sur le SMIC
de 21 876 € par an) : l'adversaire répondra avec nos chiffres.

### 7. Et si la Bourse s'effondre ?

> Votre retraite n'y est pas. Elle reste en répartition : les cotisations de
> l'année paient les pensions de l'année. Seuls cinq points de salaire sont
> épargnés à votre nom, en titres d'État parmi les mieux notés de la zone
> euro, gardés jusqu'à l'échéance : aucune action. La crise que nous avons
> étudiée est celle de l'emploi ; une réserve la couvre.

- La répartition et le placement : `index.html`, « Mon argent sera-t-il
  placé en Bourse ? » ; `docs/limites/5-ante-capitalisation.md`, point 4.
- La réserve, une prime de 2,15 % retenue sur les pensions servies, calibrée
  sur l'emploi en baisse de 1 % par an de 2030 à 2039 : décisions 73 et 74.

**Au propriétaire : la réponse est faible.** « Aucune action » est le choix
du modèle, pas une règle écrite : la décision 32 fait du pilier « un contrat
à son nom, comme un PER », et un PER se place en actions ; sa forme juridique
« n'est écrite nulle part » (`2026-11-07-message-etude.md`). Le modèle ne
simule aucun risque, ni de taux ni de crédit (même point 4), et la réserve ne
couvre que le plancher des pensions déjà servies.

### 8. Et si l'État saisit la capitalisation ?

> C'est arrivé : la Pologne a repris en 2014 51,5 % des actifs de ses fonds
> de pension, et la France a fait verser à la dette sociale 2,1 Md€ par an de
> son Fonds de réserve. Une loi ne protège pas d'une loi suivante ; la
> propriété, davantage. L'épargne n'ira donc pas à un fonds public : ce sera
> un contrat à votre nom, qui vous appartient et se transmet.

- La Pologne, son Tribunal constitutionnel (K 1/14, 4 novembre 2015) et le
  Fonds de réserve, de 2011 à 2024 : `2026-11-07-message-etude.md`, « Un
  pilier capitalisé « protégé par la loi » » ; `docs/risque_de_defaut.md`,
  « La reprise des fonds capitalisés ».
- Le compte à l'assuré : décision 32.

**Au propriétaire : la réponse est faible.** Ce que la Pologne a pris, ce
sont « toutes leurs obligations d'État », et notre pilier n'est fait que de
titres d'État (question 7). La Hongrie, en 2010, a fait « revenir » au public
97 % des adhérents de ses fonds (`docs/risque_de_defaut.md`) ; si leurs
comptes étaient à leur nom, le dépôt ne le dit pas, et la réponse s'appuie
sur la propriété : à vérifier. La forme juridique du compte reste à écrire,
et les 18 % du compte notionnel, eux, ne tiennent que par la loi.

### 9. Qui paie le déficit ?

> Les retraités d'abord : leurs pensions baissent de 118 Md€ par an, par
> cinquièmes d'ici 2030. Puis les propriétaires de terrains : un point de taxe
> sur leur valeur, 36 à 43 Md€ par an. Pas les salariés : leur cotisation
> baisse. La caisse reste en déficit jusqu'en 2054, à crédit, et finit 2070
> avec une dette d'un point de PIB, contre 66 si rien ne change.

- 118 Md€ en 2026 : programme, chantier 1, « Le 7 novembre 2026, les deux
  lectures sur la base de la page Coût ». Les cinquièmes : décision 87.
- 36 à 43 Md€ : décision 80. La TVA reste à 20 % : décision 79.
- 2054, un point, 66 points : chantier 1, « Le 8 novembre 2026, avec la LVT
  et la part de TVA », colonne « Programme, 18 % ».

**Au propriétaire : la réponse est faible.** Les chiffres de la dernière
phrase ajoutent au modèle une LVT et une part de TVA qui n'y sont pas, avant
abattement et plafonnement ; ce que le dépôt publie, lui, donne 103 points de
dette en 2070 contre 66 au système actuel, et un solde moyen de −1,44 contre
−1,13 (`docs/chiffrage_plf.md`). Les 118 Md€ sont calculés d'un coup, non
par cinquièmes ; la lecture A ou B de la décision 29 n'est pas choisie ; et
près de trente ans de déficit à crédit se lisent contre la décision 4.

### 10. Les mères paient-elles la réforme ? (proposée par la note)

> Sur leur pension, oui : les trimestres pour enfants et la majoration de
> 10 % ne sont plus servis, comme tout ce qui n'a pas été cotisé. La moitié
> de ce qu'ils coûtaient va, en argent, aux parents qui élèvent un enfant
> aujourd'hui ; l'autre moitié au déficit. L'assurance vieillesse des parents
> au foyer est gardée.

- Les trimestres et la majoration : décisions 52 à 54. Le partage :
  décision 50. L'AVPF : décision 57.

**Au propriétaire : la réponse est faible.** Elle retire un droit certain
contre une prestation dont la forme, le montant, les conditions et le payeur
restent « à étudier aux sources » (décision 51). Et elle ne chiffre rien : ce
qu'une mère retraitée type y perd n'a pas été relevé par cette note (à
prendre dans `2026-11-07-enfants-etude-et-couts.md`).

## Ce qui ressort

- **Aucune des dix réponses n'est sans faiblesse**, et quatre sont faibles
  sur le fond plutôt que sur un chiffre : la maison (4), le juge (5), la
  Pologne (8), le déficit (9). Trois tiennent mieux : l'âge (2), les cadres
  (6), la Bourse (7), à condition de dire ce qu'elles coûtent à qui.
- **Trois réponses dépendent de décisions ouvertes** : le rendement, de la
  façon de le montrer (`2026-11-08-site-etude.md`, « 3. ») ; le déficit, de
  la lecture A ou B ; la Bourse et la Pologne, de la forme du compte.
- **Deux chiffres de tête ne suivent pas le programme** : les 28 % de la
  baisse, et les 118 Md€ comptés d'un coup.
- **Deux promesses se lisent contre deux réponses** : « votre pension ne
  baissera jamais en euros » contre la question 1 ; « ne pas faire payer
  deux fois une génération » contre la question 9.

## Ce qui n'a pas été vérifié

Aucun calcul n'a été relancé : les chiffres sont ceux des notes et des pages,
à leur date. Les 28 % sont lus sur la page fabriquée, non refaits. Les arrêts
et décisions de justice ne sont pas rouverts : ils sont cités d'après les
notes, qui en disent elles-mêmes le degré de lecture. Les deux parts du brut
de la question 6 sont un calcul de cette note. La question 10 n'a lu que les
décisions, pas l'étude des enfants.

## Ce que le propriétaire tranche

1. **La liste.** Ces dix questions, ou d'autres : la dixième est de la note ;
   manquent peut-être les veuves, les fonctionnaires, et « pourquoi n'y
   a-t-il plus de simulateur ? ». Et leur ordre.
2. **Le premier mot de la première réponse.** « Oui, le plus souvent » (la
   piste, que la décision 90 autorise), ou l'égalité de traitement d'abord.
   Et le chiffre : 28 % en attendant, ou rien avant le compte des retraités.
3. **La quatrième promesse** : la récrire (« une fois recalculée, votre
   pension ne baissera plus en euros »), ou la laisser.
4. **La maison.** Répondre « non » (la piste), ou « oui, en partie, si vous
   avez touché la garantie » ; et, sur le fond, garder la reprise dès le
   premier euro sur une garantie servie d'office, ou lui donner un seuil, ou
   le droit de la refuser.
5. **Le rendement.** Dire dans la réponse 3 qu'il est négatif sous les
   conventions du COR (la piste de l'étude du site), et montrer la pension
   de 2055 à côté des 186 €, ou s'en tenir au « promis, payé, proposé ».
6. **Le juge.** Publier « nul ne peut le promettre » (la piste), et faire
   relire la réponse 5 par un spécialiste de droit public avant.
7. **Les cadres.** Dire le gain en euros qui monte avec le salaire, ou ne
   donner que les rendements.
8. **Le compte capitalisé.** Sa forme juridique, et s'il peut se placer
   ailleurs qu'en titres d'État : les réponses 7 et 8 se contredisent tant
   que ce n'est pas écrit.
9. **Le déficit.** Quels chiffres publier : ceux du modèle (103 contre 66),
   ou ceux qui comptent la LVT et la TVA hors du modèle (1 contre 66) ; et
   A ou B, que la réponse attend.
10. **L'âge.** S'en tenir à l'argument du budget, ou chercher une réponse
    pour le salarié en carrière longue.

Puis, quand la session du site (action 189) aura quitté les pages, une
session y porte les réponses retenues, les chiffres ancrés sur leurs sondes.
