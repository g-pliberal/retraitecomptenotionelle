# B6-bis : les corrections de la relecture R-B7 (la clause du n° 2021-1818, le n° 2011-1140, la preuve du n° 2023-1336, les 67 tableaux restants)

Vague 11, B6-bis, le 6 novembre 2026, sur Sonnet. Reprend les six écarts de la relecture R-B7
(`2026-11-06-relecture-r-b7.md`, commit 0036c11) du travail de B6 (commit 94f30a5,
`2026-11-06-b6-dates-relatives-au-decret.md`). Tout ce qui suit a été rouvert pendant la session,
à l'index LEGI du dépôt (dump `Freemium_legi_global_20250713-140000`, à jour au 20261102-213929)
et à l'index JORF (`Freemium_jorf_global_20250713-140000`, à jour au 20261103-002311), par
`dila_cherche.py --texte` et par des requêtes directes sur la table `doc` ; le Noyau RH du dépôt
(`data/reference/grilles/etat/`) sert de recoupement. Aucun fac-similé n'est lu. Les deux index
sont effacés en finissant. Aucune règle du scénario 1 n'est touchée : des dates d'effet de
tableaux de reclassement, une preuve, un en-tête.

## 1. Le n° 2021-1818 : la clause entière, et une garde qui voit la troncature (écart 1)

**La clause, mot pour mot** (art. 12 ; `LEGIARTI000044804898`, une seule version, du 2022-01-01 ;
`JORFARTI000044571768`, JO du 28 décembre 2021, `JORFTEXT000044571714`) : « Les dispositions du
présent décret entrent en vigueur le 1er janvier 2022. Elles ne s'appliquent pas aux auxiliaires
de puériculture relevant, au 31 décembre 2021, du cadre d'emplois régi par le décret n° 92-865 du
28 août 1992 susvisé ni aux auxiliaires de soins relevant, à la même date, de la spécialité
aide-soignant du cadre d'emplois régi par le décret n° 92-866 du 28 août 1992 susvisé. » Le LEGI et
le JORF disent la même chose. La seconde phrase écarte des personnes, non des articles : les
tableaux des art. 7, 8 et 9 gardent le 1er janvier 2022 pour les agents qu'ils reclassent. La date
n'a pas bougé ; la citation (`ENTREES_EN_VIGUEUR`, dans `scripts/fetch/dila_legi_reclassements.py`)
est maintenant l'article entier, et son commentaire dit que la seconde phrase écarte des
personnes.

**La garde.** Avant, `_plat(citation) in texte` : une citation qui garde la date passait même
coupée. Maintenant, dans `tests/test_reclassements.py` :

- `_est_l_article(citation, texte, jorf=False)` : la citation est **l'article entier**, espaces
  normalisés (`re.fullmatch`) ; au JORF seulement, « Art. 12. - » peut la précéder (le n° 98-809
  le porte). Elle sert à `ENTREES_EN_VIGUEUR`, au LEGI et au JORF.
- `_est_de_phrases_entieres(citation, texte)` : pour `DATES_D_UN_AUTRE_ARTICLE`, dont les
  citations sont une ou plusieurs phrases d'un article qui en compte d'autres (quatre sur cinq
  sont dans ce cas, lues une à une), la citation commence à un début de phrase, finit à un point
  et à une fin de phrase.

