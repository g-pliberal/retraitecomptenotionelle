# Les règles de `completer` à la façade : cinq règles du minimum contributif servies par le portage, quatre tests de plus l'éprouvent

Première tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-13-les-regles-du-droit-a-la-facade.md`, « Ce qui reste », 1.
`tests/test_simulateur.py` importe `completer` de la façade ; quatre fonctions
de test quittent la marque `sur_le_moteur_python` : il en reste 62 dans ce
fichier, contre 66. Aucune règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

**Cinq règles déclarées** (`pont.REGLES_DE_LA_FACADE["completer"]`) :
`borne_avec_les_droits_d_avant_1973`, `complement_minimum`,
`majoration_ouverte`, `plancher_du_regime`, `selon_la_regle`. Le pont charge
`droit/completer.js` parmi les modules du droit (`MODULES_DU_DROIT` de
`pont.mjs`).

**Deux sortes d'arguments de plus.** La façade transmet désormais :

- *la règle d'une fiche*, un dictionnaire de valeurs simples sous des noms
  (`{"majoration": "periodes_cotisees", "seuil_trimestres_cotises": 120}`),
  que le portage lit en objet. Un dictionnaire dont une clé n'est pas un texte
  ou une valeur n'est pas simple reste refusé : le portage le lirait en `Map`
  ou ne le lirait pas ;
- *un éligible au minimum* (`liquider.EligibleMinimum`), que le pont écrit
  sous les noms en chameau que le portage lui donne, et relit de même
  (`pont.TYPES_DE_LA_FACADE`, ajouté à `CLASSES_EN_CHAMEAU`).

**Une annotation.** `completer.selon_la_regle` du jumeau annonce ce qu'elle
rend, `liquider.EligibleMinimum` : la façade lit ce que rend le portage sous
ce type. Le code de la règle ne change pas.

**Quatre tests démarqués** : la surcote ajoutée au minimum (circulaire Cnav
2018-04), les huit exemples des circulaires de 2005 et 2009, la majoration de
2004 sans distinction des périodes cotisées, la borne des droits d'avant 1973.
Le dernier bâtit son éligible par `EligibleMinimum`, un type, importé du
moteur Python, et non plus par `liquider.EligibleMinimum`, que la façade
refuse. Ce que chacun attend est inchangé.

## Ce qui est mesuré

| `test_simulateur.py` | avant | après |
|---|---:|---:|
| fonctions de test marquées | 66 | 62 |

**Contre le jumeau.** Treize appels de plus dans `tests/test_facade_jumeau.py`,
deux au moins par règle, sous les réglages de référence et les conventions du
COR : la même valeur au bit près ; un éligible rendu se compare champ à champ.

**Les tests.** Deux tests neufs dans `tests/test_facade.py`, vus rouges avant
le code (la façade n'avait pas de `completer`) : l'éligible et la règle d'une
fiche passent et reviennent ; un dictionnaire qui ne passe pas est refusé.
La signature de chacune des cinq règles est vérifiée contre le portage par le
test qui le fait pour les vingt autres.

## Ce qui reste

1. `releve.construire` (9 fonctions de test) : chacune compare déjà le
   jumeau au portage, par node. Ce que la règle rend — le relevé et ses
   durées — ne passe pas le pont ; la voie la plus courte est sans doute de
   garder la moitié JavaScript de chaque test, et de demander à la façade la
   valeur que la moitié Python lit (`duree_du_regime_aligne` sur ces durées),
   ce qui veut une règle composée. À instruire avant d'écrire.
2. `completer.avpf_retenue` et `commun.ligne_cotisee`, que lit le test de
   l'AVPF de septembre 2023 : `ligne_cotisee` reçoit une ligne de la
   carrière, que la façade ne transmet pas.
3. Les règles dont un argument est un dictionnaire que le portage lit en
   `Map` (`repartir_les_annees`, les points de chef).
4. `liquider.maximum_des_pensions` et `reversion.mois_de_mariage`
   (`test_reversion.py`) : le premier lit aussi deux méthodes de la table des
   réversions que la façade ne sert pas, le second se heurte au nom
   `reversion`, que la façade donne déjà à l'entrée de la réversion.
5. Puis les autres fichiers de tests, et les règles du simulateur.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
