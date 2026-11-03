# Étape 2, les durées d'échelon : le temps à passer dans chaque échelon, lu dans les statuts au LEGI

**Le 3 novembre 2026 : la durée de chaque échelon que les statuts écrivent en
tableau est entrée dans le dépôt, lue au LEGI et certifiée : 762 tableaux de
336 textes, 14 345 lignes, du 12 septembre 1964 à 2025, sous
`data/reference/grilles/durees/`. Chaque ligne dit le grade, l'échelon, ses
durées en mois telles que le tableau les écrit (unique, moyenne, minimale,
maximale) et, chez les militaires, la condition d'accès qui tient lieu de
durée ; chaque tableau, l'article du LEGI et toutes ses versions qui le
redisent, et la période. 1 655 tableaux ou articles ne sont pas lus, chacun
avec sa raison. Le recoupement au Noyau RH de l'État donne 2 563 valeurs
égales sur 2 570 ; les 7 autres sont des zéros du noyau. Rattacher chaque
tableau aux grilles du dépôt reste à faire.**

Demande : la session d'orchestration du 3 novembre 2026, file B, quatrième
vague, sur une décision du propriétaire du même jour : « la durée de chaque
échelon des grilles des fonctionnaires — la faire avant le reste, puisque sans
elle aucune carrière ne se déroule sur les grilles ». Lire dans l'index, pour
chaque grille, la durée moyenne et, s'il y en a, les durées minimale et
maximale ou l'avancement accéléré, datée par ses versions ; la ranger à côté
des grilles, certifiée comme elles ; mettre de côté, avec sa raison, ce qui ne
se lit pas sans risque ; ne relier ni les reclassements ni les durées aux
grilles ; ne pas toucher au site. Exigence du propriétaire, le même jour :
aucune erreur, tout prouvé par écrit, jamais de mémoire.

- *La source.* L'index LEGI publié (`index-dila`, dump du 13 juillet 2025,
  incréments jusqu'au 2 novembre 2026 à 21 h 39), récupéré par
  `dila_index.py legi --recuperer` sans le reconstruire. Ses 7 880 versions
  d'articles de durées, 1 633 textes, mesurées par la session de l'index, se
  retrouvent : 7 880 articles, 1 633 titres. Le JORF n'a pas été lu.
- *Le lecteur* (`scripts/fetch/dila_legi_durees.py`). Il cherche la phrase qui
  annonce un tableau de durées (elle finit par « : » et dit « la durée du
  temps passé dans chacun des échelons », ou annonce un tableau dont
  l'en-tête dit « ANCIENNETÉ EXIGÉE dans l'échelon ») ; ni un reclassement ni
  un classement à la nomination, qui gardent l'ancienneté « dans la limite de
  la durée de l'échelon ». Il lit l'en-tête, qui donne les colonnes et leur
  ordre : « DURÉES Minimale Maximale » et « MAXIMALE MINIMALE » dans deux
  versions du même article, « DURÉE Moyenne Minimale », « DURÉE » seule, que
  la phrase dit moyenne, maximale ou unique. Puis chaque ligne : un échelon et
  autant de durées que de colonnes ; les échelons groupés (« 7e, 8e, 9e et
  10e échelons 3 ans », « 2e ,3e et 4e échelon »), développés ; le plus haut
  échelon, sans durée (« - », « / », « Echelon terminal », rien) ; les
  échelons des militaires sans le mot « échelon » (« 13e / 12e 3 ans ») ; la
  condition d'accès à l'échelon exceptionnel (« Après 13 ans de grade et
  avant 17 ans de grade »), qui n'est pas une durée ; le grade écrit entre
  deux lignes, et l'échelle de solde rangée sous son grade (« Colonel Echelle
  de solde n° 2 ») ; l'en-tête redit avant un grade, ôté du libellé. Une
  phrase arrête le tableau ; la ligne sans durée qu'elle aurait ouverte
  (« Le 8e échelon de la classe exceptionnelle est accessible… ») est ôtée.
  Une période réunit les versions consécutives d'un article qui redisent le
  même tableau (colonne `versions`).
