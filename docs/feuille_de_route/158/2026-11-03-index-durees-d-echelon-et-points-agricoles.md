# L'index élargi aux durées d'échelon et à D. 732-76 et D. 732-77, puis reconstruit

**Le 3 novembre 2026 : le filtre de l'index de la DILA garde désormais, sur
leur seul texte, les articles qui fixent la durée des échelons, et les deux
articles du code rural qui majorent les points de chef de 1952 à 1972. Les
deux besoins viennent des décisions du propriétaire du 3 novembre 2026. Le tri
d'avant ne gardait pas tous les textes des durées : il les prenait à leur titre,
et 864 des 1 115 tableaux de durées de l'index n'y entraient que par lui.
L'index est reconstruit :
327 817 documents au LEGI au lieu de 325 879, 518 291 au JORF au lieu de
516 798, aucun sorti. D. 732-76 et D. 732-77 y sont dans leur seule rédaction de
2005 à 2025, et l'index LEGI compte 1 633 textes de durées d'échelon au lieu de
1 280, 7 880 versions d'articles au lieu de 5 944.**

Demande : la session d'orchestration du 3 novembre 2026, file B, quatrième
vague, rapportant deux décisions du propriétaire du même jour. Élargir le tri
`THEMATIQUE` de `scripts/fetch/dila_index.py`, au plus juste, à D. 732-76 et
D. 732-77 du code rural dans toutes leurs versions de 2005 à 2025 (action 131,
note `131/2026-11-03-d-732-76-et-d-732-77-hors-de-l-index.md`), et aux textes
qui fixent la durée de chaque échelon des grilles des trois versants et des
militaires (la durée des échelons d'abord) ; le faire reconstruire par
`index-dila.yml`, lancé sans être modifié ; vérifier D. 732-76 et D. 732-77
dans l'index publié, et compter les textes de durées d'échelon, sans lire
encore ces durées. Exigence du propriétaire, le même jour : tout texte dit
retenu ou écarté se vérifie dans l'index par son identifiant, et ce qui n'a pas
pu l'être se dit.

- *D. 732-76 et D. 732-77, lus à la source.* Légifrance oppose un défi de
  Cloudflare (note de l'action 131) et le dump ne se retélécharge pas
  (`docs/veille_droit.md`) ; les incréments LEGI de la DILA se lisent
  (`echanges.dila.gouv.fr/OPENDATA/LEGI/`, de quelques centaines de Ko à
  trente Mo chacun). Celui du 31 décembre 2025 (`LEGI_20251231-230401`)
  republie D. 732-77 en vigueur ; ceux du 9, du 14 et du 15 janvier 2026 (`LEGI_20260109-215114`,
  `LEGI_20260114-215319`, `LEGI_20260115-213622`), qui consolident le décret
  n° 2025-1409 du 30 décembre 2025 (JORFTEXT000053227462), republient les deux
  articles clos au 1er janvier 2026, état « MODIFIE ». Chacun n'a eu qu'une
  rédaction de 2005 à 2025, du 22 avril 2005 au 1er janvier 2026 : la liste
  des versions que porte leur XML n'en a pas d'autre avant celles de 2026.
  - D. 732-76, LEGIARTI000006597490 : « Le nombre de points acquis par les
    chefs d'exploitations ou d'entreprises agricoles au titre de la période
    comprise entre le 1er juillet 1952 et le 31 décembre 1972 est majoré de
    17 % lorsque le nombre annuel moyen de points acquis par les intéressés au
    cours de ladite période est au moins égal à seize. » Source de
    codification : l'article 2 du décret n° 81-790 du 18 août 1981
    (JORFTEXT000000335107).
  - D. 732-77, LEGIARTI000006597491 : la majoration de 5 % entre 15 et 19,51
    points annuels moyens, « T % = 3,19 x P - 57,23 », puis de 5 à 30 % et de
    30 à 45 % entre 19,51 et 27,34 et au-delà, « T % = 1,93 x P - 22,74 », P
    étant « le nombre annuel moyen de points acquis par l'assuré » ; source :
    l'article 2 du décret n° 86-1084 du 7 octobre 1986 (LEGIARTI000006769405).
  - Sous les mêmes numéros, les rédactions de 2026 (LEGIARTI000053365504 et
    LEGIARTI000054059256 pour D. 732-76, LEGIARTI000053365517 pour D. 732-77)
    disent autre chose, le versement pour la retraite de l'article L. 351-14-1
    du code de la sécurité sociale : le décret n° 2025-1409 a réemployé les
    numéros, et R. 732-67 (LEGIARTI000053328816) renvoie aux majorations « dans
    leurs rédactions antérieures ». Deux versions parues le 9 janvier,
    LEGIARTI000053336588 et LEGIARTI000053336581, closes le 14 au jour même de
    leur début, le 1er janvier 2026, ne sont plus dans la liste du 15 janvier.
  - Pourquoi le tri les écartait : leur titre est celui du code, « Code rural
    (nouveau) », et leur texte n'a aucun des mots du tri. Ils ont en commun
    « nombre annuel moyen de points », que le tri retient désormais.
  - Les identifiants manquants de la note de l'action 131 : LEGIARTI000006597490
    et 491 sont ces deux articles ; 487 est R. 732-84 (le conjoint collaborateur
    à titre secondaire, transféré le 1er janvier 2026 en D. 732-84,
    LEGIARTI000053365550), hors de l'index et de cette décision ; 488 n'est dans
    aucun des seize incréments lus.
- *Les durées d'échelon : le tri d'avant ne les gardait pas toutes.* Il
  prenait un statut à son titre (« statut particulier », « dispositions
  statutaires communes », « organisation des carrières »), et l'article à ses
  mots (« avancement d'échelon »). Un titre au pluriel (« portant statuts
  particuliers », décrets n° 2008-930 et 2008-931 des militaires), « fixant les
  dispositions statutaires applicables », « portant statut des », « relatif aux
  emplois supérieurs », ou celui d'un code (le code de la recherche) laissait
  dehors l'article qui fixe les durées. Constaté sur pièces :
  - dans seize incréments LEGI, du 30 décembre 2025 au 16 janvier 2026, le tri
    d'avant écartait l'article 34 du décret n° 95-370 (LEGIARTI000034773651 et
    cinq autres versions : « La durée du temps passé dans chacun des échelons du
    corps des ingénieurs d'études »), les articles 27 et 28 du décret
    n° 2020-959 des emplois supérieurs de l'hospitalière (LEGIARTI000042199625,
    LEGIARTI000042199627), l'article 13 du décret n° 99-1073 des emplois de
    l'École nationale de la magistrature (LEGIARTI000006513139), l'article 10-7
    du décret n° 65-383 (LEGIARTI000034743786), ceux des décrets n° 2015-633 et
    2017-217 ;
  - dans onze incréments JORF, du 1er au 20 janvier 2026, ceux des décrets
    n° 2019-1594 (emplois de direction de l'État, JORFARTI000039727814),
    2016-1413, 2007-119, 2014-501, 2007-315, et l'article R. 423-51 du code de la
    recherche, au décret n° 2023-1321 (JORFARTI000048711012) ;
  - dans l'index du 2 novembre, des 1 115 articles qui portent un tableau de
    durées (au moins deux « Ne échelon … N ans ou mois », sans mot de
    reclassement), 251 passaient le tri sur leur seul texte : 864 n'y étaient
    que par le titre de leur texte ;
  - des 476 statuts que les corps de l'État du Noyau RH citent comme texte
    d'origine, 191 ont un titre que le tri ne retient pas ; des 161 numérotés
    parmi eux, 26 n'avaient aucun article dans l'index (n° 2006-1777,
    2008-115, 2010-1152, 2011-2009, 2016-983 des militaires du rang…, une
    circulaire, n° 2007-01, comprise), dont 10 aucun document.
- *Le tri élargi* (commit 0a64139). `DUREES_D_ECHELON`, huit alternatives,
  chacune bornée à « échelon » (et `\b`, qui laisse « échelonnement ») : le
  temps passé ou à passer dans, aux ou à tel échelon, de services effectifs ou
  « normalement » ; la durée passée dans ; la durée de l'échelon, d'échelon,
  dans l'échelon, de chaque échelon, des échelons, moyenne et minimale dans
  chaque échelon ; l'ancienneté ou la durée exigée, requise, « donnant accès »
  ou « à accomplir » pour l'échelon ; l'ancienneté moyenne, minimale ou
  maximale ; « du 1er au 2e échelon : 2 ans » ; l'en-tête « échelons durée » ;
  le tableau qui donne deux durées par échelon. `THEMATIQUE` les reprend, avec
  « nombre annuel moyen de points ».
  - Le rappel : les 1 115 tableaux de durées de l'index passent tous sur leur
    seul texte. Chaque alternative en prend au moins un qu'aucune autre ne prend
    (52, 1, 1, 4, 2, 1, 6, 2) ; « temps d'échelon », qui n'en prenait aucun, n'a
    pas été gardée.
  - La précision, sur les mêmes incréments. LEGI : 48 991 documents, 18 541
    gardés par le tri d'avant, 18 573 par le nouveau ; 32 entrent — des durées
    d'échelon, deux règles de carrière (l'article 22-1 du décret n° 89-406,
    l'article 9 du décret n° 91-56), D. 732-76 et D. 732-77 — et aucun ne sort.
    JORF : 46 134 documents, 8 750 puis 8 838 ; 88 entrent, des durées
    d'échelon d'emplois fonctionnels et de statuts et des tableaux de
    reclassement (« ancienneté conservée dans la limite de la durée de
    l'échelon »), aucune nomination, aucun concours ; aucun ne sort.
  - Le coût : le tri prend 19 % de temps de plus sur l'échantillon LEGI (56,4
    puis 67,2 secondes), 18 % sur l'échantillon JORF (26,9 puis 31,8).
- *Le test* (`tests/test_dila_index.py`), sur des textes réels : D. 732-76 et
  D. 732-77 sous le titre du code ; dix-sept articles de durées, de 1964 à
  2025, des trois versants et des militaires (gendarmerie, marine, chefs de
  musique), sur leur seul texte ; cinq articles où « points » ou « échelon » ont
  un autre sens, qui restent dehors (le permis à points, un concours, l'échelon
  du bassin, les échelons de qualité de crédit, l'échelon de poids du
  courrier). Vu rouge (dix-neuf échecs), puis vert ; `pytest -m rapide` (4 172
  réussis), la garde des présomptions (3 983), et les fichiers de tests qui
  chargent ces scripts ou lisent les grilles et les reclassements (340).
- *La reconstruction.* `index-dila.yml`, entrée `reconstruire`, lancé sans
  modification le 3 novembre 2026 à 10 h 15 UTC sur 0a64139 (run
  41617807038). Le LEGI, reconstruit en 1 h 13, est publié à 11 h 29 UTC :
  327 817 documents au lieu de 325 879, à jour au même incrément (2 novembre,
  21 h 39) ; 1 938 entrent — 1 936 par les durées, 2 par les points, de 627 textes — et aucun ne
  sort ni ne change. Le JORF, publié à 11 h 57 UTC : 518 291 documents au lieu
  de 516 798 ; 1 493 entrent, dont 45 de l'incrément du 3 novembre à 0 h 23,
  que le tri d'avant gardait aussi, et 1 448 par l'élargissement (1 446 par les
  durées, 2 par les points, de 647 textes) ; aucun ne sort ni ne change. Le run
  est vert de bout en bout.
- *Vérifié dans l'index reconstruit.*
  - D. 732-76, LEGIARTI000006597490, et D. 732-77, LEGIARTI000006597491, du
    22 avril 2005 au 1er janvier 2026 : texte et dates identiques, au caractère
    près, au XML de l'incrément du 15 janvier 2026. Avec leurs rédactions de
    2026, la suite des versions de chacun est sans trou depuis le 22 avril
    2005. Au JORF, le décret n° 2005-368 les publie le 22 avril 2005
    (JORFARTI000001910389 et JORFARTI000002065029), d'un texte identique à celui
    du LEGI. « Nombre annuel moyen de points » n'a fait entrer qu'eux : les 36
    autres documents LEGI et les 18 du JORF qui le disent y étaient déjà (au
    LEGI, les décrets n° 73-937, 86-1084, 94-714, 97-163, 2002-297 et 2002-298,
    l'article D. 643-6 du code de la sécurité sociale, D. 732-111 à D. 732-146
    du code rural ; au JORF, de plus, les décrets n° 2003-1376 et 2004-461).
  - Les textes de durées d'échelon. Mesure de la session, par un script qu'elle
    n'a pas versé : un article en est s'il répond à `DUREES_D_ECHELON` ou porte
    un tableau de durées (au moins deux « Ne échelon … N ans ou mois », sans
    « ancienneté acquise », « ancienneté conservée », « sans ancienneté »,
    « situation ancienne ou nouvelle » ni « reclass ») ; un texte est un titre ;
    son versant, celui de `versant()` (`dila_legi_grilles.py`), les statuts
    militaires reconnus en plus à leur titre. Au LEGI : 1 633 textes au lieu de
    1 280, 7 880 versions d'articles au lieu de 5 944 ; l'État 1 252 (945), la
    territoriale 193 (171), l'hospitalière 149 (129), les militaires 38 (34), un
    texte de plusieurs versants. 353 textes sont nouveaux (307, 22, 20 et 4),
    273 gagnent des articles, aucun n'en perd. Au JORF : 1 682 textes au lieu
    de 1 360, 4 676 articles au lieu de 3 274 ; l'État 1 267 (993), la
    territoriale 216 (202), l'hospitalière 160 (134), les militaires 38 (30) ;
    322 nouveaux, aucun perdu ; l'incrément du 3 novembre n'en apporte aucun.
  - Entrés, entre autres : les statuts particuliers des aides-soignants
    (n° 89-241), des sous-officiers de gendarmerie (n° 75-1214), des officiers
    greffiers (n° 2008-930), les militaires engagés (n° 2008-961), les emplois
    de direction des collectivités territoriales (n° 87-1101, de 52 à 111
    versions d'articles, dont 68 de durées), le décret n° 95-370 (de 68 à 97,
    dont 44 de durées). Les 30 articles de code entrés sont du code de
    justice administrative (7), des juridictions financières (11), de la
    recherche (6), des communes (3), de la défense (1) et du code rural (2) ;
    s'y ajoutent l'article 19 de la loi n° 72-662 (statut général des
    militaires) et l'article 2 de l'ordonnance n° 58-1270 (statut de la
    magistrature). Un tirage au hasard de douze entrées ne montre que des
    durées d'échelon.
  - Les 26 statuts de l'État sans article : un seul, le n° 2008-115, en a
    désormais un, de durées ; dans les incréments, les n° 2008-960 et 2008-1483
    n'ont aucun article de durées ; les 22 autres ne se vérifient pas sans le
    dump.
- *Ce qui n'est pas vérifié.* Le rappel ne se mesure que sur ce que l'index
  gardait déjà et sur seize incréments : un article de durée rédigé autrement,
  sous un titre que le tri ne retient pas, peut manquer encore ; le dump, qui
  fait foi, ne se lit pas depuis la session. Les durées d'avant la première
  version consolidée d'un texte restent au seul JORF, et l'index JORF n'a aucun
  texte de durées dont le premier article date d'avant 1990. Les tableaux qui
  comptent les échelons en années de services, sans phrase de durée (des
  militaires surtout), n'ont pas été mesurés à part.

*Pour l'action 131* (son bloc « Reprise » n'est pas récrit ici). D. 732-76 et
D. 732-77 sont dans les deux index, dans leur seule rédaction de 2005 à 2025 :
LEGIARTI000006597490 et LEGIARTI000006597491 au LEGI, JORFARTI000001910389 et
JORFARTI000002065029 au JORF. Ce qui arrêtait la note du 3 novembre de l'action 131 est levé : une
session de l'action les lit par `dila_cherche.py legi --texte
LEGIARTI000006597490`. Restent hors de l'index : R. 732-84 de 2005 à 2025
(LEGIARTI000006597487), et l'article 2 du décret n° 81-790, source de
D. 732-76, dont le JORF n'a que la notice (JORFTEXT000000335107).

*Pour les autres files.* Rien pour le site. Aucun fichier partagé touché. Dans
les incréments, le même mécanisme laisse dehors l'arrêté du 13 novembre 1963
« relatif au régime d'allocation viagère des gérants de débits de tabac »
(article 14, LEGIARTI000006787879 et 880), qui leur ouvre un compte de « points
tabac » : ni l'une ni l'autre décision ne le vise.

*Ce qui reste de l'action 158, étape 2.* Lire les durées d'échelon dans les
textes que l'index garde désormais : la session suivante de la file B. Puis le
chaînage, les tableaux que l'index aplatit, le minimum de traitement.
