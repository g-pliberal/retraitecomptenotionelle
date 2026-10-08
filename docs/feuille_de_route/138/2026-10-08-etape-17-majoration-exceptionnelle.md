# Étape 17, quatrième partie : la majoration exceptionnelle des petites pensions de septembre 2023

**Le 8 octobre 2026, la demande.** Le propriétaire : « la majoration
exceptionnelle de septembre 2023 des pensions du régime général et des salariés
agricoles liquidées avant cette date au minimum contributif, dans l'échéancier
(point de TRAJECTOiRE au registre) » ; et, si le mécanisme est le même, le
relèvement des pensions des exploitants déjà liquidées, au 1er septembre 2023
lui aussi (loi n° 2023-270, article 18, VI), une note par étape — celle-ci pour
l'étape 17, celle du 8 octobre à l'étape 8 pour les exploitants.

**Ce que dit le droit, lu le jour même** (journal de veille du 8 octobre ; la
fiche `majoration_exceptionnelle_2023` cite chaque texte).

- *La loi* (n° 2023-270, article 18, V) : les pensions personnelles de base du
  régime général, des régimes qu'il a intégrés et des salariés agricoles « ayant
  pris effet avant le 31 août 2023 », liquidées au taux plein, quand l'assuré a
  une durée cotisée tous régimes que le décret fixe, sont majorées « à compter
  du 1er septembre 2023 » d'un montant que le décret fixe, au prorata de la
  durée cotisée dans le régime ; la pension du régime ne dépasse pas avec elle
  un plafond au prorata de sa durée validée, ni toutes les pensions, de base et
  complémentaires, le plafond de L. 173-2 ; elle est revalorisée ensuite par
  L. 161-23-1. Elle n'est PAS réservée aux pensions portées au minimum
  contributif : la demande le disait après le registre, qui le disait après
  TRAJECTOiRE.
- *Le décret* (n° 2023-754, article 3, lu dans l'index JORF, où le registre le
  croyait absent) : 1 200 € par an, 120 trimestres cotisés, un plafond de
  10 170,86 € par an — le minimum contributif majoré des pensions de septembre
  2023 ; le dépassement du plafond tous régimes s'impute à chaque régime au
  prorata de sa majoration ; la révision quand une pension change, les plafonds
  revalorisés comme les pensions.
- *La circulaire Cnav n° 2023-21* du 2 novembre 2023 : les cultes aussi ; ni la
  retraite progressive ni le versement forfaitaire unique ; tous les cas du
  taux plein, l'âge et l'inaptitude compris ; les 120 trimestres cotisés
  français et étrangers, quatre par an, sans l'AVPF ; trois calculs en euros
  par mois, chacun tronqué au centime — la majoration théorique, 100 € au
  prorata de la durée cotisée sur la durée maximum de la génération ; retenue
  sous le plafond du régime, 847,57 € au prorata de la durée validée, la
  pension comparée avec son minimum contributif et sa majoration pour enfants,
  sans sa surcote ; servie sous les 1 352,23 € tous régimes, pensions
  étrangères exclues — ; l'ASPA la compte, la réversion ne la lit pas. Ses
  exemples sont chiffrés.

**Ce qui est fait.**

- *La fiche* `majoration_exceptionnelle_2023`, deux versions selon la date
  d'effet de la pension (avant septembre 2023, la majoration ; depuis, le
  minimum relevé), lue par les deux moteurs (`FichesDatees`), au registre des
  réformes `reforme_2023`.
- *Le départ* écrit ce que la majoration relira (`PetitePension`, dans
  `droit/completer.py` et son jumeau) : pour chaque pension que le minimum
  contributif regarde, son taux plein, ses durées cotisée et validée, la durée
  maximum de la génération, les trimestres cotisés tous régimes et la surcote,
  que le minimum laisse en sus depuis avril 2009 ; le résultat du départ les
  porte, ceux de chaque départ quand les régimes liquident à des dates
  différentes.
