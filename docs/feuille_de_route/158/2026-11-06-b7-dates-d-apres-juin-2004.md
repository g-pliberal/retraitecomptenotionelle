# B7 : les dates d'effet des tableaux d'après juin 2004, par l'article 1er du code civil

Vague 11, B7, le 6 novembre 2026, sur Opus. Reprend les 42 tableaux de reclassement que B6-bis a
comptés (`2026-11-06-b6-bis-corrections-de-r-b7.md`, point 7) : `effet` vide, une phrase qui
date le reclassement de l'entrée en vigueur, de l'effet ou de la publication « du présent
décret » (ou « du présent titre », n° 2010-982, ou d'un autre décret, n° 2004-1439 et 2010-302),
dans 34 textes publiés au JO du 30 décembre 2004 au 10 novembre 2019. Lu pendant la session :
l'index LEGI du dépôt (dump `Freemium_legi_global_20250713-140000`, à jour au 20261102-213929)
et l'index JORF (`Freemium_jorf_global_20250713-140000`, à jour au 20261103-002311), récupérés
par `dila_index.py --recuperer`, table `doc`, et effacés en finissant ; Légifrance, par l'outil de
lecture web, pour ce que les index n'ont pas (dit à chaque fois) ; le Noyau RH du dépôt
(`data/reference/grilles/etat/textes.csv`) en recoupement. Aucun fac-similé n'est lu. Aucune
règle du scénario 1 n'est touchée : des dates d'effet de tableaux de reclassement.

**Ce qui en sort.** 34 tableaux datés ; 7 laissés sans date, les deux lectures citées (points
non tranchés) ; 1 laissé sans date parce que le lecteur l'a mal découpé. 34 + 7 + 1 = 42.

## 1. La règle : code civil, art. 1er

**Lu à Légifrance** le 6 novembre 2026 (https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006419280,
réponse 200), « Article 1 », « En vigueur depuis le 01 juin 2004 », « Modifié par Ordonnance
n°2004-164 du 20 février 2004 - art. 1 () JORF 21 février 2004 en vigueur le 1er juin 2004 » :

> Les lois et, lorsqu'ils sont publiés au Journal officiel de la République française, les actes
> administratifs entrent en vigueur à la date qu'ils fixent ou, à défaut, le lendemain de leur
> publication. Toutefois, l'entrée en vigueur de celles de leurs dispositions dont l'exécution
> nécessite des mesures d'application est reportée à la date d'entrée en vigueur de ces mesures.
>
> En cas d'urgence, entrent en vigueur dès leur publication les lois dont le décret de
> promulgation le prescrit et les actes administratifs pour lesquels le Gouvernement l'ordonne
> par une disposition spéciale.
>
> Les dispositions du présent article ne sont pas applicables aux actes individuels.

La même citation, ses trois alinéas mis bout à bout, est `ARTICLE_1ER_DU_CODE_CIVIL`
(`scripts/fetch/dila_legi_reclassements.py`), et l'en-tête de `tableaux.csv` la porte une fois.

**A-t-il changé depuis 2004 ?** L'article n'est dans aucun des deux index (recherche par numéro et
par titre « code civil » au LEGI, par « 2004-164 » au JORF : seuls des visas et des avis le
citent ; les index sont filtrés sur le champ social, `THEMATIQUE` de `dila_index.py`) :
`--diff` et `--le` ne s'y appliquent pas. La page de Légifrance dit « En vigueur depuis le 01 juin
2004 » : la version en vigueur le 6 novembre 2026 est celle qui s'ouvre le 1er juin 2004, il n'y en
a donc pas eu d'autre entre-temps ; elle couvre les 34 textes (JO du 30 décembre 2004 au 10
novembre 2019). La liste des versions (« Voir les versions ») n'a pas d'adresse lisible ; la page
de l'ordonnance (/loda/id/LEGIARTI000006228779/2004-06-01) répond 403 : sa rédaction n'est lue
qu'au travers de l'article du code.

**Ce que l'article dit des cas de la tâche.** (1) La date que le texte fixe, sinon le lendemain
de sa publication. (2) Les dispositions qui attendent une mesure d'application : reportées à
l'entrée en vigueur de cette mesure ; une seule phrase de tableau en relève, celle du n° 2010-302,
art. 9, qui renvoie elle-même au décret qui inscrit chaque corps (point 6). (3) L'urgence : une
« disposition spéciale » ; aucun des 34 textes n'en porte (recherche de « urgence » dans tous
leurs articles : seul le « secours d'urgence » du n° 2016-2008, art. 3). (4) L'effet rétroactif :
l'article n'en dit rien ; « la date qu'ils fixent » peut précéder la publication (n° 2018-648,
point 3), la donnée date ce que le texte date sans en examiner la validité, comme pour les trois
de B6. (5) Les actes individuels : les 34 textes sont des décrets portant statut ou modifiant
des statuts (leurs titres) ; aucun n'est un acte individuel.

## 2. La méthode, texte par texte

- **Le jour du JO** : le champ `date` du texte signé à l'index JORF (DATE_PUBLI, `dila_index.py`,
  ligne 180), titre « Décret n° … du … », sans rectificatif. Le Noyau RH donne un autre jour pour
  deux textes ; Légifrance (page du texte au JORF) les tranche : n° 2011-489, « JORF n°0104 du 5
  mai 2011 » (le Noyau, texte 809 : publication 2011-05-06) ; n° 2006-8, « JORF n°4 du 5 janvier
  2006 » (le Noyau, texte 28 : 2006-01-04). L'index JORF dit le 5 dans les deux cas.
