# Relecture des retouches de R-D2 (commit 6585726) : conformes ; un écart faible, la deuxième année du commerçant en 2004

File R-D3, le 5 novembre 2026, sur Opus, à la demande de l'orchestration. Relecture
indépendante du commit 6585726 (file D3) et de sa note
`2026-11-05-retouches-de-la-relecture-r-d2.md`. Lecture seule : aucune règle, aucune
donnée, aucun test touchés.

**Ce que cette note règle de la précédente.** `2026-11-05-relecture-de-d3.md`, § 5, a
été écrite sur l'état du commit 4cf6b96. Elle dit (a) fait pour moitié, et (c) et les
deux défauts non faits. Le commit 6585726 était déjà sur `main` quand elle y a été
publiée, et elle n'en tenait pas compte. Son § 5 est à lire avec celle-ci, qui le
remplace.

**Verdict : conforme. Un écart faible** (§ 1). Les quatre citations sont exactes. Les
seuils en mois, refaits à la main, sont justes, sauf une case laissée vide. Les deux
défauts sont déclarés, dans la fiche et dans les limites. La cessation de 2012 est au
bloc « Reprise ». Aucune valeur du modèle ne bouge. Les 328 tests rapides des fiches et
des règles passent.

## 1. L'effet du forfait de début, au mois près (écart 1 de R-D2)

- **Les données.**
  - Minimum : 200 heures du Smic du 1er janvier, lu dans `smic_horaire_releves.csv` :
    7,19 € (relevé du 1er juillet 2003), 7,61 €, 8,03 €, 8,27 €, 8,44 €, soit 1 438 €,
    1 522 €, 1 606 €, 1 654 € et 1 688 € de 2004 à 2008.
  - Plafond : 29 712 €, 30 192 €, 31 068 €, 32 184 €, 33 276 €
    (`plafond_securite_sociale.csv`).
  - Bases mensuelles : la série de D3, rouverte aux décrets (relecture de D3, § 1).
- **Le seuil, refait.** C'est le minimum divisé par le forfait d'un mois.

  | Année | Artisan, 1re (plafond / 36) | Artisan, 2e (/ 24) | Commerçant, 1re (18 BMAF / 12) | Commerçant, 2e (27 BMAF / 12) |
  |---|---|---|---|---|
  | 2004 | 1,742 | 1,162 | 2,757 | **1,838** |
  | 2005 | 1,815 | 1,210 | 2,870 | 1,913 |
  | 2006 | 1,861 | 1,241 | 2,963 | 1,975 |
  | 2007 | 1,850 | 1,233 | 2,997 | 1,998 |
  | 2008 | 1,826 | 1,217 | 3,008 | 2,005 |

  Chaque case de la note se retrouve à la troisième décimale. **Conforme**, sauf une
  case.
- **Écart, faible : la case de 2004, deuxième année du commerçant, est vide (« — »).**
  - *Ce que fait le modèle.* Il applique les 27 bases mensuelles en 2004 au commerçant
    qui a commencé en 2003. Les périodes du NRCO de 2004 portent `[18, 27]`, et une
    ligne `commercant` de 2003 compte pour une année d'exercice.
  - *La preuve.* Commerçant à 10 000 € en 2003, puis 11 000 €, rend en 2004
    27,0334 points du NRCO, soit 27 × 347,68 × 4 % / 13,89.
  - *Le texte* le veut ainsi : D. 635-10 vise « les assurés commençant l'exercice de leur
    activité », et L. 131-6 leur « deuxième année civile d'activité ».
  - *La valeur manquante.* La case vaut 1 438 / (27 × 347,68 / 12 = 782,28) = 1,838.
    Dans la fiche, « sous 1,91 à 2,01 mois » est donc à lire « sous 1,84 à 2,01 mois ».
  - *Sans effet sur la conclusion.* Le commerçant ne passe sous le minimum, la deuxième
    année, que s'il cesse en janvier, ou en février 2008. En 2004 aussi : un mois,
    782,28 €, sous 1 438 € ; deux mois, 1 564,56 €, au-dessus.
- **Les cas datés.**
  - Commerçant, première année : octobre 2008, 18 × 374,12 × 3 / 12 = 1 683,54 € sous
    1 688 €.
  - Commerçant, deuxième année : février 2008, 27 × 374,12 × 2 / 12 = 1 683,54 €.

  **Conforme.**

## 2. La cessation de 2012 (écart 2 de R-D2)

- **La citation.** Décret n° 2012-443, article 10, II (LEGIARTI000025628404), relu :
  exacte, à la lettre.
- **Le bloc « Reprise ».** Le bloc de l'action 177 la porte parmi les questions au
  propriétaire : « complémentaire et base, où un trimestre peut manquer ». **Conforme.**

## 3. Les articles qui fixent l'effet des bornes (écart 3 de R-D2)

Rouverts dans l'index LEGI :
- **1979 :** décret n° 78-351, article 12 (LEGIARTI000006766114) : « Pour l'obligation de
  cotiser, le 1er janvier 1979 ; Pour l'entrée en jouissance des prestations, le 1er
  avril 1979. »
- **2012 :** décret n° 2012-443, article 10 (LEGIARTI000025628404), son II.
- **2015 :** décret n° 2014-1637, article 31 (LEGIARTI000029982292), I : « Le présent
  décret s'applique aux cotisations et aux contributions de sécurité sociale dues au
  titre des périodes courant à compter du 1er janvier 2015. »
  - LEGI date cette rédaction du 1er janvier 2999, un artefact de l'index. La fiche lui
    donne le 1er janvier 2015, la date que le texte dit.
- **2016 :** décret n° 2015-1856, article 10 (LEGIARTI000031791772), I : « [...] à compter
  du 1er janvier 2016. »

Les quatre citations de la fiche sont exactes, aux `textes` des versions qu'elles
bornent. **Conforme.**

## 4. Les deux défauts déclarés

- **L'invalide exonéré.**
  - *La citation.* « l'assuré titulaire d'une pension d'invalidité dans les régimes
    institués par l'article L. 635-5 est exonéré du paiement de toute cotisation
    d'assurance vieillesse complémentaire ». Elle est exacte dans les rédactions de
    D. 635-2 de 2013 à 2020 (LEGIARTI000025263548 à LEGIARTI000034721550).
  - *Depuis 2020.* « dans le régime institués par l'article L. 632-1 », faute comprise
    (LEGIARTI000041966510).
  - *Le défaut.* Que `pensionne` ne vise que le libéral est le constat de R-D2.
  - *La déclaration.* Approximation de la fiche, versions `rci_2013` à `rci_2016`, et
    limites. **Conforme.**
- **Le minimum au revenu nul.**
  - *Le code.* `carriere.py:729` (`if cotise and revenu > 0 and not micro:`) et
    `moteur/js/carriere.js:710` (`if (cotise && revenu > 0 && !micro)`), lus.
  - *La déclaration.* Fiche, de la version de 1979 à `rci_2015`, et limites.
    **Conforme.**

## Sources ouvertes dans la session

- **Index LEGI** de la DILA (2 novembre 2026) : LEGIARTI000006766114,
  LEGIARTI000025628404, LEGIARTI000029982292, LEGIARTI000031791772 ; D. 635-2, ses
  rédactions de 2013 à 2020 (`--diff`).
- **Dépôt** : `smic_horaire_releves.csv`, `plafond_securite_sociale.csv`,
  `base_mensuelle_prestations_familiales.csv` ; la fiche `assiette_rco_independants` et
  `docs/limites/3-systeme-actuel.md` au commit 6585726 ; le moteur Python, sur un
  commerçant de 2003.
