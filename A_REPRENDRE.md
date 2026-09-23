# Branche age-legal-65 : à reprendre

Brouillon à reprendre depuis une session cloud. Le détail complet est dans l'action 124 de `docs/feuille_de_route.md`.

## Ce que fait la branche
- L'âge légal de la proposition (scénario 6) passe à 65 ans dès 2026 (`Parametres.age_legal_liberal`) : la carrière est prolongée jusqu'à cet âge (`Carriere.prolongee`, `Simulateur.carriere_proposition`), dans les deux moteurs.
- `age_reference_fixe` passe de 64 à 65 ans.
- Page Coût : un volet par cohorte (`Pensionne.volet`) et une assiette élargie (`facteur_assiette`).
- Le scénario 1 (le droit en vigueur) n'est pas touché.
- Corrections faites en chemin : le taux de remplacement net de la proposition, « le 4 est le 3 », une divergence de la cascade entre `gabarit.js` et le Python, le libellé « 64 ans (défaut) », et la phrase du README sur le portage.

## État
- Rebasée sur `main` à `daac51c`, TVA à taux unique de 21,1 % comprise (action 123).
- Avant ce dernier rebasage, la suite complète était verte : 2 342 tests Python, 29/29 en JS.
- Après la fusion avec la TVA, les fichiers fabriqués sont régénérés.

## Reste à faire
1. **1 test JS échoue**, `tests/js/moteur.test.js:124` : une page n'est pas rendue à l'identique par les deux moteurs. Les 10 017 premiers caractères coïncident, la divergence est plus loin, probablement sur l'accueil (TVA et âge légal).
2. **Remesurer `MESURES_BLOCAGES`** (`pages.py` et `pages.js`) avec la TVA et l'âge légal réunis. Mesures faites sur la branche : solde moyen du scénario 6 à **+1,07** point de PIB (+0,55 sans âge légal), aucune année en déficit, dette 2070 à **−69 %** (des réserves, −31 % sans âge légal), coefficient au plus bas 1,05 en 2048, 1,28 en 2070. Les tests `test_solde_fusion.py`, `test_stock_age_legal.py` et `test_proposition_prospective.py` recalculent chaque valeur.
3. **Réécrire la prose qui parle des années de déficit.** Le README et l'accueil disent qu'il manque quelques millièmes au pic de 2044-2045 ; avec l'âge légal, ce n'est plus vrai. Il faut aussi redire ce que change l'âge légal maintenant que la TVA existe, puis lancer `python scripts/verifier_prose.py --corriger`.
4. **À arbitrer par l'utilisateur** : la TVA à 21,1 % a été calibrée pour couvrir le déficit du scénario 6 SANS âge légal. Avec 65 ans, un taux plus bas suffirait.
5. Mettre à jour les chiffres de l'action 124 de la feuille de route, qui sont d'avant la TVA.
6. Lancer la suite complète, puis intégrer sur `main` selon `CLAUDE.md` (rebasage, puis `scripts/pousser.sh`).
