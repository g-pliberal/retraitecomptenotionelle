# Retouches de la relecture R-K-bis : le taux de 17,37 % du compte de 2003 à 2025, et quatre écarts faibles

File K-ter, vague 6, les 3 et 4 novembre 2026 : ce que la relecture R-K-bis
(`2026-11-03-relecture-corrections-de-la-relecture-cotisation-de-1952.md`, commit cd360d1)
relève. Chaque texte cité a été ouvert ici, dans les index LEGI (à jour au 2 novembre 2026) et
JORF (au 3 novembre 2026) de la DILA, récupérés (`dila_index.py --recuperer`), par
`dila_cherche.py --num`, `--diff` et `--texte` ; les citations de la fiche sont tirées de
l'index par un script de brouillon, qui vérifie que chacune y est mot pour mot. Aucune règle
ni aucun taux du modèle ne change : le 17,37 % se déclare, avec sa question au propriétaire,
et les écarts faibles se corrigent.

## 1. Le 17,37 % de 2003 à 2025 : aucun texte ne le fixe, aucune somme ne le donne (moyen)

Le modèle prélève au compte 17,37 % du revenu borné au plafond à chaque période de 2003 à 2025
de `msa_non_salaries.yaml` (2003, 2004 à 2008, 2009 à 2010, 2011 à 2025). La version
`depuis_2003` de `cotisation_vieillesse_agricole_avant_2003` cite maintenant, mot pour mot,
chaque rédaction de D. 731-121 (1° de L. 731-42, borné au plafond), D. 731-122 (a du 2°, borné
au plafond), D. 731-124 (3°, sur la totalité) et D. 731-125 (la cotisation complémentaire) que
l'index porte, les articles du décret annuel de 2004 (n° 2004-1064, articles 12, 13, 15 et 16,
avant la codification du 22 avril 2005), et les décrets qui datent les changements.

| Année | 1° | a du 2° | 3° | Somme | 17,37 − somme | Complémentaire | Somme | 17,37 − somme |
|---|---|---|---|---|---|---|---|---|
| 2003 | 3,2 | 8,44 | 1,29 | 12,93 | 4,44 | 2,53 + 0,25 | 15,71 | 1,66 |
| 2004 | 3,2 | 8,44 | 1,34 | 12,98 | 4,39 | 2,53 + 0,25 | 15,76 | 1,61 |
| 2005 | 3,2 | 8,44 | 1,39 | 13,03 | 4,34 | 2,53 + 0,25 | 15,81 | 1,56 |
| 2006 à 2011 | 3,2 | 8,64 | 1,39 | 13,23 | 4,14 | 2,53 + 0,25 | 16,01 | 1,36 |
| 2012 | 3,21 | 8,69 | 1,41 | 13,31 | 4,06 | 2,50 + 0,23 | 16,04 | 1,33 |
| 2013 | 3,26 | 8,81 | 1,41 | 13,48 | 3,89 | 2,50 + 0,23 | 16,21 | 1,16 |
| 2014 | 3,28 | 11,39 | 1,94 | 16,61 | 0,76 | fondue | 16,61 | 0,76 |
| 2015 | 3,30 | 11,47 | 2,04 | 16,81 | 0,56 | fondue | 16,81 | 0,56 |
| 2016 | 3,32 | 11,55 | 2,14 | 17,01 | 0,36 | fondue | 17,01 | 0,36 |
| 2017 à 2025 | 3,32 | 11,55 | 2,24 | 17,11 | 0,26 | fondue | 17,11 | 0,26 |

En pour cent du revenu, pour un revenu sous le plafond. D'où vient chaque taux :

- **2003** : décret n° 2003-1033, articles 12 (3,2 %), 13 (8,44 %), 16 (1,29 %) et 17 (taux
  moyens de 2,53 % et 0,25 %, à plus ou moins 5 % par arrêté préfectoral), déjà cités.
