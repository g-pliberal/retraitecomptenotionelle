# Relecture de B : la tête du bloc « Reprise » (le rang de `rangs_grille`, le n° 91-783, l'article 2 du n° 2009-1322)

File R-B, le 5 novembre 2026 : relecture indépendante des commits bf56434 et ee16afd
de la session B (note `2026-11-05-tete-du-bloc-rangs-91-783-et-2009-1322.md`). Rien
n'est repris de B ni de mémoire : chaque article cité ici a été rouvert pendant la
session, dans la table `doc` de l'index LEGI publié (incrément 20261102-213929) et de
l'index JORF publié (incrément 20261103-002311), récupérés par
`dila_index.py --recuperer` ; chaque ligne du Noyau RH dans
`data/reference/grilles/etat/`. Les scripts et les tests ont été relancés dans un arbre
à part, au commit parent (bf56434^) et à 3637f88. Rien n'a été modifié dans le dépôt,
hors cette note et l'entrée du journal de veille.

**Verdict. Les trois points sont justes à la source ; les citations sont mot pour mot ;
les deux tests sont rouges sans la correction, pour la raison attendue ; les scripts
refont à l'identique les fichiers commités ; rien ne bouge hors des grilles, du chaînage
et de la certification.** Aucun écart grave ni moyen. Deux écarts mineurs (3.4 et 3.5),
qui ne changent aucun chiffre.

## 1. `rangs_grille` n'est pas le rang du Noyau RH : conforme

Noyau RH, `etat/echelons.csv`, grille 02777 en vigueur le 2011-07-01 (du 2011-07-01 au
2011-12-31) : échelons 15598 (rang 1, 581), 15597 (rang 2, 598), 15596 (rang 3, 616),
15595 (rang 4, 620), 15594 (rang 6, 631, nature « exceptionnel ») ; pas de rang 5. Les
cinq lignes et les cinq indices de la note de B sont exacts. L'en-tête de
`chainage/reclassements.csv` porte la phrase ajoutée à `ENTETES["reclassements"]`, et la
docstring de `periodes_noyau` dit de même.

Test `test_l_entete_dit_que_rangs_grille_n_est_pas_le_rang_du_noyau`, lancé au commit
parent avec les données du parent : rouge sur l'assertion de la phrase (« la place de
l'échelon parmi ceux de la grille le jour du reclassement, non la colonne rang du Noyau
RH » absente de l'en-tête) ; la relecture du noyau, elle, passe ([1, 2, 3, 4, 6]).

## 2. Le n° 91-783 n'a pas d'article qui énumère ses corps : conforme

LEGI, LEGITEXT000006077923 : 36 versions de 23 articles (1 à 23). Aucune ne nomme un
corps d'un ministère. L'art. 1er, aux deux versions que la note cite
(LEGIARTI000006461848, du 1992-02-08 au 2007-05-03 ; LEGIARTI000006461849, du
2007-05-03 au 2012-10-01), commence mot pour mot comme B le cite ; il ajoute « Les membres
de ces corps exercent leur activité à l'administration centrale et dans les services
déconcentrés des ministères […] » et « Il peut être créé […] des corps communs à
plusieurs ministères ». Le JORF du 20 août 1991 (JORFARTI000001180074) donne le même
art. 1er, « services extérieurs » au lieu de « services déconcentrés » : pas
d'énumération non plus dans la version d'origine, que le LEGI ne porte pas. L'art. 18
(LEGIARTI000006461877) intègre les assistants du décret du 19 octobre 1959 « dans le
corps d'assistants de service social du ministère dont ils relèvent », sans les nommer.

« L'un des corps régis par le présent décret » est dans les art. 9 (versions depuis le
2007-05-03 ; celle de 1991, LEGIARTI000006461863, ne le dit pas), 14, 16 et 17 ; B cite
9, 16 et 17, ce qui suffit à son propos. L'art. 15 (LEGIARTI000006461873, 634
caractères) ne contient pas « régis ». Les deux commentaires récrits disent vrai ; un
commentaire ne se teste pas, et aucun fichier de données n'a bougé pour ce point.

## 3. L'article 2 du n° 2009-1322 en 2017 : conforme, deux écarts mineurs

### 3.1 Les citations

- LEGI, art. 2 du n° 2009-1322 : six versions, LEGIARTI000021214940 (2009-10-31 →
  2015-12-31), LEGIARTI000031831690 (2015-12-31 → 2017-01-01), LEGIARTI000034034492
  (2017-01-01 → 2018-01-01), LEGIARTI000037196211 (2017-01-01 → 2025-07-01),
  LEGIARTI000036489719 (2018-01-01 → 2017-01-01, « jamais en vigueur »),
  LEGIARTI000051553099 (depuis le 2025-07-01). Le tableau de B en donne cinq, sans celle
  de 2009, hors de propos.
