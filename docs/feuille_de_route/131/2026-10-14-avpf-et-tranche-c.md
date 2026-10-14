# L'AVPF de 1972 à 1982, et la tranche C de l'Agirc à travers la fusion de 2019

**Le 14 octobre 2026 : deux restes de l'action, chacun en son commit.**

- *L'AVPF des périodes de 1972 à 1982 du régime général*, trouvée en chemin le
  13 octobre. L'assurance vieillesse des mères au foyer porte un salaire au
  compte depuis le 1er juillet 1972 (loi n° 72-8 ; décret n° 73-88, article 3,
  lu dans l'index LEGI : une assiette de « 173,33 fois » le SMIC du 1er juillet
  précédent), mais les six périodes de 1972 à 1982 ne nommaient pas `avpf`
  parmi leurs avantages : une pension liquidée avant le 1er avril 1983 perdait
  ces salaires dans son salaire annuel moyen. Elles la nomment. Aucun témoin ne
  bouge, aucun ne liquidant si tôt avec de l'AVPF ; un test et son jumeau
  (`test_l_avpf_compte_avant_avril_1983`) la montrent, 7,08 € par an de plus à
  une mère née en 1918, partie en janvier 1983. Le moteur lit l'assiette au
  barème de la Cnav, date par date : les 173,33 heures du décret de 1973,
  contre 169 depuis, n'y changent rien. Fiche `avpf`.
- *La tranche C de l'Agirc d'avant 2016, à travers la fusion de 2019.* Portée le
  28 septembre de l'acquisition à la liquidation, elle n'était montrée que
  pour un départ de 2017. L'accord de 2017, relu dans sa version de 2019,
  convertit les points Agirc au quotient des valeurs de service du 31 décembre
  2018 (article 52) et nomme encore, après la fusion, les points de tranche C
  d'avant 2016 « dans l'ancien régime AGIRC » (article 102). Le moteur les sert
  à la valeur convertie et leur garde le coefficient pour âge : un cadre de
  1960 parti à 62 ans en 2022 a ses 77 442 points de tranche C à 0,78. Rien à
  corriger ; un témoin né pour la règle (`tranche_c_apres_la_fusion`) et un cas
  de plus au test de la règle le tiennent. Fiche
  `coefficients_anticipation_agirc_arrco`, qui reste `approchee`.
- *Les lectures*, au journal de veille
  (`2026-10-14-action-131-avpf-et-tranche-c.yaml`).
- *Trouvé en chemin.* Les coefficients de solidarité de l'Agirc-Arrco, 10 % de
  moins pendant trois ans aux nés depuis 1957 partis au taux plein de 2019 à
  novembre 2023 (ANI du 30 octobre 2015), sont décrits par la fiche du régime
  et nommés parmi ses avantages, mais aucun calcul ne les sert, et aucune
  fiche de règle ne les porte : une règle du scénario 1 à écrire, hors de
  cette action.
- *Pour les pages* : rien.

Reste de l'action : `retraite_proportionnelle_msa`, le maximum M et la série de
l'AVTS (zone des données) ; `cotisation_par_classes_liberales`, les grilles ;
de `coefficients_anticipation_agirc_arrco`, le report sans abattement de
l'article 102, l'âge de référence de 2011 à 2018 et les textes d'avant 2003 ;
les restes de `decote_avant_1983`, des artisans et commerçants, de
`pension_non_salaries_agricoles_2026` et de R. 173-4-3.
