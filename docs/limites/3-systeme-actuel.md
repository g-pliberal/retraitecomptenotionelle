# 3. Le scénario « système actuel » est une approximation

Reproduire exactement le droit positif de tous les régimes depuis 1930 suppose
un moteur législatif complet, du type de ceux de la DREES (TRAJECTOiRE) ou de
l'Institut des politiques publiques (PENSIPP). Écarts connus :

- **régimes en points** — la pension est calculée en points, sur l'historique
  réel des valeurs d'achat et de service (Agirc depuis 1947, Arrco depuis 1949,
  Ircantec depuis 1949), avec conversion des points aux fusions. S'y ajoutent
  depuis peu deux régimes dont le barème n'est pas un prix d'achat mais un
  NOMBRE DE POINTS par tranche d'assiette : le régime de base des professions
  libérales (<!--chiffre:valeur(data/reference/regimes/cnavpl.yaml:periodes.debut=2015;assiette=plafonnee.points_maximum)-->525<!--/--> points au plafond jusqu'en 2024, <!--chiffre:valeur(data/reference/regimes/cnavpl.yaml:periodes.debut=2025.points_maximum)-->557<!--/--> depuis 2025, <!--chiffre:valeur(data/reference/regimes/cnavpl.yaml:periodes.debut=2024;assiette=plafonnee_5_pass.points_maximum)-->25<!--/--> sur la
  seconde tranche) et la complémentaire agricole (<!--chiffre:valeur(data/reference/regimes/msa_rco.yaml:periodes.debut=2003.points_maximum)-->100<!--/--> points pour <!--chiffre:valeur(data/reference/regimes/msa_rco.yaml:periodes.debut=2003.assiette_repere_smic)-->2 028<!--/--> SMIC).
  Le même régime de base en connaît une troisième forme pour ce qui précède
  2004 : <!--chiffre:valeur(data/reference/regimes/cnavpl.yaml:periodes.debut=1949.points_par_trimestre_valide)-->100<!--/--> POINTS PAR TRIMESTRE VALIDÉ, sans égard au montant cotisé. La complémentaire des
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
  articles du code, et recontrôlées à chaque exécution. Ce qui LIQUIDE est lu à la
  date d'effet de la pension : la formule du régime, au jour quand un texte coupe
  l'année — l'ordonnance du 26 mars 1982 au 1er avril 1983, au régime général et
  chez les salariés agricoles, deux arrêtés de la CAVEC et un du RACL au lendemain
  de leur publication —, et, à l'année de liquidation, la valeur de service du
  point, la décote de la fonction publique et le barème du minimum garanti, comme
  leurs articles l'écrivent. Reste approchée la montée en charge propre à chaque
  régime spécial ;
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
  <!--chiffre:valeur(data/reference/regimes/cnavpl.yaml:periodes.debut=2024;assiette=plafonnee.surcote_par_trimestre*100)-->1,25<!--/--> % aux liquidations de 2024 et non aux trimestres accomplis depuis
  septembre 2023, la MSA ramène à <!--chiffre:valeur(data/reference/regimes/msa_non_salaries.yaml:periodes.debut=2004.surcote_par_trimestre*100)-->0,75<!--/--> % l'escalier de <!--chiffre:illustration()-->3<!--/-->, <!--chiffre:illustration()-->4<!--/--> et <!--chiffre:illustration()-->5<!--/--> % d'avant
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
  droit ouvre la liquidation demandée ; l'inaptitude, l'invalidité et le
  handicap aussi, au régime général, dans les régimes alignés et dans la
  fonction publique, à qui les déclare. La pénibilité ne l'est pas : elle
  demande des informations professionnelles que le modèle ne collecte pas ;
- **polypensionnés** — chaque régime liquide sur ses seules années, à sa
  date, et la durée acquise dans chacun est comptée séparément ; mais un
  régime et celui qui lui succède ne sont pas deux régimes, et liquident
  ensemble (voir « Les régimes alignés » ci-dessous). La liquidation unique des régimes alignés
  DISTINCTS (LURA) et sa proratisation croisée du salaire annuel moyen sont
  servies depuis le 22 septembre 2026 ; seule en reste dehors sa troisième
  condition, la retraite de même nature déjà obtenue avant le 1er juillet
  2017 (voir « Ce qui reste hors du modèle »).
- **régimes spéciaux et régime général** — l'assuré qui a relevé du régime
  général et d'un régime spécial que nomme D. 173-1 (la Banque de France,
  les clercs de notaire, la Comédie-Française, les industries électriques et
  gazières, les marins, les mines, l'Opéra, la RATP, la SNCF…) a droit, pour
  ses périodes du régime spécial, aux « avantages dont [il] aurai[t]
  bénéficié sous le régime général » (D. 173-2) : la caisse calcule cette
  fraction selon ses règles, et le régime spécial ne peut servir moins. Le
  modèle liquide chaque régime sur ses seules règles, sans cette garantie
  (base de législation de la Cnav, exposés « Fraction de retraite pour le
  régime spécial »). Il ne sert pas non plus la validation, par un régime
  spécial, des services de non-titulaire de l'agent titularisé tardivement :
  à la demande de l'employeur, avant la retraite, la caisse annule les
  cotisations vieillesse que le régime général a reçues pour ces périodes et
  les reverse au régime spécial, qui les compte en services, avec les
  trimestres de maladie et de maternité de ces années, et ceux du chômage
  quand il valide le chômage (D. 173-13 et D. 173-19 ; exposé « Annulation au
  profit d'un régime spécial », circulaire Cnav 2020/3) : le modèle laisse ces
  années au régime général et à la complémentaire du non-titulaire. Ni, la
  pension du régime général liquidée, le rachat que le régime spécial demande
  des périodes qu'il valide aussi (D. 173-14) : la caisse lui verse la part
  de la pension qui leur répond, multipliée par un coefficient qui dépend de
  l'âge, et ne sert plus que le reste (exposés « Rachat de retraite »). Et
  l'activité accessoire de l'agent d'un régime spécial d'avant le 19 juillet
  2015, qui ne lui ouvrait aucun droit au régime général, lui en ouvre (fiche
  `un_statut_par_annee`).
- **assiettes forfaitaires des salariés** — le modèle porte au compte le
  salaire que la saisie déclare, aux taux de droit commun, faute d'un statut
  qui distingue ceux que la caisse traite autrement, et dont la base de
  législation de la Cnav publie les barèmes : l'apprenti avant 2014, cotisant
  sur une assiette forfaitaire que la fiche `apprentissage` attend ; le
  vendeur à domicile, sur un salaire forfaitaire trimestriel ; l'employé de
  maison, sur le Smic horaire de chaque heure de 1987 à 2012 et sur des
  forfaits avant ; l'artiste du spectacle, à des taux réduits, et sur un
  salaire forfaitaire par jour s'il est occasionnel ou acteur de complément ;
  le journaliste, à des taux réduits depuis 1964, et sur les sept dixièmes de
  son salaire brut quand un accord collectif prévoit la déduction pour frais
  professionnels. Les mêmes barèmes en portent d'autres : des assiettes
  forfaitaires pour le personnel hôtelier rémunéré au pourboire, les
  concierges et employés d'immeuble de 1951 à 1983, les assistants maternels
  avant 1991, les dockers, les personnels des centres de vacances, les
  formateurs occasionnels, le stagiaire aide familial étranger et le stagiaire
  de la formation professionnelle continue, dont la fiche
  `stages_formation_professionnelle` lit l'assiette dans la saisie, et les
  collaborateurs occasionnels du service public de 2000 à 2008 ; des taux
  réduits pour les professions médicales à temps partiel, les médecins depuis
  1961, et pour les collaborateurs occasionnels du service public de 2008 à
  2015. Les exposés de la base en décrivent d'autres, sans barème (thème
  « Carrière : cotisations-salaires ») : des salaires forfaitaires pour le
  président-directeur général jusqu'en 1963 et le gérant minoritaire de
  société à responsabilité limitée de 1956 à 1963, au plafond ou à ses trois
  quarts, pour l'écrivain non salarié de 1957 à 1976, le conjoint salarié de
  1951 à 1952, l'ouvrier déménageur de Paris jusqu'en 1959 et des
  Bouches-du-Rhône jusqu'en 1963, le chauffeur de taxi jusqu'en 2017, le
  cadet de golf, par parcours, de 1951 à 2017, l'énoiseur, au kilo de noix,
  de 1985 à 2017, le gérant de cabine téléphonique de 1959 à 1990, les agents
  recenseurs et les enquêteurs jusqu'en 2017, le porteur et le
  vendeur-colporteur de presse depuis 1991, par cent journaux, les
  conférenciers, préposés aux vestiaires et gardiens auxiliaires des musées
  et des monuments, les sportifs et les arbitres depuis 1994, l'animateur
  d'une association de jeunesse ou d'éducation populaire depuis 1985, à
  l'heure de Smic, l'étudiant d'une junior-entreprise depuis 1988, à quatre
  heures de Smic par journée, le travailleur handicapé d'un centre d'aide par
  le travail de 1960 à 2005 ; l'assiette minimale de l'artiste-auteur, en
  heures de Smic depuis 1977, et celle du détenu qui
  travaille, cinquante heures de Smic depuis le contrat d'emploi
  pénitentiaire ; la valeur forfaitaire de la formation et des avantages en
  nature du travailleur qu'aucun salaire en espèces ne paie, et du stagiaire
  en entreprise jusqu'en 2006 — depuis, la gratification minimale du
  stagiaire, exonérée, n'ouvre aucun droit, et seul son excédent est porté au
  compte — ; deux Smic mensuels au compte du salarié dont le travail
  dissimulé est redressé au forfait ; un salaire diminué de trois dixièmes
  pour frais professionnels au voyageur représentant placier, dans une
  limite par employeur.
