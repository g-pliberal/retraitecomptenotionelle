# La fraction d'avant 1998 des cultes : l'âge de son taux plein, le minimum majoré du V, « gratuitement »

Vague 7, le 5 novembre 2026, file M4/cultes. Cette note reprend les trois points que la
note `2026-11-05-retouches-de-la-relecture-r-m4c.md` laisse à la file des cultes (son § 2
et « Signalé, non fait »). Commits : fbf109d (le minimum majoré du V, test et code, dans
les deux moteurs), 4052d87 (« gratuitement », des commentaires), puis celui de cette note
(la fiche `cultes_fractions_de_pension`, `affiliations.yaml`, l'effet de la fiche
`taux_plein_a_soixante_cinq_ans`, le cliquet des textes).

**Les textes, lus pour cette note** : l'index LEGI, à jour au 4 novembre 2026
(`python scripts/fetch/dila_index.py legi --recuperer`, puis `--mettre-a-jour`), par
`dila_cherche.py legi --texte`, `--num … --le …` ; trois pièces publiques, lues en ligne le
5 novembre 2026 : la page de la CAVIMAC « Demander ma retraite de base », son triptyque
« Votre assurance retraite. Les démarches à effectuer » (2024), la question orale n° 122
du Sénat et sa réponse (JO Sénat du 16 janvier 2008, p. 207).

## 1. L'âge du taux plein de la fraction d'avant 1998 : le modèle suit la caisse

**La lettre.** Le décret n° 2006-1325, article 2, dans sa rédaction du 1er juillet 2011
(LEGIARTI000023397816, en vigueur depuis) : « I. - L'âge fixé au premier alinéa de
l'article D. 721-6 du code de la sécurité sociale, dans sa rédaction en vigueur au 31
décembre 1997 est celui résultant des dispositions de l'article L. 161-17-2 du code de la
sécurité sociale pour les assurés qui justifient [...] d'une durée au moins égale à la durée
fixée au 1° de l'article R. 351-27 » ; « II. - Pour les assurés qui ne remplissent pas les
conditions fixées au I du présent article, la pension de vieillesse mentionnée à l'article
D. 721-6 [...] peut également être allouée à partir de l'âge mentionné au I. Il lui est
alors appliqué le coefficient de minoration fixé au 2° du I et au II de l'article
R. 351-27 » ; « V. - Pour les assurés nés postérieurement au 31 décembre 1938 et qui soit
remplissent les conditions prévues à l'article D. 721-6 du code de la sécurité sociale,
dans sa rédaction en vigueur au 31 décembre 1997, soit justifient de la durée d'assurance
visée au I du présent article, la pension [...] est, lors de sa liquidation, assortie d'une
majoration ». D. 721-6 en vigueur au 31 décembre 1997 (LEGIARTI000006738898, du 21 décembre
1985 au 26 février 2004) : « L'âge à partir duquel est allouée la pension de vieillesse
prévue à la présente sous-section est fixé à soixante-cinq ans. » R. 351-27 (LEGIARTI000024113020,
du 3 juin 2011 au 1er septembre 2023) compte le coefficient « du nombre de trimestres
correspondant à la durée séparant l'âge auquel leur pension prend effet de leur
soixante-cinquième anniversaire, s'ils remplissent les conditions prévues [...] au III ou
IV de l'article 20 [...] ou, dans le cas contraire, de l'âge prévu au 1° de l'article
L. 351-8 », « 1,25 % pour l'assuré né après 1952 ». Lu à la lettre : à soixante-cinq ans,
l'assuré remplit les conditions de D. 721-6 de 1997 ; sa fraction d'avant 1998 lui est
allouée sans le coefficient du II, et le V la majore.

