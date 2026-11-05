# Relecture de E (CARCDSF)

File R-E2, le 5 novembre 2026 : relecture indépendante des commits ca77a60 et 564a5b7 (file E, note
`2026-11-05-carte-des-fiches-carcdsf-lue-au-droit.md`), qui lisent au droit la fiche
`carcdsf_minoration_age_seul`. Chaque texte a été rouvert dans les index JORF et LEGI récupérés par
`dila_index.py --recuperer` (JORF à jour du 3 novembre 2026, LEGI du 2 : tous les textes en cause
sont plus anciens). Chaque citation a été confrontée par un script au texte de l'index, guillemets
ôtés et espaces ramenées. Chaque cas a été joué dans les deux moteurs, sur la même requête
(statut `chirurgien_dentiste_ou_sage_femme`, carrière dès 25 ans sauf mention) : le Python par
`_python` (`tests/test_liquidation.py`), le portage par `tests/js/comparer-liquidation.mjs`.
Puis une seconde fois sous `PRESOMPTIONS_DECALEES=1`, le portage par une copie de ce script, hors
du dépôt, qui pose au paquet les `DECALAGES` du pont : le script du dépôt lit le paquet sans
passer par le pont, et sous la variable il ne décale rien. La naissance s'écrit entière
(`naissance=AAAA-MM-01`) : la saisie ne lit pas de clé `naissance_jour`. Un premier essai qui la
passait a pris le 15 du mois présumé, et chaque date d'effet y avançait d'un mois. Il est écarté.
Rien n'a été modifié : ni règle, ni donnée, ni fiche, ni test, ni le bloc « Reprise ».

**Verdict : conforme à la source pour l'essentiel.** Les 23 citations sont exactes, mot pour mot.
Les publications, les entrées en vigueur et les bornes des sept versions sont justes, comme les
calculs de la note et la carte. Les tests du lot passent (`tests/test_carte.py`,
`tests/test_sections_liberales.py` : 65 verts). **Les six erreurs du modèle sont réelles**, dans les
deux moteurs, et de même sous `PRESOMPTIONS_DECALEES=1`. Chaque valeur du modèle que donne la note
s'y retrouve exactement. **Deux écarts moyens** :

- la pension du 1er janvier 2024 n'est pas « ce que le texte ne tranche pas » : c'est une erreur
  de 12 à 13,5 points (§ 5) ;
- le refus de l'inapte frappe toute la liquidation, base CNAVPL comprise, où le texte est sans
  ambiguïté (§ 4, erreur 3).

**Cinq écarts faibles** : l'erreur 4 est plus fréquente qu'écrit (§ 4) ; les ampleurs de l'erreur 5
comprennent une part de l'erreur 4 (§ 4) ; une élision masque l'article 18 du règlement de 1955,
resté en vigueur jusqu'en 2011 (§ 1) ; le plafond de « 2,5 points au plus » des nés avant juillet
1951 est de 3,75 (§ 3) ; une erreur de renvoi dans la note (§ 5).

## 1. Les textes et les citations

