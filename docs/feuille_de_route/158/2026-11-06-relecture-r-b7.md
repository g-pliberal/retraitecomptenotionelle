# Relecture de B6 : les dates d'effet relatives au décret, la règle d'avant juin 2004

Vague 11, R-B7, le 6 novembre 2026, sur Sonnet. Relecture indépendante du commit 94f30a5 (B6,
note `2026-11-06-b6-dates-relatives-au-decret.md`). Tout ce qui suit a été rouvert pendant la
session, sans reprendre ni la note de B6 ni la mémoire : l'index LEGI (dump
`Freemium_legi_global_20250713-140000`, incrément 20261102-213929) et l'index JORF
(`Freemium_jorf_global_20250713-140000`, incrément 20261103-002311), par `dila_cherche.py`
(`--texte`, `--motif`) et par des lectures directes de la table `doc` ; en recoupement, le Noyau RH
du dépôt (`data/reference/grilles/etat/` : `textes.csv`, `grades.csv`, `echelons.csv`). Les dates
ont été refaites par un calcul écrit ici, non par celui de B6. Aucun fac-similé n'est lu. Les deux
index sont effacés en finissant. Aucune règle, aucune donnée, aucun test n'est touché.

**Verdict : aucune date fausse. Les 62 dates, celle du n° 98-896 art. 8 et les six
rattachements du chaînage tiennent au texte, et les onze qui s'écartent du LEGI sont celles de
B6, pas celles du LEGI.** Six écarts, aucun grave : une citation tronquée que la garde ne voit
pas (n° 2021-1818, moyen pour la preuve écrite, sans effet sur la date) ; le n° 2011-1140, que
trois sources de l'index tranchent (faible) ; la preuve des trois rattachements du n° 2023-1336
(faible) ; trois dates antérieures à la publication, non dites (faible) ; la file des
fac-similés non complétée (faible) ; l'élargissement de 2002 absent de la donnée (faible).
La règle d'avant juin 2004 n'est pas dans l'index, mais le texte qui la porte est nommé (§ 7).

## 1. Les citations et les 62 dates : conformes, sauf une citation tronquée

Pour chacun des 46 décrets de `ENTREES_EN_VIGUEUR`, ouvert par son identifiant :

- l'article de la clause, au LEGI : du bon décret (titre « Décret n° … du … »), **une seule
  version**, et sa citation identique mot pour mot (espaces normalisés) pour **45 sur 46** ;
- le texte au JORF : de même titre, `date` égale au jour de publication de B6 (46 sur 46), la
  clause dans un de ses articles (46 sur 46), identique à l'article pour 44 : le n° 98-809 porte
  « Art. 12. - » devant, le n° 2021-1818 est tronqué (écart 1) ;
- la date, recalculée de la citation et du jour du JO (écrite, ou 1er du mois qui suit) : égale à
  celle de B6 pour les 46 ;
- les 62 tableaux : leur article est du même décret, leur `effet` au CSV est celui du décret
  (63 cases en comptant le n° 98-896, toutes vides avant) ; leur phrase dit « entrée en vigueur »
  quand la clause dit « entre(nt) en vigueur », « date d'effet » quand elle dit « prend effet »
  (n° 98-809 : art. 10 et art. 12, lus) ; aucune phrase ne dit « date de publication ».
