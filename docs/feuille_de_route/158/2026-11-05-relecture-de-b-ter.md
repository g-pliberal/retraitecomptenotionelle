# Relecture de B-ter : le n° 96-101, l'échelon spécial du chef de projet SRIC, le directeur de recherche de 2e classe

Vague 9, R-B3, le 5 novembre 2026. Relecture indépendante du commit 9cb387b (B-ter, note
`2026-11-05-b-ter.md`). Tout ce qui suit a été rouvert pendant la relecture, dans les index
du dépôt récupérés par `dila_index.py --recuperer` (LEGI à jour au 20261102-213929, JORF au
20261103-002311, les mêmes que B-ter), par `dila_cherche.py --texte` ou une lecture directe
de la table `doc`. Rien n'est repris de la note de B-ter ni de la mémoire de la session.

**Verdict : conforme sur toutes les citations, toutes les valeurs, toutes les dates et le
code ; deux écarts mineurs (point 1 : « récrit » est une inférence dont la source n'est pas
citée ; point 3 : la déclaration du directeur de recherche de 2e classe ne chiffre que le
1er septembre 2017, non l'année 2018), deux remarques, aucune erreur de donnée.**

## 1. Le n° 96-101

- **Sept articles, pas un de plus.** `dila_cherche.py jorf --num 96-101` répond « n'est pas
  dans l'index » : `--num` est un numéro d'article du LEGI, non un numéro de texte. La table
  `doc` de l'index JORF, à la date du 1996-02-08 et au titre « Décret n°96-101 du 6 février
  1996 », donne huit documents : le texte (JORFTEXT000000191345) et sept articles,
  JORFARTI000001400977 (art. 1er), 001790554 (art. 2), 001984923 (art. 10), 002305421
  (art. 25), 001790557 (art. 27), 001153864 (art. 33), 001598161 (art. 38) ; chacun s'ouvre
  sur « Art. N. - ». **Conforme.**
- **Aucun ne vise le n° 87-1104 ni ne date l'effet.** Dans les sept : « 87-1104 », 0
  occurrence ; « vigueur », 0 ; « 1er août » et « 01-08-1995 », 0 ; « effet », 1 (art. 2,
  « ne peuvent avoir pour effet de placer les intéressés dans une situation plus
  favorable », qui ne date rien) ; « publication », 1 (art. 2, XIII). **Conforme.**
- **Les citations.** L'art. 2, mot pour mot dans l'index : I (« Au premier alinéa de
  l'article 1er, les mots : << catégorie B >> sont remplacés par les mots : << catégorie A
  >> »), IX (« huit échelons » → « douze échelons »), XII (échelons provisoires « 301, 328 et
  342 », « conformément au tableau fixé par l'article 37 du décret no 96-101 du 6 février
  1996 »), XIII (« à compter de la date de publication du décret no 96-101 du 6 février
  1996 »). Les tableaux : trois renvois au papier dans l'art. 2 (X, XII, XIII), deux dans
  l'art. 1er (tous deux au IV, les échelons provisoires 541 et 547 à 660), chacun « Vous
  pouvez consulter le tableau dans le JO no 0033 du 08/02/96 Page 2070 a 2077 ». Le résumé
  du texte : « LA PRINCIPALE MODIFICATION INTERESSE LE CADRE D'EMPLOIS DES SECRETAIRES DE
  MAIRIE,CLASSE EN CATEGORIE A,A COMPTER DU 01-08-1995 », une seule fois, hors des articles.
  **Conformes.**
- **Le LEGI.** Du décret, il garde le texte (LEGITEXT000005620312, du 1996-02-08) et
  l'art. 38 (LEGIARTI000006377880, du 1995-08-01 à 2999-01-01, dont le texte n'écrit aucune
  date) ; la requête sur le titre « 96-101 » ne rend rien d'autre. L'art. 1er du n° 87-1104
  a deux versions qui se chevauchent : LEGIARTI000006370685 (1987-12-31 → 1996-02-08 : 342
  à 620, huit échelons, et les provisoires 328, 301, 274) et LEGIARTI000006370686
  (1995-08-01 → 2017-01-01 : douze échelons, 374 à 695). **Conforme.**
- **Les grilles, inchangées.** Dans le commit, ni `echelons.csv` ni `grilles.csv` ne bougent
  ailleurs que pour le chef de projet SRIC (point 2). **Conforme.**
