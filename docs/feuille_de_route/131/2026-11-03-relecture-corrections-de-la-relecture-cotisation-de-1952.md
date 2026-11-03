# Relecture des corrections de R-K : la cotisation agricole de 1952 et le taux d'avant 2003

File R-K-bis, vague 6, le 3 novembre 2026 : relecture indépendante du travail de la file K-bis
(commits 60584b2 et 076370f ; note `2026-11-03-corrections-de-la-relecture-cotisation-de-1952.md`),
qui répond à la relecture R-K (5cda0b8, `2026-11-03-relecture-cotisation-de-1952.md`). Rien n'est
repris de K-bis ni de mémoire : chaque texte est rouvert dans les index LEGI (à jour au
2 novembre 2026) et JORF (au 3 novembre 2026) de la DILA, récupérés ici
(`dila_index.py --recuperer`) ; chaque chiffre est refait à la main, ou au moteur Python par des
scripts de brouillon hors du dépôt, qui lisent ce que le moteur passe à la majoration
(`majoration_des_points_de_1952_a_1972_d_avant_2026`), sans rien y changer ; l'historique git
est rendu entier (`git fetch --unshallow`, 2 724 commits depuis le 8 septembre 2026). Aucune
règle, donnée, fiche ni aucun test n'est modifié.

**Verdict : conforme.** Les 80 citations de la fiche neuve sont exactes, mot pour mot, à la
version et à la date qu'elle dit ; les taux des décrets annuels sont ceux qu'elle donne ; aucun
texte de l'index ne fixe 8,5 % ni 17,37 % ; D. 732-77, l'article 2 du décret n° 86-1084 et
R. 732-67 ne tranchent pas le compte de 1952 dans P, et les deux effets se refont au centime ;
les écarts faibles de R-K sont corrigés, sauf un sous-point. **Ni la source du 8,5 % ni celle
du 17,37 % ne sont trouvées.** Un écart moyen, antérieur à K et hors de la tâche de K-bis (§ 2),
quatre faibles (§ 1, 3, 4).

## 1. Les citations de la fiche neuve : conforme, deux écarts faibles

**L'échantillon.** Les 80 citations, dans l'ordre de la fiche (versions, puis textes), tirées par
`random.Random(20261103).sample(range(80), 15)` : rangs 6, 11, 14, 17, 18, 20, 22, 24, 32, 57,
65, 67, 72, 75 et 77, chaque période y étant ; plus la citation seule d'avant 1983 (rang 0).
Chacune est ouverte dans l'index, lue en entier et comparée mot pour mot :

| Rang | Texte | Version de l'index | Exacte |
|---|---|---|---|
| 0 | article 1123, LEGIARTI000006581056 | 5 juillet 1980 → 8 janvier 1986 | oui |
| 6 | n° 85-735, art. 9, LEGIARTI000006768698 (plafond 27 751 F) | 20 juillet 1985 | oui |
| 11 | n° 87-612, art. 10, LEGIARTI000006770495 | 4 août 1987 | oui (voir plus bas) |
| 14 | n° 89-510, art. 9, LEGIARTI000006774421 (31 448 F) | 22 juillet 1989 | oui |
| 17 | article 1125, LEGIARTI000006581066 | 25 janvier 1990 → 1er janvier 1992 | oui |
| 18 | article 1123, LEGIARTI000006581060 (le c) | 20 janvier 1991 → 1er janvier 1994 | oui |
| 20 | n° 90-765, art. 13, LEGIARTI000006775081 | 30 août 1990 | oui |
| 22 | n° 90-765, art. 15, LEGIARTI000006775083 (0,67 %) | 30 août 1990 | oui |
| 24 | n° 91-912, art. 13, LEGIARTI000006776126 (7,41 %) | 14 septembre 1991 | oui |
| 32 | article 1123, LEGIARTI000006581061 | 1er janvier 1994 → 10 juillet 1999 | oui |
| 57 | n° 98-768, art. 13, LEGIARTI000006772343 (1,29 %) | 1er septembre 1998 | oui |
| 65 | n° 2000-952, art. 16, LEGIARTI000006779816 (1,29 %) | 29 septembre 2000 | oui |
| 67 | n° 2001-677, art. 11, LEGIARTI000006780051 (3,2 %) | 29 juillet 2001 | oui |
| 72 | n° 2002-1228, art. 13, LEGIARTI000006780889 (8,44 %) | 4 octobre 2002 | oui |
| 75 | n° 2003-1033, art. 12, LEGIARTI000006781102 (3,2 %) | 30 octobre 2003 | oui |
| 77 | n° 2003-1033, art. 16, LEGIARTI000006781106 (1,29 %) | 30 octobre 2003 | oui |

