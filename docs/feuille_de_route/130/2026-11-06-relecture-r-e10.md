# Relecture de E9 (l'erreur de la Cipav, le décret n° 2026-418, les écarts de R-E9 repris)

File R-E10, le 6 novembre 2026 (action 130, vague 11, sur Opus) : relecture indépendante,
contre les sources, du commit 87b666c de la session E9
(`decret_2026_418_liberaux`, `sections_liberales_majoration_enfants`,
`tests/test_sections_liberales.py` ; note `2026-11-06-e9-fiches-communes-restantes.md`).
Ni règle, ni donnée, ni test n'est modifié.

**Méthode.** Les index de la DILA récupérés puis mis à jour : JORF au 6 novembre 2026
(incrément 20261106-002608), LEGI au 5 novembre (20261105-214938). Chaque texte rouvert par
`dila_cherche.py --texte`, les articles de LEGI par `--num … --le` ; les textes modificatifs
cherchés par numéro, titre et mots, sans borne (`--limite 500` ou `1000`, jamais atteinte).
Les montants refaits en décimal exact, à partir des cotisations de la Cipav que le moteur
Python crédite année par année (`droits.cotisations`, relevées pendant l'essai, sans rien
écrire au dépôt) ; les pensions servies par le portage et refaites par le moteur Python
(`servi_et_refait`), sous les deux jeux.

**Verdict.** L'erreur de la Cipav est **confirmée** : la lecture contraire est intenable
pour toute pension qui prend effet depuis le 1er juillet 2026, reports en cours compris ;
les montants de E9 sont exacts au centime. L'article 5-3 est conforme. L'inventaire du
décret compte bien 31 articles, chacun rapporté au bon décret, mais **deux écarts faibles**
dans le rattachement aux régimes et aux fiches. Les quatre reprises de R-E9 sont
conformes. **Deux écarts faibles** encore sur l'erreur elle-même : ce que le texte ne
tranche pas (le décompte d'une première année partielle ; la règle d'avant le 1er juillet
2026) n'est pas chiffré.

## 1. L'erreur de la Cipav : confirmée

**Le texte.** Décret n° 2026-418 du 29 mai 2026, JORF du 31 mai 2026 (JORFTEXT000054153355),
article 20 (JORFARTI000054153655), 4° : « Après l'article 5, sont insérés des articles 5-1
à 5-6 ainsi rédigés : » ; article 5-2, II, du décret n° 79-262, mot pour mot :
« L'affilié qui a atteint l'âge prévu au a du 1° de l'article 5-1 et comptant un minimum
de trente années d'affiliation à la CIPAV, peut différer la date d'entrée en jouissance de
la pension de retraite complémentaire de 1 à 5 ans. « Le compte de points qui est alors
établi est majoré de 5% par année entière de prorogation. « Cette majoration s'applique
uniquement aux points acquis au titre des trente premières années de cotisation à la
CIPAV. « Pour la détermination des trente années de cotisation, les années au titre
desquelles l'affilié a obtenu une exonération ou une réduction de cotisation sont prises
en compte. » La même rédaction est dans LEGI (LEGIARTI000054168515, seule version, en
vigueur le 1er juillet 2026), celle que `--le 2027-07-01` rend. L'âge du a du 1° de
l'article 5-1 : « A partir de l'âge du taux plein prévu au 1° de l'article L. 351-8 du
code de la sécurité sociale » ; l'article L. 351-8, 1° (LEGIARTI000051289852, en vigueur
le 1er juillet 2027) : « l'âge prévu au premier alinéa de l'article L. 161-17-2 augmenté de
trois années », et ce premier alinéa (LEGIARTI000053280889) : « fixé à soixante-quatre ans »,
soit 67 ans. Citations de E9 : **exactes**.

