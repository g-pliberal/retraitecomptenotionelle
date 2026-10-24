# Étape 3, dix-neuvième partie : l'âge de départ de chaque génération, pesé aux poids de la grille, contre celui du COR

**La demande.** Vague du 24 octobre 2026 : le propriétaire lance onze
sessions en parallèle, une par tâche qui se mène sans lui ; celle-ci, le point
1 de « Ce qui reste » de la note « les 65 ans et plus d'après 2030 » (23
octobre) : l'âge moyen de départ de la grille du coût, pesé à ses poids,
génération par génération, contre celui du COR (figure 4.5 du rapport de juin
2026) ; puis, si l'écart tient, ce qui fait partir la France plus tôt que le
taux plein des cas types. Ni l'entrée selon la génération dans la grille,
l'Ircantec et la table des poids, au propriétaire ; ni les naissances de
l'année dans `cout.py`, ni le taux effectif.

**La source.** Le classeur de la partie 4 du rapport (« Données_RA2026_P4_0 »),
que le dépôt ne gardait pas, l'est désormais
(`tests/temoins/cor_age_depart_generations_2026.json`,
`scripts/fetch/cor_age_depart_generations.py`, `cor_age_depart_generations`
dans `data/sources.yaml`, `controle`) : l'âge moyen de départ de chaque
génération de 1906 à 2000, observé jusqu'à celle de 1954 (DREES, EIR et
Ancetre), projeté au-delà des évolutions de TRAJECTOiRE sous la législation de
juin 2026, la suspension comprise, qui touche les générations 1964 à 1968
(figure 4.5) ; la part des résidents de chaque âge retraités au 31 décembre
2024 (figure 4.6) ; la part de chaque génération de 1942 à 1960 déjà partie à
chaque âge d'avant son âge légal (figure 4.7). Le récupérateur contrôle les
repères que le chapitre 2 de la partie 4 imprime : 64,2 ans pour la
génération 1906, 60,9 pour celle de 1932, « autour de 64,6 ans à partir des
générations nées dans les années 1975 » (64,5 au sommaire du classeur ; 64,53
en moyenne de 1975 à 2000) ; 22 % de la génération 1949 partie à 59 ans ; 48,1
% des 62 ans retraités en 2024.

**La mesure** (`ages_moyens_de_depart`, `parts_parties`,
`python scripts/facteurs_depense.py --ages`, deux minutes trois quarts). Chaque
cohorte de la grille, née en janvier, à l'âge du mois où le droit de sa
génération la fait partir (`dates_des_departs`), pesée du poids de son cas type
l'année où sa génération atteint 65 ans : sans l'effectif de la pyramide, qui
ne commence qu'à 50 ans quand le militaire part à 48 ans et demi, comme le COR
compte chaque liquidant. La part partie à chaque âge compte, comme lui, les
natifs de toute l'année au 31 décembre. La grille de `cout.py`, puis les
mesures du départage, cumulées : l'entrée selon la génération, sur le premier
trimestre cotisé, depuis celle de 1960 ; les départs avec décote, à la part
de la génération 1953 ; la décote selon la génération ; l'entrée selon la
durée validée. Sous le droit en vigueur et la référence du COR, sur `main` à
91c5acf avec ce changement.

| Âge moyen de départ, en années ; écart au COR, de chaque groupe de générations | COR | grille de `cout.py` | entrée selon la génération | départs avec décote | décote selon la génération | entrée selon la durée validée |
|---|---|---|---|---|---|---|
| 1950 | 60,48 | 61,02 | 60,89 | 60,64 | 60,64 | 60,43 |
| 1955 | 61,92 | 62,16 | 61,80 | 61,65 | 61,63 | 61,48 |
| 1960 | 62,44 | 62,47 | 62,47 | 62,25 | 62,15 | 62,15 |
| 1965 | 63,48 | 63,15 | 63,62 | 63,33 | 63,21 | 63,31 |
| 1970 | 64,18 | 63,72 | 64,29 | 64,05 | 63,95 | 64,12 |
| 1980 | 64,47 | 63,83 | 64,47 | 64,22 | 64,11 | 64,35 |
| 1990 | 64,58 | 63,81 | 64,54 | 64,28 | 64,17 | 64,37 |
| 2000 | 64,56 | 63,82 | 64,72 | 64,44 | 64,32 | 64,32 |
| 1950-1954 | 61,09 | +0,40 | +0,17 | −0,05 | −0,05 | −0,27 |
| 1955-1964 | 62,50 | +0,05 | +0,00 | −0,21 | −0,28 | −0,35 |
| 1965-1974 | 64,07 | −0,44 | +0,16 | −0,10 | −0,21 | −0,07 |
| 1975-2000 | 64,54 | −0,73 | +0,01 | −0,26 | −0,37 | −0,21 |