- **indépendants des DOM** — le modèle exonère de toute cotisation l'artisan,
  le commerçant et le gérant d'un débit de tabac dont la ligne porte un
  département d'outre-mer et dont le revenu de l'année ne dépasse pas le
  montant qu'un décret fixe, deux mille cinq cents francs puis, depuis 2002,
  trois cent quatre-vingt-dix euros (L. 756-3, L. 756-5, D. 756-7, D. 756-6) :
  ni assiette minimale, ni trimestre, ni salaire porté au compte, ni point,
  l'année ne lui ouvrant « aucun droit à retraite », dit la caisse
  (`legislation/exoneration_independants_outre_mer.csv`). Le site la sert :
  sa saisie dit les années travaillées outre-mer, dont chaque ligne du relevé
  et chaque métier prennent le département (action 177, étape 7).
  Pour le reste, il les traite comme ceux de la métropole, aux taux et sur
  l'assiette minimale de la série, que reprennent les barèmes des DOM de la
  caisse : depuis 2007 pour les taux de la retraite de base, depuis 2013 pour
  le RCI, depuis 2018 pour l'assiette minimale, sauf en 2022, où l'édition
  des DOM garde la part du plafond quand le modèle applique, comme la table de
  la métropole et la circulaire Cnav 2022/32, le montant que le décret
  n° 2022-1438 fixe à tous les indépendants. L'abattement que L. 756-4 fait
  sur leur retraite de base, la moitié de la part du revenu sous le plafond
  dans ses rédactions de 2000 à 2016, ne change pas leurs droits : la caisse
  le tient pour une exonération « génératrice de droits », la part exonérée
  ouvrant des droits « à hauteur de ce qu'il a versé », si bien que l'assuré
  qui paie la cotisation appelée voit ses droits validés sur son revenu
  entier (exposé « Validation des périodes de cotisations » et son exemple,
  que `tests/test_outre_mer.py` rejoue). L'assiette minimale moitié moindre
  des tables de 2009 à 2016 est celle de la cotisation appelée : doublée,
  elle redonne celle de la métropole, sauf en 2012, où l'édition des DOM
  la compte encore en heures du Smic quand la métropole passe à une part du
  plafond. Le modèle ne sert pas : les droits de l'assuré qui ne paie pas
  toute la cotisation appelée, validés sur le double de ce qu'il a versé, ni
  l'exonération comptée sur l'encaissé (le second exemple de la caisse), les
  cotisations étant tenues pour versées ; de 2001 à 2016, la cotisation
  calculée « à titre définitif » sur le revenu de l'avant-dernière année ou
  sur des revenus forfaitaires (L. 756-5), sur lequel D. 756-8 calcule la
  pension, quand il porte au compte le revenu de l'année ; avant 2017,
  l'exonération des vingt-quatre premiers mois d'activité du créateur, à qui
  « des droits sont attribués », sauf la part que la caisse fixe la troisième
  année pour l'assuré taxé d'office ; depuis 2017, ses cotisations des deux
  premières années, calculées à titre définitif sur un revenu forfaitaire
  (L. 756-3) et exonérées sous un revenu de cent dix pour cent du plafond
  (L. 756-2, D. 756-4), puis l'abattement de moitié, des trois quarts la
  troisième année, dégressif d'une fois et demie à deux fois et demie le
  plafond, le RCI et l'invalidité-décès exceptés (L. 756-4), dont la caisse ne
  dit pas les droits qu'ils ouvrent, « seules les cotisations versées » en
  ouvrant ; le RCO et le NRCO moindres que les tables portent de 2010 à 2012
  sur leur première tranche (sept, huit puis neuf dixièmes des taux de la
  métropole) ; avant 1986, le décret n° 75-1098, dont l'index du JORF n'a que
  le sommaire, et l'abattement de ses articles 3 et 11 ; depuis 2018,
  l'exonération du libéral non réglementé que L. 631-1 range avec l'artisan,
  et celle de Saint-Pierre-et-Miquelon (D. 756-6). Non mesuré. Le
  micro-entrepreneur, dont la caisse neutralise les taux réduits des DOM pour
  calculer ses droits (circulaires Cnav 2024/23 à 2026/12), est servi comme
  elle le sert.