**La caisse.** Sa page « Demander ma retraite de base » : « Si vous bénéficiez d'une
pension calculée à taux minoré, les fractions de pension avant 1979 et de 1979 à 1997
seront portées au niveau du montant maximum de la pension « Cavimac » et vous aurez de plus
une décote qui sera appliquée sur le taux retenu pour le calcul de ces deux fractions (une
décote de 1,25 % par trimestre manquant sera appliquée sur le taux plein qui est de
100 %) » ; « Pour calculer le nombre de trimestre de décote, on comptabilise tout d'abord
le nombre de trimestres compris entre le nombre de trimestres tous régimes confondus et le
nombre de trimestres requis pour l'obtention du taux plein puis on calcule le nombre de
trimestres entre la date d'effet de la pension et l'âge du taux plein. » Son triptyque de
2024 : « L'âge d'obtention du taux plein dépend de l'année de naissance. L'âge auquel la
retraite peut être attribuée à taux plein, quel que soit le nombre de trimestres, varie de
65 à 67 ans. » Pour la caisse, la pension entière a un âge du taux plein, celui de la
génération, jusqu'à soixante-sept ans, et ses fractions d'avant 1998 se décotent jusqu'à
lui. Ni l'une ni l'autre pièce ne nomme D. 721-6 ; aucune circulaire de la caisse sur le
décret n° 2006-1325, aucun exemple chiffré n'a été trouvé (une recherche sur le web,
élargie, n'en rend aucun).

**Ce que fait cette note.** Le scénario 1 est le droit tel que la caisse l'applique, et
la caisse publie sa règle : le modèle, qui la sert déjà, ne change pas. La fiche
`cultes_fractions_de_pension` le déclare en une approximation à elle (version
`decret_de_2010`), avec les deux pièces de la caisse et la lettre du décret mot pour mot,
et son effet mesuré ; elle ajoute la citation de la rédaction de 2011 et trois lectures à
ses `sources`. L'effet de la fiche `taux_plein_a_soixante_cinq_ans`, qui renvoyait le point
à la file des cultes, y renvoie maintenant. **Non tranché, au propriétaire** : la pièce de
la caisse est une page d'information, non une circulaire ; si le propriétaire veut la
lettre, le changement tient en une condition de `fraction_d_avant_1998` (le taux plein de
la fraction, ou soixante-cinq ans atteints), dans les deux moteurs, et le test « deux
enfants » de `CULTES_DE_BOUT_EN_BOUT` passerait de « décote 0.9375 » à 507,73 €.

**Le cas, posé à la main.** La ministre du culte de `MINISTRE_DU_CULTE`
(`tests/test_taux_plein_a_soixante_cinq_ans.py`) : née le 15 mars 1953, ministre dès ses
vingt-six ans, en mars 1979, jusqu'en 1981 : 11 trimestres d'avant 1998, que le modèle
compte et le test écrit, tous cotisés ; sans activité de 1982 à 1999 ; ministre de 2000 à 2018 ; partie à soixante-cinq
ans, pension au 1er avril 2018 ; moins de 120 trimestres cotisés en tout. Hors de la
mesure des parents :

- l'âge d'annulation de la décote de sa génération, 66 ans et 2 mois, le 15 mai 2019 :
  du 1er avril 2018, 13 mois et 14 jours, 5 trimestres au chiffre supérieur, moins que
  ceux qui lui manquent pour la durée ; coefficient 1 − 5 × 1,25 % = 0,9375 ;