- **Le texte entier** : tous les articles du texte signé, à l'index JORF, du 1er à l'article
  d'exécution (« sont chargés, chacun en ce qui le concerne, de l'exécution du présent décret »),
  sans trou : c'est le cas de 31 textes. Trois ne sont pas entiers à l'index (filtre thématique) :
  n° 2012-1139 (17 articles sur 69), n° 2014-71 (11 sur 15 : manquent 3, 8, 14, 15), n° 2015-363
  (12 sur 15 : manquent 11, 14, 15). Leurs articles manquants sont lus à Légifrance, page de
  l'article au JORF (« /jorf/article_jo/JORFARTI… », réponse 200), sauf l'art. 3 du n° 2014-71, lu
  sur la page du texte ; ceux du n° 2012-1139 autres que les art. 68 et 69 ne sont pas lus (sa
  clause vaut pour tout le décret, sans exception : point 3).
- **Les clauses** : dans chaque article, chaque phrase qui porte une date (hors celle d'un texte
  cité) ou les mots vigueur, effet, applicable, compter, partir, premier jour, lendemain,
  rétroactif, urgence, publication, relue à la main ; puis une garde écrite, `CLAUSE`
  (`tests/test_reclassements.py`) : le verbe conjugué (« entre », « entrent », « entrera »,
  « entreront en vigueur » ; « prend », « prennent », « prendra », « prendront effet » ;
  « produit effet » ; « sont applicables à compter », « au », « le ») après « présent
  décret / titre / chapitre », « dispositions » ou « article N », plus « rétroacti » et
  « urgence ». Elle trouve chacune des clauses relevées par B5-bis, B6 et B7, et ne prend ni
  « à la date d'entrée en vigueur du présent décret », ni « la titularisation prend effet »
  (n° 2016-1177, art. 7, JORFARTI000033076708), ni « sont applicables aux concours »
  (`test_la_clause_reconnait_ce_qui_date_un_texte_et_non_le_reste`). Au LEGI, les seules
  versions ouvertes au plus tard à la date retenue : les suivantes viennent d'autres décrets, dont
  le LEGI note la date (n° 2005-939 : « Conformément à l'article 12 du décret n° 2023-527 du 29
  juin 2023, ces dispositions entrent en vigueur le 1er juillet 2023 », LEGIARTI000047767158, et
  d'autres, de 2023 et de 2027).
- **La phrase du tableau**, relue entière pour chacun (l'intro de `tableaux.csv`), et confrontée
  à ses lignes : c'est ainsi que le n° 2004-1439 est écarté (point 7).
- **En recoupement** : la notice du texte signé (« Entrée en vigueur : … », à l'index JORF, pour
  les textes de 2011 et après), le début de la version du tableau au LEGI, le champ `effet` du
  Noyau RH (`etat/textes.csv`, État seulement). Ils ne décident d'aucune date : la clause, ou son
  absence, décide.

## 3. Les 13 tableaux que leur décret date d'une clause « en vigueur »

Chaque clause : seule version au LEGI ; au JORF, l'article entier, mot pour mot (au n° 2010-1719 et
2010-1720, suivi de « Fait le 30 décembre 2010. », la formule de signature, que la garde
`_est_l_article` admet au JORF seulement). « Premier jour du mois qui suit » : le 1er du mois
d'après le jour du JO.

| Décret, JO (JORFTEXT) | Clause (LEGI ; JORF), citée entière | Calcul | Tableau (LEGI, début de la version) | `effet` |
|---|---|---|---|---|
| n° 2010-1719, 31 déc. 2010 (`JORFTEXT000023333539`) | art. 23 (`LEGIARTI000023400748` ; `JORFARTI000023333637`) : « La ministre de l'économie, des finances et de l'industrie, le ministre du budget, des comptes publics, de la fonction publique et de la réforme de l'Etat, porte-parole du Gouvernement, et le secrétaire d'Etat auprès du ministre du budget, des comptes publics, de la fonction publique, et de la réforme de l'Etat, chargé de la fonction publique sont chargés, chacun en ce qui le concerne, de l'exécution du présent décret, qui entrera en vigueur au 1er janvier 2011 et sera publié au Journal officiel de la République française. » | date écrite | art. 14, `LEGIARTI000023400750` (2011-01-01) | **2011-01-01** |
| n° 2010-1720, 31 déc. 2010 (`JORFTEXT000023333639`) | art. 27 (`LEGIARTI000023410103` ; `JORFARTI000023333664`) : « La ministre de l'économie, des finances et de l'industrie, le ministre du budget, des comptes publics, de la fonction publique et de la réforme de l'Etat, porte-parole du Gouvernement, et le secrétaire d'Etat auprès du ministre du budget, des comptes publics, de la fonction publique et de la réforme de l'Etat, chargé de la fonction publique, sont chargés, chacun en ce qui le concerne, de l'exécution du présent décret, qui entrera en vigueur au 1er janvier 2011 et sera publié au Journal officiel de la République française. » | date écrite | art. 14, `LEGIARTI000023410135` (2011-01-01) | **2011-01-01** |
| n° 2012-761, 10 mai 2012 (`JORFTEXT000025838289`) | art. 17 (`LEGIARTI000025855104` ; `JORFARTI000025838367`) : « Le ministre de la défense et des anciens combattants, le garde des sceaux, ministre de la justice et des libertés, le ministre du travail, de l'emploi et de la santé, le ministre de l'éducation nationale, de la jeunesse et de la vie associative, la ministre du budget, des comptes publics et de la réforme de l'Etat, porte-parole du Gouvernement, et le ministre de la fonction publique sont chargés, chacun en ce qui le concerne, de l'exécution du présent décret, qui sera publié au Journal officiel de la République française et entrera en vigueur le premier jour du mois qui suit sa publication. » | mai → juin | art. 10, `LEGIARTI000025855090` (2012-05-11) | **2012-06-01** |
| n° 2012-762, 10 mai 2012 (`JORFTEXT000025838383`) | art. 37 (`LEGIARTI000025855239` ; `JORFARTI000025838503`) : mêmes mots que l'art. 17 du n° 2012-761, mot pour mot (vérifié à l'index) | mai → juin | art. 22, `LEGIARTI000025855187` (2012-05-11) | **2012-06-01** |
| n° 2012-1002, 30 août 2012 (`JORFTEXT000026326536`) | art. 14 (`LEGIARTI000026327475` ; `JORFARTI000026326574`) : « Le ministre de l'économie et des finances, le ministre du redressement productif, la ministre de la réforme de l'Etat, de la décentralisation et de la fonction publique et le ministre délégué auprès du ministre de l'économie et des finances, chargé du budget, sont chargés, chacun en ce qui le concerne, de l'exécution du présent décret, qui sera publié au Journal officiel de la République française et entrera en vigueur le premier jour du mois suivant sa publication. » | août → septembre | art. 8, `LEGIARTI000026327465` (2012-09-01) | **2012-09-01** |
| n° 2013-176, 28 févr. 2013 (`JORFTEXT000027114846`) | art. 39 (`LEGIARTI000027115996` ; `JORFARTI000027114957`) : « Les dispositions du présent décret entreront en vigueur le premier jour du mois suivant sa publication au Journal officiel de la République française. » | février → mars | art. 27, `LEGIARTI000027115984` (2013-03-01) | **2013-03-01** |
| n° 2013-875, 29 sept. 2013 (`JORFTEXT000027996887`) | art. 18 (`LEGIARTI000027998176` ; `JORFARTI000027996949`) : même phrase que l'art. 39 du n° 2013-176 | septembre → octobre | art. 10, `LEGIARTI000027998167` (2013-10-01) | **2013-10-01** |
| n° 2013-974, 31 oct. 2013 (`JORFTEXT000028138788`) | art. 32 (`LEGIARTI000028140167` ; `JORFARTI000028138899`) : « Le présent décret entrera en vigueur le premier jour du mois suivant sa publication. » | octobre → novembre | art. 23, `LEGIARTI000028140216` (2013-11-01) | **2013-11-01** |
| n° 2016-2008, 31 déc. 2016 (`JORFTEXT000033759014`) | art. 29 (`LEGIARTI000033792417` ; `JORFARTI000033759090`) : « Sous réserve des dispositions de l'article 12,le présent décret entre en vigueur le 1er janvier 2017. » (sans espace après la virgule, au LEGI comme au JORF) | date écrite | art. 21, `LEGIARTI000033792401` (2017-01-01) | **2017-01-01** |
| n° 2018-648, 25 juil. 2018 (`JORFTEXT000037245707`) | art. 8 (`LEGIARTI000037246485` ; `JORFARTI000037245737`) : « Les dispositions du présent décret entrent en vigueur le 1er janvier 2017, à l'exception de celles des articles 1er, 5 et 6. » | date écrite | art. 7, `LEGIARTI000037246483` (2018-07-26) | **2017-01-01** |
| n° 2012-1139, 11 oct. 2012 (`JORFTEXT000026477051`) | art. 68, **lu à Légifrance** (`JORFARTI000026477172`, absent des deux index) : « Les dispositions du présent décret entrent en vigueur le premier jour du mois suivant celui de sa publication au Journal officiel de la République française. » | octobre → novembre | art. 50, `LEGIARTI000026477976` (2012-11-01) | **2012-11-01** |
| n° 2015-363, 31 mars 2015 (`JORFTEXT000030419563`) | art. 14, **lu à Légifrance** (`JORFARTI000030419590`) : « Le présent décret entre en vigueur le premier jour du mois qui suit sa publication. » | mars → avril | art. 12, `LEGIARTI000030420449`, tableaux 1 et 2 (2015-04-01) | **2015-04-01** |

