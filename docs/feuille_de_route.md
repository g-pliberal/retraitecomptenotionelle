# Feuille de route — les actions qui font le plus progresser le modèle

Ce fichier est la liste des chantiers à mener, classés par ce qu'ils déplacent
dans les résultats du dépôt. Il sert de point d'entrée à une session de travail :
prendre l'action la plus haute qui n'est pas commencée, la mener au bout, puis
mettre à jour ce fichier. Il ne remplace ni `limites.md`, qui dit ce que vaut
chaque chiffre, ni `regimes.md`, journal de la campagne sur les régimes.

**Comment le tenir.** Une action a un état — `à faire`, `en cours`, `fait` — et
une ligne « ce que ça a déplacé » quand elle est faite, comme les tranches de
`regimes.md`. Une action qu'on abandonne ne disparaît pas : elle passe en bas,
avec la raison. Une découverte faite en chemin qui mérite un chantier se note
ici, pas dans un commentaire de code.

**Le constat de septembre 2026, qui fonde ce classement.** La couverture des
régimes est finie : 89 lignes d'inventaire, plus aucune ligne « à modéliser »,
37 fiches partielles dont chaque mur est documenté dans `regimes.md` et
`limites.md` §4. Continuer sur cet axe rapporte peu : les manques restants
portent sur des populations minuscules ou des barèmes que personne ne publie.
Les gains sont sur ce qui porte les résultats de tête du README : les agrégats
de la page Coût, la part patronale, les taux de cotisation qui sont la matière
même des scénarios notionnels, et l'étalon qu'est le scénario 1.

Un coût transversal pèse sur l'ordre : chaque changement du MODÈLE se paie deux
fois, dans `src/retraite_notionnelle/scenarios/actuel.py` (plus de trois mille
lignes) et dans le portage `moteur/js/` (douze mille lignes), puis dans les
témoins. Les actions 1 à 3 et 6 ne touchent que les données et la page Coût ;
les actions 7, 9, 10 et 11 touchent les deux moteurs, comme l'a fait l'action 5,
et l'action 4 ne les a touchés qu'en surface — deux lignes de chaque côté.
L'action 13 ne touche pas le modèle du tout : un script de certification, le
format de son journal, et une phrase de la page Données en deux exemplaires.

---

## Premier rang — ce qui déplace les résultats de tête

### 1. Pondérer les cas types par les effectifs réels, et donner une distribution au scénario 6 — `fait`

**Pourquoi.** Tous les agrégats de la page Coût — le « quinze mille milliards »
du README, le rapport de −77 % du scénario 2, la trajectoire à 2070 — reposent
sur les douze cas types de `castypes.py` à poids égal. `limites.md` §5 bis le
qualifie de plancher, biaisé vers les départs précoces (SNCF, catégorie
active), et dit qu'« aucune source ne fixerait » une pondération. C'est faux
pour les effectifs : ils existent par régime. Même trou pour la garantie
vieillesse du scénario 6 : la page ne la voit que par le seul cas type qui
liquide à 65 ans ou après, et c'est la proposition politique du dépôt.

**Sources à lire.** DREES, *Les retraités et les retraites* (édition annuelle,
effectifs de retraités et de cotisants par régime, 1990-) ; Commission des
comptes de la Sécurité sociale, rapports annuels (effectifs par régime) ;
DREES, distribution des pensions par montant (déciles, par sexe, EIR) pour
compter qui passe sous 800 € et 1 050 €.

**Fichiers.** `src/retraite_notionnelle/cout.py` (`_masses`, `_rapports`) ;
`data/reference/macro/` (nouvelle série d'effectifs par régime, avec
`source_id` dans `data/sources.yaml`) ; page Coût dans `web/pages.py` et
`moteur/js/pages.js` ; `limites.md` §5 bis et §« Le scénario 6 ».

**Marche.** Associer chaque cas type à un ou plusieurs régimes, lui donner le
poids de leurs effectifs de l'année, garder la pondération égale comme
variante pour mesurer ce que l'ancienne convention valait. Pour la garantie,
appliquer le barème (800 €, plus 250 € d'isolement) à la distribution DREES
plutôt qu'aux cas types, et afficher les deux chiffres.

**Fin.** Le README et `limites.md` donnent l'ancien et le nouveau rapport, et
la page Coût dit lequel elle affiche.

**Ce que ça a déplacé.** Deux sources nouvelles, toutes deux certifiées et
récupérées automatiquement chez leur producteur : l'enquête annuelle auprès des
caisses de retraite (`data/reference/regimes/effectifs_retraites.csv`, 28 caisses
de 2004 à 2024) et la distribution des pensions de l'échantillon interrégimes
(`data/reference/macro/distribution_pensions.csv`, 46 tranches de cent euros,
fin 2020).

- *La pondération.* Chaque cas type porte l'effectif des retraités de sa caisse,
  lu année par année ; la Cnav se partage entre les quatre carrières du privé.
  L'agent de conduite pèse 0,7 % et non 8,3 %, le privé 64 % et non 33 %. Le
  cumul 1959-2024 du scénario 2 passe de −75,9 % à **−79,5 %**, celui du
  scénario 4 de −55,9 % à **−51,9 %**, celui du 6 de −55,2 % à **−51,7 %**.
  L'ancienne convention reste calculable (`ponderation="egale"`) et un test
  vérifie qu'elle reproduit exactement l'ancien résultat.
- *Le sens du biais annoncé était faux à moitié.* `limites.md` disait le rapport
  « plutôt un plancher » ; c'est vrai des scénarios qui portent la part
  patronale, et faux du scénario 2, pour lequel c'était un plafond.
- *La garantie vieillesse.* Les 93 milliards sur soixante-six ans qu'en tiraient
  les cas types — 33 avec la pondération nouvelle — étaient un chiffre faux : un
  seul des douze liquide à 65 ans ou après. Le barème appliqué à la distribution
  réelle coûte **18,4 milliards par an** aux pensions d'aujourd'hui (22,8 % des
  retraités), 32,2 au plancher majoré, et 33 à 59 aux pensions du scénario 6. La
  page Coût porte les quatre chiffres et dit ce que chacun suppose.
- *Ce que ça a cassé, et qui n'est pas une régression.* La trajectoire projetée
  du système actuel passe de 16,5 % à **18,4 % du PIB en 2070**, contre 14,2 %
  au COR : l'écart avec le seul contrôle externe de la page double. La
  pondération a retiré une compensation accidentelle — voir l'action 8, ouverte
  pour cette raison. La borne du test de vraisemblance a été portée de 18 à
  20 %, et son texte dit que c'est un aveu.

### 2. La part patronale du public, lue dans les comptes des régimes — `fait`

**Pourquoi.** Le résultat « la part patronale pèse plus lourd que la part
salariale » (README §3) repose sur une estimation pour l'État avant 1995 et
pour douze régimes spéciaux en entier, où le taux d'un salarié du privé tient
lieu (`limites.md`, « La part patronale du public »). Ces douze régimes sont
précisément ceux des départs précoces au cœur de la comparaison.

**Sources à lire.** Rapports de la Commission des comptes de la Sécurité
sociale (cotisations employeur et subvention d'équilibre, régime par régime,
depuis les années 1990) ; COR, séries de taux de cotisation implicites ou
apparents des régimes spéciaux ; programmes 195 et 198 des lois de finances
(SNCF, RATP, mines, marins, SEITA) ; jaune « pensions » pour l'État.

**Fichiers.** `data/reference/legislation/contribution_employeur_public.csv`
(déjà porteur de l'État 1995-2026, de la CNRACL et de la SNCF 2007-2018) ;
un récupérateur dans `scripts/fetch/` par source recontrôlable ; `docs/methodologie.md`
§« La contribution employeur du public » ; le tableau de `limites.md`.

**Marche.** Régime par régime, par poids décroissant : SNCF hors 2007-2018, RATP,
IEG, mines, puis l'État 1980-1994 par le rapport charge de pensions sur masse
des traitements. Une valeur transcrite d'un rapport plafonne à `haute` ; un
taux calculé depuis un compte est marqué comme tel.

**Fin.** Le tableau de `limites.md` n'a plus de ligne « rien / tout » pour les
quatre grands régimes spéciaux, et le nombre d'années estimées affiché sous la
simulation d'un agent SNCF ou RATP a chuté.

**Ce que ça a déplacé.** Une source nouvelle,
`scripts/fetch/dila_legi_contribution_employeur.py`, et **163 valeurs
certifiées** là où la part patronale était celle d'un salarié du privé : la
RATP de 2007 à 2025, les IEG de 2005 à 2020, la SNCF de 1992 à 2006, les mines
de 1984 à 2026, l'Opéra de Paris et la Comédie-Française de 1992 à 2026. Le
fichier passe de trois régimes à neuf, et la ligne « rien / tout » du tableau
de `limites.md` de douze régimes à sept.

- *Les sources n'étaient pas celles que l'action annonçait.* Elle envoyait vers
  les rapports de la CCSS, les programmes 195 et 198 et le jaune « pensions ».
  Rien de tout cela n'a servi : les six taux sont au **Journal officiel**, sous
  deux formes que le dépôt savait déjà lire. L'arrêté annuel, pour la RATP et
  les IEG — adossés au régime général en 2005-2006, ils versent ce que les
  mêmes salariés coûteraient à la CNAV et à l'Agirc-Arrco, exactement la
  composante T1 de la SNCF. La version datée d'un article, pour les quatre
  autres, exactement la CNRACL. Ce qui manquait n'était pas une technique,
  c'était de chercher ailleurs que là où elle avait déjà servi.
- *Et l'index a remplacé le dump.* Les récupérateurs `dila_legi_*` plus anciens
  téléchargent 1,1 à 2,8 Go et mettent d'un quart d'heure à une heure ; celui-ci
  lit l'index publié, en quelques secondes, et il y trouve **plus** : le dump
  global n'a pas été régénéré depuis juillet 2025, et l'arrêté RATP du 13 mars
  2026 qui porte l'année 2025 n'est que dans les incréments.
- *Le repli n'était ni un plancher ni un plafond.* Là où la série manquait, le
  modèle prêtait au régime l'effort d'un salarié du privé. Les taux lus sont
  tantôt bien plus hauts, tantôt bien plus bas : un agent des IEG voit la part
  patronale de sa carrière passer de 224 000 à 316 000 €, un mineur la voit
  tomber de 247 000 à 177 000 €. Trente cas de témoin sur 427 bougent, et ce
  sont exactement les six régimes.
- *Sur la page Coût, l'effet est petit*, et c'est attendu : deux cas types sur
  douze sont concernés, et de faible poids. Le cumul du scénario 4 passe de
  −51,9 % à **−51,8 %**, celui du 6 de −51,7 % à **−51,6 %**.
- *Ce qui reste, et pourquoi.* Les IEG s'arrêtent en 2020 et la SNCF en 2018
  pour la même raison : le texte cesse de chiffrer et renvoie à une formule que
  la caisse applique sans la publier. L'État d'avant 1995 n'a pas été cherché —
  l'action proposait de le reconstituer par le rapport charge de pensions sur
  masse des traitements, ce que le dépôt refuse de faire depuis qu'il a écrit
  pourquoi le taux implicite ne se certifiera pas. Sept régimes restent sans
  série : FSPOEIE, marins, CRPCEN, Banque de France, port de Strasbourg, SEITA,
  chemins de fer secondaires. Pour le dernier, la lecture est faite et
  inutilisable — l'article 12 du décret de 1991 donne 14,60 % à la charge des
  exploitants, mais la fiche du régime s'arrête en 1954.
- *Une convention à garder en tête.* Ces taux sont ceux de l'**employeur**, non
  ceux de l'équilibre : les droits spécifiques que l'État finance pour la RATP,
  les 22 % des salaires qu'il verse aux mines, la subvention de l'Opéra n'y sont
  pas. C'est la convention de la SNCF, dont T1 + T2 laisse dehors la subvention
  d'équilibre — mais pas celle de l'État, dont le taux EST un taux d'équilibre.
  Un mineur et un fonctionnaire d'État ne sont donc pas mesurés à la même aune,
  et la différence joue contre le mineur. C'est écrit dans `limites.md` ; ce
  serait un chantier à part que de l'égaliser.

### 3. Certifier les taux de cotisation, matière des scénarios 2 à 6 — `fait`

**Pourquoi.** Le compte notionnel ne connaît que la cotisation. Or les taux du
régime général ne sont qu'au niveau `moyenne` depuis 1967 (OpenFisca), `estimee`
avant ; ceux de l'Agirc, de l'Arrco et des complémentaires sont `moyenne` ;
ceux des autres régimes `moyenne` ou `estimee`. C'est la série la moins tenue
du dépôt au regard de ce qu'elle porte. L'index DILA rend la lecture des décrets
annuels bon marché : le plafond a été lu ainsi sur trente et une années.

**Sources à lire.** JORF, décrets fixant les taux de cotisation d'assurance
vieillesse du régime général depuis 1967 (`dila_cherche.py jorf`) ; fédération
Agirc-Arrco, historique des taux contractuels et d'appel, publié comme les
valeurs de point déjà lues chez elle par `scripts/fetch/agirc_arrco_valeurs_point.py` ;
avant 1967, le COR et les rapports de la CCSS, faute de JORF avant 1947.

**Fichiers.** `data/reference/regimes/taux_cotisation_annuels.csv` ;
`scripts/fetch/openfisca_cotisations.py` (le recoupement actuel, à garder) ; un
récupérateur JORF et un Agirc-Arrco nouveaux ; `scripts/verifier_donnees.py`.

**Marche.** Régime général d'abord (le plus d'assurés), puis Agirc-Arrco, puis
les alignés. À chaque année lue dans le décret, le niveau monte à `certifiee` ;
là où le décret manque ou ne chiffre pas, l'année reste à la transcription et
`limites.md` le dit.

**Fin.** La ligne « Taux de cotisation, régime général » du tableau de
certification est `certifiee` sur 1967-2026, et les témoins montrent ce que la
lecture a déplacé.

**Ce que ça a déplacé.** Une source nouvelle,
`scripts/fetch/dila_legi_taux_cotisation.py`, et **368 valeurs certifiées** là
où il n'y avait qu'une transcription : le régime général de 1982 à 2026, les
salariés agricoles de 1980 à 2026, quatre mesures chacune — taux plafonné, part
salariale, taux déplafonné, sa part. **112 de ces valeurs corrigeaient la
transcription.** Le taux n'est pas une statistique mais un article de code :
article 2 du décret n° 81-1013 puis `D. 242-4` du code de la sécurité sociale,
article 2 du décret n° 50-444 puis `D. 741-35` du code rural.

- *La règle du dépôt n'était pas appliquée.* Le taux d'une année est celui du
  1er JANVIER — `methodologie.md` l'écrit, et le récupérateur d'OpenFisca le
  disait dans sa propre docstring. Son filtre comparait pourtant les ANNÉES et
  non les dates : c'était le taux du **31 décembre** qui sortait. Six années du
  régime général en portaient la marque, dont **1991**, qui recevait la réforme
  du 1er février quand au 1er janvier le régime prélevait encore 15,8 % sous le
  seul plafond. Les fiches de la fonction publique s'étaient alignées sur ce
  filtre, en écrivant que « le millésime porte le taux en vigueur en fin
  d'année, comme les autres séries de taux du dépôt » — faux du dépôt, vrai du
  seul filtre. Les deux sont corrigés ensemble.
- *L'article codifié ne dit pas tout.* Au 1er janvier 1988, `D. 242-4` portait
  6,40 % de part salariale et le *Journal officiel* 6,60 % : le décret
  n° 87-453 du 29 juin 1987 avait relevé le taux « à titre exceptionnel et
  temporaire » **sans réécrire l'article**. D'où un garde-fou qui n'existait pas
  pour la part patronale : tout décret du JORF qui annonce des taux de ces
  régimes doit être expliqué — par une version de la chaîne, par une surcharge
  déclarée et relue, ou par une ligne qui dit pourquoi il ne touche pas à ce
  taux. Un décret qui n'entre dans aucune case arrête la certification.
- *Les salariés agricoles n'avaient pas les taux du régime général.* Le dépôt
  leur donnait sa série et écrivait que « L. 741-9 renvoie aux taux du régime
  général ». C'est vrai depuis 2014, où le II de `D. 741-35` renvoie à
  `D. 242-4` ; c'est faux avant. De 1980 à 2013, **l'employeur agricole payait
  un point de moins** que celui du privé. Un salarié agricole né en 1945 voit
  la part patronale de sa carrière tomber de 87 276 à 79 909 €, et sa pension
  du scénario 4 de **5 %** — le plus gros déplacement de cette lecture.
- *Le mur est avant 1982, et la base le démontre.* L'article 3 du décret
  n° 67-803 est dans LEGI, avec ses quatre composantes en toutes lettres — mais
  avec UNE version, du 1er octobre 1967 au 14 novembre 1981, portant 12,9 %,
  c'est-à-dire l'état de 1979 quand le taux valait 8,5 % en 1967. Le
  récupérateur le lit comme les autres et le refuse par une règle écrite : un
  article qui n'a qu'une version et couvre plus de dix ans n'a pas de
  chronologie. Les décrets modificatifs sont au JORF, mais la base n'en garde
  avant 1990 que la notice, et aucune n'écrit de taux. La ligne du tableau de
  certification est donc `certifiee` sur **1982**-2026 et non 1967-2026 : c'est
  moins que ce que l'action annonçait, et la raison est vérifiable.
- *Sur la page Coût, l'effet est petit*, et c'est attendu : le cumul du scénario
  4 passe de −51,8 % à **−51,9 %**, celui du 6 de −51,6 % à **−51,7 %**, celui
  du 2 reste à −79,5 %. 287 cas de témoin sur 427 bougent, et le scénario 1 ne
  bouge nulle part.
- *Ce qui ne se certifiera pas, et la démonstration plutôt que l'aveu.* Deux
  séries restent transcrites : le régime général d'avant 1982 et les
  complémentaires du privé. Une seconde passe leur a donné ce qu'elles peuvent
  avoir — une source nouvelle, `scripts/fetch/ipp_taux_cotisation.py`, qui lit
  les barèmes de l'IPP, source AMONT d'OpenFisca, et surtout les deux colonnes
  que la transcription perd en route : le texte de chaque marche, et sa date de
  publication au *Journal officiel*.

  * *La confrontation est une copie vérifiée, et le contrôle le dit.* IPP contre
    OpenFisca n'est pas deux lectures : c'est l'original contre sa copie. Elle a
    quand même trouvé une erreur — OpenFisca servait 0,1 % de part salariale
    déplafonnée dès le 1er janvier 2004 quand elle naît le 1er juillet, même
    cause que le filtre de l'année et au même endroit.
  * *La chronologie, elle, est vérifiée.* **Trente-cinq des trente-six marches**
    de la CNAV sont retrouvées au JORF, au numéro et à la date que l'IPP annonce
    — seul le décret n° 70-680 manque à l'index. La valeur reste transcrite, la
    DATE ne l'est plus, et c'est la date dont dépend la règle du 1er janvier.
  * *Les complémentaires ne se certifieront pas, et c'est l'IPP qui le dit.* Il
    laisse lui-même la colonne du *Journal officiel* VIDE sur ses vingt-cinq
    marches Agirc et Arrco, et cite des accords collectifs. Le JO ne publie que
    l'avis d'extension, qui renvoie au Bulletin officiel sans écrire le chiffre ;
    la fédération publie la compilation de ses valeurs de point, que le dépôt lit
    déjà, mais aucun historique de taux — sa page « Paramètres » n'affiche que
    l'année courante, ses circulaires ne remontent qu'à 2003. La démonstration
    est mécanique : si l'IPP remplit un jour cette colonne, le contrôle le dira.
  * *Et une trouvaille qui change un chiffre.* Le **décret n° 79-650 du
    30 juillet 1979** a relevé « à titre exceptionnel » les taux du régime
    général du 1er août 1979 au 31 janvier 1981 : la fenêtre couvre DEUX
    premiers janvier, et aucune source ne porte la hausse. **1980 et 1981 sont
    donc fausses**, et non seulement incertaines ; le tableau de certification
    l'écrit. C'est de là que vient une règle du garde-fou : il n'exige pas le
    mot « vieillesse », parce que ce décret ne nomme aucun risque.
- *Le bloc d'exemple du README ne dérivera plus.* Le §3 collait une sortie de
  `comparaison.tableau()` périmée — 1,7 % d'écart sur la pension du scénario 1,
  et +7,0 % au lieu de +9,0 % au scénario 4 — depuis une modification
  antérieure à cette action. Il est régénéré, et un test le recalcule à chaque
  exécution.

### 4. Étendre la contre-expertise du scénario 1 — `fait`

**Pourquoi.** Le scénario 1 est le dénominateur de tous les écarts affichés.
L'oracle OpenFisca-France-Pension (`tests/test_oracle.py`) ne couvre que le
régime général, la pension civile et l'Arrco de 1999 à 2018. Rien ne contrôle
l'Agirc, l'Agirc-Arrco unifié, les régimes alignés, l'Ircantec ni la MSA.

**Sources à lire.** OpenFisca-France-Pension, pour ce qu'il expose au-delà des
trois modules déjà lus ; les cas types publiés avec leurs taux de remplacement
par le COR (rapport annuel, cas types) et la DREES (*Panorama*), qui sont une
seconde source indépendante d'OpenFisca.

**Fichiers.** `scripts/fetch/openfisca_*.py` (modèle des trois existants),
`tests/temoins/openfisca_*.json`, `tests/test_oracle.py`, `limites.md` §3.

**Marche.** Un module OpenFisca de plus à la fois, avec dix profils et le
relevé figé dans les témoins ; puis un oracle « cas types publiés » qui compare
le taux de remplacement, avec la tolérance que justifie l'écart de convention.

**Fin.** Chaque famille de régimes de plus d'un million d'assurés a une
contre-expertise, et `limites.md` §3 dit pour chacune ce qui concorde et ce qui
diverge.

**Ce que ça a déplacé.** Deux oracles nouveaux —
`scripts/fetch/openfisca_agirc.py` et `scripts/fetch/openfisca_ircantec.py`,
vingt et un profils figés dans les témoins — et un troisième qui ne demandait
aucun code de récupération. **Vingt tests de plus**, et **cinq écarts trouvés,
trois chez nous.** Le détail est dans `limites.md` §3 ; ce qui suit est ce
qu'il faut en retenir.

- *Le périmètre est atteint, et il est plus petit que l'action ne le croyait.*
  OpenFisca-France-Pension n'expose que cinq régimes : le régime général, la
  pension civile, l'Arrco, l'**Agirc** et l'**Ircantec**. Il n'a **aucun
  module** pour les régimes alignés — ni MSA, ni artisans, ni commerçants — et
  son Agirc-Arrco unifié lève toujours une exception. L'action demandait « un
  module de plus à la fois » : il n'en restait que deux, et ils sont faits.
- *Les régimes alignés n'avaient pas besoin d'un module, et c'est la loi qui le
  dit.* L. 742-3 du code rural et L. 634-2 du code de la sécurité sociale
  calculent la MSA, l'artisan et le commerçant comme le régime général : leur
  pension se confronte donc à l'oracle du régime général, sur la même carrière,
  sans qu'aucune récupération soit nécessaire. **La MSA passe** — elle rend
  exactement la pension du régime général sur les dix profils, et 1 678 770
  retraités de droit direct entrent ainsi dans le périmètre contrôlé. **L'artisan et
  le commerçant, non**, et la découverte est là : le modèle coupe leur carrière
  à chaque changement de CAISSE — CANCAVA en 2006, RSI en 2018 — et calcule
  deux salaires de référence là où la loi n'en veut qu'un. De −7,2 % à +0,3 %
  sur les dix profils. C'est l'action 10, ouverte pour cette raison.
- *L'Ircantec ne relisait personne, et deux de ses règles étaient fausses.*
  L'assiette de sa tranche B allait de un à huit plafonds depuis 1971 quand
  l'article 7 du décret n° 70-1277 la limite à **4,75 plafonds** jusqu'au
  décret de septembre 2008 ; son coefficient d'anticipation abattait 1,1 % par
  trimestre quand l'article 16 de l'arrêté du 30 décembre 1970 écrit un
  **escalier** — 1 %, 1,25 %, 1,75 % — qui est, marche pour marche, celui de
  l'Agirc-Arrco. Les deux se lisent dans l'index LEGI en quelques secondes ;
  personne ne les avait cherchées, parce que rien ne les contredisait.
- *Et ces deux corrections ne déplacent aucun témoin.* Aucun des 427 cas ne
  porte un contractuel payé plus de 4,75 plafonds, ni une liquidation Ircantec
  avec décote. Une correction qui ne déplace rien n'est pas une correction
  inutile : c'est le droit que le simulateur servira à qui saisira l'une de ces
  situations. Le mesurer et le dire vaut mieux que de le supposer.
- *Une troisième correction est sortie de là, et celle-là déplace douze
  témoins.* Le barème d'anticipation de l'Agirc-Arrco ne s'applique « à l'âge
  seul » que jusqu'à l'ASF de 1983 ; le moteur lit cette règle dans la période
  du régime à l'année de liquidation, ce qui est juste tant que le régime est
  ouvert et faux dès qu'il est FERMÉ — la dernière période de l'UNIRS est celle
  de 1957-1961, et aucune de ses pensions n'a été liquidée avant 1983. Un
  salarié du privé au taux plein se voyait abattre sa ligne UNIRS de 4 à 22 %.
  Trois fiches fermées corrigées, douze témoins qui remontent de +0,02 % à
  +0,16 % sur la pension totale.
- *Chez lui, deux transcriptions et une case vide.* L'écart le plus instructif
  n'est pas un chiffre faux mais un `null` : son barème EMPLOYEUR de la tranche
  C de l'Agirc écrit `0` avant 1991, son barème SALARIÉ écrit `null`, et
  OpenFisca lit le premier comme un taux nul et le second comme une tranche
  ABSENTE — si bien que le taux de la tranche B s'étend jusqu'à huit plafonds
  et qu'un cadre de 1983 cotise sur une assiette que l'Agirc n'ouvrira que huit
  ans plus tard. Une donnée manquante n'est pas une donnée nulle, et le dépôt
  écrit ses zéros.
- *Ce que l'oracle ne corrige pas, et qu'il a rendu visible.* L'Ircantec ne
  sert aucune SURCOTE quand l'arrêté lui en donne une depuis 2010 — 0,75 % par
  trimestre au-delà de soixante-cinq ans. OpenFisca, lui, en sert dix fois
  trop : son paramètre porte 0,075 au lieu de 0,0075, et deux ans de surcote y
  valent +60 % de pension. Les deux lectures sont figées dans un test, et la
  correction est l'action 9.
- *Un piège de mécanique, à connaître avant d'écrire le sixième oracle.* Le
  réglage `max_spiral_loops` d'OpenFisca a une borne HAUTE autant qu'une borne
  basse : trop peu de reprises tronque la carrière en silence, trop en fait
  remonter le déroulage récursif jusqu'à des années où ses propres paramètres
  n'existent pas — 1947 à l'Agirc, 1910 à l'Ircantec. Les deux récupérateurs
  calculent ce nombre et vérifient qu'il couvre la carrière.
- *Ce qui reste sans contre-expertise, et pourquoi.* Le critère de l'action
  était « chaque famille de plus d'un million d'assurés ». Il est tenu sauf
  pour UNE : les exploitants agricoles, 1 023 064 retraités de droit direct en
  2024. OpenFisca n'en a pas de module, et ils ne sont pas alignés — leur
  régime est MIXTE, une retraite forfaitaire plus une proportionnelle en
  points, sans équivalent au régime général. Rien ne les contrôle, et rien ne
  peut les contrôler par cette voie. En dessous du million, il ne reste que les
  libéraux et les régimes spéciaux, que personne d'autre ne modélise non plus.
- *Ce que l'action annonçait et qui n'est pas fait : l'oracle « cas types
  publiés ».* Le COR et la DREES publient des taux de remplacement par cas
  type, et c'eût été une seconde source INDÉPENDANTE d'OpenFisca. Elle ne l'est
  qu'en apparence : leurs cas types sont définis par une carrière type que le
  dépôt ne sait pas reconstituer — salaire à un ou deux SMIC « en moyenne de
  carrière », avec des hypothèses de progression que les rapports décrivent en
  prose —, si bien que l'écart mesuré serait celui des carrières et non celui
  des modèles. Le faire suppose d'abord le chantier de la carrière saisie
  (action 7). La ligne reste à prendre ; elle n'est pas dans cette action.

---

## Second rang — réel, mais plus cher ou plus étroit

### 5. Catégorie active et militaires — `fait`

**Pourquoi.** Policiers, hospitaliers, militaires : des populations larges, et
précisément les départs précoces au cœur de la thèse. Le drapeau
`categorie_active` existe dans `config.py` mais aucun statut ne le porte, et le
cas type `fonctionnaire_actif` est calculé comme un sédentaire (`limites.md`,
« Ce qui reste hors du modèle »). L'inventaire porte le statut `militaire`
comme manque de `fonction_publique_etat`.

**Marche.** Un indicateur de catégorie active sur les statuts de la fonction
publique dans `affiliations.yaml` : âge d'ouverture de 57 ans (52 pour la
super-active), âge d'annulation propre, condition de durée de services actifs
à lire dans le code des pensions. Puis un statut `militaire` : pension après
quinze ou dix-sept ans, limite d'âge de grade. Touche les deux moteurs et les
témoins.