**La date d'effet.** Article 30 (JORFARTI000054153813) : « Le présent décret entre en
vigueur le 1 er juillet 2026. » ; LEGI : « Conformément à l'article 30 du décret n° 2026-418
du 29 mai 2026, ces dispositions, dans leur rédaction issue dudit décret, entrent en
vigueur le 1er juillet 2026. » Aucune autre phrase d'application : l'article 20 entier
(12 055 caractères, relu pour « juillet 2026 », « antérieur », « en cours », « à compter »,
« transitoire », « statuts », « version en vigueur ») n'en porte aucune pour le report, ni
l'article 29, qui ne règle que les critères de soutenabilité (« fixent au plus tard le 31
décembre 2026 les critères de soutenabilité financière de ces régimes »), et qui exclut
d'ailleurs la Cipav (« à l'exception des régimes gérés par la section professionnelle
mentionnée au 11° de l'article R. 641-1 »). Aucun texte paru depuis ne touche le décret
n° 79-262 : au JORF, `"79-262" OR CIPAV OR "architectes, agréés"` depuis 2023, puis
`"interprofessionnelle de prévoyance"` et le titre « interprofessionnelle » depuis 2026,
rien après le 31 mai 2026 ; aucun rectificatif du décret n° 2026-418 ; LEGI ne connaît
qu'une version des articles 5-1, 5-2 et 5-3.

**Le sort des pensions et des reports en cours.** La majoration s'applique au « compte de
points qui est alors établi », à l'entrée en jouissance différée : une pension liquidée
avant le 1er juillet 2026 n'est pas revue (aucun texte ne la rouvre) ; une pension qui
prend effet depuis le 1er juillet 2026 suit l'article 5-2, II, même si le report a
commencé avant, faute de disposition transitoire. Le cas de E9 est précisément un report
en cours : 67 ans le 10 mars 2026, trois mois de report déjà courus au 1er juillet 2026.

**La lecture contraire est intenable.** Majorer tous les points n'a pour elle aucun texte
en vigueur depuis le 1er juillet 2026 : l'article 5-2, II, dit « uniquement ». Une
pension à report commencé avant cette date, qui garderait la règle d'avant, ne gagnerait
rien non plus : celle-ci n'est lisible qu'au Bulletin officiel (article 3.15 des statuts),
et la caisse elle-même l'écrivait déjà limitée (`cipav_complementaire.yaml` cite sa fiche
pratique de 2022 : « avec surcote (appliquée sur les points acquis au titre des 30
premières années de cotisations) »). L'expression « trente premières années » n'apparaît,
au JORF, qu'à l'article 20.

**Le modèle.** `cipav_complementaire.yaml`, les deux périodes de 2025 (lignes 384 et 431,
`fin: null`) : `age_taux_plein_par_generation: age_annulation_decote`,
`surcote_par_trimestre: 0.0125`, `surcote_pas_trimestres: 4`,
`surcote_trimestres_maximum: 20`, `surcote_affiliation_minimale_trimestres: 120` ; la
prose du fichier le dit elle-même : « il majore TOUS les points et non ceux des trente
premières années, ce que rien dans le modèle ne distingue ». Conforme pour l'âge (67 ans),
le pas (5 % par année entière), le plafond (cinq ans) et la condition (trente années,
comptées en cent vingt trimestres) ; contraire au texte pour l'assiette.

**Le calcul, refait.** Le cas de E9 : née le 10 mars 1959, libérale de la Cipav au double
du salaire moyen depuis 22 ans (`statut` profession_liberale, `salaire` 2, `debut` 22,
`profil` plat, `euros` 2026, `enfants` 0, `sexe` F, les autres réglages ceux du test des
deux moteurs). Les deux moteurs, sous les deux jeux (`PRESOMPTIONS_DECALEES=1` compris),
servent la même pension de la Cipav :
- à 67 ans et 3 mois (1er juillet 2026), 21 662,48 € : « cotisations revalorisées 355,123 €
  × rendement 6.10% », sans majoration ;
- à 68 ans et 3 mois (1er juillet 2027), 24 000,52 € : « cotisations revalorisées
  374,715 € × rendement 6.10% × coefficient de majoration 1.0500 » ;
- à 72 ans et 3 mois (1er juillet 2031), 35 074,52 € : « … 459,994 € … × coefficient de
  majoration 1.2500 ».

