# Étape 8, dix-neuvième partie : la réversion du régime aux plans de 1997 à 2008

**Le 19 octobre 2026, la demande.** Le dernier reste du bloc « Reprise » de
l'étape : ce que la réversion déclarée permet de servir aux plans de 1997 à
2008, point 1 de « Ce qui reste » de la note « durée de chef reconstituée »,
né de la note « réversion du régime ». Session 18 de la troisième salve de la
vague B du 19 octobre, sur le modèle.

**Ce que dit le droit** (journal de veille du 19 octobre, index LEGI et JORF à
jour au 18 octobre). Quatre règles, non trois.

- *L'exclusion* : les points des conjoints des pensions prises de 1998 à 2001
  ne vont qu'aux personnes « qui ne sont pas titulaires d'un des avantages
  mentionnés aux articles L. 732-41 à L. 732-44 et L. 732-46 » (L. 732-31 en
  2000 et 2001, L. 732-54-2, I, depuis), « à la date d'effet de leur pension
  de retraite personnelle » (D. 732-118).
- *Le plafond* : la réversion obtenue après, « le nombre de points gratuits
  est plafonné, à compter du 1er janvier de l'année qui suit cette obtention,
  au niveau atteint durant l'année au cours de laquelle a pris effet la
  pension de réversion » (mêmes articles, II) ; D. 732-126 à D. 732-130 en
  disent les nombres pour les réversions de 1998 à 2001 : ceux des pensions
  dues de chacune de ces années.
- *Le minimum figé* : la réversion entrée en jouissance avant 1995 reste sous
  L. 732-46, dont le IV majore celle du titulaire qui a sa propre pension
  (D. 732-97). L. 732-33, II, puis L. 732-54-4, relèvent cette majoration
  forfaitaire depuis 1999, à trente-deux ans et demi d'activité agricole,
  vingt-sept et demi à quinze ans de conjoint sans autre pension depuis 2000
  (décret n° 2000-261, article 2 ; décret n° 2002-297, article 11 ;
  D. 732-139). Ce relèvement passe avant la majoration de la retraite
  proportionnelle, sauf en 1999 (L. 732-33, I et II) : la pension prise avant
  1997 garde (20 - n) × d depuis 2000 (décret n° 2000-261, article 1er ;
  décret n° 2001-170, article 3 ; décret n° 2002-297, article 5 ; D. 732-116),
  celle prise de 1997 à 2001, 26,933 points depuis 2001 (décret n° 2001-170,
  article 3 ; décret n° 2002-297, article 4 ; D. 732-113).
- *Les majorations de la réversion*, de 2002 à 2008 : elles portent le droit
  propre et le droit dérivé au minimum vieillesse au prorata de la durée
  agricole, aux pensions prises avant 2002 (décret n° 2002-297, article 12 ;
  D. 732-140) comme depuis (décret n° 2002-298, article 5 ; D. 732-147). La
  note « réversion du régime » ne voyait que la seconde.

**Ce qui est fait**, dans les deux moteurs.

- *La fiche* `majoration_retraite_proportionnelle` : un paramètre
  `reversion_d_avant_1995` par version — 26,933 points depuis 2001 aux
  pensions prises de 1997 à 2001, vingt depuis 2000 à celles prises avant
  1997, les durées de D. 732-139 — ; dix-huit rédactions de plus citées par
  les versions de 2000 à 2007, cinq à rattacher par la lecture du jour ; la
  présomption `pas_de_reversion_agricole`, que les plans lisent désormais, au
  vocabulaire aussi ; l'écart qui dit la lecture de la réversion. Le cliquet
  des textes descend de 9 637 à 9 615.
- *Le code* : `_titulaire_d_une_reversion` (déclarée, ouverte, non nulle) ;
  `_points_des_conjoints` refuse les points au titulaire à la date d'effet ;
  `majoration_retraite_proportionnelle` plafonne les points des conjoints au
  niveau que la règle de l'année de la réversion redonne, et prend le minimum
  figé de `_minimum_du_veuf` ; leurs jumeaux, `titulaireDUneReversion` et
  `minimumDuVeuf`. La révision des pensions déjà liquidées passe par elle.
- *Les tests* (`tests/test_minima_agricoles.py`, quatre de plus) : la
  conjointe partie en 2000, veuve avant son départ, puis en 2001 et en 2003 ;
  le chef parti en 1995 veuf depuis 1990, et depuis 1996 ; celui parti en 1997
  veuf depuis 1993. Quatre révisions de plus dans la confrontation des deux
  moteurs, quatorze au lieu de dix, vues rouges sans le portage.

