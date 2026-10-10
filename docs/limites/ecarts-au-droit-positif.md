# Écarts avec le droit positif dans le scénario 1

## Ce qui reste hors du modèle, et pourquoi

Ces lignes ne sont pas des oublis : chacune demande une information que le
modèle n'a pas, ou décrit un dispositif qu'il représenterait faussement.

- **La pension de réversion, en partie.** Elle ne concerne pas l'assuré mais
  son conjoint survivant. Le scénario 1 la liquide pour le conjoint que la
  saisie déclare, au décès de l'assuré après son départ, ou avant lui sur la
  pension qu'il eût obtenue, sans décote (R. 353-6) : au régime général et
  dans les régimes alignés, dans la fonction publique et au RAFP, à la CRPCEN
  et aux IEG, à l'Agirc-Arrco, à l'Ircantec et à la complémentaire des
  indépendants
  (`droit/reversion.py`, le domaine de la réversion), où l'invalidité du
  conjoint, qu'il déclare, lève l'âge requis de l'Agirc-Arrco (le domaine de
  l'invalidité et de l'inaptitude), comme deux enfants de moins de dix-huit ans
  au décès, et deux enfants de moins de vingt et un ans celui de l'Ircantec ;
  depuis 2019, l'Agirc-Arrco reverse en entier la majoration pour enfants du
  défunt (accord du 17 novembre 2017, articles 109 à 111). Le régime général
  sert depuis le 7 octobre 2026 son minimum (D. 353-1), la majoration du
  survivant de trois enfants (R. 353-2) et celle des petites retraites
  (L. 353-6), et calcule la réversion, comme la caisse, sur la pension du
  défunt sans son minimum contributif et, depuis le 9 octobre, d'avant le
  maximum des pensions, sous le maximum de la réversion, la surcote en sus ;
  le même jour, il compte les ressources du ménage du survivant qui déclare
  vivre en couple, marié, pacsé ou en concubinage, sous un plafond 1,6 fois
  plus haut (D. 353-1-1), et abat de <!--chiffre:valeur(data/reference/regles/reversion.yaml:versions.id=minimum_2026.contenu.parametres.abattement_activite*100)-->30<!--/--> % ses revenus d'activité à
  cinquante-cinq ans (R. 353-1), comme la complémentaire des indépendants,
  sous son plafond. Depuis le même jour, la réversion de chaque régime se
  partage avec les précédents conjoints que la saisie déclare, deux au plus,
  au prorata des mariages en mois (L. 353-3, R. 353-4), avec les seuls non
  remariés là où le texte le dit, et s'éteint au mois qui suit l'union
  nouvelle du survivant dans les régimes qui la retirent (L. 46 du code des
  pensions, Agirc-Arrco, Ircantec, IEG, RAFP). Toujours le 9 octobre, le droit
  d'avant 2004 : l'âge de soixante-cinq ans, soixante pour l'inapte, d'avant
  1973 ; la réversion qui complète la retraite personnelle du survivant avant
  juillet 1974, puis s'y cumule dans la limite de D. 355-1, ces retraites
  sorties de ses ressources, à sa date d'effet ou au jour où sa propre
  retraite, qu'il date, la suit ; les majorations forfaitaires de décembre 1982
  et de janvier 1995, à leur date, et celles de la pension du défunt parti avant
  1975, que sa réversion suit ; et, depuis 1988, la majoration forfaitaire pour
  enfant à charge du survivant sans retraite (L. 353-5), jusqu'au mois qui suit
  l'âge limite du dernier enfant, ou sa propre retraite. Restent dehors
  l'étudiant et l'apprenti à charge jusqu'à vingt ans, la révision de la
  réversion quand le ménage, ses ressources ou ses ayants droit changent, ou que
  sa retraite, attribuée depuis juillet 2004, la recalcule, le
  complément de la fonction publique,
  le droit que recouvre le survivant quand sa nouvelle union cesse, les
  pensions d'orphelin — à
  l'Agirc-Arrco, la moitié des droits du parent pour l'orphelin de père et de
  mère de moins de vingt et un ans, ou de vingt-cinq à charge (articles 114 et
  115 de l'accord de 2017) ; au RAFP, aux IEG et à la CRPCEN, un dixième par
  orphelin —, la réversion des complémentaires des artisans et des commerçants
  pour un décès d'avant leur fusion, et celle des autres régimes, dont la ligne
  le dit ; les approximations de chaque fiche sont déclarées. Le formulaire demande le
  conjoint dans un bloc facultatif, et la page montre sa réversion pour un
  décès supposé juste après le départ, ou cette année pour qui est déjà parti :
  personne ne déclare la date du sien. La dépense de tous les ménages, elle, se
  lit (page Coût).
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
- **Les petites pensions versées en capital : servies, en partie.** Le régime
  général — depuis 2016, à qui avait une retraite prenant effet avant (loi du
  20 janvier 2014) —, l'Arrco et l'Agirc puis l'Agirc-Arrco, et l'Ircantec
  remplacent la pension sous leur seuil par un capital, dont la pension garde la
  rente qu'il remplace (fiches `versement_forfaitaire_unique`, `versement_unique_agirc_arrco`
  et `versement_unique_ircantec`, toutes trois approchées). Restent dehors les
  accords de l'Arrco et de l'Agirc d'avant 2004, les tables de coefficients de
  2019 et de 2022, la réversion versée en capital, et les versements
  forfaitaires des régimes alignés et spéciaux ; le capital reste au journal
  une composante annuelle.
