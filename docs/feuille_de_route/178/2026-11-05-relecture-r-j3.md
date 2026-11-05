# Relecture de J : les fiches 16 et 27

**Verdict : les chiffres de la source et ceux du modèle sont tous conformes ;
aucun écart grave, deux écarts moyens (point 3.3, et le « 9,5 » de J, point 4),
quatre faibles. La question
laissée ouverte a sa réponse : le coût de la garantie que montre la page
(environ 14 milliards) est BRUT de l'ASPA et de l'ASV qu'elle remplace ; la
page ne les déduit que dans un tableau à part, et ce net n'est pas le « 9,5
milliards » que J évoque.** Toutes les cellules, les valeurs de la page et les
phrases du PDF sont celles que la note dit ; les rapports (61,83 ; 61,93 ;
61,0 ; 5,5 % ; 0 % ; 62,57 ; 62,61 ; 3,7 et 3,1 fois) sont retrouvés à la
main ; les 115 tests des cinq fichiers passent. Le premier écart moyen : J
rapproche les 3,7 et 3,1 fois de ce que `garantie.py` dit coûter « aujourd'hui »,
alors que le chiffre de la page, en 2024, est calculé sur les pensions du
système 4 (facteur de déplacement 0,736), non sur les pensions servies : à
pensions servies, mon calcul de contrôle donne environ 2,4 et 2,0 fois (point
3.3).

**La demande.** Vague 10, file R-J3, le 5 novembre 2026 : revérifier, contre
les sources et sans me fier à J ni à ma mémoire, le commit `bf7098a` de la
session `session_01FVFLAn13JKyimYLuhN9HnG` et sa note
`2026-11-05-etape-5-fiches-16-27.md`. Rien n'est modifié : ni donnée, ni test,
ni code, ni note. Les écarts se décrivent ici ; une correction irait dans une
note neuve.

**Les sources, ouvertes pour cette relecture.**
`python scripts/fetch/source_locale.py --recuperer` a rapporté le PDF
(`les_retraites_et_les_retraites_-_edition_2026-1.pdf`, SHA-256
`9eb36a06639af0f4298d281b41acbde4236e47fc73e40c673f153ad86735e9be`) et
l'archive des classeurs
(`ec7503f813b0a7e38b76c6aade302afa482f927e7d83386922be0522aaf64911`), aux
empreintes de la note de J, que `sha256sum` retrouve. Le PDF : `pdftotext
-layout`, page à page ; la page du fichier est le folio imprimé plus un ;
folios 150, 152, 153, 226, 228 et 230 lus en entier, le 227 pour les 70 660.
Les classeurs : `openpyxl` (`data_only`), indépendamment de `lecture_xlsx`, le
lecteur de J ; je l'ai aussi passé par `lecture_xlsx` pour comparer, les deux
rendent les mêmes valeurs. Le modèle : un script à moi
(`scratchpad/grille.py`, non versé) qui prend les cohortes de
`controle_eacr.controle()`, la même fonction que le fixture de J, et refait
les moyennes, les parts et les rapports ; il n'est donc pas indépendant du
modèle, seulement des agrégations de J.

## 1. Fiche 16, tableau 1 (folio 150, « F16_Tableau 1 »)

**1.1. Cellules et colonnes : conforme.** Le PDF et le classeur disent la même
chose. Colonnes du classeur : C femmes résidant en France, D femmes à
l'étranger, E femmes ensemble, F hommes en France, G hommes à l'étranger, H
hommes ensemble, I les deux sexes. Âge moyen : C16 = 61,6, F16 = 60,8, I16 =
61,3. Parts « avant 60 ans » : femmes C6 + C7 + C8 = 2 + 3 + 6 = 11, hommes F6
+ F7 + F8 = 3 + 5 + 14 = 22. « 66 ans » C13 = 13, F13 = 7 ; « 67 ans ou plus »
C14 = 1, F14 = 1, I14 = 1. Aucune colonne n'est prise pour une autre ; les
hommes sont bien F (« en France »), non H (« ensemble »).