- JORF, n° 2017-171, art. 39 (JORFARTI000034026752) et art. 126 (JORFARTI000034026585) ;
  n° 2017-1737, art. 17 (JORFARTI000036250727, JO du 23 décembre 2017) ; n° 2018-610,
  art. 1er (JORFARTI000037193171) et art. 2 (JORFARTI000037193174), notice
  (JORFTEXT000037193165) : chaque passage cité par B l'est mot pour mot.
- Le texte de LEGIARTI000034034492 est celui de l'art. 39 du n° 2017-171 ; celui de
  LEGIARTI000037196211, celui de l'art. 1er du n° 2018-610 ; celui de
  LEGIARTI000036489719, le premier où « 2018 » devient « 2019 », comme l'écrit l'art. 17
  du n° 2017-1737.
- Noyau RH : grille 03500 (« Ingénieur d'études et de l'exploitation de l'aviation civile
  de classe normale »), textes 641 (origine), 645, 5946 et 5947 (modificatifs) ; 5946 est
  le n° 2018-610, 5947 le n° 2018-609, tous deux d'effet au 2017-01-01 ; le n° 2017-171
  n'y est pas cité. Au 2017-01-01 : rangs 1 à 11, 434, 483, 508, 525, 565, 610, 649, 686,
  727, 744, 774, comme B le dit.

### 3.2 La rétroactivité, à ce que disent les textes lus

Le n° 2018-610 « remplace » l'art. 2 (art. 1er) et « entre en vigueur le 1er janvier
2017 » (art. 2 ; la notice le redit) ; le n° 2018-609 du même jour, qui récrit le statut
(n° 71-917), fait entrer au même jour « la section 1 du chapitre Ier et […] l'article 9 »
(art. 11, JORFARTI000037193138). Pour toute date à partir du 1er janvier 2017, l'art. 2 se
lit donc dans la rédaction du n° 2018-610 : la lecture de B (« ne vaut à aucune date »)
est celle des textes, et celle du Noyau RH.