**Ce que ça a déplacé.** Sept statuts de plus — cinq classés (catégorie active
et super-active de l'État et de la CNRACL, ouvriers de l'État), deux militaires
—, trois tables de législation lues dans les textes par l'index LEGI, un cas
type de plus, et quatorze tests. Aucun des 427 cas de témoin existants ne
bouge : le changement est strictement additif pour les statuts de droit commun,
et c'est ce qui dit qu'il n'a rien cassé chez le sédentaire.

- *Le classement ne se devine pas, il se déclare — et c'était le nœud.* Un
  aide-soignant et un rédacteur territorial cotisent à la même CNRACL, dans la
  même fiche, au même taux, et l'un liquide cinq ans avant l'autre. Aucune
  donnée de carrière ne les distingue. Le classement est donc porté par le
  STATUT, comme `sans_employeur` l'est depuis les non-salariés : c'est
  l'assuré qui choisit « catégorie active », et le modèle vérifie ensuite sur
  la carrière la condition de durée que l'article L. 24 exige — dix-sept ans de
  services actifs, vingt-sept de services super-actifs. Dix ans d'emploi classé
  en fin de carrière ne l'ouvrent pas.
- *L'âge d'ouverture n'était que la moitié du sujet ; l'âge d'ANNULATION était
  l'autre.* `limites.md` disait que l'écart de pension restait nul, la décote
  étant plafonnée à vingt trimestres dans les deux cas. C'est vrai au seul âge
  anticipé, et faux partout ailleurs : l'article L. 14 retranche ses trimestres
  de la LIMITE D'ÂGE du grade — soixante-deux ans en catégorie active, non
  soixante-sept —, si bien qu'un agent classé né en 1965 parti à soixante ans
  touche **20 % de plus** que le sédentaire de même carrière, 13 % à
  cinquante-neuf ans, 18 % à soixante et un. Le cas type
  `fonctionnaire_actif`, qui liquide à cinquante-sept, gagne 7,4 % à la
  génération 1950 et 5 % à 1960 ; aux générations récentes sa pension ne bouge
  pas, mais son départ cesse d'être déclaré **non ouvert**, ce qu'il était
  depuis toujours.
- *La pension militaire ne s'ouvre pas à un âge, et le modèle n'avait pas
  d'autre horloge.* Le II de l'article L. 24 la liquide à la DURÉE :
  dix-sept ans de services effectifs pour un non-officier, vingt-sept pour un
  officier. Un engagé à dix-huit ans liquide à trente-cinq — le départ le plus
  précoce du système, plus précoce que l'Opéra. Le relèvement de quinze à
  dix-sept ans est en outre indexé sur l'ANNÉE où l'ancienne durée est atteinte
  (décret n° 2011-2103, article 4), et non sur la génération : c'est la seule
  table du dépôt à porter cette clé-là, et elle vaut un an et demi d'écart
  entre deux militaires nés à trois ans d'intervalle.
- *Deux règles suivent le militaire, et sans elles le résultat aurait été
  absurde.* Il n'a pas de surcote — le III de l'article L. 14 ne la donne qu'au
  « fonctionnaire civil » —, sans quoi son âge d'ouverture à trente-cinq ans
  aurait fait surcoter vingt années de carrière. Et sa décote est celle du II
  du même article, qui ne compte pas des âges mais des services manquants pour
  atteindre la durée d'ouverture majorée de dix trimestres, dans la limite de
  dix : un sous-officier parti à quarante ans perd 12,5 % au plus, non les 25 %
  du barème des civils. Symétriquement, la surcote d'un fonctionnaire CLASSÉ se
  compte depuis l'âge légal de droit commun et non depuis son âge anticipé (D
  du XXIV de l'article 10 de la loi de 2023) — la compter depuis cinquante-sept
  ans aurait payé deux fois l'avantage du classement.
- *La page Coût bouge, et c'est le cas type militaire qui la bouge.* Les
  376 810 retraités de `fonction_publique_etat_militaire` n'étaient réclamés
  par aucun cas type : ils entrent, avec 1,6 % du poids. Le cumul 1959-2024 du
  scénario 2 passe de −79,5 % à **−79,8 %**, celui du 4 de −51,9 % à
  **−52,6 %**, celui du 6 de −51,7 % à **−52,4 %** ; à l'horizon 2070 le
  système actuel passe de 18,4 % à **18,3 %** du PIB. Le militaire est le cas
  type que le compte notionnel déplace le plus — jusqu'à −94 % au scénario 2 —,
  ce qui est la thèse du dépôt vue à l'état pur : quarante ans de rente pour
  vingt-cinq ans de cotisations.

**Ce qui reste dehors, et pourquoi.** La LIMITE D'ÂGE DE GRADE, qui ouvre la
pension militaire quelle que soit la durée accomplie et qui sert d'âge
d'annulation de décote au militaire liquidant à cinquante-deux ans ou plus
(L. 14 bis, 4°) : elle suppose de connaître le grade, que la saisie ne demande
pas. Les durées super-actives atypiques — dix-sept ans pour les ingénieurs du
contrôle de la navigation aérienne, trente-deux pour les égoutiers et les
identificateurs de l'institut médico-légal — pour la même raison : la table
porte les vingt-sept ans de la police et de l'administration pénitentiaire, la
population la plus nombreuse. Et les bonifications de SERVICE — dépaysement,
campagne, cinquième du sapeur-pompier —, qui étaient hors champ avant cette
action et le restent. `limites.md` porte les trois.

### 6. Le solde, et non le coût — `fait`

**Pourquoi.** La page Coût dit ce qui est versé, jamais ce qui est encaissé
(`cout.py`, réserve 4). Un système notionnel réel se définit par son
équilibre ; sans recettes, ni coefficient d'équilibre ni rendement implicite ne
sont calculables, et `limites.md` §5 le signale comme hors champ.

**Sources.** DREES, Comptes de la protection sociale, ressources par risque
(même source que `depenses_retraite.csv`) ; CCSS pour le régime général.

**Marche.** Une série de recettes à côté de `data/reference/macro/depenses_retraite.csv`,
le solde observé, puis le coefficient d'équilibre qu'exigerait chaque scénario
année par année. Ne touche pas les moteurs de pension.

**Ce que ça a déplacé.** Une source de plus — les classeurs de données du
rapport annuel du COR —, 270 valeurs versées au niveau `haute` ou `projetee`,
deux fichiers de référence, un module de chargement de chaque côté du portage,
une section entière de la page Coût, et vingt-cinq tests. Aucun chiffre existant
ne bouge : pas une pension, pas un coût, pas un témoin. C'est un ajout pur, et
c'était la condition pour que ce qui précède reste comparable.

- *La source que l'action annonçait n'existe pas, et c'est le premier
  résultat.* « DREES, Comptes de la protection sociale, ressources par risque » :
  il n'y a pas de ressources par risque. Le jeu 305 ne porte que des postes `E`,
  c'est-à-dire des prestations ; son classeur annexe donne bien les ressources,
  mais de la protection sociale TOUT ENTIÈRE, maladie et famille comprises. Ce
  n'est pas un oubli du producteur : une « recette du risque vieillesse » n'a
  pas de définition comptable, les cotisations d'un régime polyvalent n'étant
  affectées à aucun risque. La leçon vaut au-delà de cette action — une source
  inscrite dans une feuille de route n'a pas été vérifiée du seul fait qu'elle a
  été nommée.
- *Ce qui existe est un autre compte, et il fallait en prendre les DEUX
  colonnes.* Le COR consolide chaque année, depuis les rapports à la CCSS,
  dépenses et ressources du système de retraite sur un même périmètre — régimes
  légalement obligatoires, FSV compris, RAFP exclu. Prendre ses ressources et
  les retrancher de la dépense DREES aurait fabriqué un solde en soustrayant
  deux périmètres ; on prend donc sa dépense aussi, et le solde du scénario 1
  redonne alors EXACTEMENT le solde publié — 5,1 milliards de besoin de
  financement en 2025, au dixième près. Les deux périmètres se recoupent à
  0,28 point de PIB en 2024 (0,61 en 2002) : c'est un contrôle externe, pas une
  identité, et seul le RAPPORT des masses, sans dimension, passe de l'un à
  l'autre.
- *Le coefficient d'équilibre renverse la lecture des scénarios prospectifs.*
  Il vaut 0,99 pour le système actuel en 2025 — il faudrait rogner de 1,2 % —
  et 0,84 en 2070. Il vaut 1,91 pour le scénario 3 en 2070. Lire ces 1,91 comme
  une économie de 48 % est un contresens : un système notionnel réel APPLIQUE
  son coefficient, il ne laisse pas dormir un excédent. À prélèvement inchangé,
  le scénario 3 servirait donc autant que le système actuel, autrement réparti
  entre les carrières — ce qui est exactement ce que le reste du site mesure, et
  ce que la page ne disait pas. Le modèle calcule ce facteur ; il ne l'applique
  toujours pas, et c'est désormais le seul cran qui manque.
