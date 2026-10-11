# Étape 5, deuxième partie : la CSG déductible de chaque année, le net imposable des salaires et des pensions

**La demande.** Le propriétaire, le 11 octobre 2026 : le préalable de l'impôt
dans les indicateurs de cycle de vie, la CSG déductible de chaque année, qui
donne le net imposable des salaires et des pensions qu'attend `impot_revenu.py`
(point 1 de « Ce qui reste » de la première partie). D'autres sessions tournant
en parallèle, ne toucher ni à `cout.py` ni aux pages du site.

**Ce que disent les textes, lus le jour même.**

- *L'article 154 quinquies du code général des impôts*, ses dix-neuf versions
  de l'index LEGI, de 1997 à 2026 : 1 point de la CSG des revenus d'activité
  et de remplacement « perçus à compter du 1er janvier 1997 »
  (LEGIARTI000006302866 ; loi de finances pour 1997, art. 94) ; en 1998, « la
  fraction affectée en application du IV de l'article L. 136-8 » à
  l'assurance maladie (loi de finances pour 1998, art. 80), que ce IV chiffre
  à 5,1 % des revenus d'activité et 3,8 % des revenus de remplacement du II et
  du III (LEGIARTI000006740335), et que la rédaction de 2001 écrit en points ;
  4,2 points d'une pension au taux de 6,6 % en 2005 (loi n° 2004-1485,
  art. 37) ; 6,8 et 5,9 points en 2018 (loi de finances pour 2018, art. 67) ;
  4,2 au taux médian en 2019 (loi n° 2018-1213, art. 3). La version du
  27 juin 2026 n'y change rien.
- *Avant 1997*, rien : l'article n'existe pas, et la circulaire du 14 mai 1993
  le rappelle, « conformément à la règle applicable à l'ensemble des revenus
  soumis à cette contribution, la C.S.G. […] n'est pas déductible »
  (JORFARTI000001162800).
- *L'article 83 du code* : le revenu imposable déduit les cotisations — « la
  cotisation ouvrière aux assurances sociales » et, de 1982 à 2017, « la
  contribution exceptionnelle de solidarité » des agents publics (2° ter,
  rédaction de 1983), aujourd'hui « les cotisations de sécurité sociale »
  (1°) —, la maladie des pensions comprise. La CRDS et la CASA, que l'article
  154 quinquies ne nomme pas, restent imposables.
- *Les barèmes de l'IPP* portent la part déductible de la CSG d'activité et de
  chaque taux de celle des pensions (colonnes `deductible`) : les valeurs des
  textes, marche pour marche.
- *OpenFisca-France*, lu sur sa branche principale : sa pension imposable
  (`retraite_imposable`) ne déduit que la CSG ; la cotisation maladie des
  complémentaires, qu'il ne calcule pas, y reste.

**Ce qui est fait.**

- *La donnée* : `scripts/fetch/ipp_prelevements_sociaux.py` écrit la part
  déductible de chaque marche de CSG dans `prelevements_historiques.yaml`, et
  s'arrête si l'IPP ne rend pas, à chaque date, ce que les textes disent
  (`DEDUCTIBLE_AUX_TEXTES`). La donnée tient sous 50 000 octets.
- *Le lecteur* (`donnees/prelevements_historiques.py`) :
  `csg_deductible_pension`, à chaque taux ; `taux_deductible_pension`, la CSG
  déductible et la maladie de l'année, sur leurs parts de la pension ;
  `non_deductibles`, ce qu'un salaire paie sans que l'impôt le déduise — la
  CSG au-delà de sa part déductible et la CRDS, sur l'assiette de la CSG de
  l'année, le revenu augmenté de ses cotisations pour un indépendant jusqu'en
  2024.
- *Le net imposable* (`cycle_de_vie.py`) : `revenus_imposables`, le revenu
  d'activité de chaque année moins ses cotisations et sa CSG déductible — son
  net, plus ce que la paie a retiré sans le déduire — ; et
  `parts_imposables_par_annee`, la part de la pension brute que le revenu
  imposable de chaque année retient, aux années de `prelevements_par_annee`.
  Aucun indicateur ne les prend encore. `revenus_nets` ne change pas, et ne
  calcule pas ce qu'il ne rend pas.
- *Une convention*, pour le scénario 6 : la CSG que la proposition rend baisse
  la part déductible, et son net imposable garde la part non déductible du
  droit en vigueur, comme chaque hausse et chaque baisse de la CSG depuis 1997.
  Le README ne le tranche pas : au propriétaire de le confirmer.
- *Les tests* (`tests/test_prelevements_historiques.py`, six cas) : la part
  déductible à chaque date des textes, et la dernière marche égale à celle de
  la fiche de paie du site ; les mots des textes, relus dans l'index LEGI ; le
  salaire imposable de l'année courante égal au brut de la fiche moins ses
  cotisations et sa CSG déductible ; ce qu'un salaire paie sans le déduire, de
  1990 à 2020, agent public et indépendant compris ; la pension imposable d'un
  salarié parti en 2014 et d'une fonctionnaire partie en 1995 ; la convention
  du scénario 6.
- *Le registre* : les points d'Ines et d'EUROMOD sur l'impôt des pensions
  (138.5) disent ce qui est fait, et restent `a_reprendre` pour le net du site
  et la page Coût ; un écart de plus à OpenFisca, sa pension imposable.

**Ce que montrent les mesures.** Ce que la paie d'un salarié du privé au
salaire moyen retire sans que l'impôt le déduise, en part du brut : 1,1 % en
1992, 2,4 % en 1994 et 1995, 2,86 % en 1996, la CRDS de février comprise,
2,9 % en 1997, 2,76 % de 1998 à 2004, sur le brut abattu de 5 %, 2,81 % de
2005 à 2011, 2,85 % depuis 2012 ; une fonctionnaire paie un peu plus depuis
2018, son indemnité compensatrice s'ajoutant à son brut. La pension d'un
salarié parti en 2014, au quart complémentaire, est imposable à 95,5 % de son
brut jusqu'en 2017, à 93,8 % depuis.

**Ce qui reste** de l'étape, dans l'ordre :

1. *L'impôt dans les indicateurs de cycle de vie* (première partie, point 1) :
   le foyer de chaque année — `revenus_imposables`, la pension brute fois
   `parts_imposables_par_annee` — passé à `impot_revenu.py`, et le revenu net
   d'impôt. Le bénéfice d'un indépendant, qui n'a pas l'abattement de 10 %, est
   hors du champ du module : à décider à cette session.
2. *L'effet retour de la page Coût* (première partie, point 2).
3. *Le taux de CSG d'une pension selon le revenu fiscal du foyer* (138.2), que
   la convention du taux plein écarte : le lecteur en donne déjà la part
   déductible au taux médian et au taux réduit.
4. *Les règles d'avant 1981 sans texte lu* (première partie, point 3).
