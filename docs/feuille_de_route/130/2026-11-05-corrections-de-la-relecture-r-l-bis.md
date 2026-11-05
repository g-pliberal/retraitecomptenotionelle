# Les corrections de la relecture R-L-bis : les âges au mois, et les biologistes d'avant 2009

File L-ter, 5 novembre 2026. La relecture R-L-bis
(`2026-11-05-relecture-corrections-r-l.md`) a trouvé deux écarts plus anciens que
le commit relu ; les voici corrigés, le test d'abord, dans les deux moteurs.

## 1. L'écart moyen : les âges écrits au centième, lus au mois

**La cause, et la classe.** La table `age_annulation_decote.csv` écrit 66,17 pour
66 ans et 2 mois (66,1667). Ce n'était pas la seule : `age_ouverture_requis.csv`
écrit 61,17 pour 61 ans et 2 mois, et de même `age_surcote_regimes_speciaux.csv`,
`age_jouissance_militaire.csv`, `ages_regimes.csv` (au millionième : 60,666667),
`categorie_active.csv`, `duree_services_actifs.csv`, `duree_services_militaires.csv`,
`carriere_longue.csv`, et les fiches de la CRPCEN (65,33, 66,67) et des assemblées
parlementaires (61,58). Une valeur écrite au-dessus du mois refuse l'âge exact : la
sonde de la session a trouvé, en plus de la décote, que l'assuré né le
10 février 1953 qui part à 61 ans et 2 mois, l'âge légal de sa génération, se voyait
**refuser l'ouverture du droit** (« non_ouverte »), au régime général comme à la
CNAVPL. Un chargeur, `au_mois` (`donnees/chargement.py`), ramène désormais au mois
entier le plus proche tout âge et toute durée en années que lisent les tables de la
législation (colonne `age` des tables par génération, `AgesRegimes`,
`AgesCategorieActive`, les deux durées de services, `CarriereLongue`) et les
fiches de régime (`age_ouverture`, `age_taux_plein`). Le paquet est fait de ces
chargeurs : le portage lit les mêmes valeurs, 66,16666666666667 et non 66,17.

**Les textes, lus dans la session** (index LEGI à jour au 2 novembre 2026, JORF au
3 novembre, récupérés pour elle ; l'accord de l'Agirc-Arrco, sur le site de la
fédération) :

