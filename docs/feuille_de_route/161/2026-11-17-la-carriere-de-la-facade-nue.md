# La carrière de la façade, nue : la façade des tests n'importe plus aucun fichier de règles

Action 161, suite du troisième lot de la suppression
(`2026-11-17-la-facade-sans-les-modules-de-regles.md`), menée le
17 novembre 2026. Aucune règle, aucune donnée, aucune valeur attendue ne
change ; aucun fichier de règles n'est encore supprimé.

## Fait

- **`facade.Carriere` hérite de la carrière nue**
  (`types_du_pont.carriere.Carriere`), et non plus de la classe des règles.
  Bâtie à la main, elle reçoit dans `__post_init__` la chronologie de ses
  champs, complétée des présomptions (`chronologie.completer(
  chronologie.du_resume(…))`), ce que faisait la classe des règles par
  `droit.preparer`, qui n'appelle que `completer`. `tests/facade.py` quitte
  `IMPORTEURS_DES_REGLES`.
- **Le relevé.** Essai fait la façade déjà nue : sous `-m rapide`, 120 tests
  cassaient sans la chronologie, 30 avec. Les 30 lisaient neuf lectures de
  la classe des règles : `part_retenue_ligne` (par
  `contributions_equilibre.py`), `part_retenue`, `part_cotisee_ligne`,
  `trimestres_retenus`, `qualite_agricole`, `annee_de_cessation_agricole`,
  `arretee_au_deces`, `date_entree`, `naissances_des_enfants`. Hors
  `-m rapide`, la suite complète (3 512 tests, 29 minutes) n'en montre
  qu'une de plus : `test_web_saisie.py`, déjà rouge sur `main` pour la même
  raison, réparé à part et publié d'abord.
- **Chaque lecture passe par une aide de la façade servie au portage**
  (`facade.date_entree`, `fait`, `parts_retenues`, `trimestres_retenus`,
  `qualites_agricoles`, `annee_de_cessation_agricole`, `arretee_au_deces`),
  et deux entrées neuves au pont : `carriere.parts_cotisees`
  (`partCotiseeLigne`) et `contributions.d_une_carriere`
  (`contributionsDUneCarriere` de `contributions-equilibre.js`, rendu en
  paires année, montant). `test_contributions_equilibre.py` éprouve donc le
  portage ; `contributions_d_une_carriere` du Python, que plus rien ne lit,
  est déclaré `au_moteur` dans `scripts/jumeaux_gardees.yaml` et part avec
  la suppression.

## Ce qui reste

1. **`test_facade.py`** et `test_facade_jumeau.py` confrontent encore des
   types et des constantes à ceux des modules de règles : ces
   confrontations partent avec la suppression, comme
   `jumeau_des_avantages.py`.
2. **La suppression**, telle que la décrit
   `2026-11-17-l-essai-a-blanc-de-la-suppression.md` : le quatrième lot.

**Tests.** `test_la_facade_ne_charge_aucun_fichier_de_regles` (plus aucun
import des règles, la carrière nue pour seul parent) et
`test_hors_des_regles_un_type_ou_une_constante_s_importe_de_son_module`,
vus rouges sur l'ancienne façade, verts après ; les 20 tests qui appellent
les deux entrées neuves, vus rouges avant elles. `python -m pytest -m rapide` :
5 709 réussis ; la suite hors `-m rapide` : 3 511 réussis, l'échec restant
réparé et publié avant.