- **La péréquation de la CNRACL, à la publication.** L'art. 28-1 du n° 87-1103 (art. 2, XIII)
  dit « à compter de la date de publication » : conforme. Remarque : le mot « péréquation »
  n'est pas dans le texte, qui écrit « les assimilations prévues pour fixer les émoluments de
  base mentionnés à l'article 15 » du n° 65-773 ; l'art. 16 bis de ce décret
  (LEGIARTI000006368218) donne ces règles d'assimilation « par dérogation à l'article 16 ».
  La glose de la fiche (« pour la péréquation des pensions de la CNRACL ») dit le mécanisme,
  la citation entre guillemets est exacte : aucune correction.
- **Écart mineur : « récrit » est une inférence.** La fiche et le bloc « Reprise » écrivent
  que le n° 96-101 « récrit » l'art. 1er du n° 87-1104. Aucun des sept articles ne le dit, et
  le résumé du texte (non normatif) ne cite pas le n° 87-1104. Ce qui le fait
  croire est dans le texte même du décret, que la note ne cite pas : le visa, « Vu le décret
  no 87-1104 du 30 décembre 1987 portant échelonnement indiciaire du cadre d'emplois des
  secrétaires de mairie » (JORFTEXT000000191345, seule mention du n° 87-1104 dans le
  texte), et la date du 1er août 1995 que le LEGI donne à la version à douze échelons. Un
  visa qui cite un texte sans « modifié » ne prouve pas qu'on le modifie. **Gravité :
  mineure** (la question posée au propriétaire est la bonne, le JO papier tranchera) ; à
  corriger en écrivant « que le n° 96-101 paraît récrire (son visa le cite ; le LEGI date du
  1er août 1995 la version à douze échelons) ».

## 2. Le chef de projet SRIC

- **Les sources, mot pour mot.** N° 2016-82, art. 1er (JORFARTI000031942010, num 1) :
  « ÉCHELONS INDICES BRUTS Echelon spécial HEA 9e échelon 1015 8e échelon 985 7e échelon 946
  6e échelon 901 5e échelon 850 4e échelon 800 3e échelon 750 2e échelon 700 1er échelon 650 » ;
  « Le présent décret entre en vigueur le 1er février 2016. » (art. 3). N° 2017-171, art. 8
  (JORFARTI000034026698, num 8), colonne 2017 : « 10 HEA HEA 9 1021 1027 8 990 996 7 951 959
  6 906 912 5 855 861 4 805 812 3 755 762 2 705 711 1 656 661 » ; « Les dispositions du
  présent décret entrent en vigueur le 1er janvier 2017. » (art. 126, JORFARTI000034026585).
  N° 2017-1381, art. 2 (JORFARTI000035600863, num 2) : « la ligne : « 10 HEA HEA » est
  remplacée par la ligne : « ES HEA HEA » » ; art. 7 (JORFARTI000035600872) : « Les
  dispositions du présent décret entrent en vigueur le 1er janvier 2017. » ; sa notice :
  « le décret procède à des corrections ». Les numéros d'article sont ceux de la colonne
  `num` de l'index, non un rang d'identifiant. **Conformes.**
- **Les cinq versions de l'art. 14-1-1 du n° 2008-836 au LEGI.** LEGIARTI000031948241
  (2016-02-01 → 2017-02-13 : « Echelon spécial HEA », 650 à 1015) ; 034034377 (2017-02-13 →
  2017-01-01, jamais en vigueur : « 10 HEA HEA ») ; 035602721 (2017-01-01 → 2018-01-01),
  036489603 (2018-01-01 → 2026-11-01) et 054954874 (dès le 2026-11-01), les trois à « ES HEA
  HEA », 656 à 1021 en colonne 2017, 661 à 1027 en 2018 puis 2019. **Les trois versions de
  `ES_ECHELON_SPECIAL` sont exactement celles qui portent « ES ».**
- **Les valeurs.** Neuf échelons (656, 705, 755, 805, 855, 906, 951, 990, 1021) et l'échelon
  spécial à HEA dès le 1er janvier 2017 ; 661, 711, 762, 812, 861, 912, 959, 996, 1027 dès le
  1er janvier 2019 : celles du JORF, et du LEGI. Le 10e rang de la ligne spéciale suit la règle
  de l'en-tête de `echelons.csv` (« l'échelon spécial prend le rang qui suit le plus haut »).
  **Conformes.**
