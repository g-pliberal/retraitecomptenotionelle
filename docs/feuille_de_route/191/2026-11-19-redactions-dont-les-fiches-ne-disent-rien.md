# Les rédactions dont les fiches ne disaient rien : quatre-vingt-deux lues, une question

**Reprise, au 19 novembre 2026.** Le sixième cliquet de la note de décision
0009 comptait 83 cas où une fiche ne disait rien d'une rédaction en vigueur
d'un article qu'elle cite. Quatre-vingt-deux sont lus : aucune rédaction ne
change la règle que sa fiche porte, et chaque fiche le déclare, mot à mot à
l'appui. Le cliquet est à 1. Reste un cas, que le propriétaire doit trancher :
L. 173-2 du code de la sécurité sociale ne nomme plus le régime des cultes
depuis 2018, et la fiche `minimum_contributif` écrête encore son minimum.
Reste aussi une lecture à faire, hors du cliquet : la fiche
`carpimko_ages_2015` dit ouvrir la complémentaire au départ pour carrière
longue depuis 2024, quand ses statuts renvoient au départ des assurés
handicapés. Aucun résultat n'a bougé. Le détail est plus bas.

Le 19 novembre 2026, sur l'accord du propriétaire, la session lit les
dix-huit rédactions de 2026 et après dont trente-deux couples d'une fiche et
d'une rédaction ne disaient rien. Chacune est lue dans l'index LEGI, à jour au
16 novembre, et comparée mot à mot à celle d'avant
(`dila_cherche.py legi --num <article> --diff`).

**Ce que chaque rédaction change, et pourquoi la fiche n'en bouge pas.**

- *Le décret n° 2026-948 du 12 octobre 2026*, la majoration de durée
  d'assurance des élus locaux, pour les pensions prenant effet à compter du
  1er janvier 2027 : il l'ajoute à l'article 15 du décret n° 2003-1306, à
  l'article 12 du décret n° 2004-1056, à R. 8-1 du code des pensions des
  marins, à R. 732-61 du code rural et à l'article 3 du décret n° 2017-1000.
  Treize couples. La majoration a sa fiche, `majoration_duree_elus_locaux`,
  qui rattache les cinq rédactions ; les huit fiches qui citent ces articles
  pour autre chose — la majoration des sapeurs-pompiers volontaires, la
  bonification du cinquième, le taux maximum, les enfants, le barème et la
  durée agricoles — y retrouvent leur clause.
- *R. 351-27 du code de la sécurité sociale, au 1er août 2026* : le
  coefficient de minoration « est 1,25 % », à la place de « 2,5 % pour les
  pensions ayant pris effet avant le 1er janvier 2004 ». La rédaction du
  1er janvier 2026 avait ôté le tableau par génération sans laisser de
  coefficient aux pensions d'après 2003 ; celle-ci le rend. 1,25 % est le
  coefficient des assurés nés après 1952, les seuls qu'une décote atteigne
  encore. Trois couples.
- *R. 351-12, au 1er novembre 2026* : un mot au 5°, la rente pour une
  incapacité permanente « professionnelle ». Trois couples.
- *D. 351-2-2, au 1er août 2026* : un 4° au III, les trimestres de L. 634-4
  du code général de la fonction publique et de L. 4138-6-1 du code de la
  défense ; les 120 trimestres du II, que la fiche des cultes lit, restent.
- *L'article 20 du décret n° 2003-1306, au 1er août 2026* : « bonifications
  et majorations » au I ; le reste mot pour mot. Trois couples.
- *Le code rural, au 1er janvier 2026* : L. 732-56 (des renvois), L. 732-63
  et D. 732-111 (les périodes de chef à titre secondaire et la durée de
  L. 351-1, pour les pensions prenant effet à compter de 2026), que la fiche
  du relèvement de septembre 2023 ne lit que pour des pensions d'avant ;
  D. 732-114, qui écrête à l'année une majoration qui n'est plus celle de la
  fiche qui citait sa rédaction de 2005 ; D. 731-121, les taux d'après 2025,
  quand la fiche n'en tire que ceux de 2016 à 2025.
- *L'article 2 du décret n° 79-262, au 1er juillet 2026* : la Cipav, qui n'a
  plus de classes depuis 2023.
- *Le règlement du RCI, au 1er janvier 2027* (arrêté du 21 septembre 2026) :
  l'article 27 change de renvois, pour le cumul de 2027 ; l'article 39 ne
  vise plus que D. 635-9 ; l'article 41, I, prend le revenu de référence du
  jour de l'effet de la pension du conjoint survivant, non plus de celle de
  l'assuré. Ce I, le versement en une fois de la réversion de moins de
  quarante points, le modèle ne le porte pas : la fiche
  `versement_unique_rci` le déclarait déjà, et rattache la rédaction.

