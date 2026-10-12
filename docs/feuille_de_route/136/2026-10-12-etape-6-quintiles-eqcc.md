# Étape 6, la population : ce qu'une carrière courte acquiert par année validée, certifié

**Le 12 octobre 2026 : aucune source publique ne mesure le volume de travail
des carrières courtes ; l'EIR en mesure le produit. Sa feuille des quintiles
de pension en équivalent carrière complète — la pension divisée par la
proratisation — entre au dépôt, 198 valeurs certifiées. Plus une carrière y
est courte, moins elle acquiert par année : 80,5 % des femmes de moins de dix
années validées sont au premier quintile, 18,5 % de celles de trente à
quarante ans ; 74,0 % des hommes de moins de dix ans. La population, qui tient
le salaire pour indépendant de la durée, y range 64,2 % des premières, 37,2 %
des secondes et 21,7 % des hommes.**

Demande du propriétaire : « Fait l'étape suivante », la première chose qui
restait : le volume des années des carrières courtes, à chercher et certifier.

- *Ce qui a été cherché.* Le volume d'une année ne se publie que pour tous
  les salariés d'une année, jamais selon la durée de leur carrière : la fiche
  « Revenu salarial » de l'INSEE et le dossier sur les bas revenus salariaux,
  déjà au dépôt (`volume_travail.csv`, `heures_salariees.csv`). L'EIC 2017
  de la DREES ne publie que des trimestres, ni salaires ni heures. Ce que le
  volume produit se publie, en revanche : la pension rapportée à la durée.
- *La source.* La feuille « QuintilesEQCC » du classeur de l'EIR 2020 que le
  dépôt lit déjà (DREES, « Caractéristiques de tous les retraités »). La
  pension en équivalent carrière complète est la pension de droit direct
  divisée par la somme des coefficients de proratisation des régimes de base,
  « 950 / (20 % + 60 %) = 1 188 € » ; elle « neutralise l'effet de la
  proratisation » sans dire ce qu'aurait été la pension d'une carrière
  complète (DREES, Conseil d'orientation des retraites, séance du 24 novembre
  2022). La durée retirée, il reste ce que la carrière a acquis par année
  validée : son salaire, son volume, son minimum. Les retraités en sont rangés
  en quintiles, les deux sexes réunis ; un sur cent n'en a pas.
- *Les fichiers.* `data/reference/macro/quintiles_eqcc.csv` : pour les cinq
  quintiles et l'ensemble, chaque sexe, les effectifs, la proratisation
  moyenne, les deux pensions moyennes de droit direct, la part au minimum de
  pension du régime principal, la durée validée hors majorations et ses cinq
  tranches. Le récupérateur de l'EIR
  (`scripts/fetch/drees_caracteristiques_retraites.py`) lit la feuille et
  vérifie ce qu'il lit : les tranches font cent, les quintiles redonnent
  l'ensemble à deux centièmes près, sans le passer, et sont égaux. La
  vérification (`source_quintiles_eqcc`) et la fiche de la source
  (`drees_eir_caracteristiques`) la portent ; le journal en garde la trace
  (149 séries, 72 999 valeurs), et le parcours de présentation suit.
- *Ce qu'elle dit.* La part de chaque tranche de durée validée hors
  majorations qui tombe dans le premier quintile, puis dans les deux premiers
  (en pour cent) :

  | | moins de 10 ans | 10 à 20 | 20 à 30 | 30 à 40 | 40 et plus |
  |---|---|---|---|---|---|
  | femmes | 80,5 / 96,3 | 62,0 / 85,9 | 44,2 / 73,8 | 18,5 / 46,3 | 10,1 / 32,0 |
  | hommes | 74,0 / 91,2 | 42,9 / 63,3 | 29,8 / 54,0 | 9,9 / 25,3 | 3,7 / 17,4 |

  Le premier quintile est celui des carrières courtes : sa proratisation
  moyenne est de 61,4 %, celle des trois derniers de 97,9 à 99,5 %.
- *Ce qu'elle dit à la population.* Mesurée hors du dépôt, sur les deux
  dernières versions : chaque carrière de la population, à chacune de ses
  cohortes en vie en 2020, sa pension de l'année divisée par sa durée
  d'assurance tous régimes, enfants compris, rapportée à la durée requise et
  bornée à un ; rangée en quintiles sous les poids de la page, en têtes. La
  part de chaque tranche au premier quintile :

  | | femmes, moins de 10 ans | 10 à 20 | 20 à 30 | 30 à 40 | 40 et plus | hommes, moins de 10 ans | 10 à 20 | 20 à 30 | 30 à 40 | 40 et plus |
  |---|---|---|---|---|---|---|---|---|---|---|
  | EIR | 80,5 | 62,0 | 44,2 | 18,5 | 10,1 | 74,0 | 42,9 | 29,8 | 9,9 | 3,7 |
  | quatrième version | 91,5 | 71,2 | 49,2 | 31,0 | 11,7 | 51,0 | 28,4 | 15,5 | 9,3 | 5,9 |
  | cinquième version | 64,2 | 47,3 | 43,3 | 37,2 | 15,3 | 21,7 | 20,0 | 17,9 | 10,1 | 7,5 |

  Les sexes s'y rangent juste — 31,3 % des femmes au premier quintile, pour
  29,2 % —, les durées non : la proratisation moyenne du premier quintile est
  de 79,9 %, celle des trois derniers de 87,3 à 91,3 %.
- *Ce que la mesure accuse.* Dans l'EIR, la durée range les retraités ; dans
  la population, le seul salaire. Elle donne aux carrières courtes les
  salaires de tout leur sexe, et le premier quintile se remplit de carrières
  longues à bas salaire : les femmes de trente à quarante ans y sont deux
  fois trop. Datées de la jeunesse, les carrières courtes des femmes y
  descendaient davantage que dans l'EIR, celles des hommes d'un tiers à
  moitié moins ; étalées, aucune n'y descend assez. Ce qui manque n'est pas
  un volume moyen, mais un gain par année qui baisse avec la durée, sexe
  par sexe : le tableau ci-dessus en est la mesure.

**Ce qui reste** de l'étape, dans l'ordre : donner aux carrières courtes le
gain par année que l'EIR leur mesure — par le volume de leurs années, ou par
leur rang de salaire selon leur durée —, calé sur ce tableau, la mesure entrant
dans `scripts/grille_large.py` ; puis le minimum contributif, les pensions et
la page ; la pension des hommes, sous l'EIR ; un bas d'échelle plus fin ;
enfin, au propriétaire, la bascule de la page.
