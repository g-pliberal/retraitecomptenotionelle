# Retouches de la relecture R-B2-bis des durées d'échelon (file B2-ter)

File B2-ter, le 3 novembre 2026 : ce que la relecture R-B2-bis
(`2026-11-03-relecture-corrections-r-b2.md`, commit 3dd70c4) laisse, chaque point rouvert
ici dans le texte avant d'écrire une ligne. Rien n'est repris de R-B2-bis ni de mémoire. Les
sources : l'index LEGI publié du dépôt, récupéré sans reconstruction
(`dila_index.py legi --recuperer`, à jour de l'incrément 20261102-213929, celui de B2-bis et
de R-B2-bis), et l'index JORF publié (`--recuperer`, à jour de l'incrément 20261103-002311),
interrogés par `dila_cherche.py` (`--num … --titre`, `--texte`) et directement dans leur table
`doc`. Commits : 34c2ab3 (point 1, le paquet et la page Méthode), 920758d (point 3), 299deb8
(point 2), cff6ebe (point 4), puis celui de cette note (point 5).

## 1. Le n° 83-1260, art. 34 : une coquille du LEGI, prouvée au JORF

*Au LEGI.* `dila_cherche.py legi --num 34 --titre 83-1260` : LEGIARTI000027940471,
« 1984-01-08 → 1980-08-04 (jamais en vigueur) », puis LEGIARTI000027940483, « 1990-08-04 →
2002-02-03 ». La première écrit : « Les chargés de recherche qui réunissent dans leur grade les
conditions d'ancienneté d'échelon fixées au tableau ci dessous peuvent bénéficier d'un
aVancement d'échelon : GRADES ET ECHELONS ANCIENNETE REQUISE dans l'échelon Chargés de
recherche de première classe 9e échelon Echelon terminal 8e échelon 3 ans […] 1er échelon
2 ans Chargés de recherche de deuxième classe 6e échelon Echelon terminal 5e échelon 2 ans
4e échelon 1 an 5 mois 3e échelon 1 an 4 mois 2e échelon 1 an 3 mois 1er échelon 1 an […] ».

*Au JORF, le texte qui remplace le tableau.* Le décret n° 90-685 du 27 juillet 1990
(JORFTEXT000000350640, publié le 3 août 1990), **art. 5** (JORFARTI000000984252) : « Art. 5. -
Le tableau de l'article 34 du décret du 30 décembre 1983 susvisé est remplacé par le tableau
ci-dessous: […] Vous pouvez consulter le tableau dans le JO no 0178 du 03/08/1990 ». Sa
notice : « MODIFICATION DES ART. 12,15,18,26 (AL. 1),27 (DERNIER AL.),34 (TABLEAU),35, […] » ;
ses visas : « Vu le décret no 83-1260 du 30 décembre 1983 […], modifié par le décret no 88-1072
du 24 novembre 1988 et le décret no 89-74 du 4 février 1989 ».

*Au JORF, rien d'autre de 1984 à 1990.* Recherche dans l'index, du 8 janvier 1984 au
3 août 1990, des textes qui citent « 83-1260 », « 831260 », « 30 décembre 1983 » avec
« scientifiques et technologiques », ou « établissements publics scientifiques et
technologiques » : **26 textes**. Trois seulement modifient le n° 83-1260 : le n° 90-685, et
les deux de ses visas. Le n° 88-1072 (JORFTEXT000000504532, JO du 30 novembre 1988) :
« MODIFICATION DES ART. 104 ET 185 DU DECRET 831260 DU 30-12-1983 » ; le n° 89-74
(JORFTEXT000000509890, JO du 5 février 1989) : « LA PROPORTION DE 28% VISEE AUX ART. 104 ET
185 (AL. 2) DU DECRET SUSVISE EST PORTEE A 30% ». Les 23 autres, 9 décrets (des statuts
particuliers qui l'appliquent, « Ces corps de fonctionnaires sont régis par les dispositions du
décret n° 83-1260 du 30-12-1983 et celles du présent décret », n° 84-1207 ; le statut de
l'INRIA, n° 86-576, qui y « déroge sur certains points », pour le classement à l'entrée dans
le corps ; deux décrets qui modifient des statuts particuliers ; le n° 86-575, sur la retenue
pour pension) et 14 arrêtés (équivalences des art. 26 et 48, échelonnement indiciaire, commissions),
ne nomment l'article 34 ni dans leur titre ni dans leur notice ; et aucun article de l'index,
à ces dates, qui écrit « scientifiques et technologiques » et « 34 », n'est d'un autre texte
que le n° 90-685.

