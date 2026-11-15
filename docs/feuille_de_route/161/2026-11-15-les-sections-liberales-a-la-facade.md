# Les sections libérales à la façade : les trimestres des enfants, le taux de leur majoration et la valeur de service servis par le portage

Vingt et unième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-les-referents-a-la-facade.md`, « Ce qui reste », 1 :
`test_sections_liberales.py`. Aucune règle, aucune donnée, aucun témoin n'a
bougé. La suite complète de GitHub était verte sur `dc1ede0` ; celle de
`e4919b8` tournait au commit.

## Ce qui est fait

**Deux règles** entrent dans `pont.REGLES_DE_LA_FACADE` :
`compter.majoration_pour_enfants`, les trimestres des enfants et le régime
qui les porte (R. 173-15), son dictionnaire des trimestres par régime passé
en table (`TABLES_DES_REGLES`), le module `compter` du portage ouvert à la
règle (`MODULES_DU_DROIT` de `pont.mjs`) ; et
`completer._taux_majoration_enfants`, que `completer.js` exporte désormais
sous `tauxMajorationEnfants`, comme `_cumuler`, pour la façade seule.

**Un régime du catalogue passe le pont**, par sa marque
(`pont.RegimeDuCatalogue`, `{"@": "regime", code}`), que le portage prend dans
son catalogue. La façade le reconnaît au catalogue d'un de ses simulateurs
(`_simulateur_du_regime`, que `commun.periode_de_liquidation` partage), dont
la règle prend alors les paramètres ; un régime d'un autre catalogue, ou sous
d'autres paramètres que le moteur, est refusé.

**Une table** : `valeurs_point.service` entre dans
`pont.TABLES_DE_LA_FACADE`.

**`test_sections_liberales.py` passe entier à la façade** : ses 97 cas, sans
test marqué ; il quitte `FICHIERS` et n'entre pas dans `RESTES`. Ses imports
seuls changent ; `noyau.carte`, la carte des règles, reste en Python (note de
décision 0006) et ne fait pas entrer dans le moteur. Les fonctions qu'en
empruntent d'autres fichiers : aucune (`test_sections_sante.py` ne le cite
qu'en prose).

## Ce qui est mesuré

Deux tests neufs dans `tests/test_facade.py`, vus rouges : les seize
trimestres de la mère de deux enfants à la CNAVPL (L. 643-1-1), rien aux
mines, 10 % à trois enfants à la Cipav, rien à deux, 15 % à quatre dans la
fonction publique (L. 18 du code des pensions), le refus d'un régime d'un
autre catalogue ; la valeur de service de la CNAVPL en 2026, 0,6599 €. Six
appels de règle et trois de table confrontés au jumeau
(`tests/test_facade_jumeau.py`). `-m rapide`, `test_sections_liberales.py`,
`test_facade.py`, `test_facade_jumeau.py -k "regle or table"`, `test_pont.py`
et `test_fichiers_sur_le_moteur_python.py` : verts.

## Ce qui reste

1. `test_temps_partiel.py` (`releve`, `chronologie`), `test_oracle.py`
   (l'échéancier, `departs`, `invalidite`, des tables du scénario).
2. « Faire vivre » servi ouvre la voie aux fichiers qui l'appellent :
   `test_departs.py`, `test_invalidite.py`, `test_pension_maximale.py`,
   `test_majoration_*`, `test_pension_minimum_avant_1983.py`, et le test
   marqué de `test_liquidation.py`.
3. Les 37 tests marqués de `test_simulateur.py`.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance ; `test_facade_jumeau.py` en entier.
