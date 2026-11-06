# Les fiches communes des sections libérales lues au droit : la majoration pour enfants, et les écarts de R-E8

File E8, le 6 novembre 2026 (action 130, vague 11, sur Opus). Deux temps : les cinq écarts
faibles de la relecture R-E8 (commit 316c490) repris aux sources ; puis, des quatre fiches
communes aux sections libérales qu'E7 a laissées, une lue au droit,
`sections_liberales_majoration_enfants`. Les trois autres (`surcote_par_age_seul`,
`cotisation_par_classes_liberales`, `decret_2026_418_liberaux`) restent : la session s'arrête
là, son contexte long (voir « Ce qui reste »). Aucune règle du modèle n'est corrigée.

**Méthode.** Les index de la DILA récupérés puis mis à jour (`dila_index.py --recuperer`,
`--mettre-a-jour`) : JORF au 6 novembre 2026 (incrément 20261106-002608), LEGI au 5
novembre (20261105-214938). Chaque texte ouvert par `dila_cherche.py --texte`, ses passages
par `--motif` ; les textes modificatifs relevés par titre (`--titre`), sans borne
(`--limite 200` à 300, jamais atteinte), puis chacun fouillé (« enfant », « bonification »,
« majoration », « rticle 18 »). Les essais du modèle par `servi_et_refait`
(`tests/outils_pont.py`), le portage servant et le moteur Python refaisant, le 6 novembre
2026 : une mère de trois enfants, née un 10 mars, au double du salaire moyen depuis 22 ans
(`salaire` 2, `debut` 22, `profil` plat), montants en euros de 2026 (`euros` 2026).

## 1. Les cinq écarts faibles de R-E8, revus au texte

1. **La version d'avant 2023 de `cipav_seconde_tranche` ne citait que les huit classes de
   2013.** Lu dans LEGI : LEGIARTI000006767473 (1979-01-01 → 1985-06-21),
   LEGIARTI000006767474 (1985-06-21 → 2012-12-30), LEGIARTI000026885130 (2012-12-30 →
   2013-01-01) portent tous trois « Le régime d'assurance vieillesse complémentaire
   institué par l'article 1er comporte six classes de cotisation : Classe 1 portant
   attribution de quatre points de retraite ; [...] Classe 10 portant attribution de
   quarante points de retraite. » ; celle de 1985 ajoute « La cotisation ainsi fixée peut
   faire l'objet d'un appel réduit dans les conditions fixées par les statuts prévus à
   l'article 5. », celle de 2012 « son revenu d'activité tel que défini à l'article
   L. 131-6 du code de la sécurité sociale ». **Confirmé ; corrigé** : les trois rédactions
   citées dans la version `classes_d_avant_2023`. Sans effet sur un montant (la version
   renvoie à `cotisation_par_classes_liberales`).
2. **Le décret n° 2026-239 nomme la Cipav.** JORFARTI000053748628, l'annexe des
   statuts-types : notes 51 et 52, « La caisse (hors CIPAV) choisit entre la possibilité
   prévue à l'article R. 642-2 du code de la sécurité sociale et des dispositions ad hoc »
   ; ni « classe », ni « points », ni « date d'effet », ni « enfant » dans ses 41 843
   caractères ; en vigueur le 1er juillet 2026 (article 2, JORFARTI000053748625). Aucun
   texte ne le modifie (recherche de « 2026-239 » : trois arrêtés qui le visent, des 10
   juillet et 21 septembre 2026). **Confirmé ; corrigé** : nommé parmi les textes sans
   effet de `cipav_seconde_tranche`.
