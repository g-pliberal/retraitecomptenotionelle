# Relecture des corrections de R-M1-bis (file M1-ter)

File R-M1-ter, le 3 novembre 2026. Il s'agit d'une relecture indépendante du commit
a66e323 (session M1-ter, note `2026-11-03-corrections-de-la-relecture-r-m1-bis.md`).
Ce commit corrige la limite de la grille des salaires forfaitaires des marins
d'avant 2008, après la relecture R-M1-bis. Chaque texte a été rouvert ici, sans
rien reprendre de la session ni de mémoire. Les index de la DILA ont été récupérés
puis mis à jour : JORF à l'incrément du 3 novembre 2026 (20261103-002311), LEGI à
celui du 2 novembre (20261102-213929), aucun incrément depuis. Rien n'a été
modifié : ni règle, ni donnée, ni test, ni fiche.

**Verdict.** Le travail est **conforme** sur l'essentiel :

- chaque citation, mot pour mot ;
- les vingt-trois points de l'article 3, chacun dans la rédaction en vigueur ce
  jour-là ;
- la borne de 25,7 % et le plafond de 61 275,26 €, refaits à la main au centime ;
- les tests, verts, y compris sous `PRESOMPTIONS_DECALEES=1`, et ils mordent ;
- les cinq écarts de R-M1-bis, tous corrigés.

**Écarts relevés.** Aucun grave, aucun moyen. Trois faibles et deux négligeables :

- **Faible** (point 6). La note dit que la recherche des arrêtés de 1995 et 1996
  ne donne « pas d'autre arrêté » que les quatre qu'elle nomme. Elle en donne un
  cinquième : l'arrêté du 2 août 1995 portant classement des officiers
  (JORFTEXT000000554960). Il ne porte aucun montant ; la conclusion tient, mais la
  phrase est inexacte.
- **Faible** (point 5). Ce que le texte ne tranche pas en 1994 est déclaré dans le
  test et la note, non dans la fiche. Or le plafond que le modèle prend en 1994
  (59 681,66 €) n'est écrit par aucun des deux alinéas. Il s'en écarte de 88,65 €
  au plus.
- **Faible** (point 4). Les vingt-trois relectures dans LEGI ne tournent pas sur
  GitHub, car `tests.yml` ne récupère pas l'index. Le test le dit (« quand il est
  là »). Mais un point faussé avec sa rédaction passe le deuxième test, seul juge
  sans l'index.
- **Négligeable** (point 3). « Plus de 27,49 % » en novembre et décembre 1995 :
  le seuil exact est de 27,4899 %. La formule tient sous la forme « plus de 27,48 % ».
  Ce chiffre n'est que dans la note.
- **Négligeable** (point 4). Le premier test vérifie que la borne « du 1er janvier
  au 30 juin 1995 » est écrite quelque part, non qu'elle suit chaque chiffre.

## 1. Les citations, mot pour mot

Chaque texte a été lu dans l'index, à sa version en vigueur à la date qui compte :

