# Étape 3 : la date d'effet de la pension de base des libéraux, au trimestre civil

**Reprise, au 12 novembre 2026.** La lecture est faite, la règle est écrite,
mais elle n'est pas publiée. La pension de base d'un libéral ne commence qu'un
1er janvier, avril, juillet ou octobre ; depuis le 5 mars 2023, celle d'un
affilié de la Cipav commence au mois. Le moteur la date au mois pour tous :
jusqu'à deux mois trop tôt. La règle et ses tests, verts dans les deux
moteurs, sont gardés dans un fichier à rejouer. Publiée seule, elle sépare la
base de cinq complémentaires que le moteur date à part, et ce partage change
de 4 à 7 % la complémentaire des auxiliaires médicaux, sans raison de droit.
Ce qui reste : lire la date d'effet dans les statuts de ces cinq sections ;
comprendre cet écart ; rejouer le fichier ; reprendre trois tests dont la date
change. Au propriétaire : publier la règle seule, ou avec ces lectures. Détail
plus bas.

**La demande, le 12 novembre 2026.** La passe de lecture de l'action 184 a
trouvé des points que le modèle n'applique pas ou qu'elle n'a pas pu vérifier
(note `184/2026-11-12-etape-6-bilan-de-la-passe.md`). La session
d'orchestration les a listés au propriétaire, qui a répondu : « Fait une étape
pour chaque point du modèle ». Celle-ci en est une.

**Ce qui est su.** Le lot du code de la sécurité sociale l'a relevé
(`184/2026-11-12-etape-6-code-de-la-securite-sociale.md`, « Ce qui change une
règle », point 1) : article R. 643-6 (LEGIARTI000047265890, en vigueur), règle
depuis 2004, dérogation pour la Cipav depuis le 5 mars 2023. La fiche
`cnavpl_allocation_avant_2004` ne déclare l'écart qu'avant 2004, où le modèle
date au mois.

**Ce qu'il y a à faire.**

1. Lire R. 643-6 dans ses rédactions, et ce que les sections publient de la
   date d'effet.

2. Regarder ce que le moteur fait de la date d'effet d'une pension de base
   libérale liquidée après 2004, par un cas joué.

3. S'il y a un écart : le test, vu rouge, puis la règle, la Cipav à part
   depuis mars 2023 ; sinon, la fiche le dit.

**Fini quand** la fiche dit la règle de date d'effet et que le moteur
l'applique, ou que la limite est dite.

**Les règles de l'étape.** C'est une règle du scénario 1 : la session se mène
sur Fable 5.2, ouvre par `python scripts/veille_droit.py` et suit
`docs/veille_droit.md`. Le test d'abord, sa valeur attendue tirée du texte ou
d'un calcul posé à la main. Le moteur est en chantier dans deux autres
actions, qui le séparent du site et lui font lire les règles dans les fiches
(`python scripts/reprise.py 187`, puis `191`) : lire leurs blocs avant de
toucher au moteur, et ne pas défaire ce qu'elles ont posé. Une seule session à
la fois écrit dans le modèle et son portage.

## Ce qui a été fait, le 12 novembre 2026

**Ce que la lecture a établi.** L'article R. 643-6 a trois rédactions dans
l'index LEGI du dépôt. Celle du 21 décembre 1985 (LEGIARTI000006751828) :
« L'entrée en jouissance de l'allocation est fixée au premier jour du
trimestre civil qui suit cette demande sans pouvoir être antérieure au
soixante-cinquième anniversaire ». Celle du 1er janvier 2004
(LEGIARTI000006751829) ne garde que la date : « L'entrée en jouissance de la
pension de retraite est fixée au premier jour du trimestre civil qui suit la
demande de l'intéressé. » Celle du 5 mars 2023 (LEGIARTI000047265890, en
vigueur) ajoute : « Par dérogation, l'entrée en jouissance de la pension de
retraite des travailleurs indépendants libéraux affiliés à la section
professionnelle mentionnée au 11° de l'article R. 641-1 est fixée dans les
conditions prévues au I de l'article R. 351-37 » — le premier jour d'un mois,
pour la Cipav. Le décret n° 2023-148 du 2 mars 2023 l'a écrite (article 1er,
5°, JORFARTI000047259558) ; son article 4 ne diffère que d'autres alinéas, et
celui-ci vaut du lendemain de la publication.

Les sections l'appliquent ainsi. La CARMF, guide « Préparez votre retraite en
temps choisi », édition de juin 2026, sous son tableau des âges : « Les
retraites étant liquidées au trimestre, elles ne peuvent prendre effet qu'au
1er jour du trimestre civil suivant (1er janvier, 1er avril, 1er juillet, 1er
octobre). » La CARPIMKO, page « La date de prise d'effet de ma retraite » :
« fixée au plus tôt au 1er jour du trimestre civil qui suit votre demande »,
avec un exemple daté, une assurée née le 1er janvier 1963 dont le départ
« pourra être fixé au plus tôt à partir du 1er octobre 2025 ». Cet exemple ne
départage rien : le 1er octobre est le premier jour d'un mois et d'un
trimestre, et la page fait atteindre 62 ans et 9 mois « le 1er septembre
2025 » à une assurée qui les atteint le 1er octobre. La CARCDSF et la CAVEC
publient la même règle ; les pages lues de la CNAVPL et de la Cipav ne disent
rien de la date d'effet.

