# Étape 6, la population : les durées des résidents, la quatorzième version

**Le 12 octobre 2026 : la population, qui se mesure contre les résidents en
France, prend désormais leurs durées — la part de chaque tranche de durée
validée hors majorations, cette durée et la durée cotisée, le rang de salaire
de chaque tranche et le minimum de chaque quintile. Les carrières de moins de
trente années tombent à 7,9 % des hommes, au lieu de 11,5 — celles de
l'étranger, que l'EIR de tous les retraités comptait —, et à 32,5 % des
femmes, au lieu de 33,7. Les hommes y gagnent : leur pension moyenne passe de
1 781 à 1 803 € (1 957 dans l'EIR), leur durée validée de 37,5 à 37,9 années
selon la génération à 38,5 à 39,0 (40,4 à 40,9) ; au premier quintile de la
pension en équivalent carrière complète, l'écart moyen des dix cases de
tranche tombe de 5,6 à 4,9 points. Le minimum ne bouge guère : 16,7 % des
hommes au lieu de 17,3, pour 9,8 chez les résidents. Avant tout, la suite
complète, rouge sur l'envoi de la série des résidents, est réparée.**

Demande du propriétaire : « Fait la prochaine étape » — « caler la population
sur les résidents — l'association du rang et de la durée, et le minimum de
chaque quintile, qu'elle lit encore chez tous les retraités » (note des
résidents).