**Les réserves et exceptions, lues.** n° 2016-2008 : l'art. 12 que la clause réserve
(`JORFARTI000033759055`) dit « A compter du 1er janvier 2020 : 1° Le grade de capitaine comprend
dix échelons. […] » ; le tableau est à l'art. 21 (« A la date d'entrée en vigueur du présent
décret, les capitaines, commandants et lieutenants-colonels […] sont reclassés ») : la réserve ne
le touche pas. n° 2018-648 : les articles exceptés sont l'art. 1er (une référence : « l'article
29 de la loi du 11 janvier 1984 » devient « l'article 13 de la loi du 13 juillet 1983 »), l'art. 5
(le détachement, art. 9 du décret de 2003) et l'art. 6 (l'abrogation des art. 10 à 15) ; la grille
neuve (art. 2, « Ce grade comporte douze échelons ») et le tableau (art. 7) ne le sont pas. Deux
lectures étaient possibles pour « la date d'entrée en vigueur du présent décret » d'un décret qui
en a deux ; la première (le 1er janvier 2017, la date de « les dispositions du présent décret »,
dont l'art. 7) a pour elle la notice du JORF (« le décret entre en vigueur le 1er janvier 2017, à
l'exception de ses articles 1er, 5 et 6 qui entrent en vigueur le lendemain de sa publication »)
et le Noyau RH (texte 5964, effet 2017-01-01) ; la seconde (le 26 juillet 2018) ne vaudrait que
pour les articles exceptés, aucun ne reclasse : je retiens la première, comme B6 au n° 2023-709.
C'est un effet antérieur à la publication : l'en-tête de `tableaux.csv` le dit (« Quatre effets
précèdent la publication »). n° 2012-1139 : la clause n'excepte rien ; le tableau est l'art. 50.

**Recoupements.** Notices : n° 2012-761 et 2012-762 « le texte entre en vigueur le premier jour
du mois qui suit sa publication » ; 2012-1002 « le 1er septembre 2012 » ; 2012-1139 « le 1er
novembre 2012 » ; 2013-176 « le 1er mars 2013 » ; 2013-875 « le 1er octobre 2013 » ; 2013-974 « le
1er novembre 2013 » ; 2015-363 « le 1er avril 2015 » ; 2016-2008 « le 1er janvier 2017 ». Noyau RH
(`effet`) : 2010-1719 et 2010-1720 2011-01-01 ; 2012-762 2012-06-01 ; 2012-1002 2012-09-01 ;
2012-1139 2012-11-01 ; 2013-176 2013-03-01 ; 2013-875 2013-10-01 ; 2013-974 2013-11-01. Le Noyau RH
dit 2012-05-11 pour le n° 2012-761 (texte 1315), comme le LEGI : la clause dit le premier jour du
mois qui suit, et la notice aussi.

## 4. Le tableau daté par titre : n° 2010-982

JO du 28 août 2010 (`JORFTEXT000022747189`). Art. 39 (`LEGIARTI000022751503`, seule version ;
`JORFARTI000022747215`) : « I. ― Les dispositions du titre Ier entrent en vigueur le 1er septembre
2011. II. - Les dispositions du titre II entrent en vigueur le 1er septembre 2010. » Le tableau,
art. 33 (`LEGIARTI000022751573`, version du 2010-09-01) : « Les agents appartenant au corps des
contrôleurs des impôts et au corps des contrôleurs du Trésor public sont reclassés respectivement
dans chacun des grades de leur corps à la date d'entrée en vigueur du présent titre conformément au
tableau de correspondance suivant : ». La table des matières du texte au JORF (Légifrance, page du
texte, « JORF n°0199 du 28 août 2010 ») : « TITRE II : DISPOSITIONS MODIFIANT DIVERSES
DISPOSITIONS STATUTAIRES APPLICABLES AUX CORPS DES CONTROLEURS DES IMPOTS ET DES CONTROLEURS DU
TRESOR PUBLIC (Articles 31 à 38) », dont « CHAPITRE II : DISPOSITIONS TRANSITOIRES (Articles 33 à
38) ». L'art. 33 est au titre II : **2010-09-01** (le début du LEGI). Le Noyau RH (texte 719) dit
2010-08-29, le lendemain du JO, pour le texte entier : il ne lit pas la clause.

## 5. Les trois tableaux que leur décret date d'une clause « prend effet » (points non tranchés)

Comme le n° 2011-1140 (B6-bis, point 2) : la seule clause de date du décret dit « prend effet »,
non « entre en vigueur ». Deux lectures : (1) la date de la clause est celle de l'entrée en vigueur
(le décret n'en fixe pas d'autre, et la clause serait sans objet pour le tableau sinon) ; (2) le
décret, qui ne fixe pas son entrée en vigueur, entre en vigueur le lendemain de sa publication
(code civil, art. 1er) et ne prend effet qu'à la date de la clause. J'écris la lecture (1), selon
la règle de B6-bis : aucune source ne donne l'autre date, et la garde (`PRISES_D_EFFET`,
`seule_clause`) vérifie, au JORF entier et au LEGI, qu'aucun autre article ne dit quand le décret
s'applique.

