# Étape 4, neuvième partie : la réversion d'avant 2004 que la retraite du survivant recalcule, et la révision de R. 353-1-1 à sa retraite

**Le 24 octobre 2026, la demande.** Le propriétaire, dans la deuxième vague des
sessions du jour : le premier point du bloc de l'étape — la réversion d'avant
juillet 2004 que la retraite du survivant, attribuée depuis, recalcule aux
règles de ressources de 2004, et la révision de R. 353-1-1, dont la dernière,
à sa retraite —, le point 2 du « Ce qui reste » de la septième partie. Les
champs que le bloc renvoie au site ne sont pas de cette session.

**Ce que dit le droit, lu le jour même** (journal de veille du 24 octobre,
« révision à sa retraite » ; fiche `reversion`).

- *La réversion d'avant juillet 2004.* « Lorsque le bénéficiaire d'une pension
  de réversion prenant effet avant le 1er juillet liquide un avantage personnel
  de retraite ou d'invalidité après cette date, ses droits à pension de
  réversion sont révisés pour tenir compte de la nouvelle condition de
  ressources et de la suppression concomitante des règles de cumul » ; sinon,
  elle continue d'être servie « selon ces règles » (lettre ministérielle du 22
  mars 2005, § 1), et « le nouveau dispositif doit être mis en œuvre à compter
  de la date d'effet de l'avantage personnel » (circulaire Cnav n° 2005/17,
  § 31).
- *La révision.* La réversion attribuée depuis « est révisable en cas de
  variation dans le montant des ressources », et « la date de la dernière
  révision ne peut être postérieure » de trois mois à celle où le survivant
  « est entré en jouissance de l'ensemble des avantages personnels de retraite
  de base et complémentaire », ni, quand il ne peut y prétendre, à ses soixante
  ans, puis à l'âge de L. 161-17-2 (R. 353-1-1, cinq rédactions de 2004 à
  2026 ; depuis 2026, sans les droits nouveaux du cumul emploi-retraite). La
  révision qu'ouvre une retraite « intervient donc à compter du premier jour
  du mois qui suit la date d'effet de cet avantage » (circulaire n° 2010/58,
  § 22) : retraites au 1er janvier 2008, révision au 1er février, « dernière
  révision (cristallisation) » au 1er avril (§ 24). Avant le 30 juin 2010, au
  mois qui suit le constat de la caisse, à la dernière révision au plus tard
  (circulaire n° 2006/37, § 6), à la date d'effet de la retraite du régime
  général (circulaire n° 2006/6, § 121). Après la dernière révision, « aucun
  changement de ressources ou de situation familiale n'est pris en compte »
  (exposé « Condition de ressources »).
- *Aucun exemple chiffré* : les circulaires datent la révision sans la
  chiffrer. Leurs quatre exemples datés — n° 2010/58, § 24 ; n° 2005/17,
  § 322, deux cas ; n° 2006/37, § 6, le second cas, en écart connu, le
  modèle ne sachant pas le jour du constat — entrent au témoin des exemples
  officiels.

**Ce qui est fait.**

- *Le modèle* (`droit/reversion.py`, `_revision_a_la_retraite`, et son
  jumeau) : la retraite que le survivant date après la date d'effet revoit la
  réversion du régime général et des régimes alignés — ce jour même, quand elle
  recalcule aux règles de 2004 une réversion d'avant juillet 2004 qu'elle
  trouve servie ; le mois qui suit, quand elle révise une réversion attribuée
  depuis. La réversion d'avant le plafond, minimum et maximum faits, s'y réduit
  du dépassement du plafond de la version de ce jour, au SMIC de son année —
  la dernière publiée, pour une année à venir (`_annee_du_plafond`) —, ramené
  aux euros de l'année des montants par les coefficients des pensions ; à côté
  d'elle, toutes ses ressources, retraites comprises, celles de son ménage
  quand il est formé, les réversions des autres régimes de base. La majoration
  de 10 % suit, celle de 11,1 % lit la réversion revue. La ligne écrit
  `revision_effet`, `reduction_de_la_revision` (négative quand la révision
  ajoute) et `derniere_revision`, trois mois après sa retraite, ou la date
  d'effet quand ses retraites la précèdent de plus (`_derniere_revision`).
- *Les tests* : dans `test_reversion.py`, dix de plus — le recalcul de 2004 et
  la révision, posés à la main (2 080 × 7,61 € en 2005, 2 080 × 10,15 € en
  2020, ramenés aux euros de 1999 et de 2015) ; trois enfants et le dixième
  du minimum ; le ménage formé avant sa retraite, et après sa dernière
  révision ; une révision à venir, au dernier SMIC publié ; les retraites qui
  précèdent la date d'effet ; quatre saisies aux deux moteurs, au bit près.
  Dans `test_oracle.py`, deux grandeurs neuves
  (`dates_de_revision_de_la_reversion`,
  `dates_de_derniere_revision_de_la_reversion`) et la retraite du conjoint dans
  la carrière d'un exemple. Deux témoins de simulation,
  `reversion_recalculee_a_sa_retraite` et `reversion_revisee_a_sa_retraite`.
- *La fiche* `reversion` : les rédactions de R. 353-1-1, de R. 815-40 et de
  R. 815-42 citées par leurs versions, qui ne restent plus à rattacher ; les
  approximations ; le cliquet des textes descend à 9 558.

**Les mesures.** Aucune pension ne bouge, sur 895 témoins, ni aucun rendu de
page ; une seule réversion se revoit, sans rien perdre : le veuf qui prend sa
retraite en janvier 2029 (`reversion_enfants_jusqu_a_sa_retraite`), révisé en
février, ses 12 000 € de retraites sous le plafond. Les deux témoins neufs : la
veuve de 1999 retraitée en mars 2008 garde 3 039,85 € de ses 5 937,02 € (en
euros de 1999) ; le veuf de 2015, remarié en 2018, retraité en juillet 2020,
3 080,08 € de ses 7 317,99 € (en euros de 2015), sous le plafond du ménage.

**Ce qui reste.**

1. *De la révision* : quand le ménage se forme ou se défait, ou que les
   ressources varient, avant sa retraite ou sans elle ; la dernière révision à
   l'âge légal du survivant qui ne peut prétendre à aucune retraite ; la
   révision de la majoration de 11,1 % (R. 353-13) et celle de la
   complémentaire des indépendants ; la retraite d'inaptitude substituée à la
   pension d'invalidité du survivant, qui recalcule aussi la réversion d'avant
   2004. La révision s'écrit sur la ligne, comme la limite de cumul revue, et
   non en événement de l'échéancier qui rappelle `liquider`
   (`docs/architecture.md`, § 7.4).
2. *Au site* : la phrase de la carte qui dirait la révision, son montant et sa
   date (`revision_effet`, `reduction_de_la_revision`, `derniere_revision`),
   comme celle de la limite de cumul.
3. Le point 3 de la septième partie, et ceux de la huitième.
