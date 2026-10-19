# Étape 8, dix-huitième partie : la durée de chef reconstituée des pensions prises avant 1997, dans la PMR de 2009 à 2021

**Le 19 octobre 2026, la demande.** Le reste suivant, dans l'ordre du bloc
« Reprise » : la durée de chef reconstituée de D. 732-110, III, point 1 de
« Ce qui reste » de la note « montants d'après août 2023 », né de la note
« pensions d'avant 1997 ». Session 4 de la première salve de la vague B du
19 octobre, sur le modèle ; ni la réversion aux plans de 1997 à 2008, qui
suit.

**Ce que dit le droit** (journal de veille du 19 octobre, index LEGI et JORF à
jour au 18 octobre).

- *D. 732-110, III* (décret n° 2009-173), mot pour mot dans les rédactions de
  2010, 2011 et 2016, le II depuis le décret n° 2021-1919 (« Le III devient le
  II ») : « Pour les personnes dont la pension de retraite servie à titre
  personnel a pris effet avant le 1er janvier 1997, la durée d'assurance en
  qualité de chef d'exploitation [...] est obtenue en divisant par 16 le nombre
  de points de retraite figurant au compte de l'intéressé avant application »
  des plans ; « une minoration forfaitaire de quinze points est appliquée pour
  chaque année » de chef à titre secondaire sans cotisation au forfait ; au-delà
  de la durée agricole, la durée « est ramenée à cette durée [...] dans la
  limite prévue au troisième alinéa du I ».
- *D. 732-111* (2009) : DM1 compte les périodes du 1° et du 2°, ou du 3°,
  « retenues dans les conditions et limites prévues aux I et III ». La
  reconstitution partage donc la durée agricole entre PMR1 et PMR2 de 2009 à
  2021, et décide en 2009 et 2010 des dix-sept ans et demi du 1° ; la PMR
  unique de 2022 ne la lit plus.
- Aucune publication de la MSA ne dit comment elle l'applique : circulaires de
  2009 et questions écrites de la XIIIe législature, cherchées sur le web.

**Ce qui est fait**, dans les deux moteurs.

- *`duree_de_chef_reconstituee`* (`dureeDeChefReconstituee`), calculée à la
  liquidation et gardée dans `ExploitantAgricole.chef_reconstitue` : les points
  au compte — la pension hors son forfait, à la valeur du point de la
  liquidation, comme les plans les lisent —, moins quinze par année de chef à
  titre secondaire sans forfait, divisés par seize, sans arrondi, ramenés à la
  durée agricole quand ils la dépassent, DR au plus. `reviser_les_exploitants`
  (`reviserLesExploitants`) la sert à la PMR de 2009 des pensions prises avant
  1997 ; le reste de la durée agricole va à PMR2.
- *Le forfait des années secondaires* : la retraite proportionnelle
  (`_retraite_proportionnelle`, `retraiteProportionnelle`), que les plans et la
  reconstitution lisent, retranchait le forfait de toutes les années du régime,
  celles de chef à titre secondaire comprises, que le forfait ne compte pas
  (L. 732-28) ; elle ne retranche plus que celui des autres. La même erreur
  mettait trop bas le n des plans des pensions prises de 1997 à 2008 :
  corrigée avec. `EligibleAgricole` porte ces trimestres et ces années
  (`annees_hors_forfait`, d'où `trimestres_hors_forfait` se déduit).
- *Les fiches* : `pension_majoree_reference` cite le III de 2009, les
  rédactions de 2010 et de 2022 et le DM1 de D. 732-111 ; l'écart récrit, une
  question à la MSA. `majoration_retraite_proportionnelle` : l'écart du n et
  celui des points au compte. Le cliquet des textes descend de 9 641 à 9 639,
  les rédactions de 2010 et de 2022 de D. 732-110 rattachées.
- *Les tests* (`tests/test_minima_agricoles.py`, trois de plus, un récrit) : la
  carrière complète à 30 %, ses trente ans reconstitués ; à 10 %, moins de
  treize, à PMR2 en 2009 et 2010 ; le chef à titre secondaire de 1982 à 1986 ;
  le forfait des plans. Trois révisions et une requête de plus dans les
  confrontations des deux moteurs.

**Les mesures**, d'un chef depuis ses vingt ans parti en 1995. À 30 % du
salaire moyen : 7 366,46 € de pension en 2009 au lieu des 7 671,96 € de PMR1
entière, 8 054,88 € en 2021 au lieu de 8 388,94 € ; à 10 %, 4 673,88 € en 2009
au lieu de 5 881,84 €, 5 364,74 € en 2011 au lieu de 6 059,40 € ; rien ne
change depuis 2022. Le salarié chef à titre secondaire de 1982 à 1986, puis à
titre principal jusqu'en 1996 : 1 165,53 € en 2015 au lieu de 1 200,11 €. Le
salarié chef à titre secondaire de 1982 à 1985, puis à titre principal parti
en 2005 : n de 28,390 au lieu de 24,771, 494,93 € de plans par an au lieu de
736,30 €.

**Ce que la vérification a trouvé.**

- *Au-delà de la durée reconstituée*, le modèle sert PMR2 sur le reste de la
  durée agricole, comme aux périodes qui ne sont pas de chef ; DM2 ne compte,
  au texte, que les périodes du 4°, et une lecture stricte n'en servirait rien.
  Déclaré, la question à la MSA dans la fiche.
- *Les points des années de conjoint d'avant 2004*, que le modèle prend sur le
  revenu saisi (`assiette_du_collaborateur`), entrent au compte et dans la
  reconstitution : un conjoint devenu chef en reconstitue plus d'années qu'il
  n'en a eu — trente pour seize, de 1980 à 1995 à 30 %. Inchangé.
- *La minoration de quinze points* ne joue toujours pas aux plans d'avant 1997,
  qui veulent trente-deux ans et demi, puis vingt-deux et demi, d'activité
  agricole qu'on ne peut avoir de 1981 à 1996 sans être au régime avant 1981 ;
  dans la PMR, elle joue depuis février 2014, quand D. 732-109 ne demande plus
  de durée minimale.

**Ce qui reste**, de l'étape, dans l'ordre :

1. Ce que la réversion déclarée permet de servir aux plans de 1997 à 2008
   (D. 732-118, D. 732-116, D. 732-147), point 4 de la note « réversion du
   régime ».
2. À la fin de l'étape, la fiche `complement_differentiel_rco`.
3. Chaque janvier, la série à porter jusqu'au nouveau barème (`FINS`).
4. Inchangés : les points 2 et 3 de « Ce qui reste » de la note « points des
   conjoints » ; au propriétaire, le montant de la MSA pour 2015 à 2017 et
   2019, depuis un poste qui atteint l'archive du web, et les seize points
   d'une année de conjoint d'avant 1999 ; à la MSA, s'il le juge utile, le
   plafond qu'elle sert depuis 2024 aux pensions prises avant septembre 2023,
   et, né de cette partie, le montant de la durée agricole au-delà de la durée
   de chef reconstituée.

Les témoins de simulation des chefs partis avant 1997, de 2009 à 2021, et des
chefs à titre secondaire partis de 1997 à 2008 bougent : GitHub les refait.