| Décret, JO | Clause (LEGI ; JORF), entière | Tableau | (1) | (2) | Recoupement |
|---|---|---|---|---|---|
| n° 2005-939, 6 août 2005 (`JORFTEXT000000813276`) | art. 28 (`LEGIARTI000006413799` ; `JORFARTI000001138514`) : « Le ministre d'Etat, ministre de l'intérieur et de l'aménagement du territoire, le ministre de l'économie, des finances et de l'industrie, le garde des sceaux, ministre de la justice, le ministre de la fonction publique et le ministre délégué au budget et à la réforme de l'Etat, porte-parole du Gouvernement, sont chargés, chacun en ce qui le concerne, de l'exécution du présent décret, qui prendra effet au 1er janvier 2006 et sera publié au Journal officiel de la République française. » | art. 20, `LEGIARTI000006413791` (2006-01-01), « A la date d'entrée en vigueur du présent décret » | **2006-01-01** | 2005-08-07 | LEGI 2006-01-01 ; Noyau RH (texte 295) 2006-01-01 ; pas de notice |
| n° 2011-215, 27 févr. 2011 (`JORFTEXT000023631790`) | art. 21 (`LEGIARTI000023632829` ; `JORFARTI000023631867`) : « Les dispositions du présent décret prennent effet le premier jour du mois suivant celui de sa publication. » | art. 13, `LEGIARTI000023632819` (2011-03-01), « A la date d'entrée en vigueur du présent décret » | **2011-03-01** (février → mars) | 2011-02-28 | LEGI 2011-03-01 ; pas de notice ; la ligne 5896 du Noyau RH n'est pas lue (R-B7 § 5) |
| n° 2005-1304, 22 oct. 2005 (`JORFTEXT000000241288`) | art. 43 (`LEGIARTI000006414058` ; `JORFARTI000001663216`) : « Le ministre d'Etat, ministre de l'intérieur et de l'aménagement du territoire, le ministre de l'économie, des finances et de l'industrie, le ministre de la fonction publique et le ministre délégué au budget et à la réforme de l'Etat, porte-parole du Gouvernement, sont chargés, chacun en ce qui le concerne, de l'exécution du présent décret, qui prendra effet au 1er novembre 2005 et sera publié au Journal officiel de la République française. » | art. 36, `LEGIARTI000006414050` (2005-11-01) | **2005-11-01** | 2005-10-23 | LEGI 2005-11-01 ; Noyau RH (texte 386) 2005-11-01 |

