# Relecture des corrections de R-B2 (file B2-bis)

File R-B2-bis, le 3 novembre 2026 : relecture indépendante des dix commits de la session
B2-bis (fa24baa à 260182e, note `2026-11-03-corrections-de-la-relecture-r-b2.md`), qui
répondent à la relecture R-B2 (`2026-11-03-relecture-durees-d-echelon.md`). Rien n'est repris
de la session ni de mémoire : chaque article a été rouvert ici. Les sources : l'index LEGI
publié du dépôt, récupéré sans reconstruction (`dila_index.py legi --recuperer`, à jour de
l'incrément 20261102-213929, le même que B2-bis et R-B2), interrogé par
`dila_cherche.py legi` (`--texte`, `--num … --titre`) et directement dans sa table `doc` (dates
de version, recherche de formules) ; l'index JORF publié (`--recuperer`, à jour du
3 novembre 2026, incrément 20261103-002311) ; le Noyau RH déjà au dépôt
(`data/reference/grilles/etat/`). Les fichiers de B2-bis n'ont pas bougé sur `main` depuis
260182e (vérifié au dernier `main`, aa6721d). Rien n'a été modifié : ni donnée, ni test, ni
script ; les mutations des tests (point 7) ont été faites dans la copie, puis effacées
(`git checkout`, `git status` propre).

**Verdict.** Les **32 lignes** tirées au hasard (22 nées des corrections, 10 inchangées) ont
toutes le bon grade, le bon échelon, la bonne durée, les bonnes dates et le bon article :
**32 sur 32 conformes**. Les sept versions ôtées sont bien « jamais en vigueur » au LEGI, et
la version qui les remplace est la bonne ; aucune autre n'est restée dans les tableaux lus.
Les 14 tableaux rentrés au « II.- » (28 versions) concordent tous avec leur texte. Les comptes
se recomptent (727, 340, 777, 14 506, 1 249, 750, 409, 25, 97, 441 771). Les 14 tests ajoutés
tirent leurs valeurs des textes, recopiés mot pour mot, et mordent (16 mutations sur 16).
La certification passe sans écart, et le paquet ne bouge pas. **Écarts**, tous **faibles**,
aucun ne fausse une valeur des données : le 22e refus est juste, mais pour une autre raison
que celle écrite — c'est la consolidation du LEGI qui perd le 5e échelon, le décret publié au
JORF l'écrit (point 3) ; deux des 26 tableaux « sans règle du quart » en ont une, sous une
autre forme, dans un autre article de leur décret (point 5) ; une coquille de date dans le
commentaire d'un test (point 7) ; « 38 versions » pour 39 (point 6). Hors du périmètre de
B2-bis, un trou hérité de B2 : des articles à tableau de durées que le lecteur ne sélectionne
pas, ni lus ni consignés (point 9). Aucun **grave**, aucun **moyen**.

## 1. Les sept versions jamais en vigueur

Pour chacune, l'histoire de l'article (`dila_cherche.py legi --num <article> --titre
<numéro>`), qui la marque « (jamais en vigueur) », et la version qui la suit, ouverte.

| Texte, article | Version ôtée, ses dates au LEGI | La version en vigueur à ces dates, ouverte ici | Verdict |
|---|---|---|---|
| n° 99-669, art. 17 | LEGIARTI000034810141, du 1er janvier 2021 au 1er juin 2020 | LEGIARTI000041916038, du 1er janvier 2021 au 1er janvier 2026 : « Conformément à l'article 39 du décret n° 2017-1736 du 21 décembre 2017, les présentes dispositions entrent en vigueur le 1er janvier 2021 » ; ses 25 lignes égales au texte, une à une (dont « Directeur technique de classe exceptionnelle Echelon spécial - 5e échelon - 4e échelon 3 ans 3e échelon 2 ans 6 mois ») | conforme |
| n° 83-1260, art. 34 | LEGIARTI000027940471, du 8 janvier 1984 au 4 août 1980 | aucune avant LEGIARTI000027940483, du 4 août 1990 au 3 février 2002 ; voir le point 2 | conforme |
| n° 91-868, art. 7 | LEGIARTI000035606585, du 1er janvier 2021 au 19 novembre 2018 | LEGIARTI000037623417, du 1er janvier 2021 au 1er février 2024 : « Conformément à l'article 42 du décret n° 2018-999 du 16 novembre 2018, ces dispositions entrent en vigueur le 1er janvier 2021 » ; ses 36 lignes égales au texte | conforme |
| n° 91-290, art. 14-4 | LEGIARTI000025845550, du 1er septembre 2014 au 30 août 2012, seule version | aucune ; au JORF, le décret n° 2012-999 du 27 août 2012 (JO du 29 août 2012, JORFARTI000026321289), art. 2 : « … le décret n° 91-290 du 20 mars 1991 susvisé … sont rétablis dans leur rédaction en vigueur à la date de publication du décret du 7 mai 2012 », décret n° 2012-702 qui avait créé l'article : il ne s'est jamais appliqué | conforme |
| n° 2014-923, art. 25 | LEGIARTI000032578591, du 1er janvier 2017 au même jour | LEGIARTI000037468710, depuis le 1er janvier 2017 : « 4e échelon provisoire 2 ans 3e échelon provisoire 2 ans 2e échelon provisoire 2 ans 1er échelon provisoire 2 ans » ; la version ôtée n'écrit que les trois derniers | conforme |
| n° 2014-1455, art. 22 | LEGIARTI000052465286, du 15 décembre 2025 au même jour | LEGIARTI000053027219, depuis le 15 décembre 2025 ; ses 88 lignes numérotées égales au texte, dans l'ordre | conforme |
| n° 92-851, art. 14 | LEGIARTI000034434459, du 1er janvier 2017 au même jour | LEGIARTI000037468701, depuis le 1er janvier 2017 ; ses 20 lignes numérotées égales au texte, et l'échelon spécial du médecin hors classe ; le « II.- » qui suit n'a pas fait de ligne | conforme |

