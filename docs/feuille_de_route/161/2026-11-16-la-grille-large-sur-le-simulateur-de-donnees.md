# La grille large sur le simulateur de données : ses deux jumeaux Python retirés

Action 161, suite de `2026-11-16-les-derniers-lecteurs-du-simulateur-python.md`.
Le propriétaire a décidé, le 16 novembre 2026, que les trois derniers lecteurs
du simulateur Python passent au JavaScript. Voici le premier. Aucune règle,
aucune donnée, aucun témoin n'a bougé ; le moteur Python reste en place.

`scripts/grille_large.py` bâtit désormais un `SimulateurDeDonnees`, et non
plus le `Simulateur` du moteur Python. Ses deux jumeaux partent :

- `CasTypeLarge.age_liquidation_pour`, qui datait le départ par le pilote
  Python, demande l'âge au portage (`castypes.ages_de_la_grille`), attente
  comprise ;
- `_debut_de_la_surcote_en_python`, que seul ce jumeau appelait, est retiré ;
  le premier âge surcoté se lit au portage (`debut_de_la_surcote`), comme
  avant pour les mesures. L'import de `REGIMES_CODE_DES_PENSIONS`, qui ne
  servait qu'à lui, part avec.

`CasTypeLarge._carriere` reste : il ne fait qu'appeler `carriere_parcours` du
simulateur qu'on lui passe, la façade des tests, qui le demande au pont.

**Vérifié.** Les deux tests de `test_grille_large.py` qui figent au témoin
des valeurs la grille datée, bâtie, simulée et ses mesures rendent les mêmes
valeurs. Sous la sonde, un essai qui date un fonctionnaire qui surcote,
cherche son premier âge surcoté et lit sa condition de départ sur le
simulateur de données : « aucune règle du moteur Python ».

**Tests.** `test_l_age_d_un_cas_type_large_se_demande_au_portage` (neuf) :
l'âge du cas type est celui du portage, le pilote Python interdit, et le
jumeau de la surcote n'existe plus ; `grille_large` rejoint les scripts de
`test_chargeurs_a_part.py` qui ne bâtissent plus le `Simulateur`. Vus rouges,
puis verts. `test_grille_large.py` entier (110) et `-m rapide` : verts.

**Reste.** `lectures_du_modele`, puis `contexte.simulateur` (la fabrique et le
bilan du compte) ; le retrait des règles, avec l'accord du propriétaire.