- la durée maximale de sa génération, 165 trimestres (celle que le modèle applique ; le
  test la tient du décret n° 2010-1734, article 9, que cette note n'a pas relu) ;
- le maximum de 2018, 4 635,65 € par an : celui du modèle, le maximum de 1997 revalorisé
  par les coefficients de L. 161-23-1 (VIII du décret), sans l'arrondi de la caisse
  (approximation déjà déclarée à la fiche) ;
- le minimum contributif au 1er octobre 2017, 7 615,94 € par an
  (`legislation/minimum_contributif.csv`, `montant_base`, source `cnav_montants_minimum`),
  non majoré sous 120 trimestres cotisés.

Selon la caisse, et au modèle : 4 635,65 × 11 / 165 = 50 992,15 / 165 = 309,043 ; × 0,9375
= 289,728, soit **289,73 €** par an. Selon la lettre : III, 4 635,65 × 11 / 165 = 309,04 € ;
V, 100 % de l'écart (née après 1942), (7 615,94 − 4 635,65) × 11 / 165 = 2 980,29 × 11 / 165
= 32 783,19 / 165 = 198,686, soit 198,69 € ; ensemble, 7 615,94 × 11 / 165 = 83 775,34 /
165 = 507,729, soit **507,73 €**. L'écart : 507,73 − 289,73 = **218,00 €** par an. Si le
« montant du minimum de pension majoré » du V se prenait sans la condition des 120
trimestres (voir le point 2), la lettre donnerait 8 322,13 × 11 / 165 = 91 543,43 / 165 =
554,81 € : le décret ne le tranche pas, et la caisse écrit la condition.

Qui est touché, si la lettre l'emportait : les ministres et religieux dont l'âge
d'annulation de la décote passe soixante-cinq ans, partis entre soixante-cinq ans et cet
âge sans la durée requise ni la mesure des parents de trois
enfants, pour leur seule fraction d'avant 1998.

## 2. Le minimum majoré du V : servi, sans seuil avant avril 2009 depuis cette note

**Le texte.** Le V (rédaction de 2006, LEGIARTI000006256155, comme celle de 2011) majore la
fraction d'« une fraction de l'écart entre, d'une part, le maximum de pension [...] et,
d'autre part, le montant du minimum de pension majoré au titre des périodes ayant donné
lieu à cotisations à la charge de l'assuré, fixé en application des dispositions de
l'article L. 351-10 », « 100 % de l'écart pour les assurés nés après 1942 », « au prorata
du nombre de trimestres cotisés par l'assuré entre le 1er janvier 1979 et le 31 décembre
1997, rapporté au nombre de trimestres nécessaires pour atteindre la durée maximale fixée à
l'article R. 351-6 ». L. 351-10, du 1er janvier 2004 au 19 décembre 2008
(LEGIARTI000006742926) : « Ce montant minimum est majoré au titre des périodes ayant donné
lieu à cotisations à la charge de l'assuré. » La rédaction suivante (LEGIARTI000019959492,
« applicables aux pensions prenant effet à compter du 1er avril 2009 », loi n° 2008-1330,
articles 81, II, et 89, III) ajoute : « lorsque la durée d'assurance ayant donné lieu à
cotisations à la charge de l'assuré, accomplie tant dans le régime général que dans un ou
plusieurs autres régimes obligatoires, est au moins égale à une limite fixée par décret » ;
D. 351-2-2 (LEGIARTI000020090096) : « est fixée à 120 trimestres ».

