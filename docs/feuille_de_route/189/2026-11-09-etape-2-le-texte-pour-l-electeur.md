# Étape 2 : le texte pour l'électeur

**D'où elle part.** Le propriétaire, le 9 novembre 2026 : « On est trop
technique, trop long, trop nerd. Il faut quelque chose qui donne envie à tous
les électeurs. » Il arrête le même jour le principe (décision 90), six
arguments et deux cartes de constat, une information à la fois, sans
« notionnel », « répartition », « scénario » ni « valeur actuarielle ». La
session a confronté chaque phrase aux décisions 1 à 90 et au catalogue, lui a
montré le texte exact, et ne l'a écrit qu'avec son accord ; il a changé la
phrase sous le titre.

**Ce qui est fait.**
- **L'accueil.** Le titre : « Chaque pension vaut ce qui a été cotisé. » ;
  dessous : « Une égalité de traitement pour tous et une protection pour les
  plus fragiles. » (consigné à la décision 90 du programme). La baisse n'y
  est pas : elle reste à la question « Ma retraite va-t-elle baisser ? ».
  Six arguments, avant le formulaire du simulateur désormais :
  « 1 compte à votre nom, en euros » ; « 5 % de votre salaire, placés à votre
  nom », qui reviennent aux héritiers avant la retraite ; « 1 050 € par mois
  au minimum pour qui vit seul, 800 € chacun en couple », dès 65 ans, sans
  regarder les revenus du conjoint, avec un lien vers la réponse qui dit
  l'avance reprise sur la succession ; « Vos enfants et petits-enfants auront
  leur retraite » ; « 1 règle fixée une fois pour toutes, plutôt que des
  réformes à répétition » ; « 1 € cotisé, les mêmes droits pour tous.
  Cheminot ou salarié du privé : dès 2026, le même compte, à la même règle. »
  La description des moteurs de recherche, le texte et l'image d'aperçu
  (`moteur/apercu.png`) suivent le titre.
- **Ce qui en part.** « 18 % + 5 % », « le même taux pour tout le monde »
  (que la décision 48 dément jusqu'à l'intégration de l'Agirc-Arrco),
  « 100 % de ce que vous avez cotisé vous revient » (question 4 de
  `186/2026-11-08-site-etude.md`) ; « Pas de trimestres, pas de barèmes, pas
  de surprise » ne reste qu'à « Le saviez-vous ? ».
- **Partager**, six cartes : « 4,1 milliards d'euros », ce que les impôts
  paient en 2026 pour les retraites de la SNCF et de la RATP (3 225,8 et
  885,6 M€, programme 198 du PLF 2026) ; « 2,2 milliards d'euros »
  d'excédent à la CNIEG, que les factures d'électricité et de gaz continuent
  de remplir. Ce chiffre entre au dépôt, lu à la délibération de la CRE
  n° 2026-14 (`data/reference/regimes/excedent_cnieg.csv`, manifeste
  `cre_deliberation_2026_14`, `tests/test_constats.py`) ; les deux passent au
  paquet, sous `constats` (version 43), où les cartes les lisent. Le budget
  de lecture de la page monte de 340 à 440 mots.
- **Le catalogue** : neuf entrées neuves, chacune sur un contrôle existant ;
  huit retirées avec leurs phrases ; celle de « Pas de trimestres… »
  renommée pour « Le saviez-vous ? », seule page qui la porte encore.
- **La suite rouge du matin** : le test d'écran de `cout/` mesurait la page
  avant que les polices de la feuille entière soient chargées ; le pilote
  les attend (`tests/js/ecrans.mjs`).

**Quatre phrases reformulées, et pourquoi.** « Une réforme tous les cinq
ans » n'avait pas de source, et le tableau de la même page en compte une tous
les huit ans. « Dès 2026, la même règle » n'est vrai que du compte : la
complémentaire du privé garde ses règles jusqu'à son intégration (décisions
40, 43 et 48). La part placée ne revient aux héritiers qu'avant la retraite ;
ensuite, elle est une rente. Et l'État ne verse plus rien aux régimes de la
SNCF et de la RATP : il rembourse la Cnav qui les équilibre (`docs/regimes.md`),
d'où « vos impôts paient pour les retraites de ». La phrase du propriétaire,
« une protection pour les plus fragiles », tient : elle ne promet aucun
montant, et le plancher (décision 45) comme les droits gardés des accidents
de la vie (décisions 7, 57, 58 et 78) la portent.

**Ce qui reste.**
- Le texte des autres pages, « ce que chaque page dit d'abord », sur l'avis
  du propriétaire.
- Sur Partager, la carte « Le taux » (« 18 % + 5 % de cotisation retraite,
  pour tout le monde ») et le texte prêt à coller (« 18 % de cotisation au
  lieu de 28 % ») : la décision 48 les dément, comme elle démentait l'accueil.
- Le nom du site, « Retraite à comptes notionnels », sur le bandeau, les
  onglets et l'image d'aperçu : le jargon que l'accueil a quitté.
- Hors de l'étape, ce qui attend le modèle ou une décision : la réversion
  gardée, la décision 89, le nombre des pensions qui montent, le résumé « En
  bref » du simulateur, les appels à adhérer ou à donner.
- Les 4,1 Md€ sont les crédits du projet de loi de finances ; la loi votée
  n'est pas au dépôt.
- La copie de partiliberalfrancais.fr/retraite/ se met à jour à la main.
