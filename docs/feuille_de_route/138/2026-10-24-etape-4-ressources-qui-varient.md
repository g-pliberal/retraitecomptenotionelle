# Étape 4, douzième partie : la réversion révisée quand les ressources du survivant varient — un salaire qui change, une activité reprise, les ressources du nouveau conjoint

**Le 24 octobre 2026, la demande.** Le propriétaire, dans la cinquième vague des
sessions du jour : le premier point du bloc de l'étape — la révision de la
réversion quand les ressources du survivant varient autrement que par la fin de
son activité ou de son ménage, ces variations à dater d'abord dans la
chronologie —, le point 1 du « Ce qui reste » de la onzième partie. Les
majorations de 1976 et 1977 viendront dans une autre session ; ce que le bloc
renvoie au site n'est pas de celle-ci.

**Ce que dit le droit, lu le jour même** (journal de veille du 24 octobre,
« ressources qui varient » ; fiche `reversion`).

- *La révision.* La réversion « est révisable en cas de variation dans le
  montant des ressources » (R. 353-1-1, dans toutes ses rédactions depuis le 30
  décembre 2004), selon R. 815-40, puis R. 815-42 depuis 2007 : au premier jour
  du terme d'arrérages qui suit la période de trois mois où les ressources ont
  varié. La Cnav l'applique « lorsque, notamment, la variation du montant des
  ressources résulte de la variation des revenus professionnels du conjoint
  survivant (ou du ménage) » (circulaire n° 2006-6, § 12), au mois qui suit le
  constat jusqu'en 2010, au mois qui suit la variation depuis, qu'elle réduise,
  augmente, suspende ou rétablisse la réversion (circulaire n° 2010/58, § 21).
  La circulaire RSI n° 2007/061 (annexe 3, § 8) dit la même règle aux régimes
  alignés.
- *Les ressources de la révision.* « Les ressources sont examinées sur les 3
  mois qui précèdent cette date de révision » (exposé « Condition de
  ressources ») ; les revenus d'activité « pour leur montant réellement perçu
  au cours de la période de référence » (circulaire RSI n° 2007/061, annexe 3,
  § 5.2 et 6.1) : la période porte encore des revenus d'avant la variation. Le
  modèle garde sa convention, les ressources d'après le changement, l'année
  entière.
- *Un exemple daté, aucun chiffré.* « Pension de réversion à compter du
  01/07/2005 (52 ans). L'assuré nous informe en octobre 2006 percevoir des
  revenus professionnels. Date du constat = octobre 2006 --> révision de la
  pension de réversion au 01/11/2006 » (circulaire n° 2006-6, § 12). Il entre au
  témoin des exemples officiels pour sa première révision, une grandeur neuve
  de l'oracle (`dates_de_premiere_revision_de_la_reversion`), vu rouge avant le
  code.

**Ce qui est fait.**

- *La chronologie* (`chronologie.py`, et son jumeau) : les variations des
  revenus d'activité du survivant (`variations_d_activite`) et des ressources de
  son nouveau conjoint (`variations_du_nouveau_conjoint`), `(date, montant
  annuel)` chacune, sont des événements de ses ressources, datés, sans fin,
  marqués `variation` : à partir de ce jour, la ressource est de ce montant. Les
  faits déclarés au décès et à l'union n'en changent pas, et les accesseurs qui
  les lisent passent les variations ; deux accesseurs neufs,
  `variations_d_activite` et `variations_du_menage`. Refusés : une variation
  avant le décès, celle du ménage hors de l'union, deux le même jour, ou le jour
  où l'activité cesse, un montant négatif.