- **Accre et Acre** — le modèle n'applique aux indépendants aucune exonération
  de début d'activité : il porte au compte leurs cotisations entières.
  L'Accre, puis l'Acre depuis 2019, exonère pourtant leur retraite de base,
  entière sous les trois quarts du plafond et dégressive jusqu'au plafond
  (barème « Plafonds d'exonération des cotisations des travailleurs
  indépendants » et sa table de l'ex-RSI), et réduit le taux global du
  micro-entrepreneur (barème « Cumul micro-entrepreneur / exonération ACRE »).
  La caisse compte, pour valider les trimestres, les cotisations exonérées par
  la prolongation de l'Accre de 2004 à 2012, et calcule depuis 2020 les droits
  du micro-entrepreneur sur la cotisation qu'il aurait due sans réduction
  (circulaire Cnav 2026/12) : le modèle fait de même. Ce qu'elle fait des
  autres exonérations, les pages lues ne le disent pas : non mesuré.
- **assiette provisionnelle des artisans et des commerçants** — le modèle
  porte au compte de chaque année le revenu de cette année, celui de la
  cotisation définitive : depuis 1973, la cotisation provisionnelle est ajustée
  « sur la base des revenus de l'année à laquelle se rapportent ces
  cotisations » (article 9 du décret n° 73-76, D. 633-10 jusqu'en 2008), et le
  revenu annuel moyen se calcule sur les cotisations versées (R. 634-1). Il ne
  sert pas trois exceptions, que la fiche `cotisation_vieillesse_independants`
  déclare. Jusqu'en 1999, la cotisation de la première année civile d'activité
  est définitive sur un revenu forfaitaire égal au tiers du plafond, que
  l'ajustement ne relève jamais et n'abaisse que sur demande de l'assuré dont
  le revenu est moindre (D. 633-6 et D. 633-10, jusqu'au décret n° 2000-834 ;
  L. 131-6 la rend provisionnelle le 30 décembre 1999). Jusqu'en 2007, les
  cotisations des deux dernières années d'une activité qui cesse ne sont pas
  régularisées (D. 633-11) : leur revenu porté au compte reste la base
  provisionnelle, le revenu de l'avant-dernière année, ou celui de l'année
  précédente de 1995 à 2003. L'année du départ, la caisse retient la plus
  petite de la cotisation encaissée à la date d'arrêt du compte et de la
  cotisation provisionnelle appelée, au prorata, et écarte une dette ancienne
  réglée après la date limite (ses exemples « Prise en compte de la date
  d'arrêt du compte ») ; le modèle tient les cotisations pour versées. Mesuré
  sur trois carrières types (feuille de route, action 177, étape 5) : moins
  d'un centième de la retraite de base quand ces années comptent parmi les
  meilleures, rien sinon ; l'année du départ n'est pas mesurée.
- **assiette de la complémentaire des artisans et des commerçants** — le
  modèle sert, depuis le 3 novembre 2026, ce que la fiche
  `assiette_rco_independants` lit au droit : jusqu'aux cotisations de 2008, le
  RCO des artisans et le NRCO des commerçants assis sur le revenu de
  l'avant-dernière année, sans ajustement ; l'artisan qui commence au tiers
  puis à la moitié du plafond, et, depuis le 5 novembre 2026, le commerçant qui
  commence sur dix-huit puis vingt-sept fois la base mensuelle des prestations
  familiales (D. 635-10, L. 131-6, qui n'en fait qu'un plafond que la caisse
  prend pour forfait ; R. 242-16 est la règle des allocations familiales, que
  D. 633-6 étend à la base, non à la complémentaire), forfaits définitifs
  jusqu'aux cotisations de 2008, puis régularisés sur le revenu de l'année de
  2009 à 2011 (D. 635-2, L. 131-6). Pour l'artisan, c'est une lecture, solide et
  non certaine : D. 635-7, en une seule rédaction du 1er janvier 2008 au 1er
  janvier 2012 (LEGIARTI000017869802), dit toujours « Pour les assurés
  commençant l'exercice d'une profession artisanale ou assimilée, la cotisation
  annuelle est assise : 1° Pour l'année ou la fraction d'année de début
  d'exercice, sur un revenu correspondant au tiers du plafond mentionné à
  l'article L. 241-3 ; 2° Pour l'année suivante, sur un revenu correspondant à la
  moitié dudit plafond », sans la dire provisionnelle, comme L. 131-6 le dit du
  forfait du commerçant ; D. 635-2 calcule toute la cotisation « suivant les
  modalités prévues au cinquième alinéa de l'article L. 131-6 », mais sa réserve,
  « Sous réserve des dispositions des articles D. 635-7 et D. 635-10 », est déjà
  dans sa rédaction de 2008, où le forfait est définitif ; aucun texte ni
  document de la caisse lu ne dit le forfait de l'artisan régularisé (fiche
  `assiette_rco_independants`, approximations) ; la cotisation additionnelle de
  1985 à 1996 sans points ; le conjoint collaborateur sur l'assiette de sa
  cotisation de base, sans régularisation (D. 635-10-2) — au forfait, le tiers
  du plafond de l'année ; à l'option, de 2007 à 2012, la fraction du revenu du
  chef de l'avant-dernière année, que le modèle lit sur la ligne du conjoint
  de cette année-là, et, quand elle manque ou est au forfait (ses deux
  premières années, le passage du forfait à l'option), le revenu de l'année.
  Il sert, depuis le 5 novembre 2026, le minimum de la
  cotisation, le revenu minimum du régime de base jusqu'en 2011, puis une part
  du plafond dès quatre-vingt-dix jours d'affiliation jusqu'en 2015, RCI compris
  (D. 635-4, D. 635-2), mais ne l'oppose pas au forfait définitif de celui qui
  commence, que le texte n'y soumet pas jusqu'en 2004 et dont il ne dit rien
  de 2004 à 2008, ni ne garde l'ancien minimum à qui cesse en 2012 (décret
  n° 2012-443, article 10, II). La deuxième année du commerçant qui commence,
  il prend la base mensuelle du 1er octobre de la première, quand le texte se
  lit aussi de celle d'avant le début : moins d'un point du NRCO. Il ne sert
  ni l'acompte sur le revenu estimé, ni l'assiette inférieure accordée sur
  demande motivée. Il n'exonère pas de la complémentaire l'artisan ou le
  commerçant titulaire d'une pension d'invalidité, comme D. 635-2 le fait
  depuis 2013, et n'oppose pas le minimum à l'année cotisée au revenu nul, que
  le texte n'en excepte pas. Il tient pour un début
  d'exercice la reprise après une année sans activité, ce que le texte ne dit
  pas et que R. 242-16 dit des cotisations d'allocations familiales et de base
  de début d'activité, et prend le
  forfait et le revenu de l'avant-dernière année à proportion des mois de
  l'exercice. Non mesuré.
- **rachats et versements** — le modèle ne pratique ni les rachats ni les
  versements pour la retraite (fiche `rachats_et_versements`, pas encore
  modélisée), dont la base de législation de la Cnav publie les barèmes : le
  versement pour la retraite des années d'études et des années incomplètes
  depuis 2004, à taux réduit pour l'assistant maternel et l'apprenti, et,
  depuis la loi n° 2023-270, des mandats d'élu local et des années de
  sportif de haut niveau ; celui des stages d'études en entreprise ; le
  rachat des périodes d'activité hors de France, d'affiliation tardive, de
  détention, de rapatriement, d'assistance bénévole à un proche invalide, de
  perception de l'indemnité de soins aux tuberculeux et de service dans une
  organisation internationale ; ceux du travailleur indépendant — les années
  incomplètes (rachat « Madelin »), le conjoint collaborateur, l'aide
  familial, l'ex-régime social des indépendants, et le professionnel libéral
  qu'aucun régime de base n'affiliait de 1985 à 2017 ; les cotisations
  arriérées que l'assuré verse quand son employeur ne les a pas versées, dont
  celles de l'artiste-auteur depuis 1976 et du vétérinaire sous mandat
  sanitaire avant 1990. Ni l'assurance volontaire vieillesse que l'assuré
  choisit — l'expatrié, la tierce personne d'un proche invalide, le parent
  chargé de famille qu'aucun régime n'assure, le bénéficiaire de l'indemnité
  de soins aux tuberculeux — (`regimes/caisse_francais_etranger.yaml`).
  La saisie n'a pas de quoi les dire, et aucun trimestre ainsi
  acquis n'entre au compte.
- **aidants** — le modèle sert l'assurance vieillesse des parents au foyer
  pendant l'interruption pour enfant (fiche `avpf`), non l'affiliation de
  l'aidant d'un proche handicapé ou en perte d'autonomie, que l'assurance
  vieillesse des aidants porte depuis le 1er septembre 2023 : le bénéficiaire
  de l'allocation journalière de présence parentale ou du congé de proche
  aidant, la personne qui a la charge d'un enfant ou d'un adulte handicapé, le
  travailleur indépendant qui cesse son activité pour l'aider. Un salaire
  porté au compte sur une assiette forfaitaire du Smic, que la base de
  législation de la Cnav publie, et que la saisie n'a pas de quoi dire.
- **élus locaux** — le modèle affilie l'élu local indemnisé à l'Ircantec
  depuis 1973, et au régime général depuis 2013, quand ses indemnités
  dépassent la moitié du plafond (`legislation/affiliations.yaml`). Il ne sert
  pas l'affiliation au régime général, depuis le 1er avril 1992, de l'élu qui
  a cessé toute activité professionnelle pour exercer son mandat et ne relève
  d'aucun autre régime — maires, adjoints des grandes villes, présidents et
  vice-présidents délégués des exécutifs départementaux, régionaux et
  intercommunaux —, quel que soit le montant de ses indemnités, ni l'option
  ouverte depuis le 1er septembre 2023 à l'élu dont les indemnités restent
  sous le seuil (exposé « Elu local », circulaire Cnav 2024/12).
- **Algérie** — le modèle ne sert pas la validation gratuite, au régime
  général, des périodes d'activité salariée en Algérie d'avant le 1er juillet
  1962 (loi n° 64-1330), sur un salaire forfaitaire annuel que la base de
  législation de la Cnav publie de 1938 à 1962 : la fiche
  `totalisation_des_periodes_etrangeres` les renvoie aux périodes assimilées,
  qui ne les portent pas. Ni celle des périodes antérieures à l'affiliation
  obligatoire de la catégorie au régime algérien, que ce régime aurait pu
  valider (loi n° 85-1274, article 4), ni celle des services dans les forces
  supplétives, ni les périodes assimilées que la caisse y reporte — service
  national, guerre, invalidité, rente d'accident du travail d'au moins
  soixante-six pour cent (exposés « Validation gratuite d'activité en
  Algérie »).
- **périodes assimilées** — le modèle valide sans cotisation les années que la
  saisie déclare sans emploi pour un motif — chômage indemnisé, de solidarité
  ou non indemnisé, préretraite du Fonds national de l'emploi, arrêt maladie,
  accident du travail, congé de maternité, invalidité, service militaire —,
  quatre trimestres par année au plus
  (`legislation/periodes_non_travaillees.csv`), le chômage non indemnisé dans
  ses limites (fiche `chomage_non_indemnise`) ; et, comptés au jour, les stages
  de la formation professionnelle continue, l'inscription sur la liste des
  sportifs de haut niveau et le congé supplémentaire de naissance (leurs
  fiches). La caisse compte au jour : un trimestre par cinquante jours de
  chômage, par soixante jours d'indemnités de maladie ou d'accident du
  travail, par quatre-vingt-dix jours de service national, de guerre ou de
  rééducation professionnelle, par trimestre civil de trois mensualités d'une
  pension d'invalidité ou d'une rente d'incapacité permanente des deux tiers
  au moins ; une année entière en vaut quatre ici comme là, une année partagée
  se lit à l'année. Le congé de maternité fait exception : la caisse n'en
  valide que le trimestre de l'accouchement, puis, pour les naissances depuis
  2014, un trimestre par quatre-vingt-dix jours d'indemnités (R. 351-12, 2°),
  quand le modèle donne quatre trimestres à l'année déclarée. Il ne sert pas :
  l'activité partielle depuis mars 2020, un trimestre par deux cent vingt
  heures indemnisées ; l'allocation de préparation à la retraite des anciens
  combattants d'Afrique du Nord ; les périodes de guerre — mobilisation,
  captivité, résistance, déportation, travail obligatoire et les autres
  situations que la base énumère — ; la détention, l'internement ou
  l'assignation à résidence liés aux évènements d'Afrique du Nord, et la
  détention des otages de l'invasion du Koweït ; l'affiliation des rapatriés
  au régime particulier de leur retour ; l'indemnité de soins aux
  tuberculeux, trente-six trimestres au plus ; les situations validées comme
  le chômage — cessation anticipée d'activité, congés de conversion, de
  mobilité et de reclassement, allocation de congé-solidarité d'outre-mer,
  stage d'un programme d'insertion locale, détention provisoire, intempéries
  du bâtiment, inondations de 1955 et 1956 —, l'allocation des travailleurs
  indépendants, et l'Accre d'avant 2007 de qui restait affilié au régime
  général ; la
  validation gratuite des années 2020 et 2021 que la loi n° 2021-1754
  (article 107) donne à l'indépendant, à l'artiste-auteur et au mandataire
  social que la crise sanitaire a privés de revenus ; ni les volontariats
  (`ecarts-au-droit-positif.md`). La saisie n'a pas de quoi les dire. Le
  régime qui valide la période n'est pas celui que désignent les règles de
  compétence de la caisse — premier régime d'affiliation après le service ou
  la guerre, régime spécial d'abord, dernier régime salarié avant le
  chômage — : l'année d'interruption reste au métier qui l'occupe le plus
  (`carriere.py`, `_lignes_du_parcours`), et la saisie ne déclare une période
  sans emploi qu'après un premier métier.
- **majorations de durée d'assurance** — le modèle sert, au régime général et
  dans les régimes alignés, la majoration pour enfants de L. 351-4 dans sa
  rédaction de la date d'effet — depuis avril 2010, quatre trimestres de
  maternité et quatre d'éducation par enfant —, à la mère, bénéficiaire quand
  les parents n'en ont pas désigné d'autre (fiche
  `majoration_duree_assurance_enfants`), et la majoration de qui part après
  l'âge du taux plein sans la durée maximale, par trimestre écoulé depuis cet
  âge (L. 351-6, fiche `majoration_duree_apres_65_ans`). De la première, il ne
  lit pas la durée d'assurance de deux ans que le VII de L. 351-4 demande aux
  parents pour la majoration d'éducation, que la caisse exige de chacun et
  compte sans cette majoration ; ni les quatre années d'éducation que la
  caisse veut accomplies au point de départ de la retraite. Il ne sert pas la
  majoration d'adoption, quatre trimestres par enfant adopté mineur ; celle du
  congé parental d'éducation (L. 351-5), égale à la durée du congé, comptée de
  date à date et arrondie au trimestre supérieur (R. 351-3), que la caisse
  accorde pour un enfant à la place de la majoration pour enfants quand elle
  est plus favorable ; celle de l'enfant handicapé (L. 351-4-1), un trimestre
  par trente mois d'éducation ouvrant droit à l'allocation d'éducation de
  l'enfant handicapé et à son complément, huit au plus, qui s'ajoute aux
  autres ; celle de l'assuré qui assume au foyer familial la charge permanente
  d'un adulte handicapé de sa famille (L. 351-4-2), un trimestre par trente
  mois, huit au plus ; celle du compte professionnel de prévention, un
  trimestre par dix points ; ni celles des sapeurs-pompiers volontaires et des
  élus locaux (`ecarts-au-droit-positif.md`). La saisie n'a de quoi dire ni
  l'adoption, ni le congé parental, ni l'allocation, ni la charge de l'adulte,
  ni les points.
- **allocations avant retraite** — le modèle ne sert aucune des allocations
  qui précèdent la retraite : celles de l'assurance chômage et de solidarité,
  l'allocation aux adultes handicapés, le revenu de solidarité active,
  l'allocation des travailleurs de l'amiante, le revenu de remplacement des
  cessations anticipées d'activité, l'avantage temporaire des maîtres du privé
  (fiche `retrep_avantages_temporaires`, pas encore modélisée). Il lit la fin
  de l'indemnisation du chômage, qui borne les trimestres assimilés (fiche
  `fin_indemnisation_chomage`) ; la date d'effet est celle que la saisie
  déclare : il n'oblige pas l'allocataire du revenu de solidarité active à
  demander sa pension à l'âge du taux plein, ou, reconnu inapte, à l'âge de
  L. 351-1-5 (L. 262-10 du code de l'action sociale et des familles), et ne
  tient pas pour inapte le bénéficiaire de l'allocation aux adultes
  handicapés (fiche `inaptitude_au_travail`). Il ne sert pas à l'allocataire
  des travailleurs de l'amiante sa pension à taux plein dès soixante ans s'il
  a la durée requise, et au plus tard à soixante-cinq ans, « par dérogation
  aux dispositions de l'article L. 161-17-2 » (loi n° 98-1194, article 41 ;
  fiche `inaptitude_invalidite_penibilite_amiante`, pas encore modélisée), ni
  les trimestres de l'assurance volontaire à laquelle il est affilié pendant
  l'allocation, que le fonds de l'amiante cotise. Le revenu minimum
  d'insertion et le revenu de solidarité active ne valident aucun trimestre,
  ici comme à la caisse (exposés « Allocations avant retraite »).
- **validation sur présomption** — le modèle tient pour établi ce que la
  saisie déclare, quand la caisse ne valide qu'au vu du relevé de carrière et
  de pièces, et sur présomption ce qu'il ne porte pas : les trimestres de
  salariat, huit au plus pour un même emploi, comptés comme cotisés, et le
  chômage d'avant 1980 dont l'assuré n'a pas de justificatif, huit trimestres
  au plus sur une attestation sur l'honneur (exposés « Périodes validées par
  présomption », circulaire Cnav 2020/25). Le chômage involontaire d'avant
  1980 est assimilé, indemnisé ou non : « des périodes antérieures au 1er
  janvier 1980 durant lesquelles l'assuré était en situation de chômage
  involontaire constaté » (R. 351-12, 4°, b) ; le modèle n'en valide aucun
  trimestre quand la saisie le dit non indemnisé (fiche
  `chomage_non_indemnise`, qui ne lit que le d du 4°).
