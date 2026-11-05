# Retouches de la relecture R-E2 : la CARCDSF, la pension du 1er janvier 2024 et l'inapte libéral (Retouches 3)

Le 5 novembre 2026, action 130. La relecture R-E2 (`2026-11-05-relecture-de-e-carcdsf.md`) du travail de
la file E (ca77a60 et 564a5b7, `2026-11-05-carte-des-fiches-carcdsf-lue-au-droit.md`) a trouvé deux
écarts moyens et cinq faibles. Cette note les reprend un à un ; ni règle, ni donnée, ni valeur du
modèle ne change. Textes rouverts dans les index du dépôt (`dila_index.py jorf --recuperer` : JORF à
jour du 3 novembre 2026 ; `legi --recuperer` : LEGI du 2 novembre), par `dila_cherche.py`. Valeurs du
modèle rejouées dans le moteur Python, par `Simulateur.scenario_actuel.calculer` (carrière dès 25
ans, naissance au 1er du mois, date d'effet au jour de l'âge, comme R-E2) ; le portage n'a pas été
rejoué ici, R-E2 l'a fait, et je reprends ses chiffres pour lui. Fiches touchées :
`carcdsf_minoration_age_seul` (B1, B3) et `liquidation_regime_par_regime` (B2).

## B1. La pension du 1er janvier 2024 : une septième erreur du modèle

**Ce que R-E2 dit** : E range la pension du 1er janvier 2024 parmi ce que le texte ne tranche pas ;
par les bornes mêmes de la fiche, c'est une erreur de 12 à 13,5 points.

**Ce que j'ai refait.** Les statuts de 2017 restent en vigueur jusqu'au 9 janvier 2024 (arrêté du
27 décembre 2023, publié le 9 janvier, en vigueur le 10 : bornes de la fiche, relues par R-E2 ; aucune
annexe ne porte de date d'application). Né le 1er septembre 1961, effet le 1er janvier 2024, 62 ans et
4 mois : 67 ans moins 62 ans et 4 mois, 56 mois, 18 trimestres entiers à 1,50 % (statuts de 2017,
sans limite) : 27 %, coefficient 0,73 ; 19 si le trimestre entamé compte : 28,5 %, 0,715. Le modèle,
rejoué : 0,85, la règle de 2024 (1,25 % par trimestre, 15 % au plus) : 12 à 13,5 points de trop. La
fiche l'avait déjà dit en approximation, mais le bloc « Reprise », la note de E et le compte rendu le
rangeaient hors de la liste des erreurs à poser au propriétaire.

**Fait** : l'approximation de la version `statuts_de_2017` de `carcdsf_minoration_age_seul` s'ouvre
sur « Septième erreur du modèle », dit que le texte tranche et que restent ouverts le compte du
trimestre entamé et ce que la caisse a servi (non lu), et donne l'écart, 12 à 13,5 points ; son
`a_relire` ne range plus la pension du 1er janvier 2024 parmi ce que le texte ne tranche pas ; l'effet
d'ensemble de la fiche ajoute « ni ceux de 2017 du 1er au 9 janvier 2024 ». Sous
`PRESOMPTIONS_DECALEES=1`, selon R-E2, l'effet passe au 1er décembre 2023 et le modèle sert 0,715
(non rejoué ici) : déclaré comme tel.

## B2. Le refus de l'inapte libéral à 62 ans frappe toute la liquidation, la base CNAVPL comprise

**Ce que R-E2 dit** : le refus de l'inapte à 62 ans (`non_ouverte`, âge opposé 62,75 pour le né de
1965) vient de l'ouverture, commune à toute la personne ; il frappe aussi la pension de base de la
CNAVPL, que L. 643-3, IV, D. 643-14 et D. 351-1-14 ouvrent à 62 ans « sans doute possible ». La
fiche range ce refus parmi les erreurs de la CARCDSF, et `inaptitude_au_travail` ne dit des
professions libérales que la décote gardée.

**Ce que j'ai lu** (code de la sécurité sociale, index LEGI, pensions depuis le 1er septembre 2023) :

- L. 643-4 (LEGIARTI000047453026) : « Sont liquidées sans coefficient de réduction, même s'ils ne
  justifient pas de la durée d'assurance prévue à l'article L. 643-3, les pensions de retraite : […]
  2° Des assurés ayant atteint l'âge prévu au IV de l'article L. 643-3 et relevant de l'une des
  catégories suivantes : a) Reconnus inaptes au travail dans les conditions prévues à l'article
  L. 643-5 ».
- L. 643-3, IV (LEGIARTI000047453031, du 1er septembre 2023 au 31 décembre 2025 ; la rédaction du
  31 décembre 2025, LEGIARTI000053280388, le garde mot pour mot) : « IV.-La condition d'âge prévue au
  premier alinéa du I du présent article est abaissée, dans des conditions fixées par décret, pour
  les assurés relevant des 2° et 3° de l'article L. 643-4. »
