# Action 194 : l'Agirc-Arrco avant l'âge légal, d'avril 1983 à mars 2023, à l'âge seul

Action 194, suite de l'Ircantec servie avant le régime général
(`2026-11-21-ircantec-sans-la-base.md`). La fiche
`coefficients_anticipation_agirc_arrco` déclarait l'écart en approximation,
« non mesuré, sans doute nul ».

L'écart : du 1er avril 1983 au 15 mars 2023, l'Agirc et l'Arrco n'ouvrent la
table des trimestres manquants, et l'exonération par la durée du taux plein,
qu'à l'âge légal. Jusqu'au 30 juin 2011, aux participants « âgés de 60 à
65 ans » (arrêté du 21 mars 1983, son résumé ; accord du 23 décembre 1996,
article 2 ; accord du 13 novembre 2003, article 1er, prorogé jusqu'au 30 juin
2011), et avant soixante ans à la seule carrière longue (même article). Puis
la table, à ceux « ayant un âge compris entre celui visé à l'article
L. 161-17-2 [...] et celui visé au 1° de l'article L. 351-8 » (annexes E et V
de l'accord du 18 mars 2011, articles 2 et 4 ; accord du 17 novembre 2017,
article 85, 3) ; l'exonération, de 2019 à mars 2023, à qui a « obtenu » la
pension du régime général au taux plein (article 84, 3), sans borne d'âge,
mais que la durée ne donne pas avant l'âge légal. L'avenant n° 15 du 16 mars
2023 ouvre la table à ceux « ayant un âge inférieur à » l'âge du 1° de
L. 351-8. Le modèle prenait la table et l'exonération à tout âge. L'écart
touche la liquidation d'un départ déclaré avant l'âge légal, que le modèle
chiffre sans que le droit l'ouvre.

La correction, dans le portage :

- la fiche porte `trimestres_manquants_des_l_age_legal`, vrai aux versions
  du 1er avril 1983 au 15 mars 2023, de `structure_financiere` à
  `regime_unifie`, faux à `avenant_15` ; l'approximation qui déclarait
  l'écart est retirée ;
- `liquider.abattementPoints` le lit comme la seconde table de l'Ircantec :
  avant l'âge légal, hors carrière longue, l'âge seul fixe le coefficient ;
- la pension provisoire de la retraite progressive en est tenue hors
  (`provisoire`, que `liquidation.js` passe à `liquiderChaqueRegime` pour
  une demande provisoire) : elle a sa règle, un « coefficient d'anticipation
  spécifique temporaire, tenant compte de la durée d'assurance », « le cas
  échéant » (accord de 2017, articles 85, 2, et 88 ; annexes E et V de 2011,
  article 3). Au taux plein, aucun ; sous lui, le barème temporaire de la
  circulaire, que le modèle ne porte pas : la table des trimestres en tient
  lieu, sous l'approximation que la fiche `retraite_progressive` déclare ;
- `scenario-actuel.resultatDesDeparts` : quand l'Ircantec seule part au
  départ déclaré, le résumé du départ (l'âge et le motif de l'ouverture, la
  durée requise, le taux) décrivait cette pension, qui n'a ni âge ni durée à
  elle ; il décrit désormais le premier départ qui suit et sert un régime de
  base. Défaut de l'étape de l'Ircantec, trouvé ici : né en janvier 1966,
  contractuel, parti à cinquante-sept ans en février 2023, l'âge de
  l'ouverture que la page lui opposait était vide ; il est de 63 ans et
  3 mois, l'âge légal.

L'Ircantec, relue pour la même question : l'article 16, III, de l'arrêté du
30 décembre 1970 (rédactions de 2011, 2018 et 2023) ne fait de la pension
provisoire de la retraite progressive qu'une « liquidation provisoire » sous
le I et le II, sans règle à elle : l'âge seul avant l'âge légal, publié le
21 novembre, tient. Contractuelle en retraite progressive en 2020 : 0,6575.
La pratique de la caisse n'est pas lue.

Relecture sous Opus, qui a demandé trois reprises de la première version :
la pension provisoire de la retraite progressive, qu'elle mettait à l'âge
seul, 0,6575 à vie, même au taux plein ; l'article de l'exonération de 2019 à
2023, attribuée à l'article 85, 3, qui ne règle que la table ; la borne de
soixante ans d'avant juillet 2011, que la première version ne posait pas.

