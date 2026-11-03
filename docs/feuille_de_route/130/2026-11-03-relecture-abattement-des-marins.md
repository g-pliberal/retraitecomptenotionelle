# Relecture de l'abattement des marins au-delà du plafond de R. 11, 3°

File R-M1, le 3 novembre 2026 : relecture indépendante du commit e5dd612 (session M1,
note `2026-11-03-abattement-des-marins.md`). Chaque texte a été rouvert ici, sans rien
reprendre de la session ni de mémoire : l'index de la DILA, LEGI et JORF récupérés (à jour
de l'incrément du 2 novembre 2026, 20261102-213929), interrogé texte par texte, les
rédactions relevées par script ; hors de l'index, le rapport S2023-0865 de la Cour des
comptes, téléchargé et lu en entier, la question écrite n° 8440 de l'Assemblée nationale, un
document de formation du ministère de la mer, deux pages de l'ENIM et la page Légifrance de
l'arrêté du 31 décembre 1985. Rien n'a été modifié : ni règle, ni donnée, ni test, ni fiche ;
le paquet refait pour les essais l'a été hors commit, puis remis en l'état.

**Verdict.** Le point décisif est **conforme** : « le traitement brut correspondant à
l'indice 100 dans la fonction publique » de R. 11, 3° est celui que l'article 7 du décret
n° 85-1148 constitue de l'indice majoré de sa date — l'indice brut 100 —, et non celui de
l'indice majoré 100 ; aucune lecture contraire n'a été trouvée. Les citations sont exactes
mot pour mot, les vingt lignes de la série et leurs dates conformes aux textes, chaque
plafond de 2008 à 2026 se refait au centime, et aucune catégorie ne l'atteint de 2008 à
2026. **Écarts** : un moyen, sur une conclusion annoncée — « aucune catégorie de 1985 à
2007 » n'est pas prouvé, et les 79 % ne valent que pour la grille estimée du modèle (point
4) ; trois faibles — le paquet absent du commit, contre ce qu'écrit la note (point 5), la
limite absente de `docs/limites/` (point 6), deux lectures concurrentes de la série, sans
effet, non déclarées (point 2) ; deux négligeables — un arrondi de deux centimes (point 3),
la date de fin de l'article du décret de 1948 (point 1).

## 1. Les textes, à la version en vigueur

| Texte | Identifiant ouvert | Constat |
|---|---|---|
| Code des pensions de retraite des marins, R. 11, 3° | LEGIARTI000006791987 | seule rédaction de l'index, du 31 mars 1968, sans fin ; « 3° Lorsque le salaire ainsi défini excède huit fois le montant du traitement brut correspondant à l'indice 100 dans la fonction publique, la portion dépassant cette limite n'est comptée que pour moitié. » : **conforme**, mot pour mot |
| Code des transports, L. 5552-19 | LEGIARTI000023079221 | seule rédaction, depuis le 1er décembre 2010 ; « sous réserve d'un abattement au-delà d'un plafond » ; « Ce pourcentage, cet abattement, ce plafond, cette période et ce maximum sont fixés par décret en Conseil d'Etat » : **conforme** (la note marque ce qu'elle élide) |
| Décret n° 48-1108, article 1er | LEGIARTI000006561748 ; LEGIARTI000018696261 | « Les indices minimum et maximum de la hiérarchie générale sont respectivement égaux à 100 et à 800 » : **conforme** ; **précision** : cette rédaction vaut du 11 juillet 1948 au 25 avril 2008, la suivante (décret n° 2008-385) ne porte plus la phrase. La lecture n'en souffre pas : depuis le 1er juillet 2008, l'article 7 nomme lui-même « l'indice 100 ou l'indice brut 100 » |
| Décret n° 85-1148, article 7, premier alinéa | les vingt-sept rédactions de l'index : LEGIARTI000006454537 à LEGIARTI000006454557, LEGIARTI000018728042, LEGIARTI000019111495, LEGIARTI000020817875, LEGIARTI000023427631, LEGIARTI000025140235, LEGIARTI000047751780 | l'indice majoré de chaque alinéa, relevé par script : 150, 152, 154, 155, 156, 158, 158, 160, 161, 163, 164, 164, 164, 172, 172, 174, 174, 186, 190, 191, 194, 199, 201, 203, 203, 203, 208 ; les vingt lignes de `legislation/indice_100_fonction_publique.csv` sont celles qui changent l'indice, chacune avec son identifiant : **conforme**. Les trois citations de la note (1985, 2008, 2024) : **conformes**, mot pour mot |
| Le même article, second alinéa | les mêmes | une liste de textes (code des pensions civiles et militaires, régime de la CNRACL, décret n° 49-1416, code des communes…) jusqu'au 1er janvier 2004, rien en 2004, le seul article 65 de la loi du 11 janvier 1984 depuis le 18 janvier 2005 ; le mot « marin » n'est dans aucune des vingt-sept rédactions : **conforme** |
| Décret n° 2008-622, article 2, 3° | JORFARTI000019108393 | « à compter du 1er juillet 2008 » ; « Pour l'application des dispositions législatives et réglementaires se référant au traitement de l'indice 100 ou de l'indice brut 100, ce traitement est constitué par le traitement afférent à l'indice majoré 201. » : **conforme** |
| Décret n° 2023-519, article 2, II, C | JORFARTI000047749229 | « Au premier alinéa, les mots : « indice majoré 203 » sont remplacés par les mots : « indice majoré 208 » », en vigueur le 1er janvier 2024 (article 3, que rappelle LEGIARTI000047751780) : **conforme** |

