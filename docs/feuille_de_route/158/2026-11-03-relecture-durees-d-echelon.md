# Relecture des durées d'échelon (file B2)

File R-B2, le 3 novembre 2026 : relecture indépendante du commit 04cbe34 (session B2,
note `2026-11-03-etape-2-durees-d-echelon.md`), sur échantillon. Chaque article a été
rouvert ici, sans rien reprendre de la session ni de mémoire : l'index LEGI publié du
dépôt, récupéré sans reconstruction (`dila_index.py legi --recuperer`, à jour de
l'incrément du 2 novembre 2026, 20261102-213929), interrogé article par article
(`dila_cherche.py legi --texte`, `--num … --titre`, `--diff`, `--motif`) ; le Noyau RH de
l'État (CISIRH, juillet 2026), déjà au dépôt sous `data/reference/grilles/etat/`, pour les
sept écarts. Les fichiers de B2 n'ont pas bougé depuis 04cbe34. Rien n'a été modifié : ni
donnée, ni test, ni script.

**Verdict.** Les **32 lignes** tirées au hasard (8 par versant) ont toutes le bon grade, le
bon échelon, la bonne durée et la bonne référence d'article : **32 sur 32 conformes** pour la
valeur. Les totaux annoncés se recomptent (720 textes, dont 336 avec un tableau lu ;
762 tableaux ; 14 345 lignes ; 1 655 non lus). Les tests tirent leurs valeurs des textes
(point 4). Les six écarts au Noyau RH sur les zéros du noyau sont justes : le texte a
raison. **Écarts** : un **moyen** — six tableaux, 178 lignes, viennent de versions que le
LEGI dit « jamais en vigueur », certifiées avec une période impossible (fin avant ou au
début) ; trois lignes de l'échantillon en sont (lignes 3, 18, 25), leur durée juste
(point 1 et point 5.1) ; six **faibles** — un tableau lisible écarté pour une phrase qui
le suit, avec une raison inexacte, défaut qui touche aussi les agrégés (point 2) ; le
septième écart au Noyau RH, comparé au grade éteint des administrateurs civils (point 3) ;
les fiches comptées en plusieurs tableaux non lus (point 2) ; trois chevauchements de
périodes, recopiés du LEGI (point 5.2) ; un groupe vide quand le grade précède l'en-tête
(ligne 15, point 5.3) ; la règle du quart d'un article, ni lue ni consignée (point 5.4).
Aucun **grave**.

## 1. L'échantillon : trente-deux lignes de `lignes.csv`

Le tirage, par un script du bloc-notes de la session, hors du dépôt, lancé depuis la racine
du dépôt ; graine **20261103** ; le versant est celui de `textes.csv` :

```python
"""Échantillon de la relecture R-B2 : 8 lignes par versant, graine 20261103."""
import csv, random, sys
D = 'data/reference/grilles/durees/'
def lire(p):
    with open(D + p, encoding='utf-8') as f:
        return list(csv.DictReader(l for l in f if not l.startswith('#')))
textes = {t['texte']: t for t in lire('textes.csv')}
tableaux = {(t['texte'], t['article'], t['tableau']): t for t in lire('tableaux.csv')}
lignes = lire('lignes.csv')
rng = random.Random(20261103)
for versant in ('etat', 'territoriale', 'hospitaliere', 'militaires'):
    pool = [l for l in lignes if textes[l['texte']]['versant'] == versant]
    for l in rng.sample(pool, 8):
        t = textes[l['texte']]; tb = tableaux[(l['texte'], l['article'], l['tableau'])]
        print('|'.join([versant, t['numero'], l['texte'], l['article'], tb['numero'], l['tableau'], l['ligne'],
              l['groupe'], l['echelon'], l['rang'], 'u=' + l['duree'], 'moy=' + l['duree_moyenne'],
              'min=' + l['duree_minimale'], 'max=' + l['duree_maximale'], 'cond=' + l['condition'],
              tb['debut'], tb['fin'], tb['colonnes'], tb['versions']]))
```

Pour chaque ligne : l'article ouvert à la version que la ligne cite, ses dates au LEGI, et
la liste de ses versions (`--num <article> --titre <numéro du décret>`, `--diff`) pour la
période. « T/L » : le tableau et la ligne dans `lignes.csv`. Les durées sont en mois.

| # | Versant | Texte, article (version) | T/L | Grade, échelon | Au dépôt | Au texte | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | État | n° 96-158, art. 15 (LEGIARTI000036939082, puis LEGIARTI000044467398) | 1/15 | Psychologue de classe normale, 5e | 30 ; depuis le 1er janvier 2021 | « 5e échelon 2 ans 6 mois » ; version du 1er janvier 2021 au 1er janvier 2022, la suivante ne change que le nom du corps (`--diff`) | conforme |
| 2 | État | n° 98-898, art. 20 (LEGIARTI000037217015) | 1/14 | Ingénieur-économiste de la construction principal et ingénieur des services culturels et du patrimoine principal, 2e | 30 ; depuis le 1er janvier 2021 | « 2e échelon 2 ans 6 mois » ; en vigueur depuis le 1er janvier 2021 | conforme |
| 3 | État | n° 99-669, art. 17 (LEGIARTI000034810141) | 1/3 | Directeur technique de 1re classe, 7e | 36 ; du 1er janvier 2021 au 1er juin 2020 | « 7e échelon 3 ans » ; mais le LEGI date cette version du 1er janvier 2021 au 1er juin 2020 et la dit « jamais en vigueur » ; celle en vigueur le 1er janvier 2021, LEGIARTI000041916038, écrit aussi « 7e échelon 3 ans » | durée conforme ; période impossible (point 5.1) |
| 4 | État | n° 99-669, art. 17 (LEGIARTI000041902378) | 1/1 | Directeur technique de classe exceptionnelle, échelon spécial (rang 6) | sans durée ; du 1er juin 2020 au 1er janvier 2021 | « Echelon spécial - 5e échelon 4e échelon 3 ans » ; version du 1er juin 2020 au 1er janvier 2021 | conforme |
| 5 | État | n° 2002-1520, art. 16 (LEGIARTI000041519684) | 1/17 | Professeurs des écoles nationales supérieures d'art de 2e classe, 2e | 24 ; depuis le 1er septembre 2017 | « 2e échelon 2 ans » ; en vigueur au 1er septembre 2017 (article 19 du décret n° 2020-61) | conforme |
| 6 | État | n° 92-345, art. 10 (LEGIARTI000032526360) | 1/9 | grade unique (chef de service éducatif), 1er | 24 ; depuis le 1er janvier 2017 | « 1er échelon 2 ans » ; version du 1er janvier 2017, sans fin | conforme |
| 7 | État | n° 2021-1869, art. 18 (LEGIARTI000046347153) | 1/15 | Aide-soignant civil de classe normale, 8e | 36 ; depuis le 1er octobre 2022 | « 8e échelon 3 ans » ; version du 1er octobre 2022, sans fin | conforme |
| 8 | État | n° 92-344, art. 18 (LEGIARTI000006468078) | 1/20 | Educateur de 1re classe, 5e | 24 ; du 1er janvier 2016 au 1er janvier 2017 | « 5e échelon 2 ans » ; version du 1er janvier 2016 au 1er janvier 2017 | conforme |
| 9 | Territoriale | n° 87-1099, art. 17 (LEGIARTI000033677396) | 1/10 | Attaché principal, 6e | 30 ; du 1er janvier 2017 au 1er janvier 2021 | « 6e échelon 2 ans 6 mois » ; mêmes dates | conforme |
| 10 | Territoriale | n° 95-25, art. 16 (LEGIARTI000006376945) | 1/26 | Rédacteur, 3e | maximale 18, minimale 18 ; du 1er août 1995 au 1er août 2012 | en-tête « DUREES Maximale Minimale », « 3e échelon 1 an 6 mois 1 an 6 mois » ; mêmes dates, seule version de l'article dans ce décret | conforme |
| 11 | Territoriale | n° 2013-490, art. 14 (LEGIARTI000032551065) | 1/3 | Moniteur-éducateur et intervenant familial principal, 11e | 36 ; du 1er janvier 2017 au 1er septembre 2022 | « 11e échelon 3 ans » ; mêmes dates | conforme |
| 12 | Territoriale | n° 91-855, art. 16 (LEGIARTI000035647832) | 1/11 | Directeur d'établissement d'enseignement artistique de 1re catégorie, 9e | sans durée ; depuis le 1er janvier 2017 | « 9e échelon - » | conforme |
| 13 | Territoriale | n° 2013-490, art. 14 (LEGIARTI000032551065) | 1/7 | Moniteur-éducateur et intervenant familial principal, 7e | 24 | « 7e échelon 2 ans » | conforme |
| 14 | Territoriale | n° 2021-1079, art. 15 (LEGIARTI000044812856) | 1/6 | Gardien-brigadier, 7e | 24 ; depuis le 1er janvier 2022 | « 7e échelon 2 ans » ; version du 1er janvier 2022, sans fin | conforme |
| 15 | Territoriale | n° 2016-2003, art. 13 (LEGIARTI000033792629, puis LEGIARTI000045657613) | 3/6 | groupe vide, 3e | 24 ; depuis le 1er janvier 2017 | le 3e tableau est celui du « Directeur départemental du service d'incendie et de secours de catégorie C » : « 3e échelon 2 ans » ; la version du 17 avril 2022 ne change que « du service » en « des services » | durée et période conformes ; l'emploi n'est nommé qu'à la fin de l'`intro` du tableau, pas dans `groupe` (faible) |
| 16 | Territoriale | n° 2017-901, art. 17 (LEGIARTI000034726981) | 1/16 | Assistant socio-éducatif, 10e | 30 ; depuis le 1er janvier 2021 | « 10e échelon 2 ans 6 mois » ; entrée en vigueur reportée au 1er janvier 2021 (article 48 du décret n° 2017-1736) | conforme |
| 17 | Hospitalière | n° 2014-99, art. 10 (LEGIARTI000028566814) | 1/10 | Moniteur-éducateur principal, 4e | moyenne 24 ; du 7 février 2014 au 22 mai 2016 | en-tête « MOYENNE », « 4e échelon 2 ans » ; mêmes dates | conforme (le II de l'article, point 5.4) |
| 18 | Hospitalière | n° 91-868, art. 7 (LEGIARTI000035606585) | 1/28 | Ingénieur hospitalier, 9e | 48 ; du 1er janvier 2021 au 19 novembre 2018 | « 9e échelon 4 ans » ; mais version du 1er janvier 2021 au 19 novembre 2018, jamais en vigueur ; celle en vigueur le 1er janvier 2021, LEGIARTI000037623417, écrit aussi « 9e échelon 4 ans » | durée conforme ; période impossible (point 5.1) |
| 19 | Hospitalière | n° 91-45, art. 6 (LEGIARTI000006710407) | 1/12 | Agents chefs de 1re catégorie, 4e | moyenne 30 ; du 25 juin 2007 au 30 juin 2011 | « ANCIENNETÉ MOYENNE », « 4e échelon 2 ans 6 mois » ; mêmes dates | conforme |
| 20 | Hospitalière | n° 2011-661, art. 24 (LEGIARTI000046247539) | 1/16 | Deuxième grade, 8e | 36 ; depuis le 1er septembre 2022 | « 8e échelon 3 ans » | conforme |
| 21 | Hospitalière | n° 2017-1260, art. 14 (LEGIARTI000045071936) | 1/14 | Technicien médical de classe normale, 8e | 36 ; du 26 janvier 2022 au 1er septembre 2022 | « 8e échelon 3 ans » ; mêmes dates | conforme |
| 22 | Hospitalière | n° 91-45, art. 6 (LEGIARTI000006710407) | 1/7 | Agents chefs de classe exceptionnelle, 1er | moyenne 24 | « 1er échelon 2 ans » | conforme |
| 23 | Hospitalière | n° 2010-1139, art. 19 (LEGIARTI000032577456) | 1/37 | Premier grade, 4e | 36 ; du 22 mai 2016 au 1er juillet 2016 | « 4e échelon 3 ans » ; mêmes dates | conforme |
| 24 | Hospitalière | n° 2014-1585, art. 19 (LEGIARTI000033621822) | 1/4 | Second grade, 6e | 36 ; du 1er janvier 2017 au 1er janvier 2021 | « 6e échelon 3 ans » ; mêmes dates | conforme |
| 25 | Militaires | n° 2014-1455, art. 22 (LEGIARTI000052465286) | 1/8 | Général de brigade, échelle de solde n° 3, 1er | 12 ; du 15 décembre 2025 au 15 décembre 2025 | « 1 er échelon 1 an » ; mais version du 15 décembre 2025 au 15 décembre 2025, jamais en vigueur ; celle en vigueur, LEGIARTI000053027219, n'en diffère que par un quota (« 15 % » devenu « 10 % », comparaison mot à mot) | durée conforme ; période vide (point 5.1) |
| 26 | Militaires | n° 2008-940, art. 34 (LEGIARTI000052465274) | 1/56 | Lieutenant-colonel, échelle de solde n° 1, 3e | 24 ; depuis le 15 décembre 2025 | « Echelle de solde n° 1 … 3 e échelon 2 ans », sous le lieutenant-colonel | conforme |
| 27 | Militaires | n° 2008-944, art. 28 (LEGIARTI000052465320) | 1/64 | Ingénieur principal, échelle de solde n° 2, 2e | 12 ; depuis le 15 décembre 2025 | « 2 e échelon 1 an » | conforme |
| 28 | Militaires | n° 2008-944, art. 28 (LEGIARTI000052465320) | 1/8 | Ingénieur général de 2e classe, échelle de solde n° 3, 1er | 12 | « 1 er échelon 1 an » | conforme |
| 29 | Militaires | n° 2012-1029, art. 31 (LEGIARTI000052465282) | 1/78 | Commissaire principal, échelle de solde n° 1, 2e | 12 ; depuis le 15 décembre 2025 | « 2 e échelon 1 an » | conforme |
| 30 | Militaires | n° 2008-952, art. 8 (LEGIARTI000047908829) | 1/1 | Major, 6e | sans durée ; depuis le 1er janvier 2024 | « Major 6e échelon - » | conforme |
| 31 | Militaires | n° 2012-1029, art. 31 (LEGIARTI000052465282) | 1/75 | Commissaire principal, échelle de solde n° 1, 5e | 12 | « 5 e échelon 1 an » | conforme |
| 32 | Militaires | n° 2008-942, art. 14 (LEGIARTI000052465276) | 1/2 | Ingénieur général de 1re classe, échelle de solde n° 3, 3e | 12 ; depuis le 15 décembre 2025 | « 3 e échelon 1 an » | conforme |

Aucune borne de durée n'est écrite dans ces trente-deux lignes hors des colonnes que le
dépôt garde (moyenne, minimale, maximale) ; la condition d'accès n'y apparaît pas.

## 2. Cinq tableaux de `non_lus.csv`

Tirage parmi les 1 155 lignes de `non_lus.csv` qui portent un rang de tableau (les autres,
500, sont des articles en phrases ou des renvois), même graine :

```python
"""Cinq tableaux non lus (colonne tableau remplie), graine 20261103."""
import csv, random
D = 'data/reference/grilles/durees/'
def lire(p):
    with open(D + p, encoding='utf-8') as f:
        return list(csv.DictReader(l for l in f if not l.startswith('#')))
textes = {t['texte']: t for t in lire('textes.csv')}
nl = [n for n in lire('non_lus.csv') if n['tableau']]
for n in random.Random(20261103).sample(nl, 5):
    t = textes[n['texte']]
    print('|'.join([t['versant'], t['numero'], n['article'], n['numero'], n['tableau'], n['debut'], n['fin'], n['motif']]))
```

| # | Texte, article (version) | Raison donnée | Ce que dit l'article | Verdict |
|---|---|---|---|---|
| 1 | n° 98-343, art. 39 (LEGIARTI000006506811, du 1er août 2000 au 30 décembre 2006), tableau 5 | « un libellé porte une durée ou un échelon : « 2 ans ÉCHELON » » | un seul tableau en fiches : « ÉCHELON : 5e échelon DURÉE Moyenne : 4 ans DURÉE Minimale : 3 ans ÉCHELON : 4e échelon … » ; l'analyseur en fait cinq tableaux, tous refusés | mise de côté juste (une fiche ne se lit pas sans risque) ; un tableau compté cinq fois ; lisible à la main |
| 2 | n° 59-772, art. 8-4 (LEGIARTI000006509816, du 22 septembre 1994 au 19 mai 2004), tableau 1 | « un libellé porte une durée ou un échelon : « 1° Un an , pour les deux premiers échelons de la 2 » » | pas un tableau : « 1° Un an, pour les deux premiers échelons de la 2e classe ; 2° Deux ans, pour les 3e, 4e, 5e, 6e et 7e échelons … » | mise de côté juste ; la raison est le symptôme, la nature est « durées en phrases » |
| 3 | n° 67-715, art. 13 (LEGIARTI000006508433, du 25 août 1967 au 21 mai 2000), tableau 4 | « un libellé porte une durée ou un échelon : « 1 ans 6 mois . GRADE : Ingénieur de 1re classe » » | un seul tableau en fiches : « GRADE : Ingénieur général, 1er et 2e échelon DUREE moyenne : 3 ans. DUREE minimum : 2 ans 3 mois. GRADE : … » ; sept tableaux pour l'analyseur | mise de côté juste ; un tableau compté sept fois |
| 4 | même article, tableau 5 | « aucun échelon » | le morceau entre deux « DUREE » de la même fiche | mise de côté juste ; même remarque |
| 5 | n° 72-583, art. 6 (LEGIARTI000044268513, depuis le 29 octobre 2021), tableau 1 | « un échelon manque dans « II.-Les anciennetés détenues dans les » » | « ÉCHELON DURÉE 11e échelon - 10e échelon 4 ans 6 mois 9e échelon 3 ans 6 mois … 1er échelon 1 an », complet, puis un « II.- » en phrases sur les bonifications du 6e et du 8e échelon | **écarté à tort** : le tableau est lisible et complet ; aucun échelon n'y manque ; c'est la phrase du II, qui nomme des échelons, que l'analyseur a prise pour un grade (faible) |

Le défaut du cinquième est un motif : les quatre versions de l'article depuis le
1er septembre 2017 (LEGIARTI000034779361, LEGIARTI000038669106, LEGIARTI000041436438,
LEGIARTI000044268513) portent la même raison ; 21 des 22 refus « un échelon manque »
citent une phrase qui suit le tableau (« II.-Les anciennetés détenues dans les » : 8 ; « Le
recteur d'académie prononce, pour chaque année scolaire, » : 5 ; « Le ministre prononce les
promotions des professeurs agrégés. » : 3 ; …). Un seul a été rouvert de plus : l'article 13
du statut des professeurs agrégés (n° 72-580, LEGIARTI000044268441, du 29 octobre 2021 au
2 septembre 2024), dont le tableau des trois grades est complet avant « Le ministre prononce
les promotions des professeurs agrégés. II.-… ». Les autres ne l'ont pas été. Ces tableaux ne
sont pas faux au dépôt — ils n'y sont pas, et le disent —, mais la raison écrite est inexacte,
et ils couvrent de grands corps de l'enseignement.

## 3. Les sept écarts au Noyau RH

B2 n'a pas versé son script de recoupement ; les écarts sont refaits ici à partir de
`data/reference/grilles/etat/` (`textes.csv`, `corps.csv`, `grades.csv`, `echelons.csv`) et
des articles. Sept « durées » sont des valeurs de colonne : moyenne et minimale comptent
chacune.

| Corps, texte, article (version) | Au texte | Au noyau | Qui a raison |
|---|---|---|---|
| Médecins inspecteurs de santé publique, n° 91-1025, art. 11 (LEGIARTI000006711476, du 30 septembre 2000 au 1er janvier 2017) | « Médecin inspecteur de santé publique … 2e échelon 1 an 1 an 1er échelon 1 an 1 an » (moyenne, minimale) : minimale 12 aux 1er et 2e | grille 00097, du 1er octobre 2000 au 31 décembre 2016 : rangs 1 et 2, minimale 0, moyenne 12 ; les rangs 3 à 8 égaux au texte | le texte : 2 écarts, zéros du noyau |
| Techniciens supérieurs des études et de l'exploitation de l'aviation civile, n° 93-622, art. 14 (LEGIARTI000006471150, du 1er janvier 2007 au 15 novembre 2013) | classe normale : « 10e échelon 4 ans 3 ans », « 5e échelon 2 ans 1 an 6 mois » | grille 00227, versions du 27 octobre 2009 : rangs 1 et 2 élève et stagiaire, le 1er échelon au rang 4 ; rang 8 (5e) et rang 13 (10e) à 0, les autres rangs égaux au texte | le texte : 4 écarts (deux échelons, deux colonnes), zéros du noyau |
| Administrateurs de l'État, n° 2021-1550, art. 9 (LEGIARTI000044396371, du 1er janvier 2022 au 1er janvier 2023) | « Administrateur général 6e échelon - 5e échelon 4 ans 4e échelon 3 ans … » : 48 au 5e | grade 05041 « Administrateur général de l'Etat », grille 03742, du 1er janvier 2022 au 1er janvier 2023 : rang 5 à **48**, égal au texte ; le seul 0 au rang 5 sous ce libellé est la grille 02929 du grade 02979 « Administrateur général » des administrateurs civils, fini le 31 décembre 2021, dont les versions d'échelon restent ouvertes au noyau | le texte, et le noyau aussi, à son bon grade : 1 écart, qui vient d'un lien au grade éteint (faible) |

Les six premiers sont expliqués comme B2 le dit. Le septième ne l'est qu'à moitié : « zéro au
noyau » est exact pour la grille comparée, mais ce n'est pas la grille du corps que régit le
décret n° 2021-1550 ; à son grade, le noyau donne 48 mois. Le même zéro du noyau au 5e échelon
de la classe normale des TSEEAC revient dans la version du 15 novembre 2013 (grille 00227,
rang 8) : il n'est pas compté, le tableau de 2013 nommant le grade « Technicien de classe
normale », que le lien par libellé ne retrouve pas.

## 4. Les tests de `tests/test_durees_echelon.py`

Vingt et un tests, tous verts ici. Les dix textes recopiés en constantes ont été comparés, par
un script du bloc-notes, à l'article du LEGI à la version qu'en donne le commentaire : chacun y
figure **mot pour mot** (espaces près), en entier ou en début d'article —
TECHNICIENS_SANITAIRES (LEGIARTI000006470031), INGENIEURS_D_ETUDES (LEGIARTI000034794372),
INGENIEURS_HOSPITALIERS (LEGIARTI000037623011), GENDARMES (LEGIARTI000026912312),
DESSINATEURS (LEGIARTI000032192685), CONTROLEURS (LEGIARTI000006377526), TERMINAL
(LEGIARTI000006476831), ONF (LEGIARTI000006509643), BIOLOGISTES (LEGIARTI000034434471),
PROFESSEURS_ARTISTIQUES (LEGIARTI000006374077) ; les dates des commentaires sont celles du
LEGI. Chaque liste de valeurs attendues a été recomptée à la main depuis ces textes (par
exemple les techniciens d'études de classe normale, du 13e au 1er : 36, cinq fois 24, six fois
18, 12) : toutes justes. Les assertions sur les fichiers ont été vérifiées aux articles :
l'article 24 du décret n° 2010-329 dans ses trois versions (LEGIARTI000022021243 : troisième
grade, 10e, « 2 ans 5 mois 3 ans », soit 29 et 36 ; LEGIARTI000028542716, « MAXIMALE
MINIMALE » ; LEGIARTI000032542276, du 15 mai 2016 au 1er janvier 2017), les gendarmes (la
version du 5 janvier 2013 n'ajoute que la phrase finale à celle du 1er janvier 2012), le
colonel du décret n° 76-1001 (LEGIARTI000052465264 : « 12 e échelon 1 an et 6 mois » en
échelle n° 3, « 14 e échelon 1 an » en échelle n° 2). Le test de la condition d'accès cite,
sans identifiant, un passage qui se lit mot pour mot dans l'article 34 du décret n° 2008-940
(LEGIARTI000052465274) ; trois tests de refus portent sur des textes écrits pour le test, ce
qui convient à un refus. **Conforme.** Aucun test ne garde les deux défauts relevés ici : une
version jamais en vigueur, un tableau suivi d'un « II.- ».

## 5. Ce que la relecture a trouvé en plus

1. **Six tableaux de versions jamais en vigueur (moyen).** Le LEGI date ces versions d'une fin
   antérieure ou égale à leur début, et `dila_cherche.py --num … --diff` les marque « (jamais
   en vigueur) » ; le dépôt les certifie comme les autres, avec cette période : n° 99-669,
   art. 17 (LEGIARTI000034810141), n° 83-1260, art. 34 (LEGIARTI000027940471, du
   8 janvier 1984 au 4 août 1980), n° 91-868, art. 7 (LEGIARTI000035606585), n° 91-290,
   art. 14-4 (LEGIARTI000025845550, du 1er septembre 2014 au 30 août 2012), n° 2014-923,
   art. 25 (LEGIARTI000032578591, du 1er janvier 2017 au 1er janvier 2017), n° 2014-1455,
   art. 22 (LEGIARTI000052465286) : 178 lignes. Deux ne redisent pas la version en vigueur le
   même jour : celle du n° 99-669 n'a pas la classe exceptionnelle (six lignes de moins),
   celle du n° 2014-923 n'écrit que trois des « quatre échelons provisoires » qu'elle annonce,
   la version en vigueur (LEGIARTI000037468710) écrivant le 4e, « 2 ans ». Aucune durée
   n'en sert aujourd'hui ; le chaînage aux grilles devra les ôter, ou les marquer.
2. **Trois chevauchements, hérités du LEGI (faible).** Deux versions du même article en
   vigueur ensemble, d'après les dates du LEGI lui-même : n° 91-868, art. 7
   (LEGIARTI000033602862 et LEGIARTI000035742510, toutes deux du 1er janvier 2017) ; décret
   n° 96-366, art. 5 (LEGIARTI000006482187, jusqu'au 24 juin 1998, et LEGIARTI000006482188,
   depuis le 24 juin 1996) ; n° 92-847, art. 14 (LEGIARTI000006374721, jusqu'au
   8 février 1996, et LEGIARTI000006374722, depuis le 1er août 1995). Le dépôt les recopie
   fidèlement ; le chaînage devra choisir, la version rétroactive l'emportant.
3. **Le groupe vide quand le grade précède l'en-tête (faible).** Ligne 15 : dans l'article 13
   du décret n° 2016-2003, chaque emploi est nommé avant « ÉCHELONS DURÉE » ; les six tableaux
   ont un `groupe` vide, et l'emploi ne se lit qu'à la fin de l'`intro`.
4. **La règle du quart, ni lue ni consignée (faible).** L'article 10 du décret n° 2014-99
   (ligne 17) écrit en son II : « La durée maximale … est égale à la durée moyenne majorée du
   quart. La durée minimale … est égale à la durée moyenne réduite du quart. Cette durée ne
   peut être inférieure à un an. » Le dépôt garde la moyenne, juste, sans dire que l'article
   fixe aussi les deux autres ; l'article n'est pas dans `non_lus.csv`. L'index compte 27
   articles qui écrivent les deux formules ; 36 tableaux n'ont que la colonne moyenne.

*Ce qui n'a pas été vérifié.* Les 2 563 valeurs égales du recoupement au Noyau RH, faute du
script de B2 ; la contre-lecture de B2 (12 392 lignes), pour la même raison ; les autres
refus « un échelon manque » que les deux rouverts ; les lignes hors de l'échantillon.

*Pour la suite de l'action 158, sans rien en faire ici.* Ôter ou marquer les versions jamais
en vigueur avant le chaînage ; arrêter un tableau à la phrase qui le suit même quand elle
nomme des échelons, puis relire les refus « un échelon manque » ; compter un tableau en fiches
une seule fois ; consigner la règle du quart avec la moyenne ; corriger l'explication du
septième écart au Noyau RH.