- **avantages de survivant** — le modèle sert la réversion (fiche
  `reversion`), et aucun des autres avantages que la caisse sert au décès de
  l'assuré : l'allocation de veuvage, temporaire, au conjoint survivant qui
  n'a pas l'âge de la réversion, sous condition de ressources (L. 356-1) ; la
  pension de vieillesse de veuve ou de veuf, qui remplace à cinquante-cinq ans
  la pension d'invalidité de veuve ou de veuf, et dont la caisse ne sert, avec
  la réversion du même conjoint, que le plus élevé des deux ; la pension
  d'orphelin, à l'enfant dont les deux parents sont décédés, disparus ou
  absents depuis le 1er septembre 2023 (L. 358-1). De la réversion, il ne lit
  ni la disparition de l'assuré (L. 353-2), ni l'annulation du mariage, ni les
  épouses simultanées d'un polygame, ni la régularité du séjour du survivant
  étranger (L. 161-18-1) ; il tient pour ressources du survivant ce que la
  saisie déclare, quand la caisse les évalue — les biens, censés rapporter
  trois pour cent de leur valeur vénale, les biens donnés, les ressources
  qu'elle exclut —, et c'est la saisie qui dit au lecteur d'y compter ses
  biens ainsi ; et il ne calcule pas la fraction de réversion que le
  régime général met à la charge d'un régime spécial de D. 173-1 (voir
  « régimes spéciaux et régime général »). Exposés « Avantages liés au décès
  de l'assuré » de la base de législation de la Cnav.
- **allocations du minimum** — le modèle sert l'allocation de solidarité aux
  personnes âgées, différentielle, sous le barème d'une personne seule ou du
  couple, et, avant 2007, les deux étages de l'allocation aux vieux
  travailleurs salariés et de l'allocation supplémentaire (fiches
  `minimum_vieillesse` et `residence_et_minimum_vieillesse` ; « Un ménage, un
  patrimoine, des ressources », `ecarts-au-droit-positif.md`). Il ne sert pas
  l'allocation supplémentaire d'invalidité, qui complète, sous condition de
  ressources, l'avantage viager d'invalidité ou de vieillesse de l'assuré
  invalide qui n'a pas l'âge de l'allocation de solidarité (L. 815-24), et
  prend fin à cet âge, son titulaire étant présumé inapte ; ni, avant 2006,
  les anciennes allocations du minimum autres que les deux étages —
  l'allocation aux mères de famille, l'allocation spéciale, l'allocation
  viagère aux rapatriés, le secours viager. De l'allocation de solidarité, il
  ne lit pas l'âge abaissé à celui de L. 351-1-5 des titulaires d'une retraite
  anticipée pour handicap ou pour carrière longue (L. 351-8, 4° bis et 4° ter,
  et R. 815-1, pour les pensions prenant effet depuis le 1er septembre 2023),
  qu'il ne sert qu'à soixante-cinq ans ; le plafond propre à la veuve de
  guerre (R. 815-26) ; le plafond d'une personne seule des époux séparés de
  corps, ou de fait avec des résidences distinctes ; ce que la caisse retient
  des ressources hors des pensions — les revenus d'activité, abattus depuis
  2015, les avantages en nature, les biens, censés rapporter trois pour cent
  de leur valeur vénale, les biens donnés depuis moins de dix ans — et ce
  qu'elle en exclut ; la subsidiarité, qui veut que l'allocataire et son
  conjoint aient demandé toutes leurs pensions ; l'exclusion de l'allocataire
  de l'aide à la vie familiale et sociale des anciens migrants ; les
  versements exceptionnels de mars 2008, à tous, et de décembre 2009, en
  Guadeloupe et en Martinique ; la récupération
  sur la succession, que la loi n° 2019-1479 a supprimée pour l'allocation
  supplémentaire d'invalidité des assurés décédés depuis 2020. Exposés
  « Allocation du minimum » de la base de législation de la Cnav.
