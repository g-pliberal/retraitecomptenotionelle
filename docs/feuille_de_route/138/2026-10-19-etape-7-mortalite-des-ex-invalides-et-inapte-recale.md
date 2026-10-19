# Étape 7, quatorzième partie : la mortalité des ex-invalides de la Cnav, sa phrase sur la page Coût, et l'inapte recalé

**La demande.** Vague B du 19 octobre 2026, session 21 de la cinquième salve,
lancée par la session de suivi sur la demande du propriétaire (« Vas-y, lance
ce qui n'a pas besoin de ma décision ») : ce que le bloc de l'étape confie à
une session qui tienne la page Coût, les points 1 et 3 de « Ce qui reste » de
la douzième partie (note « ex-invalides de la Cnav ») — la mortalité des
ex-invalides et sa phrase, en un envoi, puis l'inapte recalé. Ni le déficit
des scénarios 3 et 5, ni la limite de fin d'étape. Aucune règle du scénario 1
n'est en cause : la carrière d'un cas type de la grille n'en change aucune ;
ni veille du droit, ni entrée au journal.

**La mortalité des ex-invalides, et sa phrase** (`77cf2da`).

- *Sa survie.* L'ex-invalide de la grille (`castypes.EX_INVALIDE_CNAV`) vit au
  rythme des ex-invalides de la Cnav (`mortalite="cnav_ex_invalide"`, facteurs
  1,81 et 1,42 sur la table générale de 2017, calés sur leur espérance à
  65 ans du Cadr'@ge n° 40) : sa survie, cohorte par cohorte depuis son
  départ, est celle de cette population rapportée à la population générale, à
  nombre de décès égal (`cout._survies`), comme celle de l'inapte ; son
  diviseur garde le vingtile de son salaire. Parti en 2022, comme l'inapte né
  en 1960, il meurt plus vite que lui, et l'inapte que le salarié au SMIC : à
  soixante-deux ans, la Cnav mesure à ses ex-invalides 6,2 et 4,4 ans de
  moins qu'à ses pensions normales, hommes et femmes, à ses inaptes 4,7 et
  4,1.
- *Sa phrase* (`pages.js`, dépliant « Les quatre systèmes comparés, du passé
  jusqu'à 2070 ») : « Le salarié reconnu inapte au travail et le salarié
  ex-invalide, comptés avec le salarié au SMIC dans le dépliant « Ce que
  chaque carrière type pèse dans ces chiffres », survivent, eux, l'un au
  rythme des inaptes de la Cnav, l'autre au rythme de ses ex-invalides. »
- *Ce qu'elle déplace*, mesuré sur `384d341`, le paquet d'avant contre celui
  d'après, refaits tous deux par `construire_donnees.py`, celui de `main`
  n'étant pas celui de ses sources. La dérive du système actuel passe de
  1,0188 à 1,0190 en 2030, de 1,0278 à 1,0285 en 2050, de 1,0503 à 1,0507 en
  2070. La proposition, de 8,873 à 8,876 % du PIB en 2030, de 9,745 à 9,751 %
  en 2050, de 8,139 à 8,144 % en 2070 ; son solde moyen de 2026 à 2070, de
  −1,067 à −1,072 point ; sa garantie en 2070, de 13,94 à 13,92 Md€
  constants ; son coefficient de 2070, de 1,0013 à 1,0006, au-dessus de un
  encore, et la branche des phrases de Cas types ne bascule pas. Le scénario 2
  passe de 4,692 à 4,697 % du PIB en 2070, le scénario 4 de 10,350 à
  10,359 %. L'ex-invalide coûte moins à la proposition qu'au droit en
  vigueur : mort plus tôt, il retire au stock une pension que la proposition
  servait moins cher, et la proposition, rapportée au droit calé sur le COR,
  s'en trouve un peu plus chère.

**L'inapte recalé** (le commit qui suit `77cf2da`).

- *Le défaut* (douzième partie, « Un défaut de la même classe ») : à 70 % du
  SMIC de vingt à quarante-huit ans, ses 116 trimestres tous cotisés,
  l'inapte n'avait, né en 1959 et parti en 2021, qu'un salaire annuel moyen
  de 55 % du SMIC de 2021, quand la Cnav en publie 68 %.
- *La source, relue le jour même* : l'étude 2023-014 de la Cnav, tableau 4 —
  19 358 anciens titulaires de l'AAH, 94 trimestres, dont 56 % cotisés, un
  salaire annuel moyen de 56 % du SMIC ; 27 332 autres inaptes, 131
  trimestres, 71 %, 77 % ; ensemble, 116 trimestres, dont quelque 76 cotisés,
  et 68 % du SMIC. Le chômage fait l'essentiel des périodes assimilées des
  hommes anciens de l'AAH ; l'AVPF et la majoration pour enfants, celles des
  femmes ; la maladie vient en fin de carrière chez les autres inaptes
  (graphique 1). L'emploi et le chômage se mêlent à tout âge jusque vers
  cinquante ans, et les années sans report se multiplient ensuite
  (chronogrammes, graphiques 5 à 8).
- *Sa carrière* (`castypes.INAPTE_CNAV`) : à 0,90 SMIC, entré à vingt ans, il
  passe au chômage indemnisé une année sur trois, de vingt et un à
  quarante-huit ans, puis n'a plus d'activité : 76 trimestres cotisés et 40
  assimilés, 116 en tout ; son salaire annuel moyen, né en 1959, fait 68,3 %
  du SMIC de 2021. L'AVPF, la majoration pour enfants et la maladie, qu'il
  n'a pas, se fondent dans son chômage, comme le chômage et l'AVPF de
  l'ex-invalide dans son invalidité. En deux blocs, l'emploi de vingt à
  trente-huit ans puis dix ans de chômage, il lui aurait fallu 0,95 SMIC ;
  les chronogrammes ne montrent pas de bloc. Il part aux mêmes âges.
- *Ce qu'il change à sa pension* : sous le droit en vigueur, son régime
  général reste porté au minimum contributif, et l'Agirc-Arrco seule gagne,
  par le salaire plus haut et les points du chômage indemnisé : sa pension
  passe de 8 171 à 8 668 € par an né en 1965, de 6 %. Le compte du scénario 4
  en perd 9 %, de 5 763 à 5 257 € : dix-neuf années à 0,90 SMIC cotisent
  moins que vingt-neuf à 0,70, et ses dix années de chômage n'y portent que ce
  que l'Unédic verse aux complémentaires.
- *Ce qu'il déplace*, mesuré sur `77cf2da`, la grille d'avant contre celle
  d'après. La dérive du système actuel ne bouge qu'au cinquième chiffre. La
  proposition passe de 8,876 à 8,856 % du PIB en 2030, de 9,751 à 9,729 % en
  2050, de 8,144 à 8,128 % en 2070 ; son solde moyen, de −1,072 à
  −1,052 point ; sa garantie en 2070, de 13,92 à 13,95 Md€ constants ; son
  coefficient de 2070, de 1,0006 à 1,0026, son plus bas, en 2048, de 0,8315 à
  0,8334. Le scénario 2 passe de 4,697 à 4,687 % du PIB en 2070, le
  scénario 4 de 10,359 à 10,335 %. Les pages de simulation suivent les
  coefficients du coût que le paquet leur passe (« vraiment payé »), comme à
  chaque changement de la grille.

**Les tests.**
`test_l_ex_invalide_vit_au_rythme_des_ex_invalides_de_la_cnav` (`test_cout.py`),
vu rouge (0,978, la survie du vingtile, pour 0,930), puis vert ;
`test_la_page_cout_dit_au_rythme_de_qui_chaque_cas_type_survit` (`test_web.py`),
l'ex-invalide dans `nommees`, vu rouge puis vert, comme son test l'annonçait ;
`test_l_ex_invalide_de_la_cnav_part_au_taux_plein_des_l_age_legal`
(`test_moteur.py`), sa mortalité ;
`test_l_inapte_de_la_cnav_part_au_taux_plein_des_l_age_legal`
(`test_moteur.py`), récrit sur le tableau 4 — 76 trimestres d'emploi et 40 de
chômage indemnisé, un salaire annuel moyen de 68 % du SMIC —, vu rouge puis
vert ; `test_pont.py`, l'inapte au portage, au bit près. Aucun cliquet ni
aucune tolérance du coût n'a bougé : `test_cout.py`, `test_facteurs_depense.py`,
`test_affirmations.py`, `test_mortalite_population.py`,
`test_controle_eacr.py` et les confrontations légères passent après chacun
des deux changements.

**Les registres.** `prisme` reste `a_reprendre` au chantier 138.7 : chaque
type de pension de la Cnav vit désormais à son rythme dans la grille ; reste
la forme de la surmortalité, un facteur constant calé à 65 ans, quand Prisme
a des quotients à chaque âge. Au registre des sources, `cnav_inaptitude_2021`
dit la part cotisée, le chômage et l'ex-invalide.

**Ce qui reste**, dans l'ordre :

1. *Le déficit des scénarios 3 et 5* (note « la prémisse du déficit »,
   point 1), une session, en Python seul.
2. *À la session des pages, le coefficient au-dessus de un* (douzième
   partie, point 2) : à 1,0026, la page Coût écrit encore « Les 1,00 de la
   proposition en 2070 disent une marge de 0 % », Cas types « jusqu'à 1,00 en
   2070 » ; il leur faut, au-dessus de un, les décimales que `decimalesSousUn`
   donne au-dessous. L'affirmation `cas_types.coefficient_sous_un` garde sa
   branche, le coefficient s'étant éloigné de un.
3. *La forme de la surmortalité* (onzième partie, point 2), pour les inaptes
   et les ex-invalides.
4. *La limite, à la fin de l'étape* (note « la prémisse du déficit »,
   point 3).
5. *Au propriétaire* : les départs qui suivent l'espérance de vie ; la
   carrière heurtée (étape 19), la grille ayant l'inaptitude et l'invalidité,
   non la carrière longue.
