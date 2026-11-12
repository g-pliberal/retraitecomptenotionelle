# Lot B, quatrième session : `mortalite_population.py` demande ses calculs au portage

**Ce qui est fait.** L'étude de la mortalité ne fait plus tourner le moteur
Python d'une carrière : ni sa mesure par cas type, qu'une sonde de la prose
lit pour onze chiffres de `docs/methodologie.md`, ni son option `--deficit`.
Le portage date, bâtit et simule ses carrières, par le pont. Rien de ce
qu'elle calcule n'a bougé. La fabrique n'entre plus dans le moteur Python
que par trois appels, contre sept : le chargeur des âges de référence
(`construire_donnees.py`), et les deux exemples du README
(`construire_tableaux_md.py`), qui attendent la décision du propriétaire sur
le § 3.

**Ce qui change.**

- *Le pont, en un bloc à part de chaque côté* (« ce que l'étude de la
  mortalité demande »). La demande de la grille du coût reçoit un paramètre
  facultatif, `capitaux`, comme elle avait reçu `comptes` : des scénarios
  qu'il nomme, chaque case rend le capital du compte à la liquidation et ce
  qu'en portent les droits acquis à la bascule (`CAPITAUX_DU_COMPTE` de
  `pont.py`, `capitauxDuCompte` de `pont.mjs`). Sans lui, la case rend un
  dictionnaire vide, et le coût ne lit rien de plus. Une règle de plus
  s'appelle par `pont.droit` : `conversion.niveau_relatif`, le niveau de
  salaire d'une carrière passée en données (`LECTURES_DE_LA_MORTALITE`,
  `FONCTIONS_DE_LA_MORTALITE`, et son jumeau dans `tests/outils_pont.py`,
  `JUMEAUX_DE_LA_MORTALITE`). Le jumeau Python de la demande,
  `cout._simulations_en_python`, rend `capitaux` de même : les
  confrontations de `tests/test_pont.py` comparent les deux réponses champ
  par champ.
- *La mesure* (`mesurer`). Le cas type se bâtit par
  `pont.carrieres_de_la_grille`, qui rend aussi la carrière que l'âge légal
  de la proposition en dérive ; il se simule deux fois par
  `pont.grille_du_cout`, la table de mortalité dans les paramètres de la
  demande. Le report du départ de la proposition se lit sur la simulation
  (`depart_reporte`), non sur la carrière bâtie : le simulateur ne reporte
  pas un départ antérieur à la bascule.
- *Le niveau de salaire d'un cas type* (`niveau_relatif`, dans le script) :
  le niveau écrit, sauf pour le salarié au SMIC, dont le portage lit le
  niveau sur la carrière qu'il a bâtie. La sonde de la prose et l'option
  `--niveau-de-vie` l'appellent à la place de `CasType.niveau_relatif`.
- *Le déficit.* Les carrières de la grille se bâtissent au portage, sur le
  paquet des données du jour, comme le coût bâtit la sienne (`_carrieres`).
  `_vingtiles` demande le niveau de toutes en une fois ; `_parts_ouvertes`
  lit les capitaux de la demande de la grille.

**Le critère, vérifié en faisant tourner**, avant le premier changement puis
après le dernier :

| ce qui est comparé | résultat |
|---|---|
| les sorties du script sans option, sous `--cas-type salaire_moyen --generations 1960 1990`, sous `--niveau-de-vie` | identiques à l'octet |
| les deux sorties du déficit, `--deficit` et `--deficit --depuis 2026` | identiques à l'octet |
| 111 mesures à pleine précision : le fonctionnaire sédentaire sur sept générations, les treize cas types sur huit, chacun à son vingtile | égales, nombre par nombre |
| le niveau de salaire des 104 mêmes couples, par le pont | égal à celui que rendait `CasType.niveau_relatif` |
| le vingtile et la part ouverte à la bascule des 498 couples de la grille | égaux |
| les onze chiffres ancrés | `verifier_prose.py` : la prose dit le vrai |
| `python scripts/regenerer.py`, la fabrique entière | aucun fichier changé : le paquet, les agrégats du coût, les témoins, les pages |
| `test_cout.py`, `test_facteurs_depense.py`, `test_affirmations.py` | 875 tests verts |

