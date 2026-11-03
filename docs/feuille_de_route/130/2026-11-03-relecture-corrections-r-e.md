# Relecture des corrections de R-E, et trois écarts de la CNAVPL

File R-E-bis, le 3 novembre 2026 : relecture indépendante du commit 471a14b (file E-bis, note
`2026-11-03-corrections-de-la-relecture-r-e.md`), qui corrige, d'après la relecture R-E
(4b8a756, note `2026-11-03-relecture-minorations-cavec-et-carpv.md`), les fiches
`cavec_minoration_age_seul` et `carpv_minoration_age_seul` du dixième lot (9020e7b) et le bloc
« Reprise » de l'action 130 ; puis les trois écarts de la CNAVPL que E-bis laisse à une file
du modèle, établis ici sans rien reprendre de E-bis. Chaque texte a été rouvert dans les index
JORF et LEGI récupérés par `dila_index.py --recuperer`, puis mis à jour de l'incrément
`20261103-214151` ; chaque essai, fait dans les deux moteurs, par `servi_et_refait`
(`tests/outils_pont.py`), qui lève à la moindre différence entre le portage et le moteur
Python, et au portage seul pour lire le motif d'une ligne et l'âge opposé. Rien n'a été
modifié : ni règle, ni donnée, ni fiche, ni test.

**Verdict : les corrections de E-bis sont conformes à la source** — citations mot pour mot,
dates d'effet, les six versions de la CARPV, les montants de la réversion, le bloc
« Reprise ». **Un écart moyen** : le décret de l'âge du IV de L. 643-3, que E-bis dit absent
de l'index, y est (D. 643-14, qui renvoie à D. 351-1-14 : soixante-deux ans), et l'écart de
l'inapte de la CNAVPL en est plus large qu'elle ne l'écrit (point 3, b). **Un écart faible** :
deux arrondis d'un centime dans les calculs écrits (point 2). **Les trois écarts de la
CNAVPL sont réels, dans les deux moteurs, et la cause du troisième est trouvée** : la
liquidation d'une carrière sans régime en annuités prend le plus bas des âges de ses régimes en
points, et la CARPV, la CAVEC et l'ASV des directeurs de laboratoire ouvrent à 60 ans.

## 1. Les sources, rouvertes

### La CARPV

| Ce que la fiche ou la note cite | Texte rouvert | Verdict |
|---|---|---|
| Arrêté du 11 janvier 2011, annexe, article 21, sixième alinéa | JORFARTI000023448554, publié le 19 janvier 2011 | mot pour mot |
| Ses articles 1er à 3 | JORFARTI000023448550 à 552 | aucune date : en vigueur le 20 janvier 2011 |
| Arrêté du 16 avril 2014, annexe, II, a) et h) | JORFARTI000028939421, publié le 17 mai 2014 | mot pour mot |
| Ses articles 1er et 2 | JORFARTI000028939418 et 419 | aucune date : le 18 mai 2014 |
| Arrêté du 2 novembre 2015, annexe, I, 3° | JORFARTI000031549970, publié le 1er décembre 2015 | mot pour mot |
| Ses articles 1er et 2 | JORFARTI000031549967 et 968 | aucune date : le 2 décembre 2015 |
| Statuts de 2021, articles 33, 34 et 38 à 41 | JORFARTI000044220745, publié le 19 octobre 2021 | mot pour mot |
| Arrêté du 18 octobre 2021, article 2 | JORFARTI000044220741 | « entrent en vigueur le 1er janvier 2022 » |
| Règlement de 2026, articles 1er, 2 et 6 à 9 | JORFARTI000054436031, publié le 17 juillet 2026 ; LEGIARTI000054437680, en vigueur le 18 | mot pour mot |
| Arrêté du 10 juillet 2026, article 1er | JORFARTI000054436028 | aucune date |
| Titres des arrêtés de 1960, 1968, 1970, 1977 | JORFTEXT000000803770, 437434, 483025, 489267 | conformes |

