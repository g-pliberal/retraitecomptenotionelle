# Étape 4, première partie : le minimum et les majorations de la réversion du régime général

**Reprise, au 9 octobre 2026.** Fait : le minimum de D. 353-1, la majoration
de 10 % du survivant de trois enfants et celle de 11,1 % (L. 353-6), dans les
deux moteurs, sur deux séries de la Cnav ; Destinie 2 concorde au centime ; la
base de la réversion sans le minimum contributif ; le maximum, surcote en sus,
sur la pension d'avant le maximum des pensions (note du 9 octobre). Reste, dans
cet ordre : le plafond du ménage ; la réversion d'un assuré mort avant son
départ ; le partage entre ex-conjoints et le remariage ; L. 353-5 et D. 355-1.
Commencer par le plafond du ménage, 1,6 fois celui d'une personne seule, quand
le survivant vit en couple, ce que la saisie ne dit pas encore. Détail : plus
bas, « Ce qui reste », « La base », et la note du 9 octobre.

**Le 7 octobre 2026, la demande.** Le propriétaire : « Quels sont les écarts
encore présents avec trajectoire et destinie 2 ? J'aimerais combler les manques
de notre modèle. » Le registre des modèles et les deux confrontations exécutées
(`tests/test_destinie.py`, `tests/test_trajectoire.py`) les disent : du côté de
Destinie, la réversion du régime général, que le dépôt servait sans minimum ni
majorations, était le plus gros écart que le dépôt avait tort de porter (−41 %
sous le minimum, −47 % avec la majoration de 11,1 %, −9,6 % pour la survivante
de trois enfants). C'est l'étape 4 de l'action ; elle commence par là.

**Ce que dit le droit, lu le jour même** (journal de veille du 7 octobre).

- *Le minimum* (D. 353-1) est entier quand le défunt a soixante trimestres
  d'assurance au régime général, et au régime des indépendants depuis 2020 ;
  « réduit à autant de soixantièmes » en deçà, depuis le 1er décembre 1982 —
  avant, la réversion était portée au minimum entier ; depuis le 1er juillet
  2004, quand les régimes alignés comptent ensemble plus de soixante
  trimestres, chacun le sert au prorata de sa durée (exposé de la Cnav,
  circulaires n° 2005-17 et 2008-42). La caisse porte la réversion au minimum,
  puis la réduit du dépassement du plafond de ressources. Le montant est
  l'ancienne allocation aux vieux travailleurs salariés : D. 353-1 ne l'écrit
  qu'en 2026, et le barème de la Cnav en porte chaque date depuis la loi du
  14 mars 1941.
- *L'exception de juillet 2012* : le minimum « n'est pas applicable aux
  pensions de réversion issues d'une pension dont le montant est inférieur au
  minimum prévu à l'article L. 351-9 » (L. 353-1). La fiche y lisait le minimum
  contributif — un paramètre que le moteur ne lisait pas, et qui, appliqué,
  aurait privé du minimum la réversion de toute petite pension. L. 351-9 est le
  versement forfaitaire unique, sous 175 francs par an en 1974 (R. 351-26) : le
  paramètre est retiré, l'exception déclarée, son effet de quelques dizaines
  d'euros.
- *La majoration de 10 %* du survivant de trois enfants s'ajoute à la
  réversion réduite, hors du plafond : « 10 % du montant non majoré de la
  retraite de réversion » (circulaire n° 2022-26, § 3.6, et son exemple) ; elle
  « ne peut être inférieure au dixième du montant minimum » (R. 353-2), que le
  modèle lit comme le minimum de cette réversion, soixantièmes faits — la
  lecture que l'exemple de la circulaire laisse ouverte. Le registre
  reprochait à Destinie de ne pas l'opposer au plafond : c'est ce que fait la
  caisse, et le reproche est retiré.
- *La majoration de 11,1 %* (L. 353-6, D. 353-4) : au survivant qui a l'âge du
  taux plein, quand ses retraites et réversions, de base et complémentaires,
  majorations pour enfants comprises, ne dépassent pas le plafond — 2 400 € par
  trimestre en 2010, revalorisés comme les pensions —, 11,1 % de la réversion
  réduite, « réduite à due concurrence du dépassement », partagée entre
  régimes au prorata de leurs réversions ; due au premier jour du mois qui suit
  l'âge du taux plein (R. 353-13), dès l'anniversaire pour qui est né le
  premier d'un mois, jamais avant 2010.

**Ce qui est fait.**

- *Les données.* `scripts/fetch/cnav_reversion.py` lit deux barèmes de la
  Cnav et refuse d'écrire s'ils ne redonnent pas les montants des articles
  (3 983,29 € en 2025, 2 400 € en 2010) ou si le plafond ne garde pas avec le
  minimum le rapport de 2010 ; `legislation/minimum_reversion.csv` (1941-2026,
  francs et anciens francs convertis) et `plafond_majoration_reversion.csv`
  (2010-2026), une ancre au 31 décembre, niveau `haute`, certifiées par
  `verifier_donnees.py` ; `data/sources.yaml`, `cnav_reversion`.