**Ce que fait le moteur.** Il date toute pension au premier jour du mois qui
suit l'âge (fiche `date_effet_mois_suivant`, qui nomme la CNAVPL). Un cas
joué : le médecin né le 15 janvier 1963, parti à 62 ans et 9 mois, atteints le
15 octobre 2025. Le moteur lui sert ses trois pensions au 1er novembre 2025 ;
R. 643-6 fait commencer sa base au 1er janvier 2026. Né le 15 février, il
perd un mois ; né le 15 mars, la date est la même. L'écart touche deux
libéraux sur trois, d'un ou deux mois.

**La règle écrite.** Le test d'abord, dix essais datés à la main depuis le texte
(`tests/test_date_d_effet_des_liberaux.py`), vus rouges puis verts, servis par
le portage et refaits au bit près par le moteur Python. Le moteur date l'unité
de la base des libéraux comme avant — au départ déclaré, à l'ouverture du
droit ou à la date demandée —, puis la reporte au premier mois d'un trimestre
civil qui n'est pas avant, sous un motif neuf, `trimestre_civil`, que la page
dit en deux phrases. La Cipav reste au mois quand sa pension, datée au mois,
commence après le 5 mars 2023. Les paramètres se lisent dans une fiche neuve,
`cnavpl_entree_en_jouissance`, trois versions : avant le code de 1985, que
personne n'a lu et qu'elle présume pareille ; le trimestre civil ; la Cipav au
mois. Le texte date de la demande, que le modèle ne connaît pas : la règle
tient la pension pour demandée à temps.

**Ce qu'elle déplace.** Sur 932 témoins de simulation, 87 bougent, tous de
libéraux : leurs dates d'effet, et un départ de plus quand la complémentaire
est datée à part. La pension annuelle du système actuel ne bouge que dans
quatre, de +0,80 % à +1,80 %. Le médecin du cas joué passe de 30 929,86 € à
30 742,96 € par an. La table du coût reste identique à l'octet. Deux fichiers
de tests des libéraux, écrits sur des dates au mois, sont remis à leur valeur
dans le correctif. Cinq tests de la suite rapide rougissent encore : deux
coefficients des sections de santé et une majoration pour enfants, dont la
date change, et le cliquet des textes, à baisser encore.

**Pourquoi elle n'est pas publiée.** Elle déplace plus que son cas. Le moteur
date à part cinq complémentaires — CARPV, CAVEC, CAVOM, CARPIMKO, CPRN. La
règle, qui ne lit que R. 643-6, les laisse au mois : la base part alors un ou
deux mois après elles, en deux départs. Or la complémentaire de la CARPIMKO
n'a pas le même montant selon qu'elle se liquide avec la base ou sans elle, à
la même date : pour l'auxiliaire médical né en 1955 et parti à 64 ans, son
coefficient de majoration passe de 1,075 à 1,15, et sa pension de 4 315,68 € à
4 616,77 € ; pour celui de 1965, de 1,025 à 1,0625. Cet écart existe déjà sur
`main` pour qui demande sa complémentaire avant sa base ; la règle l'étendrait
à deux auxiliaires médicaux sur trois. Lequel des deux coefficients est le bon
n'est pas établi.

Le règlement de la CARPIMKO de 2026 date d'ailleurs sa complémentaire comme la
base (article 7, JORFARTI000054435915) : « La date d'entrée en jouissance de
la retraite est fixée au premier jour du trimestre civil qui suit la demande,
sans pouvoir être antérieure à l'âge terme ». Les statuts des quatre autres
sections ne sont pas lus pour la date d'effet.

**Sur `main`.** La fiche `cnavpl_allocation_avant_2004` dit l'écart pour la
pension en points et porte les lectures. Le correctif est dans
`docs/mesures/192/2026-11-12-etape-3-la-regle-et-ses-tests.txt` : la règle
dans les deux moteurs, la fiche neuve, les phrases de la page, les tests. Rien
du moteur n'a changé.

**Au propriétaire.**

1. Publier la règle seule, ou attendre la lecture des cinq sections datées à
   part. Recommandation : attendre. Seule, elle fait partir la base après sa
   complémentaire là où la caisse les sert le même jour, et elle étend l'écart
   de la CARPIMKO.

2. La pension tenue pour demandée à temps : le texte compte du jour de la
   demande, le modèle du jour où il servirait la pension au mois.
   Recommandation : garder cette présomption, que la fiche déclare.

**Ce qui reste.**

1. Lire la date d'effet dans les statuts de la CARPV, de la CAVEC, de la
   CAVOM, de la CPRN et, avant 2026, de la CARPIMKO ; puis ceux de la Cipav
   pour sa complémentaire.

2. Comprendre pourquoi la complémentaire de la CARPIMKO change de coefficient
   quand elle se liquide sans la base, et corriger, le test d'abord.

3. Rejouer le correctif, refaire le paquet et les témoins, puis reprendre à
   la main les trois tests dont la date change, et le cliquet des textes.
