# Étape des militaires : leurs indices de solde, lus au LEGI, certifiés et recoupés au Noyau RH

**Le 3 novembre 2026 : les grilles des militaires sont entrées dans le dépôt,
tirées des textes de leurs indices de solde que l'index LEGI garde, et
certifiées : 18 textes, 192 grilles, 2 959 périodes d'échelons, chacune avec
l'article qui la fixe, depuis 1993 pour le contrôle général des armées, 2000
pour les officiers, 2009 pour tous. Elles redonnent, indice pour indice, les
grilles militaires que le Noyau RH de l'État publie de 2009 à 2026. Les
échelons des sous-officiers et des militaires du rang d'avant 2009, comptés en
années de services, ne se lisent pas dans le texte aplati ; les durées
d'échelon ne sont pas dans ces textes.**

Demande : la session d'orchestration du 3 novembre 2026, file B, pour
l'étape des militaires de l'action 158, décidée par le propriétaire le
2 novembre 2026 : « les grilles des militaires, qui ont leur propre barème (les
indices de solde), entrent au périmètre ». Pas de site.

- *Le récupérateur* (`scripts/fetch/dila_legi_grilles.py`, test
  `tests/test_grilles_militaires.py`). Un troisième versant, `militaires`, lu
  au titre : les indices de solde, l'échelonnement indiciaire applicable aux
  militaires, un corps militaire, les praticiens des armées ; non les textes des
  « personnels civils et militaires de l'État » ensemble, ni les corps civils
  dont le nom dit officier (contrôleurs de la circulation aérienne, officiers de
  port, de protection des réfugiés). Leurs tableaux écrivent ce que la
  territoriale n'écrit pas, et l'analyseur l'apprend pour eux seuls
  (`lire_tableau(..., militaire=True)`) : l'échelle de solde sous son grade
  (« Adjudant Echelle de solde n° 4 », puis « Echelle de solde n° 3 », encore
  celle de l'adjudant) ; les en-têtes « GRADE ÉCHELLE DE SOLDE ÉCHELON »,
  « CORPS GRADE ET CLASSE », « Désignation des échelons » ; l'échelon unique,
  particulier (l'élève gendarme) ou provisoire (sous le premier, au rang zéro) ;
  « 2e échelon exceptionnel » et « 1er échelon spécial », au-dessus du plus haut ;
  « Exceptionnel » seul ; la case vide que suit son renvoi (« -(2) ») ; le
  groupe « afférent » que la phrase nomme (la classe fonctionnelle du grade de
  major) ; « 1 re classe » pour « 1re classe ».
- *Pourquoi pour eux seuls.* Les mêmes règles, appliquées à tous, ouvraient six
  versions d'articles de la territoriale (conservateurs du patrimoine et des
  bibliothèques, décrets n° 91-840 et 91-842, « Echelon unique » de stage) et
  une de l'hospitalière (l'échelon provisoire des directeurs d'école de
  sages-femmes), avec des groupes douteux, que leur certification n'a pas vus.
  Réservées aux militaires, elles laissent les fichiers de la territoriale et de
  l'hospitalière identiques à l'octet (vérifié par la session).
- *Ce qu'il refuse* (`militaires/non_lus.csv`, 10 versions) : les échelons
  comptés en années de services (« Après 21 ans »), seule forme des sous-officiers
  et des militaires du rang avant 2009, dont l'aplatissement entrelace les
  colonnes de grades — arrêtés du 30 décembre 1975, du 3 août 1992 (sapeurs-pompiers
  de Paris), du 26 décembre 2007 (majors), articles 1er à 4 du décret
  n° 2008-532 ; le tableau de l'arrêté du 20 décembre 2002 des militaires
  infirmiers, qui mêle durées et indices ; les indices majorés du décret
  n° 2017-491. Sans ce refus, l'arrêté de 2007 donnait aux majors un seul
  échelon, sous un libellé fait de l'en-tête.
- *Une date rendue au texte* (`DATES_CORRIGEES`). Le décret n° 2014-1257 entre
  en vigueur le premier jour du mois qui suit sa publication, le 1er novembre
  2014 (article 3) ; le n° 2015-1041 le portait au 1er janvier 2014, mais le
  n° 2015-1304 l'a retiré. Le LEGI a gardé la date retirée à la seule version de
  l'article 2 du décret n° 2009-21 qu'il écrit, et clos avant son début celle du
  décret n° 2014-988, en vigueur au 1er septembre 2014 ; ses articles 3, et 1er
  du n° 2009-23, disent bien le 1er novembre. Les deux versions reprennent ces
  dates : les sergents à l'échelle n° 2 changent avec les soldats, le
  1er novembre 2014.
