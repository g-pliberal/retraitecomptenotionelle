# Le jaune pensions du PLF 2027, lu : la part « retraite seule » n'y est pas année par année

Le jaune « Rapport sur les pensions de retraite de la fonction publique »
annexé au projet de loi de finances pour 2027 est en ligne sur budget.gouv.fr
depuis le 13 octobre, sous « PLF 2027 - Jaunes budgétaires » ; à 13 h 28, le
dossier de l'Assemblée ne le porte pas encore. budget.gouv.fr répondant
toujours 403 au cloud, le propriétaire l'a téléchargé depuis son téléphone et
déposé sur la branche `jaune-2027` : `34465.pdf`, 11 964 640 octets,
250 pages, créé le 12 octobre 2026, SHA-256
`73dd4a66051cd71bdf2c77eb5345a34f99f862330f0f20164c930492be2dbaf5`. Il n'est
pas commité sur `main` : une session qui en a besoin le reprend de la branche
tant qu'elle existe, ou du miroir de l'Assemblée quand il paraîtra, après en
avoir comparé l'empreinte.

**Ce qu'il dit du taux de l'État** (partie I, pages 19 à 24) : rien d'année
en année.

- Il actualise, sur l'exécution de 2025, l'« affichage alternatif » du jaune
  2026 : au taux du régime général sous le plafond (16,67 %), les
  contributions employeurs des civils et des militaires tomberaient de 54,9 à
  11,0 Md€, et la subvention d'équilibre serait de 43,9 Md€, 65,2 % des
  67,3 Md€ de recettes du CAS (figure 3A). Son texte écrit 41,5 Md€, que la
  figure et son propre pourcentage démentent.
- Il cite les deux décompositions connues, celle de la Cour (44,1 % civil,
  51,2 % militaire, en 2025) et celle de l'IPP (34,7 %, civils et militaires,
  en 2020), et impute leur écart de neuf points au taux de départ et au coût
  des avantages professionnels, l'IPP comptant en plus les bonifications des
  actifs servies après l'âge d'ouverture des droits. Il écrit que la Cour
  retraite le taux de 2026 (82,28 %) ; son tableau n° 15 part de 83,6 %, le
  taux d'équilibre de 2025, et `contribution_etat_retraite_seule.csv` garde
  la Cour.
- Il conclut qu'« il n'existe donc pas de taux consensuel », renonce à
  comparer le taux de l'État à celui du régime général, et annonce que la
  direction du budget poursuivra « dans les prochains mois », avec des
  groupes de travail, ses travaux vers « un taux d'équilibre après
  neutralisation de ce qui relève des dépenses de solidarité en s'appuyant
  sur une méthodologie applicable d'année en année ».

**La décision.** Rien ne change dans le modèle : `PartRetraiteSeuleEtat`
garde la proportion de 2025, et n'a pas à accepter plusieurs années tant
qu'aucune autre n'est publiée. Le point 1 attend les travaux annoncés, et au
plus tard le jaune du PLF 2028.

**Un recoupement, en passant.** Le tableau 14 du jaune, les taux de
contribution employeur de 2000 à 2026, recoupe année par année les séries du
modèle : l'État civil et les militaires de 2006 à 2026
(`contribution_employeur_public.csv`, `contribution_employeur_militaires.csv`),
la CNRACL de 2000 à 2026. Seul écart, 2013 : le jaune donne la moyenne de
l'année, 71,78 %, et le modèle le taux appelé, 74,28 %, la baisse ponctuelle
de décembre (44,28 %) étant déjà déclarée dans l'en-tête du fichier.

**Ce qui reste.**

- Le point 1, comme dit.
- Au propriétaire : la convention du jaune, le taux du régime général sous le
  plafond au lieu de celui de l'État, pourrait devenir une troisième valeur
  de `contribution_etat`, à côté de `entiere` et de `retraite_seule`. Le jaune
  la dit lui-même « une convention parmi d'autres possibles ».
- La mise à jour, sur le jaune 2027, des bonifications que
  `sre_jaune_pensions.py` tire du jaune 2026 (tableaux A-7, 50 et B-1) : une
  autre étape, dans la zone des données.
- La branche `jaune-2027`, que seul le propriétaire peut supprimer.
