# Étape 11, première partie : les points du relevé convertis en revenus

**Reprise, au 14 octobre 2026.** Fait : les points d'un relevé convertis en
revenu dans les deux moteurs et leur branchement au site (11 octobre) ; le
diviseur éprouvé sur les exemples officiels de la Finlande, de la Pologne, de
la Suède et de l'Italie, par les deux moteurs, en cas d'essai
(`test_diviseur_exemples_officiels.py`, 14 octobre) : exact là où la
convention est la même, plus court du terme des versements ailleurs. Reste :
au propriétaire, le terme des versements, la réversion dans le diviseur, et
ce que reçoit une année sans montant ni points ; puis la Lettonie, la grille
publiée, les lissages, le prorata des mois, les chocs du COR. Détail :
`2026-10-14-etape-11-exemples-officiels.md`, « Ce qui reste ».

**La demande.** Le propriétaire, le 11 octobre 2026 : « les années sans
montant sont comptées zéro au compte notionnel, et les points du relevé sont
“lus, et jetés”. Convertis ces points en montants, dans les deux moteurs. »
Une année qui n'a ni montant ni points : un choix du programme, à signaler sans
le trancher ; un champ de saisie, s'il en fallait un : à la session du site ;
ni `cout.py`, ni les pages du site. C'est le rang lourd du classement par poids
(note du 9 octobre), et les points du chantier 138.11 au registre : la
Pologne, la Lettonie, PROST.

**Ce qui est fait.**

- *Le relevé des droits à rebours* (`droit/releve.py`, `revenu_des_points` ;
  `moteur/js/droit/releve.js`, `revenuDesPoints`). Pour un statut, une année,
  un étage — la base ou la complémentaire — et des points, le revenu entier le
  plus bas dont une année de ce statut, cotisée par un assuré fictif, ouvre au
  moins ces points dans les régimes de l'étage que le statut cotise : une
  dichotomie sur le relevé des droits, qui applique le barème du scénario 1,
  tranches, assiettes minimales, paliers et arrondis compris. Rien n'est
  recopié, et la pension recalculée de la saisie retrouve les points du relevé.
  Au plafond d'un barème, un drapeau le dit ; rien n'est rendu quand les points
  ne disent aucun revenu : les cent points par trimestre des libéraux d'avant
  2004, le plancher d'une assiette minimale (23 points de retraite
  proportionnelle, 133 de RCO), plus de points que le barème n'en ouvre,
  l'additionnel (le RAFP compte les primes), un régime où la coordination route
  une carrière d'un an (un fonctionnaire rétabli à l'Ircantec). Une conversion
  coûte une vingtaine de relevés d'une année : de 13 à 23 ms en Python, de 3 à
  21 ms en JavaScript.
- *La place.* Un module à part, `droit/inverser`, faisait échouer
  `test_les_modules_sont_tous_precharges` : tout module de `moteur/js/` doit
  être préchargé ou importé à la demande par `index.html`, page du site que
  cette session ne touche pas. Le relevé des droits l'est déjà, et l'inversion
  y vit, sur son `construire`.
- *La lecture des relevés* (`web/releve_lu.py`, `moteur/js/releve-lu.js`).
  Elle garde les points de chaque ligne — étiquetés « pts », ou le nombre d'un
  régime qui compte en points —, par année, statut et étage, et, quand
  l'appelant passe le convertisseur, en tire le revenu d'une année sans montant
  hors d'une période assimilée : le plus haut des étages d'un même statut, qui
  disent chacun un revenu au moins atteint ; la somme de deux statuts, deux
  emplois ; le barème du cadre pour une année de points Agirc. Deux notes
  remplacent l'ancienne : les années converties, et celles du plafond, « le
  revenu a pu le dépasser » ; les années restées sans revenu, « à compléter à
  la main ; à défaut, la simulation leur prête un revenu nul ». Un montant en
  euros sur une ligne d'un régime en points reste ignoré, comme avant : c'est
  une cotisation plus souvent qu'un revenu.