- *Ce qui est refusé* (`non_lus.csv`, 1 655 lignes) plutôt que lu de travers :
  un libellé qui porte une durée ou un échelon (459, surtout les tableaux
  rendus en fiches, « Durée moyenne : 2 ans Durée minimale : 1 an 6 mois ») ;
  une durée hors de sa ligne (158) ; un grade qui ne descend pas au 1er
  échelon (76) ; une ligne qui n'a pas autant de durées que de colonnes
  (57) ; un échelon qui manque (22), en double (13) ou dans le désordre (7) ;
  une phrase qui coupe le tableau (38) ; les durées écrites d'un échelon au
  suivant (« du 1er au 2e échelon : 1 an », 35), qui se liraient décalées
  d'un échelon ; un en-tête d'une colonne quand la phrase en nomme deux (42) ;
  un en-tête redit dans un autre ordre (2) ; une durée minimale au-dessus
  d'une autre (6) ou de 252 mois (1) ; un tableau dessiné en caractères
  (115) ; aucun échelon après la phrase (119), moins de deux durées (5). Sont
  consignés aussi, sans tableau, les articles qui écrivent les durées en
  phrases (411 : « un an pour les quatre premiers échelons de la 2e classe ;
  deux ans pour… ») ou les renvoient à un autre texte (89 : « sont fixées à
  l'article 4 du décret du 20 septembre 1973 »).
- *Ce qu'il écrit.* `textes.csv` (720 textes, dont 336 avec un tableau lu :
  232 de l'État, 62 de la territoriale, 29 de l'hospitalière, 13 des
  militaires ; le versant est celui des grilles, les statuts militaires
  reconnus en plus à leur titre) ; `tableaux.csv` (762 : 495, 172, 78, 17 ;
  3 dans les années 1960, 5 en 1970, 12 en 1980, 175 en 1990, 91 en 2000, 287
  en 2010, 189 en 2020 ; 255 en vigueur) ; `lignes.csv` (14 345 : 8 154,
  3 143, 1 820, 1 228). Colonnes : la durée unique (443 tableaux), moyenne et
  minimale (209), maximale et minimale (72), moyenne seule (36), les autres
  (2). 1 449 lignes sans durée, le plus haut échelon surtout ; 74 avec une
  condition.
- *La certification.* `scripts/verifier_donnees.py` certifie, sous la clé
  « texte|article|tableau|ligne », le rang (14 345), la durée unique (8 507),
  moyenne (3 323), minimale (3 460) et maximale (1 058), toutes identiques à
  leur source ; séries `durees_echelon_*`. Le journal ne reçoit que ces cinq
  traces : la date de quatre séries d'autres zones, que le passage avait
  rafraîchie, est rendue.
- *Le test d'abord* (`tests/test_durees_echelon.py`, 21 tests). Les valeurs
  attendues sont lues à la main dans les articles, recopiés : l'État, les
  techniciens sanitaires (n° 92-1436, LEGIARTI000006470031, moyenne et
  minimale après une phrase de renvoi), les ingénieurs d'études (n° 83-1260,
  LEGIARTI000034794372), le service de dessin des PTT (n° 56-448,
  LEGIARTI000032192685, échelons groupés), l'ONF (n° 98-1262,
  LEGIARTI000006509643, groupés au singulier, dans l'ordre croissant), le
  grade provisoire du n° 95-83 (LEGIARTI000006476831, « Echelon terminal ») ;
  la territoriale, l'article 24 du décret n° 2010-329 dans trois versions
  (LEGIARTI000022021243 « Minimale Maximale », LEGIARTI000028542716
  « MAXIMALE MINIMALE », LEGIARTI000032542276 la durée unique), les
  contrôleurs de travaux (n° 95-952, LEGIARTI000006377526, « 2 ans 9mois »),
  les professeurs d'enseignement artistique (n° 91-857,
  LEGIARTI000006374077, l'en-tête redit), les biologistes (n° 92-867,
  LEGIARTI000034434471, la phrase qui suit) ; l'hospitalière, les ingénieurs
  de l'AP-HP (n° 93-145, LEGIARTI000037623011) ; les militaires, les gendarmes
  (n° 2008-952, LEGIARTI000026912312, dont la période réunit
  LEGIARTI000025074407) et les officiers du cadre spécial (n° 76-1001,
  LEGIARTI000052465264, l'échelle de solde sous son grade, la condition de
  l'échelon exceptionnel). Chaque comportement vu rouge, puis vert.
  `pytest -m rapide` : 4 231 réussis ; la garde des présomptions : 4 036 ; les
  fichiers de la zone (données, grilles, reclassements, index, durées,
  carte) : 394.
- *Les défauts trouvés en cours, et corrigés.* La première lecture laissait
  passer, sans les refuser : « 2 ans 9mois », lu 2 ans, le reste devenu un
  grade ; « 7e, 8e ,9e et 10e échelon », au singulier, dont seul le 10e était
  lu ; « Echelon terminal », pris pour un grade ; « n° 2 Echelon
  exceptionnel », lu 2e échelon ; une phrase finale qui ouvrait une ligne. Ils
  sont venus de l'audit des libellés (un grade qui porte « ans », « mois »,
  « échelon »), chacun reproduit par un test avant sa correction. Restent
  dans un libellé, sans effet sur les durées : « Echelon fonctionnel »
  (12 lignes), écrit dans la case du plus haut échelon.