Tests, vus rouges :

- `test_la_pension_provisoire_de_l_agirc_arrco_a_sa_regle`
  (`tests/test_retraite_progressive.py`), les cas de la relecture : née en
  janvier 1956, deux enfants, retraite progressive à soixante ans et trois
  mois en mai 2016, 166 trimestres sur 166 : ses points entiers ; née en
  1960, de même en mai 2020, 167 sur 167 ; sans enfant, 161 sur 167 : 0,94
  par la table. Vus rouges à 0,6575 sous la première version ;
- `test_avant_juillet_2011_la_duree_n_exonere_la_complementaire_qu_a_soixante_ans`
  (`tests/test_simulateur.py`) : né en janvier 1950, parti à cinquante-huit
  ans en 2008, 0,64 avec la durée comme sans elle (0,43 à cinquante-cinq ans,
  plus 0,0175 par trimestre : accord Arrco du 25 avril 1996, article 10) ;
  1 sous la carrière longue ; à soixante ans et six mois en 2010, la durée
  l'exonère. Vu rouge à 1 ;
- `test_le_resume_du_depart_est_celui_de_la_base` (`tests/test_ircantec.py`),
  vu rouge sur le cas de 1966.

Deux tests attendaient l'ancienne règle, et se récrivent d'après le texte :
`test_l_abattement_de_la_complementaire_n_est_pas_celui_de_la_base`
(`tests/test_simulateur.py`) et
`test_une_regle_du_droit_se_demande_par_son_module_et_son_nom`
(`tests/test_facade.py`) : à cinquante-sept ans en 2022, avec la durée, 0,43,
et 1 sous la carrière longue. `test_agirc_arrco_au_droit.py` et
`test_exonerations_agirc_arrco.py` lisent le nouveau paramètre, depuis 1983 ;
le contrat de `abattement_points` (`tests/contrats_de_la_facade.py`) prend
`provisoire`.

Ce qui bouge : cinq témoins de simulation sur 933, les `reversion_revisee_*`
(née en 1955, départ déclaré à soixante ans en 2015, que le droit n'ouvre
pas) : la complémentaire prend le coefficient de l'âge, 0,64, et non plus
celui de dix trimestres manquants, 0,90 ; la pension baisse de 7,91 % aux
scénarios 1, 3 et 5, avec la réversion qui en dépend. La retraite
progressive de 2016 (`progressive_liberale_puis_salariee_2016`) ne bouge
plus. La page des avantages compte désormais le coefficient de l'âge que la
carrière longue épargne à la complémentaire : 163 millions d'euros en 2013,
1 618 millions en 2024 ; le total de ce que personne n'a cotisé passe, en
2024, de 98,1 à 99,7 milliards d'euros (23,0 à 23,4 % de la dépense). De 2004
à 2012, la ligne reste nulle : aucun cas type de la grille ne part en
carrière longue avant la génération 1955, le plus précoce entrant à dix-huit
ans, quand la carrière longue de 2003 demandait d'avoir commencé avant dix-sept
ans. Ces départs ne sont pas mesurés : une limite de la grille, non de la
règle. Six rendus de page, celle des avantages et cinq du coût ; le paquet.

Reste :

- la présomption, que le propriétaire décide : le modèle sert toujours
  l'Agirc-Arrco avec la pension de base (approximation de
  `liquidation_regime_par_regime`), quand l'article 84, 2 la laisse demander
  dix ans avant l'âge du 1° de L. 351-8 ; ou bien elle se présume demandée au
  départ déclaré, comme l'Ircantec, ou bien elle attend la base, sauf demande
  expresse, et l'Ircantec avec elle ;
- le contrefactuel de la carrière longue (`avantages.py`) compte la base
  liquidée : depuis le 16 mars 2023, la durée y exonère encore la
  complémentaire, quand la circulaire 2020-02-DRJ (fiche 3, I.1.3.3)
  subordonne la table des trimestres à la liquidation de la base. La ligne
  sous-estime peut-être les départs d'après ;
- le barème temporaire de la pension provisoire de la retraite progressive,
  et la pratique de l'Ircantec en retraite progressive ;
- la relecture de la règle sur Opus, Fable manquant de quota, à la demande du
  propriétaire.
