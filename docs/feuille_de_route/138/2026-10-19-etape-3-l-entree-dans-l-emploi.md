# Étape 3, seizième partie : les 0,19 point de la couverture de 2022-2030, l'entrée dans l'emploi selon la génération

**La demande.** Vague B du 19 octobre 2026, session 11 de la deuxième salve :
« les 0,19 point qui séparent encore le coût du dépôt de celui de l'AWG », le
premier des restes « une session par point » du bloc de l'étape (point 2 de
« Ce qui reste » de la note « la grille », point 1 de celle de « la date de
chaque cohorte », 18 octobre) : les mesurer depuis les corrections du jour,
puis les expliquer ou les corriger. Ni l'Ircantec, ni le taux effectif, ni la
prémisse du déficit. Les trois causes que la note « la grille » proposait : les
naissances de l'année, l'entrée dans l'emploi de Destinie, les départs hors du
taux plein.

**Ce qu'il en reste.** La ligne « ce qui reste » du départage de 2022-2030
(`python scripts/facteurs_depense.py --sans-suspension`), en points de PIB,
positive quand le modèle recule moins que l'AWG :

| Sur `main` | 65 ans et plus | Moins de 65 ans | Couverture |
|---|---|---|---|
| avant l'inapte de la Cnav (168a0e5), comme au 18 octobre | +0,08 | +0,11 | +0,19 |
| avec l'inapte (282bf47), et jusqu'à 36e04d7 | +0,08 | +0,14 | +0,22 |
| avec l'ex-invalide (b4fa4e6), à ba42715 | +0,08 | +0,17 | +0,25 |

L'inapte et l'ex-invalide partent à 62 ans quelle que soit leur durée, que la
réforme de 2023 leur garde : leurs moins de 65 ans ne reculent pas, et la
grille recule moins. L'AWG les a aussi : ils ne sont pas une erreur, mais ils
creusent l'écart. Les corrections du jour dans `avantages.py` et
`mortalite_population.py` ne touchent pas ces têtes.

**Les naissances de l'année** (`--naissances`). La grille fait naître ses cas
types en janvier : partie à 62 ans et 9 mois, en novembre, une cohorte se
compte toute au 31 décembre, quand, née toute l'année, elle n'en a que le
sixième de partis (`compter_retraites`, `mois`). Au même âge, nées toute
l'année, les cohortes de la grille ne changent presque rien à ce qui reste,
un centième : leurs moins de 65 ans reculent de trois centièmes de moins, leurs
65 ans et plus de deux de plus. Elles changent les niveaux : sous la réforme
entière, 2,19 millions de retraités de moins de 65 ans en 2022 au lieu de
2,51, plus près des 2,34 millions de droit direct d'Ancetre, 1,90 au lieu de
2,07 en 2025, 1,51 au lieu de 1,68 en 2030. Tous âges, avec la suspension,
les têtes de `cout.py` comptent ainsi 0,39 million de retraités de trop en
2022, 0,27 en 2025 et en 2030, quand l'âge légal avance d'un trimestre par
génération, 0,07 en 2035 et en 2040, aux âges ronds (mesuré sur 36e04d7) : la
masse de 2024, sur laquelle le modèle s'ancre, et celle de 2025, d'où la
dérive se compte, en sont grossies (« Ce qui reste », point 3).