| Texte | Identifiant ouvert | Constat |
|---|---|---|
| Arrêté du 30 juin 1995 : titre et texte | JORFTEXT000000188385 | conforme : le titre « portant majoration des salaires forfaitaires […] » ; le texte n'a que les signatures et « BASE DE CALCUL DES CONTRIBUTIONS,COTISATIONS ET PENSIONS APPLICABLE AU 01-07-1995. » |
| Son article 1er | JORFARTI000001014013 | conforme : « sont modifiés, pour compter du 1er juillet 1995, conformément au tableau ci-joint: » |
| Son tableau | JORFARTI000001014119 | conforme : « Vous pouvez consulter le tableau dans le JO no 0164 du 16/07/95 Page 10596 » ; aucun montant |
| Son visa | JORFARTI000001977662 | conforme : il vise L. 42 et « les arrêtés du 29 décembre 1994 et du 31 janvier 1995 portant majoration des salaires forfaitaires » ; l'ellipse de la note couvre le visa du décret n° 52-540 |
| Son article 2 | JORFARTI000001594620 | conforme : l'exécution, sans montant |
| Arrêté du 30 décembre 1995, article 1er | JORFARTI000001593286 | conforme : « pour compter du 1er janvier 1996, conformément au tableau ci-joint » ; tableau au « JO no 0014 du 17/01/96 Page 801 » |
| Arrêté du 29 décembre 1994, article 1er | JORFARTI000001974748 | conforme : « pour compter du 1er janvier 1995 » |
| Arrêté du 31 janvier 1995 | JORFARTI000002373607 | conforme : « au lieu de: << 14 773,03 >>, lire: << 14 733,03 >>. » |
| Code des pensions de retraite des marins, L. 42 | LEGIARTI000006791949, du 31 mars 1968 au 1er décembre 2010 | conforme : « En cas de modification générale des salaires dépassant 5 % par rapport aux taux antérieurs, il est procédé à la révision du salaire forfaitaire. » |
| Le même code, R. 11, 3° | LEGIARTI000006791987 | conforme au « huit fois » du test : « Lorsque le salaire ainsi défini excède huit fois le montant du traitement brut correspondant à l'indice 100 dans la fonction publique, la portion dépassant cette limite n'est comptée que pour moitié. » |
| Décret n° 2001-1203 | JORFTEXT000000580421 | conforme, mot pour mot, y compris l'erreur de la source (« 1103/97 du 17 Juin 1991 », quand le visa dit « du 17 juin 1997 ») ; la phrase suit bien les signatures et « Rectificatif au JO du 23-02-2002 page 3475 » ; les articles du décret sont à part dans l'index (JORFARTI000001325423…) : « paragraphe d'explication » est juste |
| Décret n° 85-1148, article 7, en 1995 | LEGIARTI000006454542, du 1er août 1991 au 20 février 1998 | conforme : « le traitement afférent à l'indice majoré 158 (indice brut 100) » ; la dérogation de l'indice majoré 202 vise une liste close (code des pensions civiles et militaires, décret du 9 septembre 1965, code des communes…) où le code des marins n'est pas |
| Décret n° 95-942 | JORFTEXT000000736551, article 5 (JORFARTI000001784299) | conforme : il nomme le forfait de la troisième catégorie et celui du classement du marin, sans aucun montant |

## 2. Les vingt-trois points de l'article 3

J'ai listé les quarante-six rédactions de l'article 3 du décret n° 85-1148 que
l'index porte, avec leurs dates. Pour chaque jour du test, une seule est en
vigueur, et c'est celle de `POINT_DE_L_ARTICLE_3`. Elle écrit le montant que le
test prend. Aucune rédaction n'y fixe un montant rétroactif, à une date antérieure
à son entrée en vigueur.

| Jour | Rédaction en vigueur (début → fin) | Ce qu'elle fixe |
|---|---|---|
| 1985-12-01, 1986-01-01, 1987-01-01 | LEGIARTI000006454423 (1985-11-05 → 1987-02-20) | « 26428 F » |
| 1988-01-01 | …426 (1987-07-31 → 1988-03-01) | « 26 719 F » |
| 1989-01-01 | …428 (1988-09-01 → 1989-03-01) | « 27 523 F à compter du 1er septembre 1988 » |
| 1990-01-01 | …431 (1990-01-01 → 1990-04-01) | « 28 270 F à compter du 1er janvier 1990 » |
| 1991-01-01 | …433 (1990-12-01 → 1991-08-01) | « 28 973 F à compter du 1er décembre 1990 » |
| 1992-01-01 | …434 (1991-08-01 → 1992-02-01) | « 29 118 F à compter du 1er août 1991, puis à 29 408 F à compter du 1er novembre 1991 » : 29 408 F |
| 1993-01-01 | …436 (1992-09-19 → 1993-01-26) | « 30 190 F à compter du 1er octobre 1992 » |
| 1994-01-01 | …438 (1993-12-21 → 1994-07-19) | 30 926 F, et 31 018 F par dérogation (point 5) |
| 1995-01-01 | …440 (1994-12-01 → 1995-02-18) | « 31 422 F à compter du 1er décembre 1994 » |
| 1996-01-01, 1997-01-01 | …442 (1995-11-01 → 1997-03-01) | « 32 244 F à compter du 1er novembre 1995 » |
| 1998-01-01 | …444 (1997-09-27 → 1998-02-20) | « 32 567 F à compter du 1er octobre 1997 » |
| 1999-01-01 | …446 (1998-10-23 → 1999-03-20) | « 32 990 F à compter du 1er novembre 1998 » |
| 2000-01-01 | …448 (1999-11-14 → 2000-11-30) | « 33 419 F à compter du 1er décembre 1999 » |
| 2001-01-01 | …449 (2000-11-30 → 2001-05-01) | « 33 586 F à compter du 1er décembre 2000 » |
| 2002-01-01 | …452 (2002-01-01 → 2002-02-16) | « 5 181,75 Euros à compter du 1er janvier 2002 » |
| 2003-01-01 | …454 (2002-10-26 → 2004-01-01) | « 5 249,33 Euros à compter du 1er décembre 2002 » |
| 2004-01-01, 2005-01-01 | …455 (2004-01-01 → 2005-01-18) | « 5 275,58 Euros à compter du 1er janvier 2004 » |
| 2006-01-01 | …458 (2005-10-21 → 2006-07-01) | « 5 371,10 Euros à compter du 1er novembre 2005 » |
| 2007-01-01 | …459 (2006-07-01 → 2007-02-01) | « 5 397,95 Euros à compter du 1er juillet 2006 » |

