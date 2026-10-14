# Les modèles publics français : treize lignes déjà lues, et closes

**Le 14 octobre 2026 : treize lignes réservées (7ec59db), puis dépouillées.**
Ce sont les modèles publics français du sas : TRAJECTOiRE, `legiretraite` et
EDIFIS de la DREES, Til-Pension et PENSIPP de l'IPP, Destinie 2, les exemples
de Catala, et six calculateurs de la société civile (Aurain, « Quand
pourrai-je partir », Sud Éducation, devcrafting, le tableur de vérification,
nosretraites). Toutes passent à `epuise`.

- *Ce qu'il y avait à en tirer l'était déjà.* L'action 137 les a lues en
  entier du 1er au 11 octobre pour le registre des modèles
  (`data/reference/referents.yaml`) : chacune y a ses écarts, ce qu'elle fait
  mieux et le chantier de l'action 138 qui le reprend ; TRAJECTOiRE et
  Destinie 2 ont été exécutés à part, leurs sorties en témoin. Le sas
  n'avait pas été vidé : ses lignes restaient `a_explorer`. Chaque note dit
  maintenant, en une page, ce que la source apporte, ce que le dépôt en prend
  et ce qui la contredit, en renvoyant à l'entrée du registre.
- *Ce qui a été vérifié ce jour.* La tête de chaque dépôt, par
  `git ls-remote` : douze n'ont pas bougé depuis le commit lu. Seul
  `lfi-site` a avancé (`94616bc` → `0121861`, six commits du 1er au 7
  octobre), sur des pages étrangères à la retraite : rien sous
  `src/lib/boite-a-outils/retraite`. Les séries du dépôt que les écarts citent
  (âge d'ouverture et durée requise par génération) sont inchangées et
  certifiées : les écarts tiennent.
- *Ce qui contredit le dépôt : rien.* Tous les écarts sont ceux des modèles —
  la loi du 30 décembre 2025 manquante (TRAJECTOiRE, et la durée de
  `legiretraite`), un droit arrêté en 2011, 2014 ou 2020, la génération 1961
  mal ouverte (deux calculateurs), Catala sur 1967.
- *La trajectoire d'emploi de TRAJECTOiRE*, que sa ligne voulait confronter à
  celle de l'action 46, vient du COR comme la nôtre : rien à confronter hors
  de sa population, au CASD (138.14).
- *Ce qui attend le propriétaire*, déjà au registre en `a_trancher` : trois
  choix de PENSIPP pour la proposition (règles de départ, crédits de périodes
  non cotisées, forme du diviseur), deux de TRAJECTOiRE, un de Sud Éducation
  et un de devcrafting (les systèmes à points de 2019 et 2020).
- *Aucune saisie à proposer* : le lot n'a pas de simulateur. Les trois
  saisies proposées par le lot de la Cnav (`cnav_arrierees_artiste_auteur`)
  attendent toujours la réponse du propriétaire.
- *Laissées aux autres sessions* : `openfisca_france_pension` (action 153),
  et, faute d'empiéter, les lignes du net et de l'impôt (LexImpact, TaxIPP,
  Saphir, EUROMOD, `ir-catala`, Tilloy : 138.3), de la page Coût (Scherrer,
  Corral : 138.5 et 138.7) et des diviseurs étrangers (138.11).
- *Ce que le lot suivant trouvera* : sur les trente-huit lignes de règles, de
  code et de documents encore `a_explorer`, vingt-sept ont déjà leur entrée
  au registre, lue le 4 ou le 14 octobre ; elles se ferment comme celles-ci, tête du dépôt vérifiée, une fois
  les sessions de leur zone finies. Restent vraiment à lire : les deux
  documents du COR, F33841 (138.12), les cubes du SRE, deux jeux de la DREES,
  Gallica, les points d'entrée JSON et WordPress des caisses ; Légifrance
  refuse toujours.
- *Fichiers.* `data/sources_a_explorer.yaml`, et cette note. Ni fiche, ni
  témoin, ni page, ni journal de veille : le scénario 1 n'est pas touché.
