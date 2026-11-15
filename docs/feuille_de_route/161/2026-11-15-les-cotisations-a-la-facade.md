# Les cotisations à la façade : les cotisations du relevé et deux méthodes du constructeur du compte servies par le portage

Sixième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-la-reversion-a-la-facade.md`, « Ce qui reste », 1. Dix fonctions
de test de `tests/test_simulateur.py` quittent la marque
`sur_le_moteur_python` : l'exercice 1952 et les neuf marquées
`Simulateur.constructeur_employeur`. Il en reste 39 dans ce fichier, contre
49. Aucune règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

**Les cotisations du relevé.** `releve.construire` rend aussi
`droits.cotisations`, `(code, annee, montant)`, dans l'ordre
(`releveEnDonnees` de `pont.mjs`, `pont.releve_des_donnees`).

**Le constructeur du compte.** La façade sert `cotisation_annuelle` et
`taux_effectif` de `simulateur.constructeur` et de
`simulateur.constructeur_employeur` (`pont.CONSTRUCTEURS_DE_LA_FACADE`,
`pont.constructeur_du_compte`, entrée `simulateur.constructeur` de
`pont.mjs`). Leurs arguments passent comme ceux d'une méthode de table : une
carrière, une période du catalogue par son rang ; ce qu'elles rendent revient
sous le type du jumeau (`CotisationAnnuelle`, le quadruplet du taux).
`table_du_moteur` et la nouvelle fonction partagent `pont._methode_servie`.

**Ce qui est refusé** : une autre méthode (`construire`), un autre
constructeur (`constructeur_liberal`, `constructeur_prelevement`), une
retouche, un appel sous un modèle modifié.

## Ce qui est mesuré

| `test_simulateur.py` | avant | après |
|---|---:|---:|
| fonctions de test marquées | 49 | 39 |

**Contre le jumeau.** `tests/test_facade_jumeau.py` confronte sept appels de
constructeur (un salarié, deux activités la même année, une fonctionnaire,
un artisan de 1970, l'État civil et militaire), sous le défaut et sous
`ContributionEtat.ENTIERE`, et les cotisations des trois relevés déjà
confrontés : au bit près.

**Les tests.** Quatre tests neufs dans `tests/test_facade.py`, vus rouges
avant le code : les cotisations de 1952 et 1953 du chef d'exploitation,
4,25 € et 8,50 € (décret n° 52-1166, article 45) ; la même cotisation par les
deux constructeurs ; 44,1 % pour un civil de l'État en 2025 (Cour des
comptes, tableau n° 15) ; ce qui est refusé. `-m rapide`, `test_facade.py`,
`test_facade_jumeau.py`, `test_simulateur.py`, `test_pont.py`,
`test_oracle.py`, `test_fichiers_sur_le_moteur_python.py` : verts.

## Ce qui reste

1. `Simulateur.constructeur_prelevement` et `construire` du constructeur
   (un compte entier, `test_le_prelevement_du_droit_en_vigueur…`), et
   `Simulateur.regime_fusionne` : le compte rendu en données demande ses
   types.
2. Les quatre tests marqués de `test_reversion.py` (note précédente,
   « Ce qui reste », 2).
3. Puis les autres fichiers de tests qui lisent le relevé
   (`test_droit.py`, `test_liquidation.py`, `test_cultes.py`,
   `test_bonifications_emplois.py`…), et les règles du simulateur ;
   `completer.points_rco_de_chef`.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
