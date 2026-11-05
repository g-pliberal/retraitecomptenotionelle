# Relecture des corrections de R-L : la CARPV d'avant 2022, le coefficient des biologistes

File R-L-bis, vague 7, le 5 novembre 2026 : relecture indépendante du commit 9fcd8a1
(file L-bis), de sa note `2026-11-05-corrections-de-la-relecture-r-l.md` et de son journal
de veille, qui corrigent la relecture R-L
(`2026-11-04-relecture-ouverture-de-la-base-des-liberaux.md`). Lecture seule : aucune
règle, aucune donnée, aucun test n'est touché. Chaque texte a été rouvert dans l'index de
la DILA récupéré dans la session (LEGI à jour au 2 novembre 2026, JORF au 3 novembre) ;
chaque valeur, refaite à la main puis servie par le portage et refaite par le moteur
Python (`servi_et_refait`, `tests/outils_pont.py`).

**Verdict : conforme, un écart moyen, un écart faible.** Les citations sont exactes, les
trois valeurs du test justes, les déclarations faites, et la présomption de la CARPV est
la plus prudente des deux lectures. L'écart moyen n'est pas né du commit, mais celui-ci
l'étend aux biologistes : la table écrit 66,17 pour 66 ans et 2 mois, et la génération
1953 reste minorée d'un trimestre au mois exact de son âge du taux plein.

## 1. La CARPV d'avant le 1er janvier 2022 : conforme

**Les citations, rouvertes.** L'arrêté du 18 octobre 2021, article 2 (JORFARTI000044220741) :
« Les modifications des statuts prévues par le présent arrêté entrent en vigueur le
1er janvier 2022 », exact. L'article 34 des statuts de 2021 (JORFARTI000044220745) dit « les
adhérents remplissant les conditions de l'article 33 » et le règlement de 2026, article 2
(JORFARTI000054436031), « les adhérents remplissant les conditions de l'article 1 er » ; la
fiche `liquidation_regime_par_regime` cite la phrase de 2021 et l'attribue à 2021 : exact.

L'arrêté du 11 janvier 2011 (JORFARTI000023448554) : « Le sixième alinéa de l'article 21 est
remplacé », et l'alinéa nouveau dit que les invalides « peuvent demander à bénéficier de la
retraite à 60 ans sans minoration » ; l'article 23 exige d'avoir « liquidé ses pensions de
vieillesse personnelles auprès de la totalité des régimes légaux ou rendus légalement
obligatoires, de base et complémentaires » au seul vétérinaire qui veut que « le bénéfice de
la retraite complémentaire [soit] entièrement cumulée avec une activité professionnelle » :
exact. Comptés dans l'index : « liquid » ne vient ni en 2014 (JORFARTI000028939421) ni en
novembre 2015 (JORFARTI000031549970), et une seule fois en février 2015
(JORFARTI000030285511), pour la pension d'invalidité ; « soixant » et « 60 ans » ne viennent
dans aucun des trois ; « base » n'y vient que pour l'appel des cotisations (« appelée sur la
base de la classe B », « sur les bases suivantes ») ; en 2014, « les quatrième et cinquième
alinéas sont supprimés » de l'article 13. Les avis de 1999 et de 2006 : « art. 3 à 40 du
titre II » (JORFARTI000001562289), « sera publié intégralement au Bulletin officiel no 99/33
du ministère de l'emploi et de la solidarité » (JORFARTI000001368893), « art. 21, 23 et 24
du titre II », au « Bulletin officiel du ministère de la santé et des solidarités »
(JORFARTI000001494755) : exact.

**Le Bulletin officiel, cherché une fois.** Le n° 99/33 est celui de 1999 (arrêté du
5 juillet 1999) ; celui de 2006 n'a pas de numéro dans l'avis du Journal officiel. Aucun
des deux n'est dans l'index, qui ne porte que le JORF et LEGI ; deux recherches sur le web
(« "Bulletin officiel" "99/33" … CARPV », puis les statuts de 2006) n'ont rien rendu. Ils
sont **introuvables d'ici** : il faut les demander à la caisse ou à la Direction de
l'information légale et administrative.

