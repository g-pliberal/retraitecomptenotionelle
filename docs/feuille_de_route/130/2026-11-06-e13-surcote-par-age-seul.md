# Les écarts de R-E13 repris, et la CARMF, l'ASV et la CARPIMKO de `surcote_par_age_seul` écrites en versions (E13)

File E, session E13, le 6 novembre 2026 (action 130, vague 11, sur Opus), après E12
(45453aa) et sa relecture R-E13 (6df64a1). Index de la DILA récupérés ce jour : JORF à
jour du 3 novembre 2026, LEGI du 2 novembre. Cas posés dans les deux moteurs par
`servi_et_refait` (`tests/outils_pont.py`), réglages de E11 : `profil` plat, `euros`
2026, `enfants` 0, `sexe` F, `salaire` 2, `debut` 22 ; un script hors du dépôt.
Aucune valeur servie ne change ; trois erreurs neuves et un point non tranché sont
déclarés, non corrigés (candidats, au propriétaire).

## 1. Les quatre écarts de R-E13

**Écart 1 : les arrêtés qui modifient les statuts de 1979.** Recherche à l'index JORF,
sans borne de réponses, des arrêtés de 1979 à 2006 dont le titre nomme les
« architectes », la « cipav » ou l'« interprofessionnelle de prévoyance », puis ceux
du complémentaire : 7 février 1980 (« ART. 6, 8 ET 10 ») ; 5 mai 1981
(JORFTEXT000000871027, « (ART. 8,11 ET 17) », le titre seul à l'index) ; 4 mai 1982
(JORFTEXT000000677739, « UNE MODIFICATION », « CET ARRETE SERA INTEGRALEMENT PUBLIE
AU BULLETIN OFFICIEL ») ; 17 juin 1985 (JORFTEXT000000840042, « APPROBATION DES
MODIFICATIONS APPORTEES AUX ART. 4,9,12,13,17,17-BIS ET 21 DES STATUTS ») ; 22 août
1986 (« ART. 11 ANNEXE 1 ») ; 29 juillet 2003 (JORFARTI000001531753, « (art. 9, 11,
13, 15, 17 et 17 bis) », « sera publié intégralement au Bulletin officiel n° 2003-35 ») ;
28 décembre 2004 (« statuts (art. 7) ») ; 3 octobre 2006. Ceux de 1980 (allocation de
vieillesse, art. 18, 20 et 21), 1981 (7 avril), 1985 (26 février, 12 juin) et 2005
(18 mars, base, art. 15) sont d'autres régimes. Aucun ne nomme l'article 16 ; trois
nomment l'article 17, un quatrième ne dit pas l'article. Ils sont cités dans
`avant_2007`, `cipav_2007` (lecture B), `cipav_de_2008`, l'approximation d'avant 2007
et `sources.a_relire` ; la question 22, écrite dans la note du 3 novembre, ne se récrit
pas : ils s'y ajoutent ici.

**Écart 2 : l'affiliation comptée depuis 1979.** Si les « trente années d'affiliation »
se comptent depuis la première année du régime, comme les trois décomptes de la
cotisation : pension au 1er janvier 2007, 2007 − 1979 = 28 années (1979 à 2006),
moins de trente : rien n'est dû sous la lecture A même, 0 € d'écart ; pension au
1er janvier 2008, 29 années (1979 à 2007) : rien n'est dû, le modèle (qui ne majore
rien jusqu'en 2012) sert juste, 0 € ; au 1er janvier 2009, 30 années (1979 à 2008). En
2007, l'ensemble des valeurs ne change pas (0 €, ou 136,19 à 347,40 €) ; « au moins
215,43 € » en 2012 tient sous toutes les lectures (33 années). Écrit dans `cipav_2007`,
`cipav_de_2008`, leurs approximations et `sources.a_relire`.

**Écart 3 : le 18° de l'arrêté du 16 décembre 2021**, relu (JORFARTI000044554134) :
« 18° L'article 3.13 est remplacé par les dispositions suivantes : « La pension de
retraite complémentaire est liquidée, […] aux conditions suivantes : « 1° A taux
plein : « - à partir de l'âge du taux plein prévu au 1° de l'article L. 351-8 du code
de la sécurité sociale » : cité dans `cipav_2022`.

**Écart 4 : l'ASV** : dans le bloc « Reprise », la piste de 2017 nomme la CARMF et
l'ASV (elle est instruite ci-dessous).

## 2. Les versions, coupées aux dates des trois sections lues

| version | bornes | Cipav | CARMF et ASV | CARPIMKO |
|---|---|---|---|---|
| `avant_2007` | jusqu'au 31 décembre 2006 | rien (supposée) | rien | rien |
| `cipav_2007` | 2007 | non tranché | rien | rien |
| `cipav_de_2008` | 1er janvier 2008 au 2 octobre 2015 | 5 % par an après 65 ans | rien | rien |
| `carpimko_octobre_2015` | 3 octobre 2015 au 31 décembre 2016 | id. | rien | 1,25 % par trimestre civil entier, 20 au plus |
| `carmf_asv_2017` | 1er janvier au 29 mars 2017 | id. | 1,25 % de l'âge légal, 0,75 % de 65 ans, jusqu'à 70 | id. |
| `carmf_asv_mars_2017` | 30 mars 2017 au 31 décembre 2021 | id. | id., de 62 ans | id. |
| `cipav_2022`, `cipav_2023_a_juin_2026`, `cipav_depuis_juillet_2026` | 2022 au 17 juillet 2026 | (E12) | id. | id. |
| `reglements_de_2026` | depuis le 18 juillet 2026 | au décret | règlements, article 2 | règlement, article 5 |

**CARMF et ASV.** Arrêtés relevés au titre (« section professionnelle des médecins »
ou « carmf », 2016 à 2026), annexes lues aux articles 15 (complémentaire) et 12 (ASV).
Du 30 novembre 2016 (JORFARTI000033521562) et du 1er décembre 2016
(JORFARTI000033538061) : « A compter du 1er janvier 2017, […] 1. Etre âgé de l'âge
prévu au premier alinéa de l'article L. 351-1 […]. « Si le médecin demande à
bénéficier de la retraite complémentaire après cet âge, il est fait application d'un
coefficient de majoration de 1,25 % par trimestre séparant le premier jour du trimestre
civil suivant celui où le médecin atteint cet âge de la date d'effet de la retraite » ;
article 2 de chacun : « Le présent arrêté entre en vigueur au 1er janvier 2017. » Du
21 décembre 2016 : les alinéas de l'inaptitude seuls. Du 22 mars 2017
(JORFARTI000034298521) : « après cet âge » devient « après l'âge de 62 ans » ; ni
l'article 1er ni l'article 2 ne datent : publié le 29 mars, en vigueur le 30 mars 2017
(comme `carmf_asv_minoration_enfants`). Du 21 février 2024 : « A compter du 1er janvier
2017 » ôté, l'inaptitude récrite. Ceux de septembre et novembre 2017, juillet, août,
novembre et décembre 2018, octobre 2020 (son « article 12 » est celui de
l'invalidité-décès), mars 2021 (invalidité-décès), février 2024 (statuts généraux) et
janvier 2025 (son « article 15 » de l'ASV est la réversion) : rien. Règlements du
10 juillet 2026 (JORFARTI000054435859), publiés le 17 juillet sans date (articles 1er et
2) : le 18 juillet 2026, le texte de mars 2017 ; l'arrêté du 21 septembre 2026 ne
modifie que l'article 5. Avant 2017 : rien, supposée (« A compter du 1er janvier
2017 » ; l'article 32 et le « différé », `sources.a_relire`).

**CARPIMKO.** Arrêtés relevés au titre (« carpimko » ou « auxiliaires médicaux », 2014
à 2026), annexes lues à « 12 ter », « ajourn », « Surcote ». Du 31 juillet 2015
(JORFARTI000031255547), publié le 2 octobre 2015 : article 12 ter inséré, « Cette
majoration est égale à 1,25 % par trimestre civil entier d'ajournement postérieur à
l'âge du taux plein dans la limite de vingt trimestres » ; ni ses articles 1er et 2 ni
son annexe (« 2016 », « compter du », « vigueur ») ne datent : le 3 octobre 2015. Du
27 décembre 2023 : l'intitulé « Majoration de la pension », l'alinéa des enfants. Les
autres (2014, 2016, 2017, 2018, 2019, 2020, 2022, 2024, 2025) : rien. Règlement du
10 juillet 2026, article 5 (JORFARTI000054435915) : les deux phrases, le 18 juillet 2026.

**Le modèle sert-il chaque règle ?** Taux, palier, limite de 70 ans, vingt trimestres,
62 ans depuis mars 2017 : oui. Trois erreurs et un point non tranché, ci-dessous. Le
décompte par l'âge où la durée est atteinte (CARPIMKO) est celui que la fiche écrit
déjà (`surcote_depuis_la_duree`).

## 3. Les erreurs neuves, déclarées, non corrigées (candidats, au propriétaire)

**(1) CARMF et ASV, du 1er janvier au 29 mars 2017 : l'âge légal, non 62 ans.** Le
texte compte « après cet âge », l'âge du premier alinéa de L. 351-1, c'est-à-dire de
L. 161-17-2 (LEGIARTI000025014605) et D. 161-2-1-9 (LEGIARTI000025089933, en vigueur
en 2017) : « 1° Soixante ans pour les assurés nés avant le 1er juillet 1951 ; […] 3°
Soixante ans et neuf mois pour les assurés nés en 1952 ». Le modèle compte de 62 ans
dès 2017 (`surcote_age_debut: 62`). Née le 10 mars 1952, pension au 1er janvier 2017 :
60 ans et 9 mois le 10 décembre 2012 (4e trimestre), le décompte part du 1er janvier
2013 ; 16 trimestres jusqu'au 1er janvier 2017, tous avant le palier (65 ans le 10 mars
2017) : 1 + 16 × 0,0125 = 1,20. Le modèle : 62 ans en mois révolus le 1er avril 2014,
33 mois, 11 trimestres : 1 + 11 × 0,0125 = 1,1375. Servi : CARMF 12 364,012486 €
(« cotisations revalorisées 211,880 € × rendement 5.13% × coefficient de majoration
1.1375 »), ASV 15 894,81012 € (« 1,235.50 points × valeur de service 11.31 € ×
coefficient de majoration 1.1375 »). Hors coefficient : 12 364,0125 / 1,1375 =
10 869,4615 ; × 0,0625 = **679,34 €** par an servis en moins ; 15 894,8101 / 1,1375 =
13 973,4594 ; × 0,0625 = **873,34 €**. Née le 10 mars 1948 : 60 ans le 10 mars 2008,
décompte du 1er avril 2008 ; 20 trimestres à 1,25 % jusqu'au 1er avril 2013 (65 ans le
10 mars 2013), 15 à 0,75 % jusqu'au 1er janvier 2017 : 1 + 0,25 + 0,1125 = 1,3625. Le
modèle : 12 à 1,25 % (1er avril 2010 au 1er avril 2013), 15 à 0,75 % : 1,2625. Servi :
CARMF 14 503,908959 €, ASV 18 610,457009 € ; 14 503,9090 / 1,2625 = 11 488,2447,
× 0,10 = **1 148,82 €** ; 18 610,4570 / 1,2625 = 14 740,9560, × 0,10 = **1 474,10 €**.
La lecture contraire (62 ans dès janvier, l'arrêté de mars ne faisant que corriger)
n'a d'appui dans aucun texte lu : l'arrêté du 22 mars 2017 ne rétroagit pas. Ce que la
caisse a servi ce trimestre-là n'est pas lu.

**(2) CARMF et ASV, depuis 2017 : le médecin né le premier jour d'un trimestre
civil.** Le texte part du « premier jour du trimestre civil suivant celui où le médecin
atteint cet âge » ; le modèle, du premier jour du mois où l'âge est atteint
(`origine_des_ages`), en trimestres de trois mois révolus. Né un autre jour, le compte
est le même aux dates d'effet du premier jour d'un trimestre civil (né le 10 mars : le
mois d'après, 1er avril, est aussi le trimestre d'après) ; né le 1er janvier, avril,
juillet ou octobre, le modèle compte un trimestre de plus, sauf quand la limite des
70 ans est atteinte (les deux décomptes y glissent ensemble). Né le 1er janvier 1958,
pension au 1er janvier 2025 : le texte, du 1er avril 2020, 12 trimestres à 1,25 %
jusqu'au 1er avril 2023, 7 à 0,75 % : 1 + 0,15 + 0,0525 = 1,2025 ; le modèle, du
1er janvier 2020, 12 et 8 : 1,21 ; né le 2 janvier, 1,2025. Servi : CARMF 16 116,028856 €
(« 294,018 € × rendement 4.53% × coefficient de majoration 1.2100 »), ASV
19 267,202482 € ; 16 116,0289 / 1,21 = 13 319,0321, × 0,0075 = **99,89 €** par an de
trop ; 19 267,2025 / 1,21 = 15 923,3078, × 0,0075 = **119,42 €**. La même erreur est
déclarée à la CARCDSF.

**(3) CARPIMKO, du 3 octobre au 31 décembre 2015, sous une réserve.** Le texte majore,
le modèle n'a rien jusqu'en 2015 (`surcote_par_trimestre: null`). Né le 10 mars 1949,
taux plein à 65 ans (article 12 quater, 1°, « 1955 ET ANTÉRIEURE […] 65 ans ») le
10 mars 2014, pension au 1er novembre 2015 : servi 5 298,18605 € (« cotisations
revalorisées 47,991 € × rendement 11.04% », sans coefficient) ; le texte, au moins six
trimestres civils entiers après le 10 mars 2014 (avril 2014 à septembre 2015), 1,075 :
5 298,1861 × 0,075 = **397,36 €** par an au moins, plus si la pension pouvait être
liquidée sans abattement avant 65 ans. La réserve : si la pension ne prend effet qu'au
premier jour d'un trimestre civil (statuts de 1984, article 11 ; règlement de 2026,
article 7 ; l'article de 1996 à 2026 n'est pas lu), aucune ne prend effet dans ces
trois mois, et l'écart se réduit à la date d'effet, déjà déclarée dans
`carpimko_ages_2015`.

**Point non tranché, CARPIMKO, depuis le 3 octobre 2015.** « Par trimestre civil entier
d'ajournement postérieur à l'âge » : le trimestre civil qui commence le jour même où
l'âge, ou la durée, est atteint, le modèle le compte, et le texte ne dit pas s'il est
« postérieur ». Né le 1er janvier 1950, pension au 1er janvier 2017 : le modèle, 18
trimestres, « coefficient de majoration 1.2250 », 6 707,96361 € ; sans ce trimestre,
17, 1,2125 (ce que le modèle sert né le 2 janvier) : 6 707,9636 / 1,225 × 1,2125 =
6 639,5150 €. Écart : 0 € ou **68,45 €** par an de trop.

## Tests

`tests/test_sections_liberales.py` (seul à nommer la fiche), `tests/test_carte.py`,
`tests/test_textes.py`, `tests/test_regle_de_chacun.py` : 100 verts. `carte.manques()` :
73 fiches à manques, 412 manques, `surcote_par_age_seul` sans manque ni écart
(`outils_carte.ecarts`) ; elle n'entre pas à `LUES_AU_DROIT` : la CAVEC, la CAVP et la
CPRN ne sont pas écrites. Les textes de la CARMF, de l'ASV et de la CARPIMKO sortent de
`textes_a_rattacher`, cités par les versions ; le cliquet des rédactions sans statut ne
bouge pas. Suite rapide et paquet : voir le message du commit.

## Ce qui reste

- `surcote_par_age_seul`, ses trois derniers régimes en versions, chaque rédaction lue à
  la source, leurs dates coupant les versions : la CAVEC (arrêtés du 22 février 2008, du
  9 février 2012, du 20 août 2018, du 4 juillet 2025, règlement de 2026 ; les coupures
  du 5 septembre 2018 et du 7 juillet 2025 sont déjà au modèle), la CAVP (piste : le
  modèle ne majore qu'en 2012, pour un arrêté du 23 juin 2011), la CPRN (16 décembre
  2013, 31 mai 2017, 29 novembre 2023, règlement de 2026). Puis la fiche entre à
  `LUES_AU_DROIT` si `tests/test_carte.py` l'admet.
- Puis `cotisation_par_classes_liberales`.
- Au propriétaire : les trois erreurs et le point non tranché ci-dessus, avec ceux de
  la Cipav.
