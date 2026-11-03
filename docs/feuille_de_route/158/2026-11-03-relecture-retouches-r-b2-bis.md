# Relecture des retouches de R-B2-bis (file B2-ter)

File R-B2-ter, le 3 novembre 2026 : relecture indépendante des six commits de la session
B2-ter (ddde684, f16c3d7, 39643e8, d75b842, 6db5939, 54983bd ; note
`2026-11-03-retouches-de-la-relecture-r-b2-bis.md`). Rien n'est repris de la session ni de
mémoire : chaque article cité ci-dessous a été rouvert ici. Les sources : l'index LEGI publié du
dépôt (`dila_index.py legi --recuperer`, à jour de l'incrément 20261102-213929, le même que
B2-ter) et l'index JORF publié (`jorf --recuperer`, incrément 20261103-002311), récupérés sans
reconstruction, interrogés par `dila_cherche.py legi --num … --titre` et directement dans leur
table `doc`. Les fichiers de B2-ter n'ont pas bougé sur `main` depuis 54983bd (vérifié au
dernier `main`, ee67f54). Rien n'a été modifié dans le dépôt : les mutations des tests, le
lecteur relancé, le recontrôle appliqué et le paquet refait l'ont été dans une copie à part
(un `git worktree` du bloc-notes, au même commit), jamais dans la copie de travail.

**Verdict.** Les six points sont **conformes** : les 15 lignes rendues au n° 83-1260, art. 34,
sont égales au texte du LEGI, et la coquille est établie au JORF ; le motif du 22e refus cite
mot pour mot le décret publié ; les deux règles du quart sont citées mot pour mot ; les deux
coquilles de B2-bis sont bien corrigées ; le trou se recompte à l'identique (102 versions,
58 articles, 48 textes ; 97, 54, 44), et les trois versions tirées au hasard sont des tableaux
de durées ; les 5 tests ajoutés tirent leurs valeurs des textes et mordent (7 mutations sur 7) ;
la certification passe sans écart, et le paquet ne bouge pas. **Un écart faible**, de rédaction,
aucune valeur des données n'est fausse : « 409 lignes en moins » (point 4) n'est pas la baisse
du fichier, qui perd 384 lignes. Deux réserves, que B2-ter déclare ou qui renforcent sa prudence,
sont dites à leur point.

## 1. Le n° 83-1260, art. 34 : conforme

*Au JORF, ouvert ici.* JORFARTI000000984252, daté du 3 août 1990, du « Décret n°90-685 du
27 juillet 1990 modifiant le décret n° 83-1260 du 30 décembre 1983 modifié […] » : « Art. 5. -
Le tableau de l'article 34 du décret du 30 décembre 1983 susvisé est remplacé par le tableau
ci-dessous: ...................................................... Vous pouvez consulter le
tableau dans le JO no 0178 du 03/08/1990 ». Le texte (JORFTEXT000000350640, du 3 août 1990)
porte la notice « MODIFICATION DES ART. 12,15,18,26 (AL. 1),27 (DERNIER AL.),34 (TABLEAU),35,
[…] » et le visa « Vu le décret no 83-1260 du 30 décembre 1983 […], modifié par le décret
no 88-1072 du 24 novembre 1988 et le décret no 89-74 du 4 février 1989 ». Le n° 88-1072
(JORFTEXT000000504532, JO du 30 novembre 1988) : « MODIFICATION DES ART. 104 ET 185 DU DECRET
831260 DU 30-12-1983 » ; le n° 89-74 (JORFTEXT000000509890, JO du 5 février 1989) : « LA
PROPORTION DE 28% VISEE AUX ART. 104 ET 185 (AL. 2) DU DECRET SUSVISE EST PORTEE A 30% ».
Recompté : 26 textes du JORF, du 8 janvier 1984 au 3 août 1990, citent « 83-1260 »,
« 831260 », ou « 30 décembre 1983 » avec « scientifiques et technologiques », ou nomment les
établissements publics scientifiques et technologiques : 12 décrets, dont ces trois, et
14 arrêtés, comme B2-ter les compte. Les 57 articles du JORFTEXT000000316777 (JO du 7 janvier
1984) sont vides dans l'index : 57, dont 0 avec un texte.

*Au LEGI.* `dila_cherche.py legi --num 34 --titre 83-1260` : LEGIARTI000027940471,
« 1984-01-08 → 1980-08-04 », puis LEGIARTI000027940483, « 1990-08-04 → 2002-02-03 » ; aucune
version entre les deux.

