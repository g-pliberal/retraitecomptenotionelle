# Le Python seul débranché : les cas types, la mesure des avantages et la fiche de paie sans règle Python

Action 161, étape 4 de l'inventaire
(`2026-11-16-l-inventaire-du-retrait-des-regles.md`, section 4), menée la
nuit du 16 novembre 2026 sur la demande du propriétaire d'avancer sur ce qui
ne demande pas son avis. Aucune donnée, aucune règle n'a changé de sens ;
aucun résultat n'a bougé.

- **Les cas types** (`castypes.py`). `calculer_cas_types` et
  `carriere_de_la_grille`, qui simulaient la grille en Python et n'avaient
  plus d'appelant, sont retirés ; `CasType.niveau_relatif`, qui bâtissait la
  carrière au moteur Python, aussi, avec la surcharge de la grille large qui
  y renvoyait : aucun code ne l'appelait plus (la mortalité par niveau de vie
  lit le niveau au portage, `mortalite_population.niveau_relatif`).
  `CasType.age_liquidation_pour` demande l'âge au portage
  (`ages_de_la_grille`), comme la grille large le faisait déjà, et non plus
  au pilote Python. Les deux variantes de départ (`VARIANTES_LIQUIDATION`)
  passent du pilote aux cas types, que le pilote reprend. Le module ne
  charge plus `carriere.py`, `simulateur.py` ni `pilote.py`.
- **Le métier et les profils.** `Metier`, un dataclass sans méthode, et les
  noms `PROFIL_AUTOMATIQUE` et `PROFIL_SMIC` passent de `carriere.py` à
  `types_du_pont/carriere.py`, que `carriere.py` reprend (les mêmes objets).
  La grille large les prend là.
- **La mesure des avantages** (`avantages.py`). `recalculer`,
  `scenarios_neutralises`, `carriere_variante`, `_catalogue_sans`,
  `statuts_des_emplois` et `FICHES_RETIREES` liquidaient au scénario 1
  Python ; le coût des avantages ne les appelait plus (le portage bâtit les
  mêmes variantes, `scenariosNeutralises` de `pont.mjs`). Seuls des tests les
  appelaient : ils passent, tels quels, à `tests/jumeau_des_avantages.py`,
  qui partira avec les règles. `test_agregats.py` bâtit sa carrière par les
  options que le module garde (`_options_de_la_variante`), sans le jumeau.
- **Le salaire moyen** (`ancrage_salaire_moyen`, `indice_salaire_moyen`,
  `salaire_moyen_annuel`, `ANNEE_ANCRAGE_SALAIRE_MOYEN`) passe de
  `carriere.py` à `donnees/salaire_moyen.py`, que `carriere.py` reprend. La
  fiche de paie (`remuneration.py`) le lit là. Choix fait : la fiche de paie
  reste le jumeau Python de `remuneration.js`, hors du périmètre du retrait ;
  la faire demander le salaire moyen au pont l'aurait fait dépendre de son
  propre portage. Le salaire moyen n'est qu'une série de l'INSEE ancrée et
  cumulée, sans droit : il se range avec les chargeurs. La sonde des entrées
  du moteur (`scripts/entrees_du_moteur.py`) ne le compte donc plus comme
  porte.
- **La date d'entrée CRPCEN ou IEG** (`Affiliations.date_entree`) reste sous
  `donnees/affiliations.py`, avec le routage, sans passer par le pont. Elle
  route comme `Affiliations.regimes` ; la fiche de paie et les contributions
  d'équilibre, qui la lisent, ne chargent aucune règle.
- **Les fiches.** Quatre fiches citaient un nom déplacé dans `code.python`
  (`bonification_cinquieme_militaires`, `retraite_anticipee_handicap`,
  `micro_social_abattement`, `un_statut_par_annee`) : elles citent la
  nouvelle place, ou ne citent plus ce qui n'est plus au modèle.
  L'architecture nomme le salaire moyen et `Metier`.

**Ce qui reste de l'étape 4 : la carrière que le pont relit.**
`pont.carriere_des_donnees` bâtit encore la carrière sous la classe des
règles (`carriere.Carriere`), qui hérite de la carrière nue. Mesuré en la
relisant sous la carrière nue : 476 tests rapides échouent, dans 48
fichiers (92 dans `test_simulateur.py`, 33 dans
`test_coefficients_agirc_1947.py`, 29 dans `test_limite_age.py`…), parce
qu'ils lisent sur la carrière rendue des propriétés de règle
(`trimestres_actuels`, `date_entree`, `trimestres_retenus`, `prolongee`,
`pension_d_invalidite`…). Ces lectures doivent passer au portage, ou
partir avec les règles, avant la suppression : un travail de plusieurs
sessions, fichier de tests par fichier, que l'étape 5 n'attend pas.

**Vérifié.** Le paquet refait par `construire_donnees.py`
(`moteur/donnees.json` et les `data/derive/*.json`, agrégats compris) est
identique à l'octet. Les témoins, que le portage calcule sur ce paquet, ne
bougent donc pas. La surcote de 2004 à 2006 n'est pas touchée.

**Tests.** `tests/test_python_seul_debranche.py`, cinq tests (rapides) : le
coût, ses cas types et les avantages se chargent sans module de règles ;
aucun de ces modules ni la fiche de paie n'importe une règle, même tard ; le
code qui simulait en Python est parti ; le salaire moyen se lit sans le
moteur ; les règles reprennent les mêmes objets. Vus rouges, puis verts.
`test_types_du_pont.py` compte `Metier` ; `test_entrees_du_moteur.py` suit
la sonde. `python -m pytest -m rapide` : vert (5 692) ; `test_carte.py`,
`test_entrees_du_moteur.py`, `test_agregats.py` : verts.

**Reste.** L'étape 5, les fiches, les ancres et les gardes ; la carrière
relue par le pont ; puis la suppression des fichiers de règles, sur l'accord
du propriétaire.