- L. 351-8, LEGIARTI000028498855 (« applicable aux pensions prenant effet à compter
  du 1er février 2014 », jusqu'au 1er septembre 2023) : « Bénéficient du taux plein
  même s'ils ne justifient pas de la durée requise [...] : 1° Les assurés qui
  atteignent l'âge prévu à l'article L. 161-17-2 augmenté de cinq années ».
- D. 161-2-1-9, LEGIARTI000025089933 (du 31 décembre 2011 au 1er septembre 2023) :
  « 2° Soixante ans et quatre mois pour les assurés nés entre le 1er juillet 1951 et
  le 31 décembre 1951 inclus ; 3° Soixante ans et neuf mois pour les assurés nés en
  1952 ; 4° Soixante et un ans et deux mois pour les assurés nés en 1953 ;
  5° Soixante et un ans et sept mois pour les assurés nés en 1954 ; 6° Soixante deux
  ans pour les assurés nés à compter du 1er janvier 1955 ». L. 161-17-2,
  LEGIARTI000025014605, le renvoie au décret, « à raison de quatre mois » puis « de
  cinq mois par génération ».
- L. 351-1, LEGIARTI000023035688 : la pension est servie « à partir de l'âge
  mentionné à l'article L. 161-17-2 ».
- R. 351-27, LEGIARTI000024113020 (du 3 juin 2011 au 1er septembre 2023) : « le
  " taux plein ", soit 50 % » aux « catégories de personnes mentionnées à l'article
  L. 351-8 » ; sinon un coefficient de minoration « fonction soit du nombre de
  trimestres correspondant à la durée séparant l'âge auquel leur pension prend effet
  [...] de l'âge prévu au 1° de l'article L. 351-8, soit du nombre de trimestres
  supplémentaires qui leur serait nécessaire [...] Le plus petit de ces deux nombres
  est pris en considération » ; « 1,25 % pour l'assuré né après 1952 ».
- R. 643-7, LEGIARTI000024113055 (du 3 juin 2011 au 5 mars 2023), à la CNAVPL : la
  même durée, jusqu'à « l'âge prévu au 1° de l'article L. 351-8 » ; « Le
  coefficient de minoration est égal à 1,25 % par trimestre manquant dans la limite
  de vingt trimestres ».
- Statuts de la CAVP, prestations des biologistes, article 14 (arrêté du
  23 juin 2011, JORFARTI000024270214) : « La prestation supplémentaire de vieillesse
  est alors réduite par application d'un coefficient d'anticipation qui est fonction
  du nombre de trimestres manquants, à la date d'effet des droits, pour atteindre
  l'âge fixé à l'article L. 351-8 (1°) du code de la sécurité sociale. Ce
  coefficient est égal à 1,25% par trimestre manquant dans la limite de vingt
  trimestres ».
- Accord national interprofessionnel du 17 novembre 2017, version « Applicable au
  1 janvier 2019 », article 84 : « 1. Le participant peut bénéficier de sa pension au
  titre du présent régime sans abattement dès lors qu'il a atteint l'âge visé au 1°
  de l'article L. 351-8 du code de la sécurité sociale » ; la table du 2 finit à
  « moins 1 trimestre 0,99 ».

**Les valeurs attendues, à la main.** Né le 10 février 1953, l'assuré a 66 ans et
2 mois le 10 avril 2019, et part le 1er mai 2019. L'âge du 1° de L. 351-8 est
61 ans 2 mois + 5 ans = 66 ans 2 mois. Trimestres manquants pour l'atteindre :
(66 + 2/12 − 66 − 2/12) × 4 = 0. Débutant à 26 ans, il a 160 trimestres pour 165 :
la durée ne lui donne rien, l'âge tout. Donc :

| Régime | Texte | Attendu | Servi avant | Servi après |
|---|---|---|---|---|
| Régime général | R. 351-27, 1° | taux 50 % | 49,375 % = 50 × (1 − 1,25 %) | 50 % |
| CNAVPL | R. 643-7 | 1 − 1,25 % × 0 = 1 | 0,9875 | 1 |
| ASV des biologistes | statuts, art. 14 | 1 − 1,25 % × 0 = 1 | 0,9875 | 1 |
| Agirc-Arrco, Arrco, Agirc | ANI de 2017, art. 84, 1 | sans abattement | 0,99 | aucun coefficient |

Avant, (66,17 − 66,1667) × 4 = 0,0133, arrondi au millième puis au trimestre
supérieur : 1 trimestre. L'ouverture : à 61 ans et 2 mois (1er mai 2014) le droit
s'ouvre (L. 351-1 et D. 161-2-1-9, 4°) ; à 61 ans et 1 mois, non. Avant, refusé aux
deux.

Les autres générations, vérifiées aux mêmes âges exacts : 65 ans 4 mois (juillet
1951), 65 ans 9 mois (1952), 66 ans 7 mois (1954), 67 ans (1955) : taux plein,
aucun coefficient à la CNAVPL ni à l'ASV, et à l'Agirc-Arrco pour les pensions
d'après le 1er janvier 2019 (1953, 1954, 1955 ; celles de 1951 et 1952 relèvent de
la convention de 1947 et de l'accord Arrco, non relus ici, et le test ne les
affirme pas). Le droit s'ouvre à 60 ans 4 mois, 60 ans 9 mois, 61 ans 2 mois,
61 ans 7 mois et 62 ans, et pas un mois avant. Ces 65,33 et 66,58 tombaient sous le
mois, sans effet sur ces cas ; seuls 61,17 et 66,17 le dépassaient.

**Les tests.** `tests/test_ages_au_mois.py`, vu rouge (7 échecs : les trois
valeurs, l'ouverture à 61 ans 2 mois dans les deux statuts, et les trois relevés
« chaque âge tombe sur un mois entier » — tables par génération, autres tables,
fiches de régime), puis vert, 23 cas par `servi_et_refait` et les relevés. Six
attentes de `tests/test_simulateur.py` écrivaient le centième (`approx(60.33)`,
`approx(66.17)`…) : elles écrivent désormais le mois du texte que leur commentaire
cite (`60 + 4 / 12`).

## 2. L'écart faible : les biologistes d'avant 2009, minorés jusqu'à 65 ans

**Le texte.** R. 351-27, de sa rédaction du 21 décembre 1985 à celle qui court
jusqu'au 3 juin 2011 (LEGIARTI000006749434, LEGIARTI000006749435,
LEGIARTI000006749436, LEGIARTI000020082993) : « l'âge prévu au 1° de l'article
L. 351-8 est fixé à soixante-cinq ans », quand L. 351-8 visait « 1°) les assurés qui
atteignent un âge déterminé » (LEGIARTI000006742633, du 22 août 2003 au
1er juillet 2011). Les soixante-sept ans du guide de la CNAVPL de 2025 sont l'âge du
même 1° depuis la loi n° 2010-1330 : aucun texte ne les opposait avant.