- **2004** : décret n° 2004-1064, articles 12 (3,2 %), 13 (8,44 %), 15 (« La moitié du produit
  obtenu en appliquant à la totalité des revenus […] un taux de 1,29 % » et la moitié à 1,39 %)
  et 16 (2,53 % et 0,25 %) ; les rédactions de D. 731-121, -122, -124 et -125 du 22 avril 2005
  redisent ces taux « Pour l'année 2004 ». Au 3°, (1,29 + 1,39) / 2 = 2,68 / 2 = 1,34 %.
- **2005 à 2007** : les rédactions du 27 août 2005, du 19 octobre 2006 et du 20 octobre 2007,
  chacune « Pour l'année » qu'elle nomme : 3,2 % ; 8,44 % en 2005, 8,64 % en 2006 et 2007 ;
  1,39 % ; complémentaire autour de 2,53 % et 0,25 %.
- **2008 à 2011** : les rédactions du 22 septembre 2008, sans année : 3,2 % (« 3, 2 % » dans
  l'index), 8,64 %, 1,39 % ; la complémentaire, préfectorale autour de 2,53 % et 0,25 %, puis,
  depuis la rédaction de D. 731-125 du 15 octobre 2009, fixée à ces taux.
- **2012** : D. 731-121 et D. 731-122 dans la rédaction du 4 juillet 2012 (décret n° 2012-847,
  article 12) : « a) 3,21 % pour l'année 2012 », « a) 8,69 % pour l'année 2012 » ; elles
  remplacent les 3,2 % de la rédaction de 2008 et les 8,67 % de la rédaction du 1er janvier 2012
  (décret n° 2011-2039, « au titre de l'année 2012 »). D. 731-124, 1,41 %, et D. 731-125,
  2,50 % et 0,23 %, dans leurs rédactions du 1er janvier 2012. **Le texte ne dit pas** ce que
  la caisse a appelé au premier semestre, sous les 3,2 % et les 8,67 % : la table prend les
  taux que les textes donnent « pour l'année 2012 ».
- **2013** : les mêmes rédactions : 3,26 %, 8,81 %, 1,41 %, 2,50 % et 0,23 %.
- **2014** : le décret n° 2013-1223, en vigueur le 1er janvier 2014, « supprime toute référence
  aux notions de cotisations techniques et de cotisations complémentaires […], le taux global
  des cotisations sociales dues n'étant pas modifié » (notice) ; son article 2 (13°, 14°) porte
  D. 731-122 de 8,69, 8,81, 8,89, 8,97 et 9,05 % à 11,19, 11,31, 11,39, 11,47 et 11,55 %, soit
  2,50 points de plus à chaque année, et D. 731-124 de 1,41 à 1,64 %, 0,23 point de plus. Le
  décret n° 2013-1290 (article 2, appliqué « aux cotisations […] dues au titre des périodes
  courant à compter du 1er janvier 2014 », article 9) remplace le même jour D. 731-124 par
  1,94 % ; la rédaction à 1,64 % n'a jamais été en vigueur (déclarée sans effet). Vérifié à la
  main : avant la fusion, 2014 aurait pris 3,28 + 8,89 + 1,41 + 2,50 + 0,23 = 16,31 % ; après,
  3,28 + 11,39 + 1,64 = 16,31 % : le taux global est le même ; puis 1,94 − 1,64 = 0,30 point de
  plus, 16,61 %. L'index n'a plus de rédaction de D. 731-125 après le 1er janvier 2014. La
  rédaction de 2014 récrit aussi 2012 et 2013 (11,19 % et 11,31 %) ; la somme de ces deux
  années, complémentaire comprise, n'en change pas : 8,69 + 2,50 = 11,19 et 8,81 + 2,50 = 11,31.
- **2015 à 2025** : D. 731-121 de 2012 (3,30 % en 2015, 3,32 % depuis 2016), D. 731-122 de 2014
  (11,47 %, puis 11,55 %), D. 731-124 du décret n° 2014-1531 (« a) 2,04 % pour l'année 2015 ;
  b) 2,14 % pour l'année 2016 ; c) 2,24 % à compter de l'année 2017 »).

