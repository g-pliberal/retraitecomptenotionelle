# Étape 12, onzième partie : le RCI en cumul plafonné, et son versement forfaitaire unique

**Le 23 octobre 2026, la demande.** Vague du 23 octobre : la session de suivi
« Qu'est-ce qu'il reste à faire ? » lance, sur la demande du propriétaire
(« Fait ça », en réponse à l'offre d'une session par chantier qu'une session peut
mener seule), douze sessions en parallèle, une étape chacune ; celle-ci,
l'étape 12 de l'action 138 : au RCI, le cumul plafonné et le versement unique,
le premier point « une session » du bloc de l'étape (le 1 de « Ce qui reste »
de `…-rci-et-cotisation-minimale-en-cumul.md`). Règle du scénario 1, en Python
puis en JavaScript.

**Ce que dit le droit** (journal de veille,
`2026-10-23-action-138-etape-12-cumul-et-versement-unique-du-rci.yaml` ; fiches
`cumul_emploi_retraite_complementaire_des_independants` et
`versement_unique_rci`).

- *Le cumul.* Les règlements du RCO et du NRCO de 2009 (articles 23, II, et 10),
  puis celui du RCI (article 27, de 2013) : « Lorsque l'assuré est soumis à une
  suspension dans le régime de base en application des alinéas 2 et 3 de
  l'article L. 634-6 [...], le service de la pension de vieillesse
  complémentaire est suspendu pour la même durée », et servi entier en cumul
  intégral ; la caisse l'applique depuis le 1er janvier 2009 (circulaire RSI
  n° 2009-044). Depuis l'arrêté du 19 juin 2024, en vigueur le 26 juin, « Les
  dispositions de la section 3 [...] sont applicables au service de la
  pension » : L. 634-6 et D. 634-11-5, la réduction du dépassement. En 2027
  (arrêté du 21 septembre 2026), L. 161-22, dont la réduction « est appliquée,
  par priorité, sur les pensions versées par les régimes de retraite de base ».
- *Le versement.* Sous quarante points, « le service de la pension est remplacé
  par un versement forfaitaire unique », les points par le revenu de
  référence, la « dernière valeur connue » jusqu'en juin 2024, celle de la date
  d'effet depuis (article 39) ; quel que soit leur nombre quand la base l'a été
  (article 40) ; il « fait obstacle à l'attribution d'une pension de
  réversion » (article 41, II). La circulaire RSI n° 2013-004 compte « le nombre
  total des points complémentaires » ; « si seul un des droits personnels du RVB
  est servi sous forme de VFU, le droit personnel unique du RCI sera payé
  mensuellement ».
- *La caisse.* Ni instruction ni exemple du cumul plafonné du RCI depuis 2024 :
  l'exposé « Retraite personnelle complémentaire » dit seulement que « Les
  règles du cumul emploi-retraite du régime de base des travailleurs
  indépendants s'appliquent au régime complémentaire ».

**Ce qui est fait.**

- *Le cumul, dans les deux moteurs* (`_complementaire_des_independants`,
  `complementaireDesIndependants`) : la complémentaire — le RCI, le RCO et le
  NRCO, une seule pension, la réduction répartie au prorata — suspendue avec la
  base depuis 2009, entière en cumul intégral et quand la base n'est que
  réduite ; depuis juillet 2024, réduite du dépassement entier, comme la base ;
  pour la première pension de 2027, de ce que la base n'absorbe pas ; avant
  2009, servie entière, par une version supposée. Hors de 2027, seule
  l'activité d'artisan ou de commerçant la touche.
- *Le versement, dans les deux moteurs* (`verser_en_capital`,
  `_seconde_retraite_rci`, et leurs jumeaux) : la pension du RCI de moins de
  quarante points — la pension divisée par la valeur de service de chaque
  nature de points —, ou dont la base de l'indépendant, à défaut le régime
  général qui la liquide, a été versée en une fois, remplacée par ses points au
  revenu de référence de la date d'effet ; la seconde pension de même, sous
  quarante points (`NouvellePension.capital`) ; plus de réversion du RCI après
  lui (`rien_apres_un_capital`).
- *Fiches* : deux neuves, `cumul_emploi_retraite_complementaire_des_independants`
  et `versement_unique_rci` (lue par `FichesDatees`, que le paquet porte) ;
  `reversion_rci` (article 41) et `cumul_emploi_retraite_et_retraite_progressive`
  mises à jour ; le cliquet des textes abaissé.
