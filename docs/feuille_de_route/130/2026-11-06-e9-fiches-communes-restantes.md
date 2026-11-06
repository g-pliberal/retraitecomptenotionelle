# Les fiches communes aux sections : les écarts de R-E9 repris, le décret n° 2026-418 entamé

File E9, le 6 novembre 2026 (action 130, vague 11, sur Opus). Deux temps : reprendre aux
sources les quatre écarts faibles que la relecture R-E9 (commit 00b4c15,
`2026-11-06-relecture-r-e9.md`) a trouvés dans E8 (commit 40d3fbc) ; puis lire au droit les
trois fiches communes qui restent (`surcote_par_age_seul`,
`cotisation_par_classes_liberales`, `decret_2026_418_liberaux`). Aucune règle du modèle ne
change ; aucune erreur n'est corrigée.

**Méthode.** `veille_droit.py` (rien de neuf à la base de la Cnav), `docs/veille_droit.md` ;
les index de la DILA récupérés puis mis à jour : JORF au 6 novembre 2026 (incrément
20261106-002608), LEGI au 5 novembre (20261105-214938). Chaque texte rouvert par
`dila_cherche.py --texte`, et les textes modificatifs relevés par titre, sans borne
(`--limite 500`, jamais atteinte). Les essais par les deux moteurs (`servi_et_refait`) et
par `acquerir` ; les montants refaits en décimal exact.

## Les quatre écarts de R-E9, repris au texte

