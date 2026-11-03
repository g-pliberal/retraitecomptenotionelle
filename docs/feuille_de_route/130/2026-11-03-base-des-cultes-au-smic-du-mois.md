# La base des cultes au SMIC de chaque mois

**La demande.** Le 3 novembre 2026, la session d'orchestration confie à la
file M5 la décision 13 du propriétaire : compter la base forfaitaire des cultes
au SMIC de chaque mois et, si la pratique de la caisse se lit, avec la garantie
mensuelle de rémunération de 2002 au 30 juin 2005. Les deux écarts venaient de
la file E (`2026-11-03-carte-des-fiches-cultes-lus-au-droit.md`). Le premier
est comblé ; le second ne l'est pas, faute d'un document qui tranche.

## Ce qui est lu

- **Les articles, à chaque version**, dans l'index LEGI à jour du 2 novembre
  2026 (`dila_cherche.py legi --num … --diff`) : R. 721-29 et R. 721-30, du
  21 juin 1998 au 26 février 2004, « La base forfaitaire […] est égale, par
  mois, à 169 fois le montant du salaire minimum de croissance » (mot pour mot
  au 29 décembre 1999) ; du 26 février 2004 au 1er novembre 2006, « égale, par
  mois, à la valeur horaire du salaire minimum de croissance en vigueur,
  multipliée par le nombre légal d'heures de travail mensuel en vigueur. A
  titre transitoire, du 1er janvier 2002 jusqu'au 30 juin 2005, cette base est
  augmentée de la valeur de la garantie mensuelle de rémunération la plus
  élevée […] » ; R. 382-89 et R. 382-90, leur seule version depuis le
  1er novembre 2006, dans les mêmes termes. Toutes disent « par mois ».