- **La troisième condition de la liquidation unique des régimes alignés.** La
  LURA elle-même est servie depuis le 22 septembre 2026 — voir plus bas —, et
  ses deux premières conditions sont opposées : la génération, la date d'effet
  au mois près. La troisième ne l'est pas : la loi écarte la LURA de qui avait
  DÉJÀ obtenu, avant le 1er juillet 2017, une retraite de même nature dans
  l'un des trois régimes. Les régimes alignés d'une carrière du dépôt ouvrent
  au même âge et liquident à la même date, si bien qu'elle ne peut pas porter
  ce cas. De même, le revenu annuel moyen de la LURA
  additionne les salaires et revenus d'une MÊME année civile avant de les
  écrêter au plafond : une carrière du dépôt n'exerce qu'un métier à la fois,
  et la somme n'a jamais lieu.
- **Bonifications de service.** Bonifications de dépaysement, de campagne
  militaire, pour services aériens ou sous-marins, des douaniers de la branche
  surveillance et des contrôleurs aériens, de la moitié du temps des égoutiers.
  La bonification POUR ENFANTS, elle, est servie : elle demande le nombre
  d'enfants et, à qui la connaît, la naissance de chacun. Celles des policiers,
  des surveillants pénitentiaires, des sapeurs-pompiers professionnels et le
  cinquième des militaires le sont aussi, et la majoration de durée des
  hospitaliers actifs, parce qu'un statut porte chacun de ces emplois ; la
  bonification des militaires ne compte que les années servies sous les deux
  statuts militaires, sans le service national. Les autres supposent de connaître le
  CORPS d'appartenance et le détail des services, que la saisie ne demande
  pas.
- **Les primes soumises à retenue.** L'indemnité de sujétions spéciales des
  policiers et l'indemnité de feu des sapeurs-pompiers professionnels majorent le
  traitement que leur pension liquide ; la prime spéciale de sujétion des
  aides-soignants ouvre un supplément de pension ; toutes trois paient la retenue,
  avec leurs retenues supplémentaires, parce qu'un statut porte chacun de ces
  emplois. Le taux de l'indemnité des policiers est celui des gardiens de la paix
  et des brigadiers. La jouissance de la majoration et du supplément, que la loi
  diffère jusqu'à l'âge de la catégorie active, court dès la date d'effet ;
  l'ancien sapeur-pompier n'a pas sa majoration. Ne sont pas portées la prime de
  sujétions spéciales des surveillants pénitentiaires, l'indemnité des gendarmes,
  ni la nouvelle bonification indiciaire, faute de statut ou de saisie.
- **Le temps partiel.** Il compte à temps plein dans la durée d'assurance, et
  seulement à sa quotité dans les services qui liquident une pension de la
  fonction publique — sauf le temps partiel thérapeutique, le temps partiel de
  droit pour un enfant né depuis 2004 et la surcotisation, bornée à quatre
  trimestres. La saisie ne demande la quotité que d'une retraite progressive
  (ci-dessous), dont les années la portent ; un temps partiel plus ancien
  compte ici à temps plein, et un fonctionnaire qui a travaillé à temps partiel
  sans surcotiser reçoit la pension d'un temps plein.