- D. 643-14 (LEGIARTI000047634694) : « L'âge prévu au IV de l'article L. 643-3 est celui prévu à
  l'article D. 351-1-14. »
- D. 351-1-14 (LEGIARTI000047634688, puis LEGIARTI000053355951 depuis le 1er janvier 2026, mêmes
  mots) : « L'âge prévu au premier alinéa de l'article L. 351-1 est abaissé, en application de
  l'article L. 351-1-5, à soixante-deux ans pour les assurés reconnus inaptes au travail dans les
  conditions prévues à l'article L. 351-7 et pour les assurés dont l'incapacité permanente est
  supérieure ou égale au pourcentage prévu pour l'application de l'article L. 821-2. »

Ces trois références sont celles que Retouches 2 avait citées dans `cavamac_minoration_age_seul` : je
les ai reprises après les avoir relues à l'index, mot pour mot.

**Un point que le texte ne tranche pas, que R-E2 range « sans doute possible » et que j'ai lu** : D.
351-1-14 nomme l'inapte « dans les conditions prévues à l'article L. 351-7 » (LEGIARTI000006742675 :
« Peut être reconnu inapte au travail, l'assuré qui n'est pas en mesure de poursuivre l'exercice de
son emploi sans nuire gravement à sa santé […] »), quand L. 643-4, 2°, a, nomme celui de L. 643-5
(LEGIARTI000006743795 : « L'inaptitude au travail s'apprécie en déterminant si, à la date de la
demande ou à une date postérieure, le requérant, compte tenu de son âge, de son état de santé, de ses
capacités physiques et mentales, de ses aptitudes ou de sa formation professionnelle, n'est plus en
mesure d'exercer […] »). Deux définitions, en d'autres termes. Une recherche de « L. 643-5 » dans
l'index LEGI ne rend aucun décret qui fixe un âge à l'inapte de L. 643-5. La lecture de R-E2 est la
seule qui donne un âge au IV pour l'inapte du 2°, a (D. 643-14 ne renvoie qu'à D. 351-1-14) : la
base s'ouvre à 62 ans. Mais le texte ne dit pas en toutes lettres que l'inapte de L. 643-5 est celui de
L. 351-7 ; la fiche le dit comme tel. La CAVAMAC avait déjà cette réserve (`cavamac_minoration_age_seul`,
« si l'inapte de L. 643-5 est celui que D. 351-1-14 nomme […] : L. 643-5 n'est pas lu ici ») : elle est
levée à moitié, L. 643-5 étant lu, le renvoi restant à la lettre.

**Le modèle** (essais de la file E, relus par R-E2 dans les deux moteurs, non rejoués ici) : l'inapte
de la CARCDSF né en 1965 est refusé à 62 ans, `non_ouverte`, âge opposé 62,75 ; le salarié inapte né
la même année part, lui, à 62 ans, au motif `inaptitude`. Le refus vient, selon R-E2, de
l'ouverture commune à toute la personne : la CARCDSF n'est pas dans `SANS_LEUR_BASE` (`departs.py`,
l. 102 : la CARPV, la CAVEC et la CRPNPAC y sont), elle suit donc sa base. Je n'ai pas tracé le
chemin du refus dans le code.