1. **Les textes de la CAVAMAC d'avant 2011.** Au titre « agents généraux d'assurance »,
   jusqu'en 2011, sans borne : la requête `enfant OR enfants OR enfance` ne rend, avant le
   23 juin 2011, aucun document ; les textes de 1967 à 1992 n'ont que leur titre. Les trois
   arrêtés que R-E9 nomme, rouverts :
   - du 17 décembre 2001, publié le 28 décembre (JORFARTI000002036105) : « sont approuvées
     les modifications apportées aux statuts du régime d'assurance vieillesse
     complémentaire (art. 4) de la section professionnelle des agents généraux d'assurance
     » ; « Nota. - L'arrêté du 17 décembre 2001 sera publié intégralement au Bulletin
     officiel no 2002-04 » (JORFARTI000001070359) ;
   - du 26 décembre 2003, publié le 28 décembre : article 1er (JORFARTI000001665767), «
     (articles 3, 8 bis, 17 et 24) » ; article 2 (JORFARTI000002053081), « Le présent
     arrêté entrera en vigueur le 1er janvier 2004. » ; annexe (JORFARTI000001280567) :
     l'article 3 complété (adhérents nouvellement nommés, maintien sous le plancher),
     l'article 8 bis remplacé (validation de points de l'invalide), « Article 17 L'article
     17 est abrogé. Article 24 L'article 24 est abrogé. » — l'objet des deux articles
     abrogés ne se lit pas (statuts de 1967, au fac-similé) ;
   - l'autre arrêté du 17 décembre 2007, publié le 18 janvier 2008 : article 1er
     (JORFARTI000017890646), « articles 1er, 3, 4, 5 » ; annexe (JORFARTI000017890649) :
     adhérents, assiette, « La cotisation génératrice de droit due au début de chaque
     exercice est égale à 6,30 % », paiement et majorations de retard.
   Sont aussi au titre, sans l'enfant : les décrets nos 2001-864 (« le mot : « dix » est
   remplacé par le mot : « douze » », « 127,5 % » devient « 129,5 % ») et 2003-1255 (« A
   titre transitoire, elle est appelée à hauteur de 142,9 % au titre des années 2004 à 2011
   inclus. ») ; pour la base et les statuts généraux, l'arrêté du 17 décembre 2007 publié le
   15 janvier 2008 (JORFARTI000017871508, « statuts du régime d'assurance vieillesse de
   base ») et celui du 26 janvier 2011 (JORFARTI000023503093, « les statuts généraux et les
   statuts du régime d'assurance vieillesse de base »). **R-E9 confirmé** : l'inventaire de
   la fiche est complété (approximation `[aucune_avant_2000, cipav_depuis_2000]`,
   `cavamac_complementaire`) ; la conclusion ne change pas.
2. **L'article 8 du règlement de 2026.** Annexe de l'arrêté du 10 juillet 2026
   (JORFARTI000054436046), publié le 17 juillet ; article 2 (JORFARTI000054436044), « Le
   présent arrêté sera publié au Journal officiel de la République française. », en
   vigueur le 18. Article 8 : « [...] un enfant ouvrant droit, en application des premier
   et deuxième alinéas de l'article L. 541-1 du code de la sécurité sociale, à l'allocation
   d'éducation de l'enfant handicapé et à son complément ou, en lieu et place de ce
   dernier, de la prestation de compensation prévue par l'article L. 245-1 du code de
   l'action sociale et des familles, soit à l'allocation aux adultes handicapés prévue à
   l'article L. 821-1 du code de la sécurité sociale. » ; l'article 19 des statuts de 2011
   (JORFARTI000024270173) écrit « en vertu » et s'arrête à la prestation de compensation.
   **R-E9 confirmé** : le manque des 5 % couvre, depuis le 18 juillet 2026, l'enfant qui
   ouvre droit à l'AAH ; la fiche le dit.
3. **La réversion de la CAVEC.** `cavec_minoration_age_seul.yaml` déclare : « Le modèle ne
   sert aucune réversion de la CAVEC : aucune fiche de réversion ne nomme
   `cavec_complementaire`, et la ligne vaut zéro, motif `non_portee` » ; vérifié au code
   (`droit/reversion.py`, lignes 1820 et 2177 ; `moteur/js/droit/reversion.js`, lignes
   1684 et 2073) et aux fiches (aucune fiche `*reversion*` ne nomme
   `cavec_complementaire`). **R-E9 confirmé** : là où E8 l'avait écrit hors des notes — à la
   fiche, son approximation, son `effet` et ses `a_relire`, et au bloc « Reprise », parmi
   les candidats —, la majoration de la réversion est rangée dans l'écart déclaré de
   `cavec_minoration_age_seul`, et le candidat quitte le bloc.
4. **Le test « au texte ».** `MAJORATIONS_AUX_DATES_QUI_COMPTENT`
   (`tests/test_sections_liberales.py`) porte désormais, pour chaque cas, les lectures du
   texte (un taux ; deux quand le texte ne tranche pas ; `None` quand il atteste sans
   donner le taux), le taux servi, et l'approximation de la fiche qui déclare l'écart :
   | cas | date d'effet | texte | servi | écart déclaré |
   |---|---|---|---|---|
   | CAVAMAC | 1er juillet 2011 | 0,10 (statuts de 2011, art. 2 et 18) | 0 | `cavamac_depuis_juillet_2011` |
   | CAVAMAC | 1er janvier 2012 | 0,10 | 0,10 | — |
   | CAVEC | 1er juillet 2025 | 0 (statuts de 2018, sans « bonification ») | 0 | — |
   | CAVEC | 1er août 2025 | 0,10 (arrêté du 4 juillet 2025, art. 20) | 0,10 | — |
   | Cipav | 1er décembre 1999 | 0 ou 0,10, non tranché | 0 | `aucune_avant_2000` |
   | Cipav | 1er janvier 2000 | attestée, sans taux (décret n° 99-913, art. 6) | 0,10 | `cipav_depuis_2000` |
   | Cipav | 1er juillet 2026 | 0,10 (décret n° 79-262, art. 5-2) | 0,10 | — |
   La recherche de « bonification » au titre « experts comptables », sans borne, ne rend
   que l'arrêté du 4 juillet 2025 (JORFARTI000051849616) et le règlement de 2026
   (JORFARTI000054435943) : rien avant le 7 juillet 2025. Le test des deux moteurs vérifie
   le taux servi, et le dit ; un test neuf,
   `test_les_lectures_de_la_majoration_pour_enfants_des_sections_que_le_modele_ne_suit_pas_sont_declarees`,
   vu rouge (`TypeError` : l'ancien format), vérifie qu'un cas où le modèle n'est pas la
   lecture unique du texte porte son écart, et que la fiche le déclare (trois écarts). Le
   montant de la pension n'y est pas posé : le test vérifie un taux de la pension servie.

## Le second temps : où il s'arrête

La lecture au droit des trois fiches ne tient pas dans une session : `surcote_par_age_seul`
couvre sept régimes et leur histoire, `cotisation_par_classes_liberales` les classes de
toutes les sections, et le décret n° 2026-418 a 31 articles (197 071 caractères dans l'index) qui
modifient vingt-sept décrets. **E9 s'arrête au décret, entamé** ; aucune des trois fiches
n'entre à `LUES_AU_DROIT`, la carte reste à 74 fiches et 425 manques.

**Le décret, article par article** (JORF du 31 mai 2026, JORFTEXT000054153355) : chaque
article rapporté au décret qu'il modifie, et à la fiche lue au droit qui le cite :
- 1, « L'article D. 641-6 du code de la sécurité sociale est abrogé. » ; 29, les
  règlements ; 30, « Le présent décret entre en vigueur le 1 er juillet 2026. » ; 31,
  l'exécution ;
- 2, décret n° 49-578 (CPRN, `cprn_ages_decote_enfants`) ; 3, n° 49-579 (CARMF,
  `carmf_asv_minoration_enfants`) ; 4, n° 49-580 (CAVP, `cavp_minoration_deux_pentes`) ; 5,
  décret du 6 janvier 1950 (CARCDSF, `carcdsf_minoration_age_seul`) ; 6, du 21 octobre 1950
  (CARPV, `carpv_minoration_age_seul`) ; 8, du 21 mai 1953 (CAVEC,
  `cavec_minoration_age_seul`) ; 20, n° 79-262 (Cipav, `cipav_seconde_tranche`,
  `sections_liberales_majoration_enfants`) ; 22, du 27 mars 1979 (CAVOM,
  `cavom_assiette_2016`) ;
- 13, décret du 22 décembre 1967 (CAVAMAC), que nulle fiche ne cite : exonérations de 100,
  75, 50 ou 25 %, cotisation au prorata de l'année de cessation ; 21, n° 79-263, et 27, du
  26 décembre 2003, l'invalidité-décès de la Cipav et de la CAVAMAC ;
- 7, 9 à 12, 14 à 19, 23 à 26 et 28 : décrets des 3 mars 1951, 18 octobre 1955, 4 juillet
  1960, 28 décembre 1961, 23 décembre 1965, 10 octobre 1968, 4 septembre 1970, 27 octobre
  1972, 20 mai 1974, 23 septembre 1975, 28 février 1978, 3 août 1981, 24 novembre 1981, 22
  février 1984, 5 avril 1984 et 30 décembre 2016 : régimes complémentaires spéciaux,
  prestations complémentaires de vieillesse, invalidité-décès ; leur régime reste à
  rapporter, décret par décret.
Les phrases de ces articles qui chiffrent (un pourcentage, un âge, une classe, un taux,
une valeur de point), relevées par script : hors de la Cipav, aucune ne touche l'âge, la
minoration ou la majoration de la liquidation ; elles règlent l'affiliation, les classes
(la classe d'office de la première année : B à la CARPV, article 6 ; A à la CAVEC, article
8 ; 3 à la CAVP pendant deux ans, article 4 ; la classe des notaires, de leur âge et de
leur serment, annexe 1, article 2), les dispenses, les rachats, les cotisations
volontaires. Ce qui relève des classes va à `cotisation_par_classes_liberales`.

**L'article 20, lu en entier** (JORFARTI000054153655), confronté au modèle
(`cipav_complementaire.yaml`, périodes de 2025 ; `surcote_points`,
`droit/liquider.py`) :
- article 5-2, II : « L'affilié qui a atteint l'âge prévu au a du 1° de l'article 5-1 et
  comptant un minimum de trente années d'affiliation à la CIPAV, peut différer la date
  d'entrée en jouissance de la pension de retraite complémentaire de 1 à 5 ans. « Le
  compte de points qui est alors établi est majoré de 5% par année entière de prorogation.
  « Cette majoration s'applique uniquement aux points acquis au titre des trente premières
  années de cotisation à la CIPAV. » — l'âge du a du 1° est « l'âge du taux plein prévu au
  1° de l'article L. 351-8 » ; le modèle : `age_taux_plein_par_generation:
  age_annulation_decote`, `surcote_par_trimestre: 0.0125` au pas de 4 trimestres (5 % par
  année entière), 20 trimestres au plus, `surcote_affiliation_minimale_trimestres: 120` :
  **conforme**, sauf la dernière phrase : **erreur prouvée**, la lecture contraire
  (majorer tous les points) n'ayant aucun texte pour elle depuis le 1er juillet 2026 ;
- article 5-3 : « La date d'effet de la pension de retraite complémentaire est fixée au
  premier jour du mois qui suit la demande prévue à l'article 5-1. » — au mois, comme le
  modèle : la Cipav est bien hors du candidat 23 ;
- article 5-1, 2° : « a) [...] avec application des mêmes coefficients de réduction que le
  régime de base si la pension au régime de base a été liquidée avec des coefficients de
  réduction ; « b) [...] avec application d'un taux de minoration de 5 % par année séparant
  l'âge de l'assuré à la date de la liquidation de l'âge requis pour bénéficier de la
  pension de retraite complémentaire à taux plein. » — lu, non confronté : la minoration
  n'est dans aucune des trois fiches ; le modèle sert `decote_par_trimestre: 0.0125` avec la
  durée requise du régime, à confronter au coefficient de la base (le cas a) et au « par
  année » du cas b, entière ou non.

**Le calcul de l'erreur.** Née le 10 mars 1959 (l'âge se compte du 1er avril 1959),
libérale de la Cipav au double du salaire moyen depuis 22 ans (`salaire` 2, `debut` 22,
`profil` plat, `euros` 2026, `enfants` 0) ; la carrière de la saisie, ses cotisations
revalorisées par `acquerir`, année par année, de 1981 à la liquidation ; le rendement du
modèle, 6,10 %. Les trente premières années de cotisation : 1981 à 2010.
- À 68 ans et 3 mois, pension au 1er juillet 2027, une année entière au-delà de 67 ans
  (1er avril 2026) : cotisations revalorisées de 1981 à 2027, 374 715,4414 € (le moteur
  imprime « cotisations revalorisées 374,715 € × rendement 6.10% × coefficient de
  majoration 1.0500 », 24 000,52 €) ; de 1981 à 2010, 184 754,1840 €. Le modèle : 0,05 ×
  374 715,4414 × 0,061 = 1 142,882096 € ; le texte : 0,05 × 184 754,1840 × 0,061 =
  563,500261 € ; **579,38 € par an de trop**.
- À 72 ans et 3 mois, au 1er juillet 2031, cinq années : 459 993,6709 € et 198 030,4407 € ;
  0,25 × 459 993,6709 × 0,061 = 7 014,903481 € contre 0,25 × 198 030,4407 × 0,061 =
  3 019,964221 € ; **3 994,94 € par an de trop** (le moteur sert 35 074,52 €, coefficient
  1,25).
Avant le 1er juillet 2026, la règle est à l'article 3.15 des statuts, au seul Bulletin
officiel ; l'arrêté du 20 mars 2023 (JORFARTI000047334800, 17°) le complète par « Pour la
détermination des trente années de cotisation, les années au titre desquelles l'adhérent a
obtenu une exonération ou une réduction de cotisation sont prises en compte. » : l'écart y
est probable, non lu au texte officiel. Déclaré à `decret_2026_418_liberaux`
(`sources.a_relire`) ; `surcote_par_age_seul` n'a pas encore de versions où l'écrire.

## Ce qui reste, et par quoi commencer

- **`decret_2026_418_liberaux`** : la fiche porte un texte, non une règle, à plusieurs
  étapes (cotiser, liquider) ; sa lecture au droit demande d'abord de décider sa forme
  (versions sur `liquidation.date_effet` et sur l'année, ou renvoi de chaque article à la
  fiche de sa règle), puis de rapporter les seize décrets non identifiés à leur régime.
- **`surcote_par_age_seul`** : sept régimes ; y écrire l'erreur de la Cipav dans ses
  versions, à partir du 1er juillet 2026, et la règle des statuts d'avant.
- **`cotisation_par_classes_liberales`** : les classes d'office de la première année (CARPV,
  CAVEC, CAVP), la classe des notaires par âge et serment (article 2, annexe 1).
- **Candidats** : la minoration de la Cipav (article 5-1, 2°) à confronter ; l'article 13
  (CAVAMAC), que nulle fiche ne cite.
- **Le candidat 23** (date d'effet au trimestre civil) : aucune des trois fiches ne le porte
  à ce jour ; l'article 5-3 confirme que la Cipav en est hors.

Tests : `tests/test_sections_liberales.py`, `tests/test_carte.py`, `tests/test_textes.py`,
92 verts ; sous `PRESOMPTIONS_DECALEES=1`, 91 et un sauté.
