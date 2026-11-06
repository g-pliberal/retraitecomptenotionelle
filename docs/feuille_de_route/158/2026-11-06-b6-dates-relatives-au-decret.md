# B6 : les dates d'effet relatives au décret, et les trois écarts de R-B6

Vague 11, B6, le 6 novembre 2026, sur Opus. Tout ce qui suit a été lu pendant la session :
l'index LEGI du dépôt (dump `Freemium_legi_global_20250713-140000`, à jour au 20261102-213929)
et l'index JORF (`Freemium_jorf_global_20250713-140000`, à jour au 20261103-002311), par des
requêtes directes sur la table `doc` (pour un texte du JORF, `date` y est le `DATE_PUBLI` du
JO, `scripts/fetch/dila_index.py`, `lire`) ; et, pour l'art. 1er du code civil, Légifrance,
lu par l'outil de lecture web (la page directe répond 403 au conteneur). Aucun fac-similé
n'est lu. Les deux index sont effacés en finissant.

## 1. Les trois écarts de R-B6

### 1 a. n° 98-896, art. 8 : la date du tableau est le 1er août 1996 (tranché) ; l'élargissement de 2002, non tranché

Les trois articles, ouverts aux deux bases :

- **n° 2002-378, art. 1er**, au JORF (`JORFARTI000002416455`, JO du 21 mars 2002,
  `JORFTEXT000000586605`) : « A l'article 8 du décret du 7 octobre 1998 susvisé, les mots :
  « en fonctions à la date du présent décret » sont supprimés. » Au LEGI, l'art. 1
  (`LEGIARTI000006209301`) n'est que « a modifié les dispositions suivantes ». L'art. 2
  (`JORFARTI000002195228` ; `LEGIARTI000006209302`) est l'exécution. Le décret n'a pas
  d'autre article : aucune clause d'entrée en vigueur ni d'effet.
- **n° 98-896, art. 10**, au JORF (`JORFARTI000002486581`, JO du 9 octobre 1998,
  `JORFTEXT000000573079`) : « Art. 10. - Les dispositions des articles 1er, 6, 7 et 8 du présent
  décret sont applicables à compter du 1er août 1996. » Au LEGI, `LEGIARTI000006508631`,
  seule version (depuis le 1998-10-09), mêmes mots.
- **n° 98-896, art. 8**, au JORF (`JORFARTI000002094938`) : « Art. 8. - Les lieutenants de port
  en fonctions à la date du présent décret sont reclassés conformément au tableau ci-après :
  […] Vous pouvez consulter le tableau dans le JO n° 234 du 09/10/1998 page 15305 à 15307 ».
  Au LEGI, deux versions : `LEGIARTI000006508628` (du 1996-08-01 au 2002-03-21), « Les
  lieutenants de port en fonctions à la date du présent décret sont reclassés conformément
  au tableau ci-après : », et `LEGIARTI000006508629` (depuis le 2002-03-21), « Les lieutenants
  de port sont reclassés conformément au tableau ci-après : ». Les deux tableaux, comparés
  ligne à ligne, sont les mêmes : classe fonctionnelle, 4e après 1 an → 5e (ancienneté
  acquise moins 1 an), 4e avant 1 an → 4e (plus 1 an), 3e → 4e (1/3), 2e après 1 an → 3e et
  2e avant 1 an → 2e (deux fois l'ancienneté acquise), 1er → 1er (acquise) ; classe normale,
  4e → 5e (acquise), 3e après 2 ans → 4e (moins 2 ans), 3e avant 2 ans → 3e (acquise),
  2e → 2e et 1er → 1er (2/3) ; stage → stage. Onze lignes de part et d'autre.

Tous les textes modificatifs, cherchés au titre (« 98-896 », « 2002-378 ») et au plein texte
(« 98-896 » ; « 7 octobre 1998 » et « officiers de port ») dans les deux index : seul le
n° 2002-378 modifie le n° 98-896 ; les autres textes trouvés le citent (n° 98-895, n° 2006-443,
n° 2012-1058, n° 2013-1146, arrêtés du 7 octobre 1998, du 22 décembre 2004, du 13 décembre
2005, du 31 octobre 2006 et du 17 avril 2008), sans que leur titre dise qu'ils le modifient ;
et l'art. 8 n'a au LEGI que ses deux versions, qu'un autre texte modificatif aurait
multipliées.

**Ce qui se tranche.** Le tableau de 2002 est celui de 1996 ; l'art. 10, en vigueur et non
modifié, rend l'art. 8 applicable « à compter du 1er août 1996 » ; le n° 2002-378 ne touche ni
le tableau ni l'art. 10. Le reclassement de la grille de 1996 à la suivante est daté du
1er août 1996 ; le 2002-03-21 n'est que le début de la version consolidée. La lecture
contraire (« le tableau ne vaut que depuis 2002 ») ferait du tableau de 1996 un tableau de 2002
que le décret de 2002 ne contient pas. `effet` = **1996-08-01**, par
`DATES_D_UN_AUTRE_ARTICLE`, avec la citation de l'art. 10.

**Ce qui ne se tranche pas.** Le n° 2002-378 élargit le champ : il ôte la condition d'être
« en fonctions à la date du présent décret ». Pour l'agent que cette condition excluait, deux
lectures : le 1er août 1996, si l'art. 10 vaut pour l'art. 8 dans sa rédaction de 2002 ; ou
l'entrée en vigueur du n° 2002-378 (JO du 21 mars 2002), par la règle générale de l'époque,
qui n'est pas lue (point 3) : ni sa date ni l'une des deux lectures ne s'écrivent donc ici.
La donnée ne porte que la date du tableau.

**Au fac-similé** (non lu, à ajouter à
`docs/feuille_de_route/138/2026-11-05-la-file-des-fac-similes.md`) : le tableau d'origine,
« JO n° 234 du 09/10/1998 page 15305 à 15307 ».

### 1 b. n° 2017-903, art. 12 : une version « jamais en vigueur »

Au LEGI, deux versions de l'art. 12 du n° 2017-903 (JO du 10 mai 2017, `JORFTEXT000034637501`) :
`LEGIARTI000034702202`, du **2018-02-01 au 2017-12-24** — son début est postérieur à sa fin :
elle n'a jamais été en vigueur —, « I. - Au 1er février 2018, les conseillers supérieurs
socio-éducatifs sont reclassés selon le tableau de correspondance ci-après » ; puis
`LEGIARTI000036440010`, depuis le 2017-12-24, « I. - Au 1er février 2019, […] ». La rédaction du
1er février 2018 a été remplacée avant de prendre effet : le reclassement qu'elle annonce n'a pas
eu lieu à cette date. Le texte qui a ouvert la version du 2017-12-24 n'est pas dans l'index
(recherche plein texte de « 2017-903 » au JORF de décembre 2017 : rien), et n'est pas nommé
ici. La note de B5-bis la présentait comme une version ordinaire (« du 2018-02-01 ») ; le
chaînage lui donne la date 2018-02-01. Sans conséquence aujourd'hui (versant territorial,
groupe déclaré, que rien ne consomme). *Candidat*, repris de R-B6 : avant tout rattachement
du versant territorial, ne pas lire comme un reclassement une version dont la fin précède le
début.

