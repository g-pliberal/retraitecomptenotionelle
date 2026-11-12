# Étape 2 : la carrière longue du non-salarié agricole, quatre trimestres à la fin de l'année de l'anniversaire

**Reprise, au 12 novembre 2026.** La lecture est faite, la règle est écrite,
mais elle n'est pas publiée. Le non-salarié agricole est tenu pour entré tôt
avec quatre trimestres à son régime à la fin de l'année de l'anniversaire,
depuis 2004 ; la MSA l'applique. La règle et son test, verts dans les deux
moteurs, sont gardés dans un fichier à rejouer. Publiée, elle avance d'un an
le départ du cas type de l'exploitant agricole, le seul de son régime dans le
coût : sept tests du coût se déplacent, et le calcul qui date les cas types
fait partir celui de 1953 à un âge où le droit n'est pas ouvert. Ce qui
reste : corriger ce calcul, le test d'abord ; rejouer le fichier ; remesurer
les sept tests. Au propriétaire, avant : garder ou recaler ce cas type.
Détail plus bas.

**La demande, le 12 novembre 2026.** La passe de lecture de l'action 184 a
trouvé des points que le modèle n'applique pas ou qu'elle n'a pas pu vérifier
(note `184/2026-11-12-etape-6-bilan-de-la-passe.md`). La session
d'orchestration les a listés au propriétaire, qui a répondu : « Fait une étape
pour chaque point du modèle ». Celle-ci en est une.

**Ce qui est su.** Le lot de la fonction publique l'a lu
(`184/2026-11-12-etape-6-fonction-publique.md`, « Ce qui change une règle »,
point 2) : article D. 732-40 du code rural (LEGIARTI000053365409, décret n°
2025-1410, pensions prenant effet à compter du 1er janvier 2026). La rédaction
de 2023 offrait déjà cette voie (« soit… soit ») ; celle de 2026 l'écrit « par
dérogation à D. 351-1-3 ». Le modèle : `entreePrecoce`. La fiche
`carriere_longue` tient la rédaction à rattacher.

**La décision sur l'état de la fiche.** Le lot l'a laissée `conforme` malgré
l'écart, qui ne touche qu'un régime et un cas étroit. La session
d'orchestration a jugé ce choix défendable ; le propriétaire, le 12 novembre :
« Pour les décisions à trancher : je choisis tes recommandations ». Elle reste
donc `conforme` jusqu'à cette étape, qui ferme l'écart.

**Ce qu'il y a à faire.**

1. Lire les rédactions de 2005, 2011, 2012, 2023 et 2026 de l'article
   D. 732-40, et dire depuis quand la voie des quatre trimestres existe ; si
   « par dérogation » ferme en 2026 la voie des cinq trimestres ; ce que la
   MSA publie.

2. Le test, vu rouge : un non-salarié agricole né hors du dernier trimestre,
   quatre trimestres à son régime à la fin de l'année de l'anniversaire.

3. La règle, datée de ce que la lecture a établi, dans le modèle et son
   portage ; la fiche.

**Fini quand** la condition d'entrée du non-salarié agricole est celle du
texte à chaque date, et que la fiche cite la rédaction qu'elle applique.

**Les règles de l'étape.** C'est une règle du scénario 1 : la session se mène
sur Fable 5.2, ouvre par `python scripts/veille_droit.py` et suit
`docs/veille_droit.md`. Le test d'abord, sa valeur attendue tirée du texte ou
d'un calcul posé à la main. Le moteur est en chantier dans deux autres
actions, qui le séparent du site et lui font lire les règles dans les fiches
(`python scripts/reprise.py 187`, puis `191`) : lire leurs blocs avant de
toucher au moteur, et ne pas défaire ce qu'elles ont posé. Une seule session à
la fois écrit dans le modèle et son portage.

**Ce qui a été fait, le 12 novembre 2026.** L'étape n'est pas close : la
lecture est faite et publiée dans la fiche, la règle est écrite et testée, et
elle reste hors de `main`, qu'elle aurait rougi.

- *Lu.* L'article D. 732-40 du code rural dans ses cinq rédactions, et le III
  de l'article 28 ter du décret n° 55-753 qui le précédait
  (LEGIARTI000006763597), dans l'index LEGI à jour au 11 novembre 2026 ;
  D. 351-1-3 et D. 732-41 en vigueur en 2026 ; le décret n° 2025-1410 dans
  l'index JORF. **La voie a l'âge de la carrière longue du régime** : dès 2004,
  sont tenus pour entrés avant seize ou dix-sept ans ceux qui justifient « soit
  des conditions définies à l'article D. 351-1-3 », soit de « quatre trimestres
  à la fin de l'année » de l'anniversaire, validés au régime agricole. Les
  rédactions de 2005, 2011, 2012 et 2023 n'en changent que les bornes. Aucun
  autre régime n'a cette voie.
- *Ce qu'applique la MSA.* Son guide de janvier 2020 (réf. 11342) : « au moins
  quatre trimestres si vous étiez non-salarié agricole ; cinq trimestres si
  vous étiez salarié (quatre trimestres si vous êtes né au cours du dernier
  trimestre) ». Aucun exemple chiffré. Son tableau des conditions par
  génération de 2026 ne donne que la règle générale, et ne dit rien du
  non-salarié agricole. Les pages du site national de la MSA n'ont pas
  répondu ; les deux documents viennent de caisses régionales.
- *La rédaction de 2026 ferme-t-elle la voie des cinq trimestres ?* Elle écrit
  « par dérogation à l'article D. 351-1-3 », sans « soit… soit ». La lecture
  n'a rien trouvé qui le tranche : ni circulaire, ni page de la MSA postérieure
  au décret.