En 1995, les rédactions …441 (du 18 février au 1er novembre : « 31 799 F à compter
du 1er mars 1995 ») et …442 (« 32 244 F à compter du 1er novembre 1995 ») sont
celles que la note cite. L'indice majoré que `INDICE_100` donne à chacun de ces
jours a été comparé aux rédactions de l'article 7. Il est conforme : 150 en 1985
et 1986, 152 en 1987 et 1988, 154 en 1989, 156 en 1990 et 1991, 158 de 1992 à
1998, 160 en 1999, 164 en 2000 et 2001, 172 de 2002 à 2004, 174 en 2005, 186 en
2006 et 191 en 2007.

## 3. La borne et les plafonds, refaits à la main

Calculs posés en décimales exactes, puis arrondis à la fin :

- la 13e catégorie du 1er janvier 1995 : 14 733,03 × 12 = 176 796,36 F, soit
  26 952,4313 €. La structure de 2008, lue dans l'arrêté du 31 décembre 2007
  (JORFARTI000017964781 : « 13 33 126,69 » et « 20 59 899,76 »), donne un rapport
  de 1,80820239. La vingtième estimée vaut donc 48 735,4507 €, soit 48 735,45 € :
  **conforme** ;
- le plafond du 1er janvier 1995 : 8 × 158 × 314,22 = 397 174,08 F, soit
  60 548,80 €, et le rapport 80,49 %, « 80,5 % » : **conforme** ;
- le plafond du 1er mars au 31 octobre 1995 : 8 × 158 × 317,99 = 401 939,36 F,
  soit **61 275,26 €**. Il vaut 1,2573037 fois la vingtième estimée : il faudrait
  une majoration de 25,7304 % pour que la vingtième passe le plafond. « Plus de
  25,7 % » est donc une condition nécessaire exacte : **conforme** ;
- le plafond du 1er novembre 1995 : 8 × 158 × 322,44 = 407 564,16 F, soit
  62 132,76 €, et le rapport 1,2748986. La note en tire « plus de 27,49 % »,
  quand le seuil est de 27,4899 % : une majoration de 27,4899 % suffit, sans
  dépasser 27,49 %. C'est un écart **négligeable**, et seulement dans la note : la
  fiche dit « plus haut au 1er novembre », sans chiffre ;
- 2005 : 8 × 174 × 5 275,58 / 100 = 73 436,07 €. La vingtième du modèle, de
  55 160,27 €, en fait 75,11 %, soit « au plus 75,1 % ». Relevée de l'écart du
  1er janvier 1995 (× 1,1454424), elle atteint 86,04 %, soit « sous 86,1 % » :
  **conforme** ;
- 1985 : 8 × 150 × 264,28 / 6,55957 = 48 347,07 €, soit un rapport de 62,79 %. Au
  plafond que le modèle prend en 1985 (46 265,28 €, le point de la série au
  1er janvier), le rapport est de 65,62 % : **conforme**.

