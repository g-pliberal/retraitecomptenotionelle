# Étape 8, seizième partie : la pension majorée de référence revue quand la situation ou les ressources changent

**Le 19 octobre 2026, la demande.** Le deuxième reste de l'étape, dans
l'ordre du bloc « Reprise », sa saisie faite la même nuit (note « saisie de
la réversion ») : la PMR revue quand les ressources changent (D. 732-114),
dont la réversion ouverte après le départ d'une pension prise de 2009 à 2021,
au modèle et dans le portage. Session 14 de la deuxième salve de la vague du
19 octobre ; ni la durée de chef reconstituée, qui suit, ni l'année du décès
de l'exploitant (action 131).

**Ce que dit le droit** (journal de veille du 19 octobre, index LEGI à jour
au 18 octobre).

- *La révision* : « Toute modification de la situation familiale ou du
  montant des ressources donne lieu à une révision de la majoration de
  pension. La majoration de pension recalculée prend effet à compter du
  premier jour du mois suivant la date à laquelle est constatée la
  modification » (D. 732-114, rédactions de 2009 et de 2026).
- *Le recalcul* : « Le cas échéant, le montant de la majoration est
  recalculé en fonction du montant des pensions versées au bénéficiaire, de
  l'évolution du montant minimum prévu à l'article L. 732-54-2 du présent
  code et de l'évolution du plafond » (L. 732-54-3, rédactions de 2008, 2023
  et 2026), les pensions « français et étrangers » comprises.
- *Les montants* : PMR1, PMR2 puis PMRmax, et le plafond, revalorisés comme
  les pensions de base jusqu'en août 2023 (D. 732-111, D. 732-113) ; depuis,
  PMRmax des pensions prises avant septembre 2023 toujours comme elles, et le
  plafond, que D. 732-113 dit après ses I et II « revalorisé aux mêmes dates
  et dans les mêmes proportions que le salaire minimum de croissance ».

**Ce qui est fait**, dans les deux moteurs.

- *Le changement* : `modification_constatee` (`modificationConstatee`) dit
  si la situation ou les ressources ont changé depuis la date d'effet de la
  pension agricole, autrement que par les revalorisations, à temps pour
  l'échéance : la réversion du régime ouverte depuis, au plus tard le mois de
  l'échéance — elle commence le mois qui suit le décès, le veuvage qui
  révise — ; une pension étrangère, ou une autre pension, que l'assuré
  demande plus tard, commencée depuis, au plus tard le mois qui précède, la
  révision prenant effet le mois qui suit.
- *La révision* : `reviser_les_exploitants` (`reviserLesExploitants`) refait
  alors à l'échéance la majoration de toute pension prise depuis 2009, à la
  règle de sa date d'effet, que la liquidation a servie : la PMR et le
  plafond de l'échéance, la pension de base avant surcote, la réversion du
  régime retranchée et comptée au plafond, toutes les pensions de
  l'échéance ; la base porte la différence avec la majoration de la
  liquidation menée par le coefficient. Avant 2022 pour une pension prise de
  2009 à 2021, à toute échéance pour une pension prise depuis ; depuis 2022,
  la PMR unique refaisait déjà les premières.
- *La fiche* `pension_majoree_reference` : ses écarts de la réversion et de
  la majoration d'une pension prise depuis 2009 disent la révision servie et
  la saisie faite ; la lecture du 19 octobre ; D. 732-114 de 2026 et
  L. 732-54-3 de 2023 rattachés à leurs versions, le cliquet des textes
  descendu de deux (9 657).
- *Les tests* (`tests/test_minima_agricoles.py`) : la veuve de juin 2018,
  révisée en 2018 et en 2021, rien avant ni sans réversion ; la pension
  allemande de décembre 2017, qui écrête la majoration en janvier 2018, pas
  avant ; le régime général demandé à soixante-cinq ans, qui l'écrête le
  mois qui suit ; la pension prise en 2022, veuve en 2023 ; « faire vivre » à
  l'année dite dans les deux moteurs, sur sept échéances.

**Les mesures.** La conjointe collaboratrice partie en février 2016, veuve
en juin 2018 à 150 € par mois : 468,91 € de majoration en décembre 2018 —
8 248,06 € de PMR du chef sur ses 164 trimestres, moins 5 979,15 € de
pension avant surcote et 1 800 € de réversion —, au lieu des 988,13 € de la
liquidation menés par le coefficient ; 476,90 € au lieu de 1 005,01 € en
décembre 2021. La même, avec 500 € par mois d'une pension allemande depuis
décembre 2017 : plus de majoration en décembre 2018. Vingt ans de salarié
puis vingt-deux de chef, parti en 2012, son régime général demandé en 2015 :
plus de majoration depuis. La conjointe partie en février 2022, veuve en
mars 2023 : 1 800,01 € de moins en décembre 2023, ce que sa réversion sert.

**Ce qui n'est pas fait.**

- Entre deux révisions, la majoration suit le coefficient : ce que les
  complémentaires, revalorisées autrement, et le plafond, indexé sur le SMIC
  depuis septembre 2023, changent à l'écrêtement ne la révise pas, ni la fin
  d'une majoration pour enfant à charge ; une pension commencée le mois de
  l'échéance compte aux ressources d'une révision qu'un autre changement
  ouvre. Déclaré dans la fiche.
- *Un défaut trouvé*, que la révision lit comme la PMR de 2009 et la PMR
  unique : pour les pensions prises avant septembre 2023, la table
  `pension_majoree_reference.csv` ne porte la PMR et le plafond que jusqu'au
  31 août 2023 (`FINS` de `scripts/fetch/dila_legi_pension_majoree.py`, fait
  pour la seule liquidation) ; aux échéances d'après, le modèle les
  extrapole, fiabilité estimée : 9 567,86 € de PMR entière en décembre 2026
  au lieu de 9 741,00 € (8 970,86 € de janvier 2023 revalorisés de 5,3 %,
  2,2 % et 0,9 %, au centime inférieur). Déclaré dans la fiche ; le premier
  reste.

**Ce qui reste**, de l'étape, dans l'ordre :

1. Les montants d'après août 2023 des pensions prises avant septembre 2023 :
   la PMR, revalorisée comme les pensions de base (D. 732-111) ; le plafond,
   en lisant si la phrase du SMIC de D. 732-113 vaut pour son I ; la série
   prolongée par le script, son test d'abord.
2. La durée de chef reconstituée de D. 732-110, III.
3. Ce que la réversion déclarée permet de servir aux plans de 1997 à 2008
   (D. 732-118, D. 732-116, D. 732-147), point 4 de la note « réversion du
   régime ».
4. À la fin de l'étape, la fiche `complement_differentiel_rco`.
5. Inchangés : les points 2 et 3 de « Ce qui reste » de la note « points des
   conjoints » ; au propriétaire, le montant de la MSA pour 2015 à 2017 et
   2019, depuis un poste qui atteint l'archive du web, et les seize points
   d'une année de conjoint d'avant 1999.