Les cotisations de la Cipav, relevées année par année : pour 2027, de 1981 à 2027, 47
années, aucune nulle, 374 715,4414 € ; de 1981 à 2010, 184 754,1840 €. Pour 2031, de 1981
à 2031, 459 993,6709 € ; de 1981 à 2010, 198 030,4407 €. À la main, 0,05 × 0,061 =
0,00305 :
- le modèle, un an : 374 715,4414 × 0,003 = 1 124,1463 ; × 0,00005 = 18,7358 ; somme
  **1 142,8821 €** ; le texte : 184 754,1840 × 0,003 = 554,2626 ; × 0,00005 = 9,2377 ;
  somme **563,5003 €** ; **579,38 € par an de trop** ;
- cinq ans, 0,25 × 0,061 = 0,01525 : 459 993,6709 × 0,015 = 6 899,9051 ; × 0,00025 =
  114,9984 ; somme **7 014,9035 €** ; 198 030,4407 × 0,015 = 2 970,4566 ; × 0,00025 =
  49,5076 ; somme **3 019,9642 €** ; **3 994,94 € par an de trop** ;
- contrôle : 374 715,4414 × 0,061 × 1,05 = 24 000,5240, la pension servie ; 459 993,6709
  × 0,061 × 1,25 = 35 074,5174.
Montants de E9 : **exacts au centime**. Ils sont ceux du modèle, qui convertit les
cotisations revalorisées au rendement unique de 6,10 % ; les points réels de chaque année,
achetés à son prix, donneraient une autre part aux trente premières années, que le modèle
ne tient pas.

**Écart faible (a) : le décompte des trente années n'est pas tranché, ni dit.** E9 prend
1981 à 2010 sans dire que 1981 est une année partielle (3 771,63 € de cotisation revalorisée,
contre 4 828,46 € en 1982 : l'activité commence au 22e anniversaire, le 10 mars). Le texte
compte des « années de cotisation » et y range les années exonérées ou réduites ; il ne dit
pas si une première année incomplète compte pour une. Les lectures, chiffrées au même cas
(2027, un an de report ; 2031, cinq ans) :

| trente années | cotisations revalorisées | texte | de trop | (cinq ans) de trop |
|---|---|---|---|---|
| 1981 à 2010, l'année partielle comptée (E9) | 184 754,1840 € | 563,50 € | 579,38 € | 3 994,94 € |
| 1982 à 2011, l'année partielle non comptée | 190 880,0248 € | 582,18 € | 560,70 € | 3 894,81 € |
| 1981 à 2011, borne d'une durée de trente ans comptée de mars 1981 | 194 651,6538 € | 593,69 € | 549,19 € | 3 833,16 € |

L'erreur tient sous toutes : au moins 549,19 € par an pour un an de report, 3 833,16 €
pour cinq. La première lecture est la plus naturelle (la cotisation de la Cipav est
annuelle, et la première année en est une) ; la correction devra la dire, avec ses
bornes.

**Écart faible (b) : la règle d'avant le 1er juillet 2026, déclarée « probable », non
chiffrée.** E9 écrit « l'écart y est probable, non lu au texte officiel » : c'est un point
non tranché (l'article 3.15 des statuts au seul Bulletin officiel ; l'arrêté du 20 mars
2023, JORFARTI000047334800, 17°, b) le complète par « Pour la détermination des trente
années de cotisation, les années au titre desquelles l'adhérent a obtenu une exonération ou
une réduction de cotisation sont prises en compte. », et son a) y supprime « , telles
qu'elles sont définies à l'article 3.6 », sans montrer l'alinéa qui limite l'assiette).
Les deux lectures, chiffrées : née le 10 mars 1957, même carrière, pension au 1er janvier
2026 (68 ans et 9 mois, un an de report entier depuis 67 ans), le modèle sert 22 677,41 €
(« cotisations revalorisées 354,058 € × rendement 6.10% × coefficient de majoration
1.0500 ») ; si les statuts majoraient tous les points, rien de trop ; s'ils majoraient
les seules trente premières années (cotisations de 1979, partielle, à 2025 : 354 057,8613 € ;
de 1979 à 2008 : 168 552,9726 €), 0,00305 × 354 057,8613 = 1 062,1736 + 17,7029 =
1 079,8765 € contre 0,00305 × 168 552,9726 = 505,6589 + 8,4276 = 514,0866 €, **565,79 € par
an de trop** (542,83 € ou 537,96 € sous les deux autres décomptes, 1980 à 2009 ou 1979 à
2009). La source de la caisse (fiche
pratique de 2022) penche pour la seconde ; seul le Bulletin officiel tranche (la file des
fac-similés, `138/2026-11-05-la-file-des-fac-similes.md`).

