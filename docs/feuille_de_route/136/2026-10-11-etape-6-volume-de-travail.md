# Étape 6, la population : le volume de travail certifié

**Le 11 octobre 2026 : deux tableaux de l'INSEE entrent au dépôt — le volume
de travail annuel moyen en équivalent temps plein, par sexe et par âge, en
2023, et les heures salariées dans l'année, centile par centile, des salariés
du privé et de ceux à bas revenu salarial, en 2019. Une salariée travaille
0,74 année, un salarié 0,79, un temps complet 0,85 ; la moitié des bas revenus
salariaux, moins de 755 heures, quand une année à temps complet en compte
1 820. La population, elle, compte une année entière pour chaque année
travaillée, hors le temps partiel.**

Demande du propriétaire : « vas-y, certifie le volume de travail », la pièce
que la note sur la persistance désignait.

- *Où il se trouve.* Pas dans Melodi : les séries longues de salaires du
  privé n'y portent que des salaires en équivalent temps plein. L'INSEE le
  publie dans « Emploi, chômage, revenus du travail ». Chaque édition de la
  fiche « Revenu salarial » en donne une année — le revenu salarial, le
  salaire en équivalent temps plein et le volume —, par sexe, âge, diplôme,
  catégorie, quotité et secteur, sans les croiser ; sa série longue, depuis
  1995, ne porte que le revenu salarial. Le dossier de l'édition 2024 sur les
  bas revenus salariaux (Emmanuel Berger, Dares) donne la distribution des
  heures de l'année, centile par centile, que la fiche ne donne pas.
- *Les fichiers.* `data/reference/macro/volume_travail.csv`, 21 valeurs
  certifiées, celles de 2023 (le diplôme, de 2022) ; et
  `data/reference/macro/heures_salariees.csv`, 200 valeurs : les centiles 00
  à 99 des salariés du privé de 24 à 62 ans et de ceux d'entre eux dans les
  20 % des revenus salariaux les plus bas deux années de suite, en 2019. Un
  récupérateur neuf (`scripts/fetch/insee_volume_travail.py`) télécharge les
  deux classeurs, les lit avec le lecteur du dépôt et vérifie ce qu'il lit :
  les centiles croissent, et le volume s'écarte de moins de deux centièmes du
  rapport du revenu salarial au salaire. Il ne l'est pas tout à fait — de
  −0,001 à +0,016 selon la ligne, l'INSEE ne calculant pas ses trois moyennes
  sur la même pondération — : seul le volume se certifie. La vérification
  (`source_volume_travail`, `source_heures_salariees`) et le manifeste
  (`insee_volume_travail`, `insee_heures_salariees`) les portent ; le journal
  reçoit leur trace (148 séries, 72 801 valeurs), le parcours de présentation
  suit, et les fichiers restent dans l'empreinte du modèle.
- *Ce qu'il dit.* En années d'équivalent temps plein, en 2023 : 0,74 pour les
  femmes, 0,79 pour les hommes ; 0,48 avant 25 ans, 0,79 de 25 à 39, 0,84 de
  40 à 49, 0,86 de 50 à 54, 0,77 après ; 0,85 à temps complet, 0,51 à temps
  partiel ; 0,68 pour les employés, 0,73 pour les ouvriers, 0,87 pour les
  cadres ; 0,75 dans le privé, 0,83 dans la fonction publique. Les heures de
  2019 :

  | centile | 10 | 25 | 50 | 75 | 90 | 99 |
  |---|---|---|---|---|---|---|
  | salariés du privé | 655 | 1 308 | 1 813 | 1 824 | 1 989 | 2 324 |
  | à bas revenu salarial | 286 | 458 | 755 | 1 030 | 1 241 | 1 489 |

  Un quart des salariés du privé travaillent moins des trois quarts d'une
  année à temps complet ; les trois quarts de ceux à bas revenu salarial,
  moins de 1 030 heures.
- *Ce qu'il dit à la population.* Ses carrières travaillent chaque année
  travaillée en entier, sauf le temps partiel de 25 à 49 ans : pour les
  hommes, dont 3,6 % des carrières en ont, à six dixièmes d'un temps complet,
  un volume de près de 0,99, quand l'INSEE mesure 0,79 ; même un temps
  complet n'en fait que 0,85. Les années sans
  aucun salaire n'y comptent pas : ce qui manque est la part de l'année que
  les entrées, les sorties, le chômage et les contrats courts retirent.
- *Ce qu'il n'est pas.* Le volume d'une carrière : celui des salariés d'une
  année, qui ne dit pas si les années coupées reviennent aux mêmes. Un
  croisement du sexe et de l'âge, ni des heures par sexe : les femmes font 57
  % des bas revenus salariaux, et rien de plus. Ni les heures des bas
  salaires : les bas revenus salariaux sont classés par leur revenu de
  l'année, que les heures font, si bien que leurs heures sont basses par
  construction. Une seule année, enfin : 2023 pour le volume, 2019, avant
  l'activité partielle, pour les heures.

**Ce qui reste** de l'étape : le volume mis dans la population — une part de
l'année retirée aux carrières du salariat privé, par sexe et par âge, qui
redonne en moyenne les 0,74 et 0,79 de l'INSEE et pèse là où le dossier la
met, au bas de l'échelle —, puis mesuré : minimum contributif contre l'EACR,
pensions contre l'EIR, page ; un bas d'échelle plus fin ; enfin, au
propriétaire, la bascule de la page.
