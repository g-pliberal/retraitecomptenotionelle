# Étape 1, les militaires : le cas type au militaire moyen du jaune budgétaire

**Le 12 octobre 2026 : le cas type militaire part désormais à quarante-huit
ans et demi, après vingt-sept ans et demi de services, à 1,15 salaire moyen ;
il partait à quarante-quatre ans, après vingt-cinq ans, à 0,95. C'est le
militaire moyen des départs pour ancienneté que le Service des retraites de
l'État publie dans le jaune budgétaire, et non plus un non-officier des
armées parti tôt, qui portait pourtant le poids de tous. La
population met désormais 51,5 % de ses militaires hommes aux deux quintiles du
haut, contre 25,8 % ; l'EIR, 87,3 %. Ce qui l'en sépare encore tient à la
population, non au cas type : elle décline chaque carrière statutaire sur la
dispersion des salaires du privé, dont les classes du bas tombent au minimum
garanti.**

Demande du propriétaire : « Lance l'action 152 ». Décidé par lui le même jour,
sur la lecture ci-dessous : déplacer le cas type existant plutôt que lui en
adjoindre un second, et traiter les groupes dans l'ordre du plan.

- *Ce qui place le groupe.* Le rapport sur les pensions de retraite de la
  fonction publique annexé au PLF 2026 (`sre_jaune_pensions`), lu dans le PDF
  du miroir de l'Assemblée nationale, d'empreinte conforme au manifeste. Les
  9 655 militaires partis pour ancienneté en 2024, 85,7 % d'hommes, sont radiés
  à 48,7 ans, après 110,1 trimestres de services et 37,5 de bonifications, à
  l'indice 585, et touchent 1 900 € par mois (tableau B-3). Chez les hommes,
  70 % sont sous-officiers (1 846 €), 16 % officiers, 14 % caporaux et soldats
  (1 172 €) (tableau B-18). Par armée, tous motifs de départ confondus, les
  non-officiers de terre, de mer et de l'air partent à 41,6 ans après 82,5
  trimestres de services, à 1 180 € ; les gendarmes non officiers à 51,5 ans,
  à 2 142 € ; les officiers à 52,1 et 56,3 ans, à 2 935 et 3 501 € (tableau
  B-4). L'indice de liquidation vaut de 0,83 à 0,98 salaire moyen de 2003 à
  2024, 0,90 en moyenne (tableau 98, rapporté au point d'indice et au salaire
  moyen du dépôt), et les pensions militaires de droit direct en paiement,
  1 705 € par mois en 2020, accessoires compris (tableau A-4). L'EIR range ces
  retraités aux quintiles du haut, et les deux tiers d'entre eux sont
  monopensionnés : ce n'est pas le second métier qui les y met.
- *Ce qui en écartait le cas type.* Le niveau d'abord : sa solde finale valait
  0,71 salaire moyen, contre 0,90. La carrière ensuite : vingt-cinq ans de
  services et cinq de bonification, radié à quarante-quatre ans, contre 27,5,
  9,4 et 48,7. Il touchait 1 310 € en partant en 2024, et 1 195 € en moyenne
  aux militaires de 2020, pesés comme la page les pèse.
- *La correction* (`castypes.py`). Entré à vingt et un ans, radié après
  vingt-sept ans et demi de services, à 1,15 salaire moyen : 0,90 à la
  radiation, les primes comptées pour un quart, part inchangée faute de
  source. Il touche 1 825 € en partant en 2024, et 1 593 € en moyenne aux
  militaires de 2020 : 7 % sous les 1 705 € du SRE, accessoires compris, et
  2 % sous son avantage principal, au rapport que le tableau A-5 donne en
  2023. Ce qui manque est
  la part des bonifications que le simulateur ne saisit pas : les bénéfices de
  campagne et le service aérien, à 79,4 % et 58,3 % des liquidants de 2023,
  pour 13,1 et 11 trimestres et 101 et 69 € par mois chez leurs bénéficiaires
  (tableau 50). Le libellé et le commentaire de la page suivent, comme le
  parcours de présentation, deux fiches (`cas_types_csp.yaml`,
  `avantages_non_contributifs.yaml`) et trois tests.