- **Rachats, surcotisation.**
  Le modèle liquide chaque régime une fois, à sa date (« Les départs
  échelonnés », ci-dessous), sur la carrière saisie, la retraite progressive
  mise à part : il ne rachète pas d'années d'études et ne surcotise pas. Les
  barèmes sont lus et rangés au registre de veille (`rachats_et_versements`) —
  dont celui du rachat d'études de la fonction publique, refait au premier
  janvier 2026, que la calculette de l'ENSAP n'applique pas encore.
- **Le cumul emploi-retraite : calculé, sur une activité déclarée.** Depuis le
  30 septembre 2026, l'activité exercée après le départ — sa date, sa fin, son
  statut, son revenu, l'employeur, le dernier ou un autre — se déclare au
  formulaire, dans le dépliant « Retraite progressive et cumul
  emploi-retraite », ou par l'adresse (`emploi_retraite`), et le modèle dit, mois par
  mois, ce que chaque pension en garde, selon le droit du mois, la date de la
  pension et celle de la première pension de base : le cumul libre avant 1983,
  la rupture avec le dernier employeur jusqu'en 2003, le plafond du dernier
  salaire de 2004, le cumul intégral au taux plein depuis 2009, la suspension
  au-delà du plafond, puis, pour la première pension de 2015 et les activités
  d'après mars 2017, la réduction du dépassement ; le délai de six mois chez le
  dernier employeur ; le seuil des artisans, des commerçants et des libéraux ;
  le tiers de la pension du fonctionnaire ; le plafond de l'Agirc-Arrco. Pour
  la première pension de 2027, la pension est réduite de tout le revenu avant
  l'âge légal ; de l'âge légal au taux plein automatique, le seuil qu'un décret
  doit fixer n'a pas paru, et la pension est servie entière. La page le dit, et
  le montant du système 1 reste celui de la pension entière. Chaque régime ne
  réduit que ses pensions, pour l'activité qui relève de lui : le salarié
  devenu artisan garde sa pension du régime général entière. Ce que l'activité
  ouvre de droits se dit aussi mois par mois : rien depuis la première pension
  de 2015, ni depuis 2023, sauf, en cumul intégral, une nouvelle pension au taux
  plein, que le modèle calcule au régime général et aux salariés agricoles,
  plafonnée à <!--chiffre:valeur(data/reference/regles/seconde_pension.yaml:versions.id=loi_2023.contenu.parametres.plafond_en_pass*100)-->5<!--/--> % du plafond de la sécurité sociale avant les premières
  pensions de 2027, et une seconde retraite de l'Agirc-Arrco sur les points de
  la tranche 1. Pour une première pension d'avant 2015, avant 2023, et toujours
  pour une pension militaire, l'activité ouvre des droits dans les régimes qui
  ne servaient pas de pension : ils se liquident à la fin de l'activité, ou à
  l'âge d'ouverture du régime. Restent dehors : les règles des avocats, des
  exploitants agricoles, de l'outre-mer et des élus, et celles des
  complémentaires autres que l'Agirc-Arrco, dont la pension est servie
  entière ; la nouvelle pension des autres régimes, que la page nomme ;
  l'activité exercée avant qu'un régime du départ ne liquide, à son âge
  d'ouverture, qu'il ne compte pas ; plusieurs activités après le départ, la
  saisie n'en déclarant qu'une (fiches
  `cumul_emploi_retraite_et_retraite_progressive`,
  `cumul_emploi_retraite_fonction_publique`, `droits_apres_la_premiere_pension`
  et `seconde_pension`). Les systèmes 2 à 6 n'ont ni cumul ni seconde pension :
  leur pension est celle du départ, entière, et la proposition n'a pas encore
  dit ce qu'elle fait de l'activité après lui.