| Partis au 31 décembre de l'année du dernier âge d'avant l'âge légal, en % | âge | COR | grille de `cout.py` | entrée selon la génération | entrée selon la durée validée |
|---|---|---|---|---|---|
| 1950 | 59 | 20,6 | 6,5 | 6,5 | 7,1 |
| 1953 | 60 | 29,8 | 20,3 | 26,2 | 26,2 |
| 1955 | 61 | 33,6 | 21,5 | 27,3 | 27,3 |
| 1958 | 61 | 30,7 | 20,3 | 24,9 | 25,3 |
| 1960 | 61 | 26,1 | 17,0 | 17,0 | 17,0 |

| Retraités au 31 décembre 2024, en % des résidents de l'âge | génération | COR | grille de `cout.py` | entrée selon la durée validée |
|---|---|---|---|---|
| 61 ans | 1963 | 19,4 | 16,9 | 15,9 |
| 62 ans | 1962 | 48,1 | 36,0 | 41,7 |
| 63 ans | 1961 | 70,7 | 56,8 | 67,8 |
| 64 ans | 1960 | 78,9 | 77,1 | 82,9 |
| 65 ans | 1959 | 84,8 | 88,0 | 93,3 |
| 66 ans | 1958 | 86,7 | 98,3 | 98,7 |
| 67 ans | 1957 | 94,3 | 99,9 | 99,9 |
| 68 ans | 1956 | 97,0 | 100,0 | 100,0 |

**Ce qu'elle dit.**

- *L'écart ne tient pas : pesée à ses poids, la grille ne part pas plus tard
  que la France.* Telle que `cout.py` la fait partir, chaque génération entrée
  au même âge, elle fait partir celles de 1975 à 2000 à 63,8 ans, sept
  dixièmes d'an avant les 64,5 ans du COR, et chacune avant lui. Entrées dans
  l'emploi selon leur génération, elles partent avec lui, à un centième ;
  selon leur durée validée, une part partie avec une décote, à 64,3 ans. Le
  cadre, l'artisan, le contractuel, le libéral et les deux fonctionnaires
  sédentaires, qui partent alors à 67 ans au taux plein, portent 43 % des
  poids de la génération 1980 ; un cinquième part avant 63 ans quoi qu'il
  arrive — le militaire à 48 ans et demi, l'agent de conduite à 54, le
  super-actif à 57, celui des IEG à 59, les actifs, l'inapte et l'ex-invalide à
  62 —, et le salarié au SMIC, entré à 18 ans, en carrière longue, à 62 ou 63.
- *Les générations 1950 à 1954 partent plus tard dans la grille de `cout.py`*,
  de quatre dixièmes d'an : elles n'y ont pas les carrières longues d'avant 60
  ans, de 2004 à 2008. À 59 ans, 17 à 21 % des générations 1950 à 1952
  étaient parties (figure 4.7), 6,5 % de la grille, ses seuls statutaires.
- *Ce qui fait partir la France plus tôt que le taux plein des cas types : les
  carrières longues, avant l'âge légal.* À 61 ans, les générations 1955 à 1957
  étaient parties à 34 %, celle de 1960 à 26 %, « car ils ont bénéficié de
  l'assouplissement des conditions d'accès au dispositif carrière longue à
  partir de novembre 2012 » (p. 220) ; la grille de 17,0 à 21,5 %, de 25 à 27 %
  entrée selon sa génération jusqu'à celle de 1958 : un seul de ses cas types
  part en carrière longue, le salarié au SMIC, 11 à 12 % de ses poids. Au 31
  décembre 2024, la France compte 48 % de retraités à 62 ans et 71 % à 63, la
  grille 36 et 57 % ; 42 et 68 % entrée selon sa durée validée, une part
  partie avec une décote.