**La présomption est-elle la plus prudente ?** Oui. Deux lectures sont possibles avant
2022 : la complémentaire se demande sans la base (celle du modèle), ou elle l'attend. La
première prolonge le seul texte complet lu, celui de 2021, qui garde « dès leur soixantième
anniversaire » quand la base est à 62 ans depuis la génération 1955. Un indice la soutient,
sans la prouver : l'arrêté du 11 janvier 2011 ouvre encore « la retraite à 60 ans » à
l'inapte, deux mois après la loi n° 2010-1330, qui porte au-delà de soixante ans l'âge de
L. 161-17-2 (LEGIARTI000025014605). La seconde lecture ajouterait une condition qu'aucun
texte lu n'écrit. La présomption est déclarée là où il faut : les approximations de
`liquidation_regime_par_regime` (l'écart, son effet, les trois cas du test, l'`a_relire`),
celles de `carpv_minoration_age_seul`, la limite `docs/limites/ecarts-au-droit-positif.md`,
et le commentaire de `SANS_LEUR_BASE` (`departs.py`). Le « rien ne la fonde » de L-bis est
un peu sévère, à cause de cet indice ; ce n'est pas un écart.

## 2. Le cliquet des textes : conforme

`git show 9772e14 -- data/reference/textes/perimetre.yaml` : `redactions_sans_statut`
passe de 9340 à 9334. La note L n'est pas récrite ; seul un renvoi daté s'y ajoute.

## 3. Le coefficient des biologistes : conforme, sauf la génération 1953 (écart 1)

**Les textes, rouverts.** Les statuts de la CAVP, article 14 des prestations des
biologistes (arrêté du 23 juin 2011, JORFARTI000024270214, au Journal officiel du 29 juin ;
aucune date d'effet écrite, donc en vigueur le lendemain, le 30 juin) : « La prestation
supplémentaire de vieillesse est alors réduite par application d'un coefficient
d'anticipation qui est fonction du nombre de trimestres manquants, à la date d'effet des
droits, pour atteindre l'âge fixé à l'article L. 351-8 (1°) du code de la sécurité sociale.
Ce coefficient est égal à 1,25% par trimestre manquant dans la limite de vingt
trimestres » : exact, mot pour mot. L'article est bien le 14 (« Article 14 : Cet article est
remplacé par les dispositions suivantes »). Le règlement de 2026, article 1er
(JORFARTI000054436087), dit de même, « coefficient de minoration » et « au 1° de l'article
L. 351-8 » : exact.