Les trois autres lignes de `non_lus.csv` au même motif (n° 98-343, art. 39,
LEGIARTI000006506809 ; n° 93-569, art. 12, LEGIARTI000006470899 ; n° 2010-1239, art. 24,
LEGIARTI000035604145) ont, au LEGI, une fin antérieure à leur début. Aucune version de la
colonne `versions` de `tableaux.csv` n'a une fin antérieure ou égale à son début (recherche sur
toutes, dans l'index), et aucune période de tableau n'est vide.

## 2. Le n° 83-1260, art. 34, au JORF

Le texte qui a remplacé l'article est le **décret n° 90-685 du 27 juillet 1990**, publié au
JORF n° 178 du 3 août 1990 (JORFTEXT000000350640), dont l'**article 5** (JORFARTI000000984252)
écrit : « Le tableau de l'article 34 du décret du 30 décembre 1983 susvisé est remplacé par le
tableau ci-dessous : … Vous pouvez consulter le tableau dans le JO no 0178 du 03/08/1990 ».
Aucun article de ce décret ne fixe une autre date : ses articles 1er à 42 sont dans l'index
(le 41 est transitoire, sur l'âge d'accès ; le 42 est l'article d'exécution) et le mot
« vigueur » n'y paraît qu'une fois, au 41 (JORFARTI000001895119), pour les candidats déjà
présentés à un concours, qui peuvent « rester soumis aux dispositions en vigueur avant ». Ses visas citent le n° 83-1260 « modifié par le décret no 88-1072
du 24 novembre 1988 et le décret no 89-74 du 4 février 1989 » ; au JORF, le premier modifie
les articles 104 et 185, le second ces deux mêmes articles (« la proportion de 28 % visée aux
art. 104 et 185 … est portée à 30 % ») : aucun ne touche l'article 34. Le texte d'origine a
paru au JORF du 7 janvier 1984 (JORFTEXT000000316777).

*La période qui vaut*, d'après le JORF : la rédaction d'origine, du 8 janvier 1984 (date du
LEGI) au **4 août 1990** (fin exclue, comme dans `tableaux.csv`), jour où le LEGI fait
commencer la version suivante, au lendemain du JO du 3 août 1990 qui la publie. La fin « 4 août 1980 » du LEGI est une coquille pour 1990 : aucun texte
publié entre 1984 et 1990 ne modifie l'article. *Non vérifié, faute de texte* : la rédaction
même des deux tableaux. Les articles du JORF de 1984 sont vides dans l'index, et le tableau de
1990 n'est qu'en image (« Vous pouvez consulter le tableau dans le JO ») ; les 15 lignes de
LEGIARTI000027940471 ne se recoupent donc qu'au LEGI. Rien n'est rendu ici : la question au
propriétaire reste posée.

## 3. Le « II.- » qui arrête le tableau, et le 22e refus

*Les 14 tableaux.* Le commit e0713a5 fait naître 14 tableaux, soit 28 versions (1 + 4 + 4 + 1 +
2 + 1 + 3 + 2 + 2 + 2 + 1 + 1 + 2 + 2), dont les 21 refus « un échelon manque » (n° 72-583,
art. 6 : 4 ; n° 72-580, art. 13 : 4 ; n° 90-680, art. 24 : 7 ; n° 93-752, art. 17 : 3 ;
n° 65-383, art. 10-7 : 2 ; n° 96-1113, art. 14 : 1) et les 7 « une phrase coupe le tableau »
(n° 90-90, art. 18 : 4 ; n° 92-778, art. 31-6 et 32 : 3). *Contre-lecture* : chaque version
ouverte, sa suite (échelon, durées) relue par un découpage écrit ici, sans le lecteur du dépôt
(le script `comparer.py`, plus bas), puis comparée aux lignes : **les 28 sont égales**, de la
première ligne au « II.- » ; les seuls échelons hors des lignes sont ceux que nomment les
paragraphes II et III (« dans les 6e et 8e échelons de la classe normale… »), sans durée. Les
périodes ont été relues dans l'histoire de chaque article : toutes égales à celles du LEGI.

*Le 22e refus.* N° 96-1113, art. 14, version du 1er janvier 2021 (LEGIARTI000042571828), au
LEGI : « Professeur technique hors classe 7e échelon - 6e échelon 3 ans 4e échelon 2 ans 6 mois
3e échelon 2 ans 6 mois 2e échelon 2 ans 1er échelon 2 ans ». La consolidation du LEGI saute
bien le 5e échelon, et le refus est juste : le lecteur n'invente pas une ligne. Mais le décret
publié ne le saute pas. Au JORF du 25 novembre 2020, le **décret n° 2020-1435 du 23 novembre
2020, art. 8** (JORFARTI000042558759) : « Dans le tableau de l'article 14 du même décret, les
lignes relatives au grade de professeur technique hors classe sont remplacées par les lignes
suivantes : « Professeur technique hors classe 7e échelon - 6e échelon 3 ans **5e échelon
3 ans** 4e échelon 2 ans 6 mois 3e échelon 2 ans 6 mois 2e échelon 2 ans 1er échelon 2 ans » » ;
son art. 11 (JORFARTI000042558764) : « Les dispositions du chapitre III entrent en vigueur le
1er janvier 2021 » ; son art. 6 porte les échelons du grade de six à sept. **Écart faible** :
la phrase de B2-bis « saute le 5e échelon » vaut pour le LEGI, non pour le texte ; le tableau
en vigueur depuis le 1er janvier 2021 se lit au JORF, à relire à la main avec les autres refus.

