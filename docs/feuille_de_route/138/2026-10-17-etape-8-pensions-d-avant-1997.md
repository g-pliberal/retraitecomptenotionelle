# Étape 8, onzième partie : les pensions de chef prises avant 1997, révisées par les plans sur la durée de chef reconstituée

**Le 17 octobre 2026, la demande.** Le premier reste de l'étape, dans l'ordre
du bloc « Reprise » : « avant 1997, la révision des plans » (point 1 de « Ce
qui reste » de la note « pensions déjà liquidées »). Le modèle ne servait les
plans qu'aux pensions prises de 1997 à 2008 : une pension de chef prise avant
1997 n'en recevait rien, et la PMR de 2009 la relevait d'un coup. Session 4 de
la vague du 17 octobre, sur le modèle.

**Ce que dit le droit** (journal de veille du 17 octobre ; index JORF et LEGI,
aux incréments du 17 octobre).

- *La révision* (décret n° 97-163, article 2) : les retraites proportionnelles
  « ayant pris effet avant le 1er janvier 1997 » sont « révisé[es] et
  porté[es] à un minimum à compter du 1er janvier 1997 », à qui a trente-deux
  ans et demi d'activité agricole à titre exclusif ou principal et dix-sept et
  demi de chef « reconstitués » : la durée de chef « est obtenue en divisant
  par 16 le nombre des points de retraite figurant au compte », et ramenée à
  la durée agricole quand elle la dépasse. P = (20 - n) × d : n, les points
  divisés par la durée reconstituée — seize, sauf quand elle est ramenée — ; d,
  trente-sept ans et demi au plus. Sous vingt-deux ans et demi de chef
  reconstitués et sous trente-sept et demi d'activité agricole, deux
  coefficients de 15, 15, 20, 20, 20 et 10 % par année manquante, « seul le
  coefficient de minoration le plus élevé » joue. Le tiers en 1997, les deux
  tiers en 1998 (article 3). Pas de condition de taux plein.
- *Les relèvements* : 23,9 points en 1999, les coefficients à 15, 15, 10, 10,
  10 et 40 % (décret n° 99-141) ; 26,96 en 2000 (décret n° 2000-261) ; 29,23
  en 2001, la minoration du chef supprimée (décret n° 2001-170 ; le Journal
  officiel imprimait 26,23, que le rectificatif du 3 mars 2001 corrige) ;
  depuis 2002, A = (MV1 - AVTS) / (37,5 × VP), la durée ramenée dans la limite
  de trente-sept ans et demi et n divisé par elle (décret n° 2002-297,
  article 5 ; D. 732-114 à D. 732-117) ; en 2007, vingt-deux ans et demi
  d'activité agricole et 5,5 % par année manquante, 4 % en 2008 (décret
  n° 2006-1638). Les points de 2008 restent, que la PMR de 2009 compte
  (D. 732-112).

**Ce qui est fait**, dans les deux moteurs.

- *La fiche* `majoration_retraite_proportionnelle` : un paramètre
  `pensions_prises_avant_1997` dans chaque version de 1997 à 2008 — A, la
  durée agricole minimale, la limite de la durée ramenée, les deux
  minorations — ; quatorze rédactions citées de plus, dont six de LEGI : le
  cliquet des textes descend à 9 714. Elle écrivait 26,23 points pour 2001.
- *`majoration_retraite_proportionnelle`* (`majorationRetraiteProportionnelle`)
  sert à la révision (`quand`) d'une pension prise avant 1997
  `_points_d_avant_1997` (`pointsDAvant1997`) : les points au compte sont la
  retraite proportionnelle de la liquidation à la valeur du point de la
  liquidation. *`reviser_les_exploitants`* (`reviserLesExploitants`) lit la
  version de l'année de l'échéance, non celle de la date d'effet.
- *Les tests* (`test_minima_agricoles.py`, quatre de plus, un récrit, trois cas
  de plus dans la comparaison des deux moteurs) : 20 points au tiers puis aux
  deux tiers, 23,9, 26,96, 29,23, le A de 2002 et de 2008, sur la durée
  reconstituée ; la durée ramenée à la durée agricole ; rien sous trente-deux
  ans et demi jusqu'en 2006, puis 5,5 et 4 % ; le plus fort des deux
  coefficients ; rien sous dix-sept ans et demi reconstitués, même à
  trente-quatre ans de chef.

**Les mesures**, d'un chef depuis ses vingt ans parti en 1995. À 30 % du
salaire moyen : 112 € de plus en 1997, 1 159 € en 2001, 2 036 € en 2008 ;
depuis 2009, la PMR le porte comme avant à 9 568 € en 2026. À 60 %, la durée
reconstituée ramenée à la durée agricole : les points de 2008 dépassent la PMR,
et la pension de 2026 passe de 9 568 € à 9 767 €. Au salaire moyen, rien : n
dépasse A. Vingt-six ans de chef : rien jusqu'en 2006, 886 € en 2008.

**Ce que la vérification a trouvé.**

- *Les points au compte d'avant 1990* sont, dans le moteur, ce que vaut leur
  rendement, faute du barème des classes : la durée reconstituée en dépend.
  Déclaré dans la fiche.
- *La minoration de quinze points* par année de chef à titre secondaire sans
  cotisation au forfait ne joue jamais : qui a trente-deux ans et demi
  d'activité agricole avant 1997 était au régime avant 1981, et garde dans le
  moteur le forfait de ses années à titre secondaire (R. 732-65). Déclaré.
- *D. 732-117 dans sa rédaction de 2005* n'est pas dans l'index LEGI : le
  moteur lui donne les coefficients de l'article 5, III, du décret
  n° 2002-297, que le décret n° 2006-1638 supprime en 2007.
- *La PMR de 2009 reconstitue aussi la durée de chef* d'une pension prise
  avant 1997, des points d'avant les plans divisés par seize (D. 732-110, III,
  décret n° 2009-173) ; le moteur y prend la durée de la carrière (fiche
  `pension_majoree_reference`). Inscrit à « Ce qui reste ».

**Ce qui reste**, de l'étape, dans l'ordre du bloc « Reprise » :

1. Les restes d'avant, inchangés : des conjoints, les pensions dues de 1998 à
   2001 ; un montant de la MSA pour 2015 à 2017 et 2019 ; le 2° de D. 732-110,
   II (décès du conjoint, à saisir) ; la PMR revue quand les ressources
   changent ; les points 2 et 3 de « Ce qui reste » de la note « points des
   conjoints ».
2. Né de cette partie : la durée de chef reconstituée dans la PMR des pensions
   prises avant 1997 (D. 732-110, III, rédaction du décret n° 2009-173), que
   `_points_d_avant_1997` reconstitue déjà pour les plans.

Les témoins de simulation des chefs partis avant 1997 bougent : GitHub les
refait.