- *Les chiffres.* 18 textes, dont 13 avec une grille lue : les décrets
  n° 2009-17 (contrôle général des armées), 2009-18 (armement, jusqu'en 2011),
  2009-19 (praticiens), 2009-20 (officiers), 2009-21 (aspirants, sous-officiers,
  militaires du rang), 2009-22 puis 2011-388 (gendarmerie), 2009-23
  (sapeurs-pompiers de Paris), 2011-1235 (armement et infrastructure), le
  n° 2008-532 pour les seuls gendarmes de 2008 ; les arrêtés de 1994, 2000 et
  2004. 192 grilles, 2 959 périodes, dont 84 en lettre de hors-échelle ;
  114 versions d'articles lues, 10 non lues ; 86 grilles en vigueur au
  3 novembre 2026. La première période date du 1er octobre 1993.
- *La certification.* `scripts/verifier_donnees.py` certifie le rang (2 959) et
  l'indice (2 875) de chaque période, toutes identiques ; aucun tableau des
  militaires ne laisse de colonne présumée, et leurs deux séries d'appoint
  restent vides. Le journal (`data/derive/certification.json`) ne reçoit que
  ces deux traces.
- *Le recoupement au Noyau RH* (`tests/test_grilles_militaires.py`). Le noyau du
  CISIRH (juillet 2026, `grilles/etat/`) porte ses propres grilles militaires
  depuis 2009 ; onze d'entre elles, à deux ou trois dates de 2009 à 2026,
  redonnent celles du LEGI indice pour indice : aspirants, sergents,
  sergents-chefs, adjudants-chefs, caporaux-chefs, gendarmes et
  adjudants-chefs de gendarmerie, capitaines des armées et de la gendarmerie,
  médecins. Mesure de la session, mois par mois de janvier 2009 à octobre 2026,
  par des scripts qu'elle n'a pas versés : les aspirants et les sergents-chefs à
  l'échelle n° 4 concordent les 214 mois, les sergents 213. Trois écarts, que le
  test et cette note disent :
  - la structure : le noyau découpe colonels, lieutenants-colonels, contrôleurs,
    ingénieurs et médecins en chef en « échelles », et met à part les échelons
    fonctionnels hors échelle ; il numérote autrement les échelons
    exceptionnels (deux rangs 7 chez les caporaux-chefs). La comparaison se fait
    donc sur les indices, du plus bas au plus haut ;
  - les dates : le noyau date du 1er janvier 2010 le décret n° 2009-1111, qui
    « prend effet au 1er janvier 2009 » ; du 1er janvier 2014 le décret
    n° 2014-1257 pour les militaires du rang et les sergents à l'échelle n° 2,
    la date retirée — il paie alors l'indice majoré 313 (indices bruts 307 et
    308) où le texte en vigueur donne 288 et 289, payés au minimum, 309 ; du
    1er juillet 2013 ce que le LEGI date du 13 juillet ;
  - le retard : le noyau de juillet 2026 n'a ni le décret n° 2024-1121, qui
    relève au 15 décembre 2024 les majors, adjudants-chefs et adjudants, ni le
    n° 2025-1000, qui refait au 15 décembre 2025 les grilles des officiers ; ses
    grilles restent à leurs valeurs de 2020. Le LEGI est plus à jour.
- *Ce qui n'a pas pu se lire.* Aucune grille de solde publiée en euros n'a
  répondu à la session : les sites du ministère des armées
  (bo.sga.defense.gouv.fr, archives.defense.gouv.fr) refusent son mandataire
  (502), emploi-collectivites.fr répond 403. Le recoupement au traitement
  mensuel d'une grille publiée reste à faire d'un poste qui y accède.
- *Ce que la donnée ne dit pas.*
  - Avant 2009, les sous-officiers et les militaires du rang : refusés (plus
    haut). Le dump XML de la DILA garde les tableaux ; l'index les aplatit.
  - Les arrêtés de 1994, 2000 et 2004 restent au LEGI jusqu'au 22 juin 2020
    (abrogés par l'arrêté du 18 juin 2020), quand les décrets du 7 janvier 2009
    les ont remplacés : de 2009 à 2020, deux grilles disent les mêmes grades,
    et la carrière (étape 3) prendra celle du décret.
  - Les durées d'échelon : ni ces textes ni le noyau, dont les durées des
    grilles militaires valent zéro ; les statuts particuliers des décrets du
    12 septembre 2008 (n° 2008-930 à 2008-961) les fixent.
  - Le chaînage et les reclassements, comme aux autres versants ; une grille
    est celle d'un groupe d'un texte, et la même renommée (« Major – Echelle de
    solde des majors » en 2009, « Major – Echelle de solde n° 4 » fin 2012) en
    fait deux.

*Pour les autres files.* Rien pour le site. Des fichiers partagés ont reçu des
lignes : `scripts/verifier_donnees.py` (quatre certifications),
`tests/test_donnees.py` (les quatre séries, dont deux d'appoint),
`data/derive/certification.json` (deux traces), `data/sources.yaml` (l'entrée
`dila_legi_grilles`). Les deux tests de `test_donnees.py` qui échouaient déjà
sur `main` (l'inventaire des régimes, que GitHub refait) échouent toujours, sans
lien avec cette étape.

*Ce qui reste de l'action 158, étape 2.* Les durées d'échelon, dans les statuts
des trois versants et des militaires ; les tableaux que l'index aplatit — en
caractères avant 1995, en années de services chez les militaires avant 2009 ;
le chaînage et les reclassements ; le barème avant 2006, au décret n° 82-1105 ;
les grilles de l'État d'avant le noyau ; le traitement mensuel d'une grille
militaire publiée.
