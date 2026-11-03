# Étape 4, thème « Retraite personnelle de base » : les exposés et leurs références

**Le 3 novembre 2026, ce qui est fait.**

- *La lecture* : les 45 exposés du thème, relus par l'API à la version que le registre
  date, sous-thème par sous-thème, chacun confronté aux fiches de la carte qui portent
  ses règles — l'âge légal, la durée requise, le revenu annuel moyen, le taux, le taux
  plein à 65 ans, la surcote, le montant et le maximum, le minimum contributif, la
  majoration exceptionnelle, la carrière longue, le handicap, l'inaptitude,
  l'incapacité permanente, la retraite progressive, le cumul emploi-retraite, les
  anciens combattants, les mères de famille ouvrières, la retraite substituée à la
  pension d'invalidité ou à l'allocation aux adultes handicapés, la révision. Les
  fiches portent ce que les exposés disent, ou déclarent ce que le modèle n'en sert
  pas, sauf les quatre écarts qui suivent.
- *Les tableaux, confrontés aux séries* : `tests/test_cnav_exposes.py`, à la manière
  de `tests/test_cnav_baremes.py` — l'âge légal, depuis le 1er septembre 2026 et avant
  la suspension ; l'âge du taux plein ; la durée requise, depuis septembre 2026, avant
  la suspension, avant 2023 et avant 2003 ; la durée de proratisation ; le nombre
  d'années du revenu annuel moyen, des salariés et des indépendants ; l'âge de départ
  en carrière longue, par génération, sous les deux calendriers. Tout concorde, au mois
  près, décembre 1965 compris (soixante ans et huit mois) ; faussée, chaque table
  rougit.
- *Un écart corrigé, les deux moteurs* : R. 351-45, dans ses rédactions de 1993 et de
  1995, ne donne l'escalier de 151 à 159 trimestres aux nés de 1934 à 1942 que pour une
  pension prenant effet avant 2003 ; depuis, 160 trimestres « quelle que soit la date
  de naissance », sauf au né en décembre 1942 parti le 1er janvier 2003 (III), puis
  R. 351-27 depuis 2009 pour les nés avant 1949. L'exposé « Durée d'assurance pour le
  taux plein » le dit. Le modèle opposait l'escalier à toute date : 157 trimestres au
  né en 1940 parti en 2003. Le test, huit cas posés depuis le texte, passe par le
  portage et fait refaire chaque appel au jumeau Python (`droit_et_refait`) : vu rouge
  au portage, puis au jumeau seul. Aucun témoin ne bouge ; les chiffres ancrés du coût
  bougent à peine (2 761 à 2 763 Md € au scénario 2), que GitHub récrit. Fiche
  `duree_requise_par_generation`, et le cliquet des textes, deux rédactions de R. 351-45
  désormais citées.
- *Trois écarts déclarés* : le taux plein à 65 ans de L. 351-8 hors du 1° — l'aidant
  familial (1° bis), le parent d'un enfant handicapé ou aidant (6°, loi n° 2025-199),
  le parent de trois enfants né du 1er juillet 1951 au 31 décembre 1955 (loi
  n° 2010-1330, article 20) —, dans une fiche neuve, `taux_plein_a_soixante_cinq_ans`,
  pas encore modélisée ; la réduction de durée des appelés d'Afrique du Nord, de 1994 à
  2002 (R. 351-45, IV), dans la fiche des anciens combattants ; la garantie de D. 173-2
  — le régime spécial sert au moins ce que le régime général aurait servi pour ses
  périodes —, dans `docs/limites/3-systeme-actuel.md`.
- *Les sorts*, que les étapes 4 suivantes peuvent reprendre : un exposé est `recoupe`
  quand ses tableaux sont tout ce qu'il dit et qu'un test les confronte (l'âge légal, la
  durée requise, le nombre d'années, la carrière longue) ; `limite`, renvoyé aux fiches
  et aux limites qui portent ses règles et disent ce que le modèle n'en sert pas ;
  `hors_modele`, la caisse compétente. Une liste, une fenêtre, de même ; une définition
  du lexique, une procédure (les délais, les échanges entre régimes, le formulaire),
  `hors_modele`. Une référence prend les renvois des objets rangés qui la lient — les
  fiches des exposés `recoupe` pour elle —, et ceux des fiches qui la citent déjà par
  son numéro (70) ; une procédure pure que seuls lient le point de départ et la caisse
  compétente, `hors_modele`. Un avis de mise à jour, `hors_modele` : il date un
  changement d'objets qui ont chacun leur sort. En tout : 45 exposés (4 `recoupe`, 40
  `limite`, 1 `hors_modele`), 31 listes, 26 fenêtres, 400 références (391 `limite`,
  9 `hors_modele`) et 65 avis.

**Ce que la lecture a trouvé, sans écart.** La majoration du départ anticipé des
assurés handicapés, que la caisse sert aussi à qui part à l'âge légal sans l'avoir
demandé, était déjà déclarée dans sa fiche. Le plancher de 37,5 % du taux de qui part
avant l'âge légal par son compte professionnel de prévention n'est pas écrit dans la
fiche `inaptitude_invalidite_penibilite_amiante`, qui ne modélise pas le compte : à y
porter quand elle le sera. Les exposés de la retraite progressive, de l'incapacité
permanente et du minimum contributif annoncent des mises à jour qui attendent leurs
instructions (loi n° 2023-270, articles 17, 18 et 26) : la veille les dira.

**Pour la file D**, sans y toucher : les huit barèmes de Mayotte que l'étape 3 a
laissés à lire — `mayotte_minimum_contributif_bar.aspx`,
`mayotte_retraite_personnelle_minimum_plafond_retraite_bar.aspx`,
`mayotte_retraite_personnelle_montant_maximum_bar.aspx`,
`retraite_reversion_montant_minimum_mayotte_bar.aspx`,
`mayotte_retraite_reversion_montant_maximum_bar.aspx`,
`mayotte_retraite_reversion_plafond_ressource_bar.aspx`, `aspa_montant_mayotte_bar.aspx`
et `aspa_plafond_ressource_mayotte_bar.aspx` — sont à confronter aux valeurs que la
fiche `mayotte_pension_de_base` dit servir, avec le thème Mayotte de l'étape 4 ; aucune
règle n'a été changée.

**À la session du modèle**, les deux moteurs ensemble : le taux plein à 65 ans du parent
de trois enfants né de juillet 1951 à 1955, pour les pensions de 2016 à 2022, qui se lit
sur la carrière et les naissances que la saisie déclare (huit trimestres avant la
naissance, au plus huit dans l'année et les deux suivantes) ; la garantie de D. 173-2 ;
et, de l'étape 3, la revalorisation des pensions d'invalidité, à laquelle cette session
n'a pas touché. Aucun fichier d'une autre file n'a été changé.