**Les mesures.** La conjointe de trente et un ans partie en février 2000 :
veuve avant son départ, rien des plans, 575 € de moins par an en 2008 ; veuve
en 2001, 38,40 points au lieu de 161,21 en 2008 (137 € au lieu de 575 €) ;
veuve en 2003, 96,99 points. Le chef parti en 1995 à 30 % du salaire moyen,
veuf depuis 1990 : 120,92 points de plans de 2000 à 2008, au lieu de 607,12 en
2008 (431 € au lieu de 2 164 €), et, PMR comprise, une pension de base de
5 425 € en 2012 au lieu de 7 748 € ; celui parti en 1997, veuf depuis 1993 :
409,99 points au lieu de 753,16 (980 € au lieu de 2 204 €).

**Ce que la vérification a trouvé.**

- *Le droit dérivé n'est pas servi* : le relèvement de la majoration
  forfaitaire (642,47 points en 2002 pour trente-sept ans et demi) et les
  majorations de D. 732-140 et D. 732-147 rendent en réversion l'essentiel de
  ce que le veuf perd en droit propre. Le modèle rend le droit propre, et
  prend la réversion telle qu'elle est déclarée : sa pension baisse, le total
  de ce que la caisse lui verse, non. Déclaré dans la fiche ; au propriétaire.
- *Titulaire* se lit d'une réversion déclarée non nulle : nulle, les
  ressources l'absorbent (L. 732-41), et l'assuré n'en est pas titulaire,
  quand le 2° de D. 732-110, II, le dit « susceptible » d'en bénéficier.
- *L'option de L. 732-46, V* : le conjoint survivant de moins de soixante ans
  au 1er janvier 1995 pouvait demander L. 732-41 ; la réversion déclarée
  commencée avant 1995 se lit sous L. 732-46. Déclaré.
- *La réversion déclarée* suit les pensions de base depuis son début, sans ses
  majorations de 1999 à 2008 : la PMR de 2009, qui retranche celle que le
  régime sert, en retranche peut-être moins qu'il ne faut. Déclaré, une
  question à la MSA dans la fiche.

**Ce qui reste**, de l'étape :

1. À la fin de l'étape, la fiche `complement_differentiel_rco`.
2. Chaque janvier, la série à porter jusqu'au nouveau barème (`FINS`).
3. Inchangés : les points 2 et 3 de « Ce qui reste » de la note « points des
   conjoints » ; au propriétaire, le montant de la MSA pour 2015 à 2017 et
   2019, depuis un poste qui atteint l'archive du web, les seize points d'une
   année de conjoint d'avant 1999, et, à la MSA s'il le juge utile, le plafond
   servi depuis 2024 aux pensions prises avant septembre 2023 et le montant de
   la durée agricole au-delà de la durée de chef reconstituée.
4. Au propriétaire, né de cette partie : montrer ou non, dans les résultats,
   les majorations de la réversion, droits dérivés que le modèle ne calcule
   pas ; à la MSA, s'il le juge utile, la réversion d'avant 1995 de qui a
   demandé L. 732-41, et le sort des majorations de D. 732-140 et D. 732-147
   après 2009.
5. Pour la session des pages : le champ de la réversion dit le mois où elle
   commence ; avant 1995, il décide désormais du minimum des plans, ce que le
   formulaire pourrait dire.

Aucun témoin ne bouge : le seul qui déclare une réversion du régime, la veuve
de 2010 partie en 2016, n'a pas de plans.

**Le 19 octobre au soir, la suite rouge.** Le paquet de cette partie, refait
sur le modèle du jour, porte le coefficient d'équilibre de la proposition à
1,0013 en 2070, 44 années sur 45 sous un, quand celui qu'il remplaçait, figé
plus tôt, le gardait sous un jusqu'au bout (0,9955) : les changements du coût
faits depuis, les ex-invalides de la Cnav dans la grille entre autres, l'y
avaient porté, non la réversion, qu'aucune carrière du coût ne déclare. La page
Cas types a pris sa lecture « mixte », sans le manque de 17 %, et
`tests/test_parcours.py` a rougi sur GitHub. Le parcours
(`docs/parcours_presentation.md`, section 3) dit désormais une phrase vraie de
part et d'autre de un.