*Les 15 lignes, une à une, contre LEGIARTI000027940471* (« Chargés de recherche de première
classe 9e échelon Echelon terminal 8e échelon 3 ans 7e échelon 3 ans 6e échelon 3 ans
5e échelon 2 ans 6 mois 4e échelon 2 ans 6 mois 3e échelon 2 ans 6 mois 2e échelon 2 ans
6 mois 1er échelon 2 ans Chargés de recherche de deuxième classe 6e échelon Echelon terminal
5e échelon 2 ans 4e échelon 1 an 5 mois 3e échelon 1 an 4 mois 2e échelon 1 an 3 mois
1er échelon 1 an ») et `lignes.csv`, lignes 4266 à 4280 :

| Grade | Échelon | Le texte | Au dépôt (mois) |
|---|---|---|---|
| Chargés de recherche de première classe | 9 | Echelon terminal | vide |
| | 8, 7, 6 | 3 ans | 36, 36, 36 |
| | 5, 4, 3, 2 | 2 ans 6 mois | 30, 30, 30, 30 |
| | 1 | 2 ans | 24 |
| Chargés de recherche de deuxième classe | 6 | Echelon terminal | vide |
| | 5 | 2 ans | 24 |
| | 4 | 1 an 5 mois | 17 |
| | 3 | 1 an 4 mois | 16 |
| | 2 | 1 an 3 mois | 15 |
| | 1 | 1 an | 12 |

15 sur 15, grade, échelon et durée. `tableaux.csv`, ligne 257 : début 1984-01-08, fin
1990-08-04, colonne `unique`, 15 lignes, et la correction, qui cite le n° 90-685, art. 5,
JORFARTI000000984252, « JO n° 178 du 3 août 1990 » et la version du LEGI ; c'est le seul
tableau qui porte une correction. La ligne de `non_lus.csv` est partie.