- *Ce que ça déplace.* Aucun témoin de simulation ; 54 rendus de page sur 70,
  la plupart par la page Coût, que les autres citent. Carrières types : le
  militaire de la génération 2000 passe de +40 à +14 % au système 4, toujours
  le mieux traité, 48 points devant la carrière interrompue, contre 75 ; celui
  de la génération 1980, radié en 2028 et non plus en 2024, après la bascule,
  passe de −51 à +45 %. Coût : l'écart du passé passe de −78,9 à −79,0 % au
  scénario 2, la part du PIB du scénario 3 en 2070 de 7,1 à 7,0 %. Programme :
  la baisse médiane sur la pension d'un retraité, de 27 à 29 % ; le solde
  moyen de la proposition, de −0,9 à −0,8 point de PIB, sa dette en 2070 de
  58 à 56 %, son coefficient de 2070 de 1,00 à 1,01, et la variante
  prospective de −3,1 à −3,0 (`MESURES_BLOCAGES`, que l'accueil cite). La
  grille, qui partait en moyenne 0,02 an plus tôt que l'âge conjoncturel de
  la DREES, part 0,07 an plus tard (`test_age_conjoncturel.py`). Avantages : le
  minimum garanti n'a plus de montant — l'ancien militaire, seul à l'atteindre,
  en portait 0,56 Md€ en 2024 —, et la fiche dit pourquoi ; le modèle en
  chiffre 21, pour 97,9 Md€, et 12,5 Md€ de pensions servies avant l'âge
  légal, contre 11,4. L'écart au COR de la fonction publique d'État s'élargit
  à l'horizon : sa pension relative de +4,2 à +9,3 %, sa dépense de +19,2 à
  +24,8 %, et les deux cliquets remontent (`test_cout.py`) ; partie en 2028,
  quand le traitement indiciaire a déjà décroché de 5 %, la pension militaire
  perd 7 % rapportée au salaire moyen jusqu'aux départs de 2048, quand
  l'ancienne, partie en 2024, perdait 12 % jusqu'à ceux de 2044.
- *La population remesurée* (`grille_large.py --grille population`). La place
  des militaires, en pour cent de leurs retraités de chaque sexe :

  | militaires | q1 | q2 | q3 | q4 | q5 |
  |---|---|---|---|---|---|
  | hommes, EIR | 0,0 | 0,7 | 12,0 | 49,7 | 37,6 |
  | hommes, avant | 2,3 | 11,9 | 60,0 | 14,3 | 11,5 |
  | hommes, après | 0,6 | 7,8 | 40,1 | 25,7 | 25,8 |
  | femmes, EIR | 0,0 | 0,0 | 22,8 | 65,5 | 11,7 |
  | femmes, avant | 3,5 | 27,4 | 52,8 | 11,5 | 4,9 |
  | femmes, après | 0,6 | 27,4 | 34,2 | 22,1 | 15,6 |

  La part des hommes au minimum passe de 16,7 à 14,3 %, pour 9,8 dans l'EIR ;
  au troisième quintile, de 23,2 à 14,9 %, pour 6,2. Le plus grand écart de la
  distribution des pensions des hommes à celle de l'EIR passe de 7,8 à 5,9
  points, à 1 400 €. Les bornes des quintiles bougent à peine : 988, 1 328,
  1 659 et 2 192 €. Les 27,4 % de militaires femmes du deuxième quintile n'ont
  pas bougé : ce sont pour l'essentiel les deux classes du bas, à 0,57 et
  0,69 fois le niveau du cas type — la dispersion des salaires du privé des
  femmes —, que le minimum garanti relève dans les générations d'avant 1960,
  avant comme après. L'EIR n'en compte aucune.
- *Ce qui reste.* À l'action, les groupes suivants, un par session : la
  CNRACL, les exploitants agricoles, les professions libérales, les civils de
  l'État. Hors du cas type, deux choses que cette étape fait voir : la
  dispersion des carrières statutaires dans la population, celle du privé,
  trop large pour une grille indiciaire (une dispersion propre à la fonction
  publique la remplacerait) ; les bénéfices de campagne et la bonification de
  service aérien, que le simulateur ne saisit pas (« suppose le détail des
  services », dit leur fiche). Et l'écart de la fonction publique d'État au
  COR, que la correction a élargi.
