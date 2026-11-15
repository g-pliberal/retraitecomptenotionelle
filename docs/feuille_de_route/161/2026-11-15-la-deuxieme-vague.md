# La deuxième vague : trente et un fichiers de tests sortis du moteur Python

Action 161, étape 9c, après `2026-11-15-la-fin-de-la-premiere-vague.md`.
Aucune règle, aucune donnée, aucun témoin, aucune page n'a bougé : des tests
changent, et la façade sert ce que le portage portait déjà. `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) passe de 75 à 44.

## Ce qui est fait

Trente et un des quarante fichiers de la vague 2 simulent, bâtissent et
lisent leurs règles par la façade (`tests/facade.py`). Pour cela, la façade
sert de plus, chaque appel confronté à son jumeau dans
`test_facade_jumeau.py` :

- **Sept tables** (`pont.TABLES_DE_LA_FACADE`) : `ages_regimes.ages`,
  `ages_surcote_regimes_speciaux.age`, `calendriers_duree_requise.trimestres`,
  `decote_regimes_speciaux.parametres`, `durees_requises_regimes.ligne`,
  `majorations_enfants.par_enfant`, `baremes_trimestre.valeurs`.
- **Des règles** (`pont.REGLES_DE_LA_FACADE`) : `liquider.assiette_de_reference`,
  les quatre du RAFP (`majoration_rafp`, `conversion_capital_rafp`,
  `prestation_rafp`, `mois_apres_le_depart`), `compter.arrondir_les_services`,
  `ouvrir.mois_ouverture_des_droits`, et un module de plus, `categories`
  (`age_legal`, `age_des_anciens_combattants`), que `pont.mjs` ajoute à
  `MODULES_DU_DROIT`.
- **La façade transmet** une ligne avec sa carrière quand la règle ne reçoit
  pas la carrière (`facade.ligne_de`, pour `assiette_de_reference`) ; la
  règle d'une fiche à paliers, dictionnaires et suites imbriqués
  (`_donnee_de_fiche`) ; une constante de module qui est une suite de valeurs
  simples (`categories.FICHES_DES_CATEGORIES`).

Quatre confrontations au moteur Python changent de forme : le RAFP et le
diviseur des comptes étrangers perdent la leur (le jumeau confronte les
règles du RAFP ; les diviseurs ne se lisent plus qu'au portage) ; la table
Agirc de 1947 se confronte au portage par la fiche ; la grille des mères ne
se garde plus que du moteur Python, sans se comparer à lui. Le décompte des
services saisit par `Saisies(Simulateur)` de la façade.

## Ce qui reste

Neuf fichiers de la vague 2, plus lourds qu'annoncé :

- `test_ines.py` remplace le barème de l'ASPA par celui d'Ines
  (`SimpleNamespace` en guise de moteur) : à écrire en données ou au pont.
- `test_regle_de_chacun.py` : une durée simulée à la main
  (`annuites_au_taux_de_leur_annee`), et un balayage par statut.
- `test_pcv_sante.py` (`Simulateur._constructeur_variante`),
  `test_effet_retour.py` (`distributions_par_sexe`),
  `test_cycle_de_vie_script.py` (`regimes_interpenetres` lit les affiliations
  du moteur) : ce que la façade ne sert pas encore.
- `test_marins.py`, `test_flux_fonction_publique.py`, `test_univers.py`,
  `test_web.py` : des confrontations au moteur Python et ses univers.

Puis les vagues 3 et 4. L'angle mort de l'inventaire demeure : `Saisies()`
sans la façade y entre sans être compté.

## Ce qui attend le propriétaire

L'écart `rattachement_pension_smic` (3,45 € par an), inchangé.

**Tests.** `python -m pytest -m rapide` : vert ; les fichiers passés,
`test_facade.py`, `test_facade_jumeau.py` et
`test_fichiers_sur_le_moteur_python.py` : verts.
