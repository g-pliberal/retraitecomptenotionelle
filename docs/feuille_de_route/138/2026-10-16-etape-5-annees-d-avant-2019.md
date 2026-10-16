# Étape 5, sixième partie : les années d'avant 2019 de l'effet retour, chacune au barème de CSG de son année

**La demande.** Le point 4 de « Ce qui reste » de
`2026-10-14-etape-5-effet-retour.md` : l'effet retour valait zéro avant 2019,
faute de barème, et les années suivantes prenaient toutes celui de 2026,
ramené sur les prix.

**Ce qui est fait.**

- `data/reference/legislation/csg_pensions_seuils.csv` : la règle et les
  seuils de chaque année de 1991 à 2025, pour une part, lus aux textes. Trois
  règles. De 1991 à 1997, l'exonération quand l'impôt n'est pas mis en
  recouvrement (L. 136-2, III, 2°) ; le taux de 1 % de 1997 (L. 136-8, II)
  ne touche personne qui n'a que sa pension. De 1998 à 2014, l'exonération
  sous le seuil du I de l'article 1417 du CGI, le taux réduit quand l'impôt
  n'est pas mis en recouvrement (L. 136-8, III). Depuis 2015, le revenu fiscal
  seul, contre les seuils de L. 136-8, III. Les seuils de 1998 à 2007 sont
  ceux des arrêtés annuels de la taxe d'habitation, lus au Journal officiel
  par l'index de la DILA ; de 2008 à 2014, l'article 1417 dans LEGI ; de 2015
  à 2025, L. 136-8 et les barèmes de l'IPP. La CSG d'une année prend le seuil
  de la taxe d'habitation de l'année précédente : 10 224 € pour 2014, que
  L. 136-8 porte à 10 633 € en 2015.
- `effet_retour.py` : `charger_seuils_csg`, `tranche_csg`, et
  `EffetRetour._preleve_historique`, qui applique à chaque année d'avant 2026
  sa règle, ses seuils et ses taux (`prelevements_historiques.yaml`, moyenne
  des douze mois) : la CSG de la tranche, la CRDS hors exonération, la CASA au
  taux plein (au taux médian aussi depuis 2019), et l'impôt de l'année sur la
  pension nette de la part déductible de la tranche. Jusqu'aux revenus de 2005,
  le revenu fiscal suit l'abattement de 20 % (la réforme de 2006 relève le
  seuil de 7 417 à 9 437 €). Avant février 1991, l'impôt seul.
  `PREMIERE_ANNEE_EFFET_RETOUR` disparaît : chaque année de la trajectoire,
  depuis 1990, a son effet retour. 2026 et les suivantes ne bougent pas.

**Ce que cela donne**, sous la référence. De 1990 à 2018, l'effet retour
reprend 24,7 % de l'économie du scénario 2 et 23,2 % du 4 ; de 2019 à 2025,
26,8 et 27,5 % (26,8 et 27,8 au barème de 2026) ; de 2026 à 2070, 27,4, 29,5,
30,5 et 31,8 % des scénarios 2 à 5, inchangés. Les prélèvements d'un euro
d'économie montent de 4 % en 1990, l'impôt seul, à 10 % en 1998 et 15 % en
2025 ; l'ASPA, elle, en reprend davantage à mesure qu'on remonte : 12 % en
2018, 19 % en 1990 (scénario 2). Aucun témoin
ni chiffre ancré ne porte l'effet retour : rien d'une page ne bouge.
`tests/test_effet_retour.py` tient les seuils lus, la tranche de chaque
règle, un effet retour à chaque année, croissant avec la CSG, et l'ordre de
grandeur des années passées.

**Limites**, à reporter dans `docs/limites/5-bis-cout-agrege.md` à la fin de
l'étape : le revenu et l'impôt sont ceux de l'année même, non ceux de
l'avant-dernière et de la précédente que la loi regarde ; l'abattement de
10 % est celui de 2026, ramené sur les prix ; le seuil de 2002 (CSG de 2003)
est interpolé, l'arrêté manquant à l'index ; en 1999 et 2000, L. 136-2
renvoie au I de l'article 1417, qu'une loi de finances venait de couper en
deux (25 200 F au I, 43 900 F au I bis) : la table suit la série, au I bis ;
la tranche se décide sur l'impôt au taux plein déductible, à la marge près.

**Ce qui reste** de l'étape, dans l'ordre : au propriétaire, si l'effet retour
entre dans le solde ; son affichage, à la session du site ; l'impôt au site,
le bénéfice des indépendants, les règles d'avant 1981.