Les sommes, posées à la main : 3,2 + 8,44 + 1,29 = 12,93 ; 3,2 + 8,44 + 1,34 = 12,98 ;
3,2 + 8,44 + 1,39 = 13,03 ; 3,2 + 8,64 + 1,39 = 13,23 ; 3,21 + 8,69 + 1,41 = 13,31 ;
3,26 + 8,81 + 1,41 = 13,48 ; 3,28 + 11,39 + 1,94 = 16,61 ; 3,30 + 11,47 + 2,04 = 16,81 ;
3,32 + 11,55 + 2,14 = 17,01 ; 3,32 + 11,55 + 2,24 = 17,11. La complémentaire ajoute
2,53 + 0,25 = 2,78 points de 2003 à 2011, 2,50 + 0,23 = 2,73 en 2012 et 2013. Les écarts, de
17,37 − 12,93 = 4,44 à 17,37 − 17,11 = 0,26 ; en rapport, 17,37 / 12,93 = 1,343 en 2003 et
17,37 / 17,11 = 1,015 de 2017 à 2025. Au-dessus du plafond, le 3° (et, jusqu'en 2013, la
complémentaire de 0,25 % puis 0,23 %) porte sur la totalité du revenu, que le modèle ne
prélève pas.

**Un point de R-K-bis à reprendre : les 2,36 % ne valent pas pour 2024 et 2025.** R-K-bis
(§ 2) donne « 17,23 % avec les 2,36 % de la rédaction du 7 juillet 2024 ». Cette rédaction de
D. 731-124 (LEGIARTI000049904742) vient de l'article 5 (16°) du décret n° 2024-688, dont
l'article 6 dit : « Les dispositions des articles 1er, 2 et 5 s'appliquent au calcul des
cotisations et des contributions dues par les travailleurs indépendants agricoles au titre des
périodes courant à compter du 1er janvier 2026. » De 2017 à 2025, le 3° reste donc à 2,24 %,
et la somme la plus haute de 2003 à 2025 est 17,11 %, non 17,23 %. La note que LEGI met en tête
de cette rédaction renvoie encore, comme celle de la rédaction précédente, au décret
n° 2014-1531.

**La coïncidence de R-K-bis, revérifiée** : 3,32 + 11,55 + 2,50 = 17,37, où 2,50 % est le taux
de D. 731-125 sur la partie plafonnée en 2012 et 2013 (LEGIARTI000025095712) ; mais
11,55 − 9,05 = 2,50 : les 11,55 % de D. 731-122 le comprennent depuis 2014, et cette somme le
compterait deux fois. Une coïncidence possible, pas une source. Depuis 2026, D. 731-121 renvoie
aux taux de D. 633-3 du code de la sécurité sociale (LEGIARTI000053296666), non lus ici.

**Ce qui est écrit.** La fiche : la version `depuis_2003` (44 textes, la table ci-dessus dans
son contenu), l'approximation `depuis_2003` (« LE TAUX DE 17,37 % N'A AUCUNE SOURCE », l'écart
année par année), une question au propriétaire, une lecture, une rédaction sans effet, le
`lit`, l'effet, l'historique. La fiche du régime : aux notes des périodes de 2003 à 2025, une
phrase qui le dit et renvoie à la fiche ; le taux n'y change pas.

## 2. Le décret n° 87-664 (faible) : cité

Son article 2 (LEGIARTI000006770506, du 14 août 1987) : « Le montant des cotisations
mentionnées à l'article 1123 (1°, a) du code rural, fixé par l'article 10 du décret du 31
juillet 1987 susvisé, est majoré de 4 p. 100. » Cité à la version
`montants_cadastraux_de_1983_a_1989`, dit dans son contenu et dans les lectures. Son article
1er majore de 2,2 % les cotisations maladie, son article 3 est d'exécution.

