# La carte des fiches : le code des fonctionnaires, des régimes spéciaux, des marins et des mines, écrit

**La demande.** Vague du 28 octobre 2026 : le propriétaire demande une session
par tâche qui se mène sans lui ; la session de suivi ouvre celle-ci après les
trois premiers lots, onze, douze et onze fiches. Celle-ci, de l'action 130 : le
lot suivant des 23 fiches tirées du registre de veille qui n'avaient ni code ni
régimes (note `130/2026-10-28-carte-des-fiches-liberaux-et-independants.md`),
les dix des fonctionnaires, des régimes spéciaux, des marins et des mines.
Aucun chiffre du modèle ne bouge : seuls changent les champs `code` et
`regimes` de dix fiches, et un test.

## Ce qui est fait

- **Le test d'abord** : `CODE_ET_REGIMES_ECRITS` (`tests/test_carte.py`)
  grandit des dix, vu rouge de dix fiches, deux champs chacune, puis vert ;
  leur code, `test_le_code_de_chaque_fiche_tient` le confronte au dépôt.
- **Les dix fiches.** Le RAFP : ses bénéficiaires, que le routage tient hors
  des ouvriers de l'État (`Affiliations.regimes`), et le plafond de ses primes
  au cinquième du seul traitement, dans le scénario 1 comme dans le compte
  notionnel (`PeriodeRegime.part_du_revenu`). La fermeture de la caisse du
  CESE au 1er septembre 2023 (`Affiliations._periode`, `releve_par`,
  `statutFerme`). L'interpénétration des trois régimes du code des pensions
  (`regimes_interpenetres`, `groupes_de_succession`, `droit_a_pension`) et le
  rétablissement au régime général et à l'Ircantec (`retablir`, `regimes_de`,
  `ServicesOuvrantPension`). Le minimum garanti : ses services, sa condition
  de taux plein et sa minoration, son d sous quinze ans, son barème et sa
  référence (`EligibleMinimumGaranti`, `MinimumGaranti.montant`, `completer`).
  Les marins : l'ouverture à cinquante ans, le plafond de vingt-cinq annuités
  et sa levée (`ouverture_par_services`, `liquider_chaque_regime`), le forfait
  de la catégorie (`assiette_de_reference`, `SalairesForfaitaires.forfait`).
  Les mines : le plafond de cent vingt trimestres, le barème du trimestre et
  l'âge du fond (`acquerir`, `BaremesTrimestre.valeurs`). La fiche commune des
  fermetures de 2023 et des réformes de 2023 à 2026, que portent le routage et
  les périodes des fiches de régime (`Regime.periode`, `reformes_non_portees`).
- **Le champ `regimes`**, lu à la règle et au code, aucune de ces fiches
  n'étant nommée par un interrupteur : le RAFP et le FSPOEIE pour ses
  bénéficiaires ; la caisse du Conseil, le régime général et l'Ircantec pour
  le CESE ; les trois régimes du code des pensions et les pensions civiles
  d'avant 1948, que le code compte avec l'État, pour l'interpénétration ; pour
  le rétablissement, les régimes rétablis (`REGIMES_RETABLIS`, la SEITA
  comprise) et ceux qui reçoivent leurs années, le régime général, l'Ircantec,
  ses devancières de 1951 et de 1959 et les assurances sociales d'avant 1945 ;
  pour le minimum garanti, les quatre régimes dont les périodes le déclarent,
  la Banque de France comprise, que le code sert au même barème ; pour la
  fiche commune, les dix-sept régimes que ses réformes touchent et les cinq
  que 2023 ferme. La carte passe de 679 manques à 659 ; ses 106 fiches à mûrir
  restent.
- **Les tests nommés**, relevés par une sonde de session, hors du dépôt : dans
  une copie du dépôt, au paquet du site refait, chaque règle neutralisée tour à
  tour par un interrupteur d'environnement dans les deux moteurs, vingt et une
  neutralisations pour dix fiches — le minimum garanti et les marins en quatre
  chacun, les mines en trois, le RAFP et le CESE en deux, les fermetures de
  2023 à part, les réformes de la fiche commune en trois groupes de régimes
  ramenés à leur période d'avant la première — ; la suite rapide, seize
  fichiers des oracles et des contrôles, ceux des données et de la règle de
  chacun, les deux tests du site sur les statuts fermés, pour les règles des
  fonctionnaires ceux de TRAJECTOiRE, du jaune pensions et des mères, et, sans
  le minimum, le rétablissement ou l'interpénétration, les deux du coût des
  avantages, rejoués ; les 912 témoins en Python, comparés au Python non
  neutralisé ; puis, la règle neutralisée dans le seul Python, les 188 tests
  qui confrontent les deux moteurs, ceux que `tests/conftest.py` reconnaît au
  portage (`_confronte_au_portage`). Changent, dans le scénario 1, sept
  témoins sans la règle des ouvriers de l'État, neuf sans le plafond du RAFP,
  quatre sans l'interpénétration, cinq sans le rétablissement, deux sans le
  minimum garanti et un sans son d, huit sans l'ouverture des marins à
  cinquante ans, neuf sans leur forfait, un sans leur plafond de vingt-cinq
  annuités, sept sans le plafond ou l'ouverture des mines et six sans leur
  barème, 49 sans les réformes des libéraux, neuf sans celles de la MSA et du
  RAFEP, quatorze sans celles d'outre-mer ; aucun sans la levée du plafond des
  marins, la condition de taux plein ou le décompte des services du minimum,
  la fermeture du CESE ou son renvoi à l'agent non titulaire. Les fiches
  nomment ces témoins (`tests/temoins/simulations.json`), que le portage
  rejoue (`tests/js/moteur.test.js`), et, à part, les tests qui ne tombent que
  parce qu'ils confrontent les deux moteurs sur des carrières qui portent la
  règle. Au coût des avantages, seul le minimum garanti fait tomber un test.