Les rapports de la vingtième au plafond du texte ont été refaits pour les vingt-trois
jours. Ils vont de 62,79 % (1985) à 75,11 % (2005), qui reste le plus haut. Le
second plus haut est 2004, à 73,59 %.

Les centimes de la section 4 de la note ont aussi été refaits :

- 25 980,90 × 28 043,44 / 29 486,72 = 24 709,2186, soit 24 709,22 € ;
- 25 980,90 × 0,951054 = 24 709,2389, soit 24 709,24 € ;
- 26 952,43 × 1,808202 = 48 735,4378, soit 48 735,44 € ;
- 59 899,76 × 9 466,62 / 29 486,72 = 19 230,6322, soit 19 230,63 €.

Les salaires moyens du modèle, non arrondis, sont ceux que la note écrit. Les
autres pourcentages de la fiche sont **conformes** :

- 14,544 %, soit « 14,5 % » ;
- 12,697 %, soit « 12,7 % » ;
- 2,164 %, soit « 2,2 % » ;
- 2,118 %, soit « 2,1 % ».

Une remarque, qui n'est pas un écart. Que l'écart du second semestre soit « plus
grand » se déduit du seul titre de l'arrêté, « portant majoration ». La fiche le
dit, en écrivant « majorée selon son titre ». Une majoration qui épargnerait une
catégorie y laisserait l'écart égal.

## 4. Les tests

`tests/test_marins.py` donne 76 tests verts, aucun sauté, l'index LEGI étant là.
Sous `PRESOMPTIONS_DECALEES=1`, ils sont encore 76, et verts.
`python -m pytest -m rapide` est vert lui aussi (point 8).

Pour voir les tests mordre, j'ai faussé une valeur dans ma copie, lancé le test
visé, puis tout rétabli (`git checkout --`, arbre propre ensuite) :

| Ce qui est faussé | Ce qui échoue |
|---|---|
| le point de 1990 pris à « 28 607 F à compter du 1er avril 1990 », même rédaction | la relecture LEGI : le montant est absent de LEGIARTI000006454431 |
| le même, avec la rédaction d'avril 1990 (…432) | la relecture LEGI : « 1990-04-01 <= 1990-01-01 » est faux |
| le point de 1993 pris à la rédaction de février 1993 (…437, « 30 711 F ») | la relecture LEGI, sur la date. **Le deuxième test, seul, passe** |
| le point de 1994 pris à la dérogation, 31 018 F | la relecture LEGI : « est fixée à 31 018 F » n'est pas dans le texte |
| le point de 2005 à « 5 175,58 Euros » (essai de la note) | le deuxième test : « au plus 76,6 % du plafond (2005) » absent, comme la note le dit |
| l'indice de juillet 2004 mis à 172 | la relecture de l'article 7, et le deuxième test (« au plus 76,0 % ») |
| `PLAFOND_DU_1ER_JUILLET_1995` au point de janvier, 314,22 | le premier test : « la relevait de plus de 24,2 % » absent |
| dans la fiche, « 25,7 % » mis à 25,8 % | le premier test |
| dans la fiche, « 61 275,26 € » mis à 61 275,25 € | le premier test |
| la fiche d'avant le commit (a66e323^) | le premier test : « paragraphe d'explication » absent, comme la note le dit |
| la première des trois mentions « du 1er janvier au 30 juin 1995 » ôtée de la fiche | **rien** : les deux autres suffisent au test |

Les tests mordent donc. Deux limites, toutefois :

- **Faible.** `.github/workflows/tests.yml` ne récupère pas l'index de la DILA :
  aucune ligne n'y nomme `dila_index` ni `legi.sqlite`. Sur GitHub, les vingt-trois
  relectures des points sont donc sautées, comme celles de l'article 7. Le
  deuxième test, seul à tourner, ne voit pas un point faussé avec sa rédaction tant
  que 2005 reste le plus haut : c'est l'essai de 1993. La garde des vingt-trois
  valeurs ne tient que dans une session qui a récupéré l'index. Le test le dit
  (« quand il est là ») ; le propriétaire peut vouloir que la suite de GitHub
  récupère l'index.
- **Négligeable.** La borne au premier semestre n'est vérifiée qu'en une
  occurrence. Ôtée devant un chiffre, elle laisserait le test vert.

