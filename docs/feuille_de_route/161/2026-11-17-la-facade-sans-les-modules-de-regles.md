# La façade sans les modules de règles : le troisième lot de la suppression, sauf la carrière

Action 161, troisième des quatre lots que décrit
`2026-11-17-l-essai-a-blanc-de-la-suppression.md`, mené le 17 novembre 2026.
Aucune règle, aucune donnée, aucune valeur attendue ne change ; aucun
fichier de règles n'est encore supprimé.

## Fait

`tests/facade.py` n'importe plus qu'un fichier de règles, `carriere.py`,
pour la classe dont sa `Carriere` hérite (voir « Ce qui reste ») :

- **Les modules du droit sans jumeau.** `Regles` et `_Module` ne lisent plus
  rien sur le module Python : une règle servie se demande au portage
  (`pont.REGLES_DE_LA_FACADE`), une constante s'y lit
  (`pont.CONSTANTES_DE_LA_FACADE`, lue une fois par processus), le reste
  manque (`AttributeError`), comme à un module. Une règle non servie n'est
  donc plus refusée (`NonTransmissible`) mais absente : sans jumeau, la
  façade ne sait plus qu'elle existe.
- **91 constantes de plus au portage.** Les tests lisaient sur les modules
  de règles 86 noms (fiches, statuts, motifs, versions de `categories`,
  `completer`, `compter`, `cumul`, `departs`, `limite_age`, `liquider`,
  `progressive`, `releve`, `seconde`), relevés par l'arbre syntaxique des
  tests, plus cinq que `test_emploi_retraite.py` lit par `getattr`. Le
  portage les exporte tous sous le même nom, à la même valeur (vérifié un à
  un, et tenu par
  `test_chaque_constante_du_droit_lue_au_portage_est_celle_du_jumeau`), sauf
  `limite_age.FICHES`, ajouté à `limite_age.js`. `pont.mjs` sert `seconde`,
  et une liste de valeurs simples, que `pont.constante_du_droit` rend en
  tuple. `liquidation.APPELS_DECLARES` vient de `noyau.budget`,
  `NEUTRALISATIONS` de `types_du_pont`.
- **Trois types logés sous `types_du_pont/droit.py`** : `Contexte` et `Etat`
  (de `droit/liquidation.py`), `PensionServie` (de `droit/departs.py`), et
  `NEUTRALISATIONS` ; les fichiers de règles les réimportent, le même objet.
- **Plus de test marqué.** `JUMEAUX`, la marque `sur_le_moteur_python` (et
  son inscription dans `conftest.py`) et la fixture `entrees_du_test` sont
  partis ; `simulateur_du_test` rend toujours le simulateur de la façade.

## Ce qu'il a fallu voir

Une sonde à l'exécution (un greffon pytest jetable qui note ce que la façade
lit encore sur les jumeaux) était trop lente sur les 136 fichiers : deux
heures. Le relevé statique des attributs lus sur les objets de la façade l'a
remplacée, et les tests ont dit le reste.

La `Carriere` de la façade ne peut pas encore hériter de la carrière nue.
Essayé : sa chronologie se pose comme dans `scripts/mesures_prose.py`
(`chronologie.completer(chronologie.du_resume(…))`), et `depuis_lignes`
s'ajoute sans calcul ; mais une carrière bâtie à la main dans un test reste
lue en Python par les méthodes de la classe des règles. Sous
`-m rapide`, 19 tests cassent : `test_contributions_equilibre.py` (10, par
`contributions_equilibre.py`, un module hors des règles qui appelle
`carriere.part_retenue_ligne`), `test_fiche_date_d_entree.py` (8,
`carriere.date_entree`) et `test_chronologie.py` (1,
`naissances_des_enfants`). La suite complète en montrera sans doute
d'autres.

## Ce qui reste

1. **La carrière de la façade, nue.** Recenser, sur la suite complète, les
   méthodes de la classe des règles lues sur une carrière bâtie à la main ;
   passer chacune par une aide de la façade servie au portage
   (`facade.date_entree`, `facade.parts_retenues` existent) ;
   `contributions_equilibre.py` doit lire la part retenue autrement, ou
   partir avec la suppression s'il n'est plus qu'un jumeau. Puis `Carriere`
   hérite de la carrière nue, et `tests/facade.py` quitte
   `IMPORTEURS_DES_REGLES`.
2. **`test_facade.py`** compare encore des types et des constantes à ceux
   des modules de règles (`*_python`) : ces confrontations partent avec la
   suppression.
3. **La suppression**, telle que la décrit la note de l'essai à blanc.

**Tests.** `test_la_facade_ne_charge_aucun_fichier_de_regles` et
`test_les_noms_du_droit_que_lisaient_les_tests_se_lisent_au_portage`, vus
rouges avant le changement (la façade importait 26 modules de règles ; les
noms n'étaient pas déclarés au pont), verts après ; les refus de règle non
servie de `test_facade.py` attendent `AttributeError`.
`python -m pytest -m rapide` : 5 709 réussis ; les 26 fichiers qui lisent
les constantes ou le simulateur du test : 1 114 réussis ; `-m site` : 38.