- *La contre-lecture*, par un script de la session qu'elle n'a pas versé :
  pour chaque ligne qui a une durée, le segment du texte qui va de la mention
  de son échelon à la suivante, et ses durées recomptées par une autre
  expression. 12 392 lignes s'y retrouvent ; 471 sont des échelons groupés,
  qu'un segment ne peut isoler (68 dont le segment ne correspond pas, 403
  sans segment), tous vérifiés dans une liste du texte ; aucune autre.
- *Le recoupement au Noyau RH de l'État* (CISIRH, juillet 2026), par un
  script de la session qu'elle n'a pas versé. Un tableau de l'État se lie à
  un grade du noyau quand le numéro de son texte est celui d'un texte du corps
  ou du grade, et que son libellé est celui du grade (sans accents ni « de
  l'État ») ; puis, à chaque date où une version d'échelon du noyau commence
  dans la période du tableau, ses échelons sont alignés sur les rangs du
  noyau au décalage qui en accorde le plus (0 pour 281 dates, 1 pour 20, 2
  pour 2, 3 pour 22 : le noyau compte parfois un rang de plus en bas, ou le
  tableau omet le plus haut échelon, comme celui des ingénieurs d'études et
  de fabrications, n° 89-750, vérifié au texte). 62 tableaux s'y lient ;
  2 563 durées sont égales, 7 diffèrent, toutes là où le noyau écrit 0 : les
  médecins inspecteurs de santé publique (n° 91-1025, minimale des 1er et 2e
  échelons, 12 mois au texte), les techniciens supérieurs des études et de
  l'exploitation de l'aviation civile (n° 93-622, 10e et 5e échelons), les
  administrateurs généraux (n° 2021-1550, 5e échelon, 4 ans au texte). Les
  deux cas de l'inspection du travail (n° 2003-770) et des IEF, qui
  différaient d'abord, sont des décalages de rang du noyau, vérifiés au
  texte.
- *Ce qui n'a pu être recoupé.* Aucune grille publiée hors du LEGI et du noyau
  n'a été lue : les pages des centres de gestion (CDG 59, 69, 31, CIG petite
  couronne), de la FNCDG et d'emploi-territorial.fr, lues le 3 novembre 2026,
  ne donnent pas les durées sans aller jusqu'à leurs fiches ou PDF ; le site
  de la gendarmerie et emploi-collectivites.fr répondent 403. La territoriale,
  l'hospitalière et les militaires ne sont donc recoupés qu'aux articles lus à
  la main dans les tests, et entre eux : la catégorie B de la territoriale
  (n° 2010-329, article 24) et celle de l'hospitalière (n° 2011-661,
  article 24) écrivent, depuis le 1er septembre 2022, les mêmes durées grade
  par grade.
- *Ce que les textes ne tranchent pas, ou que la donnée ne dit pas.*
  - Le rattachement aux grilles. Un tableau nomme ses grades par leur libellé
    dans le statut, non par les clés de `grilles/<versant>/grilles.csv`, qui
    suivent les textes d'échelonnement. Le lien se fait pour l'État par le
    texte du corps (le recoupement le montre) ; pour la territoriale et
    l'hospitalière, il passe par le statut que vise chaque texte
    d'échelonnement : à écrire.
  - Le plus haut échelon d'un grade a parfois une durée écrite (« 14e et 13e
    échelons 2 ans » à La Poste) : la donnée la garde telle quelle.
  - L'avancement accéléré, les réductions et bonifications d'ancienneté sont
    écrits en phrases (dix articles des praticiens hospitaliers, des
    instituteurs de Mayotte…) : non lus. Les durées « moyenne » et « minimale »
    d'avant 2017 sont celles du texte ; laquelle s'appliquait à un agent
    dépendait de sa notation.
  - Les durées d'avant la première version consolidée d'un texte (avant 1990
    pour presque tous) ne sont qu'au JORF imprimé ; les tableaux dessinés en
    caractères et les fiches refusées, à relire.

*Pour les autres files.* Rien pour le site. Des fichiers partagés ont reçu des
lignes : `scripts/verifier_donnees.py` (une source, cinq certifications),
`tests/test_donnees.py` (les cinq séries et leur fichier),
`data/derive/certification.json` (cinq traces), `data/sources.yaml` (l'entrée
`dila_legi_durees`).

*Ce qui reste de l'action 158, étape 2.* Rattacher les tableaux de durées et
de reclassement aux grilles (le chaînage) ; relire les tableaux refusés,
fiches et tableaux dessinés en caractères d'abord ; les tableaux que l'index
aplatit ; le minimum de traitement ; les grilles et les durées d'avant 1990,
d'un poste.
