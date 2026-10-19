# Étape 3, dix-septième partie : les départs hors du taux plein, à l'âge légal avec une décote, mesurés dans le départage

**La demande.** Vague B du 19 octobre 2026, session 19 de la quatrième salve :
« les départs hors du taux plein, aux 65 ans et plus », le premier des restes
« une session par point » du bloc de l'étape (point 2 de « Ce qui reste » de
la note « l'entrée dans l'emploi », du même jour) : la décote à l'âge légal,
que la population de l'étape 14 sait servir, mesurée dans le départage. Ni
les naissances de l'année dans `cout.py`, ni le taux effectif, ni l'entrée
selon la génération dans la grille, qui attend le propriétaire.

**La part.** La grille fait partir chacun au taux plein. L'EIR de 2020 range
les retraités nés en 1953 par la place de leur départ, dans leur régime
principal (`macro/departs_generations.csv`, certifié) : 31,2 % à l'âge légal,
dont 13,8 % avec une décote ; 26,6 % entre lui et l'âge d'annulation, dont
19,0 % ; 8,3 % à cet âge et 3,1 % après, presque aucun décoté. La génération
est partie avec une décote dès l'âge légal à 9,4 %, sur ses 10,6 % de départs
décotés (`part_decotee_des_l_age_legal`) ; le reste, 3,9 % des 30,9 % partis
avant l'âge légal, tient aux régimes qui ouvrent plus tôt. Dans la grille,
peuvent décoter les cohortes d'un cas type qui part au taux plein, dont le
droit s'ouvre à l'âge légal de leur génération et le taux plein vient après
(`dates_a_l_age_legal`) : le salarié au salaire moyen, le cadre, le
fonctionnaire sédentaire de l'État et celui de la CNRACL, l'artisan, le
libéral, le contractuel. Non le salarié au SMIC, en carrière longue, ni la
carrière interrompue ou l'exploitant, qui ont le taux plein dès l'ouverture,
ni l'inapte et l'ex-invalide, ni les actifs, que leur classement ouvre plus
tôt, ni le militaire et les agents de la SNCF et des IEG. Elles pèsent 52,4 %
de la génération 1953 aux poids de 2020 : 17,9 % de chacune part à l'âge
légal (`part_avec_decote`), comme la population de l'étape 14 rapporte la
part de l'EIR à ses carrières incomplètes.

**Trois conventions.** La décote se prend à l'âge légal, quand l'EIR en place
plus de la moitié, 5,1 points sur 9,4, entre lui et l'âge d'annulation : la
mesure avance ces départs plus que la France ne le fait. La part ne dépend ni
de ce qui manque au taux plein ni du cas type, et reste celle de 1953 à
chaque génération. La pension reste celle de la grille : la couverture ne
compte que des têtes.

**La mesure**, sur `main` à 798d0f0 avec ce changement, `python
scripts/facteurs_depense.py --decote`, sous la réforme de 2023 entière, en
points de PIB, positive quand le modèle recule moins que l'AWG :

| L'écart de 2022-2030, départagé | 65 ans et plus | Moins de 65 ans | Couverture |
|---|---|---|---|
| le périmètre | −0,01 | +0,11 | +0,11 |
| la suspension | +0,06 | +0,00 | +0,06 |
| les naissances de l'année | +0,02 | −0,03 | −0,01 |
| l'entrée dans l'emploi | +0,12 | +0,14 | +0,26 |
| les départs hors du taux plein | −0,05 | −0,00 | −0,06 |
| ce qui reste | −0,01 | +0,07 | +0,06 |
| l'écart | +0,14 | +0,28 | +0,42 |

| Effet de la couverture, au périmètre de l'AWG | AWG | entrée selon la génération | et départs avec décote |
|---|---|---|---|
| 2022-2030, 65 ans et plus | −0,22 | −0,28 | −0,23 |
| 2022-2030, moins de 65 ans | −1,16 | −1,10 | −1,09 |
| 2030-2070, 65 ans et plus | −0,03 | −0,16 | −0,13 |
| 2030-2070, moins de 65 ans | −0,79 | −0,78 | −0,78 |
| 2022-2070, 65 ans et plus | −0,26 | −0,44 | −0,36 |
| 2022-2070, moins de 65 ans | −1,95 | −1,88 | −1,87 |

**Ce qu'elle dit.**

- *Avant 2030, les 65 ans et plus reculent comme ceux de l'AWG*, à un
  centième près, au lieu de six. Entrés selon leur génération, l'artisan, le
  contractuel et le libéral n'ont le taux plein qu'après 65 ans à toutes les
  générations de la période, le cadre à partir de celle de 1961, le
  fonctionnaire sédentaire de celle de 1965 (`dates_des_departs`) : de 2022 à
  2030, de plus en plus de 65 ans et plus attendent leur taux plein, dont la
  part décotée part dès l'âge légal. Ce qui reste de 2022-2030 est désormais
  aux moins de 65 ans, +0,07 point, que la décote ne déplace pas : partis plus
  tôt, ils sont plus nombreux en 2022 comme en 2030, 2,35 millions au lieu de
  2,19, puis 1,42 au lieu de 1,32, dans la même proportion.
