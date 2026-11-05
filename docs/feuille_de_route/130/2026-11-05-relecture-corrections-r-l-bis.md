# Relecture des corrections de R-L-bis : les âges au mois, les biologistes d'avant 2009

File R-L-ter, vague 7, le 5 novembre 2026 : relecture indépendante du commit f6012e5
(file L-ter), de sa note `2026-11-05-corrections-de-la-relecture-r-l-bis.md` et de son
journal de veille, qui corrigent la relecture R-L-bis
(`2026-11-05-relecture-corrections-r-l.md`). Lecture seule : aucune règle, aucune donnée,
aucun test n'est touché. Chaque texte a été rouvert dans l'index de la DILA récupéré dans
la session (LEGI à jour au 2 novembre 2026, JORF au 3 novembre) ; l'accord de
l'Agirc-Arrco, téléchargé du site de la fédération
(`agirc-arrco.fr/storage/2024/09/201809dc_ANI_du_17_novembre_2017.pdf`). Chaque âge a été
reconverti en ans et en mois à la main, puis confronté à son texte.

**Verdict : conforme ; trois écarts faibles, aucun moyen ni grave.** Les citations sont
exactes, les âges en mois des neuf tables et des deux fiches sont ceux des textes, la
correction passe dans les deux moteurs, les treize témoins bougent pour elle seule. Les
écarts : une période de quatre ans sans texte cité (point 4), un relevé incomplet de ce
qui bouge (point 5), et `ages_reference.csv`, qui porte le même défaut, sans effet sur
le scénario par défaut (point 6).

## 1. Les textes cités : exacts

| Texte | Identifiant, version | Constat |
|---|---|---|
| L. 351-8, 1° | LEGIARTI000028498855, 22 janvier 2014 → 1er septembre 2023 | exact, mention d'application au 1er février 2014 comprise : « 1° Les assurés qui atteignent l'âge prévu à l'article L. 161-17-2 augmenté de cinq années » |
| L. 351-8, 1° | LEGIARTI000006742633, 22 août 2003 → 1er juillet 2011 | exact : « 1°) les assurés qui atteignent un âge déterminé » ; les mêmes mots dans la rédaction d'avant, LEGIARTI000006742632 (21 décembre 1985 → 22 août 2003) |
| D. 161-2-1-9 | LEGIARTI000025089933, 31 décembre 2011 → 1er septembre 2023 | exact, du 2° au 6° |
| L. 161-17-2 | LEGIARTI000025014605 | exact : « A raison de quatre mois par génération », « A raison de cinq mois par génération » |
| L. 351-1 | LEGIARTI000023035688 | exact : « à partir de l'âge mentionné à l'article L. 161-17-2 » |
| R. 351-27 | LEGIARTI000024113020, 3 juin 2011 → 1er septembre 2023 | exact ; l'ellipse « [...] » ôte « de leur soixante-cinquième anniversaire, s'ils remplissent les conditions prévues au 1° bis ou 1° ter [...] ou, dans le cas contraire, », sans changer le sens pour l'assuré qui ne les remplit pas ; « 1,25 % pour l'assuré né après 1952 » |
| R. 351-27 | LEGIARTI000006749434, 006749435, 006749436, 020082993 (21 décembre 1985 → 3 juin 2011) | les quatre rédactions portent « l'âge prévu au 1° de l'article L. 351-8 est fixé à soixante-cinq ans » |
| R. 643-7 | LEGIARTI000024113055, 3 juin 2011 → 5 mars 2023 | exact, « dans la limite de vingt trimestres » compris |
| Statuts de la CAVP, art. 14 | JORFARTI000024270214 (arrêté du 23 juin 2011) | exact, mot pour mot |
| Arrêté du 11 mai 2009 | JORFARTI000020694605 | son titre ne vise que les statuts généraux, de base et complémentaires de la CAVP, comme la note le dit |
| Décret n° 81-1046, art. 2 | LEGIARTI000006768391, 1er juillet 1981 → 26 avril 2007 | exact : « le montant, les modalités de calcul et d'attribution » |
| ANI du 17 novembre 2017, art. 84, 1 | PDF de la fédération, page 51, « applicable au 1er janvier 2019 » | exact : « sans abattement dès lors qu'il a atteint l'âge visé au 1° de l'article L. 351-8 » |

Un fait de plus, qui soutient la présomption de la note sans la lever : l'arrêté de 2011
approuve « des modifications apportées [...] aux statuts des prestations complémentaires
de vieillesse des directeurs de laboratoire » ; ces statuts existaient donc avant, et
c'est leur texte qui manque au Journal officiel.

## 2. Les âges en mois, table par table : conformes

