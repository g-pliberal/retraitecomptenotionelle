# Étape 4, dix-huitième partie : les majorations au maximum — la pension majorée sur son montant entier, sous le maximum du jour de chaque majoration ; le maximum de la réversion relevé avec son taux

**Le 25 octobre 2026, la demande.** Le propriétaire, dans la onzième vague des
sessions : le dernier point sans propriétaire du bloc de l'étape, les majorations au
maximum. Les décrets agricoles de 1976 et 1977, au fac-similé, et le choix de la date
de la demande restent au propriétaire, et ce que le bloc renvoie au site, au site.

**Ce que dit le droit, lu le jour même** (journal de veille du 25 octobre,
« majorations au maximum » ; fiches `majorations_forfaitaires_1972_1982`, `reversion`
et `pension_maximale_regime_general`).

- *La pension.* « La majoration de 5 % s'applique à la pension principale non
  écrêtée résultant des versements » (circulaires Cnav n° 2/72, IV, A, n° 15/76 et
  n° 64/77, A), « avant comparaison au minimum et au maximum » (exposé « Montant de
  la retraite personnelle ») ; et les maxima de 1972 à 1974 « sont à retenir pour
  toutes les pensions servies au cours des années précitées, quelles que soit leur
  date d'entrée en jouissance » (n° 2/72, I, C). En 1993 encore, la compensation de
  la revalorisation se calcule « sur la pension non écrêtée », le maximum pouvant
  « continuer à être servi » (circulaire ministérielle n° DSS/VI/93/85) : la caisse
  mène la pension entière, et la compare au maximum à chaque revalorisation.
- *La réversion.* La majoration de 4 % de décembre 1982 « répercute exactement
  l'augmentation du taux de la pension de réversion », de 50 à 52 %, sur « le
  montant calculé de la pension avant qu'elle n'ait été portée éventuellement au
  minimum » (n° 120/82, § 2), dont le maximum vaut « 52% du maximum qui était ou
  aurait été opposable à l'assuré décédé » (§ 4) ; en 1995, la réversion est
  « revalorisée par le coefficient 1,03846. Le montant revalorisé est ensuite
  comparé avec le montant minimum et le montant maximum » (n° 3/95, § 241), celui de
  54 % (§ 23) ; réduite pour cumul, elle « n'est pas revalorisée » (§ 242).
- *Aucun exemple chiffré* ne majore une pension ni une réversion au maximum.

**Ce qui est fait.**

- *La réversion* (`droit/reversion.py`, `_majorations_ulterieures`, et son jumeau) :
  le maximum de la date d'effet suit les majorations de la réversion même, de 50 à
  52 puis 54 % du maximum des pensions ; celles de la pension du défunt, qui ne
  changent pas le maximum des pensions, se comparent à lui. La réversion ramenée à
  son maximum ne recevait rien de ses majorations : elle en reçoit la part du taux.
- *La pension* (`revalorisation.maximum_du_jour`, `maximumDuJour`) : le jour de la
  dernière majoration venue, la pension servie est la plus basse de la pension
  entière — ce que le coefficient mène, plus ce que le maximum de sa liquidation en
  avait retiré (`PensionRegime.ecretement_du_maximum`) —, majorée, et du maximum de
  ce jour, que le coefficient de l'ajournement d'avant 1983 multiplie ; elle suit
  ensuite les pensions jusqu'à la majoration suivante. Ce que cela change, en euros
  de l'échéance, s'ajoute à la pension servie (`RegimeServi.maximum_du_jour`, au
  schéma de l'étape et au détail de la composante de l'échéance) : positif quand le
  maximum du jour rend ce que celui de la liquidation avait retiré, négatif quand il
  ramène la pension que ses majorations portent au-dessus de lui. La majoration pour
  enfants suit la pension servie, en décembre 2019 comme à l'échéance ; la
  réversion, calculée « avant comparaison au minimum et au maximum », garde la
  pension entière, majorée.
- *Les tests*, posés à la main depuis les circulaires et vus rouges : la réversion de
  1980 ramenée à son maximum, que ses deux majorations portent à 52 puis 54 % ; la
  même sous son maximum, que les 6 % de la pension du défunt parti en 1971 et ses
  4 % portent au-dessus ; celle de 1990, portée à 54 % en 1995 (`test_reversion.py`) ;
  les deux moteurs sur le témoin du cadre parti et mort en 1990 ; la pension de 1971
  sur quatre-vingt-seize trimestres, au salaire annuel moyen forcé à 1,3 puis à 3
  plafonds, servie en décembre 1982 entière et majorée, puis au maximum de 1982
  (`test_pension_maximale.py`) ; les deux moteurs sur huit pensions, par la fonction
  seule, et sur la liquidation qu'on fait vivre de 1981 à 2026, aucune saisie
  n'atteignant une pension d'avant 1975 au maximum.
- *Les fiches* : `majorations_forfaitaires_1972_1982` — l'intitulé, ce qu'elle lit et
  écrit, l'écart du maximum récrit, la lecture de la circulaire n° 2/72, le code,
  l'historique, l'effet ; `reversion`, l'écart des majorations, une lecture,
  l'historique ; `pension_maximale_regime_general`, l'écart des arrérages et
  l'historique ; la page des limites.

**Les mesures.** Sur les 907 témoins de simulation, aucune pension des six scénarios ne
bouge, ni aucun rendu de page ; une réversion bouge, celle de la veuve du cadre parti
et mort en 1990, ramenée à 52 % du maximum des pensions, 5 194,02 euros de 1990 par
an, que la majoration de 1995 relève désormais de 199,76 euros, 3,846 % de son
maximum, au lieu de rien. Aucun témoin ne porte une pension d'avant 1975 au maximum :
celles des carrières du modèle, comptées depuis 1945, restent loin des durées de leur
date. Sur les cas posés, aux euros de 1982 : la pension de 1971 sur quatre-vingt-seize
trimestres, au salaire annuel moyen de 1,3 plafond, sert en décembre 1982 6 051,64
euros par an au lieu de 5 818,89 (+4,0 %) ; à trois plafonds, le maximum de 1982,
6 252 euros (+7,4 %). La pension de 1970 sur la durée maximum, ramenée au maximum de sa
liquidation, en vaut, revalorisée et majorée, 1,07 fois celui d'octobre 1977, auquel
elle est désormais ramenée : 6,9 % de moins que ce que le modèle lui servait alors.

**Ce qui reste.**

1. *La comparaison à chaque revalorisation* : avant 1987, chaque arrêté bornait au
   maximum de la date la pension en cours de service, et la réversion ; le modèle ne
   compare qu'à la liquidation, à la date d'effet de la réversion et le jour des
   majorations, et compte le maximum de décembre 1982 sur le plafond moyen de
   l'année. Ce sont les écarts des fiches `pension_maximale_regime_general` et
   `reversion`, que les notes de l'étape 17 et du maximum de la réversion
   déclaraient.
2. *La réversion réduite pour cumul*, que la caisse ne majorait pas en 1995
   (n° 3/95, § 242), et que le modèle majore : l'écart de la fiche `reversion`.
3. *Au propriétaire* : les décrets n° 76-727 et n° 77-966, au fac-similé ; le choix de
   la date de la demande, présumée le mois qui précède la date d'effet.
4. *Au site* : rien de neuf. La réversion y porte déjà ses majorations, et aucune
   saisie n'atteint une pension d'avant 1975 au maximum.
