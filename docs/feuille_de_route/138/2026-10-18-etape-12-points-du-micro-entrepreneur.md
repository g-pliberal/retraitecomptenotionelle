# Étape 12, huitième partie : les points du micro-entrepreneur, achetés par son forfait, et sa nouvelle pension en cumul

**Le 18 octobre 2026, la demande.** Vague du 18 octobre, session 138.12 : le
point 5 de « Ce qui reste » de `…-revenu-annuel-moyen-du-micro-entrepreneur.md`.
Les points du RCI, et ceux de la CNAVPL pour la Cipav, se calculaient au
barème sur le revenu abattu, et non sur la part du forfait qui les achète ; la
nouvelle pension du micro-entrepreneur en cumul additionnait son revenu abattu.

**Ce que dit le droit** (journal de veille,
`2026-10-18-action-138-etape-12-points-du-micro-entrepreneur.yaml`).

- *Le RCI.* Son compte porte « les droits acquis, année par année, par les
  cotisations versées par l'assuré » (règlement, article 3), un point par
  « revenu de référence » cotisé (article 47) ; celles du micro-entrepreneur
  sont la part complémentaire de son forfait (D. 613-6 ; la clef de la Cnav
  avant le décret n° 2022-1529). La caisse l'écrit : « 211 € / 17,691 € =
  11,92 = 12 points » (circulaire n° 2025-20, annexe 1) ; « (102,10 € + 48,58 €
  + 55,89 € + 87,49 €) / 21,726 € = 13,53 arrondi à l'entier inférieur 13 »
  pour 12 100 € de ventes en 2026 (F23369, vérifié le 14 octobre 2026).
- *La CNAVPL.* Ses points se comptent « au prorata des cotisations acquittées
  sur chacune des tranches » (D. 643-1) ; D. 613-6 affecte au micro-entrepreneur
  de la Cipav une part « au 1° » et une « au 2° de l'article D. 642-3 ». La
  Cipav : 48 000 € de recettes en 2026, « 2 706,05 / 7,53 = 359,37 points »,
  579,07 € à 179,76 € le point, et « 3 418,75 € » à la complémentaire, « 72,13
  points » (fiche pratique des auto-entrepreneurs, 2026).
- *Trouvé en chemin.* L'arrêté du 21 septembre 2026 ouvre au libéral de
  l'Assurance retraite, du 1er janvier 2027 au 31 décembre 2033, un versement
  facultatif de RCI pour 2018 à 2025, « CA ou recettes × taux GC × taux RCI »,
  ses points arrondis à l'entier le plus proche (règlement, articles 9-7, 9-8
  et annexe 4). Le scénario 1 ne le présume pas.
- *La nouvelle pension de l'indépendant.* De 2023 à 2025, D. 634-1 écarte
  R. 351-29, et R. 634-1 fait le revenu annuel moyen des cotisations versées,
  l'année d'effet comprise ; depuis 2026, D. 634-3 applique R. 351-29, « Les
  III et IV ne sont pas applicables ». Le salaire mensuel moyen du salarié ne
  vaut donc pas pour l'indépendant.

**Ce qui est fait.**

- *Les deux moteurs* : `acquerir` (`acquerir.js`) achète les points d'une ligne
  de micro-entrepreneur avec les parts de son forfait, chacune à la période de
  sa tranche, aux années qui ont la répartition ; `charger_cotisation_micro`
  rend la part de la seconde tranche de la CNAVPL, et le paquet la porte. La
  nouvelle pension (`seconde.py`, `seconde.js`) prend le revenu cotisé.
- *Tests* : `test_micro_social.py`, les exemples de F23369, de la circulaire et
  de la Cipav, le libéral de 2023 et de 2024, la Cipav de 2020 posée à la main
  depuis D. 131-5-3 et D. 643-1 ; `test_emploi_retraite.py`, la nouvelle
  pension ; `moteur.test.js`, les mêmes dans le portage, vus rouges.
- Fiches `micro_social_abattement` et `seconde_pension`, régime
  `micro_entrepreneurs`, statut d'`affiliations.yaml`, inventaire ; le cliquet
  des textes descend à 9 676.

**Mesuré.** Six témoins bougent au scénario 1 : le libéral de l'Assurance
retraite perd 6,55 %, son RCI 25 %, sans part complémentaire de 2018 au
30 juin 2024 ; la Cipav 3,57 %, celle de petites recettes 12,48 %, les classes
de la complémentaire passant le forfait de 2019 à 2022 ; la vente et les
services gagnent de 0,35 à 0,49 %. Au scénario prospectif, les droits acquis
avant la bascule suivent : de −11,72 % à −0,12 %. La nouvelle pension de la
vente de 2023 et 2024 vaut 0,9988 fois celle du revenu abattu.

**Ce qui reste.**

1. *La nouvelle pension de l'indépendant* : son revenu annuel moyen, et non le
   salaire mensuel moyen de R. 351-29, III ; la circulaire Cnav qui applique
   R. 634-1 et D. 634-3, que la recherche de la Cnav n'a pas rendue.
2. *L'arrondi des points du RCI à l'entier*, au plus proche pour la
   circulaire, à l'inférieur pour service-public : déclaré.
3. *La Cipav de 2009 à 2015* : les points de la « cotisation réduite », que la
   cour d'appel de Versailles a refusés le 8 mars 2018 (Previssima, 8 juin
   2018) ; avant 2019, aucune répartition lue, le barème reste.
4. Les restes des notes précédentes, et la part de base de l'ordre de
   D. 133-4 de 2016 à 2019, au propriétaire.