Le script a cherché chaque fragment cité (entre guillemets, hors renvois d'article) dans le texte de
l'identifiant que la fiche nomme : 23 citations, dans les sept versions, aucun fragment absent.

| Version | Texte | Publié | En vigueur | Contrôle |
|---|---|---|---|---|
| statuts de 2007 | JORFARTI000001859980, art. 18, 20, 23 ; JORFARTI000002063756, art. 39, 48 | 10 oct. 2007 | 11 oct. 2007 | conforme |
| statuts de 2011 | JORFARTI000023909792, art. 17, 19, 22 ; arrêté, art. 2 et 3 | 27 avr. 2011 | 1er juil. 2011 | conforme |
| bornes de 2012 | JORFARTI000026208364 ; arrêté, art. 1er | 21 juil. 2012 | 22 juil. 2012 | conforme |
| statuts de 2017 | JORFARTI000036251928, 3°, 21°, 25° ; arrêté, art. 1er | 24 déc. 2017 | 25 déc. 2017 | conforme |
| statuts de 2024 | JORFARTI000048880707, 4°, 8° ; arrêté, art. 1er et 2 | 9 janv. 2024 | 10 janv. 2024 | conforme |
| règlement de 2026 | JORFARTI000054435749, art. 1er, 3, 5, 9, 18, 24 ; arrêté, art. 1er | 17 juil. 2026 | 18 juil. 2026 | conforme |
| décret n° 2026-418 | JORFARTI000054153467 (art. 5, 3°), JORFARTI000054153813 (art. 30) | 31 mai 2026 | 1er juil. 2026 | conforme |

- **Les numéros d'articles** ont été relus dans les annexes : 18, 19 (« à jour de ses
  cotisations »), 20, 21 à 23 en 2007 ; 32, 33 et 41 en 2011. La table de renumérotation de 2017
  (3°) fait bien de 19 l'article 35, et de 41 l'article 51. L'annexe de 2017 s'ouvre sur « la
  section professionnelle des agents généraux d'assurance ». L'article 1er de l'arrêté et ses visas
  (l'arrêté du 13 avril 2011 de la CARCDSF) nomment les chirurgiens-dentistes et les sages-femmes.
  L'erreur de plume est fondée.
- **Pas de majoration au-delà de 65 ans en 2007** : l'article 26 n'applique au montant que « les
  coefficients de minoration et de majoration visés aux articles 20 et 23 ». La majoration de
  l'article 23 est celle des trois enfants ; les « coefficients de majoration » de l'article 33
  portent sur le prix du rachat. Conforme.
- **Le code de la sécurité sociale**, à la version de chaque date :
  - L. 161-17-2 : rédaction du 23 décembre 2011, 62 ans pour les nés depuis 1955 ; du 1er septembre
    2023, 64 ans depuis 1968 ; du 31 décembre 2025 (LEGIARTI000053280889), 64 ans depuis 1969 ;
  - L. 351-8, 1° : 1er septembre 2023 et 28 février 2025, « augmenté de trois années » ;
  - L. 643-3, IV : 2023 et 2025, mot pour mot ;
  - L. 643-4, 2° ; D. 643-14 ;
  - D. 351-1-14 : 2023 et 2026, 62 ans pour l'inapte.

  Tout est conforme. La loi n° 2023-270 (article 10, JORFARTI000047445097) récrit le 1° de
  L. 351-8 sans disposition qui garde, pour les nés de 1951 à 1954, l'ancien âge majoré de cinq
  ans. La lecture « 67 ans » de l'erreur 5 est donc fondée sur la lettre.
- **Écart faible, une élision.** La fiche cite l'article 2 de l'arrêté du 1er octobre 2007
  (JORFARTI000002267801) avec un « […] » qui ôte la fin de la phrase : l'arrêté de 1955 « est
  abrogé à l'exception de l'article 18 des statuts relatifs au régime d'assurance vieillesse
  complémentaire ». Cet article 18 de 1955 est resté en vigueur avec les statuts de 2007, jusqu'à
  l'arrêté du 28 décembre 2010 : « L'article 18 mentionné à l'article 2 de l'arrêté du 1er octobre
  2007 est abrogé » (article 2, JORFARTI000023336803, publié le 1er janvier 2011). Son texte n'est
  pas à l'index. C'est probablement le cumul : le même arrêté insère le titre VII, « Retraite
  libérale et activité professionnelle ». Il est donc sans effet probable sur la minoration, mais
  la fiche ne dit nulle part qu'une règle de 1955 a survécu jusqu'en 2011. Autre trait, que la
  fiche ne cite pas : l'article 23 de 2007 a une seconde phrase, qui compte pour les 10 % les
  enfants élevés neuf ans avant leurs seize ans.

## 2. Les bornes

Les six arrêtés ont été listés article par article dans l'index. Seul celui du 13 avril 2011 fixe
une date (article 3, le 1er juillet 2011). Les autres ne font que charger de l'exécution ou
ordonner la publication : arrêté de 2007, art. 3 ; de 2012, art. 2 ; de 2017, art. 2 ; de 2023,
art. 2 ; de 2026, art. 2. Aucune annexe ne porte de disposition transitoire sur l'âge ou la
minoration. Sont lus : le chapitre VI de 2011 (articles 49 et 50, les points et le rachat des
sages-femmes), la seule date de l'annexe de 2017 (le paiement mensuel « à compter du 1er janvier
2019 »), et les « mesures transitoires » du règlement de 2026 (les points du régime facultatif).
Les bornes sont donc les dates d'effet, au lendemain de la publication hors 2011. Cette règle
vient de l'article 1er du code civil, ni à l'index LEGI ni, par l'ordonnance n° 2004-164, à l'index
JORF, qui est filtré par thème : la fiche le déclare justement. Le règlement de 2026, appelé par
le décret n° 2026-418 dès le 1er juillet, n'est approuvé que le 18 juillet. Les statuts de 2024
tiennent entre les deux dates, et la règle est la même, mot pour mot. Les arrêtés du 28 décembre
2010, du 30 juillet 2013 et du 21 septembre 2026 sont sans effet sur la minoration : conforme,
sous la réserve de l'article 18 (§ 1).