**Le test d'abord, vu rouge puis vert.** `test_la_garde_des_citations_refuse_une_citation_tronquee`
et `test_la_garde_d_un_autre_article_refuse_une_phrase_coupee` : la citation du n° 2021-1818 coupée
exprès (la première phrase seule ; sans son point ; la seconde seule ; sans ses derniers mots ; sans
son début) ; l'article entier, avec ou sans « Art. 12. - » au JORF, est accepté. Rouge d'abord :
avec l'ancienne garde, la première phrase seule du n° 2021-1818 était acceptée (essai en
mémoire : `True`). Puis, la garde resserrée, les deux tests passent, et
`test_chaque_date_lue_a_la_main_est_citee_mot_pour_mot_dans_son_texte` (l'index présent) échoue sur
le seul n° 2021-1818 tant que la citation n'est pas l'article entier, puis passe.

**Contrôle des 46 décrets de B6** (script écrit ici, non celui de B6) : la citation est égale à
l'article entier du LEGI pour 45 ; le n° 2021-1818 seul faisait exception. Au JORF, elle est égale
à l'article pour 44 et précédée de « Art. 12. - » pour le n° 98-809 ; le 46e est encore le
n° 2021-1818.

## 2. Le n° 2011-1140 : daté du 1er octobre 2011 (écart 2)

**Ce que je lis.** Art. 35 (`LEGIARTI000024581626`, une seule version, du 2011-10-01 ;
`JORFARTI000024580614`), JO du 23 septembre 2011 (`JORFTEXT000024580517`) : « Le présent décret
prend effet à compter du 1er jour du mois qui suit sa publication. » Les tableaux : art. 21
(`LEGIARTI000024581630`) et art. 22 (`LEGIARTI000024581632`), « I. ― A la date d'entrée en
vigueur du présent décret, les bibliothécaires adjoints spécialisés […] » et « […] les assistants
des bibliothèques […] sont intégrés et reclassés […] conformément au tableau de correspondance
suivant ». Les mots ne sont pas les mêmes (« prend effet » ; « entrée en vigueur »).

**Les 39 articles du décret au LEGI, versions comprises, relus** pour « entre(nt) en vigueur »,
« prend(nent) effet », « produit effet », « rétroactiv », « applicab » : l'art. 35 est la seule
clause qui dise quand le décret s'applique ; ses art. 25 et 26 parlent de « la date de publication
du présent décret » (deux dates que le décret distingue) ; aucun article ne fixe une autre date.

**Le calcul, à la main.** Publié le 23 septembre 2011 : le mois de la publication est septembre ;
« le mois qui suit » est octobre ; son 1er jour est le **1er octobre 2011**.

**Les deux lectures.** (1) « la date d'entrée en vigueur du présent décret » est la date que
l'art. 35 fixe, le 1er octobre 2011 : le décret n'a pas d'autre clause de date, et l'art. 35 est
sans objet pour les tableaux si ce n'est pas elle. (2) « l'entrée en vigueur » est une autre date,
la règle générale de l'index (« à la date qu'ils fixent ou, à défaut, le lendemain de leur
publication », R-B7 § 2), soit le 24 septembre 2011 : aucun texte de l'index ne la donne. Pour la
lecture (1) : le texte au JORF a pour notice « Entrée en vigueur : le 1er octobre 2011 »
(`JORFTEXT000024580517`) ; les versions des art. 21 et 22 s'ouvrent au LEGI le 2011-10-01 ; le Noyau
RH (`etat/textes.csv`, texte 926) porte `effet` 2011-10-01 et `publication` 2011-09-23. **J'écris
le 1er octobre 2011**, lecture (1) : c'est la date que la notice, le LEGI et le Noyau RH
donnent, et aucune source ne donne l'autre. L'équivalence « prend effet » = « entrée en vigueur » est la mienne,
déduite de la structure du décret (une seule clause de date), non un mot du texte : la garde ne
l'admet que pour les décrets de `PRISES_D_EFFET` (ici ce seul décret) et vérifie à l'index que
nul autre article du décret ne dit quand il s'applique. Revenir en arrière, c'est retirer les
deux articles de `DATES_DU_DECRET` et le décret d'`ENTREES_EN_VIGUEUR`.

**Le test d'abord.** `test_un_tableau_date_de_l_entree_en_vigueur_de_son_decret_prend_la_date_qu_il_fixe`
attend « 2011-10-01 » aux deux articles (vu rouge : `effet` vide), puis la donnée ; la garde
(`PRISES_D_EFFET`) est jouée à l'index.

