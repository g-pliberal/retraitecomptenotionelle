# Retouches de la relecture R-D2 : l'effet du forfait borné au mois, les bornes prouvées, deux candidats déclarés (file D3)

**Le 5 novembre 2026, file D3.** La relecture R-D2 (`2026-11-05-relecture-de-d2.md`,
§ 5) jugeait le minimum de la cotisation complémentaire conforme, avec trois écarts
faibles et deux défauts vus hors de D2, que l'orchestration a confiés à la file D.
Chaque source a été rouverte ici ; aucune valeur du modèle n'en dépend, rien n'est
corrigé dans les moteurs.

## 1. L'effet du forfait de début face au minimum, au mois près (écart 1)

Le forfait, que le modèle prend à proportion des mois, ne passe sous le minimum,
200 heures du Smic du 1er janvier, que sous un seuil, en mois, que voici, de 2004 à
2008 : le minimum divisé par le forfait d'un mois. Plafonds de
`plafond_securite_sociale.csv`, Smic de `smic_horaire.csv`, bases mensuelles de
`base_mensuelle_prestations_familiales.csv`.

| Année | Minimum | Artisan, 1re année (PSS / 36 par mois) | Artisan, 2e (PSS / 24) | Commerçant, 1re (1,5 BMAF) | Commerçant, 2e (2,25 BMAF) |
|---|---|---|---|---|---|
| 2004 | 200 × 7,19 = 1 438 € | 1 438 / 825,33 = 1,742 | 1 438 / 1 238 = 1,162 | 1 438 / 521,52 = 2,757 | — |
| 2005 | 200 × 7,61 = 1 522 € | 1 522 / 838,67 = 1,815 | 1 522 / 1 258 = 1,210 | 1 522 / 530,39 = 2,870 | 1 522 / 795,58 = 1,913 |
| 2006 | 200 × 8,03 = 1 606 € | 1 606 / 863 = 1,861 | 1 606 / 1 294,50 = 1,241 | 1 606 / 542,06 = 2,963 | 1 606 / 813,08 = 1,975 |
| 2007 | 200 × 8,27 = 1 654 € | 1 654 / 894 = 1,850 | 1 654 / 1 341 = 1,233 | 1 654 / 551,81 = 2,997 | 1 654 / 827,71 = 1,998 |
| 2008 | 200 × 8,44 = 1 688 € | 1 688 / 924,33 = 1,826 | 1 688 / 1 386,50 = 1,217 | 1 688 / 561,18 = 3,008 | 1 688 / 841,77 = 2,005 |

L'artisan n'y passe donc qu'avec un seul mois au forfait : la première année s'il
commence en décembre, la seconde s'il cesse en janvier ; le commerçant, la première
année s'il commence en novembre ou en décembre, ou en octobre 2008 (18 × 374,12 € sur
trois mois, 1 683,54 € sous 1 688 €), la seconde s'il cesse en janvier, ou en février
2008 (27 × 374,12 € sur deux mois, 1 683,54 €). Les seuils de l'artisan sont ceux de
la relecture. Écrit dans l'effet de l'approximation de la fiche
`assiette_rco_independants`, qui ne vaut plus que de 2004 à 2008
(`2026-11-05-forfaits-de-debut-des-independants.md`).

## 2. La cessation de 2012, à la base (écart 2)

Le décret n° 2012-443, article 10, II (LEGIARTI000025628404), relu : « Les
cotisations définitives dues au titre de l'année 2012 par les travailleurs
indépendants non agricoles qui cessent leur activité au cours de cette même année
demeurent régies par les dispositions du code de la sécurité sociale qui leur sont
applicables dans leur rédaction antérieure à la date de publication du présent
décret, sauf si ces personnes reprennent leur activité avant le 1er janvier 2013. »
Il vaut pour la base comme pour la complémentaire ; à la base, sous
quatre-vingt-dix jours, le minimum d'avant, 1 844 €, valide un trimestre que le
modèle peut ne pas donner. Inscrit au bloc « Reprise » de l'action 177, avec la
complémentaire, comme question au propriétaire, sans correction.

## 3. Les bornes, prouvées par leurs textes (écart 3)

Cités mot pour mot dans les `textes` de la fiche, chacun dans la version qu'il
ouvre : le décret n° 78-351, article 12 (LEGIARTI000006766114 : « Pour l'obligation
de cotiser, le 1er janvier 1979 »), dans `avant_derniere_annee_1979`, où il manquait
(il était dans `avant_1979`) ; le décret n° 2012-443, article 10, II
(LEGIARTI000025628404), qui place a contrario les cotisations définitives de 2012 de
tous les autres sous la rédaction nouvelle, dans `sans_forfait_2012` ; le décret
n° 2014-1637, article 31, I (LEGIARTI000029982292 : « Le présent décret s'applique
aux cotisations et aux contributions de sécurité sociale dues au titre des périodes
courant à compter du 1er janvier 2015 »), dont l'article 15 modifie D. 635-2, dans
`rci_2015` ; le décret n° 2015-1856, article 10, I (LEGIARTI000031791772 : « dues au
titre de la période courant à compter du 1er janvier 2016 »), dont l'article 1er
modifie D. 635-2, dans `rci_2016`.

## 4. Deux candidats, déclarés sans être corrigés

- *L'invalide exonéré de complémentaire.* D. 635-2, relu à ses rédactions de 2013 à
  aujourd'hui : « Par dérogation à l'alinéa qui précède, l'assuré titulaire d'une
  pension d'invalidité dans les régimes institués par l'article L. 635-5 est exonéré
  du paiement de toute cotisation d'assurance vieillesse complémentaire »
  (LEGIARTI000025263548, LEGIARTI000030034575, LEGIARTI000031799392,
  LEGIARTI000034721550) ; « dans le régime institués par l'article L. 632-1 » depuis
  le 25 mai 2020 (LEGIARTI000041966510) ; absent de la rédaction de 2012
  (LEGIARTI000025629861). La dispense `pensionne` du modèle ne vise que les libéraux
  (`dispenses_assiette_minimale.yaml`, `familles: [liberaux]`).
- *Le minimum au revenu nul.* Le minimum de la base, que celui de la complémentaire
  suit, tombe quand le revenu déclaré est nul (`carriere.py`, `if cotise and revenu > 0
  and not micro` ; `carriere.js`, `if (cotise && revenu > 0 && !micro)`) ; aucune des
  rédactions relues de D. 635-2 n'excepte cette année.

Déclarés à la fiche `assiette_rco_independants` (approximations) et à
`docs/limites/3-systeme-actuel.md`, inscrits au bloc « Reprise » comme candidats.