3. **L'enjeu des taux de 2026.** Refait à la main, sous l'hypothèse de R-E8 (9 % et 22 %,
   les taux de 2023 et 2024, au lieu des 11 % et 21 % que le modèle reconduit), au plafond
   de 2026, P = 4 005 × 12 = 48 060 € (arrêté du 22 décembre 2025), et au coût du point de
   2025, 47,40 €, servi à 2,8914 € (0,061 × 47,40) : un euro de cotisation rend 0,061 €.
   L'écart de cotisation, modèle moins hypothèse, à un revenu R :
   - R ≤ P : (0,11 − 0,09) × R = 0,02 R ; au plus 0,02 × 48 060 = 961,20 € ;
     961,20 / 47,40 = 20,2785 points ; 961,20 × 0,061 = 58,6332, **+58,63 €** par an ;
   - P < R ≤ 4 P : 0,02 P − 0,01 (R − P) ; nul quand 0,01 (R − P) = 961,20, R − P =
     96 120, R = 144 180 € (trois plafonds) ;
   - R ≥ 4 P = 192 240 € : 961,20 − 0,01 × 144 180 = 961,20 − 1 441,80 = −480,60 € ;
     −480,60 / 47,40 = −10,1392 points ; −480,60 × 0,061 = −29,3166, **−29,32 €** par an.
   Les deux cas de E7 : à 40 000 €, 800,00 € et 800,00 / 47,40 = 16,8776 points, 800,00 ×
   0,061 = 48,80 € ; à 150 000 €, 0,11 × 48 060 + 0,21 × 101 940 = 5 286,60 + 21 407,40 =
   26 694,00 € contre 4 325,40 + 22 426,80 = 26 752,20 €, −58,20 €, −1,2278 point, −58,20
   × 0,061 = −3,5502, −3,55 €. E7 écrivait « 16,88 points, 48,80 € » et « 1,23 point,
   3,55 € » : les points arrondis au centième et l'euro tiré des points non arrondis, d'où
   les 48,81 € et 3,56 € de R-E8 (16,88 × 2,8914 = 48,8068 ; 1,23 × 2,8914 = 3,5564).
   Les points arrondis à la décimale, comme le veut le texte, déplacent chaque écart
   d'au plus 0,1 point, 0,1 × 2,8914 = 0,29 € : à 40 000 €, 4 400 / 47,40 = 92,827 → 92,8
   et 3 600 / 47,40 = 75,949 → 75,9, 16,9 points, 48,86 € ; à 150 000 €, 26 694,00 /
   47,40 = 563,165 → 563,2 et 26 752,20 / 47,40 = 564,392 → 564,4, −1,2 point, −3,47 € ;
   au plafond, 5 286,60 / 47,40 = 111,531 → 111,5 et 4 325,40 / 47,40 = 91,253 → 91,3,
   20,2 points, 58,41 € ; à quatre plafonds, 35 564,40 / 47,40 = 750,304 → 750,3 et
   36 045,00 / 47,40 = 760,443 → 760,4, −10,1 points, −29,20 €. **Confirmé ; corrigé** :
   l'approximation `depuis_2026` de `cipav_seconde_tranche` dit désormais l'enjeu de
   −29,32 € à +58,63 € par an et par exercice, nul à trois plafonds, et ses arrondis. Hors
   des notes, l'enjeu n'était écrit que là (`grep` de « 48,80 € » dans `data`, `docs`,
   `src`, `tests`, `scripts`, hors les notes et le journal).
