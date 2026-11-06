# B7-bis : les corrections de la relecture R-B8 (le n° 2007-835, les quatre « prend effet », le n° 2018-648, le n° 2012-1139, le paquet, le code civil)

Vague 11, B7-bis, le 6 novembre 2026. Reprise, à la place de leur auteur, des écarts que la relecture
R-B8 (commit 25e66e9, `2026-11-06-relecture-r-b8.md`) a trouvés dans le travail de B7 (commit 9071c32,
`2026-11-06-b7-dates-d-apres-juin-2004.md`) et de B6-bis (commit aa32559). **Aucune date n'est fausse :
ce sont des déclarations.** Chaque point est revérifié au texte avant d'être écrit, non repris de la note
de R-B8 ni de la mémoire. Lu pendant la session : l'index LEGI (dump `Freemium_legi_global_20250713-140000`,
incrément 20261102-213929) et l'index JORF (même dump, incrément 20261103-002311), récupérés par
`dila_index.py --recuperer` et interrogés par `dila_cherche.py` et par des requêtes écrites ici. Aucun
fac-similé n'est lu. Légifrance n'est pas ouvert (point 6). Les deux index sont effacés en finissant
(`data/brut/dila/`).

## 1. Le n° 2007-835, art. 4 : deux lectures, une date gardée (écart moyen de R-B8)

**Ce que je lis.** Le texte signé au JORF (`JORFTEXT000000793379`, JO du 13 mai 2007) a cinq articles
(art. 1 `JORFARTI000002268791`, art. 2 `JORFARTI000001085112`, art. 3 `JORFARTI000002268792`, art. 4
`JORFARTI000002102781`, art. 5 `JORFARTI000002268793`). Aucun ne dit « entre en vigueur » ; l'art. 5
est l'exécution (« qui sera publié au Journal officiel de la République française »). Deux articles
parlent de la publication, et ils sont cités entiers à l'en-tête de `tableaux.csv` :

- art. 1er (`JORFARTI000002268791`) : « L'article 1er du décret n° 93-658 du 26 mars 1993 susvisé est
  complété par un alinéa ainsi rédigé : « Le corps des moniteurs d'atelier est placé en voie d'extinction à
  compter de la date de publication du décret n° 2007-835 du 11 mai 2007. » » ;
- art. 4 (`JORFARTI000002102781`, le tableau) : « Les moniteurs d'atelier en fonctions à la date de
  publication du présent décret sont reclassés conformément au tableau ci-dessous : ».

Le LEGI porte la phrase de l'art. 1er dans la version de l'art. 1er du décret n° 93-658 ouverte le
2007-05-13 (`LEGIARTI000006713282`, 2007-05-13 → 2017-01-01). Les art. 1 à 3 du n° 2007-835, au LEGI, ne
sont que « a modifié les dispositions suivantes » ; l'art. 4 (`LEGIARTI000006264680`) et l'art. 5
(`LEGIARTI000006264681`) s'ouvrent le 2007-05-13.

**Les deux lectures, que le texte ne tranche pas.** (1) Le décret ne fixe pas la date de son entrée en
vigueur, et la phrase du tableau ne date que la condition (« en fonctions à la date de publication ») :
le tableau entre en vigueur à défaut le lendemain de la publication (code civil, art. 1er), le **14 mai
2007**. (2) Le décret prend lui-même la date de publication pour début de l'extinction du corps (art. 1er),
et le reclassement de l'art. 4 la prendrait pour pivot : le **13 mai 2007**, jour du JO, que le LEGI porte.