Le relevé de toutes les colonnes d'âge et de durée des tables de
`data/reference/legislation/` et de toutes les clés d'âge des YAML de `data/reference/`
trouve hors du mois exactement les neuf tables et les deux fiches de la note, et
`ages_reference.csv` (point 6) ; aucun âge écrit en dur dans `src/` ni `moteur/js/`.
Chaque valeur, reconvertie ; « au-dessus » marque celles qui refusaient l'âge exact :

- `age_ouverture_requis.csv` : 1951,5 60,33 → 60 ans 4 mois ; 1953 61,17 → 61 ans
  2 mois, au-dessus ; 1954 61,58 → 61 ans 7 mois. D. 161-2-1-9, 2°, 4° et 5° : conforme.
- `age_annulation_decote.csv` : 65,33, 66,17 (au-dessus), 66,58 : les mêmes, cinq ans
  de plus (L. 351-8, 1°) : conforme.
- `categorie_active.csv` : active, 1956,5 55,33 et 60,33, 1958 56,17 et 61,17
  (au-dessus), 1959 56,58 et 61,58 ; super-active, 1961,5 50,33 et 55,33, 1963 51,17 et
  56,17 (au-dessus), 1964 51,58 et 56,58. Décret n° 2011-2103, article 2
  (LEGIARTI000025100416) : « Du 1er juillet 1956 au 31 décembre 1956 55 ans et 4 mois
  1957 55 ans et 9 mois 1958 56 ans et 2 mois 1959 56 ans et 7 mois », et « Du 1er juillet
  1961 au 31 décembre 1961 50 ans et 4 mois 1962 50 ans et 9 mois 1963 51 ans et 2 mois
  1964 51 ans et 7 mois » ; l'âge d'annulation suit le pas de l'article 8
  (LEGIARTI000025100429), quatre mois puis cinq : conforme.
- `duree_services_actifs.csv` : 15,33, 16,17 (au-dessus), 16,58 ; 25,33, 26,17
  (au-dessus), 26,58. Article 6 (LEGIARTI000025100424) : « 15 ans et 4 mois [...] 16 ans
  et 2 mois 2014 16 ans et 7 mois », et de même à vingt-cinq ans : conforme.
- `duree_services_militaires.csv` : les mêmes. Article 4 (LEGIARTI000025100420) :
  « + 4 mois », « + 1 an et 2 mois », « + 1 an et 7 mois » : conforme.
- `age_jouissance_militaire.csv` : 1961,5 50,33, 1963 51,17 (au-dessus), 1964 51,58 ;
  aucun tableau propre aux militaires, la table prend le pas de l'article 8, et le
  déclare (`estimee`, en tête du fichier) : conforme à ce qu'elle déclare.
- `age_surcote_regimes_speciaux.csv` : 1957 60,33, 1958 60,67 (au-dessus), 1960 61,33,
  1961 61,67 (au-dessus) : quatre mois par génération, ceux du décret n° 2008-637,
  article 51-1 (LEGIARTI000023732424 : « soixante ans et huit mois pour les agents nés
  en » 1958) : conforme.
- `ages_regimes.csv` : 69 âges d'ouverture et 53 âges du taux plein hors du mois, tous
  au pas de quatre mois (SNCF, RATP, IEG, CRPCEN, CARPIMKO, Mayotte, Comédie-Française)
  ou de quatre puis cinq (assemblées, Saint-Pierre-et-Miquelon), un sur la CPRN
  (1954 : 63 ans 7 mois et 68 ans 7 mois). Rouverts au texte : la Comédie-Française,
  décret n° 68-960, article 51, I, A et B (LEGIARTI000029134323, en vigueur depuis le
  1er janvier 2017 : « 3° A soixante ans et huit mois pour les assurés nés en 1958 »,
  puis 61 ans 4 mois, 61 ans 8 mois, 55 ans 4 mois…) ; la SNCF et la RATP à 50 ans
  4 mois pour 1967 (décret n° 2008-639, article 37-1, LEGIARTI000029165223 ; décret
  n° 2008-637, article 51-1, LEGIARTI000029137528). Les autres, reconvertis seulement :
  écrits au centième ou au millionième, ils ne laissent qu'un mois possible, à
  0,06 mois près, et `au_mois` ne peut pas les porter sur un autre.
- `carriere_longue.csv` : 59 ans 4 mois, 58 ans 4 mois, 59 ans 8 mois (au-dessus),
  58 ans 8 mois (au-dessus), 56 ans 4 mois, 56 ans 8 mois (au-dessus), 57 ans 4 mois,
  57 ans 8 mois (au-dessus), aux deux dates d'effet de 2011 et 2012 : ce sont les âges
  de D. 351-1-1 (LEGIARTI000023397567, 1er juillet 2011 → 1er novembre 2012) ; la ligne
  de septembre 2026 (né en décembre 1965, 60,67, au-dessus) : « soixante ans et huit
  mois » pour les « assurés nés entre le 1er décembre et le 31 décembre 1965 inclus »
  (LEGIARTI000054059621) : conforme.
