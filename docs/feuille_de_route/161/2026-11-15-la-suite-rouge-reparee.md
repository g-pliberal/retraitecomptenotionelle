# La suite rouge réparée : trois fichiers d'oracle qui prêtaient le moteur Python à un outil passé à la façade

La suite complète de GitHub était rouge depuis le passage de
`test_oracle_familles.py` à la façade (« Trois fichiers du relevé à la
façade ») : sa fonction `_notre_calcul`, qui demande désormais ses règles à
la façade, était aussi appelée par `test_oracle_minima.py`,
`test_oracle_categorie_active.py` et `test_oracle_enfants.py`, qui lui
passaient un simulateur du moteur Python. La façade refuse un moteur qu'elle
ne sait pas transmettre (`NonTransmissible` sur `ouvrir.duree_requise`), et
chaque test du module tombait à la mise en place.

**La réparation.** Les trois fichiers prennent leur `Simulateur` à la façade,
comme celui dont ils empruntent le calcul ; `test_oracle_minima.py` y prend
aussi `Carriere` et `liquider`. Aucune règle, aucune donnée, aucun témoin ne
change. Deux tests de `test_oracle_categorie_active.py` lisent la table des
âges des emplois classés (`ages_categorie_active`), que la façade ne sert
pas : ils la lisent, par une fixture à part, sur le moteur Python, et le
fichier reste dans la liste de `test_fichiers_sur_le_moteur_python.py`, d'où
sortent `test_oracle_minima.py` et `test_oracle_enfants.py`.

**Ce qui reste.** Servir cette table à la façade, ou la demander au pont,
quand `test_oracle_categorie_active.py` passera entier au portage.

**Leçon.** Un fichier de tests qui passe à la façade peut prêter ses outils à
d'autres : chercher `from test_<fichier> import` avant de le commiter, et
lancer ces fichiers-là aussi.