**Deux différences de chemin, sans effet sur les sorties.**

1. *Une case que le droit écarte.* Le portage refuse de bâtir un cas type
   dont le départ précède l'origine de la répartition, ou dont aucun régime
   n'existe encore ; `CasType.construire` ne le vérifiait pas, et laissait
   la simulation décider. La mesure dit alors « écarté », avec le motif du
   portage. Aucun des 111 couples mesurés n'est dans ce cas ; une génération
   ancienne demandée à la main pourrait l'être.
2. *Le paquet lu.* La mesure se calcule sur `moteur/donnees.json`, comme les
   autres sondes de la prose ; le déficit, sur le paquet du jour, comme le
   coût. Le moteur Python lisait les données du jour. Les deux sont les
   mêmes dès que la fabrique a tourné.

**Les tests, écrits d'abord.** Quatre tests neufs dans
`tests/test_mortalite_population.py`, de la suite rapide. Vus rouges pour la
raison attendue : les capitaux (la demande ne connaissait pas `capitaux`) ;
le relevé de ce qui entre dans le moteur Python quand la sonde, les
vingtiles et les parts ouvertes tournent (il nommait `simuler`,
`niveau_relatif`, `age_de_depart` et `carriere_simple`, il est vide). Le
niveau de salaire a été vérifié rouge sans sa déclaration, à la main. Le
test de la mesure — le scénario 1 ne bouge pas d'un euro, la proposition
reportée se sert sur l'espérance de son départ à 65 ans — est vert avant
comme après : il tient un comportement que le changement devait garder.
Deux attentes de mes tests étaient fausses, et ont été corrigées contre la
règle, non contre le code : le fonctionnaire sédentaire né en 1975 part à
65 ans, sa proposition n'est donc pas reportée, et l'exemple est devenu le
salarié au salaire moyen ; une carrière d'un seul statut n'a le niveau saisi
que sous le profil plat. Les quatre tests passent sous la garde des
présomptions (`PRESOMPTIONS_DECALEES=1`) : aucun n'attend un chiffre publié.
La liste de `tests/test_entrees_du_moteur.py` perd les quatre appels de
l'étude.

**Ce que cette étape laisse.**

- `CasType.niveau_relatif` (`castypes.py:129`) bâtit encore la carrière du
  salarié au SMIC au moteur Python. Il lui reste deux appelants :
  `tests/test_moteur.py:333`, qui le confronte au moteur Python, et
  `scripts/grille_large.py:1682`. Il part avec la paire, ou se branche sur
  `mortalite_population.niveau_relatif`, qui rend le même nombre.
- `cout._simulations_en_python` porte une lecture de plus, `capitaux` : elle
  part avec lui.
- Le déficit bâtit deux fois la grille, une pour les vingtiles, une pour les
  parts ouvertes, comme avant ; les deux lectures prennent 25 secondes
  ensemble.

**Ce qu'il faudrait changer au bloc « Reprise » de l'action 161**, que cette
session ne récrit pas : « trois études » devient « quatre études », l'étude
de la mortalité comprise ; et la fabrique n'entre plus dans le moteur Python
que par le chargeur des âges de référence et les deux exemples du README.

**Ce qui n'est pas vérifié.** La suite complète, que GitHub lance. L'étude
sur une autre population que les fonctionnaires civils de l'État et les
vingtiles, ou sur des données d'ailleurs, que personne ne demande.

**Ce qui ne change pas.** Aucune règle du scénario 1, aucune donnée, aucun
fichier fabriqué, aucune garde. Aucun code du moteur Python n'est retiré.