- **La retraite progressive : servie, sur une quotité déclarée.** Depuis le
  29 septembre 2026, qui la demande — une date, et la quotité du temps
  partiel gardé jusqu'au départ — la voit examinée à sa date comme le droit
  l'examine : l'âge, la durée d'assurance, la quotité, et le régime où il
  travaille, les fonctionnaires, les libéraux et les avocats ne l'ayant que
  depuis le 1er septembre 2023. Sa pension provisoire se liquide dans les
  régimes que nomme L. 351-15, puis, depuis 2023, dans tous les régimes de
  base, et les complémentaires qui les suivent ; la page dit la fraction
  servie jusqu'au départ. Au départ, la pension complète se recalcule, les
  années à temps partiel comprises — réduites de la quotité, et comptées à leur
  durée réelle dans les services de la fonction publique, dont le traitement
  se lit à temps plein —, sans descendre sous la pension provisoire
  revalorisée, sauf au fonctionnaire ; avant le décret du 8 juin 2006, elle
  était la pension provisoire. Restent dehors : les changements de quotité et
  la suspension, la baisse de revenus qui fait la fraction d'un non-salarié,
  les décrets propres des régimes spéciaux et les règles propres des
  complémentaires. Elle se déclare au formulaire, dans le même dépliant que
  le cumul, ou par l'adresse (fiche `retraite_progressive`). Les systèmes 2
  à 6 n'en servent pas de fraction : le temps partiel y réduit seulement la
  cotisation, et la proposition n'a pas encore dit si elle l'ouvre.
- **Les départs échelonnés : servis, sur une date présumée ou dite.** Depuis le 29
  septembre 2026, chaque régime liquide à sa date, comme le droit le veut :
  le régime qui n'ouvre pas encore sa pension au départ attend son âge — le
  régime général de l'aide-soignante partie de l'hôpital à cinquante-sept
  ans —, la pension militaire est servie dès la sortie de l'armée, le RAFP
  attend l'âge légal. Chaque départ voit servies les pensions des précédents,
  sur lesquelles son minimum contributif s'écrête. La date à laquelle
  l'assuré demande chaque pension est présumée quand il ne la dit pas
  (`depart_de_chaque_regime`) ; depuis le 30 septembre 2026, il la dit, régime
  par régime, au formulaire ou par l'adresse (`demande_<régime>`) : une date
  plus tardive remplace la présumée — pour éviter une décote qui tient à
  l'âge, toucher une surcote accordée à l'âge seul —, une plus précoce ne
  l'avance pas, et la page dit pourquoi. Qui demande une pension avant son
  départ — l'agent d'un régime spécial parti tôt — se représente en déclarant
  son départ à cette date, et l'activité qui suit comme une activité après le
  départ. Une complémentaire des salariés n'est pas anticipée seule, sous son
  abattement ; le minimum contributif n'est pas révisé quand une pension
  française commence après lui (R. 173-8), seulement quand c'est une pension
  étrangère. Les montants du
  système 1 sont ceux du départ déclaré, la pension déjà servie y étant menée
  par sa revalorisation, celle qui ne commence qu'après ramenée par les prix
  (fiche `liquidation_regime_par_regime`). Les systèmes 2 à 6 liquident leur
  compte au départ déclaré, quelle que soit la date dite de chaque pension.