**1.2. Le champ : conforme, et déclaré.** Nés en 1953, EIR 2020, âge « atteint à
la première liquidation d'une pension de base », vivants au 31 décembre 2020
(note du tableau, folio 150). Les trois réserves de J (l'âge de quoi ; le « 60
ans » est 60 ans à 60 ans et 11 mois, note 9 ; « Ensemble » comprend les
résidents à l'étranger) sont exactes, au folio 150. Je n'en vois pas d'autre.

**1.3. La grille, nés en 1953 : conforme.** Cohortes de 2024 dont
`2024 − âge = 1953` : une cohorte par cas type, 750 357 têtes en tout, 81 714,64
de femmes (le seul cas type féminin, `carriere_interrompue`, régime général,
61 ans), 668 642,36 d'hommes. Les dix-huit âges et les dix-huit têtes du
tableau de la note sont ceux que je lis (le militaire 48 ans, 11 116,68 ; la
SNCF 50, 9 364,87 ; les IEG 55, 9 793,66 ; le super-actif 55, 6 797,70 ; le
libéral 66, 16 607,90 ; l'artisan 65, 37 584,60 ; le contractuel 65, 65 133,31 ;
le cadre 64, 77 716,68 ; le salaire moyen 62, 81 333,30 ; le Smic 60, 81 415,76 ;
les fonctionnaires actif 60, actif~sédentaire 63, sédentaire~actif 60,
sédentaire 63 ; l'exploitant 61, 32 854,65 ; l'inapte 61, 32 982,51 ;
l'ex-invalide 61, 34 228,02). Rapports refaits :

| quantité | mon calcul | note de J | publié |
|---|---|---|---|
| âge moyen, femmes | 61,0 (100 % à 61 ans) | 61,0 | 61,6 (C16) |
| âge moyen, hommes | 61,93197 | 61,932 ; +1,13 | 60,8 (F16) |
| âge moyen, ensemble | 61,83048 | 61,830 ; +0,53 | 61,3 (I16) |
| hommes avant 60 ans | 37 072,91 ÷ 668 642,36 = 5,5445 % | 5,545 % | 22 % |
| hommes à 66 ans ou plus | 16 607,90 ÷ 668 642,36 = 2,4838 % | 2,484 % | 8 % |
| hommes à 67 ans ou plus | 0 % | 0 | 1 % (F14) |
| femmes à 61 ans | 100 % | 100 % | 45 % (C10) |

Les quatre parts du 5,54 % (1,66 ; 1,40 ; 1,46 ; 1,02) se retrouvent aussi.
L'écart moyen des hommes (+1,13), de l'ensemble (+0,53) et des femmes (−0,6) :
exact. Les bornes du test (1,0 à 1,3 ; 0,4 à 0,7 ; moins d'un tiers de 22 ;
moins de la moitié de 8) entourent la mesure à ± 0,15 an, c'est ce que
l'énoncé du test dit.

**1.4. Tableau 2 (folio 153, « F16_Tableau 2 ») : conforme.** C6 = 62,0, D6 =
62,3 (régime général) ; C8 = « 60,0 » et D8 = 62,2 (FPE civils) ; C10 = 59,8 et
D10 = « 62,0 » (CNRACL) ; C14 = 61,4, D14 = 62,3 (ensemble) ; E8 = 8,1, F8 =
12,8, G8 = 13,3 (somme 34,2) ; M13 = 3,7. Les deux cellules à virgule (« 60,0 »,
« 62,0 ») sont bien du texte dans le classeur (openpyxl rend la chaîne) ; la
colonne C est l'âge moyen brut, la D l'âge après neutralisation, non
l'inverse. Côté modèle, mon calcul : AOD de 1953 = 61 + 2/12 = 61,16667 (le
test le compare à la note du tableau, « 61 ans et 2 mois »). Brut puis
neutralisé : régime général 62,3085 et 62,5520 (têtes 492 108,83) ; CNRACL 62,2892
et 62,5656 (93 032,59) ; FPE civils 61,9655 et 62,6108 (85 477,82) ; tous régimes
61,8305 et 62,5201. Les écarts de la note (+0,31 ; +2,49 ; +1,97 ; +0,43 ; puis
+0,25 ; +0,57 ; +0,41 ; +0,22) sont exacts. Le super-actif pèse 6 797,70 ÷
85 477,82 = 7,9526 % des FPE civils, pour 34,2 % publiés : exact.

**1.5. Un lapsus de calcul intermédiaire : faible.** L'exemple « posé à la
main » de la note, la CNRACL neutralisée, donne « 22 041,55 × 61,1667 =
1 348 195,8 » ; le produit est 1 348 208,1 (1 348 208,9 avec 61,1667). Le
résultat, 62,566, ne bouge pas (62,5656), mais l'intermédiaire écrit est faux
de 12.

**1.6. Encadré 2 (folio 152) : conforme.** Les trois phrases sont mot pour mot
au folio : « les départs à la retraite entre 68 et 70 ans représentent environ
1 % des départs, et ceux qui ont lieu entre 71 et 74 ans environ 0,2 % » (nés
en 1950 et en 1946) ; « 11 % de départs entre 67 et 70 ans » chez les
professions libérales ; « plus élevé de 1 à 11 mois selon le régime » ; et les
résultats de l'EIR sont ceux des nés en 1953 observés à 67 ans. La grille, nés
en 1946 puis en 1950 : dix-huit cohortes chacune, âge de liquidation le plus
tardif 65 ans (le libéral), 0 % à 68 ans ou plus ; nés en 1953, le plus tardif
66 ans, 0 % à 67 ans ou plus. La mesure de la population (0 % à 68 ans ou plus,
action 138) n'est ni rejouée par J ni par moi : J le dit, et le test la cite
sans l'asserter. Conforme à la source, déclaré.

## 2. Fiche 27, les chiffres de la source (folios 226, 228, 230)

**2.1. Cellules : conforme.** « F27_Tableau 1 » ligne 24 : D24 = 93 280
(premier étage), E24 = 101 990 (ASV), F24 = 652 470 (Aspa), G24 = 754 460
(ASV et Aspa), J24 = 66 940 (ASI) ; 101 990 + 652 470 = 754 460. « F27_Graphique
1 » ligne 70 : B70 = 2024, C70 = 754 (milliers), D70 = 3,9 (% des 60 ans ou
plus), E70 = 4,6 (**% des 65 ans ou plus**). Le « 4,6 » du graphique est donc un
pourcentage de population, distinct des « 4,6 milliards » de dépenses : J les
distingue et le test ne lit les milliards que par `atteignent (\d+,\d)
milliards d'euros` dans la citation, sans risque de confusion.

**2.2. Le texte : conforme.** Folio 226 : « Fin 2024, 754 460 personnes
perçoivent l'allocation supplémentaire du minimum vieillesse (ASV) ou
l'allocation de solidarité aux personnes âgées (Aspa) » ; « 4,6 % [des 65 ans
ou plus] sont titulaires d'une allocation » ; 70 660 nouveaux allocataires.
Folio 230 : les dépenses d'ASV et d'Aspa de 2024 « atteignent 4,6 milliards
d'euros » (+11,6 %) ; « en incluant les allocations de premier étage … 4,8
milliards d'euros en 2024 » ; 466 euros mensuels d'ASV, 527 d'Aspa. Les 13
phrases du témoin sont au PDF (`test_chaque_citation_du_temoin_est_dans_le_pdf`
passe).

