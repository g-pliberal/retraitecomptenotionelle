# Étape 1, les sources et le périmètre : les grilles de l'État ouvertes et datées, celles des deux autres versants au seul LEGI

**Le 13 octobre 2026 : les grilles de la fonction publique de l'État sont
publiées en licence ouverte, structurées et datées, par le CISIRH — 2 105
grilles et 33 169 lignes d'échelons, chacune avec ses dates et ses textes —,
depuis 1989-1990 pour les enseignants, qui font 46,7 % des fonctionnaires de
l'État, et depuis 2005 à 2011 pour les autres grands corps. Pour les
professeurs des écoles, elles concordent, de 1990 à 2024, avec un second jeu
tiré des textes. La territoriale et l'hospitalière n'ont rien de tel : leurs
grilles ne sont qu'au LEGI, et l'index que le dépôt en tient ne les garde pas,
son filtre ne retenant d'un texte de grille que les articles qui écrivent
« indice brut » au singulier — 144 des 489 textes de grilles de l'État y
manquent, comme les échelles C1 à C3 de la territoriale, où sont 60,8 % de ses
fonctionnaires.
Rien n'est écrit dans le code ni dans les données : l'étape fixe les sources,
le périmètre reste à trancher.**

Demande du propriétaire : « Je lance l'action 158, à faire jusqu'ici :
l'étape 1, les sources et le périmètre, sans une ligne de code. Finis en me
posant les questions de « Ce que le propriétaire tranche ». » En parallèle,
l'action 152 tient `castypes.py`, `cas_types_csp.yaml` et `grille_large.py`,
l'action 147 `cout.py`, une seule session les pages : aucun n'est touché, et ce
qui devrait s'écrire dans les pages est à la fin de cette note.

