# Étape 9, suite de la huitième partie : le plafond de 2027 de la SNCF, que rien ne fixe encore

**La demande.** Vague du 28 octobre 2026 : une session par tâche, que le
propriétaire ne suit pas pas à pas. Le point « le plafond de 2027 » du bloc
« Reprise » de la huitième partie (point 4 de « Ce qui reste » de la note
`2026-10-16-etape-9-maladie-sncf-et-mines.md`) : s'il n'est pas encore
publié, dire où et quand il le sera, pousser, s'arrêter. Il ne l'est pas.

**Ce que disent les textes, lus ce jour dans l'index LEGI.** La SNCF prélève
0,70 % « du montant trimestriel de la pension inférieur à un plafond fixé à
5 128 euros » (décret n° 2007-1056, art. 7, IV, LEGIARTI000052041125), plafond
« revalorisé dans les mêmes conditions que les pensions » (VII). La caisse ne
publie pas le plafond revalorisé (note du 16 octobre) : le dépôt le calcule,
4 × 5 128 € multipliés par chaque coefficient de `revalorisation_pensions.csv`
depuis le 14 novembre 2010 jusqu'au 1er janvier de son `annee`, 25 582 € en
2026 (`prelevements_remuneration.yaml`), et
`test_le_plafond_de_la_sncf_est_celui_du_texte_revalorise` le refait. Celui
de 2027 attend donc le coefficient du 1er janvier 2027. L. 161-23-1
(LEGIARTI000051289722, depuis le 1er janvier 2026) le fixe « par application
du coefficient mentionné à l'article L. 161-25 » ; L. 161-25
(LEGIARTI000031781092) le tire des « douze derniers indices mensuels » des
prix hors tabac publiés par l'INSEE « l'avant-dernier mois qui précède la
date de revalorisation » : ceux qui paraîtront en novembre 2026.

**Ce qui n'est pas publié, le 28 octobre 2026.**

- *Le coefficient.* Le barème « Coefficients de revalorisation des
  retraites » de la Cnav, lu ce jour par l'API de
  `scripts/fetch/cnav_revalorisation_pensions.py`, s'arrête au 1er janvier
  2026, 1,009 (circulaire 2025/29 du 22 décembre 2025).
- *La loi qui pourrait y déroger.* L'article 35 du projet de loi de
  financement pour 2027 (n° 3211, déposé le 1er octobre 2026), « Dérogation
  exceptionnelle aux modalités de revalorisation des pensions de retraite
  pour 2027 », lu aux données ouvertes de l'Assemblée nationale. Les pensions
  des régimes obligatoires de base, la SNCF comprise, y sont revalorisées
  selon le montant mensuel total, au 31 décembre 2026, des pensions de droit
  direct et dérivé de l'assuré, complémentaires comprises : du coefficient de
  L. 161-23-1 jusqu'à 1 260 € ; d'un coefficient réduit par décret, jamais
  sous un, jusqu'à 1 265, 1 270, 1 275 et 1 281 € (II). Au-delà, le
  coefficient est de un tant qu'un décret n'en fixe pas un autre, entre un et
  celui de L. 161-23-1, par tranches bornées à 2 000, 2 007, 2 014, 2 021,
  2 028 et 2 034 €, puis au-delà, chacune au plus le plus petit de la
  précédente ; ce décret peut paraître jusqu'au 31 octobre 2027, et vaut pour
  les pensions dues depuis le 1er janvier 2027 (III).
- *Le vote.* L'Assemblée nationale a rejeté le projet en première lecture le
  23 octobre 2026 (T.A. n° 358, dossier `PLFSS_2027`) ; le dossier du Sénat
  (`plfss2027`), mis à jour le 28 octobre, ne porte encore aucun texte.

**Ce que la convention du dépôt en ferait.** Le test prend, pour 2020, la
tranche d'une pension mensuelle de la taille du plafond (loi n° 2019-1446,
art. 81) : 2 132 € en 2026, au-dessus de 2 034 €. L'article 35 adopté tel
qu'il est déposé, le plafond de 2027 resterait à 25 582 € au 1er janvier, et
ne bougerait qu'au décret du III, s'il en vient un ; l'article tombé, il
suivrait le coefficient de L. 161-23-1. Cette convention reste
une lecture, qu'aucune source ne confirme : le VII revalorise un plafond, non
la pension d'un assuré, et la caisse ne dit pas comment elle l'applique.
L'écart, en 2020, tenait entre 1 % et 0,3 % ; en 2027, il irait de rien à
tout le coefficient.

**Où et quand il le sera.**

1. *La loi de financement pour 2027*, au Journal officiel, après la décision
   du Conseil constitutionnel : celle de 2026 a été promulguée le
   30 décembre 2025 (loi n° 2025-1403), celle de 2020, aux tranches, le
   24 décembre 2019 (loi n° 2019-1446). Elle dira si l'article 35 survit, et
   à quels seuils.
2. *Le coefficient de L. 161-25* : les indices des prix hors tabac que
   l'INSEE publiera en novembre 2026, le dernier celui d'octobre.
3. *La circulaire de la Cnav* sur la revalorisation du 1er janvier 2027, et
   sa ligne au barème, que `cnav_revalorisation_pensions.py` porte dans
   `revalorisation_pensions.csv` : les trois dernières ont paru du 22 au
   29 décembre ; celle de 2020, aux tranches, le 4 février (2020/9).
4. *Les décrets de l'article 35*, s'il survit : celui du II, b, et celui du
   III, jusqu'au 31 octobre 2027 ; le plafond de 2027 peut donc changer en
   cours d'année, à effet du 1er janvier.
5. *La CPRP SNCF* ne publie pas son plafond : rien à attendre d'elle, sinon,
   dans son avis de revalorisation de janvier, la manière dont elle applique
   les tranches, qui confirmerait ou démentirait la convention.

**Ce qui reste**, à la session qui reprendra le point, quand la ligne de 2027
sera au barème de la Cnav :

- relancer `scripts/fetch/cnav_revalorisation_pensions.py` ; des tranches en
  2027 lui demanderaient peut-être de les lire comme celles de 2020, son test
  d'abord (`tests/test_revalorisation.py`) ;
- le test d'abord : `annee: 2027` à la ligne de la SNCF de
  `maladie_regimes_speciaux` (`prelevements_remuneration.yaml`), et
  `test_le_plafond_de_la_sncf_est_celui_du_texte_revalorise` rougit si le
  coefficient de la tranche passe un ; puis le plafond et son commentaire
  (« 1,2472 et 25 582 € ») ; un coefficient de un ne change que l'année ;
- si l'article 35 survit, le décret du III, jusqu'au 31 octobre 2027, refait
  le plafond une seconde fois, et la convention se relit à l'avis de la
  caisse (point 5).