La chaîne de l'alinéa de l'inapte tient, et une lettre de l'arrêté de 2014 la confirme : son
a) abroge l'article 14 dans l'ancienne numérotation, et son i) modifie pourtant « l'article
14 », où il remplace « article 21 » par « article 13 » ; les lettres qui suivent le a)
parlent donc la numérotation nouvelle, et « l'article 13 » du h) est l'ancien article 21. Le
h) supprime ses quatrième et cinquième alinéas et récrit le renvoi de son sixième, « article
23 », celui de la retraite progressive, que seul l'alinéa de l'inapte porte (texte de 2011) ;
le 3° de 2015 vise ensuite « le quatrième alinéa de l'article 13 ». La rectification de E-bis
sur les titres est juste : celui de 1960 vise les « ART. 10, 16 ET 21 DU TITRE II […] RELATIFS
AU REGIME COMPLEMENTAIRE D'ASSURANCE VIEILLESSE » ; celui de 1968, les articles « 9, 17, 21, 23,
24, 32 & 34 » des statuts relatifs « AUX REGIMES D'ASSURANCE VIEILLESSE COMPLEMENTAIRE ET AU
REGIME D'ASSURANCE INVALIDITE DECES », sans titre ; celui de 1970, les articles « 15, 17, 18, 19,
21 & 25 » des statuts « RELATIFS AU REGIME D'ASSURANCE INVALIDITE DECES » ; celui de 1977, des
articles sans régime nommé.

### La CAVEC

| Ce que la fiche ou la note cite | Texte rouvert | Verdict |
|---|---|---|
| Statuts de 2008, articles 3.13 et 3.15 à 3.18 | JORFARTI000018197778, publié le 1er mars 2008 | mot pour mot |
| Arrêté du 22 février 2008, articles 1er et 2 | JORFARTI000018197775 et 776 | aucune date : le 2 mars 2008 |
| Statuts de 2018, partie 2, articles 12, 15 et 16 | JORFARTI000037363871, publié le 4 septembre 2018 | mot pour mot |
| Arrêté du 20 août 2018, articles 1er et 2 | JORFARTI000037363868 et 869 | aucune date |
| Arrêté du 19 juin 2019, annexe, II, 7° | JORFARTI000038689131, publié le 27 juin 2019 | mot pour mot |
| Ses articles 1er et 2 | JORFARTI000038689128 et 129 | aucune date |
| Arrêté du 2 juillet 2024, annexe, II | JORFARTI000049880543 | articles 3, 5, 10, 14, 15 (forme de la demande) et 17 ; ni 12 ni 16 |
| Règlement de 2026, articles 1.1.3, 1.2.1 et 1.2.2 | JORFARTI000054435943, publié le 17 juillet 2026 ; LEGIARTI000054437585, en vigueur le 18 | mot pour mot |
| Arrêté du 10 juillet 2026, article 1er | JORFARTI000054435940 | aucune date |
| Décret n° 53-506 du 21 mai 1953 | JORFTEXT000000670150 | l'analyse citée est exacte |
| Arrêté du 23 mai 1953 | JORFTEXT000000472264, publié le 6 juin 1953 | le titre cité est exact |
| Le livre des 70 ans de la caisse | retéléchargé ici : 80 564 762 octets, sha256 f37b161d…d030, le même | page 15 : « (comme annoncé pour le régime général par Pierre Mauroy en 1982). Il reste et restera fixé à 65 ans. » |

### Le code de la sécurité sociale (LEGI)

- **L. 643-3, I**, première phrase, à ses cinq rédactions de 2004 au 31 août 2023
  (LEGIARTI000006743789, 019959477, 023035054, 025014529, 028498667), puis de 2023
  (LEGIARTI000047453031) et de 2026 (LEGIARTI000053280388) : « La liquidation de la pension
  prévue à l'article L. 643-1 peut être demandée à partir de l'âge prévu au premier alinéa de
  l'article L. 351-1 ». Conforme. Le IV (« La condition d'âge prévue au premier alinéa du I du
  présent article est abaissée, dans des conditions fixées par décret, pour les assurés
  relevant des 2° et 3° de l'article L. 643-4 ») est déjà dans la rédaction de 2023, pour les
  pensions qui prennent effet depuis le 1er septembre 2023 ; E-bis cite celle de 2026, qui
  vaut pour son essai de 2028 : exact.
- **L. 643-4** : rédactions du 19 décembre 2008 (LEGIARTI000019959512) et de 2023
  (LEGIARTI000047453026), citations exactes.
- **L. 161-17-2** : « soixante-deux ans pour les assurés nés à compter du 1er janvier 1955 »
  (LEGIARTI000025014605, 2011) ; « 3° Soixante-deux ans et neuf mois, pour les assurés nés
  entre le 1 er janvier 1963 et le 31 mars 1965 » (LEGIARTI000053280889), pour les pensions
  qui prennent effet depuis le 1er septembre 2026 (VI de l'article 105 de la loi
  n° 2025-1403). Conforme.
