# Relecture de J5 et des chiffres neufs de J4-bis : le solde du suivi du panorama de la DREES, l'âge du graphique 7 et le test de la garantie

**Verdict : aucun écart fort ; aucun chiffre tiré de la source n'est faux, chez J5
comme chez J4-bis (une seule recopie fautive, dans la prose de J5).** Les 4 209 cellules du témoin de J5 sont
celles des classeurs, ses 13 phrases sont au folio qu'il nomme, ses 63 âges
conjoncturels se refont, ses 29 tests passent aux deux jeux de présomptions, et
les chiffres neufs de J4-bis (arrondis, CNRACL, minima, garantie) se refont à la
main ou au modèle, y compris l'isolement du jour de naissance présumé. **Trois
écarts moyens, tous de déclaration** : l'explication du 13,2 contre 14,1 de la
fiche 1 est à la source (annexe 3, folio 299) et J5 ne l'a pas lue (point 2) ;
trois des quatre feuilles « REVISIONS » de la fiche 21 comparent deux générations,
ce que la feuille « Synthese » dit et que ni la note ni le suivi ne rapportent
(point 3) ; « aucune erreur du dépôt » (message du commit) et « Aucune erreur du
modèle » (suivi, fiche 15) disent plus que les preuves (point 5). **Treize faibles**
(point 9), dont la recopie fautive (« 61,63 », point 9, n° 4).

**La demande.** Vague 11, tâche R-J5, le 6 novembre 2026 : revérifier contre les
sources, sans me fier à J5 (`session_01FVFLAkubMcXgSKWuXBDaqK`, commit `cef7bfa`),
à J4-bis (`session_01FVFLAnDxvdSxz2ipG5WbqM`, commit `9429683`) ni à ma mémoire,
leurs règles, chiffres et dates. Je ne modifie ni règle, ni donnée, ni test, ni
note ; je n'écris aucun bloc « Reprise ». Le bloc de l'étape 5-bis est périmé
(fiche 21, fiche 12 et jeu `drees_minimum_vieillesse`, que l'étape 7 a traités ou
nommés) : la tâche J suivante le récrira.

