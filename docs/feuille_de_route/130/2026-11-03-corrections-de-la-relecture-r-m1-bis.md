# Les corrections de la relecture R-M1-bis : la grille des marins de 1995, bornée

**La demande.** Le 3 novembre 2026, la session d'orchestration confie à la file
M1-ter de corriger la limite de la grille des salaires forfaitaires des marins
d'avant 2008 (8cf8615, note `2026-11-03-limite-de-la-grille-des-marins.md`)
d'après la relecture R-M1-bis (aa35999, note
`2026-11-03-relecture-limite-de-la-grille-des-marins.md`) : un écart moyen, deux
faibles, deux négligeables. Aucun calcul du modèle ne change : la fiche
`marins_salaire_de_reference`, la ligne des marins de
`docs/limites/4-regimes-incomplets.md` et `tests/test_marins.py`. Le paquet
refait ne bouge pas.

## Ce qui a été relu

Dans les index de la DILA récupérés et mis à jour (JORF à l'incrément du
3 novembre 2026, 20261103-002311 ; LEGI à celui du 2 novembre, 20261102-213929 ;
aucun incrément depuis) :

| Texte | Identifiant | Ce qu'il dit, mot pour mot |
|---|---|---|
| Arrêté du 30 juin 1995, titre | JORFTEXT000000188385 | « Arrêté du 30 juin 1995 portant majoration des salaires forfaitaires servant de base au calcul des contributions des armateurs, des cotisations et des pensions des marins du commerce, de la pêche et de la plaisance » ; le texte n'a que les signatures et « BASE DE CALCUL DES CONTRIBUTIONS,COTISATIONS ET PENSIONS APPLICABLE AU 01-07-1995. » |
| Son article 1er | JORFARTI000001014013 | « Les salaires forfaitaires […] sont modifiés, pour compter du 1er juillet 1995, conformément au tableau ci-joint: » |
| Son tableau | JORFARTI000001014119 | « BASE DE CALCUL DES CONTRIBUTIONS, COTISATIONS ET PENSIONS APPLICABLE AU 1er JUILLET 1995 […] Vous pouvez consulter le tableau dans le JO no 0164 du 16/07/95 Page 10596 » |
| Son visa | JORFARTI000001977662 | « Vu l'article L. 42 du code des pensions de retraite des marins […] ; Vu les arrêtés du 29 décembre 1994 et du 31 janvier 1995 portant majoration des salaires forfaitaires […] » |
| Son article 2 | JORFARTI000001594620 | l'exécution, sans montant |
| Arrêté du 30 décembre 1995, article 1er | JORFARTI000001593286 | « sont modifiés, pour compter du 1er janvier 1996, conformément au tableau ci-joint. […] Vous pouvez consulter le tableau dans le JO no 0014 du 17/01/96 Page 801 » |
| Code des pensions de retraite des marins, L. 42 (1968-2010) | LEGIARTI000006791949 | « En cas de modification générale des salaires dépassant 5 % par rapport aux taux antérieurs, il est procédé à la révision du salaire forfaitaire. » |
| Décret n° 2001-1203 | JORFTEXT000000580421 | après les signatures et « Rectificatif au JO du 23-02-2002 page 3475 » : « En application des règlements communautaires 1103/97 du 17 Juin 1991 […], 974/98 du 3 mai 1998 […] et 2866/98 du 31 décembre 1998 concernant les taux de conversion entre l'euro et les monnaies des États membres adoptant l'euro, les références monétaires aux unités nationales qui figurent dans les textes réglementaires devront être lues à compter du 1er janvier 2002 comme des références à l'euro, en appliquant le taux de conversion de 6,55957 F pour un euro, avec arrondissement à la deuxième décimale. » |
| Décret n° 85-1148, article 3, en 1995 | LEGIARTI000006454441 (18 février au 1er novembre 1995) ; LEGIARTI000006454442 (1er novembre 1995 au 1er mars 1997) | « est fixée à 31 799 F à compter du 1er mars 1995 » ; « est fixée à 32 244 F à compter du 1er novembre 1995 » |
| Le même décret, article 7, en 1995 | LEGIARTI000006454542 (1er août 1991 au 20 février 1998) | « le traitement afférent à l'indice majoré 158 (indice brut 100) » |
| Le même article 3, le 1er décembre 1985 et le 1er janvier de 1986 à 2007 | de LEGIARTI000006454423 à LEGIARTI000006454459 | les vingt-trois valeurs de `POINT_DE_L_ARTICLE_3`, dans `tests/test_marins.py`, chacune avec sa rédaction ; en 1992, « 29 118 F à compter du 1er août 1991, puis à 29 408 F à compter du 1er novembre 1991 » ; en 1994, « 30 926 F à compter du 1er janvier 1994 », puis : « Par dérogation à l'alinéa précédent, la valeur annuelle […] est fixée, pour les agents dont l'indice majoré est inférieur ou égal à 275, à 31 018 F à compter du 1er janvier 1994. » |

