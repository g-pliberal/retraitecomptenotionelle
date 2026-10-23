# Étape 3, dix-huitième partie : les 65 ans et plus d'après 2030, la décote selon la génération et l'entrée lue sur la durée validée

**La demande.** Vague du 23 octobre 2026 : la session de suivi « Qu'est-ce
qu'il reste à faire ? » lance, sur la demande du propriétaire (« Fait ça »),
douze sessions en parallèle, une étape chacune ; celle-ci, le premier point du
bloc de l'étape 3 : les départs à 65 ans et plus d'après 2030, que la décote
n'explique pas (point 1 de « Ce qui reste » de la note « les départs hors du
taux plein », 19 octobre), et ses deux pistes, à mesurer chacune : la décote
selon la génération ; la durée validée à chaque âge, au lieu du premier
trimestre cotisé (point 4 de la note « l'entrée dans l'emploi »). Ni les
naissances de l'année dans `cout.py`, ni le taux effectif ; ni l'entrée selon
la génération dans la grille, l'Ircantec et la table des poids, au
propriétaire.

**La décote selon la génération.** L'EIR ne suit pas les générations d'après
1953 : 6,8 % des nés en 1950 sont partis avec une décote dès l'âge légal,
9,4 % des nés en 1953 (`macro/departs_generations.csv`). L'EACR compte, année
par année, les liquidants de chaque caisse selon leurs conditions de départ
(table H, `tests/temoins/drees_eacr_tables_2026.json`) : la Cnav a décoté
13,4 % des siens en 2024, 12,8 % en 2020, 13,7 % en 2022 et 2023, tous partis
à l'âge légal ou après lui, ses départs anticipés, carrières longues et
inaptes, se prenant au taux plein (`part_decotee_du_flux`). La part de chaque
génération garde 9,4 % jusqu'à celle de 1953, prend 13,4 % depuis celle de
1960, celle des liquidants de la Cnav de 2024 à l'âge moyen des nouveaux
retraités de l'année, 63,6 ans tous régimes (table C, tirée d'Ancetre), et va
en droite ligne entre les deux
(`part_decotee_de_la_generation`) ; elle se rapporte, comme celle de 1953, aux
cohortes de la grille qui peuvent décoter (`part_avec_decote`) : 25,5 % de
chacune depuis 1960, pour 17,9. La convention prête à une génération entière
la part d'une caisse, dont les liquidants comptent ceux dont elle n'est pas le
régime principal ; l'État civil décote 18,4 % des siens.

**La durée validée.** L'âge médian du premier trimestre cotisé compte un
emploi d'été comme une entrée ; le taux plein regarde la durée validée. Le
fichier de la DREES qui donne le premier trimestre en donne aussi le cumul par
affilié d'avant 23 ans, à la fin de l'année de chaque âge, génération par
génération, de 16 ans à l'âge qu'elle avait en 2017
(`tests/temoins/drees_duree_validee_2017.json`,
`scripts/fetch/drees_duree_validee.py`). Le retard d'une génération sur celle
de 1960 se lit dans l'écart de leurs cumuls au dernier âge où l'EIC voit l'une
et l'autre, en années de quatre trimestres, au trimestre près
(`decalage_par_la_duree`) : nés en 1970, les hommes avaient validé 96,3
trimestres à 47 ans, ceux de 1960 102,9. `--duree` le substitue à celui du
premier trimestre (`decalage_d_entree`), la décote selon la génération
comprise. Chez les hommes, dont sont tous les cas types de la grille qui
peuvent décoter, il monte plus vite, puis plafonne ; les générations d'avant
1960, qui avaient validé plus qu'elle, entrent plus tôt. Chez les femmes, il
recule moins que leur premier trimestre, de trois quarts d'an pour la
génération 1970, pour un an et demi ; la grille n'a qu'une femme, la carrière
interrompue, au taux plein dès l'ouverture.

| Retard d'entrée des hommes sur la génération 1960, en années | 1954 | 1966 | 1970 | 1975 | 1980 | 1990 | 2000 |
|---|---|---|---|---|---|---|---|
| lu sur le premier trimestre cotisé | −0,5 | 1,0 | 1,25 | 2,0 | 1,5 | 1,75 | 2,25 |
| lu sur la durée validée | −1,0 | 1,25 | 1,75 | 2,25 | 2,25 | 2,5 | 2,25 |

Au-delà de 1994, la dernière génération que l'EIC suive, les deux lectures
donnent son retard.

