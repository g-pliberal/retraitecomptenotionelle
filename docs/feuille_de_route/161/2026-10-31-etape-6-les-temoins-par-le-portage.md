# Étape 6 : les témoins par le portage — la demande au pont, la table des types, et les zéros ambigus soumis au propriétaire

**La demande.** Le 31 octobre 2026, le propriétaire ouvre l'étape suivante
de l'action 161, les témoins de simulations calculés par le JavaScript, sous
une condition : préparer tout ce qui ne change aucun octet de
`tests/temoins/simulations.json`, puis s'arrêter et lui demander, avant la
moindre réécriture d'un zéro. Ni `construire_temoins.py` branché sur le
portage, ni le moteur Python touché.

**Ce qui est fait.**

1. *La demande au pont* : `simulations`, dans `pont.mjs` et `pont.py`. Chaque
   requête d'un témoin, lue par `Saisie.depuisRequete` et simulée par
   `Contexte.simuler`, comme `tests/js/moteur.test.js` la simule : le
   `dictionnaire()` entier et les appels de `liquider`, liquidations d'essai
   comprises. `_fini` est reproduit sans code de plus : `JSON.stringify` écrit
   NaN et les infinis `null`, comme lui.
2. *La table des types*, dans `pont.py`, déclarée champ par champ depuis le
   code, puis confrontée aux 913 témoins : 16 champs entiers, que le moteur
   Python calcule en `int` (années, mois, trimestres, comptes d'années,
   version) ; 105 flottants ; 5 dictionnaires à clés libres (le capital par
   régime, la pension et le coefficient d'aujourd'hui de chaque scénario, et
   deux comptes d'années par origine) ; 3 champs flottants dont le zéro ne
   s'écrit qu'entier. Un nombre sous un champ qu'elle ne déclare pas arrête la
   relecture (`resultat_des_donnees`) au lieu d'en deviner le type, et un
   entier qui n'en est pas un aussi.
3. *Quatre tests* (`tests/test_pont.py`), vus rouges avant le code : la table
   relit chaque témoin écrit comme node l'écrirait, sans node, en suite
   rapide ; elle refuse ce qu'elle ne déclare pas ; le pont simule des
   témoins de chaque forme ; et, en suite complète (un quart de minute), les
   913 témoins simulés par le portage, relus par la table et écrits comme
   `construire_temoins.py` les écrit, redonnent le fichier ligne pour ligne,
   sauf aux zéros ambigus, tout nombre égal en valeur. Trois mutations de la
   table rougissent le premier : un champ privé de son zéro entier, un champ
   retiré, un entier déclaré flottant.

**Le recompte.** 913 témoins, 171 732 nombres : 153 672 flottants, dont
43 114 de valeur entière, et 18 060 entiers ; aucun « -0.0 ». Sur 627 chemins
de champs, 14 mêlent entiers et flottants, tous pour la même raison :
`somme_ordonnee`, comme `sum`, part de l'entier 0, et la somme d'une liste
vide rend « 0 », celle de flottants nuls « 0.0 », comme un 0.0 écrit tel
quel ailleurs. Dans 3 champs, aucun témoin n'écrit 0.0 : les intérêts du
pilier capitalisé (470 zéros), la majoration pour enfants d'aujourd'hui (439),
le montant des droits acquis après le départ (17) ; la table garde leur zéro
entier. Dans les 11 autres, le même champ vaut tantôt « 0 », tantôt « 0.0 » :
ce sont les zéros ambigus, 2 103 dans 825 témoins, que node seul ne peut pas
départager.

| Champ | Zéros « 0 » |
|---|---:|
| `scenarios.actuel.pension_hors_repartition` | 720 |
| `scenarios.notionnel_liberal.capitalisation.versements` | 461 |
| `scenarios.notionnel_liberal.capitalisation.frais_preleves` | 461 |
| `aujourd_hui.actuel.pension_hors_repartition` | 414 |
| `scenarios.notionnel_liberal.capitalisation.capital` | 9 |
| `scenarios.notionnel_liberal.capitalisation.capital_hors_frais` | 9 |
| `scenarios.notionnel_liberal.capitalisation.cout_des_frais` | 9 |
| `scenarios.notionnel_prospectif.cotisations_employeur` | 5 |
| `scenarios.notionnel_prospectif.cotisations_versees` | 5 |
| `scenarios.notionnel_prospectif_employeur.cotisations_employeur` | 5 |
| `scenarios.notionnel_prospectif_employeur.cotisations_versees` | 5 |

**Les durées**, mesurées dans le conteneur de la session. `construire_temoins.py` prend
77,6 secondes : 47,3 pour les simulations au moteur Python, dont 5,3 pour les
carrières que le portage bâtit, et 32,3 pour les pages, que node rend déjà.
Par le portage, les simulations prennent 12,9 secondes, relecture comprise :
le script tomberait vers 43 secondes. L'ordre des témoins n'y change rien :
ceux de `_cas()` et ceux du fichier rendent les mêmes appels de `liquider`.

**Ce que la normalisation déplacerait**, essayée dans un arbre de travail
jetable, sans rien commiter : `construire_temoins.py` y passe le résultat du
moteur Python par la table, et le fichier qu'il écrit est, à l'octet, celui
que le portage relu par la table écrit. Le diff tient en 2 103 lignes de
`simulations.json`, chacune « 0 » devenu « 0.0 », 4 206 octets de plus ;
`pages.json` ne bouge pas. `python scripts/regenerer.py --verifier` y dit
toutes ses étapes à jour, en 572 secondes, du paquet à la conservation : le
tableau de bord ne lit du fichier que les appels de `liquider`, et la prose
que son nombre de témoins. La concordance de `tests/js/moteur.test.js`, au
bit près, passe sur le fichier normalisé : « 0 » et « 0.0 » y sont le même
nombre.

**Ce qui attend le propriétaire.** La normalisation proposée, en deux
commits : le premier fait écrire à `construire_temoins.py` le résultat du
moteur Python sous la table (`pont.resultat_des_donnees`), et récrit les
2 103 zéros « 0.0 », aucune valeur ne changeant ; le second simule les
témoins par le portage, sans changer un octet, et confronte le moteur Python
au fichier par la même table, tant qu'il reste. Une variante : les 3 champs
au zéro entier passent aussi en flottants, 926 zéros de plus, et la table n'a
plus que deux sortes de nombres. L'autre voie, écrire « 0 » tous les zéros de
ces 14 champs, récrirait 2 805 « 0.0 » et mettrait des entiers dans des
champs flottants ; corriger les sommes du moteur Python toucherait le moteur,
ce que l'étape s'interdit.

**Ce qui ne change pas.** Aucun octet des témoins ni des agrégats ; aucune
garde, aucune règle du scénario 1, donc pas d'entrée au journal de veille ;
aucune dépendance. Sans node, la demande s'arrête (`pont.PontIndisponible`).

**Tests.** `python -m pytest -m rapide` ; `tests/test_pont.py` en entier ;
`tests/test_web.py::test_le_portage_javascript_retrouve_les_chiffres_du_modele`,
`tests/test_niveaux.py`, `tests/test_jumeaux.py` ;
`node --test tests/js/moteur.test.js`, 46 essais.
