# Étape 1 : le temps partiel des fonctionnaires et le départ des parents de trois enfants, confrontés à OpenFisca

**Le 13 octobre 2026, la demande.** Le propriétaire : « Je lance l'action 153,
à faire jusqu'ici : la première famille de profils (le temps partiel des
fonctionnaires et le départ anticipé des parents de trois enfants), avec sa
convention de traduction écrite. Ne signale rien à OpenFisca : j'en
déciderai. » En parallèle, l'action 152 tient `castypes.py`,
`cas_types_csp.yaml` et `grille_large.py`, l'action 147 `cout.py`, une session
`pages.js` et `index.html` : aucun n'est touché, et ce qui irait aux pages est
plus bas.

**Ce qui a été lu.** OpenFisca-France-Pension 0.1.3, la version des témoins
existants (commit `1c45423`), installé à part dans un environnement jetable,
hors du dépôt : le code de sa fonction publique — la quotité
(`duree_assurance_annuelle`), le départ des parents
(`date_satisfaction_condition_…`, `aod_egal_…`, `depart_anticipe_trois_enfants`,
`decote_a_date_…`, `decote_trimestres`), la proratisation — et ses tests
`parent_trois_enfants.yml`. Dans l'index LEGI, à jour au 11 octobre :
l'article 66 de la loi n° 2003-775 (II, la durée, et III, la décote, selon
l'« Année au cours de laquelle sont réunies les conditions mentionnées au I et
au II de l'article L. 24 ») ; son article 5, VI, dans ses rédactions de 2006,
2009 et 2010 ; L. 24 en vigueur du 28 juin 2006 au 1er juillet 2011
(LEGIARTI000006362730) ; L. 5 en 1991 et en 2004 ; l'article 44 de la loi
n° 2010-1330, III et IV.

**La convention de traduction**, écrite en tête du script qui fige le témoin
(`scripts/fetch/openfisca_temps_partiel_et_parents.py`) et portée par le
témoin, avec les entrées qu'OpenFisca a reçues pour chaque profil ; le test la
vérifie avant toute comparaison.

- *La carrière* : celle du premier oracle de la fonction publique — née un
  1er janvier, entrée un 1er janvier, traitement nominal constant, sans prime,
  sédentaire, liquidée au 1er janvier.
- *Le temps partiel* : au dépôt, des années entières et leur quotité, comme le
  formulaire les saisit ; la ligne porte la quotité et le traitement réduit.
  OpenFisca reçoit les services eux-mêmes, quatre trimestres fois la quotité,
  et la quotité, dont il retrouve la durée d'assurance en les divisant ; et le
  traitement à temps plein, d'où il tire l'indice (L. 15).
- *Les enfants* : au dépôt, des naissances datées ; OpenFisca n'en lit qu'un
  nombre, une date — celle du troisième enfant —, et le nombre de ceux nés
  avant 2004. Toutes tombent pendant les services.
- *Ce qui ne se traduit pas* : l'interruption d'activité pour chaque enfant,
  qu'OpenFisca ne lit pas et que le dépôt présume de la mère seule ; la
  demande d'avant 2011, que le dépôt présume. La raison du départ n'est pas
  déclarée, sauf à un profil qui montre ce qu'elle fait. Seule l'année des
  quinze ans se compare : OpenFisca les date du 1er janvier.

**Ce qui est fait.**

- *Le témoin*, `tests/temoins/openfisca_temps_partiel_et_parents.json` :
  quatorze profils, liquidés de 2010 à 2018 — six fonctionnaires à temps
  partiel sans enfant (dix ans à 80 %, cinq à mi-temps à la CNRACL, trois à
  70 %, à 80 % jusqu'au départ, au minimum garanti, à 90 % pendant la
  surcote), sept mères de trois enfants et un père.
- *Les tests*, `tests/test_oracle_familles.py`, au niveau des contrôles
  (`conftest.py`) : quinze, la convention d'abord, puis chaque grandeur ; un
  écart connu y est déclaré avec son texte, et chaque modèle rend ce que sa
  règle commande (`ANNEES_DES_PARENTS`, `DUREE_DE_L_ANNEE`, `DEPARTS`).
- *Le registre* (`referents.yaml`) : quatre écarts de plus à
  OpenFisca-France-Pension, tranchés ; la vérification des deux points repris
  (136.3 et 138.17), le point 153.2 dit ce qui est fait, le bilan, le
  manifeste, `lu_le`. Le manifeste des sources a sa ligne
  (`openfisca_temps_partiel_et_parents_oracle`), les deux fiches leur bloc
  `referents`, et les limites (`3-systeme-actuel.md`) un paragraphe ; trois
  chiffres ancrés suivent (48 profils confrontés devenus 62, 209 jeux de
  sources devenus 210).

**Ce que la confrontation a trouvé.**