## 4. L'échantillon : trente-deux lignes

Le tirage, par un script du bloc-notes de la session, hors du dépôt, lancé depuis la racine du
dépôt à 260182e ; graine **202611031**. Une ligne « née » est une ligne de 260182e dont le
contenu (texte, article, tableau, groupe, échelon, rang, durées, condition) n'est pas à
b121b49 : 545 lignes, en six catégories — les 14 tableaux rentrés au « II.- » (A, 273 lignes,
dont les 5 lignes « spécial » qu'acccb16 leur a ajoutées), les échelons spéciaux nés ailleurs
(B, 24), les tableaux « Avant le » (C, 16), les lignes dont le grade a perdu la case
« Spécial » (D, 122), le groupe des SDIS (E, 90), la version du n° 92-851 qui remplace celle
jamais en vigueur (F, 20). Aucune n'est des militaires. Les inchangées : 13 961 lignes.

```python
"""Échantillon de la relecture R-B2-bis, graine 202611031 : 22 lignes nées des corrections
de B2-bis (b121b49..260182e), par catégorie, et 10 lignes inchangées, par versant.
Lancé depuis la racine du dépôt, à 260182e."""
import csv, random, subprocess
D = 'data/reference/grilles/durees/'
def lire(p, rev):
    txt = subprocess.run(['git', 'show', f'{rev}:{D}{p}'], capture_output=True, text=True).stdout.splitlines()
    return list(csv.DictReader(l for l in txt if not l.startswith('#')))
C = ('texte', 'article', 'tableau', 'groupe', 'echelon', 'rang', 'duree', 'duree_moyenne',
     'duree_minimale', 'duree_maximale', 'condition')
avant = {tuple(l[c] for c in C) for l in lire('lignes.csv', 'b121b49')}
lignes = lire('lignes.csv', '260182e')
tx = {t['texte']: t for t in lire('textes.csv', '260182e')}
tb = {(t['article'], t['tableau']): t for t in lire('tableaux.csv', '260182e')}
II = {t['article'] for t in tb.values() if t['article'] in (
    'LEGIARTI000042571613 LEGIARTI000034779104 LEGIARTI000034779361 LEGIARTI000034798803 '
    'LEGIARTI000034809942 LEGIARTI000048031531 LEGIARTI000034947965 LEGIARTI000034948501 '
    'LEGIARTI000047941733 LEGIARTI000034749579 LEGIARTI000048031577 LEGIARTI000041912415 '
    'LEGIARTI000041912896 LEGIARTI000034743786').split()}  # les 14 tableaux rentrés (e0713a5)
def versant(l): return tx[l['texte']]['versant']
def cat(l):
    n = tx[l['texte']]['numero']
    if l['article'] in II: return 'A_II'
    if l['echelon'] == 'special': return 'B_special'
    if n in ('2014-923', '2016-336'): return 'C_avant'
    if n == '2016-2003': return 'E_emploi'
    if n == '92-851': return 'F_jamais'
    return 'D_libelle'
nees = [l for l in lignes if tuple(l[c] for c in C) not in avant]
inchangees = [l for l in lignes if tuple(l[c] for c in C) in avant]
rng = random.Random(202611031)
QUOTAS = [('A_II', None, 8), ('B_special', 'etat', 3), ('B_special', 'hospitaliere', 1),
          ('B_special', 'territoriale', 1), ('C_avant', None, 2), ('D_libelle', 'etat', 1),
          ('D_libelle', 'hospitaliere', 1), ('D_libelle', 'territoriale', 1), ('E_emploi', None, 2),
          ('F_jamais', None, 2)]
tirage = []
for c, v, n in QUOTAS:
    pool = [l for l in nees if cat(l) == c and (v is None or versant(l) == v)]
    tirage += [(c, l) for l in rng.sample(pool, n)]
for v, n in (('etat', 3), ('territoriale', 3), ('hospitaliere', 2), ('militaires', 2)):
    tirage += [('inchangee', l) for l in rng.sample([l for l in inchangees if versant(l) == v], n)]
for i, (c, l) in enumerate(tirage, 1):
    t = tx[l['texte']]; b = tb[(l['article'], l['tableau'])]
    print('|'.join([str(i), c, versant(l), t['numero'], b['numero'], l['article'], l['tableau'], l['ligne'],
                    l['groupe'], l['echelon'], l['rang'], 'u=' + l['duree'], 'moy=' + l['duree_moyenne'],
                    'min=' + l['duree_minimale'], 'max=' + l['duree_maximale'], 'cond=' + l['condition'][:30],
                    b['debut'], b['fin'], b['versions']]))
```

Pour chaque ligne : l'article ouvert à chacune des versions que le tableau dit le redire
(colonne `versions`), la fenêtre du texte après le grade, et l'histoire de l'article au LEGI
pour les dates ; puis la suite entière du tableau comparée par `comparer.py`. « T/L » : le
tableau et la ligne dans `lignes.csv`. Les durées sont en mois.

| # | Catégorie | Versant | Texte, article (versions) | T/L | Grade, échelon | Au dépôt | Au texte, au LEGI | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | A, « II.- » | État | n° 92-778, art. 31-6 (LEGIARTI000034749579, LEGIARTI000044270249) | 1/13 | Certifié classe normale, 10e | 48 ; du 1er septembre 2017 au 1er septembre 2023 | « 10e échelon 4 ans », dans les deux versions ; du 1er septembre 2017 au 29 octobre 2021, puis au 1er septembre 2023 | conforme |
| 2 | A | État | n° 90-90, art. 18 (LEGIARTI000048031531) | 1/17 | Professeur de lycée professionnel agricole de classe normale, 7e | 36 ; depuis le 1er septembre 2023 | « 7e échelon 3 ans » ; en vigueur depuis le 1er septembre 2023 | conforme |
| 3 | A | État | même version | 1/22 | même grade, 2e | 12 | « 2e échelon 1 an » | conforme |
| 4 | A | État | n° 90-90, art. 18 (LEGIARTI000034798803) | 1/12 | même grade, 11e | sans durée ; du 1er septembre 2017 au 1er janvier 2021 | « 11e échelon - » ; mêmes dates | conforme |
| 5 | A | État | n° 93-752, art. 17 (LEGIARTI000041912415) | 1/2 | Professeur technique hors classe, 6e | 36 ; du 1er septembre 2017 au 1er janvier 2021 | « 6e échelon 3 ans » ; mêmes dates | conforme |
| 6 | A | État | n° 90-680, art. 24 (LEGIARTI000047941733, LEGIARTI000047971090) | 1/1 | Professeur des écoles de classe exceptionnelle, 5e | sans durée ; depuis le 6 août 2023 | « classe exceptionnelle 5e échelon ― 4e échelon 3 ans », sans échelon spécial, dans les deux versions ; du 6 au 16 août 2023, puis en vigueur | conforme |
| 7 | A | État | n° 93-752, art. 17 (LEGIARTI000041912896, LEGIARTI000044268231) | 1/12 | Professeur technique de classe normale, 6e | 36 ; du 1er janvier 2021 au 29 décembre 2024 | « 6e échelon 3 ans », dans les deux ; du 1er janvier au 29 octobre 2021, puis au 29 décembre 2024 | conforme |
| 8 | A | État | n° 90-680, art. 24 (mêmes versions que 6) | 1/14 | Professeur des écoles de classe normale, 10e | 48 | « 10e échelon 4 ans » | conforme |
| 9 | B, spécial | État | n° 70-738, art. 10-6 (LEGIARTI000034839812, LEGIARTI000044268412) | 1/1 | Conseiller principal d'éducation de classe exceptionnelle, spécial (rang 5) | sans durée ; du 1er janvier 2021 au 6 août 2023 | « Spécial ― 4e échelon ― 3e échelon 2 ans 6 mois » ; du 1er janvier au 29 octobre 2021, puis au 6 août 2023 | conforme |
| 10 | B | État | n° 72-581, art. 32 (LEGIARTI000034779238, LEGIARTI000038669104, LEGIARTI000041436490) | 1/1 | Certifié de classe exceptionnelle, spécial (rang 5) | sans durée ; du 1er septembre 2017 au 1er janvier 2021 | « Spécial ― 4e échelon ― », dans les trois ; du 1er septembre 2017 au 17 juin 2019, au 1er janvier 2020, au 1er janvier 2021 | conforme |
| 11 | B | État | n° 72-581, art. 32 (LEGIARTI000034840090, LEGIARTI000044268483) | 1/1 | même grade, spécial (rang 5) | sans durée ; du 1er janvier 2021 au 6 août 2023 | « Spécial ― 4e échelon ― » ; mêmes dates | conforme |
| 12 | B | Hospitalière | n° 2001-1207, art. 11 (LEGIARTI000037109006) | 1/1 | Attaché hors classe, spécial (rang 7) | sans durée ; depuis le 1er janvier 2021 | « Spécial - 6e échelon - 5e échelon 3 ans » ; en vigueur depuis le 1er janvier 2021 | conforme |
| 13 | B | Territoriale | n° 87-1099, art. 17 (LEGIARTI000033857328) | 1/1 | Attaché hors classe, spécial (rang 7) | sans durée ; depuis le 1er janvier 2021 | « Spécial 6e échelon - 5e échelon 3 ans » ; en vigueur depuis le 1er janvier 2021 | conforme |
| 14 | C, « Avant le » | Territoriale | n° 2014-923, art. 25 (LEGIARTI000029383847) | 1/1 | Avant le 1er échelon de la classe supérieure, 4e provisoire | maximale 24, minimale 22 ; du 1er septembre 2014 au 15 mai 2016 | « DURÉE MAXIMALE DURÉE MINIMALE Avant le 1er échelon de la classe supérieure 4e échelon provisoire 2 ans 1 an 10 mois » ; mêmes dates | conforme |
| 15 | C | Territoriale | n° 2016-336, art. 25 (LEGIARTI000032578363) | 1/2 | Avant le 1er échelon du grade de cadre de santé de 1re classe, 1er provisoire | 12 ; depuis le 15 mai 2016 | « 1er échelon provisoire 1 an » ; en vigueur depuis le 15 mai 2016 | conforme |
| 16 | D, libellé | État | n° 92-1189, art. 23 (LEGIARTI000034849077, LEGIARTI000044268765) | 1/4 | Professeur de lycée professionnel de classe exceptionnelle, 2e | 24 ; du 1er janvier 2021 au 6 août 2023 | « 2e échelon 2 ans » ; du 1er janvier au 29 octobre 2021, puis au 6 août 2023 | conforme |
| 17 | D | Hospitalière | n° 2001-1207, art. 11 (LEGIARTI000037101278) | 1/4 | Attaché hors classe, 4e | 30 ; du 1er janvier 2018 au 1er janvier 2021 | « 4e échelon 2 ans 6 mois » ; mêmes dates | conforme |
| 18 | D | Territoriale | n° 87-1099, art. 17 (LEGIARTI000033857328) | 1/5 | Attaché hors classe, 3e | 24 ; depuis le 1er janvier 2021 | « 3e échelon 2 ans » | conforme |
| 19 | E, SDIS | Territoriale | n° 2016-2003, art. 13 (LEGIARTI000045657613) | 4/6 | Directeur départemental adjoint des services d'incendie et de secours de catégorie A, 3e | 24 ; depuis le 17 avril 2022 | quatrième tableau, « … adjoint des services d'incendie et de secours de catégorie A : ÉCHELONS DURÉE 8e échelon - … 3e échelon 2 ans » ; en vigueur depuis le 17 avril 2022 | conforme |
| 20 | E | Territoriale | n° 2016-2003, art. 13 (LEGIARTI000033792629) | 6/6 | Directeur départemental adjoint du service d'incendie et de secours de catégorie C, 3e | 24 ; du 1er janvier 2017 au 17 avril 2022 | sixième tableau, « … adjoint du service … de catégorie C : ÉCHELONS DURÉE 8e échelon - … 3e échelon 2 ans » ; mêmes dates | conforme |
| 21 | F, n° 92-851 | Territoriale | n° 92-851, art. 14 (LEGIARTI000037468701) | 1/15 | Médecin de 2e classe, 7e | 30 ; depuis le 1er janvier 2017 | « 7e échelon 2 ans 6 mois » ; en vigueur depuis le 1er janvier 2017 | conforme |
| 22 | F | Territoriale | même version | 1/5 | Médecin hors classe, 2e | 24 | « 2e échelon 2 ans » | conforme |
| 23 | inchangée | État | n° 56-448, art. 9 (LEGIARTI000032192685) | 1/18 | Chef dessinateur, 5e | 36 ; depuis le 29 février 2016 | « Chef dessinateur 2e, 3e, 4e, 5e, 6e et 7e échelons 3 ans » ; en vigueur depuis le 29 février 2016 | conforme |
| 24 | inchangée | État | n° 92-1432, art. 13 (LEGIARTI000041792225) | 1/13 | Pharmacien inspecteur de santé publique, 8e | 30 ; du 10 avril 2020 au 1er août 2025 | « 8e échelon 2 ans 6 mois » ; mêmes dates | conforme |
| 25 | inchangée | État | n° 97-511, art. 14 (LEGIARTI000035653463) | 1/13 | Attaché économique principal, 4e | 24 ; du 1er janvier 2017 au 1er janvier 2021 | « 4e échelon 2 ans » ; mêmes dates | conforme |
| 26 | inchangée | Territoriale | n° 2016-336, art. 18 (LEGIARTI000032578361) | 1/17 | Cadre de santé de 2e classe, 10e | sans durée ; du 15 mai 2016 au 1er janvier 2022 | « 10e échelon - » ; mêmes dates | conforme |
| 27 | inchangée | Territoriale | n° 2013-262, art. 21 (LEGIARTI000032615908) | 1/10 | Technicien paramédical de classe normale, 7e | 48 ; du 1er janvier 2017 au 1er septembre 2022 | « 7e échelon 4 ans » ; mêmes dates | conforme |
| 28 | inchangée | Territoriale | n° 2012-1420, art. 18 (LEGIARTI000032578450) | 1/5 | Infirmier en soins généraux hors classe, 6e | 42 ; du 1er janvier 2017 au 1er janvier 2022 | « 6e échelon 3 ans 6 mois » ; mêmes dates | conforme |
| 29 | inchangée | Hospitalière | n° 2001-1207, art. 11 (LEGIARTI000037109006) | 1/27 | Attaché, 2e | 24 ; depuis le 1er janvier 2021 | « 2e échelon 2 ans » | conforme |
| 30 | inchangée | Hospitalière | n° 2014-101, art. 11 (LEGIARTI000032572791) | 2/7 | assistant socio-éducatif principal, 5e | 24 ; du 1er janvier 2017 au 1er février 2019 | « 5e échelon 2 ans » ; mêmes dates | conforme |
| 31 | inchangée | Militaires | n° 2010-1239, art. 24 (LEGIARTI000052465332) | 1/77 | Ingénieur principal, échelle de solde n° 1, 3e | 12 ; depuis le 15 décembre 2025 | « Echelle de solde n° 1 … 13 e échelon 12 e échelon 1 an … 3 e échelon 1 an », sous l'ingénieur principal | conforme |
| 32 | inchangée | Militaires | n° 2008-931, art. 17 (LEGIARTI000052465270) | 1/30 | Chef de musique hors classe, échelle de solde n° 1, 8e | 12 ; depuis le 15 décembre 2025 | « Echelle de solde n° 1 … 9 e échelon 1 an 8 e échelon 1 an » | conforme |

La comparaison de la suite entière (`comparer.py`) a donné, pour chacun de ces tableaux, toutes
les lignes numérotées égales au texte, dans l'ordre. Deux fois, le découpage d'ici a manqué un
échelon que le dépôt a lu juste : « 6eéchelon », sans espace (n° 97-511, art. 14 : le dépôt
écrit 30, le texte « 2 ans 6 mois ») ; et les échelons provisoires (n° 2014-923, n° 2016-336),
relus à la main ci-dessus. Le tableau du n° 2016-336, art. 25, du 1er avril au 15 mai 2016
(LEGIARTI000032276890), que acccb16 fait lire, l'a été aussi : « DURÉE MAXIMALE DURÉE
MINIMALE 2e échelon provisoire 2 ans 1 an 10 mois 1er échelon provisoire 1 an 1 an », soit 24
et 22, 12 et 12, comme au dépôt.

```python
"""comparer.py ARTICLE [TABLEAU [VERSION]] : compare, échelon par échelon, la suite
(échelon, durées) lue dans le texte du LEGI par un découpage indépendant, et les lignes du
dépôt (celles du tableau ARTICLE ; le texte est celui de VERSION, par défaut ARTICLE)."""
import csv, re, subprocess, sys
D = 'data/reference/grilles/durees/'
art = sys.argv[1]; tb = sys.argv[2] if len(sys.argv) > 2 else None
ver = sys.argv[3] if len(sys.argv) > 3 else art
txt = subprocess.run([sys.executable, 'scripts/fetch/dila_cherche.py', 'legi', '--texte', ver],
                     capture_output=True, text=True).stdout.split('\n', 3)[3]
txt = txt.replace(' ', ' ').replace(' ', ' ')
DUR = re.compile(r'\s*(?:(\d+)\s*ans?(?:\s*(?:et\s*)?(\d+)\s*mois)?|(\d+)\s*mois|(-|―|–|—))')
ECH = re.compile(r'(\d+)\s?(?:e|er|re|ème)\s+[ée]chelon', re.I)
seq = []
for m in ECH.finditer(txt):
    pos = m.end(); durs = []
    while True:
        d = DUR.match(txt, pos)
        if not d: break
        if d.group(4): durs.append('-')
        elif d.group(3): durs.append(int(d.group(3)))
        else: durs.append(int(d.group(1)) * 12 + int(d.group(2) or 0))
        pos = d.end()
    seq.append((int(m.group(1)), durs, txt[pos:pos + 50].strip()))
with open(D + 'lignes.csv', encoding='utf-8') as f:
    rows = [l for l in csv.DictReader(x for x in f if not x.startswith('#'))
            if l['article'] == art and (tb is None or l['tableau'] == tb)]
rows.sort(key=lambda l: (int(l['tableau']), int(l['ligne'])))
rows = [l for l in rows if l['echelon'].isdigit()]
cols = ['duree', 'duree_moyenne', 'duree_minimale', 'duree_maximale']
dep = [(int(l['echelon']), [int(l[c]) for c in cols if l[c]], l['groupe'][:40]) for l in rows]
print('texte :', len(seq), 'échelons ; dépôt :', len(dep), 'lignes numérotées')
i = 0
for e, durs, after in seq:
    durs2 = [d for d in durs if d != '-']
    if i < len(dep) and dep[i][0] == e:
        ok = dep[i][1] == durs2
        print(('  ok ' if ok else '  ÉCART'), e, durs, dep[i][1], dep[i][2], '' if ok else '| suite: ' + after)
        i += 1
    else:
        print('  hors dépôt', e, durs, '| suite:', after[:60])
for x in dep[i:]: print('  reste au dépôt', x)
```

## 5. La règle du quart

Des 777 tableaux, 36 n'ont que la colonne moyenne, et 10 portent une `regle_du_quart` ; aucun
autre tableau n'en porte. Recherche ici, dans chaque version de chacun des 36 articles, des
formules « majorée / réduite / minorée du quart » : les **10** les écrivent, deux fois par
version, tous de l'hospitalière (n° 2001-1207, art. 12 ; 2010-1139, art. 19 ; 2011-661,
art. 24, deux versions ; 2012-1466, art. 16 ; 2014-99, art. 10 ; 2014-100, art. 11 ; 2014-101,
art. 11 ; 2014-1585, art. 19 ; 2015-1048, art. 14), et les **26** autres, aucune, dans leur
propre article : conforme. L'index compte bien 27 articles qui écrivent « majorée du quart » et
« réduite du quart », 28 avec « minorée ».

