# Étape 6 : le JavaScript fait foi — la décision du propriétaire vérifiée, la concordance au bit près, et ce qui reste avant qu'une règle ne s'écrive qu'une fois

**La demande.** Le 31 octobre 2026, le propriétaire tranche les points en
attente de l'action 161, par un plan qu'il a reçu d'un autre assistant et
qu'il demande de vérifier avant de l'appliquer : « Prends des pincettes,
vérifie toutes les consignes et utilise une méthode prudente. Je ne veux pas
que mon travail soit perdu à cause de mauvais choix. » Trois points : le
JavaScript fait foi dès maintenant, et aucune règle ne s'écrit plus en Python
« lorsqu'elle est déjà couverte par le pont » ; les deux paires de données
tranchées, puis le coût, la datation des cas types et les confrontations
branchés sur le pont ; le retrait par sous-ensemble cohérent. Pour cette
session : l'étape la plus directe vers le passage complet du coût et des
confrontations par le pont, et la bascule des consignes de `src/` et de
`moteur/`. La priorité, redite : rien de cassé, les témoins et les agrégats
identiques à l'octet, à tout instant.

**Ce que la vérification trouve, point par point.**

1. *Le JavaScript qui fait foi* : sûr, à une condition, que son jumeau Python
   le suive dans le même commit. Les deux moteurs calculent la même chose : sur
   les 913 témoins, 171 732 nombres, aucun écart au bit près, mesuré par un
   essai de node hors du dépôt — depuis `libm.js` (étape 5, deuxième partie).
   Mais `tests/js/moteur.test.js` tolérait 1e-9 : un Python porté dans un autre
   ordre d'addition serait passé.
2. *Plus aucune règle en Python* : impossible aujourd'hui sans casser. Les
   témoins se simulent au moteur Python (`construire_temoins.py`,
   `simulateurs[parametres].simuler(carriere)`), et le portage leur est
   confronté. Le coût ne fait simuler par le portage que sa grille
   (`cout._simulations`, `_par_le_portage`), et pas sous
   `memoire.modele_modifie()`, `monkeypatch`, `scripts/solde_fusion.py` ni
   des données copiées ; il bâtit et date ses carrières en Python
   (`_carrieres_du_cout`, `castypes.carriere_de_la_grille`,
   `pilote.age_de_depart`, qui interroge `droit/ouvrir.py`), puis
   `test_agregats.py` et `test_cout.py` exigent les deux moteurs identiques
   sur la grille. Les exemples officiels (`test_oracle.py`, 2 399 lignes)
   éprouvent les fonctions du moteur Python. Chaque paire du moteur est
   atteinte par le coût et par 94 à 173 fichiers de tests. Une règle écrite
   en JavaScript seul rougirait `main` à son premier envoi ; une suite
   desserrée laisserait le coût sous l'ancienne règle. La condition du
   propriétaire, « déjà couverte par le pont », ne tient pour aucune paire du
   moteur.
3. *Les deux paires de données* : revérifiées ce jour. La fabrique n'importe
   de `donnees/agregats.py` que ses écrivains, `figer_*`
   (`construire_donnees.py`, `_agregats`), et de `credits_ministeres.py` que
   le chargeur (`_credits_ministeres` : `annee`, `fiabilite`, `parts()`) ;
   les lecteurs de la table et les trois calculs des crédits ne servent qu'aux
   tests (`test_agregats.py`, `test_bilan_compte.py`, `test_web.py` ;
   `test_sre_jaune_ministeres.py`, `test_web.py`). La décision se lit ainsi :
   le Python garde chargeur et écrivains, le portage seul les calculs et les
   accesseurs. Son exécution est une étape à elle.
4. *Les témoins par le pont* (`construire_temoins.py`) : les nombres sont les
   mêmes, mais pas l'écriture. Des 171 732 nombres, 43 114 sont des flottants
   entiers, que le Python écrit « 2.0 » et node « 2 » : sans une table des
   types, les témoins changeraient d'octets.
5. *Le retrait par sous-ensemble cohérent* : une règle de méthode, que la
   note 0005 écrit avec ses conditions. Elle ne lève pas le blocage : le coût
   et les tests atteignent encore chaque paire.
6. *Les gardes* : aucune n'a eu à changer — ni les workflows, ni les hooks,
   ni `pousser.sh` ; aucune ligne `Garde-modifiée:`.
7. *Le site* : la page « Méthode » (`methodeConstruction`, `pages.js`) dit le
   modèle Python « de référence », « qui fait foi ». La zone du site ; non
   touchée.

**La concordance au bit près.** `tests/js/moteur.test.js` exige chaque nombre
des témoins à l'égalité exacte sous Linux x86_64, où GitHub les fabrique ;
ailleurs, des témoins refaits par une autre libm gardent la tolérance de 1e-9
(`_fichier_a_jour`, `tests/test_web.py`). Un NaN là où le Python écrit un
nombre ne passe plus, ni ici ni là. Vu rouge : un nombre d'un témoin décalé
d'un ulp (`age_reference_cliquet_legal`, `frais_preleves` du pilier capitalisé,
1,79 × 10⁻¹⁶ en relatif) donne « 1 écart(s) sur 913 cas », quand 1e-9
l'aurait laissé passer ; le fichier remis à l'octet, vert. C'est la garde qui
rend la bascule sûre : le Python qui suit doit retomber au bit près, et les
témoins ne changeront pas d'un nombre le jour où le portage les écrira.

**La bascule.** La note de décision 0005, décidée par le propriétaire,
mise en forme ici ; la dernière phrase du principe 4, le § 7.1 et la ligne
« Où va quoi » (`docs/architecture.md`) ; la carte du dépôt, son schéma
compris ; les consignes de `src/` — la règle et la liste « Un changement du
moteur d'une carrière » — et de `moteur/` — l'ouverture et la liste « Un
chiffre de plus » ; cinq en-têtes du portage qui disaient leur jumeau Python
« qui fait foi » ; une version de l'architecture. Aucun chiffre publié ne
bouge ; un commentaire du portage n'entre dans aucune page. Pas d'entrée au
journal de veille : aucune règle du scénario 1 n'est touchée.

**Tests.** `node --test tests/js/moteur.test.js`, 46 essais ;
`python scripts/verifier_prose.py --corriger` ; la suite rapide ; les tests
de la prose, de la carte du dépôt et des jumeaux.

**Ce qui reste, dans l'ordre**, avant qu'une règle du moteur ne s'écrive
qu'une fois :
1. Les témoins simulés par le portage : une table des types des résultats,
   pour que `construire_temoins.py` écrive à l'octet ce que le portage rend ;
   le moteur Python confronté au fichier tant qu'il reste.
2. Les confrontations par le pont : `test_estimation_officielle.py`, dont le
   portage bâtit déjà la carrière ; `test_destinie.py` ; puis
   `test_oracle.py`, chaque exemple officiel passé au portage.
3. Le coût par le pont : ses cas types datés par le portage (`point_fixe` et
   `pointFixe`), puis ses carrières ; un autre chemin pour ce que
   `_simulations_en_python` simule encore.
4. Les deux paires de données, selon la note 0005.
5. Les paires du moteur, par sous-ensemble cohérent ; la page « Méthode »
   récrite par une session du site quand le point 2 est fait.
