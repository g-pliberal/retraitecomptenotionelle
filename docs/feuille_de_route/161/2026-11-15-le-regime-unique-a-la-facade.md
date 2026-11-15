# Le régime unique à la façade : `Simulateur.regime_fusionne` servi par le portage, et reçu par le compte

Huitième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-le-compte-entier-a-la-facade.md`, « Ce qui reste », 1. Une
fonction de test de `tests/test_simulateur.py` quitte la marque
`sur_le_moteur_python` : `test_le_regime_unique_herite…`. Il en reste 37
dans ce fichier, contre 38. Aucune règle, aucune donnée, aucun témoin n'a
bougé.

## Ce qui est fait

**Le régime unique.** Une dixième entrée de la façade,
`simulateur.regime_fusionne`, rend le `regimeFusionne` du simulateur du
portage, lu strictement sous `RegimeFusionne` (`pont.LECTURES_DE_LA_FACADE`,
`ENTREES_DE_LA_FACADE` de `pont.mjs`). Le simulateur de la façade le garde :
le même objet à chaque lecture.

**Reçu par le compte.** `construire` reçoit ce régime-là, et lui seul : il
passe au portage par une marque (`pont.REGIME_FUSIONNE`,
`{"@": "regime_fusionne"}`), que `argumentDeLaFacade` remplace par le
régime du simulateur, et refuse ailleurs qu'à un simulateur. Un autre
`RegimeFusionne`, retouché par le test, est refusé (`NonTransmissible`).

## Ce qui est mesuré

| `test_simulateur.py` | avant | après |
|---|---:|---:|
| fonctions de test marquées | 38 | 37 |

**Contre le jumeau.** Le régime unique, sous la bascule de référence (2026)
et sous une bascule en 2035, et deux comptes entiers de plus, une
fonctionnaire liquidée en 2039 sous le régime unique, par le constructeur et
par celui de l'employeur, sous le défaut et sous `ContributionEtat.ENTIERE` :
au bit près.

**Les tests.** Deux tests neufs dans `tests/test_facade.py`, vus rouges
avant le code : le régime unique à la bascule de 2026, sur une assiette
déplafonnée (`_taux_total` de `fusion.py`), la fonction publique de l'État
parmi ce qu'il fusionne ; le compte d'une fonctionnaire au taux du régime
unique en 2030, pas en 2020. `-m rapide`, `test_facade.py`,
`test_facade_jumeau.py`, `test_simulateur.py`, `test_pont.py`,
`test_oracle.py`, `test_fichiers_sur_le_moteur_python.py` : verts.

## Ce qui reste

1. Les quatre tests marqués de `test_reversion.py`
   (`2026-11-15-la-reversion-a-la-facade.md`, « Ce qui reste », 2).
2. Puis les autres fichiers de tests qui lisent le relevé
   (`test_droit.py`, `test_liquidation.py`, `test_cultes.py`,
   `test_bonifications_emplois.py`…), et les règles du simulateur ;
   `completer.points_rco_de_chef`.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
