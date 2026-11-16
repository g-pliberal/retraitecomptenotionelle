# Les tables du droit sous `donnees/` : les chargeurs de `scenarios/actuel.py` relogés tels quels

Action 161, étape 3 de l'inventaire
(`2026-11-16-l-inventaire-du-retrait-des-regles.md`), sur le choix du
propriétaire du 16 novembre 2026 : reloger tels quels, sans attendre la
décision qui remplacera la note 0009. Aucune donnée, aucune règle n'a bougé.

- `donnees/tables_du_droit.py` (neuf) : les 43 classes de tables que
  `scenarios/actuel.py` gardait (âges, durées requises, décotes, surcotes,
  minima, majorations, réversions, conversions et valeurs du point…), leurs
  deux aides (`_rang_mois`, `_age_ou_rien`) et leurs six constantes, sans un
  caractère changé dans leur corps. Il n'importe aucun module de règles.
  `scenarios/actuel.py` les reprend par import (650 lignes au lieu de 3 704),
  et ne garde que `ScenarioActuel` et ce qui bâtit son résultat.
- Deux dépendances aux règles levées pour cela : `date_d_effet`, que
  `CarriereLongue` lisait à `droit/commun.py`, loge à `calendrier.py`, que
  `droit/commun.py` reprend ; `DEBUT_REGLE_GENERALE_PUBLIC` se lit à
  `revalorisation_servie.py`, d'où le prenait déjà `revalorisation.py`.
- Les lecteurs hors des règles les prennent à leur place :
  `scripts/construire_donnees.py` et `avantages.py` (qui ne garde de
  `scenarios/actuel.py` que `ScenarioActuel`).
- Les 115 fiches qui citaient une de ces tables sous `scenarios/actuel.py`
  la citent sous `donnees/tables_du_droit.py` (`code.python`, que l'étape 5
  retirera) ; l'architecture, § « Ce qui reste en Python » et la table des
  fichiers, aussi.

**Vérifié.** Le paquet refait par `construire_donnees.py`
(`moteur/donnees.json` et les `data/derive/*.json`) : identique à l'octet
avant et après, fiches comprises. Les témoins, que le portage calcule sur ce
paquet, ne bougent donc pas.

**Reste de l'étape 3.** Deux chargeurs logés ailleurs dans les règles :
`moteur/age_reference._charger_ages` et `carriere.Affiliations`. Et
`CarriereLongue` porte encore des méthodes de règle (`age_de_depart`,
`cotises_reputes`, `age_propose`…) : reloger tel quel les a emportées avec
la table ; elles partiront avec les règles ou à la réécriture selon la
décision qui suivra la note 0009.

**Tests.** `tests/test_chargeurs_a_part.py`, trois de plus (rapides) : les
tables s'importent sans un module du moteur Python ; `scenarios/actuel.py`
reprend les mêmes objets et n'en définit plus aucune ; la fabrique et le
coût des avantages ne les prennent plus aux règles. Vus rouges, puis verts.
`test_fichiers_sur_le_moteur_python.py` : `AgesOuverture`, devenu chargeur,
n'y fait plus entrer ; `ScenarioActuel` sert d'exemple de classe du moteur.
`python -m pytest -m rapide` (5 679), `test_carte.py`, `test_avantages.py`,
`test_types_du_pont.py`, les confrontations légères : verts.
