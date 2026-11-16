# Les types du pont hors des règles : 45 types sortis des fichiers de règles Python

Action 161, étape 1 du plan de `2026-11-16-l-inventaire-du-retrait-des-regles.md`.
Aucune règle n'a changé : le paquet et les témoins refaits sont identiques à
l'octet, la suite rapide et les tests de la zone sont verts.

## Ce qui a bougé

Un paquet neuf, `src/retraite_notionnelle/types_du_pont/`, loge les types sous
lesquels le pont relit ce que calcule le moteur JavaScript. Ses six modules ne
chargent aucun fichier de règles :

- `carriere.py` : `AnneeCarriere` ;
- `droit.py` : les types du droit (pensions, avantages, compléments, cumul,
  départs, foyer, liquidation, réversion, seconde liquidation), avec les
  constantes que leurs méthodes lisent (statuts du cumul et leur ordre,
  barèmes du foyer et leurs libellés, `OUVERTE`, la version du schéma du foyer
  et de la réversion) et `jour` ;
- `journal.py` : `Evenement`, `Entree`, `Journal` ;
- `moteur.py` : écart d'âge, capitalisation (avec `_taux_interne`), compte
  notionnel, conversion, fusion, indexation ;
- `revalorisation.py` : les sept types de la revalorisation ;
- `resultats.py` : `ResultatActuel`, `ResultatNotionnel`, `GarantieVieillesse`
  et les types de leurs champs.

Ce sont les 19 types que le pont relit, hors `Carriere` et `Comparaison`, et
les 26 types que leurs champs portent : la lecture stricte du pont descend
dans chaque champ (`typing.get_type_hints`), et un type laissé dans un fichier
de règles l'y ramènerait. L'inventaire comptait 22 types ; la liste qu'il
donne en nomme 21.

Les fichiers de règles réimportent chaque nom parti, le temps du retrait :
`from ..types_du_pont.droit import Foyer  # noqa: F401`, et leur
`SCHEMA_VERSION` renvoie à la constante du type. Le pont importe désormais du
nouveau paquet, ses contenus du journal (`CONTENUS_DU_JOURNAL`) compris. Les
18 fiches dont le champ `code.python` nommait un type parti le nomment sous
`types_du_pont/` : `tests/test_carte.py` confronte ce champ au dépôt, et le
retrait du champ, que le propriétaire a choisi, vient à l'étape 5.

## Ce qui reste dans les types

Les méthodes parties avec les types ne font que lire leurs champs : sommes,
douzièmes, `donnees()`, la lecture du journal (`Journal.servi`). Deux restent
à trancher :

- `Foyer.servie_avec` dit le barème de l'ASPA d'une personne seule. Son jumeau
  JavaScript, `servieAvec` de `moteur/js/droit/foyer.js`, est aussi une méthode
  du type, et `tests/test_facade.py` et `tests/test_liquidation.py` l'appellent
  sur le foyer que le pont rend : la sortir du type demanderait que la façade
  la serve. Elle est restée ; l'étape 2, où la façade porte ses contrats, la
  règle.
- `DemandeExaminee.donnees` passait par `Depart(...).date_effet`, une classe du
  droit : elle écrit la même date par `jour`, le premier du mois.

## Ce qui n'a pas bougé

`Carriere` et `Comparaison` restent dans `carriere.py` et `simulateur.py`.
`Carriere` porte quelque soixante-dix méthodes de règle (durées, trimestres,
statuts, `prolongee`, les constructeurs `depuis_*`), et `Comparaison` porte une
`Carriere` dans ses champs. Les séparer est une étape à elle, à mener avant la
suppression : le type nu sous `types_du_pont/carriere.py`, ses règles en
fonctions des fichiers de règles, et les appelants Python qui les lisent comme
des méthodes.

## Tests

`tests/test_types_du_pont.py`, vu rouge avant le déplacement (48 échecs) :
chaque type relu loge sous `types_du_pont`, et reste le même objet sous son
ancien module ; le paquet, chargé seul dans un processus neuf, ne charge aucun
fichier de règles ; le pont relit le journal sous ses types. Suite rapide :
5 469 réussis. Zone : `test_pont`, `test_facade`, `test_facade_jumeau`,
`test_jumeaux`, la sonde, les confrontations légères, 878 réussis.
`python scripts/construire_donnees.py` et `construire_temoins.py` ne changent
aucun fichier.

## En passant

La suite était rouge sur `main` depuis l'action 175 :
`tests/test_droit.py::test_chaque_etape_ecrit_ce_que_le_temoin_fige` ne
trouvait pas 115 sorties de `comparer-droit.mjs` au témoin. `FIGER_SORTIES=1`
les y a ajoutées, sans changer ni retirer aucune des 838 autres, dans un commit
à part.