- *Le système actuel ne repasse jamais à l'équilibre sur la fenêtre du COR* —
  solde moyen de −1,13 % du PIB de 2026 à 2070 —, là où les deux réformes
  applicables y repassent, d'autant plus tard que la part patronale entre au
  compte. L'année du croisement, elle, ne vaut pas mieux que « quelques années
  près » : le déficit actuel fait 0,17 point de PIB, c'est-à-dire l'ordre de
  grandeur de l'écart que le pas de la grille des générations introduit à lui
  seul autour de la bascule. Le dire était plus utile que de l'arrondir.
- *Un quart des ressources n'est pas cotisé, et cette part grandit.* 77,3 % des
  ressources de 2025 sont des cotisations — en comptant la contribution
  d'équilibre de l'État à ses fonctionnaires, que le modèle porte déjà au compte
  des scénarios 4 et 5 —, contre 79,6 % en 2004. Les impôts et taxes affectés
  passent de 7,1 % à 15,3 % : l'État a exonéré des cotisations patronales, puis
  remboursé par l'impôt. Un compte notionnel ne sait créditer que la part
  cotisée ; c'est ce qui borne la lecture du coefficient, et il fallait le
  chiffrer pour pouvoir le dire.

**Ce qui reste dehors, et pourquoi.** L'APPLICATION du coefficient, qui est le
chantier suivant et qui touche, lui, les deux moteurs. Les RÉSERVES financières
des régimes, que le COR chiffre à part : le solde dit le flux, jamais le stock.
Et la RÉACTION des recettes aux scénarios — le 6, qui pose un taux unique de
18 %, déplacerait aussi les ressources, et le coefficient suppose celles du
système actuel. `limites.md` §5 porte les trois.

- **Septembre 2026, seconde passe : la recette suit le droit.** Le poste
  « transferts d'organismes extérieurs » est désormais ventilé par celui qui
  paie, lu dans les rapports à la Commission des comptes de la Sécurité
  sociale — fiche de la CNAF pour l'AVPF et les majorations pour enfants,
  fiches de l'Agirc-Arrco et de l'Ircantec pour les points des chômeurs que
  l'Unédic paie — par `scripts/fetch/ccss_transferts_retraite.py`, dans
  `transferts_retraite.csv`, au niveau `haute`, de 2011 à 2025. Le COR ventile
  le même poste pour la dernière année de chaque rapport depuis 2023 : son
  « dont Unédic » est EXACTEMENT la somme des deux lignes de la CCSS, son
  « dont CNAF » s'en écarte de quelques pour cent dans un sens ou dans
  l'autre, et le vérificateur confronte les deux. Ce que cela dit : les
  scénarios notionnels suppriment l'AVPF et les majorations, et ne portent
  rien au compte pendant une année de chômage, mais comptaient jusqu'ici la
  recette qui finance ces droits — 10,9 milliards de la branche famille et
  3,9 de l'assurance chômage en 2024, 3,7 % des ressources. Retirée à part
  constante, elle ramène le coefficient du scénario 3 en 2070 de 1,94 à 1,87.
  La page Coût le dit dans un dépliant ; le coefficient lui-même n'est pas
  corrigé, ce qui est le pas suivant de l'action 11. Deux choses que le
  chantier a coûtées au passage : le lecteur PDF du dépôt ne séparait pas les
  cellules d'un tableau posées chacune par leur propre `Tm` — « 4 929 5 002 »
  se lisait « 49295002 » — et tombait sur une table de correspondance hors du
  plan Unicode ; il lit désormais les rapports à la CCSS de 2013 à 2026, et
  toujours pas ceux d'avant, chiffrés ou compressés en flux d'objets.

### 7. Saisir un relevé de carrière réel sur le site — `fait`

**Pourquoi.** Le chemin le plus exact, `Carriere.depuis_lignes`, n'est
accessible qu'en Python. Le site plafonne à six métiers et des interruptions
par plage. Un relevé collé année par année permettrait à chacun de confronter
le simulateur à son estimation Info-Retraite : c'est le levier de crédibilité
le plus fort du projet.

**Marche.** Un format texte simple (année, régime, revenu, trimestres),
analysé dans `moteur/js/pages.js` et dans `web/pages.py` à l'identique, porté
dans l'adresse comme le reste des paramètres, avec des témoins. L'import
automatique reste impossible (`limites.md` §5, « Les carrières réelles »).

**Ce que ça a déplacé.** Aucun chiffre : les **469 témoins de simulation** sont
inchangés au bit près, et les neuf qui s'y ajoutent sont ceux du chemin neuf.
Les 31 témoins de page bougent, mais d'une seule façon et pour une seule raison
— le champ ajouté au formulaire, et le `releve=` vide que toute adresse porte
désormais, comme elle portait déjà `interruptions=`. Ce qui change est donc ce
que le site SAIT recevoir, et rien d'autre.

- *Un champ, et un format.* `releve` est un paramètre comme les autres — il
  voyage dans l'adresse, donc un lien décrit une carrière réelle entière. Une
  ligne par année, `année:régime:revenu[:trimestres]`, séparées par des retours
  à la ligne, des virgules ou des points-virgules : c'est la convention que les
  interruptions avaient déjà posée, et non une seconde grammaire à apprendre.
  Rempli, il remplace les métiers, le profil et le niveau de revenu ; l'année de
  naissance, l'âge de départ, les enfants, la part de primes et les
  interruptions continuent de valoir, parce qu'aucun relevé ne les porte.
- *Le seul chemin où l'euro n'est converti par rien.* Le formulaire
  paramétrique saisit un revenu d'AUJOURD'HUI, que le modèle ramène à un
  multiple du salaire moyen puis promène le long de sa série ; le relevé donne
  déjà les euros de chaque année, l'unité même d'`AnneeCarriere`. C'est ce qui
  fait de ce chemin le plus exact, et c'est aussi ce qui rendait le tableau des
  arrondis de `methodologie.md` caduc sur une ligne : la conversion des francs
  se fait désormais avant le modèle, et hors de lui.
- *Une règle écrite une fois pour deux chemins.* Ce que le droit fait d'une
  année non cotisée — les trimestres qu'elle assimile, les points
  complémentaires que l'UNEDIC finance, l'AVPF que la CNAF cotise — a été
  extrait de `depuis_parcours` dans `_ligne_annuelle`, des deux côtés du
  portage. Les deux constructeurs y passent, et c'est le témoin qui l'a
  prouvé : aucune des 469 simulations figées n'a bougé d'une décimale.
- *Ce que le relevé ne dit pas, et que rien ne devine.* Le MOIS. Chaque ligne
  vaut une année civile pleine, sauf celle du départ, que la date de
  liquidation tronque — celle-là, le modèle la connaît. L'année d'entrée dans
  la vie active reste donc comptée pour une année entière alors qu'elle est
  presque toujours partielle ; `limites.md` §5 le dit, et c'est la seule
  approximation qui subsiste sur ce chemin.
- *Un refus qui coûte le découpage, et rien de plus.* Les lignes sont comptées
  AVANT d'être lues. Le calcul se fait chez le lecteur et l'adresse est la
  saisie : un relevé de cent mille lignes forgé dans un lien aurait figé
  l'onglet de celui qui le suit, exactement comme la plage d'interruption sans
  borne l'avait fait. La borne est de 63 lignes, et un test vérifie qu'elle
  reste au-dessus de ce que la fenêtre des âges permet — 61 années — pour
  qu'elle ne refuse jamais une carrière que le reste du formulaire accepte.

### 8. Faire liquider chaque cas type à l'âge de SA génération — `fait`

**Pourquoi.** Découvert en menant l'action 1, et c'est désormais le premier
défaut de la page Coût. Un cas type liquide à l'âge écrit dans `castypes.py` —
64 ans pour les carrières ordinaires — quelle que soit sa génération. Une
génération née en 1940 est donc réputée partir en 2004 à 64 ans, alors qu'elle
est partie à 60 ou 65 ans sous d'autres règles ; le stock de retraités du modèle
est trop vieux au départ de la projection, et il croît donc trop vite — la
population des 64 ans et plus gagne 41 % d'ici 2070 quand celle des 52 ans et
plus n'en gagne que 25 %. C'est la principale cause des quatre points d'écart
avec le COR en 2070 (18,4 % du PIB contre 14,2 %), et l'ancienne pondération
égalitaire le masquait en donnant un sixième du poids à des carrières qui
liquident à 52 et 57 ans.

**Sources à lire.** Rien à récupérer : le dépôt porte déjà, et certifiés, l'âge
d'ouverture des droits par génération (`legislation/age_ouverture_requis.csv`)
et l'âge d'annulation de la décote. Pour le comportement plutôt que le droit :
DREES, âge conjoncturel moyen de départ à la retraite — la feuille
`A-Age_conjoncturel` du classeur EACR déjà téléchargé par
`scripts/fetch/drees_eacr.py` le porte de 2004 à 2024.

**Fichiers.** `src/retraite_notionnelle/castypes.py` (`CasType.age_liquidation`
devient une règle et non un nombre), `moteur/js/castypes.js`, les témoins,
`docs/limites.md` §5 ter.

**Marche.** Donner au cas type un âge de liquidation RELATIF — « à l'âge
d'ouverture de sa génération », « dix ans avant » pour la catégorie active —
plutôt qu'absolu, en gardant l'âge absolu comme variante pour mesurer l'écart.
Puis regarder si la trajectoire 2070 revient vers le COR : c'est le contrôle
qui dira si le diagnostic était bon.

**Fin.** L'écart avec le COR en 2070 est mesuré avant et après, `limites.md`
§5 ter le dit, et la borne du test de vraisemblance redescend si elle le peut.

**Ce que ça a déplacé.** L'âge de liquidation d'un cas type n'est plus un
nombre mais une RÈGLE, et les treize en portent trois. Les 469 témoins de
simulation sont inchangés au bit près — la règle date un départ, elle ne touche
à aucune formule de pension —, et ce sont les agrégats de la page Coût, qui
liquident les cas types, qui bougent.

- *Le contrôle a démenti le diagnostic, et c'est le résultat.* L'action était
  fondée sur l'idée que ce défaut était « la principale cause des quatre points
  d'écart avec le COR en 2070 ». La mesure dit le contraire : la trajectoire
  2070 passe de **18,3 % à 19,3 % du PIB** quand le COR en projette 14,2. Le
  défaut était réel, son sens était faux. La raison est lisible dans la grille
  des âges : les générations d'après 1970 liquidaient DÉJÀ à peu près à l'âge
  que le droit leur ouvre — soixante-quatre ans est l'âge d'aujourd'hui, et
  c'est lui qui était écrit —, si bien que la correction a déplacé les
  générations anciennes, celles qui font 2024, et non celles qui font 2070.
  `limites.md` §5 ter porte la mesure, la raison, et la seule piste que le dépôt
  puisse mesurer chez lui : son taux de remplacement ne recule pas — 51,3 % pour
  la génération 1970, 50,9 % pour celle de 2000 — là où le COR fait reculer le
  rapport de la pension moyenne au revenu d'activité moyen.
- *Trois règles, parce que trois droits.* `taux_plein` pour les dix carrières de
  droit commun : le premier âge auquel la pension est servie ENTIÈRE, c'est-à-dire
  l'âge d'ouverture si la durée requise y est atteinte, l'âge auquel elle l'est
  sinon, et jamais au-delà de l'âge d'annulation de la décote. C'est la règle des
  cas types du COR, et l'action avait d'abord écrit `ouverture` comme la marche
  le demandait : il a fallu la mesurer pour voir qu'elle faisait partir le cadre
  à soixante-quatre ans avec huit trimestres de décote, ce que personne ne fait,
  et qu'elle éloignait le résultat d'un point de plus. `ouverture` reste, mais
  pour les trois carrières dont un STATUT commande le départ — catégorie active,
  agent de conduite, agent des IEG —, dont le cas type existe précisément pour
  montrer ce départ-là. `services` pour le militaire, dont la pension ne s'ouvre
  pas à un âge mais à une durée.
- *La fermeture d'un régime est une information, et la règle la lit.* La SNCF
  n'embauche plus au statut depuis 2020 : l'agent de conduite né en 2000 relève
  du régime général et liquide à soixante-quatre ans. L'âge écrit le faisait
  partir à cinquante-deux ans — une pension que le droit n'ouvrait à personne.
  Aucune donnée n'a été ajoutée pour cela : la fiche portait déjà la fermeture,
  et c'est l'âge écrit qui l'ignorait.
- *Un point fixe, et pourquoi il en faut un.* L'âge de référence dépend de la
  carrière, laquelle dépend de l'âge de liquidation : la question tourne en rond,
  parce que les fiches de la SNCF et des IEG indexent l'âge d'ouverture sur
  l'ANNÉE de départ et non sur la génération. On part de l'âge écrit et on
  itère, quatre passes au plus. Une descente n'est retenue que si l'âge plus
  précoce est lui-même confirmé : sans cette garde, un artisan né en 1910
  « ouvrirait » à soixante ans — le droit de 1973 — un départ que son année
  réelle, 1970, refuse encore à soixante-cinq.
- *Ce que la règle a rendu visible ailleurs.* La garantie vieillesse du
  scénario 6, servie à 65 ans, n'était vue que par un cas type sur treize ; elle
  l'est maintenant par cinq aux générations récentes, et la masse que la grille
  en tire passe de 0,5 à 9,4 milliards par an. Le chiffre reste faux — il vaut
  la moitié de ce que le barème coûte sur la vraie distribution — mais il l'est
  d'un facteur deux au lieu de quarante, et deux tests qui figeaient l'ancien
  ordre de grandeur ont été réécrits plutôt que rebornés en silence.
- *Ce qu'elle ne sait toujours pas faire.* Elle ne connaît pas la carrière
  longue : le moteur sait la calculer, mais comme une dérogation qu'on demande,
  non comme un âge qu'on propose. Et les âges d'ENTRÉE des cas types restent
  ceux de la grille — vingt-quatre ans pour l'artisan, vingt-sept pour le
  libéral —, ce qui suffit à les faire partir à soixante-sept ans une fois la
  durée requise opposée : la grille part donc un peu plus tard que la France
  réelle, et l'âge conjoncturel de départ de la DREES, que l'action citait comme
  source de comportement, permettrait de le chiffrer. Il n'est pas dans le
  dépôt, et l'y mettre est un chantier à part.

### 9. La surcote de l'Ircantec, qu'aucun assuré ne touche — `fait`

**Pourquoi.** Découvert en menant l'action 4. Le paragraphe 4 de l'article 16
de l'arrêté du 30 décembre 1970 majore le total des points « de 0,75 % par
trimestre entier écoulé entre le soixante-cinquième anniversaire de l'assuré et
la date d'entrée en jouissance », et de 0,625 % par trimestre cotisé entre
l'âge du taux plein et soixante-cinq ans, depuis le 1er janvier 2010. Le modèle
n'en sert rien : la fiche de l'Ircantec porte `surcote_par_trimestre: null`, et
`_abattement_points` ne rend jamais plus de 1. Un agent non titulaire qui
travaille jusqu'à soixante-sept ans y perd 6 % de sa complémentaire. Le
contrôle est écrit : `test_la_surcote_ircantec_est_dix_fois_trop_forte_chez_lui`
fige les deux lectures, la sienne (0,075 par trimestre, dix fois le texte) et
la nôtre (aucune).

**Sources à lire.** Rien à récupérer : l'arrêté est dans l'index LEGI
(`LEGIARTI000019511923` pour la version qui crée la surcote,
`LEGIARTI000048065521` pour l'état courant). Vérifier au passage si d'autres
régimes en points du catalogue sont dans le même cas.

**Fichiers.** `data/reference/regimes/complementaires_prive.yaml` (fiche
Ircantec), `src/retraite_notionnelle/scenarios/actuel.py`
(`_abattement_points`, qui doit pouvoir dépasser 1),
`moteur/js/scenario-actuel.js`, les témoins, `tests/test_oracle.py`.

**Marche.** Un coefficient de majoration lu à la fiche, comme l'abattement,
avec ses deux taux et ses deux bornes d'âge. Touche les deux moteurs.

**Fin.** Le test d'oracle compare la surcote servie à celle de l'arrêté plutôt
qu'à zéro, et `limites.md` §3 retire l'Ircantec de la liste des avantages
manquants.

**Ce que ça a déplacé.**

- *Le droit, à ses deux taux.* La fiche porte `surcote_points: ircantec` à
  partir de 2010, et `_abattement_points` rend un coefficient qui peut dépasser
  un. Le 1° paie 0,75 % par trimestre ENTIER écoulé entre l'âge du taux plein
  et l'entrée en jouissance ; le 2° paie 0,625 % par trimestre COTISÉ au-delà
  de la durée requise entre l'âge légal et ce même âge. Les deux assiettes sont
  disjointes par construction, ce que le texte exige : « en aucun cas une même
  période ne peut donner lieu à la fois » aux deux.
- *Le chiffre.* Sur le seul profil surcoté de l'oracle — un agent né en 1945
  parti à soixante-sept ans — le modèle servait 1,00 et sert 1,06 ; OpenFisca
  lui sert 1,30. Dans les témoins, deux cas types bougent, `contractuel_public`
  et `elu_local` de la génération 1955 : leur pension Ircantec monte de 3,75 %,
  leur pension totale de 1,1 %. Aucun autre chiffre du dépôt ne bouge, et c'est
  la mesure de ce que valait le droit manquant.
- *Une coupure de fiche, pour une date qu'aucune version de texte ne porte.*
  Le paragraphe 4 vit dans la version du 25 septembre 2008 mais ne s'applique
  qu'« à compter du 1er janvier 2010 » : la période 2009-2010 est donc coupée
  en deux, alors que `calendrier_regimes.py` ne pouvait pas la réclamer — il
  compare les DÉBUTS de version, et celui-ci est dans le corps du texte. **Une
  version de texte n'est pas une date d'effet**, et c'est un mode de panne à
  chercher ailleurs.
- *Le coefficient se nomme par ce qu'il fait.* « Coefficient d'anticipation »
  quand il retire, « coefficient de majoration » quand il ajoute : l'ancien
  libellé aurait écrit le contraire de sa valeur sous chaque pension majorée.
  Le lecteur de formule de `test_web.py`, qui refait chaque ligne affichée à la
  main, lit les deux.
- *Ce que la vérification demandée a trouvé, et qui n'est pas corrigé ici.*
  L'action demandait de regarder si d'autres régimes en points sont dans le
  même cas. Ils le sont, et pour une autre raison : la branche en points ne lit
  PAS `surcote_par_trimestre`, que seule la branche en annuités consulte. Neuf
  fiches de non-salariés portent une surcote sourcée — 0,5 à 1,25 % par
  trimestre — que le moteur laisse tomber. C'est l'action 22, ouverte plus bas.
  La RAFP, seul autre régime en points dont on pouvait attendre une majoration
  d'âge, n'en est pas : son article 8 renvoie à « un barème actuariel […] établi
  par le conseil d'administration », qu'aucun texte ne chiffre.

### 10. Liquider ensemble un régime et celui qui lui succède — `à faire`

**Pourquoi.** Découvert en menant l'action 4, et c'est le plus gros écart
qu'elle ait mesuré. Le modèle liquide chaque régime sur ses seules années, ce
qui est juste d'un polypensionné — mais la CANCAVA, le RSI et le régime général
ne sont pas trois régimes pour un artisan : ce sont trois NOMS du même droit,
et le catalogue le sait, puisqu'il porte `succede_a` et `integre_dans`. Un
artisan payé 60 000 € de 1976 à 2015 reçoit « 30 077 € × 120/165 » plus
« 36 778 € × 40/165 » là où la caisse calculerait « 34 152 € × 160/165 ».
Mesuré contre l'oracle du régime général, l'écart va de −7,2 % à +0,3 % — il
joue dans les deux sens, les vingt-cinq meilleures années de chaque morceau
pouvant être meilleures que celles de la carrière entière.

**Qui est touché.** Les artisans et les commerçants d'abord (CANCAVA/ORGANIC →
RSI en 2006 → régime général en 2018), et toute carrière qui traverse
1945 (assurances sociales → régime général). Les régimes en POINTS ne le sont
pas : leurs points se convertissent et s'additionnent déjà
(`regimes/conversions_points.csv`).