**Ce que le texte ne tranche pas.** Le décret n° 81-1046, article 2
(LEGIARTI000006768391), laisse « le montant, les modalités de calcul et
d'attribution » au règlement. Les statuts d'avant 2011 ne sont pas au Journal
officiel : l'index JORF n'a, avant 2011, que l'arrêté du 11 mai 2009
(JORFARTI000020694605), qui approuve les statuts généraux, de base et
complémentaires de la CAVP, non ceux des prestations des biologistes. Que ces
statuts aient renvoyé au 1° de L. 351-8, comme ceux de 2011, reste une présomption,
déclarée dans la fiche du régime et dans `asv_autres_professions_de_sante` ; le
coefficient de 1,25 % l'était déjà. Elle remplace une présomption anachronique.

**Les valeurs, à la main** (né le 10 février, parti au 1er mars ;
c = 1 − 1,25 % × min(20, trimestres)) :

| Né en | Part à | Effet | 65 − âge | c attendu | Servi avant |
|---|---|---|---|---|---|
| 1943 | 62 ans | 2005 | 12 trimestres | 0,85 | 0,7875 |
| 1941 | 64 ans | 2005 | 4 | 0,95 | 0,8875 |
| 1940 | 65 ans | 2005 | 0 | 1 | 0,9375 |
| 1946 | 62 ans | 2008 | 12 | 0,85 | 0,7875 |

Le modèle servait, non les 0,75, 0,85 et 0,90 des 67 ans, mais la durée quand elle
manquait de moins (17, 9 et 5 trimestres), comme il le fait par défaut
(`decote_annulee_par_la_duree`, point 5 de la relecture). À 65 ans, l'âge en oppose
moins dans les quatre cas : la durée ne les décide plus. Les périodes 1981-2007 et
2008 de `asv_directeurs_laboratoire.yaml` portent `age_taux_plein: 65`. Le test,
`test_avant_2009_le_biologiste_est_minore_jusqu_a_soixante_cinq_ans`
(`tests/test_ouverture_des_liberaux.py`), vu rouge puis vert.

## 3. Ce qui bouge

Mesuré dans la session, paquet et témoins refaits (GitHub les refait à son tour) ;
les fichiers fabriqués de `HEAD`, refaits dans un arbre à part, étaient à jour :
tout ce qui bouge vient de la correction.

- **Témoins** : 13 sur 930, et aucune pension, dans aucun des six scénarios. Douze ne
  changent que l'écriture de `age_ouverture_opposable` (61,166667 →
  61,166666666666664). Le treizième, `comedie_francaise_generation_1958_apres_soixante_ans`
  (né le 15 janvier 1958, départ en octobre 2018, à 60 ans et 8 mois, l'âge que
  `ages_regimes.csv` donne à sa génération, 60,666667, d'après le décret n° 68-960,
  article 51, lu le 13 octobre 2026 et non relu ici), passe de « non_ouverte » à
  « age_legal » :
  `scripts/construire_temoins.py` le décrit comme ouvrant son droit « en septembre
  2018 » ; la table, au millionième au-dessus du mois, le lui refusait.
- **Coût** (`data/derive/agregats.json`, `equilibre.json`) : 1,1 × 10⁻⁵ au plus en
  valeur relative sur le coût, la dette et les soldes ; les départs anticipés des
  longues carrières, aux avantages, 1 952,8 → 1 947,2 en 2014 (−0,29 %) et
  2 663,7 → 2 669,3 en 2015 (+0,21 %), les générations 1953 et 1954 partant au mois
  exact ; les catégories classées −0,09 % en 2014 ; la carrière type
  `agent_sncf_conduite|1970`, −0,2435 → −0,2434 au notionnel libéral.
- **Pages** : 6 rendus sur 85 — avantages, cout, cout_cascade_horizon,
  cout_cascade_hors_liste, cout_flux_horizon, cout_solde_vise.
- **Chiffres ancrés** : `verifier_prose.py --corriger` porte le cumul passé des
  scénarios 2, 4 et 6 du README de 2 762 à 2 763 et de 6 385 à 6 386 Md €, à
  l'arrondi ; la session n'a pas départagé sa correction des commits que GitHub n'a
  pas encore refaits, et laisse ces chiffres à GitHub.

## 4. Ce qui reste

- `ages_reference.csv`, l'âge de référence de la proposition par année, écrit aussi
  au centième (61,17, 66,17…), lu par `moteur/age_reference.py` : hors du
  scénario 1 et de cette zone, non corrigé.
- La durée qui efface la minoration des biologistes, que les statuts ne prévoient
  pas (relecture R-L-bis, point 5) : à la file du modèle.
- Les statuts des prestations des biologistes d'avant 2011, à demander à la CAVP.
