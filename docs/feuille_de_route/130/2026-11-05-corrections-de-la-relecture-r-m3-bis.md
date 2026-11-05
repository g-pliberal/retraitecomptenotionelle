# Corrections de la relecture R-M3-bis : le 6° a) jusqu'au 31 décembre 2003 (file M3-ter)

File M3-ter, le 5 novembre 2026, sur Opus : les quatre écarts de la relecture R-M3-bis
(`2026-11-05-relecture-corrections-r-m3d.md`, points 1, 5, 6 et 7) sur l'Ircantec,
l'IPACTE et l'IGRANTE. Chaque texte a été rouvert pendant la session, dans l'index de la
DILA récupéré de la release (LEGI à jour de l'incrément du 2 novembre 2026,
20261102-213929 ; JORF du 3 novembre, 20261103-002311), par `scripts/fetch/dila_cherche.py`.

## 1. Le 6° a) après le 31 mars 1983 (écart moyen) : la lettre, servie

**Ce que la caisse en a fait : rien de trouvé.** Recherche faite une fois, dans le JORF
de 1983 à 2004 : `ircantec AND (circulaire OR instruction)`, `ircantec AND coefficient
AND (reduction OR abattement OR anticipation)`, `"non titulaires" AND "63 ans"`,
`"article 9" AND "26 mars 1982" AND ircantec`. Seules en sortent les analyses déjà citées
des arrêtés du 27 janvier 1983 (JORFTEXT000000654120) et du 26 juillet 1983
(JORFTEXT000000837384), et des textes sans rapport (organisation de bureaux, circulaire
du 23 janvier 1997 sur le congé de fin d'activité). LEGI ne porte pas de circulaire de
la caisse ; le dépôt (`data/sources.yaml`, `data/sources_a_explorer.yaml`,
`data/reference/legislation/`) n'en nomme aucune sur le 6° a). Aucune pratique
documentée, donc : la lettre.

**La lettre.** « 6° a) A compter du 1er juillet 1982 aux agents visés aux articles
L. 351-16 et L. 351-17 du code du travail remplissant les conditions fixées par l'article
9, alinéa 2, de l'ordonnance du 26 mars 1982 susvisée », mot pour mot dans les rédactions
du 31 août 1983 (LEGIARTI000006381610, jusqu'au 2 octobre 1990) et du 2 octobre 1990
(LEGIARTI000006381611, jusqu'au 1er janvier 2004), relues ici. Celle du 1er janvier 2004
(LEGIARTI000006381612) le récrit : « 6° a) Aux agents et anciens agents admis à faire
liquider leur retraite au régime général en application de l'article L. 351-1-1 ».
L'article 9 de l'ordonnance borne sa troisième phrase, non sa deuxième ; l'article 13 du
décret n° 82-628 est sans terme. Le 6° a) se sert donc du 1er juillet 1982 au
31 décembre 2003.

**Ce qui change.** Dans la fiche `coefficient_anticipation_ircantec`, les versions
`structure_financiere_1983` (1er avril au 31 août 1983) et `escalier_au_trimestre_1983`
(31 août 1983 au 1er janvier 2004) portent désormais
`exoneration_des_agents_de_soixante_trois_ans: {age: 63, trimestres: 150}`, comme
`ordonnance_du_26_mars_1982`. Les deux moteurs lisent ce paramètre dans la version de la
date d'effet (`exonereParLAgeEtLaDuree`, `exonere_par_l_age_et_la_duree`) : aucune ligne
de calcul ne change, seuls les commentaires qui bornaient le 6° a) au 31 mars 1983. La
déclaration « le texte ne tranche pas » est récrite : la lettre est servie ; la lecture
du rapport au Président de la République, qui ferait du 6° a) la seule anticipation de
l'ordonnance, est déclarée **lecture écartée**, un rapport n'étant pas une norme ; ce qui
trancherait est nommé (une circulaire de l'Ircantec de 1983 à 2003, les articles
L. 351-16 et L. 351-17 du code du travail), avec l'effet si la caisse avait lu le
rapport.

**Le test d'abord.** `test_le_6_a_sert_l_agent_de_soixante_trois_ans_jusqu_au_1er_janvier_2004`
(`tests/test_ircantec.py`), vu rouge avant la fiche (le portage servait 0,99 au premier
cas), vert ensuite dans les deux moteurs, aux trois régimes. Agent contractuel depuis
février de ses vingt-cinq ou vingt-six ans, payé deux plafonds ; les âges se comptent du
mois qui suit la naissance (né le 15 janvier : soixante-trois ans en février) ; quatre
trimestres l'année d'entrée et par année pleine.