4. **L'article 2 de l'arrêté du 7 janvier 2025 ne « charge » de rien.** JORFARTI000050962836 :
   « Le présent arrêté sera publié au Journal officiel de la République française. »
   **Confirmé.** L'erreur n'est que dans la note de E6-bis, un récit, qui ne se récrit pas ;
   aucune fiche ne la porte (`grep` de « charge de l'exécution » dans les fiches de la CARMF
   et de l'ASV). La conclusion de E6-bis tient : sans date, le lendemain de la publication.
5. **E6-bis mené sur Sonnet** : le commit 8c955fe le porte. Dit, sans conséquence.

## 2. `sections_liberales_majoration_enfants`, lue au droit

La fiche avait trois régimes, `cavamac_complementaire`, `cavec_complementaire`,
`cipav_complementaire`, et ni versions, ni domaine, ni étape. Le modèle déclare
`majoration_enfants` à la période de liquidation de chaque section
(`periode_de_liquidation`, la période de l'année de la date d'effet, ou celle de ses
`date_effet`) : 10 % de la pension dès trois enfants (`_taux_majoration_enfants`), sur la
pension minorée ou majorée par l'âge (`regimes_sans_anticipation` ne nomme que
l'Agirc-Arrco : le coefficient reste dans la part). Cinq versions sur
`liquidation.date_effet`.

**La CAVAMAC.** Arrêté du 23 juin 2011, publié le 29 : article 2 (JORFARTI000024270156),
« Les dispositions du présent arrêté entrent en vigueur le 1er juillet 2011. » ; article 3
(JORFARTI000024270158), l'arrêté du 22 décembre 1967 modifié « est abrogé » ; annexe
(JORFARTI000024270173), article 17, « les majorations prévues aux articles 18 et 19 des
présents statuts sont calculées sur la base du compte de droits majoré ou minoré de
l'adhérent », article 18, « Le nombre des points de retraite acquis dans le présent régime
est majoré de 10 % au profit de l'adhérent ayant eu au moins trois enfants [...] Sont
également considérés comme ouvrant droit à la majoration les enfants ayant été élevés par
l'adhérent et à sa charge effective pendant au moins neuf ans avant leur seizième
anniversaire. », article 19, 5 % par enfant handicapé à charge. Ni « 2011 » ni « 2012 »
dans les 29 983 caractères de l'annexe : aucune disposition transitoire. Les modifications
des statuts depuis (28 septembre 2012, 28 mars 2014, 4 mai 2016, 20 novembre 2017, 4 août
2023, 8 juillet 2025), toutes fouillées : aucune ne touche l'article 18 du régime
complémentaire (en 2016, le « 15° L'article 18 est ainsi modifié » porte sur les statuts
généraux, « Le conseil d'administration dé[...] » ; « enfant » n'y paraît pas ; en 2023, la
majoration pour report ; en 2025, le capital décès). Le règlement du 10 juillet 2026
(JORFARTI000054436046, publié le 17 juillet, article 2 : la publication seule, donc en
vigueur le 18), article 7, reprend mot pour mot l'article 18, l'article 8 le 19. Avant le
1er juillet 2011 : l'arrêté de 1967 et ses modifications de 1972, 1975 et 1983, toutes
« relatifs au régime d'assurance vieillesse complémentaire des agents généraux
d'assurances », n'ont dans l'index JORF que leur titre (JORFTEXT000000660274, …000283882,
…000831972, …000494188 ; celui de 1983 finit par « (ART. 15,15-BIS ET 16) »), et celui de
1975 un résumé de 86 caractères, « (MODIFICATION DES ART. 4, 5, 8 & 8 BIS, 10, 14, 15, 17
& 18 DES STATUTS DE LA CAISSE). » ;
des textes de la CAVAMAC d'avant le 23 juin 2011 qu'il porte au texte, aucun ne nomme
l'enfant (recherche « enfant OR enfants » au titre « agents généraux d'assurance »,
jusqu'en 2011 : le seul arrêté du 28 juin 2011 de l'invalidité-décès).

- **Erreur prouvée, déclarée, non corrigée : la CAVAMAC de juillet à décembre 2011.** Le
  modèle ne déclare la majoration qu'à sa période de 2012 (« servis à partir de 2012,
  première année pleine », `cavamac_complementaire.yaml`). Une pension qui prend effet du
  1er juillet au 1er décembre 2011 se liquide aux statuts de 2011, seuls en vigueur ; la
  lecture contraire n'a aucun texte. Essai : née le 10 mars 1946 (l'âge se compte du 1er
  avril, `Carriere.origine_des_ages`), partie à 65 ans et 3 mois, pension au 1er juillet
  2011 : 13 323,31 € de CAVAMAC, aucune majoration ; le texte en donne 0,10 × 13 323,31 =
  1 332,331, **1 332,33 € par an**. À 65 ans et 6 mois (1er octobre 2011), rien non plus
  (13 442,34 €) ; à 65 ans et 9 mois (1er janvier 2012), le modèle sert 1 382,64 € =
  0,10 × 13 826,36. Six dates d'effet touchées, de juillet à décembre 2011.
