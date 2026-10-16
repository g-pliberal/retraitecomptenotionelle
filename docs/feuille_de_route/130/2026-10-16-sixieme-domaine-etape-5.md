# Le sixième domaine, étape 5 : le bloc du formulaire

Session 1 de la vague quinquies du 16 octobre 2026, sans le propriétaire, seule
sur les pages. L'étape 5 du gabarit (`2026-10-14-sixieme-domaine-mesure.md`) :
que le simulateur déclare les périodes que les étapes 1 à 4 savent compter.
La saisie ne fait que déclarer : ce que chaque période valide, les fiches et
leurs versions le décident.

## Ce qui est fait

- **Le bloc plutôt qu'un motif de plus aux lignes de carrière** : une ligne
  de carrière est un statut par mois, que les interruptions ramènent à
  l'année ; une période assimilée se compte au jour, a ses jours propres
  (jours de stage, de congé indemnisés) et peut couvrir une année travaillée
  (le sportif). D'où un dépliant, « Apprentissage et périodes assimilées »,
  replié, sur le modèle de « Carrière hors de France » : quatre lignes au
  plus, `assimilee1_motif` à `assimilee4_…` — le motif, le dispositif d'un
  stage d'insertion, `debut` et `fin` (AAAA, AAAA-MM ou AAAA-MM-JJ, gardés
  tels quels, la fin exclue : « le lendemain du dernier »), les `jours` — ;
  et `apprentissage`, le rang de la ligne de carrière qui est le contrat, un
  seul (la ligne porte `Metier.apprentissage`, de son début à la ligne
  suivante).
- **Les deux saisies** (`saisie.py`, `saisie.js`) : la lecture
  (`_periodes_assimilees_saisies`), la vérification (`_verifier_assimilees` :
  motif, dispositif du seul stage d'insertion, dates lisibles, fin après le
  début, début après la naissance et avant le départ, jours de un à ceux des
  dates ; l'apprentissage sur une ligne qui est un emploi, et jamais avec un
  relevé, qui n'a pas d'attribut pour lui), la réécriture de l'adresse,
  `periodes_assimilees_declarees`. La borne `min` du champ des jours est
  opposée par la saisie ; les dates n'en ont pas.
- **Les deux contextes** passent les périodes à la carrière, par parcours et
  par relevé ; `Carriere.depuis_parcours` et `depuis_releve` (et leurs
  jumeaux) les posent dans la chronologie par `avec_periodes_assimilees`,
  avant `preparer`.
- **Les témoins** : cinq simulations (`assimilee_…` : un an de TUC, qui ajoute
  cinq trimestres ; l'apprenti de 1983, que rien ne change, la fiche d'avant
  2014 n'existant pas ; l'apprenti de 2016 payé peu, trois trimestres de
  plus ; quatre-vingts jours de stage dans une année sans activité ; une
  sportive de haut niveau à vingt ans) et une page,
  `simuler_periodes_assimilees`, au formulaire figé entier.
- **Les tests** : `tests/test_saisie_assimilees.py` (rapide) — la lecture,
  l'adresse relue, l'attribut posé, treize refus, et les deux moteurs
  d'accord, refus compris (`tests/js/comparer.mjs`). Le budget de mots du
  formulaire vierge monte de quatre, pour le titre du dépliant.

## Ce que l'étape laisse

- **Étape 6**, la page Coût : le complément de l'apprentissage ; puis
  **l'étape 7**, la décision de la proposition. L'inventaire des avantages
  non contributifs garde `etat_modele: absent` pour l'apprentissage : à revoir
  avec le coût.
- Un seul contrat d'apprentissage par carrière, faute d'un champ par ligne de
  métier, que le budget de mots du formulaire vierge aurait payé : deux
  contrats successifs se déclarent en une seule ligne de métier.
- Le relevé déposé ne porte toujours pas l'apprentissage ; ses trimestres
  font foi.

## Ce qui attend le propriétaire

Rien de neuf : la décision de la proposition, à l'étape 7.
