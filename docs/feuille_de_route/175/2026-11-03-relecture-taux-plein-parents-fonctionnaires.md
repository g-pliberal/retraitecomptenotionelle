# Relecture du taux plein à 65 ans des parents de trois enfants fonctionnaires

File R-M4 de la sixième vague, le 3 novembre 2026 : relecture indépendante du commit
8ea1ce7 (session M4, note `2026-11-03-taux-plein-parents-de-trois-enfants-fonctionnaires.md`),
qui borne à soixante-cinq ans l'âge d'annulation de la décote du fonctionnaire sédentaire
parent de trois enfants né de juillet 1951 à 1955. Rien n'a été repris de la session M4 ni
de mémoire : l'index de la DILA récupéré dans la session (LEGI à jour au 2 novembre 2026,
JORF au 3 novembre), chaque texte ouvert à la rédaction en vigueur aux dates d'effet de ces
pensions (2015 à 2021) ; chaque fragment cité entre « » dans la fiche cherché par un script
dans le texte de l'index (les vingt textes de la fiche qui y ont un identifiant, dont les
onze que M4 ajoute : aucun fragment absent ; un fragment altéré à dessein y est bien dit
absent) ; chaque valeur attendue refaite à la main, et cinq
cas de plus calculés par les deux moteurs. Rien n'a été modifié : ni règle, ni donnée, ni
test, ni fiche.

**Verdict : conforme, sauf un écart moyen et quatre faibles.** Les textes sont cités mot
pour mot, à la bonne rédaction ; les conditions de R. 26 ter, I, sont complètes ; les
vingt-six valeurs attendues des tests se refont à la main ; les deux moteurs les rendent.
L'écart moyen : une année que la saisie dit « congé de maternité », seule, ouvre la borne,
quand un congé de maternité n'atteint jamais l'« année » que R. 26 ter demande (point 5).

## 1. Les textes, à la rédaction en vigueur

