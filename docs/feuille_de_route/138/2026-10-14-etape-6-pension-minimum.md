# Étape 6, troisième partie : la pension minimum d'avant le 1er avril 1983

**La demande.** La session de nuit du 14 octobre 2026 : « la pension minimum
d'avant avril 1983, le premier reste du bloc de l'étape, dans les deux moteurs,
texte en main ». Le point 2 de « Ce qui reste » de la première partie : « la
pension minimum d'avant le 1er avril 1983, au montant de l'AVTS, que la fiche du
minimum contributif renvoie ici ». Ni pages ni saisie, que tient une autre
session cette nuit.

**Ce que disent les textes, lus dans les index LEGI et JORF** (journal de veille
du 14 octobre).

- *La règle*, au décret n° 45-0179, article 70-5, dans sa rédaction du 12 mai
  1976 (décret n° 76-404), recopiée en article 70-7 le 23 juillet 1982 : « Seuls
  peuvent bénéficier de l'intégralité du minimum de base prévu à l'article L. 345
  du code de la sécurité sociale les titulaires d'une pension de vieillesse
  substituée à une pension d'invalidité et les titulaires de pensions
  correspondant à une durée d'assurance d'au moins quinze années (soit 60
  trimestres) accomplies dans le régime général de la sécurité sociale. Lorsque
  cette durée est inférieure à quinze années, le minimum de base est réduit à
  autant de soixantièmes que l'assuré justifie de trimestres d'assurance. » La
  bonification de 10 % pour trois enfants s'y ajoute, « du montant du minimum de
  base », et la majoration pour conjoint à charge.
- *Qui y a droit* : l'assuré « âgé de plus de soixante-cinq ans ou de moins de
  soixante-cinq ans mais inapte au travail » (décret n° 51-727, article 1er bis,
  paragraphe 2, qui l'étend aux salariés agricoles) ; la Cnav le dit de la
  retraite « attribuée au taux plein ». Avant 1983, le taux croît avec l'âge : la
  pension au taux de soixante-cinq ans est celle qu'aucun abattement ne réduit,
  à cet âge ou avant au titre de l'inaptitude ou d'une catégorie (ancien
  combattant, travailleur manuel, mère de famille ouvrière). Cent cinquante
  trimestres à soixante ans n'y suffisent pas.
- *Son montant* est celui de l'AVTS : les décrets « fixant le montant de divers
  avantages de vieillesse » les fixent dans le même article — « Sont portés à
  10.100 F par an à compter du 1er janvier 1982 : Le montant de l'allocation aux
  vieux travailleurs salariés […] ; Le montant de la pension minimum de
  vieillesse visée aux articles L. 345, L. 350 et L. 379 » (n° 81-1166), de même
  10 900 F (n° 82-561) et 11 300 F (n° 82-1142) —, et renvoient encore à
  l'article 13 de l'ordonnance n° 45-170 du 2 février 1945, qui l'a créé. Après la
  réforme, les pensions « portées, avec une date d'effet antérieure au 1er avril
  1983, au montant minimum de base » suivent l'AVTS (n° 83-551, article 4).
- *Le même article.* La loi n° 83-430 du 31 mai 1983, article 2, récrit L. 345
  en minimum contributif (notice du décret n° 84-187) : la pension minimum en est
  l'ancêtre, au même article.
- *Avant 1976*, les index n'ont aucun article : ni l'ordonnance de 1945, ni le
  code de 1956, ni les rédactions antérieures du décret n° 45-0179.

**Ce qui est fait.**

- *La fiche `minimum_contributif`* coupe sa première version en deux :
  `pension_minimum_de_1976`, lue, du 12 mai 1976 au 31 mars 1983, et
  `pension_minimum_de_1945`, supposée, avant, au niveau `estimee`, qui présume la
  règle de 1976. Le minimum contributif n'y existe toujours pas (`existe: false`) ;
  un paramètre de plus, `pension_minimum`, porte la règle : le minimum entier à
  soixante trimestres dans le régime, entier à l'ex-invalide, les deux régimes qui
  le servent (régime général, salariés agricoles). Le code reste
  `minimum_contributif`, le libellé dit « Pension minimum (AVTS) ».
- *Les montants* : `data/reference/legislation/pension_minimum_avant_1983.csv`,
  chaque date de l'AVTS du barème de la Cnav (`cnav_avts`), du 1er janvier 1945 au
  1er janvier 1983, au niveau `haute` ; un test redonne de chacune la colonne
  `avts` de `minimum_vieillesse_avant_2007.csv` au 31 décembre.
- *Les deux moteurs* : `MinimumContributif.pension_minimum` (`pensionMinimum`) lit
  le montant du mois de la date d'effet ; `completer` porte la pension au taux de
  soixante-cinq ans à ce montant, au prorata de sa durée dans le régime sur
  soixante trimestres (`plancher_d_avant_1983`, `plancherDAvant1983`), sans
  majoration ni écrêtement ; `liquider` tient pour taux plein, avant 1983, la
  pension qu'aucun abattement ne réduit. Les périodes d'avant 1983 du régime
  général et des salariés agricoles déclarent l'avantage. La bonification pour
  enfants se calcule après, sur la pension relevée, comme le texte le veut.
- *Ce que la règle ne touche pas.* La majoration exceptionnelle de 2023 ne relève
  toujours pas une pension d'avant 1983 (l'écart que sa fiche déclare) ; la
  réversion lit la pension sans le minimum, comme pour le minimum contributif.
- *Les tests* (`tests/test_pension_minimum_avant_1983.py`) : quinze ans au demi-
  SMIC liquidés en avril 1980, portés aux 7 400 F de l'AVTS, au régime général et
  chez les salariés agricoles ; vingt-huit trimestres, aux 28/60 des 8 500 F de
  1981 ; la pension abattue de 1978, à soixante ans, sans minimum ; la bascule du
  1er avril 1983 ; la série datée ; six requêtes, dont deux de part et d'autre du
  1er avril 1983, identiques dans les deux moteurs.

**Ce qui reste.**

1. *Avant 1976*, au fac-similé du Journal officiel, sur le poste du propriétaire :
   l'article 13 de l'ordonnance n° 45-170, L. 345 du code de 1956, le décret
   n° 45-0179 d'avant 1976. Avant le 1er juillet 1974, la rente des moins de quinze
   ans n'était peut-être pas portée au minimum.
2. *Les autres régimes* : la proratisation du minimum des salariés agricoles, que
   fixe un décret non lu ; le minimum de base des artisans et commerçants pour
   leurs périodes d'après 1972 (décret n° 73-937, article 7) ; le cumul de deux
   pensions portées au minimum.
3. *Ce qui s'ajoutait au minimum* et que le modèle ne connaît pas : la rente des
   assurances sociales au 31 décembre 1940 et celle des retraites ouvrières et
   paysannes.
4. *Les trois montants de 1982 et 1983*, lus dans l'article, à certifier par un
   contrôle de `jorf_avts.py`.
5. Les autres points de l'étape : l'AVTS dans R. 732-70 — la série datée de
   l'AVTS, que cette table commence, s'y prolongera jusqu'en 2026 — ; l'outre-mer ;
   avant 1946, la retenue ; le fac-similé.

**Pour les pages, rien à écrire** : le détail de la pension et la ligne de
l'avantage disent « pension minimum » d'eux-mêmes.
