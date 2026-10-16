# Étape 8, sixième partie : l'assiette forfaitaire du collaborateur, et la retraite forfaitaire du chef à titre secondaire

**Le 16 octobre 2026, la demande.** Les points 1 et 4 de « Ce qui reste » de
la note du 14 octobre sur le statut agricole : le collaborateur et l'aide
familial cotisent sur une assiette forfaitaire, que le modèle prenait de leur
revenu ; le chef à titre secondaire recevait, avant 2026, la retraite
forfaitaire comme le chef principal (4 900 € par an au salarié de 1958 chef à
côté depuis ses trente ans). Session du modèle, une de quatorze cette nuit.

**Ce que dit le droit** (journal de veille du 16 octobre, index LEGI et JORF).

- *L'assiette du collaborateur et de l'aide familial* : au b du 2° de
  L. 731-42, « déterminée forfaitairement » depuis 2004, l'assiette minimale de
  D. 731-120, 400 SMIC horaires (D. 731-123), 600 depuis 2026. Elle ouvre les
  quinze points de R. 732-71, que R. 732-73 porte à seize « pour le calcul des
  retraites proportionnelles prenant effet postérieurement au 31 décembre
  1993 » — plancher que le modèle n'appliquait à personne, chefs compris. À
  la RCO, depuis 2011 : 1 200 SMIC, 66 points par an jusqu'en 2016, 77 en
  2017, 88 depuis (D. 732-155, II). En 2000, la cotisation du conjoint
  collaborateur se prenait des revenus du chef.
- *Le chef à titre secondaire* : « Les personnes ayant exercé, concurremment
  avec une activité salariée, une activité agricole non salariée ne présentant
  qu'un caractère accessoire peuvent seulement prétendre à la pension de
  retraite proportionnelle » (L. 732-28, et l'article 1121-1 de l'ancien code
  depuis 1980) ; elles ne doivent pas la cotisation de la forfaitaire
  (L. 731-42, 1°) ; qui était non-salarié agricole avant 1981 la garde
  (R. 732-65). La MSA ne sert le forfait qu'à « l'activité non-salariée
  agricole exercée à titre exclusif ou principal ». La loi n° 2025-199 abroge
  L. 732-28 au 1er janvier 2026, le décret n° 2025-1409 R. 732-65 et
  R. 732-69 à D. 732-77 pour les pensions prenant effet depuis.

**Ce qui est fait**, dans les deux moteurs.

- `acquerir.assiette_du_collaborateur` : l'assiette du collaborateur et de
  l'aide familial est le forfait, quel que soit le revenu — 400 puis 600 SMIC
  à la base depuis 2004, 1 200 SMIC à la RCO depuis 2011, dont les points sont
  les entiers du texte (66, 77, 88). Le revenu de leurs années depuis 2016, au
  1° de L. 732-24, est ce même forfait (`salaire_de_reference`).
- `acquerir.points_msa_retenus` : le plancher de seize points de R. 732-73,
  pour les pensions de 1994 à 2025 ; le chef de 1990 à 2003 au plus bas
  revenu passe de quinze à seize points (`test_simulateur`, renommé
  `…ouvre_seize_points…`).
- `liquider.trimestres_hors_forfait` : pour une pension d'avant 2026, le
  forfait ne compte plus les années de chef à titre secondaire, sauf à qui
  était non-salarié agricole avant 1981. Le modèle l'applique à toute année
  de chef secondaire, comme la MSA, quand L. 732-28 ne nomme que l'activité
  accessoire d'un salarié.
- Les tests (`tests/test_minima_agricoles.py`, deux de plus) : la
  collaboratrice partie en 2024, seize points par an à la base depuis 2004,
  66, 77 et 88 à la RCO, la même RCO à deux revenus ; le salarié de 1958 chef
  à côté, sans forfait, et celui de 1945, qui l'était avant 1981, avec. La
  comparaison des deux moteurs, qui porte déjà ces carrières, est verte.
- Les fiches `retraite_proportionnelle_msa`, `assiette_minimale_agricole` et
  `pension_non_salaries_agricoles_2026` le disent, lectures datées.

**Ce qui reste**, aux sessions du modèle :

1. *Le chef secondaire des pensions de 2026* : L. 732-28 abrogé, le modèle
   garde ses années d'avant 2016 dans la part forfaitaire du 2° a de
   L. 732-24 ; ce que fait la MSA est à lire (circulaire de la réforme).
2. *Le collaborateur d'avant 2004*, dont la cotisation se prenait des revenus
   du chef, et les qualités d'avant 1999 — le conjoint participant aux
   travaux n'avait que la forfaitaire (L. 732-34), l'aide familial cotisait
   au b du 2° — que le statut unique ne distingue pas : le modèle garde le
   revenu saisi.
3. *Le revenu du collaborateur de 2016 à 2025* au 1° de L. 732-24, que la loi
   déduit peut-être de ses cotisations : le modèle prend le forfait.
4. Les points 2 et 3 de la note du 14 octobre : DM1 au-delà du chef, et les
   seuls points de RCO de chef dans la formule différentielle.

Les témoins de simulation des carrières agricoles bougent : GitHub les refait.