La date d'entrée en vigueur que donne la fiche est, pour chacune, celle de la version de
l'index, et la version couvre l'année que la fiche lui prête. Le même contrôle, par script, sur
les 80 citations et les trois textes sans effet : aucun écart.

**Les taux des décrets annuels**, relus dans chacun (article, taux, assiette) :

| Année | a (1°), plafonné | b (a du 2°), plafonné | c (3°), totalité | complémentaire, taux moyens |
|---|---|---|---|---|
| 1993 | 3,06 % (n° 93-1153, art. 12) | 8,140 % (art. 13) | 1,306 % (art. 14) | 2,30 % et 0,16 % |
| 1994 | 3,10 % (n° 94-715, art. 15) | 8,36 % (art. 16) | 1,34 % (art. 18) | 2,41 % et 0,16 % |
| 1995 | 3,10 % (n° 95-1038, art. 15) | 8,27 % (art. 16) | 1,26 % (art. 18) | 2,48 % et 0,24 % |
| 1996 à 1998 | 3,2 % | 8,445 % | 1,29 % | 2,53 % et 0,25 % |
| 1999 à 2002 | 3,2 % | 8,44 % | 1,29 % | 2,53 % et 0,25 % |
| 2003 | 3,2 % (n° 2003-1033, art. 12) | 8,44 % (art. 13) | 1,29 % (art. 16) | 2,53 % et 0,25 % (art. 17) |

Les fourchettes de K-bis (3,06 à 3,2 % ; 8,14 à 8,445 % ; 1,26 à 1,34 % ; 2,30 à 2,53 % et
0,16 à 0,25 %) sont exactes, et 2003 garde les taux de 2002. Les montants de 1983 et de 1989 aussi
(340 à 860 F, article 10 du n° 83-664 ; 532 à 2 010 F, article 10 du n° 89-510 ; plafonds de
23 359 F et 31 448 F, articles 9).

**Les décrets de 1990 à 1992**, dont la note de K-bis parle (§ 1, quatrième point) comme la fiche
(version `assiette_mixte_de_1990_a_1992`), disent ce qu'elles en rapportent. N° 90-765 : le a, un
montant par tranche, de 532 à 2 128 F (art. 13) ; le b, une part cadastrale et 2,25 % des
revenus « dans la limite du plafond » (art. 14) ; la complémentaire, à plus ou moins 15 % d'un
taux moyen de 0,67 % (art. 15). N° 91-912 : le a, de 532 à 3 020 F (art. 11) ; le b, une part
cadastrale et 7,41 %, moins une remise de 462 F (art. 13) ; le c, 1,155 % de la totalité, au
moins sur 400 SMIC (art. 14) ; la complémentaire, 1,78 % et 0,16 % (art. 15). N° 92-793 : le a,
un premier élément de 215 à 1 725 F (art. 12) et un second de 1,23 % (art. 13) ; le b, 8,105 %,
moins une remise de 504 F (art. 14) ; le c, 1,28 % (art. 15) ; la complémentaire, 2,17 % et
0,16 % (art. 16).

**Faible : le décret n° 87-664 manque.** Son article 2 (LEGIARTI000006770506, du 14 août 1987) :
« Le montant des cotisations mentionnées à l'article 1123 (1°, a) du code rural, fixé par
l'article 10 du décret du 31 juillet 1987 susvisé, est majoré de 4 p. 100. » L'index le signale
en tête de l'article 10 du n° 87-612 (« Décret 87-664 du 13 aôut 1987 art. 2 : majoration du
présent décret »). Les montants de 1987 que la fiche cite ne sont donc pas ceux qui ont été
réclamés, et sa liste des lectures ne le nomme pas. Sans effet sur le modèle, qui n'a pas le
revenu cadastral. C'est le seul décret de « majoration exceptionnelle » des cotisations des
non-salariés agricoles de 1983 à 2004 à l'index (recherche sur les titres).