**Le modèle** servait la majoration du V (`fraction_d_avant_1998`), au minimum majoré à qui
a 120 trimestres cotisés tous régimes, au minimum sinon, comme la page de la caisse l'écrit
(« si vous totalisez au moins 120 trimestres cotisés tous régimes, votre pension sera portée
au niveau du minimum contributif majoré ») ; mais il opposait ce seuil à toute date, quand
L. 351-10 ne le pose qu'aux pensions prenant effet depuis le 1er avril 2009. Le régime
général lit déjà le seuil par date (`completer.majoration_ouverte`, fiche
`minimum_contributif` : `seuil_trimestres_cotises` nul jusqu'au 31 mars 2009, 120 ensuite) ;
la fraction des cultes le lit maintenant de même, dans les deux moteurs (`cultes.py`,
`cultes.js`), sans la constante de 120.

**Le test d'abord**, `test_avant_avril_2009_le_minimum_majore_du_v_ne_demande_pas_120_trimestres`
(`tests/test_cultes.py`, par `droit_et_refait`) : vu rouge (1 855,52 €), vert après le
code ; l'ancien `cultes.js` seul le fait encore échouer. Né le 15 janvier 1943, ministre du
culte de quarante-cinq à soixante-cinq ans, pension au 1er février 2008 : 40 trimestres
cotisés de 1988 à 1997, 40 depuis, 80 en tout ; durée maximale de 150 trimestres (R. 351-6,
LEGIARTI000006749349 : « 150 trimestres pour les assurés nés avant 1944 ») ; le minimum
majoré « de façon à atteindre 7 603,41 euros par an au 1er janvier 2008 » (D. 351-2-1,
LEGIARTI000017870194), le minimum « 6 958,21 euros par an au 1er janvier 2008 » (même
article). Le maximum (4 235,28 € en 2008) se retranche : 4 235,28 × 40 / 150 + (7 603,41 −
4 235,28) × 40 / 150 = 7 603,41 × 40 / 150 = 304 136,40 / 150 = 2 027,576, soit
**2 027,58 €**, au lieu de 6 958,21 × 40 / 150 = 278 328,40 / 150 = 1 855,523, soit
1 855,52 € : 172,06 € de plus par an.

Qui est touché : les ministres et religieux nés après 1938, dont la pension a pris effet du
1er novembre 2006 au 31 mars 2009, au taux plein, avec des trimestres cotisés de 1979 à 1997
et moins de 120 trimestres cotisés tous régimes ; nés de 1939 à 1942, pour 20 % à 80 % de
l'écart. **Non fait, candidat** : depuis le 1er septembre 2023, le régime général compte
l'AVPF et l'AVA dans les 120 trimestres (`completer.avpf_retenue`, qui cite L. 351-10,
D. 351-2-2 et la circulaire Cnav 2024/28) ; le V des cultes ne les compte pas. Ces textes
n'ont pas été relus ici.

## 3. « Gratuitement » : la caisse et le Sénat le disent, non D. 721-11

D. 721-11 (LEGIARTI000006739120) et le décret n° 79-607, article 42 (LEGIARTI000006766268,
du 1er janvier 1979 au 21 décembre 1985), relu ici, disent la même chose : « Sous réserve
qu'à la date d'entrée en jouissance de la pension l'assuré soit à jour de ses cotisations
personnelles, sont prises en compte pour l'ouverture du droit et le calcul de la pension,
les périodes d'exercice d'activités mentionnées à l'article 1er de la loi du 2 janvier 1978
susvisée accomplies antérieurement au 1er janvier 1979 [...] » ; ni l'un ni l'autre ne dit
« sans cotisation ». Les deux pièces qui le disent : la page de la CAVIMAC (« Une fraction
de pension pour les périodes d'activité cultuelle réalisées avant 1979 correspondant à des
trimestres validés à titre gratuit »), que son triptyque redit (« Les trimestres sont
validés à titre gratuit avant 1979 ») ; la réponse du Gouvernement à la question orale
n° 122 de M. Auguste Cazalet, en séance le 15 janvier 2008, publiée au JO Sénat du 16
janvier 2008, p. 207 (« pour les années antérieures à 1979, qui n'ont donné lieu à aucune
cotisation et ont été validées gratuitement »). Les commentaires de
`droit/categories.py` et `categories.js`, de `droit/cultes.py` et `cultes.js`, la
docstring de `test_les_annees_cultuelles_d_avant_1979_ne_sont_pas_cotisees`, les trois
passages d'`affiliations.yaml` les citent maintenant ; la fiche les porte à ses `sources`,
et la citation de l'article 42. Aucun nom de test, aucune valeur ne change.

## Ce qui bouge

Les 931 témoins de simulation et les 85 rendus de page, refaits par
`construire_temoins.py` : aucun ne bouge. Le paquet (`moteur/donnees.json`)
et `data/derive/agregats.json`, refaits : inchangés ; le coût ne bouge pas. Aucune page.
Le cliquet des rédactions sans statut (`data/reference/textes/perimetre.yaml`) passe de
9 324 à 9 323, comme `tests/test_textes.py` le demande.

*Renvoi, le 5 novembre 2026* : rebasés à la publication, les commits fbf109d et 4052d87 que
cette note et son entrée du journal de veille citent sont, sur `main`, 62fe670 et 9dce08d ;
celui de cette note est f16bdf0.