| Cas | Date d'effet | Calcul posé à la main | Attendu | Avant |
|---|---|---|---|---|
| Né en 1936, dès 25 ans, 63 ans | 1999-02-01 | 1961 à 1998 : 4 + 37 × 4 = 152 ≥ 150 ; agent ; 63 ans ; …611 en vigueur : 6° a) | aucun | 0,99 |
| Né en 1938, dès 26 ans, 64 ans | 2002-02-01 | 1964 à 2001 : 4 + 37 × 4 = 152 ≥ 150 ; 6° a) | aucun | 0,97 |
| Né en 1940, dès 26 ans, 63 ans 10 mois | 2003-12-01 | 1966 à 2002 : 4 + 36 × 4 = 148, et au moins trois trimestres des onze mois de 2003 : ≥ 151 ; 6° a) | aucun | 0,95 |
| Le même, 63 ans 11 mois | 2004-01-01 | …612 : plus de 6° a). 152 trimestres, 160 requis (R. 351-45, I) : 8 manquent ; seconde table à 65 − 8/4 = 63 ans, 0,88 + 4 × 0,01 = 0,92 ; l'âge, 63 ans 11 mois, 7 trimestres écoulés depuis 62 ans, 0,88 + 7 × 0,01 = 0,95, plancher du total | 0,95 | 0,95 |

Les « avant » des deux premiers cas sont ceux que R-M3-bis a mesurés : la seconde table,
à 65 − 1/4 ans, 0,88 + 11 × 0,01 = 0,99 (153 requis en 1936, R. 351-45, II), et à
65 − 3/4 ans, 0,88 + 9 × 0,01 = 0,97 (155 requis en 1938). Les coefficients sont ceux de
l'escalier de l'article 16 (« le coefficient applicable à soixante-deux ans, soit 0,88,
est majoré de 0,01 par trimestre écoulé ») et le plancher, son paragraphe 2 (« le total
des points de retraite ainsi calculé ne pourra être inférieur à celui qui aurait été
obtenu après application du coefficient d'abattement correspondant à l'âge de
l'intéressé »), relus dans …612. La durée de la génération : R. 351-45, rédaction du
10 mai 1995 (LEGIARTI000006749450), « 153 trimestres pour l'assuré né en 1936 ; […]
155 trimestres pour l'assuré né en 1938 », et, au I, « 160 trimestres […] applicable aux
pensions prenant effet postérieurement au 31 décembre 2002, quelle que soit la date de
naissance de l'assuré ».

## 2. L'article 13 du décret n° 82-628 (écart faible) : cité, la durée est la bonne

LEGIARTI000006763435, en vigueur du 23 juillet 1982, sans terme : « La durée d'assurance
dont doivent justifier les personnels visés à l'article 9, deuxième alinéa, de
l'ordonnance du 26 mars 1982 susvisée pour bénéficier, dès le 1er juillet 1982, du taux
plein peut avoir été accomplie dans le régime général ou dans ce régime et un ou
plusieurs autres régimes de base obligatoires. » Il ne fixe pas le nombre : les
150 trimestres sont ceux de l'article 9 (« justifiant d'une durée d'assurance de
150 trimestres »). Il dit les régimes : le régime général, avec les autres régimes de base
obligatoires. Le modèle compare à 150 la durée d'assurance tous régimes de base
(`trimestres`, celle du taux plein), où l'agent non titulaire a toujours du régime
général : c'est la durée qu'il définit, rien à corriger. Il est cité dans la fiche (versions
`ordonnance_du_26_mars_1982` et `escalier_au_trimestre_1983`, et `lit`), comme source
normative de la durée tous régimes, que la fiche ne tenait que du rapport. La
déclaration de la femme de 1977, qui disait le décret absent de l'index, dit désormais
que LEGI a ses articles 8, 9 et 13 à 16 (LEGIARTI000006763432 à 438), mais non celui qui
récrit l'article 70-2. Les articles 14 et 15, relus aussi, sont versés aux déclarations :
le 6° b) demande l'assuré « en situation de chômage constaté à la date d'entrée en
jouissance de [sa] pension » (article 14) ; L. 351-16 et L. 351-17 servent des
« allocations aux travailleurs privés d'emploi » (article 15), et l'agent privé d'emploi
qu'ils indemnisent, que le modèle abat, pourrait être de ces « personnels » — le texte ne
le tranche pas, déclaré avec « qui est agent », étendu aux versions jusqu'en 2003.

