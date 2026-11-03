# Étape 2, sixième et dernière partie : la CRFM de Mayotte, les élus du Pacifique et les régies ferroviaires, lus et mis en fiche ; les limites de l'étape

**Le 16 octobre 2026 : trois fiches de règles, `pas_encore_modelisee`, pour les
trois derniers régimes hors champ de l'étape — `crfm_mayotte_pension_unique`,
`elus_nouvelle_caledonie_cafat`, `regies_ferroviaires_pensions_en_extinction` —,
leurs lignes d'inventaire corrigées, et le paragraphe de l'étape aux limites
(`docs/limites/4-regimes-incomplets.md`). Aucun moteur, aucun chiffre de page
ne bouge. L'étape 2 est close.**

Demande : la vague ter du 16 octobre, session 12, « action 145, étape 2. Les
trois régimes hors champ […] lus à la source et mis en fiche, documentés sans
être calculés ; puis, si l'étape le permet, ses limites (note `pacifique`), et
une nouvelle tentative sur LexPol et le Journal officiel de Wallis-et-Futuna ».

- *La méthode.* L'index LEGI et JORF du dépôt (à jour au 11 octobre), lu
  article par article ; pour la Nouvelle-Calédonie, deux décisions de justice
  sur Juridoc, citées, non gardées.
- *La CRFM de Mayotte.* La ligne d'inventaire tenait la caisse pour close. La
  loi n° 2001-616 (article 64-1, VII, depuis la loi n° 2007-148) et le décret
  n° 2012-1256 disent plus : l'agent intégré dans une fonction publique reçoit
  une **pension unique** du régime d'accueil, dont la part des services d'avant
  l'intégration suit le règlement de la caisse au 1er janvier 2006, sur les
  derniers émoluments tenus six mois, préliquidée par la caisse puis revalorisée
  comme les pensions du régime d'accueil ; il garde l'âge de la caisse, 55 ans
  et une limite à 60 ans (rapport sur l'ordonnance n° 2012-790), sauf option,
  irrévocable, pour ceux de son corps ; ses enfants nés avant l'intégration
  comptent selon la caisse. Les pensions des non-intégrés sont versées depuis
  2011 par la CNRACL ou l'État (décret n° 2013-255). Le règlement de la caisse,
  adopté localement, reste introuvable.
- *Les élus du Pacifique.* En Nouvelle-Calédonie, l'arrêt de la cour
  administrative d'appel de Paris du 1er février 2006 (n° 02PA01530) cite la
  délibération n° 431 du 22 juillet 1977 : affiliation obligatoire des élus
  indemnisés à la CAFAT, sauf pour qui garde un régime obligatoire (le
  fonctionnaire détaché en est exclu), rachat des mandats antérieurs, pris en
  charge par le territoire depuis la délibération n° 124 de 1981. Ce que le
  congrès et les provinces en ont fait depuis 1999 n'est pas lu. La Polynésie
  n'a pas de fiche : aucun texte du pays n'a pu être lu, et le contrôle de la
  carte refuse une fiche sans texte ; la ligne d'inventaire garde la presse.
- *Les régies ferroviaires.* Le règlement de la caisse, approuvé par l'arrêté
  du 13 mai 1996, est « disponible à la Caisse des dépôts », non publié. Lus :
  le reclassement à la SNCF des agents sous statut (ordonnance n° 58-1036), la
  validation des services d'Algérie (loi n° 64-1330), la garantie de l'État
  (loi n° 2003-1312, article 80, 23°), et L. 134-3, 3°, i et j : depuis 2025, la
  Cnav assure l'équilibre des régimes des chemins de fer d'Afrique du Nord et
  d'outre-mer et des régies, dès que leurs fonds propres sont négatifs.
- *LexPol et Wallis-et-Futuna, nouvelle tentative.* Toujours injoignables :
  `lexpol.cloud.pf` répond 502 au tunnel ou coupe la connexion ;
  `wallis-et-futuna.gouv.fr`, une réponse vide, en HTTP/2 comme en HTTP/1.1.
  Le proxy n'y est pour rien (son état est sain) : à tenter d'un poste.
- *Ce que le modèle ne fait pas*, et que les fiches nomment : la part de pension
  CRFM et l'âge de 55 ans des agents mahorais intégrés, simulés aux seules
  règles du régime d'accueil ; les mandats calédoniens indemnisés, qui valent
  des points de la CAFAT depuis 1977 ; les services d'outre-mer des anciens
  cheminots des régies. Au propriétaire de dire si le premier, qui touche des
  agents vivants, mérite un statut.
- *Les limites de l'étape*, écrites une fois : un paragraphe de
  `docs/limites/4-regimes-incomplets.md` range ce que les fiches de l'étape ont
  trouvé en trois familles (approchés, hors champ dont la loi garde une part,
  sans texte lisible).
- *Les tests.* `test_carte.py`, `test_contrats.py`, `test_textes.py`,
  `test_regle_de_chacun.py`, `test_donnees.py`, la suite rapide et
  `test_parcours.py` passent ; `regenerer.py`, lancé, ne déplace que des poids
  de fichiers, non commités. `inventaire.yaml` et `docs/regimes.md` sont refaits
  par leurs scripts.
- *Ce que devrait dire une page* : rien en dur ; la page Données lit les lignes
  d'inventaire corrigées.
- *Ce qui reste de l'action.* Aucune étape. Attendent : la décision du
  propriétaire sur les écarts des notes du 13, du 14 et du 16 octobre ; la
  lecture de LexPol et du Journal officiel de Wallis-et-Futuna, d'un réseau qui
  les joint ; le règlement de la CRFM, à demander à la CNRACL. L'action peut se
  clore quand le propriétaire aura tranché.