**Les dates d'effet.** Chaque relèvement a été relu dans le décret qui le fait, à son « à
compter du » : n° 88-1067 (1er octobre 1988, JORFTEXT000000504298), n° 89-64 (1er février
1989, JORFTEXT000000882942), n° 90-321 (1er janvier 1990, JORFTEXT000000166950),
n° 91-1191 (1er août 1991, JORFTEXT000000538342), n° 98-462 (JORFARTI000001750322),
n° 99-208 (JORFARTI000001818188), n° 99-491 (JORFARTI000002013615), n° 99-943
(JORFARTI000001130980), n° 2001-559 (JORFARTI000002402166), n° 2004-679
(JORFARTI000001532552), n° 2005-726 (JORFARTI000002064055), n° 2006-759
(JORFARTI000002439927), n° 2006-1283 (JORFARTI000002439195), n° 2007-1054
(JORFARTI000002081161), n° 2008-400 (JORFARTI000018693723), n° 2008-622, n° 2009-824
(JORFARTI000020815923), n° 2023-519 : chaque date et chaque indice de la série s'y
retrouvent : **conforme**. Une seule date n'a pu être vérifiée, le 7 février 1986 (152) :
le décret qui modifie l'article 7 ce jour-là n'est dans aucun des deux index ; la série prend
la date de la base LEGI (voir le point 2).

## 2. La lecture « indice brut 100 », et la lecture contraire cherchée

**Ce que les textes imposent.** L'article 7 dit lui-même son champ : les « dispositions
législatives et réglementaires se référant au traitement de l'indice 100 prévu par le décret
du 10 juillet 1948 », de 1985 à 2008, puis « au traitement de l'indice 100 ou de l'indice
brut 100 » depuis le 1er juillet 2008. R. 11, 3° se réfère au « traitement brut
correspondant à l'indice 100 dans la fonction publique » : il est dans ce champ, à la lettre
depuis 2008. L'« indice 100 majoré » de l'article 3 n'est pas un renvoi que l'article 7
constitue : c'est l'unité dans laquelle le décret fixe le point (« La valeur annuelle du
traitement […] afférents à l'indice 100 majoré […] est fixée à 5 907,34 € »,
LEGIARTI000047751772). Le décret confirme l'équivalence : le troisième et dernier alinéa de
son article 8 écrit « l'indice majoré 203 (indice brut 100) » jusqu'au 31 décembre 2023
(LEGIARTI000047751766), et le décret n° 2023-519 (II, D, 2°) y met « l'indice majoré fixé
au premier alinéa de l'article 7 ».

**La lecture contraire, cherchée.** Dans LEGI, « indice 100 » avec « marins » : R. 11 seul ;
dans JORF, rien. « huit fois », « traitement » et « indice » : R. 11 seul. Hors de l'index :
le rapport S2023-0865 de la Cour des comptes (138 pages) ne dit rien de l'abattement, ni du
plafond, ni de l'indice 100 ; la question écrite n° 8440 (publiée le 29 novembre 1993) porte
sur le service militaire ; le document de formation du ministère de la mer
(`SalaireForfaitaireENIM.docx`, formations.mer.gouv.fr) ne parle pas du plafond ; les pages
`printpdf/364` et `printpdf/388` de l'ENIM arrivent vides. **Aucune lecture contraire** ; la
réserve de la note demeure : aucun document de la caisse n'écrit le plafond.

