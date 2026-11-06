# Les écarts de R-E14 repris, et la CAVEC, la CAVP et la CPRN de `surcote_par_age_seul` écrites en versions (E14)

File E, session E14, le 6 novembre 2026 (action 130, vague 11, sur Opus), après E13
(1a6013d) et sa relecture R-E14 (64120bd). Index de la DILA récupérés ce jour : JORF à
jour du 3 novembre 2026, LEGI du 2 novembre ; recherches au titre et au texte, en SQL sur
toute la table `doc`, sans borne de réponses. Cas posés dans les deux moteurs par
`servi_et_refait` (`tests/outils_pont.py`), réglages de E11 : `profil` plat, `euros`
2026, `enfants` 0, `sexe` F, `salaire` 2, `debut` 22 ; un script hors du dépôt. Aucune
valeur servie ne change ; un point non tranché neuf est déclaré (la CAVEC, au début de
2008), non corrigé. La fiche entre à `LUES_AU_DROIT`.

## 1. Les écarts de R-E14

**(A) Les arrêtés qui modifient les statuts de 1979 de la Cipav.** Relevé de nouveau, de
1979 à 2008, au titre puis au texte (« architect », « cipav », « interprofessionnelle
de prévoyance », avec « statut », puis sans lui ; ensuite les arrêtés à plusieurs
sections dont le titre ne nomme pas les architectes). Les statuts du complémentaire de
1979 sont modifiés, au Journal officiel, par les arrêtés du 7 février 1980
(JORFTEXT000000832498, « ART. 6, 8 ET 10 »), du 5 mai 1981 (art. 8, 11 et 17), du 4 mai
1982 (article non dit), du 17 juin 1985 (art. 4, 9, 12, 13, 17, 17-bis et 21), du
22 août 1986 (JORFTEXT000000862986, « ART. 11 ANNEXE 1 »), du **9 mars 1987**
(JORFTEXT000000321565 : « ARCHITECTES,AGREES EN ARCHITECTURE,INGENIEURS,TECHNICIENS,
EXPERTS ET CONSEILS: ANNEXE N0 5,STATUTS DU REGIME DE RETRAITE COMPLEMENTAIRE: ART.
8,13,17 ET 17-BIS »), du **13 août 1987** (JORFTEXT000000475761, titre seul : « DES
REGIMES D'ASSURANCE VIEILLESSE ET INVALIDITE-DECES DES ARCHITECTES […] »), du **12 mai
2000** (JORFARTI000002418428 : « (art. 1er, 4, 4 bis, 11, 12 et 18) »), du **27 février
2003** (JORFARTI000001710064 : « du régime complémentaire d'assurance vieillesse (art. 6)
[…] de la section professionnelle des architectes »), du 29 juillet 2003, du
28 décembre 2004 (art. 7) et du 3 octobre 2006. Celui du 27 février 2003, au titre muet
(« à des statuts relatifs au régime de l'allocation de vieillesse, au régime
complémentaire d'assurance vieillesse et au régime invalidité-décès »), manquait aussi
à R-E14 : il ne touche que l'article 6. Ne touchent pas le complémentaire : le 7 avril
1981 et le 12 juin 1985 (l'allocation vieillesse), le 26 février 1985 (l'invalidité), le
26 mars 1987 (l'allocation vieillesse), le 19 juin 1991 (l'invalidité-décès), le
18 mars 2005 (la base), le 26 mai 2005 (les statuts généraux) ; le 20 mai 1987
(« DIVERS REGIMES ») ne nomme pas les architectes. **L'article 17 est modifié par ceux
du 5 mai 1981, du 17 juin 1985, du 9 mars 1987 et du 29 juillet 2003, et peut-être par
ceux du 4 mai 1982 et du 13 août 1987**, qui ne disent pas l'article ; tous au seul
Bulletin officiel. Écrit dans `avant_2007`, `cipav_2007`, `cipav_de_2008`,
`sources.a_relire` et la lecture d'E13 dans `sources.lectures`. Aucune valeur ne bouge :
`avant_2007` reste supposée, 2007 non tranché, la question 22 ouverte.

**(B) L'arrêté du 21 septembre 2026.** Relu (JORFARTI000054888279) : a) l'article 5,
deuxième alinéa, b) l'article 25, dernier alinéa, c) l'article 28, 3° et 7°, du règlement
du complémentaire de la CARMF ; d) l'article 4 de celui de l'invalidité-décès ; e)
l'article 3 de celui de l'ASV. Aucun article 2. Un second arrêté du même jour
(JORFARTI000054888289 et JORFARTI000054888291) modifie la CARCDSF (articles 20 et 21 des
prestations complémentaires) et l'article 16 du règlement de la CAVP, la réversion :
« les trois occurrences du mot : « premier » sont remplacées par le mot : « deuxième » » ;
l'article 12 de la CAVP n'y perd que ses guillemets (LEGIARTI000054437738 et
LEGIARTI000054890978 comparés mot à mot : quinze « « » ôtés, rien d'autre). Écrit dans
`reglements_de_2026`.

**(C) Les arrêtés de la CARMF de 2018.** La note d'E13 (section 2) range parmi eux ceux
de « juillet, août, novembre et décembre 2018 » ; l'index n'a, en 2018, que ceux du
20 août (JORFTEXT000037352127) et du 20 décembre (JORFTEXT000037864937), comme R-E14 l'a
relevé. La fiche écrit « d'août et décembre 2018 », juste. La note d'E13 est un récit :
elle n'est pas récrite, l'erreur est rectifiée ici.

**(D) La CARPIMKO, le cas posé de l'erreur (3) d'E13.** Confirmé. Née le 10 mars 1949,
âges comptés d'avril 1949 (`origine_des_ages`) : 66 ans et 7 mois, le 1er novembre 2015,
servi 5 298,186050419041 €, sans coefficient ; 66 ans et 9 mois, le 1er janvier 2016,
« coefficient de majoration 1.2250 », 6 529,68 €. Le modèle compte
`int((66,75 − début) × 4) = 18`, d'où un début dans ]62 ; 62,25] ; il avance de l'âge
légal, 60 ans, par trimestres (`age_de_la_duree_atteinte`) : 62,25, le 1er juillet 2011.
Au 1er novembre 2015, sous cette lecture, le texte compte les trimestres civils entiers
de juillet 2011 à septembre 2015 : 2 + 12 + 3 = 17, ou 16 si celui qui commence le jour
même ne compte pas (le point non tranché d'E13). 5 298,1861 × 17 × 0,0125 =
5 298,1861 × 0,2125 = 1 125,86 € ; × 0,20 = 1 059,64 € par an, sous la réserve de la
date d'effet. Écrit dans l'erreur de `carpimko_octobre_2015`, à côté de « au moins
397,36 € ».

## 2. La CAVEC, la CAVP et la CPRN, en versions

Chaque relevé au titre, sans borne, depuis 1979 (CAVEC) ou 1995 (CAVP) ou 2004 (CPRN),
puis au texte pour les arrêtés à plusieurs sections ; chaque arrêté lu à son annexe à
« prorogation », « 3.14 », « majoration », « surcote », « 70 ans », « vigueur », et ses
articles à leur date.

**La CAVEC.** Arrêtés : 22 février 2008, 26 novembre 2010, 9 février 2012, 27 mars 2012,
7 octobre 2013, 7 octobre 2014, 20 août 2018, 19 juin 2019, 2 juillet 2024, 4 juillet
2025, 16 décembre 2025, règlement du 10 juillet 2026. Touchent la majoration : 2008
(JORFARTI000018197778, article 3.14 « ainsi rédigé », publié le 1er mars, sans date, le
2 mars 2008), 2012 (JORFARTI000025395367 : les points « arrêté à la fin du trimestre »
du 65e anniversaire ; publié le 23 février, sans date, le 24 février 2012), 2018
(JORFARTI000037363871, article 13 : 0,75 %, 15 %, les points « arrêté à la date de
liquidation » ; le 5 septembre 2018), 2025 (JORFARTI000051849616, 7° : 1,25 % et 25 % ;
le 7 juillet 2025), le règlement (LEGIARTI000054437585, article 1.1.4, le même texte ; le
18 juillet 2026). Les autres n'y touchent pas (celui du 16 décembre 2025, en vigueur le
1er janvier 2026, sert la pension au prorata des points payés).
Versions neuves : `cavec_statuts_de_2008`, `cavec_fevrier_2012`, `cavec_septembre_2018`,
`cavec_juillet_2025`.

**Point non tranché neuf, la CAVEC avant le 2 mars 2008.** Le modèle majore dès le
1er janvier 2008 ; le texte de 2008 vaut le 2 mars, et l'article 3.14 qu'il « rédige »,
en vigueur avant, est au seul Bulletin officiel. La pension de la CAVEC ne prenant effet
qu'au premier jour d'un trimestre civil (article 3.15), la seule date de la fenêtre est
le 1er janvier 2008. Cas posé : expert-comptable né le 10 mars 1940 (âges d'avril 1940),
65 ans le 10 mars 2005.
- Au 1er janvier 2008 (67 ans et 9 mois) : servi 22 676,944501327118 €, « coefficient
  de majoration 1.1375 » (`int(2,75 × 4) = 11` trimestres × 1,25 %). Sans majoration :
  22 676,9445 / 1,1375 = 19 935,7754 € ; majoration : 22 676,9445 − 19 935,7754 =
  **2 741,17 €** par an, servis de trop sous la lecture A (rien avant le 2 mars 2008,
  celle de la fiche) ; rien sous la lecture B (l'article d'avant majorait de même).
- Au 1er octobre 2007 (67 ans et 6 mois) : servi 19 185,657428660852 €, sans majoration.
  Sous la lecture B, dix trimestres pleins (10 mars 2005 au 10 septembre 2007) :
  19 185,6574 × 0,125 = **2 398,21 €** par an au plus servis en moins (le texte de 2008
  ne majore que les points arrêtés au 31 décembre 2005, le modèle tous).

Écrit en approximation, versions `avant_2007`, `cipav_2007`, `cipav_de_2008`. L'écart des
points majorés (jusqu'au 4 septembre 2018, ceux arrêtés à la fin de l'année, puis du
trimestre, du 65e anniversaire, le modèle tous), déjà déclaré dans `effet` et
`sources.a_relire`, est redit à ses huit versions, non mesuré.

**La CAVP.** Arrêtés : 5 septembre 1997, 21 juin 2002, 27 juin 2006, 27 mars 2007,
11 mai 2009, 23 juin 2011, 24 septembre 2012, 4 juin 2015, 30 novembre 2016, 5 juillet
2017, 3 octobre 2019, 19 juin 2023, 19 décembre 2023, 5 mai 2025, règlement du 10 juillet
2026, 21 septembre 2026. Les statuts de 2009 (JORFARTI000020694605, le 7 juin 2009)
n'écrivent aucune majoration au complémentaire (« major » n'y nomme, des pensions, que la
base, article 21, et les enfants). Celui du 23 juin 2011 (JORFARTI000024270214, publié le
29 juin, sans date à ses six articles : le 30 juin 2011) l'institue à l'article 12 et
dans le tableau de l'article 15. Ceux de 2015, 2016, 2019, 2023 et 2025 n'y touchent pas
(celui du 19 décembre 2023 ôte de l'article 12, premier alinéa, la cessation ; celui de
2025 modifie l'article 12 de l'invalidité-décès) ; le règlement, article 12, la reprend
(LEGIARTI000054437738), sans changement au 25 septembre 2026. **La piste de 2011** :
le modèle ne majore qu'au 1er janvier 2012 ; déjà instruite et déclarée dans
`cavp_minoration_deux_pentes` (sans effet dans la lecture du tableau ; le non-tranché
des nés jusqu'au 30 juin 1951), redite ici, non redéclarée. Version neuve :
`cavp_statuts_de_2011`.

**La CPRN.** Arrêtés : 28 décembre 2004 (nouveaux statuts, titre seul : Bulletin
officiel), 27 février 2008 (la majoration pour enfants), 16 décembre 2013, 31 mai 2017,
29 novembre 2023, règlement du 10 juillet 2026 (celui du 29 janvier 2024 est le
règlement professionnel). Touchent la majoration : 2013 (JORFARTI000028387445, article
16 « ainsi rédigé » ; article 2 : « Le présent arrêté prend effet au 1er janvier
2014. »), 2017 (JORFARTI000034975971, article 23, la même règle ; publié le 21 juin, sans
date, le 22 juin 2017), 2023 (JORFARTI000048679350, 5° : « 1 % », « fin d'activité » ;
article 2 : le 1er janvier 2024), le règlement (LEGIARTI000054437637, article 9, 1°).
Versions neuves : `cprn_2014`, `cprn_juin_2017`, `cprn_2024`. Avant 2014, rien, supposé.

**Le modèle sert chaque règle.** Confronté mois par mois (taux, nombre de trimestres,
âges, trimestres cotisés), de 1980 à 2040 : seuls ressortent la CAVEC de janvier à mars
2008 et la CAVP de juillet à décembre 2011, les deux écarts écrits. Cas posés, servis
dans les deux moteurs : CAVEC, né le 10 mars 1950, au 1er avril 2018, 1,15 (12 × 1,25 %),
au 1er octobre 2018, 1,105 (14 × 0,75 %), au 1er octobre 2025, 1,25 (vingt au plus) ;
né en 1958, au 1er octobre 2025, 1,125 ; né en 1943, au 1er janvier 2012, 1,1875. CAVP,
né en 1956, au 1er avril 2024, 1,02, au 1er avril 2027, 1,06 (70 ans) ; né en 1953, au
1er avril 2023, 1,04 (68 ans) ; né en 1952, au 1er avril 2020, 1,02 (66 ans) ; né en
mars 1951, au 1er avril 2019, rien. CPRN, né en 1950, au 1er avril 2018, 1,06, au
1er avril 2023, 1,10 (70 ans) ; né en 1955, au 1er avril 2026, 1,16 (1 % sans borne) ;
né en 1948, au 1er janvier 2014, 1,015.

Dix-huit versions désormais, contiguës ; `cipav_2023_a_juin_2026` devient `cipav_2023`
(nulle part ailleurs nommée). Les sept régimes écrits, `tests/test_carte.py` admet la
fiche à `LUES_AU_DROIT` sans rien forcer.

## 3. Tests

`tests/test_carte.py`, `tests/test_sections_liberales.py`, `tests/test_textes.py`,
`tests/test_regle_de_chacun.py` : 100 verts, et 99 verts et un sauté sous
`PRESOMPTIONS_DECALEES=1`. Suite rapide : 4 589 verts et 9 sautés ; sous le jeu décalé,
4 384 verts et 214 sautés. `tests/test_donnees.py` et `tests/test_outillage.py` : 220 verts.
Le paquet ne lit pas la fiche : `construire_donnees.py` ne change rien.

## Pour la suite

`cotisation_par_classes_liberales`. Restent au propriétaire, non corrigés, les erreurs
déjà déclarées, et le point neuf de la CAVEC ; au Bulletin officiel : les statuts de la
CAVEC d'avant 2008 et de la CPRN de 2004, et les arrêtés de la Cipav de 1979 à 2006.