**La mesure**, sur `main` à 8b60629 avec ce changement, `python
scripts/facteurs_depense.py --duree`, sous la réforme de 2023 entière, en
points de PIB, positive quand le modèle recule moins que l'AWG :

| L'écart de 2022-2030, départagé | 65 ans et plus | Moins de 65 ans | Couverture |
|---|---|---|---|
| le périmètre | −0,01 | +0,11 | +0,10 |
| la suspension | +0,06 | +0,00 | +0,06 |
| les naissances de l'année | +0,02 | −0,03 | −0,01 |
| l'entrée dans l'emploi | +0,12 | +0,14 | +0,26 |
| les départs hors du taux plein | −0,05 | −0,00 | −0,06 |
| la décote selon la génération | −0,02 | −0,00 | −0,03 |
| l'entrée selon la durée validée | +0,07 | +0,04 | +0,11 |
| ce qui reste | −0,05 | +0,03 | −0,02 |
| l'écart | +0,14 | +0,28 | +0,42 |

| Effet de la couverture, au périmètre de l'AWG | AWG | départs avec décote | décote selon la génération | et entrée selon la durée validée |
|---|---|---|---|---|
| 2022-2030, 65 ans et plus | −0,22 | −0,23 | −0,21 | −0,27 |
| 2022-2030, moins de 65 ans | −1,16 | −1,09 | −1,09 | −1,13 |
| 2030-2070, 65 ans et plus | −0,03 | −0,13 | −0,12 | −0,07 |
| 2030-2070, moins de 65 ans | −0,79 | −0,78 | −0,78 | −0,76 |
| 2022-2070, 65 ans et plus | −0,26 | −0,36 | −0,33 | −0,35 |
| 2022-2070, moins de 65 ans | −1,95 | −1,87 | −1,87 | −1,89 |
| 2022-2030, couverture | −1,38 | −1,32 | −1,29 | −1,40 |
| 2030-2070, couverture | −0,83 | −0,91 | −0,90 | −0,83 |
| 2022-2070, couverture | −2,21 | −2,23 | −2,19 | −2,23 |

**Ce qu'elle dit.**

- *La décote selon la génération rend un centième.* De 2030 à 2070, les 65
  ans et plus reculent de 0,12 point au lieu de 0,13, pour 0,03 à l'AWG ;
  avant 2030, de 0,21 au lieu de 0,23, pour 0,22. Le compte est linéaire en
  la part : celle de 1953 rendait aux 65 ans et plus d'après 2030 0,030
  point, celle de la Cnav, 1,4 fois plus haute, 0,0126 de plus. Pour rendre
  les 0,09 point qui restaient, il faudrait qu'elle soit quatre fois celle de
  1953 : 40 % de la génération partie avec une décote dès l'âge légal, quand
  la Cnav en décote 13,4 %.
- *La durée validée avance le recul des 65 ans et plus, sans le réduire.* En
  2022, les 65 à 67 ans, nés de 1955 à 1957, entrés plus tôt, sont plus
  nombreux à être partis ; en 2030, ceux nés de 1963 à 1965, entrés plus
  tard, moins nombreux ; en 2070, ceux nés de 2003 à 2005 ont le même retard
  sous les deux lectures, et la grille compte les mêmes retraités. Le recul
  passe d'une période à l'autre : 0,27 point avant 2030, 0,07 après, pour
  0,22 et 0,03 à l'AWG ; 0,35 de 2022 à 2070, pour 0,33 sous le premier
  trimestre et 0,26 à l'AWG.
- *La couverture entière recule comme celle de l'AWG*, à deux centièmes près
  sur chaque période : de 1,40 point de 2022 à 2030, pour 1,38 ; de 0,83 de
  2030 à 2070, autant ; de 2,23 de 2022 à 2070, pour 2,21. Ce qui reste de
  l'écart de 2022-2030 tombe à −0,02 point ; il ne tient plus qu'au partage
  entre les âges : de 2022 à 2070, les 65 ans et plus de la grille reculent
  de 0,09 point de plus que ceux de l'AWG, ses moins de 65 ans de 0,06 de
  moins.
- *Le niveau de 2022.* Entrées sur leur durée validée, les cohortes de la
  grille comptent 2,47 millions de retraités de moins de 65 ans en 2022, 2,41
  sous le premier trimestre et la décote selon la génération, pour 2,34
  millions de droit direct dans Ancetre : les générations d'avant 1960
  partent plus tôt.