- **Ce que la sonde a montré hors du scénario 1**, que les fiches disent sans
  le trancher. Le compte notionnel demande au routage, sans la date d'entrée,
  si une ligne a un employeur (`ConstructeurCompte.a_un_employeur`) : le membre
  du CESE entré avant septembre 2023 en gagne un pour ses années depuis 2024,
  celles du régime général et de l'Ircantec, quand le scénario 1 le garde à la
  caisse du Conseil ; un commentaire du code tient que l'année d'entrée « ne
  change rien », et la fermeture du CESE le dément. Les trois témoins des
  membres du CESE ne bougent que là, sans sa fermeture comme sans celles de
  2023. Le régime fusionné de la proposition prend l'âge du taux plein le plus
  élevé des régimes : Mayotte ramenée d'avant 2026 le porte de 67 à 69 ans, et
  896 témoins de plus ne bougent que par lui ; vingt et un tests qui
  confrontent les deux moteurs tombent par la même voie, que la fiche commune
  ne nomme pas. L'avenant 17 de l'Agirc-Arrco ne change rien : le modèle ne
  porte pas les coefficients de solidarité qu'il supprime.
- **Les trous, que les fiches disent.** Aucun cas posé à la main ne tient le
  décompte des services du minimum garanti, arrondis au décompte final et sans
  les bonifications : seuls tombent sans lui trois tests qui confrontent les
  deux moteurs. La levée du plafond des marins à cinquante-deux ans et demi
  n'a qu'un test, `test_les_ages_des_marins_suivent_la_duree_de_leurs_services`,
  et aucun témoin. Aucun cas ne bâtit la carrière d'un membre du CESE entré
  depuis septembre 2023, que la saisie refuse : seul `tests/test_donnees.py`
  tient son routage, et son renvoi à l'agent non titulaire. Les fermetures de
  2023 n'ont aucun témoin du scénario 1.

L'écriture s'est faite par un outil de session, hors du dépôt, qui a vérifié
qu'aucun autre champ ne bougeait. Les phrases `moteur` disent ce que le code
fait, relu fonction par fonction. L'étape n'écrit aucune règle du scénario 1 :
ni veille, ni entrée au journal. Rien n'est dû aux pages. Dans le clone de la
session, sept tests qui confrontent les deux moteurs tombent dans la suite
rapide, avec ou sans l'étape : son paquet du site datait d'avant les derniers
envois, et GitHub le refait avant la suite.

## Ce que l'étape laisse

- 13 fiches sans code ni régimes — 9 conformes, 2 approchées, une
  transcrite, une à vérifier —, celles du régime général, des durées, des
  minima et des paramètres, et trois sans régimes
  (`inaptitude_invalidite_penibilite_amiante`, `micro_social_abattement`,
  `rachats_et_versements`) : le dernier lot, qui entre à
  `CODE_ET_REGIMES_ECRITS`.
- Pour une session du modèle : la date d'entrée que
  `ConstructeurCompte.a_un_employeur` ne lit pas, pour le CESE ; un cas posé à
  la main pour le décompte des services du minimum garanti, et un témoin pour
  la levée du plafond des marins.
- Pour la proposition, une observation : son régime fusionné tient l'âge du
  taux plein de tous les régimes, Mayotte compris, dont la réforme de 2026 l'a
  ramené de 69 à 67 ans.
- `pension_non_salaries_agricoles_2026`, seule fiche de `EN_PROSE`, à la session
  de l'action 131 ; les 106 fiches à lire au droit, et les points ouverts des
  phases 2 à 8.

## Ce qui attend le propriétaire

Rien de neuf : la septième étape du sixième domaine, la décision de la
proposition, et celle sur la retraite progressive, le cumul et la seconde
pension, README muet.