- **Manque : les statuts de 1967.** Le modèle ne sert rien avant le 1er juillet 2011 ; s'ils
  majoraient comme ceux de 2011, jusqu'à 10 % de la pension. Au fac-similé
  (`138/2026-11-05-la-file-des-fac-similes.md`).
- **Manque : les 5 % par enfant handicapé à charge** (article 19, puis 8) ; la saisie ne
  connaît pas cet enfant : 0,05 × 13 323,31 = 666,17 € par an et par enfant au cas de 2011.

**La CAVEC.** Arrêté du 4 juillet 2025, publié le 6 juillet (JORFARTI000051849616), annexe,
II (les statuts du régime complémentaire : le « II. - » au caractère 790, le « III. - » au
5 337, l'article 20 au 4 650), 10° : « Il est ajouté un article 20 ainsi rédigé : « Art.
20. - Bonification de la pension pour enfants. « Le montant de la première pension
personnelle et de la pension de réversion relatives au régime d'assurance vieillesse
complémentaire des assurés ayant eu au moins trois enfants est majoré de 10 % dans les
conditions fixées par les articles L. 643-1-1 et L. 351-12 du code de la sécurité sociale. »
; son article 2 (JORFARTI000051849614) ne dit que la publication : en vigueur le 7 juillet
2025. Le règlement du 10 juillet 2026 (JORFARTI000054435943), article 1.3.1, le reprend.
Avant : les statuts du 22 février 2008 (JORFARTI000018197778, 37 431 caractères), du 9
février 2012 (JORFARTI000025395367) et du 20 août 2018 (JORFARTI000037363871, 80 716
caractères) n'ont aucune « bonification » ; l'enfant n'y paraît qu'à la réversion et aux
rentes d'orphelins. Essai : née le 10 mars 1960, à 65 ans et 3 mois (1er juillet 2025),
32 178,71 €, rien ; à 65 ans et 4 mois (1er août 2025), 3 246,21 € = 0,10 × 32 462,07.
**Conforme.** À examiner, hors de cette fiche : la CAVEC majore aussi « la pension de
réversion » ; que la réversion reprenne la part de la majoration (`echeancier`,
`parts_de_la_majoration`) relève des fiches de la réversion, non ouvertes ici (candidat).

**La Cipav.** Décret n° 99-913, article 6 (LEGIARTI000006780306, en vigueur le 1er janvier
2000) : « Les droits acquis au titre des périodes d'activité postérieures au 1er janvier
2000 dans le régime complémentaire de la Caisse interprofessionnelle de prévoyance et
d'assurance vieillesse par les anciens affiliés de la Caisse autonome de retraite des
géomètres experts et des experts agricoles et fonciers peuvent bénéficier d'une
bonification pour enfants dans les conditions prévues par les statuts de ce régime. »
Décret n° 79-262, article 5-2, I (LEGIARTI000054168515, en vigueur le 1er juillet 2026 ;
décret n° 2026-418, articles 20 et 30) : « Il est majoré de 10 % au profit du demandeur
ayant eu au moins trois enfants. Le demandeur ne peut bénéficier de cette majoration s'il a
été privé de l'exercice de l'autorité parentale ou s'est vu retirer l'autorité parentale
[...] Cette majoration bénéficie également au demandeur qui a élevé au moins trois enfants
pendant 9 ans jusqu'à leur 16e anniversaire. » ; la majoration porte sur « le produit du
nombre de points acquis diminué, le cas échéant, du coefficient de réduction par la valeur
de service du point », ce que le modèle fait. Essais : née le 10 mars 1934, à 65 ans et 8
mois (1er décembre 1999), 4 033,95 €, rien ; à 65 ans et 9 mois (1er janvier 2000),
418,15 € = 0,10 × 4 181,48 ; née le 10 mars 1961, à 65 ans et 3 mois (1er juillet 2026),
2 102,74 € = 0,10 × 21 027,42. **Conforme depuis le 1er juillet 2026.**

- **Point non tranché : la Cipav avant 2000.** Première lecture, celle du modèle : rien
  avant la date où le décret n° 99-913 atteste la bonification. Seconde : le décret renvoie
  à une bonification déjà « prévue par les statuts de ce régime », à une date que seuls les
  statuts (Bulletin officiel) disent. Au cas du 1er décembre 1999 : 0 € ou 0,10 × 4 033,95 =
  403,395, 403,40 € par an.
- **Supposé : la forme de 2000 à 2026**, celle de l'article 5-2 ; et les anciens affiliés
  de la caisse des géomètres ne la reçoivent que sur leurs droits d'après 2000, que le
  modèle ne distingue pas (non mesuré).
- **Non portés** (les trois sections) : les enfants élevés neuf ans, le parent privé ou
  retiré de l'autorité parentale (non mesuré).

**Le 1er au 17 juillet 2026** : le décret n° 2026-418 en vigueur, les règlements de la
CAVAMAC et de la CAVEC pas encore ; leurs statuts majorent des mêmes 10 % : sans effet.

**Les tests.** Le test d'abord : `test_chaque_version_de_la_majoration_pour_enfants_des_sections_est_portee`
(`tests/test_sections_liberales.py`), vu rouge (la fiche sans versions), puis vert : à
chaque date d'effet, mois par mois, de 1990 à 2040, la majoration de la période de
liquidation de chaque section est celle de la version de la date, 1 830 dates vues et les
six de la CAVAMAC de 2011 déclarées (le modèle 0, le texte 0,10). Puis
`test_la_majoration_pour_enfants_des_sections_aux_dates_qui_comptent_dans_les_deux_moteurs`,
vert d'emblée (il tient ce que le modèle rend) : les sept cas aux bornes ci-dessus, servis
par le portage et refaits par le moteur Python. La fiche entre dans `LUES_AU_DROIT`
(`tests/test_carte.py`) ; la carte compte 74 fiches et 425 manques (75 et 432 avant).

`python -m pytest -m rapide` : 11 rouges, tous `test_pages_en_dossier`, 4 554 verts ; sous
`PRESOMPTIONS_DECALEES=1`, les mêmes 11, 4 349 verts. `test_sections_liberales.py`,
`test_carte.py`, `test_textes.py`, `test_sections_sante.py`, en entier : 146 verts ; sous
`PRESOMPTIONS_DECALEES=1`, 145 et un sauté. `test_syntaxe_ancien_python.py`,
`test_coupures_au_mois.py` : verts. Le paquet refait est identique : il ne lit pas ces
fiches. Le cliquet des textes reste à 9 312.

## Ce qui reste

- **À la file E**, les trois autres fiches communes, à lire ensemble : `surcote_par_age_seul`
  (les articles 5-1 et 5-2 du décret n° 79-262 : minoration de 5 % par an, majoration réservée
  aux points des trente premières années, « un minimum de trente années d'affiliation à la
  CIPAV » ; l'arrêté du 4 août 2023 de la CAVAMAC, « Cette majoration ne s'applique pas aux
  années de cotisations versées dans le cadre du dispositif prévu à l'article 14 »),
  `cotisation_par_classes_liberales` (les six classes de 1979 à 2012 de la Cipav, lues
  ci-dessus), `decret_2026_418_liberaux` (les règlements des neuf sections du 10 juillet
  2026, publiés le 17, en vigueur le 18 : JORFARTI000054436046, …054435943, …054435995,
  …054435969, …054436031, …054435915, …054435749, …054435859, …054436087).
- **Au propriétaire**, l'erreur de la CAVAMAC en 2011 (1 332,33 € par an au cas posé) ; le
  non-tranché de la Cipav avant 2000 (403,40 €) ; les statuts de la CAVAMAC de 1967, au
  fac-similé, et ceux de la Cipav d'avant 2026, au Bulletin officiel.
- **Candidat, hors de la tâche** : la réversion de la CAVEC, que ses statuts de 2025 et son
  règlement de 2026 majorent aussi de 10 %.