L. 351-8, 1° : « l'âge prévu à l'article L. 161-17-2 augmenté de cinq années »
(LEGIARTI000023030950, du 1er juillet 2011, que la loi n° 2010-1330, article 118, II, rend
applicable « aux pensions prenant effet à compter du 1er juillet 2011 » ;
LEGIARTI000028498855, « applicable aux pensions prenant effet à compter du 1er février
2014 », jusqu'au 31 août 2023) ; puis « l'âge prévu au premier alinéa de l'article
L. 161-17-2 augmenté de trois années » (LEGIARTI000047452736, LEGIARTI000051289852) : exact.
D. 161-2-1-9 (LEGIARTI000025089933, du 31 décembre 2011 au 1er septembre 2023) : de « 1°
Soixante ans pour les assurés nés avant le 1er juillet 1951 » à « 6° Soixante deux ans pour
les assurés nés à compter du 1er janvier 1955 », mot pour mot. La rédaction d'avant
(LEGIARTI000023388636, du 1er juillet au 31 décembre 2011) donne 60 ans et 8 mois en 1952 :
elle ne régit aucun biologiste, nul né en 1952 ne pouvant partir avant 2012.

D'où l'âge du taux plein : 65 ans avant le 1er juillet 1951 ; 65 ans 4 mois au second
semestre 1951 ; 65 ans 9 mois en 1952 ; 66 ans 2 mois en 1953 ; 66 ans 7 mois en 1954 ;
67 ans depuis 1955. La table `data/reference/legislation/age_annulation_decote.csv` les
écrit au centième : 65,00, 65,33, 65,75, **66,17**, 66,58, 67,00. Or 66 ans et 2 mois valent
66,1667, et 66,17 les dépasse.

**Les valeurs, à la main, puis aux deux moteurs.** La convention du modèle : l'assuré part
au premier du mois qui suit l'âge demandé, les trimestres manquants se comptent au
trimestre supérieur (déclaré dans la fiche, le texte ne le disant pas). Né le 10 du mois,
début d'activité à 30 ans, pour que la durée n'efface rien (voir le point 5) ; c = 1 −
1,25 % × min(20, manquants) :

| Né le | Part à | Âge du taux plein | Manquants à la main | c attendu | Les deux moteurs |
|---|---|---|---|---|---|
| 10/06/1951 | 60 a | 65 a | 20 | 0,75 | 0,75 |
| 10/06/1951 | 62 a | 65 a | 12 | 0,85 | 0,85 |
| 10/06/1951 | 64 a | 65 a | 4 | 0,95 | 0,95 |
| 10/06/1951 | 65 a | 65 a | 0 | 1 | 1 |
| 10/07/1951 | 60 a 4 m | 65 a 4 m | 20 | 0,75 | 0,75 |
| 10/07/1951 | 62 a | 65 a 4 m | 13,33 → 14 | 0,825 | 0,825 |
| 10/07/1951 | 65 a | 65 a 4 m | 1,33 → 2 | 0,975 | 0,975 |
| 10/07/1951 | 65 a 3 m | 65 a 4 m | 0,33 → 1 | 0,9875 | 0,9875 |
| 10/07/1951 | 65 a 4 m | 65 a 4 m | 0 | 1 | 1 |
| 10/12/1951 | 63 a | 65 a 4 m | 9,33 → 10 | 0,875 | 0,875 |
| 10/02/1952 | 60 a 9 m | 65 a 9 m | 20 | 0,75 | 0,75 |
| 10/02/1952 | 64 a | 65 a 9 m | 7 | 0,9125 | 0,9125 |
| 10/02/1952 | 65 a 8 m | 65 a 9 m | 0,33 → 1 | 0,9875 | 0,9875 |
| 10/02/1952 | 65 a 9 m | 65 a 9 m | 0 | 1 | 1 |
| 10/02/1953 | 61 a 2 m | 66 a 2 m | 20 | 0,75 | 0,75 |
| 10/02/1953 | 64 a | 66 a 2 m | 8,67 → 9 | 0,8875 | 0,8875 |
| 10/02/1953 | 66 a | 66 a 2 m | 0,67 → 1 | 0,9875 | 0,9875 |
| 10/02/1953 | 66 a 1 m | 66 a 2 m | 0,33 → 1 | 0,9875 | 0,9875 |
| **10/02/1953** | **66 a 2 m** | **66 a 2 m** | **0** | **1** | **0,9875** |
| 10/02/1953 | 66 a 3 m | 66 a 2 m | 0 | 1 | 1 |
| 10/02/1954 | 61 a 7 m | 66 a 7 m | 20 | 0,75 | 0,75 |
| 10/02/1954 | 62 a | 66 a 7 m | 18,33 → 19 | 0,7625 | 0,7625 |
| 10/02/1954 | 66 a | 66 a 7 m | 2,33 → 3 | 0,9625 | 0,9625 |
| 10/02/1954 | 66 a 6 m | 66 a 7 m | 0,33 → 1 | 0,9875 | 0,9875 |
| 10/02/1954 | 66 a 7 m | 66 a 7 m | 0 | 1 | 1 |
| 10/02/1955 | 62 a | 67 a | 20 | 0,75 | 0,75 |
| 10/02/1955 | 64 a | 67 a | 12 | 0,85 | 0,85 |
| 10/02/1955 | 66 a | 67 a | 4 | 0,95 | 0,95 |
| 10/02/1955 | 66 a 11 m | 67 a | 0,33 → 1 | 0,9875 | 0,9875 |
| 10/02/1955 | 67 a | 67 a | 0 | 1 | 1 |

Vingt-neuf cas sur trente sont conformes. Les trois du test aussi (né le 10 février 1950, 1952
et 1953, partis à 62, 63 et 63 ans : 12, 11 et 13 trimestres, 0,85, 0,8625 et 0,8375), et
leur arrondi ne dépend pas du jour où l'âge se compte : de la date d'effet au jour de l'âge,
11,77, 10,77 et 12,43 trimestres ; à l'anniversaire, 12, 11 et 12,67 ; au premier du mois,
11,67, 10,67 et 12,33, chaque fois portés à 12, 11 et 13.

**L'écart 1, moyen : la génération 1953 à 66 ans et 2 mois.** Le biologiste né le
10 février 1953 qui part à 66 ans et 2 mois, à effet du 1er mai 2019, a atteint l'âge de
L. 351-8, 1° : aucun trimestre ne lui manque, le coefficient vaut 1. Les deux moteurs lui
servent 0,9875. La cause : `auTrimestreSuperieur((66,17 − 66,1667) × 4)`, soit 0,0133,
arrondi au millième (0,013) puis porté à 1 (`moteur/js/droit/liquider.js`,
`trimestresDeDecote` ; son jumeau, `liquider.py`). Les autres générations y échappent :
65,33 et 66,58 sont sous 65 ans 4 mois et 66 ans 7 mois, et 65,75 tombe juste. Ce n'est pas
le cas d'un régime : c'est la classe. Le même assuré, salarié, reçoit au régime général
« taux 49.375% » au lieu de 50 %, et à l'Arrco, à l'Agirc-Arrco et à la tranche 2,
« coefficient d'anticipation 0.9900 » au lieu de rien. Il faut attendre 66 ans et 3 mois pour
le taux plein. Le défaut précède le commit, puisque la table et l'arrondi sont plus anciens,
mais le commit l'étend à l'ASV des biologistes. Sa note cite « 66,17 » sans le voir.
Gravité moyenne : un seul mois de départ, une seule génération, un trimestre (−1,25 % de la
pension de base, −1 % de l'Agirc-Arrco). Mais c'est justement le mois que vise l'assuré né en
1953 à qui manque de la durée. La correction est à la file du modèle : écrire l'âge au mois
près, 66,1667 ou en mois, ou comparer en mois. Elle se fait le test d'abord, dans les deux
moteurs, pour tous les régimes qui lisent la table (`age_annulation_decote`, fiche du même
nom). D'autres tables au centième peuvent avoir le même défaut, qu'on n'a pas cherché ici.

## 4. La déclaration du coefficient des biologistes : conforme

L'approximation de `asv_autres_professions_de_sante` nomme désormais chaque génération et
ses textes, l'effet mesuré (0,7625 → 0,85 ; 0,80 → 0,8625 et 0,8375), et ce que le texte ne
tranche pas : l'arrondi, les 65 ans du parent de trois enfants (loi n° 2010-1330,
article 20, IV, lu au `--le` de L. 351-8 : « l'âge mentionné au 1° dudit article est fixé à
soixante-cinq ans pour les assurés nés entre le 1er juillet 1951 et le 31 décembre 1955
inclus »), et la durée. `asv_directeurs_laboratoire` est ajouté à la liste des régimes de
`age_annulation_decote`, et `age_taux_plein_par_generation: age_annulation_decote` est mis
aux cinq périodes de 2009 et d'après, celles qui portaient déjà
`age_ouverture_par_generation` : exact.

**L'écart 2, faible, hors du commit : avant 2009, 67 ans.** Les périodes de 1981 à 2008
gardent `age_taux_plein: 67`, « du guide » de la CNAVPL de 2025. La fiche le déclare. Mais
l'âge de 67 ans n'existe que depuis la loi n° 2010-1330 : avant le 1er juillet 2011, le 1°
de L. 351-8 visait « un âge déterminé » (LEGIARTI000006742633), et R. 351-27 le fixait :
« l'âge prévu au 1° de l'article L. 351-8 est fixé à soixante-cinq ans »
(LEGIARTI000006749436, du 15 février 2004 au 1er janvier 2009). Si les statuts d'alors
renvoyaient déjà à cet article, comme ceux de 2011, le biologiste parti à 62 ans en 2008
aurait été minoré de 12 trimestres (0,85), et non de 20 (0,75). Aucun statut d'avant 2011
n'est lu : c'est une présomption contre une autre, et celle qui est gardée est la plus
défavorable. Elle est à revoir avec les statuts, à la file du modèle.

## 5. La durée qui efface la minoration : déclarée, et mesurée ici

Les deux textes comptent les trimestres manquants « pour atteindre l'âge » ; ni l'article 14
de 2011, ni l'article 1er de 2026 ne parlent de la durée. Ils ne connaissent que l'inapte,
servi sans coefficient à l'âge de L. 161-17-2, et, en 2026, la liquidation anticipée du
II au IV de L. 643-3. Le modèle prend pourtant le plus favorable de l'âge et de la durée.
L-bis le déclare dans la fiche, avec un effet « non mesuré ». Le voici : le biologiste né le
10 février 1953, entré à 20 ans et parti à 63 ans, a 172 trimestres pour 165 requis. Les
deux moteurs lui servent 1. Le texte lui oppose 13 trimestres, soit 0,8375 (−16,25 %). Entré
à 30 ans, il garde 0,8375. Le point est déclaré : ce n'est pas un écart de L-bis. C'est un
écart au droit, qui reste à la file du modèle.

## 6. Les deux moteurs, et les présomptions décalées

`tests/test_ouverture_des_liberaux.py` : 36 verts ; sous `PRESOMPTIONS_DECALEES=1`, 36
verts. Les trente cas du point 3 passent par `servi_et_refait` : le portage les sert, le
moteur Python les refait au bit près, et les deux rendent les valeurs du tableau, la
génération 1953 à 66 ans et 2 mois comprise. Sous `PRESOMPTIONS_DECALEES=1`, dix cas
rendent les mêmes valeurs : sept du tableau (1951 de juin et de juillet, 1952, 1953, dont
66 ans et 2 mois, 1954, 1955) et les trois du test.

## 7. Les écarts

| # | Écart | Gravité | Preuve |
|---|---|---|---|
| 1 | La table écrit 66,17 pour 66 ans et 2 mois. Né en 1953 et parti à 66 ans et 2 mois, l'assuré reste minoré d'un trimestre : ASV des biologistes 0,9875, régime général 49,375 %, Agirc-Arrco 0,99, au lieu du taux plein. Le défaut précède le commit, qui l'étend aux biologistes | moyen | L. 351-8, 1°, LEGIARTI000028498855 ; D. 161-2-1-9, 4°, LEGIARTI000025089933 ; `age_annulation_decote.csv` ; `trimestresDeDecote` ; point 3 |
| 2 | Avant 2009, l'ASV des biologistes est minorée jusqu'à 67 ans, quand l'âge du 1° de L. 351-8 était de 65 ans. La présomption est déclarée, mais elle est la plus défavorable. Hors du commit | faible | L. 351-8, LEGIARTI000006742633 ; R. 351-27, LEGIARTI000006749436 ; `asv_directeurs_laboratoire.yaml`, périodes de 1981 à 2008 ; point 4 |

Le reste est conforme : les citations de la CARPV et de la CAVP, les dates d'effet, le
cliquet, les trois valeurs du test et les déclarations. La durée qui efface la minoration
(point 5) est déclarée, et son effet est maintenant mesuré. Les statuts de la CARPV de 1999
à 2021 et ceux de la CAVP d'avant 2011 restent introuvables d'ici.
