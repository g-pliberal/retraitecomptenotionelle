# Étape 4, septième partie : la durée de la majoration pour enfant, la limite de cumul revue à la retraite du survivant, les majorations forfaitaires de 1972 à 1982

**Le 9 octobre 2026, la demande.** Le propriétaire, reprenant trois points de
« Ce qui reste » de la sixième partie : « la durée de la majoration pour
enfant, qui devrait s'arrêter quand le dernier enfant n'est plus à charge ; la
limite de cumul recalculée quand la retraite du survivant arrive après sa
réversion ; les majorations des retraites personnelles d'avant 1983 ». La
suite était rouge sur `main` à l'ouverture : le contrôle du barème de la
réversion appelait `controler` à l'ancienne, et le parcours de présentation
comptait encore 138 séries ; réparés d'abord (ac0d7a6).

**Ce que dit le droit, lu le jour même** (journal de veille du 9 octobre,
« durée, cumul revu, majorations » ; fiches `majoration_forfaitaire_reversion`,
`reversion` et `majorations_forfaitaires_1972_1982`). L'API de la base de la
Cnav sert aussi ses exposés (`expose/exposeByFileLeafRef`) et ses circulaires
(`reference/referencesByFileLeafRef`), adresses relevées dans le code de son
site.

- *La durée de la majoration pour enfant.* « La majoration n'est plus servie »
  quand le bénéficiaire se remarie, vit maritalement, perçoit une retraite
  personnelle, ou que l'enfant n'est plus à charge ou atteint l'âge limite :
  « 1er jour du mois suivant celui au cours duquel l'une des conditions
  d'attribution n'est plus satisfaite à l'exception de la condition d'âge du
  titulaire » (circulaire Cnav n° 76/88, fiche n° 9). L'enfant « n'est plus à
  charge le jour de son » anniversaire : seize ans jusqu'en 2015 (R. 313-12),
  la majorité depuis le 1er janvier 2016 (R. 161-4), vingt ans pour
  l'étudiant, l'apprenti et l'enfant infirme. Avant juillet 2004, le
  remariage et la vie maritale l'arrêtaient.
- *La limite revue.* « Les règles de cumul s'appliquaient à la date
  d'attribution du 2e avantage : soit au point de départ de l'avantage
  personnel s'il était attribué après la retraite de réversion » (exposé
  « Retraite de réversion cumulable ») ; la pension du défunt y est
  « revalorisée par les coefficients intervenus » entre les deux points de
  départ — avant le 15 novembre 1990, tenue pour « 100/52èmes de la pension de
  réversion effectivement servie », le double avant décembre 1982 (circulaire
  n° 105/90, § 12 et 13, avec un exemple : (65 973 + 50 000) × 52 % =
  60 305 F). La retraite attribuée depuis juillet 2004 « recalcul[e] » la
  réversion « compte tenu des règles de ressources » de 2004.
- *Les majorations des pensions d'avant 1975.* 5 % au 1er janvier 1972 (loi
  n° 71-1132, articles 8 et 10, salariés agricoles compris), au 1er juillet
  1976 (loi n° 75-1279, article 3) et au 1er octobre 1977 (loi n° 77-657) aux
  pensions d'avant 1973 liquidées sur la durée maximum de leur date, 120
  trimestres avant 1972, 128 en 1972 ; au 1er décembre 1982, 6 % à celles
  d'avant 1972 et 4 % à celles de 1972, quelle que soit leur durée, 5,5 % à
  celles de 1973 sur 136 trimestres, 1,5 % à celles de 1974 sur 144 (loi
  n° 82-599, articles 1er et 2, salariés agricoles compris). La pension
  principale et la bonification pour enfants, non le minimum ni la majoration
  pour conjoint à charge ; « Les pensions de réversion accordées aux conjoints
  survivants d'assurés qui auraient pu bénéficier » de ces majorations
  « doivent être revalorisées dans les mêmes conditions » (circulaires
  n° 15/76, n° 64/77 et n° 79/82, C).

**Ce qui est fait.**

- *La majoration pour enfant* (`droit/reversion.py` et son jumeau) : chaque
  enfant à charge à la date d'effet compte jusqu'au mois qui suit son
  anniversaire à l'âge de la version en vigueur ce jour-là
  (`_fin_de_la_charge`) ; la majoration entière cesse le mois qui suit la
  retraite du survivant, ou, avant juillet 2004, son union nouvelle. La ligne
  écrit ses étapes, `majoration_forfaitaire_enfants_etapes`, la dernière
  nulle.
- *La retraite du survivant* : un champ de plus, `conjoint_retraite`, dans
  les deux saisies, le formulaire et la chronologie — l'acte de départ du
  conjoint —, que `Conjoint.retraite` relit. Sans lui, la présomption neuve
  `retraites_du_survivant_servies` les tient pour servies dès la date
  d'effet, comme avant. Avec lui, la réversion ne compte pas à cette date des
  retraites qui ne sont pas encore servies, avant juillet 2004 comme depuis.
