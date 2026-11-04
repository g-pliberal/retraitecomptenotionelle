# Relecture des taux de la cotisation agricole de 2003 à 2025

File R-K-ter, vague 6, le 4 novembre 2026 : relecture indépendante des retouches de la file K-ter
(commits 3b06c54 et a0835b3 ; note `2026-11-04-retouches-de-la-relecture-r-k-bis.md`), qui
répondent à la relecture R-K-bis (cd360d1). Rien n'est repris de K-ter ni de mémoire : chaque
texte est rouvert dans les index LEGI (à jour au 2 novembre 2026) et JORF (au 3 novembre 2026)
de la DILA, récupérés ici (`dila_index.py legi --recuperer`, puis `jorf`), par
`dila_cherche.py --num`, `--diff`, `--le` et `--texte` ; chaque somme est refaite en décimaux par
un script de brouillon hors du dépôt ; l'historique git est rendu entier
(`git fetch --unshallow`). Aucune règle, donnée, fiche ni aucun test n'est modifié.

**Verdict : conforme.** Les taux de D. 731-121, D. 731-122 et D. 731-124 de 2003 à 2025 sont
ceux de la table de K-ter, au centime, année par année ; le décret n° 2024-688 date bien de 2026
les 2,36 % ; les 120 citations de la fiche sont exactes, mot pour mot ; les trois contrôles
(tests, paquet, `git status`) sont ceux qu'on attend. **Aucun texte de l'index ne fixe 17,37 %.**
Deux écarts faibles (§ 1 bis, § 3), une observation hors de la tâche de K-ter (§ 1 ter).

## 1. Les taux de 2003 à 2025 : conforme

**Les textes ouverts.** Quatre articles du code rural, chacun en toutes ses rédactions
(`dila_cherche.py legi --num D731-121`, etc., puis `--texte` de chaque identifiant) : D. 731-121,
7 rédactions, du 22 avril 2005 au 1er janvier 2026 et au-delà ; D. 731-122, 8, jusqu'au 1er janvier
2026 ; D. 731-124, 10 (dont une « jamais en vigueur », LEGIARTI000028393428), jusqu'au 1er janvier
2026 ; D. 731-125, 7, jusqu'au 1er janvier 2014. D. 731-123, le b du 2° (collaborateur), n'entre
pas dans la somme du chef d'exploitation et n'est pas lu. Avant le
22 avril 2005 : le décret annuel, ouvert à part (décret n° 2003-1033, articles 12, 13, 16 et 17,
JORFARTI000002257033, …1278568, …1146400, …1090400 ; décret n° 2004-1064, articles 12, 13, 15 et
16, JORFARTI000002499386, …1530372, …1673818, …2454542). Le sens des trois cotisations vient de
L. 731-42, lu aux rédactions du 1er janvier 2004 (LEGIARTI000006585488) et du 28 décembre 2023
(LEGIARTI000048683785) : 1° « calculée, dans la limite du plafond », 2° a) « calculée dans les
conditions définies au 1° », b) forfaitaire (aide familial, collaborateur), 3° « calculée sur la
totalité des revenus » : pour un revenu sous le plafond, le chef d'exploitation verse 1° + a du
2° + 3° ; le b du 2° n'est pas le sien. L'index n'a aucune rédaction de D. 731-122 ni de
D. 731-124 après le 1er janvier 2026, ni de D. 731-125 après le 1er janvier 2014.

**Le tableau.** Pour un revenu sous le plafond, en pour cent du revenu ; la colonne « Compl. » est
la cotisation complémentaire de D. 731-125 (sur la partie plafonnée + sur la totalité, aux taux
moyens, à ± 5 % par arrêté préfectoral), que D. 731-122 contient depuis le 1er janvier 2014 ;
« …N » est LEGIARTI + N complété de zéros à douze chiffres. Sommes et écarts refaits en décimaux.