**2.3. Ce que le texte ne dit pas.** Le folio 230 ne donne d'unité (« euros
courants ») que pour l'ASI ; pour l'ASV et l'Aspa, « courants » est une
inférence raisonnable, non un texte (voir 3.4).

## 3. Fiche 27, ce que le modèle donne et ce que J en conclut

**3.1. Les valeurs du modèle : conformes.** `mesures_prose.mesurer`, 2024 :
`garantie?annee=2024&quoi=beneficiaires` = 2,800 133 millions ; `ayants_droit` =
5,600 266 millions (recours `Parametres.taux_recours_garantie` = 0,5) ;
`cout_annee?scenario=garantie&annee=2024` = 14,3071 milliards d'euros constants
de 2026 (`Parametres.annee_euros_constants` = 2026).

**3.2. Les rapports : conformes.** 2 800 133 ÷ 754 460 = 3,7114 ; 14,3071 ÷ 4,6
= 3,1102 (3,0768 à 3,1444 pour 4,65 à 4,55) ; 14 307,1 M€ ÷ 2 800 133 ÷ 12 =
425,8 € par mois (J : 425,8) ; 4,6 Md€ ÷ 754 460 ÷ 12 = 508,1 € (J : 508).

**3.3. ÉCART MOYEN : de quelle garantie parle-t-on.** J écrit : « Ce que le
dépôt calcule qui s'y compare : la garantie vieillesse de la page Coût, que
`garantie.py` dit coûter “aujourd'hui, en remplacement de l'ASPA” » (note ;
même phrase au test). Or `garantie.py:29-31` dit cela du cas `facteur = 1`,
« le barème appliqué aux pensions TELLES QU'ELLES SONT ». Le chiffre de la page
n'est pas celui-là : `garantie?annee=2024&quoi=facteur` = **0,7365** (0,6222 en
2020, 0,7632 en 2026). Les pensions que la garantie regarde en 2024 sont celles
du système 4, déplacées à 0,7365 de celles du système actuel de 2020
(`cout.py:3451`, `facteur = masses[RESSOURCES_GARANTIE] / tetes /
pension_reference`). Plus de monde passe sous le plancher qu'aujourd'hui. Mon
calcul de contrôle (script à moi, `scratchpad/mes3.py`, non versé) applique
`garantie.cout_garantie` à la distribution de l'EIR 2020, effectif de 2024
(14,39 millions), aux deux planchers de la page :

