# Relecture des corrections de R-M4 : le congé de maternité, et quatre écarts faibles, chez les fonctionnaires parents de trois enfants

File R-M4-bis de la sixième vague, le 3 novembre 2026 : relecture indépendante du commit
badc7bf (file M4-bis, note `2026-11-03-corrections-de-la-relecture-r-m4-fonctionnaires.md`),
qui corrige ce que la relecture R-M4 (commit e14c779, note
`2026-11-03-relecture-taux-plein-parents-fonctionnaires.md`) relevait dans le taux plein à
65 ans des fonctionnaires parents de trois enfants nés de juillet 1951 à 1955 (commit
8ea1ce7). Rien n'a été repris de M4-bis, de R-M4 ni de mémoire : l'index de la DILA
récupéré dans la session (LEGI à jour au 3 novembre 2026 après son incrément, JORF au 3
novembre), chaque texte ouvert à la rédaction en vigueur aux dates qui comptent ; les 61
fragments cités entre « » dans les citations des trois versions de la fiche cherchés par
un script dans le texte de l'index (`dila_cherche.py --texte`) : aucun n'y manque, et deux
fragments altérés à dessein (« vingt-cinq semaines », « quinze semaines après ») y sont bien
dits absents ; chaque valeur attendue refaite par un calcul qui n'appelle pas le modèle.
Rien n'a été modifié : ni règle, ni donnée, ni test, ni fiche.

**Verdict : conforme, sauf deux écarts faibles, de forme, sans effet sur aucune valeur.**
L'écart moyen de R-M4 est corrigé comme le texte le veut, et ses quatre écarts faibles
aussi ; les valeurs nouvelles se refont à la main ; les deux moteurs les rendent ; le
paquet se refait à l'octet. Les deux écarts tiennent à la preuve écrite, non à la règle :
la fiche date « seize semaines en 1978 » d'une rédaction du code du travail qui n'était pas
encore en vigueur à la naissance du cas du test (avril 1978 : quatorze semaines), et elle
ne cite pas les statuts territorial, hospitalier et des ouvriers de l'État, qui renvoient
comme celui de l'État à la sécurité sociale pour la durée du congé.

## 1. Les textes, à la rédaction en vigueur

