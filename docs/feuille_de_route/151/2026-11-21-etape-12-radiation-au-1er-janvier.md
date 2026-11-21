# Étape 12 : la radiation qui tombe un 1er janvier ne disparaît plus

**Le 21 novembre 2026 : quand la limite d'âge tombait en décembre, la pension
partait du départ saisi et non de la fin de l'emploi. Corrigé dans
`moteur/js/droit/limite_age.js`, sur le test qui le dit ; le défaut touchait
tous les emplois à limite, du contractuel au fonctionnaire.**

## La cause

Trouvée par le balayage de la carte de justesse (action 194, étape B,
piste 4) : contractuel né en juillet 1951, parti à 70 ans, 19 880,71 € ; né en
août 1951, 21 005,16 € (+5,7 %). Les deux ont une limite de soixante-cinq ans
et quatre mois (L. 556-11 CGFP, marche du décret prévu au II de l'article 28
de la loi n° 2010-1330 : soixante ans atteints au second semestre 2011).
Le premier l'atteint en novembre 2016, ses pensions partent le 1er décembre ;
le second en décembre, elles auraient dû partir le 1er janvier 2017.

`radier` arrête la carrière au 31 décembre 2016, puis `departsEtDemandes`
relit la radiation sur cette carrière arrêtée : ses services y finissent le
1er janvier 2017, le jour même de la limite, et `radiation` ne retenait une
limite que strictement avant la fin des services. La radiation disparaissait,
la carrière restait coupée, et la pension partait en septembre 2021, avec le
coefficient de l'Ircantec d'un départ à 70 ans (1,1475 au lieu de 1,0125).
Même chose pour toute limite atteinte en décembre : contractuel né en
décembre 1950 ou en mars 1952, fonctionnaire né en décembre 1950 ou en
mars 1952, agent des IEG du test de l'étape 9 dans le calcul complet.

## La correction

Quand les services s'arrêtent avant l'année du départ saisi, ils finissent au
31 décembre : une limite atteinte au 1er janvier qui suit est la leur, et la
radiation reste. Quand ils vont jusqu'au départ saisi, rien ne change. Ainsi
`radiation(radier(c))` rend la radiation de `c`.

- Test : `test_la_limite_atteinte_en_decembre_fait_partir_la_pension_en_janvier`
  (`tests/test_limite_age.py`), vu rouge (`{None}` au lieu de `2017-01-01`).
- Contractuel né en août 1951, parti à 70 ans : 21 005 € → 20 001 € par an,
  pensions au 1er janvier 2017 ; né en juillet, 19 881 € au 1er décembre 2016.
  L'écart entre les deux mois passe de +5,7 % à +0,6 %.
- Témoins refaits, un seul cas déplacé : l'agent des IEG né en 1940 entré à
  32 ans (`limite_age_ieg_1940_entre_a_32_ans`), dont l'étape 9 disait la
  pension au 1er janvier 1997 et que le calcul complet servait au départ
  saisi : 15 746 → 15 738 € par an (`simulations.json`, `droit.json`,
  `sorties.json`). Les 936 autres témoins et les pages ne bougent pas.

## Le texte, et ce qu'il laisse au modèle

R. 351-37 CSS (LEGIARTI000023796396, 2011-2023) : « Chaque assuré indique la
date à compter de laquelle il désire entrer en jouissance de sa pension » ;
article 17 de l'arrêté du 30 décembre 1970, Ircantec (LEGIARTI000019511935) :
« La liquidation ne peut être opérée que sur demande de l'intéressé ». Ni l'un
ni l'autre ne fait partir la pension du contractuel à la fin de son contrat :
le modèle le présume (choix 5 de l'étape 4), comme pour le fonctionnaire radié.
La correction ne touche pas ce choix ; elle l'applique à tous les mois de
naissance. Reste au propriétaire : garder la présomption, ou servir au
contractuel radié ses pensions au départ saisi, sur une carrière arrêtée à la
limite (l'Ircantec majorant alors le départ tardif).