- aucune clause d'effet contraire : les autres articles de chacun des 46 décrets, toutes versions
  du LEGI, cherchés pour « entre(nt) en vigueur », « prend effet », « produit effet »,
  « rétroactiv », « titre transitoire » : rien qui touche le tableau (les seules occurrences sont
  des notes de décrets postérieurs et, dans le n° 2012-924, art. 26, « prend effet à la date
  d'entrée en vigueur du présent décret » : la même date). Aucun rectificatif du JORF, cherché
  par « rectificatif » et le numéro de chacun des 46 décrets, au titre et au texte, ne touche
  une clause (celui du n° 2015-1275, art. 35, JORFARTI000031360111, JO du 24 octobre 2015,
  rétablit le tableau, non la date). Limite : l'index est filtré par thème ; un rectificatif hors
  champ pourrait y manquer.

Recoupements indépendants de la clause : la **notice** du texte au JORF (« Entrée en vigueur : … »)
dit la même chose pour **43 des 46** (la date écrite, ou « premier jour du mois suivant » ; les
trois autres, n° 98-809, 2020-1174 et 2020-1175, n'en portent pas) ; le **Noyau RH**
(`textes.csv`) porte le décret pour **25 des 46**, avec un `effet` égal à la date de B6 et une
`publication` égale au JO, **25 sur 25**.

**Écart 1 (moyen pour la preuve, aucune date fausse) : citation tronquée, n° 2021-1818.** La
clause (art. 12, `LEGIARTI000044804898` ; `JORFARTI000044571768`) est : « Les dispositions du
présent décret entrent en vigueur le 1er janvier 2022. **Elles ne s'appliquent pas aux auxiliaires
de puériculture relevant, au 31 décembre 2021, du cadre d'emplois régi par le décret n° 92-865 du
28 août 1992 susvisé ni aux auxiliaires de soins relevant, à la même date, de la spécialité
aide-soignant du cadre d'emplois régi par le décret n° 92-866 du 28 août 1992 susvisé.** » B6 (le
code, le test et sa note) n'en cite que la première phrase. L'exception vise des personnes, non
des articles, et les tableaux des art. 7, 8 et 9 gardent le 1er janvier 2022 pour les agents
qu'ils reclassent : la date est juste. Mais la citation n'est pas « mot pour mot » l'article, et
la garde (`_plat(citation) in texte`, `tests/test_reclassements.py:710`) laisse passer une
citation tronquée dès qu'elle garde la date : essai en mémoire, la citation du n° 2025-1327
réduite à « Le présent décret entre en vigueur » échoue (la date n'y est plus), celle du
n° 2021-1818 telle quelle passe. À corriger : citer l'article entier, et faire dire à la garde
que la citation est l'article (ou son début, suivi de ce qu'on déclare omis). Preuve : les deux
textes ci-dessus.

## 2. Les onze dates qui s'écartent du LEGI : B6 tient, le LEGI ne tient pas

Les onze sont bien celles de la note : des 63 tableaux que B6 date, onze ont un `effet` différent
du début de version (`debut`) du LEGI ; des 67 que le décret ou un autre article date, quinze, les
quatre autres étant ceux de B5-bis (n° 98-268, 2001-325, 2017-1367, 2017-1494), déjà relus. Pour
chacune, quelle date tient au texte :

| Décret, articles | LEGI (`debut`) | B6 | La clause (JO) | Notice JORF | Noyau RH `effet` |
|---|---|---|---|---|---|
| n° 98-896, art. 8 | 2002-03-21 | 1996-08-01 | art. 10, « applicables à compter du 1er août 1996 » (JO du 9 octobre 1998) | aucune (texte de 1998) | absent |
| n° 2012-379, art. 16 | 2012-03-22 | 2012-04-01 | art. 25, « premier jour du mois suivant sa publication » (JO du 21 mars 2012) | « le 1er avril 2012 » | 2012-04-01 |
| n° 2017-180, art. 20 | 2017-02-16 | 2017-01-01 | art. 25, « le 1er janvier 2017 » (JO du 15 février 2017) | « applicable au 1er janvier 2017 » | 2017-01-01 |
| n° 2022-1200, art. 6, 8, 9 | 2022-09-02 | 2022-09-01 | art. 17, « le 1er septembre 2022 » (JO du 1er septembre 2022) | « le 1er septembre 2022 » | absent (territorial) |
| n° 2023-709, art. 28 | 2023-08-03 | 2023-09-01 | art. 30, « le 1er septembre 2023 à l'exception de celles de l'article 11 » (JO du 2 août 2023) | « le 1er septembre 2023 à l'exception de l'article 11 » | 2023-09-01 |
| n° 2025-1002, art. 11 | 2025-10-31 | 2025-11-01 | art. 12, « premier jour du mois qui suit celui de sa publication » (JO du 30 octobre 2025) | « premier jour du mois suivant » | 2025-11-01 |
| n° 2025-1003, art. 7 | 2025-10-31 | 2025-11-01 | art. 8, id. (JO du 30 octobre 2025) | id. | 2025-11-01 |
| n° 2025-1327, art. 31, 35 | 2025-12-28 | 2026-01-01 | art. 50, « le 1 er janvier 2026 » (JO du 27 décembre 2025) | « le 1 er janvier 2026 » | 2026-01-01 |

**Pourquoi la date de B6.** Pour les sept décrets autres que le n° 98-896 (dix articles), le début
de version du LEGI est le lendemain du jour du JO : le LEGI applique la règle « à défaut de date,
le lendemain de la publication » sans lire la date que le décret fixe. La preuve que ce début
n'est pas la date du décret : le n° 2022-1200 (LEGI 2022-09-02) et le n° 2022-1206 (LEGI
2022-09-01) sont du même JO du 1er septembre 2022 et portent la même clause, mot pour mot (« Les
dispositions du présent décret entrent en vigueur le 1er septembre 2022. ») ; le LEGI les date
différemment, et le LEGI date le n° 2022-1209, de ce JO aussi, au 2022-09-01. La règle
« la date qu'ils fixent, à défaut le lendemain de leur publication » n'est pas dans l'index sous
l'art. 1er du code civil, mais elle y est, à l'adaptation du lieu près, pour les collectivités
d'outre-mer :
loi organique n° 2007-223 du 21 février 2007, art. LO 6113-2 (Mayotte,
`JORFARTI000001883716`), LO 6213-2 (Saint-Barthélemy, `JORFARTI000002473942`), LO 6313-2
(Saint-Martin, `JORFARTI000001304282`), LO 6413-2 (Saint-Pierre-et-Miquelon,
`JORFARTI000001139543`) : « Les lois et, lorsqu'ils sont publiés au Journal officiel de la
République française, les actes administratifs entrent en vigueur à [la collectivité] à la date
qu'ils fixent ou, à défaut, le lendemain de leur publication. Toutefois, l'entrée en vigueur de
celles de leurs dispositions dont l'exécution nécessite des mesures d'application est reportée à
la date d'entrée en vigueur de ces mesures. » C'est la rédaction que B6 lit à l'art. 1er du code
civil (`LEGIARTI000006419280`, lu sur Légifrance par l'outil web, non revérifié ici) ; l'avis du
Conseil d'État publié au JO du 18 décembre 2009 (`JORFTEXT000021491765`) cite l'art. 1er, al. 1,
avec des points de suspension. Ce sont des recoupements, non l'art. 1er lui-même. Le n° 98-896
est un autre cas (voir § 3).

**Le n° 2017-180, une date antérieure à la publication** (le texte du 15 février 2017 entre en
vigueur « le 1er janvier 2017 ») : c'est la clause, la notice et le Noyau RH qui le disent ; la
date est celle du texte. Voir l'écart 4.

## 3. Les trois écarts de R-B6

**n° 98-896, art. 8 : conforme.** Ouverts : JORF `JORFARTI000002486581` (« Art. 10. - Les
dispositions des articles 1er, 6, 7 et 8 du présent décret sont applicables à compter du 1er août
1996. »), LEGI `LEGIARTI000006508631` (une version, depuis 1998-10-09, mêmes mots) ; art. 8,
`LEGIARTI000006508628` (1996-08-01 → 2002-03-21, avec « en fonctions à la date du présent
décret ») et `LEGIARTI000006508629` (depuis 2002-03-21, sans) ; n° 2002-378, `JORFARTI000002416455` :
« A l'article 8 du décret du 7 octobre 1998 susvisé, les mots : « en fonctions à la date du présent
décret » sont supprimés. », et le décret n'a que ces deux articles (LEGI : art. 1
`LEGIARTI000006209301`, art. 2 `LEGIARTI000006209302`). Les deux tableaux, relus ligne à ligne : les
mêmes onze lignes. Le LEGI lui-même ouvre la première version de l'art. 8 au 1996-08-01 (l'art. 10).
Un seul tableau est dans `tableaux.csv` (la version de 2002) ; le premier est en colonnes ASCII
que le lecteur ne lit pas, sans effet ; ses deux groupes au chaînage sont « déclarés ».