- **Ce qui bouge, et rien d'autre.** `git show 9cb387b` sur `echelons.csv` : 18 lignes ôtées
  (le nom `…-de-l-etat-es-hea-hea`) et 19 ajoutées (le nom `…-de-l-etat`, les mêmes indices,
  et la ligne `special,10,2017-01-01,,,A` de LEGIARTI000035602721) ; sur `grilles.csv` : une
  ligne, la même grille, de 9 à 10 échelons ; aucune autre ligne des deux fichiers. Aucun
  fichier du dépôt (hors index et historique) ne porte plus l'ancien nom. J'ai refait
  l'extraction (`extraire()`, en mémoire, les quatre versants) et comparé à ce qui est
  commité : aucune ligne en trop ni en moins, 1794 grilles et 21 075 périodes de l'État. Dans
  `certification.json` et `moteur/donnees.json` : l'empreinte de `grilles_etat_legi_indice`
  change (la clé change), ses 19 943 valeurs non ; `grilles_etat_legi_rang` passe de 21 067 à
  21 068 (la ligne spéciale). `docs/parcours_presentation.md` : 441 830 → 441 831, la somme
  ancrée. **Conforme.**
- **Le test.** `test_la_grille_du_chef_de_projet_sric_de_2016_cesse_au_1er_janvier_2017`
  attend, au 15 janvier 2017, sous `…-de-l-etat`, les valeurs du JORF écrites dans le test
  (656 à 1021, puis l'échelon spécial à HEA), plus rien sous l'ancien nom, et pour 2016
  « 650 … 1015 » et HEA du n° 2016-82 : des valeurs du texte, non du code. Relancé :
  `tests/test_grilles_legi.py`, 68 passés. Il lit les CSV commités, non le code : il garde la
  donnée ; l'accord du code et de la donnée, je l'ai vérifié à la main (l'extraction refaite,
  ci-dessus, ne diffère d'aucune ligne). **Conforme.**
- **La règle d'un mot.** `re.sub(r"(?<![\w'])ES(?=\s+HE[A-G])", "Echelon spécial", …)` ne
  s'applique qu'aux trois versions de l'ensemble. Le LEGI compte 22 versions d'articles qui
  écrivent « ES » devant une lettre hors échelle (j'ai recompté : 22, dans huit textes) ; les
  19 autres gardent leur lecture d'avant, et leurs neuf grilles gardent « -es- » dans le
  nom (recompté dans `grilles.csv` : neuf). Ce que B-ter dit n'être « pas relu » l'est bien
  resté. **Conforme.**
- **Remarque : « ES » n'est pas développé par le texte.** La note de B-ter le dit (« le
  n° 2017-1381 écrit « ES », sans le développer ; « échelon spécial » est le mot du
  n° 2016-82 pour le même emploi, et la ligne prend la place d'un 10e échelon ») ; la fiche
  écrit « est l'échelon spécial, que le n° 2016-82 écrivait « Echelon spécial HEA » », ce qui
  donne la base de la lecture sans dire qu'elle est une lecture. Pas un écart (la lecture est
  la seule cohérente : la ligne remplace « 10 », le n° 2016-82 avait neuf échelons et un
  échelon spécial à HEA, et le tableau 2017 a neuf échelons plus la ligne) ; une demi-phrase de
  plus dans la fiche la rendrait irréprochable.

## 3. Le directeur de recherche de 2e classe

- **Les sources, mot pour mot.** N° 2017-171, art. 36 (JORFARTI000034026745, num 36) :
  « Directeur de recherche de 2e classe 6 HEA HEA 5 1021 1027 4 962 969 3 906 912 2 857 862 1
  807 813 » ; n° 2018-917, art. 1er (JORFARTI000037532992, num 1 ; date d'index 2018-10-27,
  décret du 25 octobre 2018), II : « Au 1er septembre 2017, le tableau figurant à l'article 4
  du décret du 17 septembre 2012 susvisé est remplacé par les tableaux suivants », colonnes
  « INDICES BRUTS à compter du 1er septembre 2017 » et « à compter du 1er janvier 2019 » :
  « Directeur de recherche de 2e classe 7e échelon HEB HEB 6e échelon HEA HEA 5e échelon 1021
  1027 4e échelon 963 969 3e échelon 906 913 2e échelon 857 863 1er échelon 807 814 ».
  Aucune de ces quatre sources (n° 2016-82, 2017-171, 2017-1381, 2018-917, soit 145 documents)
  ne contient « pension », « rétroactif » ni « retroactif » : 0 occurrence, recomptée. La
  notice du n° 2018-917 : « le texte entre en vigueur à compter du 1er janvier 2017 », sans
  article d'entrée en vigueur (l'art. 2 est l'exécution). **Conformes.**
