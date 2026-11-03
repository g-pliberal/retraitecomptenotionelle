# Les corrections de la relecture R-E : les minorations de la CAVEC et de la CARPV, redites au droit

**La demande.** Le 3 novembre 2026, vague 6, la session d'orchestration confie à
la file E-bis les écarts que la relecture R-E (commit 4b8a756, note
`130/2026-11-03-relecture-minorations-cavec-et-carpv.md`) relève dans le dixième
lot de la file E (commit 9020e7b, note
`130/2026-11-03-carte-des-fiches-minorations-cavec-et-carpv-lues-au-droit.md`) :
trois moyens, sept faibles, et deux écarts de la CNAVPL hors du lot, à vérifier
et à chiffrer sans les corriger. Aucune règle du modèle ne change ; chaque texte
cité ici a été rouvert pendant la session, dans les index JORF et LEGI du dépôt
mis à jour au 3 novembre 2026 (incréments `20261103-214151`), et rien n'est repris
de la relecture sans relecture.

## Moyen 1 : la réversion n'est pas servie, en rien

Les fiches et la note de E disaient la réversion « servie coefficient compris,
15 % trop basse ». Le moteur n'en sert aucune :

- aucune fiche de réversion ne nomme `cavec_complementaire`,
  `carpv_complementaire` ni `cnavpl` (les neuf fiches `reversion*.yaml` et
  `majoration_forfaitaire_reversion.yaml`, leurs régimes lus un à un) ; `fiche_du_regime` rend alors `None`, et la ligne vaut zéro, motif
  `non_portee` (`src/retraite_notionnelle/droit/reversion.py:1818-1821`,
  `moteur/js/droit/reversion.js:1681-1686`) ;
- essai dans les deux moteurs : un vétérinaire et un expert-comptable nés le
  10 février 1964, au travail depuis leurs 26 ans à deux fois le salaire moyen,
  partis à 62 ans le 1er mars 2026, morts en juin 2027 (et en juin 2032 pour
  l'expert-comptable), conjoint né en 1962, marié en juin 1988. Par
  `servi_et_refait` (`tests/outils_pont.py`), le portage et le moteur Python
  servent la même réversion, 0 € à la CARPV, à la CAVEC et à la CNAVPL ; le
  résultat entier du moteur Python, comparé au portage par
  `tests/js/comparer.mjs`, donne 600 valeurs identiques au bit près et les
  mêmes motifs (`non_portee`, le comparateur comparant aussi les chaînes).

Ce que disent les textes, relus : à la CAVEC, 60 % des points, ceux d'avant la
mise en œuvre des statuts à 50 % (2008, article 3.17), puis 50 % des points
acquis avant le 1er janvier 2009 et 60 % des autres (2018, partie 2, article 16 ;
2026, article 1.2.2), toujours « sans application du coefficient de réduction »,
au conjoint d'au moins 60 ans, marié deux ans au moins ou dont un enfant est
issu du mariage, non remarié (articles 3.16 et 3.18 ; 15 ; 1.2.1) ; à la CARPV,
« 60 % des points acquis par le vétérinaire décédé » (2021, article 40 ; 2026,
article 8), avec « le même coefficient de minoration », sauf « si le décès de
l'adhérent se produit avant son soixante-cinquième anniversaire » (articles 41
et 9), aux mêmes conditions (articles 38 et 6).

Les deux fiches le disent désormais, et la limite le dit
(`docs/limites/ecarts-au-droit-positif.md`, la réversion : « la CNAVPL et ses
sections libérales parmi eux, dont la ligne le dit, qui vaut zéro »).

**Le calcul.** Le modèle compte les deux caisses en cotisations revalorisées ×
rendement × coefficient (détail de la pension : « coefficient d'anticipation
0.8500 »). Né le 10 février 1964, l'assuré a 65 ans le 10 février 2029 ; du
1er mars 2026 à ce jour, 2 ans, 11 mois et 9 jours, soit 12 trimestres entamés,
que le modèle compte entiers : 12 × 1,25 % = 15 %, coefficient 0,85.

- CARPV, pension servie 17 406,29 € (aux montants de 2026) ; sans le
  coefficient, 17 406,29 / 0,85 = 20 477,99 € ; mort avant 65 ans, le conjoint
  reçoit 0,60 × 20 477,99 = 12 286,79 € par an ; le modèle, 0.
- CAVEC, pension servie 27 616,84 € ; sans le coefficient, 27 616,84 / 0,85 =
  32 490,40 € ; le conjoint reçoit de 0,50 × 32 490,40 = 16 245,20 € à 0,60 ×
  32 490,40 = 19 494,24 € par an, selon la part des droits d'avant 2009, que le
  modèle ne sépare pas ; le modèle, 0.

