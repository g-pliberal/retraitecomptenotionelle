# La fin de la deuxième vague : sept fichiers lourds sortis du moteur Python

Action 161, étape 9d, après `2026-11-15-la-deuxieme-vague.md`. Aucune règle,
aucune donnée, aucune page n'a bougé. `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) passe de 44 à 37.

## Ce qui est fait

- **`test_pcv_sante.py`** : le constructeur sous une autre part des
  cotisations est celui d'un simulateur de la façade bâti sous ces
  paramètres.
- **`test_cycle_de_vie_script.py`** : la grille des cas types se simule par
  la façade (`_grille`), l'âge fixé par le pilote du portage, au lieu de
  `castypes.calculer_cas_types`.
- **`test_regle_de_chacun.py`** : le balayage — 74 statuts, 86 générations,
  21 âges de départ, 264 497 départs — part en une demande (`pont.droit`).
  Pour qu'il tienne en dix secondes de plus, la carrière se bâtit une fois
  par statut et génération, puis se porte à chaque départ :
  `pont.CarriereSimple(options, depart=…)`, le pendant de
  `dataclasses.replace(carriere, age_liquidation=…)`. Lu une fois contre le
  moteur Python : identique sur les 264 497 départs. Le pont relit de plus
  `ouvrir.age_ouverture` et `liquider.annuites_au_taux_de_leur_annee` ;
  l'annuité du CESE se liquide sur le vrai relevé d'un conseiller entré à
  quarante ans et parti à soixante, au lieu de durées écrites à la main.
- **`test_ines.py`** : le barème d'Ines se prête au moteur du portage
  (`pont.Moteur.au_bareme_de_l_aspa`), au lieu d'un faux moteur Python.
- **`test_marins.py`** : `liquider.plafond_du_salaire_de_reference` et
  `liquider.abattre_au_dela_du_plafond` servis par la façade, chacun
  confronté au jumeau dans `test_facade_jumeau.py`.
- **`test_flux_fonction_publique.py`** : ce que le pont et l'étude rendent,
  vu identique au moteur Python, figé au témoin des valeurs.
- **`test_web.py`** : les simulateurs de la façade, et le cumul des règles
  d'indexation par `pont.indexation`.

## Ce qui reste

Deux fichiers de la vague 2 :

- `test_effet_retour.py` : `EffetRetour`, du coût, lit
  `simulateur.scenario_actuel.minimum_vieillesse`, une table du moteur
  Python. Il attend que le coût cesse de lire le moteur Python (vagues 3
  et 4, `test_cout.py`).
- `test_univers.py` : la résolution des univers en calculs notionnels
  (`scenarios/univers.calcul_notionnel`) n'est qu'en Python ; le portage a
  la sienne (`tests/js/univers.test.js`). À confronter par le pont, ou à
  figer au témoin.

Puis les vagues 3 et 4 (`2026-11-15-les-temoins-sans-jumeau-et-l-inventaire.md`).

## Ce qui attend le propriétaire

L'écart `rattachement_pension_smic` (3,45 € par an), inchangé.

**Tests.** `python -m pytest -m rapide` : vert ; les fichiers passés,
`test_facade_jumeau.py`, `test_pont.py`, `test_oracle.py`,
`test_droit_fige.py` et `test_fichiers_sur_le_moteur_python.py` : verts.
