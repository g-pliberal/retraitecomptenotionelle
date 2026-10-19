# Étape 10, deuxième partie : les droits contrefactuels de la carrière saisie, au 31 août 2023 et sous la loi de 2023 sans la suspension

**La demande.** Le premier des restes de la note du 16 octobre
(`2026-10-16-etape-10-ages-de-depart-au-site.md`, « Ce qui reste », 1) : les
droits de la carrière saisie sous deux autres états du droit que celui qui
s'applique — le droit en vigueur au 31 août 2023, avant que la loi n° 2023-270
du 14 avril 2023 ne prenne effet, et cette loi sans la suspension que l'article
105 de la loi n° 2025-1403 du 30 décembre 2025 y a mise. Le registre dit ce que
font les autres : PENSIPP applique à une génération le barème d'une année
donnée (`UseLeg`) ; l'outil « Quand pourrai-je partir » donne l'âge et la durée
sous trois états du droit, et l'écart en mois ; le simulateur de dépense
publique, le gain de la suspension génération par génération. Ni le contrôle
d'un relevé, ni l'indice majoré, ni le solveur inverse. Session du 19 octobre,
la seule sur les pages.

**La veille.** `python scripts/veille_droit.py`, puis l'index LEGI, récupéré et
mis à jour (aucun incrément depuis le 18 octobre) : aucune version de
L. 161-17-2 ni de L. 161-17-3 postérieure au 31 décembre 2025. Lues :
D. 161-2-1-9 dans ses versions du 31 décembre 2011 (« 6° Soixante deux ans pour
les assurés nés à compter du 1er janvier 1955 ») et du 1er septembre 2023 (10° à
14°, 63 ans pour 1964, 64 ans dès 1968) ; L. 161-17-2 dans ses versions de 2011,
du 28 février 2025 et du 31 décembre 2025 ; L. 161-17-3 dans celles de 2014, de
2023 et de 2025. Entrée du journal : `2026-10-19-action-138-etape-10-droits-contrefactuels.yaml`.

**Ce qui est fait.**

- Le modèle, Python puis portage. `Parametres.droit_contrefactuel` (`null` dans
  `config.js`) nomme l'état du droit que le scénario 1 applique : `None`, le
  droit qui s'applique ; `loi_2023_sans_suspension` ; `au_31_aout_2023`
  (`DROITS_CONTREFACTUELS`, `scenarios/actuel.py` et `scenario-actuel.js`). Un
  nom inconnu arrête le moteur. Trois tables changent, rien d'autre
  (`ScenarioActuel._sous_le_droit`, `_sousLeDroit`) : l'âge légal et la durée
  requise des textes gardés, posés sur les tables du droit en vigueur de leur
  première génération à toutes les suivantes (`TableRecouverte`) ; la carrière
  longue sans les décrets qui prennent effet à compter de la date écartée
  (`CarriereLongue.avant`) — ceux du 7 mai 2026, puis aussi ceux du 3 juin 2023 ;
  la copie garde les rédactions de D. 351-1-2 que l'étape 14 a datées le même
  jour, et le JavaScript, qui les perdait, est tenu par la carrière du chômeur.
  Au 31 août 2023, la durée que le droit en vigueur garde aux pensions d'avant
  septembre 2026 devient celle de 2014.
- Les données : `age_ouverture_avant_reforme_2023.csv` (62 ans dès septembre
  1961) et `age_ouverture_avant_suspension.csv` (1964 à 1968), niveau `haute`,
  au paquet du site, qui passe à la version 31 : deux sessions avaient porté la
  29 puis la 30 le même jour, sans ces tables, et un navigateur qui aurait gardé
  l'une d'elles ne la redemanderait pas. Les durées des deux états
  existaient : `duree_requise_avant_reforme_2023.csv`,
  `duree_requise_avant_suspension.csv`. Les fiches `age_legal_par_generation` et
  `duree_requise_par_generation` disent l'usage ; deux rédactions que la première
  cite prennent un statut, et le cliquet des textes descend d'autant.
- La page des résultats : le dépliant « Avec ou sans la réforme de 2023 »
  (`avecOuSansLaReforme`, `pages.js`), après « Partir plus tôt ou plus tard ».
  Pour chaque état du droit, les deux premiers départs de l'estimation
  officielle, au plus tôt et au taux plein — l'âge, le mois, l'écart au droit
  qui s'applique, le net du premier mois —, et la durée requise ; une bulle dit
  ce que chaque état retient et ce qui ne change pas.
- Les tests : `tests/test_droits_contrefactuels.py`, l'âge et la durée de cinq
  mois de naissance sous les trois états, lus aux textes, la carrière longue
  d'un né en février 1966 (60 ans et 9 mois, 61 ans, 60 ans), la durée d'un
  départ de juillet 2026 (171, 171, 169) ; dans `test_estimation_du_site.py`,
  les deux moteurs d'accord sous chaque droit, sur les dix-sept carrières du
  fichier — dont, nouvelle, la carrière longue coupée de deux ans de chômage
  indemnisé —, et le dépliant contre le Python. Au registre, deux points passent à
  `repris` : celui de PENSIPP, celui de l'outil « Quand pourrai-je partir ».

**Ce que montrent les mesures.** Le né en mai 1968 entré à vingt-deux ans part
au plus tôt à 63 ans et 9 mois, à 64 ans sans la suspension, à 62 ans au
31 août 2023, avec 172, 172 et 170 trimestres requis ; son taux plein vient à
65 ans et 6 mois, au même âge, puis 6 mois plus tôt. Le né en juin 1964 gagne
3 mois à la suspension au plus tôt comme au taux plein. Le fonctionnaire né en
1975 part à 64 ans sous les deux premiers, à 62 ans sous le troisième, avec le
même taux plein. Les deux droits contrefactuels coûtent 30 à 40 ms chacun dans
node. Aucun des 888 témoins de simulation ne bouge ; 40 des 79 rendus de page
gagnent le dépliant, et rien d'autre.

**Ce qui reste.**

1. Ce que les droits contrefactuels ne changent pas, et que la bulle déclare :
   les âges propres des catégories actives, des militaires et des régimes
   spéciaux ; le minimum contributif relevé en septembre 2023 ; les
   coefficients de solidarité que l'Agirc-Arrco appliquait encore en août
   2023 ; la durée du XXIV de la loi de 2023 pour les fonctionnaires partis
   avant soixante ans ; et, au 31 août 2023, les articles 103 et 104 de la loi
   du 30 décembre 2025, que le droit garde.
2. Les deux tables d'âges à certifier par le recoupement de l'IPP
   (`RECOUPEMENTS_IPP`, `scripts/verifier_donnees.py`), comme les durées.
3. Le gain de la suspension génération par génération, en un tableau, que le
   simulateur de dépense publique donne (registre, `a_reprendre`) : la page ne
   le montre que pour la génération saisie.
4. Les restes de la note du 16 octobre, dans l'ordre, une session par point :
   le contrôle d'un relevé, l'indice majoré, le solveur inverse ; puis, s'il le
   faut, le dépliant des âges de départ.