| plancher | coût à facteur 0,7365 | coût à facteur 1 | rapport | part sous le plancher |
|---|---|---|---|---|
| 800 € (vie à deux) | 15 291 M€ | 10 244 M€ | 0,670 | 31,2 % → 19,4 % |
| 1 050 € (seul) | 29 144 M€ | 19 140 M€ | 0,657 | 44,1 % → 29,7 % |

À pensions servies, le coût serait donc de l'ordre des deux tiers de celui de
la page, et les bénéficiaires, de 0,62 à 0,67 selon le plancher : environ 1,7 à
1,9 million de bénéficiaires (2,3 à 2,5 fois les allocataires) et 9,5
milliards d'euros de 2026 (2,1 fois les 4,6 milliards, 2,0 en euros de même
base). C'est un ordre de grandeur, non une
mesure du dépôt : il suppose le mélange de planchers de la page, que je n'ai pas
rejoué ; mais le sens est sûr. Les 3,7 et 3,1 fois sont exacts pour la
garantie de la page en 2024 ; ils ne disent pas ce que la garantie coûterait
aujourd'hui sur les pensions servies. Ni la note, ni le test, ni le suivi
(« compte en 2024 2,80 millions de bénéficiaires … pour 754 460 allocataires »)
ne déclarent que le chiffre dépend du facteur de déplacement, 0,74 : c'est
aussi ce qui fait tenir les bornes 3,5 à 3,9 et 2,9 à 3,3. Gravité : moyenne
(champ mal nommé ; les chiffres, justes).

**3.4. ÉCART FAIBLE : les euros.** La note laisse « un écart de prix de quelque
trois pour cent que je n'ai pas chiffré ». Je le chiffre :
`coefficient_prix(2026, 2024)` = 0,97362, d'où le coût de 2024 en euros
courants = 13,93 Md€ (`AvenirAnnuel.cout` rend 13,9297, `cout_constants`
14,3071). Même base : 13,93 ÷ 4,6 = **3,03** (3,00 à 3,06 pour 4,65 à 4,55),
non 3,11. Les bornes 2,9 à 3,3 du test l'admettent ; la phrase « 3,1 fois » du
commit et du suivi est trop haute de 0,08. Le texte de la source ne dit pas «
courants » pour l'ASV et l'Aspa (point 2.3).

