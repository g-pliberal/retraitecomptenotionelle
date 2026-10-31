# Étape 4 : les indépendants des DOM, l'exonération sous 390 € et l'abattement qui ouvre des droits

**Le 31 octobre 2026, ce qui est fait.** La lecture d'abord, puis la question
au propriétaire, qui a tranché : la limite mieux dite, la règle des 390 €
dans les deux moteurs, et deux étapes neuves à la feuille de route, la saisie
du département pour la session du site (étape 7) et les non-salariés de
Mayotte (étape 8).

1. *La lecture.* Dans l'index LEGI à jour du 30 octobre 2026, toutes les
   versions de L. 756-1 à L. 756-5 et de D. 756-1 à D. 756-9 : de 2000 à
   2016, L. 756-4 assied la cotisation de l'indépendant des DOM « pour la
   partie des revenus inférieurs au plafond de la sécurité sociale, sur une
   assiette égale à la moitié des revenus concernés » (LEGIARTI000006744204 à
   LEGIARTI000031324257) ; depuis 2017, un abattement de moitié, des trois
   quarts la troisième année, dégressif jusqu'à deux fois et demie le plafond,
   le RCI et l'invalidité-décès exceptés (LEGIARTI000033712488,
   LEGIARTI000037063454). D. 756-8 calcule la pension « compte tenu du revenu
   professionnel effectivement pris en considération pour le calcul de la
   cotisation ». La caisse, elle, tient l'abattement d'avant 2017 pour une
   exonération « génératrice de droits » : « La part exonérée lui ouvre des
   droits à hauteur de ce qu'il a versé » (exposé « Validation des périodes de
   cotisations », version du 13 novembre 2025), et son exemple valide sur
   1 715 € de cotisations, le revenu entier de 10 000 €, l'assuré qui en a
   payé 857,50 €. Le modèle, qui porte au compte le revenu entier, a donc ses
   droits ; `tests/test_outre_mer.py` rejoue l'exemple. Depuis 2017, la caisse
   ne dit pas ce que l'abattement ouvre, sauf pour le micro-entrepreneur, dont
   elle neutralise les taux réduits (circulaires 2024/23 à 2026/12).
2. *L'exonération.* L. 756-3 exonère « du versement de toute cotisation »
   l'artisan et le commerçant des DOM dont le revenu « ne dépasse pas un
   certain montant fixé par décret », L. 756-5, II, depuis 2017, de « toute
   cotisation d'assurance vieillesse » ; D. 756-7 fixe le montant à 2 500 F,
   puis à 390 € depuis 2002, D. 756-6 à 390 € depuis 2017 ; la caisse : « Il
   ne bénéficie d'aucun droit à retraite ». Le modèle lui donnait l'assiette
   minimale. `_ligne_annuelle` et `ligneAnnuelle` exonèrent désormais la
   ligne de l'artisan, du commerçant ou du gérant d'un débit de tabac qui
   porte un département d'outre-mer et dont le revenu, positif, ne dépasse pas
   le montant de `exoneration_independants_outre_mer.csv` : l'assiette
   minimale tombe, et l'année ne verse pas de cotisation
   (`cotisations_versees`), si bien que rien n'en va au salaire annuel moyen,
   aux points ni au compte notionnel. La table part de 1986 : le décret
   n° 75-1098 du 25 novembre 1975, que D. 756-7 codifie, n'a dans l'index du
   JORF que son sommaire. Elle ne nomme pas le libéral non réglementé, que
   L. 631-1 vise depuis 2018 sans que son statut le distingue de celui de la
   CNAVPL. Trois cas posés depuis les textes, que le cas des deux moteurs
   reprend ; le paquet passe en version 38.
3. *La limite et les registres.* La limite « indépendants des DOM »
   (`docs/limites/3-systeme-actuel.md`) est récrite : ce que le modèle sert,
   l'abattement qui ne change rien aux droits, puis ce qu'il ne sert pas — les
   droits de l'assuré qui ne paie pas toute la cotisation appelée, la base de
   l'avant-dernière année de 2001 à 2016, l'exonération du créateur,
   l'abattement depuis 2017, le RCO et le NRCO réduits de 2010 à 2012. Le
   test des barèmes redit l'assiette minimale moitié moindre de 2009 à 2016 :
   celle de la cotisation appelée, l'écart des droits ne restant qu'en 2012.
   La fiche neuve `exoneration_independants_outre_mer` ; au registre de la
   Cnav, l'exemple génératrice de droits `recoupe`, celui du créateur et les
   deux barèmes des indépendants de Mayotte `limite`. Le `manque` de la fiche
   `cssm_mayotte` dit leur trimestre validé par un montant de cotisations.

**Ce que le calcul en reçoit.** Mesuré au moteur Python avant et après la
règle : l'artisan de La Réunion qui déclare 300 € en 2010 validait un
trimestre sur 1 772 € d'assiette minimale, et n'en valide plus aucun ;
l'artisane de La Réunion née en 1955, à 15 000 € par an de 1985 à 2014 puis à
300 € en 2015, partie à soixante-deux ans, touche 7 508,18 € par an au lieu de
7 597,79 €. Aucun des témoins de simulation ne porte de département
d'outre-mer : aucun ne bouge. La saisie du site ne portant pas le
département, la règle n'y joue pas encore (étape 7).

**Vu en chemin, non corrigé.**

- La caisse date les 390 € « à compter de 2001 » ; D. 756-7 garde 2 500 F
  jusqu'au 1er janvier 2002, soit 381,12 € : la table suit le décret.
- La règle du chômage non indemnisé de `carriere.py` lit
  `cotisations_versees` pour dire si l'assuré a « retravaillé » : une année
  exonérée qui suit la série compte comme une année sans reprise. Un cas de
  plus que rare, laissé.
- L'exposé « Validation des périodes de cotisations » reste `a_lire` au
  registre de la Cnav : il porte aussi les salariés, dont l'étape n'a lu que
  ce que les DOM touchent.
- D. 756-6 nomme Saint-Pierre-et-Miquelon, dont le modèle ne route pas les
  indépendants ; la limite le dit.

**L'étape est faite.** La suite : l'étape 5, l'assiette d'avant 2007 (la
fiche `cotisation_vieillesse_independants`, à relire puis à trancher) ;
l'étape 7 revient à la session du site, l'étape 8 au modèle.