La recherche `"salaires forfaitaires" marins`, publiés en 1995 et 1996, ne
donne pas d'autre arrêté que ceux du 29 décembre 1994, du 31 janvier 1995, du
30 juin 1995 et du 30 décembre 1995. Le décret n° 95-942 du 25 août 1995, qui
parle des marins « dont les cotisations sont établies par catégories de
salaires forfaitaires », n'a aucun montant de forfait.

## 1. Le second semestre 1995 (écart moyen)

**La période.** La grille du 1er janvier 1995 (arrêté du 29 décembre 1994,
corrigé le 31 janvier 1995) vaut du 1er janvier au 30 juin 1995 ; celle de
l'arrêté du 30 juin 1995, du 1er juillet au 31 décembre 1995 ; celle de
l'arrêté du 30 décembre 1995, depuis le 1er janvier 1996. Le 14,5 % de la
treizième et le 12,7 % de la vingtième ainsi estimée ne valent donc que pour
une pension qui prend effet, et pour des cotisations dues, du 1er janvier au
30 juin 1995. La fiche, la ligne des limites et le premier test le disent.

**Ce que l'arrêté donne : rien qui permette de refaire l'écart.** Son titre
dit une « majoration » ; aucun de ses articles, ni son texte, n'écrit un
montant ou un taux : le tableau est au Journal officiel imprimé, n° 164 du
16 juillet 1995, page 10596, que l'index ne porte pas. L'article L. 42 qu'il
vise n'en dit pas davantage : il commande une révision quand les salaires
montent de plus de 5 %, sans en fixer le montant ni interdire une révision plus
petite. L'écart du second semestre 1995 est donc plus grand qu'au premier,
d'un montant inconnu. Le modèle n'a qu'une grille pour 1995.

**Ce qu'on peut borner.** Ce que la majoration devrait atteindre pour que la
vingtième réelle, si elle suit l'écart de la treizième et la structure de 2008,
passe le plafond du droit du second semestre :

- la vingtième du 1er janvier 1995 ainsi estimée : 176 796,36 / 6,55957 =
  26 952,431 € ; × (59 899,76 / 33 126,69 = 1,8082024) = 48 735,45 € ;
- le plafond du droit de juillet à octobre 1995 : 8 × 158 × 317,99 F =
  401 939,36 F ; / 6,55957 = 61 275,26 € ; puis, au 1er novembre, 8 × 158 ×
  322,44 F = 407 564,16 F, 62 132,76 € ;
- 61 275,26 / 48 735,45 = 1,25730 : il faudrait une majoration de plus de
  25,7 % pour que la vingtième passe le plafond de juillet à octobre ;
  62 132,76 / 48 735,45 = 1,27490, plus de 27,49 % en novembre et décembre.

Ce n'est qu'une borne, sous l'hypothèse de la fiche. La conclusion sur le
plafond reste ce que la fiche en dit : très probable, non prouvée. « La grille
relevée de l'écart de 1995, le plus grand des deux » se lit désormais « de
l'écart du 1er janvier 1995, le plus grand des deux mesurés, et non le plus
grand possible ».

## 2. La ligne des limites (faible)

La ligne des marins dit maintenant que le forfait des plus hautes catégories
« paraît en être sous-estimé, si la vingtième catégorie suit l'écart de la
treizième et la structure de la grille de 2008, aucune vingtième d'avant 2008
n'étant lue », et que la treizième réelle est celle de la grille « du
1er janvier au 30 juin 1995 », l'écart du second semestre restant inconnu.
Aucune autre ligne du fichier n'a changé. Elle ne porte aucun chiffre nu.

## 3. Le deuxième test pose le plafond depuis le texte (faible)

