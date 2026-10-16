# Le sixième domaine, étape 2 : les faits de la chronologie

Session 8 de la vague bis du 16 octobre 2026, sans le propriétaire. L'étape 2
du gabarit (`2026-10-14-sixieme-domaine-mesure.md`) : donner aux périodes
assimilées manquantes leurs faits dans la chronologie. Aucune étape ne les lit
encore : aucun résultat ne bouge, ni le site, ni les témoins.

## Ce qui est fait

- **Le vocabulaire** (`data/reference/vocabulaire/valeurs.yaml`) : deux
  listes neuves, `motifs_d_assimilation` — `stage_de_formation_professionnelle`
  (L. 351-3, 8°), `stage_d_insertion` (9°), `sportif_de_haut_niveau` (7°),
  `conge_supplementaire_de_naissance` (1°) — et `dispositifs_d_insertion`, les
  cinq que nomme le k du 4° de R. 351-12 (TUC, stage pratique en entreprise,
  stage jeunes volontaires, programme d'insertion locale, stage d'initiation à
  la vie professionnelle). La sorte `periode_assimilee` renvoie à ses motifs.
  Le chômage, la maladie, la maternité et le service militaire restent des
  `periode_d_interruption`, que la carrière lit déjà : rien n'y est déplacé.
- **La présomption `pas_de_periode_assimilee`** : qui n'en déclare pas n'en a
  eu aucune, et aucun de ses emplois n'était en apprentissage ;
  `appliquee_par` le dit, `entrera_a: compter_les_durees`. Les quatre fiches
  la lisent (`presomptions:`), comme `test_carte` l'exige.
- **La chronologie** (`chronologie.py` et son jumeau `chronologie.js`) :
  `avec_periodes_assimilees(chronologie, declarees)` ajoute à une chronologie
  construite les périodes déclarées, une table chacune — `motif`, `debut` et
  `fin` (année, mois ou jour, fin exclue), `dispositif` pour un stage
  d'insertion et lui seul, `jours` quand la période n'en compte pas tous les
  jours de ses dates (jours de stage, jours de congé indemnisés) —, et refuse,
  avec les mêmes mots dans les deux moteurs, un motif inconnu, un dispositif
  manquant ou de trop, une fin avant le début, une période avant la naissance
  ou après le départ, des jours hors de la période. `periodes_assimilees` les
  relit ; `periodes`, donc la carrière d'aujourd'hui, ne les voit pas ;
  `controler` vérifie motif et dispositif.
- **L'apprentissage, attribut de l'emploi** : `Metier.apprentissage` (faux
  par défaut) pose `apprentissage: true` sur chaque morceau du métier dans la
  chronologie, les dates du métier étant celles du contrat ; `controler`
  refuse l'attribut hors d'une `periode_d_activite`.
- **Les tests** (`tests/test_chronologie.py`) : neuf saisies de plus au test
  de concordance des deux moteurs, dont sept refus ; un test des listes, du
  contrôle, et de la carrière inchangée quand on ajoute des périodes.

## Ce que l'étape laisse aux suivantes

- **Étape 3**, les fonctions de `compter_les_durees` : les deux règles de
  décompte de l'étape 1 — l'apprentissage complète, année par année, jusqu'à
  la durée du contrat ; les trois autres comptent des jours dans l'année
  (cinquante, quatre-vingt-dix, cinquante-huit par trimestre), dans la limite
  de quatre trimestres par an tous motifs confondus, et ne sont pas cotisés.
  La borne du 9°, les pensions prenant effet depuis le 1er septembre 2023, est
  la date d'effet de la liquidation, non un fait de la période. Le plafond des
  sportifs (seize, puis trente-deux trimestres) et leurs conditions d'âge et
  de ressources lisent des faits qui existent déjà (naissance, ressources).
- **Le relevé déposé** ne porte pas l'apprentissage : une ligne de relevé
  n'a pas d'attribut pour lui (`LigneRelevee`). Les trimestres d'un relevé
  font foi ; à voir à l'étape 3 s'il faut l'en dire, ou laisser le relevé tel.
- **Étape 5**, le bloc du formulaire : la saisie appellera
  `avec_periodes_assimilees` et posera `Metier.apprentissage` ; elle revient à
  la session des pages.
- Une version de l'architecture, à la clôture du domaine, dira que
  l'apprentissage, que le § 5.2 range parmi les périodes assimilées, est un
  attribut de l'emploi.

## Ce qui attend le propriétaire

Rien de neuf : la décision de la proposition, à l'étape 7.