*Réserve, faible.* Que la fin soit en **1990**, le JORF le prouve. Le **jour**, 4 août, est
celui où le LEGI fait commencer la version suivante : les 43 articles du n° 90-685 dans l'index
(de « Décrète: » à l'art. 42) ne fixent pas d'entrée en vigueur (l'art. 41 est transitoire,
l'art. 42 d'exécution), et la règle qui faisait entrer en vigueur un décret de 1990 n'a pas été
lue ici : non vérifié, faute de texte.

## 2. Le 22e refus : conforme

*Au LEGI.* LEGIARTI000042571828, du 1er janvier 2021, sans version après (`--num 14 --titre
96-1113` : 1995-01-01 → 2017-09-01, 2017-09-01 → 2021-01-01, 2021-01-01) : « Professeur
technique hors classe 7e échelon - 6e échelon 3 ans 4e échelon 2 ans 6 mois 3e échelon 2 ans
6 mois 2e échelon 2 ans 1er échelon 2 ans » : le 5e échelon manque.

*Au JORF.* Décret n° 2020-1435 du 23 novembre 2020 (JORFTEXT000042558725, du 25 novembre
2020). Art. 8 (JORFARTI000042558759) : « Dans le tableau de l'article 14 du même décret, les
lignes relatives au grade de professeur technique hors classe sont remplacées par les lignes
suivantes : « Professeur technique hors classe 7e échelon - 6e échelon 3 ans 5e échelon 3 ans
4e échelon 2 ans 6 mois 3e échelon 2 ans 6 mois 2e échelon 2 ans 1er échelon 2 ans ». ».
Art. 2 (JORFARTI000042558743) : « L'article 14 du même décret est remplacé par lesdispositions
suivantes : « Art. 14.-I.-[…] GRADES ÉCHELONS DURÉE Professeur technique hors classe 6e échelon
- 5e échelon 3 ans […] » ; ses lignes de la classe normale sont celles de la version du LEGI de
2021, mot pour mot. Art. 11 (JORFARTI000042558764) : « Les dispositions du chapitre Ier et des
articles 9 et 10 entrent en vigueur le 1er septembre 2017. Les dispositions du chapitre III
entrent en vigueur le 1er janvier 2021. »

*Le motif écrit* (`non_lus.csv`, ligne 74) : « un échelon manque dans « Professeur technique
hors classe » ; la consolidation du LEGI saute le 5e échelon, que le décret publié écrit :
décret n° 2020-1435 du 23 novembre 2020, art. 8 (JORFARTI000042558759, JORF du 25 novembre
2020), « Professeur technique hors classe 7e échelon - 6e échelon 3 ans 5e échelon 3 ans
4e échelon 2 ans 6 mois … », « 5e échelon 3 ans » » : la citation est celle de l'art. 8, mot
pour mot ; le motif est juste.

*La date d'effet de l'art. 8.* Les douze articles du décret portent leur seul numéro dans
l'index ; aucun ne dit son chapitre. L'art. 11 date le chapitre Ier, les art. 9 et 10 et le
chapitre III, pas le chapitre II ; la notice du texte, lue ici, ajoute : « Les dispositions du
chapitre II entrent en vigueur en 2020 ». L'art. 8 peut donc être du chapitre II (2020) ou du
chapitre III (1er janvier 2021) : l'index ne le dit pas, et ne pas rendre le tableau est juste.
B2-ter ne cite pas cette phrase de la notice ; elle renforce sa raison.

## 3. La règle du quart des agents chefs : conforme

*N° 91-45.* Au LEGI, art. 32, LEGIARTI000006710496, du 7 août 2007 au 30 juin 2011 : « Les
durées moyenne et minimale du temps passé dans les échelles prévues dans le décret
n° 2006-227 du 24 février 2006 modifié sont fixées dans les conditions précisées par ledit
décret. Les durées moyennes et minimales du temps passé dans les échelons des grades du corps
des agents chefs sont égales respectivement à l'ancienneté moyenne et à l'ancienneté moyenne
réduite du quart. » Le tableau, art. 6, LEGIARTI000006710407, du 25 juin 2007 au 30 juin 2011 :
« L'ancienneté moyenne pour accéder à l'échelon supérieur de chacun des grades du corps des
agents chefs est ainsi fixée : ÉCHELON ANCIENNETÉ MOYENNE […] ». Au JORF, décret n° 2007-1185,
art. 10 (JORFARTI000001693140, du 7 août 2007) : « b) Le deuxième alinéa de l'article 57 qui
devient l'article 32 est ainsi rédigé : « Les durées moyennes et minimales du temps passé dans
les échelons des grades du corps des agents chefs sont égales respectivement à l'ancienneté
moyenne et à l'ancienneté moyenne réduite du quart. » » ; art. 3 (JORFARTI000001115574) : « « Art.
6. - L'ancienneté moyenne pour accéder à l'échelon supérieur de chacun des grades du corps des
agents chefs est ainsi fixée : ».

*N° 91-936.* Au LEGI, art. 29, LEGIARTI000018616899, du 7 avril 2008 au 26 janvier 2012, en
entier : « Les durées moyennes et minimales du temps passé dans les échelons des grades du corps
des agents-chefs sont égales respectivement à l'ancienneté moyenne et à l'ancienneté moyenne
réduite du quart. » Le tableau, art. 6, LEGIARTI000018616795, mêmes dates : « L'ancienneté
moyenne requise pour accéder à l'échelon supérieur de chacun des grades du corps des
agents-chefs est fixée conformément au tableau suivant : […] ». Au JORF, décret n° 2008-319,
art. 6 (JORFARTI000018571778, du 6 avril 2008) : « 5° Le second alinéa de l'article 45, qui
devient l'article 29, est remplacé par les dispositions suivantes : « Les durées moyennes et
minimales du temps passé dans les échelons des grades du corps des agents-chefs sont égales
respectivement à l'ancienneté moyenne et à l'ancienneté moyenne réduite du quart. » » ; art. 2
(JORFARTI000018571736) : « « Art. 6.-L'ancienneté moyenne requise pour accéder à l'échelon
supérieur de chacun des grades du corps des agents-chefs est fixée conformément au tableau
suivant : ».

*Au dépôt.* `tableaux.csv` porte, pour LEGIARTI000006710407 et LEGIARTI000018616795, la phrase
de la règle égale au texte du LEGI, et l'article qui l'écrit (LEGIARTI000006710496,
LEGIARTI000018616899) ; ce sont les deux seuls tableaux à `regle_du_quart_article`. Recompté :
36 tableaux à moyenne seule, dont 12 avec la règle ; aucune règle hors des tableaux à moyenne
seule. Pour les 24 autres, aucun article de leur texte au LEGI (recherche sur le numéro du
texte, toutes versions, « réduite », « minorée » ou « majorée du quart », au singulier ou au
pluriel) n'écrit la règle à des dates qui recouvrent les leurs : 24 sur 24, comme B2-ter.