- *Sous la suspension*, sur les données du dépôt, la durée validée fait
  reculer les 65 ans et plus de 0,22 point avant 2030 et de 0,13 après, pour
  0,15 et 0,18 sous le premier trimestre.

**Ce qui est fait.**

- *`facteurs_depense.py`* : `part_decotee_du_flux` lit la table H
  (`controle_eacr.conditions_publiees`) ; `part_decotee_de_la_generation`
  (`CAISSE_DU_FLUX`, `ANNEE_DU_FLUX`, `GENERATION_DU_FLUX`) ;
  `retraites_par_age` reçoit `decote_du_flux`. `durees_validees` lit le
  témoin de l'EIC, `decalage_par_la_duree` le retard ; `dates_des_departs`,
  `dates_a_l_age_legal` et `retraites_par_age` reçoivent `durees`.
- *`scripts/facteurs_depense.py`* : `--decote-generation`, qui implique
  `--decote`, et `--duree`, qui l'implique ; leurs colonnes, leurs lignes du
  départage, la part de la Cnav et les retards des hommes de 1966 à 2000 sous
  les deux lectures.
- *Le témoin de l'EIC*, `tests/temoins/drees_duree_validee_2017.json`, et son
  lecteur, `scripts/fetch/drees_duree_validee.py` (`--fichier` lit le fichier
  déjà téléchargé, Python n'ayant pas passé le proxy ce jour-là), déclarés
  dans `data/sources.yaml` (`drees_eic_duree_validee`, `controle`) : ils
  n'alimentent aucune valeur.
- *Les tests*, `tests/test_facteurs_depense.py` : en suite rapide, la part de
  la Cnav, refaite à la main du témoin de l'EACR ; la part de chaque
  génération ; le témoin de l'EIC, sa source et trois cumuls lus ; les
  retards lus sur la durée validée, refaits à la main ; le salarié de 1966,
  entré un an et quart plus tard, parti quinze mois après la date de la
  grille ; les deux étapes du départage. En contrôle, sous la suspension : la
  décote selon la génération rend aux 65 ans et plus d'après 2030 entre 0,005
  et 0,03 point, l'écart à l'AWG restant au-delà de 0,07 ; l'entrée lue sur la
  durée validée, au plus autant de retraités chaque année dès 2030, autant en
  2070, des 65 ans et plus qui reculent de plus de 0,02 point de plus avant
  2030 et de moins après.
- *Le registre*, `ageing_report`, la décomposition de la France.

**Ce que ça déplace.** Rien : ni page, ni témoin fabriqué, ni fichier de la
fabrique ; un témoin de source neuf. `retraites_par_age`, sans ses options
neuves, rend ce qu'il rendait. `--duree` refait les têtes deux fois de plus :
neuf minutes ici pour le script entier, deux pour chacun des contrôles neufs
quand la mémoire tient le coût.

**Ce qui reste**, de cette partie ; le point 1 de la note « l'entrée dans
l'emploi », au propriétaire, et son point 3, les naissances de l'année dans
`cout.py`, demeurent ; son point 4, une mesure plus juste de l'entrée, est
fait ici.

1. *L'âge de départ de chaque génération, contre celui du COR.* Le partage qui
   reste entre les âges tient à l'âge où la grille fait partir ses cohortes.
   Entrée sur sa durée validée, sous la suspension, elle fait partir à 67 ans
   le cadre, le fonctionnaire sédentaire, l'artisan, le contractuel et le
   libéral nés en 1980, à 66 ans et 4 mois le salarié au salaire moyen ;
   TRAJECTOiRE fait partir cette génération à 64,5 ans en moyenne, et celles
   de 1975 à 2000 de même, à un demi-an de l'âge légal (figure 4.5 du rapport
   du COR de juin 2026, « Âge moyen de départ, par génération », classeur
   « Données_RA2026_P4_0 », lue le 23 octobre et que le dépôt ne garde pas).
   À confronter : l'âge moyen de départ de la grille, pesé à ses poids,
   génération par génération ; puis, si l'écart tient, ce qui fait partir la
   France plus tôt que le taux plein des cas types.
2. *Au propriétaire, avec le point 1 de la note « l'entrée dans l'emploi »* :
   si l'entrée selon la génération entre dans la grille, la mesure dit
   qu'elle se lirait mieux sur la durée validée que sur le premier trimestre
   cotisé, la couverture entière reculant alors comme celle de l'AWG.