**Les sources, ouvertes pour cette relecture.** `python
scripts/fetch/source_locale.py --recuperer` a rapporté le PDF (SHA-256
`9eb36a06639af0f4298d281b41acbde4236e47fc73e40c673f153ad86735e9be`, le miroir de
l'UNSA) et l'archive des 36 classeurs
(`ec7503f813b0a7e38b76c6aade302afa482f927e7d83386922be0522aaf64911`) : les deux
empreintes sont celles des notes de J5 et de J4-bis, que `sha256sum` retrouve. Le
PDF par `pdftotext`, page à page, le folio imprimé étant la page du fichier moins
un (vérifié au pied de la page 300 : « Drees 299 »). Les classeurs par `openpyxl`
(`data_only`), indépendamment de `lecture_xlsx`, le lecteur de J5. Le modèle : des
scripts à moi, hors dépôt, qui appellent les mêmes fonctions que les tests de J4-bis
(`controle_eacr.controle`, `memoire.cout(...).poids`, `memoire.avantages`,
`mesures_prose._avenir`) ; ils sont indépendants de l'arithmétique et des cellules
de J5, non de la grille.

## 1. Ce qui est conforme, sans réserve

- **Le témoin** (`drees_panorama_2026_solde.json`) : j'ai relu avec `openpyxl` ses
  4 209 cellules (1 098 cellules isolées, 25 blocs), non un échantillon : 0 écart,
  au bit près. La consigne était un échantillon d'au moins trente cellules et toutes
  celles qui fondent une conclusion ; la relecture entière les couvre.
- **Ses citations** : les 10 blocs (13 phrases) sont dans le PDF à la page que
  le témoin nomme, lus comme le test les lit (`pdftotext` sans `-layout`, césures
  retirées). En `-layout`, deux phrases sont coupées par les colonnes : c'est la
  lecture du test qui fait foi. Cinq phrases se retrouvent aussi sur d'autres folios
  (la source du tableau 1 de la fiche 10 aux folios 100 à 103, la note du tableau 2 de
  la fiche 1 aux folios 9, 23 et 25, par exemple) : elles sont toutes au folio que le
  témoin nomme.
- **Les 29 tests** (section 10) : leurs valeurs viennent des cellules, non du
  code. Plusieurs attentes sont des écarts de la source, épinglés (J5 le dit).
- **La fiche 10** refaite à la main : 426,7 / 395,3 / 359,7 / 41,7 ; 401 426,39 =
  359 717,10 + 41 709,29 ; 395,3 ÷ 426,7 = 0,9264 ; 2022-2023 5,048 %, 2023-2024
  6,714 % (publié 6,7), 1990-2024 3,949 % par an (publié 3,9) ; 395 338,73 ÷
  2 935 236 = 13,469 %, 370 465,23 ÷ 2 833 826 = 13,073 % ; la comparaison
  européenne 14,612 % avec le PIB du panorama, 14,536 % avec celui du dépôt. Le
  PIB de 1990 à 2022 est identique au million à `pib_courant.csv` (33 années) ;
  2023 : 2 826,542 ÷ 2 833,826 = 0,99743 ; 2024 : 2 919,9 ÷ 2 935,236 = 0,99478.
  La cellule D7 de « F10_Tableau 2 » est du texte (« 5,0 », type `s`).
- **Les fiches 28, 16, 3, 21 et 12**, par les calculs de la note : 77,04 % (E15) =
  50,64 + 26,41 à l'arrondi près (50,636 + 26,406 = 77,042 au dépôt) ; 753 900 ÷ 17 291 318 = 4,36 %, ÷ 17 579 342 = 4,29 % (publié
  4,32) ; 412 125 ÷ 848 498 = 48,57 % (+0,45 point sur 48,12) ; 886,13 × 95,3 % ÷
  4 407 = 19,2 % ; 4 406,64 − 4 368,15 = 38,49 ; 87,63 % ; 27,97 + 46,51 + 24,23
  + 14,69 − 13,40 = 100,00 (C5, C9, C10, C11 de « F21_Tableau encadré 2 ») ;
  génération 1946, 37,4 / 44,0 / 40,7 à la feuille publiée et au dépôt, 37,6 /
  44,1 / 41,0 à « Graphique 1 (2) », dont l'en-tête dit « avant ou en 2017 » (la
  feuille publiée, « 2021 ») : les copies de travail sont bien l'édition d'avant.
- **La fiche 17** : régime général, décote 52 / 40 / 8 pour une moyenne de 10,3,
  bornes 6,04 et 13,48 ; surcote 12 / 29 / 29 / 30, borne basse 5,15 pour 7,7 ; le
  dépôt (`retraites_generations.csv`) porte 13,1 / 16,1, 5,1 (MSA salariés), 15,8
  / 28,2 (FPE civils), 8,1 / 17,3 (CNRACL), 6,6 (MSA non-salariés) pour la
  génération 1957, ce que « F17_Graphique 4 » (C24, D24, E24, F24, G24) et
  « F17_Graphique 5 » (C22, D22, E22) donnent cellule pour cellule : les écarts au
  « F17_Graphique 2 » sont bien ceux du champ.
- **Les sept régimes pesés** de J4-bis, la CNRACL à 12,40 %, ses deux cas types
  (0,02937 et 0,09461), la seule femme de la grille à 81 714,64 têtes sur 750 357,0
  (10,89 %), les cellules N10, N20 et N30 de « F16_Tableau 2 compl » (9,3 ; 5,3 ;
  7,4) : section 8.

## 2. (a) Le régime général de 2014 à 2024, fiche 1 : l'explication est à la source

J5 : « le cadrage donne +14,1 %, la source +13,2 % : 0,9 point, la note 2 renvoie à
l'annexe 3 sur l'intégration de la SSI », **point non tranché**. Il a cité le renvoi,
non l'annexe. Je l'ai lue : annexe 3, « Création de la SSI et fusion avec le régime
général » (folio 299, page 300 du fichier) :

