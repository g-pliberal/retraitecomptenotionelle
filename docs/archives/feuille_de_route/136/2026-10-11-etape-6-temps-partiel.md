# Étape 6, la population : le temps partiel par sexe et âge certifié

**Le 11 octobre 2026 : la part du temps partiel dans l'emploi, par sexe et
par âge, entre au dépôt, de 1975 à 2025. Les centiles du salaire, certifiés
le même jour, sont en équivalent temps plein ; elle est la première pièce du
volume de travail que la population donnera à chacun.**

Demande du propriétaire : « vas-y, certifie le temps partiel », la première
des étapes que la note du même jour sur les salaires par sexe laissait.

- *Le jeu.* Les séries longues de l'enquête Emploi sur Melodi
  (`DD_EEC_SERIES`, mesure `PT_WKTIME_IN_EMP_BY_SEX_AGE`), en France entière :
  la part du temps partiel parmi les personnes en emploi, salariées ou non,
  pour les femmes, les hommes et l'ensemble, à 15-24 ans, 25-49 ans, 50 ans
  ou plus et tous âges, chaque année de 1975 à 2025. Toutes les valeurs sont
  dites normales ; une valeur non significative ne se certifierait pas.
- *Ce qu'il dit.* Le temps partiel des femmes monte de 17,2 % en 1975 à
  32,0 % en 2000, puis redescend à 26,7 % en 2024 ; celui des hommes passe de
  3,3 % à 8,7 %. Chez les femmes, il est le plus fréquent après 50 ans en 2024
  (31,3 %) comme en 1975 (28,2 %) ; chez les hommes, avant 25 ans (15,1 %).
- *Le fichier.* `data/reference/macro/temps_partiel.csv`, 612 valeurs
  certifiées, en pour cent, une ligne par année, sexe et tranche — les
  tranches sous leur code INSEE, tous âges sous `ensemble`. Un récupérateur
  neuf (`scripts/fetch/insee_temps_partiel.py`), la vérification
  (`source_temps_partiel`) et le manifeste (`insee_temps_partiel`) le portent ;
  le journal de certification ne reçoit que sa trace (144 séries, 71 728
  valeurs), et le parcours de présentation suit. Comme les centiles par
  sexe, il reste dans l'empreinte du modèle : la population le lira.
- *Ce qu'il n'a pas.* La quotité : la part dit combien travaillent à temps
  partiel, non combien d'heures. Melodi ne la donne pas par sexe — les
  résultats annuels (`DD_EEC_ANNUEL`) ne portent la durée travaillée que par
  profession, tous sexes et temps de travail confondus, et ne détaillent
  l'âge par cinq ans, pour la part, que la dernière année. Le champ n'est pas
  non plus celui des salariés du privé : la série compte les non-salariés et
  la fonction publique. Le revenu salarial de l'INSEE (fiche F30 d'« Emploi,
  chômage, revenus du travail », 2026) donne le volume de travail entier,
  temps partiel et année incomplète ensemble : 0,74 année d'équivalent temps
  plein pour les femmes et 0,79 pour les hommes en 2023, dans un classeur et
  non par l'API.

**Ce qui reste** de l'étape, dans l'ordre : la quotité du temps partiel par
sexe, ou le volume de travail du revenu salarial, à chercher et certifier ;
puis la population par génération et par sexe, construite à côté de la page
et mesurée ; enfin, au propriétaire, la bascule de la page, chiffres en main.
