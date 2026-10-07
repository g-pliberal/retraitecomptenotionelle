# Étape 3, première partie : la part des reportés en emploi, lue dans les évaluations de 2010

**Reprise, au 7 octobre 2026.** Fait : la part des reportés en emploi, la
moitié par défaut au lieu du plafond de un, lue dans les trois évaluations du
recul de l'âge légal de 2010, dans les deux moteurs ; cinq points du registre
repris. Reste, une session par point : la décomposition dépendance ×
couverture × prestation, confrontée à l'Ageing Report de 2024 ; le levier de
l'âge, avec le « tax gap » et le « pension gap » du COR ; la CSG effective ;
les contrôles d'Ancetre et de l'EACR ; les retraités par régime et la
pondération par les masses, avec l'action 147. Commencer par la
décomposition, dont le modèle a déjà les têtes et la pension relative.
Détail : plus bas, « Ce qui reste ».

**Le 7 octobre 2026, la demande.** Le propriétaire : « 138.3 ». L'étape est
vaste — sept chantiers, vingt-neuf points du registre — ; cette session en
mène un, le plus sûr : le plafond que la page Coût déclarait depuis le
24 septembre, « tous ceux que le report fait attendre sont en emploi », et dont
`config.py` disait qu'« une valeur retenue devra y avoir été lue » dans les
évaluations de la réforme de 2010.

**Ce que disent les évaluations, lues le jour même.** Le recul de l'âge légal
de 60 à 62 ans en a trois qui suivent ce que deviennent ceux qu'il fait
attendre.

- *IPP, rapport n° 61, novembre 2025* (Aubert, Bozio, Pedrono, Tô ; § 5.2.1
  et conclusion), sur l'échantillon interrégimes de cotisants de la DREES,
  générations 1950 et 1954, assurés qui ont travaillé entre 50 et 55 ans et
  cotisé surtout au régime général, hors carrières longues (52 % des
  générations) : 60 % reportent leur départ ; l'emploi gagne jusqu'à
  30 points entre 60 et 61 ans et demi, le chômage indemnisé 15, l'inactivité
  18 ; « parmi les individus affectés par la réforme, la moitié passe plus de
  temps en emploi, et environ un quart reçoit une allocation chômage ». Chez
  ceux que l'élargissement des carrières longues a rendus éligibles, « deux
  tiers prolongent leur durée d'activité ».
- *Rabaté et Rochut, document n° 11 de la séance du COR du 19 octobre 2016*
  (publié en 2020 au Journal of Pension Economics and Finance), sur
  l'échantillon au 1/20e de la Cnav, générations 1951 à 1953, hors carrières
  longues : à 60 ans, la retraite perd 40,2 points ; l'emploi en gagne 13,5 au
  régime général et 1,7 ailleurs, le chômage 13,3, l'invalidité 5,9, la
  maladie 1,4, l'inactivité 4,4 (tableau 7) — « un tiers en emploi, un tiers
  au chômage, un cinquième en invalidité ou en maladie », 37 % en emploi.
- *Insee Analyses n° 30, janvier 2017* (Dubois et Koubi), sur l'enquête
  Emploi : salariés du privé de 60 ans, générations 1949 à 1952, hors départs
  anticipés, allocataires de l'AAH, pensionnés d'invalidité, et qui a fini ses
  études avant 18 ans (figure 3). La retraite perd 27 points chez les hommes,
  dont 14 d'emploi à temps complet, 3 à temps partiel, 7 de chômage et 3
  d'inactivité ; 22 chez les femmes, dont 9, 7, 6 et 0. Soit 63 % et 73 % en
  emploi, les chiffres que le registre citait (`simulateur_aurain`), sur un
  champ qui écarte ceux qui n'auraient guère travaillé.

La convention du simulateur du COR (2016) est 0,5. L'enquête Emploi que le
COR publie (rapport de juin 2026, figure 4.3), 72 % des non-retraités en
emploi à 60 ans, est un stock, et non l'effet d'un report.

**Ce qui est retenu, et pourquoi.** La moitié : la mesure de l'IPP, la plus
récente, sur l'échantillon le plus large — tous régimes, invalides compris —,
et la convention du COR. L'INSEE la majore par son champ ; la Cnav, qui voit
l'invalidité et la maladie, la trouve plus basse, à 60 ans. Un seul
paramètre : le dépôt ne sépare ni les sexes ni les régimes de ceux qu'il fait
attendre. Les trois mesures portent sur le privé et sur 60-62 ans ; la
proposition fait attendre jusqu'à 65 ans, et un fonctionnaire garde son
emploi en attendant. La partie 4 des limites le dit.

**Ce qui est fait.**

- `Parametres.part_reportes_en_emploi` passe de 1 à 0,5, et son jumeau de
  `config.js` ; le commentaire cite les trois évaluations. `cout.js` et
  `pages.js` ne prennent plus un quand le paramètre manque, mais le défaut.
- La page Coût cite la source à cette valeur, et à elle seule : « C'est ce
  qu'a fait le recul de l'âge légal de 60 à 62 ans, en 2010 […] (IPP, rapport
  n° 61, 2025). Tous en emploi, ce serait un plafond. » Elle ne dit plus que
  l'âge légal retient au travail tous ceux qui seraient partis plus tôt.
- Les tests : le plafond devient la variante (`cout_tous_en_emploi`), contre
  laquelle l'assiette du défaut s'élargit deux fois moins ; les tests du
  portage la refont en JavaScript, et un test garde la valeur dans les deux
  moteurs.
