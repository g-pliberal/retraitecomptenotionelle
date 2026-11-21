# Le tri des tests : huit confrontations du moteur à lui-même retirées

Le 21 novembre 2026, à la demande de Gilles (tri des tests anciens), après un
audit en lecture seule de la suite (rapport dans le dossier du projet,
`architecture/tri-des-tests/`).

Depuis que le moteur Python est parti, la façade des tests (`tests/facade.py`)
sert ses anciens noms par le portage. Huit tests confrontaient encore « les
deux moteurs » : l'un des côtés passait par la façade, l'autre appelait le
même moteur JavaScript par un extrait lancé sous node. Ils ne pouvaient
échouer que si le pont transmettait mal, ce que `tests/test_pont.py` et
`tests/test_contrats_de_la_facade.py` vérifient déjà, et ils ne disaient rien
du droit.

Retirés, avec l'extrait JavaScript que chacun était seul à lire :

- les six `test_le_portage_javascript_*` des fichiers `test_oracle_*.py`
  (carrière longue de la fonction publique, catégorie active, minima,
  périodes assimilées, points enfants de l'Arrco, salaire annuel moyen). Le
  calcul de la façade reste confronté à OpenFisca par les autres tests de
  chaque fichier ;
- les deux tests de `test_mayotte.py` sans assertion propre, qui ne faisaient
  que demander la confrontation de la fixture `deux_moteurs` ; les trois tests
  qui lisent ses lignes, aux valeurs tirées des textes, restent.

Aucun témoin ne bouge. Les fichiers touchés passent (69 tests).
