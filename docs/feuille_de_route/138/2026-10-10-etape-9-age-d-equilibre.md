# Étape 9, sixième partie : l'âge d'équilibre, du diviseur et de la part de vie, confronté à l'ETK et au simulateur du COR

**La demande.** Le propriétaire, le 10 octobre 2026 : l'âge d'équilibre,
dernier indicateur de l'étape avant son portage. Au registre (chantier
« 138.9 »), deux points restaient `a_reprendre` : l'âge que l'ETK publie pour
chaque génération, qui compense son coefficient d'espérance de vie
(`elinaikakerroin`), et la part de la vie passée en retraite du simulateur du
COR réécrit, avec l'âge qui la tient constante (`retraites_scherrer`). Pour
chaque génération et chaque cas type, sur les tables du dépôt : l'âge où le
diviseur égale celui de la génération de référence à 65 ans, qui rend, à
cotisations égales, la pension de celle-ci ; l'âge qui tient constante la part
de la vie en retraite. Les confronter à la méthode de l'ETK et aux chiffres du
simulateur, puis repasser les deux points à `repris`.

**Ce que disent les références, lues le jour même.**

- *L'ETK*, son mémo du 26 octobre 2023 sur le coefficient de 2024
  (`eak2024.pdf`). Le coefficient de la génération 1962, 0,94692, est le
  rapport de deux valeurs en capital d'une pension à 62 ans, au taux de 2 % :
  16,778288 en 2009, sur la mortalité de 2003 à 2007, et 17,718722 en 2024,
  sur celle de 2018 à 2022 (p. 2). Son âge cible (« tavoite-eläkeikä », TyEL
  75 c §) est l'âge où la majoration pour report, comptée depuis l'âge minimal
  de la génération, est « au moins aussi grande » que ce que le coefficient
  retire : 65 ans d'âge minimal, quinze mois de report, 66 ans et 3 mois
  (p. 3). La page « Vanhuuseläke » d'etk.fi donne la majoration :
  « Lykkäyskorotus on 0,4 % kuukautta kohti », depuis l'âge minimal.
- *Le simulateur du COR réécrit* par B. Scherrer et M. Baudin
  (`brunoscherrer/retraites`, commit `f3c2d92`, GPL, lu sans être copié) :
  `doc/pilotage-vie-en-retraite.ipynb` et `SimulateurRetraites.py`
  (`_calcule_S_RNV_REV`, `calculeAge`). La part de la vie en retraite d'une
  année est (60 + E − A) / (60 + E), A l'âge effectif moyen de départ que le
  COR de juin 2019 projetait pour l'année, E l'espérance de vie à 60 ans de
  la génération qui part cette année-là à cet âge, `round(année + 0,5 − A)` ;
  l'âge qui tient une part s'en tire par inversion numérique. 29,05 % en 2020
  (62,17 ans, génération 1958), 32,25 % en 2070 (63,91 ans, génération
  2007) ; l'âge qui tiendrait en 2070 la part de 2020 est « proche de 66
  ans », lu sur une figure. Ses espérances de vie (`fileProjection.json`)
  sont celles du COR de juin 2019.
- *Le compte du dépôt*. La conversion des droits acquis prend le diviseur de
  l'âge de référence au 1er janvier de l'année de la bascule
  (`ScenarioNotionnel._droits_acquis`) : 65 ans en 2026, la génération 1961.
  Le taux de préfinancement est nul : le diviseur est l'espérance de vie
  résiduelle, sur la table de génération unisexe de la population où le
  salaire range la carrière.

**Ce qui est fait.**

- *`cycle_de_vie.py`*, une section « l'âge d'équilibre ».
  `reference_du_compte` ; `age_cible`, la règle de l'ETK, le premier mois où
  le coefficient fois la majoration atteint un ; `age_d_equilibre`, qui
  l'applique au compte — le coefficient est le rapport du diviseur de la
  référence à celui de la génération à 65 ans, la majoration ce dont le
  diviseur baisse quand l'âge monte —, au mois, et exact par interpolation
  entre deux mois ; `part_de_vie` et `age_de_part_de_vie_constante`, sous les
  deux conventions de `Indicateurs.part_de_vie`, la référence étant la même
  (sous celle du COR, l'âge vaut 65 ans fois le rapport des deux âges de
  décès, 60 + e60) ; `ages_d_equilibre`, par cas type, sur la mortalité de
  sa population, la même des deux côtés de l'égalité, et, pour la part de
  vie, de son sexe.
- *`python scripts/cycle_de_vie.py --equilibre`* : la table commune,
  génération par génération, et quatre tableaux des treize cas types sur les
  sept générations de la grille.
- *Les tests*. Les définitions, dans `tests/test_cycle_de_vie.py`, dont le
  croisement du balayage de la génération 1970 : la part de vie de
  `part_de_vie` est celle du balayage au millionième, et l'âge où elle
  rejoint celle de la référence, celui où la courbe du balayage la croise, à
  0,002 an près. La confrontation, dans
  `tests/test_cycle_de_vie_references.py` : l'âge cible du mémo de l'ETK, la
  règle sous le compte, les chiffres du simulateur, la figure 3.6 du COR de
  2026.
