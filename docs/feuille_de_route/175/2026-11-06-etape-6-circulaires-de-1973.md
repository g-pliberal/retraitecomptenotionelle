# Étape 6, circulaires : les 43 d'avant 1973 restées à lire, puis celles de 1973

**Le 6 novembre 2026, ce qui est fait.**

- *Les textes* : les 31 références de 1936 à 1959 et les 12 de 1960 à 1972 que les notes
  de G8 et de G9 nomment à lire, puis les 27 références sans thème et à lire de 1973 dont
  le titre commence par « Circulaire », « Lettre », « Instruction », « Note
  d'information » ou « Diffusion d'instructions ». Le registre en comptait 1 866 de 1973
  à 2026 ce matin, non 1 886 : la note de G9 les comptait autrement. Borne : la fin de
  1973 ; 1974 aurait passé ce que la session pouvait lire.
- *La lecture* : les 70, relues par l'API le 6 novembre 2026 à 10 h 08 et 10 h 16 UTC,
  toutes servies ; 68 en page, lues en entier (les deux conventions de 1973, avec le
  Portugal et la Turquie, par leurs titres et leur partie vieillesse) ; deux PDF sous
  `/Pdf/` : `lettre_Fnoss_1958_22091958.pdf`, lu par son texte, et l'annexe de la
  circulaire n° 113 SS, deux pages numérisées, lues en image à 200 points par pouce. Pour
  le rapprochement, les quinze textes qui les citent dans `citations.csv`, relus de même.
- *Le rapprochement des 43.* Trois se rapprochent : `LE_MIN_25081954`, dont l'en-tête
  porte « Lettre ministérielle n° 21984 du 25 août 1954 », le numéro de sa jumelle
  `LE_MIN_25081954_21984`, au mot près ; `LE_MIN_25101961`, que la lettre ministérielle
  du 20 octobre 1981 (`LE_MIN_20101981`) lie et cite, « prises par lettre ministérielle
  n° 32 25AG du 25 octobre 1961 », le 3225/AG de l'API ; l'annexe de la circulaire
  n° 113 SS, qui la lie : « La vignette modèle n° S. 2211 est un imprimé de format 27 X
  13 [...] de deux volets détachables », et la vignette porte à son pied « Réf. S 2211 ».
  Les 40 autres ne sont reliées que par leur date et leur origine — quatre portent en
  en-tête un numéro que la base ne donne pas (« Circulaire ministérielle n° 57 SS du 16
  mai 1956 », « Lettre N° 4004 SC/DA. 1 du 10 Juillet 1951 », « Lettre N° 4798 SC/DA. 1
  du 7 août 1951 », « Lettre-circulaire n° 36/062 du 13 juin 1962 ») : lues en entier,
  rangées par ce qu'elles disent. Aucune ne reste à lire.
