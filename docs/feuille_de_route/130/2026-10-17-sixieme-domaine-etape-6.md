# Le sixième domaine, étape 6 : le coût du complément

Session 11 de la vague du 17 octobre 2026, sans le propriétaire. L'étape 6 du
gabarit (`2026-10-14-sixieme-domaine-mesure.md`) : ce que coûte le complément
de l'apprentissage, que le FSV puis la branche vieillesse versent. Aucun
fichier des pages ni de la saisie ne bouge : la page Droits non cotisés lit
l'inventaire et la liste des retraits dans le paquet, que GitHub refait.

## Ce qui est fait

- **La mesure par retrait** (`avantages.py`) : une onzième neutralisation,
  `apprentissage`, par la table. Le scénario 1 sans la fiche `apprentissage`
  (`fiches_datees.sans`) ne sert plus le complément : `version_aux_dates`
  rend `None` sans fiche, et le contrat ne valide plus que ce que ses salaires
  portent, sans qu'aucun code du moteur change. `recalculer` saute la carrière
  qui ne déclare aucun contrat (`compter._contrats`) : aucun cas type de la
  grille n'est apprenti, et l'agrégat ne bouge pas.
- **Ce que le complément vaut à un apprenti**, posé à la main
  (`tests/test_avantages.py`). Payé quelques centaines d'euros de juillet 2014
  à décembre 2016, l'apprenti y perd ses dix trimestres (D. 373-3), et rien
  d'autre. Salarié ensuite jusqu'à soixante-quatre ans, il a sans eux 180
  trimestres pour 172 dus : sa pension n'en dépend pas. Salarié jusqu'à
  cinquante ans et parti à soixante-sept, l'âge où la décote s'annule, il a sa
  pension du régime général dans le rapport de 134 à 124 (L. 351-1), sa
  complémentaire inchangée. Le complément ne vaut qu'aux carrières
  incomplètes.
- **Ce qu'il coûte en pensions** : presque rien encore. Né en 2014, il vaut
  pour des apprentis de seize à vingt-neuf ans, sauf exceptions
  (service-public.gouv.fr, fiche F2918, vérifiée le 8 septembre 2026), dont la
  plupart n'atteindront l'âge légal qu'après 2050.
- **Ce que le payeur verse** ne s'isole dans aucune publication lue. Le
  tableau 1 des comptes du FSV (annexe 2 du PLFSS 2024) le fond dans une ligne
  « Au titre de la formation professionnelle des périodes d'apprentissage et
  du service national » : 305 M€ en 2022, sur 13 529 de cotisations prises en
  charge. Le seul montant de l'apprentissage seul est une régularisation de
  « près de 0,2 Md€ » en 2021, au titre de 2015 à 2020. Depuis 2022, le
  versement est forfaitaire (D. 373-4, rédaction du décret n° 2022-652) :
  35 % (arrêté du 25 avril 2022, article 1) du nombre d'apprentis payés moins
  de 33 % du SMIC dans l'année, que le ministère du travail transmet au fonds
  sans le publier, fois les taux vieillesse et veuvage, fois la moitié du
  plafond trimestriel. Depuis 2026, la branche le prend en charge (L. 222-2-1,
  7°, inchangé dans sa rédaction du 1er janvier 2028) : la part du régime
  général n'est plus un transfert. Le rapport d'activité du FSV n'a pas été
  lu : son site répond 503.
- **L'inventaire** : `apprentissage` passe de `absent` à `integre`, avec
  `chiffre_par`, mesuré par le modèle, sa source au manifeste
  (`dss_plfss_2024_annexe_2`, saisie à la lecture) ; son `sans_chiffre` dit les
  trois raisons du blanc. `docs/avantages_non_contributifs.md` : la ligne
  manquait à la liste ; le § 2 compte onze lignes mesurées par retrait et deux
  lues, au lieu de sept et une.
- **La frontière contributive** : la bascule `apprentis_au_fsv` vise
  `apprentissage` et non plus `periodes_assimilees`, et passe à `applique` ;
  la liste reprise par la branche (L. 222-2-1) le compte.

## Ce que l'étape laisse

- **Étape 7**, la décision de la proposition : comment le compte reçoit le
  complément, que paie un tiers. Ce que l'étape 6 lui apporte : la page Coût
  retire des ressources des scénarios notionnels toute la recette du FSV,
  parce qu'elle paie des droits qu'aucun compte notionnel ne sert. Si le
  compte crédite le complément, sa part de la recette devrait rester ; on ne
  sait pas la séparer, mais la ligne entière où elle se fond, 305 M€ en 2022,
  fait 0,08 % des 365 Md€ de ressources du système cette année-là : la garder
  ou la retirer déplace le coefficient d'équilibre de moins d'un millième. La
  décision est de principe.
- `--par-carriere` (`scripts/cout_avantages.py`) n'a pas de dose
  d'apprentissage : la carrière d'un cas type se bâtit d'un profil, sans
  ligne de métier qui porte l'attribut.
- Les périodes que le simulateur déclare (stages, sportifs, congé de
  naissance) se rangent sous la ligne `periodes_assimilees`, dont le retrait
  ne touche que les interruptions : aucun cas type ne les porte, et leur
  mesure attend qu'un cas en porte.
- L'index LEGI est à jour au 17 octobre ; les rédactions parues depuis le 15
  n'ont pas été inscrites (`textes.py --inscrire`) : aucune règle du
  scénario 1 n'a changé ici.

## Ce qui attend le propriétaire

La décision de la proposition, à l'étape 7 : rien de neuf, sinon qu'elle ne
déplace pas d'un millième le coefficient d'équilibre de la page Coût.
