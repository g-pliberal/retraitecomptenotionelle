# Étape 12, douzième partie : la classe du cumul — l'Ircantec, la RCO agricole, les sections libérales — et le versement forfaitaire de la base des indépendants

**Le 24 octobre 2026, la demande.** Lot du 24 octobre : onze sessions en
parallèle, une tâche chacune, que le propriétaire a demandé de mener sans lui ;
celle-ci, le point 5 du « Ce qui reste » de la note du 23 octobre
(`…-cumul-et-versement-unique-du-rci.md`), « la classe » : les sections
libérales en cumul, l'Ircantec, la RCO agricole, et le versement forfaitaire de
la base des indépendants. Règle du scénario 1, en Python puis en JavaScript.

**Ce que dit le droit** (journal de veille,
`2026-10-24-action-138-etape-12-la-classe-du-cumul.yaml` ; fiches
`versement_forfaitaire_unique`, `cumul_emploi_retraite_ircantec`,
`cumul_emploi_retraite_rco_agricole`,
`cumul_emploi_retraite_complementaires_des_liberaux`).

- *Le versement de la base.* L. 634-2 calcule, liquide et sert la pension des
  artisans et des commerçants « dans les conditions définies [...] aux articles
  [...] L. 351-7 à L. 351-10 », dont le versement de L. 351-9, depuis le code de
  1985 ; « Pour l'application des dispositions de l'article R. 351-26, sont
  totalisés » la pension des périodes d'après 1972 et l'avantage de celles
  d'avant (D. 634-9, de 1990 au 25 mai 2020), auquel le décret n° 73-937,
  article 8, applique aussi R. 351-26.
- *L'Ircantec.* L'article 14 de l'arrêté du 30 décembre 1970 : « La reprise
  d'activité est autorisée dans les conditions prévues à l'article L. 161-22 »
  (2004), le cumul avec « une activité professionnelle entraînant un
  assujettissement à l'IRCANTEC » (2011), « à l'exception de son troisième
  alinéa » depuis le 19 décembre 2020 — l'alinéa qui réduit « chacune des
  pensions » ; la caisse : « l'Ircantec continue de vous verser la totalité ».
- *La RCO agricole.* « Les dispositions des articles L. 732-39 et L. 732-40 sont
  applicables à la pension de retraite complémentaire obligatoire » (D. 732-157,
  depuis 2003).
- *Les sections libérales*, chacune dans ses statuts, que l'index JORF garde :
  la CARCDSF suspend la complémentaire dès la reprise de la profession (2007),
  puis « pour la même durée » que la base (2011), comme la CAVAMAC (2011), qui
  la règle en 2026 « dans les mêmes conditions que pour le régime de base » ; la
  CARMF la suspend « conjointement à celui des autres pensions [...] et à
  concurrence du montant du dépassement » (2011) ; la CARPV, « pendant la durée
  qui aurait procuré [...] un montant brut d'allocations [...] égal au montant du
  dépassement » (2011), plus rien depuis 2022 ; la CAVOM, de ce que la base
  n'absorbe pas (2020), du dépassement entier (2026) ; la CPRN : « Il est
  incompatible avec l'exercice de la profession de notaire libéral » (2017).
  Rien de lu ne suspend celle de la CARPIMKO, de la CAVEC, de la CAVP, de la
  CIPAV.
- *2027.* L. 161-22, III, A, vise toute pension « de base ou complémentaire »,
  la réduction « par priorité » sur les pensions de base ; la CARCDSF et la
  CARMF l'écrivent dans leurs règlements de 2026.

**Ce qui est fait.**

- *Le versement de la base, dans les deux moteurs* (`groupes_du_versement`,
  `groupesDuVersement`, `verser_en_capital`) : la pension de CANCAVA,
  d'ORGANIC et du RSI, depuis 1985, avec ses avantages d'avant 1973, comparée
  ensemble au seuil, remplacée par quinze annuités ; l'article 40 du RCI joue
  désormais par elle.
- *Le cumul, dans les deux moteurs* (`droit/cumul.py`, `cumul.js`) : l'Ircantec
  suit la règle de la base du salarié pour l'activité qui y cotise, de 2004 à
  2020, puis reste entière au-delà du plafond ; la RCO agricole prend le statut
  de la base de l'exploitant, « règle non lue » ; la complémentaire des sections
  suit la table de leurs statuts (`REGLES_DES_SECTIONS`, que
  `test_les_regles_des_sections_sont_celles_de_leur_fiche` confronte à la
  fiche) ; pour la première pension de 2027, le RCI, l'Ircantec, la RCO et les
  sections se partagent au prorata ce que les bases n'absorbent pas
  (`_complementaire_2027`).
- *Fiches* : trois neuves, citées ci-dessus ; `versement_forfaitaire_unique`
  et `cumul_emploi_retraite_et_retraite_progressive` mises à jour ; le cliquet
  des textes abaissé à 9 568 ; vingt rédactions du décret n° 2003-1277, que la
  fiche de la RCO cite, inscrites « à examiner ».