- *Le registre* : les deux points repris.

**Ce que montrent les mesures.**

- *L'âge d'équilibre du diviseur*, sur la table commune : 63 ans et 7 mois
  pour la génération 1940, 64 ans et 1 mois pour 1950, 65 ans pour 1961,
  65 ans et 2 mois pour 1962, 66 ans et 1 mois pour 1970, 67 ans et 3 mois
  pour 1980, 68 ans et 2 mois pour 1990, 69 ans pour 2000 : de 1961 à 2000,
  un mois et quart par génération. Le coefficient de l'ETK y vaut 1,053 pour
  1940, 0,963 pour 1970, 0,869 pour 2000. À cet âge, chaque génération
  espère la retraite de la référence, 22,7 ans : sans préfinancement, l'âge
  d'équilibre tient constante la DURÉE de la retraite.
- *Par cas type*, il suit le vingtile de la mortalité du diviseur : pour la
  génération 2000, de 68,64 ans (la profession libérale, vingtile 20) à
  69,30 (le SMIC et l'exploitant, vingtile 4). De 1961 à 2000, le diviseur à
  65 ans du vingtile 4 gagne 3,58 ans, contre 3,38 au vingtile 14, et il
  baisse moins vite avec l'âge, de 0,83 an par an, contre 0,88. Deux cas types
  du même vingtile ont les mêmes âges : l'âge d'équilibre dit la longévité,
  non la carrière. Le fonctionnaire actif de la génération 2000 part à
  59 ans, à dix ans du sien ; le cadre à 66, à 2,7 ans.
- *La méthode de l'ETK*. Sa règle, `age_cible`, redonne son âge cible de la
  génération 1962 sur les chiffres de son mémo. Sous le compte, la majoration
  pour report est actuarielle, 0,31 % par mois à 65 ans pour la génération
  1961, 0,30 % pour 2000, quand la Finlande la fixe à 0,4 % : sous la
  sienne, plus généreuse, la génération 2000 partirait à 68 ans et 2 mois, non
  à 69 ans. Le reste diffère aussi : l'ETK lit son coefficient une fois, à
  62 ans, sur la mortalité du moment des cinq dernières années, au taux de
  2 %, et le rapporte à 2009 ; le compte lit des tables de génération, sans
  actualisation, et se rapporte à sa bascule. La génération 1962 y reporte de
  deux mois, non de quinze : sa référence n'a qu'un an d'écart avec elle.
- *L'âge de part de vie constante*, la part de la référence valant 25,1 %
  sous la convention du COR : 64,06 ans pour la génération 1940, 65,74 pour
  1970, 66,50 pour 1980, 67,83 pour 2000 ; sous la survie de génération,
  68,43 ans pour un homme de la génération 2000, 67,25 pour une femme, et,
  par cas type, de 67,19 (la carrière interrompue, une femme) à 68,96 (le
  SMIC). Il monte moins que l'âge d'équilibre du diviseur, 67,8 ans contre 69
  pour la génération 2000 : tenir la part de la retraite dans la vie partage
  les gains d'espérance de vie entre le travail et la retraite, dans le
  rapport des deux ; tenir le diviseur les donne tous au travail.
- *Les chiffres du simulateur*. Sa part de vie est celle du dépôt sous la
  convention du COR, et redonne ses 29,05 % et 32,25 % sur ses espérances de
  vie. Sur celles du dépôt, les mêmes départs passent en retraite 28,09 % et
  29,85 % de leur vie : les siennes, du COR de 2019, passent celles du dépôt
  de 0,4 an pour la génération 1940, 1,2 pour 1958, 1,8 pour 1970, 3,0 pour
  2000 et 3,2 pour 2007. Par sa méthode, l'âge qui tiendrait en 2070 la part
  de 2020 est 66,70 ans sur ses espérances de vie, 65,41 ans sur celles du
  dépôt, qui tiennent sa part de 2020, 28,09 % (64,59 pour tenir 29,05 %) :
  de la génération 1958 à 2004, ses espérances de vie à 60 ans gagnent 6,4
  ans, celles du dépôt 4,5 de 1958 à 2005. Celles du dépôt sont celles du COR
  de 2026 : sa part de vie de chaque génération de 1940 à 2000, figure 3.6, à
  l'âge moyen de départ qu'il projette, se retrouve à 0,04 point près.

**Ce qui reste** de l'étape, dans l'ordre :

1. *Le portage et l'affichage*, avec l'étape 10 : les jumeaux JavaScript de
   `cycle_de_vie.py`, âge d'équilibre compris, de
   `prelevements_historiques.py` et de `contributions_equilibre.py`. L'action
   143, la page qui compare les générations, peut y prendre les deux âges.
2. *La révision de 2026*, au COR, et *la rémunération moyenne par tête du
   COR*, à la session des données : les points 4 et 5 de la cinquième partie,
   inchangés. La génération 1941, leur point 3, est réglée aux données le même
   jour (étape 7, deuxième partie).
3. *Typfallsmodellen*, le dernier point du chantier « 138.9 » encore
   `a_reprendre` au registre : la pension par étage, avant et après impôt, en
   part du dernier salaire, et le revenu autour du départ.