**n° 2017-903, art. 12 : conforme.** `LEGIARTI000034702202` : `date` 2018-02-01, `fin`
2017-12-24, texte « I. - Au 1er février 2018, … » ; `LEGIARTI000036440010` : depuis 2017-12-24,
« I. - Au 1er février 2019, … ». La première n'a jamais été en vigueur. Le texte qui a ouvert la
seconde n'est pas dans l'index : recherche plein texte « 2017 903 » avec « socio » et
« 1er février 2019 », LEGI et JORF, décembre 2017 à janvier 2018 : seul le LEGI rend l'art. 12 et
l'art. 13 (`LEGIARTI000036440008`, depuis le 2017-12-24 : « Les dispositions du chapitre Ier et de
l'article 12 entrent en vigueur le 1er février 2019. »), rien au JORF. B6 ne cite pas cet art. 13,
qui porte la date de 2019 pour l'art. 12 comme pour le chapitre Ier.

**La garde des citations : elle mord, sauf sur une troncature.** Rejouée en mémoire sur la
fonction de test, sans toucher au dépôt : le témoin inchangé passe ; **douze falsifications
échouent** : date du n° 2012-379 mise au 2012-03-22 ou au 2012-05-01, date écrite du n° 2011-1987
changée, citation du n° 2022-1200 changée (« octobre »), citation du n° 2023-1336 changée
(« précédant »), son jour de JO changé, son article de clause pris à un autre décret, citation du
n° 2025-1327 raccourcie sans la date, tableau rattaché à un autre décret, date du n° 98-268 mise
à 1996, date du n° 98-896 mise à 2002-03-21, citation de son art. 10 faussée (1997) ; **passe : le
n° 2021-1818 tel que B6 le cite, première phrase seule** (écart 1).

