# Relecture de I : les inaptes

File R-I4, vague 9, le 5 novembre 2026 : relecture indépendante, étroite, des
chiffres du commit f0d180e (session `session_01FVFLAkqFRPAjopjCw91n5M`, note
`2026-11-05-etape-14-inaptes.md`, mesure
`docs/mesures/138/2026-11-05-etape-14-inaptes.txt`), action 138, étape 14,
trente-huitième version, sur `main` à f0d180e. Rien n'est repris de la session I
ni de mémoire : chaque chiffre est relu à sa source ou recalculé ici. Seule cette
note est écrite : ni règle, ni donnée, ni test, ni script, ni bloc « Reprise ».

**Verdict : conforme, à deux arrondis près.** Les 90 cellules de l'EIR que la note
cite et les 160 du fichier du dépôt sont celles des classeurs ; les 70,8 et 71,3 %,
les deux attentes, l'âge moyen 61,83 et le 58,6 % se retrouvent. Deux chiffres
de la note, 17,6 % et 25,1 %, sont faux d'un dixième de point : ils sont dérivés
d'un chiffre arrondi, et la mesure donne 17,7 et 25,2 (point 2, écart A). Trois
réserves de forme, sans effet sur un chiffre de la page ni sur la règle.

## Les sources, ouvertes ici

- *Les deux classeurs de la DREES*, jeu `3013_donnees-statistiques-sur-les-caracteristiques-des-retraites`,
  pièces `caracteristiques_des_retraites_nes_en_1953_eir_2020_xlsx` et
  `…_nes_en_1950_eir_2016_xlsx`. Aucun n'est au dépôt (`data/brut/` est vide,
  ignoré) ; `curl` y est coupé (`Recv failure: Connection reset by peer`, quatre
  essais ; le point d'état du proxy note « tunnel closed (code 1006) » sur
  `data.drees.solidarites-sante.gouv.fr`) ; l'outil de lecture du web a rendu les
  deux fichiers. Octets et SHA-256 recalculés, ceux que cite la note de I : 1953,
  195 574 octets, `d5e8b8776768e31a3a8a0490bf749fc6615d12a8d25716e57a658dd16f94c5e0` ;
  1950, 194 522 octets,
  `59f76598591d20cb4704659a65ba30ce687ca8cb0a733198a3182c6bbaef61a8`. Lus cellule par cellule par un lecteur écrit ici
  (`zipfile` et XML), non par `scripts/fetch/lecture_xlsx.py`, pour que la lecture
  ne soit pas celle de I.
- *Au dépôt* : `data/reference/macro/departs_generations.csv`, comparé aux
  classeurs, 160 cellules (les parts de chaque place, de chaque âge de 60 à 66
  ans, les parts d'invalidité et d'inaptitude, les carrières complètes de
  `CondLiquidation`, deux générations, deux sexes) : aucun écart.

## 1. Les cellules de l'EIR, relues (conforme)

Classeur de 1953. Feuille « ÂgeLiq » (en-têtes ligne 1, D à H : avant l'âge
légal, à lui, entre lui et l'âge d'annulation de la décote, à l'âge d'annulation,
après) :
`D6 = 21,7`, `E6 = 37,5`, `F6 = 26,7`, `G6 = 10,8`, `H6 = 3,3` (femmes) ;
`D7 = 40,8`, `E7 = 24,4`, `F7 = 26,4`, `G7 = 5,5`, `H7 = 2,8` (hommes) ;
`D285 … H285 = 1,6 ; 17,9 ; 3,8 ; 0,6 ; 0,4` et `D286 … H286 = 1,4 ; 25,6 ; 2,5 ;
0,6 ; 0,1` (colonne C : « Part des retraités ayant liquidé pour invalidité »,
femmes, hommes) ; `D291 … H291 = 0 ; 13,7 ; 10,2 ; 0,3 ; 0,1` et `D292 … H292 =
0 ; 15,2 ; 8,4 ; 0,5 ; 0,4` (« … pour inaptitude »). Feuille « ÂgeLiq_Détails »,
F à K, 61 à 66 ans : `F6 … K6 = 42,1 ; 8,9 ; 5,0 ; 5,7 ; 2,9 ; 14,9`, `F7 … K7 =
29,7 ; 8,2 ; 5,2 ; 6,1 ; 3,1 ; 9,1`, `F285 … K285 = 16,1 ; 8,6 ; 1,7 ; 1,3 ; 1,1 ;
0,6`, `F286 … K286 = 21,2 ; 6,3 ; 0,8 ; 0,7 ; 0,6 ; 0,5`, `F291 … K291 = 13,0 ;
9,7 ; 10,6 ; 10,7 ; 9,2 ; 0,9`, `F292 … K292 = 13,3 ; 8,7 ; 7,8 ; 8,6 ; 6,5 ;
1,8`. Feuille « CondLiquidation » : `H6 = 8,2`, `I6 = 7,9`, `H7 = 7,5`, `I7 =
6,0` (taux plein pour invalidité et pour inaptitude, part de la génération) ;
`H18 = 67,6`, `I18 = 14,7`, `H19 = 65,3`, `I19 = 17,1` (« Part d'assurés à
carrière complète »).