**Remarque.** L'erreur est écrite au `sources.a_relire` de `decret_2026_418_liberaux`,
fiche qui n'est pas lue au droit, et non en approximation d'une version : la correction
annoncée la rangera où la règle se versionne (`surcote_par_age_seul`, ou la période de la
Cipav qui naîtra le 1er juillet 2026).

## 2. L'article 5-3 : conforme

Article 5-3 (même article 20 ; LEGIARTI000054168512) : « La date d'effet de la pension de
retraite complémentaire est fixée au premier jour du mois qui suit la demande prévue à
l'article 5-1. » Le modèle date la pension au premier jour d'un mois (1er juillet 2026,
2027, 2031 aux essais) ; la Cipav est hors du candidat 23 (le trimestre civil), comme E7
l'avait déjà établi (`2026-11-06-carte-des-fiches-cipav-lue-au-droit.md`). **Conforme.**
Les citations de l'article 5-1, 2°, a) et b), sont exactes.

## 3. L'inventaire des 31 articles

**Le compte : exact.** L'index JORF tient 32 documents d'articles sous le décret ; le
32e, JORFARTI000054153640, étiqueté « art. 8 », est la fin de l'article 18 (« Peuvent
être exonérés de la cotisation au régime de prestations complémentaires de vieillesse, à
compter de l'année suivant celle de leur soixante-dixième anniversaire, les auxiliaires
médicaux […] » ; « 7° A l'article 9 […] 9° A la première phrase de l'article 11 ») : le
décret a bien 31 articles. Les articles 2 à 28 modifient chacun un des vingt-sept décrets
des visas ; l'article 1er abroge l'article D. 641-6 du code de la sécurité sociale ; 29,
30 et 31 comme E9 les dit.