## 4. Le code et les tests

`python -m pytest tests/test_reclassements.py tests/test_chainage_grilles.py` : 76 passés (l'index
présent ; les trois tests de B6, dont la garde, passent et ne sont pas ignorés).
`python -m pytest -m rapide` : **4 499 passés, 6 ignorés, 11 rouges** ; sous
`PRESOMPTIONS_DECALEES=1` : **4 294 passés, 211 ignorés, 11 rouges**. Les 11 rouges sont les mêmes
dans les deux cas, tous de `tests/test_pages_en_dossier.py` (dix `test_une_page_toute_faite_est_a_jour`
et `test_le_corps_d_une_page_toute_faite_est_son_rendu`) : pages que GitHub refait, du nombre
même que B6 donne. Les comptes de B6 tiennent : tableaux sans `effet` 361 avant, 298 après
(63 datés) ; chaînage 13 → 19 rattachés, tableaux déclarés faute de date 155 → 126, 128 lignes
qui prennent `date` et `date_lue` à `effet`, six statuts de `declare` à `rattache`, les
colonnes `date`, `date_lue`, `raison`, `statut`, `corps`, `grade_*`, `grille_*`, `preuve` seules
changées ; au CSV des tableaux, une seule colonne change (`effet`), toujours de vide à une date.

## 5. Ce que le texte ne tranche pas

**L'élargissement de 2002 : déclaré dans la note, bien tenu.** Deux lectures pour l'agent que la
condition « en fonctions à la date du présent décret » excluait ; ni l'une ni l'autre n'est écrite.
Rien dans la donnée : `effet` de la version de 2002 est le 1996-08-01, son `debut` le 2002-03-21.
**Écart 6 (faible)** : la nuance n'est que dans la note ; à porter, si la donnée la sert un jour,
au CSV ou à son en-tête.

**n° 2011-1140 : déclaré, mais l'index le tranche. Écart 2 (faible), aucune donnée fausse
(`effet` reste vide).** L'art. 35 (`JORFARTI000024580614` ; `LEGIARTI000024581626`, une version)
dit « Le présent décret prend effet à compter du 1er jour du mois qui suit sa publication », le
JO du 23 septembre 2011 : **1er octobre 2011**. Le texte au JORF (`JORFTEXT000024580517`) a pour
notice « Entrée en vigueur : le 1er octobre 2011 » ; le Noyau RH (`textes.csv`, texte 926) porte
`effet` 2011-10-01 et `publication` 2011-09-23 ; les versions des tableaux (art. 21 et 22) s'ouvrent
au LEGI le 2011-10-01. Aucune source de l'index ne donne le 24 septembre, que la seconde lecture
supposerait. La clause fixe une date : elle vaut par la règle du § 2. Le dater est
raisonnable ; le laisser vide est prudent. À décider par la session qui reprend ces tableaux.
Même enseignement pour le n° 2011-215 (« prennent effet »), à rouvrir avec la notice du JORF ;
**attention** : le texte 5896 de `textes.csv` donne pour le n° 2011-215 (« du 25 février 2011 »)
`date` 2018-02-25 et `effet` 2018-03-01, incohérent avec son titre : ne pas s'en servir sans le JORF.

## 6. Les six groupes du chaînage : justes

