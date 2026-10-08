# Étape 17, dixième partie : la majoration de l'Agirc-Arrco pour enfants à charge

**Le 8 octobre 2026, la demande.** La troisième du reste de l'étape : l'Arrco,
l'Agirc puis l'Agirc-Arrco majorent l'allocation de qui part avec un enfant à
charge, au lieu de la majoration pour enfants nés ou élevés quand c'est plus ;
OpenFisca-France-Pension et Til-Pension la servent (registre, chantier 138.17),
et la fiche `majoration_enfants_agirc_arrco` la disait « pas modélisée ».

**Ce que dit le droit, lu le jour même** (journal de veille du 8 octobre ; fiche
`majoration_enfants_a_charge_agirc_arrco`).

- *L'Arrco, depuis 1999* : 5 % de l'allocation « pour chaque enfant à charge […]
  à la date de liquidation de l'allocation et aussi longtemps que l'enfant reste
  à charge », sans cumul avec les 5 % des trois enfants élevés (accord du 25 avril
  1996, articles 12 et 13).
- *L'Agirc, depuis 2012* (accord du 18 mars 2011, article 8), et l'une et l'autre
  dès lors sur « 5 % des droits bruts de l'ensemble de la carrière par enfant à
  charge », la plus élevée des deux majorations servie (annexe A, article 17 ;
  annexe I, article 6 bis).
- *L'Agirc-Arrco, depuis 2019* (accord du 17 novembre 2017, articles 93 à 96) :
  l'enfant à charge a moins de dix-huit ans, de dix-huit à vingt-cinq ans s'il
  étudie, est apprenti ou demandeur d'emploi non indemnisé, ou il est invalide
  avant vingt et un ans ; la majoration se calcule « sans tenir compte des
  coefficients d'anticipation », n'est « pas plafonnée », cesse « au fur et à
  mesure » que les enfants cessent d'être à charge, et, à montant égal, la
  majoration pour enfants nés ou élevés est servie (circulaire n° 2020-02-DRJ,
  fiche 4).

**Ce qui est fait.**

- *La fiche*, quatre versions : rien avant 1999 ; l'Arrco seule, sur
  l'allocation ; l'Arrco et l'Agirc, chacune sur ses droits bruts ; une seule
  allocation depuis 2019.
- *Le modèle* (`completer.majoration_pour_enfants_a_charge`, son jumeau) : à la
  date d'effet, chaque allocation compare 5 % de son assiette par enfant de moins
  de dix-huit ans à sa majoration pour enfants nés ou élevés, plafond compris ; ce
  qui la passe s'ajoute à la majoration pour enfants, que la cascade, la page et
  l'échéancier lisent déjà. La majoration garde ses étapes
  (`AvantageApplique.a_charge`), une par anniversaire, et la revalorisation,
  l'échéancier et les deux mesures de septembre 2023 servent, à chaque date,
  celle qui court (`commun.parts_de_la_majoration`). L'assiette sans le
  coefficient d'anticipation vient de la liquidation (`Pensions.anticipations`).
- *Les tests* : `test_majoration_enfants_a_charge.py`, dix cas, dont les quatre
  versions, l'assiette sans coefficient, le non-cumul, la fin de la charge à
  chaque échéance et les deux moteurs ; un témoin neuf de simulation,
  `enfants_a_charge_agirc_arrco`.

**Les mesures.** Aucune carrière de la grille ne part avec un enfant de moins de
dix-huit ans, que seule une naissance déclarée peut donner : un seul témoin bouge,
la mère née en 1948 partie à soixante ans en 2008 avec un enfant de quatre ans, de
+1,52 % — 5 % de son allocation Arrco, jusqu'en 2022. Le témoin neuf, le salarié
parti à l'âge légal en 2022 avec deux enfants de quatorze et neuf ans, voit sa
complémentaire majorée de 613 € par an, 10 % de ses droits sans le coefficient
d'anticipation, puis de la moitié depuis janvier 2026, et de rien en mai 2030.

**Ce qui reste.**

1. *La majoration pour enfants nés ou élevés sans le coefficient
   d'anticipation* : la même circulaire la calcule ainsi (fiche 4, II.2.1), le
   modèle sur l'allocation ; sous un coefficient, il la sous-estime, et l'enfant
   à charge l'emporte plus souvent qu'il ne le devrait.
2. *L'enfant de dix-huit à vingt-cinq ans qui étudie, et l'enfant invalide*, que
   la saisie ne porte pas : le modèle ne tient pour à charge que l'enfant de moins
   de dix-huit ans.
3. *Avant 2019* : la définition de l'enfant à charge des deux régimes, et les
   règlements des caisses de l'Arrco d'avant 1999.
4. *De l'étape 17, ensuite* : la majoration pour conjoint à charge.