**Ce que je garde : le 14 mai 2007**, comme B7 et la règle de B6-bis pour le n° 2011-1140 (une date
retenue, l'autre lecture écrite). Raison : aucune source ne donne le 13 mai en dehors du début des versions
du LEGI, et ce début n'en est pas une preuve, puisque le LEGI ouvre au jour du JO les articles de décrets de
cette époque qui n'ont aucune clause : l'art. 18 du n° 2005-1132 (`LEGIARTI000006413884`) s'ouvre le
2005-09-10, jour de son JO (index JORF, texte signé du n° 2005-1132). L'écart est d'un jour. **Rien ne
change dans la colonne `effet`** (2007-05-14) ; l'en-tête dit les deux lectures, les deux articles entiers,
les deux dates, et « le texte ne tranche pas ».

**Pourquoi la garde ne l'a pas vu.** Le test des décrets sans clause cherche `CLAUSE`, qui ne contient pas
« à compter de la date de publication » : l'art. 1er du n° 2007-835 passe. J'ai refait la recherche avec un
motif large (entre en vigueur, prend effet, produit effet, applicable à, rétroactif, urgence, lendemain,
premier jour, dès sa publication, à compter de, avec effet, date de publication) sur tous les articles
du JORF des treize décrets sans clause, sans les expressions de condition (« la date d'entrée en vigueur du
présent décret », « à compter de la notification »…) : 23 occurrences. Deux, de la même phrase, sont
l'art. 1er du n° 2007-835 : **le seul article qui date le décret lui-même**. Une est l'art. 4 du même décret
(la condition « en fonctions à la date de publication »). Les 20 autres sont des conditions ou des
échéances (« les dispositions applicables à la date de publication de cet arrêté », « demeurent valables
jusqu'au 31 décembre 2012 », « la titularisation prend effet à la date prévue de fin de stage »). Les art.
3, 8, 14 et 15 du n° 2014-71 ne sont pas à l'index (lus à Légifrance par B7, relus par R-B8).

**Le chaînage.** La ligne 244 de `chainage/reclassements.csv` (art. 4, `LEGIARTI000006264680`) porte la
date 2007-05-14 (`date_lue` `effet`), statut `declare`, raison « versant hospitaliere : ses grilles ne
sont qu'au LEGI […] » : le groupe est déclaré pour cette raison, que ni l'une ni l'autre lecture ne change.
Le fichier est donc inchangé ; l'autre lecture n'y est pas répétée, elle est à l'en-tête de `tableaux.csv`.

**Le test d'abord.** `test_l_entete_declare_les_prises_d_effet_les_deux_lectures_du_2007_835_et_le_2012_1139`
(vu rouge : l'en-tête ne portait rien de ces déclarations), puis le code. Un second test, à l'index,
`test_les_deux_lectures_du_2007_835_et_les_articles_non_lus_du_2012_1139_sont_ceux_des_index`, vérifie que
les deux articles cités sont ceux du JORF, entiers, que le LEGI porte la phrase de l'art. 1er, ses dates, et
que le n° 2005-1132 s'ouvre au jour de son JO (il passe d'emblée : il confronte des faits, non du code).

## 2. Les quatre « prend effet » : déclarés à l'en-tête (écart faible 1)

B7 les intitulait « points non tranchés » (note, point 5) et écrivait la date sans un mot à l'en-tête.
L'en-tête dit maintenant, pour chacun, son article, le JO, la clause entière (celle d'`ENTREES_EN_VIGUEUR`,
égale à l'article du LEGI, relue ici pour les quatre), la date de la donnée (lecture 1 : la date de la
clause lue comme l'entrée en vigueur, déduite de ce que le décret n'a pas d'autre clause de date, non un
mot du texte) et l'autre (lecture 2 : l'entrée en vigueur au lendemain de la publication, le décret ne
prenant effet qu'à la date de la clause).

| Décret | JO | Clause | Donnée (lecture 1) | Lecture 2 |
|---|---|---|---|---|
| n° 2005-939 | 6 août 2005 | art. 28, « qui prendra effet au 1er janvier 2006 » | 2006-01-01 | 2005-08-07 |
| n° 2005-1304 | 22 octobre 2005 | art. 43, « qui prendra effet au 1er novembre 2005 » | 2005-11-01 | 2005-10-23 |
| n° 2011-215 | 27 février 2011 | art. 21, « prennent effet le premier jour du mois suivant celui de sa publication » | 2011-03-01 | 2011-02-28 |
| n° 2011-1140 | 23 septembre 2011 | art. 35, « prend effet à compter du 1er jour du mois qui suit sa publication » | 2011-10-01 | 2011-09-24 |

**Ce que portent les sources, relu.** Le début des versions des tableaux au LEGI est la date de la clause
(2006-01-01, art. 20 ; 2005-11-01, art. 36 ; 2011-03-01, art. 13 ; 2011-10-01, art. 21 et 22). Le Noyau RH
(`etat/textes.csv`) porte `effet` 2006-01-01 (texte 295), 2005-11-01 (texte 386), 2011-10-01 (texte 926) ;
sa ligne 5896 (n° 2011-215) porte des dates de 2018 (2018-02-25, 2018-03-01, 2018-02-27), une erreur du
Noyau RH que je n'utilise pas. Seule la notice du n° 2011-1140 dit « Entrée en vigueur : le 1er octobre
2011 » ; celles des trois autres n'en ont pas. **Aucune source lue ne porte l'autre date**, d'où la phrase de
l'en-tête. Les tableaux : n° 2005-939, art. 20, n° 2011-215, art. 13, n° 2011-1140, art. 21 et 22 disent « A
la date d'entrée en vigueur du présent décret » ; celui du n° 2005-1304, art. 36, n'écrit pas la date du
reclassement (« qui se trouvent, à la date de publication du présent décret, dans l'une des positions »).

## 3. Le n° 2018-648 : la formule (écart faible 2)

**Où elle est écrite.** « La date qu'ils fixent peut précéder la publication » n'est écrite que dans la note
de B7 (point 1, cas 4), un récit qui ne se récrit pas (recherche faite dans `scripts/`, `tests/`, `data/` et
`docs/` hors des notes : rien dans les données, le script, les tests, le journal de veille). **L'en-tête de
`tableaux.csv` ne dit pas cela** : il dit « Quatre effets précèdent la publication de leur décret, et le
texte les date ainsi […] ; la donnée date ce que le texte date, sans examiner la validité d'un effet
antérieur à la publication ». Rien à y corriger ; la correction est ici, avec un renvoi daté au bout de la
note de B7.

**Ce que l'art. 1er du code civil dit.** Les actes administratifs « entrent en vigueur à la date qu'ils
fixent ou, à défaut, le lendemain de leur publication » : il ne dit rien de l'effet rétroactif, ne le
permet ni ne l'interdit.

**Ce qui soutient la date du n° 2018-648 (1er janvier 2017, JO du 25 juillet 2018, `JORFTEXT000037245707`).**
(a) L'art. 8 (`JORFARTI000037245737` ; `LEGIARTI000037246485`), cité entier dans `ENTREES_EN_VIGUEUR` : « Les
dispositions du présent décret entrent en vigueur le 1er janvier 2017, à l'exception de celles des articles
1er, 5 et 6. » ; (b) l'art. 7, le tableau (`JORFARTI000037245735` ; `LEGIARTI000037246483`, 2018-07-26 →),
n'est pas un article excepté, et son II dit : « II. - Les fonctionnaires mentionnés au I conservent les
réductions et majorations d'ancienneté accordées au titre des années précédant l'année 2017 et non utilisées
pour un avancement d'échelon dans les conditions fixées par le décret du 28 juillet 2010 susvisé. » : le
reclassement du I est pensé à l'année 2017. La lecture contraire (26 juillet 2018, lendemain du JO) n'a pour
elle que le début de la version au LEGI.

## 4. Le n° 2012-1139 : où sont les articles non lus (écart faible 3)

B7 le déclarait dans sa note seulement. **Dit maintenant à l'en-tête** : la clause (art. 68) est lue à
Légifrance et vaut pour tout le décret (« Les dispositions du présent décret entrent en vigueur le premier
jour du mois suivant celui de sa publication au Journal officiel de la République française. ») ; la notice
du texte à l'index JORF (`JORFTEXT000026477051`, JO du 11 octobre 2012) dit « Entrée en vigueur : le texte
entre en vigueur le 1er novembre 2012. » ; les art. 16 à 20, 24, 25, 28, 34 à 42, 44 à 47, 52 à 62 et 64 à 66
ne sont lus ni aux index, qui ne les ont pas, ni à Légifrance.

**Vérifié ici** : l'index JORF n'a que 17 articles de ce décret (21 à 23, 26, 27, 29 à 33, 43, 48 à 51, 63,
67) et l'index LEGI 4 (48 à 51) ; aucun n'est dans la liste des non lus, et l'art. 68 n'y est pas (test à
l'index). **Non rouvert ici** : la lecture à Légifrance des art. 1 à 15, 68 et 69, par B7 et R-B8 (lecteur
web, qui ne rend une page que jusqu'à environ 39 400 caractères). Je laisse la lecture telle quelle : le
risque est mince, la clause valant pour tout le décret et la notice disant la même date.

## 5. Le paquet (écart faible 4)

B7 (point 10) écrivait que `construire_donnees.py` « ne lit que `reclassements/lignes.csv` ». **C'est
inexact** : ce script ne nomme aucun fichier de reclassements (recherche de « reclassements » dans
`scripts/construire_donnees.py`, `src/` et `moteur/js/` : aucune ligne). `lignes.csv` est lu par
`scripts/verifier_donnees.py` (la série `reclassements_*`), non par le paquet. `tableaux.csv` ne l'est pas
davantage ; j'ai relancé `python scripts/construire_donnees.py` : `moteur/donnees.json` ne bouge pas.

## 6. L'article 1er du code civil : non lu en direct (écart faible 5)

**Ce que je n'ai pas pu faire** : le lire à Légifrance. La page
(`https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006419280`, et la même avec `/2004-06-01`)
répond **403** à `curl` (retesté le 6 novembre 2026, via le mandataire de la session). Il n'est dans aucun
des deux index du dépôt (filtre thématique : `dila_cherche.py legi --num 1 --titre "code civil"` ne rend que
des articles 1er de décrets et d'arrêtés). **Ce que la preuve est** : le texte de B7 (la constante
`ARTICLE_1ER_DU_CODE_CIVIL`, citée entière à l'en-tête de `tableaux.csv`), confronté par R-B8, phrase à
phrase, à la page de Légifrance, au moyen d'un lecteur web intermédiaire (« identique » pour les quatre
phrases) ; B7 l'avait lu au même lecteur. C'est une comparaison, non une copie. Selon B7 et R-B8, aucune
version plus récente n'est affichée (« En vigueur depuis le 01 juin 2004 » à la date du 6 novembre 2026),
mais la liste des versions n'a été ouverte par personne. **Question au propriétaire** : ouvrir cette page, et en garder une
copie PDF avec les preuves du dépôt (`LEGIARTI000006419280`, version du 1er juin 2004).

## 7. Ce qui bouge

- `scripts/fetch/dila_legi_reclassements.py` : `LECTURES_DES_PRISES_D_EFFET` et `LECTURES_NON_TRANCHEES`,
  qui entrent dans l'en-tête de `tableaux.csv` ; rien d'autre (aucune règle, aucune date).
- `data/reference/grilles/reclassements/tableaux.csv` : la première ligne (l'en-tête, 2 846 → 6 791 octets) ;
  aucune ligne de données.
- `tests/test_reclassements.py` : deux tests neufs (point 1) et leurs constantes.
- `docs/feuille_de_route.md` : le bloc « Reprise » de l'action 158 ; `2026-11-06-b7-dates-d-apres-juin-2004.md` :
  un renvoi daté d'une ligne ; le journal de veille `2026-11-06-action-158-b7-bis.yaml`.
- Inchangés : `effet` des 450 tableaux, `chainage/reclassements.csv`, `moteur/donnees.json`.
- Lancés : `tests/test_reclassements.py` et `tests/test_chainage_grilles.py` en entier, sous les deux jeux
  (`PRESOMPTIONS_DECALEES=1` aussi), index présent : 88 passés ; `python -m pytest -m rapide` : 4 554
  passés, 8 ignorés, 11 rouges (tous `tests/test_pages_en_dossier.py`, pages que GitHub refait) ;
  `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide` : 4 349 passés, 213 ignorés, les mêmes 11.
  `python scripts/construire_donnees.py` : `moteur/donnees.json` et `data/derive/` inchangés.

## 8. Candidats (non corrigés)

- **`CLAUSE` ne reconnaît pas « à compter de la date de publication du décret »** (point 1) : le test des
  décrets sans clause laisse passer l'art. 1er du n° 2007-835. Le motif large du point 1 le trouve ; l'ajouter
  à `CLAUSE` demande d'excepter ce décret, à décider avec la lecture (1) ou (2).
- Toujours ouverts, hors de la tâche : les 25 tableaux d'avant juin 2004 (la règle du décret du 5
  novembre 1870, question 29 au propriétaire) ; les 7 points non tranchés de B7, et ceux déjà nommés ; le
  tableau mal découpé du n° 2004-1439, art. 23 ; les art. 18 et 19 du n° 2005-939, sans ligne dans
  `tableaux.csv` (R-B8) ; l'en-tête pourrait dire que l'art. 26 du n° 2010-989 est au chapitre III (R-B8) ;
  les 90 tableaux de l'index publié ; le rectificatif du n° 2015-1275 ; l'annexe du n° 94-1016.

Sources : index LEGI et JORF de la DILA (identifiants cités dans le texte, lus pendant la session) ; Noyau
RH du dépôt (`etat/textes.csv`), en recoupement ; Légifrance, réponse 403 à `curl` pour le code civil, art.
1er (aucune lecture directe) ; tests du dépôt rejoués.
