# La vague du 12 novembre 2026 : les étapes 2, 3, 5 et 6 menées, et ce qui attend le propriétaire

Note de la session d'orchestration qui a mené, une à la fois, les quatre
étapes de l'action 192 qui écrivent dans le modèle. Elle ne remplace aucune
note d'étape : elle dit où chacune s'est arrêtée, ce que le propriétaire a à
trancher, et un fait que la note de l'étape 2 ne porte pas.

**Où en est chaque étape.**

- *Étape 5, close.* La règle du cumul de la pension militaire, pour les
  premières pensions de 2027, est publiée (8ac03c7). La suite complète de
  GitHub l'a jugée verte (course 1733 de `tests.yml`).
- *Étapes 2, 3 et 6, ouvertes.* Chacune a lu le droit, écrit sa règle et son
  test, verts dans les deux moteurs, puis gardé le tout hors de `main`, dans
  un fichier que `git apply` rejoue, sous `docs/mesures/192/` : la règle
  déplaçait plus que son cas, ou tenait à une décision du propriétaire. Sur
  `main` : la lecture dans la fiche, l'écart déclaré, la note et son bloc
  « Reprise » (208aa46, 936bddd, 6a6f253). L'étape 6 a vérifié que les trois
  fichiers s'appliquent encore ensemble sur son commit.

**Ce que le propriétaire a à trancher**, chaque note portant la
recommandation de sa session.

- *Étape 2.* Garder ou recaler le cas type de l'exploitant agricole, que la
  règle fait partir un an plus tôt ; la lecture de « par dérogation » dans la
  rédaction de 2026 ; l'état de la fiche `carriere_longue` d'ici là.
- *Étape 3.* Publier la date d'effet au trimestre civil seule, ou après la
  lecture des statuts des cinq sections dont le moteur date la complémentaire
  à part ; la pension tenue pour demandée à temps.
- *Étape 5.* Le grade, qui manque à la saisie.
- *Étape 6.* La « deuxième ligne » du tableau : 22 % ou 20,75 % ; l'abattement
  servi au-delà de vingt trimestres avant 2027.
- *De la vague d'avant*, toujours sans réponse : l'exception de l'article
  R. 173-3-2 (note de l'étape 7), l'ouvrier de l'État maintenu après la limite
  d'âge, les deux points de la réversion (note de l'étape 4), l'année cotisée
  au prorata du chef d'exploitation (note de l'étape 1).

**Les étapes que les sessions proposent, et qu'aucune n'a ouvertes** : elles
ne sont pas dans la feuille de route, et attendent l'accord du propriétaire.

- Le calcul qui date les cas types, pour le régime agricole : préalable à la
  publication de la règle de l'étape 2.
- La complémentaire de la CARPIMKO, qui n'a pas le même montant à la même
  date selon qu'elle se liquide avec la base ou sans elle : défaut présent sur
  `main`, que l'étape 3 a trouvé.
- La date d'effet dans les statuts de la CARPV, de la CAVEC, de la CAVOM, de
  la CPRN et de la CARPIMKO d'avant 2026.
- Avant 2027, la pension d'invalidité et celle du non-officier de moins de
  vingt-cinq ans de services, plafonnées devant un employeur public quand
  l'article L. 86 les laisse entières.
- Le seuil de sept mille euros et l'imputation par montants décroissants du
  décret n° 2026-1017 ; le cumul entier des marins, des artistes du ballet de
  l'Opéra et des anciens mineurs.
- Le complément différentiel de points du régime complémentaire des
  indépendants, qui naît en 2027.

**Ce que la note de l'étape 2 ne dit pas.** Sa session, avant de s'arrêter,
a tracé le calcul qui date le cas type de l'exploitant né en 1953, la règle
appliquée : le point fixe du pilote ne converge pas. L'âge proposé monte d'un
trimestre à chaque passe tant que l'année ne change pas : 164 trimestres
cotisés de mai 2013 à janvier 2014, puis 168 d'un bloc en février 2014, où le
départ s'ouvre bien, à 61 ans. Les quatre passes s'arrêtent sur octobre 2013,
où le droit n'est pas ouvert. Le fait vient de son compte rendu ; il n'a pas
été rejoué ici.

**La suite rouge de la nuit.** La course 1728 a conclu rouge, quatorze échecs
de `tests/test_entrees_du_moteur.py` : la sonde des entrées dans le moteur,
ajoutée par l'action 161, se servait de `sys.monitoring`, que le Python 3.11
de GitHub n'a pas. La session qui l'avait écrite l'a réparée (334694e), sans
toucher au workflow ; la course 1732 a conclu verte.

**Ce que la vague a appris, pour la consigne d'une étape du modèle.** Une
règle verte sous `-m rapide` peut déplacer un cas type de la grille du coût,
des témoins, ou des tests écrits sur l'ancien comportement : la consigne des
étapes 3, 5 et 6 demandait donc de lancer aussi les quatre fichiers du coût
et de compter les témoins déplacés avant d'envoyer, et de garder la règle en
correctif plutôt que de pousser au rouge.
