# Étape 4, cinquième partie : le partage entre ex-conjoints et le remariage

**Le 9 octobre 2026, la demande.** La seconde moitié de celle du propriétaire
(note « assuré mort avant son départ ») : « puis le partage entre
ex-conjoints et le remariage ». La saisie ne connaissait qu'un conjoint, et
la fiche du régime général déclarait le partage absent ; le ménage déclaré
n'avait pas de date.

**Ce que dit le droit, lu le jour même** (journal de veille du 9 octobre ;
les huit fiches de réversion).

- *Le régime général.* L. 353-3 : la réversion « est partagée entre son
  conjoint survivant et le ou les précédents conjoints divorcés au prorata de
  la durée respective de chaque mariage » — les « non remariés » seuls
  jusqu'en 2003 —, et la part d'un bénéficiaire qui meurt « accroîtra » celle
  des autres ; R. 353-4 : la durée, « déterminée de date à date, est arrondie
  au nombre de mois inférieur », et, jusqu'en 2004, chaque mariage a duré deux
  ans, sauf enfant. La circulaire n° 105/90, § 3, réduit le minimum et le
  maximum dans la même proportion ; l'exposé de la Cnav « Existence
  d'ex-conjoint(s) » fige le partage au calcul de la première réversion. Le
  remariage du survivant ne retire rien : seul le ménage compte au plafond.
- *La fonction publique et la CRPCEN.* L. 45, puis L. 43 depuis 2012 : la
  pension « répartie entre ces conjoints au prorata de la durée respective de
  chaque mariage » ; L. 46 : le conjoint, survivant ou divorcé, « qui
  contracte un nouveau mariage ou vit en état de concubinage notoire, perd son
  droit à pension ». La CRPCEN renvoie à L. 43 à L. 46.
- *Les complémentaires et les régimes spéciaux.* L'Ircantec (articles 20 et
  22 de l'arrêté de 1970) et les IEG (annexe 3, articles 22 et 25) partagent
  avec les ex-conjoints non remariés et retirent la réversion au remariage ;
  la complémentaire des indépendants (article 22 du règlement) partage avec
  tous, comme le régime général ; le RAFP (article 4 de l'arrêté de 2004)
  suspend au remariage ou au concubinage notoire le paiement du conjoint,
  survivant ou divorcé, sans l'écarter du partage. La fédération Agirc-Arrco :
  partage au prorata des mariages, retrait « définitif » au remariage, ni
  PACS ni concubinage ; et la réversion entière au conjoint marié avant le
  13 janvier 1998 quand le mariage précédent du défunt a été dissous avant le
  1er juillet 1980. Le texte de l'accord, sur le site de la fédération, est
  refusé par son filtre ; sa page se lit.
- *Destinie 2* (`Retraite.cpp:253-334`, au commit `4c1d34b`) compte des
  années de mariage, ne partage les régimes de base qu'entre conjoints
  vivants, l'Agirc-Arrco entre tous, et retire l'Agirc-Arrco au remarié.

**Ce qui est fait.**

- *La saisie* (deux moteurs) : deux précédents conjoints au plus (`ex1`,
  `ex2`), chacun par sa naissance, son mariage, son divorce et, s'il le dit,
  son remariage ; le mois où commence l'union nouvelle du survivant
  (`nouvelle_union_depuis`). Elle refuse une ligne incomplète, des dates dans
  le désordre, un mariage avec le conjoint avant le dernier divorce, une union
  nouvelle avant le décès ; l'adresse garde tout.
- *La chronologie* : chaque précédent conjoint est une personne, avec sa
  naissance, l'union datée que le divorce clôt, et le ménage de son
  remariage ; le ménage du survivant prend la date de son union.
  `Carriere.ex_conjoints` les lit.
- *Le modèle* (`droit/reversion.py` et son jumeau) : la part du survivant,
  son mariage jusqu'au décès rapporté à tous ceux qui partagent, en mois
  (`mois_de_mariage`, `_part_du_survivant`) ; qui partage, au régime général
  selon la date (`_admis_au_regime_general`), ailleurs selon la fiche
  (`ex_conjoints` : `tous`, `non_remaries` ou `aucun`) ; la réversion entière
  de l'Agirc-Arrco quand ses deux dates le disent (`entiere_au_conjoint`) ;
  la ligne arrêtée au mois qui suit l'union nouvelle dans les régimes qui la
  retirent à cette forme d'union (`perte_au_remariage`), nulle quand l'union
  précède la date d'effet. Le minimum et le maximum du régime général se
  partagent comme la réversion ; le ménage ne compte au plafond que formé à la
  date d'effet. La ligne dit sa part (`part`) et sa fin (`fin`).
- *La page* : le formulaire demande les précédents conjoints, repliés dans le
  bloc du conjoint ; la carte dit la part, « au prorata des mariages », et la
  fin que l'union nouvelle impose.
- *Les fiches* : les huit fiches de réversion portent `ex_conjoints` et
  `perte_au_remariage` par version, citent leurs textes, et déclarent ce qui
  reste ; le registre reprend le point de Destinie et celui d'Aphrodite ; les
  limites et le tableau de l'architecture.
- *Les tests* (`test_reversion.py`) : la durée en mois, le partage, le
  précédent conjoint remarié, la règle d'avant 2004, l'Agirc-Arrco entière,
  le RAFP partagé avec le remarié, le remariage et le concubinage, l'adresse,
  la page ; deux témoins de simulation, `reversion_partage_et_remariage` et
  `reversion_fonctionnaire_partage_concubinage`, les deux moteurs au bit près.

**Les mesures.** Aucune pension ni réversion des témoins ne bouge : celles du
conjoint gagnent les champs `part` et `fin`. La veuve d'un salarié né en 1958,
mariée 215 mois, dont le mari l'avait été 120 mois à une première épouse,
remariée, puis 164 à une seconde, reçoit 43,1 % de la réversion du régime
général (215/499), 4 190,99 euros au lieu de 8 441,60, et 56,7 % de celle de
l'Agirc-Arrco (215/379), qui s'éteint au 1er avril 2026, après son remariage
de mars : 6 491,76 euros en tout la première année, au lieu de 12 497,37. La
veuve d'un fonctionnaire, mariée 275 mois après un premier mariage de 180,
reçoit 60,4 % de la moitié de sa pension civile et de son RAFP, 7 383,30 euros
au lieu de 12 216,01, jusqu'au 1er octobre 2024, son concubinage notoire de
septembre les éteignant.

**Ce qui reste.**

1. *De l'étape 4* : L. 353-5 et D. 355-1, avec lesquelles les retraites
   personnelles du survivant sortiront de ses ressources d'avant juillet
   2004 ; les majorations forfaitaires d'avant 1995 et 1982.
2. *Du partage* : la part qui « accroîtra » celle des autres au décès d'un
   bénéficiaire, et la révision au fil du temps (R. 353-1-1, R. 353-4) ; plus
   de deux précédents conjoints ; leur propre réversion ; la condition de
   mariage qu'ils remplissent dans la fonction publique, l'Ircantec et les
   IEG ; les lits d'orphelins de L. 43 ; l'ex-conjoint seul de l'Agirc-Arrco
   (article 112) ; la part non demandée des IEG (article 26) ; la date de
   mariage dite par l'année, que la Cnav présume au 31 décembre.
3. *Du remariage* : le droit que le survivant recouvre quand sa nouvelle
   union cesse (L. 46, Ircantec, IEG, RAFP) ; l'union formée après la date
   d'effet, qui révise la réversion du régime général par son ménage.