- Les fiches : `crpcen.yaml`, périodes 9 à 14, 60 ans 4 mois et 65 ans 4 mois, 60 ans
  8 mois et 65 ans 8 mois (au-dessus), 61 ans 4 mois et 66 ans 4 mois, 61 ans 8 mois et
  66 ans 8 mois (au-dessus), le pas de sa table `crpcen_2011` ;
  `assemblees_parlementaires.yaml`, période 2, 61,58, 61 ans 7 mois (D. 161-2-1-9,
  5°) : conforme.

## 3. Les deux moteurs : conformes

`au_mois` (`donnees/chargement.py`) est appelé partout où ces valeurs se lisent : la
colonne `age` de `charger_table_par_generation` (âges d'ouverture, dont ceux d'avant la
réforme de 2023 et d'avant la suspension, d'annulation, de surcote, de jouissance
militaire), `AgesRegimes` (ouverture, taux plein, `age_surcote_maximum`),
`AgesCategorieActive` (ses trois champs), `DureesServicesMilitaires` et sa fille
`DureesServicesActifs`, `CarriereLongue.age_depart`, `CatalogueRegimes` (`age_ouverture`,
`age_taux_plein`). Le portage lit le paquet que ces chargeurs fabriquent
(`scripts/construire_donnees.py`) : dans `moteur/donnees.json`, `ages_annulation_decote`
donne 66,16666666666667 pour 1953, et les seuls âges légaux encore hors du mois sont les
séries `age_reference` et `age_taux_plein_legal`, de `ages_reference.csv`.

Les valeurs, refaites à la main. Né le 10 février 1953, parti le 1er mai 2019 à 66 ans
2 mois : (66 + 2/12) − (61 + 2/12 + 5) = 0 trimestre ; régime général 50 %, CNAVPL et
ASV 1 − 1,25 % × 0 = 1, Agirc-Arrco sans abattement ; l'ouverture à 61 ans 2 mois, et
non à 61 ans 1 mois. Les biologistes d'avant 2009, nés le 10 février, partis le
1er mars : en 1943 à 62 ans (2005), 65 ans le 10 février 2008, soit 2 ans 11 mois
9 jours, 11,77 trimestres, 12 au trimestre supérieur (déclaré) ou en mois entiers,
0,85 ; en 1941 à 64 ans, 4 trimestres, 0,95 ; en 1940 à 65 ans, 0, 1 ; en 1946 à
62 ans (2008), 12, 0,85. Ce sont les valeurs des tests.

`tests/test_ages_au_mois.py` et
`test_avant_2009_le_biologiste_est_minore_jusqu_a_soixante_cinq_ans` : 24 tests verts,
24 aussi sous `PRESOMPTIONS_DECALEES=1`, chaque cas servi par le portage et refait par le
moteur Python (`servi_et_refait`). La garde décale le jour de naissance, les enfants et
le mariage ; les cas écrivent leur jour, le 10 : elle ne les déplace pas, comme
attendu. Les six attentes de `tests/test_simulateur.py` passent du centième au mois que
leur commentaire cite : légitime, la valeur vient du texte.

## 4. Ce que le texte ne tranche pas : déclaré, sauf quatre ans

La présomption des statuts des biologistes d'avant 2011 est déclarée dans la fiche du
régime et dans `asv_autres_professions_de_sante.yaml` ; les complémentaires des
générations 1951 et 1952, sous la convention de 1947 et l'accord Arrco, non relues, sont
dites dans la note et laissées hors du test. Conforme.

**Écart faible.** La période de `asv_directeurs_laboratoire.yaml` qui porte désormais
`age_taux_plein: 65` s'ouvre en 1981 (`debut: 1981`) ; le texte qu'elle cite, R. 351-27,
« toutes ses rédactions du 21 décembre 1985 au 3 juin 2011 », ne commence qu'en
décembre 1985. Pour une prestation prise d'effet de 1981 à 1985, l'âge de 65 ans n'a pas
de texte cité, et l'écart n'est pas déclaré. L'âge de l'ancien code, avant la
codification de 1985, n'a pas été lu ici : à lire, ou à déclarer.

## 5. Ce qui bouge : treize témoins, pour cette seule cause