- **D. 161-2-1-9**, 10° (LEGIARTI000047634502, pensions depuis le 1er septembre 2023) :
  « Soixante-trois ans pour les assurés nés en 1964 ». Conforme.
- **L. 351-1** (LEGIARTI000023035688) : « à partir de l'âge mentionné à l'article
  L. 161-17-2 ». L'index date cette rédaction du 11 novembre 2010 ; la note qu'il porte
  (article 118 de la loi n° 2010-1330) l'applique aux pensions qui prennent effet depuis le
  1er juillet 2011 : la date de E-bis est juste.

**Moyen — le décret du IV de L. 643-3 est à l'index.** E-bis l'écrit « que l'index thématique
ne porte pas, cherché » (sa note, « Hors du lot »), et renvoie au Bulletin officiel « le décret
du IV de L. 643-3 » (« Ce que l'étape laisse ») ; son journal de veille le répète (`reste`). Il
y est, trouvé par `dila_cherche.py legi '"IV de l article L. 643-3"'` : **D. 643-14**,
LEGIARTI000047634694, pour les pensions qui prennent effet depuis le 1er septembre 2023
(article 9 du décret n° 2023-436) : « L'âge prévu au IV de l'article L. 643-3 est celui prévu
à l'article D. 351-1-14. » Et **D. 351-1-14** (LEGIARTI000047634688, puis LEGIARTI000053355951
depuis le 1er janvier 2026, même phrase) : « L'âge prévu au premier alinéa de l'article
L. 351-1 est abaissé, en application de l'article L. 351-1-5, à soixante-deux ans pour les
assurés reconnus inaptes au travail dans les conditions prévues à l'article L. 351-7 ». Le
registre du dépôt porte déjà D. 643-14 (`data/reference/textes/redactions.csv`, ligne 2774).
Aucun chiffre servi n'en dépend ; mais une session irait le chercher au Bulletin officiel, et
l'écart de l'inapte de la CNAVPL est plus large que ne l'écrit E-bis : depuis le 1er septembre
2023, l'inapte part à 62 ans, et au taux plein dès cet âge (point 3, b).

## 2. Les montants, refaits à la main

- **CARPV, 12 286,79 €.** Le modèle sert 17 406,289 € au coefficient 0,85 ; sans lui,
  17 406,289 / 0,85 = 20 477,987 € ; 60 % = 12 286,79 €. Conforme. Le coefficient : du
  1er mars 2026 au 10 février 2029, ses 65 ans, 2 ans, 11 mois et 9 jours, 12 trimestres
  entamés, 12 × 1,25 % = 15 %. Les conditions : mort en juin 2027, à 63 ans, avant ses
  65 ans (règlement de 2026, article 9 : « sans minoration ») ; conjoint de 65 ans, marié en
  1988 (article 6).
- **CAVEC, 16 245 à 19 494 €.** 27 616,836 / 0,85 = 32 490,395 € ; 50 % = 16 245,20 € ;
  60 % = 19 494,24 €. Conforme, sans le coefficient à tout décès (article 1.2.2 de 2026).
- **CNAVPL, 1 833,36 €.** Le modèle sert à l'inapte, à 64 ans en mars 2028, 10 389,0488 € au
  coefficient 0,85 ; sans lui, 12 222,410 € ; 15 % = 1 833,36 €. La perte est juste.

**Faible — deux arrondis d'un centime.** La note écrit « 17 889,98 points × 0,683199 € =
12 222,42 € », sur les points arrondis, puis « 12 222,42 − 10 389,05 = 1 833,36 € » : la
soustraction écrite donne 1 833,37 €. De même, « 15 641,60 points × 0,6399 € × 0,75 =
7 506,79 € », quand le modèle sert 7 506,80 € (7 506,796, sur ses points non arrondis). Aucune
conclusion n'en change.

## 3. Les trois écarts de la CNAVPL

### a) La réversion : servie nulle part, au scénario 1, dans aucun moteur — confirmé