*La rédaction de 1984 au JORF.* Les 57 articles du décret publiés le 7 janvier 1984
(JORFTEXT000000316777) sont **vides** dans l'index : le texte de 1984 ne s'y lit pas. Le
contenu vient donc de la version du LEGI.

*Établi.* La fin « 4 août 1980 » est une coquille du LEGI pour le **4 août 1990** : le jour où
le LEGI fait commencer la version suivante, au lendemain du JO du 3 août 1990 qui publie le
tableau qui la remplace. La rédaction d'origine vaut du 8 janvier 1984 (date du LEGI) au
4 août 1990 (fin exclue).

*La correction* (34c2ab3). `COQUILLES_DU_LEGI` du lecteur nomme la version, le champ, ce que
le LEGI écrit (1980-08-04), ce que le dépôt retient (1990-08-04) et la preuve ; `corriger` ne
corrige que si le LEGI écrit encore la coquille relevée. La colonne neuve `correction` de
`tableaux.csv` la dit, mot pour mot : « fin corrigée : le LEGI écrit 1980-08-04, coquille pour
1990-08-04 ; au JORF, le décret n° 90-685 du 27 juillet 1990, art. 5 (JORFARTI000000984252),
publié au JO n° 178 du 3 août 1990, remplace ce tableau […] ; le contenu est celui de la
version du LEGI, les articles du JORF de 1984 étant vides dans l'index ». Les **15 lignes**
rentrent, certifiées : première classe, du 9e au 1er, —, 36, 36, 36, 30, 30, 30, 30, 24 ;
deuxième classe, du 6e au 1er, —, 24, 17, 16, 15, 12 (en mois). La ligne de `non_lus.csv`
s'en va. Tests : `test_une_coquille_du_legi_se_corrige_sur_la_preuve_du_jorf`,
`test_la_redaction_d_origine_des_charges_de_recherche_est_lue` (le texte recopié du LEGI, les
durées comptées à la main) ; `JAMAIS_EN_VIGUEUR` passe de sept versions à six.

## 2. Le 22e refus : la raison écrite corrigée

*Au LEGI.* N° 96-1113, art. 14, LEGIARTI000042571828, depuis le 1er janvier 2021 :
« Conformément au décret n° 2020-1435 du 23 novembre 2020, les présentes dispositions entrent
en vigueur le 1er janvier 2021. I.-[…] GRADES ÉCHELONS DURÉE Professeur technique hors classe
7e échelon - 6e échelon 3 ans 4e échelon 2 ans 6 mois 3e échelon 2 ans 6 mois 2e échelon 2 ans
1er échelon 2 ans Professeur technique de classe normale 11e échelon - […] ». Le 5e échelon
manque : le refus est juste, le lecteur n'invente pas une ligne.

*Au JORF.* Le décret n° 2020-1435 du 23 novembre 2020 (JORFTEXT000042558725, publié le
25 novembre 2020), **art. 8** (JORFARTI000042558759) : « Dans le tableau de l'article 14 du même
décret, les lignes relatives au grade de professeur technique hors classe sont remplacées par
les lignes suivantes : « Professeur technique hors classe 7e échelon - 6e échelon 3 ans
**5e échelon 3 ans** 4e échelon 2 ans 6 mois 3e échelon 2 ans 6 mois 2e échelon 2 ans 1er échelon
2 ans ». » ; art. 11 (JORFARTI000042558764) : « Les dispositions du chapitre Ier et des
articles 9 et 10 entrent en vigueur le 1er septembre 2017. Les dispositions du chapitre III
entrent en vigueur le 1er janvier 2021. » C'est donc la consolidation du LEGI qui perd le
5e échelon, non le décret.