- **Les valeurs.** 962 → 963 au 4e échelon, un 7e échelon à HEB : exacts, au 1er septembre 2017,
  comparés à la colonne 2017 du n° 2017-171 ; les 1er, 2e, 3e et 5e échelons (807, 857, 906,
  1021) et le 6e (HEA) ne changent pas à cette date. Les données (`echelons.csv`, grille
  `directeur-de-recherche-de-2e-classe` du n° 2012-1058) portent ces valeurs, 963 et le 7e à
  HEB dès 2017-09-01 (LEGIARTI000034774287). **Conformes.**
- **Écart mineur : la déclaration ne chiffre que 2017.** La fiche écrit que la pension
  liquidée « du 1er septembre 2017 au 27 octobre 2018 » a pu l'être sur la grille appliquée
  alors, et que le II donne « un 4e échelon à 963 au lieu de 962 ». Pour les quatre derniers
  mois de 2017, c'est exact. Pour 2018 (dix mois sur les quatorze), le n° 2017-171 donnait,
  en colonne « A compter du 1er janvier 2018 », une autre grille, que le II remplace en entier
  (il n'a pas de colonne 2018, seulement 2017 puis 2019) :

  | échelon | n° 2017-171, 1er janvier 2017 | n° 2017-171, 1er janvier 2018 | n° 2018-917, II, du 1er septembre 2017 au 31 décembre 2018 |
  |---|---|---|---|
  | 1er | 807 | 813 | 807 |
  | 2e | 857 | 862 | 857 |
  | 3e | 906 | 912 | 906 |
  | 4e | 962 | 969 | 963 |
  | 5e | 1021 | 1027 | 1021 |
  | 6e | HEA | HEA | HEA |
  | 7e | — | — | HEB |

  En 2018, le II est donc de 5 à 6 points sous la colonne du n° 2017-171 à chaque échelon
  chiffré (« 963 au lieu de 969 », non « au lieu de 962 »). De même, le 1er échelon du
  directeur de recherche de 1re classe : « 1 1021 1027 » au n° 2017-171, « 1er échelon 1021
  1027 » (1er septembre 2017, 1er janvier 2019) au II : 1027 en 2018 d'un côté, 1021 de
  l'autre ; la fiche ne nomme pas cette classe. Les données suivent le II (1021 jusqu'au
  31 décembre 2018, 1027 dès 2019). Aucun texte lu ne dit quelle colonne les caisses ont
  appliquée en 2018 : c'est ce que la fiche déclare déjà (« qu'elle ait été révisée, aucun
  texte lu ne le dit »). **Gravité : mineure** (la déclaration est vraie ; son exemple
  chiffré est trop étroit) ; à compléter par « ou, en 2018, de 969 au lieu de 963 (de 1027 au
  lieu de 1021 pour le 1er échelon de la 1re classe) ».

## 4. Ce que les textes ne tranchent pas, déclaré

Déclaré à la fiche et au bloc « Reprise » : la période du 1er août 1995 au 7 février 1996 des
grilles des secrétaires de mairie (NON TRANCHÉ, trois articles à lire au JO papier, question
au propriétaire) ; l'absence de toute mention de pension ou de rétroactivité dans les quatre
décrets, et que des pensions ont pu être liquidées sur la grille appliquée alors (avec
l'écart du point 3) ; la lecture de « ES » (dans la note) ; les neuf autres grilles « ES » et
les échelons provisoires 301, 328, 342 du n° 87-1103 (candidats, dits « non relus »). Le
journal de veille de B-ter (`2026-11-05-action-158-b-ter.yaml`) dit la même chose, y compris
ses « 22 » versions : recomptées. La note de B (`2026-11-05-chainage-corrige-et-trois-
articles.md`) : un renvoi daté ajouté à la fin (cinq lignes), aucune ligne récrite.

## Candidats (hors de la tâche, non corrigés)

- La version LEGIARTI000054954874 de l'art. 14-1-1 du n° 2008-836, en vigueur dès le
  1er novembre 2026, s'ouvre sur « Conformément à l'article 10 du décret n° 2026-928 du
  5 octobre 2026 […] 1er novembre 2026 » et parle désormais de l'emploi de « conseiller
  numérique des administrations de l'Etat » (« régi par le décret n° 2016-81 […] relatif à
  l'emploi de conseiller numérique »), tout en gardant la ligne du tableau « Chef de projet
  en systèmes et réseaux d'information et de communication des administrations de l'Etat ».
  Le nom de la grille, tiré de cette ligne, n'a pas changé ; le n° 2026-928 n'a pas été lu
  (un texte de cinq jours) : à lire avant d'écrire que la grille a gardé son nom.