*Mais deux des 26 trouvent la règle dans un autre article de leur décret*, sous une autre
forme, que B2-bis n'a pas cherchée (« l'ancienneté moyenne réduite du quart ») :

- N° 91-45, art. 6 (LEGIARTI000006710407, du 25 juin 2007 au 30 juin 2011), « L'ancienneté
  moyenne pour accéder à l'échelon supérieur de chacun des grades du corps des agents chefs » ;
  et son **art. 32** (LEGIARTI000006710496, du 7 août 2007 au 30 juin 2011) : « Les durées
  moyennes et minimales du temps passé dans les échelons des grades du corps des agents chefs
  sont égales respectivement à l'ancienneté moyenne et à l'ancienneté moyenne réduite du
  quart. »
- N° 91-936, art. 6 (LEGIARTI000018616795, du 7 avril 2008 au 26 janvier 2012), agents-chefs
  de l'AP-HP ; et son **art. 29** (LEGIARTI000018616899, mêmes dates) : « Les durées moyennes et
  minimales du temps passé dans les échelons des grades du corps des agents-chefs sont égales
  respectivement à l'ancienneté moyenne et à l'ancienneté moyenne réduite du quart. »

**Écart faible** : pour ces deux tableaux, « le texte ne dit pas ce que sont les durées
maximale et minimale » est inexact pour la minimale ; aucune durée du dépôt n'en est fausse
(la moyenne est juste), mais la règle n'est pas consignée. L'index garde 23 versions d'article
qui écrivent « ancienneté moyenne réduite du quart » sans « majorée » (n° 88-1077, 89-609,
89-611, 89-613, 90-839, 91-45, 91-129, 91-936, 91-1269, 91-1271, 91-1273) ; seules les deux
ci-dessus touchent un tableau à moyenne seule.

