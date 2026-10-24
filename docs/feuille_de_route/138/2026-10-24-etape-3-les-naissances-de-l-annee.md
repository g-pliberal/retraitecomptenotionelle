# Étape 3, vingt-deuxième partie : les naissances de l'année dans `cout.py`, mesurées — l'ancrage de 2024, la dérive comptée de 2025

**La demande.** Sixième vague du 24 octobre 2026, six autres sessions en
parallèle, une tâche chacune : celle-ci, le premier point du bloc de l'étape,
les naissances de l'année dans les têtes et les masses de `cout.py`, avec
l'ancrage de 2024 et la dérive comptée de 2025 (point 3 de « Ce qui reste »
de la note « l'entrée dans l'emploi », point 2 de celle du « coût des
avantages »), mesurées avant d'en décider ; un choix qui revient au
propriétaire se dit dans le bloc, sans se trancher. Ni le taux effectif, ni
la phrase des poids, ni ce qui est déjà au propriétaire.

**Le défaut.** La grille fait naître ses cas types en janvier, et chaque
cohorte compte toute l'année de son départ, dans ses têtes comme dans ses
masses (`cout._masses`, `_masses_regimes`, `_tetes_par_poids`) : partie en
novembre, elle compte au 31 décembre tous ses retraités, et une année entière
de leur pension. Née toute l'année, comme les effectifs de la pyramide qui la
pèsent, sa part née le mois `b` part le mois `m + b − 1`, `m` étant celui de
sa part née en janvier : au 31 décembre, ses nés de janvier et de février,
deux douzièmes ; servis cette année-là, 1/48 d'une année de pension, et 99/144
la suivante. Une cohorte part ainsi en moyenne `m − 1 + 5,5` mois après le
1er janvier de son année de départ, et c'est ce que la grille compte de trop
à chacune : de six mois et demi, partie en février, à un âge rond, à quinze
mois et demi, partie en novembre — à 62 ans et 9 mois, comme la génération
1963.

**La mesure** (`calculer_cout(naissances="toute_l_annee")`,
`python scripts/cout_naissances.py`), sur `main` à 0d99429, sous la
référence : la grille, puis ses cohortes nées toute l'année.

| | 2009 | 2022 | 2024 | 2025 | 2030 | 2040 | 2070 |
|---|---|---|---|---|---|---|---|
| têtes, millions, sous la grille | 13,58 | 16,54 | 16,86 | 16,96 | 17,85 | 19,44 | 22,00 |
| nées toute l'année, écart | −0,06 | −0,39 | −0,36 | −0,28 | −0,27 | −0,07 | −0,08 |
| masse du système actuel, écart | −3,3 % | −5,6 % | −4,9 % | −4,1 % | −3,9 % | −2,7 % | −2,6 % |

| En points de PIB | 2026 | 2027 | 2030 | 2050 | 2070 |
|---|---|---|---|---|---|
| système 6, sous la grille | 8,87 | 8,79 | 8,93 | 9,75 | 8,07 |
| nées toute l'année | 9,10 | 8,99 | 8,89 | 9,78 | 8,10 |
| sa borne haute, sous la grille | | | 9,10 | 10,07 | 8,56 |
| nées toute l'année | | | 9,08 | 10,26 | 8,73 |
| système 2, sous la grille | 3,76 | 3,80 | 3,83 | 4,60 | 4,73 |
| nées toute l'année | 3,75 | 3,79 | 3,82 | 4,60 | 4,74 |

- *L'ancrage de 2024* monte de 5,1 % : la masse de 2024, que la dépense
  observée convertit en euros, perd 4,9 % à compter ses cohortes nées toute
  l'année. Il ne fait pas la page, qui part de la dépense du COR, mais la base
  du modèle, ses masses par régime, et l'engagement acquis, qui le reprend.
- *La dérive comptée de 2025* : 1,077 en 2070 au lieu de 1,060, 1,048 en 2050
  au lieu de 1,033. La masse de 2025 est plus grossie par la grille que celle
  de 2070 — 4,1 % pour 2,6 % — : nées en janvier, les cohortes qui partent de
  2022 à 2030 le font en moyenne entre mai et juillet, au pas d'un trimestre
  de l'âge légal et de la durée requise, celles de 2009 et d'après 2040 en
  février (le mois moyen des départs de l'année, pesés comme la grille : 6,6
  en 2022, 7,1 en 2024, 5,9 en 2025, 5,6 en 2030, 2,1 en 2009, 2040 et 2070,
  mesuré dans un brouillon). L'écart de la masse du modèle à la dépense du
  COR était sous-estimé d'un point et demi, et la borne haute de la fourchette
  avec lui : 0,17 point du système 6 en 2070, 0,19 en 2050.
- *La page* : le système actuel ne bouge pas, le système 2 de moins d'un
  centième et demi. Le système 6 gagne 0,23 point en 2026 et 0,20 en 2027 :
  la proposition reporte à 65 ans les cohortes que le droit en vigueur fait
  partir ces années-là ; comptées toute l'année, elles grossissaient la masse
  du système actuel, que son rapport divise. Il perd 0,04 point en 2030,
  quand partent à 65 ans, comptées toute l'année dans sa propre masse, les
  cohortes qu'il a reportées ; il en gagne 0,04 en 2050 et 0,03 en 2070.
- *Le passé refait* (la base du modèle sur la dépense observée) : −9,6 % en
  2009 au lieu de −11,0, ses têtes à −3,9 % de l'enquête auprès des caisses,
  2024 valant un, au lieu de −5,5 ; −4,3 % en 2004 au lieu de −5,0, ses têtes
  à +2,5 % au lieu de +1,4 ; −1,6 % en 2020 au lieu de −1,1. Mieux chaque
  année jusqu'en 2018, 2012 excepté, un peu moins bien de 2019 à 2022.
