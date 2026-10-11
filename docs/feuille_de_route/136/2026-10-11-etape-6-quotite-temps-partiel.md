# Étape 6, la population : la quotité du temps partiel certifiée

**Le 11 octobre 2026 : la durée d'un temps partiel salarié, rapportée à celle
d'un temps complet, entre au dépôt, par sexe et par âge, de 1983 à 2025. Avec
la part du temps partiel et les centiles du salaire, certifiés le même jour,
la population a de quoi passer du salaire d'une heure à celui d'une année.**

Demande du propriétaire : « vas-y, certifie la quotité du temps partiel »,
l'étape que la note du même jour sur le temps partiel laissait.

- *Où elle se trouve.* L'INSEE la mesure par l'enquête Emploi, mais ne la
  publie par sexe que dans le texte de sa fiche « Temps partiel » d'« Emploi,
  chômage, revenus du travail », une année par édition et sans la durée d'un
  temps complet — en 2025, 23,5 heures pour les femmes à temps partiel et
  21,9 pour les hommes, hors apprentis ; sa figure 3 répartit les salariés à
  temps partiel en quatre tranches d'heures, de moins de 15 à 30 ou plus.
  Aucun jeu de Melodi ne la porte. Eurostat la rediffuse en série, de
  l'enquête française sur les forces de travail : `lfsa_ewhuis`, la durée
  habituelle hebdomadaire dans l'emploi principal, par statut, temps de
  travail, âge, sexe et profession, de 1983 à 2025. Elle redonne la fiche :
  23,5 heures pour les femmes en 2025, et 22,1 pour les hommes, apprentis
  compris. Sans filtres, la table ne se sert qu'en différé ; filtrée sur les
  salariés de toutes professions, elle rend 1 032 durées.
- *Le fichier.* `data/reference/macro/quotite_temps_partiel.csv`, 516 valeurs
  certifiées : pour chaque année, chaque sexe et l'ensemble, et chaque
  tranche — 15-24 ans, 25-54 ans, 50 ans ou plus, tous âges —, la durée d'un
  temps partiel rapportée à celle d'un temps complet du même sexe et de la
  même tranche. Les tranches portent les noms de celles de l'INSEE ; celle
  des 25-54 ans chevauche celle des 50 ans ou plus, Eurostat ne publiant pas
  les 25-49 ans. Un récupérateur neuf
  (`scripts/fetch/eurostat_duree_temps_partiel.py`), la vérification
  (`source_quotite_temps_partiel`), qui ne certifierait pas une année dite peu
  fiable, et le manifeste (`eurostat_duree_temps_partiel`) le portent ; le
  journal reçoit sa seule trace (145 séries, 72 244 valeurs), le parcours de
  présentation suit, et le fichier reste dans l'empreinte du modèle.
- *Ce qu'elle dit.* Un temps partiel de femme vaut 0,53 temps complet en
  1983, 0,61 en 2000, 0,62 en 2025 ; d'homme, 0,63, puis 0,58 et 0,56. En
  2025, il est plus court avant 25 ans (0,54 pour les femmes) et après 50
  (0,57) qu'entre les deux (0,66). L'ensemble des deux sexes peut tomber sous
  chacun d'eux — 0,551 en 1990, pour 0,562 chez les femmes et 0,553 chez les
  hommes — : les hommes, plus nombreux à temps complet, y allongent la durée
  d'un temps complet.
- *Ce qu'elle n'est pas.* La quotité d'une personne : une moyenne, quand un
  temps partiel va de moins de 15 heures à plus de 30. Une série d'un seul
  tenant : elle se rompt en 2003 (l'enquête en continu), 2005, 2006, 2014,
  2021 et 2024, et sa définition change en 2021 ; les ruptures se gardent,
  l'en-tête les dit.

**Ce qui reste** de l'étape : la population par génération et par sexe,
construite à côté de la page et mesurée — minimum contributif, part et
montant, contre l'EACR ; pensions contre l'EIR — ; puis, au propriétaire, la
bascule de la page, chiffres en main.
