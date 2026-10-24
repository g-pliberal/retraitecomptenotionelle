# L'Agirc-Arrco d'EDIFIS, rejoué au droit de sa date

**La demande**, le 24 octobre 2026 : la quatrième vague du lot que le
propriétaire a demandé ce jour-là, une session par tâche qui se mène sans
lui. Pour l'action 137, le premier reste de son bloc : « l'Agirc-Arrco
d'EDIFIS, ses tranches 1 et 2 et le CET, contre la donnée du dépôt qui dit
la même règle. Rejouez son calcul au droit de sa date, confrontez chaque
écart, et dites de qui est l'erreur. »

**Fait, le 24 octobre 2026 : le calcul rejoué à deux commits ; sur le droit,
le dépôt a raison, et EDIFIS a quatre erreurs ; sur le partage des
cotisations, EDIFIS suit la caisse, et le dépôt s'en écarte de quelques
millièmes de point, un point nul, coupé.**

- *Ce qui a tourné.* EDIFIS (GPL-3.0), cloné à part, à deux commits : `95ef983`
  (11 février 2026), celui que sa ligne du registre confrontait, et ses
  classeurs de 2015 à 2025 ; sa tête, `2fa5bc0` (19 octobre 2026), la
  maquette 2026, refondue sur les fonctions d'« abc », ses barèmes dans
  `data/baremes.RData`, son curseur de 2019 à 2026, ses classeurs retirés. R
  4.3.3 et readxl, installés dans le conteneur. Au premier commit, son code
  lui-même : `read_excel` et `modif_df` (`R/bareme.R`), qui nomment les
  valeurs de la feuille « Barème », puis `cs_sal` et `cs_emp`
  (`R/base.R:328-385`), évalués tels quels ; la retraite complémentaire est
  le total moins les cotisations des autres branches, que la feuille détaille.
  À la tête, `calculVect_PrelevementsSociaux_salaires`, qui sépare la tranche
  1, la tranche 2, la CEG et la CET, sur le dernier barème de chaque année.
  Son salarié est un non-cadre en CDI. La grille : dix-neuf salaires
  mensuels, d'un quart de plafond à douze plafonds, au plafond pile et juste
  au-dessus — 209 points au premier commit, 152 à la tête. Le dépôt : les
  fiches de régime du non-cadre de chaque année (`arrco`, `arrco_tranche_2`,
  `agirc_arrco`), sur leurs tranches, et les contributions d'équilibre
  (`contributions_equilibre_agirc_arrco.yaml`), sur douze mois égaux, son
  plafond annuel valant douze fois le mensuel d'EDIFIS. Les fichiers du rejeu
  sont restés hors du dépôt.
- *Ce qui concorde.* De 2015 à 2018, au centime : l'Arrco, 7,75 % sous le
  plafond et 20,25 % jusqu'à trois plafonds, l'AGFF de 2,00 et 2,20 %,
  partagés à 40 et 60 %, et rien au-delà de trois plafonds pour un non-cadre.
  Depuis 2019, les taux de l'accord du 17 novembre 2017, lu ce jour sur le PDF
  de la fédération : 6,20 et 17 % appelés à 127 %, « arrondis au centième »
  (article 36), 7,87 et 21,59 % ; la CEG de 2,15 et 2,70 % (article 37, 1°) ;
  la CET de 0,35 %, due au-dessus du plafond, sur les tranches 1 et 2
  (article 37, 2°) ; et leurs bornes, un et huit plafonds (article 32). Ses
  sources : jusqu'en 2020, des barèmes qu'il cite par leur numéro (« BSP
  108 » en 2015, « BLS 128 » en 2020), ceux de l'IPP depuis 2021 : de 2021 à
  2025, son accord avec le dépôt est en partie celui de l'IPP.