- *Tests* : quatre dans `test_versements_uniques.py` et trois cas de plus à sa
  confrontation des moteurs ; quatorze dans `test_emploi_retraite.py`, dix-neuf
  cas ; un dans `moteur.test.js` ; posés sur les textes, vus rouges ; trois
  témoins, `cumul_contractuelle_ircantec_2020`, `cumul_medecin_carmf_2017` et
  `cumul_notaire_cprn_2022`.

**Mesuré.** Python et JavaScript au bit près sur les cas et sur les témoins de
cumul. Aucun des 892 témoins d'avant ne bouge, ni aucune page. Le versement :
la commerçante d'une année en 1980, partie à 65 ans en 2010, a 138,00 € par an
d'ORGANIC, sous le seuil de 147,83 € : 2 070,00 € en une fois ; l'artisane de
1972 et de 1980, 83,48 € et 8,52 € d'avant 1973 : 1 252,20 € et 127,80 € ; celle
de 1971 et de 1980, 38,56 € et 283,44 € : rien, ensemble au-dessus du seuil.
Le cumul : la contractuelle partie en 2020 perd son Ircantec de 493,60 € par
mois d'août à décembre 2020, et la garde depuis ; le médecin parti en 2016, à
trois fois le salaire moyen, sa complémentaire de 481,09 € ; le notaire libéral
de 2022 n'a pas sa complémentaire de 367,18 €, sous le seuil.

**Trouvé en chemin.**

- *La suspension de la base des non-salariés* : D. 634-11-5 (pensions de 2004)
  et D. 643-10-2 (depuis le 17 janvier 2011) ne suspendent la pension que « pour
  un nombre de mois égal au rapport entre le montant du dépassement constaté et
  le montant mensuel net de la pension, arrondi à l'entier inférieur » ; le
  modèle la suspend chaque mois d'activité au-delà du seuil. La complémentaire
  du RCI de 2009, de la CARCDSF et de la CAVAMAC, « pour la même durée », hérite
  de l'écart. Déclaré dans `cumul_emploi_retraite_et_retraite_progressive`.
- *La durée requise d'une carrière seulement libérale* : le résultat en compte
  zéro trimestre, et le modèle la laisse cumuler entièrement dès l'âge légal,
  quand L. 643-6 exige la durée de L. 351-1. Les tests des sections la
  contournent par quatre ans de salariat. Déclaré dans la même fiche.
- *2027* : L. 161-22, III, A, vise aussi l'Agirc-Arrco, que le modèle laisse à
  sa règle, et les autres complémentaires — avocats, navigants,
  artistes-auteurs, prestations supplémentaires, RAFP —, qu'il sert entières.
- *L'élu local de l'Ircantec*, dont l'allocation était suspendue pendant un
  nouveau mandat jusqu'au 1er août 2026 : son activité n'a pas de règle lue.

**Pour les pages**, que leur session tient.

- `cumulEmploiRetraite` (`pages.js`) n'a pas de phrase pour `non_due/notaire_liberal`
  ni pour `suspendue/reprise`, qui peuvent être les plus touchées : pour le
  notaire libéral sous le seuil (témoin `cumul_notaire_cprn_2022`), la page
  dirait, par sa phrase par défaut, « votre pension est servie entière » quand
  sa complémentaire n'est pas due. Ni pour `plafonnee/sans_le_troisieme_alinea`
  et `libre/sans_suspension`, jamais les plus touchées. Aucun témoin de page ne
  le montre.

**Ce qui reste.**

1. Aux pages, ci-dessus : la session des pages.
2. La base des non-salariés, suspendue le nombre de mois que le dépassement
   épuise (D. 634-11-5, D. 643-10-2), et la durée requise des carrières
   libérales : une session du modèle, puis les complémentaires qui la suivent.
3. Les statuts des sections que l'index ne garde pas (CARPIMKO, CAVEC après
   2012, CAVP, CIPAV) et chaque section avant les rédactions lues ; la date
   d'effet des règlements du 10 juillet 2026 ; comment la CARMF répartit la
   suspension conjointe.
4. L'Ircantec de 2004 à 2020 et avant 2004 : une instruction de la caisse.
5. L. 732-39 et L. 732-40, pour la base de l'exploitant, que la RCO suit.
6. Le versement des artisans et des commerçants avant 1985 : le décret
   n° 73-937 au Journal officiel en images, que l'index ne garde qu'en notice.
7. Les restes du bloc : la veille du projet de loi de financement pour 2027 ;
   le RCO et le NRCO d'avant 2009 (au propriétaire, action 89) ; aux pages, la
   phrase du RCI ; au propriétaire, la part de base de l'ordre de D. 133-4 de
   2016 à 2019.