L'écart n'est donc pas 15 % de la réversion, mais la réversion entière.

## Moyen 2 : l'arrêté de la CARPV du 2 novembre 2015, une version

L'arrêté du 2 novembre 2015 (JORFARTI000031549970, publié le 1er décembre 2015),
annexe, I, 3° : « Au quatrième alinéa de l'article 13, les mots : « titulaires de
la rente d'invalidité à 100 % » sont remplacés par les mots : « reconnus inaptes
au taux fonctionnel ou professionnel de 100 % », et après les mots : « peuvent
demander à bénéficier de la retraite », est inséré le mot : « complémentaire » ».

La chaîne se suit d'un arrêté à l'autre, texte en main :

- 2011 (JORFARTI000023448554) : « Le sixième alinéa de l'article 21 est remplacé
  par les dispositions suivantes : « Les invalides reconnus inaptes […] et
  titulaires de la rente d'invalidité à 100 % […] peuvent demander à bénéficier
  de la retraite à 60 ans sans minoration. Les invalides titulaires d'une rente
  […] ne peuvent demander à bénéficier des dispositions de l'article 23
  ci-dessous concernant la retraite progressive. » » ;
- 2014 (JORFARTI000028939421), II, a) : « les articles 9, 11, 12, 13, 20, 21, 22,
  […] deviennent respectivement les articles 8, 9, 10, 11, 12, 13, 14, […] » —
  l'article 21 devient 13 ; II, h) : « L'article 13 est ainsi modifié : ― les
  quatrième et cinquième alinéas sont supprimés ; ― au sixième alinéa, les mots :
  « article 23 » sont remplacés par les mots : « article 15 » » — le sixième
  alinéa est celui de l'inapte, le seul qui renvoie à l'article 23, devenu 15, et
  il devient le quatrième ;
- 2015 : le « quatrième alinéa de l'article 13 », qui porte « titulaires de la
  rente d'invalidité à 100 % », est bien celui-là.

Les articles des trois arrêtés (1er à 3 en 2011, 1er et 2 en 2014 et 2015) ne
fixent aucune date : chacun entre en vigueur le lendemain de sa publication, le
20 janvier 2011, le 18 mai 2014, le 2 décembre 2015. La fiche de la CARPV passe
de trois versions à six : `statuts_d_avant_2011`, `statuts_de_2011`,
`statuts_de_2014`, `inapte_a_100_pour_cent_2015`, toutes `supposee` pour le taux
et l'âge du taux plein, que nul texte publié ne donne avant 2022, puis les deux
versions lues. L'écart de l'inapte dit les trois rédactions de l'alinéa ; les
arrêtés de 2014 et de 2015 quittent les `textes_sans_effet`. Aucun chiffre du
modèle ne bouge : il minore l'inapte de la CARPV à toute date.

## Moyen 3 : le bloc « Reprise » de l'action 130

