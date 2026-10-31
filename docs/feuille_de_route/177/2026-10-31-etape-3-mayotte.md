# Étape 3 : Mayotte, les trimestres au Smig mahorais et le salaire annuel moyen au plafond de la caisse

**Le 31 octobre 2026, ce qui est fait.** La fiche `cssm_mayotte` validait les
trimestres au Smic national et plafonnait le salaire annuel moyen au plafond
de la Sécurité sociale, faute de série ; `mayotte_smig_et_plafond.csv`, que
l'étape 2 de l'action 175 a tirée des barèmes de la Cnav, les lui donne. Deux
comportements, un par commit, chacun vu rouge d'abord, dans les deux moteurs.

1. *La validation.* Lus dans l'index LEGI à jour du 30 octobre 2026 :
   l'article 3 du décret n° 87-175 (LEGIARTI000006770151) et l'article 8 du
   décret n° 2003-589 dans ses quatre rédactions — « autant de trimestres que
   le salaire annuel correspondant aux retenues [...] représente de fois le
   montant du salaire minimum garanti en vigueur à Mayotte au 1er janvier de
   l'année considérée, calculé sur la base de 200 heures, avec un maximum de
   quatre trimestres par année civile » (LEGIARTI000006781027,
   LEGIARTI000026514455) ; 150 heures « pour les périodes postérieures au
   31 décembre 2016 » (LEGIARTI000033155442) ; depuis 2018, du « salaire
   minimum de croissance en vigueur à Mayotte » (LEGIARTI000048241292, du
   22 octobre 2023). La règle suit l'année de la période, et aucune rédaction
   ne revient sur une année passée. Les heures vont dans
   `validation_trimestres_mayotte.csv` ; `DonneesMacro.trimestres_valides` et
   `seuil_d_un_trimestre` prennent `mayotte`, que portent les statuts routés
   au régime (`statuts_de_mayotte`), et leurs jumeaux de même. Le Smig se
   prolonge au-delà de 2026 comme le Smic (`_prolonger_par_salaire`, tiré de
   `smic_horaire`). Avant 2002, faute de série, le Smic national reste.
2. *Le plafond.* L'article 7 du décret n° 2003-589 calcule le salaire annuel
   moyen sur les salaires « reportés au compte de l'assuré dans la limite du
   plafond annuel de cotisations mentionné au II de l'article 19 de
   l'ordonnance » (LEGIARTI000006781026, LEGIARTI000026514457,
   LEGIARTI000033155445). L'article 19 de l'ordonnance n° 2002-411 assied les
   cotisations « dans la limite d'un plafond » qu'un décret fixe
   (LEGIARTI000006698330) ; depuis 2012, l'ordonnance n° 96-1122 crée « un
   plafond de cotisations de sécurité sociale à Mayotte » (article 28-1,
   LEGIARTI000025018554 ; article 28-2, LEGIARTI000025018560). L'article 21
   du décret le fixe à 825 € par mois pour les rémunérations de 2003,
   revalorisé comme le Smig « majoré de trois points » (LEGIARTI000006781041),
   puis à 1 070 € « à compter du 1er janvier 2011 », revalorisé comme le
   plafond de la métropole « majoré de cinq points et un dixième »
   (LEGIARTI000023019089, LEGIARTI000026514398) : la série de la caisse a
   1 070 € en 2011, et la règle en redonne chaque année depuis à moins d'un
   euro par mois, sauf 2024 (2 644 € pour 2 645,39 €).
   `DonneesMacro.plafond_de_cotisations(annee, mayotte)` le rend depuis 2005,
   prolongé comme le plafond de la Sécurité sociale, et `salaire_de_reference`
   l'oppose au régime de Mayotte (`REGIME_DE_MAYOTTE`), son jumeau de même ;
   `charger_serie_annuelle` apprend à sauter une cellule vide
   (`sauter_les_vides`), le plafond commençant en 2005 et le Smig en 2002.

