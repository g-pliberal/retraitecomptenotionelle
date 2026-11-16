# Les chargeurs sous `donnees/` : le barème de l'ASPA, les revalorisations et le nombre déclaré, lus sans le moteur Python

Action 161, première moitié du point 4 de « Ce qui reste » de
`2026-11-16-le-tri-des-scripts-et-des-modules.md`. Aucune règle, aucune
donnée, aucun témoin n'a bougé.

- `donnees/minimum_vieillesse.py` : `MinimumVieillesse` et `DeuxEtages`,
  déplacés tels quels de `scenarios/actuel.py`, qui les reprend par import.
- `donnees/revalorisations.py` : `Revalorisation`, `produit` et
  `RevalorisationsPensions`, déplacés de `revalorisation.py`, qui les reprend.
- `noyau/budget.py` : `APPELS_DECLARES`, le nombre déclaré d'appels de
  `liquider` (§ 7.8). Ce n'est pas un chargeur : il va au noyau, qui reste en
  Python, plutôt que sous `donnees/`. `droit/liquidation.py` le reprend.

Les lecteurs hors des règles les prennent à leur nouvelle place : `cout.py`,
`effet_retour.py`, `scripts/construire_donnees.py`,
`scripts/tableau_de_bord.py`. Les fiches `minimum_vieillesse`,
`revalorisation_des_pensions` et `pension_differee_fonction_publique` disent
le nouveau fichier ; l'architecture, § 7.8, aussi.

**Vérifié.** Le paquet du site refait par `construire_donnees.py` (le
`moteur/donnees.json` et les `data/derive/*.json`) : identique à l'octet
avant et après. Les barèmes de l'ASPA de 1935 à 2080, les deux étages, les
revalorisations et le maximum des cultes : même empreinte.

**Reste du point 4.** `Simulateur.univers_de_la_demande`, puis un simulateur
de données seules, que la façade des tests prend aussi. Ensuite, hors du
point 4 mais sur le même chemin : `construire_donnees.py` lit encore une
vingtaine de chargeurs logés dans `scenarios/actuel.py` (`ConversionsPoints`,
`MinimumGaranti`, `MaximumDesCultes`, les durées requises, les décotes…).
Ce sont des données, mais leur place touche à la refonte des fichiers du
droit (note de décision 0009, en cours ailleurs) : à ne pas anticiper.

**Tests.** `tests/test_chargeurs_a_part.py` (5, rapide) : chaque chargeur
s'importe sans un module du moteur Python, les règles reprennent les mêmes
objets, et le coût, l'effet retour et les deux scripts ne les prennent plus
aux règles ; vus rouges, puis verts. `test_carte.py` a demandé les fiches.
`python -m pytest -m rapide`, `test_revalorisation.py`, `test_effet_retour.py` :
verts.