**n° 2012-984, art. 21 (trois groupes, 2012-09-01) : juste.** Le tableau (`LEGIARTI000026311271`) :
technicien supérieur en chef de l'industrie et des mines → technicien supérieur en chef de
l'économie et de l'industrie ; principal (industrie et mines) → en chef (économie et industrie) ;
technicien supérieur → principal (économie et industrie). Au Noyau RH, `grades.csv` : 00675 (02694),
00676 (02695) et 02547 (02693) finissent le 2012-08-31, avec 03076 et 03075 pour suivants ; 03076
(01926) et 03075 (01925) commencent le 2012-09-01, corps 01112. La date 2012-09-01 est celle du
texte (JO du 24 août 2012), du LEGI et du Noyau RH.

**n° 2023-1336, art. 9 (trois groupes, 2024-01-01) : un rattachement juste, pas un leurre.** Le
tableau (`LEGIARTI000048842644`, « reclassés à la date d'entrée en vigueur du présent décret »)
reclasse chaque grade dans le même grade en renumérotant les échelons (hors classe : 7e → 6e, 6e →
5e, 5e → 4e, 4e → 4e sans ancienneté, …). Au Noyau RH, `grades.csv` garde 04188 (03781), 00533
(00541), 00534 (00542), mais `echelons.csv` change les trois grilles **à cette date**, 2024-01-01 :
03781, nouvelles versions d'échelon 5 (BB), 6 (C), 7 (D) ; 00541, indices 820, 862, 912, 977, 1027 puis
A et B, au lieu de 767, 826, 876, 927, 977, 1027 puis A ; 00542, indices 410, 456, 542, 600, 660, …
au lieu de 399, 445, 522, 563, 611, … ; et dans la hors classe l'ancien 5e échelon (977) devient le
4e (977) et l'ancien 6e (1027) le 5e (1027), comme le tableau le dit (5e → 4e, 6e → 5e). L'identifiant
de grille ne change pas ; son contenu, si.
Le rattachement ne prouve donc pas « le passage d'une grille à la suivante », mais le passage
d'une version des échelons à la suivante dans la même grille, daté du bon jour. Le chaînage le
vérifie déjà : les rangs du tableau sont cherchés dans la grille d'origine à la veille et dans
celle d'accueil au jour (`natures_noyau_au(grille, jour)`).
**Écart 3 (faible)** : la colonne `preuve` de ces trois lignes (« grade 04188 (03781) le
2023-12-31, 04188 (03781) le 2024-01-01 ») ne montre que deux identifiants égaux ; elle ne montre
pas que les échelons de la grille changent le 2024-01-01. À compléter si ces lignes doivent se
défendre telles quelles. Avant B6, aucun des 13 rattachés n'avait la même grille des deux côtés ;
après, 3 sur 19.

## 7. La règle d'avant le 1er juin 2004 : nommée, non lue

**Trouvé dans l'index (nom et formule d'application, non le texte de la règle).** Les décrets
« relatifs à l'entrée en vigueur de décrets » prennent pour visa : « Vu le décret du 5 novembre
1870 relatif à la promulgation des lois et décrets, notamment le deuxième alinéa de son article 2 »
et écrivent : « Application de l'article 2 (al. 2) du décret du 5 novembre 1870. Entrent en
vigueur immédiatement à compter de leur publication au Journal officiel de la République
française les dispositions : … ». Ouverts : n° 98-1212 du 29 décembre 1998
(`JORFTEXT000000209444`), n° 2001-1369 du 31 décembre 2001 (`JORFTEXT000000774679`), n° 2002-1613
du 31 décembre 2002 (`JORFTEXT000000234129`), n° 2003-1313 du 30 décembre 2003
(`JORFTEXT000000429658`) ; et, hors de cette série, n° 94-910 du 21 octobre 1994
(`JORFTEXT000000347846`, « ENTREE EN VIGUEUR IMMEDIATE EN APPLICATION DE L'ART. 2 (AL. 2) DU
DECRET DU 05-11-1870 »), n° 2002-1270 (`JORFTEXT000000600016`) et n° 2003-1131
(`JORFTEXT000000796798`). Après le 1er juin 2004 : le n° 2004-1029 du 30 septembre 2004
(`JORFTEXT000000445903`) vise « le code civil, notamment son article 1er ». Le texte qui fixait
l'entrée en vigueur des décrets avant l'ordonnance n° 2004-164 est donc **le décret du 5 novembre
1870 relatif à la promulgation des lois et décrets, art. 2** : son al. 2 est invoqué pour une entrée
en vigueur « immédiate » ; que la règle ordinaire soit à son al. 1 est une déduction, non lue.