| Texte | Rédaction lue | Constat |
|---|---|---|
| CPCMR, R. 26 ter, I et II | LEGIARTI000024111781, seule rédaction (depuis le 3 juin 2011) | conforme, mot pour mot : « interrompu leur activité pendant une durée d'au moins une année » ; « Cette interruption d'activité doit être intervenue dans le cadre des congés ou de la disponibilité mentionnés au 1° de l'article R. 13 du présent code » ; II : « au moins trente mois consécutifs » |
| CPCMR, R. 13, 1° | LEGIARTI000023449727 (1er janvier 2011 → 1er octobre 2025) | conforme : « d'une durée continue au moins égale à deux mois » ; a) le congé pour maternité « au 5° de l'article 34 de la loi n° 84-16 », « au 5° de l'article 57 de la loi n° 84-53 », « au 5° de l'article 41 de la loi n° 86-33 », « aux articles L. 331-3 et L. 615-19 du code de la sécurité sociale et à l'article 4 du décret n° 72-154 » ; c) le congé parental ; e) « D'une disponibilité pour élever un enfant de moins de huit ans » |
| Loi n° 84-16, art. 34, 5° | LEGIARTI000006450574 (12 janvier 1984 → 27 juillet 1991) et ses quinze rédactions suivantes jusqu'au 27 novembre 2020 (de LEGIARTI000006450575 à LEGIARTI000038922290), « 5° a) » dès LEGIARTI000032442186 (22 avril 2016) | conforme : « 5° Au congé pour maternité, ou pour adoption, avec traitement, d'une durée égale à celle prévue par la législation sur la sécurité sociale », présente dans chacune ; depuis le 27 novembre 2020, l'article est récrit (« Le congé de maternité est accordé pour une durée égale »), hors des naissances qui comptent |
| CSS, L. 331-3 | LEGIARTI000006742541 (21 décembre 1985 → 26 juillet 1994), LEGIARTI000006742542 (→ 26 décembre 2001), LEGIARTI000006742543 (→ 20 décembre 2005), LEGIARTI000006742544 (→ 24 mars 2006), LEGIARTI000006742545 (depuis) | conforme : en 1985, six semaines avant et dix après, « prolongée de deux semaines en cas de naissances multiples », « seize ou de dix-huit semaines » ; en 1994, « seize ou de trente-quatre semaines, quarante-six semaines en cas de naissance de plus de deux enfants » ; en 2005, « du nombre de jours courant entre la naissance de l'enfant et six semaines avant la date présumée de l'accouchement » ; en 2006, « de la date effective de l'accouchement au début de la période de repos » |
| CSS, L. 331-4 | LEGIARTI000006742546 (21 décembre 1985 → 26 juillet 1994), LEGIARTI000006742547 à LEGIARTI000006742550 | conforme : en 1985, huit semaines avant et dix-huit après dès le troisième enfant, « vingt semaines en cas de naissances multiples », vingt-deux après quand des naissances multiples portent les enfants à trois, « vingt-six ou de vingt-huit semaines » ; en 1994, « vingt-six semaines » (remarque, écart 1) |
| CSS, L. 331-5 | LEGIARTI000006742551 (21 décembre 1985 → 26 décembre 2001), LEGIARTI000006742552, LEGIARTI000006742553 (depuis le 24 mars 2006) | conforme : « une période supplémentaire n'excédant pas deux semaines » ; dès 1985 aussi le report du congé à la fin de l'hospitalisation de l'enfant, qui le déplace sans l'allonger |
| Code du travail, L. 122-26 | LEGIARTI000006646773 (23 novembre 1973 → 1er octobre 1978), LEGIARTI000006646774 (→ 3 janvier 1984), LEGIARTI000006646786 (6 mars 2007 → 1er mai 2008) | citations conformes ; en 1973, six semaines avant et « huit semaines après », « quatorze semaines de suspension », un état pathologique « sans pouvoir excéder huit semaines avant la date présumée de l'accouchement et douze semaines après » ; au 1er octobre 1978, dix après, « seize semaines », quatorze après pour l'état pathologique, deux de plus pour des naissances multiples : écart 1 |
| Loi n° 84-53, art. 57, 5° ; loi n° 86-33, art. 41, 5° ; décret n° 72-154, art. 4 | LEGIARTI000006366816 (27 janvier 1984 →) et ses rédactions jusqu'au 27 novembre 2020 ; LEGIARTI000006695883 (11 janvier 1986 →) et ses rédactions jusqu'au 27 novembre 2020 ; LEGIARTI000006769789 (20 décembre 1976 → 16 décembre 1987), LEGIARTI000006769790 (→ 27 novembre 2004) | lus ici, la fiche ne les cite pas : la même phrase que la loi n° 84-16, dans chaque rédaction ; pour l'ouvrière de l'État, « un congé à plein salaire d'une durée égale à celle prévue par la législation sur la sécurité sociale » : écart 2 |
| CSS, L. 381-1 | toutes ses rédactions, de LEGIARTI000006742941 (21 décembre 1985 → 1er janvier 1987) à LEGIARTI000047453431 (depuis le 1er septembre 2023) | conforme : la citation de 1985, mot pour mot ; « n'exerçant pas d'activité professionnelle » ; le temps partiel avec l'allocation parentale d'éducation à taux partiel dès le 26 juillet 1994 ; l'allocation de présence parentale dès le 24 décembre 2000. Aucune rédaction ne nomme un congé parental ni une disponibilité : « disponibilité » n'y vient jamais, « congé » seulement pour le congé de soutien familial, puis de proche aidant |
| CPCMR, L. 18, II et III | LEGIARTI000025076852 (1er janvier 2012 → 16 avril 2023) | conforme : le III vaut pour tous les enfants du II, « A l'exception des enfants décédés par faits de guerre » ; non tranché, déclaré (point 4) |
| CSS, L. 351-12 | LEGIARTI000006742643 (27 décembre 1998 → 1er septembre 2023) | conforme : « Ouvrent également droit à cette majoration les enfants élevés dans les conditions prévues au deuxième alinéa de l'article L. 342-4 » |
| CPCMR, L. 14, I | LEGIARTI000028498863 (22 janvier 2014 → 15 juillet 2018), LEGIARTI000037200740 (→ 1er septembre 2023) | conforme : les deux phrases citées, dont « arrondi à l'entier supérieur » et « Le plus petit des deux nombres », dans les deux |
| Loi n° 2003-775, art. 66 | LEGIARTI000006758610 | conforme : « 2014 II : 1,125 % III : Limite d'âge moins 6 trimestres », « 2015 II : 1,25 % III : Limite d'âge moins 5 trimestres », « 2016 [...] moins 4 », « 2017 [...] moins 3 » |
| Décret n° 2011-2103, art. 1er et 8 | JORFARTI000025061553, JORFARTI000025061595 | conforme : « 1954 61 ans et 7 mois », « A compter de 1955 62 ans » ; « 2° De cinq mois par génération pour les fonctionnaires atteignant cet âge entre le 1er janvier 2012 et le 31 décembre 2014 » |
| Loi n° 2010-1330, art. 28, I à III | LEGIARTI000025014566 | conforme : « nés à compter du 1er janvier 1955, la limite d'âge est fixée à soixante-sept ans » ; quatre, puis cinq mois par génération |

