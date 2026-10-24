# Étape 4, huitième partie : les parts de la majoration pour enfant après la date d'effet, l'étudiant, l'apprenti et l'enfant infirme jusqu'à vingt ans, le régime qui la sert

**Le 24 octobre 2026, la demande.** Le propriétaire, dans le lot de onze
sessions du jour : le point 1 du « Ce qui reste » de la septième partie — de
la majoration pour enfant, l'étudiant, l'apprenti et l'enfant infirme à charge
jusqu'à vingt ans, l'enfant de seize ans à la fin de 2015, l'enfant né après
la date d'effet (R. 353-10), le régime qui la sert (D. 173-21-7), un exemple
chiffré —, et son point 4 : `docs/avantages_non_contributifs.md` disait
toujours « absent » la majoration forfaitaire pour enfant à charge. Aucune
session n'y avait touché depuis le 9 octobre.

**Ce que dit le droit, lu le jour même** (journal de veille du 24 octobre,
« parts, prolongation, régime » ; fiche `majoration_forfaitaire_reversion`).

- *Les parts après la date d'effet.* « La majoration est due à la date
  d'entrée en jouissance de la pension de réversion si, à cette date, les
  conditions d'ouverture du droit à cette majoration sont remplies ou à
  compter du premier jour du mois suivant la date à laquelle ces conditions
  sont satisfaites » (R. 353-10) ; l'enfant qui « redeviendrait à charge après
  avoir cessé de l'être » la rouvre de même (circulaire Cnav n° 76/88, § 6).
  Née le 1er janvier 1988, elle a rejoint ce jour-là les réversions déjà
  servies, aux survivants de moins de soixante-cinq ans (§ 3 et 31).
- *2016.* Le 1er janvier, R. 353-9 renvoie à R. 161-4 au lieu de R. 313-12
  (décret n° 2015-1865, article 10, 18°, et article 12, sans disposition pour
  les majorations en cours) : l'enfant mineur est à charge, celui de seize ou
  dix-sept ans le redevient.
- *Vingt ans.* R. 313-12 : seize ans, dix-huit pour l'apprenti, vingt pour
  l'étudiant et l'enfant infirme ; l'apprenti, vingt ans « quel que soit le
  niveau de leurs rémunérations » depuis la circulaire n° 44/94 ; depuis 2016,
  L. 161-1 et R. 161-4 : le mineur, et jusqu'à vingt ans l'étudiant et
  l'enfant infirme, l'apprenti scolarisé « considéré poursuivre [ses] études »
  (exposé « Qualité d'enfant à charge »).
- *Le régime qui la sert.* « Par priorité, [...] le régime auquel l'assuré a
  été affilié en dernier lieu si ce régime sert la majoration », de plusieurs
  à la fois celui de « la plus longue durée d'assurance » (D. 173-21-1 depuis
  1988, D. 173-21-7 depuis juillet 2017, avec la liquidation unique,
  R. 173-17-3 depuis 2026), à égalité la réversion la plus élevée (fiche
  n° 7).
- *L'exemple chiffré.* Aucun n'est publié : ni les exposés de la Cnav, ni ses
  circulaires n° 76/88 et n° 44/94, ni la circulaire RSI n° 2007/061, ni la
  fiche F13104 de service-public, qui dit « moins de 21 ans » et compte la
  majoration au plafond, là où la Cnav dit vingt ans et la réduit dans la
  proportion de la réversion réduite (D. 353-2) ; le modèle suit la caisse.

**Ce qui est fait.**

- *Les parts* (`droit/reversion.py` et son jumeau) : chaque enfant a ses
  jours à charge, version par version (`_jours_a_charge`), et ses parts, de la
  date d'effet, du 1er janvier 1988, ou du mois qui suit
  (`_parts_de_l_enfant`) ; la majoration s'attribue au début de la première
  part, où se lisent l'âge du survivant, ses retraites et son union, et son
  montant de 1988 se ramène aux euros d'une année des montants antérieure par
  les coefficients des pensions. Les étapes disent ce qui commence comme ce
  qui cesse.
- *Vingt ans* : `chronologie.prolongations_de_la_charge` lit les études de
  l'enfant (`periode_d_etudes`, sorte neuve du vocabulaire), son contrat
  d'apprentissage (un emploi qui porte `apprentissage`) et son infirmité (la
  décision médicale `infirmite`) ; la fiche porte `enfant_prolonge_moins_de_ans`
  à chaque version. Sans eux, la présomption neuve
  `charge_jusqu_a_l_age_limite` ; la part qui commence ou revient,
  `majoration_demandee_des_sa_condition`.
- *Le régime* : `_regime_de_la_majoration`, la dernière année cotisée de
  chaque régime (`_dernieres_affiliations`), puis la durée, puis le montant ;
  l'aide `_carriere` des tests prend une affiliation qui existe,
  `salarie_prive_non_cadre`, que rien ne routait jusqu'ici.
- *Les tests* (`test_reversion.py`, douze de plus, et
  `tests/js/moteur.test.js`) : la majorité de 2016 qui rouvre la part,
  l'enfant né après la date d'effet, 1988, les quatre prolongations, les trois
  dernières affiliations, l'exemple de 2026 posé à la main (2 × 12 × 113,59 ×
  4 001,60 / 5 400 = 2 020,19 €), et cinq saisies aux deux moteurs, au bit
  près.
- *Le point 4* : la ligne de l'inventaire passe à « déclaré », comme la
  réversion, sa base légale à L. 353-5, sa création à 1988 ; le cliquet des
  textes descend à 9 581.

**Les mesures.** Aucun des 892 témoins de simulation ne bouge : aucun n'a
d'enfant de seize ans à la fin de 2015, de décès d'avant 1988 avec enfant, ni
de carrière qui finisse dans un autre régime aligné avec un enfant à charge.

**Ce qui reste.**

1. *Au site* : le champ qui dit l'enfant étudiant, apprenti ou infirme, et
   jusqu'à quand ; la saisie qui refuse l'enfant né après le départ, que la
   majoration compte ; la page, qui tait une majoration nulle à la date
   d'effet et servie ensuite.
2. *De la majoration pour enfant* : l'apprenti d'avant le 18 mai 1994, à
   charge jusqu'à dix-huit ans sous 55 % du SMIC ; l'enfant aux études
   interrompues par la maladie, jusqu'au 30 septembre de ses vingt et un ans
   avant 2016 (R. 313-14) ; la majoration des exploitants agricoles
   (L. 732-50 du code rural), hors du modèle.
3. *Hors de l'étape* : la ligne de la majoration de 11,1 %, dite « absent »
   au tableau, est l'une des dix que les comptes comblent ; la passer à
   « déclaré » récrit la phrase du § 2 qui les compte.
4. Les points 2 et 3 de la septième partie.
