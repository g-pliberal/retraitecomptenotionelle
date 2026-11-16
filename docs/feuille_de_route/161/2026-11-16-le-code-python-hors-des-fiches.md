# Le code Python hors des fiches : les fiches du droit ne nomment plus que le moteur JavaScript

Action 161, étape 5 de l'inventaire
(`2026-11-16-l-inventaire-du-retrait-des-regles.md`, section 5), menée la
nuit du 16 novembre 2026, sur le choix du propriétaire (« On applique tes
recommandations ») : le champ `code.python` des fiches se retire, avec la
confrontation que `tests/test_carte.py` en faisait. Aucune donnée, aucune
règle, aucun résultat n'a bougé : les fiches n'entrent pas dans le paquet.

- **Les fiches.** 240 des 267 fiches de `data/reference/regles/` portaient
  une clause `python` ; elle est ôtée, ligne à ligne, et chaque fiche relue
  par YAML est celle d'avant moins cette clause. Toutes gardent leur clause
  `javascript`, que la note de décision 0009 et son rectificatif font la liste
  des fonctions de la règle : aucune n'en manquait.
- **La confrontation** (`tests/outils_carte.py`). Elle ne lit plus que le
  moteur JavaScript, et refuse une clause `python`, quoi qu'elle nomme
  (`test_le_code_d_une_fiche_ne_nomme_plus_le_python`, vu rouge d'abord).
  Le contrat de la fiche (`data/reference/contrats/fiche.yaml`) dit « les
  fonctions du moteur JavaScript » ; l'exemple de fiche de
  `docs/architecture.md` perd sa clause Python.
- **Un test devenu faux par l'étape 4.**
  `test_le_cout_atteint_le_simulateur_que_le_site_charge_aussi`
  (`tests/test_jumeaux.py`), hors des tests rapides, échouait déjà avant
  cette étape : le coût et la fabrique n'atteignent plus le simulateur
  Python, ce que l'étape 4 cherchait. Il dit désormais ce fait.

**Ce qui reste de l'étape 5.** Les neuf fiches de la proposition
(`data/reference/regles/proposition/`) nomment encore, par leur module, le
Python du modèle notionnel, que `tests/test_univers.py` importe : elles
relèvent du même choix, mais leur test charge les modules, et passe à la
session suivante. Puis les 22 chiffres ancrés qui chargent un module de
règles, les chargements par chemin et les gardes des jumeaux.

**Tests.** `python -m pytest -m rapide` : 5 693 passés. Les 37 fichiers de
tests qui lisent les fiches ou la carte : verts, hors le test du simulateur
corrigé ci-dessus, vert ensuite.
