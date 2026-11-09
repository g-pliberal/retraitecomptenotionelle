# Étape 3 : le pont relancé

**Le 9 novembre 2026, ce qui est fait.** Le pont gardé ouvert
(`src/retraite_notionnelle/pont.py`, machine 15 de l'inventaire) a désormais
l'état qui lui manquait : node mort. Trois tests de `tests/test_pont.py`
l'ont dit d'abord, vus rouges chacun pour sa raison :

- `test_le_pont_ouvert_se_relance_quand_node_s_est_arrete` — node tué entre
  deux demandes, la suivante rend le jour de naissance présumé, le 15, sur
  un node relancé, au lieu de « node s'est arrêté » jusqu'à un
  `pont.fermer()` ; le pont mort est refermé.
- `test_node_mort_en_pleine_demande_la_fait_echouer_avec_son_journal` —
  un programme qui tombe en lisant sa demande la fait échouer, avec ce qu'il
  a écrit sur sa sortie d'erreur, comme aujourd'hui ; la demande suivante
  relance le vrai `pont.mjs`, sans que le paquet ait changé.
- `test_fermer_un_pont_mort_ferme_son_tuyau_d_entree` — une demande écrite
  à un node mort reste dans le tuyau ; le pont refermé le ferme sans
  l'écrire, au lieu que Python le signale en le ramassant
  (`Exception ignored … BrokenPipeError`).

Le code : `_PontOuvert.vivant()` lit si node tourne encore ; `_ouvert()`
relance un pont mort comme un pont dont le paquet a changé ; une demande
qui voit node s'arrêter lit son journal, referme le pont, puis échoue ;
`fermer()` ferme le tuyau d'entrée dans tous les cas, l'erreur d'un tuyau
rompu tue, et attend node. Une demande en vol quand node meurt échoue
encore — la relancer cacherait un node qu'elle aurait fait tomber —, et la
suivante aboutit : un `kill()` sans `wait()` le montre, la mort n'étant pas
encore vue quand la demande part.

**Ce qui reste.** Rien pour cette étape. Hors d'elle, relevé en chemin :
chaque `_PontOuvert` s'inscrit à `atexit`, qui le garde jusqu'à la sortie,
avec son tuyau de sortie et son journal ; un pont relancé souvent les
accumulerait. Ce n'est pas un défaut observé, et rien ne l'inscrit.
