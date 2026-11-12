# Lot A, première ligne : les tableaux du README et le tableau de bord par le pont, et la liste de ce qui entre encore dans le moteur Python depuis la fabrique

**La pertinence, analysée avant d'agir.** L'étape est pertinente et sûre.

- *Déjà faite ?* Non. Sur `origin/main` au 12 novembre (3944fdc), le dernier
  commit qui touche `scripts/construire_tableaux_md.py` ou
  `scripts/tableau_de_bord.py` est celui de l'action 135 (9747e44), sans
  rapport ; les quatre notes du jour instruisent les questions de
  l'inventaire et ne changent aucun code.
- *Les deux scripts appellent-ils encore ce que l'inventaire dit ?* Oui,
  mesuré en les faisant tourner sous une sonde, sur le `main` du jour.
  `construire_tableaux_md.py` entrait dans le moteur Python par
  `Simulateur.carriere_simple`, `Simulateur.simuler`,
  `moteur/indexation.cumuls` et `EcartAge` ; `tableau_de_bord.py`, par
  `releve.construire`, `Releve.lignes` et, à travers `castypes.py`,
  `pilote.age_de_depart` et `Simulateur.carriere_simple`. C'est la liste de
  l'inventaire du 9 novembre, à une précision près : deux des quatre blocs du
  README, ses deux exemples, ne viennent pas du script mais des sondes de la
  prose, qu'il appelle.
- *Le pont rend-il déjà ce qu'ils lisent ?* Presque tout. Les cumuls des
  règles d'indexation sont une fonction du site, `cumulsIndexation`, que le
  Python fait déjà tourner par node (`web/site.py`). L'écart de chaque
  génération est ce que `pont.carrieres` rend sous `ecarts`. Les carrières
  des cas types se datent et se bâtissent par `pont.carrieres_de_la_grille`.
  Il ne manquait qu'une lecture : ce que chaque ligne d'un relevé cite.
- *Le gain vaut-il le coût ?* Oui. Deux étapes de la fabrique, lancées à
  chaque envoi, cessent de faire tourner les règles du moteur Python, pour
  une lecture de quatre lignes de chaque côté du pont ; et la liste qui en
  sort dit à chaque session suivante ce qui reste, mesuré et non déduit.

**Ce qui est fait.**

1. *Les deux tableaux du README et de la méthodologie.*
   `construire_tableaux_md.cumuls` demande les cumuls à la fonction du site ;
   `ecarts_par_generation` fait bâtir et simuler ses cinq carrières au
   portage, sous chacune des deux règles d'indexation (`pont.carrieres`, les
   paramètres dans la demande). Les neuf cumuls et les dix écarts sortent du
   portage au bit près de ce que le Python calculait ; `README.md` et
   `docs/methodologie.md` sont identiques à l'octet.
2. *Les relevés du tableau de bord.* `tableau_de_bord.releves_des_cas_types`
   fait dater et bâtir les 91 carrières au portage, puis construire leur
   relevé. Le pont gagne une lecture du droit,
   `releve.construire.lignes.citations` : de chaque ligne du relevé, son
   identifiant, sa fiche et sa version (`pont.py`, `pont.mjs`, et son jumeau
   dans `tests/outils_pont.py`). Les quatre comptes sont ceux du Python — 91
   relevés, 23 131 lignes, 782 qui citent leur fiche, 14 sa version — et
   `docs/etat.md` est identique à l'octet, fabriqué avant et après sur le
   même arbre. Mesuré à part : les 91 relevés du portage sont, ligne à ligne,
   ceux du Python, au zéro près que node écrit « 0 » et le Python « 0.0 ».
3. *La sonde*, `scripts/entrees_du_moteur.py`. Elle lance un script sous
   `sys.monitoring` et relève chaque appel qui entre dans le moteur Python du
   dehors — aucune fonction du moteur n'est alors en cours —, rangé sous le
   fichier qui appelle. Sans argument, elle passe chaque étape de la
   fabrique ; avec un script et ses arguments, ce script seul : les sessions
   du lot B y liront ce que leur étude appelle encore.
4. *La liste*, `ENTREES_DE_LA_FABRIQUE`, dans
   `tests/test_entrees_du_moteur.py`. Le test lance chaque étape de
   `regenerer.py` pour vérifier, sous la sonde, et exige l'égalité : une
   entrée de plus rougit, une entrée déclarée qui n'entre plus aussi. Une
   étape de plus dans `regenerer.py` doit s'y déclarer.

**Ce qui entre encore, au 12 novembre.**

Sept des onze étapes n'y entrent pas : l'inventaire, les régimes, les
témoins, les pages, le chiffrage, le tableau de bord et la conservation.
Quatre y entrent encore, par 28 appels.

| étape | qui appelle | ce qu'il appelle | où cela se défait |
|---|---|---|---|
| `construire_donnees.py` | lui-même | `moteur/age_reference._charger_ages` | un chargeur : sous `donnees/` au lot F |
| `mesures_accueil.py` | `scripts/solde_fusion.py` | `moteur/fusion.fusionner` | lot B, les études |
| `construire_tableaux_md.py` | `scripts/mesures_prose.py` | `carriere_simple`, `simuler` | lot A, ligne suivante |
| | lui-même | `EcartAge.anticipe`, `EcartAge.ecart`, lus sur ce que les sondes rendent | lot A, ligne suivante |
| `verifier_prose.py` | `scripts/mesures_prose.py` | `carriere_simple`, `simuler`, et seize règles appelées une à une : `salaire_de_reference`, `AgeReference.age`, trois de `ConstructeurCapitalisation` et deux de `Capitalisation`, `ConstructeurCompte.parts_retraite_seule`, trois de `Convertisseur`, `fusionner` et `_taux_total`, deux d'`Indexation`, `ScenarioNotionnel._garantie_vieillesse` | lot A, ligne suivante |
| | `scripts/mortalite_population.py` | `simuler` | lot B |
| | `castypes.py` | `pilote.age_de_depart`, `carriere_simple`, `conversion.niveau_relatif` | lot A, ligne suivante : une sonde bâtit un cas type en Python |