## 6. Les comptes

Recomptés dans les fichiers, à 260182e et à b121b49, par un script du bloc-notes :

| | B2-bis dit | Recompté |
|---|---|---|
| Textes, dont avec un tableau lu | 727, 340 | 727, 340 |
| Tableaux (État, territoriale, hospitalière, militaires) | 777 (506, 178, 77, 16) | 777 (506, 178, 77, 16) ; somme de la colonne `lignes` : 14 506 |
| Lignes | 14 506 (8 400, 3 184, 1 787, 1 135) | les mêmes |
| Valeurs : rang, unique, moyenne, minimale, maximale | 14 506, 8 626, 3 323, 3 462, 1 060 | les mêmes |
| Non lus, dont avec un rang de tableau | 1 249, 750 | 1 249, 750 |
| Passage, commit par commit (tableaux, lignes, non lus) | −6, −178, +7 ; +14, +268, −28 ; +1, +26, −1 ; +6, +45, 0 ; fiches −384, +7 textes | les mêmes |
| Fiches : lignes de `non_lus.csv` en moins, versions consignées de plus, tableaux en fiches | 409 (38 versions), 25, 97 | 409, en **39** versions ; 25 versions neuves, de 18 textes, dont 7 neufs ; 97 |
| « Spécial » ; « Avant le » | 28 tableaux ; 4 | 28 tableaux dont un libellé finissait par « Spécial » à e0713a5, aucun à acccb16 (de 65 à 93 tableaux à ligne spéciale) ; 4 lignes « Avant le », en 4 tableaux |
| Certification | de 441 487 à 441 771 | 441 487 à b121b49, 441 771 à 260182e : +284 = 161 + 119 + 2 + 2 (rang, unique, minimale, maximale) |