Le paquet du site passe en version 36, puis 37 : deux séries de plus, puis
une troisième. `tests/test_mayotte.py` pose trois cas depuis les textes et la
série : une salariée dont 1 100 € valident deux trimestres en 2002 (aucun au
Smic national), 4 750 € quatre en 2010 (deux), 2 910 € un seul en 2016 (deux :
200 heures du Smig font plus que 150 du Smic), 2 220 € deux en 2017 (un) et
5 400 € quatre en 2025 (trois) ; une autre, à 25 000 € en 2005, 2011, 2016,
2020 et 2024, dont le salaire annuel moyen s'écrête à 10 944 €, 12 840 €,
17 904 € et 23 208 € les quatre premières années, 20 762,09 € au lieu de
29 630 € ; la même sur son relevé, dans les deux moteurs. Les deux cas à
deux moteurs passent par la fixture `deux_moteurs`, que la garde des
présomptions saute.

**Ce que le calcul en reçoit.** Mesuré au moteur Python avant et après
l'étape : la salariée née en 1962, à mi-temps au Smig mahorais de 2002 à 2025
et partie à soixante-quatre ans, valide 96 trimestres au lieu de 75, et sa
pension passe de 1 208,00 € à 1 546,24 € par an ; celle née en 1961, à
25 000 € par an de 2005 à 2024, a un salaire de référence de 20 069,09 € au
lieu de 29 947,50 €, et sa pension passe de 5 823,13 € à 3 902,32 € ; au Smig
à temps plein, la salariée née en 1965 gagne un trimestre, 3 142,51 € au lieu
de 3 109,78 €. Des 913 témoins de simulation, refaits sur le poste, les cinq
salariés de Mayotte baissent, de 13,12 % à 28,36 % au scénario 1 (−27,50 % en
médiane), au plafond : leurs salaires, d'un profil national, dépassent celui
de la caisse ; les scénarios 3 et 5 les suivent, et les comptes notionnels
(2, 4 et 6), assis sur les cotisations, ne bougent pas. Aucune des 85 pages ne
change ; GitHub refait les témoins après l'envoi.

**Vu en chemin, non corrigé.**

- Le Smig de Mayotte de 1987 à 2001, et le plafond de la caisse de 1987 à
  2004 : des arrêtés préfectoraux jusqu'en 2002 (décret n° 87-175, articles 9
  et 21), puis 825 € par mois en 2003, que la Cnav porte à 912 € « du
  01/07/2004 » sans dire le premier semestre. Les barèmes ne remontent pas
  plus haut : le Smic et le plafond de la Sécurité sociale tiennent lieu, ce
  que la fiche de régime et la fiche `mayotte_pension_de_base` déclarent.
- Les cotisations — la fiche de paie, le compte notionnel — restent assises
  sur le plafond et aux taux du régime général : la caisse a les siens, que
  l'article 28-2 de l'ordonnance n° 96-1122 fait converger jusqu'en 2036, et
  qu'aucune série ne porte.
- Au-delà de 2026, le plafond de la caisse suit le salaire moyen, comme celui
  de la Sécurité sociale ; l'article 21 le revalorise de 5,1 points de plus
  chaque année, ce qui l'amènerait au plafond national vers 2032. Rien ne le
  borne au plafond national ni ne dit la suite, que la fusion de 2028
  (ordonnance n° 2026-647) remet aux décrets.
- La même classe d'écart ailleurs : Saint-Pierre-et-Miquelon a eu son plafond
  propre de 1987 à 2015, fixé par arrêté, que sa fiche déclare déjà ; les
  autres territoires ne valident pas de trimestres au Smic.
- Le registre des référents passe à `repris` l'apport de Catala (le Smic de
  Mayotte recopié décret par décret), chantier 177.3.

**L'étape est faite.** La suite : l'étape 4, les indépendants des DOM, à
trancher d'abord avec le propriétaire.