- *La limite revue* (`_cumul_a_la_retraite`) : à la date de sa retraite,
  avant juillet 2004, la limite de la version en vigueur ce jour-là, sur la
  réversion servie, majorations forfaitaires venues comprises, la limite
  forfaitaire de son année ramenée aux euros de l'année du décès par les
  coefficients des pensions, la pension du défunt ou, avant le 15 novembre
  1990, la réversion servie rapportée au taux de la limite. La ligne écrit
  `cumul_effet`, `reduction_du_cumul` — la majoration de 10 % suivant la
  réversion — et la limite de ce jour ; la majoration de 11,1 % lit la
  réversion revue.
- *Les majorations de 1972 à 1982* : la fiche neuve, cinq versions de la date
  d'effet de la pension ; la liquidation écrit si la pension a pris la durée
  maximum de sa date (`PensionRegime.sur_la_duree_maximum`) ; « faire vivre »
  les porte dans le coefficient du régime général et des salariés agricoles
  (`majorations_forfaitaires`), la bonification pour enfants les suivant ;
  l'échéancier passe à la réversion celles qui viennent après l'année de ses
  montants, comprises dans son montant calculé jusqu'à sa date d'effet,
  écrites ensuite à leur date, avant celles de la réversion le même jour.
- *La page* : la carte dit ce que devient la majoration pour enfant (« plus
  rien à partir de février 2032 ») et ce que la limite revue retire (« de
  moins à partir de mars 2001, limite de cumul avec sa propre retraite ») ;
  le formulaire demande « Sa propre retraite, depuis ».
- *Les tests* (`test_reversion.py`, vingt-quatre de plus, et celui de la page) : la fin de chaque
  part, avant et après 2016, la retraite et l'union qui l'arrêtent ; la
  limite revue, la règle d'avant le 15 novembre 1990, l'exemple de la
  circulaire n° 105/90 rejoué ; les majorations de chaque date, les taux que
  les circulaires donnent à la pension majorée (46,30 %, 47,04 %, 47,82 %,
  48,72 %), la réversion qui les suit ; la page ; les refus de la saisie
  (`test_web.py`). Quatre témoins de simulation : `reversion_cumul_a_sa_retraite`,
  `reversion_enfants_jusqu_a_sa_retraite`, `retraite_majoree_en_1982`,
  `reversion_majorations_avant_1983`, les deux moteurs au bit près.

**Les mesures.** Aucune pension au départ ne bouge, sur 781 témoins. Trois
témoins changent de valeur : la retraitée partie en 1970 voit sa pension du
régime général majorée de 6 % depuis décembre 1982 (5 054,80 € par an
aujourd'hui au lieu de 4 768,68 €), que son minimum vieillesse compense à
l'euro près ; le salarié parti en 1971 reçoit 303,07 € de plus par an, et la
réversion de sa veuve 52,27 € en décembre 1982 au lieu de 20,42 € — 6 % puis
4 % —, en euros de 1971 ; le veuf aux deux enfants de 2012 et 2014 voit sa
majoration de 2 643,84 € tomber à moitié en février 2030, à rien en février
2032. La veuve de 1999 qui date sa retraite en mars 2001 reçoit sa réversion
entière, 5 937,02 €, puis 2 217,99 € de moins, sous la limite de 2001
(9 719,03 €, en euros de 1999).

**Ce qui reste.**

1. *De la majoration pour enfant* : l'étudiant, l'apprenti et l'enfant
   infirme à charge jusqu'à vingt ans, que la saisie ne distingue pas ;
   l'enfant de seize ans à la fin de 2015, que la majorité de 2016 rendait de
   nouveau à charge ; l'enfant né après la date d'effet (R. 353-10) ; le régime
   qui la sert (D. 173-21-7) ; un exemple chiffré.
2. *De la retraite du survivant* : la réversion d'avant juillet 2004 que sa
   retraite, attribuée depuis, recalcule aux règles de ressources de 2004, et
   la révision de R. 353-1-1, dont la dernière, à sa retraite ; ses retraites
   servies toutes à la fois.
3. *Des majorations de 1972 à 1982* : les textes qui les auraient étendues
   aux salariés agricoles en 1976 et 1977, l'Alsace-Moselle (décret
   n° 76-405) ; l'ancien invalide des deuxième et troisième groupes, que les
   circulaires en écartent en partie. Les carrières que la saisie reconstitue
   ne comptent au régime général que depuis 1945 : seules celles de 1982 sans
   condition de durée jouent dans les témoins.
4. *Hors de l'étape* : le tableau de `docs/avantages_non_contributifs.md`
   (« 3. La liste ») dit toujours « absent » la majoration de 11,1 % et la
   majoration pour enfant à charge.