Comparé à l'ancien (`git show 9020e7b -- docs/feuille_de_route.md`), le bloc de
E avait perdu « Au propriétaire, README muet : sa septième étape, la décision de
la proposition, la retraite progressive, le cumul et la seconde pension ». La
note des décisions du propriétaire n'en dit rien (cherchée à « README »,
« proposition », « progressive », « cumul », « seconde pension ») ; elles restent
écrites dans la note `130/2026-10-17-sixieme-domaine-etape-6.md` (« La décision
de la proposition, à l'étape 7 ») et dans le corps de l'action
(`docs/feuille_de_route.md`, la clôture du domaine de la vie après le départ :
« la décision de la proposition reste à prendre, par le propriétaire : le README
ne dit rien de la retraite progressive, du cumul emploi-retraite, de la seconde
pension ni de la date de chaque pension »). Le bloc, récrit au 3 novembre 2026
en dix lignes, les y remet.

## Les sept faibles

1. **« L'arrêté du 23 mai 1953 »** (CAVEC). Le seul de l'index
   (JORFTEXT000000472264) porte « FIXATION DES COTISATIONS DE L'ASSURANCE
   VIEILLESSE COMPLEMENTAIRE POUR L'ANNEE 1953 » : corrigé. La fiche nomme
   désormais le décret n° 53-506 du 21 mai 1953, qui institue le régime
   (JORFTEXT000000670150, l'index n'en ayant que l'analyse : « ART. 5: AVANTAGES
   DU REGIME,GESTION DE LA CAISSE COMPLEMENTAIRE »), et dit qu'aucun texte lu ne
   nomme l'arrêté qui approuve les statuts d'avant 2008.
2. **L'ouverture à 60 ans avant 2008 (CAVEC) et avant 2011 (CARPV).** Déclarée
   faible dans la fiabilité des deux versions supposées. Le livre de la CAVEC,
   retéléchargé et relu (80 564 762 octets, sha256 f37b161d…d030, page 15 du
   PDF : « 1983 Les administrateurs choisissent de ne pas abaisser l'âge de
   départ en retraite à 60 ans (comme annoncé pour le régime général par Pierre
   Mauroy en 1982). Il reste et restera fixé à 65 ans. »), peut dire qu'on ne
   partait pas avant 65 ans : la fiche le dit. À la CARPV, la version d'avant
   2011 est faible en tout. Les titres que l'index donne : l'arrêté du 9 mars
   1960 vise les « ART. 10, 16 ET 21 DU TITRE II […] RELATIFS AU REGIME
   COMPLEMENTAIRE D'ASSURANCE VIEILLESSE » ; celui du 16 septembre 1968, les
   articles « 9, 17, 21, 23, 24, 32 & 34 » des statuts des deux régimes,
   vieillesse complémentaire et invalidité-décès ; celui du 8 juillet 1977, les
   articles « 21, 23, 23 BIS, 24, 36 », sans nommer le régime ; celui du
   30 décembre 1970, l'article 21 des statuts « RELATIFS AU REGIME D'ASSURANCE
   INVALIDITE DECES ». La relecture les disait quatre à modifier l'article 21 du
   titre II : seul celui de 1960 le dit, et celui de 1970 vise un autre régime.
3. **La suppression de deux alinéas en 2014.** Effet inconnu : la version
   `statuts_de_2014` le dit, l'approximation aussi, `a_relire` le demande.
4. **Le 1er janvier 2009 de la CAVEC.** Déclaré dans les conditions de la
   version de 2008 et dans `a_relire` : les statuts de 2018 et le règlement de
   2026 datent « avant le 1er janvier 2009 » ce que l'article 3.17 de 2008 dit
   « avant la mise en œuvre des présents statuts », ce qui situe leur mise en
   œuvre à cette date, au moins pour la réversion ; la règle d'avant étant
   supposée la même, rien ne bouge.
5. **La portée de l'inapte de la CAVEC de 2008 à 2019.** Corrigée dans l'effet
   de l'écart : l'inapte n'y est servi sans abattement que si la base de la
   CNAVPL le liquide à ce titre, ce qu'elle ne fait qu'« à partir de l'âge prévu
   au premier alinéa de l'article L. 351-1 » (L. 643-3, I, les cinq rédactions
   de 2004 au 1er septembre 2023, relues) ; cet alinéa renvoie à L. 161-17-2
   depuis le 1er juillet 2011 (L. 351-1, LEGIARTI000023035688), qui dit
   « soixante-deux ans pour les assurés nés à compter du 1er janvier 1955 »
   (LEGIARTI000025014605). Pour elles, la perte se mesure à 62 ans : 12 × 1,25 %
   = 15 % ; depuis le 28 juin 2019, à 60 ans : 20 × 1,25 % = 25 %. La même
   question se pose à la CARPV de 2011 à 2021, dont l'alinéa vise l'inapte
   reconnu « en application de l'article L. 643-4 » : le texte ne dit pas si
   cette reconnaissance précède l'âge de la base ; la fiche le déclare.
6. **Le second test neuf ne tenait que la cohérence de la fiche.** Corrigé par
   un test tiré de la source,
   `test_chaque_version_nait_d_un_texte_a_sa_date_du_journal_officiel`
   (`tests/test_sections_liberales.py`) : une table des textes dont naît chaque
   version, avec leur publication et leur entrée en vigueur relevées à l'index
   JORF pendant la session (la CAVEC : 1er mars 2008, 4 septembre 2018, 27 juin
   2019, 17 juillet 2026, chacun le lendemain ; la CARPV : 19 janvier 2011,
   17 mai 2014, 1er décembre 2015, le lendemain, 19 octobre 2021, au 1er janvier
   2022 que fixe son article 2, 17 juillet 2026, le lendemain), les articles des
   arrêtés de 2018, 2019 et 2026 relus, qui ne fixent aucune date. Le test veut
   les naissances de la fiche égales à la table, lues et supposées, chacune à sa
   date : vu rouge sur la CARPV faute des versions de 2011, 2014 et 2015, vert
   après.
7. **La preuve de la renumérotation de 2014.** La fiche cite désormais le a) du
   II, qui la dit, et le h), qui récrit l'alinéa (moyen 2).

## Hors du lot : deux écarts de la CNAVPL, pour une file du modèle

Vérifiés à la source et dans les deux moteurs, non corrigés.

