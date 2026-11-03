# La carte des fiches : les coefficients d'anticipation de l'Agirc-Arrco lus au droit, neuvième lot

**La demande.** Le 3 novembre 2026, la session d'orchestration confie à la
file E le lot que le précédent avait désigné : la fiche de l'Agirc-Arrco sur
la baisse pour départ anticipé, `coefficients_anticipation_agirc_arrco`, à lire
au droit texte par texte et à mettre dans `LUES_AU_DROIT`, sans toucher au
code du modèle ; et dire ce que la lecture ajoute à la question qui attend le
propriétaire, l'ordre de la majoration pour enfants et du coefficient. Le
moteur lit les versions de cette fiche à la date d'effet de la pension (ce qui
exonère) : aucun chiffre du modèle ne bouge.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; les index LEGI et JORF
  récupérés, à jour de l'incrément du 2 novembre, et du 3 pour le JORF ;
  `textes.py --inscrire`, aucune rédaction nouvelle.
- **Le test d'abord.** La fiche entre dans `LUES_AU_DROIT`
  (`tests/test_carte.py`), vu rouge de ses quatre manques ; dans
  `tests/test_agirc_arrco_au_droit.py`, qui tient désormais les deux fiches de
  l'Agirc-Arrco, six tests neufs, vus rouges faute de versions et
  d'approximations : les versions se coupent aux neuf jours où un texte change
  la règle, chacun cité ; depuis le 1er avril 1983, toutes portent ce que le
  moteur lit ; les quarante lignes de la table des âges (accord de 2017,
  article 84, 2) sont l'escalier du portage (`liquider.js`) et la formule de
  l'accord Arrco de 1996 ; les vingt de la table des trimestres manquants
  (article 85, 3), ses vingt dernières ; l'âge que la caisse servait de 2011 à
  2018, de 65 ans et 4 mois à 67 ans, est celui des données ; chaque écart du
  modèle est déclaré. Le texte de 1983, daté du jour qu'il nomme, fait aussi
  tenir le test qui veut chaque version née de son texte.
- **Les textes**, dans les copies de la caisse : l'accord du 17 novembre 2017,
  articles 84, 85 et 102 ; l'avenant n° 15 du 16 mars 2023 et sa circulaire
  2023-03-DRJ ; la convention de 1947 (annexe I, articles 6, 8 et 9 ; annexe V)
  et l'accord de 1961 (annexe A, articles 18 et 19 ; annexe E), mis à jour au
  1er janvier 2018 ; au recueil des accords, l'accord Arrco du 25 avril 1996
  (article 10), ceux du 10 février 2001, du 13 novembre 2003 (et sa copie), du
  16 juillet 2008, du 23 mars 2009, du 25 novembre 2010, du 18 mars 2011, du
  13 mars 2013 et du 30 octobre 2015 ; la circulaire 2020-02-DRJ, fiches 3 et
  4. Au Journal officiel : les avis d'extension des avenants de 2002 et 2003,
  les arrêtés du 29 juin 2004, du 27 juin 2011 et du 11 juillet 2023 ; L.
  351-8 et L. 161-17-2, dans les rédactions de 2011. Les empreintes des copies
  sont celles du lot précédent, quand il les avait lues.
- **`coefficients_anticipation_agirc_arrco`**, du domaine de la décote et de
  l'étape qui liquide, approchée : dix versions, de trois. L'âge seul avant le
  1er juillet 1976, supposé ; le protocole de 1976 à l'Arrco ; la structure
  financière le 1er avril 1983, que seul le résumé de son agrément dit ;
  l'accord du 23 décembre 1996 le 1er janvier 1997 ; le régime unique de
  l'Arrco le 1er janvier 1999, sa table et, de 2001, l'AGFF ; l'accord du
  13 novembre 2003 le 1er janvier 2004, prorogé jusqu'au 30 juin 2011 ;
  l'accord du 18 mars 2011 et les annexes le 1er juillet 2011 ; la tranche C
  le 1er janvier 2016 ; le régime unifié le 1er janvier 2019 ; l'avenant n° 15
  le 16 mars 2023, où vont les deux exemples de la caisse. Six approximations,
  une lecture divergente sur l'âge de 2011 à 2018 (le texte fige la rédaction
  du 18 mars 2011, la caisse a servi la loi du 21 décembre 2011, le modèle
  avec elle), plus aucun texte à rattacher. La question ouverte des assurés
  dont la base n'est pas le régime général est levée : la caisse compte la
  durée « tous régimes de base confondus », comme le moteur.