- **complémentaire des artisans et des commerçants** — le modèle sert les
  points cotisés du régime complémentaire obligatoire des artisans depuis
  1979, du nouveau régime complémentaire des commerçants depuis 2004 et du
  régime complémentaire des indépendants depuis 2013, qui reprend les points
  des deux autres, ceux des artisans au coefficient de l'article 8 de son
  règlement (`conversions_points.csv`) ; les points d'invalidité, l'abattement,
  la réversion, le versement unique et le cumul (fiches
  `points_invalidite_independants`, `abattement_rci`, `reversion_rci`,
  `versement_unique_rci`, `cumul_emploi_retraite_complementaire_des_independants`).
  Il ne sert pas les points gratuits de la reconstitution de carrière des
  artisans : seize points par trimestre d'activité artisanale d'avant 1973,
  après une carence de douze trimestres, et, de 1973 à 1978, les trimestres
  validés au régime de base, au quotient des points cotisés depuis 1979, ou à
  seize points à qui n'a rien cotisé ; ni la prise en charge, jusqu'en 2012,
  de la cotisation de l'artisan dispensé pour maladie, sinistre ou service
  national, six, deux et quatre trimestres au plus ; ni les points que le
  commerçant garde du régime des conjoints fermé en 2003 (fiche
  `organic_conjoints_de_commercants`). Il sert les points des artisans cotisés
  avant 1997 à la valeur de service des autres, quand le règlement leur en
  donne une plus basse, que relève, pour les pensions prenant effet depuis
  2008, la moitié seulement de la revalorisation des autres, et le tiers pour
  les points de la reconstitution (articles 49 et 50 de l'arrêté du 9 février
  2012). Il ne donne aucun point, de 2013 à juin 2024, à
  l'invalide qui n'avait rien cotisé, quand la caisse lui en sert deux par
  mois depuis 2013 (circulaire RSI 2013/4) ; il établit le quotient des
  points d'invalidité sur les points et les mois d'artisan et de commerçant
  ensemble, quand la caisse ne retient que ceux de l'activité au titre de
  laquelle l'invalidité est reconnue ; il compte, l'année du départ, les mois
  jusqu'à la date d'effet, quand la caisse arrête le compte au dernier jour du
  trimestre civil qui la précède. Exposés « Retraite complémentaire des
  indépendants (RCI) » de la base de législation de la Cnav.
- **anciennes prestations** — avant l'allocation de solidarité, le modèle sert,
  sur les pensions, les deux étages du minimum vieillesse : la majoration de
  L. 814-2, qui porte la pension au montant de l'allocation aux vieux
  travailleurs salariés, et l'allocation supplémentaire (fiche
  `minimum_vieillesse`) ; au régime général, la majoration pour conjoint à
  charge (fiche `majoration_conjoint_a_charge`). Il ne distingue pas de cette
  majoration l'allocation aux vieux travailleurs salariés elle-même, servie
  sans pension sous ses conditions propres — vingt-cinq ans de salariat, ou
  quinze après cinquante ans, dix outre-mer, et l'âge de soixante ans dans un
  département d'outre-mer — ; il ne sert pas l'allocation complémentaire de la
  région parisienne, avant avril 1962, ni l'allocation aux mères de famille, ni
  le secours viager, ni la rente des assurances sociales, le dixième des
  cotisations portées au compte avant 1941, ni celle des retraites ouvrières
  et paysannes, qui s'ajoutent à l'avantage de base. Il ignore les conditions de
  nationalité de ces allocations avant juin 1998, ne connaissant pas la
  nationalité ; l'exclusion de l'allocation supplémentaire du non-salarié
  agricole qui exploitait plus de trois hectares ; le montant de l'allocation
  aux vieux travailleurs salariés proratisé comme la pension qu'une convention
  proratise ; le versement exceptionnel payé avant février 2005 aux titulaires
  de l'allocation supplémentaire au 1er décembre 2004 ; et le maintien, depuis 2006, des anciennes
  allocations à qui ne demande pas l'allocation de solidarité, à qui il sert
  celle-ci. Il refuse la majoration de L. 814-2 à qui réside hors de France,
  quand la caisse la sert sans condition de résidence ; et, avant avril 1993,
  il retranche de l'allocation aux vieux travailleurs salariés toute pension
  étrangère, quand la caisse ne comptait que dans les ressources celle d'un
  État dont la convention n'avait pas de règle de non-cumul. Exposés
  « Anciennes prestations » de la base de législation de la Cnav.
- **régimes intégrés** — cinq régimes fermés, repris par le régime général,
  font servir par lui les droits acquis avant leur intégration : celui des
  agents de change à la caisse des officiers ministériels, jusqu'au
  31 décembre 1988 (loi n° 89-18, article 19 ; décret n° 89-640) ; celui du
  Crédit foncier de France, jusqu'à la même date (décret n° 89-157) ; celui de
  la Compagnie générale des eaux, jusqu'en 1990 (décret n° 91-408) ; celui de
  la chambre de commerce et d'industrie de Roubaix, jusqu'en 1997 (décret
  n° 98-183) ; celui de la chambre de commerce et d'industrie de Paris,
  jusqu'en 2005 (décret n° 2006-1748). La caisse sert à leurs anciens agents
  une rente garantie — la moitié d'un salaire forfaitaire pour cent cinquante
  trimestres validés par le régime intégré, en cent-cinquantièmes au-dessous,
  revalorisée comme les pensions, comparée seule au maximum, et au minimum
  contributif sauf la rente différée de la chambre de Paris, payée avec la
  pension du régime général —, une rente de réversion garantie, au taux et
  aux conditions de la réversion du régime général, ressources comprises
  depuis juillet 2004, sauf pour qui tenait déjà une réversion de la chambre
  de Paris, une retraite de substitution garantie à l'ancien
  invalide, la pension de vieillesse de veuve ou de veuf et l'allocation de
  veuvage. Aucun statut ne porte ces agents, et le modèle ne sert aucune de
  ces rentes (fiches `credit_foncier_transfert_1989`,
  `compagnie_generale_eaux_transfert_1991`, `cci_roubaix_transfert_1998` et
  `cci_paris_transfert_2006`, pas encore modélisées) : les années d'avant
  l'intégration, saisies en salarié du privé, vont au régime général sur leur
  salaire, ce que la loi ne fait que pour l'agent de la chambre de Paris qui
  n'avait pas liquidé sa pension, rétabli dans les droits qu'il aurait eus
  sous le régime général ; et la pension de qui l'avait liquidée avant
  l'intégration n'est pas servie. L'agent de change, que le statut d'officier
  ministériel ne nomme pas, saisi sous ce statut, a au modèle ses années
  d'avant 1989 au régime de base des libéraux, quand la loi les a transférées
  au régime général, en une rente de trente pour cent du salaire plafond moyen
  de 1988 pour cent cinquante trimestres, ou, s'il exerce encore en 1989, au
  régime des industriels et commerçants, qui lui en garantit une calculée de
  même sur son propre plafond. Exposés « Régimes intégrés » de la base de
  législation de la Cnav.
- **règlements européens** — le modèle totalise les périodes accomplies dans
  un État de l'Union, de l'Espace économique européen ou en Suisse, et sert
  la plus élevée de la pension nationale et de la pension proratisée, chacune
  portée à son minimum (fiches `totalisation_des_periodes_etrangeres`,
  `pension_proratisee` et `minimum_contributif_international`) ; sa réversion
  est celle de la pension ainsi servie. Il ne sert pas ce que les règlements
  font des prestations qu'il ne sert pas non plus hors de la coordination —
  l'allocation de veuvage, nationale contre proratisée, la pension de
  vieillesse de veuve ou de veuf, la majoration pour tierce personne — ; ni
  les règles de non-cumul des règlements, qui bornent celles du droit
  français quand l'autre État réduit aussi sa prestation : le dépassement
  divisé par le nombre des prestations réduites, les ressources et le
  plafond proratisés, la réversion et sa majoration ouvertes quand la
  condition de ressources française n'est pas remplie ; ni la majoration
  d'assurance volontaire superposée, que valent, hors de la pension
  théorique, les périodes d'assurance volontaire ou de rachat pour une
  activité à l'étranger qui couvrent une période d'assurance obligatoire
  d'un autre État (voir « rachats et versements ») ; ni l'ordre entre États
  de la majoration forfaitaire pour charge d'enfant. Il liquide une fois, au
  départ en France : ni la pension nationale arrêtée au premier départ et la
  proratisée refaite au départ dans l'autre État, quand les pensions se
  succèdent, ni la seconde proratisée de qui a relevé de trois États sans
  demander toutes ses pensions, ni la révision qu'ouvre, sur demande,
  l'entrée d'un État dans l'Union ou l'application d'un règlement neuf. Il
  compte les périodes étrangères à trois mois le trimestre, et non selon la
  semaine de cinq, six ou sept jours du régime de l'autre État, ni selon les
  règles propres au Portugal et à la Grèce. Il ne connaît pas la
  nationalité, qui ouvre les règlements. Exposés « Règlements européens » de
  la base de législation de la Cnav.
- **accords d'outre-mer** — les régimes de Mayotte, de la
  Nouvelle-Calédonie, de la Polynésie française et de
  Saint-Pierre-et-Miquelon sont des régimes du modèle, dont les trimestres
  comptent dans la durée tous régimes (fiches de régime `cssm_mayotte`,
  `cafat_nouvelle_caledonie`, `cps_polynesie` et
  `cps_saint_pierre_et_miquelon`) : la pension du régime général y est celle
  que sert la coordination, la pension théorique réduite au prorata de ses
  trimestres sur la durée des deux territoires, plafonnée à la durée maximum
  (décrets n° 94-1146, article 7 ; n° 2002-1371, annexe, article 7 ;
  n° 2005-1050, article 12 ; n° 2011-512, article 13), et que la pension
  nationale ne dépasse pas. Il compte ces trimestres à toute date et pour
  tout régime : avant que la coordination commence — en 1966, refondue en
  décembre 2002, pour la Nouvelle-Calédonie, en 1995 pour la Polynésie, en
  août 2005 pour Mayotte, en juin 2011 pour Saint-Pierre-et-Miquelon —, ce
  qui s'appliquait n'étant pas lu ; et pour les régimes des fonctionnaires,
  que les accords de la Polynésie et de Saint-Pierre-et-Miquelon laissent
  hors de la vieillesse, quand le code des pensions compte la durée « dans
  un ou plusieurs autres régimes de retraite de base obligatoires » sans dire
  s'ils en sont. Exposés « Accords d'outre-mer » de la base de législation
  de la Cnav.