- *Le modèle* (`droit/reversion.py`, son jumeau `reversion.js`) : le minimum,
  proratisé sur la durée du défunt dans chaque régime, que l'échéancier compte
  à ses départs (`durees_au_depart`), et, sous la liquidation unique, sur celle
  de tous les régimes qu'elle réunit — la pension d'un salarié passé du privé
  à l'agriculture, que la Lura sert d'un seul régime, en aurait reçu la
  moitié ; la majoration de 10 % ; celle de 11,1 %,
  une fois toutes les réversions chiffrées, comprise dans le montant quand elle
  commence à la date d'effet de la ligne, écrite à part avec sa date sinon.
  Chaque ligne dit son minimum et ses deux majorations ; le paquet du site
  porte les deux séries. La carte de la réversion sur le site dit ces parts,
  et la réserve qui disait le minimum absent est remplacée par celles qui
  restent vraies : un conjoint qui vivrait seul, sans ex-conjoint.
- *Les mesures.* Destinie 2 : le minimum, 3 701,38 €, et la majoration de
  11,1 %, 4 112,23 €, au centime ; la survivante de trois enfants à −0,6 %,
  l'écart de la base de Destinie, déclaré. Sur les 737 témoins, aucune pension
  des six scénarios ne bouge ; trois réversions changent : les deux couples à
  l'ASPA, dont le défunt, aux petites pensions, voit sa réversion portée au
  minimum, et la contractuelle au mariage court, majorée de 11,1 %. Les
  témoins de réversion portent les champs nouveaux.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La base sans le minimum contributif* — faite le jour même, plus bas. La
   Cnav calcule la réversion sur la
   pension « avant comparaison au minimum et au maximum », surcote comprise ; le
   modèle y garde le minimum contributif, que `completer.py` ajoute à la ligne
   du régime. Il faut la part du minimum par régime (`par_regime` de
   l'avantage, dans les deux moteurs), menée comme la pension jusqu'au décès
   (`_pensions_au_deces`), puis ôtée de la base. Effet : jusqu'à −31 % pour la
   réversion d'une carrière complète au minimum majoré de 2025.
2. *Le maximum* : 54 % du maximum des pensions (barème de la Cnav, 12 976,20 €
   en 2026), 54 % de la surcote en sus, non ramenée (circulaire n° 2018-4,
   § 5) — fait le 9 octobre, note du jour.
3. *Le plafond du ménage* (1,6 fois celui d'une personne seule), quand le
   survivant vit en couple ; l'abattement de 30 % de ses revenus d'activité
   après cinquante-cinq ans (R. 353-1).
4. *La réversion d'un assuré mort avant son départ* : la pension qu'il « eût
   obtenue », au taux de 50 % (R. 353-6).
5. *Le partage entre ex-conjoints* au prorata des mariages (L. 353-3), le
   remariage ; puis L. 353-5 et les limites de cumul d'avant 2004 (D. 355-1),
   dont le barème de la Cnav porte la limite forfaitaire.
6. Les majorations forfaitaires des réversions d'avant 1995 (3,846 %) et
   d'avant décembre 1982 (4 %), que l'exposé de la Cnav décrit, à vérifier dans
   l'échéancier.

**Le 7 octobre 2026, la base.** La réversion est « un pourcentage fixé par
décret de la pension principale » (L. 353-1, ses cinq rédactions depuis 1985),
et le minimum contributif une « majoration permettant de porter cette
prestation à un montant minimum » (L. 351-10, ses six rédactions) : la Cnav
prend « le montant calculé de la retraite de l'assuré décédé, avant
comparaison au minimum et au maximum », revalorisé jusqu'au départ de la
réversion (exposés relus le jour même par son API). L'avantage du minimum
contributif porte désormais sa part dans chaque régime (`par_regime`, dans les
deux moteurs) ; l'échéancier la mène au décès comme la pension qui la porte
(`_pensions_au_deces`), et la réversion du régime général et des régimes
alignés multiplie la pension sans elle. La ligne de réversion la dit
(`minimum_contributif`), et la carte du site aussi, dans la cellule de la
pension. Aucune pension des six scénarios ne bouge, ni aucune réversion des
737 témoins : aucun de leurs défunts n'avait le minimum contributif. Un témoin
neuf, `reversion_minimum_contributif` — le petit salaire parti au taux plein à
soixante-sept ans en 2022, mort en 2024 —, reçoit 4 112,94 € par an au lieu
de 5 856,46 € (−29,8 %), les deux moteurs au bit près ; Destinie ne bouge pas,
ses deux défunts au minimum contributif laissant une réversion portée au
minimum de D. 353-1. Sous des départs échelonnés, le montant de l'avantage suit
désormais le coefficient de son régime, et non leur moyenne : aucun témoin ne
le montre.