- *Le mois du départ et la naissance*, départagés dans un brouillon que le
  code ne garde pas : nées en janvier, la seule année du départ comptée au
  mois fait déjà la dérive de 2070 à 1,075, le système 6 de 2026 à 8,99 ; la
  naissance toute l'année y ajoute deux millièmes et un dixième, et fait toutes
  les têtes.

**Le choix, au propriétaire.** La page garde la grille ; la mesure en fait
un choix de modèle qui lui revient, en deux lectures.

1. *Compter les cohortes nées toute l'année*, comme la pyramide qui les
   pèse : la proposition coûte 0,2 point de PIB de plus à la bascule, la borne
   haute de la fourchette autant à l'horizon, et la dérive de la grille au COR
   est de 1,077 ; le passé se refait mieux jusqu'en 2018, un peu moins bien
   de 2019 à 2022. Il faudrait que suivent, dans la même session :
   l'engagement acquis (`calculer_engagements`), dont l'ancrage monterait de
   5,1 % sans que ses sommes ne comptent de même ; le coût des avantages, dont
   les masses comptent aussi l'année du départ entière (`avantages.masses`) ;
   `facteurs_depense.retraites_par_age`, qui refait les têtes de `cout.py` ;
   les cliquets du coût (la dérive, la reconstitution, les têtes) et la prose
   qui les dit.
2. *Garder la grille*, la convention des cas types nés en janvier, et dire à
   la limite du coût agrégé (§ 2 de `docs/limites/5-bis-cout-agrege.md`), à la
   fin de l'étape, ce qu'elle déplace : ces chiffres.

**Ce qui est fait.**

- *Le compte, en mesure.* `calculer_cout` et `memoire.cout` reçoivent
  `naissances` (`NAISSANCES`, `janvier` par défaut, la grille, et
  `toute_l_annee`), comme `ponderation="egale"` : un second compte qui
  n'existe que pour mesurer le premier, que `Cout.naissances` dit.
  `_nees_toute_l_annee` donne à chaque couple le mois où part la part née en
  janvier de chacune de ses cohortes, celui de la carrière que le droit de sa
  génération lui donne (`_carrieres_voisines`), puis ceux où elle atteint
  l'âge légal de la proposition et 65 ans (`Pensionne.mois`,
  `mois_age_legal`, `mois_65_ans`). `_partie` et `_servie` disent ce qui en est
  parti au 31 décembre et ce qu'elle touche de l'année ; `_masses`,
  `_masses_regimes` et `_tetes_par_poids` les lisent, au droit en vigueur, à
  la proposition (`Pensionne.mois_de_depart_liberal`) et à la garantie
  (`mois_d_ouverture_garantie`). `Avenir.ancrage` garde l'ancrage. Deux
  approximations du second compte, que l'adopter réglerait : la part d'une
  cohorte qui part l'année suivante garde la revalorisation de l'année de la
  cohorte, et la rente du pilier, servie l'année qui suit le départ
  (`_masses_pilier`), n'y est pas comptée au mois.
- *Les tests*, vus rouges pour la raison attendue avant le code, sauf le
  dernier, écrit avec le script : les deux parts posées à la main — partie en
  novembre, deux douzièmes, 1/48 puis 99/144 ; en février, onze douzièmes,
  66/144 puis l'année entière ; perdus, `m − 1 + 5,5` mois pour chaque mois
  de départ —, puis un couple dont les têtes et les masses de chaque système,
  de chaque régime, et les têtes qui divisent sa caisse se comptent ainsi, la
  grille sans mois inchangée (`tests/test_cout.py`) ; les mois du salarié au
  salaire moyen né de 1963 à 1967, août et février, ou juillet et janvier pour
  l'assuré né un 1er (R. 351-37, la présomption du jour de naissance lue au
  vocabulaire) ; un compte que `calculer_cout` ne connaît pas, refusé ; le
  tableau du script, posé à la main ; et, au niveau complet, des têtes et des
  masses moindres chaque année, l'ancrage qui monte de ce que la masse de 2024
  baisse, la dérive de 2070 qui monte, le système actuel inchangé
  (`tests/test_cout_naissances.py`).

**Ce que ça déplace.** Rien : la page reste la grille, au bit près — toutes
ses années, ses six systèmes et sa garantie, confrontés au brouillon mesuré
avant le code —, et le second compte redonne le brouillon, au bit près lui
aussi, deux écritures indépendantes. Ni témoin, ni page, ni fichier de la
fabrique.

**Ce qui reste**, de cette partie ; les points 1 à 5 de la note « le poids du
militaire », 1 de la note « le militaire dès 48 ans », 3 de la note « l'âge de
départ de chaque génération » et 1 de la note « l'entrée dans l'emploi », au
propriétaire, et le taux effectif, demeurent.

1. *Au propriétaire* : compter les cohortes nées toute l'année dans la page,
   ou garder la grille (« Le choix », plus haut).
2. *S'il les fait compter*, une session du modèle : le défaut de
   `calculer_cout` passe à `toute_l_annee`, et suivent l'engagement acquis, le
   coût des avantages, `facteurs_depense.retraites_par_age`, la rente du
   pilier, les cliquets du coût et leur prose, que GitHub ne refait pas.
3. *S'il garde la grille* : la limite, à la fin de l'étape, avec ces chiffres.
