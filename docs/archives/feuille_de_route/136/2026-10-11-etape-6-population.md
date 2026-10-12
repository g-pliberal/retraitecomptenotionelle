# Étape 6, la population : une première version, construite à côté de la page et mesurée

**Le 11 octobre 2026 : la population entre dans `scripts/grille_large.py`,
comme une grille de plus que les deux mesures savent lire
(`--grille population`). Elle rapproche de l'EACR la part au minimum
contributif, sexe par sexe, et de l'EIR les pensions de 2020 ; le montant du
minimum et l'écart des pensions entre les sexes restent loin. La page Coût
n'en bouge pas.**

Demande du propriétaire : « vas-y, construis la population », la forme B des
trois proposées le même jour, construite à côté de la page.

- *Ce qu'elle est.* La grille « ensemble » — ses personnes, ses carrières
  mêlées, ses femmes, ses carrières courtes —, dont les quatre cas types de la
  Cnav (le Smic, le salaire moyen, le cadre, la carrière interrompue) cèdent
  leur part à un seul gabarit, le salarié du privé, décliné aux sept centiles
  du salaire de SON sexe : la forme de la distribution du sexe, rapportée à sa
  moyenne, au niveau de cette moyenne l'année où la génération a 45 ans, si
  bien que chaque génération a l'écart des sexes de son temps. Les trois
  centiles du haut sont cadres, 17,5 % du salariat privé : une convention.
  Pour la part de ses carrières que donne la moyenne, de 1975 à 2025, du temps
  partiel des 25-49 ans — 25,4 % des femmes, 3,6 % des hommes —, le salarié
  travaille à temps partiel de 25 à 49 ans, à la quotité de sa génération à
  40 ans. Les autres groupes gardent la dispersion de la grille élargie
  autour de leur niveau, celle de leur sexe. 686 carrières ; les poids, ceux
  des retraités de 2020 pour toutes les générations, comme toute grille.
  `CasTypeLarge` porte un niveau qui dépend de la génération et le temps
  partiel, que la construction d'une carrière savait déjà appliquer
  (`temps_partiel`). Trois tests le tiennent, dans `test_grille_large.py`.
- *Trouvé en chemin : l'activité partielle.* En 2020 et 2021, le centile 10
  du salaire en équivalent temps plein tombe de 0,46 à 0,40 fois la moyenne
  des deux sexes chez les femmes, de 0,52 à 0,46 chez les hommes. La
  génération 1975, qui y lisait sa forme, touchait le minimum à 24,4 %, ses
  voisines à 19 ou 20 % ; la forme se lit désormais à l'année la plus proche.
- *Le minimum contributif contre l'EACR* (`part_minimum_contributif.py`,
  les deux grilles passées le même jour), en pour cent des liquidants et, pour
  le minimum moyen, en euros de 2023 par mois :

  | | grille « ensemble » | population | EACR, alignés (Cnav) |
  |---|---|---|---|
  | 2019 | 22,3 | 17,4 | 20,4 (19,8) |
  | 2020 | 21,5 | 17,4 | 18,4 (17,8) |
  | 2021 | 22,0 | 17,1 | 17,9 (17,5) |
  | 2022 | 23,7 | 18,8 | 18,9 (18,3) |
  | 2023 | 24,6 | 20,1 | 18,8 (17,9) |
  | 2024, estimée | 27,6 | 24,3 | 18,6 (17,4) |
  | femmes, 2022 et 2023 | 24,8 et 25,2 | 26,9 et 27,4 | 25,2 et 25,2 |
  | hommes, 2022 et 2023 | 22,3 et 23,8 | 9,2 et 10,4 | 12,2 et 12,2 (11,0 et 10,7) |
  | minimum moyen, 2019-2023 | 123 à 153 € | 78 à 91 € | 134 à 139 € (138 à 142 €) |

  La part tient, de 2019 à 2023, de −3,0 à +1,3 point des régimes alignés,
  quand la grille « ensemble » en était de +1,9 à +5,8 ; les hommes, que cette
  grille mettait au double, sont au niveau de la Cnav. Mais le minimum moyen
  tombe à six dixièmes de l'observé, et 2024 saute : la réforme de 2023 fait
  passer les femmes de 27,4 à 37,6 %, quand TRAJECTOiRE attend 4,3 points de
  plus en tout et que l'estimation de l'EACR n'en voit aucun.