**Ce que le chaînage en fait.** Les six groupes du n° 2011-1140 restent déclarés, pour une autre
raison : « le libellé ne se coupe pas en deux grades des corps 00050 du Noyau RH (n° 92-30), en
vigueur la veille et le jour du 2011-10-01 » (trois groupes), « […] des corps 00249 du Noyau RH
(n° 2001-326) […] » (trois groupes), au lieu de « la phrase […] n'écrit pas la date ». Les
tableaux déclarés faute de date passent de 126 à 124 (126 − 2) ; les rattachés restent 19.

**Le n° 2011-215** (« prennent effet », comme le n° 2011-1140) reste dans les 67 tableaux à lire
décret par décret : à rouvrir avec sa notice et sa clause entière. Ne pas se servir de la ligne 5896
de `etat/textes.csv`, incohérente avec son titre (R-B7 § 5).

## 3. Le n° 2023-1336 : la preuve montre que les échelons changent (écart 3)

**Ce que le Noyau RH dit** (`etat/echelons.csv`, lu pour les trois grilles) : le 2024-01-01,
la grille 03781 reçoit un 5e échelon (23530, hors échelle BB) de 36 mois au lieu de 0, et deux
échelons neufs, 25333 (rang 6, C) et 25334 (rang 7, D) ; la grille 00541 change ses sept
échelons (rang 1 : 767 → 820 ; rang 4 : 927 → 977 et 24 → 36 mois ; rang 6 : 1027 → A ; rang 7 : A
→ B) ; la grille 00542 change ses échelons de rang 3 à 13 (rang 3 : 522 → 542 et 12 → 6 mois ; rang
13 : 996 → 1027). L'identifiant de la grille ne change pas ; son contenu, si.