Le tableau du n° 2005-1304 n'écrit pas la date du reclassement : « Les ingénieurs régis par le
décret n° 65-1147 du 15 décembre 1965 […], qui se trouvent, à la date de publication du présent
décret, dans l'une des positions mentionnées à l'article 32 de la loi du 11 janvier 1984
susvisée, sont reclassés conformément au tableau de correspondance ci-après : ». « à la date de
publication » dit qui est reclassé, non quand ; le reclassement vaut quand l'article s'applique,
ce que la clause date (`SANS_DATE_ECRITE`). Une troisième lecture, le jour du JO (22 octobre 2005)
comme date du reclassement, prête à la phrase ce qu'elle ne dit pas.

## 6. Les 17 tableaux de décrets sans clause : le lendemain du JO

Chaque décret lu en entier (point 2) : aucun article ne dit quand il s'applique ; aucun n'invoque
l'urgence. Le lendemain du JO, calculé à la main (fin de mois comprise). Les phrases disent « A la
date d'entrée en vigueur du présent décret », ou « régis, à la date d'entrée en vigueur du présent
décret, par le décret […] sont intégrés et reclassés » (n° 2011-744, 2012-78, 2015-1792…) : la
condition et le reclassement tombent le même jour, l'entrée en vigueur de l'article, qui est
celle du décret.