Classeur de 1950. « ÂgeLiq » : `E6 = 44,4`, `F6 = 22,4`, `E7 = 35,3`, `F7 = 25,4` ;
invalidité `E282 = 14,6`, `F282 = 1,8` (femmes), `E283 = 16,6`, `F283 = 1,1`
(hommes) ; inaptitude `E288 = 14,4`, `F288 = 11,0` (femmes), `E289 = 12,4`, `F289 =
7,8` (hommes) ; « CondLiquidation » `H18 = 66,3`, `I18 = 12,8`, `H19 = 62,4`,
`I19 = 18,5`. Toutes celles que la note cite, aux lignes qu'elle dit : 74 cellules
du classeur de 1953, 16 de celui de 1950. Aucune ne manque ni ne diffère. (Les
parts de génération de 1950, `H6 = 7,1`, `I6 = 8,9`, `H7 = 6,6`, `I7 = 6,4`, que la
note ne cite pas, servent au point 2.)

*Contrôle de la lecture de chaque ligne* : la part de la colonne, fois la part
d'invalidité ou d'inaptitude « parmi ses départs », sommée sur les cinq places,
redonne la part de la génération de « CondLiquidation » : invalidité des
femmes, 815,23 pour `H6 = 8,2` ; inaptitude, 789,66 pour `I6 = 7,9` ; hommes,
751,34 pour `H7 = 7,5` et 596,51 pour `I7 = 6,0`. La lecture de I (la part est
celle des départs de la colonne) est donc la bonne.

## 2. Refaits à la main (conforme, sauf l'écart A)

Avec, pour les femmes, 1 − 0,676 = 0,324 d'invalides et 1 − 0,147 = 0,853
d'inaptes sans carrière complète ; hommes 0,347 et 0,829.

- *Les 70,8 et 71,3 %* (colonne « EIR » de la note) : ce sont les places, de
  l'âge légal à « après » (`E`, `F`, `G`, `H` de « ÂgeLiq »), chacune pesée par
  `part × (0,324 × invalidité + 0,853 × inaptitude)`. Femmes : 655,714, 265,179,
  4,863 et 0,709, soit 926,465 en tout, **70,78 % à l'âge légal**, 28,62 entre les
  deux âges, 0,60 après ; hommes : 524,210, 206,741, 3,425 et 1,026, soit
  735,401, **71,28 %**, 28,11 et 0,61. D'où 70,8 et 71,3 ; 28,6 et 28,1 ; « 0,6 % »
  du texte. Nés en 1950 (« Ce qui reste », point 1) : 22,68 % des femmes et
  22,76 % des hommes entre les deux âges, soit les 22,7 et 22,8 ; leur part des
  départs, 10,154 et 7,698 % (`H6 × 0,337 + I6 × 0,872`, `H7 × 0,376 + I7 × 0,815`),
  soit les 10,15 et 7,70. Nés en 1953 : 9,396 et 7,577 %, soit les 9,40 et 7,58.