**Les rédactions d'avant 2026, lues le même jour.** Le propriétaire a demandé
d'enchaîner : trente rédactions, cinquante et un couples. Ce sont les
rédactions en vigueur d'articles que les fiches citent dans une rédaction
plus ancienne. Cinquante couples reçoivent leur déclaration sans effet, dans
trente fiches, et se rangent en quatre familles.

- *La fiche renvoie à un âge qu'elle ne fixe pas.* L. 161-17-2 dans sa
  rédaction du 31 décembre 2025, D. 161-2-1-9 dans celle du 1er septembre
  2023, L. 351-8 dans celle du 28 février 2025, L. 643-3 dans celle du
  31 décembre 2025, D. 351-2 : les fiches des complémentaires — notaires,
  auxiliaires médicaux, agents d'assurance, Agirc-Arrco — et celle de l'âge
  où la décote s'annule disent « l'âge de L. 161-17-2 » ou « celui du 1° de
  L. 351-8 », que le moteur lit à la table de l'âge légal. Seize couples.
- *La fiche s'arrête avant la rédaction.* L'assiette de la complémentaire des
  artisans et des commerçants finit aux revenus de 2015, et cinq rédactions
  de 2020 à 2024 n'y touchent pas ; de même l'allocation des professions
  libérales d'avant 2004, la valeur de service de 2004, le maximum des
  militaires de 1964, la limite d'âge des industries électriques de 1946.
- *L'article a changé ailleurs que là où la fiche lit.* L. 24 et L. 17 du
  code des pensions, L. 351-10, l'article 16 de l'arrêté de l'Ircantec,
  l'article 26 du décret de la caisse des navigants, les articles 22 et 25 du
  décret de la CNRACL, les articles 6 et 51 du règlement de la RATP,
  l'annexe 3 du statut des industries électriques : la clause que la fiche
  cite s'y retrouve mot pour mot.
- *La rédaction dit ce que la fiche disait déjà, ou ce qu'elle déclare ne
  pas porter.* L. 10 du code des pensions compte depuis 2004 les services
  d'après la limite d'âge ; les périodes d'assurance vieillesse des parents
  au foyer retirées du minimum garanti, que le modèle ne compte pas ; les
  indemnités journalières de maternité d'avant 2012, que la fiche du salaire
  annuel moyen déclare absentes.

**La question laissée au propriétaire.** L. 173-2 du code de la sécurité
sociale, qui écrête le minimum contributif sur l'ensemble des pensions,
nommait de 2012 à 2017 les régimes de L. 200-2, de L. 382-15 — les cultes —,
du 2° de L. 611-1 et des salariés agricoles. Sa rédaction du 1er janvier 2018
(LEGIARTI000036391874) ne nomme plus que le régime général, les salariés
agricoles et le régime social des indépendants. La fiche
`minimum_contributif` compte la Cavimac parmi ses régimes. La session n'a
pas établi si la caisse écrête encore le minimum des cultes, par L. 382-27,
ni ce que le moteur fait : le couple reste sans réponse, et le cliquet à 1.

**Une lecture à faire, trouvée en passant.** La fiche `carpimko_ages_2015`,
version `statuts_de_2024`, écrit que la complémentaire s'ouvre « dès l'âge du
III de L. 643-3 à qui part en carrière longue à la base ». Le III de L. 643-3
est le départ des assurés handicapés ; la carrière longue est au II, que les
statuts ne nomment pas. Si le moteur sert la complémentaire sans abattement
au départ pour carrière longue depuis 2024, c'est un écart au texte, et sa
correction changerait des résultats : à instruire à part, sur l'accord du
propriétaire.

**Ce qui est posé.** Trente-deux déclarations `textes_sans_effet`, dans
vingt-deux fiches, chacune avec ce que la rédaction change et ce que la fiche
tient de l'article ; les citations sont vérifiées contre le texte de l'index.
Pour les rédactions d'avant 2026, cinquante de plus, dans trente fiches.
`sans_un_mot` passe de 83 à 1 dans `data/reference/textes/perimetre.yaml`,
en deux commits.
Aucune règle, aucun paramètre, aucun fichier de régime ne change.

**À savoir.** Chacune des dix-huit rédactions était déjà rattachée par une
autre fiche : la lecture n'a trouvé aucune règle que le modèle aurait
manquée. La session, ouverte sur Opus, est passée sur Fable 5.2
avant d'écrire, sur l'accord du propriétaire.