## 3. Les calculs, refaits à la main

Tous les calculs de la note sont justes, aux dates d'effet qu'elle donne (naissance au 1er du
mois, date d'effet au jour de l'âge, ce que font les deux moteurs) :

- 15 % « au cours de la 63e année » (62 ans et 1 mois) ;
- 10 % au cours de la 64e (63 ans) ;
- 25 % au cours de la 61e (60 ans et 6 mois) ;
- 20 trimestres × 1,50 % = 30 % (le né de 1955 à 62 ans, taux plein à 62 + 5 = 67 ans) ;
- deux années × 5 % (le né de janvier 1951, effet d'un départ à 65 ans le 1er janvier 2016) ;
- les trimestres civils entiers :
  - 7 d'avril 2013 à décembre 2014 ;
  - 11 d'avril 2019 à décembre 2021 ;
  - 2 en 2011 (avril à septembre) ;
  - 7 à 1 % et 4 à 1,25 %, 12 % ;
  - 15 à 1 % et 1 à 1,25 %, 16,25 % ;
  - 11 à 1,25 %, 13,75 % ;
- 8 × 1,25 % = 10 % ;
- 67 − 5 = 62 pour la mère de cinq enfants ;
- 56 mois avant 67 ans : 18 trimestres entiers, 27 %, ou 19 entamés, 28,5 % ;
- la réversion : 60 % × 6 912,27 = 4 147,36 € ; 60 % × 9 423,69 = 5 654,21 €.

Les bases de la réversion ne se refont pas au centime : la note ne donne pas le salaire de la
requête. Au salaire par défaut, la même personne a une base de 8 843,50 € (60 % : 5 306,10 €), puis
de 10 647,24 € (6 388,34 €). Le motif et la règle sont les mêmes.

**Écart faible.** Pour les nés avant juillet 1951, la fiche borne l'écart à « 2,5 points au plus »
si l'année d'anticipation entamée compte. Il va jusqu'à 3,75 points. Né le 1er janvier 1947, avec
un effet au 1er décembre 2011, un mois avant 65 ans : le modèle sert 0,9875 (un trimestre entamé)
dans les deux moteurs ; le texte, 0,95 si l'année entamée compte (0,9958 au prorata).

## 4. Les six erreurs, au moteur

Python et portage rendent partout la même date d'effet, le même motif et le même coefficient.
36 cas ont été joués à la date entière ; 32 d'entre eux, rejoués sous `PRESOMPTIONS_DECALEES=1`,
rendent les mêmes valeurs. 45 cas au jour présumé concordent aussi entre les deux moteurs sous la
variable : le jour décalé y avance la date d'effet d'un mois, sans changer de coefficient, sauf au
1er janvier 2024 (§ 5).

1. **Du 11 octobre au 31 décembre 2007 : réelle, ampleur juste.**
   - Né le 1er octobre 1945, dès 20 ans, effet au 1er novembre 2007 : le modèle sert 1, le texte
     0,85.
   - Né le 1er octobre 1947, dès 20 ans, à 60 ans et 1 mois : le modèle sert 1, le texte 0,75, soit
     25 points.
   - La mère de trois enfants, au 1er novembre 2007 : le modèle sert 1 sans complément, le texte
     1 et 10 %.

   Contre-épreuves conformes : au 1er février 2008, la même reçoit 1 et les 10 %. En 2009, la mère
   de trois enfants reçoit 1 et les 10 %, le père 0,95 et les 10 %, comme le texte. Le né de
   janvier 1945 reçoit 0,90 en janvier 2008.
2. **Du 1er janvier au 30 juin 2011 : réelle, ampleur juste.**
   - Né le 1er septembre 1950, effet au 1er mars 2011 : le modèle sert 0,775, le texte 0,75.
   - Né le 1er janvier 1944, au 1er avril 2011 : le modèle sert 1,09, le texte 1.
   - Né le 1er janvier 1940, au 1er janvier 2011 : le modèle sert 1,20, soit les 20 points.

   L'écart de minoration varie avec l'âge : nul à 61 ans et 1 mois (0,80 des deux côtés), 3,75
   points à 60 ans et 9 mois.
3. **L'inapte et les catégories sans minoration : réelle, ampleur juste.** L'inapte comme l'ancien
   déporté reçoit 0,75 au 1er janvier 2008 (25 points) et 0,70 au 1er janvier 2017 (30 points).
   L'inapte né en 1965 est refusé à 62 ans (`non_ouverte`, âge opposé 62,75 ; le vocabulaire dit
   que le montant n'y est qu'un contrefactuel), puis reçoit 0,85 à 62 ans et 9 mois (15 points).
   **Écart moyen.** Le refus vient de l'ouverture, commune à toute la personne : il frappe aussi
   la pension de base de la CNAVPL. Le contrefactuel la minore à 0,75. Pour la base, le texte ne
   laisse pas de doute : L. 643-3, IV, D. 643-14 et D. 351-1-14 l'ouvrent à 62 ans à l'inapte du
   2° de L. 643-4. Le salarié inapte né en 1965 part bien à 62 ans, au motif `inaptitude`, dans
   les deux moteurs. La fiche range ce refus parmi les erreurs de la CARCDSF, dont elle dit
   pourtant l'âge non tranché (article 1er contre article 3, II). Et la fiche
   `inaptitude_au_travail` ne déclare, pour les professions libérales, que la décote gardée, non
   le refus. C'est une erreur de la base à porter au propriétaire, hors de cette fiche.