- *La suite, d'abord.* GitHub l'a trouvée rouge sur l'envoi de la série des
  résidents : `test_chaque_compte_du_parcours_est_sur_sa_page`. La page
  Données compte les séries certifiées et leurs valeurs, 150 et 73 251 depuis
  la série des résidents ; le parcours de présentation en écrivait encore 149
  et 72 999. Il les suit désormais (`docs/parcours_presentation.md`) ; vérifié
  ici sur le paquet du site refait du journal de certification, vert sur
  GitHub depuis. Une série certifiée de plus déplace la page Données, et le
  parcours avec elle : la note des quintiles de l'EIR le disait, l'étape des
  résidents l'a oublié. - *La forme* (`DUREES_DES_RESIDENTS`,
  `DureesDesResidents`, `eir`, `scripts/grille_large.py`). Les grilles lisent
  les caractéristiques de tous les retraités, leurs durées remplacées par
  celles des résidents — la colonne « ensemble » de leurs quintiles
  (`quintiles_eqcc_residents.csv`) : la part de chaque tranche, la durée
  validée hors majorations, la durée cotisée. Le rang de chaque tranche et le
  minimum de chaque quintile se lisent dans leurs quintiles. Restent ceux de
  tous : les parts des régimes, des polypensionnés et des femmes, que le dépôt
  ne certifie pas chez les résidents ; et la durée des carrières pleines
  (`durees_pleines`) : l'EIR arrondit ses durées moyennes à l'année, et celle
  des résidentes, au même arrondi, la déplacerait d'une année, à 43,1 au lieu
  de 44,0, sans rien en apprendre. La composition de l'EIR normalise ses
  tranches comme la population, celles des résidentes faisant 99,9 %. Un test
  tient la forme (`test_la_population_prend_les_durees_des_residents`). - *La
  composition*, retraités de 2020 : les carrières de moins de trente années
  hors majorations, 32,5 % des femmes et 7,9 % des hommes, celles des
  résidents, au lieu de 33,7 et 11,5 ; la durée validée hors majorations, 31,7
  années pour les femmes au lieu de 31,4 (32,0 chez les résidentes), 38,9 pour
  les hommes au lieu de 37,8 (40,0). - *Les pensions de 2020 contre l'EIR*, en
  euros par mois ; Kolmogorov : le plus grand écart des répartitions, et la
  borne où il tombe :

  | | moyenne | d1 | d3 | médiane | d9 | Kolmogorov |
  |---|---|---|---|---|---|---|
  | ensemble, EIR | 1 536 | 402 | 933 | 1 382 | 2 730 | |
  | ensemble, treizième version | 1 557 | 599 | 1 067 | 1 377 | 2 684 | −9,9 pt à 900 |
  | ensemble, quatorzième | 1 569 | 639 | 1 080 | 1 377 | 2 684 | −10,9 pt à 900 |
  | femmes, EIR | 1 177 | 283 | 703 | 1 013 | 2 229 | |
  | femmes, treizième version | 1 348 | 465 | 928 | 1 237 | 2 294 | −17,4 pt à 900 |
  | femmes, quatorzième | 1 349 | 463 | 929 | 1 249 | 2 294 | −17,2 pt à 900 |
  | hommes, EIR | 1 957 | 872 | 1 374 | 1 745 | 3 242 | |
  | hommes, treizième version | 1 781 | 871 | 1 245 | 1 631 | 2 892 | +8,0 pt à 1 400 |
  | hommes, quatorzième | 1 803 | 909 | 1 248 | 1 631 | 2 892 | +7,8 pt à 1 400 |

  - *La pension en équivalent carrière complète*, contre les résidents. Au
  premier quintile, la part de chaque tranche : chez les femmes, 82,1 % de
  celles de moins de dix ans (83,5 chez les résidentes), 68,8 de dix à vingt
  (66,0), 47,2 de vingt à trente (48,2), 19,6 de trente à quarante (21,0),
  15,2 de quarante et plus (11,0) ; chez les hommes, 71,1 (73,1), 40,8 (34,3),
  2,9 (23,8), 5,8 (7,4), 11,5 (4,3). L'écart moyen des dix cases tombe de 5,6
  à 4,9 points. Au minimum, 32,7 % des femmes au lieu de 32,8 (37,7), 16,7 %
  des hommes au lieu de 17,3 (9,8). Les hommes du premier quintile, 10,5 % des
  hommes (7,2 chez les résidents), sont proratisés à 90,4 % au lieu de 81,8
  (76,1) et valident 36,9 années au lieu de 32,9 (32,0) ; ceux du deuxième,
  94,2 % au lieu de 90,9 (97,1), et 39,7 années au lieu de 38,1 (40,0). Aux
  trois quintiles du haut, les hommes valident toujours 37,8 à 39,6 années,
  pour 42. - *Le minimum contributif* (`part_minimum_contributif.py`) : en
  2023, 15,3 % des liquidants au lieu de 16,1 (EACR 18,8), les hommes à 7,0 %
  au lieu de 8,8 (12,2) ; en 2024, 18,9 % au lieu de 20,0 (18,6 estimée), les
  hommes à 10,9 % au lieu de 13,0 (12,7). Son montant moyen, 115 € en 2023 au
  lieu de 108 (134 à 138), 140 € en 2019 au lieu de 131 (139 à 142). - *Sur la
  page*, contre la treizième version : l'écart des années observées passe de
  −1,39 à −1,38 point au scénario 2, de −3,12 à −3,11 aux scénarios 4 et 6 ;
  la part du PIB en 2070 ne bouge qu'au centième ; le coefficient de 2070 du
  scénario 2 passe de +0,118 à +0,115 ; la garantie de +0,050 à +0,046 point ;
  le passé refait, au pire depuis 2000, de 17,1 à 17,2 %. - *Ce que la mesure
  accuse.* Les hommes au minimum ne le sont pas par le minimum contributif,
  dont ils prennent désormais moins que l'EACR, mais par les minima des
  carrières statutaires et des exploitants agricoles (note des résidents) : le
  premier quintile de la population a des carrières longues au minimum, là où
  celui de l'EIR en a de courtes.

**Ce qui reste** de l'étape, dans l'ordre : les carrières statutaires
déclinées aux classes de salaire du privé, que le minimum garanti relève ; les
départs avec décote ; le minimum selon la génération ; enfin, au propriétaire,
la bascule de la page — et, s'il le veut, une action à part pour les
catégories des régimes statutaires. La quatorzième version reste en place,
débrayable par sa constante.