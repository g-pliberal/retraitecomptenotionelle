# Les corrections de la relecture R-E5 : la CAVP et la CARPIMKO, retouchées

**La demande.** Le 5 novembre 2026, vague 10, la session d'orchestration confie à la file
E (tâche E4-bis) les points de la relecture R-E5 (`130/2026-11-05-relecture-r-e5.md`,
639b779), qui trouve la CAVP de E4 (c7fbb26) conforme et relève : un non-tranché non
déclaré, la majoration des nés jusqu'au 30 juin 1951 de 2011 à 2026 (moyen) ; deux textes
d'avant 2009 non nommés (faibles) ; pour la CARPIMKO, la ligne « Âge du taux plein » des
textes de 2024 et 2026, non citée (moyen), et un montant de 136,90 € qui n'est qu'un minimum
(faible). Consigne : rouvrir chaque texte, refaire chaque montant. Aucune règle du modèle ne
change.

## Ce qui est fait

- **Les textes, rouverts** dans l'index JORF du dépôt, récupéré de nouveau et mis à jour
  au 5 novembre (cinq incréments) : l'annexe de l'arrêté du 23 juin 2011
  (JORFARTI000024270214), le règlement de la CAVP de 2026 (JORFARTI000054436087), les
  titres et résumés des arrêtés de 1956, 1977, 1988 et 1989 ; pour la CARPIMKO, l'annexe de
  l'arrêté du 27 décembre 2023 (JORFARTI000048880643), le règlement de 2026
  (JORFARTI000054435915) et les statuts de 2015 (JORFARTI000031255547). Chaque fragment
  cité, cherché par un script dans son texte, s'y trouve.
- **La CAVP, la majoration des nés jusqu'au 30 juin 1951 : d'accord avec R-E5, non
  tranché.** L'article 12 récrit en 2011 : « De façon transitoire : ― les affiliés nés
  jusqu'au 31 décembre 1952 peuvent bénéficier d'une majoration de leur pension de retraite
  dans les mêmes conditions, mais uniquement jusqu'à l'âge permettant d'obtenir une
  retraite entière augmenté d'un an ». Le tableau de la même annexe : « 1. Pour les assurés
  nés avant le 30 juin 1951 inclus [...] Pas de majoration de pension pour un départ après
  65 ans ». Les deux se contredisent du 30 juin 2011 au 17 juillet 2026 ; le règlement de
  2026 suit le tableau, comme le modèle. Aucune lecture n'est exclue : le tableau est le
  texte spécial ; l'article 12, celui qui crée la majoration, le tableau n'étant annexé
  qu'à l'article des coefficients d'anticipation. Déclaré dans la fiche, avec le cas ; la
  version de 2011, l'approximation de la fin de 2011, la docstring de
  `CAVP_HORS_DU_MODELE` et le commentaire du cas `(1950, 67.0, 1.0)` le disent aussi.
- **La CAVP, les textes d'avant 2009** : l'arrêté du 17 septembre 1956 nommé ; celui du 6
  avril 1989 dit au seul Bulletin officiel (« N0 8920 »), avec celui de 1990 ; les deux
  courts résumés de 1977 et 1988 cités ; l'article 10 de 1977 et l'arrêté de 1989 ajoutés au
  « à relire ».
- **La CARPIMKO, la ligne « Âge du taux plein » : citée ; le point reste non tranché.**
  Les statuts récrits au 10 janvier 2024 nomment la ligne de leur table « Âge du taux plein
  65 ans 65 ans 4 mois [...] 67 ans » (article 12 quater, 6°), le règlement « Age du taux
  plein » (article 6), là où 2015 disait « Age prévu à l'article 11.1 ». La seconde phrase
  de l'article 5 du règlement, « par trimestre civil entier d'ajournement postérieur à l'âge
  du taux plein », en reçoit un appui. Je ne le tiens pas pour une erreur prouvée : la
  première phrase, « ajournée au-delà de l'âge auquel elle aurait pu être liquidée sans
  abattement », soutient le modèle, et l'article 4 du même règlement écrit « l'âge du taux
  plein sans condition » quand il veut l'âge de la table — ce qui laisse à « l'âge du taux
  plein » seul le sens de l'âge où l'assuré l'atteint. R-E5 laissait la question ouverte ;
  elle reste non tranchée, la citation ajoutée.
- **La CARPIMKO, 136,90 € : un minimum**, dit comme tel dans les deux approximations qui le
  donnent, avec 205,35 € dans la lecture de la table.

## Les calculs

Chaque valeur du modèle est celle des deux moteurs (essai du jour, `servi_et_refait`,
requête du formulaire) ; chaque valeur du texte, posée à la main.

- **CAVP, né le 10 mars 1950, entré à 21 ans, parti à 66 ans le 1er avril 2016** : le
  modèle sert 12 330,55 € par an, sans majoration, comme le tableau. L'article 12 : du 10
  mars 2015, ses 65 ans, au 1er avril 2016, douze mois et 22 jours, quatre trimestres
  entiers, 4 × 0,5 % = 2 % ; 12 330,55 × 1,02 = 12 577,16 €, **246,61 € par an de plus**.
- **CARPIMKO, né le 10 décembre 1954, entré à 20 ans, parti à 62 ans le 1er janvier
  2017** : le modèle sert 5 681,23 €, 1,0375 ; sans majoration, 5 681,23 / 1,0375 =
  5 475,89 €. Comptée de l'âge légal de la base, un trimestre, × 1,0125 = 5 544,34 €,
  **136,90 € de trop** ; comptée de l'âge de la table, 65 ans, aucune, **205,35 € de
  trop**.
- **CARPIMKO, né le 10 novembre 1959, entré à 20 ans, à 67 ans le 1er décembre 2026** : le
  modèle, 7 022,19 €, 1,25 ; de 66 ans et 4 mois, deux trimestres civils entiers, 1,025,
  7 022,19 / 1,25 × 1,025 = 5 758,20 €, 1 263,99 € de plus que la lecture de la table.

## Ce que l'étape laisse

- **Au propriétaire** : la CAVP compte trois non-tranchés (la valeur de service par
  génération, le trimestre entamé, la majoration des nés jusqu'au 30 juin 1951) et deux
  erreurs, inchangées ; la CARPIMKO, ses trois erreurs et trois non-tranchés, le montant de
  l'erreur (2) dit au moins 136,90 €.
- **Le paquet** ne lit pas les fiches : rien à refaire.

Renvoi du 5 novembre 2026 : la relecture R-E6 (`2026-11-05-relecture-r-e6.md`) trouve ces chiffres exacts et confirme l'écart d'écriture d'un centime, avec un second : écrits sur 5 681,23, les intermédiaires valent 5 475,88 et 5 544,33.

Renvoi du 6 novembre 2026 : la file E5-bis écrit 5 475,88 et 5 544,33 dans `carpimko_ages_2015` (`2026-11-06-e5-bis-corrections-de-r-e6.md`).
