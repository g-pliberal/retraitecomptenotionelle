# L'AVPF à la façade : une ligne de carrière passe au portage par son rang, et deux règles de plus sont servies

Troisième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-le-releve-a-la-facade.md`, « Ce qui reste », 1. Le test de
l'AVPF de septembre 2023 (`tests/test_simulateur.py`) quitte la marque
`sur_le_moteur_python` : il en reste 53 dans ce fichier, contre 54. Aucune
règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

**Deux règles de plus** : `commun.ligne_cotisee` et
`completer.avpf_retenue` rejoignent `pont.REGLES_DE_LA_FACADE` (vingt-huit
règles servies). Le module `commun` entre dans `MODULES_DU_DROIT` de
`pont.mjs`, et la façade le sert sous le nom de son jumeau (`facade.commun`).

**Une ligne passe par son rang.** `ligne_cotisee` reçoit une ligne de la
carrière. La façade la cherche, par identité, dans les lignes de la carrière
que la règle reçoit, et la transmet par son rang (`pont.LigneDeCarriere`) ;
le portage la relit dans sa propre copie de cette carrière (`ligne`,
`argumentDuDroit`), qui garde les lignes dans le même ordre
(`carriereDesDonnees`). Une ligne d'une autre carrière, ou une ligne
retouchée (`dataclasses.replace`), est refusée (`NonTransmissible`).

## Ce qui est mesuré

| `test_simulateur.py` | avant | après |
|---|---:|---:|
| fonctions de test marquées | 54 | 53 |

**Contre le jumeau.** `tests/test_facade_jumeau.py` confronte quatre appels
de plus, sous les réglages de référence et les conventions du COR : la ligne
d'emploi de 1984 et la ligne d'éducation de 1990 d'une mère née en 1962, et
l'AVPF retenue sous un plafond de 24 et de 0.

**Les tests.** Deux tests neufs dans `tests/test_facade.py`, vus rouges avant
le code (la façade n'avait pas de `commun`) : la mère sous l'AVPF de 1985 à
2002, son année 1984 cotisée, son année 1990 non, 24 trimestres d'AVPF
retenus (L. 351-10, D. 351-2-2), aucun sous un plafond nul ; et les lignes
refusées. `-m rapide`, `test_facade.py`, `test_facade_jumeau.py`,
`test_oracle.py`, `test_fichiers_sur_le_moteur_python.py` et le test de
l'AVPF : verts.

## Ce qui reste

1. Les règles dont un argument est un dictionnaire que le portage lit en
   `Map` (`repartir_les_annees`, les points de chef).
2. `liquider.maximum_des_pensions` et `reversion.mois_de_mariage`
   (`test_reversion.py`) : le premier lit aussi deux méthodes de la table des
   réversions que la façade ne sert pas, le second se heurte au nom
   `reversion`, que la façade donne déjà à l'entrée de la réversion.
3. Les cotisations du relevé (`droits.cotisations`) et le constructeur du
   compte, pour le test de l'exercice 1952 et ses voisins marqués
   `Simulateur.constructeur_employeur`.
4. Puis les autres fichiers de tests qui lisent le relevé
   (`test_droit.py`, `test_liquidation.py`, `test_cultes.py`,
   `test_bonifications_emplois.py`…), et les règles du simulateur.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