- *Le temps partiel : rien à corriger.* Durée, services, décote, surcote,
  traitement et pension tombent au centime sur les six profils. Trois ans à
  70 % font 8,4 trimestres, arrondis une fois des deux côtés (148, et non 149).
  À 80 % jusqu'au départ, les deux liquident le traitement à temps plein. Le
  minimum garanti lit des deux côtés les services réduits : le rapport de ses
  deux montants, 1,03819, est celui de la carrière à temps plein liquidée la
  même année (`minimum_garanti_1946`), à 5·10⁻⁸ près — le point 4 de l'action
  154 est vérifié.
- *Le départ des parents : quatre écarts, tous chez OpenFisca.* L'année des
  conditions réunies, le barème et l'âge d'annulation de sa décote, la
  bonification de L. 12, b, et la majoration de L. 18 concordent ; ce qui
  diffère, avant la majoration :

  | profil | le dépôt : année, durée, taux, pension | OpenFisca | ce qui tranche |
  |---|---|---|---|
  | mère, conditions en 1992 | 1992, 150, 75 %, 21 707,99 € | 1992, 165, 75 %, 19 734,53 € | article 66, II |
  | CNRACL, conditions en 2007 | 2007, 158, 71,25 %, 10 278,66 € | 2007, 165, 71,25 %, 9 842,60 € | article 66, II |
  | mère, conditions en 2009 | 2009, 161, 67,5 %, 9 286,57 € | 2009, 165, 67,5 %, 9 061,44 € | article 5, VI |
  | dix ans à 80 % avant ses quinze ans | 2004, 152, 75 %, 12 218,68 € | 2006, 165, 73,125 %, 10 974,59 € | L. 5 |
  | CNRACL, née en 1962, partie en 2011 | 2004, 152, 75 %, 12 377,36 € | départ fermé : 2022, 165, 56,25 %, 8 551,63 € | L. 24, I, 3° ; article 44, IV, 1° |
  | partie en 2012 | 2016, 166, 56,25 %, 14 231,93 € | départ fermé ; la même pension | article 44, III |
  | la même, raison « famille » | 2016, 166, 56,25 %, 14 231,93 € | 2012, 166, 61,875 %, 15 655,12 € | article 44, IV |
  | le père | départ non ouvert | 1992, 165, 75 %, 18 089,99 € | l'interruption d'activité |

  OpenFisca proratise toujours sur la durée de la génération, quand la loi
  prend celle de l'année des conditions ; avant juillet 2011, il ferme le
  départ à qui n'atteint pas son âge d'ouverture avant 2016 et n'a pas réuni
  les conditions avant 2003, une condition que L. 24, I, 3°, n'écrit pas ;
  après juin 2011, il ne le sert qu'à la raison « famille », qu'il date du
  départ ; et il compte les quinze ans sur les services réduits. Le père n'est
  pas un écart : OpenFisca ne lit pas l'interruption d'activité, le dépôt la
  présume de la mère seule — une limite de la traduction, que la fiche déclare.
  L'oracle a donc trouvé onze erreurs chez OpenFisca, sept avant cette étape.

**Ce qui ne bouge pas.** Aucun résultat, aucun moteur, aucune page, aucune
fiche de droit dans ses règles : le modèle avait raison sur chaque point
confronté. Aucun signalement à OpenFisca.

**Vu en passant, pour les familles suivantes.** Le minimum garanti de la
CNRACL vaut zéro chez OpenFisca : sa formule lit les services de l'État
(`fonction_publique_duree_de_service_effective`), nuls pour un agent de la
CNRACL — à trancher avec la famille des minima. Sa majoration de durée des
enfants nés après 2004, à la CNRACL, lit de même la date de liquidation de
l'État : à la famille des enfants.

**Ce qui devrait s'écrire dans les pages**, que cette session ne touche pas :
rien n'y devient faux, puisqu'aucun résultat ne bouge, et elles ne citent
OpenFisca qu'en termes généraux. Au plus, dans « Comment ce site est construit,
et comment on le vérifie » (`methodeConstruction`, `pages.js`), la phrase sur
les « calculateurs extérieurs comme OpenFisca, qui servent d'oracle au
système 1 » pourrait dire qu'ils confrontent aussi, depuis le 13 octobre 2026,
le temps partiel des fonctionnaires et le départ des parents de trois enfants.
Le motif d'ouverture « parent de trois enfants », que le site dit encore
« âge légal », reste le point de l'action 138 (étape 17).

**Ce qui reste.** L'étape 2, une famille par session, chacune avec sa
convention : d'abord les enfants — la bonification et la majoration de durée
au-delà de trois enfants, nés après 2004 ou hors des services, le père —,
puis la catégorie active, la carrière longue de la fonction publique, les
minima, la minoration de l'Arrco, les périodes assimilées, le salaire annuel
moyen sur des salaires qui varient. Le propriétaire tranche le signalement à
OpenFisca, de onze erreurs désormais.
