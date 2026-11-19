# Les scripts de l'évaluation du 18 novembre 2026

Ces scripts ont servi à contrôler les affirmations de la note de décision 0009
et à mesurer ce qu'elle ne compte pas. Ils ne modifient rien. Ils se lancent
depuis la racine du dépôt, après `pip install -e '.[dev]'`. Les résultats
ci-dessous sont ceux du 18 novembre 2026, sur `main` à `d3a22e5`.

| Script | Ce qu'il fait | Résultat |
|---|---|---|
| `fenetres.py` | L'âge légal en cinq versions choisies à la date d'effet, contre la table fusionnée, sur quatre jours par mois de naissance de 1923 à 1975 | 2 544 naissances, 0 écart, 0 droit ouvert puis refermé |
| `fenetres_tous_les_jours.py` | Le même essai sur chaque jour de naissance (il importe `fenetres.py`) | 19 358 naissances, 0 écart, 0 droit ouvert puis refermé |
| `fenetres_cl.py <carriere_longue.csv>` | Les portes de la carrière longue : l'âge du texte de la date déclarée, contre la première date d'effet dont le texte ouvre le droit, durée supposée acquise | bascule du 1er septembre 2026, porte des vingt ans : 1 856 dates sur 2 617 trop tard ; bascule de 2023 : 3 410 sur 3 440 trop tôt ; 0 droit ouvert puis refermé |
| `regimes.py` | Les renvois des fichiers de régime, les valeurs de repli, les frontières de périodes | 2 573 renvois, 562 et 469 replis, 793 frontières, 38 périodes datées au jour |
| `bascules.py` | Les changements de renvoi après la première période d'un régime | 216, dont 173 débuts, 41 fins, 2 changements de cible ; 180 à l'année, 36 au jour |
| `compte.py` | Les fiches, leurs versions, leurs dates qui décident, leurs exemples | 267 fiches et 9 de la proposition, 70 sans versions, 65 avec un exemple |
| `code2.py` | Les fiches citées par leur identifiant dans le code | 114 dans `moteur/js`, 124 avec le Python et les scripts |
| `constantes.py` | Les constantes nommées du moteur, celles dont la valeur porte une année ou une date, et les années écrites en clair dans le code des règles (`--liste` les énumère) | 745 constantes dans le moteur hors du site, dont 131 datées ; 399 dans le code des règles, dont 77 datées, où 45 lignes écrivent une année en clair |

Les 152 « trop tôt » que `fenetres_cl.py` affiche pour les portes de 18 et
21 ans sont un artefact : la recherche s'arrête neuf ans après la bascule,
avant l'âge des nés d'août à décembre 1972.

`fenetres_cl.py` simule deux façons de lire la table, hors du moteur : il ne
dit pas ce que le moteur rend.