- *Les chiffres, sur les relevés d'essai.* Le tableau des années du relevé de
  2026, collé seul : 2,90 points d'Agirc-Arrco en 2018, 783 € ; 7 points
  d'Ircantec en 2019, 620 €. L'estimation d'Info Retraite : 4 points
  d'Ircantec en 2022, 364 €. La CARMF : 412 points en 2015, 29 571 € ; 550
  points en 2016, le plafond, cinq plafonds de la Sécurité sociale, 193 080 € ;
  400 points en 2003, cent par trimestre, rien. Un exploitant : 80 points de
  retraite proportionnelle en 2018, 29 717 €, et 221,89 de RCO, 30 000 €, que
  l'année prend ; les 23 points du plancher en 2019, rien.
- *Les tests.* `tests/test_revenu_des_points.py`, dix-sept cas : le revenu
  rendu ouvre les points et un euro de moins ne les ouvre pas, sur neuf
  barèmes ; le plafond ; sept points qui ne disent rien. Dans
  `tests/test_releve_lu.py`, deux relevés d'essai de plus, quatre cas, et la
  comparaison des deux implémentations rejouée avec les points convertis par
  chaque moteur : même saisie, mêmes notes, mêmes lignes ignorées.
- *Le registre.* Les trois points du chantier 138.11 sur les années sans
  montant passent `a_trancher`, au chantier 138.13 : ce qui en reste est
  l'imputation d'une année sans montant ni points. La limite « Un régime qui
  compte en points ne porte aucun revenu » (`docs/limites/5-hors-du-modele.md`)
  dit ce que le modèle sait faire, et ce que le site ne fait pas encore.

**Ce que le propriétaire tranche.** Ce que le compte notionnel reçoit d'une
année qui n'a ni montant ni points qui le disent : zéro, comme aujourd'hui ;
le salaire minimum, au prorata, comme la Pologne ; la moyenne nationale, comme
la Lettonie ; la moyenne revalorisée de la carrière, comme PROST. Une année
laissée à zéro ôte au compte environ un quarante-troisième du capital d'une
carrière complète au même salaire relatif. La lecture ne tranche pas : elle
laisse l'année à zéro, et le dit.

**Ce qui reste**, dans l'ordre :

1. *Le branchement*, à la session du site. `index.html` appelle
   `lireReleve(lignes, new Date().getFullYear())` sans convertisseur : le site
   lit encore ces années à zéro. Il lui faut passer, en troisième argument,
   `(...a) => revenuDesPoints(contexte.simulateur().scenarioActuel, ...a)`,
   `revenuDesPoints` venant de `moteur/js/droit/releve.js`, déjà préchargé ;
   puis récrire la limite. Aucun champ de saisie : la conversion écrit un
   revenu dans le champ du relevé.
2. *Les autres parties de l'étape*, chacune au registre, chantier 138.11 : les
   exemples officiels du diviseur (Suède, Finlande, Italie, Pologne, Lettonie),
   la grille publiée des diviseurs, le lissage italien exact, le lissage du
   seul réel, le prorata des mois de l'année du départ, les chocs stylisés du
   COR.
3. *Les cadres d'avant 2019 sur un relevé d'aujourd'hui.* Info Retraite fond
   leurs points Agirc dans ceux de l'Agirc-Arrco, sans nommer l'Agirc : la
   lecture convertit alors l'année au barème du non-cadre, qui ne connaît ni la
   tranche B ni la garantie minimale de points, et le revenu rendu est trop
   haut. Seules les années sans montant en souffrent, et le relevé de 2026 en
   donne d'ordinaire le revenu.
4. *Une ligne qui ne porte que des points* — ni revenu, ni trimestres, ni
   motif, ni emploi — reste ignorée, ses points avec elle : un total écrit avec
   son année se lirait sinon comme une année.
