# Le taux propre de l'indépendant de Mayotte, de l'article 4-2 à la série des taux (file D)

*Le 5 novembre 2026, file D de la vague 7, sur Opus.* Le bloc « Reprise » disait
de commencer par « les taux de Mayotte (étape 8) ; en 2026, le décret, 150 € le
trimestre ». Le second point était tranché : la décision 4 du propriétaire
(`130/2026-11-03-decisions-du-proprietaire.md`) garde le décret, 150 €, et la note
`177/2026-11-03-etape-9-assiette-du-rco-ecrite.md` l'a écrit ; rien d'autre à faire.
Le premier ne l'était pas : la note de l'étape 8 laissait, « vu en chemin, non
corrigé », les taux de l'article 4-2 hors de `taux_cotisation_annuels.csv`, et
l'indépendant de Mayotte payait au compte et sur sa fiche de paie la série du régime
général, celle du salarié et de son employeur. C'est l'écart que cette note ferme ; le
minimum de la cotisation jusqu'en 2015 (D. 633-2, D. 612-6) attend.

**Ce que disent les textes, lus dans l'index LEGI du dépôt à jour du 4 novembre 2026.**

- Décret n° 2011-2085, article 4-2, I, rédaction du 25 juin 2019
  (LEGIARTI000038680068) : « Conformément aux dispositions de l'article 2 du décret
  n° 2019-632 du 24 juin 2019, ces dispositions s'appliquent aux cotisations de
  sécurité sociale dues au titre des périodes courant à compter du 1er janvier 2019.
  I.-La cotisation annuelle d'assurance vieillesse de base due par les travailleurs
  indépendants […] est assise sur le revenu d'activité […] dans la limite du plafond
  prévu au I de l'article 28-1 de l'ordonnance du 20 décembre 1996 susvisée. […] Le
  taux de cette cotisation est fixé, pour chaque année civile de 2019 à 2036,
  conformément au tableau suivant : Année Cotisation au régime d'assurance vieillesse
  obligatoire de base 2019 5,85 % 2020 6,55 % 2021 7,25 % 2022 7,95 % 2023 8,65 % 2024
  9,35 % 2025 10,05 % 2026 10,75 % 2027 11,45 % […] 2036 17,75 % ».
- La rédaction du 1er janvier 2026 (LEGIARTI000053297541) garde le même tableau et la
  même assiette ; elle n'ajoute que les quatre-vingt-dix jours d'affiliation de
  l'assiette minimale.
- Ordonnance n° 96-1122, article 28-2, I, 1°, dans ses deux rédactions
  (LEGIARTI000025018560, LEGIARTI000046455192) : les cotisations du régime de base de
  Mayotte sont assises « dans la limite du plafond », dues « par tout employeur […] et
  par tout assuré, ainsi que par les travailleurs indépendants agricoles et non
  agricoles ». Aucune cotisation sur la totalité : la mesure déplafonnée vaut 0.
- Décret n° 2011-2085, article 4, rédactions de 2012 et de 2026 (LEGIARTI000025097520,
  LEGIARTI000026514552, LEGIARTI000053469930) : il fixe le taux des cotisations de
  l'article 28-2 par une part salariale (4,00 % en 2012) et une part patronale (9,90 %),
  sans nommer les travailleurs indépendants. Ce que l'indépendant devait de 2012 à
  2018, le texte ne le tranche pas : le modèle lui garde la série alignée, et la fiche
  le déclare (`supposee`).

**Ce qui est écrit.** Un récupérateur, `scripts/fetch/dila_legi_taux_mayotte.py`, lit
les rédactions de l'article dans l'index : le tableau du I et lui seul, la date
d'application qu'écrit la note de 2019, qui l'emporte sur l'entrée en vigueur du
25 juin ; il s'arrête sur un I sans tableau ou qui parle de la totalité du revenu. Sa
série s'arrête à l'année en cours, comme celle de D. 633-3. Une certification de plus
dans `scripts/verifier_donnees.py` (`taux_cotisation_mayotte`) verse seize valeurs
`certifiee` : `taux_plafonne_non_salarie` et `taux_deplafonne_non_salarie` de
`cssm_mayotte`, de 2019 à 2026. Le chargeur et `PeriodeRegime.taux_du_cotisant` les
servaient déjà à l'assuré sans employeur, dans les deux moteurs : la donnée suffit, le
paquet refait. La fiche `cotisation_vieillesse_independants_mayotte`, à part : les
versions de `cotisation_vieillesse_independants`, datées par la seule année, ne
peuvent pas porter deux taux la même année. `sources.yaml`, l'inventaire de
`cssm_mayotte` et `docs/limites/1-certification.md` le disent.

**Les valeurs attendues, posées à la main.** L'artisane de Mayotte à 10 000 € par an,
sous le plafond de la caisse (23 208 € en 2020, 31 728 € en 2024) et au-dessus de son
assiette minimale (450 × 7,57 € = 3 406,50 € en 2019) :

- 2019 : 10 000 × 5,85 % = 585,00 € ; avant, 10 000 × 15,45 % + 10 000 × 2,30 % =
  1 545 + 230 = 1 775,00 €, ce que les tests ont vu rouge ;
- 2024 : 10 000 × 9,35 % = 935,00 € ;
- la fiche de paie de 2019 : 585,00 €, à la seule charge de l'assuré.

**Les tests** (`tests/test_mayotte.py`), vus rouges puis verts : la période de la
caisse porte le taux de chaque année de 2019 à 2026, et rien en 2018 ; le compte, dans
les deux moteurs ; la fiche de paie ; le récupérateur sur les deux rédactions, et son
refus d'un texte qu'il ne sait pas lire. `test_donnees.py` admet désormais ces deux
mesures de `cssm_mayotte` parmi les taux certifiés. Aux témoins, les cinq indépendants
de Mayotte perdent de 0,84 % (né en 1955) à 21,38 % (né en 1965) de leur pension
notionnelle aux scénarios 2 et 4, 0,84 % au scénario 6 pour celui de 1955 ; aucune
pension du scénario 1 ne bouge ; le jumeau Python refait les témoins au bit près.

**Vu en chemin, non corrigé.** Le salarié de Mayotte paie, lui aussi, la série du
régime général, quand l'article 4 lui donne sa part salariale et sa part patronale
(4,77 % et 9,90 % en 2019) et que l'article 28-2 n'appelle rien sur la totalité ; la
limite le disait déjà. Ce n'est pas la zone de la file D. De 2027 à 2036, le tableau
monte jusqu'à 17,75 %, que la série ne porte pas : la fiche le déclare.

**Où en est l'action.** L'écart des taux de Mayotte est fermé. Restent déclarés le
minimum de la cotisation jusqu'en 2015, à lire d'abord (D. 633-2, D. 612-6), le
forfait du commerçant qui commence et celui de l'artisan de 2009 à 2011.