> « Depuis le 1er janvier 2018, les régimes de base RSI commerçants et RSI artisans
> ont fusionné au sein du régime de la Sécurité sociale des indépendants (SSI). Ce
> régime a lui-même disparu fin 2019, suite à son intégration au régime général de
> la Sécurité sociale. [...] À partir de 2020, seul le régime général total existe.
> Par ailleurs, les effectifs du régime général après intégration des indépendants
> de l'ex-SSI sont estimés dans le passé à partir du modèle ANCETRE : un individu
> polypensionné du régime général et de la SSI ne compte qu'une fois dans le régime
> général. »

Le tableau 2 de la fiche 1 (folio 23, note 2 ; « F01_Tableau 2 compl », même renvoi)
envoie à cette annexe ; la note 2 du tableau 1 (folio 21) dit : « Une rupture de
série a lieu en 2020 du fait de la révision à la baisse des effectifs de retraités
résidant à l'étranger [...] et de l'intégration de la Sécurité sociale des
indépendants (SSI) au régime général » ; la note 5 du folio 24 : « À compter du 1er
janvier 2020, les effectifs du régime général incluent les indépendants de l'ex-Sécurité
sociale des indépendants (SSI). »

**Ce qui en découle, chiffré.** Le cadrage (`effectifs_retraites.csv`, en-tête) dit
lui-même que la Cnav « porte le code 0010 jusqu'en 2019 puis 0015, sur un champ
légèrement plus large » : 12 922 464 en 2014 est le régime général d'avant
l'intégration. La DREES, elle, rapporte 2024 à un régime général *reconstitué*
pour 2014, où les ex-indépendants comptent une fois : 14 744 736 ÷ 1,132 donne une
base de 13 019 à 13 031 mille (13,15 à 13,25 % publiés), soit 97 à 109 mille de plus
que le cadrage. Les autres colonnes concordent à 0,05 point : 2020-2024 est 14 744
736 ÷ 14 052 675 = +4,925 % (publié 4,9) sur la même base 2020, post-intégration. **La
source donne donc le mécanisme (une série reconstituée par ANCETRE) ; elle ne donne
pas la base de 2014**, et l'ordre de grandeur de l'écart (+0,8 % de la base) est
compatible, non démontré. Ce qu'il faut écrire : « écart de périmètre, 2014 reconstitué
par la DREES, annexe 3 folio 299 », non « point non tranché ». Le dépôt n'a pas
d'erreur ici : l'en-tête du cadrage dit qu'il sert à pondérer les cas types, non à
mesurer une évolution à travers 2020 (je n'ai pas cherché d'autre usage dans le code).
**Écart moyen**, de déclaration.

## 3. (b) Les quatre feuilles « REVISIONS » de la fiche 21 autres que le graphique 1

J5 les a « lues par leurs en-têtes seuls » et le dit. Je les ai vérifiées
cellule par cellule contre les feuilles de 2026 : la valeur de 2025 plus la
révision est celle de 2026 pour **43 cellules du tableau 1, 48 du tableau 3 et 432 du
graphique 2** (trois blocs de 18 âges et 8 colonnes), et pour les quatre lignes
comparables du tableau 2 (10, 13, 14, 16 : 0,98 + 0,74 = 1,72 ; 6,99 + 1,87 =
8,86 ; 2,77 + 1,48 = 4,25) : 0 écart. Restent hors identité deux cellules « <1 »
(texte) du tableau 1, un `#VALUE!` (N20), trois `#REF!` (H8:J8 du tableau 2).