| Texte | Rédaction lue | Constat |
|---|---|---|
| Loi n° 2010-1330, art. 28, III | LEGIARTI000023023851 (1er juillet → 23 décembre 2011), LEGIARTI000025014566 (depuis, seule en vigueur de 2012 à aujourd'hui) | conforme : le III identique dans les deux, cité mot pour mot ; « nés entre le 1er juillet 1951 et le 31 décembre 1955 », « dont la limite d'âge était fixée à soixante-cinq ans », « les conditions prévues aux 1° à 3° du IV de l'article 20 », « ne peut être supérieur à soixante-cinq ans », les enfants de L. 18, II |
| Même loi, art. 118, II | JORFARTI000023022348 | conforme : pensions « prenant effet à compter du 1er juillet 2011 » |
| Même loi, art. 20, IV, 1° à 3° | LEGIARTI000023023835 (11 novembre 2010 → 28 février 2025) | lu : trois enfants « eus ou élevés » ; l'interruption ou la réduction « dans des conditions et un délai déterminés » ; un minimum de trimestres d'activité « avant cette interruption ou réduction », dans un régime obligatoire de l'Union, de l'EEE ou de la Suisse |
| CPCMR, R. 26 ter, I | LEGIARTI000024111781, seule rédaction (depuis le 3 juin 2011), insérée par le décret n° 2011-620, art. 3 (JORFARTI000024110126) | conforme, mot pour mot ; conditions complètes (point 2) |
| CPCMR, R. 13, 1° et 2° | LEGIARTI000023449727 (1er janvier 2011 → 1er octobre 2025) | conforme : a) le congé pour maternité, b) d'adoption, c) parental — dont celui de L. 122-28-1 du code du travail —, d) de présence parentale, e) la disponibilité pour élever un enfant de moins de huit ans |
| CPCMR, L. 18, II | LEGIARTI000006362714 cité (1991 → 2012) ; en vigueur aux dates d'effet : LEGIARTI000025076852 (2012 → 16 avril 2023) | conforme : le II, comparé par script, est identique, au caractère près, dans les quatre rédactions suivantes |
| CPCMR, L. 14, I | LEGIARTI000025014534 cité (2011 → 2014) ; en vigueur aux dates d'effet : LEGIARTI000028498863 (22 janvier 2014 → 15 juillet 2018), LEGIARTI000037200740 (→ 1er septembre 2023) | conforme : la première phrase et le 1° cités, retrouvés à l'identique dans les deux rédactions en vigueur ; elles portent aussi « arrondi à l'entier supérieur », dont dépendent les calculs (remarque faible e, point 6) |
| Loi n° 2003-775, art. 66, III | LEGIARTI000006758610, seule rédaction | conforme : « 2014 [...] moins 6 trimestres » à « 2018 [...] moins 2 trimestres », 1,25 % de 2015 à 2018, la colonne « Année au cours de laquelle sont réunies les conditions mentionnées au I et au II de l'article L. 24 » |
| CPCMR, L. 17 | LEGIARTI000023033916 (11 novembre 2010 → 16 avril 2023), en vigueur aux dates d'effet | conforme, mot pour mot |
| Décret n° 2010-1744, art. 3 | JORFARTI000023334941 | conforme : la minoration de l'âge du minimum garanti ne vaut que pour qui atteint l'âge d'ouverture de 2011 (9 trimestres) à 2015 (1 trimestre) |
| Décret n° 2003-1306, art. 65-3 ; décret n° 2004-1056, art. 50-3 | LEGIARTI000024113270, LEGIARTI000024113274 (depuis le 1er juillet 2011 ; la rédaction précédente, jamais en vigueur) | conforme, mot pour mot ; leurs enfants sont ceux de leur article 24, II, et 20, II, que j'ai lus : la même liste que L. 18, II |
| Décret n° 2010-1740, art. 7 et 16, III | JORFARTI000023334770, JORFARTI000023334739 | conforme : l'article 7 insère 65-3 et 50-3 ; « applicables aux pensions liquidées à compter du 1er juillet 2011 » |
| Décret n° 2011-620, art. 10 | JORFARTI000024110234 | conforme : il ajoute à 65-3 et 50-3 « Les modalités d'application du présent article sont celles prévues pour les fonctionnaires de l'Etat à l'article R. 26 ter » |
| Décret n° 2011-2103, art. 1er et 8 | JORFARTI000025061553, JORFARTI000025061595 | conforme : l'âge d'ouverture, « 1954 61 ans et 7 mois A compter de 1955 62 ans » ; la limite d'âge, « quatre mois par génération » (60 ans atteints de juillet à décembre 2011), « cinq mois » (de 2012 à 2014) : 65 ans et 4 mois, 65 ans et 9 mois, 66 ans et 2 mois, 66 ans et 7 mois de 1951 à 1954 ; soixante-sept ans « nés à compter du 1er janvier 1955 » (art. 28, I, LEGIARTI000025014566) |
| Loi n° 2025-199, art. 87, IV et VIII, A | JORFARTI000051269910 | conforme : le IV de l'article 20 abrogé pour les pensions prenant effet dès le 1er janvier 2026 ; l'article 28 reste en vigueur (LEGIARTI000025014566, sans fin) |

## 2. Les conditions de R. 26 ter, I, complètes et justes

- *Les enfants* : trois, ceux de L. 18, II (art. 28, III) ; la saisie n'en distingue pas
  l'origine, déclaré. Les neuf ans d'éducation : remarque faible d, point 6.
- *La fenêtre* : « l'année civile de la naissance [...] et les deux années civiles
  suivantes ou, si l'enfant est né [...] au cours d'un second semestre, [...] les trois
  années civiles suivant celle de cette naissance » : le code (`debuts`, mois ≤ 6 ou non)
  le lit ainsi ; dite à l'année, la naissance demande les deux fenêtres, ce qui est plus
  strict que le texte, et déclaré.
- *La durée* : « une durée d'au moins une année » dans la fenêtre : la somme des parts
  d'année des lignes aux motifs `maternite` et `education_enfant` ; non dite continue par
  le texte, déclaré.