| Année | 1° | a du 2° | 3° | Somme | 17,37 − somme | Compl. | Somme avec compl. | 17,37 − somme | Textes ouverts |
|---|---|---|---|---|---|---|---|---|---|
| 2003 | 3,20 | 8,44 | 1,29 | 12,93 | 4,44 | 2,53 + 0,25 | 15,71 | 1,66 | décret n° 2003-1033, art. 12, 13, 16, 17 |
| 2004 | 3,20 | 8,44 | 1,34 | 12,98 | 4,39 | 2,53 + 0,25 | 15,76 | 1,61 | décret n° 2004-1064, art. 12, 13, 15, 16 ; D. 731-121, -122, -124, -125 du 22/04/2005 (…6597337, …341, …349, …353), « Pour l'année 2004 » |
| 2005 | 3,20 | 8,44 | 1,39 | 13,03 | 4,34 | 2,53 + 0,25 | 15,81 | 1,56 | …6597338, …342, …350, …354 (27/08/2005), « Pour l'année 2005 » |
| 2006 | 3,20 | 8,64 | 1,39 | 13,23 | 4,14 | 2,53 + 0,25 | 16,01 | 1,36 | …6597339, …343, …351, …355 (19/10/2006), « Pour l'année 2006 » |
| 2007 | 3,20 | 8,64 | 1,39 | 13,23 | 4,14 | 2,53 + 0,25 | 16,01 | 1,36 | …6597340, …344, …352, …356 (20/10/2007), « Pour l'année 2007 » |
| 2008 | 3,20 | 8,64 | 1,39 | 13,23 | 4,14 | 2,53 + 0,25 | 16,01 | 1,36 | rédactions « Pour l'année 2007 » jusqu'au 22/09/2008, puis …19506734, …729, …719, …715 (« 3, 2 % », « 8, 64 % », « 1, 39 % », sans année) |
| 2009 | 3,20 | 8,64 | 1,39 | 13,23 | 4,14 | 2,53 + 0,25 | 16,01 | 1,36 | …19506734, …19506729, …19506719 ; D. 731-125 …19506715, puis …21149863 (15/10/2009, taux fixés) |
| 2010 | 3,20 | 8,64 | 1,39 | 13,23 | 4,14 | 2,53 + 0,25 | 16,01 | 1,36 | les mêmes |
| 2011 | 3,20 | 8,64 | 1,39 | 13,23 | 4,14 | 2,53 + 0,25 | 16,01 | 1,36 | les mêmes |
| 2012 | 3,21 | 8,69 | 1,41 | 13,31 | 4,06 | 2,50 + 0,23 | 16,04 | 1,33 | …26140087 (3,21), …26140079 (8,69), …25095716 (1,41), …25095712 (2,50 ; 0,23), « pour l'année 2012 » (décret n° 2012-847, art. 12 ; décret n° 2011-2039, art. 1 et 3) |
| 2013 | 3,26 | 8,81 | 1,41 | 13,48 | 3,89 | 2,50 + 0,23 | 16,21 | 1,16 | …26140087 (3,26), …26140079 (8,81), …25095716, …25095712 |
| 2014 | 3,28 | 11,39 | 1,94 | 16,61 | 0,76 | fondue | — | — | …26140087 (3,28), …28393435 (11,39), …28435889 (1,94) |
| 2015 | 3,30 | 11,47 | 2,04 | 16,81 | 0,56 | fondue | — | — | …26140087 (3,30), …28393435 (11,47), …29924569 (2,04) |
| 2016 | 3,32 | 11,55 | 2,14 | 17,01 | 0,36 | fondue | — | — | …26140087 (3,32), …28393435 (11,55), …29924569 (2,14) |
| 2017 à 2023 | 3,32 | 11,55 | 2,24 | 17,11 | 0,26 | fondue | — | — | …26140087, …28393435, …29924569 (2,24) |
| 2024, 2025 | 3,32 | 11,55 | 2,24 | 17,11 | 0,26 | fondue | — | — | les mêmes ; le 2,36 % de …49904742 ne vaut qu'au 1er janvier 2026 (§ 2) |

**Les points d'où viennent les chiffres, un à un.**

- 2003 : « Pour la cotisation mentionnée au 1° […], le taux est fixé à 3,2 % » (art. 12) ;
  « un taux de 8,44 % » (art. 13) ; « égale à 1,29 % de la totalité des revenus » (art. 16) ;
  complémentaire « de plus ou moins 5 % d'un taux moyen de 2,53 % sur la partie plafonnée […] et
  de 0,25 % sur la totalité » (art. 17). Somme : 3,2 + 8,44 + 1,29 = 12,93.
- 2004 : décret n° 2004-1064, art. 12 (3,2 %), 13 (8,44 %), 15 (« La moitié du produit […] un
  taux de 1,29 % ; […] La moitié du produit […] un taux de 1,39 % », soit (1,29 + 1,39) / 2 = 1,34).
- 2005 à 2007 : « Pour l'année 2005 / 2006 / 2007 », chaque rédaction nommant son année : 3,2 % ;
  8,44 % (2005), 8,64 % (2006, 2007) ; 1,39 % ; complémentaire inchangée.