4. **La majoration au temps : réelle, ampleur juste, fréquence sous-estimée.**
   - Effet au 1er janvier 2015, né le 1er janvier 1948 : le modèle sert 1,08, le texte 1,07.
     Sans activité de 2010 à 2014 : le modèle 1,08, le texte 1.
   - Effet au 1er octobre 2011, né le 1er janvier 1946 : le modèle 1,03, le texte 1,02.
   - Effet au 1er janvier 2028, né le 1er janvier 1958 : le modèle 1,15, le texte 1,1375.
   - Effet au 1er janvier 2022, né le 1er janvier 1953 : 1,11 des deux côtés.

   **Écart faible.** Le trimestre de trop ne vient pas seulement « quand l'âge tombe le premier
   jour d'un trimestre civil ». Le modèle prend le quotient entier des mois écoulés depuis l'âge,
   le texte les trimestres civils pleins qui suivent celui de l'âge. Le trimestre de trop vient
   donc aussi quand l'âge tombe en cours de trimestre, selon le mois de l'effet. Né le 1er janvier
   1953, taux plein le 1er mars 2019 : au 1er mars 2022, le modèle sert 1,12 et le texte 1,11 ; au
   1er décembre 2021, le modèle 1,11 et le texte 1,10 ; au 1er février 2022, 1,11 des deux côtés.
   La phrase de la fiche ne vaut que pour des effets au premier jour d'un trimestre, ceux du
   texte (article 61 de 2017, article 24 de 2026), que le modèle ne sert pas.
