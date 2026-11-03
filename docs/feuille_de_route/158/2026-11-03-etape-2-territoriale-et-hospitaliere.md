# Étape 2, seconde moitié : les grilles de la territoriale et de l'hospitalière, lues au LEGI

**Le 3 novembre 2026 : les grilles de la fonction publique territoriale et de
la fonction publique hospitalière sont entrées dans le dépôt, tirées des
textes d'échelonnement indiciaire que l'index LEGI reconstruit garde, et
certifiées : 230 textes, 497 grilles, 7 545 périodes d'échelons, chacune avec
l'article qui la fixe. Leurs échelles C1 à C3, leurs agents de maîtrise et
leurs aides-soignants redonnent, indice pour indice, les grilles qu'un centre
de gestion et une fédération publient. Les durées d'échelon, que fixent
d'autres textes, et les grilles d'avant 1995, dessinées en caractères, restent
à faire. Le propriétaire a décidé que les militaires entrent au périmètre :
ce sera une étape à venir.**

Demande : la session d'orchestration du 2 novembre 2026, file B, pour la
seconde moitié de l'étape 2 : les grilles de la territoriale et de
l'hospitalière, lues dans les textes par l'index LEGI et JORF reconstruit.
Elle rapporte une décision du propriétaire, du 2 novembre 2026 : **les grilles
des militaires, qui ont leur propre barème (les indices de solde), entrent
aussi au périmètre**, à inscrire comme une étape à venir et à ne pas faire
dans cette session. La note du 2 novembre les rangeait encore parmi les
grilles de l'État ; elles ont désormais leur étape.

- *Le récupérateur* (`scripts/fetch/dila_legi_grilles.py`, test
  `tests/test_grilles_legi.py`). Il retient les textes dont le titre dit
  échelonnement indiciaire, échelles de rémunération, classement indiciaire
  ou grille indiciaire, et dont il lit le versant : la fonction publique
  territoriale ou hospitalière nommée, « territoriaux », « hospitaliers »,
  « établissements d'hospitalisation », la loi n° 86-33. Il écarte ceux de
  l'État — un ministère « des collectivités territoriales » n'en fait pas un
  texte de la territoriale —, ceux des corps hospitalo-universitaires, qui
  sont de l'État, et ceux qui modifient les trois versants à la fois. L'index
  ôte les balises : un tableau n'y est qu'une suite de mots et de nombres, où
  les cases vides ont disparu. L'analyseur le relit — les dates en tête des
  colonnes, quand « à compter du », « au », « à partir du » ou « depuis le »
  les introduit, et la colonne sans date de la version ; les échelles en
  colonnes ; les grades entre les lignes ; le rang nu ou l'ordinal seul devant
  l'indice (« 11e 801 ») ; deux grades côte à côte, que l'aplatissement
  entrelace ; l'échelon spécial et la lettre de hors-échelle ; « 1 027 » et
  « 1.000 » ; ce que le LEGI colle (« Indices brutsà compter », « 8eéchelon »).
  La réforme de la haute fonction publique porte l'indice brut des
  administrateurs jusqu'à 2 074 : la borne de l'analyseur est 2 200.
- *Ce qu'il refuse*, plutôt que de le lire de travers, chaque refus consigné
  dans `non_lus.csv` : les tableaux dessinés en caractères, de reclassement,
  d'indices majorés (ceux de 1985 donnent l'indice brut et l'indice nouveau
  majoré côte à côte), les indices extrêmes d'un grade sans ses échelons, une
  ligne de plus de valeurs que de colonnes, un échelon en double, un indice
  qui baisse quand l'échelon monte, et un indice resté dans un libellé, signe
  d'une mise en page qu'il ne connaît pas (« 681/660 », deux indices d'un même
  échelon, en 1986). La date d'un texte cité (« abrogé par l'arrêté du
  1er septembre 1989 ») n'ouvre plus de colonne : sans cela, l'indice nouveau
  majoré de 1985 passait pour l'indice brut de 1989, et le contrôle de l'ordre
  des indices ne le voyait pas.
