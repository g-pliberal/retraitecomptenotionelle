# Les six écarts de la relecture R-H6, déclarés dans la fiche de l'activité accessoire (H6-bis)

**Le 6 novembre 2026** (session H6-bis, onzième vague, sur Opus). La relecture R-H6
(`2026-11-06-relecture-r-h6.md`, § 6) a trouvé conforme le travail de H6 (commit dbf6104),
avec six écarts faibles, de déclaration ou de preuve. Chacun est relu à la source puis écrit
dans la fiche `un_statut_par_annee`. Aucun code, aucun test, aucune donnée lue par le paquet
ne change : `construire_donnees.py` rend le paquet identique, et aucune valeur servie ne
bouge. La constante `REGIMES_DES_ORGANISATIONS_SPECIALES` reste telle quelle.

## Ce qui a été lu

Index LEGI à jour au 2 novembre 2026 (20261102-213929) et JORF au 3 novembre
(20261103-002311), récupérés ce jour ; la base de la Cnav, par son API, ce jour.

- *R. 711-1*, LEGIARTI000006752039 (21 décembre 1985 au 16 mai 1991) : « 9°) la compagnie
  générale des eaux » ; `--diff` : la rédaction du 17 mai 1991 ne fait que l'ôter et
  renuméroter. *Article 61 du décret n° 46-1378* (LEGIARTI000006761348, du 9 juin 1946 au
  20 décembre 1985) : « 9° La Compagnie générale des eaux ». *Loi n° 91-73, article 17, I*
  (JORFARTI000001952341) : « Il est mis fin à compter de la même date [le 1er janvier 1991]
  au régime spécial de la Compagnie générale des eaux ». *Décret n° 91-489 du 14 mai 1991*
  (JORFTEXT000000866470, JO du 17 mai 1991) : son résumé, qui « ACTUALISE LA LISTE […]
  DRESSEE A L'ART. R711-1 ».
- *R. 711-24*, LEGIARTI000006752270 (21 décembre 1985 au 5 mai 2017), en entier. *Décret
  n° 97-1325* (LEGITEXT000005624982), ses visas. *D. 412-79*, ses dix-sept rédactions, de
  LEGIARTI000006736957 (1985) à LEGIARTI000049795072 (1er juillet 2024, en vigueur) : chacune
  porte les mêmes « c. », « d. » (la RATP), « f. » (la compagnie générale des eaux) et
  « i. » (R. 711-24). Les visas des décrets du régime de la RATP qui citent R. 711-1, cherchés
  sans borne dans le JORF (« transports parisiens » avec « R. 711-1 » ou « R. 711-24 »), et
  lus : n° 91-226 (JORFTEXT000000172016), n° 2004-174 (LEGITEXT000005765413), n° 2005-1635
  (JORFTEXT000000454090), n° 2005-1639 (JORFTEXT000000815795), n° 2008-637
  (JORFTEXT000019103570) ; la recherche sort aussi les arrêtés annuels du taux de sa
  contribution patronale, de 2012 à 2024, dont l'extrait, de 2014 à 2024, vise « L. 711-1 et
  R. 711-1 ». « transports parisiens » avec « R. 711-24 » : rien dans le JORF ; dans LEGI,
  D. 412-79 seul.
- *Le résumé du décret n° 80-475* (JORFTEXT000000696623), relu : sa ponctuation est
  « 01-07-1980,LES », « SPECIAL,ET,A », « GENERAL,SONT », « CONTREPARTIE,ILS », sans espace ;
  la fiche le citait espacé, c'est corrigé dans les deux versions qui le citent.
- *D. 171-11*, LEGIARTI000006735491 et LEGIARTI000030910553, en entier : « D. 171-3 à
  D. 171-10 » devient « D. 171-3 à D. 171-9 » en 2015, rien d'autre.
- *La lettre Cnav du 25 janvier 1988* (`LE_CN_25011988.aspx`), relue entière par
  `/reference/referencesByFileLeafRef/` : ses situations n° 1 et n° 2.