**3.5. ÉCART FAIBLE : allocataires ou personnes.** 754 460 est un nombre
d'allocataires. La note 1 du folio 226 dit : en comptant les éventuels
conjoints, « environ 897 810 personnes bénéficieraient du minimum vieillesse »
(enquête Drees sur les bénéficiaires des minima sociaux de 2018). La garantie
est individuelle ; par personne, 2 800 133 ÷ 897 810 = 3,12, non 3,71. La
note ne le déclare pas ; la section 2 de J n'a d'ailleurs pas son paragraphe «
Ce que la source ne tranche pas » (la section 1 l'a). Autres réserves non
dites : l'effectif de la source est un stock au 31 décembre, celui du modèle
une année ; les 3 960 de l'Aspa Mayotte sont hors des 754 460 (note 4).

**3.6. Les tests : conformes, avec les réserves 3.3 à 3.5.** Les valeurs viennent
du témoin, dont chaque cellule est celle du classeur
(`test_chaque_valeur_du_temoin_est_celle_de_sa_cellule`, 104 cellules : 33 + 63 +
5 + 3, je les ai comptées ; 13 phrases : 4 + 2 + 7) ; aucune n'est tirée du
code. Les bornes ne sont pas celles de la source (qui est exacte ou arrondie à
0,1) mais celles de la mesure du modèle, à ± 0,15 an pour les âges, ± 0,2
pour les rapports de la fiche 27 ; leur raison est dite. Elles épinglent
l'écart, ce que le test annonce (« ÉCART DÉCLARÉ »). Le test de la fiche 27
est le seul à lire la page par `mesures_prose` et non par un calcul du dépôt :
J le dit. Exécution : `tests/test_controle_drees_panorama.py`, 45 passent,
aucun sauté ; les quatre autres fichiers que la note nomme
(`test_drees_panorama.py`, `_2024`, `_eic`, `_series`), 70 passent : 115, aucun
rouge, aucun sauté. J annonce 117 « avec le test de syntaxe de Python 3.11 » :
l'écart de deux n'est pas reproduit ici (Python 3.13) ; négligeable, non
élucidé. Le suivi (`data/reference/drees_panorama_2026.yaml`) : les fiches 16 et
27 en `confronte`, `confronte_par` nomme des tests qui existent ;
`test_les_fiches_16_et_27_nomment_leurs_confrontations` passe.

## 4. La question laissée ouverte : le coût de la garantie est-il net de l'ASPA et de l'ASV ?

**Réponse : non. Le coût de la garantie que la page montre (14,3 milliards
d'euros de 2026 en 2024, 14 en 2026 et en 2070 dans
`docs/limites/4-regimes-incomplets.md:699-700`) est le coût BRUT du complément
au plancher ; il ne retire ni l'ASPA ni l'ASV. La déduction existe, une seule
fois, dans un tableau séparé de la page, et sur quatre minima, non sur deux.**
Lecture du code seule, rien n'est lancé pour cette réponse :

1. `garantie.py:103-124` (`cout_garantie`) : le coût est Σ part × manque × effectif
   × 12, où le manque d'une tranche est `plancher − pension` (milieu de la
   tranche, `_manque_moyen`, lignes 65-87). La pension est celle de la
   distribution de l'EIR (droit direct) ; aucun terme d'ASPA ou d'ASV n'y
   entre.
2. `cout.py:3446-3463` (`GarantieDistribution.chiffrer`) :
   `cout_constants = chiffre.cout_annuel_meur * self.vers_constants *
   self.taux_recours`. Rien n'est retranché ; le seul facteur de réduction est
   le recours de 50 %.
3. `Grep` de `aspa` dans `cout.py` : sept occurrences, toutes des commentaires
   (lignes 952, 969, 1400, 2513, 2926, 3333, 3348), aucune opération.
   `garantie_nette_constants` (`cout.py:1016-1018`) est la garantie moins les
   REPRISES SUR SUCCESSION (`cout_constants(COMPOSANTE_GARANTIE) -
   reprises_constants()`), non moins l'ASPA.
4. `cout.py:2511-2514` : le scénario 1 de la page « ne sert pas l'ASPA, que la
   dépense qu'elle multiplie ne compte pas » ; l'ASPA n'est donc ni dans le
   système actuel de la page, ni retranchée de la garantie : la ligne
   « garantie vieillesse » du scénario 6 est comptée toute.
5. `effet_retour.py:15-17` : la garantie, « qui remplace l'ASPA, est déjà
   chiffrée à part (`GarantieDistribution`) » : l'effet retour n'a pas de terme
   d'ASPA pour le scénario 6.
6. `docs/limites/4-regimes-incomplets.md:703` : « Ces chiffres sont bruts des
   reprises sur succession » ; le brut des minima n'est pas dit là.
7. **Là où la page nettoie** : `moteur/js/pages.js:13321-13349` (le dépliant
   « Ce que coûte la garantie vieillesse »), tableau « Ce que la garantie
   vieillesse remplace » (13512-13523, « Ce que l'impôt paierait *en plus* est
   la garantie moins ces quatre-là »). Le code nomme la variable `garantieBrute
   = c.annee(anneeMinima).cout(COMPOSANTE_GARANTIE)` et lui retranche
   `totalRemplace`, somme de QUATRE minima : « Minimum vieillesse (ASPA) » (lu
   dans les comptes), minimum contributif, minimum garanti de la fonction
   publique, minima des exploitants agricoles (pension majorée de référence +
   complément différentiel de la RCO).

