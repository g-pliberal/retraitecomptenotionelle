# Étape 6, la population : les salaires de chaque sexe certifiés, la forme laissée à la mesure

**Le 11 octobre 2026 : les centiles du salaire du privé, sexe par sexe,
entrent au dépôt — l'étape que les trois formes de population proposées au
propriétaire ont en commun. La forme elle-même se tranchera sur la mesure.**

Demande du propriétaire : « Action 136, étape 6, seconde moitié : la
population », chercher une distribution publiée du salaire du privé par sexe,
puis proposer deux ou trois formes de population, leur coût, ce qu'elles
changent aux réglages de la page Coût, et les mesures qui les valident. Après
la proposition : « je ne sais pas quoi choisir […] il faut faire un choix
parce qu'on manque de données ? » ; puis, à la réponse qui suit, « vas-y ».

- *La source était dans celle de la dispersion.* Le jeu de l'INSEE que lit
  déjà `dispersion_salaires.csv`, `DS_DERA_PRIVE_SERIES_LONGUES`, a une
  dimension `SEX`, que le récupérateur fixait à l'ensemble. Laissée libre,
  elle donne, à temps complet et en équivalent temps plein, la moyenne de
  chaque sexe depuis 1951 ; le centile 10 et la médiane en 1955, 1960, 1965
  et 1970, puis chaque année depuis 1975, le 90 de même depuis 1960 ; le 25
  et le 75 depuis 1976 ; le 95 et le 99 depuis 1994 (tous sexes, le 10, la
  médiane et le 90 sont annuels depuis 1951). Ses valeurs tous sexes redonnent
  le fichier certifié à la quatrième décimale. Rapporté à la moyenne des deux
  sexes, en 2024 : 0,48, 0,77 et 1,46 pour les femmes (centile 10, médiane,
  90), 0,53, 0,86 et 1,71 pour les hommes ; le salaire moyen des femmes vaut
  0,65 fois celui des hommes en 1955, 0,69 en 1976, 0,80 en 2000, 0,87 en
  2024.
- *Ce qu'elle n'a pas.* Ni le temps partiel ni l'année incomplète, que la
  pension compte : le même jeu porte les sept centiles de chaque sexe tous
  temps de travail confondus, de 1996 à 2024, mais toujours ramenés à
  l'équivalent temps plein. Aucun centile n'y croise le sexe avec l'âge ou la
  catégorie, seulement des moyennes. Deux sources ont le volume de travail :
  le revenu salarial de l'INSEE (fiche F30 d'« Emploi, chômage, revenus du
  travail », 2026 : annuel, public compris, 0,74 année d'équivalent temps
  plein pour les femmes et 0,79 pour les hommes en 2023, déciles par sexe pour
  2023 seulement) ; l'enquête Emploi (Melodi `DD_EEC_SERIES`), qui donne la
  part du temps partiel dans l'emploi par sexe et grande tranche d'âge de
  1975 à 2025 — 17,2 % des femmes en emploi en 1975, 32,0 en 2000, 26,7 en
  2024.
- *Le fichier.* `data/reference/macro/dispersion_salaires_sexe.csv`, 790
  valeurs certifiées : chaque centile et la moyenne de chaque sexe, rapportés
  au salaire moyen des DEUX sexes de l'année — le dénominateur commun garde
  l'écart, et la ligne `moyenne` d'un sexe ramène ses centiles à sa propre
  moyenne. Le récupérateur (`insee_profil_salaire_age.py`), la vérification
  (`source_dispersion_salaires_sexe`) et le manifeste
  (`insee_dispersion_salaires_sexe`) le portent ; le journal de certification
  ne reçoit que sa trace (143 séries, 71 116 valeurs), et le parcours de
  présentation suit. Le fichier reste dans l'empreinte du modèle, hors de
  `memoire.HORS_DU_MODELE` : la population le lira. En passant, l'en-tête de
  `dispersion_salaires.csv` et sa note au manifeste dataient le 25 et le 75
  de 1980, le 95 et le 99 de 1995 : le fichier les porte depuis 1976 et 1994.