- La prose : la partie 4 des limites dit la part, ses sources et ce qu'elle
  déplace ; le README ne dit plus que l'âge légal fait cotiser tous ceux qu'il
  fait attendre, ni que le scénario 6 n'est à l'équilibre qu'au lendemain de
  la bascule : il ne l'est plus aucune année de l'horizon, quand il l'était de
  2028 à 2030, et en 2070.
- Ce que le nouveau profil a montré sur le site : la proposition finit sous
  un, à 0,9997 en 2070, et la page écrivait « 1,00 » d'un facteur qu'elle
  disait inférieur à un, et « un manque de 0 % » ; elle prend désormais assez
  de décimales (`decimalesSousUn`), comme elle le faisait du plus bas. La
  phrase « Un coefficient inférieur à un est un manque », que Cas types rend de
  nouveau, retrouve son entrée au catalogue des affirmations, retirée le
  23 septembre. Et le contrôle du coefficient non appliqué se vérifie l'année
  où il s'écarte le plus de un, non plus à l'horizon, désormais presque à
  l'équilibre.
- Le registre : quatre points repris au chantier 138.3 (`maquette_globale_cor`,
  `simulateur_cor`, `aphrodite`, `simulateur_aurain`), et un que l'étape 9 de
  l'action 147 avait fait sans le dire (`canopee`, les retraités projetés de
  la CNRACL).

**Ce que ça déplace**, la proposition seule, sur la page Coût : son solde
moyen 2026-2070 passe de −0,75 à −0,90 point de PIB (−1,13 pour le système
actuel), sa dette de 2070 de 49 à 59 % du PIB (66 %), son coefficient
d'équilibre de 2070 de 1,015 à 1,000, au plus bas 0,85 en 2049 au lieu de 0,86
en 2051. Sa dépense recule un peu, 8,2 % du PIB en 2070 au lieu de 8,4 : qui
attend sans activité liquide un compte plus petit. Les cinq autres systèmes ne
bougent pas, ni le simulateur, où chacun prolonge sa propre situation.

**Ce qui reste**, de l'étape 3 ; chaque point cite ceux du registre au
chantier 138.3 (`id` du modèle).

1. *La décomposition de l'Ageing Report* : dépendance (65 ans et plus sur
   20-64 ans), couverture (pensionnés sur 65 ans et plus), prestation (pension
   moyenne sur salaire moyen), marché du travail. La fiche France de 2024 :
   14,4 % du PIB en 2022, 13,6 % en 2070, dont dépendance +6,0 points,
   couverture −2,2, prestation −3,4 (tableaux 7, 9 et 10) ; le flux des
   pensions nouvelles (tableau 14) ; la dépense nette d'impôts (tableau 7). Le
   modèle a déjà, année par année, les têtes, la pension relative et la
   dépendance (`AvenirAnnuel`, `Avenir.decomposition`, action 147) ; il lui
   manque la couverture, qu'il suppose constante (`cout.py`, limite 2), et la
   confrontation. `ageing_report` (4 points), `modello_rgs`, `simulateur_cor`
   (l'équation de bouclage), `maquette_globale_cor` (la décomposition par
   groupe, que l'action 147 confronte déjà : à relire).
2. *Le levier de l'âge, le « tax gap » et le « pension gap »* : ce qui
   équilibrerait le système, que le COR chiffre (tableau 2.11, figure 2.24 :
   pensions de −1,4 à −8,6 %, prélèvement de +0,4 à +2,8 points, ou départ à
   67,6 ans en 2070) ; le dépôt a le coefficient et les points d'assiette,
   pas l'âge. `maquette_globale_cor`, `retraites_scherrer`, `trajectoire`
   (l'âge de départ que le COR projette).
3. *La CSG effective* : la page Coût retire 9,1 % à la masse, quand la CCSS
   de mai 2024 (tableau 3) compte 23,7 Md€ de CSG sur les retraites en 2023,
   6,3 % des masses de la DREES ; la table de l'EACR par taux de CSG.
   `taxipp`, `legiretraite`.
4. *Les contrôles d'Ancetre et de l'EACR* : la pension par régime principal,
   fin 2024 (rapport du COR de 2026, tableau 3.2) ; les tables E, H, B et C de
   l'EACR. `ancetre`, `legiretraite`, `pablo` (le biais de l'individu moyen).
5. *Les retraités par régime et la pondération par les masses* : l'action
   147 a projeté la fonction publique et les régimes qui se ferment ; restent
   l'Ircantec, la CNRACL par catégorie, et peser par les masses plutôt que par
   les têtes, ce qui ôterait le double compte des polypensionnés. À mener avec
   ce qui reste de l'action 147 (« le privé au milieu de la période, les
   polypensionnés »). `maquette_globale_cor`, `canopee`, `mistral`.
6. *Le reste* : le recours à l'ASPA calé sur les allocataires de la DREES, et
   selon la situation conjugale (`taxipp`, `prisme`) ; les rémunérations
   publiques sur les hypothèses de la Direction du budget
   (`maquette_globale_cor`) ; l'engagement de l'État que calcule Pablo,
   1 573 Md€ fin 2024 (`pablo`) ; un univers sans la réforme de 2023, pour
   retrouver les chiffrages de Prisme et de Pablo (`prisme`, `pablo`).
