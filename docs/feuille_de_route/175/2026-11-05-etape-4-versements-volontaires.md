# Étape 4, thème « Carrière : versements volontaires » : les exposés et leurs références

**Reprise, au 5 novembre 2026.** Trois thèmes de l'étape sont rangés : « Retraite
personnelle de base », « Carrière : cotisations-salaires », puis « Carrière : versements
volontaires » — ses 49 exposés, et les 12 fenêtres, 1 liste, 151 références et 5 avis
qu'ils lient (cette note). Suivant, dans l'ordre de l'étape : « Carrière : périodes
assimilées » (25 exposés), sous la convention de la note du premier thème. La base se
relit par `cnav_legislation.py` sans mise en garde, hors de 5 h–6 h UTC. Restent à lire
avec leur thème : les listes d'accords, de périodes de guerre, de l'Union et de l'Espace
économique européens. Aux sessions du modèle : les deux candidats de cette note,
l'activité accessoire d'avant 2015 (`un_statut_par_annee`), l'AVPF du père (`avpf`).

**Le 5 novembre 2026, ce qui est fait.**

- *La mise en garde de l'import de nuit ne tient plus.* La base relue ce jour de 18 h 16 à
  18 h 25 UTC par `python scripts/fetch/cnav_legislation.py` (import de la nuit à 5 h 00 min
  19 s), le récupérateur n'a pas refusé et est sorti sur le code 0 : dans les contenus des
  633 exposés, 324 listes et 397 barèmes, aucun lien ne suit les chemins du site SharePoint
  (`liens_de_l_import` : 0), et `liens` en lit 9 629. Ces chemins étaient l'état passager de
  l'import du 3 novembre (note `2026-11-03-forme-des-liens.md`), et le récupérateur refuse
  depuis de relire une base dans cet état (note `2026-11-03-refus-pendant-l-import-de-nuit.md`,
  `test_une_base_en_plein_import_de_nuit_ne_se_relit_pas`). Le commit qui a porté ce refus
  n'a plus d'identifiant à lui : l'historique de `main`, réécrit, ne le garde que dans son
  commit racine, `43cfa28` (`git log -S liens_de_l_import`). Rien n'a été porté au
  récupérateur. La relecture a mis au registre ce que la base a changé depuis : une
  référence neuve, la circulaire ministérielle 2026/140 du 3 novembre 2026, un avis neuf
  (357), la date de deux exposés et le thème d'une circulaire, tous à lire, hors du thème.
- *La lecture* : les 49 exposés du thème, à la version que le registre date (du 24 octobre
  2025 au 14 octobre 2026, celle que la base sert ce jour), sous-thème par sous-thème —
  assurance volontaire ; cotisations arriérées (4) ; versement pour la retraite (4) ; stage
  d'études en entreprise ; rachats de l'activité hors de France (6), de l'affiliation
  tardive, de l'assistance à un invalide, des rapatriés, du travail pénal des détenus, de
  l'indemnité de soins aux tuberculeux (5 chacun), des organisations internationales (2),
  des fonctionnaires partis sans droit, des travailleurs indépendants (5 : « Madelin »,
  conjoint collaborateur, aide familial, ex-RSI, professions libérales non classées) —,
  chacun confronté aux fiches et aux limites qui portent ses règles : `rachats_et_versements`
  (pas encore modélisée), la caisse des Français de l'étranger, `trimestres_avant_1972`,
  `retablissement_fonction_publique`, `conjoint_collaborateur_independants`,
  `assiette_rco_independants`, `points_avant_1973_independants`. Aucun exemple chiffré
  publié n'y rejoue une règle du modèle.
