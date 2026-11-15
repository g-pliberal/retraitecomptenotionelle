# Le code mort du portage retiré : 31 fonctions et 3 constantes que rien n'atteint

Le portage JavaScript perd 31 fonctions et 3 constantes que ni le site, ni
le pont, ni la fabrique, ni un test n'atteignent : 249 lignes de moins, dans
18 fichiers de `moteur/js/`. Aucun comportement ne change, aucun test non
plus.

**La consigne.** La note de décision 0008 et sa lecture
(`2026-11-13-les-decisions-du-proprietaire.md`) : le code mort du portage
retiré en une session, hors les six fonctions réservées, selon la
recommandation de `2026-11-12-le-code-mort.md`, « Une session de retrait ».

**Ce qui part.** Chaque candidat de la mesure du 12 novembre a été recherché
de nouveau sur l'état du jour, par son nom dans tout le dépôt, par son nom de
propriété (`.nom`, `"nom"`) dans le portage, les lanceurs (`pont.mjs`,
`web/site.mjs`), les essais de `tests/js/` et les chaînes du Python, et
contre les méthodes que la façade des tests déclare
(`pont.TABLES_DE_LA_FACADE`).

- *Vingt et une sans lecteur d'aucun côté* : `SoldeFige.observees`,
  `DetteFigee.cumulInterets` (`agregats.js`) ; `presomptionsEmployees`
  (`chronologie.js`) ; `sommeDesParts` (`distribution.js`) ; `ressourceEec`,
  `anneesTransferts` (`equilibre.js`) ; `textePdf` (`lecture-pdf.js`) ;
  `LoiMortalite.force`, `utiliseTablesReelles` (`mortalite.js`) ;
  `partRepriseBascule` (`pages.js`) ; `classements`, `enRepartition`,
  `resoudreSuccession`, `aUneConvention`, `couvertureMilitaires`
  (`regimes.js`) ; `cotisationsPatronales`, `tauxRetraite`, `ecartBrutNet`,
  `ficheDePaiePossible` (`remuneration.js`) ; `tauxRemplacementProspectif`
  (`simulateur.js`) ; `forwardContinu` (`taux.js`).
- *Dix que seul le Python lit* : `DepensesRetraite.prestation`,
  `TrancheComplementaire.part_au_dessus`, `LoiMortalite.esperance`,
  `esperancePubliee`, `anneeNiveauxDeVie` (et le champ qu'il rendait),
  `tauxCsgPension`, `DureesServicesMilitaires.categories`,
  `CatalogueRegimes.ouverts`, `AssietteTva.recette` et `tauxMoyen`. Le jour où
  un script qui lit leur jumeau Python passera au pont, il les demandera ; ce
  sont des lectures d'une ligne.
- *Trois constantes sans lecteur* : `PERIODES_NON_COTISEES` (`carriere.js`),
  `FICHES_DES_PRIMES` (`droit/primes.js`), `ASSIETTES` (`primes.js`).
- Trois commentaires de documentation orphelins, restés au-dessus d'une
  fonction retirée plus tôt (`equilibre.js`, deux ; `pages.js`, un), et trois
  commentaires qui nommaient une fonction retirée, récrits sans son nom.

**Ce qui reste, et pourquoi.**

- *Trois des vingt-quatre « sans lecteur » ont pris un lecteur depuis le
  12 novembre*, ou en gardent un : `impotDUnRevenuImposable`, que
  `tests/test_relecture_zone_grise.py` éprouve désormais ; `Journal.etatAu`,
  qu'un essai de `tests/js/journal.test.js` lit ; `droitRegimeSpecial`, que
  le champ `code` de `regles/priorite_majorations_enfants.yaml` nomme, et qui
  se rebranche avec la fiche au retrait du moteur Python.
- *Les six fonctions réservées* : `Convertisseur.effetAnticipation`, que le
  pont sert déjà aux sondes de la prose ; `Comparaison.renteCapitalisee`,
  `FicheDePaie.cotisationsSalariales`, `classeDe`, `Indexation.historique`
  et `tauxReel`.
- *Les neuf fonctions et les neuf constantes que seuls des tests atteignent*,
  et les 98 nommées jamais exécutées : laissées aux étapes des tests, comme
  la note du 12 novembre le recommande.
- *Les cinq jumeaux Python que rien ne nomme* dans les 24 paires qui restent
  des deux côtés : non retirés ici, l'étape portant sur le portage ; ils
  partent avec la liste des fonctions gardées des deux côtés.

**Ce qui est vérifié.** Chaque module touché se charge sous node.
`python -m pytest -m "rapide or site"` : 5 117 verts, 64 sautés. Les 172
essais de `tests/js/` sont verts. Les fichiers de tests des modules touchés
(agrégats, chronologie, équilibre, frontière, lecture des PDF, mortalité,
primes, rémunération, TVA, zone grise, données, site, jumeaux, moteur à
part) : 742 verts. Le paquet n'est pas touché : le champ
`annee_niveaux_de_vie` y reste, que la fabrique écrit et que le Python lit.
Les pages, les témoins et la suite complète sont à GitHub.

**L'étape suivante.** Les autres règles de `droit/` à la façade des tests,
puis les autres fichiers de tests : `2026-11-13-les-regles-du-droit-a-la-facade.md`,
« Ce qui reste ».