- *Le cadre* : « dans le cadre des congés ou de la disponibilité mentionnés au 1° de
  l'article R. 13 » : lu sur le motif de la ligne ; « sans activité » ne l'ouvre pas ;
  « élever un enfant » est tenu pour un congé ou une disponibilité de R. 13, déclaré ;
  « congé de maternité », point 5.
- *Avant la naissance* : « au titre des deux années précédant l'année de la naissance
  [...], une durée d'assurance, telle que définie à l'article L. 14, égale ou supérieure à
  huit trimestres » : les trimestres de toutes les lignes des deux années, ce que L. 14, I,
  totalise (services et « durée d'assurance [...] validées dans un ou plusieurs autres
  régimes de retraite de base obligatoires ») ; la même pour l'enfant du second semestre,
  comme le texte le dit.
- *L'activité* : « huit trimestres » de durée d'assurance « à raison de l'exercice d'une
  activité professionnelle, préalablement à l'interruption » (3°) : les lignes d'emploi
  des années qui précèdent la première année d'interruption de la fenêtre ; l'année de
  l'interruption n'y entre pas, ce qui est plus strict que le texte quand elle commence en
  cours d'année.
- *Les catégories* : « dont la limite d'âge était fixée à soixante-cinq ans » : le
  sédentaire seul ; l'emploi classé actif dont il a les services, et le militaire, exclus
  (`_age_du_parent_sedentaire`) ; les trois régimes du code et de ses deux décrets.
- *La réduction d'activité* (2°) : non lue, déclarée dans la fiche et la limite.

## 3. Les valeurs attendues, refaites à la main

Les âges, des textes du point 1 : née le 15 mars 1955, 62 ans le 15 mars 2017, « moins 3
trimestres » de 67 ans : **66,25** ; née le 15 septembre 1954, 61 ans et 7 mois le 15 avril
2016, « moins 4 trimestres » de 66 ans et 7 mois : **65,583** ; née le 15 mars 1953, 61 ans
et 2 mois le 15 mai 2014, « moins 6 » de 66 ans et 2 mois : **64,667** ; née le 15 janvier
1956, hors des générations, 62 ans en 2018, « moins 2 » de 67 ans : **66,5** ; née le 15
décembre 1955 : 62 ans en décembre 2017 : 66,25.

Les dix-sept carrières de `CAS_FONCTIONNAIRES` (en service de 1973 à 1977, enfants d'avril
1978, juin 1980, juin 1982, sauf mention), toutes refaites :

| Cas | Fenêtre, avant, activité | Attendu | Refait |
|---|---|---|---|
| trois ans à élever un enfant | 1978-1980, 3 années ; 1976 + 1977 = 8 ; 1973-1977 = 20 | 65 | 65 |
| un an, 1980 | 1980 dans 1978-1980 ; 8 ; 20 | 65 | 65 |
| un an de maternité, 1978 | une année « maternité » | 65 | 65 selon la règle du modèle ; **66,25 selon le texte**, point 5 |
| sans activité | aucune année de congé | 66,25 | 66,25 |
| mars 1978, congé en 1981 | 1978-1980 sans congé ; juin 1980 : 1978 + 1979 = 0 < 8 ; juin 1982 : 1982-1984 sans congé | 66,25 | 66,25 |
| septembre 1978, congé en 1981 | second semestre : 1979-1981 ; 1976 + 1977 = 8 ; 20 avant 1981 | 65 | 65 |
| à l'année, congé en 1979 | « 1978 » : 1979 dans 1978-1980 et 1979-1981 ; 8 ; 20 | 65 | 65 |
| à l'année, congé en 1981 | « 1978 » : 1981 hors de 1978-1980 ; « 1980 » : 0 avant ; « 1982 » : aucun congé de 1982 à 1985 | 66,25 | 66,25 |
| huit trimestres d'activité | service 1976-1977 : 8 avant, 8 d'activité, « fixé à huit » | 65 | 65 |
| quatre trimestres d'activité | 1976 au chômage indemnisé : 8 de durée, 4 d'activité < 8 ; juin 1980 : 4 d'activité avant 1980 ; juin 1982 : aucun congé | 66,25 | 66,25 |
| deux enfants | 2 < 3 | 66,25 | 66,25 |
| naissances non dites | aucune fenêtre | 66,25 | 66,25 |
| née en septembre 1954 | conditions remplies | 65 | 65 |
| née en septembre 1954, sans activité | — | 65,583 | 65,583 |
| née en mars 1953 | conditions remplies, l'âge déjà sous 65 | 64,667 | 64,667 |
| née en décembre 1955 | service dès 1974 : 16 d'activité | 65 | 65 |
| née en janvier 1956 | hors des générations | 66,5 | 66,5 |

