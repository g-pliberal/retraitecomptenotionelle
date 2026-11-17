# Les constantes au portage : le premier lot de la suppression des règles Python

Action 161, premier des quatre lots de
`2026-11-17-l-essai-a-blanc-de-la-suppression.md`, mené le 17 novembre 2026.
Aucune règle, aucune donnée, aucune valeur attendue ne change ; aucun fichier
de règles n'est encore supprimé.

## Fait

- **Les constantes que seuls les fichiers de règles tenaient** se lisent au
  portage, par `pont.constante_du_droit`, qui les déclare
  (`CONSTANTES_DE_LA_FACADE`) : la minoration de l'âge du minimum garanti
  (décret n° 2010-1744, article 3), la table d'anticipation de la
  convention du 14 mars 1947, le plancher de l'Ircantec (0,43), la maturité
  maximale de la courbe de la BCE (30 ans), le nom de la fiche de la
  majoration exceptionnelle de 2023 et celui de la règle des régimes
  spéciaux. Le portage rend désormais une table de valeurs simples (un
  `Map` ou un objet) en objet, que le pont relit en dictionnaire, ses clés
  numériques en entiers ; `liquider.js` exporte les trois constantes du
  droit, `pont.mjs` sert `capitalisation.MATURITE_MAXIMALE`. Les sept tests
  qui les importaient des règles les lisent ainsi.
- **`EligibleAgricole`** loge sous `types_du_pont/droit.py`, que
  `droit/liquider.py` réimporte ; `pont.OBJETS_DU_RESULTAT` le lit là.
- **`scripts/mesures_prose.py`** bâtit sa carrière nue
  (`types_du_pont.carriere.Carriere`) avec la chronologie que la classe des
  règles lui posait : `chronologie.completer(chronologie.du_resume(…))`, ce
  que `droit/preparer.py` fait. L'écart à OpenFisca reste le même au bit
  près (2,524773561672 % au plus, 0,123689720619 % au moins).

## Ce qu'il a fallu voir

- La carrière nue sans chronologie ne passe pas le pont : le portage la
  complète sans la table des présomptions (`présomption inconnue :
  jour_de_naissance`). La façade (troisième lot), dont la `Carriere` hérite
  encore de la classe des règles, rencontrera la même chose.
- `test_agirc_arrco_au_droit.py` lit les constantes de `liquider.js` dans
  la source : il accepte désormais une constante exportée.

## Ce qui reste

Les lots 2 à 4 de la note de l'essai à blanc. Il ne reste que cinq fichiers
qui importent des règles (`IMPORTEURS_DES_REGLES`) : `tests/facade.py`,
`tests/outils_pont.py`, `tests/jumeau_des_avantages.py`, `test_facade.py`,
`test_facade_jumeau.py`.

**Tests.** Deux tests neufs, vus rouges avant le lot :
`test_les_tables_et_les_noms_du_droit_se_lisent_au_portage`
(`test_facade.py`) et
`test_le_pont_ne_lit_aucun_type_par_son_nom_dans_un_fichier_de_regles`
(`test_fichiers_sur_le_moteur_python.py`), avec la liste des importeurs
raccourcie de huit ; la confrontation des constantes à leur jumeau les
compare toutes. `python -m pytest -m rapide` : 5 705 réussis ; les
confrontations légères, la façade et les jumeaux : 970 réussis.