- **accords internationaux** — le modèle applique à une période dans un État
  lié à la France par une convention bilatérale l'accord que le tableau
  `legislation/accords_internationaux.yaml` lui donne à la date d'effet,
  selon son mode de calcul (fiches `totalisation_des_periodes_etrangeres`,
  `pension_proratisee` et `minimum_contributif_international`). Il ne sert
  pas ce que les conventions font des prestations qu'il ne sert pas hors
  d'elles — l'allocation de veuvage proratisée, que sept conventions
  ouvrent par l'assurance dans l'autre État, le complément différentiel de
  la pension d'invalidité — ; ni le partage de la réversion entre les
  épouses d'un polygame, ni son paiement à l'institution de l'autre État,
  ni, sous la convention tunisienne de 2003, sa réserve à l'épouse qui la
  première a obtenu les prestations de l'assurance maladie ;
  ni le transfert au régime général des droits acquis en Côte-d'Ivoire, au
  Gabon ou au Mali (« recours au régime unique ») ; ni l'accord des bateliers
  rhénans, que le tableau ne porte pas ; ni la révision, à son entrée en
  vigueur, de la pension liquidée avant une convention ; ni l'accord
  tripartite avec les Pays-Bas et la Pologne (1967-2004), ni la résidence
  au Danemark ou en Norvège comptée pour période d'assurance. Il ne
  distingue pas l'ex-RDA, où les règlements ne s'appliquent que depuis le
  3 octobre 1990. Il ne connaît pas la nationalité, qui ouvre l'accord
  intérimaire européen, et la plupart des conventions. Il compte une période
  dans un État dès qu'elle est déclarée, quand la caisse attend que la
  carrière dans l'ex-Yougoslavie soit attestée pour totaliser, et ne tient
  pour période d'assurance turque que le travail accompli depuis le
  1er avril 1950. Exposés « Accords internationaux » de la base de
  législation de la Cnav, de « Anciens accords » à « États-Unis ».

Un écart de quelques pour cent avec la pension réelle est attendu.

## Ce que dit la confrontation à une seconde implémentation

Le scénario 1 est l'étalon : tous les écarts affichés se mesurent par rapport à
lui, et il n'avait aucune contre-expertise. « Mon estimation retraite », le seul
simulateur officiel qui chiffre une pension entière, exige FranceConnect et le
relevé de carrière réel ; les simulateurs anonymes des caisses ne répondent
qu'une saisie à la fois, dans un budget (§ 3.5 de l'architecture), et leurs
réponses rejoignent les exemples publiés, plus bas. Et relire deux fois le même
code ne prouve rien : une réimplémentation écrite par la même main hérite des
mêmes hypothèses.

**OpenFisca-France-Pension** comble ce trou. Ce n'est pas une source officielle,
c'est un autre MODÈLE — le module « retraites » de l'écosystème OpenFisca — mais
il est écrit par d'autres à partir des mêmes textes.
`scripts/fetch/openfisca_regime_general.py` y calcule dix profils à salaire
nominal constant et fige le relevé dans `tests/temoins/`, que `tests/test_oracle.py`
rejoue sans avoir à installer le paquet.

**Cinq familles de régimes y passent aujourd'hui**, et c'est tout ce
qu'OpenFisca expose : le régime général, la pension civile (État et CNRACL),
l'Arrco d'avant 2019, l'Agirc des cadres et l'Ircantec des agents non
titulaires — <!--chiffre:mesure(profils_oracle)-->146<!--/--> profils en tout. Les régimes alignés — MSA des
salariés agricoles, artisans, commerçants — n'ont chez lui aucun module, et
n'en ont pas besoin : la loi les calcule comme le régime général, et c'est à
l'oracle du régime général qu'ils se confrontent — à une table près : le
revenu annuel moyen des artisans et des commerçants nés de 1935 à 1952,
partis avant 2026, retient moins d'années que le salaire annuel moyen
(`R. 634-1-1`), et le test leur prête la table du régime général pour les
y opposer. Restent hors de portée le
régime unifié Agirc-Arrco, dont son code lève une exception, et tout ce qui
n'est ni salarié ni fonctionnaire : les régimes spéciaux, les libéraux, les
exploitants agricoles, que personne d'autre ne modélise. Les exploitants sont
le seul trou qui porte plus d'un million d'assurés — 1 023 064 retraités de
droit direct en 2024 —, et il ne se comblera pas par cette voie : leur régime
est MIXTE, une retraite forfaitaire plus une proportionnelle en points, sans
équivalent au régime général auquel l'opposer.

Le résultat, sur dix profils — et les régimes alignés le partagent, puisque
leur pension est, à table égale, celle du régime général :

| Grandeur | Accord |
|---|---|
| Durée d'assurance | **exacte** sur les dix |
| Trimestres de décote | **exacts** sur les dix |
| Taux de liquidation | **exact** sur les dix |
| Coefficient de proratisation | **exact** sur les dix |
| Salaire annuel moyen | jusqu'à <!--chiffre:mesure(ecart_openfisca)-->2,52<!--/--> %, **et c'est OpenFisca qui s'écarte de la source** |
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
jusqu'à <!--chiffre:mesure(ecart_openfisca)-->2,52<!--/--> %, toujours dans le même sens — n'est plus le nôtre.

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

- **Avant octobre 2017**, la caisse publie aussi ses colonnes :
  <!--chiffre:distinctes(data/reference/legislation/revalorisation_salaires_anciennes.csv:date_effet)-->88<!--/-->
  dates d'effet, de l'arrêté du 14 mai 1946 à la colonne d'octobre 2015, sur la
  page de ses coefficients d'avant avril 2013 et dans ses barèmes d'avril 2013
  et d'octobre 2015 (`revalorisation_salaires_anciennes.csv`). Le modèle sert à
  toute liquidation de ces années la colonne **en vigueur à sa date d'effet**,
  telle quelle, sans rapport de deux valeurs : avant 1952, l'arrêté fixait un
  coefficient par année de perception, et jusqu'en 1993 la revalorisation de
  janvier ne touchait pas encore le salaire de l'année tout juste close —
  aucune colonne ne s'y reconstruit depuis une autre. Restent les salaires
  d'avant 1947, que ces colonnes ne portent qu'en cotisations, revalorisés par
  le rapport de la colonne récente la plus proche ; et deux cellules de la
  colonne de juillet 1990, qui s'écartent de la chaîne des autres, gardées
  telles que la caisse les publie.
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

