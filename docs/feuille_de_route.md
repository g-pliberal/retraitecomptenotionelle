# Feuille de route — les actions qui font le plus progresser le modèle

Ce fichier est la liste des chantiers à mener, classés par ce qu'ils déplacent
dans les résultats du dépôt. Il sert de point d'entrée à une session de travail :
prendre l'action la plus haute qui n'est pas commencée, la mener au bout, puis
mettre à jour ce fichier. *Précisé le 23 septembre 2026* : aucune action n'est
plus « à faire », la liste s'allongeant par la fin à mesure que les sessions
ouvrent les leurs ; une session commence donc par les actions `en cours` et ce
que leurs dernières notes laissent ouvert. Deux numéros servent deux fois,
37 et 38 : chaque paire se distingue par son titre, et les renvois du dépôt
nomment l'une ou l'autre. Il ne remplace ni `limites.md`, qui dit ce que vaut
chaque chiffre, ni `regimes.md`, journal de la campagne sur les régimes.

**Comment le tenir.** Une action a un état — `à faire`, `en cours`, `fait` — et
une ligne « ce que ça a déplacé » quand elle est faite, comme les tranches de
`regimes.md`. Toute session qui touche au scénario 1 commence par
`python scripts/veille_droit.py` et finit par une entrée au journal de
`data/reference/legislation/veille.yaml` : voir `docs/veille_droit.md`. Une action qu'on abandonne ne disparaît pas : elle passe en bas,
avec la raison, et l'action elle-même dans l'archive. Une découverte faite en chemin qui mérite un chantier se note
ici, pas dans un commentaire de code.

**Le constat de septembre 2026, qui fonde ce classement.** La couverture des
régimes est finie : <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire)-->91<!--/--> lignes d'inventaire, plus aucune ligne « à modéliser »,
<!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=partiel)-->39<!--/--> fiches partielles dont chaque mur est documenté dans `regimes.md` et
`limites.md` §4. Continuer sur cet axe rapporte peu : les manques restants
portent sur des populations minuscules ou des barèmes que personne ne publie.
Les gains sont sur ce qui porte les résultats de tête du README : les agrégats
de la page Coût, la part patronale, les taux de cotisation qui sont la matière
même des scénarios notionnels, et l'étalon qu'est le scénario 1.