**Ce que J5 n'a pas vu, et que ses en-têtes disaient.** Le bloc de 2025 des
tableaux 2 et 3 et du graphique 2 est celui de la **génération 1950** (B2 : « pour la
génération née en 1950 », « génération 1950 » ; source « EIC 2017 » aux tableaux 2
et 3), les feuilles de 2026 sont celles de la **génération 1954** (« née en 1954 » ;
« EIC 2021 », que le PDF confirme pour le tableau 2, folio 186). L'identité 2025 + révision = 2026
est donc exacte *entre deux générations* : ces « révisions » ne sont pas des
révisions d'une même donnée. La feuille « Synthese » de la DREES le dit en toutes
lettres (colonnes D, E, F, ligne 3) : « 1954 dans Pano 2026, vs 1950 auparavant »
pour le tableau 2, le graphique 2 et le tableau 3, et (ligne 4) pour l'origine des
écarts : au tableau 3, « Quasi exclusivement du fait du changement de génération » ; au
graphique 2, « [...] du changement de génération et des règles de liquidation
différentes (recul progressif de l'AOD entre générations 1950 et 1955) » ; au tableau
2, « Principalement changement méthodologique [...] Dans une moindre mesure, impact du
changement de sources (EIC 2021) et de génération ». Le tableau 1 (générations 1942,
1946 et 1950 communes) et le graphique 1 sont, eux, de vraies révisions : la
génération 1942, de l'EIC 2013 dans les deux éditions, a une révision de 0 à chaque
cellule.

**Conséquence.** Le suivi (fiche 21, `solde`) écrit « les quatre autres feuilles de
révisions [...] ne sont lues que par leurs en-têtes et la note de Synthese » et ne
rapporte pas cette différence : qui citerait « la DREES a révisé de 3,9 points la part
des femmes à deux transitions (hors cumul emploi-retraite) » citerait un écart
entre la génération 1950 de 2025 et la génération 1954 de 2026. Le test
`test_les_revisions_du_graphique_1_...` ne couvre que le graphique 1, comme il
se doit. **Écart moyen** (une phrase à ajouter au suivi), et trois faits de source
de plus à lister : `#VALUE!` (« F21_Tableau 1 REVISIONS », N20), `#REF!` (« Tableau
2 REVISIONS », H8:J8), et la colonne « Total » du bloc des révisions du tableau 1 qui
écrit 100 là où une révision vaut 0 (R7:R15). La Synthese minore elle-même deux
maxima : « jusqu'à 2,8 point » (tableau 1) pour 2,91 (M11, hommes de 1946) et
« jusqu'à 3 points » (tableau 3) pour 3,93 (N9).

## 4. (c) Les neuf défauts de la source, un par un

| n° | J5 | verdict | preuve |
|---|---|---|---|
| 1 | D7 de « F10_Tableau 2 » est du texte | **conforme** | type `s`, `'5,0'`, format `@` ; E7 et C7 sont des nombres |
| 2 | PIB 2023 et 2024 ≠ `pib_courant.csv` | **réel, mais ce n'est pas un défaut** | 1990-2022 identiques ; 2023 et 2024 plus bas de 0,26 et 0,52 %. La feuille marque « 2024(p) » et la source « semi-définitives pour 2023 et provisoires pour 2024 » : un autre millésime de l'INSEE, non dit (le dépôt lit la série de la BDM, base 2020). Faible |
| 3 | trois zéros, le régime général | **zéros conformes ; régime général : point 2** | I23, I24, I25 = 0 ; le cadrage n'a ni 2014 ni 2015 pour la Banque de France (série depuis 2016 : 13 521), la CANSSM (depuis 2019 : 120 139) ni l'Enim (depuis 2020) |
| 4 | CNRACL, Ircantec en fractions | **conforme, et plus fort** | G12:I13 = 0,016 ; 0,093 ; 0,23 et −0,01 ; −0,068 ; −0,155, format `0.0` ; **le PDF imprime « 0,0 0,1 0,2 » et « 0,0 −0,1 −0,2 »** (folio 37, tableau 2), quand le complément écrit 1,6 ; 9,3 ; 23 et −1 ; −6,8 ; −15,5 |
| 5 | bloc « Ensemble » de 2023 | **conforme** | 16 âges sur 21, de 0,01 à 0,32 ; les trois autres feuilles qui donnent 55,6 à 62 ans sont « F15_Graphique 3 », « F15_Graphique 4 » et « F16_Graphique 1 » : c'est le complément, seul, qui s'écarte |
| 6 | nouveaux retraités de 2023, deux millésimes | **conforme** | 19 âges sur 21, 30,53 contre 29,93 à 62 ans ; 2024 : 0 écart. « Deux millésimes » est une lecture, que J5 déclare non tranchée |
| 7 | graphique 2 de la fiche 17, « secteur privé » | **conforme** | le Champ dit « au moins un droit direct dans un régime de base du secteur privé » avec les colonnes FPE civils et CNRACL ; graphiques 4 et 5 : « un droit direct dans le régime, [...] l'année de leurs 67 ans » |
| 8 | fiche 23, intégration de la SSI en 2020 ou 2021 | **conforme ; la source tranche** | Tableau 1 et Graphique 1 : « depuis 2020 » ; Graphique 1 compl. : « en 2021 ». L'annexe 3 (folio 299) tranche : fin 2019, « à partir de 2020 ». Faible |
| 9 | fiche 12, « A DECIDER » aux figures 2 et 5 | **conforme, mais ce n'est pas un défaut** | C7 et F7 de « Synthese » ; une note de travail restée dans le classeur, qui n'engage pas l'édition. Faible |

**Aucun n'est une lecture fautive**, et aucun n'est déclaré erreur sans que la lecture
contraire soit intenable (J5 s'en tient à « non tranché » ou « à ne pas citer »).
Sur les zéros : l'argument de J5 (la CANSSM aurait dû croître de 30,7 % de 2014 à
2020, quand elle en perd 23,5 de 2020 à 2024) ne vaut que pour la CANSSM. Pour la
Banque de France, le cadrage commence en 2016 (13 521) et finit à 14 769 : un vrai
zéro supposerait 14 769 en 2014, donc une baisse de 8,5 % jusqu'en 2016 puis une
hausse de 9,2 % : peu plausible, non exclu. Pour l'Enim (65 575 en 2020, 62 598 en
2024), rien dans le cadrage ne contredit un zéro. Le « à ne pas citer » tient aux
trois ; sa preuve est plus faible que sa conclusion pour deux. Faible.

