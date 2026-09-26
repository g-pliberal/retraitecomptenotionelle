# Limites — à lire avant d'utiliser un chiffre

Ce modèle est une charpente complète et fonctionnelle. Ses séries
macroéconomiques sont **certifiées de 1950 à 2025**, ses tables de mortalité sont
celles réellement observées depuis 1899, son plafond de la Sécurité sociale
remonte à 1931 daté décret par décret, et les tables par génération qui
commandent la décote — âge d'ouverture, durée requise, coefficient de
minoration — sont **lues dans le texte des articles du code** : le tout
recontrôlé automatiquement contre les sources, à chaque exécution. Ce qui
précède 1950 pour le salaire et la productivité, et les barèmes propres à
certains régimes, restent saisis à la main. Ce document dit exactement où passe
la frontière, pour qu'aucun résultat ne soit cité sans savoir sur quoi il
repose.

Il ne dit que ce qui vaut aujourd'hui. Les récits — un défaut trouvé, sa
correction, et ce qu'il valait ce jour-là — sont dans
`docs/archives/limites.md`, sous les titres qui les contenaient ici.

---

## Paramètres du scénario 1, et ce qu'ils valent

Le scénario 1 sert d'étalon : ce qui n'y est pas sourcé fragilise tout le reste.
Ce qui suit est le recensement complet de ses paramètres et de leur état.

| Paramètre | Valeur retenue | État |
|---|---|---|
| Minimum contributif | ancres du code 2007 et 2023 ; montants servis 2020, 2024-2026 | **certifié** (D. 351-2-1) et transcrit |
| Minimum contributif majoré | idem, <!--chiffre:cellule(data/reference/legislation/minimum_contributif.csv:valeur?mesure=montant_majore&annee=2007)-->7 603,41<!--/--> → <!--chiffre:cellule(data/reference/legislation/minimum_contributif.csv:valeur?mesure=montant_majore&annee=2023)-->10 170,86<!--/--> €/an | **certifié**, même article |
| Plafond d'écrêtement du minimum | ancres 2012 et 2014 ; montants servis 2020, 2024-2026 | **certifié** (D. 173-21-0-0-1) et transcrit |
| Minimum garanti, barème | montée en charge 2004-2013, indice 216 → 227 | **certifié** (loi de 2003, article 66 V) ; la ligne 1976 décrit le droit antérieur et reste transcrite |
| Minimum garanti, référence | <!--chiffre:cellule(data/reference/legislation/minimum_garanti_montants.csv:valeur/12?annee=2004)-->997,96<!--/--> €/mois au 1er janvier 2004 ; montants servis 2020, 2023-2025 | transcrit ; l'ancre de 2004 est recoupée à chaque exécution au point d'indice certifié — 227 × 52,7558 = <!--chiffre:cellule(data/reference/legislation/minimum_garanti_montants.csv:valeur?annee=2004)-->11 975,57<!--/--> € |
| Point d'indice de la fonction publique | série datée 1960-2027 | OpenFisca-France, **recontrôlé à chaque exécution** |
| Minimum vieillesse (ASPA) | montants servis 2007, 2010, 2016-2026 | transcrit des publications |
| Décote de la fonction publique | article L. 14, montée en charge 2006-2020 | **certifiée** (loi de 2003, article 66 III) jusqu'à 2019 ; la ligne 2020 est la jonction avec L. 14 |
| Carrière longue | quatre étapes datées au mois, 2004, novembre 2012, septembre 2023, septembre 2026 ; la borne des vingt ans par génération | **certifiée** pour la règle générale de 2023 (L. 351-1-1, D. 351-1-1) ; les lignes par génération et celles de 2026 transcrites du II de l'article et de la circulaire Cnav 2026-17 |
| Trimestres accordés au titre des enfants | MDA à <!--chiffre:cellule(data/reference/legislation/majoration_duree_assurance.csv:trimestres_par_enfant?dispositif=mda&debut=1972)-->4<!--/--> puis <!--chiffre:cellule(data/reference/legislation/majoration_duree_assurance.csv:trimestres_par_enfant?dispositif=mda&debut=1975)-->8<!--/--> trimestres par enfant (1972, 1975) ; bonification de la fonction publique à <!--chiffre:cellule(data/reference/legislation/majoration_duree_assurance.csv:trimestres_par_enfant?dispositif=bonifications&debut=1900)-->4<!--/--> puis <!--chiffre:cellule(data/reference/legislation/majoration_duree_assurance.csv:trimestres_par_enfant?dispositif=bonifications&debut=2004)-->2<!--/--> (2004) | reprise des textes, non recontrôlée |
| Surcote parentale | <!--chiffre:cellule(data/reference/legislation/surcote_parentale.csv:taux_par_trimestre*100?debut=2023)-->1,25<!--/--> % par trimestre cotisé dans l'année qui précède l'âge légal, dès que celui-ci atteint <!--chiffre:cellule(data/reference/legislation/surcote_parentale.csv:age_ouverture?debut=2023)-->63<!--/--> ans, <!--chiffre:cellule(data/reference/legislation/surcote_parentale.csv:trimestres_maximum?debut=2023)-->4<!--/--> au plus | reprise des textes (L. 351-1-2-1), non recontrôlée |
| Durée requise par génération | table 1934-1975, <!--chiffre:cellule(data/reference/legislation/duree_assurance_requise.csv:trimestres?generation=1934)-->151<!--/--> → <!--chiffre:maximum(data/reference/legislation/duree_assurance_requise.csv:trimestres)-->172<!--/--> trimestres, suspension de 2026 comprise (<!--chiffre:cellule(data/reference/legislation/duree_assurance_requise.csv:trimestres?generation=1965)-->170<!--/--> pour 1964 et le premier trimestre 1965, <!--chiffre:cellule(data/reference/legislation/duree_assurance_requise.csv:trimestres?generation=1965.25)-->171<!--/--> jusqu'à fin 1965, <!--chiffre:cellule(data/reference/legislation/duree_assurance_requise.csv:trimestres?generation=1966)-->172<!--/--> dès 1966) | **certifiée** depuis 1953 (L. 161-17-3 réécrit par la loi de financement pour 2026, relu dans l'index LEGI à jour ; décrets pour 1953-1957) et pour 1934-1942 (R. 351-45) ; 1943-1952 transcrite |
| Durée de proratisation par génération | table 1900-1948, <!--chiffre:minimum(data/reference/legislation/duree_proratisation.csv:trimestres)-->150<!--/--> → <!--chiffre:maximum(data/reference/legislation/duree_proratisation.csv:trimestres)-->160<!--/--> trimestres | **certifiée** (R. 351-6 II) jusqu'à 1947 ; la ligne 1948 est la jonction avec la durée requise, que l'article ne fixe pas |
| Heures de SMIC pour valider un trimestre | <!--chiffre:cellule(data/reference/legislation/validation_trimestres.csv:heures?annee=1972)-->200<!--/--> depuis 1972, <!--chiffre:cellule(data/reference/legislation/validation_trimestres.csv:heures?annee=2014)-->150<!--/--> depuis 2014 | **certifiée** (R. 351-9) |
| Revalorisation des salaires portés au compte | <!--chiffre:distinctes(data/reference/legislation/revalorisation_salaires.csv:date_effet)-->10<!--/--> colonnes publiées, effets d'octobre 2017 à janvier 2026 | circulaires de la Cnav ; ailleurs, ancrage sur la plus proche |
| Âge légal par génération | table 1900-1975, <!--chiffre:minimum(data/reference/legislation/age_ouverture_requis.csv:age)-->60<!--/--> → <!--chiffre:maximum(data/reference/legislation/age_ouverture_requis.csv:age)-->64<!--/--> ans, suspension de 2026 comprise (<!--chiffre:cellule(data/reference/legislation/age_ouverture_requis.csv:age?generation=1965)-->62,75<!--/--> ans, soit neuf mois de plus que 62, de 1963 au premier trimestre 1965, un trimestre par génération ensuite, <!--chiffre:cellule(data/reference/legislation/age_ouverture_requis.csv:age?generation=1969)-->64<!--/--> ans dès 1969) | **certifié** (L. 161-17-2, qui porte la table depuis la loi de financement pour 2026, et D. 161-2-1-9 pour les générations qu'elle renvoie à sa rédaction antérieure), recontrôlé à chaque exécution sur l'index LEGI du dépôt, à jour des incréments quotidiens de la DILA |
| Surcote | barème daté trimestre par trimestre : <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=regime_general&debut=2004&rang_minimum=1)-->0,75<!--/--> % (2004-2006), <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=regime_general&debut=2007&rang_minimum=1&apres_65_ans=0)-->0,75<!--/--> % puis <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=regime_general&debut=2007&rang_minimum=5)-->1<!--/--> % à compter du cinquième et <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=regime_general&debut=2007&apres_65_ans=1)-->1,25<!--/--> % après <!--chiffre:tenu(test_le_bareme_2007_de_la_surcote_majore_au_dela_de_65_ans)-->65<!--/--> ans (2007-2008), <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=regime_general&debut=2009)-->1,25<!--/--> % (depuis 2009) ; fonction publique <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=fonction_publique&debut=2004)-->0,75<!--/--> % plafonné à <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:trimestres_maximum?bareme=fonction_publique&debut=2004)-->20<!--/--> trimestres puis <!--chiffre:cellule(data/reference/legislation/surcote_baremes.csv:taux*100?bareme=fonction_publique&debut=2009)-->1,25<!--/--> % ; période de référence au trimestre civil | transcrit de D. 351-1-4 et de L. 14 III, rejoué contre les trois exemples de la circulaire Cnav 2018-04 et deux fiches de service-public |
| Salaire annuel moyen des parents | 24 meilleures années pour un enfant, 23 pour deux et plus, pensions dès septembre 2026 | transcrit de R. 173-3-2 (décret n° 2026-699), non recontrôlé |
| Âge d'annulation de la décote par génération | table 1930-1955, <!--chiffre:minimum(data/reference/legislation/age_annulation_decote.csv:age)-->65<!--/--> → <!--chiffre:maximum(data/reference/legislation/age_annulation_decote.csv:age)-->67<!--/--> ans | calculée depuis l'âge d'ouverture certifié, selon la règle de `L. 351-8` ; recontrôlée à chaque exécution |
| Coefficient de minoration par génération | table 1900-1975, <!--chiffre:maximum(data/reference/legislation/coefficient_minoration.csv:coefficient*100)-->2,5<!--/--> → <!--chiffre:minimum(data/reference/legislation/coefficient_minoration.csv:coefficient*100)-->1,25<!--/--> % | **certifié** (R. 351-27 II), recoupé à la DREES |
| Années retenues au salaire de référence | table 1934-1948, <!--chiffre:minimum(data/reference/legislation/annees_salaire_reference.csv:annees)-->10<!--/--> → <!--chiffre:maximum(data/reference/legislation/annees_salaire_reference.csv:annees)-->25<!--/--> années | **certifiée** (R. 351-29-1) |
| Coefficients d'anticipation Agirc-Arrco | deux tables, 1 → 0,78 et 1 → 0,43 | barème publié par la caisse, saisi |
| Plafond de la majoration familiale Agirc-Arrco | <!--chiffre:partout(data/reference/regimes/complementaires_prive.yaml:regimes.*.periodes.*.plafond_majoration_enfants)-->2 367<!--/--> €/an (novembre 2025) | publié par la caisse, saisi |
| Garantie minimale de points de l'Agirc | <!--chiffre:partout(data/reference/regimes/complementaires_prive.yaml:regimes.*.periodes.*.points_minimum_annuels)-->120<!--/--> points par an, 1989-2018 | accord du 9 février 1988, saisi |
| Assiette de l'AVPF | SMIC annuel, <!--chiffre:tenu(test_l_avpf_porte_un_salaire_au_compte)-->1 820<!--/--> heures | principe sourcé, assiette déduite du SMIC |
| Droits ouverts par motif d'interruption | <!--chiffre:lignes_csv(data/reference/legislation/periodes_non_travaillees.csv)-->9<!--/--> motifs | principe sourcé, fractions non recontrôlées |

**Une règle a été appliquée partout : le montant SERVI prime sur la projection.**
Le minimum contributif, le minimum garanti et le minimum vieillesse sont trois
grandeurs que la loi ne fixe pas chaque année — elle les revalorise « comme les
pensions », c'est-à-dire selon une décision annuelle qui a été gelée en 2014 et
sous-indexée plusieurs fois depuis. Projeter une ancre sur l'indice des prix
donne donc, pour le minimum garanti de 2024, un montant supérieur de <!--chiffre:tenu(test_le_minimum_garanti_servi_est_sous_sa_projection)-->4,6<!--/--> % à
celui que l'État a payé. Les montants transcrits de leur publication, moins bien
sourcés, l'emportent sur les valeurs calculées depuis une ancre certifiée —
parce que les premiers disent ce qui a été payé et les seconds ce qui aurait dû
l'être.

## Écarts avec le droit positif dans le scénario 1

### Ce qui reste hors du modèle, et pourquoi

Ces lignes ne sont pas des oublis : chacune demande une information que le
modèle n'a pas, ou décrit un dispositif qu'il représenterait faussement.

- **Pension de réversion.** Elle ne concerne pas l'assuré mais son conjoint
  survivant, et suppose de connaître un ménage. Hors périmètre par
  construction : le modèle décrit une carrière, pas une famille.
- **Les revalorisations servies APRÈS la liquidation.** Le moteur s'arrête au
  jour du départ : il calcule la pension du premier mois et ne suit aucune des
  revalorisations qu'un retraité a reçues depuis. La page l'exprime en euros
  constants de l'année de référence, ce qui rend le montant comparable aux prix
  d'aujourd'hui — mais par le CHEMIN DES PRIX, non par celui des arrêtés. Or le
  droit indexe les pensions servies sur les prix : les deux chemins coïncident,
  à ceci près que plusieurs années ont été sous-indexées par décision expresse
  — gels et revalorisations partielles —, et le modèle ne les reprend pas. La
  conséquence se voit sur la saisie par la pension, où c'est cette convention
  qui autorise un retraité à taper le montant qu'il touche aujourd'hui. Ce
  montant est un peu plus bas que sa première pension revalorisée sur les prix,
  puisque les pensions ont décroché des prix ces années-là ; la page vise donc
  une cible un peu trop basse, et le revenu d'activité qu'elle en déduit est
  un peu plus bas que celui qui a réellement été gagné. Servir la vraie trajectoire
  demanderait la série des coefficients réellement appliqués aux pensions,
  lue dans les arrêtés ; le dépôt porte celle des salaires portés au compte,
  qui n'est pas la même chose.
- **La troisième condition de la liquidation unique des régimes alignés.** La
  LURA elle-même est servie depuis le 22 septembre 2026 — voir plus bas —, et
  ses deux premières conditions sont opposées : la génération, la date d'effet
  au mois près. La troisième ne l'est pas : la loi écarte la LURA de qui avait
  DÉJÀ obtenu, avant le 1er juillet 2017, une retraite de même nature dans
  l'un des trois régimes. Une carrière du dépôt liquide tout à la fois, et ne
  peut donc pas porter ce cas. De même, le revenu annuel moyen de la LURA
  additionne les salaires et revenus d'une MÊME année civile avant de les
  écrêter au plafond : une carrière du dépôt n'exerce qu'un métier à la fois,
  et la somme n'a jamais lieu.
- **Bonifications de service.** Bonifications de dépaysement, de campagne
  militaire, du cinquième pour les emplois de sécurité. La bonification POUR
  ENFANTS, elle, est servie : elle ne demande que le nombre d'enfants. Les
  autres supposent de connaître le CORPS d'appartenance et le détail des
  services, que la saisie ne demande pas.
- **Le temps partiel.** Il compte à temps plein dans la durée d'assurance, et
  seulement à sa quotité dans les services qui liquident une pension de la
  fonction publique — sauf le temps partiel thérapeutique, le temps partiel de
  droit pour un enfant né depuis 2004 et la surcotisation, bornée à quatre
  trimestres. La saisie ne demande pas la quotité, et le champ `quotite` des
  lignes de carrière n'est lu nulle part : un fonctionnaire qui a travaillé à
  temps partiel sans surcotiser reçoit ici la pension d'un temps plein.
- **Rachats, surcotisation, retraite progressive, cumul emploi-retraite.**
  Le modèle liquide une fois, à une date, sur la carrière saisie : il ne
  rachète pas d'années d'études, ne surcotise pas, ne sert pas de pension
  partielle et ne suit pas le retraité qui reprend un emploi. Les barèmes
  sont lus et rangés au registre de veille (`rachats_et_versements`,
  `cumul_emploi_retraite_et_retraite_progressive`) — dont celui du rachat
  d'études de la fonction publique, refait au premier janvier 2026, que la
  calculette de l'ENSAP n'applique pas encore — et les règles du cumul
  changent pour les pensions prenant effet en 2027.
- **Catégorie active : servie, mais sur un classement déclaré.** L'âge anticipé
  de l'article L. 24 — <!--chiffre:cellule(data/reference/legislation/categorie_active.csv:age_ouverture?classement=active&generation=1960)-->57<!--/--> ans, <!--chiffre:cellule(data/reference/legislation/categorie_active.csv:age_ouverture?classement=super_active&generation=1965)-->52<!--/--> pour la super-active, <!--chiffre:maximum(data/reference/legislation/categorie_active.csv:age_ouverture?classement=active)-->59<!--/--> et <!--chiffre:maximum(data/reference/legislation/categorie_active.csv:age_ouverture?classement=super_active)-->54<!--/--> après la
  réforme de 2023 — est désormais opposé, ainsi que l'âge d'annulation de décote
  propre au classement (<!--chiffre:maximum(data/reference/legislation/categorie_active.csv:age_annulation?classement=active)-->62<!--/--> et <!--chiffre:maximum(data/reference/legislation/categorie_active.csv:age_annulation?classement=super_active)-->57<!--/--> ans), la condition de durée de services
  classés (<!--chiffre:maximum(data/reference/legislation/categorie_active.csv:services_requis_annees?classement=active)-->17<!--/--> et <!--chiffre:maximum(data/reference/legislation/categorie_active.csv:services_requis_annees?classement=super_active)-->27<!--/--> ans) et, depuis le 22 septembre 2026, la DURÉE REQUISE
  propre aux emplois classés, dont le calendrier est donné plus bas (« La durée
  requise des emplois classés »). Ce qui reste hors
  du modèle est le CLASSEMENT lui-même : il tient à l'emploi occupé, qu'aucune donnée de carrière ne révèle,
  et c'est donc l'assuré qui le déclare en choisissant l'un des cinq statuts
  classés. Qui se trompe de statut se trompe d'âge. La table ne porte par
  ailleurs qu'une durée par classement — <!--chiffre:maximum(data/reference/legislation/categorie_active.csv:services_requis_annees?classement=active)-->17<!--/--> ans en active, <!--chiffre:maximum(data/reference/legislation/categorie_active.csv:services_requis_annees?classement=super_active)-->27<!--/--> en super-active :
  les <!--chiffre:illustration()-->17<!--/--> années des ingénieurs du contrôle de la navigation aérienne et les <!--chiffre:illustration()-->32<!--/-->
  des égoutiers et des identificateurs de l'institut médico-légal ne sont pas
  distinguées, faute d'un corps déclaré.
- **Pension militaire : la durée est servie, le grade ne l'est pas.** Les deux
  statuts militaires opposent la durée de services qui ouvre la pension —
  <!--chiffre:maximum(data/reference/legislation/duree_services_militaires.csv:annees_requises?categorie=non_officier)-->17<!--/--> ans pour un non-officier, <!--chiffre:maximum(data/reference/legislation/duree_services_militaires.csv:annees_requises?categorie=officier)-->27<!--/--> pour un officier, <!--chiffre:minimum(data/reference/legislation/duree_services_militaires.csv:annees_requises?categorie=non_officier)-->15<!--/--> et <!--chiffre:minimum(data/reference/legislation/duree_services_militaires.csv:annees_requises?categorie=officier)-->25<!--/--> avant la loi du
  9 novembre 2010 —, l'âge de jouissance différée de l'article L. 25 et la
  décote propre du II de l'article L. 14, plafonnée à dix trimestres. Restent
  dehors : la LIMITE D'ÂGE DE GRADE, qui ouvre la pension quelle que soit la
  durée accomplie et qui sert d'âge d'annulation de la décote au militaire
  liquidant à <!--chiffre:illustration()-->52<!--/--> ans ou plus (L. 14 bis, 4°) — le modèle ne connaît pas le
  grade et applique donc à tous le barème du II —, et la limite de durée de
  services, qui l'ouvre de la même façon. Conséquence : un officier supérieur
  radié par limite d'âge peut être déclaré non ouvert quand le droit l'ouvre, et
  la décote d'un militaire parti très tôt est au plus de <!--chiffre:mesure(constante?de=retraite_notionnelle.droit.ouvrir&nom=TRIMESTRES_DECOTE_MILITAIRE&echelle=1.25)-->12,5<!--/--> %, jamais de <!--chiffre:illustration()-->25<!--/--> %.
- **Pension majorée de référence (PMR)** du régime des non-salariés agricoles.
  Le régime agricole est déjà le plus approché du catalogue — sa part
  forfaitaire, sa complémentaire obligatoire et ses valeurs de point ne sont que
  partiellement sourcées. Ajouter la PMR sur ce socle donnerait un chiffre plus
  précis d'apparence et pas davantage de vérité.
- **Coefficients de solidarité et majorants de l'Agirc-Arrco.** Le malus de
  <!--chiffre:illustration()-->10<!--/--> % pendant trois ans, et le bonus de <!--chiffre:illustration()-->10<!--/-->, <!--chiffre:illustration()-->20<!--/--> ou <!--chiffre:illustration()-->30<!--/--> % pendant un an, ne
  s'appliquent qu'aux pensions prenant effet entre le 1er janvier 2019 et le
  30 novembre 2023 : le dispositif est éteint. Surtout, leur effet est
  TEMPORAIRE, quand le modèle ne calcule qu'une pension annuelle unique.
  L'appliquer à titre permanent créerait une erreur nouvelle, plus grande que
  celle qu'il corrigerait.
- **Pénibilité, invalidité, inaptitude, handicap.** Quatre autres portes du
  départ anticipé, qui demandent des informations médicales ou
  professionnelles que le modèle ne collecte pas. Un assuré qui en relèverait
  est ici déclaré « non ouvert » alors que le droit l'ouvrirait, et subit une
  décote dont le droit le dispenserait.
- **Trimestres « réputés cotisés » de la carrière longue : deux cas sur sept.**
  Les six enveloppes de l'article D. 351-1-2 sont servies depuis le
  22 septembre 2026 — service national, incapacité temporaire, chômage
  indemnisé, maternité, invalidité, assurance vieillesse des parents au foyer —,
  chacune sous sa limite. Restent dehors le 6° du I, majoration de durée
  d'assurance du compte professionnel de prévention, que le modèle ne calcule
  pas, et la part du 7° qui vise les fonctionnaires affiliés à un régime spécial
  tout en remplissant les conditions de L. 381-1, qu'il ne distingue pas. Reste
  aussi une lecture qui manque : l'article D. 351-1-3 pose la condition de DÉBUT
  d'activité sur une « durée d'assurance » de cinq trimestres, quand le modèle
  n'y compte que les trimestres cotisés — plus dur que la lettre du décret, en
  attendant la circulaire qui l'applique.
- **La date d'effet est le mois de l'anniversaire.** Le modèle liquide au mois
  où l'âge demandé est atteint ; la caisse fait prendre effet la pension le
  premier jour du mois SUIVANT, sauf pour qui est né un premier. Un mois
  d'écart, qui se voit là où un texte coupe au mois : la borne de la carrière
  longue des nés en décembre 1965, fixée à <!--chiffre:illustration()-->60<!--/--> ans et 8 mois pour que la
  pension prenne effet le 1er septembre 2026, tombe ici en août 2026, sous le
  décret précédent, qui demande <!--chiffre:illustration()-->60<!--/--> ans et 9 mois.
- **La durée requise d'un droit ouvert avant soixante ans : servie, sauf au
  civil non classé.** Le XXIV, B de l'article 10 de la loi du 14 avril 2023 pour
  l'État, et le II, B de l'article 13 du décret n° 2023-435 pour la CNRACL et le
  FSPOEIE, donnent aux catégories actives leur propre calendrier de durée —
  <!--chiffre:cellule(data/reference/legislation/categorie_active.csv:duree_requise_trimestres?classement=active&generation=1967)-->169<!--/--> trimestres des nés de septembre 1966 à 1967, <!--chiffre:cellule(data/reference/legislation/categorie_active.csv:duree_requise_trimestres?classement=active&generation=1971)-->172<!--/--> dès 1971, les
  mêmes marches cinq ans plus tard pour la super-active —, et
  `categorie_active.csv` le porte. Pour l'emploi classé né avant ces marches, et
  pour le militaire qui pouvait liquider avant le 1er septembre 2023, la durée
  n'est pas celle de sa génération mais celle de la génération qui a soixante
  ans l'année où son droit s'ouvre (L. 13, III, du code des pensions, version de
  2014) : `duree_requise_avant_soixante_ans.csv` la porte, et le super-actif né
  en 1965 se voit opposer <!--chiffre:cellule(data/reference/legislation/duree_requise_avant_soixante_ans.csv:trimestres?regle=l13_iii&annee_ouverture=2017)-->166<!--/--> trimestres, comme le publie la Cour des comptes.
  Le militaire qui peut liquider depuis relève du C du même XXIV : <!--chiffre:cellule(data/reference/legislation/duree_requise_avant_soixante_ans.csv:trimestres?regle=xxiv_c&annee_ouverture=2023.667)-->169<!--/-->
  trimestres, puis un de plus au 1er janvier 2025 et au 1er janvier 2027. Reste
  dehors le fonctionnaire CIVIL non classé qui liquide avant soixante ans —
  parent de trois enfants, handicap — : le modèle ne sert ces départs à
  personne.
- **Ce qui compte en services dans les régimes spéciaux.** La pension des
  dix-huit régimes spéciaux du catalogue se proratise, comme celle de la
  fonction publique, sur des services et non sur une durée d'assurance ; mais
  ce que chacun retient comme service tient à son propre règlement, et aucun
  n'a été lu. La règle tirée des articles L. 5 et L. 9 du code des pensions —
  le chômage n'ouvre aucun service, les congés de maladie et de maternité en
  ouvrent, le congé parental dans la limite de trois ans par enfant — ne
  s'applique donc qu'à la famille `fonction_publique`. Partout ailleurs, une
  interruption qui valide des trimestres continue d'entrer au prorata, ce qui
  surestime la pension d'un agent de régime spécial à carrière hachée.
- **Montée en charge propre aux régimes spéciaux.** La décote créée par la
  réforme de 2008 y monte en charge comme celle de la fonction publique, mais
  selon un calendrier qui lui est propre, régime par régime. Le modèle applique
  d'emblée le coefficient plein à partir de la date d'entrée en vigueur portée
  par chaque fiche.
- **Année de naissance des enfants.** Le modèle ne la collecte pas : il présume
  les enfants nés aux trente ans de leur mère, l'âge moyen des mères à
  l'accouchement (la présomption `naissance_des_enfants`, que la chronologie
  pose et que le moteur lit ; une naissance déclarée la remplacerait). La
  convention ne déplace qu'une chose, la bascule des quatre aux deux
  trimestres de la fonction publique, qui tombe ainsi sur les générations nées
  à partir de 1974. Elle ne peut pas non plus savoir si les
  parents ont attribué au père les quatre trimestres d'éducation ouverts en
  2010, ni si un père fonctionnaire a interrompu son activité les deux mois
  qu'exige la bonification depuis 2003 : dans les deux cas le modèle retient
  l'attribution par défaut, celle de la mère.
- **Montée en charge des bonifications dans les régimes spéciaux.** Ils suivent
  ici le calendrier de la fonction publique — un an par enfant né avant 2004 —
  quand leurs propres réformes sont de 2008. La documentation de la CNRACL
  donne, pour la RATP, une bonification d'un an jusqu'aux enfants nés le
  30 juin 2008 puis deux trimestres, et pour la SNCF deux trimestres depuis le
  décret du 30 juin 2008 ; pour les IEG, la bascule est en revanche datée de
  2004 comme dans la fonction publique. Trois calendriers pour trois régimes,
  qu'aucune source ne donne en série : le modèle retient le seul qui soit
  documenté article par article, celui de la fonction publique.
- **Majorations pour enfants des non-salariés agricoles.** La MSA sert bien une
  majoration de durée d'assurance à ses non-salariés, mais elle s'y convertit en
  POINTS et non en trimestres, selon une règle qui change au 1er janvier 2026.
  Le régime des exploitants étant déjà le plus approché du catalogue, la porter
  ici donnerait un chiffre plus précis d'apparence et pas davantage de vérité.
- **Un ménage, un patrimoine, des ressources.** Le minimum vieillesse est servi
  sous le barème d'une personne seule sans autre ressource — le cas le plus
  favorable — et à tous, alors que la DREES estime le non-recours à la moitié
  des ayants droit. C'est pourquoi il apparaît toujours comme une ligne séparée
  de la cascade, et pourquoi un paramètre le retire d'un seul geste.

## 1. État de certification des données

La page **Données** du site affiche l'état exact, et date chaque série du jour
où elle a été relue contre sa source (`verifiee_le` dans le journal, §6). En
résumé :