- *Les corps les plus nombreux.* Fin 2023, 1 504 500 fonctionnaires à l'État
  et 313 400 militaires, 1 422 000 fonctionnaires à la territoriale, 826 600 à
  l'hospitalière (rapport annuel sur l'état de la fonction publique de la
  DGAFP, édition 2025, vue 1, figure 1 ; SIASP).
  - *L'État.* Les six corps enseignants du ministère de l'éducation nationale
    comptent 701 904 titulaires du public en 2023 (DEPP, Panorama statistique
    des personnels de l'enseignement scolaire 2024-2025, figure 7.1 ; SIASP) :
    professeurs des écoles 349 284, certifiés 217 126, de lycée
    professionnel 53 205, agrégés 53 057, d'EPS 27 086, de chaire
    supérieure 2 146. C'est 46,7 % des fonctionnaires de l'État, dont 23,2 %
    pour les seuls professeurs des écoles et 14,4 % pour les certifiés ; l'Insee
    l'écrit autrement : plus d'un fonctionnaire de l'État sur deux exerce une
    profession d'enseignement (Insee Première n° 2065). Les autres grands
    corps — encadrement et application de la police nationale, finances
    publiques, surveillance pénitentiaire, corps administratifs
    interministériels, enseignants-chercheurs — n'ont d'effectifs dans aucune
    source ouverte trouvée. Le rapport sur l'état de la fonction publique et
    les rémunérations annexé au projet de loi de finances a été supprimé par la
    loi de finances pour 2023, comme doublant le rapport annuel de la DGAFP
    (rapport pour avis du Sénat n° 134, 2023-2024, tome V), et ce rapport ne
    compte pas les corps en 2025 ; les jeux de la DGAFP que data.gouv.fr
    montre datent de 2018 et 2019.
  - *La territoriale.* 1 424 441 fonctionnaires au 31 décembre 2023 (DGCL,
    synthèse nationale des rapports sociaux uniques 2023, 2e partie, C ;
    SIASP). Dix cadres d'emplois en font 77,2 % : adjoints techniques
    421 447 (29,6 %), adjoints administratifs 208 008 (14,6 %), agents de
    maîtrise 90 140 (6,3 %), adjoints techniques des établissements
    d'enseignement 72 578 (5,1 %), rédacteurs 68 302 (4,8 %), adjoints
    d'animation 65 656 (4,6 %), attachés 58 597 (4,1 %), techniciens 42 286
    (3,0 %), ATSEM 39 704 (2,8 %), agents sociaux 33 487 (2,4 %). Les cadres
    d'emplois que la circulaire du centre de gestion du Haut-Rhin du
    1er février 2017 range dans les échelles C1 à C3 en font 60,8 %
    (865 422), hors les auxiliaires de puériculture, passés depuis en
    catégorie B (décret n° 2021-1882), et les sapeurs et caporaux, dont la
    circulaire attendait le décret.
  - *L'hospitalière.* Aucune source ouverte trouvée ne compte ses
    fonctionnaires corps par corps. La filière des soins fait 72,3 % du volume
    de travail de ses fonctionnaires (51,0 points d'EQTP sur 70,5 ; Insee
    Première n° 2067, 2023) ; dans les services de soins des 409 établissements
    de plus de 300 agents, 37 % d'infirmiers, puis autant d'aides-soignants que
    d'autres personnels (ATIH, bilan social 2022, en ETP, tous statuts). Les
    corps qui comptent : infirmiers en soins généraux et spécialisés (A),
    aides-soignants et auxiliaires de puériculture (B depuis le 1er octobre
    2021), agents des services hospitaliers qualifiés, puis les corps
    administratifs et techniques de catégorie C.
  - *Les militaires.* Leurs grilles sont des « indices de solde » : décret
    n° 2009-21 du 7 janvier 2009 pour les militaires non officiers, n° 2009-22
    puis n° 2011-388 pour la gendarmerie, d'autres pour les officiers, que le
    décret n° 2017-1362 modifie ensemble. L'index du dépôt les garde bien,
    leurs articles écrivant « indice brut » : quarante versions d'articles pour
    le seul décret n° 2009-21. La statistique publique de la défense publie sur
    data.gouv.fr des séries d'indice de traitement brut des militaires, des
    agrégats et non des grilles.

- *Les textes qui fixent les grilles des corps les plus nombreux.*
  - *Les enseignants.* Jusqu'au 31 août 2010, un arrêté par corps — du 22 août
    1990 pour les professeurs des écoles, du 30 mai 1990 pour les certifiés,
    modifié le 30 mai 1997 —, abrogés ensemble au 1er septembre 2010 par
    l'arrêté du 26 août 2010 ; puis le décret n° 2010-1007 du 26 août 2010,
    modifié par le n° 2012-31 au 1er février 2012 ; le décret n° 2016-1620 du
    29 novembre 2016 au 1er janvier 2017 ; puis le décret n° 2017-789 du
    5 mai 2017, celui du
    protocole PPCR, appliqué au 1er septembre 2017 avec ses marches de 2019 et
    2020, modifié depuis (décrets n° 2017-1678 et 2021-111 ; le Noyau RH y
    rattache aussi le n° 2023-721 du 4 août 2023).
  - *La catégorie C de l'État.* Le Noyau RH rattache les grilles des adjoints
    administratifs à une douzaine de textes, du décret n° 2005-1229 du
    29 septembre 2005,
    qui institue les échelles de rémunération de la catégorie C, au décret
    n° 2021-1835 du 24 décembre 2021, en passant par le décret n° 2008-836 du
    22 août 2008, qui fixe l'échelonnement des corps et emplois communs, et le
    décret n° 2016-580 du 11 mai 2016, qui organise les carrières de la
    catégorie C à partir de 2017.
  - *La catégorie C de la territoriale.* Depuis le 1er janvier 2017, le décret
    n° 2016-596 du 12 mai 2016 (carrières, échelles C1 à C3) et le décret
    n° 2016-604 du même jour, qui fixe ces échelles, avec leurs valeurs de
    2017 à 2020, modifié par le décret n° 2021-1819 du 24 décembre 2021 ; avant
    2017, d'autres échelles, à dater à l'étape 2. La catégorie B : les
    décrets n° 2010-329 du 22 mars 2010 et n° 2016-594 du 12 mai 2016, portant
    dispositions statutaires communes ; le texte de son échelonnement reste à
    identifier.
  - *L'hospitalière.* La catégorie C : le décret n° 2016-636 du 19 mai 2016,
    dont l'article 5 nomme les échelles C1 et C2, le texte qui les fixe restant
    à identifier. Les aides-soignants et
    auxiliaires de puériculture : statut du décret n° 2021-1257 et
    échelonnement du décret n° 2021-1267, tous deux du 29 septembre 2021,
    modifié par le décret n° 2022-1207 du 31 août 2022. Les infirmiers en soins
    généraux et spécialisés : statut du décret n° 2010-1139 du 29 septembre
    2010, échelonnement du décret n° 2021-1262 du 29 septembre 2021 (Ségur de
    la santé), après le décret n° 2016-647 et l'arrêté du 19 mai 2016 pour les
    corps paramédicaux de catégorie A.
  - *Le barème.* L'indice majoré se lit au barème A du décret n° 82-1105,
    modifié notamment par le décret n° 2017-85 du 26 janvier 2017 et le
    n° 2023-519. Le minimum de traitement s'y ajoute : le Noyau RH paie
    l'indice majoré 366 à tout indice brut jusqu'à 367 depuis le 1er janvier
    2024, quand le barème A donne 330 à l'indice brut 347 au 1er juin 2026. Le
    bas de l'échelle C1 est ainsi payé au minimum, que le SMIC rattrape encore
    (question écrite n° 16217 de la 17e législature, sur le SMIC du 1er juin
    2026).

  Les titres de la territoriale et de l'hospitalière ont été lus sur
  Légifrance par ses résultats de recherche, la page refusant le proxy ; leurs
  articles, non.

- *Ce que le LEGI garde, et ce que l'index du dépôt en voit.* Le filtre de
  l'index (`THEMATIQUE`, `scripts/fetch/dila_index.py`) juge chaque document,
  article ou texte, sur son titre et son contenu. Le titre d'un texte de grille
  ne le passe pas (« échelonnement indiciaire »), ses articles seulement quand
  ils écrivent « indice brut » au singulier, quand beaucoup écrivent
  « indices bruts » ou ne nomment pas l'indice. Des 489 textes de grilles que
  le Noyau RH cite (échelonnement, échelles de rémunération, classement
  indiciaire), l'index
  n'en a pas 144, n'en a que les visas pour 157 — le texte sans ses
  articles —, et quelques articles pour 183, sans rien qui dise qu'ils y sont
  tous. Il manque les plus utiles : les échelles C1 à C3 de la territoriale
  (n° 2016-604, 2021-1819), sa catégorie B (n° 2016-594), les aides-soignants
  (n° 2021-1267, 2022-1207) ; le décret n° 82-1105 lui-même n'y est que par
  ses visas. Les plus anciens textes de grilles qu'il connaît datent de 1978 ;
  il en a 71 sur 79 des années 1990, 103 sur 116 des années 2000, 128 sur 191
  des années 2010, 28 sur 85 des années 2020. Les visas disent les dates des
  textes : l'arrêté du 22 août 1990 des professeurs des écoles vit au LEGI du
  7 septembre 1990 au 1er septembre 2010, le décret n° 2008-836 y a quinze
  versions depuis le 25 août 2008. Jusqu'où le LEGI garde les versions des
  articles, là où sont les indices, l'index ne le dit pas : l'étape 2 le
  mesurera, une fois l'index reconstruit sous un filtre élargi — « indices
  bruts », « échelonnement indiciaire », « échelles de rémunération »,
  « classement indiciaire », et les textes de carrière, qui fixent les durées
  d'échelon. La reconstruction part du dump, ce que seul le workflow
  `index-dila.yml` fait (entrée `reconstruire`) : une session ne retélécharge
  pas le dump et ne peut pas publier l'index.

- *Le Noyau RH du CISIRH : les grilles de l'État.*
  - *Où.* Le jeu de data.gouv.fr que le journal de veille du 12 octobre citait
    (édition « Février 2026 ») est archivé depuis le 8 juillet 2026, et ses
    fichiers répondent 404. L'édition vivante est sur data.economie.gouv.fr :
    « Offre de référentiels pour la gestion de la chaîne ressources humaines
    (RH) de l'État (Gestion administrative, Paye et Post-paye) – Juillet
    2026 », licence ouverte 2.0, version 26.00.00 du noyau, mise en ligne le
    7 juillet 2026. L'API Ingres, qui sert les mêmes nomenclatures, n'est
    ouverte qu'au réseau interministériel.
  - *Quoi.* 363 tableaux, en xlsx comme en xml, dont CORPS (971 corps),
    GRADE (4 051 grades, avec leurs codes PCS et NNE), GRILLE_IND (2 105 grilles),
    ECHELON (33 169 lignes), INDICE (la correspondance des indices bruts et
    majorés) et TEXTE (6 001 textes, avec leur NOR). Chaque grille et chaque
    ligne d'échelon a sa date de début et de fin ; chaque échelon, son indice
    brut, ses trois durées — minimale, moyenne et maximale, codées en années et
    mois : les trois rythmes d'avant PPCR, un seul depuis — et l'échelon qui le
    suit ; chaque grille, ses textes, d'origine ou modificatifs. Le même jeu
    porte le recueil des fiches carrière des corps (2026), les guides de
    l'avancement d'échelon et de grade, et le chaînage des corps, qui dit le
    corps d'avant et d'après une fusion. Il couvre l'État, quelques corps
    militaires (médecins des armées) et les maîtres du privé sous contrat, rien
    des deux autres versants.
  - *Jusqu'où.* Les grilles commencent : 94 dans les années 1970, 105 dans les
    années 1980, 304 dans les années 1990, 739 dans les années 2000, 538 dans
    les années 2010, 279 depuis 2020. Pour les grands corps, la grille
    commence avec le corps : septembre 1989 ou 1990 pour les professeurs des
    écoles, les certifiés et les conseillers principaux d'éducation ; 2005 pour
    l'encadrement et l'application de la police ; avril 2006 pour la
    surveillance pénitentiaire ; novembre 2006 pour les adjoints administratifs
    et les agents des finances publiques ; novembre 2009 pour les contrôleurs
    des finances publiques ; octobre 2011 pour les attachés. Une carrière
    commencée en 1990 dans un de ces corps traverse ceux qui les ont précédés,
    que le chaînage nomme, et dont il faudra vérifier que le noyau porte les
    grilles.
  - *Le recoupement des enseignants.* Un producteur tiers, Épicycle, publie
    sur data.gouv.fr les grilles, durées et reclassements des professeurs des
    écoles, certifiés et agrégés, chaque valeur avec sa date d'effet et son
    texte, sous licence CC BY-SA, qui obligerait à partager à l'identique ce
    qu'on en tirerait : un recoupement, non une source à reprendre. Pour la
    classe normale des professeurs des écoles, les deux jeux concordent indice
    pour indice aux neuf dates d'effet de 1990 à 2024 — les onze échelons de
    1990, de l'indice brut 379 à 801, inchangés jusqu'en 2010, ce que
    l'arrêté du 22 août 1990 fonde chez Épicycle quand le noyau ne rattache
    cette grille qu'au décret de 2010 —, et pour les durées : la minimale du
    noyau est le grand choix, la moyenne le choix, la maximale l'ancienneté.
    Deux écarts : le noyau ignore les durées nulles des deux premiers
    échelons qu'Épicycle date de 2011 à 2014 (décret n° 2010-1006), et
    l'avancement accéléré d'un an aux 6e et 8e échelons qu'il porte depuis
    2017 (durées « au choix »).
  - *Le barème.* La table INDICE n'a pas d'histoire avant novembre 2006 (une
    seule ligne de 1900 au 31 octobre 2006), et mêle le barème et le minimum de
    traitement ; la « correspondance IB-IM juridique » de la même livraison
    (en vigueur au 1er juin 2026) donne le barème A seul. L'histoire du barème
    se prendra au décret n° 82-1105.
  - *Un recoupement entre versants.* Au 1er février 2017, l'échelle C1 de
    l'État (adjoint administratif) porte aux cinq premiers échelons les
    indices bruts 347, 348, 349, 351 et 352, pour un an puis deux ans, et les
    échelles C2 et C3 s'ouvrent à 351 et 374 : ce sont, indice pour indice,
    ceux que la circulaire du centre de gestion du Haut-Rhin donne le même jour
    à la territoriale.

- *La territoriale et l'hospitalière.* Aucune base ouverte et datée trouvée.
  Les centres de gestion publient des circulaires qui photographient toutes
  les grilles de la territoriale à une date : celle du Haut-Rhin, diffusée
  par le centre de la Haute-Garonne, « Grilles indiciaires de rémunération et
  traitement brut moyen du grade applicables à la fonction publique
  territoriale à compter du 1er février 2017 », trente pages, indices bruts
  et majorés et durées, cadre d'emplois par cadre d'emplois. Elle anticipe
  parfois — des grilles y sont « en attente de la publication du décret » — :
  ces circulaires recoupent, elles ne fondent pas. Pour l'hospitalière, rien
  de structuré : un guide des carrières de la DGOS de juillet 2009, hébergé
  par un CHU, et les notes de la FHF sur les grilles du Ségur de 2021. La
  source des deux versants est le LEGI.

- *Les points du RAFP sur le relevé.* Le relevé de carrière donne « le détail
  par année civile du nombre de points cotisés » au RAFP (rafp.fr, page « Droit
  à l'information », lue le 13 octobre 2026). La lecture du relevé déposé
  (`releve_lu.py`) range le RAFP parmi les régimes qui disent le statut et ne
  portent pas de carrière : elle en reconnaît les lignes, n'en tire aucun
  revenu. Les points d'une année disent sa cotisation, donc son assiette : les
  primes, sous le plafond de 20 % du traitement (`rafp.yaml`), ou le
  traitement lui-même, le plafond atteint — ce qui contrôlerait la grille, à
  partir de 2005.

- *Les taux de primes.* Le chiffre de 23,8 % pour 2021, que la presse
  prêtait à la DGAFP, se lit à la source pour 2023 : 24,6 % du salaire brut des
  fonctionnaires, indemnité de résidence et supplément familial compris
  (rapport annuel 2025, figure 9) ; 24,7 % à l'État, 25,3 % à la territoriale,
  23,5 % à l'hospitalière. Par catégorie, État, territoriale, hospitalière :
  A 22,0, 29,9 et 24,9 % ; B 34,5, 27,0 et 23,3 % ; C 29,6, 23,4 et 20,2 %. Les
  enseignants 17,2 %, les autres fonctionnaires de catégorie A 32,9 % ; les
  policiers et l'encadrement pénitentiaire 39,3 % en catégorie B, la
  surveillance pénitentiaire 40,0 % en catégorie C. La nouvelle bonification
  indiciaire y est comptée parmi les primes, alors qu'elle compte pour la
  pension. Par corps, seuls les enseignants : professeurs des
  écoles 12,6 %, certifiés 17,3 %, d'EPS 18,2 %, de lycée professionnel 19,3 %,
  agrégés 18,9 %, de chaire supérieure 34,8 % (DEPP, Panorama 2024-2025,
  figure 7.7, 2023, heures supplémentaires et bonification comprises,
  résidence et supplément familial exclus). La part baisse avec le grade et
  l'âge : 14,2 % en classe normale chez les professeurs des écoles, 8,2 % en
  hors classe ; 19,7 % avant trente ans, 9,9 % après cinquante. Une seule part
  pour toute la carrière en met trop à la fin, là où se calcule la pension.

- *Le périmètre que cela dessine*, pour le propriétaire.
  - *L'État d'abord, les enseignants en tête* : le noyau donne les grilles
    datées et leurs textes, Épicycle les recoupe, et six corps font 46,7 % des
    fonctionnaires de l'État, depuis 1989-1990 ; l'étape 2 peut partir du
    noyau sans attendre l'index, le LEGI venant en contrôle.
  - *Les échelles communes d'abord* : C1 à C3, partagées depuis 2017 par
    l'État et la territoriale et nommées par l'hospitalière, plus les
    enseignants ; avant 2017, les échelles de chaque versant diffèrent, et
    celles de la territoriale et de l'hospitalière ne sont qu'au LEGI : il
    faut l'index reconstruit d'abord.
  - *Les trois versants ensemble* : tout le LEGI, et l'hospitalière sans
    effectifs par corps pour choisir lesquels.
  - *Les militaires* : leurs indices de solde sont lisibles dès aujourd'hui
    dans l'index ; leurs primes sont à part.
  - *Le chemin type* : avant PPCR, la durée moyenne du noyau est celle du
    choix, la plus lente celle de l'ancienneté ; depuis 2017, une durée
    unique, l'avancement accéléré des 6e et 8e échelons mis à part.
  - *Les entreprises à statut* (SNCF, RATP, IEG) : pas regardées à cette
    étape.

- *Pour la session des pages.* Rien ne doit changer dans les pages à cette
  étape : aucune donnée n'entre. Une suggestion, si elle le veut avant
  l'étape 5 : l'aide du champ « part de primes », qui vaut zéro par défaut,
  peut citer les parts de 2023 — 24,6 % en moyenne, 12,6 % chez les
  professeurs des écoles, 17,3 % chez les certifiés, 29,6 % en catégorie C de
  l'État, 20,2 % en catégorie C de l'hospitalière — avec leurs sources, le
  rapport annuel de la DGAFP et le Panorama de la DEPP.

- *L'accès, pour l'étape 2.* Répondent au proxy : data.economie.gouv.fr,
  fonction-publique.gouv.fr, insee.fr, collectivites-locales.gouv.fr,
  atih.sante.fr, le portail des archives de la DEPP, rafp.fr, senat.fr,
  assemblee-nationale.fr ; data.gouv.fr par intermittence, une nouvelle
  tentative suffit. Refusent : legifrance.gouv.fr, education.gouv.fr et
  economie.gouv.fr (403), cisirh.gouv.fr et ensap.gouv.fr ; le site de la
  DREES et celui du centre de gestion de la Haute-Garonne ne répondent pas.

Les sources, où elles sont :

- Noyau RH FPE, juillet 2026 : jeu
  `offre-de-referentiels-pour-la-gestion-de-la-chaine-ressources-humaines-rh-de-letat-gestion-administrative-paye-et-post-paye-juillet-2026`
  de data.economie.gouv.fr, pièces jointes `7_nomenclatures_noyau_xlszip`
  (29 Mo), `14_recueil_fiche_carriere_corps_emploiszip` et
  `4_informations_complementaireszip` ; l'édition de février, archivée, est le
  jeu `5995685388ee383c90cb6091` de data.gouv.fr.
- Rapport annuel sur l'état de la fonction publique, édition 2025 :
  `https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf`.
- Panorama statistique des personnels de l'enseignement scolaire 2024-2025,
  chapitre 7, « Les rémunérations » : portail des archives de la DEPP,
  `parentDocumentId=56919&documentId=56920`.
- Synthèse nationale des rapports sociaux uniques 2023 :
  `https://www.collectivites-locales.gouv.fr/files/files/Etudes-et-statistiques/RSU/Synth%C3%A8se%20RSU-2023.pdf`.
- Insee Première n° 2065 et n° 2067 : `https://www.insee.fr/fr/statistiques/8612453`
  et `https://www.insee.fr/fr/statistiques/8612479`.
- ATIH, bilan social 2022 :
  `https://www.atih.sante.fr/sites/default/files/public/content/4978/rapport_bilan_social_2022.pdf`.
- Circulaire du centre de gestion du Haut-Rhin du 1er février 2017 :
  `https://cdg31.fr/sites/default/files/g_grille_indiciaire_2.pdf`.
- Épicycle, sur data.gouv.fr : jeux `62ee45827f08a4c7877d37b1` (professeurs
  des écoles), `62c0b1ec18f63ca6e565d643` (certifiés),
  `62ee3488b096c6e73968d11b` (agrégés).
- Légifrance, par leur identifiant : décrets n° 2016-604
  (`JORFTEXT000032527130`), 2021-1819 (`JORFTEXT000044571773`), 2016-594
  (`JORFTEXT000032526619`), 2021-1257 (`JORFTEXT000044126316`), 2021-1267
  (`JORFTEXT000044126512`), 2022-1207 (`JORFTEXT000046242710`), 2021-1262
  (`JORFTEXT000044126441`), 2016-647 (`JORFTEXT000032551863`), 2009-21
  (`JORFTEXT000020052729`).
- Sénat, rapport pour avis n° 134 (2023-2024), tome V :
  `https://www.senat.fr/rap/a23-134-5/a23-134-5_mono.html` ; question écrite
  n° 16217 : `https://questions.assemblee-nationale.fr/dyn/17/questions/QANR5L17QE16217.pdf`.

*Ce qui reste.* Que le propriétaire tranche le périmètre, le chemin type, la
part de primes par période, les cas types de l'action 152 et les entreprises à
statut. Puis l'étape 2, qui commence par élargir le filtre de l'index et le
faire reconstruire, à moins que le périmètre retenu ne soit l'État seul, que le
noyau porte déjà.