*Réserve, déclarée par B2-ter.* Du 25 juin au 7 août 2007, le tableau du n° 91-45 est daté et
la règle pas encore : la colonne ne le dit pas, sa note le dit. Les huit articles du
n° 2007-1185 dans l'index (art. 3, 4, 5, 7, 8, 10, 11 et un sans numéro) ne datent pas son
entrée en vigueur ; on y lit des reclassements dont « La première tranche interviendra à
compter du 25 juin 2007 ».

## 4. Les coquilles de B2-bis : conforme, une précision

- *N° 67-715.* JORFTEXT000000513902 : « Décret n°67-715 du 16 août 1967 RELATIF AU STATUT
  PARTICULIER DU CORPS DES INGENIEURS DES TELECOMMUNICATIONS » ; LEGIARTI000006508433 :
  « Décret n°67-715 du 16 août 1967 relatif au statut particulier du corps des ingénieurs des
  télécommunications ». Le commentaire du test dit désormais « du 16 août 1967 » (d75b842).
- *39 versions.* Recompté de f28cdbd^ à f28cdbd, `non_lus.csv`, ligne à ligne : 1 633 lignes
  avant, 1 249 après ; 481 ôtées, 97 écrites ; 39 versions perdent des lignes, 409 en tout
  (481 ôtées moins les 72 réécrites pour ces versions) ; 25 versions, absentes avant, gagnent
  chacune une ligne ; aucune n'en gagne d'autre. Les « 39 versions » sont justes.
- **Écart faible, de rédaction.** La note de B2-ter écrit « 409 lignes en moins, en 39 versions
  (481 ôtées, 97 écrites dont 72 pour des versions déjà consignées) » : 409 est la baisse des
  39 versions qui perdent des lignes, non celle du fichier, qui perd 384 lignes (481 − 97),
  25 lignes étant écrites pour 25 versions neuves, que la phrase ne nomme pas. Aucune donnée
  n'en est fausse.

## 5. Le trou du motif : conforme

