# Étape 18, troisième partie : les points d'avant 1973 des artisans et des commerçants

**La demande.** La session n° 7 du 14 octobre 2026 : « action 138, étape 18,
les points d'avant 1973 des artisans et des commerçants, par quoi le bloc de
l'étape dit de commencer, dans les deux moteurs, texte en main ». La saisie des
PCV reste à la session du site, les classes des libérales à la session 16.
`pages.js`, `index.html`, `castypes.py`, `cout.py` et la saisie n'ont pas été
touchés.

**Ce que faisait le dépôt.** Les fiches `cancava` et `organic` portaient une
période en points de 1949 à 1972, au rendement estimé de 9 %
(`rendements_points.csv`). Mais la liquidation lit la période de la DATE
D'EFFET : un artisan parti en 2000 voyait ses années de 1955 à 1972 servies en
annuités de la pension alignée, comptées dans sa proratisation (« SR × 50 % ×
72/150 »), le rendement ne servant à rien.

**Ce que disent les textes**, lus le jour même dans l'index LEGI du dépôt.

- *La liquidation à part.* L. 634-3 : les prestations des périodes antérieures
  au 1er janvier 1973 « demeurent calculées, liquidées et servies dans les
  conditions définies par les dispositions législatives et réglementaires en
  vigueur au 31 décembre 1972 ». Ces dispositions sont des points : chez le
  commerçant, l'allocation est « le produit de la valeur du point de retraite
  […] par la somme des points acquis » (décret n° 66-248, art. 19) ; chez
  l'artisan, le nombre de points de chaque classe (décret n° 64-994, art. 26).
- *L'âge et la minoration.* L'article 3 du décret n° 73-937, six rédactions
  (1976, 1990, 1993, 2004, 2012, 2023) : liquidables à soixante ans puis à
  l'âge de L. 161-17-2 ; sans abattement avec 150, puis 150 à 160 par
  génération, puis 160, puis la durée de L. 351-1 dans tous les régimes de
  base ; sinon 2,5 % par trimestre manquant à la durée ou à soixante-cinq ans
  (puis à l'âge de L. 351-8, 1°), au plus petit des deux, et, depuis 2004, de
  2,5 % à 1,25 % selon la génération — la table de R. 351-27.
- *Les points.* L'artisan est rangé dans l'une de quinze classes, de 4 à 60
  points, selon son revenu de l'année précédente (décret n° 64-994, art. 4 et
  5), les seuils « fixés par décret » ; le commerçant OPTE pour la classe VI bis
  (20 points), VII (24) ou VIII (36), la VI bis s'il ne dit rien, et ne descend
  sous elle que sur demande (décret n° 66-248, art. 3, rédaction de 1971). Ni
  les seuils, ni les classes de 1949 à 1970, ni les tableaux d'assimilation ne
  sont dans l'index : le Journal officiel d'avant 1990 n'y est qu'en notices.
  Reste une équivalence que le droit en vigueur écrit, D. 634-8 : un revenu
  « à autant de fois un pourcentage dudit plafond que la dernière cotisation
  annuelle […] antérieurement au 1er janvier 1973 comporte de points », 3 % chez
  l'artisan, 5 % chez le commerçant (de même l'article 1er du décret n° 73-937).
- *La valeur du point.* Le barème de la Cnav depuis 2020 (10,7637 € et
  14,84302 € au 1er janvier 2026, circulaire 2025/29), les fiches « Valeur du
  point de retraite RVB » du RSI qu'il cite pour 1988 à 2019, l'IPP avant. Aucun
  exemple chiffré publié n'a été trouvé.

**Ce qui est fait**, en un envoi.

1. *Deux régimes neufs*, `cancava_avant_1973` et `organic_avant_1973` : une
   période qui acquiert (1949-1972, `points_maximum` de 33,33 et de 20 points
   au plafond, soit un point par 3 % et par 5 % du plafond, l'assiette
   plafonnée), puis quatre qui liquident, selon les rédactions de l'article 3
   (1973-1993, 1994-2003, 2004-2012, depuis 2013), au taux nul — le test des
   taux l'admet pour une période postérieure à la fermeture. Le routage
   (`affiliations.yaml`) y envoie les années d'artisan, de commerçant, de
   gérant de débit de tabac et de micro-entrepreneur de 1949 à 1972 ; la CANCAVA
   et l'ORGANIC commencent en 1973. Les mécanismes servaient déjà dans les deux
   moteurs : aucun code nouveau, ni en Python ni en JavaScript.
