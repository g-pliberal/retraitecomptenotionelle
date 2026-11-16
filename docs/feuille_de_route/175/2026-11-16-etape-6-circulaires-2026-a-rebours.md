# Étape 6, circulaires de 2026 : la lecture à rebours s'ouvre sur les deux références sans thème de l'année

**Reprise, au 16 novembre 2026.** Une seconde lecture des circulaires sans thème
avance à rebours, de 2026 vers le passé, pendant que la première avance depuis
2008. Ce bloc est le sien ; celui de la note de 2007 reste à la lecture
chronologique. 2026 est faite : deux circulaires, rangées en `limite`, sans écart
neuf. Viennent ensuite 2025 (3 circulaires), 2024 (11), 2023 (7), 2022 (6),
2021 (9), 2020 (7), 2019 (10), 2018 (8). Les deux lectures s'arrêtent où elles se
rejoignent. Méthode : celle de la note de 2007, la base relue par l'API, chaque
texte lu en entier, chaque citation retrouvée par script dans le texte servi.
Détail ici.

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2026 : deux, les circulaires Cnav
  n° 2026/15 du 17 avril et 2026/17 du 12 juin. Les autres circulaires de l'année sont
  au registre sous un thème (étape 4) ou déjà rangées.
- *La lecture* : les deux, relues par l'API le 16 novembre 2026 vers 12 h 40 UTC
  (`/reference/referencesByFileLeafRef/`), servies en PDF et lues au site
  (`/Pdf/<nom>`) par leur texte (`pdftotext`) : 2 pages et 28 pages, 62 Ko de texte, lus
  en entier par la session elle-même, sans agent. Les citations de cette note
  ont été retrouvées mot pour mot, par script, dans le texte servi (blancs normalisés).
- *Les sorts* : 2 références rangées, toutes deux `limite` ; le registre seul a changé
  (`data/reference/legislation/cnav/references.csv`, 2 lignes, les colonnes `sort` et
  `renvoi` seules).

**Par ce qu'elles disent.**

- *Les plafonds des veuves de guerre au 1er avril 2026* (n° 2026/15, qui « Annule et
  remplace la circulaire Cnav 2026/11 du 03/04/2026 ») : seul le plafond de l'ASI change,
  revalorisé « au taux de 0,8 % sur la base des montants en vigueur au 1er avril 2025 »,
  à 22 025,66 € par an ; les autres restent ceux du 1er janvier 2026 (15 019,46 € pour
  l'AVTS et les allocations de même étage, 23 482,88 € pour l'allocation supplémentaire
  et l'ASPA). Rangée comme ses devancières de 2005 et 2006 (n° 2005/56, 2006/53,
  2006/77) : `minimum_vieillesse.yaml` et `docs/limites/3-systeme-actuel.md`, où le
  plafond propre à la veuve de guerre (R. 815-26) est déclaré hors du modèle (ligne 495).
  Aucun de ces montants n'est dans les séries, comme attendu.
- *La retraite anticipée pour carrière longue au 1er septembre 2026* (n° 2026/17) :
  « Annulée et remplacée par la circulaire Cnav 2026/29 du 04/09/2026 », elle-même déjà
  rangée. Elle tire de l'article 105 de la loi de financement pour 2026 et du décret
  n° 2026-345 les âges de la porte des vingt ans et les durées cotisées par génération.
  La fiche `carriere_longue.yaml` (lignes 232 à 236) dit la circulaire 2026-29, relue ligne
  à ligne, de « mêmes âges et mêmes durées que la 2026-17 qu'elle annule ». La session l'a
  revérifié contre les séries : les âges de l'annexe 2 (60 ans et 3 mois pour les nés de
  septembre à décembre 1963, 60 ans et 6 mois en 1964, 60 ans et 9 mois de janvier à
  novembre 1965, 60 ans et 8 mois en décembre 1965, puis 60 ans et 9 mois, 61 ans,
  61 ans et 3 mois, 61 ans et 6 mois, 61 ans et 9 mois de 1966 à 1970, 62 ans ensuite)
  sont ceux de `legislation/carriere_longue.csv` à la date d'effet 2026.667 ; les durées
  (170 trimestres jusqu'aux nés de mars 1965, 171 d'avril à décembre 1965, 172 ensuite),
  celles de `legislation/duree_assurance_requise.csv` (lignes 128 à 137). Le reste — les
  quatre bornes de début d'activité, les périodes réputées cotisées et leurs plafonds,
  la règle « Le nombre de trimestres cotisés ou réputés cotisés ne peut excéder quatre
  pour une même année civile tous régimes de base obligatoires confondus », le volontariat
  associatif et le service civique exclus de la durée cotisée — est la lettre de la
  2026-29, que `carriere_longue_reputes_cotises_autres.yaml` et `service_civique.yaml`
  citent. Les rachats et versements (« Les versements demandés à compter du 13 octobre
  2008 sont exclus », les rachats de l'option taux seule refusés depuis 2011) ne sont pas
  pratiqués par le modèle, ce que `docs/limites/3-systeme-actuel.md` déclare (lignes 303
  à 315). L'ASPA, qui « peut être versée à compter de 62 ans aux assurés titulaires d'une
  retraite anticipée pour carrière longue », est déclarée servie à soixante-cinq ans par
  le modèle (même fichier, lignes 490 à 494). Une différence de fond avec la 2026-29, sans
  effet : la 2026-17 n'a pas le point 1.2.3.8 des trimestres de majoration pour enfant
  réputés cotisés, que la 2026-29 ajoute, et que le modèle tient de celle-ci
  (`carriere_longue_enfants_reputes_cotises.yaml`).

**Aucun écart neuf.** Les montants relus ne sont pas portés par le modèle (les plafonds
des veuves de guerre), ou sont conformes (les âges et les durées de la carrière longue).

**Ce que la base sert de travers.**

- Deux circulaires annulées, servies comme textes vivants : la n° 2026/17, par la
  n° 2026/29 ; la n° 2026/11, par la n° 2026/15 (la n° 2026/11 est au registre, sous le
  thème « Allocations du minimum », à lire).
- À la n° 2026/17 : l'annexe 2 ne donne aux nés de 1966 que les départs à 60 ans, à
  60 ans et 9 mois et à 63 ans, sans la ligne « avant 16 ans » à 58 ans que le point
  1.1.1 et les autres générations portent ; le point 1.1.1 écrit « varie de 60 à 61 ans
  et 9 mois ans selon l'année de naissance », quand son tableau dit « De 60 à 62 ans ».
- La circulaire n° 2026/5, que la n° 2026/15 cite, est au registre sous le nom
  `circulaire_cnav_2026_05_06022025.pdf`, millésimé 2025 au nom.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Le décret n° 2026-345 et
l'instruction interministérielle n° DSS/2A/2026/36 n'ont pas été relus au Journal
officiel ; les moteurs n'ont tourné sur aucun cas.