**Deux lectures concurrentes de la série, sans effet (écart faible).** Le barème A du décret
n° 82-1105 que le dépôt tient (`grilles/bareme/indices.csv`, lu sur data.gouv.fr) donne
l'indice majoré 152 à l'indice brut 100 dès le 1er janvier 1985 — le décret n° 86-166,
publié le 7 février 1986, remplace ce barème « à compter du 1er janvier 1985 »
(LEGIARTI000006455048 ; JORFTEXT000000881232) —, quand la série garde 150 du 5 novembre 1985
au 6 février 1986 ; et il donne 169 en mai et juin 2001, quand la série garde 164. Le second
cas est le « piège » de la note, confirmé : le décret n° 2001-370 (JORFARTI000002487322)
relève le second alinéa de l'article 7 et le dernier de l'article 8 (« 164 » y devient
« 169 », LEGIARTI000006454571), pas le premier de l'article 7, que le n° 2001-559 croit à
169. La série suit la lettre de l'article 7, ce qui se défend ; la lecture par le barème
relèverait le plafond de 8 × 2 × 38,5544 = 616,87 € (1985) ou 8 × 2 × 40,2892 = 644,63 €
(1986) de novembre 1985 à février 1986, et de 8 × 5 × 51,2015 = 2 048,06 € en mai et juin
2001, au point du modèle : aucune catégorie n'en approche. Le choix est à déclarer dans la
fiche. Enfin, la base LEGI manque une rédaction : le décret n° 2000-1154
(JORFARTI000001711931) porte au 1er décembre 2000 le second alinéa de « l'indice majoré 204
(indice brut 164) » à « l'indice majoré 208 (indice brut 173) », que LEGI ignore (elle garde
« 204 (indice brut 164) », puis « 213 (indice brut 164) ») : vingt-huit rédactions au droit,
vingt-sept dans l'index, sans effet, l'alinéa ne visant pas les marins.

## 3. Les plafonds refaits à la main

Le traitement d'un indice majoré est celui du barème B (article 5 : « Les traitements et
soldes annuels correspondant aux indices majorés figurent au barème B »), l'indice fois le
point de l'article 3 au jour dit, arrondi au centime ; le plafond, huit fois plus ; la
catégorie 20, celle de l'arrêté en vigueur.