## 3. 1993 sous la rédaction de 1991 de l'article 1123 (faible) : corrigé

La version `trois_taux_de_1993_a_2002` cite d'abord la rédaction du 20 janvier 1991
(LEGIARTI000006581060, en vigueur jusqu'au 1er janvier 1994), ses a, b et c, mot pour mot ;
puis celle du 1er janvier 1994 (LEGIARTI000006581061), une fois : la seconde citation, mot pour
mot la même, est ôtée.

## 4. La reconstitution de 1990 (faible) : dite ici

Vérifié par `git diff 8ea1ce7 79cbb6f -- docs/limites/5-ter-trajectoire.md` : l'ancre
`mesure(reconstitution?annee=1990)` passe de −9,6 % à −9,7 % au commit de la file K (79cbb6f,
dont 8ea1ce7 est le parent), qui ne change au modèle que la période de 1952 de
`msa_non_salaries.yaml` (4,25 %). Elle vaut toujours −9,7 % sur 5492e2a. Ni la note de K ni
celle de K-bis ne le disaient.

## 5. « Quelques points de taux » (faible) : l'écart va jusqu'à 12,78 points

La note de K-bis (§ 6, 2) dit de la moyenne P, où le modèle compte 1952 pour une année (A)
plutôt qu'une demie (B), « quelques points de taux pour des carrières interrompues après
1952 ». Refait au moteur Python, par un script de brouillon qui lit ce que le moteur passe à
`majoration_des_points_de_1952_a_1972_d_avant_2026`, sans rien y changer, pour un chef au
plafond en 1952 puis de k à 1972, parti en février 1989 (valeur de service 2,473 812 €,
rendement 6 %) : rien jusqu'à k = 1955 ; la perte de A monte à 21,05 € par an (k = 1969) ;
l'écart de taux, à 12,78 points (k = 1971). Ce cas, posé à la main : les points de 1952, 1971
et 1972 valent 6,18, 26,368 8 et 27,546 9, S = 60,095 6 ; P = S / 3 = 20,031 9 (A) et
S / 2,5 = 24,038 2 (B), tous deux entre 19,51 et 27,34, où le modèle applique la formule
« T % = 3,19 x P - 57,23 » de D. 732-77 (LEGIARTI000006597491) : 3,19 × 20,031 9 − 57,23 =
6,672 % et 3,19 × 24,038 2 − 57,23 = 19,452 % ; 19,452 − 6,672 = 12,78 points ; la pension de
ces points, 60,095 6 × 2,473 812 = 148,665 €, en perd 0,127 8 × 148,665 = 19,00 € par an. En
euros, l'ordre que donne K-bis (20,52 €) est juste ; en taux, l'écart va jusqu'à 12,78 points.
La question au propriétaire ne change pas.

## Tests et paquet

`python -m pytest -m rapide`, puis sous `PRESOMPTIONS_DECALEES=1`, et les fichiers qui lisent
les fichiers touchés : voir le message de commit. `python scripts/construire_donnees.py` refait
le paquet, dont les notes de la fiche du régime font partie.

## À reprendre

- Au propriétaire, en plus des questions de K-bis : le taux de 17,37 % du compte de 2003 à
  2025 (§ 1), dont la fiche pose la question.
- Les taux depuis 2026 (D. 633-3 du code de la sécurité sociale, où renvoie D. 731-121) : non
  lus ici.

*Renvoi du 5 novembre 2026 : au § 5, la formule « T % = 3,19 x P - 57,23 » est celle du
« premier cas » du 2° de l'article 2 du décret n° 86-1084 (LEGIARTI000006769405), que D. 732-77
codifie en la plaçant sous le 1° ; voir `2026-11-05-retouches-de-la-relecture-r-k-ter.md`.*