- *Le rapprochement de l'index* (LEGI à jour au 2 novembre 2026, JORF au 3). Les exposés
  lient les articles de code et les textes officiels à Légifrance, non au registre :
  179 liens, 150 identifiants. 170 se trouvent à l'index par leur identifiant ; 162
  concordent avec leur ancre, 5 ancres vides ou réduites à une virgule (des liens
  imbriqués) avec le texte voisin ; « Décret 2012/598 du 27/04/2012 » mène à D. 173-16
  dans la rédaction que ce décret lui donne (LEGIARTI000025766876) ; un lien vide, sans
  texte voisin, au décret n° 2005-600 ; et « Loi 2003-775 du 21 août 2003 art.29 » (exposé
  « Versement pour la retraite (VPLR) ») mène à LEGITEXT000023023907, la loi n° 2010-1330
  du 9 novembre 2010 : un lien faux de la base. Par le numéro, l'article 29 de la loi
  n° 2003-775 est à l'index JORF (JORFARTI000001072418) : « I. - La section 8 du chapitre
  Ier du titre V du livre III du code de la sécurité sociale est complétée par un article
  L. 351-14-1 », le versement pour la retraite, comme l'exposé le dit. Des 9 absents par
  l'identifiant, 2 se trouvent par le numéro — R. 742-8 (LEGIARTI000006752128 et
  LEGIARTI000031483809) et le décret n° 73-848 du 22 août 1973 (LEGITEXT000006062129,
  « relatif à l'internat en pharmacie », que l'exposé « Demande de rachat » de
  l'affiliation tardive cite pour « les internes en pharmacie ») ; 5 liens, à quatre textes,
  ni par l'un ni par l'autre — la loi n° 84-604, le décret n° 2001-899 (deux fois), le
  décret n° 66-370, servi en fac-similé sans identifiant, et l'article 38 de la loi
  n° 94-126 ; 2 sont hors du champ social de l'index (code civil, article 2224 ; code
  général des impôts, article 156). Les 194 références du registre que lient les exposés
  sont des circulaires (126), des lettres (57), des instructions ministérielles (6), des
  accords (3), un règlement et une réponse ministérielle : aucune n'est à l'index, ni par
  un identifiant, ni par un numéro — les numéros de trois lettres ministérielles (102, 18,
  106) n'y rencontrent que des avenants à des conventions collectives, autres textes.