| Date | Indice (art. 7) | Traitement | Plafond | Catégorie 20 | Rapport |
|---|---|---|---|---|---|
| 1er janvier 1986 | 150 | 150 × 264,28 F = 39 642 F (art. 3 : 26 428 F pour l'indice 100 majoré, LEGIARTI000006454423) | 317 136 F = 48 347,07 € | non lue : l'arrêté du 31 décembre 1985 (JORFTEXT000000494793) n'est dans l'index qu'en analyse, « TABLEAU ANNEXE » ; grille du modèle, estimée : 31 750,44 € | 65,7 % sur la grille estimée |
| dès le 7 février 1986 | 152 | 40 170,56 F | 321 364,48 F = 48 991,70 € | id. | — |
| 1er janvier 2008 | 194 | 10 555,79 € (art. 3 : 5 441,13 €, LEGIARTI000018201350) | 84 446,32 € | 59 899,76 € (arrêté du 31 décembre 2007, JORFARTI000017964781) | 70,9 % |
| 1er juillet 2008 | 201 | 10 991,36 € (5 468,34 € depuis le 1er mars 2008, LEGIARTI000018197142) | 87 930,88 € | 59 899,76 € ; 60 378,96 € dès le 1er septembre (arrêté du 26 août 2008, JORFARTI000019428703) | 68,1 % ; 68,7 % |
| 2013 | 203 | 11 279,39 € (5 556,35 €, LEGIARTI000022450760) | 90 235,12 € | 64 976,91 € (arrêté du 2 avril 2013, JORFARTI000027287201) | 72,0 % |
| 2024 | 208 | 12 287,27 € (barème B du décret n° 2023-519, JORFARTI000047749261) | 98 298,16 € | 74 982,29 € (arrêté du 9 avril 2024, JORFARTI000049446355) | 76,3 % |
| 2026 | 208 | 12 287,27 € | 98 298,16 € | 76 867,05 € (arrêté du 19 mars 2026, JORFARTI000053743024) | 78,2 % |

Refait de même au 1er juillet de chaque année de 2008 à 2026, le rapport ne dépasse jamais
78,2 % (2026) : de 2008 à 2026, **aucune catégorie n'atteint le plafond, prouvé**. Les
vingt montants de 2008, de 2013, de 2024 et de 2026 de `regimes/salaires_forfaitaires.csv`
sont ceux des arrêtés, au centime.

**Un arrondi de deux centimes (négligeable).** La note, la fiche, les docstrings et le
détail du montant écrivent 98 298,14 €, soit 8 × 208 × 59,0734 ; le traitement de l'indice
majoré 208 étant au barème B de 12 287,27 €, le plafond exact est 98 298,16 €. Sans effet.

**Le point du 1er janvier**, déclaré par la fiche, fait ce qu'elle dit : au 1er juin 2008, le
modèle prend 8 × 199 × 54,4113 = 86 622,79 €, le droit 8 × 10 882,00 = 87 056,00 € (barème
B du décret n° 2008-400, JORFARTI000018693731) ; au 1er décembre 1985, 46 265,28 € contre
48 347,07 €. Le modèle prend un plafond plus bas que le droit, jamais plus haut ; aucune
catégorie n'en approchant de 1985 à 2026, l'effet est nul.

## 4. La catégorie 20 de 1985 à 2007 : une conclusion non prouvée (écart moyen)

La note, la fiche (`effet`, et l'approximation du point du 1er janvier), le journal et le
message du commit affirment qu'aucune catégorie n'a atteint le plafond « de 1985 à 2026, la
vingtième restant sous 79 % de lui ». De 2008 à 2026, c'est prouvé (point 3). De 1985 à
2007, les arrêtés ne sont pas lus : la grille est celle de 2008 ramenée par le salaire moyen,
et c'est sur elle que se mesurent les 79 % (65,7 % en 1986, 75,1 % en 2005, refaits ici par
le moteur Python). Or les deux seuls montants réels que l'index garde la disent trop basse :

- la 13e catégorie du 1er janvier 1995, « 14 733,03 » F par mois (arrêté du 31 janvier 1995,
  qui corrige le tableau de celui du 29 décembre 1994, JORFARTI000002373607), soit
  176 796,36 F = 26 952,43 € par an, quand le modèle prend 23 530,15 € : le réel est 14,5 %
  plus haut ;
- la 10e catégorie de 2006, « 25 243,83 » € (rectificatif publié le 21 janvier 2006,
  JORFARTI000001490715), quand le modèle prend 24 709,23 € : 2,2 % plus haut.

Portée à la structure de 2008 (la vingtième vaut 1,808 fois la treizième, en 2008 comme en
2026), la vingtième catégorie réelle du 1er janvier 1995 vaudrait 48 735 €, 80,5 % du plafond
du jour (60 548,80 €) : au-delà des 79 %. La conclusion — aucune catégorie n'atteint le
plafond — reste très probable, avec une marge voisine de 20 % ; elle n'est démontrée par
aucun texte de 1985 à 2007, et la structure de la grille d'avant 2008 n'est pas lue non plus.
Aucun chiffre du modèle n'en dépend : sur sa propre grille, le modèle n'abat rien de 1985 à
2026. C'est l'affirmation qui doit changer : « prouvé de 2008 à 2026 ; de 1985 à 2007, sur la
grille estimée du modèle, que les montants de 1995 et de 2006 montrent trop basse ».

Hors de cette tâche, mais mesuré ici pour la première fois : l'approximation « avant 2008, la
grille de 2008 est ramenée par le salaire moyen », dont la fiche dit l'effet « non mesuré »,
vaut −14,5 % en 1995 sur la 13e catégorie et −2,2 % en 2006 sur la 10e — sur le forfait ; la
convention du forfait le plus proche du revenu en amortit l'effet sur la pension.

## 5. Les deux moteurs

- `tests/test_marins.py` : **49 réussis**, dont les vingt relectures de l'article 7 dans
  l'index LEGI, jouées et non sautées ; **49 réussis** aussi sous la garde des présomptions.
- `tests/js/moteur.test.js`, « le salaire des marins ne compte que pour moitié au-delà du
  plafond de R. 11 » : **rouge sur `main` tel quel** (`null ≠ 98298.1376`), **vert sur le
  paquet refait**. Le paquet commité, `moteur/donnees.json`, est en version 38, sans
  `minimum_garanti.indice_100` : e5dd612 ne le porte pas (au rebasage, `-merge` garde celui
  de `main`), quand le code lit la version 39 (`VERSION_PAQUET`, `contexte.js`). La note
  écrit que « le paquet, les témoins et les chiffres ancrés de cette étape sont commités
  refaits » : inexact pour le paquet (écart faible). Jusqu'à la prochaine fabrique verte de
  GitHub, le portage tiré de `main` n'abat pas, et le routeur refuse ce paquet (« et ce code
  lit la 39 : rechargez la page dans un moment ») ; le site publié n'est pas touché, Pages ne
  se déployant que sur une course verte. Or la course qui contient e5dd612 (sur 1aa23ce,
  https://github.com/g-pliberal/retraitecomptenotionelle/actions/runs/41620986070) est rouge
  sur un seul test, `test_cout.py::test_la_projection_suit_le_cor_groupe_par_groupe`
  (« ('depense_part_pib', 'complementaires') : +8.2% du COR à l'horizon, tolérance 8% ») :
  le groupe des complémentaires, que l'abattement d'un régime de base ne déplace pas.
  **Depuis 144a622** (action 177, « le paquet et les fichiers fabriqués refaits »), poussé
  pendant cette relecture, le paquet de `main` est en version 39, la série comprise, et
  l'essai y passe : l'écart ne tient plus qu'à ce que la note affirme.
- `python -m pytest -m rapide`, sur le paquet refait : 4 193 réussis, 16 échecs, aucun des
  marins — 13 pages toutes faites (`test_pages_en_dossier.py`), dont les agrégats ont bougé
  depuis la dernière fabrique, sans aucune clé des marins, et qui passent sur l'état
  commité ; 3 confrontations de `test_pont.py`, sur le seul témoin `cumul_artisan`
  (action 177).
- La garde des présomptions (`PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide`), sur le
  paquet refait : 4 001 réussis, les mêmes 13 pages en échec, rien d'autre.
- La confrontation complète du jumeau Python
  (`test_pont.py::test_le_moteur_python_refait_chaque_temoin`), sur le paquet refait : 32
  témoins sur 930 s'écartent, tous d'artisans, de commerçants et de leurs complémentaires ;
  aucun des dix témoins des marins, le nouveau `marin_au_dela_du_plafond` compris, dont le
  détail (« forfait 121,749.59 € compté pour moitié au-delà de 98,298.14 € ») se refait :
  98 298,1376 + (121 749,59 − 98 298,1376) / 2 = 110 023,86 €. **Conforme**.

## 6. Ce qui n'est pas lu, avant le 5 novembre 1985

**Conforme dans la fiche** : l'approximation (versions `loi_du_12_avril_1941` et
`code_de_1968`, « R. 11, 3° ; décret n° 85-1148, article 7, depuis le 5 novembre 1985 ») dit
que le modèle n'abat pas avant ; le test
`test_avant_le_5_novembre_1985_le_plafond_n_est_pas_lu_et_la_fiche_le_declare` la tient ; les
deux moteurs rendent `null` au 1er octobre 1985 ; l'en-tête de la série et les deux
docstrings le disent. Les seuils de la fiche (76,5 en 1968, 102,8 en 1980) se refont sur la
grille du modèle ; sur la grille réelle, plus haute (point 4), ils seraient plus hauts, sans
approcher l'indice majoré 150 de 1985. **Écart faible** : la ligne des marins de
`docs/limites/4-regimes-incomplets.md`, qui reprend les autres approximations de la fiche
(R. 11, 1° ; R. 12), ne dit ni l'abattement désormais servi, ni ce qui n'est pas lu avant le
5 novembre 1985, ni le point du 1er janvier.

## Ce qui attend

- Restreindre, dans la fiche, la note et le journal, l'affirmation « aucune catégorie de
  1985 à 2026 » (point 4). La prouver demanderait la vingtième catégorie réelle de quelques
  années (1986, 1995, 2000, 2005), au Journal officiel imprimé, que l'outil n'atteint pas :
  Légifrance répond 403 à curl, et sa page ne montre pas le tableau, dont le fac-similé
  passe par un script.
- Déclarer dans la fiche le choix de la lettre de l'article 7 contre le barème A (novembre
  1985 à février 1986, mai et juin 2001), et dans `docs/limites/` ce qui n'est pas lu
  (points 2 et 6) ; ramener, si l'on veut, le plafond au barème B (98 298,16 €).
- Le paquet : refait sur `main` depuis 144a622, l'essai JavaScript de la session y passe ;
  rien n'attend plus, que la course verte de GitHub.
- Une confirmation de l'ENIM reste souhaitable, comme la note le dit.