**Le décret de chaque article : exact.** Rouverts un à un (la première phrase de chacun) :
2, n° 49-578 ; 3, n° 49-579 (« Le décret du 49-579 », sic) ; 4, n° 49-580 ; 5, du 6 janvier
1950 ; 6, du 21 octobre 1950 ; 7, du 3 mars 1951 ; 8, du 21 mai 1953 ; 9, du 18 octobre
1955 ; 10, du 4 juillet 1960 ; 11, du 28 décembre 1961 ; 12, du 23 décembre 1965 ; 13, du
22 décembre 1967 ; 14, du 10 octobre 1968 ; 15, du 4 septembre 1970 ; 16, du 27 octobre
1972 ; 17, du 20 mai 1974 ; 18, du 23 septembre 1975 ; 19, du 28 février 1978 ; 20, n°
79-262 ; 21, n° 79-263 ; 22, du 27 mars 1979 ; 23, du 3 août 1981 ; 24, du 24 novembre
1981 ; 25, du 22 février 1984 ; 26, du 5 avril 1984 ; 27, du 26 décembre 2003 ; 28, du 30
décembre 2016. Les phrases citées par E9 (classe B la première année à la CARPV, « Sauf
option pour la classe B, l'affilié est inscrit d'office en classe A » à la CAVEC, « en
classe 3 pendant les deux premières années » à la CAVP ; les exonérations de « 100 %,
75 %, 50 % ou 25 % » de l'article 13) : exactes.

**Écart faible (c) : les seize décrets ne sont pas « non identifiés », et l'article 25 est
la complémentaire de la CARPIMKO.** Les visas nomment le régime de chacun ; E9 range
l'article 25 parmi les « régimes complémentaires spéciaux, prestations complémentaires de
vieillesse, invalidité-décès ; leur régime reste à rapporter ». Or le visa : « décret n°
84-143 du 22 février 1984 modifié relatif au régime d'assurance vieillesse complémentaire
des infirmiers, masseurs-kinésithérapeutes, pédicures, orthophonistes et orthoptistes » :
le régime complémentaire de la CARPIMKO lui-même, que citent dans sa rédaction du
1er juillet 2026 `carpimko_assiette_2026` (« décret n° 84-143, article 2, rédaction du
décret n° 2026-418 », LEGIARTI000054168663) et `carpimko_ages_2015` (« décret n° 84-143,
article 5, rédaction du 1er juillet 2026 ») ; la fiche du décret elle-même l'écrit (« les
sections de santé (articles 3 à 6, 16 et 25) », « CARPIMKO »). De même, l'article 16
(décret n° 72-968, prestations supplémentaires des médecins) est cité par
`asv_medecins_points`, les articles 18 et 24 (décrets nos 75-891 et 81-1046) par
`asv_autres_professions_de_sante`. Les autres : invalidité-décès (9, 10, 11, 12, 14, 15,
17, 23, 28), prestations complémentaires (19, 26), le régime spécial des notaires de Colmar
(7). L'article 25 n'écrit rien de la liquidation qui ne soit un rachat : « La différence
entre l'abattement appliqué sur la retraite du régime complémentaire […] et l'abattement
appliqué sur la retraite du régime de base […] peut faire l'objet d'un rachat », au
coefficient de 11,9 à 60 ans jusqu'à 10,6 à 64 ans ; l'affirmation de E9 (« hors de la
Cipav, aucune ne touche l'âge, la minoration ou la majoration de la liquidation ; elles
règlent […] les rachats ») tient donc. De même l'article 4-4 nouveau du décret n° 49-579
(trois trimestres par enfant aux femmes médecins) : des périodes « assimilées », qui ne
servent qu'au rachat de points (article 4-2, I).

**Écart faible (d) : l'article 13 n'est pas « que nulle fiche ne cite ».**
`cavamac_minoration_age_seul` (lignes 315 à 318) cite le « décret n° 67-1169 du 22
décembre 1967, article 4, dans la rédaction du décret n° 2026-418, en vigueur le 1er
juillet 2026 », et la fiche du décret le lit déjà (« la CAVAMAC (13) »). Le résumé de E9,
« cotisation au prorata de l'année de cessation », omet que c'est une faculté :
« la faculté de verser, en plus de la cotisation normale de l'exercice, une cotisation
supplémentaire de fin de carrière », « calculée au prorata du temps écoulé entre le 1 er
janvier précédant la date de cessation et cette dernière date ».