- **L'inapte minoré.** L. 643-4, en vigueur pour les pensions qui prennent
  effet depuis le 1er septembre 2023 (LEGIARTI000047453026) : « Sont liquidées
  sans coefficient de réduction, même s'ils ne justifient pas de la durée
  d'assurance prévue à l'article L. 643-3, les pensions de retraite : […] 2° Des
  assurés ayant atteint l'âge prévu au IV de l'article L. 643-3 et relevant de
  l'une des catégories suivantes : a) Reconnus inaptes au travail dans les
  conditions prévues à l'article L. 643-5 » ; le IV de L. 643-3
  (LEGIARTI000053280388, pour les pensions qui prennent effet depuis le
  1er septembre 2026) abaisse « dans des conditions fixées par décret » l'âge du
  I pour les assurés des 2° et 3° de L. 643-4 — décret que l'index thématique
  ne porte pas, cherché ; la rédaction de 2008 (LEGIARTI000019959512) disait
  l'âge du premier alinéa du I. Essai : le vétérinaire né le 10 février 1964,
  `inaptitude: oui`, parti à 64 ans le 1er mars 2028, au-delà de l'âge du I, que
  le IV ne fait qu'abaisser : la CNAVPL, 17 889,98 points × 0,683199 € =
  12 222,42 €, devrait être servie sans coefficient ; le modèle la sert au
  coefficient 0,85, comme sans inaptitude, soit 10 389,05 € : l'inapte perd
  12 222,42 − 10 389,05 = 1 833,36 € par an (aux montants de 2028). La fiche
  `inaptitude_au_travail` ne nomme pas la CNAVPL, et aucune fiche ne lit L. 643-4
  pour elle.
- **La CNAVPL ouverte à 60 ans à la génération 1964.** L. 643-3, I : « La
  liquidation de la pension prévue à l'article L. 643-1 peut être demandée à
  partir de l'âge prévu au premier alinéa de l'article L. 351-1 », l'âge de
  L. 161-17-2 : pour qui est né en 1964, 63 ans pour une pension qui prend
  effet avant le 1er septembre 2026 (D. 161-2-1-9, 10°, LEGIARTI000047634502),
  62 ans et 9 mois depuis (L. 161-17-2, 3°, « nés entre le 1er janvier 1963 et
  le 31 mars 1965 », LEGIARTI000053280889). Essai, le même vétérinaire sans
  inaptitude : à 60 ans, le 1er mars 2024, le modèle oppose un âge d'ouverture
  de 60 ans (`age_ouverture_opposable`, motif `age_legal`) et sert la CNAVPL,
  15 641,60 points × 0,6399 € × 0,75 = 7 506,79 € par an ; à 62 ans, le
  1er mars 2026, 16 752,15 × 0,6599 € × 0,75 = 8 291,06 €. La loi n'ouvre pas
  sa base avant le 10 novembre 2026, ses 62 ans et 9 mois. La fiche du régime
  (`data/reference/regimes/cnavpl.yaml`) lit `age_legal_par_generation`, qui
  rend 62,75 ans à la génération 1964 : l'ouverture à 60 ans vient d'ailleurs,
  que la file du modèle trouvera. L'essai de la réversion (moyen 1) en porte
  la trace : la ligne de la CNAVPL y a pour base une pension de 2026 que la loi
  ne liquide pas encore.

## Ce que l'étape laisse

- Les tests : `tests/test_sections_liberales.py` et `tests/test_carte.py`,
  61 passés ; `-m rapide`, et sous `PRESOMPTIONS_DECALEES=1`, au commit.
  `conservation.py --depuis HEAD` dit changés le paragraphe de la réversion
  des limites, un état, et les lignes de veille des deux fiches ; la référence
  figée l'admet (`test_rien_de_ce_qui_est_gele_ne_se_perd`, vert). Le paquet
  du site, refait, ne change pas. La carte : 85 fiches, 503 manques, aucun aux
  deux fiches.
- `textes.py --inscrire`, après l'incrément LEGI du 3 novembre au soir, inscrit
  neuf textes et quelque six cents rédactions que citent les fiches d'autres
  files, aucune des deux fiches : non commités, ce fichier partagé n'étant pas
  de cette zone ; la veille suivante les inscrira.
- À une file du modèle : la réversion de la CNAVPL et de ses sections, les deux
  inaptes (les sections, la CNAVPL), l'ouverture de la CNAVPL à 60 ans.
- À relire au Bulletin officiel : les statuts d'avant 2008 de la CAVEC, d'avant
  2022 de la CARPV, et les deux alinéas que l'arrêté de 2014 supprime ; le
  décret du IV de L. 643-3.
- Le lot suivant : la CAVAMAC (`cavamac_minoration_age_seul`) ou la CARCDSF.