- 2008 à 2011 : rédactions du 22 septembre 2008, sans année (3,2 %, 8,64 %, 1,39 %) ; au 1er janvier
  2008, la rédaction en vigueur nomme 2007 ; les mêmes taux courent.
- 2012 : décret n° 2011-2039, art. 1 (6° : D. 731-122, 8,64 → 8,67 % ; 7° : D. 731-124, 1,39 →
  1,41 % ; 8° : D. 731-125, 2,53 → 2,50 % et 0,25 → 0,23 %) et art. 3, 1° (« au titre de l'année
  2012 ») ; décret n° 2012-847 du 2 juillet 2012, art. 12 : D. 731-121 « a) 3,21 % pour l'année
  2012 ; b) 3,26 % pour l'année 2013 ; c) 3,28 % pour l'année 2014 ; d) 3,30 % pour l'année 2015 ;
  e) 3,32 % à compter de l'année 2016 », D. 731-122 « a) 8,69 % pour l'année 2012 ; b) 8,81 % […] ;
  e) 9,05 % ». **Lecture littérale au 1er janvier 2012** : D. 731-121 est encore à 3,2 %
  (…19506734, jusqu'au 4 juillet 2012) et D. 731-122 à 8,67 % (…25095727) : 3,2 + 8,67 + 1,41 =
  13,28, et 16,01 avec la complémentaire, soit 0,03 de moins que la table. K-ter le dit (« Le texte
  ne dit pas ce que la caisse a appelé au premier semestre ») : la table prend les taux écrits
  « pour l'année 2012 ». Pas un écart.
- 2014 : décret n° 2013-1223 (JORFTEXT000028388007), art. 2, 13° (D. 731-122 : 8,69 / 8,81 / 8,89
  / 8,97 / 9,05 → 11,19 / 11,31 / 11,39 / 11,47 / 11,55 %, soit 2,50 de plus partout) et 14° (D.
  731-124 : 1,41 → 1,64 %, soit 0,23 de plus) ; sa notice : « Entrée en vigueur : le texte entre
  en vigueur le 1er janvier 2014 » et « le décret supprime toute référence aux notions de
  cotisations techniques et de cotisations complémentaires […], le taux global des cotisations
  sociales dues n'étant pas modifié ». Décret n° 2013-1290, art. 2, 2° (D. 731-124 : « est fixé à
  1,94 % ») et art. 9 (« aux cotisations de sécurité sociale dues au titre des périodes courant à
  compter du 1er janvier 2014 »). La rédaction à 1,64 % est « jamais en vigueur » dans LEGI
  (…28393428 : 2014-01-01 → 2013-12-31). Refait : avant la fusion, 3,28 + 8,89 + 1,41 + 2,50 + 0,23
  = 16,31 ; après, 3,28 + 11,39 + 1,64 = 16,31 ; puis 1,94 − 1,64 = 0,30 de plus : 16,61.
- 2015 à 2025 : décret n° 2014-1531, art. 5 (D. 731-124 : « a) 2,04 % pour l'année 2015 ; b) 2,14 %
  pour l'année 2016 ; c) 2,24 % à compter de l'année 2017 »), appliqué par l'art. 13, II (« aux
  cotisations de sécurité sociale dues au titre des périodes courant à compter du 1er janvier
  2015 ») ; D. 731-121 (…26140087) et D. 731-122 (…28393435) de 2012 et 2014 : 3,30 % puis 3,32 % ;
  11,47 % puis 11,55 %.

**Les bornes.** 17,37 − 12,93 = 4,44 (2003) ; 17,37 − 17,11 = 0,26 (2017 à 2025) : l'écart va de
0,26 à 4,44 points, comme l'écrit K-ter. 17,37 / 12,93 = 1,343 ; 17,37 / 17,11 = 1,015. La somme la
plus haute de 2003 à 2025 est 17,11 % (la complémentaire comprise, 16,21 % en 2013 au plus avant
la fusion) : aucune année n'atteint 17,37 %. La coïncidence que K-ter redit se refait : 3,32 +
11,55 + 2,50 = 17,37, avec 2,50 % de D. 731-125 (2012, 2013) ; et 11,55 − 9,05 = 2,50 : les 11,55 %
le comprennent depuis 2014, la somme le compterait deux fois.

