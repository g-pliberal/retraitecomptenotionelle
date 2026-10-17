# Étape 3, dixième partie : la part stable des moins de 65 ans de l'AWG, mesurée — l'invalidité, l'AAH et la réversion seule, qui suivent les 20-64 ans

**La demande.** Vague du 17 octobre 2026, session 9 sur 12 : « action 138,
étape 3 : la part stable des moins de 65 ans de l'AWG, à mesurer » — le point
1 de « Ce qui reste » de la note du 16 octobre (« la couverture de
2022-2030 »), qui la calait à 20,7 %, 1,01 million de pensionnés, pour refaire
l'effet des moins de 65 ans de l'AWG de 2022 à 2070. Ni l'Ircantec, qui attend
une décision (avec l'action 147), ni la table des poids de `pages.js`, au
propriétaire ; rien dans `cout.py` ni dans les pages.

**Les sources** (`scripts/fetch/pensionnes_de_2022.py`, témoin
`tests/temoins/pensionnes_de_2022.json` ; `data/sources.yaml`,
`drees_pensionnes_2022` et `cnaf_aah_age`), au 31 décembre 2022, par tranche
d'âge :

- *l'EACR de la DREES*, version du 26 mai 2026 : les retraités de droit
  direct et de réversion seule, tous régimes, résidents en France ou non
  (tables C et D, tirées d'Ancetre 2022) ; les pensionnés d'invalidité et les
  rentiers d'accident du travail, caisse par caisse (tables I et J). La
  campagne de 2022 ne porte pas l'invalidité de la SNCF ni de la RATP, 13 357
  pensionnés en 2021 ;
- *la CNAF* : les bénéficiaires de l'AAH par âge, dont la somme refait son
  total national de décembre 2022, 1 258 267 ; *la DREES*, minima sociaux,
  tableau 2 : 1 294 700 dans la France entière, MSA comprise ;
- *la fiche France de l'Ageing Report de 2024* : son invalidité comprend l'AAH,
  les rentes d'accident du travail et les pensions d'invalidité (§ 3.1) ; son
  tableau 12 rapporte ses pensionnés de 2022 à la population de leur âge.

**Ce que l'AWG compte**, en millions, ses tranches tirées du tableau 12 et de
la population de l'INSEE au milieu de 2022 (`tests/test_pensionnes_de_l_awg.py`) :

| 2022 | AWG | sources | écart | avec les rentiers AT-MP | écart |
|---|---:|---:|---:|---:|---:|
| moins de 55 ans | 1,404 | 1,403 | −0,1 % | 1,629 | +16,0 % |
| 55-59 ans | 0,776 | 0,761 | −1,8 % | 0,893 | +15,2 % |
| 60-64 ans | 2,688 | 2,507 | −6,8 % | 2,671 | −0,6 % |
| 65 ans et plus | 15,395 | 15,234 | −1,0 % | 15,845 | +2,9 % |
| tous âges | 20,263 | 19,905 | −1,8 % | 21,038 | +3,8 % |

Les retraités de droit direct, les réversions seules, l'invalidité et l'AAH
— avant 62 ans : après, ses bénéficiaires sont aussi retraités — refont les
pensionnés de l'AWG avant 60 ans à 2 % près ; les rentiers d'accident du
travail en plus, ils les dépassent de 15 % : l'AWG met leurs rentes dans sa
dépense, non leurs rentiers parmi ses pensionnés. Il lui reste 0,18 million de
pensionnés de 60 à 64 ans de plus que les sources, ceux que Destinie simule en
2022.

**La part stable, mesurée.** Avant 65 ans, l'invalidité, 0,84 million, l'AAH,
1,17, la réversion seule, 0,32 : 2,33 millions, 47,8 % des 4,87 millions de
l'AWG, plus du double des 1,01 million calés. Les retraités de droit direct en
sont 2,34 millions.

**Sa dynamique.** La note du 16 octobre supposait que la part stable garde son
rapport aux 65 ans et plus : elle n'avait pas d'effet de couverture, et il en
fallait 20,7 %. Mais l'AAH, l'invalidité et la réversion seule d'avant 65 ans
suivent leur classe d'âge : le tableau 12 garde les pensionnés de moins de 55
ans à 3,1 % de la population de leur âge de 2022 à 2070. Gardant sa
prévalence parmi les 20-64 ans de l'AWG (`au_perimetre`, `population_stable`),
la part qui refait l'effet de 2022 à 2070 est de 41,7 %, près de la mesure ;
gardant son rapport aux 65 ans et plus, la part mesurée en laisserait −1,26
point pour −1,95.

**Ce que la mesure change**, sous la référence du COR, en points de PIB
(`python scripts/facteurs_depense.py --sans-suspension`) :

| 2022-2030 | Ageing Report 2024 | modèle | au périmètre de l'AWG | et 48 % stables, mesurés | sans la suspension |
|---|---|---|---|---|---|
| 65 ans et plus | −0,22 | −0,08 | −0,07 | −0,07 | −0,23 |
| Moins de 65 ans | −1,16 | −0,76 | −1,26 | −0,87 | −0,95 |
| Couverture | −1,38 | −0,84 | −1,34 | −0,94 | −1,19 |

| 2022-2070 | Ageing Report 2024 | modèle | au périmètre de l'AWG | et 48 % stables, mesurés | sans la suspension |
|---|---|---|---|---|---|
| 65 ans et plus | −0,26 | −0,19 | −0,18 | −0,18 | −0,18 |
| Moins de 65 ans | −1,95 | −1,50 | −2,50 | −1,87 | −1,48 |
| Couverture | −2,21 | −1,69 | −2,68 | −2,05 | −1,67 |

- *De 2022 à 2070*, la dynamique du modèle, portée au périmètre de l'AWG avec
  la part stable mesurée, refait l'effet de ses moins de 65 ans à 0,08 point
  près.
- *De 2022 à 2030*, l'écart de 0,54 point se départage autrement que le 16
  octobre : le périmètre, 0,10, et non 0,23 ; les 65 ans et plus, 0,15 ; les
  moins de 65 ans à périmètre égal, 0,29, et non 0,16 — la suspension, de
  l'ordre de 0,09 à sa mesure, et 0,20 que rien ne sépare encore. Les
  retraités de moins de 65 ans du modèle reculent plus tard que ceux de l'AWG
  hors de la part stable, de 36 % contre 51 % de 2022 à 2030, rapportés aux
  65 ans et plus, et rattrapent ensuite : −1,00 point contre −0,79 de 2030 à
  2070.
- *Au périmètre de l'AWG*, il ne manque au modèle que la part stable : ses
  2,56 millions de retraités de moins de 65 ans sont les 2,54 millions de
  l'AWG hors d'elle. Rien n'y désigne une erreur de la mécanique du modèle ;
  l'écart tient au moment où ses retraités partent.

**Ce qui est fait.**

- *`facteurs_depense.py`* : `au_perimetre` reçoit `population_stable`, la
  population à laquelle la part stable garde son rapport — les 65 ans et plus
  par défaut, comme avant ; `pensionnes_de_2022` lit le témoin, par catégorie
  et par tranche, l'AAH portée à la France entière et ôtée après 62 ans ;
  `STABLES` et `JEUNES` nomment ce qui ne recule pas et les tranches d'avant
  65 ans.
- *`scripts/facteurs_depense.py`* : la colonne de la part stable est la
  mesure, qui suit les 20-64 ans ; la ligne des pensionnés dit leur
  composition et les deux parts calées.
- *Les tests* : `tests/test_pensionnes_de_l_awg.py`, en suite rapide — le
  témoin et ses totaux publiés, ce que l'AWG compte, la part mesurée, la part
  qui suit sa population ; `tests/test_facteurs_depense.py`, en contrôle, la
  part mesurée contre la dynamique du modèle, et sa docstring redite.
- *Le registre*, `ageing_report`, points 1 et 2, et son manifeste ; les deux
  jeux au manifeste des sources, dont la méthodologie compte les jeux.

**Ce que ça déplace.** Rien : ni chiffre de page ni témoin du site ; la
colonne de la part stable du script.

**Ce qui reste**, de cette partie ; les points 2 et 3 du 16 octobre demeurent.

1. *Les 0,20 point des moins de 65 ans de 2022-2030* : la grille d'une
   génération sur cinq date les départs de 2030 à l'âge des générations
   qu'elle simule, la réforme comme la suspension ; et Destinie fait entrer
   plus tard dans l'emploi les générations qui ont étudié plus longtemps, et
   partir plus tard, ce que le modèle ne fait pas (limite n° 2 de `cout.py`).
2. *Les doubles comptes de l'AAH et de l'invalidité*, que rien ne mesure ici :
   ils diminueraient la part stable.
3. *Les 0,18 million de pensionnés de 60 à 64 ans* que l'AWG compte de plus
   que les sources.