**Fait** : une approximation de la version `chaque_regime_a_sa_date` de
`liquidation_regime_par_regime`, la fiche qui porte l'âge de la base des libéraux (L. 643-3, I, citée
dans son texte) : les quatre textes cités mot pour mot, la réserve de L. 643-5, le modèle, et
« erreur du modèle, posée au propriétaire, non corrigée ». Les textes sont rattachés à la version
(`textes`), et le refus est repris par un renvoi dans l'approximation « catégories sans minoration » de
`carcdsf_minoration_age_seul`. Je n'ai pas trouvé de fiche qui s'appelle « la base des libéraux » et
« porte l'âge d'ouverture » : `age_legal_par_generation` (la table, `conforme`, sans approximations) et
`cnavpl_allocation_avant_2004` (d'avant 2004) n'étaient pas le lieu ; au propriétaire de dire s'il
veut le déclarer aussi ailleurs.

## B3. Cinq écarts faibles

1. **Le trimestre de l'âge, aussi en cours de trimestre (erreur 4).** Rejoué, Python : né le 1er janvier
   1953, taux plein le 1er mars 2019 (66 ans et 2 mois), le modèle sert 1,12 au 1er mars 2022, 1,11 au
   1er décembre 2021, 1,11 au 1er février 2022. Le texte (« par trimestre civil entier d'exercice
   libéral suivant le dernier jour du trimestre civil incluant l'âge », 1 %) : onze trimestres entiers
   d'avril 2019 à décembre 2021, 1,11 ; dix d'avril 2019 à septembre 2021, 1,10 ; onze, 1,11. Donc
   1,12 contre 1,11 ; 1,11 contre 1,10 ; 1,11 des deux côtés : la phrase de la fiche, « quand l'âge
   tombe le premier jour d'un trimestre civil », ne vaut que pour ce cas. **Corrigée**, avec les trois
   effets.
2. **Les 3 et 8,75 points de l'erreur 5.** Rejoué : né le 1er janvier 1955, effet le 1er janvier 2025 :
   1,15 ; né le 1er janvier 1953, effet le 1er avril 2024 : 1,25. Les textes : 1,12 (sept trimestres à
   1 %, quatre à 1,25 %) et 1,1625 (quinze à 1 %, un à 1,25 %) : 3 points et 8,75. Ils comprennent
   le trimestre de l'âge compté à tort, qui est l'erreur 4 : 1 à 1,25 point sur 3, 1,25 sur 8,75,
   selon l'ordre du partage ; le reste est le taux, et pour le né de 1953 l'âge du départ de la
   majoration, 3,75 points chacun (R-E2, repris). **Corrigée** : la fiche le dit sous son effet.
   Le partage de R-E2 (1,25 + 3,75 + 3,75 = 8,75) est juste en arithmétique ; je ne l'ai pas refait
   trimestre par trimestre.
3. **L'article 18 du règlement de 1955.** JORFARTI000002267801 (arrêté du 1er octobre 2007, article
   2), rouvert : « L'arrêté du 6 janvier 1955 portant approbation du règlement de la section
   professionnelle des chirurgiens-dentistes relatif au régime d'assurance vieillesse complémentaire
   des chirurgiens-dentistes est abrogé à l'exception de l'article 18 des statuts relatifs au régime
   d'assurance vieillesse complémentaire. » La fiche coupait la phrase par un « […] ». Arrêté du 28
   décembre 2010, article 2 (JORFARTI000023336803, publié le 1er janvier 2011) : « L'article 18
   mentionné à l'article 2 de l'arrêté du 1er octobre 2007 est abrogé. » ; son article 3
   (JORFARTI000023336805) insère un titre VII « Retraite libérale et activité professionnelle »
   (articles 57 et 58 : cumul). Le texte de l'article 18 de 1955 n'est pas à l'index : **ce qu'il
   disait n'est pas lu**, et que ce fût le cumul est une inférence, non un texte. **Corrigée** :
   la citation en entier dans l'hypothèse de la version d'avant 2007 ; une approximation de plus
   (« L'article 18 du règlement de 1955 », versions d'avant 2007 et de 2007), sans effet probable
   sur la minoration, non établi ; le motif du texte « sans effet » le dit de même.
4. **3,75 points, non 2,5, pour les nés avant juillet 1951.** Rejoué : né le 1er janvier 1947, effet le
   1er décembre 2011, un mois avant 65 ans : le modèle sert 0,9875 (un trimestre entamé à 1,25 %) ;
   le texte (« 5 % par année d'anticipation », statuts de 2011, article 19, I, b), 0,95 si l'année
   entamée compte, 0,9958 au prorata : 3,75 points au plus. **Corrigée** : la fiche garde le cas du
   1er juillet 2011 (2,5 points) et ajoute celui-ci.
5. **Le renvoi à « l'écart 6 ».** Il est dans la note de E (`2026-11-05-carte-des-fiches-carcdsf-lue-au-droit.md`,
   ligne 21 : « du 1er au 9 janvier 2024 (écarts 1, 2 et 6 ci-dessous) »), non dans la fiche ; une
   note est un récit, qu'on ne récrit pas. Ce qu'il faut lire : les écarts **1 et 2** de la liste des
   six, et, pour le 1er au 9 janvier 2024, la **septième** erreur (point B1), l'écart 6 étant la
   réversion. Un renvoi daté a été ajouté au bout de la note de E.

## Ce que je laisse

- L'article 23 des statuts de 2007, qui compte pour les 10 % les enfants élevés neuf ans avant leurs
  seize ans (R-E2, § 1) : non repris, la fiche ne le cite pas et ce n'était pas au programme.
- Non lus, faute d'être à l'index (R-E2, § 7) : l'article 1er du code civil et l'ordonnance
  n° 2004-164 ; l'article 18 du règlement de 1955 ; le tableau de 2011 et de 2012. Non essayés :
  l'ancien prisonnier ou combattant de 2007 et le grand invalide de guerre.
- Au propriétaire : la pension du 1er janvier 2024 (B1) et le refus de l'inapte libéral par la base de la
  CNAVPL (B2), en plus des six erreurs de la note de E.
