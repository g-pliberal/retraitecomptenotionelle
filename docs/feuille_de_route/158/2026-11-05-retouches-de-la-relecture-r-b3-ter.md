# Retouches de la relecture R-B3-ter : le rang de `rangs_grille`, le n° 91-783, la grille de 2017 des IEEAC

Vague 7, le 5 novembre 2026. La relecture R-B3-ter
(`2026-11-04-relecture-corrections-r-b3-bis.md`, commit a8ef9d3) trouve les retouches de
B3-ter justes à la source, chaque écart de R-B3-bis corrigé, sans écart grave ni moyen :
deux écarts faibles et une remarque en amont. Cette note les reprend. **Aucun code, aucune
donnée, aucun test n'est touché** : les deux premiers écarts sont écrits dans
`scripts/fetch/dila_legi_chainage.py`, dans le fichier `reclassements.csv` que ce script
écrit, et dans `tests/test_chainage_grilles.py` ; ils restent à une session qui écrit du
code, test d'abord. Cette note dit, de chacun, ce qu'il faut écrire, après avoir rouvert
chaque pièce.

**Pièces rouvertes pour cette note** : l'index LEGI, à jour au 4 novembre 2026 (table
`doc`, ouverte en lecture seule) ; `data/reference/grilles/etat/echelons.csv` (Noyau RH) ;
`data/reference/grilles/etat_legi/echelons.csv` ; `data/reference/grilles/chainage/reclassements.csv`.

## 1. `rangs_grille` est la place de l'échelon dans sa grille le jour du reclassement

Ce que le fichier écrit : au groupe « Major de police Major de police » du texte
LEGITEXT000005971737, article LEGIARTI000023734900, reclassé le 2011-07-01,
`rangs_grille` vaut « origine exceptionnel 4 ; accueil exceptionnel 5 » (grilles
d'origine 02774 et d'accueil 02777).

Ce que le Noyau RH porte, rouvert : la grille 02777, du 2011-07-01 au 2011-12-31, a les
rangs 1 (581), 2 (598), 3 (616), 4 (620) et **6** (631, nature « exceptionnel »). Le rang 5
n'existe pas ce jour-là. L'échelon exceptionnel y est donc le cinquième échelon de la
grille, et c'est le rang 6 qui le désigne au Noyau. **`rangs_grille` n'est pas la colonne
`rang` du Noyau RH** : c'est la place de l'échelon parmi ceux que la grille a ce jour-là
(élève, stagiaire et provisoires mis à part), calculée par `rang_dans_la_grille`. La
relecture le demande ; l'en-tête du fichier ne le dit pas.

L'en-tête de `reclassements.csv` est écrit par le script (`ENTETES["reclassements"]`,
l. 1144 à 1152 de `scripts/fetch/dila_legi_chainage.py`) ; il dit « rangs_grille : le
rang, dans sa grille (élève, stagiaire et provisoires mis à part), de chaque échelon du
groupe que le tableau ne numérote pas (« accueil exceptionnel 5 ») ; il l'emporte sur le
rang de reclassements/lignes.csv ». **À y ajouter** : « Ce rang est la place de
l'échelon parmi ceux de la grille le jour du reclassement, non la colonne `rang` du Noyau
RH, qui donne 6 à l'exceptionnel de la grille 02777 le 2011-07-01 (rangs 1 à 4, puis 6) ».
La docstring de `periodes_noyau` (même script, l. 444) dit déjà que « le rang ordonne les
échelons sans les numéroter » ; elle ne dit pas que le rang du noyau d'un exceptionnel peut
sauter un numéro (1 à 4, puis 6) : la même précision lui revient. Ce sont des chaînes que le
script écrit dans un fichier : un changement de code, et de fichier fabriqué, pour une
session qui le fait, test d'abord. Rien n'est écrit ici dans le CSV, que le script refait.

## 2. Le n° 91-783 n'a pas d'article qui énumère ses corps