## 5. (d) « Aucune erreur du dépôt »

La note est prudente : « aucune de ces lectures contraires n'est intenable : aucune
n'est déclarée erreur du dépôt ni de la DREES ». Le message du commit (« aucune erreur
du dépôt ») et le suivi (fiche 15, « Aucune erreur du modèle ») disent plus. Pour ce
qui a un vis-à-vis, j'ai repris chaque écart du dépôt à la source :

- **concordants, ou expliqués par la source, refaits par moi** : l'encadré 1 et les
  sous-postes de `pensions_droits.csv` ; la fiche 12 (génération 1946) ; la
  génération 1957 de la fiche 17 ; l'âge conjoncturel de 2022 à 2024 (0 écart aux neuf
  valeurs) ; le PIB de 1990 à 2022 ; le régime général du tableau 2 complémentaire de
  la fiche 1, par l'annexe 3 ; **vus verts aux tests de J5, non refaits** : la pyramide
  de la fiche 1 (0,049 au plus), les effectifs de 2024 et les évolutions de 2023-2024 et
  de 2020-2024 des 19 lignes du tableau 2 complémentaire (et 2014-2024 de 14 d'entre
  elles), les allocataires de la fiche 28 par âge, sexe et situation ;
- **écart déclaré, non expliqué, que rien ne permet d'appeler erreur ni de
  disculper** : (1) le taux de retraités de la table C rapportée à la projection du
  dépôt, **+0,45 point à 62 ans, +2,13 à 67 ans**, croissant avec l'âge (J5 : « la
  source compte les personnes résidant en France, la table C tous les retraités,
  dont 5 % à l'étranger (folio 38) » : le folio 38 donne bien 95 / 5 pour les
  bénéficiaires d'un droit direct, mais c'est une moyenne tous âges ; la part des
  résidents à l'étranger à 62 ou 67 ans n'est pas dans la source, de sorte que
  l'explication est plausible (l'écart croît avec l'âge), non démontrée, et J5 la
  dit « déclarée, non expliquée ») ; (2) `age_conjoncturel_depart.csv` (série du
  portail) contre le panorama de 2004 à 2021 : **20 valeurs sur 63** diffèrent de
  plus de 0,005 an, jusqu'à 0,10 (2013, femmes) ; la source ne dit pas laquelle est
  révisée ; (3) six comparaisons sur seize d'un point entre la fiche 16 (graphique 5
  compl.) et le tableau 1 du dépôt (arrondi ou millésime).

Aucun de ces trois n'est établi comme erreur du dépôt ; aucun n'est établi comme son
absence. **La formule juste : « aucune erreur établie, trois écarts non expliqués »**,
et le « Aucune erreur du modèle » de la fiche 15 se contredit lui-même, deux phrases
après « champs différents, écart non expliqué ». **Écart moyen** : les mots d'un
fichier durable, sans chiffre faux.

