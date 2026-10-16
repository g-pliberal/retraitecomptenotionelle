# L'empreinte de `node --test`

**Le 16 octobre 2026.** `node --test`, que lance
`test_le_portage_javascript_retrouve_les_chiffres_du_modele` (`test_web.py`),
coûtait encore 13 s à chaque passage, la mémoire des calculs pleine : sa
moitié est tout entière en JavaScript. Il ne lit rien du modèle : le portage,
le paquet, les témoins, ses deux fichiers d'essai et les quotients de
mortalité qu'il refait au bit près. Il entre donc dans `ISOLES`
(`tests/conftest.py`), comme `test_pousser.py`, avec deux extensions.

- *Un test seul.* `test_web.py` lit le modèle ; le test, non. Une clé
  `fichier::test` déclare ce seul test ; son fichier entre dans l'empreinte,
  mais pas les modules qu'il importe. `test_un_test_isole_ne_lit_rien_de_son_fichier`
  (`test_niveaux.py`) tient la condition : aucune fixture, aucun nom du module
  hors `pytest` et `__file__`, aucun import du dépôt.
- *Des dossiers.* Ce qu'il lit se déclare en dossiers entiers — `moteur`,
  `tests/js`, `tests/temoins`, `data/reference/mortalite` — dont chaque
  fichier, à toute profondeur, entre dans l'empreinte avec son chemin : un
  fichier retouché, né ou disparu la change (0,2 s pour les 33 Mo).
  `node --version` et les variables `NODE_*` y entrent aussi.

Visé expressément, le test se rejoue ; viser `test_web.py` ne suffit pas,
sans quoi la session du site, qui lance ce fichier, ne gagnerait rien.
`TESTS_SANS_MEMOIRE=1` rejoue tout, et GitHub, sans mémoire, aussi : la garde
ne vaut que sur un poste ou dans une session.

**La preuve, avant de pousser**, le paquet régénéré : le test passe en 8 s,
puis se saute en 0,3 s ; une ligne vide ajoutée à `moteur/js/format.js`, à
`moteur/donnees.json` ou à `tests/temoins/simulations.json`, ou un témoin
vide qui naît, le relance chaque fois (7 à 8 s), et le passage suivant le
saute de nouveau ; le fichier rendu, la marque d'avant resert. Viser
`test_web.py` le saute ; viser le test le rejoue. Un échec ne se marque pas :
le paquet en retard sur le modèle, il se rejoue jusqu'à ce qu'il passe.

**Ce qui reste**, de la note du 10 octobre : les pages au hasard
(`test_web.py`), que la session des pages tient ; les cumuls tirés au hasard
et le portage du coût, à mesurer ; `actions/cache` sur GitHub, que le
propriétaire décide.