- *Les 70,9 et 71,3 % de la population* : même numérateur, mais au dénominateur
  la somme des âges (feuille « ÂgeLiq_Détails », 61 à 66 ans, le 61 ans diminué de
  la part de l'âge légal) : femmes 655,714 / 925,411 = 70,86 %, hommes 524,210 /
  735,562 = 71,27 %.
- *Les attentes, de 1 an 1 mois et de 3 ans 4 mois* : ni une médiane ni une
  tranche de l'EIR, mais la moyenne, pondérée par les poids de chaque âge, des
  milieux d'âge comptés de l'âge légal, 61 ans et 2 mois. Première attente, les
  âges de 61 (de 61 ans et 2 mois à 62 ans, milieu à 0,4167 an) et 62 ans (1,3333
  an), poids 30,744 et 98,438 : **1,1152 an**, soit 13,4 mois, pour 13,96 % ;
  seconde, 63 à 66 ans (2,3333 ; 3,3333 ; 4,3333 ; 4,9167, le 66 ans courant
  jusqu'à 66 ans et 2 mois), poids 47,963, 54,425, 23,792 et 14,335 : **3,3228
  ans**, soit 39,9 mois, pour 15,18 %. Hommes, 1,1317 an (13,6 mois, 13,43 %) et
  3,3892 ans (40,7 mois, 15,30 %). La convention est celle que la note dit ; « un an
  et un mois » et « trois ans et quatre mois » sont ses chiffres arrondis,
  justes pour les femmes (réserve 1 pour les hommes).
- *L'âge moyen 61,83* : 61,1667 + 0,1396 × 1,1152 + 0,1518 × 3,3228 =
  **61,827** ; hommes 61,837 (61,84 à la mesure). L'âge d'avant, 61,17, est l'âge
  légal de la génération.
- *Les 58,6 et 17,6 %* : la mesure du matin
  (`…-duree-des-femmes.txt`, 61,3 et 14,9) moins ou plus 9,40 × 0,291 = 2,74
  points donne 58,56 et 17,64. **Mesuré ici**, par le pilote de cette mesure du
  matin lancé sur `main` à f0d180e (`pilote.py 1953 2020 1955 2022`, `.1f` changé
  en `.2f`), puis le même avec `INAPTES_ENTRE_LES_DEUX_AGES = False` :

  | femmes, % de leurs départs | avant (drapeau coupé) | après (f0d180e) | note de I |
  |---|---|---|---|
  | 1953, à l'âge légal | 61,31 | 58,58 | 58,6 conforme |
  | 1953, entre les deux âges | 14,95 | 17,69 | **17,6 : 17,7** |
  | 1955, à l'âge légal | 51,51 | 48,78 | 48,8 conforme |
  | 1955, entre les deux âges | 22,44 | 25,17 | **25,1 : 25,2** |

  Le drapeau coupé redonne les 61,3, 14,9, 51,5 et 22,4 de la mesure du matin,
  dont le commit (319ee4b) et l'arbre (fe79998) ne sont plus au dépôt, sans
  doute rebasés par `pousser.sh`. **Écart A, faible** : I ajoute 2,7 à 14,9 et à 22,4, chiffres arrondis
  de 14,95 et de 22,44, et écrit 17,6 et 25,1 ; le déplacement exact est de 2,74 et
  2,73 points, les valeurs 17,69 et 25,17. La conclusion (2,7 points passent de
  l'âge légal à l'entre-deux) tient ; deux chiffres de la note sont à corriger, d'un
  dixième.

## 3. Les tests (conforme)

Trois tests ajoutés à `tests/test_grille_large.py`, relancés avec le test voisin
(`test_les_invalides_et_les_inaptes_partent_au_taux_plein_des_l_age_legal`,
retouché d'un code) : 6 cas passés, 57 s.

- `test_l_attente_des_invalides_et_des_inaptes_se_lit_dans_l_eir` : la valeur
  attendue vient de l'EIR. Les cellules y sont saisies à la main (37,5, 17,9,
  13,7, 0,676, 0,147 ; 42,1 à 14,9 ; 16,1 à 0,6 ; 13,0 à 0,9 ; celles des hommes),
  **identiques à celles des classeurs** relues ci-dessus ; les attentes et les
  parts se recalculent dans le test, sans le code ; les arrondis fixés (`[0,0 ; 1,12
  ; 3,32]` et `[0,0 ; 1,13 ; 3,39]`, 0,709 et 0,713) sont ceux de ce point 2.
- `test_les_invalides_et_les_inaptes_attendent_comme_ceux_des_nes_en_1953` :
  des relations (trois jumelles pour une, leurs poids dans la proportion des
  parts), sans valeur tirée du code.
- `test_un_inapte_qui_attend_part_apres_l_age_de_son_taux_plein` : 62 ans, taux
  de 50 %, 100 trimestres (vingt-cinq ans), sans surcote, viennent de la loi et de
  la carrière posée, non du rendu. Je n'ai pas relu la loi (L. 351-1-5, D. 351-1-14,
  L. 351-1-2) : hors du champ « chiffres » de cette relecture.

## 4. « Rien ne bouge » (conforme)

`git show f0d180e --stat` : sept fichiers, les deux notes, la mesure,
`docs/limites/5-bis-cout-agrege.md`, `scripts/grille_large.py`,
`src/retraite_notionnelle/pont.mjs` et le test. Aucun fichier de `moteur/`, aucune
page, aucun témoin de `tests/temoins/`, aucun fichier fabriqué. `pont.mjs` gagne
une branche (`apres_le_taux_plein`), prise seulement par un cas qui porte cette
clé, soit les jumelles inaptes de la population ; la page ne lit pas la
population. L'autre note modifiée, `…-carriere-longue-des-femmes.md`, ne l'est que
dans son bloc « Reprise », le seul qui se récrit. `python -m pytest -m rapide`, sur
f0d180e : **4 422 passés, 56 ignorés, aucun rouge**, 3 min 4 s (I en compte
4 411 ; la différence n'est pas élucidée, elle ne change pas le verdict).

## 5. Ce que la source ne tranche pas (conforme, déclaré)

La note le dit : l'EIR ne croise ni l'âge ni la place avec la carrière complète
(première convention, « chaque condition pèse ses départs sans carrière
complète ») ; l'attente se compte de l'âge du taux plein, « à toute génération,
sans échelle », cinq ans à chacune ; les attentes des nés en 1953 sont celles de
toute génération de 1950 à 1965, et celles de 1950 (22,7 et 22,8 % entre les deux
âges, non 29,1 et 28,7) sont dites plus basses (« Ce qui reste », point 1) ;
l'âge dans chaque attente (point 2), les invalides d'avant l'âge légal (point 3),
les générations hors de l'enquête (point 4, qui renvoie à la trente-deuxième
version) sont déclarés. La fiche `docs/limites/5-bis-cout-agrege.md` le reprend
(« leurs attentes selon la génération »).

## Les écarts et les réserves

- **A. 17,6 % et 25,1 % (faible)** : 17,7 et 25,2, mesurés (point 2). À corriger
  dans une retouche, la note étant un récit.
- **Réserve 1 (négligeable)** : « un an et un mois puis trois ans et quatre mois »
  vaut pour les femmes (13,4 et 39,9 mois) ; les hommes attendent 13,6 et 40,7 mois,
  1 an 2 mois et 3 ans 5 mois, ce que dit la docstring du troisième test. Un mois
  au plus.
- **Réserve 2 (négligeable)** : 70,9 pour 70,8 des femmes tient à ce que la
  population pèse les âges (925,411) quand la colonne de l'EIR pèse les places
  (926,465) ; la note ne le dit pas. L'écart des deux totaux est de 0,11 %.
- **Réserve 3 (négligeable)** : la colonne « 61 ans » de « ÂgeLiq_Détails » compte
  aussi les départs de 61 ans à 61 ans et 2 mois, d'avant l'âge légal, que la
  première attente prend alors pour des attentes. Elle en porte au plus 0,76 sur 735
  chez les hommes et rien chez les femmes (11,25 d'avant l'âge légal moins 7,93
  d'avant 60 ans et 3,54 à 60 ans), soit 0,1 % au plus.
- *Candidat, hors de ma tâche* : la mesure du matin
  (`…-duree-des-femmes.txt`) cite un commit et un arbre que le dépôt ne connaît
  plus ; ses chiffres se retrouvent par son script, qu'elle joint, non par son
  hash.