**Non trouvé : le texte de ce décret, et l'art. 1er du code civil d'avant 2004.** Cherché, dans les
deux index : par le titre (`promulgation`, `1870`, `2004-164`, « Code civil » à l'art. 1, sous
`LEGIARTI000006419280` : le LEGI porte 156 documents « Code civil », pas celui-là) ; au plein texte
(« exécutoires dans tout le territoire », « promulgation en pourra être connue », « la promulgation
en est connue », « réputée connue », « jour franc » avec « promulgation », « modalités et effets de
la publication », « publication des lois et de certains actes administratifs », « 5 novembre 1870 »,
« article 1er du code civil »). Résultat : l'ordonnance n° 2004-164 n'a pas de texte à elle dans
l'index ; la loi n° 2004-1343 du 9 décembre 2004, art. 78, XIII (`JORFARTI000001288321`), la cite
« sous réserve de l'insertion » de mots à son art. 2 et d'un art. 5-1, sans reproduire l'ancien
art. 1er ; la décision n° 89-269 DC du 22 janvier 1990 (`JORFTEXT000000158576`) rapporte que les
auteurs de la saisine estiment qu'un décret « N'EST ENTRE EN VIGUEUR QU'UN JOUR FRANC APRES SA
PUBLICATION » : un argument de saisine, non la règle ; aucun texte de l'index ne donne le délai
de l'al. 1 de l'art. 2. **Rien n'est écrit ici de mémoire** : ni le délai,
ni la lecture « jour franc ». La question au propriétaire de B6 est donc plus précise : lire, à
Légifrance ou au Journal officiel, le décret du 5 novembre 1870 relatif à la promulgation des
lois et décrets (art. 2), à sa version d'avant 2004, et l'art. 1er du code civil dans sa version
d'avant le 1er juin 2004.

## 8. Écarts et candidats (non corrigés)

- **Écart 1 (moyen, preuve)** : n° 2021-1818, citation tronquée, garde aveugle à la troncature (§ 1).
- **Écart 2 (faible)** : n° 2011-1140 non tranché alors que l'index le tranche ; même cas, n° 2011-215
  (§ 5).
- **Écart 3 (faible)** : `preuve` des trois rattachements du n° 2023-1336 (§ 6).
- **Écart 4 (faible)** : trois dates d'effet antérieures à la publication, non dites : n° 98-809
  (1er août 1995, JO du 12 septembre 1998), n° 98-896 (1er août 1996, JO du 9 octobre 1998),
  n° 2017-180 (1er janvier 2017, JO du 15 février 2017). Les trois sont dans le texte ; la
  validité d'un effet antérieur à la publication n'est pas examinée ici, et n'est pas la question
  de la donnée, qui date ce que le texte date. À dire en une phrase dans la note ou l'en-tête.
- **Écart 5 (faible)** : B6 dit ajouter le tableau d'origine du n° 98-896 (« JO n° 234 du
  09/10/1998 page 15305 à 15307 », art. 8) et celui du n° 98-809 (« JO n° 211 du 12/09/1998 page
  13913 à 13915 », art. 10, lu à `JORFARTI000001895846`) à la file des fac-similés ;
  `docs/feuille_de_route/138/2026-11-05-la-file-des-fac-similes.md` ne les porte pas. À y
  ajouter, et à lire au fac-similé : le texte de l'index n'est pas l'original.
- **Écart 6 (faible)** : l'élargissement de 2002 n'est que dans la note (§ 5).
- **Candidat, méthode pour les 67 tableaux restants** : la notice du texte au JORF (« Entrée en
  vigueur : … ») et le `effet` du Noyau RH (`textes.csv`) recoupent la clause dans 43 et 25 cas
  sur 46 sans une erreur. Les utiliser en recoupement (jamais seuls), et ne pas se fier au texte
  5896 de `textes.csv` (n° 2011-215, § 5).
- **Candidat, pour le n° 2015-1275 art. 35** (rectificatif du 24 octobre 2015, déjà noté par B6) :
  non vérifié ici que `lignes.csv` suit le tableau rétabli.

Sources : index LEGI et JORF de la DILA (identifiants cités dans le texte) ; Noyau RH, `textes.csv`,
`grades.csv`, `echelons.csv` du dépôt ; tests du dépôt rejoués.
