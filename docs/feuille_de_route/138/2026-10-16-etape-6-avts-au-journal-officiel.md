# Étape 6, sixième partie : l'AVTS de chaque date, certifiée au Journal officiel

**La demande.** La session n° 10 du 16 octobre 2026 : « certifier au Journal
officiel les montants de l'AVTS d'après 1983 (`scripts/fetch/jorf_avts.py`),
décret par décret, par l'index de la DILA », le premier point de « Ce qui
reste » de la cinquième partie (`2026-10-14-etape-6-r-732-70.md`).

**Ce que portent les index, lus le jour même** (journal de veille
`2026-10-16-action-138-etape-6-avts-au-journal-officiel.yaml`). Le
certificateur relisait déjà chaque montant daté de l'AVTS, non le seul du
31 décembre : 185 montants datés de la caisse redits par un texte, dont l'AVTS
à chacune de ses dates du 1er juillet 1983 au 1er janvier 2003, par l'article
(LEGI, et le JORF depuis 1990), et de 1970 à 1983 par la notice ou le titre.
Après, aucun texte de l'index n'écrit un montant de l'AVTS : les arrêtés de
2004 à 2007 ne fixent qu'un coefficient, et la caisse revalorise depuis 2008
par ses circulaires ; la recherche de l'allocation près de « montant », depuis
2003, ne rend que des renvois (R. 732-70, L. 341-15, D. 643-9…). Un calcul ne se
certifie pas.

**Ce qui est fait.**

- *Deux contrôles* dans `scripts/verifier_donnees.py` sur
  `pension_minimum_avant_1983.csv`, par date : `…_journal_officiel`, au niveau
  `certifiee`, l'AVTS des montants datés que `jorf_avts.json` certifie ;
  `…_cnav`, au niveau `haute`, les autres dates du barème depuis l'ordonnance
  du 2 février 1945. 47 dates certifiées, d'octobre 1970 au 1er janvier 2003,
  dont les 31 d'après le 1er avril 1983 ; 57 restent à la caisse. Aucune valeur
  ne change : les deux sources s'accordent au centime.
- *Le paquet* refait (`construire_donnees.py`) : la fiabilité de la pension
  minimum change dans les deux moteurs ensemble, et
  `test_les_deux_moteurs_servent_la_meme_pension_minimum` le vérifie.
- *Un test* (`tests/test_verification.py`) : l'AVTS seule, et la loi de 1941
  hors de la table. L'en-tête de la table, `data/sources.yaml` (`cnav_avts`) et
  le tableau de `docs/limites/1-certification.md` le disent.

**Ce qui reste** à l'étape : l'outre-mer, avec un champ de saisie ; avant 1946,
la retenue ; au fac-similé, les textes d'avant 1970 et les plafonds de 1956 à
1981 ; l'AVTS de 2004 à 2026, qu'aucun texte n'écrit, reste à la caisse.