- *Tests* : huit dans `test_emploi_retraite.py`, dix cas ; quatre dans
  `test_versements_uniques.py`, et un cas de plus à sa réversion, deux à sa
  confrontation des moteurs ; deux dans `moteur.test.js` ; posés à la main — la
  moitié du plafond ; 7 % au revenu de référence de 2020, 17,691 €, et celui de
  2022, 17,956 € ; 8,1 % à 21,532 €, et celui de 2026, 21,726 € —, vus rouges ;
  trois témoins, `cumul_commercant_suspendu_2013`, `cumul_artisan_2024` et
  `cumul_artisan_carriere_longue_2028`.

**Mesuré.** Python et JavaScript au bit près sur les cas et sur les témoins.
Le cumul : un témoin bouge, `cumul_artisan`, par le statut de sa complémentaire,
servie entière quand la base n'est que réduite, sans qu'aucune pension bouge.
`cumul_artisan_2024` : depuis juillet 2024, la complémentaire de 428,12 € par
mois perd 112,85 €, 33,71 du RCI et 79,14 du RCO, autant que la base ;
`cumul_commercant_suspendu_2013` : le NRCO et le RCI, 97,67 € par mois,
suspendus avec la base ; `cumul_artisan_carriere_longue_2028` : la base de
1 913,73 € réduite de tout, la complémentaire de 338,75 € de ses 642,24 €. Le
versement : l'artisane de 2020 à 4 000 €, 15,83 points, 19,33 € par an, reçoit
284,19 € en une fois en 2022, et sa réversion du RCI disparaît. Six témoins
bougent, par la clef `capital` des nouvelles pensions ; un seul en reçoit un,
`seconde_pension_artisane_au_minimum_2026` : sa seconde retraite du RCI, 15,66
points, 340,17 € en une fois au lieu de 21,09 € par an. Aucune pension ne bouge ;
aucune page, hors la page Méthode, par les données d'autres sessions.

**Trouvé en chemin.**

- *La classe.* Les sections libérales — des statuts de 2010 et 2011, que l'index
  JORF garde, suspendent aussi la complémentaire « pour la même durée » que la
  base —, l'Ircantec et la RCO agricole sont toujours servies entières en cumul
  plafonné (fiche `cumul_emploi_retraite_et_retraite_progressive`).
- *Le versement forfaitaire de la base de l'artisan et du commerçant*, que la
  fiche `versement_forfaitaire_unique` ne porte pas : l'article 40 ne joue que
  par celui du régime général.

**Pour les pages**, que leur session tient.

- `cumulEmploiRetraite` (`pages.js`) range dans la « base » toute pension qui
  n'est pas de l'Agirc-Arrco. Depuis juillet 2024, la complémentaire de
  l'indépendant, réduite comme la base et rangée avant elle, devient la pension
  « la plus touchée » : la page dirait « votre pension est réduite du
  dépassement, 225,70 € par mois en moyenne » quand la base et la
  complémentaire perdent chacune 112,85 € (témoin `cumul_artisan_2024`) ; mieux,
  « votre pension de base et votre complémentaire sont chacune réduites du
  dépassement ». Les motifs `base_reduite` et `imputee_sur_la_base`, jamais les
  plus touchés, n'ont pas de phrase. Aucun témoin de page ne le montre.
- `droitsDuCumul` ne dit pas le versement forfaitaire unique de la seconde
  pension du RCI (`capital`).

**Ce qui reste.**

1. Aux pages, ci-dessus : la session des pages.
2. Le RCO et le NRCO avant 2009 (cumul) et avant 2013 (versement) : leurs
   règlements de 1978 et de 2003, et la circulaire RSI n° 2007-109 ; les deux
   versions sont supposées.
3. La réversion du RCI de moins de quarante points (article 41, I), et les
   points du 6 du IV de l'article 7, que le versement compte.
4. Une instruction ou un exemple de la caisse : la complémentaire perd-elle le
   dépassement entier, ou une part ?
5. La classe, ci-dessus : les sections libérales, l'Ircantec, la RCO agricole ;
   le versement forfaitaire de la base des indépendants.
6. Les restes du bloc : la veille du projet de loi de financement pour 2027 ;
   aux pages, la phrase du RCI ; au propriétaire, la part de base de l'ordre de
   D. 133-4 de 2016 à 2019.