**Au-delà des carrières simples, une famille de profils à la fois**
(`tests/test_oracle_familles.py`, action 153 de la feuille de route). Chaque
famille a sa convention de traduction, écrite dans le script qui la fige et
portée par son témoin avec les entrées qu'OpenFisca a reçues ; le test la
vérifie avant de comparer. La première, le temps partiel des fonctionnaires et
le départ anticipé des parents de trois enfants, ne trouve rien à corriger chez
nous. Le temps partiel tombe au centime — durée, services, décote, surcote,
traitement à temps plein, minimum garanti sur les services réduits. Au départ
des parents, l'année des conditions réunies, sa décote, la bonification et la
majoration concordent, et les quatre écarts sont les siens : il proratise sur
la durée de la génération et non sur celle de l'année des conditions ; il
ferme le départ, avant juillet 2011, à qui n'atteint pas son âge d'ouverture
avant 2016 ni n'a réuni les conditions avant 2003 ; il ne le sert ensuite qu'à
la raison « famille », datée du départ, quand la loi du 9 novembre 2010 le
garde à l'année des soixante ans ; et il compte les quinze ans de services
sur les services réduits par la quotité, que L. 5 compte en entier. Il ne lit
pas l'interruption d'activité pour chaque enfant, que le dépôt présume de la
mère seule : son père de trois enfants part, le nôtre non. La deuxième, les
enfants des fonctionnaires (`tests/test_oracle_enfants.py`), ne trouve rien à
corriger non plus : la bonification d'un an par enfant né avant 2004 jusqu'à
sept enfants, la majoration de pension de cinq points par enfant au-delà du
troisième et son plafond au traitement, la majoration de durée des enfants
nés depuis 2004 à l'État concordent. Ses trois écarts tiennent à ce qu'il ne
lit pas : le recrutement, si bien qu'il accorde la bonification à l'enfant né
avant lui d'une pension de 2009, que R. 13 réservait alors à l'interruption
prise dans un congé du statut, et la majoration de durée à la femme qui a
accouché avant ; et la liquidation de la CNRACL, que sa majoration de durée
confond avec celle de l'État, de sorte qu'il ne la sert jamais. Comme lui, le
dépôt ne lit pas le b bis de L. 12, la bonification de la femme qui a
accouché pendant ses études. La troisième, la catégorie active
(`tests/test_oracle_categorie_active.py`), a trouvé une erreur chez nous : le
dépôt exigeait dix-sept ans de services actifs de toute génération née depuis
juillet 1956, quand le décret n° 2011-2103 relève les quinze ans selon l'année
où ils sont atteints ; qui les avait achevés avant 2011 sans aller jusqu'à
dix-sept se voyait refuser l'âge anticipé. Corrigée le 14 octobre 2026, elle
laisse l'âge anticipé, la limite d'âge et la décote concorder. Ses deux écarts
sont les siens : il proratise la pension des actifs sur la durée de leur
génération, et non sur celle de l'année où le droit s'ouvre (L. 13, III) ; il
ne connaît pas la super-active, ni ses années, ni l'âge minoré, ni la
bonification du cinquième. La quatrième, la carrière longue des
fonctionnaires (`tests/test_oracle_carriere_longue_fonction_publique.py`), a
trouvé deux erreurs chez nous : le dépôt ouvrait aux fonctionnaires les trois
portes du régime général dès 2004, quand la fonction publique ne les a eues
qu'une à une, de 2005 à 2008, et sur la durée de l'année d'ouverture, quand
la loi la fixait à cent soixante trimestres et le supplément de la porte.
Corrigées le 16 octobre 2026, elles laissent les deux ouvrir et refuser les
mêmes départs. Ses deux écarts sont les siens : il lit l'entrée avant vingt
ans à la fin de l'année des seize, et l'entrée précoce de la CNRACL dans les
services de l'État, si bien qu'il ne sert la carrière longue ni à qui a
commencé à dix-huit ans ni à aucun fonctionnaire territorial ou hospitalier.
La cinquième, les minima (`tests/test_oracle_minima.py`), n'a rien trouvé
chez nous : le barème du minimum garanti, rapporté à sa référence, et le
minimum contributif concordent au centime. Ses quatre écarts sont les siens :
son minimum garanti de la CNRACL lit les services de l'État et vaut zéro ; il
sert sous quinze ans la règle de 2011 à qui avait gardé l'ancienne ; il ne
minore pas, de 2011 à 2015, l'âge qui ouvre le minimum sans la durée ; il
proratise le minimum contributif sans la durée corrigée après l'âge du taux
plein. La sixième, les points enfants de l'Arrco et de l'Agirc et la
minoration qui les frappe (`tests/test_oracle_points_enfants_arrco.py`), a
trouvé une erreur chez nous : le plafond de la majoration pour enfants nés ou
élevés était, de 2012 à 2018, celui du régime unifié, commun aux deux régimes
et double de celui de chacun ; il est désormais de <!--chiffre:partout(data/reference/regimes/arrco.yaml:periodes.*.plafond_majoration_enfants)-->1 000<!--/--> € par régime au point
du 1er janvier 2012, dans les deux moteurs. Les taux par période
d'acquisition, les enfants à charge et le coefficient d'anticipation
concordent ; son écart est le sien : de 2012 à 2018, il minore du coefficient
la majoration pour enfants à charge, qui porte sur les droits bruts. La
septième, le salaire annuel moyen sur des salaires qui varient
(`tests/test_oracle_salaire_annuel_moyen.py`), n'a rien trouvé chez nous :
rejouée sous les coefficients et le plafond du dépôt, sa règle rend notre
salaire au centime — les meilleures années, l'écrêtement de chacune,
l'exclusion depuis 2004 des années qui n'achètent pas un trimestre, le nombre
par génération. Ses écarts sont les siens : ses coefficients, composés d'une
série annuelle, s'écartent des colonnes de la Cnav dès avant 2022 ; il écrête
au plafond de janvier une année où le plafond a changé, 1960 et 1961 ; il
divise par le nombre d'années avant juillet 1995, quand la somme se rapportait
aux trimestres ; et il compte un trimestre de décote de trop à qui part le
jour anniversaire d'un âge entier, son âge en mois tiré d'un mois moyen.
La huitième et dernière, les périodes assimilées
(`tests/test_oracle_periodes_assimilees.py`), n'a rien trouvé chez nous :
OpenFisca ne compte pas les trimestres d'un stage, d'une inscription de
sportif ou d'un contrat d'apprentissage, mais, ceux du dépôt reçus, il les
mène à la même durée, quatre par année au plus, au même taux et à la même
proratisation, et les tient comme nous hors de la durée cotisée, de la
surcote et de la majoration du minimum contributif. Son écart est le sien :
il ne compte aucune surcote l'année de l'âge légal quand le trimestre qui
suit cet âge commence après le 1er janvier.

**TRAJECTOiRE**, le modèle de la DREES dont un module calcule les cas types du
COR, s'exécute à part, sa licence à réciprocité (EUPL) le tenant hors du dépôt :
`scripts/fetch/trajectoire.py` fige ses sorties, sur les cas types du COR et sur
les carrières de Destinie 2, et `tests/test_trajectoire.py` y confronte le
scénario 1 sans R. Il confirme les durées, la carrière longue et le minimum
contributif ; refaits sur ses propres paramètres, ses écarts de salaire annuel
moyen ne sont que sa chaîne de coefficients, et ses écarts de points la
convention des taux d'acquisition, que le propriétaire tranchera. Il a montré au
dépôt une erreur, corrigée le 5 octobre 2026 (action 138, étape 20) : la valeur
de service de l'Agirc-Arrco était celle du 31 décembre de l'année de la
liquidation, quand la caisse sert celle du jour du départ, et la retraite
complémentaire d'un départ antérieur au relèvement de l'année en sortait trop
haute du montant de ce relèvement. Les deux moteurs servent désormais **la
valeur du jour**, datée de 1947 à 2025 dans `regimes/valeurs_service_datees.csv`
(fiche `agirc_arrco_valeur_service`). Restent lues au 31 décembre les valeurs
des régimes en points que ce fichier ne date pas : l'Ircantec, qui relevait la
sienne au 1er avril à partir de 2009 avant de suivre en 2018 la date de
l'article L. 161-23-1, et les autres, à relire. La bonification du cinquième
des super-actifs et la majoration de durée des hospitaliers actifs, qu'il sert,
le dépôt les sert aussi : les durées concordent, et TRAJECTOiRE borne la
bonification à cinq points de taux proratisés, quand la loi la fait entrer aux
services liquidés, sous le pourcentage maximum.

## Ce que disent les exemples publiés par les caisses