Absents de l'index, et cherchés : l'ordonnance n° 59-244 du 4 février 1959, le statut
d'avant 1984, que d'autres textes citent seulement ; l'ancien code de la sécurité sociale,
d'avant la codification du 21 décembre 1985 (aucun article de l'indemnité journalière de
repos ; `--num L298` ne rend que deux autres codes).

## 2. Le congé de maternité du fonctionnaire : le statut, qui renvoie à la sécurité sociale

Le congé de maternité du fonctionnaire relève de son statut, qui le donne « avec
traitement » et en fixe la durée par renvoi : « égale à celle prévue par la législation
sur la sécurité sociale » — l'article 34, 5°, de la loi n° 84-16 pour l'État, l'article
57, 5°, de la loi n° 84-53 et l'article 41, 5°, de la loi n° 86-33 pour la CNRACL,
l'article 4 du décret n° 72-154 pour les ouvriers de l'État, dès le 20 décembre 1976. R. 13,
1°, a, nomme les uns et les autres. La durée est donc celle de L. 331-3 à L. 331-5, et la
conclusion de M4-bis ne change pas : aux rédactions lues, le congé n'atteint jamais une
année. De 1985 à 1994, trente semaines au plus (huit avant et vingt-deux après, quand des
naissances multiples portent les enfants à trois), trente-deux avec L. 331-5 ; depuis
1994, quarante-six (plus de deux enfants), quarante-huit avec L. 331-5. Seul l'allongement
d'une naissance très prématurée, depuis le 20 décembre 2005, n'a pas de borne écrite, ce
que M4-bis déclare. Pour la salariée, au code du travail, quatorze semaines jusqu'au 30
septembre 1978, vingt au plus avec un état pathologique ; seize ensuite, vingt-quatre au
plus avec l'état pathologique et des naissances multiples. Les « seize à quarante-six
semaines » de M4-bis valent depuis le 1er octobre 1978, non pour les naissances
d'avant : quatorze ; la conclusion n'en dépend pas.

## 3. Les valeurs, refaites à la main

La fonctionnaire de l'État née le 15 mars 1955, en service de 1973 à 1977 et de 2003 à
2019, enfants d'avril 1978, juin 1980 et juin 1982, effet le 1er avril 2020 (65 ans et 17
jours) ; un calcul à part, qui n'appelle pas le modèle, sur les textes du point 1.

| Cas | Calcul | Attendu du test | Constat |
|---|---|---|---|
| un an de maternité, 1978 | aucune année « élever un enfant » dans les fenêtres 1978-1980, 1980-1982, 1982-1984 : pas de borne ; 62 ans le 15 mars 2017, « Limite d'âge moins 3 trimestres » de 67 ans : 67 − 0,75 | 66,25 | conforme |
| maternité en 1978, puis un an à élever un enfant | 1979 « élever un enfant », dans 1978-1980 : une année ; 1976 et 1977, 8 trimestres ; l'emploi avant 1979, 1973 à 1977, 20 trimestres | 65 | conforme |
| de bout en bout, État, un an de maternité, 65 ans | annulation à 66 ans et 3 mois, le 15 juin 2021 ; du 1er avril 2020, 14,47 mois, 4,82 trimestres, « arrondi à l'entier supérieur » : 5 ; la durée en manque bien plus ; 75 % × (1 − 5 × 1,25 %) | 70,3125 % | conforme |
| effet de 1954, née de janvier à mai | 61 ans et 7 mois d'août à décembre 2015, « moins 5 trimestres » de 66 ans et 7 mois (65 ans + 4 + 5 + 5 + 5 mois) : 65 ans et 4 mois ; effet le 1er du mois qui suit les 65 ans, 3,47 mois, 1,16 trimestre : 2 ; 75 % × (1 − 2 × 1,25 %) | 2, 73,125 % (fiche) | conforme |
| effet de 1954, née de juin à décembre | 61 ans et 7 mois de janvier à juillet 2016, « moins 4 trimestres » : 65 ans et 7 mois ; 6,47 mois, 2,16 : 3 ; 72,1875 % | 3, 72,1875 % (fiche) | conforme |