- *Contre TRAJECTOiRE, la génération 1975* : 26,1 % des femmes et 11,7 % des
  hommes, pour 31,6 et 18,1, qu'il dit surestimer ; la majoration à 14,3 et
  9,1 %, pour 15,0 et 5,2 ; un minimum moyen de 106 € pour les femmes, comme
  lui, et de 74 € pour les hommes, pour 82.
- *Les pensions de 2020 contre l'EIR* (`grille_large.py --grille population`),
  en euros par mois, la grille « ensemble » au 7 octobre entre parenthèses :

  | | moyenne | d1 | médiane | d9 | Kolmogorov |
  |---|---|---|---|---|---|
  | EIR, ensemble | 1 536 | 402 | 1 382 | 2 730 | |
  | population | 1 488 (1 436) | 582 (478) | 1 265 (1 197) | 2 532 (2 603) | −7,4 pt à 800 € (+9,9 à 1 300) |
  | EIR, femmes | 1 177 | 283 | 1 013 | 2 229 | |
  | population | 1 275 (1 329) | 427 (386) | 1 153 (1 126) | 2 217 (2 435) | −14,4 à 800 (−11,1 à 800) |
  | EIR, hommes | 1 957 | 872 | 1 745 | 3 242 | |
  | population | 1 715 (1 558) | 805 (647) | 1 389 (1 229) | 3 028 (2 768) | +16,6 à 1 300 (+26,6 à 1 300) |

  La pension moyenne des femmes est inférieure de 26 % à celle des hommes,
  pour 40 % dans l'EIR et 15 % dans la grille « ensemble » ; les femmes
  touchent encore 8 % de trop, les hommes 12 % de moins.
- *Ce que la page en dirait*, contre la page du jour : l'écart des années
  observées, −2,10 points au scénario 2 et −3,89 aux scénarios 4 et 6
  (−2,51 et −4,94 pour la grille « ensemble » au 7 octobre) ; la part du PIB
  en 2070, rien au système actuel, calé sur le COR, −0,14 point à la
  proposition ; son solde moyen de 2026 à 2070, de −0,89 à −0,58 point de
  PIB ; la garantie vieillesse en 2070, +0,081 point de PIB ; le passé refait
  à rebours, au pire depuis 2000, à 12,9 % de la dépense observée, pour
  16,6 % sur la page. Les 980 couples que le moteur écarte, contre 21 sur la
  page, le sont pour les deux mêmes motifs, une liquidation antérieure à la
  répartition ou aucun régime actif : des carrières courtes des générations
  d'avant les assurances sociales, plus nombreuses parce que les carrières le
  sont.
- *Un essai, hors dépôt : le temps partiel toute la carrière.* Le salaire
  annuel moyen ne retenant que les vingt-cinq meilleures années, le temps
  partiel de 25 à 49 ans le touche peu. Tenu de l'entrée au départ, il porte
  la part des femmes de 28,6 à 31,9 % de 2019 à 2023, au-dessus de l'observé,
  et le minimum moyen à 93 à 112 € seulement : ce n'est pas sa durée qui
  manque.
- *Ce que la mesure accuse, à vérifier.* L'ancrage n'en est pas la cause : le
  salaire moyen par tête du modèle, 40 897 € bruts en 2024, est à quelques
  pour cent près le salaire moyen en équivalent temps plein du privé. Restent
  les deux points que la note du 7 octobre de l'action 138 (étape 14) laissait
  après le salaire des sexes. Une dispersion de CARRIÈRE : la coupe de
  l'année, tous âges, donnée à vie au-dessus d'un profil d'âge, compte deux
  fois l'âge au bas de l'échelle ; les hommes y touchent trop peu, et le
  minimum y relève surtout des carrières complètes posées juste sous son
  seuil, d'où de petits compléments. Des parts par GÉNÉRATION : celles de
  2020 donnent aux femmes 26,9 % de carrières de moins de trente années, pour
  33,7 % dans l'EIR, et à toutes les générations les durées des retraités de
  2020. Le saut de 2024, enfin, est celui de sept centiles devant un seuil
  qui monte.

**Ce qui reste** de l'étape, dans l'ordre : une dispersion de carrière, bornée
par des sources publiées, et des parts par génération, qui demandent que les
mesures donnent à une carrière un poids par génération ; puis la mesure, sans
s'y caler ; enfin, au propriétaire, la bascule de la page, chiffres en main.