**Le code.** `Reversions` range chaque régime sous la fiche de réversion qui le nomme dans
`regimes` (`src/retraite_notionnelle/scenarios/actuel.py:1499-1512`,
`moteur/js/regimes.js:1506-1521`). Les dix fiches lues (`reversion.yaml`, les huit
`reversion_*.yaml`, `majoration_forfaitaire_reversion.yaml`) nomment le régime général, la MSA
salariés, l'Organic, la Cancava, le RSI, les assurances sociales, l'Agirc-Arrco et ses régimes,
la fonction publique, la CNRACL, le RAFP, l'Ircantec, la RCI, la CRPCEN, les IEG et la SNCF :
ni la CNAVPL, ni une section, ni une ASV. `fiche_du_regime` rend alors `None`, et la ligne
vaut zéro, motif `non_portee` (`src/retraite_notionnelle/droit/reversion.py:1818-1821`,
`moteur/js/droit/reversion.js:1681-1686`).

**L'essai.** Les quatorze statuts que la CNAVPL couvre (`data/reference/regimes/cnavpl.yaml`,
`statuts`), nés le 10 février 1964, au travail depuis 26 ans à deux fois le salaire moyen,
partis à 62 ans le 1er mars 2026, morts en juin 2027, conjoint né en 1962, marié en juin
1988 : le portage sert 0 €, motif `non_portee`, à la CNAVPL, aux dix sections (Cipav, CARPIMKO,
CAVP, CAVEC, CAVAMAC, CPRN, CARPV, CAVOM, CARCDSF, CARMF) et aux cinq ASV ; le moteur Python
rend la même ligne, motif `non_portee`, au vétérinaire et à l'expert-comptable ; `servi_et_refait`
confirme les mêmes montants dans les deux moteurs.

**La loi.** L. 643-7 (LEGIARTI000019959385, en vigueur depuis le 1er janvier 2010) : « En cas
de décès de l'assuré, son conjoint survivant a droit à une pension de réversion dans les
conditions prévues aux articles L. 353-1, L. 353-2, L. 353-3 et L353-6. » Les statuts de la
CAVEC et de la CARPV servent la leur (point 1). Le conjoint d'un libéral ne reçoit donc, dans
le modèle, ni la réversion de sa base ni celle de sa complémentaire. Ce que E-bis en écrit, et
la limite (`docs/limites/ecarts-au-droit-positif.md`, la réversion : « la CNAVPL et ses
sections libérales parmi eux, dont la ligne le dit, qui vaut zéro »), est conforme.

### b) L'inapte minoré, contre L. 643-4, 2°, a — confirmé, et plus large

**Le code.** La fiche `inaptitude_au_travail` nomme `regime_general, msa_salaries, cancava,
organic, rsi, assurances_sociales`, et non la CNAVPL ; aucune fiche ne lit L. 643-4 pour la
base (seules les fiches de la CAVEC et de la CARPV le citent, pour leurs sections), ni
D. 643-14.

**La loi, de 2015 à 2028.** Jusqu'au 31 août 2023, L. 643-4 (LEGIARTI000019959512) liquide
« sans coefficient de réduction » la pension des assurés « ayant atteint l'âge prévu au premier
alinéa du I de l'article L. 643-3 » et « a) Reconnus inaptes au travail dans les conditions
prévues à l'article L. 643-5 » : à l'âge légal, 62 ans pour les générations nées depuis 1955.
Depuis le 1er septembre 2023 (LEGIARTI000047453026), à « l'âge prévu au IV de l'article
L. 643-3 », que D. 643-14 fixe à celui de D. 351-1-14 : 62 ans ; le IV abaisse aussi à cet âge
l'ouverture de la base. L. 643-5 (LEGIARTI000006743795) dit l'inaptitude : n'être « plus en
mesure d'exercer […] une activité professionnelle ».

**Les essais**, dans les deux moteurs : un vétérinaire né le 10 février, au travail depuis
26 ans à deux fois le salaire moyen, `inaptitude: oui` puis sans. La CNAVPL est la même, au
même coefficient, avec ou sans inaptitude, à chaque date :

| Génération, départ | CNAVPL servie | Coefficient | La loi | Perte par an |
|---|---|---|---|---|
| 1956, 62 ans, mars 2018 | 6 674,06 € | 0,75 | sans coefficient (2008) | 2 224,69 € |
| 1961, 62 ans, mars 2023 | 7 442,49 € | 0,75 | sans coefficient (2008) | 2 480,83 € |
| 1964, 62 ans, mars 2026 | 8 291,06 € | 0,75 | sans coefficient (2023, D. 643-14) | 2 763,69 € |
| 1964, 64 ans, mars 2028 | 10 389,05 € | 0,85 | sans coefficient (2023) | 1 833,36 € |