- **Les carrières hors de France : servies, sur des périodes déclarées.** Depuis
  le 1er octobre 2026, les périodes passées dans un État que lie à la France un
  accord — les règlements européens, l'accord avec le Royaume-Uni, une
  convention bilatérale —, dans une organisation internationale, ou à
  l'étranger avant le 1er avril 1983, comptent pour le taux, l'ouverture des
  droits, la surcote et la carrière longue de chaque régime que l'accord
  coordonne, jamais pour la durée qui proratise (`droit/etranger.py`) ; celles
  d'un seul accord à la fois, avec les États tiers qu'une convention fait
  compter, comme la caisse les totalise, selon la dernière liste lue à la date
  d'effet. Les calculs de Léna et de Jahan que le CLEISS publie se rejouent
  (`tests/temoins/exemples_officiels.yaml`), hors le prorata de son exemple
  franco-japonais, rapporté à la durée de trois États quand l'accord n'en
  totalise que deux. Quand l'accord compare, chaque régime qui porte le minimum
  contributif sert la plus élevée de la pension nationale et de la pension
  proratisée, chacune portée à son minimum, le salaire annuel moyen de la
  seconde pris, de 2004 à juin 2022 et depuis hors de la liquidation unique, sur
  des années réduites au prorata des régimes étrangers équivalents ;
  l'écrêtement de ce minimum compte les pensions étrangères déclarées, et se
  révise quand l'une commence après le départ. L'ASPA, comme la garantie
  vieillesse de la proposition qui la remplace, compte ces pensions dans ses
  ressources, et n'est servie qu'à qui réside en France plus de six mois par an,
  plus de neuf depuis septembre 2023. La pension que sert l'autre État n'est pas
  calculée : seul son montant déclaré entre dans les ressources et
  l'écrêtement. Restent dehors le minimum garanti des fonctionnaires, que le
  modèle ne proratise pas quand leurs périodes européennes l'ouvrent ; la
  subsidiarité du minimum, présumée remplie ; la tolérance de cent soixante
  jours de la caisse ; le calcul des conventions d'avant l'entrée des États dans
  l'Union, dont seules les dates sont lues. Le formulaire demande la carrière
  hors de France dans un bloc facultatif.
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
- **Les minima des exploitants agricoles, en partie.** La pension majorée de
  référence est servie depuis le 7 octobre 2026 aux pensions de non-salarié
  agricole qui prennent effet depuis 2009, au taux plein, au prorata de la
  durée agricole, écrêtée au plafond de toutes les pensions ; le complément
  différentiel de la complémentaire agricole, aux pensions qui prennent effet
  depuis 2015, à qui compte <!--chiffre:valeur(data/reference/regles/complement_differentiel_rco.yaml:versions.id=complement_de_2026.contenu.parametres.seuil_chef)-->70<!--/--> trimestres de chef d'exploitation. Restent
  dehors : la pension majorée que la loi de 2008 a accordée aux pensions déjà
  liquidées, et les plans de revalorisation de 1994 à 2002 ; le montant réduit
  des conjoints et des aides familiaux, que le modèle ne distingue pas du chef
  d'exploitation ; la réversion, que le plafond ne compte pas. Le SMIC net
  agricole qui fixe le complément n'est publié par la MSA que pour 2021, 2023
  et depuis 2024 : les autres années sont estimées. Le relèvement de septembre
  2023 est servi : le taux plein ouvre les points gratuits et le complément aux
  pensions déjà liquidées sans la durée requise, celles prises depuis 2003 pour
  les uns, depuis 2015 pour l'autre (fiche `relevement_des_exploitants_2023`) ;
  la loi les doit depuis 1997, et le complément des pensions déjà liquidées ne
  se recalcule pas ensuite.
- **Coefficients de solidarité et majorants de l'Agirc-Arrco.** Le malus de
  <!--chiffre:illustration()-->10<!--/--> % pendant trois ans (article 98 de l'accord du 17 novembre 2017) ne
  frappe aucune pension prenant effet depuis le 1er décembre 2023, et cesse sur
  les allocations dues depuis le 1er avril 2024 de celles qu'il frappait (accord
  du 5 octobre 2023, article 2). Le bonus de <!--chiffre:illustration()-->10<!--/-->, <!--chiffre:illustration()-->20<!--/--> ou <!--chiffre:illustration()-->30<!--/--> % pendant un an
  (article 99), lui, n'est pas éteint : il ne vaut plus pour les assurés nés
  depuis le 1er septembre 1961 dont la pension de base prend effet depuis le
  1er décembre 2023, mais continue pour ceux qui remplissaient les conditions
  du taux plein avant cette date (avenant n° 17). La page « Conditions
  d'ouverture de mes droits » de la fédération écrit <!--chiffre:illustration()-->10<!--/-->, <!--chiffre:illustration()-->15<!--/--> et <!--chiffre:illustration()-->20<!--/--> % : l'accord
  dit 1,10, 1,20 et 1,30. Surtout, leur effet est TEMPORAIRE, quand le modèle
  ne calcule qu'une pension annuelle unique. L'appliquer à titre permanent
  créerait une erreur nouvelle, plus grande que celle qu'il corrigerait.