| Décret (JORFTEXT) | Articles lus | JO | Lendemain | Tableau (LEGI, début) | Recoupement |
|---|---|---|---|---|---|
| n° 2007-835 (`JORFTEXT000000793379`) | 5 | 13 mai 2007 | **2007-05-14** | art. 4, `LEGIARTI000006264680` (2007-05-13) | pas de notice, pas au Noyau RH |
| n° 2010-647 (`JORFTEXT000022337185`) | 13 | 13 juin 2010 | **2010-06-14** | art. 12, `LEGIARTI000022338220` (2010-06-14) | Noyau RH 950 : 2010-06-14 |
| n° 2011-489 (`JORFTEXT000023947061`) | 38 | 5 mai 2011 | **2011-05-06** | art. 24, `LEGIARTI000023947863` (2011-05-06) | Noyau RH 809 : 2011-05-07 (publication 2011-05-06 : point 2) |
| n° 2011-744 (`JORFTEXT000024269791`) | 23 | 29 juin 2011 | **2011-06-30** | art. 11, `LEGIARTI000024272771`, tableaux 1 et 2 (2011-06-30) | pas de notice |
| n° 2011-1139 (`JORFTEXT000024580227`) | 30 | 23 sept. 2011 | **2011-09-24** | art. 18, `LEGIARTI000024581275` ; art. 19, `LEGIARTI000024581277` (2011-09-24) | notice « le lendemain de sa publication » ; Noyau RH 1362 : 2011-09-24 |
| n° 2012-78 (`JORFTEXT000025195530`) | 23 | 25 janv. 2012 | **2012-01-26** | art. 11, `LEGIARTI000025196191`, tableaux 1 et 2 (2012-01-26) | notice « le lendemain » |
| n° 2012-229 (`JORFTEXT000025376677`) | 29 | 18 févr. 2012 | **2012-02-19** | art. 18, `LEGIARTI000025377504` (2012-02-19) | notice « le lendemain » ; Noyau RH 1041 : 2012-02-19 |
| n° 2013-489 (`JORFTEXT000027534080`) | 34 | 12 juin 2013 | **2013-06-13** | art. 23, `LEGIARTI000027535136` (2013-06-13) | notice « le lendemain » |
| n° 2013-1173 (`JORFTEXT000028339653`) | 28 | 19 déc. 2013 | **2013-12-20** | art. 17, `LEGIARTI000028342387` (2013-12-20) | notice « le lendemain » ; Noyau RH 1548 : 2013-12-20 |
| n° 2014-71 (`JORFTEXT000028539091`) | 15 (11 à l'index ; 3, 8, 14, 15 à Légifrance) | 31 janv. 2014 | **2014-02-01** | art. 12, `LEGIARTI000028540018` ; art. 13, `LEGIARTI000028540020` (2014-02-01) | notice « le lendemain » |
| n° 2015-1792 (`JORFTEXT000031733312`) | 12 | 30 déc. 2015 | **2015-12-31** | art. 11, `LEGIARTI000031826959` (2015-12-31) | notice « le lendemain du jour de sa publication » ; Noyau RH 1536 : 2015-12-31 |
| n° 2016-1177 (`JORFTEXT000033076677`) | 30 | 31 août 2016 | **2016-09-01** | art. 22, `LEGIARTI000033078337` (2016-09-01) | notice « le lendemain » |
| n° 2019-1160 (`JORFTEXT000039357806`) | 6 | 10 nov. 2019 | **2019-11-11** | art. 5, `LEGIARTI000039363229` (2019-11-11) | notice « au lendemain » ; Noyau RH 6661 : 2019-11-11 |

13 décrets, 17 tableaux (1 + 1 + 1 + 2 + 2 + 2 + 1 + 1 + 1 + 2 + 1 + 1 + 1 = 17). Les articles du
n° 2014-71 lus à Légifrance sont recopiés dans le test (`LUS_A_LEGIFRANCE`) : art. 3 (une
substitution de mots à l'art. 3-1 du n° 2006-227), art. 8 et 14 (l'avancement « postérieurement
à la date d'entrée en vigueur du présent décret »), art. 15 (l'exécution, « qui sera publié au
Journal officiel ») ; aucun ne fixe de date.

**Le n° 2007-835, un écart au LEGI.** Le tableau : « Les moniteurs d'atelier en fonctions à la
date de publication du présent décret sont reclassés conformément au tableau ci-dessous : » : la
date de publication dit qui est reclassé ; le reclassement vaut à l'entrée en vigueur de l'article,
que le décret ne fixe pas : le lendemain, 14 mai 2007. Le LEGI ouvre tous les articles du décret
le 13 mai 2007, jour du JO (comme ceux du n° 2005-1132 le 10 septembre 2005 : son début est le jour
du JO pour ces textes, non une lecture de leur clause) ; entrer en vigueur le jour même demande
l'urgence et une disposition spéciale (art. 1er, deuxième alinéa), que le décret n'a pas.

**Le n° 2013-489 au JORF** : l'article d'exécution (`JORFARTI000027534187`) dit « de l'exécution du
présent, qui sera publié au Journal officiel » ; le mot « décret » manque au texte de l'index, et
le test l'admet en le disant.

## 7. Les huit tableaux laissés sans date

**Les points non tranchés** (`NON_TRANCHES`, effet vide : la donnée garde le début de la version
au LEGI, que l'en-tête de `tableaux.csv` dit) :

- **n° 2005-1132, art. 18, tableaux 1 à 3** (`LEGIARTI000006413884` ; JO du 10 septembre 2005,
  `JORFTEXT000000632356` ; 19 articles, aucune clause) : « A compter de la date de publication du
  présent décret, les préparateurs en pharmacie civils […] sont reclassés selon le tableau de
  correspondance qui suit : ». (1) La date que la phrase écrit, le jour du JO : **10 septembre
  2005** (le début du LEGI). (2) Le décret ne fixe pas son entrée en vigueur : le lendemain, **11
  septembre 2005**, et l'article ne s'applique pas avant ; l'entrée en vigueur le jour même relève
  de l'urgence (deuxième alinéa), que le décret n'invoque pas. Le texte ne dit pas si « à compter
  de la date de publication » est « la date qu'ils fixent » du premier alinéa.
- **n° 2006-8, art. 32 et 33** (`LEGIARTI000006414364`, `LEGIARTI000006414365` ; JO du 5 janvier
  2006, `JORFTEXT000000813897` ; 40 articles, aucune clause) : « […] sont, à la date de publication
  du présent décret, reclassés dans le grade d'ingénieur (divisionnaire) de l'agriculture et de
  l'environnement […] ». (1) **5 janvier 2006** (LEGI ; Noyau RH, texte 28, effet 2006-01-05) ; (2)
  **6 janvier 2006**. Le décret distingue les deux dates : art. 30 (« à compter de l'entrée en
  vigueur du présent décret »), art. 34 (« Les dispositions des articles 32 et 33 ne peuvent
  conduire à reclasser les intéressés à un échelon inférieur à celui dans lequel ils auraient été
  classés si leur promotion par changement de grade n'était intervenu qu'à la date d'entrée en
  vigueur du présent décret »), art. 35, 37, 38 (« la publication du présent décret »).
- **n° 2010-989, art. 26** (`LEGIARTI000022755950`, version du 2010-09-01 ; JO du 28 août 2010,
  `JORFTEXT000022748014`) : « A la date d'entrée en vigueur du présent décret, les contrôleurs des
  douanes et droits indirects […] sont reclassés ». Art. 36 (`LEGIARTI000022755975` ;
  `JORFARTI000022748122`) : « I. ― Les dispositions des chapitres Ier et III entrent en vigueur le
  1er septembre 2010. II. - Les dispositions du chapitre II entrent en vigueur le 1er janvier
  2011. » La table des matières au JORF (Légifrance) : chapitre Ier, art. 1 à 24 ; chapitre II,
  art. 25 (« DISPOSITION MODIFIANT LE DECRET N° 2010 192 DU 25 FEVRIER 2010 […] ») ; chapitre III,
  art. 26 à 37. (1) Le chapitre de l'art. 26 : **1er septembre 2010** (le début du LEGI). (2) « Le
  présent décret » entier, en vigueur quand son dernier chapitre l'est : **1er janvier 2011**, la
  date que le Noyau RH donne au texte (texte 1062). Une source donne la seconde : le critère de
  B6-bis pour écrire la première n'est pas rempli.
- **n° 2010-302, art. 9** (`LEGIARTI000022007850` ; JO du 23 mars 2010, `JORFTEXT000022006980` ;
  18 articles, aucune clause) : « A la date d'entrée en vigueur du décret portant inscription de
  leur corps au sein de l'annexe du présent décret et de celle du décret du 11 novembre 2009
  susvisé, les secrétaires administratifs et membres de corps analogues […] sont intégrés […] et
  reclassés ». Une date par corps, que fixe un autre décret, non lu ici ; la règle de l'art. 1er
  (premier alinéa, seconde phrase) mène au même endroit. Ni l'entrée en vigueur du n° 2010-302 (24
  mars 2010) ni une autre date unique.

**Le tableau mal découpé** (`A_RELIRE`) : **n° 2004-1439, art. 23**, version du 2023-08-01
(`LEGIARTI000047908641`), rétabli par le n° 2023-676, art. 17 (`JORFARTI000047901627`). Sa ligne
de `tableaux.csv` a pour phrase le I (« I.-A la date de l'entrée en vigueur du décret n° 2023-676
du 28 juillet 2023 modifiant le statut particulier du corps d'encadrement et d'application de la
police nationale, les gardiens de la paix, brigadiers de police et brigadiers-chefs de police sont
reclassés selon les modalités suivantes : », sans le mot « tableau »), le tableau du I aplati, puis
le II (« II.-Au 1er janvier 2024, les brigadiers-chefs de classe normale, les brigadiers-chefs de
classe supérieure et les majors sont reclassés conformément au tableau de correspondance
suivant : ») ; ses 15 lignes (`lignes.csv`) sont celles du II (groupes « Major de police »,
« Brigadier-chef de classe supérieure », « Brigadier-chef de la classe normale »). La date du I est
le **1er août 2023** (n° 2023-676, art. 21, `LEGIARTI000047905418` ; JO du 29 juillet 2023,
`JORFTEXT000047901570` : « Le présent décret entre en vigueur le premier jour du mois qui suit celui
de sa publication, à l'exception des dispositions des 3°, 4° et 5° de l'article 3 ainsi que de
celles du 1° de l'article 6, en tant qu'il concerne les majors de police, qui entrent en vigueur le
1er janvier 2024. »), celle du II le **1er janvier 2024**, écrite. Je l'avais d'abord daté du 1er
août 2023 : le chaînage en a tiré un rattachement « Major de police → Major de police » à cette
date, ce qui m'a fait relire l'article ; daté ainsi, le tableau des majors l'aurait été de sept
mois trop tôt. Il reste sans date, et sa lecture est un candidat (point 10).

## 8. Les écarts au LEGI

Quatre des 34 dates s'écartent du début de la version au LEGI : n° 2007-835, art. 4 (2007-05-13 →
2007-05-14) ; n° 2012-761, art. 10, et n° 2012-762, art. 22 (2012-05-11 → 2012-06-01) ; n° 2018-648,
art. 7 (2018-07-26 → 2017-01-01). Les 30 autres le confirment, désormais prouvé. Tableaux sans
`effet` : 296 → 262 (296 − 34).

