# Étape 6, la population : les quintiles des résidents de l'EIR, certifiés, et la population mesurée contre eux

**Le 12 octobre 2026 : la population ne compte que des résidents, et se mesure
désormais contre eux. La feuille des quintiles en équivalent carrière complète
du classeur des résidents en France de l'EIR 2020 est certifiée
(`quintiles_eqcc_residents.csv`) : 252 valeurs, avec la durée validée, la
durée cotisée et la part des départs avec décote. Contre les résidents, un
écart tombe : la proratisation des hommes du premier quintile, 76,1 % chez eux
et non 47,6 — les retraités de l'étranger, aux carrières françaises courtes,
faisaient le premier quintile de tous —, quand la population en a 81,8. Deux
autres se creusent : 17,3 % des hommes au minimum, pour 9,8 chez les
résidents, dont six points de militaires et de fonctionnaires actifs, que la
population décline aux classes de salaire du privé ; et les hommes des trois
quintiles du haut valident 37,6 à 39,5 années, pour 42. La population ne
change pas.**

Demande du propriétaire : « Effectue la prochaine étape » — « certifier le
classeur des résidents de l'EIR, et y confronter la population, qui ne compte
qu'eux » (note de la treizième version).

- *La certification* (`scripts/fetch/drees_caracteristiques_retraites.py`,
  `scripts/verifier_donnees.py`). Le jeu de la DREES joint à chaque millésime
  trois classeurs : tous les retraités, ceux qui résident en France, une
  génération. Le récupérateur lit désormais aussi le deuxième, du même
  millésime, et sa feuille « QuintilesEQCC », sous les mêmes contrôles : les
  tranches font cent, les quintiles redonnent l'effectif, et chacun en compte
  le cinquième, 3 096 milliers de résidents. Il y lit les onze indicateurs des
  quintiles de tous les retraités, et trois de plus : la durée validée,
  majorations comprises ; la durée cotisée ; la part des départs avec décote.
  Le vérificateur en certifie 252 valeurs, et retrouve identiques les 444 déjà
  certifiées du classeur de tous. Deux tests tiennent la lecture
  (`test_les_quintiles_des_residents_se_lisent_dans_le_fichier_certifie`,
  `test_une_grille_se_range_en_quintiles_comme_l_eir`). - *La mesure*
  (`grille_large.py --grille population`). La confrontation lit les quintiles
  des résidents, et y ajoute la durée validée de chaque quintile ; la
  population se construit encore sur ceux de tous les retraités
  (`RANG_SELON_LA_DUREE`, `MINIMUM_AU_PREMIER_QUINTILE`). La treizième
  version, contre les résidents et contre tous, en pour cent et en années :

  | femmes | q1 | q2 | q3 | q4 | q5 | ensemble |
  |---|---|---|---|---|---|---|
  | proratisation, résidentes | 71,3 | 89,7 | 97,0 | 98,9 | 98,5 | |
  | proratisation, toutes | 66,5 | 87,0 | 96,0 | 98,6 | 98,2 | |
  | proratisation, population | 76,2 | 89,4 | 94,3 | 96,9 | 97,7 | |
  | au minimum, résidentes | 65,9 | 52,7 | 18,1 | 9,3 | 0,9 | 37,7 |
  | au minimum, toutes | 64,3 | 59,9 | 18,4 | 9,9 | 1,1 | 38,5 |
  | au minimum, population | 84,3 | 23,2 | 18,0 | 2,7 | 0,0 | 32,8 |
  | durée validée, résidentes | 28,0 | 38,0 | 41,0 | 41,0 | 41,0 | |
  | durée validée, population | 31,0 | 37,7 | 39,5 | 41,6 | 41,6 | |

  | hommes | q1 | q2 | q3 | q4 | q5 | ensemble |
  |---|---|---|---|---|---|---|
  | proratisation, résidents | 76,1 | 97,1 | 101,3 | 100,5 | 99,4 | |
  | proratisation, tous | 47,6 | 88,5 | 99,1 | 100,0 | 98,5 | |
  | proratisation, population | 81,8 | 90,9 | 91,7 | 94,2 | 95,0 | |
  | au minimum, résidents | 48,7 | 25,2 | 6,2 | 3,5 | 0,4 | 9,8 |
  | au minimum, tous | 51,5 | 32,6 | 6,2 | 3,9 | 0,4 | 12,4 |
  | au minimum, population | 74,0 | 22,1 | 23,3 | 0,0 | 0,0 | 17,3 |
  | durée validée, résidents | 32,0 | 40,0 | 42,0 | 42,0 | 42,0 | |
  | durée validée, population | 32,9 | 38,1 | 37,6 | 39,1 | 39,5 | |

  Au premier quintile, la part de chaque tranche de durée des femmes est, chez
  les résidentes, de 83,5 % pour moins de dix ans, 66,0 de dix à vingt, 48,2
  de vingt à trente, 21,0 de trente à quarante, 11,0 de quarante et plus
  (population : 81,4, 66,0, 42,8, 19,1, 15,1) ; l'écart moyen des dix cases de
  tranche reste à 5,6 points. - *Les hommes au minimum* (essai, hors du
  dépôt : la population de 2020, sous les poids de la page, décomposée). Des
  17,3 % au minimum, le salariat privé fait 6,7 points — sa classe du bas,
  7,8 % des hommes, y est à 77,9 % —, les militaires 3,9 points, 57,3 %
  d'entre eux, les exploitants agricoles 3,9, les fonctionnaires actifs 2,1.
  Les militaires de l'EIR sont aux quintiles du haut : monopensionnés, 0,2 %
  des hommes résidents du deuxième, 1,9 du troisième, 5,8 du quatrième, 3,2 du
  cinquième. La population décline chaque carrière statutaire, autour de son
  niveau, aux écarts de la distribution des salaires du privé de son sexe ;
  les classes les plus basses tombent au minimum garanti. - *Les carrières des
  hommes du haut.* Aux trois quintiles du haut, ils valident 37,6 à 39,5
  années, majorations comprises, pour 42 chez les résidents, et leur
  proratisation reste de 92 à 95 %, pour 99 à 101 : les carrières statutaires
  courtes et la tranche de trente à quarante ans, que la note du haut de
  l'échelle des hommes décomposait.

**Ce qui reste** de l'étape, dans l'ordre : caler la population sur les
résidents — l'association du rang et de la durée, et le minimum de chaque
quintile, qu'elle lit encore chez tous les retraités — ; les carrières
statutaires déclinées aux classes de salaire du privé, que le minimum garanti
relève ; les départs avec décote ; le minimum selon la génération ; enfin, au
propriétaire, la bascule de la page — et, s'il le veut, une action à part pour
les catégories des régimes statutaires.