Les bornes du mois ont été refaites pour chaque mois extrême (janvier, mai, juin, décembre
1954 ; mars et décembre 1955). La note de M4-bis compte « 4 mois, 1,33 trimestre » pour les
nées de janvier à mai, de soixante-cinq ans juste ; de l'effet au 1er du mois suivant, 3,47
mois : le même arrondi, 2. Que la décote ôtée soit de 2, 3 ou 5 trimestres « au plus » est
juste : L. 14, I, prend le plus petit des deux nombres.

## 4. Les deux moteurs, et ce que le texte ne tranche pas

Les tests, dans l'arbre de la session au commit 9367bc6, qui contient badc7bf :
`tests/test_taux_plein_a_soixante_cinq_ans.py` et `tests/test_regle_de_chacun.py`, 22
passés ; `python -m pytest -m rapide`, 4 344 passés, 13 rouges, tous de
`test_pages_en_dossier.py`, les pages toutes faites que GitHub refait ; sous
`PRESOMPTIONS_DECALEES=1`, 4 145 passés, les mêmes 13 ; les fichiers qui lisent la fiche,
la limite, les règles ou le paquet, avec les confrontations légères
(`test_agirc_arrco_au_droit.py`, `test_carte.py`, `test_reversion.py`, `test_prose.py`,
`test_donnees.py`, `test_referents.py`, `test_jumeaux.py`, `test_oracle.py`,
`test_destinie.py`, `test_estimation_officielle.py`, `test_verification.py`), 1 219
passés, deux rouges attendus (le tableau de bord et `docs/chiffrage_plf.csv`, périmés dès
que `main` bouge). `python scripts/construire_donnees.py`, puis `git status` : rien ne
change, le paquet est celui du commit, à l'octet. Le portage
(`remplitPourLEnfantFonctionnaire`) et son jumeau lisent les motifs dans la fiche, qui ne
porte plus que `education_enfant` : la règle des deux moteurs n'a pas eu à changer.

Ce que le texte ne tranche pas est déclaré, là où un lecteur le voit :

