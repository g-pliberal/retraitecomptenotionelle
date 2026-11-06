# Relecture de B7 et de B6-bis : les dates d'effet des tableaux d'après juin 2004, par l'article 1er du code civil

Vague 11, R-B8, le 6 novembre 2026. Relecture indépendante du commit 9071c32 (B7, note
`2026-11-06-b7-dates-d-apres-juin-2004.md`) et des dates neuves du commit aa32559 (B6-bis, note
`2026-11-06-b6-bis-corrections-de-r-b7.md`). Rien n'est repris de leurs notes ni de la mémoire. Lu
pendant la session : l'index LEGI (dump `Freemium_legi_global_20250713-140000`, incrément
20261102-213929) et l'index JORF (même dump, incrément 20261103-002311), récupérés par
`dila_index.py --recuperer` et interrogés par un script écrit ici, non par celui du dépôt (table
`doc` : le texte au JORF par son numéro, tous ses articles par le titre et le jour du JO, les
versions au LEGI) ; les dates refaites par `datetime`, non par le calcul de B7. Légifrance, par un
lecteur web (agent `web-fetch`), avec les limites du point 1. Le Noyau RH du dépôt sert de
recoupement, jamais de preuve. Aucune règle, donnée ou test n'est touché. Aucun fac-similé n'est lu.
Les deux index sont effacés en finissant (`data/brut/dila/`).