- **Les relèvements du SMIC**, un à un dans l'index JORF à jour du 3 novembre
  2026 : ceux que l'index LEGI porte (`dila_legi_smic.py`, 1997 à 2017), et ce
  qu'il ne porte pas, les arrêtés de l'article L. 3231-5 du code du travail et
  les textes d'après 2017. Vingt et un relèvements hors d'un 1er janvier, de
  1998 à 2026, chacun avec son identifiant dans l'en-tête de
  `macro/smic_horaire_releves.csv` et dans `tests/test_cultes_smic_du_mois.py` :
  chaque 1er juillet de 1998 à 2009 (« A compter du 1er juillet 1998 […] porté
  à 40,22 F de l'heure en métropole », décret n° 98-518), le 1er mai 2008
  (« 8,63 € de l'heure », arrêté du 25 avril 2008), le 1er décembre 2011
  (« 9,19 € de l'heure », arrêté du 29 novembre 2011), le 1er juillet 2012
  (décret n° 2012-828, 9,40 €), le 1er octobre 2021 (10,48 €), les 1er mai et
  1er août 2022 (10,85 € et 11,07 €), le 1er mai 2023 (11,52 €), le
  1er novembre 2024 (décret n° 2024-951, 11,88 €), le 1er juin 2026 (12,31 €).
  Les décrets de chaque 1er janvier de 2018 à 2026 redonnent, au centime,
  `smic_horaire.csv`. L'article 3 du décret n° 2001-554 (JORFARTI000002428309)
  fixe le SMIC à « 6,67 Euro de l'heure » au 1er janvier 2002 : le texte que
  l'en-tête de `smic_horaire.csv` dit absent.
- **La pratique de la caisse.** Circulaire de la CAVIMAC n° 2024/01 du
  10 janvier 2024 : les assiettes forfaitaires « vieillesse et retraite
  complémentaire obligatoire des cultes » sont « modifiées […] afin de tenir
  compte du relèvement du montant brut du [SMIC] […] (montant mensuel arrondi
  à 1 767 €) ». Circulaire n° 2025/01 du 14 janvier 2025 (une image, lue page
  1), « Cotisations et contributions sociales applicables à compter du 1er
  novembre 2024 (échéance au 15 décembre 2024) » : « A compter du 1er novembre
  2024, le montant brut du [SMIC] […] est porté à 1 802 € mensuels […]. A la
  suite de cette revalorisation du SMIC, les assiettes forfaitaires
  respectives des cotisations mensuelles d'assurance maladie – maternité –
  invalidité, vieillesse et retraite complémentaire obligatoire des cultes […]
  sont modifiées à compter de l'échéance du 15 décembre 2024 », celle du mois
  de novembre (« échéances des 10 et 15 février 2024 », « au titre du mois de
  janvier 2024 », n° 2024/01). L'exposé « Cultes » de la base de la Cnav
  (24 octobre 2025), lu par l'API du site : « une base forfaitaire mensuelle
  égale au Smic multiplié par le nombre légal d'heures de travail en vigueur ».
- **La garantie de 2002 à 2005**, cherchée sans réponse : le décret n° 2004-181
  (visas et articles, dont la même clause pour la maladie) ; l'article 66 de la
  loi n° 2001-1246 qu'il vise, qui ne parle pas de la base ; l'exposé de la
  Cnav ; deux recherches sur le web ; les circulaires de la CAVIMAC en ligne,
  qui commencent en 2020.
- **La classe, pas le cas** : les forfaits des non-salariés agricoles, qui
  lisent aussi un repère en heures de SMIC, disent « le montant du salaire
  minimum de croissance en vigueur au 1er janvier de l'année considérée »
  (décrets n° 90-498, 94-690 et 2001-584, dans l'index LEGI) : le SMIC de
  janvier y est le bon, rien n'est à étendre.

## Ce qui est fait

- **Le test d'abord**, vu rouge pour la raison attendue des deux côtés :
  `tests/js/cultes-smic-du-mois.test.js` (le portage, qui fait foi ; ni
  `smicHoraireDesMois` ni `smic_du_mois`) et son pendant
  `tests/test_cultes_smic_du_mois.py`, qui recoupe aussi chaque ligne du
  fichier des relèvements à son texte.
- **La donnée** : `macro/smic_horaire_releves.csv` porte les vingt et un
  relèvements, et non plus le seul dernier ; la projection n'en lit toujours
  que le dernier de la dernière année du barème, rien d'autre n'y bouge.
- **Le code, dans les deux moteurs**, au bit près des témoins : un drapeau de
  période, `smic_du_mois`, sur les périodes de la CAVIMAC depuis 1998 et sur
  toutes celles de l'Arrco des cultes, qui prélève sur la même assiette
  (circulaire n° 2025/01) ; `smicHoraireDesMois` et `smic_horaire_des_mois`,
  la moyenne des douze mois du barème de janvier et des relèvements, le SMIC de
  janvier au bit près sans relèvement ; `smicHoraireDuForfait`, que lisent le
  salaire porté au compte (`assietteDeReference`), l'assiette des droits
  (`acquerir`), le compte notionnel (`compte.js`) et le forfait des
  contributions d'équilibre. Le paquet porte le drapeau et la liste.
- **Les tests qui posaient le SMIC de janvier** sur ce forfait, récrits avec
  les SMIC des mois, posés à la main : la cotisation de 2000
  (`test_cultes.py`), la CEG de 2022 (`test_contributions_equilibre.py`), les
  points Arrco d'un ministre du culte (`test_simulateur.py` et
  `moteur.test.js`) ; `test_cultes_au_droit.py` ne tient plus que l'écart de
  la garantie, et mesure ce que la règle relève.
- **Les fiches** : `cultes_salaire_annuel_moyen` perd l'approximation du SMIC
  de janvier, en gagne une plus petite (l'arrondi à l'euro de la caisse,
  l'année incomplète à la moyenne de ses mois), cite les lectures du jour et
  dit la garantie cherchée sans réponse ; `cultes_retraite_complementaire` lit
  `smic_du_mois`. La partie 4 des limites le dit.

## Les calculs posés à la main

La base d'une année entière est la somme de ses douze mois, heures du mois
fois SMIC du mois : 169 heures jusqu'en 2001, 1 820 / 12 depuis.

| Année | Le SMIC de chaque mois | Base de l'année | Au SMIC de janvier |
|---|---|---|---|
| 1999 | 40,22 F de janvier à juin, 40,72 F ensuite | 169 × (6 × 40,22 + 6 × 40,72) = 82 073,16 F, 12 511,97 € | 12 434,68 € |
| 2007 | 8,27 € de janvier à juin, 8,44 € ensuite | 1 820 / 12 × (6 × 8,27 + 6 × 8,44) = 15 206,10 € | 15 051,40 € |
| 2008 | 8,44 € jusqu'en avril, 8,63 € en mai et juin, 8,71 € ensuite | 1 820 / 12 × (4 × 8,44 + 2 × 8,63 + 6 × 8,71) = 1 820 / 12 × 103,28 = 15 664,13 € | 15 360,80 € |
| 2016 | 9,67 € toute l'année | 1 820 × 9,67 = 17 599,40 € | la même |
| 2022 | 10,57 € jusqu'en avril, 10,85 € de mai à juillet, 11,07 € ensuite | 1 820 / 12 × 130,18 = 19 743,97 € | 19 237,40 € |
| 2024 | 11,65 € jusqu'en octobre, 11,88 € ensuite | 1 820 / 12 × 140,26 = 21 272,77 € | 21 203,00 € |

La caisse, qui arrondit l'assiette du mois à l'euro, appelle en 2024
10 × 1 767 + 2 × 1 802 = 21 274 € : 1,23 € de plus que le modèle, l'écart
déclaré.

- **La cotisation de 2000** : 169 × (6 × 40,72 + 6 × 42,02) F / 6,55957, fois
  le taux de la période.
- **La CEG de 2022** : 2,15 % de 1 820 / 12 × (4 × 10,57 + 3 × 10,85 +
  5 × 11,07) = 19 743,97 €, 424,50 €.
- **Les points Arrco** d'un ministre du culte né le 1er janvier 1961, parti à
  soixante-cinq ans, de 2006 à 2025 : chaque année, 1 820 heures au SMIC de
  ses mois, au taux de cotisation de la période (7,5 % jusqu'en 2013, 7,625 %
  en 2014, 7,75 % jusqu'en 2018, 7,87 % depuis), divisé par le taux d'appel
  (1,25, puis 1,27) et par le salaire de référence de l'année
  (`valeurs_point.csv`). Le même calcul, au SMIC de janvier, refait l'ancien
  total, 1 348,24 points ; au SMIC des mois, 1 355,82, que les deux moteurs
  rendent. 2022 y gagne le plus, 2,6 %.
- **Ce que la règle relève**, de 1998 à 2026 : la moitié du relèvement de
  juillet de 1998 à 2009, au plus 2,9 %, en 2004 ((7,19 + 7,61) / 2 / 7,19).

## L'effet

Quinze témoins de simulation bougent, tous des cultes, à la hausse ; aucun
rendu de page ne change (`resumer_temoins.py`), ni les agrégats du paquet.
Au scénario 1, douze témoins, de +0,11 € à +4,08 € par mois : de +0,01 %
(`statut_membre_congregation_1965`, 1 017,26 €) à +0,77 %
(`cultes_taux_minore`, 323,85 € à 326,34 €), +3,64 € pour
`statut_ministre_du_culte_1945` (+0,54 %), +4,08 € pour
`statut_ministre_du_culte_1955` (+0,48 %), +1,28 € pour
`statut_ministre_du_culte` (1 591,65 €, +0,08 %, par l'Arrco seule). Aux
comptes notionnels, jusqu'à +5,08 € par mois (`statut_ministre_du_culte`,
+0,51 %) et +0,95 % (`statut_ministre_du_culte_1945`). Le paquet passe de
5 873 à 5 894 Ko bruts.

## Ce que l'étape laisse

- **La garantie mensuelle de rémunération**, de 2002 au 30 juin 2005, non
  codée : aucun texte ni document de la caisse lu ne dit si la base était
  relevée jusqu'à la garantie la plus élevée (au plus le SMIC de cent
  soixante-neuf heures, 11 % de plus que la durée légale) ou si la garantie
  s'y ajoutait entière (près du double). Une circulaire de la CAVIMAC de 2002
  à 2005, ou un relevé de carrière de ces années, le dirait.
- **L'arrondi à l'euro** de l'assiette du mois, que la caisse pratique, et
  **l'année incomplète**, comptée à la moyenne de ses douze mois : la ligne de
  la carrière ne dit pas ses mois. Moins de 0,03 % pour l'un, au plus 2,9 % de
  la base de l'année d'entrée ou de départ pour l'autre.
- **Le SMIC de 2002**, `haute` dans `smic_horaire.csv` faute de texte : le
  texte est l'article 3 du décret n° 2001-554 ; une session des données peut le
  certifier.
- Le premier semestre de 1998, avant le décret du 17 juin 1998, reste au
  forfait de toute l'année, comme la fiche le déclarait.

## Ce qui attend le propriétaire

Une question : la garantie de 2002 à 2005 se compte-t-elle en relevant la base
jusqu'à elle, ou en l'ajoutant ? Sans document de la caisse, la règle n'est pas
écrite ; un ministre du culte qui a cotisé ces années, ou la CAVIMAC, peut le
dire.

*Renvoi du 3 novembre 2026, après la relecture R-M5.* Quatre phrases de cette
note sont corrigées dans `2026-11-03-retouches-de-la-relecture-r-m5.md` : 2025
n'a pas de décret du 1er janvier (point 3) ; la circulaire n° 2025/01 a une
couche de texte, et son tableau dit « à compter du 1er janvier 2025 » (point 4) ;
les 11 % de la garantie sont une estimation, que l'article 32 n'écrit pas
(point 5) ; le décret n° 2001-584 dit « celui en vigueur au 1er janvier de
l'année au titre de laquelle les cotisations sont dues » (point 6).
