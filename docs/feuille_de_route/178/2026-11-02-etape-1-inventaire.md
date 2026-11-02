# Étape 1 : l'inventaire du panorama de la DREES, édition 2026

**Le 2 novembre 2026, ce qui est fait.** Le panorama est récupérable par
toute session, relevé fiche par fiche, et chaque fiche a son statut au suivi.

1. *L'accès.* Le site de la DREES refuse le cloud : réponse vide à curl, 503
   à WebFetch, comme les notes le disent depuis le 11 octobre ; Internet
   Archive coupe la connexion, et WebFetch ne l'atteint pas. Le portail de
   données répond à WebFetch (à curl, par intermittence : la poignée de main
   tombe) ; il n'a reçu de l'édition 2026 ni données ni fichiers — son seul
   jeu « panorama-retraite » est le graphique 1 de 2025 —, et l'EACR qu'il
   sert est celle du 22 mai 2026, que le dépôt lit déjà. L'UNSA Retraités sert
   le PDF depuis la parution, le 14 octobre (« Panorama DREES Retraités et
   retraites 2026 ») : titre « Les retraités et les retraites - Édition
   2026 », créé sous InDesign le 12 octobre 2026, 314 pages, ISBN
   978-2-11-162795-6. Le manifeste le déclare, `drees_panorama_retraites_2026`,
   `blocage: refus`, avec ce miroir et son empreinte ; `--recuperer` l'a
   rapporté dans `data/brut/` et l'a vérifié. Les mentions légales de la DREES
   refusent aussi le cloud : la licence n'est pas lue, rien ne se republie.
2. *Le relevé.* `scripts/fetch/drees_panorama.py` lit le PDF par
   `pdftotext -layout` et écrit `tests/temoins/drees_panorama_2026.json` :
   le sommaire (titre et première page de chaque fiche et de chaque annexe),
   puis chaque figure — 172 tableaux, graphiques, cartes et schémas — et
   chaque encadré — 41 —, sa page imprimée, son titre entier et sa source.
   Une page se range sous sa fiche par sa ligne de tête, où le numéro est à
   gauche ou à droite selon la parité ; son numéro vient du pied de page. Un
   titre se prolonge sur les lignes de texte qui le suivent, une source tant
   qu'elle ne finit pas sur un point ; ni une note numérotée, ni l'étiquette
   d'un volet (« 4a. »), ni une rangée de nombres ou une graduation ne les
   prolongent, et un encadré ne prend pas la source de la figure qui le suit.
   Chacune de ces règles a son cas, tiré du PDF, dans
   `tests/test_drees_panorama.py`. Contrôles : aucun numéro manquant dans
   aucune fiche ; aucun titre de figure ailleurs qu'en tête de ligne, ce que
   la mise en page à deux colonnes aurait pu cacher ; chaque figure des
   fiches a sa source.
3. *Le suivi.* `data/reference/drees_panorama_2026.yaml` : de chaque fiche,
   ses sources d'amont, son statut — `au_depot`, `a_tirer`, `a_confronter`,
   `hors_champ` —, les jeux du manifeste qui portent déjà sa donnée, ce que
   le dépôt en tirera et l'étape qui s'en charge. Un test refuse une fiche du
   relevé qui n'y est pas.

**Ce que le panorama apporte de neuf**, que le classement fait ressortir :
sept fiches au dépôt, sept à tirer, seize à confronter, quatre hors champ.

1. *L'EIC de 2021* (fiches 12 et 21, et la 23 en partie), la première fois
   qu'un panorama s'en sert, quand le dépôt lit celle de 2017 : les durées
   validées par âge et par génération, leur nature, la situation à 59 ans et
   les trajectoires de fin de carrière. C'est l'étape 3.
2. *Les chiffres de 2024 que le dépôt n'a pas* : l'âge conjoncturel de 2023
   et de 2024, 62 ans et 11 mois fin 2024 (le dépôt s'arrête à 2022) ; la
   pension moyenne de fin 2024, 1 752 euros bruts et 1 626 nets (le dépôt,
   2022) ; l'invalidité de 2024, 843 400 bénéficiaires, leurs montants et les
   106 000 nouveaux (le dépôt, les effectifs de 2022) ; le cumul
   emploi-retraite, 619 000 cumulants, et la retraite progressive, environ
   42 400 personnes ; les parts au minimum de pension de la génération 1953,
   de l'EIR de 2020, au lieu de celles de l'EIR de 2012 que cite
   `part_minimum_contributif.py`. Les comptes de la protection sociale, eux,
   vont déjà à 2024, mais sur le risque vieillesse-survie entier, 426,7
   milliards d'euros, dont les 395 milliards de pensions de retraite du
   panorama sont une part, à recouper poste par poste.
3. *Les règles de 2026*, pour le scénario 1 (étape 5) : l'encadré 1 de la
   fiche 2, les mois où chaque génération atteint l'âge d'ouverture des
   droits sous la loi de financement pour 2026, et les tableaux de la fiche 14
   (âges, durées, carrière longue) ; les pensions d'invalidité du régime
   général au 1er janvier 2026 (fiche 24) ; le minimum vieillesse (fiche 26) ;
   les revalorisations, 0,9 % au 1er janvier 2026 pour les régimes de base,
   que le dépôt porte déjà, et aucune à l'Agirc-Arrco en novembre 2025 (fiche
   4).
4. *Ce que le modèle peut affronter* (étape 4) : l'érosion des pensions par
   génération, sur les cas types de TRAJECTOiRE ; le taux de remplacement
   médian par génération ; la pension des nouveaux retraités, que le cadrage
   de l'EACR porte sans que le dépôt la retienne ; les durées de carrière ;
   les départs anticipés ; la polyaffiliation ; le profil des allocataires du
   minimum vieillesse et le non-recours ; la retraite supplémentaire (fiches
   29 à 32), que le pilier capitalisé de la proposition, « logé dans
   l'enveloppe du PER », et sa capitalisation volontaire rendent pertinente.
5. *Hors champ* : les opinions (fiche 19), les motivations de départ (20),
   le PER d'entreprise collectif (33) et la retraite supplémentaire
   d'entreprise (34), que ni le modèle ni la proposition ne représentent.

Trois jeux du portail de données, repérés au catalogue, sont au vivier : les
trimestres validés à 30 ans, refaits le 9 octobre 2026 (étape 3), les séries
de la retraite supplémentaire (étape 4), et un graphique sur le non-recours
des personnes âgées, du 6 juillet 2026, à identifier.

**Ce que le classement a vérifié**, par l'éclaireur puis à la source : la
dernière ligne de `age_conjoncturel_depart.csv` (2022), de
`depenses_retraite.csv` (2024) et de `pensions_brutes_nettes.csv` (2022) ; le
total du minimum vieillesse de 2024, que le classeur de l'INSEE redonne à 552
près ; la revalorisation du 1er janvier 2026 dans `revalorisation_pensions.csv`.

**Ce qui reste.** Les étapes 2 à 7 de l'action, et ce qui revient au
propriétaire : les fichiers Excel des fiches, les mentions légales de la
DREES, l'empreinte du PDF qu'elle sert.