**L'entrée dans l'emploi** (`--entree`). La grille fait entrer ses cas types
au même âge à chaque génération (limite n° 2 de `cout.py`) ; l'échantillon
interrégimes de cotisants de 2017 les voit entrer plus tard
(`macro/premier_trimestre.csv`, certifié, parmi les affiliés d'avant 23 ans).
L'âge où la moitié d'une génération a cotisé un trimestre
(`ages_medians_du_premier_trimestre`), chez les hommes : 17,6 ans nés en 1958,
17,8 en 1960, 18,1 en 1962, 18,2 en 1964, 18,8 en 1966, 19,2 en 1968, 19,1 en
1970 ; chez les femmes, de 18,1 à 19,8 ans. Les générations de 1966 à 1970,
celles des moins de 65 ans de 2030, entrent un an à un an et demi après celles
de 1958 à 1962, celles de 2022. Destinie, le modèle de l'AWG pour la France,
fait partir plus tard ceux qui ont fini leurs études plus tard (fiche France,
§ 3.3, note du 16 octobre). `--entree` fait entrer chaque génération d'un cas
type qui part au taux plein plus tard que la génération 1960, celle du milieu
des moins de 65 ans de 2022, d'autant que l'âge médian de son sexe recule, au
trimestre près (`decalage_d_entree`) ; le militaire, après ses services, et
les agents de la SNCF et des IEG, à leur âge, gardent leur date ; la pension
reste celle de la grille. Entré à 22 ans au lieu de 21, le salarié au salaire
moyen né en 1966 part à 65 ans, en février 2031, et non à 64, en février 2030
(`dates_des_departs`).

Sur `main` à ba42715, `python scripts/facteurs_depense.py --entree` :

| L'écart de 2022-2030, départagé | 65 ans et plus | Moins de 65 ans | Couverture |
|---|---|---|---|
| le périmètre | −0,01 | +0,11 | +0,11 |
| la suspension | +0,06 | +0,00 | +0,06 |
| les naissances de l'année | +0,02 | −0,03 | −0,01 |
| l'entrée dans l'emploi | +0,12 | +0,14 | +0,26 |
| ce qui reste | −0,06 | +0,06 | +0,00 |
| l'écart | +0,14 | +0,28 | +0,42 |

| Effet de la couverture, au périmètre de l'AWG | AWG | réforme entière, nés toute l'année | et l'entrée selon la génération |
|---|---|---|---|
| 2022-2030, 65 ans et plus | −0,22 | −0,16 | −0,28 |
| 2022-2030, moins de 65 ans | −1,16 | −0,96 | −1,10 |
| 2030-2070, 65 ans et plus | −0,03 | +0,02 | −0,16 |
| 2030-2070, moins de 65 ans | −0,79 | −0,76 | −0,78 |
| 2022-2070, 65 ans et plus | −0,26 | −0,14 | −0,44 |
| 2022-2070, moins de 65 ans | −1,95 | −1,71 | −1,88 |

Entrées selon leur génération, les cohortes de la grille font tout ce qui
restait de 2022 à 2030 : il reste −0,00 point, −0,06 aux 65 ans et plus et
+0,06 aux moins de 65 ans. Leurs moins de 65 ans reculent alors comme ceux de
l'AWG sur chaque période, à sept centièmes près, et sont 1,32 million en 2030
au lieu de 1,51 ; leurs 65 ans et plus reculent plus que les siens, de 0,13
point de 2030 à 2070 : le recul de l'entrée porte au-delà de 65 ans le taux
plein des générations d'après 1966. La mesure garde sa forme sous une autre
génération de référence : celle de 1962 gardant l'entrée de la grille,
l'entrée fait 0,26 point et il reste −0,00 ; celle de 1966, dont les cohortes
de 2022 entrent un an plus tôt que dans la grille, 0,16, et il reste 0,11
(`--entree 1962`, `--entree 1966`). Elle se lit nées toute l'année : nées en
janvier, une cohorte saute d'une année de départ pour un trimestre d'entrée,
et ce qui reste allait de −0,01 à +0,14 point selon la génération de référence
(mesuré sur 36e04d7).

**Les départs hors du taux plein.** Ils ne sont pas mesurés : la grille fait
partir chacun au taux plein. L'entrée selon la génération en montre la place :
aux 65 ans et plus, où le recul de l'entrée porte le taux plein du salarié au
salaire moyen, du fonctionnaire sédentaire et du cadre au-delà de 65 ans,
quand Destinie laisse la couverture des 65 ans et plus presque stable après
2030 (−0,03 point de 2030 à 2070). Un départ à l'âge légal avec une décote,
celui de 13,4 % des liquidants de la Cnav en 2024 (note du 16 octobre, « les
tables de l'EACR »), l'y retiendrait.

**Ce qui est fait.**

- *`facteurs_depense.py`* : `compter_retraites` reçoit `mois`, et compte
  l'année du départ d'une cohorte née toute l'année à ses seuls partis ;
  `ages_medians_du_premier_trimestre` et `decalage_d_entree` lisent l'EIC ;
  `dates_des_departs` refait la date du départ de chaque cohorte, née en
  janvier, et, avec `entree_depuis`, entrée selon sa génération ;
  `retraites_par_age` reçoit `nes_toute_l_annee` et `entree_depuis`, et
  redonne sans eux les têtes de `cout.py`.
- *`scripts/facteurs_depense.py`* : `--naissances`, la colonne « nés toute
  l'année » de la réforme entière, et `--entree [GÉNÉRATION]`, qui l'implique,
  la colonne de l'entrée selon la génération ; le départage y ajoute « les
  naissances de l'année » et « l'entrée dans l'emploi » ; une ligne dit les
  moins de 65 ans de 2022, 2025 et 2030 sous chaque compte.
- *Les tests*, `tests/test_facteurs_depense.py` : en suite rapide, le compte
  d'une cohorte née toute l'année, sur une grille posée à la main ; l'âge
  médian du premier trimestre et le recul d'un an de 1960 à 1966, refaits à la
  main des parts de l'EIC ; le salarié de 1966 entré un an plus tard, parti à
  65 ans (L. 161-17-3), le militaire à son heure ; les deux étapes du
  départage. En contrôle, la mesure : l'entrée selon la génération ôte plus de
  0,15 point à l'écart de 2022-2030, les moins de 65 ans reculent comme ceux de
  l'AWG à 0,1 point près de 2022 à 2030 comme de 2030 à 2070, les 65 ans et
  plus, de 2030 à 2070, de plus de 0,1 point de plus.
- *Le registre*, `ageing_report`, la décomposition de la France.

**Ce que ça déplace.** Rien : ni page, ni témoin, ni fichier fabriqué ;
`retraites_par_age`, sans ses deux options, rend les têtes de `cout.py`. Le
script gagne deux options ; `--entree` refait le coût de la réforme entière,
puis deux fois ses têtes, une dizaine de minutes. Le contrôle neuf prend une
demi-minute quand la mémoire tient le coût.

**Ce qui reste**, de cette partie ; les points 2 et 3 de la note du 17
octobre et le point 3 de celle de « la date de chaque cohorte » demeurent.

1. *Au propriétaire : l'entrée selon la génération dans la grille du coût.*
   La page Coût suit les conventions du COR, dont les cas types du privé
   entrent au même âge à chaque génération ; seule l'entrée des
   fonctionnaires y recule (`delai_entree`). Porter l'entrée de l'EIC dans
   `castypes.py` et `cout.py`, sous `conventions_cor`, ferait partir plus tard
   les générations nées après 1960, plus tôt celles d'avant, et déplacerait la
   page : à mesurer d'abord, avec ce que la pension en devient.
2. *Les départs hors du taux plein*, aux 65 ans et plus, que l'entrée selon la
   génération pousse au-delà de 65 ans : la décote à l'âge légal, que la
   population de l'étape 14 sait servir, mesurée dans le départage.
3. *Les naissances de l'année dans les têtes et les masses de `cout.py`*,
   avec le point 2 de la note « le coût des avantages » : l'ancrage de 2024 et
   la dérive comptée de 2025, à mesurer avant d'en décider.
4. *Une mesure plus juste de l'entrée* : le premier trimestre cotisé compte un
   emploi d'été comme une entrée ; le cumul des trimestres validés à chaque
   âge, génération par génération, que le même jeu de la DREES diffuse
   (`drees_eic_droits_valides`, dont `scripts/fetch/drees_premier_trimestre.py`
   ne garde que la part des affiliés), dirait la durée que le taux plein
   regarde, surtout après la génération 1970.
