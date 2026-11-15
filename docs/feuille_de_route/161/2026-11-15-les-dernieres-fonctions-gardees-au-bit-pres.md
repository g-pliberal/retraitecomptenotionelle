# Les dernières fonctions gardées au bit près : les comptes du COR, le bilan figé et le contexte confrontés à leur double, six fonctions par leur appelant, et la colonne `test` de la liste rendue obligatoire

Action 161, étape 7e, après `2026-11-15-six-fichiers-et-les-regimes-au-bit-pres.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

- **Toutes les fonctions gardées ont leur test.** La liste en compte 118,
  chacune confrontée à son double : 108 par leur grille dans
  `tests/test_jumeaux_au_bit.py`, dont deux attendues rouges sur un écart
  déclaré, six par la grille de leur appelant, trois par
  `tests/test_agregats.py`, et `en_mois` par `tests/test_moteur.py`. `jumeaux.ecarts_de_la_liste` rougit désormais
  une fonction gardée sans test (`tests/test_jumeaux.py`).
- **27 grilles de plus** : vingt des comptes du COR (`equilibre.py`, sous la
  référence et ses quatre variantes : années, dépense, ressource, fiabilité,
  structure des ressources, engagements, transferts, la décomposition de la
  dépense et ses croissances, les deux fonctions de variante) ; trois du
  bilan figé (`charger_bilan`, lu entier, `part_pib` et `ecart_pour` de
  l'engagement acquis) ; quatre du contexte (`assiette`, `depenses`,
  `comptes`, `simulateur`, lus par des méthodes déjà confrontées). Toutes
  identiques, sauf une.
- **Un écart déclaré, au dernier bit** : `ecart_pour` de l'engagement acquis
  n'associe pas son interpolation de même, `(Δécart × Δvaleur) / largeur` en
  Python, `Δécart × (Δvaleur / largeur)` au portage. La prose en cite le
  résultat (`mesures_prose.py`, `quoi=ecart`) ; le site ne l'écrit pas.
  Rien n'est tranché : il est déclaré dans `ECARTS_DECLARES`, et la
  confrontation rougira le jour où les deux s'accordent.
- **Six fonctions confrontées par leur appelant**
  (`PAR_L_APPELANT`, `test_la_fonction_gardee_se_confronte_par_son_appelant`,
  qui rejoue la grille de l'appelant) : les deux chargeurs dont le portage
  rend des tables (`charger_prelevements_historiques`, par `valeur` ;
  `charger_contributions_equilibre`, par ce que chaque contribution prélève,
  `montant` en Python, `montantDeLaContribution` au portage, sur 216 points
  de 1995 à 2026) ; `bareme` des contributions, que le portage n'exporte pas,
  par la même grille ; `_en_vigueur` des employeurs publics, par `taux` ;
  `dater_les_taux_moyens`, par `periode` aux taux moyens ; `_donnee` du
  contexte, par `comptes`.
- **Trois fonctions du contexte confrontées par `tests/test_agregats.py`** :
  `cout` et `_agregat`, par le solde figé, `avantages`, par les avantages
  figés. Le portage ne les calcule pas : il lit la table que la fabrique
  tire du coût Python, et ces tests confrontent la table au calcul.
- **Le test sait davantage** : un dossier de `data/` qui vaut le paquet au
  portage (`SousRacine`) ; une fonction du portage sous un autre nom
  (`nom_js`) ; une clé du paquet à la place du paquet (`cle_du_paquet`).

## La relecture des lecteurs

Par leurs appels, comme aux étapes 7b à 7d, en suivant l'objet qui reçoit
l'appel : `depense`, `solde`, `coefficient` ou `ressources_de` sur une
ligne du coût (`cout.SoldeAnnuel`, que la table du bilan imite) ne sont pas
ceux du bilan figé ni du compte du COR.

- **8 lecteurs corrigés** : `part_pib` du bilan, lu par `mesures_prose.py`
  sur l'engagement acquis ; six du compte du COR lus par `cout.py`
  (`annees`, `depense`, `fiabilite`, `part`, `part_contributive`, et
  `valeur` de la décomposition) ; `periodes` de la décomposition, par son
  propre fichier, qu'`indice_croissance` appelle.
- **11 fonctions passent au moteur** : huit du bilan figé (`annee`,
  `coefficient`, `depense`, `exemple`, `ressources`, `ressources_de`,
  `sensibilite`, `solde`), qu'aucun fichier qui reste ne lit, la fabrique
  lisant le coût et `mesures_prose.py` le seul engagement ; `bilan` et
  `distribution` du contexte, qu'aucun fichier qui reste n'appelle ;
  `solde` du compte du COR.

La liste compte 118 fonctions gardées et 116 au moteur.

## Ce qui reste

1. **Le retrait des règles du moteur Python**, avec les fonctions
   `au_moteur` de la liste, une paire à la fois, par la méthode des notes de
   décision 0003, 0005 et 0006 (`src/CLAUDE.md`, « Un retrait de jumeau ») :
   la liste dit, fichier par fichier, ce qui part et ce qui reste ; ce qui
   reste a son test. Les grilles qui lisent une méthode partie (`_bilan` lit
   déjà les tables du Python, non ses accesseurs) s'adaptent au retrait.
2. Puis les périodes assimilées du relevé (note de décision 0008).
3. L'écart d'`ecart_pour` attend la décision du propriétaire.

**Tests.** `tests/test_jumeaux_au_bit.py` et `tests/test_jumeaux.py` :
137 passés, deux écarts attendus ; `python -m pytest -m rapide` : 5 368
passés, deux écarts attendus.
