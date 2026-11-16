# La carrière nue hors des règles : `Carriere` et `Comparaison` sous `types_du_pont/`

Action 161, étape 1 bis du plan de `2026-11-16-l-inventaire-du-retrait-des-regles.md`,
qui clôt l'étape 1. Aucune règle n'a changé : le paquet et les témoins refaits
sont identiques à l'octet, la suite rapide et les tests de la zone sont verts.

## Ce qui a bougé

- **`types_du_pont/carriere.py`** porte la carrière nue : ses champs, sa
  validation (sexe, mois et jour de naissance, tri des lignes, deux lignes
  d'une année sous le même statut), et dix-huit lectures de ses lignes, du
  calendrier et de sa chronologie, sans règle du droit : première et dernière
  années, naissance, jour de naissance, origine des âges, `date_de_l_age`,
  `mois_de_l_anniversaire`, `age_au`, `generation`, date, année, mois et
  fraction de la liquidation, années cotisées, `lignes_de`, `ligne`,
  `affiliations_utilisees`.
- **`carriere.py`** garde les règles sur une classe qui hérite de la nue,
  `Carriere(_CarriereNue)`, sans `@dataclass` : elle reprend les champs, le
  constructeur et l'égalité. Son `__post_init__` appelle celui du type, puis
  remplit la chronologie d'une carrière bâtie ligne à ligne
  (`droit.preparer`), seule règle du constructeur. Tout le reste est là, tel
  quel : durées et dates de service, trimestres, statuts au 1er janvier,
  invalidité, conjoint, `prolongee`, `arretee_au_deces`, les `depuis_*`.
- **`types_du_pont/comparaison.py`** loge `Comparaison`, `ContributionEmployeur`
  et les deux résumés de `dictionnaire()` ; `simulateur.py` les réimporte.
  Son champ `carriere` est annoncé sous le type nu.
- **Le pont** lit la carrière sous le type nu (champs, indices, `isinstance`,
  lecture stricte, qui accepte toute sous-classe), et la bâtit sous la classe
  des règles : les appelants Python l'interrogent encore comme une carrière
  du moteur. `OBJETS_DU_RESULTAT` et la lecture de la comparaison nomment
  `types_du_pont`.
- La fiche `date_effet_mois_suivant` nomme ses quatre lectures sous
  `types_du_pont/carriere.py` (`tests/test_carte.py`).

## Pourquoi une sous-classe, et non des fonctions

Le plan de l'étape 1 voulait les règles en fonctions, et leurs appelants
récrits. Le relevé en compte quelque 670 appels dans les fichiers de règles et
jusqu'à 1 300 ailleurs (scripts, tests, modules hors règles ; le compte par nom
surestime, `generation` ou `ligne` servant à d'autres objets). Récrire ceux des
fichiers de règles ne sert à rien, ils partent ; ceux d'ailleurs sont l'étape 4,
« le Python seul encore branché ». La sous-classe sépare le type de ses règles
sans toucher à un appelant, et disparaît avec `carriere.py`.

## Ce qui reste

- Le pont importe encore `carriere.py` pour BÂTIR la carrière qu'il rend. Il
  bâtira la nue quand plus aucun appelant ne lui demandera une règle
  (étape 4) ; ce jour-là, `carriere_des_donnees` change d'une ligne.
- `Comparaison.dictionnaire()` lit `trimestres_actuels`, une règle de la
  classe des règles : il ne marche que sur la carrière que le pont bâtit.
  L'étape 2, où la façade porte ses contrats, ou l'étape 4 le tranche.
- `Foyer.servie_avec`, laissé à l'étape 1, attend toujours l'étape 2.

## Tests

`tests/test_types_du_pont.py`, vu rouge avant le déplacement (4 échecs) :
`Comparaison` et `ContributionEmployeur` logent sous `types_du_pont`, et
restent les mêmes objets sous `simulateur` ; la classe des règles hérite de la
nue ; la nue ne porte que ses champs et les dix-huit lectures nommées ; le pont
relit le champ `carriere` d'une comparaison sous la nue. Suite rapide :
5 473 réussis. Zone : `test_pont`, `test_facade`, `test_facade_jumeau`,
`test_jumeaux`, les confrontations légères, 828 réussis. `construire_donnees.py`
et `construire_temoins.py` ne changent aucun fichier.