- *Après 2030, la décote n'explique pas les 65 ans et plus.* Elle n'en
  reprend que 0,03 point : de 2030 à 2070, ils reculent encore de 0,13, quand
  Destinie garde leur couverture presque stable, −0,03. L'entrée selon la
  génération leur ôtait 0,18 point (de +0,02 à −0,16) ; à la part de 1953,
  les départs hors du taux plein n'en rendent qu'un sixième, en les avançant
  pourtant à l'âge légal.
- *Le niveau de 2022.* Nées toute l'année, entrées selon leur génération,
  partie pour une part décotées, les cohortes de la grille comptent 2,35
  millions de retraités de moins de 65 ans en 2022 ; Ancetre, 2,34 millions de
  droit direct, résidents ou non (note « l'entrée dans l'emploi ») : un
  rapprochement, non un calage, la grille comptant des résidents.
- *Sous la suspension*, sur les données du dépôt, la même part rend aux 65 ans
  et plus 0,04 point de 2022 à 2030 comme de 2030 à 2070 ; ses moins de 65 ans
  bougent de deux centièmes au plus.

**Ce qui est fait.**

- *`facteurs_depense.py`* : `compter_retraites` reçoit `decotes`, la part de
  chaque cohorte qui part avant son taux plein et la date de ce départ ;
  `part_decotee_des_l_age_legal` lit l'EIR ; `part_avec_decote` la rapporte
  aux cohortes qui peuvent décoter ; `dates_des_departs` reçoit
  `a_l_ouverture` ; `dates_a_l_age_legal` garde celles dont le droit s'ouvre
  à l'âge légal (L. 161-17-2) et le taux plein vient après ;
  `retraites_par_age` reçoit `avec_decote`, la part calée sur la génération
  1953 aux poids et aux survies de 2020.
- *`scripts/facteurs_depense.py`* : `--decote`, qui implique `--entree`, la
  colonne « et les départs avec décote », la ligne « les départs hors du taux
  plein » du départage, la part de l'EIR et les moins de 65 ans de 2022, 2025
  et 2030 sous ce compte.
- *Les tests*, `tests/test_facteurs_depense.py` : en suite rapide, le compte
  d'une cohorte dont une part part plus tôt, sur une grille posée à la main ;
  les 9,4 % de 1953, refaits à la main de l'EIR ; leur rapport aux cohortes
  qui peuvent décoter ; le salarié né en 1966, entré à 22 ans, qui peut
  partir à l'âge légal en 2029 (L. 161-17-2), quand l'actif, le salarié au
  SMIC et le militaire gardent leur départ ; le départage. En contrôle, la
  mesure sous la suspension : chaque année au moins autant de retraités ; les
  65 ans et plus qui reculent de 0,02 point de moins au moins de 2022 à 2030
  comme de 2030 à 2070, mais encore de 0,1 point de plus que ceux de l'AWG
  après 2030 ; les moins de 65 ans à 0,03 point près.
- *Le registre*, `ageing_report`, la décomposition de la France.

**Ce que ça déplace.** Rien : ni page, ni témoin, ni fichier fabriqué ;
`retraites_par_age`, sans `avec_decote`, rend ce qu'il rendait. `--decote`
refait les têtes une fois de plus, et les dates de chaque cohorte deux fois,
au taux plein et à l'ouverture : six minutes ici pour le script entier, une
minute et quart pour le contrôle neuf quand la mémoire tient le coût.

**Ce qui reste**, de cette partie ; les points 1, 3 et 4 de la note
« l'entrée dans l'emploi » demeurent : l'entrée selon la génération dans la
grille, au propriétaire, les naissances de l'année dans `cout.py`, une mesure
plus juste de l'entrée.

1. *Les 65 ans et plus d'après 2030*, que la décote de 1953 n'explique pas.
   Deux pistes, à mesurer chacune : la décote selon la génération — 6,8 % des
   nés en 1950, 10,6 % des nés en 1953, 13,4 % des liquidants de la Cnav en
   2024 (EACR, note du 16 octobre) —, que l'EIR ne suit pas au-delà de 1953 ;
   et la durée validée à chaque âge, que le point 4 de la note « l'entrée dans
   l'emploi » propose de lire au lieu du premier trimestre cotisé, et qui dit
   quand le taux plein vient vraiment.
2. *Les moins de 65 ans de 2022-2030*, +0,07 point, qui reculent moins que
   ceux de l'AWG : ce qui reste du départage, désormais.