Le 409 est un solde : 481 lignes ôtées, 97 lignes « en fiches » écrites, dont 72 pour des
versions déjà consignées ; 481 − 72 = 409. La 39e version est n° 98-343, art. 39,
LEGIARTI000006506809, jamais en vigueur, dont la seconde ligne s'en va (**faible**, sans
effet).

## 7. Les tests

`tests/test_durees_echelon.py` : 35 tests, tous verts, dont 14 ajoutés par B2-bis.

*Les textes recopiés.* Les neuf constantes ont été comparées, espaces près, à l'article du LEGI
que leur commentaire cite : chacune y est **mot pour mot**, en entier quand le commentaire le
dit (ADJOINTS_D_ENSEIGNEMENT, LEGIARTI000044268513 ; PUERICULTRICES, LEGIARTI000037468710 ;
SDIS, LEGIARTI000045657613 ; AIDES_TECHNIQUES, LEGIARTI000006506811 ;
INGENIEURS_DES_TELECOMMUNICATIONS, LEGIARTI000006508433), en tête d'article (AGREGES,
LEGIARTI000044268441 ; PROFESSEURS_DES_ECOLES, LEGIARTI000034947965), ou au milieu
(CHAIRES_SUPERIEURES, LEGIARTI000038669047 ; QUART_2014_99, LEGIARTI000028566814) ; les dates
des commentaires sont celles du LEGI. Une coquille : le commentaire écrit « Décret n° 67-715 du
18 août 1967 » ; le LEGI et le JORF (JORFTEXT000000513902) disent « du 16 août 1967 »
(**faible**, sans effet sur le test).