### 1 c. La garde des citations

`tests/test_reclassements.py::test_chaque_date_lue_a_la_main_est_citee_mot_pour_mot_dans_son_texte`,
qui passe quand l'index manque (la CI ne l'a pas). Pour `DATES_D_UN_AUTRE_ARTICLE` : la citation
est dans le texte de l'article d'effet au LEGI (espaces normalisés), cet article est du même
décret que le tableau, et la date est écrite dans la citation. Pour `ENTREES_EN_VIGUEUR`
(point 2) : de même, et le texte au JORF porte le jour de publication donné, la clause est
dans un article signé de ce JO, et la date se recalcule de la citation (écrite, ou « le
premier jour du mois » qui suit la publication) ; la phrase du tableau dit le mot de la
clause (« entrée en vigueur » / « entre en vigueur », « date d'effet » / « prend effet »).
Vu rouge (le module n'avait pas `ENTREES_EN_VIGUEUR`), puis vert ; et, pour voir qu'il mord,
une citation faussée pour l'essai (« au 1er août 1996 » pour le n° 98-268) l'a fait échouer
(« assert 'Les articles 17, 18, 21 et 22 du présent décret prennent effet au 1er août 1996.' in
'… au 1er août 1995. …' »), puis rétablie.

## 2. Les dates relatives au décret : 62 tableaux de 46 décrets datés

**Le relevé.** Des 361 tableaux sans `effet`, 131 (104 textes) disent une date relative au
décret : « entrée en vigueur » (110, dont 100 « date d'entrée en vigueur du présent décret »), « date d'effet du
présent décret » (12), « date de publication » (9). Pour chaque décret, l'article qui fixe son
entrée en vigueur a été cherché parmi tous ses articles au LEGI, puis relu au JORF.

**La règle suivie.** Le décret date lui-même son entrée en vigueur, d'une clause qui vaut
pour tout le décret ou n'excepte pas l'article du tableau, et dont le verbe répond à la
phrase du tableau : « entre(nt) en vigueur » pour « à la date d'entrée en vigueur du présent
décret », « prend effet » pour « à la date d'effet du présent décret ». La clause n'a qu'une
version au LEGI, et elle est mot pour mot dans le texte signé, au JORF. La date est celle
qu'elle écrit, ou, pour « le premier jour du mois suivant (celui de) sa publication », le 1er
du mois qui suit le jour du JO. Les phrases des 62 tableaux ont été relues : aucune ne porte
une autre date du reclassement (les autres dates qu'elles contiennent sont celles des textes
qu'elles citent). La règle générale d'entrée en vigueur ne sert à aucune de ces dates.

**Les dates.** `effet` reçoit 62 dates (`ENTREES_EN_VIGUEUR`, par décret : la date, l'article
qui la fixe, le texte au JORF, le jour de publication, les mots ; `DATES_DU_DECRET`, l'article
du tableau → son décret). Calcul posé pour chaque ligne ci-dessous ; par exemple n° 2012-379 :
JO du 21 mars 2012, « le premier jour du mois suivant sa publication » → 1er avril 2012, quand le
LEGI ouvre la version du tableau au 2012-03-22. Onze dates s'écartent du début de la version au
LEGI, que la donnée prenait jusqu'ici : n° 98-896 art. 8 (2002-03-21 → 1996-08-01), n° 2012-379
art. 16 (2012-03-22 → 2012-04-01), n° 2017-180 art. 20 (2017-02-16 → 2017-01-01), n° 2022-1200
art. 6, 8, 9 (2022-09-02 → 2022-09-01), n° 2023-709 art. 28 (2023-08-03 → 2023-09-01),
n° 2025-1002 art. 11 et n° 2025-1003 art. 7 (2025-10-31 → 2025-11-01), n° 2025-1327 art. 31
et 35 (2025-12-28 → 2026-01-01). Les autres confirment le début du LEGI, désormais prouvé.


**Le point non tranché : n° 2011-1140** (JO du 23 septembre 2011, `JORFTEXT000024580517`). Ses
deux tableaux (art. 21, `LEGIARTI000024581630` ; art. 22, `LEGIARTI000024581632`) s'ouvrent sur
« A la date d'entrée en vigueur du présent décret » ; sa seule clause, art. 35
(`LEGIARTI000024581626`, seule version ; `JORFARTI000024580614`), dit : « Le présent décret
prend effet à compter du 1er jour du mois qui suit sa publication. » Deux lectures : la date
que le décret fixe est le **1er octobre 2011** (premier jour du mois qui suit le 23 septembre),
et elle est son entrée en vigueur ; ou le décret, qui ne fixe pas son entrée en vigueur, entre
en vigueur « à défaut, le lendemain de [sa] publication » (code civil, art. 1er, ci-dessous),
le **24 septembre 2011**, et ne prend effet que le 1er octobre. `effet` reste vide (la donnée
garde le début du LEGI, 2011-10-01), et le test le garde.

**La règle générale, lue pour ce point.** Code civil, art. 1er, `LEGIARTI000006419280`,
« En vigueur depuis le 01 juin 2004 », « Modifié par Ordonnance n°2004-164 du 20 février 2004 -
art. 1 () JORF 21 février 2004 en vigueur le 1er juin 2004 » (Légifrance,
https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006419280, lu le 6 novembre
2026 par l'outil de lecture web) : « Les lois et, lorsqu'ils sont publiés au Journal officiel de
la République française, les actes administratifs entrent en vigueur à la date qu'ils fixent
ou, à défaut, le lendemain de leur publication. Toutefois, l'entrée en vigueur de celles de
leurs dispositions dont l'exécution nécessite des mesures d'application est reportée à la date
d'entrée en vigueur de ces mesures. »

Les 46 décrets, par ordre de numéro :

| Décret, JO (JORFTEXT, `DATE_PUBLI`) | Clause (LEGI, seule version ; JORF) | Calcul | Tableaux (LEGI, version) | `effet` |
|---|---|---|---|---|
| n° 98-809, JO du 12 septembre 1998 (`JORFTEXT000000194869`) | « Le présent décret prend effet au 1er août 1995, à l'exception des articles 3 et 4. » `LEGIARTI000006508229` ; `JORFARTI000001751771` | date écrite | art. 10, `LEGIARTI000006508227` (1995-08-01) | **1995-08-01** |
| n° 2011-964, JO du 18 août 2011 (`JORFTEXT000024476275`) | « Le présent décret entre en vigueur le premier jour du mois suivant sa publication. » `LEGIARTI000024477652` ; `JORFARTI000024476297` | premier jour du mois qui suit le 18 août 2011 | art. 21, `LEGIARTI000024477660` (2011-09-01)<br>art. 22, `LEGIARTI000024477662` (2011-09-01) | **2011-09-01** |
| n° 2011-1642, JO du 25 novembre 2011 (`JORFTEXT000024846671`) | « Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa publication. » `LEGIARTI000024847365` ; `JORFARTI000024846769` | premier jour du mois qui suit le 25 novembre 2011 | art. 18, `LEGIARTI000024847333` (2011-12-01)<br>art. 19, `LEGIARTI000024847335` (2011-12-01) | **2011-12-01** |
| n° 2011-1987, JO du 29 décembre 2011 (`JORFTEXT000025046328`) | « Les dispositions du présent décret entrent en vigueur le 1er janvier 2012. » `LEGIARTI000025072735` ; `JORFARTI000025046424` | date écrite | art. 24, `LEGIARTI000025072785` (2012-01-01) | **2012-01-01** |
| n° 2011-1988, JO du 29 décembre 2011 (`JORFTEXT000025046447`) | « Les dispositions du présent décret entrent en vigueur le 1er janvier 2012. » `LEGIARTI000025073321` ; `JORFARTI000025046536` | date écrite | art. 22, `LEGIARTI000025073303` (2012-01-01) | **2012-01-01** |
| n° 2012-230, JO du 18 février 2012 (`JORFTEXT000025376765`) | « Les dispositions du présent décret entrent en vigueur le 1er mars 2012. » `LEGIARTI000025378144` ; `JORFARTI000025376847` | date écrite | art. 19, `LEGIARTI000025378134` (2012-03-01) | **2012-03-01** |
| n° 2012-379, JO du 21 mars 2012 (`JORFTEXT000025545406`) | « Le présent décret entre en vigueur le premier jour du mois suivant sa publication au Journal officiel de la République française. » `LEGIARTI000025546343` ; `JORFARTI000025545480` | premier jour du mois qui suit le 21 mars 2012 | art. 16, `LEGIARTI000025546325` (2012-03-22) | **2012-04-01** |
| n° 2012-924, JO du 31 juillet 2012 (`JORFTEXT000026236871`) | « Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa publication. » `LEGIARTI000026237262` ; `JORFARTI000026236967` | premier jour du mois qui suit le 31 juillet 2012 | art. 19, `LEGIARTI000026237250` (2012-08-01) | **2012-08-01** |
| n° 2012-984, JO du 24 août 2012 (`JORFTEXT000026310499`) | « Le présent décret entre en vigueur le premier jour du mois suivant sa publication. » `LEGIARTI000026311285` ; `JORFARTI000026310560` | premier jour du mois qui suit le 24 août 2012 | art. 21, `LEGIARTI000026311271` (2012-09-01) | **2012-09-01** |
| n° 2012-1099, JO du 30 septembre 2012 (`JORFTEXT000026427069`) | « Le présent décret entre en vigueur le 1er octobre 2012. » `LEGIARTI000026428567` ; `JORFARTI000026427142` | date écrite | art. 16, `LEGIARTI000026428541` (2012-10-01) | **2012-10-01** |
| n° 2012-1161, JO du 19 octobre 2012 (`JORFTEXT000026507710`) | « Le présent décret entre en vigueur le premier jour du mois suivant celui de sa publication au Journal officiel de la République française. » `LEGIARTI000026508387` ; `JORFARTI000026507825` | premier jour du mois qui suit le 19 octobre 2012 | art. 35, `LEGIARTI000026508372` (2012-11-01) | **2012-11-01** |
| n° 2012-1419, JO du 20 décembre 2012 (`JORFTEXT000026796060`) | « Le présent décret entre en vigueur à compter du premier jour du mois qui suit sa publication. » `LEGIARTI000026797414` ; `JORFARTI000026796096` | premier jour du mois qui suit le 20 décembre 2012 | art. 6, `LEGIARTI000026797412` (2013-01-01) | **2013-01-01** |
| n° 2012-1420, JO du 20 décembre 2012 (`JORFTEXT000026796099`) | « Le présent décret entre en vigueur à compter du premier jour du mois qui suit sa publication. » `LEGIARTI000026796792` ; `JORFARTI000026796196` | premier jour du mois qui suit le 20 décembre 2012 | art. 26, `LEGIARTI000026796776` (2013-01-01) | **2013-01-01** |
| n° 2013-830, JO du 18 septembre 2013 (`JORFTEXT000027962189`) | « Les dispositions du présent décret entrent en vigueur le premier jour du mois suivant sa publication. » `LEGIARTI000027962726` ; `JORFARTI000027962267` | premier jour du mois qui suit le 18 septembre 2013 | art. 16, `LEGIARTI000027962708` (2013-10-01) | **2013-10-01** |
| n° 2014-75, JO du 31 janvier 2014 (`JORFTEXT000028539339`) | « Les dispositions du présent décret entrent en vigueur le premier jour du mois suivant sa publication. » `LEGIARTI000028540391` ; `JORFARTI000028539399` | premier jour du mois qui suit le 31 janvier 2014 | art. 6, `LEGIARTI000028540405` (2014-02-01)<br>art. 6 t2, `LEGIARTI000028540405` (2014-02-01) | **2014-02-01** |
| n° 2014-76, JO du 31 janvier 2014 (`JORFTEXT000028539402`) | « Le présent décret entre en vigueur le premier jour du mois suivant sa date de publication. » `LEGIARTI000028540771` ; `JORFARTI000028539451` | premier jour du mois qui suit le 31 janvier 2014 | art. 8, `LEGIARTI000028540761` (2014-02-01)<br>art. 9, `LEGIARTI000028540763` (2014-02-01)<br>art. 10, `LEGIARTI000028540765` (2014-02-01)<br>art. 11, `LEGIARTI000028540767` (2014-02-01) | **2014-02-01** |
| n° 2014-79, JO du 31 janvier 2014 (`JORFTEXT000028539499`) | « Les dispositions du présent décret entrent en vigueur le premier jour du mois suivant sa publication. » `LEGIARTI000028540862` ; `JORFARTI000028539534` | premier jour du mois qui suit le 31 janvier 2014 | art. 6, `LEGIARTI000028540858` (2014-02-01)<br>art. 6 t2, `LEGIARTI000028540858` (2014-02-01) | **2014-02-01** |
| n° 2014-81, JO du 31 janvier 2014 (`JORFTEXT000028539558`) | « Les dispositions du présent décret entrent en vigueur le premier jour du mois suivant sa date de publication. » `LEGIARTI000028541522` ; `JORFARTI000028539591` | premier jour du mois qui suit le 31 janvier 2014 | art. 6, `LEGIARTI000028541518` (2014-02-01) | **2014-02-01** |
| n° 2014-922, JO du 21 août 2014 (`JORFTEXT000029382044`) | « Le présent décret entre en vigueur le premier jour du mois qui suit sa publication. » `LEGIARTI000029384148` ; `JORFARTI000029382104` | premier jour du mois qui suit le 21 août 2014 | art. 16, `LEGIARTI000029384142` (2014-09-01) | **2014-09-01** |
| n° 2014-1164, JO du 11 octobre 2014 (`JORFTEXT000029562200`) | « Le présent décret entre en vigueur le premier jour du mois suivant sa publication au Journal officiel de la République française. » `LEGIARTI000029563614` ; `JORFARTI000029562245` | premier jour du mois qui suit le 11 octobre 2014 | art. 10, `LEGIARTI000029563606` (2014-11-01) | **2014-11-01** |
| n° 2015-303, JO du 19 mars 2015 (`JORFTEXT000030370469`) | « Le présent décret entre en vigueur le premier jour du mois qui suit sa publication. » `LEGIARTI000030371580` ; `JORFARTI000030370554` | premier jour du mois qui suit le 19 mars 2015 | art. 24, `LEGIARTI000030371569` (2015-04-01) | **2015-04-01** |
| n° 2015-1275, JO du 15 octobre 2015 (`JORFTEXT000031313295`) | « Le présent décret entre en vigueur le premier jour du mois suivant sa publication au Journal officiel de la République française. » `LEGIARTI000031317655` ; `JORFARTI000031313409` | premier jour du mois qui suit le 15 octobre 2015 | art. 35, `LEGIARTI000031317649` (2015-11-01) | **2015-11-01** |
| n° 2016-219, JO du 28 février 2016 (`JORFTEXT000032114422`) | « Le présent décret entre en vigueur le premier jour du mois suivant celui de sa publication. » `LEGIARTI000032128540` ; `JORFARTI000032114531` | premier jour du mois qui suit le 28 février 2016 | art. 6, `LEGIARTI000032128528` (2016-03-01)<br>art. 7, `LEGIARTI000032128530` (2016-03-01) | **2016-03-01** |
| n° 2016-336, JO du 22 mars 2016 (`JORFTEXT000032276187`) | « Le présent décret entre en vigueur à compter du premier jour du mois qui suit celui de sa publication. » `LEGIARTI000032276866` ; `JORFARTI000032276290` | premier jour du mois qui suit le 22 mars 2016 | art. 27, `LEGIARTI000032276852` (2016-04-01) | **2016-04-01** |
| n° 2016-2002, JO du 31 décembre 2016 (`JORFTEXT000033758808`) | « Le présent décret entre en vigueur le 1er janvier 2017. » `LEGIARTI000033792205` ; `JORFARTI000033758906` | date écrite | art. 23, `LEGIARTI000033792187` (2017-01-01) | **2017-01-01** |
| n° 2017-180, JO du 15 février 2017 (`JORFTEXT000034035533`) | « Le présent décret entre en vigueur le 1er janvier 2017. » `LEGIARTI000034036522` ; `JORFARTI000034035566` | date écrite | art. 20, `LEGIARTI000034036512` (2017-02-16) | **2017-01-01** |
| n° 2017-233, JO du 25 février 2017 (`JORFTEXT000034080592`) | « Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa publication. » `LEGIARTI000034082772` ; `JORFARTI000034080669` | premier jour du mois qui suit le 25 février 2017 | art. 17, `LEGIARTI000034082758` (2017-03-01) | **2017-03-01** |
| n° 2020-1174, JO du 27 septembre 2020 (`JORFTEXT000042365978`) | « Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa publication. » `LEGIARTI000042368622` ; `JORFARTI000042366068` | premier jour du mois qui suit le 27 septembre 2020 | art. 25, `LEGIARTI000042368604` (2020-10-01) | **2020-10-01** |
| n° 2020-1175, JO du 27 septembre 2020 (`JORFTEXT000042366071`) | « Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa publication. » `LEGIARTI000042368942` ; `JORFARTI000042366153` | premier jour du mois qui suit le 27 septembre 2020 | art. 25, `LEGIARTI000042368924` (2020-10-01) | **2020-10-01** |
| n° 2021-1818, JO du 28 décembre 2021 (`JORFTEXT000044571714`) | « Les dispositions du présent décret entrent en vigueur le 1er janvier 2022. » `LEGIARTI000044804898` ; `JORFARTI000044571768` | date écrite | art. 7, `LEGIARTI000044804888` (2022-01-01)<br>art. 8, `LEGIARTI000044804890` (2022-01-01)<br>art. 9, `LEGIARTI000044804892` (2022-01-01) | **2022-01-01** |
| n° 2021-1826, JO du 28 décembre 2021 (`JORFTEXT000044572291`) | « Les dispositions du présent décret entrent en vigueur le 1er janvier 2022. » `LEGIARTI000044799842` ; `JORFARTI000044572326` | date écrite | art. 6, `LEGIARTI000044799836` (2022-01-01) | **2022-01-01** |
| n° 2021-1834, JO du 28 décembre 2021 (`JORFTEXT000044572775`) | « Les dispositions du présent décret entrent en vigueur le 1er janvier 2022. » `LEGIARTI000044804034` ; `JORFARTI000044572802` | date écrite | art. 3, `LEGIARTI000044804028` (2022-01-01) | **2022-01-01** |
| n° 2022-516, JO du 10 avril 2022 (`JORFTEXT000045537923`) | « Les dispositions du présent décret entrent en vigueur le premier jour du mois suivant celui de sa publication. » `LEGIARTI000045540046` ; `JORFARTI000045537959` | premier jour du mois qui suit le 10 avril 2022 | art. 4, `LEGIARTI000045540040` (2022-05-01) | **2022-05-01** |
| n° 2022-1093, JO du 31 juillet 2022 (`JORFTEXT000046114822`) | « Le présent décret entre en vigueur le premier jour du mois suivant celui de sa publication. » `LEGIARTI000046121303` ; `JORFARTI000046114855` | premier jour du mois qui suit le 31 juillet 2022 | art. 9, `LEGIARTI000046121299` (2022-08-01) | **2022-08-01** |
| n° 2022-1200, JO du 1er septembre 2022 (`JORFTEXT000046242148`) | « Les dispositions du présent décret entrent en vigueur le 1er septembre 2022. » `LEGIARTI000046243434` ; `JORFARTI000046242219` | date écrite | art. 6, `LEGIARTI000046243448` (2022-09-02)<br>art. 8, `LEGIARTI000046243452` (2022-09-02)<br>art. 9, `LEGIARTI000046243454` (2022-09-02) | **2022-09-01** |
| n° 2022-1206, JO du 1er septembre 2022 (`JORFTEXT000046242594`) | « Les dispositions du présent décret entrent en vigueur le 1er septembre 2022. » `LEGIARTI000046243814` ; `JORFARTI000046242660` | date écrite | art. 4, `LEGIARTI000046243822` (2022-09-01)<br>art. 5, `LEGIARTI000046243824` (2022-09-01)<br>art. 6, `LEGIARTI000046243826` (2022-09-01) | **2022-09-01** |
| n° 2022-1209, JO du 1er septembre 2022 (`JORFTEXT000046242908`) | « Le présent décret entre en vigueur le 1er septembre 2022. » `LEGIARTI000046243977` ; `JORFARTI000046242928` | date écrite | art. 2, `LEGIARTI000046243983` (2022-09-01) | **2022-09-01** |
| n° 2023-527, JO du 30 juin 2023 (`JORFTEXT000047752873`) | « Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa publication. » `LEGIARTI000047766737` ; `JORFARTI000047752923` | premier jour du mois qui suit le 30 juin 2023 | art. 10, `LEGIARTI000047766733` (2023-07-01) | **2023-07-01** |
| n° 2023-709, JO du 2 août 2023 (`JORFTEXT000047915341`) | « Les dispositions du présent décret entrent en vigueur le 1er septembre 2023 à l'exception de celles de l'article 11 qui s'appliquent aux procédures engagées à compter du 1er janvier 2024. » `LEGIARTI000047917296` ; `JORFARTI000047915465` | date écrite | art. 28, `LEGIARTI000047917292` (2023-08-03) | **2023-09-01** |
| n° 2023-1092, JO du 26 novembre 2023 (`JORFTEXT000048460347`) | « Le présent décret entre en vigueur le premier jour du mois suivant celui de sa publication. » `LEGIARTI000048461730` ; `JORFARTI000048460366` | premier jour du mois qui suit le 26 novembre 2023 | art. 3, `LEGIARTI000048461728` (2023-12-01) | **2023-12-01** |
| n° 2023-1336, JO du 30 décembre 2023 (`JORFTEXT000048728435`) | « Le présent décret entre en vigueur le premier jour du mois suivant celui de sa publication. » `LEGIARTI000048842648` ; `JORFARTI000048728472` | premier jour du mois qui suit le 30 décembre 2023 | art. 9, `LEGIARTI000048842644` (2024-01-01) | **2024-01-01** |
| n° 2024-51, JO du 31 janvier 2024 (`JORFTEXT000049060184`) | « Le présent décret entre en vigueur le premier jour du mois suivant celui de sa publication. » `LEGIARTI000049063869` ; `JORFARTI000049060232` | premier jour du mois qui suit le 31 janvier 2024 | art. 27, `LEGIARTI000049063861` (2024-02-01)<br>art. 18, `LEGIARTI000049063907` (2024-02-01) | **2024-02-01** |
| n° 2024-282, JO du 30 mars 2024 (`JORFTEXT000049343100`) | « Le présent décret entre en vigueur le premier jour du mois suivant celui de sa publication. » `LEGIARTI000049350387` ; `JORFARTI000049343136` | premier jour du mois qui suit le 30 mars 2024 | art. 9, `LEGIARTI000049350385` (2024-04-01) | **2024-04-01** |
| n° 2025-1002, JO du 30 octobre 2025 (`JORFTEXT000052456736`) | « Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa publication. » `LEGIARTI000052461403` ; `JORFARTI000052456771` | premier jour du mois qui suit le 30 octobre 2025 | art. 11, `LEGIARTI000052461401` (2025-10-31) | **2025-11-01** |
| n° 2025-1003, JO du 30 octobre 2025 (`JORFTEXT000052456773`) | « Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa publication. » `LEGIARTI000052461514` ; `JORFARTI000052456794` | premier jour du mois qui suit le 30 octobre 2025 | art. 7, `LEGIARTI000052461512` (2025-10-31) | **2025-11-01** |
| n° 2025-1327, JO du 27 décembre 2025 (`JORFTEXT000053174358`) | « Le présent décret entre en vigueur le 1 er janvier 2026. » `LEGIARTI000053186037` ; `JORFARTI000053174545` | date écrite | art. 31, `LEGIARTI000053185999` (2025-12-28)<br>art. 35, `LEGIARTI000053186007` (2025-12-28) | **2026-01-01** |

## 3. Ce qui manque : la règle d'avant le 1er juin 2004

Pour un décret publié avant le 1er juin 2004 sans clause d'entrée en vigueur, la règle est
celle d'avant l'ordonnance n° 2004-164 : ni l'art. 1er du code civil dans cette version, ni le
texte auquel il renverrait (non nommé ici : il n'a pas été ouvert) ne sont dans les index
filtrés du dépôt ; Légifrance refuse la page directe au conteneur
(403), et l'outil de lecture web n'a pu lire que la version en vigueur (la page de l'ordonnance
répond 403, le lien « Versions » n'a pas d'adresse lisible). **Question au propriétaire** : par
quelle source lire, à leur version d'époque, l'art. 1er du code civil d'avant 2004 et le texte
qui fixait alors l'entrée en vigueur des décrets ? Sans elle, aucun décret d'avant juin 2004
sans clause ne se date, et les deux lectures d'un jour franc ou d'une date d'arrivée du JO ne
s'écrivent pas.

## 4. Où je m'arrête

Restent 67 tableaux de 57 textes, à lire décret par décret : n° 71-917, 72-774, 75-687 (2
tableaux), 84-145, 84-196, 84-965, 86-229, 87-1107, 88-547, 90-126, 90-393, 90-404, 90-405 (2),
92-859, 92-861, 92-863, 92-871, 93-278, 98-203, 2000-508, 2001-128, 2003-466, 2004-1439,
2005-939, 2005-1132 (3), 2005-1304, 2006-8 (2), 2007-835, 2010-302, 2010-647, 2010-982,
2010-989, 2010-1719, 2010-1720, 2011-215, 2011-489, 2011-744 (2), 2011-1139 (2), 2012-78 (2),
2012-229, 2012-761, 2012-762, 2012-1002, 2012-1139, 2013-176, 2013-489, 2013-875, 2013-974,
2013-1173, 2014-71 (2), 2015-363 (2), 2015-1792, 2016-1177, 2016-2008, 2018-648, 2019-1160, et
l'arrêté du 21 décembre 1982. Ce que le relevé en dit, pour qui reprend :

- Sans clause globale trouvée (« Le présent décret entre en vigueur… ») : la plupart. Après le
  1er juin 2004, la règle lue au point 2 s'applique (« le lendemain de leur publication ») si
  aucun article ne fixe de date ; mais le LEGI ouvre certaines versions au 1er du mois
  (n° 2012-1002, au 2012-09-01, publié le 30 août), signe qu'une clause d'une autre forme existe
  peut-être : chaque décret se relit en entier, au JORF. Avant juin 2004 : point 3.
- Une date relative à un **autre** décret (« à la date d'entrée en vigueur du décret
  n° 2000-484 », n° 71-917 ; « du décret n° 2006-1694 », n° 88-547 ; « du décret n° 2003-1024 »,
  n° 90-126 ; « du décret n° 2023-676 », n° 2004-1439 ; « du décret portant inscription… »,
  n° 2010-302) : la clause de ce décret-là.
- Des clauses à exceptions ou par parties : n° 2016-2008 (« Sous réserve des dispositions de
  l'article 12, le présent décret entre en vigueur le 1er janvier 2017 » ; son art. 12 fixe le
  nombre et la durée des échelons « A compter du 1er janvier 2020 », que le tableau de l'art. 21
  peut viser) ; n° 2018-648 (« entrent en vigueur le 1er janvier 2017, à l'exception de celles
  des articles 1er, 5 et 6 », publié le 25 juillet 2018 : laquelle des deux dates est
  « la date d'entrée en vigueur du présent décret » ?) ; n° 2010-989 (par chapitres, « Pas
  maintenant ») ; n° 2011-215 (« prennent effet », quand le tableau dit « entrée en vigueur » :
  le même point que le n° 2011-1140).
- « à la date de publication du présent décret » (n° 2005-1304, 2006-8) : le jour du JO, à
  lire au JORF.

## 5. Candidats (non corrigés)

- **n° 2023-1336, trois rattachements neufs à la même grille.** Daté du 1er janvier 2024
  (JO du 30 décembre 2023), le tableau de l'art. 9 (`LEGIARTI000048842644`) passe le chaînage :
  ses trois groupes sont rattachés (corps 00220), avec, pour chacun, la même grille la veille
  et le jour (04188 sur 03781 ; 00533 sur 00541 ; 00534 sur 00542). Au Noyau RH, le grade 04188
  est sur la grille 03781 depuis le 2022-07-20, sans fin (`etat/grades.csv`) : le Noyau RH ne
  change pas de grille au 1er janvier 2024. Les seize rattachements déjà relus changent tous de
  grille. Je n'ai pas touché au chaînage : à juger par R-B7 (un rattachement dont la grille
  d'origine est celle d'accueil prouve-t-il le passage d'une grille à la suivante ?).
- **n° 2015-1275, art. 35** : un rectificatif au JORF (`JORFARTI000031360111`, JO du 24 octobre
  2015) : « Rectificatif au Journal officiel n° 239 du 15 octobre 2015, édition électronique,
  texte n° 14 : Au I de l'article 35, rétablir le tableau comme suit : […] ». Sa date ne bouge
  pas ; que `lignes.csv` suive le tableau rétabli reste à vérifier.
- **Au fac-similé** : le tableau du n° 98-809, art. 10 (« Vous pouvez consulter le tableau dans
  le JO n° 211 du 12/09/1998 ») et celui du n° 98-896, art. 8 (point 1 a).

## 6. Ce qui bouge

- `scripts/fetch/dila_legi_reclassements.py` : l'entrée du n° 98-896 dans
  `DATES_D_UN_AUTRE_ARTICLE` ; `ENTREES_EN_VIGUEUR` (46 décrets) et `DATES_DU_DECRET` (60
  articles, 62 tableaux) ; `effet_du_tableau` les lit ; l'en-tête de `tableaux.csv` le dit.
- `data/reference/grilles/reclassements/tableaux.csv` : la colonne `effet` refaite par
  `effet_du_tableau` sur la phrase stockée (le lecteur n'est pas relancé, voir le candidat de
  B5) : 63 cases vides prennent leur date, les 387 autres se refont à l'identique ; aucune
  autre colonne ne change.
- `data/reference/grilles/chainage/reclassements.csv`, le chaînage relancé : 128 lignes
  prennent `date` et `date_lue` effet ; six groupes rattachés de plus (n° 2012-984, art. 21,
  trois groupes, au 2012-09-01 ; n° 2023-1336, art. 9, trois groupes, voir les candidats) :
  19 rattachés, 843 déclarés. Les tableaux déclarés faute de date passent de 155 à 126 : les
  29 qui sortent sont tous datés ici (`test_aucune_phrase_restee_sans_date_ne_s_ouvre_sur_une_date`).
- `moteur/donnees.json` : reconstruit, inchangé (le paquet ne lit pas les reclassements).
- Tests, vus rouges puis verts : `test_un_tableau_que_date_un_autre_article_de_son_decret_prend_cette_date`
  (le n° 98-896 daté), `test_un_tableau_date_de_l_entree_en_vigueur_de_son_decret_prend_la_date_qu_il_fixe`
  (les 62 dates, écrites à la main dans le test avec leur clause ; le n° 2011-1140 vide),
  `test_chaque_date_lue_a_la_main_est_citee_mot_pour_mot_dans_son_texte` (point 1 c).
- Lancés : `tests/test_reclassements.py`, `tests/test_chainage_grilles.py`, `tests/test_dila_index.py`
  et `tests/test_donnees.py` en entier, 303 passés (l'index présent, la garde jouée) ;
  `python -m pytest -m rapide`, 4 499 passés, 6 ignorés, 11 rouges, tous
  `tests/test_pages_en_dossier.py` (pages que GitHub refait) ; `PRESOMPTIONS_DECALEES=1 python
  -m pytest -m rapide`, 4 294 passés, 211 ignorés, les mêmes 11 ; aucun âge ni aucune durée ne
  change (`test_regle_de_chacun.py` non concerné).