**Verdict : aucune date fausse.** Les 36 dates (34 de B7, 2 de B6-bis) se refont à la main d'après
la clause, ou d'après l'absence de clause ; les quatre écarts au LEGI tiennent ; les 61 clauses
citées de `ENTREES_EN_VIGUEUR` sont, mot pour mot, l'article du LEGI. Aucun écart fort. **Un écart
moyen** (une déclaration, n° 2007-835 : une seconde lecture est tenable et n'est pas dite) et **cinq
faibles**. Deux limites de preuve, dites aux points 1 et 10.

## 1. La règle : code civil, art. 1er

**Ouvert** (Légifrance, `/codes/article_lc/LEGIARTI000006419280`, réponse 200, par le lecteur web) :
titre de la page « Article 1 - Code civil - Légifrance », « En vigueur depuis le 01 juin 2004 »,
« Modifié par Ordonnance n°2004-164 du 20 février 2004 - art. 1 () JORF 21 février 2004 en vigueur
le 1er juin 2004 », trois alinéas. L'index LEGI du dépôt ne l'a pas (`--num 1 --titre "code civil"` ne
rend que des articles 1 de décrets et d'arrêtés), comme B7 le dit.

**Ce que je n'ai pas pu faire : le lire moi-même, d'un seul tenant.** La page répond 403 à
`curl` ; le lecteur web ne cite pas plus de 125 caractères de suite et a refusé de découper
l'article en fragments. J'ai donc fait le contraire : je lui ai soumis le texte de B7 (la constante
`ARTICLE_1ER_DU_CODE_CIVIL`, 666 caractères, qui est mot pour mot celle de l'en-tête de
`tableaux.csv`, vérifié par un `in`) et demandé, phrase par phrase, « identique » ou « différente » :
**les quatre phrases sont identiques**, la page n'a pas de phrase de plus ni de moins. Le début des
alinéas 1 et 2 et l'alinéa 3 en entier, que le lecteur a pu citer, concordent. C'est une
comparaison, par un lecteur intermédiaire, non une copie : la preuve écrite de l'énoncé exact est la
constante de B7, confirmée ainsi. **Pour la tenir sans intermédiaire, le propriétaire peut ouvrir la
page et en garder une copie (PDF) avec les preuves.**

**A-t-il changé depuis 2004 ?** La mention « En vigueur depuis le 01 juin 2004 », à la date du 6
novembre 2026, dit qu'aucune version plus récente ne l'a remplacé ; la liste des versions n'est pas
visible du lecteur et n'a pas été ouverte. B7 a vu la même mention. Les 34 textes sont publiés du 6
août 2005 au 10 novembre 2019 : la version est la bonne pour tous.

**Ce que l'article dit des cas de la tâche** : B7 (point 1) est conforme sur (1) la date fixée, sinon
le lendemain de la publication ; (2) les mesures d'application (aucune des 36 phrases de tableau n'en
nomme, voir plus bas, sauf le n° 2010-302, laissé sans date) ; (3) l'urgence, une « disposition
spéciale » ; (5) les actes individuels. **Nuance sur (4), écart faible 3** : l'article ne dit rien de
l'effet rétroactif, comme B7 l'écrit ; la suite de la phrase de B7 (« la date qu'ils fixent peut
précéder la publication ») n'est pas dans l'article, qui ne le permet ni ne l'interdit.

## 2. Les 36 dates refaites

Pour chaque décret : le texte au JORF par son numéro ; le jour du JO (champ `date`) ; **tous** ses
articles (même titre, même jour, numérotation sans trou sauf les trois décrets du point 4) ; chaque
phrase passée à un motif écrit ici, plus large que `CLAUSE` du dépôt (entre/entrent/entrera en
vigueur, prend/prendra/prennent effet, produit effet, applicab, s'appliqu, rétroact, urgence,
lendemain, premier jour, dès sa publication, à compter de la publication/du/de l'entrée, au 1er mois
année, à partir du, avec effet, date de publication) ; la clause comparée à la citation du dépôt, au
LEGI (une seule version à chaque fois) et au JORF ; la date refaite. **Légifrance** : le jour du JO
de 19 textes relu à la page du texte (« JORF n°… du … »), identique à l'index pour les 19.

| Décret | JO (JORF) | Fondement, relu | Date refaite | `effet` | JO à Légifrance |
|---|---|---|---|---|---|
| 2010-1719 | 31 déc. 2010 | art. 23 « entrera en vigueur au 1er janvier 2011 » | 2011-01-01 | idem | – |
| 2010-1720 | 31 déc. 2010 | art. 27, mêmes mots | 2011-01-01 | idem | – |
| 2012-761 | 10 mai 2012 | art. 17 « le premier jour du mois qui suit sa publication » | mai → 2012-06-01 | idem | n°0109 du 10 mai 2012 |
| 2012-762 | 10 mai 2012 | art. 37, mêmes mots | 2012-06-01 | idem | – (notice : même clause) |
| 2012-1002 | 30 août 2012 | art. 14 « le premier jour du mois suivant sa publication » | 2012-09-01 | idem | n°0201 |
| 2012-1139 | 11 oct. 2012 | art. 68 (Légifrance, page d'article : identique) | 2012-11-01 | idem | – (en-tête de la page : « 1er novembre 2012 ») |
| 2013-176 | 28 févr. 2013 | art. 39 | 2013-03-01 | idem | – (notice : 1er mars 2013) |
| 2013-875 | 29 sept. 2013 | art. 18 | 2013-10-01 | idem | – (notice : 1er octobre 2013) |
| 2013-974 | 31 oct. 2013 | art. 32 | 2013-11-01 | idem | n°0254 |
| 2015-363 | 31 mars 2015 | art. 14 (Légifrance, page d'article : identique) | 2015-04-01 (2 tableaux) | idem | – (page : « 1er avril 2015 ») |
| 2016-2008 | 31 déc. 2016 | art. 29 « Sous réserve des dispositions de l'article 12,le présent décret entre en vigueur le 1er janvier 2017 » | 2017-01-01 | idem | – (notice : 1er janvier 2017) |
| 2018-648 | 25 juil. 2018 | art. 8 « entrent en vigueur le 1er janvier 2017, à l'exception de celles des articles 1er, 5 et 6 » | 2017-01-01 | idem | n°0169 |
| 2010-982 | 28 août 2010 | art. 39 II, « titre II … le 1er septembre 2010 » ; art. 33 au titre II | 2010-09-01 | idem | table des matières lue (point 3) |
| 2005-939 | 6 août 2005 | art. 28 « qui prendra effet au 1er janvier 2006 » | 2006-01-01 | idem | – |
| 2005-1304 | 22 oct. 2005 | art. 43 « qui prendra effet au 1er novembre 2005 » | 2005-11-01 | idem | – |
| 2011-215 | 27 févr. 2011 | art. 21 « prennent effet le premier jour du mois suivant celui de sa publication » | févr. → 2011-03-01 | idem | n°0049 du 27 févr. 2011 |
| 2011-1140 (B6-bis) | 23 sept. 2011 | art. 35 « prend effet à compter du 1er jour du mois qui suit sa publication » | sept. → 2011-10-01 (2 tableaux) | idem | n°0221 |
| 2007-835 | 13 mai 2007 | aucune clause (point 5) | 2007-05-14 | idem | n°111 du 13 mai 2007 |
| 2010-647 | 13 juin 2010 | aucune clause | 2010-06-14 | idem | n°0135 |
| 2011-489 | 5 mai 2011 | aucune clause | 2011-05-06 | idem | n°0104 du 5 mai 2011 |
| 2011-744 | 29 juin 2011 | aucune clause | 2011-06-30 (2 tableaux) | idem | n°0149 |
| 2011-1139 | 23 sept. 2011 | aucune clause ; notice « le lendemain de sa publication » | 2011-09-24 (2 tableaux) | idem | n°0221 |
| 2012-78 | 25 janv. 2012 | aucune clause ; notice « le lendemain » | 2012-01-26 (2 tableaux) | idem | n°0021 |
| 2012-229 | 18 févr. 2012 | aucune clause ; notice « le lendemain » | 2012-02-19 | idem | n°0042 |
| 2013-489 | 12 juin 2013 | aucune clause ; notice « le lendemain » | 2013-06-13 | idem | n°0134 |
| 2013-1173 | 19 déc. 2013 | aucune clause ; notice « le lendemain » | 2013-12-20 | idem | n°0294 |
| 2014-71 | 31 janv. 2014 | aucune clause ; notice « le lendemain » | fin de mois → 2014-02-01 (2 tableaux) | idem | n°0026 |
| 2015-1792 | 30 déc. 2015 | aucune clause ; notice « le lendemain du jour de sa publication » | 2015-12-31 | idem | n°0302 |
| 2016-1177 | 31 août 2016 | aucune clause ; notice « le lendemain » | fin de mois → 2016-09-01 | idem | n°0202 |
| 2019-1160 | 10 nov. 2019 | aucune clause ; notice « au lendemain » | 2019-11-11 | idem | n°0262 |

12 + 1 + 4 + 13 = 30 décrets, **36 tableaux** (13 + 1 + 3 + 17 pour B7, 2 pour B6-bis) ; la colonne `effet` du
dépôt est égale à ma date pour les 36. L'index porte une notice « Entrée en vigueur » pour les textes de 2011 et après
(9 des 13 « lendemain » en ont une, qui dit le lendemain ; les 4 autres sont de 2007 à 2011 et n'en ont pas). Les
`debut` du LEGI sont égaux à `effet` pour 32 tableaux sur 36 ; les quatre autres sont au point 3.

**Les clauses.** Pour les 14 décrets que j'ai passés un à un (les dix de la clause « en vigueur », les trois « prend
effet » de B7 et le n° 2011-1140 de B6-bis), le texte de l'article au LEGI est la citation du dépôt, à l'espace
près ; au JORF il est identique (le n° 2010-1719 et le n° 2010-1720 y
ajoutent « Fait le 30 décembre 2010. » et la signature, comme B7 le dit). **Les 61 entrées** de
`ENTREES_EN_VIGUEUR` (celles de B6 comprises), contrôlées par un script écrit ici : citation = article au LEGI, JO =
index, numéro dans les deux titres : **0 écart** ; la date est écrite dans la citation (21 cas) ou est le premier du
mois suivant le JO (39 cas) ; le 61e, le n° 2025-1327, écrit « 1 er janvier 2026 » avec une espace dans la source.

## 3. Les quatre écarts au LEGI, et le n° 2010-982

- **n° 2012-761 et n° 2012-762** (2012-05-11 → 2012-06-01) : la clause est écrite (art. 17 et art. 37) ; la notice
  de l'index dit « le texte entre en vigueur le premier jour du mois qui suit sa publication » ; le LEGI ouvre la
  version au lendemain du JO, sans lire la clause (le Noyau RH aussi, texte 1315, effet 2012-05-11). **B7 tient, le LEGI ne
  tient pas.** Le tableau de l'art. 10 du n° 2012-761 dit, au bout de sa phrase, « à la date d'entrée en vigueur du
  présent décret » (lu en entier) : même date.
- **n° 2018-648** (2018-07-26 → 2017-01-01) : l'art. 8 est écrit comme B7 le cite ; l'art. 7, le tableau, est un article
  que l'exception (art. 1er, 5, 6) ne touche pas. **Ce que le texte ajoute et que B7 ne cite pas** : l'art. 7, II, « Les
  fonctionnaires mentionnés au I conservent les réductions et majorations d'ancienneté accordées au titre des
  années précédant l'année 2017 » : le reclassement est bien pensé à l'année 2017, ce qui soutient la lecture de
  B7. La lecture contraire (26 juillet 2018) n'a pour elle aucune source ; B7 la cite, avec raison. L'effet
  précède la publication : dit à l'en-tête (« Quatre effets précèdent la publication », JO du 25 juillet 2018,
  exact). Conforme, sauf la nuance du point 1.
- **n° 2007-835** (2007-05-13 → 2007-05-14) : voir le point 5, écart moyen 1.
- **n° 2010-982**, tableau daté par titre. Art. 39 : « I. ― Les dispositions du titre Ier entrent en vigueur le 1er
  septembre 2011. II. - Les dispositions du titre II entrent en vigueur le 1er septembre 2010. » Table des matières
  lue à Légifrance : **Titre Ier « Articles 1 à 30 »** (l'art. 20 y est, au chapitre V), **Titre II « DISPOSITIONS
  MODIFIANT DIVERSES DISPOSITIONS STATUTAIRES APPLICABLES AUX CORPS DES CONTROLEURS DES IMPOTS ET DES CONTROLEURS DU
  TRESOR PUBLIC (Articles 31 à 38) »**, Titre III « Articles 39 à 40 ». L'art. 33 est donc au titre II : 2010-09-01.
  Recoupement au LEGI : les versions des art. 19 à 23 (titre Ier) s'ouvrent le 2011-09-01, celles des art. 33, 34 et 38
  (titre II) le 2010-09-01. **Conforme.**

## 4. Les « prend effet » (2005-939, 2005-1304, 2011-215) et le n° 2011-1140

**Le texte.** Les quatre clauses sont citées au point 2 ; pour le n° 2005-939 et le n° 2005-1304, « qui prendra
effet » est dans l'article d'exécution. Les articles de tableau disent, pour le n° 2005-939 et le n° 2011-215, « A la date
d'entrée en vigueur du présent décret » ; le n° 2005-1304 n'écrit pas la date du reclassement (« qui se trouvent, à la date de
publication du présent décret, dans l'une des positions … sont reclassés conformément au tableau ») : la date de
publication dit qui est reclassé, non quand, comme B7 l'écrit. **Une seule clause de date par décret** : mon
balayage des 28, 43, 22 et 36 articles (JORF) et des 39 documents du n° 2011-1140 au LEGI (36 numéros, versions
comprises) n'en trouve aucune autre.

**La déduction « prend effet » = « entrée en vigueur » tient, au texte.** La lecture contraire demanderait que le
reclassement de l'art. 20 du n° 2005-939 (« A la date d'entrée en vigueur du présent décret ») tombe le 7 août 2005,
cinq mois avant que le décret « prenne effet » : elle ne s'écrit pas. Les sources vont toutes dans le sens de B7 :
LEGI (début de version) 2006-01-01, 2005-11-01, 2011-03-01, 2011-10-01 ; Noyau RH `effet` 2006-01-01 (texte 295), 2005-11-01 (texte 386),
2011-10-01 (texte 926) ; notice du n° 2011-1140 « **Entrée en vigueur : le 1er octobre 2011** » : l'index écrit « entrée
en vigueur » pour cette clause « prend effet » ; aucune source ne donne le 24 septembre (n° 2011-1140) ni le 7 août
2005, le 23 octobre 2005 ou le 28 février 2011. Le n° 2011-215 n'a que le LEGI (pas de notice) ; la ligne 5896 du
Noyau RH, titre « Décret n° 2011-215 du 25 février 2011 », porte pourtant les années 2018 (2018-02-25 / 2018-03-01 / 2018-02-27) :
le jour et le mois sont ceux de B7, l'année est celle d'une erreur du Noyau RH. **Conforme** pour les dates ;
la déclaration est l'écart faible 2.

## 5. Les 13 décrets sans clause : le lendemain du JO

**Lus en entier.** 11 sur 13 sont entiers à l'index. Le n° 2014-71 en a 11 sur 15 : les art. 1 à 6 sont lus en entier à
Légifrance, les art. 3 (début identique à celui du test), 8 et 14 (début identique ; ils disent « postérieurement à la
date d'entrée en vigueur du présent décret » et, pour l'art. 14, II, « avant la date d'entrée en vigueur ») et 15
(l'exécution, « qui sera publié au Journal officiel ») sur leurs pages d'article ; le n° 2013-489 : l'article
d'exécution dit bien « de l'exécution du présent, qui sera publié » (le mot « décret » manque à l'index, B7 le dit).
**Aucune phrase des 13 ne fixe la date du décret** ; les dates écrites qu'on y trouve sont des listes d'aptitude, des
tableaux d'avancement « au titre de l'année 2011 », une CAP « au plus tard le 15 novembre 2011 » (n° 2011-489, art. 32) :
des échéances, non l'entrée en vigueur. Les 13 JO sont ceux de l'index et de Légifrance (tableau du point 2) ; le lendemain
se refait à la main pour les fins de mois (31 janvier, 31 août) et l'année bissextile (18 février 2012 → 19).

**Écart moyen 1 : le n° 2007-835, art. 4.** B7 écrit (point 6) : « aucun article ne dit quand il s'applique ». Or
l'art. 1er du décret (`JORFARTI000002268791`) dit : « Le corps des moniteurs d'atelier est placé en voie d'extinction **à
compter de la date de publication du décret n° 2007-835 du 11 mai 2007.** » Le décret fixe donc une date, la
publication, pour une de ses dispositions, et le tableau de l'art. 4 reclasse « les moniteurs d'atelier en fonctions
**à la date de publication du présent décret** ». Deux lectures sont tenables : (1) le tableau, que la phrase ne date
pas, entre en vigueur par défaut le lendemain, **14 mai 2007** (art. 1er du code civil : l'urgence demande une
disposition spéciale) ; (2) le décret prend sa date de publication, **13 mai 2007**, pour pivot de l'extinction et du
reclassement, et le LEGI (les versions des art. 4 et 5 s'ouvrent le 2007-05-13) la porte. La donnée écrit la
première seule, sans l'art. 1er et sans le dire. B7 a raison de dire que le LEGI ouvre ces textes au jour du JO par
habitude (le n° 2005-1132 de même), non par lecture de la clause ; mais la phrase de l'art. 1er est, elle, une clause. La
règle du propriétaire : la lecture contraire n'est pas intenable, donc point non tranché, les deux
dates citées. **À faire** (non fait ici) : ou laisser `effet` vide et ajouter le n° 2007-835, art. 4, aux points
non tranchés de l'en-tête, ou garder le 14 mai et l'y dire avec l'art. 1er. L'écart de date est d'un jour.

## 6. Les huit laissés sans date : conformes

Texte, article, JO et durées relus à l'index ; les phrases sont celles de B7 ; **7 + 1 = 8**.
- **n° 2005-1132** (JO 10 sept. 2005, 19 articles) : art. 18, trois tableaux, « A compter de la date de publication
  du présent décret » ; aucune clause.
- **n° 2006-8** (JO 5 janv. 2006 à l'index, 40 articles) : art. 32 et 33, « sont, à la date de publication du
  présent décret, reclassés » ; l'art. 30 dit « à compter de l'entrée en vigueur du présent décret », l'art. 38 « à
  compter de la date de publication » : deux dates que le décret distingue. (Le JO du 5 janvier n'a pas été relu à
  Légifrance par moi ; B7 l'a fait.)
- **n° 2010-989** (JO 28 août 2010, 37 articles) : art. 36, « chapitres Ier et III … 1er septembre 2010 », « chapitre
  II … 1er janvier 2011 ». La table des matières lue à Légifrance : chapitre Ier « Articles 1 à 24 », chapitre II
  « Article 25 », **chapitre III « DISPOSITIONS TRANSITOIRES ET FINALES (Articles 26 à 37) »** : l'art. 26 est au chapitre
  III. B7 laisse vide parce que la phrase dit « le présent décret » et que le Noyau RH (texte 1062) donne 2011-01-01 :
  prudent et cohérent avec son critère. L'en-tête ne dit pas que l'art. 26 est au chapitre III (la note le dit).
- **n° 2010-302** (JO 23 mars 2010, 18 articles) : art. 9, « A la date d'entrée en vigueur du décret portant
  inscription de leur corps au sein de l'annexe du présent décret » ; le LEGI ouvre l'art. 9 le 2010-03-24.
- **n° 2004-1439, art. 23** (version du 2023-08-01) : la ligne de `tableaux.csv` a pour phrase le I (« selon les
  modalités suivantes »), 15 lignes qui sont celles du II (Major de police 2, Brigadier-chef de classe supérieure 6,
  Brigadier-chef de la classe normale 7) ; le II dit « Au 1er janvier 2024 » ; le n° 2023-676, art. 21 (JO du 29 juillet
  2023), dit « le premier jour du mois qui suit celui de sa publication, à l'exception des dispositions des 3°, 4° et 5°
  de l'article 3 ainsi que de celles du 1° de l'article 6, en tant qu'il concerne les majors de police, qui entrent en
  vigueur le 1er janvier 2024 » : I au 1er août 2023, II au 1er janvier 2024. **B7 a raison de ne pas dater**.

## 7. Le chaînage : conforme

`chainage/reclassements.csv` : 862 groupes, **25 rattachés** (12 tableaux), 837 déclarés. **105 tableaux** (224 groupes)
déclarés « la phrase … n'écrit pas la date du reclassement » : recompté ici. Les six rattachements neufs, au Noyau RH
(`grades.csv`, `corps.csv`, `textes.csv`) :
- **n° 2012-229, art. 18** : le corps 00109 finit le 2012-02-18 et a pour suivant 01088 (texte 1041, « Décret n° 2012-229 »,
  abrogateur du premier, origine du second) ; les grades 00230, 00231, 00232 (grilles 01881, 01917, 01919) finissent le
  2012-02-18, les grades 03005, 03004, 03003 (grilles 01926, 01925, 01924) s'ouvrent le 2012-02-19 : les paires de B7.
- **n° 2013-875, art. 10** : les grades 00471 et 00472 finissent le 2013-09-30 et ont pour suivant 03405 (grille 01926,
  ouvert le 2013-10-01) ; 00473 passe de la grille 00481 à la grille 01925 le 2013-10-01. Les paires de B7.

Le Noyau RH change donc de corps ou de grilles le jour que la clause fixe (1er octobre 2013) ou le lendemain du JO (19
février 2012) : la date écrite et la date du Noyau RH s'accordent.

## 8. B6-bis

1. **N° 2011-1140** : la déduction tient (point 4).
2. **N° 2021-1818, art. 12** (JORF `JORFARTI000044571768`, JO du 28 décembre 2021) : l'article entier, première
   phrase (« entrent en vigueur le 1er janvier 2022 ») et seconde (« Elles ne s'appliquent pas aux auxiliaires de
   puériculture … ni aux auxiliaires de soins … »), est la citation du dépôt, au LEGI (une seule version, 2022-01-01) et au JORF.
   Les phrases des art. 7, 8 et 9 visent le décret du 12 mai 2016, le décret n° 2021-1079 et celui du 6 mai 1988 : pas les cadres d'emplois
   des décrets n° 92-865 et 92-866 que la seconde phrase écarte. La date ne bouge pas.
3. **La garde** (`_est_l_article`) : jouée ici avec cinq coupes de la citation du n° 2021-1818 (première phrase seule ;
   sans point ; seconde phrase seule ; sans les 25 derniers caractères ; sans les 20 premiers) : **les cinq sont refusées**,
   au LEGI comme au JORF ; l'article entier passe, avec « Art. 12. - » devant ou « Fait le 30 décembre 2010. » après
   dans le texte du JORF.
4. **La colonne `preuve` du n° 2023-1336** (trois lignes de l'art. 9) : comparée à `echelons.csv`, grille par grille, la
   veille et le jour du 2024-01-01 : grille 00541, les sept échelons (767 → 820, 826 → 862, 876 → 912, 927 → 977 et 24 → 36
   mois, 977 → 1027, 1027 → hors échelle A, A → B) ; grille 00542, les rangs 3 à 13 (522 → 542 et 12 → 6 mois, … 996 →
   1027), les rangs 1 et 2 (élève, stagiaire : 399 → 410, 445 → 456) mis à part, comme l'en-tête le dit ; grille 03781, l'échelon
   23530 (0 → 36 mois) et les deux neufs 25333 (C) et 25334 (D). **Les valeurs sont exactes.**
5. **Le compte 25 / 42** : recompté sur `tableaux.csv` (effet vide, phrase qui renvoie à l'entrée en vigueur, à l'effet ou à la publication) :
   25 tableaux d'avant le 1er juin 2004 (22 décrets et un arrêté, 23 textes) ; 8 d'après (le n° 2004-1439, les sept) ; 34
   datés par B7 : 25 + 8 + 34 = 67 ; 8 + 34 = 42. Les deux lignes du fichier des fac-similés (n° 98-809, n° 98-896)
   sont dans `138/2026-11-05-la-file-des-fac-similes.md`.

## 9. Tests lancés

- `tests/test_reclassements.py` et `tests/test_chainage_grilles.py` en entier, index présent : **86 passés**, sous les
  deux jeux (`PRESOMPTIONS_DECALEES=1` aussi). `tests/test_donnees.py` : 151 passés, puis 148 passés et 3 ignorés avec
  `PRESOMPTIONS_DECALEES=1`.
- `python -m pytest -m rapide` : **4 546 passés, 8 ignorés, 11 rouges** (tous `tests/test_pages_en_dossier.py`, pages que GitHub refait) ;
  avec `PRESOMPTIONS_DECALEES=1` : **4 341 passés, 213 ignorés, les mêmes 11**.
- `tableaux.csv` et `chainage/reclassements.csv` ne sont lus ni par le paquet ni par aucun des deux moteurs (grep dans `src`,
  `moteur`, `scripts/construire_donnees.py`) : les dates ne se rendent nulle part sur le site ; la preuve est celle des tests de
  référence.

## 10. Écarts et candidats (non corrigés)

**Forte** : aucune.

**Moyenne**
1. **n° 2007-835, art. 4** (point 5) : 14 mai 2007 écrit comme seule lecture ; l'art. 1er du décret (« à compter de la date de
   publication du décret n° 2007-835 ») rend le 13 mai tenable ; non dit.

**Faibles**
2. **Les quatre « prend effet »** (n° 2005-939, 2005-1304, 2011-215, 2011-1140) : la note B7 (point 5) les intitule « points
   non tranchés » et écrit pourtant la date ; l'en-tête de `tableaux.csv` n'en dit rien, et décrit `effet` comme « celle que le décret fixe »
   pour l'entrée en vigueur. Les dates sont soutenues (point 4) ; il faut un mot à l'en-tête : « ces quatre décrets disent
   "prend effet" ; la donnée y lit l'entrée en vigueur ».
3. **n° 2018-648** : B7, point 1 (4), « la date qu'ils fixent peut précéder la publication » : l'article 1er ne le dit pas ;
   et l'art. 7, II (« années précédant l'année 2017 ») n'est pas cité à l'appui (point 3).
4. **n° 2012-1139** : 35 articles sur 69 ne sont lus par personne (art. 16 à 20, 24, 25, 28, 34 à 42, 44 à 47, 52 à 62, 64 à 66 ;
   l'art. 69, d'exécution, n'est que résumé par le lecteur), ni à l'index ni à Légifrance (le lecteur web ne rend le texte d'une page que jusqu'à environ 39 400 caractères ; les pages d'article
   se lisent une à une, et leurs identifiants ne se devinent pas). B7 le dit. Le risque est mince (la clause vaut pour tout le
   décret, la notice et la page de Légifrance disent le 1er novembre 2012).
5. **Le paquet** : B7 (point 10) écrit que `construire_donnees.py` « ne lit que `reclassements/lignes.csv` » ; il ne lit
   aucun fichier de reclassements (seuls `verifier_donnees.py`, `verifier_prose.py` et les tests lisent `lignes.csv`).
6. **L'article 1er du code civil** n'est lu que par un lecteur intermédiaire, par B7 comme ici (point 1) ; la liste de ses versions
   n'est pas ouverte. Le propriétaire peut en garder une copie.

**Candidats (nouveaux ou rappelés)**
- Les art. 18 et 19 du n° 2005-939 (« A la date d'entrée en vigueur du présent décret, les commissaires de police [principaux]
  sont reclassés … conformément au tableau suivant », LEGI `LEGIARTI000006413789` et `…790`) n'ont pas de ligne dans `tableaux.csv`
  (l'art. 20 en a une) : sans doute parmi les 90 tableaux de l'index publié ; à dater du 2006-01-01 s'ils entrent.
- L'en-tête pourrait dire que l'art. 26 du n° 2010-989 est au chapitre III.
- Le Noyau RH : ligne 5896 (n° 2011-215, années 2018), publication du n° 2011-489 au 2011-05-06 (le JO est du 5 mai, Légifrance),
  `effet` du n° 2012-761, du n° 2010-982 et du n° 2010-989 : le recoupement ne vaut pas preuve.
- Le rectificatif du n° 2004-1439 (`JORFTEXT000000605093`, JO du 29 janvier 2005) existe : il ne touche pas l'art. 23 rétabli en 2023.
- Toujours ouverts, hors de la tâche : les 25 tableaux d'avant juin 2004 (la règle du décret du 5 novembre 1870), les 90 tableaux de l'index publié, le
  rectificatif du n° 2015-1275, l'annexe du n° 94-1016.

Sources : index LEGI et JORF de la DILA (identifiants cités, lus pendant la session) ; Légifrance, lu le 6 novembre 2026 par un
lecteur web : code civil, art. 1er (LEGIARTI000006419280, par comparaison phrase à phrase), pages des textes (mentions
« JORF n°… du … » de 19 textes ; tables des matières des n° 2010-982 et 2010-989), pages d'article (JORFARTI000026477172,
JORFARTI000030419590, JORFARTI000028539113, …120, …137, …142, JORFARTI000030419592, …612) ; Noyau RH du dépôt (`textes.csv`,
`grades.csv`, `corps.csv`, `echelons.csv`) en recoupement ; tests du dépôt rejoués.