*La correction* (299deb8). `ABIMEES_PAR_LE_LEGI` ajoute au motif du refus, dans
`non_lus.csv` : « un échelon manque dans « Professeur technique hors classe » ; la
consolidation du LEGI saute le 5e échelon, que le décret publié écrit : décret n° 2020-1435 du
23 novembre 2020, art. 8 (JORFARTI000042558759, JORF du 25 novembre 2020), « Professeur
technique hors classe 7e échelon - 6e échelon 3 ans 5e échelon 3 ans 4e échelon 2 ans 6 mois
… », « 5e échelon 3 ans » ». La phrase de B2-bis (« saute le 5e échelon ») est corrigée dans sa
note et son entrée de veille (cff6ebe). Test :
`test_un_refus_dit_ce_que_le_decret_publie_ecrit_et_que_le_legi_perd`.

*Le JORF permet-il de lire le tableau complet ?* **Oui**, en deux articles du même décret :
l'**art. 2** (JORFARTI000042558743) remplace tout l'article 14 au 1er septembre 2017 (« GRADES
ÉCHELONS DURÉE Professeur technique hors classe 6e échelon - 5e échelon 3 ans […] Professeur
technique de classe normale 11e échelon - 10e échelon 4 ans 9e échelon 4 ans 8e échelon 3 ans
6 mois 7e échelon 3 ans 6e échelon 3 ans 5e échelon 2 ans 6 mois 4e échelon 2 ans 3e échelon
2 ans 2e échelon 1 an 1er échelon 1 an ») ; l'art. 8 en remplace les lignes du grade hors
classe. Les lignes de la classe normale de l'art. 2 sont celles de la version du LEGI de 2021,
mot pour mot. *Pas rendu ici*, pour deux raisons que l'index ne lève pas : le découpage du
décret en chapitres n'y est pas (ses articles n'y portent que leur numéro), et que l'art. 8
soit du chapitre III, en vigueur le 1er janvier 2021, ne se lit qu'à la date que le LEGI donne
à la version ; et des textes qui citent le n° 96-1113 publiés depuis le 25 novembre 2020, tous
sont des arrêtés, sauf le décret n° 2021-1392 du 26 octobre 2021, « adaptation de divers statuts
particuliers de fonctionnaires », qui le vise (« Vu le décret n° 96-1113 du 19 décembre 1996
modifié […] ») mais dont l'index ne garde qu'un article, l'art. 157, sur un autre statut : ce
qu'il fait du n° 96-1113 ne se lit pas dans l'index (l'index LEGI ne connaît aucune version de
l'article 14 après celle du 1er janvier 2021). Le tableau reste refusé, à relire à la main avec
les autres refus.

## 3. La règle du quart écrite dans un autre article

*Au LEGI.* N° 91-45, art. 6, LEGIARTI000006710407, du 25 juin 2007 au 30 juin 2011 :
« L'ancienneté moyenne pour accéder à l'échelon supérieur de chacun des grades du corps des
agents chefs est ainsi fixée : ÉCHELON ANCIENNETÉ MOYENNE […] » ; son **art. 32**,
LEGIARTI000006710496, du 7 août 2007 au 30 juin 2011 : « Les durées moyenne et minimale du
temps passé dans les échelles prévues dans le décret n° 2006-227 du 24 février 2006 modifié
sont fixées dans les conditions précisées par ledit décret. Les durées moyennes et minimales du
temps passé dans les échelons des grades du corps des agents chefs sont égales respectivement
à l'ancienneté moyenne et à l'ancienneté moyenne réduite du quart. » N° 91-936, art. 6,
LEGIARTI000018616795, du 7 avril 2008 au 26 janvier 2012 : « L'ancienneté moyenne requise pour
accéder à l'échelon supérieur de chacun des grades du corps des agents-chefs est fixée
conformément au tableau suivant : […] » ; son **art. 29**, LEGIARTI000018616899, mêmes dates :
« Les durées moyennes et minimales du temps passé dans les échelons des grades du corps des
agents-chefs sont égales respectivement à l'ancienneté moyenne et à l'ancienneté moyenne
réduite du quart. »

*Au JORF.* Le décret n° 2007-1185 du 3 août 2007 (publié le 7 août 2007) écrit l'un et
l'autre : art. 3 (JORFARTI000001115574), la section des agents chefs et son « Art. 6. -
L'ancienneté moyenne pour accéder à l'échelon supérieur de chacun des grades du corps des
agents chefs est ainsi fixée : » ; art. 10 (JORFARTI000001693140) : « b) Le deuxième alinéa de
l'article 57 qui devient l'article 32 est ainsi rédigé : « Les durées moyennes et minimales du
temps passé dans les échelons des grades du corps des agents chefs sont égales respectivement à
l'ancienneté moyenne et à l'ancienneté moyenne réduite du quart. » ». Le décret n° 2008-319 du
4 avril 2008 (publié le 6 avril 2008), art. 2 (JORFARTI000018571736), « « Art. 6.-L'ancienneté
moyenne requise pour accéder à l'échelon supérieur de chacun des grades du corps des
agents-chefs est fixée conformément au tableau suivant : » », et art. 6 (JORFARTI000018571778) :
« 5° Le second alinéa de l'article 45, qui devient l'article 29, est remplacé par les
dispositions suivantes : « Les durées moyennes et minimales du temps passé dans les échelons
des grades du corps des agents-chefs sont égales respectivement à l'ancienneté moyenne et à
l'ancienneté moyenne réduite du quart. » ».