- *Le modèle* (`droit/reversion.py`, et son jumeau) : les revenus d'activité
  d'un jour sont ceux de la dernière variation venue (`_activite_au`), ce
  qu'apporte le nouveau conjoint de même (`_apport_au`), à la date d'effet
  comme à chaque révision ; le mois qui suit chaque variation révise la
  réversion d'après juillet 2004 ; les cinquante-cinq ans la révisent quand une
  activité court ce jour-là ; le survivant sans activité au décès qui en
  commence une avant son âge légal la garde révisable jusqu'à sa retraite
  (circulaire n° 2007-35, § 222). La réversion d'avant 2004 n'en est pas
  touchée, ni la complémentaire des indépendants, qui les lit à sa date d'effet.
- *La saisie* (`saisie.js`) : `activite_conjoint_variations` et
  `ressources_nouveau_conjoint_variations`, « date:montant » séparés de
  virgules, lus, vérifiés — chacune suit ce qu'elle fait varier, soixante au
  plus, comptées avant d'être lues —, gardés dans l'adresse.
- *Les tests* : dans `test_chronologie.py`, les variations et leurs refus, aux
  deux moteurs ; dans `test_reversion.py`, trois cas posés à la main — la veuve
  de 2006, sans ressources, qui commence une activité en mars 2007 (2 080 fois
  8,27 €, ramené aux euros de 2006, moins ses 14 000 €), le veuf de 2015 dont le
  salaire passe à 25 000 € en mars 2018 (2 080 fois 9,88 €), puis, remarié en
  mai 2018, sa conjointe dont les ressources tombent à 12 000 € en janvier 2020
  (1,6 fois 2 080 fois 10,15 €) —, ce que rien ne révise plus après la dernière
  révision ou avant juillet 2004, quatorze refus de la saisie, l'adresse, trois
  saisies aux deux moteurs ; l'exemple de la circulaire n° 2006-6 à l'oracle ;
  trois témoins de simulation neufs.
- *La fiche* `reversion` : ce qu'elle lit, ses écarts, une lecture de plus,
  trois textes sans effet — R. 815-20, R. 815-39 et R. 815-41 de 2001, auxquels
  R. 353-1-1 renvoie, des contrôles — ; la page des limites. Le cliquet des
  textes descend à 9 533.

**Les mesures.** Aucune pension ne bouge, sur les 904 témoins d'avant, ni aucun
rendu de page, ni aucune réversion : aucun ne datait une variation. Les trois
témoins neufs, en euros de l'année du décès : la veuve de 2006, sans ressources,
reçoit sa réversion entière, 6 667,51 € ; son activité commencée en mars 2007
la ramène le 1er avril à 2 897,44 €, et ses cinquante-cinq ans, en octobre 2008,
la rendent entière, toujours révisable. Le veuf de 2015, sa réversion entière à
7 317,99 €, la voit ramenée le 1er avril 2018 à 2 887,30 € quand son salaire
passe à 25 000 € ; remarié en mai 2018, le 1er juin à 2 119,68 €, puis entière
le 1er février 2020, quand les ressources de sa conjointe tombent à 12 000 €.

**Ce qui reste.**

1. *De la révision* : les trois mois que la caisse examine avant chaque
   révision, tels que perçus, qui portent encore des revenus d'avant la
   variation ; le droit personnel liquidé après la dernière révision d'abord
   fixée (circulaire n° 2010/58, § 24) ; la révision de la majoration de 11,1 %
   (R. 353-13) et celle de la complémentaire des indépendants ; la retraite
   d'inaptitude substituée à la pension d'invalidité du survivant ; la
   réversion que la fin de l'union rendrait dans les régimes qui la retirent au
   remariage, à lire régime par régime.
2. *Au site* : les quatre champs du formulaire (`activite_conjoint_fin`,
   `nouvelle_union_fin`, `activite_conjoint_variations`,
   `ressources_nouveau_conjoint_variations`), et la phrase de la carte qui
   dirait les révisions.
3. Les majorations de 1976 et 1977 aux salariés agricoles, l'Alsace-Moselle,
   l'ancien invalide ; les points 3 de la septième partie et ceux de la
   huitième.
