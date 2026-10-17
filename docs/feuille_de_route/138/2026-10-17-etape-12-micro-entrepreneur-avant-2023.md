# Étape 12, cinquième partie : le micro-entrepreneur d'avant 2023, la validation et la répartition du forfait

**Le 17 octobre 2026, la demande.** Vague du jour, session 5 sur 12 : du
micro-entrepreneur, la validation et la répartition d'avant 2023, le 1 de
« Ce qui reste » des notes du 14 octobre (`…-trimestres-du-micro-entrepreneur.md`)
et du 16 (`…-cotisation-du-micro-entrepreneur.md`). Avant, le revenu abattu
validait, et le compte portait le barème sur ce revenu.

**Ce que dit le droit** (journal de veille,
`2026-10-17-action-138-etape-12-micro-entrepreneur-avant-2023.yaml`).

- *De 2018 à septembre 2022*, D. 613-6 ne répartit que le forfait de la Cipav
  (circulaire Cnav n° 2023-4, point 3). La Cnav affecte celui de l'Assurance
  retraite par des « clefs de répartition » : au régime de base, 40,31 % de
  la vente, 40,36 % des services, 53,23 % du libéral ; au RCI, 15,94 %,
  15,91 % et rien. Elle valide sur ce qu'elles achètent, divisé par 17,75 %,
  comparé à 150 SMIC horaires (circulaire Cnav n° 2025-20, annexe 1, ses
  exemples de 2020 et de 2021). Taux globaux de 12,8 % et 22 % (D. 131-5-1,
  puis D. 613-4).
- *La Cipav* : D. 131-5-3, du décret n° 2018-1120, en vigueur le
  13 décembre 2018, puis D. 613-6 : 25 % du forfait à la première tranche de
  la CNAVPL, 5 % à la seconde, 20 % à la complémentaire ; au 1er juillet
  2021, 24,80, 5 et 19,80 %, sur un taux global de 22 % puis 22,2 %.
- *De 2009 à 2015*, l'État compensait aux caisses la cotisation « normalement
  due » sur le revenu abattu (circulaire RSI n° 2010/034, point III). En
  2009, sur une année civile entière, un trimestre au moins (circulaire RSI
  n° 2009/024). Depuis 2010, plus rien sous un revenu abattu de 200 heures de
  SMIC, 300 en 2015 (L. 133-6-8-2, D. 131-6-4) ; en deçà, le forfait de qui
  relève de la maladie du RSI va tout entier à ce risque, et rien ne valide.
  Jusqu'en 2013, c'est le seuil du trimestre ; en 2014, le premier trimestre
  demande encore 200 heures quand les suivants en demandent 150 (circulaire
  RSI n° 2016/010) ; en 2015, la compensation en valide deux (circulaire RSI
  n° 2015/007). Elle cesse en 2016.

**Ce qui est fait.**

- *La table* `legislation/micro_social.yaml` remonte à 2018 pour l'Assurance
  retraite, à 2019 pour la Cipav, dont les versions marquées `valide: false`
  répartissent le forfait sans valider. Une section `compensation` porte le
  plancher de 2009 et les seuils de 2010 à 2015, en heures de SMIC ; le
  paquet la porte (`compensation_micro`).
- *Les deux moteurs* : `charger_validation_micro` saute les versions qui ne
  valident pas ; `validant_compense` (`validantCompense`, `carriere.js`)
  annule le revenu validant sous le seuil et le relève au plancher, sur une
  année civile entière seulement. Le compte lit la table comme avant
  (`forfait_micro`), sans code neuf.
- *Tests* : `test_micro_social.py` rejoue les clefs, l'exemple de 2020 de la
  circulaire n° 2025-20 (535,58 € au régime de base, 211,12 € au RCI, un
  trimestre), les tableaux du RSI de 2009, 2010, 2014 et 2015, l'année 2009
  entamée, la Cipav et le paquet ; `moteur.test.js`, les mêmes seuils dans
  le portage, sous les bornes de la saisie qu'aucun témoin ne franchit.
- Fiche `micro_social_abattement`, régime `micro_entrepreneurs` et
  inventaire, récrits.

**Mesuré.**

- *La validation* : le revenu validant de 2018 à 2021 vaut 1,0024 fois le
  revenu abattu pour la vente, 1,0005 pour les services, 0,9996 pour le
  libéral ; aucun des 874 témoins ne bouge au scénario 1. La compensation
  change le compte des trimestres sous les bornes de la saisie seulement :
  3 000 € de ventes en 2009 valident un trimestre, et non zéro ; 6 500 € en
  2014, et 7 000 € en 2015, aucun, et non un.
- *Le compte notionnel*, à 40 000 € de chiffre d'affaires en 2020, forfait
  contre barème : vente 2 880 € contre 2 871 € ; services 4 952 € contre
  4 950 € ; libéral 4 684 € contre 6 534 €, sans RCI ; Cipav 4 400 € contre
  5 450 €. Les témoins : au compte rétroactif, le libéral perd 4,2 %, la
  Cipav 1,7 %, la Cipav de petites recettes 11,0 % ; la vente gagne 0,04 %.

**Ce qui reste.**

1. *Les clefs de 2016 et de 2017* (taux globaux de 13,4 % et 23,1 %) et
   celles de janvier à septembre 2022, que la table prend à 2021 : aucune
   source lue ne les donne.
2. *La Cipav avant 2023* : la CNAVPL validait-elle sur sa part du forfait ?
   La table ne la fait que cotiser.
3. *En 2014 et 2015*, qui ne relevait pas de la maladie du RSI — un salarié,
   un assuré au RSA — validait dès 150 heures sans compensation ; le compte
   garde le barème sous le seuil, où l'État ne versait rien.
4. Les restes des notes précédentes : le salaire annuel moyen, l'arrondi
   trimestriel, D. 131-6-3, les points du RCI sur la part du forfait.