- *Les valeurs du calcul de 2015* : `revalorisation_salaires.csv`, ligne
  « 2022-01-01,2015,1.049 » ; `smic_horaire.csv`, « 2015,9.610000 ».

## Les six écarts, et ce qui est écrit

1. **La compagnie générale des eaux.** Déclarée dans l'approximation « Qui est l'agent d'un
   régime spécial », et lue dans `sources.lectures` : au 9° de R. 711-1 du 21 décembre 1985
   au 16 mai 1991, et de l'article 61 du décret n° 46-1378 avant ; régime fermé le
   1er janvier 1991. Non ajoutée à la constante, et le code ne change pas : le régime n'est
   pas routable. Vérifié : aucune ligne de `src/` ni de `moteur/js/` ne nomme
   `compagnie_generale_eaux` ; le paquet ne le nomme qu'à `inventaire` (son code et son
   manque) ; son fichier de régime a `statuts: []` et dit que son salarié se simule en
   salarié du privé. **Aucune pension n'en dépend.** L'y ajouter demanderait, de plus, de
   dater la constante (le régime finit en 1990, la règle en 2014).
2. **De 1981 à 1985, ce qui est lu.** La version `dispense_de_l_activite_accessoire` porte un
   champ `ce_qui_est_lu` : de 1986 à 2014, D. 171-2 et D. 171-4 au texte ; de 1981 à 1985, le
   seul résumé du décret n° 80-475, cité mot pour mot, dont le champ ne renvoie ni à R. 711-1
   ni à l'article 61 du décret n° 46-1378, et dit « OU REDUIT » : NON LU, que la règle de ces
   années vise les seuls régimes de R. 711-1, ne compte que l'activité accessoire, et laisse
   le militaire. Renvoyé au fac-similé du JO du 29 juin 1980. La file des fac-similés
   (`docs/feuille_de_route/138/2026-11-05-la-file-des-fac-similes.md`) ne porte pas encore le
   décret n° 80-475 : H6 demandait de l'y ajouter, et cette note de l'action 138 n'est pas de
   ma zone (candidat 1).
3. **R. 711-24 et la RATP.** Dans l'approximation : le décret n° 97-1325 range la CCI de
   Paris sous R. 711-24 (`cci_paris`, sans statut à l'inventaire, aucune ligne de `src/` ni de
   `moteur/js/` : sans effet) ; pour la RATP, **point non tranché**. Pour la ranger sous
   R. 711-1 : cinq décrets de son régime, de 1991 à 2008, visent R. 711-1. Contre : un visa
   n'est pas une disposition, R. 711-1 ne la nomme à aucun numéro, et D. 412-79, de 1985 à
   aujourd'hui, la met au « d. », à part du « c. » (le 7°, chemins de fer d'intérêt local et
   tramways) et du « i. » (R. 711-24) — une liste qui garde pourtant, en 2024, la compagnie
   générale des eaux fermée en 1991, d'où son faible poids. L'effet, ci-dessous.
4. **L'année 2015, à droit exact** : 48,11 €, ci-dessous, déclaré dans l'approximation des
   années entières, avec son hypothèse (mensualités égales, celles de janvier à juin versées
   avant le 19 juillet).