*Le recompte.* Le script de la note de B2-ter, recopié, lancé à la racine sur l'index du
même incrément, avec le motif `DUREES_D_ECHELON` de `dila_index.py`, qui n'a pas changé depuis
39643e8 (`git log 39643e8..origin/main -- scripts/fetch/dila_index.py` : rien) : **102**
versions ; **58** articles (titre du texte et numéro de l'article) ; **48** textes ; aucune
dans `tableaux.csv` (colonnes `article` et `versions`) ni dans `non_lus.csv` ; 52 de textes de
`textes.csv` ; 20 d'articles dont une autre version y est. Les cinq que B2-ter range hors des
durées, relues ici : n° 75-62, art. 18, deux versions (LEGIARTI000028929424,
LEGIARTI000051290410), « Après six mois d'ancienneté : un mois à plein traitement et un mois à
demi traitement » (congés de maladie) ; n° 95-869, art. 20 (LEGIARTI000006479528), « L'accès
aux différents grades d'avancement de la catégorie A du Trésor public est ouvert dans les
conditions prévues au tableau ci-après » ; n° 82-1067, art. 30 (LEGIARTI000006502669),
« bénéficient, lors de ce reclassement, d'une bonification d'ancienneté d'échelon » ;
n° 2001-188, art. 14 (LEGIARTI000052464782), « Situation dans le grade de capitaine de port de
2 e classe Situation dans le grade de capitaine de port de 1 re classe Ancienneté attribuée ou
conservée ». Pas des durées d'échelon : 5 versions, 4 articles, 4 textes, chacun sans autre
version dans les 102. Restent **97**, **54**, **44**.

*Le tirage.* Trois versions parmi les 97, triées par identifiant, graine **20261103** :

- LEGIARTI000006457982, décret n° 90-90 du 24 janvier 1990 (professeurs de lycée
  professionnel agricole), art. 18, du 31 décembre 2003 au 1er septembre 2017 : « ECHELONS
  GRAND CHOIX CHOIX ANCIENNETE Du 1er au 2e 3 mois Du 2e au 3e 9 mois Du 3e au 4e 1 ans Du 4e au
  5e 2 ans 2 ans 6 mois 2 ans 6 mois […] ». **Un tableau de durées d'échelon**, d'un échelon au
  suivant.
- LEGIARTI000006562645, décret n° 82-700 du 6 août 1982 (professeurs des écoles nationales
  d'art), art. 13-1, du 29 mai 1998 au 27 décembre 2002 : « I - ECHELONS : Du 1er au 2e
  échelon ; II - ANCIENNETE : 2 ans 6 mois ; I - ECHELONS : Du 2e au 3e échelon ; II -
  ANCIENNETE : 2 ans 6 mois ; […] ». **Un tableau de durées d'échelon**, en fiches.
- LEGIARTI000006700221, décret n° 96-182 du 7 mars 1996 (pharmaciens des hôpitaux à temps
  partiel), art. 18, du 13 mars 1996 au 31 mars 2001, en entier : « L'avancement d'échelon
  s'effectue selon les durées suivantes : 9e échelon : trois ans ; 8e échelon : trois ans ;
  7e échelon : deux ans et demi ; […] 1er échelon : un an. L'avancement d'échelon est prononcé
  par le préfet du département. » **Une liste de durées d'échelon.**

Trois sur trois sont des durées d'échelon. Le trou est consigné où B2-ter le dit : la
documentation du lecteur (« 97 versions au moins ») et la note de la source `dila_legi_durees`
de `data/sources.yaml` ; les trois citations de cette note (« L'avancement d'échelon s'effectue
selon les durées suivantes : 1er échelon : un an », « CONDITIONS d'accès à l'échelon »,
« GRAND CHOIX CHOIX ANCIENNETÉ ») se trouvent, mot pour mot, dans 5, 20 et 6 des 102 versions.

*Le code* (bloc-notes, hors du dépôt, lancé à la racine) :

```python
"""Recompte du trou du motif DUREES_D_ECHELON et tirage de trois versions (R-B2-ter).
Lecture seule. Le filtre est celui de la note de B2-ter."""
import csv, random, re, sqlite3, sys
sys.path.insert(0, 'scripts/fetch')
from dila_index import DUREES_D_ECHELON
c = sqlite3.connect('file:data/brut/dila/legi.sqlite?mode=ro', uri=True)
N = r"(?:\d{1,2}|un|une|deux|trois|quatre|cinq|six)"
DUREE = rf"{N}\s*(?:ans?|mois)\b"
PAIRE = re.compile(rf"[ée]chelon\s*:?\s*{DUREE}", re.I)
DU_AU = re.compile(rf"\bdu\s+\d+\s*(?:er|e|ème)\s+(?:[ée]chelon\s+)?au\s+\d+\s*(?:e|ème)\b"
                   rf"[^.]{{0,40}}?{DUREE}", re.I)
APRES = re.compile(rf"\bapr[èe]s\s+{DUREE}\s+(?:dans|d.anciennet)", re.I)
trouves = [(i, n, t) for i, n, t, texte in c.execute(
               "SELECT id, num, titre, texte FROM doc WHERE nature LIKE 'Article%'")
           if texte and not DUREES_D_ECHELON.search(texte)
           and (len(PAIRE.findall(texte)) >= 3 or len(DU_AU.findall(texte)) >= 2
                or len(APRES.findall(texte)) >= 2)]
print(len(trouves), len({(t, n) for _, n, t in trouves}), len({t for *_, t in trouves}))
lire = lambda f: list(csv.DictReader(
    l for l in open(f'data/reference/grilles/durees/{f}.csv', encoding='utf-8')
    if not l.startswith('#')))
tab, nl = lire('tableaux'), lire('non_lus')
au_depot = ({r['article'] for r in tab + nl}
            | {v for r in tab for v in r['versions'].split()})
print(sum(i in au_depot for i, *_ in trouves))                       # 102 58 48, puis 0
CINQ = {'LEGIARTI000028929424', 'LEGIARTI000051290410', 'LEGIARTI000006479528',
        'LEGIARTI000006502669', 'LEGIARTI000052464782'}
durees = sorted(i for i, *_ in trouves if i not in CINQ)
print(len(durees), random.Random(20261103).sample(durees, 3))         # 97, les trois
```

## 6. Les tests, la certification, le paquet : conforme

*Les valeurs viennent des textes.* B2-ter ajoute 5 tests (35 avant, 40 après) :
`test_une_coquille_du_legi_se_corrige_sur_la_preuve_du_jorf`,
`test_la_redaction_d_origine_des_charges_de_recherche_est_lue`,
`test_un_refus_dit_ce_que_le_decret_publie_ecrit_et_que_le_legi_perd`,
`test_la_regle_ecrite_dans_un_autre_article_se_cite_mot_pour_mot`,
`test_la_regle_ecrite_dans_un_autre_article_est_consignee_avec_la_moyenne`, et passe le compte
de `test_la_regle_du_quart_est_consignee_avec_la_moyenne` à (36, 12). Les textes recopiés dans
le fichier de tests sont, au caractère près, ceux de l'index : `CHARGES_DE_RECHERCHE_1984` égale
LEGIARTI000027940471, `ARTICLE_32_91_45` égale LEGIARTI000006710496, `QUART_91_936` égale
LEGIARTI000018616899 (comparaison par `==`). Les durées attendues
(`CHARGES_DE_RECHERCHE_1984_DUREES`) sont celles du tableau du point 1, comptées à la main ;
les citations du test du refus sont celles de l'art. 8 du n° 2020-1435.

*Ils mordent.* Une valeur faussée à la fois, dans la copie à part, puis le fichier remis :

| Mutation | Test qui échoue |
|---|---|
| `lignes.csv`, deuxième classe, 4e échelon : 17 → 18 | `test_la_redaction_d_origine_des_charges_de_recherche_est_lue` |
| `tableaux.csv`, fin du tableau corrigé : 1990-08-04 → 1990-08-05 | le même |
| `COQUILLES_DU_LEGI` du lecteur, date retenue : 1990-08-04 → 1990-08-05 | `test_une_coquille_du_legi_se_corrige_sur_la_preuve_du_jorf` |
| `non_lus.csv`, motif du refus : « 5e échelon 3 ans » → « 5e échelon 2 ans » | `test_un_refus_dit_ce_que_le_decret_publie_ecrit_et_que_le_legi_perd` |
| `tableaux.csv`, règle du n° 91-45 : « réduite du quart » → « réduite du tiers » | `test_la_regle_ecrite_dans_un_autre_article_est_consignee_avec_la_moyenne` |
| `tableaux.csv`, article de la règle du n° 91-936 → l'art. 6 | le même |
| `tableaux.csv`, la règle du n° 2014-99, art. 10, ôtée | `test_la_regle_du_quart_est_consignee_avec_la_moyenne` |

7 sur 7, chacune un seul test, celui qui la vise. (Au premier essai de la quatrième, un
bytecode périmé du lecteur, laissé par la troisième dans la copie, faisait échouer aussi le
test de la coquille ; relancée sans bytecode, elle n'en fait échouer qu'un.)

*La certification.* Dans la copie à part, au dernier `main` (ee67f54) : le lecteur relancé
(`dila_legi_durees.py --index …`, 727 textes, 340 avec un tableau lu, 778 tableaux,
14 521 lignes, 1 248 non lus) redonne les 14 521 lignes de `lignes.csv`, à l'ordre près ;
`verifier_donnees.py` : « durees_echelon_rang : 14521 valeurs confrontables […] 14521
identiques, 0 corrigées, 0 ajoutées », « durees_echelon_duree : 8639 […] 8639 identiques »,
moyenne 3 323, minimale 3 462, maximale 1 060, toutes identiques ; `--appliquer` remet
`lignes.csv` dans l'ordre commité et ne change, dans `data/derive/certification.json`, que la
date de recontrôle de huit séries qui ne sont pas des durées. Dans la copie de travail, sans
le fichier brut du lecteur, `verifier_donnees.py` dit les cinq séries « IGNORÉ » et n'écrit
rien.

*Le paquet.* `construire_donnees.py`, dans la copie à part au dernier `main` (ee67f54) : `git
status` vide, rien ne change.

## Ce qui n'a pas été vérifié

- Le tableau de 1990 du n° 83-1260, art. 34 (LEGIARTI000027940483) : hors de cette relecture,
  comme B2-ter le dit ; au JORF, il n'est qu'en image.
- La règle d'entrée en vigueur d'un décret de 1990 sans article qui la fixe (point 1) : non
  lue.
- Le chapitre de l'art. 8 du n° 2020-1435 (point 2) : l'index ne le porte pas.
