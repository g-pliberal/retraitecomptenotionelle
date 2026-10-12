# Étape 6, la population : la place de chaque régime — le niveau des cas types statutaires, et non leur déclinaison

**Le 12 octobre 2026 : ce n'est pas la déclinaison des carrières statutaires
aux classes de salaire du privé qui les met au minimum, c'est leur niveau. La
classe médiane des militaires est au minimum garanti pour 68 % de ses
retraités, celle des fonctionnaires actifs pour 52 % ; sans déclinaison, les
militaires y seraient plus nombreux encore. La place de chaque régime dans les
quintiles des résidents, désormais certifiée et confrontée, le dit régime par
régime : la population met 60 % de ses militaires au troisième quintile de la
pension en équivalent carrière complète, l'EIR 12, qui en met 50 au
quatrième ; 88 % de ses exploitants agricoles au premier, l'EIR 41 ; et 72 %
de ses professions libérales au cinquième, pour 45. Ce sont les niveaux des
cas types de la page, que la population décline sans les changer. La
population ne change pas ; la décision revient au propriétaire.**

Demande du propriétaire : « Fait la prochaine étape » — « les carrières
statutaires déclinées aux classes de salaire du privé, que le minimum garanti
relève » (note de la quatorzième version).

- *La certification* (`scripts/fetch/drees_caracteristiques_retraites.py`,
  `scripts/verifier_donnees.py`). La feuille des quintiles des résidents porte
  aussi, quintile par quintile, la part des monopensionnés et des
  polypensionnés de deux régimes de base selon leur régime principal. Le
  récupérateur en lit les seize lignes, sous les codes de
  `caracteristiques_retraites.csv` ; une case vide s'y lit zéro, la DREES n'y
  comptant aucun retraité — aucun militaire au premier quintile des hommes. Le
  vérificateur en certifie 288 valeurs de plus, 540 en tout
  (`quintiles_eqcc_residents.csv`), et le journal 73 539 valeurs sur 150
  séries ; le parcours de présentation suit, dans le même envoi. Deux tests
  tiennent la lecture et la confrontation
  (`test_les_quintiles_des_residents_se_lisent_dans_le_fichier_certifie`,
  `test_une_grille_se_range_en_quintiles_comme_l_eir`). - *La mesure*
  (`places_des_groupes`, `grille_large.py --grille population`). Chaque groupe
  de la grille, sexe par sexe, rangé par quintile, contre son régime dans
  l'EIR des résidents, monopensionnés et polypensionnés de deux régimes, en
  pour cent de ses retraités :

  | hommes | q1 | q2 | q3 | q4 | q5 |
  |---|---|---|---|---|---|
  | régime général, EIR | 6,8 | 16,6 | 25,3 | 23,8 | 27,5 |
  | régime général, population | 7,8 | 23,5 | 21,3 | 21,0 | 26,3 |
  | État, civils, EIR | 0,1 | 0,5 | 13,9 | 27,6 | 58,0 |
  | État, civils, population | 0,0 | 3,4 | 18,0 | 33,1 | 45,5 |
  | État, militaires, EIR | 0,0 | 0,7 | 12,0 | 49,7 | 37,6 |
  | État, militaires, population | 2,3 | 11,9 | 60,0 | 14,3 | 11,5 |
  | CNRACL, EIR | 0,0 | 1,8 | 39,8 | 42,2 | 16,1 |
  | CNRACL, population | 3,3 | 10,3 | 48,6 | 23,4 | 14,4 |
  | régimes spéciaux, EIR | 0,1 | 0,8 | 11,5 | 36,9 | 50,6 |
  | régimes spéciaux, population | 0,1 | 7,1 | 14,0 | 25,7 | 53,0 |
  | MSA non-salariés, EIR | 40,8 | 51,7 | 6,4 | 1,2 | 0,0 |
  | MSA non-salariés, population | 88,3 | 9,6 | 2,0 | 0,1 | 0,0 |
  | professions libérales, EIR | 0,9 | 5,8 | 17,5 | 30,7 | 45,1 |
  | professions libérales, population | 0,9 | 1,2 | 3,2 | 22,5 | 72,2 |

  Chez les femmes, les militaires sont aussi trop bas — 27,4 % au deuxième
  quintile, aucune dans l'EIR —, la CNRACL aussi — 27,9 % au deuxième, pour
  4,3 —, les fonctionnaires civils de l'État un peu — 12,3 % au deuxième, pour
  1,2 ; les exploitantes sont à leur place, 91,7 % au premier pour 93,3 ; les
  professions libérales trop haut, 51,9 % au cinquième pour 13,5. - *Ce que la
  déclinaison y fait* (essai, hors du dépôt : la population de 2020 de la
  quatorzième version, sous les poids de la page, décomposée par classe). Chez
  les hommes, les militaires des deux classes du bas sont au minimum garanti à
  95 %, ceux de la classe médiane à 68 %, du soixante-quinzième centile à
  23 %, au-delà jamais ; en 2020, la classe médiane touche 1 157 €. Les
  fonctionnaires actifs, à 75, 69, 52 et 4 % ; les exploitants agricoles, à 77
  à 79 % de la classe du bas à celle du soixante-quinzième centile, à 27 % au
  quatre-vingt-dixième. La déclinaison ajoute au minimum les classes du bas ;
  elle en retire les classes du haut ; sans elle, chaque carrière statutaire
  serait à la place de sa classe médiane. Ce qui les met au minimum, c'est le
  cas type que la population décline : le militaire parti à 44 ans après 25
  années de services, au niveau de 0,95 salaire moyen, sans second métier ; le
  fonctionnaire actif de catégorie C, parti à 57 ans ; l'exploitant agricole,
  à la moitié du salaire moyen pour les deux sexes ; la profession libérale, à
  2,5 salaires moyens. Leurs niveaux et leurs carrières sont ceux de la page
  et du droit du scénario 1 (note du haut de l'échelle des hommes).

**Ce qui reste** de l'étape, dans l'ordre : au propriétaire, les cas types
statutaires et non salariés — leur niveau et leur carrière, que l'EIR range
autrement, désormais régime par régime —, une action à part, ou un calage du
niveau de chaque groupe de la population sur sa place dans l'EIR, qui la
détacherait des cas types de la page ; les départs avec décote ; le minimum
selon la génération ; enfin, au propriétaire, la bascule de la page.