- *Deux essais, hors dépôt*, la grille « ensemble » de
  `scripts/grille_large.py` passée par `part_minimum_contributif.py` (3 min
  30 s chacun sur quatre cœurs), en 2023 :

  | | grille du dépôt | salaire lié au sexe | et le cas type du Smic gardé au Smic | EACR, Cnav ; alignés |
  |---|---|---|---|---|
  | ensemble | 24,6 % | 24,6 % | 20,8 % | 17,9 % ; 18,8 % |
  | femmes | 25,2 % | 27,6 % | 26,2 % | 24,5 % ; 25,2 % |
  | hommes | 23,8 % | 20,6 % | 13,9 % | 10,7 % ; 12,2 % |
  | minimum moyen, € de 2023 par mois | | 129 € | 63 € | 138 € ; 134 € |
  | hommes de 1975, majorés | 22,4 % | 19,6 % | 25,3 % | 5,2 % (TRAJECTOiRE) |

  Lié au sexe, le salaire ne ferme qu'un quart de l'écart des hommes, éloigne
  les femmes et laisse l'ensemble où il était. Le reste vient de l'axe des
  salaires, qui étale chaque cas type sur toute la coupe du privé : le cas
  type du Smic, payé le Smic de chaque année, met 17,5 % de son poids à la
  moitié du Smic, toute une carrière. Gardé au Smic, la part tombe à un à
  trois points de l'EACR, mais le minimum moyen tombe à la moitié de
  l'observé, 2024 saute à 30,2 % et les hommes de 1975 remontent à 29,3 % : la
  carrière complète au Smic est posée sur le seuil du minimum, où quelques
  euros décident de la part. Sept centiles autour de treize cas types ne
  posent que des masses ponctuelles là où le minimum se décide ; le bas de
  l'échelle demande une distribution fine, sexe par sexe, avec le temps
  partiel.
- *Les trois formes proposées.* A : la grille élargie, le salaire lié au
  sexe, la page gardant ses treize cas types — une session, rien de plus à
  chaque envoi, et l'essai en donne déjà le verdict. B : une population
  construite génération par génération et sexe par sexe — les régimes de
  l'EIR, le salaire tiré du rang dans la distribution de son sexe, le temps
  partiel, les durées recalées sur chaque génération —, des parts calculées
  sans tirage, fabriquée en Python et lue par la page ; trois à cinq
  sessions, six à sept minutes de plus à chaque course de GitHub. C : une
  population tirée au hasard, microsimulée, passée par le pilote, qui seule
  accueillera couples, départs choisis et recours à l'ASPA ; une dizaine de
  sessions, et un bruit d'échantillonnage à tenir. Aucune ne touche aux
  réglages de la page Coût, qu'elle n'a plus depuis l'action 150 ; B et C
  changent le tableau de ce que pèse chaque carrière, les « treize cas
  types » de son texte, et laissent Carrières types sur les siens. Les
  mesures qui les jugent : la part et le montant du minimum contributif par
  sexe contre l'EACR, la génération 1975 contre TRAJECTOiRE, la distribution
  des pensions de 2020 contre l'EIR (`grille_large.py --distribution`) ; pour
  B et C, la composition contre l'EIR et le passé refait à rebours contre la
  dépense observée.
- *Pourquoi un choix, et pourquoi pas encore.* Le choix vient de ce qui
  manque : sans les carrières réelles (l'EIC et l'EIR, au CASD, sur une
  habilitation que seul le propriétaire peut demander), le dépôt n'a que des
  distributions publiées une à une, et toute population suppose comment elles
  se combinent chez une même personne. Les trois formes commencent par la
  même étape, faite ici. B se construit ensuite à côté de la page, sans y
  toucher, et se mesure comme la grille élargie ; la bascule de la page — la
  seule vraie décision — se prendra sur ses résultats.

**Ce qui reste** de l'étape, dans l'ordre : le temps partiel par sexe et âge
de l'enquête Emploi, à certifier ; la population par génération et par sexe,
construite à côté de la page et mesurée ; puis, au propriétaire, la bascule de
la page, chiffres en main, et Droits non cotisés, qui resterait sur ses
treize cas types.