- **Le cliquet des textes** ne bouge pas : les rédactions citées avaient déjà
  leur statut. **La carte** passe de 89 fiches à lire au droit à 88, de 527
  manques à 523. `conservation.py --depuis HEAD` dit changée la ligne de veille
  de la fiche, refaite depuis elle, ce que la référence figée admet.

## Ce que l'étape laisse

- **Des écarts du modèle, déclarés, que la lecture montre** (la file E ne
  touche pas au modèle) :
  - de 1983 à 2003, la structure financière n'exonérait que les salariés en
    activité, les chômeurs et quelques cas assimilés ; le modèle exonère tous
    ceux qui ont la durée ; déjà au propriétaire depuis le 18 octobre ;
  - de 2011 à 2018, l'Agirc n'exonérait pas les mères de famille ouvrières ni
    les travailleurs manuels, ni l'Arrco ces derniers ; le modèle les exonère
    partout ;
  - les mineurs de fond, sans coefficient dès 60 ans avec trente ans de mine
    (accord de 2017, article 85, 1) : le moteur ne les connaît pas ;
  - le report sans abattement des points de la tranche C d'avant 2016
    (article 102), que le modèle ne sert pas, déjà su ;
  - la table des trimestres manquants avant l'âge légal, que les textes
    n'ouvraient pas avant l'avenant n° 15 : sans effet dans le modèle ;
  - la complémentaire prise avant la base, renvoyée à la fiche
    `liquidation_regime_par_regime`.
- **À relire** : le texte et la date d'effet des avenants du 4 juin 2002 ; ce
  que l'Agirc exonérait de 2004 à 2011, et la table des trimestres manquants de
  1983 à 2011, dans les rédactions d'alors des annexes ; les accords de 1983,
  1990 et 1993, que seul le résumé de leur agrément dit.
- **Le paquet du site** porte les versions de la fiche : couper les versions le
  change, sans changer un calcul ; GitHub le refait, comme le tableau de bord.

## Ce que la lecture ajoute à la question de l'ordre

La question attend le propriétaire : calculer la majoration pour enfants avant
le coefficient d'anticipation, comme la caisse, ou après, comme le modèle. Le
texte ne la tranche pas : l'accord de 2017 applique le coefficient « aux points
de retraite inscrits au compte » (article 84, 2), et la majoration « de son
allocation » (article 94) ; les annexes de 2011 à 2018 écrivent le coefficient
de la même façon. C'est la caisse qui tranche, dans la circulaire 2020-02-DRJ :
la majoration pour enfants nés ou élevés « est calculée sur les droits de base
du participant sans tenir compte des coefficients d'anticipation
éventuellement appliqués » (fiche 4, II.2.1), et celle pour enfants à charge de
même (II.2.3). Trois précisions pour qui corrigera : « les coefficients
d'anticipation » comprennent celui des trimestres manquants et celui des
points de la tranche C d'avant 2016 ; la correction se date, l'Arrco dès 2012
et l'Agirc dès 2019 (guide n° 9 : « le régime Agirc en tient compte ») ; et les
majorations pour ancienneté des anciens régimes de l'Arrco vont en sens
inverse, la caisse les compte dans l'assiette du coefficient (II.4). Rien dans
ces textes ne contredit la caisse.

## Ce qui attend le propriétaire

La même question, que la lecture renforce : corriger l'ordre, la majoration
avant le coefficient, comme la caisse ? Avis : oui, dans une étape du modèle,
datée comme ci-dessus. Les écarts neufs (les catégories de 2011 à 2018, les
mineurs de fond) touchent très peu de monde : ils sont déclarés, sans urgence.