Et le libéral de la Cipav (`profession_liberale`), inapte, né le 10 février 1964 : le modèle
lui refuse la liquidation à 62 ans (âge opposé 62,75, motif `non_ouverte`), puis le minore à
62 ans et 9 mois (coefficient 0,7875) ; la loi l'ouvre à 62 ans, au taux plein. L'inapte de la
CNAVPL perd donc la minoration de toute la base, et, depuis le 1er septembre 2023, les mois
qui séparent ses 62 ans de l'âge légal.

### c) L'âge d'ouverture de la base, générations 1961 à 1968

**Ce que la loi fixe.** L. 643-3, I, ouvre la base « à partir de l'âge prévu au premier alinéa
de l'article L. 351-1 », celui de L. 161-17-2. Pour les pensions qui prennent effet depuis le
1er septembre 2026, L. 161-17-2 (LEGIARTI000053280889) ; avant, D. 161-2-1-9
(LEGIARTI000047634502) sous L. 161-17-2 de 2023, et L. 161-17-2 de 2011 pour les nés avant le
1er septembre 1961. Les deux tables ne diffèrent qu'à partir de la génération 1964, qui
n'atteint son âge qu'après le 1er septembre 2026 : à l'âge légal, la table de 2026 s'applique
seule.

**Ce que le modèle sert**, au départ demandé à 60 ans, dans les deux moteurs
(`servi_et_refait`) : au vétérinaire et à l'expert-comptable, liquidation ouverte, motif
`age_legal`, la CNAVPL servie, l'âge opposé 60 ; au libéral de la Cipav, refusée
(`non_ouverte`), à l'âge de sa génération.

| Naissance | Âge légal (texte) | Vétérinaire, expert-comptable | Libéral de la Cipav |
|---|---|---|---|
| 10 février 1961 | 62 ans (L. 161-17-2 de 2011 ; D. 161-2-1-9, 6°) | 60 | 62 |
| 10 octobre 1961 | 62 ans et 3 mois (7° ; 1° de 2026) | 60 | 62,25 |
| 1962 | 62 ans et 6 mois (8° ; 2°) | 60 | 62,5 |
| 1963 | 62 ans et 9 mois (9° ; 3°) | 60 | 62,75 |
| 1964 | 62 ans et 9 mois (3° de 2026 ; 63 ans, 10°, avant le 1er septembre 2026) | 60 | 62,75 |
| 10 février 1965 | 62 ans et 9 mois (3°) | 60 | 62,75 |
| 10 juin 1965 | 63 ans (4°) | 60 | 63 |
| 1966 | 63 ans et 3 mois (5°) | 60 | 63,25 |
| 1967 | 63 ans et 6 mois (6°) | 60 | 63,5 |
| 1968 | 63 ans et 9 mois (7°) | 60 | 63,75 |

Le vétérinaire né en 1955 et l'expert-comptable né en 1958 sont aussi ouverts à 60 ans, quand
la loi dit 62 ans ; et tous deux, nés en 1969, quand elle dit 64 ans. La table des âges de la CNAVPL est
juste : le libéral de la Cipav reçoit, génération par génération, l'âge du texte.

**La cause.** `ouvrir` (`src/retraite_notionnelle/droit/ouvrir.py:258-290`,
`moteur/js/droit/ouvrir.js:166-200`) cherche l'âge d'ouverture parmi les régimes en annuités,
puis, s'il n'y en a aucun, parmi les régimes en points, sauf l'Agirc-Arrco, l'Ircantec et les
complémentaires qui ont une table d'âges (`age_table`, ligne 273 du Python, 183 du
JavaScript) ; il prend le plus bas des âges retenus. Les périodes de `carpv_complementaire` et
de `cavec_complementaire` portent `age_ouverture: 60` sans `age_table`
(`data/reference/regimes/carpv_complementaire.yaml`, lignes 49, 76, 104, 130, 157, 183, 212,
238…) : elles entrent dans le minimum, et 60 l'emporte sur l'âge de la CNAVPL. Les âges de
chaque régime, lus au moteur Python (`age_ouverture`) : CARPV et CAVEC 60 à toute génération,
CNAVPL 62, 62,75 et 63,75 aux générations 1961, 1964 et 1968. Le même minimum date les
carrières types (`age_ouverture_droit`, `ouvrir.py:1114-1150`, par `sans_ages_propres`,
1153-1169) : 60 ans au vétérinaire et à l'expert-comptable.

