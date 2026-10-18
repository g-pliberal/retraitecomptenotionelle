# Étape 8, quatorzième partie : le 2° de D. 732-110, II, et la réversion du régime dans la pension majorée de référence

**Le 18 octobre 2026, la demande.** Le premier reste de l'étape, dans l'ordre
du bloc « Reprise » : le 2° de D. 732-110, II, qui servait de 2009 à 2021 le
montant du chef (PMR1) à toutes les périodes de qui peut prétendre à une
réversion du régime, au modèle et dans le portage ; sa saisie, pour une
session des pages. Session 138.8 de la vague du 18 octobre.

**Ce que dit le droit** (journal de veille du 18 octobre, index LEGI).

- *Le 2°*, dans les rédactions de 2009, 2010, 2011 et 2016 de D. 732-110,
  II : « Pour tout ou partie des périodes d'assurance non salariée agricole à
  titre exclusif ou principal validées par les personnes susceptibles de
  bénéficier d'une pension de réversion prévue aux articles L. 732-41 à
  L. 732-46 » ; DM1 compte « les périodes définies aux 1° et 2°, ou au 3° »
  (D. 732-111). En 2009 et 2010, le 2° servait PMR1 même aux années de chef
  d'un chef de moins de dix-sept ans et demi. Les rédactions de 2022 et de
  2026, la PMR unique, ne l'ont plus.
- *La réversion se retranche* : la majoration est l'écart entre la PMR et
  « la somme des pensions de retraite et de réversion, servies à l'assuré par
  le régime » (D. 732-112, de 2009 à aujourd'hui).
- *Elle compte au plafond* : « l'ensemble des pensions de retraite et des
  pensions de réversion servies à l'assuré par les régimes de base et par les
  régimes complémentaires » (D. 732-114) ; « les pensions de droit propre et
  de droit dérivé » (L. 732-54-3).
- *La réversion de L. 732-41* va au conjoint survivant du chef, sous un
  plafond de ressources qui la réduit « à due concurrence du dépassement » :
  « susceptible d'en bénéficier » se lit comme veuf d'un assuré du régime,
  quelles que soient ses ressources, réversion nulle comprise.

**Ce qui est fait**, dans les deux moteurs.

- *La chronologie* : `reversion_agricole`, son `debut` (une date, comme le
  décès) et son montant `mensuel` en euros de cette date, positif ou nul, se
  déclare aux trois constructeurs et devient un acte de la caisse de l'assuré
  (`acte: reversion`, `regime: msa_non_salaries`), que
  `chronologie.reversion_agricole` relit et `Carriere.reversion_agricole`
  porte (`reversionAgricole` en JavaScript). Ni pension étrangère, ni
  présumée.
- *La règle* : `reversion_agricole_servie` (`reversionAgricoleServie`) dit ce
  que la réversion sert par an au mois des montants, revalorisée comme les
  pensions de base (L. 161-23-1), hors la revalorisation du jour où elle
  commence, celle de 2020 à la tranche de son seul montant ;
  `pension_majoree` la retranche de la PMR, la compte au plafond, et, de 2009
  à 2021, porte toutes les périodes dans DM1 dès qu'elle est ouverte. À la
  liquidation comme à chaque échéance que le modèle refait — la PMR de 2009
  des pensions prises avant, la PMR unique de 2022 —, puisque l'une et
  l'autre passent par `pension_majoree`. Le détail de l'avantage le dit :
  « moins 1 919,81 € de réversion du régime ».
- *La présomption* `pas_de_reversion_agricole` : au vocabulaire, au § 5.6 de
  l'architecture, dans la fiche `pension_majoree_reference`, qui la lit.
- *Les tests* : `tests/test_chronologie.py`, le fait et quatre saisies de
  plus dans la confrontation des chronologies ;
  `tests/test_minima_agricoles.py`, le 2°, la réversion retranchée et
  écrêtée, la réversion ouverte après le départ, et le résultat entier de
  trois veuves dans les deux moteurs. Le cliquet des textes descend d'une
  rédaction (9 677).

**Les mesures.** La conjointe collaboratrice de 1972 à 2016, veuve d'un
exploitant depuis mars 2010 : PMR1 sur ses 164 trimestres, 2 250,90 € de
majoration en février 2016 au lieu de 980,29 € ; avec 150 € de réversion par
mois, qui en servent 1 919,81 € par an en février 2016, 331,09 €. Veuve en
juin 2018, après son départ : rien ne change jusqu'en 2021 ; en 2026, sa
pension de base perd les 2 106,90 € que sa réversion sert. Tant que la saisie
ne la demande pas, aucun assuré du site n'est servi.

**La saisie, pour une session des pages** (liste « Un champ de saisie de
plus » de `moteur/CLAUDE.md`). Deux champs, offerts à qui a un statut de
non-salarié agricole : le mois où la réversion de la MSA commence
(AAAA-MM) et son montant mensuel brut à ce mois, zéro admis, à lire et
vérifier dans `saisie.py` et `saisie.js`, réécrits dans l'adresse, et passés
par les deux contextes au constructeur de la carrière :
`reversion_agricole={"debut": "2010-03", "mensuel": 150.0}`. Le formulaire
annonce la présomption : sans réversion déclarée, aucune n'est retranchée, et
de 2009 à 2021 le montant du chef ne va qu'aux années de chef et de
collaborateur de 1999 à 2008.

**Ce qui reste**, de l'étape, dans l'ordre du bloc « Reprise » :

1. La saisie de la réversion, ci-dessus (session des pages).
2. La PMR revue quand les ressources changent (D. 732-114 : « Toute
   modification de la situation familiale ou du montant des ressources donne
   lieu à une révision », au premier du mois qui suit) : entre autres, la
   réversion ouverte après le départ d'une pension prise de 2009 à 2021, que
   le modèle ne retranche, ni ne sert au 2°, qu'à partir de 2022.
3. La durée de chef reconstituée de D. 732-110, III.
4. Ce que la réversion déclarée permet désormais de servir aux plans de 1997
   à 2008, et que leur fiche déclare non servi : la condition de ne pas en
   être titulaire à la date d'effet (D. 732-118), le minimum A de vingt
   points de qui reçoit la revalorisation de la réversion (D. 732-116), et la
   majoration de la réversion de D. 732-147.
5. Inchangés : les points 2 et 3 de « Ce qui reste » de la note « points des
   conjoints » ; à la fin de l'étape, la fiche `complement_differentiel_rco`.
6. Au propriétaire, inchangés : le montant de la MSA pour 2015 à 2017 et
   2019, depuis un poste qui atteint l'archive du web ; les seize points
   d'une année de conjoint d'avant 1999.