| Donnée | Période | Niveau | Source |
|---|---|---|---|
| Inflation (IPC) | <!--chiffre:minimum(data/reference/macro/ipc_annuel.csv:annee?fiabilite=certifiee)-->1950<!--/-->-<!--chiffre:maximum(data/reference/macro/ipc_annuel.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, idbanks 000008965 et 001764363 |
| Inflation | <!--chiffre:minimum(data/reference/macro/ipc_annuel.csv:annee?fiabilite=estimee)-->1930<!--/-->-<!--chiffre:maximum(data/reference/macro/ipc_annuel.csv:annee?fiabilite=estimee)-->1949<!--/--> | estimée | reconstitution, dérive cumulée recoupée à l'INSEE idbank 010605954 (1901-) |
| Salaire moyen par tête | <!--chiffre:minimum(data/reference/macro/salaire_moyen.csv:annee?fiabilite=certifiee)-->1950<!--/-->-<!--chiffre:maximum(data/reference/macro/salaire_moyen.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, idbanks 011785411 et 011793486 |
| Salaire moyen par tête | <!--chiffre:minimum(data/reference/macro/salaire_moyen.csv:annee?fiabilite=estimee)-->1930<!--/-->-<!--chiffre:maximum(data/reference/macro/salaire_moyen.csv:annee?fiabilite=estimee)-->1949<!--/--> | estimée | reconstitution |
| Productivité réelle | <!--chiffre:minimum(data/reference/macro/productivite.csv:annee?fiabilite=certifiee)-->1950<!--/-->-<!--chiffre:maximum(data/reference/macro/productivite.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, idbanks 011785223 et 011793334 |
| Productivité réelle | <!--chiffre:minimum(data/reference/macro/productivite.csv:annee?fiabilite=estimee)-->1930<!--/-->-<!--chiffre:maximum(data/reference/macro/productivite.csv:annee?fiabilite=estimee)-->1949<!--/--> | estimée | reconstitution |
| Produit intérieur brut, en niveau | <!--chiffre:minimum(data/reference/macro/pib_courant.csv:annee?fiabilite=certifiee)-->1949<!--/-->-<!--chiffre:maximum(data/reference/macro/pib_courant.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, idbank 011779992 |
| Profil de salaire par tranche d'âge | <!--chiffre:minimum(data/reference/macro/profil_salaire_age.csv:annee?fiabilite=certifiee)-->1962<!--/-->-<!--chiffre:maximum(data/reference/macro/profil_salaire_age.csv:annee?fiabilite=certifiee)-->2024<!--/--> | **certifiée** | INSEE Melodi, DS_DERA_PRIVE_SERIES_LONGUES |
| Profil de salaire par âge et catégorie | 2024 | **certifiée** | INSEE Melodi, DS_DERA_PRIVE_ANNUEL |
| Profil de salaire public par âge et statut | 2023 | **certifiée** | INSEE Melodi, DS_DERA_PUBLIC_ANNUEL |
| Profil de salaire par âge et secteur | 2018, 2022 | **certifiée** | Eurostat, enquête sur la structure des salaires |
| Population par âge, <!--chiffre:minimum(data/reference/macro/population_par_age.csv:age)-->50<!--/--> ans et plus | <!--chiffre:minimum(data/reference/macro/population_par_age.csv:annee?fiabilite=certifiee)-->1962<!--/-->-<!--chiffre:maximum(data/reference/macro/population_par_age.csv:annee?fiabilite=certifiee)-->2023<!--/--> | **certifiée** | INSEE, estimations de population (classeur des projections 2026) |
| Population par âge, <!--chiffre:minimum(data/reference/macro/population_par_age.csv:age)-->50<!--/--> ans et plus | <!--chiffre:minimum(data/reference/macro/population_par_age.csv:annee?fiabilite=projetee)-->2024<!--/-->-<!--chiffre:maximum(data/reference/macro/population_par_age.csv:annee?fiabilite=projetee)-->2070<!--/--> | projetée | INSEE, projections de population 2026, scénario central |
| Population des 20-64 ans | 1962-2023 / 2024-2070 | **certifiée** / projetée | mêmes sources |
| Dépenses de vieillesse-survie, tous régimes | <!--chiffre:minimum(data/reference/macro/depenses_retraite.csv:annee?fiabilite=certifiee)-->1959<!--/-->-<!--chiffre:maximum(data/reference/macro/depenses_retraite.csv:annee?fiabilite=certifiee)-->2024<!--/--> | **certifiée** | DREES, Comptes de la protection sociale, poste E11-2 |
| Dépenses de vieillesse-survie, par système | <!--chiffre:minimum(data/reference/macro/depenses_retraite_regimes.csv:annee?fiabilite=certifiee)-->1990<!--/-->-<!--chiffre:maximum(data/reference/macro/depenses_retraite_regimes.csv:annee?fiabilite=certifiee)-->2024<!--/--> | **certifiée** | DREES, mêmes comptes, ventilation par organisme |
| Dépenses de vieillesse-survie, par système | 1981-1989 | absentes | nomenclature d'alors sans raccord publié — voir §5 bis |
| Retraités de droit direct, par caisse | 2004-2024, <!--chiffre:distinctes(data/reference/regimes/effectifs_retraites.csv:caisse)-->27<!--/--> séries, les caisses et le total tous régimes | **certifiée** | DREES, enquête annuelle auprès des caisses de retraite, fichier diffusé |
| Retraités de droit direct, par caisse | hors 2004-2024 | estimée | la répartition du bord est reconduite — voir §5 bis |
| Distribution des pensions mensuelles brutes de droit direct | fin 2020, <!--chiffre:distinctes(data/reference/macro/distribution_pensions.csv:borne_mensuelle?sexe=ensemble)-->46<!--/--> tranches | **certifiée** | DREES, échantillon interrégimes de retraités 2020, tableau 1 |
| Patrimoine des ménages : déciles, moyennes et médianes par âge | début 2021 et début 2024 | **haute** | INSEE, enquête Histoire de vie et Patrimoine, Insee Focus n° 287 et page « Distribution du patrimoine des ménages », classeurs lus par script |
| Mode de résidence après <!--chiffre:minimum(data/reference/macro/vie_en_couple.csv:age)-->65<!--/--> ans, par âge et par sexe | 2021, <!--chiffre:distinctes(data/reference/macro/vie_en_couple.csv:age)-->36<!--/--> âges | **haute** | INSEE, recensement 2021, *Insee Première* n° 2040, figure 2, classeur lu par script |
| Patrimoine des ménages retraités selon leur revenu disponible | 2018, <!--chiffre:lignes_csv(data/reference/macro/patrimoine_menages.csv?source_id=cor_patrimoine_retraites)-->6<!--/--> valeurs | **saisie** | COR, « Le patrimoine des retraités », séance du 16 décembre 2021, sur l'enquête Patrimoine 2018 — les graphiques du PDF ne se lisent pas |
| Hypothèses de projection | 2026-2100 | **saisie** | COR, rapport annuel de juin 2025, jeu reconduit en juin 2026 |
| Emploi projeté (croissance de l'emploi, dérivée) | 2026-2070 | **saisie** | COR, rapport annuel de juin 2026, données de la partie 1 : population active et chômage du scénario de référence |
| Espérance de vie à 0 et <!--chiffre:illustration()-->60<!--/--> ans | <!--chiffre:minimum(data/reference/mortalite/esperances_vie.csv:annee?mesure=e0&fiabilite=certifiee)-->1946<!--/-->-<!--chiffre:maximum(data/reference/mortalite/esperances_vie.csv:annee?mesure=e0&fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, quatre idbanks, annuel par sexe |
| Espérance de vie à <!--chiffre:illustration()-->65<!--/--> ans | 1960-2024 | **certifiée** | OCDE `DSD_HEALTH_STAT@DF_LE` |
| Espérance de vie à <!--chiffre:illustration()-->65<!--/--> ans | 1946-1959 | haute | **dérivée** des quotients INED, recalculée à chaque exécution |
| Espérances de vie e0, e60, e65 | 2026-2125 | projetée | **dérivée** des quotients projetés par l'INSEE, projections 2026 |
| Espérance de vie par vingtile de niveau de vie, e0, e60, e65 | 2012-2016 et 2020-2024 | haute | INSEE, tables de mortalité par niveau de vie (Insee Résultats 2025), lues telles quelles, l'ensemble contrôlé contre la série certifiée |
| Espérance de vie à <!--chiffre:illustration()-->65<!--/--> ans des fonctionnaires civils de l'État | 2024 | **saisie** | Service des retraites de l'État, PAP 741 du PLF 2026, apporté par l'utilisateur |
| Quotients de mortalité par âge | 1986-2024 | **certifiée** | Eurostat `demo_mlifetable`, âges 0-<!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age?annee=2024)-->94<!--/--> depuis 2014, 0-<!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age?annee=2010)-->84<!--/--> de 1998 à 2013 |
| Quotients de mortalité par âge | 1899-1985 | **certifiée** | INED, tables de Vallin et Meslé, âges 0-104 |
| Quotients de mortalité par âge | 1986-1997, jusqu'à <!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age?annee=1990)-->104<!--/--> ans | **certifiée** | INED, là où Eurostat s'arrête |
| Quotients de mortalité par âge | après 1997, au-delà de <!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age?annee=2010)-->84<!--/--> ans jusqu'en 2013 et de <!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age?annee=2024)-->94<!--/--> ans depuis | absents | calibration paramétrique, dont le biais est mesuré |
| Minimum contributif et plafond d'écrêtement | ancres de 2007 à 2014 | **certifiée** | DILA, base LEGI, code de la sécurité sociale |
| Minimum contributif, minimum majoré et plafond | montants servis 2020 | haute | transcrits d'une réponse ministérielle, recoupés à chaque exécution contre les circulaires Cnav que transcrit OpenFisca-France-Pension — sa série s'arrête en 2023, les montants postérieurs restent sans recoupement |
| Minimum vieillesse (ASPA) | ancres 2006, 2009-2012, 2014, 2018-2020 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 815-1` |
| Minimum vieillesse (ASPA) | ancres 2007, 2016, 2017, depuis 2021 | haute / moyenne | publications — l'article n'est pas réécrit à chaque revalorisation |
| Minimum garanti, traitement de référence | 2004 et année courante | **certifiée** | Service des retraites de l'État, sa page du minimum garanti |
| Minimum garanti, traitement de référence | ancres intermédiaires | haute | non publiées : la page ne porte que l'ancre et l'année courante |
| Âge d'ouverture des droits par génération | <!--chiffre:minimum(data/reference/legislation/age_ouverture_requis.csv:generation?fiabilite=certifiee)-->1900<!--/-->-<!--chiffre:maximum(data/reference/legislation/age_ouverture_requis.csv:generation?fiabilite=certifiee)-->1975<!--/--> | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 161-2-1-9` |
| Durée d'assurance requise par génération | 1958-1975 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `L. 161-17-3` |
| Durée d'assurance requise par génération | 1953-1957 | **certifiée** | DILA, base LEGI, décrets d'application des lois de 2003 et de 2010 |
| Durée d'assurance requise par génération | 1934-1942 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-45` II |
| Durée d'assurance requise par génération | 1943-1952 | haute | 160 vient de la règle générale, non d'un alinéa qui les nomme ; les 161-164 sont dans des décrets absents de la base — recoupées à chaque exécution contre la table d'OpenFisca-France-Pension |
| Durée de services de la fonction publique, droits ouverts 2004-2008 | <!--chiffre:minimum(data/reference/legislation/duree_requise_fonction_publique.csv:trimestres)-->152<!--/--> à <!--chiffre:maximum(data/reference/legislation/duree_requise_fonction_publique.csv:trimestres)-->160<!--/--> trimestres | haute | loi n° 2003-775, article 66 II, lu dans la base LEGI et mis en table ; recoupé contre OpenFisca-France-Pension |
| Coefficient de minoration par génération | <!--chiffre:minimum(data/reference/legislation/coefficient_minoration.csv:generation?fiabilite=certifiee)-->1900<!--/-->-<!--chiffre:maximum(data/reference/legislation/coefficient_minoration.csv:generation?fiabilite=certifiee)-->1975<!--/--> | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-27` |
| Bornes de la carrière longue | 2023-, règle générale et borne des vingt ans par génération | **certifiée** | DILA, base LEGI, `L. 351-1-1` et `D. 351-1-1` (I et II, versions de 2023 et de 2026, lues à leur date d'effet) |
| Bornes de la carrière longue | 2004, 2011 et 2012, par génération | **certifiée** | DILA, base LEGI, versions abrogées de `D. 351-1-1` que l'index expose |
| Durée maximale prise en compte par la proratisation | avant 1944 à 1947 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-6` II |
| Heures de SMIC à cotiser pour valider un trimestre | 1972 et 2014 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-9` |
| Années retenues au salaire annuel moyen, par génération | avant 1934 à 1948 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-29-1` |
| Décote de la fonction publique, coefficient et âge d'annulation | <!--chiffre:minimum(data/reference/legislation/decote_fonction_publique.csv:annee?fiabilite=certifiee)-->2006<!--/-->-<!--chiffre:maximum(data/reference/legislation/decote_fonction_publique.csv:annee?fiabilite=certifiee)-->2019<!--/--> | **certifiée** | DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 III |
| Barème du minimum garanti, montée en charge | <!--chiffre:minimum(data/reference/legislation/minimum_garanti.csv:annee?fiabilite=certifiee)-->2004<!--/-->-<!--chiffre:maximum(data/reference/legislation/minimum_garanti.csv:annee?fiabilite=certifiee)-->2013<!--/--> | **certifiée** | DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 V |
| Âge d'annulation de la décote, régime général | 1930-1955 | haute | calculé — l'âge d'ouverture certifié majoré de cinq ans, comme l'écrit `L. 351-8` ; recontrôlé à chaque exécution, et recoupé contre la table transcrite d'OpenFisca-France-Pension |
| Point d'indice de la fonction publique | <!--chiffre:minimum(data/reference/legislation/point_indice_fonction_publique.csv:annee?fiabilite=certifiee)-->1996<!--/-->-<!--chiffre:maximum(data/reference/legislation/point_indice_fonction_publique.csv:annee?fiabilite=certifiee)-->2027<!--/--> | **certifiée** | DILA, base LEGI, décret n° 85-1148 du 24 octobre 1985, article 3 |
| Point d'indice de la fonction publique | <!--chiffre:minimum(data/reference/legislation/point_indice_fonction_publique.csv:annee?fiabilite=haute)-->1960<!--/-->-<!--chiffre:maximum(data/reference/legislation/point_indice_fonction_publique.csv:annee?fiabilite=haute)-->1995<!--/--> | haute | OpenFisca-France, `point_indice_en_euros` — deux versions manquent au dump avant 1996 |
| SMIC horaire | 1997-2017, sauf 2002 | **certifiée** | DILA, base LEGI, décrets portant relèvement du SMIC |
| SMIC horaire | 1970-1996, 2002 et depuis 2018 | haute | OpenFisca-France, `smic_horaire_brut` |
| Plafond Sécurité sociale | 2002-2025 | **certifiée** | INSEE BDM, idbank 000822494 |
| Plafond Sécurité sociale | 1963, 1965-1981, 1984, 1987, 1988, 1990-1993, 1996-2001 | **certifiée** | DILA, base JORF, décrets portant fixation du plafond |
| Plafond Sécurité sociale | le reste de 1931-2001 | haute | OpenFisca-France, daté décret par décret — la notice ancienne du JORF n'a pas d'écriture stable |
| Revalorisation des salaires portés au compte | <!--chiffre:distinctes(data/reference/legislation/revalorisation_salaires.csv:date_effet)-->10<!--/--> colonnes, effets 2017-2026, perceptions depuis 1930 | haute | Cnav, circulaires de revalorisation, recoupées deux à deux |
| Taux de cotisation, régime général | <!--chiffre:minimum(data/reference/regimes/taux_cotisation_annuels.csv:annee?regime=regime_general&fiabilite=certifiee)-->1982<!--/-->-<!--chiffre:maximum(data/reference/regimes/taux_cotisation_annuels.csv:annee?regime=regime_general&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 242-4` et décret n° 81-1013 du 13 novembre 1981, article 2 ; la hausse temporaire de 1987-1988, qui n'a pas réécrit l'article, est lue dans la base JORF |
| Taux de cotisation, régime général | 1967-1979 | haute | OpenFisca-France, transcrit des barèmes IPP — l'article 3 du décret n° 67-803 n'a qu'une version dans LEGI, datée de 1967 et portant l'état de 1979. Chaque marche est **ancrée** à son décret, retrouvé au JORF au numéro et à la date que l'IPP annonce (35 sur 36 ; le n° 70-680 manque à l'index) |
| Taux de cotisation, régime général | 1980 et 1981 | haute, **comme leurs voisines** | le décret n° 79-650 du 30 juillet 1979 a relevé des taux « à titre exceptionnel » du 1er août 1979 au 31 janvier 1981 : c'est le point du plan Barrot, porté par la seule cotisation MALADIE du salarié, et la vieillesse n'y est pas — voir plus bas |
| Taux de cotisation, salariés agricoles | <!--chiffre:minimum(data/reference/regimes/taux_cotisation_annuels.csv:annee?regime=msa_salaries&fiabilite=certifiee)-->1980<!--/-->-<!--chiffre:maximum(data/reference/regimes/taux_cotisation_annuels.csv:annee?regime=msa_salaries&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | DILA, base LEGI, décret n° 50-444 du 20 avril 1950, article 2, puis code rural `D. 741-35`, qui renvoie à `D. 242-4` depuis 2014 |
| Taux de cotisation, salariés agricoles | 1967-1979 | moyenne | la série du régime général tenant lieu, faute d'une version antérieure de l'article 2 |
| Taux de cotisation, cultes, Mayotte, Saint-Pierre-et-Miquelon | depuis 1979 et 1987 | haute | la série du régime général du dépôt, que ces trois régimes portent faute d'un barème propre : la valeur est certifiée, la substitution est une décision de modélisation |
| Taux de cotisation, complémentaires du privé | Arrco 1962-2018, Agirc 1981-2018, Agirc-Arrco 2019- | moyenne | OpenFisca-France, taux effectifs par tranche, recoupés à chaque exécution. **Ne se certifieront pas** : ces taux sont fixés par accord collectif, l'IPP — source amont d'OpenFisca — laisse lui-même la colonne du *Journal officiel* vide pour chacune de leurs 25 marches, et le JO ne publie que l'avis d'extension, qui renvoie au Bulletin officiel sans écrire le chiffre |
| Retenue pour pension, État, CNRACL, ouvriers de l'État | 1948-2026, une période par taux | moyenne | OpenFisca-France, article L. 61 et barème de la caisse, recoupés à chaque exécution |
| Cotisation vieillesse de base des artisans et commerçants | 1973-2018, moyennes par période | moyenne | OpenFisca-France, décrets d'application de la loi du 3 juillet 1972, recoupés à chaque exécution |
| Taux de cotisation, autres régimes | tous | moyenne / estimée | Comptes de la Sécurité sociale |
| Répartition salarié/employeur, régime général | 1968-2026 | haute | OpenFisca-France, recoupée à chaque exécution |
| Répartition salarié/employeur, autres régimes de salariés | toutes | moyenne / estimée | OpenFisca et textes ; règle 40-60 pour les complémentaires |
| Contribution employeur, État | <!--chiffre:minimum(data/reference/legislation/contribution_employeur_public.csv:annee?regime=fonction_publique_etat&fiabilite=certifiee)-->2006<!--/-->-<!--chiffre:maximum(data/reference/legislation/contribution_employeur_public.csv:annee?regime=fonction_publique_etat&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | Service des retraites de l'État, fiche « Historique des taux de cotisations » |
| Contribution employeur, État (implicite) | 1995-2005 | haute | OpenFisca-France, jaune « pensions » du PLF 2011 — reconstitution dont le producteur refuse les requêtes automatisées |
| Contribution employeur, CNRACL | 1993-2028 | **certifiée** | DILA, base LEGI, décret n° 91-613 du 28 juin 1991, article 5 II |
| Contribution employeur, CNRACL | 1984-1988 | **certifiée** | DILA, base LEGI, décret n° 47-1846 du 19 septembre 1947, article 3 |
| Contribution employeur, CNRACL | 1948-1983, 1989-1992 | haute | OpenFisca-France — la chaîne des versions de l'article 3 est trouée, et la base le démontre |
| Contribution employeur, SNCF (T1 + T2) | 2007-2011 | **certifiée** | DILA, arrêtés annuels du taux T1 (base JORF) et décret n° 2007-1056, article 2 IV (base LEGI) |
| Contribution employeur, SNCF (T1 + T2) | 2012-2018 | haute | OpenFisca-France — le décret cesse de chiffrer T2 après 2011 et le fait évoluer par formule |
| Valeurs d'achat et de service du point, Ircantec | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=ircantec&fiabilite=certifiee)-->1971<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=ircantec&fiabilite=certifiee)-->2021<!--/--> | **certifiée** | Caisse des dépôts, qui gère le régime |
| Valeurs d'achat et de service du point, Agirc | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=agirc&fiabilite=certifiee)-->1947<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=agirc&fiabilite=certifiee)-->2018<!--/--> | **certifiée** | Fédération Agirc-Arrco, sa compilation des valeurs de point |
| Valeurs d'achat et de service du point, Arrco | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=arrco&fiabilite=certifiee)-->1999<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=arrco&fiabilite=certifiee)-->2018<!--/--> | **certifiée** | Fédération Agirc-Arrco, la même compilation |
| Valeurs d'achat et de service du point, UNIRS | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=unirs&fiabilite=certifiee)-->1961<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=unirs&fiabilite=certifiee)-->1998<!--/--> | **certifiée** | Fédération Agirc-Arrco, la même compilation |
| Valeurs du point, Arrco avant 1999 | 1949-1998 | moyenne | l'UNIRS tenant lieu d'Arrco : la valeur est certifiée, la substitution reste une décision du dépôt |
| Valeurs d'acquisition et de service du point, RAFP | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=rafp&fiabilite=certifiee)-->2005<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=rafp&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | ERAFP, dont le conseil d'administration les fixe |
| Valeurs d'achat et de service du point, autres | RCI 2013-2023, IGRANTE et IPACTE 1947-2022 | haute | OpenFisca-France-Pension |
| Valeurs du point, complémentaire des avocats | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=cnbf_complementaire&fiabilite=certifiee)-->2017<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=cnbf_complementaire&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | CNBF, ses barèmes annuels |
| Valeur du point, base des professions libérales | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=cnavpl&mesure=valeur_service&fiabilite=certifiee)-->2004<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=cnavpl&mesure=valeur_service&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | CNAVPL, ses recueils statistiques |
| Taux des deux tranches, base des professions libérales | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=cnavpl&mesure=taux_t1&fiabilite=certifiee)-->2020<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=cnavpl&mesure=taux_t1&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | CNAVPL, le tableau des cotisations de ses recueils, exercice par exercice |
| Valeur de service du point, complémentaire agricole | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=msa_rco&fiabilite=certifiee)-->2005<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=msa_rco&fiabilite=certifiee)-->2025<!--/--> | **certifiée** | DILA, base LEGI, code rural `D. 732-166` |
| Valeur du point, base agricole et valeurs d'achat RCO | — | absentes | hors du code ; voir plus bas |

**Comment la certification fonctionne.** Une valeur n'est `certifiee` que si
elle a été confrontée à un fichier téléchargé depuis le producteur. Le circuit
est le même pour toutes les séries : récupérer, puis confronter.

```bash
python scripts/fetch/insee_bdm.py              # séries longues INSEE
python scripts/fetch/oecd_esperance_vie.py     # espérance de vie à 65 ans
python scripts/fetch/eurostat_mortalite.py     # tables de mortalité par âge
python scripts/fetch/openfisca_plafond.py      # plafond ancien
python scripts/fetch/openfisca_cotisations.py  # taux de cotisation du RG, du public, des non-salariés
python scripts/fetch/openfisca_minimum_contributif.py  # montants du minimum contributif
python scripts/fetch/openfisca_parametres_generation.py  # durée requise, âge d'annulation, par génération
python scripts/fetch/openfisca_points.py       # valeurs du point, depuis 1947
python scripts/fetch/cdc_ircantec.py           # barèmes Ircantec, par son gestionnaire
python scripts/fetch/cnbf_baremes.py           # valeurs du point des avocats
python scripts/fetch/cnavpl_recueils.py        # valeur du point des professions libérales
python scripts/fetch/dila_legi_msa.py          # point de la complémentaire agricole (index LEGI)
python scripts/fetch/dila_legi_minimum_contributif.py  # minimum contributif et plafond (index LEGI)
python scripts/fetch/dila_legi_parametres_retraite.py   # âges, durées, décotes par génération : lit l'index LEGI, en secondes
python scripts/fetch/openfisca_point_indice.py  # point d'indice et barème du minimum garanti
python scripts/fetch/dila_legi_point_indice.py # point d'indice, dans son décret (index LEGI)
python scripts/fetch/dila_legi_smic.py         # SMIC, dans ses décrets de relèvement (index LEGI)
python scripts/fetch/dila_legi_duree_requise.py # durée requise des générations 1953-1957 (index LEGI)
python scripts/fetch/dila_legi_cnracl.py       # contribution employeur de la CNRACL (index LEGI)
python scripts/fetch/dila_legi_contribution_employeur.py  # part patronale de six régimes spéciaux (index, rapide)
python scripts/fetch/dila_legi_decote_fonction_publique.py  # décote de la fonction publique (index LEGI)
python scripts/fetch/dila_legi_minimum_garanti.py  # barème du minimum garanti (index LEGI)
python scripts/fetch/erafp_valeurs_point.py    # valeurs du point du RAFP, par l'ERAFP
python scripts/fetch/jorf_plafond_securite_sociale.py  # plafond ancien, dans ses décrets (index JORF)
python scripts/fetch/sncf_contribution_employeur.py  # contribution SNCF, dans les deux index
python scripts/fetch/dila_legi_minimum_vieillesse.py  # montant de l'ASPA, dans le code (index LEGI)
python scripts/fetch/sre_minimum_garanti.py     # référence du minimum garanti, par le service qui la sert
python scripts/fetch/ined_vallin_mesle.py      # quotients de mortalité d'avant 1986
python scripts/fetch/insee_projections_mortalite.py  # espérances de vie projetées, jusqu'en 2125
python scripts/fetch/eurostat_hicp.py          # contrôle croisé de l'inflation

python scripts/verifier_donnees.py             # confronte, sans rien écrire
python scripts/verifier_donnees.py --appliquer # aligne sur la source et certifie
```

`data/brut/` n'est pas versionné : c'est `data/derive/certification.json` qui
garde la trace du dernier recontrôle — quelle source, quel jour, combien de
valeurs, à quel niveau, et une empreinte de la série reconstruite.

**Les hypothèses de projection ne sont pas certifiables par script, et il faut
le dire.** `verifier_donnees.py` confronte des séries à un producteur ; une
hypothèse de long terme n'a pas de producteur, elle a un auteur. Le fichier
`data/reference/macro/hypotheses_projection.yaml` transcrit donc le jeu du COR
— référence <!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_reference.productivite_reelle*100)-->0,7<!--/--> %, variantes <!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_productivite_basse.productivite_reelle*100)-->0,4<!--/--> % et <!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_productivite_haute.productivite_reelle*100)-->1,0<!--/--> % de croissance annuelle de la
productivité — en nommant son millésime, et rien ne garantit qu'il suive le
prochain rapport autrement qu'à la main. Deux réserves s'y ajoutent : le taux
est appliqué dès 2026 quand le COR ne l'atteint qu'en 2040, et l'inflation de
<!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_reference.inflation*100)-->1,75<!--/--> % est une convention reconduite de ses rapports antérieurs, que les
documents publics de juin 2025 et de juin 2026 ne restatent pas.

**Deux niveaux, deux exigences.** `certifiee` suppose que la source soit le
**producteur** de la donnée : INSEE, Eurostat, OCDE. Une transcription tierce,
même sourcée et reprise automatiquement, plafonne à `haute` — c'est le cas des
années du plafond ancien dont le décret n'a pas été lu, et qui viennent
d'OpenFisca-France. La distinction n'est pas cosmétique : elle dit ce qu'on
saurait vérifier soi-même en remontant d'un cran. Et le plafond montre à quoi
elle sert : sur les trente et une années où les deux chemins existent — la
transcription et le *Journal officiel* —, ils donnent le même chiffre à l'euro
près, ce qui certifie ces trente et une-là et rend les autres un peu moins
incertaines sans les certifier.

### Ce que la certification garantit

**Ce que cela veut dire concrètement.** Les carrières entamées après 1950 —
c'est-à-dire les générations nées à partir de 1930 environ, soit la quasi-totalité
des cas simulés — reposent désormais sur des séries recontrôlées. Les **écarts
entre les trois scénarios** restent plus robustes encore que les niveaux : ils
sont calculés sur les mêmes carrières, avec les mêmes séries, et une erreur
résiduelle se propage dans le même sens aux trois scénarios.

---

## 2. La règle d'indexation domine le scénario rétroactif

Le modèle revalorise par défaut sur la croissance de la masse salariale — le
taux d'équilibre de la répartition. Ce qui suit décrit la règle demandée, le
triple lock inversé (`indexation=triple_lock_inverse`), parce que c'est elle
qui porte les écarts les plus lourds ; les limites propres à la règle par défaut
sont énoncées à la fin de cette section.

Le triple lock inversé, pris à la lettre, retient le minimum entre deux taux
**nominaux** (inflation, salaire moyen) et un taux **réel** (productivité). Dès
que l'inflation dépasse la croissance de la productivité, c'est cette dernière
qui l'emporte.

Sur 1941-2025, les comptes sont revalorisés ×<!--chiffre:mesure(cumul_indexation?regle=triple_lock_inverse&de=1940&a=2025)-->4,9<!--/--> quand les prix sont multipliés
par <!--chiffre:mesure(cumul_indexation?regle=prix&de=1940&a=2025)-->322,2<!--/--> : **un euro cotisé en 1940 conserve, en 2025, <!--chiffre:mesure(conserve?regle=triple_lock_inverse)-->1,5<!--/--> % de sa valeur
réelle.**

Conséquence : dans le scénario rétroactif, l'essentiel de la baisse affichée
vient de la règle d'indexation, pas du passage aux comptes notionnels. Les deux
effets ne sont pas séparables par lecture directe du tableau.

Pour les distinguer :

Comparer, sur la même carrière, la règle « triple lock inversé, tout en
nominal » et la règle « revalorisation portée au compte » — le sélecteur
d'indexation du formulaire, ou `mode_indexation` en Python.

La variante nominale conserve <!--chiffre:mesure(conserve?regle=triple_lock_inverse_nominal)-->69<!--/--> % du pouvoir d'achat sur la même période, tout
en restant plus sévère que l'indexation sur les prix. C'est probablement ce que
vise l'intention d'une règle d'indexation prudente ; le choix reste ouvert.

## 3. Le scénario « système actuel » est une approximation

Reproduire exactement le droit positif de tous les régimes depuis 1930 suppose
un moteur législatif complet, du type de ceux de la DREES (TRAJECTOiRE) ou de
l'Institut des politiques publiques (PENSIPP). Écarts connus :

- **régimes en points** — la pension est calculée en points, sur l'historique
  réel des valeurs d'achat et de service (Agirc depuis 1947, Arrco depuis 1949,
  Ircantec depuis 1949), avec conversion des points aux fusions. S'y ajoutent
  depuis peu deux régimes dont le barème n'est pas un prix d'achat mais un
  NOMBRE DE POINTS par tranche d'assiette : le régime de base des professions
  libérales (<!--chiffre:valeur(data/reference/regimes/non_salaries.yaml:regimes.code=cnavpl.periodes.debut=2015;assiette=plafonnee.points_maximum)-->525<!--/--> points au plafond jusqu'en 2024, <!--chiffre:valeur(data/reference/regimes/non_salaries.yaml:regimes.code=cnavpl.periodes.debut=2025.points_maximum)-->557<!--/--> depuis 2025, <!--chiffre:valeur(data/reference/regimes/non_salaries.yaml:regimes.code=cnavpl.periodes.debut=2024;assiette=plafonnee_5_pass.points_maximum)-->25<!--/--> sur la
  seconde tranche) et la complémentaire agricole (<!--chiffre:valeur(data/reference/regimes/non_salaries.yaml:regimes.code=msa_rco.periodes.debut=2003.points_maximum)-->100<!--/--> points pour <!--chiffre:valeur(data/reference/regimes/non_salaries.yaml:regimes.code=msa_rco.periodes.debut=2003.assiette_repere_smic)-->1 820<!--/--> SMIC).
  Le même régime de base en connaît une troisième forme pour ce qui précède
  2004 : <!--chiffre:valeur(data/reference/regimes/non_salaries.yaml:regimes.code=cnavpl.periodes.debut=1949.points_par_trimestre_valide)-->100<!--/--> POINTS PAR TRIMESTRE VALIDÉ, sans égard au montant cotisé. La complémentaire des
  avocats les a rejoints, avec le prix d'achat publié par la CNBF et les cinq
  tranches en euros de la classe C1, depuis 2019 seulement — les tranches
  antérieures ne sont pas publiées. Restent au rendement instantané, faute
  d'une série de prix d'achat, les complémentaires des sections libérales et de
  l'IRCEC, quelques petits régimes — CAFAT, tranche B de la Polynésie,
  additionnel des enseignants du privé, gérants de débits de tabac, conjoints du
  bâtiment —, et les années postérieures au dernier barème publié de
  l'Agirc-Arrco, de l'Ircantec, du RCI et de la complémentaire des avocats. Le
  RAFP, lui, a sa série ;
- **montée en charge des réformes** — le modèle a trois horloges, comme le
  droit. Ce qui s'ACQUIERT est lu à l'année travaillée : taux de cotisation,
  assiette et ses bornes, plafond de la Sécurité sociale, prix d'achat du point,
  heures de SMIC pour valider un trimestre. Ce qui commande la MONTÉE EN CHARGE
  est lu à la génération : durée requise, âge d'ouverture, âge d'annulation de
  la décote, coefficient de minoration et nombre d'années retenues au salaire de
  référence — quatre de ces cinq tables sont lues dans le texte même des
  articles du code, et recontrôlées à chaque exécution. Ce qui LIQUIDE est lu à l'année
  de liquidation : formule du régime, valeur de service du point, décote de la
  fonction publique et barème du minimum garanti, comme leurs articles
  l'écrivent. Reste approchée la montée en charge propre à chaque régime
  spécial ;
- **avantages datés** — la fiche de chaque période dit ce que le régime
  accordait cette année-là, et le moteur ne sert que cela : ni minimum
  contributif avant 1983, ni surcote avant 2004, ni trimestres pour enfants
  avant 1972. Restent hors du modèle les avantages familiaux des régimes que
  leur fiche ne déclare pas, faute de barème sourcé : le régime de base des
  professions libérales, celui des avocats, et celui des exploitants
  agricoles. La SURCOTE de l'Ircantec, elle, en est sortie : le IV de
  l'article 16 de l'arrêté du 30 décembre 1970 est servi depuis le
  1er janvier 2010, à ses deux taux — <!--chiffre:mesure(constante?de=retraite_notionnelle.droit.liquider&nom=_SURCOTE_IRCANTEC_AGE&echelle=100)-->0,75<!--/--> % par trimestre entier écoulé
  au-delà de l'âge du taux plein, <!--chiffre:mesure(constante?de=retraite_notionnelle.droit.liquider&nom=_SURCOTE_IRCANTEC_DUREE&echelle=100)-->0,625<!--/--> % par trimestre cotisé au-delà de la
  durée requise en deçà de cet âge —, et le coefficient d'un régime en points
  peut désormais dépasser un, des deux côtés du portage. Les neuf autres
  régimes en points dont la fiche écrit une surcote la servent aussi depuis
  l'action 22, chacun à sa règle, lue dans son texte : la CNAVPL et la MSA des
  non-salariés à celle du régime général — trimestres cotisés au-delà de l'âge
  légal et de la durée requise, R. 643-8 et D. 732-42 —, les sept
  complémentaires de sections libérales À L'ÂGE SEUL, en trimestres civils
  entiers écoulés depuis l'âge que leurs statuts nomment — soixante-deux ans à
  la CARMF et à l'ASV, soixante-cinq à la CAVEC, l'âge du taux plein à la
  CARPIMKO, à la CAVP, à la CPRN et à la CIPAV —, et bornés comme ils le
  sont : soixante-dix ans chez les médecins et, jusqu'en 2023, les notaires,
  vingt trimestres à la CAVEC et à la CARPIMKO, douze à la CAVP, années
  pleines seulement à la CIPAV et à la CARMF d'avant 2017. Rien n'est servi
  avant le texte qui date chaque règle, et les taux que les fiches
  reportaient en arrière sans texte — <!--chiffre:illustration()-->0,75<!--/--> % à la CARPIMKO, <!--chiffre:illustration()-->1<!--/--> % à la CPRN —
  sont ceux des arrêtés. Ce que la fiche ne porte pas est dit dans ses
  notes : la CIPAV ne majore que les points des trente premières années, la
  CAVP borne les générations 1951 à 1955 à un ou deux ans, la CNAVPL sert
  <!--chiffre:valeur(data/reference/regimes/non_salaries.yaml:regimes.code=cnavpl.periodes.debut=2024;assiette=plafonnee.surcote_par_trimestre*100)-->1,25<!--/--> % aux liquidations de 2024 et non aux trimestres accomplis depuis
  septembre 2023, la MSA ramène à <!--chiffre:valeur(data/reference/regimes/non_salaries.yaml:regimes.code=msa_non_salaries.periodes.debut=2004.surcote_par_trimestre*100)-->0,75<!--/--> % l'escalier de <!--chiffre:illustration()-->3<!--/-->, <!--chiffre:illustration()-->4<!--/--> et <!--chiffre:illustration()-->5<!--/--> % d'avant
  2009 ;
- **revalorisation des salaires portés au compte** — le modèle ne les
  reconstitue plus, il les LIT dans la circulaire annuelle de la Cnav
  (`legislation/revalorisation_salaires.csv`, perceptions 1930-2025). Il les
  approchait par « les salaires jusqu'en 1986, les prix depuis » ; cette
  approximation sur-revalorise les salaires anciens.
  Dix colonnes publiées sont dans le dépôt ; hors d'elles, le coefficient est
  ancré sur la plus proche, et l'approximation ne reprend toute la main
  qu'avant 1930, où elle joue À LA HAUSSE ;
- **départs anticipés** — la carrière longue est modélisée, et sert à dire si le
  droit ouvre la liquidation demandée. La pénibilité, l'invalidité, l'inaptitude
  et le handicap ne le sont pas : ils demandent des informations médicales ou
  professionnelles que le modèle ne collecte pas ;
- **polypensionnés** — chaque régime liquide sur ses seules années, et la
  durée acquise dans chacun est comptée séparément ; mais un régime et celui
  qui lui succède ne sont pas deux régimes, et liquident ensemble (voir « Les
  régimes alignés » ci-dessous). La liquidation unique des régimes alignés
  DISTINCTS (LURA) et sa proratisation croisée du salaire annuel moyen sont
  servies depuis le 22 septembre 2026 ; seule en reste dehors sa troisième
  condition, la retraite de même nature déjà obtenue avant le 1er juillet
  2017 (voir « Ce qui reste hors du modèle »).

Un écart de quelques pour cent avec la pension réelle est attendu.

### Ce que dit la confrontation à une seconde implémentation

Le scénario 1 est l'étalon : tous les écarts affichés se mesurent par rapport à
lui, et il n'avait aucune contre-expertise. Aucun simulateur officiel n'est
automatisable — M@rel exige FranceConnect et le relevé de carrière réel, sans
mode anonyme ni API — et relire deux fois le même code ne prouve rien : une
réimplémentation écrite par la même main hérite des mêmes hypothèses.

**OpenFisca-France-Pension** comble ce trou. Ce n'est pas une source officielle,
c'est un autre MODÈLE — le module « retraites » de l'écosystème OpenFisca — mais
il est écrit par d'autres à partir des mêmes textes.
`scripts/fetch/openfisca_regime_general.py` y calcule dix profils à salaire
nominal constant et fige le relevé dans `tests/temoins/`, que `tests/test_oracle.py`
rejoue sans avoir à installer le paquet.

**Cinq familles de régimes y passent aujourd'hui**, et c'est tout ce
qu'OpenFisca expose : le régime général, la pension civile (État et CNRACL),
l'Arrco d'avant 2019, l'Agirc des cadres et l'Ircantec des agents non
titulaires — <!--chiffre:mesure(profils_oracle)-->48<!--/--> profils en tout. Les régimes alignés — MSA des
salariés agricoles, artisans, commerçants — n'ont chez lui aucun module, et
n'en ont pas besoin : la loi les calcule comme le régime général, et c'est à
l'oracle du régime général qu'ils se confrontent. Restent hors de portée le
régime unifié Agirc-Arrco, dont son code lève une exception, et tout ce qui
n'est ni salarié ni fonctionnaire : les régimes spéciaux, les libéraux, les
exploitants agricoles, que personne d'autre ne modélise. Les exploitants sont
le seul trou qui porte plus d'un million d'assurés — 1 023 064 retraités de
droit direct en 2024 —, et il ne se comblera pas par cette voie : leur régime
est MIXTE, une retraite forfaitaire plus une proportionnelle en points, sans
équivalent au régime général auquel l'opposer.

Le résultat, sur dix profils — et les régimes alignés le partagent, puisque
leur pension est celle du régime général :

| Grandeur | Accord |
|---|---|
| Durée d'assurance | **exacte** sur les dix |
| Trimestres de décote | **exacts** sur les dix |
| Taux de liquidation | **exact** sur les dix |
| Coefficient de proratisation | **exact** sur les dix |
| Salaire annuel moyen | jusqu'à <!--chiffre:mesure(ecart_openfisca)-->2,40<!--/--> %, **et c'est OpenFisca qui s'écarte de la source** |
| Pension de base | l'écart du salaire annuel moyen, et rien d'autre |

Le décompte des trimestres de décote est le contrôle le plus exigeant du lot :
il met en jeu la durée requise par génération, l'âge d'annulation par
génération, la règle du minimum entre les deux décomptes, le plafond de vingt
trimestres et l'arrondi à l'entier supérieur. Cinq tables et trois règles
tombent juste ensemble, dix fois.

Le salaire de référence, lui, a divergé — et l'enquête qu'il a déclenchée a
trouvé une erreur de chaque côté, la nôtre d'abord.

Il s'écartait de +0,30 % à +7,55 %, toujours dans le même sens, parce que le
modèle APPROCHAIT les coefficients de revalorisation des salaires portés au
compte : « les salaires jusqu'en 1986, les prix depuis ». Mesurée sur les
coefficients réels, cette approximation sur-revalorise les salaires anciens de
**12,1 % sur 1970-2018** et de **13,6 % sur 1980-2018**. L'erreur comptait
double, parce que la grandeur compte double : le salaire de référence retient
les N MEILLEURES années, et « meilleures » se juge sur des salaires revalorisés
— changer les coefficients ne déplace pas seulement le niveau de chaque année,
cela change lesquelles sont retenues.

Le dépôt a d'abord repris la table cumulée d'OpenFisca, faute d'avoir cherché
plus haut. **C'était une erreur de méthode, et elle a duré un commit.** Une
seconde implémentation est une contre-expertise ; ce n'est pas une source. La
source existe : la Cnav publie chaque année, dans sa circulaire de
revalorisation, la table entière des coefficients qu'elle applique. Confrontée à
celle du 9 janvier 2023, la table d'OpenFisca s'en écarte :

- de **−3 % à −5,5 %** sur toutes les perceptions postérieures à 1990, un
  déficit à peu près uniforme — c'est la revalorisation exceptionnelle de 4 % du
  1<sup>er</sup> juillet 2022 (loi « pouvoir d'achat ») qui lui manque ;
- de **−17 % à +10 %**, sans régularité, sur les années 1949-1962.

Le modèle lit donc la circulaire, et le désaccord résiduel avec OpenFisca —
jusqu'à <!--chiffre:mesure(ecart_openfisca)-->2,40<!--/--> %, toujours dans le même sens — n'est plus le nôtre.

**Le coefficient se lit dans une colonne, par rapport de deux de ses valeurs.**
L'arrêté annuel applique un coefficient unique à tous les salaires déjà portés
au compte, quelle que soit leur année de perception : une colonne suffit donc,
en théorie, à en reconstruire toutes les autres.

En pratique, non — et c'est mesuré. La caisse arrondit sa table publiée à trois
décimales et repart chaque année de la précédente : les arrondis s'accumulent, et
reconstruire une colonne depuis une autre dérive avec la distance. Le tableau
donne l'écart relatif entre une colonne publiée et sa reconstruction, en
médiane sur les années de perception qu'elle porte :

| Colonne de janvier reconstruite | depuis 2026 | depuis la colonne suivante |
|---|---|---|
| 2025 (1 an) | <!--chiffre:mesure(derive_revalorisation?annee=2025&ancre=2026)-->0,012<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2025&ancre=voisine)-->0,012<!--/--> % |
| 2024 (<!--chiffre:illustration()-->2<!--/--> ans) | <!--chiffre:mesure(derive_revalorisation?annee=2024&ancre=2026)-->0,019<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2024&ancre=voisine)-->0,005<!--/--> % |
| 2023 (<!--chiffre:illustration()-->3<!--/--> ans) | <!--chiffre:mesure(derive_revalorisation?annee=2023&ancre=2026)-->0,059<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2023&ancre=voisine)-->0,009<!--/--> % |
| 2022 (<!--chiffre:illustration()-->4<!--/--> ans) | <!--chiffre:mesure(derive_revalorisation?annee=2022&ancre=2026)-->0,096<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2022&ancre=voisine)-->0,028<!--/--> % |
| 2021 (<!--chiffre:illustration()-->5<!--/--> ans) | <!--chiffre:mesure(derive_revalorisation?annee=2021&ancre=2026)-->0,127<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2021&ancre=voisine)-->0,005<!--/--> % |
| 2020 (<!--chiffre:illustration()-->6<!--/--> ans) | <!--chiffre:mesure(derive_revalorisation?annee=2020&ancre=2026)-->0,130<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2020&ancre=voisine)-->0,006<!--/--> % |
| 2019 (<!--chiffre:illustration()-->7<!--/--> ans) | <!--chiffre:mesure(derive_revalorisation?annee=2019&ancre=2026)-->0,135<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2019&ancre=voisine)-->0,007<!--/--> % |

Le dépôt n'a d'abord gardé que la colonne la plus récente, en annonçant 0,13 %
sur la foi d'un seul recoupement.

**Le dépôt porte maintenant <!--chiffre:distinctes(data/reference/legislation/revalorisation_salaires.csv:date_effet)-->10<!--/--> colonnes**, de 2017 à 2026 : le modèle sert
la colonne publiée quand elle existe — l'écart est alors nul, pas petit — et
ancre sinon sur la plus proche. Ce que cela gagne dépend de ce qu'on mesure. En
médiane, la reconstruction de la colonne la plus éloignée tombe de
<!--chiffre:mesure(derive_revalorisation?annee=2019&ancre=2026)-->0,135<!--/--> à <!--chiffre:mesure(derive_revalorisation?annee=2019&ancre=voisine)-->0,007<!--/--> %. Au pire, toutes colonnes et toutes années de perception
confondues, elle ne tombe que de <!--chiffre:mesure(derive_revalorisation?ancre=recente&stat=max)-->0,26<!--/--> à <!--chiffre:mesure(derive_revalorisation?ancre=voisine&stat=max)-->0,12<!--/--> %, et c'est ce pire que
`test_la_reconstruction_entre_colonnes_reste_dans_sa_derive` tient sous
<!--chiffre:tenu(test_la_reconstruction_entre_colonnes_reste_dans_sa_derive)-->0,2<!--/--> %. Le récupérateur recoupe chaque colonne contre chacune des autres
à chaque exécution et refuse d'écrire si l'une s'écarte, et deux tests rejouent
les colonnes figées dans `tests/temoins/`.

Ce document a un temps affirmé qu'« aucune formule ne reproduit les arrêtés,
une série d'ancrages fuit de 20 % ». Cette mesure portait sur la table
d'OpenFisca : ce sont ses incohérences qu'elle mesurait, pas celles du droit.

Ce que cela ne referme pas, et les trois bornes sont différentes.

- **Avant 2017**, aucune circulaire n'est accessible en ligne : les liquidations
  antérieures sont reconstruites depuis la colonne d'octobre 2017, la plus
  proche, et la dérive y est **invérifiable**. Extrapolée depuis le profil
  mesuré ci-dessus, elle croît d'environ trois centièmes de pour cent par année
  d'écart.
- **Après 2026**, le coefficient est ancré sur la dernière colonne et
  l'approximation ne couvre que les dernières années ; avant 1930, il n'y a rien
  sur quoi ancrer et elle reprend toute la main, à la hausse.
- **Le mois existe désormais, et il désigne la colonne applicable.** Le modèle
  retenait l'état au 1<sup>er</sup> janvier : la revalorisation s'étant
  appliquée au 1<sup>er</sup> avril de 2009 à 2013, puis au 1<sup>er</sup>
  octobre jusqu'en 2017, une liquidation de cette période était lue avant la
  revalorisation de son année — **0,52 % en médiane, 0,93 % au maximum**,
  toujours à la baisse. Le cas le plus lourd n'était pas celui-là : la
  **revalorisation exceptionnelle du 1<sup>er</sup> juillet 2022** dépasse celle
  du 1<sup>er</sup> janvier de **3,9 %**, et toutes les liquidations du second
  semestre 2022 lisaient la colonne de janvier. La colonne retenue est
  maintenant la plus récente dont la date d'effet n'est pas postérieure à la
  liquidation, ce que le mois suffit à trancher. Ce qui reste : les années
  qu'aucune circulaire ne couvre, où le modèle passe par la colonne la plus
  proche et son rapport de deux valeurs — le mois n'y change rien, faute de
  colonne à désigner.

Les régimes qui liquident sur le dernier traitement ou les six derniers mois ne
portent aucun salaire à un compte : les coefficients de la Cnav ne leur sont pas
appliqués.

Trois désaccords sont sortis de la confrontation, **et pas tous du même côté**.
Chez nous : la durée de proratisation, confondue avec la durée requise, et les
coefficients de revalorisation, approchés au lieu d'être lus — corrigés tous
deux, et ce sont les paragraphes précédents. Chez lui, deux fois. Sa table de
revalorisation, à laquelle il manque la revalorisation exceptionnelle de juillet
2022 — c'est le paragraphe précédent. Et : une table de durée requise
antérieure à la réforme du 14 avril 2023, qui oppose <!--chiffre:illustration()-->169<!--/--> trimestres à la
génération 1965 là où l'article L. 161-17-3, lu dans la base LEGI, en donne
<!--chiffre:cellule(data/reference/legislation/duree_assurance_requise.csv:trimestres?generation=1965)-->170<!--/--> depuis la suspension de la réforme.
**Un désaccord ne désigne donc pas d'office le coupable.**

Quatre bornes à connaître, et elles sont étroites :

* **le régime unifié Agirc-Arrco est hors de portée.** Son code demande le
  paramètre `agirc_arrco.salaire_de_reference.salaire_reference_en_euros`, que
  les barèmes livrés ne définissent pas — ils portent
  `salaire_reference_prix_achat_valeur_nominale`. Toute liquidation postérieure
  à 2019 y lève une erreur. L'Arrco d'avant, lui, se confronte : voir plus bas ;
* **les liquidations antérieures à 2025.** Ses barèmes s'arrêtent : valeur du
  point Agirc-Arrco en novembre 2024, revalorisations CNAV en 2023. Cinq des
  sept générations de la grille de cas types sont hors de portée ;
* **il rend zéro sans se plaindre.** Sans `simulation.max_spiral_loops`, la
  durée d'assurance, le coefficient de proratisation et la pension valent tous
  zéro, sans qu'aucune exception ne soit levée. Un oracle silencieusement nul
  valide tout : le récupérateur refuse donc d'écrire un profil dont la durée ou
  la pension serait nulle, et le test le revérifie ;
* **et ce même réglage a une borne HAUTE**, découverte en écrivant les oracles
  de l'Agirc et de l'Ircantec. Le total de points d'un régime en points lit le
  total de l'année précédente et remonte ainsi jusqu'à ce que
  `max_spiral_loops` l'arrête. Laissé à cent, il atteint 1947 à l'Agirc, dont
  la formule de points commence au 1<sup>er</sup> janvier quand son prix
  d'achat commence au 1<sup>er</sup> avril, et 1910 à l'Ircantec, dont la
  cotisation lit un plafond de la Sécurité sociale qu'OpenFisca ne définit pas
  avant 1931 : `ParameterNotFoundError` dans les deux cas. Le nombre de
  reprises est donc calculé pour que la remontée s'arrête à la première année
  sûre, et le récupérateur vérifie qu'il couvre encore la carrière. Trop peu de
  reprises tronque la carrière en silence, trop lève une exception : la fenêtre
  est étroite des deux côtés.

### Ce que disent les exemples publiés par les caisses

OpenFisca est un autre modèle ; les caisses, elles, publient des EXEMPLES —
une carrière de trois lignes dont la réponse est écrite par l'organisme qui
applique la règle. `tests/temoins/exemples_officiels.yaml` en transcrit
<!--chiffre:entrees(tests/temoins/exemples_officiels.yaml:exemples)-->54<!--/-->, chacun avec sa source et sa date de vérification, et
`tests/test_oracle.py` les rejoue : le test construit la carrière — une
affiliation, un salaire constant, le nombre de trimestres de l'exemple, l'âge
d'entrée cherché au mois près — et compare la grandeur que l'exemple nomme.

| Source | Ce qu'elle fait rejouer | Accord |
|---|---|---|
| service-public.gouv.fr, fiches F19666 et F20349 | décote du privé et de la fonction publique, né en 1964, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->159<!--/--> trimestres sur 170 : taux <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->43,125<!--/--> %, réduction de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->13,75<!--/--> % | **exact** |
| fiches F19643 et F16494 | surcote du privé et de la fonction publique, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->4<!--/--> trimestres civils après l'âge légal : +<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->5<!--/--> % | **exact**, une fois la période de référence comptée au trimestre civil |
| fiches F21552 et F36464 | taux plein à 170, taux plein à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->67<!--/--> ans avec 158, taux minoré à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->65<!--/--> ans (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->45<!--/--> %), proratisation <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->158<!--/-->/170 | **exact** |
| actualité A15703 | minimum contributif 2026 : <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->170<!--/--> trimestres dont 135 cotisés, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->873,53<!--/--> € par mois | **exact** au centime |
| circulaire Cnav 2026-07 | âges légaux et durées de la suspension pour trois dates de naissance, décote d'un né en novembre 1961 (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->44,375<!--/--> %) | **exact**, une fois les tables réécrites |
| circulaire Cnav 2026-29 | carrière longue par génération, 1964 à 1971, ouverte à la borne et refusée un trimestre plus tôt | **exact**, une fois la borne lue par génération |
| circulaire Cnav 2018-04 | surcote à un, deux et trois taux (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->2,5<!--/--> %, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->4,75<!--/--> %, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->10,25<!--/--> %) | **exact**, une fois le barème daté |
| fiche F16336 et circulaire carrière Cnav 2017-01, fiche 6.2b | huit trimestres par enfant au régime général — quatre de maternité, quatre d'éducation | **exact** |
| fiche F37311 | bonification de la fonction publique : quatre trimestres par enfant né avant 2004, deux pour ceux nés depuis | **exact** |
| circulaire Cnav 2022-26 | assiette de la majoration pour trois enfants : <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->10<!--/--> % de la retraite telle qu'elle est servie, surcotée, décotée ou pile au taux plein | **exact** |
| ENIM, pages « Le mode de calcul » et « Les conditions d'attribution » | marin : bonification de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->5<!--/--> % dès deux enfants (R. 14), pension d'ancienneté ouverte à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->50<!--/--> ans pour <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->25<!--/--> ans de services et refusée un trimestre plus tôt (R. 2) | **exact** |
| CARCDSF, CARMF et CAVAMAC, pages et document d'exemples des sections libérales | la mère de deux enfants au taux plein dès <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->65<!--/--> ans à la CARCDSF ; le coefficient de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->1,15<!--/--> à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->65<!--/--> ans de la CARMF ; à la CAVAMAC, la décote du régime de base au plus favorable de l'âge et de la durée (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->5<!--/--> %), sa surcote de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->7,5<!--/--> % pour six trimestres, et la décote de la complémentaire par l'âge seul (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->6,25<!--/--> %) | **exact**, une fois les complémentaires minorées par l'âge seul |
| Cour des comptes, « Les retraites des fonctionnaires de l'État », tableau n° 20 | durée requise des emplois classés, génération par génération : super-active <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->166<!--/--> trimestres pour 1965, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->168<!--/--> jusqu'en août 1971, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->169<!--/--> ensuite ; active <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->168<!--/--> pour 1965 et jusqu'en août 1966 | **exact**, une fois la durée lue à l'année d'ouverture du droit |
| Service des retraites de l'État, pages « La décote » et « La surcote » | la même fonctionnaire née en mars 1962, à l'âge légal avec <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->163<!--/--> trimestres sur <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->169<!--/--> : décote de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->7,5<!--/--> % ; à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->64<!--/--> ans avec <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->175<!--/--> : surcote de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->7,5<!--/--> % | **exact**, une fois la pension datée au premier du mois qui suit la cessation, comme la caisse la date |

**Ce que la confrontation a trouvé, dans l'ordre.** Le premier exemple lu
contredisait les tables certifiées du dépôt : non que le récupérateur se soit
trompé, mais parce que le droit avait changé depuis le dump qu'il avait lu —
la suspension de la réforme est de décembre 2025, ses décrets de mai 2026, et
le dump LEGI du dépôt de juillet 2025. Une table certifiée est certifiée à une
date ; c'est pourquoi les lignes réécrites sont redescendues au niveau
`moyenne` plutôt que de porter un `certifiee` que rien ne soutient plus, et
pourquoi ce niveau remonte jusqu'au résultat affiché à qui est né de 1964 à
1968 — jusqu'à ce que l'action 27, le même jour, fasse relire les articles
réécrits au récupérateur dans l'index LEGI du dépôt, qui porte les
incréments quotidiens de la DILA : toutes les lignes sont redevenues
`certifiee`, sans qu'un chiffre bouge. Puis la surcote : 5 % dans les deux fiches quand le modèle en servait
6,25, parce qu'il comptait le trimestre de l'anniversaire ; et les trois
exemples de 2018, qui ne se rejouent qu'avec le taux de chaque trimestre à sa
date. Puis la carrière longue, dont la borne des vingt ans n'avait jamais été
lue par génération. Le minimum contributif, la décote, la proratisation, le
taux plein sont tombés justes du premier coup — c'est aussi un résultat.

**Six exemples de plus, le 21 septembre 2026, et ce qu'ils ont demandé de
neuf.** Les enfants n'avaient aucun témoin — ni les trimestres qu'ils
accordent, ni la majoration de 10 % —, et pour une raison de forme : aucune
caisse ne publie une carrière entière dont elle donne la durée d'assurance.
Ce qu'elle publie, c'est **le nombre de trimestres ajoutés par enfant**, et
**le taux de la majoration**. Deux grandeurs neuves ont donc été ajoutées au
banc, qui se mesurent l'une et l'autre sans rien recalculer du modèle :
`trimestres_de_majoration_enfants` rejoue LA MÊME carrière sans enfant et
compare les deux durées — l'écart, lui, ne dépend ni de l'âge d'entrée ni de
la durée requise de la génération ; `majoration_enfants_sur_pensions` rapporte
la majoration servie à la somme des pensions de régime. Les six exemples
tombent justes : 16 trimestres pour deux enfants au régime général, 24 pour
trois, 8 pour deux enfants nés avant 2004 dans la fonction publique et 4 pour
deux enfants nés depuis — et 10 % exactement dans les trois cas, sur une
carrière surcotée à 58,125 %, au taux plein, et minorée à 41,25 %.

Ce dernier point est ce que la circulaire 2022-26 tient à dire et que le
modèle aurait pu manquer : « la surcote majore la retraite et fait partie
intégrante de l'avantage de base », si bien que la majoration pour enfants
« est donc calculée sur la base du montant annuel de la retraite, majorée par
la surcote ». Son exemple le chiffre — <!--chiffre:illustration()-->10<!--/--> % × (600 + 22,50) = 62,25 — et
c'est un ordre d'opérations, pas un barème : appliquer les <!--chiffre:illustration()-->10<!--/--> % à la pension
d'AVANT la surcote rendrait <!--chiffre:illustration()-->9,52<!--/--> % de celle d'après, et le témoin le verrait.

**Une circulaire annulée ne certifie plus rien.** Les six témoins de carrière
longue citaient la circulaire Cnav 2026-17 du 12 juin 2026, que la 2026-29 du
4 septembre a annulée et remplacée. Ses âges et ses durées ont été relus ligne
à ligne dans la circulaire en vigueur : aucun n'a bougé — 60 ans et 6 mois et
170 trimestres pour 1964, 60 ans et 9 mois pour 1965, deux ans et six mois
avant l'âge légal de 1966 à 1969 — mais les témoins citent désormais celle qui
fait foi. C'est la même leçon qu'en juillet, d'un cran plus loin : une table
certifiée l'est à une date, et une SOURCE aussi.

**Ce que les exemples ne couvrent pas.** Ils restent courts par construction :
une affiliation, pas de polypension, pas de carrière hachée. Les vingt-quatre
et vingt-trois années des parents et les âges des catégories actives n'ont pas
d'exemple publié que le dépôt ait trouvé : ils sont transcrits du texte, et
attendent le leur. La durée requise des catégories actives a trouvé le sien, et
il ne vient pas d'une caisse : c'est la Cour des comptes qui la publie
génération par génération, et sa table a démenti celle du dépôt. Les trimestres réputés cotisés
de la carrière longue en ont un, maintenant lu — les trois exemples du point
1.2 de la circulaire 2026-29 —, mais il ne se rejoue pas : il arbitre entre
des périodes assimilées de nature différente, maladie, chômage, service
national, invalidité, maternité, que le modèle ne distingue pas dans une
carrière qu'il synthétise. Le rejouer demanderait d'abord de porter ces
natures, ce que l'entrée `carriere_longue_reputes_cotises_autres` du registre
de veille dit toujours.

**Ce que cette source vaut, et ce qu'elle ne vaut pas.** Un exemple de
circulaire est antérieur à la règle qui le suit — ceux de 2018 valent pour le
droit de 2018 — et une fiche de service-public est réécrite sans que son
exemple le soit toujours : chaque désaccord se tranche par le texte, jamais
par l'exemple seul. Mais quand les <!--chiffre:entrees(tests/temoins/exemples_officiels.yaml:exemples)-->54<!--/--> tombent justes ensemble, sur
une douzaine de sources et autant de règles, c'est le droit que le modèle applique, et non une
lecture qu'il aurait de lui.

### La pension d'aujourd'hui d'un retraité : ce qui est lu, et ce qui est reconstitué

Le simulateur montre à qui est déjà parti la pension qu'il touche cette année,
et non plus celle de son premier mois ramenée par l'indice des prix. Chaque
régime la revalorise par son texte (`src/retraite_notionnelle/revalorisation.py`,
porté dans `moteur/js/revalorisation.js`). L'écart n'est pas un détail : le
salarié non cadre du cas type, parti en janvier 2012, touche en 2026
<!--chiffre:mesure(aujourd_hui?generation=1950&niveau=0.8)-->−3,4<!--/--> % de
moins que sa pension de départ ramenée par les prix — ce que la page lui
affichait. Le calcul est exact là où un texte donne un coefficient ou une
valeur de point ; ailleurs il est reconstitué, et le dépliant « Votre pension,
de votre départ à aujourd'hui » le dit au retraité concerné.

**Ce qui est lu.** Le régime général et les régimes alignés : chaque date
d'effet depuis 1949, les cinq tranches de 2020 comprises, dans le barème de la
Cnav. Les régimes en points : la valeur de service de l'année, le long des
fusions et des changements d'échelle — le point Arrco d'avant 1999 est converti
à l'échelle de l'année. La fonction publique depuis 2004 : un décret par an
jusqu'en 2008, puis l'article L. 161-23-1. La majoration pour enfants suit,
part par part, le régime qui la porte. Deux contrôles le tiennent : le cas
type, refait à la main coefficient par coefficient
(`tests/test_revalorisation.py`), et les cas types du COR, figure 3.14 du
rapport de juin 2026, dont le non-cadre des quatre générations est retrouvé en
2026 à <!--chiffre:tenu(test_le_pouvoir_d_achat_du_non_cadre_du_cor_est_retrouve)-->0,1<!--/-->
point et, pour la génération 1952, année après année à
<!--chiffre:tenu(test_le_non_cadre_de_1952_se_suit_annee_apres_annee)-->0,3<!--/-->
point.

**Ce qui est reconstitué.**

- *La péréquation de la fonction publique, avant 2004.* La pension suivait le
  traitement de l'indice auquel elle avait été liquidée. Le modèle suit la
  valeur du point d'indice, et non les tableaux d'assimilation qui relevaient
  aussi les pensions d'un grade réformé : un fonctionnaire parti avant 2004
  dont le corps a été revalorisé depuis touche davantage que ce que la page
  lui montre.
- *Les régimes spéciaux avant 2009.* Leurs pensions suivaient les salaires de
  leurs actifs, qu'aucune série publique ne donne ; la règle du régime général
  en tient lieu, et la fiabilité affichée tombe à « estimée ».
- *Les régimes en points au-delà de leur dernière valeur publiée* — le régime
  de base des libéraux en 2026 — suivent la règle générale, comme ceux dont le
  dépôt ne porte pas la série des valeurs de service, la complémentaire de la
  Cipav par exemple ; la fiabilité affichée le dit.
- *La revalorisation du jour du départ, dans la fonction publique depuis
  2009.* Les décrets de 2004 à 2007 la servaient aux pensions « dont la date
  d'effet est au plus tard » ce jour-là ; aucun texte lu ne le redit sous
  l'article L. 161-23-1, et le modèle prolonge la règle. Un départ au
  1er janvier 2024 reçoit ainsi la revalorisation de ce jour-là.
- *La tranche de 2020 d'une pension de la fonction publique prise le
  1er janvier 2020.* L'article 81 de la loi n° 2019-1446 choisit le
  coefficient sur la retraite totale reçue le mois précédent, nulle ici : le
  modèle sert le coefficient des petites retraites. Aucune circulaire lue ne
  dit comment le service des retraites de l'État l'a appliqué.
- *Ce qui n'est pas une revalorisation* n'est pas servi : la prime
  exceptionnelle de 2015 aux petites retraites, notamment. Et la pension
  d'aujourd'hui est calculée en brut, puis nette aux prélèvements de cette
  année — la CSG du départ n'intervient nulle part.

**Le cadre du COR s'écarte davantage, et la cause n'est pas trouvée.** Le
dépôt le retrouve à
<!--chiffre:tenu(test_le_cadre_du_cor_est_retrouve_a_un_tiers_de_point)-->0,2<!--/-->
point en 2025, et à
<!--chiffre:tenu(test_le_cadre_du_cor_est_retrouve_a_un_tiers_de_point)-->0,4<!--/-->
point en 2026, l'année prévisionnelle du rapport, toujours du côté d'une perte
plus forte. Aucune hypothèse d'inflation ou de revalorisation de novembre ne le
résorbe sans ouvrir l'écart du non-cadre, et les conventions publiées de
l'annexe n'en disent pas davantage.

**Ce qui reste celui du départ.** Le graphique des cumuls de la trajectoire
additionne la pension du premier mois, supposée garder son pouvoir d'achat, et
sa légende le dit. Les systèmes 2 à 4 ne sont pas le droit : leur pension
servie suit la règle que le modèle prête aux comptes notionnels, celle de la
page Coût, et la garantie vieillesse du système 4 se recalcule sur la pension
d'aujourd'hui.

---

## 4. Régimes incomplets, et de combien

Un régime « incomplet » n’est pas un régime absent : les <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=modelise|partiel)-->74<!--/--> régimes du catalogue
calculent tous une pension. Ce qui manque est, chaque fois, un ÉTAGE ou un
BARÈME qu'aucune source publique ne donne en série. Le tableau dit lequel, ce
qui le remplace, et **dans quel sens** l'approximation joue — car un modèle dont
on ignore le sens de l'erreur ne se corrige pas dans la tête du lecteur.

| Régime | Ce qui manque | Ce qui le remplace | Sens et ordre de grandeur |
|---|---|---|---|
| Professions libérales (CNAVPL) | la SECTION B du complémentaire des notaires, dont les bornes de classes ne sont publiées nulle part ; le volet CAPITALISÉ de la CAVP ; le complémentaire de la CAVOM d'avant 2016, qui prélevait par classes et dont la grille n'est nulle part ; le montant de la cotisation FORFAITAIRE du régime de base d'avant 2004 — qui ne commande plus la pension, seulement le flux versé au compte notionnel | le régime de base, en points plafonnés à <!--chiffre:valeur(data/reference/regimes/non_salaries.yaml:regimes.code=cnavpl.periodes.debut=2025.points_maximum)-->557<!--/-->, PLUS le complémentaire de la section : les DIX sections en ont un maintenant — CARMF, CARCDSF, CNBF, CAVEC, CAVP (volet réparti), CARPIMKO, CARPV, CAVOM (depuis 2016), CAVAMAC, CPRN (section C), et la Cipav pour le statut générique | **sous-estime** la pension d'un notaire de près de quatre dixièmes de son complémentaire, et celle d'un officier ministériel de tout son complémentaire d'avant 2016. Pour la CAVAMAC et la CPRN, l'assiette elle-même est reconstituée par un FACTEUR moyen — commissions, produits de l'office — et ne décrit aucun assuré en particulier |
| Marins (ENIM) | les salaires forfaitaires d'avant 2008, que les textes de l'index ne chiffrent pas ; la CATÉGORIE du marin, que le décret définit par le métier et qu'une carrière saisie ne porte pas, et la catégorie MOYENNE des trente-six derniers mois qui fait le salaire de référence (R. 11) ; le décompte des services au semestre (R. 12) ; la pension d'invalidité, seule exception au plafond de vingt-cinq annuités qui ne soit pas servie | la grille des vingt forfaits lue au Journal officiel depuis 2008, la catégorie la plus proche du revenu — convention nommée —, et la grille de 2008 ramenée par le salaire moyen avant ; le plafond de vingt-cinq annuités avant cinquante-cinq ans est porté | **estimé** avant 2008, la grille de 2008 étant ramenée par le salaire moyen ; l'écart de catégorie et de décompte tient à une catégorie et à un trimestre au plus ; la levée du plafond à cinquante-deux ans et demi pour trente-sept annuités et demie est servie depuis le 22 septembre 2026 |
| Avocats (CNBF) | la progression de la cotisation forfaitaire sur les cinq premières années (au barème 2026, <!--chiffre:illustration()-->363<!--/--> € la première, <!--chiffre:valeur(data/reference/regimes/non_salaries.yaml:regimes.code=cnbf.periodes.debut=2004.cotisation_forfaitaire_euros)-->1 510<!--/--> € à partir de la sixième) ; la contribution équivalente aux droits de plaidoirie ; les tranches de la grille complémentaire d'avant 2019 | la cotisation proportionnelle de <!--chiffre:valeur(data/reference/regimes/non_salaries.yaml:regimes.code=cnbf.periodes.debut=2004.taux_cotisation_retraite*100)-->3,00<!--/--> % ET le forfait à sa valeur de croisière, <!--chiffre:valeur(data/reference/regimes/non_salaries.yaml:regimes.code=cnbf.periodes.debut=2004.cotisation_forfaitaire_euros)-->1 510<!--/--> € ; les années d'avant 2019 restent au rendement instantané | **surestime de <!--chiffre:illustration()-->4 586<!--/--> € sur une carrière**, au barème 2026, le flux des cinq premières années, contre près de <!--chiffre:illustration()-->70 000<!--/--> € qui manquaient quand le forfait n'était pas porté du tout. Sans effet sur la pension actuelle, qui est forfaitaire |
| Non-salariés agricoles | les points gratuits de la RCO des conjoints, aides familiaux et collaborateurs — <!--chiffre:illustration()-->66<!--/--> par an pour leurs années d'avant 2011, dans la limite de <!--chiffre:illustration()-->17<!--/--> ans —, le modèle ne connaissant que le statut de chef ; le barème de points du régime de base AVANT 1990, l'article qui l'écrit ne l'ouvrant qu'à cette date ; la réforme du 28 février 2025, EN VIGUEUR depuis le 1er janvier 2026 et non calculable : deux de ses trois paramètres sont renvoyés à un décret que la base ne porte pas | le barème en points de 1990 à aujourd'hui, la retraite forfaitaire et la RCO, tous trois lus dans le code rural, avec les points gratuits des chefs d'exploitation pour leurs années d'avant 2003 ; le rendement instantané pour les années d'avant 1990 ; la formule d'avant la réforme pour les liquidations de 2026 et au-delà, seule dont les paramètres existent | **sous-estime** la pension des carrières de conjoint et d'aide familial, qui sont précisément les plus modestes du régime |
| Régimes spéciaux résiduels | des paramètres certifiés — mais plus des textes : l'Opéra, la Comédie-Française, la SEITA, les clercs de notaires, la Banque de France, le fonds spécial des ouvriers de l'État et le personnel navigant ont leurs décrets lus VERSION PAR VERSION dans la base LEGI, et passent au niveau `moyenne`. Restent au niveau `estimee` les mines — dont dix-huit millésimes sont interpolés entre deux valeurs sourcées —, les marins, le port autonome de Strasbourg et les chemins de fer secondaires | pour les quatre derniers, les textes fondateurs sans recontrôle ; le port de Strasbourg n'a rien dans LEGI que des décrets de compensation, son règlement de retraite étant un acte de l'établissement | **indéterminé** pour ces quatre-là, et c'est le seul cas où le dépôt ne sait pas dire le sens. Ces régimes portent peu d'assurés ; leur poids dans les agrégats est faible |

**Ce qui a été refermé depuis la version précédente de ce tableau.** Le régime
de base des avocats était rangé ici comme « à scinder » : il l'est, et sa
pension ne dépend plus du revenu. La complémentaire agricole y figurait sans
valeur de point : elle en a une, certifiée de 2005 à 2024, tirée du code rural.
Le régime de base des professions libérales y figurait sans barème : il a le
sien, plafonné en points comme la caisse le publie. La grille des classes de
son étage d'avant 2004 y figurait aussi : **elle n'était pas la bonne
question** — la pension d'avant 2004 ne dépend d'aucune classe, et la section sur
le régime de base des libéraux d'avant 2004, plus bas, dit pourquoi.

**Pourquoi ce qui reste ne se referme pas de la même façon.** Les limites
refermées cette année l'ont toutes été par un changement de CLÉ D'ENTRÉE — un
numéro d'article plutôt qu'un mot, un IDBANK plutôt qu'une page, un lecteur de
format écrit à la main. Ce qui subsiste ci-dessus n'est pas d'une autre
difficulté technique : ce sont des barèmes que personne ne publie sous aucune
forme, ni en série, ni en texte réglementaire, ni en PDF. Les chercher encore
supposerait de les reconstituer à partir de cas individuels, ce qui produirait
un chiffre plus précis d'apparence et pas davantage de vérité.

Le catalogue compte **<!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=modelise|partiel)-->74<!--/--> régimes**, actuels et disparus. Il est structurellement
extensible : ajouter un régime consiste à écrire une fiche YAML conforme à
`data/reference/regimes/_schema.yaml`, sans toucher au moteur.

### Les régimes qui manquent encore, et ce qui bloque chacun

**Cette liste est désormais dérivée d'un fichier.** Elle ne l'était pas, et
c'était une limite en soi : aucune source du dépôt n'énumérait les régimes
français — la série DREES agrège en treize systèmes, le panorama du COR est un
document saisi à la main, et les portails officiels ne servent pas de liste
exploitable —, si bien qu'un régime pouvait manquer à la liste des manquants.
[`data/reference/regimes/inventaire.yaml`](../data/reference/regimes/inventaire.yaml)
énumère maintenant TOUS les régimes obligatoires, vivants, disparus ou hors
champ — <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire)-->91<!--/--> lignes, ancrées sur `R. 711-1`, `D. 643-1`, `L. 921-1` et le
programme 195 des lois de finances, chacune avec son texte fondateur et, quand
l'index DILA du dépôt le porte, son identifiant —, et dit pour chacun s'il est
modélisé, partiel, à modéliser ou hors champ. `tests/test_donnees.py` impose
que l'inventaire et le catalogue coïncident sur les régimes calculés ; la page
« Données » du site l'affiche ; [`docs/regimes.md`](regimes.md) le commente,
famille par famille. Ce qui suit est l'histoire de la façon dont les fiches
sont entrées, et reste vrai ; la liste à jour de ce qui manque est là-bas.

**Ce que l'inventaire a fait apparaître**, que la liste de mémoire ne portait
pas : le régime d'allocation viagère des gérants de débits de tabac (décret
du 30 octobre 1963, géré par la Caisse des dépôts), le régime additionnel des
enseignants du privé sous contrat (décret n° 2005-1233), les deux
complémentaires d'Organic d'avant le NRIC — conjoints de commerçants
(`D. 635-35-1`) et entrepreneurs du bâtiment (loi n° 70-13) —, les régimes
RACD et RACL de l'IRCEC, les régimes professionnels intégrés à l'Agirc-Arrco
(banques, organismes de sécurité sociale, caisses d'épargne, CCI, CAMARCA),
l'affiliation des élus locaux à l'Ircantec dès 1973 (loi n° 72-1201) et non
1992, le régime micro-social, l'ASV des conventionnés, et cinq régimes
d'outre-mer. Et trois régimes fermés dont on ne savait plus s'ils avaient
existé, retrouvés dans l'index : le régime spécial du Crédit foncier de France
(transféré au régime général au 1er janvier 1989, décret n° 89-157), la caisse
des régies ferroviaires d'outre-mer (décret n° 58-1090, puis transfert à
l'État en 1993), et le régime de l'ORTF. Une relecture de septembre 2026
contre l'arrêté du 22 juillet 2003 relatif à l'échantillon interrégimes de
cotisants, qui énumère les organismes de tous les régimes obligatoires, a
ajouté quatre caisses fermées — la CREA des professions de l'enseignement
fondue dans la Cipav en 2004, la Caisse de retraites de la France d'outre-mer,
les caisses des fonctionnaires d'Algérie, du Maroc et de Tunisie, la CRFM des
agents publics de Mayotte —, les non-salariés de Mayotte à la caisse de
sécurité sociale de Mayotte et le personnel au sol d'Air France aux régimes
professionnels intégrés, puis une ligne pour les élus des assemblées de
Polynésie française et de Nouvelle-Calédonie, dont la loi organique de 1999
confie le régime de retraite aux assemblées elles-mêmes ; voir
[`docs/regimes.md`](regimes.md).

#### Ce que JORF et LEGI ne contiennent pas

Le dépôt embarque, par l'index de `scripts/fetch/dila_index.py`, deux bases de
la DILA filtrées sur le champ social. Pour l'histoire des règles de chaque
régime — l'étape qui suit l'inventaire —, il faut savoir ce qu'elles ne
donnent pas, afin de ne pas le chercher deux fois :

1. **Tout ce qui précède 1947.** Le dump JORF commence en 1947. Les lois de
   1910, de 1928 et 1930, de 1941, les ordonnances de 1945, la loi de 1909 sur
   les retraites des cheminots, celle de 1894 sur les mines et celle de 1937
   sur les clercs de notaires ne s'y trouvent que par les textes postérieurs
   qui les citent. Elles sont sur Gallica, en images.
2. **De 1947 à 1989, le texte intégral manque souvent.** Le JORF ancien n'est
   dans le dump que par sa notice ou son titre — constaté sur 1950 et sur
   1985-1986 —, et certains tableaux ne sont que des images (1994-1995). C'est
   la période où les règles des régimes se sont fixées : 1945, 1971, 1982,
   1983. Le « JO numérisé » en fac-similé de Légifrance n'est pas en open
   data.
3. **LEGI ne remonte pas avant la codification de 1985** pour les états
   datés des articles ; les versions antérieures des décrets des régimes
   spéciaux — statut des IEG de 1946, règlement SNCF de 1954 — n'y sont pas.
4. **Les accords de l'Agirc et de l'Arrco** — 1947, 1961, 2017 — et leurs
   annexes ne sont ni dans le JORF, qui n'a les avis d'extension que depuis
   les années 2000, ni dans KALI. La fédération est la seule source.
5. **Les règlements des caisses** — sections de la CNAVPL, CNBF, IRCEC, CRPN,
   port autonome de Strasbourg, Banque de France, CCI — : le JORF porte
   l'arrêté d'approbation, rarement son annexe.
6. **Les circulaires** de la Cnav et le BOSS ne sont pas dans JORF ni LEGI ;
   celles de la revalorisation des salaires sont récupérées à part.
7. **Les régimes des assemblées et des collectivités du Pacifique** relèvent
   de textes qui ne paraissent pas au Journal officiel.

Ce qu'il ne manque pas : le filtre thématique de l'index est assez large —
« retrait », « pension », « cotis », « invalidit »… — pour retenir les textes de
tous les régimes de l'inventaire ; les recherches qui ont établi la liste y
ont trouvé le décret du Crédit foncier, celui de Mayotte, l'arrêté des débits
de tabac, la loi des maires et adjoints, sans reconstruire l'index.

**Le régime des cultes, lui, est entré**, et c'est le seul du lot que le code
spécifie entièrement — sans lui donner un seul chiffre propre :

* l'**assiette** : R. 382-89 et R. 382-90 égalent la base forfaitaire, pour
  l'assuré comme pour sa congrégation, à « la valeur horaire du salaire
  minimum de croissance en vigueur, multipliée par le nombre légal d'heures de
  travail mensuel » ;
* les **taux** : les mêmes articles les égalent à ceux du régime général,
  respectivement part salarié et part employeur ;
* la **pension** : L. 382-27 la sert « dans les conditions définies aux
  articles L. 351-1 à L. 351-1-3 […] L. 351-8 à L. 351-13 », c'est-à-dire aux
  règles du régime général.

La fiche ne porte donc aucune valeur qui lui soit propre, et un test relit les
deux fiches année par année pour interdire qu'elle dérive de celle du régime
général. Il a fallu un drapeau au moteur, `assiette_forfaitaire` : un ministre
du culte n'a pas de salaire dont on prélèverait une fraction, l'assiette EST le
forfait, là où `assiette_plancher` ne relevait que les assiettes trop basses.

**Ce que la fiche des cultes approxime.** Le passage du forfait de <!--chiffre:illustration()-->169<!--/--> à <!--chiffre:mesure(constante?de=retraite_notionnelle.web.pages&nom=HEURES_SMIC_PAR_MOIS)-->151,67<!--/--> heures mensuelles est daté de 2002, ce
que la clause transitoire de R. 382-89 rend probable sans l'écrire ; et la
garantie mensuelle de rémunération qui, du 1<sup>er</sup> janvier 2002 au
30 juin 2005, s'ajoutait à cette base n'est pas modélisée — ces quatre années
sous-estiment donc la cotisation. L. 382-27 réserve les périodes antérieures
au 1<sup>er</sup> janvier 1998 aux règles d'avant — la caisse porte leur
fraction de pension au minimum contributif, ou au maximum de la pension
« Cavimac » quand le taux est minoré — : le modèle applique les règles du
régime général sur toute la durée, sur un salaire annuel moyen fait du forfait,
comme celui que la caisse calcule. Et les années d'activité cultuelle d'avant
1979, qu'elle valide gratuitement et dont elle sert une fraction de pension, ne
sont pas comptées : le modèle n'ouvre rien avant la création du régime. Cela ne
touche que le scénario 1 ; les comptes notionnels, eux, ne lisent que des
cotisations, et celles-là sont sourcées de bout en bout.

**Les autres, et le mur devant chacun** : voir la couverture « à modéliser »
de l'inventaire, qui porte pour chacun ce qui bloque.

### Un rendement unique là où il faudrait une série

La fiche CARPIMKO met en lumière une approximation qui vaut pour TOUS les
régimes convertis par `rendements_points.csv` : le moteur applique **un seul
rendement, celui de l'année de liquidation**, aux cotisations revalorisées de
toute la carrière. Or le rendement de la CARPIMKO tombe de <!--chiffre:cellule(data/reference/regimes/rendements_points.csv:rendement*100?regime=carpimko_complementaire&debut=2010)-->13,10<!--/--> % en 2010 à
<!--chiffre:cellule(data/reference/regimes/rendements_points.csv:rendement*100?regime=carpimko_complementaire&debut=2025)-->7,36<!--/--> % en 2025. Une infirmière qui liquide en 2027 voit donc ses cotisations de
2010 converties au rendement de 2025 au lieu du leur, à peine plus de la moitié :
sa complémentaire ressort très en deçà de ce que l'accumulation année par année
en donnerait — d'un tiers, quand cette section a été écrite.

Le chemin exact existe déjà dans le moteur — `valeurs_point.csv`, qui accumule
des points année par année —, et la CARPIMKO a de quoi l'emprunter : son prix
du point implicite est le forfait divisé par 8, et il donne les mêmes points que
la part proportionnelle divisée par 22. Ce qui manque n'est pas la donnée mais
le raccordement : `valeurs_point.csv` est un fichier CERTIFIÉ, dont le journal
verrouille le nombre de lignes par niveau, et y verser des valeurs demande un
contrôle dans `verifier_donnees.py` — donc un récupérateur pour la valeur de
service, que la caisse publie en PDF depuis 2010.

UN PIÈGE DÉCOUVERT EN CHEMIN, et refermé par un test. La table des tranches
d'assiette existe DEUX FOIS — `BORNES_ASSIETTE` dans `donnees/regimes.py` et
dans `moteur/js/regimes.js` —, parce que le portage ne lit pas le Python. La
tranche `tranche_1_3_pass` ajoutée pour la Cipav n'avait été écrite que d'un
côté : le JavaScript retombait sur `[0, null]`, c'est-à-dire SANS PLAFOND, et
cotisait 39 146 € là où le modèle en cotisait 19 356. Aucune erreur n'était
levée ; seule la comparaison des témoins l'a vu. Un test compare désormais les
deux tables.

### Le simulateur doit être juste à tout âge : où il ne l'est pas encore

Une fiche de régime porte des PÉRIODES, et chaque période un jeu de règles. Un
régime dont la fiche n'a qu'une période applique donc les mêmes règles à toute
son histoire — et comme les fiches sont écrites à partir des paramètres
d'aujourd'hui, c'est le droit de 2026 qu'elles appliquent à 1950. Le tableau
ci-dessous compte, pour chaque régime, le nombre d'ANNÉES par jeu de règles
distinct. Plus le nombre est grand, moins l'histoire du régime est dans le
modèle :

| Régime | Couverture | Jeux de règles | Années par jeu | Coupures de texte non reflétées | Réformes non portées |
|---|---|---|---|---|---|
| `port_strasbourg` | 1930-2026 | 1 | 97 | 0 | 0 |
| `marins` | 1930-2026 | 1 | 97 | 2 | 0 |
| `sncf` | 1930-2033 | 16 | 79 | 1 | 0 |
| `ratp` | 1930-2033 | 16 | 79 | 3 | 0 |
| `assemblees_parlementaires` | 1930-2030 | 22 | 79 | 0 | 0 |
| `banque_de_france` | 1930-2026 | 16 | 78 | 0 | 0 |
| `opera_de_paris` | 1930-2026 | 4 | 72 | 4 | 0 |
| `crpcen` | 1937-2026 | 16 | 71 | 0 | 0 |
| `fonctionnaires_pacifique` | 1959-2029 | 8 | 65 | 0 | 0 |
| `cafat_nouvelle_caledonie` | 1958-2026 | 5 | 65 | 0 | 0 |
| `comedie_francaise` | 1930-2026 | 4 | 63 | 1 | 0 |
| `cnbf` | 1948-2026 | 2 | 56 | 2 | 0 |
| `cps_polynesie` | 1968-2026 | 2 | 55 | 0 | 0 |
| `cnavpl` | 1949-2026 | 8 | 55 | 9 | 0 |
| `cavec_complementaire` | 1953-2026 | 5 | 55 | 0 | 0 |
| `ircec_racl` | 1962-2026 | 3 | 52 | 1 | 0 |
| `ircec_raap` | 1962-2026 | 6 | 52 | 1 | 0 |
| `ircec_racd` | 1964-2026 | 3 | 50 | 2 | 0 |
| `seita` | 1935-2026 | 8 | 49 | 0 | 0 |
| `cese_membres` | 1957-2026 | 14 | 48 | 0 | 0 |
| `carcdsf_complementaire` | 1949-2026 | 22 | 48 | 0 | 0 |
| `regimes_professionnels_integres` | 1947-1993 | 1 | 47 | 0 | 0 |
| `mines` | 1930-2026 | 22 | 44 | 1 | 0 |
| `cnbf_complementaire` | 1979-2026 | 2 | 40 | 0 | 0 |
| `cnracl` | 1945-2026 | 19 | 39 | 11 | 0 |
| `ieg` | 1946-2026 | 15 | 38 | 3 | 0 |
| `gerants_debits_tabac` | 1963-2026 | 2 | 37 | 10 | 0 |
| `cavom_complementaire` | 1979-2026 | 2 | 37 | 5 | 0 |
| `wallis_et_futuna` | 1975-2026 | 13 | 34 | 0 | 0 |
| `msa_non_salaries` | 1952-2026 | 7 | 34 | 13 | 0 |
| `cipav_complementaire` | 1979-2026 | 5 | 34 | 1 | 0 |
| `crpnpac_tranche_2` | 1963-2026 | 4 | 32 | 0 | 0 |
| `crpnpac` | 1963-2026 | 4 | 32 | 5 | 0 |
| `cps_polynesie_tranche_b` | 1995-2026 | 1 | 32 | 0 | 0 |
| `cavp_complementaire` | 1949-2026 | 8 | 29 | 2 | 0 |
| `chemins_fer_secondaires` | 1930-1954 | 1 | 25 | 0 | 0 |
| `organic` | 1949-2006 | 15 | 24 | 0 | 0 |
| `msa_rco` | 2003-2026 | 1 | 24 | 24 | 0 |
| `cancava` | 1949-2006 | 15 | 24 | 0 | 0 |
| `cprn_complementaire` | 1949-2026 | 10 | 22 | 2 | 0 |
| `cavamac_complementaire` | 1968-2026 | 8 | 22 | 5 | 0 |
| `ipacte` | 1951-1970 | 1 | 20 | 0 | 0 |
| `fspoeie` | 1930-2026 | 21 | 20 | 2 | 0 |
| `fonction_publique_etat` | 1948-2026 | 20 | 20 | 2 | 0 |
| `pensions_civiles_1853` | 1930-1948 | 1 | 19 | 0 | 0 |
| `ircantec` | 1971-2026 | 16 | 17 | 6 | 0 |
| `rafp` | 2005-2026 | 2 | 16 | 6 | 0 |
| `assurances_sociales` | 1930-1945 | 1 | 16 | 0 | 0 |
| `carpv_complementaire` | 1950-2026 | 10 | 15 | 0 | 0 |
| `organic_conjoints_batiment` | 1973-2003 | 4 | 13 | 0 | 0 |
| `asv_conventionnes` | 1972-2026 | 21 | 13 | 10 | 0 |
| `agirc` | 1947-2018 | 24 | 13 | 0 | 0 |
| `regime_general` | 1945-2026 | 33 | 12 | 0 | 0 |
| `rco_artisans` | 1979-2012 | 10 | 12 | 2 | 0 |
| `rci` | 2013-2026 | 2 | 12 | 2 | 0 |
| `msa_salaries` | 1945-2026 | 35 | 12 | 0 | 0 |
| `carpimko_complementaire` | 1984-2026 | 27 | 12 | 0 | 0 |
| `arrco` | 1961-2018 | 18 | 12 | 1 | 0 |
| `igrante` | 1960-1970 | 1 | 11 | 0 | 0 |
| `enseignants_prive_additionnel` | 2005-2026 | 6 | 11 | 1 | 0 |
| `cssm_mayotte` | 1987-2036 | 37 | 11 | 0 | 0 |
| `arrco_tranche_2_entreprises_nouvelles` | 1997-2018 | 6 | 11 | 0 | 0 |
| `arrco_tranche_2` | 1961-2018 | 22 | 9 | 0 | 0 |
| `nric` | 2004-2012 | 2 | 8 | 3 | 0 |
| `cavimac` | 1979-2026 | 22 | 8 | 0 | 0 |
| `carmf_complementaire` | 1949-2026 | 62 | 8 | 1 | 0 |
| `cps_saint_pierre_et_miquelon` | 1987-2037 | 37 | 7 | 0 | 0 |
| `agirc_entreprises_nouvelles` | 1981-2018 | 17 | 7 | 0 | 0 |
| `unirs` | 1957-1961 | 1 | 5 | 0 | 0 |
| `avts` | 1941-1945 | 1 | 5 | 0 | 0 |
| `agirc_arrco` | 2019-2026 | 2 | 5 | 0 | 0 |
| `rsi` | 2006-2018 | 7 | 4 | 1 | 0 |
| `rsi` | 2006-2018 | 2 | 10 | 4 | 0 |
| `arrco_tranche_2` | 1961-2018 | 22 | 9 | 0 | 0 |
| `nric` | 2004-2012 | 2 | 8 | 3 | 0 |
| `carmf_complementaire` | 1949-2026 | 62 | 8 | 1 | 0 |
| `agirc_entreprises_nouvelles` | 1981-2018 | 17 | 7 | 0 | 0 |
| `unirs` | 1957-1961 | 1 | 5 | 0 | 0 |
| `avts` | 1941-1945 | 1 | 5 | 0 | 0 |
| `agirc_arrco` | 2019-2026 | 2 | 5 | 0 | 0 |

**Ce tableau n'est plus écrit à la main** : c'est la sortie de
`python scripts/calendrier_regimes.py --carte`, relevée après les tranches B1
à B5d de la campagne « les règles à travers l'histoire » (voir
[`regimes.md`](regimes.md), journal de la campagne). Les deux dernières
colonnes viennent de l'index LEGI et du calendrier des réformes
(`legislation/reformes.yaml`) : une « coupure de texte non reflétée » est une
version d'un article pivot (`regimes/pivots.yaml`) qui commence une année où
aucune période de la fiche ne commence — un endroit où lire, pas un verdict,
car beaucoup de versions ne changent qu'un renvoi ; une « réforme non portée »
est un manque, et le test `test_toute_reforme_est_coupee_absorbee_ou_declaree`
impose qu'il n'y en ait aucune. Les deux premières lignes restent ce qui
résiste : le port autonome de Strasbourg, dont le règlement de retraite est un
acte de l'établissement et non un texte publié, et les marins, dont la formule
est stable depuis 1968 — vérifiée article par article —, et dont la grille des
salaires forfaitaires, lue au Journal officiel depuis 2008, ne demande pas de
période de plus : elle est une table annuelle, que la fiche lit à part.

Le nombre n'est pas à lui seul un verdict : un régime dont les règles n'ont pas
bougé mérite une seule période. Mais il
dit où chercher, et ce qu'on y trouve est parfois gros : le régime des salariés
agricoles portait une période pour quatre-vingt-seize ans, avec les paramètres de
2023 — un salarié agricole parti en 1980 se voyait opposer 172 trimestres au lieu
de 150 et calculer sur ses vingt-cinq meilleures années au lieu de dix.

**Les témoins ne le voyaient pas, et c'est le second enseignement.** Le balayage
par statut ne connaissait qu'une génération, née en 1975 : il ne visitait que les
périodes RÉCENTES de chaque fiche. Corriger le régime agricole n'a déplacé aucun
témoin. Chaque statut est donc désormais simulé à QUATRE générations — née en
1925, qui liquide vers 1990 ; née en 1935, qui liquide vers 1999, sous la durée
requise de 150 ou 160 trimestres et les dix meilleures années ; née en 1955, qui
liquide vers 2019 ; née en 1975, qui liquide après la réforme de 2023. Le fichier
de témoins passe de 138 à 250 cas, et une correction d'histoire s'y voit
maintenant. La génération 1925 est la dernière venue, et pour une raison
précise : les tables par génération ne répondent pas toutes en deçà de 1934, et
le défaut que cela cachait est raconté plus bas.

Ce qui a été refermé de cette façon jusqu'ici : le régime des salariés agricoles
(aligné sur le régime général, ses huit périodes reprises une à une), les régimes
alignés des artisans et des commerçants depuis 1973, le fonds spécial des
ouvriers de l'État (aligné sur le code des pensions, six périodes), la Banque de
France (alignée depuis 2007, quatre périodes) et la caisse des clercs de notaire
(trois périodes au lieu d'une depuis 2009, et le barème de décote de la fonction
publique que son décret lui donne) ; la durée requise de l'Opéra et de la
Comédie-Française ; les bornes d'âge de la RATP et des IEG, qui étaient celles de
2017 dès 2009 ; et la clause du grand-père des régimes fermés.

**Trois manières de se tromper, et elles reviennent.** La première est la fiche
d'un régime ALIGNÉ qui ne suit pas l'histoire de son modèle : on la corrige en
recopiant les périodes du régime général ou du code des pensions, ce qui est sûr
parce que l'alignement est une règle de droit. La deuxième est la période
OUVERTE — `fin: null` — qui porte les paramètres du jour : elle applique le droit
d'aujourd'hui à toute la période qu'elle couvre, et c'est ainsi qu'un agent de la
Banque de France parti en 2009 se voyait opposer l'âge de 2023. La troisième est
la réforme qui ne touche pas tout en même temps : celle de 2008 ne relève les
bornes d'âge des régimes spéciaux qu'à partir de 2017, et sa décote n'existe pas
avant le 1er juillet 2010 — elle monte ensuite en charge jusqu'en 2024, quand les
fiches la servaient pleine dès 2009.

### Ce que vaut une série qu'on ne peut pas certifier

Deux séries de taux ne se certifieront pas, et il fallait dire mieux que « pas
certifiées ». Le régime général d'avant 1982, que la base LEGI ne date pas ; et
les complémentaires du privé, dont les taux ne sont dans aucun texte
réglementaire. Les deux venaient d'OpenFisca-France.

**OpenFisca n'est pas la source.** Il transcrit les barèmes de l'Institut des
politiques publiques, qui sont l'amont — la page qui précède l'écrivait déjà,
pour dire que l'IPP « ne commence pas plus tôt que lui ». C'était vrai, et à
côté de la question : ce que l'IPP a et qu'OpenFisca perd en route, ce sont deux
colonnes. `reference` nomme le texte de chaque marche ; `official_journal_date`
donne sa publication. `scripts/fetch/ipp_taux_cotisation.py` les lit, et
`verifier_donnees.py` en tire trois constats à chaque exécution.

**Un : la confrontation vérifie une copie, pas une lecture.** Les soixante
années du régime général sont confrontées à l'IPP, et un écart y est une erreur
de recopie d'OpenFisca — non un désaccord entre deux témoins. Le contrôle le dit
dans ses propres mots, pour que personne ne prenne son « OK » pour une seconde
source. Il en a déjà trouvé une : OpenFisca servait 0,1 % de part salariale
déplafonnée **dès le 1er janvier 2004** quand elle naît le 1er juillet. La cause
était la même que celle du filtre de l'année, et au même endroit : l'exception
« année d'ouverture » s'appliquait à chaque composante au lieu de la seule année
où la série commence.

**Deux : la chronologie, elle, se vérifie.** Pour chaque marche, le récupérateur
cherche dans l'index JORF le texte que l'IPP nomme, au numéro et à la date
annoncés. **Trente-cinq des trente-six marches de la CNAV y sont** ; la seule qui
manque est le décret n° 70-680 du 30 juillet 1970, absent de l'index. Une valeur
transcrite reste une valeur transcrite, mais la DATE de chaque marche est
désormais vérifiée contre le *Journal officiel* — et c'est la date dont dépend
la règle du 1er janvier, celle qui déplaçait six années à elle seule.

**Trois : les complémentaires ne se certifieront pas, et c'est l'IPP qui le
dit.** Pour l'Agirc, l'Arrco et le régime unifié, il laisse lui-même la colonne
du *Journal officiel* VIDE sur ses vingt-cinq marches, et cite « Convention
AGIRC du 14 mars 1947 », « Accords ARRCO du 12 novembre 1986 »,
« Lettre-circulaire ARRCO 82-28 ». Ces taux sont fixés par accord collectif ; le
*Journal officiel* n'en publie que l'**avis d'extension**, qui renvoie au
Bulletin officiel Conventions collectives sans jamais écrire le chiffre — on
peut le lire dans la base, avis par avis, de 2006 à 2015. La fédération
Agirc-Arrco publie la compilation de ses valeurs de point, que le dépôt lit déjà,
mais aucun historique de taux : sa page « Paramètres » n'affiche que l'année
courante, et ses circulaires ne remontent qu'à 2003. La démonstration est
mécanique, et c'est ce qui la rend utile : si l'IPP se met un jour à remplir
cette colonne, le contrôle le dira.

**Et il a trouvé ce que personne ne cherchait.** Sur 1967-1981, le récupérateur
demande au JORF les décrets qui annoncent dans leur titre des taux de cotisation
du régime général, et compte ceux qu'aucune marche ne rejoint. Il en reste **un**,
et il est lourd : le **décret n° 79-650 du 30 juillet 1979** a relevé « à titre
exceptionnel, par dérogation aux dispositions du décret n° 78-1213 » les taux du
régime général « du 01-08 au 31-12-1979 et du 01-01-1980 au 31-01-1981 ». La
fenêtre couvre **deux premiers janvier**, 1980 et 1981. Ni l'IPP ni OpenFisca ne
la portent, et le dépôt en a conclu que les taux servis pour ces deux années
étaient **trop bas**, d'un montant que la notice n'écrit pas — elle ne nomme
même aucun risque, et le décret lui-même a disparu de LEGI avec sa date
d'expiration.

### La réforme agricole de 2026 n'est pas modélisée, et il faut le dire

L'article 87 de la loi n° 2025-199 du 28 février 2025 de financement de la
sécurité sociale réécrit `L. 732-24` : pour les pensions prenant effet à compter
du **1er janvier 2026**, la retraite de base des non-salariés agricoles n'est
plus la somme d'un forfait et de points de carrière entière, mais un calcul sur
les **vingt-cinq meilleures années** — de revenus à partir de 2016, de points
avant, les revenus n'étant pas connus plus tôt. Un dispositif transitoire
recalcule en 2028 les pensions liquidées en 2026 et 2027, au bénéfice de
l'assuré.

Le modèle sert encore la formule d'avant. C'est une limite DATÉE, et la seule de
ce document qui se périme d'elle-même : elle porte sur les liquidations
postérieures à 2025, c'est-à-dire sur la moitié des simulations que le site
propose. La modéliser demande une mécanique que le régime agricole n'a jamais
eue — un salaire annuel moyen sur vingt-cinq années, greffé sur un compte en
points — et c'est pourquoi elle n'est pas faite ici plutôt que faite à moitié.

### La part patronale du public, et ce qu'on n'en sait pas

Les scénarios 4 et 5 ajoutent à la part salariale ce que verse l'employeur. Pour
un salarié du privé, la fiche du régime le porte — `part_salariale` en donne la
répartition, recoupée à OpenFisca année par année. Pour un agent public, elle
n'est dans aucune fiche : le modèle la lit dans
`legislation/contribution_employeur_public.csv`, qui couvre aujourd'hui huit
régimes, mais aucun sur toute sa durée. Partout ailleurs, la part patronale est
**estimée** par l'effort d'un salarié du privé de la même année — jamais laissée
à zéro, qui ferait retomber les scénarios 4 et 5 sur les 2 et 3 sans le dire —
la fiabilité de l'année retombe à `estimee`, et le nombre d'années concernées
est affiché sous la simulation.

| Régime | Couvert | Découvert | Ce qui manque |
|---|---|---|---|
| Fonction publique d'État | 1995-2026 | 1930-1994 | rien à retrouver : l'État ne versait aucune cotisation, les pensions étaient payées sur crédits budgétaires, et le plus ancien chiffrage a posteriori — le jaune « pensions » — s'arrête à 1995 ; ses militaires ont leur taux propre, appelé depuis 2006, dans `contribution_employeur_militaires.csv` |
| CNRACL | 1948-2028 | 1945-1947 | le décret fondateur date du 19 septembre 1947 ; la convention « taux au 1er janvier » fait donc commencer la série en 1948 |
| SNCF | 1992-2018 | 1930-1991, 2019- | avant 1992, aucun texte de la base LEGI ne porte le taux ; après 2018, le décret cesse de chiffrer la composante T2, qui évolue par formule |
| RATP | 2007-2025 | 1930-2006, 2026- | rien à retrouver : avant l'adossement de 2006, la RATP payait les pensions sans qu'aucun texte fixe un taux, exactement comme l'État avant son compte d'affectation spéciale ; après 2025, la série n'a pas encore sa ligne, et le dernier taux est reconduit au niveau `estimee` |
| IEG | 2005-2020 | 1946-2004, 2021- | avant 2005, EDF et GDF payaient les pensions directement ; après 2020, l'arrêté du 29 décembre 2021 remplace la fixation annuelle par une formule que la caisse applique sans la publier |
| Mines | 1984-2026 | 1930-1983 | la base LEGI ne garde aucune version de l'article 52 du décret de 1946 avant le 1er janvier 1984 |
| Opéra de Paris, Comédie-Française | 1992-2026 | 1930-1991 | même mur : les versions datées du décret qui fixe ces taux commencent au 1er juillet 1991 |
| FSPOEIE, marins, CRPCEN, Banque de France, port de Strasbourg, SEITA, chemins de fer secondaires | rien | tout | aucune série de taux employeur trouvée sous une forme exploitable. Pour ces sept régimes, la part patronale des scénarios 4 et 5 est celle d'un salarié du privé de la même année, et le modèle le dit |

**Ces taux sont ceux de l'employeur, non ceux de l'équilibre**, et c'est une
convention qui se défend mais qui se paie. Trois de ces régimes reçoivent aussi
de l'État une contribution que la série ne porte pas, parce qu'elle n'est pas
une cotisation d'employeur : les droits spécifiques de la RATP jusqu'à 45 000
agents, « une cotisation correspondant à <!--chiffre:illustration()-->22<!--/--> % des salaires » plus un complément
d'équilibre pour les mines — près de trois fois ce que verse l'exploitant —, la
subvention de l'Opéra. Pour la SNCF d'après 2007, la somme T1 + T2 laisse de
même dehors la subvention d'équilibre. La ligne de l'État est la seule exception
du tableau : son taux EST un taux d'équilibre. Un agent minier et un
fonctionnaire d'État ne sont donc pas mesurés à la même aune, et la différence
joue contre le mineur.

**Et ce taux d'équilibre paie plus que la retraite de l'agent.** La Cour des
comptes le décompose dans sa communication du 22 septembre 2026 sur les
retraites des fonctionnaires de l'État (tableau n° 15, recopié ligne à ligne
dans `legislation/contribution_etat_retraite_seule.csv`) : des <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2025&regime=fonction_publique_etat)-->78,28<!--/--> % appelés
en 2025 pour un civil, elle ne garde que <!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*100?population=civils&poste=retraite_stricto_sensu)-->44,1<!--/--> % pour la retraite au sens
strict ; le reste finance l'invalidité avant soixante-deux ans, les majorations
pour enfants, les départs anticipés des emplois classés et, pour <!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*-100?population=civils&poste=desequilibre_demographique)-->35,3<!--/-->
points, le déséquilibre démographique du régime. Pour un militaire, dont
l'employeur paie <!--chiffre:cellule(data/reference/legislation/contribution_employeur_militaires.csv:taux*100?annee=2025)-->126,07<!--/--> %, elle garde <!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*100?population=militaires&poste=retraite_stricto_sensu)-->51,2<!--/--> %. Créditer au compte le taux entier,
comme le scénario 4, et le 6 jusqu'à la bascule, le faisaient jusqu'au
24 septembre 2026, c'était porter au compte d'un fonctionnaire d'État ce que
son employeur verse pour d'autres. Le militaire, lui, recevait jusqu'au même
jour le taux des civils, moins que ce que le sien verse : son taux propre, lu
dans les décrets qui le fixent, est dans
`legislation/contribution_employeur_militaires.csv` — <!--chiffre:cellule(data/reference/legislation/contribution_employeur_militaires.csv:taux*100?annee=2006)-->100<!--/--> % en 2006,
<!--chiffre:cellule(data/reference/legislation/contribution_employeur_militaires.csv:taux*100?annee=2013)-->126,07<!--/--> % depuis 2013.

**Le compte ne reçoit donc, par défaut, que la part de la Cour**
(`contribution_etat=retraite_seule`) : ce qui n'est pas contributif se finance
par l'impôt, non par le compte. Dans les options du site, « Contribution de
l'État portée au compte » rétablit le taux entier. L'année que la Cour a
mesurée, le compte reçoit ses deux taux ; les autres années, la même
proportion du taux versé à sa population — <!--chiffre:mesure(retraite_seule)-->56,3<!--/--> % pour un civil,
<!--chiffre:mesure(retraite_seule?militaire=1)-->40,6<!--/--> % pour un militaire, soit <!--chiffre:mesure(retraite_seule?militaire=1&annee=2020)-->51,2<!--/--> % chaque année depuis 2013, son taux
n'ayant pas bougé —, et c'est une hypothèse, que le résultat qualifie
d'`estimee`. Pourquoi une proportion
plutôt qu'un taux fixe : le rapport n'éclaire qu'une autre année, 2020, où le
taux était de <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2020&regime=fonction_publique_etat)-->74,28<!--/--> % ; la proportion y donne <!--chiffre:mesure(retraite_seule?annee=2020)-->41,8<!--/--> %, un taux fixe <!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*100?population=civils&poste=retraite_stricto_sensu)-->44,1<!--/-->, et
la Cour — qui impute cinq points de l'écart avec l'Institut des politiques
publiques à la seule différence d'année (annexe n° 6) — environ <!--chiffre:illustration()-->39<!--/-->.
Ce que ce choix déplace est considérable. Sous le taux entier, la fonctionnaire
de l'exemple du README, née en 1975, aurait <!--chiffre:mesure(ecart?exemple=fonctionnaire&scenario=4&contribution_etat=entiere)-->+45,0<!--/--> % d'écart au système
actuel dans le scénario 4 ; sous la part de la Cour, <!--chiffre:mesure(ecart?exemple=fonctionnaire&scenario=4)-->−1,3<!--/--> %. Dans la
proposition, <!--chiffre:mesure(ecart?exemple=fonctionnaire&scenario=6&contribution_etat=entiere)-->+44,9<!--/--> % deviennent <!--chiffre:mesure(ecart?exemple=fonctionnaire&scenario=6)-->−3,4<!--/--> %, et le solde moyen de la proposition
passe de <!--chiffre:mesure(solde_moyen?scenario=6&contribution_etat=entiere)-->−0,91<!--/--> % à <!--chiffre:mesure(solde_moyen?scenario=6)-->−0,49<!--/--> % du PIB, de <!--chiffre:mesure(solde_moyen?scenario=6&en=milliards&contribution_etat=entiere)-->−27<!--/--> à <!--chiffre:mesure(solde_moyen?scenario=6&en=milliards)-->−15<!--/--> milliards
d'euros par an, parce que les droits qu'elle reprend à la bascule étaient
gonflés de ce qui payait d'autres pensions. Le privé, la CNRACL, le scénario 1
et la part salariale ne bougent pas, ni les années d'avant 1995, où le compte
reçoit déjà l'effort d'un salarié du privé. Un point reste ouvert, que
l'action 129 de la feuille de route détaille : une série mesurée année par
année, plutôt qu'une proportion prêtée à trente ans de taux.

**Ce que les documents budgétaires ajoutent, et ce qu'ils n'ajoutent pas.** Les
projets annuels de performances annexés au PLF 2026 — programmes 195, 197 et
198 —, lus le 20 septembre 2026 et saisis dans
`regimes/pap_regimes_subventionnes.csv`, donnent ce taux d'équilibre que la
série laisse dehors : la subvention rapportée aux pensions servies vaut 0,60 à
0,64 à la SNCF et 0,58 à 0,62 à la RATP, chaque année de 2012 à 2023 ; pour les
marins, la subvention inscrite pour 2026 couvre les trois quarts de la dépense
de pensions prévue. Ils ne donnent en revanche aucun TAUX employeur : les
cotisations reçues de la RATP y sont en millions d'euros, salariés et
employeur confondus, et l'ENIM n'y a que sa subvention. Le tableau ci-dessus
ne bouge donc pas — il compte des séries de taux —, et la ligne « rien /
tout » des sept régimes non plus. Depuis le 1er janvier 2025, ces crédits ne
vont d'ailleurs plus aux régimes : la CNAV les équilibre en dernier ressort et
l'État la compense, net de la compensation démographique et des cotisations
que la fermeture a portées au régime général et à l'Agirc-Arrco, si bien que
les crédits 2026 ne se comparent pas à la subvention d'avant.

Trois conséquences à garder en tête.

**Plus une carrière publique est ancienne, moins le scénario 4 s'écarte du
scénario 2** — non parce que le financement d'alors ressemblait à celui du
privé, mais parce qu'on ne le connaît pas.

**Le repli n'est pas neutre, et il ne l'était pas dans le sens qu'on croyait.**
Là où la série manquait, le modèle prêtait au régime l'effort d'un salarié du
privé — de l'ordre de <!--chiffre:mesure(fiche?exemple=salaire_moyen&quoi=total)-->27,98<!--/--> % en 2026. Les taux lus sont tantôt plus élevés (la
RATP, <!--chiffre:valeur(data/reference/regimes/regimes_speciaux.yaml:regimes.code=ratp.periodes.debut=2025.taux_cotisation_retraite*100)-->12,29<!--/--> % de retenue et <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2025&regime=ratp)-->19,13<!--/--> % d'employeur en 2025), tantôt bien
plus bas (les mines et leurs <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2026&regime=mines)-->7,75<!--/--> %, l'Opéra et ses <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2026&regime=opera_de_paris)-->9,56<!--/--> %). Le repli
surestimait donc la part patronale des régimes à faible cotisation d'employeur
et la sous-estimait pour les régimes adossés : ce n'était ni un plancher ni un
plafond, mais un brouillage.

**Le scénario 5 ne voit presque jamais la contribution publique.** Il n'ouvre
son compte qu'à la bascule, et à compter de la bascule le régime unique remplace
tous les régimes : la part patronale y est celle du statut pivot privé, pas
celle d'un employeur public. Ce que le scénario 5 mesure après 2026 est donc la
répartition du régime unique, non le financement de la fonction publique — qui,
par construction, n'existe plus.

### Le scénario 6, et ce que sa garantie ne voit pas

Le scénario 6 — le scénario 4 jusqu'à la bascule, puis un taux unique de <!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> %
pour tous, plus une garantie vieillesse individualisée, financée par l'impôt —
hérite des limites du scénario 4, part patronale inconnue du public comprise :
ce qui a été cotisé avant la bascule y est porté aux mêmes taux, et estimé là
où le 4 l'estime. Il en ajoute d'autres, que les paragraphes suivants
prennent une à une.

**La garantie est ouverte à <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=MinimumVieillesse.AGE_OUVERTURE)-->65<!--/--> ans, et le modèle sert désormais ce qu'elle
doit à qui est parti plus tôt.** *Corrigé le 19 septembre 2026.* Avant <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=MinimumVieillesse.AGE_OUVERTURE)-->65<!--/--> ans
on ne touche pas le minimum vieillesse ; à partir de <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=MinimumVieillesse.AGE_OUVERTURE)-->65<!--/--> ans on le touche, même
si l'on a liquidé à <!--chiffre:illustration()-->62<!--/-->. Le complément est donc CALCULÉ dans tous les cas, et il
n'entre dans la pension affichée que lorsqu'il est dû dès le départ ; la page
de simulation dit l'année où il s'ouvre, et le montant qu'il vaudra.

**La garantie regarde l'ENSEMBLE de la pension obligatoire.** *Tranché le
19 septembre 2026 par le programme.* Les <!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> % de répartition et les <!--chiffre:mesure(parametre?nom=taux_capitalisation_obligatoire)-->5<!--/--> %
capitalisés sont comparés ensemble au plancher : une allocation différentielle
compte les ressources, non leur origine. La rente du pilier réduit donc le
complément euro pour euro, et c'est ce qui coûte le moins à l'impôt. Le modèle
laissait jusque-là cette rente hors du calcul, faute que la question — de
droit, pas de modèle — ait été tranchée.

**La garantie ne sert que les retraités qui résident en France.** *Corrigé
le 23 septembre 2026.* Elle remplace l'ASPA, qui exige une résidence stable et
régulière en France (article L. 815-1), et en garde la condition. L'enquête
sur laquelle son coût se chiffre compte aussi les retraités partis à
l'étranger — <!--chiffre:cellule(data/reference/macro/pensions_residence.csv:valeur?annee=2020&residence=etranger&indicateur=effectifs&sexe=ensemble)-->905<!--/--> milliers en 2020, dont la pension française moyenne est de
<!--chiffre:cellule(data/reference/macro/pensions_residence.csv:valeur?annee=2020&residence=etranger&indicateur=pension_droit_direct&sexe=ensemble)-->437<!--/--> € brut par mois, parce que leur carrière française a été courte : presque
tous sont sous le plancher. Le dépôt les servait, et le coût de la garantie
s'en trouvait gonflé d'un cinquième environ. Il les retire de la distribution
par la seule information que l'enquête publie sur eux — leur effectif et leurs
quantiles —, et vérifie que les déciles des résidents en France qui en
sortent sont ceux qu'elle publie. Ce qui reste d'approché : entre deux
quantiles, leur répartition est supposée uniforme.

**Les montants sont des euros de 2026, déflatés par les prix.** <!--chiffre:mesure(parametre?nom=garantie_vieillesse_mensuelle)-->800<!--/--> € et <!--chiffre:mesure(parametre?nom=allocation_isolement_mensuelle)-->250<!--/--> €
sont ceux de la proposition ; une liquidation de 1995 les reçoit ramenés par
l'indice des prix, comme l'ASPA entre deux ancres de son barème. Ce n'est
qu'une convention : rien ne dit qu'une garantie créée en 2026 aurait été
indexée sur les prix depuis 1941.

**Ce que la garantie coûte aujourd'hui, dans la trajectoire.** Le barème est
appliqué, année par année, à la distribution des pensions de l'échantillon
interrégimes de 2020, déplacée du facteur que la grille donne : la pension
moyenne que la garantie regarde, rapportée à celle du système actuel en 2020.
Ce facteur vaut <!--chiffre:mesure(garantie?annee=2020&quoi=facteur)-->0,61<!--/--> en 2020 et <!--chiffre:mesure(garantie?annee=2070&quoi=facteur)-->1,12<!--/--> en 2070. La garantie coûte
<!--chiffre:mesure(part_pib?scenario=garantie&annee=2026)-->0,47<!--/--> % du PIB en 2026 — <!--chiffre:mesure(cout_annee?scenario=garantie&annee=2026)-->14<!--/--> milliards d'euros de 2026, <!--chiffre:mesure(garantie?annee=2026&quoi=beneficiaires)-->2,8<!--/--> millions de
bénéficiaires — et <!--chiffre:mesure(part_pib?scenario=garantie&annee=2070)-->0,30<!--/--> % en 2070 — <!--chiffre:mesure(cout_annee?scenario=garantie&annee=2070)-->12<!--/--> milliards, <!--chiffre:mesure(garantie?annee=2070&quoi=beneficiaires)-->2,3<!--/--> millions —, soit
<!--chiffre:mesure(cumul_avenir?scenario=garantie)-->575<!--/--> milliards constants cumulés sur la projection ; le passé, où le même
déplacement est appliqué à rebours, en porte <!--chiffre:mesure(cumul_passe?scenario=garantie)-->1 437<!--/--> depuis 1959. Ces chiffres
sont bruts des reprises sur succession ; la sous-section qui suit dit comment
chacun a été établi.

Ce que cette méthode suppose, et qui reste une limite : la FORME de la
distribution est celle de 2020, déplacée sans être déformée, le passé comme
l'avenir ; le déplacement est proportionnel et uniforme, quand le scénario ne
déplace pas toutes les carrières du même rapport ; et les retraités de moins
de <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=MinimumVieillesse.AGE_OUVERTURE)-->65<!--/--> ans, qui attendent la garantie, sont supposés répartis comme les autres.
Une seule méthode sur toute la série, plutôt qu'une falaise entre deux.

**Ce que la garantie n'est plus : une dépense du compte des cotisants.** Elle
est financée par l'impôt, et elle a donc quitté la masse contributive du
scénario 6, où elle était comptée jusqu'ici. C'est la symétrie de ce que la
recette fait déjà — la CSG de solidarité sort des ressources —, et sans elle la
garantie aurait été payée deux fois : une fois par les cotisations, une fois
par le contribuable.

### L'âge légal de la proposition : ce que le report suppose

La proposition fixe l'âge légal de départ à <!--chiffre:mesure(parametre?nom=age_legal_liberal)-->65<!--/--> ans à compter de la
bascule (`Parametres.age_legal_liberal`). Qui serait parti plus tôt sous le
droit en vigueur liquide la pension du scénario 6 à cet âge ; qui partait à
cet âge ou après, et qui a liquidé avant la bascule, n'est pas touché. Le
modèle le calcule en PROLONGEANT la carrière jusqu'à l'âge légal
(`Carriere.prolongee`), et le report suppose cinq choses.

**La dernière année se prolonge.** Même statut, même nature de période, même
salaire relatif, avancé au rythme du salaire moyen. C'est une convention, et
elle est la même pour toutes les carrières, qu'elles viennent d'un profil,
d'un parcours ou d'un relevé : un relevé n'a pas de profil à prolonger. Elle
fait travailler l'agent de conduite, l'agent des IEG ou le militaire dans
leur statut jusqu'à l'âge légal, là où beaucoup en changeraient ; mais à
compter de la bascule tout le monde cotise au même taux unique sur le même
revenu, et c'est le revenu seul qui compte. C'est TOUTE la dernière année qui
se prolonge : l'activité principale et chaque activité cumulée qui court
encore au départ, chacune à son revenu — jusqu'au 23 septembre 2026, seule la
dernière ligne de l'année le faisait, et le salarié qui exerçait aussi en
libéral perdait son salaire pendant les années du report. Qui finissait sa
carrière au chômage la finit au chômage, et une carrière qui s'arrêtait avant
son départ — un relevé dont les dernières années sont vides — ne gagne aucune
année travaillée.

**Le report est immédiat.** Toute liquidation qui prendrait effet à compter du
1<sup>er</sup> janvier de la bascule est portée à l'âge légal, sans montée en
charge par génération comme en ont eu les réformes de 2010 et de 2023. La
proposition n'en prévoit pas ; une montée en charge adoucirait les premières
années, au prix du solde.

**Tous ceux que le report fait attendre sont en emploi — par défaut.** C'est
ce qui fait de la recette un PLAFOND. Sur la page Coût, la recette de la
proposition est son taux appliqué à l'assiette que le COR projette aux âges
d'aujourd'hui ; le report l'élargit du rapport des revenus d'activité de la
grille sous les deux âges (`SoldeAnnuel.facteur_assiette`). Or tous les
seniors ne sont pas en emploi : qui arrive à l'âge légal au chômage ou en
invalidité ne cotise pas davantage, et ce que l'assurance chômage ou
l'invalidité lui verseraient pendant l'attente n'est compté nulle part.
Depuis le 24 septembre 2026, un paramètre le dit :
`Parametres.part_reportes_en_emploi`, <!--chiffre:mesure(parametre?nom=part_reportes_en_emploi)-->100<!--/--> % par défaut. En deçà,
chaque cohorte reportée de la grille mêle ceux qui travaillent et cotisent
jusqu'à l'âge légal et ceux qui l'attendent sans activité, sans cotiser ni
acquérir de droits, et liquident au même âge : ses recettes comme ses pensions
sont celles de ce mélange (`VoletLiberal.melange`). Il ne joue que sur la page
Coût ; le simulateur prolonge la situation de chacun.

C'est de cette part que dépend l'essentiel de ce que l'âge légal fait au
solde. Le solde moyen de la proposition est de <!--chiffre:mesure(solde_moyen?scenario=6)-->−0,49<!--/--> point de PIB quand
tous les reportés travaillent, de <!--chiffre:mesure(solde_moyen?scenario=6&emploi_reportes=0.5)-->−0,66<!--/--> quand la moitié le font, de
<!--chiffre:mesure(solde_moyen?scenario=6&emploi_reportes=0)-->−0,83<!--/--> quand aucun, contre <!--chiffre:mesure(solde_moyen?scenario=6&age_legal=aucun)-->−1,00<!--/--> sans âge légal et <!--chiffre:mesure(solde_moyen?scenario=1)-->−1,13<!--/--> pour le système
actuel : sans emploi, le report n'épargne guère que des années de pension, et
sert ensuite des pensions plus fortes. Aucun impôt ne couvre ce qui reste —
la TVA à taux unique qui le faisait du 23 au 24 septembre 2026 est retirée —,
et le déficit s'accumule : la dette de la proposition en 2070 est de <!--chiffre:mesure(dette?scenario=6)-->33<!--/--> % du
PIB quand tous les reportés travaillent, de <!--chiffre:mesure(dette?scenario=6&emploi_reportes=0.5)-->45<!--/--> % quand la moitié le font,
de <!--chiffre:mesure(dette?scenario=6&emploi_reportes=0)-->56<!--/--> % quand aucun, contre <!--chiffre:mesure(dette?scenario=1)-->66<!--/--> % pour le système actuel et <!--chiffre:mesure(dette?scenario=6&age_legal=aucun)-->70<!--/--> % pour
la proposition sans âge légal. L'ampleur de son avantage sur le système actuel
tient donc à ce que les reportés travaillent ; qu'elle en ait un n'en dépend
plus, depuis que le compte d'un fonctionnaire d'État ne reçoit que la part
« retraite » du taux de l'État — sous le taux entier, la dette atteindrait
<!--chiffre:mesure(dette?scenario=6&emploi_reportes=0&contribution_etat=entiere)-->84<!--/--> % si aucun ne travaillait. La part reste à lire dans
les évaluations de la réforme de 2010, qui a reculé l'âge légal de deux ans :
elles ont suivi ce que sont devenus ceux qu'elle a fait attendre.

**Le PIB ne bouge pas.** Plus d'emploi ferait plus de production, et le modèle
garde le PIB que le COR projette aux âges d'aujourd'hui. Toutes les parts de
PIB de la proposition sont donc rapportées à un dénominateur un peu trop bas.

**La dépense et la recette se lisent en une marche.** La cascade de la page
Coût porte le taux unique et l'âge légal dans une seule marche, parce que le
modèle ne calcule pas la proposition sans l'un des deux ; elle le dit dans son
étiquette. Mesurer l'âge seul se fait en comparant le réglage par défaut à
`age_legal_liberal=None`.

Ce que le report n'est pas : une baisse de la pension mensuelle. Dans un compte
notionnel, partir plus tard ajoute des cotisations et raccourcit la retraite,
et les deux relèvent la pension ; ce qui se perd, ce sont les années de
pension d'avant l'âge légal. Et il ne relève rien pour qui partait déjà à cet
âge ou après, le compte n'ayant ni décote ni surcote à déplacer. La garantie
vieillesse, ouverte au même âge, est désormais due dès le départ à toute
liquidation que la proposition régit ; elle ne reste différée que pour les
départs antérieurs à la bascule, que le scénario 6 recalcule rétroactivement.

Les scénarios 2 à 5 gardent les âges du droit en vigueur : ils mesurent ce que
change le compte, à carrière égale, et un âge différent y mêlerait deux effets.
L'âge de référence des scénarios prospectifs suit l'âge légal
(`age_reference_fixe`, <!--chiffre:mesure(parametre?nom=age_reference_fixe)-->65<!--/--> ans) ; il
ne pèse que sur la conversion des droits acquis.

### La réforme agricole de 2026 est en vigueur, et elle n'est pas calculable

Le tableau des manques disait « la réforme du 28 février 2025 n'est pas
modélisée ». La lecture du code rural dans la base LEGI dit quelque chose de plus
précis, et de plus gênant.

**La loi est bien en vigueur.** L'article L. 732-24 a été entièrement réécrit au
1<sup>er</sup> janvier 2026 par la loi n° 2025-199 du 28 février 2025, et
l'article L. 732-24-1 — celui qui fixait l'objectif à la Nation depuis 2023 — a
été abrogé le même jour, son objet étant atteint. La pension « cumule » désormais
une part calculée sur les seuls revenus postérieurs à 2016 et une part reprenant
les droits d'avant 2016.

**Mais deux de ses trois paramètres n'existent pas.** Le texte les renvoie
ailleurs, mot pour mot : la part forfaitaire d'avant 2016 est « d'une part dont
le montant maximal attribué pour une durée minimale d'assurance **est prévu par
décret** » ; la part proportionnelle d'avant 2016 se calcule « en retenant un
nombre d'années sélectionnées **dans des conditions fixées par voie
réglementaire** » ; et son IV ajoute « les modalités d'application du présent
article sont définies par **décret en Conseil d'État** ».

Ce décret n'est pas dans la base. Un dépouillement de toute la législation
consolidée ne rend, pour le 1<sup>er</sup> janvier 2026, que des articles
LÉGISLATIFS — L. 732-21, L. 732-24, L. 732-35, L. 732-60 du code rural, et trois
articles du code de la sécurité sociale — et aucun article réglementaire nouveau.
Les articles R. 732-60, R. 732-63 et R. 732-66, qui décrivent le calcul en
points, courent toujours jusqu'à 2999.

**Ce que le modèle fait, et pourquoi c'est le moins faux.** Il sert la formule
d'avant — retraite forfaitaire plus retraite proportionnelle en points —, qui est
la seule dont les paramètres soient publiés, et dont la partie réglementaire est
toujours en vigueur. Inventer les deux paramètres manquants reviendrait à écrire
le décret à la place du Conseil d'État. C'est écrit dans les trois périodes
concernées de la fiche, et c'est la seule limite du dépôt qui tienne à un texte
que le Gouvernement n'a pas encore pris.

## 5. Ce que le modèle ne calcule pas, et pourquoi

Ce qui suit n'est pas une liste de manques mais un **périmètre**, et chaque
ligne dit ce qu'elle coûte et dans quel sens. Une limite qu'on sait mesurer
n'est plus une limite : c'est un paramètre connu du résultat.

- **La grille de cas types ne sait pas compter le coût d'un avantage non
  contributif, et le sens de l'erreur est connu : elle n'a pas d'enfants.** Un
  seul des treize cas types en a — `carriere_interrompue`, deux enfants —, si
  bien que la majoration de pension pour trois enfants et plus valait **zéro
  toutes les années de la série**. La surcote parentale, elle, la grille la
  sert à la carrière interrompue à partir de la génération 1970, mais elle ne
  paie que des pensions prenant effet à compter de 2026 : rien à mesurer sur
  les années publiées. La grille est faite pour comparer des systèmes sur une même
  carrière, où les erreurs de niveau s'annulent au dénominateur ; le coût d'un
  avantage est un compte de POPULATION. C'est l'erreur déjà rencontrée sur la
  garantie vieillesse, que les cas types surestimaient de loin et que le barème
  appliqué à la distribution DREES chiffre juste.

  **La limite tient toujours, mais elle ne mord plus sur le chiffre publié**,
  parce que le chiffre publié n'est plus calculé. Les avantages non contributifs
  valent <!--chiffre:mesure(avantages?annee=2024)-->96,6<!--/--> milliards en 2024, soit <!--chiffre:mesure(avantages?annee=2024&quoi=part_depense)-->22,6<!--/--> % de la dépense, et **<!--chiffre:mesure(avantages?annee=2024&quoi=part_lue)-->85<!--/--> % de ce
  total est LU** : la réversion dans l'enquête de la DREES auprès des caisses,
  et dix autres lignes dans les sous-postes des Comptes de la protection
  sociale, dont la majoration pour enfants à <!--chiffre:mesure(avantages?annee=2024&quoi=ligne&cle=majoration_enfants)-->7,8<!--/--> milliards — que le modèle
  chiffrait à zéro. Le COR chiffre l'ensemble des droits de solidarité à « de
  l'ordre d'un cinquième » : on y est. Ce que le modèle apporte n'est donc pas
  le chiffre mais la LISTE, et les <!--chiffre:mesure(avantages?annee=2024&quoi=calculees)-->14,5<!--/--> milliards qu'il calcule encore lui-même
  restent soumis à cette limite. Vingt-sept dispositifs sur quarante-cinq ne
  portent aucun chiffre, chacun avec sa raison écrite.

  **Une seconde limite, découverte en réparant la première : les deux mesures
  n'ont pas la même fenêtre.** Les sous-postes des comptes ne sont publiés que
  depuis 2020, la réversion depuis 2004, et le modèle calcule depuis 1959. Une
  ligne ne mélange donc jamais les deux périmètres — la règle a été posée après
  qu'un minimum vieillesse eut valu <!--chiffre:illustration()-->0,02<!--/--> milliard en 2019 par le modèle et 4,01
  en 2020 par les comptes, dans la même série. Le site porte en conséquence
  deux tracés qui ne s'additionnent pas : le NIVEAU sur cinq ans, la FORME sur
  soixante-six. Voir `docs/avantages_non_contributifs.md`.

- **Le diviseur est le même pour tout le monde, et il transfère à qui vit
  plus longtemps — le système actuel autant que les autres.** Ce fut la règle
  jusqu'au 21 septembre 2026 : l'espérance de vie du §5 de `methodologie.md`
  était alors celle de la population générale. Les
  pensionnés civils de l'État vivent un an de plus à 65 ans, d'après leur
  propre régime ; les 5 % d'hommes les plus aisés vivent sept ans de plus à
  65 ans que les 5 % les plus modestes, d'après l'INSEE. Depuis le
  20 septembre 2026, les deux écarts sont MESURÉS
  (`scripts/mortalite_population.py`, action 14) — et, depuis le
  21 septembre 2026, le diviseur par vingtile de niveau de vie est le DÉFAUT
  du modèle, stock compris, sur tous les chiffres du site ;
  `population_conversion=None` rend la table commune, et les chiffres
  ci-dessous sont mesurés contre elle. Pour le fonctionnaire sédentaire né en 1975, la
  table de sa population lui donne 1,5 an de rente de plus que la table
  commune, soit 5,7 % de pension notionnelle à capital égal et 54 000 € sur
  la vie sous le système actuel, dont la pension ne bouge pas d'un euro parce
  qu'aucun diviseur ne l'a calculée. Par le revenu, chaque cas type rattaché
  au vingtile de niveau de vie où son salaire le place : le salarié au SMIC a
  3,0 ans de rente de moins que la table commune ne lui en compte et
  l'exploitant agricole 3,7 de moins, le cadre 2,7 de plus et le libéral 3,1
  de plus — 49 000 € retirés au premier, 186 000 € ajoutés au dernier (3,2
  ans et 173 000 € avant que la règle de départ du libéral ne change, le
  22 septembre 2026), sur la
  vie et sous le système actuel. Le diviseur commun transfère donc des
  modestes vers les aisés, dans le sens qu'on craignait, puisque qui vit
  longtemps est aussi qui a le plus cotisé ; et ce n'est pas un défaut du
  notionnel, toute rente viagère à taux commun le porte, le droit en vigueur
  le premier. Ce que la mesure suppose est écrit avec elle : un rattachement
  par le salaire là où l'INSEE mesure un niveau de vie de ménage, un facteur
  constant dans le temps, une espérance de stock appliquée à des liquidants
  futurs, et une grille de cas types qui n'est pas une population. Ce que
  ce transfert coûte au régime se mesure aussi (`--deficit`) : un diviseur
  par vingtile baisserait la dépense des scénarios notionnels de 3,5 à
  4,4 %, de deux à cinq dixièmes de point de PIB de solde moyen, parce que les gros capitaux
  sont servis le plus longtemps. La page
  Coût l'applique depuis lors par les pensions de ses cas types, mais compte
  encore tout le monde à la mortalité générale : ce sous-compte déplace son
  rapport de masses de moins de 1 %, un dixième de point de PIB au plus en
  2070, et ne se corrigerait proprement qu'avec la distribution des pensions
  par niveau de vie.

- **La décote surpunit l'anticipation ordinaire et sous-punit l'extrême.**
  Mesuré en comparant ce que coûte une année d'anticipation sous le droit en
  vigueur et sous le coefficient de conversion notionnel, sur un fonctionnaire
  sédentaire de la génération 1965 : partir deux ans plus tôt laisse 81,7 % de
  la pension sous le droit actuel contre 84,1 % sous le notionnel — le droit est
  PLUS DUR de 2,4 points ; à cinq ans d'avance, plus dur de 7,0 points. Puis la
  décote bute sur son plafond de vingt trimestres et le rapport s'inverse : à
  huit ans d'avance le droit est plus doux de 0,8 point, à dix ans de 4,2, à
  douze ans de 6,4. Or l'anticipation extrême est exactement celle de la
  catégorie active, de la super-active, de la conduite SNCF et des militaires :
  le barème est le plus clément là où il devrait l'être le moins. Voir
  `docs/avantages_non_contributifs.md` §4 ter.

- **Une décote plafonnée ne sait pas dire qui part trop tôt, et le modèle en
  hérite.** L'article L. 14 borne la décote à vingt trimestres : un agent de
  catégorie active parti à <!--chiffre:cellule(data/reference/legislation/categorie_active.csv:age_ouverture?classement=active&generation=1960)-->57<!--/--> ans et un agent sédentaire parti le même jour
  butent tous deux sur le même plafond, et leurs pensions ne diffèrent que de
  quelques centaines d'euros par an pour la génération 1960 — la page Avantages
  en donne le chiffre, que le modèle calcule depuis le 22 septembre 2026 ; le
  chiffre que cette page et le site portaient en dur avait dérivé deux fois
  sans que rien ne le dise. Pour la génération 1965 l'écart tombe sous la centaine d'euros, le classement abaissant
  par ailleurs la durée requise d'un trimestre. Mesurer la
  valeur d'un avantage d'ÂGE par l'écart de MONTANT à date de départ fixe donne
  donc un chiffre petit — <!--chiffre:mesure(avantages?annee=2024&quoi=ligne&cle=categorie_active)-->0,6<!--/--> milliard en 2024 pour la catégorie active — et ce
  chiffre n'est pas faux, il est incomplet. Il porte de surcroît, depuis le
  22 septembre 2026, la durée requise propre aux emplois classés, que le
  contrôle d'isolement de `avantages.py` accepte pour ce seul avantage
  (`DUREE_REQUISE_EST_L_AVANTAGE`), le texte la donnant « au titre de la
  catégorie active ». Ce que l'avantage coûte, ce sont les annuités
  servies avant l'âge légal, que nulle décote ne rattrape. Elles valent **<!--chiffre:mesure(avantages?annee=2024&quoi=anticipees)-->10,9<!--/--> milliards en 2024**, dont <!--chiffre:mesure(avantages?annee=2024&quoi=anticipees&motif=classement)-->6,6<!--/--> pour le
  classement, <!--chiffre:mesure(avantages?annee=2024&quoi=anticipees&motif=regime_special)-->2,3<!--/--> pour les régimes spéciaux et <!--chiffre:mesure(avantages?annee=2024&quoi=anticipees&motif=carriere_longue)-->2,0<!--/--> pour la carrière longue
  (`scripts/cout_avantages.py --duree`). Ce sont des annuités anticipées et non
  un surcoût net — partir tôt, c'est aussi cotiser moins et mourir plus tôt en
  moyenne ; c'est exactement l'arbitrage qu'un coefficient de conversion
  notionnel rend automatique et que le droit actuel ne rend nulle part.

- **Le pilotage, et non plus le solde.** Le modèle calcule des droits
  individuels ; il porte une pyramide des âges, qui lui dit ce que chaque
  système COÛTERAIT ; il porte depuis peu les RESSOURCES, et donc le solde et le
  **coefficient d'équilibre** de chaque système, année par année, de 2002 à
  2070. Ce qui lui manque encore est le cran suivant : APPLIQUER ce
  coefficient. Un système notionnel réel ne laisse pas dormir un excédent — il
  relève les pensions jusqu'à l'équilibre, ou les abaisse, par un fonds de
  réserve et un facteur commun à toutes les pensions de l'année. Le modèle
  calcule ce facteur et ne l'applique jamais : toutes les courbes de coût de la
  page **Coût** sont celles d'un système qui ne se pilote pas. Le facteur étant
  commun, l'appliquer déplacerait les niveaux sans toucher aux ÉCARTS ENTRE
  CARRIÈRES, qui sont l'objet du modèle — mais il déplacerait bel et bien les
  niveaux, et un coefficient de <!--chiffre:mesure(coefficient?scenario=3)-->1,74<!--/--> en 2070 pour le scénario 3 ne se lit donc
  pas comme une économie de <!--chiffre:mesure(coefficient?scenario=3&quoi=economie)-->43<!--/--> % : il se lit comme la marge dont ce système
  disposerait pour servir davantage à prélèvement inchangé.

- **Les ressources ne sont pas celles du risque vieillesse, et ne peuvent pas
  l'être.** Les Comptes de la protection sociale, d'où vient toute la dépense du
  dépôt, NE VENTILENT PAS LEURS RESSOURCES PAR RISQUE : ils publient la dépense
  risque par risque et le financement de l'ensemble, maladie et famille
  comprises. Une « recette du risque vieillesse » n'a pas de définition
  comptable, les cotisations d'un régime polyvalent n'étant affectées à aucun
  risque. Le solde vient donc d'un autre compte et d'un autre périmètre : celui
  du COR — régimes légalement obligatoires, FSV compris, RAFP exclu —, dont on
  prend les DEUX colonnes, dépenses et ressources, pour ne pas soustraire deux
  périmètres. Les deux se recoupent à moins de trois dixièmes de point de PIB
  (<!--chiffre:cellule(data/reference/macro/comptes_retraite.csv:part_pib*100?annee=2024&poste=depenses)-->13,86<!--/--> % contre <!--chiffre:mesure(depense?annee=2024&quoi=part_pib_repartition)-->13,59<!--/--> % en 2024, <!--chiffre:mesure(depense?annee=2024&quoi=cor)-->407<!--/--> contre <!--chiffre:mesure(depense?annee=2024&quoi=repartition)-->398,8<!--/--> Md€), ce qui
  vaut contrôle et non identité ; seul
  le RAPPORT des masses, qui est sans dimension, passe de l'une à l'autre. Ce
  compte vaut `haute` et jamais `certifiee` : le COR consolide des comptes
  produits par les régimes, c'est le critère 1 du manifeste des sources.

### Le reste du périmètre

- **L'horizon de la projection.** La dépense observée s'arrête à 2024,
  dernière année publiée par la DREES ; la trajectoire projetée s'arrête à
  2070, dernière année des projections de population de l'INSEE. Ni l'une ni
  l'autre de ces bornes n'est une décision du dépôt : ce sont celles des
  sources. Au-delà de 2070, le dépôt ne dit rien, et le COR non plus.

- **Les comportements.** Les âges de liquidation sont ceux que l'utilisateur
  déclare. Or une réforme qui pénalise fortement les départs précoces conduit à
  les décaler. Le sens du biais est connu : les écarts affichés sont des effets
  **à comportement inchangé**, et ils surestiment donc la perte réelle — un
  assuré qui, dans un système notionnel, travaillerait deux ans de plus
  récupérerait à la fois des cotisations et un diviseur plus favorable.

- **Le net.** Le modèle calcule en **brut**, et le site convertit en net ce
  qu'on touche — la pension, le salaire —, saisie comprise. La conversion
  suppose ce que le §5 ante ter décrit : un taux de CSG sur les pensions qui
  est celui du taux plein pour tout le monde, faute de connaître le revenu
  fiscal du FOYER, que le modèle ne connaît pas puisqu'il décrit une carrière
  et non un ménage. Ce prélèvement étant proportionnel et identique dans tous
  les scénarios, il ne déplace aucun des écarts affichés.

- **L'arrondi des revenus portés au compte.** L'article L. 133-10 du code de
  la sécurité sociale arrondit à l'euro le plus proche « le montant des
  cotisations et contributions sociales et de leurs assiettes » — donc les
  revenus inscrits au compte, la fraction de <!--chiffre:illustration()-->0,50<!--/--> € étant comptée pour 1. Le
  modèle ne l'applique pas : il porte au compte des revenus reconstitués, au
  centime. L'écart est borné et il est petit — chaque année retenue s'écarte de
  <!--chiffre:illustration()-->0,50<!--/--> € au plus, donc leur moyenne aussi, donc une pension au taux plein de
  **<!--chiffre:illustration()-->0,25<!--/--> € par an** au plus, soit **<!--chiffre:illustration()-->0,02<!--/--> € par mois**, quel que soit le niveau
  de revenu. Deux
  raisons de ne pas l'appliquer aujourd'hui : la règle vise des assiettes
  DÉCLARÉES, que le modèle n'a pas — il synthétise ses revenus depuis un profil
  —, et la doctrine ne dit pas si l'arrondi précède ou suit la revalorisation,
  ce qui n'a aucun effet sur le résultat mais en aurait un sur ce qu'on pourrait
  affirmer. Le reste de la chaîne, lui, est conforme : les trimestres sont
  arrondis à l'entier supérieur (R. 351-27), et la pension n'est pas arrondie du
  tout — voir `methodologie.md`.

- **La capitalisation.** Le compartiment RAFP est isolé et servi à son propre
  barème, identique dans les six scénarios et sorti des totaux de la
  répartition (§3), mais son **rendement financier propre** n'est pas
  modélisé : ses points sont valorisés au barème publié par l'ERAFP,
  non par le rendement de son portefeuille. C'est le traitement demandé — seule
  la répartition est en cause — et il rend le RAFP comparable au reste plutôt
  que de le faire dépendre d'hypothèses de marché.

- **Les carrières réelles.** Une carrière se décrit de deux façons, et la
  seconde n'est plus réservée au Python : le **profil paramétrique** — des
  métiers, un niveau de revenu relatif, une progression —, ou le **relevé**
  saisi année par année dans le champ prévu du simulateur, qui n'en reconstitue
  rien. Il reste à ce chemin une approximation et une impossibilité.

  L'approximation est le MOIS. Un relevé donne l'année, jamais le mois : chaque
  ligne vaut donc une année civile pleine, sauf celle du départ, que la date de
  liquidation tronque parce que le modèle la connaît. L'année d'entrée dans la
  vie active reste comptée pour une année entière alors qu'elle est presque
  toujours partielle — son revenu est celui des mois travaillés, et le modèle ne
  peut pas l'annualiser sans savoir lesquels. Un régime liquidant sur les six
  derniers mois de service n'en souffre pas, cette année-là n'étant pas la
  dernière ; un régime qui prend les vingt-cinq meilleures années y voit une
  année faible de plus, exactement comme le droit.

  L'impossibilité reste l'INTERROGATION AUTOMATIQUE du répertoire de gestion
  des carrières uniques : il n'est pas ouvert au public, et son accès passe par
  une authentification personnelle qu'un script ne saurait porter sans détenir
  les identifiants de l'assuré. Ce qui a cédé, en revanche, c'est la recopie à
  la main : **le relevé se dépose maintenant en PDF sur le simulateur**, qui le
  lit dans le navigateur — il est téléchargé par l'assuré sur son compte
  retraite, et le fichier ne quitte pas la page. `moteur/js/lecture-pdf.js` en
  tire les lignes de texte, `moteur/js/releve-lu.js` la carrière, et le champ
  `releve` reçoit ce que l'un et l'autre ont compris. Restent quatre choses que
  le document lui-même ne donne pas, et que le site dit à qui le dépose :

  - **Le revenu est plafonné.** Le régime général ne reporte au compte que la
    part du salaire brut qui tombe sous le plafond de la Sécurité sociale :
    au-delà, le relevé n'affiche pas le salaire en entier, et la simulation lit
    donc un revenu tronqué. La carrière paramétrique, elle, ne l'est pas.
  - **Un régime qui compte en points ne porte aucun revenu.** Les professions
    libérales depuis 2004, les exploitants agricoles : leur relevé donne des
    points et des trimestres. La lecture prend les années et les trimestres,
    laisse le revenu à zéro et le dit — déduire un revenu du barème de la
    caisse serait écrire un chiffre que le document ne porte pas.
  - **Un état de services couvrant plusieurs années n'est pas réparti.** « Du
    01/09/1996 au 31/08/2001 », tel que la fonction publique l'écrit, ne dit ni
    le revenu de chaque année ni leur partage : la ligne ressort telle quelle
    et reste à saisir.
  - **Le document doit se reconnaître.** Un fichier qui ne porte ni le titre
    d'un relevé ni l'en-tête de la colonne des trimestres n'est pas lu du tout.
    C'est un vrai document qui l'a imposé : le rapport de l'OPEF sur les frais
    de l'épargne retraite, cent pages sans le moindre relevé, rendait
    vingt-deux « années de carrière » qui n'avaient jamais existé.

  Et un PDF qui n'est qu'une image — un scan, une photographie, une capture
  d'écran — ne porte aucun texte : rien ne s'y lit, et la page le dit plutôt
  que de rendre une carrière vide sans explication.

  **Ce qu'un vrai document a appris, le 22 septembre 2026 — et ce qu'il ne
  prouve pas.** La lecture avait été écrite contre des relevés d'essai, faute
  d'en avoir un vrai : aucun n'est public. La première estimation retraite
  déposée sur le site a corrigé quatre défauts d'un coup, et c'est elle qui fixe
  désormais les règles de lecture. **Ce document n'était pas intact** : produit
  par le composeur d'Info Retraite (`KslPrn`), il avait été rouvert dans une
  suite bureautique (`ONLYOFFICE 9.4`) pour être anonymisé, puis ré-exporté. Ce
  qui vient de la caisse et ce qui vient de l'éditeur se sépare donc, et il faut
  le séparer :

  - **De la caisse, et vérifiable comme tel** : les deux tableaux et leurs
    en-têtes, les colonnes, les unités écrites, la note de bas de tableau, le
    pied de page daté, les projections de départ. C'est le CONTENU, et c'est de
    lui que viennent les règles de lecture du relevé.
  - **De l'éditeur, ou probablement de lui** : les polices du fichier — du
    Calibri, qu'aucune administration n'emploie —, donc la table `ToUnicode` et
    la forme de ses plages ; et la couche de doublure, où le texte d'une page
    entière est collé bout à bout. Les deux défauts du lecteur de PDF ont été
    trouvés là, et les corriger est juste — la forme tableau d'un `bfrange` est
    de la norme, et le texte tourné existe partout — mais **rien ne dit encore
    qu'un document intact d'Info Retraite les aurait exigés**.

  Le relevé n'a donc toujours pas été confronté à un PDF de caisse INTACT. Ce
  qui a été vérifié sur celui-ci est que la carrière s'en lit en entier, et le
  contrôle vient du document lui-même : le total de trimestres enregistrés qu'il
  annonce en synthèse est exactement celui que la lecture recompose, année par
  année, depuis l'autre tableau. Le chiffre est sous l'action correspondante de
  la feuille de route : il appartient à un document qui ne peut pas être publié,
  et aucune sonde du dépôt ne saurait donc le recalculer.

  - **Un relevé porte deux tableaux, et ils se complètent.** L'un donne les
    trimestres année par année et ne porte aucun revenu ; l'autre donne les
    revenus par PÉRIODE — « 01/01/2025 31/12/2025 49 150 € » — et ne porte
    aucun trimestre. Une année se lit donc dans les deux à la fois.
  - **L'unité écrite l'emporte sur la position.** « 4 trim. », « 203,91 pts »,
    « 49 150 € » : une caisse écrit toujours ce que ses nombres sont, et s'y
    fier vaut mieux que de deviner une colonne. C'est ce qui permet de prendre
    à une ligne d'Agirc-Arrco sa durée sans prendre ses points pour un revenu —
    et de compter une période que seule la complémentaire a reportée.
  - **Un document mêle à sa carrière des lignes qui lui ressemblent.** Un pied
    de page daté, une valeur du point à une date, une phrase française qui
    porte une année, un montant et des trimestres, et des projections de départ
    en 2060. Quatre règles les écartent : une période a deux bornes, une ligne
    de tableau n'est pas une phrase, une ligne de tableau porte quelques
    nombres et non quarante, et un relevé ne rapporte jamais l'avenir.
  - **Un PDF peut porter deux fois le même texte** : une couche visible, mise
    en page, et une couche de doublure où toute une page est collée bout à
    bout. Additionnée à la première, elle faisait des revenus de deux millions
    d'euros. Celle-ci venait de la suite bureautique ; un document rouvert pour
    être anonymisé, ou simplement ré-enregistré, en porte une.

- **La coordination interrégimes.** Chaque régime liquide sur ses seules
  années, et la durée acquise dans chacun est comptée séparément — c'est le
  droit, et un régime et celui qui lui succède comptent pour un seul (voir
  §3). La **liquidation unique** (LURA), qui, depuis 2017, fait calculer par
  une seule caisse la retraite d'un polypensionné des trois régimes alignés,
  est servie depuis le 22 septembre 2026, avec la **proratisation croisée** de
  son salaire annuel moyen. En reste dehors sa troisième condition — la
  retraite de même nature déjà obtenue avant le 1er juillet 2017 —, qu'une
  carrière du dépôt, liquidée tout d'un coup, ne peut pas porter.

---

## 5 ante. Le pilier capitalisé : ce que sa rente suppose

Le compartiment de capitalisation obligatoire du scénario 6 est le seul endroit
du modèle où de l'argent est placé, et il porte donc des incertitudes que le
reste n'a pas. Six, et la première est de loin la plus lourde.

**1. La prime de terme n'est pas retirée des forwards.** Les versements futurs
se placent aux taux forward implicites de la courbe du jour. Sous l'hypothèse
des anticipations pures, le forward est le taux futur attendu ; en pratique, il
le dépasse d'une prime de terme que la littérature situe entre <!--chiffre:illustration()-->0,3<!--/--> et <!--chiffre:illustration()-->1<!--/--> point
sur les maturités longues quand la courbe est ascendante. **Le pilier est donc
flatté**, et d'autant plus que la carrière est longue. L'alternative — retirer
une prime estimée — supposerait davantage et se vérifierait moins ; le choix
est dit plutôt que corrigé. Ordre de grandeur : un demi-point de rendement sur
quarante ans vaut une dizaine de pour cent de capital final.

Depuis septembre 2026, le modèle **sait** la retirer :
`Parametres.prime_terme_trente_ans` décompose le taux observé en une moyenne de
taux courts attendus et une prime proportionnelle à la maturité, calcule les
forwards sur la première et rajoute la seconde à la maturité achetée — de sorte
qu'un placement comptant rend toujours le taux coté du jour. **Le paramètre vaut
zéro, et le site publie à zéro** : la réserve ci-dessus tient donc entière, et
ce qui change est qu'elle est désormais mesurable plutôt que seulement dite. À
0,005 — le milieu de la fourchette — le capital d'une carrière de trente-six ans
partant en 2060 recule de 4,8 %, et la rente de 23 € par mois.

Il ne porte que sur le **pilier**, et c'est une correction : portée sur la
courbe commune, la prime déplaçait aussi le taux auquel la page Coût finance
les déficits, donc le stock de dette de TOUS les systèmes — jusqu'à dix points
de PIB sur le système actuel, qui n'a pas de pilier capitalisé. Le coût de
rouler une dette courte se pose dans les mêmes termes et reste une question
ouverte, mais c'en est une autre, et un réglage du pilier n'est pas l'endroit
d'où la trancher. Un test tient la séparation.

Depuis, il est un **réglage du site** : « Taux futurs du pilier capitalisé »,
à côté de celui des frais, avec trois positions — les taux à terme de la
courbe (défaut), la prime retirée au milieu de la fourchette (<!--chiffre:mesure(constante?de=retraite_notionnelle.config&nom=PRIME_TERME_MILIEU&echelle=100)-->0,50<!--/--> point à
trente ans), la prime retirée au haut (<!--chiffre:mesure(constante?de=retraite_notionnelle.config&nom=PRIME_TERME_HAUTE&echelle=100)-->1<!--/--> point). Une réserve qu'un lecteur peut
chiffrer lui-même cesse d'être une réserve qu'on lui demande de croire, et le
choix de publier sous les anticipations pures redevient ce qu'il est : un
choix, pas un impensé.

Cette réserve en portait une autre, restée invisible tant qu'elle n'était pas
chiffrée : **sous les anticipations pures, l'allocation des maturités n'a
aucune conséquence.** C'est une identité, pas une approximation — découper un
horizon en un trente ans, en trois dix ans ou en quinze deux ans accumule
exactement la même chose, parce que c'est ce que l'arbitrage impose au forward,
et les frais annuels n'y changent rien. L'échelle glissante 2/10/30 que le
pilier pratiquait jusque-là était donc un paramètre libre sans effet ; elle a
été remplacée par l'adossement à l'horizon, qui est la bonne règle pour une
autre raison — l'actif sans risque d'une dette datée est le titre qui tombe ce
jour-là — et dont le changement n'a pas déplacé un centime de capital ni de
rente. Voir `docs/methodologie.md`.

**2. La courbe est celle d'un jour.** Elle est datée, publiée, recontrôlée,
mais elle est un instantané : le 17 septembre 2026 et non un mois plus tôt. Un
déplacement général de la courbe déplace tout le pilier, et rien dans le modèle
ne lisse cette dépendance. C'est assumé — une moyenne de courbes n'est la
courbe de personne — et c'est la raison pour laquelle le fichier de référence
garde les courbes successives : un chiffre publié doit pouvoir être refait tel
qu'il a été publié.

**3. Les frais sont ceux du marché, et leur baisse est une hypothèse.** Le
pilier supporte quatre frais, aux vraies moyennes du marché du PER individuel
en 2025, lues sur le rapport de l'OPEF (tableau T7) et sur celui du CCSF de
2021 : <!--chiffre:mesure(parametre?nom=frais_versement_capitalisation)-->1,09<!--/--> % sur versement et <!--chiffre:mesure(parametre?nom=frais_gestion_capitalisation)-->0,76<!--/--> % par an sur encours, moyennes pondérées
par les primes et par l'encours ; <!--chiffre:mesure(parametre?nom=frais_arrerages_capitalisation)-->0,99<!--/--> % sur arrérages, moyenne sur les vingt
assureurs déclarants et non sur les seuls neuf qui facturent (<!--chiffre:illustration()-->2,20<!--/--> %) ; et
<!--chiffre:mesure(parametre?nom=frais_encours_rente_capitalisation)-->0,52<!--/--> % par an sur la réserve de la rente, que l'OPEF ne mesure pas et que le
CCSF relevait sur 22 contrats sur 34, de <!--chiffre:illustration()-->0,60<!--/--> à <!--chiffre:illustration()-->1<!--/--> % par an, estimé au milieu
de la fourchette sur la part des contrats qui facturent. Ce dernier frais pèse
plus que les arrérages au diviseur du modèle. Trois choses que
ces sources disent sur ce que les moyennes sont :

- Le frais sur versement du PER (<!--chiffre:mesure(parametre?nom=frais_versement_capitalisation)-->1,09<!--/--> %) est le double de celui de
  l'assurance-vie (<!--chiffre:illustration()-->0,55<!--/--> %) et six fois celui du contrat de capitalisation
  (<!--chiffre:illustration()-->0,19<!--/--> %), pour les mêmes assureurs et les mêmes fonds en euros. L'OPEF
  l'explique par des frais fixes qui pèsent sur des primes petites. Une
  cotisation prélevée sur chaque paie n'a pas cette structure de coût.
- La moyenne des frais sur arrérages publiée est **non pondérée** et ne porte
  que sur les 9 organismes, sur 20, qui les facturent : onze assureurs sur
  vingt ne prélèvent rien sur la rente. Le <!--chiffre:illustration()-->2,20<!--/--> % est la moyenne de ceux qui
  facturent, le <!--chiffre:mesure(parametre?nom=frais_arrerages_capitalisation)-->0,99<!--/--> % celle du marché, et la médiane est nulle.
- Le frais de gestion du fonds en euros est le poste qui compte, parce qu'il
  s'applique chaque année à tout l'encours, et c'est celui qu'un régime
  obligatoire fait le plus baisser : la prime de pension suédoise, seul pilier
  obligatoire capitalisé adossé à un compte notionnel, coûte <!--chiffre:illustration()-->0,11<!--/--> % des
  encours en frais de fonds après remise et <!--chiffre:illustration()-->0,024<!--/--> % d'administration ; le
  Fonds de réserve pour les retraites, <!--chiffre:illustration()-->0,41<!--/--> % toutes charges comprises, dont
  <!--chiffre:illustration()-->8,6<!--/--> points de base de coûts fixes, en gérant des actions ; l'ERAFP
  provisionne « au moins <!--chiffre:illustration()-->0,2<!--/--> % des encours ». Aucun ne prélève sur les
  versements ni sur les arrérages.

**Ce que ces moyennes sont, et ce qu'on sait des médianes.** Les frais sur
versement et de gestion de l'OPEF sont des moyennes **pondérées** de tout le
marché remis à l'ACPR, par les primes pour le premier, par l'encours moyen pour
le second : un euro versé ou placé y pèse un euro, ce sont les vraies moyennes
de ce qui est payé. Aucune source publique ne donne de médiane pour ces deux
postes ; la seule autre mesure du même marché est le rapport du CCSF de
juillet 2021, sur 34 PER assurance et leurs tarifs affichés, en moyennes
arithmétiques non pondérées. Ce que l'on a, le 20 septembre 2026 :

| Poste | OPEF 2025, marché | Sur tous les déclarants | Médiane | CCSF 2021, 34 contrats affichés |
|---|---|---|---|---|
| Versement | 1,09 %, pondéré par les primes | idem | non publiée | maximum affiché 3,18 % en moyenne, 0 à 5 %, courtiers en ligne à 0 |
| Gestion, fonds en euros | 0,76 %, pondéré par l'encours | idem | non publiée, entre 0,75 et 0,90 % à en juger par la dispersion | 0,87 % en moyenne, 0,60 à 1 % hors un fonds à 2 %, 0,66 à 0,93 % par catégorie |
| Arrérages | 2,20 %, non pondéré, 9 facturants sur 20 | 0,99 % | nulle, onze déclarants sur vingt à zéro | 1,18 % zéros compris sur 30 contrats, 0 à 3 %, onze à zéro, 0,60 % (banques) à 2,30 % (mutuelles) |
| Réserve de rente | non mesuré | non mesuré | non publiée | 22 contrats sur 34 facturent, de 0,60 à 1 % par an |

**La baisse des frais, et ce qu'elle suppose.** Le modèle fait baisser chaque
poste par paliers (`Parametres.frais_*_paliers`), parce que c'est ainsi que
les frais ont bougé partout où une épargne retraite obligatoire a mis les
gérants sous plafond ou en concurrence, et les sources de chaque marche sont
des jeux `controle` du manifeste :

| Marché | Mécanisme | Ce qui s'est passé |
|---|---|---|
| Royaume-Uni | plafond de 0,75 % sur les fonds par défaut, avril 2015 | 0,48 % en moyenne en 2020 sur les régimes concernés, 0,29 % dans les régimes fiduciaires ; les régimes hors plafond passent de 0,79 % à 0,53 % |
| Chili | adjudication des nouveaux entrants tous les deux ans, depuis 2010 | commission du gagnant : 1,14 %, 0,77 %, 0,47 %, 0,41 %, puis 0,69 % en 2018, 0,58 %, 0,49 %, 0,46 % en 2025 ; 1,36 % avant ; un gagnant a remonté de 0,47 à 1,16 % une fois libre |
| Suède | remise imposée aux gérants de la prime de pension, plafonds en 2015 et 2021 | frais moyen net de 0,31 % en 2013, 0,21 % en 2020, 0,13 % en 2022, 0,11 % en 2026 ; 0,45 % sans la remise |
| États-Unis | concurrence seule | fonds actions, pondérés par les encours : 1,04 % en 1996, 0,40 % en 2025, 3,3 % de baisse par an ; plans 401(k) : 0,76 % en 2000, 0,26 % en 2024 |
| Australie | produit par défaut MySuper, 2014 ; test de performance, 2021 | frais MySuper de 1,05 % à 1,00 % en 2023, « la plus forte baisse depuis 2014 » ; plus lent que les autres |
| France | concurrence des courtiers en ligne, transfert des PER | frais sur versement, mesuré sur les primes de l'année : PER 1,20 % → 1,09 %, assurance-vie 0,75 % → 0,55 % en deux ans ; frais de gestion, mesuré sur tout l'encours : 0,73, 0,77, 0,76 % |

Trois leçons, et le modèle les tient. **La baisse va par à-coups**, une
décision puis un plateau, d'où des paliers plutôt qu'une pente : le frais de
gestion suit le rythme américain, le seul observé sur trente ans, par marches
de dix ans (<!--chiffre:mesure(parametre?nom=frais_gestion_capitalisation)-->0,76<!--/-->, <!--chiffre:mesure(parametre?nom=frais_gestion_paliers.0.1)-->0,54<!--/-->, <!--chiffre:mesure(parametre?nom=frais_gestion_paliers.1.1)-->0,39<!--/-->, <!--chiffre:mesure(parametre?nom=frais_gestion_paliers.2.1)-->0,28<!--/-->, <!--chiffre:mesure(parametre?nom=frais_gestion_paliers.3.1)-->0,20<!--/--> % en 2066, le plancher de l'ERAFP) ;
le frais sur versement rejoint l'assurance-vie de 2025 en 2031, le contrat de
capitalisation en 2036, zéro en 2046 ; le frais sur arrérages, dont la médiane
est déjà nulle, s'éteint en 2046 ; le frais sur la réserve suit le rythme de
la gestion. **Elle porte sur les nouveaux dépôts, et un peu sur le stock** :
un frais de gestion est contractuel, l'OPEF le montre en deux ans, et les
lignes de l'échelle portent le tarif de leur cohorte, qui ne referme chaque
année que <!--chiffre:mesure(parametre?nom=convergence_frais_stock&echelle=100)-->10<!--/--> % de son écart avec le tarif du jour, la moitié en sept ans,
entre le contrat privé qu'on ne renégocie pas (0) et le plafond qui touche
tout le stock d'un coup (1), comme au Royaume-Uni et en Suède. **Elle n'est
pas acquise** : le Chili a vu la commission d'une caisse remonter de <!--chiffre:illustration()-->0,47<!--/--> % à
<!--chiffre:illustration()-->1,16<!--/--> % dès qu'elle a cessé d'être adjudicataire, et le modèle ne fait jamais
remonter un frais. Les paliers sont une hypothèse, datée et sourcée, pas une
mesure ; leurs années et leurs niveaux se changent en un endroit.

**Ce que chaque hypothèse déplace.** Rente mensuelle du pilier, les deux
cotisations réunies, pour un non-cadre né en 2004 qui cotise de 22 à 64 ans,
donc toute sa carrière après la bascule (le 20 septembre 2026, courbe du 17,
diviseur par niveau de vie) :

| Réglage | Rente | Écart |
|---|---|---|
| retenu : moyennes 2025 du marché, paliers, convergence 0,10 | 1 800 € | référence |
| PER 2025 tel que vendu, figé, sans frais de réserve, l'ancien réglage : 1,09 / 0,76 / 2,20 | 1 665 € | − 8 % |
| moyennes 2025 du marché figées, aucune baisse | 1 553 € | − 14 % |
| paliers, mais le stock garde son tarif, convergence 0 | 1 750 € | − 3 % |
| paliers, et tout le stock suit, convergence 1 | 1 832 € | + 2 % |
| retenu, sans frais sur la réserve de rente | 1 839 € | + 2 % |
| aucun frais | 2 035 € | + 13 % |

Pour un assuré né en 1985, qui liquide en 2049, les paliers ne sont encore
qu'à moitié parcourus : les moyennes figées lui coûtent 7 %, et le frais sur
la réserve, encore à 0,27 %, 4 %. Pour un assuré né en 1970, qui liquide en
2034, aucun palier n'est atteint, et le nouveau réglage sert 7 % de moins que
l'ancien, parce que le frais sur la réserve de rente (8 %) pèse plus que la
baisse des arrérages ne rend. Sur le total servi par le scénario 6, dont le
pilier pèse au plus deux cinquièmes, chaque hypothèse déplace donc de un à six
points. Le sens de chacune est connu, la taille est encadrée, et le choix
reste celui du paramètre.

**4. Aucun risque n'est simulé.** Le pilier est sans risque par construction,
et c'est un choix de proposition autant que de modèle : un régime obligatoire
qui promet une rente ne peut pas la gager sur des actions. Mais le modèle ne
dit rien de ce qu'un panachage aurait donné, ni de la volatilité qu'il aurait
fallu accepter pour cela. Il ne dit rien non plus du risque de crédit : la
courbe retenue est celle des souverains les mieux notés, pas celle de la dette
française, qui rendait <!--chiffre:illustration()-->51<!--/--> points de base de plus au dix ans
le jour de la courbe.

**5. Aucune fiscalité.** Les versements au PER sont déductibles du revenu
imposable, la rente est imposable à la sortie, et le capital transmis au décès
relève d'un régime successoral propre. Tous les montants du dépôt sont bruts,
et l'avantage fiscal à l'entrée — qui est une part réelle du rendement d'un PER
pour un contribuable imposé — n'est pas compté. Il joue en sens inverse des
points 1 et 2 : il minore la rente affichée.

**6. La garantie vieillesse compte la rente capitalisée, et la prend pour ce
qu'elle est.** Le programme a tranché le 19 septembre 2026 : une allocation
différentielle regarde toutes les ressources de retraite, la rente du pilier
comprise, volontaire comme obligatoire. Ce paragraphe a dit l'inverse jusqu'au
23 septembre 2026, bien après que le code l'eut réglé. Reste la manière de la
compter entre le départ et l'ouverture, puis année après année : la rente est
NOMINALE et constante, et les prix seuls la déprécient. La garantie la
revalorisait jusqu'à la même date comme la pension notionnelle, sur la masse
salariale, quand le compte des flux du pilier la servait nominale : deux
conventions pour la même rente, et un complément sous-estimé d'autant. La
rente prise nominale, et la règle du stock appliquée à la pension, ajoutaient
le jour du changement <!--chiffre:illustration()-->0,9<!--/--> milliard de 2026 à la garantie de 2070 et
<!--chiffre:illustration()-->33<!--/--> au cumul de 2026 à 2070.

Une dernière chose, qui n'est pas une limite mais une convention à connaître :
**l'espérance de capital transmis n'est pas conditionnée à la survie**. Elle se
lit de l'ouverture du pilier, et se rapporte donc à quelqu'un qui peut mourir
avant son départ, quand la rente affichée, elle, suppose qu'il l'atteint. Les
deux chiffres décrivent deux futurs, et leur somme n'a pas de sens.

---

## 5 ante bis. La fiche de paie : neuf réserves, dont trois décisives, et deux que la restitution ajoute

Le site affiche, sous les quatre pensions, ce qu'un actif touche PENDANT qu'il
cotise : coût du travail, revenu brut, revenu net, sous le droit en vigueur et
sous la proposition. C'est la seule grandeur du dépôt qui ne soit pas une
pension, et elle porte ses incertitudes propres. Trois d'entre elles — la 1, la
2 et la 5 — commandent le SIGNE du résultat, et pas seulement sa taille.

**1. L'incidence est supposée intégrale, et c'est une hypothèse.** Le coût du
travail est tenu fixe, et le salaire brut est celui qui l'épuise sous les
nouveaux taux : ce que l'employeur ne verse plus en cotisations, il le verse en
salaire. C'est la lecture que fait l'économie du travail à long terme — une
cotisation patronale est du salaire différé —, et c'est la plus favorable à une
baisse de cotisation. Rien n'oblige un employeur à rendre son économie du jour
au lendemain, et la lecture prudente, où seule la part salariale bouge, donne
environ la moitié du gain : c'est `Incidence.ASSIETTE` dans `remuneration.py`,
et la réserve 5 dit pour quels statuts c'est la seule lecture disponible.

**2. Le partage salarial/patronal du taux unique n'est pas neutre, et la
proposition ne le fixait pas.** Elle dit « 18 %, salariale et patronale
additionnées ». Le dépôt a partagé moitié-moitié jusqu'au 20 septembre 2026,
faute d'avoir mesuré ; **le programme a tranché ce jour-là, sur la mesure : la
part patronale ne bouge pas — 16,67 points, ce qu'elle vaut aujourd'hui — et la
part salariale tombe de 11,31 à 6,33.** On croirait ce choix sans effet sous
l'incidence intégrale ; il ne l'est pas, pour deux raisons distinctes : la CSG
et la CRDS sont assises sur le BRUT, que le partage déplace ; et la réduction
générale n'efface que des cotisations PATRONALES. À deux fois le SMIC, le gain net
mensuel du partage retenu vaut **+182 € dès le premier mois et +175 € une fois
le brut stabilisé** ; il valait −7 puis +81 sous le moitié-moitié, −426 puis
−141 si les 23 points étaient entièrement salariaux, +412 puis +286 s'ils
étaient entièrement patronaux. Ces quatre lectures isolent le partage : elles
neutralisent la restitution aux salaires décidée le même jour, qui s'ajoute à
toutes et que les réserves 8 et 9 de ce bloc décrivent. Le paramètre pèse donc toujours plus que la
baisse de taux elle-même, et c'est ce qui rend son arbitrage politique.

**Ce que le choix retenu achète, et ce qu'il coûte**, mesuré par
`scripts/partage_taux_unique.py` et détaillé à l'action 56 de la feuille de
route. Il achète l'immédiateté : la baisse est sur la fiche le lendemain de la
réforme, sans hypothèse d'incidence, et elle ne fuit pas, le brut ne bougeant
pas pour grossir l'assiette de la CSG et des autres branches. Il coûte le
brut : celui-ci ne monte pas, donc ni les droits qui en dépendent, ni le crédit
au compte notionnel. Le partage inverse ferait monter le brut de 2,9 %, mais
des années plus tard, amputé du quart en chemin, et de rien du tout au SMIC.
C'est la réserve la plus lourde de ce bloc, et elle n'a pas disparu en étant
tranchée : elle a changé de nature, d'un paramètre non mesuré à un arbitrage
entre le net d'aujourd'hui et le brut de demain.

**3. Le résultat au voisinage du SMIC était négatif, et ne l'est plus.** Il
l'était sous le moitié-moitié, pour une raison qui tient et qu'il faut garder
en tête : la réduction générale dégressive unique efface depuis 2026 la
totalité des cotisations patronales de son périmètre au niveau du SMIC — son
coefficient maximal, <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:reduction_generale.coefficient_maximal*100)-->40,21<!--/--> %, est exactement leur somme —, si bien qu'un
salarié au SMIC ne supporte aujourd'hui que ses <!--chiffre:mesure(fiche?exemple=smic&quoi=salarie)-->11,3<!--/--> points salariaux, et que
baisser la part patronale ne lui rend rien. Le partage retenu ne touche pas à
cette part : il ramène la retenue de l'assuré à <!--chiffre:mesure(fiche?exemple=smic&quoi=salarie&systeme=proposition)-->6,33<!--/--> points, et le gain au SMIC
est de **+<!--chiffre:mesure(gain_net?exemple=smic&en=mensuel)-->89<!--/--> € par mois à coût du travail inchangé**, et davantage le premier
mois, à brut inchangé. *Corrigé le 23 septembre 2026* : la phrase disait
l'inverse, ce chiffre pour celui du premier mois.

**Deux réserves subsistent au SMIC, et elles sont de sens opposé.** Le coût du
travail y monte, à brut inchangé, de **66 € par mois** : la part patronale du
pilier capitalisé est hors du périmètre de la réduction générale, donc
l'employeur la verse pour de bon, là où la réduction absorbait ce que le
régime général lui prenait. Ce n'est pas le seul niveau où il bouge, comme
cette réserve l'écrivait jusqu'au 23 septembre 2026 : la réduction s'éteignant
à mesure que le salaire monte, la hausse diminue — 48 € à 1,2 SMIC, 30 € à 1,5,
12 € à 2 — et devient une baisse à 3 SMIC, où la réduction ne mord plus.
`scripts/partage_taux_unique.py` imprime la colonne entière. Et la lecture de long terme y est
impossible en droit, comme la réserve 4 le dit : elle supposerait un brut
inférieur au salaire minimum.

**4. L'incidence intégrale n'est pas praticable au SMIC.** Elle y supposerait un
salaire brut inférieur au salaire minimum, ce que la loi interdit. Dans la
réalité, c'est le coût du travail qui monterait. Le site pose un avertissement
quand le cas se produit ; le modèle, lui, ne recalcule pas la variante « coût du
travail en hausse », qui supposerait de décider ce que l'employeur en fait.

**5. Le gain d'un fonctionnaire et celui d'un salarié du privé ne se comparent
pas terme à terme.** Le site couvre désormais quatre profils, et le découpage
n'est pas celui des familles de statut : c'est celui de ce que l'on sait de
l'employeur. Quand il verse des taux de DROIT COMMUN — un salarié du privé, un
agent d'un régime spécial que la fermeture de 2023 a versé au régime général, un
agent public non titulaire —, le site affiche un coût du travail et le tient
fixe : l'incidence est intégrale. Quand ce qu'il verse est un taux
d'ÉQUILIBRE — <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2026&regime=fonction_publique_etat)-->82,28<!--/--> % du traitement pour l'État en 2026, <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2026&regime=cnracl)-->37,65<!--/--> % pour la
CNRACL —, **le site n'affiche pas de coût du travail** : ce taux est fixé pour
que le compte d'affectation spéciale « Pensions » tombe juste, non parce que
l'agent acquerrait <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2026&regime=fonction_publique_etat)-->82<!--/--> % de son traitement en droits nouveaux, et poser dessus
l'incidence intégrale afficherait une hausse de salaire de soixante-dix points
qui n'existe pas — la dette de pensions qu'il finance, elle, reste à payer. Pour
ces statuts, le traitement n'est donc ni tenu fixe ni porté à l'incidence
intégrale : la moitié de ce que l'employeur cesse de verser remonte dans le
traitement, l'autre moitié paie la dette de pensions déjà promises
(`Incidence.PARTAGEE`, décidée le 20 septembre 2026). L'État garde en entier ce
que son taux payait de départs anticipés, que la proposition supprime
(<!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*-100?population=militaires&poste=avantages_professionnels)-->33,8<!--/--> points de la solde d'un militaire, <!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*-100?population=civils&poste=avantages_professionnels)-->1,5<!--/--> point du traitement d'un civil
dans le tableau de la Cour des comptes) : seul le reste se partage, depuis le
24 septembre 2026. Le partage est une décision, non une mesure, et mettre le
gain qu'il donne en regard de celui d'un salarié du privé compare deux
hypothèses et non deux statuts. La page le dit à l'endroit où elle affiche le
chiffre. Un indépendant, lui, tient son revenu fixe, et là ce n'est pas une
hypothèse : il n'a pas d'employeur, donc rien à répercuter.

**5 bis. Quatre familles de statut ne reçoivent toujours aucune fiche de paie.**
Les salariés et exploitants agricoles — la MSA a ses propres taux hors
retraite —, l'outre-mer, dont chaque collectivité a sa caisse, les élus, dont
l'indemnité de fonction n'est pas un salaire, et qui n'a pas d'emploi. Mieux
vaut rien qu'un net faux, et c'est un test qui le tient.

**5 ter. Ce que chaque profil laisse dehors.** Pour un fonctionnaire, la
retraite additionnelle de la fonction publique (RAFP), assise sur les PRIMES que
l'assiette du dépôt — traitement indiciaire brut et NBI — exclut par
construction : un agent dont les primes pèsent lourd ne voit ici qu'une fraction
de sa feuille de paie. Pour un indépendant, la contribution à la formation
professionnelle (un forfait de <!--chiffre:illustration()-->0,25<!--/--> % du plafond, et non un taux, laissé dehors
par symétrie avec les taxes sur salaires du privé) et l'assiette minimale que la
loi impose aux très bas revenus, faute de savoir si l'assuré relève d'une de ses
exonérations : le net affiché en bas de barème est un plafond. Ses cotisations
de retraite sont par ailleurs celles des fiches de régime, qui alignent
l'artisan et le commerçant sur le régime général — <!--chiffre:valeur(data/reference/regimes/base_prive.yaml:regimes.code=regime_general.periodes.debut=2023.taux_cotisation_retraite*100)-->15,45<!--/--> % sous le plafond et
<!--chiffre:illustration()-->2,51<!--/--> % déplafonnés plutôt que <!--chiffre:illustration()-->17,15<!--/--> % et <!--chiffre:illustration()-->0,72<!--/--> % : c'est la convention du modèle
entier, et la fiche de paie ne peut pas en diverger sans que le compte notionnel
et elle cessent de dire la même chose. Enfin, pour un agent public non
titulaire, le coefficient maximal de la réduction générale reste celui du décret
— un chiffre national bâti sur les taux du privé —, alors que le périmètre de
son employeur est plus étroit de la CEG et plus large de l'Ircantec ; ce qui
borne la réduction est alors la règle générale, qui interdit d'effacer plus que
ce qui est dû.

**6. Le coût du travail affiché est un plancher.** Ne sont comptées ni la taxe
d'apprentissage, ni la contribution à la formation, ni la participation à la
construction, ni le versement mobilité, ni la prévoyance et la mutuelle
d'entreprise. Aucune ne bouge d'un système à l'autre, et plusieurs dépendent de
la commune ou de la taille de l'entreprise ; les porter demanderait de choisir
un employeur type de plus. L'employeur retenu est une entreprise de cinquante
salariés et plus ; sous le seuil, le FNAL et le coefficient de la réduction
générale valent <!--chiffre:illustration()-->0,40<!--/--> point de moins. Le taux d'accidents du travail est le taux
moyen d'OpenFisca (<!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:profils.salarie_prive.postes.code=accidents_travail.employeur.0.taux*100)-->3,00<!--/--> %), au-dessus du taux net moyen national ; il ne déplace
aucun écart entre systèmes, seulement le niveau du coût affiché.

**7. Les taux sont ceux d'un millésime, appliqués aux années à venir.** Le
barème est celui en vigueur au 1er janvier 2026, reconduit tel quel jusqu'au
départ : le modèle ne prévoit pas la prochaine loi de financement. Les salaires,
le plafond et le SMIC, eux, suivent les séries projetées, si bien que le rapport
du salaire au SMIC — ce qui commande la réduction générale — reste stable. Les
taux viennent d'OpenFisca-France, transcription tierce du Journal officiel :
fiabilité `haute`, jamais `certifiee`. Quatre barèmes ont en revanche été lus à
la source dans l'index LEGI : la réduction générale (L. 241-13, version du
1er janvier 2026, LEGIARTI000053280526) et les trois barèmes d'indépendant que
la réforme de l'assiette unique de 2024 a réécrits et dont OpenFisca porte
encore la rédaction de 2018 — maladie et maternité (D. 621-1 et D. 621-2),
allocations familiales (D. 613-1) et indemnités journalières (D. 621-3). C'est
la réserve à surveiller en sens inverse : là où OpenFisca a du retard, le dépôt
ne le voit que s'il va lire.

**8. La suppression de la taxe sur les salaires ne se voit sur aucune fiche de
paie du modèle, et c'est un manque, pas un oubli.** Depuis le 20 septembre
2026, la proposition supprime les deux impôts du poste « impôts et taxes
affectés » qui sortent d'une rémunération — la taxe sur les salaires, dont
<!--chiffre:illustration()-->58,35<!--/--> % va à la branche vieillesse (L. 131-8, 1°), et le forfait social, qui
lui va en entier (L. 241-3, 1°). Or la taxe sur les salaires n'est due que par
les employeurs NON assujettis à la TVA — hôpitaux, banques, assurances,
associations —, et le profil d'employeur du dépôt est une entreprise de
cinquante salariés et plus assujettie à la TVA : la ligne n'y est pas, et sa
suppression n'y rend donc rien. Un salarié d'hôpital ou d'association verrait,
lui, son coût du travail baisser d'autant, et sous l'hypothèse d'incidence du
module cela remonterait dans son salaire. Le dépôt COMPTE cette suppression
dans l'enveloppe rendue — c'est ce que la page Coût chiffre —, mais ne la
RÉPARTIT sur personne. Le corriger demanderait un cinquième profil, celui de
l'employeur non assujetti, et le barème de la taxe, qui est progressif par
tranches. Même remarque pour le forfait social, assis sur l'intéressement et la
participation, que la fiche du dépôt ne porte pas davantage.

**9. La pension est calculée sur le revenu de la carrière, pas sur le brut que
la fiche affiche.** C'est vrai depuis toujours et cela ne pesait presque rien :
sous l'incidence intégrale, le brut d'un salarié du privé monte de quelques
pour cent, et la pension calculée sur l'ancien brut est sous-estimée d'autant.
Depuis que la contribution d'équilibre d'un employeur public est partagée, cela
pèse beaucoup plus : le traitement d'un fonctionnaire d'État monte d'un tiers
sur la fiche, et sa pension continue d'être calculée sur le traitement
d'avant. **Le dépôt sous-estime donc la pension de la proposition pour les
agents publics**, et l'écart est du même ordre que la hausse du traitement. Le
corriger demanderait de reboucler la fiche de paie sur la carrière — le brut
sous la proposition devenant l'assiette de la cotisation —, ce qui est une
boucle de point fixe et non un calcul de plus. La fiche de paie et la pension
restent, pour l'instant, deux lectures d'un même monde qui ne se parlent pas.

Rien de tout cela ne touche une pension : retiré, le modèle calcule exactement
les mêmes six scénarios.

---

## 5 ante ter. Le net et le brut : ce que la bascule suppose

Le simulateur se lit entièrement en net ou entièrement en brut, saisie comprise.
Quatre réserves, dont la première commande tout le reste.

**1. Le taux de CSG sur les pensions est celui du TAUX PLEIN, pour tout le
monde.** L'article L. 136-8 le fait dépendre du revenu fiscal de référence du
foyer, perçu l'avant-dernière année, et en tire quatre cas pour une part de
quotient familial (montants 2026, revalorisés chaque année sur les prix) :
exonéré jusqu'à <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.bareme_csg.libelle=exonéré.revenu_fiscal_maximum)-->13 048<!--/--> €, <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.bareme_csg.libelle=taux réduit.taux*100)-->3,80<!--/--> % jusqu'à <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.bareme_csg.libelle=taux réduit.revenu_fiscal_maximum)-->17 057<!--/--> €, <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.bareme_csg.libelle=taux médian.taux*100)-->6,60<!--/--> % jusqu'à <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.bareme_csg.libelle=taux médian.revenu_fiscal_maximum)-->26 472<!--/--> €,
<!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.bareme_csg.libelle=taux plein.taux*100)-->8,30<!--/--> % au-delà. Le simulateur ne demande ni la composition du foyer, ni les
autres ressources, ni un revenu d'il y a deux ans : il applique donc <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.csg_taux_plein*100)-->8,30<!--/--> %,
plus <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.crds*100)-->0,50<!--/--> % de CRDS et <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.casa*100)-->0,30<!--/--> % de CASA, soit **<!--chiffre:mesure(prelevement_pension)-->9,10<!--/--> %**.

La convention SURESTIME le prélèvement sur les petites pensions — et ce sont
justement celles des scénarios notionnels. Une pension de <!--chiffre:illustration()-->660<!--/--> € par mois
placerait son titulaire, s'il vivait seul et n'avait rien d'autre, sous le
premier seuil : il serait exonéré des trois, et son net vaudrait son brut. Le
site lui retire <!--chiffre:mesure(prelevement_pension)-->9,1<!--/--> %. L'écart entre systèmes affiché en net est donc un peu
RESSERRÉ pour les petites pensions, et exact pour les grandes. La page le dit
sous la clé de lecture.

**2. La cotisation maladie de <!--chiffre:illustration()-->1<!--/--> % sur la retraite complémentaire n'est pas
comptée.** Elle ne porte que sur une partie de la pension, et les cinq scénarios
notionnels ne distinguent pas base et complémentaire — leur compte est unique.
L'appliquer aux uns et pas aux autres fabriquerait un écart qui ne viendrait
d'aucune règle. Le net d'un retraité du privé est donc, de ce fait, très
légèrement surestimé.

**3. La rente du pilier capitalisé suit le barème des pensions**, et c'est une
convention : le dépôt la traite en rente viagère à titre GRATUIT, ce qu'elle est
quand la cotisation qui l'a constituée a été prélevée à la source et déduite —
le cas d'une cotisation obligatoire. Une rente à titre onéreux relèverait des
prélèvements sur revenus du patrimoine, à <!--chiffre:illustration()-->17,2<!--/--> % sur une fraction du montant qui
dépend de l'âge. La proposition ne tranche pas.

**3 bis. Le taux de remplacement suit le mode, et il MONTE en net.** Le modèle
le calcule brut sur brut. En mode net, le site le convertit — pension nette
rapportée au dernier revenu net —, sans quoi il serait le seul chiffre de la
page à parler l'autre langue. Le taux net dépasse alors le taux brut de
plusieurs points. Ce n'est pas
un artefact, c'est un fait du système français — une pension est prélevée de
<!--chiffre:mesure(prelevement_pension)-->9,1<!--/--> %, un salaire d'une vingtaine de points — et il est rarement montré. La
conversion emprunte le rapport net/brut de la DERNIÈRE fiche de paie de la
carrière, celle de l'année du départ, qui est l'année du dénominateur ; pour un
statut sans fiche de paie, le taux reste brut faute de pouvoir le netter
honnêtement.

**4. Ce qui reste brut, et le restera.** Un CAPITAL notionnel et une ASSIETTE de
cotisation n'ont pas de net : on ne « nette » pas un capital. Les tableaux de
détail — décomposition par régime, capital, cotisations versées, contribution de
l'employeur — restent donc en brut dans les deux modes, et c'est leur seule
lecture possible. La bascule ne gouverne que ce qu'on TOUCHE : le salaire et la
pension.

**Et un mot sur la saisie.** En mode net, le nombre tapé est un net mensuel que
le modèle convertit en brut en résolvant la fiche de paie du statut — ce n'est
pas une estimation, c'est l'inverse exact du calcul qui produit le net. Les
statuts que le modèle ne sait pas décrire — exploitant agricole, élu,
collectivités d'outre-mer — font exception : leur montant est lu tel quel, et le
formulaire l'affiche plutôt que de le taire.

---

## 5 bis. Le coût agrégé : ce qui est observé, ce qui est estimé

La page **Coût** superpose deux natures de chiffres, et il faut les séparer pour
la lire.

**La dépense observée n'est pas modélisée.** Elle vient des Comptes de la
protection sociale de la DREES, risque vieillesse-survie, poste `E11-2`, et elle
est **certifiée** : recontrôlée contre l'API du producteur à chaque exécution,
1959 à 2024 pour le total, 1990 à 2024 pour la ventilation par système. Deux
réserves de PÉRIMÈTRE, et non de fiabilité :

- le risque vieillesse-survie est plus large que « les retraites » : il porte
  aussi le minimum vieillesse, la dépendance des personnes âgées et la retraite
  supplémentaire par capitalisation, soit <!--chiffre:mesure(depense?annee=2024&quoi=hors_repartition)-->27,9<!--/--> milliards sur <!--chiffre:mesure(depense?annee=2024)-->426,7<!--/--> en 2024. La
  ventilation permet de les retrancher, et la page affiche les deux grandeurs ;
- la ventilation ne commence qu'en 1990. De 1981 à 1989 la DREES en publie une
  autre, dont les périmètres ne se raccordent pas — « Régime général de la
  Sécurité sociale » y recouvre ce qui est aujourd'hui réparti entre la Cnav et
  d'autres organismes. Personne n'a publié le raccord : c'est une impasse
  démontrée, et non un oubli.

Le découpage lui-même est celui de la **comptabilité nationale**, par secteur
institutionnel et non par caisse. Deux conséquences qu'il faut connaître :
« régimes spéciaux » réunit la CNRACL — donc la fonction publique territoriale
et hospitalière —, la SNCF, la RATP et les IEG ; et « régime général » absorbe à
compter de 2020 les artisans et les commerçants, dont le régime a été adossé à
la Cnav. La marche de 2020 est une réorganisation, pas une dépense nouvelle.

**Le coût des quatre autres systèmes est estimé, et ne peut pas être autre
chose.** Il est obtenu en multipliant les pensions de répartition obligatoire
observées par le rapport des masses de pension — la moyenne des écarts entre
systèmes, pondérée par le poids de chaque génération dans la masse de l'année.
*Corrigé le 23 septembre 2026* : le rapport multipliait jusque-là le risque
vieillesse-survie entier, et réduisait donc comme des pensions l'aide à
l'autonomie, la retraite supplémentaire et le minimum vieillesse, qui ne sont la
pension d'aucun système. Les économies du passé en étaient grossies de près
d'un dixième. Avant 1990, que la DREES ne ventile pas, la part de la
répartition dans le total est celle de 1990 : une hypothèse, que l'aide à
l'autonomie, inexistante alors, et le minimum vieillesse, plus lourd,
tirent en sens contraires. Ce rapport porte quatre
approximations, énoncées sur la page — la quatrième ayant cessé d'en être une
le 19 septembre 2026 :

1. **Les effectifs de génération ne sont plus supposés.** Cette page a d'abord
   pesé toutes les générations à égalité, faute de pyramide des âges ; elle
   porte désormais celle de l'INSEE, observée jusqu'en 2023. On sait donc
   maintenant ce que valait l'hypothèse levée : elle déplaçait l'écart cumulé du
   scénario 2 de six dixièmes de point sur soixante-six ans (−77,3 % contre
   −77,9 %). C'était peu, et c'est désormais mesuré plutôt qu'argumenté.
2. **Les treize cas types ne pèsent plus d'un poids égal.** Ils ont longtemps
   pesé ainsi, faute de source, et cette page affirmait qu'« aucune source ne
   fixerait » la pondération. C'était faux : l'enquête annuelle auprès des
   caisses de retraite dénombre les retraités caisse par caisse et année par
   année depuis 2004. Chaque cas type porte désormais l'effectif de sa caisse ;
   l'agent de conduite pèse <!--chiffre:mesure(poids?cas=agent_sncf_conduite)-->0,7<!--/--> % et non <!--chiffre:mesure(poids?cas=agent_sncf_conduite&ponderation=egale)-->7,7<!--/--> %, et les quatre carrières du
   privé <!--chiffre:mesure(poids?cas=smic_carriere_complete|salaire_moyen|cadre|carriere_interrompue)-->63<!--/--> % à elles quatre.

   Ce que l'ancienne convention valait est donc mesuré plutôt qu'argumenté, et
   **le sens du biais annoncé n'était juste qu'à moitié**. On disait le rapport
   affiché « plutôt un plancher », les départs très précoces que le notionnel
   pénalise le plus étant surreprésentés. C'est vrai des scénarios qui portent
   la part patronale — le scénario 4 passe de <!--chiffre:mesure(ecart_passe?scenario=4&ponderation=egale)-->−55,6<!--/--> % à <!--chiffre:mesure(ecart_passe?scenario=4)-->−52,6<!--/--> % — et faux du
   scénario 2, qui passe de <!--chiffre:mesure(ecart_passe?scenario=2&ponderation=egale)-->−75,7<!--/--> % à <!--chiffre:mesure(ecart_passe?scenario=2)-->−78,9<!--/--> % : la pondération donne aux
   carrières du privé, que le compte salarial seul pénalise davantage encore,
   les deux tiers du poids. C'était un plancher pour les uns, un plafond pour
   l'autre.

   Trois réserves subsistent, et elles sont de nature différente de la
   précédente. **Un effectif de caisse n'est pas un effectif de personnes** :
   un polypensionné compte dans chacune des siennes, et la somme des caisses
   dépasse d'un tiers la ligne « tous régimes » ; le poids des régimes dont les
   affiliés ont typiquement aussi une carrière au régime général — Ircantec,
   MSA salariés — en est gonflé. **Une caisse réclamée par plusieurs cas types
   se partage également entre eux** : la Cnav est celle des quatre carrières du
   privé, et aucune source ne dit combien de ses retraités ont été cadres ;
   c'est la seule part de convention égalitaire qui subsiste, et elle ne joue
   plus qu'à l'intérieur du salariat privé. **Hors de 2004-2024, la répartition
   du bord est reconduite** : la France de 1960 comptait plus d'exploitants
   agricoles que ces poids ne le disent, et la série tombe au niveau `estimee`
   pour le dire.
3. **Avant 1975, la reconstitution est mince.** La répartition ne commence
   qu'en 1941 : les générations antérieures à 1880 n'ont, dans ce modèle,
   aucune pension, et plusieurs régimes n'existaient pas encore. Les premières
   années reposent sur deux ou trois générations et la moitié des cas types.
   Elles pèsent peu dans le cumul — la dépense de 1959 vaut <!--chiffre:mesure(rapport_depenses?de=1959&a=2024)-->0,5<!--/--> % de celle de
   2024 en euros courants — mais leur rapport ne vaut pas ce que valent ceux
   d'après 1980.

4. **Le rapport ne multiplie plus la réversion, et c'est le volet C.** Il
   décrit les droits DIRECTS et eux seuls : il est le quotient de deux masses
   calculées sur treize cas types, qui n'ont ni conjoint ni survivant, et la
   réversion figure depuis toujours parmi les droits que même l'étalon ne sert
   pas. La base à laquelle on l'appliquait, elle, porte les deux. Un scénario
   notionnel réduisait donc la réversion dans la même proportion que les
   pensions propres, **sans que rien ne l'ait décidé** — et il l'a fait
   jusqu'au 19 septembre 2026.

   La base est désormais ventilée. `part_droits_derives.csv` dit quelle
   fraction de la masse versée est une pension de réversion : <!--chiffre:cellule(data/reference/macro/part_droits_derives.csv:part*100?annee=2010)-->12,4<!--/--> % en 2010,
   <!--chiffre:cellule(data/reference/macro/part_droits_derives.csv:part*100?annee=2024)-->10,4<!--/--> % en 2024, <!--chiffre:cellule(data/reference/macro/part_droits_derives.csv:part*100?annee=2040)-->9,5<!--/--> % en 2040, <!--chiffre:cellule(data/reference/macro/part_droits_derives.csv:part*100?annee=2070)-->5,7<!--/--> % en 2070 — la réversion recule dans la
   projection du COR, les carrières des femmes se rapprochant de celles des
   hommes. Le rapport ne multiplie plus que le reste.

   **Ce que le scénario fait de la réversion est maintenant une décision, et
   elle est écrite : seul le scénario 1 la sert.** Décision du Parti libéral,
   19 septembre 2026, et elle ne fait qu'appliquer à cette ligne la règle des
   trente-huit autres. Les scénarios 2 à 6 retirent tous les avantages non
   contributifs, et l'inventaire du dépôt range la réversion parmi eux depuis
   toujours : « non contributive au sens strict, la cotisation de l'assuré
   ayant déjà été rendue par sa propre pension », et « de très loin la
   PREMIÈRE dépense non contributive du système ». La servir dans un compte
   notionnel était l'exception non écrite, pas la règle ; ces cinq scénarios
   mesurent ce qu'une retraite composée uniquement de part contributive
   représente, et une réversion n'en est pas. C'est le chemin de la Suède, où
   un compte notionnel ne verse qu'à son titulaire. Celui de l'Italie, qui
   partage le capital du défunt, reste calculable sous
   `convention_reversion="servie"`.

   **Les cinq la retirent à tout le monde, et du même jour.** Les scénarios
   RÉTROACTIFS (2, 4, 6) recalculent toutes les pensions depuis 1941 : ils n'en
   servent jamais un euro. Les scénarios PROSPECTIFS (3, 5) sont, par
   construction, le système actuel jusqu'à leur bascule — ils y recopient ses
   pensions, et un test tient l'égalité de leurs courbes à l'euro près —, si
   bien qu'ils y servent sa réversion comme le reste ; à compter de la bascule
   ils ne la servent plus, aux veuves d'avant comme à celles d'après.
   `reforme_en_vigueur` porte ce seul basculement.

   Ce n'est pas le traitement que le modèle réserve aux autres avantages non
   contributifs dans les scénarios prospectifs : un minimum contributif servi à
   qui a liquidé en 2010 lui reste acquis pour toujours, parce que sa pension
   entière est recopiée. La réversion fait exception, et par décision : le
   programme a voulu qu'aucun scénario notionnel n'en verse à compter du jour
   où il s'applique.

   Ce que la décision rend : **+1,19 point de solde moyen 2026-2070 à chacun
   des cinq**, exactement le même chiffre. Ce n'est pas une coïncidence — la
   réversion retirée est une part de la BASE, qui ne dépend d'aucun rapport de
   masses, et les cinq la retirent sur la même fenêtre, celle qui commence à la
   bascule. Le scénario 1 ne bouge pas d'un iota, son
   rapport valant un, et un test l'exige. Le scénario 5 retrouve au passage
   l'équilibre dès la bascule et repasse au-dessus du système actuel, sa
   moyenne restant néanmoins négative.

   **Et la part est contrôlée chez un autre producteur.** Elle est construite à
   partir du classeur du COR, où douze des vingt-deux régimes publient leur
   droit dérivé à part — pour les dix autres, dont la fonction publique d'État
   et la CNRACL, c'est la différence entre la masse de prestations et le droit
   direct. La DREES, elle, ventile ses propres comptes en droit direct
   (`E11-21.1`) et droit dérivé (`E11-22.1`) depuis 2020. Deux enquêtes, deux
   périmètres, deux nomenclatures, cinq années communes : les parts s'écartent
   de **0,06 point au plus**, et de 0,01 point deux fois. C'est le seul
   contrôle externe dont cette série dispose, et il est bon.

   Ce qui reste : la part est très légèrement SURESTIMÉE pour les dix régimes
   sans bloc dédié, la différence prestations moins direct portant aussi un
   petit résidu de prestations qui n'est ni l'un ni l'autre — 0,3 % des
   prestations là où on peut le mesurer. Et hors de 2010-2070, la valeur de
   bord est reconduite au niveau `estimee` : la dépense observée remonte à
   1959, cette ventilation non.

5. **La grille ne monte pas au-delà de 2,5 fois le salaire moyen.** Le plus
   haut des treize cas types est la profession libérale, à 2,5 ; le
   simulateur, lui, accepte jusqu'à dix fois le salaire moyen. Toute règle qui
   ne mord qu'aux hauts revenus est donc INVISIBLE dans l'agrégat, et cela
   vaut dans les deux sens : ni la pension qu'elle ouvre, ni la cotisation
   qu'elle appelle. Le déplafonnement de l'assiette, décidé le 20 septembre
   2026 (action 61), en est la démonstration : il change la pension du
   simulateur de +12 à +14 % au-delà de neuf fois le salaire moyen, et il ne
   déplace ni le coût, ni le solde, ni un coefficient d'équilibre — mesuré à
   l'identique, au centime, sur les quatre systèmes et tout l'horizon. Ce
   n'est pas une propriété du déplafonnement : c'est que personne, dans la
   grille, ne gagne assez pour être concerné. La recette supplémentaire qu'un
   vrai déplafonnement apporterait n'est donc pas chiffrée ici, et la dépense
   supplémentaire non plus.

**Ce qui, en revanche, n'est pas une approximation** : l'égalité des scénarios
3 et 5 avec le système actuel sur toute la période observée. Elle est EXACTE, et
au sens strict — le scénario prospectif recopie la pension du scénario actuel
pour qui a liquidé avant la bascule. La page ne l'écrit pas en dur : elle teste
l'identité des courbes année par année, et les séparerait si la bascule était
avancée avant la dernière année publiée.

## 5 ter. La trajectoire projetée : ce qu'elle suppose, et ce qu'elle vaut

La seconde moitié de la page **Coût** projette les six systèmes de 2025 à 2070.
Rien n'y est certifié, rien ne peut l'être, et le lecteur doit savoir sur quoi
chaque chiffre repose.

**Ce qui n'est pas de nous.** La démographie est celle du scénario central des
projections de population 2026 de l'INSEE : effectifs par âge de 1962 à 2070,
observés jusqu'en 2023. C'est cette source qui fixe l'horizon de la page — 2070
et pas 2080 — et non une préférence du dépôt. L'INSEE publie seize autres
scénarios ; leur écart mesurerait l'incertitude démographique, que cette page ne
montre pas. Les hypothèses macroéconomiques sont celles du COR, déjà décrites
dans `data/reference/macro/hypotheses_projection.yaml`.

**Ce qui est de nous, et qui se discute.** Le PIB projeté suit le rythme nominal
du COR — <!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_reference.pib_nominal*100)-->2,45<!--/--> % par an dans le scénario de référence — **composé avec sa
trajectoire d'emploi**, qui recule de <!--chiffre:mesure(emploi_projete)-->−6<!--/--> % d'ici 2070. C'est la convention que
`hypotheses_projection.yaml` énonce pour tout le dépôt (« le PIB nominal suit la
même convention que la masse salariale »), et c'est la même série que lit
l'indexation des comptes : la page n'a plus de PIB à elle.

Elle en avait un jusqu'au 20 septembre 2026, et c'était le paramètre le plus
discutable de la section : le rythme du COR corrigé par la **population des
20-64 ans**, qui recule de 10 % là où son emploi recule de 6 %. Ce proxy avait
été posé contre une hypothèse d'emploi constant, qui aurait prêté à la France de
2070 douze pour cent d'actifs qu'aucune projection ne lui donne ; l'hypothèse a
disparu le même mois (action 46), le proxy lui a survécu quelques jours, et le
dépôt a porté pendant ce temps TROIS PIB projetés — celui-ci, celui de
l'indexation, et celui qu'implique le compte du COR. Une part de PIB dont le
dénominateur n'est pas celui du reste du dépôt ne se compare à rien. La
substitution rend 1,05 point : la trajectoire 2070 passe de 19,4 à **18,35 %**,
et c'est du dénominateur seul — aucune pension ne bouge.

**Ce que la substitution laisse ouvert.** Le PIB reste UNIQUE PAR ANNÉE, commun
aux six systèmes. C'est ce qui rend les six courbes comparables, et c'est aussi
une hypothèse : la trajectoire d'emploi ne s'applique qu'aux systèmes 2 à 6
(action 46, « un emploi qui bouge sous la réforme, pas sous le droit constant »),
alors que le PIB qu'elle produit sert de dénominateur aux six. Un système qui
déplacerait réellement l'emploi déplacerait son propre dénominateur, et la page
ne sait pas le montrer.

**Ce qui n'est pas modélisé.** Le taux de couverture est supposé constant : le
modèle compte des générations, non des cotisants, et suppose que la même
proportion de chacune perçoit une pension et que la carrière type ne change pas.
Un recul de l'âge effectif de départ, une carrière plus longue ou plus hachée
déplaceraient la trajectoire. Aucune règle de pilotage n'est appliquée non plus :
un système notionnel réel porte un coefficient d'équilibre qui ajusterait toutes
ses pensions par un même facteur — commun, donc sans effet sur les écarts entre
carrières, mais avec effet sur les courbes de cette page. Ce coefficient est
désormais CALCULÉ, section « Le solde, et non le coût » de la même page, à
partir des ressources que le COR publie ; il n'est toujours pas appliqué, et le
§ 5 dit ce que cette distinction coûte.

**Ce que le pas de la grille laisse passer.** Une génération sur cinq est
simulée, et chacune représente les cinq classes d'âge qui l'entourent, décalées
d'un an à deux ans, chacune liquidant sa propre année. Une cohorte qui part
juste avant la bascule est donc représentée par une génération qui part juste
après, et hérite de son traitement : les courbes prospectives s'écartent de la
courbe actuelle d'un à deux dixièmes de pour cent avant même la bascule. Le
résidu est mesuré et un test le borne à un demi-point. Le pas commande le temps
de calcul de la page ; il ne doit pas commander la forme du résultat, et c'est
pourquoi les cinq cohortes ne basculent pas le même jour — sans quoi la
trajectoire avancerait par marches de cinq ans.

**Le contrôle externe, et ce qu'il dit.** Le COR projette la même grandeur avec
un modèle de population complet et une méthode qui n'a rien de commun avec
celle-ci : il trouve <!--chiffre:cellule(data/reference/macro/comptes_retraite.csv:part_pib*100?annee=2024&poste=depenses)-->13,9<!--/--> % du PIB en 2024 et **<!--chiffre:cellule(data/reference/macro/comptes_retraite.csv:part_pib*100?annee=2070&poste=depenses)-->15,3<!--/--> % en 2070** (rapport annuel
de juin 2026, champ « ensemble des régimes légalement obligatoires, y compris
FSV, hors RAFP »). Le dépôt trouve <!--chiffre:mesure(part_pib?scenario=1&annee=2024)-->13,6<!--/--> % et **<!--chiffre:mesure(part_pib?scenario=1&annee=2070)-->18,23<!--/--> %**. Trois dixièmes de point
d'écart au départ — l'affaire du périmètre, la répartition obligatoire des
Comptes de la protection sociale n'étant pas exactement celle du COR — et **trois
points à l'arrivée**.

## 5 quater. Comparaison à la littérature : pourquoi les écarts d'ici sont plus grands

Trois travaux français ont simulé le passage des retraites aux comptes
notionnels, et **aucun ne trouve ce que trouve ce dépôt**. Un lecteur qui les
connaît arrive ici avec une objection d'une ligne — « la CNAV dit <!--chiffre:illustration()-->−7<!--/--> %, vous
dites <!--chiffre:mesure(ecart?exemple=litterature_prive&scenario=2)-->−71<!--/--> % » — et cette page lui doit une réponse chiffrée. La voici.

### Ce que la littérature trouve

| Travail | Ce qu'il simule | Résultat |
|---|---|---|
| **CNAV, Albert & Oliveau, nov. 2009** (modèle PRISME, régime général, euros 2004) | bascule au prorata des générations 1952-1961, taux réel de la CNAV, **droits non contributifs conservés** | masses de prestations **<!--chiffre:illustration()-->−7<!--/--> % en 2050** (hommes <!--chiffre:illustration()-->−10,5<!--/--> %, femmes <!--chiffre:illustration()-->−3,4<!--/--> %) ; besoin de financement 36 Md€ contre 49 Md€ |
| **COR, 7e rapport, janv. 2010** | l'expertise demandée par le Parlement ; pas de chiffrage central | les dispositifs de solidarité valent **« de l'ordre d'un cinquième des retraites tous régimes »** |
| **CEPII, Lettre n° 297, avril 2010** (OLGAMAP, équilibre général) | régime unique, **taux unique ~<!--chiffre:illustration()-->22<!--/--> %**, transition 2015-2030 | besoin de financement **−0,7 pt de PIB** en 2050 ; en variante à actualisation nulle, **−3,2 pts** et système excédentaire |

Et ce que trouve ce dépôt, pour une carrière ascendante au salaire moyen,
entrée à <!--chiffre:mesure(constante?de=mesures_prose&nom=EXEMPLES.litterature_prive.debut)-->22<!--/--> ans, née en 1975, liquidée à <!--chiffre:mesure(constante?de=mesures_prose&nom=EXEMPLES.litterature_prive.depart)-->64<!--/--> ans — à <!--chiffre:mesure(parametre?nom=age_legal_liberal)-->65<!--/--> ans sous la
proposition, qui en fait son âge légal, et c'est ce qui la rapproche du
scénario 4 :

| | Salarié du privé non cadre | Fonctionnaire d'État |
|---|---:|---:|
| 2. Notionnel rétroactif, part salariale | **<!--chiffre:mesure(ecart?exemple=litterature_prive&scenario=2)-->−70,7<!--/--> %** | **<!--chiffre:mesure(ecart?exemple=litterature_etat&scenario=2)-->−77,3<!--/--> %** |
| 3. Notionnel dès 2026, part salariale | <!--chiffre:mesure(ecart?exemple=litterature_prive&scenario=3)-->−24,1<!--/--> % | <!--chiffre:mesure(ecart?exemple=litterature_etat&scenario=3)-->−25,5<!--/--> % |
| 4. Notionnel rétroactif, salariale + patronale | <!--chiffre:mesure(ecart?exemple=litterature_prive&scenario=4)-->−27,5<!--/--> % | **<!--chiffre:mesure(ecart?exemple=litterature_etat&scenario=4)-->−6,1<!--/--> %** |
| 5. Notionnel dès 2026, salariale + patronale | <!--chiffre:mesure(ecart?exemple=litterature_prive&scenario=5)-->−10,2<!--/--> % | <!--chiffre:mesure(ecart?exemple=litterature_etat&scenario=5)-->−14,1<!--/--> % |
| 6. Proposition libérale (<!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> % dès 2026) | <!--chiffre:mesure(ecart?exemple=litterature_prive&scenario=6)-->−30,4<!--/--> % | <!--chiffre:mesure(ecart?exemple=litterature_etat&scenario=6)-->−7,1<!--/--> % |

### Ce n'est pas une contradiction : c'est la somme de quatre choix

L'écart ne vient pas d'un désaccord de calcul. Il vient de quatre décisions
prises ici et pas là-bas, et chacune est chiffrée ou chiffrable.

1. **La rétroactivité.** La CNAV bascule en 1961, le CEPII entre 2015 et 2030,
   et l'un comme l'autre **conservent les droits déjà acquis**. Les scénarios 2
   et 4 recalculent la carrière ENTIÈRE depuis 1941. Le dépôt publie lui-même
   la mesure de ce choix : les scénarios 3 et 5, qui figent les droits acquis
   comme le fait la littérature, ramènent l'écart de <!--chiffre:mesure(ecart?exemple=litterature_prive&scenario=2)-->−70,7<!--/--> % à <!--chiffre:mesure(ecart?exemple=litterature_prive&scenario=3)-->−24,1<!--/--> % pour le
   salarié du privé. **L'essentiel de l'écart est de la rétroactivité, rien
   d'autre.**
2. **Les droits non contributifs.** La CNAV les CONSERVE et les convertit en
   cotisations fictives ; son tableau 2.1 en donne la part dans le capital
   porté au compte — **hommes <!--chiffre:illustration()-->16<!--/--> % en 2020 et <!--chiffre:illustration()-->13<!--/--> % en 2050, femmes <!--chiffre:illustration()-->36<!--/--> % et
   <!--chiffre:illustration()-->31<!--/--> %**. Le COR donne le même ordre de grandeur tous régimes, un cinquième.
   Le §6 de `methodologie.md` les supprime tous. C'est, à soi seul, dix à
   trente-cinq points de capital en moins selon le sexe — et c'est aussi
   pourquoi les écarts de ce dépôt sont, à carrière égale, plus durs pour les
   femmes.
3. **Le périmètre de la cotisation.** Les scénarios 2 et 3 ne portent au compte
   que la part SALARIALE, soit <!--chiffre:mesure(part_salariale_versee?exemple=litterature_prive)-->40<!--/--> % de ce que le scénario 4 y porte pour le salarié
   du privé et <!--chiffre:mesure(part_salariale_versee?exemple=litterature_etat)-->26<!--/--> % pour le fonctionnaire. La littérature raisonne toujours sur la
   cotisation entière. Le scénario 4 est la comparaison honnête, et il donne
   <!--chiffre:mesure(ecart?exemple=litterature_prive&scenario=4)-->−27,5<!--/--> % pour le privé et **<!--chiffre:mesure(ecart?exemple=litterature_etat&scenario=4)-->−6,1<!--/--> %** pour le fonctionnaire.
4. **L'âge de liquidation.** La CNAV suppose les âges de départ INCHANGÉS, et
   observe malgré tout que ses perdants partent à <!--chiffre:illustration()-->60<!--/--> ans et ses gagnants à 65.
   Ici, le diviseur est la seule sanction du départ précoce, et il n'est pas
   amorti par une décote plafonnée.

Additionnés, ces quatre écarts rendent compte de la distance entre <!--chiffre:illustration()-->−7<!--/--> % et
<!--chiffre:mesure(ecart?exemple=litterature_prive&scenario=2)-->−71<!--/--> % sans qu'aucun chiffre ait besoin d'être révisé de part ou d'autre. Ce
qu'il faut en retenir : **les résultats de ce dépôt ne mesurent pas « le
notionnel » en général, mais une version précise et volontairement dure du
notionnel**, et la littérature en mesure une autre, volontairement douce.

### Ce que la comparaison valide

Quatre choix du modèle sont confirmés par des sources qui ne le connaissent
pas :

- **La table de génération** (§5). La CNAV calcule sur des tables
  transversales et écrit ce que cela lui coûte : sa mortalité PRISME étant
  longitudinale, « les pensions sont par conséquent plus élevées que celles qui
  permettraient d'épuiser le capital notionnel ». Le biais que le dépôt évite,
  constaté par un praticien sur son propre calcul.
- **La table unisexe** (§5), qui est aussi celle de la CNAV.
- **L'indexation sur la masse salariale** (§3). La maquette du secrétariat
  général du COR : « l'équilibre à chaque date est assuré par construction […]
  dans la mesure où le taux de revalorisation est ici supposé égal au taux de
  croissance de la masse salariale ». Avec sa limite, en note : ce n'est pas le
  choix suédois, qui indexe sur les salaires et non sur la masse.
- **La part patronale de l'État en 2008.** Le CEPII écrit <!--chiffre:illustration()-->55,7<!--/--> % ; la ligne
  certifiée du dépôt porte <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2008&regime=fonction_publique_etat)-->55,71<!--/--> %. Deux chaînes sans rapport, le même chiffre.

### Ce qu'elle ne valide pas, et qui reste assumé

- **Le bouclage macroéconomique.** Le CEPII calcule en équilibre général : ses
  réformes déplacent le taux d'intérêt, l'emploi et la croissance, qui
  rétroagissent sur l'équilibre des régimes. Le dépôt est comptable de bout en
  bout. Ses trajectoires agrégées (§5 bis, §5 ter) ne doivent donc pas être
  lues comme des projections d'économiste.
- **Le pilotage.** Aucun des trois travaux ne laisse dormir un excédent ; le
  dépôt, lui, calcule un coefficient d'équilibre sans l'appliquer. C'est la
  limite déjà nommée au §5 bis.

### Les limites de la comparaison elle-même

Ces travaux datent de 2009 et 2010, **d'avant les réformes de 2010, 2014 et
2023** : leur contrefactuel « système actuel » n'est plus le droit en vigueur,
leurs montants sont en euros 2004, et la CNAV ne couvre que le régime général.
Ils ne sont donc pas des étalons, et **aucun n'alimente une seule valeur de
`data/reference/`** : ils figurent au manifeste en `controle`, statut réservé
aux sources qui n'apportent aucun chiffre mais en contrôlent un autre. Ce qu'ils
apportent, c'est une méthode déjà éprouvée et des ordres de grandeur — pas des
barèmes.

---

## 6. Reproductibilité

- Aucune dépendance hors PyYAML ; tous les calculs sont déterministes.
- La calibration des tables de mortalité est mémorisée dans
  `data/derive/calibrations_mortalite.json`, que `scripts/construire_donnees.py`
  réécrit et dont `test_le_paquet_est_a_jour` vérifie la fraîcheur. Chaque loi y
  porte l'empreinte de ses entrées — les deux espérances cibles, les quotients
  observés de l'année, les constantes de la méthode — et n'est reprise que si
  elles n'ont pas changé. Ce n'était pas le cas jusqu'au 23 septembre 2026 : la
  mémoire, indexée sur « année|sexe » seulement, avait survécu au remplacement
  des espérances de vie projetées par celles de l'INSEE, et les lois de 2025 à
  2080 restaient calées sur les anciennes cibles — plus d'un an d'espérance de
  vie de trop pour les femmes —, dans le modèle comme sur le site, sans qu'aucun
  test le voie : tous construisaient leur table sans cette mémoire.
- La certification des séries est tracée dans `data/derive/certification.json`,
  que `scripts/verifier_donnees.py --appliquer` COMPLÈTE au lieu de le
  remplacer : les récupérateurs sont indépendants et lents, on ne lance
  presque jamais les dix-sept d'un coup, et réécrire le journal à partir des
  seules sources présentes ce jour-là effaçait la trace de toutes les autres.
  Chaque fiche de série porte `verifiee_le`, le jour où elle a été relue contre
  sa source, valeurs changées ou non ; `dernier_passage_le` n'est que la date
  du dernier `--appliquer`, fût-il partiel. La page Données dit le minimum des
  dates de fiche, seule affirmation que le journal soutient, et un test refuse
  une fiche sans date. Les dates antérieures au 17 septembre 2026 ont été
  rétablies depuis l'historique du dépôt — le dernier commit où chaque fiche a
  changé —, ce qui est une borne basse : une série relue sans changement avant
  cette date n'a laissé aucune trace.
- Les tests couvrent le chargement, la fiabilité, la règle de certification, la
  concordance des tables de mortalité observées avec les espérances publiées, les
  propriétés du moteur et le comportement des scénarios : `python -m pytest`.
  Aucun test n'accède au réseau : les sources sont simulées.
- Les bases JORF et LEGI de la DILA sont interrogeables sans retélécharger
  leurs dumps : `python scripts/fetch/dila_index.py jorf --recuperer` rapatrie
  l'index plein texte publié sur la release `index-dila` du dépôt,
  `--mettre-a-jour` y applique les incréments quotidiens parus depuis, et
  `dila_cherche.py` l'interroge. L'index se reconstruit depuis le dump par
  `dila_index.py jorf` (une demi-heure, dump gardé en cache dans `data/brut/dila/`).