**Faible : 80 citations, 79 articles ; 1993 sous la rédaction de 1994.** La version de 1993 à
2002 cite deux fois, mot pour mot, l'article 1123 du 1er janvier 1994 (LEGIARTI000006581061,
rangs 32 et 34). Et l'année 1993 relève de la rédaction du 20 janvier 1991 (LEGIARTI000006581060,
jusqu'au 1er janvier 1994), que la fiche ne cite qu'à la version de 1990 à 1992 : pour 1993,
celle de 1993 à 2002 cite un texte qui n'est pas encore en vigueur. Sans effet : les a, b et c
sont les mêmes, la rédaction de 1994 n'ajoutant au b que « une cotisation due pour chaque aide
familial majeur ».

## 2. Le 8,5 % et le 17,37 % : aucun texte ne les fixe ; un écart moyen antérieur à K

**Dans l'index.** Recherche plein texte, LEGI et JORF, jusqu'en 2004 : (« 8 5 » ou « 8 50 ») et
vieillesse et agricole(s) et cotisation(s). Un seul 8,50 % dans un texte de la vieillesse
agricole : le décret n° 65-314, article 3 (LEGIARTI000006763756, 1980 → 1988), « à 8,50 % desdits
salaires forfaitaires pour les périodes d'activité comprises entre le 1er octobre 1967 et le
30 septembre 1970 », le rachat de cotisations des salariés agricoles (loi n° 62-789), qui ne
touche pas les non-salariés. « 17 37 » avec les mots de l'agriculture ou de L. 731-42 : rien qui
porte sur une cotisation. De 1952 à 1982, le JORF n'a de ces textes que des notices, de 300 à
1 300 caractères (la loi n° 52-799 : 642 caractères, sans taux) ; LEGI n'a aucun décret annuel
de financement avant le n° 83-664 (23 juillet 1983). Ce que dit K-bis est exact.

**Dans le dépôt.** `git log -S"0.085"` et `-S"0.1737"`, sur l'historique entier : les deux taux
naissent ensemble au commit bdaecdbc (8 septembre 2026, « Add files via upload », le dépôt du
compte du propriétaire), dans `data/reference/regimes/non_salaries.yaml` : une période de 1952 à
2002 à 0.085, une de 2003 sans fin à 0.1737, sans note sur le taux, sous la source
`msa_parametres` (« Paramètres des régimes agricoles (RCO, points, AVA) », `https://www.msa.fr/`,
la page d'accueil de la caisse) et la fiabilité « moyenne ». Le modèle ne les tient de rien de
plus.

**Moyen, antérieur à K, hors de la tâche de K-bis : le 17,37 % court de 2003 à aujourd'hui.** La
fiche du régime le donne à toutes ses périodes depuis 2003 (2003, 2004 à 2008, 2009 à 2010, 2011
à 2025, depuis 2026), et la fiche neuve dit, honnêtement, que « les années suivantes ne sont pas
lues ici ». Lu ici : aucune rédaction de D. 731-121, D. 731-122 et D. 731-124 qui porte un taux,
de 2005 à 2025, n'en fait 17,37 %. De 2005 à 2008, de 3,2 + 8,44 + 1,29 = 12,93 % à
3,2 + 8,64 + 1,39 = 13,23 % ; depuis 2017, 3,32 % (D. 731-121,
LEGIARTI000026140087) + 11,55 % (D. 731-122, LEGIARTI000028393435) + 2,24 % (D. 731-124,
LEGIARTI000029924569) = 17,11 %, et 17,23 % avec les 2,36 % de la rédaction du 7 juillet 2024
(LEGIARTI000049904742) ; en 2003, 12,93 %. Seule la somme 3,32 + 11,55 + 2,50 tombe sur 17,37 %,
où 2,50 % est la complémentaire de D. 731-125 de 2012 à 2013 (LEGIARTI000025095712) ; mais la
rédaction de D. 731-122 du 1er janvier 2014 l'absorbe, chaque taux montant de 2,50 points
(8,69 → 11,19 % pour 2012, 9,05 → 11,55 % depuis 2016), et D. 731-125 n'a plus de rédaction
après 2014 : cette somme compterait deux fois les 2,50 %. Une coïncidence possible, pas une
source. La question au propriétaire de K-bis (§ 6, 1) vaut donc pour 2003 à 2025, pas pour
2003 seul.

## 3. La moyenne P : le texte ne tranche pas ; les effets se refont, un écart faible

**Les textes, aux versions en vigueur.** L'article 2 du décret n° 86-1084 (LEGIARTI000006769405,
du 8 octobre 1986 au 22 avril 2005, seule version), « pour le calcul des retraites
proportionnelles prenant effet postérieurement au 30 juin 1986 » : « le nombre annuel moyen de
points acquis par les intéressés au cours de cette période », celle « comprise entre le 1er
juillet 1952 et le 31 décembre 1972 ». D. 732-77 (LEGIARTI000006597491, du 22 avril 2005 au
1er janvier 2026) : « Le terme P figurant aux formules des 1° et 2° représente le nombre annuel
moyen de points acquis par l'assuré au cours de la période mentionnée au premier alinéa du
présent article. » R. 732-67 (LEGIARTI000053328816, depuis 2026, seule version) : les conditions
« relatives au nombre moyen de leurs points au titre de l'ensemble de la période comprise entre
le 1 er juillet 1952 et le 31 décembre 1972 », les majorations s'appliquant « séparément pour
chacune des années civiles comprises dans cette période ». La rédaction de 2026 de D. 732-77
(LEGIARTI000053365517) porte sur les versements de rachat. Aucun ne dit comment compter une
année que la période ne couvre qu'à moitié. Les décrets n° 97-163 (article 2,
LEGIARTI000006771705) et 2002-297 (article 5, LEGIARTI000006780505) disent bien, chacun pour sa
majoration, « en divisant le nombre de points retenu en application du 2° du I par la durée
reconstituée ». Ce que dit K-bis est exact, et le moteur compte 1952 pour une année (lecture A :
la moyenne divise par le nombre des années de chef qui ont cotisé).