**Aucune source du 17,37 %.** Recherche plein texte de « 17,37 » : 36 documents dans l'index LEGI,
45 dans l'index JORF (parcourus en partie : horaires, loyers, indemnité de chômage de 17,37 EUR).
Croisée avec « vieillesse », « agricoles », « rural » ou « cotisation(s) » : 1 document LEGI (le
barème de rachat de l'arrêté du 18 décembre 2009, « 17,37 % », versements de l'article
L. 351-14-1, LEGIARTI000021680097) et 15 documents JORF (allocation de chômage, monuments
historiques, avis de vacance d'emploi, convention nationale…), tous lus dans leur ligne de
résultat, aucun n'est un taux de cotisation des non-salariés agricoles. L'index ne couvre que le
champ social (`THEMATIQUE`) : l'absence n'y est pas une preuve d'absence au Journal officiel. Les
deux taux du modèle naissent au commit bdaecdbc (8 septembre 2026) :
`git log -S"taux_cotisation_retraite: 0.1737"` et `-S"0.085"` y remontent tous deux, dans
`data/reference/regimes/non_salaries.yaml` (période de 2003 sans fin à 0.1737).

## 1 bis. « Sans source ni note » (faible) : un peu fort

La fiche (question R-K-bis) dit du 17,37 % : il « naît, avec les 8,5 % d'avant, sans source ni
note, le 8 septembre 2026 ». À bdaecdbc, le régime `msa_non_salaries` portait pourtant
`source_id: msa_parametres` et `fiabilite: moyenne` (la page d'accueil de la MSA, que R-K-bis
nommait), et sa période de 2003 une note qui cite « le taux de 17,37 % qui figure ici n'a jamais
compris les 4 % de la RCO », sans le justifier. Il faut lire : sans texte qui le fixe, et sans note
qui le justifie. Le fond tient (§ 1) ; seul le mot « source » est à resserrer, par exemple au
prochain passage sur la fiche.

## 1 ter. Hors de la tâche de K-ter : le 17,37 % court aussi après 2025 (observation)

`msa_non_salaries.yaml` porte 0.1737 sur six périodes : 2003, 2004 à 2008, 2009 à 2010, 2011 à
2025 (les quatre où K-ter écrit sa phrase), et 2026 à 2027, 2028 sans fin, qui n'ont pas la
phrase. K-ter le sait (« Depuis 2026, non lu ici »). Lu ici, sans plus : D. 731-121 depuis le
1er janvier 2026 (LEGIARTI000053296666) dit que « les taux applicables à la cotisation prévue au 1°
de l'article L. 731-42 sont égaux à ceux fixés respectivement au I de l'article D. 633-3 du code de
la sécurité sociale pour la part calculée sur l'assiette retenue dans la limite du plafond […] et
au II du même article pour la part calculée sur la totalité de l'assiette » ; D. 633-3, rédaction
du 7 juillet 2024 (LEGIARTI000049904636), dit au I « 17,15 % » et au II « 0,72 % » ; D. 731-122 et
D. 731-124 n'ont plus de rédaction après le 1er janvier 2026. Ni 17,15 %, ni 17,87 % (17,15 +
0,72) ne sont 17,37 %. C'est une piste, non une lecture : la structure de L. 731-42 en 2026 et le
décret n° 2025-1417 ne sont pas relus ici.

## 2. Le décret n° 2024-688, article 6 : conforme

L'article 6 (JORFARTI000049888606), mot pour mot : « Les dispositions du présent décret, à
l'exception de celles de l'article 5, s'appliquent au calcul des cotisations et des contributions
dues par les travailleurs indépendants non agricoles […] au titre des périodes courant à compter du
1er janvier 2025. Les dispositions des articles 1er, 2 et 5 s'appliquent au calcul des cotisations
et des contributions dues par les travailleurs indépendants agricoles au titre des périodes
courant à compter du 1er janvier 2026. » L'article 5 (JORFARTI000049888585), 16° : « L'article
D. 731-124 est ainsi rédigé : a) Au premier alinéa, les mots : « des revenus professionnels ou de
l'assiette forfaitaire définis aux articles L. 731-14 à L. 731-22, est fixé à : » sont remplacés
par les mots : « de l'assiette déterminée en application des articles L. 731-15, L. 731-16 et
L. 731-22, est fixé à 2,36 %. » ; b) Les deuxième à quatrième alinéas sont supprimés » ; c'est la
rédaction LEGIARTI000049904742 (7 juillet 2024). Les 2,36 % ne s'appliquent donc aux agricoles qu'à partir de 2026 : de 2017 à
2025, le 3° reste à 2,24 % (…29924569, « c) 2,24 % à compter de l'année 2017 »). K-ter a raison de
reprendre R-K-bis : 3,32 + 11,55 + 2,36 = 17,23 ne vaut pas pour 2024 ni 2025 ; le maximum de
2003 à 2025 est 17,11 %. La note que LEGI met en tête de la rédaction du 7 juillet 2024 renvoie
encore au décret n° 2014-1531 : un reste de la rédaction précédente, que K-ter relève. Aucun
autre texte de l'index ne touche D. 731-124 entre 2015 et 2026. La lecture repose sur la clause
d'application de l'article 6 ; aucune pratique de la caisse n'est lue pour 2024 et 2025.