Deux écarts avec l'inventaire du 9 novembre, qui ne lisait pas l'accueil à
part : `mesures_accueil.py` entre par `solde_fusion.py`, et la prose par
`mortalite_population.py`, deux études que l'inventaire rangeait hors de la
fabrique. Elles en sont, par les mesures qui les appellent.

**Ce que la sonde compte, et ce qu'elle ne voit pas.** Une entrée est l'appel
d'une règle : toute fonction d'un fichier qui ne porte que des règles
(`droit/`, `moteur/`, `scenarios/notionnel.py`, `echeancier.py`, `pilote.py`,
`journal.py`), et, dans les six fichiers qui mêlent règles, chargeurs et types
(`simulateur.py`, `scenarios/actuel.py`, `carriere.py`, `chronologie.py`,
`remuneration.py`, `revalorisation.py`), les portes nommées par lesquelles
une carrière se bâtit, se liquide ou se simule (`PORTES`). Charger les
données par `Simulateur()` n'en est pas une. Trois angles morts, écrits en
tête du script :

- une règle d'un fichier mêlé qui n'est pas une porte, appelée directement —
  l'inventaire en nomme dans les sondes de la prose (`RemunerationActif`,
  `FicheDePaie`, `ActuelAujourdhui.pension_annuelle`) ; la session qui porte
  ces sondes ajoute la porte avant de retirer l'appel, pour voir la liste
  décroître ;
- ce qu'un calcul gardé par la mémoire des calculs appelle (`memoire.memoriser` :
  le coût, ses variantes, le coût des avantages) : le relevé changerait avec
  l'état de la mémoire, et le coût est tenu par ses propres tests
  (`tests/test_pont.py`, « sans les jumeaux ») ;
- ce qu'un script fait calculer à un autre processus.

**Ce qui reste, hors de cette étape.**

- Les deux exemples du README (`sortie_exemple`, `sortie_sncf`) : ils
  demandent leur comparaison aux sondes de la prose
  (`mesures_prose._comparaison_de`), qui bâtissent et simulent en Python, et
  l'écrivent par `Comparaison.tableau()`, une mise en forme qui n'existe
  qu'en Python. C'est la ligne suivante du lot A. Elle rencontrera une
  question que cette étape n'a pas tranchée : le § 3 du README montre un
  appel du simulateur Python et sa sortie ; quand ce simulateur part, soit le
  bloc montre autre chose, soit `tableau()` se récrit sur le résultat que le
  pont rend.
- `mesures_accueil.py` et les sondes de la prose : la ligne suivante.

**Une décision laissée au propriétaire.** Le test de la liste refait tourner
chaque étape de la fabrique. Mesuré sur ce conteneur : le fichier de tests
prend 155 s sur quatre cœurs, la mémoire des calculs pleine ; la régénération
entière lancée pour vérifier, en série et la mémoire vide au départ, 406 s
(le paquet 189 s, l'accueil 95 s, la prose 76 s, les témoins 34 s). Le
fichier est rangé au niveau « contrôle », que GitHub lance, hors de la suite
rapide. Si ce temps pèse trop sur la course de GitHub, deux issues : ne
garder sous le test que les quatre étapes qui entrent encore, ou faire écrire
le relevé par la régénération elle-même, que GitHub lance déjà — ce qui
touche `tests.yml`, une garde.

**Ce qui est vérifié, ce qui ne l'est pas.** Vérifié en faisant tourner : les
fichiers fabriqués identiques à l'octet (`construire_tableaux_md.py
--verifier`, `tableau_de_bord.py` avant et après) ; les cumuls et les écarts
au bit près ; les relevés ligne à ligne ; le test de la liste vu rouge sur
les deux scripts avant leur passage, vert après ; le test de la lecture du
pont vu rouge avant elle, et son jumeau Python qui la refait ; le test du
calcul gardé, vu rouge sans la règle qu'il tient ; la liste identique,
mémoire des calculs pleine ou vide, pour le paquet, l'accueil et la prose.
Non vérifié : le relevé
d'une étape qui s'arrêterait avant la fin parce que son fichier est périmé —
les étapes lancées pour vérifier calculent tout avant de comparer, lu dans
les deux scripts de cette étape seulement. Une différence connue : le portage
écarte aussi une case dont aucun régime n'est actif sur la période, que le
tableau de bord comptait en Python ; aucune des 91 cases n'est dans ce cas.

**Ce qui ne change pas.** Aucune règle du moteur, aucune règle du scénario 1,
aucune donnée, aucun fichier fabriqué, aucune garde. Aucun code du moteur
Python n'est retiré. Le bloc « Reprise » de l'action n'est pas récrit : la
session d'orchestration le tient.

**Tests.** `python -m pytest -m rapide` ; `tests/test_entrees_du_moteur.py`,
`tests/test_pont.py`, `tests/test_niveaux.py`, `tests/test_arbre.py` ; les
tests de la prose qui lancent les deux scripts ; la prose vérifiée.