Remarque d'arrondi. Le test écrit « plus de {X} % », X étant arrondi au plus proche
(`_dixiemes`). Une condition nécessaire voudrait un arrondi vers le bas. Le seuil
étant de 25,730 %, les deux donnent 25,7 ; l'écart n'apparaîtrait que si le seuil
passait au-dessus de x,x5.

## 5. 1994 : les deux valeurs de l'article 3

**Le texte.** La rédaction LEGIARTI000006454438, en vigueur du 21 décembre 1993 au
19 juillet 1994, a deux alinéas. Le premier fixe la valeur annuelle « afférents à
l'indice 100 majoré » à « 30 926 F à compter du 1er janvier 1994 ». Le second :
« Par dérogation à l'alinéa précédent, la valeur annuelle du traitement et de la
solde afférents à l'indice 100 majoré et soumis aux retenues pour pension est
fixée, pour les agents dont l'indice majoré est inférieur ou égal à 275, à
31 018 F à compter du 1er janvier 1994. »

L'article 7 (LEGIARTI000006454542) constitue le traitement de l'indice 100 par « le
traitement afférent à l'indice majoré 158 ». Aucun des deux articles ne dit quel
alinéa s'applique à ce traitement. **M1-ter a raison** : le texte ne le dit pas.

J'ajoute un argument que la note ne donne pas. Lu à la lettre, l'article 7 parle
du traitement d'un indice majoré, 158, qui est inférieur à 275 : on peut y lire la
dérogation. On peut lire aussi que la dérogation ne vise que des « agents », et que
le traitement de l'indice 100 est une référence, non un agent. Le test prend
30 926 F, qui donne le plafond le plus bas et ne peut que relever le rapport. Pour
ce que le test affirme (la vingtième reste sous le plafond), c'est le choix
prudent.

**La série.** `legislation/point_indice_fonction_publique.csv` porte 47,2165 € en
1994. Les deux points de l'article 3 valent 309,26 / 6,55957 = 47,14638 € et
310,18 / 6,55957 = 47,28664 €. Leur moyenne, 47,21651 €, arrondie au dix-millième,
donne bien 47,2165 € : **conforme** à ce que M1-ter relève. Pour les autres années
de 1986 à 2007, la série est celle de l'article 3, à l'arrondi près. Le plafond
qu'en tire le modèle s'écarte de moins de six centimes de celui du texte.

Son en-tête dit aussi que « la base ne garde pas toutes les versions anciennes de
l'article — deux relèvements manquent, celui du 1er novembre 1991 et celui du
1er janvier 1994 ». Or l'index les porte : le premier dans LEGIARTI000006454434
(« puis à 29 408 F à compter du 1er novembre 1991 »), le second dans
LEGIARTI000006454438. Sur ce point aussi, M1-ter est **conforme**.

**Ce que cela change au plafond de 1994, au plus :**

| Plafond du 1er janvier 1994 (8 × 158 points) | Montant | Rapport de la vingtième du modèle (41 535,47 €) |
|---|---|---|
| à l'alinéa général, 30 926 F | 390 904,64 F, soit 59 593,03 € | 69,70 % |
| à la dérogation, 31 018 F | 392 067,52 F, soit 59 770,31 € | 69,49 % |
| au modèle, la série à 47,2165 € | 59 681,66 € | 69,60 % |

Le droit laisse un écart de 177,28 € (0,30 %) entre ses deux lectures. Le modèle
se tient entre les deux : à 88,63 € au-dessus de la première, à 88,65 € au-dessous
de la seconde. Il s'écarte donc de **88,65 € au plus, soit 0,15 %**, de la valeur
que le droit retiendra.

Au-delà du plafond, le salaire de référence n'est compté que pour moitié : pour un
marin qui le dépasse, le salaire de référence se déplace de **44,33 € par an au
plus**. Pour la grille du modèle, rien ne change : sa vingtième reste sous le
plafond. Relevée de l'écart de 1995, elle fait 79,84 % ou 79,60 %, et 2005 reste
le plus haut. L'abattement ne mord pas.

