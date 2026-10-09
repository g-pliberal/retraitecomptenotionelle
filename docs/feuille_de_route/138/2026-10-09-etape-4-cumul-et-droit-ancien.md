# Étape 4, sixième partie : le cumul d'avant 2004, la majoration pour enfant à charge, les majorations forfaitaires et l'âge d'avant 1973

**Le 9 octobre 2026, la demande.** Le propriétaire : « étape 4 : L. 353-5 et
D. 355-1, avec les limites de cumul d'avant 2004 ; les majorations
forfaitaires d'avant 1995 et 1982 ; l'âge de 65 ans d'avant 1973. » Les trois
derniers points de « Ce qui reste » (note du 7 octobre), dont la fiche
`reversion` déclarait les deux premiers absents, et que le registre portait
pour le troisième (`baremes_ipp`, chantier 138.4).

**Ce que dit le droit, lu le jour même** (journal de veille du 9 octobre ;
fiches `reversion` et `majoration_forfaitaire_reversion`).

- *Le cumul d'avant juillet 2004.* D. 355-1 (1985-2004), après l'article 90
  du décret n° 45-179 : la réversion se cumule avec les retraites
  personnelles du survivant « dans la limite de 52 p. 100 du total de ces
  avantages et de la pension principale » — la moitié avant décembre 1982 —,
  limite qui « ne peut être inférieure à 73 p. 100 du montant maximum de la
  pension de vieillesse du régime général liquidée à 65 ans » ; au-delà, la
  réversion « est réduite en conséquence ». L'exposé de la Cnav « Retraite de
  réversion cumulable » ajoute que la limite ne descend pas sous la réversion
  portée au minimum ou ramenée au maximum, qu'elle se calcule sur la pension du
  défunt « sans être porté au minimum, ni ramené au maximum », et que les
  retraites du survivant et la limite forfaitaire se divisent par le nombre de
  ses réversions de base (article 91 du décret n° 45-179, D. 171-1). Ces
  retraites, en revanche, « n'étaient pas retenues dans les ressources »
  (exposé « Condition de ressources »). Le cumul naît au 1er juillet 1974
  (loi n° 75-3, article 21) : avant, la réversion complétait la retraite
  personnelle. La limite forfaitaire, au barème de la Cnav : l'AVTS et
  l'allocation supplémentaire jusqu'en juin 1977, puis 60 %, 70 % et, depuis
  décembre 1982, 73 % du maximum des pensions.
- *La majoration forfaitaire pour enfant à charge.* L. 353-5 : au survivant
  « qui n'est pas titulaire d'un avantage personnel de vieillesse d'un régime
  de base obligatoire et qui satisfait à une condition d'âge », par enfant à
  sa charge ; R. 353-9 : moins de soixante-cinq ans, puis l'âge du taux plein
  depuis le 3 juin 2011, l'enfant de moins de seize ans (R. 313-12), mineur
  depuis 2016 (R. 161-4) ; R. 353-11 : 400 F par mois au 1er janvier 1988,
  112,58 € au 1er janvier 2025 ; D. 353-2 : réduite « dans les mêmes
  proportions » que la réversion. Avant juillet 2004, refusée au remarié et au
  concubin (exposé de la Cnav).
- *Les majorations forfaitaires.* La réversion attribuée avant le 1er janvier
  1995 « a été majorée de 3,846 % », celle d'avant le 1er décembre 1982 de
  4 %, sur son montant calculé, avant le minimum (exposé « Montant - retraite
  de réversion », circulaires Cnav n° 120/82 et n° 3/95) : 50 %, puis 52 %,
  puis 54 % de la pension.
- *L'âge d'avant 1973.* Le décret n° 72-1098 abroge au 1er janvier 1973 l'âge
  de soixante-cinq ans, soixante en cas d'inaptitude ; pour un décès
  antérieur, la réversion s'ouvre à cinquante-cinq ans, « au plus tôt à
  compter du 1er janvier 1973 » (article 5).

**Ce qui est fait.**

- *Les données* : `cnav_reversion.py` lit deux barèmes de plus, la limite
  forfaitaire depuis 1974 et la majoration par enfant depuis 1988, et
  confronte la première au barème du maximum de la réversion à chaque date
  commune ; il corrige le montant annuel du 1er janvier 1982, que le barème
  écrit 27 278 F pour un mensuel de 2 306,50 F (27 678 F, 70 % du maximum),
  et exige les deux montants de R. 353-11. Deux séries certifiées `haute`,
  `limite_cumul_reversion.csv` et
  `majoration_forfaitaire_enfant_reversion.csv`, que les deux moteurs lisent.
