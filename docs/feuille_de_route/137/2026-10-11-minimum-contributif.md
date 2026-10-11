# Le minimum contributif : la part des nouveaux retraités, confrontée à l'EACR et à TRAJECTOiRE

**Le 11 octobre 2026 : la série de l'EACR entre au dépôt, et les grilles du
modèle s'y confrontent, à côté de TRAJECTOiRE.**

- *La demande.* Confronter le minimum contributif du modèle aux chiffres que
  la DREES publie : l'Études et résultats n° 1297 (février 2024), chiffré par
  TRAJECTOiRE, qui prévient qu'il surestime la part des bénéficiaires (note
  7), et la part observée par l'EACR, que l'étude trace (graphique 1).
- *La série était dans le classeur, pas au dépôt.* Le manifeste récupère
  l'EACR (`drees_eacr`), mais `scripts/fetch/drees_eacr.py` ne lisait que la
  feuille `A-Cadrage` du premier des deux classeurs. Le second porte
  `E-Minima` : les nouveaux retraités de la Cnav et de la MSA salariés portés
  au minimum, par année de liquidation, sur les campagnes de 2015 à 2024, et
  par sexe depuis 2022. Le récupérateur la lit, avec le flux des nouveaux
  retraités de droit direct du cadrage (`nl_ddir`) ; `verifier_donnees.py`
  certifie la part (`regimes/minimum_contributif_liquidants.csv`, 38
  valeurs, de 2012 à 2024). La trace s'est ajoutée seule au journal :
  `--appliquer`, avec les seules sources de l'EACR dans `data/brut/`, aurait
  retiré celles des autres. Le fichier redonne l'étude pour 2021 (17,5 % au
  régime général, 25,1 % à la MSA salariés) ; 2012 y vaut 27,1 %, au
  millésime le plus récent, quand l'étude lisait 27,6 % à celui de 2021.
  Trois pièges, dits dans son en-tête : la Cnav transmet avec un an de
  retard, et une année grossit d'une campagne à l'autre (2021 : 14,9 % à la
  campagne de 2021, 17,5 % à la suivante) ; le type change de nom en 2023 ;
  2024 n'est qu'une estimation de la DREES. La feuille `B-Liquidants` ne sert
  pas : son sexe perd des liquidants en 2023 (468 686 sur 692 416 à la Cnav).
  Le lecteur de classeurs ne lit plus que les feuilles qu'on lui demande :
  celles de l'EACR vont jusqu'à 125 Mo de XML.
- *Ce que le modèle en sait.* Le minimum d'une carrière, entier ; une part
  demande une population, et le dépôt n'a que des grilles.
  `scripts/part_minimum_contributif.py` passe au scénario 1 de la page
  (`pour_la_projection`) les treize cas types et les 791 carrières de la
  grille « ensemble » de `scripts/grille_large.py`, des générations 1942 à
  1995, et compte, parmi les carrières qui liquident une pension du régime
  général, celles que le minimum relève, à leur poids de personnes de 2020.
  Deux lectures : par génération, et par année de liquidation, où chaque
  génération, née en janvier dans la grille, s'étale sur ses douze mois de
  naissance — sans quoi 2018 et 2021, qu'aucune génération n'atteint à l'âge
  du taux plein des carrières courtes, tombaient à 15,4 %. Trois minutes sur
  huit cœurs, gardées sous l'empreinte du modèle ; le fichier certifié entre
  dans `memoire.HORS_DU_MODELE`, qu'aucun calcul ne lit.
- *La grille de la page.* Un seul cas type au minimum, celui du Smic, que
  la génération 1960 dépasse de peu (8 453 € de pension de base pour un
  minimum majoré de 8 430,56 € en 2020) ; aucune femme ; de 0 à 36 % selon
  l'année. Rien à en tirer.
- *La grille élargie, contre l'EACR.* Elle suit l'enquête jusqu'en 2019, de
  −1,8 à +3,1 points (28,8 % en 2012 pour 27,1), puis s'en écarte : +3,7
  points en 2020, +6,7 en 2023 (24,6 % pour 17,9), +10,1 en 2024 contre
  l'estimation (27,6 % pour 17,4). L'écart est celui des hommes : en 2022 et
  2023, 24,8 et 25,2 % des femmes, pour 24,9 et 24,5 observés ; 22,3 et
  23,8 % des hommes, pour 10,9 et 10,7. Les axes de la grille sont
  indépendants : ses hommes ont les salaires de ses femmes.
- *Contre TRAJECTOiRE.* La génération 1975, qu'il ne donne que par sexe :
  25,3 % des femmes et 26,0 % des hommes dans la grille, pour 31,6 et 18,1 ;
  la majoration à 14,9 % des femmes, autant que lui (15,0), et à 22,4 % des
  hommes, pour 5,2 ; un minimum moyen de 138 et 189 € de 2023, pour 106 et
  82. À long terme, 26,0 % des liquidants de 2030 et de 2040, 24,9 % de ceux
  de 2050, pour 26,5 % chez lui. La réforme de 2023 : près de trois points de
  plus de 2023 à 2024 dans la grille, +4,3 chez lui, −0,5 dans l'estimation
  de l'EACR, que la campagne de 2025 remplacera. TRAJECTOiRE surestime de sept à huit points (25,7 %
  des liquidants de 2024 sans la réforme, pour 17,9 % au régime général en
  2023) : l'écart est le sien, et deux de ses causes sont celles de la
  grille — le taux plein pour tous, aucun non-recours.
- *Où c'est écrit.* Le registre des modèles (`trajectoire` : la
  confrontation, et un écart de plus) ; la limite du coût agrégé
  (`docs/limites/5-bis-cout-agrege.md`, un procès-verbal daté, déclaré
  récit) ; le registre des sources (`drees_er_1297_minimum_contributif`) et
  le manifeste (`drees_eacr`).
- *Ce qui reste.* La part des régimes alignés réunis, que le fichier ne
  porte pas (la Cnav et la MSA y sont à part) ; le montant moyen du minimum
  servi (colonne `m1`), lu dans le fichier source mais non certifié, la MSA
  de 2022 y recopiant l'effectif ; l'estimation de 2024, à remplacer par la
  campagne de 2025 ; et, pour une population (action 136, étape 6), un
  salaire lié au sexe. Les tableaux de l'Études et résultats n° 1283, qu'une
  session parallèle a laissés le même jour faute de population, pourraient
  se lire sur la grille élargie comme ceux-ci, sous les mêmes réserves.
