# Saphir, rejoué au droit de 2017 : l'ASPA et l'impôt des pensions

**La demande**, le 24 octobre 2026 : la cinquième vague du lot que le
propriétaire a demandé ce jour-là, une session par tâche qui se mène sans
lui. Pour l'action 137, le premier reste de son bloc : « l'ASPA de Saphir. La
note du 22 octobre en nomme aussi l'abattement de 2017 et celui des personnes
âgées. Rejouez son calcul au droit de sa date, confrontez chaque écart à la
donnée du dépôt qui dit la même règle, et dites de qui est l'erreur. »

**Fait, le 24 octobre 2026 : le calcul rejoué ; sur l'ASPA et l'abattement de
10 % des pensions, Saphir est le dépôt ; ses deux autres abattements sont
faux ; le dépôt a, sur l'ASPA de 2017, deux centimes d'écart à la caisse,
nuls, déclarés.**

- *Ce qui a tourné.* Saphir (CeCILL 2.1, ses paramètres sous Licence
  Ouverte), cloné à part au commit `7bc72c9`, son seul, encore sa tête. SAS,
  logiciel propriétaire, n'est pas dans le conteneur : un évaluateur de ses
  variables macro lit ses `%let` (`Lancement.sas`, `7a-Legislation_sociale.sas`,
  `7b-Legislation_IR.sas`, sous l'indexation de 1,001 de
  `9b-Calcul_de_l_impot_sur_le_revenu_2017.sas:33`) et les évalue comme SAS,
  `round` à l'unité, la moitié loin de zéro ; ses étapes sont transcrites
  ligne à ligne, sous leurs noms : l'ASPA (`12-Prestations_20ans.sas:561-605`),
  l'abattement de 10 % des pensions
  (`8b-Calcul_de_l_impot_sur_le_revenu_2016.sas:895-960`) et celui des
  personnes âgées (`8b:599-605, 2017-2022`). Dix-sept foyers de pensions
  seules pour l'ASPA, huit avec des revenus d'activité ; vingt-quatre foyers
  de pensionnés pour chacun des impôts de 2016 et de 2017. Le dépôt :
  `droit/foyer.py` sous le barème de Saphir, comme Ines le 13 octobre ;
  `impot_revenu.py` sur `impot_revenu.yaml`. Les textes : les articles 157 bis
  et 158 du code général des impôts et R. 815-29 du code de la sécurité
  sociale, dans l'index LEGI du dépôt ; le barème de l'ASPA de la Cnav, par
  son API. Les fichiers du rejeu sont restés hors du dépôt.
- *Ce qui concorde.* L'ASPA : sa règle — une personne seule, deux
  allocataires qui se partagent par moitié ce qui manque au couple, un seul
  borné au montant d'une personne seule — est celle du dépôt sur les
  dix-sept foyers, au barème égal, à l'identique. Son barème : 800,80 € par
  mois, 1 243,24 € pour un couple, depuis le 1er avril 2016, revalorisés de
  0,3 % au 1er avril 2017, ce que la circulaire Cnav 2017/13 porte à 803,20 et
  1 246,97 € ; Saphir n'arrondit pas le mensuel (803,2024 €), et sert la
  moyenne de l'année, 9 631,22 €, quand la caisse a servi 9 631,20 €.
  L'abattement de 10 % des pensions : 379 € par pensionné au moins, borné à
  sa pension, et 3 711 € par foyer au plus pour les revenus de 2015, 3 715 €
  pour ceux de 2016, ceux du dépôt et de l'article 158, 5, a
  (LEGIARTI000032701811 et LEGIARTI000034597100). Le revenu net global est le
  même, sauf l'euro du partage du plafond (ci-dessous).
