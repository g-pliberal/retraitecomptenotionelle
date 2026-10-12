# Étape 6, la population : le haut de l'échelle des hommes — la tranche de trente à quarante ans et les carrières statutaires

**Le 12 octobre 2026 : ni la tranche de trente à quarante ans ni la mesure ne
sont en cause. Lues par moindres carrés dans les quintiles de l'EIR, les
carrières de trente à quarante ans durent 33 ans pour les hommes, 34 pour les
femmes ; la population leur en donne 35, et n'a pas à les allonger. Ce qui
abaisse la proratisation des hommes aux deux quintiles du haut — 94 et 95 %,
pour 100 et 98,5 dans l'EIR —, ce sont pour près des deux tiers les carrières
statutaires : l'agent de conduite SNCF, le militaire, le fonctionnaire actif
et l'agent des IEG, proratisés de 78 à 88 %. Chaque régime statutaire y est
représenté par sa catégorie la plus précoce, et le droit du modèle ne connaît,
à la SNCF, que les agents de conduite : ce n'est pas à la population de le
changer. Elle ne change pas ; la mesure compte désormais la proratisation de
chaque quintile.**

Demande du propriétaire : « Fait la prochaine étape » — « le haut de l'échelle
des hommes — la durée de la tranche de trente à quarante ans, et la
proratisation des carrières statutaires » (note de la onzième version).

- *La durée de la tranche de trente à quarante ans* (essai, hors du dépôt).
  L'EIR donne, quintile par quintile de la pension en équivalent carrière
  complète, la durée validée moyenne hors majorations, arrondie à l'année, et
  la part de chaque tranche (`quintiles_eqcc.csv`). Les trois tranches courtes
  comptées à leur milieu, les moindres carrés des cinq quintiles de chaque
  sexe donnent 44,1 années aux carrières de quarante ans et plus et 33,1 à
  celles de trente à quarante pour les hommes, 44,9 et 34,1 pour les femmes, à
  des résidus de 0,6 année au plus, l'ordre de l'arrondi. La population, qui
  leur donne 35 ans, n'a pas à les allonger. La proratisation presque entière
  que l'EIR leur trouve au haut de l'échelle tient à autre chose : la durée
  requise des générations anciennes, de 37,5 à 40 années, les bonifications,
  la somme des coefficients des polypensionnés. - *Ce qui abaisse la
  proratisation du haut* (essai : la population de 2020, sous les poids de la
  page, décomposée). Au quatrième quintile, les hommes sont proratisés à
  94,4 % ; les carrières statutaires font 56 % du manque — l'agent de conduite
  20,6 %, le militaire 15,7, le fonctionnaire actif 13,4, l'agent des IEG 6,2
  —, le salariat privé de trente à quarante ans 16,8. Au cinquième, proratisés
  à 95,1 %, les carrières statutaires en font 64 % — l'agent de conduite 27,0,
  l'agent des IEG 17,5, le militaire 10,7, le fonctionnaire actif 9,2 —, le
  salariat privé de trente à quarante ans 16,5. La mesure ne s'y trompe pas :
  la simulation proratise ces carrières comme leur régime, « 120/150 » pour
  l'agent de conduite né en 1950, ses trente années de services, « 120/150 »
  pour le militaire, la bonification du cinquième comprise, « 132/154 » pour
  le fonctionnaire actif. Leurs carrières sont courtes. - *Pourquoi elles le
  sont.* Chaque régime statutaire est représenté par un cas type, celui de sa
  catégorie la plus précoce : l'agent de conduite, ouvert à 50 ans, puis
  jusqu'à 54 ; le militaire, parti à 44 ans sans second métier ; le
  fonctionnaire actif, à 57. Le droit du modèle ne connaît, à la SNCF, que les
  âges des agents de conduite (`sncf.yaml`), et aucune bonification de
  traction ; les autres agents du régime partent à 55 ans, puis 57. Ce sont
  les règles du scénario 1 et les cas types de la page : la population ne les
  change pas. - *Les poids de la page* (essai). Repesée aux parts de régime
  principal de l'EIR, la population donne aux hommes une pension moyenne de
  1 793 € au lieu de 1 761, un premier décile de 884 € au lieu de 857, une
  médiane de 1 634 € au lieu de 1 631. Le recalage de la page sur la dépense
  des groupes du COR, qui y compte 6,3 % de militaires et 6,3 % d'exploitants
  agricoles parmi les hommes, pour 4,3 et 4,2 % dans l'EIR, ne fait qu'une
  petite part de l'écart. - *La mesure* (`grille_large.py --grille
  population`) : la confrontation à l'EIR moyenne désormais, quintile par
  quintile, la proratisation de la population, contre celle de l'EIR, la somme
  des coefficients des régimes de base :

  | | q1 | q2 | q3 | q4 | q5 |
  |---|---|---|---|---|---|
  | femmes, EIR | 66,5 | 87,0 | 96,0 | 98,6 | 98,2 |
  | femmes, population | 70,1 | 86,8 | 92,7 | 96,4 | 97,1 |
  | hommes, EIR | 47,6 | 88,5 | 99,1 | 100,0 | 98,5 |
  | hommes, population | 81,8 | 91,0 | 92,0 | 94,4 | 95,1 |

  Au premier quintile des hommes, l'EIR compte les retraités de l'étranger,
  aux courtes carrières françaises, que la population n'a pas.

**Ce qui reste** de l'étape, dans l'ordre : la pension des femmes, trop haute
par année validée au bas de l'échelle ; le minimum selon la génération ;
enfin, au propriétaire, la bascule de la page. Au propriétaire aussi : les
catégories des régimes statutaires — les sédentaires de la SNCF, les officiers
et le second métier des militaires — tiennent au droit du scénario 1 et aux
cas types de la page, hors de la population ; c'est, s'il le veut, une action
à part.
