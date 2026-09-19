# Feuille de route — les actions qui font le plus progresser le modèle

Ce fichier est la liste des chantiers à mener, classés par ce qu'ils déplacent
dans les résultats du dépôt. Il sert de point d'entrée à une session de travail :
prendre l'action la plus haute qui n'est pas commencée, la mener au bout, puis
mettre à jour ce fichier. Il ne remplace ni `limites.md`, qui dit ce que vaut
chaque chiffre, ni `regimes.md`, journal de la campagne sur les régimes.

**Comment le tenir.** Une action a un état — `à faire`, `en cours`, `fait` — et
une ligne « ce que ça a déplacé » quand elle est faite, comme les tranches de
`regimes.md`. Toute session qui touche au scénario 1 commence par
`python scripts/veille_droit.py` et finit par une entrée au journal de
`data/reference/legislation/veille.yaml` : voir `docs/veille_droit.md`. Une action qu'on abandonne ne disparaît pas : elle passe en bas,
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
  téléchargeaient 1,1 à 2,8 Go et mettaient d'un quart d'heure à une heure —
  jusqu'au 17 septembre 2026, où tous sont passés à l'index ; celui-ci
  lisait l'index publié le premier, en quelques secondes, et il y trouvait **plus** : le dump
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
  3,9 de l'assurance chômage en 2024, 3,7 % des ressources. Le coefficient la
  RETIRE désormais aux cinq scénarios notionnels : année par année de 2013 à
  2024, à part constante des ressources avant et sur tout l'horizon projeté.
  Le scénario 3 en 2070 passe de 1,94 à 1,87, le 5 de 1,17 à 1,13, et les
  deux sont en déficit dès 2025, où ils servent encore les pensions du système
  actuel ; le système actuel encaisse tout et garde le solde du COR. Le solde
  annuel porte un `retrait`, et `ressources_de(scenario)` dit ce que chaque
  système peut compter. Deux choses que le
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
- *Ce qu'elle ne savait pas faire, et qu'elle sait depuis le 17 septembre
  2026.* Elle ne connaissait ni la carrière longue — le moteur savait la
  calculer, mais comme une dérogation qu'on demande, non comme un âge qu'on
  propose — ni les trimestres pour enfants, que `calculer` ajoute à la durée et
  qu'elle ne comptait pas : voir le Journal à cette date. Les âges d'ENTRÉE des
  cas types restent ceux de la grille — vingt-quatre ans pour l'artisan, vingt-sept pour le
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

### 10. Liquider ensemble un régime et celui qui lui succède — `fait`

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

**Ce que ça a déplacé.**
- *Le regroupement, et sa règle de date.* Avant de liquider, le moteur suit
  `integre_dans` de chaque régime d'annuités que la carrière a traversé, tant
  que la chaîne reste en annuités, et groupe ce qui aboutit au même bout :
  un seul salaire de référence sur les années de tous les membres, une seule
  proratisation, une seule ligne, sous le nom de la caisse de la dernière
  période active — celle qui aurait le dossier —, dont la fiche donne les
  règles, et la ligne dit la succession (« 3 caisses liquidées ensemble »).
  La chaîne ne se suit qu'à partir de l'année où le régime absorbé FERME à
  ses affiliés : avant 2018, le régime général et le RSI sont deux régimes,
  et un salarié devenu artisan qui liquide en 2010 garde deux pensions ;
  en 2020 il n'en a qu'une. Les régimes en points n'entrent dans aucun
  groupe. Le découpage d'avant reste une variante
  (`calculer(..., liquider_successions=False)`), qu'un test garde mesurée.
  Les deux moteurs sont touchés, et les témoins.
- *L'oracle.* Sur les dix profils, l'artisan et le commerçant rendent
  maintenant EXACTEMENT la pension du régime général, comme la MSA — vingt
  cas à 10⁻⁹ près —, et donc celle d'OpenFisca à la tolérance près. La
  variante coupée retrouve les −7,2 % à +0,3 % d'avant.
- *Les cas types du site, bien plus que l'oracle ne le laissait voir.* Les
  profils de l'oracle sont à salaire constant ; ceux du site montent avec
  l'âge, et c'est là que la césure coûtait : chaque morceau de moins de
  vingt-cinq ans liquidait sur la moyenne de TOUTES ses années, quand la
  carrière entière liquide sur ses vingt-cinq meilleures, qui sont les
  dernières. Artisan, commerçant, micro-entrepreneur et gérant de débit de
  tabac des générations 1955 et 1965 : de +8 % à +17 % de pension actuelle ;
  génération 1945, qui ne traverse qu'une succession sur ses dernières
  années : +1 % à +1,6 % ; les carrières mixtes privé puis indépendant :
  +2,5 % à +5 %, et +16 % pour « creux en milieu de carrière », dont les
  années d'indépendant, mieux payées, entrent maintenant dans les
  vingt-cinq meilleures. Le modèle sous-estimait les pensions des
  indépendants d'un ordre de grandeur que rien n'avait mesuré, faute d'un
  oracle à salaire croissant.
- *L'autre chaîne : la fonction publique de 1948.* Le fonctionnaire de la
  génération 1925, entré sous la loi de 1853, empilait « 10 345 € × 60 % ×
  8/120 » SUR une pension civile déjà à 150/150 : la pension dépassait les
  75 % que le code plafonne. Groupé, il rend 16 467 € au lieu de 16 881,
  soit −2,45 %, et c'est la correction d'un cumul que le droit n'a jamais
  permis. Cinq cas types 1925 — État, actif, super-actif, militaire,
  officier — bougent d'autant.
- *La liquidation unique, de fait, pour la chaîne du régime général.* Depuis
  2018, un salarié devenu artisan liquide chez nous une seule pension sur
  ses meilleures années tous régimes confondus : c'est ce que fait la LURA
  depuis juillet 2017 pour les générations 1953 et suivantes, et ce que
  l'absorption du RSI produit de toute façon. Restent hors du modèle la
  LURA entre le régime général et la MSA des salariés, qui sont deux
  régimes distincts sans lien d'absorption, et la proratisation croisée
  d'avant elle ; et pour les générations d'avant 1953, que la LURA ne
  couvre pas, la caisse calcule encore deux pensions coordonnées là où le
  modèle n'en calcule qu'une.
- *La page Coût.* La courbe « ce qui sortirait en comptes notionnels dès
  2026 » baisse de 0,1 point de PIB sur neuf des années 2044-2067 : la
  pension actuelle des indépendants monte, le rapport notionnel/actuel de
  leurs cas types baisse d'autant.

### 11. Appliquer le coefficient d'équilibre — `à faire`

**Pourquoi.** Ouverte par l'action 6, qui s'arrête juste avant. Le coefficient
d'équilibre de chaque système est désormais CALCULÉ, année par année, de 2002 à
2070 ; il n'est pas APPLIQUÉ. Un système notionnel réel ne laisse pas dormir un
excédent : il relève les pensions jusqu'à l'équilibre, ou les abaisse, par un
facteur commun à toutes les pensions de l'année et un fonds de réserve qui
lisse. Tant que ce facteur n'est pas appliqué, les courbes de la page Coût sont
celles d'un système qui ne se pilote pas, et le coefficient de 1,87 du
scénario 3 en 2070 se lit trop facilement comme une économie de 46 %.

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

**Marche.** Le premier pas est fait : les ressources des scénarios notionnels
sont diminuées de ce que la branche famille et l'assurance chômage versent pour
des droits qu'ils ne servent pas (action 6, seconde passe). Ensuite au seul
niveau de l'AGRÉGAT — une variante de la page Coût où chaque système est ramené à
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

### 13. Dater la certification série par série — `fait`

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

**Ce que ça a déplacé.** *Aucun chiffre*, et une affirmation. Fait le
17 septembre 2026.

- *Une date dans chaque fiche.* `confronter` écrit `verifiee_le` dans la
  trace de chaque série, à chaque passage, que les valeurs bougent ou non ;
  c'est ce qui rend l'absence de diff lisible. Le champ global est renommé
  `dernier_passage_le`, pour ce qu'il est : la date du dernier `--appliquer`,
  fût-il partiel. Un test refuse une fiche sans date, et une date de fiche
  postérieure au dernier passage.
- *La page dit le minimum.* « La vérification la plus ancienne remonte au
  13 septembre 2026, la plus récente au 16 septembre 2026 », au lieu de
  « recontrôlé le 16 septembre » ; la fiche d'ouverture dit la plus ancienne,
  et la table des séries gagne une colonne « Vérifiée le », triable comme les
  autres. Un test vérifie que les deux dates sont le minimum et le maximum du
  journal, et que la date du dernier passage n'est plus présentée comme celle
  de tout.
- *Les dates d'avant sont rétablies depuis l'historique.* Aucune source n'a
  été retéléchargée : les fiches existantes sont datées du dernier commit où
  chacune a changé — 60 au 13 septembre, 7 au 14, 9 au 15, 4 au 16 —, ce qui
  est une borne basse, dite comme telle dans `limites.md` §6. Le prochain
  passage des récupérateurs les remplacera par des dates vraies.
- *Le bruit de diff redouté n'a pas lieu.* Le journal se complète : un passage
  ne réécrit que les fiches des séries qu'il a atteintes, et le diff montre
  exactement lesquelles — c'est même devenu sa vertu.

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

### 22. La surcote que les régimes en points écrivent et que le moteur laisse tomber — `fait`

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

**Ce que ça a déplacé.** Fait le 17 septembre 2026, sur les textes et non sur
le texte de cette action — qui se trompait sur un point : les sept
complémentaires de sections portaient bien une durée requise, celle du régime
de base copiée dans la fiche, et c'est elle qu'il a fallu retirer là où les
statuts n'en connaissent aucune.

- *Trois barèmes au lieu d'un.* `surcote_points` prend quatre valeurs.
  `regime_general` compte, comme la branche en annuités, les trimestres cotisés
  au-delà de l'âge légal et de la durée requise : c'est la CNAVPL (R. 643-8,
  LEGIARTI000006751834 — 0,75 % ; puis LEGIARTI000047985850, 1,25 % pour les
  trimestres accomplis à compter du 1er septembre 2023, que la fiche applique
  aux liquidations de 2024) et la MSA des non-salariés (D. 732-42, dont
  l'escalier de 3, 4 et 5 % d'avant 2009 est ramené à 0,75 % comme au régime
  général). `par_age_seul` compte les trimestres civils ENTIERS écoulés depuis
  un âge, sans durée ni cotisation, bornés par un âge maximal, un nombre de
  trimestres, un pas (« par année pleine ») et un palier de taux, sous
  condition d'une durée d'affiliation au régime : c'est la forme des sept
  statuts de sections. `ircantec` ne change pas.
- *Sept statuts lus dans l'index LEGI et JORF*, tous approuvés par arrêté, et
  chacun date sa règle. CARMF (arrêté du 30 novembre 2016, retraite en temps
  choisi depuis 2017) : 1,25 % par trimestre dès 62 ans, 0,75 % après 65,
  rien après 70 ; avant 2017, taux plein à 65 ans, anticipation abattue de
  1,25 % par trimestre à l'âge seul, différé majoré « de 5 % par année
  pleine ». ASV (arrêté du 1er décembre 2016) : les mêmes mots, et rien
  d'attesté avant. CAVEC (arrêtés du 22 février 2008, du 20 août 2018 et du
  10 juillet 2026) : taux plein à 65 ans sans durée, 1,25 % par trimestre
  plein dans la limite de 25 %, ramené à 0,75 % et 15 % de 2019 à 2025.
  CARPIMKO (arrêté du 31 juillet 2015) : 1,25 % par trimestre civil entier
  après l'âge du taux plein, vingt au plus — la fiche portait 0,75 %, le taux
  du régime de base. CAVP (arrêté du 23 juin 2011) : 0,5 % par trimestre
  jusqu'à l'âge du taux plein augmenté de trois ans. CPRN (arrêtés du
  16 décembre 2013 et du 29 novembre 2023) : 0,5 % jusqu'à 70 ans, puis 1 %
  jusqu'à la fin d'activité depuis 2024 — la fiche portait 1 % depuis 1949.
  CIPAV (fiche pratique 2022, seul texte trouvé) : 5 % par année pleine
  depuis l'âge du taux plein, à qui a trente ans de caisse.
- *Ce que les fiches ne servent plus.* Rien avant le texte qui date la règle :
  la CARMF avant 2000, l'ASV avant 2017, la CAVEC avant 2008, la CIPAV avant
  2013, la CARPIMKO avant 2016, la CAVP avant 2012, la CPRN avant 2014 — leur
  `surcote_par_trimestre` est nul, et la note de la période dit pourquoi.
- *Les témoins.* 26 cas sur 484 bougent, tous libéraux ou exploitants
  agricoles, sur 530 cellules ; par régime, la CNAVPL sur 22 lignes, la CARMF
  et l'ASV sur 3, la MSA sur 2. Les plus grands écarts sur le scénario
  actuel : l'exploitant agricole né en 1945, 11 078 → 12 671 € (+14,4 %),
  celui de 1955 +9,2 %, le médecin de 1955 +8,7 %, l'officier ministériel de
  1945 +9,0 %. Les cinq autres complémentaires ne déplacent aucun témoin :
  aucun profil témoin ne liquide au-delà de leur âge de départ du compte.
  Python et JavaScript rendent les mêmes chiffres, au bit près.
- *Deux tests de plus qui gardent la porte.* Le garde-fou annoncé — une
  période en points qui porte un taux porte un barème, et réciproquement — et
  un test par régime qui refait, à la main, le décompte de son texte. Neuf
  entrées au calendrier des réformes datent les coupures ; R. 643-8 rejoint
  les pivots de la CNAVPL.
- *Ce qui reste hors des fiches, et se lit dans leurs notes.* La CIPAV ne
  majore que les points des trente premières années, que rien ne distingue
  ici ; la CAVP borne les générations 1951 à 1955 à un ou deux ans ; la
  CARPIMKO monte de 65 à 67 ans sur les générations 1956 à 1961 quand la
  table du régime général le fait sur 1951 à 1955 ; la CARMF a compté depuis
  64 ans entre septembre 2023 et 2025 ; les règlements de juillet 2026 valent
  ici pour l'année entière.

---

### 23. La revue extérieure du 15 septembre 2026 : vingt-sept chantiers sur le site — `fait`

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

**Ce que ça a déplacé.** Les vingt-sept cases sont cochées, en quatre passes
les 16 et 17 septembre 2026, une par thème, chacune avec sa ligne au Journal ;
aucune n'a été barrée. *Aucun chiffre du modèle n'a bougé* : les témoins de
simulation sont identiques au bit près d'un bout à l'autre, et seuls les
témoins de page ont changé. Ce qui a changé est ce qu'un visiteur voit : un
glossaire, un menu groupé, des onglets, des tables qui se filtrent, un plan de
page, une navigation en trois groupes, une clé de lecture avant les chiffres,
des badges, une note signée, et une prose sans ses tics — le tout tenu par
une trentaine de tests nouveaux, dont ceux qui plafonnent les incises et
interdisent le retour du procédé. Une seule question a été renvoyée au modèle
plutôt que tranchée ici : le défaut de conversion des droits acquis, mesuré et
versé à l'action 24.

---

#### 1. Expérience utilisateur

*Le design visuel est déjà sobre et cohérent (thème sombre, pas de fioritures) ; les frictions viennent surtout de la densité du contenu et de l'absence d'outils pour la traverser.*

- [x] 🔴 **Des bulles de définition sur le vocabulaire technique** `Simuler · Global`
  Le simulateur est le point d'entrée le plus concret du site — celui où « le commun des mortels » vient voir sa propre pension, pas seulement un lecteur déjà averti. Il concentre pourtant du jargon non défini : « compte notionnel », « trimestres » / « durée d'assurance », « décote » / « surcote », « salaire de référence », « table de mortalité unisexe », « taux de remplacement », « assiette déplafonnée », « statut d'affiliation ». Souligner ces termes en pointillé et afficher, au clic ou au survol, une définition d'une ou deux phrases en langage courant — sans jargon économique, sans renvoi obligé vers Méthode. Un seul petit composant de bulle, réutilisé partout où le terme reparaît (Programme, Cas types, Coût), évite d'avoir à choisir entre simplifier le texte et perdre la précision : la précision reste dans la bulle, la phrase principale reste lisible.
  *Fait le 16 septembre 2026.* Le site a désormais un GLOSSAIRE, écrit une
  fois dans `gabarit.py` (vingt entrées) et recopié dans le portage, où un
  test le compare entrée pour entrée. Chaque mot de la liste du relecteur y
  est, en une ou deux phrases sans jargon : compte notionnel, trimestres,
  durée d'assurance, décote, surcote, salaire de référence, table de
  conversion, taux de remplacement, assiette déplafonnée, statut
  d'affiliation, âge de référence — plus coefficient de conversion, capital
  notionnel, coefficient d'équilibre, part patronale, indexation, taux plein,
  garantie vieillesse, répartition, part du PIB. Le composant est celui de
  l'action 19 (`g.mot`), posé par `g.terme` : sur les résultats du simulateur
  (le taux de remplacement de chaque scénario, les fiches « coefficient de
  conversion », « capital notionnel » et « âge de référence »), sous un
  point d'interrogation dans le formulaire (statut, table, âge de référence,
  part de la cotisation, indexation), sur Programme (trimestres, décote,
  surcote, taux plein, les 25 meilleures années), Cas types (le réglage
  annuel), Coût et Méthode. « Répartition » se définissait en deux endroits
  avec deux textes : il n'y en a plus qu'un. Aucun chiffre qui bouge dans une
  définition — un test l'interdit —, sans quoi un plafond y dériverait.