**La preuve, maintenant** (colonne `preuve` de `chainage/reclassements.csv`, trois lignes de
l'art. 9, `LEGIARTI000048842644`). Quand la grille d'origine est celle d'accueil,
`Depot.changement_noyau` (`scripts/fetch/dila_legi_chainage.py`) ajoute : « la grille 00541 change
d'échelons le 2024-01-01 (Noyau RH, echelons.csv) : 05819 (rang 1) : indice brut 767, 24 mois →
indice brut 820, 24 mois ; 05818 (rang 2) : […] ». Pour 03781, par exemple : « 23530 (rang 5) :
hors échelle BB, 0 mois → hors échelle BB, 36 mois ; 25333 (rang 6) : aucune version la veille →
hors échelle C, 0 mois ; 25334 (rang 7) : aucune version la veille → hors échelle D, 0 mois ». Élève,
stagiaire et provisoires sont mis à part, comme le chaînage les met à part. Si aucun échelon ne
changeait, la preuve le dirait (« aucune version d'échelon de la grille … ne s'ouvre le … »).
L'en-tête de `reclassements.csv` le dit. Seules ces trois lignes changent : les 16 autres
rattachés ont deux grilles différentes.

**Le test d'abord, vu rouge.** `test_la_preuve_d_un_reclassement_dans_la_meme_grille_montre_que_ses_echelons_changent` :
les valeurs sont posées à la main d'après les lignes du Noyau RH (commentaire du test), et le test
confronte aussi chaque échelon ordinaire dont une version s'ouvre le 2024-01-01 à la preuve ;
`test_l_entete_dit_la_preuve_d_un_reclassement_dans_la_meme_grille` pour l'en-tête.

## 4. Les trois dates antérieures à la publication (écart 4)

Trois dates de B6 précèdent la publication de leur décret ; le texte les date ainsi :

| Décret | Clause | Date | JO |
|---|---|---|---|
| n° 98-809, art. 10 | art. 12 (`LEGIARTI000006508229`) : « Le présent décret prend effet au 1er août 1995, à l'exception des articles 3 et 4. » | 1er août 1995 | 12 septembre 1998 (`JORFTEXT000000194869`) |
| n° 98-896, art. 8 | art. 10 (`LEGIARTI000006508631`) : « Les dispositions des articles 1er, 6, 7 et 8 du présent décret sont applicables à compter du 1er août 1996. » | 1er août 1996 | 9 octobre 1998 (`JORFTEXT000000573079`) |
| n° 2017-180, art. 20 | art. 25 (`LEGIARTI000034036522`) : « Le présent décret entre en vigueur le 1er janvier 2017. » | 1er janvier 2017 | 15 février 2017 (`JORFTEXT000034035533`) |

La donnée date ce que le texte date. La validité d'un effet antérieur à la publication n'est
pas examinée ici (ce n'est pas la question de la donnée). L'en-tête de `tableaux.csv` le dit en
une phrase ; `test_l_entete_dit_les_effets_anterieurs_a_la_publication_et_l_elargissement_de_2002`
calcule la liste (les entrées d'`ENTREES_EN_VIGUEUR` dont la date précède le JO : n° 98-809 et
n° 2017-180 ; le n° 98-896 est dans `DATES_D_UN_AUTRE_ARTICLE`) et exige que l'en-tête
nomme les trois.

## 5. La file des fac-similés (écart 5)

L'en-tête de `docs/feuille_de_route/138/2026-11-05-la-file-des-fac-similes.md` dit : « Ce qu'une
fiche attend, par ordre de poids (un numéro à la fois ; une ligne lue sort de cette liste au
commit qui la lit) », avec les colonnes JO, Texte, Identifiant, Pour. Deux lignes ajoutées, aux
renvois que l'index porte au texte même : « Vous pouvez consulter le tableau dans le JO n° 211 du
12/09/1998 page 13913 à 13915 » (art. 10 du n° 98-809, `JORFARTI000001895846`) et « Vous pouvez
consulter le tableau dans le JO n° 234 du 09/10/1998 page 15305 à 15307 » (art. 8 du n° 98-896,
`JORFARTI000002094938`). Elles sont à lire au fac-similé : le texte de l'index n'est pas l'original.

## 6. L'élargissement de 2002, hors de la donnée (écart 6)

L'art. 1er du n° 2002-378 (JO du 21 mars 2002, `JORFARTI000002416455`) : « A l'article 8 du décret
du 7 octobre 1998 susvisé, les mots : « en fonctions à la date du présent décret » sont
supprimés. » ; le décret n'a que cet article et l'art. 2 d'exécution (`JORFARTI000002195228`), sans
clause d'effet. L'art. 8 du n° 98-896 a deux versions au LEGI : `LEGIARTI000006508628` (du
1996-08-01 au 2002-03-21, « Les lieutenants de port en fonctions à la date du présent décret sont
reclassés […] ») et `LEGIARTI000006508629` (depuis 2002-03-21, « Les lieutenants de port sont
reclassés […] »). La donnée ne porte que la date du tableau, le 1er août 1996. Pour l'agent que la
condition « en fonctions à la date du présent décret » excluait, deux lectures, et le texte n'en
écrit aucune : le 1er août 1996 (l'art. 10 du n° 98-896 est en vigueur, non modifié, mais vaut-il
pour l'art. 8 dans sa rédaction de 2002 ?) ; ou l'entrée en vigueur du n° 2002-378, par la règle
générale de l'époque, qui n'est pas lue (point 7). Déclaré hors de la donnée dans l'en-tête de
`tableaux.csv` (même test que le point 4).

## 7. Les 67 tableaux restants : 25 d'avant le 1er juin 2004, 42 d'après

Les 67 tableaux se retrouvent dans `tableaux.csv` (`effet` vide, phrase qui renvoie à l'entrée en
vigueur, l'effet ou la publication « du présent décret » ; la même recherche en rendait 69
avant la date du n° 2011-1140, dont ses 2 tableaux). La date de publication est celle du JORF (champ `date` du texte
signé, titre « Décret no … » pour les plus anciens) :

| Avant le 1er juin 2004 | Tableaux | JO (JORF) |
|---|---|---|
| n° 71-917 | 1 | 17 nov. 1971 (`JORFTEXT000000511420`) |
| n° 72-774 | 1 | 25 août 1972 (`JORFTEXT000000505630`) |
| n° 75-687 | 2 | 1er août 1975 (`JORFTEXT000000335036`) |
| arrêté du 21 décembre 1982 (classement et échelonnement indiciaires des personnels d'exécution des établissements d'hospitalisation, LEGITEXT000006072914) | 1 | 23 déc. 1982 (`JORFTEXT000000860003`) |
| n° 84-145 | 1 | 29 févr. 1984 (`JORFTEXT000000335616`) |
| n° 84-196 | 1 | 22 mars 1984 (`JORFTEXT000000335852`) |
| n° 84-965 | 1 | 28 oct. 1984 (`JORFTEXT000000886526`) |
| n° 86-229 | 1 | 20 févr. 1986 (`JORFTEXT000000700918`) |
| n° 87-1107 | 1 | 31 déc. 1987 (`JORFTEXT000000334479`) |
| n° 88-547 | 1 | 7 mai 1988 (`JORFTEXT000000866458`) |
| n° 90-126 | 1 | 10 févr. 1990 (`JORFTEXT000000166678`) |
| n° 90-393 | 1 | 13 mai 1990 (`JORFTEXT000000159751`) |
| n° 90-404 | 1 | 17 mai 1990 (`JORFTEXT000000707994`) |
| n° 90-405 | 2 | 17 mai 1990 (`JORFTEXT000000524911`) |
| n° 92-859 | 1 | 30 août 1992 (`JORFTEXT000000724510`) |
| n° 92-861 | 1 | 30 août 1992 (`JORFTEXT000000359140`) |
| n° 92-863 | 1 | 30 août 1992 (`JORFTEXT000000175753`) |
| n° 92-871 | 1 | 30 août 1992 (`JORFTEXT000000725321`) |
| n° 93-278 | 1 | 5 mars 1993 (`JORFTEXT000000164876`) |
| n° 98-203 | 1 | 24 mars 1998 (`JORFTEXT000000569939`) |
| n° 2000-508 | 1 | 11 juin 2000 (`JORFTEXT000000765237`) |
| n° 2001-128 | 1 | 10 févr. 2001 (`JORFTEXT000000404701`) |
| n° 2003-466 | 1 | 31 mai 2003 (`JORFTEXT000000603479`) |

**Le calcul, à la main.** Décrets d'avant juin 2004 : 71-917, 72-774, 75-687, 84-145, 84-196, 84-965,
86-229, 87-1107, 88-547, 90-126, 90-393, 90-404, 90-405, 92-859, 92-861, 92-863, 92-871, 93-278,
98-203, 2000-508, 2001-128, 2003-466 = **22 décrets, 24 tableaux** (1+1+2+1+1+1+1+1+1+1+1+1+2+1+1+1+1+1+1+1+1+1 = 24),
plus **l'arrêté** du 21 décembre 1982, 1 tableau : **25 tableaux de 23 textes**. D'après :
67 − 25 = **42 tableaux** de 57 − 23 = **34 textes**, du n° 2004-1439 (JO du 30 décembre 2004,
`JORFTEXT000000785734`) au n° 2019-1160. Aucun texte entre le 31 mai 2003 et le 30 décembre 2004 :
la limite du 1er juin 2004 ne coupe aucun décret.

**La règle d'avant juin 2004 : nommée, non écrite.** Les visas des décrets « relatifs à l'entrée
en vigueur de décrets » la nomment : « Vu le décret du 5 novembre 1870 relatif à la promulgation
des lois et décrets, notamment le deuxième alinéa de son article 2 » (ouverts : n° 98-1212 du
29 décembre 1998, `JORFTEXT000000209444`, et n° 2003-1313 du 30 décembre 2003,
`JORFTEXT000000429658`). Le texte de ce décret n'est dans **aucun des deux index** (la recherche
plein texte de « 5 novembre 1870 » ne rend que des visas, des avis de vacance de postes et la
décision n° 89-269 DC). **Je ne l'écris pas, ni le délai, ni la lecture « jour franc » : elle
attend le propriétaire**, qui peut lire à Légifrance, à sa version d'avant 2004, le décret du
5 novembre 1870 relatif à la promulgation des lois et décrets (art. 2) et l'art. 1er du code civil
d'avant le 1er juin 2004. Un décret d'avant juin 2004 qui ne fixe pas lui-même sa date (B6, point 4 : « la plupart » n'ont
pas de clause globale trouvée, chacun se relit en entier) ne se date donc pas sans elle. Pour
les 42 d'après, la règle est celle du point 2 de la note de B6 (leur clause, ou à défaut le
lendemain de leur publication), que R-B7 n'a lue qu'aux lois organiques de l'outre-mer, non à
l'art. 1er du code civil.

## 8. Ce qui bouge

- `scripts/fetch/dila_legi_reclassements.py` : `ENTREES_EN_VIGUEUR` (47 décrets : le n° 2011-1140
  ajouté, la clause du n° 2021-1818 entière), `DATES_DU_DECRET` (62 articles, 64 tableaux) ;
  l'en-tête de `tableaux.csv` (point 4, point 6).
- `data/reference/grilles/reclassements/tableaux.csv` : `effet` de deux tableaux (n° 2011-1140,
  art. 21 et 22, de vide à 2011-10-01), l'en-tête ; rien d'autre. Tableaux sans `effet` : 298 → 296.
- `scripts/fetch/dila_legi_chainage.py`, `data/reference/grilles/chainage/reclassements.csv` : la
  preuve des trois lignes du n° 2023-1336 (point 3), l'en-tête, la `raison` de six groupes du
  n° 2011-1140 (point 2). Rattachés : 19 ; déclarés : 843 (inchangés). Tableaux déclarés faute de
  date : 126 → 124.
- `docs/feuille_de_route/138/2026-11-05-la-file-des-fac-similes.md` : deux lignes (point 5).
- Le paquet : `python scripts/construire_donnees.py` ; `moteur/donnees.json` ne change pas (le
  paquet ne lit que `reclassements/lignes.csv`, intact).
- Tests neufs, vus rouges puis verts : `test_la_garde_des_citations_refuse_une_citation_tronquee`,
  `test_la_garde_d_un_autre_article_refuse_une_phrase_coupee` (point 1), les deux du point 3,
  `test_l_entete_dit_les_effets_anterieurs_a_la_publication_et_l_elargissement_de_2002`
  (points 4 et 6) ; resserrés ou mis à jour : `test_chaque_date_lue_a_la_main_est_citee_mot_pour_mot_dans_son_texte`
  (l'article entier ; `PRISES_D_EFFET`), `test_un_tableau_date_de_l_entree_en_vigueur_de_son_decret_prend_la_date_qu_il_fixe`
  (le n° 2011-1140), `test_aucune_phrase_restee_sans_date_ne_s_ouvre_sur_une_date` (126 → 124). Lancés : `tests/test_reclassements.py`, `tests/test_chainage_grilles.py`,
  `tests/test_donnees.py`, `tests/test_syntaxe_ancien_python.py` en entier, 234 passés ;
  `python -m pytest -m rapide`, 4 509 passés, 6 ignorés, 11 rouges (tous
  `tests/test_pages_en_dossier.py`, pages que GitHub refait) ; `PRESOMPTIONS_DECALEES=1 python -m
  pytest -m rapide`, 4 304 passés, 211 ignorés, les mêmes 11.

## 9. Candidats (non corrigés)

- **Le n° 2011-215** (« prennent effet ») : à lire en entier, avec sa notice au JORF.
- **Le n° 2015-1275, art. 35** : que `lignes.csv` suive le tableau rétabli par le rectificatif du
  24 octobre 2015 (R-B7), non vérifié ici.
- **Les citations des 4 autres `DATES_D_UN_AUTRE_ARTICLE`** sont des phrases d'un article qui en
  compte d'autres : la garde dit qu'elles sont entières, non qu'aucune autre phrase du même
  article ne les contredit ; B5-bis les avait relues une à une.

Sources : index LEGI et JORF de la DILA (identifiants cités dans le texte, lus pendant la session) ;
Noyau RH, `textes.csv` et `echelons.csv` du dépôt ; `tests/` du dépôt rejoués.
