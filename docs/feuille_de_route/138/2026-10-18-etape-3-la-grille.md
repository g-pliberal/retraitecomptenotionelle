# Étape 3, onzième partie : la grille d'une génération sur cinq, qui fait partir trop tôt les cohortes de 1966 et 1967 — 0,18 des 0,29 point des moins de 65 ans

**La demande.** Deuxième vague du 17 octobre 2026 : « action 138, étape 3 :
ces 0,29 point à séparer » — la part de l'écart de couverture de 2022-2030
qui tient aux moins de 65 ans du modèle, qui reculent plus tard que ceux de
l'AWG (point 1 de « Ce qui reste » de la note du 17 octobre, « la part stable
mesurée »). Ni l'Ircantec, qui attend une décision (avec l'action 147), ni la
page Coût, ni la table des poids de `pages.js`, au propriétaire ; rien dans
`cout.py` ni dans les pages.

**Ce que fait la grille.** `cout.py` ne simule qu'une génération sur cinq,
née en janvier, et fait partir les cinq cohortes qu'elle représente à l'âge
de celle-ci, la date décalée d'autant (`cout._masses`). Sous la suspension de
la loi de financement pour 2026 (loi n° 2025-1403, art. 105 ; L. 161-17-3),
la génération de janvier 1965 doit 170 trimestres, celles de 1966 et 1967 en
doivent 172 : entré à 21 ans, le salarié au salaire moyen de 1965 part à 63
ans et demi, en 2028, et la grille fait partir sa cohorte de 1967 en 2030,
quand le droit la fait partir à 64 ans, en 2031. De même le fonctionnaire
sédentaire et l'actif devenu sédentaire de 1966, partis en 2030 au lieu de
2031 ; plus tôt, les cohortes de 1961 et 1962 de six cas types, datées aux
167 trimestres de la génération 1960. En 2030, la grille compte 1,90 million
de retraités de moins de 65 ans, la date de chaque cohorte 1,62 million. Sans
la suspension, la génération 1965 doit 172 trimestres, comme 1966 et 1967, et
l'erreur de 2030 disparaît : 1,62 million des deux façons.

**La mesure.** `departs_par_generation` donne à chaque cohorte l'année de
départ que le droit de sa génération donne au cas type, comme la grille la
donne à celle qu'elle simule (`castypes.carriere_de_la_grille`) ;
`retraites_par_age(..., par_generation=True)` compte avec ces dates, sur la
même population et sous les mêmes poids. Sous la référence du COR, en points
de PIB, au périmètre de l'AWG, la part stable mesurée
(`python scripts/facteurs_depense.py --sans-suspension`) :

| 2022-2030 | Ageing Report 2024 | et 48 % stables, mesurés | et datés à leur génération | sans la suspension, datés |
|---|---|---|---|---|
| 65 ans et plus | −0,22 | −0,07 | −0,07 | −0,14 |
| Moins de 65 ans | −1,16 | −0,87 | −1,05 | −1,04 |
| Couverture | −1,38 | −0,94 | −1,12 | −1,19 |

| 2030-2070 | Ageing Report 2024 | et 48 % stables, mesurés | et datés à leur génération | sans la suspension, datés |
|---|---|---|---|---|
| 65 ans et plus | −0,03 | −0,10 | −0,10 | −0,03 |
| Moins de 65 ans | −0,79 | −1,00 | −0,83 | −0,83 |
| Couverture | −0,83 | −1,11 | −0,93 | −0,86 |

| 2022-2070 | Ageing Report 2024 | et 48 % stables, mesurés | et datés à leur génération | sans la suspension, datés |
|---|---|---|---|---|
| 65 ans et plus | −0,26 | −0,18 | −0,18 | −0,18 |
| Moins de 65 ans | −1,95 | −1,87 | −1,87 | −1,87 |
| Couverture | −2,21 | −2,05 | −2,05 | −2,05 |

L'écart de 2022-2030, colonne après colonne, positif quand le modèle recule
moins :

| L'écart de 2022-2030, départagé | 65 ans et plus | Moins de 65 ans | Couverture |
|---|---|---|---|
| le périmètre | −0,01 | +0,11 | +0,10 |
| la grille | 0,00 | +0,18 | +0,18 |
| la suspension | +0,07 | 0,00 | +0,07 |
| ce qui reste | +0,08 | +0,11 | +0,19 |
| l'écart | +0,14 | +0,40 | +0,54 |