- *Le test, vu rouge puis vert*
  (`test_le_non_salarie_agricole_debute_avec_quatre_trimestres_a_son_regime`,
  pour `tests/test_simulateur.py`) : trois aides familiaux devenus chefs
  d'exploitation, quatre trimestres à la fin de l'année de la borne, aucun né
  au dernier trimestre, 172 trimestres cotisés chacun. Né en juin 1965, il
  part en janvier 2026 par la porte des dix-huit ans (172 requis) ; né en
  septembre 1964, en janvier 2025 par la même porte (171 requis) ; né en juin
  1950, en janvier 2010 par celle des dix-sept ans (162 requis, 170
  d'assurance). Le salarié du même parcours n'a pas la porte. Les six motifs
  dans les deux moteurs.
- *La règle.* `entreePrecoce` (`moteur/js/regimes.js`) et son jumeau ouvrent la
  borne à qui a quatre trimestres au régime agricole à la fin de l'année de
  l'anniversaire, sans date : le texte la porte depuis 2004. Ces trimestres
  sont ceux des lignes que le régime reçoit, passés par les trois appels qui
  datent ou ouvrent un départ. Les deux voies restent ouvertes en 2026. Aucun
  des témoins existants ne bouge ; un témoin de plus la couvre, et sans elle
  dans le jumeau Python sa confrontation rougit.
- *Où elle est.* Dans
  `docs/mesures/192/2026-11-12-etape-2-la-regle-et-ses-tests.txt`, un
  correctif que `git apply` rejoue : le code des deux moteurs, le test, le
  témoin. L'arbre de `main` n'en porte rien.

**Pourquoi la règle n'est pas publiée.** L'écart n'est pas un cas étroit.

- *Le cas type de l'exploitant agricole est sur le bord de la règle.* Il naît
  en janvier et s'installe à vingt ans : présent au 1er janvier de l'année de
  ses vingt ans, il a quatre trimestres agricoles à la fin de cette année,
  exactement. La règle lui ouvre la porte des vingt ans. Son départ avance :
  61 ans au lieu de 62 pour les nés de 1955 à 1960, 61 ans et 3 mois au lieu
  de 62 ans et demi en 1962, 62 ans au lieu de 62 ans et 9 mois en 1964 et
  1965, 62 ans au lieu de 63 à partir de 1966. Rien ne change avant 1953.
- *Le calcul qui date les cas types le fait alors partir trop tôt, né en
  1953* : à 60 ans et 8 mois, en octobre 2013, avec 164 trimestres cotisés
  pour 165, et le droit n'est pas ouvert. Posé à la main, il part au début de
  2014, à 61 ans : 160 trimestres à la fin de 2012, quatre en 2013, et les
  quatre de l'année où il cesse. L'âge que le droit propose est une projection
  linéaire, quatre trimestres par an au fil des mois, quand le régime agricole
  valide l'année entière au 1er janvier ; le défaut dormait, aucun exploitant
  type n'ayant eu la carrière longue. Les autres générations partent à un âge
  ouvert, mais l'âge proposé y est jusqu'à six mois trop précoce (60 ans et
  demi pour 61 en 1955).
- *Sept tests de la suite complète se déplacent*, tous verts sur `main` seul,
  régénéré le même jour. Quatre de `tests/test_controle_drees_panorama.py` :
  l'exploitant n'a plus de cohorte qui liquide en 2024 (celle de 1962 part en
  2023, la suivante après 2024), et ses hommes nés en 1953 partent deux ans
  avant ceux de la DREES, et non un. `tests/test_cout.py`, la borne haute :
  0,2048 pour un seuil de 0,2. `tests/test_cout_age_depart.py` : l'exploitant
  de 1955 part à 61 ans, quand l'âge proposé est de 60 ans et demi.
  `tests/test_solde_fusion.py` : l'accueil ne cite plus « des réserves de 6 %
  du PIB ». Un huitième, `tests/test_cycle_de_vie_script.py`, est déjà remis à
  sa valeur dans le correctif. Le coût bouge peu : le cumul passé du
  scénario 2 passe de 2 763 à 2 761 milliards d'euros.

**Ce qui reste, dans l'ordre.**

1. Le calcul qui date les cas types (`pilote.js` et son jumeau,
   `agePropose`) : le test d'abord, l'exploitant de 1953, 61 ans posés à la
   main.
2. Rejouer le correctif, refaire les témoins, et remesurer les sept tests,
   datés.
3. La fiche : la voie dans son intitulé et son effet, l'écart levé.

**Au propriétaire.**

- *Le cas type de l'exploitant agricole.* Le garder tel quel, et la règle lui
  avance son départ d'un an ; ou le recaler, par exemple en l'installant en
  cours d'année, et il garde ses âges. La session recommande de le garder : le
  texte lui ouvre cette porte, et le recaler pour l'éviter cacherait la règle.
  Mais son écart à l'âge que la DREES observe double, et le propriétaire peut
  préférer un cas type moins près du bord.
- *La lecture de la rédaction de 2026.* « Par dérogation à l'article
  D. 351-1-3 » : la voie agricole s'ajoute à la voie générale, comme avant, ou
  la remplace. Le correctif applique la première lecture, et la session la
  recommande : le texte dit qui est tenu pour entré sans dire qu'eux seuls le
  sont ; le régime applique désormais le code de la sécurité sociale, dont
  D. 351-1-3 ; le tableau de la MSA de 2026 donne la règle générale à tous ses
  assurés.
- *Une limite, à dire quand la règle sera publiée.* La porte s'ouvrira pour
  tous les régimes de la carrière, qui n'a qu'un départ, quand D. 732-40 ne
  règle que la pension du régime agricole.
