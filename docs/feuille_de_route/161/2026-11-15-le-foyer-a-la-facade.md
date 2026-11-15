# Le foyer à la façade : l'étape « foyer et net » et le plafond du couple servis par le portage, deux tests de l'ASPA y passent

Douzième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-la-liquidation-a-la-facade.md`, « Ce qui reste », 1 : le foyer.
Aucune règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

**L'étape entière.** `foyer.foyer_et_net` entre dans
`pont.REGLES_DE_LA_FACADE`, sous un module `foyer` que le pont tient
(`MODULES_DU_DROIT` de `pont.mjs`) et que la façade expose
(`facade.foyer`). Le portage rend son `Foyer`, que la façade lit sous le type
du Python : ses méthodes (`servie_avec`, `avantage`, `donnees`) se lisent sur
ce qu'il a calculé. La carrière passe telle quelle, conjoint compris. Le
contexte d'une liquidation, objet du moteur Python, est refusé : un appel qui
le passe reste sur le moteur Python.

**La table.** `minimum_vieillesse.plafond_couple` entre dans
`pont.TABLES_DE_LA_FACADE`.

**`test_liquidation.py`.** Les deux tests de l'ASPA, celui du couple et celui
des deux étages d'avant 2007, passent à la façade, inchangés hors de leur
marque. Il en garde 11 marqués sur 22 (`RESTES`).

## Ce qui est mesuré

**Contre le jumeau.** Six appels de l'étape (seul, en couple, deux
allocataires, 1990, 1970, âge non atteint) et deux du plafond du couple,
confrontés au jumeau sous la référence et sous les conventions du COR, au bit
près. Une seule différence de type : le jumeau rend l'entier `0` pour les
pensions étrangères d'une carrière qui n'en a pas (une somme vide), que la
façade lit `0.0`, le type que le champ annonce ; la confrontation des objets
du droit compare la valeur de ces champs-là.

**Les tests.** Trois tests neufs dans `tests/test_facade.py`, vus rouges ;
`-m rapide`, `test_facade.py`, `test_facade_jumeau.py`, `test_liquidation.py`,
`test_droit.py`, `test_reversion.py`, `test_pont.py`,
`test_fichiers_sur_le_moteur_python.py` : verts.

## Ce qui reste

1. Le troisième test du foyer, « chaque étape suit son schéma », appelle aussi
   `ouvrir.ouvrir`, `liquider.liquider_chaque_regime` et
   `completer.completer`, et passe un contexte de liquidation : il passe avec
   les étapes seules, la tranche suivante, qui devra transmettre le contexte
   (ses neutralisations) aux quatre étapes.
2. Puis le reste de « Ce qui reste » de
   `2026-11-15-la-liquidation-a-la-facade.md`.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