*Les valeurs attendues*, recomptées à la main depuis ces textes : adjoints, du 11e au 1er,
—, 54, 42, 42, 36, 36, 36, 24, 12, 12, 12 ; agrégés, 3 + 4 + 11 lignes ; professeurs des écoles
de classe exceptionnelle, spécial et 4e sans durée, puis 30, 24, 24 ; chaires supérieures, 54
au 5e (« 4 ans 6 mois »), puis 24 ; puéricultrices, quatre fois 24 ; SDIS, catégorie A
—, 36, 36, 36, 30, 24, 18, catégorie C —, 36, 36, 36, 30, 24, 18, 18, adjoint B —, 36, 36, 30,
24, 18, 18 ; attaché hors classe du n° 2011-1317 (« Spécial 7e ― 6e 3 ans »), spécial au rang 8,
7e sans durée, 36 au 6e ; administrateur général du n° 2021-1550, 48 au 5e et 36 au-dessous. Au
Noyau RH, relu ici : le grade 05041 « Administrateur général de l'Etat », du 1er janvier 2022 au
1er janvier 2023, grille 03742, texte 7257 « origine » ; la grille 03742, à cette date, 48 au
rang 5 et 36 aux rangs 1 à 4 ; le grade 02979, des administrateurs civils, fini le
31 décembre 2021, texte 7257 « abrogateur ». **Conforme** (point 3 de B2-bis).

*Ils mordent.* Chaque mutation, faite dans la copie, a fait échouer le test qui la vise :