- *La grille fait 0,18 des 0,29 point.* Datés à leur génération, les
  retraités de moins de 65 ans du modèle reculent de 45 % de 2022 à 2030,
  rapportés aux 65 ans et plus, contre 36 % sous la grille et 51 % chez l'AWG
  hors de la part stable ; et ce qu'ils rattrapaient ensuite disparaît :
  −0,83 point de 2030 à 2070, contre −1,00 sous la grille et −0,79 chez
  l'AWG. De 2022 à 2070, rien ne change : la grille date les départs, elle
  n'en ôte aucun.
- *La suspension ne fait rien aux moins de 65 ans.* Datée à sa génération,
  elle ne change l'année de départ d'aucune cohorte qui a moins de 65 ans en
  2025 ou en 2030 : elle retarde d'un an huit cas types de 1965, deux de 1964
  et un de 1968, qui ont 65 ans et plus en 2030 ou partent après. Ses 0,07
  point sont ceux des 65 ans et plus : le cadre de janvier 1965, entré à 23
  ans, part en août 2030 avec 170 trimestres, en février 2031 avec 172.
  L'estimation des notes du 16 et du 17 octobre, 0,09 point, le quart de
  l'effet de la grille, tombait près de cette mesure, mais aux moins de 65
  ans, où la suspension ne fait rien. Elle est faite à l'année, sur des cas
  types nés en janvier.
- *Ce qui reste*, 0,19 point, dont 0,11 aux moins de 65 ans et 0,08 aux 65
  ans et plus, est presque celui de 2022-2070 (0,08 et 0,08) : après 2030,
  le modèle daté suit l'AWG à 0,03 point près. Rien n'y désigne une erreur
  de la mécanique du modèle.

**Ce qui est fait.**

- *`facteurs_depense.py`* : `compter_retraites`, la somme des têtes de
  `cout._masses`, la date de départ en paramètre, par laquelle
  `retraites_par_age` compte désormais — tous âges, elle redonne toujours les
  têtes de `cout.py`, la survie propre des cas types de l'étape 7 comprise
  (`cout._survies_alignees`) ; `depart_de_la_grille`, la date de la grille, et
  `departs_par_generation`, celle de chaque cohorte ; `retraites_par_age`
  reçoit `par_generation`, et garde ces dates comme la grille (`memoire`).
- *`scripts/facteurs_depense.py`* : les colonnes « et datés à leur
  génération » et, avec `--sans-suspension`, « sans la suspension, datés » ;
  le dernier tableau départage l'écart de 2022-2030 (`departage`). Deux
  minutes avec `--sans-suspension`.
- *Les tests*, `tests/test_facteurs_depense.py` : en suite rapide, chaque
  cohorte comptée dès l'année de son départ, sur une grille posée à la main ;
  en contrôle, le départ du salarié au salaire moyen de 1967, tiré de
  L. 161-17-3, et la mesure : la grille fait plus de 0,15 point de l'effet de
  2022-2030, et l'écart à l'AWG tombe sous 0,15. La colonne sans la
  suspension n'a pas de test, comme avant : elle refait le modèle sur une
  copie des données.
- *Le registre*, `ageing_report`, points 1 et 2.

**Ce que ça déplace.** Rien : ni chiffre de page ni témoin du site ;
`retraites_par_age`, sans `par_generation`, rend les mêmes têtes ; le script
gagne deux colonnes et un tableau.

**Ce qui reste**, de cette partie ; les points 2 et 3 de la note du 17
octobre demeurent (les doubles comptes de l'AAH et de l'invalidité ; les 0,18
million de pensionnés de 60 à 64 ans que l'AWG compte de plus que les
sources).

1. *La date de chaque cohorte dans `cout.py`* : ses têtes et ses masses
   portent la même erreur — 0,28 million de retraités de trop en 2030, les
   cohortes de 1961 et 1962 de six cas types parties un an trop tôt. À porter
   dans `cout.py` (action 147), par la date de chaque cohorte ou par une
   grille d'une génération par an autour de 1960-1970 : elle déplacerait la
   page Coût.
2. *Les 0,19 point qui restent* : les naissances de l'année — la grille fait
   naître ses cas types en janvier, et un pas de trois mois de l'âge légal y
   déplace la cohorte entière d'un an ou pas du tout, quand il en déplace le
   quart d'une cohorte née toute l'année ; l'entrée dans l'emploi de Destinie
   (limite n° 2 de `cout.py`), qu'aucune source du dépôt ne donne par
   génération ; les départs hors du taux plein.