**Les effets, refaits au moteur.** Valeur de service d'un départ de février 1989 :
2,473 812 €, celle que le moteur passe à la majoration.
- Le témoin `statut_exploitant_agricole_1925` : S = 372,935 1 points sur 21 années ; P = 17,758 8
  (A), S / 20,5 = 18,192 0 (B) ; 5 % dans les deux cas ; 46,128 6 € de majoration : rien ne
  change.
- Au plafond chaque année de 1952 à 1972 : S = 381,813 4, le même pour des départs de 1987
  (2,325 097 €), 1989, 1994 (2,803 838 €) et 1999 (2,982 18 €) ; P = 18,181 6 (A), 18,625 0
  (B) ; 5 % dans les deux cas.
- Au seuil de quinze points, n = 21 : S de 15 × 20,5 = 307,5 à 15 × 21 = 315 ; perte de A,
  0,05 × S × 2,473 812, de 38,035 € à 38,965 € (exclu) ; aux 4,589 € de 2025, de 70,56 € à
  72,28 €. Exact.
- 1952, puis 1966 à 1972, au plafond : S = 176,660 2 sur n = 8 ; P = 22,082 5 (A), 23,554 7
  (B) ; T = 3,19 P − 57,23 = 13,213 % et 17,909 % ; la pension de ces points, 437,024 € ; la
  majoration, 57,745 € (le moteur rend 57,745 1) et 78,269 € : 20,52 € de moins. Exact.
- R-K écrivait 39,5 € ; K-bis le corrige en 38,54 € (S = 15,2 × 20,5 = 311,6) : exact.

**Faible : « quelques points de taux » sous-estime l'écart de taux.** Pour la famille « 1952,
puis de k à 1972, au plafond, départ en 1989 », refaite pour k de 1953 à 1972 : rien pour k
jusqu'à 1955 ; la perte de A monte à 21,05 € par an (1952, puis 1969 à 1972 : 12,66 % au lieu de
20,43 %), l'ordre des 20,52 € de K-bis ; mais l'écart de taux va jusqu'à 12,78 points (1952,
puis 1971 et 1972 : 6,67 % au lieu de 19,45 %, 19,00 €). La note de K-bis (§ 6, 2) dit « quelques
points de taux pour des carrières interrompues après 1952 », et son « au plus de 5 % » ne vaut
que pour la bande du seuil. En euros, l'ordre qu'elle donne est juste ; la fiche
`retraite_proportionnelle_msa`, qui ne donne que des exemples, n'est pas en cause.

## 4. Les écarts faibles de R-K : corrigés, sauf un sous-point

- **Le renvoi du taux** : corrigé. La période de 1974 à 1985 de `msa_non_salaries.yaml` déclare
  « LE TAUX DE 8,5 % EST UNE CONVENTION, de 1953 à 2002 » ; celle de 1952 renvoie à elle et à la
  fiche neuve ; l'approximation de `cotisation_agricole_de_1952` dit son effet « non mesuré, la
  cotisation réelle de 1952 ne se chiffrant pas sans la loi n° 52-799 », sous un renvoi à la
  fiche neuve.
