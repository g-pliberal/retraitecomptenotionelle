# Le compte entier à la façade : `construire` et le constructeur du prélèvement servis par le portage

Septième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-les-cotisations-a-la-facade.md`, « Ce qui reste », 1. Une
fonction de test de `tests/test_simulateur.py` quitte la marque
`sur_le_moteur_python` : `test_le_prelevement_du_droit_en_vigueur…`. Il en
reste 38 dans ce fichier, contre 39. Aucune règle, aucune donnée, aucun
témoin n'a bougé.

## Ce qui est fait

**Le compte entier.** La façade sert `construire` des constructeurs du
compte : le `CompteNotionnel` du portage revient sous le type du jumeau, ses
`CotisationAnnuelle` comprises. Il suffisait de le déclarer
(`pont.CONSTRUCTEURS_DE_LA_FACADE`) : `telQuel` et `lu_strictement` savaient
déjà le transmettre. `regime_fusionne`, l'argument, ne passe que nul.

**Le constructeur du prélèvement.** `simulateur.constructeur_prelevement`
sert les trois méthodes. Sous `ContributionEtat.ENTIERE`, la façade rend
le constructeur des scénarios 4 et 5, comme `constructeurPrelevement` de
`moteur/js/simulateur.js` : c'est la façade, non le portage, qui dit cette
identité. Un constructeur est gardé par simulateur, le même à chaque lecture.

## Ce qui est mesuré

| `test_simulateur.py` | avant | après |
|---|---:|---:|
| fonctions de test marquées | 39 | 38 |

**Contre le jumeau.** Sept appels de plus dans
`tests/test_facade_jumeau.py` (quatre comptes entiers, dont un ouvert en
1975, et les trois méthodes du prélèvement), sous le défaut et sous
`ContributionEtat.ENTIERE` : au bit près.

**Les tests.** Deux tests neufs dans `tests/test_facade.py`, vus rouges
avant le code : le compte du chef d'exploitation de 1952 à 1972, 4,25 € puis
8,50 € (décret n° 52-1166, article 45) ; 78,28 % prélevés sur un civil de
l'État en 2025, la série des taux appelés. `-m rapide`, `test_facade.py`,
`test_facade_jumeau.py`, `test_simulateur.py`, `test_pont.py`,
`test_oracle.py`, `test_fichiers_sur_le_moteur_python.py` : verts.

## Ce qui reste

1. `Simulateur.regime_fusionne` (`test_le_regime_unique_herite…`) : un
   type de données à servir, et le seul `regime_fusionne` que `construire`
   recevrait.
2. Les quatre tests marqués de `test_reversion.py`
   (`2026-11-15-la-reversion-a-la-facade.md`, « Ce qui reste », 2).
3. Puis les autres fichiers de tests qui lisent le relevé
   (`test_droit.py`, `test_liquidation.py`, `test_cultes.py`,
   `test_bonifications_emplois.py`…), et les règles du simulateur ;
   `completer.points_rco_de_chef`.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