Les régimes : la CNRACL et les ouvriers de l'État, 65 avec trois enfants, 66,25 avec deux,
refaits ; l'emploi classé actif, avec ses services (1973-1977 et 2003-2019, vingt-deux
ans), garde l'âge de sa catégorie, le même avec deux ou trois enfants, sous 65 ans.

De bout en bout (sept requêtes), refaites : partie à 65 ans le 1er avril 2020 (65 ans et
17 jours), trois enfants : âge atteint, **75 %** ; sans la borne, 14,5 mois jusqu'à 66 ans
et 3 mois, arrondis à 5 trimestres (L. 14, I), la durée manquant bien davantage (166 − 108
ou 112) : 75 % × (1 − 5 × 1,25 %) = **70,3125 %**, les deux cas témoins et « sans
activité » ; partie à 64 ans le 1er avril 2019 : 11,5 mois, 4 trimestres, 75 % × 0,95 =
**71,25 %**, sans la borne 26,5 mois, 9 trimestres, 75 % × 0,8875 = **66,5625 %** ; la
CNRACL et l'ouvrière de l'État, 75 %. Le minimum garanti (deux requêtes) : avec trois
enfants, l'âge « auquel s'annule le coefficient de minoration prévu aux I et II de
l'article L. 14 » (L. 17) est celui que l'article 28, III, borne : 65 ans, atteint, le
minimum s'ouvre ; avec deux, ni la durée ni l'âge (66 ans et 3 mois), et le décret
n° 2010-1744 ne minore pas l'âge de qui atteint l'âge d'ouverture en 2017 : fermé.
Conforme : l'ouverture du minimum suit du texte, sans autre lecture.

Cinq cas de plus, posés à la main puis demandés aux deux moteurs (`droit_et_refait`) :
née en mars et en mai 1954, sans congé, 61 ans et 7 mois en 2015, « moins 5 trimestres »
de 66 ans et 7 mois : **65,33** — les deux moteurs rendent 65,33 ; avec trois ans de
congé, 65 ; née en juin 1954 : 65,58 ; née en novembre 1953, 61 ans et 2 mois en janvier
2015, « moins 5 » de 66 ans et 2 mois : **64,92**, sous 65 ans, ce que rendent les moteurs.
« Rien ne change pour 1951 à 1953 » est donc juste jusqu'aux derniers nés de 1953.

## 4. Les deux moteurs, les tests, le paquet

Le portage (`categories.js`, `liquider.js`) et son jumeau (`categories.py`, `liquider.py`)
se lisent ligne pour ligne : mêmes motifs, même fenêtre, mêmes seuils, la borne prise par
`min` dans la seule branche du barème `fonction_publique`.

Les tests, lancés dans cette session sur main à 207cb53 :

- `tests/test_taux_plein_a_soixante_cinq_ans.py` et `tests/test_regle_de_chacun.py` : 22
  passés.
- `python -m pytest -m rapide` : 4 333 passés, 6 sautés, 2 rouges, étrangers à M4 :
  `test_simulateur.py::test_l_exercice_1952_ne_preleve_que_la_moitie_de_la_cotisation_annuelle`
  (`{'msa_non_salaries': 8.5} != {'msa_non_salaries': 4.25}`) et
  `test_minima_agricoles.py::test_les_deux_moteurs_revisent_la_meme_majoration` (dix écarts
  python/js de la majoration des non-salariés agricoles). Ils tiennent au commit 79cbb6f
  (action 131, la cotisation agricole de 1952), qui change `msa_non_salaries.yaml` sans
  refaire `moteur/donnees.json` : paquet refait, les deux passent.
