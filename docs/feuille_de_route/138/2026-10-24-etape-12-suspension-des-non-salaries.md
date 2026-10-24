# Étape 12, treizième partie : la base des non-salariés, suspendue le nombre de mois que le dépassement épuise, et la durée requise des libéraux

**Le 24 octobre 2026, la demande.** Troisième vague du lot du 24 octobre, une
session par tâche, que le propriétaire a demandé de mener sans lui : celle-ci,
le premier point du bloc de l'étape, que la note de la classe du cumul
(`…-la-classe-du-cumul.md`) avait trouvé en chemin. Règle du scénario 1, en
Python puis en JavaScript.

**Ce que dit le droit** (journal de veille,
`2026-10-24-action-138-etape-12-suspension-des-non-salaries.yaml` ; fiche
`cumul_emploi_retraite_et_retraite_progressive`).

- *L'artisan et le commerçant.* Au-delà du seuil, la pension est suspendue
  « pour un nombre de mois égal au rapport entre le montant du dépassement
  constaté et le montant mensuel net de la pension, arrondi à l'entier
  inférieur, sans que ce nombre puisse être inférieur à un » (D. 634-11-5, pour
  les pensions de 2004), et, depuis 2010, « ni supérieur au nombre de mois »
  de l'activité de l'année ; la lettre ministérielle du 8 mars 2010 étend la
  borne aux revenus de 2008 et de 2009 (circulaire RSI 2010/013). La pension
  compte « pour son montant net, c'est-à-dire après déduction des prélèvements
  sociaux » (RSI 2007/109, § 4.2.1) ; la complémentaire est suspendue le même
  nombre de mois (RSI 2009/044, 2010/013).
- *Le libéral.* De même depuis le 17 janvier 2011, sans minimum (D. 643-10-2),
  sous le plafond rapporté à la durée de son affiliation (D. 643-10) ; avant,
  le seuil est « égal, annuellement, au plafond », et « le service de sa pension
  est suspendu » (L. 643-6) sans décret qui en compte les mois. La réduction de
  2017 vaut pour lui aussi « à compter du 1er janvier 2017 » (D. 643-10-2).
- *La durée.* Le cumul intégral à l'âge légal exige « une durée d'assurance
  [...] au moins égale à la limite » de L. 351-1 (L. 161-22, L. 634-6,
  L. 643-6), celle du régime général pour la génération.

**Ce qui est fait.**

- *Dans les deux moteurs* (`droit/cumul.py`, `cumul.js`) : `_suspension`
  compte, par année, les mois que le dépassement épuise, sur les mois de
  l'activité hors du cumul intégral, la pension nette tirée des prélèvements de
  l'année (`_part_nette`, sur `prelevements_historiques.yaml`, que le moteur du
  scénario 1 charge désormais) ; les derniers mois de l'année sont suspendus, les
  autres servis, au motif `hors_des_mois_suspendus`. Les complémentaires
  « pour la même durée » — RCI, CARCDSF, CAVAMAC — suivent ces mois ; celle de
  la CARMF et de la CAVOM de 2020 perd ce que ces mois n'absorbent pas ; celle
  de la CARPV, le dépassement entier, comme avant. Le seuil du libéral d'avant
  février 2011 est le plafond de l'année. La durée du cumul intégral d'une
  carrière tout en points, que le résultat compte nulle, est celle de L. 351-1
  (`duree_du_taux_plein`).
- *Fiches* : `cumul_emploi_retraite_et_retraite_progressive`, ses versions de
  2004 à 2017 et ses écarts, les deux relevés le 24 octobre levés avec celui du
  calendrier du libéral ; `cumul_emploi_retraite_complementaires_des_liberaux`
  et `cumul_emploi_retraite_complementaire_des_independants` mises à jour ;
  treize rédactions citées, le cliquet des textes abaissé à 9 545.
- *Tests* : deux exemples de la circulaire 2010/013 au registre, le premier
  rouge avant le changement (7 920 € suspendus au lieu de 660 €) ; cinq tests
  dans `test_emploi_retraite.py`, dix cas, la pension prêtée comme l'exemple de
  la caisse la pose ; un dans `moteur.test.js` ; posés sur les textes, vus
  rouges ; deux témoins à fabriquer, `cumul_commercant_mois_suspendus_2013` et
  `cumul_medecin_seulement_liberal_2017`. Le RSI entre parmi les éditeurs des
  exemples.

**Mesuré.** Python et JavaScript identiques sur six requêtes de cumul par la
saisie, journaux compris ; aucun des témoins d'avant ne bouge, ni aucune page.
L'artisane partie en 2008, à 4 700 € au-delà de la moitié du plafond en 2010 :
cinq mois suspendus sur douze, quatre si l'on divisait par la pension brute.
Le commerçant de 2013 à 65 % du salaire moyen, d'août 2013 à janvier 2015 : un
mois en 2013, trois en 2014, un en 2015 ; il perd 4 769,77 € au lieu de
17 168,71 €. Le médecin seulement libéral parti en 2016, à 144 trimestres pour
165, à trois fois le salaire moyen : 19 554,88 € au lieu de rien.

**Trouvé en chemin.**

- *Les exemples 6 et 7 de la circulaire 2010/013* ne rapportent pas la moitié
  du plafond à la durée de l'activité, que D. 634-11-2 de 2004 y rapporte : le
  modèle suit le texte.
- *La pension nette* de la caisse compte la majoration pour enfants,
  l'allocation supplémentaire et l'ASPA (RSI 2007/109) ; le modèle, la pension
  de la base au taux plein de la CSG. Déclaré dans la fiche.
- *La date de la suspension*, au mois qui suit la notification du dépassement
  constaté : le modèle place les mois suspendus à la fin de l'année de
  l'activité. Déclaré.

**Pour les pages**, que leur session tient : `cumulEmploiRetraite`
(`pages.js`) n'a pas de phrase pour `plafonnee/hors_des_mois_suspendus`, le
mois d'une année de dépassement où la pension est servie ; il ne dit pas non
plus combien de mois le dépassement suspend. Aucun témoin de page ne le montre.

**Ce qui reste.**

1. Aux pages, ci-dessus, et les phrases que la note de la classe du cumul
   laisse : la session des pages.
2. Une instruction de la CNAVPL ou un exemple d'une section pour D. 643-10-2.
3. Les restes du bloc : la veille du projet de loi de financement pour 2027 ;
   le RCO et le NRCO d'avant 2009 (au propriétaire, action 89) ; la part de base
   de l'ordre de D. 133-4 de 2016 à 2019 (au propriétaire).
