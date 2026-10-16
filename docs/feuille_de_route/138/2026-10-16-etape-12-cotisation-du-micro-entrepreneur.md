# Étape 12, quatrième partie : la cotisation du micro-entrepreneur au compte notionnel, le forfait versé

**Le 16 octobre 2026, la demande.** Vague quinquies, session 6 sur 11 : le
point 2 de « Ce qui reste » de `2026-10-14-etape-12-micro-entrepreneur.md`,
repris au point 3 de `2026-10-14-etape-12-trimestres-du-micro-entrepreneur.md`.
La cotisation du commerçant reproduisait le taux global de la vente par
construction ; celles des services, du libéral et de la Cipav, à mesurer
contre D. 613-4 et ses versions, puis à corriger dans les deux moteurs.

**Ce que dit le droit** (journal de veille,
`2026-10-16-action-138-etape-12-cotisation-du-micro-entrepreneur.yaml`).
D. 613-6, relu dans toutes ses rédactions, affecte au régime complémentaire
16,50 % puis, en 2026, 19,75 % du forfait de la vente et des services ; rien
de celui du libéral de l'Assurance retraite jusqu'au 30 juin 2024 — le Conseil
d'État annule la rédaction de 2022 au 1er juin 2024, « en tant qu'[elle
n'inclut] pas » de cotisation complémentaire, et tient ses effets passés pour
définitifs (décision n° 471203) —, puis 7,85, 13 et 21 % ; 20,75, 25,60 puis
30,70 % de celui de la Cipav, dont la CNAVPL reçoit aussi une seconde tranche
(5,30, 5,35 puis 5,20 %). Avant le décret n° 2022-1529, D. 613-6 ne répartit
que le forfait de la Cipav.

**Mesuré**, à 40 000 € de chiffre d'affaires, le barème sur le revenu abattu
que le compte portait, contre le forfait de retraite versé : vente et
services, +0,1 % en 2023 — la construction tenait —, +5 % en 2025, −3 % en
2026, le barème et la répartition ne bougeant pas ensemble ; libéral, +39 % en
2023, sans part complémentaire, +15 % en 2025, −1 % en 2026 ; Cipav, +13 à
+15 % de 2023 à 2025, +2 % en 2026. Le même écart à 15 000 et à 70 000 €.

**Ce qui est fait.**

- *La table* `legislation/micro_social.yaml` porte, pour chaque version, la
  part complémentaire, la seconde tranche de la Cipav, et les deux régimes
  qui reçoivent le forfait ; `charger_cotisation_micro` et `forfait_micro`
  en tirent, par année, deux taux sur le revenu abattu, aux mêmes années que
  la validation (2023 et après) ; le paquet les porte (`cotisation_micro`).
- *Les deux moteurs* : `ConstructeurCompte._cotisation_ligne` (`compte.js`,
  `_cotisationLigne`) remplace, pour une ligne de micro-entrepreneur, ce que
  le barème donnait au régime de base et à la complémentaire par la part du
  forfait ; avant 2023, et sous le taux uniforme, le barème reste. Aucun
  choix de la proposition : le compte porte ce qui a été versé, sa règle.
- *Tests* : `test_micro_social.py` rejoue les parts de cinq cas, dont le
  libéral de 2023 et de 2024 et la Cipav, le paquet, et le barème d'avant
  2023 ; les témoins `micro_entrepreneur_*` refaits, que le portage retrouve.
- Fiche `micro_social_abattement`, régime `micro_entrepreneurs`, statut
  d'`affiliations.yaml` et registre, récrits.

**Ce qui reste.**

1. *Avant le 1er octobre 2022*, la répartition du forfait de l'Assurance
   retraite n'est dans aucune rédaction de D. 613-6 ; celles de 2020 et de
   2021 donnent celle de la Cipav, à porter sans changer la validation.
2. *D. 131-6-3*, la fraction du taux pendant l'exonération de début
   d'activité, n'est pas portée.
3. *Les points du RCI* au scénario 1, sur la part du forfait et non au barème.