- *Le rapprochement des 27 de 1973* : 19 par le numéro de l'API que porte leur en-tête,
  ou par leur identifiant (« Circulaire n° 102bis/73 », « n° 28 bis/73 », « n° 54 bis
  73 », que l'API numérote 102/73, 28/73 et 54/73 ; `CR_CN_5473_2_06071973`, la seconde
  54/73 du jour) ; 8 par leur date seule, lues en entier : `LC_22111973` (en-tête
  « n° 49/1973 », que la base ne donne pas), `LE_CNAM_11_19071973`, `LE_CN_06071973`,
  `LE_CN_18041973`, `LE_CN_20121973`, `LE_MIN_01101973`, `LE_MIN_08081973`,
  `LE_MIN_22111973` (l'API 7919, un en-tête sans numéro).
- *Les sorts* : 70 références rangées, 55 `limite`, 15 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 70 lignes, colonnes et ordre
  gardés ; récrit à l'identique par `ecrire_registre`).

**Les 43, par ce qu'elles disent.**

- *À `minimum_vieillesse`* (17) — l'AVTS, l'allocation aux mères de famille, l'allocation
  de veuf ou de veuve de la loi du 23 août 1948, l'allocation supplémentaire :
  `LE_MIN_06011948` (les métayers non assujettis « ne peuvent bénéficier de l'allocation
  aux vieux travailleurs salariés ») ; `LE_FNOSS_04MDAB_11021954` (les années de salariat
  après une rente « pour l'attribution de l'allocation aux vieux travailleurs
  salariés ») ; `LE_MIN_03091953` (les périodes de 1914 à 1919 « seront désormais
  applicables aux ressortissants belges ») ; `LE_MIN_04051956`, `LE_MIN_28031956`,
  `LE_MIN_10061952` (l'allocation aux mères de famille : la nationalité des enfants,
  l'activité du mari « sur le territoire métropolitain », le non-cumul avec
  « l'allocation de la loi du 17 janvier 1948 ») ; `LE_MIN_11031959` (la dernière activité
  non salariée « insuffisante quant à l'importance de la rémunération ») ;
  `LE_MIN_13071950` (l'allocation de veuf ou de veuve) ; `LE_MIN_25081954` (comme sa
  jumelle) ; `LE_MIN_01031968` (l'allocation supplémentaire rétroactive, « le délai peut
  être fixé à trois mois au plus ») ; avec une autre fiche : `CR_MIN_58_25021947` et
  `inaptitude_au_travail` (« les mères de famille âgées de 60 à 65 ans qui seront
  reconnues inaptes ») ; `LE_MIN_06051949` et `residence_et_minimum_vieillesse`
  (« quinze années de résidence ininterrompue en France ») ; `LE_MIN_04041956` et
  `liquidation_regime_par_regime` (la rente de coordination du décret n° 50-132,
  « suspendue en cas d'attribution de ladite allocation ») ; `LE_MIN_30061950` et
  `reversion` (la pension de réversion « de l'article 76 de l'ordonnance du 19 octobre
  1945 »).
- *À `docs/limites/3-systeme-actuel.md`* (14, dont 8 avec une fiche ou un régime) : le
  service militaire « depuis le 1er juillet 1930 » (`LE_MIN_24101950`) et le chômage
  d'avant 1942 (`LC_17041948`), que la limite des périodes assimilées compte autrement ;
  l'assurance volontaire, avec `regimes/caisse_francais_etranger.yaml` — « un assuré
  obligatoire ne saurait, en principe, cotiser au titre de l'assurance volontaire »
  (`LE_MIN_30061951`), le Français à bord d'un navire étranger, qui « peut demander à
  bénéficier de l'assurance volontaire » (`LE_MIN_05061950`), les rachats des affiliés de
  la CIMR (`LE_FNOSS_21051964`) ; l'Algérie, avec `totalisation_des_periodes_etrangeres`
  (`LE_AUTRE_10071951`, l'affiliation des auxiliaires de la Défense nationale ;
  `LE_CN_09071966`, l'allocation viagère des rapatriés) ; les réfugiés du BOPRE, avec
  `chomage_non_indemnise` (`LE_MIN_29011963`) ; les assiettes et les taux forfaitaires —
  le taux réduit des artistes (`LC_13061962`), le personnel temporaire des maisons
  d'enfants (`LE_MIN_03081970_6106`), les apprentis (`LE_MIN_19101972`, que la circulaire
  Acoss n° 39, rangée là, cite mot pour mot), la vignette des spectacles occasionnels
  (l'annexe de la n° 113 SS, rangée comme elle) ; les assurés mobilisés de 1939, avec
  `regimes/assurances_sociales.yaml` (`CR_MIN_26101939`, IV B : « Les droits des assurés
  mobilisés seront maintenus intégralement en ce qui concerne l'assurance vieillesse et
  invalidité », par une « cotisation fictive [...] égale au quart de la double
  contribution » de l'année d'avant ; le reste, le paiement et la gestion des caisses).
- *À d'autres fiches* (9) : `pension_d_invalidite_substituee` et
  `pension_maximale_regime_general` (`LE_MIN_14091951`) ; les retraites ouvrières et
  `pension_d_invalidite_substituee` (`LE_MIN_05051953`, la bonification d'invalidité
  « portée à 3.000 francs, avec effet du 1er juillet 1948 ») ; `inaptitude_au_travail`
  (`LE_MIN_07071959`, l'inaptitude constatée pour le régime complémentaire, comme
  `LE_MIN_02011991`, qui la cite) ;
  `majoration_conjoint_a_charge` et `reversion` (`LE_MIN_21091959`) ; `reversion`
  (`LE_MIN_20091968`, le gain de l'épouse qui reprend un emploi « par suite de la maladie
  » du mari, « par mesure de bienveillance » hors des ressources ; la saisie ne dit pas
  pourquoi le survivant travaille) ; `totalisation_des_periodes_etrangeres`
  (`LE_MIN_01091959`, les périodes inférieures aux équivalences du règlement n° 4,
  « purement et simplement négligées ») ; `retablissement_fonction_publique`,
  `liquidation_regime_par_regime` et `pension_d_invalidite_substituee`
  (`lettre_Fnoss_1958_22091958.pdf`, le rachat complémentaire au profit d'un régime
  spécial « en considérant l'âge de l'assuré au versement initial », comme la lettre Cnav
  du 27 août 2013 le rappelle).
- *Hors du modèle* (9), sous les raisons du registre : les héritiers (`CR_MIN_15061939`) ;
  l'assiette des dirigeants (`CR_MIN_16051956`) ; l'organisation (`LE_FNOSS_21071954`,
  à laquelle répond la lettre n° 22341, rangée là) ; l'assurance maladie
  (`LE_AUTRE_07081951` : « Couverture des seules prestations en nature ») ;
  l'assujettissement (`LE_MIN_01071949`) ; la procédure (`LE_MIN_18101954`, les rentes
  « présumées éteintes ») ; la caisse compétente (`LE_MIN_25101961`, la CRAV de
  Strasbourg, comme la lettre de 1981 qui la cite) ; le mode de paiement
  (`LE_AUTRE_27011960`) ; l'assurance volontaire des autres risques (`LE_FNOSS_01081963`,
  à laquelle répond la lettre n° 40374/AG, rangée là).
- *Trois sorts autres que ceux que les notes proposaient* : `LE_MIN_05061950`, à la
  limite et non à l'assujettissement, pour l'assurance volontaire qu'elle ouvre ;
  `CR_MIN_26101939`, à la limite et non à l'organisation, pour son IV B ;
  `LE_MIN_25101961`, à la caisse compétente et non au régime local, son seul objet.

**Les 27 de 1973, par ce qu'elles disent.** À `minimum_vieillesse` et
`residence_et_minimum_vieillesse`, le secours viager de la veuve qui réside en Algérie
(`CR_CN_28bis73_20041973`, `LE_CN_18041973`, `LE_MIN_22111973`,
`CR_CN_102bis73_24121973` : « les conjoints survivants résidant en Algérie peuvent
bénéficier du secours viager ») ; à `minimum_vieillesse`, l'allocation aux mères de
famille (`CR_CN_5473_2_06071973`, `LE_CN_06071973`) ; à `residence_et_minimum_vieillesse`,
l'allocation supplémentaire des Algériens rentrés « postérieur[ement], non plus au
4 juillet 1962, mais au 30 avril 1965 » (`LE_MIN_08081973`) ; à `reversion` et
`minimum_vieillesse`, la réversion du titulaire d'un secours viager (`CR_CN_6773_10081973`) ;
à `trimestres_avant_1972`, la validation de la première année (`CR_CN_2573_09041973`) ; à
`salaire_annuel_moyen` (`CR_CN_3473_04051973`) ; à `totalisation_des_periodes_etrangeres`,
les conventions avec le Portugal (`CR_MIN_25SS_21061973`) et la Turquie
(`CR_MIN_38SS_15101973`, avec `residence_et_minimum_vieillesse` pour l'AVTS) ; à
`retablissement_fonction_publique`, le fonctionnaire retraité sans pension de sa seconde
carrière, « quelle que soit la date à laquelle le nouvel emploi a cessé », après le
29 janvier 1950 (`LC_22111973`), et, avec `liquidation_regime_par_regime`, les régimes
d'équivalence de 1935 (`LE_MIN_31081973`, n° 462) ; à la limite seule, la détention
d'Afrique du Nord (`CR_CN_4073_04061973`) et les apprentis (`LC_7347_12121973`) ; à la
limite et à `caisse_francais_etranger`, les rachats des lois n° 61-1413 et 65-555
(`CR_CN_1373_08021973`, `CR_CN_5673_06071973`, `LE_CN_20121973`, `LE_MIN_11011973`) ; à la
limite et à `rachats_et_versements`, les religieux admis « au titre de la loi du
13 juillet 1962 » (`LE_MIN_01101973`). Hors du modèle : la répétition de l'indu
(`CR_CN_5973_11071973`), la tutelle (`CR_CN_9173_29101973`), le compte joint
(`LC_138_27031973`), les héritiers (`LE_MIN_05021973`), l'assurance volontaire maladie
(`LE_CNAM_11_19071973`), la caisse qui instruit un rachat (`LE_MIN_05111973`).

**Les montants relus, conformes.** Le maximum des pensions, « 129.600 francs (40 p. 100 de
324.000 francs) » au 1er janvier 1951, et 105 600 F en 1949 et 1950 (lettre du
14 septembre 1951) : le barème de la Cnav, relu par l'API ce jour, « 01/03/1949 105 600 AF
Loi du 24/02/1949 », « 01/01/1951 129 600 AF Loi du 30/12/1950 » ; les coefficients 1,15
« (arrêté du 19 avril 1950) » et 1,16 « (arrêté du 16 avril 1951) », ceux de
`legislation/revalorisation_pensions.csv` (1950-01-01, 1951-01-01) ; 105 600 × 1,15 =
121 440, × 1,16 = 140 870,4 (la lettre écrit « 121.400 » au second calcul). Le plafond,
« 132.000 francs par trimestre, soit 44.000 francs par mois » depuis le 1er octobre 1955
(circulaire n° 57 SS) : 12 × 44 000 = 528 000 AF = 5 280 F, / 6,55957 = 804,93 €, les
805 € de 1956 de `macro/plafond_securite_sociale.csv`.

**Les règles confrontées, conformes.** La validation de la première année (n° 25/73) :
« au moins égal à 30 anciens francs » de double cotisation de 1936 à 1941, 120, 90, 60 ou
30 pour quatre, trois, deux ou un trimestre de 1942 à 1945, soit deux fois la retenue de
15 anciens francs par trimestre que la fiche `trimestres_avant_1972` lit à l'article 71
du décret du 29 décembre 1945 ; de 1930 à 1935, soixante cotisations journalières par
trimestre, « dans la limite de 22 » ; après 1945, « dans la limite de 4 », le salaire sur
le minimum de l'année. Les ressources du conjoint, dont on exclut « le montant de
l'avantage de vieillesse dont le conjoint est bénéficiaire » (lettre du 21 septembre
1959) : la version `avant_1973` de `reversion` (« ses retraites exceptées ») ; la
majoration pour conjoint à charge, qui retranche ces avantages sans plafond. Les
ressources des survivants d'avant le 1er mars 1971 appréciées « à la date de la
demande », la demande « renouvelée » (n° 67/73) : l'écart que `reversion` déclare déjà.

**Un candidat pour la session du modèle**, sans y toucher : *le maximum de 1949, 1951 et
1955 dans l'année.* La fiche `pension_maximale_regime_general` déclare que, l'année où le
plafond change, « le maximum de la Cnav est celui du semestre, plus bas de 1 à 4 % au
premier, plus haut au second ». Le barème relu dit d'autres dates et d'autres écarts au
maximum du modèle, 40 % du plafond moyen de la série : 1949, 0,40 × 393 = 157,20 € ;
91 200 AF, 139,03 €, jusqu'au 28 février (−11,6 %), 105 600 AF, 160,99 €, ensuite
(+2,4 %) ; 1951, 0,40 × 526 = 210,40 € ; 129 600 AF, 197,57 €, jusqu'au 30 septembre
(−6,1 %), 163 200 AF, 248,80 €, ensuite (+18,2 %) ; 1955, 0,40 × 723 = 289,20 € ; 182 400 AF,
278,07 €, jusqu'au 30 septembre (−3,8 %), 211 200 AF, 321,97 €, ensuite (+11,3 %). La
moyenne de 1951 pondérée par les mois, (9 × 129 600 + 3 × 163 200) / 12 = 138 000 AF =
210,38 €, est le maximum du modèle : la règle annuelle tient, la phrase non. Une pension au
maximum prenant effet de janvier à septembre 1951 : 210,40 € au modèle, 197,57 € à la
caisse, 12,83 € par an de trop, +6,5 %. Ce n'est pas une règle neuve : la quantification
d'un écart déclaré, fausse pour 1949 et 1951, et ses dates, qui ne sont pas des semestres.

**Un écart déjà déclaré, précisé.** La lettre du 14 septembre 1951 ramène au maximum la
pension substituée revalorisée — « 140.870 francs et ramenée au chiffre-limite en vigueur
de 129.600 francs » —, et revalorise ensuite « sur le chiffre de 140.870 francs, montant
réel de la pension ». La fiche du maximum déclare que le modèle ne borne pas les
arrérages revalorisés : 140 870 AF, 214,75 €, servis en 1951 au lieu de 197,57 €, +8,7 % ;
la base des revalorisations suivantes, la pension réelle, est celle du modèle.

**Un point non tranché.** La circulaire n° 34/73 fait chercher, quand la période de
référence ne compte « aucun trimestre valable », « les 10 années civiles d'assurance
antérieures », d'avant 1948 au besoin (« seront retenues les années 1947 - 1946 [...] -
1936 », « les 4/5èmes du total des salaires revalorisés ») ; le décret n° 72-1229 que
cite la fiche `salaire_annuel_moyen` retient les années « postérieurement au 31 décembre
1947 ». Quand les années retenues ne portent aucun trimestre, le moteur divise leur
somme par leur nombre (`moyenne_selon_la_regle`,
`src/retraite_notionnelle/droit/liquider.py:3132`). Le cas de la circulaire n'a pas été
posé sur les moteurs ; il touche les assurés que le minimum sert le plus souvent, comme
elle le dit (« liquider ses droits sur la base du minimum »).

**Ce que la base sert de travers.**

- Quatre des 31 de G8 portent en en-tête un numéro, que la note les disait sans :
  `LE_MIN_25081954` (21984), `CR_MIN_16051956` (57 SS), `LE_AUTRE_10071951` (4004 SC/DA. 1,
  que la lettre n° 4798 du 7 août 1951 cite : « ma lettre n° 4004 SC/DA. 1 du 10 juillet
  1951 »), `LE_AUTRE_07081951` (4798 SC/DA. 1) ; de même, chez G9, `LC_13061962`
  (36/062).
- `CR_MIN_15061939`, datée du 15 juin 1939 par la base et par son texte : la circulaire
  n° 30 du 5 juillet 1939, qui la joint, dit « en date du 13 juin 1939 ». Le texte ne
  tranche pas.
- `LE_MIN_25101961` écrit « antérieurement au 1er juillet 1916 » sous un objet qui dit
  1946 ; `LE_MIN_14091951`, « 121.400 » pour 121 440.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune valeur du modèle
n'a changé. Les lois et décrets que ces textes appliquent n'ont pas été relus au Journal
officiel ; les montants l'ont été au barème de la Cnav et aux séries. Les moteurs n'ont
tourné sur aucun cas. Les conventions avec le Portugal et la Turquie ne sont lues qu'en
leur partie vieillesse.