**Sources à lire.** Rien à récupérer. La règle est dans le catalogue ; ce qui
manque est son emploi par le moteur.

**Fichiers.** `src/retraite_notionnelle/scenarios/actuel.py` (la boucle par
régime, le salaire de référence et la proratisation),
`moteur/js/scenario-actuel.js`, les témoins, `tests/test_oracle.py`
(`test_les_regimes_alignes_des_independants_sont_coupes_a_la_succession`, qui
mesure l'écart aujourd'hui et devra le voir disparaître), `limites.md` §3.

**Marche.** Grouper les régimes d'ANNUITÉS par chaîne de succession avant de
liquider : un seul salaire de référence, une seule proratisation, la fiche de
la dernière période active donnant les règles. Garder le découpage actuel comme
variante, pour mesurer. Ne pas confondre avec la coordination entre régimes
alignés DISTINCTS (proratisation croisée, LURA), qui reste hors du modèle.

**Fin.** L'artisan et le commerçant rendent la pension du régime général sur
les dix profils de l'oracle, comme la MSA, et `limites.md` §3 dit ce que la
correction a déplacé.

### 11. Appliquer le coefficient d'équilibre — `à faire`

**Pourquoi.** Ouverte par l'action 6, qui s'arrête juste avant. Le coefficient
d'équilibre de chaque système est désormais CALCULÉ, année par année, de 2002 à
2070 ; il n'est pas APPLIQUÉ. Un système notionnel réel ne laisse pas dormir un
excédent : il relève les pensions jusqu'à l'équilibre, ou les abaisse, par un
facteur commun à toutes les pensions de l'année et un fonds de réserve qui
lisse. Tant que ce facteur n'est pas appliqué, les courbes de la page Coût sont
celles d'un système qui ne se pilote pas, et le coefficient de 1,91 du
scénario 3 en 2070 se lit trop facilement comme une économie de 48 %.

**Sources.** Aucune à récupérer : tout est là. Le mécanisme, en revanche, se
décrit — le coefficient suédois (`balansindex`), qui n'ajuste que le
dénominateur du ratio actif/passif, et le coefficient italien, qui indexe le
capital notionnel sur le PIB, ne font pas la même chose. Le COR décrit les deux
dans ses fiches, et elles sont désormais au manifeste sous
`cor_retour_septieme_rapport` : les documents 5 à 7 de la séance du 5 juillet
2017 — Suède, Suède (complément), Italie — avec, au document 4, la maquette du
secrétariat général qui chiffre ce que le mécanisme évite (sur un choc
démographique permanent, des déficits transitoires de l'ordre de 10 % de la
masse des cotisations contre près de 90 % en annuités et en points).
`hypotheses_projection.yaml` est déjà la trace d'un emprunt de cette nature.

**Fichiers.** `src/retraite_notionnelle/cout.py` (la trajectoire et le solde) ;
`src/retraite_notionnelle/scenarios/` si l'ajustement doit porter sur la pension
individuelle et non seulement sur l'agrégat ; `moteur/js/` en regard ; les
témoins ; `limites.md` §5.

**Marche.** D'abord retirer des ressources ce que la branche famille et
l'assurance chômage versent pour des droits que les scénarios ne servent pas —
la série est là depuis l'action 6, seconde passe, et le dépliant de la page
Coût en calcule déjà l'effet à part constante. Ensuite au seul niveau de
l'AGRÉGAT — une variante de la page Coût où chaque système est ramené à
l'équilibre —, ce qui ne touche pas les moteurs de pension et se mesure
aussitôt. Ensuite seulement, si l'écart le justifie,
l'ajustement porté à la pension individuelle, qui les touche tous les deux. Le
piège à nommer d'avance : un facteur commun ne déplace AUCUN écart entre
carrières, si bien qu'appliquer le coefficient ne change rien à ce que le site
mesure page par page — et change tout à ce que la page Coût affiche.

**Fin.** La page Coût porte les deux lectures — système piloté, système non
piloté — et dit laquelle répond à quelle question.

---

### 12. Mettre le programme du PLF sur l'accueil, et élaguer le site — `fait`

**Pourquoi.** Le site est le livrable d'un parti politique, et il s'ouvrait sur
un formulaire. Rien n'y disait ce qu'est le système actuel, ce qu'est un compte
notionnel, ni pourquoi le second vaudrait mieux que le premier ; la proposition
du PLF — le scénario 6 — n'existait qu'en note de bas de page de la Méthode.
L'autre moitié du défaut est de ton : les pages portaient l'historique du dépôt
et le récit de ses propres corrections, là où un programme doit tenir en
phrases courtes.

**Fichiers.** `src/retraite_notionnelle/web/pages.py` et `web/gabarit.py` ;
`moteur/js/pages.js` et `moteur/js/gabarit.js` en regard ; `index.html` pour le
routage ; `scripts/construire_temoins.py` ; `tests/test_web.py` et
`tests/js/` ; `README.md`.

**Marche.** Une page `/` — l'accueil — qui expose le programme, le simulateur
déplacé sous `/simuler`, et une relecture d'élagage de toutes les pages.

**Ce que ça a déplacé.**

- *L'accueil est le programme.* Six onglets au lieu de cinq, « Programme » en
  tête. La page dit le système actuel, le compte notionnel, la différence terme
  à terme, pourquoi il est plus juste et plus lisible, la justice entre
  générations, les minima sociaux et la garantie vieillesse, les six étapes de
  la transition, et renvoie à chacune des cinq autres pages. Elle ne calcule
  aucune carrière : elle lit les régimes, la dépense et le solde, et rien de ce
  qui coûte des secondes.
- *Le simulateur a changé d'adresse.* `#/simuler`, et non plus `#/`. Toute
  adresse inconnue retombe sur l'accueil, des deux côtés du portage.
- *Élagage.* Près de mille mots de prose en moins sur l'ensemble du site,
  presque tous du commentaire sur le dépôt lui-même — ce qu'une page a
  « longtemps » affiché, ce qui « a changé ici en dernier », ce qu'une hypothèse
  levée « valait ce qu'on disait qu'elle valait ». Aucun chiffre, aucune réserve
  méthodologique et aucune mention légale n'a été retirée.
- *Deux points de routage.* Le formulaire lit sa route dans son propre attribut
  `action` plutôt que dans une constante d'`index.html` — la constante aurait
  renvoyé chaque calcul sur l'accueil. Et une adresse `#/` porteuse de
  paramètres, c'est-à-dire un lien de simulation partagé avant ce changement,
  est reconnue et rendue au simulateur.

**Ce qui reste.** La page Programme ne chiffre pas ce que la transition coûte
année par année : elle renvoie à la page Coût, qui le fait pour les scénarios 3
et 5. Un tableau propre au scénario 6 sur cette page serait le prolongement
naturel, et suppose l'action 11.

---

### 13. Dater la certification série par série — `à faire`

**Pourquoi.** La page Données affirme : « le tout recontrôlé automatiquement
contre les sources, le 2026-09-15 ». Elle n'en sait rien. Cette date est un
horodatage GLOBAL, que `verifier_donnees.py` écrase avec `date.today()` à chaque
`--appliquer`, fût-il partiel :

```python
if arguments.appliquer and (journal or retires):   # UNE série suffit
```

Or le journal est conçu pour se COMPLÉTER et non se remplacer — c'est ce que
son propre commentaire revendique, et `limites.md` §6 avec lui : « on ne lance
presque jamais les dix-sept d'un coup ». Les deux dispositions se contredisent.
Recertifier une seule série dans six mois fera dire à la page que les
soixante-dix-neuf l'ont été ce jour-là.

**Ce que le fichier ne sait pas dire.** Les fiches de séries ne portent aucune
date : `ajoutees`, `colonne`, `corrigees`, `empreinte`, `identiques`, `niveau`,
`source`, `valeurs`, rien d'autre. En datant chaque série par le dernier commit
où sa fiche a CHANGÉ, on trouve 60 séries au 13 septembre, 7 au 14 et 12 au 15
— mais ce décompte ne prouve rien, et c'est tout le sujet : une série
recontrôlée sans changement réécrit une fiche identique, donc ne laisse aucune
trace. **Le journal est incapable de distinguer « recontrôlé le 15, inchangé »
de « pas regardé depuis le 13 ».** L'écart est de deux jours aujourd'hui, donc
inoffensif ; le mécanisme, lui, ne dérive que dans un sens.

**Sources.** Aucune à récupérer : le défaut est entièrement dans le dépôt.

**Fichiers.** `scripts/verifier_donnees.py` (l'écriture du journal, vers la
ligne 4716) ; `data/derive/certification.json` ;
`src/retraite_notionnelle/web/pages.py` et `moteur/js/pages.js` (la phrase, en
deux exemplaires) ; les témoins ; `tests/test_verification.py`
(`test_journal_de_certification_est_lisible`, qui n'exige aujourd'hui que la
présence du champ global) ; `limites.md` §1 et §6.

**Marche.** Écrire une date DANS chaque fiche de série, posée à chaque passage
du récupérateur que les valeurs bougent ou non — c'est la condition pour que
l'absence de diff cesse d'être une perte d'information. Puis faire dire à la
page le MINIMUM et non le maximum : « la plus ancienne vérification remontant
au … », qui est la seule affirmation que les données soutiennent. Garder
`certifie_le` comme date du dernier passage, en le nommant pour ce qu'il est.
Le piège à nommer d'avance : une date par série rend le fichier bruyant en
diff — chaque exécution le réécrit en entier — et il faudra choisir entre cette
gêne et une granularité plus grossière, par exemple la date du récupérateur et
non de la série.

**Fin.** La page Données ne promet plus que ce qu'elle peut tenir, et le test
du journal échoue si une fiche de série arrive sans date.

### 14. La mortalité différentielle par revenu, que le diviseur ignore — `à faire`

**Pourquoi.** Le diviseur du §5 de `methodologie.md` est une espérance de vie de
population générale : la même pour l'ouvrier et pour le cadre. À capital
notionnel égal, deux liquidants reçoivent donc la même pension annuelle, servie
treize ans de plus à l'un qu'à l'autre — c'est l'écart que l'INSEE mesure chez
les hommes entre les 5 % les plus aisés et les 5 % les plus modestes. La
promesse du README, « au franc le franc des cotisations réellement versées »,
est alors tenue sur le flux annuel et non sur le total perçu : à cotisation
identique, le notionnel verse plus à qui vit longtemps, et qui vit longtemps est
aussi celui qui a le plus cotisé. Le dépôt sait déjà chiffrer l'effet sur l'axe
du sexe — `--table par_sexe`, 5 à 10 % d'écart, assumé au §5 — et n'a rien sur
l'axe du revenu, qui est le plus grand des deux et le seul que personne n'ait
choisi : la table unisexe est une décision de non-discrimination, la table
commune par niveau de vie n'est qu'un défaut d'observation.

**Ce qui l'a ouverte.** Une lecture proposée de l'extérieur : Sylvain Catherine,
Max Miller et Natasha Sarin, « Social Security and Trends in Wealth Inequality »,
*Journal of Finance* 80-3, juin 2025. Ils valorisent les droits à retraite
américains en stock, et le font avec une mortalité par revenu, faute de quoi le
calcul se trompe de bénéficiaire. Le résultat n'est pas transportable — la
Social Security est progressive par sa formule, un compte notionnel ne l'est par
rien — mais la précaution l'est.

**Sources à lire.** L'INSEE publie ce qu'il faut, et récemment : « De 2012-2016 à
2020-2024, l'écart d'espérance de vie entre les personnes modestes et aisées
s'est accru », *Insee Première* n° 2085 (2025), dont l'*Insee Résultats* attaché
donne des **tables de mortalité par vingtile de niveau de vie, par sexe et par
âge détaillé** ; le document de travail 2025-24 en décrit la méthode ; le
n° 1687 (2018) est la livraison précédente. Vérifier d'abord ce qu'on cherche
vraiment : non pas l'écart à la naissance, qui est le chiffre de presse, mais
les quotients à partir de soixante ans, seuls utiles à un diviseur — et la
profondeur historique, qui ne remonte pas avant 2012 quand le modèle liquide
depuis 1941.

**Fichiers.** `data/reference/mortalite/` (série nouvelle, `source_id` dans
`data/sources.yaml`, fiche de certification) ;
`src/retraite_notionnelle/donnees/mortalite.py`, dont les lois sont clés par
`(annee, sexe)` et qu'il faut ouvrir à une troisième clé ;
`src/retraite_notionnelle/config.py` (`TableConversion`) ; `moteur/js/mortalite.js`
et `moteur/js/conversion.js` ; `src/retraite_notionnelle/castypes.py`, où
`niveau_salaire` est le rattachement tout trouvé ; les témoins ;
`methodologie.md` §5 et `limites.md` §5.

**Marche.** Ne pas chercher des tables complètes par décile et par génération :
elles n'existent pour aucune des années que le modèle traverse. Caler un
décalage sur la table existante — facteur sur la force de mortalité, ou
translation d'âge — qui reproduise l'écart d'espérance publié, comme le dépôt
calibre déjà ses grands âges, et le tenir constant hors de la fenêtre observée
en le disant. Puis en faire une variante et non le défaut : le diviseur servi
reste commun — un système qui trierait ses rentes par revenu ne serait pas
défendable —, et la variante mesure ce que ce choix transfère, en euros et en
années de rente, cas type par cas type.

**Fin.** Le dépôt répond par un chiffre, et non par un silence, à l'objection
« le notionnel fait payer les carrières courtes pour la longévité des autres ».
Un garde-fou à poser d'avance, sans quoi la mesure serait malhonnête : le défaut
n'appartient pas au notionnel. Toute rente viagère à taux commun le porte, le
système actuel le premier, et le calcul doit donc porter sur les six scénarios ;
si l'écart s'y retrouve du même ordre, c'est un résultat, et il coupe
l'objection au lieu de la nourrir.

---

### 15. Rendre les pages longues parcourables — `fait`

**Pourquoi.** Deux des six pages ne sont plus des pages mais des documents :
Coût pèse 8 516 mots, seize tableaux et treize titres ; Données, 5 851 mots et
huit tableaux. Aucune des deux ne porte de sommaire, et aucun de leurs titres ne
porte d'ancre — qui cherche la part patronale, ou la date de certification d'une
série, fait défiler jusqu'à la trouver. L'action 12 a réglé le ton des pages et
leur ordre ; elle n'a rien réglé du parcours À L'INTÉRIEUR d'une page. Le
livrable est un programme politique : il est lu par quelqu'un qui cherche une
réponse, rarement par quelqu'un qui lit de haut en bas.

**Ce qui l'a ouverte.** Une consigne de septembre 2026 : tenir la liste des
procédés à employer désormais, chaque fois qu'une page s'allonge. Elle est
ci-dessous en entier, classée par ce que chaque procédé résout. C'est un
catalogue où l'on pioche page par page, pas un programme à exécuter d'un bloc :
une page de 1 700 mots n'a besoin d'aucun d'eux.

**Les vingt-cinq procédés.**

*Se repérer dans une page longue.*