- *Ce qui la fait partir plus tard : les départs après 66 ans.* Au 31 décembre
  2024, 13 % des résidents de 66 ans n'ont liquidé aucun droit, 6 % de ceux de
  67 et 3 % de ceux de 68 (figure 4.6) ; la grille, dont chaque cas type part
  au taux plein, 2 % à 66 ans, presque aucun à 67. Les deux compensent :
  l'âge moyen est le même, la forme non.
- *Le partage qui reste entre les âges* (note du 23 octobre : de 2022 à 2070,
  les 65 ans et plus de la grille reculent de 0,09 point de PIB de plus que
  ceux de l'AWG, ses moins de 65 ans de 0,06 de moins) ne tient donc pas à
  l'âge moyen de départ, que la grille partage avec le COR à deux dixièmes
  près sous chacune des mesures, mais à la forme de ses départs. Le COR ne la
  publie pas pour les générations qu'il projette : entrée selon sa durée
  validée, la grille a fait partir 59 % de la génération 1980 au 31 décembre
  de l'année de ses 65 ans, 73 % telle que `cout.py` la fait partir.

**Ce qui est fait.**

- *`facteurs_depense.py`* : `ages_moyens_de_depart` et `parts_parties`, deux
  fonctions pures des départs, des poids et des décotes (`_cohortes_pesees`) ;
  `grille_ponderee` et `parts_decotees`, tirées de `retraites_par_age`, qui
  les appelle et rend ce qu'il rendait, `parts_decotees` recevant les dates à
  l'âge légal déjà calculées.
- *`scripts/facteurs_depense.py --ages`* : `departs_des_mesures`, les départs
  de la grille sous chaque mesure, et les trois confrontations.
- *Le témoin du COR* et son récupérateur, déclarés dans `data/sources.yaml` :
  ils n'alimentent aucune valeur.
- *Les tests*, `tests/test_facteurs_depense.py` : en suite rapide, le témoin,
  sa source et ce que le rapport imprime ; l'âge moyen d'une génération et la
  part partie à chaque âge, sur des cohortes posées à la main. En contrôle :
  la grille de `cout.py` précède le COR de cinq dixièmes à un an pour les
  générations 1975 à 2000, et chacune ; entrées selon leur génération, à un
  dixième près, selon leur durée validée, à trois ; à 61 ans, elle a fait
  partir moins que la France chacune des générations 1955 à 1960, de plus de
  cinq points ; en 2024, elle a plus de dix points de retraités de moins à 62
  et 63 ans, plus de cinq de plus à 66 et 67.
- *Le registre*, `ageing_report`, la décomposition de la France.

**Ce que ça déplace.** Rien : ni page, ni témoin fabriqué, ni fichier de la
fabrique ; un témoin de source neuf. `retraites_par_age` rend ce qu'il rendait :
ses contrôles des têtes du coût et des départs avec décote passent, en deux
minutes et demie ; les deux contrôles neufs, en deux minutes trois quarts.

**Ce qui reste**, de cette partie ; le point 2 de la note « les 65 ans et plus
d'après 2030 » et le point 1 de la note « l'entrée dans l'emploi », au
propriétaire, et son point 3, les naissances de l'année dans `cout.py`,
demeurent.

1. *La forme des départs des générations projetées.* Le partage qui reste
   entre les âges en tient ; le classeur du COR n'en donne que l'âge moyen. À
   chercher : la part de chaque génération projetée partie à chaque âge, que
   TRAJECTOiRE calcule (la DREES, le COR à l'une de ses séances), pour la
   confronter à `parts_parties`.
2. *Le militaire, que la pyramide ne compte qu'à 50 ans* (`AGE_MINIMAL` de
   `donnees/population.py`, dont le commentaire dit encore que le cas type qui
   part le plus tôt part à 52 ans) : radié à 48 ans et demi depuis l'action
   152, il ne sert ni têtes ni masses ses deux premières années de pension,
   déjà relevé le 16 octobre (note « les tables de l'EACR »), sans suite. Pour
   une session du modèle, le test d'abord.
3. *Au propriétaire*, avec le point 1 de la note « l'entrée dans l'emploi » :
   l'entrée selon la génération dans la grille lui donnerait l'âge moyen de
   départ du COR, quand la grille de `cout.py` le précède de sept dixièmes
   d'an. Et, pour la table des poids : un seul cas type part en carrière
   longue, 11 à 12 % des poids, quand un quart à un tiers des générations 1953
   à 1960 sont parties avant l'âge légal.
