# Étape 6, la population : le volume de travail mesuré, la quatrième version

**Le 11 octobre 2026 : chaque année d'activité du salariat privé est payée à la
part de l'année que l'INSEE mesure à son âge. Le minimum contributif de 2019 à
2021 retrouve le niveau de l'EACR, celui des hommes de 2023 passe de 5,7 à
9,4 % pour 12,2, et le minimum moyen monte de 65-76 € à 80-94 €. Mais les
femmes dépassent l'EACR de huit points, par leurs carrières courtes, que la
population fait commencer à 21 ans, là où le volume est le plus bas ; et les
pensions des hommes s'éloignent encore de l'EIR.**

Demande du propriétaire : « vas-y, mets le volume dans la population », sur la
série certifiée le même jour (`volume_travail.csv`).

- *La forme* (`VOLUME_DE_TRAVAIL`, `scripts/grille_large.py`). La part de
  l'année d'une tranche d'âge est son volume, rapporté à celui de l'ensemble
  des salariés (0,77), fois celui d'un temps complet (0,85) : 0,53 avant 25
  ans, 0,87 de 25 à 39, 0,93 de 40 à 49, 0,95 de 50 à 54, 0,85 ensuite
  (`volumes_de_travail`). Le sexe n'y entre pas : le volume de chacun, divisé
  par ce que lui retire son temps partiel, laisse la même part de l'année,
  0,825 pour les femmes et 0,821 pour les hommes en 2023 ; le temps partiel
  de la population s'y ajoute. Elle passe par le canal du temps partiel : le
  revenu de l'année en est réduit, et les trimestres se déduisent du revenu.
  Seul le salariat privé la reçoit ; une carrière complète à temps complet,
  de 21 à 61 ans, travaille désormais 0,86 de ses années.
- *Une variante selon le rang* (`VOLUME_SELON_LE_RANG`, débrayée). Chaque
  classe de centiles prend en outre le volume de la catégorie qu'elle
  représente, rapporté à l'ensemble — employés au dixième centile (0,88),
  ouvriers au vingt-cinquième (0,95), professions intermédiaires au
  soixante-quinzième (1,08), cadres au-delà (1,13) —, sans dépasser l'année
  entière. Une convention : l'INSEE ne croise pas le rang du salaire et le
  volume, et celui des employés compte aussi leur temps partiel.
- *Le minimum contributif* (`part_minimum_contributif.py`, en pour cent des
  liquidants, en euros de 2023 par mois) :

  | | 2019 | 2020 | 2021 | 2022 | 2023 | femmes 2023 | hommes 2023 | 2024 | hommes 2024 | minimum moyen, 2019-2023 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | troisième version | 13,5 | 12,5 | 12,3 | 13,9 | 13,8 | 20,0 | 5,7 | 17,3 | 6,4 | 65 à 76 € |
  | quatrième version | 20,0 | 19,0 | 18,8 | 21,4 | 22,8 | 33,1 | 9,4 | 25,7 | 9,6 | 80 à 94 € |
  | selon le rang | 21,5 | 20,6 | 20,7 | 23,1 | 24,6 | 34,4 | 11,8 | 28,9 | 11,8 | 93 à 110 € |
  | EACR, alignés | 20,4 | 18,4 | 17,9 | 18,9 | 18,8 | 25,2 | 12,2 | 18,6 (estimée) | 12,7 | 134 à 139 € |

- *D'où vient le saut*, chez les liquidants de 2023 : des carrières courtes
  du salariat privé. Chez les femmes, moins de dix années validées passent de
  43,9 à 97,0 % au minimum, de dix à vingt de 43,9 à 71,3 %, de vingt à trente
  de 28,9 à 51,5 %, de trente à quarante de 15,0 à 28,9 % ; chez les hommes,
  moins de dix de 35,9 à 91,7 %, de dix à vingt de 19,1 à 39,5 %. La
  population fait commencer ces carrières à 21 ans et les arrête quand leur
  durée est validée : leurs années sont celles de la jeunesse, où l'INSEE
  mesure le volume le plus bas, si bien qu'une carrière de cinq ans n'en
  travaille plus qu'à peine trois. La carrière persistante au Smic, complète,
  touche aussi le minimum dès 2023 : son revenu passe sous le seuil.
- *Les pensions de 2020 contre l'EIR*, en euros par mois :

  | | moyenne | médiane | femmes, moyenne | femmes, médiane | hommes, moyenne | hommes, médiane | Kolmogorov, hommes |
  |---|---|---|---|---|---|---|---|
  | EIR | 1 536 | 1 382 | 1 177 | 1 013 | 1 957 | 1 745 | |
  | troisième version | 1 488 | 1 327 | 1 229 | 1 158 | 1 742 | 1 547 | +8,4 pt à 1 600 |
  | quatrième version | 1 454 | 1 302 | 1 200 | 1 087 | 1 692 | 1 479 | +12,3 pt à 1 700 |
  | selon le rang | 1 447 | 1 270 | 1 198 | 1 103 | 1 685 | 1 473 | +13,3 pt à 1 400 |

  La moyenne ne perd que 2 % : seul le salariat privé reçoit le volume, et
  son salaire annuel moyen ne retient que ses vingt-cinq meilleures années,
  celles des âges où le volume est le plus haut. Les femmes se
  rapprochent de l'EIR (écart de Kolmogorov de −12,3 à −11,9 points) ; les
  hommes, déjà trop bas, s'en éloignent.
- *Sur la page*, contre celle du jour, les trois sur les mêmes données :
  l'écart des années observées passe de −1,43 et −3,01 points à −1,02 et
  −2,87 ; la part du PIB en 2070, au scénario 3, de +0,66 à +0,44 point, à la
  proposition de −0,02 à −0,18 ; son solde moyen de 2026 à 2070, de +0,10 à
  +0,22 ; la garantie, de +0,089 à +0,098 point ; le passé refait, au pire
  depuis 2000, de 12,5 à 11,9 %.
- *Ce que la mesure accuse.* Le volume est bien la pièce qui manquait au
  minimum : son niveau de 2019 à 2021, la moitié de l'écart des hommes (les
  neuf dixièmes selon le rang), un quart à un tiers de celui du montant. Il
  en ajoute trop aux femmes, mais par une convention de la population plus
  que par lui : les années d'une carrière courte, que l'EIR ne date pas,
  tombent dans la jeunesse. Et la pension des hommes, déjà sous l'EIR avant lui (une
  médiane à 1 547 € pour 1 745), descend encore : ce manque-là, du premier
  au neuvième décile, n'est pas propre au bas de l'échelle.

**Ce qui reste** de l'étape, dans l'ordre : dater autrement les années des
carrières courtes ; chercher pourquoi la pension des hommes reste sous
l'EIR ; un bas d'échelle plus fin ; enfin, au propriétaire, la bascule de la
page. Le volume reste en place, débrayable par sa constante ; la variante
selon le rang reste débrayée.
