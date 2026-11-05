# Retouches de la relecture R-I-ter : le « total », l'écart à la cible, le 17 % de l'État civil

Vague 7, le 5 novembre 2026. La relecture R-I-ter
(`2026-11-03-relecture-etape-14-decote-depuis-1960.md`) trouve la note de la
décote d'après 1960 (`2026-11-03-etape-14-decote-depuis-1960-et-ecarts-de-r-i-bis.md`,
commits 207cb53 à 9649199, sur `main` à 5492e2a) conforme sur l'essentiel, avec
trois écarts faibles (commit de la relecture : 5492e2a). Cette note les corrige,
là où ils se lisent : le résumé de la note du 3 novembre est un récit et ne se
récrit pas ; elle renvoie ici. Aucune
règle, aucun chiffre, aucune donnée, aucun test du modèle ne change.

**Sources rouvertes pour cette note.** Le panorama de la DREES, « Les retraités
et les retraites – Édition 2026 » : le PDF du miroir de `data/sources.yaml`,
9 983 866 octets, SHA-256 `9eb36a06…ad86735e9be`, recalculée, celle du manifeste ;
p. 155 à 159 du PDF lues (texte extrait par `pdftotext`). La sortie de la mesure,
`docs/mesures/138/2026-11-03-etape-14-mesure-e12fe03.txt`, l. 167 à 196.

## 1. Le « total » du résumé est une fourchette construite

Le résumé de la note du 3 novembre écrit : « Le modèle tombe près du total
(génération 1960, 12,4 % tous régimes) par compensation ». Aucune source ne
publie ce total. Ce qu'il faut lire : le modèle, 12,42 % tous régimes pour la
génération 1960 (sortie, l. 179), tombe **près de ce que les parts publiées par
régime donnent à ses poids, de 11,6 à 12,8 %, non d'un total publié, qui
n'existe pas**. Cette fourchette est un calcul de la note, point 2 de « D'où
vient l'écart » : aux poids de la génération 1960, les parts publiées de la
génération 1957 par régime donnent 11,64 points sur les 93,97 % de la génération
qu'elles couvrent, et 11,6 à 12,8 % en tout si les libéraux et les régimes
spéciaux, qui n'ont pas de source, décotaient de 0 à 20 %. La note dit elle-même,
au même point, que « leur moyenne n'est pas une part tous régimes, et aucune
source ne la donne ». La seule part tous régimes publiée est celle des nés en
1953 (10,7 %, contre 11,6 % au régime général : graphique 4, p. 158 de l'ouvrage).

## 2. L'écart du modèle à sa cible, hommes et femmes, générations 1955 et 1960

La cible de la décision 17 est le flux de la Cnav de 2024 (régime général,
indépendants compris) : 13,00 % des hommes et 13,73 % des femmes pour les
générations nées depuis 1960 ; pour 1955, 9,21 % des hommes et 12,42 % des
femmes, qui ne sont pas publiés : la population les prend en droite ligne entre
les nés en 1953 de l'EIR (7,7 % des hommes, 11,9 % des femmes) et ces 13,00 et
13,73 de 1960 (`decotes_des_generations`, relu par R-I-ter, § 2). Ce que la
population rend, à 67 ans, à la condition, tous
régimes (sortie de la mesure, colonnes « cible » et « version », l. 169, 171,
181, 183) :

| génération | sexe | modèle | cible | écart du modèle, en points |
|---|---|---|---|---|
| 1955 | hommes | 10,04 | 9,21 | +0,83 (trop) |
| 1955 | femmes | 12,40 | 12,42 | −0,02 |
| 1960 | hommes | 11,66 | 13,00 | −1,34 (trop peu) |
| 1960 | femmes | 13,10 | 13,73 | −0,63 (trop peu) |

Qui lit « 13,0 % des hommes » comme la part de la population des nés depuis
1960 doit donc savoir que la population en rend **11,66 % à la génération 1960
(hommes)**, et 10,04 % pour 9,21 à la génération 1955. La note du 3 novembre
explique l'écart de 1965 (point 4 de « D'où vient l'écart ») ; **ceux de 1955 et
de 1960 ne sont expliqués nulle part, et cette note ne les explique pas non
plus** : elle les chiffre.

## 3. L'État civil de la génération 1957 : une troisième valeur, 17 %

Le texte de la fiche 17 du panorama, p. 156 de l'ouvrage (p. 157 du PDF), dit :
« Parmi les assurés nés en 1957, 17 % des retraités du régime de la FPE civils
sont partis avec une décote, contre moins de 15 % dans les autres principaux
régimes (13 % au régime général et 8 % à la CNRACL […]) ». La note de relecture
écrit « p. 155 » : à la lecture du PDF, la note 6 (génération 1957) est bien
p. 155 (p. 156 du PDF), mais cette phrase est une page plus loin, p. 156.

Trois valeurs, donc, pour l'État civil de la génération 1957, aucune source
ne départageant la lecture :

| source | part décotée, FPE civils, génération 1957 |
|---|---|
| le texte de la fiche 17, p. 156 | 17 % |
| le graphique 4, p. 158 (étiquette du dernier point, 15,8, attribuée au régime par le classeur que R-I-ter a lu) | 15,8 % |
| la table H de l'EACR (stock à 67 ans de 2024, au témoin) | 16,00 % |

La note du 3 novembre prend la table H ; elle relève l'écart du graphique à la
table, non celui du texte, plus grand (17 pour 16,00, 1 point). Cela ne change
aucun calcul : le 16,00 est celui du tableau des groupes et de la fourchette du
point 1. Le texte écrit aussi 13 % au régime général et 8 % à la CNRACL, pour
13,11 et 8,1 aux autres sources : ceux-là s'accordent à l'arrondi.

## Ce qui n'est pas fait

Rien qui touche au modèle : la cible par génération ou par groupe, les
fonctionnaires qui décotent, restent à la décision du propriétaire (décision 11).
Le bloc « Reprise » de l'étape 14 (note
`2026-10-07-etape-14-la-distribution-de-2020.md`) dit que R-I-ter est relue et
ce qui reste. Aucun texte de droit lu : pas d'entrée au journal de veille.
