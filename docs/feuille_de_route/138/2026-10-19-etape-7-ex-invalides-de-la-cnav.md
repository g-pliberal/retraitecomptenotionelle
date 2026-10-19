# Étape 7, douzième partie : les ex-invalides de la Cnav, dans la grille du coût

**La demande.** Vague B du 19 octobre 2026, session 3 de la première salve,
lancée par la session de suivi sur la demande du propriétaire (« Vas-y, lance
ce qui n'a pas besoin de ma décision ») : le premier point de « Ce qui reste »
de la onzième partie (note « inaptes de la Cnav ») — les ex-invalides, 8,8 %
des départs de la Cnav, que les quatre carrières du privé portaient encore.
Aucune règle du scénario 1 n'est en cause : la fiche
`pension_d_invalidite_substituee` remplace déjà, à l'âge légal, la pension
d'invalidité par la pension de vieillesse de l'inapte, au taux plein
(L. 341-15) ; chaque année d'invalidité valide quatre trimestres et ouvre des
points de l'Agirc-Arrco sur le salaire d'avant l'arrêt
(`periodes_non_travaillees.csv`) ; sous la proposition, elle ne verse rien au
compte, qui se liquide à 65 ans (README). Ni veille du droit, ni entrée au
journal.

**La source, relue le jour même.** L'étude 2023-014 de la Cnav (Couhin et
Floderer, février 2023), sur les 56 914 ex-invalides partis en 2021 : un
premier trimestre l'année de leurs dix-huit ans, 171 trimestres tous régimes,
dont 64 % cotisés (73 % pour les hommes, 57 % pour les femmes), un salaire
annuel moyen de 18 468 € de 2020, 97 % du SMIC annuel d'octobre 2021,
19 073,64 € (tableau 4) ; un départ à 62,06 ans en moyenne, au mois près
pour 97 % (tableau 3). À cinquante-cinq ans, un quart travaille encore et la
moitié touche une pension d'invalidité (graphiques 3 et 4) ; le chômage, la
maladie et, pour les femmes, l'AVPF font le reste de leurs périodes
assimilées.

**Ce qui est fait.**

- *Le cas type* (`castypes.EX_INVALIDE_CNAV`), variante du salarié au SMIC, à
  qui la page Coût rapporte son poids, comme l'inapte : il travaille de
  dix-huit à quarante-cinq ans, puis touche une pension d'invalidité, que sa
  carrière déclare par ses années (`invalidite`, présomption
  `pension_d_invalidite_de_la_periode`) — 112 trimestres cotisés sur 176, la
  part cotisée publiée. Le chômage, la maladie et l'AVPF, que le cas type n'a
  pas, se fondent dans son invalidité : d'où une entrée plus précoce que celle
  du chronogramme. C'est la part cotisée qui sépare les deux systèmes : la
  proposition ne porte au compte que les années cotisées, quand le droit en
  vigueur sert le taux plein et des points sur toute la carrière. Il part à
  soixante ans né en 1950, à soixante-deux né en 1955 et après ; inactif au
  lieu d'invalide, il attendrait soixante-cinq puis soixante-sept ans. Sous la
  proposition, son compte se liquide à 65 ans, l'invalidité prolongée ne
  cotisant pas.
- *Son salaire* : 1,29 SMIC chaque année, ce qui lui donne, né en 1959 et
  parti en 2021, le salaire annuel moyen publié — 97,2 % du SMIC de 2021 dans
  le détail de sa pension. Le SMIC de chaque année n'en ferait que 75 % : le
  salaire annuel moyen revalorise les salaires sur les prix, et le SMIC a crû
  plus vite qu'eux. Entré en invalidité à cinquante ans, comme la note du
  19 octobre l'envisageait, il aurait eu la part cotisée des seuls hommes,
  73 %, à 1,22 SMIC.
- *Sa part* : 8,78 % de la Cnav (`PART_EX_INVALIDES_CNAV`), celle de ses
  départs de 2020 à 2024 ; les quatre carrières du privé se partagent le
  reste, 20,71 % chacune, l'inapte gardant ses 8,37 %.
- *Le pont* : le portage simule l'ex-invalide né en 1965 au bit près du
  moteur Python (`test_pont.py`, `CASES_DU_COUT`) ; aucune case ne finissait
  encore en invalidité.