## 9. Ce que le chaînage en fait

`python scripts/fetch/dila_legi_chainage.py`, sur les fichiers du dépôt : les durées ne bougent
pas (555 rattachés), ni la file du JORF ; les reclassements passent de 19 à **25** groupes
rattachés (843 → 837 déclarés). Tableaux déclarés faute de date : 124 → **105**, dix-neuf tableaux
de l'État (n° 2005-1304, 2010-982, 2010-1719, 2010-1720, 2011-215, 2011-489, 2011-1139 ×2,
2012-229, 2012-761, 2012-762, 2012-1002, 2012-1139, 2013-176, 2013-875, 2013-974, 2013-1173,
2015-1792, 2019-1160 : 17 + 2 = 19), qui sont désormais déclarés pour une autre raison (le libellé
ne se coupe pas en grades du Noyau RH, ou le Noyau RH ne cite pas le statut) ou rattachés. Les six
rattachements neufs, preuve relue :

- **n° 2012-229, art. 18**, trois groupes (classe exceptionnelle, supérieure, normale), le
  2012-02-19 : le Noyau RH fait passer le corps 00109 au corps 01088, le premier cité par le
  n° 2012-229 « du 1993-01-01 au 2012-02-18 », le second « depuis le 2012-02-19 » ; grades
  00230 (grille 01881) → 03005 (01926), 00231 (01917) → 03004 (01925), 00232 (01919) → 03003
  (01924), la veille et le jour. Le jour où le Noyau RH change de corps est le lendemain du JO.
- **n° 2013-875, art. 10**, trois groupes, le 2013-10-01 : corps 00195 (n° 97-364) ; « Contrôleur
  du travail de classe exceptionnelle » 00471 (00479) et « de classe supérieure » 00472 (00480)
  → « hors classe » 03405 (01926) ; « de classe normale » 00473 (00481) → 00473 (01925). Le Noyau RH
  change de grades le jour que la clause fixe.

## 10. Le test d'abord, et ce qui a été lancé