- **L'unité et le mécanisme du coût passé** : corrigés. Relu ici dans `agregats.json` aux deux
  commits : scénario 2 (`notionnel_retroactif`), 2 764 825,80 → 2 762 262,82 M€, soit
  −2 562,98 M€ ; `notionnel_liberal` et `notionnel_retroactif_employeur`, 6 386 967,96 →
  6 384 555,98 M€, −2 411,98 M€ ; garantie, +731,87 M€ ; `actuel`, 13 766 728,75 M€, inchangé.
  `cumul_passe` est « en Md€ constants », `annee_euros` vaut 2026, le README titre « Cumul
  1959-2024, euros de 2026 ». La note de K porte le renvoi daté. **Faible, non repris** : R-K
  relevait aussi que la note de K ne dit pas le déplacement de la reconstitution de 1990, et
  K-bis ne le dit pas davantage. Vérifié ici : l'ancre de `docs/limites/5-ter-trajectoire.md`
  passe de −9,6 % (8ea1ce7) à −9,7 % (79cbb6f), au commit de K.
- **`docs/chiffrage_plf.csv`** : laissé à GitHub, comme le veut la tâche ; toujours périmé en
  local.
- **La fiche absente de `veille_droit.py`** : expliqué (`transcrite`, lue le 3 novembre 2026) ;
  la fiche neuve y paraît, avec la question au propriétaire et ce qui reste au fac-similé.
- **La borne de l'arrondi** : corrigée, et juste. L'article 23 (LEGIARTI000019272750, du
  19 octobre 1952 au 9 juillet 1975) : « La cotisation réclamée aux assujettis est arrondie à la
  dizaine de francs inférieure » ; la perte est donc de moins de 10 anciens francs, 0,10 franc
  de 1960, 0,10 / 6,559 57 = 0,015 24 € par cotisation réclamée. L'article 22
  (LEGIARTI000019272741) notifie la cotisation cadastrale « au cours du premier mois de chaque
  semestre civil », et les cotisations des personnes des articles 8 et 9 « sont ajoutées à la
  cotisation cadastrale du deuxième semestre » : deux cotisations réclamées par an au plus,
  moins de 0,030 5 € par an, en euros du revenu de 1952, l'unité du modèle.

## 5. Les tests et le paquet : conforme

- `python -m pytest -m rapide`, sur 076370f : 4 346 réussis, 6 sautés, 13 en échec, tous dans
  `test_pages_en_dossier.py` (les pages toutes faites, que GitHub refait). Sous
  `PRESOMPTIONS_DECALEES=1` : 4 147 réussis, 205 sautés, les mêmes 13.
- Les fichiers qui lisent les fichiers touchés (`grep -l`) et les confrontations de la zone :
  `test_carte`, `test_conditions_selon_l_age`, `test_jumeaux`, `test_minima_agricoles`,
  `test_pension_minimum_avant_1983`, `test_periodes_assimilees`, `test_prelevements_historiques`,
  `test_regle_de_chacun`, `test_reversion`, `test_simulateur`, `test_oracle`, `test_destinie`,
  `test_estimation_officielle`, `test_verification`, `test_pont`, `test_contrats`,
  `test_donnees`, `test_prose`, `test_outillage`, `test_versions`, `test_univers`,
  `test_saisie_de_la_reversion_agricole`, `test_sources_a_explorer`, `test_net_pensions`,
  `test_textes` : 1 709 réussis, 1 sauté, 3 en échec dans `test_prose.py`, que GitHub refait :
  le tableau de bord, `chiffrage_plf.csv`, et le poids du paquet dans quatre ancres (5 905 →
  5 907 Ko). `test_cout` et `test_avantages` sont laissés à GitHub.
- `python scripts/construire_donnees.py` puis `git status` : rien à commiter (paquet de
  5 907 Ko).

## À reprendre

- Au propriétaire, en plus des deux questions de K-bis : le taux de 17,37 % du compte de 2003 à
  2025, qu'aucune somme des taux lus ne donne (§ 2).
- À la session suivante de l'action 131 : citer le décret n° 87-664 pour 1987, et la rédaction
  de 1991 de l'article 1123 pour 1993, dans la fiche neuve (§ 1).
