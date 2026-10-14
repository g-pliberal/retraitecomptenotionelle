# Étape 3, quatrième partie : la CSG effective, et la dépense nette de l'Ageing Report

**La demande.** Session du 14 octobre 2026, la n° 4 de dix-neuf : « action
138, étape 3, la CSG effective, avec la dépense nette de l'AWG », le premier
reste du bloc de l'étape (point 3 de « Ce qui reste » de la première partie,
point 4 de la deuxième). Les sessions 10 et 11 tenaient la page Coût, la
session 2 les pages : rien n'est écrit dans `cout.py`, `pages.js` ni la
saisie.

**Ce que le relevé disait, et ce qui en reste.** Le relevé du 1er octobre
écrivait que la page Coût « retire 9,1 % à tous » ; elle ne retire plus rien,
et chiffre la dépense en brut. Ce qui manquait est le taux que les
prélèvements sociaux prennent vraiment à la masse des pensions, que la page
n'a pas, et dont l'effet retour d'une baisse des pensions sur la CSG (étape 5,
session 10) aura besoin.

**Les sources, lues le jour même** (`scripts/fetch/drees_pension_nette.py`,
témoin `tests/temoins/drees_pension_nette.json`, jeu `drees_pension_nette` de
`data/sources.yaml`).

* Le tableau 2.1-a de la DREES, « Effectifs de retraités, montants des
  pensions et âges de départ », édition fin 2022, la dernière en classeur : la
  pension moyenne brute et la nette, de droit direct et totale, de 2008 à
  2022, sur les mêmes retraités, résidents ou non. La nette déduit la CSG, la
  CRDS, la Casa et la cotisation maladie des complémentaires ; l'ASPA n'y est
  pas. Le rapport des deux moyennes est celui des masses.
* La feuille `A-Prelev_sociaux` de l'EACR diffusée le 26 mai 2026, lignes
  tous régimes : les retraités sans doublon par taux de CSG, de 2012 à 2024.
  Ancetre 2024, droit direct : 22,1 % d'exonérés, 13,4 % au taux réduit,
  21,6 % au médian, 42,9 % au plein, les chiffres du registre.

**Ce qui est fait** (`src/retraite_notionnelle/depense_nette.py`,
`tests/test_depense_nette.py`, cinq tests rapides).

* `taux_effectifs` : un moins la nette sur la brute. Pension totale : 6,2 % de
  2008 à 2012, 6,5 % de 2013 à 2016, 6,4 % en 2017, 7,6 % en 2018 (la CSG
  relevée de 1,7 point), 7,2 % en 2019 (le taux médian), 6,8 % de 2020 à 2022.
  Le taux plein, CSG, CRDS et CASA, est de 9,1 % depuis 2018.
* `borne_par_les_tetes` : le taux qu'auraient les retraités de droit direct à
  leur taux de CSG si leurs pensions étaient égales, au barème de
  `prelevements_historiques.yaml` (la CASA ni pour l'exonéré ni pour le taux
  réduit). 5,4 % en 2022 : chaque année de 2012 à 2022, le taux effectif passe
  la borne et reste sous le taux plein augmenté d'un point de cotisation
  maladie.
* `part_reprise_par_l_awg` : l'Ageing Report reprend 11,10 % de la dépense
  brute, chaque année de 2022 à 2070 (« public pension scheme, tax
  revenues », 1,60 point de PIB sur 14,45 en 2022). L'écart au taux de la
  DREES, 4,3 points de la dépense, est l'impôt sur le revenu des pensions,
  environ 0,6 point de PIB : l'AWG le compte, la pension nette de la DREES non.
* `taux_projetes` et `depense_nette` : le dernier taux observé, tenu après
  2022 comme l'AWG tient sa part ; la dépense nette en est la brute diminuée.
  La proposition paie le même taux que le droit en vigueur, l'hypothèse que
  le site fait déjà pour la pension nette d'une personne (décision du
  4 octobre 2026).

**Une réserve sur 2023.** La borne par les têtes saute de 5,4 % en 2022 à
6,1 % en 2023 : Ancetre 2023 compte 22,3 % d'exonérés de droit direct, contre
30,3 % en 2022, sans que le barème ait bougé — un changement de méthode, ou
des seuils. La CCSS de mai 2024 compte 23,7 Md€ de CSG sur les retraites en
2023, 6,3 % des masses de la DREES : la CSG seule, à quoi la CRDS, la CASA et
la cotisation maladie ajoutent près d'un point. Le taux de 2022, tenu, est
donc sans doute bas d'un demi-point ; l'édition suivante du tableau 2.1-a le
dira.

**Ce que ça déplace.** Rien : aucun chiffre de page, aucun témoin du site ;
le module n'est lu que par son test.

**Ce qui reste**, de cette partie ; le reste de l'étape 3 est dans les notes
de la première et de la deuxième.

1. *Les montants de 2023 et 2024*, que la DREES publie dans le Panorama
   « Les retraités et les retraites » de 2025 et de 2026, hors du classeur
   lu : à ajouter au témoin, ce qui tranchera la réserve sur 2023.
2. *Le taux dans le modèle* : un fichier de `data/reference/macro/`, avec sa
   ligne de vérification, que `cout.py` lirait pour l'effet retour sur la CSG
   (étape 5) et la page Coût pour une dépense nette ; à la session qui tient
   le Coût.
3. *L'impôt sur le revenu des pensions*, agrégé, qui ferait la dépense nette
   au sens de l'AWG (étape 5, `impot_revenu.py`).
4. *Le taux de chaque système*, qui ne diffère que par la répartition de ses
   pensions entre les tranches de CSG, que le modèle ne projette pas.