Vus rouges (attribut ou date absents), puis verts : dans `tests/test_reclassements.py`,
`DATES_DU_DECRET` (34 tableaux de plus, la clause et le calcul en commentaire) ;
`test_un_tableau_que_le_texte_ne_date_pas_d_une_seule_lecture_reste_sans_effet` (les sept, et le
tableau mal découpé : sa phrase dit le I, ses lignes portent « Major de police ») ;
`test_l_entete_cite_l_article_1er_du_code_civil_et_les_tableaux_non_tranches` ;
`test_un_decret_sans_clause_entre_en_vigueur_le_lendemain_de_sa_publication` (les 13, à l'index :
le jour du JO, tous les articles du 1er à celui d'exécution, `CLAUSE` ne trouve rien, au JORF et
au LEGI) ; `test_la_clause_reconnait_ce_qui_date_un_texte_et_non_le_reste` ;
`test_une_clause_lue_a_legifrance_est_absente_des_index_et_recoupee_par_la_notice`. Mis à jour :
`test_chaque_date_lue_a_la_main_est_citee_mot_pour_mot_dans_son_texte` (les branches « présent
titre », `SANS_DATE_ECRITE`, `PRISES_D_EFFET` élargi à trois décrets, la garde `seule_clause` au
JORF aussi) ; la garde des citations admet au JORF la formule de signature, et
`test_la_garde_des_citations_refuse_une_citation_tronquee` vérifie qu'elle ne couvre pas une
citation coupée ; `test_l_entete_dit_les_effets_anterieurs_…` (quatre effets, le n° 2018-648) ;
dans `tests/test_chainage_grilles.py`, 124 → 105, le calcul en commentaire.

Les dates du test viennent des textes, non du script : la date de la clause, ou le jour du JO lu
à l'index plus un. `tableaux.csv` ne change que par sa colonne `effet` (34 lignes) et son
en-tête : la régénération complète par `dila_legi_reclassements.py` sur l'index du jour refait
tout (540 tableaux au lieu de 450, l'index ayant changé depuis la lecture) ; elle n'est pas
commitée, et seule la colonne `effet` est recalculée par `effet_du_tableau`, comme l'ont fait B5
à B6-bis (leurs commits ne touchent que cette colonne). Lancés : les fichiers de la zone en
entier, puis `python -m pytest -m rapide` et `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide`
(résultats au commit). Le paquet (`construire_donnees.py`) ne change pas : il ne lit que
`reclassements/lignes.csv`.

## 11. Candidats (non corrigés)

- **Le lecteur des reclassements, n° 2004-1439, art. 23** : il cherche « tableau » pour couper la
  phrase et manque le I, qui dit « selon les modalités suivantes » ; le tableau du I n'est pas lu,
  celui du II prend la phrase du I. D'autres articles à plusieurs paragraphes peuvent être dans ce
  cas : à chercher (une intro qui contient « II.- » ou un second « reclassés »).
- **Le début des versions au LEGI pour les textes de 2005 à 2007** : le jour du JO (n° 2005-1132,
  2007-835, tous leurs articles ; n° 2006-8), non le lendemain. Les tableaux de cette époque dont
  `effet` est vide et dont le décret ne fixe pas de date gardent donc le jour du JO, que l'art. 1er
  ne donne pas : à relever, hors des 42.
- **Le Noyau RH** : jour de publication du n° 2011-489 (2011-05-06 pour le 5 mai) et du n° 2006-8
  (2006-01-04 pour le 5 janvier) ; `effet` du n° 2012-761 (2012-05-11), du n° 2010-982
  (2010-08-29), du n° 2010-989 (2011-01-01) : le recoupement ne vaut pas preuve.
- **n° 2010-302, art. 9** : dater chaque corps par le décret qui l'inscrit à l'annexe.
- Toujours ouverts, hors de la tâche : les 25 tableaux d'avant juin 2004 (question 29 au
  propriétaire), le rectificatif du n° 2015-1275, les 90 tableaux de l'index publié, l'annexe du
  n° 94-1016.

## 12. Ce qui bouge

- `scripts/fetch/dila_legi_reclassements.py` : `ENTREES_EN_VIGUEUR` (14 décrets de plus),
  `ENTREES_LUES_A_LEGIFRANCE` (2), `LENDEMAINS_DE_PUBLICATION` (13), `NON_TRANCHES` (5 articles,
  7 tableaux), `A_RELIRE` (1), `ARTICLE_1ER_DU_CODE_CIVIL`, `DATES_DU_DECRET` (31 articles de plus),
  `effet_du_tableau`, l'en-tête de `tableaux.csv`.
- `data/reference/grilles/reclassements/tableaux.csv` : `effet` de 34 tableaux, l'en-tête.
- `data/reference/grilles/chainage/reclassements.csv` : 76 lignes (6 rattachées, 70 déclarées
  dont la date ou la raison change).
- `tests/test_reclassements.py`, `tests/test_chainage_grilles.py`.

Sources : index LEGI et JORF de la DILA (identifiants cités, lus pendant la session) ; Légifrance,
lu le 6 novembre 2026 par l'outil de lecture web : code civil, art. 1er (LEGIARTI000006419280) ;
pages au JORF des n° 2012-1139 (art. 68, 69), 2014-71 (art. 3, 8, 14, 15), 2015-363 (art. 11, 13,
14, 15), 2010-982 et 2010-989 (tables des matières), 2011-489 et 2006-8 (numéro du JO) ; Noyau
RH, `etat/textes.csv`, en recoupement.

*Corrigé le 6 novembre 2026 (B7-bis) : `2026-11-06-b7-bis-corrections-de-r-b8.md` (le n° 2007-835 : deux lectures ; les quatre « prend effet » et le n° 2012-1139 déclarés à l'en-tête de `tableaux.csv` ; le n° 2018-648 ; le paquet ne lit aucun fichier de reclassements ; l'article 1er du code civil non lu en direct).*