Deux commentaires supposent un tel article : celui de `COMMUNS`
(`scripts/fetch/dila_legi_chainage.py`, l. 598 à 604 : « Les décrets communs à plusieurs
corps dont l'article qui énumère les corps […] n° 91-783, les assistants de service
social) ne sont pas lus ») et celui de
`test_deux_corps_qui_citent_le_statut_et_ont_les_memes_grades_ne_se_rattachent_pas`
(`tests/test_chainage_grilles.py`, l. 252 : « L'article qui énumère les corps de ce
décret n'est pas lu ici »). Le texte, rouvert dans l'index :

- **art. 1**, LEGIARTI000006461848 (du 1992-02-08 au 2007-05-03) : « Les corps
  d'assistants de service social des administrations de l'Etat, classés dans la catégorie
  B prévue à l'article 29 de la loi du 11 janvier 1984 susvisée, sont soumis aux
  dispositions communes du présent décret. » La rédaction suivante, LEGIARTI000006461849
  (du 2007-05-03 au 2012-10-01), ajoute « et à celles du décret n° 94-1016 du 18
  novembre 1994 » : elle désigne de même les corps par leur catégorie.
- **art. 15**, LEGIARTI000006461873 (du 1991-08-20 au 2012-10-01) : « La durée moyenne et
  la durée minimale du temps passé dans chaque échelon sont fixées ainsi qu'il suit »,
  puis les grades « Assistant de service social principal » et « Assistant de service
  social ». Le tableau ne dit pas « régis par le présent décret ».

Aucun article n'énumère donc les corps du n° 91-783 : le décret les désigne par leur
catégorie (B) ; au Noyau RH, les deux corps 00671 (« Assistants de service social du MAE »)
et 00873 (« Assistants de service social ») citent le texte 112 (n° 91-783) pour origine
du 1991-08-01 au 2012-09-30 (`etat/corps.csv`, `etat/textes.csv`). **À écrire, dans les deux commentaires** :
« le n° 91-783 n'a pas d'article qui énumère ses corps : son article 1 les désigne par
leur catégorie, et son tableau (art. 15) ne dit pas « régis par le présent décret » ; la
règle de rattachement du n° 2012-762 ne s'y applique pas telle quelle, et la session qui
le rattachera écrira la sienne ». Ce que les textes ne tranchent pas : à quels corps du
Noyau RH, autres que 00671 et 00873, le tableau s'appliquerait.

## 3. La grille de 2017 des IEEAC mêle deux versions de l'article 2 du n° 2009-1322

Le LEGI porte, pour l'article 2 du décret n° 2009-1322 du 27 octobre 2009, deux versions
en vigueur ensemble du 2017-01-01 au 2018-01-01, rouvertes :

| version | période | colonnes | classe normale, 11e échelon |
|---|---|---|---|
| LEGIARTI000034034492 | du 2017-01-01 au 2018-01-01 | « A compter du 1er janvier 2017 », « A compter du 1er janvier 2018 » | « 11 767 774 » (767 en 2017, 774 en 2018) ; 1er échelon : 421 |
| LEGIARTI000037196211 | du 2017-01-01 au 2025-07-01 | « Au 1er janvier 2017 », « Au 1er janvier 2019 », « Au 1er janvier 2020 » | « 11e 774 780 780 » (774 en 2017) ; pas de 1er échelon de classe normale, le « 1er » (434) est celui de l'ingénieur stagiaire |

Les deux disent des indices différents pour la même année 2017 (767 et 774 au 11e
échelon ; 737 et 744 au 10e ; 1021 et 1022 au 9e de l'ingénieur principal). La grille que le
dépôt tire de ce texte, `etat_legi/echelons.csv`, grille
`ingenieur-des-etudes-et-de-l-exploitation-de-l-aviation-civile-de-classe-normale`
(LEGITEXT000021214923), prend en 2017 le 1er échelon de la première version (421,
LEGIARTI000034034492) et les échelons 2 à 11 de la seconde (483 à 774, LEGIARTI000037196211,
du 2017-01-01 au 2018-12-31), tous « certifiee ». **Ses indices de 2017 sont donc un
mélange de deux versions** : celui du 1er échelon (421) n'a pas d'équivalent dans la
seconde, et ceux des échelons 2 à 11 diffèrent de ceux de la première. Le rattachement de
2017 du chaînage tient (la première version a onze échelons, comme le tableau), comme R-B3-ter
le dit. **Ce que les textes ne tranchent pas** : laquelle des deux versions s'applique en
2017, le LEGI les donnant en vigueur ensemble ; ni la notice ni l'index ne le disent, et
aucun JORF n'a été ouvert pour cette note. C'est au lecteur des grilles de trancher, ou de
déclarer le conflit, avec le texte du JORF ; rien n'est changé dans `etat_legi/`.

## Le bloc « Reprise » de l'action 158

Récrit au 5 novembre 2026 (`docs/feuille_de_route.md`) : B3-ter relue conforme par
R-B3-ter, trois relectures du chaînage au total ; la suite rouge sous Python 3.11 réparée
par B3-quater (a084290, note du 4 novembre) ; ce qui reste, dont les trois points de cette
note.