- `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide` : 4 136 passés, 205 sautés, aucun
  rouge.
- Les fichiers de tests qui lisent les fichiers touchés (`grep -l` : `test_agirc_arrco_au_droit.py`,
  `test_caisses_du_pacifique.py`, `test_carte.py`, `test_coefficients_agirc_1947.py`,
  `test_cultes_au_droit.py`, `test_donnees.py`, `test_fabrique.py`, `test_ircantec.py`,
  `test_jumeaux.py`, `test_outillage.py`, `test_rafp.py`, `test_simulateur.py`), avec
  `test_textes.py`, `test_pont.py` et les confrontations légères (`test_oracle.py`,
  `test_destinie.py`, `test_estimation_officielle.py`, `test_verification.py`), sur le
  paquet refait : 1 188 passés, 1 sauté.
- `python scripts/construire_donnees.py`, puis `git status` : `moteur/donnees.json` change,
  mais aucune clé ne nomme les fonctionnaires ni la fiche : ce qui bouge (les agrégats,
  l'équilibre, l'inventaire, un régime) vient des commits suivants, celui de l'action 131
  d'abord. Le bloc que M4 a fabriqué est à jour. Le paquet de main a été remis tel quel.

## 5. Le congé de maternité : un cadre de R. 13, 1°, mais jamais une année

R. 13, 1°, a), nomme bien « le congé pour maternité » : il est l'un des « congés [...]
mentionnés au 1° de l'article R. 13 », et une interruption qui le contient y entre. Mais
R. 26 ter, I, 1°, demande que le fonctionnaire ait « interrompu [son] activité pendant
une durée d'au moins une année », et aucun congé de maternité n'a jamais duré une année :

- en 1978, au code du travail, L. 122-26 : « six semaines avant la date présumée de
  l'accouchement et se termine huit semaines après » (LEGIARTI000006646773, jusqu'au
  1er octobre 1978), vingt semaines au plus avec un état pathologique ; puis « dix
  semaines après », seize en tout, vingt-deux au plus avec un état pathologique, « deux
  semaines » de plus « en cas de naissances multiples » (LEGIARTI000006646774, du 1er
  octobre 1978 au 3 janvier 1984) ;
- aujourd'hui, L. 1225-17 à L. 1225-19 (LEGIARTI000018764596, LEGIARTI000006900898,
  LEGIARTI000018764594) : seize semaines, vingt-six à partir du troisième enfant,
  trente-quatre pour des jumeaux, quarante-six pour des triplés ;
- au fonctionnaire de l'État, la loi n° 84-16, art. 34, 5° : « Au congé pour maternité
  [...] avec traitement, d'une durée égale à celle prévue par la législation sur la
  sécurité sociale » (LEGIARTI000032442186).

Une année d'interruption qui commence par un congé de maternité ne s'atteint donc qu'en
l'enchaînant avec un congé parental ou une disponibilité pour élever un enfant, ce que la
saisie dit « élever un enfant ». Or le modèle compte une année « congé de maternité » pour
une année entière d'interruption, et `CAS_FONCTIONNAIRES` l'affirme : « un an de maternité,
1978 » → 65, avec pour seule raison « Le congé de maternité est un congé de R. 13, 1°, a. »
Pour la carrière telle que saisie — une année 1978 sans emploi, dite congé de maternité —,
le texte ne donne la borne que si le reste de l'année a été un congé parental ou une
disponibilité : la valeur attendue ne suit pas de la source. Le même cas arrive par un
relevé : une année sans revenu dont la ligne dit « maternité » ou « adoption » devient une
interruption `maternite` de toute l'année (`moteur/js/releve-lu.js`, `MOTIFS` et
l'interruption des années sans revenu). Et dès qu'une année « élever un enfant » est dans
la fenêtre, elle suffit seule : le motif `maternite` ne décide que là où il ne devrait pas
suffire.

## 6. Les écarts, et leur gravité