- *La fiche `reversion`* : la version `avant_1982` coupée en trois —
  `avant_1973`, à soixante-cinq ans, soixante pour l'inapte ;
  `avant_juillet_1974`, sans cumul ; `avant_1982`, le cumul dans la moitié —,
  et quatre paramètres à chaque version : `age_inaptitude`, `cumul`
  (`aucun`, `limite`), `cumul_taux`, `majorations_forfaitaires`. D. 355-1 et
  l'article 90 sont cités ; L. 353-5 et D. 355-1 quittent les textes à
  rattacher.
- *La fiche neuve `majoration_forfaitaire_reversion`*, cinq versions de la
  date d'effet (avant 1988, 1988, 2004, juin 2011, 2016), `transcrite` :
  aucun exemple chiffré publié n'a été trouvé.
- *Le modèle* (`droit/reversion.py` et son jumeau) : la date d'effet est la
  plus proche que chaque version permet (`_premiere_date_d_effet`), ce qui
  donne le 1er janvier 1973 au survivant de cinquante-cinq ans d'un assuré
  mort en 1970 ; avant juillet 2004, les retraites du survivant — ses
  ressources hors de ses revenus d'activité — sortent de ses ressources et
  passent au cumul (`_cumuler`), après le maximum, motif `cumul` ; les
  majorations de 1982 et 1995 s'écrivent à leur date, hors du montant
  (`_majorations_ulterieures`) ; la majoration pour enfant à charge s'ajoute à
  la réversion du régime général, ou du premier régime aligné qui en sert
  une, réduite dans la proportion de la réduite à l'entière
  (`_majoration_forfaitaire_enfants`). La ligne dit `limite_cumul`,
  `majoration_forfaitaire_enfants` et `majorations_forfaitaires`.
- *La page* : la carte dit la réversion réduite « avec ses propres
  retraites », la majoration pour enfants à charge, et chaque majoration
  forfaitaire « de plus à partir de » sa date.
- *Les tests* (`test_reversion.py`) : l'âge d'avant 1973 à trois cas, le
  complément d'avant juillet 1974, le cumul à trois niveaux de retraite, les
  deux séries, les majorations forfaitaires à quatre cas, la majoration pour
  enfant, son âge depuis 2016, sa réduction, le taux plein, la page ; trois
  tests d'avant 2004 déclarent désormais leurs ressources comme revenus
  d'activité. Trois témoins de simulation, `reversion_avant_1973`,
  `reversion_cumul_avant_2004` et `reversion_enfants_a_charge`, les deux
  moteurs au bit près. Le registre : le point de l'IPP sur l'âge d'avant 1973
  passe à `repris` ; celui de Destinie sur L. 353-5 dit que le dépôt la sert.

**Les mesures.** Aucune pension ni réversion des 778 témoins existants ne
bouge : aucun ne déclarait de retraite au survivant d'avant 2004, ni d'enfant
à charge. La veuve d'un salarié mort en mai 1999, qui déclare 6 000 € de
retraite, reçoit du régime général 3 662,01 € au lieu de 5 400 € (−32,2 %), sa
réversion plus sa retraite ramenées à la limite forfaitaire de 1999
(9 662,01 €) ; avec 20 000 € de retraite, rien. La veuve d'un salarié mort en
1971, née en 1916, attend le 1er janvier 1973 au lieu d'avril 1971, et sa
réversion gagne deux fois 20,42 € par an, en euros de 1971, en décembre 1982 et
en janvier 1995.
Le veuf de la mère morte à cinquante-quatre ans en 2024, ses deux enfants de
2012 et 2014 mineurs à sa date d'effet, reçoit 2 643,84 € de majoration par
an, en euros de 2024.

**Ce qui reste.**

1. *De l'étape 4* : rien de son ordre. Ce que ses six notes déclarent reste
   dans les fiches : la révision de la réversion au fil du temps
   (R. 353-1-1), le partage qui « accroîtra », le droit recouvré à la fin
   d'une union nouvelle, la réversion d'un assuré disparu.
2. *Du cumul* : la limite revue à l'attribution du second avantage, quand la
   retraite du survivant suit sa réversion ; la majoration pour enfants de ses
   retraites, que la limite comptait avant septembre 2003 ; les réversions des
   régimes que le modèle ne porte pas, qui divisent aussi.
3. *De la majoration pour enfant* : sa durée, qui finit avec la charge du
   dernier enfant, et l'enfant étudiant ou apprenti jusqu'à vingt ans ; le
   régime qui la sert (D. 173-21-7) ; un exemple chiffré.
4. *Des majorations forfaitaires* : celles des retraites personnelles d'avant
   1983 (1972, 1976, 1977, 1982), que la réversion suivait.
5. *Hors de l'étape* : le tableau de `docs/avantages_non_contributifs.md`
   (« 3. La liste ») dit encore « absent » la majoration de 11,1 % et la
   majoration pour enfant à charge, que le modèle sert.