*La correction* (920758d). `REGLE_AILLEURS` nomme, pour ces deux tableaux, la version de
l'article qui écrit la règle ; `regle_de_l_anciennete` l'y lit, dans l'index, mot pour mot ;
`tableaux.csv` la porte dans `regle_du_quart`, comme pour les dix autres, et l'article dans la
colonne neuve `regle_du_quart_article` (vide pour les dix : le même article). Aucune durée n'en
est déduite. Des 36 tableaux à moyenne seule, **12** portent la règle (10 avant). Tests :
`test_la_regle_ecrite_dans_un_autre_article_se_cite_mot_pour_mot`,
`test_la_regle_ecrite_dans_un_autre_article_est_consignee_avec_la_moyenne`, et le compte de
`test_la_regle_du_quart_est_consignee_avec_la_moyenne` (36, 12).

*Contre-vérification.* Pour les 24 autres tableaux à moyenne seule, aucun article de leur
texte, dans l'index, n'écrit « réduite », « minorée » ou « majorée du quart » à des dates qui
recouvrent les leurs (recherche sur tous les articles du texte, toutes versions).

*Ce que le texte ne tranche pas.* Au n° 91-45, le tableau de l'art. 6 commence au LEGI le
25 juin 2007, la règle de l'art. 32 le 7 août 2007, alors que le même décret, n° 2007-1185,
écrit l'un et l'autre ; son article d'entrée en vigueur n'est pas dans l'index (on y lit
seulement, à son art. 11, des reclassements « à compter du 25 juin 2007 »). Du 25 juin au
7 août 2007, la règle n'est donc pas prouvée en vigueur ; la colonne ne le dit pas, cette note
le dit.

## 4. Les coquilles de B2-bis

- Le commentaire du test des fiches datait le n° 67-715 « du 18 août 1967 » ; le JORF
  (JORFTEXT000000513902 : « Décret n°67-715 du 16 août 1967 RELATIF AU STATUT PARTICULIER DU
  CORPS DES INGENIEURS DES TELECOMMUNICATIONS ») et le LEGI (LEGIARTI000006508433 : « Décret
  n°67-715 du 16 août 1967 relatif au statut particulier du corps des ingénieurs des
  télécommunications ») disent **16** : corrigé (cff6ebe).