- *L'AVPF.* La fiche le dit dans l'approximation des fonctionnaires (« elle ne prouve pas
  le cadre de R. 13, que le modèle présume ») et son effet (« une année d'AVPF sans congé
  ni disponibilité, a la borne que le droit ne lui donne pas »), la limite aussi
  (`docs/limites/ecarts-au-droit-positif.md` : « présumée prise dans un congé ou une
  disponibilité, ce qu'elle ne prouve pas »). Conforme ; le point 1 confirme qu'aucune
  rédaction de L. 381-1 ne demande un congé ni une disponibilité.
- *Les neuf ans de L. 18, III* : non tranchés, déclarés en nommant L. 18, III ; l'article 28,
  III, ne renvoie qu'au II, et l'article 20, IV, 1°, dit « Avoir eu ou élevé ». Conforme.
- *L'année continue, les deux mois de R. 13, 1°, l'allongement d'une naissance très
  prématurée* : déclarés. Conforme.
- *L'année « élever un enfant » de sept mois.* La saisie donne à une année le motif d'une
  période sans emploi qui en occupe plus de la moitié des mois (`anneesCreuses`,
  `moteur/js/saisie.js` : `occupes * 2 > portee`) ; déclaré dans la fiche, son effet, la
  limite et l'« à relire ». Conforme.
- *Le statut d'avant 1984* : absent de l'index, confirmé (point 1), et déclaré ; mais voir
  l'écart 1.

## 5. Les écarts de R-M4

a. **Moyen, corrigé.** `maternite` a quitté `fonctionnaires.interruptions` dans la fiche et
   dans le paquet, d'une ligne ; le cas « un an de maternité, 1978 » attend 66,25 ; le cas
   « maternité en 1978, puis un an à élever un enfant » et le cas de bout en bout ajoutés
   (point 3) ; l'approximation et la limite disent qu'un congé de maternité suivi d'un
   congé parental ou d'une disponibilité se dit « élever un enfant ». R-M4 proposait de ne
   compter la maternité qu'avec une année « élever un enfant » : M4-bis l'écarte, avec
   raison, la saisie ne disant que des années entières et une seule année « élever un
   enfant » suffisant déjà.
b. **Faible, corrigé.** L'effet général dit 2 trimestres au plus de janvier à mai 1954, 3 de
   juin à décembre, 5 en 1955, avec « arrondi à l'entier supérieur » ; l'effet de
   l'approximation ajoute le cas de janvier à mai, 73,125 % (point 3).
c. **Faible, corrigé.** L'AVPF d'un relevé : présumée, déclarée (point 4).
d. **Faible, corrigé.** Les neuf ans : déclarés non tranchés, L. 18, III nommé (point 4).
e. **Faible, corrigé.** L. 14, I, cité aux deux rédactions en vigueur aux dates d'effet,
   avec « arrondi à l'entier supérieur » (point 1).

## 6. Les écarts de cette relecture

1. **Faible, de forme** — « seize semaines en 1978 ». L'approximation des fonctionnaires
   dit « seize en 1978, au code du travail, L. 122-26 » et cite LEGIARTI000006646774 ; le
   commentaire de tête du test, « en 1978, seize semaines au code du travail, L. 122-26,
   LEGIARTI000006646774 », et celui du cas, « seize semaines en 1978 (L. 122-26) ». Cette
   rédaction n'entre en vigueur que le 1er octobre 1978 ; l'enfant du cas naît en avril
   1978, sous LEGIARTI000006646773 : « six semaines avant la date présumée de
   l'accouchement et se termine huit semaines après », « quatorze semaines de suspension ».
   Et c'est le congé de la salariée : l'entrée du texte dit que le statut des
   fonctionnaires d'alors n'est pas dans l'index, l'approximation ne le dit pas. La note de
   M4-bis est exacte (« quatorze puis seize en tout »). De même, l'entrée de L. 331-4 de
   2006 dit « les vingt-six semaines dès la rédaction du 26 juillet 1994 » : la rédaction
   de 1985 (LEGIARTI000006742546) les donne déjà (« vingt-six ou de vingt-huit
   semaines »), seule la phrase citée date de 1994. Sans effet : quatorze semaines, vingt au
   plus, restent loin d'une année. À dire : « quatorze, puis seize dès le 1er octobre 1978,
   pour la salariée », LEGIARTI000006646773 cité avec l'autre.
2. **Faible** — la durée du congé n'est prouvée que pour l'État. L'approximation nomme
   « pour le fonctionnaire de l'État, l'article 34, 5°, de la loi n° 84-16 » ; la règle sert
   aussi la CNRACL et les ouvriers de l'État, dont les statuts disent la même chose (point
   2) : loi n° 84-53, article 57, 5° (LEGIARTI000006366816), loi n° 86-33, article 41, 5°
   (LEGIARTI000006695883), décret n° 72-154, article 4 (LEGIARTI000006769789,
   LEGIARTI000006769790). La conclusion tient ; la preuve écrite manque à la fiche pour
   deux des trois régimes. À ajouter à ses textes, chacun par son identifiant.

## Ce qui reste

À une file du modèle, sans test à changer qu'un commentaire : les écarts 1 et 2, dans la
fiche et les deux commentaires du test. Non lus, faute d'être dans l'index : l'ordonnance
n° 59-244, qui fixait le congé du fonctionnaire avant 1984, et l'ancien code de la sécurité
sociale, auquel les statuts renvoyaient avant le 21 décembre 1985 (dès 1976 pour
l'ouvrière de l'État) ; M4-bis ne déclare que le premier. Pour le propriétaire, aucune
question : les textes lus tranchent l'écart moyen.
