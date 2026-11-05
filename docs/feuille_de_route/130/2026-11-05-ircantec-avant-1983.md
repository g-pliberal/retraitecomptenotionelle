# L'Ircantec d'avant 1983 : la table par année d'âge et l'exonération datée

**La demande.** Le 5 novembre 2026, la session d'orchestration confie à la file
M3 la décision 9 du propriétaire (« Ircantec : corriger deux erreurs d'avant
1983 ? Oui, sans urgence », `2026-11-03-decisions-du-proprietaire.md`) : les
deux erreurs du modèle que la lecture au droit du 3 novembre avait laissées
(`2026-11-03-carte-des-fiches-ircantec-lue-au-droit.md`, « Ce que l'étape
laisse »). Un commit par erreur, test et code ensemble, dans les deux moteurs.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; les index LEGI et JORF
  récupérés. Relues mot pour mot, dans LEGI, les rédactions de l'article 16
  de l'arrêté du 30 décembre 1970 du 9 février 1971, du 3 janvier 1976, du
  26 juillet 1977, du 30 septembre 1978 (LEGIARTI000006381606 à 609) et du
  31 août 1983 (LEGIARTI000006381610) ; dans JORF, l'analyse de l'arrêté du
  26 juillet 1983 (JORFTEXT000000837384). Les quatre premières donnent la même
  table, « AGES COEFFICIENTS […] 55 ans 0,43 60 ans 0,78 56 ans 0,50 61 ans
  0,83 57 ans 0,57 62 ans 0,88 58 ans 0,64 63 ans 0,92 59 ans 0,71 64 ans
  0,96 », et aucune durée n'y exonère ; la cinquième fixe les coefficients
  « désormais par trimestre », et n'exonère à la durée (6° c) et n'ouvre la
  seconde table (II) qu'« A compter du 1er avril 1983 ».
- **Le moteur lit la version de la date d'effet.** La fiche
  `coefficient_anticipation_ircantec` entre dans les fiches datées du paquet
  (`FichesDatees.NOMS`) ; `baremeIrcantec` (`bareme_ircantec` au jumeau) en
  rend les paramètres à la date d'effet de la pension, pour les trois régimes
  qui portent `abattement_points: ircantec`, comme `exonerationsAgircArrco` le
  fait de l'Agirc-Arrco. Aucune période ne change.
- **Première erreur, la table par année d'âge** (premier commit,
  `Ircantec : la table par année d'âge jusqu'au 31 août 1983`). Là où la
  version porte `coefficients_par_annee_d_age`, `coefficientParAnneeDAge` en
  rend la ligne de l'âge révolu, un dès soixante-cinq ans, au lieu de
  l'escalier. La seconde table, d'avril à août 1983, la lit à l'âge assimilé
  à soixante-cinq ans : soixante-cinq ans moins les trimestres manquants.
  Calculs à la main, sur un contractuel payé deux plafonds, né le 15 janvier
  1922, ses âges comptés de février :
  - parti à 60 ans et 9 mois, en novembre 1982 : la ligne de 60 ans, **0,78** ;
    l'escalier servait 0,78 + 3 × 0,0125 = 0,8175 ;
  - né en 1919, parti à 63 ans et 11 mois, en janvier 1983 : la ligne de
    63 ans, **0,92** ; l'escalier, 0,88 + 7 × 0,01 = 0,95 ;
  - au travail à 25 ans, parti à 61 ans et 3 mois, en mai 1983, avec 145
    trimestres pour 150 : 5 manquants, âge assimilé 65 − 5/4 = 63,75, la
    ligne de 63 ans, 0,92, contre 0,83 à son âge révolu, 61 ans : **0,92** ;
    l'escalier, 1 − 5 × 0,01 = 0,95 ;
  - né en 1923, parti à 60 ans et 9 mois, en novembre 1983, après la
    publication : l'escalier, **0,8175**, inchangé.
- **Seconde erreur, l'exonération servie trop tôt** (second commit). Là où la
  version n'a pas `duree_requise_par_generation`, avant le 1er avril 1983, le
  coefficient se lit à l'âge seul, quelle que soit la période : celle de
  l'IPACTE et de l'IGRANTE, qui porte la durée, et celle de l'Ircantec de
  1983, qui commençait au 1er janvier. Calculs à la main, au travail dès
  18 ans, plus de cent cinquante trimestres à soixante ans :
  - né en 1922, parti à 60 ans et 9 mois en novembre 1982 : **0,78** aux trois
    régimes, quand l'IPACTE et l'IGRANTE n'avaient aucun coefficient ;
  - parti à 61 ans et 1 mois en mars 1983 : la ligne de 61 ans, **0,83**, quand
    aucun des trois n'en avait ;
  - parti en avril 1983 : **aucun coefficient**, le 6° c) vaut ;
  - né en 1905, parti à 62 ans en février 1967 : la ligne de 62 ans, **0,88**,
    de la table que la version `ipacte_et_igrante` présume, sur les points de
    l'IPACTE et de l'IGRANTE, quand ils n'en avaient aucun.
- **Les tests** : `tests/test_ircantec.py`, deux tests neufs qui font
  liquider chaque cas au portage (`comparer-liquidation.mjs`) et à son jumeau,
  vus rouges, chacun de son erreur, puis verts ; la confrontation des versions
  aux périodes ne compare plus ce que le moteur lit dans la version même
  (`DE_LA_VERSION`), et dix-sept écarts déclarés s'en vont. La fiche perd ses
  deux approximations, et en déclare une, ci-dessous ; les notes des fiches de
  régime de l'Ircantec, de l'IPACTE et de l'IGRANTE le disent, celle de
  l'IPACTE et de l'IGRANTE corrigée : elle tenait qu'aucune de leurs pensions
  n'avait été liquidée avant 1983.
- **Ce qui bouge** : aucun des 930 témoins de simulation ; les pages du coût
  et des avantages, par le coût du passé (le cumul passé des scénarios 2, 4
  et 6, d'une unité), et le paquet, que GitHub refait avec ses chiffres
  ancrés.

## Ce que l'étape laisse

- **Ce que le texte ne tranche pas** : le II, publié le 31 août 1983 avec
  l'escalier et rétroactif au 1er avril, renvoie aux « coefficients de
  réduction prévus au paragraphe Ier » ; d'avril à août 1983, le modèle y lit
  la table, en vigueur à la date d'effet, déclaré en approximation de la
  version `structure_financiere_1983` (jusqu'à 3,75 points, si la caisse
  lisait l'escalier). Avant 1971, la table de l'IPACTE et de l'IGRANTE reste
  présumée, comme la fiche le disait : les arrêtés du 12 décembre 1951 et du
  17 février 1960 ne sont pas dans l'index LEGI.
- **La même classe ailleurs** : les coefficients de l'Agirc et de l'Arrco de
  1955 au 31 mars 1983, que le modèle lit au trimestre, sont à relire de même
  — par année d'âge ou par trimestre —, ce que cette étape n'a pas fait.
