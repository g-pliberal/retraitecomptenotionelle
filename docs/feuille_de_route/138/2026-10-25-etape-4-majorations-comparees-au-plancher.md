# Étape 4, seizième partie : les majorations forfaitaires de 1972 à 1982 comparées au plancher — la pension des cotisations majorée, le minimum des pensions et l'AVTS sans elles, la pension d'invalidité relevée en 1982

**Le 25 octobre 2026, la demande.** Le propriétaire, dans la neuvième vague des
sessions : le premier point sans propriétaire du bloc de l'étape, les majorations
de 1972 à 1982 comparées au plancher de la pension substituée. La date de la
demande et celle du décès, avant juillet 2004, viendront dans une session suivante ;
les décrets agricoles de 1976 et 1977, au fac-similé, restent au propriétaire, et ce
que le bloc renvoie au site, au site.

**Ce que dit le droit, lu le jour même** (journal de veille du 25 octobre,
« majorations comparées au plancher » ; fiche `majorations_forfaitaires_1972_1982`).

- *Les circulaires*, relues en entier par la recherche de la base de la Cnav :
  « La majoration forfaitaire de 5 % s'applique uniquement à la pension de
  vieillesse résultant des cotisations. En conséquence, pour les ex-invalides, une
  nouvelle comparaison devrait, en principe, être faite entre cette pension de
  vieillesse majorée et la pension d'invalidité afin de servir le montant le plus
  élevé, comparaison qui nécessiterait la reprise de tous les dossiers » (n° 2/72,
  IV, B ; n° 15/76 et n° 64/77, B ; n° 79/82, B). Par simplification, le deuxième et
  le troisième groupe, à 50 % du salaire annuel moyen, n'ont pas les 5 % de 1972, 1976
  et 1977, ni les 5,5 % et 1,5 % de 1982 ; le premier, à 30 %, les a d'office ; « en
  cas de réclamation, les redressements nécessaires devront être effectués lorsque
  l'assuré y aura intérêt ». Les 6 % et les 4 % de 1982, « notamment destinées à
  compenser le calcul du salaire annuel moyen », vont à « tous les ex-invalides (quel
  que soit leur groupe) » (n° 79/82, B, 1°). La majoration « ne joue pas [...] sur le
  minimum des pensions » (n° 2/72, n° 15/76, n° 64/77, A).
- *L'exposé* « Montant de la retraite personnelle » (6 mars 2026) le redit : « Ces
  majorations s'appliquaient au montant de base, avant comparaison au minimum et au
  maximum » ; « Les titulaires de retraites substituées à des pensions d'invalidité de
  2e et 3e catégories ont bénéficié seulement des majorations de 6 % et 4 % au
  01/12/1982 ».
- *Aucun exemple chiffré* ne compare une pension majorée à un plancher.

**Ce qui est fait.**

- *La classe, non le cas* : la règle vaut pour tout plancher que les majorations ne
  relèvent pas — le plancher de la pension substituée, et la pension minimum d'avant
  le 1er avril 1983 (L. 345), que le modèle majorait de même.
- *La fiche* dit de chaque majoration les planchers qu'elle relève (`planchers`) :
  la pension d'invalidité pour les 6 % et les 4 % de 1982, aucun pour les autres.
  Le paquet refait sur les agrégats de `main` les porte : seuls y changent les
  planchers des neuf majorations.
- *La liquidation* (`droit/completer.py`, et son jumeau) écrit sur la pension les
  planchers auxquels elle l'a comparée — `minimum`, `avts`,
  `pension_d_invalidite` — et la pension d'avant eux (`PensionRegime.planchers`,
  `avant_les_planchers`).
- *« Faire vivre »* (`revalorisation.plancher_non_majore`, `plancherNonMajore`) sert
  la plus haute de la pension d'avant les planchers, majorée, et de chaque plancher,
  de ses seules majorations, tous revalorisés comme les pensions : ce que le
  coefficient porte de trop se retire (`RegimeServi.plancher_non_majore`, au schéma
  de l'étape, et au détail de la composante de l'échéance). Le modèle compare donc,
  comme la réclamation le faisait ; la simplification de la caisse donne le même
  montant tant que la pension des cotisations, majorée, reste sous la pension
  d'invalidité des deuxième et troisième groupes et au-dessus de celle du premier.
  La majoration pour enfants suit la pension servie, en décembre 2019 comme à
  l'échéance ; la réversion, calculée « avant comparaison au minimum », garde la
  pension des cotisations, majorée.
- *Les tests*, posés à la main depuis les circulaires et vus rouges :
  l'ex-invalide de 1969 de deuxième catégorie, tenu pour liquidé sur la durée
  maximum, servi à son plancher sans les trois 5 %, puis relevé des 6 % de 1982 ; en
  première catégorie, ses quatre majorations ; l'ex-invalide porté à l'AVTS, que les
  6 % de 1982 ne relèvent pas (`test_invalidite.py`) ; la pension de 1970 portée à la
  pension minimum, de même (`test_pension_minimum_avant_1983.py`) ; les deux moteurs
  confrontés sur trois saisies, au niveau `complet`, le portage lisant le paquet.
- *Les fiches* : `majorations_forfaitaires_1972_1982` — la règle, ses lectures,
  l'écart de l'ex-invalide récrit, celui du maximum ouvert, l'historique ;
  `pension_d_invalidite_substituee` et `minimum_contributif`, leur historique ; la
  page des limites.

**Les mesures.** Aucun des 907 témoins de simulation ne bouge, ni aucun rendu de
page : un seul porte un plancher, l'ex-invalide substitué en 1980, que nulle
majoration ne relève. Sur les saisies confrontées, en 2026 : l'ex-invalide de 1969
porté à l'AVTS reçoit 185,76 € de moins par an du régime général, et le retraité de
1970 porté à la pension minimum 183,99 € de moins, que l'ASPA leur rend à l'euro près ;
l'ex-invalide relevé par sa pension d'invalidité ne bouge pas. Une pension d'avant
1975 sur la durée maximum, qui ferait jouer les majorations de 1972 à 1977, n'est à la
portée d'aucune carrière du modèle, que le régime général compte depuis 1945.

**Ce qui reste.**

1. *Le maximum* : la pension ramenée au maximum à sa liquidation, que la caisse
   majorait sur son montant entier avant de la ramener au maximum de l'année, et que
   le modèle majore sur son montant ramené (l'écart neuf de la fiche).
2. *Le minimum des pensions et l'AVTS*, que le modèle revalorise comme les pensions :
   suivaient-ils chaque décret de l'AVTS, pour les pensions servies ? Au fac-similé
   (la question de la fiche).
3. *Au site* : la phrase de la carte qui dirait le plancher que les majorations ne
   relèvent pas (`plancher_non_majore`).