- *La population de l'étape 14* : il lui cède sa part, comme l'inapte
  (`reference_population`, par `cas_type_affiche`).

**Sa mortalité, pas encore.** L'ex-invalide vit au rythme du vingtile de son
salaire, comme les cas types de la page, quand ceux de la Cnav vivent, à
soixante-deux ans, 6,2 ans de moins que les pensions normales chez les hommes
et 4,4 chez les femmes. La population est au dépôt (`cnav_ex_invalide`,
facteurs 1,81 et 1,42) ; mais
`test_la_page_cout_dit_au_rythme_de_qui_chaque_cas_type_survit`
(`test_web.py`) veut que toute variante qui vit à part se nomme dans la phrase
des poids de la page Coût, et `moteur/js/pages.js` est, pendant cette vague, à
la seule session des pages. La mortalité et sa phrase se feront donc ensemble,
par une session qui tienne la page.

**Ce que l'ex-invalide déplace**, mesuré sur `881bd21`, la grille d'avant
contre celle d'après. Le système actuel reste calé sur la dépense du COR,
15,30 % du PIB en 2070 ; sa dérive, ce que ses masses font seules, passe de
1,0177 à 1,0188 en 2030, de 1,0255 à 1,0278 en 2050, de 1,0483 à 1,0503 en
2070. La proposition passe de 8,928 à 8,873 % du PIB en 2030, de 9,798 à
9,745 % en 2050, de 8,186 à 8,139 % en 2070 ; son solde moyen de 2026 à 2070,
de −1,119 à −1,067 point ; sa garantie en 2070, de 13,79 à 13,94 Md€
constants. Le scénario 2 passe de 4,711 à 4,692 % du PIB en 2070, le scénario
4 de 10,435 à 10,350 %. L'ex-invalide coûte moins à la proposition qu'au droit
en vigueur : il part trois ans plus tard, et seize ans d'invalidité ne lui ont
rien porté au compte, ce que la garantie ne comble qu'en partie. La pension
d'invalidité qu'il touche de 62 à 65 ans n'est comptée nulle part, ce que les
limites déclarent déjà (`docs/limites/4-regimes-incomplets.md`, « La moitié de
ceux que le report fait attendre sont en emploi »).

**Les tests** : `test_l_ex_invalide_de_la_cnav_part_au_taux_plein_des_l_age_legal`
(`test_moteur.py`), sa carrière, ses trimestres, sa pension d'invalidité, son
départ avec et sans l'invalidité, son salaire annuel moyen contre celui de la
Cnav ; `test_l_inapte_porte_la_part_de_la_cnav_que_ses_departs_lui_donnent` et
`test_la_cnracl_se_partage_entre_ses_departs_actifs_et_sedentaires`
(`test_cout.py`), les parts de la Cnav, les ex-invalides compris ;
`test_la_grille_du_cout_passe_le_pont_au_bit_pres_du_moteur_python`
(`test_pont.py`), une case de plus.

**Les mesures qu'il déplace**, chacune relevée avant et après :

- *Le passé refait* : 2009 passe de −11,0 à −10,7 % ; le cliquet descend de
  12 à 11 % (`test_la_projection_refait_le_passe`).
- *Les groupes du COR*, en croissance de la dépense de 2024 à 2070 : les
  complémentaires de +4,8 à +5,2 %, les non-salariés de +6,0 à +8,2 %, LURA
  de +2,3 à +2,5 % ; la FPE de +22,0 à +21,6 %, la CNRACL de +10,9 à +10,5 %.
  Les tolérances des complémentaires et des non-salariés passent à 6 et 9 %
  (`DECOMPOSITION_GROUPES_SUIVIS`), comme l'étape 14 et la PMR les avaient
  relevées. Les non-salariés ne bougent pas de leur fait : l'ex-invalide sert
  LURA et les complémentaires dans d'autres proportions que les carrières dont
  il prend la part, et déplace le calage des poids par groupe
  (`_poids_par_groupe`), qui ramène ensuite les poids de chaque année à leur
  somme ; sous la table commune même, leur masse de 2070 gagne 2,4 %. Ni
  l'alignement des survies, ni la mortalité de l'ex-invalide, essayée à part
  (+5,26 % pour les complémentaires), n'y sont pour rien.
