# Les indépendants à la façade : la valeur de service datée servie, le plafond propre du RCI retiré par les données

Action 161, quatrième vague, après `2026-11-15-la-capitalisation-au-portage.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé. `test_independants.py`
quitte `FICHIERS`.

## Ce qui est fait

- **`test_independants.py`** importe `Carriere`, `ConstructeurCompte`,
  `Simulateur`, `acquerir`, `compter` et `coordonner` de la façade ; les
  affiliations se lisent sur le simulateur (`Simulateur().affiliations`), au
  lieu du chargeur Python ou du moteur.
- **`valeurs_point.service_au`**, la valeur de service en vigueur au 1er d'un
  mois, entre dans `pont.TABLES_DE_LA_FACADE` : la minoration de l'article 3
  lit la valeur de l'ORGANIC d'avant 1973 au départ de janvier 1995.
  Confrontée au jumeau (`test_facade_jumeau.py`) sur trois appels, dont les
  deux valeurs de l'Agirc-Arrco de 2022, avant et après le relèvement de
  novembre.
- **Le plafond propre du RCI** : le test qui le comparait au plafond de la
  Sécurité sociale remplaçait `PeriodeRegime.bornes_de_l_annee` sous
  `monkeypatch`, ce que le portage ne voit pas. Il bâtit désormais un
  simulateur sur une copie des données où la fiche du RCI ne porte plus ses
  `borne_*_par_annee` (`facade.donnees_retouchees`) : la même comparaison,
  servie par le portage.

## Ce qui reste de la vague 4

`test_emploi_retraite.py`, `test_moteur.py`, `test_pont.py` ; puis, après le
coût, `test_cout.py` et `test_grille_large.py`.

**Tests.** `python -m pytest -m rapide` : 5 417 passés, 64 sautés ;
`test_independants.py` (55), `test_fichiers_sur_le_moteur_python.py`, les
confrontations des tables de `test_facade_jumeau.py` : verts.
