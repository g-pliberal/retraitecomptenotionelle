# Les derniers chargeurs sous `donnees/` : les âges légaux, le routage des statuts, et la table de la carrière longue sans ses règles

Action 161, fin de l'étape 3 de l'inventaire
(`2026-11-16-l-inventaire-du-retrait-des-regles.md`), sur le choix du
propriétaire du 16 novembre 2026 : reloger tels quels. Aucune donnée, aucune
règle n'a changé de sens ; aucun résultat n'a bougé.

- **Les âges légaux.** `moteur/age_reference._charger_ages` devient
  `charger_ages`, sous `donnees/tables_du_droit.py`, corps inchangé. La
  fabrique du paquet le prend là, l'âge de référence du moteur Python le
  reprend de là. `tests/test_entrees_du_moteur.py` : la fabrique n'entre plus
  du tout dans le moteur Python (`construire_donnees.py` ne porte plus
  d'entrée).
- **Le routage des statuts.** `Affiliations`, avec `rang_borne` et
  `FAMILLES_STATUT`, passe de `carriere.py` à `donnees/affiliations.py`, que
  `carriere.py` reprend (les mêmes objets). Le simulateur de données, la
  fabrique du paquet et celle des témoins le prennent à sa place, sans
  importer `carriere.py`. Il passe **avec** sa date d'entrée
  (`Affiliations.date_entree`, le maintien d'une affiliation CRPCEN ou IEG) :
  je l'avais d'abord détachée en règle, mais la fiche de paie
  (`remuneration.py`) et les contributions d'équilibre
  (`contributions_equilibre.py`), hors des règles, la lisent ; elle route
  comme `Affiliations.regimes`, qui reste aussi au chargeur. La question de
  savoir si ces deux modules doivent la demander au pont relève de l'étape 4.
- **La table de la carrière longue.** `CarriereLongue` ne garde que son
  chargement, ses fiches, sa variante datée (`avant`) et `_annee_decimale`.
  Ses huit méthodes de règle (`_portes`, devenue `portes_opposables`,
  `de_la_fonction_publique`, `_requis`, `_entree_precoce`, `cotises_reputes`,
  `_reputes_assimiles`, `age_de_depart`, `age_propose`) et les neuf
  constantes du droit qu'elles lisent passent, telles quelles, en fonctions
  de `droit/carriere_longue.py`, qui prennent la table en premier argument.
  `droit/ouvrir.py` et `droit/departs.py` les appellent ainsi. Le coût des
  avantages, qui vide la table pour sa variante, n'a pas changé.
- **Trois tests passent au portage** au lieu d'exécuter le Python :
  `test_retour_crpcen_ieg.py` lit la date d'entrée au portage
  (`scenario_actuel.affiliations.date_entree`), `test_droits_contrefactuels.py`
  l'âge de la carrière longue (`carriere_longue.age_de_depart`). La façade
  sert ces deux méthodes de plus (`pont.TABLES_DE_LA_FACADE`, leurs contrats
  dans `tests/contrats_de_la_facade.py`). `test_facade_jumeau.py` confronte
  chacune au jumeau, au bit près, et, pour les règles détachées de leur
  table, appelle la fonction sur la table (`REGLES_DETACHEES`).
- **Les fiches.** Treize fiches citaient ces noms à leur ancienne place
  (`code.python`) : elles les citent à la nouvelle. L'architecture suit.

**Vérifié.** Le paquet refait par `construire_donnees.py`
(`moteur/donnees.json` et les `data/derive/*.json`) est identique à l'octet,
avant et après. Les témoins, que le portage calcule sur ce paquet, ne
bougent donc pas. La surcote de 2004 à 2006 n'est pas touchée.

**Tests.** `tests/test_chargeurs_a_part.py`, cinq de plus (rapides) : les
âges et le routage se lisent sans le moteur Python, les règles reprennent les
mêmes objets, la fabrique ne prend plus ses chargeurs aux règles, la table de
la carrière longue ne porte plus de règle. Vus rouges, puis verts.
`python -m pytest -m rapide` (5 686) ; `test_facade_jumeau.py`,
`test_facade.py`, `test_carte.py`, `test_retour_crpcen_ieg.py`,
`test_droits_contrefactuels.py`, l'oracle de la carrière longue des
fonctionnaires, `test_types_du_pont.py`, les contrats et la liste des
fichiers sur le moteur Python, les confrontations légères : verts.

**Reste.** L'étape 4 : le Python seul encore branché aux règles (section 4
de l'inventaire). Puis l'étape 5, les fiches, les ancres et les gardes. La
suppression des fichiers de règles, désormais 40 avec
`droit/carriere_longue.py`, attend l'accord du propriétaire.
