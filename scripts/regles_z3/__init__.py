"""Les règles du droit que le contrôle Z3 interroge (action 194).

Chaque règle est écrite UNE fois, pour deux usages : exécutée avec des entiers
Python (`calcul.Py`), elle est comparée au moteur, cas par cas ; donnée à Z3
(`calcul.Z3`), elle devient une question, à laquelle il répond par une preuve
ou par un contre-exemple chiffré. Tout se lit dans les données du dépôt — les
fiches, le paquet du moteur, ce que le moteur garde au code (`moteur.mjs`) —,
aucun chiffre n'est recopié ici.

- `calcul` : les deux calculs, les mois, les dates ;
- `duree` : la durée requise du régime général (fiche
  `duree_requise_par_generation`, sa table, la pratique de la Cnav) ;
- `fiches` : l'âge légal, l'âge du taux plein, la carrière longue (le paquet,
  `fiches_datees`) ;
- `pension` : la pension de base du régime général rapportée au salaire annuel
  moyen, avec décote, proratisation et surcote ;
- `moteur` : ce que le moteur rend, pour la comparaison et les tables ;
- `questions` : les propriétés posées, chacune avec les champs de ses
  contre-exemples ;
- `controle` : la question posée à Z3, les cas attendus qui l'excusent.

Né des deux essais du 21 novembre 2026 (`docs/feuille_de_route/194/`).
"""