## 3. Les citations de la fiche : conforme, un écart faible sur la source de D. 732-77

**Les 120 citations**, comparées par un script de brouillon (`python -I`, hors du dépôt) à l'index
(`--texte <id>`, espaces réduits ; chaque « […] » ou « … » coupe la citation en fragments, chacun
cherché mot pour mot) : 119 sont exactes d'un bloc, sans autre normalisation. La 120e (décret
n° 2013-1223, JORFTEXT000028388007) joint par « » ; « » deux phrases de la notice, chacune exacte
à part : « Entrée en vigueur : le texte entre en vigueur le 1er janvier 2014. » et « Enfin, le
décret supprime toute référence aux notions de cotisations techniques et de cotisations
complémentaires qui ne sont plus pertinentes à la suite de la réforme, le taux global des
cotisations sociales dues n'étant pas modifié. ». Les 116 textes LEGIARTI portent une date
`en_vigueur` : elle est celle de l'index pour les 116.

**L'échantillon lu**, graine 20261104 (`random.Random(20261104).sample(range(120), 12)`), plus les
deux demandées : #0 (1123, rédaction du 5 juillet 1980, LEGIARTI000006581056), #2 (décret n° 83-664,
art. 9), **#12 (décret n° 87-664, art. 2, LEGIARTI000006770506)**, **#19 et #33 (article 1123,
rédaction du 20 janvier 1991, LEGIARTI000006581060)**, #26 (n° 91-912, art. 14), #29 (n° 92-793,
art. 13), #41 (n° 94-715, art. 16), #47 (n° 95-1038, art. 19), #49 (n° 96-679, art. 13), #63
(n° 99-725, art. 16), #75 (n° 2002-1228, art. 17), #80 (L. 731-42 du 1er janvier 2004), #83 (n°
2004-1064, art. 15), #94 (D. 731-122 du 19 octobre 2006) : 15 citations, toutes exactes, avec leur
position dans le texte de l'index.

**Le décret n° 87-664.** Son article 2, LEGIARTI000006770506, en vigueur du 14 août 1987 : « Le
montant des cotisations mentionnées à l'article 1123 (1°, a) du code rural, fixé par l'article 10
du décret du 31 juillet 1987 susvisé, est majoré de 4 p. 100. » : la citation de la fiche est cette
phrase, avec « 4 p. 100 ». Son intitulé dans la fiche (« portant majoration exceptionnelle pour
1987 des cotisations d'assurance maladie, invalidité et maternité ainsi que des cotisations
d'assurance vieillesse du régime de protection sociale des personnes non-salariées des professions
agricoles ») est celui de l'index. L'article 1er (LEGIARTI000006770505) majore de « 2,2 p. 100 » les
cotisations maladie des articles 3, 4 et 5 du décret du 31 juillet 1987, l'article 3
(LEGIARTI000006770504) est d'exécution : ce que dit K-ter.

**L'article 1123 de 1991.** LEGIARTI000006581060 court du 20 janvier 1991 au 1er janvier 1994 :
1993 est donc sous cette rédaction, et la fiche la cite d'abord, a, b et c, dans la version
`trois_taux_de_1993_a_2002`. La rédaction du 1er janvier 1994 (LEGIARTI000006581061) n'y est qu'une
fois. Aucune version de la fiche ne porte deux fois le même identifiant (contrôle par script, six
versions).

