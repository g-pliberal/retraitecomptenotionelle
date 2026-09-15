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

### 9. La surcote de l'Ircantec, qu'aucun assuré ne touche — `à faire`

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
dans ses fiches ; `hypotheses_projection.yaml` est déjà la trace d'un emprunt de
cette nature.

**Fichiers.** `src/retraite_notionnelle/cout.py` (la trajectoire et le solde) ;
`src/retraite_notionnelle/scenarios/` si l'ajustement doit porter sur la pension
individuelle et non seulement sur l'agrégat ; `moteur/js/` en regard ; les
témoins ; `limites.md` §5.

**Marche.** D'abord au seul niveau de l'AGRÉGAT — une variante de la page Coût
où chaque système est ramené à l'équilibre —, ce qui ne touche pas les moteurs
de pension et se mesure aussitôt. Ensuite seulement, si l'écart le justifie,
l'ajustement porté à la pension individuelle, qui les touche tous les deux. Le
piège à nommer d'avance : un facteur commun ne déplace AUCUN écart entre
carrières, si bien qu'appliquer le coefficient ne change rien à ce que le site
mesure page par page — et change tout à ce que la page Coût affiche.

**Fin.** La page Coût porte les deux lectures — système piloté, système non
piloté — et dit laquelle répond à quelle question.

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