- *« Faire vivre »* (`majorer_les_petites_pensions`, et
  `majorerLesPetitesPensions`) la calcule au mois où elle est due, sur ce que
  les pensions servent alors, chacune menée par la règle de son régime, en
  trois temps comme la caisse ; une pension française qui commence après la
  révise à sa date, sous les plafonds revalorisés ; elle suit ensuite
  L. 161-23-1 jusqu'à l'échéance. La pension servie de chaque régime la porte
  (`RegimeServi.majoration`) ; la réversion, qui lit la pension du départ
  menée, ne la voit pas ; l'ASPA de l'échéance la compte.
- *L'échéancier* l'inscrit : un début de composante, induit, au 1er septembre
  2023, sa composante au montant de ce mois, et la pension de l'échéance qui la
  dit comprise. La sortie JSON du simulateur et le schéma de « faire vivre »
  portent la majoration de chaque régime.
- *Les tests* (`tests/test_majoration_exceptionnelle.py`, onze) : les exemples
  de la circulaire rejoués sur la fonction — 95,80 €, 812,04 €, 0 € au-dessus
  du plafond, 87,42 €, 69,69 € et 30,30 € de deux régimes d'avant la
  liquidation unique, 88,02 € rognés à 50,35 € — ; l'écrêtement tous régimes
  au prorata ; des carrières construites, majorées ou non (après septembre
  2023, décotée, sans les 120 trimestres, au-dessus du plafond) ; l'événement,
  la réversion inchangée ; le journal des deux moteurs, sur sept requêtes dont
  cinq majorées. Et l'exemple 3 de la circulaire, rejoué par une carrière dans
  `exemples_officiels.yaml` (170 trimestres dont 146 cotisés : 87,42 €), par
  une grandeur neuve de `tests/test_oracle.py`.

**Les mesures.** Une pension partie en février 2015 au minimum majoré, 168
trimestres cotisés : 99,99 € en septembre 2023 — sa pension sans surcote
dépasse le plafond d'un centime —, 108,57 € en 2026. La même mère de trois
enfants : 22,96 €, sa majoration pour enfants entrant dans la comparaison. Sur
les 763 témoins de simulation, un seul la reçoit, `reversion_minimum_contributif`
(108,59 € par mois en 2026), et son ASPA baisse d'autant ; aucune pension au
départ ne bouge, ni aucune page : la page Coût et les cas types travaillent au
départ. Les deux moteurs concordent sur les 763 témoins.

**Ce que la vérification a trouvé.**

- La loi majore toute petite pension au taux plein, portée ou non au minimum
  contributif : une pension au-dessus du minimum et sous le plafond est relevée
  jusqu'à lui. TRAJECTOiRE recalcule le minimum aux montants de septembre 2023
  et ne garde que la hausse du minimum majoré, bornée à 100 € par personne.
- Le montant de la circulaire est mensuel et tronqué, celui du décret annuel :
  le modèle calcule au mois, la pension du mois arrondie au centime, puis
  annualise. La majoration d'une pension au minimum majoré de 2015 est de
  99,99 €, non de 100 €, parce que le minimum du départ, mené par les
  coefficients de L. 161-23-1, dépasse d'un centime celui de septembre 2023.
- Le décompte des 120 trimestres est celui des trimestres cotisés tous régimes
  que l'ouverture compte déjà, étrangers compris, sans l'AVPF ; la majoration
  du minimum contributif, elle, compte l'AVPF depuis septembre 2023.
- `textes.py` : l'article 18 de la loi, rattaché, abaisse le cliquet des
  textes d'une rédaction (9 899).

**Ce qui reste**, de cette partie :

1. La surcote des autres pensions de base (fonction publique, régimes
   spéciaux), que la comparaison tous régimes garde.
2. La révision par la seconde pension de qui retravaille, et par une pension
   modifiée après coup — le minimum contributif que révise une pension
   étrangère.
3. Aux cultes, les durées d'avant 1998, que le minimum contributif ne lit pas ;
   la circulaire de la Cavimac, et celle de la MSA pour les salariés agricoles.
4. Une carrière qui rende les pensions des autres exemples de la circulaire,
   pour les rejouer dans `exemples_officiels.yaml`.
5. Les pensions prises avant le 1er avril 1983, que le minimum contributif ne
   regardait pas, et qui ne sont pas majorées.