2. *La valeur du point*, à chaque date d'effet (`valeurs_service_datees.csv`) et
   au 31 décembre (`valeurs_point.csv`), artisans depuis 1973 et commerçants
   depuis 1960 : 121 valeurs annuelles, certifiées `haute` par un récupérateur
   neuf, `scripts/fetch/cnav_points_avant_1973.py` (contrôle
   `valeurs_point_avant_1973` de `verifier_donnees.py`, source
   `cnav_points_avant_1973`). L'IPP porte en 2011, pour les commerçants, la
   valeur des artisans : la fiche du RSI l'emporte.
3. *La fiche de règle* `points_avant_1973_independants`, `approchee` ; les deux
   points du registre (chantier 138.18, IPP et OpenFisca) passent à `repris`.
   Tests : `tests/test_independants.py` (routage, points, proratisation,
   minoration, jumeau JavaScript sur un artisan et un commerçant) ;
   `tests/test_oracle.py` lit désormais l'égalité de l'alignement sur les cinq
   profils entrés depuis 1973, et ce que deviennent les cinq autres.
4. *Ce que la suite a exigé ailleurs.* La cotisation maladie des pensions
   d'indépendants porte sur les deux régimes, et l'artisan d'avant 1973 garde
   sa famille dans l'histoire des prélèvements
   (`prelevements_historiques.yaml`, `maladie_des_pensions.py`,
   `prelevements_historiques.py`). Au coût, les deux régimes entrent dans le
   groupe LURA (`donnees/equilibre.py`), et le cliquet de la reconstitution du
   passé monte de 14,0 à 14,2 % (`test_cout.py` : −14,1 % en 2009). La pension
   minimum d'avant 1983 de l'étape 6, que l'autre session avait écrite sur la
   pension alignée entière, borne désormais le cumul avec la pension des droits
   d'avant 1973 (`complement_des_alignes`, jumelle en JavaScript ; son test
   compte la somme des deux). Deux comptes que la suite vérifie, hors des
   pages : le README dit 80 régimes, et `docs/parcours_presentation.md` recopie
   ceux de la page Données (136 639 valeurs, 166 séries, 114 régimes dont 80
   calculés), au jour du rebasage.

**Ce que montrent les mesures.**

- Un artisan à 80 % du plafond de 1960 à 2004, né en 1940, parti en 2005 : sa
  pension alignée passe de 150/150 à 128/150 (−1 722 €), ses 346,67 points en
  rendent 2 780 € ; sa pension de base monte de 11 739 à 12 798 €. Le même au
  commerce : 208 points, 2 300 €, la base à 12 317 €.
- De 1955 à 1972 seul, parti en 2000 : 480 points d'artisan, 3 501 € ; 288
  points de commerçant, 2 900 € ; les annuités en donnaient 3 828 €.
- Les cas types (`resumer_temoins.py`, scénarios 1, 3 et 5) : douze bougent,
  de −20,7 % (commerçant et micro-entrepreneur nés en 1925) à +3,4 % (artisan
  né en 1945). La génération 1925, qui a l'essentiel de sa carrière avant
  1973, perd le plus : sous le plafond, l'équivalence de D. 634-8 lui ouvre
  moins de points que la classe VI bis, imposée à qui ne demandait rien.

**Pour les pages**, que la session du site tient. Les douze cas types et
leurs rendus changent : GitHub refera les témoins. La page qui détaille la
pension montrera une ligne de plus, « Droits en points d'avant 1973 du régime
de base des artisans » (ou des industriels et commerçants), avec ses points et
leur valeur ; son libellé et son rangement sous la pension de base sont à
voir.

**Ce qui reste** de ce point, dans l'ordre du poids : lire au fac-similé du
Journal officiel, sur le poste du propriétaire, les seuils des classes des
artisans de 1969 à 1972, les tableaux d'assimilation de 1949 à 1968 (annexes du
décret n° 64-994) et les classes des commerçants avant 1971 (décret n° 66-248
d'origine, décret n° 71-239) ; alors seulement, remplacer l'équivalence par la
classe. Puis les points gratuits des années d'avant 1949, la bonification des
points acquis au 1er décembre 1962, la majoration pour ajournement d'avant
juillet 1984, la bonification des points de la mère sans période d'assurance
après 1972 (article 5), la liquidation avec la retraite anticipée (article 3
bis). Un
exemple chiffré de la Cnav manque.