Un coût transversal pèse sur l'ordre : chaque changement du MODÈLE se paie deux
fois, dans `src/retraite_notionnelle/scenarios/actuel.py`
(<!--chiffre:lignes(src/retraite_notionnelle/scenarios/actuel.py)-->6 687<!--/--> lignes)
et dans le portage `moteur/js/` (<!--chiffre:lignes(moteur/js/*.js)-->38 607<!--/--> lignes), puis dans les
témoins. Les actions 1 à 3 et 6 n'ont touché que les données et la page Coût ;
les actions 7, 9, 10 et 11 ont touché les deux moteurs, comme l'action 5, et
l'action 4 ne les a touchés qu'en surface — deux lignes de chaque côté.
L'action 13 n'a pas touché le modèle du tout : un script de certification, le
format de son journal, et une phrase de la page Données en deux exemplaires.
Toutes sont faites ; ce paragraphe, écrit quand elles étaient à mener, est
passé au passé le 23 septembre 2026.

**Les actions closes sont dans l'archive**, `docs/archives/feuille_de_route.md`,
avec le journal : faites, archivées ou abandonnées, elles y gardent leur
numéro, leur texte et leur ordre (`docs/architecture.md`, § 9.3). Ce fichier
ne garde que ce qui vit : ce qui est délibérément en bas, et les actions
`en cours`, à la fin, où les sessions ouvrent les leurs. Une action qui se
clôt passe, telle quelle, à la fin de l'archive ; un test refuse une action
close ici, ou ouverte là-bas.

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

---

## Les actions en cours

### 47. La garantie vieillesse est une avance : la reprise sur succession, sa règle et son chiffrage — `en cours`

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

### 119. Les complémentaires relues : le plafond du RAFP, les points gratuits de la RCO, l'Arrco des cultes, et trois trous que rien ne disait — `en cours`

**Demande.** « Il me semble qu'il manque encore pas mal de choses sur certains
régimes complémentaires. Tu peux me dire ce qu'il manque ? », puis, la liste
faite : « vas-y, commence par le plafond RAFP », et « vas-y » pour la suite
(23 septembre 2026).

**Ce que la relecture a trouvé.** Les manques connus des complémentaires sont
écrits dans l'inventaire, dans `limites.md` §4 et au registre de veille. La
relecture — inventaire, fiches, les deux moteurs, `sources_a_explorer.yaml`,
puis les textes et les caisses — en a trouvé cinq qui ne l'étaient nulle part,
ici par ordre de poids :

1. *Les points gratuits de RCO des chefs d'exploitation, pour leurs années
   d'avant 2003* : cent par an à qui a cotisé dix-sept ans et demi comme chef,
   dans la limite de trente-sept ans et demi moins ses années de RCO ; sinon
   soixante-six, sur dix-sept ans au plus, depuis 2014 (La retraite en clair,
   le site du GIP Union Retraite). Le dépôt ne connaît que ceux des conjoints
   et des aides familiaux. Tout exploitant parti depuis 2003 a donc une RCO
   sous-estimée au scénario 1 — ce qui flatte les comptes notionnels, dont
   ces points gratuits sont absents par construction.
2. *L'Arrco des ministres des cultes*, obligatoire depuis 2006 pour qui
   perçoit un revenu d'activité individuel, les membres des congrégations en
   étant exclus (réponse ministérielle au Sénat de 2007, tableau des régimes
   du GIP Union Retraite). Le statut `ministre_du_culte`, qui confond les deux
   populations, ne route que la CAVIMAC.
3. *Le plafond de l'assiette du RAFP* : fait, voir ci-dessous.
4. *La majoration pour enfants de l'Ircantec* : 10, 15, 20, 25 puis 30 % de
   trois à sept enfants, selon la base documentaire du régime. La fiche la
   déclare sans barème, et le moteur sert 10 % à partir de trois.
5. *La Nouvelle-Calédonie* : l'inventaire date l'Agirc-Arrco de l'accord
   territorial de 1995 et dit que le statut ne route pas vers la
   complémentaire, quand `affiliations.yaml` route l'Arrco dès 1961 ; le
   compte notionnel y porte trente-quatre ans de cotisations jamais versées.

Un sixième est sorti en lisant l'article 76 de la loi n° 2003-775 pour le
RAFP : le régime n'est ouvert qu'aux fonctionnaires civils, aux magistrats et
aux militaires, et le modèle y affilie les deux statuts d'ouvrier de l'État
depuis 2005. Une piste, enfin, qu'aucun texte lu ne confirme encore : les droits
gratuits accordés à la création de l'Agirc et des institutions de l'Arrco pour
les années travaillées avant, dont le dépôt ne dit rien. Vérifiés et justes,
en revanche : Mayotte et la Polynésie sans Agirc-Arrco, l'adhésion y étant
facultative.

**Ce qui a été fait : le plafond du RAFP.** Les primes n'y cotisent que
« dans la limite de 20 % du traitement indiciaire brut total ou de la solde
brute totale perçus au cours de l'année considérée » : l'article 2 du décret
n° 2004-569 le dit dans ses six versions depuis 2004, l'ERAFP en tête de sa
page sur les cotisations, et la fiche le citait sans qu'aucun moteur le lise.
Un champ de période, `plafond_primes_traitement` ; une méthode,
`PeriodeRegime.part_du_revenu` en Python et `partDuRevenu` en JavaScript, qui
remplace les trois copies du découpage traitement/primes du scénario 1 et du
compte notionnel ; le taux unique, lui, garde la rémunération entière. Les
deux pages de l'ERAFP ont été réservées avant d'être ouvertes (action 89) :
celle des cotisations est `explore`, la calculette, qui part des cotisations
et non des primes, retourne au vivier avec ce qu'elle peut vraiment rendre.

**Ce que ça a déplacé.** Deux témoins sur 505, les deux carrières de
fonctionnaire à 22 % de primes : leur RAFP baisse de 29 %, au scénario 1 comme
dans les compartiments de capitalisation des scénarios notionnels. Les trois
cas types publics cotisaient sur une assiette trop forte de 10, 41 et 67 %.
Aucun écart entre scénarios ne bouge, le RAFP étant servi à l'identique dans
les six.

**Ce qui a été fait ensuite : les points gratuits de la RCO.** Cent points
par année de chef d'avant 2003, dans la limite de trente-sept ans et demi
moins les années de RCO, à qui a dix-sept ans et demi comme chef et le taux
plein de sa retraite de base (D. 732-154, D. 732-151, L. 732-56, II, 2° et
III du code rural, lus dans toutes leurs versions de l'index LEGI). Le taux
plein a changé de nature le 1er septembre 2023 : il fallait en réunir la durée,
il suffit depuis d'avoir liquidé au taux plein, par l'âge aussi (loi
n° 2023-270, art. 18, VI). La page de la MSA sur les non-salariés agricoles,
réservée puis lue en ses quatre onglets, écrit la règle des cent points à
l'identique et la condition d'avant 2023. Un champ de période,
`points_gratuits`, que `_points_gratuits` lit dans les deux moteurs ; les
points entrent au compte de la RCO, la formule le dit (« dont … points
gratuits »), et la cascade les isole sous une neuvième ligne chiffrée,
`points_gratuits_rco`, mesurée comme l'AVPF par un second calcul. Le régime
des 66 points (V et VI de L. 732-56) ne peut pas s'ouvrir dans le modèle : il
demande dix-sept ans et demi d'activité non salariée agricole à un autre titre
que celui de chef, que le modèle ne connaît pas.

**Ce que ça a déplacé.** Quatre témoins sur 509, les chefs d'exploitation du
simulateur : leur pension du scénario 1 monte de 7,5 % pour la génération
1945, 4,3 % pour 1955, 2,1 % pour 1965 et 0,25 % pour 1975. Pour un chef né en
1955, installé à vingt ans et payé la moitié du salaire moyen, les points
gratuits font 56 % de la RCO. La page
Avantages chiffre la ligne à 0,64 Md € en 2024, et le chiffrable passe de 96,1
à 96,7 Md €. Les écarts des comptes notionnels rétroactifs se creusent
d'autant pour ces carrières.

**Deux pistes sorties de la page de la MSA**, pour le régime de base : elle
donne 3 940,51 € de retraite forfaitaire intégrale au 1er janvier 2026 et
4,631 € de point de proportionnelle, quand la fiche, qui les indexe sur les
prix, en tire 3 801,89 € et 4,6693 € ; et la version de D. 732-166 en vigueur
depuis le 14 février 2026 fixe encore la valeur de service de la RCO « pour
l'année 2025 », 0,3919 €, quand le modèle extrapole 2026. À reprendre avec la
réforme des vingt-cinq meilleures années.

**Ce qui a été fait ensuite : l'Arrco des ministres des cultes.** L. 921-1,
complété par l'article 75 de la loi de financement de la sécurité sociale pour
2006, affilie à l'Arrco depuis le 1er janvier 2006 les personnes du régime des
cultes « qui bénéficient d'un revenu d'activité perçu individuellement ». Les
circulaires de la CAVIMAC, qui recouvre la cotisation, en donnent l'assiette —
le forfait du SMIC mensuel, comme ses autres cotisations — et le taux de base,
10,02 %, soit les 7,87 % de l'Agirc-Arrco et ses 2,15 % de contribution
d'équilibre. Le statut `ministre_du_culte` est scindé : il garde son code et
reçoit une fiche `arrco_cultes` depuis 2006, qui emprunte les points de
l'Arrco puis de l'Agirc-Arrco ; `membre_congregation` n'a que la CAVIMAC. Le
ministre du simulateur né en 1975 gagne 14 % de pension au scénario 1, celui
né en 1955 6,2 %.

**Puis le salaire annuel moyen de la CAVIMAC.** La caisse le calcule « sur la
base du SMIC [...] pour tous les assurés cultuels », comme L. 382-27 et le
forfait de R. 382-89 le veulent ; le moteur prélevait la cotisation sur le
forfait mais liquidait sur le revenu saisi. `_assiette_de_reference` prend
désormais, dans les deux moteurs, le forfait de chaque année : à une fois et
demie le salaire moyen, la pension de base du ministre était 2,17 fois trop
haute. La page de la caisse, réservée puis lue, dit aussi que les années
d'avant 1979 sont validées gratuitement, quand le statut affirmait qu'elles ne
portaient aucun droit.

**Ce qui reste**, dans l'ordre où le prendre : les fractions de pension de la
CAVIMAC d'avant 1979, validées gratuitement, et de 1979 à 1997, portées au
minimum contributif ou au maximum de la pension « Cavimac » ; les ouvriers de
l'État hors du RAFP ; le barème de l'Ircantec pour enfants ; le routage calédonien et sa
ligne d'inventaire ; les deux exceptions au plafond du RAFP — la GIPA, cotisée
en entier, les jours de compte épargne-temps convertis — et la cotisation
volontaire des agents de l'État outre-mer ; les 66 points gratuits des
conjoints, aides familiaux et collaborateurs, qui demandent de connaître ces
statuts ; les huit taux spécifiques de l'Arrco des cultes. Les lignes
`rafp_assiette_plafond`, `rco_points_gratuits`,
`cultes_retraite_complementaire` et `cultes_salaire_annuel_moyen` du registre
de veille et les quatre récits de `limites.md` en tiennent le détail.

**Fichiers.** `data/reference/regimes/_schema.yaml`,
`data/reference/regimes/fonction_publique.yaml`, `non_salaries.yaml`,
`inventaire.yaml` et `pivots.yaml` ;
`src/retraite_notionnelle/donnees/regimes.py`, `scenarios/actuel.py`,
`moteur/compte.py`, et leurs pendants `moteur/js/regimes.js`,
`scenario-actuel.js`, `compte.js` ; `scripts/construire_donnees.py` ;
`tests/test_simulateur.py`, `tests/js/moteur.test.js`, les témoins ;
`data/reference/legislation/veille.yaml`,
`data/reference/legislation/avantages_non_contributifs.yaml`,
`data/sources_a_explorer.yaml`, `data/reference/prose/zones.yaml`,
`docs/limites.md`, `docs/regimes.md`, `docs/parcours_presentation.md` ; pour
les cultes, `data/reference/legislation/affiliations.yaml`,
`majoration_enfants_points.csv` et `reformes.yaml`, `data/sources.yaml`,
`scripts/construire_temoins.py`.

### 121. Le droit de chacun, et non celui de la génération de l'année : toutes les personnes vivantes — `en cours`

**Demande.** « Il faut prendre en compte la loi applicable pour tout le monde
et pas seulement pour les derniers entrants ou sortants » ; « il faut aussi
prendre le cas des personnes déjà à la retraite » ; « mon site doit
représenter toutes les personnes encore vivantes sur lesquelles la réforme du
scénario du Parti libéral français pourrait s'appliquer ».

**Le défaut.** Une fiche ne porte qu'un âge par PÉRIODE de liquidation. Quand
le droit indexe l'âge sur la génération, les fiches écrivaient, pour chaque
année, l'âge de la génération qui l'atteint cette année-là : juste pour elle,
faux pour toutes les autres. Un agent des IEG né en 1965 parti en 2030 se
voyait opposer 58 ans et 3 mois au lieu de 56 ans et 4 mois. Et la durée
requise des régimes spéciaux, que la réforme de 2008 indexe sur la DATE où
l'assuré réunit les conditions, leur était lue dans la table commune par
génération : 167 trimestres à un cheminot parti en 2010, dont le droit en
demande 154. Ce sont les retraités, et les générations qui ne partent pas à
l'âge, qui payaient l'approximation.

**Fait le 23 septembre 2026 : la SNCF, la RATP et les IEG.** Les âges se lisent
par génération dans `legislation/ages_regimes.csv` (`age_table`, tables
`sncf_conduite_2011` et `_2023`, `ratp_roulant_2011` et `_2023`,
`ieg_actif_2011` et `_2023`) ; le moteur, qui réservait cette table aux
complémentaires, l'ouvre aux régimes de base en annuités. La durée se lit au
mois où l'agent réunit les conditions : calendrier de 2008
(`legislation/duree_requise_calendriers.csv`), puis tables par génération de
2014 à compter du 1er juillet 2019, de 2023 à compter du 1er janvier 2025
(colonne `depuis` de `legislation/duree_requise_regimes_speciaux.csv`). Les
quinze périodes annuelles de chaque fiche deviennent trois. Un agent de
conduite né en 1955 doit 150 trimestres et non 166, né en 1960 154 et non 167,
né en 1968 166 et non 172 ; un agent des IEG né en 1960 ouvre à 55 ans et
doit 162 trimestres, né en 1965 ouvre à 56 ans et 4 mois. Les pensions du
scénario 1 de leurs retraités remontent de 3 à 11 %. Trois témoins de retraités.

**Ce qui reste, fiche par fiche, et chacune demande de lire son texte.** Le même
relevé, une période par année et aucune lecture par génération depuis 2011,
signale dix autres fiches : `cps_saint_pierre_et_miquelon`, `cssm_mayotte`,
`cps_polynesie`, `cafat_nouvelle_caledonie`, `fonctionnaires_pacifique`,
`crpnpac` et `crpnpac_tranche_2`, `crpcen`, `comedie_francaise`,
`assemblees_parlementaires`. Pour chacune : dire si son texte indexe l'âge sur
la génération ou sur l'année — les deux existent —, et, s'il s'agit de la
génération, la table dans `ages_regimes.csv`. Puis la durée requise de même :
toute fiche qui lit la table commune par génération sur des années où son texte
la fixe à la date des conditions réunies se trompe pour ses retraités.

**Et la couverture.** Les générations vivantes remontent aux années 1920, et
les plus anciennes ont liquidé avant 1990 : le balayage des témoins va de 1925
à 1975 pour chaque statut, mais aucun test ne vérifie encore qu'une fiche
réponde, pour toute génération de 1920 à aujourd'hui, par une règle datée qui
vaut pour elle. C'est le test à écrire à la fin de ce chantier.

### 129. Le taux de l'État ramené à sa part « retraite seule » : un réglage, puis le défaut — `en cours`

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

**Ce qu'il déplace**, mesuré le 24 septembre 2026 sur `main` (cbe5678, la
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

### 130. L'architecture du dépôt : décidée, la phase 0 faite, la phase 1 à lancer — `en cours`

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
6. le repère git `phase-0`, sur dae2819, le dernier commit de la phase
   (§ 12). Le jeton d'une session n'écrit pas de tag (HTTP 403) : à la
   demande du propriétaire, un workflow lancé une fois l'a posé, puis a été
   supprimé.

**Ce qui reste ouvert.**

- La phase 1 (§ 11) : la documentation rangée par nature. L'état « écart
  connu » des exemples officiels (§ 9.2) et le contrôle de conservation
  (§ 12) sont faits (plus bas).
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