## 6. (e) L'âge conjoncturel de la fiche 15, refait

50 + Σ de 50 à 70 ans de (1 − taux ÷ 100), les taux de « F15_Graphique 3 » (ensemble,
lignes 5 à 25) et de « F15_Graphique 3 compl » (femmes, lignes 7 à 27 ; hommes, 32 à
52) : **63 valeurs sur 63** à moins de 0,005 an de « F15_Graphique 1 » (lignes 5 à 7),
le plus éloigné à 0,0049 (hommes, 2011 : 60,4651 pour 60,47). 2024 : 62,9515 (publié
62,95) ; 2023 : 62,7541 avec le graphique 3, 62,7333 avec le bloc « Ensemble » du
complément (publié 62,75). Conforme.

## 7. (f) Les six candidats de la section 5, et ce que J5 a laissé

Chacun vérifié contre les jeux de `data/reference/macro` et `regimes` (ce que le dépôt
porte déjà, ce qu'il n'a pas) ; que « aucun calcul » du code lise ces chiffres, je ne
l'ai pas contrôlé par une recherche exhaustive du code.

1. **Le sexe du taux de liquidation** (fiche 17) : `retraites_generations.csv` n'a le
   sexe que pour la génération 1953 (9 modalités) ; le complément en a 12. Aux 107
   cellules comparables, l'ensemble du dépôt est compris entre les deux sexes, bornes
   comprises, sans la marge de 0,1 point que J5 se donne ; **une cellule est vide**
   (hommes 1942, « autre motif », J27) et le test la saute sans le dire (`vus >= 100`).
2. **Le cumul par sexe de 2022** (fiche 23) : `cumul_emploi_retraite_profil.csv` a le
   sexe pour les champs `csp`, `generation_1950`, `meme_regime` et `temps_travail`, pas
   pour `age` : exact.
3. **Les flux de nouveaux retraités** (fiches 1 et 3) : aucun jeu du dépôt ne porte les
   flux de tous les régimes ; il a celui de la Cnav seule (`nouveaux_retraites_cnav.csv`,
   salariés et salariés-indépendants, depuis 2003), qui n'est pas le même champ, et la
   masse du droit dérivé (`droits_derives.csv`), non ses entrants.
4. **Les trimestres moyens de décote et de surcote** : aucun jeu, et les bornes (6,04 /
   13,48 ; 5,15) sont refaites.
5. **Les tableaux 3 et 4 de la fiche 28** : ils datent de **fin 2020** (EIR 2020), non de
   2024 ; la note ne le dit pas, le suivi ne le dit que du tableau 4. À écrire avant
   de les « confronter à la garantie de la proposition ».
6. **Les pensions du champ PRRO de 1990 à 2024** (fiche 10) : `pensions_droits.csv` est
   le champ CPS complet et ne commence qu'en 2020 (359 717,10 pour 2024, contre 354
   243,97 au champ PRRO) ; `depenses_retraite.csv` est le total CPS depuis 1959 :
   exact.

**À ajouter** : les trois feuilles « REVISIONS » entre deux générations (point 3), qui
ne se portent pas. Le candidat nommé de J4-bis (folio 142, « 61 ans et 7 mois » pour
la génération 1957) est **vrai** : le PDF (folio 142) l'écrit avec « soit 1 an et 1
mois de plus que pour la génération 1950 », quand « F15_Graphique 5 » donne 60,46
(E29) et 61,85 (E36), le graphique 6 61,88 (T13), la Lecture du graphique 5 61,9 : 61
ans et 10 mois, 1 an et 5 mois de plus. 61,58 est la valeur de 1955 (61,59). Une
coquille du texte ou une autre édition : la source ne dit pas laquelle.

## 8. J4-bis : les chiffres neufs

