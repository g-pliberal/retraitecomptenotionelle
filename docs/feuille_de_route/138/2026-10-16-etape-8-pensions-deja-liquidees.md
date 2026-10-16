# Étape 8, septième partie : les pensions des exploitants déjà liquidées — les plans de revalorisation révisés, la pension majorée de référence de 2009

**Le 16 octobre 2026, la demande.** Le premier reste de l'étape : « les
pensions déjà liquidées, révisions des plans comprises » (point 2 de « Ce qui
reste » de la note du 14 octobre sur les plans). Le modèle calculait les plans
de 1997 à 2008 et la PMR à la liquidation, puis menait le tout au coefficient
de la pension : le tiers servi en 1997 le restait à vie, et une pension prise
avant 2009 ne recevait jamais la PMR. Session du modèle, une de treize.

**Ce que dit le droit** (journal de veille du 16 octobre, index JORF et LEGI).

- *Les plans servent les « pensions dues »*, non les pensions prises : le tiers
  en 1997, les deux tiers en 1998 (décret n° 97-163, article 3) ; « pour les
  pensions dues à compter du 1er janvier 2001 », 29,23 points, le IV de
  l'article 1er, la minoration, « supprimé » (décret n° 2001-170, article 3) ;
  pour les pensions prises de 1997 à 2001, A = (MV1 - AVTS) / (37,5 × VP) aux
  montants « en vigueur au 1er janvier de l'année considérée » (décret
  n° 2002-297, article 4), sans le minimum C, que le seul décret n° 2002-298
  ouvre aux pensions prises depuis 2002.
- *La PMR de 2009 s'ouvre aux pensions prises avant* (loi n° 2008-1330,
  article 77 ; décret n° 2009-173) : avant 2002, vingt-deux ans et demi dans le
  régime en 2009, dix-sept et demi depuis 2011, sans condition de taux plein
  (D. 732-109, 1°) ; de 2002 à 2008, le taux plein en plus (2°). Elle compare
  les pensions « après mise en œuvre des revalorisations prévues aux articles
  D. 732-110 à D. 732-149 dans leur rédaction antérieure au 1er janvier 2009 ou
  de la majoration de pension prévue à l'article L. 732-25-1 » (D. 732-112) :
  les points des plans de 2008 restent, et la surcote compte, quand elle ne
  compte pas pour une pension prise depuis 2009. Le montant et le plafond de
  septembre 2023 et de 2026 ne nomment que les pensions prises depuis
  (D. 732-111, D. 732-113) : celles d'avant suivent la règle de 2022.

**Ce qui est fait**, dans les deux moteurs.

- *La liquidation écrit ce que la révision relira* : `ExploitantAgricole`
  (`droit/completer.py`, et `exploitant` du jumeau), la carrière du départ,
  l'éligible agricole, la durée, la pension de base avant les plans et la PMR,
  la majoration des plans servie.
- *`majoration_retraite_proportionnelle` prend `quand`* : la règle des pensions
  dues cette année-là, A au minimum vieillesse, au forfait et à la valeur du
  point du 1er janvier, n celui de la liquidation ; le minimum C ne s'ouvre pas
  aux pensions prises avant 2002 (paramètre `minimum_reduit_depuis` de la
  fiche). `pension_majoree` prend la règle, le jour des montants, et les deux
  conditions que D. 732-109 et D. 732-112 posent autrement avant 2009.
- *« Faire vivre » révise* (`reviser_les_exploitants`, `reviserLesExploitants`) :
  les plans à la règle de l'année de l'échéance, 2008 au plus, leurs points
  menés ensuite par le coefficient, en lieu de ceux de la liquidation ; puis,
  depuis 2009, la PMR d'une pension prise avant, à l'échéance, écrêtée sur
  toutes ses pensions et ses majorations pour enfants. La base les porte
  (`RegimeServi.plans`, `.pmr`), le schéma de l'étape les nomme, l'échéancier
  les dit dans le détail de la pension.
- *Les tests* (`tests/test_minima_agricoles.py`, quatre de plus, deux cas de
  plus dans la comparaison des deux moteurs) : le tiers, les deux tiers, 26,933
  puis 29,23, les points de 2008 gardés ; la minoration tombée en 2001 ; la
  carrière complète de 1995 portée en 2009 à la PMR entière ; vingt ans de chef
  partis sans le taux plein en 2000, rien en 2009 et 2010, la PMR au prorata
  depuis 2011, et rien à la même carrière partie en 2004.

**Les mesures**, en 2026, un chef à 30 % du salaire moyen depuis ses vingt ans.
Parti en 1997 : 9 568 € par an au lieu de 6 492, dont 2 801 € des plans révisés
et 275 € de PMR. Parti en 1995, sans plans : 9 568 € au lieu de 5 710, la PMR
entière. Vingt ans de chef partis en 2000 sans le taux plein : 5 103 € au lieu
de 1 904. Parti en 2002 : 34 € de plus, A ayant crû de 2002 à 2008.

**Ce que la vérification a trouvé.**

- *A peut reculer* : la douzaine d'années de chef après trente de conjoint
  collaborateur, partie en 2005 au minimum C, perd 34 € en 2026, MV2 ayant
  moins crû que la valeur du point de 2005 à 2008. Les textes ne l'interdisent
  pas ; la caisse l'a peut-être évité. Déclaré dans la fiche.
- *La comparaison de `test_liquidation`* échoue, sans ce changement aussi, sur
  la requête 188, un départ du FSPOEIE daté de 1995 en Python et de 1999 en
  JavaScript : pas de ce sujet.

**Ce qui reste**, de cette partie :

1. La révision des pensions prises avant 1997 (article 2 du décret n° 97-163 :
   vingt points, puis 23,9 en 1999… ; D. 732-114 à D. 732-117 ; décret
   n° 2002-297, articles 5 et suivants), sur la durée de chef reconstituée des
   points d'avant 1994 divisés par seize ; elle ne joue que de 1997 à 2008,
   la PMR de 2009 portant ces pensions au moins à son montant.
2. La PMR des pensions prises depuis 2009, toujours calculée au départ : la
   PMR unique de 2022, servie aux pensions déjà liquidées (« y compris aux
   pensions de retraite ayant pris effet avant cette date »), que les
   conjoints collaborateurs partis à PMR2 de 2009 à 2021 ne reçoivent pas ; sa
   révision quand les ressources changent.
3. Le complément du relèvement de septembre 2023, qui ne compte pas la PMR de
   2009 dans les pensions agricoles qu'il plafonne.
4. Les restes de l'étape, inchangés : DM1 au-delà du chef et les seuls points
   de RCO de chef (D. 732-166-4) ; les points des conjoints et aides familiaux
   des plans ; un montant de la MSA pour 2015 à 2017 et 2019.

Les témoins de simulation des chefs partis avant 2009 bougent : GitHub les refait.