- « 409 lignes de `non_lus.csv` s'en vont (38 versions d'article) » : recompté ici, de
  f28cdbd^ à f28cdbd, version par version (lignes ôtées moins lignes écrites) : 409 lignes en
  moins, en **39** versions (481 ôtées, 97 écrites dont 72 pour des versions déjà consignées,
  comme R-B2-bis l'a dit) : corrigé dans la note de B2-bis.

## 5. Le trou hérité de B2 : mesuré, consigné, non forcé

*La mesure.* Un script du bloc-notes, hors du dépôt, lancé depuis la racine à 299deb8, lit tous
les articles de l'index LEGI que le motif des durées (`DUREES_D_ECHELON`, de `dila_index.py`)
ne retient pas, et garde ceux qui portent la signature d'un tableau de durées :

```python
"""Le trou du lecteur des durées : les articles du LEGI à tableau de durées que le motif
DUREES_D_ECHELON ne retient pas. Comptage sur l'index, en lecture seule."""
import re, sqlite3, sys
sys.path.insert(0, 'scripts/fetch')
from dila_index import DUREES_D_ECHELON
c = sqlite3.connect('file:data/brut/dila/legi.sqlite?mode=ro', uri=True)
N = r"(?:\d{1,2}|un|une|deux|trois|quatre|cinq|six)"
DUREE = rf"{N}\s*(?:ans?|mois)\b"
PAIRE = re.compile(rf"[ée]chelon\s*:?\s*{DUREE}", re.I)            # « 8e échelon 3 ans »
DU_AU = re.compile(rf"\bdu\s+\d+\s*(?:er|e|ème)\s+(?:[ée]chelon\s+)?au\s+\d+\s*(?:e|ème)\b"
                   rf"[^.]{{0,40}}?{DUREE}", re.I)                   # « Du 1er au 2e 3 mois »
APRES = re.compile(rf"\bapr[èe]s\s+{DUREE}\s+(?:dans|d.anciennet)", re.I)  # « Après 1 an dans »
trouves = [ident for ident, texte in c.execute(
               "SELECT id, texte FROM doc WHERE nature LIKE 'Article%'")
           if texte and not DUREES_D_ECHELON.search(texte)
           and (len(PAIRE.findall(texte)) >= 3 or len(DU_AU.findall(texte)) >= 2
                or len(APRES.findall(texte)) >= 2)]
print(len(trouves))   # 102
```

**102 versions d'article**, de 58 articles, de 48 textes ; aucune n'est dans `tableaux.csv` ni
dans `non_lus.csv` (52 sont de textes déjà au dépôt, 20 d'articles dont une autre version y
est). Chaque article relu ici, dans une de ses versions, au début de son texte et autour de sa
première signature, puis rangé :

| Famille | Versions | Articles | Textes | Exemple, mot pour mot |
|---|---|---|---|---|
| Durées d'échelon à échelon, au grand choix, au choix, à l'ancienneté | 21 | 17 | 13 | n° 90-680, art. 24, LEGIARTI000006459200 : « ÉCHELONS GRAND CHOIX CHOIX ANCIENNETÉ Du 1er au 2e 3 mois Du 2e au 3e 9 mois » |
| Durée par échelon, en liste (praticiens et pharmaciens des hôpitaux, conseillers techniques et pédagogiques supérieurs, secrétaire général adjoint de la grande chancellerie de la Légion d'honneur) | 28 | 10 | 7 | code de la santé publique, R6152-218 : « L'avancement d'échelon s'effectue suivant les durées suivantes : 1er échelon : un an ; 2e échelon : un an ; 3e échelon : deux ans » |
| Durée en fiches dans un arrêté d'échelonnement | 4 | 3 | 2 | arrêté du 1er octobre 1980, annexe I : « 1re classe, 5e échelon : Indices bruts : 741. Durée moyenne d'ancienneté dans l'échelon : 4 ans » |
| Conditions d'accès aux échelons (militaires, juridictions) | 41 | 21 | 19 | n° 2010-1239, art. 24, LEGIARTI000042864809 : « ANCIENNETE DE GRADES OU D'ECHELONS EXIGEE pour accéder à l'échelon […] Echelon spécial Après 1 an dans l'échelon précédent » |
| Durées en phrases | 3 | 3 | 3 | n° 93-658, art. 6 : « L'ancienneté pour accéder à l'échelon supérieur est d'un an dans le 1er échelon, de deux ans du 2e au 6e échelon » |
| Pas des durées d'échelon | 5 | 4 | 4 | n° 75-62, art. 18 : « Après six mois d'ancienneté : un mois à plein traitement » (congés de maladie) ; n° 95-869, art. 20 (accès aux grades) ; n° 82-1067, art. 30 (bonification au reclassement) ; n° 2001-188, art. 14 (classement au grade supérieur) |

Soit **97 versions** de tableaux ou de phrases de durées, de 54 articles, de 44 textes, que le
lecteur ne voit pas. C'est un plancher : la signature ne voit pas un tableau dont aucune case
ne met une durée juste après « échelon ».

*La décision.* Ils sont **nombreux**, et de cinq formes. Le lecteur ne les voit pas même comme
tableaux : la phrase qui annonce un tableau se reconnaît au même motif (`annonce_des_durees`),
et `tableaux` n'en trouve aucun, ni `_en_prose` de phrase de durées, dans une version de chaque
forme essayée ici (R6152-218, LEGIARTI000006918475 ; arrêté de 1980, LEGIARTI000006717992 ;
n° 2008-950, LEGIARTI000019483423 ; n° 90-680, LEGIARTI000006459200 ; n° 2010-1239,
LEGIARTI000042864809). Ce qu'il en ferait, motif élargi, n'est pas su : les faire lire est une
étape à elle, avec une contre-lecture, non une retouche. Rien n'est forcé :
le trou est consigné, avec son compte, dans la documentation du lecteur (« CE QUE LA DONNÉE NE
DIT PAS ») et dans la note de la source `dila_legi_durees` (`data/sources.yaml`) ; « 1 248 non
lus, avec leur raison » ne vaut que pour les articles que le motif retient. Le motif est dans
`dila_index.py`, qui n'est pas de cette file. Aucun de ces articles ne sert au calcul.

## Les comptes, avant et après

| | 3dd70c4 (avant) | après |
|---|---|---|
| Textes, dont avec un tableau lu | 727, 340 | 727, 340 |
| Tableaux (État, territoriale, hospitalière, militaires) | 777 (506, 178, 77, 16) | 778 (507, 178, 77, 16) |
| Lignes | 14 506 (8 400, 3 184, 1 787, 1 135) | 14 521 (8 415, 3 184, 1 787, 1 135) |
| Valeurs : rang, unique, moyenne, minimale, maximale | 14 506, 8 626, 3 323, 3 462, 1 060 | 14 521, 8 639, 3 323, 3 462, 1 060 |
| Non lus, dont avec un rang de tableau ; « jamais en vigueur » | 1 249, 750 ; 10 | 1 248, 749 ; 9 |
| Tableaux à moyenne seule, dont avec la règle du quart | 36, 10 | 36, 12 |
| Tableaux qui portent une correction de date | — | 1 |
| Valeurs recontrôlées (page Méthode) | 441 771 | 441 799 (+15 rangs, +13 durées) |

`python scripts/verifier_donnees.py --appliquer` certifie les 15 lignes (« 14521 identiques,
0 corrigées, 0 ajoutées » au rang ; 8 639 à la durée unique) ; seules les traces des séries
`durees_echelon_*` de `data/derive/certification.json` sont gardées, les dates des autres
séries refaites ce jour n'étant pas de cette file. `tests/test_durees_echelon.py` : 40 tests,
dont 5 ajoutés.

## Le site

Les durées ne servent pas au calcul des pensions : le modèle et son portage ne lisent pas
`data/reference/grilles/durees/`. Dans `moteur/donnees.json`, `construire_donnees.py` ne change,
de cette file, que la trace de certification de deux séries, `durees_echelon_rang` et
`durees_echelon_duree` (valeurs, identiques, empreinte) ; le paquet refait porte aussi la fiche
`majoration_enfants_agirc_arrco`, que la file M3 (488c30a) a écrite sans refaire le paquet, et
que GitHub aurait refaite. `construire_pages.py --verifier` ne trouvait périmée que la page
Méthode, refaite : seul y bouge le compte des valeurs recontrôlées, 441 771 → 441 799. Aucun
chiffre de pension ne bouge du fait de cette file.

## Ce qui n'a pas été vérifié, ce qui reste

- Le tableau de 1990 du n° 83-1260, art. 34, au JORF : il n'y est qu'en image (« Vous pouvez
  consulter le tableau dans le JO ») ; la version du LEGI qui le porte (LEGIARTI000027940483)
  n'a pas été recontrôlée ici.
- Le tableau complet du n° 96-1113, art. 14, en vigueur depuis 2021 : lisible au JORF, non
  rendu (point 2).
- La règle du n° 91-45 du 25 juin au 7 août 2007 (point 3).
- Les 97 versions hors du motif (point 5) : à lire dans une étape à elles, avant le chaînage
  s'il doit les rattacher.
- *Question au propriétaire, reprise de R-B2-bis.* Faut-il lire au JORF, à la main, les
  tableaux que la consolidation du LEGI abîme, à commencer par celui des professeurs techniques
  de la PJJ depuis le 1er janvier 2021 (décret n° 2020-1435, art. 2 et 8) ?
