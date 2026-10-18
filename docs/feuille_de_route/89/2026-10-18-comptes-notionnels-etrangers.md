# Les comptes notionnels étrangers : treize lignes, l'indice suédois refait, les âges ronds du GUS

**Le 18 octobre 2026 : treize lignes réservées (7af072b), puis dépouillées.**
Ce sont les comptes notionnels étrangers du sas : la Suède (Pensionsmodellen,
Typfallsmodellen, les prescriptions de Pensionsmyndigheten, le rapport orange
2025), la Norvège (MOSART), l'Italie (le rapport n° 27 de la RGS, le décret des
coefficients), la Pologne (le communiqué du GUS), le Brésil (le fator
previdenciário), la Finlande (le coefficient d'espérance de vie), et trois
outils internationaux (PROST, le modèle de l'OIT, OG-Core). Toutes passent à
`epuise`. Le registre des modèles les avait lues le 4 octobre, l'étape 138.11
en avait refait les diviseurs le 14 ; chaque source a été rouverte ce jour,
sa version ou la tête de son dépôt vérifiée.

- *L'indice d'équilibre suédois, refait.* Le rapport orange donne son bilan
  en millions de couronnes : la recette de cotisation de 2025, 366 783
  (tableau 6.6), fois la durée de rotation de 2024, 76,31936 − 45,31928 =
  31,00008 ans (tableau 6.8), plus le fonds tampon, 2 233 988, sur la dette,
  11 858 539 (tableau 2.2). `BilanCompte` en refait l'indice de 2027, 1,1472,
  au dix-millième, et l'actif de cotisation à deux millions près, la recette
  étant arrondie : l'identité du bilan du dépôt est celle de l'ordonnance
  2002:780 (formules B.1.1, B.1.2 et B.3.1 de l'annexe B), et ses âges
  prennent le même milieu d'année, i + 0,5. Le cas d'essai est dans
  `tests/test_bilan_compte.py`.
- *Ce que l'annexe B apprend au bilan du compte.* La loi suédoise ne lit pas
  les deux âges sur la pyramide de l'année : l'âge des cotisations pèse les
  droits par tête de chaque âge par une survie tirée des effectifs d'une
  année sur l'autre (B.4.1 à B.4.5), l'âge de versement pèse les pensions par
  la survie des paiements, actualisée à 1,6 % (B.6.1 à B.6.3), et l'actif de
  l'année prend la durée de l'année d'avant. Sa durée de rotation est celle
  d'une population stationnaire, « om bokslutsperiodens ekonomiska,
  demografiska och juridiska förhållanden vore konstanta » (p. 14). Celle du
  dépôt pèse les profils par les effectifs réels (`profils_par_age`) : la
  limite que la note de l'étape 19 avait relevée, la formule suédoise l'ôte
  par construction. Le point est au registre (`balanstal_suede`,
  `a_reprendre`, 138.19) ; la session de l'étape 19 qui tourne aujourd'hui
  mène la carrière heurtée, et `bilan_compte.py` n'est pas touché.
- *La Pologne, à ses trente et un âges ronds.* Le cas d'essai ne jouait que
  sept âges du communiqué du 25 mars 2026. Il joue maintenant tous ceux de
  60 à 90 ans : trente se refont au dixième de mois, et 64 ans tombe sur le
  fil de l'arrondi. Les colonnes en entiers de la table D de 2025 y donnent
  T64 / l64 = 1 665 185 / 86 256 = 19,30515 ans, que le GUS écrit 19,31,
  soit 231,7 mois ; l'espérance refaite des quotients publiés, 19,30485,
  donne 231,6. Un arrondi, non une règle : le test le dit, à part.
- *La Finlande : le coefficient de 1964 ne se refait pas exactement.* L'ETK
  publie les coefficients de 1947 à 1964 (0,94643 pour 1964), mais seul le
  mémo de 2023 porte ses quotients, et il est déjà refait au millionième ;
  ceux de 2024 et de 2025 ne sont pas en ligne. Sur les quotients annuels de
  Statistics Finland (tables 12ap et 12ag de PxWeb), aucune façon simple de
  cumuler cinq années ne redonne ceux du mémo (27 à 34 écarts sur 38) ;
  cumulés par leurs décès, ils refont les coefficients de 1960 à 1964 à
  quatre cent-millièmes près, toujours par excès (0,94646 pour 1964). Rien
  n'entre au test : la formule y est déjà exacte, et l'écart tient à la
  construction des quotients, que l'ETK ne publie pas.
- *Ce qui n'a pas bougé.* Pensionsmodellen 2.2 et Typfallsmodellen 4.8 ;
  le portage non officiel de ce dernier a avancé de `bb46d93` à `3f3ad9f`,
  une mémoire des facteurs de rente, sans changer leur calcul. Les trois
  prescriptions de 2026 : le § 2 de PFS 2026:2 donne à la génération 1963 les
  diviseurs de la génération 1960, une table du moment. MOSART 7.5 décrit sa
  machine (C#, tirages, versions), non l'arithmétique du compte, qui se lit
  chez NAV. Le rapport n° 27 de la RGS, le décret italien du 20 novembre 2024
  (sa révision pour 2027 n'a pas été trouvée ce jour), la loi brésilienne de
  1999, le PROST de 2019, le guide de l'OIT de 2018 (l'outil reste derrière un
  compte) : déjà lus en entier au registre. OG-Core est passé de `b690537` à
  `81f4549` (la 0.21.2, trente-quatre commits sur les pensions à prestations
  définies et la sécurité sociale américaine) : ses trois écarts tiennent.
- *Ce qui attend le propriétaire*, déjà au registre en `a_trancher` : le
  frein suédois et son accélérateur, la réversion dans le diviseur (Italie),
  le terme des versements, les gains d'héritage et les frais (Suède), le
  capital initial et les salaires manquants (PROST). Aucune saisie à
  proposer : le lot n'a pas de simulateur.
- *Ce que le lot suivant trouvera* : vingt et une lignes `a_explorer`. Trois
  sont du COR et se lisent sans personne : les documents de la séance du 5
  mars 2020 et du suivi statistique de 2024, et son simulateur, « fermé pour
  révision » au dernier passage. Dix sont des modèles du registre : les
  barèmes de l'IPP, à recouper table par table (le scénario 1, sur Opus), et
  neuf dans les zones de 138.3, 138.5, 138.7 et 153 (le net et l'impôt, la
  page Coût, OpenFisca). F33841 est à 138.12 ; deux sont des simulateurs
  d'Union Retraite ; les cinq dernières attendent le propriétaire (le lot des
  simulateurs, Légifrance, Gallica).
- *Fichiers.* `data/sources_a_explorer.yaml`, le registre
  (`balanstal_suede`), `tests/test_bilan_compte.py`,
  `tests/test_diviseur_exemples_officiels.py`, cette note et l'entrée du
  journal de veille. Ni fiche, ni témoin, ni page : le scénario 1 n'est pas
  touché.
