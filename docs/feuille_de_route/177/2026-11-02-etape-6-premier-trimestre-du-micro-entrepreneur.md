# Étape 6 : le premier trimestre du micro-entrepreneur en 2014 et en 2015, aux deux seuils de la grille de la caisse

**Le 2 novembre 2026, ce qui est fait.** La question se tranche aux textes,
et ses deux écarts se séparent. En 2015, la divergence que l'étape 2 de
l'action 175 voyait entre deux sources de la caisse n'en était pas une : le
modèle se corrige, dans les deux moteurs. L'assuré qui ne relève pas de la
maladie du RSI reste une limite : rien, dans la saisie, ne le dit.

1. *La lecture.* `python scripts/veille_droit.py`, l'index LEGI mis à jour
   au 2 novembre 2026, `python scripts/textes.py --inscrire` : aucune
   rédaction nouvelle. Trois pièces de la caisse, sur son site :
   l'« Info-doc RSI » « Micro-entrepreneurs - Validation de trimestres
   retraite », mis à jour le 16 avril 2019, que joint le barème « Chiffre
   d'affaire des micro-entrepreneurs validant un trimestre » ; les circulaires
   RSI n° 2015/007 du 9 mars 2015 et n° 2016/010 du 15 juin 2016. Dans
   l'index LEGI, D. 131-6-4 (LEGIARTI000030034478, en 2015 : le montant
   minimal de L. 133-6-8-2, « calculé sur la base de 300 heures ») et
   D. 131-6-5 (LEGIARTI000023565887, de 2011 à 2015 : le solde du forfait à
   la maladie d'abord, à la vieillesse de base en dernier).
   - *La circulaire n° 2016/010, point 1.* Après le barème « en principe »
     de 2014, le trimestre à 150 heures, 4 930 € de ventes, « lorsque la
     compensation est nécessaire à la validation du premier trimestre
     d'assurance », 6 573 € ; « Ce dispositif complexe, à deux niveaux de
     validation du premier trimestre d'assurance, est toutefois transitoire.
     Il est applicable en 2014 et 2015 et disparaît dès 2016 ». Les « AE
     prestataires santé au RSI » valident le premier à 200 heures, leur
     forfait étant « entièrement imputé sur le risque maladie » ; « Les AE
     non prestataires santé au RSI, les AE prestataires santé au RSI mais qui
     sont au RSA socle », à 150 heures.
   - *La circulaire n° 2015/007, point 2.* La compensation, sur l'assiette
     minimale de 300 SMIC horaires, « permettra ainsi la validation de deux
     trimestres d'assurance ». Elle ne dit rien de ce qui valide en deçà : le
     « rien en deçà » que le test lui prêtait n'y est pas.
   - *La grille.* En 2015, le premier trimestre à « 9 621 € si prestataires
     santé » et « 6 636 € si non prestataires santé » de ventes, à 5 592 et
     3 854 € de services, et aux prestations de service BNC « Pas de
     validation de trimestres sans déclenchement de la compensation » ; les
     trois suivants, ceux que le modèle refaisait déjà. En 2014, « 2 barèmes
     peuvent s'appliquer. Pour savoir lequel prendre en compte, se référer à
     la C 2016/010 ».
2. *Ce qui se tranche.* La grille de 2015 est le double seuil de la
   circulaire n° 2016/010, que la n° 2015/007 ne contredit pas : sous les
   300 heures, le forfait dépasse la maladie avant que la compensation ne
   joue, et valide seul un trimestre à la vente et aux services. Aucun texte
   lu ne dit comment la caisse refait ces seuils, de l'ordre de D. 131-6-5 et
   des cotisations dues : le modèle les prend tels qu'elle les publie, comme
   ceux de 2017 à 2019.
3. *Le premier écart, corrigé dans les deux moteurs* (`f6f7285`).
   `legislation/micro_social.yaml`, `seuils` : les lignes de 2015 des ventes
   et des services, que `charger_seuils_micro` abat, que le paquet porte
   (`seuils_micro`), et que comptent `trimestres_aux_seuils_micro` et son
   jumeau `trimestresAuxSeuilsMicro` ; le libéral garde la compensation.
   Vus rouges : `test_la_compensation_de_l_etat_de_2009_a_2015` (9 621 € de
   ventes, 5 592 € de services : un trimestre),
   `test_le_modele_valide_les_trimestres_de_la_grille_de_la_compensation`,
   ses deux entrées de 2015 ôtées d'`ECARTS_A_LA_GRILLE`, et le même cas au
   portage (`moteur.test.js`) ; `test_les_taux_des_micro_entrepreneurs_sont_ceux_de_la_caisse`
   lit les lignes de 2015 à la grille.
4. *Le second écart, une limite.* `docs/limites/3-systeme-actuel.md`,
   « micro-entrepreneur de 2014 et de 2015 » ;
   `test_hors_de_la_maladie_du_rsi_le_premier_trimestre_est_une_limite`
   garde les seuils de la grille, et rougira le jour où le modèle les
   servira. Le champ `dispense` de la saisie dit le RSA, sans le RSA socle
   que la circulaire nomme : il ne sert pas. Fiche `micro_social_abattement`
   : effet, lectures, approximations, dix au lieu de neuf.

**Mesuré.** Ni témoin ni agrégat ne bouge. En 2015, 9 621 € de ventes
valident un trimestre au lieu de rien, 5 592 € de services aussi ; l'assuré
hors de la maladie du RSI en perd un au plus par année, deux en tout. Tous
ces seuils sont sous le plancher de la saisie, un dixième du salaire moyen
(de 0,044 à 0,087 fois le salaire moyen de l'année) : le site ne les atteint
pas, seul le modèle.

**Ce qui reste.**

1. *La question au propriétaire* : une saisie de plus, avec la session du
   site, pour l'assuré hors de la maladie du RSI en 2014 et en 2015 ?
   Proposé : non, la limite reste, la saisie ne descendant pas si bas.
2. En 2015, l'année dont le forfait seul valide le premier trimestre ne porte
   rien au revenu annuel moyen, quand la caisse y porte ce que sa part de
   base a versé (une approximation de la fiche).
3. Le plancher de 2009 (`ECARTS_A_LA_GRILLE`), que la grille ignore et que
   la circulaire n° 2009/024 pose : hors de l'étape, la circulaire fait foi.
4. Le registre de la Cnav : les deux circulaires, lues ici, restent `a_lire`
   dans `references.csv`, où aucune référence n'est encore rangée ; l'étape
   6 de l'action 175, qui lit les références sans thème, les rangera.

**L'étape est faite.** La suite : l'étape 7 revient à la session du site ;
l'étape 8, les non-salariés de Mayotte, au modèle.