- *Le partage : le dépôt s'écarte de la caisse.* L'article 38 met 40 % des
  cotisations à la charge du salarié. Le dépôt en prend 40 % exacts
  (`regimes/agirc_arrco.yaml`) : 3,148 % sur la tranche 1, 8,636 % sur la
  tranche 2. La caisse publie ses parts au centième, 3,15 et 4,72 %, 8,64 et
  12,95 %, que portent EDIFIS aux deux commits, modele-social de l'Urssaf, et
  la circulaire de la CAVIMAC que la fiche `arrco_cultes` cite déjà (4,01 %
  à l'assuré, 3,15 + 0,86). L'écart est au dépôt : 0,002 point de moins au
  salarié sur la tranche 1, 0,004 sur la tranche 2, autant de plus à
  l'employeur, 14,42 € par an à huit plafonds en 2026. Le total, les points
  et la pension n'en bougent pas, et une erreur sur le net déplace les deux
  côtés de la comparaison ensemble : un point nul, que la règle de la coupe
  du 14 octobre fait déclarer sans le faire (le registre, `fait_mieux`
  d'EDIFIS, état `coupe`, 138.12). La même classe ailleurs : la fiche
  `arrco_cultes`, dont l'assuré verse 4,008 % au lieu des 4,01 % de la
  circulaire.
- *Ses erreurs.* Au commit `95ef983`, il prélève deux fois la CET sur la
  tranche 2 : ses taux de tranche « Calculé », de un à huit plafonds, portent
  déjà la ligne de la CET — pour l'employeur de 2021 à 2025 (0,47776 en 2021
  de un à trois plafonds, quand 2020 portait 0,47566 au même chômage), pour
  le salarié en 2025 (0,1026 = 0,40 + 9,72 + 0,14 %) —, et `cs_emp` et
  `cs_sal` (`R/base.R:335`, `:374`) la prélèvent encore sur toute la
  rémunération jusqu'à huit plafonds : en 2025, à deux plafonds, 98,91 € de
  trop par an pour l'employeur et 65,94 € pour le salarié, 692,37 et
  461,58 € à huit plafonds et au-delà. La tête ne la compte plus qu'une fois,
  mais a trois erreurs à elle. La CEG du salarié sur la tranche 2 vaut 1,02 %
  au lieu de 1,08 (`tx_sal_AA2_ceg_tr2`, à chaque mois de 2019 à 2026) :
  201,85 € de moins par an à huit plafonds en 2026. La CET est due dès que la
  rémunération atteint le plafond (`x>=pss`), quand l'accord veut qu'elle
  l'« excède » : 168,21 € de trop au plafond pile. Et elle est assise sur
  toute la rémunération (`x* (x>=pss) # oui oui`), au-delà de huit plafonds
  compris : 336,42 € de trop à dix plafonds. Le dépôt et modele-social
  suivent l'accord sur les trois. Avec le partage, ces erreurs expliquent au
  centime l'écart en chacun des 361 points. Avant 2019, la tête ne calcule
  plus rien (« to do : cotisations agirc-arrco avant 2019 ») ; son curseur
  commence en 2019 : une couverture plus étroite, non une erreur.
- *Ce que les tests tiennent* (`tests/test_referents.py`) : ses taux de
  chaque année, aux deux commits, contre ceux que le dépôt prélève, chaque
  part au centième, sauf la CEG de la tête ; douze salaires rejoués, où ce
  qu'il prélève est ce que prélève le dépôt, plus le partage de la caisse et
  ses erreurs, posés à la main depuis l'accord ; et les deux versions que sa
  ligne doit nommer, vues rouges avant le registre. Le tableau de bord compte
  233 écarts au registre, dont 201 chez les modèles confrontés.

**Ce qui reste.** Pour l'action 137 : l'ASPA de Saphir, puis EUROMOD de 2015
à 2025 ; la campagne 2025 de l'EACR, au printemps 2027 ; les `referents` des
fiches, à leur relecture. Au propriétaire, rien à trancher : le partage au
centième, s'il le voulait fait malgré la coupe, est une étape du modèle (les
fiches `agirc_arrco` et `arrco_cultes`, la fiche de paie et ses témoins). Les
erreurs d'EDIFIS se signalent à la DREES, ce qu'une session ne fait pas. Aux
pages, rien : le site ne lit pas le registre.

*Fichiers.* Le registre (ligne `edifis`), le registre des sources
(`drees_edifis`), `tests/test_referents.py`, `docs/etat.md`, la feuille de
route (le bloc « Reprise » de l'action 137), cette note et l'entrée du
journal de veille. Ni fiche, ni règle, ni page. EDIFIS et les fichiers du
rejeu sont restés hors du dépôt.