**Écart faible : D. 732-77 aplatit l'ordre des formules.** La note de K-ter (§ 5) dit que, pour P
entre 19,51 et 27,34, « le modèle applique la formule « T % = 3,19 x P - 57,23 » de D. 732-77
(LEGIARTI000006597491) ». Le modèle le fait (`taux_de_majoration_de_1952_a_1972`, de 19,51 à 27,34 :
3,19 × P − 57,23 ; au-delà : 1,93 × P − 22,74, plafonné à 45 %), mais le texte de D. 732-77 de
l'index range la première formule après le 1° (« 5 % […] entre 15 et 19,51. Le taux est déterminé
par la formule suivante : T % = 3,19 x P - 57,23 ») et la seconde après le 2°. C'est le décret
n° 86-1084, article 2 (LEGIARTI000006769405), qui lève l'ambiguïté : « 5 à 30 p. 100 et de 30 à 45
p. 100 selon que le nombre annuel moyen […] est compris entre 19,51 et 27,34 ou est supérieur à
27,34. Dans le premier cas, le taux est déterminé par la formule suivante : T p. 100 = 3,19 P -
57,23 Dans le second cas, il est déterminé par la formule : T p. 100 = 1,93 P - 22,74 ». Les
extrémités le confirment : 3,19 × 19,51 − 57,23 = 5,007 et 3,19 × 27,34 − 57,23 = 29,985 (de 5 à
30 %) ; 1,93 × 27,34 − 22,74 = 30,026 ; mais 1,93 × 19,51 − 22,74 = 14,91, qui ne vaut pas 5.
L'arithmétique de K-ter, refaite à partir de ses entrées (S = 60,095 6 ; P = S / 3 = 20,031 9 et
S / 2,5 = 24,038 2 ; 3,19 × 20,031 9 − 57,23 = 6,672 % et 3,19 × 24,038 2 − 57,23 = 19,452 % ;
19,452 − 6,672 = 12,78 points ; 60,095 6 × 2,473 812 = 148,665 € et 0,127 8 × 148,665 = 19,00 €
par an), est juste. Ses entrées (les points de 1952, 1971 et 1972, 6,18, 26,368 8 et 27,546 9, la
valeur de service 2,473 812 €) viennent du moteur : elles ne sont pas refaites ici, pas plus que
la perte de 21,05 € par an à k = 1969 ni le « rien jusqu'à k = 1955 ». Il fallait citer l'article 2
du décret n° 86-1084 pour l'appariement, que le code de 2005 a perdu. Faible : le résultat est
exact, la référence est la moins nette.

## 4. La reconstitution de 1990 : conforme

`git diff 8ea1ce7 79cbb6f -- docs/limites/5-ter-trajectoire.md` : l'ancre
`mesure(reconstitution?annee=1990)` passe de −9,6 à −9,7 % ; 8ea1ce7 est le parent de 79cbb6f
(`git log`), qui est le commit de la file K (la période de 1952 à 4,25 %). Elle vaut −9,7 % sur
5492e2a et au `HEAD` de ce jour. Ni la note de K (`2026-11-03-cotisation-de-1952.md`) ni celle de
K-bis (`2026-11-03-corrections-de-la-relecture-cotisation-de-1952.md`) ne portent « 9,7 » : ce que
K-ter dit. Aucun taux du modèle n'a changé : `git show 3b06c54 --
data/reference/regimes/msa_non_salaries.yaml` n'ajoute que quatre phrases de note (les périodes de
2003, 2004 à 2008, 2009 à 2010, 2011 à 2025) ; `taux_cotisation_retraite` y est inchangé ; a0835b3
ne change dans `moteur/donnees.json` que quatre champs `"notes"` (quatre lignes ôtées, quatre
mises), qui sont ces quatre périodes.

## 5. Les tests et le paquet : conforme

- `python -m pytest -m rapide`, sur fc27dec2 : 4 409 réussis, 6 sautés, 13 en échec, tous dans
  `tests/test_pages_en_dossier.py` (dix `test_une_page_toute_faite_est_a_jour` et trois
  `test_le_corps_d_une_page_toute_faite_est_son_rendu`) : les treize rouges connus des pages
  toutes faites, que GitHub refait.
- `python scripts/construire_donnees.py` puis `git status` : rien à commiter (paquet de 5 914 Ko,
  arbre propre).

## À reprendre

- Au propriétaire : la question de K-ter ne change pas (le taux de 17,37 % du compte de 2003 à
  2025, que les textes ne donnent pas : 12,93 à 17,11 %). La table du § 1 en est la réponse écrite,
  avec ses textes.
- À la session suivante de l'action 131 : resserrer « sans source ni note » (§ 1 bis) ; citer le
  décret n° 86-1084, article 2, avec D. 732-77 pour l'appariement des formules (§ 3) ; lire les
  taux de 2026 (D. 633-3 du code de la sécurité sociale, décret n° 2025-1417) et dire, dans la fiche
  du régime, si le 17,37 % des périodes de 2026 en reste aussi sans source (§ 1 ter).