**Le net de la page, 2024 (mon calcul, non lu sur la page rendue).** Les
quatre minima de la dernière année des avantages (2024, `contexte.avantages().derniere`
côté JS, `memoire.avantages` côté Python), en milliards d'euros courants :
minimum vieillesse 4,941 ; minimum contributif 1,563 ; minimum garanti 0,007 ;
pension majorée de référence 0,349 ; complément différentiel de la RCO 0,637 ;
total 7,497. La garantie brute en euros courants de 2024 : 13,930
(`AvenirAnnuel.cout`, le même appel que le `cout()` de `agregats.js:407` qui lit
la table `couts`, non `couts_constants` ; je ne l'ai pas fait tourner côté JS,
je l'infère du nom de la table). Net : 13,93 − 7,50 = **6,43 milliards**, ce
que la page appelle « Ce que l'impôt paierait en plus ». Cette soustraction
compte les mêmes euros de chaque côté, si l'inférence tient.

**Ce que J propose est faux de forme.** « 14,3 − 4,8 = 9,5 milliards » retranche les
4,8 de la DREES (ASV, Aspa et premier étage, courants de 2024) de 14,3
(constants de 2026) : deux bases d'euros, et seulement un minimum sur quatre.
À la même base, 13,93 − 4,8 = 9,1 ; mais ce n'est pas le net de la page, qui
retire aussi le minimum contributif, le minimum garanti et les minima des
exploitants. Un écart à noter : la page lit le minimum vieillesse dans les
comptes (4,94 Md€, 2024), la DREES en donne 4,6 (ASV et Aspa) ou 4,8 (premier
étage compris) ; je ne l'explique pas (le poste des comptes peut compter
d'autres lignes).

## 5. Récapitulatif des points

| point | verdict | gravité |
|---|---|---|
| 1.1 à 1.4, 1.6 : cellules, colonnes, champ, grille, tableau 2, encadré 2 | conforme | — |
| 1.5 : « 1 348 195,8 » pour 1 348 208,1 | écart d'un intermédiaire, résultat juste | faible |
| 2.1, 2.2 : cellules, texte, 13 phrases | conforme | — |
| 3.1, 3.2 : valeurs du modèle et rapports | conforme | — |
| 3.3 : « aujourd'hui » pour un chiffre à facteur 0,7365 ; à pensions servies, environ 2,4 et 2,0 fois | écart de champ | moyen |
| 3.4 : euros constants de 2026 contre courants de 2024 ; 3,03 et non 3,11 | écart | faible |
| 3.5 : allocataires contre personnes (897 810, conjoints compris) ; stock contre année ; Mayotte | non déclaré | faible |
| 3.6 : tests, 115 passent contre 117 annoncés | négligeable | faible |
| 4 : coût brut ; net de la page 6,43 Md€ (quatre minima) ; « 9,5 » de J mal établi | réponse | moyen (la question était posée de travers) |

**Candidats, hors de cette tâche** (rien n'est modifié ici) : (a) dire, au
test, à la note et au suivi de la fiche 27, que le chiffre est calculé au facteur
0,7365, et non aux pensions servies, et donner les rapports à pensions
servies par un test du dépôt (aujourd'hui, mon calcul est un script jetable) ;
(b) poser les 3,03 (même base d'euros) et les 3,12 (par personne) à côté des
3,7 et 3,1 ; (c) la question au propriétaire de la note de J (point 2) est
close par la section 4 ; (d) l'écart de 4,94 (comptes) contre 4,6 ou 4,8
(DREES) pour le minimum vieillesse à la ligne « lu dans les comptes » de la
page.

Sources : PDF « Les retraités et les retraites », édition 2026 (Drees),
folios 150, 152, 153, 226, 227, 228, 230 ; classeurs `fiche_16.xlsx`
(« F16_Tableau 1 », « F16_Tableau 2 ») et `fiche_27.xlsx` (« F27_Tableau 1 »,
« F27_Graphique 1 ») ; code : `garantie.py:65-124`,
`cout.py:1016-1018, 2511-2514, 3446-3463`, `effet_retour.py:15-17`,
`moteur/js/pages.js:13321-13349, 13512-13523`,
`docs/limites/4-regimes-incomplets.md:699-704`.