- *La ligne courte.* Une ligne d'une valeur de moins que les autres n'a pas dit
  où était sa case vide. Première de son grade, c'est l'échelon le plus haut :
  à droite, il est créé à une date plus tardive ; à gauche, supprimé. L'ordre
  des indices tranche quand il n'admet que l'une des places (lecture
  « deduite » : en 2016, le 9e échelon de la classe normale des personnels de
  rééducation de l'hospitalière, à 621, passerait sous le 8e de 2018 à droite,
  il est à gauche) ; sinon, la place est présumée à droite (« presumee »).
  Ailleurs, le tableau est refusé.
- *Ce qu'il écrit*, sous `data/reference/grilles/territoriale/` et
  `.../hospitaliere/` : `textes.csv`, `grilles.csv` (une par groupe : grade,
  échelle, classe, sa clé tirée de son libellé), `echelons.csv` (l'indice
  brut ou la lettre de hors-échelle de chaque échelon, période par période,
  fin incluse, avec l'article du LEGI), `non_lus.csv`. Une période vaut de la
  date de sa colonne, ou du début de sa version si elle est plus tardive, à la
  veille de la suivante : une colonne qu'une version suivante a remplacée
  avant son effet ne s'applique jamais (le décret n° 2017-1737, qui reporte
  d'un an le protocole PPCR, décale ainsi les colonnes de 2018 à 2020 du
  décret n° 2016-604). Deux articles d'un texte qui nomment pareil un groupe,
  au même moment et avec les mêmes échelons, en décrivent deux : chacun prend
  son numéro d'article.
- *Les chiffres.* La territoriale : 75 textes, dont 61 avec une grille lue,
  280 grilles, 4 521 périodes, 201 versions d'articles lues et 87 non lues
  (43 en caractères, 26 sans échelon, 9 valeurs hors des lignes) ; la
  première période date du 15 mars 1986. L'hospitalière : 155 textes, dont 63
  avec une grille lue, 217 grilles, 3 024 périodes, 137 versions lues et 454
  non lues (227 en caractères, 70 sans échelon, 62 indices extrêmes, 53
  reclassements, 21 valeurs hors des lignes), dont 380 d'avant 2000 ; la
  première période date du 1er janvier 1990. 63 et 35 périodes y sont hors
  échelle.
- *La certification.* `scripts/verifier_donnees.py` relit
  `data/brut/dila_legi_grilles.json` et certifie le rang et l'indice de chaque
  période lue : 4 520 périodes de la territoriale, 3 016 de l'hospitalière ;
  les 1 et 8 périodes à la place présumée passent au niveau `estimee`. Le
  journal (`data/derive/certification.json`) ne reçoit que ces huit traces.
- *Le recoupement à des sources publiées* (`tests/test_grilles_legi.py`). Le
  centre de gestion de la fonction publique territoriale du Nord publie les
  « Échelles de rémunération de catégorie C, à compter du 1er janvier 2024 »
  (cdg59.fr, lu le 3 novembre 2026) : pour les échelles C1 à C3 (décret
  n° 2016-604) et les deux grades des agents de maîtrise (n° 88-548), l'indice
  brut et l'indice majoré au 1er janvier 2022, au 1er juillet 2023 et au
  1er janvier 2024. Les indices bruts du LEGI sont les siens aux deux dates,
  et le barème du Noyau RH, commun aux trois versants, redonne ses trois
  rangées d'indices majorés, échelon par échelon. La fédération UNSA Santé et
  Sociaux publie les grilles de l'hospitalière (mise à jour du 25 janvier
  2022, unsa-fp.org) : les indices majorés payés des échelles C1 à C3 au
  1er janvier 2022 (décret n° 2021-1827) et des deux grades des
  aides-soignants au 1er octobre 2021 (n° 2021-1267) sont ceux du barème,
  relevés au minimum de traitement que le LEGI date — l'indice majoré 340 du
  1er octobre 2021, 343 du 1er janvier 2022 (décret n° 85-1148, article 8,
  écrit par le n° 2021-1749) —, et sa valeur du point, 4,6860 €, est celle du
  dépôt. Le site du centre de gestion de la Haute-Garonne ne répond toujours
  pas.