5. **La lettre de 1988** : sa situation n° 2 est citée dans la lecture et dans
   l'approximation « Ce que la règle ne touche pas ». Un relevé ne dit pas si la cotisation
   ouvrière a été précomptée (situation n° 1, les droits restent acquis) ou si le report est
   venu de la déclaration sans précompte (situation n° 2, la Cnav l'annule) : le modèle garde
   le report dans les deux ; l'effet de la seconde est déclaré non mesuré.
6. **D. 171-11.** La lecture et l'approximation « Deux règles voisines » le citent mot pour
   mot, champ compris (« ne relevant pas, au titre de leur activité principale, des
   dispositions du livre IV du présent code »). « Ni Ircantec » est ôté : l'article n'en dit
   rien, et l'affiliation à l'Ircantec relève du décret n° 70-1277, non lu. La note de H6 (un
   récit) garde ses mots ; la fiche porte la correction. D. 171-11 nomme les « agents
   permanents des collectivités locales », non tout agent de la CNRACL : le candidat de H6,
   qui dit « le fonctionnaire de l'État ou de la CNRACL », est à lire à ce champ.

## Les chiffres, posés à la main

**Le cas** (celui de H6) : né le 15 janvier 1960, entré en 1982, parti à 62 ans (effet au
1er février 2022) ; salarié du privé en plus, à 0,3 fois le salaire moyen. Le taux du régime
général : 160 trimestres tous régimes (quatre par an, 1982 à 2021) sur les 167 de la
génération 1960, sept manquants, moins que les vingt jusqu'à 67 ans : 50 − 7 × 0,625 =
45,625 %. Le salaire annuel moyen est celui que le modèle sert, que cette session ne touche
pas.

- **L'agent de la RATP, de 2000 à 2004** (servi par les deux moteurs, `servi_et_refait`) :
  RATP 33 218,94 € ; régime général 10 130,98 × 0,45625 = 4 622,26, × 20 = 92 445,19, / 167 =
  **553,56 €** ; Arrco 203,81 points × 1,2841 × 0,93 = 243,40 € ; total 33 218,94 + 243,40 +
  553,56 = 34 015,90 €. La lecture qui range la RATP sous R. 711-1 (moteur Python, la
  constante élargie à `ratp` en mémoire, le code inchangé) : plus de régime général, et
  l'Arrco liquidée sans coefficient d'anticipation, 261,72 € (le modèle sert 261,72 ; 203,81
  × 1,2841 = 261,71 sur les points arrondis) ; 261,72 × 0,93 = 243,40, soit 18,32 € de plus ;
  total 33 218,94 + 261,72 = 33 480,66 €, **535,24 € de moins par an** (553,56 − 18,32).
- **L'année 2015, à droit exact** : le modèle sert 11 739,30 × 0,45625 × 4 / 167 = 5 356,06
  × 4 / 167 = 128,29 €. Salaire nominal de 2015 : 11 739,30 / 1,049 = 11 191,90 € ; la
  moitié versée à compter du 19 juillet : 5 595,95 €. Un trimestre vaut 150 × 9,61 =
  1 441,50 € ; 3 × 1 441,50 = 4 324,50 ≤ 5 595,95 < 4 × 1 441,50 = 5 766 : **trois
  trimestres**. Salaire annuel moyen : 5 595,95 × 1,049 = 5 869,65 €. Pension :
  5 869,65 × 0,45625 = 2 678,03, × 3 = 8 034,08, / 167 = **48,11 €**. Le modèle sert
  128,29 − 48,11 = 80,18 € de plus ; l'année ôtée, 48,11 € de moins.

## Les tests

`test_carte`, `test_cumul_activites`, `test_referents`, `test_trajectoire` (les quatre qui
nomment la fiche ; aucun ne nomme la constante), `test_regle_de_chacun`, `test_contrats`,
`test_versions`, `test_textes`, `test_donnees`, `test_sncf_ratp`, `test_prose` et les
fichiers qui lisent la feuille de route, `test_web` compris, en entier : verts, hors
`test_le_tableau_de_bord_n_est_pas_perime` et `test_les_temoins_du_portage_sont_a_jour`,
rouges connus que GitHub refait ; `-m rapide`, et `-m rapide` sous
`PRESOMPTIONS_DECALEES=1` : seuls les onze rouges connus de `test_pages_en_dossier` ;
`verifier_prose.py`. Le cliquet des textes reste à 9 307 ; le paquet ne change pas.

## Candidats, hors de cette tâche

1. *La file des fac-similés* (action 138) : y inscrire le décret n° 80-475, JO du 29 juin
   1980, JORFTEXT000000696623, pour la fiche `un_statut_par_annee`.
2. *La RATP* (sessions du modèle) : trancher si son agent relève de D. 171-2 de 1981 à 2014,
   par une source de la caisse ou de la Cnav qui le dise ; effet sur le cas, 535,24 € par an.
3. *R. 711-24* : l'article 23 du décret du 28 octobre 1935, non lu, dirait quels autres
   régimes il vise.