- *Les moins de 65 ans de l'AWG* : l'effet de la grille, porté au périmètre de
  l'AWG, s'en écarte de 0,16 point en 2070 et de 0,17 en 2030, au lieu de
  0,12 et 0,14 ; les deux tolérances passent de 0,15 à 0,2
  (`test_facteurs_depense.py`). L'ex-invalide part à soixante-deux ans, comme
  97 % des ex-invalides de 2021, quand les carrières dont il prend la part
  partent plus tard.
- *L'EACR de 2024* : l'âge moyen de la grille reste à 62,3 ans pour 63,6 ;
  les départs à 62 ans passent de 33 à 37 % pour 26, ceux à 60 ans, du
  salarié au SMIC né en 1964, de 16 à 15 % pour 5 : moins de trois fois la
  part de l'EACR, le seuil du défaut que le test décrit passe à deux fois et
  demie (`test_la_grille_part_trop_tot_et_trop_groupee`).
- *Le coefficient de la proposition* : celui de 2070 passe de 0,9955 à
  1,0013 ; la proposition n'est plus sous un que quarante-quatre années sur
  quarante-cinq, au plus bas 0,83 en 2048. Les pages suivent le signe, et
  l'entrée `cas_types.coefficient_sous_un` du catalogue des affirmations
  (`data/reference/site/affirmations.yaml`) dit désormais la branche du milieu
  de la phrase de Cas types, son identifiant gardé.
- *Les fichiers figés* (le paquet, `agregats.json`, le bilan) et les
  affirmations qui lisent la page, que la fabrique de GitHub refait avant la
  suite : refaits ici par `regenerer.py`, ils repassent, l'affirmation
  ci-dessus comprise.

**Le registre** : `prisme` reste `a_reprendre` au chantier 138.7 : l'ex-invalide
a sa carrière et sa part, non sa mortalité.

**Un défaut de la même classe, chez l'inapte.** Son salaire, 70 % du SMIC de
chaque année, ne lui donne, né en 1959 et parti en 2021, qu'un salaire annuel
moyen de 55 % du SMIC de 2021, quand la Cnav publie 68 % ; il faudrait
0,86 SMIC. Mais ses 116 trimestres sont tous cotisés, quand la Cnav en compte
56 % pour les anciens titulaires de l'AAH et 71 % pour les autres inaptes,
quelque 76 sur 116 : les deux écarts se compensent en partie dans son compte,
et relever son salaire seul l'éloignerait de ce qu'il cotise. Sa pension du
régime général, portée au minimum contributif, n'en dépend pas. Il se recale
sur les deux à la fois, comme l'ex-invalide.

**Ce qui reste** du point, dans l'ordre :

1. *La mortalité des ex-invalides et sa phrase*, en un seul envoi, par une
   session qui tienne la page Coût : `mortalite="cnav_ex_invalide"` sur
   `EX_INVALIDE_CNAV` ; le test de sa survie, sur le modèle de
   `test_l_inapte_vit_au_rythme_des_inaptes_de_la_cnav` ; dans la phrase des
   poids de `pages.js`, l'ex-invalide nommé avec l'inapte, et son entrée dans
   `nommees` (`test_web.py`) ; les cliquets du coût qu'elle déplace.
2. *À la session des pages, le coefficient tout juste au-dessus de un* : la
   page Coût écrit « Les 1,00 de la proposition en 2070 disent une marge de
   0 % », Cas types « supérieur les autres, jusqu'à 1,00 en 2070 » ; il leur
   faut, au-dessus de un, les décimales que `decimalesSousUn` donne au-dessous.
   Et l'extrait de `cas_types.coefficient_sous_un` change de branche avec le
   signe : à un millième de un, il basculera encore ; une phrase commune aux
   trois branches le tiendrait.
3. *L'inapte recalé* sur son salaire annuel moyen et sa part cotisée
   (ci-dessus).
4. *La forme de la surmortalité* (note du 19 octobre, « inaptes de la Cnav »,
   point 2), pour les deux populations.
5. *La carrière heurtée*, au propriétaire (étape 19, note du 18 octobre) : la
   grille a désormais l'inaptitude et l'invalidité ; la carrière longue manque
   encore.