## 3. La citation du rapport (écart faible) : l'ordre rétabli

Dans la fiche, les deux morceaux du rapport (LEGIARTI000006759661) sont désormais dans
l'ordre du texte, relu ici : « une durée d'assurance d'au moins 150 trimestres obtenue en
totalisant les périodes cotisées et assimilées dans un ou plusieurs régimes de base quels
qu'ils soient […] elle entrera en vigueur, selon des modalités spécifiques, dès le
1er juillet 1982 pour les agents non titulaires de l'Etat, des collectivités locales, des
établissements et entreprises publiques qui n'ont pas accès actuellement au dispositif de
la garantie de ressources ». La note de M3-bis
(`2026-11-05-corrections-de-la-relecture-r-m3d.md`), récit qui ne se récrit pas, les cite
aussi dans l'ordre inverse, séparés, et dit que le rapport donne « quelle durée compte » ;
c'est inexact sur un point : le passage des 150 trimestres décrit la réforme de tous les
salariés de soixante ans, non ces seuls agents. La durée du 6° a) est celle de l'article 9
de l'ordonnance, ses régimes ceux de l'article 13 du décret n° 82-628.

## 4. Les fiches de l'IPACTE et de l'IGRANTE (écart faible)

Leur note nomme désormais, à côté du 5° et du 6° a) (« que l'article garde jusqu'au
31 décembre 2003 »), le 6° b) : l'ancien agent de soixante ans et de quarante trimestres,
inscrit comme demandeur d'emploi au 1er février 1982 et au chômage à l'entrée en
jouissance de sa pension, du 1er juillet 1982 au 31 mars 1983, que le moteur ne sert pas.

## Ce qui bouge

- **Les témoins** : rien. `construire_temoins.py` puis `resumer_temoins.py` : « 930 témoins
  de simulation, aucun ne bouge depuis HEAD », « 85 rendus de page, aucun ne change ».
- **Le coût** : rien. Le coût agrégé, celui des avantages, la grille et le bilan,
  recalculés sous l'empreinte du modèle changé par `construire_donnees.py`, sont
  identiques à l'octet à ceux du modèle d'avant (`.cache/calculs/`, douze calculs
  comparés par `cmp`) ; `data/derive/agregats.json` ne change pas.
- **Le paquet** : `moteur/donnees.json`, les deux versions de la fiche.
- **La population** : les agents des générations 1934 à 1940, de soixante-trois ou
  soixante-quatre ans, encore en fonction, qui liquident de 1997 à 2003 avec cent
  cinquante trimestres au moins sans la durée de leur génération : jusqu'à huit points de
  coefficient de plus qu'avant (0,92 à un, à soixante-trois ans, en 2003).

## Les tests

`tests/test_ircantec.py` et `tests/test_ircantec_minoration.py` : 66 réussis.
`python -m pytest -m rapide` : 14 échecs, tous de `test_pages_en_dossier` (pages toutes
faites, refaites par GitHub). Sous `PRESOMPTIONS_DECALEES=1` : les mêmes 14. Les fichiers
qui lisent les fiches touchées (`grep -l`), les confrontations légères et
`test_textes.py` : un échec, `test_journal_de_certification_est_lisible` sur
`taux_cotisation_mayotte` (« '2026-11-05' <= '2026-11-03' »), qui échoue déjà sans ce
changement : zone de la file D-bis, non touché.

## Hors du périmètre

Le régime général du modèle ne sert toujours pas le taux plein de l'article 9 de
l'ordonnance à l'agent de soixante-trois ans (transmis par M3-bis) : l'article 13 du
décret n° 82-628 en dit les régimes, à verser à sa fiche.

Sources : LEGI LEGIARTI000006381610, 611, 612 ; LEGIARTI000006275868 ;
LEGIARTI000006759661 ; LEGIARTI000006763435, 436, 437 (décret n° 82-628, articles 13 à
15) ; LEGIARTI000006749450 (R. 351-45). JORF JORFTEXT000000654120, 837384, et les
recherches de circulaires de l'Ircantec de 1983 à 2004, sans résultat.