- *Ses erreurs.* L'abattement des personnes âgées : Saphir indexe lui-même
  les montants de l'année précédente et les arrondit à l'euro le plus
  proche — 2 346 € jusqu'à 14 725 € de revenu net global, 1 173 € jusqu'à
  23 724 € pour l'impôt de 2016 ; 2 348, 14 740, 1 174 et 23 748 € pour celui
  de 2017 —, quand l'article 157 bis porte 2 348 €, 14 730 €, 1 174 € et
  23 730 €, puis 2 352, 14 750, 1 176 et 23 760 € (LEGIARTI000032701889 et
  LEGIARTI000034597178), « arrondis [...] à l'euro supérieur en ce qui
  concerne les abattements et à la dizaine d'euros supérieure en ce qui
  concerne les plafonds de revenus » ; et il ne donne le plein que
  strictement sous le plafond, quand le code l'accorde à qui « n'excède pas ».
  Le dépôt suit le code. Rejoué, un foyer qui y a droit reçoit de Saphir 1 à
  8 € de moins, et, entre ses plafonds et ceux du code, la moitié ou rien de
  ce que le code lui donne : 1 174 € au lieu de 2 352 € à 14 745 € en 2016,
  rien au lieu de 1 176 € à 23 760 €. L'abattement des revenus d'activité
  dans l'ASPA, déjà au registre : un trimestre sur l'année, au lieu de
  quatre (R. 815-29, LEGIARTI000029968931 : « 0,9 fois la valeur de la
  rémunération mensuelle minimale » sur trois mois de ressources) ; pour un
  couple, à chacun des deux et non au foyer, et rien quand la personne de
  référence n'est pas éligible. Rejoué : une personne seule de 6 000 €
  d'activité et de 3 000 € de pension reçoit 1 963 € au lieu de 5 960 €. Le
  dépôt ne compte pas les revenus d'activité dans ces ressources, ce que sa
  fiche déclare.
- *Ce que le dépôt a de nul.* Sa série d'une personne seule porte en 2017
  9 638,40 €, douze fois le mensuel, quand la circulaire fixe l'annuel à
  9 638,42 € ; de même en 2007, 7 455,24 € pour 7 455,30 €. L'approximation de
  la fiche `minimum_vieillesse` ne le disait que depuis 2021 : complétée, sans
  le faire, comme la coupe du 14 octobre le veut. Le montant de l'année est
  celui du 31 décembre, 7,20 € de plus que ce que la caisse a servi en 2017 ;
  Saphir prorate la revalorisation d'avril, comme Ines : l'approximation déjà
  déclarée. Et quand deux pensionnés au plafond de l'abattement de 10 % s'en
  partagent des moitiés d'euro, le dépôt arrondit chacune au-dessus et abat
  3 712 € pour 3 711 ; Saphir abat 3 711 €, mais arrondit au-dessus les
  pensions nettes et n'en compte que 3 710 : un euro, nul, dit ici seulement.
- *Ce que les tests tiennent* (`tests/test_referents.py`) : l'ASPA de dix
  foyers, rejouée, contre la règle du dépôt sous son barème ; son barème au
  centime du mensuel en 2016 et 2017, et l'écart de l'année au montant du
  31 décembre ; trois foyers avec des revenus d'activité, son erreur posée à
  la main depuis R. 815-29 ; son abattement de 10 % de 2017 parmi les
  constats ; l'abattement des personnes âgées du dépôt, celui du code et non
  le sien, et quatre pensionnés rejoués entre ses plafonds et ceux du code ;
  et l'écart que sa ligne doit dire, vu rouge avant le registre. Le tableau
  de bord compte 234 écarts au registre, dont 202 chez les modèles
  confrontés.

**Ce qui reste.** Pour l'action 137 : EUROMOD de 2015 à 2025 ; la campagne
2025 de l'EACR, au printemps 2027 ; les `referents` des fiches, à leur
relecture. Au propriétaire, rien à trancher : l'annuel de l'ASPA de 2007 et
de 2017 au centime, s'il le voulait fait malgré la coupe, est une donnée du
scénario 1 (`minimum_vieillesse.csv`), avec les témoins qu'elle déplace. Les
erreurs de Saphir se signalent à la DG Trésor, ce qu'une session ne fait pas.
Aux pages, rien : le site ne lit pas le registre.

*Fichiers.* Le registre (ligne `saphir`), le registre des sources
(`dgtresor_saphir`), la fiche `minimum_vieillesse` (son référent Saphir et son
approximation), `tests/test_referents.py`, `docs/etat.md`, la feuille de route
(le bloc « Reprise » de l'action 137), cette note et l'entrée du journal de
veille. Ni règle, ni donnée chiffrée, ni page. Saphir et les fichiers du rejeu
sont restés hors du dépôt.