`tests/temoins/simulations.json`, comparé champ par champ entre `bbb85b0`, fait avant
que le rebasage ne prenne f6012e5, et `d8124ff`, refait sur le dernier `main` : treize
témoins sur 930, aucun autre. Douze ne changent que `age_ouverture_opposable`
(61,166667 → 61,166666666666664, 61,58 → 61,583333333333336, 51,33 → 51,333333333333336…),
qui n'ouvre ni ne ferme rien. Le treizième,
`comedie_francaise_generation_1958_apres_soixante_ans`, passe de « non_ouverte » à
« age_legal », sans qu'aucun montant ne change : né le 15 janvier 1958, il a 60 ans
8 mois le 15 septembre 2018, l'âge du décret n° 68-960, article 51, I, A, 3°, pour sa
génération ; l'ouverture lui est due. Entre `f6012e5^` et `bbb85b0`, seuls cinq témoins
de Mayotte bougent, de l'action 177.

`data/derive/agregats.json` et `equilibre.json`, de `f6012e5^` à f6012e5 : le coût et
les soldes, 1,08 × 10⁻⁵ au plus en valeur relative ; les longues carrières aux
avantages, 1 952,82 → 1 947,19 en 2014 (−0,29 %) et 2 663,75 → 2 669,29 en 2015
(+0,21 %) ; les catégories classées, −0,09 % en 2014 ; les cas types, 2,9 × 10⁻⁴ au
plus. Conforme à la note.

**Écart faible.** Le relevé de la note n'est pas complet : les leviers bougent jusqu'à
2,3 × 10⁻⁵ et les variantes de migrations jusqu'à 1,8 × 10⁻⁵, au-delà du « 1,1 × 10⁻⁵ au
plus » qu'elle donne, qui ne vaut que pour le coût, la dette et les soldes ; les
départs anticipés des régimes spéciaux bougent de 0,04 % au plus (2014, 2015, 2017,
2018, 2021 et 2022), et ceux des catégories classées aussi en 2015, 2019 et 2020
(+0,08 %, +0,09 %, −0,10 %), qu'elle ne cite pas. Tout vient de la même cause, les départs au mois exact. Les six pages
n'ont pas été recomptées ici.

## 6. `ages_reference.csv` : le même défaut, sans effet sur le scénario par défaut

**Écart faible, hors du scénario 1, non corrigé ici.** La table de l'âge de référence de
la proposition, par année, écrit 61,17 et 66,17 en 2013 (au-dessus de 61 ans 2 mois et
66 ans 2 mois), 61,42 et 66,42 en 2014 (au-dessus de 61 ans 5 mois et 66 ans 5 mois, un
âge qu'aucune génération n'a : la table est une construction par année, non un âge de
texte), 61,58 et 66,58 en 2015 (en dessous). `_charger_ages`
(`moteur/age_reference.py`) la lit sans `au_mois`, et le paquet la porte telle quelle ;
sa colonne `age_ouverture_legal` n'est lue par aucun moteur.

Son effet, lu dans `moteur/js/age-reference.js`, `scenario-notionnel.js` et
`cycle-de-vie.js` :
- au réglage par défaut (`fixe_apres_bascule`), l'âge à la bascule est de 65 ans : aucun
  droit converti ne change, aucune pension ;
- avant la bascule, le cliquet rend 66,17 en 2013 et 66,42 en 2014 : un départ à
  66 ans 2 mois pile en 2013 porte un écart de +0,0033 an, et `anticipe: true`, dans
  le bloc `age_reference` du résultat, qu'aucune page ne lit ;
- sous les variantes à cliquet ou sans cliquet, une bascule posée en 2013, 2014 ou 2015
  (le formulaire l'accepte de 1941 à 2070) convertit les droits acquis à 66,17, 66,42
  ou 66,58 ans, à un ou deux jours de l'âge en mois. Dès 2016, la table rend 66,75 puis
  67, exacts.

## Sources

Index LEGI de la DILA (à jour au 2 novembre 2026) : L. 351-8 (LEGIARTI000028498855,
000006742633, 000006742632) ; D. 161-2-1-9 (000025089933) ; L. 161-17-2 (000025014605) ;
L. 351-1 (000023035688) ; R. 351-27 (000024113020, 000006749434, 000006749435,
000006749436, 000020082993) ; R. 643-7 (000024113055) ; décret n° 81-1046, article 2
(000006768391) ; décret n° 2011-2103, articles 2, 4, 6 et 8 (000025100416, 000025100420,
000025100424, 000025100429) ; décret n° 68-960, article 51 (000029134323) ; décret
n° 2008-637, article 51-1 (000023732424, 000029137528) ; décret n° 2008-639,
article 37-1 (000029165223) ; D. 351-1-1 (000023397567, 000054059621). Index JORF (à
jour au 3 novembre 2026) : JORFARTI000024270214, JORFARTI000020694605. Accord national
interprofessionnel du 17 novembre 2017, article 84, version « applicable au 1er janvier
2019 », circulaire 2018-09-DC, PDF de l'Agirc-Arrco.