a. **Moyen** — une année « congé de maternité » seule ouvre la borne (point 5). Preuve :
   R. 26 ter, I, 1° ; L. 122-26 (1973 et 1978) ; L. 1225-17 à L. 1225-19 ; loi n° 84-16,
   art. 34, 5° ; le cas « un an de maternité, 1978 », et sa valeur rendue par les deux
   moteurs (65, au lieu de 66,25 pour la carrière saisie). Effet : jusqu'à 5 trimestres de
   décote (6,25 % de la pension en 1955, 3,75 % au plus en 1954) et le minimum garanti,
   servis sans que la saisie dise la condition. À reprendre, le test d'abord, à la file M4 : ôter
   `maternite` des motifs qui suffisent seuls (ne le compter qu'avec une année « élever un
   enfant », ou pour la durée légale de son congé), récrire le cas à 66,25, et dire dans
   l'approximation et la limite qu'un congé de maternité suivi d'un congé parental ou d'une
   disponibilité se dit « élever un enfant ».
b. **Faible** — l'effet de la fiche (son `effet` général) dit « 3 trimestres de décote de
   moins en 1954, 5 en 1955, [...] une décote de 3,75 % et de 6,25 % en moins » : juste pour
   les nés de juin à décembre 1954 (65 ans et 7 mois) ; les nés de janvier à mai 1954 ont
   65 ans et 4 mois (61 ans et 7 mois atteints en 2015, « moins 5 trimestres »), et la
   fonctionnaire née le 15 du mois, partie le 1er du mois qui suit ses soixante-cinq ans,
   n'y gagne que 2 trimestres, 2,5 % (3,5 mois, arrondis à l'entier supérieur). Le calcul
   du modèle est juste (65,33, point 3) ; la phrase seule est à préciser, comme le dit déjà
   `contenu.droit` (« 65 ans et 4 ou 7 mois »).
c. **Faible** — l'AVPF d'un relevé : `releve-lu.js` range « avpf » et « parent au foyer »
   sous `education_enfant`, que la règle tient pour un congé ou une disponibilité de R. 13.
   L'AVPF va aussi au parent resté au foyer sans congé ni disponibilité, après une
   démission. L'approximation déclare qu'une année « élever un enfant » a pu être une
   disponibilité pour convenances personnelles ou une démission, sans dire qu'une année
   d'AVPF d'un relevé y entre : à ajouter à sa déclaration.
d. **Faible** — les neuf ans : l'approximation de la version de 2011 présume « les neuf ans
   d'éducation avant leur seizième anniversaire (R. 342-2), pour l'enfant qui n'est pas né
   de l'assuré » ; au fonctionnaire, les enfants sont ceux de L. 18, II, et L. 18, III,
   veut qu'ils aient « été élevés pendant au moins neuf ans » pour la majoration ; que
   l'article 28, III, l'exige aussi, le texte ne le dit pas (il ne renvoie qu'au II, et le
   1° de l'article 20, IV, au deuxième alinéa de L. 351-12). À déclarer comme non tranché,
   en nommant L. 18, III.
e. **Faible, de forme** — L. 14, I, est cité dans sa rédaction de 2011 à 2014, non dans
   celles en vigueur aux dates d'effet (2014-2018, 2018-2023), dont les phrases citées sont
   identiques ; et « arrondi à l'entier supérieur », d'où viennent les 3 trimestres de
   1954 et les 5 de 1955, n'est pas cité.

Ce que les textes ne tranchent pas, et que M4 déclare, est juste : le renvoi de l'article
28, III, au IV de l'article 20 abrogé depuis 2026 est sans effet (né au plus tard en 1955,
le fonctionnaire a soixante-dix ans au moins, au-delà de son âge d'annulation, 66 ans et 3
mois au plus) ; « liquidées » ou « prenant effet » le 1er juillet 2011, sans effet (le
sédentaire né en juillet 1951 n'ouvre son droit qu'en novembre 2011, et la borne ne mord
qu'en 1954 et 1955) ; l'année d'interruption non dite continue.

## Ce qui reste

À la file M4 : l'écart a, le test d'abord ; les remarques b à e avec lui. Pour le
propriétaire, aucune question : le texte tranche le point 5.
