# Le paquet du dépôt dans la clé de `moitie_python`

**Le 3 novembre 2026.** La moitié Python d'une confrontation bâtit souvent ses
carrières par le pont gardé ouvert, sur le paquet du dépôt
(`moteur/donnees.json`) : celles de `test_droit.py`, de `test_liquidation.py`
et de `test_web.py` (`_carrieres_au_hasard`), par `outils_pont.Saisies`. Ni
l'empreinte de la mémoire ni la clé de `moitie_python` ne le lisaient : une
moitié calculée sur un paquet en retard sur `data/` se gardait sous l'empreinte
des données nouvelles, et resservait une fois le paquet refait (note du 29
octobre).

- *Le remède.* `memoire.memoriser` prend des `fichiers_lus`, lus hors des
  sources : l'empreinte de leur contenu entre dans la clé, et un calcul pendant
  lequel l'un d'eux a bougé se rend sans se garder, comme pour les sources.
  `moitie_python` y nomme le paquet (`outils_portage.PAQUET`), 22 ms de
  hachage. Toutes ses moitiés le portent, même celles qui ne passent pas par le
  pont : le paquet ne bouge sans le modèle que lorsqu'il rattrape les données
  (`regenerer.py`, ou le commit de GitHub), et l'une d'elles se refait alors une
  fois pour rien, quand une déclaration au cas par cas s'oublierait.
- *Le test.* `test_une_moitie_python_se_garde_sous_le_paquet_que_le_pont_lit`
  (`test_outillage.py`), vu rouge : le paquet refait ne refaisait rien. La
  garde du paquet récrit pendant le calcul ôtée, sa dernière assertion tombe.

**La preuve**, sur `test_les_deux_moteurs_ecrivent_les_memes_etapes`
(`test_droit.py`) : 31 s la mémoire froide, 9 s ensuite ; une ligne vide au
bout du paquet, 29 s, puis 8 s ; le paquet rendu, 7 s, la moitié d'avant
relue. `-m rapide`, `test_outillage.py` et les autres confrontations qui
passent par `moitie_python` sont verts. `memoire.py` retouché, toute la mémoire
des calculs se refait une fois, comme après toute retouche de `src/`.

**Ce qui reste**, de l'action : `actions/cache` sur GitHub, le modèle et
l'effort des sessions, que le propriétaire décide ; la part de l'éclaireur, à
relever ; les leviers 4 et 5.