- **Pénibilité ; le handicap, l'invalidité et l'inaptitude en partie.** La
  pénibilité est une autre porte du départ anticipé, qui demande des
  informations professionnelles que le modèle ne collecte pas : un assuré qui
  en relèverait est ici déclaré « non ouvert » alors que le droit l'ouvrirait,
  et subit une décote dont le droit le dispenserait. Le handicap se déclare
  depuis le 5 octobre 2026, par le mois depuis lequel l'incapacité permanente
  atteint <!--chiffre:valeur(data/reference/regles/retraite_anticipee_handicap.yaml:versions.id=generations_2026.contenu.parametres.taux_incapacite)-->50<!--/--> % : le départ anticipé des assurés handicapés s'ouvre dès
  cinquante-cinq ans à qui a cotisé depuis la durée que D. 351-1-5 exige, au
  taux plein, la pension majorée, l'Agirc-Arrco, l'Ircantec et la
  complémentaire des indépendants sans coefficient ; sans cette durée,
  l'incapacité fait partir au taux plein à soixante-deux ans, et le
  fonctionnaire handicapé n'a jamais de décote. Restent dehors les départs
  d'avant 2015, quand le taux exigé était de <!--chiffre:valeur(data/reference/regles/retraite_anticipee_handicap.yaml:versions.id=travailleurs_handicapes_2011.contenu.parametres.taux_incapacite)-->80<!--/--> %, que la saisie n'établit pas ;
  la reconnaissance de la qualité de travailleur handicapé, qui compte pour les
  périodes d'avant 2016 ; la commission qui valide des périodes sans
  justificatif ; une incapacité interrompue ; les régimes que la fiche
  `retraite_anticipee_handicap` ne nomme pas — non-salariés agricoles,
  professions libérales, avocats, cultes, régimes spéciaux — ; la majoration de
  qui part à l'âge légal sans l'avoir demandée, que la Cnav compare à une
  retraite anticipée fictive ; et la réversion, que la Cnav calcule sur la
  pension non majorée. L'inaptitude, la pension d'invalidité et la radiation pour
  invalidité d'un fonctionnaire se déclarent : l'inapte et l'ex-invalide ont le
  taux plein au régime général et dans les régimes alignés, à l'âge que la loi
  leur ouvre, et l'ASPA au même âge ; la pension de vieillesse remplace d'office
  la pension d'invalidité ; le fonctionnaire radié liquide à sa radiation, sans
  décote, à ses planchers et avec sa rente viagère. Restent dehors le plancher
  de l'allocation aux vieux travailleurs salariés, sans effet sur le montant tant
  que l'ASPA est servie ; l'inaptitude des régimes que la fiche
  `inaptitude_au_travail` ne nomme pas ; les réputés inaptes qui ne se déclarent
  pas (allocation aux adultes handicapés, carte d'invalidité) ; le militaire
  réformé ; la majoration pour tierce personne. Les autres taux pleins de
  L. 351-8 se déclarent aussi : l'ancien déporté ou interné, la mère de famille
  ouvrière, le travailleur manuel d'avant 1983, l'ancien combattant ou
  prisonnier de guerre selon ses mois de captivité et de services ont le taux
  plein sans la durée requise, au régime général et chez les salariés
  agricoles, aux artisans et aux commerçants pour le premier et le dernier, et
  leurs complémentaires sans coefficient (fiches `taux_plein_*`). Restent dehors
  l'ASPA dès l'âge de la catégorie, les évadés et les rapatriés pour maladie,
  la carte de patriote résistant, que la saisie ne distingue pas, et la date où
  chaque régime aligné a reçu chaque règle. La proposition n'en fait pas
  exception, le propriétaire l'a décidé : le compte de l'inapte, de
  l'ex-invalide et du fonctionnaire radié se liquide à l'âge de tous, leur
  dernière année prolongée jusque-là — l'invalidité, qui ne cotise pas, ou
  l'emploi de l'inapte qui travaillait encore (README).
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
- **La date d'effet suit l'anniversaire, et le jour se présume.** La pension
  prend effet le premier jour du mois qui suit celui où l'âge est atteint, ou
  le jour même pour qui est né un 1er (R. 351-37 ; L. 90 du code des
  pensions), et le modèle la date ainsi depuis le 28 septembre 2026 (fiche
  `date_effet_mois_suivant`) : la borne de la carrière longue des nés en
  décembre 1965, fixée à <!--chiffre:illustration()-->60<!--/--> ans et 8 mois pour que la pension prenne effet
  le 1er septembre 2026, y tombe désormais. Qui ne dit pas son jour — une
  adresse d'avant le calendrier, les cas types, la page Coût — est présumé né
  le <!--chiffre:valeur(data/reference/vocabulaire/valeurs.yaml:listes.presomptions.valeurs.jour_de_naissance.valeur)-->15<!--/-->, ce qui est juste vingt-neuf fois sur trente environ, et la
  population ne tire pas ce jour au sort (§ 5.6 de l'architecture). Un cas
  type né en janvier part donc au 1er février, et l'année de son départ compte
  un mois, que le pas annuel du moteur traite parfois comme une année : le
  traitement de référence de la fonction publique se lit sur la ligne de
  cette année-là, une ligne d'un mois reçoit le minimum annuel de points de la
  RCO, et la fenêtre de la surcote parentale perd un trimestre quand elle
  chevauche une année de départ qui ne compte pas un nombre entier de
  trimestres civils. Ces effets valaient déjà pour tout départ hors de
  janvier ; l'action 134 de la feuille de route les reprend. Un relevé qui
  s'arrête à l'année d'avant, lui, n'en souffre plus : le site lui ajoute les
  mois qui le séparent du départ (§ 5, « Les carrières réelles »).
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
  trimestres, puis un de plus au 1er janvier 2025 et au 1er janvier 2027. Le
  parent de trois enfants qui avait quinze ans de services avant 2012 part à
  tout âge depuis le 8 octobre 2026 (fiche
  `depart_anticipe_parents_trois_enfants`), à la durée de l'année de ses
  conditions s'il garde l'ancien calcul, à celle de la génération qui a
  soixante ans l'année de ses soixante ans sinon ; mais le modèle présume de
  la mère seule l'interruption d'activité qu'il exige pour chaque enfant, et
  n'en sert rien au père ni au militaire. Reste dehors le fonctionnaire CIVIL
  non classé et handicapé qui liquide avant soixante ans : le modèle sert son
  départ depuis le 5 octobre 2026, mais sur la durée de sa génération.
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
- **Naissance des enfants.** Le formulaire la demande à qui veut la dire, à
  l'année ou au mois, dans l'ordre des enfants ; celle qu'il ne dit pas est
  présumée aux trente ans de la mère, l'âge moyen des mères à l'accouchement
  (la présomption `naissance_des_enfants`, que la chronologie pose et que le
  moteur lit, enfant par enfant). La présomption place l'enfant avant ou après
  ce qui change ses droits : la bascule des quatre aux deux trimestres de la
  fonction publique tombe ainsi sur les générations nées à partir de 1974,
  quand chaque naissance déclarée la place à sa date. Le modèle ne peut pas
  non plus savoir si les
  parents ont attribué au père les quatre trimestres d'éducation ouverts en
  2010, ni si un père fonctionnaire a interrompu son activité les deux mois
  qu'exige la bonification depuis 2003 : dans les deux cas le modèle retient
  l'attribution par défaut, celle de la mère. Une naissance déclarée fait aussi
  l'enfant à charge de la complémentaire : à qui part avec un enfant de moins de
  dix-huit ans, l'Arrco depuis 1999, l'Agirc depuis 2012 et l'Agirc-Arrco
  servent cinq pour cent par enfant au lieu de la majoration pour enfants nés ou
  élevés quand c'est plus, jusqu'à ses dix-huit ans (fiche
  `majoration_enfants_a_charge_agirc_arrco`) ; l'enfant de dix-huit à vingt-cinq
  ans qui étudie, est apprenti ou cherche un emploi, et l'enfant invalide, n'y
  sont pas à charge, et la majoration des enfants nés ou élevés à laquelle elle
  se compare garde le coefficient d'anticipation que la caisse ne lui applique
  pas.
- **Les trimestres des enfants dans les régimes spéciaux.** La SNCF, la RATP,
  les IEG et la CRPCEN ont leur fiche, lue article par article
  (`enfants_sncf`, `enfants_ratp`, `enfants_ieg`, `enfants_crpcen`). À la
  SNCF, deux trimestres de durée par enfant né après le recrutement, aucun aux
  services, et rien avant le 1er juillet 2008 ; à la RATP et aux IEG, une
  année de services par enfant né avant le 1er juillet 2008 — deux pour le
  second d'une fratrie de deux aux IEG —, puis deux trimestres de durée pour
  le premier enfant de la fratrie et quatre pour chacun des suivants ; à la
  CRPCEN, quatre trimestres au taux par enfant né avant le 1er juillet 2006,
  puis deux et quatre trimestres de durée pour l'enfant né pendant
  l'affiliation. Les autres régimes spéciaux suivent encore le calendrier de
  la fonction publique — un an par enfant né avant 2004, deux trimestres
  ensuite —, que le COR dément pour les mines et les marins, à qui il n'en
  connaît aucun (séance du 19 octobre 2023, document n° 2). Les congés pris
  pour élever un enfant, que ces régimes comptent comme services, ne sont pas
  portés : la carrière ne les dit pas ; ni l'âge que la bonification des IEG
  avance pour les parents d'un ou deux enfants.
- **Majorations pour enfants des non-salariés agricoles.** La majoration d'un
  dixième des parents de trois enfants est servie depuis le 1er juillet 1974
  (décret n° 55-753, article 37, puis D. 732-38 du code rural, puis L. 351-12
  depuis 2026) ; aucune période ne la déclarait avant le 5 octobre 2026. La
  MSA sert aussi une majoration de durée d'assurance, mais elle s'y convertit
  en POINTS et non en trimestres, selon une règle qui change au 1er janvier
  2026. Le régime des exploitants étant déjà le plus approché du catalogue, la
  porter ici donnerait un chiffre plus précis d'apparence et pas davantage de
  vérité.
- **Le plafond de la majoration pour enfants des fonctionnaires.** Depuis le
  8 octobre 2026, la pension majorée du code des pensions est bornée au
  traitement qui l'a liquidée (L. 18, V, et les décrets de la CNRACL et du
  FSPOEIE ; fiche `majoration_enfants_plafond_fonction_publique`) : sans
  surcote, le plafond mord à sept enfants au pourcentage que les bonifications
  portent à son maximum, à huit au pourcentage ordinaire. Depuis la décision
  du Conseil d'État du 29 décembre 2020, la surcote reste hors du plafond, et
  le modèle la sert au-delà aux trois régimes, comme la CNRACL ; le service
  des retraites de l'État écrit « sauf en cas d'application d'une surcote »,
  ce qui ne diffère que pour la pension que le plafond borne déjà sans elle.
  Restent trois écarts : le modèle ne retire que la majoration, quand le
  texte réduit pension et majoration « à due proportion » — la pension servie
  est la même, la part de la majoration plus faible — ; il date l'exception de
  la décision, quand le Conseil d'État date la différence de traitement de la
  loi du 9 novembre 2010 ; et la rédaction d'avant 1964, qu'aucun index ne
  porte, n'est pas lue : la pension de ce temps-là n'est pas bornée.
- **Le minimum de pension des IEG.** Depuis le 1er juillet 2008, la CNIEG
  porte au minimum — huit cents, neuf cents ou mille euros de 2008, selon
  quinze, trente ou trente-cinq ans de services, revalorisés depuis — la
  pension de qui a peu de ressources (annexe 3 au statut national, article
  19, II). Mais ce sont celles de l'année qui précède le versement, salaires
  compris l'année du départ, et le modèle, qui calcule la pension du premier
  mois, ne sait pas lesquelles retenir : la fiche `minimum_pension_ieg` la
  dit manquante.
- **Un ménage, un patrimoine, des ressources.** Le minimum vieillesse est servi
  sous le barème d'une personne seule, ou sous celui du couple quand la saisie
  déclare un conjoint — le plafond du couple sur les ressources des deux, la
  moitié de ce qui manque à chacun quand le conjoint a lui aussi soixante-cinq
  ans, tout ce qui manque sinon, au plus le montant d'une personne seule
  (fiche `minimum_vieillesse`). Les ressources de l'assuré ne sont que ses
  pensions, sans revenu d'activité ni patrimoine ; celles du conjoint sont
  celles qu'il déclare, comptées entières, sans l'abattement de ses revenus
  d'activité, et aucune s'il n'en déclare pas (présomption
  `ressources_du_conjoint`) ; le conjoint inapte, ex-invalide ou allocataire de
  l'allocation supplémentaire d'invalidité n'y est pas distingué. Et il est
  servi à tous, alors que la DREES estime le non-recours à la moitié des ayants
  droit. C'est pourquoi il apparaît toujours comme une ligne séparée de la
  cascade, et pourquoi un paramètre le retire d'un seul geste. La majoration
  pour conjoint à charge des pensions du régime général prenant effet avant
  2011 est servie au conjoint que la saisie déclare avec ses ressources, lues
  comme ses pensions, qui s'en retranchent, dès qu'il a soixante-cinq ans
  avant 2011, nominale ensuite (fiche `majoration_conjoint_a_charge`) ; sans
  ressources dites, elle ne l'est pas, ni au conjoint inapte dès soixante ans,
  ni dans les régimes alignés.