- *Les sorts*, sous la convention de la note du premier thème : 49 exposés (34 `limite`,
  15 `hors_modele` — les sept demandes, les sept paiements, la déclaration sur l'honneur
  des cotisations arriérées : des procédures, d'un dispositif que le modèle ne pratique
  pas) ; 12 fenêtres (10 `limite`, la fiche d'état civil et le Kbis `hors_modele`) ; la
  liste des professions affiliées tardivement, `limite` ; 151 références, dont 4 que
  seules les fenêtres lient (137 `limite`, 14 `hors_modele` que ne lient que les demandes et
  les paiements), et 35 déjà rangées dont les renvois s'étendent ; 5 avis de mise à jour
  (le versement pour la retraite à coût réduit, en 2015 ; le rachat du volontariat pour la
  solidarité internationale, en 2015 ; les cotisations arriérées des artistes-auteurs, en
  2016 et en 2022 ; le délai de la demande des stages d'études, en 2023), `hors_modele`. Les
  22 barèmes liés étaient déjà rangés. Restent `a_lire`, avec leur thème, la liste des
  accords de sécurité sociale et les trois listes des règlements européens.
- *La limite* « rachats et versements » (`docs/limites/3-systeme-actuel.md`) nomme
  désormais ce que les exposés décrivent et qu'elle taisait : le versement pour la
  retraite des mandats d'élu local et des années de sportif de haut niveau (loi
  n° 2023-270) ; les rachats de l'assistance à un invalide, de l'indemnité de soins aux
  tuberculeux, des organisations internationales et ceux du travailleur indépendant ; les
  cotisations arriérées de l'artiste-auteur et du vétérinaire sous mandat sanitaire ; et
  l'assurance volontaire vieillesse, hors de l'expatriation aussi.

**Ce que la lecture a trouvé, sans écart.** L'exclusion du régime général, de 1930 à
1946, du salarié payé au-delà du plafond d'assujettissement (exposé « Rachat - Affiliation
tardive » : « Certains travailleurs salariés ou assimilés étaient exclus du régime général
entre le 01/07/1930 et le 01/01/1947, en raison de leur salaire supérieur au plafond
d'assujettissement aux assurances sociales ») est ce que `trimestres_avant_1972` sert. Les
rachats, les versements, les cotisations arriérées et l'assurance volontaire, que le
modèle ne pratique pas, sont déclarés. L'exposé du versement pour la retraite et sa
fenêtre « Ce qui change au 01/09/2023 » annoncent une mise à jour qui attend ses
instructions (loi n° 2023-270, articles 10 et 23) : la veille la dira.

**Deux candidats, aux sessions du modèle** (rien n'a été corrigé) :

1. *Les trimestres de l'artisan et du commerçant d'avant 1973.* L'exposé « Demande »
   du versement pour la retraite (version du 3 mars 2026) : « Les années d'activité
   artisanale ou commerciale exercées avant le 01/01/1973 ne sont pas concernées, en
   raison de la validation systématique de 4 trimestres par an, quelle que soit la classe
   de cotisations à laquelle l'assuré a adhéré. » Le modèle les compte au revenu :
   l'artisan et le commerçant ne sont pas des statuts des assurances sociales
   (`donnees/macro.py`, `statuts_assures_sociaux`), et `trimestres_valides`
   (`donnees/macro.py`, lignes 716 à 728, appelé par `carriere.py`, lignes 755 à 763)
   leur rend, de 1949 à 1971, autant de trimestres que le revenu contient de fois le
   salaire validant de l'année, quatre au plus ; aucune assiette minimale ne les relève
   avant 1973 (`legislation/assiette_minimale_independants.csv` commence en 1973). Cas
   posé à la main : l'artisan qui déclare 100 € pour toute l'année 1965 ; le salaire
   validant de 1965 est de 38,112254309 € (`legislation/salaire_validant_trimestre_avant_1972.csv`) ;
   100 ÷ 38,112254309 = 2,62, soit 2 trimestres au modèle, 4 à la caisse. Ce que le texte ne
   tranche pas : la base n'attache à cette phrase aucune référence propre, et l'index LEGI
   ne l'a pas donnée (requêtes `NEAR(janvier 1973 trimestres, 25)` avec les mots des
   artisans et des commerçants, `NEAR(antérieures 1973 trimestres, 20)`, `NEAR(1973
   "quatre trimestres", 25)` : D. 634-2-1 et D. 634-5, sur les trimestres d'après 1972,
   et les règlements des régimes complémentaires). À lire avant la correction :
   les décrets d'application de la loi n° 72-554 et la circulaire Cnav qui l'applique.
2. *Le rétablissement des services hors de France d'avant 1989.* L'exposé « Rachat -
   Fonctionnaires sans droit au régime spécial » (version du 13 août 2026) : « Depuis le
   30/04/2012, tous les services accomplis à l'étranger ou dans une collectivité
   d'outre-mer (ex-TOM) avant le 01/01/1989 peuvent faire l'objet d'un rétablissement dans
   les droits au régime général » ; « Avant le décret 2012/598, les fonctionnaires civils
   de l'État, des collectivités territoriales et hospitalières, les ouvriers de l'État et
   les militaires ayant quitté le régime spécial sans droit à pension, pouvaient racheter
   des cotisations pour les périodes de services à l'étranger ou dans les collectivités
   d'outre-mer effectués avant le 01/01/1989 ». Le modèle rétablit toute ligne du régime,
   sans regarder où le service s'est fait (`droit/coordonner.py`, `_retablir`, lignes 296
   à 307), quelle que soit la date de la pension. Cas posé à la main : l'agent titulaire de
   l'État de 1975 à 1984, en poste à l'étranger de 1975 à 1979, radié en 1985 sans droit
   (dix ans de services, moins de quinze), pension du régime général au 1er janvier 2010 :
   la caisse rétablit 1980 à 1984, 20 trimestres, et 1975 à 1979 ne valent que rachetés ; le
   modèle rétablit les dix années, 40 trimestres, si chaque traitement en valide quatre. Ce
   que le texte ne tranche pas : D. 173-16, rédaction de 1985 (LEGIARTI000006735535), ne
   distingue pas le lieu — « ses droits sont rétablis, en ce qui concerne l'assurance
   vieillesse, dans la situation dont il aurait bénéficié sous le régime général de sécurité
   sociale, si ce régime lui avait été applicable durant la période où il a été soumis à son
   régime de retraites postérieurement au 30 juin 1930 » —, et le décret n° 2012-598
   (JORFTEXT000025757633) ne fait que compléter l'article par le versement complémentaire de
   cotisations (`dila_cherche.py legi --num D173-16 --diff`) : la coupure de 2012 est la
   lecture de la caisse, que l'exposé appuie sur des circulaires non lues ici (Cnav 46/73,
   48/90, lettre du 19 décembre 2008). La session du modèle dira d'abord si la saisie peut dire qu'un service s'est fait
   hors de France.

**Pour le thème suivant**, « Carrière : périodes assimilées » : l'exposé du rachat de
l'indemnité de soins aux tuberculeux dit ses périodes « validées gratuitement dans la
limite de 36 trimestres », règle de son thème, que ni fiche ni limite ne nomme
aujourd'hui. Aucun fichier d'une autre file n'a été changé.