OpenFisca est un autre modèle ; les caisses, elles, publient des EXEMPLES —
une carrière de trois lignes dont la réponse est écrite par l'organisme qui
applique la règle. `tests/temoins/exemples_officiels.yaml` en transcrit
<!--chiffre:entrees(tests/temoins/exemples_officiels.yaml:exemples)-->218<!--/-->, chacun avec sa source et sa date de vérification, et
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
| circulaire Cnav 2018-04 | surcote à un, deux et trois taux (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->2,5<!--/--> %, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->4,75<!--/--> %, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->10,25<!--/--> %) ; la réversion d'une pension ramenée au maximum des pensions, la surcote en sus : <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->836,77<!--/--> € par mois en 2012 | **exact**, une fois le barème daté ; au centime pour la réversion, depuis le 9 octobre 2026 |
| fiche F16336 et circulaire carrière Cnav 2017-01, fiche 6.2b | huit trimestres par enfant au régime général — quatre de maternité, quatre d'éducation | **exact** |
| fiche F37311 | bonification de la fonction publique : quatre trimestres par enfant né avant 2004, deux pour ceux nés depuis | **exact** |
| circulaire Cnav 2022-26 | assiette de la majoration pour trois enfants : <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->10<!--/--> % de la retraite telle qu'elle est servie, surcotée, décotée ou pile au taux plein | **exact** |
| ENIM, pages « Le mode de calcul » et « Les conditions d'attribution » | marin : bonification de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->5<!--/--> % dès deux enfants (R. 14), pension d'ancienneté ouverte à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->50<!--/--> ans pour <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->25<!--/--> ans de services et refusée un trimestre plus tôt (R. 2) | **exact** |
| CARCDSF, CARMF et CAVAMAC, pages et document d'exemples des sections libérales | la mère de deux enfants au taux plein dès <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->65<!--/--> ans à la CARCDSF ; le coefficient de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->1,15<!--/--> à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->65<!--/--> ans de la CARMF ; à la CAVAMAC, la décote du régime de base au plus favorable de l'âge et de la durée (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->5<!--/--> %), sa surcote de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->7,5<!--/--> % pour six trimestres, et la décote de la complémentaire par l'âge seul (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->6,25<!--/--> %) | **exact**, une fois les complémentaires minorées par l'âge seul |
| Cour des comptes, « Les retraites des fonctionnaires de l'État », tableau n° 20 | durée requise des emplois classés, génération par génération : super-active <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->166<!--/--> trimestres pour 1965, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->168<!--/--> jusqu'en août 1971, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->169<!--/--> ensuite ; active <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->168<!--/--> pour 1965 et jusqu'en août 1966 | **exact**, une fois la durée lue à l'année d'ouverture du droit |
| Service des retraites de l'État, pages « La décote » et « La surcote » | la même fonctionnaire née en mars 1962, à l'âge légal avec <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->163<!--/--> trimestres sur <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->169<!--/--> : décote de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->7,5<!--/--> % ; à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->64<!--/--> ans avec <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->175<!--/--> : surcote de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->7,5<!--/--> % | **exact**, une fois la pension datée au premier du mois qui suit la cessation, comme la caisse la date |
| Agirc-Arrco, page « La pension de réversion » | la date d'effet de la réversion de huit survivants : le mois qui suit le décès, ou celui qui suit leurs cinquante-cinq ans | **exact** pour cinq, dont le survivant devenu invalide, que l'âge n'arrête pas, depuis le 1er octobre 2026 ; en écart connu pour trois défunts payés par trimestre ou par an, dont la retraite court jusqu'au terme de sa période |
| circulaires Cnav 2024/25, point 6.4, et 2012/27, point 4 | l'ex-invalide né en novembre 1962, dont la retraite commence d'office à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->62<!--/--> ans, le 1er décembre 2024, avant l'âge légal de sa génération ; l'inapte au taux plein avec <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->158<!--/--> trimestres ; l'un et l'autre ne cumulent entièrement qu'à l'âge légal de leur génération avec la durée requise, ou à celui du taux plein automatique | **exact** |
| Service des retraites de l'État, pages « Le minimum garanti » et « Le calcul de la pension » des invalides | le minimum garanti de l'invalidité en quinzièmes, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->7 542,25<!--/--> € par an pour douze ans de services ; la pension portée à la moitié du traitement à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->65<!--/--> % d'invalidité, non à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->55<!--/--> % ; pension et rente ramenées ensemble au traitement | **exact** ; la page partage ce total en comptant le seuil de la rente sur la rente, quand L. 28 le compte sur le traitement, et ce partage ne se compare pas |
| circulaire Cnav 2005/17, § 31 | la réversion réduite au plafond de ressources : <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->530<!--/--> € avant, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->169,06<!--/--> € après, pour <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->1 150<!--/--> € de salaire mensuel | **exact** au centime, la circulaire tronquant le plafond que le modèle arrondit |
| circulaire Cnav 2006/37, § 7 | l'abattement de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->30<!--/--> % des revenus d'activité du survivant, dès le mois qui suit ses cinquante-cinq ans, sur tout le salaire de la période de référence : <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->1 000<!--/--> € par mois retenus au 1er août et au 1er septembre 2006, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->700<!--/--> € au 1er octobre | **exact** |
| Union Retraite, simulateurs anonymes d'info-retraite : carrière longue et réversion saisis à la main le 1er octobre 2026, complétés par Claude le 4 octobre 2026 avec l'âge légal | l'âge légal des nés en 1968, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->63<!--/--> ans et <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->9<!--/--> mois, et des nés en 1969 et après, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->64<!--/--> ans, avec <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->172<!--/--> trimestres ; les quatre portes de la carrière longue ; la réversion à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->54<!--/--> % au régime général et à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->60<!--/--> % à l'Agirc-Arrco, l'âge de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->55<!--/--> ans, le mariage de quatre ans de la fonction publique, que l'enfant commun lève à la CNRACL ; la MSA des salariés ; la moitié au RAFP et à l'Ircantec, et à la complémentaire des indépendants le taux de l'Agirc-Arrco ; l'invalidité, qui lève l'âge à l'Agirc-Arrco et non au régime général | **exact**, une fois deux arrondis de la carrière longue corrigés ; en écart connu pour la condition d'âge de l'Agirc-Arrco, que deux enfants à charge lèvent, pour la réversion du RAFP, que le simulateur refuse quand le mariage ne remplit pas la condition de la pension civile, qu'aucun texte du RAFP ne pose, et pour le plafond de ressources, où c'est le simulateur qui se trompe : il n'a pas revalorisé ses seuils depuis 2024, et refuse ce que D. 353-1-1 accorde |
| ERAFP, simulateur de prestation : dix saisies par Claude le 4 octobre 2026 | le coefficient de majoration du RAFP au mois — <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->1,03<!--/--> à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->62<!--/--> ans et 9 mois, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->1,10<!--/--> à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->64<!--/--> ans et 6 mois — et <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->1,81<!--/--> à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->75<!--/--> ans, comme la délibération du 5 février 2015 ; l'âge légal qui ouvre le droit ; le capital au coefficient de conversion de l'âge, la rente dès <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->5 125<!--/--> points, le capital versé en deux fois de 4 900 à 5 124 | **exact** pour huit ; en écart connu pour deux : le simulateur arrondit au centième le coefficient qu'il interpole, ce qu'aucun texte ne dit, et prête à la génération 1958 l'âge légal de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->64<!--/--> ans |
| ERAFP, prestations-types des rapports annuels 2015 et 2022, page « Calcul et paiement de votre prestation » | le capital de 2015 au barème de conversion de 2005 (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->24,62<!--/--> à soixante-deux ans), celui de 2022 au barème de 2021 (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->27,11<!--/-->) ; la première fraction de quinze mois de rente, puis de quatre depuis avril 2024 ; le capital versé en une fois quand la retraite de base précède le RAFP de plus de quinze mois ; les rentes de soixante-deux, soixante-quatre et soixante-sept ans | **exact** |
| Union Retraite, simulateur du départ anticipé des assurés handicapés : vingt-quatre saisies par Claude le 4 octobre 2026 ; circulaire Cnav 2026-18 | la durée cotisée en situation de handicap, de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->60<!--/--> à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->100<!--/--> trimestres sous la durée requise, de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->55<!--/--> à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->59<!--/--> ans, et la durée validée de la double condition de 2015 ; les trimestres retranchés en plus aux nés avant 1973, puis la durée d'avant 2023 de ces générations ; le départ ouvert à l'âge saisi et refusé un trimestre plus tôt ; la majoration de la pension, le tiers du rapport arrondi au centième, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->0,28<!--/--> et <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->0,29<!--/-->, écrêtée à la pension entière | **exact** |
| Ircantec, pages « Les conditions de départ à la retraite » et « Les points acquis par cotisations », et sa base documentaire, « Mode de calcul » | la minoration d'un départ à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->63<!--/--> ans avec <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->157<!--/--> trimestres sur <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->171<!--/--> : <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->85,50<!--/--> %, par la durée, plus avantageuse que l'âge — le premier exemple publié de cette seconde table ; les points d'un salaire de 2024, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->494<!--/-->, et de 2019, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->458<!--/--> et <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->298<!--/--> par tranche | **exact**, au point que la caisse arrondit ; en écart connu pour la pension demandée à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->61<!--/--> ans et 9 mois, avant l'âge légal : <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->76,25<!--/--> % chez la caisse, que le modèle n'ouvre qu'avec le régime général |

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
par l'exemple seul. Mais quand les <!--chiffre:entrees(tests/temoins/exemples_officiels.yaml:exemples)-->218<!--/--> tombent justes ensemble, hors
les écarts connus que chacun déclare, sur une douzaine de sources et autant de
règles, c'est le droit que le modèle applique, et non une
lecture qu'il aurait de lui.

## La pension d'aujourd'hui d'un retraité : ce qui est lu, et ce qui est reconstitué

Le simulateur montre à qui est déjà parti la pension qu'il touche cette année,
et non plus celle de son premier mois ramenée par l'indice des prix. Chaque
régime la revalorise par son texte (`src/retraite_notionnelle/revalorisation.py`,
porté dans `moteur/js/revalorisation.js`). L'écart n'est pas un détail : le
salarié non cadre du cas type, parti en janvier 2012, touche en 2026
<!--chiffre:mesure(aujourd_hui?generation=1950&niveau=0.8)-->−2,5<!--/--> % de
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
part par part, le régime qui la porte, et celle des enfants à charge de la
complémentaire cesse à leurs dix-huit ans ; la majoration pour conjoint à
charge, qui ne se revalorise pas, commence aux soixante-cinq ans du conjoint
quand ils tombent avant 2011. Deux contrôles le tiennent : le cas
type, refait à la main coefficient par coefficient
(`tests/test_revalorisation.py`), et les cas types du COR, figure 3.14 du
rapport de juin 2026, dont le non-cadre des quatre générations est retrouvé en
2026 à <!--chiffre:tenu(test_le_pouvoir_d_achat_du_non_cadre_du_cor_est_retrouve)-->0,1<!--/-->
point et, pour la génération 1952, année après année à
<!--chiffre:tenu(test_le_non_cadre_de_1952_se_suit_annee_apres_annee)-->0,3<!--/-->
point.

**Ce qui s'y ajoute.** La majoration exceptionnelle des petites pensions, due
depuis le 1<sup>er</sup> septembre 2023 aux pensions de base du régime général,
des indépendants, des salariés agricoles et des cultes prises avant cette date
au taux plein, quand l'assuré a cotisé la durée du décret tous régimes :
proratisée sur la durée cotisée dans le régime, sous un plafond proratisé sur
sa durée validée que la pension du régime ne dépasse pas avec elle, puis sous
celui du minimum contributif, revalorisée ensuite comme la pension (fiche
`majoration_exceptionnelle_2023`, loi n° 2023-270, article 18, V). L'échéancier
l'inscrit au mois où elle est due ; l'ASPA la compte, la réversion ne la lit
pas. Restent approchées la surcote des autres pensions de base, que la
comparaison tous régimes garde, et la révision par la seconde pension de qui
retravaille ou par une pension modifiée après coup.

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