Ni (c) ni (d) n'a d'effet sur un montant : la lecture inscrite à la fiche (« chacun
rapporté au décret qu'il modifie ») est vraie ; le rattachement aux fiches est à reprendre
quand la fiche du décret sera lue au droit.

## 4. Les quatre reprises de R-E9 : conformes

1. **La CAVAMAC d'avant 2011.** Rouverts : JORFARTI000002036105 (« sont approuvées les
   modifications apportées aux statuts du régime d'assurance vieillesse complémentaire
   (art. 4) de la section professionnelle des agents généraux d'assurance ») et
   JORFARTI000001070359 (« Nota. - L'arrêté du 17 décembre 2001 sera publié intégralement
   au Bulletin officiel no 2002-04 ») ; JORFARTI000001665767 (« (articles 3, 8 bis, 17 et
   24) »), JORFARTI000002053081 (« Le présent arrêté entrera en vigueur le 1er janvier
   2004. »), JORFARTI000001280567 (« Article 17 L'article 17 est abrogé. Article 24
   L'article 24 est abrogé. ») ; JORFARTI000017890646 (« articles 1er, 3, 4, 5 ») et
   JORFARTI000017890649 (« égale à 6,30 % du montant des commissions et rémunérations ») ;
   les décrets nos 2001-864 (JORFARTI000001234936, « dix » devient « douze », « 127,5 % »
   devient « 129,5 % ») et 2003-1255 (JORFARTI000002053080, « appelée à hauteur de 142,9 %
   au titre des années 2004 à 2011 inclus »). Au titre « agents généraux d'assurance »,
   jusqu'en 2011, sans borne : `enfant OR enfants OR enfance` ne rend que l'arrêté du 23
   juin 2011 (JORFARTI000024270173, « Article 18 Majoration pour enfant ») et celui du 28
   juin 2011 (invalidité-décès) ; `majoration OR majoré OR bonification` ajoute les
   décrets nos 92-1372 et 97-1056 (« La majoration de cotisation afférente à la fraction du
   taux d'appel excédant 100 % n'ouvre pas de droit supplémentaire »), l'annexe
   invalidité-décès de 2003 et les deux arrêtés de 2007, aucun sur l'enfant. **Conforme.**
2. **L'article 8 du règlement de 2026.** JORFARTI000054436046 (publié le 17 juillet
   2026) : « Le nombre des points de retraite acquis dans le présent régime est majoré de
   5 % au profit de l'adhérent qui […] déclare fiscalement à sa charge un enfant ouvrant
   droit, en application des premier et deuxième alinéas de l'article L. 541-1 […], soit
   à l'allocation aux adultes handicapés prévue à l'article L. 821-1 du code de la
   sécurité sociale. » ; article 2 (JORFARTI000054436044) : « Le présent arrêté sera
   publié au Journal officiel de la République française. » : sans date propre, il
   s'applique le lendemain de sa publication, le 18 juillet 2026. L'article 19 des
   statuts de 2011 (JORFARTI000024270173) écrit « en vertu » et s'arrête à « l'article L.
   245-1 du code de l'action sociale et des familles ». **Conforme.**
3. **La réversion de la CAVEC.** L'arrêté du 4 juillet 2025, article 20
   (JORFARTI000051849616) : « Le montant de la première pension personnelle et de la
   pension de réversion relatives au régime d'assurance vieillesse complémentaire des
   assurés ayant eu au moins trois enfants est majoré de 10 % ». Aucune fiche
   `*reversion*` ne nomme `cavec_complementaire` ; le code rend `non_portee` quand le
   régime n'a pas de fiche (`droit/reversion.py`, ligne 1820 ;
   `moteur/js/droit/reversion.js`, ligne 1684) ou que sa version n'est pas portée (ligne
   2177 ; ligne 2073) ; `cavec_minoration_age_seul` (ligne 251) : « Le modèle ne sert
   aucune réversion de la CAVEC ». **Conforme.**
4. **Le test « au texte ».** `MAJORATIONS_AUX_DATES_QUI_COMPTENT` : les sept dates
   refaites (âge compté du premier du mois qui suit la naissance : 1er juillet 2011, 1er
   janvier 2012, 1er juillet et 1er août 2025, 1er décembre 1999, 1er janvier 2000, 1er
   juillet 2026) ; la lecture du texte, le taux servi et l'écart déclaré séparés ;
   `test_les_lectures_…_sont_declarees` exige qu'un cas porte un écart si et seulement si
   le modèle n'est pas la lecture unique, et que la fiche le déclare (trois écarts). Les
   tests de la zone (`test_sections_liberales.py`, `test_carte.py`, `test_textes.py`) :
   92 verts ; sous `PRESOMPTIONS_DECALEES=1`, 91 et un sauté (« le portage lit ses
   présomptions dans le paquet, que la mesure ne décale pas »). **Conforme.**

## Ce qui repart en « -bis »

À la correction de la Cipav (avec l'erreur, que cette relecture confirme) : dire le
décompte des trente années et ses bornes (a) ; chiffrer et déclarer comme non tranchée la
règle d'avant le 1er juillet 2026, aux deux lectures (b). À la lecture au droit de
`decret_2026_418_liberaux` : rattacher l'article 25 à la CARPIMKO, les articles 16, 18 et
24 aux fiches des prestations supplémentaires, l'article 13 à
`cavamac_minoration_age_seul` (c, d). Aucune erreur neuve dans le modèle.