`test_de_1985_a_2007_la_vingtieme_estimee_reste_sous_le_plafond_meme_relevee`
ne demande plus le plafond au code (`liquider.plafond_du_salaire_de_reference`).
Il le pose : huit fois (R. 11, 3°) le traitement de l'indice majoré que
l'article 7 fait correspondre à l'indice 100 ce jour-là (`INDICE_100`, que
d'autres tests relisent rédaction par rédaction), au point de cent indices de
l'article 3 (`POINT_DE_L_ARTICLE_3`, nouveau), au 1er janvier de chaque année et
au 1er décembre en 1985. Un test nouveau,
`test_chaque_point_se_relit_dans_sa_redaction_de_l_article_3`, relit chacun des
vingt-trois points dans l'index LEGI, quand il est là : la rédaction est celle
de l'article 3 du décret n° 85-1148, en vigueur ce jour-là, et écrit le montant
que le test prend.

Calcul posé de l'année qui culmine, 2005 : 8 × 174 × 5 275,58 / 100 =
73 436,07 € ; la vingtième estimée, 55 160,27 € ; 55 160,27 / 73 436,07 =
75,11 %, « au plus 75,1 % » ; × 1,145442 = 86,04 %, « sous 86,1 % ». En 1985,
le point du droit au 1er décembre, 26 428 F, donne 8 × 150 × 264,28 / 6,55957 =
48 347,07 € et un rapport de 62,8 % (le modèle, au point du 1er janvier 1985,
65,6 %) : 2005 reste le plus haut. En 1994, le texte ne dit pas si le
traitement de l'indice 100 suit l'alinéa général (30 926 F) ou la dérogation
des agents d'indice majoré inférieur ou égal à 275 (31 018 F) : le test prend
le plus bas, qui ne peut que relever le rapport, et 2005 reste le plus haut.

**Vu mordre.** Le point de 2005 faussé à « 5 175,58 Euros » : la relecture LEGI
échoue (« est fixée à 5 175,58 Euros à compter du 1er janvier 2004 » absent de
LEGIARTI000006454455), et le deuxième test aussi (« au plus 76,6 % du plafond
(2005) » absent de la fiche). Remis à 5 275,58, les deux passent. Le premier
test, lui, a été vu échouer sur la fiche d'avant (« paragraphe d'explication »
absent), puis passer avec elle.

## 4. Les centimes et le décret n° 2001-1203 (négligeables)

**Les centimes.** Les montants de la fiche se calculent sans arrondi en
chemin, sur les salaires moyens du modèle non arrondis (1980 : 9 466,624117 € ;
1995 : 20 944,647182 € ; 2006 : 28 043,444387 € ; 2008 : 29 486,715746 €). Le
dernier centime bouge quand on arrondit en chemin :

- 25 980,90 × 28 043,444387 / 29 486,715746 = 24 709,226, soit 24 709,23 € ;
  aux salaires moyens arrondis au centime, 25 980,90 × 28 043,44 / 29 486,72 =
  24 709,219, soit 24 709,22 € ; au facteur arrondi à six décimales,
  25 980,90 × 0,951054 = 24 709,239, soit 24 709,24 € ;
- 26 952,431 × 1,8082024 = 48 735,451, soit 48 735,45 € ; aux deux facteurs
  arrondis, 26 952,43 × 1,808202 = 48 735,438, soit 48 735,44 € ;
- la vingtième de 1980 : 59 899,76 × 9 466,624117 / 29 486,715746 =
  19 230,643, soit 19 230,64 € ; aux salaires moyens arrondis au centime,
  59 899,76 × 9 466,62 / 29 486,72 = 19 230,632, soit 19 230,63 €.

La fiche le dit en une phrase, à la fin de l'effet de l'approximation des
arrêtés annuels.

**Le décret n° 2001-1203.** La phrase du taux du franc n'est pas un article : c'est
un paragraphe d'explication, que l'index JORF donne à la suite des signatures
du décret et de la mention de son rectificatif, et qui rattache la conversion
aux règlements communautaires, dont le n° 2866/98 « concernant les taux de
conversion ». La fiche et le commentaire du test le désignent ainsi ; le
règlement lui-même n'a pas été ouvert, et rien n'en est cité. La conversion
n'en change pas.

## Hors de la tâche, relevé en chemin

La série `legislation/point_indice_fonction_publique.csv` porte 47,2165 € en
1994. Ce n'est ni le point de l'alinéa général de l'article 3 au 1er janvier
1994, 30 926 F (47,1464 €), ni celui de la dérogation, 31 018 F (47,2866 €),
mais leur moyenne (47,21651), arrondie au dix-millième. Son en-tête dit aussi que la base
LEGI ne garde pas les relèvements du 1er novembre 1991 et du 1er janvier 1994 :
l'index les porte, l'un dans LEGIARTI000006454434 (« puis à 29 408 F à compter
du 1er novembre 1991 »), l'autre dans LEGIARTI000006454438. La série n'est pas
dans la zone de cette tâche : rien n'y est changé, et c'est signalé à
l'orchestration. Les points du 1er janvier de 1986 à 1993 et de 1995 à 2007
sont, eux, ceux de l'article 3, à l'arrondi de la série près.

## Ce qui attend

La question au propriétaire demeure : les tableaux des arrêtés de 1985 à 2007,
au Journal officiel imprimé ; celui du 30 juin 1995 dirait de combien le second
semestre 1995 s'écarte. Une relecture indépendante de ces corrections suit.
