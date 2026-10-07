# 6. Reproductibilité

- Aucune dépendance hors PyYAML ; tous les calculs sont déterministes.
- La calibration des tables de mortalité est mémorisée dans
  `data/derive/calibrations_mortalite.json`, que `scripts/construire_donnees.py`
  réécrit et dont `test_le_paquet_est_a_jour` vérifie la fraîcheur. Chaque loi y
  porte l'empreinte de ses entrées — les deux espérances cibles, les quotients
  observés de l'année, les constantes de la méthode — et n'est reprise que si
  elles n'ont pas changé. Ce n'était pas le cas jusqu'au 23 septembre 2026 : la
  mémoire, indexée sur « année|sexe » seulement, avait survécu au remplacement
  des espérances de vie projetées par celles de l'INSEE, et les lois de 2025 à
  2080 restaient calées sur les anciennes cibles — plus d'un an d'espérance de
  vie de trop pour les femmes —, dans le modèle comme sur le site, sans qu'aucun
  test le voie : tous construisaient leur table sans cette mémoire.
- La certification des séries est tracée dans `data/derive/certification.json`,
  que `scripts/verifier_donnees.py --appliquer` COMPLÈTE au lieu de le
  remplacer : les récupérateurs sont indépendants et lents, on ne lance
  presque jamais les dix-sept d'un coup, et réécrire le journal à partir des
  seules sources présentes ce jour-là effaçait la trace de toutes les autres.
  Chaque fiche de série porte `verifiee_le`, le jour où elle a été relue contre
  sa source, valeurs changées ou non ; `dernier_passage_le` n'est que la date
  du dernier `--appliquer`, fût-il partiel. La page Données dit le minimum des
  dates de fiche, seule affirmation que le journal soutient, et un test refuse
  une fiche sans date. Les dates antérieures au 17 septembre 2026 ont été
  rétablies depuis l'historique du dépôt — le dernier commit où chaque fiche a
  changé —, ce qui est une borne basse : une série relue sans changement avant
  cette date n'a laissé aucune trace.
- Les tests couvrent le chargement, la fiabilité, la règle de certification, la
  concordance des tables de mortalité observées avec les espérances publiées, les
  propriétés du moteur et le comportement des scénarios : `python -m pytest`.
  Aucun test n'accède au réseau : les sources sont simulées.
- Les bases JORF et LEGI de la DILA sont interrogeables sans retélécharger
  leurs dumps : `python scripts/fetch/dila_index.py jorf --recuperer` rapatrie
  l'index plein texte publié sur la release `index-dila` du dépôt,
  `--mettre-a-jour` y applique les incréments quotidiens parus depuis, et
  `dila_cherche.py` l'interroge. L'index se reconstruit depuis le dump par
  `dila_index.py jorf` (une demi-heure, dump gardé en cache dans `data/brut/dila/`).