- **Le graphique 7, la clause.** La cellule B38 de « F15_Graphique 7 » porte mot pour
  mot la note citée (« dans le champ des personnes vivantes à 66 ans parmi les
  générations nées en 1950 ou avant, et à 67 ans pour les générations nées en 1951 ou
  après »), sans renvoi à aucun graphique ; celle de « F15_Graphique 5 » (B38) définit
  l'âge « atteint à la liquidation [...] dans le régime pour lequel la durée validée est
  la plus élevée », sans cette clause. Le PDF les a aux folios 144 et 142 (note 5 :
  « scénario central de mortalité des projections démographiques de l'Insee au 1er
  janvier 2026 »), les sources du folio 144 disent « au 1er janvier 2026 », la note
  du graphique « de 2021 » : 2026 deux fois, 2021 une. **Conforme** ; l'âge du
  graphique 7 est bien une hypothèse du test. Les graphiques 5 et 6 : 13 des 15
  générations communes identiques au centième, 1956 à 0,01 (61,66 et 61,67), 1957 à
  0,03 (61,85 et 61,88) : exact. *Un fait de source de plus :* le Champ du
  graphique 5 dit « à 67 ans (pour les générations nées après 1954) », quand celui du
  graphique 7 dit « en 1954 ou après » : la génération 1954 n'est dans aucun membre au
  graphique 5, et J4-bis range les deux sous « 1953/1954 ». Faible.
- **Les arrondis**, refaits sur `Cohorte.nouvelle` (16 cohortes) : 688 584,801 ;
  23 804,644 ; 243 459,058 (92 457,619 + 24 939,340 + 37 174,035 + 12 841,397 +
  37 318,704 + 38 727,963) ; 177 235,129 ; 35,356 % à 62 ans ; 17,435 % au régime
  général à 60 ans (96 351,159 ÷ 552 624,878). Les neuf parts de la ligne « tous
  régimes » et celles du régime général sont celles de la note. **Conforme.**
- **La CNRACL** (inférence) : les sept parts de poids (65,58 ; 11,39 ; 12,40 ; 1,48 ;
  2,55 ; 4,38 ; 2,21 %) et les têtes de 1953 (750 357,0 dont 81 714,64 pour la seule
  femme, 10,89 %) sont refaits ; N10, N20, N30 = 9,3 ; 5,3 ; 7,4 ; (7,4 − 5,3) ÷ (9,3 −
  5,3) = 0,525. Le mécanisme (« la part de la grille est celle des poids ») est établi
  par construction ; l'inférence (que les poids soient la cause) est bien dite
  inférence. **Conforme.**
- **Le test de la garantie.** Refait aux deux jeux, par la garde même
  (`conftest._decaler_les_presomptions`, `PRESOMPTIONS_DECALEES=1`, le portage
  décalant ses propres présomptions par `pont.mjs`) : au vocabulaire (jour 15), les
  cinq lignes valent 4 941,15 ; 1 563,2415 ; 6,6596 ; 349,0065 ; 636,7330, **somme
  7 496,7906**, garantie 13 929,6777, différence 6 432,8871, facteur 0,73648, 2 800 133
  bénéficiaires ; sous la garde, 4 941,15 ; 1 568,6446 ; 6,6826 ; 396,0106 ;
  677,6846, **somme 7 590,1724**, garantie 13 912,4329, différence 6 322,2605,
  facteur 0,73714, 2 796 860. **L'isolement du jour de naissance est reproduit** : dans un arbre de
  travail jetable, `pont.mjs` rendu paramétrable (jamais dans mon arbre), le jour au 1er
  seul donne 7 590,17 aux quatre lignes qui bougent ; les enfants à 27 seuls et le
  mariage à 30 seul, 7 496,79 : J4-bis dit vrai. Le test est rendu *robuste* aux
  deux jeux, non indépendant du jour (il lit le jour au vocabulaire et écrit une
  mesure par jeu) ; son dictionnaire `{15: ..., 1: ...}` lèvera une `KeyError` si le
  vocabulaire présume un troisième jour. Faible. Aucune source ne publie ces
  trois lignes : la fourchette est une mesure, non un texte, comme J4-bis le dit.

## 9. Les faibles

1. **Les lignes 2 et 9 du tableau du point 4 ne sont pas des défauts** (PIB : autre
   millésime ; « A DECIDER » : note de travail) : le titre de la section 3 de J5, « Les
   défauts de la source », est plus large que sa liste.