**Un troisième statut, de la même cause.** Des quatorze statuts que la CNAVPL couvre, essayés
un à un, onze reçoivent l'âge de la CNAVPL ; le biologiste libéral, non : l'ASV des directeurs
de laboratoire porte `age_ouverture: 60` sans table
(`data/reference/regimes/asv_directeurs_laboratoire.yaml`, lignes 59, 92, 120, 145…), et le
modèle l'ouvre à 60 ans, motif `age_legal`, aux générations 1961, 1964 et 1968, dans les deux
moteurs, et lui sert dès cet âge la CNAVPL et la CAVP, quand la CAVP a sa table (62,75 à la
génération 1964). Ce que la loi fixe à l'ASV elle-même n'a pas été lu ici.

**L'effet, sur un cas.** Le vétérinaire né le 10 février 1964, départ demandé à 60 ans, le
1er mars 2024 : le modèle ouvre la liquidation « à l'âge légal » et sert la CNAVPL,
7 506,80 € par an, avec la CARPV, 14 280,87 €, soit 21 787,67 €. La CARPV est due à 60 ans
(statuts de 2021, article 34 : « dès leur soixantième anniversaire », sous la seule condition
des cotisations de l'article 33) ; la base, non : 63 ans pour une pension qui prend effet en
2024 (D. 161-2-1-9, 10°), 62 ans et 9 mois depuis le 1er septembre 2026, le 10 novembre 2026.
Pendant 32 mois au moins, le modèle sert 7 506,80 € par an de trop, 34,5 % de ce qu'il
affiche : 20 018 € sur ces 32 mois, aux montants de 2024.

## 4. Les tests

- `python -m pytest tests/test_sections_liberales.py tests/test_carte.py` : 61 passés.
- `python -m pytest -m rapide` : 4 346 passés, 6 sautés, 13 rouges, tous
  `tests/test_pages_en_dossier.py` (les pages toutes faites, périmées dès que `main` bouge).
- `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide` : 4 147 passés, 205 sautés, les mêmes
  13 rouges.
- `python scripts/construire_donnees.py`, puis `git status` : rien ne change.
- La carte : `carte.manques()` rend 85 fiches et 503 manques, aucun aux deux fiches.

Le test neuf, `test_chaque_version_nait_d_un_texte_a_sa_date_du_journal_officiel`, tient
chaque naissance à une table de publications et d'entrées en vigueur ; chacune a été relue ici à
l'index (point 1) : ses valeurs viennent du texte, et non de la fiche. La faiblesse que R-E
relevait au second test neuf de E est levée.

## 5. Le bloc « Reprise » de l'action 130

Comparé à celui d'avant 9020e7b (`git show 9020e7b^:docs/feuille_de_route.md`) :

- revenu : « Au propriétaire, README muet : la décision de la proposition, septième étape du
  sixième domaine, et la retraite progressive, le cumul et la seconde pension » ;
- renvoyés à la note des décisions, et bien dedans : la grille des marins d'avant 2008
  (question 3) et la garantie des cultes de 2002 au 30 juin 2005 (question 7) ;
- mis à jour, non perdus : les relectures des cultes et de l'Agirc-Arrco, dites faites ;
  l'Ircantec d'avant 1983, sous sa décision 9 ; 85 fiches et 503 manques, que la carte rend ;
  le lot suivant, la CAVAMAC ou la CARCDSF ; le détail, la note de E-bis.

Rien d'autre ne s'est perdu ; le bloc tient en dix lignes. Le renvoi que E-bis ajoute à la fin
de la note de E n'en efface rien.

## Ce que la relecture laisse

À l'orchestration, pour le propriétaire, sans rien en corriger ici : (a) la réversion de la
CNAVPL, de ses dix sections et de ses ASV, servie nulle part ; (b) l'inapte de la CNAVPL,
minoré à toute date, et refusé à 62 ans depuis le 1er septembre 2023 (D. 643-14) ; (c) la base
ouverte à 60 ans au vétérinaire, à l'expert-comptable et au biologiste libéral, par le minimum
des âges de `ouvrir`.