5. **Depuis 2024 : réelle ; ampleurs à partager.**
   - Effet au 1er janvier 2025, né le 1er janvier 1955 : le modèle sert 1,15, le texte 1,12.
   - Effet au 1er avril 2024, né le 1er janvier 1953 : le modèle 1,25, le texte 1,1625.

   **Écart faible.** Les « 3 points » et les « 8,75 points » que la note met au compte de
   l'erreur 5 comprennent le trimestre de l'âge, compté à tort, qui est l'erreur 4. Selon l'ordre
   du partage, c'est 1 à 1,25 point sur 3, et 1,25 sur 8,75. Le reste se partage entre le taux
   et, pour le né de 1953, l'âge de départ : 3,75 points chacun.
6. **La réversion : réelle, ampleur juste.** La ligne de la CARCDSF vaut 0, motif `non_portee`,
   dans les deux moteurs : décès en juin 2020 et en juin 2030, conjointe de 68 et de 72 ans, plus
   de deux ans de mariage. Le texte sert 60 % (2007, article 48 ; 2011, article 41 ; 2026, article
   18). Les montants, voir § 3.

## 5. Ce que le texte ne tranche pas

Sont justement déclarés : le droit d'avant le 11 octobre 2007, au Bulletin officiel ; les
sages-femmes avant le 1er juillet 2011 (les statuts de 2011 les intègrent, articles 49 et 50, au
décret n° 2008-1423) ; le tableau des nés de juillet 1951 à 1954, que l'index ne porte qu'en
renvoi au JO (« Vous pouvez consulter le tableau dans le JOn° 98 du 27/04/2011 texte numéro 14 »).
Aussi : l'année d'anticipation entamée, l'inapte de la CARCDSF à 62 ans, le cumul des plafonds de
20 et de 25 %, l'exercice d'avant le 1er juillet 2011, le trimestre entamé de la minoration et la
date d'effet trimestrielle.

**Écart moyen : la pension du 1er janvier 2024.** Le texte, lui, tranche. Par les bornes mêmes de
la fiche, les statuts de 2017 sont en vigueur jusqu'au 9 janvier 2024. Aucune des deux annexes ne
porte de date d'application. Né le 1er septembre 1961, effet au 1er janvier 2024 : le modèle sert
0,85, dans les deux moteurs ; les statuts de 2017, 0,73 ou 0,715. C'est une erreur de 12 à 13,5
points. Seul le compte du trimestre entamé reste ouvert, avec la pratique de la caisse, que la
fiche demande de lire. Sous `PRESOMPTIONS_DECALEES=1` à jour présumé, l'effet passe au 1er
décembre 2023, et le modèle sert alors 0,715. La fiche le déclare bien en approximation, mais la
note et le compte rendu le rangent parmi ce qui n'est pas tranché, hors de la liste des erreurs à
porter au propriétaire. **Écart faible, de renvoi** : la note renvoie aux « écarts 1, 2 et 6 »
pour ce point, quand l'erreur 6 est la réversion.

## 6. La carte

`carte.manques()`, joué sur l'arbre d'avant le lot (ca77a60^, dans un arbre de travail à part) puis
sur `HEAD` : 85 fiches et 498 manques, puis 84 et 491. Les sept manques levés sont ceux de la fiche
(`domaine`, `etape`, `lit`, `ecrit`, `dates_qui_decident`, `versions`, `approximations`). Les
deux comptes de la note sont ceux du script. Les six publications et entrées en vigueur de
`NAISSANCES_AU_JOURNAL_OFFICIEL` sont celles de l'index.

## 7. Ce que la relecture laisse

- **Non lus, faute d'être à l'index** : l'article 1er du code civil et l'ordonnance n° 2004-164 ;
  l'article 18 du règlement de 1955 ; le tableau de 2011 et de 2012.
- **Non essayés** : l'ancien prisonnier ou combattant de 2007 et le grand invalide de guerre, comme
  la file E.
- **Au propriétaire, en plus des six erreurs** : la pension du 1er janvier 2024 (§ 5), et le refus
  de l'inapte libéral par la base de la CNAVPL (§ 4, erreur 3).