Rien, dans les textes lus, ne garde un effet de la version du n° 2017-171 : le
n° 2018-610 n'a que trois articles (remplacement, entrée en vigueur, exécution) ; le
n° 2018-609 ne garde que « les réductions et majorations d'ancienneté accordées au titre
des années précédant l'année 2017 » (art. 9, JORFARTI000037193136) et le régime des
concours déjà ouverts (art. 10) ; il ne reclasse pas les IEEAC en place (son art. 2 est
le tableau d'intégration des TSEEAC). Le n° 2017-171 (JORFTEXT000034026392) ne touche
aux IEEAC que par son art. 39, qui remplace le tableau d'indices échelon pour échelon
(onze, neuf et trois échelons, comme avant) ; au JORF, aucun décret publié de juin 2016
au n° 2018-609 ne nomme le n° 71-917 dans son titre ; au LEGI, l'art. 17 du statut passe
de LEGIARTI000031831608 (jusqu'au 2017-01-01) à LEGIARTI000037197020 (dès le
2017-01-01), sans version entre les deux.

Un maintien n'aurait pas d'objet : refait à la main, colonne « 1er janvier 2017 » contre
colonne « 1er janvier 2017 », aucun indice du n° 2018-610 n'est plus bas que celui du
n° 2017-171. Classe normale, 2e à 11e : 483 = 483, puis +7, +10, +5, +10, +10, +10, +14,
+7, +7 ; principal, 1er à 9e : +43 (566 → 609), +6, +6, +12, +10, +14, +9, +8, +1 ; hors
classe : 971 → 979, 1021 → 1022, HEA = HEA ; élève : 340 et 359, égaux ; le 1er échelon
de classe normale du n° 2017-171 (421) contre le « 1er » d'ingénieur stagiaire du
n° 2018-610 (434) : +13.

Le n° 2018-610 vise l'art. 148 de la loi n° 2015-1785 (JORFARTI000031733035) : c'est
l'abattement sur les indemnités des corps revalorisés au titre du protocole, non une
autorisation de rétroagir. Aucun texte lu ne dit si la rétroactivité est régulière ; la
jurisprudence n'a pas été ouverte, et rien n'en est affirmé ici.

### 3.3 Ce que portaient les quatre lignes ôtées, et ce qui reste

Au commit parent, `etat_legi/echelons.csv` portait, pour 2017 (du 2017-01-01 au
2017-12-31, LEGIARTI000034034492) : le 1er échelon de classe normale à 421 (colonne 2017
de l'art. 39 du n° 2017-171), et un groupe « Ingénieurs des études et de l'exploitation de
l'aviation civile Ingénieur des études et de l'exploitation de l'aviation civile hors
classe », né de l'intertitre du tableau du n° 2017-171 collé au grade : 1er 971, 2e 1021,
3e HEA. Une seconde hors classe, celle du n° 2018-610 (979, 1022, HEA), était à côté : en
2017, deux hors classe, et une classe normale de onze échelons mêlant deux décrets.

Au commit 3637f88, en vigueur le 2017-06-30 : classe normale 2e à 11e, 483 à 774 ;
principal 1er à 9e, 609, 633, 697, 763, 821, 879, 929, 979, 1022 ; hors classe 979, 1022,
puis HEA (ligne de LEGIARTI000031831690, que la fusion des valeurs égales prolonge) ;
ingénieur stagiaire 434 ; élève 340 et 359. Chaque valeur est celle de la colonne
« Au 1er janvier 2017 » de l'art. 1er du n° 2018-610 ; aucune ligne ne vient de
LEGIARTI000034034492.

### 3.4 Les tests et la reproduction

- `test_la_grille_de_2017_des_ieeac_est_celle_du_decret_2018_610`, au commit parent : rouge
  sur la première assertion (des lignes de LEGIARTI000034034492 restent), la raison
  attendue. Les valeurs attendues viennent du JORF, non du code.
- `dila_legi_grilles.py --index …`, relancé à 3637f88 : aucun fichier ne change (484
  textes, 1 794 grilles, 21 074 périodes d'échelons pour `etat_legi`). La seule
  différence de code avec le parent est l'entrée de `DATES_CORRIGEES` et sa docstring.
- `dila_legi_chainage.py --index …`, relancé à 3637f88 : aucun fichier ne change (612
  lignes de durées `rattache`, 511 grades rattachés ; 13 grades de reclassement).
- Certification : `grilles_etat_legi_rang` 21 071 → 21 067 (les quatre lignes) ;
  `_indice` 19 946 → 19 943 (421, 971, 1021 ; le HEA n'a pas d'indice). ee16afd ne change
  que ces deux comptes dans `moteur/donnees.json`.

**Écart mineur (3.4).** La ligne de chaînage qui reste, hors classe du n° 71-917, art. 17
(LEGIARTI000037197020) rattachée à la grille du LEGI du 2017-01-01 au 2025-07-01, a pour
preuve : « l'article qui fixe la grille (LEGIARTI000034034492, LEGIARTI000037196211) nomme
ce statut par sa date ». Or, depuis la correction, LEGIARTI000034034492 ne fixe la grille
à aucune date, et `etat_legi` n'en a plus une ligne : le chaînage lit les dates du LEGI,
sans `DATES_CORRIGEES`. Le rattachement reste juste, la seconde version suffit à la
preuve ; c'est une citation de trop, que B a vue et dite, mais pas déclarée comme à
corriger. À ôter, test d'abord, quand le chaînage lira `DATES_CORRIGEES`.

### 3.5 « Rien ne bouge dans le modèle, les carrières, les témoins, les cas »

Vrai. Les deux commits ne touchent ni `src/`, ni `moteur/js/`, ni `tests/temoins/`, ni les
cas ; `moteur/donnees.json` ne porte des grilles que les traces de certification. Aucun
fichier du moteur ni de `src/` ne lit `etat_legi` ; le simulateur ne pré-remplit encore
aucune carrière depuis un corps : il ne pré-remplit donc pas de carrière d'IEEAC en 2017.

**Écart mineur (3.5), à déclarer.** B déclare que « ni la paie versée de février 2017 à
juillet 2018 sous le n° 2017-171, ni son rappel, ne sont dans les textes lus ». Il manque
la pension : un IEEAC dont la pension a pris effet entre le 1er janvier 2017 et le
14 juillet 2018 a pu être liquidé sur les indices du n° 2017-171, appliqués alors ; si sa
pension a été révisée, aucun texte lu ne le dit. Sans effet aujourd'hui, puisque rien ne
lit ces grilles ; à déclarer avant l'étape qui pré-remplira les carrières, le scénario 1
étant le droit « tel que la caisse l'applique ».

## 4. Ce que les textes ne tranchent pas : déclaré

- Le « 1er » (434) que le n° 2018-610 range sous l'ingénieur stagiaire, quand le statut
  (n° 71-917, art. 17, LEGIARTI000037197020, écrit par l'art. 3 du n° 2018-609) compte un
  « 1er échelon » de classe normale (1 an) et que le Noyau RH en fait le rang 1 de la
  classe normale : déclaré par B (note, journal de veille).
- Les trois autres articles que le LEGI date en vigueur ensemble (n° 2008-836,
  art. 14-1-1 ; n° 2012-1058, art. 4 ; n° 87-1104, art. 1er) : inscrits pour la suite,
  au bloc « Reprise » de l'action 158 (« Reste, test d'abord : les autres articles que le
  LEGI date en vigueur ensemble […], à lire au JORF »), dans la note de B
  (« Candidats pour le propriétaire ») et à son journal de veille (`reste`).

`tests/test_textes.py`, que B disait rouge sur `origin/main` : vert à 3637f88 (11 tests).