1. Sommaire / navigation interne ancrée.
2. Sommaire contextuel avec progression (la section où l'on est, marquée).
3. Navigation latérale fixe.
4. Ancres contextuelles (un lien vers une section depuis le corps du texte).
5. Liens d'évitement dans le contenu, et non plus seulement en tête de page.
6. Résumés de section.

*Doser ce qu'on donne d'abord.*

7. Résumé d'abord, détail ensuite.
8. Blocs « À retenir ».
9. Affichage « Essentiel / Tout afficher ».
10. Regroupement par niveaux de lecture.
11. Mise en avant des informations prioritaires.
12. Séparation du contenu principal et du contenu de référence.

*Trouver sans lire.*

13. Recherche locale dans la page.
14. Filtres et facettes.
15. Filtres intelligents préremplis.
16. Tri et filtrage dynamique.
17. Navigation par catégories.

*Les tableaux et les grands ensembles.*

18. Tableaux optimisés.
19. En-têtes et colonnes fixes.
20. Pagination ou chargement progressif.
21. Cartes avec contenu hiérarchisé.
22. Comparateur.

*Changer de forme sans changer de page.*

23. Onglets.
24. Vues alternatives.
25. Hiérarchie typographique forte.

**Ce que le dépôt fait déjà, et qu'il ne faut pas refaire.** Le lien d'évitement
existe, mais global et unique (`a.evitement`, posé par `gabarit.entete`, servi
par un écouteur d'`index.html`) : le procédé 5 est son extension au corps des
pages, pas sa création. Le procédé 7 a un embryon — onze `<details>` répartis sur
quatre pages. Le procédé 24 en a un aussi, et le meilleur du lot :
`gabarit.donnees_du_graphique` rend en tableau ce que le graphique montre en
courbes, ce qui est exactement la vue alternative demandée ; il est à généraliser,
non à inventer. Le procédé 25 a ses outils — `tableau`, `fiche`, `gloses` — mais
pas son usage : la page Coût n'a que trois `<h2>` pour huit mille mots, et
l'accueil, un seul pour huit `<h3>`. Les procédés 1 à 4 n'existent nulle part :
deux ancres sur toute la Méthode (`#indexation`, `#unites`), aucune ailleurs.

**L'obstacle technique, à connaître avant d'écrire une ligne.** Le site tient
dans une seule page et L'ADRESSE EST LA ROUTE : `#/cout` désigne la page Coût.
La place de l'ancre est donc prise, et un `href="#une-section"` ne défilerait pas
vers la section — il renverrait le lecteur à l'accueil, en perdant au passage la
simulation en cours (c'est écrit dans la docstring de `gabarit.lien`). Tout
sommaire, toute ancre contextuelle passe par le mécanisme déjà employé pour le
lien d'évitement : un écouteur délégué qui appelle `focus()` et
`scrollIntoView()` sans toucher à l'adresse. Deux conséquences. La première est
qu'une section visée doit porter un `tabindex="-1"`, comme le fait déjà
`id="resultats"`, sans quoi le focus ne s'y pose pas. La seconde est qu'un lien
de section n'est pas partageable tant que le routeur ne sait pas lire
`#/cout/part-patronale` ; le décider avant, plutôt que de le regretter après.

**Fichiers.** `src/retraite_notionnelle/web/pages.py` et `web/gabarit.py`, et en
regard `moteur/js/pages.js` et `moteur/js/gabarit.js` — tout fragment HTML
existe deux fois, et le Python fait foi. Le style s'écrit une seule fois, dans
`gabarit.py`, d'où `scripts/construire_donnees.py` l'extrait vers
`moteur/style.css` ; à reconstruire après coup. Le comportement — replier,
filtrer, trier, chercher — va dans `index.html`, en écouteurs délégués : c'est là
que vit déjà celui du lien d'évitement et celui qui grise les statuts fermés.
Tests : `tests/test_web.py` et `tests/js/comparer-pages.mjs`, qui compare les
deux portages page à page.

**Marche.** Par page, et de la plus lourde à la plus légère — Coût, Données, Cas
types —, pas par procédé : un sommaire posé partout d'un coup ajoute du bruit aux
pages courtes. Pour chacune : donner d'abord aux titres leur niveau juste
(procédé 25), qui est la condition de tous les autres puisqu'un sommaire se
déduit des titres ; poser les ancres et le sommaire (1, 4) ; sortir de la prose
ce qui est référence et non lecture (12, 6, 8) ; alors seulement, là où le volume
le justifie encore, les filtres et la recherche (13 à 17), qui sont les seuls à
coûter du code de comportement. Les procédés 18 à 20 valent pour l'inventaire des
régimes et les tableaux de la page Coût ; le 22, pour la comparaison des six
scénarios, qui est le seul endroit du site où un comparateur a un sens.

**Garde-fous.** Aucune bibliothèque, ici pas plus qu'ailleurs. Rien qui rende un
chiffre inatteignable : replier n'est pas supprimer, et un filtre doit toujours
pouvoir être rendu à « tout afficher » — une réserve méthodologique masquée par
défaut est une réserve retirée. Le clavier d'abord, comme pour le focus des
résultats : un onglet, un filtre, un tri qui ne se prennent qu'à la souris ne
passeront pas la page Mentions, où le dépôt s'engage sur l'accessibilité. Et rien
qui calcule à l'affichage : l'accueil a été rendu rapide en ne lisant que ce
qu'il montre, un sommaire ne doit pas le défaire.

**Fin.** Un lecteur qui arrive sur la page Coût avec une question — combien coûte
la transition, qui paie la part patronale, ce que vaut tel chiffre — l'atteint en
un coup d'œil et un clic, et voit du premier regard ce que la page contient
d'autre. Le dépôt cesse de faire payer au lecteur la densité qu'il a mis un an à
accumuler.

**Ce que ça a déplacé.** Les six pages sont faites. L'action 16 a servi de
banc d'essai sur la plus lourde, puis la même forme a été appliquée aux cinq
autres : ce qui répond à la question en tête de page, et tout ce qui la
justifie dans des sections repliées qui se parcourent comme un sommaire.

| Page | Mots à traverser, avant | Après | Tableaux ouverts | Après |
|---|---|---|---|---|
| Coût | 5 652 | **530** | 9 | **0** |
| Données | 5 851 | **149** | 8 | **0** |
| Méthode | 2 375 | **339** | 1 | **1** |
| Cas types | 1 768 | **479** | 5 | **1** |
| Programme | 1 745 | **448** | 3 | **1** |
| Simuler | 1 318 | **281** (hors menus) | 0 | **0** |

Rien n'a été retiré : les pages pèsent toujours ce qu'elles pesaient, à deux
graphiques et deux tableaux près qui redisaient une série déjà tracée. Ce qui a
changé est ce qu'elles imposent avant qu'on ait choisi de lire, et
`BUDGETS_DE_LECTURE` le tient page par page dans `tests/test_web.py`.

Des vingt-cinq procédés ci-dessus, six ont porté l'essentiel : le résumé
d'abord (7), les blocs « à retenir » (8), l'affichage essentiel / tout afficher
(9), la séparation du principal et de la référence (12), les cartes
hiérarchisées (21) et la hiérarchie typographique (25). Deux ont été
inutiles : les procédés 1 à 4 — une pile de sections repliées EST un sommaire,
et elle évite l'obstacle de l'adresse-route — et les procédés 13 à 17, filtres
et recherche, qu'aucune page ne justifie plus une fois son détail rangé.

---

### 16. Refaire la page Coût : les recettes, et une page qu'on lit en trois minutes — `fait`

**Pourquoi.** Deux défauts d'un coup, et ils tenaient ensemble.

Le premier est un trou : la page montrait la DÉPENSE — d'où son nom — et les
RESSOURCES n'y existaient que par une courbe et un tableau de structure, en fin
de page, après tout le reste. Un système de répartition ne se juge pourtant pas
à sa dépense mais à son solde, et la question que tout le monde pose — « est-ce
que ça rapporte plus que ça ne coûte ? » — n'avait pas de réponse en tête de
page. L'action 6 avait posé les données ; personne n'en avait fait une lecture.

Le second est celui que l'action 15 décrit : 8 516 mots, seize tableaux, treize
titres, quinze mille pixels de haut. Rien n'y était faux ; tout y était au même
niveau d'importance, ce qui revient à n'en donner aucun. Une page qu'on ne lit
pas ne dit rien, si documentée soit-elle.

**Fichiers.** `src/retraite_notionnelle/web/pages.py` et `web/gabarit.py` ;
`moteur/js/pages.js`, `moteur/js/gabarit.js`, `moteur/js/equilibre.js` et
`moteur/js/cout.js` en regard ; `src/retraite_notionnelle/donnees/equilibre.py`
et `cout.py` ; `index.html` ; `tests/test_web.py`, `tests/test_cout.py` et
`tests/js/moteur.test.js`.

**Ce que ça a déplacé.**

- *Les recettes passent au même rang que les dépenses.* La page s'ouvre sur
  trois chiffres en euros — ce qui est sorti, ce qui est rentré, ce qui a
  manqué — et sur le graphique qui les tient : ressources et dépenses du système
  de retraite de 2002 à 2070, avec le ruban qui les sépare peint en vert quand
  il en reste et en rouge quand il en manque. Un second graphique, nouveau, dit
  d'où vient l'argent année par année : les quatre parts de `GROUPES`
  (`donnees/equilibre.py`), empilées en part de PIB, de 2004 à 2025. C'est le
  tableau 2.2 du rapport du COR rendu à sa dimension temporelle, et il montre ce
  qu'un tableau d'une seule année ne peut pas montrer — la part de l'impôt qui
  passe de 7 % à 15 % pendant que celle des cotisations ne bouge pas.
- *Le périmètre des cartes de tête est celui du COR, et uniquement.* Le modèle
  n'y intervient que par un rapport sans dimension. C'est ce qui a fait
  disparaître le graphique qui portait le niveau de dépense du modèle lui-même —
  19,3 % du PIB en 2070 contre 14,2 % au COR, écart que la page annonçait sous
  une phrase qui disait le contraire (« il ne dérape pas »). L'écart est
  maintenant écrit là où il se mesure, dans le dépliant des six scénarios, et
  nulle part ailleurs.
- *Deux graphiques ouverts au lieu de sept, aucun tableau ouvert au lieu de
  neuf, 535 mots à traverser au lieu de 5 652.* La page en contient toujours
  près de sept mille et quinze tableaux : rien n'a été retiré, sauf ce qui
  redisait une série déjà tracée. Tout le reste est dans huit sections repliées
  qui se lisent comme un sommaire — ce qui est, du catalogue de l'action 15, les
  procédés 7, 8, 9, 10, 12, 21 et 25 appliqués ensemble, et l'aveu que les
  procédés 1 à 4 n'étaient pas nécessaires ici : une pile de titres repliés EST
  un sommaire, et elle ne se heurte pas à l'obstacle de l'adresse-route.
- *Les trois tracés d'une part de PIB n'en font plus qu'un.* L'histoire depuis
  1959, le bilan jusqu'en 2070 et l'effet de la réforme suivaient la même
  grandeur sur trois fenêtres qui se recouvraient, à trois échelles verticales
  différentes : les comparer supposait de recomposer de tête ce qu'un seul cadre
  montre d'un coup. Les séries, elles, ne se recouvrent pas — chacune vaut
  `None` hors de la plage que sa source publie, et la courbe s'y interrompt.
  Le décrochement d'un demi-point entre la DREES et le COR, en 2002, se voit :
  c'est ce que les deux comptes ne comptent pas pareil, et le masquer aurait
  collé deux séries qui ne mesurent pas la même chose.
- *Les graphiques se lisent, et ils sortent du site.* Survol, doigt et flèches
  du clavier posent un trait de repère, un point sur chaque courbe et la valeur
  de l'année — lue dans le tableau de points que le tracé porte déjà, et non
  dans un attribut qui ferait une seconde vérité. Et un bouton compose, dans le
  navigateur, une image de la carte entière : question, réponse, tracé, légende,
  source, signature `@pliberal`. Sans bibliothèque et sans serveur — le SVG est
  cloné, ses styles calculés recopiés nœud à nœud, puis dessiné sur une toile
  où le texte est composé au trait. C'est, du catalogue de l'action 15, le
  procédé 24 poussé jusqu'à sa conséquence : la vue alternative d'un graphique
  n'est pas seulement un tableau, c'est aussi une image qui se poste.
- *Quatre briques nouvelles dans le gabarit*, portées des deux côtés :
  `cle(question, réponse, tracé, source)`, la carte encadrée qui se découpe et
  se comprend hors du site ; `depliant(titre, corps)`, la section repliée ;
  `mot(terme, définition)`, le mot de spécialiste qui porte sa définition ; et
  le paramètre `ecart` de `graphique()`, qui peint le ruban entre deux courbes
  en changeant de teinte à l'intersection exacte, interpolée.
- *Un piège du HTML, qui vaut d'être noté.* Le mot du glossaire a d'abord été un
  `<details>`. `<details>` fait partie des balises dont l'analyseur FERME un
  `<p>` ouvert : chaque mot coupait son paragraphe en deux, silencieusement, et
  la fin de la phrase tombait à la ligne. Le mot est désormais un `<button>`,
  qui est du contenu de phrase, et un test interdit à toute balise de bloc de se
  trouver dans un `<p>`, sur toutes les pages.

**Ce qui reste.** *Les quatre autres pages*, et l'action 15 les liste. Les
briques y sont réutilisables telles quelles : la carte, la section repliée, le
mot du glossaire, la lecture au survol et la composition d'image valent pour
tout graphique du site, et rien n'y est propre à la page Coût. *Le ruban d'écart
sur un axe qui descend sous zéro* : `_sommet` ne connaît que des valeurs
positives, ce qui interdit pour l'instant de tracer un solde directement, et
oblige à le lire comme l'écart de deux courbes. *Les recettes ne réagissent
toujours à rien* : le scénario 6, qui pose un taux unique de 18 %, déplacerait
l'assiette comme les pensions, et c'est l'action 11 qui ouvrirait cette porte.

### 17. Un calendrier à la place des champs d'âge — `fait`

**Pourquoi.** Le formulaire demandait cinq champs pour dire deux dates : une
année de naissance, un menu de douze mois, un âge de départ, un second menu de
douze mois, et, par métier, un âge d'entrée doublé d'un troisième menu. Or
personne ne connaît son âge de départ au mois près : on connaît une date. La
soustraction était demandée au lecteur, alors que c'est exactement ce qu'un
navigateur sait faire.

**Marche.** Trois champs date là où il en fallait cinq, et un calendrier —
celui du navigateur — partout où un âge était demandé. L'âge que la date fait
s'écrit sous le champ et se refait à chaque frappe.

**Ce que ça a déplacé.** *Aucun chiffre.* Les 478 témoins de simulation sont
inchangés au bit près, et les deux qui s'y ajoutent décrivent au calendrier une
carrière qu'un témoin décrivait déjà par des âges : ils portent les mêmes
chiffres, ligne à ligne. Les témoins de page bougent tous, et d'une seule
façon — le formulaire, et les adresses qu'il écrit.

- *Un champ date, et non un champ mois.* `type="month"` serait le champ juste :
  le modèle ne descend pas sous le mois, et le jour n'entre dans aucun calcul.
  Mais Firefox et Safari de bureau ne savent pas l'ouvrir — ils le rendent en
  texte brut, où il faut écrire « 1975-03 » à la main. `type="date"` ouvre le
  même calendrier partout, dans la langue du lecteur. Le jour de naissance est
  donc gardé tel qu'il est saisi — répondre « 1er mars » à qui est né le 15
  ferait douter de ce que la page a compris —, et les dates de carrière sont
  ramenées au premier du mois, où le droit place toute prise d'effet.
- *L'adresse perd trois paramètres.* `debut=1996-09` dit d'un coup ce que
  `debut=21` et `debut_mois=8` disaient à deux. Les adresses d'ancienne forme
  restent lues telles quelles, y compris l'âge décimal d'avant les mois
  (`liquidation=64.5`) : un témoin figé le vérifie des deux côtés du portage,
  et un test compare les deux écritures de la même carrière.
- *Un gain qu'on n'était pas allé chercher.* Le changement de métier se date au
  mois, ce qu'il ne savait pas faire : l'âge entier était tout ce que le champ
  acceptait, et un métier commencé en mai commençait en janvier. Le calendrier
  le donne sans un champ de plus.
- *Les bornes sont des âges, et le calendrier les porte.* On entre dans la vie
  active entre 14 et 40 ans, on part entre 40 et 75 : ce sont des âges, que le
  champ porte en `data-age-min` et `data-age-max` et que la page retraduit en
  dates à chaque frappe, sans attendre un calcul. Un refus les redit en dates
  — « de septembre 2015 à septembre 2050 » —, faute de quoi il laisserait la
  soustraction à faire à qui vient d'écrire une date. Et, comme pour les champs
  numériques, un test vérifie que le mois d'à côté est refusé par le modèle :
  une adresse forgée à la main ne passe par aucun calendrier.

### 18. La carrière peut s'arrêter avant le départ — `fait`

**Pourquoi.** Découvert en relisant l'action 17 : le formulaire demandait une
date de début d'activité et une date de départ, et supposait qu'on avait
travaillé entre les deux. Qui cesse à 58 ans pour liquider à 64 voyait donc six
années cotisées qu'il n'a pas vécues. Le champ « Interruptions » permettait bien
de les retirer — « 2020:2026:chomage_indemnise » —, mais il est enfoui dans les
options de modélisation, il demande d'écrire une syntaxe, et rien sur la page ne
laissait deviner qu'il fallait s'en servir. Le défaut silencieux est le pire de
tous : il donne un chiffre, et il est faux.

**Marche.** Aucune date de fin d'activité en plus : une ligne de carrière peut
n'être pas un emploi. Le menu des statuts de chaque ligne suivante propose, à la
suite des métiers, les neuf motifs de `periodes_non_travaillees.csv`. La
dernière ligne dit alors quand l'activité s'arrête.

**Ce que ça a déplacé.** *Aucun chiffre.* Les 480 témoins de simulation sont
inchangés au bit près, et les quatre qui s'y ajoutent sont ceux du chemin neuf.
Ce qui change est ce que le formulaire SAIT recevoir — et, pour qui s'arrête
avant de partir, un chiffre qui devient vrai.

- *Une ligne, et non un champ.* « À partir de quand, et quoi » : c'est ce que
  demandait déjà une ligne de métier, et une période sans emploi ne demande rien
  d'autre. Le formulaire ne gagne donc aucun champ — il en perd un sur ces
  lignes-là, le revenu, qu'une période sans emploi ne paie pas. Une date de fin
  d'activité séparée aurait coûté deux champs à tout le monde (la date et le
  motif) pour couvrir moins de cas : celle-ci décrit aussi les creux au MILIEU
  d'une carrière.
- *Le motif n'est pas un détail.* Carrière type arrêtée à 57 ans, départ à 64 :
  chômage indemnisé 1 975 €, chômage non indemnisé 1 819 €, inactivité 1 396 €
  au scénario 1. Le premier valide des trimestres ET fait cotiser l'UNEDIC aux
  complémentaires — d'où 326 € contre 276 € au scénario 2, où seule la
  cotisation réellement versée compte. Le troisième n'ouvre rien : c'est la
  réponse du modèle à qui n'est ni en emploi ni au chômage.
- *Un statut qui existait en double.* « Sans activité professionnelle » est à la
  fois une affiliation sans régime et un motif de la table des périodes. Les
  deux donnent le même résultat au bit près — c'est vérifié —, mais deux options
  de même valeur dans un menu, c'est une saisie qui ne revient pas : la première
  ligne garde l'affiliation qu'elle a toujours eue, les suivantes lisent le
  motif, et un test interdit désormais à tout menu du site de proposer deux fois
  la même valeur.
- *La maille reste l'année.* Une période sans emploi est bornée au mois, le
  moteur ne connaît qu'un statut par année civile : l'année où l'activité
  s'arrête revient à ce qui en occupe le plus de mois, à égalité elle reste
  travaillée. C'est la convention déjà retenue pour l'année d'un changement de
  métier ; `limites.md` la redit pour celle-ci.

### 19. Le simulateur, réduit à ses champs et à ses chiffres — `fait`

**Pourquoi.** Le formulaire s'ouvrait sur quatre-vingt-dix mots — un chapeau, un
encadré, un dépliant — avant le premier champ, et la page de résultats faisait
suivre chaque tableau de cent à cent soixante-cinq mots de commentaire. Rien de
tout cela n'est faux, et rien n'est nécessaire pour remplir un champ ou lire un
chiffre. Or on vient ici pour remplir des champs : le reste est du temps pris à
quelqu'un qui a déjà décidé.

**Marche.** Ce qui est nécessaire reste écrit ; ce qui explique, nuance ou
justifie passe derrière un point d'interrogation, dans la bulle que le glossaire
utilisait déjà pour ses mots de jargon. La ligne de métier vide se replie, et le
sexe rejoint les options de modélisation.

**Ce que ça a déplacé.** *Aucun chiffre* : les 484 témoins de simulation sont
inchangés au bit près. Ce qui change est ce qu'on lit à l'ouverture.

| | Avant | Après |
|---|---|---|
| Formulaire vierge | 424 mots | **115** |
| Page de résultats | 3 351 mots | **1 484** |

- *Une bulle, et non un dépliant.* `g.bulle` reprend le bouton, la bulle et le
  basculement en écoute déléguée que `g.mot` avait déjà : même mécanique, même
  accessibilité — `aria-expanded`, pas d'attribut `title`, ouverture au clavier
  —, autre ancre. Un mot de jargon est souligné dans la phrase ; un appel est un
  point d'interrogation posé après un titre ou un libellé de champ, et son
  `aria-label` est son seul nom. Vingt-deux appels sur la page de résultats.
- *Ce qui reste visible est ce qui porte un chiffre.* Un montant, une date, un
  âge, une unité, un refus, un avertissement. Ce qui explique d'où vient le
  chiffre s'ouvre à côté de lui. La règle a tranché tous les cas : « la
  fourchette ne fait varier que la productivité » est du commentaire, « le
  scénario 2 passe de 467,21 € à 467,21 € » est un résultat.
- *Le clic d'un appel ne fait plus deux choses.* Un `<button>` dans un `<label>`
  active aussi le champ que le libellé désigne : sur un champ date, le
  calendrier s'ouvrait par-dessus la bulle. `preventDefault` sur l'écouteur
  délégué le règle une fois pour tous les appels.
- *La ligne de métier vide coûtait un tiers du formulaire.* Trois champs offerts
  à qui n'en veut pas, alors que la plupart des carrières n'ont qu'un métier.
  Il n'en reste que la demande — « Ajouter une période » —, et les champs
  paraissent si on la suit. Un `<details>` et non un `<fieldset>` : c'est le
  résumé qui nomme le groupe, et le nommer deux fois ferait lire deux titres
  pour une période qui n'existe pas encore.
- *Le sexe est sans effet par défaut, et il était en tête.* Il ne compte que de
  deux façons : si la table de conversion est « par sexe », et si la carrière
  porte des enfants — le système actuel réserve à la mère la majoration de durée
  d'assurance. Les deux réglages qui le font compter vivent dans les options ; il
  les rejoint. Sur la carrière type, `sexe=H` et `sexe=F` donnent la même pension
  au centime près tant qu'on n'y a pas touché, et c'est vérifié.

### 20. Une bibliothèque de pictogrammes, au lieu de trois dessins — `fait`

**Pourquoi.** Le site n'avait pas d'icônes : il avait trois façons d'en faire
semblant. Un emoji 📈 posé dans un `<text>` SVG servait d'icône de page — son
dessin change avec le système, et il se brouillait en petit ; un chevron était
tracé à coups de bordures CSS tournées à 45° ; les autres dépliants gardaient le
triangle du navigateur, qui n'a pas deux fois la même forme sur deux moteurs ;
l'appel d'une bulle était un point d'interrogation typographique dans un cercle
dessiné en CSS. Trois grilles, trois épaisseurs, aucune échelle commune.

**Marche.** Un seul jeu, **Lucide 1.46.0** (licence ISC) : grille de 24, trait
de 2, extrémités et jointures arrondies. Les originaux sont recopiés sans
retouche dans `moteur/icones/`, le tracé est écrit dans les deux gabarits — le
portage n'utilise aucune bibliothèque, et la page ne charge aucune ressource
tierce —, et un test rouvre les fichiers pour vérifier que les tables disent
exactement ce qu'ils disent.

**Ce que ça a déplacé.** *Aucun chiffre*, et cinq pictogrammes : `chevron-down`
sur tous les dépliants, `circle-help` sur l'appel d'une bulle, `download` sur le
bouton qui compose l'image, `triangle-alert` sur l'avertissement de liquidation
non ouverte, `trending-up` pour la marque du site — dans le bandeau et dans
`moteur/icone.svg`, l'icône de page.

- *Le tracé est dans le code, l'original dans le dépôt.* C'est la seule façon de
  tenir ensemble deux promesses du site : aucune ressource tierce chargée, aucun
  paquet dans le portage. Le risque — une table qui dérive de son original, ou
  qui diverge d'un moteur à l'autre — est tenu par deux tests : l'un compare la
  table aux fichiers de `moteur/icones/`, l'autre demande au portage JavaScript
  d'imprimer la sienne et la compare à celle de Python, entrée par entrée.
- *Un dépliant n'a plus le chevron de son navigateur.* `summary::marker` est
  masqué une fois pour tout le site, et chaque résumé passe par `g.sommaire` :
  même chevron, même place, même rotation à l'ouverture. Un test parcourt les
  six pages et refuse un `<summary>` qui ne commencerait pas par lui.
- *L'icône de page est un fichier, et elle tient à toutes les tailles.* Le carré
  de la charte, le tracé de `trending-up`, la même grille : vérifiée à 16, 32,
  64 et 128 px, elle garde sa forme et son poids là où l'emoji se brouillait.
- *Un test interdit le retour des faux pictogrammes.* Aucun emoji dans le HTML
  rendu des six pages, ni dans `index.html`, ni dans la feuille de style : c'est
  par là que celui-ci était entré.

### 21. Les résultats sur un téléphone : le chiffre d'abord, le reste replié — `fait`

**Pourquoi.** Deux défauts se cumulaient sous les six montants, et le second
n'apparaissait qu'à cause du premier.

Un bug d'affichage, d'abord. Sous 34 rem, l'entête d'un scénario passe en
colonne pour que le montant tombe sous son intitulé ; mais `flex: 1 1 14rem`,
écrit pour la disposition en ligne, ne réserve plus une largeur en colonne — il
réserve une **hauteur**. Chaque scénario portait donc 224 px de vide entre son
titre et son chiffre, six fois de suite : sur un écran de 390 points, le premier
montant de la page tombait sous la ligne de flottaison, et lire les six en
demandait cinq.

Une question d'édition, ensuite. L'action 19 avait réduit la page à ses champs
et à ses chiffres, l'action 15 avait rangé les pages longues en sections
repliées — mais la page de résultats faisait toujours suivre ses six montants de
sept sections dépliées : un graphique, neuf tableaux, 2 958 mots. Dix écrans de
téléphone à traverser après le résultat, pour quelqu'un qui n'a pas fait
d'économie et qui est venu chercher un chiffre.

**Marche.** La règle CSS qui rend au titre sa hauteur de texte, et les sept
sections derrière `g.depliant` — le même procédé que la page Coût, sous le même
titre « Pour aller plus loin ». Chaque section garde son nom en résumé, et
l'appel qui portait son titre passe dans la phrase de tête de son contenu.

**Ce que ça a déplacé.** *Aucun chiffre* : les témoins de simulation sont
inchangés au bit près, et ceux des pages ne bougent que de la structure.

| | Avant | Après |
|---|---|---|
| Mots à traverser, formulaire et résultats | 3 744 | **1 407** |
| Tableaux ouverts | 8 | **0** |
| Graphiques ouverts | 1 | **0** |
| Hauteur de la page, écran de 390 points | 11 871 px | **4 085 px** |

- *Le détail est rangé, pas retiré.* Sept sections nommées — ce que chaque
  scénario finit par verser, ce que l'hypothèse pèse, d'où vient l'écart, qui
  verse la cotisation, le scénario 6, la cascade du 1 au 3, le détail du calcul
  —, qui se parcourent du regard et s'ouvrent une par une. Les 4 200 mots qu'on
  ne lit plus d'office sont toujours là, à un doigt.
- *Ce que le téléphone gagne encore.* Les tableaux du détail passent à
  0,88 rem et resserrent leurs marges — un cinquième de hauteur en moins, une
  colonne de plus avant que la zone ne défile —, et le retrait d'une section
  repliée leur rend 26 points de largeur.
- *Seconde passe : ce que le téléphone ne dit pas à la page.* La première
  passe avait été mesurée dans un navigateur de bureau réduit à 390 points, où
  les deux montants d'un scénario tiennent côte à côte. Sur un vrai téléphone,
  ils n'y tenaient pas : aucun des empattements de la charte n'existe sur
  Android, qui leur substitue un serif plus large, et le réglage « taille du
  texte » du système grossit le tout par-dessus sans que les requêtes média le
  voient — elles restent calées sur 16 px. Une somme insécable dans une rangée
  qui ne se replie pas : « par mois, en euros de 2039 » sortait de la carte, et
  la page entière défilait horizontalement. Les libellés se replient désormais,
  les sommes jamais, et la rangée passe à la ligne en dernier recours ; le trait
  qui séparait les deux montants disparaît sur téléphone, faute de sélecteur qui
  dise qu'une rangée s'est repliée. Vérifié sans aucun débordement de 320 à
  1 280 points, jusqu'à 150 % de grossissement et avec deux serifs de
  substitution — la règle « écran très étroit » de 22 rem, qui traitait le même
  défaut trop tard, disparaît.
- *La cible tactile d'un appel de bulle.* La feuille de style promettait 24 px
  de côté (WCAG 2.5.8) ; le padding seul la dimensionnait en proportion du
  texte, et elle tombait à 19 px dans une glose ou une note — où se trouvent
  justement la plupart des appels. Un minimum l'y tient.
- *Trois tests tiennent l'ensemble.* Le budget de lecture couvrait « /simuler »
  sans paramètres, c'est-à-dire le formulaire seul : il couvre maintenant la
  page de résultats, avec la même borne de mots, aucun tableau ni graphique
  ouvert, et le détail plus lourd que ce qui reste visible. Les deux autres
  gardent les règles CSS elles-mêmes, faute de quoi le trou de 224 px
  reviendrait sans que rien ne le dise.

---

### 22. La surcote que les régimes en points écrivent et que le moteur laisse tomber — `à faire`

**Pourquoi.** Découvert en menant l'action 9, qui demandait de vérifier si
d'autres régimes en points étaient dans le même cas. Ils le sont, et pour une
raison plus bête que la sienne : la branche en POINTS de `calculer` ne lit pas
`surcote_par_trimestre`. Ce champ n'est consulté que par la branche en
annuités, si bien qu'une surcote écrite dans une fiche de régime en points n'a
aucun effet — elle est chargée, portée par la période, transportée jusque dans
`moteur/donnees.json`, et jamais servie. Le catalogue distingue pourtant
soigneusement les régimes qui en ont une de ceux qui n'en ont pas : la CARCDSF
porte `null` parce que « il n'existe pas de surcote dans le régime
complémentaire au-delà du taux plein », la CNBF aussi pour la même raison
citée à sa source. Ces `null`-là ne servent à rien tant que les autres ne
servent à rien.

**Qui est touché.** Neuf fiches, toutes chez les non-salariés : la CNAVPL
(0,75 %), la MSA des non-salariés (0,75 % puis 1,25 %), la CARMF, la CAVEC, la
CIPAV et l'ASV des conventionnés (1,25 %), la CARPIMKO (0,75 %), la CPRN (1 %)
et la CAVP (0,5 %). C'est le régime de BASE des professions libérales qui pèse
le plus : la CNAVPL est un régime en points, et sa surcote est celle de
l'article L. 643-1-1, la même que celle du régime général.

**Ce qui n'est pas une simple ligne à ajouter.** Les neuf ne comptent pas leurs
trimestres de la même façon, et c'est tout le travail. La CNAVPL et la MSA
suivent la règle du régime général — cotisés, au-delà de l'âge légal, au-delà
de la durée requise —, et leur fiche porte une durée requise. Les sept
complémentaires de sections libérales n'en portent aucune : « sur la base de
l'âge légal de départ à la retraite est appliqué un coefficient correspondant à
l'âge de l'affilié », écrit la CPRN, « aucune durée d'assurance n'y entre ».
Leur surcote se compte donc en trimestres ÉCOULÉS au-delà du taux plein, comme
le 1° de l'arrêté de l'Ircantec. C'est la distinction que `_abattement_points`
fait déjà sous le nom de `par_age_seul`, et c'est elle qu'il faut reprendre.

**Un plafond à ne pas oublier.** La CPRN borne sa surcote « jusqu'au
soixante-dixième anniversaire ». Aucun champ ne porte cette borne aujourd'hui,
et aucune carrière simulée ne l'atteint — mais l'écrire est moins cher que de
découvrir un jour qu'on sert au-delà.

**Fichiers.** `src/retraite_notionnelle/scenarios/actuel.py` (la branche en
points de `calculer`, et `_surcote_points` que l'action 9 y a laissé),
`moteur/js/scenario-actuel.js`, `data/reference/regimes/non_salaries.yaml`,
`data/reference/regimes/_schema.yaml`, les témoins, `limites.md` §3.

**Fin.** Un test interdit qu'une période en points porte un
`surcote_par_trimestre` que personne ne lit — c'est le garde-fou qui manquait,
et qui aurait signalé le défaut sans qu'on le cherche.

---

### 23. La revue extérieure du 15 septembre 2026 : vingt-sept chantiers sur le site — `à faire`

**Pourquoi.** Une relecture des six pages publiées (Programme, Simuler, Cas
types, Coût, Méthode, Données), faite par un lecteur extérieur au dépôt le
15 septembre 2026 et transmise le 16. Elle ne porte pas sur le modèle mais sur
ce qu'un visiteur en voit : le parcours, la clarté des arguments, l'architecture
de l'information, et les tics d'écriture qui signalent un texte généré. C'est
la première revue du site qui ne vienne pas d'une session de travail, et elle
vaut d'être gardée entière plutôt que dispersée dans les actions existantes.

**Comment la tenir.** Chaque chantier a sa case, à cocher quand il est fait ;
on y ajoute alors une ligne « ce que ça a déplacé », comme partout ailleurs
dans ce fichier. Un chantier qu'on écarte reste dans la liste, barré, avec la
raison. Les priorités sont celles du relecteur : 🔴 haute (change la
compréhension ou bloque l'usage), 🟠 moyenne (gêne réelle, contournable),
⚪ basse (finition). Le texte de chaque chantier est le sien, tel que reçu.

**À vérifier avant de commencer.** La revue a été écrite sur le site tel qu'il
était le 15 septembre ; deux chantiers recoupent des travaux déjà faits, et il
faut d'abord regarder ce qui en reste :

- *Les bulles de définition* (thème 1, premier chantier) : la bulle du
  glossaire existe déjà — action 19 — pour les mots de jargon du simulateur.
  Le chantier devient : vérifier quels termes de la liste du relecteur n'en ont
  pas encore, et étendre la bulle aux autres pages.
- *Le scénario 6 en avant* (thème 1) et *la clé de lecture avant les tableaux*
  (thème 2) : l'action 16 a ramené les cinq grilles de Cas types à une seule,
  accompagnée de trois chiffres. Vérifier ce que le relecteur voyait encore et
  si le reste du chantier tient.

**Fichiers.** Presque tout est dans `src/retraite_notionnelle/web/pages.py` et
`web/gabarit.py`, avec leur portage `moteur/js/pages.js` et `moteur/js/gabarit.js`,
et les témoins `tests/temoins/pages.json` à régénérer après chaque passe. Les
chantiers du thème 4 ne touchent que le texte ; ceux du thème 1 qui ajoutent un
composant (recherche dans le menu des statuts, table filtrable) se heurtent à
la contrainte relevée par l'action 15 : rien qui ne se prenne qu'à la souris,
et rien qui défasse ce que la route affiche.

**Fin.** Les vingt-sept cases cochées ou barrées, et une ligne au Journal par
passe, disant quelles pages ont bougé et de combien de mots.

---

#### 1. Expérience utilisateur

*Le design visuel est déjà sobre et cohérent (thème sombre, pas de fioritures) ; les frictions viennent surtout de la densité du contenu et de l'absence d'outils pour la traverser.*

- [ ] 🔴 **Des bulles de définition sur le vocabulaire technique** `Simuler · Global`
  Le simulateur est le point d'entrée le plus concret du site — celui où « le commun des mortels » vient voir sa propre pension, pas seulement un lecteur déjà averti. Il concentre pourtant du jargon non défini : « compte notionnel », « trimestres » / « durée d'assurance », « décote » / « surcote », « salaire de référence », « table de mortalité unisexe », « taux de remplacement », « assiette déplafonnée », « statut d'affiliation ». Souligner ces termes en pointillé et afficher, au clic ou au survol, une définition d'une ou deux phrases en langage courant — sans jargon économique, sans renvoi obligé vers Méthode. Un seul petit composant de bulle, réutilisé partout où le terme reparaît (Programme, Cas types, Coût), évite d'avoir à choisir entre simplifier le texte et perdre la précision : la précision reste dans la bulle, la phrase principale reste lisible.

- [ ] 🔴 **Expliquer l'âge de référence, pas seulement l'afficher** `Simuler`
  Après calcul, les résultats ouvrent sur cinq pastilles chiffrées (43 années cotisées, 64 ans liquidation, **67 ans — âge de référence — départ 3 ans plus tôt**, 25,667 coefficient de conversion, 252 025 € capital notionnel) sans un mot sur ce que chacune change. L'âge de référence n'est pourtant pas cosmétique : sur l'exemple testé, le scénario 3 convertit les droits acquis au diviseur de 67 ans alors que la pension part à 64 — l'anticipation est payée une seconde fois, ce que la page reconnaît elle-même (« l'anticipation est donc payée une seconde fois, sur le passé »). Le réglage qui corrige ça (« Conversion des droits acquis » → « à l'âge de départ effectif », présenté comme ce qu'« une réforme réelle retiendrait ») est enterré dans les options repliées, en bas de formulaire, et n'est pas la valeur par défaut. Trois choses à faire : une bulle de définition sur « âge de référence » (voir le chantier ci-dessus) ; une phrase explicite dès que l'âge de départ saisi est inférieur à l'âge de référence, qui nomme la pénalité et pointe vers le réglage qui l'enlève ; et réexaminer si « à l'âge de départ effectif » ne devrait pas être le défaut plutôt qu'une option cachée.

- [ ] 🔴 **Rendre cherchable la liste des statuts d'affiliation** `Simuler`
  Le menu « Statut d'affiliation » aligne plus de 60 entrées dans un `<select>` natif sans recherche, répété à l'identique pour le second métier. Trouver « SNCF » ou « artisan » suppose de tout parcourir. Ajouter un champ de recherche/autocomplétion, ou grouper les options par famille (privé, public, agricole, libéral, spécial) avec des `<optgroup>`.

- [ ] 🔴 **Mettre le scénario 6 (la proposition) en avant, pas en dernier** `Cas types`
  Cinq tableaux de 13 lignes × 7 générations s'enchaînent (scénarios 2 à 6) avant d'atteindre la proposition réelle. Un lecteur pressé s'arrête souvent au premier — un contrefactuel, pas la proposition. Ajouter des onglets ou un sélecteur de scénario, avec le scénario 6 affiché par défaut.

- [ ] 🟠 **Transformer la page Données en table filtrable** `Données`
  72 régimes (35 modélisés, 37 partiels, 15 hors champ) listés en prose continue avec leur niveau de fiabilité. Impossible de vérifier un régime précis sans faire Ctrl+F. Le contenu est intrinsèquement tabulaire : en faire un tableau triable et filtrable (par famille, statut, fiabilité).

- [ ] 🟠 **Ajouter un sommaire aux pages longues** `Coût · Données`
  Coût et Données déroulent plusieurs dizaines d'écrans (graphiques, tableaux, encarts « ce que ça ne dit pas ») sans ancre ni retour en haut. Une table des matières collante en tête de page rendrait la navigation praticable.

- [ ] ⚪ **Généraliser les sections repliables** `Toutes`
  Cas types propose déjà des triangles ▸ dépliables (« Ce que recouvre chacun des treize cas types »). Données, tout aussi dense, n'en a aucun. Généraliser le pattern à chaque page à forte densité de texte.

- [ ] 🟠 **Vérifier le rendu mobile des tableaux à 7 colonnes** `Cas types · Coût`
  Non testé durant cette revue : à confirmer explicitement. Les tableaux « écart par génération » (7 colonnes de 1940 à 2000) et ceux de la page Coût risquent de déborder sur petit écran. Prévoir un conteneur à défilement horizontal borné, ou une vue empilée en dessous d'un certain seuil.

- [ ] ⚪ **Transformer les chemins de fichiers cités en liens** `Coût`
  La page Coût cite « docs/limites.md § 5 ter » comme une référence en texte brut plutôt qu'un lien cliquable. Chaque renvoi à un document du dépôt devrait pointer directement vers ce document.

#### 2. Clarté des arguments

*L'argumentaire de la page Programme est solide et bien construit (constat → alternative → comparaison → transition). Le point faible est ailleurs : ce que les pages de preuve montrent peut contredire, en apparence, ce que Programme promet.*

- [ ] 🔴 **Expliquer la baisse affichée avant les tableaux, pas après** `Cas types`
  Le scénario 6 — la proposition réelle — affiche entre -28 % et -76 % de pension par rapport à aujourd'hui pour la plupart des carrières. La clé de lecture existe (« un coefficient supérieur à un n'est pas une économie, c'est une marge »), mais elle est sur la page Coût, pas sur Cas types. Un lecteur qui saute directement aux tableaux peut comprendre l'inverse du message. Mettre cette clé de lecture en tête de Cas types, avant les chiffres.

- [ ] 🔴 **Rappeler que le système actuel n'est pas stable, dans les tableaux eux-mêmes** `Cas types · Coût`
  Programme insiste sur le déficit (-0,17 % du PIB en 2025, 19,3 % du PIB projeté en 2070). Les tableaux de Cas types comparent pourtant chaque scénario à « aujourd'hui » comme s'il s'agissait d'un point fixe. Le vrai choix n'est pas « notionnel contre système stable » mais « notionnel contre système qui dérive ». Rappeler la trajectoire du système actuel à côté de chaque comparaison.

- [ ] 🟠 **Distinguer visuellement « contrefactuel » et « proposition »** `Cas types · Coût`
  Que les scénarios 2 à 5 soient des exercices théoriques et que seul le 6 soit la proposition du parti est expliqué en préambule, mais jamais rappelé au niveau de chaque tableau. Un badge « proposition » sur le scénario 6 et « contrefactuel » sur les autres évite l'erreur de lecture au moment où elle se produit.

- [ ] 🟠 **Ajouter un résumé en langage courant aux pages techniques** `Coût · Méthode · Données`
  Ces pages sont rigoureuses mais écrites pour un lecteur déjà convaincu ou technicien (« coefficient d'équilibre », « assiette déplafonnée », « EIR 2020 »). Trois ou quatre phrases en langage simple avant le détail donneraient un point d'entrée à un lecteur non spécialiste, sans rien retirer à la rigueur qui suit.

- [ ] ⚪ **Sortir l'autocritique méthodologique de la masse de texte** `Coût`
  La comparaison à la projection du COR (« notre écart vaut -0,3 point de PIB au départ et 5,1 à l'arrivée […] il n'est pas flatteur ») est un vrai gage de sérieux, mais elle est noyée dans un paragraphe. En faire un encart « point de vigilance » à part la transforme en argument de crédibilité au lieu de la laisser passer inaperçue.

- [ ] ⚪ **Remonter le tableau de la garantie vieillesse** `Programme`
  Le tableau « 300 € et 1 500 € → 0 € aujourd'hui, 500 € avec la garantie » est l'argument le plus immédiatement parlant du site pour un lecteur non spécialiste. Il arrive tard, après plusieurs tableaux denses. Le rapprocher du haut de page renforcerait l'accroche.

#### 3. Architecture

*Le moteur (Python de référence + JS sans dépendance, 469 cas de test à parité bit-à-bit) est une vraie force technique, à préserver telle quelle. L'architecture de l'information, elle, mériterait d'être retravaillée.*

- [x] 🔴 **Protéger le texte et l'habillage du site, pas seulement le code** `Global · Dépôt`
  Le texte du site — l'argumentaire de Programme, les explications de chaque page — est une œuvre protégée par le droit d'auteur dès sa création, sans qu'aucune licence ne soit nécessaire pour ça. Le choix actuel fait l'inverse : « cette page […] sous licence libre » renvoie au MIT, qui autorise explicitement la copie et la modification du texte par un tiers, à la seule condition de garder une notice dans les copies du *code* — une condition qui ne s'applique même pas à qui reprend juste la prose d'une page sans toucher au dépôt. Si l'objectif est de protéger cette expression-là (le texte, pas l'idée qu'il porte — voir le constat plus bas), deux pistes : sortir la prose éditoriale de la licence MIT et la laisser sous « tous droits réservés », le régime par défaut du droit d'auteur français, sans rien à publier pour l'obtenir ; ou choisir une licence Creative Commons plus adaptée à du texte que le MIT ne l'est, par exemple CC BY-ND (partage autorisé, réécriture ou déformation du message interdite) ou CC BY-SA (partage et adaptation autorisés, mais attribution et même licence obligatoires en aval). Un repère, pas un avis juridique — à faire trancher par un juriste avant de changer quoi que ce soit.
  *Fait le 16 septembre 2026.* Le code est passé de MIT à Apache 2.0, et les
  textes, infographies, graphiques, tableaux et la documentation sous CC BY-SA
  4.0, la seconde des deux pistes proposées : reprise et adaptation libres, à
  condition de citer le site et de republier sous la même licence. `LICENSE`
  dit ce que chaque licence couvre ; le README, la page « À propos » et le pied
  de page reprennent la règle, dans le Python et son portage. Le nom et le
  logo du parti ne sont couverts par aucune des deux.

- [x] 🟠 **Pour les données : un droit séparé existe, indépendant de la licence du code** `Données · Dépôt`
  Les séries et barèmes bruts sont en grande partie des faits, que le droit d'auteur classique ne protège pas, quelle que soit la licence choisie. Le droit français prévoit néanmoins un régime distinct, le droit sui generis des producteurs de bases de données (articles L341-1 et suivants du code de la propriété intellectuelle, transposant la directive 96/9/CE) : il protège celui qui démontre un investissement substantiel dans la constitution, la vérification ou la présentation d'une base de données, contre la réutilisation d'une partie substantielle de son contenu — ce que documente déjà, de fait, la page Données avec ses 72 régimes recoupés contre LEGI, DILA, COR et DREES. Ce droit existe indépendamment de la licence du code : la publier en MIT ne l'éteint pas forcément, mais ne le mentionne pas non plus. À faire vérifier par un juriste avant de fixer la licence des données, plutôt que de la déduire de celle du moteur.
  *Fait le 16 septembre 2026, avec le précédent.* `LICENSE` ne déduit plus la
  licence des données de celle du moteur : les données de `data/` restent sous
  les conditions de leurs producteurs, et ni l'Apache 2.0 du code ni la CC BY-SA
  des textes ne les couvrent.

  > **Constat (pas une action) :** la proposition elle-même — comptes notionnels, taux unique à 18 %, garantie vieillesse individualisée — n'est protégeable par aucune licence : le droit d'auteur couvre une expression, jamais une idée ou un système. N'importe quel parti peut reprendre le principe sans rien devoir au dépôt, quoi que ce dernier choisisse pour son texte ou ses données — et c'est en général dans l'intérêt d'un parti que sa proposition circule et se discute. Ce qui reste établissable, ce n'est pas l'exclusivité de l'idée mais son antériorité : la publication datée et publique en fait déjà foi.

- [ ] 🔴 **Regrouper la navigation par fonction, pas juste par page** `Global`
  Les six entrées (Programme, Simuler, Cas types, Coût, Méthode, Données) ne distinguent pas le message (Programme), la preuve (Simuler, Cas types, Coût) et la confiance (Méthode, Données). Un visiteur ne sait pas où aller après Programme. Regrouper visuellement la nav en blocs, ou ajouter une micro-description sous chaque lien.

- [ ] 🟠 **Traiter Données comme une base, pas comme un article** `Données`
  La taxonomie (certifiée / haute / moyenne / estimée × modélisé / partiel / hors champ) est un vrai jeu de données. La rendre en tableaux HTML statiques dans une page de prose sous-exploite sa structure. C'est la page qui justifierait le plus un vrai composant de table interactive.

- [ ] 🟠 **Créer des renvois croisés entre pages complémentaires** `Programme · Méthode · Cas types`
  Programme renvoie vers Méthode (« le détail du calcul »), mais rien ne relie Méthode aux cas concrets qui l'illustrent en retour. Ajouter des renvois contextuels dans les deux sens entre Programme, Méthode et Cas types.

- [ ] ⚪ **Donner plus de visibilité à la rigueur technique du dépôt** `Méthode`
  Le moteur JS sans framework, validé contre le modèle Python sur 469 cas à la précision du flottant, est un vrai argument de confiance auprès d'un public technique — actuellement seulement accessible via le lien GitHub en bas de Programme. Un lien « comment c'est construit » depuis Méthode le mettrait en valeur là où le lecteur est déjà dans le détail.

- [ ] ⚪ **Vérifier les méta-descriptions par route** `Global`
  Le routage en hash (#/) n'est pas un problème pour un site statique GitHub Pages, mais chaque route doit avoir sa propre balise `<title>` (déjà le cas, vérifié) et sa propre méta-description, pour un partage et un référencement corrects.

#### 4. Gommer la touche IA

*Le design visuel n'a pas ce problème : pas de dégradés, pas d'icônes génériques, pas d'emoji. La « touche IA » à corriger est dans le texte — des procédés rhétoriques efficaces isolément, mais reconnaissables à force d'être répétés à l'identique.*

- [ ] 🔴 **Varier le procédé « Ce n'est pas X, c'est Y »** `Global`
  Répété des dizaines de fois sur l'ensemble du site (« ce n'est pas une économie, c'est une marge » ; « ce n'est pas l'ASPA à un autre montant » ; « non du passage aux comptes notionnels »…). Efficace isolément, systématique à l'échelle du site, ce qui le rend reconnaissable comme procédé. Relire chaque page en variant : comparaison implicite, exemple concret, question rhétorique.

- [ ] 🟠 **Sortir les rubriques « Ce que cette page ne dit pas » du gabarit** `Coût · Données`
  Bon réflexe de transparence, mais le titre quasi identique d'une page à l'autre (« Ce que cette page ne dit pas », « Ce que ce solde ne dit pas ») accentue l'effet de patron répété. Varier les titres et intégrer ces réserves plus naturellement dans le texte plutôt qu'en rubrique systématique.

- [ ] 🟠 **Alléger les incises en tiret cadratin** `Global`
  Usage très dense du tiret cadratin en incise (« — c'est-à-dire […] — », « — et c'est […], — »). C'est l'un des tics de ponctuation les plus souvent associés à un texte généré. Remplacer une partie de ces incises par des phrases séparées, des parenthèses, ou des notes de bas de page.

- [ ] ⚪ **Casser la symétrie des triades rhétoriques** `Programme`
  Des groupes de trois membres parallèles reviennent régulièrement (« Il est illisible. Il est inégal. Il n'est pas piloté. »). Élégant isolément, répétitif à l'échelle du site. Casser le motif par endroits avec deux points, ou quatre, ou une liste asymétrique.

- [ ] ⚪ **Ajouter une voix incarnée** `Programme`
  Aucun « nous avons choisi », aucun nom, aucune note personnelle sur pourquoi ce site existe : tout reste à la troisième personne impersonnelle. Une courte note signée — qui, pourquoi ce projet, quelles réserves — sur Programme ou dans une page « À propos » ferait contrepoint humain à la rigueur méthodologique.

> **Constat (pas une action) :** le design visuel — thème sombre sobre, sans dégradé ni icône générique — n'a pas la « touche IA » habituelle des sites générés. Le travail porte sur le texte, pas sur l'interface.

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

---

## Journal

- **Septembre 2026.** Fichier créé à l'issue d'une relecture du dépôt après
  les tranches B1 à B5d de la campagne sur les régimes. Aucune action
  commencée.
- **Septembre 2026, action 1.** Faite. Deux sources certifiées de plus (EACR,
  EIR), les cas types pondérés par les effectifs de leur caisse, la garantie
  vieillesse chiffrée sur la distribution des pensions. Le détail de ce qu'elle
  a déplacé est sous l'action. Elle a ouvert l'action 8, qui est le défaut
  qu'elle a rendu visible : l'âge de liquidation des cas types ne suit pas leur
  génération.
- **Septembre 2026, action 2.** Faite. Six régimes spéciaux quittent la ligne
  « rien / tout » de la part patronale, 163 valeurs certifiées, une source
  nouvelle qui lit l'index DILA au lieu des dumps. Le détail est sous l'action.
  Deux choses à en retenir pour la suite : les sources que l'action annonçait
  n'ont pas servi — tout était au Journal officiel —, et l'index rend une
  lecture de texte assez bon marché pour qu'on la tente avant de conclure
  qu'une série n'existe pas. L'action 3, qui porte sur les taux de cotisation,
  est la plus haute qui ne soit pas commencée, et c'est le même outil qui
  l'attend.
- **Septembre 2026, action 3.** Faite, mais moins largement que l'action ne
  l'annonçait : 368 valeurs certifiées sur le régime général depuis 1982 et les
  salariés agricoles depuis 1980, et rien avant, parce que la base LEGI ne garde
  de l'article d'avant 1982 qu'une version de quatorze ans. Le détail est sous
  l'action. Trois choses à en retenir pour la suite. Une règle écrite dans la
  documentation n'est pas une règle appliquée : celle du 1er janvier ne l'était
  pas, et une fiche s'était alignée sur le défaut plutôt que sur la règle — ce
  qui est un mode de panne à chercher ailleurs. Un article codifié ne porte pas
  toujours le droit en vigueur, et il faut donc un garde-fou qui interroge le
  JORF sur ce que la chaîne des versions ne montre pas. Enfin, un renvoi d'un
  article à un autre est une information : c'est lui qui datait l'alignement des
  salariés agricoles sur le régime général, que le dépôt supposait éternel.
  L'action 4, la contre-expertise du scénario 1, est la plus haute qui ne soit
  pas commencée.
- **Septembre 2026, action 3, seconde passe.** Les deux réserves de la première
  ont été reprises. Aucune des deux ne se referme par une certification — les
  sources n'existent pas —, mais les deux cessent d'être des aveux : une source
  nouvelle ancre chaque marche des séries transcrites au décret qui la porte, et
  démontre, par la source amont elle-même, que les taux des complémentaires ne
  sont dans aucun texte officiel. La leçon à retenir est celle-là : quand une
  série ne se certifie pas, il reste à dire de quoi elle est faite, et la
  DATE d'une marche se vérifie même quand sa valeur ne se vérifie pas. La
  recherche a rapporté au passage ce que personne ne cherchait — un décret de
  1979 qui rend fausses deux années de la série.
- **Septembre 2026, action 4.** Faite. Deux oracles nouveaux — l'Agirc des
  cadres et l'Ircantec des agents non titulaires —, un troisième qui n'a
  demandé aucun code, vingt tests de plus et cinq écarts trouvés, trois chez
  nous. Le détail est sous l'action. Quatre choses à en retenir pour la suite.
  Le périmètre d'OpenFisca-France-Pension est ATTEINT : il n'expose que cinq
  régimes, ils y sont tous, et son Agirc-Arrco unifié reste cassé — la prochaine
  contre-expertise, quelle qu'elle soit, ne viendra pas de lui. Un régime que
  la loi déclare ALIGNÉ n'a pas besoin de son propre oracle : la MSA, l'artisan
  et le commerçant se confrontent à celui du régime général, et c'est
  l'alignement lui-même qu'on met alors à l'épreuve — la MSA le passe, l'artisan
  non. Une donnée MANQUANTE n'est pas une donnée nulle : l'écart le plus
  instructif de cette campagne n'est pas un chiffre faux mais un `null` lu comme
  une tranche absente. Et une correction qui ne déplace aucun témoin n'est pas
  une correction inutile : les deux règles de l'Ircantec corrigées ici ne
  changent aucun chiffre publié, parce qu'aucun cas type n'est dans la situation
  qu'elles gouvernent ; elles changent ce que le simulateur servira à qui l'est.
  Les actions 9 et 10 sont ouvertes par ce qu'elle a rendu visible. L'action 5,
  la catégorie active et les militaires, est la plus haute qui ne soit pas
  commencée.
- **Septembre 2026, action 5.** Faite. Sept statuts de plus, trois tables de
  législation lues dans les textes, un cas type militaire, quatorze tests, et
  aucun des 427 témoins existants déplacé. Le détail est sous l'action. Quatre
  choses à en retenir pour la suite. Un paramètre qui ne se déduit d'aucune
  donnée de carrière n'est pas pour autant hors du modèle : il peut se
  DÉCLARER, et `sans_employeur` avait déjà ouvert cette voie — c'est la forme
  que prendra tout ce qui dépend d'un corps, d'un grade ou d'un emploi. Une
  limite écrite dans `limites.md` peut être vraie et trompeuse à la fois :
  « l'écart de pension reste nul » l'était au seul âge anticipé, et cachait
  20 % d'écart à soixante ans, parce que le plafond de vingt trimestres masquait
  l'âge d'annulation. Une règle dérogatoire en appelle d'autres, en sens
  inverse : ouvrir la pension militaire à trente-cinq ans obligeait à lui
  retirer la surcote et à lui donner sa décote propre, faute de quoi le résultat
  aurait été absurde. Enfin, toutes les tables du droit ne s'indexent pas sur la
  génération : celle des durées militaires se lit à l'année où l'ancienne durée
  est atteinte, et le supposer aurait valu un an et demi d'erreur. L'action 6,
  le solde plutôt que le coût, est la plus haute qui ne soit pas commencée.
- **Septembre 2026, action 6.** Faite. Une source de plus — les classeurs de
  données du rapport annuel du COR —, 270 valeurs, deux fichiers de référence,
  une section de la page Coût, vingt-cinq tests, et aucun chiffre existant
  déplacé. Le détail est sous l'action. Quatre choses à en retenir pour la
  suite. **La source qu'une action annonce n'a pas été vérifiée du seul fait
  qu'elle a été nommée** : celle-ci n'existe pas, les Comptes de la protection
  sociale ne ventilant pas leurs ressources par risque, et l'action n'a
  commencé qu'une fois ce constat fait. Quand on change de compte, **on en
  prend toutes les colonnes** : prendre les ressources du COR et les retrancher
  de la dépense DREES aurait fabriqué un solde en soustrayant deux périmètres,
  alors qu'en prenant aussi sa dépense, le solde du scénario 1 redonne
  exactement le solde publié — et le voisinage des deux périmètres devient un
  contrôle au lieu d'être un risque. **Une grandeur nouvelle peut renverser la
  lecture des anciennes sans en changer un chiffre** : le coefficient
  d'équilibre ne déplace aucune courbe de coût, et il interdit pourtant de lire
  celles des scénarios prospectifs comme des économies. Enfin, **un chiffre
  dont on connaît la marge se publie avec sa marge** : l'année du retour à
  l'équilibre est du même ordre de grandeur que l'artefact du pas de la grille,
  et le dire valait mieux que de l'arrondir ou de la taire. L'action 7, la
  saisie d'un relevé de carrière réel, est la plus haute qui ne soit pas
  commencée ; elle ouvre aussi, à côté d'elle, un chantier que celle-ci laisse :
  APPLIQUER le coefficient d'équilibre, qui touche les deux moteurs.
- **Septembre 2026, action 7.** Faite. Un paramètre de plus, un constructeur de
  carrière de chaque côté du portage, onze témoins ajoutés, dix-huit tests, et
  aucune des 469 simulations témoins déplacée. Le détail est sous l'action.
  Trois choses à en retenir pour la suite. **Une action qui n'ajoute aucune
  donnée peut quand même se vérifier par les témoins** : le seul fait que ces
  469 valeurs figées n'aient pas bougé prouve que l'extraction de
  `_ligne_annuelle` n'a rien changé au chemin existant, et c'est le contrôle qui
  manquerait à une réécriture faite sans eux. **Un chemin neuf hérite des fautes déjà commises
  sur l'ancien** : la plage d'interruption sans borne avait appris que l'adresse
  EST la saisie, et le relevé a reçu son garde-fou — le comptage avant la
  lecture — le jour où il a été écrit, plutôt qu'après un incident. Enfin,
  **une limite qui tombe en déplace une autre d'un cran** : le modèle ne
  reconstitue plus le revenu de qui saisit son relevé, mais il ignore toujours
  le MOIS d'entrée dans la vie active, que nul relevé ne porte — c'est là que
  `limites.md` §5 se tient désormais. L'action 8, faire liquider chaque cas
  type à l'âge de SA génération, est la plus haute qui ne soit pas commencée.
- **Septembre 2026, action 8.** Faite, et elle a démenti sa propre hypothèse :
  l'écart avec le COR en 2070 se creuse au lieu de se refermer, de 18,3 à 19,3 %
  du PIB. Le détail est sous l'action. Trois choses à en retenir pour la suite.
  **Une action dont le contrôle échoue n'a pas échoué** : la feuille de route
  demandait de « regarder si la trajectoire 2070 revient vers le COR » — elle
  n'y revient pas, et savoir que l'âge de départ n'est pas la cause vaut mieux
  que de continuer à le croire. **Une marche peut être fausse dans le détail
  sans l'être dans le principe** : l'action prescrivait de liquider à l'âge
  d'OUVERTURE, et c'est la mesure qui a montré qu'il fallait liquider au TAUX
  PLEIN — un assuré qui part avec huit trimestres de décote n'existe pas, et la
  variante « ouverture » éloignait le résultat d'un point de plus. Enfin,
  **corriger un défaut en révèle un autre qu'il masquait** : la garantie
  vieillesse du scénario 6 était sous-estimée d'un facteur quarante parce que
  les cas types partaient trop tôt pour la voir ; elle ne l'est plus que d'un
  facteur deux, et ce qui reste ne vient plus d'un âge mais de la nature d'une
  grille. Reste, pour la suite, la piste que `limites.md` §5 ter ouvre sur
  l'écart avec le COR : le taux de remplacement du modèle ne recule pas, celui
  du COR recule ; c'est là qu'il faut chercher, et non dans les âges. L'action 9,
  la surcote de l'Ircantec, est la plus haute qui ne soit pas commencée.
- **Septembre 2026, action 12.** Faite. L'accueil du site est désormais le
  programme du Parti libéral français, le simulateur vit sous `#/simuler`, et
  les pages ont perdu près de mille mots de commentaire. Le détail est sous
  l'action. Deux choses à en retenir pour la suite. **Un dépôt finit par écrire
  son propre journal dans ses pages** : la moitié de ce qui a été retiré
  racontait ce que le modèle avait cru avant de se corriger — c'est une chose
  qui a sa place dans `limites.md` et dans ce fichier, pas devant un lecteur qui
  vient lire une proposition. Et **une page d'accueil qui calcule est une page
  d'accueil lente** : celle-ci lit le catalogue des régimes, la dépense et le
  solde, jamais `cout()` ni une simulation, et s'affiche donc sans attente.
  L'action 9, la surcote de l'Ircantec, reste la plus haute qui ne soit pas
  commencée.
- **Septembre 2026, hors action.** Dépouillement de quatre travaux publiés sur
  les comptes notionnels — CNAV/PRISME 2009, 7e rapport du COR de janvier 2010
  et la séance du 5 juillet 2017 qui y revient, Lettre du CEPII n° 297. Ils
  entrent au manifeste en `controle`, statut qui n'avait encore jamais servi :
  aucun n'apporte un chiffre à `data/reference/`, tous en contrôlent un. Et
  `limites.md` gagne un §5 quater qui répond à l'objection que ces travaux
  fondent — la CNAV trouve −7 %, ce dépôt trouve −73 % — en décomposant l'écart
  en quatre choix déjà chiffrés par le modèle lui-même. Trois choses à en
  retenir. **La rétroactivité pèse la moitié de l'écart** : les scénarios 3 et 5
  figent les droits acquis comme le fait toute la littérature, et l'écart tombe
  de −73,1 % à −37,4 %. **Le CEPII recontrôle une valeur certifiée du dépôt**
  sans le savoir : sa part patronale implicite de l'État en 2008, 55,7 %, est le
  0,5571 de `contribution_employeur_public.csv`. Et **les fiches que l'action 11
  cherchait existent** : la maquette du SG-COR et les descriptions des
  mécanismes suédois et italien sont attachées à la séance de 2017, référencées
  sous `cor_retour_septieme_rapport`. L'action 9, la surcote de l'Ircantec,
  reste la plus haute qui ne soit pas commencée.
- **Septembre 2026, hors action (suite).** La vérification du rendu de la page
  Données, après l'entrée des quatre travaux au manifeste, a ouvert l'action 13.
  Elle n'était pas cherchée : la phrase contrôlée était celle des institutions
  recensées, et c'est le bandeau au-dessus qui s'est révélé plus affirmatif que
  ses données. **Un horodatage global sur un fichier qui se complète par
  morceaux ment dès le premier passage partiel**, et le dépôt avait les deux
  dispositions écrites côte à côte sans voir qu'elles se contredisaient. La
  leçon vaut au-delà de ce fichier : ce qui n'est pas daté à la granularité où
  il est produit finit par emprunter la date du dernier venu.
- **Septembre 2026, hors action (suite).** Lecture d'un travail proposé de
  l'extérieur : Catherine, Miller et Sarin, *Social Security and Trends in
  Wealth Inequality* (*Journal of Finance*, juin 2025). Rien à en tirer côté
  données — il est américain et travaille sur la *Survey of Consumer Finances* —
  et son résultat de tête ne se transporte pas, la Social Security tenant sa
  progressivité d'une formule qu'un compte notionnel n'a pas. Mais une de ses
  précautions a ouvert l'action 14 : il valorise les droits à retraite avec une
  mortalité par revenu, là où le diviseur d'ici ignore que cet axe existe. **Le
  dépôt avait chiffré l'écart de longévité entre les sexes et oublié celui entre
  les niveaux de vie**, qui est le plus grand des deux et le seul qui ne résulte
  d'aucun choix. L'action est notée, pas menée : rien du modèle n'a bougé, et la
  leçon vaut au-delà d'elle — une lecture extérieure trouve les angles morts que
  le dépôt ne peut pas voir, puisqu'il ne cherche que là où il a déjà regardé.
  L'action 9, la surcote de l'Ircantec, reste la plus haute qui ne soit pas
  commencée.
- **Septembre 2026, action 15 notée.** Une consigne demande de tenir la liste
  des procédés d'ergonomie à employer quand une page s'allonge : elle est
  entière sous l'action 15, avec ce que le dépôt en fait déjà. Rien n'a bougé
  du site. Deux choses relevées en la classant. **Le dépôt a les outils et pas
  l'usage** : `donnees_du_graphique` rend déjà en tableau ce que le graphique
  montre en courbes, onze `<details>` replient déjà du détail — les procédés
  existent, mais posés une fois, jamais généralisés ; et la page Coût aligne
  huit mille mots sous trois titres de second niveau. **Et l'adresse est la
  route**, ce qui interdit le sommaire ancré tel qu'on l'écrit partout
  ailleurs : la place du `#` est prise par la navigation, et toute ancre doit
  passer par l'écouteur délégué qui sert déjà le lien d'évitement. Ce point
  vaut d'être connu avant de commencer, pas découvert au premier clic.
  L'action 9, la surcote de l'Ircantec, reste la plus haute qui ne soit pas
  commencée.
- **Septembre 2026, action 16.** Faite. La page Coût est refaite : les
  ressources ouvrent la page à égalité avec les dépenses, leur ventilation est
  tracée dans le temps, et ce qu'on traverse avant d'avoir une réponse passe de
  5 652 mots, sept graphiques et neuf tableaux à 953 mots, quatre graphiques et
  aucun tableau — sans qu'aucun chiffre ni aucune réserve ne soit retiré. Le
  détail est sous l'action ; l'action 15, dont elle est la première application,
  passe en cours. Trois choses à en retenir. **Une page trop longue cache ses
  propres démentis** : un graphique y portait le niveau du modèle plutôt qu'un
  rapport, et la phrase qui le commentait affirmait le contraire des chiffres
  au-dessus d'elle, depuis assez longtemps pour que personne ne s'en souvienne.
  **Le sommaire ancré n'était pas nécessaire** : une pile de sections repliées
  en tient lieu, se parcourt du regard, et évite l'obstacle de l'adresse-route
  que l'action 15 signalait. Enfin, **le ruban peint entre deux courbes fait
  plus pour la lisibilité d'un solde que n'importe quelle légende** : c'est la
  seule brique de cette action qui mériterait d'être reprise ailleurs.
- **Septembre 2026, action 16, seconde passe.** Trois demandes, toutes tenues.
  Les graphiques qui traitaient du même sujet sur deux fenêtres sont regroupés :
  la page passe de quatre tracés ouverts à deux, et de 953 mots à 535. Les
  graphiques se lisent au survol, au doigt et aux flèches — la valeur de l'année
  vient du tableau de points que le tracé porte déjà, ce qui évite d'écrire deux
  fois les mêmes chiffres dans deux portages qui ne formatent pas les flottants
  pareil. Et chaque carte se télécharge en image signée `@pliberal`, composée
  dans le navigateur sans bibliothèque. Deux choses à en retenir. **Un tracé
  porte déjà sa propre description** : le tableau de points, écrit pour
  l'accessibilité, s'est trouvé être exactement la source de données dont
  l'interaction avait besoin — une contrainte tenue pour une raison en a servi
  une autre, sans rien ajouter. Et **l'axe et les chiffres n'ont pas la même
  précision** : un axe qui gradue de quatre en quatre se lit mieux en nombres
  ronds, mais l'écart entre deux courbes s'y perdait à l'arrondi, et il fallait
  séparer les deux réglages pour que la lecture au survol serve à quelque chose.
- **Septembre 2026, action 15.** Faite, sur les six pages. La forme mise au
  point sur la page Coût — ce qui répond à la question en tête, le reste dans
  des sections repliées — a été portée au Programme, aux Cas types, à la
  Méthode, aux Données et au formulaire de simulation. Le tableau des mots est
  sous l'action. Trois choses à en retenir. **Le catalogue était trop large de
  moitié** : six procédés sur vingt-cinq ont tout fait, et les deux familles
  qui semblaient les plus ambitieuses — le sommaire ancré, les filtres — se
  sont révélées inutiles une fois le détail rangé. **Une page de référence se
  replie comme une autre** : Données passe de 5 851 mots à 149 sans qu'une
  ligne disparaisse, et c'est la page où le gain est le plus net, parce que
  tout y était une pièce justificative et rien n'y était une réponse. Enfin,
  **une seule grille vaut mieux que cinq** : les Cas types en alignaient cinq
  de quatre-vingt-onze cellules, et personne ne compare cinq tableaux — celle
  qui reste est accompagnée des trois chiffres qui la résument, ce qu'aucune
  des cinq ne donnait.
- **Septembre 2026, action 17.** Faite. Le simulateur demandait cinq champs
  pour deux dates ; il en demande trois, et chaque date se prend au calendrier
  du navigateur. Rien n'a bougé dans les chiffres : la conversion d'une date en
  âge tient en une soustraction de mois, et elle a été écrite une fois de chaque
  côté du portage, là où les âges entraient déjà. Deux choses à en retenir. **Le
  champ le plus juste n'est pas toujours celui qu'on peut poser** : `type="month"`
  décrit exactement ce que le modèle sait lire, et deux navigateurs de bureau sur
  trois ne l'ouvrent pas — c'est `type="date"`, moins juste d'un jour inutile,
  qui donne un calendrier à tout le monde. Et **une simplification en ouvre une
  autre** : demander une date plutôt qu'un âge a donné au changement de métier
  la précision au mois qu'il n'avait jamais eue, sans un champ de plus.
- **Septembre 2026, action 18.** Faite, dans la foulée de la 17 et à la
  demande qui l'a suivie : « il faut aussi indiquer la date de fin d'activité ».
  Oui — et elle ne valait pas un champ de plus. Une ligne de carrière peut
  désormais n'être pas un emploi, et la dernière dit quand l'activité s'arrête.
  Deux choses à en retenir. **Le défaut le plus coûteux ne refuse rien** : le
  formulaire ne demandait pas quand on s'arrête, il supposait la réponse, et
  affichait un chiffre faux sans rien signaler — les refus, eux, se voient.
  Et **une liste de choix se paie en unicité** : ajouter les motifs au menu des
  statuts y a mis « sans activité » deux fois, sous deux libellés, pour le même
  résultat ; un test l'interdit maintenant à tous les menus du site.
- **Septembre 2026, action 19.** Faite, à la demande qui a suivi l'action 18 :
  « garde seulement le nécessaire et utilise des infobulles ». Le formulaire
  vierge passe de 424 mots visibles à 115, la page de résultats de 3 351 à
  1 484, et aucun chiffre ne bouge. Deux choses à en retenir. **Le tri se fait
  sur une règle, pas au jugé** : reste visible ce qui porte un chiffre — un
  montant, une date, une unité, un refus —, s'ouvre en bulle ce qui explique
  d'où ce chiffre vient. Et **un mécanisme déjà là valait mieux qu'un
  nouveau** : la bulle du glossaire, écrite pour les mots de jargon, tenait déjà
  l'accessibilité et le basculement délégué ; il n'a fallu qu'une autre ancre.
- **Septembre 2026, action 20.** Faite, à la demande : « je veux une
  bibliothèque de logos uniforme et propre ». C'est Lucide, recopié dans le
  dépôt plutôt qu'appelé à un CDN — le site ne charge rien chez personne, et le
  portage n'a toujours aucune dépendance. Deux choses à en retenir. **Un emoji
  n'est pas un dessin** : sa forme appartient au système qui l'affiche, et rien
  dans le dépôt ne peut la tenir. Et **une copie se surveille** : le tracé écrit
  dans le code n'est juste que tant qu'un test le confronte à son original, et
  qu'un second confronte les deux portages l'un à l'autre.
- **Septembre 2026, action 21.** Faite, à la demande : « réparer l'affichage
  des résultats sur mobile, et enlever beaucoup de texte à la suite des
  résultats — le site est destiné à quelqu'un qui ne connaît pas l'économie et
  qui veut surtout les résultats ». La page passe de 11 871 px à 4 085 px sur un
  écran de téléphone, et de 3 744 mots ouverts à 1 407, sans qu'un chiffre
  bouge. Deux choses à en retenir. **Un raccourci flex change de sens avec la
  direction** : `flex-basis` est une largeur en ligne et une hauteur en colonne,
  si bien qu'une règle juste dans la requête média du bureau creusait six trous
  d'un tiers d'écran dans celle du téléphone — un défaut qu'aucun test de HTML
  ne pouvait voir, et qu'il a fallu mesurer dans un navigateur. Et **une
  discipline ne vaut que sur la page qu'on ouvre vraiment** : le budget de
  lecture tenait les six pages, mais rendait « /simuler » sans paramètres,
  c'est-à-dire tout sauf la page que le visiteur vient voir.
- **Septembre 2026, action 21, seconde passe.** « J'ai toujours des soucis »,
  avec une capture d'écran : les deux montants d'un scénario débordaient de la
  carte, et la page défilait horizontalement. La leçon vaut pour tout ce qui
  suivra : **une page mesurée dans un navigateur de bureau réduit n'est pas une
  page mesurée sur un téléphone.** La police demandée n'y existe pas, le système
  grossit le texte sans que les requêtes média l'apprennent, et une largeur qui
  tient au point près chez soi déborde chez l'autre. Ce qui se replie ne déborde
  jamais ; ce qui est insécable doit être court, et rien d'autre.
- **Septembre 2026, action 9.** Faite. L'Ircantec sert la surcote de l'arrêté
  du 30 décembre 1970 à ses deux taux ; le coefficient d'un régime en points,
  qui ne pouvait pas dépasser un, le peut. Deux cas types bougent, de 1,1 % sur
  la pension totale, et rien d'autre dans le dépôt. Le détail est sous
  l'action. Trois choses à en retenir. **Une version de texte n'est pas une
  date d'effet** : le paragraphe qui crée la surcote vit dans la version du
  25 septembre 2008 et ne s'applique qu'au 1er janvier 2010, si bien que la
  coupure de fiche qu'il faut est une date que `calendrier_regimes.py` ne sait
  pas réclamer — il compare les débuts de version, pas ce qu'elles disent
  d'elles-mêmes. **Deux sources peuvent être fausses de deux façons
  opposées** : OpenFisca servait dix fois trop, le dépôt ne servait rien, et
  lire le texte était le seul moyen de ne pas choisir entre les deux. Enfin, la vérification
  que l'action demandait « au passage » a trouvé un défaut plus large qu'elle —
  neuf régimes en points dont la surcote, pourtant sourcée et chargée, n'est
  lue par aucune branche du moteur — et c'est l'action 22, ouverte plutôt que
  glissée dans celle-ci.
- **Septembre 2026, action 23.** Ouverte. Une revue extérieure des six pages,
  datée du 15 septembre et reçue le 16, est versée entière sous l'action 23 :
  vingt-sept chantiers en quatre thèmes, chacun avec sa case à cocher et la
  priorité que le relecteur lui donne. Deux sont cochés d'emblée : les deux
  chantiers de licence, réglés le 16 septembre par le passage du code sous
  Apache 2.0 et des textes sous CC BY-SA 4.0, les données restant sous les
  conditions de leurs producteurs. Deux autres recoupent des travaux déjà
  faits — la bulle du glossaire de l'action 19, la grille unique de l'action
  16 — et l'action dit pour chacun ce qu'il faut vérifier avant de le reprendre.
