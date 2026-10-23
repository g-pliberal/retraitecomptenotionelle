# Feuille de route — les actions qui font le plus progresser le modèle

Ce fichier est la liste des chantiers à mener, classés par ce qu'ils déplacent
dans les résultats du dépôt. Il sert de point d'entrée à une session de travail :
prendre l'action la plus haute qui n'est pas commencée, la mener au bout, puis
mettre à jour ce fichier. *Précisé le 23 septembre 2026* : aucune action n'est
plus « à faire », la liste s'allongeant par la fin à mesure que les sessions
ouvrent les leurs ; une session commence donc par les actions `en cours` et ce
que leurs dernières notes laissent ouvert. *Précisé le 27 septembre 2026* : une
action peut de nouveau naître « à faire », quand le propriétaire l'ouvre pour
plus tard ; elle attend qu'il la lance, et une session ne la prend pas
d'elle-même. Deux numéros servent deux fois,
37 et 38 : chaque paire se distingue par son titre, et les renvois du dépôt
nomment l'une ou l'autre. Il ne remplace ni `limites.md`, qui dit ce que vaut
chaque chiffre, ni `regimes.md`, journal de la campagne sur les régimes.

**Comment le tenir.** Une action a un état — `à faire`, `en cours`, `fait` — et
une ligne « ce que ça a déplacé » quand elle est faite, comme les tranches de
`regimes.md`. Toute session qui touche au scénario 1 commence par
`python scripts/veille_droit.py` et finit par une entrée au journal de veille,
un fichier à elle sous `data/reference/legislation/journal_de_veille/` : voir
`docs/veille_droit.md`. Une action qu'on abandonne ne disparaît pas : elle passe en bas,
avec la raison, et l'action elle-même dans l'archive. Une découverte faite en chemin qui mérite un chantier se note
ici, pas dans un commentaire de code.

**Le constat de septembre 2026, qui fonde ce classement.** La couverture des
régimes est finie : <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire)-->114<!--/--> lignes d'inventaire,
<!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=partiel)-->44<!--/--> fiches partielles dont chaque mur est documenté dans `regimes.md` et
`limites.md` §4, et <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=a_modeliser)-->9<!--/--> lignes « à modéliser » — aucune en
septembre, celles-ci rouvertes le 4 octobre par l'action 145 pour des régimes
que l'inventaire ne nommait pas, documentés et non calculés. Continuer sur cet axe rapporte peu : les manques restants
portent sur des populations minuscules ou des barèmes que personne ne publie.
Les gains sont sur ce qui porte les résultats de tête du README : les agrégats
de la page Coût, la part patronale, les taux de cotisation qui sont la matière
même des scénarios notionnels, et l'étalon qu'est le scénario 1.

Un coût transversal pèse sur l'ordre : chaque changement du MODÈLE se paie deux
fois, dans `src/retraite_notionnelle/scenarios/actuel.py`
et dans le portage `moteur/js/`, puis dans les témoins ; leur taille
s'affiche par `python scripts/tableau_de_bord.py --cout`. Les actions 1 à 3 et 6 n'ont touché que les données et la page Coût ;
les actions 7, 9, 10 et 11 ont touché les deux moteurs, comme l'action 5, et
l'action 4 ne les a touchés qu'en surface — deux lignes de chaque côté.
L'action 13 n'a pas touché le modèle du tout : un script de certification, le
format de son journal, et une phrase de la page Données en deux exemplaires.
Toutes sont faites ; ce paragraphe, écrit quand elles étaient à mener, est
passé au passé le 23 septembre 2026.

**Les actions closes sont dans l'archive**, `docs/archives/feuille_de_route.md`,
avec le journal : faites, archivées ou abandonnées, elles y gardent leur
numéro, leur texte et leur ordre (`docs/architecture.md`, § 9.3). Ce fichier
ne garde que ce qui vit : ce qui est délibérément en bas, les actions
`à faire`, et les actions `en cours`, à la fin, où les sessions ouvrent les
leurs. Une action qui se clôt passe, telle quelle, à la fin de l'archive ; un
test refuse une action close ici, ou ouverte là-bas.

**Les notes, une par fichier.** Depuis le 6 octobre 2026 (action 148), une
session n'écrit plus sa note ici : elle l'écrit dans un fichier à elle,
`docs/feuille_de_route/<action>/<AAAA-MM-JJ>-<sujet>.md`, qui s'ouvre sur son
titre. Ce fichier ne garde, de chaque action ouverte, que son titre, son bloc
« Reprise », sa demande, son plan, et les notes écrites avant cette date.
Quand les étapes d'une action se mènent en parallèle, son bloc le dit, et
chaque étape inachevée tient le sien sous le titre de sa note : deux sessions
n'écrivent jamais dans le même fichier. `python scripts/reprise.py` imprime
tous ces blocs. Une action close emporte le dossier de ses notes sous
`docs/archives/feuille_de_route/`, où elles sont gelées.

---

## Ce qui est délibérément en bas

- **Les 37 fiches partielles.** Chaque mur est documenté dans `regimes.md` ;
  les populations sont petites ; reprendre un mur ne se justifie que si une
  source nouvelle apparaît (règlement du port de Strasbourg, grille des marins
  d'avant 2008, barème de l'UNIRS par institution).
- **Les éventails d'incertitude.** Les seize autres scénarios de l'INSEE et les
  deux variantes du COR (déjà dans `hypotheses_projection.yaml`) donneraient un
  éventail à la trajectoire 2025-2070. Utile, mais ne change aucun chiffre
  central.
- **La réversion.** Hors périmètre par construction : le modèle décrit une
  carrière, pas un ménage. À noter tout de même que la dépense DREES comparée
  sur la page Coût inclut la survie ; l'écart de périmètre est dit, pas corrigé.
  L'action 35 en reprend la moitié qui ne demande pas de ménage : ventiler la
  base en droits directs et dérivés au seul niveau de l'agrégat, et dire ce que
  le scénario 6 fait de la réversion. Modéliser une pension de réversion reste
  en bas.
- **Piloter l'agrégat par le coefficient d'équilibre** — l'action 11,
  archivée le 20 septembre 2026. Un système notionnel réel ne laisse pas
  dormir un excédent : il relève les pensions jusqu'à l'équilibre, ou les
  abaisse, par un facteur commun à toutes les pensions de l'année et un fonds
  de réserve qui lisse. Le dépôt CALCULE ce facteur ; il ne l'applique pas, et
  les courbes de la page Coût restent celles d'un système qui ne se pilote pas.

  *Pourquoi c'est en bas.* Un facteur commun ne déplace aucun écart entre
  carrières. L'appliquer changerait tous les niveaux de la page Coût et rien de
  ce que le site mesure ailleurs, qui est la comparaison de quatre systèmes sur
  une même carrière. Ce qui manquait vraiment n'était pas le pilotage mais la
  LECTURE : que le visiteur voie, à côté de la pension que la loi promet, ce
  que les recettes en paient. C'est l'action 62, faite.

  *Ce qu'il faudrait pour la reprendre.* Rien à récupérer, tout est là. Le
  mécanisme se décrit en revanche : le coefficient suédois (`balansindex`),
  qui n'ajuste que le dénominateur du ratio actif/passif, et le coefficient
  italien, qui indexe le capital notionnel sur le PIB, ne font pas la même
  chose. Les deux sont au manifeste sous `cor_retour_septieme_rapport` — les
  documents 5 à 7 de la séance du 5 juillet 2017, avec au document 4 la
  maquette du secrétariat général, qui chiffre ce que le mécanisme évite : sur
  un choc démographique permanent, des déficits transitoires de l'ordre de
  10 % de la masse des cotisations contre près de 90 % en annuités et en
  points. Les fichiers : `src/retraite_notionnelle/cout.py`, les moteurs de
  pension si l'ajustement doit porter sur la pension individuelle,
  `moteur/js/` en regard, les témoins, `limites.md` §5.

  *Ce que l'archivage laisse ouvert, et il faut le dire.* Trois phrases du
  site promettent ce pilotage — « L'écart se solde chaque année », « Le chiffre
  qui ramène l'année à zéro est publié et appliqué chaque année », « Dépenser
  moins n'est pas économiser ». Elles sont au catalogue des affirmations à
  l'état `contredite`, sous cette action : le modèle ne fait pas ce qu'elles
  annoncent, et plus rien n'est programmé pour l'y amener. Le programme peut
  le promettre — c'est une proposition politique, pas une description du
  modèle —, mais le dépôt ne le simule pas, et c'est le catalogue qui tient
  cet écart visible.

- **Convertir les droits acquis à l'âge de départ effectif** — l'action 24,
  abandonnée le 19 septembre 2026. Elle demandait que les droits d'avant la
  bascule soient convertis en capital au diviseur de l'âge où l'assuré part
  vraiment, et non à celui de l'âge de référence. La mesure l'a réfutée.

  *Ce que le réglage ferait.* Les droits acquis sont une pension annuelle ; la
  convertir en capital demande un âge, et c'est le seul rôle de ce réglage.
  Pour un même passé — carrière témoin née en 1975, homme, salarié du privé non
  cadre entré à 21 ans au salaire moyen et à profil plat, donc trente années
  cotisées avant 2026 et un droit figé de 18 683 € par an —, le défaut actuel
  constitue un pot de 459 467 € quel que soit l'âge de départ. Le réglage proposé en constituerait **526 244 € pour un départ à
  60 ans et 411 567 € pour un départ à 67 ans**. Le même passé vaudrait donc
  28 % de plus à qui arrête plus tôt, ce qui n'a pas de sens : le passé est le
  même.

  *Ce que ça casse.* Le pot rétrécissant avec l'âge à peu près au rythme où les
  cotisations nouvelles le remplissent — au privé, −47 900 € de pot contre
  +53 931 € de versements entre 60 et 67 ans —, les deux s'annulent. Sept
  années de travail supplémentaires ne feraient plus monter le capital total
  que de **0,8 %** (1,6 % sur une carrière publique), contre 26 % aujourd'hui,
  et la pension de 25 % au lieu de 56 %. Un compte notionnel promet qu'on
  retrouve ce qu'on verse ; le réglage romprait cette promesse sur la part
  venue du passé, et d'autant plus fort que cette part est lourde — c'est-à-dire
  pour les générations de transition, les premières concernées.

  *Et il rétablirait ce que le dépôt critique.* `limites.md` chiffre à
  23,7 milliards en 2024 les annuités servies avant l'âge légal, et les range
  parmi les avantages non contributifs que les comptes notionnels suppriment.
  Un capital majoré pour qui part tôt est le même mécanisme, financé par les
  autres.

  *Ce qui n'entre pas dans la balance, vérifié.* Le pilier capitalisé de 5 %
  n'appartient qu'au scénario 6, qui est rétroactif et ne fige aucun droit : la
  convention lui est indifférente au centime, à tout âge de départ. Le RAFP est
  servi à l'identique par les six scénarios et ne départage rien. Le réglage
  `liquidation` reste disponible en variante, pour que la mesure soit
  reproductible.

- **Porter les contributions d'équilibre de l'Agirc-Arrco au compte
  notionnel** — l'action 140, abandonnée le 2 octobre 2026 à la demande du
  propriétaire : « je ne veux pas prendre les contributions d'équilibre ; ce
  ne sont pas des cotisations ».

  *Pourquoi c'est en bas.* Le compte reçoit les cotisations, et toutes leurs
  parts, même celles qui n'ouvrent aucun droit : la majoration du taux d'appel
  de l'Agirc-Arrco, la cotisation déplafonnée du régime général. La
  contribution d'équilibre général et la contribution d'équilibre technique,
  l'AGFF et l'ASF avant elles, ne sont pas des cotisations : ce sont des
  contributions, que l'accord du 17 novembre 2017 institue « dans une
  perspective de financement des opérations du régime » (article 37), la
  première « afin de financer plus particulièrement les charges d'anticipation
  du régime ». La frontière passe donc entre la cotisation et la contribution,
  et non entre ce qui ouvre des droits et ce qui n'en ouvre pas. Le taux du régime unique les
  omet de même : 25,83 %, la somme des cotisations du statut pivot.

  *Ce qu'il faudrait pour la reprendre.* Une décision contraire du
  propriétaire ; puis les taux, année par année, que l'action 140 énumère dans
  l'archive.

---

## Les actions à faire

### 134. Les lignes d'un mois : ce que le pas annuel fait d'un départ au 1er février — `à faire`

**D'où elle vient.** L'action 132 a fait partir la pension au premier du
mois qui suit l'anniversaire, et présumé le 15 le jour qu'on ne dit pas. Un
cas type né en janvier part donc au 1er février, et l'année de son départ
compte un mois. Le moteur, dont le pas est l'année, traite parfois cette
ligne d'un mois comme une année. Rien de ceci n'est né de l'action : tout
départ hors de janvier le subissait déjà ; la convention du 1er le cachait
aux cas types, qui naissent en janvier.

**Ce qui est à regarder**, chacun à sa fiche :

1. Le traitement de référence de la fonction publique, lu sur la ligne de
   l'année du départ dès qu'elle compte un mois : partir le 1er février
   plutôt que le 1er janvier 2044 le relève d'une année de croissance, soit
   quatre points de pension pour le militaire de la génération 2000, et
   partir le 1er février 2020 l'abaisse de 2,65 %, le salaire moyen ayant
   baissé cette année-là (témoin `reversion_fonctionnaire`). Le droit lit le
   traitement des six derniers mois.
2. Les points de la RCO : une ligne d'un mois reçoit le minimum annuel de
   l'assiette. Lire la règle de l'année de la cessation (D. 732-155 et la
   MSA).
3. La contiguïté d'un relevé au départ (`Carriere.prolongee`) : un relevé qui
   s'arrête à l'année d'avant n'est contigu que si le départ tombe en
   janvier, et la proposition ne prolonge pas les autres — le témoin
   `releve_deux_statuts` y a perdu 2,31 % au scénario 6. Réglé pour le site
   le 4 octobre 2026 (action 142, étape 3, suite) : le relevé y est prolongé
   jusqu'au départ, ses mois compris, et le témoin regagne 2,53 %.
4. La fenêtre de la surcote parentale, datée au mois : elle chevauche l'année
   du départ, qui ne valide que ses trimestres civils écoulés, et perd un
   trimestre deux mois de naissance sur trois. Chercher la circulaire qui
   l'applique ; aucun texte lu ne la découpe.
5. Le plafond aux trimestres civils écoulés que le moteur oppose à l'année
   d'entrée, que R. 351-9 n'écrit pas.

**Ce que le propriétaire tranche** : s'il faut les corriger une à une, ou
faire naître les cas types un autre jour que le 15 de janvier. Rien n'est
commencé.

### 143. La même carrière, née une autre année : une page qui compare les générations — `à faire`

**Demande**, le 4 octobre 2026 : « Je veux que tu crées une page avec une
comparaison entre années de naissance. Je veux qu'avec cette page les gens se
rendent compte de la différence de traitement en fonction de l'année de
naissance. Il faut un comparateur pour des cas égaux qui différencient
uniquement l'année de naissance. Il faut aussi des statistiques qui montrent
les différences entre les années de naissance. Il faut que l'on puisse voir
les nombres d'années à travailler, l'âge de départ à la retraite, le cumul net
de l'argent reçu au cours de la vie, le nombre d'heures travaillées au cours
de la vie, etc. » Puis : « Je veux juste que tu documentes pour l'instant. »
Elle naît `à faire` : elle attend que le propriétaire la lance.

**Ce que le site en montre déjà, épars.** La page Carrières types croise
treize carrières et sept générations (`GENERATIONS`, 1940 à 2000, de dix en
dix), mais chaque case y rapporte un système à un autre pour une même
génération : elle compare des systèmes, non des générations ; son dépliant
« À quel âge chacun part » donne pourtant l'âge de liquidation de chaque cas
type par génération. Le dépliant « Ce que chaque système finit par verser »,
au bas des résultats du simulateur, cumule une pension jusqu'à 105 ans, en
euros constants, avec la part de la génération encore en vie à chaque âge.
La page Pourquoi changer cite, dans « Les jeunes cotisent plus pour recevoir
moins », le rendement interne par génération de Dubois et Marino (INSEE,
2015) et celui du COR. Aucun de ces morceaux ne met deux années de naissance
côte à côte.

**« Des cas égaux » : ce qui reste fixe, ce qui bouge.** Un cas type
(`castypes.CasType`) est déjà « une carrière de référence, indépendante de la
génération » : un âge d'entrée, un salaire en multiples du salaire moyen de
chaque année, un profil par âge, un sexe, des enfants, un statut, des
interruptions au même âge. Le comparateur fixe tout cela et ne change que
l'année de naissance. Ce qui bouge est ce que la page veut montrer : le droit
de chaque génération (âge légal, durée requise, décote, taux de cotisation,
revalorisations, fermeture d'un régime spécial), les salaires et les prix
qu'elle traverse, sa mortalité. Le départ suit la règle du cas type, que le
pilote résout sous le droit de chaque génération (`pilote.age_de_depart`,
variante `droit`) ; la variante `absolu`, qui fait partir toutes les
générations à l'âge écrit du cas type, isole ce que la pension doit au seul
barème. Pour les générations qui ne sont pas parties, le droit est celui
d'aujourd'hui, appliqué tel qu'il est écrit, et le contexte celui des
projections : la page le dit à chaque génération. Ce qu'elle ne fait pas
varier, et doit le dire aussi : les comportements — études plus longues,
chômage, temps partiel —, qui séparent les générations réelles. La partie
statistique les montre.

**Les indicateurs, et ce que le modèle en sait le 4 octobre 2026.**

1. **L'âge de départ** : calculé, par le pilote ; l'âge légal et l'âge
   d'annulation de la décote sont des tables par génération
   (`age_ouverture_requis.csv`, `age_annulation_decote.csv`).
2. **Les années à travailler**, deux grandeurs à ne pas confondre : la durée
   requise pour le taux plein, par génération (`duree_assurance_requise.csv`),
   et les années que le cas type travaille vraiment, que sa carrière porte.
3. **Les heures travaillées sur la vie** : aucune série d'heures au dépôt.
   Deux voies, qui ne disent pas la même chose. Les heures LÉGALES — durée
   hebdomadaire, congés payés, jours fériés chômés, selon les textes qui les
   fixent depuis 1936, à lire sur Légifrance avant toute valeur — sont la
   règle, dans la logique du scénario 1. Les heures EFFECTIVES — comptes
   nationaux de l'INSEE, enquêtes de la DARES — sont le fait. Le dépôt
   télécharge déjà la croissance de la productivité horaire (idbank
   011793337, `scripts/fetch/insee_bdm.py`) à côté de la productivité par
   tête : leur rapport donne l'évolution des heures par emploi, non leur
   niveau, et temps partiel compris. L'indicateur ne se choisit pas pour sa
   conclusion : à âge d'entrée égal, les générations anciennes ont fait des
   semaines plus longues et des carrières plus courtes, et la page montre ce
   que la série dit.
4. **Les années de retraite** : l'espérance de vie à l'âge de départ, sur la
   table de génération (`esperance_residuelle`), par sexe ; calculée. Elle
   donne la part de la vie passée à la retraite, et les années de retraite par
   année travaillée.
5. **La pension** : brute au départ, calculée, avec le taux de remplacement ;
   nette, convertie par le site à un taux unique, le taux plein d'aujourd'hui
   (9,10 %).
6. **Le cumul reçu sur la vie** : la pension sommée sur la survie de la
   génération, en euros constants, comme le cumul des résultats. Brut,
   calculé. Net, c'est un trou : `limites.md` admet le taux d'aujourd'hui pour
   tous parce qu'il ne déplace aucun écart ENTRE SCÉNARIOS ; entre générations,
   il en déplace, la CSG des pensions et la Casa étant nées ou relevées
   pendant la retraite des générations anciennes. Il faut la série des
   prélèvements sur les pensions — CSG, CRDS, Casa, cotisation maladie —,
   année par année, lue sur Légifrance. Après le départ, le droit pour le
   passé — le dépôt mène déjà une pension liquidée jusqu'à aujourd'hui par
   les textes de chaque régime, contrôlé sur la figure 3.14 du COR —, le
   pouvoir d'achat constant pour l'avenir, convention déclarée.
7. **Les cotisations versées** : le compte qui porte les taux réels de chaque
   régime (`SourceCotisations.TAUX_HISTORIQUES`) les somme déjà
   (`cotisations_versees`), mais en euros courants : à remettre en euros
   constants. Ce qu'un taux contient sans rien acquérir — le taux d'appel des
   complémentaires, la contribution d'équilibre de l'État — se dit, puisqu'il
   pèse sur le rendement.
8. **Le rendement** : ce qu'un euro cotisé rapporte de pension, et le taux de
   rendement interne de la carrière, l'indicateur de référence de l'équité
   entre générations, que le site cite sans le calculer. Il se tire des deux
   flux précédents.

**Le piège des euros.** En euros constants, une pension de la génération 2000
se compare mal à une pension de la génération 1950 : entre-temps les salaires
auront crû, et un écart en euros mêle la croissance au traitement. Les
grandeurs de tête sont donc relatives — âges, années, heures, taux de
remplacement, cumul en années de salaire, rendement —, et les euros viennent
ensuite, dits pour ce qu'ils sont.

**Le « cumul net », deux lectures.** Net des prélèvements sur la pension, ce
qui arrive sur le compte ; ou net de ce qui a été cotisé, ce que la génération
reçoit de plus qu'elle n'a versé. Le revenu net de toute la vie, salaires
compris, n'est pas à portée : la fiche de paie du modèle (`remuneration.py`)
ne connaît, hors retraite, que les taux de 2026.

**Les statistiques.** Une partie distincte du comparateur : ce que les
générations réelles ont vécu ou vivront — âge moyen de départ, durée validée,
durée de retraite, espérance de vie à 60 ans, taux de prélèvement, rendement
interne —, chaque chiffre dit observé, projeté ou modélisé. Sources à relever,
à inscrire au registre et à certifier : la DREES, dont le dépôt lit déjà deux
séries (`caracteristiques_retraites.csv`, `age_conjoncturel_depart.csv`), mais
par année et non par génération ; le rapport annuel du COR
(`cor_rapport_annuel`) ; les tables de mortalité par génération de l'INSEE
(`insee_tables_mortalite`). Le modèle a aussi les siennes : la page Coût
simule les générations 1880 à 2015, de cinq en cinq, pondérées par les
effectifs (`cout.js`) ; les moyennes par génération se tirent de cette grille.

**Le calcul, et son prix.** Le comparateur calcule une carrière par année de
naissance choisie, dans le navigateur et sous les réglages du lecteur, comme
les pages qui agrègent (`PAGES_AGREGEES`). Une courbe année par année, de 1930
à 2005, en calcule soixante-seize : à mesurer d'abord
(`scripts/budget_calcul.py`) et, si elle dépasse le budget, à fabriquer à
l'avance, comme `data/derive/equilibre.json`.

**Ce qu'une page de plus touche**, relevé le 4 octobre 2026 en cherchant
`/cas-types` dans le dépôt. Dans `moteur/js/pages.js` : `DESCRIPTIONS`,
`TITRES`, `PAGES_AGREGEES` ; et sans doute `VUES_DE_PAGE`, ce que le lecteur
choisit — le profil, les années de naissance, le sexe — étant un regard, qui
ne change aucune règle et ne voyage pas vers les autres pages, non un
réglage. Dans `moteur/js/gabarit.js`, `GROUPES_NAVIGATION`. Dans
`index.html`, `MESSAGES_ATTENTE`, qui annonce encore « 12 cas types » pour
Carrières types et pour Coût quand `CAS_TYPES` en compte treize. Puis les
témoins de pages (`scripts/construire_temoins.py`,
`tests/temoins/pages.json`), le catalogue des affirmations
(`data/reference/site/affirmations.yaml`, `tests/test_affirmations.py`), le
parcours de présentation (`docs/parcours_presentation.md`,
`tests/test_parcours.py`), les tests du site (`test_web.py`,
`test_web_revues.py`), et la table des adresses de
`docs/integration-partiliberalfrancais.md`, dont l'accueil renvoie aux « sept
autres pages ».

**Ce qui est à faire**, dans l'ordre, chaque étape valant seule :

1. Les indicateurs à portée — âges, durées, années de retraite, pension, cumul
   brut, cotisations, rendement —, en Python d'abord, puis dans son jumeau,
   avec un témoin par génération pour deux cas types.
2. La page : son adresse, son titre, sa place dans la navigation ; le
   comparateur (un profil, deux ou trois années de naissance, le sexe) ; un
   tableau sous chaque graphique (`donneesDuGraphique`) ; et ce que toute page
   demande : témoins de pages, catalogue des affirmations, tests du site, et
   l'adresse dans `docs/integration-partiliberalfrancais.md`, qui promet de
   dire toute adresse.
3. Le net : la série des prélèvements sur les pensions depuis leur création,
   ses fiches, puis le cumul net.
4. Les heures : la série choisie, enregistrée et certifiée, puis l'indicateur.
5. Les statistiques, source par source.
6. Peut-être, « votre carrière, née une autre année » : la saisie du
   simulateur décalée d'autant d'années, ses salaires gardés en multiples du
   salaire moyen ; il y faut une règle qui translate les dates et les montants
   saisis.

**Ce que le propriétaire tranche.** Une page de plus, ou une partie de la page
Carrières types : le site est passé de dix pages à huit le 23 septembre 2026,
en fondant deux pages dans d'autres. Son nom, son adresse (`#/generations` ?),
sa place (« L'essentiel » ou « Pour vérifier »). Les quatre ou cinq
indicateurs de tête. La lecture du « net ». Les heures légales ou effectives.
La plage des générations — l'action 121 veut toutes les personnes vivantes —
et les profils offerts : les treize cas types, ou quelques-uns. S'il faut
montrer à côté ce que la proposition ferait des mêmes écarts : un taux unique
et une pension convertie par l'espérance de vie sont faits pour les réduire,
ce que la page mesurera plutôt qu'elle ne l'affirmera. Et si le dépliant de la
page Pourquoi changer sur le rendement des générations y renvoie, ou s'y
fond.

### 144. Les propositions des candidats à la présidentielle, au simulateur et à la page Coût : leurs mots seuls, montrées par défaut, masquables — `à faire`

**Demande**, le 4 octobre 2026 : « J'aimerais que l'on puisse voir les
scénarios des candidats à la présidentielle dans la page des coûts et dans le
simulateur. Il faut que ce soit une option désactivable mais activée par
défaut. Il faut s'en tenir à leurs propositions, il ne faut rien inventer.
C'est quelque chose qui sera amené à beaucoup changer pendant la campagne
électorale. Il faut prévoir une architecture légère et flexible pour mettre
ça en place. Je veux seulement documenter pour l'instant mais ne pas encore
ajouter cette fonctionnalité. » Elle naît `à faire` : rien n'en est
construit, et elle attend que le propriétaire la lance.

**Ce sur quoi elle s'appuie, déjà là.** La fiche
`fin_de_la_suspension_2028` le dit : l'élection « peut abroger, prolonger ou
refaire le calendrier ». La proposition d'un candidat est un autre droit,
posé sur le droit réel : un univers (`docs/architecture.md`, § 4.8), comme
les scénarios 2 à 6, dont la pile se résout à la fabrication du paquet, que
le site lit sans rien résoudre (§ 13.5). Le contrôle des couches refuse déjà
tout passage cité qu'il ne retrouve pas mot pour mot dans le README
(`controler`, dans `noyau/univers.py`) : « une déduction n'est pas une
lecture » vaut pour un programme comme pour la proposition. Le registre des
sources sait garder la copie d'un document hors du dépôt, son empreinte et
ce que sa licence permet (`miroir`, `sha256`, `rediffusion`). Les réglages
s'écrivent une fois, dans `champsModelisation`, pour les options du
simulateur et pour le bloc de réglages de la page Coût. Et le pilote par
univers est réservé, « codé plus tard sans rien refondre » (§ 13.5).

**Ce qui manque.** Le moteur ne calcule un univers que s'il ajoute le compte
notionnel, et le droit réel que par l'échéancier, sans couche
(`scenarios/univers.py`) : un droit réel modifié, ce qu'est presque toute
proposition de campagne, n'a pas de chemin. La page Coût connaît six
systèmes en liste fermée (`SCENARIOS`, dans `cout.py` et `cout.js`), la
comparaison du simulateur ses cinq univers notionnels (`CHAMPS_NOTIONNELS`,
dans `simulateur.js`). Et rien ne masque un bloc sur deux pages à la fois :
un réglage change le modèle, un regard ne vaut que pour sa page
(`VUES_DE_PAGE`).

**Les règles, qui font « ne rien inventer ».**

1. *Une mesure est une citation.* Mot pour mot, entre guillemets français,
   d'un texte du candidat : son programme, son site, un discours, un
   entretien où il est cité entre guillemets, une publication de son compte.
   Elle porte sa date de publication, sa date de lecture, son adresse et une
   copie datée. Une paraphrase de presse, un propos rapporté sans
   guillemets, le chiffrage d'un tiers ne sont jamais une source ; le
   chiffrage d'un tiers peut servir de contrôle, comme un autre modèle
   (§ 3.4).
2. *Chaque nombre du calcul se lit dans la citation.* L'âge, la durée, le
   montant, la date qu'un levier emploie figurent dans le passage cité —
   hors la date que fournirait la convention de calendrier, si elle est
   admise —, et un test le vérifie, comme `controler` vérifie les motifs
   des couches.
3. *Ce que le candidat ne dit pas ne se complète pas.* La mesure reste
   `non_chiffree`, avec ce qui manque — un montant sans dire s'il est brut
   ou net, un âge sans dire pour quelles générations —, et le site la
   montre citée, à côté des chiffres. Seule exception possible, que le
   propriétaire tranche : une convention de calendrier, la même pour tous.
4. *Rien d'amputé non plus.* Un chiffre qui ne compte qu'une partie d'une
   proposition le dit (« trois mesures sur cinq »). Le solde d'un candidat
   ne paraît que si ses mesures de financement sont chiffrées : sinon la
   page montre la dépense, et dit pourquoi le solde manque. Une dépense sans
   les recettes annoncées trahirait la proposition autant qu'un chiffre
   inventé.
5. *Le même traitement pour tous.* Un seul gabarit, l'ordre alphabétique des
   noms, aucune couleur qui classe ; ni commentaire, ni note, ni adjectif :
   le bloc ne dit que ce que le candidat a dit et ce que le modèle a
   calculé. Chaque candidat se compare au scénario 1, l'étalon, jamais à la
   proposition du dépôt, et son bloc reste à part des six scénarios. Le
   coût qu'un candidat annonce lui-même se montre, cité, à côté de celui du
   modèle.
6. *Rien ne se perd.* Une mesure qui change reçoit une version datée et
   sourcée ; une mesure abandonnée, une version qui le dit ; un candidat qui
   se retire, un statut daté. Aucun fichier ne s'efface : la campagne reste
   lisible après coup.
7. *Le scénario 1 n'en reçoit rien.* Une proposition n'entre au droit réel
   qu'une fois votée et publiée, par la veille (`docs/veille_droit.md`),
   jamais par ce bloc.

**L'architecture prévue : des données, et presque pas de code.**

1. *Un fichier par candidat*, `data/reference/candidats/<identifiant>.yaml`,
   et un fichier commun dans le même dossier, `conventions.yaml` : le
   critère d'inclusion, la convention de calendrier si elle est admise, et
   un interrupteur `actif`. Ajouter, corriger ou retirer un candidat ou une
   mesure ne touche que ces fichiers : ni code, ni fiche de règle, ni
   univers ni couche à écrire à la main. Les sources s'y écrivent avec les
   champs du registre, pour que `source_locale.py` sache en garder la copie
   dans `data/brut/`, sans charger `data/sources.yaml` du va-et-vient d'une
   campagne. Le format, à fixer à l'étape 1 :

   ```yaml
   schema_version: 1
   id: <identifiant>
   nom: <prénom et nom>
   etiquette: <le parti ou le mouvement, tel que le candidat le dit>
   statuts:                  # déclaré, investi, retiré : chacun daté, sourcé
   - {etat: declare, du: <date>, source: <id>}
   sources:
   - id: <id>
     type: programme         # ou site, discours, entretien, publication
     url: <adresse>
     publie_le: <date>
     lu_le: <date>
     miroir: <copie datée : archive du web, ou release du dépôt>
     sha256: <empreinte de la copie lue>
     rediffusion: {statut: a_lire}   # ce que sa licence permet
   mesures:
   - id: <id>
     cote: depense           # ou financement
     versions:
     - du: <date de la déclaration>
       source: <id>
       citation: « <le passage, mot pour mot> »
       levier: <un levier du catalogue>
       valeurs: {<paramètre>: <nombre lu dans la citation>}
       # ou, à la place du levier et des valeurs :
       # non_chiffree: <ce qui manque, ou « aucun levier ne la calcule »>
   cout_annonce: {citation: « … », source: <id>}   # s'il en publie un
   ```

2. *L'univers se déduit du fichier.* Le chargeur des univers lit chaque
   candidat comme un univers `candidat_<identifiant>` — le droit réel, puis
   une couche faite de la dernière version de chaque mesure chiffrée — :
   le contrôle, le paquet et les moteurs voient un univers ordinaire. Au
   contraire de la proposition, ce que le candidat ne touche pas garde le
   droit réel, et le test des fiches sans décision ne s'y applique pas : qui
   ne dit rien de la réversion garde la réversion en vigueur.
3. *Un catalogue fermé de leviers*, dans le code : ce qu'une mesure sait
   changer. Deux sortes.
   - *Le levier de table* réécrit une table que le paquet porte déjà
     (`ages_ouverture`, `durees_requises`, `minimum_contributif`…), à la
     fabrication, en Python seul : le moteur JavaScript lit la table
     substituée comme l'originale, sans connaître le levier. C'est la sorte
     à préférer : elle ne se paie qu'une fois.
   - *Le levier de règle* écrit une règle qu'aucune table ne porte : dans
     les deux moteurs, avec sa fiche, comme tout changement du modèle.

   Un levier ne s'écrit que quand une mesure sourcée le demande, aucun
   d'avance. En attendant, la mesure est `non_chiffree` (« le modèle ne sait
   pas encore la calculer »), ce qui n'est pas une erreur ; un nom de levier
   inconnu en est une, que le contrôle refuse, comme `scenarios/univers.py`
   refuse ce qu'il ne sait pas faire. À regarder à l'étape 2 : les tables
   vont par génération, et le moteur coupe les dates d'effet par des
   constantes (`SUSPENSION_2026_EFFET`, `REFORME_2023_EFFET`, dans
   `droit/ouvrir.py`) ; une mesure datée à l'effet de la pension demandera
   peut-être d'en faire une table datée, changement du modèle, dans les deux
   moteurs.
4. *Le paquet* porte les candidats sous une clé à eux, résolus comme les
   univers aujourd'hui, avec la date du relevé, que chaque bloc affiche ;
   `actif: false` l'en retire en entier. C'est l'interrupteur du
   propriétaire, distinct de celui du lecteur : pour la fin de la campagne,
   ou pour retirer le bloc sur l'heure.
5. *L'option du lecteur* : un paramètre, `candidats`, que l'adresse ne porte
   pas quand les candidats se montrent — le défaut n'a pas besoin de
   voyager — et qui vaut `non` quand le lecteur les masque. Une case, écrite
   une fois dans `champsModelisation`, paraît donc dans les options du
   simulateur et dans les réglages de la page Coût. C'est une troisième
   sorte, entre le réglage et le regard : elle voyage de page en page comme
   un réglage, mais ne change aucun chiffre, comme un regard, et n'allume
   donc pas l'encadré « Ces chiffres ne sont pas ceux des réglages par
   défaut ». Les réglages qui valent pour tout le modèle — la projection,
   l'emploi, les euros constants — valent pour les candidats ; ceux du
   compte notionnel ne les touchent pas. À la surface publique (annexe C.9),
   `entree` gagne `candidats`, au défaut « oui » : une ancienne adresse rend
   les mêmes six résultats, plus le bloc ; `sortie` grandit par la règle
   additive, et `docs/integration-partiliberalfrancais.md` le dit à l'hôte
   avant la mise en ligne, puisque ses pages changeront sans qu'il ait rien
   fait.
6. *Au simulateur*, sous les six scénarios, un bloc à part : pour chaque
   candidat, la pension de la même carrière sous son univers, l'âge de
   départ, l'écart au scénario 1, puis ses mesures, chiffrées ou non,
   citées, datées, sourcées. Le budget de mots du formulaire vierge
   (`test_le_simulateur_tient_en_peu_de_mots`) dira si la case y tient.
7. *À la page Coût*, une section à elle, et non des courbes de plus sur le
   bilan : la dépense de chaque candidat, comparée au scénario 1, et son
   solde quand son financement est chiffré, sur le même axe pour tous,
   comme le bilan. Le pilote par univers la calcule. Chaque candidat coûte
   un passage de plus des cas types sur les générations : `budget_calcul.py`
   le mesure à l'étape 4, la section ne se calcule que si elle se montre,
   et, s'il le faut, ses agrégats aux réglages par défaut se fabriquent
   d'avance, le navigateur ne recalculant que sous d'autres réglages.
8. *Les témoins* : un fichier à eux, `tests/temoins/candidats.json`, et les
   témoins de pages faits sous `candidats=non`. Une semaine de campagne ne
   récrit alors qu'un fichier, et non chaque témoin de page.
9. *Les contrôles* : la forme de chaque fichier ; chaque citation retrouvée
   dans la copie de sa source, gardée dans `data/brut/` sous son empreinte,
   jamais versionnée si sa licence l'interdit ; chaque nombre d'un levier
   dans sa citation ; chaque levier connu ; aucun chiffre sans la liste de
   ses mesures ; `candidats=non` laisse le reste de la page identique au
   caractère près ; un seul gabarit pour tous.
10. *La routine de campagne* : `scripts/candidats.py`, à écrire, liste les
    candidats, leurs mesures par état et les sources que personne n'a
    relues depuis trop longtemps (`--perimees`). Une mesure nouvelle se
    saisit ainsi : lire la source, en garder la copie, écrire la version,
    puis `candidats.py --verifier`, `regenerer.py`, la suite, `pousser.sh` —
    sans code, sauf un levier qui manque. Après l'élection, `actif: false`,
    et les fichiers restent.

**Où regarder, relevé le 4 octobre 2026**, pour n'avoir pas à le chercher :

- *Les deux moteurs ne lisent pas leurs tables au même endroit.* Le
  JavaScript les construit depuis le paquet (`regimes.js` :
  `paquet.ages_ouverture`, `paquet.durees_requises`,
  `paquet.durees_requises_avant_suspension`, `paquet.minimum_contributif`…) ;
  le Python, qui fait foi, depuis les fichiers de
  `data/reference/legislation/` (`TableParGeneration`, dans
  `scenarios/actuel.py` : `AgesOuverture` lit `age_ouverture_requis.csv`,
  `DureesRequises` `duree_assurance_requise.csv`), par
  `charger_table_par_generation`, mémorisé et partagé. Le levier de table
  se calcule donc une fois, en Python (point 3), mais le moteur Python doit
  apprendre, une fois pour toutes, à recevoir une table substituée : une
  table neuve, jamais une retouche de celle que la mémoire partage.
- *Les réglages* : `CLES_MODELISATION` et `DEFAUTS`, dans `saisie.js` ; en
  Python, la même liste et les défauts de `Saisie`, dans `saisie.py`.
  `requeteModelisation()` (`requete_modelisation()` en Python) écrit dans
  l'adresse les réglages qui s'écartent du défaut, et c'est elle qui allume
  l'encadré (`avertissementReglages`, dans `pages.js`) : l'option
  `candidats` doit voyager sans passer par elle, ou en être filtrée.
- *Les univers du paquet* : la clé `univers`, dont chaque entrée porte son
  `calcul`, nul pour le droit réel. Le simulateur garde ceux dont le calcul
  n'est pas nul (`scenariosNotionnels`) et refuse toute clé hors de
  `CHAMPS_NOTIONNELS` ; le Python les lit dans `SCENARIOS_NOTIONNELS`
  (`simulateur.py`). Un candidat, qui n'a pas de calcul notionnel, y entrera
  par une autre porte.
- *La page Coût* : `SCENARIOS` commande `CLES_CAS_TYPES` et `CLES_MASSES`
  (`cout.js`). Le coût d'un système y est, pour le passé, la dépense
  observée multipliée par le rapport de sa masse à celle du système actuel,
  et, pour l'avenir, un ancrage multiplié par sa masse (en-tête de
  `cout.js`) : celui d'un candidat se lira de même, rapporté au scénario 1.
  Son solde passe par `ressourcesDe` : une mesure de financement y
  demandera un levier côté ressources. L'axe du bilan est fixe sous tous
  les réglages, plafonné par la variante la plus dépensière des comptes du
  COR (`depenseMaximaleToutesVariantes`, dans `equilibre.js`) : une section
  qui le partage vérifie qu'aucun candidat ne le dépasse.
- *Le contrôle des citations* : `citations()` et `controler()`, dans
  `noyau/univers.py`, se reprennent tels quels, contre la copie d'une
  source au lieu du README.

**Ce qui est à faire**, dans l'ordre, chaque étape valant seule :

1. Le format, le chargeur, les contrôles et `candidats.py`, sans rien
   afficher ; puis les premiers candidats, saisis à leurs sources, une fois
   le critère d'inclusion tranché. Aucun résultat ne bouge.
2. Le moteur : les leviers que les mesures saisies demandent, l'échéancier
   sous l'univers d'un candidat dans les deux moteurs, les témoins des
   candidats, la mesure du budget de calcul.
3. Le simulateur : le bloc, l'option `candidats`, la surface publique,
   l'avis à l'hôte, les témoins de pages sous `candidats=non`.
4. La page Coût : le pilote par univers, la section, la règle du solde, le
   budget.
5. La version de l'architecture (§ 4.8, § 8, annexe C.9), et ce que vaut le
   chiffre d'un candidat, dans `limites.md`.

**Ce que le propriétaire tranche**, avant l'étape 1 :

1. *Qui figure.* Un critère objectif, le même pour tous et écrit dans
   `conventions.yaml` : une candidature déclarée et sourcée, puis la liste
   officielle du Conseil constitutionnel quand elle paraît. Et si un
   candidat sans proposition sur les retraites figure quand même, sous la
   mention « aucune proposition relevée », datée.
2. *Le calendrier qu'un candidat ne donne pas.* Strict, ce que dit la
   demande : une mesure sans date ne se chiffre pas. Ou une convention, une
   seule pour tous, montrée à côté de chaque chiffre comme une hypothèse du
   site et non du candidat. Recommandé : strict d'abord, et la convention
   seulement si trop peu de mesures se chiffrent, pour le seul calendrier,
   jamais pour une valeur.
3. *Le chiffrage partiel.* Un candidat se chiffre sur ses mesures chiffrées,
   leur compte affiché, ce qui est recommandé ; ou ne se chiffre que si
   toutes le sont.
4. *Les corrections.* Par où l'équipe d'un candidat signale une erreur, et
   dans quel délai elle est reprise.
5. *Le droit d'une publication en campagne*, à faire relire par un juriste
   avant la mise en ligne : le droit de citation (L. 122-5 du code de la
   propriété intellectuelle), le référé contre la diffusion en ligne
   d'allégations inexactes pendant les trois mois qui précèdent un scrutin
   général (L. 163-2 du code électoral), et ce qu'implique, en campagne,
   d'être publié sur le site d'un parti. Un repère, pas un avis juridique :
   articles cités de mémoire, à lire.

### 154. Le temps partiel des fonctionnaires, fini : la surcotisation, et ce que la quotité laisse — `à faire`

**D'où elle vient.** L'action 136 (étape 3) a écrit, le 11 octobre 2026, le
temps partiel des fonctionnaires : la quotité réduit les services sans
réduire la durée d'assurance, dans les deux moteurs, et l'exemple du SRE rend
ses 148 trimestres (`sre_temps_partiel_pierre`). La fiche
(`temps_partiel_fonction_publique`) reste `approchee`.

**Ce qui est à faire**, selon la règle du scénario 1 (`docs/veille_droit.md`) :

1. La surcotisation (L. 11 bis), un choix borné à quatre trimestres, qui
   demande une saisie de plus et le taux de sa retenue.
2. La rémunération à six septièmes et à trente-deux trente-cinquièmes, que le
   modèle ramène à la quotité, comme pour la retraite progressive.
3. Le mi-temps d'avant 1982, que l'index ne porte pas.
4. Le minimum garanti : vérifier qu'il lit les services réduits.

La confrontation à l'oracle est à l'action 153.

**Ce que le propriétaire tranche** : le champ de plus que la surcotisation
demande au formulaire.

### 155. La trace d'un calcul : chaque ligne cite sa fiche, puis chaque simulation rend ce qu'elle a lu — `à faire`

**D'où elle vient.** L'action 136 (étape 4). OpenFisca rend, pour toute
simulation, chaque variable calculée, sa valeur, et les variables et les
paramètres qu'elle a lus (`openfisca test -v`, ou `/trace` sur son interface
web) ; les modèles Publicodes du registre (`modele_social`, `modele_ti`,
`modele_as`) portent leurs références sous chaque règle et en tirent une page
par valeur ; Catala écrit chaque règle sous l'alinéa qu'elle transcrit. Le
1er octobre 2026, le relevé des droits ne citait la fiche qui l'écrit que sur
733 de ses 22 789 lignes (3 %), et sa version sur 14 ; « Le détail du
calcul », sur le site, ne cite ni fiche ni article. « D'où vient ce
chiffre ? » : les autres y répondent par construction, le dépôt par une
lecture du code.

**Ce qui est à faire** :

1. Chaque ligne du relevé et chaque composante de la liquidation citent leur
   fiche et sa version, comme l'architecture le prévoyait aux phases 4 et 5.
2. Une simulation rend l'arbre de ce qu'elle a lu, en ligne de commande.
3. Le même arbre sous le résultat du site : « Le détail du calcul » cite la
   fiche et l'article de chaque ligne.

### 156. Les résultats datés : l'empreinte du paquet sur chaque simulation, et le journal des changements de résultats — `à faire`

**D'où elle vient.** L'action 136 (étape 5). OpenFisca se publie sur PyPI en
versions numérotées, son intégration continue refuse un changement
fonctionnel sans numéro nouveau ni ligne à son journal des changements, et
`openfisca serve` expose son calcul à qui l'appelle (`/calculate`, `/trace`,
`/variables`, `/parameters`, et une description OpenAPI, `/spec`). Le dépôt
n'expose que les adresses du site (`docs/architecture.md`, annexe C.9) ;
aucun résultat ne porte la version du modèle qui l'a calculé — C.9 range des
empreintes parmi ce qu'une simulation rend, et aucune n'était calculée le
1er octobre 2026 —, et un chiffre cité ne se retrouve que par l'historique.

**Ce qui est à faire** :

1. Chaque simulation porte l'empreinte du paquet qui l'a calculée.
2. Chaque commit qui déplace un témoin écrit son résumé
   (`scripts/resumer_temoins.py`) dans un journal des changements de
   résultats.

**Ce que le propriétaire tranche** : s'il faut une interface d'appel — sans
serveur, une commande, ou un JSON à télécharger depuis la page — et des
versions numérotées, qu'une session ne peut pas étiqueter elle-même (HTTP 403,
action 130).

### 157. La page Coût sur la population : la bascule, une fois les cas types à leur place — `à faire`

**D'où elle vient.** L'action 136 (étape 6). La page Coût repose sur treize
cas types pondérés par les effectifs de leur caisse ; repassée le 5 octobre
2026 sur une grille élargie, elle bougeait assez pour justifier une
population. Celle-ci est faite, à sa première version : tirée des
distributions publiées et certifiées, mesurée contre les résidents de l'EIR
2020 en quatorze versions, puis régime par régime, les 11 et 12 octobre, elle
tourne à côté de la page (`scripts/grille_large.py --grille population`), et
ses écarts sont aux limites (`docs/limites/5-bis-cout-agrege.md`). Contre la
page du jour, elle creuse l'écart des années observées de 1,38 point au
scénario 2 et de 3,11 aux scénarios 4 et 6, ajoute 0,046 point de PIB à la
garantie vieillesse en 2070, et refait le passé à 17,2 % au pire depuis 2000,
pour 16,6 sur la page. Depuis l'action 150, la page n'a plus de réglages :
elle lit une référence que le Python fabrique d'avance, et la bascule n'est
plus que celle de sa grille.

**Ce qui est à faire**, après l'action 152, dont la population hérite les cas
types :

1. La référence de la page Coût fabriquée sur la population plutôt que sur
   les treize cas types, et ce qu'elle coûte en temps à la fabrique, que
   GitHub refait à chaque envoi (action 148).
2. Ce que la page et les limites disent de leur grille, réécrit avec les
   chiffres qui en bougent.

**Ce que le propriétaire tranche** : s'il bascule la page, et quand.

### 165. Ce que le compte crédite : des cotisations que personne n'a versées, d'autres comptées deux fois ou perdues — `à faire`

**D'où elle vient.** L'audit des scénarios 2 à 6 que le propriétaire a demandé
le 23 octobre 2026 : « On s'est beaucoup concentré sur le scénario 1. »
Six zones relues, chaque défaut prouvé par une simulation ou par la lecture du
code, puis revérifié ; cette action prend ceux de l'alimentation du compte.
Aucun ne vient du portage : 456 cas confrontés entre le Python et le
JavaScript, aucun écart. C'est la règle qui est fausse, des deux côtés.

**Ce qui est à faire**, chaque point par le test qui le reproduit, vu rouge :

1. **« Sans activité professionnelle » cotise au compte dès la bascule.** Née
   en 1990, statut `sans_activite`, salaire au niveau 1 : 0 € au scénario 1,
   22 225 € par an aux scénarios 2 à 5, 16 928 € et un pilier au 6 ; le compte
   reçoit 11 014 € en 2026, rien avant. `compte.py:607-608` fait passer au
   régime unifié toute ligne qui cotise, même sans régime, et `a_un_employeur`
   la traite en indépendant ; `affiliations.yaml:1296-1300` dit « Aucune
   cotisation, donc aucun droit ». Le site offre ce statut en premier métier et
   exige un salaire (0,1 fois le salaire moyen au moins) ; le test
   `test_simulateur.py:698` (« sans cotisation, aucun droit notionnel ») ne
   simule aucune carrière sans cotisation.
2. **La RAFP comptée deux fois après la bascule.** Le régime unifié prend la
   rémunération entière, primes comprises, sans rien hors répartition
   (`compte.py:641-658`) ; les six scénarios servent pourtant la rente RAFP du
   scénario 1, qui accumule jusqu'au départ (`simulateur.py:390-399`). La fiche
   `compte_notionnel` (« le RAFP n'y entre pas ») et `fusion.py:73` (« La
   capitalisation reste à part ») disent l'inverse. Fonctionnaire d'État née en
   1975, 20 % de primes : assiette du compte 33 297 € et 666 € à la RAFP en
   2025 ; 46 975 € et 0 en 2030 ; rente RAFP de 1 233 € servie dans les six.
   Pour la fonctionnaire du README, 49 % des versements à la RAFP sont
   postérieurs à 2025.
3. **Les cotisations de 1941 à 1944 perdues.** Le salarié du privé y relève
   des assurances sociales, marquées `hors_repartition`
   (`assurances_sociales.yaml:18`), alors que l'origine de 1941 se justifie
   par elles (`avts.yaml:40-42`, `methodologie.md:42-46`) ; le scénario 1 ne
   leur sert aucune rente à part : elles ne vont ni au compte, ni au
   compartiment servi. Le scénario 4 y perd 10 % (né en 1915) et 15 % (né en
   1905). Les retenues d'avant 1941 des pensions civiles, de la SNCF et des
   mines sont écartées (`compte.py:1152-1155`), quand `methodologie.md:54-55`
   les dit « incluses ».
4. **La part patronale du repli, nulle.** Quand le taux du privé de l'année
   ne dépasse pas la retenue de l'agent, le repli rend une part patronale nulle
   (`compte.py:376-379`), et le scénario 4 égale le 2 : SNCF, RATP, mines,
   Banque de France, SEITA de 1941 à 1956 ; marins, CRPCEN, Opéra,
   Comédie-Française, port de Strasbourg jusqu'en 1965 ; État, militaires,
   policiers, FSPOEIE de 1941 à 1946. `limites/4-regimes-incomplets.md:502-506`
   la promet « jamais laissée à zéro », et le site écrit « effort du privé de la
   même année » (`pages.js:6172`). Les années que le modèle prolonge au bout
   d'une série (SNCF 2019-2025, IEG 2021-2025) sortent comptées « trouvées ».
5. **L'option `totale_alignee` sous la retenue de l'agent** : SNCF né en 1925,
   4,86 % en 1946 et 6,48 % en 1950 au compte, quand la seule retenue faisait
   7,90 % (`compte.py:388-392`) ; un seul test, une carrière de 1975
   (`test_simulateur.py:824-845`).
6. **Une bascule réglée avant 2019** : le taux du régime unique additionne en
   dur le régime général et l'Agirc-Arrco (`fusion.py:72`), dont la fiche naît
   en 2019, et ignore le statut pivot que la fiche `fusion_des_regimes` nomme
   (`simulateur.py:1173-1174`). Bascule en 2000 : 16,35 % au lieu de 23,85 %,
   −29 % aux scénarios 2 et 4 ; en 1945, 4,86 % figés jusqu'au départ ; de 1941
   à 1944, « aucun régime pivot exploitable », alors que le formulaire accepte
   1941 (`saisie.js:423`) et que le test tiré au sort borne à 1945
   (`test_web.py:694`). La fusion n'est testée qu'en 2026
   (`test_moteur.py:1023-1084`).
7. **Le pilier, sur une activité cumulée** : il ne prélève rien l'année où la
   ligne principale ne cotise pas (`notionnel.py:462-465` lit `carriere.ligne`,
   la principale), quand l'assiette somme toutes les lignes
   (`compte.py:559-572`) : un artisan cumulé pendant un chômage ne verse rien.
8. **`fusion_au_plus_defavorable=False`**, réglage du Python : le scénario 6
   garde 25,07 % après la bascule au lieu de 18 %, et son pilier prélève sur la
   somme des assiettes des régimes (1,56 fois le revenu ; rente +56 %).

**Ce que le propriétaire tranche** : si la RAFP continue après la bascule — ses
cotisations restent à part, et les primes sortent de l'assiette du régime
unique — ou s'arrête à ses droits de 2025 ; si les assurances sociales de 1941
à 1944 sont de la répartition ; ce que vaut le taux du régime unique après une
bascule ancienne, ou si la saisie s'arrête à 2019.

### 166. La bascule des scénarios 3 et 5 : des droits acquis qui ne sont pas « au contributif seul », des pensions déjà servies re-figées, une date qui flotte — `à faire`

**D'où elle vient.** Le même audit, du 23 octobre 2026. Le site ne montre plus
les scénarios 3 et 5 (`pages.js:149-162`), mais le README, la méthodologie, la
page Coût, `scripts/proposition_prospective.py` et le JSON les portent. Le
Python et le JavaScript y concordent au bit ; aucun test ne tient ce qui suit.

**Ce qui est à faire** :

1. **La liquidation fictive garde ce qui n'a pas été cotisé.** La couche
   `contributif_seul` ne neutralise que les avantages non contributifs, les
   points gratuits — que le vocabulaire réduit à ceux de la complémentaire
   agricole (`vocabulaire/valeurs.yaml:220-222`) — et la décote. Les lignes
   d'interruption portent leurs trimestres assimilés (`carriere.py:704-711`),
   que `droit/compter.py:638-645` crédite sans condition : le drapeau ne coupe
   que les périodes déclarées à part (`compter.py:657-661`). Restent donc
   la maladie, le chômage, le service national, les points de l'Agirc-Arrco
   donnés « sans contrepartie de cotisations » (`carriere.py:748-753`), et
   l'AVPF, que le moteur sait neutraliser (`scenarios/univers.py:53`) et que la
   couche ne demande pas, quand `comptes_notionnels` la retire du compte. Née en
   1975, non-cadre, quatre ans de maladie de 2005 à 2008 plutôt que sans
   activité : pension figée de 18 365 € au lieu de 15 846 € (+15,9 %),
   scénario 3 de 27 585 € au lieu de 24 287 € (+13,6 %), scénario 2 inchangé.
   Huit ans d'AVPF : +25,5 % de pension figée ; le cas type « carrière
   heurtée » de 1975 : +25 %. Le README (lignes 17, 28, 412), `methodologie.md`
   (lignes 564-568, 621-623) et `notionnel.py:663-667` disent l'inverse ;
   `avantages.py:401-418` range ces dispositifs parmi les avantages non
   contributifs, et sait les retirer. `test_univers.py:37-40` fige la
   neutralisation incomplète.
2. **Une pension servie avant la bascule est re-figée quand le dernier départ
   vient après.** La carrière tronquée à la bascule (`notionnel.py:686`)
   reliquide tous ses régimes, et la liquidation fictive ignore les départs
   (`actuel.py:3507-3513`). Militaire de 20 à 40 ans, né en 1975, puis salarié
   jusqu'à 64 ans : sa pension militaire, servie depuis le 1er janvier 2015 au
   scénario 1 (15 624 €), entre dans la pension figée de 2026, se convertit,
   et n'est plus servie qu'en 2039 : treize années de pension disparaissent
   (scénario 1, 38 476 € ; scénario 3, 31 070 €). La fiche dit qu'« une pension
   qui a pris effet avant ne bouge pas ». L'inverse est faux aussi : un régime
   demandé après la bascule, quand le premier départ la précède, reste au droit
   réel (cadre né en 1962, parti en 2025, Agirc-Arrco demandée en 2029).
3. **La date de la bascule.** Les scénarios 3 et 5 gardent le droit réel à qui
   liquide l'année même de la bascule (`notionnel.py:598`, son jumeau, et
   `cout.py:3009` : `<=`) ; le scénario 6 la fait régir par la réforme
   (`simulateur.py:1280` : `<`), `config.py:457-460` fait basculer le compte au
   1er janvier, la revalorisation traite l'année comme nouvelle
   (`revalorisation.py:1847`), et la fiche `valorisation_des_droits_acquis`
   dit « avant » (ligne 13) puis « l'année de la bascule ou avant »
   (lignes 51-52). Agent SNCF né en 1974 : 19 259 € pour un départ en août
   2026, 16 439 € en janvier 2027 (−14,6 %). La décision n'est consignée que
   dans `docs/archives/limites.md`.
4. **Qui a tout acquis avant la bascule touche plus qu'au droit réel**, et
   rien ne le dit : le capital figé suit l'indice du compte, la masse salariale,
   le droit réel les prix, et la décote est neutralisée
   (`notionnel.py:726-729`). Activité arrêtée en 2020 : né en 1966, parti à
   62 ans, 17 982 € contre 15 086 € (+19 %) ; né en 1970, à 64 ans, +19 %.
   `methodologie.md:1138-1140` dit que la bascule ne peut que retirer.
5. **Le diviseur de conversion.** La conversion se fait à 65 ans au diviseur de
   2026, celui de la génération 1961, et la pension se sert au diviseur de
   l'année du départ (`notionnel.py:715-724`) : un départ à 65 ans perd sur sa
   part figée 2,1 % (60 ans en 2026), 5,8 % (50), 9,0 % (40), 11,7 % (30),
   quand le README (ligne 395) promet qu'il « ne perd plus rien ».
   `methodologie.md:1157-1161` écrit « G(64, 2026), 23,56 », qui est
   G(65, 2026) (G(64, 2026) vaut 24,48), et « environ 17 % est retiré » pour
   16,5 % de diviseur, 14,2 % de part retirée. Le choix du diviseur est suivi à
   l'action 138 (étape 13) ; la phrase du README, non. Qui a plus de 65 ans à
   la bascule est converti à 65 ans quand même (`notionnel.py:715-716`) : né en
   1940, parti à 88 ans, 117 094 € au scénario 3 contre 56 167 € au 1.
6. **Le salaire de référence d'une carrière courte** : la liquidation fictive
   prend la moyenne de toutes les années d'une carrière de moins de vingt-cinq
   ans. Né en 1996, payé 0,3 fois le salaire moyen de 18 à 24 ans puis au
   salaire moyen : 23 847 € au scénario 3, contre 29 354 € s'il avait eu le
   salaire moyen dès 18 ans (−19 %, contre −2,3 % au scénario 1).
7. **La date fictive du 1er janvier** perd le mois de naissance
   (`notionnel.py:690-702`, et son jumeau) : né en novembre 1961, 168
   trimestres requis au lieu de 169 ; né en 1965, la table d'avant la
   suspension (`duree_requise_avant_suspension.csv`), 172 au lieu de 170.
8. **Ce que l'architecture promet** (`docs/architecture.md:624-633`) : une
   liquidation fictive qui lit la retraite progressive, la réversion attendue
   et l'invalidité en cours, et un relevé « ligne par ligne » ; le code exclut
   la retraite progressive (`actuel.py:3495-3498`), et la carrière tronquée
   reconstruit sa chronologie et perd les faits déclarés
   (`carriere.py:948-952`). La docstring de `DroitsAcquis`
   (`notionnel.py:224-226`) parle d'une cascade que la page n'affiche plus.
9. **Les variantes** : sous `rattachement_niveau_de_vie='pension'`, la part
   figée, partielle, prend la mortalité des petites pensions
   (`notionnel.py:719-723`, diviseur 20,36 au lieu de 24,58) ; le capital
   d'ouverture n'est revalorisé qu'à partir de 2027 (`notionnel.py:727`), à
   vérifier contre la date que la pension figée représente.

**Ce que le propriétaire tranche** : ce que « au contributif seul » retire —
les périodes assimilées, l'AVPF et les points de chômage, que la CNAF et
l'Unédic paient, et que le compte des scénarios 2, 4 et 6 devrait alors
porter aussi ; si une pension servie avant la bascule la traverse telle
quelle ; si une pension qui prend effet en 2026 relève de la réforme ;
l'indice du capital figé ; le salaire de référence d'une carrière courte ;
l'âge de conversion de qui a passé 65 ans.

### 167. Le scénario 6 : la rente du pilier, la garantie vieillesse et l'âge légal, là où ils servent faux — `à faire`

**D'où elle vient.** Le même audit, du 23 octobre 2026. Le Python et le
JavaScript y concordent au centime, sur onze carrières aux bords ; les défauts
sont dans les règles, et dans ce que le site en dit.

**Ce qui est à faire** :

1. **La rente du pilier, à taux technique nul et jamais revalorisée.** Elle
   divise le capital par le diviseur du compte (`capitalisation.py:672`), qui
   vaut l'espérance de vie sans actualisation, puis reste « NOMINALE et
   constante » (`revalorisation.py:1814-1823`). Le dépôt dit lui-même, de la
   pension notionnelle, que ce diviseur « ne la vaut QUE si la rente est
   ensuite revalorisée » (`revalorisation.py:1486-1491`) ; le capital du pilier,
   placé en titres sans risque, rapporte, et la rente n'en reçoit rien : la
   participation aux bénéfices des contrats de rente n'est nulle part. Rapportée
   à la courbe des taux du modèle, la rente vaut environ 0,63 fois le capital
   qui la constitue, pour les générations 1970 à 2004. `capitalisation.py:80-84`,
   `config.py:1235-1241` et `methodologie.md:1825-1830` présentent pourtant les
   deux compartiments comme « comparables au centime ». Pour la génération
   2004, dont la rente fait le tiers du total du scénario 6, une rente
   revalorisée sur les prix relèverait ce total d'environ 10 %.
2. **Sous le plancher, le site promet un gain qui n'existe pas.** La garantie
   reprend la rente volontaire euro pour euro, et le total ne bouge pas
   (`test_sous_le_plancher_les_cinq_points_volontaires_ne_rapportent_rien`,
   qui dit : « Le site doit le dire ») ; le site écrit pourtant « elle serait de
   945 € … et jusqu'à 1 050 € si vous épargnez aussi », et « 945 € par mois
   sans rien ajouter — et 105 € de plus si vous placez les cinq points »
   (née en 1995, 0,25 fois le salaire moyen) : il retranche la rente volontaire
   du total (`pages.js:4534`, `pages.js:5128`, et `castypes.py:1020`) au lieu de
   recompter la garantie sans elle. Attendu : 1 050 € sans rien placer, rien de
   plus en plaçant.
3. **L'écart d'un départ avant 65 ans, sans l'ASPA du scénario 1.** Le
   scénario 1 ne sert l'ASPA qu'à un départ à 65 ans ou plus
   (`scenarios/actuel.py:398`) ; le scénario 6, reporté à 65 ans, sert sa
   garantie dès son départ. Née en 1995, 0,25 fois le salaire moyen : partie à
   64 ans, l'écart est de +99 % (6 330 € contre 12 600 €) ; à 65 ans, +0,6 %.
   La page ne dit pas que le système actuel servirait 1 044 € par mois dès
   65 ans.
4. **Le fonctionnaire radié pour invalidité, prolongé en emploi.**
   `Carriere.prolongee` (`carriere.py:1953-2022`) poursuit la dernière ligne
   telle qu'elle est, un emploi à plein traitement, quand le README (lignes
   157-162) et la fiche `age_legal_de_la_proposition` disent que l'assurance
   invalidité couvre jusqu'à 65 ans, « l'invalidité, qui ne cotise pas ».
   Fonctionnaire d'État né en mai 1980, radié à 50 ans : 2 392 € par mois au
   scénario 6, contre 1 921 € au 1 ; déclaré en invalidité jusque-là, sa
   pension baisserait de 17 % et sa rente de 78 %. Le site ne refuse que la
   radiation de janvier (`contexte.js:905-912`) ; aucun test du scénario 6 sur
   l'invalidité.
5. **L'allocation d'isolement, sans le conjoint déclaré.** Elle ne lit que le
   champ « foyer », « seul » par défaut (`notionnel.py:516-519`,
   `saisie.js:726`, `saisie.js:1427`), quand l'ASPA du scénario 1 passe au
   barème du couple dès qu'un conjoint est déclaré (`config.py:718-726`).
   `config.py:1040-1042` dit pourtant « de sorte que les deux planchers se
   comparent ». Avec un conjoint, le scénario 1 passe au couple, et le 6 garde
   ses 250 € par mois d'isolement ; la page écrit « Garantie calculée ici pour
   une personne seule ».
6. **Un décès déclaré avant le départ, ignoré.** Né en 1980, mort le 15 juin
   2035 : le scénario 6 sert 27 293 € de pension et 5 249 € de rente en 2045,
   et les 54 247 € que le pilier transmettrait (`capitalisation.py:86-87`) ne
   sont rendus nulle part. Le décès ne sert qu'à la réversion du scénario 1.
7. **Le chômage indemnisé de fin de carrière, prolongé jusqu'à 65 ans** au-delà
   de toute durée d'indemnisation : la prolongation copie la ligne après le
   bornage (`simulateur.py:1296-1303`) ; né en 1975, au chômage de 2033 à 2037,
   l'Unédic cotise encore de 2038 à 2040.
   `limites/4-regimes-incomplets.md:711-712` ne dit que « la finit au
   chômage ».
8. **La « pension d'aujourd'hui » du scénario 6 sous une bascule passée** se
   revalorise depuis l'année de départ du scénario 1, non de la carrière
   reportée (`revalorisation.py:1382-1386`, `1429-1430`, et
   `revalorisation.js:909-957`) ; le cycle de vie prend la bonne
   (`cycle-de-vie.js:947`). Bascule 2020, née en 1960, partie à 62 ans en
   2022 : +10,65 % ; née en 1963, partie en 2025, une pension « d'aujourd'hui »
   à qui, sous la proposition, travaille encore.
9. **La garantie à rebours**, avant la bascule, déflatée par les seuls prix
   (`notionnel.py:512-520`) : 1,57 fois le salaire moyen en 1945, 1,43 en 1950,
   0,90 en 1960, contre 0,30 en 2026. La convention est déclarée
   (`limites/4-regimes-incomplets.md:659-663`), pas son ordre de grandeur.
10. **Les sorties et les textes** : la clé `rente_capitalisation_obligatoire`
    du JSON porte les deux rentes (`notionnel.py:276-285`,
    `simulateur.py:689-690`), quand le tableau retranche la volontaire ; la
    garantie dite regarder « 5 % capitalisés » (`notionnel.py:150`, `154`,
    `487-488`, `scenario-notionnel.js:177-178`,
    `limites/4-regimes-incomplets.md:637`) quand elle regarde les dix points ;
    trois, quatre ou cinq différences avec le scénario 4 (`config.py:745`,
    `notionnel.py:69`, `methodologie.md:1442`, README ligne 85) ;
    `garantie.py:7-10`, d'avant l'âge légal ; douze ou treize cas types
    (`garantie.js:7`, `garantie.py:7`).

**Ce que le propriétaire tranche** : la rente que promet le pilier — indexée,
revalorisée par la participation aux bénéfices, ou nominale à un taux
technique positif ; la date à laquelle les deux scénarios se comparent quand
l'âge légal reporte le départ ; ce que la proposition sert à qui meurt avant
son départ, et ce qu'elle prolonge après un chômage indemnisé ou une
radiation pour invalidité.

### 168. La revalorisation et la conversion des comptes : l'écart de tête, les années aux bords, et ce que le diviseur suppose — `à faire`

**D'où elle vient.** Le même audit, du 23 octobre 2026. Le Python et le
JavaScript concordent au bit sur vingt et une carrières et saisies aux bords ;
ce qui suit tient aux conventions, et à ce qu'on en dit.

**Ce qui est à faire** :

1. **L'écart de tête compare les premières pensions** (`simulateur.py:260-276`),
   quand la pension notionnelle servie suit ensuite la masse salariale, de 2,45
   à 3 % par an (`revalorisation.py:1536-1546`), et celle du scénario 1 les prix
   (1,75 %) ; la page dit « première pension » sans dire que les deux systèmes
   la revalorisent autrement (`pages.js:2634-2656`). Génération 1970 : −20,8 %
   au départ au scénario 4, −14,0 % en moyenne sur la retraite ; génération
   1990 : −29,0 % et −25,4 %. Seuls les indicateurs du cycle de vie en tiennent
   compte, dans un dépliant.
2. **Le taux d'indexation saute d'un demi-point en 2071** : l'emploi projeté
   s'arrête en 2070 à −0,50 % par an, et sa croissance est nulle ensuite
   (`donnees/macro.py:136-145`, `176-183`) ; l'indexation passe de 1,94 % en 2070
   à 2,45 % de 2071 à 2150. Rien ne le dit, ni aux limites ni dans
   `hypotheses_projection.yaml`. Capital d'un départ de 2077 : +3,6 % sur ce qui
   précède 2071 ; pensions servies après 2070 : +16 % en trente ans.
3. **Le diviseur d'une liquidation passée lit la mortalité observée après
   coup** : la table de génération y dépasse, à 65 ans, la table du moment de
   l'année de 5,4 % (1950) à 11,9 % (1980). `methodologie.md:450-460` ne la
   justifie que pour l'avenir ; un compte de 1970 ne pouvait connaître la
   mortalité de 1990.
4. **La pension notionnelle servie baisse de 4 % en 2020** (masse salariale
   −4,02 %), en euros courants : aucun plancher, et rien ne le dit.
5. **Le stock « prix » contre la fiche** : par défaut, une pension rétroactive
   d'avant la bascule est servie aux prix après elle (`config.py:296-306`),
   quand la fiche `indexation_du_compte` dit que « toute pension des scénarios
   2 à 6 » suit la règle du compte ; liquidée en 2010, elle vaut en 2050 1,18
   fois sa valeur réelle de départ, contre 1,43.
6. **Le net des scénarios 2 à 6 à la tranche de CSG du scénario 1**
   (`contexte.py:1019-1025`, `1075-1076`), déclaré
   (`limites/5-ante-ter-net-et-brut.md:26-28`) mais contraire au barème que la
   ligne 19 du même document dit garder : génération 1975, au salaire moyen, le
   scénario 2 brut de 729 € par mois s'affiche à 661 € net, quand son propre
   revenu l'exonère. Les fiches `csg_des_pensions_selon_le_revenu` et
   `cotisation_maladie_pensions_complementaires` sont sans décision.
7. **La fiche du diviseur muette sur la table par niveau de vie**, qui est le
   défaut depuis le 21 septembre 2026 (`config.py:649`, `conversion.py:198-211`) :
   génération 1975, départ à 64 ans, diviseur de 21,99 à 0,5 fois le salaire
   moyen, 25,56 à 1 fois, 27,55 à 2,5 fois, contre 24,91 pour la table commune.
8. **La variante à préfinancement ν** : la garantie différée revalorise la
   pension sans la diviser par 1 + ν (`notionnel.py:545-548`,
   `scenario-notionnel.js:219-224`), quand la règle de service le fait
   (`revalorisation.py:1537-1546`) ; à ν = 1,6 %, 306 € de complément au lieu
   d'environ 931 €. Aucun test.
9. **Le mode « explicite » de l'âge de référence**, promis par la fiche
   `age_de_reference`, `methodologie.md:418-419` et `age_reference.py:34-38`,
   n'est lu par aucun code ni aucun réglage.
10. **Les textes périmés** : README, lignes 391 (« ne revalorise pas les
    pensions servies »), 469, 534 et 563 (une septième puis une neuvième règle,
    sans huitième) ; `config.py:547-553` et `pages.js:2616-2617` ; le triple lock
    « par défaut » de `notionnel.py:6` et `conversion.py:16` ;
    `indexation.js:181-184`, que son jumeau Python a corrigé ;
    `limites/2-indexation.md:7` ; « G(64, 2026) » à `methodologie.md:1158` et
    `1192` ; « ×1,15 au bout de vingt ans » à `revalorisation.py:1496`.

**Ce que le propriétaire tranche** : quel écart sert de chiffre de tête — la
première pension, ou la pension sur la vie ; la convention d'après 2070 ; la
mortalité que l'on prête à un compte rétroactif ; un plancher nominal des
pensions servies ; la tranche de CSG de chaque scénario.

### 169. Le régime unique de la bascule, statut par statut : ce qu'il prélève, qui y est employeur, et ce que le texte en dit — `à faire`

**D'où elle vient.** Le même audit, du 23 octobre 2026. À compter de la
bascule, les scénarios 2 à 6 portent tous les statuts au régime unique
(`fusion_des_regimes`, que la couche `comptes_notionnels` ajoute), et le code
décide en silence de ce qu'il fait des statuts qui ne sont ni salariés du privé
ni indépendants. Rien n'en est écrit ; plusieurs phrases du texte de la
proposition le contredisent.

**Ce qui est à faire** :

1. **Le scénario 4 après la bascule.** Le README le dit aux taux réels de chaque
   régime — « celle réellement versée — jusqu'à 82,28 % du traitement en
   2026 » (ligne 29), « le scénario 4 porte les taux réellement en vigueur »
   (lignes 86-91), « 18 % au lieu des 46,4 % que le 4 porte au compte »
   (lignes 684-688) — ; le code lui donne le régime unique dès 2026 : la
   fonctionnaire d'État née en 1975 a 55,2 % au compte en 2025, 25,83 % en 2026
   et 2030, et le 6, 18 %. Le README est le texte de la proposition : l'un des
   deux est à corriger.
2. **Qui y a un employeur** : `a_un_employeur` (`compte.py:394-419`) le déduit
   de la part salariale et du routage d'un entrant d'aujourd'hui. Le
   parlementaire passe de 10,85 % à 25,83 % des deux côtés, comme un
   indépendant ; l'agent général d'assurance gagne 15,4 points « employeur » ;
   le membre du CESE, dont « le Conseil ne verse pas de part employeur », en
   gagne un ; le médecin conventionné perd la part de l'assurance maladie (ASV)
   dès 2026, et l'auxiliaire médical de même. « Pour un non-salarié […] les
   quatre se réduisent à deux » (README, lignes 40-43 ; `part_patronale.yaml` ;
   `notionnel.py:51-52`) est faux pour eux : médecin de secteur 1, 20 378 € au
   scénario 2 et 25 118 € au 4 ; la page écrit à la fois « L'employeur verse ici
   15,1 % du total » et « vous n'avez pas d'employeur » (`pages.js:6769`). Le
   test (`test_simulateur.py:856-874`) ne vise que trois statuts.
3. **Les assiettes minimales et les forfaits disparaissent** : à 0,1 fois le
   salaire moyen, l'exploitant agricole passe de 50,5 % de son revenu au compte
   en 2025 à 25,8 % en 2026, le ministre du culte de 54,3 % à 10,4 % ;
   `methodologie.md:744-750` n'annonce qu'une hausse pour les indépendants.
4. **Les régimes d'outre-mer de compétence locale** — la CAFAT, la CPS de
   Polynésie, Wallis-et-Futuna — passent au régime unique (salarié calédonien :
   7,35 % au scénario 2 en 2025, 10,45 % en 2026), quand
   `limites/4-regimes-incomplets.md:81-82` rappelle que la loi organique les
   confie aux assemblées locales.
5. **Le revenu conventionnel** des collaborateurs, des aides familiaux et des
   congréganistes, auquel le taux unique s'applique après 2026 comme à un
   revenu réel.
6. **L'activité après la première pension** : le scénario 1 en tire une
   seconde pension (1 788 € par an pour quatre ans au salaire moyen) ; les
   comptes des scénarios 2 à 6 n'en reçoivent rien, et rien ne le dit.
   `droits_apres_la_premiere_pension`, le cumul et la retraite progressive sont
   sans décision.
7. **Les fiches du droit réel qui alimentent le compte sans décision** :
   `assiette_minimale_independants`, `assiette_sociale_independants`,
   `cotisation_vieillesse_independants`, `conjoint_collaborateur_independants`,
   `chomage_retraite_complementaire`, `financement_chomage_complementaire`,
   `micro_social_abattement`, `rci_seuil_premiere_tranche`, les `asv_*`,
   `organic_conjoints_de_commercants`, `points_au_prorata_des_cotisations`,
   `agirc_arrco_valeur_achat` (docs/etat.md, « Les domaines sans décision »).
   La fiche `compte_notionnel` ne nomme que l'Unédic pour tiers payeur, quand
   le code porte aussi l'État pour l'ASS et le FNE, et 3 % de l'allocataire
   (`compte.py:1085-1135`).

**Ce que le propriétaire tranche** : le taux du scénario 4 après la bascule ;
un « tiers payeur » statut par statut — l'assemblée, l'assurance maladie, le
mandant — et ce qu'il verse au régime unique ; un plancher d'assiette ;
l'outre-mer ; ce que vaut l'activité après la première pension.

### 170. La page Coût des scénarios 2 à 6 : la dette, la recette et la réversion qu'elle compte autrement que le modèle — `à faire`

**D'où elle vient.** Le même audit, du 23 octobre 2026 ; le coût refait sous
les réglages de référence redonne au bit `data/derive/agregats.json`. Ni
l'action 157 (la population) ni l'action 47 (la reprise de la garantie) ne
couvrent ce qui suit.

**Ce qui est à faire** :

1. **La moitié « qui éteint de la dette » n'éteint rien.** Le README (lignes
   1072-1077, 1095-1098) et la page Coût (`pages.js:11537-11538`, et
   `pages.js:16450` au programme) disent que la moitié des trois postes que la
   proposition n'encaisse plus éteint de la dette, « à commencer par celle que
   le système de retraite porte » ; la même note dit « Rien de tout cela ne
   change le solde ci-dessus » (`pages.js:11550-11553`), et `calculer_dette` ne
   cumule que les soldes (`cout.py:2060-2066`) : `Restitution.eteint_de_dette`
   (`restitution.py:185`) n'est lu par aucun calcul. La seule moitié des
   impôts affectés, portée à la dette de la retraite, ferait passer le solde de
   2026 du scénario 6 de −0,70 à +0,37 point de PIB et sa dette de 2070 de 70 %
   à environ 2 % du PIB, ce qui renverse « 70 % contre 66 % pour le système
   actuel » (README, lignes 972-975).
2. **La recette des scénarios 2 à 5 ne suit pas le régime unique.** Leurs
   comptes reçoivent dès la bascule le taux du régime unique — la
   fonctionnaire d'État passe de 55,2 % à 25,8 %, l'artisan de 13,0 % à
   25,8 % —, et leur recette reste celle du droit en vigueur
   (`CLES_RECETTES`, `cout.py:229-239` ; `cout.py:1444-1448`). Le README écrit
   « leur recette ne bouge pas » (ligne 1064) et `test_cout.py:3548-3573` le
   tient ; `scripts/solde_fusion.py` dit « La page ne le compte pas ». Solde
   moyen 2026-2070, de la page au régime unique : scénario 2, +7,97 à +7,14 ;
   3, +1,55 à +0,66 ; 4, +2,09 à +1,26 ; 5, −0,04 à −0,93. L'accueil dit que
   les 18 % coûtent 2,3 points de PIB par an (`pages.js:16484`,
   `scripts/mesures_accueil.py:76`), la page Coût et le README 3,1. Mesuré le
   20 septembre 2026, puis archivé sans suite.
3. **Les engagements du bilan « à la suédoise » comptent la réversion des
   notionnels**, qui n'en servent pas : la masse de chaque système y est
   multipliée par le facteur de réversion (`cout.py:4686-4688`, `4782-4788`),
   quand `masse_du_scenario` ne leur sert que les droits directs
   (`cout.py:761-770`). Engagement de 2025, en points de PIB : scénario 2,
   163,4 au lieu de 149,5 ; 4, 393,6 au lieu de 360,0 ; 6, 361,1 au lieu de
   330,1 ; le ratio d'équilibre du 6 passerait de 0,91 à 1,00. Aucun test.
4. **La réversion déjà servie à la bascule, retirée aux scénarios 3 et 5.**
   Ils ne la servent plus, « aux veuves d'avant comme à celles d'après »
   (`limites/5-bis-cout-agrege.md:145-152`, `cout.py:740-751`), quand la fiche
   `valorisation_des_droits_acquis` dit qu'« une pension qui a pris effet avant
   ne bouge pas » et le README (ligne 28) que qui a liquidé garde sa pension.
   C'est, mesuré par l'audit, toute l'économie du scénario 3 en 2026 :
   environ 1,5 point de PIB.
5. **Les cohortes que la bascule sépare de leur génération de grille**, aux
   scénarios 3 et 5, prennent la pension de celle-ci (`cout.py:3006`) ; le
   même défaut n'a été corrigé que pour le 6 (`cout.py:2673-2676`). Le rapport
   du 3 vaut 0,99797 en 2025 au lieu de 1 ; le cumul 2025-2070 est sous-estimé
   de 41 milliards au 3 et de 40 au 5. `test_cout.py:446-463` tolère 0,5 % et
   ne vise que le 3.
6. **L'ASPA et les majorations que les comptes suppriment restent dans leur
   dépense projetée** : le rapport multiplie la dépense du COR, FSV compris
   (`cout.py:4337`, `cout.py:1330-1332`), environ 0,04 point de PIB au
   scénario 2, 0,10 au 4 et 0,09 au 6, en plus de sa garantie ; aucun cas type
   n'a trois enfants (`castypes.py:352`), et les majorations pour enfants passent
   aux notionnels au prorata, environ 0,14 point aux 4 et 6. L'effet retour,
   lui, sert l'ASPA aux scénarios 2 à 5 (`effet_retour.py:12-15`, `105-107`,
   tenu par `test_effet_retour.py:143-158`), que la couche `comptes_notionnels`
   neutralise.
7. **La garantie, chiffrée sur une population incomplète et une épargne
   universelle** : son effectif est celui des droits directs
   (`cout.py:3345-3349`), quand le 6 supprime la réversion et que
   199 925 résidents de 65 ans et plus ne touchent qu'une réversion
   (`tests/temoins/pensionnes_de_2022.json`), environ 1,3 milliard par an ; et
   elle compte chez tous la rente des cinq points volontaires
   (`cout.py:2652`, `2979-2984`), que le README dit « une convention de
   comparaison » et non un comportement : sans elle, la garantie de 2070 passe
   de 14,0 à 16,5 milliards (+18 %).
8. **Les soldes du 6 et du 1 se comparent sur deux périmètres** : « −1,03 %
   contre −1,13 % » (README, lignes 1057-1060), quand le 1 garde l'ASPA dans son
   solde et que le 6 sort sa garantie (`cout.py:2405-2410`) ; garantie
   comprise, le 6 est à −1,27 %.
9. **Les textes** : la docstring de `cout.py` (lignes 17-28, 88-92, 97-102,
   776-780) ; le README, lignes 391, 789 et 1009-1010 ; la numérotation des
   systèmes, de 1 à 6 au README et de 1 à 4 sur la page (`pages.js:200-204`) ;
   l'âge du 6 que les leviers lisent sur les retraités du droit en vigueur
   (`leviers.py:64-66`), dit ni sur la page ni aux limites.

**Ce que le propriétaire tranche** : de quelle dette parle « la moitié éteint
de la dette » ; si la recette des scénarios 2 à 5 suit leur régime unique, ou
si le régime unique les quitte ; si les scénarios 3 et 5 servent la réversion
déjà liquidée ; si la garantie sert qui n'a aucune retraite obligatoire, et sur
quelle part de verseurs volontaires elle se chiffre.

### 171. Les couches de la proposition gouvernent-elles le calcul ? Ce qu'elles gardent ou neutralisent n'y agit pas, et le moteur ne le refuse pas — `à faire`

**D'où elle vient.** Le même audit, du 23 octobre 2026. `data/CLAUDE.md` dit
qu'« une variante s'écrit en couche, jamais dans le code, et le moteur refuse
ce qu'il ne sait pas calculer » ; `scenarios/univers.py:10-15`, qu'il « refuse
ce qu'il ne sait pas faire… c'est ce qui rend l'ajout d'un univers sans
risque » ; `docs/architecture.md`, § 4.8, qu'« une fiche neutralisée n'accorde
rien ».

**Ce qui est à faire** :

1. **Les opérations `garder`, `neutraliser` et `remplacer_une_version` d'une
   couche d'univers ne sont ni appliquées ni refusées.** `calcul_notionnel`
   (`scenarios/univers.py:92-159`) ne lit que les ajouts, les changements de
   paramètre et les couches d'un seul calcul ; ce que le compte ne sert pas —
   le minimum, l'ASPA, l'AVPF, la réversion —, il ne le sert pas parce que son
   code ne les connaît pas. Une copie des couches où `comptes_notionnels` garde
   l'ASPA et l'AVPF et ne neutralise plus le minimum ni la réversion se charge
   sans erreur, passe `calcul_notionnel` pour les cinq univers, et rend des
   résultats identiques au centime ; seul le décompte « sans décision » bouge,
   de 129 à 145. Une opération `remplacer_une_version` est acceptée, puis
   ignorée ; `neutraliser {domaine: minima}` est refusée dans une couche d'un
   seul calcul, acceptée et sans effet dans une couche d'univers.
   `tests/test_univers.py` (19 tests) ne vérifie jamais l'effet d'une décision.
2. **Le report de l'âge légal, rattaché en dur au scénario 6** dans la
   comparaison (`simulateur.py:205-206`, `simulateur.js:156-157` :
   `scenario == "notionnel_liberal"`) : posé sur le scénario 4, son compte
   liquiderait en 2040 et la comparaison lui garderait la carrière de 2037.
   L'action 130 (phase 7) note déjà que le pilote et les pages lisent les
   univers par leur identifiant.
3. **Les décisions que le code prend sans la carte** : la garantie applique la
   condition de résidence de l'ASPA (`notionnel.py:529-532`) que la carte dit
   `residence_et_minimum_vieillesse` sans décision ; le compte crédite les
   cotisations que l'Unédic verse, sans décision non plus.

**Ce que le propriétaire tranche** : si les décisions des couches restent
déclaratives — un test refuse alors toute opération que le moteur n'exécute
pas, et confronte chaque neutralisation à ce que le compte sert —, ou si le
moteur les exécute.

### 172. Ce que le README, le site et les sorties disent des scénarios 2 à 6, et ce que les tests n'en tiennent pas — `à faire`

**D'où elle vient.** Le même audit, du 23 octobre 2026 : ce qui suit ne change
aucun calcul, mais ce qu'on lit des scénarios 2 à 6, ou ce qui les garde.

**Ce qui est à faire** :

1. **Les témoins ne figent pas l'indexation par défaut** : 881 des 889 cas de
   `tests/temoins/simulations.json` tournent sous `triple_lock_inverse`, la base
   de `scripts/construire_temoins.py:53-61`, et la boucle des règles
   (`construire_temoins.py:526-530`) omet la masse salariale, qui est le défaut.
   Aucun témoin ne fait varier `part_cotisation`, `foyer`, `reprise`, `frais` ni
   `taux` ; le test tiré au sort ne fait varier ni ceux-là, ni
   `contribution_etat`, `stock`, `esperance_vie`, `emploi`, et tire la bascule
   entre 1945 et 2065 (`test_web.py:694`). Aucun test ne simule une carrière
   sans cotisation ; `test_univers.py:185-209` ne contrôle que trois des règles
   de cotisation que le compte applique.
2. **Le réglage « Part de la cotisation portée au compte »** ne change que le
   système 2, qui garde son libellé : sous `totale`, « 2. Ce que vous avez
   cotisé, part salariale seule » affiche le montant du système 3, sa
   description « 11,3 % du brut » (`pages.js:5199`) et l'info-bulle
   (`pages.js:7053`) inchangées ; libellés en dur à `pages.js:184-189`.
3. **Le tableau du Python** attribue aux « scénarios 2 et 3 » et « 4 et 5 » les
   cotisations des comptes rétroactifs (`simulateur.py:448-457`, et l'exemple du
   README, lignes 677-679), quand le compte du 3 n'en a reçu qu'une part ; sa
   ligne de la garantie cite les ressources au départ et non à l'ouverture
   (`simulateur.py:488-493`) : « 427 € portent la pension de 7 619 € au plancher
   de 8 999 € » ne tombe pas juste. Le JSON des deux moteurs
   (`simulateur.py:691-707`, `simulateur.js:524-537`) n'a pas de quoi recalculer
   le complément ; il porte `cotisations_employeur` nul après la bascule au 6
   (`compte.py:440-442`), et range l'année du départ dans le compte des
   scénarios 3 et 5 qui ont déjà liquidé (`notionnel.py:641-645`).
4. **Le README** : « à 50 ans la garantie vieillesse n'est pas ouverte »
   (lignes 79-81), quand le modèle sert 427 € par an à l'agent SNCF dès 65 ans,
   ligne que `scripts/construire_tableaux_md.py:209-217` coupe du bloc ; la
   retenue des fonctionnaires « alignée sur l'effort contributif total du
   privé » (ligne 396), qui ne l'est que sous `totale_alignee` ; « le compte
   rétroactif à 18 % pour tous » (ligne 392), que la ligne 31 contredit.
5. **Le site** : « systèmes 2 à 6 seulement » (`pages.js:833`, `841`) sur un
   site qui numérote de 1 à 4 ; « retiré des six totaux … dans les quatre
   systèmes » (`pages.js:5248`) ; la description du système 3, fixe quel que
   soit le statut (`pages.js:5205`, « les 28 % prélevés aujourd'hui ») : pour un
   artisan, les systèmes 2 et 3 affichent le même montant, sans rien qui dise
   pourquoi ; sous une bascule passée, la ligne « salaire » des quatre systèmes
   montre celui de la première année.
6. **Les textes du code** : `regimes.py:1078-1085` et `notionnel.py:46-48`
   (« trois régimes », la SNCF « de 2007 à 2018 », quand
   `contribution_employeur_public.csv` en porte neuf et la SNCF depuis 1992).

**Ce que le propriétaire tranche** : si le réglage « Part de la cotisation
portée au compte » reste sur le site, et sous quel libellé.

---

## Les actions en cours

### 47. La garantie vieillesse est une avance : la reprise sur succession, sa règle et son chiffrage — `en cours`

**Reprise, au 22 octobre 2026.** La garantie, avance reprise sur la succession
dès le premier euro, est au programme et chiffrée sur la page Coût en brut,
reprises et net, d'après le patrimoine des ménages (INSEE, COR), que le
patrimoine des défunts de 2018 recoupe (`macro/patrimoine_defunts.csv`) : une
succession y couvre une avance de trois à neuf points de moins qu'un ménage.
Aucune source publique ne donne la couverture par tranche de pension (fichier
de l'enquête hors de portée, DG Trésor lue). Le programme dit pourquoi il
reprend là où l'Assemblée a voté, le 11 juin 2026, la fin de la récupération
de l'ASPA. Reste au propriétaire le choix de reprendre sur le patrimoine des
défunts. Détail : les notes des 11, 12 et 22 octobre 2026.

**Demande.** « Dans notre cas, la reprise sur succession est dès le premier
euro + on prend des intérêts pour ne pas y perdre au niveau des finances
publiques. » Puis, sur la règle proposée : « Tout me va là-dedans. Il faut
juste faire attention à ce que les héritiers enfants ne paient pas plus que ce
qui est compris dans l'héritage. Il faudrait aussi faire attention aux
personnes qui feraient des dons pour éviter la reprise sur héritage ; c'est
une vraie stratégie d'évitement qu'il faut prendre en compte dans la règle. »

**Ce que ça change de nature.** Jusqu'ici la garantie était décrite comme une
allocation financée par l'impôt, et le 20 septembre au matin le dépliant du
coût, `limites.md` et le point 3 de l'action 35 disaient même qu'elle n'était
pas récupérable, à la différence de l'ASPA. Reprise dès le premier euro avec
intérêts, elle devient une AVANCE de l'État gagée sur le patrimoine, un prêt
viager public. Le coût net pour les finances publiques se réduit à ce qui est
servi à ceux qui meurent sans rien laisser, plus le portage entre le versement
et la succession, que l'intérêt annule en valeur actuelle si son taux est au
moins celui auquel l'État emprunte et si la succession couvre la dette.

**La règle, telle que le programme l'écrit désormais** (dépliant « Le plancher,
et ce qu'il change pour les petites pensions », `_programme_garantie` et
`programmeGarantie`) :

1. Ce que la garantie verse est une créance de l'État sur le bénéficiaire ;
   elle porte intérêt au taux auquel l'État emprunte, capitalisé.
2. Elle est reprise sur la succession dès le premier euro : ni seuil d'actif
   net, ni plafond par année servie, à la différence de l'ASPA.
3. **Premier garde-fou, les héritiers.** La créance ne s'exerce que sur ce que
   la succession contient. Les héritiers ne sont jamais tenus sur leurs biens
   propres ; ce que l'actif ne couvre pas est abandonné, et c'est cette part-là,
   et elle seule, que l'impôt finance. C'est déjà la construction de
   `L. 815-13` CSS, où la récupération porte sur « la fraction de l'actif net
   qui excède un seuil ».
4. Le logement est repris comme le reste, mais la reprise attend le décès du
   conjoint survivant qui l'occupe, les intérêts courant entre-temps. *Point
   posé par la session, à retourner si le programme en décide autrement.*
5. **Second garde-fou, les donations.** Les donations faites depuis
   l'ouverture de la garantie, ou dans les dix ans qui l'ont précédée, sont
   réintégrées : la créance se poursuit contre le donataire, à hauteur de ce
   qu'il a reçu et jamais au-delà. Les primes d'assurance-vie versées après
   65 ans sont traitées de même, contre leur bénéficiaire. Et la créance est
   garantie par une hypothèque légale inscrite dès le premier versement, de
   sorte qu'un bien donné la porte avec lui : pour l'immobilier, c'est la
   parade la plus simple, la charge suit le bien. *Le délai de dix ans et le
   seuil de 65 ans pour l'assurance-vie sont posés par la session.*

**Ce que le droit fait déjà, lu dans l'index LEGI le 20 septembre 2026.**
`L. 815-13` CSS (LEGIARTI000048697753, en vigueur depuis le 1er janvier
2024) : les sommes servies au titre de l'ASPA « sont récupérées après le
décès du bénéficiaire dans la limite d'un montant fixé par décret », sur « la
fraction de l'actif net qui excède un seuil dont le montant est fixé à
100 000 euros au 1er septembre 2023 et revalorisé » ; hypothèque légale ;
prescription de cinq ans ; pour un couple, l'allocation « est réputée avoir
été perçue pour moitié par chacun ». Le recours contre le donataire existe
pour l'aide sociale départementale : l'article 146 du code de la famille et de
l'aide sociale (LEGIARTI000006681336, version 1997) ouvrait le recours
« contre le donataire lorsque la donation est intervenue postérieurement à la
demande d'aide sociale ou dans les dix ans qui ont précédé cette demande » et
« contre le légataire » ; il est codifié depuis 2000 à `L. 132-8` CASF, que
l'index thématique ne porte pas et qu'il faudra lire sur Légifrance pour la
version en vigueur (le recours contre le bénéficiaire d'un contrat
d'assurance-vie y a été ajouté depuis, à confirmer). Les montants 2026 de
l'ASPA lus sur service-public le même jour : seuil de récupération
108 586,14 € en métropole, 150 000 € outre-mer, plafond de reprise 8 463,42 €
par an pour une personne seule et 11 322,77 € pour un couple ; environ
120 millions d'euros récupérés par an.

**Le contexte à assumer par écrit.** Le 11 juin 2026, l'Assemblée nationale a
adopté à l'unanimité, en première lecture, une proposition de loi qui supprime
la récupération de l'ASPA pour les propriétaires et la remplace par un forfait
logement d'environ 40 € par mois ; le texte est au Sénat, et les débats ont
cité 300 000 ayants droit qui renoncent à l'ASPA par crainte de la reprise. La
proposition du dépôt va à rebours, et il faudra le dire sur la page.

**Ce qui est fait le 20 septembre 2026.** La règle est écrite dans le dépliant
du programme, dans les deux moteurs. La note « Deux corrections » du dépliant
« Ce que coûte la garantie vieillesse » ne dit plus que la garantie ne se
récupère pas : elle dit que le coût affiché est brut, avant reprise, et que ce
que la reprise rendrait n'est pas chiffré. `limites.md`, section « Le scénario
6, et ce que sa garantie ne voit pas », dit la même chose. Aucun paramètre n'a
été ajouté à `config.py` : un réglage que rien ne calcule serait un réglage
qui n'existe pas (action 40).

**Ce qui reste : chiffrer le net.** Le modèle n'a ni distribution de
patrimoine par niveau de pension, ni mortalité selon le patrimoine. Il faut :

1. *Une distribution de patrimoine des retraités par tranche de pension.*
   INSEE, enquête Histoire de vie et Patrimoine (patrimoine net des ménages
   retraités par décile de revenu) ; à défaut, DGFiP, statistiques des
   successions déclarées (actif net par tranche). Chaque série au manifeste
   des sources avec son `source_id`.
2. *Un stock d'avances avec intérêts.* La page Coût sait déjà tenir un stock
   qui porte intérêt, celui de la dette du système (`_cout_detail_dette` et sa
   jumelle) : la même mécanique, alimentée par le flux brut de la garantie et
   vidée au décès par ce que la succession couvre, donne la ligne « avances en
   cours » et la ligne « reprises de l'année ».
3. *Le net.* Flux brut moins reprises de l'année, en part de PIB, sur la
   trajectoire ; et dans le tableau poste par poste, la ligne « pour mémoire »
   de la garantie en deux lignes, brut et reprises.
4. *Le non-recours de la reprise.* Une reprise dès le premier euro dissuade
   plus qu'un seuil à 108 586 € : la part des ayants droit qui refuseraient la
   garantie est un paramètre à afficher, pas une hypothèse cachée.

**Fichiers.** `src/retraite_notionnelle/web/pages.py` et `moteur/js/pages.js`
(dépliant du programme, note du coût) ; `docs/limites.md` ; à venir,
`src/retraite_notionnelle/cout.py` et `moteur/js/cout.js` (le stock),
`data/reference/macro/` (le patrimoine), `data/sources.yaml`.

**Le même jour, plus tard : le recours, tranché à un sur deux.** Trois
questions posées de suite — « ça donne quoi sur notre scénario 6 ? », « on
serait à 9,2 % de personnes qui rentrent dans les critères actuels de l'ASPA »,
« le but était d'estimer le coût de notre mesure par rapport aux statistiques
actuelles de non-recours » — puis la décision : « on prend l'hypothèse que
seulement un sur deux réclame ». Ce qui a été établi en chemin, hors du modèle
et à hypothèses affichées :

- *Les 9,2 %.* Source exacte non retrouvée, chiffre cohérent : 723 020
  allocataires fin 2023 (DREES, fiche 26 de l'édition 2025), 4,3 % des 62 ans
  ou plus ; avec un non-recours de moitié, 1,05 à 1,45 million de personnes
  remplissent les critères, 7 à 10 % des 65 ans et plus. Sur la seule pension
  directe de l'EIR 2020, 32 % des retraités sont sous le plafond d'une
  personne seule et 23 % sous la moitié du plafond d'un couple : ce sont les
  ressources du foyer qui ramènent ces 23 à 32 % vers 9 %. La garantie
  individualisée sur les pensions du système 4 en touche 41 %, soit quatre à
  cinq fois plus, et le coût suit la population, non le montant du plancher.
- *L'avance à la mort d'un bénéficiaire.* Complément moyen 372 € par mois,
  servi 24,2 ans (espérance de vie à 65 ans du modèle, génération 2026) :
  108 k€ sans intérêt réel, 122 k€ à 1 %, 138 k€ à 2 % ; en régime permanent,
  un stock d'avances de l'ordre de 370 Md€, douze points de PIB.
- *Ce que la succession couvre.* Patrimoine brut des ménages retraités selon
  le COR (16 décembre 2021, sur l'enquête Histoire de vie et Patrimoine 2018) :
  médiane 190 200 €, deuxième décile 23 000 €, sept sur dix propriétaires ;
  pour le quart aux revenus les plus bas, médiane 36 800 € et moyenne triple.
  Sur la distribution basse, la succession couvre 40 % de l'avance d'une
  personne seule et 26 % de deux avances d'un couple ; sur la distribution de
  tous les retraités, 75 % et 65 %.
- *Le net, en régime permanent, brut 30,5 Md€ au plancher de base.* Tous
  réclament : reprises 12 à 20 Md€, net 10 à 19. Un sur deux réclame, comme
  l'ASPA : versé 15,3, reprises 6 à 10, net 5 à 9. Renoncent ceux dont la
  succession couvrirait l'avance : versé 15 à 25, reprises 5 à 6, net 10 à
  19 — le même net que « tous », parce que qui refuse est qui aurait remboursé
  en entier. Le coût net de la mesure est donc la garantie servie à ceux dont
  la succession ne peut pas la couvrir, et le non-recours uniforme est le seul
  à faire baisser ce net, pour une mauvaise raison : il suppose que les plus
  pauvres aussi renoncent, ce que la DREES observe. Les vingt premières
  années, l'État verse sans reprendre. Script d'estimation non versionné, hors
  du modèle ; la distribution de patrimoine des bénéficiaires reste la donnée
  qui manque.

**Ce qui est codé.** `Parametres.taux_recours_garantie = 0.5` et son jumeau
dans `config.js` ; `GarantieDistribution` prend le taux, `GarantieProjetee`
porte `ayants_droit` et `taux_recours` à côté des bénéficiaires et du coût,
qui sont ceux qui réclament ; la ligne « dont garantie » de la trajectoire, le
dépliant de la garantie (colonne « Sous le plancher » ajoutée, paragraphe
« Un ayant droit sur deux réclame ») et la ligne pour mémoire du tableau poste
par poste suivent ; le dépliant du programme dit que la garantie se demande et
se refuse. Un test tient le taux et refuse une part hors de ]0, 1]. Ce que ça
déplace, plancher majoré sur la trajectoire : la garantie de 2024 passe de
39,0 à 19,5 Md€ et le surcoût pour l'impôt de 31 à 11,7 Md€ ; en 2026, la
ligne pour mémoire du tableau poste par poste de 30,5 à 15,0 Md€ (1,02 à 0,50 %
du PIB) ; en 2070, 0,46 % du PIB au lieu de 0,92. Le simulateur d'une
carrière ne connaît pas ce taux : qui réclame la reçoit en entier.

**Le même jour, encore : la reprise dans le net, sur la page.** « Et avec la
reprise sur succession dans le net ? », puis « oui, code-le sur la page
Coût ». `_reprises_successions` dans `cout.py`, et `reprisesSuccessions` dans
`moteur/js/cout.js`, suivent les avances de la garantie à compter de la
bascule : chaque euro versé porte intérêt au taux réel que la courbe des taux
sans risque implique (le forward à un an de la dette, déflaté par les prix de
la projection), la population des bénéficiaires est supposée stationnaire sur
la courbe de survie à 65 ans de la génération de la bascule, un bénéficiaire
d'un âge donné porte les compléments moyens des années écoulées, au plus
autant que son âge lui en laisse, et les décès libèrent ces avances ; la
succession en rend la part `Parametres.part_reprise_garantie`, la moitié par
défaut, réglage `reprise` du formulaire (0 à 100, page Coût seulement).
`GarantieProjetee` porte `avances_liberees_constants`, `reprises_constants`,
`stock_avances_constants` et `taux_reel` ; `AvenirAnnuel` expose
`reprises_constants`, `part_pib_reprises` et `garantie_nette_constants`,
`Avenir` un `cumul_reprises`. Sur la page : deux lignes de plus sous « dont
garantie » dans le tableau de la projection, « dont reprises » (en moins) et
« garantie nette » ; dans le dépliant, un paragraphe et le tableau « La
reprise sur succession dans la trajectoire » (versé, avances libérées,
reprises, net, part du PIB, avances en cours) ; une quatorzième réserve dit
que la couverture est une hypothèse. Un test tient que rien n'est repris
avant la bascule, que les reprises sont la part couverte des avances
libérées, que le net est le versé moins les reprises, et que le stock monte.
Ce que ça donne, au réglage par défaut, plancher majoré, diviseur par niveau
de vie (le défaut depuis le même jour) : en 2070, 17,9 Md€ versés, 23,8
libérés par les décès, 11,9 repris, 6,0 nets, 0,16 % du PIB contre 0,5 brut ;
de 2026 à 2070, 849 versés, 344 repris, 505 nets ; un stock d'avances en
cours de 383 Md€ à l'horizon, dix points de PIB, qui plafonne quand les décès
libèrent autant que la bascule verse. Les vingt premières années restent
presque brutes : 20,8 net en 2026, 12,5 en 2040. Ce
que le modèle ne distingue pas, et que la règle prévoit : le report au décès
du conjoint survivant, la donation réintégrée, l'assurance-vie. Ce qui reste
du point 1 ci-dessus, la distribution de patrimoine des bénéficiaires, est
désormais ce qui remplacerait le réglage par une donnée.

**Le premier temps du point 1, fait le 20 septembre 2026 : la couverture
calculée, sur ce qui est publié.** « Est-ce qu'on peut faire des recherches
pour enlever cette limite ? », puis « oui, commence par le premier temps ». Ce
qui existe de publié : l'INSEE donne les déciles de patrimoine de tous les
ménages (Insee Focus n° 287, début 2021 ; page « Distribution du patrimoine
des ménages », début 2024) et les moyennes et médianes par âge, dans deux
classeurs de quelques kilo-octets ; le patrimoine des retraités selon leur
PENSION n'est publié nulle part, et la seule publication qui croise le
patrimoine des ménages retraités et leur REVENU est le document n° 3 du COR
du 16 décembre 2021, sur l'enquête Histoire de vie et Patrimoine 2018 —
médiane 190 200 €, moyenne 296 600 €, deuxième décile 23 000 €, neuvième
622 900 € pour les ménages retraités ; médiane 36 800 € et moyenne triple pour
le quart au revenu disponible le plus bas. Les médianes des deuxième, troisième
et quatrième quartiles sont dans un graphique que `lecture_pdf.py` ne lit pas.
Fait : `scripts/fetch/insee_patrimoine_menages.py` lit les deux classeurs de
l'INSEE et porte en dur les six valeurs du COR, avec leur `source_id`, dans
`data/reference/macro/patrimoine_menages.csv` (78 lignes, `haute` ; deux
entrées au manifeste, `insee_patrimoine_menages` et `cor_patrimoine_retraites`).
`donnees/patrimoine.py` et `moteur/js/patrimoine.js` en tirent, par
population, ce qu'une succession couvre d'une avance : une fonction de
quantile linéaire par morceaux quand la population publie des quantiles,
plate au-delà du dernier ; une log-normale calée sur la médiane et la moyenne
sinon, avec la formule 7.1.26 d'Abramowitz et Stegun des deux côtés pour que
les deux moteurs rendent le même chiffre. `_reprises_successions` calcule la
part couverte quand `part_reprise_garantie` est `None`, désormais le défaut :
chaque tranche de pension sous le plancher reçoit l'avance qu'elle
constituerait (complément annuel capitalisé au taux réel moyen sur la durée
moyenne d'une avance), la part que la succession en couvre est celle du quart
le plus modeste pour le premier quart des retraités, celle de l'ensemble à
partir de la médiane, et le mélange linéaire entre les deux ; la part retenue
est la moyenne pesée par les avances. Et la mortalité des bénéficiaires est
celle du vingtile de niveau de vie où leur pension moyenne les place, par la
convention de l'action 14 (`population_niveau_de_vie_euros`) : le premier
vingtile, une avance de 19,6 ans au lieu de 24,2. Le réglage `reprise` du
formulaire est devenu facultatif ; vide, la part est calculée, et la page
l'écrit avec son origine, un paragraphe du dépliant donnant les deux médianes
et la convention, et la quatorzième réserve la disant. Ce que ça donne :
43 % de couverture, contre la moitié posée à la main ; en 2070, 17,7 Md€
versés, 9,7 repris, 8,0 nets, 0,22 % du PIB ; de 2026 à 2070, 849 versés, 310
repris, 539 nets ; un stock d'avances de 320 Md€ à l'horizon. Les deux
mouvements se compensent en partie : la couverture est plus basse que la
moitié, mais les avances plus courtes se reprennent plus tôt.

**Le même jour, encore : les femmes.** « Est-ce que tu peux prendre en compte
le facteur que ce sont principalement des femmes qui vont demander ce minimum
vieillesse ? » Mesuré sur l'EIR 2020 par sexe, plancher majoré, pensions du
système 4 : 72 % des femmes sont sous le plancher contre 42 % des hommes (46 %
et 18 % aux pensions d'aujourd'hui), et les femmes font 68 % des
bénéficiaires, pesées par la part des femmes parmi les 65 ans et plus que les
courbes de survie du modèle donnent en population stationnaire — le dépôt n'a
pas d'effectif de retraités par sexe. Codé : `_reprises_successions` mélange
les deux courbes de survie du vingtile dans cette proportion au lieu de
moitié-moitié (`GarantieProjetee.part_femmes`), le paquet porte la
distribution de l'EIR par sexe (`distribution_pensions_sexes`), et la page
écrit la part des femmes. Ce que ça déplace : une avance dure 20,5 ans au lieu
de 19,6, la couverture passe de 43 à 42 %, le net de 2070 de 8,0 à 8,2 Md€,
le stock de 320 à 331 : peu, parce que la longévité des femmes allonge les
avances et rapproche la couverture de celle d'un homme, mais c'est le bon
chiffre. Ce que le sexe change au PATRIMOINE ne peut pas être codé sans le
fichier de l'enquête : les femmes sous le plancher vivent souvent dans un
ménage moins pauvre que leur pension, et beaucoup sont veuves, dont la
succession porte tout le patrimoine du couple pour une seule avance ; les
deux vont dans le sens d'une couverture plus haute que le calcul, et la
quatorzième réserve le dit.

**Le même jour, la suite : deux avances sur une succession.** « Tu peux
chercher ce que ça fait pour les héritages avec cette différence homme/femme ?
», puis « vas-y, fais ça ». Ce que la recherche a établi : la femme est presque
toujours le conjoint survivant — l'INED mesure que 70 % des femmes en couple à
60 ans connaîtront le veuvage, pour treize ans en moyenne, et 81 % des 3,6
millions de veufs de 60 ans et plus sont des femmes ; l'écart d'âge dans les
couples est de 2,6 ans (INSEE, 2017), et le modèle donne 4,7 ans d'écart
d'espérance de vie à 65 ans dans le premier vingtile. La règle reportant la
reprise au décès du conjoint survivant, c'est la succession de la mère qui
porte les deux avances, et le patrimoine du fichier étant celui d'un MÉNAGE,
le calcul d'avant supposait que chaque bénéficiaire laissait seul sa
succession. Codé : `scripts/fetch/insee_vie_en_couple.py` lit la figure 2 de
l'*Insee Première* n° 2040 (recensement 2021) et écrit
`data/reference/macro/vie_en_couple.csv` — part en couple et part seul(e), âge
par âge de 65 à 100 ans et par sexe, 144 lignes, `haute` ;
`donnees/vie_en_couple.py` et `moteur/js/vie-en-couple.js` la chargent et la
moyennent sur les années vécues ; `_reprises_successions` en tire le nombre
moyen d'avances par succession — la part de chaque sexe en couple, multipliée
par la part de l'autre sexe sous le plancher, les pensions du couple étant
supposées indépendantes —, et confronte au patrimoine l'avance MULTIPLIÉE par
ce nombre. Résultat : 1,28 avance par succession, la couverture passe de 42 à
37 %, le net de 2070 de 8,2 à 9,2 Md€, le cumul net de 549 à 582. Un homme de
65 ans du premier vingtile passe 70 % du temps qui lui reste en couple, une
femme 42 %. Ce que le dépliant dit en plus : la corrélation des revenus dans
un couple rendrait ce nombre plus grand, et deux concubins que le recensement
compte en couple ne se succèdent pas l'un à l'autre. Ordres de grandeur
calculés en chemin, hors du modèle : l'avance d'une femme seule vaut 173 k€
contre 94 k€ pour un homme (durée et complément), et 274 k€ pour un couple sur
la succession de la veuve ; à ce niveau, la succession est absorbée en entier
pour 91 % des ménages retraités modestes et 58 % de l'ensemble des ménages
retraités. Le garde-fou « les héritiers ne paient jamais plus que l'héritage »
n'est donc pas un cas limite : il est saturé le plus souvent. Et le scénario 6
ne servant aucune réversion, ce que la réversion versait sans contrepartie
devient une créance reprise sur le patrimoine du couple.

**Le même jour, la fin : le site le dit.** « Décris cette situation dans le
site pour parler du minimum vieillesse. » Le dépliant « Le plancher, et ce
qu'il change pour les petites pensions », sur la page Programme, porte
désormais deux sections de plus, dans les deux moteurs. *Le minimum vieillesse
est d'abord une affaire de femmes* : un tableau calculé sur la distribution de
l'EIR, sans rien emprunter au modèle — 46 % des femmes retraitées ont une
pension de droit direct sous le plancher majoré contre 18 % des hommes, mais
l'homme qui tombe dessous tombe plus bas (537 € de manque moyen contre 476),
parce que ce sont des carrières très courtes là où c'est la règle chez les
femmes —, puis le recensement de 2021 : 62 % des femmes de 65 ans vivent en
couple, 26 % à 85 ans, contre 65 % des hommes du même âge. *Ce que cela change
pour une veuve, et pour ses enfants* : le système actuel sert une réversion
qu'on ne rembourse pas et qui ne touche pas à l'héritage ; la proposition n'en
sert aucune (seul le scénario 1 la sert, décision écrite dans `limites.md`),
et ce qui prend sa place est la garantie, c'est-à-dire une avance reprise sur
la succession de la veuve, celle qui porte le patrimoine du couple et souvent
l'avance du mari. La page dit que les héritiers ne paient jamais de leur poche
et qu'ils héritent souvent de rien, et que le dispositif se refuse. Trois
règles de style du dépôt ont dû être respectées en chemin : pas de « ce n'est
pas X, c'est Y », pas de « et non », trois incises en tiret par page au plus.

**Ce qui reste du point 1, et demande une personne.** Le fichier individuel
de l'enquête Histoire de vie et Patrimoine 2020-2021 ou 2023-2024 : le
fichier standard se commande auprès de Progedo-ADISP (data.progedo.fr) sur
inscription, à des fins de recherche ou d'enseignement, sans passage devant le
comité du secret ; le fichier de production et de recherche demande ce
comité, le fichier détaillé du CASD est payant. Avec le fichier, un script du
dépôt calculerait par personne de 65 ans et plus la pension individuelle et le
patrimoine net du ménage, donc la couverture par tranche de pension, et le
poids des couples ; le fichier resterait hors de git, la table agrégée
entrerait avec son script. À vérifier au dictionnaire des variables que le
montant individuel des pensions y est.

*Le 22 septembre 2026, les deux blocages sont déclarés, et c'était le geste qui
manquait.* L'action 45 avait bâti le mécanisme — un champ `blocage` dans le
manifeste, une liste que `scripts/fetch/source_locale.py` imprime — et ce qui
bloque le point 1 restait écrit ici seulement, c'est-à-dire nulle part où on
le cherche. Deux jeux sont entrés au manifeste : `adisp_histoire_de_vie_patrimoine`
(`convention` — le catalogue de Progedo répond depuis une session, le fichier
se commande sur inscription, et rien n'est à déposer dans `data/brut/` :
un fichier individuel d'enquête n'entre pas dans un dépôt public, c'est la
table agrégée qui entrerait, avec son script) et `cdc_successions_2024`
(`reseau` — le rapport de septembre 2024 sur les droits de succession donne la
distribution des successions déclarées, pour un recoupement d'ensemble, et
`ccomptes.fr` ferme la connexion avant toute réponse : « Recv failure:
Connection reset by peer », vérifié le 22 septembre 2026 sur la racine comme
sur la page de recherche). Le jeu `cdc_rapports_retraites`, qui portait ce même
blocage sans le dire, le porte aussi. La liste en compte dix.

*Le 22 septembre 2026, plus tard : les trois règles de la reprise sont
comptées.* « Calcule les trois », puis « oui » à les coder, la fenêtre de
l'assurance-vie alignée sur celle des donations. Le report du logement au
décès du conjoint survivant, les donations réintégrées et l'assurance-vie ne
jouaient jusque-là que dans le texte du programme. `cout._recouvrement` et
son jumeau `recouvrement` les font entrer dans la couverture, calculée
désormais sur mille rangs de chaque distribution de patrimoine
(`DistributionPatrimoine.grille`, l'inverse de la loi normale par
l'approximation d'Acklam des deux côtés) ; `_deces_en_couple` lit sur le
recensement et les courbes de décès du premier vingtile la part des décès en
couple, 35 %, et ce que vit ensuite le survivant, 11,1 ans ; la trajectoire
rend au décès la part immédiate et, onze ans plus tard, ce que le logement
des couples rend, intérêts courus (`part_reprise_immediate`, `report_annees`,
`facteur_report` sur `GarantieProjetee`). Quinze paramètres, chacun avec sa
source ou son motif d'hypothèse, dont trois interrupteurs
(`reprise_report_logement`, `reprise_donations`, `reprise_assurance_vie`) ;
les trois coupés et l'assurance-vie à zéro rendent le calcul d'avant au
chiffre près, et un test le tient. Deux sources au manifeste
(`cor_transmissions_retraites`, `bdf_comptes_distributionnels`), `L. 132-8`
CASF lu sur une copie, Légifrance refusant la session. Une correction en
chemin : le calcul d'avant comptait l'assurance-vie comme saisissable alors
qu'elle est hors succession, ce qui surestimait la couverture ; et la règle
écrite laissait placer son épargne en assurance-vie avant 65 ans hors
d'atteinte, d'où l'alignement, écrit dans le dépliant du programme. Ce que ça
déplace : la couverture reste à 39 %, les reprises de 2070 passent de 7,8 à
8,0 milliards d'euros, leur cumul de 2026 à 2070 de 243 à 239, parce que le
report décale onze ans de reprises pendant la montée en charge. Les
hypothèses sans source, de bas en haut, laissent 2070 entre 7,5 et 9,1. La
page Coût porte un paragraphe de plus, « Les trois règles qui protègent la
reprise sont comptées », et son affirmation contrôlée ; `limites.md` dit le
détail et les hypothèses. Reste ce qui restait : le fichier individuel de
l'enquête, qui remplacerait aussi la part du logement, le patrimoine du
propriétaire et les donations par des données.

**Fin.** La page Coût donne la garantie en trois lignes, brut, reprises et
net, sur le patrimoine des bénéficiaires selon leur pension lu dans le fichier
de l'enquête, couples compris, et le programme dit en une phrase pourquoi il
reprend là où le Parlement renonce.

*Le 20 septembre 2026, plus tard.* **La garantie vieillesse est annoncée comme
le SEUL plancher du système 4, et le minimum garanti de la fonction publique
reste dans le tableau « ce que la garantie remplace ».** Le tableau en était
d'abord sorti le même jour, au motif que les régimes de la fonction publique
servent ce minimum dans leur dépense de pensions, que la trajectoire remplace
déjà, et non par un transfert que l'impôt paierait à part. Le programme a
tranché dans l'autre sens : *on ne garde le minimum de la fonction publique
que pour montrer le système actuel, et on le supprime dans la proposition.*
Le tableau montre donc les quatre planchers d'aujourd'hui — 7,8 milliards en
2024, dont 0,72 de minimum garanti — contre le seul de demain, et l'écart
revient à 11,7 milliards. Le motif du retrait valait d'ailleurs pour le
minimum contributif, que les régimes servent aussi et que le tableau gardait :
le retirer seul était incohérent.

Ce qui reste écrit de ce passage : la garantie est **le seul plancher** du
système 4, et la ligne du programme le dit désormais en nommant les quatre
qu'elle remplace. Le scénario 1 continue de servir le minimum garanti, parce
qu'un fonctionnaire le perçoit aujourd'hui et que c'est ce qui permet de
chiffrer ce que la proposition lui retire ; l'étalon est le droit en vigueur,
et rien d'autre. Python, JS, témoins, `limites.md`.

**La question a été rouverte deux fois dans la même journée, et elle est
close : le tableau reste tel quel.** Pour qu'une troisième session ne la
reprenne pas, voici ce qui a été vu et écarté. Les quatre planchers du tableau
ne sont pas de même nature : l'ASPA est une allocation hors de la masse des
pensions, que l'impôt paie et à laquelle la garantie succède vraiment — même
forme différentielle, même âge de 65 ans, même financement — tandis que le
minimum contributif et le minimum garanti sont servis par les régimes, dans
une dépense de pensions que la trajectoire remplace en entier. La ligne « ce
que l'impôt paierait en plus » retranche donc d'un coût payé par l'impôt
quatre planchers dont deux ne le sont pas : elle mêle deux budgets.

Deux réécritures ont été proposées et refusées. *Un.* Un avant/après séparé
par payeur : l'État paierait 15,8 milliards de plus — la garantie moins la
seule ASPA — et les régimes 2,9 de moins, à l'intérieur d'une masse que la
trajectoire compte déjà. *Deux.* Garder les 12,9 et renommer la ligne « tous
payeurs confondus », ce qui la rend juste sans rien déplacer. Le programme a
gardé la formulation actuelle. **C'est un arbitrage, pas un oubli** : le
chiffre d'affiche du dépliant ne se change pas pour un gain de précision
comptable, et la page dit déjà, sous le tableau, que le total remplacé est une
borne basse et l'écart une borne haute.

### 89. Dépouiller les 260 sources officielles remises le 22 septembre 2026 — `en cours`

**Reprise, au 23 octobre 2026.** Sont faits l'IRCEC, les libérales, la CRPN,
l'Ircantec, l'ENIM, la fonction publique, la CNRACL, la Caisse des dépôts, le
RAFP, l'Agirc-Arrco, les régimes spéciaux, la Cnav, service-public, le CLEISS,
les modèles publics, mon-entreprise, les API publiques, l'abattement du RCI,
les comptes notionnels étrangers, le COR, l'IPP, les parcours d'Union Retraite,
les neuf modèles du registre et F33841, avec F23369. Attendent le propriétaire :
le lot de `scripts/simulateurs.py` (RAFP, Ircantec, artistes-auteurs), un compte
PISTE, Gallica, les règlements du RCO (1978) et du NRIC (2004). Restent
`a_explorer` six lignes : le simulateur du COR, fermé, et cinq qui attendent le
propriétaire. Détail : `89/2026-10-23-f33841-et-f23369.md`.

**Demande.** Huit lots d'adresses, remis le même jour : « explorer chaque lien
assez profondément et en tirer le maximum possible pour notre site. Il ne faut
pas rester à la surface et regarder uniquement la page servie par le lien mais
aussi l'ensemble des pages qui peuvent être explorées. Il y a énormément de
simulateurs qui peuvent s'avérer être une mine d'or si on exécute plusieurs
simulations sur chaque. Il faudrait bien entendu faire attention à des
comportements imparfaits vu qu'en grande majorité, ces simulateurs ont été
conçus par l'homme. Ces liens vont surtout aider à documenter comment le
système actuel fonctionne. »

**Pourquoi c'est le premier rang.** Le dépôt a fini de COMPTER les régimes :
89 lignes d'inventaire, plus aucune « à modéliser ». Il n'a pas fini de les
LIRE — 37 fiches sont `partiel`, et pour la plupart parce que leur barème n'a
jamais été lu chez celui qui l'applique. Ce lot vise précisément ces
trente-sept, dont vingt sont visées par au moins une adresse : les salaires
forfaitaires des marins, les classes de la Cipav,
le forfait par ancienneté de la CNBF, les tranches de la CAVOM, la part
capitalisée de la CAVP. Et il touche l'étalon : le scénario 1 doit être le
droit en vigueur tel que la caisse l'applique, et ces sources sont exactement
les sources d'application que `docs/veille_droit.md` exige à côté du texte.

**Ce qui est déjà fait, et qui était le plus long.** Les 260 adresses sont
inventoriées dans `data/sources_a_explorer.yaml`, une ligne chacune, avec le
régime qu'elles concernent, la nature de ce qu'elles portent et, en une
phrase, ce qu'on va y chercher. Elles ont toutes été sondées : 252 répondent
200 à une session, et les huit autres tiennent en cinq cas dont quatre se
contournent proprement. `docs/exploration_sources.md` porte les recettes.

**La découverte du sondage, qui change le chantier.** Le dépôt tenait pour
acquis qu'aucun simulateur officiel n'est automatisable —
`tests/temoins/exemples_officiels.yaml` l'écrit en tête. C'est vrai des
simulateurs nominatifs, qui exigent FranceConnect, et faux des vingt-huit
calculettes anonymes publiées par les mêmes caisses. Les simulateurs du GIP
Union Retraite passaient même pour injoignables : leur serveur omet
l'intermédiaire de son certificat, un navigateur le rattrape tout seul, `curl`
non. Le maillon ajouté, ils répondent. Un simulateur est un ORACLE : on peut
l'interroger cent fois, et vingt appels bien choisis rendent un barème que
personne n'a publié.

**Le risque, et il est nommé par la demande.** Ces calculettes sont écrites à
la main et vieillissent : un paramètre resté à l'année passée, une borne d'âge
qui n'a pas suivi la dernière loi, un arrondi, un champ qui plafonne sans le
dire. Le dépôt est mal placé pour en douter — le 17 septembre 2026, ses propres
âges légaux étaient certifiés et faux. D'où la règle : un simulateur est une
source d'APPLICATION, jamais de droit ; sa valeur plafonne au niveau `haute`,
comme celles d'OpenFisca ; quand il contredit le texte, le texte l'emporte et
l'écart s'écrit dans `limites.md`. Une calculette gelée à sa date n'est
d'ailleurs pas un défaut mais une chance : `sim2010` de la CNRACL applique le
droit de 2010, et c'est le seul moyen de vérifier le modèle sur le PASSÉ.

**Marche.** Par lots cohérents, jamais au hasard : les sections libérales, les
régimes spéciaux, la fonction publique, le versant international du CLEISS,
les quatre modèles publics (CALIPER, trajectoire, calcul_pension, OpenFisca),
le versant cotisations de mon-entreprise. Pour chaque lot : lire la fiche du
régime AVANT la source, pour chercher ce qui manque et non ce qu'on a ; puis
transcrire là où ça va — un exemple chiffré dans
`tests/temoins/exemples_officiels.yaml`, une règle dans `veille.yaml`, un
barème dans `data/reference/regimes/` avec sa ligne au manifeste, un mur dans
`limites.md` ; puis passer la ligne de l'inventaire à `explore` ou `epuise`
avec sa date et sa note. `docs/exploration_sources.md` détaille chaque geste.

**Passe du 22 septembre 2026 : les artistes-auteurs (IRCEC).** Neuf adresses
de l'IRCEC dépouillées (guide, mémo, trois règlements, FAQ, pages de taux, de
liens et de routage), puis les arrêtés d'approbation des règlements lus au
JORF, de 2013 à 2025. Ce qu'elle a trouvé : la minoration des trois régimes
n'est pas la décote du régime de base, que les trois fiches leur prêtaient,
mais 2,5 % pour chacune des deux premières années manquantes et 5 % au-delà,
ou le régime de base s'il est plus favorable ; le RACL n'a rejoint ce barème
qu'en 2025. Deux modes nouveaux, `abattement_points: ircec` et
`ircec_age_seul`, portés en JavaScript ; les fiches sont coupées en 2014 (et
en 2025 pour le RACL) ; le rendement du RAAP passe à 10,8 % en 2026 ; le
routage SACD/SACEM a sa source. Écrit dans `docs/limites.md` (« L'IRCEC compte
des années ») et au registre de veille (`minoration_ircec`). Restent du lot :
le simulateur de cotisations de la Sécurité sociale des artistes-auteurs,
celui de mon-entreprise, la page des âges de l'IRCEC — qui a servi un PDF au
lieu d'une page —, et le barème des cotisations arriérées de la Cnav.

**Seconde passe du même soir sur les artistes-auteurs.** Une autre session
avait pris le même lot sans le savoir ; elle a gardé le barème de minoration de
la première, mieux sourcé que le sien, et n'a porté que ce que la première
n'avait pas. Trois corrections du scénario 1, toutes lues au texte. *La
majoration de 10 % pour trois enfants*, au RAAP depuis 2014 (article 28) et au
RACD depuis l'arrêté du 17 avril 2024 ; aucune fiche ne la déclarait. *Le RAAP
des auteurs dramatiques et des compositeurs à la moitié du taux* (décret
n° 62-420, article 2 II, depuis 2016) : le texte vise la personne affiliée au
RACD ou au RACL, non la part de son revenu ; une fiche `ircec_raap_taux_amenage`
à points du RAAP, et le rendement suit désormais `points_de`. *La classe
spéciale d'avant 2016* : de 1981 à 2015, le RAAP prélevait une classe, et
« à défaut d'option » la classe spéciale, six points par an ; trente et un
montants lus dans les décrets annuels, de 876 F en 1984 à 448 € en 2015, là où
la fiche prélevait 8 % du revenu. Les témoins des trois statuts d'auteur
perdent de 7 à 27 % au scénario 1. La table des âges de l'IRCEC recoupe celle
du dépôt ; sa foire aux questions décrit encore le RACL d'avant mai 2025. Les
cinq pages de la Sécurité sociale des artistes-auteurs confirment le droit du
régime général pour le scénario 1, et montrent ce que le compte notionnel
prête à tort : la part patronale d'un salarié, 54 % du compte « patronal » du
témoin, quand le diffuseur ne verse que 1 % pour toutes les branches.

**Ce que ce second passage laisse ouvert.** Un drapeau de statut qui porte au
compte la seule part salariale des auteurs, dans le compte notionnel et la
fiche de paie des deux moteurs — la question de la part du 1 % du diffuseur
qui revient à la vieillesse est à trancher d'abord (`docs/limites.md`,
« Les artistes-auteurs n'ont pas d'employeur »). La classe A d'office des
musiciens avant 2004, que l'article 1er d'alors, absent de l'index, dirait. Et
restent `a_explorer` le simulateur de mon-entreprise et les cotisations
arriérées de la Cnav.

**Le 23 septembre : la part patronale des auteurs est retirée.** Le drapeau
`part_salariale_seule` (`affiliations.yaml`) marque les trois statuts
d'auteur ; `compte.py` et `compte.js` ne leur portent plus que la part
salariale, sous toutes les conventions, et la fiche de paie du salarié ne leur
est plus servie. Le 1 % du diffuseur compte pour zéro : l'article L. 382-4 le
verse à toutes les branches sans dire la part de la vieillesse. Seuls les
témoins des trois statuts d'auteur bougent, et le scénario 1 n'en bouge pas ;
tenu par trois tests (`test_simulateur.py`, `test_donnees.py`,
`test_remuneration.py`). Détail dans `docs/limites.md`, « Les artistes-auteurs
n'ont pas d'employeur ».

**Passe du 23 septembre 2026 : les professions juridiques (CNBF, CAVOM,
CPRN).** Seize adresses, réservées par un commit `en_cours` poussé seul, puis
les statuts et règlements des deux sections lus au Journal officiel, le décret
n° 2026-418 et les articles du code propres aux avocats. Corrigé au scénario
1, dans les deux moteurs : les âges propres de la CAVOM et de la CPRN de 2014
à 2023 (champ `age_table`, `legislation/ages_regimes.csv`) ; leurs décotes par
l'âge seul, que la durée n'annule plus (`abattement_points: cavom`,
`decote_annulee_par_la_duree: false`) ; le plafond de la CAVOM de quatre à
huit PASS de 2016 à 2020 et son assiette minimale ; la surcote des avocats à
1,25 % depuis le 1er juillet 2010 (barème `cnbf`) ; la majoration de 10 %
pour trois enfants de la CNAVPL, de la CNBF et de sa complémentaire, de la
CPRN. Témoins : officier ministériel -7 % et jusqu'à +65 % avant 1950, faute
de rendement jusque-là ; notaire -6 à -9 % ; avocat +1 à +2 %. Récit dans
`docs/limites.md`, « Les sections juridiques écrivaient leurs règles » ; tests
dans `tests/test_sections_juridiques.py`.

**Ce que ce lot laisse ouvert, par ordre de poids.** *La section B de la
CPRN*, quatre dixièmes du complémentaire d'un notaire : la règle des bornes
est écrite (un huitième des notaires par classe, décret n° 2026-418), la
grille des montants publiée (k fois la classe 1 du décret annuel, 10 k
points ; plaquette du congrès 2025), les valeurs de point dans les rapports
d'activité de 2016 à 2025 ; il reste à estimer les huit bornes sur la loi des
revenus que la section C calibre, et à décider de la classe 1 d'office
d'avant 2014. *La série de la retraite forfaitaire des avocats*, 2017-2026 dans
les barèmes, à porter comme une série par année — le modèle la ramène de 2026
par les prix, 5 % de moins pour une liquidation de 2017 —, avec celle de la
cotisation forfaitaire par ancienneté. *Le rendement de la section C de la
CPRN* de 2016 à 2023, que les rapports d'activité donnent année par année et
que `rendements_points.csv` tient à 4,12 % sur douze ans. *La valeur de
service 2026 de la CNAVPL*, 0,6599 €, écrite par la CAVOM et la CPRN, à
reprendre du recueil statistique à sa parution. *La majoration de durée
d'assurance pour enfants* et la surcote parentale des libéraux et des avocats.

**Passe du 23 septembre 2026 : les professions de santé (CARMF, CARCDSF,
CAVP, CARPIMKO, CARPV).** Vingt et une adresses, réservées par un commit
`en_cours` poussé seul ; les calculettes de la CARMF lancées sur une grille
de revenus, puis les statuts et règlements des cinq sections lus au Journal
officiel, et le décret n° 2026-418 dans ses articles de santé, qui ne change
aucun paramètre des fiches. Les barèmes de 2026 étaient justes ; les règles
d'âge ne l'étaient pas. Corrigé au scénario 1, dans les deux moteurs : la
minoration par l'âge seul, que la durée annulait parce qu'une durée requise
vide ne suffisait pas à le dire (CARMF de 2000 à 2016, CARPV) ; la règle
d'âge de la CARCDSF — 5 % par année de 2008 à 2010, table par génération de
2011, plafond de 15 % depuis 2024, surcote de 1 puis 1,25 % — et le taux
plein anticipé des mères, un an par enfant ; les âges propres de la CAVP et
sa minoration à deux pentes ; l'escalier des générations 1956 à 1961 de la
CARPIMKO ; la majoration de 10 % pour trois enfants des cinq complémentaires
et de l'ASV ; et les âges d'une carrière, qui ne lisent plus ceux d'un
complémentaire. Quatre champs de période (`decote_palier_age`,
`taux_plein_anticipe_par_enfant_annees` et leurs compagnons), une colonne de
décote dans `ages_regimes.csv`. Témoins : dentistes −2 à −7 %, pharmaciens
−3 à −4,5 %, vétérinaires −2,6 à −3,3 %, médecin né en 1945 −1,4 %. Deux
exemples publiés entrent aux témoins officiels : la CARCDSF, deux enfants et
le taux plein à 65 ans ; la CARMF, le coefficient de 1,15 à 65 ans. Récit
dans `docs/limites.md`, « Les sections de santé minorent à l'âge » ; tests
dans `tests/test_sections_sante.py`.

**Ce que ce lot laisse ouvert, par ordre de poids.** *La même forme de
minoration ailleurs* : la CAVAMAC, la CAVEC et la CPRN d'avant 2014 écrivent
une décote en laissant la durée requise vide, et le moteur la laisse annuler
par la durée — à relire contre leurs statuts avant de la corriger. *Les
prestations complémentaires de vieillesse* des dentistes, des sages-femmes,
des auxiliaires médicaux et des biologistes, dont les barèmes sont lus
(décrets de 2007 et de 2017, pages des caisses) et qu'aucun statut ne reçoit.
*Les tables transitoires* que l'index ne porte pas : la minoration des
dentistes nés de juillet 1951 à 1954 (en image au JO du 21 juillet 2012), les
coefficients des pharmaciens nés jusqu'en 1955 (annexe des statuts de 2011),
l'abattement des auxiliaires nés avant 1956 de 2016 à 2023. *La participation
de l'assurance maladie* à la cotisation de base des médecins de secteur 1, et
les dispenses des premières années d'affiliation. *Les statuts antérieurs*,
publiés au Bulletin officiel : CARCDSF avant 2007, CAVP avant 2009, CARPIMKO
avant 2015, CARPV avant 2021.

**Passe du 22 septembre 2026, suite : les avocats (CNBF).** Les onze
barèmes annuels de la caisse, 2016 à 2026, dont celui de 2024 retrouvé dans
Internet Archive. Le récupérateur n'en lisait que la valeur du point : la
grille de cotisation du complémentaire était celle de 2026 depuis 2019, alors
que son taux de première tranche a doublé en dix ans, et la pension de base
celle de 2026 ramenée par les prix. Les deux fiches sont lues année par
année ; les valeurs du point de 2024 sont certifiées. Écrit dans
`docs/limites.md` (« Les avocats cotisaient au taux de 2026 depuis 2019 »).
Restent du lot : les fiches pratiques et les deux simulateurs de la caisse.

**Passe du 23 septembre 2026 : les dernières sections libérales (CNAVPL,
Cipav, CAVAMAC, CAVEC).** Vingt-trois adresses, réservées par un commit
`en_cours` poussé seul : le guide 2026 de la CNAVPL en trois parties, ses pages
et ses recueils, les fiches pratiques de la Cipav, les documents de la CAVAMAC,
la calculette de la CAVEC lue dans son script, et le simulateur Cipav de
mon-entreprise interrogé hors navigateur par ses deux modèles publicodes ;
puis, au Journal officiel, les statuts de la CAVAMAC de 2011 et de 2023, ceux
de la CAVEC depuis 2008, et les articles 8, 13, 20 et 21 du décret
n° 2026-418, ce qui clôt sa ligne de veille. Corrigé au scénario 1, dans les
deux moteurs : la minoration par l'âge seul de la CAVAMAC et de la CAVEC, que
la durée annulait (`abattement_points: cavom` jusqu'en 2023,
`decote_annulee_par_la_duree: false`, 65 ans à la CAVEC pour toutes les
générations) ; la surcote de la CAVAMAC, par années pleines, et depuis 2024
par années COTISÉES (champ `surcote_trimestres_cotises`) ; la majoration de
10 % pour trois enfants de la CAVAMAC (2012), de la Cipav (2000) et de la
CAVEC (2026) ; la majoration de durée d'assurance des libérales depuis 2010
— le moteur ne la cherchait que dans les régimes en annuités, et lit
désormais `mda` dans toute fiche qui le porte — et leur surcote parentale
depuis 2024. La valeur de service de la CNAVPL est certifiée de 2004 à 2026,
lue dans la page que la caisse publie (`scripts/fetch/cnavpl_valeur_service.py`) :
les pensions de base liquidées de 1989 à 2019 remontent de 1,4 à 5 %. Et deux
défauts de carrière : un revenu pile sur un seuil de trimestre en validait un
de moins (virgule flottante), l'âge du taux plein d'avant la génération 1930
retombait sur 67 ans. Témoins : agent général −5 à −15 % sur sa
complémentaire, expert-comptable −5 %, libérale mère de deux enfants sans
décote. Trois exemples de la CAVAMAC entrent aux témoins officiels, et les deux
exemples de points de la CNAVPL sont rejoués. Récit dans `docs/limites.md`,
« Les dernières sections libérales » ; tests dans
`tests/test_sections_liberales.py`.

**Ce que ce lot laisse ouvert, par ordre de poids.** *La CPRN d'avant 2014*,
dernière fiche de section à porter une minoration que la durée annule, à
relire contre ses statuts. *La majoration de durée d'assurance et la surcote
parentale des avocats*, que L. 653-3 leur ouvre comme L. 643-1-1 aux
libéraux, et que la fiche de la CNBF ne porte pas. *Les statuts d'avant 2011 de la CAVAMAC et d'avant 2008 de la CAVEC*,
au Bulletin officiel, et le taux d'abattement de la CAVEC d'avant 2008. *La
condition de trente années d'affiliation* de la majoration pour report de la
Cipav, qui ne porte que sur les points de ces trente années. *La liquidation
des carrières longues à 15 %* de la CAVAMAC. *Les cent points par trimestre
d'accouchement* de D. 643-1, qui demandent la date de naissance des enfants.
Les rapports d'activité de la Cipav et de la CAVEC, non ouverts, pour les
effectifs par classe. Les caisses, elles, publient de travers — la Cipav ses
taux de 2024, la calculette de la CAVEC huit classes sur neuf, le paquet
`modele-social` de l'Urssaf les paramètres d'avant la réforme — : c'est écrit
dans `docs/limites.md`, et c'est le droit que le dépôt suit.

**Passe du 23 septembre 2026 : les navigants de l'aviation civile (CRPN).**
Cinq adresses, réservées par un commit `en_cours` poussé seul. L'âge qui
annule la décote est soixante ans (L. 6521-4, premier alinéa, lu sur
Légifrance), non soixante-cinq ; depuis 2022, la décote se compte sur la
seule durée (R. 6527-22), d'où le champ `decote_par_la_duree_seule` dans les
deux moteurs ; le taux d'appel de 2026 est de 111 %. Restent, notés dans
`docs/limites.md` : le dispositif transitoire des navigants nés avant 1971,
les conditions montantes de 2012 à 2021, les taux d'appel de 2016 à 2025.

**Passe du 24 septembre 2026 : la fonction publique de l'État (SRE, ENSAP,
service-public).** Vingt adresses, réservées par un commit `en_cours` poussé
seul : treize pages du Service des retraites de l'État, les fiches F21142 et
F13736 de service-public, la FAQ de la DGAFP sur la retraite progressive, et
trois calculettes lues dans leur script ; puis, dans les index LEGI et JORF,
L. 14, L. 14 bis, L. 17 dans ses trois rédactions, L. 18, L. 25 bis et D. 16-2
du code des pensions, les articles 45 et 53 de la loi n° 2010-1330, le décret
n° 2010-1744, le XXIV de l'article 10 de la loi n° 2023-270 et l'article 13 du
décret n° 2023-435 dans la version du décret n° 2026-344. Les pages
confirment la fiche presque partout ; trois règles ne l'étaient pas, et sont
corrigées au scénario 1 dans les deux moteurs. *Le minimum garanti d'une
pension de moins de quinze ans* est, depuis 2011, la référence rapportée à la
durée requise (L. 17, d) : le moteur servait à tous le quinzième de 57,5 % de
l'invalidité, 63 % de trop pour treize ans de services ; le c reste à qui
avait atteint l'âge d'ouverture avant 2011. *L'âge qui ouvre ce minimum sans
la durée* est minoré de neuf trimestres pour un âge d'ouverture atteint en
2011, puis sept, cinq, trois et un (`MINORATION_AGE_MINIMUM_GARANTI`). *L'emploi
classé surcote à l'âge anticipé majoré de cinq ans*, l'âge minoré majoré de
dix pour la super-active, et à soixante-deux ans avant les marches de 2023 :
le moteur attendait l'âge légal de leur génération, jusqu'à sept trimestres
de trop. Témoins : les super-actifs d'État et hospitaliers partis à 64 ans,
+2,4 et +2,5 %. Deux exemples du SRE entrent aux témoins officiels, le SRE
devenant le huitième éditeur ; trois autres sont faux et écrits comme tels.
La calculette du rachat d'études de l'ENSAP applique un barème abrogé au
1er janvier 2026 (décret n° 2025-1340), celle de surcotisation d'Aix-Marseille
le taux employeur de 2025. Récit dans `docs/limites.md`, « La fonction
publique de l'État : le minimum de l'invalidité servi à tous, et la surcote
des classés attendue trop tard » ; tests dans
`tests/test_fonction_publique_etat.py`.

**Ce que ce lot laisse ouvert, par ordre de poids.** *Le temps partiel*, que
la saisie ne porte pas : le modèle compte à temps plein des services que la
loi compte à leur quotité, et c'est le seul manque du lot qui touche une
population nombreuse — il demande un champ de saisie, les services de la
famille `fonction_publique` et la surcotisation bornée à quatre trimestres.
*Le barème du rachat d'études* (D. 7-1, de 20 à 66 ans) confronté à la
neutralité actuarielle du compte notionnel : deux mains qui calculent le prix
d'un même trimestre. *L'écrêtement du minimum garanti* par le total des
pensions (L. 17, sixième alinéa), dont le décret reste à trouver, et le
plafond de L. 18, V, qui ne mord qu'à sept enfants. *La décote « carrière
longue » des militaires* et la PAGS, qui demandent le grade. *Le d de L. 17 à
la Banque de France*, que son décret de 2012 écrit et que sa fiche ne date
pas. Les lots voisins restent `a_explorer` : la CNRACL et juris-cnracl, la
Caisse des dépôts (FSPOEIE, mines), le RAFP — dont les règles corrigées ici
valent déjà pour la CNRACL et le FSPOEIE.

**Passe du 24 septembre 2026, suite : la CNRACL et la Caisse des dépôts
(juris-cnracl, FSPOEIE, mines).** Vingt-cinq adresses, réservées par un
commit `en_cours` poussé seul : six pages et trois calculettes de la CNRACL,
douze pages de sa base juridique — d'où 369 pages ont été déroulées —, le
convertisseur de validation de la Caisse des dépôts, deux pages du FSPOEIE et
celle des droits directs des mines ; puis les tableaux « Barèmes et
revalorisations » des mines de 2024 à 2026, la fiche du COR, et dans les
index LEGI et JORF le décret n° 46-2769, le décret n° 2002-800, les arrêtés du
coefficient de majoration, L. 13, L. 14 et D. 16-1 du code des pensions, le
décret n° 2003-1306, R. 173-15, deux versions de L. 161-17-3 et l'article 10
de la loi n° 2023-270. Quatre règles corrigées au scénario 1, dans les deux
moteurs. *La pension du mineur* est trimestres × coefficient de majoration ×
valeur du trimestre : le moteur n'avait pas le coefficient (1,473 en 2026),
portait la valeur par les prix au lieu des pensions, ne plafonnait pas la
durée à cent vingt trimestres hors ceux d'avant cinquante-cinq ans, et
ouvrait la pension à cinquante ans à tous — 17 172 € dus pour trente ans
liquidés en 2026, 12 299 servis (`legislation/bareme_trimestre_mines.csv`,
dont la chaîne retombe au centime sur les sept valeurs publiées). *La
carrière longue d'un fonctionnaire ouverte avant soixante ans* lit sa durée à
la date d'ouverture (C du XXIV ; L. 13, III, avant septembre 2023) : 170
trimestres et non 172 au né en 1967 parti à cinquante-huit ans en 2025. *La
surcote de la fonction publique* se compte en trimestres de durée depuis le
premier du mois qui suit l'âge, non en trimestres civils. *Et, trouvée en
chemin, la durée des générations nées de septembre 1961 à 1965 parties avant
le 1er septembre 2023* est celle de la version de 2014 de L. 161-17-3 : le
moteur leur opposait la loi de 2023, jusqu'à trois trimestres de trop. Six
exemples entrent aux témoins officiels — un du COR, trois de la CNRACL, deux
de la circulaire Cnav 2023-19 —, et le COR et la CNRACL deviennent éditeurs.
Témoins : les mineurs, de −21 % (générations 1925 et 1935, que le plafond
prive de neuf années) à +21 % (1975) ; les autres corrections ne touchent
aucun cas type — tous partent à un anniversaire de janvier, et aucun des
générations 1961 à 1965 avant septembre 2023 —, et le chiffrable de la page
Avantages passe de 96,7 à 96,6 Md €. La CNRACL tranche aussi une question de la passe précédente : elle n'applique
pas l'écrêtement du minimum garanti, faute de décret. Récit dans
`docs/limites.md`, « La pension du mineur », « La CNRACL » et « Les
générations de 1961 à 1965 » ; tests dans `tests/test_mines.py` et
`tests/test_cnracl.py`. La piste des mines qu'ouvrait le lot de l'ENIM est
refermée.

**Ce que ce lot laisse ouvert, par ordre de poids.** *La pension différée* :
l'article 26 du décret n° 2003-1306 revalorise le traitement de l'agent
radié comme les pensions, de la radiation à la mise en paiement, et le
moteur le porte au point d'indice — +6,3 % de 2011 à 2026 quand les pensions
ont pris près d'un quart ; toute carrière qui quitte la fonction publique
avant de liquider en est sous-évaluée. *La priorité du régime spécial* pour
les majorations pour enfants (R. 173-15, et ses exceptions) : le moteur
retient la plus favorable, et sert à une fonctionnaire passée par le privé
les trimestres du régime général. *L'interpénétration* : un fonctionnaire
passé de l'État à la CNRACL ou au FSPOEIE reçoit une pension unique,
liquidée par le dernier régime ; les groupes de succession du moteur seraient
le point d'appui. *Le rétablissement* au régime général et à l'Ircantec de
qui quitte la fonction publique avant deux ans de services (quinze avant
2011), que le moteur pensionne au prorata. *La clause de sauvegarde* du
décret n° 2023-436 pour les carrières longues des nés de septembre 1961 à
1963. *La bonification de 0,15 % par trimestre au fond* des mineurs, qui
demande de savoir où il a travaillé. *Les seuils de validation d'avant 1972*
que porte le convertisseur, le SP-CTI, la NBI, le supplément des
aides-soignants, les emplois insalubres, la montée de quinze à dix-sept ans
des services actifs. Et deux témoins possibles : les trois exemples de
`taux_maximum_fonction_publique` de la page du montant, et le deuxième de la
surcote parentale (génération 1969). Cent quatorze adresses restent
`a_explorer`, dont le RAFP, voisin de ce lot.

**Le même soir, la pension différée est corrigée.** Premier des restes du
lot, sur demande. La règle est la même depuis 2004 pour les trois régimes du
code des pensions — L. 25 pour l'État, l'article 26 du décret n° 2003-1306
pour la CNRACL, l'article 22 du décret n° 2004-1056 pour le FSPOEIE — : le
traitement de l'agent radié avant de pouvoir liquider suit les revalorisations
des pensions civiles jusqu'à la mise en paiement, celle de ce jour-là
comprise, et non le point d'indice des actifs, gelé de 2010 à 2016. Un
fonctionnaire de l'État parti au privé à cinquante ans fin 2011 et liquidant
en janvier 2026 avait un traitement de référence de 34 739 € ; il est de
39 913 €, 14,9 % de plus. En 2020, le traitement prend le coefficient de
L. 161-25, la dérogation de 0,3 % de la loi de financement ne visant que les
pensions servies. Avant 2004, la péréquation faisait déjà suivre le point, et
rien ne change ; la Banque de France, dont le règlement n'écrit pas la
phrase, non plus. Aucun témoin existant ne bouge ; deux parcours entrent aux
témoins pour que les deux moteurs rejouent la règle. Récit dans
`docs/limites.md`, « La pension différée d'un fonctionnaire » ; tests dans
`tests/test_cnracl.py`.

**Puis la priorité du régime spécial pour les trimestres des enfants.**
Deuxième reste du lot, sur demande. R. 173-15 fait accorder ces trimestres
par UN régime : le régime spécial qui peut servir une pension à la mère et où
le droit est ouvert pour ses enfants, sinon le régime général, sinon le
dernier régime aligné. Le moteur retenait le plus favorable. Il sait
désormais quelle durée de services ouvre une pension dans chaque régime
spécial, lue au texte : quinze ans avant les réformes, deux pour les
fonctionnaires radiés depuis 2011, un pour les agents partis de la SNCF, de
la RATP, des IEG et de l'Opéra depuis juillet 2008
(`services_ouvrant_pension.csv`). Il sait aussi quand le droit est ouvert :
un enfant né depuis 2004 doit l'être après le recrutement (L. 12 bis), un
enfant né avant selon les trois versions de R. 13. Une fonctionnaire de
l'État passée au privé à cinquante ans perd huit trimestres pour deux
enfants et 755 € par an ; une salariée recrutée par l'État à quarante ans en
gagne 407, ses huit trimestres de bonification entrant au prorata de sa
pension civile. Cinq parcours entrent aux témoins. Restent hors du modèle le
rétablissement, l'interpénétration, l'exception de la CRPCEN et l'enfant
handicapé. Récit dans `docs/limites.md`, « Les trimestres des enfants » ;
tests dans `tests/test_priorite_enfants.py`.

**Et l'interpénétration.** Troisième reste du lot, sur demande. L'État, la
CNRACL et le FSPOEIE comptent et liquident chacun les services des deux
autres (L. 5 et L. 11 du code des pensions, articles 8 et 13 du décret
n° 2003-1306, articles 4 et 10 du décret n° 2004-1056, depuis au moins 1964),
et le dernier régime sert une pension unique : un traitement, celui de fin de
carrière publique, et une proratisation sur tous les services. Le moteur en
liquidait une par régime, chacune sur son propre traitement. Un fonctionnaire
de l'État devenu territorial à quarante ans perdait 14,1 % de sa pension, un
territorial devenu fonctionnaire de l'État 15,8 %, un ouvrier de l'État
devenu fonctionnaire 16,3 %. Les groupes de succession, qui liquidaient déjà
ensemble un régime et son successeur, réunissent désormais les trois sous
une même clé. La durée qui ouvre une pension, pour la priorité des trimestres
d'enfants, se compte sur les trois. Le militaire garde sa pension militaire
(L. 77), et sa carrière d'État seulement militaire reste à part. Cinq
parcours entrent aux témoins. Reste le rétablissement de qui n'a pas la durée
minimale. Récit dans `docs/limites.md`, « L'État, la CNRACL et le FSPOEIE ne
servent qu'une pension » ; tests dans `tests/test_interpenetration.py`.

**Puis le rétablissement.** Quatrième reste du lot, sur demande. L'agent qui
quitte l'État, la CNRACL, le FSPOEIE ou la SEITA sans la durée qui ouvre une
pension n'a pas de pension de son régime : il est rétabli au régime général et
à l'Ircantec pour toute la période (L. 65 du code des pensions, D. 173-15 et
D. 173-16 du code de la sécurité sociale, article 64 du décret n° 2003-1306,
article 9 du décret n° 70-1277). Le moteur lui servait une pension au prorata.
Les années rétablies gardent leur statut et changent de régimes : le régime
général y porte le dernier traitement, écrêté au plafond de chaque année
(circulaire Cnav 2011/38), l'Ircantec le traitement de l'année, le RAFP garde
les primes. Un agent hospitalier parti au privé après treize ans passe de
26 312 à 28 718 € ; la mère de deux enfants passée un an par l'État, qui avait
déjà sa durée au régime général, perd au contraire une pension civile qui ne
lui était pas due. La même table des durées a corrigé celle des militaires :
quinze ans pour qui s'est engagé avant 2014, la loi n° 2014-40 ne donnant les
deux ans qu'aux engagés depuis (article 42, II). Cinq parcours entrent aux
témoins. Restent l'Ircantec sans la NBI, la solde militaire au lieu des
salaires forfaitaires de D. 173-17, et les coordinations propres des autres
régimes spéciaux. Récit dans `docs/limites.md`, « Le fonctionnaire parti sans
droit à pension » ; tests dans `tests/test_retablissement.py`.

**Fichiers.** `data/sources_a_explorer.yaml` (l'inventaire et son avancement),
`docs/exploration_sources.md` (la méthode), `tests/test_sources_a_explorer.py`
(la forme), puis, selon ce qu'on trouve : `tests/temoins/exemples_officiels.yaml`,
`data/reference/legislation/veille.yaml`,
`data/reference/legislation/reformes.yaml`, `data/reference/regimes/`,
`data/sources.yaml`, `docs/limites.md`, `docs/regimes.md`.

**Fin.** Aucune ligne de `sources_a_explorer.yaml` n'est restée `a_explorer` ;
chacune porte sa date et ce qu'elle a donné. Les fiches `partiel` qui le sont
faute de barème publié ne le sont plus, ou disent lequel n'existe pas. Et
`limites.md` dit, source par source, ce que les caisses appliquent que le
modèle n'applique pas.
**Premier lot dépouillé : l'Ircantec, le 22 septembre 2026.** Trois annexes de
la base documentaire que la Caisse des dépôts tient pour les gestionnaires du
régime — elle le GÈRE, elle en est donc le producteur —, lues dans leur PDF
avec `scripts/fetch/lecture_pdf.py`.

*Une convention soldée, et une erreur avec elle.* La fiche du régime écrivait
noir sur blanc que la répartition salarié/employeur était reportée sur toute
la série « faute d'une série publiée ». Elle est publiée, à chaque date d'effet
depuis 1925 : l'annexe 4-4 donne les taux appelés part par part. La tranche A
vaut 40 % de l'agent d'un bout à l'autre — la convention était juste. La
tranche B, non : l'agent en portait 34 % de 1971 à 2010, et la part n'est
montée aux 35,64 % d'aujourd'hui que par paliers annuels, de 2011 à 2017.
Quatorze périodes corrigées ; sur le témoin du contractuel, quinze euros par an
passent de l'agent à l'employeur.

*Un escalier confirmé ligne à ligne.* L'action 88 avait tiré du texte de
l'article 16 de l'arrêté du 30 décembre 1970 un barème à trois marches, contre
la décote plate de 1,1 % par trimestre que le dépôt appliquait. L'annexe
« Retraite à taux réduit » le tabule, génération par génération : le modèle
rend les quarante et une lignes des onze tables. Et elle apprend ce que le
texte ne disait pas — les ancrages sont des ÂGES FIXES, 1 à 67 ans, 0,88 à 64,
0,78 à 62, 0,43 à 57, les mêmes pour toutes les générations, quand l'âge légal
passe de 62 à 64 ans sur cette plage. C'est l'âge du taux plein qui ancre
l'escalier, jamais l'âge d'ouverture. `tests/test_ircantec_minoration.py` le
tient désormais, et la ligne `coefficient_anticipation_ircantec` est entrée au
registre de veille.

*Ce que ce lot laisse ouvert.* Le salaire de référence de 2023 (5,329 €) et de
2024 (5,611 €) est dans l'annexe 8-1 ; les deux CSV de la Caisse des dépôts
s'arrêtent à 2021 — vérifié en relançant le récupérateur —, et le dépôt porte
donc ces années au niveau `haute`, d'OpenFisca. Les certifier demande un
récupérateur qui lise ce PDF et le recontrôle qui va avec, dans
`scripts/verifier_donnees.py` : c'est la suite immédiate, et elle vaut pour
toutes les annexes du même genre.

**Lot de l'ENIM, le 22 septembre 2026 : les six pages du régime des marins.**
Le site répond 200 à `curl`, et le sondage l'avait rangé en `session` ; mais
ces 200 portent une page de 212 octets, le script d'un pare-feu anti-robots.
Chromium passe une fois son magasin de certificats préparé. Les six lignes
sont `epuise`, et deux règles de droit en sont sorties, lues ensuite dans le
code des pensions de retraite des marins.

*Le marin de cinquante ans était refusé.* R. 2 ouvre la pension d'ancienneté
à « la double condition de cinquante ans d'âge et de vingt-cinq années de
services » ; les cinquante-cinq ans qu'il fixe ensuite ne bornent que la
jouissance de qui continue à naviguer (L. 5552-5 du code des transports). La
fiche avait pris la borne pour l'âge, et refusait le départ même que le
plafond de vingt-cinq annuités de R. 13 organise. Nouveau champ de fiche,
`age_ouverture_services`, dans les deux moteurs ; l'exception des
cinquante-deux ans et demi à ce plafond est portée avec lui.

*La bonification pour enfants n'était pas servie* : 5 % pour deux enfants,
10 % pour trois, 15 % au-delà (R. 14). Le barème est en données
(`taux_majoration_enfants`), le seul du catalogue qui commence à deux enfants.

Deux exemples de la caisse deviennent témoins — l'ENIM entre comme troisième
éditeur de `exemples_officiels.yaml` —, la grille des salaires forfaitaires
de 2026 est recoupée au centime, et trois lignes entrent au registre de
veille. Un seul témoin de simulation bouge : un marin parti avant
cinquante-cinq ans, refusé hier, liquidé aujourd'hui au même montant.
`docs/limites.md` dit ce qui reste : la pension spéciale à soixante ans sans
autre pension (R. 5, que la page de l'ENIM contredit elle-même), la
catégorie moyenne de trente-six mois, le décompte au semestre, la petite
pêche outre-mer, la réversion et la cessation anticipée amiante.

**Ce que le lot de l'ENIM a appris, appliqué le même soir.** Cinq
enseignements, chacun porté là où il sert.

*La règle qui restait ouverte est fermée.* La pension spéciale des marins
(moins de quinze ans de services) suit l'entrée en jouissance de l'autre
pension de base, jamais avant cinquante-cinq ans, et attend soixante ans sans
autre pension (L. 5552-12 du code des transports, R. 5). Le modèle l'ouvrait
à cinquante-cinq ans dans tous les cas — et, l'âge d'une carrière étant le
plus précoce de ses régimes, il faisait liquider à cet âge toute la carrière
d'un polypensionné passé dix ans par la mer, régime général compris. Champs
`pension_speciale_*`, deux moteurs, un test de chaque côté ; aucun témoin
figé ne portait ce cas, d'où les tests.

*Le site disait encore l'ancien droit.* La méthode affichée ne connaissait
que « la majoration pour trois enfants » et un droit ouvert par l'âge légal
ou la carrière longue ; elle dit maintenant le barème des marins et
l'ouverture par la durée de services. La ligne de l'inventaire des régimes,
que la page des régimes affiche, disait les exceptions de R. 13 « hors
fiche » : elle dit ce qui est porté et ce qui manque.

*Un 200 n'est pas une page lue.* `scripts/fetch/sonder_sources.py` ressonde
l'inventaire en jugeant le texte servi. Sur les deux cent soixante adresses,
il a rangé en `navigateur` trois pages de mon-entreprise en plus des six de
l'ENIM ; et il a montré son propre piège, Incapsula glissant son script dans
de vraies pages. Un test hors réseau tient les deux cas.

*Un paragraphe était en quatre exemplaires*, en tête de ce fichier. Ce
n'était pas le script de la prose : deux résolutions de conflit successives
avaient gardé les deux côtés. Réparé ; `tests/test_prose.py` refuse deux
paragraphes identiques à la suite, et `CLAUDE.md` dit de garder un seul
côté d'un conflit de chiffres ancrés — et de ne jamais prendre un fichier de
prose entier d'un côté, ce que cette session a failli faire en rebasant.

*Le lot de l'Ircantec était rangé sous l'action 92* ; il est revenu ici.

**Piste ouverte par ce lot.** La fiche des mines ouvre la pension à
cinquante ans pour tous, quand l'article 147 du décret de 1946, dans sa
version de 1974, réservait cet âge aux trente ans de mine dont vingt au fond
et donnait cinquante-cinq aux autres. Sa version en vigueur n'a pas été lue ;
c'est la même question que celle des marins, posée à l'envers.

**Les calculettes officielles, le 22 septembre 2026 au soir.** Environ cent
cinquante calculs sur mon-entreprise, l'ERAFP, la CARMF et la CARPIMKO, chacun
confronté au scénario 1 puis au texte ; le rapport est dans les fichiers du
projet (`ecarts_simulateurs_officiels.md`). Six écarts étaient chez nous, et
la loi leur donne tort à chaque fois ; ils sont corrigés dans les deux moteurs.
La seconde tranche de la Cipav va jusqu'à quatre plafonds depuis 2025, et non
trois. Le RCI n'avait aucune valeur de point après 2023 et achetait au
rendement de 2013, 9 % de points de trop : `scripts/fetch/cnav_baremes_rci.py`
lit désormais les barèmes de la Cnav. La CARPIMKO de 2026 cotise sur le revenu
entier, relevé à un demi-plafond (`assiette_minimale_pass`), au point de 391 €
que seule sa calculette publie. L'ASV des médecins sert 27 points plus
l'ajustement proportionnel au revenu, neuf au plus (`points_ajustement_*`), et
non 36 à tous. Le RAFP est majoré par l'âge de liquidation (`surcote_points:
rafp`) et versé en capital sous 5 125 points (`capital_seuil_points`), le
capital étant écrit dans le détail de la pension. Enfin l'artisan, le
commerçant et le libéral cotisent au régime de base sur une assiette minimale,
200 SMIC horaires puis 450 depuis 2023 (`legislation/assiette_minimale_independants.csv`),
qui valide leurs trimestres. Reste à lire le décret n° 2026-418, qui réécrit
les complémentaires libérales, contre les dix fiches.

**Les simulateurs d'info-retraite, saisis à la main le 1er octobre 2026.** Le
propriétaire a saisi neuf cas dans deux simulateurs anonymes de l'Union
Retraite, selon la règle du § 3.5 de l'architecture : une saisie par borne,
chaque prédiction du modèle écrite avant la réponse. Ils sont aux exemples
officiels sous le préfixe `ur_`. Celui de la carrière longue confirme les
quatre portes (16, 18, 20 et 21 ans), les 172 trimestres de 1966, 1968 et
1969, et l'année 1965 coupée en trois, décembre compris. Ce dernier cas a levé
deux arrondis, corrigés dans les deux moteurs : la date d'effet lue sans
l'arrondi de la table (`2026.667`) rendait au premier mois d'un décret de
septembre les portes du décret d'avant, et 60 ans et 8 mois n'atteignaient
jamais les 60,67 de la table ; l'assuré né mi-décembre 1965 partait au
1er octobre 2026 au lieu du 1er septembre. Aucun témoin de simulation n'en
bouge. Celui de la réversion confirme les 54 % du régime général, les 60 % de
l'Agirc-Arrco sans condition de ressources — une fiche jusqu'ici supposée —,
l'âge de 55 ans, et la condition de quatre ans de mariage de la fonction
publique, des deux côtés de la borne, à 50 %. Il mesure un écart que la fiche
déclarait : deux enfants à charge au décès lèvent la condition d'âge de
l'Agirc-Arrco (`ur_reversion_prive_50_ans_deux_enfants`, en écart connu). Les
imperfections des simulateurs sont notées en tête du lot : les quatre
trimestres omis pour les nés d'octobre et de novembre 1965, la réversion du
régime général jamais écrêtée, sous un seuil de ressources de 2024, et la
branche « deux ans avant la cessation » de L. 39 ignorée. Une grandeur naît
pour les comparer, `reversions_mensuelles`, qui prête au défunt les pensions
saisies. *Laisse ouvert* : l'exception des enfants à charge, à lire dans
l'accord Agirc-Arrco avant de la porter (jusqu'à quand est-elle servie ?) ;
une fiche de réversion pour la RAFP, que le simulateur sert à 50 % ; le
remariage (perte de l'Agirc-Arrco, plafond du ménage à 1,6) et l'Ircantec, à
saisir une autre fois ; le budget par simulateur du § 3.5, qu'aucun registre
ne tient encore — cinq saisies pour la carrière longue, quatre pour la
réversion.

**Les API publiques, sondées le 5 octobre 2026.** Le propriétaire a demandé
la liste des API publiques qui pourraient servir, après celle de la Cnav.
Le catalogue des API de l'État (`www.data.gouv.fr/api/1/dataservices/`) n'en
recense aucune d'ouverte sur la retraite : hors des portails de données déjà
branchés (Urssaf, DREES), tout y est réservé aux administrations (API
Particulier, API Entreprise), et Légifrance est derrière un compte PISTE.
Aucune des caisses sondées ne sert sa base réglementaire comme la Cnav.
Quinze lignes entrent au vivier, sous « Les API publiques », toutes mesurées
le jour même : les cubes de pensions du SRE (data.economie.gouv.fr, de 2015 à
2025), l'API de calcul de mon-entreprise (`mon_entreprise_developpeur` passe
`explore`), les fiches de service-public en XML, datées, l'interface SRU de
Gallica, les WordPress ouverts de la CNAVPL, de la CAVEC, de la CAVAMAC, de la
CAVOM, de la CPRN et de la CRPN, les pages en JSON de la base de l'Ircantec et
de la Cipav, deux jeux de la DREES (taux de remplacement, minimum vieillesse)
et Légifrance par PISTE, en `refus` faute de compte. Parmi elles, commencer
par les cubes du SRE et l'API de mon-entreprise. *Laissé* : l'open data de la
Caisse des dépôts, déjà au manifeste (`cdc_open_data`) ; le jeu 1393 de la
DREES, que le critère 1 fait remonter à l'EACR et à l'EIR ; l'API web
d'OpenFisca, qui sert le YAML déjà lu ; Webstat, ILOSTAT et le grunnbeløp de
la NAV, sans rien pour le modèle ; l'API tabulaire de data.gouv.fr, un outil —
les cinq CSV de la MSA n'y comptent que des retraités par intercommunalité.
*Sondés sans résultat* : la réglementation de l'Agirc-Arrco (pages HTML
seules), les simulateurs d'info-retraite, la MSA (refus), le SRE et le COR
(pare-feu), le BOSS, la CNIEG, Juris-CNRACL (un flux RSS d'un seul article, de
2019) et les WordPress fermés de la CNBF, de l'IRCEC et de la CARPV.

**Le RAFP, le 5 octobre 2026.** Les quatre lignes du régime additionnel,
réservées puis dépouillées après la note de l'action 142 sur la délibération
de l'ERAFP, pour ce qu'elle n'avait pas pris. *Quatre exemples de plus*,
grandeur `prestation_rafp` : les trois prestations-types du rapport annuel
2012 (page 25), premiers exemples du barème de surcote de 2005, au pivot de
soixante ans, à 62 et 67 ans en 2013, et le capital unique de la page « Calcul
et paiement », 4 448 points à 64 ans en 2026, 6 965,93 €. Tous concordent,
sauf le capital de Jean, que le rapport imprime 4 030,38 € quand son produit,
3 429 × 0,04421 × 24,62 × 1,08, fait 4 030,88 € : une coquille, en écart
connu. *La réversion* : les barèmes de conversion en capital du conjoint et de
l'orphelin, « à compter du 1er janvier 2022 », au mois, et celui de l'orphelin
de 2005 au rapport annuel 2012, lus dans la fiche `reversion_rafp`, non
portés — le modèle montre en rente la réversion qu'un capital paie ; celui
du conjoint d'avant 2022 n'est publié nulle part. Deux lectures divergentes :
la page convertit par 29 un conjoint de 54 ans, son barème dit 30,94 ; elle
plafonne les orphelins à 50 %, le décret (article 10) le total du conjoint et
des orphelins. *La calculette de points* reste `a_explorer` : le serveur
calcule, rien ne se lit sans saisir. Les points de l'année sont « arrondis au
point supérieur » selon l'ERAFP, ce que le décret (article 5) ne dit pas ni le
modèle ne fait, moins d'un point par an. *Laissé* : porter la conversion de la
réversion au barème de 2022, et l'allocation d'orphelin.

**L'Agirc-Arrco, le 5 octobre 2026.** Les seize lignes du régime, lues par
quatre agents en lecture seule — les pages, l'accord du 17 novembre 2017
dans sa version de 2019 et ses avenants n° 16, 17 et 19, les circulaires
de 2017 à 2026, la compilation des valeurs, les livrets —, chaque chiffre
revérifié sur le texte avant d'entrer. Six corrections, chacune son commit.
*La réversion* : deux enfants à charge du survivant au décès lèvent l'âge,
pour toujours (articles 110 et 111), et la majoration pour enfants du
défunt, que le modèle ne reversait pas du tout, l'est en entier (article
109) ; l'écart connu des deux enfants se retire, Max entre, et Destinie,
qui reverse cette majoration à 60 %, porte l'écart. *Les points* se
comptent au taux de calcul, 6,20 % et 17 %, et non à la cotisation appelée,
arrondie à 7,87 %, divisée par 127 % : 0,05 % de points de tranche 1 en plus
depuis 2019, deux exemples du livret n° 3 par une grandeur nouvelle,
`points_de_l_annee`. *La seconde retraite* du cumul part au 1er janvier
2024 au plus tôt (avenant n° 16), et non en septembre 2023. *L'UNIRS* de
1949 à 1957 restait en francs chez OpenFisca : le point de 1957 coûtait six
fois et demie trop cher ; le récupérateur lit ces années dans sa série
nominale. *Le plafond* de la majoration vaut 2 367,48 € depuis novembre
2024, non 2 367 € de 2025. *La calculette fiscale* concorde au dernier euro
et fait corriger un commentaire (26 472 € au taux plein), une docstring
périmée et l'arrondi du quart de part, qui séparait les deux moteurs.
`docs/limites.md` disait le bonus d'un an éteint : il survit pour qui avait
le taux plein avant décembre 2023. Un exemple de plus, la minoration de
0,90 à 64 ans et 6 mois du livret n° 4. *Laissé*, dans les notes du vivier :
le coefficient temporaire de la retraite progressive (article 88, barème de
la circulaire 2026-1, exemple du livret n° 4), les points de maladie de
l'article 58, l'orphelin, le partage entre ex-conjoints, la version
consolidée de l'accord, les deux limites du cumul plafonné que la fiche
réglementaire de la fédération ne date pas, et le taux de calcul de
l'Arrco des cultes, que l'action 119 tient.

**Les régimes spéciaux, le 5 octobre 2026.** Les vingt-trois lignes de la
CNIEG, de la CRPCEN, de la CPRPF et de la MSA, lues par des agents en
lecture seule, chaque trouvaille revérifiée dans l'index LEGI avant
d'entrer, chaque correction son commit. *La CRPCEN* liquidait les six
derniers mois sans plafond : le décret n° 90-1215 dit les dix meilleures
années, comptées pour moitié de trois à sept plafonds (article 89),
revalorisées comme au régime général (article 96) — un écrêtement nouveau
dans les deux moteurs, et sept cas types de clercs de 4 à 9 % plus bas ; ses
taux salariaux depuis 2018 ; sa réversion (article 113) et ses trimestres
pour enfants (article 92), qu'elle n'avait pas, avec la durée qui ouvre sa
pension. *Les trimestres pour enfants* : la SNCF, la RATP et les IEG
recevaient la bonification de la fonction publique, coupée en 2004. Chacune
a sa fiche, lue article par article et recoupée par le COR (séance du
19 octobre 2023, document n° 2) : rien aux services à la SNCF ; un an avant
juillet 2008, puis deux et quatre trimestres selon le rang dans la fratrie,
à la RATP et aux IEG, qui doublent le second d'une fratrie de deux ; de même
à la CRPCEN, coupée en 2006. Et les trimestres de durée seule ne proratisent
plus la pension d'un régime spécial, ce que le modèle faisait déjà des deux
trimestres de L. 12 bis. *Les IEG* : leur réversion, la moitié majoration
comprise (articles 22 à 25) ; la retraite progressive que leur statut ouvre
depuis 2023 (article 21-1) ; quatre textes faux corrigés, dont l'âge du cas
type ; le minimum de pension en fiche manquante (`minimum_pension_ieg`) ; la
CAMIEG dite dans `docs/limites.md`. *La MSA* : la majoration d'un dixième des
parents de trois enfants, servie depuis 1974 (décret n° 55-753, article 37 ;
D. 732-38), qu'aucune période ne déclarait. Huit témoins nouveaux font
passer les deux moteurs par ces chemins, au bit près. *Défauts des sources* :
l'exemple du minimum de la CNIEG, au montant de 2025 sous le plafond de
2026 ; la circulaire n° 2024/15, qui nomme la même assurée Madame B puis
Madame D. *Laissé* : le minimum des IEG, dont il faut décider quelles
ressources retenir ; la CAMIEG ; la surcote et les âges des sédentaires des
IEG, avec l'exemple de Monsieur E ; la surcote parentale de la CRPCEN et de
la SNCF ; la part employeur de la CRPCEN, que le décret n° 91-613 fixe à
16,91 % depuis 2026 ; les trimestres pour enfants de la Banque de France,
des mines et des marins, que le COR dit autres que ceux de la fonction
publique.

### 129. Le taux de l'État ramené à sa part « retraite seule » : un réglage, puis le défaut — `en cours`

**Reprise, au 13 octobre 2026.** Le réglage et le défaut sont faits ; reste le
point 1, une vraie série année par année de la part « retraite seule », au lieu
de la proportion de 2025 prêtée aux autres années. Le jaune pensions du PLF
2027, lu le 13 octobre, n'en donne pas : il reprend la Cour (2025) et l'IPP
(2020), conclut qu'« il n'existe donc pas de taux consensuel » et annonce des
travaux de la direction du budget vers « une méthodologie applicable d'année
en année ». `PartRetraiteSeuleEtat` n'a donc pas à accepter plusieurs années.
Reste à guetter ces travaux, ou le jaune du PLF 2028 ; au propriétaire, dire
s'il veut la convention du jaune (16,67 %) comme valeur de `contribution_etat`.
Détail : `129/2026-10-13-jaune-pensions-2027.md`.

**Demande.** « Dis-moi en plus sur le taux seulement dédié à la retraite, ça
m'intéresse — ça peut changer beaucoup de choses », puis : « intègre-le comme
réglage d'abord, pour voir ». C'est le premier chantier de l'action 120.

**Ce qui est fait.** Un paramètre, `contribution_etat` (`ContributionEtat`),
dans les deux moteurs et dans les options du site — « Contribution de l'État
portée au compte ». Il ne joue que sous `part_cotisation=totale`, donc dans les
scénarios 4 et 5 et dans le 6 jusqu'à la bascule, et que pour l'État, seul
employeur dont le taux est un taux d'équilibre. `entiere`, le défaut, porte au
compte le taux versé, comme avant. `retraite_seule` n'en porte que la part que
la Cour des comptes rattache à la retraite de l'agent lui-même : son tableau
n° 15, recopié ligne à ligne dans `legislation/contribution_etat_retraite_seule.csv`
— le rapport passe au manifeste du statut `controle` à `saisi` —, garde 44,1 %
pour un civil et 51,2 % pour un militaire en 2025, sur les 78,28 % versés pour
un civil. Cette année-là, le compte reçoit exactement ces deux taux, en
fiabilité `haute`. Les autres années reçoivent la même proportion du taux de
l'année — 56,3 % pour un civil, 65,4 % pour un militaire, rapportés au taux
civil que le modèle lui crédite —, et c'est une hypothèse, en fiabilité
`estimee`. Avant 1995, l'État n'a pas de série et le compte reçoit déjà l'effort
d'un salarié du privé : le réglage n'y touche pas. Sous la simulation,
l'origine de la part patronale le dit année par année, et un paragraphe de plus
dit ce que le compte n'a pas reçu.

**Pourquoi une proportion, et non 44,1 % chaque année.** Les deux conventions
ont été mesurées avant d'écrire le réglage, et l'annexe n° 6 du rapport les
départage : l'Institut des politiques publiques, qui a fait l'analyse pour 2020
sur un taux d'équilibre de 75 % au lieu de 83,6 %, trouve 34,7 %, et la Cour
impute cinq points de l'écart à la seule différence d'année — environ 39 % pour
2020 par sa méthode. La part « retraite seule » suit donc le taux d'équilibre.
Pour 2020, la proportion donne 41,8 %, le taux fixe 44,1 %.

**Ce qu'il déplace**, mesuré le 24 septembre 2026 sur `main` (6081ae4, la
proposition avec son âge légal de 65 ans). L'écart au système actuel de la
fonctionnaire de l'exemple du README, née en 1975, passe de +45,0 % à −1,3 %
dans le scénario 4, de +44,9 % à −3,4 % dans la proposition. Dans la
proposition toujours : la sédentaire née en 1975 de +16,7 % à −21,2 %, l'actif
né en 1975 parti à 60 ans de +46,5 % à −0,8 %, le militaire né en 1985 parti à
45 ans de +102,9 % à +59,4 % — l'âge légal de 65 ans le fait cotiser vingt ans
de plus —, la sédentaire née en 1995 de −38,9 % à −48,0 %. Le solde moyen de
la proposition passe de −0,87 % à −0,48 % du PIB — de −26,1 à −14,4 milliards
d'euros par an —, et de −1,44 % à −0,98 % en 2050 : les droits qu'elle reprend
à la bascule étaient gonflés de ce qui payait d'autres pensions. Le cumul passé
du scénario 4 recule de 6 598 à 6 522 milliards. Le privé, la CNRACL, le
scénario 1 et la part salariale ne bougent pas, et un test le tient. La veille,
avant l'âge légal de 65 ans, le solde moyen passait de −1,40 % à −1,00 %.

**Ce qui restait à établir avant d'en faire le défaut.**

1. *Une vraie série, année par année.* La proportion de 2025 est prêtée à
   trente ans de taux. La Cour recommande que les documents budgétaires en
   rendent compte dès le projet de loi de finances pour 2027, et les
   ingrédients existent : les dépenses d'invalidité avant 62 ans, les
   majorations et les départs anticipés au Service des retraites de l'État,
   les effectifs de la compensation démographique chaque année, les durées
   validées tous les quatre ans par l'échantillon interrégimes. Le point dur
   est le déséquilibre démographique des années passées.
2. *Le militaire.* Le modèle lui crédite la série civile ; son taux appelé,
   126,07 % en 2025, n'est dans aucune table. Le réglage lui donne les 51,2 %
   de la Cour cette année-là, mais la proportion qu'il prête aux autres est
   celle d'un taux qui n'est pas le sien. Fait le même jour : voir « Le taux
   propre des militaires », plus bas.
3. *Le choix.* La doctrine du projet — ce qui n'est pas contributif se finance
   par l'impôt, non par le compte — plaide pour `retraite_seule` ; c'est aussi
   le résultat le plus lu du site qui bouge, de +45 % à −1 %. La décision est
   à l'utilisateur. Elle a été prise le même jour : voir « Le défaut », plus
   bas.

**Le passage sur `main`, le 24 septembre 2026.** Le travail avait été remis
dans une pull request, à la demande de l'utilisateur, pour être poursuivi dans
une session cloud, les fichiers fabriqués NON régénérés : calculés sous
Windows, ils auraient différé des témoins au dernier chiffre. La session cloud
qui l'a reprise a tiré le rapport et le zip des données de ses graphiques de la
release `documents-apportes`, aux empreintes du manifeste. `ccomptes.fr`, lui,
ne répond pas depuis le cloud : « Connection reset by peer » sur la page, le
PDF et le zip. Le manifeste le déclare donc (`blocage: reseau`, la release pour
`miroir`), et `source_locale.py --recuperer` en reprend le PDF. Tout a ensuite
été régénéré sous Linux. Le paquet de données porte la nouvelle table, et les
témoins gagnent trois simulations et une page. Les chiffres ne bougent que
dans les trois pages agrégées calculées sous le jeu de règles qui porte le
réglage (cas types, coût, avantages) ; les autres ne gagnent que l'option. Le
chiffrage budgétaire n'a rien eu à réécrire. Suite complète : 2 374 réussis,
1 ignoré, 0 échec. Les cas types de l'État mesurés le même jour disent
l'ampleur du choix qui reste : dans le scénario 4, le fonctionnaire sédentaire
né en 1970 passe de +41 % à −6 %, celui de 1960 de +26 % à −16 %, quand le
salarié moyen du privé des mêmes générations perd 30 % et 33 % sous les deux
réglages.

**Le défaut, le 24 septembre 2026.** L'utilisateur a tranché le point 3 au vu
des chiffres : `retraite_seule` est le défaut, dans les deux moteurs et dans le
formulaire du site, et `entiere` reste une option. La raison est la doctrine du
projet, et la cohérence qui en découle : l'État était le seul employeur crédité
d'un taux d'équilibre plutôt que d'un taux de cotisation, et c'est ce qui
faisait gagner 41 % au fonctionnaire sédentaire né en 1970, dans le scénario 4,
quand le salarié du privé de la même génération y perd 30 %. Sous le nouveau
défaut, la fonctionnaire de l'exemple du README passe de +45,0 % à −1,3 % dans
le scénario 4, et de +44,9 % à −3,4 % dans la proposition. Le solde moyen de la
proposition passe de −0,87 à −0,48 point de PIB, sa dette en 2070 de 59 % à
33 % du PIB (66 % pour le système actuel), et son coefficient d'équilibre, au
plus bas, de 0,85 à 0,90. Son régime est en léger excédent de 2028 à 2030, en
déficit de 2031 à 2065, en excédent ensuite. Et son avantage sur le système
actuel ne dépend plus de ce que les reportés travaillent : si aucun ne
travaillait, sa dette serait de 56 % du PIB en 2070, quand le taux entier la
portait à 82 %. Le privé, la CNRACL, le scénario 1, la part salariale et la
variante prospective ne bougent pas. Les points 1 et 2 restent ouverts : ils
ne décident plus du défaut, ils en affinent la valeur.

**Un défaut du réglage, trouvé en changeant le défaut.** Le dénominateur du
rapport de recettes de la page Coût — ce que le droit en vigueur prélève sur
chaque carrière de la grille — était calculé par le constructeur des scénarios
4 et 5, celui qui porte la part patronale AU COMPTE. Sous `retraite_seule`, il
comptait donc que l'État verse 46 % du traitement en 2026 au lieu de 82 %, et
la recette que la proposition garde des agents de l'État en était gonflée
d'autant. Le solde par défaut lit la recette sur l'assiette, non sur ce
rapport, et n'était pas touché ; la lecture « rapport » l'était, et les quatre
tests de `test_cout.py` qui recoupent le taux moyen qu'elle implique avec celui
du COR l'ont vu. `Simulateur.constructeur_prelevement`, dans les deux moteurs,
dit désormais ce qui est PRÉLEVÉ, avec le taux entier de l'État, et un test
tient qu'il ne dépend pas du réglage. Le réglage change ce qui est porté au
compte, jamais ce que l'employeur paie.

Ce que le changement a touché : `config.py` et `config.js` ; `simulateur.py`,
`simulateur.js`, `cout.py` et `cout.js` (le constructeur du prélèvement) ;
`web/pages.py` et `pages.js`, où l'option passe en tête avec « (défaut) », où
l'aide le dit, et où le paragraphe sous la simulation dit ce que le compte ne
reçoit pas — la question « et si tout avait été porté au compte ? » n'y paraît
plus que sous `entiere` ; `MESURES_BLOCAGES`, remesuré dans les deux moteurs ;
les témoins, dont les trois cas, la page du réglage et le jeu de règles des
pages agrégées portent désormais `entiere`, que le balayage des statuts ne
visite plus ; les tests du réglage, qui ont leur fixture `entiere`, et deux
tests du simulateur qui décrivaient le taux entier et le font désormais sous
lui ; les sondes de `mesures_prose.py` ; la prose — le README, `limites.md`,
dont la conclusion sur les reportés en emploi ne tenait plus, `methodologie.md`,
deux paragraphes datés de `chiffrage_plf.md`, et le parcours de présentation,
où le fonctionnaire n'est plus « le cas qui surprend ». Suite complète,
rebasée sur le lot de la fonction publique de l'État poussé entre-temps par une
autre session : 2 400 réussis, 1 ignoré, 0 échec.

**Le taux propre des militaires, le 24 septembre 2026.** Le point 2, à la
demande de l'utilisateur. Le 1° de l'article L. 61 du code des pensions fixe
deux taux de contribution à la charge de l'État, et le modèle ne prêtait au
militaire que celui des civils. Le sien est lu dans les décrets qui le fixent,
versions datées de la base LEGI (`dila_legi_contribution_employeur.py`) : 100 %
en 2006, 101,05 %, 103,5 %, 108,39 %, 108,63 %, 114,14 %, 121,55 %, puis
126,07 % depuis 2013, que les deux décrets de 2025 qui ont relevé le taux civil
n'ont pas touché. Vingt et une valeurs certifiées, dans
`legislation/contribution_employeur_militaires.csv` — un fichier à part, parce
que ce n'est pas un régime de plus. Deux sources se trompaient d'une année, et
le décret a tranché : la fiche du Service des retraites de l'État porte
106,83 % pour 2010, où le décret n° 2010-53 fixe 108,63 %, et les données du
graphique n° 23 de la Cour 101,5 % pour 2007, où le décret n° 2006-1798 fixe
101,05 %. La version de 2011 ne s'ouvre dans la base que le 6 janvier : chaque
taux est donc daté par l'entrée en vigueur que son décret écrit, faute de quoi
2011 aurait reçu le taux de 2010.

Sous `retraite_seule`, le militaire reçoit 51,2 / 126,07 de son propre taux,
soit 51,2 % chaque année depuis 2013 et 40,6 % en 2006 ; avant 2006, où il n'a
pas de taux propre, le taux implicite de tout l'État, dont sa part reste prise
sur le taux civil (51,2 / 78,28). Sous `entiere`, 126,07 % de sa solde. Le cas
type militaire gagne deux à trois points sous le défaut : −60 % au lieu de
−62 % pour la génération 1970 dans le scénario 4, +51 % au lieu de +47 % pour
1990 dans la proposition. Le solde moyen de la proposition passe de −0,48 à
−0,49 point de PIB, et de −0,87 à −0,91 sous le taux entier.

**La fiche de paie du militaire, et la question qu'elle pose.** Le même taux
entre dans la fiche de paie, où la moitié de ce que l'État cesserait de verser
remonte dans la solde (règle du partage, 20 septembre 2026). Le militaire y
gagne désormais +57,7 % de solde nette sur la carrière de l'exemple du README,
là où un civil gagne +37,6 % — et où il gagnait +37,6 % lui aussi quand le
modèle lui prêtait le taux civil. C'est la règle appliquée à ce que l'État
verse vraiment, non une décision nouvelle. Mais le taux des militaires paie
aussi leurs départs anticipés — 33,8 points dans la décomposition que la Cour
fait de leur taux d'équilibre en 2025 —, que la proposition supprime en portant
l'âge de départ à 65 ans : rendre à la solde la moitié de ces points-là est un
choix, et il reste à l'utilisateur.

Ce que le changement a touché : `dila_legi_contribution_employeur.py` (la
lecture, et un test sur une base en mémoire), `verifier_donnees.py` (la
certification et l'en-tête du fichier), `donnees/regimes.py` et `regimes.js`
(`taux(..., militaire)`), `moteur/compte.py` et `compte.js` (la part « retraite
seule » prise sur la série dont le taux vient), `remuneration.py` et
`remuneration.js`, `construire_donnees.py`, les textes du site qui citaient
82,28 % comme le taux de tous les agents de l'État, le manifeste, et la prose
— `limites.md`, `methodologie.md`, le README, `chiffrage_plf.md`, le parcours
de présentation. Suite complète : 2 407 réussis, 0 échec.

**La fiche de paie du militaire : l'État garde les départs anticipés, le
24 septembre 2026.** Cette question et la série du point 1 avaient été remises
le même jour dans une pull request, à la demande de l'utilisateur, pour être
reprises dans une autre discussion. Celle-ci les a reprises le soir même, et
l'utilisateur a tranché la première au vu de la mesure qu'elle portait. L'État
garde en entier ce que son taux payait de départs anticipés, et seul le reste se
partage avec la solde ou le traitement. La raison est celle du défaut du compte :
un avantage non contributif se finance par l'impôt, et sa suppression ne se
convertit pas plus en salaire qu'elle ne se porte au compte. Rendre à la solde
la moitié de ces points aurait augmenté le militaire d'autant plus qu'il perdait
l'avantage.

La part gardée est le poste `avantages_professionnels` du tableau n° 15 de la
Cour, pris comme la part « retraite seule » du compte : rapporté au taux versé
l'année mesurée, sur la série dont le taux de l'agent vient. Pour un militaire,
c'est 33,8 / 126,07, soit 33,8 points chaque année depuis 2013 ; pour un civil,
1,5 / 78,28, soit 1,6 point en 2026. C'est la variante « tels quels » de la
mesure, retenue pour les deux populations. La variante « en proportion »
rapportait les 33,8 points au taux d'équilibre de la Cour, 112,3 %, et comptait
donc parmi les départs anticipés une partie des 13,8 points que l'État appelle
au-delà : elle sortait de la convention du compte.

Sur la carrière de l'exemple du README, le militaire gagne désormais +42,2 % de
solde nette au lieu de +57,7 %, soit 1 275 € par mois au lieu de 1 746 € ; le
civil, +36,9 % au lieu de +37,6 %, soit 1 114 € au lieu de 1 136 €. Garder la
part revient exactement à la retirer du taux : la dépense d'aujourd'hui et ce
que la proposition libère baissent du même montant, et un test le tient. Rien
d'autre ne bouge : la fiche de paie ne fait ni la pension, ni le compte, ni le
solde, et la CNRACL, qui n'a pas de décomposition, garde tout son partage. Les
témoins ne changent que sur la page du programme et sur les deux simulations
d'un fonctionnaire d'État qu'ils figent. Aucune ne porte un militaire : sa fiche
a été comparée à part entre les deux moteurs, avec celles d'un officier, d'un
civil actif et d'un agent de la CNRACL, et les dix pages sont identiques. Le
chiffrage budgétaire n'a rien eu à réécrire. En passant, la réserve 5 de la
fiche de paie, dans `limites.md`, disait encore le traitement d'un agent public
tenu fixe, quatre jours après le partage ; elle dit désormais les deux
décisions. Et l'en-tête de `contribution_etat_retraite_seule.csv` disait le
réglage sans effet par défaut et le militaire rapporté au taux civil ; il dit
maintenant ce que font les deux lignes lues.

Le point 1 reste ouvert, et il attend un document. Le projet de loi de finances
pour 2027, où la Cour demande que la décomposition soit publiée, passe en
Conseil des ministres le 30 septembre selon la presse, et doit être déposé au
plus tard le 6 octobre. Son jaune pensions se tirera du miroir de l'Assemblée
nationale, comme celui de 2026. `PartRetraiteSeuleEtat`, qui refuse aujourd'hui
plus d'une année, devra alors en accepter plusieurs, dans les deux moteurs.

Ce que le changement a touché : `remuneration.py` et `remuneration.js`
(`departs_anticipes`, le champ du bloc, la formule de `brut_partage`),
`donnees/regimes.py` et `regimes.js` (`PartRetraiteSeuleEtat.taux` lit tout
poste), `web/pages.py` et `pages.js` (le paragraphe de la fiche de paie,
l'hypothèse sous le chiffre, les deux phrases du programme),
`test_remuneration.py` (deux tests, et le partage vérifié avec sa part gardée),
`test_donnees.py`, le manifeste, l'en-tête de la table de la Cour, le README,
`methodologie.md` et `limites.md`. Suite complète, rebasée sur deux commits
poussés entre-temps par d'autres sessions (le lot des mines et de la CNRACL, la
durée des générations 1961 à 1965) : 2 437 réussis, 1 ignoré, 0 échec.

**Fichiers.** `data/reference/legislation/contribution_etat_retraite_seule.csv`
(nouveau), `src/retraite_notionnelle/config.py`,
`src/retraite_notionnelle/donnees/regimes.py`,
`src/retraite_notionnelle/moteur/compte.py`, `src/retraite_notionnelle/web/pages.py`,
`moteur/js/config.js`, `moteur/js/regimes.js`, `moteur/js/compte.js`,
`moteur/js/pages.js`, `scripts/construire_donnees.py`,
`scripts/construire_temoins.py` (trois cas, une page, et le réglage dans le jeu
de règles des pages agrégées), `scripts/mesures_prose.py` (la sonde
`retraite_seule`, et `contribution_etat` dans les sondes de carrière et de
coût), `tests/test_simulateur.py`, `tests/test_donnees.py`, `data/sources.yaml`,
`README.md`, `docs/limites.md`, `docs/methodologie.md`, et les fichiers
fabriqués.

### 130. L'architecture du dépôt : décidée, les phases 0 à 8 faites, les domaines à ouvrir — `en cours`

**Reprise, au 23 octobre 2026.** Fait : phases 0 à 8, cinq domaines clos ; le
sixième, les périodes assimilées manquantes, a ses étapes 1 à 6 faites
(`130/2026-10-17-sixieme-domaine-etape-6.md`). Au propriétaire, README muet :
sa septième étape, la décision de la proposition, et la retraite progressive,
le cumul et la seconde pension. La carte mûrit : le code de toute fiche est
confronté au dépôt par un test, hors des 69 qui l'écrivent encore en prose
(`EN_PROSE`, `tests/test_carte.py`) ; restent les 107 fiches à lire au droit,
800 manques, et les points ouverts des phases 2 à 8. Par quoi commencer : vider
`EN_PROSE` : 23 fiches à récrire, puis 46 dont le code est à écrire. Détail :
`130/2026-10-23-carte-des-fiches-code-confronte.md`.

Le dépôt devenait de plus en plus lourd à faire avancer. Une modification du
moteur du scénario 1 touchait vingt fichiers en médiane, dont sept ou huit de
prose et de registres écrits à la main, et la suite de tests prenait dix
minutes et demie. Une session du 25 septembre 2026 en a cherché la cause, puis
a conçu une architecture. Trois séries de vérifications et une contre-épreuve
l'ont éprouvée, et le propriétaire l'a décidée le même jour :
`docs/decisions/0001-architecture.md`, version 5.4. Il y a élargi le principe
des références à tous les modèles publics, gardé toutes les sources, et fixé
la règle des simulateurs officiels : ne jamais solliciter les caisses. Rien du
modèle n'a changé.

**Ce que la phase 0 a fait**, le 25 septembre 2026, un commit par étape et
sans qu'un seul résultat bouge — les témoins sont restés identiques à
l'octet :

1. `docs/architecture.md`, l'état tiré de la note 0001 : L'essentiel, les
   § 2 à 13 et les annexes, dans la numérotation de la note, avec le numéro
   de version et la liste des changements. Ses chiffres datés sont devenus
   des ancres (l'inventaire des régimes, l'âge présumé aux naissances, le
   prélèvement sur les pensions) ou des renvois à la note, qui les garde à
   leur date ;
2. le tableau de bord, `docs/etat.md`, que `scripts/tableau_de_bord.py`
   fabrique depuis les registres, et qu'un test refuse périmé. Le coût du
   travail, qui se lit sur l'historique git, s'affiche à la demande
   (`--cout`) ;
3. `.github/workflows/tests.yml`, qui rejoue la suite complète à chaque
   envoi sur main : 2 503 tests passés en 13 min 39 à son premier passage ;
4. la suite rapide, `python -m pytest -m rapide` : 769 tests en 18 s sur
   quatre cœurs, 51 s en série. `tests/conftest.py` range chaque fichier de
   tests dans son niveau, rapide, complet ou contrôle ;
5. `CLAUDE.md` renvoie à l'architecture et au tableau de bord ;
6. le repère git `phase-0`, sur 4bb438f, le dernier commit de la phase
   (§ 12). Le jeton d'une session n'écrit pas de tag (HTTP 403) : à la
   demande du propriétaire, un workflow lancé une fois l'a posé, puis a été
   supprimé.

**Ce qui reste ouvert.**

- La phase 2 (§ 11) : la carte des règles et des relations, tirée des
  registres existants ; le vocabulaire des dates ; les contrats de
  l'annexe C en schémas validés par les tests ; les cliquets des textes ;
  le tableau de bord qui passe à la carte. Avec elle, les entrées de
  `veille.yaml` passent dans les fiches, et son journal en archive.
- Les constats faits en chemin sur le scénario 1, que
  `docs/decisions/0001/phase_0.md` liste (« Ce qui vient après ») : consignés
  le 25 septembre 2026 par la procédure de veille (plus bas), aucun corrigé.

Le propriétaire a tranché le même jour ce que le § 10 laissait ouvert :
`python -m pytest` reste la suite complète, qu'on passe avant d'envoyer sur
main, et la suite rapide est celle qu'on relance en travaillant
(`docs/architecture.md`, version 5.5). Les recettes de `CLAUDE.md` n'ont
donc pas à changer.

Relu le même jour sous l'angle des licences (§ 3.4), `documents-apportes.yml`
ne republie plus que ce que la licence permet. `source_locale.py --publier` ne
dépose sur la release que les documents dont le manifeste dit la rediffusion
`libre`, clause citée, et chaque ligne de la release nomme la licence ; un test
refuse qu'un document servi par la release ait une rediffusion interdite ou
non déclarée, et qu'un fichier de `data/brut/` soit versionné. Le seul document
que le workflow aurait déposé, le rapport de l'OPEF, l'interdit en toutes
lettres, page 180 : « Aucune représentation ou reproduction, même partielle,
[…] ne peut être faite de la présente publication sans l'autorisation expresse
du Secrétariat général du Comité consultatif du secteur financier ». Il était
versionné sous `data/brut/` depuis que le propriétaire l'y avait déposé
(action 51) ; il en est retiré, et son empreinte reste au manifeste.
L'historique git le garde : seule une réécriture de tout l'historique l'en
effacerait, et c'est au propriétaire d'en décider. Les deux fichiers de la Cour
des comptes que la release sert, déposés à la main le 24 septembre 2026,
restent `a_lire` : ses mentions légales ne se lisent pas depuis une session. Il
reste à les lire depuis un poste, puis à passer ces documents à `libre`, clause
citée, ou à retirer leurs assets.

Le même jour aussi, les actions des trois workflows, écrites pour Node 20 et
que GitHub exécutait sous Node 24 avec un avertissement, sont passées à leurs
dernières versions, qui tournent sous Node 24 : `checkout@v7`,
`setup-python@v7`, `setup-node@v7`. Aucune de leurs ruptures ne touche une
option qu'emploient ces workflows.

**Les constats du scénario 1, consignés sans être corrigés.** En écrivant ses
fiches d'exemple, la note 0001 avait relevé sur le scénario 1 des écarts
qu'elle ne corrigeait pas. Une session les a relus le 25 septembre 2026 dans
l'index LEGI, mot à mot, par la procédure de veille, et ils tiennent tous.
Pour les pensions prenant effet de la fin de 2003 au 1er avril 2010,
`D. 351-1-7` attribue les trimestres d'enfants un par un, à la naissance puis
à chaque anniversaire, huit au plus. Le modèle en sert huit d'un coup. La loi
n° 75-3, qui porte la majoration à huit trimestres dès le premier enfant,
s'applique « au 1er juillet 1974 » hors son titre II (article 21), et son
décret applique aux avantages prenant effet après le 30 juin 1974 l'article
sur la majoration des mères ; le modèle ne l'applique qu'à partir de 1975. Le
Journal officiel du 4 janvier 1975 reste à lire, pour savoir ce que couvre le
titre II : l'index n'a pas la structure de la loi. Cinq rédactions de `L. 351-4` changent le droit depuis 2013 sans être
découpées en versions : les parents de même sexe, le tuteur, le plancher de
deux trimestres pour la mère, le retrait de l'autorité parentale,
l'abrogation du IX. Au premier semestre 2011 enfin, `R. 13` du code des
pensions civiles et militaires admet la réduction d'activité, que `L. 12` b
ne nomme que pour les pensions prenant effet à compter du 1er juillet. La
ligne `majoration_duree_assurance_enfants` de `veille.yaml` passe donc de
`conforme` à `approximation` : son effet dit ce que le modèle approche, son
`a_faire` ce qu'il faut couper, avec les identifiants des versions. Le
journal de veille dit ce qui a été lu. Aucun exemple publié n'a été trouvé
pour ces fenêtres.

Deux constats de plus. L'action 26 disait les modèles des administrations
« pas publiés ». Le code de Destinie 2, de l'INSEE, l'est sur GitHub
(`InseeFr/Destinie-2`, sous GPL) ; celui de TRAJECTOiRE, de la DREES, l'est
sous EUPL. L'architecture les range déjà parmi les autres modèles (§ 3.4).
Et pour dix-sept des vingt-quatre règles déjà approchées au registre, l'effet
raconte l'erreur corrigée sans dire ce qui reste approché : le tableau de bord
le compte. Chacun de ces effets est à réécrire au présent, à la relecture de
sa règle.

**La phase 1, premier pas : l'écart connu.** Depuis le 25 septembre 2026, un
exemple officiel que le modèle ne reproduit pas entre quand même dans
`tests/temoins/exemples_officiels.yaml`, avec un champ `ecart_connu` : la
valeur que rend le modèle, l'explication, la date, et la ligne de veille qui
déclare l'écart. Cette ligne ne peut être ni `conforme` ni `transcrit`, et
compte l'exemple parmi ses témoins. Le test compare chaque grandeur publiée à
la mesure du modèle ; pour une grandeur en écart, il exige la valeur déclarée.
Si le modèle rend la valeur publiée, l'écart est corrigé, et sa déclaration se
retire ; s'il rend autre chose, le résultat a changé, et seul le diff du témoin
l'accepte. Le tableau de bord compte et liste ces écarts ; aucun exemple n'y
est ce jour-là. Pour s'assurer que rien ne se compare à vide, chacune des
121 grandeurs publiées a été faussée tour à tour : toutes ont été détectées,
et toutes, déclarées en écart avec la valeur du modèle, ont été admises.

**Le contrôle de conservation** (§ 12) est posé le même jour :
`scripts/conservation.py`. Avant de commiter un déplacement, `--depuis HEAD`
compare le dernier commit au répertoire de travail : tout paragraphe, toute
entrée de registre qui ne se retrouve pas quelque part, à l'identique, est une
perte. Le filet, lui, tourne à chaque envoi : `tests/test_conservation.py`
tient, contre une référence figée, `tests/temoins/conservation.json`, les
3 590 paragraphes gelés du dépôt et ses 1 290 entrées de registres. Sont
gelés les paragraphes des récits, des notes de décision et des archives, hors
les actions en cours de cette feuille de route et les tableaux que
`chiffrage_plf.py` réécrit. Deux paragraphes sont les mêmes aux blancs, aux
dièses d'un titre et aux valeurs des chiffres ancrés près. Un récit réécrit y
apparaît comme perdu, et c'est voulu : un récit est gelé. S'il faut vraiment
le réécrire, `--figer --accepter-les-pertes` refige la référence, et le commit
dit pourquoi.

**La feuille de route rangée**, le même jour. Ses 125 actions closes et son
journal sont passés, tels quels, dans `docs/archives/feuille_de_route.md` :
15 157 lignes, contre 1 748 qui restent ici. Le contrôle de conservation n'a
rien trouvé de perdu, et le déplacement est un commit à lui seul. Le tableau
de bord et le catalogue des affirmations lisent les deux côtés, et un test
tient le partage : une action close passe à l'archive.

**Les chiffres du dépôt sortis de la prose** (§ 9.3). Le nombre de tests
s'écrivait à trois endroits, le README, son arborescence et `limites.md`, et
chaque test ajouté obligeait à les récrire : trois fois en une journée. Il ne
s'écrit plus, ni les lignes du moteur et du portage que citait le préambule
de cette feuille de route ; `python scripts/tableau_de_bord.py --cout` les
affiche. Le test qui tenait le compte du README tient maintenant son absence.

**Les récits de `limites.md` et l'histoire de `CLAUDE.md`, rangés** le même
jour. Les 80 sections de récit de `limites.md` sont passées dans
`docs/archives/limites.md`, chacune sous les titres qui la contenaient. Il en
reste 2 803 lignes d'état, et `zones.yaml` ne déclare plus ses 116 sections une
à une : `etat` est son régime par défaut. `CLAUDE.md` est ramené à une page de
règles, 169 lignes au lieu de 326. Le texte d'avant est gardé tel quel dans
`docs/archives/conventions.md`, et non sous le nom `CLAUDE.md`, que Claude
Code chargerait comme des consignes dès qu'une session lit un fichier de ce
dossier. Chaque déplacement est un commit à lui seul, et le contrôle de
conservation n'y a rien trouvé de perdu.

**Ce que la phase 1 laisse ouvert.** L'annexe B veut `docs/fraicheur.md` en
note de décision, avec un contrôle des chiffres allégé, et
`docs/veille_droit.md` raccourci. Ces deux réécritures demandent de juger ce
qui reste une règle, et n'ont pas été tentées. Plusieurs documents mêlent
encore deux régimes, là où `zones.yaml` en voudrait un par fichier :
- les 30 procès-verbaux enclavés dans les sections d'état de `limites.md` ;
- les quatre paragraphes de récit du README ;
- la section de récit de `fraicheur.md`, celle de `veille_droit.md`, celle de
  l'intégration, et les deux d'`outillage_interface.md` ;
- les trois sections d'état d'`avantages_non_contributifs.md`, et le
  préambule d'état de cette feuille de route ;
- la liste des versions de l'architecture, qui est un récit par
  construction.

Le journal de veille reste dans `veille.yaml` : l'annexe B ne le range en
archive qu'avec le passage de ses entrées aux fiches, qui est la phase 2. Le
repère `phase-1` n'est pas posé : comme pour `phase-0`, il y faut un workflow
lancé une fois, et l'accord du propriétaire.

**La Cour des comptes et l'OPEF, tranchés le 26 septembre 2026.** Les
mentions légales de ccomptes.fr, que les sessions ne joignent pas, se lisent
dans l'archive du web : deux copies, du 4 août 2025 et du 22 mars 2026,
identiques au crédit des photographies près. « La reproduction des contenus
de ce site est autorisée », pourvu que `www.ccomptes.fr` soit cité avec la
date et l'intitulé du document, et que rien n'en soit altéré. Le rapport sur
les retraites des fonctionnaires de l'État passe donc à `libre`, clause citée,
avec le zip de ses données, qui a désormais son jeu au manifeste. Le PDF ne
porte aucune photographie, que la clause exclut : ses images sont les
graphiques et deux pages scannées d'une lettre. Une réserve est écrite au
manifeste. La même rubrique exclut les contenus où figurent des données
personnelles, sauf accord des intéressés, et le rapport nomme ses auteurs,
lettre signée comprise. Le dépôt le reproduit entier, comme la clause
l'exige, et l'asset se retire si la Cour le demande. La release doit citer la
source à côté de chaque document : `source_locale.py --mentions` l'écrit dans
la ligne qui le décrit, sans toucher au fichier, et `documents-apportes.yml`
le lance à chaque passe. Le rapport de l'OPEF, lui, reste dans l'historique
git : le propriétaire le garde, et l'historique n'est pas réécrit.

**La phase 1 achevée**, le 26 septembre 2026, à la demande du propriétaire.
`docs/fraicheur.md` est devenu une note de décision,
`docs/decisions/0002-fraicheur-de-la-prose.md`, qui en garde le texte entier,
et une page courte qui dit la règle : un régime par document, et ses
exceptions déclarées une à une. `zones.yaml` le suit. Le README, la
méthodologie et l'outillage d'interface y passent à `etat` par défaut, sans
plus déclarer leurs sections une à une, et le fichier passe de 500 lignes à
360 ; ce qu'il perdait, commentaires compris, est gardé dans
`docs/archives/zones.md`. Les récits d'`outillage_interface.md` et de
`veille_droit.md` ont rejoint leurs archives, et la procédure de veille ne
garde que la procédure : ses principes, ses trois pièces, sa règle, et le
tableau de bord pour l'état du registre. Restent, par construction, des
exceptions déclarées :
- les paragraphes de récit du README, texte de la proposition, et de la
  méthodologie ;
- les procès-verbaux enclavés dans `limites.md` ;
- la liste des versions de l'architecture, et le préambule d'état de cette
  feuille de route ;
- la section de récit de l'intégration, que l'annexe B garde inchangée ;
- les trois sections d'état d'`avantages_non_contributifs.md`, qui deviendra
  une vue à la phase 2.

Le repère `phase-1` marquera le commit qui porte cette note, comme `phase-0`
le dernier commit de la phase 0 : le propriétaire a demandé qu'on le pose, et
un workflow lancé une fois le fait.

Le repère `phase-1` est posé sur fc285ad, le même jour, par
`repere-phase-1.yml`, lancé une fois puis supprimé.

**La phase 2 achevée**, le 26 septembre 2026, à la demande du propriétaire.
Six commits, la suite complète passée avant chaque envoi sur `main`, et aucun
résultat qui bouge :
1. le vocabulaire des dates qui décident, `data/reference/vocabulaire/dates.yaml`
   — les quatre sortes, liste fermée, et trente dates nommées —, et les listes
   de valeurs, `valeurs.yaml`, dont deux fermées : les étapes et les statuts
   d'un texte ; un test les confronte au texte même de l'architecture ;
2. les neuf contrats de l'annexe C en schémas, `data/reference/contrats/`, que
   `src/retraite_notionnelle/noyau/contrats.py` applique : une erreur — champ
   inconnu, valeur hors vocabulaire, type faux — est refusée, un manque —
   champ obligatoire absent — est compté ;
3. la carte des règles : les 98 entrées de `veille.yaml` sont devenues les 98
   fiches de `data/reference/regles/`, sous le même identifiant, dont une
   relation, la priorité entre régimes pour les trimestres d'enfants. La
   veille en est une vue, et `veille.yaml` ne garde que ses sources et son
   journal. `conservation.py` retrouve chaque entrée dans sa fiche, à
   l'identique, et sa référence, refigée, tient désormais les archives ;
4. le partage des versions, contrôlé sur chaque fiche par l'outil que la note
   0001 avait laissé, qui rend sur les fiches de l'annexe A ce que rendait le
   prototype ;
5. la liste de contrôle des textes, `data/reference/textes/` : 10 738
   rédactions de 33 textes, lues dans l'index LEGI, leur statut lu dans les
   fiches, et le cliquet des rédactions sans statut posé à 10 549 ;
6. le tableau de bord, qui lit la carte et la liste sans avoir changé de
   questions.

**Ce que la phase 2 laisse ouvert.**
- Les fiches ne savent pas encore leur domaine, leurs régimes, leur étape, ce
  qu'elles lisent et écrivent, leurs dates qui décident ni leurs versions :
  805 manques, que le tableau de bord compte. Aucun cliquet ne les tient,
  pour qu'une règle découverte puisse entrer avant d'être mûre. Elles
  mûriront domaine par domaine (§ 11), à commencer par les dates des enfants.
- Le cliquet des textes ne compte que les articles. Les situations des
  fiches service-public et des circulaires n'ont pas de liste : il y faut
  celle des fiches retraite de service-public et l'index des circulaires de
  la Cnav, que le dépôt n'a pas. Les accords Agirc-Arrco et les statuts des
  caisses ne sont pas dans l'index LEGI.
- Le journal de veille reste dans `veille.yaml`, quand l'annexe B le rangeait
  en archive avec cette phase : la procédure lit encore « la dernière date du
  journal » pour savoir quoi consulter, et rien ne la remplace pour les
  circulaires et service-public ; `data/reference/textes/inscription.yaml` le
  fait déjà pour l'index LEGI. Il passera en archive quand la liste des
  situations l'aura rendu inutile.
- `avantages_non_contributifs.md` et `frontiere_contributive.md` deviendront
  des vues quand les fiches porteront leurs faces et leurs neutralisations,
  et l'inventaire des régimes quand chacune portera ses régimes : la note de
  la phase 1 qui l'annonçait pour la phase 2 allait trop vite.
- Le repère `phase-2` n'est pas posé : comme pour les deux premiers, il y faut
  un workflow lancé une fois, et l'accord du propriétaire.

**L'OPEF, rouvert le 26 septembre 2026.** Le propriétaire est revenu sur sa
première réponse : garder, pour les sources, une copie vérifiée par son
empreinte, ce n'est pas reproduire le rapport. Vérifié le même jour :
- la copie qui sert les sources est le fichier de `data/brut/`, que git
  ignore, et son empreinte SHA-256 au manifeste. La release
  `documents-apportes` ne l'a jamais porté : elle ne sert que les deux
  documents de la Cour des comptes ;
- mais le PDF, déposé le 20 septembre par l'interface web de GitHub sous le
  nom `OPEF2026_pdf.pdf`, renommé le jour même et retiré le 25, restait dans
  l'historique : dans l'histoire de chaque branche, de chaque repère `phase-*`
  et de trois des quatre références de pull request, et l'arbre de `phase-0`
  le portait, comme l'archive que GitHub en sert. Le dépôt est public :
  n'importe qui le téléchargeait. (Cette note disait d'abord le PDF dans le
  commit racine : c'était la limite d'un clone de session, qui ne porte
  qu'une partie de l'historique, et non la racine.)
- la clause de la page 180 n'admet que la copie privée et la courte citation
  (code de la propriété intellectuelle, L. 122-5, 2° et 3°, a). Une copie
  offerte à tous n'est ni l'une ni l'autre. Les trois valeurs saisies et les
  extraits que citent les tests sont de courtes citations, source nommée :
  ils restent.

L'effacer demande de réécrire tout l'historique, ce qu'une session ne fait
pas : `git filter-repo --invert-paths --path data/brut/OPEF2026.pdf` sur un
clone miroir, une poussée forcée des branches et des tags, puis une demande
au support de GitHub pour les références de pull request et les vues en
cache. Toutes les empreintes changeraient, comme le 23 septembre : chaque
clone serait à remplacer, et les empreintes que la prose cite, à reporter
depuis la table de correspondance que `filter-repo` écrit. L'autre voie est
de demander l'autorisation au secrétariat général du CCSF. La décision
revient au propriétaire.

Le repère `phase-2` est posé sur 6fb8284, le même jour, à la demande du
propriétaire, par `repere-phase-2.yml`, lancé une fois puis supprimé.

**L'historique réécrit, le 26 septembre 2026**, à la demande du propriétaire,
pour en retirer ce seul document, sous ses deux noms :
`git filter-repo --invert-paths --path data/brut/OPEF2026.pdf --path
data/brut/OPEF2026_pdf.pdf`, sur un miroir complet du dépôt. Vérifié commit
par commit : sur 818 commits, 474 réécrits et un retiré, celui du dépôt du
PDF, qui ne portait que lui ; aucun autre écart d'arbre, d'auteur ni de date,
et l'arbre de `main` identique au bit près. Les empreintes que la prose citait
sont reportées, et les récits gelés qui en citaient ont été refigés pour
cette seule raison. `main` a été remplacée le même jour ; le document n'y
est plus.

Il reste atteignable par trois chemins, qu'une session ne peut pas fermer :
- les repères, qui désignent encore l'ancien historique. Ils doivent passer,
  `phase-0` de dae2819 à 4bb438f, `phase-1` de 05ed5a9 à fc285ad, `phase-2`
  de 82463d5 à 6fb8284. Le jeton d'une session n'écrit pas de tag, et celui
  d'un workflow n'a pu ni les déplacer ni en créer un sur le nouvel
  historique (HTTP 403, deux passes de `reperes-reecriture.yml`, qui n'ont
  rien touché, puis retiré) : c'est au propriétaire de les replacer depuis
  son poste ;
- les trois vieilles branches `age-legal-65`, `claude/taux-etat-retraite-seule`
  et `claude/taux-etat-retraite-seule-7ggdie`, que le propriétaire supprime
  depuis l'onglet Branches ;
- les références des pull requests fermées 2, 3 et 4, que GitHub garde en
  lecture seule : leur purge, avec celle des vues en cache, se demande au
  support de GitHub. La référence de la pull request 1, d'avant la réécriture
  du 23 septembre, porte encore, elle, des adresses nominatives : la même
  demande peut la viser.

Vérifié le même jour, depuis un clone neuf de GitHub, après le passage du
propriétaire : les trois vieilles branches et les trois repères sont
supprimés, et un clone ordinaire, toutes branches et tous tags compris, ne
porte plus le document. Seules les références des pull requests fermées 2, 3
et 4 l'atteignent encore, jusqu'à ce que le support de GitHub les purge.

Les repères `phase-1` et `phase-2` sont reposés le même jour, sur fc285ad et
6fb8284, par `reperes-phases.yml`, lancé puis supprimé : le jeton d'un
workflow crée un tag quand les workflows du commit visé sont ceux de `main`.
`phase-0` ne l'est pas : son commit, 4bb438f, porte des workflows plus
anciens, et GitHub refuse d'y créer un tag au jeton d'un workflow comme à
celui d'une session (HTTP 403). Seul le propriétaire pourrait le poser, et
il a décidé le même jour de le laisser absent : la fin de la phase 0 reste
le commit 4bb438f, que cette note nomme.

**La phase 3, le 26 septembre 2026** (§ 11) : la chronologie datée et le
réseau de personnes, les présomptions d'aujourd'hui par défaut. Cinq commits,
et pas un résultat déplacé : les témoins sont restés identiques à l'octet, le
portage les reproduit comme avant, et 600 carrières tirées au hasard — des
parcours de un à quatre métiers, avec activités cumulées et interruptions, et
des relevés — donnent, par l'ancien chemin et par le nouveau, les mêmes années
au bit près (une vérification faite une fois, hors des tests). La suite
complète a passé avant chaque envoi sur main, sauf pour l'étape 4 : le hook
de fin de tour l'a envoyée pendant que tournait la suite qui la couvrait —
`pousser.sh` ne refuse des modifications non commitées que lorsqu'il doit
rebaser —, et cette suite a passé ensuite, avec l'étape 5.

1. **Le contrat et le vocabulaire.** La chronologie (C.1) reçoit, par la
   règle additive, son enveloppe — ses faits et ses liens, ce qu'une étape
   passe à la suivante — et le nom de la présomption qui pose un fait ; une
   période y vaut [début, fin). Les cinq présomptions du § 5.6 entrent au
   vocabulaire, chacune avec sa valeur et sa raison, et avec le fait qu'elle
   pose ou, à défaut, le code qui l'applique et l'étape où son fait entrera ;
   deux autres, que l'annexe A nommait sans que le § 5.6 les liste, les
   rejoignent à l'étape 5 : l'enfant élevé neuf ans, l'interruption
   d'activité de la mère seule.
   Une sorte de fait s'ajoute : la période où l'emploi s'interrompt, avec son
   motif. L'architecture passe en version 5.6.
2. **La chronologie** : `src/retraite_notionnelle/chronologie.py`. Le
   parcours et le relevé y deviennent des faits datés au jour ; les enfants,
   des personnes reliées à l'assuré par une filiation ; `completer` pose ce
   que la saisie ne dit pas, au nom de la présomption, sans jamais remplacer
   un fait déclaré.
3. **La carrière, vue de la chronologie.** Les constructeurs de `Carriere`
   passent par elle, et `Carriere.depuis_chronologie` en tire les années que
   le moteur liquide ; la carrière garde sa chronologie, et ses copies de
   travail aussi. Le moteur lit la naissance des enfants dans la chronologie :
   la constante `AGE_PRESUME_A_LA_NAISSANCE` quitte le code, et sa valeur ne
   vit plus qu'au vocabulaire. Une naissance déclarée prendrait la place de
   la présomption, et le moteur la lirait ; des naissances à des années
   différentes l'arrêtent, puisqu'il ne lit encore qu'une année pour tous.
4. **Le portage.** `moteur/js/chronologie.js`, fonction pour fonction ; le
   paquet de données porte les présomptions, et un test compare, au JSON
   près, les chronologies des deux moteurs.
5. **Les vues.** Cinq fiches de la carte disent les présomptions qu'elles
   lisent, sous leur nom au vocabulaire, et la carte refuse un nom qu'il ne
   connaît pas ; chaque présomption est lue par au moins une fiche. Le
   tableau de bord montre chacune, sa valeur, les fiches qui la lisent et
   où elle s'applique ; la méthodologie et les limites disent la
   chronologie.

**Ce qui reste ouvert.** Six présomptions sur sept s'appliquent encore
dans le code, faute de pouvoir poser leur fait avant leur étape : la
radiation se date par régime, les trois interpénétrés ensemble, et
l'Ircantec ne valide qu'au rétablissement — c'est la coordination des
affiliations (phase 4) ; la position statutaire de l'agent et l'accord des
parents, l'éducation de l'enfant et l'interruption d'activité se liront au
compte des durées. Le site ne montre pas encore les
présomptions qu'une simulation emploie : la chronologie les liste, la sortie
publique (C.9) les portera. Un régime spécial absent de la table des
services est présumé pouvoir pensionner : c'est une hypothèse sur le droit
(§ 4.7), pas sur la personne, et elle attend sa version supposée. Et
`scripts/scenarios_meres.py` place le premier enfant à vingt-huit ans en se
disant l'hypothèse du scénario 1, qui présume trente : sa grille est à relire
contre la présomption. Le repère `phase-3` n'est pas posé : comme les
précédents, il attend l'accord du propriétaire. La phase 4 suit :
l'acquisition en étapes et le relevé des droits, qui liront la chronologie
elle-même, et remplaceront le pont qu'est aujourd'hui la carrière.

Le repère `phase-3` est posé sur 75b545a, le même jour, à la demande du
propriétaire, par `repere-phase-3.yml`, lancé une fois puis supprimé.

**La phase 4, lancée le 26 septembre 2026** (§ 11) : l'acquisition en étapes
et le relevé des droits, sans qu'un résultat bouge. Mesuré avant d'y toucher,
par carrière, sur les 535 que les témoins simulent, données chargées
(§ 7.8) : 3,05 ms pour le scénario 1 en Python et 0,60 en JavaScript ; 25,8
et 4,05 ms pour les six scénarios. Cinq étapes, chacune envoyée sur main
après la suite complète :

1. les schémas des données que les étapes s'échangent, écrits avant leur
   code : un par étape dans `data/reference/etapes/`, contrôlés comme les
   contrats, et l'enveloppe du relevé (C.5) ;
2. `src/retraite_notionnelle/droit/` : le scénario 1 y déplace ce qui
   construit le relevé — le rétablissement et le routage de chaque ligne,
   les durées et les trimestres des enfants, les points et les cotisations —,
   et sa liquidation le lit ; les témoins restent identiques à l'octet ;
3. le portage, `moteur/js/droit/` ;
4. chaque étape testée seule, et comparée seule entre les deux moteurs ;
5. les vues, la mesure du budget, la documentation.

**La phase 4, faite le 26 septembre 2026** (§ 11) : l'acquisition en étapes
et le relevé des droits. Cinq commits, la suite complète avant chaque envoi
sur main, et pas un résultat déplacé : les témoins Python sont restés
identiques à l'octet, le portage les reproduit comme avant, et, sur les 535
carrières des témoins, les deux moteurs écrivent la même donnée à chaque
étape — 135 246 lignes de relevé, aucun écart (une vérification faite une
fois, hors des tests ; le test en rejoue une requête sur cinq).

1. **Les schémas**, écrits avant le code : un par étape dans
   `data/reference/etapes/`, contrôlés comme les contrats, et l'enveloppe du
   relevé (C.5). L'architecture passe en version 5.7.
2. **`src/retraite_notionnelle/droit/`** : `preparer`, `coordonner`,
   `compter`, `acquerir`, `releve`. Le code de l'acquisition quitte
   `scenarios/actuel.py` tel quel, les sommes se font dans l'ordre d'avant,
   et `calculer` ne lit que le relevé ; chaque ligne n'est plus routée
   qu'une fois.
3. **Le portage**, `moteur/js/droit/`, fonction pour fonction, préchargé par
   la page.
4. **Les tests** : chaque étape seule, chaque donnée contre son schéma, le
   relevé contre le contrat C.5, et les deux moteurs comparés étape par
   étape (`tests/test_droit.py`, `tests/js/comparer-droit.mjs`).
5. **Les vues** : le tableau de bord montre les étapes, les fiches qui disent
   les appliquer — neuf désormais —, et les lignes du relevé des cas types
   qui citent leur fiche ; la méthodologie, l'architecture (annexes A et B,
   § 7.8) et le README suivent ; `scripts/budget_calcul.py` refait la mesure
   dans les deux moteurs.

**Le budget**, mesuré dos à dos avant et après la phase, sur les 535
carrières des témoins : en Python, 2,71 puis 2,52 ms pour le scénario 1, 21,8
puis 21,3 ms pour les six scénarios ; en JavaScript, 0,56 puis 0,58 ms et 3,4
puis 3,3 ms, dans le bruit de la mesure (cinq pour cent d'une passe à
l'autre). La suite rapide passe de 14,7 à 14,9 secondes avec ses dix-huit
tests de plus, et la suite complète reste sous onze minutes.

**Ce qui reste ouvert.** Les salaires portés au compte restent calculés par
la liquidation, qui en choisit l'assiette sur la fiche du régime qui liquide :
ils entreront à l'étape « acquérir les droits » avec la liquidation en
fonction pure (phase 5). Les points gratuits de la RCO s'acquièrent dans
l'étape, mais lisent la durée requise et l'âge du taux plein par les
fonctions de la liquidation. Les étapes lisent encore la chronologie par sa
vue, la carrière — ses trimestres retenus, le plafond de ses années et la
part de l'année du départ restent des méthodes de `Carriere` —, et les tables
du scénario 1 par le moteur qui les tient, jusqu'aux fiches (phase 6). Les
lignes du relevé ne citent ni la version de leur règle ni le texte appliqué,
les fiches n'étant pas découpées en versions, et 3 % seulement citent leur
fiche sur les cas types. Le relevé n'est pas encore montré sur le site
(C.9), mais son écriture en lignes part avec le moteur, qui pèse 10 Ko
compressés de plus (971) : elle pourrait se charger à la demande. Et
`revalorisation.py` garde sa propre copie de la dernière année d'un régime,
qu'il pourrait prendre à `droit/commun.py`. Le repère `phase-4` n'est pas
posé : comme les précédents, il attend l'accord du propriétaire. La phase 5
suit : la liquidation en fonction pure, le journal, l'échéancier et le
pilote.

Le repère `phase-4` est posé sur d9e44fe, le même jour, à la demande du
propriétaire, par `repere-phase-4.yml`, lancé une fois puis supprimé.

**La phase 5, faite le 26 septembre 2026** (§ 11) : la liquidation en
fonction pure, le journal, l'échéancier et le pilote. Six commits, la suite
complète avant chaque envoi sur main, et pas un résultat déplacé. Les témoins
Python sont restés identiques à l'octet. Sur les 535 témoins, les sorties du
portage sont identiques au bit près avant et après, et les deux moteurs
appellent `liquider` le même nombre de fois, témoin par témoin.

1. **Les schémas**, écrits avant le code : les trois étapes de la liquidation
   — ouvrir le droit, liquider chaque régime, compléter tous régimes — et les
   deux que l'échéancier applique sans liquider, faire vivre et foyer et net.
   La liquidation (C.6) reçoit ses mesures, et l'architecture passe en
   version 5.8.
2. **`liquider(demande, état, contexte)`**, en Python : `droit/ouvrir.py`,
   `liquider.py`, `completer.py`, `foyer.py`, et `liquidation.py`, qui les
   enchaîne. Le code de la liquidation quitte `scenarios/actuel.py` tel quel.
   `calculer` en devient la façade, et ses drapeaux des neutralisations du
   contexte. Chaque avantage non contributif se mesure par une liquidation
   d'essai, et la liquidation dit ce qu'elle a mesuré.
3. **Le journal, l'échéancier, le pilote** : `journal.py`, `echeancier.py`,
   `pilote.py`. Le simulateur fait passer le scénario 1 par l'échéancier.
   « Faire vivre » devient une étape de `revalorisation.py`, l'ASPA de
   l'échéance passe par « foyer et net », et le point fixe des cas types
   passe au pilote.
4. **Le portage**, fonction pour fonction : `moteur/js/droit/` et
   `journal.js`, `echeancier.js`, `pilote.js`, préchargés par la page.
5. **Les tests** : chaque étape seule contre son schéma, la liquidation contre
   le contrat C.6, l'événement contre le C.7, le journal contre le C.8. Les
   deux moteurs sont comparés sur les étapes et sur le journal
   (`tests/test_liquidation.py`, `tests/js/comparer-liquidation.mjs`). Chaque
   témoin déclare ses appels de `liquider` : de 1 à 6, et aucun au-delà des 6
   du nombre déclaré (`APPELS_DECLARES`, § 7.8).
6. **Les vues** : treize fiches disent l'étape de la liquidation ou de
   l'échéancier qui les applique, vingt-deux avec celles de l'acquisition. Le
   tableau de bord montre ces étapes et les appels déclarés. La méthodologie,
   l'architecture (annexe B, § 7.8 ; version 5.9) et les renvois des
   registres suivent, et `scripts/budget_calcul.py` refait la mesure.

**Le budget**, mesuré dos à dos avant et après la phase, le meilleur de deux
tours, sur les 535 carrières des témoins : en Python, 2,45 puis 2,39 ms pour
le scénario 1, 20,6 puis 20,1 ms pour les six scénarios ; en JavaScript, 0,50
puis 0,51 ms et 3,0 puis 3,0 ms, dans le bruit de la mesure. La suite rapide
passe de 13,4 à 13,7 secondes avec ses vingt-neuf tests de plus, et la suite
complète tient en neuf minutes et demie. Le moteur pèse 16 Ko compressés de plus
(987) : les étapes écrivent leurs données, et l'échéancier tient son journal.

**Ce qui reste ouvert.**

- **L'échéancier ne connaît que le départ**, tiré de la carrière. Les autres
  sortes d'événements du vocabulaire (seconde pension, réversion, révision)
  attendent leurs domaines.
- **« Faire vivre » applique d'un coup**, à l'échéance, les revalorisations
  publiées depuis le départ, dans l'ordre où `revalorisation.py` les compose.
  Une revalorisation par date, que chaque fiche inscrirait à la sienne,
  changerait l'ordre des produits, donc les derniers chiffres des pensions :
  elle viendra avec les fiches.
- **Pour qui est déjà parti à la bascule**, les scénarios notionnels refont
  la liquidation du départ (`_deja_liquide`), deux fois, liquidations d'essai
  comprises : ces témoins liquident trois fois le même départ, que
  l'échéancier pourrait leur donner.
- **L'essai sans l'AVPF ne déplace la pension d'aucun témoin** : la période
  d'éducation valide ses trimestres d'elle-même, et le salaire au SMIC que
  l'AVPF porte au compte ne joue que sur le salaire de référence. L'essai
  tourne, et coûte un appel, sans qu'aucun témoin montre ce qu'il mesure.
- **Les étapes lisent encore les tables** du scénario 1 par le moteur qui les
  tient, jusqu'aux fiches (phase 6). La demande ne nomme pas encore les
  régimes qu'elle vise, un manque du contrat C.6, et le contexte n'a ni date
  d'observation ni hypothèse. Les salaires portés au compte restent choisis
  par la liquidation, et non par l'acquisition.
- **Le repère `phase-5` n'est pas posé** : comme les précédents, il attend
  l'accord du propriétaire. La phase 6 suit : un fichier par régime, et les
  interrupteurs deviennent des renvois aux fiches.

Le repère `phase-5` est posé sur 4db363e, le 27 septembre 2026, à la demande
du propriétaire, par `repere-phase-5.yml`, lancé une fois puis supprimé.

**La phase 6, faite le 27 septembre 2026** (§ 11) : un fichier par régime, et
les interrupteurs deviennent des renvois aux fiches. Quatre commits, la suite
complète avant chaque envoi sur main, et pas un résultat déplacé : le
catalogue chargé est identique période par période, le paquet du portage à
l'octet, les témoins aussi.

1. **Un fichier par régime** : les 74 régimes calculés quittent leurs cinq
   fichiers de familles, au texte près, chacun dans
   `data/reference/regimes/<code>.yaml`. L'ordre où le catalogue les lit
   départage la fusion : il devient un champ, `rang`. Les ancres de la prose,
   la sonde `fiche_regime`, les contrôles de `verifier_donnees.py` et les
   cibles du manifeste des sources nomment le fichier du régime.
2. **L'inventaire, vue fabriquée** : chaque régime porte sa ligne (le bloc
   `inventaire`), et les dix-sept que le modèle ne calcule pas ont leur
   fichier. `scripts/construire_inventaire.py` écrit `inventaire.yaml`, relu
   identique ; la famille, les dates et la lignée ne s'écrivent plus qu'une
   fois.
3. **Les renvois** : 2 103 interrupteurs, dans 56 régimes, renvoient à 38
   fiches, qui déclarent la valeur (`code.interrupteurs`) et disent ce que le
   moteur en fait (`code.moteur`) ; dix fiches naissent « à vérifier » pour
   les règles qu'aucune ne décrivait. Le schéma passe en version 3 et ne
   garde de chaque interrupteur que sa définition ; le chargeur refuse une
   valeur à la place d'un renvoi.
4. **Les vues** : le tableau de bord compte les fiches que les interrupteurs
   désignent ; l'architecture passe en version 5.10, et l'annexe B dit où
   sont allés les fichiers de régimes, le schéma et l'inventaire.

**Le budget** : charger le catalogue, dos à dos avant et après la phase, le
meilleur de six fois, prend 1 544 puis 1 533 ms à froid, où l'analyse des
YAML domine, et 38 puis 50 ms à chaud : les deux mille renvois se résolvent
fiche par fiche, chacune lue une fois par chargement.

**Ce qui reste ouvert.**

- **Les dix fiches nouvelles sont à relire à la source** : chacune dit, dans
  `sources.a_relire`, par où commencer ; `veille_droit.py` les liste.
- **Les fiches ne disent pas encore leurs régimes**, que le contrat exige
  (`regimes`, qui manque aux 108) : pour les 38 que les interrupteurs
  désignent, les renvois le disent déjà, et la liste pourrait s'en fabriquer.
- **Une fiche dit la valeur qu'elle pose, pas encore sa fonction** : le code
  qui lit chaque interrupteur reste dans `droit/`, sans que la fiche le nomme.
- **Les paramètres des périodes** — taux, âges, durées — restent dans les
  fichiers de régimes ; ils attendent les versions des fiches (§ 4.1).
- **Les récits datés gardent les valeurs d'alors** : l'effet d'une fiche ou
  la note d'une période qui écrit `decote_par_generation: true` disent ce
  que la période portait avant la phase.
- **Le repère `phase-6` n'est pas posé** : comme les précédents, il attend
  l'accord du propriétaire. La phase 7 suit : la proposition réécrite en
  univers de droit.

Le repère `phase-6` est posé sur 49a01da, le 27 septembre 2026, à la demande
du propriétaire, par `repere-phase-6.yml`, lancé une fois puis supprimé.

**La phase 7, faite le 27 septembre 2026** (§ 11) : la proposition réécrite
en univers de droit. Trois commits, la suite complète avant chaque envoi sur
main, et pas un résultat déplacé : les témoins Python sont identiques à
l'octet, et sur les 535 témoins, les sorties du portage le sont au bit près,
avant et après.

1. **Les univers, en Python** : les six scénarios sont six univers
   (`data/reference/univers/`), piles de huit couches
   (`data/reference/couches/`) posées sur le droit réel. Le 4 est le 2 plus
   la part patronale, le 5 est le 3 plus la même. Le prospectif est le
   rétroactif posé sur la transition, et une couche d'un seul calcul, « au
   contributif seul », sert la liquidation fictive de la bascule. Neuf fiches
   de la proposition (`data/reference/regles/proposition/`) citent le README
   mot pour mot et nomment leur code. `noyau/univers.py` tient le contrat C.4
   et les règles de la pile. `scenarios/univers.py` dit ce que le moteur en
   tire, et refuse ce qu'il ne sait pas faire. Le simulateur bâtit les
   scénarios 2 à 6 depuis les univers ; la liste des scénarios, les
   prospectifs de la page Coût et la pension d'aujourd'hui s'en tirent aussi.
2. **Le portage** : le paquet porte les univers résolus, et
   `moteur/js/simulateur.js` en tire ses scénarios comme le Python. Le taux
   unique reste un renvoi à `taux_cotisation_liberal`, que le site lit sous
   ses réglages. Deux tests confrontent les moteurs.
3. **Les vues** : le tableau de bord montre les univers et, pour chacun, les
   fiches du droit réel sans décision (§ 8). L'architecture passe en version
   5.11, et l'annexe B dit où la proposition est allée.

**Le budget**, dos à dos avant et après la phase, le meilleur de plusieurs
tours, sur les 535 carrières des témoins : en Python, 3,11 puis 2,98 ms pour
le scénario 1, 26,62 puis 26,81 ms pour les six scénarios ; en JavaScript,
0,68 puis 0,66 ms et 4,24 puis 4,23 ms. C'est le bruit de la mesure, plus
large d'un tour à l'autre que d'un arbre à l'autre : un premier tour
montrait les six scénarios du portage plus lents de 6 %, que trois tours
alternés ont démentis. Les univers ne coûtent qu'au démarrage. L'import du
simulateur, qui les charge, passait de 145 à 470 ms tant que leur contrôle
lisait toute la carte ; il ne lit plus que le nom des fiches, et l'import
prend de 210 à 260 ms. La règle des décisions contraires, la seule qui lise
les fiches, reste aux tests (`univers.controler`).

**Ce qui reste ouvert.**

- **66 fiches du droit réel sont sans décision** dans chaque univers de la
  proposition. Soixante ne disent pas encore leur étape : une couche ne les
  atteint que par leur nom, et leur étape les rangera. La plupart sont des
  règles de la liquidation, que le compte notionnel remplace. Les six qui
  disent leur étape sont des décisions qui manquent, et le tableau de bord
  les nomme.
- **Le compte ne porte pas la cotisation que prélève l'assiette minimale des
  indépendants** (`assiette_minimale_independants`, que le scénario 1
  applique) : il la calcule sur le revenu réel. C'est peut-être un écart au
  « la cotisation retraite effectivement versée est inscrite au compte » du
  README : à trancher, par une note de décision.
- **Trois fiches mêlent la cotisation et le droit** (`carpimko_assiette_2026`,
  `cavom_assiette_2016`, `cipav_seconde_tranche`). Le compte en applique la
  cotisation, par les périodes des régimes. Quand elles diront leur face, ou
  seront coupées en deux, une couche en gardera la cotisation par sélecteur.
- **La variante prospective de la proposition**
  (`scripts/proposition_prospective.py`) remplace encore une méthode le temps
  d'un calcul. Le moteur ne sert ni le pilier ni la garantie sur un compte
  ouvert à la bascule : servis là, elle deviendrait un univers de plus, que
  la comparaison et la page Coût apprendraient à montrer.
- **Le pilote et les pages lisent encore les univers par leur identifiant** :
  la page Coût range la proposition, sa recette et sa garantie sous
  `notionnel_liberal`, et le portage garde sa liste des univers prospectifs,
  qu'un test tient égale à celle du Python. Le pilote par univers vient avec
  les domaines (§ 13.5).
- **`restitution.py`**, la moitié des impôts affectés rendue aux salaires,
  n'a pas encore de fiche : il ne touche pas la pension, mais la fiche de
  paie et la page Coût.
- **Le repère `phase-7` n'est pas posé** : comme les précédents, il attend
  l'accord du propriétaire. La phase 8 suit : le texte du site écrit une
  fois.

**Une correction de la note qui précède**, le même jour : la phase a fait
quatre commits, non trois, et l'un est parti sur main avant la fin de la
suite complète qui l'éprouvait. Le hook de fin de tour a poussé l'étape 2
(d15d401) pendant qu'elle tournait ; elle a trouvé un échec, `test_prose.py`,
les poids du paquet que la prose annonçait, et de9e6a6 l'a réparé, rejoué par
GitHub sans échec. Le message de d15d401 dit « N tests passés » : c'était
2 660, et cet échec. Une session qui commite avant que la suite complète ait
fini ne finit pas son tour : le hook publierait le commit.

Le repère `phase-7` est posé sur 17b54f3, le 27 septembre 2026, à la demande
du propriétaire, par `repere-phase-7.yml`, lancé une fois puis supprimé.

**La phase 8, faite le 27 septembre 2026** (§ 11) : le texte du site écrit une
fois. Cinq commits. Un seul résultat bouge, celui que la phase rendait faux :
- les témoins de simulations et le paquet du site sont identiques à l'octet ;
- ceux des pages le sont aussi, sauf un paragraphe de la page Méthode, qui
  disait les deux rendus comparés.

1. **La saisie et le contexte sortent du site** (d317c7f). `web/pages.py`
   mêlait le texte du site et ce que le calcul lit. Le second passe dans deux
   modules, et le code est déplacé à l'octet près :
   - `saisie.py` : ce que l'adresse d'une simulation dit, lu en carrière et
     en règles ;
   - `contexte.py` : les données du site, et le jeu de règles sous lequel il
     calcule.

   Le portage prend le même découpage : `saisie.js` et `contexte.js`.
2. **Le Python lit le site dans son portage** (483d1c1). `web/site.py` lance
   node (`site.mjs`) et lui demande une page, une constante ou une fonction
   d'un module du portage ; une instance revient par référence.
   - Les témoins de pages en sortent, identiques à ceux que le Python avait
     figés.
   - Les tests des pages y lisent le site, et confrontent ce qu'il écrit à
     ce que le modèle Python calcule.
   - Les scripts y lisent ce que le texte du site décide : les règles
     d'indexation comparées, les systèmes que le bilan couvre, les
     décimales que la méthodologie cite.
3. **Le site dit comment on le vérifie** (372b478). La page Méthode disait
   « chaque page du site est rendue par les deux [moteurs], et comparée
   caractère par caractère ». Elle dit maintenant que le texte n'est écrit
   qu'une fois, et que chaque page est figée en témoin.
   - Le § 12 veut les pages reproduites au bit près ; reproduite, celle-ci
     aurait dit faux. Le changement a son commit, et son témoin ne bouge
     que de ce paragraphe.
   - Les deux tests qui comparaient les deux rendus confrontent maintenant
     les deux moteurs. Le site refuse ce que le modèle refuse, du même mot,
     et rend le reste sans trou.
4. **Le rendu Python est retiré** (e483229). `web/pages.py` et
   `web/gabarit.py` n'existent plus.
   - La feuille de style est sa propre source, `moteur/style.css`.
   - Les 129 commentaires du portage qui renvoyaient au Python portent ce
     que ses docstrings disaient. Le code des deux fichiers, lu sans ses
     commentaires, est inchangé.
   - L'ancien rendu se relit au repère `phase-7`.
   - L'architecture passe en version 5.12, et `CLAUDE.md` dit où le texte du
     site s'écrit.
5. **Les tests sans node, le tableau de bord, la veille** (ce commit). Sans
   node, la suite comptait 25 échecs :
   - 22 tests des pages et de la prose, qui lisent le site par node depuis
     l'étape 2 ;
   - 3 comparaisons des deux moteurs, nées aux phases 3 à 5, qui lançaient
     node sans vérifier qu'il était là.

   Ils sont sautés, comme le dépôt saute ce qu'il ne vérifie pas sans node,
   et le contrôle des sondes garde celles qui répondent sans lui.

**Le coût.**
- Le site transfère 25 Ko de plus au premier chargement : 1 014 Ko
  compressés au lieu de 989, et 5 627 Ko bruts au lieu de 5 563.
  - 3 Ko tiennent aux deux modules nouveaux, compressés chacun à part, et à
    leurs imports ;
  - 22 Ko tiennent aux commentaires, qui voyagent avec le portage : il n'a pas
    d'étape de construction.
- La suite complète a raccourci, sur quatre cœurs : 11 min 26 à l'étape 1,
  quand ses tests rendaient encore les pages par le Python ; 8 min 20 aux
  deux commits suivants, et 9 min 47 au quatrième.

**Ce qui reste ouvert.**

- **Les listes de la saisie portent encore leurs libellés en Python**
  (`PROFILS`, `INDEXATIONS`…, dans `saisie.py`). Le Python n'en lit que les
  codes : les libellés sont du texte du site, que seul `saisie.js` affiche.
  Ils pourraient n'être écrits que là, un test tenant les codes égaux des
  deux côtés.
- **La liste des systèmes montrés vit dans le texte du site**
  (`SCENARIOS_MONTRES` de `pages.js`). Le paquet la lit par node pour
  construire son bilan : le fabriquer demande désormais node.
- **Le contrôle de conservation** « se retire après la phase 8, quand plus
  rien ne se déplace » (§ 12). Les domaines déplaceront encore des fichiers :
  le garder ou le retirer est une décision du propriétaire.
- **Le repère `phase-8` n'est pas posé** : comme les précédents, il attend
  l'accord du propriétaire. Il se posera sur ce commit, quoi qui le suive :
  les corrections que l'action 131 gardait « après la phase 8 » peuvent se
  faire, chacune dans son commit, avec le diff de ses témoins. Les phases de
  réorganisation sont finies ; les domaines suivent, un à la fois (§ 11).

Le repère `phase-8` est posé sur 9799ba4, le 27 septembre 2026, avec l'accord
du propriétaire, par `repere-phase-8.yml`, lancé une fois puis supprimé.

**Le contrôle de conservation reste**, décidé par le propriétaire le même
jour. Le § 12 le retirait « après la phase 8, quand plus rien ne se
déplace » ; or les domaines déplaceront encore des fichiers, et un récit ne
se réécrit pas, quelle que soit la phase.
- Il a tenu les déplacements des phases 1, 2 et 6.
- Le 26 septembre, pendant la phase 4, il a refusé la réécriture d'un
  récit : la liste des fichiers observés le 17 septembre, dans
  `docs/integration-partiliberalfrancais.md`, à laquelle une mise à jour
  ajoutait `moteur/js/droit/*.js`, qui n'existait pas encore.

Sa référence se refige désormais à la fin de chaque domaine, pour protéger
les récits nés depuis : `docs/architecture.md`, version 5.13 (§ 11 et
§ 12), et `CLAUDE.md`. Elle l'a été en dernier par a8e8139, après la phase 8.

Une correction de la phase 8, le même jour : `.gitattributes` tenait encore
`moteur/style.css` pour un fichier fabriqué, que git ne fusionne pas et
qu'un script refait. Il ne l'est plus depuis e483229. Un conflit sur lui
aurait gardé un seul côté, sans script pour refaire l'autre ; il se
fusionne désormais comme tout texte écrit à la main.

**Le premier domaine, les dates des enfants, ouvert le 27 septembre 2026**
(§ 11), à la demande du propriétaire. L'ordre se mesure au moment de choisir,
sur les sources publiques ; le premier l'a été ce jour-là :
- les enfants : près de 90 % des retraitées des générations 1930 à 1953 ont
  validé des trimestres à ce titre, la majoration pour trois enfants va à
  38 % des retraités nés en 1953, et plus d'une femme sur deux née de 1954 au
  début des années 1980 a des droits à l'AVPF (COR, rapport « Droits
  familiaux et conjugaux » de novembre 2025, publié en avril 2026, partie 1,
  chapitre 3, sur l'EIR 2020) ;
- la réversion : 4,4 millions de bénéficiaires en 2023, 24,3 % des retraités
  (même rapport, sur l'EACR) ;
- l'invalidité et l'inaptitude : 19 % des nouveaux retraités du régime
  général en 2024 (COR, rapport annuel de juin 2026) — un flux, que la
  mesure du domaine suivant devra ramener à un effectif.

Les enfants passent donc les premiers, et la réversion paraît devoir
précéder l'invalidité. Le site de la DREES ne répond pas d'une session : les
autres domaines se mesureront chacun à son tour.

**Première étape : chaque enfant compte à sa date.** Aucun témoin ne bouge,
et le modèle sait désormais ce qu'il ne savait pas :
1. **Les fiches en versions.** `majoration_duree_assurance_enfants` ne porte
   plus que la majoration du régime général (L. 351-4), en six versions ; la
   fonction publique a sa fiche, `enfants_fonction_publique`, en sept, celles
   de l'annexe A. Ce sont les deux premières fiches découpées de la carte,
   et le moteur les lit : `noyau/versions.py` choisit la version par les
   dates qui décident, et son jumeau `moteur/js/versions.js` fait de même sur
   le paquet, qui les porte. `majoration_duree_assurance.csv` disparaît, son
   en-tête passé dans leur historique. Leurs bornes reproduisent d'abord le
   modèle : le b ter au 1er janvier 2026, la loi n° 75-3 au 1er janvier 1975,
   huit trimestres d'un coup de 2004 à 2010. Ce sont des approximations
   déclarées, que les étapes suivantes corrigent une à une, chacune avec le
   diff de ses témoins.
2. **La chronologie** date chaque enfant : la saisie peut déclarer la
   naissance des premiers (`naissances=1999,2004-11`), à l'année ou au mois,
   et la présomption ne pose que celles qui manquent. La carrière ne s'arrête
   plus sur des enfants nés à des années différentes.
3. **L'étape `compter_les_durees`** (schéma en version 2) compte les enfants
   un par un : la version de chacun se lit sur sa naissance et sur la date
   d'effet de la pension, et la priorité entre régimes se lit pour chacun —
   le régime général accorde l'enfant qui n'ouvre pas droit dans le régime
   spécial, comme l'écrit la circulaire Cnav 2017-01 (fiches 6.2a et 6.2b,
   « Compétence »). Chaque ligne d'enfant du relevé cite sa fiche, sa version
   et le texte appliqué : les premières de la carte à le faire.
4. **Les témoins** : trois de plus, aux enfants datés, que les deux moteurs
   rendent à l'identique, étape par étape ; les 535 d'avant restent
   identiques à l'octet, et les pages aussi.

Lu en chemin, dans l'index LEGI et au Journal officiel : le décret
n° 2003-1280, article 3, applique le trimestre par anniversaire aux pensions
prenant effet à compter du 1er janvier 2004, ce que l'annexe A laissait en
hypothèse ; la loi n° 75-3 s'applique au 1er juillet 1974, l'index ne datant du
4 janvier 1975 que ses articles 7 et 8, son titre II ; la loi n° 2009-1646,
article 65, VIII et IX, pour les pensions depuis le 1er avril 2010 et les
enfants nés avant 2010. Restent de ce domaine : le bloc du formulaire, les
trois corrections, les exemples publiés aux enfants datés, la page Coût et la
décision de la proposition, puis la référence de conservation à refiger.

**Deuxième étape : le bloc du formulaire**, le même jour. Le champ
« Naissance des enfants », facultatif, suit le nombre d'enfants parmi les
options : « 1995, 1998-06 », dans l'ordre des enfants ; ceux qu'il ne date
pas restent présumés, et sa bulle dit à quel âge. Les pages du simulateur
en changent, rien d'autre. Quatre témoins de plus fixent, aux bornes que les
fiches déclarent approchées, ce que le modèle rend avant que chaque
correction le déplace : une pension de la fonction publique d'avril 2026 et
un enfant né en 2005, pour le b ter ; une pension de juillet 1974 et un
enfant unique, pour la loi n° 75-3 ; une pension de 1990 et un enfant de
cinq ans, pour la condition des neuf ans d'éducation ; une pension de 2008
et un enfant de quatre ans, pour le trimestre par année d'éducation.
`docs/limites.md`, `docs/methodologie.md` et l'architecture le disent : les
naissances se déclarent, et la présomption ne pose que celles qu'on tait.

**Première correction : le b ter à sa date.** L. 12 b ter vaut pour les
pensions prenant effet à compter du 1er septembre 2026 (loi n° 2025-1403,
article 104), et non dès janvier, comme le modèle le faisait en datant à
l'année : les versions `l12bis` et `l12bter` se coupent désormais au
1er septembre, et l'approximation se retire de la fiche. La fiche F37311 de
service-public.gouv.fr, relue le même jour, dit la même règle : des deux
trimestres d'un enfant né depuis 2004, « l'autre trimestre est pris en compte
[…] pour le calcul de votre pension ». Un seul témoin bouge, celui de la
bascule : la fonctionnaire partie en avril 2026 perd le trimestre de services
de son enfant né en 2005, 133 cent-soixante-neuvièmes au lieu de 134, et sa
pension passe de 23 561 à 23 386 euros par an. Un test tient la veille et le
jour de la borne (`tests/test_trimestres_enfants.py`).

**Deuxième correction : la loi n° 75-3 à sa date, et l'enfant élevé neuf
ans.** Deux circulaires de la Cnav, lues dans sa base législative, disent ce
que les textes laissaient à déduire : la n° 2/72 (§ II B 1°), que la loi
Boulin sert « une année d'assurance supplémentaire par enfant élevé » neuf
ans avant ses seize ans, à la mère d'au moins deux tels enfants, « Un enfant
n'ouvre aucun droit » ; la n° 31/75, que les deux années par enfant « le
premier enfant y ouvrant droit » valent, comme toute la loi n° 75-3, pour
les avantages prenant effet après le 30 juin 1974 (§ 35 et 7). Les versions
`mda_1972` et `mda_1975` se coupent donc au 1er juillet 1974, et leur
condition d'éducation se lit sur l'âge de l'enfant à la date d'effet : celui
qui n'a pas neuf ans ne peut pas avoir été élevé neuf ans, et ne compte ni
pour la majoration ni pour les deux enfants de la loi Boulin. La présomption
`enfant_eleve_neuf_ans` ne porte plus que sur ce qu'on ne sait pas : que la
mère a élevé les autres. Deux témoins bougent, ceux des bascules : la mère
d'un seul enfant partie en juillet 1974 reçoit huit trimestres (126
cent-cinquantièmes au lieu de 118, 1 394 euros par an au lieu de 1 320) ; la
mère partie en 1990 perd ceux de son enfant de cinq ans (seize trimestres
ramenés à huit, taux de 32,5 % ramené à 25 %, 5 791 euros par an au lieu de
7 460). `par_enfant` reçoit désormais les naissances de tous les enfants,
et les deux chronologies savent compter des années révolues.

**Troisième correction : de 2004 à mars 2010, un trimestre par année
d'éducation.** D. 351-1-7, que le décret n° 2003-1280 applique aux pensions
prenant effet à compter du 1er janvier 2004, accorde un trimestre à la
naissance, puis un « au terme de chaque année d'éducation », huit au plus,
et la circulaire Cnav n° 2004/22 ajoute que « la condition de durée minimum
d'éducation de 9 ans est supprimée ». La version `mda_2003` les compte
désormais un à un, à la date d'effet ; l'anniversaire qui tombe ce jour-là
compte, l'année qu'il clôt étant accomplie la veille (`unites.ancrage` de la
version). Un témoin bouge, celui de la bascule : la mère partie en 2008
reçoit cinq trimestres, et non huit, pour son enfant de quatre ans (treize
au lieu de seize pour ses deux enfants, 133 cent-soixantièmes au lieu de
136, 10 313 euros par an au lieu de 10 475). Les trois corrections faites,
les constats du 25 septembre consignés dans la fiche sont clos, sauf le
dernier : les rédactions de L. 351-4 depuis 2013, à couper en versions.

**Le domaine se clôt le même jour**, le gabarit du § 11 rempli :
- **les exemples publiés** : deux de plus, tirés de la fiche F37311 aux
  enfants datés — la fonctionnaire mère d'un enfant né en 2001 et d'un autre
  né en 2006 réunit six trimestres, celle qui a accouché en 2006 avant son
  recrutement de 2010 n'en reçoit aucun de la fonction publique —, que le
  modèle rend tous deux ; les exemples officiels savent désormais dater les
  enfants (`naissances_enfants`) ;
- **la relation** `priorite_majorations_enfants` mûrit : elle relie les deux
  fiches découpées, porte son domaine, ses régimes, son rang, et six
  versions, les rédactions de l'article 16 du décret n° 75-109 (1975, 1982)
  et de R. 173-15 (1985, 2001, 2008, 2011), lues dans l'index LEGI. Elle
  passe `approchee` : le moteur applique partout la règle de 1982, où le
  texte de 1975 et la circulaire Cnav n° 31/75 écartaient le régime général
  dès qu'un régime spécial était en cause ;
- **la page Coût** ne bouge pas : aucun de ses chiffres n'a changé dans les
  commits du domaine ;
- **la décision de la proposition** est déjà prise : la couche
  `comptes_notionnels` neutralise l'étape `compter_les_durees`, où
  s'appliquent les trois fiches du domaine, et le README le dit (« Ni
  majorations enfants, ni MDA, ni AVPF, ni bonifications ») ; les naissances
  n'y changent rien, comme le formulaire l'annonce ;
- **la référence de conservation** est refigée
  (`python scripts/conservation.py --figer`) : elle tient désormais les
  récits nés depuis la phase 8, ceux du domaine compris.

Restent, hors du domaine clos, et consignés dans ses fiches : les rédactions
de L. 351-4 depuis 2013, à couper en versions ; l'adoption, que la chronologie
ne connaît pas encore ; l'enfant handicapé ; la majoration d'éducation d'un
enfant de moins de quatre ans depuis 2010 ; l'exception de la CRPCEN. Le
domaine suivant se mesurera à son ouverture : la réversion paraît devoir
précéder l'invalidité.

**Le deuxième domaine, la réversion, ouvert le 28 septembre 2026**, sur la
demande de continuer. L'ordre s'est mesuré ce jour-là, sur ce que les
sources publiques dénombrent :
- la réversion : 4,41 millions de bénéficiaires d'un droit dérivé tous
  régimes fin 2024, dont 3,86 millions résidant en France (DREES, enquête
  annuelle auprès des caisses de retraite, classeur du 26 mai 2026, feuille
  de cadrage, champ `ddert`) ;
- l'invalidité et l'inaptitude : 2,26 millions de retraités partis au taux
  plein à ce titre fin 2016, 0,90 pour invalidité et 1,36 pour inaptitude,
  sur 16,0 millions (DREES, échantillon interrégimes de retraités 2016,
  jeu `rec05`) ; en flux, 19 % des nouveaux retraités du régime général
  en 2024 (COR, rapport annuel de juin 2026) ;
- les carrières hors de France : 1,28 million de retraités résidant à
  l'étranger fin 2024 (même enquête), un minimum ; 20,3 % des retraités
  étaient nés à l'étranger fin 2016 (`rec08`) ;
- les périodes assimilées manquantes — apprentissage, stages, TUC,
  sportifs, congé de naissance — ne sont dénombrées par aucune source
  trouvée : l'EIC et l'EIR de la DREES ne les isolent pas.

La réversion passe donc la deuxième, devant l'invalidité, et la liste de
première lecture du § 11 se réordonne à mesure. Le site de la DREES ne
répond toujours pas d'une session ; son portail de données ouvertes, si.

**Première étape : les fiches lues.** Aucun témoin ne bouge : le moteur ne
calcule pas encore la réversion.
1. **`reversion`**, qui ne portait que son intitulé, devient la fiche du
   régime général et des régimes alignés, en quatorze versions, partage de
   la date d'effet de la réversion et du décès : 50 %, 52 % au 1er décembre
   1982, 54 % au 1er janvier 1995 ; la condition de ressources d'ouverture,
   puis, en juillet 2004, l'écrêtement sous 2 080 heures de SMIC, 1,6 fois
   pour le ménage, et la fin de la condition de durée de mariage ; l'âge,
   55 ans, 52 en juillet 2005, 51 en juillet 2007, 55 de nouveau en 2009,
   51 au survivant d'un décès d'avant 2009 ; la majoration de 11,1 % en
   2010 ; le minimum, écarté en juillet 2012 pour la réversion d'une pension
   sous le minimum contributif, et écrit en 2026. Lues dans l'index LEGI et
   dans cinq circulaires de la Cnav (n° 120/82, 3/95, 2005/17, 2009/11,
   2010/15), toutes dans sa base législative.
2. **`reversion_fonction_publique`**, en quatre versions : 50 % de la
   pension obtenue ou qu'il aurait pu obtenir au jour du décès, sans âge ni
   ressources, sous la condition d'antériorité du mariage de L. 39, perdue
   au remariage ; la veuve avant 2004, les conjoints depuis ; le plancher
   porté au montant de l'ASPA pour les réversions liquidées depuis 2025
   (loi de finances pour 2026, article 205). La CNRACL y est, son décret
   reprenant L. 38 et L. 39 mot pour mot.
3. **`reversion_agirc_arrco`**, en cinq versions par date du décès : 60 %
   des points, à cinquante-cinq ans depuis 2019, et les âges de l'Arrco et
   de l'Agirc avant. Ses versions sont supposées : l'accord de 2017 n'a pas
   pu être relu sur Légifrance, qui répond par une vérification du
   navigateur, et elles suivent la page que la fédération publie.

Le vocabulaire des dates dit impossible une réversion prenant effet avant le
décès qui l'ouvre ; l'inventaire des avantages rattache la réversion à ses
trois fiches, la pension d'orphelin à celle de la fonction publique. Restent
de ce domaine : le conjoint dans la chronologie et la liquidation du
survivant, dans les deux moteurs ; le bloc du formulaire ; les exemples
publiés ; la page Coût ; la décision de la proposition, puis la référence de
conservation à refiger.

**Deuxième étape : le conjoint dans la chronologie, la réversion liquidée
pour le survivant**, le même jour. La saisie déclare, à qui veut les dire, la
naissance du conjoint, son sexe, la date du mariage, ses ressources annuelles
et le décès de l'assuré (`conjoint`, `conjoint_sexe`, `mariage`,
`ressources_conjoint`, `deces`), et la chronologie les porte (C.1) : la
naissance du conjoint, un lien d'union de forme mariage que le décès clôt, ses
ressources. Quatre présomptions posent ou appliquent ce qu'elle ne dit pas :
le mariage aux vingt-sept ans de l'assuré, un conjoint de l'autre sexe, un
survivant sans autres ressources que ses réversions, une réversion demandée
dans l'année du décès. L'échéancier inscrit le décès, mène la pension du
défunt à l'année du décès par « faire vivre » — l'année courante pour un décès
à venir, jamais avant le départ —, puis liquide la réversion, régime par
régime (`droit/reversion.py` et son jumeau) : au régime général, le taux,
l'âge qui reporte la date d'effet au mois qui suit l'anniversaire — sans
l'exception de qui est né un 1er, que R. 353-7 ne fait pas —, la durée du
mariage d'avant juillet 2004 et le plafond de ressources, où la réversion de
la fonction publique compte et celle des complémentaires non (R. 353-1 et
R. 353-7, relus au texte ce jour-là) ; dans la
fonction publique, la moitié, sous la condition de L. 39 ; à l'Agirc-Arrco,
60 %, à l'âge que la date du décès choisit. L'UNIRS, les régimes
professionnels intégrés et les assurances sociales suivent la fiche du régime
qui les a absorbés ; les autres régimes le disent, sans montant. La saisie
refuse un décès antérieur au départ.

Aucun témoin de simulation ne bouge : la sortie n'a de clé `reversion` que
déclarée. Cinq témoins la rejouent dans les deux moteurs — des ressources
déclarées qui écrêtent, un fonctionnaire, un âge différé, un mariage de neuf
mois en 1995, un décès à venir —, `tests/test_reversion.py` tient les bornes
et les conditions, et la parité des chronologies compte six saisies de plus.
Les trois fiches passent « approchées », chacune avec ses approximations : ni
le minimum ni les majorations, le survivant seul, sans partage ni remariage,
les montants de l'année du décès, le coefficient d'anticipation compris dans
les 60 % de l'Agirc-Arrco. La page Coût ne dit plus que le modèle ne
produira jamais la réversion. Restent de ce domaine : le bloc du formulaire
et ce que la page de résultat montre de la réversion, deux choix à soumettre
au propriétaire ; les exemples publiés ; la page Coût ; la décision de la
proposition, puis la référence de conservation à refiger.

**Troisième étape : les exemples publiés**, le même jour. Neuf exemples
entrent au témoin des exemples officiels, et `tests/test_oracle.py` les
rejoue : la carrière d'un exemple y déclare le conjoint et le décès comme la
saisie, et deux grandeurs s'ajoutent, la date d'effet de la réversion régime
par régime, et la réversion écrêtée, en euros par mois. La page « La pension
de réversion » de la fédération Agirc-Arrco date la réversion de dix
survivants : Leïla, Kim, Annie et Eric concordent ; François, David et
Simone, dont le défunt était payé par trimestre ou par an, et Claude, devenu
invalide, entrent en écart connu, et la fiche de l'Agirc-Arrco déclare le
paiement au mois parmi ses approximations ; Max, dont l'âge n'est pas dit,
et Léo, qui demande sa réversion dix-huit mois après le décès, n'entrent pas.
La circulaire Cnav n° 2005/17 (§ 31) réduit une réversion de 530 € à
169,06 € pour un survivant qui gagne 1 150 € par mois : le modèle rend
169,07 €, la circulaire tronquant le plafond au centime. Service-public
(F13104, vérifiée le 1er janvier 2026) donne le plafond de 2026, 25 001,60 €
pour une personne seule, que le modèle rend exactement ; ni ses fiches du
régime général et de la fonction publique ni la foire aux questions de
l'Assurance retraite ne publient d'autre exemple chiffré. Restent de ce
domaine : le bloc du formulaire et ce que la page de résultat montre de la
réversion, à soumettre au propriétaire ; la page Coût ; la décision de la
proposition, puis la référence de conservation à refiger.

**Quatrième étape : le bloc du formulaire et la page**, le même jour, sur la
décision du propriétaire : l'hypothèse de décès, écrite dans cette session. Le
formulaire demande, dans un bloc replié « Conjoint et réversion », sa
naissance, son sexe, la date du mariage et ses ressources ; personne n'y
déclare la date de sa mort. Le budget de mots du formulaire vierge monte de
trois, ceux du titre du dépliant, un contrôle, comme le test l'exige. Sans décès déclaré, l'échéancier
liquide une réversion d'essai, hors du journal, pour un décès supposé juste
après le départ, ou au 1er janvier de l'année courante pour qui est déjà parti
(présomption `deces_apres_le_depart`) : la réversion porte alors sur la
pension même que la page affiche, dans ses euros. La page de résultat montre,
sous le salaire net, ce que le conjoint recevrait du système actuel, régime
par régime, et qu'aucun des trois autres systèmes n'en verse. Deux témoins de
simulation et un témoin de page la rejouent ; les autres ne bougent pas.

**Le domaine se clôt le même jour**, le gabarit du § 11 rempli :
- **les fiches** : trois, découpées en versions — le régime général et les
  régimes alignés, la fonction publique et la CNRACL, l'Agirc-Arrco —,
  `approchee` chacune, avec ses approximations ;
- **les faits de la chronologie** : la naissance du conjoint, l'union de
  forme mariage, le décès, les ressources ; cinq présomptions ;
- **les fonctions dans l'étape** : `droit/reversion.py` et son jumeau, que
  l'échéancier appelle au décès ;
- **les exemples publiés** : neuf, dont quatre en écart connu ;
- **le bloc du formulaire** : « Conjoint et réversion », et la section de la
  page ;
- **la page Coût** ne bouge pas : sa réversion est lue dans l'enquête de la
  DREES, et aucun de ses chiffres n'a changé dans les commits du domaine ;
- **la décision de la proposition** est déjà prise : « ni réversion »
  (README) ; la couche `comptes_notionnels` neutralise l'étape
  `liquider_chaque_regime`, où s'appliquent les trois fiches, et la page le
  dit ;
- **la référence de conservation** est refigée
  (`python scripts/conservation.py --figer`).

Restent, hors du domaine clos, et consignés dans ses fiches : le minimum de
réversion et ses majorations ; le complément de la fonction publique ; le
partage entre ex-conjoints et le remariage ; la réversion d'un assuré mort
avant son départ ; la réversion minorée de l'Agirc et la périodicité du
paiement ; l'accord Agirc-Arrco de 2017, à relire sur Légifrance ; les régimes
spéciaux, les indépendants et les libéraux. Le domaine suivant se mesurera à
son ouverture : l'invalidité et l'inaptitude paraissent devoir venir ensuite.

**Le troisième domaine, les départs multiples et la vie après le départ,
ouvert le 29 septembre 2026** (§ 11), à la demande du propriétaire, qui le
fait passer devant l'invalidité : « Je souhaite qu'on puisse traiter tous les
cas où cela peut se produire. Il faut que l'on colle le plus possible à la
réalité. » Le modèle liquidait tout à une date, à l'âge du régime le plus
précoce. Mesuré sur deux carrières avant tout changement :
- une aide-soignante née en 1965, dix ans dans le privé puis vingt-sept à
  l'hôpital, partie à cinquante-sept ans, recevait dès cet âge sa pension de
  la CNRACL (14 254 € par an), mais aussi 2 001 € de régime général au taux
  de 37,5 %, que le droit ne lui sert qu'à soixante-deux ans et neuf mois, et
  460 € d'Arrco au coefficient de 0,43 ;
- un militaire né en 1965, dix-sept ans de services puis le privé jusqu'à
  soixante-quatre ans, voyait sa pension militaire (10 795 € par an) commencer
  avec les autres, à soixante-quatre ans, quand le droit la lui sert dès sa
  sortie de l'armée, à trente-cinq ans.

Le domaine couvre tout ce qui fait qu'on ne touche pas toutes ses pensions au
départ, ou qu'on en touche après lui. Son gabarit (§ 11), en cinq étapes :
1. les fiches, lues ce jour (ci-dessous) ;
2. **un départ par régime** : chaque régime liquide à sa date, présumée
   quand la saisie ne la dit pas ; le RAFP à l'âge légal ; le minimum
   contributif écrêté sur les pensions déjà servies, puis révisé ; les deux
   moteurs, les témoins, et la page, qui dit quand chaque pension commence ;
3. **la retraite progressive** : la quotité, la fraction provisoire, la
   pension complète ;
4. **la vie après le départ** : le cumul emploi-retraite, l'extinction des
   droits après une première pension, la seconde pension ;
5. le bloc du formulaire, les exemples publiés, la page Coût, la décision de
   la proposition, la référence de conservation refigée.

Les carrières hors de France, où chaque pays paie à son âge, restent un
domaine à part : le modèle n'a pas encore de période à l'étranger.

**Première étape, le 29 septembre : les textes lus, cinq fiches nouvelles,
deux complétées.** Lus dans
les index LEGI et JORF du jour (journal de veille) : les articles 19 de la loi
n° 2014-40 et 26 de la loi n° 2023-270, en entier ; L. 161-22 à L. 161-22-1-9
dans leurs rédactions de 2014, 2023, 2025 et 2027 ; la retraite progressive
depuis 1988 ; l'âge du RAFP ; l'anticipation de l'Ircantec ; la condition et
l'écrêtement du minimum contributif. Ce qu'ils disent est rangé en fiches :
- `liquidation_regime_par_regime`, `manquante` : chaque régime sert sa
  pension à sa date, hors les régimes que la loi réunit ; elle lit une
  présomption nouvelle, `depart_de_chaque_regime` — chaque pension au départ
  déclaré, celle d'un régime qui n'ouvre pas encore à son ouverture, celle
  d'un régime quitté plus tôt dès qu'il s'ouvre quand la demander ne ferme
  aucun droit (la pension militaire, toute première pension d'avant 2015) ;
- `rafp_age_d_ouverture`, `manquante` : soixante ans jusqu'au 3 juin 2011,
  l'âge légal depuis, et l'admission à la retraite ;
- `droits_apres_la_premiere_pension`, `pas_encore_modelisee` : aucune règle
  générale avant 2015, L. 161-22-1 A pour les premières pensions de 2015,
  L. 161-22-1 pour tous depuis le 1er janvier 2023, les règles de 2027 ; la
  pension militaire, la retraite progressive et le cumul intégral exceptés ;
- `retraite_progressive` et `seconde_pension`, `pas_encore_modelisee`, nées
  de `cumul_emploi_retraite_et_retraite_progressive`, qui ne garde que le
  cumul et ses deux rédactions lues ;
- `minimum_contributif`, complétée de L. 351-10-1, R. 173-7 et R. 173-8.

Le cliquet des rédactions sans statut descend de 10 335 à 10 302 : les
fiches en citent trente-trois de plus. Aucun résultat ne bouge à cette étape.

**Deuxième étape, le 29 septembre : un départ par régime.** Les deux moteurs
datent chaque départ (`droit/departs.py`, et son jumeau) : une unité par
régime de base ou intégré, ou par groupe que la loi fait liquider ensemble ;
chaque complémentaire suit l'unité dont elle partage les années ; le RAFP
attend l'âge légal, et ne fait pas de départ de plus pour qui n'a pas de
primes. Chaque départ est liquidé sur la carrière arrêtée à sa date, pour ses
seuls régimes, en voyant servies les pensions des précédents, menées au mois
de sa date d'effet : le minimum contributif s'écrête sur elles (R. 173-7).
L'échéancier inscrit un départ par date, le déclaré comme un acte, les autres
comme induits ; « faire vivre » part de la date de chaque pension, et ne sert
pas celle qui n'a pas commencé. Les montants du scénario 1 restent ceux du
départ déclaré, la pension déjà servie y étant menée par sa revalorisation,
celle qui commence après ramenée par les prix ; la page dit quand chaque
pension commence, et le résumé, quand la retraite est complète.

La présomption est plus étroite que celle que la première étape écrivait :
seule la pension militaire est demandée avant le départ. Demander une autre
pension plus tôt figerait son taux sur la durée acquise, perdrait la surcote
de l'activité poursuivie, et L. 161-22 exigeait jusqu'en 2003 de cesser toute
activité non salariée ; le premier essai, qui faisait demander à soixante ans
le régime général d'un salarié devenu artisan, a fait tomber le test des
régimes alignés.

Sur les deux carrières mesurées à l'ouverture : l'aide-soignante garde sa
pension de la CNRACL à cinquante-sept ans (14 253,51 €), et son régime général
et son Arrco ne commencent plus qu'au 1er novembre 2027, à soixante-deux ans
et neuf mois : 3 365,26 € de 2027, soit 3 010,21 € de 2022, au lieu de
2 461,72 € décotés dès son départ. Le militaire touche sa pension dès le
1er janvier 2000, 5 878,18 € à cette date, 8 416,70 € au départ déclaré ;
l'ancien calcul lui en donnait 10 795,09 €, dont 2 378,39 € de minimum garanti,
que le modèle ne sert pas aux pensions liquidées avant 2004 : le régime de
l'État ne le déclare qu'à partir de cette année-là, quand son barème et le
texte de 1975 sont dans le dépôt. C'est l'objet du commit suivant.

Le nombre déclaré d'appels de `liquider` vaut désormais par départ (§ 7.8) :
un témoin nouveau, la même aide-soignante mère de trois enfants, en fait
douze, six par départ. Cinq témoins ont plusieurs départs, et le test des
deux moteurs compare leurs journaux, liquidation par liquidation. Les fiches
`liquidation_regime_par_regime` et `rafp_age_d_ouverture` passent à
`approchee` et `transcrite`. Restent ouverts : la date de chaque pension,
déclarée (cinquième étape) ; la révision du minimum contributif quand une
pension commence après lui (R. 173-8) ; l'anticipation d'une complémentaire
seule ; la demande tardive pour une surcote.

**Le minimum garanti d'avant 2004, le même jour.** Les régimes de l'État, de
la CNRACL et des ouvriers de l'État ne le déclaraient qu'à partir de 2004 ;
L. 17 du code des pensions dans sa rédaction de 1975 (LEGIARTI000006362711),
l'article 17 du décret n° 65-773 et l'article 10 du décret n° 65-836, lus
dans l'index LEGI, le servaient avant : 4 % de la référence par année de
services, la totalité à vingt-cinq ans, le barème que le dépôt date de 1976.
Leurs périodes le déclarent désormais depuis le code de 1964 et les décrets de
1965. Le militaire mesuré ci-dessus retrouve son plancher : 7 483,08 € au
1er janvier 2000, 10 714,69 € au départ déclaré (l'ancien calcul, fait aux
règles de 2029, en donnait 10 795,09 €). Aucun témoin de simulation ne bouge ;
la page Coût, si : le minimum garanti chiffré en 2024 passe de 0,29 à
1,39 Md €, les avantages de 96,5 à 97,6 Md €, et les autres systèmes, dont le
coût est la dépense observée au prorata de leurs pensions sur celles du
scénario 1, perdent un milliard certaines années. La référence d'avant 2004
reste celle de l'indice majoré 216, que la loi de 2003 donne au droit
antérieur ; la correspondance de l'indice brut 100 des années plus anciennes
n'est pas lue.

**Troisième étape, le 29 septembre : la retraite progressive.** Une demande —
sa date, la quotité du temps partiel gardé jusqu'au départ — entre à la
chronologie comme un acte de la personne ; la saisie la lit dans l'adresse
(`progressive`, `quotite`), le formulaire ne la demandant qu'à la cinquième
étape. Les deux moteurs l'examinent à sa date (`droit/progressive.py`, et son
jumeau) : l'âge, la durée d'assurance, la quotité, et le régime où l'assuré
travaille cette année-là. Ouverte, elle liquide à titre provisoire les régimes
que nomme L. 351-15, puis, depuis 2023, tous les régimes de base, avec les
complémentaires qui les suivent, et sert sa fraction jusqu'au départ ; au
départ, la pension complète se liquide sur la carrière entière, bornée par la
provisoire revalorisée hors de la fonction publique, et elle était la
provisoire avant le 8 juin 2006. Les lignes de carrière portent désormais
leur quotité : le revenu en est réduit, les services de la fonction publique
la comptent, et le traitement de référence se lit à temps plein.
L'échéancier inscrit la demande, la liquidation provisoire et une composante
par pension servie en fraction, que la pension complète remplace ; la page
dit la fraction servie, ou pourquoi la demande est fermée.

Relire les textes, avant d'écrire la fiche, a corrigé le moteur de l'étape
même sur trois points : les libéraux et les avocats ne demandent la
retraite progressive que depuis le 1er septembre 2023, avec les clercs de
notaire, l'Opéra et les mines (décrets n° 2023-751 et 2023-753), le décret de
L. 643-8-1 n'ayant jamais paru — le moteur les ouvrait en 2014 ; la pension de
libéral d'un salarié se liquide pourtant avec la sienne depuis 1988, L. 351-15
nommant les professions libérales ; et la pension complète du fonctionnaire
n'a pas de plancher (D. 37-3, et les décrets de la CNRACL et des ouvriers de
l'État). La quotité s'arrondit à l'unité, la moitié comptée pour un. La
décote de la pension provisoire, bornée à 25 % de 2014 à 2023 (R. 351-41), n'a
pas de code : les vingt trimestres de chaque régime la tiennent déjà, et un
test le vérifie.

Une salariée née en 1965, entrée à vingt ans au salaire moyen, à 60 % depuis
novembre 2025, touche 40 % de sa pension provisoire, 9 522,70 € par an en
euros de 2025 ; à son départ à soixante-quatre ans, sa pension complète est de
31 114,77 €, contre 32 221,46 € à temps plein. Six témoins de simulation (`progressive_*`)
et deux de pages, deux affirmations ; les cas de retraite progressive font de
trois à six appels de `liquider`, sous le nombre déclaré. La fiche
`retraite_progressive` passe à `approchee`, en sept versions datées, et le
cliquet des rédactions sans statut descend de 10 298 à 10 276. Restent ouverts : les changements
de quotité et la suspension, la baisse de revenus d'un non-salarié, les règles
propres de l'Agirc-Arrco et de l'Ircantec, les décrets des régimes spéciaux,
un exemple publié ; le formulaire, à la cinquième étape.

**Quatrième étape, le 30 septembre : la vie après le départ, première partie.**
Les textes du cumul emploi-retraite sont lus (journal de veille) : L. 161-22
depuis 1985, ses décrets, les règles des indépendants, des libéraux et des
fonctionnaires, la page de l'Agirc-Arrco et deux fiches de service-public. La
fiche `cumul_emploi_retraite_et_retraite_progressive` est découpée en six
versions — la rupture avec l'employeur de 1983, le plafond du dernier salaire
de 2004, le cumul libéralisé de 2009, la réduction du dépassement de 2015, les
trois régimes selon l'âge de 2027, dont le seuil n'a pas paru —, et une fiche
nouvelle, `cumul_emploi_retraite_fonction_publique`, porte le tiers de la
pension du fonctionnaire. L'activité exercée après le départ se déclare par
l'adresse (`emploi_retraite`, `emploi_retraite_fin`, son statut, son revenu,
l'employeur), dans les deux moteurs : la chronologie la date comme une période
d'activité postérieure au départ, et la carrière en garde les années à part,
que la première liquidation ne voit pas. Aucun résultat ne bouge. Restent, dans
l'ordre : la pension servie pendant l'activité — suspendue, réduite du
dépassement, entière au taux plein —, puis les droits que l'activité ouvre ou
non et la seconde pension.

**Quatrième étape, deuxième partie, le même jour : la pension servie pendant
l'activité.** `droit/cumul.py` et son jumeau disent, mois par mois de
l'activité après le départ, ce que chaque pension en garde, selon le droit du
mois, la date de la pension et celle de la première pension de base : le
salarié (L. 161-22 et ses décrets), l'artisan, le commerçant et le libéral
(L. 634-6, L. 643-6), le fonctionnaire (L. 84 à L. 86 du code des pensions),
l'Agirc-Arrco, et la première pension de 2027. Les décrets, relus dans leurs
rédactions de 2004 à 2017, recoupent la fiche : la première pension de 2015
reste suspendue jusqu'au décret de la réduction, qui ne vaut que pour les
activités exercées depuis le 1er avril 2017 (version nouvelle
`premieres_pensions_de_2015`), et celle d'avant 2015 garde la suspension. Chaque
régime ne réduit que ses pensions, pour l'activité qui relève de lui ; la
pension des régimes alignés, que le modèle liquide au régime général, suit
aussi la règle des artisans pour l'ancien artisan qui le redevient. Au-delà de
l'année courante, les pensions et le dernier salaire suivent les prix.
L'échéancier inscrit la pension réduite, suspendue ou non due pour les seuls
mois où elle l'est ; le résultat du départ porte le cumul, et la page dit,
période par période, ce que la pension devient et ce que l'activité fait
perdre en tout. Huit témoins de simulation et deux de page ; quatre exemples
publiés, des fiches F12402 et F13243, reproduits ; les deux fiches du cumul
passent à `approchee`. Restent : les droits que l'activité ouvre ou non et la
seconde pension, puis la cinquième étape.

**Quatrième étape, troisième partie, le même jour : les droits de l'activité
après le départ.** `droit/seconde.py` et son jumeau disent, mois par mois, ce
que l'activité ouvre : rien depuis la première pension de 2015 (L. 161-22-1 A),
ni, pour tous, depuis 2023 (L. 161-22-1), hors du cumul intégral ; jamais après
un retour chez le dernier employeur dans les six mois ; des droits dans les
régimes qui n'ont pas liquidé avant 2023 pour une première pension d'avant 2015,
et toujours pour une pension militaire — que le modèle nomme sans les calculer.
En cumul intégral depuis 2023, la nouvelle pension se calcule au régime général
et aux salariés agricoles — le salaire mensuel moyen des années qui valident un
trimestre (R. 351-29, III), au taux plein, proratisé par la durée requise,
plafonné à 5 % du plafond de la sécurité sociale —, et la seconde retraite de
l'Agirc-Arrco sur les points de la tranche 1 ; pour une première pension de 2027,
en cumul entier seulement, à l'âge du taux plein automatique, et sans plafond,
la rédaction de 2026 n'en portant plus. Elle s'inscrit à sa date d'effet dans
une lignée à elle ; la page la dit sous le cumul. Le cumul de la première
pension de 2027 n'est plus entier qu'à cet âge, l'Agirc-Arrco compris : le
témoin de la carrière longue de 2028 le montre. Cinq témoins de simulation et un
de page ; l'exemple du plafond de 2 403 € de la fiche F13243, reproduit ; les
fiches `droits_apres_la_premiere_pension` et `seconde_pension` passent à
`approchee`. Restent : les droits ouverts dans les régimes qui n'ont pas liquidé
(première pension d'avant 2015, pension militaire), puis la cinquième étape.

**Quatrième étape, fin, le même jour : les régimes que l'activité ouvre.** Les
droits que l'activité après le départ ouvre dans un régime qui ne servait pas
de pension — avant 2023 pour une première pension d'avant 2015, toujours pour
une pension militaire — se liquident comme un départ induit : à la fin de
l'activité, ou à l'âge d'ouverture du régime, sur la carrière prolongée des
seules années qui les ouvrent, dont la durée tous régimes fait le taux. La
fonctionnaire partie en 2011, salariée jusqu'en 2016, reçoit alors une pension
du régime général et une retraite de l'Arrco ; le militaire parti à quarante-cinq
ans, salarié ensuite, les siennes à l'âge légal. Le nombre d'appels de
`liquider` d'un témoin vaut désormais par départ, ceux-ci compris. Reste dehors
l'activité exercée avant qu'un régime du départ ne liquide, à son âge
d'ouverture, qu'il ne compte pas. L'étape est close ; reste la cinquième : le
formulaire, la page Coût, la décision de la proposition, et la clôture du
domaine.

**Cinquième étape, première partie, le même jour : le formulaire.** Un
dépliant replié, « Retraite progressive et cumul emploi-retraite », demande ce
que seule l'adresse portait : la date et la quotité d'une retraite progressive,
et l'activité exercée après le départ — sa date, sa fin, son statut, son
revenu, l'employeur. Il s'ouvre quand l'une ou l'autre est dite. Son statut ne
propose pas les périodes sans emploi, que la saisie refuse, et le revenu
laissé vide y est celui du dernier métier. Le budget de mots du formulaire
vierge monte de quatre, pour le titre du dépliant. Une quotité nulle se refuse
désormais, au lieu de valoir absence : le formulaire en fait sa borne, et la
saisie l'oppose hors du navigateur, comme toute borne. Aucun témoin de
simulation ne bouge ; les pages du simulateur gagnent le dépliant. Restent : la
date de chaque pension, déclarée, que la deuxième étape et la fiche
`liquidation_regime_par_regime` renvoyaient ici ; la décision de la
proposition ; la clôture.

**Cinquième étape, deuxième partie, le même jour : la date de chaque pension,
dite.** L'assuré dit désormais, régime par régime, la date où il demande sa
pension : au formulaire, un champ par régime de base quand la carrière en
compte plusieurs, dans le dépliant, devenu « Retraite progressive, dates des
pensions, cumul emploi-retraite » ; ou par l'adresse
(`demande_regime_general=2027-06`). La chronologie la porte en acte de la
personne, un par régime, et les deux moteurs la lisent (`departs_et_demandes`,
et son jumeau) : une date plus tardive que la présumée la remplace, une unité
prenant la plus tardive des dates de ses régimes, et une complémentaire
demandée après son régime de base se liquide à sa date. Une date plus précoce
n'avance rien : demander une pension avant son départ ferait de la fin de la
carrière une activité exercée après une première pension, que le modèle
représente déjà en déclarant le départ à cette date et l'activité qui suit. La
page dit, pour chaque date qu'elle ne retient pas, pourquoi : le départ,
l'ouverture du régime, la sortie de l'armée, la pension que la loi lui
attache, ou l'absence de droit dans ce régime. Un seul départ qui n'est pas le
déclaré — toutes les pensions demandées plus tard, ou la seule pension
militaire — se liquide maintenant à sa date, et le RAFP servi à l'âge légal
avant le départ déclaré n'est plus daté « dès la sortie de l'armée ». La
fonctionnaire née en 1960, treize ans dans le privé avant l'État, partie en
juin 2022 sans la durée du taux plein, qui demande son régime général à
soixante-sept ans, le touche sans décote : 4 662,60 € en 2027, soit 4 170,68 €
de 2022, au lieu de 3 023,61 € décotés dès son départ. Aucun témoin de
simulation ne bouge ; cinq naissent (`demande_*`), et une page ; le budget de
mots du formulaire vierge monte de deux, le titre du dépliant. Les systèmes 2
à 6 liquident leur compte au départ déclaré : la proposition n'a pas dit
davantage. Restent : sa décision, et la clôture du domaine.

**Le domaine se clôt le même jour**, pour tout ce que le dépôt peut faire
seul, le gabarit du § 11 rempli :
- **les fiches** : sept, découpées en versions —
  `liquidation_regime_par_regime`, `retraite_progressive`, les deux du cumul
  emploi-retraite, `droits_apres_la_premiere_pension` et `seconde_pension`,
  `approchee` chacune avec ses approximations ; `rafp_age_d_ouverture`,
  `transcrite` —, et `minimum_contributif`, complétée ;
- **les faits de la chronologie** : la demande de retraite progressive et sa
  quotité, la date demandée de chaque pension, deux actes de la personne ;
  l'activité exercée après le départ, une période d'activité qui porte
  `apres_depart` et l'employeur ; une présomption,
  `depart_de_chaque_regime` ;
- **les fonctions dans l'étape** : `droit/departs.py`, `droit/progressive.py`,
  `droit/cumul.py` et `droit/seconde.py`, et leurs jumeaux, que l'échéancier
  appelle à la retraite progressive, à chaque départ et après le départ ;
- **les exemples publiés** : cinq, des fiches F12402 et F13243 de
  service-public, tous reproduits ; aucun encore pour la retraite progressive
  ni pour un polypensionné qui liquide à deux dates, que les fiches disent à
  chercher ;
- **le bloc du formulaire** : « Retraite progressive, dates des pensions,
  cumul emploi-retraite », replié tant qu'il est vide, et les notes de la page
  — quand chaque pension commence, la fraction servie, le cumul période par
  période, les droits de l'activité, les dates non retenues ;
- **la page Coût** : aucun commit du domaine ne l'a déplacée, hors le minimum
  garanti d'avant 2004, corrigé en chemin (en 2024, de 0,29 à 1,39 Md €) ; la
  retraite progressive, le cumul et la seconde pension n'y ont pas de ligne :
  la dépense du système 1 est celle qu'on observe, où ce qu'ils servent est
  déjà compté, et les autres systèmes s'en déduisent au prorata des pensions
  entières ;
- **la décision de la proposition** reste à prendre, par le propriétaire : le
  README ne dit rien de la retraite progressive, du cumul emploi-retraite, de
  la seconde pension ni de la date de chaque pension. En attendant, les
  systèmes 2 à 6 liquident leur compte au départ déclaré, entier, sans
  fraction ni cumul, le temps partiel d'une retraite progressive n'y réduisant
  que la cotisation ; `docs/limites.md` et le README le disent ;
- **la référence de conservation** est refigée
  (`python scripts/conservation.py --figer`).

Restent, hors du domaine clos, et consignés dans ses fiches : la révision du
minimum contributif quand une pension commence après lui (R. 173-8) ;
l'anticipation d'une complémentaire seule ; une pension demandée avant le
départ sans redéclarer le départ ; plusieurs activités après le départ, et
celle qu'exerce l'assuré avant qu'un régime du départ ne liquide ; la nouvelle
pension des régimes autres que le régime général, les salariés agricoles et
l'Agirc-Arrco ; le cumul des avocats, des exploitants agricoles, de
l'outre-mer, des élus et des complémentaires autres que l'Agirc-Arrco ; les
changements de quotité et la suspension de la retraite progressive, la baisse
de revenus qui fait la fraction d'un non-salarié, les décrets des régimes
spéciaux ; le seuil de 2027, que son décret n'a pas fixé ; les exemples
publiés à chercher. Le domaine suivant se mesurera à son ouverture :
l'invalidité et l'inaptitude, que le propriétaire avait fait passer après
celui-ci, viennent en tête.

**Le quatrième domaine, l'invalidité et l'inaptitude, ouvert le 30 septembre
2026** (§ 11), à la demande du propriétaire : « Je veux qu'on traite
l'invalidité et l'inaptitude. » Il n'a pas été remesuré : la mesure du
28 septembre le plaçait déjà en tête des domaines restants — 2,26 millions de
retraités partis au taux plein à ce titre fin 2016, 0,90 pour invalidité et
1,36 pour inaptitude (DREES, EIR 2016), 19 % des nouveaux retraités du
régime général en 2024 (COR). Le modèle compte les années d'invalidité en
trimestres assimilés et en points gratuits, et rien d'autre : l'invalide et
l'inapte y sont décotés faute de durée, l'inapte de la génération 1968 ne
peut partir à soixante-deux ans, et le fonctionnaire radié pour invalidité
part à l'âge légal. Son gabarit (§ 11), en cinq étapes :
1. les fiches, lues ce jour (ci-dessous) ;
2. les faits de la chronologie : la pension d'invalidité et le régime qui la
   sert, l'inaptitude reconnue ou présumée, la radiation pour invalidité du
   fonctionnaire, son taux et son imputabilité ; la saisie qui les lit ;
3. les fonctions dans l'étape, dans les deux moteurs : le départ induit à
   l'âge de la substitution, le taux plein de l'inapte et de l'ex-invalide, le
   départ du fonctionnaire à sa radiation, sans décote, au minimum garanti de
   l'invalidité, au plancher de L. 30 et avec sa rente ; le plancher de
   l'AVTS ; l'ASPA à soixante-deux ans ; les témoins, et la page ;
4. les exemples publiés ;
5. le bloc du formulaire, la page Coût, la décision de la proposition, la
   référence de conservation refigée.

**Première étape, le 30 septembre : les textes lus, trois fiches nouvelles.**
Lus dans les index LEGI et JORF du jour et dans la base de la Cnav (journal
de veille) : la pension d'invalidité et sa substitution (L. 341-15 à
L. 341-17, R. 341-22, D. 341-1, l'article 62 de l'ordonnance de 1945, les
circulaires n° 2018-18 et 2023-25), l'inaptitude (L. 351-7, L. 351-8,
R. 351-21, L. 351-1-5, D. 351-1-14, R. 815-1, L. 821-1, les articles 63 à 65
de l'ordonnance de 1945, l'article 70-1 du décret de 1945, les circulaires
n° 2023-22 et 2024-26), la retraite pour invalidité des fonctionnaires
(L. 4, L. 14, L. 17, L. 24, L. 27 à L. 30 ter du code des pensions, le décret
de la CNRACL et celui des ouvriers de l'État). Ce qu'ils disent est rangé en
fiches, `pas_encore_modelisee` toutes trois :
- `pension_d_invalidite_substituee`, en six versions : la substitution à
  soixante ans et le plancher de la pension d'invalidité depuis 1945 ; le
  plancher de l'AVTS pour les invalidités nées depuis le 31 mai 1983 ;
  l'invalide qui travaille, qui garde sa pension d'invalidité jusqu'à sa
  demande depuis mars 2010 ; l'âge légal en 2011 ; le demandeur d'emploi, six
  mois de plus, en 2017 ; soixante-deux ans en 2023 ;
- `inaptitude_au_travail`, en cinq : le taux de soixante-cinq ans dès
  soixante ans en 1945, puis sous la loi Boulin ; le taux plein sans durée en
  1983 ; l'âge légal en 2011 ; soixante-deux ans en 2023, et l'ASPA au même
  âge ; les réputés inaptes, dont les bénéficiaires de l'AAH ;
- `retraite_pour_invalidite_fonction_publique`, en quatre : la jouissance
  immédiate sans durée de services, le plancher de L. 30 et la rente de
  L. 28, puis l'exemption de décote en 2004 et le minimum garanti de
  l'invalidité en 2011.

La fiche `inaptitude_invalidite_penibilite_amiante`, qui les portait sans
versions, garde son identifiant et les départs anticipés particuliers :
l'incapacité permanente, le compte professionnel de prévention, l'amiante.
Elle citait « L. 351-8 1° bis » pour l'inaptitude, et un contrôle de la veille
du 20 septembre disait qu'« L. 351-7 [...] N'EXISTE PAS » au code de la
sécurité sociale : les deux étaient faux, la requête rendant d'abord les
articles homonymes du code de la construction. L'inventaire des avantages
cite désormais L. 351-7, L. 351-8, 2°, L. 341-15 et L. 29 du code des
pensions, et renvoie aux trois fiches. Aucun résultat ne bouge.

**Deuxième étape, le 30 septembre : les faits, et la saisie qui les lit.**
L'adresse du simulateur porte cinq champs nouveaux : `invalidite`, le mois où
la pension d'invalidité a commencé ; `inaptitude=oui`, l'inaptitude reconnue
au départ ; `radiation_invalidite`, le mois de la radiation des cadres d'un
fonctionnaire civil, et `invalidite_imputable=oui` et `taux_invalidite`, qui ne
servent qu'à elle. La chronologie les garde en trois faits, dans les deux
moteurs : deux décisions médicales et une radiation de motif `invalidite`. La
carrière les lit, avec les affiliations de leur année et de l'année d'avant,
où se trouvent le régime qui sert la pension et l'emploi que la radiation
clôt : le modèle rattache l'année d'un changement d'emploi à l'activité qui en
occupe le plus de mois, et le fonctionnaire radié en juin, salarié ensuite, ne
l'est plus que l'année d'avant. Faute de date déclarée, une carrière qui finit
en période d'invalidité présume la pension depuis le 1er janvier de sa
première année (présomption `pension_d_invalidite_de_la_periode`, § 5.6) ;
une invalidité que l'activité suit a pris fin, et ne présume rien. Se
refusent, avec les mêmes mots dans les deux moteurs : une date hors de la
carrière, un taux hors de 1 à 100, l'imputabilité ou le taux sans radiation,
une radiation qui ne clôt aucun emploi de fonctionnaire civil, ou que la
carrière suit dans la fonction publique. Le moteur ne lit pas encore ces
faits : aucun résultat ne bouge. `tests/test_invalidite.py` les tient.

**Troisième étape, le 30 septembre : les fonctions, dans les deux moteurs.**
Les trois fiches du domaine sont lues par le moteur (`droit/invalidite.py` et
son jumeau, table `Invalidites`, portée par le paquet), `approchee` toutes
trois, leurs écarts déclarés.
- L'inapte déclaré et l'ex-invalide — pension d'invalidité déclarée, ou
  présumée d'une carrière qui finit en invalidité — ont le taux plein quelle
  que soit leur durée, au régime général et dans les régimes alignés, à l'âge
  de la version, soixante-deux ans depuis 2023 quand l'âge légal est plus haut
  (motif d'ouverture `inaptitude`) ; le minimum contributif les sert,
  l'Agirc-Arrco et l'Ircantec ne leur appliquent aucun coefficient (l'article
  16 de l'arrêté Ircantec le dit dès 1971) ; l'ASPA s'ouvre au même âge, au
  départ et aux échéances (R. 815-1, relu).
- La pension de vieillesse de l'ex-invalide commence d'office au premier du
  mois qui suit l'âge de la substitution, avant son départ déclaré s'il le
  faut (départ de motif `invalidite`) ; l'invalide qui travaille part à sa
  demande, au plus tard à l'âge du taux plein automatique ; le demandeur
  d'emploi indemnisé, six mois après l'âge au plus tard ; avant mars 2010, la
  présomption `opposition_a_la_substitution` fait s'opposer qui travaille.
- Le fonctionnaire radié des cadres pour invalidité liquide à sa radiation, à
  tout âge et sans condition de durée de services (départ de motif
  `radiation`, ouverture `invalidite`), sans décote, au minimum garanti sans
  condition de taux plein et en quinzièmes sous quinze ans, porté à la moitié
  du traitement à 60 % d'invalidité, avec la rente viagère de L. 28 quand
  l'invalidité est imputable, le tout sous le traitement (L. 30 ter). Le RAFP
  attend l'âge légal, sans exception (décret n° 2004-569, article 6, relu).
- Le plancher de l'allocation aux vieux travailleurs salariés n'est pas écrit :
  l'ASPA de l'ex-invalide, servie au même âge, porte toujours ses ressources
  plus haut, et le montant du scénario 1 n'en changerait pas.
- Chemin faisant, une période « sans activité », qui ne valide rien, ne fait
  plus acquérir le RAFP au fonctionnaire parti avant 2005 : elle lui ajoutait
  un départ vide.

Aucun des 653 témoins d'avant le domaine ne bouge ; quinze témoins de
simulation et deux pages naissent pour lui, rendus à l'identique par les deux
moteurs. L'inventaire des avantages range le taux plein par inaptitude ou
invalidité en « intégré », sa dépense lue dans les comptes de la protection
sociale.

**Quatrième étape, le 1er octobre : les exemples publiés.** Sept exemples
entrent dans `tests/temoins/exemples_officiels.yaml`, et le modèle les rend
tous : l'ex-invalide de la circulaire Cnav n° 2024/25, dont la pension de
vieillesse commence d'office le 1er décembre 2024, à soixante-deux ans, avant
l'âge légal de sa génération, et qui ne cumule entièrement qu'à celui-ci ;
l'inapte de la circulaire n° 2012/27, au taux plein avec 158 trimestres, qui ne
cumule entièrement qu'à soixante-cinq ans et quatre mois ; trois pages du
Service des retraites de l'État, le minimum garanti de l'invalidité en
quinzièmes, le plancher de L. 30 de Monsieur G. et le total de Monsieur H.,
ramené au traitement par L. 30 ter. Deux grandeurs naissent pour eux,
`cumul_integral_depuis` et `pension_et_rente_d_invalidite_sur_traitement`, qui
prête le traitement et le taux que la page donne ; `pensions_annuelles_a_leur_date`,
qu'aucun exemple n'emploie, se retire. La page de Monsieur H. compte le seuil
de la rente sur la rente, et le taux d'invalidité deux fois, quand L. 28 le
compte sur le traitement : seul le total se compare. Ne se rejouent pas ceux de
la circulaire RSI n° 2011/017, d'avant le relèvement de 2011, ni l'ASPA de
l'ex-invalide de la circulaire n° 2012/63, parti pour pénibilité.

L'écart connu que le domaine de la réversion avait laissé à celui-ci est levé :
l'invalidité du conjoint survivant, que la saisie déclare désormais
(`conjoint_invalidite`, dans le bloc du conjoint, dans les deux moteurs), lève
l'âge de la réversion de l'Agirc-Arrco au mois qui suit sa reconnaissance, et
Claude, devenu invalide en février 2024, a la sienne au 1er mars, comme la
fédération l'écrit. Aucun des 668 témoins ne bouge ; un naît,
`reversion_conjoint_invalide`.

**Cinquième étape, le 1er octobre : le formulaire, la page Coût, la
décision.** Le formulaire demande le domaine dans un dépliant « Invalidité et
inaptitude », replié tant qu'il est vide — la pension d'invalidité,
l'inaptitude, la radiation pour invalidité, son imputabilité et son taux —, et
l'invalidité du conjoint dans le bloc du conjoint ; le budget de mots du
formulaire vierge monte de trois, le titre du dépliant. La page Avantages
compte à part le taux plein par inaptitude ou invalidité, que les comptes de la
protection sociale chiffrent ; la page Coût ne bouge pas. Le propriétaire a
décidé que la proposition n'en fait pas exception : le compte de l'inapte, de
l'ex-invalide et du fonctionnaire radié se liquide à soixante-cinq ans dans le
scénario 6, au départ déclaré dans les scénarios 2 à 5, l'assurance
invalidité, hors du système de retraite, les couvrant jusque-là ; le README,
`docs/limites.md` et la fiche `age_legal_de_la_proposition` le disent, et
aucun chiffre n'en bouge : c'est ce que le modèle faisait.

**Le domaine se clôt le même jour**, le gabarit du § 11 rempli :
- **les fiches** : trois, découpées en versions et `approchee` chacune avec ses
  approximations — `pension_d_invalidite_substituee`, `inaptitude_au_travail`,
  `retraite_pour_invalidite_fonction_publique` —, et `reversion_agirc_arrco`,
  complétée de l'invalidité du survivant ;
- **les faits de la chronologie** : deux décisions médicales et une radiation
  de l'assuré, une décision médicale de son conjoint ; deux présomptions,
  `pension_d_invalidite_de_la_periode` et `opposition_a_la_substitution` ;
- **les fonctions dans l'étape** : `droit/invalidite.py` et son jumeau, que
  l'ouverture, la liquidation, les départs, la coordination et la réversion
  appellent ;
- **les exemples publiés** : huit, tous reproduits ;
- **le bloc du formulaire** : « Invalidité et inaptitude », et le champ du
  conjoint ;
- **la page Coût** ne bouge pas : aucun de ses chiffres n'a changé dans les
  commits du domaine, la dépense de l'avantage étant lue dans les comptes ;
- **la décision de la proposition** : « comme tout le monde » ;
- **la référence de conservation** est refigée
  (`python scripts/conservation.py --figer`).

Restent, hors du domaine clos, et consignés dans ses fiches : le plancher de
l'allocation aux vieux travailleurs salariés, sans effet tant que l'ASPA est
servie ; l'inaptitude des régimes que les fiches ne nomment pas (exploitants
agricoles, professions libérales, avocats, régimes spéciaux) ; les réputés
inaptes qui ne se déclarent pas ; le militaire réformé et les pensions de
réforme des régimes spéciaux ; la majoration pour tierce personne et la
revalorisation des pensions d'invalidité de L. 341-6 ; le seuil de la rente de
L. 28, que trois sources écrivent chacune autrement ; les exemples de la CNRACL
et de l'Ircantec ; la pension de veuf ou de veuve invalide de l'assurance
invalidité. Le domaine suivant se mesurera à son ouverture.

**Le cinquième domaine, les carrières hors de France, ouvert le 1er octobre
2026** (§ 11), à la demande du propriétaire : « Je veux qu'on traite les
carrières hors de France. » Il n'a pas été remesuré : la mesure du 28
septembre le plaçait derrière l'invalidité, désormais close — 1,28 million de
retraités résidant à l'étranger fin 2024 (DREES, enquête annuelle auprès des
caisses), un minimum, et 20,3 % des retraités nés à l'étranger fin 2016 (EIR).
Le modèle ne connaît aucune période à l'étranger : une carrière commencée
ailleurs part décotée faute de durée, quand la caisse compte ses périodes
étrangères pour le taux et ne proratise que sur les françaises. Son gabarit
(§ 11), en cinq étapes :
1. les fiches et le tableau des accords, lus ce jour (ci-dessous) ;
2. les faits de la chronologie : les périodes à l'étranger — l'État, le
   début, la fin —, la pension étrangère, liquidation observée (§ 5.5), et la
   résidence après le départ ; la saisie qui les lit ;
3. les fonctions dans l'étape, dans les deux moteurs : les trimestres
   étrangers que chaque accord fait compter, le taux et l'ouverture des droits
   qu'ils changent, la pension proratisée contre la pension nationale, le
   minimum théorique et proratisé, l'écrêtement sur les pensions étrangères,
   l'ASPA refusée hors de France ; les témoins, et la page ;
4. les exemples publiés : les quatre calculs de Léna du CLEISS, et ceux des
   circulaires de la Cnav ;
5. le bloc du formulaire, la page Coût, la décision de la proposition, la
   référence de conservation refigée.

**Première étape, le 1er octobre : les textes lus, quatre fiches nouvelles et
le tableau des accords.** Lus (journal de veille) : les règlements européens
dans leurs versions consolidées, au dépôt de l'Office des publications de
l'Union — 883/2004 (articles 6, 50 à 60, annexes VIII, X et XI), 987/2009
(articles 12, 13, 43), 1408/71, 1248/92, 1606/98, 859/2003, 1231/2010 — et le
protocole de coordination de l'accord avec le Royaume-Uni (article SSC.47) ;
dans l'index LEGI, L. 161-19-1 et R. 161-16-1, R. 351-4, R. 351-5, R. 351-27,
R. 351-38, R. 173-4-3, L. 173-2, R. 173-7, L. 351-10-1, L. 742-2, L. 815-1,
R. 111-2 et R. 115-6 ; dans la base de la Cnav, ses exposés sur les règlements
européens, sur chaque convention et sur les coordinations d'outre-mer, et les
circulaires n° 2010/42 et 2021/33 ; au CLEISS, ses pages sur la retraite après
une carrière à l'étranger et celles des accords. Ce qu'ils disent est rangé en
fiches, `pas_encore_modelisee` toutes quatre :
- `totalisation_des_periodes_etrangeres`, en quatre versions : avant 1983, le
  taux se lit sur l'âge et les périodes étrangères ne le changent pas ; depuis
  le 1er avril 1983, celles qu'un accord fait compter s'ajoutent à la durée qui
  fixe le taux et ouvre les droits, jamais à celle qui proratise, et l'activité
  à l'étranger d'avant 1983 compte, pour le taux seul, comme période reconnue
  équivalente ; depuis 2010, les institutions européennes et les organisations
  internationales, pour le taux seul ; depuis 2011, l'équivalence sous la
  condition de L. 742-2 ;
- `pension_proratisee`, en cinq : la pension nationale au taux de toute la
  carrière jusqu'en juin 1992 ; puis la plus élevée de la pension nationale et
  de la pension proratisée (règlement 1248/92), les fonctionnaires coordonnés
  depuis le 25 octobre 1998 ; le salaire annuel moyen de la pension théorique
  réduit au prorata de 2004 à juin 2022 ; le règlement 883/2004, dont les
  régimes en points ne proratisent pas ;
- `minimum_contributif_international`, en trois : le minimum proratisé comme
  la pension avant 2004 ; depuis, un minimum et une majoration théoriques puis
  proratisés sur la durée totale non limitée, les périodes étrangères comptées
  comme cotisées ; depuis 2012, la subsidiarité et l'écrêtement sur les
  pensions étrangères, hors celles des règlements européens et de six
  conventions ;
- `residence_et_minimum_vieillesse`, en trois : l'ASPA ne se sert qu'en France,
  plus de six mois par an jusqu'en août 2023, plus de neuf mois depuis.

Le tableau `data/reference/legislation/accords_internationaux.yaml` dit, pour
68 États et pour les organisations internationales, l'accord en vigueur à la
date d'effet de la pension : les règlements européens depuis l'entrée de
chacun des 31 États qu'ils lient, et la convention qui les y précédait ; les 37
conventions bilatérales en vigueur, et celles qu'elles ont remplacées ; leur
type de calcul — option, calcul séparé, comparaison, le classement du CLEISS —,
leur prorata quand la Cnav l'écrit, les personnes qu'elles visent. Les collectivités d'outre-mer qui ont leur régime
n'y sont pas : leurs régimes sont déjà des régimes du modèle, et leurs
trimestres comptent déjà dans la durée tous régimes. Quatre réserves sont
déclarées dans les fiches : la règle de la CNRACL et du Service des retraites
de l'État, injoignables d'une session au-delà d'une page ; la circulaire Cnav
n° 2008/58, que la base n'a pas rendue ; les conventions d'avant l'entrée des
États dans l'Union, dont seules les dates sont lues ; le prorata des
conventions à option, que la Cnav n'écrit pas. Aucun résultat ne bouge.

**Deuxième étape, le 1er octobre : les faits, et la saisie qui les lit.**
L'adresse du simulateur porte trois groupes de champs, qui ne servent qu'à
eux : jusqu'à quatre périodes hors de France — `etrangerN_pays`, le code de
l'État au tableau des accords, ou `autre` pour un État qu'aucun accord ne lie
à la France, `etrangerN_debut`, `etrangerN_fin`, et `etrangerN_activite`,
salariée quand la ligne ne la dit pas, puisque 23 des 37 conventions en
vigueur ne coordonnent que les salariés — ; jusqu'à quatre pensions
étrangères — `pension_etrangereN_pays`, `pension_etrangereN`, son montant
brut mensuel en euros d'aujourd'hui, et `pension_etrangereN_debut` — ; et
`residence`, l'État où la personne réside après son départ. Une pension
étrangère est une ligne à part, et non un champ de la période : un État sert
souvent plusieurs pensions, de base et complémentaires, et une pension compte
à l'écrêtement du minimum sans que ses périodes comptent pour le taux. La
chronologie les garde dans les deux moteurs : une période à l'étranger par
période, son État pour `territoire` — le champ du contrat C.1 que rien
n'écrivait encore —, un acte de la caisse de l'État par pension, la
liquidation qu'elle notifie, son montant ramené sur les prix au mois où elle
commence, et une résidence à compter du départ ; la carrière les lit. Une
année que l'étranger occupe pour plus de la moitié de ses mois de carrière y
est une année sans activité, comme celle d'une période sans emploi ; une
période qui précède le premier emploi en France n'en interrompt aucune. Le
paquet du site porte le tableau des accords, sur lequel les deux contextes
contrôlent chaque État. Se refusent, avec les mêmes mots dans les deux
moteurs : une ligne incomplète, une activité ou un État inconnus, la France,
une période avant quatorze ans ou après le départ, deux qui se chevauchent,
une pension sans montant ou qui commence hors de quatorze à soixante-quinze
ans, une résidence dans une organisation internationale. Aucune présomption
nouvelle : celles qui diront la résidence en France et l'absence de pension
étrangère de qui n'en déclare pas entreront avec le calcul qui les lit, à la
troisième étape. Le moteur ne lit pas encore ces faits : aucun témoin ne bouge.

**Troisième étape, le 1er octobre : les fonctions, dans les deux moteurs.**
Les quatre fiches du domaine sont lues par le moteur (`droit/etranger.py` et
son jumeau ; la table `CarrieresHorsDeFrance` et le tableau des accords, portés
par le paquet), `approchee` toutes quatre, leurs écarts déclarés.
- « Coordonner les affiliations » dit à quel titre chaque période compte —
  l'accord en vigueur avec son État à la date d'effet, s'il vise son activité,
  l'organisation internationale depuis 2010, l'activité d'avant 1983 reconnue
  équivalente — et pour quelle famille de régimes : le régime général et ceux
  que la fiche coordonne avec lui ; les trois du code des pensions, que seuls
  les règlements européens coordonnent, depuis le 25 octobre 1998. « Compter
  les durées » en fait des trimestres, quatre au plus par année avec ceux de la
  France, que le taux, la décote, la surcote et la carrière longue lisent,
  jamais la proratisation.
- Quand un accord compare — les règlements depuis juin 1992, les conventions à
  comparaison ou à option —, la liquidation se refait sans les trimestres de
  ses périodes, et « compléter tous régimes » sert, dans chaque régime qui
  porte le minimum contributif, la plus élevée de la pension nationale et de la
  pension proratisée, chacune portée à son minimum : celui de la proratisée,
  depuis 2004, théorique puis réduit à la part du régime dans la durée totale
  non limitée, sa majoration selon les trois cas de l'exposé de la Cnav, les
  périodes étrangères comptées comme cotisées.
- Depuis 2012, l'écrêtement du minimum compte les pensions étrangères
  déclarées, hors celles des règlements européens et de six conventions ; « foyer
  et net » ne sert l'ASPA, à la liquidation ni à aucune échéance, à qui déclare
  résider hors de France.
- Deux présomptions naissent (§ 5.6), `pas_de_pension_etrangere` et
  `residence_en_france` ; la saisie accepte un premier emploi en France après
  l'âge de début le plus tardif quand la carrière a commencé à l'étranger.

Aucun des 669 témoins d'avant le domaine ne bouge ; douze témoins de simulation
et deux pages naissent pour lui, rendus à l'identique par les deux moteurs. La
page de simulation dit les trimestres que valent les périodes hors de France,
laquelle des deux pensions l'accord sert, et que l'ASPA ne se sert qu'en
France ; `docs/limites.md` dit ce qui est servi, et ce qui reste dehors.

**Quatrième étape, le 1er octobre : les exemples publiés.** Neuf exemples
entrent dans `tests/temoins/exemples_officiels.yaml`, et le modèle les rend
tous : les huit calculs de Léna et de Jahan que le CLEISS publie — les
règlements européens (France, Italie, Norvège), un accord à calcul séparé (les
États-Unis, deux fois), un accord qui compare (l'Inde), plusieurs accords (le
Canada et l'Uruguay, le Japon et le Maroc), les règlements et un accord
(l'Espagne et la Tunisie), un État sans accord (le Burkina Faso) — et
l'exemple 1 de la circulaire Cnav n° 2021/33 : la pension théorique sur les
vingt-cinq meilleures années depuis juillet 2022. Le banc date désormais une
carrière qui commence hors de France (`debut`, `etranger`), et une grandeur
naît, `annees_du_salaire_annuel_moyen`.

Les exemples à plusieurs accords ont appris au modèle la règle qui lui
manquait : la caisse ne totalise que les périodes d'un seul accord, avec celles
des États tiers qu'une convention fait compter. Il additionnait les années
japonaises et marocaines de Jahan, 176 trimestres au taux plein, quand le
CLEISS n'en compte que 160. Chaque famille de régimes retient désormais
l'accord qui lui apporte le plus de trimestres (`droit/etranger.py`, et son
jumeau), et le tableau des accords porte la liste des États tiers de sept
conventions, telle que le CLEISS l'énumère — le code de la Norvège entre
guillemets, que YAML lisait « faux ». Le prorata de l'exemple franco-japonais,
que le CLEISS rapporte à la durée des trois États quand l'accord n'en totalise
que deux, ne se compare pas, et la fiche `pension_proratisee` le dit. Aucun
des 681 témoins ne bouge ; deux naissent.

**Cinquième étape, le 1er octobre : le formulaire, la page Coût, la
décision.** Le formulaire demande le domaine dans un dépliant « Carrière hors
de France », replié tant qu'il est vide : jusqu'à quatre périodes — l'État, au
tableau des accords ou « un autre État », le mois où elle commence et celui où
elle finit, l'activité —, jusqu'à quatre pensions étrangères — l'État qui la
sert, son montant brut mensuel en euros d'aujourd'hui, le mois où elle
commence —, et la résidence après le départ ; chaque ligne déclarée en appelle
une vide. Le calendrier du début d'activité s'ouvre désormais jusqu'à
soixante-quinze ans, puisqu'une carrière commencée hors de France entre en
France à tout âge, et la saisie, qui refuse le début tardif d'une carrière
toute française, le dit. Le budget de mots du formulaire vierge monte de
quatre, le titre du dépliant ; la page de l'Espagnole qui réside en Espagne le
fige rempli. La page Coût ne bouge pas : aucun de ses chiffres n'a changé dans
les commits du domaine, et elle retirait déjà de la garantie les retraités qui
résident à l'étranger. La proposition n'en fait pas exception, comme son texte
le disait déjà : son compte ne connaît que les cotisations versées en France —
il n'a ni durée ni taux à totaliser —, et sa garantie vieillesse que les
retraités qui résident en France, comme l'ASPA qu'elle remplace (README,
`docs/limites.md`). Le simulateur l'applique désormais à qui déclare résider
ailleurs : la garantie du scénario 6 lui est refusée, au départ et aujourd'hui,
dans les deux moteurs, et la fiche `garantie_vieillesse` cite la phrase du
README ; le seul témoin qui réside hors de France perd la sienne.

**Le domaine se clôt le même jour**, le gabarit du § 11 rempli :
- **les fiches** : quatre, découpées en versions et `approchee` chacune avec
  ses approximations — `totalisation_des_periodes_etrangeres`,
  `pension_proratisee`, `minimum_contributif_international`,
  `residence_et_minimum_vieillesse` —, et le tableau des accords, qui dit pour
  68 États et les organisations internationales l'accord en vigueur à chaque
  date, son calcul, et les États tiers que sept conventions font compter ;
- **les faits de la chronologie** : les périodes à l'étranger, les pensions
  étrangères, liquidations observées, et la résidence après le départ ; deux
  présomptions, `pas_de_pension_etrangere` et `residence_en_france` ;
- **les fonctions dans l'étape** : `droit/etranger.py` et son jumeau, que la
  coordination, les durées, l'ouverture, la liquidation, « compléter tous
  régimes » et « foyer et net » appellent ;
- **les exemples publiés** : neuf, tous reproduits ;
- **le bloc du formulaire** : « Carrière hors de France » ;
- **la page Coût** ne bouge pas ;
- **la décision de la proposition** : elle n'en fait pas exception, comme son
  texte le disait ;
- **la référence de conservation** est refigée
  (`python scripts/conservation.py --figer`).

Restent, hors du domaine clos, et consignés dans ses fiches : la pension que
sert l'autre État, que le modèle ne calcule pas ; les années du salaire annuel
moyen de la pension théorique, réduites au prorata de 2004 à juin 2022 ; la
comparaison des pensions des fonctionnaires, que le minimum garanti peut
relever ; la révision de l'écrêtement quand une pension étrangère commence
après le départ (R. 173-8) ; la subsidiarité du minimum, présumée remplie ; les
mois de séjour de chaque année et la condition de L. 816-1 ; les listes d'États
tiers à leurs dates d'avant 2026 ; le calcul des conventions d'avant l'entrée
des États dans l'Union ; la règle de la caisse des fonctionnaires. Le domaine
suivant se mesurera à son ouverture.

**Ses limites, reprises le même jour**, à la demande du propriétaire : « Fait
de ton mieux pour gérer ces limites. » Cinq sont levées, dans les deux moteurs,
chacune avec ses tests, ses témoins et sa fiche, dans un commit à part :
- **le salaire annuel moyen de la pension proratisée** se prend sur des années
  réduites au prorata des régimes alignés et des régimes étrangers « équivalant
  au régime général » (R. 173-4-3 ; circulaires ministérielle 2008/219 et Cnav
  2008/58, 2012/26, 2013/56), de 2004 à juin 2022, et depuis hors de la
  liquidation unique (circulaire n° 2021/33, point 4) ; le tableau des accords
  porte la liste de 2012 (`salaire_moyen`) ; l'exemple 2 de la circulaire de
  2008 est rejoué, et le seul témoin qui bouge, une carrière portugaise
  liquidée en 2018, gagne 2,77 % ;
- **la pension étrangère déclarée** compte dans les ressources de l'ASPA
  (R. 815-22 ; exposé de la Cnav « Evaluation des ressources - Aspa ») et dans
  celles de la garantie de la proposition, qui « remplace l'ASPA », au départ
  et à chaque échéance ; la page dit qu'elle se sert à part, et une
  affirmation de plus le contrôle ;
- **les mois passés en France** se déclarent (`mois_en_france`, dans les deux
  saisies, le formulaire et le fait de résidence) : l'ASPA et la garantie ne se
  servent qu'à qui y séjourne plus de six mois de l'année civile, plus de neuf
  depuis le 1er septembre 2023 (L. 815-1, R. 111-2) ;
- **le minimum contributif se révise** quand une pension étrangère commence
  après le départ (R. 173-8) : « faire vivre » rogne, à chaque échéance, ce
  qu'elle passe de la marge sous le plafond, que le départ garde ;
- **les listes d'États tiers se datent** : une pension prend la dernière lue au
  plus tard à sa date d'effet — Maroc 2011, Uruguay 2017, Brésil 2019, puis le
  CLEISS en 2026 ; l'annexe de la circulaire n° 2020/30 date les liens du
  Canada, tous antérieurs à son accord.

La sixième, la comparaison des pensions des fonctionnaires, reste : la France
n'est pas à l'annexe VIII, partie 1, du règlement 883/2004, et ses périodes
européennes entrent dans la durée de L. 14-I (bulletin officiel du Service des
pensions n° 473), mais la règle du minimum garanti d'une pension au prorata
n'a été trouvée ni chez le Service des retraites de l'État ni à la CNRACL ;
l'approximation de `pension_proratisee` dit ce qui est lu. Restent aussi, dans
les fiches : la pension que sert l'autre État, prise déclarée ; la subsidiarité
du minimum ; la tolérance de cent soixante jours ; le foyer permanent de
R. 111-2 ; la condition de L. 816-1 ; le tableau de 2008 des régimes
équivalents, avant 2012 ; les conventions d'avant l'Union.

### 131. Les dix fiches nées à la phase 6, relues à la source : les écarts qu'elles montrent, à corriger — `en cours`

**Reprise, au 23 octobre 2026.** Faits, des coupures au mois au forfait du collaborateur
au compte. Restent : des classes, l'acte vétérinaire (au propriétaire), des décrets non
lus ; de `coefficients_anticipation_agirc_arrco`, l'ASF réservée de 1983 à 2003 aux
salariés et aux chômeurs (au propriétaire) ; de `decote_avant_1983`, l'ajournement des
artisans et commerçants et les « soixante et un ans » agricoles, aux décrets de 1956 à
1968 (au propriétaire) ; la durée du minimum de D. 634-14 (la Cnav, au propriétaire) ;
`pension_non_salaries_agricoles_2026` ; les années au prorata de l'exploitant, celle du
décès comprise (au propriétaire : la pratique de la MSA, l'option du conjoint survivant) ;
l'assiette minimale des indépendants au compte (D. 633-2 ; au propriétaire : la carte la
laisse sans décision) ; l'AVI du collaborateur, sur les revenus du chef. Détail : les notes.

**La relecture, le 27 septembre 2026**, menée pendant la phase 7 par une autre
session, à la demande du propriétaire, après avoir vérifié qu'elle ne lui
prenait rien : ni fichier commun, ni fichier déplacé, ni résultat. Les dix
fiches que la phase 6 avait fait naître « à vérifier » ont été lues à la
source, dans l'index LEGI ou JORF du dépôt et sur le site de chaque caisse.
Toutes passent à `approchee` : le moteur s'écarte du texte sur chacune. Rien
n'est corrigé : la phase 7 devait garder ses témoins au bit près, et deux de
ces fiches, `assiette_minimale_agricole` et `cotisation_par_classes_liberales`,
sont gardées par leur nom dans la couche des comptes notionnels. Ce que le
moteur lit d'une fiche, son `code` et son étape, n'a pas bougé ; témoins et
paquet sont restés identiques. Le journal de veille dit ce qui a été lu ;
chaque fiche, ses lectures, ses textes, ses écarts, et deux lectures
divergentes entre le texte et la caisse (la décote des IEG depuis 2025, la
borne de la surcote de la CPRN).

**En chemin**, `scripts/textes.py --inscrire` butait sur deux arrêtés du
10 juillet 2026 sous la même clé datée : un texte nouveau prend désormais le
sigle de sa section (`arrete_2026_07_10_carmf`), un texte déjà inscrit garde
la sienne, et un test le tient. Les 767 rédactions des textes que les fiches
citent sont entrées « à examiner », et le cliquet des rédactions sans statut
est descendu de 10 547 à 10 440.

**Ce qui reste : les corrections**, chacune écrite dans l'`a_relire` de sa
fiche, « Après la phase 7 : ». Elles déplacent des résultats : chacune se fait
dans un commit à part, avec le diff de ses témoins, et jamais pendant une
phase de réorganisation, qui doit garder les siens au bit près. Des plus
lourdes aux moindres :

- `assiette_minimale_agricole` : les points de la complémentaire au minimum,
  100 par an depuis 2017 au lieu de 117 puis 133, et ses minima de 2003 à
  2005 ; la base au plancher de 600 SMIC dès 1990, quand les textes en fixent
  400 jusqu'en 2003 au moins.
- `cotisation_par_classes_liberales` : les grilles de chaque époque de la
  Cipav et de la CAVEC, que le moteur tire d'une seule par le rapport des
  plafonds ; la CARPV d'avant 1998 et son taux d'appel ; l'année de revenu que
  le texte désigne.
- `decote_avant_1983` : le taux de soixante-cinq ans aux femmes de 150
  trimestres, dès soixante ans de 1979 au 31 mars 1983, et la coupure au
  1er avril 1983.
- `decote_regimes_speciaux` : les IEG et la CRPCEN depuis 2025, la borne par
  la durée, et la lecture à l'année des pas de 2010 à 2024.
- `coefficients_anticipation_agirc_arrco` : les points de tranche C d'avant
  2016, minorés même au taux plein.
- `surcote_par_age_seul` : les bornes de la CAVP et de la Cipav, les dates de
  la CAVEC, le départ de la CARPIMKO, les trimestres d'exercice de la CPRN.
- `minoration_racl_2014_2024`, `retraite_proportionnelle_msa`,
  `surcote_ircantec`, `decote_opera_de_paris` : des écarts moindres, chacun
  dit dans sa fiche.

Deux notes de fichiers de régimes sont à corriger avec elles (`msa_non_salaries`,
`msa_rco`), et les exemples publiés trouvés sont à porter dans
`tests/temoins/exemples_officiels.yaml` : la CNIEG, la CRPCEN, le dépliant de
la tranche C d'Agirc-Arrco, le guide de la CARMF, la page de la MSA sur la
réforme de 2026. `python scripts/veille_droit.py` ne liste plus ces fiches,
lues ce jour : c'est cette action qui les tient.

**La suite, le 27 septembre 2026 au soir**, pendant la phase 8, et seulement ce
qui ne déplace aucun résultat. Cinq exemples publiés entrent dans
`tests/temoins/exemples_officiels.yaml` (CNIEG, Agirc-Arrco, CARMF), et le
modèle les rend tous ; ceux qu'on laisse le sont avec leur raison, dans leur
fiche. Les textes que les index ne portaient pas sont lus où ils sont : le droit
de 1945 à 1972 au Journal officiel que Gallica numérise et dans la base des
circulaires de la Cnav, les statuts des sections libérales sur les sites des
caisses. Deux écarts que rien ne déclarait le sont désormais : aux IEG, la durée
requise de l'agent qui peut partir avant soixante ans, de 2019 à 2024
(`regimes_speciaux_par_generation`, qui passe de `conforme` à `approchee`) ; au
régime général, les trimestres retenus en 1972, 1973 et 1974
(`trimestres_retenus_1972_1974`, qui naît `manquante`). Le journal de veille dit
le reste, lu, trouvé et introuvable.

Les corrections attendent désormais la fin de la phase 8, qui court dans une
autre session et doit garder ses témoins au bit près : les fiches disent
« Après la phase 8 : ». Les notes des fichiers de régimes qu'elles citent
(`carmf_complementaire`, `cavec_complementaire`, `ircec_racl`, `opera_de_paris`,
`msa_non_salaries`) attendent avec elles, puisqu'elles passent dans le paquet du
site.

**Les premières corrections, le 27 septembre 2026, la phase 8 close.**
Préparées pendant la phase sur une branche à part, sans rien publier, puis
reprises sur son dernier commit ; chacune a son commit et le diff de ses
témoins, et la suite complète est passée sur chacune :
- **La complémentaire agricole et le plancher de la base**
  (`assiette_minimale_agricole`, `retraite_proportionnelle_msa`) : la RCO lue
  année par année, sept périodes au lieu d'une (le minimum d'assiette, les
  points qu'il ouvre, le taux), et le plancher de la base à 400 SMIC de 1990 à
  2003 ; les notes de `msa_rco` et de `msa_non_salaries` avec elles. Cinq
  témoins sur 535 : +2,4 % pour un chef d'exploitation né en 1975, +1,4 % pour
  un chef né en 1965, et de 1 à 3 % de moins dans les scénarios rétroactifs.
  La dette de la proposition en 2070 passe de 32,85 % à 32,48 % du PIB :
  l'accueil et la page Programme disent 32 % au lieu de 33.
- **Les IEG** (`regimes_speciaux_par_generation`, `age_reference_decote_ieg`) :
  la durée de l'agent qui ouvre son droit avant soixante ans, de 2019 à 2024,
  est celle de la génération qui atteint cet âge ce mois-là (article 9-1 de
  l'annexe 3) ; qui a ouvert son droit avant 2025 garde l'âge d'annulation
  d'avant, quelle que soit la date d'effet, comme la CNIEG l'applique. Deux
  témoins : +3,2 % et +1,2 % pour des agents nés en 1965. L'exemple 1 de la
  circulaire CNIEG n° 2024/15, Monsieur A, entre au témoin, et le modèle le
  rend ; `regimes_speciaux_par_generation` repasse `conforme`.
- **En chemin, le filet de conservation** (`docs/architecture.md`, § 12)
  gelait les tableaux que `scripts/chiffrage_plf.py` réécrit, collés à leur
  repère : la première correction les disait perdus. Il lit désormais les
  `blocs_produits` de `zones.yaml`, et sa référence est refigée sans rien
  perdre.

Restent, de la liste : `cotisation_par_classes_liberales`, `decote_avant_1983`,
`decote_regimes_speciaux` (la CRPCEN depuis 2025, la borne par la durée, la
lecture au mois des pas de 2010 à 2024), `coefficients_anticipation_agirc_arrco`,
`surcote_par_age_seul`, `minoration_racl_2014_2024`, les autres écarts de
`retraite_proportionnelle_msa`, `surcote_ircantec`, `decote_opera_de_paris` et
`trimestres_retenus_1972_1974` ; et les notes de `carmf_complementaire`,
`cavec_complementaire`, `ircec_racl` et `opera_de_paris`.

**La suite des corrections, le 27 septembre 2026 dans la soirée**, à la demande
du propriétaire. Chacune a son commit, le diff de ses témoins et la suite
complète ; les rebasages sur les commits de l'autre session ont relancé les
fichiers fabriqués à chaque arrêt :
- **Les régimes spéciaux** (`decote_regimes_speciaux`, qui passe `conforme`) :
  le barème de la décote lu au mois où le droit s'ouvre, et le décompte par la
  durée borné à la durée requise moins 150 ; la surcote, pour les seuls
  trimestres d'après le 1er juillet 2008 et dès 160 trimestres (neuf témoins) ;
  la CRPCEN, l'âge et la durée de ses textes par génération et l'âge de
  référence de 2025, qui rendent la table que la caisse publie et l'exemple de
  Maria (trois clercs témoins, de −1,2 % à +9,3 %).
- **L'Opéra** (`decote_opera_de_paris`, qui passe `transcrite`) : l'âge
  d'annulation du ballet, 41, 41,5 puis 42 ans de 2010 à 2012.
- **La loi Boulin** (`trimestres_retenus_1972_1974`, qui passe `transcrite`) :
  128, 136 puis 144 trimestres retenus, au régime général et chez les salariés
  agricoles, que l'article 72-1 du décret de 1945 et l'article 59-1 du décret
  n° 50-1225 écrivent, trouvés dans l'index LEGI.
- **Avant avril 1983** (`decote_avant_1983`) : le taux qui croît au-delà de 65
  ans, le taux acquis au 31 mars 1983, les femmes de 150 trimestres dès 63 puis
  60 ans, les années d'assurance avant 1951 ; les trois exemples de la
  circulaire Cnav n° 22/83 entrent au témoin. Le bilan ne bouge que sur les
  années passées, et l'écart du scénario 4 sur les générations passées passe de
  −52,6 % à −52,8 %.
- **Les sections libérales** (`surcote_par_age_seul`) : le départ de la
  CARPIMKO à la durée atteinte, les bornes de la CAVP par génération, les cinq
  ans de la Cipav comptés de 65 ans jusqu'en 2021, les trimestres d'exercice de
  la CPRN ; les notes de la CARMF et de la CAVEC, et `cavec_report_2025` au
  calendrier (deux témoins, +1,9 % et +0,6 %).
- **Le RACL et l'Ircantec** (`minoration_racl_2014_2024` ; `surcote_ircantec`,
  qui passe `transcrite`) : l'annexe de 2013 par génération, la fenêtre de la
  surcote comptée au mois ; la note du RACL (un témoin, +0,06 %).
- **La MSA** (`retraite_proportionnelle_msa`) : les points arrondis à l'entier ;
  le motif de non-application de la réforme de 2026 mis à jour (six témoins,
  moins de 0,05 %).
- **Les classes libérales** : les notes de la CARPV et de la Cipav.

Une règle manquante trouvée en chemin est déclarée :
`majoration_duree_apres_65_ans`, la durée « corrigée » de 2,5 % par trimestre
après 65 ans, de l'article 70-6 du décret de 1945 à R. 351-7, avec le premier
exemple de la circulaire n° 22/83 en écart connu.

**Ce qui reste de l'action, et pourquoi.**
- Les coupures au mois : le 1er avril 1983 au régime général et chez les
  salariés agricoles, le 4 septembre 2018 et le 6 juillet 2025 à la CAVEC, le
  15 mai 2025 au RACL. Le moteur choisit ses périodes à l'année, partout ; elles
  attendent les versions datées (`docs/architecture.md`, § 4.6), que le domaine
  des enfants vient d'ouvrir.
- `majoration_duree_apres_65_ans`, à porter : elle touche toute liquidation
  après 65 ans sans la durée, depuis 1983.
- `retraite_proportionnelle_msa` : le maximum M avec l'allocation aux vieux
  travailleurs salariés, dont la série est à faire entrer (zone des données) ;
  la réforme des vingt-cinq meilleures années, en vigueur depuis 2026, un
  chantier à part (R. 173-3-2 lu).
- `cotisation_par_classes_liberales` : les grilles de chaque époque (les points
  des classes intermédiaires dans chaque rédaction de l'article 2, les montants
  des décrets annuels, les bornes que publient les caisses), l'année de revenu
  et la classe de début d'activité, la CAVEC d'avant 1980, l'exemple de la
  Cipav de 2022, qui demande à l'oracle une grandeur de cotisation.
- `coefficients_anticipation_agirc_arrco` : les points de tranche C d'avant
  2016, à suivre de l'acquisition à la liquidation à travers la fusion de 2019.
- `decote_avant_1983` : le maximum des pensions, l'ajournement des artisans et
  commerçants, et les « soixante et un ans » des salariés agricoles.

**Le 28 septembre 2026, la durée majorée après l'âge du taux plein**, portée
(`majoration_duree_apres_65_ans`, qui passe `approchee`) : 2,5 % de la durée
du régime par trimestre écoulé depuis l'âge du taux plein, pour qui n'a pas la
durée, au régime général et chez les salariés agricoles depuis 1983 ; depuis
2004, la durée de tous les régimes de base ouvre et borne la majoration, et un
régime aligné liquidé à part n'en reçoit que sa part (R. 173-4-2). La garantie
du taux acquis au 31 mars 1983 compare désormais deux pensions, comme le fait
la circulaire Cnav n° 8/89 : le premier exemple de la circulaire n° 22/83 est
rendu, le troisième devient un écart connu, qu'un salaire moyen de 1,7 plafond
et le maximum décident ; l'exemple de la circulaire n° 8/89 entre au témoin, les
cinq partages de la circulaire n° 2004/20 sont des tests. Aucun témoin ne
bougeait : deux témoins nés pour la règle la montrent aux deux moteurs. Le
décompte part du mois qui suit l'âge, comme celui de la surcote : il suivra
l'action 132. Restent, avec leur raison :
- les artisans et commerçants liquidés à part des salariés : D. 634-5 les
  majore depuis 1990 sur leurs seuls trimestres d'après 1972, à porter ; de
  1984 à 1989, le texte n'est pas dans l'index (l'article 2 du décret
  n° 73-937 ne renvoie qu'à l'article 70-6 d'avant 1982) ;
- le maximum des pensions, 50 % du plafond à la date d'effet, surcote non
  comprise, que la base de la Cnav écrit sur la loi n° 49-244 du 24 février
  1949, article 2 : l'index du Journal officiel n'en porte que le titre, et
  Légifrance refuse les requêtes de la session (403) ; la règle attend sa
  lecture ;
- l'ajournement des artisans et commerçants avant le 1er juillet 1984 :
  l'article 70 du décret de 1945 majorait la pension « de 5 p. 100 du salaire
  annuel moyen de base par année postérieure à [soixante ans] », sans borne,
  mais l'index ne porte le renvoi du décret n° 73-937 que dans sa rédaction
  de 1984, déjà à la règle nouvelle ;
- les « soixante et un ans » des salariés agricoles, que seule une lecture de
  la caisse trancherait.

**Le même jour, la tranche C de l'Agirc d'avant 2016**, portée
(`coefficients_anticipation_agirc_arrco`, qui reste `approchee` pour ses
autres questions) : les points constitués sur la tranche C jusqu'en 2015
gardent le coefficient pour âge avant soixante-sept ans, même au taux plein.
L'acquisition les range à part, depuis les périodes de la tranche C de 1991 à
2015 (`points_abattus_a_l_age`, la période 2015-2018 coupée au 1er janvier
2016) ; la liquidation leur applique le coefficient de la table des âges quand
il est plus sévère que celui des autres points. Aucun témoin ne bougeait,
aucun cadre témoin n'étant payé au-delà de quatre plafonds : un témoin né pour
la règle la montre, 40 % des points Agirc d'un cadre de 1955 parti à 62 ans à
0,78. Restent : le report de ces points sans abattement à soixante-sept ans
(article 102 de l'accord de 2017), que le moteur ne sert pas faute de liquider
une pension en deux fois ; et les liquidations de 1991 à 2003, où le moteur
applique la règle de 2003 sans avoir lu l'accord de l'ASF.

**Puis les artisans et commerçants**, que la durée majorée laissait de côté
quand ils sont liquidés à part des salariés : D. 634-5 la leur donne depuis le
1er janvier 1990, dans chacune de ses rédactions jusqu'à celle de 2023. Les
périodes 1983-1993 de la CANCAVA et de l'ORGANIC sont coupées à cette date ;
les suivantes, et celles du RSI, portent les deux interrupteurs. Aucun témoin
ne bougeait ; un artisan né pour la règle, parti à 68 ans en 2008 avec 132
trimestres, en a 150. Restent : leurs années d'avant 1973, que D. 634-5 exclut
de la base de la majoration et que le moteur liquide comme les suivantes ; et
1984 à 1989, dont le texte n'est pas lu.

**Enfin, la réforme agricole de 2026**, que la fiche
`retraite_proportionnelle_msa` rangeait en chantier à part et que
`docs/limites.md` disait incalculable faute de décrets — ils ont paru au
Journal officiel du 31 décembre 2025. L. 732-24 dans sa rédaction de 2026 est
porté (`pension_non_salaries_agricoles_2026`, `approchee`) : les périodes des
non-salariés agricoles sont coupées au 1er janvier 2026 et au 1er janvier
2028. Depuis 2028, la pension cumule le revenu annuel moyen des meilleures
années depuis 2016, au taux et au prorata du régime général, la retraite
forfaitaire de D. 732-62 au prorata de la seule durée d'avant 2016, et la
moyenne arrondie des points des meilleures années d'avant 2016, multipliée par
le nombre de ces années (R. 732-66) ; les vingt-cinq années se répartissent
entre régimes et entre les deux périodes par R. 173-3-2
(`liquider.repartir_les_annees`) ; la pension est bornée à la moitié du
plafond, avant la surcote. En 2026 et 2027, la plus forte du calcul provisoire
— l'ancienne formule, la moyenne d'avant 2016 en plus — et du recalcul de 2028.
Les points ne s'acquièrent plus depuis 2028 : la période n'en porte pas le
barème. Un test rejoue l'exemple de la MSA : six, treize et six années, 403
points sur treize ans, 682 points. Deux témoins bougent, l'exploitant né en
1975 (+6,8 % de pension totale) et celui né en 1965 (+11,4 %) ; le coût du
système actuel en 2070 passe de 710 à 712 Md€, et l'équilibre des comptes
notionnels suit. Le calendrier ne déclare plus la réforme `non_appliquee`.
Restent, avec leur raison :
- le régime général, les salariés agricoles et les indépendants d'un ancien
  exploitant, dont le salaire annuel moyen garde ses vingt-cinq années au lieu
  de la part que R. 173-3-2 leur laisse : à porter, en commit à part ;
- les années d'avant 1990, dont le barème de points n'est pas lu, qui entrent
  dans la moyenne par l'équivalent en points de leur rendement ;
- le revenu des années cotisées au minimum, que L. 732-24 déduit des
  cotisations acquittées, porté au plancher de six cents SMIC horaires ;
- les durées que R. 173-3-2 arrête au 31 décembre de l'année d'effet, comptées
  à la date d'effet ; les majorations de points de 1952 à 1972 (R. 732-67), les
  rachats et les conjoints collaborateurs ;
- les trimestres d'enfants des exploitantes, que le moteur ne leur attribue
  pas : R. 732-61 est porté pour le jour où il le fera.

**Puis la part des régimes alignés**, en commit à part : depuis 2026, le
salaire annuel moyen du régime général, des salariés agricoles et des
indépendants d'un assuré qui a aussi été exploitant ne retient que la part des
vingt-cinq années que la première répartition de R. 173-3-2 leur laisse
(`liquider.annees_des_regimes_alignes`) — six sur dix années de salarié
agricole dans l'exemple de la MSA, que le test rejoue désormais des deux
côtés. Aucun témoin ne bouge : aucun ne mêle les deux régimes après 2025.
Restent :
- pour qui est né avant 1953, le partage de cette part entre régimes alignés
  (R. 173-3-2, II, a), que le moteur leur donne à chacun entière ;
- trouvé en chemin, R. 173-4-3, qui de 2004 à 2025 partageait déjà les années
  entre régimes alignés que la liquidation unique ne réunit pas — assuré né
  avant 1953, ou parti avant le 1er juillet 2017 —, « en multipliant le nombre
  d'années fixé dans le régime considéré [...] par le rapport entre la durée
  d'assurance accomplie au sein de ce régime et le total des durées » : le
  moteur ne le porte pas et donne vingt-cinq années à chaque régime, ce qui
  sous-estime leurs salaires moyens. Noté à la fiche `salaire_annuel_moyen`.

**Puis R. 173-4-3, porté**, avec la circulaire Cnav n° 2004/29 qui
l'applique : depuis les pensions de 2004, le polypensionné des régimes alignés
que la liquidation unique ne réunit pas retient dans chaque régime la part des
années que sa durée lui donne, arrondie au plus proche sans descendre sous un,
les artisans et commerçants comptés depuis 1973
(`liquider.annees_au_prorata`) ; depuis 2026, pour qui est né avant 1953, la
seconde répartition de R. 173-3-2 fait de même. Les deux exemples de la
circulaire sont des tests — 15 années sur 21, 4 sur 20 —, et un assuré né en
1944, salarié puis artisan, en retient 15 et 6. Aucun témoin ne bouge. Les
deux restes du paragraphe précédent sont faits ; reste, de R. 173-4-3, que les
durées sont celles de la date d'effet et non du dernier jour du trimestre
civil qui la précède.

### 133. La retraite de base et ses complémentaires, sous le montant du système 1 — `en cours`

**Reprise, au 13 octobre 2026.** L'étage de chaque régime, la ligne sous le
système 1 et le détail sont faits. Les mineurs attendent une décision du
propriétaire : servir leur complémentaire, l'Agirc-Arrco, plus tard que la
base, et ce que vaut le système 1 entre cinquante-cinq et soixante ans ;
viendraient ensuite son routage, l'ANGDM, les ETAM et les ingénieurs. Les
chemins de fer secondaires sont lus : reste à garder à la caisse autonome les
embauchés d'avant le 1er octobre 1954, ce qui demande au modèle le salaire
moyen des trois dernières années et au propriétaire le choix entre service
actif et sédentaire ; la complémentaire des embauchés d'après n'a de barème
publié que pour 1955. Détail : note du 13 octobre (`133/`), « Le 28 septembre ».

**Demande**, le 27 septembre 2026. « On ne montre pas réellement le découpage
du montant des retraites dans les différents scénarios, c'est normal ? On ne
devrait pas avoir la retraite de base et ensuite toutes les complémentaires
qui s'ajoutent par-dessus ? », puis « Vas-y ».

**La réponse.** Pour les systèmes notionnels, c'est voulu : le compte reçoit
chaque année les cotisations de tous les régimes, base et complémentaires
ensemble, et ne sert qu'une pension ; la proposition affiche déjà ses seules
lignes, répartition et rentes capitalisées. Pour le système 1, le détail
existait (`pensions_par_regime`), mais seulement dans le dernier dépliant, « Le
détail du calcul », et dans l'ordre alphabétique des codes, qui mettait l'Agirc
avant le régime général et coupait la complémentaire d'un cadre en trois lignes
sans les réunir.

**Ce qui est fait.**

- Chaque fiche de régime calculé porte son `etage`, une ligne sous `famille` :
  `base` (17), `complementaire` (34), `integre` (19 — la fonction publique et
  les régimes spéciaux, dont la pension tient les deux rôles) ou `additionnel`
  (4 — RAFP, ASV, RAFEP, allocation des gérants de débits de tabac). La
  famille ne suffisait pas : la CNAVPL et la CARMF sont toutes deux `liberal`.
  Le schéma le décrit, avec sa source pour « intégré » (Fipeco, « Les retraites
  des fonctionnaires ») ; le chargeur refuse une autre valeur ; le paquet le
  porte au site. La tranche B de Polynésie reste à la base : le CLEISS range
  tout le régime de la CPS dans l'assurance vieillesse de base, l'Agirc-Arrco y
  étant la complémentaire, facultative (« La sécurité sociale des salariés en
  Polynésie française », lu le 27 septembre 2026).
- Sous le montant du système 1, une ligne : « 1 652 € de retraite de base +
  1 335 € de retraite complémentaire », pour le cadre né en 1962. Elle est dans
  l'unité du montant, arrondie au plus fort reste, pour que les parts fassent le
  montant affiché. La majoration pour enfants y suit le régime qui la sert, le
  minimum vieillesse y est un terme à part, et pour qui est déjà parti chaque
  régime y porte sa propre revalorisation. Un régime intégré seul écrit « une
  seule pension, sans complémentaire à part », et le glossaire définit « régime
  intégré ».
- « Le détail du calcul » range les régimes par étage, dans l'ordre du
  catalogue ; un étage de plusieurs régimes a sa ligne de somme, chacun en
  retrait dessous.
- Deux tests de données (l'étage de chaque régime ; un régime intégré n'est
  routé avec aucune base ni complémentaire) et trois tests de page (la ligne
  fait le montant sur quatre profils, dont un minimum vieillesse et un
  retraité ; le régime intégré ; l'ordre et la somme du détail).

**Ce qu'il déplace.** Aucun chiffre du modèle : les témoins de simulation sont
identiques. Les 29 témoins de pages qui calculent gagnent la ligne et le
nouveau tableau, et le paquet du site un kilo-octet.

**Ce qui reste.**

- L'étage `integre` de cinq régimes spéciaux — mines, marins, SEITA, chemins
  de fer secondaires, port de Strasbourg — ne repose que sur le routage, qui ne
  leur adjoint aucune complémentaire ; il n'a pas été lu à la source. Qui
  trouvera la leur, celle des mineurs par exemple, la routera et passera
  l'étage à `base` : le test l'y obligera.
- La ligne de la proposition arrondit ses termes un à un : 2 316 + 10 + 10 font
  2 336 € sous un montant affiché de 2 337 €, pour le même cadre. Le plus fort
  reste la ferait s'additionner ; le parcours de présentation en cite peut-être
  les chiffres.
- Découper aussi la pension notionnelle selon l'origine des cotisations — tant
  venu de ce qui a été cotisé au régime général, tant de l'Agirc-Arrco : le
  compte ne garde que le total de chaque année. C'est un choix de présentation
  de la proposition, qui attend le propriétaire.

**La suite, le 27 septembre 2026 au soir.** « Continue l'action 133. Ne fais
pas d'erreur. » Deux des trois points restants sont faits ; le troisième est
posé au propriétaire.

- **Les cinq régimes spéciaux, lus à la source**, dans l'index JORF et LEGI
  du dépôt et sur les sites officiels. Les mines passent à `base` : leurs
  assurés avaient une complémentaire — la caisse de retraite complémentaire
  des employés des mines (arrêté du 5 octobre 1949 et ses modifications
  jusqu'en 1956), le régime complémentaire des ouvriers mineurs des
  Charbonnages de France (arrêté du 6 novembre 1967, sur le protocole UNIRS du
  25 avril 1960), et leur caisse, la CARCOM (statuts de 1990 à 1995). Le routage ne
  la porte pas : la fiche passe de `modelise` à `partiel`, et son `manque` le
  dit, textes cités. Les quatre autres restent `integre`, et chaque fiche dit
  en commentaire ce qui a été lu : l'ENIM (page du ministère de la mer,
  portail commun des régimes, rapport du Sénat n° 707 de 2012-2013), la SEITA
  (loi n° 84-603, décret n° 85-844, décret n° 95-99, arrêté du 9 mai 1995),
  le port de Strasbourg (portail commun des régimes) et les chemins de fer
  secondaires, dont le régime complémentaire n'est institué qu'en 1954, avec
  la fermeture (décret n° 54-953 ; décret n° 55-1297, article 5). Chemin
  faisant : le routage de ces derniers ne porte aucune complémentaire en 1955
  et 1956, puis celle de l'UNIRS, quand le texte les affilie à la caisse
  autonome de retraites complémentaires et de prévoyance du transport ; leur
  `manque` le dit aussi. L'arrêté du 20 juillet 2018 sur le répertoire de
  gestion des carrières unique, lu en passant, range la CRPN, l'IRCEC, le RCI,
  l'Agirc-Arrco et l'Ircantec parmi les régimes complémentaires, comme leurs
  étages. Le schéma ne prête plus à tous les régimes spéciaux la fermeture
  vers le régime général et l'Agirc-Arrco : il la nomme pour ceux dont le
  routage la porte.
- **La ligne de la proposition s'additionne.** Le montant et le plancher « sans
  rien ajouter » gardent chacun leur arrondi, celui du grand nombre et celui
  du résumé en tête de page ; la rente volontaire est leur écart, et le
  plancher se partage au plus fort reste. Un test le tient sur sept profils :
  l'ancien code en manquait quatre.

**Ce qu'il déplace.** Aucun chiffre du modèle. L'inventaire compte un régime
modélisé de moins et un partiel de plus ; les pages des résultats écrivent la
ligne de la proposition à l'euro près.

**Ce qui reste, à cette date.**

- L'étage `integre` de six autres régimes ne repose encore que sur le
  routage : l'Opéra, la Comédie-Française, les assemblées, le CESE, les
  fonctionnaires du Pacifique et les ouvriers de l'État. Leurs textes restent
  à lire, comme l'ont été ce soir ceux des cinq premiers.
- Router la complémentaire des mineurs, et celle des chemins de fer
  secondaires en 1955 et 1956 : leurs taux et leurs barèmes restent à lire.
  C'est un changement du scénario 1, qui relève de la session des données.
- Découper la pension notionnelle selon l'origine des cotisations : la
  question est posée au propriétaire.

**Le 28 septembre 2026 : la pension notionnelle, par origine des
cotisations.** Le propriétaire a demandé tout ce qui restait. Chaque
cotisation du compte garde désormais le régime qui l'a encaissée
(`CotisationAnnuelle.par_regime`), et le capital se partage entre eux, chaque
versement revalorisé comme le reste (`CompteNotionnel.capital_par_regime`,
porté au dictionnaire des résultats, en Python comme en JavaScript). Deux
origines ne sont pas des régimes : le régime unique, depuis la bascule, et le
taux d'acquisition commun, qui réunit les assiettes avant de prélever.
« Le détail du calcul » y gagne un tableau, « Les quatre systèmes, régime par
régime » : ce que chaque régime sert au système 1, et ce que valent ses
cotisations dans chacun des trois comptes — leur part du capital, sur le
diviseur ; puis le régime unique, la majoration pour enfants, le minimum
vieillesse et la garantie vieillesse, chacun sur sa ligne. Le système 4, quand
son départ est reporté, y est ramené aux euros du même départ par les prix ;
la rente du pilier capitalisé reste hors du tableau, qui le dit, comme un
régime provisionné. Un test du moteur tient le partage sans reste (un cadre,
deux activités cumulées, un taux commun) ; un test de la page, l'addition de
chaque colonne sur les montants affichés, et ses totaux, sur six profils ; le
catalogue des affirmations, la ligne du total, par un contrôle sur le modèle.
Aucun chiffre du modèle ne bouge : les témoins des simulations gagnent le seul
`capital_par_regime`.

**Le 28 septembre 2026, suite : l'étage des six derniers régimes, deux
routages corrigés, deux complémentaires lues.**

- **L'étage.** Le schéma de l'Union Retraite, « Les régimes de retraite en
  France » (PDF du 27 mars 2025), lu sur son rendu, range sous « Retraite de
  base + complémentaire » le SRE, la CNRACL et les régimes spéciaux qu'il
  nomme : FSPOEIE, CRPCEN, CNIEG, RATP, Banque de France, CPR, Comédie-Française,
  Opéra, port de Strasbourg, Enim. Les six fiches qui ne reposaient que sur le
  routage restent `integre`, chacune sur sa source, dite en commentaire de son
  étage : ce schéma pour l'Opéra et la Comédie-Française ; ce schéma et le
  décret n° 2004-1056 (article 8, IV : les cotisations vieillesse et Ircantec
  des services validés sont annulées au profit du fonds spécial) pour les
  ouvriers de l'État ; la loi n° 2023-270, a contrario, pour le CESE ;
  l'article 5 du règlement de la caisse des députés pour les assemblées ; la
  page retraite de la DRHFPNC pour la caisse locale de Nouvelle-Calédonie. Les
  douze autres fiches intégrées disent aussi ce qui a été lu — celle des
  pensions civiles d'avant 1948, que son étage ne l'a pas été à part —, et le
  schéma des régimes le dit. Le `manque` des assemblées nomme deux compléments internes
  qu'il ne porte pas : le « système de retraite complémentaire facultatif »
  des députés, supprimé au 1er janvier 2018, et le régime par points des
  sénateurs, que seule une page de la-retraite-en-clair.fr décrit.
- **Deux routages du scénario 1 corrigés, chacun avec sa fiche.** Le RAFP
  n'est ouvert qu'aux fonctionnaires civils, aux magistrats et aux militaires
  (loi n° 2003-775, article 76, II ; page « Actif » de l'ERAFP) : le routage le
  donnait depuis 2005 aux ouvriers de l'État, ce que la fiche
  `rafp_assiette_plafond` signalait déjà ; il ne le fait plus
  (`rafp_beneficiaires`). Les membres du CESE entrés en fonction depuis le 1er
  septembre 2023 relèvent du régime général et de l'Ircantec (loi n° 2023-270,
  article 1er, VI, 4° et 14°, et IX ; L. 921-2-1 ; base de connaissance de
  l'Ircantec), non de l'Agirc-Arrco : le statut qui relève le leur est
  désormais l'agent non titulaire (`cese_affiliation_2023`), et c'est vers lui
  que le formulaire renvoie. Aucun total ne bouge ; un ouvrier né en 1970, à
  20 % de primes, perd les 1 244,88 € de RAFP que le site lui servait à part.
- **Deux complémentaires lues, non routées.** Celle des mineurs est
  l'Agirc-Arrco (le même schéma ; la CARCOM, « Régime : AGIRC-ARRCO », créée le
  25 avril 1961 ; le protocole UNIRS–Charbonnages du 25 avril 1960, par le titre
  de l'arrêté du 6 novembre 1967). Routée à l'essai comme celle des salariés
  agricoles, elle était servie dès le départ du mineur, à cinquante ou
  cinquante-cinq ans, sans abattement ; or la circulaire Agirc-Arrco
  2020-02-DRJ (fiche 3, I.1.3.1) ne la sert au mineur de fond sans abattement
  qu'à soixante ans, et l'ANGDM verse entre les deux des « allocations
  anticipées de retraite complémentaire » (décret n° 2004-1466, article 2, 3°)
  dont le montant n'est pas lu. L'essai est retiré, et le `manque` des mines
  le dit. Celle des chemins de fer secondaires est créée à compter du 1er
  janvier 1955 par le décret n° 54-1061 du 30 octobre 1954, qui complète
  l'article 4 du décret n° 54-953 — et non par ce dernier, comme l'écrivaient
  la fiche et la note du 27, qui suivaient le titre du décret n° 55-1297 ; elle
  ne vise que les embauchés d'après le 1er octobre 1954. Ses règles sont lues
  au Journal officiel du 4 octobre 1955, sa valeur du point et son salaire de
  référence ne le sont pas : elle n'est pas routée. Chemin faisant : l'article
  4 du décret n° 54-953 laisse à la caisse autonome mutuelle les agents
  embauchés avant le 1er octobre 1954, que le routage passe au régime général
  en 1955 ; le `manque` le dit.

**Ce qu'il déplace.** Aucun total des quatre systèmes : la ligne de RAFP des
ouvriers de l'État, nulle dans les témoins faute de primes ; le statut vers
lequel le formulaire renvoie un membre du CESE entré depuis 2023 ; les listes
de statuts et les `manque` de la page Méthode.

**Ce qui reste, à cette date.**

- Router la complémentaire des mineurs demande qu'une complémentaire puisse
  être servie plus tard que la pension de base : une décision du moteur et de
  la page — que vaut le système 1 entre cinquante-cinq et soixante ans ? —,
  posée au propriétaire. Viendraient ensuite le routage, sur les taux de
  l'Arrco comme pour les salariés agricoles, faute de ceux de la CARCOM, et ce
  que servent les allocations de l'ANGDM ; les régimes des ETAM (CAREM, 1948 à
  1970) et des ingénieurs restent à distinguer.
- Chemins de fer secondaires : lire la valeur du point et le salaire de
  référence de leur caisse complémentaire (arrêtés de 1955 et 1956) et son
  adhésion à l'Arrco, puis la router ; lire la caisse autonome mutuelle
  d'après 1954 et y garder les agents embauchés avant le 1er octobre 1954.

### 135. Aller plus vite sans rien céder : l'outillage d'un changement de résultats — `en cours`

**Reprise, au 17 octobre 2026.** Fait : les leviers 1, 2 et, pour
l'essentiel, 3 ; le hook de démarrage ; « Économiser le contexte » ; l'arbre
du dépôt ; le parcours `tenu` ; le contexte en cinq étapes ; la mémoire
indexée sur le seul modèle ; `pousser.sh` publie une tête détachée ;
`node --test` sauté quand rien de ce qu'il lit n'a bougé, les cumuls au
hasard et le portage du coût (notes du 16) ; la lecture confiée à Haiku,
`consommation.py` par modèle, le skill `claude-api` du dépôt (note du 17).
Reste : `actions/cache` sur GitHub, le modèle et l'effort des sessions, que
le propriétaire décide ; la part de l'éclaireur, à relever ; du portage
rejoué, les pages au hasard, que la session des pages tient ; le 4 et 5.

**Demande**, le 28 septembre 2026, l'action 132 close : « On passe un temps
interminable à faire ces changements. Pourquoi ? Est-ce qu'on peut aller plus
vite sans dégrader la qualité ? », puis, le diagnostic lu : « Vas-y ».

**Le diagnostic, sur l'action 132.** La règle elle-même a pris peu de temps ;
tout le reste est allé à ce qui bouge avec elle. Environ 150 lectures de la
naissance en Python et 130 dans le portage, triées deux fois. Près de
90 tests en échec, parce qu'ils écrivent en dur un montant ou une date, et
chacun demandait une décision. Des approximations anciennes révélées, dont
une partie corrigée sur place. Environ cinq passages de la suite complète, de
huit minutes chacun, et quatre régénérations de sept ou huit commandes, les
corrections venant par vagues. Six commits d'autres sessions sur les mêmes
fichiers, et douze conflits.

**Les cinq leviers**, dans l'ordre où ils se prennent :

1. Un script qui régénère tout, et un qui résume ce que les témoins ont
   bougé. Fait, ci-dessous.
2. Des tests qui ne dépendent pas des présomptions : un test qui raconte une
   date déclare la date entière, et les chiffres exacts du modèle vivent dans
   les témoins, relus en bloc, pendant que les tests tiennent les règles.
3. Une régénération et une suite plus rapides, en commençant par les chiffres
   ancrés (mesures ci-dessous) : ce que plusieurs fichiers de tests et les
   sondes de la prose recalculent — le coût agrégé surtout — se garde d'un
   calcul à l'autre, comme les lois de mortalité le sont déjà
   (`data/derive/calibrations_mortalite.json`), ou se calcule en parallèle.
4. Le parcours de présentation, que son test fait suivre les pages et que le
   contrôle de conservation gèle comme un récit : à chaque changement des
   pages, sa référence se refige avec `--accepter-les-pertes`, comme à
   l'action 132. Le déclarer autrement.
5. Un changement transversal passe seul, sans autre session sur les mêmes
   fichiers. C'est une règle du partage entre sessions, que le propriétaire
   décide.

**Fait, le 28 septembre : les deux scripts.**

- `scripts/regenerer.py` lance tout ce qu'un script fabrique, en trois
  temps : l'inventaire et le document des régimes ; puis, ensemble, le paquet
  suivi des témoins, le chiffrage et les tableaux du README, qui ne se lisent
  pas ; enfin le tableau de bord, les chiffres ancrés et le contrôle de
  conservation, qui ne fait que contrôler. `--verifier` passe chaque étape en
  mode vérification et les dit toutes au lieu de s'arrêter à la première ;
  `--prose` ne relance que le dernier temps, quand seuls les documents ou les
  registres ont changé ; `--sequentiel` enchaîne les branches ; `--etapes`
  les liste. La recette de `CLAUDE.md` et le commentaire de `.gitattributes`
  y renvoient ; un test tient que chaque fichier que `.gitattributes` déclare
  fabriqué a son étape.
- `scripts/resumer_temoins.py` dit, depuis une révision (`--depuis`, HEAD par
  défaut), combien de témoins bougent et, scénario par scénario, combien de
  pensions, de combien en médiane, lesquelles le plus (`--extremes`), et
  quels rendus de page changent, au format de la prose, prêt pour un message
  de commit. Sur le commit de l'action 132, il redonne en une seconde le
  tableau que la session avait calculé à la main.
- `tests/test_outillage.py` les tient, sans lancer un calcul du modèle.

**Mesuré le même jour**, chaque étape en mode vérification : l'inventaire,
2 s ; le paquet, 44 s ; les témoins, 50 s ; le chiffrage, 41 s ; les tableaux
du README, 3 s ; le tableau de bord, 5 s ; les chiffres ancrés, 178 s ; la
conservation, 2 s. Le tout prend 4 min 41 s, contre 5 min 26 s enchaîné :
le parallèle ne gagne que les 45 s du chiffrage, parce que les chiffres
ancrés, qui viennent en dernier, font à eux seuls les deux tiers du temps. Le
profilage dit pourquoi : 85 % de leur durée passe à recalculer le coût agrégé
sept fois, sous sept jeux de réglages (`mesures_prose._cout`), une fois par
processus. C'est le premier morceau du levier 3.

**Fait, le 28 septembre : les chiffres ancrés, premier morceau du levier 3.**
Leur contrôle passait 85 % de son temps à recalculer sept variantes du coût
agrégé et le coût des avantages, une vingtaine de secondes chacun, à chaque
passage, même quand rien n'avait bougé. Deux mécanismes, dans
`scripts/mesures_prose.py`, dont aucun ne change un chiffre :

- une mémoire sur le disque, `.cache/mesures_prose/<empreinte>/`, que git
  ignore. L'empreinte est celle de tout ce que git voit sous `src/`, `data/`
  et `scripts/`, octet par octet, et de la version de Python : qu'un de ces
  fichiers bouge, et tout se refait ; un calcul pendant lequel l'un d'eux a
  bougé ne se garde pas ; les quatre empreintes les plus récentes restent.
  `MESURES_SANS_MEMOIRE=1` s'en passe ;
- un précalcul, le temps d'un contrôle (`mesures_prose.campagne`, où
  `verifier_prose.controler` se place) : les mesures se lancent une première
  fois pour dire les calculs lourds qu'elles attendent, qui se font ensemble,
  un processus neuf par cœur, pendant que les mesures légères se calculent ;
  chaque mesure ne se calcule qu'une fois par contrôle. `MESURES_PROCESSUS=1`
  fait tout à la demande, comme avant.

`verifier_prose.py` garde en plus, d'une ancre à l'autre, les YAML qu'il
analyse. Les 417 mesures que la prose cite rendent les mêmes 417 nombres, au
bit près, par l'ancien chemin, à froid, à chaud et hors d'une campagne ;
`tests/test_outillage.py` tient la mécanique sur des calculs factices, et
qu'un processus neuf retrouve le module.

**Mesuré.** Le contrôle des chiffres ancrés passe de 178 s à 53 s quand le
modèle, ses données ou les scripts ont bougé, et à 16 s sinon. Son test, le
plus long de la suite, passe de 175 s à 53 s et 16 s quand il tourne seul ;
dans la suite complète, où les autres fichiers occupent les cœurs, il prend
90 s à froid. La suite complète passe de 7 min 56 s à 6 min 53 s quand la
mémoire sert, et entre 7 min 25 s et 7 min 45 s sinon ; `regenerer.py --verifier`, de 4 min 41 s à
1 min 55 s quand la mémoire sert.

**Mesuré et écarté : libyaml.** Le PyYAML de ce conteneur est celui de
Debian, construit sans libyaml, et `donnees/chargement.py` s'y rabat sur le
chargeur Python. Les 274 YAML du dépôt se lisent à l'identique par les deux,
huit fois plus vite par le chargeur C ; mais la suite complète n'y gagne rien
(7 min contre 6 min 53 s), parce que la mémoire de `charger_yaml` fait
déjà qu'un fichier ne s'analyse qu'une fois par processus. Seuls le contrôle
de la prose (16,5 s contre 13,4 s) et la suite rapide (18 s contre 16 s) le
sentiraient.

**Le reste du levier 3**, par ordre de gain :

- les fichiers de tests de la page Coût recalculent chacun leurs coûts : la
  mise en place de `test_cout_age_depart.py`, 112 s, est désormais le plus
  long de la suite ; `test_cout.py` a dix tests de plus de 18 s ;
  `test_solde_fusion.py`, `test_garantie_par_sexe.py`,
  `test_proposition_prospective.py` et `test_stock_age_legal.py` mettent en
  place les leurs en 20 à 41 s. Une mémoire commune des coûts, que chaque
  test demande là où rien du modèle n'est remplacé — jamais sous
  `PropositionProspective`, qui en remplace des fonctions —, les ramènerait à
  la lecture d'un fichier ;
- le chiffrage (39 s dans la suite, 41 s dans la régénération) calcule deux
  fois le coût agrégé, dont la variante par défaut que la mémoire des
  chiffres ancrés garde déjà : la lire par `mesures_prose._cout()` en
  économiserait la moitié ;
- les témoins et le paquet, 43 et 40 s, qui se vérifient en se refaisant.

**Fait, le 28 septembre : une mémoire commune des calculs lourds, second
morceau du levier 3.** Un greffon de mesure a relevé, pendant une suite
complète, chaque calcul du coût agrégé et du coût des avantages : 55 calculs,
dix-sept minutes de calcul en tout, dont près des deux tiers refaisaient un
calcul déjà fait. Le coût de la page Coût y était calculé vingt fois, dans neuf
fichiers et quatre processus ; celui des avantages huit fois, dont cinq dans le
même processus. Chaque fichier gardait le sien dans une fixture, et aucun ne
pouvait prendre celui d'un autre.

- `src/retraite_notionnelle/memoire.py` garde ces calculs dans
  `.cache/calculs/<empreinte>/`, sous leur clé — paramètres, options défaut
  compris, grille de cas types — et sous l'empreinte des sources, comme la
  mémoire des chiffres ancrés, qu'elle remplace (`CALCULS_SANS_MEMOIRE=1`
  s'en passe). `memoire.cout(parametres, …)` et `memoire.avantages(parametres)`
  construisent eux-mêmes le simulateur et les données de leur calcul ; chaque
  lecture rend un objet neuf ; une copie des données ailleurs que dans le dépôt
  se calcule sans mémoire ; un calcul fait après qu'un fichier Python des
  sources a changé ne se garde pas, parce que le processus a peut-être calculé
  avec l'ancien code.
- La mémoire ne connaît que le modèle intact. Les trois contextes qui en
  remplacent des fonctions — la proposition prospective, le stock à l'âge
  légal, le régime unique — la font taire tant qu'ils sont ouverts
  (`memoire.modele_modifie()`), et `tests/conftest.py` fait de même sous
  `monkeypatch` ; `memoire_isolee` la rouvre, dans un dossier à lui, pour ses
  propres tests.
- Y passent : les fixtures et les calculs de `test_cout.py` (treize), de
  `test_avantages.py` (cinq), de `test_solde_fusion.py`,
  `test_stock_age_legal.py`, `test_garantie_par_sexe.py` ; le coût de
  `chiffrage_plf.py`, de `postes_ecartes.py`, de `garantie_par_sexe.py`, de
  `cout_age_depart.py` avec ses deux recherches d'âges ; le coût prospectif,
  désormais un calcul gardé de `proposition_prospective.py`
  (`proposition_prospective.cout`), que le chiffrage partage ; les chiffres
  ancrés, dont le précalcul ne confie plus à ses processus que ce que la
  mémoire n'a pas.

**Mesuré.** La suite complète passe, quand la mémoire sert, de 6 min 53 s à
3 min 57 s — elle en prenait 7 min 56 s avant l'action ; quand la mémoire est
vide, de 7 min 25 s au mieux à 6 min 17 s, mesuré avant que les recherches
d'âges y passent. Le contrôle du chiffrage passe de 40 s à 0,3 s, et le
document qu'il produit est le même par les deux chemins ;
`test_cout_age_depart.py`, de 153 s à 15 s.

**Ce qui reste du levier 3**, par ordre de gain mesuré sur la suite chaude :

- le `Contexte` du site (`contexte.py`), que les tests des pages, des
  affirmations et du portage lisent, et qui calcule encore ses coûts lui-même :
  près de trois minutes de calcul du coût, selon le relevé, et les plus longs
  tests de la suite chaude. Le faire passer par la mémoire demande de
  s'assurer d'abord qu'aucun test ne remplace une fonction du modèle, à la
  main et sans `monkeypatch`, avant d'y lire un coût : `test_affirmations.py`,
  `test_capitalisation.py`, `test_droit.py` et `test_liquidation.py` le font,
  pour d'autres calculs ;
- les résultats des scripts calculés sous leur contexte, le régime unique
  (`test_solde_fusion.py`, 58 s de mise en place) et le stock à l'âge légal
  (40 s), qui se gardent comme le coût prospectif, le contexte ouvert dans le
  calcul ;
- les contrôles du paquet et des témoins, 44 et 43 s, qui se refont en entier ;
- la répartition des tests : xdist distribue un à un les tests d'un même
  fichier, et deux processus calculent ensemble la même fixture de module,
  ce que la mémoire ne rattrape pas quand elle est vide (`--dist loadgroup`,
  pour les fichiers qui ont une fixture lourde) ;
- sur GitHub, où chaque exécution part sans mémoire : la garder d'une
  exécution à l'autre (`actions/cache`, sous l'empreinte des sources).

**Fait, le 28 septembre : le contexte du site passe par la mémoire.**
`Contexte.cout()` et `Contexte.avantages()` — ce que lisent, en Python, les
tests des pages (`test_web.py`), les affirmations (`test_affirmations.py`), le
portage du coût (`test_cout.py`) et le paquet (`construire_donnees.py`) —
demandent leur calcul à `memoire.cout(self.base)` et
`memoire.avantages(self.base)`, qui bâtissent le même simulateur et les mêmes
données, avec les comptes du COR du scénario de projection des règles, comme
le contexte ; les affirmations y lisent aussi leur coût sous la convention
« rapport ». Avant cela, les quatre fichiers de tests qui remplacent une
fonction du modèle à la main, sans `monkeypatch`, ont été relus :
`test_affirmations.py` et `test_capitalisation.py` le font pour une carrière
ou un pilier, `test_droit.py` et `test_liquidation.py` pour épier, sans les
changer, les simulations d'une saisie — comme `scripts/budget_calcul.py` ;
aucun ne lit un coût sous son remplacement. Le coût que le site calcule en
JavaScript, dans node, ne passe pas par la mémoire.

**Mesuré.** La suite complète passe de 3 min 57 s à 3 min 9 s quand la
mémoire sert, et de 6 min 17 s à 5 min 20 s quand elle est vide ;
`regenerer.py --verifier`, de 1 min 55 s à 1 min 33 s, le paquet s'y vérifiant
en 24 s au lieu de 44 s. Depuis le début de l'action : la suite, de 7 min 56 s
à 3 min 9 s ; la régénération vérifiée, de 4 min 41 s à 1 min 33 s.

**Ce qui reste**, par ordre de gain sur la suite chaude : les résultats du
régime unique et du stock à l'âge légal, calculés sous leur contexte (58 s et
42 s de mise en place), à garder comme le coût prospectif ; les témoins,
37 s, et le portage que node rejoue, 27 s ; puis la répartition des tests par
xdist et la mémoire sur GitHub, comme dit plus haut.

**Fait, le 28 septembre : le régime unique et le stock à l'âge légal gardent
leurs résultats.** `solde_fusion.calculer(hypothese, parametres, …)` et
`stock_age_legal.calculer(variante, parametres)` ne prennent plus que leurs
réglages et les paramètres, bâtissent eux-mêmes simulateur et données, et
rendent un calcul gardé : le contexte qui remplace les fonctions du modèle
s'ouvre DANS le calcul que la clé nomme — l'hypothèse ou la variante, les
paramètres, les conventions —, comme pour le coût prospectif. Les résultats
relus du disque sont égaux, au bit près, à leur calcul direct, lectures,
pensions et couples touchés compris ; leurs tests passent de 95 s à 3 s quand
la mémoire sert.

**Mesuré.** Les deux mises en place disparaissent de la suite chaude, soit une
centaine de secondes de calcul ; la suite, elle, prend 3 min 13 s, puis
2 min 36 s au passage suivant, sans rien changer : son temps tient désormais à
la répartition des tests entre les processus plus qu'à leur calcul. Sur ce
dernier passage, les tests calculent 519 s en tout, dont 203 s pour
`test_web.py` — les témoins (41 s), le portage que node rejoue (27 s), le
paquet (24 s) —, 75 s pour `test_cout.py` et 44 s pour `test_prose.py`.

**Ce qui reste**, par ordre de gain : `test_web.py` et ce que node y
recalcule ; dans `test_cout.py`, le coût sous l'ancienne convention des
cotisants (20 s, sur un simulateur retouché, que la mémoire ne sait pas
décrire) et le refus d'une pondération inconnue, qui ne tombe qu'après 17 s
de calcul ; les grilles de départs de `test_age_conjoncturel.py` et
`test_age_depart_csp.py` (19 et 17 s de mise en place), à garder comme les
recherches d'âges ; puis la répartition des tests et la mémoire sur GitHub.

**Le 30 septembre 2026, à la demande du propriétaire, qui trouvait le travail
plus lent et plus coûteux qu'avant.** Trois retouches, sans aucun résultat
déplacé. Un fichier visé seul se répartit sur les cœurs quand il est lourd
(`POIDS_REPARTI`, dans `pytest_parallele.py`) : `test_web.py`, visé seul,
tenait près de quatre minutes en série. La marque `site` rassemble le filet
d'une retouche des pages ou de la saisie — le budget de mots, les bornes
opposables, les pages figées et leur portage, le catalogue des affirmations —,
sept tests en une minute, là où la suite complète les montrait au bout de
cinq. `test_web.py` est découpé en trois, avec `test_web_saisie.py` et
`test_web_revues.py`, qui partagent `outils_web.py` et, par processus, le
contexte et les pages rendues : la suite complète passe de quatre minutes et
demie à trois trois quarts. Les pages figées ne gardent le formulaire entier
que là où il est le sujet (`FORMULAIRE_ENTIER`, onze pages) ; les cinquante
autres n'en figent que la balise, et le témoin passe de 11,9 à 8,8 Mo.
CLAUDE.md porte les listes de contrôle d'une retouche des pages, d'un champ de
saisie et d'un changement du modèle.

**Le même jour, la documentation allégée**, sur la décision du propriétaire :
une note de feuille de route par étape, une version de l'architecture par
domaine clos ou par décision, les fiches et `limites.md` une fois par étape,
des messages de commit de cinq lignes au plus (`CLAUDE.md`).

**Le même jour, le cycle d'un commit raccourci.** La régénération garde
l'empreinte de ses étapes lourdes (`fabrique.py`) : refaite sans changement, elle
passe de 149 à 11 s, et de 150 à 75 s après une retouche du site ; la suite ne
revérifie plus ce qu'elle vient de fabriquer, et le vol de tâches
(`--dist worksteal`) la fait passer de près de quatre minutes à deux, mémoire
des calculs chaude. La première suite après une retouche de `src/`, `data/` ou
`scripts/` en tient encore cinq : la mémoire des calculs lourds s'indexe sur
tout le code, et se refait entière. L'indexer sur le seul code du modèle est le
levier suivant.

**Le 1er octobre 2026, le hook de démarrage posé, à la demande du
propriétaire, pour ne plus payer l'installation à chaque session.** Le hook
`SessionStart` de l'action 33, dont le texte attendait dans les archives
faute d'une session qui ait pu écrire sous `.claude/`, est dans le dépôt :
`.claude/hooks/session-start.sh`, inscrit dans `.claude/settings.json`.
L'écriture, cette fois demandée expressément, est passée. Une session web
s'ouvre avec pytest, pytest-xdist, le paquet et un PyYAML qui embarque
libyaml, et ne commence plus par « No module named pytest ». Essayé depuis un
état neuf, ces paquets désinstallés : 6 s, sans erreur, et rien sur la sortie
standard, qui entrerait sinon dans le contexte de la session ; hors d'une
session web, il ne fait rien. Un écart avec le texte archivé : la commande
passe par `bash`, comme celle de `pousser.sh`.

**Le même jour, le hook passe en asynchrone**, à la demande du propriétaire :
la session s'ouvre sans attendre l'installation, qui se fait en arrière-plan.
Le script l'annonce par sa première ligne de sortie,
`{"async": true, "asyncTimeout": 300000}`, et n'écrit plus rien d'autre, pip
compris (`--root-user-action=ignore`). Le prix : un test lancé dans les
premières secondes peut ne pas trouver pytest, et `CLAUDE.md` dit alors de
relancer plutôt que de réinstaller. Essayé depuis un état neuf : 6 s, une
seule ligne sur la sortie standard, rien sur la sortie d'erreur.

**Le même jour, le coût en jetons mesuré, et deux retouches pour le
contenir**, à la demande du propriétaire, qui trouvait qu'on consommait
énormément pour avancer, malgré les tentatives précédentes. Les douze sessions
du 27 septembre au 1er octobre ont coûté environ 1 000 $ en équivalent API,
dont 880 $ pour les six qui ont duré de sept heures à deux jours. Deux tiers
du coût sont la relecture du contexte : chaque appel d'outil relit toute la
conversation, qui montait à 500 000 ou 770 000 jetons dans ces sessions, la
compaction ne venant qu'à 80 % d'un million. Les retouches précédentes
raccourcissaient les tests et l'installation, du temps et non des jetons ; le
dépôt ne pèse qu'environ 6 000 des 70 000 jetons qu'une session porte au
départ. Les leviers sont la durée des sessions, l'effort et le modèle, que le
propriétaire règle, et ce que chaque session lit. D'où, dans `CLAUDE.md`, la
section « Économiser le contexte » — une session par étape, chercher avant de
lire, les sorties longues par `tail`, l'enquête à la mesure de la question —,
et, sous le titre de chaque action en cours, un bloc « Reprise » de dix lignes
au plus, seul à lire au démarrage, que la session qui avance l'action récrit.

**Le 4 octobre 2026, la suite complète sous Windows, à la demande du
propriétaire** : « il faut rendre le plus possible les tests plus rapides […]
la plupart des sessions sont bloquées par la suite complète qui tourne ». Son
poste — quatre cœurs, seize gigaoctets, plusieurs sessions à la fois, chacune
dans son worktree — tenait la suite en dix à vingt minutes, et en cinquante-six,
mesurée à froid dans un worktree neuf pendant que deux autres suites
tournaient. Un greffon de mesure, hors du dépôt — durées par fichier, calculs
gardés, processus lancés, appels à `stat` —, et deux profils du coût agrégé ont
dit pourquoi. Six retouches, sans aucun résultat déplacé : les vingt-cinq
calculs gardés que l'ancien code et le nouveau ont en commun sont égaux au bit
près.

- **Le `stat` de Windows.** Les chargeurs du disque se gardent sur la
  signature du fichier, au prix d'un `stat` à chaque appel : 285 818 par coût
  agrégé, à près de 260 µs sous Windows, le tiers de son temps. Trois
  chargeurs appelés à chaque ligne de chaque carrière — l'assiette minimale
  des indépendants, le chômage des complémentaires, les tables du profil
  salarial — et trois fonctions du profil, qui regroupaient leur table à
  chaque appel, ne s'appellent plus qu'une fois par arguments le temps d'un
  calcul (`chargement.instantane`, qu'ouvrent la construction d'une carrière,
  la simulation, la grille des cas types et chaque calcul gardé) : 26 032
  `stat`, et un coût deux fois plus court. Un calcul voit ses données telles
  qu'elles étaient à son début.
- **Les calculs faits en double.** La recherche d'âges de
  `test_cout_age_depart.py` se faisait trois fois ensemble, une par worker,
  un quart d'heure chacune. Un verrou du système par calcul (`memoire._seul`) :
  qui demande un calcul en cours attend qu'il finisse, puis le relit.
- **Un worktree neuf repartait sans mémoire**, quand le dépôt principal
  gardait, sous la même empreinte, les trente calculs que la suite refaisait.
  `.cache/calculs/` est désormais celui du dépôt principal, commun à ses
  worktrees (`memoire.dossier_commun`), et garde seize empreintes au lieu de
  quatre.
- **Les tests de `pousser.sh`**, chaque git coûtant près d'une seconde sur la
  machine chargée, tenaient le cinquième de la suite chaude. Leur atelier se
  monte une fois par fichier et se copie ; surtout, un fichier isolé — qui ne
  lit rien du modèle, seulement ce qu'il déclare, ici le script — ne rejoue
  plus un cas qui a réussi tant que ni lui, ni le script, ni git n'ont bougé
  (`ISOLES`, dans `tests/conftest.py`) ; visé expressément, il se rejoue.
- **La grille des cas types**, l'essentiel d'un coût agrégé, que chaque
  variante refaisait alors qu'elle ne dépend que des paramètres, des cas types
  et de la liquidation : `memoire.cout` la garde, et la passe à
  `calculer_cout` (`grille_simulee`). Cinq des treize variantes de la suite la
  relisent, et se calculent en six secondes au lieu de cinquante.
- **Ce que des tests refaisaient pour rien** : le contrôle de la prose, que
  quatre tests relançaient ; le refus d'une pondération inconnue, qui tombait
  après la grille ; l'ancienne convention des cotisants dans `test_cout.py` et
  les deux grilles des tests d'âge, désormais gardées par la mémoire des
  calculs.

**Mesuré**, la machine chargée d'autres sessions, ce qui rend chaque chiffre
approché : à froid, la suite passe de 56 min à 14 min ; à chaud, de 10 min
23 s, mesurées après les trois premières retouches, à 6 min 54 s. Les
trente-deux calculs gardés que les deux dernières suites froides ont en commun,
avant et après la grille gardée, sont égaux au bit près. Les trois tests qui
échouent sous Windows à la dernière décimale échouent toujours, et eux seuls.

**Ce qui reste**, par ordre de gain : ces trois tests, qui ne peuvent pas
passer sous Windows et y coûtent quatre minutes de travail par suite — les
sauter hors de Linux, ou y comparer à une tolérance, que le propriétaire
décide ; les tests du portage que node rejoue ; l'indexation de la mémoire sur
le seul code du modèle ; `actions/cache` sur GitHub.

**Le 5 octobre 2026, les trois tests de la dernière décimale, à la décision du
propriétaire** : les comparer à une tolérance hors de Linux, la CI, sous
Linux, restant au bit près. Ils échouaient sous Windows même quand tout était
à jour, et un vrai oubli de régénération y donnait le même message.

- **Le paquet et les témoins** (`test_web.py`). La comparaison octet par octet
  demeure ; si elle échoue hors de Linux, un JSON se compare en structure —
  mêmes clés, mêmes types, mêmes chaînes, les flottants à 10⁻¹² près en écart
  relatif (`_fichier_a_jour`) —, et le test n'échoue qu'au-delà, avec le même
  message. La libm de Windows déplaçait la dernière décimale de 7 · 10⁻¹⁴ au
  plus, le 4 octobre ; le portage, lui, tolère 10⁻⁹.
- **La prose** (`test_prose.py`). Hors de Linux, `portage(identiques)` et
  `portage(pire)` ne dérivent plus (`PROPRES_A_LINUX`) : ce que node retrouve
  au bit près des témoins dépend de la plateforme — ce jour-là, 121 721 valeurs
  sur 130 714 sous Windows, soit 93,1 %, quand la CI comptait tantôt 93,0,
  tantôt 93,1. Une dérive porte désormais sa mesure (`Anomalie.mesure`, dans
  `verifier_prose.py`). `portage(valeurs)`, qui ne compte que les témoins,
  reste tenu partout.
- **La mécanique a ses tests** : un ulp passe ; un écart relatif de 10⁻⁹
  échoue, comme une clé en plus ou en moins, une chaîne, un type ou une liste
  qui changent ; sous Linux, un ulp périme le fichier, et ailleurs seul un
  JSON se compare à la tolérance ; seules les deux mesures du bit près sont
  exemptées, et hors de Linux seulement.

**Mesuré** sous Windows, sans rien régénérer : les trois tests passent —
avant, ceux du paquet et des témoins échouaient, et celui de la prose ne
passait que parce que le README disait 93,1, comme Windows ; il passe aussi à
93,0, le chiffre de la CI des jours d'avant. La suite complète passe sans un
échec : 3 328 tests passés, 12 sautés, en 7 min 37 s.

**Ce qui reste.** Ces trois tests coûtent toujours leur calcul, quatre minutes
de travail par suite : la tolérance les fait passer, pas aller plus vite. Sous
Windows, `regenerer.py` réécrit encore les trois fichiers à la dernière
décimale, et `verifier_prose.py --corriger` les deux mesures du bit près : ce
qu'on y régénère ne se commite toujours pas, la WSL ou HEAD y pourvoient. Puis,
comme le 4 octobre : les tests du portage que node rejoue ; l'indexation de la
mémoire sur le seul code du modèle ; `actions/cache` sur GitHub.

### 137. Les autres modèles publics : le registre exhaustif, puis leur confrontation — `en cours`

**Reprise, au 23 octobre 2026.** Fait : le registre (70 modèles), relu à
l'action 138 ; Destinie 2, TRAJECTOiRE et Ines exécutés à part ; les pistes
du 1er octobre, closes ; les treize modèles « jamais confrontés », remis à
plat (note du 22 octobre) ; modele-as, rejoué sur des revenus de dirigeant
(note du 23 octobre) : les trimestres et les points du dépôt, à deux erreurs
près, les siennes. Le premier qui reste à confronter, dans l'ordre du
registre : Catala, au droit de sa date ; puis le simulateur de SUD éducation
et Nos Retraites. Restent aussi l'Agirc-Arrco d'EDIFIS, l'ASPA de Saphir,
les années 2015 à 2025 d'EUROMOD ; la campagne 2025 de l'EACR, au printemps
2027 (note du 14 octobre) ; les `referents` des fiches, à leur relecture.

**Demande**, le 1er octobre 2026 : « Quels sont les autres modèles publics
autres que openfisca ? », puis : « Ajoute les modèles qui ne sont pas encore
pris dans le dépôt. Je veux qu'on fasse une liste exhaustive. »

**Fait, le 1er octobre 2026 : le registre.** Celui que la note 0001
prévoyait (§ 3.4, annexe B) est né : `data/reference/referents.yaml`. Il
recense 69 modèles, 47 en France et 22 à l'étranger ou dans les
organisations internationales : 32 au code ouvert, un sur demande, 13
documentés sans leur code, 23 non publics. Chacun dit ce qu'il couvre, ce
dont il dépend, sa licence et ce qu'elle permet au dépôt, comment le
confronter, les écarts trouvés, et ce qu'il confronte : le droit réel, la
page Coût ou l'arithmétique de la proposition. Quatre recherches menées en
parallèle l'ont établi — la statistique publique, les caisses et les
ministères, le code ouvert et la recherche, les pays à comptes notionnels —,
chaque fait lu sur sa page le jour même ; le recensement des modèles de
microsimulation du COR (séance du 5 mars 2020) a servi de contrôle : il
n'en nomme aucun, en France, qui n'y soit pas. Le registre des sources reçoit 41 adresses à explorer,
leur accès mesuré par `sonder_sources.py`. Un test tient la forme du
registre, la règle des licences du § 3.4, et ses renvois aux fiches, au
manifeste et au registre des sources ; le tableau de bord le résume.
L'architecture passe en version 5.33. L'action 136, sur
OpenFisca-France-Pension, en est un cas particulier, mené à part.

**Ce que la liste apprend.**

- *Les familles.* Un accord à l'intérieur d'une famille ne vaut qu'une
  confirmation. Les barèmes de l'IPP nourrissent OpenFisca-France-Pension,
  TIL, PENSIPP, TRAJECTOiRE et la moitié des paramètres de retraite
  d'OpenFisca-France. La DREES ne tient qu'une lignée, de CALIPER (2013) à
  TRAJECTOiRE, par calcul_pension, et c'est elle qui calcule les cas types du
  COR. Restent hors de toute famille : Destinie 2, Ines, EDIFIS, EUROMOD,
  Catala, et les lectures de la société civile.
- *Aucune caisse ne publie son moteur.* La Cnav décrit le sien en onze
  fiches, sans formule ; PRISME, Pablo, Canopée, MisrAA, Aphrodite et Osiris
  ne se connaissent que par leurs documents et leurs résultats.
- *Un écart nouveau, au texte.* `legiretraite`, le paquet de paramètres que la
  DREES a ouvert le 7 septembre 2026, garde pour la durée requise des
  générations 1964 et 1965 les valeurs de la loi de 2023, quand ses âges
  suivent la loi du 30 décembre 2025. Celui de Catala, sur l'âge de 1967,
  tient toujours. Ni OpenFisca-France-Pension, ni Destinie 2, ni la version
  publique de TRAJECTOiRE n'ont cette loi ; les barèmes de l'IPP l'ont.
- *PENSIPP a codé une conversion en comptes notionnels pour la France dès
  2013* : la seule autre qui se lise, sans licence, donc sans se copier.
- *À l'étranger*, la Suède publie ses deux outils, pour un usage non
  commercial, et a voté un accélérateur qui rend son frein symétrique (loi
  2026:1301, appliqué pour la première fois à 2027). OG-Core est le seul code
  ouvert établi qui calcule une pension notionnelle.

**Ce qui reste.**

1. Confronter, dans l'ordre que le tableau de bord donne : d'abord ce qui est
   ouvert, jamais confronté et indépendant — Destinie 2 (la réversion, l'ASPA
   et les enfants, que trois fiches attendent), Ines (l'ASPA et les
   prélèvements), `legiretraite` (les âges et les durées), EDIFIS (les taux
   de cotisation) ; puis le diviseur de la proposition contre ceux de la
   Suède, de la Norvège et de l'Italie, refaits depuis leur méthode publiée.
2. Relire la page de la DREES sur CALIPER, et son communiqué de 2021, quand
   le serveur répondra : il ferme la connexion depuis le 22 septembre 2026. Un
   moteur de recherche y lit que calcul_pension en serait la réécriture en R ;
   ce n'est pas retenu, faute de lecture.
3. Les pistes que les recherches n'ont pas vérifiées : le moteur réel de
   M@rel ; l'usage actuel d'Aphrodite, d'Oscar et d'Osiris ; des modèles pour
   les sections libérales, l'IRCEC et la CAVIMAC ; le calcul du Pension
   Adequacy Report ; la Russie, la Mongolie, l'Azerbaïdjan et l'Égypte. Les
   inventaires des « algorithmes publics » d'Etalab et de l'ODAP ne recensent
   rien sur les retraites.
4. Les fiches nomment leurs référents par l'identifiant du registre (le champ
   `referents` du contrat de la fiche) : trois le font ; les autres le feront
   à leur relecture.

**Destinie 2, exécuté à part, le 5 octobre 2026.** Le premier modèle ouvert
confronté par son exécution : dix-huit carrières écrites des deux côtés, ses
sorties figées (`tests/temoins/destinie_2.json`) et rejouées dans le scénario
1 par `tests/test_destinie.py`, sans R. Ce qu'il a montré est au registre
(`destinie_2`, compté désormais parmi les modèles confrontés) et dans la note
de l'étape 4 de l'action 142 ; les trois fiches qui l'attendaient ont leur
réponse.

**TRAJECTOiRE, exécuté à part, le 5 octobre 2026.** Le second : soixante-quatre
cas types du COR, construits par son propre script, et les onze droits directs
de Destinie 2, ses sorties figées (`tests/temoins/trajectoire.json`) et
rejouées par `tests/test_trajectoire.py`, sans R. Le registre (`trajectoire`)
reçoit huit écarts qui sont les siens et un point qu'il fait mieux, la valeur
de service du jour ; neuf fiches ont sa ligne de `referents`. Détail : la note
de l'étape 4 de l'action 142, suite.

### 138. Meilleur en tous points : ce que les autres modèles font mieux, vérifié, puis repris — `en cours`

**Reprise, au 6 octobre 2026.** Fait : l'étape 1 et son relevé (279 points,
145 écarts) ; l'étape 15 ; l'étape 16, sauf les coefficients de l'Agirc d'avant
1955 et de l'Arrco d'avant 1965 (textes de 1947 et de 1961 à trouver) ;
l'étape 2, à trois restes près que dit sa dernière note ; l'étape 20, sauf
l'Ircantec à dater. Restent les étapes 3 à 14 et 17 à 19, et les choix de
l'étape 13. Elles se mènent en parallèle, une session chacune (action 148) :
ce bloc ne se récrit plus ; chaque étape écrit sa note, et son propre bloc tant
qu'elle n'est pas finie, sous `docs/feuille_de_route/138/` (`python
scripts/reprise.py 138`). Le registre dit, au chantier de chaque étape
(« 138.16 »…), ce qu'en fait chaque modèle.

**Demande**, le 1er octobre 2026 : « J'aimerais qu'on regarde les modèles de
simulation qui existent et qu'on les compare à notre projet. Il faut que l'on
regarde quels points les modèles font mieux que nous. Lorsque les modèles font
mieux que nous, il faut vérifier (des erreurs peuvent toujours exister) et
ensuite implémenter avec ce qui se rapproche le plus de la réalité. […] Je
souhaite que mon modèle soit meilleur en tous points aux modèles existants. »

**Fait, le 1er octobre 2026 : l'étape 1, le relevé.** Sept recherches menées
en parallèle, une par famille du registre — les microsimulations dynamiques au
code ouvert, les projections du COR et des caisses, les calculateurs des
administrations, les simulateurs de la société civile, la microsimulation
statique et les barèmes, les comptes notionnels nordiques, les autres comptes
notionnels et les organisations internationales —, chacune lisant le code au
commit ou le document le jour même ; R manquant au conteneur, aucun modèle n'a
été exécuté. OpenFisca-France-Pension, que l'action 136 avait relevé, y entre
par ses points. Le registre reçoit un champ, `fait_mieux` : 94 points chez
52 modèles — 82 à reprendre, 9 à trancher, 2 repris, 1
écartés —, et 28 écarts nouveaux, les erreurs trouvées chez les autres. Un
test exige de chaque point sa preuve et son chantier, ou sa raison ; le
tableau de bord les compte. L'architecture passe en version 5.34.

Deux corrections sont faites dans la même étape, parce qu'elles sont petites
et sûres :

- *Le préfinancement rendu.* Un diviseur actualisé à ν sert d'avance un
  rendement de ν par an ; la pension servie le rend, revalorisée au taux du
  compte divisé par 1 + ν. C'est la règle suédoise, « l'indice de revenu
  nouveau sur l'ancien, divisé par 1,016 » (Pensionssystemets årsredovisning
  2025, note 6), et la grecque. Le dépôt la revalorisait au taux plein, contre
  la promesse de son diviseur, « à espérance de coût inchangée ». Au défaut,
  ν = 0 : aucun témoin ne bouge. Deux tests, l'un Python, l'autre JavaScript.
- *Des descriptions fausses.* La masse salariale n'est le taux d'indexation
  que des comptes polonais et lettons — la loi polonaise prend les prix
  majorés de la croissance réelle de la somme des cotisations (art. 25) ; la
  Suède indexe sur le revenu moyen, l'Italie sur le PIB nominal lissé (README,
  page Méthode). L'Italie ne « partage » pas le capital du défunt : elle
  tarife la réversion dans son coefficient, 1,460 des 19,049 années de rente
  de son diviseur à 65 ans (`cout.py`, `limites.md`). Un système notionnel
  réel laisse parfois dormir un excédent : la Suède l'a fait jusqu'à son
  accélérateur de 2026 (`limites.md`). Le lissage sur cinq ans n'est pas la
  règle italienne, qui prend les cinq années qui précèdent et interdit un
  coefficient sous un, sauf rattrapage (loi n° 335 du 8 août 1995, art. 1er,
  al. 9 ; `config.py`, `methodologie.md`). Le tableau de bord ne dit plus que
  le modèle ne calcule aucune réversion : il en calcule une pour une
  personne, et c'est la page Coût qui n'en lit que la part publiée. La page
  Méthode perd aussi une coquille, « alors que les le système 2 ».

**Ce que le relevé apprend.**

- *Sur l'essentiel, aucun modèle ne fait mieux.* Aucun ne couvre autant de
  régimes ni d'époques ; parmi les modèles français, seuls les barèmes de
  l'IPP ont la loi du 30 décembre 2025 ; Destinie 2, TRAJECTOiRE,
  legiretraite, Catala et les simulateurs militants portent des erreurs que le
  dépôt n'a pas, désormais au registre. Le diviseur du dépôt est plus exact
  que ceux de la Suède, de la Norvège, de l'Italie et de la Pologne — une
  table de génération contre une table du moment : à la suédoise, 6 % de
  pension en trop à 65 ans en 2025 —, et sa formule redonne au millionième le
  coefficient d'espérance de vie finlandais de 2024.
- *Le dépôt a tort sur quatre points du scénario 1*, qu'une recherche a
  trouvés et que la session a relus :
  1. la validation des trimestres de 1949 à 1971 : R. 351-9
     (LEGIARTI000053335598) les compte au « montant trimestriel de
     l'allocation aux vieux travailleurs salariés au 1er janvier de l'année
     considérée » ; le dépôt valide quatre trimestres à toute année travaillée
     avant 1972 (`donnees/macro.py`, `trimestres_valides`). Le tableur de
     vérification Cnav-MSA le fait juste ;
  2. le minimum vieillesse d'avant 2007, que le dépôt déflate sur les prix
     depuis le montant de 2006 : 1 195 € au lieu de 457 € en 1970, selon les
     barèmes de l'IPP, l'écart passant sous 3 % en 1985 ;
  3. le net : 9,1 % retirés à tous, ASPA comprise, quand la DREES compte
     22,1 % de retraités de droit direct exonérés de CSG, 13,4 % au taux
     réduit et 21,6 % au taux médian (la table des prélèvements sociaux de
     l'EACR, source Ancetre 2024, lue dans le paquet `legiretraite`) ; l'ASPA
     n'est pas prélevée, et exonère la pension de qui la reçoit
     (L. 136-1-2) ;
  4. l'ASPA d'un couple, servie au barème d'une personne seule sans les
     ressources du conjoint, que la saisie demande pourtant (L. 815-9).
- *Ce que d'autres savent faire et que le dépôt ne fait pas* : la réversion du
  régime général entière (Destinie 2) ; la PMR des exploitants et le
  complément de la RCO (calcul_pension, barèmes de l'IPP) ; la dépense
  décomposée comme le COR, avec les retraités projetés par régime, ce qui
  localiserait les trois points de PIB qui séparent en 2070 la page Coût du
  COR ; les variantes démographiques de l'INSEE ; l'effet retour d'une baisse
  des pensions sur l'ASPA et la CSG (l'IPP l'estime à 20 à 25 % de
  l'économie) ; les indicateurs de cycle de vie (TRAJECTOiRE, OCDE) ;
  plusieurs âges de départ côte à côte (M@rel) ; la trace d'un calcul
  (Publicodes, Catala, et OpenFisca à l'action 136).
- *Ce que la proposition doit trancher*, parce que l'arithmétique étrangère le
  fait et que le programme n'en dit rien : l'étape 13.

**Les étapes**, dans l'ordre, chacune valant seule ; le registre cite chacune
par son chantier (« 138.2 »…) :

1. Le relevé, et ses corrections immédiates. *Fait, le 1er octobre 2026.*
2. Le net du foyer et l'ASPA du couple, au scénario 1 et sur le site : la CSG,
   la CRDS, la CASA et le 1 % des complémentaires selon le revenu fiscal de
   référence — celui de N−2, le lissage par N−3, les parts selon le conjoint,
   l'abattement de 10 % —, l'exonération des allocataires de l'ASPA, les
   non-résidents ; l'ASPA du couple, son plafond et les ressources du
   conjoint. Sources : L. 136-8, L. 136-1-2, L. 137-41, D. 242-8 et D. 242-9,
   L. 815-9, D. 815-2, R. 815-29, fiches F2971 et F16871. Confrontations :
   OpenFisca-France, Ines, `retraites_2027`, et la répartition des taux de
   l'EACR.
   *Décidé le 4 octobre 2026 par le propriétaire* : le 1 % maladie des
   complémentaires s'applique au scénario 1, au taux plein comme le reste,
   ce que fait « Mon estimation retraite » ; il pèse environ 1 % de
   l'Agirc-Arrco, 0,25 à 0,5 % de la pension. Les cinq autres scénarios
   appliquent à leur pension brute le taux de la personne au scénario 1,
   soit 9,1 % plus 1 % de sa part complémentaire : le net s'y compare comme
   le brut, et seul le calcul de la pension les sépare. C'est une
   hypothèse, « la réforme ne change pas vos prélèvements », que la page
   dit, non une règle de la proposition ; si celle-ci fixe un jour son
   prélèvement maladie, ce sera une couche. Elle remplace, le même jour,
   l'option B — le 1 % sur la part de la pension notionnelle venue d'une
   complémentaire —, écartée parce qu'elle faussait la comparaison : il
   fallait y trancher les anciens fonctionnaires après la bascule et les
   18 % du scénario 6. À faire : la fiche du 1 %, lue sur Légifrance, et
   le paragraphe de `prelevements_remuneration.yaml` qui l'écartait ; la
   part complémentaire de la pension du scénario 1 ; le net, un taux
   unique aujourd'hui (`tauxPension`, `contexte.js`, et son jumeau
   Python), qui devient celui de la personne. Peut se faire seul, avant le
   reste de 2.
   *Fait le 4 octobre 2026.* La cotisation est lue (D. 242-8,
   LEGIARTI000037456300 ; L. 131-2, 1°, LEGIARTI000047453476 ; le tableau de
   l'Urssaf), sa fiche est `cotisation_maladie_pensions_complementaires`, et
   ses quatorze régimes sont dans `prelevements_remuneration.yaml`.
   `Montants` porte le taux de la personne (9,35 % pour une non-cadre au
   salaire moyen) ; les étages du scénario 1 et les lignes de réversion
   paient chacun celui de leur régime ; la saisie d'une pension nette compare
   des nets à chaque tour. Les points d'Ines et de devcrafting_retraites sont
   repris. Reste de 2 : le net selon le revenu fiscal du foyer, l'ASPA du
   couple.
   *Le net du foyer, fait le 5 octobre 2026.* La tranche de CSG suit le
   revenu fiscal de référence (L. 136-8, LEGIARTI000054336623 ; L. 136-1-2,
   II 1° ; D. 242-9 ; CGI, art. 158, 5 a), comme l'étape 13 l'a tranché : le
   champ facultatif `revenu_fiscal`, dans les options de modélisation, ou la
   présomption `aucun_autre_revenu_que_ses_pensions` — la pension du système
   1 et les ressources du conjoint, abattues de 10 % —, une part, deux avec
   un conjoint. La CRDS, la CASA et le 1 % suivent la tranche ; l'allocataire
   de l'ASPA n'est prélevé de rien ; les cinq autres systèmes gardent le taux
   du système 1, et l'estimation officielle nette chaque âge à sa tranche.
   Fiche `csg_des_pensions_selon_le_revenu`. Au salaire moyen, la pension
   passe du taux plein au taux médian ; au SMIC, elle n'est plus prélevée.
   Reste de 2 : l'ASPA du couple, puis les non-résidents (L. 131-9).
   *Les non-résidents, faits le 5 octobre 2026.* Le propriétaire : « je veux
   que tu prennes la législation ». Hors de France, ni CSG, ni CRDS, ni CASA
   (L. 136-1, présomption `domicile_fiscal_au_pays_de_residence`) ; si la
   France prend en charge les soins (L. 160-3 : sous les règlements
   européens, quand l'État de résidence ne sert pas de pension ; ailleurs,
   quinze années d'assurance française), 3,20 % sur la base du régime
   général et 4,20 % sur la complémentaire (L. 131-9 ; D. 242-8). Fiche
   `cotisation_maladie_des_non_residents`. Reste de 2 : l'ASPA du couple,
   dont le plafond n'est au dépôt que pour 2026.
   *L'ASPA du couple, faite le 5 octobre 2026.* Le scénario 1 sert le
   barème du foyer : à qui déclare un conjoint, à compter du mariage, le
   plafond du couple sur les pensions de l'assuré et les ressources du
   conjoint (L. 815-9 ; D. 815-2, qui l'égale au montant de deux
   allocataires) ; la moitié de ce qui manque quand le conjoint a lui aussi
   65 ans, chacun en recevant autant (D. 815-1, b ; R. 815-28) ; tout ce qui
   manque sinon, au plus le montant d'une personne seule (D. 815-1, a). Un
   conjoint qui ne dit pas ses ressources n'en a aucune (présomption
   `ressources_du_conjoint`, comme le formulaire l'annonçait déjà). La
   série du couple, que le dépôt n'avait que pour 2026, va de 2006 à 2026 :
   six ancres lues dans le b) de D. 815-1 et certifiées
   (`dila_legi_minimum_vieillesse.py`), quinze transcrites du barème de la
   Cnav (`cnav_minimum_vieillesse.py`, qui refuse d'écrire s'il ne redonne
   pas au centime les quinze montants de l'article) ; une ancre par année,
   le montant en vigueur au 31 décembre ; 2026 vaut 19 442,21 € par an, non
   douze fois 1 620,18 €. Les trois cas de la fiche F16871 sont reproduits
   au centime — un couple de 1 000 € par mois reçoit 620,18 €, 310,09 €
   chacun —, et deux témoins entrent (`aspa_couple_*`) ; aucune pension des
   735 autres ne bouge, aucun des quatorze qui déclarent un conjoint ne
   passant sous le plafond du couple. Fiche `minimum_vieillesse`, relue ;
   les points d'OpenFisca-France, de Destinie 2, d'Ines et de Saphir sont
   repris, celui de l'IPP pour le couple seulement.
   Reste de 2 : la série d'une personne seule — 2008, 2013 et 2015 qui
   manquent, 2014 au montant d'octobre, 2022 à celui de janvier, douze fois
   le mensuel depuis 2021 (12 523,08 € au lieu de 12 523,14 €) —, que le
   même barème donnerait, mais dont le 1 043,59 € affiché passerait à
   1 043,60 € : à décider ; les ressources de l'assuré hors de ses pensions
   et l'abattement des revenus d'activité (R. 815-29) ; la relecture des
   points du registre au chantier 138.2 sur la CSG et le net, encore
   `a_reprendre` bien que le net du foyer soit fait.
3. La page Coût décomposée comme le COR : les retraités projetés par régime
   (le classeur du COR), la décomposition dépendance × couverture × pension
   relative confrontée au COR de juin 2026 et à l'Ageing Report de 2024, la
   part des reportés en emploi lue à l'INSEE au lieu du plafond de un, la CSG
   effective (CCSS), le « tax gap », le « pension gap » et le levier de l'âge,
   les contrôles d'Ancetre.
4. La réversion du régime général entière : minimum et maximum, majoration de
   11,1 %, plafond de ressources du ménage, partage entre ex-conjoints, décès
   avant le départ, enfants (D. 353-1, L. 353-3, L. 353-6, D. 353-4,
   R. 353-1-1, et la circulaire de la Cnav) ; puis Destinie 2, et les cas
   types du COR par TRAJECTOiRE, exécutés à part comme témoins, R installé.
5. L'effet retour sur les finances publiques : l'ASPA que déclenchent les
   petites pensions des scénarios 2 à 5, la CSG proportionnelle aux masses,
   l'impôt borné par l'IPP.
6. L'AVTS et le minimum vieillesse d'avant 2007, au Journal officiel : la
   validation de 1949 à 1971, la série du minimum de 1956 à 2006, le
   trimestre des DOM.
7. La démographie en variantes : les quotients projetés âge par âge au lieu de
   la loi de Gompertz-Makeham, les variantes de l'INSEE de 2026 — fécondité,
   espérance de vie, migrations —, dans la population du Coût et dans le
   diviseur.
8. Les minima des exploitants : la PMR et le complément différentiel de la RCO
   (code rural, L. 732-54-1 à L. 732-54-4 et L. 732-63).
9. Les indicateurs de cycle de vie, par cas type et génération, sous les six
   systèmes : rendement interne, durée de retraite, taux de récupération,
   patrimoine retraite ; confrontés à l'OCDE de 2025 et aux cas types du COR.
10. Le site : plusieurs âges de départ côte à côte, les droits contrefactuels
    (au 31 août 2023, la loi de 2023 sans suspension), le contrôle d'un
    relevé, l'indice majoré, le solveur inverse.
11. L'arithmétique notionnelle éprouvée : les exemples officiels du diviseur
    (Suède, Finlande, Italie, Pologne), le lissage italien exact, le lissage
    du seul réel, le prorata des mois de l'année du départ, les années sans
    montant (points convertis), les chocs stylisés du secrétariat général du
    COR.
12. Le scénario 1, compléments : la seconde pension revalorisée et
    replafonnée, les micro-entrepreneurs par leur chiffre d'affaires et le
    chemin de la Cipav, les artistes-auteurs sous le seuil, la dispense des
    cotisations minimales, le rachat de trimestres, le coût du travail
    complet, la veille des projets de loi.
13. Les choix du programme, que le propriétaire tranche (ci-dessous).
14. Ce qui demande une population ou des microdonnées, avec l'action 136
    (étape 6) : une population simulée, des départs choisis, la validation
    sur des pensions réelles (l'EIR, au CASD).

**Ce que le propriétaire tranche** (étape 13), chaque choix chiffré au
registre, au point `a_trancher` du modèle qui le fait :

- les gains d'héritage : le compte d'un assuré mort avant sa retraite rendu à
  sa génération, comme en Suède et en Norvège, soit 4 à 10 % de plus sur
  toutes les pensions notionnelles ; le programme ne dit pas ce que devient
  ce compte ;
- le diviseur des droits acquis à la bascule : celui de l'année de la bascule,
  le choix actuel, que la Pologne a fait, ou celui de la génération de
  l'assuré, que retient le modèle de la Banque mondiale (PROST) ; sous le
  premier, la part figée de l'actif de quarante ans en 2026 perd 9,0 %, celle
  de l'actif de trente ans 11,8 % ;
- la réversion tarifée dans le diviseur, comme en Italie, sous
  `convention_reversion="servie"` ;
- l'équilibrage appliqué, à la suédoise : un indice d'équilibre de stocks, un
  frein et un accélérateur ;
- la convention de l'Agirc-Arrco en projection : celle du COR (le salaire
  moins 1,16 point jusqu'en 2037, puis moins 0,86) ou celle du dépôt
  (rendement gelé, prix) ;
- l'indexation suspendue en déficit, à la grecque ; les frais de gestion
  déduits du compte, à la suédoise ;
- pour le net de l'étape 2, une présomption déclarée — « aucun autre revenu
  que ses pensions » — ou un champ de plus, la question que l'action 136
  posait déjà. *Décidé le 4 octobre 2026 par le propriétaire : les deux* —
  la présomption par défaut, que la page dit, et un champ facultatif dans
  les réglages, le revenu fiscal de référence, qui la remplace.

**Demande**, le 4 octobre 2026 : « Je veux que tu regardes tous les modèles
publics comme openfisca ou destinie 2 et que tu me dises tout ce que notre
modèle fait de moins bien comparé à chaque modèle. Attention, s'il y a un
écart entre notre modèle et un modèle public, cela ne veut pas forcément dire
que le modèle public fait mieux. On a déjà vu par le passé que des modèles
publics avaient des erreurs ou n'étaient pas à jour. […] Ne fait pas de
changement dans les moteurs pour l'instant. Je veux uniquement préparer le
travail dans un premier temps. Il faut que tu regardes avec tous les
modèles. »

**Fait, le 4 octobre 2026 : le relevé repris modèle par modèle, sur les
soixante-neuf, et vérifié.** Dix recherches menées en parallèle, une par
famille — OpenFisca, l'IPP, l'INSEE, la DREES, la microsimulation statique, le
COR et les caisses, l'Urssaf et Catala, la société civile, les comptes
notionnels nordiques, les autres comptes notionnels et les organisations
internationales —, chacune lisant le code au commit ou la publication le jour
même. Chaque point a été vérifié trois fois : chez eux, chez nous, et contre
le texte en vigueur (index LEGI et JORF du dépôt, à jour au 27 septembre
2026) ou la publication officielle qui l'applique. Aucun moteur n'est touché,
à la demande du propriétaire. Le registre reçoit 186 points (279 en tout) ; 29
autres, que la vérification n'a pas tenus, n'y sont pas entrés. Il reçoit 105
écarts nouveaux, les erreurs et les retards des autres (145 en tout), et deux
champs : `verification`, ce qui établit qu'un point a raison, et `bilan`, que
chaque modèle porte désormais et qu'un test exige. Vingt points anciens sont
repris : des preuves mal placées (ANCETRE, TAXIPP, Saphir, la maquette du
COR), des chiffres périmés, un point d'ANCETRE rendu à TRAJECTOiRE ; deux
écarts anciens sont corrigés, et deux, faux, retirés (« 169 trimestres » chez
OpenFisca-France-Pension ; le RSA chez modele-ti, qui pose la question) ;
CALIPER est désormais `calcul_pension`, et la licence de Saphir, les règles
d'EUROMOD et les conditions de l'OIT sont lues.

**Ce que le relevé apprend.**

- *Le dépôt a tort, au scénario 1, là où plusieurs modèles font juste*, et la
  session a retrouvé chaque erreur dans le code :
  1. le minimum contributif. Ses montants sont projetés sur les prix entre
     six ancres, quand D. 351-2-1 les revalorise comme les pensions, et
     l'ancre « 2007 » est le montant du 1er janvier 2008 ; la majoration est
     servie avant sa création, en 2004, le seuil de 120 trimestres opposé
     avant avril 2009 (`droit/completer.py`, sans date), l'écrêtement avant
     2012, la proratisation sur la durée cotisée avant juillet 2005. Le
     majoré de 2004 est trop haut de 7,9 %, celui de 2019 de 4,7 %
     (OpenFisca-France-Pension, Destinie 2, les barèmes de l'IPP et celui de
     la Cnav concordent) ;
  2. le salaire annuel moyen garde les années qui ne valident aucun
     trimestre, que R. 351-29 exclut depuis 2004 ; avant 1995, la Cnav le
     rapportait aux trimestres ; avant 1973, il portait sur les dix dernières
     années, non sur les dix meilleures ;
  3. l'assiette de l'AVPF : 1 820 heures du SMIC de l'année
     (`carriere.py:513-515`), quand R. 381-3 dit 169 heures par mois au SMIC
     du 1er juillet précédent, soit 9 à 10 % de trop peu, 12,5 % avant 1982 ;
  4. le revenu moyen des artisans et des commerçants passe à vingt-cinq ans
     plus lentement que celui des salariés (R. 634-1-1) ; les taux de
     cotisation du régime général sont des moyennes par période ; le salaire
     de référence de l'IGRANTE et de l'IPACTE de 1948 est dix fois trop haut.
- *Ce que d'autres font et que le dépôt n'a pas*, au-delà du relevé du 1er
  octobre : la majoration exceptionnelle de 2023, les versements uniques des
  petites pensions, la bonification du cinquième, le départ anticipé des
  parents de trois enfants, le plafond de L. 18, la majoration pour enfants à
  charge de l'Agirc-Arrco, le minimum de réversion ; chez les non-salariés,
  l'assiette abattue de 26 %, les taux propres des artisans, le plafond du
  RCI, la CAVEC et la CNBF année par année, les cotisations PCV des
  professions de santé, Mayotte ; pour le net, l'impôt sur les pensions, et
  l'ASPA hors de l'assiette de la CSG, que le site prélève aujourd'hui
  (95 € par mois à un allocataire sans autre ressource) ; pour le Coût, la
  rétro-projection, l'incertitude propagée, le bilan du compte notionnel en
  indicateur, les variantes de longévité qui montrent ce que le diviseur
  absorbe.
- *Ce que la proposition doit trancher*, en plus des choix du 1er octobre : 33
  points nouveaux, au registre en `a_trancher`. Le plus lourd est l'assiette
  qui fait le rendement du compte : les seuls salaires des comptes nationaux,
  comme aujourd'hui, ou l'assiette de la caisse fusionnée, revenu des
  indépendants compris, comme en Lettonie, en Pologne et en Grèce. Sur les
  séries certifiées du dépôt, de 1950 à 2024, les salaires sont multipliés
  par 216,3, salaires et revenu mixte par 137,4 : 0,61 point de rendement par
  an (calcul refait par la session). Viennent ensuite le calendrier de
  l'indexation — le compte reçoit la croissance de l'année du départ, qu'une
  caisse réelle ne connaît pas encore : +7,9 % de pension pour un départ en
  2021, −4,0 % en 2020 —, un plancher de revalorisation, les années d'enfant
  et l'AVPF au compte, que la règle de l'action 141 ferait entrer, les droits
  acquis après le départ, une garantie à retrait partiel, une transition
  panachée par génération, un âge lié à l'espérance de vie.
- *Ce que les modèles publics ont de faux ou de périmé* : hors les barèmes de
  l'IPP, aucun modèle français n'a la loi du 30 décembre 2025 ; TRAJECTOiRE
  garde le versement forfaitaire unique de la Cnav, abrogé en 2016, et le
  coefficient de solidarité de l'Agirc-Arrco, éteint en 2024 ; EUROMOD sert
  l'ASPA du couple à qui seul y a droit et prélève la CRDS des exonérés ; Ines
  a un abattement de l'ASPA nul en 2026 ; les diviseurs suédois, norvégien et
  finlandais lisent une table du moment, moins exacte que la table de
  génération du dépôt. Quatre modèles ne font mieux sur rien : Destinie 1,
  Ariane, le fator previdenciário, qui n'est plus qu'une règle de transition
  depuis 2019, et OG-Core ; leur bilan dit pourquoi.
- *Ce qui attend son étape*, hors des moteurs comme dedans : deux phrases
  inexactes du code (`cout.py:80-84`, qui dit retirés les points des chômeurs,
  et `equilibre.py:319-322`) ; l'en-tête de `masse_salariale.csv`, qui en
  fait « l'assiette des cotisations » ; la fiche `temps_partiel_fonction_publique`,
  qui dit à tort la quotité « lue nulle part » (`compter.py:276-278`) ; les
  fiches `salaire_annuel_moyen` et `minimum_contributif`, dites conformes ;
  `limites.md:822`, qui croit introuvables les tables de revalorisation des
  salaires de 2013 et de 2015, que publie l'API des barèmes de la Cnav
  (`legislation.lassuranceretraite.fr/api/v1/baremes`, 396 barèmes, montants
  jusqu'en 2026). Cette API tranche presque toutes les séries : chaque étape
  qui touche une série du régime général commence par elle.

**Les étapes nouvelles**, qui s'ajoutent aux étapes 2 à 14 ; le registre cite
chacune par son chantier :

15. Le minimum contributif daté : ses montants de 1983 à 2026, revalorisés
    comme les pensions ; la majoration de 2004 ; le seuil de 120 trimestres
    des pensions d'avril 2009 ; l'écrêtement de 2012 ; la proratisation sur la
    durée d'assurance jusqu'en juin 2005 ; l'AVPF dans la majoration depuis
    septembre 2023, vingt-quatre trimestres au plus (D. 351-2-1, D. 351-2-2,
    L. 351-10, L. 173-2).
16. Les assiettes et les séries du régime général : le salaire annuel moyen
    (les années validantes depuis 2004, le calcul trimestriel avant 1995, les
    dix dernières années avant 1973) ; l'assiette de l'AVPF ; le revenu moyen
    des indépendants ; les taux de cotisation de chaque année ; les tables
    anciennes de revalorisation des salaires ; les coefficients de l'Agirc et
    de l'Arrco d'avant 1965 ; l'IGRANTE et l'IPACTE de 1948.
17. Les règles qui manquent au régime général, à la fonction publique et aux
    complémentaires : la majoration exceptionnelle de 2023, les versements
    uniques, la bonification du cinquième et la majoration des hospitaliers
    actifs, le départ des parents de trois enfants, le plafond de L. 18, les
    taux pleins par catégorie de L. 351-8, la pension maximale, la majoration
    pour enfants à charge de l'Agirc-Arrco, la majoration pour conjoint à
    charge.
18. Les non-salariés et Mayotte, caisse par caisse : l'assiette abattue, les
    taux propres, le plafond du RCI, les grilles de la CAVEC et de la CNBF,
    les cotisations PCV, les points d'incapacité, le conjoint collaborateur,
    les dispenses, les points d'avant 1973 des artisans et des commerçants ;
    le SMIC, le plafond et les taux de Mayotte, la Lodeom.
19. La page Coût éprouvée, et le bilan du compte : la rétro-projection depuis
    une année passée, l'incertitude propagée, la part de la solidarité
    confrontée aux masses publiées, une carrière heurtée dans la grille des
    cas types ; le bilan du compte notionnel (durée de rotation, actif de
    cotisation, réserves et leur rendement), le taux de cotisation d'équilibre.

**L'ordre proposé**, ce que le dépôt a de faux d'abord : 15, 16 et 2 (le net
du foyer et l'ASPA du couple, l'ASPA prélevée à tort comprise), puis 6, 4,
17, 18, 12 et 8, au scénario 1 ; puis 3, 19, 7, 5, 11, 9 et 10, pour le Coût
et la proposition ; 14 avec l'action 136 ; l'étape 13 reçoit 33 choix, que le
propriétaire tranche quand il le veut.

**Le même jour, le relevé archivé**, à la demande du propriétaire (« Est-ce
que tes recherches ont été commit ? Si non, fait le ») : la vue modèle par
modèle tirée du registre, et les dix rapports des recherches tels qu'ils sont
arrivés, sont dans `docs/archives/releve_des_autres_modeles.md` et le dossier
du même nom. Ils gardent ce que le registre ne garde pas : les 29 points que
la vérification n'a pas tenus et leur raison, les verdicts sur les points
anciens, la comparaison des barèmes de l'IPP famille par famille, les séries
d'OpenFisca-France confrontées à celles du dépôt.

**Demande**, le 4 octobre 2026 : « J'aimerais qu'on regarde les résultats de
notre analyse des modèles publics qu'on a fait cette nuit et ce matin et qu'on
corrige notre modèle. Il faut bien sûr vérifier à chaque fois qui a raison par
des sources officielles. »

**Fait, le 4 octobre 2026 : l'étape 15, le minimum contributif daté.** Chaque
point du relevé a été relu au texte, dans l'index LEGI du dépôt (L. 351-10,
D. 351-2-1, D. 351-2-2, R. 351-25, L. 173-2 et D. 173-21-0-0-1, toutes leurs
rédactions), puis chez la caisse qui l'applique : les deux barèmes de la Cnav,
lus par son API (le minimum depuis le 1er avril 1983, le plafond depuis 2012),
ses exposés « Minimum avant 2012 » et « Calcul du minimum contributif », ses
circulaires 2003/56, 2004/13, 2005/30, 2009/17, 2023/16, 2024/3, 2024/28,
2025/8, 2025/33 et 2026/16, les lettres ministérielles du 25 mars et du 26
novembre 2004. Les trois modèles avaient raison sur tout. Ce qui change :

- *les montants* : chaque revalorisation depuis 1983, 101 dates au lieu de
  dix-huit lignes annuelles reliées par les prix, lues au mois de la date
  d'effet ; les onze ancres du code certifiées à la date que leur texte leur
  donne (le récupérateur LEGI lit désormais R. 351-25 et les rédactions de
  2004 et 2006, qui écrivent « Euros »), et entre elles le barème de la Cnav,
  au niveau `haute` (`scripts/fetch/cnav_minimum_contributif.py`). Les
  montants de 2025 du dépôt étaient ceux de la circulaire 2024/40, que la
  2025/8 a corrigés (747,47 € et non 747,69 € ; plafond de 1 394,44 €) ;
- *la règle*, en huit versions de la fiche `minimum_contributif`, que le
  moteur lit : rien avant avril 1983 ; de décembre 1984 à 2003, le cumul de
  plusieurs pensions portées au minimum limité au minimum entier ; la
  majoration en 2004, sans distinction des périodes jusqu'en juin 2005 ; le
  seuil de 120 trimestres cotisés en avril 2009 ; l'écrêtement en 2012 ;
  l'AVPF et l'AVA, 24 trimestres au plus, en septembre 2023 ;
- *un point que le relevé n'avait pas* : depuis 2004, le minimum d'un
  polypensionné au-delà de la durée requise se proratise sur sa durée tous
  régimes, non limitée (L. 351-10 ; circulaire 2005/30, point 513 ; exposé
  actuel de la Cnav), et non sur la durée de proratisation ;
- *les preuves* : les huit exemples chiffrés des circulaires 2005/30 et
  2009/17 rejoués au centime dans les deux moteurs ; l'exemple 1 de la
  2005/30 au témoin des exemples officiels (570,04 € par mois, que l'ancien
  modèle dépassait de 7 %).

*Les effets.* Au scénario 1, quinze témoins sur 712 bougent : les carrières
des cultes liquidées de 2010 à 2022, jusqu'à −3,85 % (membre d'une
congrégation né en 1955), qui recevaient un majoré projeté sur les prix ; les
autres, de quelques centimes. Le coût du minimum contributif que le modèle
tire de sa grille tombe en 2024 de 2,11 à 1,07 Md€ : la carrière complète au
SMIC, qui en porte presque toute la masse, recevait avant 2004 une majoration
qui n'existait pas, et depuis des montants trop hauts de 3 à 8 % — 1 442 € de
complément par an au lieu de 423 € pour la génération 1940, partie en 2000.
La proratisation tous régimes ne touche aucun cas de la grille. Au README, le
cumul passé du système 2 passe de 2 866 à 2 876 Md€.

Restent, à la fiche (`approximations`) : la durée tous régimes que le modèle
compte et non celle que chaque régime communique ; la limitation d'avant 2004
sans le minimum garanti de la fonction publique ; les trimestres que la
fonction publique valide au titre de l'AVPF (D. 351-2-2, III) ; au-delà de
juin 2026, le plafond projeté sur le SMIC annuel. Et à lire : le texte du
décret n° 84-995, dont l'index ne garde que le titre.

**Le 5 octobre 2026, une étape nouvelle, que TRAJECTOiRE révèle** (action 142,
étape 4, suite ; registre, `trajectoire`, 138.20) :

20. La valeur de service du jour de la liquidation. Le scénario 1 sert à
    l'Agirc-Arrco — et à l'Arrco, à l'Agirc d'avant 2019 — la valeur du point
    du 31 décembre de l'année de la liquidation (`valeur_du_point`,
    `valeurs_point.csv`), quand la caisse sert celle du jour : la retraite
    complémentaire d'un départ antérieur au relèvement de l'année en sort
    trop haute de ce relèvement, +5,1 % en janvier 2022, +4,9 % en octobre
    2023. Lire la règle dans l'accord du 17 novembre 2017 ; dater la valeur au
    mois dans les deux moteurs ; les témoins de simulation bougeront, et
    l'écart déclaré de `tests/test_trajectoire.py` tombera.

**Demande**, le 4 octobre 2026 : « passe à l'étape 16 dans une nouvelle
session ».

**Fait, le 5 octobre 2026 : l'étape 16, les assiettes et les séries du régime
général, sauf un point.** Chaque point du relevé a été relu au texte, dans les
index LEGI et JORF du dépôt — R. 351-29 dans toutes ses rédactions, R. 634-1
et R. 634-1-1, R. 173-3-2, R. 381-3, les décrets n° 72-1229, 2004-144 et
2025-1409, l'annexe de l'arrêté du 17 février 1960 —, puis chez la caisse,
par l'API de sa base de législation : l'ordonnance de 1945, quatre circulaires
ministérielles de 1946 à 1961, les circulaires Cnav 1/73, 95/94, 2004/27 et
2025/33, deux exposés, cinq barèmes. Les modèles avaient raison partout où ils
disaient le dépôt en défaut, sauf EDIFIS sur les taux de cotisation, que le
dépôt portait année par année depuis le 14 septembre. Ce qui change :

- *le salaire annuel moyen daté*, en cinq versions de la fiche
  `salaire_annuel_moyen`, que le moteur lit à la date d'effet : les dix
  dernières années d'assurance avant soixante ans, et, de juillet 1948 à 1972,
  avant l'entrée en jouissance si c'est mieux ; les dix meilleures depuis
  1973 ; la somme des salaires rapportée aux trimestres, assimilés compris, et
  multipliée par quatre jusqu'au 30 juin 1995 ; sans les années qui ne valident
  aucun trimestre depuis 2004. Les salariés agricoles et les cultes suivent
  (L. 742-3 du code rural, L. 382-27) ;
- *les artisans et les commerçants* : leur table du nombre d'années, deux fois
  plus lente, certifiée sur R. 634-1-1, jusqu'aux pensions de 2025, la règle
  commune de R. 173-3-2 ensuite, et les années validantes depuis 2004 (fiche
  `revenu_annuel_moyen_independants`) ;
- *l'assiette de l'AVPF*, le barème de la Cnav de juillet 1972 à 2026 — 169
  heures par mois du SMIC du 1er juillet précédent, rien avant juillet 1972 ;
  en 2026, la caisse prend le SMIC de janvier, et le modèle la suit ;
- *les colonnes de revalorisation d'avant 2017*, que `limites.md` croyait
  introuvables : quatre-vingt-huit, de l'arrêté du 14 mai 1946 à octobre 2015,
  lues sur la page des coefficients d'avant 2013 de la caisse (son script de
  déclaration) et dans deux barèmes. Une liquidation lit la colonne en vigueur
  à sa date d'effet, et non plus le rapport de deux valeurs de la colonne de
  2017 ; le mode d'indexation du compte qui lit le taux annuel des arrêtés
  garde ce rapport. Le récupérateur corrige une date — la colonne « 1958 » est
  celle de l'arrêté d'avril 1957 — et deux valeurs mal ponctuées ;
- *le salaire de référence de 1948 de l'IPACTE et de l'IGRANTE* : 37 anciens
  francs, 0,056406 €, et non 0,56 €.

*Les effets.* Au scénario 1, 116 témoins sur 727 bougent ; les scénarios 2, 4
et 6, aucun. De −26,4 % pour une assurée née en 1910, partie en 1970 — les dix
dernières années lui retirent 16 % de son salaire moyen, la colonne en vigueur
18 % — à +3,1 % pour un commerçant né en 1945, dont le revenu moyen porte sur
dix-sept années au lieu de vingt-deux. La plus lourde des causes est la colonne
en vigueur : jusqu'en 1993, la revalorisation de janvier ne touchait pas
encore le salaire de l'année close, et le rapport des colonnes de 2017 la lui
ajoutait, de 4 % pour un départ de 1989 à 9 % pour 1979 et 16 % pour 1973. Au
README, le cumul passé du système 2 passe de 2 874 à 2 932 Md€ : +42,9 pour
la colonne en vigueur, +13,8 pour les règles datées, +2,4 pour l'AVPF, −0,8
pour la table des indépendants, chaque cause neutralisée à son tour sur le
`main` du matin (de 2 876 à 2 935) ; celui du système actuel, calé sur la
dépense observée, ne bouge pas, et l'avenir à peine (moins d'un milliard en
2070). Sous WSL, les 608 témoins que l'étape ne touche pas sont sortis
identiques au bit près à `main`.

*Ce que la suite a appris.* L'oracle d'OpenFisca voulait l'artisan et le
commerçant égaux au salarié : c'est faux en droit pour les générations 1935 à
1952 parties avant 2026, dont le revenu moyen retient moins d'années ; à qui
l'on prête la table du régime général, ils le redeviennent au centime sur les
dix profils. L'effet mesuré de l'AVPF tombe à zéro sur la grille : il venait
tout entier des générations 1920 et 1925, à qui le modèle portait une AVPF de
1949 à 1958, avant qu'elle n'existe, et sa ligne dit maintenant pourquoi elle
est vide. La correction de la page Méthode passe de +5,0 à +5,5 points pour
la génération 1920 ; à l'accueil, la baisse médiane de la pension d'un
retraité d'aujourd'hui, de 27 à 28 %.

Reste de l'étape 16 : les coefficients d'anticipation et d'ajournement de
l'Agirc d'avant 1955 et de l'Arrco d'avant 1965, dont les textes de 1947 et
de 1961 restent à trouver (le point des barèmes de l'IPP, toujours
`a_reprendre`). Nés de la lecture : le calcul trimestriel du revenu moyen des
indépendants que la Cnav range dans ses anciennes dispositions, à dater, et
leurs années de 2018 à 2025, que la caisse moyenne à part (étape 18) ; les
années de rachat et les indemnités journalières de maternité au salaire annuel
moyen ; les trimestres que le motif « éducation d'un enfant » valide avant
juillet 1972, quand l'AVPF n'existait pas.

**Demande**, le 5 octobre 2026 : l'étape 20, que TRAJECTOiRE a mise au jour,
dans une session à elle.

**Fait, le 5 octobre 2026 : l'étape 20, la valeur de service du jour.** La
règle est lue : l'accord du 17 novembre 2017 fait revaloriser la valeur de
service « au 1er novembre de chaque année » (article 27) et calcule
l'allocation en multipliant les points « par la valeur de service du point de
retraite du régime » (article 92), que la circulaire 2020-02-DRJ applique « à
cette même date » ; avant 2019, l'accord du 30 octobre 2015 a reporté le
relèvement de l'Agirc et de l'Arrco du 1er avril au 1er novembre (avis
d'extension de ses avenants au JORF du 6 février 2016 ; COR, séance du 13 avril
2016). Les dates, elles, sont dans la compilation de la fédération, qui imprime
chaque valeur dans la colonne de sa date d'effet depuis 1947 : lues par la
position des mots sur la page, elles retrouvent à un dixième de point
l'évolution qu'elle publie en regard de chaque valeur de l'Agirc et de
l'Arrco, et, chaque 31 décembre, la valeur que `valeurs_point.csv` certifie.
Ce qui change :

- *`regimes/valeurs_service_datees.csv`*, 268 valeurs datées : l'Agirc au
  1er janvier et au 1er juillet jusqu'en 1989, au 1er janvier jusqu'en 2000, au
  1er avril jusqu'en 2015, au 1er novembre ensuite ; l'Arrco unifiée au 1er
  janvier 1999 puis au 1er avril ; l'UNIRS, qui tient lieu de l'Arrco avant
  1999, aux deux dates que chaque année imprime ; l'Agirc-Arrco au 1er janvier
  2019, à 1,2588 €, puis chaque 1er novembre, gels compris. Le paquet la porte ;
- *la liquidation* sert la valeur du jour de sa date d'effet
  (`ValeursPoint.service_au`, `valeur_du_point`, qui reçoit la date ; leurs
  jumeaux), et, au-delà de la dernière décision publiée, la valeur du 31
  décembre de l'année d'avant pour un départ antérieur au 1er novembre
  (`millesime`) ;
- *la pension menée* (`PensionServie.coefficient`) lit la valeur du jour aux
  deux bouts : une pension de février 2022 reçoit à la fin de l'année le
  relèvement de novembre, qu'elle avait jusqu'ici dès son départ ; le plafond
  de la majoration pour enfants et la seconde retraite suivent la même date ;
- *les tests* : la cohérence des deux tables ; la liquidation, la pension
  menée et l'exemple de la circulaire 2020-02-DRJ (6 000 € de pensions de 2018
  passés au point unifié sans changer en janvier 2019), au témoin des exemples
  officiels sous une grandeur nouvelle, `valeurs_de_service_au_jour` ;
  OpenFisca concorde désormais au jour, et non plus « à une convention près ».

*Les effets.* Au scénario 1, 251 témoins sur 735 baissent, de 0,44 % en
médiane, jusqu'à −2,18 % : la complémentaire d'un départ de janvier à octobre
2022 perd 4,87 %, de 2018 0,60 %, de l'UNIRS en août 1974 12,5 % ; tout départ
futur antérieur au 1er novembre perd la revalorisation projetée de l'année,
1,72 %. Aucune hausse ; les scénarios 3 et 5 suivent pour qui était parti, les
2, 4 et 6 ne bougent pas, et la pension d'aujourd'hui de qui est parti non
plus, qui ne tient qu'à ses points et à la valeur de l'échéance. Au README, la
trajectoire que le modèle se donne pour le système actuel — le contrôle de la
dépense du COR depuis l'action 147 — passe de 694 à 692 Md€ en 2070, et le
solde moyen de la proposition de −0,52 à −0,55 % du PIB ; à l'accueil, −0,6
point et une dette de 2070 de 37 % au lieu de 35 ; page Méthode, la
correction de la génération 1920 de +5,5 à +5,6 points ; le parcours de
présentation suit, et la conservation est refigée. TRAJECTOiRE
concorde : ses écarts « valeur du jour » sont retirés ; Destinie 2, qui sert
la valeur du 31 décembre, reçoit les siens (−0,6 % en février 2018, −2,1 %
avant novembre 2024), au registre et dans `tests/test_destinie.py`. Fiche
`agirc_arrco_valeur_service`, approchée par la seule date des hausses de
l'UNIRS, que le document ne donne qu'à ses colonnes.

Restent, nés de l'étape : les autres régimes en points que la table ne date
pas, l'Ircantec d'abord, relevée au 1er avril à partir de 2009 selon
OpenFisca ; le texte de l'accord du 30 octobre 2015 ; et, le 14 octobre 2026,
la décision du 1er novembre, une ligne de plus à la table datée.

### 145. Les régimes que l'inventaire ne nommait pas : documentés, non calculés — `en cours`

**Reprise, au 16 octobre 2026.** Faites, les trois étapes : dix-sept régimes
entrés à l'inventaire ; vingt-deux fiches à l'étape 2, close le 16 par la CRFM
de Mayotte, les élus calédoniens et les régies ferroviaires, et ses limites
écrites ; huit pistes relues. Reste, hors étape : LexPol et le Journal officiel
de Wallis-et-Futuna, toujours injoignables du conteneur, et le règlement de la
CRFM. Au propriétaire, puis clore l'action : les écarts des notes du 13, du 14
et du 16 octobre, dont le rendement de la CAFAT (9 %, non 10 %) et le taux de
Wallis-et-Futuna (21 %, non 27 %), d'une donnée chacun, et la part de pension
CRFM des agents mahorais intégrés (note « trois hors champ »).

**Demande**, le 4 octobre 2026 : « Je veux que tu documentes les régimes de
retraite que nous n'avons pas encore documenter pour l'instant. Il faut
documenter le plus de régimes de retraite possibles dans le détail le plus fin
possible. Je veux juste que tu documentes pour l'instant. Ne fait pas de
changement dans les moteurs. »

**Étape 1, le 4 octobre 2026 : les régimes absents de l'inventaire.**

- *La méthode.* L'inventaire se disait complet ; il a été relu contre trois
  énumérations qu'il ne citait pas. Les décrets annuels de contribution au
  fonds spécial d'allocation vieillesse, de 1984 à 1993, nomment tous les
  débiteurs de pensions (décret n° 84-104, article 2, `LEGIARTI000006766410`,
  à décret n° 93-426, `LEGIARTI000006928885`) ; la convention du GIP Info
  Retraite nomme ses trente-huit membres de 2004 ; la carte des mandats de la
  Caisse des dépôts (février 2026) et ses arrêtés de délégation de 2003 à
  2006 détaillent ses « pensions sur fonds spéciaux ». L'article 61 du décret
  n° 46-1378 et R. 711-1, relus dans leurs trois rédactions, y ont ajouté la
  Compagnie générale des eaux, que `docs/regimes.md` tenait pour citée de
  mémoire.
- *Ce qui est entré.* Neuf lignes **à modéliser** : les régimes spéciaux de la
  CCI de Paris (fermé en 2006), de la Compagnie générale des eaux (1991) et
  de l'ancienne CCI de Roubaix (1998) ; le personnel statutaire de la CANSSM ;
  le personnel titulaire des ports autonomes de Bordeaux, du Havre et de
  Marseille ; le RETREP des maîtres du privé ; les pensions des ministres des
  cultes d'Alsace-Moselle ; l'allocation temporaire complémentaire des
  ingénieurs du contrôle aérien ; l'affiliation des représentants au
  Parlement européen. Huit lignes **hors champ** : la SUDAC, la caisse du
  personnel sédentaire de la CGMF, la caisse du chemin de fer
  franco-éthiopien, les régimes locaux d'Alsace-Moselle, les cantonniers de
  l'État et les pensions sur fonds spéciaux, les régimes par rente des élus
  locaux d'avant 1992, l'Assemblée de l'Union française, la Caisse nationale
  des retraites pour la vieillesse de 1850. Chaque ligne cite ses textes, avec
  leur identifiant quand l'index le porte, et dit ce qui manque ou pourquoi.
- *Les fiches de règles.* Sept, toutes `pas_encore_modelisee`, découpées en
  versions datées et citant leurs articles : `retrep_avantages_temporaires`
  (six versions, du décret de 1980 au décret n° 2023-435),
  `atc_icna_allocation` (cinq), `cultes_alsace_moselle_pension` (trois, la
  première supposée faute du texte de 1909), `parlement_europeen_affiliation`
  (trois), et les trois transferts au régime général —
  `compagnie_generale_eaux_transfert_1991`, `cci_roubaix_transfert_1998`,
  `cci_paris_transfert_2006` —, qui suivent un même gabarit : une rente
  forfaitaire du régime général, 64 650 F puis 62 150 F pour cent cinquante
  trimestres validés depuis le 1er juillet 1930, puis, en 2006, le
  rétablissement des droits au régime général et l'affiliation à
  l'Agirc-Arrco. Le personnel de la CANSSM et les ports n'ont pas de fiche :
  leurs règlements ne sont publiés nulle part où le dépôt lit.
- *Ce qui n'est pas entré.* Les compléments de pension CGE et SEVESC de la
  Caisse des dépôts (des bonifications d'insalubrité d'agents détachés, au-
  dessus de la CNRACL), le fonds de la mairie de Fort-de-France, les rentes
  d'invalidité de la Ville de Paris, les régimes facultatifs, les
  organisations internationales, les membres du Gouvernement (aucun texte
  d'affiliation dans l'index) ; `docs/regimes.md` les nomme, avec les pistes
  connues par leur seul titre.
- *Les tests.* Deux assertions fermaient la couverture « à modéliser » ;
  elles l'acceptent désormais, à condition qu'une fiche de règles décrive la
  ligne ou que son `manque` dise longuement ce qui bloque
  (`test_l_inventaire_couvre_les_regimes_que_le_code_enumere`), et le filtre
  de la page Données propose exactement les couvertures que l'inventaire
  porte. Aucun moteur n'est touché.
- *Ce que ça déplace.* Aucun témoin de simulation ; les pages Méthode et
  Programme comptent cent huit régimes, et le parcours de présentation suit.

**Les étapes suivantes.**

2. *Les fiches des régimes sans fiche.* Une fiche `pas_encore_modelisee` ou
   `approchee`, selon que le régime est calculé, par régime de l'inventaire
   qui n'a que la fiche générique de liquidation, en lisant ses textes dans
   l'index ou sur le site de sa caisse ; l'outre-mer d'abord, dont les
   délibérations sont citées par les lignes de l'inventaire.
3. *Les pistes.* La caisse de retraites de la presse (ordonnance
   n° 45-2411), les ingénieurs des minéraux solides (1947), l'Institut de
   France (décret n° 49-1372), les praticiens-conseils (1963), l'ONIVIT
   (décret n° 79-814), le statut du personnel de la CANSSM, les règlements
   des ports : à lire au fac-similé du Journal officiel ou aux archives, puis
   inscrire ou écarter.

### 151. Partir très tard : le départ jusqu'au bout des tables de mortalité, puis la limite d'âge des fonctionnaires et ses exceptions — `en cours`

**Reprise, au 18 octobre 2026.** Faites, les étapes 1 à 11 : le départ jusqu'à 119 ans ;
la limite d'âge lue ; la radiation à la limite des fonctionnaires, des militaires, des
contractuels, des ouvriers de l'État, de la SNCF, de la RATP, des IEG (depuis 1954), de
l'Opéra, de la SEITA et de la Banque, et la limite du mineur, présumé maintenu au-delà
(étapes 3, 4, 6, 8 à 10), en Python et en JavaScript ; la page, qui dit la limite et la
fin de l'emploi dans les mots de chaque statut (étapes 5 et 11) ; la CARMF avant 2017 et
le taux acquis en 1983 (étape 7). Reste au modèle : la SNCF, la RATP et la Banque avant
2010 et 2012, dont les textes ne se lisent pas d'ici (note de l'étape 10). Au
propriétaire : la radiation dans les comptes notionnels, l'actif d'avant 2010, les choix
des étapes 4, 6 et 8 à 10, et où la page dit le maintien du mineur (note de l'étape 11).

**Demande**, le 10 octobre 2026 : « Pourquoi on bloque à 75 ans ? Est-ce que
c'est uniquement une raison technique ? Ou est-ce qu'il y a un vrai problème
dans notre système ? » ; puis : « Met une limite d'âge très élevée. Par
exemple, dans certains pays, certaines personnes travaillent jusqu'à très tard
dans la vie. Il faut qu'on puisse simuler ça. Pour les fonctionnaires, il faut
voir si c'est vraiment un blocage. Je pense qu'il existe des exceptions. Il
faut traiter chaque exception. »

**Le constat, le 10 octobre 2026.** La borne de 75 ans était dans le premier
commit, le 8 septembre 2026 (« Âge de liquidation attendu entre 40 et 75
ans »), sans rien qui la justifie. Le moteur n'en dépendait pas : quatorze
statuts, trois générations — 1960, 2000, 2020 — et des départs de 74 à 90 ans,
294 simulations, se calculaient dans les six scénarios sans erreur, sans
pension nulle ni pension qui baisse d'un âge au suivant. Sa seule limite est
l'âge terminal des tables, 120 ans, où le diviseur du compte notionnel est nul
et où la conversion lève une erreur. Ce que la borne protégeait — l'onglet du
lecteur, contre une adresse forgée — tient par les bornes qui en dérivent : la
dernière année d'une carrière et la longueur d'un relevé.

**Le plan.** Étape 1 : relever la borne (faite le 10 octobre). Étape 2 : la
limite d'âge des fonctionnaires, texte en main — sa valeur par fonction
publique, par corps et par génération, et chacune des exceptions qui la
reculent ou la lèvent. Pistes à lire, dont aucune n'est encore vérifiée : un
recul pour enfants à charge ; une prolongation pour qui n'a pas la durée ; le
maintien des catégories actives jusqu'à la limite du droit commun ; les
maintiens en surnombre de corps particuliers ; les limites par grade des
militaires ; la reprise d'activité sous un autre statut après la radiation des
cadres, que le simulateur décrit déjà par un second métier. Étape 3 : ce que le
simulateur fait au-delà de la limite, à décider par le propriétaire sur la
proposition de l'étape 2 — refuser la saisie, ou arrêter la carrière de
fonctionnaire à la limite et liquider sa pension à la radiation des cadres —,
puis chaque exception modélisée, en Python puis en JavaScript, avec ses
témoins. La note du 10 octobre liste en outre deux règles du scénario 1 que les
départs très tardifs atteignent pour la première fois, à relire au texte.

### 152. Les cas types statutaires et non salariés à leur place dans l'EIR : le niveau et la carrière de chacun — `en cours`

**Reprise, au 14 octobre 2026.** Faites, les étapes 1 à 4 : le militaire au
militaire moyen du jaune budgétaire ; l'exploitant agricole et la profession
libérale gardent leur cas type, leur niveau moyen tenant contre la DREES. Les
libéraux restent trop haut (72 % des hommes au cinquième quintile, pour 45) :
la population resserre un seul libéral de la Cipav, que sa pension plafonne,
quand l'EIR mêle dix sections. Au propriétaire : décliner les libéraux de la
population par section, après avoir certifié le revenu de chacune, ou
consigner l'écart. Les deux civils de l'État, mesurés au passage, relèvent de
la dispersion des carrières statutaires, chantier à part, comme les
relèvements agricoles (action 147). Détail : la note de l'étape 4.

**D'où elle vient.** La population de l'action 136 (étape 6), rangée le
12 octobre 2026 dans les quintiles de la pension en équivalent carrière
complète des résidents de l'EIR 2020, régime par régime, met quatre groupes
ailleurs que l'enquête. Chez les hommes : 60 % des militaires au troisième
quintile, quand l'EIR en met 50 % au quatrième ; 62 % de la CNRACL sous le
quatrième, pour 42 ; 88 % des exploitants agricoles au premier, pour 41 ; 72 %
des professions libérales au cinquième, pour 45. Chez les femmes, les
militaires et la CNRACL trop bas aussi, les libérales trop haut, les
exploitantes à leur place. La déclinaison n'y est pour rien : c'est le cas
type qu'elle décline (`castypes.py`) — le militaire parti à 44 ans après
25 années de services, au niveau de 0,95 salaire moyen, sans second métier ;
le fonctionnaire territorial ou hospitalier actif, de catégorie C, parti à
57 ans ; l'exploitant agricole, à la moitié du salaire moyen ; la profession
libérale, à 2,5 salaires moyens. Ce sont ceux de la page Coût. Recalée sur la
dépense de chaque groupe du COR (`cout.py`, action 147, étape 8), elle tient
la dépense de chaque groupe, non sa composition : elle compte 6,3 % de
militaires et 6,3 % d'exploitants parmi les hommes, pour 4,3 et 4,2 % dans
l'EIR, et ses scénarios se comparent sur ces poids. Le détail : la note des
régimes (`docs/archives/feuille_de_route/136/2026-10-12-etape-6-regimes.md`).

**Décidé le 12 octobre 2026 par le propriétaire** : une action à part, plutôt
qu'un calage du niveau de chaque groupe de la population sur sa place dans
l'EIR, qui l'aurait détachée des cas types de la page.

**Ce qui est à faire**, un groupe à la fois — les militaires, la CNRACL, les
exploitants agricoles, les professions libérales, puis les fonctionnaires
civils de l'État, un peu bas eux aussi :

1. Lire ce qui place le groupe : sa ligne dans les quintiles des résidents
   (`quintiles_eqcc_residents.csv`, certifiée), et ce que sa caisse et la
   DREES publient de ses pensions, de ses durées et de ses âges de départ ;
   dire ce qui en écarte le cas type — le salaire, la durée, l'âge de départ,
   le second métier, les bonifications.
2. Corriger le cas type sur sa preuve, ou lui en adjoindre un second quand le
   groupe en réunit deux. C'est un changement du modèle (`src/CLAUDE.md`) :
   les cas types portent aussi d'autres résultats, les indicateurs de cycle de
   vie par exemple, et ce qui bouge se dit par `scripts/resumer_temoins.py`.
3. Remesurer la population (`grille_large.py --grille population`), qui
   hérite de ces cas types : la part des hommes au minimum, 16,7 % pour 9,8
   dans l'EIR le 12 octobre, en dépend d'abord.

**Décidé le 12 octobre 2026 par le propriétaire**, sur la lecture des
militaires (note de l'étape 1) : pour eux, déplacer le cas type existant plutôt
que lui en adjoindre un second ; pour tous, l'ordre des groupes du plan.

**Décidé le 13 octobre 2026 par le propriétaire**, sur la lecture de la CNRACL
(note de l'étape 2) : garder son cas type, juste en niveau ; faire de la
dispersion des carrières statutaires dans la population un chantier à part.

**Décidé le 13 octobre 2026 par le propriétaire**, sur la lecture des
exploitants agricoles (note de l'étape 3) : garder leur cas type ; faire des
relèvements des pensions agricoles déjà liquidées un chantier à part.

**Le 14 octobre 2026**, à l'étape 5 de l'action 159, devant le choix de
garder, de déplacer ou de scinder l'agent de la CNRACL sur les départs de 2025
du jaune pensions, le propriétaire a demandé « ce qui est le plus propre ». La
session a déplacé le cas type : au taux plein, à 0,9 salaire moyen, entré à la
CNRACL après six ans de contrat sur la page Coût ; et fait entrer le civil de
l'État dans son régime au délai que mesurent les services du jaune. Le détail :
la note de cette étape (`docs/feuille_de_route/159/`).

**Ce que le propriétaire tranche** : s'il faut un cas type de plus par groupe
plutôt que déplacer celui qui existe, et l'ordre des groupes.

### 153. L'oracle au-delà des carrières simples : ce qu'OpenFisca calcule et que le dépôt ne lui confronte pas — `en cours`

**Reprise, au 16 octobre 2026.** Faites, les deux étapes : la dernière
famille, les périodes assimilées (`openfisca_periodes_assimilees.py` et son
test), n'a rien trouvé chez nous — durée, plafond de l'année, durée cotisée,
surcote, minimum contributif concordent — et un écart chez OpenFisca : aucune
surcote l'année de l'âge légal (D. 351-1-4). Vingt-sept erreurs chez lui en
tout, quatre chez nous. Ne restent que deux décisions du propriétaire : le
signalement à OpenFisca, et la borne du 2 août 1951 (KALI) ; l'action se clôt
quand il les aura prises. Détail : la note des périodes assimilées, du
16 octobre.

**D'où elle vient.** L'action 136 (étape 2). Le 1er octobre 2026, les
48 profils que l'oracle confrontait à OpenFisca-France-Pension
(`tests/test_oracle.py`) étaient des carrières continues à salaire nominal
constant, sans enfant ni interruption, sédentaires et sans prime dans la
fonction publique : la convention l'a voulu, pour que la traduction d'un
modèle à l'autre ne devienne pas l'objet du test. OpenFisca calcule pourtant,
et le plus souvent teste, la majoration de durée et la bonification pour
enfants, la majoration de 10 %, les points enfants de l'Arrco, la catégorie
active, la carrière longue de la fonction publique, les minima garanti et
contributif, la minoration de l'Arrco, les périodes assimilées année par
année, le salaire annuel moyen sur des salaires qui varient : son point
`a_reprendre` au registre (`data/reference/referents.yaml`).

**Ce qui est à faire**, une famille de profils à la fois, chacune avec sa
convention de traduction écrite — les nombres d'enfants d'OpenFisca et son
unique date de naissance, contre les naissances datées du dépôt, par
exemple :

1. Les deux règles que l'action 136 lui avait prises : le temps partiel des
   fonctionnaires, dont OpenFisca réduit lui aussi les services, et à qui
   aucun profil à temps partiel n'a encore été passé ; le départ anticipé des
   parents de trois enfants, écrit à l'action 138 (étape 17, deuxième
   partie), qu'OpenFisca code avec quatre tests.
2. Les autres familles que le registre nomme. Un écart se tranche par la
   preuve (`docs/architecture.md`, § 3.3).

**Ce que le propriétaire tranche** : s'il faut signaler à OpenFisca les sept
erreurs que l'oracle a trouvées chez lui — un geste vers l'extérieur, qui
l'inviterait aussi à relire le dépôt.

### 158. Les grilles indiciaires de la fonction publique : la carrière d'un fonctionnaire pré-remplie depuis son corps, plutôt que de mémoire — `en cours`

**Reprise, au 13 octobre 2026.** Faite, l'étape 1, les sources et le
périmètre : les grilles de l'État sont ouvertes et datées dans le Noyau RH du
CISIRH (licence ouverte, juillet 2026), depuis 1989 pour les enseignants, de
2005 à 2011 pour les autres grands corps ; celles de la territoriale et de
l'hospitalière ne sont qu'au LEGI, dont l'index du dépôt ne garde pas les
grilles (144 textes de l'État absents sur 489). Reste : que le propriétaire
tranche le périmètre, puis l'étape 2, qui commence par élargir le filtre de
l'index (`THEMATIQUE`) et le faire reconstruire (`index-dila.yml`, entrée
`reconstruire`), sauf périmètre limité à l'État. Détail : la note de l'étape 1.


**D'où elle vient.** La demande du propriétaire, le 12 octobre 2026 : aller
chercher les grilles de salaire connues, celles des métiers publics d'abord,
pour que l'assuré parte d'une carrière pré-remplie plutôt que de ses
souvenirs. Le besoin est là où le simulateur est le plus faible. Le relevé
déposé en PDF donne au salarié ses revenus, année par année, mais au
fonctionnaire ses seuls services — « Du 01/09/1996 au 31/08/2001 » —, sans
traitement : la ligne « reste à saisir » (`docs/limites/5-hors-du-modele.md`).
Reste la carrière paramétrique, qui ne connaît qu'un niveau rapporté au
salaire moyen, le profil moyen que le modèle lit chez l'INSEE pour le statut,
et une seule part de primes pour toute la carrière (`saisie.py`).

**Ce que le dépôt a, ce qui lui manque.** Le traitement indiciaire brut est
l'indice majoré multiplié par la valeur du point, que le dépôt tient du LEGI
(`legislation/point_indice_fonction_publique.csv`), et la fiche de paie d'un
agent public l'entoure déjà : la RAFP, l'indemnité compensatrice de la CSG
(action 138, étape 12), les primes soumises à retenue (étape 17), le temps
partiel. Manque l'indice de chaque année, que donnent le corps, le grade,
l'échelon et la grille en vigueur à la date. Le décret de chaque corps fixe
l'indice brut de ses échelons et leurs durées ; l'indice majoré se lit au
barème du décret n° 82-1105 du 23 décembre 1982, qui bouge seul : cinq points
pour tous au 1er janvier 2024, par le décret n° 2023-519 du 28 juin 2023.

**Les primes pèsent moins qu'on ne le craint sur la pension.** Celle d'un
fonctionnaire se compte sur son traitement et sa nouvelle bonification
indiciaire, primes exclues — l'assiette `hors_primes` de sa fiche, sur
laquelle le modèle rebâtit aussi le compte notionnel des cotisations passées.
Les primes n'y entrent que par la RAFP, plafonnée à 20 % du traitement, et
par les quelques primes soumises à retenue ; le réglage du taux uniforme, qui
porte un seul taux sur toute la rémunération, leur en donne davantage. La
grille porte donc l'essentiel, et les primes se rangent en trois familles :

- celles qu'une règle fixe pour tous, qui se calculent : l'indemnité de
  résidence selon la commune, le supplément familial de traitement selon les
  enfants, les indemnités forfaitaires d'un corps, comme celles des
  enseignants ;
- celles que décident l'employeur et le poste — le RIFSEEP, les heures
  supplémentaires, la nouvelle bonification indiciaire elle-même — : aucune
  grille ne les donne, et un taux moyen par corps ou par catégorie en
  tiendrait lieu, que l'assuré corrige. En moyenne, près du quart du salaire
  brut des fonctionnaires (23,8 % en 2021, chiffre du rapport annuel de la
  DGAFP relevé dans la presse, à lire à la source), très inégal d'un corps à
  l'autre ;
- ce que disent, depuis 2005, les points du RAFP, si le relevé les porte
  année par année : ce que l'agent a touché hors traitement, ou, le plafond
  atteint, le traitement lui-même, qui contrôlerait la grille.

**Ce qui est difficile**, outre les primes. Le nombre et l'histoire : des
centaines de corps et de cadres d'emplois, des grilles refaites à chaque
réforme — la dernière grande, le protocole « parcours professionnels,
carrières et rémunérations » (PPCR), appliqué à partir de 2016 —, chacune
avec son tableau de reclassement, qu'une carrière commencée en 1990 traverse
plusieurs fois. Le chemin, ensuite, qui n'est pas écrit d'avance : l'échelon
avance à la durée que fixe le statut, mais qui variait avec la notation avant
PPCR — trois rythmes chez les enseignants jusqu'en 2017 —, et le grade se
gagne au choix. Une carrière pré-remplie suppose donc un chemin type, que
l'assuré corrige de ce qu'il sait : son grade et son échelon d'aujourd'hui,
qui sont sur sa fiche de paie, et la date de ses promotions.

**Ce qui est à faire**, une étape par session :

1. **Les sources et le périmètre**, sans une ligne de code. Les corps les plus
   nombreux de chaque versant, et la part des titulaires qu'ils couvrent ;
   pour chacun, le décret de son échelonnement indiciaire, et jusqu'où le LEGI
   en garde les versions. L'index de la DILA ne les a peut-être pas : son
   filtre (`THEMATIQUE`, `scripts/fetch/dila_index.py`) retient « indice
   brut », mais ni « indices bruts » ni « échelonnement indiciaire », essayé
   le 12 octobre 2026. Puis ce que le noyau RH de l'État publie en licence
   ouverte (le CISIRH, sur data.gouv.fr : nomenclatures des corps et des
   grades, recueil des fiches carrières, guide de l'avancement d'échelon), et
   s'il date ses grilles ; les circulaires des centres de gestion, pour
   recouper la territoriale ; ce que le relevé porte des points du RAFP ; les
   taux de primes par corps de la DGAFP et de l'INSEE.
2. **Les grilles, en données certifiées** sous `data/reference/` : par corps,
   ses grades, ses échelons, leurs indices bruts et leurs durées, chaque
   version datée de son texte, et le reclassement d'une version à la suivante.
   Un test y recompose le traitement mensuel qu'une source publiée affiche
   pour quelques échelons.
3. **La carrière que la grille donne**, en Python puis dans son jumeau : du
   corps, de la date d'entrée, des dates de promotion que l'assuré connaît et
   de la quotité, l'indice de chaque année, donc le traitement. Le chemin type
   par défaut est un choix écrit ; avant la plus ancienne grille connue, le
   profil de l'INSEE reprend la main, et la page le dit.
4. **Le formulaire** : « pré-remplir depuis une grille » écrit les lignes du
   relevé, que l'assuré voit et corrige, plutôt qu'un calcul caché ; l'adresse
   garde ainsi toute la simulation. Une ligne de relevé porte la rémunération
   entière, que la part de primes partage : le pré-remplissage écrit le
   traitement divisé par un moins cette part, ou la saisie apprend à recevoir
   le traitement seul. Puis la liste d'un champ de saisie de plus
   (`moteur/CLAUDE.md`).
5. **Les primes** : celles qu'une règle fixe, calculées ; pour les autres, le
   taux moyen du corps, année par année, en défaut de la part de primes ;
   puis les points du RAFP du relevé, s'ils la disent mieux.

**Ce que le propriétaire tranche** : le périmètre de départ — quelques corps
d'un versant, ou les trois versants ensemble, et les militaires, dont les
grilles et les primes sont à part ; le chemin type, à la durée moyenne ou à la
plus lente ; une part de primes par période plutôt qu'une pour toute la
carrière ; si les grilles servent aussi aux cas types statutaires de
l'action 152, le fonctionnaire de catégorie C et le militaire ; et si les
grilles des entreprises à statut (SNCF, RATP, IEG) suivent, les minima des
conventions collectives ne disant qu'un plancher, non un salaire.

### 159. Le jaune pensions du PLF 2027, exploité en entier : rangé, puis chaque tableau à sa place dans le dépôt — `en cours`

**Reprise, au 13 octobre 2026.** Faites, les étapes 0 à 2 : l'inventaire ; le
jaune au manifeste (`sre_jaune_pensions_2027`, licence ouverte Etalab 2.0),
avec pour miroir la branche `jaune-2027`, qui se garde ; les bonifications,
lues par `sre_jaune_pensions.py`, qui sait les deux éditions, et certifiées
dans `bonifications_jaune.csv`. Les étapes 3 à 9 se mènent en parallèle, une
par zone : chacune tient son bloc « Reprise » sous le titre de sa note, et
celui-ci ne se récrit plus. Commencer par celle de sa zone. Détail : les notes
des étapes 0 à 2.

**D'où elle vient.** La demande du propriétaire, le 13 octobre 2026, le jaune
lu pour l'action 129 : « Je veux garder ce doc et le ranger correctement sur
la branche principale. Il y a énormément d'informations importantes dans ce
document pour notre projet. Il faut faire une action qui exploite toutes les
informations de ce document. »

**Le document.** Le « Rapport sur les pensions de retraite de la fonction
publique » annexé au PLF 2027, 250 pages, créé le 12 octobre 2026 par la
direction du budget avec la DGAFP, le Service des retraites de l'État et la
Caisse des dépôts. Sa matière : le stock de pensionnés au 31 décembre 2025 et
le flux des pensions entrées en paiement en 2025, plus récents que ceux du
jaune 2026 dont le dépôt tire déjà ses bonifications ; et, nouveaux, le poids
des pensions dans chaque budget ministériel, une présentation alternative du
CAS Pensions, ce que l'État verse aux régimes spéciaux, les engagements de
retraite à fin 2025. budget.gouv.fr le sert depuis le 13 octobre et refuse le
cloud ; l'Assemblée, qui servait le jaune 2026 octet pour octet, ne le porte
pas encore. Le PDF n'entre pas dans l'historique de `main` : un test refuse
tout document versionné sous `data/brut/`, et le manifeste range un document
par son miroir, ici la branche `jaune-2027`, où le propriétaire l'a déposé.

**Ce que le dépôt tire déjà de l'édition 2026**, et qui passe à 2027 dans
l'étape de sa zone : `bonifications_jaune.csv` (tableaux A-7, 50 et B-1, lus
par `scripts/fetch/sre_jaune_pensions.py`, niveau `certifiee`) et les fiches
d'`avantages_non_contributifs.yaml` qui y renvoient ; le militaire moyen et
l'agent de la CNRACL des cas types (`castypes.py`, action 152) ; les effectifs
de cotisants de l'État (`donnees/cotisants.py`) ; des référents
(`referents.yaml`) ; la clé civils-militaires de la page Coût.

**Ce qui est à faire**, une étape par session ; après la 1, en parallèle, une
par zone. Le détail, tableau par tableau et page par page, est dans la note de
l'étape 0.

0. **L'inventaire** : fait le 13 octobre.
1. **Ranger le document** (données) : fait le 13 octobre. La fiche
   `sre_jaune_pensions_2027` du manifeste, avec son empreinte et sa licence ;
   pour miroir, la branche `jaune-2027`, budget.gouv.fr refusant aussi le
   workflow de la release. L'Assemblée, quand elle servira le jaune, pourra la
   remplacer : la branche se supprimera alors.
2. **Les bonifications** (données) : fait le 13 octobre.
   `sre_jaune_pensions.py` lit l'édition 2027 sans perdre celle de 2026 ;
   `bonifications_jaune.csv` porte le stock et le flux de 2025 (A-7, 50, B-1),
   et les cinq fiches qui les citent, les chiffres de 2025. Le tableau B-22,
   qui dénombre les bonifications du flux, reste à lire (étape 4).
3. **Les taux et les barèmes, en contrôle** (données) : taux salariaux et
   employeurs (13, 14, 35, 36, D-2), Ircantec depuis 1992 (24), paramètres du
   RAFP de 2005 à 2026 (22B), revalorisation des pensions (110), durée requise
   (33, 34), décote (38), minimum garanti (45, 46), âges de la catégorie
   active (57), dépaysement et campagne (48, 49), indemnité temporaire de
   retraite (54, 55), panorama des régimes (12), confrontés aux séries et aux
   fiches du dépôt ; un écart se déclare ou se corrige, en commit à part.
4. **Les référents** (données) : pensions moyennes, âges, durées, minimum
   garanti, décote et surcote, taux de liquidation, du stock et du flux de 2025
   (A-1 à A-8, B-1 à B-21, tableaux 60 à 108), dans `referents.yaml`, que les
   tests confrontent au modèle.
5. **Les cas types** (modèle, avec l'action 152) : le militaire moyen, l'agent
   de la CNRACL et le civil de l'État recalés sur le flux de 2025 (B-4, B-5,
   95 à 97).
6. **Le financement et le coût** (modèle) : ce que l'État verse aux régimes
   spéciaux (5), le CAS Pensions (17 à 19, D-3), la CNRACL (20, 21, D-4, 116),
   les ouvriers d'État (23), les ratios démographiques (113 à 115), les
   cotisants (D-5), les engagements (10, 11), contre
   `donnees/financement_regimes.py`, `donnees/cotisants.py` et `cout.py`.
7. **La population** (modèle) : la pyramide des âges des agents (87 à 91), les
   polypensionnés (15, 16), les départs anticipés de 2015 à 2025 (C-1 à C-9),
   les décès de pensionnés (B-13), contre ce que le modèle suppose.
8. **Le site** (site) : la fiche de paie du civil et du militaire primes
   comprises (figures A et A bis) contre celle de la page ; la comparaison des
   règles publiques et privées que l'éditorial cite (DREES, génération 1958),
   et les taux de remplacement, en regard des résultats du site ; la part des
   pensions dans chaque budget ministériel (figures 3B, B et B bis).
9. **Les règles** (scénario 1, par `docs/veille_droit.md`) : ce que la partie
   III décrit du droit — minimum garanti, bonifications, majorations, cumul,
   réversion, carrières longues, rachats, invalidité, départs anticipés —
   confronté aux fiches de la carte. Le jaune est un exemple officiel : le
   texte tel que la caisse l'applique l'emporte.

**Ce que le propriétaire tranche** : l'ordre des étapes 2 à 9 ; et, pour
l'action 129, la convention du jaune, le taux du régime général, comme valeur
de `contribution_etat`.

### 161. Un seul exemplaire du code : les doublons entre le Python et le JavaScript retirés une paire à la fois, chaque retrait relu — `en cours`

**Reprise, au 22 octobre 2026.** Faites, les étapes 1 à 5 : le pont fait
tourner le portage pour la fabrique et le coût (`retraite_notionnelle/pont.py`),
et, le 22 octobre, `cycle_de_vie.py` est parti — ses tests passés au portage
(`tests/js/cycle-de-vie.test.js`), ses explications dans `cycle-de-vie.js`.
Reste l'étape 6 : les paires du moteur, une à une, dans l'ordre de la carte
(`python scripts/jumeaux.py`, 68 paires), relecture d'abord ; d'une paire de
données, le propriétaire tranche le jumeau qui reste (note 0003). Détail :
`2026-10-22-etape-5-septieme-partie-le-retrait-du-cycle-de-vie.md`.

**D'où elle vient.** La demande du propriétaire, le 14 octobre 2026 : « Je
veux enlever les doublons entre JavaScript et python. […] Il faut le meilleur
au cas par cas. Python a ses avantages, JavaScript a les siens. Je veux
quelque chose de pragmatique pour avancer de façon sûre et sans faire
d'erreur sur le projet. […] Il faut que chaque ligne de code supprimée soit
vérifiée pour voir si on ne casse pas des dépendances cachées et aussi au
passage vérifier notre code. Ça permet de faire une passe de relecture pour
déceler les erreurs dans le code existant. »

**Le constat, mesuré avant de rien retirer.** Sur les 845 cas des témoins,
157 418 valeurs, 97,3 % sont identiques au bit près, et l'écart relatif le
plus grand vaut 9 × 10⁻¹⁵ : le bruit d'arrondi des flottants, non un écart de
calcul. Le risque est ailleurs : dans ce que les tests de concordance
n'exécutent pas, et dans ce qui dépend d'un jumeau sans l'importer — les
fiches qui nomment leurs fonctions, les chiffres ancrés qui chargent un module
par son nom, les chaînes qui nomment un fichier.

**La règle.** Chaque morceau de code n'existe qu'une fois, dans le langage de
l'endroit où il tourne : dans le navigateur, le JavaScript, sans choix ; à la
fabrique seulement, le Python ; aux deux endroits — le moteur d'une carrière,
que le site fait tourner pour un lecteur et le coût pour une population —, un
seul exemplaire, en JavaScript, que le Python fait tourner par node comme il
le fait déjà pour les pages (`web/site.py`), et en dernier. Elle récrit le
principe 4 (« une implémentation fait foi : aujourd'hui, le Python ») : une
note de décision d'abord (`docs/architecture.md`, § 13.1 et 13.3).

**La méthode, une paire par étape.** Relever tout ce qui dépend du jumeau à
retirer (`python scripts/jumeaux.py <nom>`) ; mesurer ce que les tests de
concordance en exécutent, des deux côtés (`--couverture`) ; relire la paire
fonction par fonction, chaque différence tranchée contre la source, la fiche
et le texte, aucun jumeau n'ayant raison par défaut (§ 3.1), et l'erreur
corrigée dans celui qui reste, avec son test ; fixer par des témoins ce que
les tests n'exécutaient pas ; brancher les dépendants sur celui qui reste ;
retirer, dans un commit à part, les témoins identiques. La relecture vaut
d'elle-même, avant tout retrait, et se mène sur n'importe quelle paire.

**Ce qui est à faire**, une étape par session :

1. **La carte des jumeaux** — faite le 14 octobre 2026.
2. **La note de décision** — validée le 14 octobre 2026 :
   `docs/decisions/0003-un-seul-exemplaire-du-code.md`.
3. **Le pilote** : le lecteur du relevé (`web/releve_lu.py` et
   `releve-lu.js`), que ni le coût ni la fabrique n'atteignent — fait le
   14 octobre 2026 : le jumeau Python est parti.
4. **Les deux autres paires hors du coût et de la fabrique**, chacune tranchée
   à sa relecture : `cycle_de_vie.py`, dont le jumeau attend l'étape 10 de
   l'action 138, qui l'affiche ; `scripts/fetch/lecture_pdf.py`, dont quatorze
   scripts de la fabrique ont besoin hors du site.
5. **Le pont** : le coût et la fabrique font tourner le moteur JavaScript par
   node, jusqu'à des témoins et des agrégats identiques.
6. **Les paires du moteur**, une à une, dans l'ordre de la carte, relecture
   d'abord.

**Ce que le propriétaire tranche** : pour chaque paire, le jumeau qui reste,
quand la règle de l'endroit ne suffit pas (note 0003) : les données, le
lecteur de PDF.

### 162. Le test d'abord : le développement piloté par les tests, sur tout le dépôt — `en cours`

**Reprise, au 17 octobre 2026.** Faites, l'étape 1 — la règle du test
d'abord dans les consignes, et le hook qui refuse une fois par commit la
première retouche du code sans rouge vu — et, à la demande du propriétaire,
la garde durcie : `pousser.sh` refuse d'envoyer un commit qui change le code
sans toucher aux tests, sauf s'il le déclare (`Sans-test: <raison>`). Reste
l'étape 2, après une semaine de sessions : relever les commits déclarés
`Sans-test` et leurs raisons, et, dans les transcriptions, les refus, pour
dire au propriétaire si la garde refuse à tort ou laisse passer. Détail :
`162/2026-10-17-l-envoi-sans-test-refuse.md`.

**D'où elle vient.** La demande du propriétaire, le 17 octobre 2026 : « Sur
ce dépôt, je veux utiliser le TDD : Test driven development. »

**Les étapes.**

1. **La règle et sa garde**, faite le 17 octobre 2026 : la règle dans les
   consignes, et le hook qui la rappelle au moment de toucher au code.
2. **La mesure**, après une semaine de sessions : parmi les commits de la
   semaine, ceux qui touchent au code (`src/`, `moteur/`, `scripts/`,
   `.claude/hooks/`) sans toucher aux tests ; dans les transcriptions, les
   rappels du hook, et ce que chaque session en a fait.

**Ce que le propriétaire tranche**, à l'étape 2 : la force de la garde —
la garder telle quelle, la durcir (refuser à chaque fois, ou refuser l'envoi
d'un commit qui change le code sans test), ou l'alléger.

### 163. Ce que la revue de code d'Anthropic apprend au dépôt : le site en ligne au vert, les rouges classés, puis un relecteur — `en cours`

**Reprise, au 19 octobre 2026.** Faites, les étapes 1, 2, 4 et 6, et les
quatre gardes que la deuxième proposait : le site ne part en ligne que d'une
suite verte ; les rouges sont classés et comptés ; les chiffres cités du
README et de l'accueil sont produits ; ceux du parcours, hors des saisies,
ancrés, en lettres comme en chiffres, années de données comprises ; ses
étiquettes de repères et ses noms d'onglets, tenus par le filet du site ; dix
tests d'une seconde sont de la suite rapide ; `pousser.sh` joue les tests de
la feuille de route, et refuse une garde changée sans `Garde-modifiée:`.
Restent les étapes 3 et 5, que le propriétaire tranche. Détail :
`163/2026-10-19-les-onglets-du-parcours.md`.

**D'où elle vient.** Le 17 octobre 2026, le propriétaire soumet à une
session l'article « How the Claude Code team does code review » (blog
claude.dev, 15 octobre 2026) : « Est-ce que c'est utile pour notre projet ? ».
Le service qu'il présente ne relit que des pull requests, que le dépôt n'a
pas ; la session en tire six pratiques transposables, et le propriétaire
lance les deux premières : « vas-y ».

**Les étapes.**

1. **Le site en ligne au vert**, faite le 17 octobre 2026 (leur canal
   « latest » avant « stable ») : `publier_fabrique.sh` dit `en_ligne=oui`
   d'une suite verte sur `main`, et `tests.yml` déploie alors l'arbre du
   commit publié.
2. **Les rouges classés**, faite le 17 octobre 2026 (leurs incidents changés
   en jeu d'épreuve, et leur taux comme garde-fou) : pour chaque verdict rouge depuis le 6 octobre, le
   test, la zone, et ce qui l'aurait vu avant l'envoi — `pytest -m rapide`,
   les tests de la zone, ou rien quand le rouge naît de deux sessions que
   `pousser.sh` a rebasées l'une sur l'autre sans relancer de test, ce
   qu'empêche leur file de fusion ; puis le taux de rouges au tableau de bord.
3. **Un relecteur à soi**, sur Opus, pour les étapes qui écrivent une règle
   du scénario 1 : il dit ce qu'est un échec ici, cite `fichier:ligne` et
   l'article de loi, renvoie l'ancien à la feuille de route ; chaque constat
   reçoit une réponse dans la note d'étape ; `pousser.sh` exige `Relu:` ou
   `Sans-relecture: <raison>`. Éprouvé d'abord sur des règles corrigées après
   coup : s'il ne les trouve pas, il ne vaut pas son coût.
4. **La classe, pas le cas**, faite le 17 octobre 2026 : un défaut corrigé
   dans une règle se cherche dans les autres régimes ; une ligne de la liste
   de contrôle de `src/CLAUDE.md`.
5. **Une passe de fond chaque semaine** : une session programmée, après la
   mise à jour de l'index DILA du lundi, relit une famille de règles du
   scénario 1 contre le droit en vigueur, inscrit ce qu'elle trouve sans le
   corriger, et en rend au propriétaire une explication courte.
6. **Les gardes gardées**, faite le 17 octobre 2026 : `pousser.sh` exige
   `Garde-modifiée: <raison>` sur un commit qui touche les workflows, les
   hooks et leurs réglages, `pousser.sh` ou `publier_fabrique.sh`, et la
   session demande d'abord au propriétaire.

**Ce que le propriétaire tranche** : les chiffres à unité du parcours, puis,
une à une, les étapes 3 et 5. Les quatre gardes de l'étape 2 sont faites le
17 octobre 2026.

### 173. Le site sur tous les écrans : rien ne déborde, ce qui va ensemble se voit ensemble, moins de vide, moins de mots — `en cours`

**Reprise, au 23 octobre 2026.** Faites, les étapes 1 et 2 : de 320 à 1 440
points, rien ne déborde ni ne défile en largeur ; les graphiques se dessinent à
la largeur de la colonne, leur légende contre eux ; les quatre systèmes du
simulateur tiennent dans un écran ; les grands vides sont tenus. Un vrai
navigateur le joue, `tests/test_ecrans.py`. Restent les étapes 3 à 10, une
page par session : moins de mots, sans perdre une idée. Par quoi commencer :
l'étape 3, l'accueil — serrer son budget de lecture (`BUDGETS_DE_LECTURE`,
`tests/test_web.py`), le voir rouge, puis récrire. Détail :
`173/2026-10-23-etapes-1-et-2-ecrans-et-vides.md`.

**D'où elle vient.** Le 23 octobre 2026, le propriétaire : « Le site web de
notre projet est plutôt adapté aux écrans d'ordinateurs (et encore...) mais
pas pour les autres types d'écrans. Il faudrait que le site soit adapté à
toutes les tailles d'écrans. Je suis convaincu qu'il y a trop de texte même
sur ordinateur. On peut dire la même chose en moins de mots sans pour autant
perdre le sens des idées. J'ai aussi remarqué qu'il y avait beaucoup
d'espaces sans forcément de justifications. Il y a aussi des contenus qui
débordent ou demandent de faire glisser de gauche à droite sur mobile comme
les graphiques. [...] Il faut aussi que certaines informations apparaissent
en même temps à l'écran sans quoi il est frustrant de comprendre
l'information. Par exemple, les différents scénarios du simulateur ou encore,
un graphique et sa légende. »

**Les étapes.**

1. **Rien ne déborde, et ce qui va ensemble se voit ensemble**, faite le
   23 octobre 2026 : un test qui pilote Chromium à cinq largeurs, sans
   dépendance ; les tableaux repliés sous la largeur où ils cessent de tenir ;
   les courbes, les schémas de Sankey, la cascade et la frise dessinés à la
   largeur de la colonne ; les cartes à publier lisibles sur un téléphone ;
   les quatre systèmes du simulateur en cartes, deux par deux ou quatre de
   front ; chaque légende à côté de son tracé, ou au-dessus.
2. **Les vides**, faite le 23 octobre 2026 : le plus grand écart entre deux
   blocs voisins tenu à quarante points sur un téléphone, cinquante-six au
   large ; la ligne réservée sous chaque graphique à une aide invisible, et
   le pied de page de cinq rem, retirés.
3. **Moins de mots : le Programme**, l'accueil.
4. **Moins de mots : Simuler**, le formulaire et les résultats.
5. **Moins de mots : Coût.**
6. **Moins de mots : Pourquoi changer.**
7. **Moins de mots : Partager et Le saviez-vous ?**
8. **Moins de mots : Carrières types.**
9. **Moins de mots : Droits non cotisés.**
10. **Moins de mots : Méthode et sources.**

Pour chaque page des étapes 3 à 10 : serrer d'abord son budget de lecture, le
voir rouge, puis récrire, chaque idée gardée et chaque chiffre à sa place ;
une phrase en gras qui change passe au catalogue des affirmations ; chercher
en chemin, dans la page, ce qui se lit ensemble et ne se voit pas ensemble —
le propriétaire n'a donné que deux exemples ; `construire_temoins.py`,
`python -m pytest -m site`, qui joue aussi le navigateur.