- *Ce que la donnée ne dit pas.*
  - Les durées d'échelon : les textes d'échelonnement ne les donnent pas, les
    statuts et les décrets d'organisation des carrières si (n° 87-1107 puis
    2016-596 pour la catégorie C de la territoriale, 2010-329 pour sa
    catégorie B, 2006-227 puis 2016-636 pour la catégorie C de
    l'hospitalière, 2021-1257 pour ses aides-soignants…).
  - Avant 1995, l'essentiel : les tableaux en caractères (270 versions, dont
    212 d'avant 1990 à l'hospitalière et 36 d'avant 1995 à la territoriale)
    ne sont pas lus. Avant la première
    version consolidée d'un texte, le LEGI ne dit rien ; le JORF, que l'index
    garde aussi, n'a pas été lu.
  - Des trous que le LEGI laisse. Le décret n° 2006-228 ne donne que les
    bornes des échelles 3 à 6 de l'hospitalière, et l'arrêté qui fixait leurs
    échelons de 2006 à 2014 n'est pas dans l'index. L'arrêté du 29 janvier
    2014 y finit le 21 mai 2016, et celui du 19 mai 2016, qui l'abroge, ne
    donne ses échelles C1 à C3 qu'à compter du 1er janvier 2017 : de mai à
    décembre 2016, la catégorie C de l'hospitalière n'a pas de grille. Un
    texte abrogé implicitement reste ouvert au LEGI : l'arrêté du 23 juillet
    1998 des catégories C et D de l'hospitalière y paraît encore en vigueur ;
    les 93 et 76 grilles « en vigueur » au 3 novembre 2026 en comptent ainsi
    de trop.
  - Le chaînage. Une grille est celle d'un groupe d'un texte : la même
    échelle, refaite par un autre texte, ou renommée (« Attaché » en 2006,
    « Attaché territorial » en 2017), est une autre grille. Le passage de
    l'une à la suivante, et le reclassement d'un échelon à l'autre, restent à
    écrire.

*Pour les autres files.* Rien pour le site (file C). Des fichiers partagés
ont reçu des lignes : `scripts/verifier_donnees.py` (huit certifications et
leur source), `tests/test_donnees.py` (les huit séries et leur fichier),
`data/derive/certification.json` (leurs traces seules, celles des autres
séries rendues telles quelles), `data/sources.yaml` (l'entrée
`dila_legi_grilles`). Sur `main`, deux tests de `test_donnees.py` échouent
avant même ces commits : l'inventaire des régimes, que `construire_inventaire.py`
fabrique, n'a pas suivi la fiche de la CAFAT (file A) ; GitHub le refait.

*Ce qui reste de l'étape 2.* Les durées d'échelon de la territoriale et de
l'hospitalière, dans les statuts et les décrets de carrière ; les tableaux en
caractères, d'avant 1995 surtout ; le chaînage et les reclassements d'une grille à la
suivante, dans les trois versants ; l'histoire du barème avant novembre 2006,
au décret n° 82-1105 ; les grilles de l'État d'avant le noyau.
*L'étape qui vient, décidée le 2 novembre 2026 :* les grilles des militaires,
leurs indices de solde — décret n° 2009-21 pour les militaires non officiers,
n° 2009-22 puis 2011-388 pour la gendarmerie, ceux des officiers, que le
décret n° 2017-1362 modifie ensemble —, que l'index garde (51 versions
d'articles au 2 novembre).