Le même dédoublement revient du 1er août au 30 novembre 1994 (LEGIARTI000006454439 :
31 080 F, et 31 173 F par dérogation). Le modèle, qui prend le point du 1er janvier
pour l'année, convention que la limite déclare (« au point du 1er janvier »), ne le
suit pas. Je n'ai rien corrigé.

**Écart faible.** L'indétermination est déclarée dans le commentaire de
`POINT_DE_L_ARTICLE_3`, dans la note et dans le journal de M1-ter. Elle ne l'est
ni dans la fiche `marins_salaire_de_reference`, ni dans l'en-tête de la série. Or
le plafond que le modèle applique en 1994 n'est écrit par aucun des deux alinéas.
La série sort de la zone de M1-ter, qui l'a signalé à l'orchestration. Il reste à
une session des données de dire, dans la fiche ou dans la série, que la valeur de
1994 est une moyenne que le texte n'écrit pas.

## 6. La recherche des arrêtés de 1995 et 1996

J'ai refait la recherche plein texte `"salaires forfaitaires" marins` dans le JORF,
publiés en 1995 et 1996. Elle rend 19 documents. On y trouve les arrêtés du
29 décembre 1994 (publié le 5 janvier 1995), du 31 janvier 1995, du 30 juin 1995 et
du 30 décembre 1995, ainsi que les décrets n° 95-428, 95-942 et 96-1231.

On y trouve aussi l'**arrêté du 2 août 1995** « portant classement des officiers
des navires transportant des passagers » (JORFTEXT000000554960). Il classe ces
officiers « en fonction de la puissance et de la jauge brute », sans aucun montant
de forfait. La note dit que la recherche « ne donne pas d'autre arrêté » que les
quatre : c'est inexact, d'où un écart **faible**. La conclusion n'en change pas :
aucune autre grille. La fiche, qui écrit « les arrêtés des salaires forfaitaires
publiés en 1995 et 1996 », ne l'a pas reprise.

## 7. Ce que le texte ne tranche pas : est-ce déclaré ?

- La grille du second semestre 1995 : déclarée inconnue, dans la fiche et dans la
  limite, avec la référence au Journal officiel imprimé. **Conforme.**
- La structure de la grille d'avant 2008, et une vingtième qui suivrait l'écart de
  la treizième : c'est l'hypothèse, dite dans la fiche et posée en condition dans
  la limite. **Conforme.**
- La valeur juridique de la phrase du taux du franc : un paragraphe d'explication,
  hors des articles, le règlement n'étant pas ouvert. **Conforme.**
- Le traitement de l'indice 100 en 1994 : déclaré dans le test et la note
  seulement (point 5, faible).
- L'écart du second semestre « plus grand », tiré du titre : dit « selon son
  titre ». **Conforme.**

## 8. La suite rapide

`python -m pytest -m rapide` : 4 265 tests verts, 6 sautés, en 3 min 28 s, sur
l'arbre d'a66e323, une fois les essais de la section 4 rétablis.

## Sources ouvertes

- Index JORF : JORFTEXT000000188385, JORFARTI000001014013, JORFARTI000001014119,
  JORFARTI000001977662, JORFARTI000001594620, JORFARTI000001593286,
  JORFARTI000001974748, JORFARTI000002373607, JORFARTI000017964781,
  JORFTEXT000000580421 en entier et la liste de ses articles,
  JORFTEXT000000554960, JORFTEXT000000736551 et son article 5
  (JORFARTI000001784299), ainsi que la recherche `"salaires forfaitaires" marins`
  de 1995 et 1996.
- Index LEGI : L. 42 (LEGIARTI000006791949) et R. 11 (LEGIARTI000006791987) du
  code des pensions de retraite des marins ; toutes les rédactions des articles 3
  (46) et 7 (27) du décret n° 85-1148.
- Dans le dépôt : `regimes/salaires_forfaitaires.csv`,
  `legislation/point_indice_fonction_publique.csv`, les salaires moyens et le
  plafond du modèle (`liquider.plafond_du_salaire_de_reference`) de 1985 à 2007.

Non vérifié, faute de texte : les tableaux du Journal officiel imprimé de 1995
(n° 164, page 10596 ; n° 14 de 1996, page 801). La question en est posée au
propriétaire.