| Mutation | Test |
|---|---|
| lignes : directeur technique de classe exceptionnelle (n° 99-669), 4e, 36 → 30 | `test_la_version_en_vigueur_a_ces_dates_est_lue` |
| tableaux : LEGIARTI000034810141 remise dans les versions du tableau de 2021 | `test_une_version_jamais_en_vigueur_n_est_pas_lue` |
| tableaux : un chevauchement effacé (n° 92-847) | `test_les_periodes_qui_se_chevauchent_sont_marquees` |
| tableaux : la règle du n° 2014-99 tronquée de son point final ; celle du n° 2014-100 effacée | `test_la_regle_du_quart_est_consignee_avec_la_moyenne` (deux fois) |
| lignes : administrateur général, 5e, 48 → 0 | `test_les_administrateurs_generaux_recoupes_au_noyau_rh_a_leur_grade` |
| non lus : le tableau en fiches du n° 98-343 compté deux fois | `test_un_tableau_en_fiches_n_est_compte_qu_une_fois` |
| lignes : « Attaché hors classe » redevenu « Attaché hors classe Spécial » | `test_aucun_libelle_ne_garde_la_case_d_un_echelon` |
| code : `jamais_en_vigueur` rend toujours faux | `test_une_version_jamais_en_vigueur_se_reconnait_a_ses_dates` |
| code : `PARAGRAPHE`, `SPECIAL`, `NOMME_UN_ECHELON`, `CHAMP_DE_FICHE` neutralisés, un à un | les quatre tests du « II.- », du « Spécial », de « Avant le », des fiches |
| code : `regle_du_quart` rend toujours vide | `test_la_regle_du_quart_se_cite_mot_pour_mot` |
| texte recopié des adjoints, « 10e échelon 4 ans 6 mois » → « 4 ans » ; des SDIS, catégorie A, « 6e échelon 3 ans » → « 2 ans » | les deux tests de ces textes |

Seize sur seize. Trois essais mal faits ont été refaits : deux visaient la première
occurrence du fichier, qui n'était pas la ligne voulue ; un autre laissait la règle non vide,
ce que le test, qui compte les règles, ne pouvait pas voir.

## 8. La certification et le paquet

Au dernier `main` (aa6721d), `python scripts/verifier_donnees.py` sort sans erreur (code 0),
sans écart. Les cinq séries `durees_echelon_*` y étaient d'abord ignorées, faute du fichier brut
(`data/brut/dila_legi_durees.json`, hors du dépôt) : le lecteur, relancé ici sur l'index
(`python scripts/fetch/dila_legi_durees.py`), a refait les quatre fichiers à l'identique, au
même compte (727 textes, 777 tableaux, 14 506 lignes, 1 249 non lus) — seul `lignes.csv`
diffère par l'**ordre** des lignes, le fichier de `main` rangeant le numéro de ligne comme un
texte (1, 10, 11…), le lecteur comme un nombre ; les 14 509 lignes du fichier, en-têtes compris,
sont les mêmes. La copie remise (`git checkout`), la certification donne, série par série :
rang 14 506, unique 8 626, moyenne 3 323, minimale 3 462, maximale 1 060 valeurs, « toutes
identiques, 0 corrigées, 0 ajoutées ». Puis `python scripts/construire_donnees.py` : `git
status` vide, le paquet ne change pas.

## 9. Trouvé en passant, hors du périmètre de B2-bis

Des articles qui portent un tableau de durées ne sont ni dans `tableaux.csv` ni dans
`non_lus.csv` : le lecteur ne les sélectionne pas (ils ne répondent pas au motif des durées
d'échelon, `_durees_d_echelon()`, qu'il applique avant tout). Deux exemples, rencontrés en
lisant l'échantillon : n° 2010-1239, art. 24, versions LEGIARTI000042864809 (du
28 décembre 2020 au 1er janvier 2022) et LEGIARTI000035604180 (du 1er janvier 2022 au
15 décembre 2025), « GRADES DÉSIGNATION DES ÉCHELONS ANCIENNETE DE GRADES OU D'ECHELONS
EXIGEE pour accéder à l'échelon … Echelon spécial Après 1 an dans l'échelon précédent … »,
alors que les versions de 2010 et de 2017 sont consignées ; n° 90-680, art. 24,
LEGIARTI000006459200 (du 1er septembre 1990 au 1er septembre 2017), « ÉCHELONS GRAND CHOIX
CHOIX ANCIENNETÉ Du 1er au 2e 3 mois … ». Ce trou est déjà à b121b49 (vient de B2) ; « 1 249 non
lus, avec leur raison » ne vaut que pour les articles que le motif retient (**faible** pour
B2-bis ; à mesurer avant le chaînage, pour l'action 158).

## Ce qui n'a pas été vérifié

Les lignes hors de l'échantillon et des 14 tableaux contre-lus ; les rédactions des tableaux du
n° 83-1260, art. 34, au JORF, faute de texte (point 2) ; l'article d'entrée en vigueur des
décrets n° 2017-1374 et n° 96-101 (chevauchements), absents de l'index, comme B2-bis l'a dit ;
les 97 tableaux en fiches et les autres refus, non relus.

*Question au propriétaire, en plus de celle de B2-bis.* Faut-il lire au JORF, à la main, les
tableaux que la consolidation du LEGI abîme, comme celui des professeurs techniques de la PJJ
depuis le 1er janvier 2021 (décret n° 2020-1435, art. 8) ?