2. **CNRACL et Ircantec** : le défaut est imprimé (folio 37, « 0,0 0,1 0,2 »), non
   seulement dans le classeur.
3. **Fiche 23** : l'annexe 3 tranche pour 2020.
4. **Un chiffre faux dans la note** : « (2013, femmes : 61,63 − 0,10) » (§ 2, fiche
   15). Le dépôt porte 61,54, le panorama 61,44 (écart −0,10, que le test pose) ;
   61,63 est le chiffre du panorama pour 2014 (M5).
5. **« 4 406,64 = 3 836,17 + 570,46 »** : la somme fait 4 406,63 (un arrondi de la
   source, 0,01).
6. **Fiche 17, complément** : une cellule vide non dite (point 7.1).
7. **« six classes sur neuf »** (fiche 16, graphique 5 compl.) : le test compare huit
   classes regroupées pour deux sexes, six écarts sur seize.
8. **Fiche 28, tableaux 3 et 4 : « fin 2020 »** non dit (point 7.5).
9. **Fiche 21** : `#VALUE!`, `#REF!`, le « Total » à 100 et la Synthese qui minore
   (point 3) ne sont pas dans la liste des défauts.
10. **Les zéros** : la preuve ne vaut que pour la CANSSM (point 4).
11. **Le « rouge » du test d'abord** : les 29 tests ont été vus rouges parce que le
    témoin n'existait pas, non pour la raison attendue (une valeur) ; la règle
    « vu échouer pour la raison attendue » est tenue à la lettre, pas dans l'esprit.
    Sans effet sur un chiffre.
12. **Graphique 5, « après 1954 »** (point 8) : un trou de la source, non relevé.
13. **J4-bis, la docstring du test de la garantie** écrit que le jour de naissance
    « déplace trois des quatre minima » ; la mesure de sa propre note (section 3) montre
    quatre lignes sur cinq qui bougent (contributif, garanti, pension majorée, complément
    RCO), le seul minimum vieillesse, lu aux comptes, restant fixe.

## 10. Les tests

- Les six fichiers de tests DREES (`test_controle_drees_panorama`, `test_drees_panorama`,
  `_2024`, `_eic`, `_series`, `_solde`) : **150 passés en 41,9 s au vocabulaire, 150
  passés en 118,7 s sous `PRESOMPTIONS_DECALEES=1`**, aucun sauté. Le fichier du test de
  la garantie de J-bis (`test_controle_drees_panorama.py`) en fait partie.
- `python -m pytest -m rapide -n 2` : **4 493 passés, 51 sautés, 11 rouges en 187 s** au
  vocabulaire ; sous `PRESOMPTIONS_DECALEES=1` : **4 288 passés, 256 sautés, les mêmes 11
  rouges, en 105 s**. Les 11 sont tous dans `tests/test_pages_en_dossier.py`
  (`test_une_page_toute_faite_est_a_jour` pour les dix pages et le plan du site,
  `test_le_corps_d_une_page_toute_faite_est_son_rendu[methode/index.html]`) : les
  pages que GitHub refait, non un vrai rouge (le brief les annonce) ; aucun autre test ne
  rougit. Lancés sur l'arbre de `cef7bfa`, sans autre ajout que cette note.

## 11. Ce que je n'ai pas fait

- Le jeu `drees_minimum_vieillesse` du portail : non ouvert (« Connection reset by
  peer » à J4 et à R-J4 ; J5 n'a obtenu que la page) ; je n'ai pas réessayé, et les
  70 660 restent lus au PDF.
- Le classeur A-Cadrage de l'EACR : le cadrage est lu au dépôt (`effectifs_retraites.csv`,
  `certifiee`), non au classeur, que je n'ai pas ouvert.
- La publication de l'INSEE de 2021 (note du graphique 7) : non lue.
- La grille n'est pas recalculée de zéro : j'ai pris `controle_eacr.controle()` et
  `memoire.cout(...)` comme J4-bis.
- Ni règle, ni donnée, ni test, ni note modifiés. Disque : le PDF, l'archive et les
  documents du manifeste dans `data/brut/` (hors dépôt), les classeurs extraits dans le
  brouillon : effacés en finissant.
