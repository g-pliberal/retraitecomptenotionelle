# Étape 2, les reclassements : où passe l'agent de chaque échelon quand une grille en remplace une autre

**Le 3 novembre 2026 : les tableaux de reclassement que les statuts écrivent
quand ils refont une grille sont entrés dans le dépôt, lus au LEGI et
certifiés : 450 tableaux de 291 textes, 7 365 lignes, du 15 août 1969 à 2025,
sous `data/reference/grilles/reclassements/`. Chaque ligne dit l'échelon
d'origine, la condition d'ancienneté qui le partage parfois, l'échelon
d'accueil et l'ancienneté conservée, telle que le texte l'écrit. Ils redonnent
les articles des décrets n° 2016-596 (l'échelle 4 de la territoriale en C2),
2005-1228 (l'ancienne échelle 4 de l'État) et 2016-634 (les cadres supérieurs
socio-éducatifs de l'hospitalière). Rattacher chaque tableau aux grilles du
dépôt, le chaînage, reste à faire ; appliquer l'ancienneté conservée demande
les durées d'échelon.**

Demande : la session d'orchestration du 3 novembre 2026, file B, troisième
vague : « quand une grille en remplace une autre, à quel échelon de la nouvelle
passe l'agent de chaque échelon de l'ancienne, lu dans les textes officiels par
l'index LEGI et JORF » ; pas de site ; les grilles d'avant 1990, au seul
Journal officiel imprimé, hors de la tâche ; la question des durées d'échelon,
posée au propriétaire, à ne pas trancher, mais à éclairer.

- *Où sont les tableaux.* Non dans les textes d'échelonnement, que lit
  `dila_legi_grilles.py`, mais dans les statuts particuliers et les décrets qui
  organisent les carrières, que le filtre de l'index garde depuis sa
  reconstruction du 2 novembre 2026 : « Les fonctionnaires […] sont reclassés
  […] conformément au tableau de correspondance suivant ». L'index LEGI en
  compte environ 1 800 versions d'articles, dans un millier de textes, qui
  disent « reclassés » ou « intégrés » ; le JORF n'a pas été lu, le LEGI gardant
  chaque version d'article depuis l'entrée en vigueur des textes qu'il consolide.
- *Le récupérateur* (`scripts/fetch/dila_legi_reclassements.py`, test
  `tests/test_reclassements.py`). Il relit chaque tableau aplati : les échelons
  (« 11e échelon », « 1 er échelon », « Echelon unique », « échelon spécial »,
  « 2e échelon provisoire », « stagiaire ») ; les conditions qui partagent un
  échelon (« - à partir de 4 ans », « - avant 4 ans », « jusqu'à 1 an »,
  « avec moins de 3 ans d'ancienneté ») ; les phrases d'ancienneté (« 1/2 de
  l'ancienneté acquise », « Deux fois l'ancienneté acquise », « Ancienneté
  acquise au-delà d'un an », « majorée de six mois », « augmenté de 33 mois »,
  « dans la limite de 3 ans ») ; le libellé écrit entre deux lignes, grade
  d'origine puis grade d'accueil, que l'aplatissement colle l'un à l'autre, et
  qui devient le groupe des lignes suivantes ; l'en-tête, jusqu'à son dernier
  mot d'en-tête ; le titre de colonne qu'une ligne redit (« SITUATION
  NOUVELLE : », « Ancienneté conservée, dans la limite de la durée de
  l'échelon » devant la case). La date du reclassement est celle que la phrase
  écrit (« A compter du 1er janvier 2017 », « sont, au 1er août 1993,
  intégrés ») pour 49 tableaux, sinon l'entrée en vigueur de l'article ; la
  version suivante d'un article qui redit le même tableau ne fait pas un second
  reclassement. Le versant se lit comme celui des grilles, au titre puis aux
  visas.
- *Ce qui n'est pas lu.* Les tableaux de promotion et de recrutement, de même
  forme : un promu « reclassé » dans son nouveau grade n'a pas changé de grille.
  Refusés, plutôt que lus de travers, et consignés dans `non_lus.csv` (456) :
  une ligne sans ancienneté (406 : les tableaux d'assimilation pour la pension,
  qui n'ont pas cette colonne, les échelons comptés en indices, les mises en
  page que l'analyseur ne connaît pas), un tableau non reproduit au LEGI (14),
  un échelon nouveau qui baisse quand l'ancien monte (12), un tableau dessiné en
  caractères (11), des échelons d'origine dans le désordre (7) ou en double (6).
  Aucun tableau des militaires n'est lu : leurs reclassements comptent en
  années de services ou en indices.
- *Ce qu'il écrit.* `textes.csv` (532 textes, dont 291 avec un tableau lu :
  390 de l'État, 76 de la territoriale, 59 de l'hospitalière, 6 des militaires,
  un des deux versants civils à la fois) ; `tableaux.csv` (450 : 328 de l'État,
  74 de la territoriale, 48 de l'hospitalière ; 1 dans les années 1960, 5 en
  1970, 14 en 1980, 79 en 1990, 87 en 2000, 212 en 2010, 52 en 2020), avec la
  phrase qui annonce chacun et son en-tête ; `lignes.csv` (7 365 : 5 370, 1 225,
  770) ; `non_lus.csv`.
- *La certification.* `scripts/verifier_donnees.py` certifie le rang de
  l'échelon d'origine et de l'échelon d'accueil de chaque ligne (7 365 et
  7 365, toutes identiques) ; le journal ne reçoit que ces deux traces, la date
  de quatre séries d'autres zones, que le passage avait rafraîchie, rendue.
- *Le recoupement aux textes* (`tests/test_reclassements.py`). Les valeurs
  attendues sont lues dans les articles, non dans ce que rend le script :
  l'article 15 du décret n° 2016-596, ses douze lignes (le 12e échelon de
  l'échelle 4 au 9e de C2 avec l'ancienneté acquise, le 11e au 8e avec sa
  moitié, le 10e au 8e sans ancienneté…), au 1er janvier 2017 ; l'ancienne
  échelle 4 de l'État dans la nouvelle, un échelon plus bas, au 1er octobre 2005
  (décret n° 2005-1228) ; les cadres supérieurs socio-éducatifs, un échelon plus
  haut, « A compter du 1er janvier 2017 » quand l'article date de mai 2016
  (décret n° 2016-634). Les tests de l'analyseur rejouent des tableaux réels :
  les contremaîtres de France Télécom (n° 2016-219), les ingénieurs des travaux
  ruraux (n° 95-230), les sages-femmes surveillantes-chefs, les contrôleurs des
  finances publiques. Aucune publication tierce n'a été confrontée : un centre
  de gestion qui publie ses tableaux de reclassement de 2017 serait la
  prochaine.
- *Ce que la donnée ne dit pas.*
  - Le chaînage. Un tableau nomme ses grilles par son libellé (« SITUATION dans
    le grade en échelle 4 ») et par la phrase qui l'annonce (« un grade relevant
    de l'échelle 4 de rémunération instituée par le décret n° 87-1108 »), non
    par les clés de `grilles/<versant>/grilles.csv`. Les y rattacher, grille
    d'origine et grille d'accueil, est la suite.
  - Le groupe d'une ligne colle le grade d'origine et le grade d'accueil
    (« Contremaître Contremaître ») : l'aplatissement a perdu la case qui les
    séparait. Une condition garde parfois un libellé de grade écrit entre les
    deux échelons (76 lignes).
  - Les tableaux refusés, dont ceux des militaires, et ceux des textes d'avant
    leur première version consolidée, que seul le JORF imprimé porte.
  - L'arrêté du 5 novembre 1959 des emplois communaux est rangé à l'État,
    faute que `versant()` connaisse « communaux » ; il n'a aucun tableau lu.

*Ce que les reclassements attendent des durées d'échelon* (la question reste
au propriétaire). Un tableau place l'agent à la date du reclassement : il faut
savoir à quel échelon il est ce jour-là, et depuis quand. Trois choses en
dépendent. L'échelon d'origine : sans les durées de l'ancienne grille, on ne
sait pas où en est, à cette date, un agent entré dans le corps des années
plus tôt. La condition qui partage l'échelon (1 466 lignes : « à partir de
4 ans », « avant un an ») : elle se lit sur l'ancienneté acquise dans
l'échelon, donc sur la date d'entrée dans celui-ci. L'ancienneté conservée :
2 893 lignes la calculent (une fraction, une majoration, « au-delà de »),
4 096 la gardent entière, 376 la remettent à zéro, et 324 des 450 tableaux la
bornent « dans la limite de la durée de l'échelon » d'accueil ; puis la date du
prochain échelon, dans la nouvelle grille, dépend de la durée de celui-ci. Les
grilles, le barème et les reclassements sont donc là ; sans les durées, aucune
carrière ne se déroule de bout en bout sur eux. Le chaînage, lui, ne demande
pas les durées.

*Pour les autres files.* Rien pour le site. Des fichiers partagés ont reçu des
lignes : `scripts/verifier_donnees.py` (une source, deux certifications),
`tests/test_donnees.py` (les deux séries et leur fichier),
`data/derive/certification.json` (deux traces), `data/sources.yaml` (l'entrée
`dila_legi_reclassements`).

*Ce qui reste de l'action 158, étape 2.* Le chaînage : rattacher chaque tableau
à sa grille d'origine et à sa grille d'accueil ; les durées d'échelon (au
propriétaire : d'abord ?) ; les tableaux que l'index aplatit, reclassements
refusés compris ; le minimum de traitement ; les grilles d'avant 1990, d'un
poste.