- [x] 🔴 **Expliquer l'âge de référence, pas seulement l'afficher** `Simuler`
  Après calcul, les résultats ouvrent sur cinq pastilles chiffrées (43 années cotisées, 64 ans liquidation, **67 ans — âge de référence — départ 3 ans plus tôt**, 25,667 coefficient de conversion, 252 025 € capital notionnel) sans un mot sur ce que chacune change. L'âge de référence n'est pourtant pas cosmétique : sur l'exemple testé, le scénario 3 convertit les droits acquis au diviseur de 67 ans alors que la pension part à 64 — l'anticipation est payée une seconde fois, ce que la page reconnaît elle-même (« l'anticipation est donc payée une seconde fois, sur le passé »). Le réglage qui corrige ça (« Conversion des droits acquis » → « à l'âge de départ effectif », présenté comme ce qu'« une réforme réelle retiendrait ») est enterré dans les options repliées, en bas de formulaire, et n'est pas la valeur par défaut. Trois choses à faire : une bulle de définition sur « âge de référence » (voir le chantier ci-dessus) ; une phrase explicite dès que l'âge de départ saisi est inférieur à l'âge de référence, qui nomme la pénalité et pointe vers le réglage qui l'enlève ; et réexaminer si « à l'âge de départ effectif » ne devrait pas être le défaut plutôt qu'une option cachée.
  *Fait le 16 septembre 2026, aux deux tiers.* La fiche « âge de référence »
  est un mot du glossaire, et une NOTE en clair paraît sous les fiches dès
  que l'âge de départ s'en écarte : « Vous partez 3 ans avant l'âge de
  référence. Dans les scénarios 3 et 5, les droits acquis avant 2026 sont
  convertis en capital comme si vous partiez à 67 ans, puis servis à partir
  de 64 ans : l'anticipation est payée une seconde fois, sur le passé. Le
  réglage « Conversion des droits acquis : à l'âge de départ effectif », dans
  les options de modélisation du formulaire, retire cet écart. » Les deux
  sens sont écrits — un départ après l'âge de référence est bonifié par le
  même pivot —, et la note se tait quand il n'y a rien à dire. Le troisième
  point, faire de « à l'âge de départ effectif » le défaut, a été RÉEXAMINÉ
  et non tranché ici : c'est un changement du modèle, pas du site, et il
  déplace des chiffres de tête — voir l'action 24, qui porte la mesure.

- [x] 🔴 **Rendre cherchable la liste des statuts d'affiliation** `Simuler`
  Le menu « Statut d'affiliation » aligne plus de 60 entrées dans un `<select>` natif sans recherche, répété à l'identique pour le second métier. Trouver « SNCF » ou « artisan » suppose de tout parcourir. Ajouter un champ de recherche/autocomplétion, ou grouper les options par famille (privé, public, agricole, libéral, spécial) avec des `<optgroup>`.
  *Fait le 16 septembre 2026.* Le menu est GROUPÉ : un `<optgroup>` par
  famille — salariés du privé, fonction publique et militaires, indépendants
  et professions libérales, agriculture, régimes spéciaux, outre-mer, élus et
  assemblées, hors emploi —, et les périodes sans emploi forment le dernier
  groupe des lignes suivantes. La famille est une donnée, pas un choix du
  gabarit : chaque statut la porte dans `affiliations.yaml` (`famille`), le
  chargement refuse un statut sans famille, et un test dit qu'aucune famille
  n'est vide. Pas de champ de recherche : un `<select>` natif groupé se
  parcourt au clavier, au doigt et sous synthèse vocale sans une ligne de
  script, et sept groupes de deux à seize entrées se lisent d'un coup d'œil
  là où soixante-deux lignes ne se lisaient pas. Le script qui grise les
  statuts fermés n'a pas bougé : il parcourt `menu.options`, que les groupes
  ne cachent pas.

- [x] 🔴 **Mettre le scénario 6 (la proposition) en avant, pas en dernier** `Cas types`
  Cinq tableaux de 13 lignes × 7 générations s'enchaînent (scénarios 2 à 6) avant d'atteindre la proposition réelle. Un lecteur pressé s'arrête souvent au premier — un contrefactuel, pas la proposition. Ajouter des onglets ou un sélecteur de scénario, avec le scénario 6 affiché par défaut.
  *Fait le 16 septembre 2026.* Ce que le relecteur voyait encore : l'action
  16 avait laissé UNE grille, mais celle du scénario 5, avec les quatre
  autres dans un dépliant — le lecteur pressé s'arrêtait donc sur un
  contrefactuel. Les cinq grilles sont désormais derrière des ONGLETS, et
  l'onglet ouvert est le scénario 6, « la proposition ». Les onglets sont des
  boutons radio dont le panneau suit en CSS (`:has()`) : le clavier les
  parcourt aux flèches, aucun script ne tourne, l'adresse ne change pas. Les
  panneaux repliés sont dans la page, `hidden` — là où `:has()` manque, le
  premier reste visible. Les trois chiffres d'ouverture sont lus sur cette
  grille-là, et une phrase avant les onglets dit que le 6 est la proposition
  et les 2 à 5 des contrefactuels. Aucun témoin de simulation ne bouge.

- [x] 🟠 **Transformer la page Données en table filtrable** `Données`
  72 régimes (35 modélisés, 37 partiels, 15 hors champ) listés en prose continue avec leur niveau de fiabilité. Impossible de vérifier un régime précis sans faire Ctrl+F. Le contenu est intrinsèquement tabulaire : en faire un tableau triable et filtrable (par famille, statut, fiabilité).
  *Fait le 16 septembre 2026.* Cinq tableaux de prose sont devenus UNE table
  de 89 lignes et sept colonnes — régime, famille, ce qu'il est dans le
  modèle, fiabilité de sa fiche, période, statuts, ce qui manque —, précédée
  d'un champ de recherche et de deux menus (famille, couverture), et dont
  chaque en-tête est un bouton de tri (`aria-sort` dit le sens). Le
  comportement tient en soixante lignes d'`index.html`, en écoute déléguée ;
  sans script, la table se lit entière dans l'ordre du fichier, ce qu'elle
  était. Une ligne filtrée n'est que masquée, le compte de ce qui reste est
  dans une région `aria-live`, et la table reste repliée dans sa section : le
  budget de lecture de la page n'a pas bougé. Mesuré au navigateur : « sncf »
  donne 3 régimes sur 89, « hors champ » 15, le tri sur le nom va de
  l'Ircantec des élus à l'Unirs et revient.

- [x] 🟠 **Ajouter un sommaire aux pages longues** `Coût · Données`
  Coût et Données déroulent plusieurs dizaines d'écrans (graphiques, tableaux, encarts « ce que ça ne dit pas ») sans ancre ni retour en haut. Une table des matières collante en tête de page rendrait la navigation praticable.
  *Fait le 16 septembre 2026.* Coût et Données portent un PLAN — « Dans cette
  page » — sous leurs trois chiffres : la liste de leurs cartes et de leurs
  sections repliées, onze sur Coût, quatre sur Données. Il n'est pas écrit à
  la main : `g.plan` le DÉDUIT du HTML rendu, où chaque section identifiée
  porte son titre, si bien qu'il ne peut pas dériver et qu'il est le même
  des deux côtés du portage. Un lien porte la route de la page et
  `data-vers` ; le script l'ouvre, y pose le focus et y fait défiler sans
  toucher à l'adresse — c'est l'obstacle relevé par l'action 15 : ici
  l'adresse est la route. Pas collant : sur un téléphone, une barre fixe
  mangerait le tiers de la hauteur que le lecteur vient chercher ; et posé
  sous les chiffres, non au-dessus, pour que le résultat vienne d'abord.

- [x] ⚪ **Généraliser les sections repliables** `Toutes`
  Cas types propose déjà des triangles ▸ dépliables (« Ce que recouvre chacun des treize cas types »). Données, tout aussi dense, n'en a aucun. Généraliser le pattern à chaque page à forte densité de texte.
  *Fait le 16 septembre 2026, par l'action 15.* Données a quatre sections
  repliées, Coût neuf, Programme six, Méthode et Cas types trois et plus ; un
  test exige au moins trois sections par page et un détail replié plus lourd
  que ce qui reste ouvert. Rien à ajouter ici.

- [x] 🟠 **Vérifier le rendu mobile des tableaux à 7 colonnes** `Cas types · Coût`
  Non testé durant cette revue : à confirmer explicitement. Les tableaux « écart par génération » (7 colonnes de 1940 à 2000) et ceux de la page Coût risquent de déborder sur petit écran. Prévoir un conteneur à défilement horizontal borné, ou une vue empilée en dessous d'un certain seuil.
  *Vérifié le 16 septembre 2026.* Mesuré dans Chromium à 360 et 390 points,
  toutes les sections dépliées, sur Programme, Cas types, Coût, Données et
  une page de résultats : aucune page ne déborde (`scrollWidth` égal à la
  largeur de l'écran partout), et les tableaux plus larges que l'écran — les
  grilles à 8 colonnes de Cas types, jusqu'à 9 sur Coût, 7 sur Données —
  défilent dans leur boîte `.defilant`, qui porte `tabindex="0"` et se prend
  donc au clavier. C'est le conteneur à défilement borné que le relecteur
  demandait, et il existait ; ce qui manquait était la mesure.

- [x] ⚪ **Transformer les chemins de fichiers cités en liens** `Coût`
  La page Coût cite « docs/limites.md § 5 ter » comme une référence en texte brut plutôt qu'un lien cliquable. Chaque renvoi à un document du dépôt devrait pointer directement vers ce document.
  *Fait le 16 septembre 2026.* Les deux `<code>docs/limites.md</code>` de la
  page Coût sont des liens vers le fichier sur GitHub, et un test refuse tout
  chemin `docs/`, `scripts/` ou `data/` cité en texte brut sur les sept
  pages.

#### 2. Clarté des arguments

*L'argumentaire de la page Programme est solide et bien construit (constat → alternative → comparaison → transition). Le point faible est ailleurs : ce que les pages de preuve montrent peut contredire, en apparence, ce que Programme promet.*

- [x] 🔴 **Expliquer la baisse affichée avant les tableaux, pas après** `Cas types`
  Le scénario 6 — la proposition réelle — affiche entre -28 % et -76 % de pension par rapport à aujourd'hui pour la plupart des carrières. La clé de lecture existe (« un coefficient supérieur à un n'est pas une économie, c'est une marge »), mais elle est sur la page Coût, pas sur Cas types. Un lecteur qui saute directement aux tableaux peut comprendre l'inverse du message. Mettre cette clé de lecture en tête de Cas types, avant les chiffres.
  *Fait le 17 septembre 2026.* La clé de lecture ouvre la page Cas types,
  AVANT les trois chiffres et les grilles : « Ces pourcentages ne sont pas des
  baisses de pension », l'écart entre lignes et non le niveau, le coefficient
  que le modèle calcule sans l'appliquer, et la phrase qui compte — « un
  coefficient supérieur à un n'est pas une économie, c'est une marge ». Elle
  affirme que ce coefficient est supérieur à un pour la proposition chaque
  année, ce qui est vérifié sur la trajectoire (1,33 au plus bas, 1,52 en
  2070), et renvoie à la section de Coût qui le chiffre. La page ne calcule
  pas le coût agrégé pour le dire : quatre secondes de plus à l'ouverture,
  pour un chiffre que Coût porte déjà.

- [x] 🔴 **Rappeler que le système actuel n'est pas stable, dans les tableaux eux-mêmes** `Cas types · Coût`
  Programme insiste sur le déficit (-0,17 % du PIB en 2025, 19,3 % du PIB projeté en 2070). Les tableaux de Cas types comparent pourtant chaque scénario à « aujourd'hui » comme s'il s'agissait d'un point fixe. Le vrai choix n'est pas « notionnel contre système stable » mais « notionnel contre système qui dérive ». Rappeler la trajectoire du système actuel à côté de chaque comparaison.
  *Fait le 17 septembre 2026.* Sous les grilles de Cas types et dans la section
  des six systèmes de Coût : « le système actuel manque de 0,17 % du PIB en
  2025, et le COR projette 2,39 % en 2070 — le choix n'est pas notionnel contre
  système stable, mais notionnel contre système qui dérive ». Les deux nombres
  sont lus dans les comptes du COR, qui portent la projection jusqu'en 2070 et
  ne coûtent rien à ouvrir ; un test les recalcule. Le « 19,3 % du PIB » cité
  par le relecteur était la DÉPENSE projetée par le modèle, pas le solde : la
  page dit le solde, qui est ce que « dérive » veut dire.

- [x] 🟠 **Distinguer visuellement « contrefactuel » et « proposition »** `Cas types · Coût`
  Que les scénarios 2 à 5 soient des exercices théoriques et que seul le 6 soit la proposition du parti est expliqué en préambule, mais jamais rappelé au niveau de chaque tableau. Un badge « proposition » sur le scénario 6 et « contrefactuel » sur les autres évite l'erreur de lecture au moment où elle se produit.
  *Fait le 17 septembre 2026.* Un badge — « proposition » sur le scénario 6,
  « contrefactuel » sur les 2 à 5, rien sur le système actuel, qui est la
  référence — dans le titre de chaque panneau de Cas types et en tête de ligne
  des trois tableaux de Coût qui alignent les six systèmes (le passé, l'avenir,
  l'équilibre). Un mot en capitales espacées, pas une couleur porteuse de sens
  à elle seule.

- [x] 🟠 **Ajouter un résumé en langage courant aux pages techniques** `Coût · Méthode · Données`
  Ces pages sont rigoureuses mais écrites pour un lecteur déjà convaincu ou technicien (« coefficient d'équilibre », « assiette déplafonnée », « EIR 2020 »). Trois ou quatre phrases en langage simple avant le détail donneraient un point d'entrée à un lecteur non spécialiste, sans rien retirer à la rigueur qui suit.
  *Fait le 17 septembre 2026.* Un encart « En clair », trois à quatre phrases
  sans un mot de spécialiste, sous le chapeau de Coût, de Méthode et de
  Données. Celui de Coût dit avec les chiffres de la page ce qui a manqué en
  2025, d'où vient l'argent, ce qui manquerait en 2070 et ce qu'un système
  notionnel changerait ; celui de Méthode dit la règle en une phrase et le rôle
  du système actuel comme étalon ; celui de Données dit d'où viennent les
  chiffres et ce que « vérifié » veut dire. Un test exige les trois, visibles
  sans rien déplier, de trois à cinq phrases.

- [x] ⚪ **Sortir l'autocritique méthodologique de la masse de texte** `Coût`
  La comparaison à la projection du COR (« notre écart vaut -0,3 point de PIB au départ et 5,1 à l'arrivée […] il n'est pas flatteur ») est un vrai gage de sérieux, mais elle est noyée dans un paragraphe. En faire un encart « point de vigilance » à part la transforme en argument de crédibilité au lieu de la laisser passer inaperçue.
  *Fait le 17 septembre 2026.* La comparaison à la projection du COR est un
  encart « Point de vigilance : notre projection s'écarte de celle du COR »,
  marqué comme un avertissement (`.note.vigilance`), dans la section des six
  systèmes. Le texte n'a pas changé ; ce qui a changé est qu'on le voit.

- [x] ⚪ **Remonter le tableau de la garantie vieillesse** `Programme`
  Le tableau « 300 € et 1 500 € → 0 € aujourd'hui, 500 € avec la garantie » est l'argument le plus immédiatement parlant du site pour un lecteur non spécialiste. Il arrive tard, après plusieurs tableaux denses. Le rapprocher du haut de page renforcerait l'accroche.
  *Fait le 17 septembre 2026.* Le tableau « 300 € et 1 500 € : 0 € aujourd'hui,
  500 € avec la garantie » est sous les quatre propositions, en haut de
  l'accueil, avec une phrase d'introduction — avant le tableau qui oppose les
  deux systèmes terme à terme. Le dépliant du plancher y renvoie au lieu de le
  répéter. Le budget de lecture de l'accueil passe à deux tableaux visibles,
  pour cette raison et elle seule.

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

- [x] 🔴 **Regrouper la navigation par fonction, pas juste par page** `Global`
  Les six entrées (Programme, Simuler, Cas types, Coût, Méthode, Données) ne distinguent pas le message (Programme), la preuve (Simuler, Cas types, Coût) et la confiance (Méthode, Données). Un visiteur ne sait pas où aller après Programme. Regrouper visuellement la nav en blocs, ou ajouter une micro-description sous chaque lien.
  *Fait le 17 septembre 2026.* Le bandeau range ses six liens en trois
  groupes, chacun sous une étiquette en clair : « Le programme » (Programme),
  « La preuve » (Simuler, Cas types, Coût), « La confiance » (Méthode,
  Données). La table `GROUPES_NAVIGATION` du gabarit porte les groupes, et
  `LIENS` en reste la liste à plat. L'étiquette est du texte, pas un
  `aria-label` : tout le monde la lit. Sur téléphone, les groupes passent à
  la ligne, l'étiquette au-dessus de ses liens.

- [x] 🟠 **Traiter Données comme une base, pas comme un article** `Données`
  La taxonomie (certifiée / haute / moyenne / estimée × modélisé / partiel / hors champ) est un vrai jeu de données. La rendre en tableaux HTML statiques dans une page de prose sous-exploite sa structure. C'est la page qui justifierait le plus un vrai composant de table interactive.
  *Fait le 17 septembre 2026, avec le chantier du thème 1.* L'inventaire est
  une table filtrable et triable depuis la première passe ; il gagne ici le
  filtre par fiabilité de la fiche, ce qui donne au relecteur sa taxonomie
  croisée — famille × couverture × fiabilité — en trois menus. Et la table des
  séries certifiées, quatre-vingts lignes, se cherche et se trie de même, par
  niveau et par source. Même mécanisme, mêmes attributs, aucune ligne de
  script en plus : le comportement d'`index.html` lit `data-cible` et
  `data-unite`, et ne sait pas quelle table il filtre.

- [x] 🟠 **Créer des renvois croisés entre pages complémentaires** `Programme · Méthode · Cas types`
  Programme renvoie vers Méthode (« le détail du calcul »), mais rien ne relie Méthode aux cas concrets qui l'illustrent en retour. Ajouter des renvois contextuels dans les deux sens entre Programme, Méthode et Cas types.
  *Fait le 17 septembre 2026.* Les six sens existent : Programme renvoyait
  déjà à Méthode et à Cas types ; Méthode renvoie au programme et aux treize
  carrières dès sa quatrième phrase, et Cas types nomme « la proposition » en
  lien vers l'accueil. Un test parcourt les six sens.

- [x] ⚪ **Donner plus de visibilité à la rigueur technique du dépôt** `Méthode`
  Le moteur JS sans framework, validé contre le modèle Python sur 469 cas à la précision du flottant, est un vrai argument de confiance auprès d'un public technique — actuellement seulement accessible via le lien GitHub en bas de Programme. Un lien « comment c'est construit » depuis Méthode le mettrait en valeur là où le lecteur est déjà dans le détail.
  *Fait le 17 septembre 2026.* Un dépliant sur Méthode, « Comment ce site est
  construit, et comment on le vérifie » : le modèle de référence en Python, le
  portage JavaScript sans bibliothèque qui tourne dans le navigateur, les
  carrières témoins comparées nombre par nombre et les pages comparées
  caractère par caractère, le paquet de données qu'un test refuse périmé, avec
  les liens vers le dépôt, le README et les tests. Aucun nombre de tests ni de
  témoins n'y est écrit — le relecteur citait « 469 cas », le dépôt en compte
  484 ce jour et davantage demain — : le README les porte, et un test les
  recalcule.

- [x] ⚪ **Vérifier les méta-descriptions par route** `Global`
  Le routage en hash (#/) n'est pas un problème pour un site statique GitHub Pages, mais chaque route doit avoir sa propre balise `<title>` (déjà le cas, vérifié) et sa propre méta-description, pour un partage et un référencement corrects.
  *Fait le 17 septembre 2026.* Chaque route a sa description, dans
  `DESCRIPTIONS` (`pages.py`, recopié dans le portage, comparé par un test),
  et le routeur d'`index.html` la pose à chaque rendu comme il pose le titre.
  Ce que cela vaut, dit sans le surestimer : le site est une seule page servie
  une fois, et c'est le navigateur qui réécrit la balise. Un partage ou un
  enregistrement la reprend ; un robot qui n'exécute pas le script lit celle
  de l'accueil, qui est aussi celle du HTML servi. Des descriptions par route
  lues sans script demanderaient un fichier par page, ce que le routage en
  ancre ne permet pas sans changer d'architecture.

#### 4. Gommer la touche IA

*Le design visuel n'a pas ce problème : pas de dégradés, pas d'icônes génériques, pas d'emoji. La « touche IA » à corriger est dans le texte — des procédés rhétoriques efficaces isolément, mais reconnaissables à force d'être répétés à l'identique.*

- [x] 🔴 **Varier le procédé « Ce n'est pas X, c'est Y »** `Global`
  Répété des dizaines de fois sur l'ensemble du site (« ce n'est pas une économie, c'est une marge » ; « ce n'est pas l'ASPA à un autre montant » ; « non du passage aux comptes notionnels »…). Efficace isolément, systématique à l'échelle du site, ce qui le rend reconnaissable comme procédé. Relire chaque page en variant : comparaison implicite, exemple concret, question rhétorique.
  *Fait le 17 septembre 2026.* Mesuré avant d'écrire : le procédé, sous ses
  formes « n'est pas X : c'est Y », « X, et non Y », « non pas X », apparaissait
  sur chaque page — de deux (Cas types) à neuf fois (Coût, Méthode) dans la
  prose hors tableaux. Il n'en reste aucun. Les contrastes se disent autrement
  : une question (« La retraite française ? Un empilement de régimes, plus
  qu'un système »), une comparaison (« bien plus que du passage aux comptes
  notionnels »), un renversement (« Un coefficient supérieur à un est une
  marge, et une marge se sert »), ou une phrase séparée. Un test tient
  désormais le compte à zéro sur les sept pages, dans la prose hors tableaux,
  des deux côtés du portage.

- [x] 🟠 **Sortir les rubriques « Ce que cette page ne dit pas » du gabarit** `Coût · Données`
  Bon réflexe de transparence, mais le titre quasi identique d'une page à l'autre (« Ce que cette page ne dit pas », « Ce que ce solde ne dit pas ») accentue l'effet de patron répété. Varier les titres et intégrer ces réserves plus naturellement dans le texte plutôt qu'en rubrique systématique.
  *Fait le 17 septembre 2026.* Il n'en restait qu'une, sur Coût — « Ce que ce
  solde ne dit pas » avait disparu avec la refonte de l'action 16. Elle
  s'appelle « Dix réserves à lire avant de citer ces chiffres », dit ce qu'elle
  contient, et s'ouvre sur une phrase qui dit pourquoi elle est là. Un test
  refuse tout titre de section en « ne dit pas ».

- [x] 🟠 **Alléger les incises en tiret cadratin** `Global`
  Usage très dense du tiret cadratin en incise (« — c'est-à-dire […] — », « — et c'est […], — »). C'est l'un des tics de ponctuation les plus souvent associés à un texte généré. Remplacer une partie de ces incises par des phrases séparées, des parenthèses, ou des notes de bas de page.
  *Fait le 17 septembre 2026.* Compté dans la prose hors tableaux, où le tiret
  est une case vide : l'accueil en avait quatorze phrases, Cas types vingt,
  Méthode vingt-quatre, Coût une quarantaine. Après la passe : zéro, sept,
  sept et dix-neuf — des parenthèses là où l'incise nommait des exemples ou
  des dates, des deux-points là où elle expliquait, des phrases séparées là
  où elle prolongeait. Une cinquantaine de phrases réécrites en tout, dans les
  deux portages et dans les gloses des données (cas types, postes de
  ressources, systèmes de dépense). Le tiret n'est pas banni, c'est une
  ponctuation française ; un test plafonne son emploi page par page, à un peu
  au-dessus du compte d'aujourd'hui.

- [x] ⚪ **Casser la symétrie des triades rhétoriques** `Programme`
  Des groupes de trois membres parallèles reviennent régulièrement (« Il est illisible. Il est inégal. Il n'est pas piloté. »). Élégant isolément, répétitif à l'échelle du site. Casser le motif par endroits avec deux points, ou quatre, ou une liste asymétrique.
  *Fait le 17 septembre 2026.* « Il est illisible. Il est inégal. Il n'est pas
  piloté. » est devenu « Illisible, d'abord. Inégal, ensuite. Et personne ne
  le pilote. » — trois membres encore, mais qui ne se répondent plus mot pour
  mot. Le chapeau de l'accueil, lui, comptait déjà quatre membres et un
  « Et » ; il reste tel quel.

- [x] ⚪ **Ajouter une voix incarnée** `Programme`
  Aucun « nous avons choisi », aucun nom, aucune note personnelle sur pourquoi ce site existe : tout reste à la troisième personne impersonnelle. Une courte note signée — qui, pourquoi ce projet, quelles réserves — sur Programme ou dans une page « À propos » ferait contrepoint humain à la rigueur méthodologique.
  *Fait le 17 septembre 2026, à la première personne du pluriel.* Une note
  signée sous « Vérifiez plutôt que de nous croire » : pourquoi un modèle
  plutôt qu'un slogan, ce que nous avons choisi, ce que nous réservons — le
  modèle reste un modèle, les séries d'avant 1950 sont fragiles, le niveau des
  pensions notionnelles dépend d'un réglage que le modèle calcule sans
  l'appliquer —, et la phrase qui dit le pari : « nous préférons un chiffre
  discutable à une promesse qu'on ne peut pas discuter ». Signée « Le Parti
  libéral français, septembre 2026 » : le relecteur demandait un nom, et le
  choix d'une signature personnelle appartient au parti, comme les champs de
  l'éditeur encore à compléter sur la page des mentions légales.

> **Constat (pas une action) :** le design visuel — thème sombre sobre, sans dégradé ni icône générique — n'a pas la « touche IA » habituelle des sites générés. Le travail porte sur le texte, pas sur l'interface.

---

### 24. Convertir les droits acquis à l'âge de départ effectif, par défaut — `à faire`

**Pourquoi.** Ouverte par l'action 23 : le relecteur demandait de « réexaminer
si "à l'âge de départ effectif" ne devrait pas être le défaut plutôt qu'une
option cachée ». Le défaut actuel (`reference`) convertit les droits acquis
avant la bascule au diviseur de l'âge de référence — 67 ans — puis les sert
au diviseur de l'âge réel : qui part à 64 ans paie son anticipation une
seconde fois, sur des droits que le système actuel aurait servis sans décote.
`methodologie.md` §5 le dit lui-même : « `liquidation` est la convention qu'une
réforme réelle retiendrait, puisqu'elle seule respecte véritablement les droits
acquis ». Le site l'écrit désormais sous les fiches du simulateur (action 23),
mais un défaut que la page doit expliquer à chaque calcul est un défaut qui
pose question.

**Ce que ça déplacerait, mesuré le 16 septembre 2026.** Sur la carrière témoin
(né en 1975, salarié non cadre à 3 500 € par mois, départ à 64 ans en 2039), le
scénario 3 passe de 23 074 € à 25 334 € par an (+9,8 %), le scénario 5 de
28 452 € à 30 712 €. Sur Cas types, 40 des 91 cellules des scénarios 3 et 5
bougent, de +0,1 à +30,8 points d'écart au système actuel, médiane +3,9 points ;
les 51 autres — départs à l'âge de référence ou après, générations déjà
retraitées — ne bougent pas. Les scénarios 1, 2, 4 et 6 sont indifférents. La
page Coût bouge sur les seuls scénarios 3 et 5 de sa section « six systèmes ».

**Fichiers.** `src/retraite_notionnelle/config.py` (`age_conversion_droits_acquis`),
`src/retraite_notionnelle/web/pages.py` (`CONVERSIONS_ACQUIS`, la note et la
cascade qui présentent le défaut comme tel), `moteur/js/config.js` et
`moteur/js/pages.js`, `docs/methodologie.md` §5, `README.md` (le tableau
d'exemple, qu'un test recalcule), les témoins.

**Marche.** Changer le défaut des deux moteurs, régénérer les témoins et lire
leur diff — c'est lui qui dit, cellule par cellule, ce que la convention
coûtait. Garder `reference` comme variante, pour que la mesure reste
reproductible. Réécrire la note et la cascade : elles décrivent aujourd'hui le
défaut comme une pénalité à retirer ; elles décriront la variante comme une
lecture stricte du cahier des charges. Le piège à nommer d'avance : le
scénario 3 est l'étalon d'une réforme applicable, et le relever de dix pour
cent sur une carrière courante déplace la lecture de tout le site — c'est
précisément pourquoi la décision se prend en connaissance des témoins, et non
dans une passe sur le site.

**Fin.** Le défaut du simulateur est la convention qu'une réforme réelle
retiendrait, `limites.md` §3 et `methodologie.md` §5 disent ce que l'ancien
défaut coûtait, et la note du simulateur ne parle plus d'un réglage à trouver.

### 25. Le barème de la surcote de 2004 à 2008, trimestre par trimestre — `fait`

**Pourquoi.** Le scénario 1 sert la surcote au taux de la fiche en vigueur
l'année de la liquidation, à tous les trimestres. Le droit la sert au taux en
vigueur l'année où chaque trimestre a été ACCOMPLI : 0,75 % pour les trimestres
de 2004 à 2006 ; à compter de 2007, 0,75 % pour les quatre premiers, 1 %
au-delà, 1,25 % pour ceux accomplis après soixante-cinq ans (décret
n° 2006-1611) ; 1,25 % pour tous ceux accomplis depuis le 1er janvier 2009
(LFSS 2009), les trimestres antérieurs gardant leur taux. La fonction publique
suit le même calendrier, avec son plafond de vingt trimestres jusqu'en 2008.
`limites.md` le range parmi les écarts connus du scénario 1 depuis longtemps.
Ce que ça touche : toute liquidation de 2004 à 2008, et toute liquidation
postérieure dont des trimestres de surcote ont été accomplis avant 2009 — les
générations 1944 à 1948. Aucun assuré qui simule aujourd'hui son départ n'est
concerné ; les cas types des générations 1940 et 1950 le sont, donc la page
Coût, et c'est le dernier écart daté que l'étalon garde sur le régime général.

**Sources à lire.** Article D. 351-1-4 du code de la sécurité sociale dans ses
versions successives — l'index LEGI les rend en une requête,
`python scripts/fetch/dila_cherche.py legi 'surcote' --num D351-1-4` —, décret
n° 2006-1611 du 19 décembre 2006, décret n° 2008-1509 du 30 décembre 2008,
article L. 14 III du code des pensions civiles et militaires.

**Fichiers.** `data/reference/regimes/base_prive.yaml` et
`fonction_publique.yaml` (couper la période 2004-2008 en 2007 et porter les
trois taux), `data/reference/regimes/pivots.yaml` et
`legislation/reformes.yaml` (la coupure doit y être déclarée, un test l'exige),
`src/retraite_notionnelle/scenarios/actuel.py` (`_trimestres_cotises_apres`
rend un compte, il doit rendre des trimestres datés), `moteur/js/scenario-actuel.js`,
les témoins.

**Marche.** Dater les trimestres de surcote — ce sont les derniers accomplis,
ceux qui suivent à la fois la durée requise et l'âge légal —, lire le taux de
chacun à la fiche de SON année et non de l'année du départ, avec le rang cumulé
depuis 2004 pour le palier de quatre. Puis confronter à l'oracle OpenFisca sur
un profil né en 1945 parti à 63 ans, si son module suit ce barème ; sinon à un
exemple de circulaire Cnav (action 26).

**Fin.** La ligne « Barème de la surcote entre 2004 et 2008 » quitte la liste
des écarts connus de `limites.md`, et le diff des témoins dit ce que valent les
surcotes des générations 1940 et 1950.

**Ce que ça a déplacé.** Fait le 17 septembre 2026, et plus largement que
l'action ne l'écrivait : non pas une coupure de fiche en 2007, mais une table
`legislation/surcote_baremes.csv` et un champ de fiche `surcote_bareme` qui
donnent à chaque trimestre civil de surcote le taux en vigueur à sa date, avec
la période de référence de la circulaire Cnav 2018-04 — depuis le trimestre
civil qui suit l'âge légal, ou le mois qui suit la durée requise. Les trois
exemples de la circulaire se rejouent au centième (2,5 %, 4,75 %, 10,25 %), et
deux fiches de service-public aussi, qui ne se rejouaient pas avant : le modèle
comptait le trimestre de l'anniversaire et servait 6,25 % là où la caisse en
sert 5. La fonction publique suit avec son plafond de vingt trimestres. La
confrontation à OpenFisca en garde une trace : sur le profil surcoté de 1948,
OpenFisca sert douze trimestres à 1,25 %, le modèle trois à 0,75 % et huit à
1,25 %, et le test vérifie que chacun rend ce que sa règle commande.

### 26. Confronter le scénario 1 aux exemples chiffrés officiels — `fait`

**Pourquoi.** L'étalon a une contre-expertise, OpenFisca-France-Pension
(action 4), et c'est un autre modèle, pas une source. Aucun simulateur officiel
n'est automatisable : « Mon estimation retraite » d'info-retraite.fr (M@rel),
le simulateur de l'Assurance retraite, celui de l'Agirc-Arrco et l'ENSAP des
fonctionnaires exigent FranceConnect et le relevé de carrière réel de la
personne connectée, sans mode anonyme ni API ; les modèles des administrations
— TRAJECTOiRE à la DREES, DESTINIE à l'INSEE, celui de la Cnav — ne sont pas
publiés. Ce qui est officiel ET reproductible, ce sont les EXEMPLES CHIFFRÉS
que les caisses et l'administration publient : les circulaires Cnav — décote,
surcote, minimum contributif, majoration pour enfants, salaire annuel moyen,
carrière longue, chacune avec un ou plusieurs cas résolus —, les fiches de
service-public.fr, le guide de l'Agirc-Arrco, les fiches de calcul du Service
des retraites de l'État, et les cas types du COR, dont chaque rapport annuel
publie l'âge de départ et le taux de remplacement par génération. Chaque
exemple est une carrière minuscule dont la réponse est écrite par la caisse qui
applique la règle : c'est la seule confrontation qui ne soit ni une relecture
ni un autre modèle.

**Sources à lire.** La base documentaire de la Cnav (circulaires et lettres
ministérielles, accessible sans compte) ; service-public.fr, fiches « Décote »,
« Surcote », « Retraite anticipée pour carrière longue », « Minimum
contributif » ; COR, rapport annuel, annexe des cas types ; Service des
retraites de l'État, fiches de calcul de la pension civile.

**Fichiers.** `tests/temoins/exemples_officiels.yaml` (nouveau : chaque exemple
avec sa source datée, sa carrière, le résultat publié et la grandeur comparée),
`tests/test_oracle.py` (une confrontation de plus, qui rejoue chaque exemple par
`carriere_parcours` et compare la grandeur nommée), `docs/limites.md` §3 (ce
que la confrontation a trouvé, de chaque côté).

**Marche.** Commencer par les exemples qui ne demandent qu'une carrière simple
et une seule règle — décote, surcote, carrière longue, majoration pour
enfants —, transcrits tels que la source les écrit, sans convention de
traduction qui deviendrait l'objet du test ; puis les cas types du COR, qui
demandent une hypothèse de salaire. Chaque désaccord se tranche par le texte,
jamais par l'exemple seul : une circulaire peut être antérieure à la règle
qu'on applique.

**Fin.** Trente exemples officiels au moins rejoués par un test, et
`limites.md` §3 dit, pour chaque famille de règle du scénario 1, laquelle a été
confrontée à un exemple publié par la caisse qui l'applique.

**Ce que ça a déplacé.** Fait le 17 septembre 2026, avec vingt-deux exemples
et non trente — les fiches de service-public en portent moins qu'espéré, et le
COR n'en publie pas qui se rejouent sans ses hypothèses de salaire. Le premier
exemple lu a fait voir que le droit avait changé depuis le dump LEGI du dépôt :
la SUSPENSION de la réforme de 2023 (loi n° 2025-1403, article 105, décrets
du 7 mai 2026) manquait, avec la carrière longue par génération, les
vingt-quatre et vingt-trois meilleures années des parents (décret
n° 2026-699) et les deux trimestres d'enfants réputés cotisés. Tout cela est
porté : tables réécrites au niveau `moyenne` en attendant un dump LEGI
postérieur au 8 mai 2026 (action 27), carrière longue datée au mois et lue par
génération, barème daté de la surcote (action 25). Les vingt-deux exemples
tombent justes, dans le privé et dans la fonction publique. Ce que ça déplace
dans les témoins : aucun chiffre de simulation ne bouge pour les générations
d'avant 1963 hors surcote d'avant 2009 ; les générations 1964 à 1968 partent
un trimestre plus tôt avec un ou deux trimestres de moins à réunir ; les
cas types au SMIC et le trajet de la page Coût suivent. Trois leçons. **Une
table certifiée l'est à une date**, et le journal de certification doit dire
laquelle — c'était déjà sa règle, c'est ce qui a permis de voir que juillet
2025 ne pouvait pas porter décembre 2025. **Un exemple publié vaut plus qu'une
relecture** : cinq règles sont tombées justes du premier coup, quatre ne le
sont devenues qu'en lisant le texte que l'exemple cite. Et **la surcote est la
règle la plus mal comptée du système** : trois barèmes en cinq ans, une
période de référence au trimestre civil, un rang qui court depuis 2004 — il
fallait trois exemples pour la tenir.

### 27. Relire dans LEGI ce que la suspension de 2026 a réécrit — `fait`

**Pourquoi.** Les tables d'âge légal, de durée requise, de carrière longue et
des catégories actives portent depuis le 17 septembre 2026 les valeurs de la
loi n° 2025-1403 et de ses décrets du 7 mai 2026, transcrites de la loi et
des circulaires Cnav 2026-07 et 2026-17 : niveau `moyenne` ou `haute`, parce
que le récupérateur `scripts/fetch/dila_legi_parametres_retraite.py` a lu le
dump LEGI du 13 juillet 2025, antérieur à la réforme. Ce niveau remonte au
résultat affiché à tout assuré né de 1964 à 1968, c'est-à-dire à la plupart de
ceux qui simulent leur départ.

**Sources à lire.** Un dump LEGI postérieur au 8 mai 2026 (échanges de la
DILA), et pour la carrière longue le II de l'article D. 351-1-1, que le
récupérateur ne lit pas — il ne prend que la règle générale — et qu'il faudra
lui apprendre à lire par génération, ou confronter à la main à la circulaire.

**Fichiers.** `data/brut/dila_legi_parametres_retraite.json` (à régénérer),
`scripts/verifier_donnees.py --appliquer`, `data/derive/certification.json`,
les quatre tables de `data/reference/legislation/`, `tests/test_donnees.py`
(les lignes « moyenne » redeviennent « certifiee »).

**Marche.** Relancer le récupérateur sur le dump récent, vérifier que les
seize segments d'âge et les durées qu'il rend sont ceux de la circulaire,
appliquer, et retirer des tests la liste des générations suspendues. Les
catégories actives sont déjà lues alinéa par alinéa dans le décret
n° 2026-344 (niveau `haute`) ; reste à les faire relire par le récupérateur.

**Fin.** Plus aucune ligne `moyenne` dans ces tables, et le journal de
certification daté d'après le 8 mai 2026.

**Ce que ça a déplacé.** Fait le 17 septembre 2026, le jour même de l'action
26. Aucun chiffre : les 79 segments d'âge, les 20 de durée requise et les 28
portes de carrière longue que le récupérateur rend sont IDENTIQUES aux lignes
transcrites de la loi et des circulaires — c'est le résultat attendu, et
c'est un résultat. Ce qui a changé, c'est d'où il les lit et ce qu'il sait
lire.

- **Il n'y a pas de dump récent, et il n'y en aura pas.** La DILA n'a pas
  régénéré son dump global depuis le 13 juillet 2025 ; tout ce qui a paru
  depuis n'est que dans ses incréments quotidiens. Le récupérateur lit donc
  l'index LEGI du dépôt (`dila_index.py legi`, dump plus incréments, tenu à
  jour chaque lundi par le workflow), en quelques secondes au lieu d'un quart
  d'heure et 1,1 Go ; `--dump` garde l'ancienne voie, qui rendra les âges de
  2023 tant que le dump ne bougera pas. Le fichier de sortie et le journal de
  certification écrivent jusqu'à quel incrément l'index était à jour.
- **La table des âges est dans la loi, plus dans le décret.** La loi
  n° 2025-1403 a réécrit L. 161-17-2 avec la table génération par génération
  (version du 31 décembre 2025, applicable au 1er septembre 2026) et a laissé
  D. 161-2-1-9 dire 63 ans pour 1964. Le récupérateur lit les deux articles,
  ordonne les versions par leur DATE D'EFFET — lue dans la note « s'appliquent
  aux pensions prenant effet à compter du » — et les fait se recouvrir AU MOIS
  près : la loi de 2025 prend les nés à compter du 1er septembre 1961, le
  décret garde ce qu'elle renvoie à « sa rédaction antérieure », janvier-août
  1961 compris. Trois formes que l'ancien récupérateur ne lisait pas :
  « 1 er » espacé, « entre le 1er avril et le 31 décembre 1965 » sans année à
  la première date, et un renvoi en fin d'alinéa qui, lu d'un bloc, aurait
  opposé 63 ans et 9 mois à tous les nés d'avant 1961 — d'où la lecture par
  phrase.
- **La carrière longue par génération est lue, plus transcrite.** Le II de
  D. 351-1-1 écrit la borne des vingt ans par substitution — « soixante »,
  « l'âge prévu à l'article L. 161-17-2 minoré de deux ans et six mois »,
  « soixante ans et neuf mois » et « huit mois » respectivement — et le
  récupérateur la résout contre la table d'âge en vigueur à la date d'effet
  de chaque version : 63 ans moins 2,5 pour 1964 au 1er septembre 2023,
  60 ans et 6 mois écrits en toutes lettres au 1er septembre 2026. La version
  du 1er janvier 2026 (décret n° 2025-1410) réécrit le I sans changer une
  valeur : elle n'ouvre pas de date d'effet.
- **Trois textes morts, découverts en passant.** Le décret n° 2025-1409 du
  30 décembre 2025 a abrogé au 1er janvier 2026 le II de R. 351-27
  (coefficient par génération : « 1,25 % » pour tous désormais), le II de
  R. 351-6 (proratisation par génération) et R. 351-29-1 (années du salaire
  de référence, passées à R. 173-3-2). Aucun ne touche personne — les
  générations nommées ont passé l'âge du taux plein d'office — et la base les
  consolide en tronquant plutôt qu'en effaçant. Les trois lectures sont
  désormais version par version, chacune ne recouvrant que les générations
  qu'elle nomme, et les tables le disent.

**Le même jour, la suite — tout ce que le dump de juillet 2025 laissait dans
l'ombre.** Les quinze autres récupérateurs de la DILA (`dila_legi_*`,
`jorf_*`, `sncf_contribution_employeur.py`) retéléchargeaient le dump global
et tombaient dans le même piège. Chacun lit désormais l'index par défaut :
son filtre, écrit pour le dump, est rejoué tel quel sur un flux qui en reprend
la forme balise par balise (`dila_index.filtrer_index`) — l'ordre compte, le
filtre de la CNRACL cherche « Article 3 MODIFIE » là où le dump l'écrit —,
et `--dump` garde l'ancienne voie pour contrôle. Ce que la relecture a
rendu, tout le reste étant identique : le point agricole de 2025, le décret
des cotisations libérales pour 2026 — avec la refonte de la CARPIMKO en un
taux unique de 8,7 %, lue dans le texte et inscrite comme rupture connue —,
la contribution CNRACL jusqu'en 2028. Et la carrière longue d'avant 2023 :
les rédactions de 2003, 2011 et 2012 de D. 351-1-1 se lisent, génération par
génération, et les quatre-vingts portes de la table sont certifiées. Ce que
cela a fait voir : la table opposait sous 2012 deux portes (56 et 58 ans pour
un début avant seize ans) à toutes les générations, quand le texte ne les
écrit que génération par génération jusqu'à 1960 ; et **le moteur retenait
une porte par borne d'entrée** quand une borne en ouvre deux — 56 ans avec
huit trimestres de plus ou 58 avec quatre —, si bien que l'une des deux
tombait au hasard de l'ordre du fichier. Il retient une porte par couple
(borne, supplément), en Python comme en JavaScript. Enfin la relecture de
l'action 27 elle-même : une version qui ne nommait que les premiers mois
d'une génération en réécrivait l'année entière ; les tables lues au mois
passent mois par mois, un test le fige, aucune valeur ne bouge.

Ce qui reste : les catégories actives (le décret n° 2026-344 modifie un
article de loi non codifié, que seul l'index JORF porte : lues à la main,
`haute`).

---

### 28. Le simulateur, outil du site partiliberalfrancais.fr — `fait`

**Pourquoi.** Le site du parti sert une copie de ce dépôt sous `/retraite/`,
et l'avait habillée de son côté : une feuille `plf-theme.css` chargée après
`moteur/style.css`, qui redéfinissait toutes les variables de couleur, forçait
le thème sombre aux deux préférences système, imposait sa police et un plancher
de taille à une vingtaine de sélecteurs INTERNES du simulateur ; et un bandeau
« retour au site » inséré dans `index.html`. Chaque mise à jour de la copie
pouvait casser cet habillage sans que rien ne le dise — et la copie avait déjà
deux blocs de retard sur `main`. Ce dépôt ne contrôle pas ce site : la seule
réponse tenable est que le simulateur porte lui-même l'air de famille et le
pont, et que l'hôte n'ait plus qu'un lien à poser.

**Marche.** Le site parent a été lu en lecture seule, dans un navigateur, à
quatre largeurs : fond bleu-vert, texte blanc, titres en police de marque, liens
turquoise, focus doré, corps dans la pile du système. Le simulateur en reprend
la FAMILLE, pas le dessin : un bandeau sombre bleu-vert souligné d'or, le même
dans les deux thèmes, qui porte au-dessus du titre le lien vers le site ; un
accent de la même teinte, assombri en clair (6,7:1 au plus bas) et éclairci en
sombre (7,3:1) ; la pile de polices du système, qui est aussi celle du site et
la seule qui existe sur tous les téléphones ; des boutons et des champs aux
angles de 6 px. Le reste — cartes claires, tableaux, tracés, dépliants — est ce
qu'un outil de calcul doit à ses chiffres, et n'a pas bougé. Le thème sombre
tire vers le bleu-vert au lieu du gris. Rien n'est chargé du site : ni police,
ni feuille, ni script, ni logo.

**Ce que ça a déplacé.** *Aucun chiffre* : les témoins de simulation et de
page sont inchangés. Ce qui change est l'habillage et le pont.

- *Le pont.* Un lien « Parti libéral français » en tête, une ligne en pied,
  tous deux `target="_top"` : ouvert dans le cadre que la page d'accueil du
  site ouvre sur `/retraite/`, un lien ordinaire aurait chargé le site DANS le
  cadre. C'est la seule adresse extérieure de l'en-tête, et un test l'impose :
  la navigation du site n'est pas recopiée, elle se périmerait à sa prochaine
  mise en page. Quand l'hôte pose `plf-embedded` sur `<body>` — ce qu'il fait
  déjà —, le pont se masque de lui-même.
- *Le contrat.* `docs/integration-partiliberalfrancais.md` dit à l'hôte ce
  qu'il doit savoir : un lien suffit ; les adresses stables ; ce qu'un
  hébergement doit servir ; que rien n'est chargé d'ailleurs ; que les NOMS des
  variables de `:root` sont stables et que rien d'autre ne l'est ; et que
  `plf-theme.css` comme `plf-back-link` sont désormais des doublons à retirer.
  Avec la comparaison `/retraite/` contre `/retraite/#/simuler` pour un lien
  nommé « simulateur » : le second, un geste avant le premier résultat, aucun
  contexte perdu.
- *Vérifié.* Contrastes retenus par les tests (textes, contours, palette des
  scénarios) dans les deux thèmes ; l'en-tête et le pied comparés entre les
  deux portages par un test nouveau ; ordre de tabulation lien d'évitement →
  pont → titre → navigation → formulaire, contour doré sur le bandeau ; aucun
  défilement horizontal de 320 à 1 440 px ; le focus des résultats après
  calcul inchangé. Impeccable ne relève que ce qui est voulu (le filet
  latéral des notes, la jauge d'attente, coupée en mouvement réduit) ; les Web
  Interface Guidelines ont donné `text-wrap: balance` sur les titres et
  `theme-color` sur la page, et rien de leurs préférences de copie anglaise.
- *Ce qui reste à l'hôte.* Retirer ses deux modifications et recopier `main`
  tel quel ; poser un lien visible — l'onglet « Retraites notionnelles » est
  masqué depuis que le site a jugé le simulateur « pas encore prêt ». La page
  Mentions nomme GitHub comme hébergeur, ce qui est vrai de l'adresse GitHub
  Pages et à compléter pour la copie : c'est à l'éditeur.

### 29. L'entrée : dire « simulateur » en dix secondes, et dans le cadre du site — `fait`

**Pourquoi.** Un visiteur qui n'a jamais entendu parler de comptes notionnels
doit comprendre en dix secondes qu'il s'agit d'un simulateur, qu'il peut y
mettre sa carrière, que six règles seront comparées, et où cliquer. Le
premier écran ne le disait pas : un titre de programme, un slogan, trois
chiffres, quatre propositions ; le mot « simuler » dans un onglet, et le seul
bouton au troisième écran — au cinquième sur un téléphone. Sur le site du
parti, qui ouvre cette page dans un cadre en masquant son titre, c'était pire :
rien ne disait « simulateur » ; « Calculer les six scénarios » laissait le
lecteur sur le haut du formulaire sans un résultat en vue, parce que le cadre
gardait la hauteur de la page d'avant jusqu'à la remesure de l'hôte ; et le
bouton du bas le laissait sur la fin du formulaire et le pied du site. Après
le calcul, un téléphone montrait d'abord un coefficient de conversion, un
capital et une note sur l'âge de référence, et pas un euro de pension.

**Marche.** Le site rendu a été lu dans un navigateur, sur ordinateur et sur
téléphone, seul puis dans le cadre du site parent (`/#simulateur`), avec les
positions mesurées de chaque élément après chaque clic. Puis le plus petit jeu
de changements qui réponde aux quatre questions, sans rien déplacer d'autre.

**Fichiers.** `src/retraite_notionnelle/web/pages.py` et `web/gabarit.py`,
`moteur/js/pages.js` en regard, `index.html`, `tests/test_web.py`,
`tests/temoins/pages.json`, `docs/integration-partiliberalfrancais.md`.

**Ce que ça a déplacé.** *Aucun chiffre* : les témoins de simulation sont
inchangés, seuls ceux des pages ont bougé.

- *L'accueil.* Sous le chapeau, un bloc de deux lignes et un bouton : « Ce
  que ça donnerait pour vous ? Simulez votre carrière. Six montants côte à
  côte : les règles d'aujourd'hui, et cinq autres. — Simuler ma retraite ».
  Dans le premier écran, sur ordinateur comme sur téléphone, seul comme dans
  le cadre. Rien d'autre ne bouge : titre, chapeau, repères, propositions,
  tableaux et bouton du bas sont là où ils étaient. Le budget de lecture de
  la page passe de 650 à 670 mots.
- *Le formulaire.* Une ligne sous le titre : « L'exemple est déjà rempli.
  Calculez-le tel quel, ou saisissez votre carrière. »
- *Les résultats.* Cinq phrases sous « Résultats », avant les chiffres : le
  scénario 1 est la référence, les cinq autres sont d'autres règles sur la
  même carrière, le grand chiffre est la pension brute mensuelle, le
  pourcentage l'écart avec le scénario 1. Et les deux cartes sont
  interverties : les six montants d'abord, les repères techniques ensuite.
  Leur contenu est inchangé.
- *Le cadre.* `index.html` : quand la page est dans un cadre de même origine,
  elle règle elle-même la hauteur du cadre après chaque rendu, puis fait
  défiler la page hôte — jusqu'aux résultats après un calcul, jusqu'au haut
  du cadre après un changement de page. Hors cadre, rien ne change. Vérifié
  sur un hôte de test qui reproduit le cadre du site : après « Calculer », le
  premier montant est à l'écran ; après le bouton du bas, le titre du
  formulaire aussi.
- *Ce qui n'a pas bougé, à dessein.* Les routes, le bandeau et ses trois
  groupes, les six scénarios et leur ordre, les bulles, les dépliants, le
  formulaire et ses options, l'accessibilité, les mentions.

**Ce qui reste.** L'onglet du site parent s'appelle « Retraites
notionnelles » et est masqué ; le titre du simulateur, masqué par l'hôte dans
le cadre, est encore « Retraite à comptes notionnels ». Ni l'un ni l'autre ne
se change d'ici.

### 30. La refonte en affiche, et le partage là où l'on regarde — `fait`

**Le constat.** Le site disait juste et ne se retenait pas. Bandeau bleu-vert
sage, cartes claires, titres de tableau de bord : la mise en page d'un outil de
calcul, posée sur un programme politique que personne n'a demandé à lire. Le
simulateur, qui est l'argument — les autres partis proposent, celui-ci
chiffre —, n'apparaissait qu'au troisième écran, et le mot ne figurait que dans
un onglet.

**Ce qui a été fait.** Une maquette, travaillée et validée écran par écran dans
Claude Design (huit écrans, quatre-vingts allers-retours), portée ici :

- *Une identité d'affiche.* Vert profond `#0b3d3a`, or `#e9c53d`, crème pour ce
  qu'on remplit ou qu'on emporte. Titres en capitales très serrées, fluides de
  36 à 97 px. Public Sans et Instrument Serif, **servies par le dépôt** —
  `moteur/polices/`, sous OFL : les charger chez Google aurait emporté
  l'adresse IP du lecteur chez un tiers à chaque visite, et fait mentir « rien
  n'est envoyé ». UN SEUL THÈME : l'affiche est l'identité, pas un habit de
  nuit, et `@media print` reteinte tout en noir sur blanc.
- *Chaque page porte son titre.* Le nom du site n'est plus un `<h1>` répété
  huit fois ; `g.affiche()` donne à chaque page un sur-titre, un `<h1>` et un
  chapeau. Un `h1` par page, vérifié au navigateur.
- *Une barre d'onglets.* Huit pages, collante au large, statique sur téléphone.
  Les trois groupes de fonction subsistent pour les synthèses vocales, sortis
  de l'écran par `clip-path` et non par `display: none`. L'onglet courant porte
  un soulignement épais EN PLUS de sa couleur, et `aria-current`.
- *Deux pages neuves.* **Trajectoire** (cumul versé du départ à 105 ans) sort
  le graphique le plus démonstratif du dépôt du dépliant où il était rangé et
  lui donne sa page, avec le formulaire court pour changer de carrière sans la
  quitter. **Partager** porte quatre cartes 1200 × 675, rendues à leur taille
  réelle dans un cadre défilant — en unités relatives, aucune capture n'aurait
  fait l'image annoncée.
- *Le partage descend sur les pages.* Une page « Partager » seule ne sert
  personne : on ne la trouve pas. Chaque carte à graphique porte donc trois
  boutons — **Publier sur X** (message pré-écrit tiré de la carte, borné à
  280 signes, l'adresse comptée pour 23), **Télécharger l'image**, **Copier le
  texte** (avec repli `execCommand` et champ sélectionnable si le
  presse-papiers refuse). `texteDeLaCarte()` dans `index.html`, à côté
  d'`imageDeLaCarte()`.
- *Accessibilité, reprise en même temps.* Un focus clavier visible, qui
  manquait entièrement — c'était le défaut le plus pénalisant du site. Libellés
  de formulaire en 15 px casse normale au lieu de capitales à 12. Gloses en
  sans-serif 16 px au lieu de serif fin 15. Emphase en or DOUBLÉE d'un
  demi-gras, pour survivre en niveaux de gris. Tableaux larges qui disent
  qu'ils défilent. Cibles tactiles portées à 24 px.

**Ce que ça a déplacé.** Rien dans le modèle : aucun scénario, aucune série,
aucun barème n'a bougé, et les témoins de simulation sont identiques au
caractère près. Deux corrections réelles cependant, l'une et l'autre trouvées
par les tests du dépôt :

- *La palette des scénarios était à refaire.* Celle d'avant avait été posée sur
  un fond presque noir ; sur le vert profond elle tombait entre 2,5 et 3,9:1.
  La nouvelle tient 4,8:1 au moins, et surtout **ΔE ≥ 15 entre toutes les
  paires** et non seulement entre voisines — l'ancienne descendait à 7,3 sur ce
  critère. Six teintes ne se séparent pas toutes sous deutéranopie (le meilleur
  arrangement possible y descend à 8,6) : c'est pourquoi tirets, intitulés et
  signes portent l'information à côté de la couleur.
- *Le contour des champs* est passé de 2,59:1 à 4,12:1 (WCAG 1.4.11).

**Vérifié.** 897 tests (contre 882), dont les neuf routes comparées
caractère par caractère entre Python et le portage. Au navigateur, sur les huit
pages : un `h1` chacune, aucune requête hors du site, aucune erreur de console,
aucun débordement latéral à 320, 390 et 820 points, les trois boutons de
partage fonctionnels (PNG composé, intention X formée, presse-papiers à
278 signes).

**Ce qui restait** — les six scénarios affichés et leurs libellés — a été fait
juste après, sous l'action 31.

### 31. Quatre systèmes comparés, au lieu de six — `fait`

**La demande.** « Les scénarios 3 et 5, on les a mis à la base, mais je pense
qu'ils sont inutiles désormais. » Ce sont les deux variantes *dès la bascule* :
droits acquis conservés, règles notionnelles ensuite. Et un renommage, proposé
par l'auteur du site : « Compte notionnel, part salariale seule » plutôt que
« Notionnel rétroactif », qui ne disait rien à qui n'avait pas lu la Méthode.

**Ce qui a été fait.**

- *Un seul endroit décide.* `SCENARIOS_MONTRES` et `LIBELLES_SYSTEMES`, dans
  `web/pages.py` : les barres de Simuler, les courbes de la Trajectoire, les
  grilles de Cas types et le comparatif de Coût les lisent tous.
- *Les quatre libellés* nomment ce qui change d'un système à l'autre —
  l'assiette —, et la GLOSE porte ce que le titre a cessé de dire : depuis
  quand la carrière est recalculée, et à quel taux. Sans elle on ne
  comprendrait pas pourquoi le 2 donne moins que le 4.
- *La numérotation suit*, 1 à 4, dans les cinquante-deux phrases qui citaient
  un numéro. Le mot a changé en même temps — « scénario » devient « système »
  dans tout ce que le lecteur voit —, ce qui rendait la substitution sûre :
  aucune collision possible entre la source et la cible. La nomenclature du
  MODÈLE ne bouge pas : `cout.SCENARIOS` numérote toujours ses six de 1 à 6, et
  aucune page n'affiche plus un libellé venu de là.
- *La page Coût passe à quatre aussi*, tableaux et graphique. Et la courbe de
  la carte de tête, qui traçait une variante que le site ne montre plus, trace
  désormais LA PROPOSITION : 8,6 % du PIB en 2025, 8,1 % en 2070, contre
  14,1 % et 15,3 % pour le système actuel.

**Ce que ça a coûté, et qui n'était pas prévu.** Les scénarios 3 et 5 étaient
les SEULS à convertir les droits acquis. Les retirer de l'affichage a donc
rendu inertes, et fait retirer avec eux : la fiche « âge de référence », son
avertissement (« vous partez 3 ans avant l'âge de référence — l'anticipation
est payée une seconde fois, sur le passé »), le dépliant « du système 1 au
système 3, ligne à ligne » qui était l'explication la plus concrète du calcul
notionnel, et deux options du formulaire. Le modèle les calcule toujours ;
aucune page ne les montre. Le choix a été posé explicitement avant d'être fait.

**Ce que ça a déplacé, en bien.** La palette. À six teintes, la séparation sous
deutéranopie plafonnait à ΔE 8,6 et aucun choix de couleurs n'y changeait rien
— six catégories ne se distinguent pas toutes pour un œil qui confond le rouge
et le vert. À quatre, la contrainte se relâche : la nouvelle palette tient
ΔE ≥ 15,5 sous deutéranopie et ≥ 15,2 sous protanopie, au-dessus du plancher de
15. **Le contrôle daltonien est désormais dans le test** — `_simuler_daltonisme`,
matrices de Viénot-Brettel-Mollon — au lieu d'être sous-traité à une relecture
extérieure comme il l'était depuis la pose de la palette.

**Vérifié.** 896 tests, les neuf routes comparées caractère par caractère entre
Python et le portage, et au navigateur : quatre barres sur Simuler, quatre
courbes sur la Trajectoire, trois onglets sur Cas types, la proposition sur le
graphique du Coût, aucune erreur de console.

### 32. Retirer les mentions légales, que le site d'accueil porte — `fait`

**La demande.** « On peut enlever toutes les mentions légales, données
personnelles et accessibilité ? Normalement le site
https://partiliberalfrancais.fr/ qui va accueillir ça prendra toute la partie
légale. »

**Pourquoi c'est juste.** Le simulateur est servi sous
`partiliberalfrancais.fr/retraite/` : c'est ce site qui l'édite et qui
l'héberge, et donc lui qui doit l'identification de l'éditeur (LCEN, article
6-III), la politique de données personnelles et la déclaration
d'accessibilité. Deux déclarations concurrentes valent moins qu'une, et celle
du dépôt était déjà fausse d'un côté : elle nommait GitHub, Inc. comme
hébergeur, ce qui n'est vrai que de l'adresse GitHub Pages. L'action 28 l'avait
noté sans le corriger — « c'est à l'éditeur » —, et les quatre champs
`a-completer` de la rubrique Éditeur attendaient depuis l'action 23.

**Ce qui a été fait.**

- *La page `/mentions` n'existe plus* : ni route, ni titre, ni description
  `meta`, ni témoin, ni lien en pied. Le site n'a désormais plus aucune page
  hors de sa barre de navigation, et un test l'exige (`set(LIENS) == set(TITRES)`).
- *Le style `.a-completer`* — le champ marqué en rouge tireté que l'éditeur
  devait combler — part avec elle.
- *Ce que l'hôte ne peut PAS porter reste*, parce qu'il ne le connaît pas : la
  licence Apache 2.0 du code, la CC BY-SA 4.0 des infographies et des textes,
  l'ISC de Lucide, et l'obligation de citer le producteur d'une série plutôt
  que ce site. Ces trois paragraphes sont repliés sous Données — dépliant
  « Licences et réutilisation », `donnees-reutilisation` —, à côté de la liste
  des vingt-huit institutions : qui vient chercher d'où sort un chiffre est
  celui-là même qui s'apprête à le reprendre. Le pied de page continue de dire
  les deux licences en une ligne, et que le simulateur n'a aucune valeur
  officielle.
- *Un test interdit le retour* de « Mentions légales », « conformité
  partielle », « règlement (UE) 2016/679», « RGAA », `a-completer` et du
  Défenseur des droits, sur toute page et dans le pied.

**Ce qui n'a pas changé : l'accessibilité elle-même.** Le site cesse de la
DÉCLARER, pas de la tenir. Les contrastes mesurés dans les deux thèmes, les
tableaux titrés, le tableau de points sous chaque graphique, le formulaire
étiqueté, le lien d'évitement, le respect des « animations réduites » et le
contrôle daltonien restent, et restent vérifiés à chaque modification par la
vingtaine de tests de la section « accessibilité » de `test_web.py`. Une
promesse écrite se périme au premier changement de gabarit ; ces contrôles-là
non.

**Ce qui reste à l'éditeur du site d'accueil**, et qui est écrit dans
`docs/integration-partiliberalfrancais.md` : porter ces mentions de façon
qu'elles couvrent `/retraite/`. Le fichier donne la matière de la rubrique
« données personnelles » — tout est calculé dans le navigateur, rien n'est
envoyé, les paramètres vivent dans le fragment `#`, que le navigateur ne
transmet pas — et l'état d'accessibilité mesuré.

**Une réserve, laissée ouverte.** L'adresse GitHub Pages
(`g-pliberal.github.io/retraitecomptenotionelle/`) n'a pas de site parent pour
porter la partie légale. C'est une publication de travail du dépôt ; si elle
doit rester une adresse publique, ses mentions sont à poser ailleurs, ou
l'adresse à fermer. Le choix appartient à l'éditeur.

**Vérifié.** 896 tests, et les huit routes comparées caractère par caractère
entre Python et le portage.

---

### 33. Le temps qu'on perd à travailler sur le dépôt — `fait`

**La demande.** « C'est vraiment lent de travailler sur ce projet. » Chantier
d'outillage : il ne déplace aucun chiffre, il rend les autres actions moins
chères. Rien n'avait jamais été mesuré, alors on a commencé par là.

**Ce qui a été mesuré.** Suite complète, machine à quatre cœurs : **7 min 25**,
905 tests. Un profil de simulation partie de zéro : 1,55 s, dont 1,5 s
d'analyse YAML en Python pur. Chaque construction de contexte relisait
1,4 Mo de fiches — les mêmes neuf fichiers, à chaque fois. Et une session
neuve ne pouvait rien lancer du tout : ni pytest ni le paquet installés,
`python -m pytest` répondait « No module named pytest ».

**Ce qui a été fait.**

- *Le YAML n'est analysé qu'une fois.* `charger_yaml` mémorise l'arbre, indexé
  sur la signature du fichier (mtime et taille), et rend une copie profonde :
  l'appelant garde un dictionnaire librement modifiable, exactement comme
  avant, et un fichier modifié sur le disque est relu sans qu'on ait à vider
  quoi que ce soit. La copie coûte 4 ms là où l'analyse coûtait 400 ms.
- *Le chargeur C quand libyaml est là.* `yaml.safe_load` ne le choisit jamais
  de lui-même ; à contenu égal il lit huit fois plus vite (0,049 s contre
  0,406 s sur la plus grosse fiche). Repli silencieux sur le chargeur Python.
- *La suite se répartit sur les cœurs.* Greffon `pytest_parallele`, chargé par
  `addopts`. Il s'efface si `pytest-xdist` n'est pas installé, si l'appelant a
  déjà posé `-n`, si `PYTEST_SANS_XDIST` est mis, ou si l'on vise un fichier ou
  un cas précis — démarrer quatre processus pour un test coûte plus que de
  l'exécuter. Il fallait un greffon et non un `conftest.py` : les conftest sont
  chargés *par* le hook `pytest_load_initial_conftests`, donc trop tard.
- *Une session démarre en état de marche.* Un hook de démarrage installe
  `.[dev]`, pytest-xdist, et le PyYAML de PyPI quand celui de la distribution
  n'a pas libyaml. **Il n'est pas dans le dépôt** : une session Claude Code
  n'a pas le droit d'écrire sous `.claude/`, ni le fichier ni son inscription
  dans `settings.json`. Son texte est donné plus bas, à poser à la main.

**Ce que ça a déplacé.**

| | avant | après |
| --- | --- | --- |
| Suite complète | 7 min 25 | **35 s** (12,7×) |
| Suite en série, un seul cœur | 7 min 25 | 1 min 54 (3,9×) |
| Simulation, contexte neuf | 1,55 s | 0,078 s (20×) |
| Construction des témoins | 19,4 s | 13,3 s |

**Vérifié.** Les 905 tests passent, avant comme après. `construire_donnees.py`
reproduit `moteur/donnees.json` et `moteur/style.css` **octet pour octet** :
c'est la preuve que le cache et le chargeur C n'ont rien changé au fond. Les
quatre garde-fous du greffon ont été essayés un par un.

**Le hook, à poser à la main.** Écrire `.claude/hooks/session-start.sh`,
le rendre exécutable (`chmod +x`) :

```bash
#!/bin/bash
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" != "true" ] && exit 0
cd "${CLAUDE_PROJECT_DIR:-.}"
python -m pip install --quiet --disable-pip-version-check -e '.[dev]'
# PyYAML de PyPI plutôt que celui de la distribution : sa roue embarque
# libyaml, que `charger_yaml` préfère au chargeur Python. Celui de Debian ne
# se laisse pas désinstaller, d'où `--ignore-installed`, qui le masque.
python -c 'import yaml,sys; sys.exit(0 if yaml.__with_libyaml__ else 1)' \
  || python -m pip install --quiet --disable-pip-version-check \
       --ignore-installed --no-cache-dir PyYAML
```

puis l'inscrire dans `.claude/settings.json`, à côté des hooks Impeccable :

```json
"SessionStart": [
  { "hooks": [ { "type": "command",
                 "command": "\"${CLAUDE_PROJECT_DIR}/.claude/hooks/session-start.sh\"",
                 "timeout": 300 } ] }
]
```

**Second tour, une fois le YAML réglé.** Le profil ne montrait plus de
lecture de fichiers mais du calcul — et, dedans, du travail refait :

- *`SerieAnnuelle.brut` mémorise, et encadre par dichotomie.* Six millions
  d'appels, presque tous sur les mêmes années. L'interpolation balayait en
  outre toute la liste des années deux fois (`max(a for a in ... if a < annee)`)
  alors qu'elle est triée. La dichotomie a été vérifiée contre l'ancien calcul
  sur 71 865 encadrements : aucun écart.
- *`date_liquidation` et `date_naissance` deviennent des `cached_property`.*
  La première était recalculée **1 300 000 fois** par construction de témoins.
  Les champs dont elles dépendent ne sont jamais réaffectés après le
  constructeur — c'est déjà le contrat des autres `cached_property` de
  `Carriere`, et une recherche sur tout le dépôt le confirme.
- *Les séries annuelles et la table des quotients de mortalité sont mises en
  cache.* `quotients_periode.csv` fait vingt-cinq mille lignes et se relisait
  trente-cinq fois pour les seuls témoins. La table est partagée sans copie :
  tout ce qui la touche la lit (`in`, `.get`), ici comme dans `LoiMortalite`.
- *Le cache YAML garde la forme `pickle` plutôt que l'arbre.* La recharger est
  une copie neuve, trois fois plus rapide que `deepcopy` : c'est ce qui fait
  passer une simulation partie de zéro de 0,156 s à 0,078 s.
- *La fixture `page` des tests mémorise son rendu.* Une trentaine de tests
  demandent la même adresse, et `/cout` coûtait trois secondes et demie à
  chaque fois. Une page rendue est une chaîne : la partager ne peut pas faire
  communiquer deux tests.

**Ce qui reste.** La suite est au plafond du parallélisme : 35 s de temps réel
pour 2 min 16 de temps processeur sur quatre cœurs, soit 97 % d'occupation.
Le plancher est `test_les_temoins_du_portage_sont_a_jour` (14,3 s), qui est un
seul bloc : aucun nombre de cœurs ne descendra sous lui tant qu'il n'est pas
découpé. Descendre plus bas demanderait d'optimiser les boucles chaudes de
`scenarios/actuel.py` — le modèle de référence lui-même, à ne toucher qu'avec
les témoins comme garde-fou. Les stratégies de répartition de xdist ont été
essayées : `loadscope` est deux fois pire (95 s, un worker hérite de tout
`test_web.py`), `worksteal` équivalent, et sur-souscrire les cœurs dégrade.

---

### 34. Un test qui confronte les affirmations du site au modèle — `à faire`

**Pourquoi.** Ouverte par le retrait de la note « aucun droit repris »
(journal, septembre 2026). Elle a vécu deux jours en page d'accueil en
affirmant le contraire de ce que le programme fait, sur la même page, trois
fois. Rien ne pouvait l'arrêter : `tests/temoins/pages.json` FIGE le texte des
pages — il rend visible une modification, il ne valide aucune affirmation —, et
`tests/test_web.py` ne vérifie que des formulaires, des bornes, des adresses et
des chiffres. Ce que `inventaire.yaml`, `reformes.yaml` et `veille.yaml` ont
chacun — un test qui refuse l'oubli —, les affirmations des pages ne l'ont pas.
Or ce sont elles qu'on lit : un lecteur du site voit la phrase, pas le témoin.

**Les trois modes de panne, à traiter ensemble.**

1. *La phrase que le code dément.* Celle qui a été retirée. Il en reste au
   moins une, jumelle, dans le dépliant de transition
   (`web/pages.py`, `_programme_transition`) : « La bascule ne reprend aucun
   droit acquis et ne touche à aucune pension déjà versée », écrite QUATRE
   LIGNES au-dessus du tableau qui dit « Les droits déjà acquis sont figés,
   réduits à leur part contributive ». C'est la première à instruire.
2. *La phrase qu'une autre page dément.* L'accueil promet « L'écart se solde
   chaque année, au lieu de s'accumuler en silence » ; la page Coût déclare
   « Le coefficient d'équilibre n'est jamais appliqué ». Les deux sont exactes
   dans leur registre — l'une décrit le système proposé, l'autre le modèle qui
   le chiffre — et leur voisinage est un mensonge. C'est exactement le sujet de
   l'action 11, et le test dirait laquelle des deux bouge quand elle sera faite.
3. *La phrase vraie qui a pourri.* Un défaut de `config.py` qui se déplace, un
   régime qui entre au catalogue, un barème recertifié : la prose ne suit pas,
   parce que rien ne la convoque. L'action 31 a renuméroté les scénarios ; la
   suivante déplacera autre chose.

**La forme.** Un catalogue, `data/reference/site/affirmations.yaml`, et un test
qui l'exploite dans les deux sens — c'est la mécanique de `inventaire.yaml`,
qui a déjà fait ses preuves. Chaque entrée porte : `id` ; la page ; l'`extrait`
verbatim, assez long pour être retrouvé et assez court pour survivre à une
retouche de mise en page ; ce que la phrase `porte`, en une ligne ; et son
`etat` — `verifiee`, `contredite` (avec l'action qui la refermera), ou
`sans_portee` pour ce qui est de la rhétorique et non une affirmation sur le
modèle.

Le test fait trois choses :

- **L'extrait est encore là.** S'il a disparu du rendu, la phrase a été
  réécrite sans qu'on repasse par le catalogue : échec. C'est le garde-fou
  contre le mode de panne 3, et il ne coûte rien — les pages sont déjà rendues
  par la fixture `page`.
- **Le contrôle passe.** Chaque entrée `verifiee` nomme une fonction qui
  interroge le MODÈLE, pas le texte : « le taux du régime fusionné est le même
  pour tous les statuts après la bascule », « deux carrières de même capital
  notionnel rendent la même pension », « aucun avantage non contributif ne
  survit dans le compte ». Une entrée `contredite` est un test qui vérifie
  qu'elle l'est encore, et qui tombe le jour où l'action qui la refermait est
  faite — de sorte qu'on ne referme pas une action en oubliant la phrase.
- **Rien n'échappe au catalogue.** Toute phrase forte des pages — au premier
  jet, le contenu des `<strong>` de `web/pages.py`, une centaine — est soit
  dans le catalogue, soit déclarée `sans_portee`. C'est la clause
  d'exhaustivité, celle qui fait qu'une phrase NOUVELLE ne peut pas entrer sans
  qu'on ait dit ce qu'elle engage.

**Le piège à nommer d'avance.** Un catalogue qu'on remplit de `sans_portee`
pour faire passer la suite ne vaut rien. La limite est simple à écrire et à
tenir en relecture : est `sans_portee` ce qui ne peut pas être faux — un titre,
une invitation, une transition. Dès qu'une phrase affirme quelque chose sur ce
que le système FAIT, elle a un contrôle ou un `contredite` qui nomme son
action.

**Fichiers.** `data/reference/site/affirmations.yaml` (neuf) ; un
`tests/test_affirmations.py` (neuf) ; `web/pages.py` pour les phrases à
corriger au passage, et `moteur/js/pages.js` en regard ; les témoins.
Le portage JavaScript n'a pas à porter le test : le catalogue vise le texte,
et les deux moteurs rendent le même.

**Fin.** Le catalogue couvre les phrases fortes des six pages, la jumelle du
dépliant de transition est corrigée, et les deux contradictions connues
(étape 2 de la transition, écart soldé contre coefficient jamais appliqué) sont
dans le fichier avec l'action qui les referme — 24 pour l'une, 11 pour l'autre.

---

### 35. Les recettes et les dépenses du scénario 6, chiffrées toutes les deux — `en cours`

**Pourquoi.** Le scénario 6 est la proposition du dépôt, et c'est celui dont le
bilan est le moins bien tenu. Sa DÉPENSE réagit à ce qu'il change, parce que le
modèle recalcule les pensions ; sa RECETTE ne réagit à rien, parce que le
coefficient d'équilibre lui laisse les ressources du système actuel alors qu'il
remplace tous les taux par 18 %. Et la moitié de sa dépense financée par
l'impôt, la garantie vieillesse, ne pèse rien du tout dans la trajectoire. La
page Coût affiche donc, pour lui, un excédent qu'aucune des deux erreurs ne
contredit : elles vont toutes les deux dans le même sens.

**Ce que le modèle dit aujourd'hui, et qui fonde l'action.** Quatre mesures,
faites le 18 septembre 2026 sur `calculer_cout` aux paramètres par défaut.

1. *Le scénario 6 affiche un excédent moyen de +3,75 % du PIB sur 2026-2070*,
   contre −1,13 % pour le système actuel, et son coefficient d'équilibre vaut
   1,57 en 2025 et 1,53 en 2070 (0,99 et 0,84 pour le système actuel). Ces
   chiffres supposent qu'un système à 18 % encaisse ce qu'encaisse un système
   à 28 %.
2. *La part contributive des ressources de 2025 est de 322 Md€*, soit 10,8 %
   du PIB : 274 Md€ de cotisations (65,6 % des ressources) et 49 Md€ de
   contribution d'équilibre de l'État (11,7 %). Le reste — 64 Md€ d'impôts et
   taxes affectés, 16 Md€ de transferts, 8 Md€ de subventions d'équilibre —
   n'est pas cotisé, et un compte notionnel ne sait pas le créditer.
3. *La garantie vieillesse coûte zéro de 2030 à 2070* dans la trajectoire du
   modèle. Son rapport de masse vaut 8,8 · 10⁻⁶ en 2024 et exactement 0
   ensuite ; les 610 Md€ constants du cumul passé viennent tous de générations
   anciennes. La raison n'est pas l'âge, contrairement à ce que `limites.md`
   laissait entendre : cinq des treize cas types liquident bien à 65 ans ou
   plus. C'est le NIVEAU. Les deux seuls cas types qui tombent sous le plancher
   au scénario 6 — l'exploitant agricole à 674 € par mois, le carrière complète
   au SMIC à 797 € — partent à 64 et 62 ans, et le modèle ne les suit pas
   jusqu'à 65 ; les cinq qui partent après 65 ans sont tous au-dessus de 800 €.
   Le barème appliqué à la distribution réelle, lui, chiffre 33 à 59 Md€ par an.
4. *La dépense à laquelle on applique le rapport n'est pas du même périmètre
   que le rapport.* Le rapport est celui des droits DIRECTS des cas types ; la
   base est la dépense DREES du risque vieillesse-SURVIE, ou celle du COR, qui
   portent l'une et l'autre les droits dérivés. L'écart est dit dans
   « ce qui est délibérément en bas », il n'est pas corrigé.

**A. Faire réagir les recettes.** C'est le gros morceau, et il se fait sans
toucher aux moteurs de pension.

1. *Poser l'assiette en NIVEAU.* Aucune série du dépôt ne la porte :
   `masse_salariale.csv` ne donne que des variations, et sert à l'indexation.
   Il faut les salaires et traitements bruts de l'ensemble des branches (D11
   des comptes nationaux, déjà lu en niveau par `verifier_donnees.py`) et les
   revenus d'activité des non-salariés. Ordre de grandeur, à établir et non à
   reprendre : pour une assiette de 1 100 à 1 400 Md€, 18 % rendent 198 à
   252 Md€, contre les 322 Md€ contributifs de 2025. L'écart serait de 70 à
   125 Md€ par an, soit 2,4 à 4,2 points de PIB. Le taux implicite d'aujourd'hui
   sur cette même assiette large est de 23 à 29 %.
2. *Un rapport de RECETTES, symétrique du rapport de masses.* C'est la route
   propre, et elle réutilise ce qui existe : la grille des cas types donne déjà,
   année par année, la cotisation versée par chaque carrière — `compte.cotisations`
   porte l'assiette retenue et le montant. Le rapport de l'année est la somme
   des cotisations à 18 % sur la somme des cotisations aux taux réels, pondérée
   par les effectifs d'ÂGE ACTIF de l'INSEE et par les effectifs de COTISANTS
   par régime. Ancré sur les cotisations observées de la dernière année du COR,
   il donne la recette de chaque système comme `_avenir` donne sa dépense.
   L'avantage sur un calcul « 18 % contre 28 % » est décisif : l'assiette du
   taux unique est DÉPLAFONNÉE dans le modèle (`compte.py`, branche du régime
   fusionné), ce qui élargit l'assiette au moment où le taux baisse, et seul un
   rapport calculé sur les carrières capte les deux effets à la fois.
3. *Une série d'effectifs de cotisants.* `effectifs_retraites.csv` compte les
   retraités ; la pondération des recettes demande les cotisants. **Cette ligne
   affirmait que « la même enquête annuelle auprès des caisses les publie ».
   C'est faux, vérifié le 19 septembre 2026**, et ce qui suit est le relevé des
   impasses, pour qu'on ne les reparcoure pas.

   - **EACR de la DREES — non.** Ses deux classeurs portent douze feuilles :
     cadrage, prélèvements sociaux, âge conjoncturel, liquidants, droits
     directs, droits dérivés, minima, cumul, conditions de liquidation,
     coefficient Agirc-Arrco, invalidité, rentes AT-MP. C'est une enquête sur
     les RETRAITÉS de bout en bout.
   - **COR — non.** Les 153 feuilles de ses six classeurs 2026 ne portent
     qu'une figure de cotisants, la 1.13, en BASE 100 et pour les seuls
     régimes de la fonction publique.
   - **Open data DREES et data.gouv.fr — rien.** Aucun jeu de données ne
     répond à « cotisants ».
   - **CCSS, fiche « La compensation généralisée vieillesse » — la seule
     source, et elle est courte.** Elle donne l'effectif de cotisants régime
     par régime, au sens légal des articles `L. 134-1` et suivants. Trois
     trous : seul le rapport de mai 2026 rend ce tableau en TEXTE (les
     quatorze rapports 2013-2026 ont été passés au lecteur ; les autres le
     portent en image) ; la CANSSM, la CPRPSNCF et la CRPRATP sont intégrées
     au régime général à compter de l'exercice 2025, si bien que la SNCF
     n'existe que sur 2024 ; l'Ircantec et l'Agirc-Arrco sont absentes par
     construction, la compensation ne couvrant que les régimes de BASE.

   Reste donc un instantané de 2024 couvrant douze des treize cas types. Ce
   n'est pas rien : l'année de bord est reconduite jusqu'en 2070, et c'est
   exactement l'intervalle où la pondération sert, le rapport de recettes
   valant 1 par construction avant la bascule. Mais ce n'est pas une série.

   **Ce que ça change, mesuré et non supposé** : sous la convention du
   programme — 18 % de l'assiette MESURÉE —, la pondération des cas types ne
   déplace pas le solde du scénario 6 d'un millième. Passer des effectifs de
   caisse aux poids égaux le laisse à −0,88 %. Elle ne mord que sous la
   convention `rapport`, où elle vaut 0,14 point. L'urgence est donc faible,
   et c'est une raison de chercher une VRAIE source plutôt que de bâtir vite
   sur celle-là.

   **Passe de recherche large, 19 septembre 2026.** Les six pistes ont été
   parcourues. Il en sort DEUX sources, dont une que la passe précédente avait
   sous le nez : elle est dans les mêmes rapports CCSS, elle est en TEXTE, et
   elle est à l'unité près. Le reste est écarté, et l'est ici pour qu'on ne le
   reparcoure pas.

   - **CCSS, fiche 4.1, tableau 1 — « Effectifs de bénéficiaires et de
     cotisants des régimes de base hors régime général ».** C'est la source.
     Elle donne le cotisant caisse par caisse, à l'unité, et
     `scripts/fetch/lecture_pdf.py` la lit en texte — c'est là que la passe
     du 19 septembre s'était trompée : ce n'est pas la fiche « compensation
     généralisée vieillesse » (5.2), qui porte ses tableaux en image, mais
     une fiche voisine du même rapport. Elle paraît dans le rapport d'AUTOMNE
     depuis celui de septembre 2022, et chaque rapport arrête l'année
     précédente : quatre millésimes, **2021, 2022, 2023 et 2024**, un de plus
     à chaque automne. Les rapports de septembre 2018, 2020 et 2021 ont été
     ouverts et ne la portent pas ; la série commence donc en 2021 et ne
     remontera pas.

     Les cotisants de 2024, tels que le rapport d'octobre 2025 les écrit :
     CNRACL 2 151 694, SRE (fonctionnaires civils ET militaires ensemble)
     2 008 352, CNAVPL 882 980, MSA salariés 764 922, MSA exploitants
     420 847, CNIEG 133 091, SNCF 108 877, CNBF 78 047, CRPCEN 55 263, RATP
     39 334, ENIM 30 132, FSPOEIE 16 612, Banque de France 6 639, CANSSM 700.
     Quatre de ces lignes se recoupent avec la fiche 5 du même rapport, au
     cotisant près pour l'ENIM, la CRPCEN, la Banque de France et la CNBF, et
     à une unité près pour la CANSSM.

     Ce qu'elle ne donne pas, et il faut le dire : le RÉGIME GÉNÉRAL, que son
     titre exclut ; les régimes COMPLÉMENTAIRES, donc l'Ircantec et le RCI ;
     et le partage des fonctionnaires d'État entre CIVILS et MILITAIRES, que
     le SRE agrège en une ligne. Sur les treize cas types, elle en couvre
     donc cinq de plein droit — CNRACL, SNCF, CNIEG, MSA exploitants,
     CNAVPL — et une sixième à la condition de trancher le partage
     civils/militaires ailleurs.
     Avantage décisif sur l'instantané de 2024 qui tenait lieu de source :
     la SNCF y est en 2021, 2022, 2023 ET 2024, là où la compensation la perd
     à partir de 2025.

   - **PQE « Retraites » annexé au PLFSS — indicateur n° 18, puis n° 11 : «
     Nombre de cotisants à des régimes de retraite, par régime ».** La piste
     était bonne et la source existe : dix-huit régimes en milliers, source
     CCSS, et la seule qui donne à la fois le régime général ET le partage
     civils/militaires. Sa notion de cotisant est celle de l'article
     `D. 134-4` du code de la sécurité sociale — le cotisant actif de la
     compensation —, mais AMPUTÉE, par dérogation assumée, de ceux dont le
     FSV prend les cotisations en charge : ce n'est donc pas le décompte de
     la compensation, et les deux ne se raccordent pas (régime général à
     18,3 millions en 2012 pour le PQE, 24,3 millions en 2022 pour la
     compensation).

     Son défaut est l'âge. Les colonnes sont 1992, 1996, 2000, 2004, 2006,
     puis 2008 à 2012, une de plus par millésime ; l'édition de 2014 est la
     dernière à porter le tableau, celle de 2017 l'a remplacé par un simple
     ratio cotisants/retraités tous régimes, et le REPSS qui a succédé au PQE
     ne l'a pas repris. L'édition de 2016 n'a pas pu être tranchée : son PDF
     résiste au lecteur du dépôt, qui n'en sort que du binaire.
     Les éditions se prennent à
     `securite-sociale.fr/.../PLFSS/<an>/ANNEXE_1/PLFSS-<an>-ANNEXE_1-PQE-RETRAITE.pdf`,
     qui répond pour 2011 à 2014 et 2016 à 2018.

   - **Ircantec — open data de la Caisse des dépôts.** Le jeu
     `cotisantsircantec_typecoll_nbagents` donne l'effectif de cotisants par
     famille d'employeurs de 2014 à 2021, en API Opendatasoft, sommable :
     3 107 780 en 2014, 3 136 894 en 2021. Son voisin
     `actifs-cotisant-a-la-cnracl-selon-les-employeurs` fait de même pour la
     CNRACL de 2014 à 2022, mais sur une autre définition que la CCSS —
     2 494 306 en 2022 contre 2 189 791 pour la fiche 4.1 de 2021 —, et les
     deux ne doivent pas être cousues.
     **Au passage, la ligne « open data DREES et data.gouv.fr — rien » de la
     passe précédente est trop large** : data.gouv.fr porte bien des
     effectifs de cotisants, ceux de l'Ircantec, sous le nom de la Caisse des
     dépôts.

   Les trois pistes restantes sont écartées, et voici pourquoi :

   - **REPSS (successeur du PQE), indicateur 1.3, tableau 1 — trop grossier.**
     Il donne bien cotisations, prestations, cotisants et bénéficiaires régime
     par régime, et il est à jour (2025). Mais les cotisants y sont en
     MILLIONS À UNE DÉCIMALE : la SNCF, la RATP, la CNIEG, l'ENIM et la
     CRPCEN y valent toutes 0,0 ou 0,1. Inutilisable là où la pondération
     mord. L'indicateur 1.7 du même REPSS, lui, ne publie que des ratios par
     GROUPES de régimes. Sur le site, ces tableaux sont des images PNG ;
     c'est l'annexe PDF au PLACSS qui les porte en texte.
   - **Jaune budgétaire « Pensions » annexé au PLF — utile en appoint, pas
     comme série.** Ses effectifs sont en prose et à deux ou trois chiffres
     significatifs (CNRACL 2,2 M, SRE 1,63 M de civils et 0,32 M de
     militaires au 1er janvier 2024, Ircantec 3,2 M, FSPOEIE 0,09 M). Il a
     pourtant une vertu que personne d'autre n'a côté source actuelle : il
     SÉPARE les civils des militaires, ce que la fiche 4.1 agrège. C'est là
     qu'on ira chercher la clé de partage, pas la série.
   - **MSA, note annuelle « Compensation démographique » — agrège ce qu'on
     cherche.** Elle est annuelle, elle remonte à 2000, elle est en texte, et
     son tableau 1 réunit TOUS les régimes spéciaux en une seule ligne
     (5 460 118 en 2022). Elle ne sert que pour le régime général, les deux
     MSA et les indépendants.
   - **URSSAF Caisse nationale, DSN agrégées — hors champ par
     construction.** Vingt-cinq jeux répondent à « cotisant » sur
     `open.urssaf.fr` : comptes cotisants, travailleurs indépendants,
     exonérations, établissements du secteur privé. Aucun n'est ventilé par
     régime de retraite, et l'URSSAF ne recouvre ni la fonction publique, ni
     la SNCF, ni la CNIEG, ni la MSA, ni la CNAVPL. Écarté.
   - **EIC de la DREES — inaccessible, et ce n'est pas un agrégat.** C'est un
     échantillon anonymisé de carrières individuelles, diffusé par le CASD
     sous habilitation. Il ne publie pas d'effectifs de cotisants par régime.
     Écarté.
   - **Cour des comptes, RALFSS 2024, chapitre III sur la compensation — pas
     lu, et sans doute pas une source.** `ccomptes.fr` est injoignable depuis
     cet environnement : le relais ferme le tunnel au bout de onze secondes,
     sur quatre tentatives. Ce que la CCSS en cite et ce qu'en disent les
     résumés converge : c'est une CRITIQUE du décompte — effectifs de la MSA
     salariés estimés sur des moyennes plutôt que relevés au 1er janvier,
     CNAVPL qui déduit les radiations rétroactives sans ajouter les
     affiliations rétroactives —, pas un tableau. À reprendre si le dépôt
     s'appuie un jour sur la compensation, parce qu'il dit alors ce que vaut
     le chiffre ; pas pour y trouver la série.

   **Seconde passe, 19 septembre 2026 : recouper, et projeter.** La première
   passe cherchait UNE source ; celle-ci en cherche PLUSIEURS, pour qu'elles se
   contredisent utilement. Elle en ajoute trois, et elle tranche une question
   que la première laissait ouverte : de QUOI la fiche 4.1 est-elle le
   décompte ?

   - **Cnav, abrégé statistique de la branche retraite, chapitre 07 — « Les
     cotisants selon les régimes participant à la compensation ».** Il porte
     la table de compensation ENTIÈRE, **régime général compris**, à l'unité
     et en texte, avec sa source en toutes lettres : « Direction de la
     sécurité sociale pour la commission de compensation ». Il comble donc
     exactement le trou de la fiche 4.1. Un millésime par édition, au 1er
     juillet de l'année N−2 : l'édition 2023 donne 2021, la 2024 donne 2022,
     la 2025 donne 2023. Au 1er juillet 2023 : régime général 23 780 528
     (dont 21 034 526 salariés et 2 746 002 indépendants), collectivités
     locales 2 259 996, fonctionnaires civils et militaires 1 854 542,
     professions libérales y compris CNBF 922 442, salariés agricoles
     758 344, exploitants agricoles 421 381, CNIEG 132 744, SNCF 112 878,
     CRPCEN 60 303, RATP 41 064, ENIM 24 800, ouvriers d'État 17 538, Banque
     de France 7 038, mines 773 — total 30 410 230.

   - **CNRACL, recueil statistique, table I.1.3 — la série longue d'une
     caisse.** « Populations cotisante et pensionnée (moyenne annuelle) »,
     2012 à 2022, à l'unité : 2 171 826 en 2012, 2 189 791 en 2021,
     2 188 201 en 2022. C'est onze ans là où la CCSS en donne quatre, et
     c'est la preuve que la piste « rapports annuels de chaque caisse » est
     productive : ce qu'on a fait pour la CNRACL, on peut le faire pour les
     douze autres.

   - **PLFSS, annexe 1 « Présentation des régimes obligatoires de base » —
     troisième véhicule du MÊME tableau.** Son tableau 2 est mot pour mot
     celui de la fiche 4.1. Il ne sert donc pas à recouper, seulement à
     confirmer que le tableau est déposé devant le Parlement — et il y est en
     IMAGE, quand la CCSS le porte en texte. C'est la CCSS qu'on lit.

   **Ce que le recoupement établit, et c'est le résultat de la passe.** Les
   deux vecteurs ne comptent PAS la même chose, et on sait maintenant lequel
   compte quoi. Pour 2021, quatre lignes coïncident au COTISANT PRÈS — MSA
   salariés 714 686, RATP 42 444, Banque de France 7 852, mines 1 027 — et les
   autres s'écartent : CNIEG −2,7 %, exploitants agricoles −1,9 %, ENIM
   −3,2 %, CRPCEN −3,4 %, SRE −5,8 %, SNCF +0,8 %. L'explication est venue du
   recueil CNRACL : sa moyenne annuelle 2021, 2 189 791, est **exactement** le
   chiffre de la fiche 4.1, quand la compensation écrit 2 206 638 au 1er
   juillet. Donc :

   - la **fiche 4.1 de la CCSS** est le décompte que CHAQUE RÉGIME déclare à
     la DSS, sur son propre champ et sa propre date ;
   - le **chapitre 07 de l'abrégé Cnav** est le décompte de la COMMISSION DE
     COMPENSATION, au 1er juillet, France métropolitaine, notion de l'article
     `D. 134-4`.

   Les petits régimes donnent le même nombre aux deux, n'en ayant qu'un ; les
   gros divergent de un à six pour cent. **Aucune des deux n'est fausse, et
   c'est pourquoi il faut en choisir une et l'écrire** — pas les mélanger
   ligne à ligne, ce qui ferait un tableau qu'aucune source ne signe.

   **Côté projections, le COR donne ce qu'il faut, et en classeur.** La passe
   précédente avait écarté le COR sur la question de l'HISTORIQUE, ce qui
   restait juste ; sur la PROJECTION, il est la seule source publique, et ses
   `.xlsx` sont lisibles par `scripts/fetch/lecture_xlsx.py` :

   - **Figure 1.13** (classeur `Donnees_RA2026_P1.xlsx`) — « Évolution des
     effectifs cotisants aux régimes de la fonction publique », base 100 en
     2025, **de 2019 à 2070**, quatre séries : FPE civils et militaires,
     FPT + FPH (donc CNRACL), Ircantec, ensemble. Appliqué à un NIVEAU de
     2025 pris à la CCSS ou à la Cnav, cet indice donne des effectifs
     projetés. Sources : Direction du budget, Ircantec, hypothèses COR 2026.
   - **Figure 2.7** (classeur `Donnees_RA2026_P2.xlsx`) — ratio
     cotisants/retraités projeté année par année **de 2025 à 2070** pour la
     CNAV, la FPE, la CNRACL et l'Agirc-Arrco. Croisé avec
     `effectifs_retraites.csv`, il redonne des cotisants.
   - Les figures 2.6, 2.12 et 2.15 ventilent dépenses et soldes par GROUPES
     de régimes — Lura, FPE, CNRACL, non-salariés base, régimes spéciaux,
     complémentaires —, ce qui est la maille à laquelle le COR raisonne.

   Ses hypothèses sont explicites et il faut les reprendre avec les chiffres :
   les effectifs de la fonction publique viennent de la Direction du budget et
   suivent, après 2037, la population active globale ; les régimes spéciaux
   intègrent les fermetures de la réforme de 2023 (CRPCEN, Banque de France,
   CNIEG, RATP) et, pour la SNCF et la RATP, le basculement de cotisants vers
   le privé qu'entraîne l'ouverture à la concurrence ; les régimes de
   non-salariés ont communiqué leurs évolutions en 2024.

   **Troisième passe, 19 septembre 2026 : les rapports annuels des caisses, et
   ce qu'ils ont mené à trouver.** La piste « rapports annuels de chaque
   caisse » a été parcourue caisse par caisse. Elle donne trois séries longues,
   elle en ferme une, et elle a mené — par la fiche que le COR consacre à la
   SNCF — à la source qui rend toutes les autres secondaires.

   - **COR, « Compléments du rapport annuel 2024 : projections détaillées par
     régime » — LA source, et elle n'était dans aucune des listes.** Vingt-deux
     fiches, une par régime, à présentation harmonisée, et surtout **un seul
     classeur**, `Données_régimes_publi_V2.xlsx`, qui porte **vingt-quatre
     feuilles, une par régime**, chacune avec un bloc « Effectifs de cotisants
     en millions » ventilé Femmes / Hommes / **Ensemble**, historique ET
     projeté **jusqu'en 2070**. `lecture_xlsx.py` le lit tel quel.

     Il couvre **les treize caisses des cas types**, Ircantec et RCI comprises
     — les deux que la CCSS rate par construction. En 2023, puis en 2070 :
     CNAV 22 257 775 → 23 596 332 ; CNRACL 2 168 137 → 2 114 975 ; FPE
     2 041 199 → 1 893 125 ; Ircantec 3 169 028 → 3 143 714 ; RCI 1 707 103 →
     1 855 338 ; CNAVPL 980 098 → 646 814 ; MSA exploitants 432 402 →
     299 168 ; CNIEG 136 287 → 51 ; SNCF 112 232 → 0 ; ENIM 30 169 → 21 806.
     Les régimes fermés par la réforme de 2023 s'éteignent bien dans la
     projection, ce qu'aucune reconduction d'effectifs de retraités ne saurait
     imiter.

     **Trois pièges, mesurés :** les feuilles CRPCEN et CRPNPAC portent des
     UNITÉS sous un en-tête qui annonce des millions (CRPCEN 60 378 cotisants
     en 2023, à rapprocher des 60 303 de la Cnav) ; l'année de départ varie
     d'une feuille à l'autre (2010 pour la plupart, 2015 pour la FPE, 2019 pour
     le RCI, 2023 pour la CNRACL et la CNBF, 2024 pour le FSPOEIE) ; et la FPE
     reste d'un seul tenant, civils et militaires confondus — le partage se
     prend au Jaune « Pensions », qui est toujours le seul à le donner.

     **Son millésime, vérifié le 19 septembre 2026, et c'est une réserve
     sérieuse.** Le classeur n'existe qu'en UNE version, celle du rapport de
     juin 2024 : son propre sommaire l'écrit — « Complément du rapport annuel
     du COR - juin 2024 » —, ses métadonnées le datent du 10 juillet 2024,
     révisé le 10 février 2025, et l'en-tête `Last-Modified` du serveur, qui
     affiche avril 2026, ne reflète qu'une remise en ligne. **Il n'existe pas
     de compléments par régime du millésime 2026.** Quatre contrôles le
     disent : l'index des fiches du COR, sur toutes ses pages, ne liste que
     ceux de 2024 ; la page du rapport de juin 2026 n'offre que ses six
     classeurs de chapitres et aucune fiche de régime ; les chemins
     `2025-06`, `2025-07` et `2026-06` à `2026-09` répondent 404 pour la fiche
     CNRACL comme pour le classeur ; et le rapport 2026 lui-même, s'il
     confirme bâtir « des hypothèses plus fines, notamment celles concernant
     les effectifs cotisants […] de chaque régime », n'annonce nulle part leur
     publication. Le rapport 2026 date du 11 juin : trois mois ont passé, là
     où les fiches de 2024 étaient parues trois semaines après le leur.

     **Ce que cette réserve interdit.** Les effectifs par régime du classeur
     sont ancrés sur 2023 et sur l'exercice de projection de juin 2024 ; les
     figures 1.13 et 2.7 du rapport 2026, elles, portent les hypothèses COR
     2026. **Les mélanger reviendrait à coudre deux exercices de projection**,
     exactement la faute que la deuxième passe interdit sur les décomptes.
     Concrètement : pour la FPE, la CNRACL, l'Ircantec, la CNAV et
     l'Agirc-Arrco, un millésime 2026 existe et c'est lui qu'on prend ; pour
     les neuf autres caisses, seul l'exercice de 2024 est publié, et il faut
     l'écrire à côté du chiffre.

     **Le millésime 2025 n'existe pas davantage — mais il a laissé autre
     chose.** Vérifié le 19 septembre 2026 : la page du rapport de juin 2025
     n'offre aucune fiche de régime ni classeur par régime. Elle porte en
     revanche une rubrique que celle de 2026 n'a PAS, « Hypothèses
     sous-jacentes au rapport », et sous elle
     `hypo_cotisants_chômage_2025.xlsx`, mis à jour le 5 mai 2025, qui est un
     complément par régime au rabais mais réel :

     - ses onglets `Chô_5%`, `Chô_7%` et `Chô_10%` déclinent **l'emploi par
       régime**, en niveau pour l'année de base et en évolution ensuite,
       jusqu'en 2070, pour chaque hypothèse de chômage — Agirc-Arrco,
       Ircantec, CRPNPAC, auto-entrepreneurs SSI et professions libérales,
       entre autres ;
     - ses onglets `FPE` et `CNRACL` donnent des NIVEAUX, et mieux ventilés
       que partout ailleurs : la FPE y sépare La Poste et Orange du reste
       (2 005 560 en 2024, dont 59 120), la CNRACL y sépare FPT et FPH ;
     - son onglet `CER` porte la part des cotisants en cumul emploi-retraite,
       par régime.

     Le même millésime publie `Données_complémentaires_RA2025.xlsx`, dont
     l'onglet `Cotisants_Retraités` donne les cotisants TOUS RÉGIMES de 2000 à
     2070 sous cinq variantes. La page de juin 2026 n'a ni l'un ni l'autre :
     elle se limite à ses six classeurs de chapitres.

     **Et ce classeur 2025 referme la boucle du recoupement.** Sa CNRACL de
     2021 vaut 2 189 790,76 — quand la fiche 4.1 de la CCSS écrit 2 189 791 et
     le recueil de la caisse 2 189 791. Trois véhicules, le même nombre à
     l'unité : la CNRACL du COR EST la moyenne annuelle que la caisse déclare,
     ce que la deuxième passe avait déduit d'un seul rapprochement et qui est
     maintenant établi sur trois.

     Le tableau des millésimes disponibles est donc celui-ci : **2024**, les
     compléments par régime complets, vingt-deux fiches et un classeur à
     vingt-quatre feuilles ; **2025**, pas de compléments, mais des hypothèses
     de cotisants par régime, en niveau pour la FPE et la CNRACL seulement ;
     **2026**, ni l'un ni l'autre, et seulement les figures 1.13 et 2.7 des
     classeurs de chapitres.

   - **Cnav, abrégé statistique, chapitre 01 — soixante ans de régime
     général.** « Évolution du nombre de cotisants actifs occupés et de
     retraités du régime général et rapport démographique **depuis 1963** » :
     2 479 205 cotisants en 1963, 9 700 735 en 2000, 14 916 011 en 2023. La
     table porte DEUX colonnes de cotisants, celle du lieu de résidence et
     celle du lieu de travail, avec la rétropolation 2010-2014 qui les
     raccorde, et elle dit sa source : « commission de compensation de
     décembre, résultats définitifs ».

   - **CNAVPL, recueil statistique — soixante-quinze ans, et trois notions dans
     la même caisse.** Le tableau « Ensemble des sections (historique) » donne
     les cotisants réels de **1950 à 2025** : 103 262 en 1950, 400 894 en 1995,
     866 581 en 2025 ; et le recueil les ventile par section professionnelle
     (CARPIMKO 253 961, CIPAV 168 613, CARMF 125 952…). Le même document écrit
     par ailleurs 839 824 « cotisants compensables » en 2024. Trois chiffres,
     trois notions, une seule caisse : cotisants réels, cotisants
     compensables, et ce que la CCSS retient (882 980 en 2024). **C'est
     l'illustration la plus nette de ce que la deuxième passe avait établi**, et
     le dépôt n'a pas le droit de les mélanger.

   - **CNIEG, annuaire statistique — publié, annuel, et illisible.** Les
     millésimes 2017 à 2024 existent. Le lecteur du dépôt n'en tire que TROIS
     lignes chiffrées sur 1 893 : tout y est en image. C'est le seul annuaire
     de caisse rencontré dans ce cas, et il n'y a pas à insister — le classeur
     du COR donne la CNIEG, et la CCSS aussi.

   - **CPRPSNCF — site injoignable depuis cet environnement.** Le proxy refuse
     le CONNECT vers `cprpsncf.fr` (502, `connect_rejected`). Sans objet : la
     fiche CPRPF du COR couvre le régime, et mieux, puisqu'elle le projette.

   **Le recoupement à trois voix, sur 2023.** Avec le COR, la CCSS et la Cnav
   sur la même année, on peut enfin mesurer la dispersion :

   | caisse | COR | CCSS 4.1 | Cnav 1/7 | étendue |
   |---|---|---|---|---|
   | FPE | 2 041 199 | 2 041 020 | 1 854 542 | +0,01 % puis −9 % |
   | SNCF | 112 232 | 112 621 | 112 878 | 0,6 % |
   | CNIEG | 136 287 | 135 775 | 132 744 | 2,7 % |
   | MSA exploitants | 432 402 | 429 423 | 421 381 | 2,6 % |
   | ENIM | 30 169 | 29 879 | 24 800 | 22 % |
   | CNAVPL | 980 098 | 913 831 | 877 881 (recueil) | 12 % |

   Ce qu'il faut en retenir : **le COR et la CCSS coïncident presque
   parfaitement sur la FPE** — 179 cotisants d'écart sur deux millions, ce qui
   dit que le COR reprend la déclaration du régime —, **et la dispersion
   explose sur les caisses où les notions divergent**, l'ENIM et la CNAVPL au
   premier chef. Une pondération bâtie sur ces effectifs doit donc citer SA
   source ligne par ligne, et le classeur du COR est le seul qui en offre une
   seule pour les treize.

   **Ce qu'une session qui code devrait faire**, si elle reprend ce point :
   partir de la fiche 4.1 (2021-2024, à l'unité, script possible avec le
   téléchargeur de rapports CCSS que `ccss_transferts_retraite.py` porte
   déjà), compléter le régime général et l'Ircantec par leurs propres
   sources, et NE PAS coudre le PQE au bout : ses deux définitions ne se
   raccordent pas, et quatre années à l'unité près valent mieux qu'une série
   longue dont la moitié compte autre chose. L'urgence reste faible — la
   mesure du 19 septembre tient : sous la convention du programme, la
   pondération ne déplace pas le solde du scénario 6 d'un millième.
4. *Dire ce que le programme fait des ressources non cotisées, et ne pas le
   décider à sa place.* Les 18 % remplacent-ils aussi les 64 Md€ d'impôts et
   taxes affectés, qui compensent pour l'essentiel des allègements de
   cotisations patronales ? Et les subventions d'équilibre aux régimes en
   extinction, qui survivent à toute réforme le temps que leurs pensionnés
   s'éteignent ? Trois variantes à poser en paramètre et à afficher côte à
   côte : les 18 % seuls, les 18 % plus la fiscalité affectée d'aujourd'hui,
   les 18 % plus la fiscalité et les subventions d'extinction. Le dépôt chiffre
   les trois ; le choix est politique.
5. *Sortir les cinq points capitalisés de la recette.* Le pilier obligatoire
   prélève 5 % sur la même assiette et ne finance pas la répartition. L'effort
   contributif du scénario 6 est donc de 23 %, sa recette de système de 18 %,
   et la page doit porter les deux nombres sans les confondre.

**Ce que le volet A a déplacé, au 18 septembre 2026.** Le point 2 est fait, et
c'est celui qui portait le résultat. La page Coût n'affiche plus, pour le
scénario 6, les recettes d'un système dont il remplace tous les taux.

- *Le rapport de recettes existe, et il est bâti sur la grille des cas types*
  (`cout.py`, `_masses_cotisations` et `_rapports_recettes`, portés en regard
  dans `moteur/js/cout.js`). La recette de chaque système est celle du COR,
  dont la part COTISÉE — 77 % du total — est multipliée par ce rapport.
- *Le dénominateur n'est pas celui qu'on croyait.* Prendre le compte du
  scénario 4 pour « ce que le droit en vigueur prélève » était faux : après la
  bascule, ce compte fusionne les régimes et prélève le taux du statut pivot
  privé pour TOUT LE MONDE — 25,8 %, fonctionnaires compris. C'était déjà une
  réforme, et le rapport ne comparait alors que deux réformes entre elles. Le
  dénominateur est désormais le même compte SANS régime fusionné, c'est-à-dire
  ce que chaque régime prélèverait jusqu'en 2070 si rien ne changeait : 25,8 %
  pour un salarié du privé, 42,7 % pour un fonctionnaire de catégorie active,
  47,9 % pour un agent de conduite, 76,6 % pour un fonctionnaire sédentaire.
  Un compte de plus par couple, soit un sixième de calcul en plus sur la grille.
- *Le rapport vaut 0,63*, stable dès deux ans après la bascule, soit un taux
  moyen implicite de **28,7 %**. Le contrôle externe était à trouver, et il
  existe : la figure 3.1 du rapport annuel du COR publie le taux de cotisation
  retraite d'un salarié non cadre du privé sous le plafond, parts salariale et
  employeur, de 1940 à 2025 — **27,9 %** en 2025. Huit dixièmes de point d'écart
  sur une grille qui mêle à ce salarié des fonctionnaires et des non-salariés.
  La même figure dit autre chose, qui n'était pas cherché : le taux moyen sur
  toute la carrière de la génération 1940 était de **18,97 %**, c'est-à-dire ce
  que la proposition demande.
- *Ce que ça déplace.* Solde moyen 2026-2070 du scénario 6 : de **+3,75 %** du
  PIB à **−0,09 %**. Coefficient de 2070 : de **1,53** à **1,07**. Solde de
  2025 : inchangé, la bascule n'ayant pas eu lieu. Le scénario reste très
  au-dessus du système actuel (−1,13 %), et son excédent devient un équilibre.
  Aucun autre chiffre du dépôt ne bouge : pas une pension, pas un rapport de
  masses, pas un témoin de simulation.
- *Un effet de bord de la grille, borné et écrit.* Chaque génération y
  représente cinq classes d'âge, et la cohorte née deux ans plus tôt verse
  l'année `t` ce que la génération de la grille verse en `t + 2`. Deux ans avant
  la bascule, ce `t + 2` était déjà à 18 % : la recette de 2025 baissait pour
  une réforme qui n'avait pas eu lieu. Le rapport est donc écrit à un avant la
  bascule plutôt que calculé. Après elle, le même décalage joue en sens inverse
  et s'éteint en deux ans.
- *Une réserve nouvelle, de sens opposé, et chiffrable.* Le modèle porte au
  compte le taux qui ACQUIERT des droits, non tout ce qui rentre : la
  contribution d'équilibre général et la contribution d'équilibre technique de
  l'Agirc-Arrco n'ouvrent aucun droit et sont pourtant encaissées. Sous le
  plafond, la première seule s'applique, à 2,15 % : et c'est exactement ce qui
  manque au modèle, dont le taux de 25,83 % plus ces 2,15 donnent 27,98 quand
  le COR publie 27,89 pour le même salarié. La seconde, 0,35 %, n'est due que
  par ceux dont la rémunération dépasse le plafond. Les compter abaisserait encore le
  rapport. Le chiffre affiché est donc favorable au scénario 6, et le refermer
  demande une série de taux ENCAISSÉS à côté de celle des taux qui acquièrent.

**Le point 1 a été instruit le 19 septembre 2026, et il n'a pas donné ce qu'on
attendait de lui : il n'infirme pas le rapport, il l'ENCADRE.**

- *L'assiette existe, et deux routes la donnent à 3,8 % près.* Route INSEE : les
  salaires et traitements bruts (D11, comptes nationaux base 2020, idbank
  011785411, déjà récupéré par `insee_bdm.py` mais employé pour ses seules
  variations) plus le revenu mixte brut des ménages, soit 1 112 + 138 =
  **1 249 Md€ en 2024**. Route COR : le tableau 2.11 du rapport annuel chiffre
  l'ajustement nécessaire à l'équilibre DEUX FOIS, en pour-cent de la masse de
  pension et en points de taux de prélèvement ; le rapport des deux donne
  l'assiette, **3,19 fois la masse de pension**, soit 1 298 Md€. Les deux routes
  sont indépendantes — l'une ne doit rien au COR, l'autre rien à l'INSEE — et
  elles s'écartent de 3,9 %. L'assiette vaut **42,5 % du PIB**, remarquablement
  stable de 2016 à 2024.
- *Le taux réellement encaissé est plus bas que le taux légal, et l'écart est
  l'exonération.* Sur cette assiette, le système encaisse **32,4 points** de
  ressources en 2024, dont **24,9 points** de cotisations et de contribution
  d'équilibre. Or le taux légal d'un salarié type est de 28 à 29 %. Les
  quatre points d'écart ont deux causes que le dépôt ne sait pas encore
  départager : l'allègement général, que l'État compense par l'impôt et qui
  reparaît plus bas dans les 4,6 points d'impôts et taxes affectés, et la
  composition de la grille, pondérée par les retraités, qui surreprésente les
  régimes à taux élevés. `limites.md` décrit le premier, article par article ;
  le point 3 du volet A refermerait le second.
- *Ce que le modèle suppose sans le dire.* Appliquer le rapport 0,62 aux
  ressources OBSERVÉES revient à prêter au taux de 18 % la même déperdition
  qu'au système actuel : le modèle fait rentrer **15,5 % de l'assiette là où la
  proposition en affiche 18**. C'est l'hypothèse « à structure d'exonérations
  inchangée ». Elle est défendable, elle n'est pas neutre, et elle n'était
  écrite nulle part.
- *Les trois variantes, et le modèle est au milieu.* En points d'assiette, et
  au titre de 2024 : à exonérations inchangées, ce que le modèle affiche,
  **22,94** ; 18 % prélevés à plat sans exonération, impôts affectés conservés,
  **25,48** ; 18 % à plat avec suppression des impôts qui compensaient les
  exonérations, **20,92**. Soit de 64 % à 79 % des ressources d'aujourd'hui,
  le modèle à 71 %. Traduit en solde moyen, la fourchette fait environ un point
  de PIB de part et d'autre du −0,09 % affiché. **C'est l'incertitude réelle de
  l'exercice, et elle est plus grande que tout ce que la page dit par
  ailleurs.**
- *Les deux séries sont certifiées depuis le 19 septembre 2026*, chez leur
  producteur et non chez un repreneur :
  `data/reference/macro/assiette_activite.csv`, 154 valeurs de 1949 à 2025,
  deux postes. Le niveau du D11 ne demandait qu'une source de plus dans
  `verifier_donnees.py`, le fichier brut étant déjà téléchargé. Le revenu mixte
  a demandé de chercher une porte : la banque de données macroéconomiques ne le
  publie pas — ses comptes de branche ne donnent qu'un agrégat « excédent
  d'exploitation / revenu mixte » qui mêle le profit des sociétés au revenu des
  entrepreneurs individuels, et son jeu de comptes des secteurs institutionnels
  ne sert que cinq ratios. **Le tableau économique d'ensemble exposé par
  Melodi, lui, le porte** (`DD_CNA_TEE`, opération B3G, secteur S14, 1949-2025),
  et `scripts/fetch/insee_revenu_mixte.py` le récupère. Rester chez le
  producteur n'était pas une coquetterie : Eurostat rediffuse la même grandeur
  sous `nasa_10_nf_tr`, et les deux millésimes s'écartent de 0,8 % sur 2023.
- *Le point 4 est tranché par le programme, et le modèle sait le calculer.*
  Le 19 septembre 2026, le Parti libéral français a posé sa convention : les
  employeurs versent la cotisation entière, l'État leur rembourse l'allègement
  par l'impôt, et ce remboursement est une aide à l'activité économique, non
  une recette de retraite. `calculer_cout(convention_recette="assiette")`
  applique donc les 18 % à l'assiette mesurée et retire les impôts et taxes
  affectés ; `"rapport"` garde l'ancienne, comme `ponderation="egale"` garde
  l'ancienne pondération. Ce que cela déplace : le solde moyen 2026-2070 du
  scénario 6 passe de **−0,09 %** du PIB à **−1,28 %**, son coefficient de 2040
  de 0,94 à 0,83, et il ne repasse plus jamais à l'équilibre — contre −1,13 %
  pour le système actuel. **Sous sa propre convention, la proposition est
  légèrement moins bien financée que le système qu'elle remplace.**
- *La ventilation du poste a été cherchée, et trouvée — pas où on l'attendait,
  et pas ce qu'on attendait.* Elle n'est pas dans les annexes du projet de loi
  de financement : elle est dans le rapport à la Commission des comptes de la
  Sécurité sociale, que `scripts/fetch/ccss_transferts_retraite.py` télécharge
  déjà, au compte de la CNAV et à celui du Fonds de solidarité vieillesse.
  Deux résultats, et le premier démolit l'argument de départ.

  **La compensation des allègements n'est pas dans ce poste.** Le compte de la
  CNAV ne porte aucune ligne de TVA, et c'est par la TVA que l'État compense
  les allègements — elle ferait 20 % des produits nets de la branche MALADIE
  en 2025. Retirer ce poste au nom de la compensation serait retirer la
  mauvaise somme pour la bonne raison.

  **Ce qu'il porte est de la CSG de solidarité, et elle, elle doit sortir.**
  Sur 57,1 Md€ d'impôts et taxes affectés en 2024, **21,7 — 38 % — sont les
  ressources du Fonds de solidarité vieillesse**, qui ne sert qu'à deux
  choses : prendre en charge des cotisations pour des périodes non travaillées
  (15,7 Md€, dont 13,0 au titre du chômage) et payer le minimum vieillesse
  (4,2 Md€). Aucun scénario notionnel ne sert l'un ni l'autre. C'est mot pour
  mot la règle déjà appliquée à la CNAF et à l'Unédic, et le fonds y échappait
  parce que sa recette entre dans les comptes sous un autre nom.

  **Ce que cela donne** : en retirant la seule CSG du fonds, le solde moyen
  2026-2070 du scénario 6 est de **−0,02 % du PIB** — l'équilibre à un
  centième près, contre −1,13 % pour le système actuel. Les trois lectures
  s'ordonnent : −1,28 % en retirant tout le poste, −0,02 % en n'en retirant
  que la solidarité, +0,76 % en n'en retirant rien.

- *Le fonds est entré dans le retrait le 19 septembre 2026.* Deux postes de
  plus dans `transferts_retraite.csv` — les cotisations qu'il prend en charge
  et les prestations qu'il verse —, lus dans les mêmes rapports et par le même
  script que ceux de la CNAF et de l'Unédic, de 2011 à 2025, et un organisme de
  plus dans `equilibre.py`. Ce n'était pas une convention nouvelle : c'est
  l'extension d'une règle existante à un fonds qu'elle avait manqué parce que
  sa recette arrive par l'impôt et non par un transfert.

  **Ce que le lecteur de PDF a coûté au passage.** Les prises en charge du
  fonds étaient illisibles une année sur deux : depuis 2024, les tableaux des
  comptes de la CNAV portent des colonnes « pro forma » qu'aucun en-tête ne
  déclare, et les cellules vides s'y écrivent « -- ». Deux tolérances ont été
  posées dans `_valeurs` — sauter une cellule vide, lire une ligne trop longue
  sur son préfixe — après avoir vérifié qu'elles ne déplacent aucune des
  quatre séries déjà certifiées, d'un euro.

  **Ce que ça déplace.** Le retrait total passe d'un demi-point de PIB à
  **1,17 %**, dont 0,67 pour le seul fonds. Les cinq scénarios notionnels
  perdent 0,64 point de solde moyen : le 6 passe de −0,09 % à **−0,73 %**, le 5
  de +0,61 % à −0,04 %, le 3 de +2,43 % à +1,79 %. Le système actuel ne bouge
  pas : il encaisse tout, et son solde reste celui du COR.

- *La page affiche la convention du programme depuis le 19 septembre 2026.*
  Le défaut de `calculer_cout` est passé à `assiette`, le portage JavaScript a
  reçu son `AssietteActivite` et les deux champs que le solde annuel porte en
  plus, le paquet de données transporte les deux postes de l'assiette, et les
  deux notes de la page qui expliquaient l'ancienne convention ont été
  réécrites. Le scénario 6 affiche donc **+0,12 %** de solde moyen 2026-2070 et
  un coefficient de 1,10 en 2070, contre −1,13 % pour le système actuel.
  L'ancienne convention reste calculable et mesurée, comme
  `ponderation="egale"`.
- *Ce qui reste du volet A* : la série d'effectifs de COTISANTS (point 3), qui
  refermerait l'autre moitié de l'écart entre taux légal et taux encaissé, et
  la ligne des cinq points capitalisés (point 5), pour que la page distingue
  l'effort contributif de 23 % de la recette de système de 18 %.

**Ce qui reste du volet A** : la certification de l'assiette et les trois
variantes ci-dessus (points 1 et 4, désormais un seul chantier) ; la série d'effectifs de COTISANTS
(point 3), qui remplacerait la pondération par les retraités ; et la ligne des
cinq points capitalisés (point 5). Deux sources repérées en chemin, chez le COR et dans le
classeur que `scripts/fetch/cor_comptes_retraite.py` télécharge déjà : la
figure 3.1, taux de cotisation d'un non-cadre du privé de 1940 à 2025, à
certifier ; et le tableau 2.11, qui donne l'équivalence du COR entre un point de
taux de prélèvement et un pour-cent de masse de pension — 2,76 points contre
8,6 % à l'horizon 2070, sur le même champ que nos comptes.

**B. Faire entrer la garantie vieillesse dans la trajectoire.**

*Le point 2 est fait le 19 septembre 2026, et il a emporté deux autres
décisions.* La garantie est désormais servie à 65 ans à qui a liquidé plus tôt :
avant 65 ans on ne touche pas le minimum vieillesse, à partir de 65 ans on le
touche. Le complément est calculé dans tous les cas et n'entre dans la pension
affichée que s'il est dû dès le départ ; `GarantieVieillesse` porte
`annee_ouverture`, `differee` et `servie_a_la_liquidation`, et la page de
simulation dit l'année d'ouverture et le montant à venir. L'égalité entre le
complément calculé au départ et celui qui sera servi trois ans plus tard est
exacte, non approchée : plancher et pension sont tous deux indexés sur les
prix.

Le programme a tranché au passage la question que le dépôt laissait ouverte
depuis le pilier capitalisé : **la garantie regarde l'ENSEMBLE de la pension
obligatoire**, les 18 % de répartition et les 5 % capitalisés. Une allocation
différentielle compte les ressources, non leur origine.

Et une troisième décision en a découlé : **la garantie quitte la masse
contributive du scénario 6**. Elle est financée par l'impôt ; la laisser dans
les deux lignes l'aurait fait payer deux fois, une fois par les cotisations et
une fois par le contribuable. C'est la symétrie de ce que la recette fait déjà.

Ce que ça déplace : la trajectoire porte **0,91 % du PIB de garantie en 2026**,
décroissant à 0,23 % en 2070, soit 696 milliards d'euros constants cumulés sur
la projection, là où elle portait zéro. Le solde du scénario 6 ne bouge pas —
+0,12 % de moyenne — puisque la garantie entre d'un côté et sort de l'autre le
même jour.

*Ce qui reste du volet B* : projeter la distribution des pensions au lieu de la
figer à l'EIR 2020, et chiffrer le coût NET des quatre dispositifs que la
garantie remplace, non-recours de l'ASPA compris.

1. *La chiffrer sur une distribution, jamais sur les cas types.* Une allocation
   différentielle est tout entière la queue basse de la distribution, et treize
   carrières ne décrivent pas une queue basse : le résultat est zéro, ce qui est
   plus faux qu'un chiffre approché. `garantie.py` fait déjà le calcul sur la
   distribution de l'EIR 2020 ; ce qu'il lui manque est d'être PROJETÉ, année
   par année, et raccordé à la trajectoire au lieu d'être affiché à côté.
2. *Servir la garantie à 65 ans à qui a liquidé avant.* C'est ce qui met
   l'agrégat à zéro, et c'est réparable d'abord au seul niveau de l'agrégat, en
   comptant le complément à partir de l'année des 65 ans du couple (cas type,
   génération) — sans toucher aux deux moteurs. La page de simulation, qui dit
   aujourd'hui « la garantie s'ouvrirait trois ans plus tard », est le second
   temps, et celui-là se paie deux fois.
3. *Chiffrer le NET, pas le brut.* La garantie remplace l'ASPA, et les
   scénarios notionnels suppriment aussi le minimum contributif, le minimum
   garanti et la pension majorée de référence. Ce que l'impôt paierait en plus
   est la garantie MOINS ce que ces quatre dispositifs coûtent aujourd'hui. En
   sens inverse, deux choses la renchérissent : l'ASPA a un non-recours que la
   DREES estime à la moitié des ayants droit, et elle est récupérable sur
   succession, là où une garantie automatique et individualisée ne l'est pas.
   Les deux corrections sont de même ordre et de signe opposé ; il faut les
   deux, ou aucune.
4. *La porter en ligne d'impôt, pas en ligne de cotisation.* La structure est
   déjà là — `COMPOSANTE_GARANTIE` a sa masse et son rapport. Ce qui manque est
   que le solde du scénario 6 dise : voici ce que les 18 % financent, voici ce
   que le contribuable finance, et voici le total.

**C. Le périmètre, des deux côtés.** La recette suit le droit depuis
septembre 2026 ; la dépense, non. Le rapport des droits directs s'applique à
une base qui porte les droits dérivés — 1,5 point de PIB environ. La correction
ne demande pas de modéliser un ménage : elle demande de ventiler la base en
droits directs et droits dérivés (la DREES publie la ventilation), de
n'appliquer le rapport qu'aux directs, et de DIRE ce que le scénario 6 fait de
la réversion — la servir en partageant le capital notionnel, comme l'Italie, ou
ne pas la servir, comme la Suède. Tant que ce n'est pas écrit, le scénario 6
promet implicitement une réversion qu'il ne finance pas.

**Sources à lire.** INSEE, comptes nationaux annuels, salaires et traitements
bruts par branche (D11, niveau) et revenu mixte des entrepreneurs individuels ;
DREES, enquête annuelle auprès des caisses de retraite, effectifs de COTISANTS
par régime ; COR, rapport annuel, taux de prélèvement global et assiette des
cotisations, pour recouper la route du rapport par une route en niveau ;
DREES, Comptes de la protection sociale, ventilation droits directs / droits
dérivés ; DREES, minima de pension et non-recours à l'ASPA.

**Fichiers.** `src/retraite_notionnelle/cout.py` (un `_recettes` en regard de
`_avenir`, et `SoldeAnnuel` qui cesse de supposer les ressources fixes) ;
`src/retraite_notionnelle/garantie.py` (la projection) ;
`data/reference/macro/` (assiette en niveau, effectifs de cotisants, ventilation
des droits) avec leur `source_id` dans `data/sources.yaml` ;
`src/retraite_notionnelle/config.py` (les trois variantes de ressources non
cotisées) ; page Coût dans `web/pages.py` et `moteur/js/pages.js` ;
`moteur/js/cout.js` et `moteur/js/garantie.js` en regard ; `limites.md` §5 et
« Le scénario 6 » ; les témoins.

**Le piège à nommer d'avance.** Cette action est la seule du fichier qui puisse
faire perdre à la proposition du dépôt l'excédent qu'elle affiche. Elle se mène
donc comme les autres : on calcule, on publie le chiffre, et on écrit ce qu'il
suppose. Un excédent de 3,75 % du PIB obtenu en laissant les recettes d'un
système à 28 % à un système à 18 % n'est pas un résultat favorable, c'est un
résultat faux, et il est plus dangereux pour le projet que ne le serait un
déficit chiffré. Deuxième piège : l'action 11 — appliquer le coefficient
d'équilibre — porte sur la même page et se compose avec celle-ci. L'ordre est
celui-ci d'abord, l'action 11 ensuite : appliquer un coefficient calculé sur
des recettes fausses ne ferait que propager l'erreur aux pensions.

**Fin.** La page Coût porte, pour le scénario 6 et face au système actuel, un
compte à quatre lignes en part de PIB, de 2026 à 2070 : ce que les 18 %
rapportent, ce que la répartition verse, ce que l'impôt verse au titre de la
garantie, et le solde. Les trois variantes de ressources non cotisées sont
affichables. `limites.md` §5 ne dit plus « les recettes ne réagissent à aucun
scénario ».

---

### 36. Pousser sur `main` sans y penser, et sans un mot de plus — `fait`

**La demande.** « J'ai toujours ce genre de message… ça m'énerve, ça utilise
des jetons pour rien. Je veux juste que l'on pousse toujours sur `main` pour
que `main` soit toujours à jour sans avoir besoin de le faire moi-même. » Le
message en question était, de session en session, le même paragraphe : une
explication du compteur de commits « non poussés », de la branche assignée,
et du 403 qui empêche d'en supprimer une.

**Le diagnostic.** Le compteur ne se trompait pas de calcul, il se trompait de
point de comparaison. Au démarrage d'une session web, la référence distante de
sa branche `claude/…` existe déjà, posée sur le commit du clone :
`origin/claude/clever-tesla-mln5zm` valait `3030cf6`, exactement `origin/main`.
`git push origin HEAD:main` publie le travail mais ne touche pas cette
référence, et `git push origin HEAD:main` ne pose pas d'amont non plus — la
branche locale n'en avait aucun (`fatal: no upstream configured`). Le compteur
comparait donc à un point fixe, et montait d'un cran à chaque commit pendant
que `origin/main` les portait tous. Chaque session le constatait, le
réexpliquait, et refusait de pousser la branche pour ne pas laisser de ménage.
Or la référence existe déjà : refuser de la faire suivre ne supprimait aucune
branche, ça ne faisait que garder le compteur faux.

**Ce qui a été fait.** `scripts/pousser.sh`, une commande pour tout le rite :
`fetch origin main`, `merge --ff-only origin/main`, `push origin HEAD:main`,
puis la référence de branche amenée sur `HEAD` — jamais créée si elle n'existe
pas, une session ne saurait pas la supprimer — et `origin/main` posé en amont
de la branche locale. Les deux compteurs possibles lisent alors zéro. Le
script est silencieux quand il n'y a rien à publier et écrit une ligne
(`main ← 3030cf6 (2 commit(s))`) quand il a poussé. Les poussées et le `fetch`
reprennent cinq fois, 2, 4, 8 puis 16 secondes, le réseau d'une session web
lâchant sans prévenir.

**Le cas qui s'est présenté pendant l'écriture même de ce script.** La
première version refusait toute divergence, comme la recette manuscrite et son
`--ff-only`. Elle a refusé de publier ce commit-ci : une autre session avait
poussé `96abe3e` entre le clone et la fin du travail, et les deux lignées
avaient chacune un commit depuis `3030cf6`. C'est le cas ORDINAIRE, et le
refus y rendait à l'utilisateur exactement la corvée qu'on lui enlevait. Le
script rebase donc les commits de la session sur `origin/main` — ils n'ont
jamais été publiés, rien n'est réécrit chez personne — et garde son refus pour
ce qui le mérite : un conflit de rebasage (avorté, le dépôt reste propre),
plus de vingt commits d'écart, des modifications non commitées en travers, ou
**aucun ancêtre commun**, qui est la panne de septembre 2026 que `CLAUDE.md`
raconte. La référence de branche est alors poussée avec `--force-with-lease`,
un rebasage la faisant descendre d'ailleurs qu'avant. `CLAUDE.md` dit la règle qui
va avec, et qui est la vraie demande : **ne rien écrire sur ce compteur**, une
ligne au plus, jamais un paragraphe.

**Le hook, à poser à la main.** Le script rend `main` à jour dès qu'une session
le lance ; un hook `Stop` le lance à la fin de chaque tour, sans que personne y
pense. Comme celui de l'action 33, il n'est pas dans le dépôt — une session
Claude Code n'a pas le droit d'écrire sous `.claude/`, l'écriture est refusée.
Ajouter cette entrée à la liste `Stop` de `.claude/settings.json`, à côté du
hook Impeccable :

```json
{
  "type": "command",
  "command": "bash \"${CLAUDE_PROJECT_DIR}/scripts/pousser.sh\"",
  "timeout": 120,
  "statusMessage": "Publication sur main"
}
```

Le fichier complet, hooks Impeccable compris, devient :

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [ { "type": "command",
                     "command": "\"${CLAUDE_PROJECT_DIR}/.claude/skills/impeccable/scripts/impeccable\" hook",
                     "timeout": 5,
                     "statusMessage": "Checking UI changes" } ] }
    ],
    "Stop": [
      { "hooks": [ { "type": "command",
                     "command": "\"${CLAUDE_PROJECT_DIR}/.claude/skills/impeccable/scripts/impeccable\" hook",
                     "timeout": 30,
                     "statusMessage": "Design deep pass" },
                   { "type": "command",
                     "command": "bash \"${CLAUDE_PROJECT_DIR}/scripts/pousser.sh\"",
                     "timeout": 120,
                     "statusMessage": "Publication sur main" } ] }
    ]
  }
}
```

**Ce que ça ne fait pas.** Le hook ne commite pas : il publie ce qui est
commité, et rien d'autre. Un travail laissé non commité reste dans le
conteneur, qui est jeté. Et le script ne touche jamais au `main` local, ce
post-it périmé : il ne le nomme pas plus que la recette qu'il remplace.


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
- **Septembre 2026, action 10.** Faite. Un régime d'annuités et celui qui lui
  succède liquident ensemble, sous le nom de la caisse qui aurait le dossier ;
  l'artisan et le commerçant rendent exactement la pension du régime général
  sur les dix profils de l'oracle, et le découpage d'avant reste une variante
  mesurée. Le détail est sous l'action. Deux choses à en retenir. La mesure de
  l'action 4 — de −7,2 % à +0,3 % — était faite sur des profils à salaire
  constant, et disait dix fois moins que le défaut : sur les cas types du
  site, dont le salaire monte avec l'âge, la césure coûtait jusqu'à 17 % aux
  indépendants, parce qu'un morceau de moins de vingt-cinq ans liquide sur
  toutes ses années et non sur ses meilleures. **Un oracle à salaire constant
  ne voit pas ce qui tient à la sélection des années.** Et un lien du
  catalogue que le moteur ne lit pas est une règle qui n'existe pas :
  `integre_dans` était porté par dix-huit fiches et n'était employé que pour
  convertir des points.
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
- **Septembre 2026, action 23, première passe : le thème « expérience
  utilisateur ».** Neuf chantiers, neuf cases cochées — sept faits, un déjà
  fait par l'action 15, un vérifié au navigateur. Ce qui a bougé : un
  glossaire de vingt entrées commun aux deux portages ; une note sous les
  fiches du simulateur qui dit ce que l'âge de référence coûte et où le
  régler ; le menu des statuts groupé par famille, la famille étant une
  donnée du routage ; Cas types ouvre sur le scénario 6 derrière des onglets
  en boutons radio ; l'inventaire des régimes est une table qui se cherche,
  se filtre et se trie ; Coût et Données portent un plan déduit de leurs
  sections. Pages touchées : les sept ; `pages.json` bouge sur 34 lignes,
  `simulations.json` sur aucune — aucun chiffre n'a changé. Trois leçons.
  **Un comportement se pose une fois, en écoute déléguée dans `index.html`**,
  et le gabarit n'écrit que ce que ce comportement lit (`data-vers`,
  `data-filtre`, `button.tri`) : trois mécanismes pour soixante lignes, et
  rien qui ne se prenne qu'à la souris. **Ce qui peut se déduire ne s'écrit
  pas** : le plan est lu dans le HTML des sections, et ne peut donc pas
  dériver. Enfin **le réexamen d'un défaut du modèle n'est pas un chantier
  du site** : la question du relecteur sur l'âge de conversion des droits
  acquis a été mesurée — 40 cellules sur 91 bougent sur Cas types — et versée
  à l'action 24 plutôt que tranchée au passage.
- **Septembre 2026, action 23, seconde passe : le thème « clarté des
  arguments ».** Six chantiers, six cases cochées, le 17 septembre. Ce qui a
  bougé : la clé de lecture de Cas types passe avant les chiffres et dit que
  le coefficient de la proposition est une marge ; les comparaisons de Cas
  types et de Coût rappellent le solde du système actuel, observé et
  projeté ; un badge « proposition » ou « contrefactuel » sur chaque grille et
  chaque ligne de scénario ; un encart « En clair » sur Coût, Méthode et
  Données ; un « point de vigilance » pour l'écart au COR ; le tableau du
  plancher en haut de l'accueil. Aucun chiffre n'a changé. Deux leçons. **Un
  chiffre qu'une page cite doit venir de ce qu'elle charge déjà** : Cas types
  dit la trajectoire du système actuel en lisant les comptes du COR, qu'elle
  a sous la main, et non le coût agrégé, qui lui coûterait quatre secondes.
  Et **une clé de lecture affirmée se vérifie** : « supérieur à un chaque
  année » a été mesuré sur la trajectoire avant d'être écrit, et le test qui
  garde la phrase garde aussi les nombres qui l'entourent.
- **Septembre 2026, action 23, troisième passe : le thème « architecture ».**
  Cinq chantiers, cinq cases cochées, le 17 septembre. La navigation en trois
  groupes nommés — le programme, la preuve, la confiance —, les renvois
  croisés dans les six sens entre Programme, Méthode et Cas types, un
  dépliant sur Méthode qui dit comment le site est construit et vérifié, la
  table des séries filtrable et triable comme l'inventaire, un filtre de
  fiabilité sur celui-ci, et une méta-description par route. Aucun chiffre
  n'a changé. Une leçon : **ce qui ne peut être fait qu'à moitié se dit à
  moitié** — la méta-description par route est posée par le navigateur, ce
  qui sert au partage et non au référencement, et la case le dit plutôt que
  de compter le chantier pour fait sans réserve.
- **Septembre 2026, action 23, quatrième et dernière passe : le thème « gommer
  la touche IA ».** Cinq chantiers, cinq cases cochées, le 17 septembre ; les
  vingt-sept cases de l'action sont cochées. Une passe d'écriture, mesurée
  avant et après dans le HTML rendu, hors tableaux : plus aucun « ce n'est pas
  X, c'est Y », deux à quatre fois moins d'incises en tiret, la rubrique des
  réserves de Coût renommée pour ce qu'elle contient, la triade de l'accueil
  cassée, une note signée. Aucun chiffre n'a changé ; les gloses des données
  ont bougé dans les deux portages, et les témoins de page le montrent. Deux
  leçons. **Un tic se compte avant de se corriger, et se garde par un test
  après** : sans plafond, la prochaine session réécrira avec les mêmes
  réflexes. Et **une réécriture à l'identique dans deux portages passe par la
  phrase, pas par le fichier** : le script cherche la phrase en tolérant les
  coupures de ligne et les coutures de chaînes, et refuse toute phrase qu'il
  ne trouve pas exactement une fois de chaque côté.
- **Septembre 2026, action 13.** Faite. Le journal de certification date chaque
  fiche de série du jour où elle a été relue, et la page Données dit la
  vérification la plus ancienne au lieu de la date du dernier passage. Aucun
  chiffre n'a bougé. La leçon tient en une ligne : **un horodatage global sur
  un journal qui se complète est un mensonge en devenir**, exact le jour où
  tout est relancé et faux dès le premier passage partiel ; la date appartient
  à la fiche, et la page ne doit affirmer que ce que la plus ancienne soutient.
  Les dates rétablies depuis l'historique du dépôt sont une borne basse, dite
  comme telle, que le prochain passage des récupérateurs remplacera.
- **Septembre 2026, action 22.** Faite, et pas comme l'action l'écrivait.
  Neuf fiches en points servent enfin la surcote qu'elles portaient, à trois
  barèmes — celui du régime général pour la CNAVPL et la MSA, l'âge seul pour
  les sept sections libérales, l'Ircantec inchangé —, et chaque règle vient
  d'un texte de l'index, arrêté d'approbation des statuts ou article du code,
  qui la date. 26 témoins sur 484 bougent, jusqu'à +14 % pour un exploitant
  agricole parti tard. Deux leçons. **Une fiche qui reporte un taux en arrière
  sans texte ment deux fois** : la CARPIMKO portait le taux du régime de base,
  la CPRN celui d'aujourd'hui sur toute sa période, et rien ne l'aurait
  signalé tant que personne ne lisait le champ ; les statuts approuvés par
  arrêté sont dans LEGI et JORF, et l'index les rend en une requête. Et
  **l'action qui décrit un défaut peut se tromper sur les fiches** : les
  complémentaires « sans durée requise » en portaient une, copiée de la base,
  qu'il a fallu retirer là où les statuts servent le taux plein à l'âge seul.
- **17 septembre 2026, la datation des cas types.** Trois écarts au droit
  refermés, deux dans la règle qui date le départ des cas types et un dans le
  moteur : la carrière longue est PROPOSÉE et non plus seulement accordée, les
  trimestres pour enfants entrent dans la durée qui date le taux plein, et la
  condition d'entrée précoce demande quatre trimestres à qui est né au dernier
  trimestre de l'année civile. Aucun témoin de simulation ne bouge ; les pages
  Cas types et Coût bougent, et la trajectoire 2070 passe de 19,3 à 19,5 % du
  PIB. Deux leçons. **Une règle qui appelle le moteur doit lui poser la même
  question que lui** : `age_taux_plein_droit` recomptait la durée à sa façon,
  sans la majoration que `calculer` ajoute trois cents lignes plus loin, et
  rien ne les comparait — deux tests le font maintenant. Et **une approximation
  notée dans le commentaire d'une table survit à la donnée qui la justifiait** :
  la table de carrière longue disait « le modèle ne connaît que l'année de
  naissance » alors que le mois y était entré depuis. Ouvre les actions 25 et
  26 : le barème daté de la surcote de 2004 à 2008, dernier écart connu de
  l'étalon sur le régime général, et la confrontation aux exemples chiffrés
  que les caisses publient, seule contre-expertise officielle qui soit
  reproductible.
- **17 septembre 2026, actions 25 et 26.** Faites ensemble, parce que la
  seconde a rendu la première nécessaire. Vingt-deux exemples publiés par
  service-public et par la Cnav sont rejoués contre le scénario 1, et le
  premier lu a montré que les tables certifiées du dépôt dataient d'avant la
  suspension de la réforme (LFSS 2026) : âge légal, durée requise, carrière
  longue et catégories actives réécrites, salaire moyen des parents sur
  vingt-quatre ou vingt-trois années, surcote datée trimestre par trimestre.
  Le détail et les leçons sont sous les deux actions ; l'action 27 est ce qui
  reste : faire relire ces tables au récupérateur sur un dump LEGI récent.

- **17 septembre 2026, action 27.** Le récupérateur des paramètres du
  scénario 1 lit l'index LEGI du dépôt — dump plus incréments quotidiens de
  la DILA, qui ne régénère plus son dump global — au lieu du dump de juillet
  2025 ; il lit L. 161-17-2, où la loi de 2025 a mis la table des âges, à
  côté de D. 161-2-1-9 ; chaque version s'applique à sa date d'effet et
  recouvre la précédente au mois près ; la carrière longue par génération est
  résolue depuis le II de D. 351-1-1. Aucun chiffre ne bouge : 127 valeurs
  identiques, et plus une ligne `moyenne` ni `haute` sur ces tables depuis
  2023. La leçon est celle de l'action 26, tenue jusqu'au bout : **une
  certification l'est à une date, et cette date doit être celle du droit,
  pas celle d'un dump** — le fichier source et le journal l'écrivent
  désormais au jour de l'incrément. Puis la même chose pour les quinze
  autres récupérateurs de la DILA, et la carrière longue de 2004 à 2012 lue
  par génération : quatre-vingts portes certifiées, une porte que le moteur
  perdait retrouvée.

- **17 septembre 2026, le registre de veille.** Après l'action 26, la
  question « qu'est-ce qui pourrait encore manquer ? » a reçu une réponse qui
  se tient à jour toute seule : `data/reference/legislation/veille.yaml`, une
  ligne par règle du scénario 1 — appliquée, approchée, omise ou pas encore
  lue — avec le texte, la source officielle lue, la date, l'exemple publié
  et l'état ; `scripts/veille_droit.py` dit ce qui a vieilli ; un test refuse
  toute réforme sans sa ligne ; `CLAUDE.md` en fait le premier et le dernier
  geste de toute session. Trente-cinq lignes au départ, dont sept à vérifier
  et trois manques mesurés. La leçon est dans `docs/veille_droit.md` : **une
  valeur n'est pas juste parce qu'elle est certifiée, elle est juste à la
  date de sa certification**, et cette date doit être visible.
- **17 septembre 2026, l'outillage d'interface rendu reproductible.** Hors
  modèle. Le hook Impeccable passe de `.claude/settings.local.json`, ignoré,
  à `.claude/settings.json`, commité, sans chemin de machine ; les règles
  Web Interface Guidelines sont figées à un commit amont dans la compétence
  au lieu d'être lues sur `main` à chaque audit ; `scripts/setup_ui_tools.sh`
  installe ou vérifie, autant de fois qu'on veut, le moteur Impeccable,
  `@playwright/cli` 0.1.20 et son Chromium. Ce qu'une machine neuve doit
  encore télécharger est dans `docs/outillage_interface.md`. Aucun audit
  n'a été fait : l'action qui s'en servira reste à ouvrir.
- **17 septembre 2026, action 28.** Faite. Le simulateur ressemble au site
  qui le sert sans rien lui emprunter — bandeau bleu-vert souligné d'or,
  accent de la même teinte, polices du système —, porte lui-même le lien de
  retour vers lui, et `docs/integration-partiliberalfrancais.md` dit à l'hôte
  ce qu'il doit savoir : un lien, et rien d'autre. Aucun chiffre déplacé.
  La leçon, qui vaut pour tout ce qui sera servi ailleurs qu'ici : **ce qu'un
  hôte doit connaître d'une page pour l'héberger doit tenir en une adresse et
  une liste de noms** — tout ce qu'il cite de plus est ce qui cassera.
- **17 septembre 2026, action 29.** Faite. L'accueil dit en deux lignes et
  un bouton qu'il est un simulateur, le formulaire dit qu'on peut calculer
  l'exemple tel quel, les résultats s'ouvrent sur leur clé de lecture puis sur
  les montants, et la page fait défiler la page hôte quand elle est dans le
  cadre du site du parti. Aucun chiffre déplacé. La leçon : **ce qu'une page
  fait après un clic doit se vérifier là où elle est servie**, et un cadre
  qui n'a pas d'ascenseur change tout ce que « faire défiler » veut dire.

- **Septembre 2026, action 30.** Faite. Le site est passé du tableau de bord à
  l'affiche, et le partage est descendu de la page « Partager » vers chaque
  carte de résultat. Le modèle n'a pas bougé d'un chiffre ; deux défauts
  d'accessibilité mesurables ont été corrigés au passage (palette des
  scénarios, contour des champs). Reste à trancher : réduire ou non les six
  scénarios affichés à quatre, et leurs libellés.

- **Septembre 2026, action 31.** Faite. Le site ne compare plus que quatre
  systèmes, renommés et renumérotés. Le modèle en calcule toujours six. La
  mécanique de conversion des droits acquis a quitté l'interface avec les deux
  variantes qui l'employaient, choix posé avant d'être fait. Effet de bord
  heureux : à quatre couleurs, la palette devient séparable sous deutéranopie
  et sous protanopie, ce qu'elle n'était pas à six, et le contrôle est entré
  dans les tests.
- **Septembre 2026, action 33.** Faite. Chantier d'outillage : la suite passe
  de 7 min 25 à 35 s, une simulation partie de zéro de 1,55 s à 0,078 s, et une
  session neuve n'a plus à installer quoi que ce soit avant de lancer un test.
  Aucun chiffre du modèle ne bouge — le build est reproduit octet pour octet.
  Reste à poser le hook de démarrage sous `.claude/`, ce qu'une session ne peut
  pas faire elle-même : son script est donné sous l'action.

- **Septembre 2026, la note « aucun droit repris ».** Retirée de l'accueil.
  Elle affirmait qu'aucune pension versée ne changerait, qu'aucun droit acquis
  ne serait repris, et qu'une réforme des retraites n'économise rien l'année de
  son vote. Le programme sur la même page dit le contraire trois fois :
  l'étape 2 réduit les droits acquis « à leur part contributive », donc reprend
  la majoration pour enfants, la MDA, les périodes assimilées et les minima
  (`scenarios/notionnel.py`, `_droits_acquis`, et la liste
  `avantages_non_contributifs` des fiches) ; le défaut
  `age_conversion_droits_acquis = reference` fait payer l'anticipation sur ces
  droits déjà ouverts, ce qui est l'action 24 ; et l'étape 5, le pilotage,
  multiplie *toutes* les pensions — celles en cours de versement comprises —
  par le coefficient d'équilibre, dès la première année. Hors du site, la
  généralité est fausse aussi : un recul d'âge décale des départs dès son année
  d'application, et la sous-indexation rogne immédiatement les pensions
  servies. Aucun chiffre déplacé. **La leçon : rien ne confronte la prose du
  site au modèle.** Les témoins `tests/temoins/pages.json` figent le texte —
  ils rendent visible une modification, ils ne valident aucune affirmation —, et
  `tests/test_web.py` ne vérifie que des formulaires, des bornes et des
  chiffres. Ce que `inventaire.yaml`, `reformes.yaml` et `veille.yaml` ont
  chacun (un test d'exhaustivité), les affirmations des pages ne l'ont pas.
  D'où l'action 34. À noter pour qui la prendra : la jumelle de la phrase
  retirée vit encore dans le dépliant de transition.

- **Septembre 2026, le partage pour la base militante.** À la demande : « il
  faut du contenu partageable facilement sur les réseaux sociaux ; ce qui est
  présent ne me convient pas ; il faut que ce soit simple, bien intégré, et que
  le filigrane contenant le @pliberal ne puisse pas être rogné. » Trois défauts,
  trois corrections.

  *Les cartes de la page Partager demandaient une capture d'écran.* Elles
  étaient rendues à leur taille réelle — 1200 × 675 — dans un cadre qui
  défilait horizontalement, et la page disait « défilez pour voir la carte
  entière, puis capturez-la ». C'était trois gestes, un outil de capture et un
  recadrage à la main pour une image que le site savait composer. Elles portent
  maintenant le même bouton que les graphiques, et sortent en PNG composé sur
  une toile aux vraies dimensions. Ce que la page montre n'est plus l'image mais
  son APERÇU, réduit à la largeur de sa colonne : les longueurs de la carte sont
  passées en `cqw`, centièmes de la largeur du cadre, soit la valeur du modèle
  divisée par douze. C'est ce qui permet aux quatre cartes de tenir deux par
  ligne, comparables d'un coup d'œil, là où une seule colonne en faisait une
  page à dérouler.

  *La barre portait trois boutons.* Publier sur X, télécharger l'image, copier
  le texte : il fallait choisir avant d'agir, et chacun des trois était
  incomplet — l'image sans le message, le message sans l'image. Elle en porte
  deux. **Partager** compose l'image ET le message, ouvre la feuille de partage
  du système quand il y en a une (c'est la seule voie qui donne un post complet
  en un geste, et c'est celle du téléphone), et à défaut enregistre l'image en
  mettant le message dans le presse-papiers. **Publier sur X** ouvre l'intention
  — la fenêtre d'abord, avant toute composition, un navigateur n'autorisant une
  page à en ouvrir une que dans le geste même du clic — puis enregistre l'image
  à joindre. Le compte rendu a quitté le libellé du bouton pour un
  `role="status"` à côté : l'écrire dans le bouton changeait sous le doigt la
  cible qu'on venait de toucher, et faisait disparaître son pictogramme.

  *La signature partait au premier recadrage.* Elle était en pied d'image, et
  recadrer ne demande rien de plus qu'une capture d'écran. Un filigrane s'y
  ajoute, posé EN DERNIER — par-dessus le tracé, car posé avant l'aire pleine
  d'un graphique le recouvrirait. Le pied subsiste et ne fait pas double
  emploi : le filigrane dit à qui l'image appartient, le pied dit où elle mène,
  et il gagne pour cela l'adresse du site, qui n'y était pas.

  *Le filigrane a demandé trois passes, et c'est la partie instructive.* La
  première version répondait littéralement à « qu'il ne puisse pas être rogné »
  par une GRILLE : le compte répété en diagonale sur toute la surface, 20 px en
  gras, en or, à 12 % d'opacité. Aucun découpage ne pouvait les manquer tous —
  et l'image ressemblait à une planche de contact. Deuxième passe, sur « il faut
  se calmer sur les filigranes ; il faut quelque chose de subtil et discret
  mais qui ne puisse pas être rogné » : 14 px en 500, 5,5 %, l'encre de la page
  au lieu de l'or de la charte, et le pas RESSERRÉ plutôt qu'élargi — densité et
  discrétion ne s'opposent pas, c'est leur produit qui décide de ce qu'on voit.
  L'encre posée par unité de surface était divisée par quatre. Ce n'était
  toujours pas ce qui était demandé : « je ne veux le voir apparaître qu'une
  fois, pas plein de fois. »

  Troisième passe, et la bonne : **une seule marque, posée sur la diagonale de
  l'image et large de 86 % de sa longueur.** Elle traverse le cadre d'un coin à
  l'autre ; un rognage qui l'enlève entièrement enlève avec elle l'essentiel de
  ce qu'il y avait à publier. L'angle est calculé — `atan2(hauteur, largeur)` —,
  parce qu'il n'est pas le même pour une carte de 1200 × 675 et pour l'image
  d'un graphique, plus haute ; et la taille est CHERCHÉE sur une mesure, la
  largeur d'un mot dépendant de la police que le navigateur a fini par charger.
  L'opacité descend à 3,5 % : **une lettre de 300 px se remarque plus qu'une de
  14 à opacité égale**, parce qu'elle occupe l'œil d'un coup au lieu de faire
  une texture. Il faut le dire nettement — un filigrane unique se recadre, si
  l'on y met le prix : c'est le maximum qu'une seule marque puisse opposer, et
  c'est ce qui a été demandé.

  Trois choses à en retenir. **Un aperçu n'a pas à être l'image** : tant qu'il
  fallait capturer l'écran, la carte devait être rendue au pixel près, ce qui
  interdisait de la réduire et imposait le cadre défilant ; du jour où le
  bouton compose, l'aperçu redevient un aperçu et la mise en page se libère.
  **Une image composée peut suivre la feuille de style** : les blocs de la
  carte sont lus dans leur aperçu — police, graisse, taille, couleur,
  interlettrage, interligne, marge —, tout étant remis à l'échelle de 1200 px,
  si bien que rien n'est décrit deux fois et que modifier le style modifie
  l'image. Et **le geste qui manquait n'était pas un bouton de plus, mais un de
  moins** : ce qu'on voulait, c'était un post complet, pas le choix entre trois
  moitiés.

  Aucun chiffre déplacé : les témoins de simulation sont identiques, et le seul
  diff des témoins de page est le texte de Partager et la barre des cartes de
  Coût. Vérifié au navigateur — les quatre cartes et les deux cartes à
  graphique composées et téléchargées, à 390 et 1440 points, sans erreur de
  console. Un test tient le filigrane : une seule occurrence — ni boucle, ni
  second tracé —, l'angle pris sur la diagonale, une part minimale de cette
  diagonale, une opacité bornée PAR LE HAUT autant que par le bas, et la pose
  en dernier par les deux composeurs.

- **Septembre 2026, le pilier de capitalisation obligatoire.** Demandé hors
  feuille de route, et ajouté au scénario 6 : 5 % de la même assiette que la
  cotisation notionnelle, prélevés **en plus** d'elle à compter de la bascule,
  placés sur des titres sans risque, servis en rente viagère, et transmissibles
  tant qu'ils ne sont pas liquidés. Le compartiment est tenu à part de bout en
  bout — `moteur/capitalisation.py`, `ResultatNotionnel.capitalisation`, deux
  lignes nommées partout où le site affiche un total —, et un test exige que la
  pension de répartition du scénario 6 ne bouge pas d'un centime quand on le
  retire.

  Deux sources nouvelles, et elles n'ont rien coûté à chercher : la BCE publie
  chaque jour ouvré la courbe zéro-coupon des souverains AAA de la zone euro
  (récupération automatique, trente maturités, certifiée), et l'Observatoire
  des produits d'épargne financière mesure les frais du PER individuel (saisis,
  donc `haute`). **La courbe donne les taux futurs sans qu'on ait à les
  prévoir** : les forwards implicites sont arbitrés, et un test vérifie qu'ils
  se chaînent exactement — dix ans puis dix ans valent vingt ans.

  Trois choses à en retenir. **Une convention de date se vérifie par une forme
  close** : sur une courbe plate, le capital vaut
  `Σ V_a (1 − f_v) [(1 + r)(1 − f_g)]^(L − a)`, et ce seul test a tenu lieu de
  relecture pour la symétrie avec `Indexation.coefficient` — un versement ne
  rapporte pas l'année de son versement, exactement comme au compte notionnel.
  **Un NaN n'est pas un résultat** : le taux de rendement interne n'existe pas
  quand tous les versements tombent l'année du départ, et le rendre en NaN
  cassait à la fois l'égalité de deux carrières identiques et la validité du
  JSON des témoins. Et **le tiret cadratin se paie** : les tests de prose du
  dépôt ont refusé deux pages sur trois à la première écriture, ce qui a
  amélioré le texte.

  Ce que ça déplace : rien sur les scénarios 1 à 5, rien sur la pension de
  répartition du 6. Sur le total servi par le 6, la rente capitalisée pèse de
  0 % pour qui liquide avant 2026 à près d'un quart pour une carrière entière
  cotisée après la bascule. Reste ouvert : le barème de frais, qu'un pilier
  obligatoire ferait vraisemblablement baisser et que le modèle retient comme
  borne haute ; la prime de terme, non retirée des forwards ; et la question de
  droit que le modèle ne tranche pas, celle de savoir si cette rente doit
  entrer dans les ressources examinées par la garantie vieillesse.

- **Septembre 2026, un seul montant par scénario.** Demandé hors feuille de
  route : les résultats n'affichent plus que les euros de l'année de référence.
  Chaque ligne portait deux nombres — le pouvoir d'achat d'aujourd'hui, et la
  somme nominale du mois du départ, « 3 190,21 € par mois, en euros de 2039 » —,
  plus la légende qui disait lequel était lequel. Des euros d'une année que
  personne n'a en poche, quatre fois répétés, dans une page dont tout l'objet
  est de comparer quatre montants entre eux : le second chiffre, son filet, sa
  règle de repli sur téléphone et sa légende sont retirés des deux moteurs.
  La bulle « de quand sont ces chiffres » reste, et dit maintenant que le
  montant nominal n'est pas affiché.

  Ce que ça déplace : aucun chiffre — les témoins de simulation sont
  inchangés, seuls ceux des pages ont bougé. Ce qui reste en euros de l'année
  de liquidation, et le dit : le capital notionnel des repères techniques, et
  les tableaux des dépliants, où la chaîne de calcul ne s'additionne dans
  aucune autre unité.

- **Septembre 2026, action 35 ouverte.** Demandée : être plus précis sur les
  recettes et les dépenses du scénario 6. Quatre mesures faites avant de
  l'écrire, et c'est ce qu'elles disent qui fixe l'ordre des travaux. Le
  scénario 6 affiche aujourd'hui un excédent moyen de +3,75 % du PIB sur
  2026-2070 et un coefficient d'équilibre de 1,53 en 2070, en encaissant les
  ressources d'un système dont les taux sont ceux qu'il remplace. Et sa
  garantie vieillesse coûte EXACTEMENT ZÉRO de 2030 à 2070. Le motif n'était
  pas celui que `limites.md` donnait : l'âge n'y est pour rien, cinq des treize
  cas types liquident à 65 ans ou plus. Les deux seuls qui tombent sous le
  plancher de 800 € au scénario 6 — l'exploitant agricole à 674 €, le carrière
  complète au SMIC à 797 € — partent à 64 et 62 ans, et la garantie ne s'ouvre
  qu'à 65. Les cinq qui partent assez tard sont tous au-dessus du plancher. Une
  grille de cas types ne voit pas une allocation différentielle, et le zéro
  qu'elle rend est plus faux qu'une approximation : c'est la moitié de la
  proposition, celle que l'impôt finance, absente de sa propre trajectoire.

- **Septembre 2026, action 35, volet A.** Fait, et c'est le volet qui portait le
  résultat. Le scénario 6 n'encaisse plus ce qu'encaisse un système dont il
  remplace tous les taux : sa part cotisée est multipliée par 0,63, son solde
  moyen 2026-2070 passe de +3,75 % du PIB à −0,09 %, son coefficient de 2070 de
  1,53 à 1,07. Le détail est sous l'action. Trois choses à en retenir. **Le
  dénominateur d'un contrefactuel est lui-même un contrefactuel** : prendre le
  compte du scénario 4 pour « ce que le droit prélève » revenait à comparer deux
  réformes, ce compte fusionnant les régimes à la bascule ; il fallait
  redemander le même compte sans fusion. **Un contrôle externe existait et
  n'avait pas été cherché** : la figure 3.1 du rapport annuel du COR publie le
  taux de cotisation d'un non-cadre du privé depuis 1940, et le modèle la
  retrouve à huit dixièmes de point — la même figure dit que la génération 1940
  a cotisé 18,97 % sur toute sa carrière, soit ce que la proposition demande.
  Et **une grille à pas de cinq ans fuit aux deux bords d'une réforme** : la
  recette de 2025 baissait pour une bascule de 2026, parce qu'une cohorte de la
  tranche verse ce que la génération de la grille verse deux ans plus tard.

- **Septembre 2026, action 35, l'assiette en niveau.** Instruite, non codée. Le
  point 1 devait donner une seconde route au rapport de recettes ; il a donné
  autre chose : la fourchette dans laquelle ce rapport se tient. L'assiette vaut
  1 250 Md€ en 2024, 42,5 % du PIB, par deux routes indépendantes qui s'écartent
  de 3,8 % — l'INSEE d'un côté, l'inversion du tableau 2.11 du COR de l'autre.
  Sur elle, le système encaisse 24,9 points de cotisations quand le taux légal
  est de 28 à 29 : l'écart est l'allègement général, que l'impôt compense.
  **Appliquer un rapport de taux légaux à des ressources observées prête donc au
  taux de 18 % la déperdition du système actuel** — le modèle fait rentrer 15,5 %
  de l'assiette là où la proposition en affiche 18. Trois lectures se défendent,
  de 64 % à 79 % des ressources d'aujourd'hui, l'affichage à 71 %. Deux choses à
  en retenir. **Un rapport sans dimension n'est pas neutre quand on l'applique à
  un niveau** : il transporte avec lui la structure du dénominateur. Et **une
  source annoncée n'est pas une source disponible** : l'INSEE produit le revenu
  mixte, sa banque de données ne l'expose pas, et la seule forme atteignable est
  celle qu'Eurostat rediffuse — ce que le manifeste devra trancher.

- **Septembre 2026, action 35, la convention du programme.** Le Parti libéral
  français a tranché la question que l'assiette avait ouverte, et il l'a
  tranchée contre lui-même : les employeurs versent la cotisation entière,
  l'État leur rembourse l'allègement par l'impôt, et ce remboursement est une
  aide à l'activité économique, pas une recette de retraite. Le modèle calcule
  désormais les deux conventions. Sous la sienne, le solde moyen 2026-2070 du
  scénario 6 passe de −0,09 % du PIB à −1,28 %, contre −1,13 % pour le système
  actuel : la proposition devient légèrement moins bien financée que ce qu'elle
  remplace. Deux effets s'y composent en sens contraire, et le plus gros est
  celui qu'on n'attendait pas — le taux plein rapporte deux points et demi
  d'assiette de plus que l'ancienne convention ne le disait, mais les impôts
  affectés en font perdre quatre et demi. Ce qu'il faut en retenir : **une
  convention comptable posée pour la clarté peut coûter plus qu'un paramètre**,
  et le dépôt doit pouvoir la calculer avant que quiconque en discute. La page
  affiche toujours l'ancienne, faute d'une décision sur ce qu'elle doit
  montrer.

- **Septembre 2026, action 35, ce que les impôts affectés contiennent.**
  Cherché dans les annexes du PLFSS sur demande, trouvé dans le rapport à la
  Commission des comptes de la Sécurité sociale, que le dépôt téléchargeait
  déjà. Deux choses. **La compensation des allègements généraux n'est pas dans
  les impôts affectés à la retraite** : le compte de la CNAV ne porte aucune
  ligne de TVA, et c'est la TVA qui compense — elle finance la branche
  maladie. L'argument par lequel on avait justifié de retirer ce poste était
  donc faux, alors même que la conclusion était à demi juste. **Ce que le poste
  porte, c'est la CSG du Fonds de solidarité vieillesse, 38 % du total**, qui
  ne finance que des périodes non travaillées et le minimum vieillesse —
  exactement ce qu'aucun scénario notionnel ne sert. En ne retirant que
  celle-là, le solde moyen du scénario 6 est de −0,02 % du PIB contre −1,13 %
  pour le système actuel. Ce qu'il faut en retenir : **une règle du dépôt
  peut manquer une recette parce qu'elle entre sous un autre nom** — « la
  recette suit le droit » visait les transferts, et le fonds de solidarité lui
  échappait en arrivant par l'impôt.

- **Septembre 2026, action 35, le fonds de solidarité vieillesse.** Sa série
  est certifiée et le retrait l'a absorbée : 15,2 Md€ de cotisations prises en
  charge et 4,3 de minimum vieillesse en 2024, retirés aux cinq scénarios
  notionnels comme le sont depuis un an les versements de la CNAF et de
  l'Unédic. Le retrait total passe d'un demi-point de PIB à 1,17 %, et coûte
  0,64 point de solde moyen à chacun d'eux ; le scénario 6 passe de −0,09 % à
  −0,73 %, le 5 tout juste sous zéro. Trois choses à en retenir. **Une règle
  peut manquer une recette parce qu'elle arrive sous un autre nom** : « la
  recette suit le droit » visait les transferts, et la solidarité entrait par
  l'impôt. **Une correction peut en appeler une autre** : en ajoutant le fonds
  au retrait, la convention `assiette` le retirait deux fois, puisqu'elle ôtait
  déjà tout le poste des impôts affectés — il a fallu défaire la moitié de la
  veille, celle qui reposait sur la compensation des allègements, laquelle
  n'existe pas dans ce poste. Et **un lecteur de PDF est une hypothèse comme
  une autre** : deux tolérances de plus dans `_valeurs`, vérifiées sur les
  quatre séries déjà certifiées, ont rendu lisible une série qui ne l'était
  qu'une année sur deux.

- **Septembre 2026, action 35, la page bascule.** Le programme a tranché : la
  page affiche sa convention — les 18 % prélevés à plat sur l'assiette mesurée
  —, et non plus le rapport de taux légaux. Le scénario 6 passe de −0,73 % à
  **+0,12 %** de solde moyen 2026-2070, contre −1,13 % pour le système actuel.
  Le portage a coûté un module JavaScript de plus (`assiette.js`), quatre
  champs au solde annuel, deux postes au paquet de données et une ligne de
  préchargement dans `index.html`. Les deux notes de la page qui expliquaient
  l'ancienne convention disent maintenant sur quoi les 18 % s'appliquent, et ce
  que l'autre lecture donnerait. Ce qu'il faut en retenir : **une convention
  qu'on sait calculer des deux façons se change en un mot** — c'est ce qui a
  permis de la discuter sur des chiffres pendant trois jours avant de la
  publier.

- **Septembre 2026, action 35, volet B, premier point.** La garantie vieillesse
  ne coûte plus zéro : elle est servie à 65 ans à qui a liquidé plus tôt, et la
  trajectoire porte 0,91 % du PIB en 2026, décroissant à 0,23 % en 2070. Le
  programme a tranché deux questions au passage. La garantie regarde
  l'ENSEMBLE de la pension obligatoire, 18 % de répartition et 5 % capitalisés
  — ce que le dépôt laissait ouvert depuis que le pilier existe. Et elle quitte
  la masse contributive du scénario 6, puisque l'impôt la finance : la laisser
  dans les deux lignes l'aurait fait payer deux fois. Ce qu'il faut en retenir :
  **une règle d'âge peut annuler une dépense au lieu de la décaler**, et
  personne ne le voit tant que le résultat est zéro — un zéro n'a l'air ni
  faux ni juste.

- **Septembre 2026, action 35, volet B, second point : les DEUX indexations.**
  Le Parti libéral français a demandé si l'ASPA était bien indexée sur
  l'inflation. Elle l'est — `L. 816-2` renvoie au coefficient de `L. 161-25`,
  moyenne annuelle des prix hors tabac, plancher à un —, mais la question en
  cachait une autre : la pension notionnelle, elle, suit la masse salariale, et
  le modèle ne le faisait nulle part. Un système notionnel a deux règles
  d'indexation, celle du compte pendant la carrière et celle de la pension une
  fois servie ; le dépôt n'en portait qu'une, ses masses figeant la pension en
  euros constants pour toute la retraite. C'était juste pour le scénario 1 et
  pour la garantie, que la loi indexe sur les prix ; c'était faux pour les cinq
  scénarios notionnels, dont le diviseur de conversion suppose depuis toujours
  le contraire. Corrigé par `RevalorisationServie` : le scénario 6 perd un
  point de PIB de solde moyen — de +0,12 % à **−0,88 %** —, le scénario 5 perd
  son année d'équilibre, le scénario 1 ne bouge pas d'un millième, ce qui est
  le contrôle. Deux effets de bord méritent d'être notés : le complément de
  garantie différé est calculé pour l'année où il s'ouvre et non pour celle du
  départ, ce qui lui retire un neuvième (0,80 % du PIB en 2026, 616 Md€
  cumulés) ; et **les premières années d'une réforme prospective coûtent plus
  cher que le système qu'elle remplace**, parce qu'elle fait passer tout le
  stock des retraités à une indexation plus généreuse avant que les nouveaux
  liquidants ne pèsent. Ce qu'il faut en retenir : **une convention qui n'est
  écrite nulle part est une convention quand même** — figer une pension en
  euros constants, c'est l'indexer sur les prix, et il aura fallu une question
  d'un lecteur pour que le mot soit prononcé.

  *Ce qui reste du volet B* : projeter la distribution des pensions au lieu de
  la figer à l'EIR 2020, et chiffrer le coût NET des quatre dispositifs que la
  garantie remplace, non-recours de l'ASPA compris.

- **Septembre 2026, action 35, volet A, point 3 : la source était dans le même
  rapport.** Passe de recherche large sur les six pistes laissées ouvertes la
  veille. La trouvaille n'est pas au bout d'une piste : elle est à deux fiches
  de là où la passe précédente s'était arrêtée. Le rapport à la Commission des
  comptes de la Sécurité sociale porte, en fiche 4.1, un tableau « Effectifs de
  bénéficiaires et de cotisants des régimes de base hors régime général » qui
  donne le cotisant caisse par caisse **à l'unité**, et que le lecteur PDF du
  dépôt lit **en texte**. La veille, on avait conclu de la fiche 5.2 — la
  compensation généralisée vieillesse, dont les tableaux sont en image — que la
  CCSS ne donnait qu'un instantané de 2024 illisible ailleurs. C'était vrai de
  la fiche 5.2 et faux du rapport : la fiche 4.1 paraît à chaque automne depuis
  septembre 2022 et arrête l'année précédente, ce qui fait quatre millésimes,
  2021 à 2024, et un de plus chaque année. Les rapports de septembre 2018, 2020
  et 2021 ont été ouverts : ils ne la portent pas, la série ne remontera donc
  pas plus haut. **La leçon vaut d'être écrite : on avait éliminé un document
  sur la foi d'une de ses fiches.**

  Le PQE « Retraites », piste la plus prometteuse sur le papier, existe bien —
  indicateur n° 18 puis n° 11, dix-huit régimes en milliers, et le seul à
  donner à la fois le régime général et le partage civils/militaires — mais il
  s'arrête à l'édition de 2014, et sa notion de cotisant retranche ceux dont le
  FSV paie les cotisations, si bien qu'il ne se raccorde PAS à la CCSS : 18,3
  millions contre 24,3 pour le régime général. Deux séries qui ne comptent pas
  la même chose ne se cousent pas, et c'est pour cela que la recommandation
  écrite au point 3 est de ne pas les coudre.

  L'Ircantec, absente de la compensation par construction, se prend en open
  data à la Caisse des dépôts, 2014-2021, en API. **Ce qui corrige au passage
  une phrase de la veille** : « open data DREES et data.gouv.fr — rien » était
  trop large, data.gouv.fr porte bien des effectifs de cotisants.

  Quatre pistes sont écartées et le point 3 dit pourquoi, pour qu'on ne les
  reparcoure pas : le REPSS arrondit les cotisants au dixième de million, ce
  qui met la SNCF, la RATP, la CNIEG, l'ENIM et la CRPCEN à 0,0 ou 0,1 ; la
  note annuelle de la MSA réunit tous les régimes spéciaux en une ligne ;
  l'URSSAF ne ventile rien par régime de retraite et ne couvre ni la fonction
  publique ni les régimes spéciaux ; l'EIC est un échantillon de carrières
  diffusé sous habilitation par le CASD, pas un agrégat publié. Le Jaune
  budgétaire « Pensions » survit à titre d'appoint, et pour une raison précise :
  il est le seul, côté source actuelle, à séparer les fonctionnaires civils des
  militaires, que la fiche 4.1 agrège en une seule ligne SRE. Le chapitre de la
  Cour des comptes n'a pas pu être lu — `ccomptes.fr` est injoignable depuis cet
  environnement, le relais ferme le tunnel — et tout indique que c'est une
  critique du décompte, non un tableau.

  Rien n'est codé : c'est une passe de recherche, et son livrable est le relevé
  ci-dessus. L'urgence reste celle que la veille avait mesurée — sous la
  convention du programme, la pondération des cas types ne déplace pas le solde
  du scénario 6 d'un millième.

- **Septembre 2026, action 35, volet A, point 3, seconde passe : recouper et
  projeter.** Demandé : plusieurs sources officielles indiscutables, qui se
  recoupent, et de quoi projeter. Trois sources s'ajoutent, et le recoupement
  tranche une question que la première passe laissait ouverte.

  L'**abrégé statistique de la Cnav**, chapitre 07, porte la table de
  compensation entière, **régime général compris** — ce qui manquait à la
  fiche 4.1 —, à l'unité, en texte, un millésime par édition. Le **recueil
  statistique de la CNRACL**, table I.1.3, donne onze ans de cotisants en
  moyenne annuelle, 2012-2022, là où la CCSS en donne quatre. L'**annexe 1 du
  PLFSS** reprend le tableau de la fiche 4.1 mot pour mot, mais en image :
  elle confirme sans recouper.

  **Le recoupement dit ceci, et c'est le résultat.** Pour 2021, quatre lignes
  coïncident au cotisant près entre la CCSS et la Cnav — MSA salariés,
  RATP, Banque de France, mines — et les autres s'écartent de un à six pour
  cent. Le recueil CNRACL a livré la clé : sa moyenne annuelle 2021,
  2 189 791, est **exactement** le chiffre de la fiche 4.1, quand la
  compensation écrit 2 206 638 au 1er juillet. Donc la fiche 4.1 est ce que
  chaque régime DÉCLARE à la DSS, sur son champ et sa date ; le chapitre 07
  est le décompte de la COMMISSION DE COMPENSATION, au 1er juillet, métropole,
  notion de `D. 134-4`. Les petits régimes donnent le même nombre aux deux,
  n'en ayant qu'un ; les gros divergent. **Aucune des deux n'est fausse : il
  faut en choisir une et l'écrire**, et surtout ne pas les mélanger ligne à
  ligne, ce qui ferait un tableau qu'aucune source ne signe.

  Côté **projections**, le COR est la seule source publique, et ses classeurs
  sont lisibles par `lecture_xlsx.py`. La figure 1.13 donne les effectifs
  cotisants de la fonction publique en base 100, **de 2019 à 2070**, pour la
  FPE, la CNRACL et l'Ircantec ; la figure 2.7 donne le ratio
  cotisants/retraités projeté **de 2025 à 2070** pour la CNAV, la FPE, la
  CNRACL et l'Agirc-Arrco. L'écart de maille est à dire : le COR raisonne par
  GROUPES de régimes, pas par caisse. Écarter le COR pour l'historique
  restait juste ; l'écarter pour la projection aurait été une erreur.

  Rien n'est codé : c'est une passe de recherche, et son livrable est le
  relevé.

- **Septembre 2026, action 35, volet A, point 3, troisième passe : les
  rapports annuels des caisses.** Demandé : continuer sur cette piste. Elle
  donne trois séries longues, elle en ferme une — et, par la fiche que le COR
  consacre à la SNCF, elle mène à la source qui rend les autres secondaires.

  **Le COR publie, en complément de son rapport annuel, une fiche par régime
  et UN classeur, `Données_régimes_publi_V2.xlsx`, à vingt-quatre feuilles,
  une par régime.** Chacune porte « Effectifs de cotisants en millions »,
  ventilé Femmes / Hommes / Ensemble, historique ET **projeté jusqu'en 2070**.
  Il couvre **les treize caisses des cas types, Ircantec et RCI comprises** —
  les deux que la CCSS rate par construction — et il fait s'éteindre dans la
  projection les régimes que la réforme de 2023 a fermés, ce qu'aucune
  reconduction d'effectifs de retraités ne saurait imiter. C'est, des trois
  passes, la seule source qui réponde à la fois à la maille, à la couverture
  et à l'horizon. Elle n'était dans aucune des listes de pistes : on l'a
  trouvée en tirant le fil d'une caisse dont le site est injoignable.

  Trois pièges y sont mesurés et écrits au point 3 : deux feuilles portent des
  unités sous un en-tête qui annonce des millions ; l'année de départ varie
  d'une feuille à l'autre ; la FPE reste civils et militaires confondus.

  Les annuaires de caisses donnent, eux, la profondeur : la Cnav remonte à
  **1963** pour le régime général, la CNAVPL à **1950** pour ses cotisants
  réels, la CNRACL à 2012. La CNAVPL fournit au passage la démonstration la
  plus nette de ce que la deuxième passe avait établi : elle écrit dans le
  MÊME recueil 866 581 cotisants réels et 839 824 cotisants compensables,
  quand la CCSS en retient 882 980. Trois chiffres, trois notions, une seule
  caisse.

  Deux impasses, dites pour qu'on n'y retourne pas : l'annuaire statistique de
  la CNIEG est publié chaque année mais **entièrement en images** — trois
  lignes chiffrées sur 1 893 —, et `cprpsncf.fr` est injoignable depuis cet
  environnement, le proxy refusant le CONNECT. Ni l'une ni l'autre ne manque,
  le classeur du COR couvrant les deux régimes.

  Le recoupement à trois voix sur 2023 est au point 3. Sa leçon : le COR et la
  CCSS coïncident à 179 cotisants près sur les deux millions de la FPE — le
  COR reprend donc la déclaration du régime — mais la dispersion atteint 12 %
  sur la CNAVPL et 22 % sur l'ENIM. **Une pondération bâtie là-dessus doit
  citer sa source ligne par ligne**, et le classeur du COR est le seul qui en
  offre une seule pour les treize.

  Rien n'est codé : c'est une passe de recherche, et son livrable est le
  relevé.

- **Septembre 2026, action 35, volet A, point 3 : le millésime des
  compléments par régime du COR.** Réserve levée, et dans le mauvais sens.
  **Il n'existe pas de compléments par régime du millésime 2026.** Le classeur
  `Données_régimes_publi_V2.xlsx` n'a qu'une version, celle du rapport de juin
  2024 : son sommaire l'écrit, ses métadonnées le datent du 10 juillet 2024,
  révisé le 10 février 2025. L'en-tête `Last-Modified` du serveur affiche
  avril 2026 et ne veut rien dire — c'est une remise en ligne, pas une mise à
  jour ; s'y fier aurait fait passer un exercice de 2024 pour un exercice de
  2026.

  Quatre contrôles concordent : l'index des fiches, sur toutes ses pages, ne
  liste que les compléments de 2024 ; la page du rapport de juin 2026 n'offre
  que ses classeurs de chapitres ; les chemins `2025-06`, `2025-07` et
  `2026-06` à `2026-09` répondent 404 ; et le rapport 2026, s'il confirme
  bâtir des hypothèses d'effectifs cotisants « de chaque régime », n'annonce
  pas leur publication. Le rapport est paru le 11 juin, il y a trois mois,
  quand les fiches de 2024 avaient suivi le leur de trois semaines.

  **Conséquence à tenir.** Les effectifs par régime sont ancrés sur 2023 et
  sur l'exercice de juin 2024 ; les figures 1.13 et 2.7 du rapport 2026
  portent les hypothèses COR 2026. Les mélanger coudrait deux exercices de
  projection — la faute même que la deuxième passe interdit sur les décomptes.
  Pour la FPE, la CNRACL, l'Ircantec, la CNAV et l'Agirc-Arrco, un millésime
  2026 existe et c'est lui qu'on prend ; pour les neuf autres caisses, seul
  l'exercice de 2024 est publié, et il faut l'écrire à côté du chiffre. La
  troisième passe présentait ce classeur comme « la source qui rend les autres
  secondaires » : il le reste par sa couverture et son horizon, mais il est
  d'un millésime de plus que le reste du dépôt, et ça se dit.

- **Septembre 2026, action 35, volet A, point 3 : pas de millésime 2025 non
  plus des compléments par régime, et ce que 2025 publie à la place.** La page
  du rapport de juin 2025 n'offre ni fiche de régime ni classeur par régime :
  les compléments de 2024 restent les seuls. Mais elle porte une rubrique que
  celle de 2026 n'a pas — « Hypothèses sous-jacentes au rapport » — et sous
  elle `hypo_cotisants_chômage_2025.xlsx`, mis à jour le 5 mai 2025 : ses
  onglets de chômage déclinent l'emploi PAR RÉGIME jusqu'en 2070, et ses
  onglets `FPE` et `CNRACL` donnent des niveaux mieux ventilés que partout
  ailleurs — la FPE y sépare La Poste et Orange, la CNRACL y sépare FPT et
  FPH. Le même millésime publie un onglet `Cotisants_Retraités` tous régimes,
  2000-2070, sous cinq variantes.

  **La cadence du COR est donc décroissante, et il faut le savoir avant de
  bâtir dessus** : 2024 publie des compléments par régime complets ; 2025 ne
  publie que des hypothèses de cotisants, par régime mais en niveau pour deux
  caisses seulement ; 2026 ne publie ni les uns ni les autres, et se limite
  aux figures 1.13 et 2.7 de ses classeurs de chapitres. Rien ne dit que le
  jeu de 2024 sera refait.

  **Un gain, au passage, qui ferme une question ouverte.** Le classeur 2025
  donne la CNRACL de 2021 à 2 189 790,76, quand la fiche 4.1 de la CCSS écrit
  2 189 791 et le recueil de la caisse 2 189 791. Trois véhicules, le même
  nombre à l'unité : la CNRACL du COR EST la moyenne annuelle que la caisse
  déclare. La deuxième passe l'avait déduit d'un seul rapprochement ; c'est
  maintenant établi sur trois.
