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
régimes est finie : <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire)-->89<!--/--> lignes d'inventaire, plus aucune ligne « à modéliser »,
<!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=partiel)-->37<!--/--> fiches partielles dont chaque mur est documenté dans `regimes.md` et
`limites.md` §4. Continuer sur cet axe rapporte peu : les manques restants
portent sur des populations minuscules ou des barèmes que personne ne publie.
Les gains sont sur ce qui porte les résultats de tête du README : les agrégats
de la page Coût, la part patronale, les taux de cotisation qui sont la matière
même des scénarios notionnels, et l'étalon qu'est le scénario 1.

Un coût transversal pèse sur l'ordre : chaque changement du MODÈLE se paie deux
fois, dans `src/retraite_notionnelle/scenarios/actuel.py`
(<!--chiffre:lignes(src/retraite_notionnelle/scenarios/actuel.py)-->4 251<!--/--> lignes)
et dans le portage `moteur/js/` (<!--chiffre:lignes(moteur/js/*.js)-->23 987<!--/--> lignes), puis dans les
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
  passent de 7,1 % à 15,3 % : la retraite est financée par l'impôt pour une
  part qui a doublé en vingt ans. Un compte notionnel ne sait créditer que la
  part cotisée ; c'est ce qui borne la lecture du coefficient, et il fallait le
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

- **19 septembre 2026, le stock après le flux : la dette que le solde
  accumule.** Repris d'un simulateur de transition répartition → capitalisation
  soumis par l'utilisateur deux choses, et deux seulement : la récurrence de la
  dette rapportée au PIB — stock(t) = stock(t−1) × (1 + taux) ÷ (1 + croissance)
  − solde(t) — et l'idée de ne montrer qu'une sensibilité, celle du seul
  paramètre lu. Le reste ne s'applique pas : ses onze scénarios de bascule, sa
  taxe sur les plus-values, son livret et son bouclage macroéconomique par
  élasticités supposent qu'une capitalisation REMPLACE la répartition, ce que
  la proposition ne fait pas — ses 5 % s'ajoutent, donc pas de dette de
  transition —, et le dépôt ne pose aucune élasticité ; son « facteur de
  couverture » est ce que l'ancrage de `cout.py` fait déjà. Livré :
  `calculer_dette` et `Cout.dette` dans `cout.py`, portés dans `cout.js` ; la
  section « Ce que le déficit accumule : la dette, si rien ne s'ajuste » sur la
  page Coût, entre le coefficient d'équilibre et la garantie, dans les deux
  rendus ; et le graphique du site sait tracer SOUS l'axe — `_sommet` rend un
  plancher, nul partout ailleurs, et les témoins de toutes les autres pages
  restent identiques à l'octet. Le taux n'est pas choisi : c'est le forward à
  un an de la courbe BCE du 17 septembre 2026, celui du pilier capitalisé, lu
  jusqu'en 2056 et prolongé à plat ensuite ; la croissance est celle du PIB
  de la projection. Le stock part de zéro en 2025 : les réserves d'aujourd'hui
  restent hors compte, et la réserve de `limites.md` est réécrite en ce sens
  sur la page. *Mesuré* : le système actuel accumule **66 % du PIB** de dette
  de 2026 à 2070 — 51 points de déficits additionnés, le reste d'intérêts nets
  de la croissance —, 57 % à un point de taux de moins, 78 % à un point de
  plus, et ses intérêts de 2070 pèsent 2,4 % du PIB ; la proposition, à 18 %,
  en accumule 145 % (115 % et 183 % à un point près) ; les systèmes 2 et 3
  accumulent l'inverse, des réserves de 526 % et 113 % du PIB, qui mesurent la
  marge que le coefficient d'équilibre, jamais appliqué, aurait à distribuer.
  *[Ces chiffres sont ceux de `main` après le rebasage : la session avait
  mesuré 150 % et 108 % sur une base antérieure au profil de carrière lu chez
  l'INSEE, et son message de commit les porte encore.]* Six tests dans
  `test_cout.py`, un dans `test_web.py` pour l'échelle négative, le plan de la
  page Coût compte une entrée de plus.

- **19 septembre 2026, la frise des flux, dans un dépliant.** La seconde
  pièce reprise du même simulateur : son registre année par année, où chaque
  colonne est un compte qui tombe juste. Ici, par système et par année de 2026
  à 2070 : ce qui rentre dans la caisse, ce qui en sort, le pied de la caisse
  coloré de ce qui manque (emprunté) ou de ce qui reste (placé), et dessous
  le stock en chiffres, du 1er janvier au 31 décembre, intérêts et emprunt
  compris ; le 31 décembre d'une année, rapporté au PIB de la suivante, est
  son 1er janvier. Le stock n'est pas dessiné à l'échelle des flux, dont il
  vaut jusqu'à cinquante fois la hauteur : il est écrit. Un système à la fois,
  par les onglets des grilles de Cas types, dont la feuille de style apprend
  le système actuel. Livré : `frise_flux` et `AnneeFrise` dans `gabarit.py`,
  `friseFlux` dans `gabarit.js`, la section « La frise des flux » sur la page
  Coût dans les deux rendus, entre la dette et la garantie, les styles
  `.frise` et `.donnees-frise`. Ce que la frise ne reprend pas de l'artifact :
  ses cinq voies (livret, fonds, caisse, deux dettes) et son zoom, parce que
  le modèle n'a qu'une caisse et un stock, et que quarante-cinq colonnes se
  parcourent au défilement. Quatre frises rendues par page, soit trois cents
  kilooctets de SVG dans le témoin de la page Coût.

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
celles d'un système qui ne se pilote pas, et le coefficient de 1,62 du
scénario 3 en 2070 se lit trop facilement comme une économie de 38 %.

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

- [x] 🔴 **Faire obéir les pages agrégées aux réglages du simulateur** `Coût · Cas types · Avantages`
  Les trois pages qui agrègent calculaient toujours sous les paramètres par défaut, quels que soient les réglages choisis dans le simulateur : changer la règle d'indexation déplaçait la pension affichée sur `/simuler` et pas un chiffre de `/cout`. Les deux pages disaient alors, sans le dire, deux choses différentes — et rien sur le site ne permettait de s'en apercevoir.
  *Fait le 19 septembre 2026.* Les trois pages lisent désormais les dix
  réglages de modélisation de l'adresse (`CLES_MODELISATION` : indexation,
  lissage, âge de référence, table, conversion des droits acquis, part de
  cotisation, foyer, projection, bascule, euros constants) et se calculent
  sous eux. Ce qui a permis de le faire sans toucher aux trente endroits qui
  lisent `contexte.base` : le `Contexte` porte le jeu de règles, et les pages
  agrégées reçoivent un contexte DÉRIVÉ par `pour()`, qui partage toutes les
  mémoires — les séries observées ne se rechargent pas, et les agrégats sont
  mémorisés par jeu de règles, six au plus. Le reste tient en trois pièces :
  les réglages suivent le lecteur, parce que `gabarit.lien` les ajoute à toute
  adresse interne (un état de module, posé par `rendre` et lui seul ; les
  formulaires visent `gabarit.route`, l'adresse nue, sinon le routeur
  doublerait la requête) ; chaque page agrégée porte le bloc « Les règles du
  calcul », qui est le formulaire du simulateur, écrit une fois et rendu
  deux ; et un encadré dit, dès qu'un réglage s'écarte du défaut, que les
  chiffres ne sont pas ceux du site, avec de quoi y revenir. Les carrières
  saisies dans l'adresse sont ignorées par ces pages — un agrégat n'a pas
  d'individu —, et une adresse qui ne porte QUE des réglages ne déclenche
  plus de calcul sur `/simuler` : sans quoi le bandeau aurait calculé d'office
  une carrière que personne n'a saisie. Tant que rien n'est changé, les trois
  pages et leurs adresses sont celles d'avant, au caractère près ; trois
  témoins de plus fixent les pages réglées, un quatrième le simulateur réglé
  sans carrière. Ce que cela ne règle pas, et qu'il ne faut pas laisser
  croire : ces pages croisent douze cas types avec des générations, pondérés
  par les effectifs des caisses. Elles obéissent aux mêmes RÈGLES que le
  simulateur, elles ne calculent pas la carrière qu'on y a saisie — une
  carrière n'a pas de poids dans une population.

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

### 24. Convertir les droits acquis à l'âge de départ effectif, par défaut — `abandonnée`

Abandonnée le 19 septembre 2026, après mesure. La raison est en bas, sous
« Ce qui est délibérément en bas » : le réglage qu'elle proposait fait dépendre
de l'âge de départ la valeur d'un passé qui, lui, ne dépend pas de l'âge de
départ. Les actions 23, 31 et 34 qui la citent renvoient donc là.

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

   **Quatrième passe, 19 septembre 2026 : tout ce qui existe, par caisse et par
   année.** Demandé : « chaque nombre de personne pour chaque régime pour
   toutes les années que les régimes ont existé », pour tracer le coût des
   retraités actuels et voir comment fluctue le coût réel d'une réforme.

   **La demande telle quelle n'est pas satisfiable, et il vaut mieux le dire
   une fois.** Aucun producteur ne publie la matrice complète. Le mur n'est pas
   le même selon ce qu'on cherche : pour les MASSES, il est à 1979 et il est
   bas ; pour les EFFECTIFS par caisse, il est à 2004 côté source unique, et
   plus haut caisse par caisse. Ce qui suit est l'état exact des lieux.

   - **Les masses, elles, remontent à 1979, et c'était le gisement le plus
     sous-estimé.** Les rapports à la CCSS sont publiés depuis 1979 et **le
     lecteur PDF du dépôt les ouvre** : 19 043 lignes lisibles sur 19 306 pour
     celui de septembre 1996, 11 767 pour 2003, 19 953 pour 2010.

     **Correction, apportée par le recensement des quarante-sept millésimes.**
     Cette passe avait écrit que la croyance du dépôt — `PREMIERE_ANNEE_LISIBLE
     = 2013`, les rapports de 2007 à 2012 « chiffrés », ceux de 2004 à 2006
     compressés — était « fausse du lecteur, et vraie seulement de son
     parseur ». **C'est inexact, et le compte de mots le dit** : 2007, 2008 et
     2011 rendent ZÉRO mot, 2009 en rend 76, 2012 en rend 3 887. Le lecteur
     échoue bel et bien sur cette fenêtre-là. Le dépôt se trompait seulement
     sur ses BORDS : 2004, 2005 et 2006 rendent 83 502, 445 070 et 97 940 mots,
     et 2010 en rend 190 989. **Quarante millésimes sur quarante-sept sont
     lisibles**, tout 1979-2006 compris, pour 6,1 millions de mots ; la fenêtre
     fermée est 2007-2009 et 2011, 2012 étant trop maigre pour compter.

     Et ce qu'on y trouve est exactement la série de coût cherchée : le rapport
     de 1996 porte « LES PRESTATIONS VERSÉES EN 1995, millions de francs »,
     colonne vieillesse, vingt-deux régimes nommés
     — CNAVTS 303 725, fonctionnaires 148 603, exploitants agricoles 79 799,
     collectivités locales 28 993, SNCF 26 566, EDF-GDF 15 287, mines 13 036,
     marins 5 963, RATP 3 778, CRPCEN 2 171, Banque de France 1 528. Quarante-
     sept millésimes existent sur le même modèle.

     Ce n'est pas une passe de recherche qui les moissonne : chaque année a sa
     mise en page, et c'est un chantier à part entière. Mais **la porte est
     ouverte, et le dépôt la croyait fermée.**

   - **Les effectifs, caisse par caisse : voici où est le mur pour chacune.**

     | source | ce qu'elle donne | couverture |
     |---|---|---|
     | Cnav, abrégé ch. 01 | cotisants ET retraités, régime général | **1963-2023** |
     | CNAVPL, recueil | cotisants réels, et par section | **1950-2025** |
     | CNRACL, recueil I.1.3 | cotisants et pensionnés, moyenne annuelle | 2012-2022 |
     | DREES EACR (dans le dépôt) | retraités de droit direct, 28 caisses | 2004-2024 |
     | COR, classeur par régime | retraités ET cotisants, 23 régimes | 2010-2070 |
     | CCSS, fiche 4.1 | cotisants, 15 caisses, à l'unité | 2021-2024 |
     | Cnav, abrégé ch. 07 | cotisants de la compensation, régime général compris | un an par édition |
     | PQE « Retraites » | cotisants, 18 régimes, en milliers | 1992-2012, années creuses |
     | CDC, open data | cotisants Ircantec et CNRACL | 2014-2021 / 2022 |

     Autrement dit : **avant 2004, il n'existe pas de source unique donnant les
     effectifs de toutes les caisses**, et il faut les prendre caisse par
     caisse, là où elles ont tenu leur propre histoire. Deux l'ont fait
     remarquablement — la Cnav depuis 1963, la CNAVPL depuis 1950. Les autres
     commencent où leur annuaire commence.

   - **Ce qui est désormais disponible en une commande :
     `scripts/fetch/cor_regimes.py`.** Il va chercher le classeur par régime du
     COR et en tire **52 049 valeurs — 23 régimes, 2010 à 2070, 36 blocs** :
     effectifs de retraités de droit direct et de cotisants (femmes, hommes,
     ensemble), masses de prestations et de pensions de droit direct et dérivé,
     dépenses totales, ressources totales et techniques, solde technique et
     solde élargi, réserves, âge moyen de départ, rapport démographique et
     pension relative — en milliards d'euros constants ET en part de PIB. C'est
     la seule source qui porte l'observé et le projeté dans le même tableau,
     par caisse ; elle couvre l'Ircantec et le RCI, que la CCSS ne couvre pas ;
     et elle éteint les régimes fermés par la réforme de 2023 au lieu de les
     reconduire — la CNIEG passe de 8,62 Md€ de dépenses en 2023 à 3,91 en
     2070, la SNCF de 5,40 à 2,03, quand la CNAV va de 159,95 à 317,77 et
     l'Ircantec de 4,18 à 11,69.

     Le script porte ses trois pièges dans son docstring, et n'en corrige aucun
     en silence : deux feuilles portent des unités sous un en-tête qui annonce
     des millions, l'année de départ varie d'une feuille à l'autre, et la FPE
     reste d'un seul tenant.

   - **Un jeu DREES qu'on avait déclaré inexistant, et ce qu'il vaut.** L'open
     data de la DREES expose bien un jeu « Les effectifs de retraités, montants
     de pensions et âges de départ », dont une pièce s'appelle « Rapport des
     effectifs de retraités et de cotisants de 2004 à 2016 ». Lu : il est TOUS
     RÉGIMES, et son dénominateur de cotisants est l'emploi intérieur de
     l'INSEE, pas un décompte de caisse. Il ne sert donc pas à ventiler — mais
     il donne une série de contrôle tous régimes, 2004-2016, et il corrige une
     formulation trop large des passes précédentes : l'open data DREES n'est
     pas vide, il est simplement au mauvais niveau.

   **Pour l'objectif annoncé — le coût des retraités actuels, et ce qu'une
   réforme y déplace — voici ce qui manque encore**, et c'est court : le
   classeur du COR donne les masses et les effectifs par caisse de 2010 à 2070
   avec les ressources et les soldes, ce qui suffit à chiffrer une réforme
   appliquée au stock ; l'avant-2010 des masses se prend dans l'archive CCSS,
   qui est ouverte mais non moissonnée ; et les subventions d'équilibre de
   l'État, régime par régime, sont dans le bloc « structure de financement » du
   même classeur, qu'il reste à lire — il est dans les feuilles, sous forme de
   parts, et le script le laisse passer faute d'en-tête d'années.

   **Cinquième passe, 19 septembre 2026 : les deux chantiers, faits.**

   - **Le bloc « structure de financement » est lu.** Il échappait au script
     parce que son en-tête ne porte que SIX années — 2010, 2023, 2030, 2040,
     2050, 2070 — là où les autres blocs en portent soixante et une. Le seuil
     descend à quatre, la reconnaissance se durcit en échange (des entiers,
     dans la fenêtre, distincts, strictement croissants), et un seul bloc
     s'ajoute : 1 183 valeurs, de 52 049 à 53 232.

     C'est **ce qui sépare le coût d'une réforme pour l'État de son coût pour
     les caisses**. Part du financement en 2023 puis en 2070 : contribution
     d'équilibre de l'État à la FPE 86,0 % puis 81,3 % ; subvention
     d'équilibre à la SNCF 60,8 % puis 94,5 %, à la RATP 60,8 % puis 92,3 %,
     aux mines 81,1 % puis 91,8 %, au FSPOEIE 76,7 % puis 85,1 %, à l'ENIM
     76,3 % puis 66,8 %. Et le **besoin de financement**, que personne ne
     couvre : 7,1 % à la CNRACL en 2023 et 48,6 % en 2070, 0 % puis 35,5 % à
     l'Ircantec, 0,8 % puis 19,3 % à la CNAV.

   - **L'archive CCSS est recensée, et elle me contredit.** Les quarante-sept
     millésimes ont été téléchargés et passés au lecteur : **quarante-six
     lisibles, 6,1 millions de mots**, un seul échec — 1995, sur un opérande
     malformé que le lecteur ne savait pas sauter, corrigé depuis, ce qui fait
     quarante-sept. Mais le compte de mots dit aussi que **2007, 2008 et 2011
     rendent zéro mot, 2009 en rend 76 et 2012 en rend 3 887** : la fenêtre
     que le dépôt disait fermée l'est bien. Il se trompait sur ses bords, pas
     sur son centre.

   - **`scripts/fetch/ccss_regimes.py` moissonne la mise en page moderne.**
     Chaque fiche de régime ouvre sur un « Tableau 1 • Données générales » qui
     porte, pour le régime seul et année par année : cotisants vieillesse,
     bénéficiaires vieillesse ventilés droit direct et droit dérivé, produits
     nets dont cotisations, charges nettes dont prestations. **5 662 valeurs,
     22 caisses, 2011-2025.** C'est la seule source qui donne les EFFECTIFS et
     les MASSES d'un régime dans le même tableau — la fiche 4.1 n'en est qu'un
     extrait.

     Couverture par caisse, en années : MSA salariés, MSA exploitants et CNIEG
     14 ; Agirc-Arrco et CNRACL 13 ; Ircantec et CNAVPL complémentaire 12 ;
     SNCF et CANSSM 10 ; RATP 9 ; RSI vieillesse 8 ; ENIM 7 ; CRPCEN et
     FSPOEIE 6 ; Banque de France 4 ; les plus petites 2 ou 3.

     Deux difficultés ont dû être traitées, et elles se reverront. **Le
     chapitre des régimes n'a pas de numéro fixe** : il est le 5 en 2019 et
     autre chose en 2017, où le 5 porte « du régime général aux autres régimes
     de base » — le chercher au chapitre 5 ne rendait qu'UN régime pour ce
     millésime. Et **le même régime change de graphie d'un rapport à l'autre**,
     la mise en page mangeant les espaces à des endroits différents :
     cinquante et un libellés pour une vingtaine de caisses. Une table de
     motifs canoniques les ramène à un code, et le fichier produit garde tous
     les titres vus sous chaque code, pour qu'on puisse vérifier.

     Ce qui reste : les libellés de SÉRIE ont les mêmes variantes de casse que
     les titres avaient — « Chargesnettes » et « CHARGESNETTES » cohabitent —
     et mériteraient la même table ; et la moisson s'arrête à la mise en page
     moderne, l'avant-2013 ayant une fiche de régime différente à chaque
     époque.

   **Sixième passe, 19 septembre 2026 : l'avant-2013 ne se moissonne pas, et
   voici les mesures qui le disent.** Demandé : moissonner aussi l'avant-2013.
   La réponse est non, pour trois raisons indépendantes, chacune mesurée sur
   les trente-deux millésimes concernés. Aucune ne se contourne en insistant.

   1. **Les deux ancres du moissonneur moderne sont absentes, partout.** Zéro
      titre « Données générales » et zéro entrée de sommaire numérotée dans
      TOUS les rapports d'avant 2013 — vérifié sur 2000, 2003, 2005, 2006 et
      2010. Le script reconnaît une fiche de régime par son numéro au
      sommaire, puis son tableau par son titre ; ni l'un ni l'autre n'existe.

   2. **De 1979 à 1998, il n'y a pas de tableau à colonnes d'années.** Le
      compte est sans appel : zéro en-tête d'années croissantes dans chacun
      des dix-huit millésimes, à une exception près (1987, un seul). Ces
      rapports présentent des tableaux d'UNE année à colonnes de RISQUES —
      celui de 1996 donne « LES PRESTATIONS VERSÉES EN 1995 », vingt-deux
      régimes en lignes et les risques en colonnes. C'est exploitable en
      principe, mais sporadique en pratique : le meilleur bloc par rapport
      compte de 0 à 7 lignes de régime selon l'année, et la plupart des
      millésimes n'en portent aucun.

   3. **De 2000 à 2006 et en 2010, ce sont des scans océrisés dont la
      géométrie ne tient pas.** Il y a bien des en-têtes d'années — 31 en
      2000, 151 en 2001, 203 en 2003, 342 en 2010 — mais **une part énorme est
      dans le désordre** : 142 sur 293 en 2001, 47 sur 226 en 2006, 91 sur 433
      en 2010. Pire, la reconstitution de mise en page **coupe les milliers** :
      « 2 937,4 » ressort en « 937,4 » d'un côté et « 2 » de l'autre, sur la
      même ligne. Changer la tolérance de regroupement n'y fait rien — essayé
      à 3,0, 1,5, 0,8 et 0,3. Et l'OCR mange les libellés : « Prestations
      extraléaales », « nrnrfi iitc affprlAcl ».

      Faute de sommaire, il faudrait reconnaître le régime à son nom dans la
      prose. **C'est le piège** : appliqués hors d'un titre de sommaire, les
      motifs de la table canonique se trompent — « Régimes de non-salariés
      non-agricoles » tombe sur `msa_salaries`, une ligne sur le déficit d'une
      branche tombe sur un régime. Ce qu'on produirait serait faux sans le
      dire, ce qui est le seul résultat que ce dépôt refuse.

   **Ce que la passe laisse quand même, et qui sert.** Deux choses sont
   entrées dans `ccss_regimes.py` :

   - `rapports_tous()`, l'index de l'archive SANS le plancher de 2013 de
     `ccss_transferts_retraite`, qui était juste pour les séries que ce
     module-là certifie et faux pour explorer ;
   - **la réconciliation entre rapports**, qui est la défense qu'il aurait
     fallu pour l'ère ancienne et qui vaut déjà pour la moderne. Chaque
     rapport porte quatre ou cinq exercices : une année donnée est donc lue
     plusieurs fois. On ne garde une valeur que si toutes les lectures
     s'accordent à 1 % près ; sinon on ne tranche pas, on écarte et on verse
     la valeur aux `conflits`, où elle reste consultable.

     **Le résultat sur la moisson moderne justifie à lui seul le garde-fou** :
     412 lectures sur 5 662 ne s'accordent pas, soit 7,3 %, et la moisson
     tombe de 5 662 à 5 250 valeurs. *(Le mot « contrôlées » écrit ici d'abord
     était trop fort, et la passe suivante le corrige : seules 20 % des valeurs
     sont lues par deux rapports et donc réellement confrontées.)* Les conflits mêlent des
     révisions légitimes — 1 282 248 contre 1 302 845 assurés cotisants à la
     MSA salariés en 2014, 1,6 % d'écart — et des lectures franchement
     fausses : 78 874 contre 571 193 pour la même case. Sans confrontation,
     les secondes seraient passées pour des données.

   **Septième passe, 19 septembre 2026 : les 412 conflits examinés, et quatre
   bogues qu'ils ont dénoncés.** Demandé : relancer la moisson avec le
   garde-fou et vérifier les conflits. Je n'en avais regardé que cinq. Les
   examiner tous a montré qu'ils n'étaient pas surtout des révisions de la
   DSS, mais surtout des fautes de mon lecteur. Quatre corrections en sont
   sorties, et la moisson passe de 5 250 valeurs et 412 conflits à **6 807
   valeurs et 195 conflits, dont plus aucune contradiction interne**.

   1. **Une fiche porte PLUSIEURS « Données générales ».** Le titre les
      distingue — « toutes branches », « Ensemble des risques », « régime
      unifié », « du régime vieillesse complémentaire des indépendants » — et
      je les fondais : un même rapport donnait alors deux valeurs pour la même
      case, 8 et 685 en charges nettes de la MSA salariés en 2013. Le titre
      entre donc dans la clé.
   2. **Mais le titre brut ne peut pas servir de clé** entre rapports : la
      mise en page écrit « Donnéesgénérales » ici et « Données générales » là.
      Le garder tel quel a fait tomber la confrontation de 30 % à 19 % des
      valeurs — j'avais réparé une fuite en en ouvrant une autre. Le titre est
      donc réduit à son QUALIFICATIF, sans le numéro, la puce ni les mots
      « données générales » eux-mêmes.
   3. **« Retraite complémentaire obligatoire des NON-SALARIÉS AGRICOLES »
      porte `salariesagricoles` en sous-chaîne.** Le RCO des exploitants
      tombait donc sur la MSA salariés, qui se contredisait elle-même — 659 061
      contre 522 534 cotisants en 2012, 2 503 203 contre 506 549 bénéficiaires.
      Son motif, que j'avais supprimé en refondant la table, est remis en tête.
   4. **L'Agirc et l'Arrco n'ont fusionné qu'au 1er janvier 2019.** Avant, ce
      sont deux régimes, deux fiches, deux comptes ; les fondre sous un seul
      code mélangeait leurs séries d'avant-fusion. Trois codes désormais.

   **Ce que le garde-fou ne fait PAS, et c'est la nuance qui manquait.** Il ne
   confronte que ce qui est lu deux fois : **1 353 valeurs sur 6 807, soit
   20 %**. Les 80 % restantes ne sont pas « contrôlées » — elles sont
   seulement non contredites, ce qui n'est pas la même chose. Écrire
   « valeurs contrôlées » pour l'ensemble, comme la passe précédente l'a fait,
   était trop fort.

   **En revanche, le contrôle par source tierce est excellent.** Cotisants
   vieillesse de la moisson, confrontés à ce que les autres sources disent :
   CNIEG 2023, 135 775 — la fiche 4.1 dit 135 775, à l'unité ; SNCF 2023,
   112 621 — la fiche 4.1 dit 112 621, à l'unité ; CNRACL 2021, 2 189 791 — la
   fiche 4.1 ET le recueil de la caisse disent 2 189 791, à l'unité. Seul
   l'écart CNIEG 2021 subsiste, 135 944 contre 135 427, soit 0,4 %, la fiche
   du régime et le tableau de synthèse ne tombant pas exactement d'accord.

   **La leçon, pour la prochaine fois.** Un garde-fou qui rejette 7 % des
   lectures ne dit pas que la source est mauvaise : il dit d'abord d'aller
   lire ce qu'il rejette. Les quatre bogues étaient tous dans mon code, pas
   dans les rapports.

   **Huitième passe, 19 septembre 2026 : les 195 conflits ont dénoncé une
   note de bas de page, et l'attribution des fiches n'est toujours pas sûre.**

   - **Le gros morceau : une NOTE DE BAS DE PAGE lue comme un en-tête.** La
     SNCF concentrait 53 des 195 conflits, dont 40 sur la seule année 2017,
     avec des valeurs qui croissaient avec le millésime du rapport — 21, 34,
     69, 116. La cause : « *(***) Le taux de cotisation T2 a été fixé à
     11,81 % entre le 1er janvier 2017 et le 30 avril 2017…* » porte trois fois
     2017, et mon détecteur d'en-tête, qui se contentait d'années NON
     DÉCROISSANTES, la lisait en colonnes `[%, 2017, 2017, %, 2017]`. **Toute
     la fiche de la SNCF était datée de 2017.** Les années doivent être
     STRICTEMENT croissantes, et c'est corrigé.

     Le résultat se voit : la SNCF donne désormais une série continue et
     décroissante, 156 963 cotisants en 2012 à 105 610 en 2025, dont trois
     points tombent à l'unité sur la fiche 4.1 — 123 019 en 2021, 112 621 en
     2023, 108 877 en 2024.

   - **L'attribution des tableaux aux fiches reste une heuristique, et elle
     se trompe.** Le numéro de fiche est répété en tête de chaque page, pas
     au-dessus de chaque tableau ; le chercher en remontant donne parfois la
     fiche précédente. Dans le rapport de 2025, un tableau de la CNRACL était
     porté au crédit de la SNCF. **Deux remèdes ont été essayés et tous deux
     ont fait pire** : préférer le titre du tableau quand il nomme le régime a
     donné le SRE à la CNRACL et un tableau SNCF à la CNIEG ; délimiter les
     fiches par intervalles a fait tomber presque tout dans un seul régime.
     Les deux sont annulés, et l'heuristique assumée dans le docstring.

   - **Faute de la réparer, on la SURVEILLE, par deux filets.** Le premier,
     grossier : une valeur éloignée d'un facteur trois de la médiane de sa
     propre série n'est pas une évolution — 237 écartées. Il ne voit pas une
     confusion entre régimes de taille voisine, et ne prétend pas la voir. Le
     second est exact : **une caisse n'a qu'un effectif de cotisants pour une
     année, donc deux tableaux qui remplissent la même case se dénoncent
     eux-mêmes** — 543 écartées. C'est lui qui attrape 135 775 et 112 621 tous
     deux portés à la CNIEG en 2023, ou 2 144 492 et 2 016 662 portés à la
     CNRACL. On n'arbitre pas : les deux partent, parce que rien dans le texte
     ne dit lequel est le bon.

   **Le bilan, et il est volontairement plus petit qu'avant.** De 6 807
   valeurs sans filet à **5 289 valeurs passées par trois contrôles
   indépendants** — accord entre rapports, ordre de grandeur, unicité de la
   case. Les contaminations connues sont devenues des TROUS et non des erreurs
   silencieuses : la CNIEG n'a plus de valeur pour 2023, et c'est préférable à
   112 621, qui était celle de la SNCF.

   Les contrôles par source tierce passent tous : SNCF 2021, 2023 et 2024 à
   l'unité sur la fiche 4.1 ; CNRACL 2021 à 2 189 791 et 2013 à 2 194 861, soit
   exactement la fiche 4.1 et le recueil de la caisse ; MSA exploitants 2021 à
   445 511, exactement la fiche 4.1.

   **Neuvième passe, 19 septembre 2026 : l'attribution est réparée, et le bon
   niveau était la PAGE.** Trois tentatives avaient échoué faute d'avoir
   regardé la source. La quatrième a commencé par là, et la cause est nette :
   **le rapport de 2025 sort ses pages dans l'ordre INVERSE des fiches** —
   marqueurs 4.15, puis 4.14, puis 4.13 à mesure que les lignes avancent.
   Chercher le marqueur « le plus proche au-dessus » y donne donc
   systématiquement la fiche VOISINE. D'où le tableau « de la branche
   vieillesse de la CNRACL » porté au crédit de la SNCF, et la CNRACL héritant
   du SRE.

   Le numéro de fiche est une TÊTE DE PAGE : il vaut pour sa page, et pour
   elle seule. Le bon niveau n'était donc ni le marqueur le plus proche, ni le
   titre du tableau, ni un intervalle — c'était la page, qu'il a fallu exposer
   dans `lecture_pdf` par une fonction `lignes_par_page`. La vérification
   tient en une ligne : sur les treize pages du rapport de 2025 qui portent un
   « Données générales », **chacune porte exactement un marqueur, et c'est le
   bon**.

   `lecture_pdf` a été scindé pour cela en `_fragments` et `_assembler`, dont
   `lignes_pdf` et `lignes_par_page` se servent toutes deux ; le refactor est
   neutre, contrôlé sur le rapport de 2025 — mêmes 15 485 lignes, en 505
   pages, à l'identique.

   **Un garde-fou est tombé avec le bogue, et c'est le signe que c'était le
   bon.** Le détecteur de « case remplie deux fois » écartait 318 valeurs. Une
   fois l'attribution réparée, on a regardé ce qu'il rejetait : **les 133 cas
   venaient tous de tableaux DIFFÉRENTS** — la table vieillesse d'une fiche
   contre sa table « toutes branches », dont les lignes portent les mêmes
   libellés sans mesurer la même chose : 10 577 contre 5 751 millions de
   prestations légales nettes à la MSA salariés en 2016. Ce n'était pas une
   contradiction, c'était deux mesures. Le détecteur ne rejette donc plus que
   la contradiction vraie, au sein d'un MÊME tableau — **et il n'en trouve
   plus aucune**.

   **L'état après réparation** : 5 419 valeurs, 25 régimes, 2011-2025, et
   **zéro case remplie deux fois**. Restent 148 désaccords entre rapports et
   191 écarts de magnitude, tous deux consultables dans le fichier produit.

   Les contrôles par source tierce passent **neuf fois sur dix à l'unité** —
   SNCF 2023 et 2024, CNRACL 2013, 2021 et 2024, CNIEG 2023 et 2024, MSA
   exploitants 2021 et 2024 — la dixième étant un trou, la SNCF de 2021.
   *(La passe suivante le comble : neuf contrôles sur neuf.)* Et deux séries qui étaient fausses ou absentes
   sont maintenant justes : la CNIEG de 2023 vaut 135 775 et non plus 112 621,
   qui était la SNCF ; la CNRACL de 2024 vaut 2 151 694 et non plus 2 008 352,
   qui était le SRE.

   **La leçon, et c'est la même que deux passes plus tôt.** Les trois
   tentatives ratées ont toutes consisté à corriger une heuristique par une
   autre sans ouvrir le document. Quinze lignes de diagnostic — afficher, pour
   chaque tableau, le marqueur trouvé et le titre — ont donné la réponse
   immédiatement.

   **Dixième passe, 19 septembre 2026 : pourquoi la SNCF de 2021 manquait.**
   Le trou n'était dans aucun des trois garde-fous — la valeur n'avait jamais
   été LUE. Deux causes, et elles se sont révélées différentes l'une de
   l'autre.

   - **Le tableau de la fiche SNCF est une IMAGE en 2022 et en 2023.** Leurs
     pages ne portent que le titre, la ligne d'unité, la source et les notes :
     aucun chiffre, aucun en-tête d'années. Ce n'est pas réparable, et il faut
     le savoir — toutes les fiches ne sont pas en texte tous les ans.

   - **Le numéro de fiche était collé en FIN de ligne.** Le rapport de 2022
     écrit « *correspond à la moyenne de ces deux taux . 5.6* » : le marqueur y
     est, mais mon motif l'ancrait au début de ligne. Six pages à tableau, sur
     l'ensemble des millésimes, n'avaient aucun marqueur en tête ; **cinq
     l'avaient en queue** — une en 2014, trois en 2016, une en 2022, une en
     2024. Le motif de secours les récupère, et il n'est essayé que si rien
     n'a été trouvé en tête, pour ne pas fabriquer d'ambiguïté.

   Cela suffit à combler le trou : la SNCF de 2021 vaut 123 019 cotisants,
   lus dans le rapport de 2022, soit exactement ce que la fiche 4.1 écrit. La
   série est désormais continue de 2012 à 2025, de 156 963 à 105 610.

   **La valeur existait bien ailleurs, et c'est une remarque utile pour la
   suite** : « 123019 » se trouve en toutes lettres dans les rapports de 2022
   et de 2023, mais dans le TABLEAU DE SYNTHÈSE — la fiche 4.1 — que ce
   moissonneur ne lit pas, puisqu'il ne cible que les « Données générales » des
   fiches. Les deux familles de tableaux se complètent : quand la fiche d'un
   régime est en image, la synthèse peut encore porter ses effectifs. La lire
   aussi est le prochain gain facile.

   **État final : 5 493 valeurs, 25 régimes, 2011-2025, zéro case remplie deux
   fois, et neuf contrôles indépendants sur neuf à l'unité.** Les caisses les
   mieux servies : CNRACL 720 valeurs, MSA salariés 599, MSA exploitants 589,
   SNCF 506, CNAVPL complémentaire 430, RATP 340, CANSSM 332, Agirc-Arrco 322,
   CNIEG 288.

   **Onzième passe, 19 septembre 2026 : la ventilation État/caisses par
   régime est posée.** C'est la première fois de cette série de passes que
   quelque chose ENTRE dans le modèle et non dans un relevé.

   `equilibre.py` savait que l'État verse une contribution d'équilibre au
   système ; il ne savait pas à QUI. La question que la page « Coût » ne
   pouvait donc pas poser est pourtant celle qui décide du coût réel d'une
   réforme : un scénario qui remplace tous les taux par 18 % rend-il de
   l'argent à l'État, ou en demande-t-il aux caisses ? La réponse dépend du
   régime, et l'écart est énorme :

   | régime | l'État finance, 2023 | 2070 | découvert 2070 |
   |---|---:|---:|---:|
   | fonction publique d'État | 86,0 % | 81,3 % | — |
   | mines (CANSSM) | 81,1 % | 91,8 % | — |
   | FSPOEIE | 76,7 % | 85,1 % | — |
   | ENIM | 76,3 % | 66,8 % | — |
   | SNCF | 60,8 % | 94,5 % | — |
   | RATP | 60,8 % | 92,3 % | — |
   | CNBF | — | — | 57,6 % |
   | CNRACL | — | — | 48,6 % |
   | Ircantec | — | — | 35,5 % |
   | RCI | — | — | 23,3 % |
   | CNAV | — | — | 19,3 % |

   Deux familles s'y lisent d'un coup d'œil, et elles ne réagiront pas de la
   même façon à une réforme : les régimes que l'État porte — et qu'il porte de
   PLUS EN PLUS, la SNCF passant de 61 % à 95 % — et ceux dont le déficit
   n'est couvert par personne, où c'est la caisse qui encaisse.

   **Ce qui est livré** : `data/reference/regimes/structure_financement.csv`,
   930 valeurs, 22 régimes, huit postes, certifié par
   `verifier_donnees.py` contre le classeur du COR ; la source déclarée dans
   `data/sources.yaml` sous `cor_regimes` ; et
   `donnees/financement_regimes.py`, exposé par `Simulateur.financement_regimes`.

   **Quatre limites, dans l'en-tête du fichier et dans le lecteur**, parce que
   c'est le genre de série qu'on utilisera sans relire sa provenance :

   1. **Le millésime est juin 2024**, seul publié, quand le reste du dépôt
      tourne sur le COR 2026. Les mélanger coudrait deux exercices.
   2. **Les années sont éparses** — 2010, 2015, 2023, 2030, 2040, 2050, 2070 —
      et le lecteur REFUSE d'interpoler : `ventilation()` lève sur une année
      non publiée plutôt que d'inventer une trajectoire que personne n'a
      calculée.
   3. **Les parts ne somment pas toujours à un** : 100 couples sur 134 y sont
      à un millième près, les autres s'en écartent jusqu'à onze pour cent.
      Rendues telles que publiées, avec `somme()` pour le vérifier avant de
      conclure.
   4. **La fonction publique d'État est d'un seul tenant**, civils et
      militaires confondus.

   Un choix mérite d'être dit : **les impôts et taxes affectés ne comptent PAS
   dans `part_etat`**. Un impôt affecté n'est pas ce que l'État verse comme
   employeur ni ce qu'il comble comme garant : c'est une recette du système,
   d'une autre nature que les deux — `cout.py` tient déjà cette distinction
   pour l'agrégat, et la brouiller ici ferait dire deux choses au même mot.
   *[Corrigé le 19 septembre 2026 au soir.] Cette ligne justifiait le choix par
   « ils compensent des exonérations de cotisations, ce qui est une aide à
   l'activité et non un financement de la retraite ». Le choix tient, la raison
   non : la TVA qui compense les allègements finance la branche maladie.*

   **Ce qui n'est pas fait** : la page « Coût » n'affiche rien de tout cela. La
   série est chargée et lisible, elle n'entre dans aucun calcul de scénario.
   C'est le pas suivant, et il demande une décision de modèle plutôt que de
   données — que devient la contribution d'équilibre de l'État quand le taux
   devient 18 % ? Le programme ne le dit pas, et le dépôt ne le décidera pas à
   sa place.

   **Douzième passe, 19 septembre 2026 : la convention de l'État est
   tranchée, et elle n'était jusque-là vraie que par accident.** Le programme
   a décidé : **la contribution d'équilibre disparaît, l'État cotise à 18 %
   comme tout employeur.**

   **La vérification a changé le travail.** Avant d'implémenter, on a regardé
   ce que le code faisait déjà — et il faisait exactement cela. La
   contribution d'équilibre est marquée `contributive` dans `equilibre.py` :
   elle entre donc dans `part_contributive`, qui vaut **77,3 % des ressources
   — 65,6 de cotisations et 11,7 de contribution** —, et c'est toute cette
   enveloppe que les 18 % remplacent. Le terme reconduit, lui, est le
   COMPLÉMENT : `ressources × (1 − part_contributive)`, d'où la contribution
   est absente.

   Le raccord n'est juste que pour une raison qu'il fallait écrire :
   **l'assiette couvre TOUTES les branches**, traitements des fonctionnaires
   compris. Les 18 % qu'on leur applique SONT ce que l'État verse désormais ;
   reconduire la contribution en plus la compterait deux fois.

   **Ce qui a donc été fait n'est pas un changement de calcul mais une mise
   sous garde.** Le docstring de `ressources_de` disait « le programme ne dit
   pas ce qu'il en ferait » : il le dit maintenant, et c'est écrit. Et un test
   tient la convention, parce qu'elle reposait sur un drapeau que personne ne
   protégeait — décocher `contributive` sur ce poste aurait fait reconduire la
   contribution EN PLUS des 18 % sans qu'aucun test ne bronche.

   **Ce que la décision ne tranche pas, et qu'il faudra trancher.** Restent
   reconduits 23,1 % des ressources de 2024 : impôts et taxes affectés
   (1,944 point de PIB), transferts (0,665), **subventions d'équilibre
   (0,274)**, autres produits (0,303). Les subventions sont le cas le plus
   discutable, et la ventilation par régime dit pourquoi : elles financent
   60,8 % de la SNCF et de la RATP en 2023, 81,1 % des mines, 76,7 % du
   FSPOEIE, 76,3 % de l'ENIM — et **94,5 % de la SNCF en 2070**. Ce ne sont
   pas des cotisations d'employeur que 18 % remplaceraient : ce sont des
   charges de liquidation de régimes fermés, dont les cotisants ont disparu
   avant les retraités, et que le budget porte quoi qu'il arrive. Les
   reconduire reste l'hypothèse qui n'en ajoute aucune autre ; c'est aussi
   celle qui flatte le scénario 6, et le docstring le dit désormais avec les
   chiffres.

   **Treizième passe, 19 septembre 2026 : les subventions d'équilibre sortent
   aussi, et le scénario 6 perd un quart de point.** Le programme a tranché, et
   l'argument est le meilleur de toute cette série de décisions parce qu'il ne
   porte pas sur la comptabilité mais sur la NATURE de ce qu'on reconduisait.

   Une subvention d'équilibre comble le compte d'un régime dont les cotisants
   ont disparu avant les retraités — la SNCF, les mines, les marins, dont le
   classeur du COR dit qu'ils sont financés à 61, 81 et 76 % par le budget en
   2023, et la SNCF à 94,5 % en 2070. **Le scénario 6 fusionne tous les
   régimes : il n'y a plus de retraité sans cotisants dès lors qu'il n'y a plus
   qu'un régime.** L'objet de la subvention disparaît avec les régimes qu'elle
   équilibrait. Les pensions, elles, restent dues : servies comme les autres,
   pour partie recalculées à la baisse par le notionnel, pour partie portées
   par les cotisants du système unifié.

   **Ce que ça coûte, mesuré et non supposé** : le solde moyen du scénario 6
   sur les 45 années projetées passe de **−0,875 % à −1,117 % du PIB**, soit
   **0,242 point perdu**. C'est exactement ce que l'ancienne hypothèse lui
   offrait, et c'est le sens de la décision : reconduire une subvention dont
   l'objet a disparu était la dernière grande faveur faite au scénario 6.

   Porté dans `moteur/js/cout.js` comme le dépôt l'exige, témoins régénérés.

   **Ce qui reste reconduit à la fin de cette passe-là** : les impôts et taxes
   affectés (1,944 point de PIB en 2024), les transferts (0,665) et les autres
   produits (0,303). *[Corrigé.] Cette ligne ajoutait ici que « le même argument
   vaudrait pour les impôts — ils compensent des allègements de cotisations
   patronales qu'un système sans exonération ne consent pas ». C'est faux, et
   c'est la phrase que le dépôt avait lui-même démolie le matin même : la TVA
   qui compense les allègements finance la branche MALADIE, et le compte de la
   CNAV n'en porte aucune ligne. Les impôts affectés sont bien sortis, le soir
   du même jour, mais par un autre argument — quatorzième passe, ci-dessous.*

   **Une précaution que le programme a demandée et qu'on respecte** : rien n'est
   écrit au public. La page affiche les chiffres nouveaux, mais aucune prose
   n'explique encore ce fonctionnement — il faut d'abord vérifier que ces
   chiffres font un système cohérent.

   **Quatorzième passe, 19 septembre 2026 : les impôts et taxes affectés
   sortent aussi, et c'était la dernière des trois.** Le programme a tranché le
   soir même, et la décision exigeait d'abord une rétractation : l'argument par
   lequel on la lui avait proposée — « ils compensent des allègements de
   cotisations patronales qu'un système sans exonération ne consent pas » — est
   celui que le dépôt avait démoli le matin, en ouvrant le compte de la CNAV.

   **L'argument qui vaut est celui des 18 %** : un compte notionnel ne crédite
   que ce qui est assis sur un revenu d'activité. Un impôt affecté n'ouvre de
   droit à personne ; le porter au crédit d'un système qui ne rend que ce qui a
   été cotisé, c'est lui prêter une recette sans contrepartie. C'est le même
   argument qui a fait sortir la contribution d'équilibre et les subventions,
   et il ne doit rien à ce que ce poste compense ou ne compense pas.

   **Il fallait ne le retirer qu'une fois.** 38 % du poste sont les ressources
   du fonds de solidarité vieillesse (21,7 des 57,1 Md€ de 2024), et ce que ce
   fonds VERSE aux régimes — 19,6 Md€ — était déjà retiré par `retrait` depuis
   le matin. Sortir le poste en entier sans toucher au retrait aurait fait
   sortir la même somme deux fois. D'où `retrait_par_impot`, qui est cette
   somme et que le scénario 6 rend au compte à l'instant où le poste s'en va ;
   les quatre autres scénarios notionnels, qui encaissent toujours les impôts
   affectés, gardent le retrait entier.

   **Ce que la sortie coûte, remesuré le 19 septembre 2026 au soir** :
   **1,395 point de solde moyen**. Sur 2026-2070, le scénario 6 passe de
   −0,28 % du PIB, poste reconduit, à **−1,67 %**, contre −1,13 % pour le
   système actuel ; il est plus déficitaire que lui dans 33 des 45 années, ne
   revient à l'équilibre sur aucune, et son coefficient de 2040 descend de 0,94
   à 0,80. *Le jour de la décision, ces deux niveaux étaient −1,12 % et
   −2,51 % : ils ont monté depuis, la réversion ayant quitté les cinq scénarios
   notionnels. Le COÛT de la sortie, lui, n'a pas bougé.*

   **Les trois décisions prises ensemble** retirent au scénario 6 les 27 % de
   ressources qui n'acquièrent de droits à personne. Ce qui reste reconduit, et
   qu'aucun programme n'a tranché : les transferts (0,665 point de PIB) et les
   autres produits (0,303) — 7 % des ressources de 2024.

   **Ce qu'une session qui code devrait faire**, si elle reprend ce point :
   partir de la fiche 4.1 (2021-2024, à l'unité, script possible avec le
   téléchargeur de rapports CCSS que `ccss_transferts_retraite.py` porte
   déjà), compléter le régime général et l'Ircantec par leurs propres
   sources, et NE PAS coudre le PQE au bout : ses deux définitions ne se
   raccordent pas, et quatre années à l'unité près valent mieux qu'une série
   longue dont la moitié compte autre chose. L'urgence reste faible — la
   mesure du 19 septembre tient : sous la convention du programme, la
   pondération ne déplace pas le solde du scénario 6 d'un millième.
4. *Dire ce que le programme fait des ressources non cotisées.* **Les trois
   questions sont tranchées, par le programme lui-même, le 19 septembre
   2026.** La contribution d'équilibre de l'État disparaît : il cotise
   à 18 % comme tout employeur, et l'assiette couvrant toutes les branches, les
   traitements de ses agents y sont déjà. Les subventions d'équilibre
   disparaissent aussi, et l'argument n'est pas comptable mais logique — une
   subvention comble le compte d'un régime dont les cotisants ont disparu avant
   les retraités, et **le scénario 6 fusionne tous les régimes, si bien que
   cette catégorie cesse d'exister**. Cette ligne disait auparavant que ces
   subventions « survivent à toute réforme le temps que leurs pensionnés
   s'éteignent » : c'est faux d'une réforme qui fusionne, et les pensions en
   question sont servies comme les autres, pour partie recalculées par le
   notionnel, pour partie portées par les cotisants du système unifié.

   Les impôts et taxes affectés disparaissent enfin — 14,1 % des ressources,
   57,1 Md€ en 2024 —, et il faut dire par quel argument ce n'est PAS. Cette
   ligne demandait auparavant si « les 18 % remplacent aussi les 64 Md€
   d'impôts et taxes affectés, qui compensent pour l'essentiel des allègements
   de cotisations patronales que ce système ne consent pas ». La prémisse est
   fausse : la TVA qui compense les allègements finance la branche maladie, et
   le compte de la CNAV n'en porte aucune ligne. L'argument qui vaut est celui
   des 18 % eux-mêmes — un compte notionnel ne crédite que ce qui est assis sur
   un revenu d'activité, et un impôt affecté n'ouvre de droit à personne. La
   sortie coûte 1,395 point de solde moyen au scénario 6, six fois ce que
   coûtaient les subventions ; la quatorzième passe du point 3 la détaille.

   Ce qui reste reconduit, faute qu'aucun programme dise ce qu'il en ferait :
   les transferts (0,665 point de PIB en 2024) et les autres produits (0,303).
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

**C. Le périmètre, des deux côtés — `fait` le 19 septembre 2026.** Il disait
ceci : la recette suit le droit depuis septembre 2026, la dépense non ; le
rapport des droits directs s'applique à une base qui porte les droits dérivés,
1,5 point de PIB environ. C'est corrigé. La base est ventilée
(`part_droits_derives.csv`, le COR, 2010-2070, contrôlée contre la DREES à
0,06 point près), le rapport ne multiplie plus que les directs, et ce que les
scénarios font de la réversion est écrit. **Le programme a tranché le jour
même : seul le scénario 1 la sert**, les cinq autres la retirant comme tout
avantage non contributif — c'est le chemin de la Suède. Celui de l'Italie, qui
partage le capital du défunt, reste calculable sous
`convention_reversion="servie"`. Le détail est à la fin de ce journal.

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

- **Septembre 2026, les cinq points rendus, et remis.** La pièce a été posée,
  retirée le soir même sur un malentendu, puis reposée à l'identique : si une
  session future la retrouve dans l'historique sous les deux formes, c'est de
  cet aller-retour qu'il s'agit, et la version en vigueur est celle-ci.
  Demandé hors feuille de
  route : « on passe d'environ 28 % de cotisation à 18 + 5 ; affichons le
  salaire en y rajoutant 5 % de capitalisation non obligatoire, ça permet de
  mieux se rendre compte à taux égal cotisé ». Le scénario 6 porte donc une
  QUATRIÈME pièce, `taux_capitalisation_volontaire`, et le pilier reçoit dix
  points au lieu de cinq. Deux décisions, prises avec le demandeur : les cinq
  points entrent dans le total du 6, et la fiche de paie les met entièrement à
  la charge de l'assuré.

  Un seul compartiment, pas deux. Tout ce que le pilier produit est exactement
  proportionnel à son taux — les frais sont des pourcentages, l'allocation ne
  dépend que de l'horizon, aucun seuil n'intervient —, si bien que
  `part_volontaire` partage le capital et la rente sans les recalculer. Un test
  le vérifie contre le calcul complet fait à taux réduit : c'est deux fois
  moins de travail au rendu, et une seule chaîne à maintenir.

  **Le net baisse, et c'est la conséquence du second choix.** À coût du travail
  tenu fixe, la proposition rendait +73 € par mois à un non-cadre du privé né
  en 1990 ; les cinq points volontaires en coûtent 179, puisque personne ne les
  cofinance là où les vingt-trois points imposés sont partagés avec
  l'employeur. Le site écrit donc les DEUX nets partout : celui de qui verse,
  celui de qui ne verse pas, et la ligne « si vous ne la versez pas » dans le
  tableau de la fiche de paie.

  **Et sous le plancher, ces cinq points ne rapportent rien.** La garantie
  vieillesse est différentielle et compte les ressources sans regarder leur
  origine : elle reprend la rente volontaire euro pour euro. Un test fixe les
  deux régimes, sous le plancher et au-dessus ; les pages Méthode et Simuler le
  disent, parce que personne ne le devine. Ce qui reste à l'épargnant dans ce
  cas est le seul avantage propre à la capitalisation : un capital qui se
  transmet, et qui vaut le double.

  Ce que ça déplace : rien sur les scénarios 1 à 5, rien sur la pension de
  répartition du 6 hors garantie. Sur le total servi par le 6, la rente
  capitalisée double. Deux traces à nettoyer trouvées en chemin, sans rapport
  avec la demande : le bloc d'exemple SNCF du README avait dérivé (scénario 4 à
  5 390 € quand le modèle en servait 7 295), et `methodologie.md` écrivait
  encore que le pilier n'entre pas dans la garantie vieillesse, ce qui n'était
  plus vrai depuis le 19 septembre. Les deux sont corrigés. Reste ouvert : le
  taux de 5 % est celui que le demandeur a fixé, et il ne coïncide avec l'écart
  aux 28 % que pour un salarié du privé — un fonctionnaire, dont l'État verse
  jusqu'à 82,28 %, se voit rendre bien davantage que cinq points.

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

- **Septembre 2026, action 35, volet A, point 3, quatrième passe : tout ce qui
  existe, par caisse et par année.** Demandé : chaque effectif, chaque régime,
  chaque année d'existence, pour tracer le coût des retraités actuels et ce
  qu'une réforme y déplace.

  **La demande telle quelle n'est pas satisfiable, et le dire une fois vaut
  mieux que le contourner.** Aucun producteur ne publie la matrice complète, et
  le mur n'est pas au même endroit selon ce qu'on cherche.

  **Pour les MASSES, il est à 1979, et c'est la découverte de la passe.** Les
  rapports à la CCSS sont publiés depuis 1979 et le lecteur PDF du dépôt les
  ouvre : 19 043 lignes lisibles sur 19 306 pour celui de septembre 1996. Le
  dépôt croyait le contraire — `ccss_transferts_retraite.py` pose
  `PREMIERE_ANNEE_LISIBLE = 2013` et dit les rapports de 2007 à 2012
  « chiffrés ». C'est faux du LECTEUR, et vrai seulement de son PARSEUR, écrit
  pour la mise en page moderne. Et ce qu'on y trouve est la série de coût
  cherchée : « LES PRESTATIONS VERSÉES EN 1995, millions de francs », colonne
  vieillesse, vingt-deux régimes nommés. Quarante-sept millésimes sur le même
  modèle. Les moissonner est un chantier — chaque année a sa mise en page — mais
  **la porte est ouverte et le dépôt la croyait fermée**.

  **Pour les EFFECTIFS par caisse, il n'existe pas de source unique avant
  2004.** Il faut les prendre caisse par caisse, là où chacune a tenu son
  histoire : la Cnav depuis 1963, la CNAVPL depuis 1950, la CNRACL depuis 2012,
  l'EACR de la DREES pour 28 caisses depuis 2004, le COR pour 23 régimes de 2010
  à 2070. Le tableau complet des couvertures est au point 3.

  **Livré, et pas seulement relevé : `scripts/fetch/cor_regimes.py`.** Il tire
  du classeur par régime du COR **52 049 valeurs — 23 régimes, 2010-2070, 36
  blocs** : effectifs de retraités et de cotisants ventilés par sexe, masses de
  prestations et de pensions, dépenses totales, ressources, soldes technique et
  élargi, réserves, âge de départ, en euros constants ET en part de PIB. C'est
  de quoi chiffrer une réforme appliquée au stock, caisse par caisse, avec les
  régimes fermés qui s'éteignent au lieu d'être reconduits. Les trois pièges du
  classeur sont dans son docstring et aucun n'est corrigé en silence.

  **Une formulation des passes précédentes était trop large** : « open data
  DREES — rien » est faux au sens strict. Le jeu « Les effectifs de retraités,
  montants de pensions et âges de départ » existe et porte une pièce « Rapport
  des effectifs de retraités et de cotisants de 2004 à 2016 ». Lu : il est tous
  régimes et son dénominateur est l'emploi intérieur de l'INSEE. Il ne ventile
  pas, mais il donne une série de contrôle, et l'open data DREES n'est pas vide
  — il est au mauvais niveau.

  Ce qui reste à faire est court et il est écrit au point 3 : moissonner
  l'archive CCSS pour l'avant-2010 des masses, et lire le bloc « structure de
  financement » du classeur COR, où sont les subventions d'équilibre de l'État
  régime par régime, que le script laisse passer faute d'en-tête d'années.

- **Septembre 2026, action 35, volet A, point 3, cinquième passe : les deux
  chantiers faits, et une correction.** Demandé : lire le bloc « structure de
  financement » et moissonner l'archive CCSS.

  Le **bloc de financement** est lu : il échappait au script parce que son
  en-tête ne porte que six années là où les autres en portent soixante et une.
  Il donne ce qui sépare le coût d'une réforme pour l'État de son coût pour les
  caisses — contribution d'équilibre, subvention d'équilibre, et le besoin de
  financement que personne ne couvre, qui passe de 7,1 % à 48,6 % du
  financement de la CNRACL entre 2023 et 2070.

  L'**archive CCSS** est recensée en entier, et **elle me contredit**. La passe
  précédente avait écrit que la croyance du dépôt — rapports de 2007 à 2012
  illisibles — était « fausse du lecteur, et vraie seulement de son parseur ».
  Le compte de mots dit l'inverse : 2007, 2008 et 2011 rendent ZÉRO mot, 2009
  en rend 76, 2012 en rend 3 887. La fenêtre est bien fermée ; le dépôt se
  trompait sur ses BORDS — 2004, 2005, 2006 et 2010 sont lisibles — pas sur son
  centre. Quarante-six millésimes sur quarante-sept étaient lisibles, et le
  quarante-septième l'est devenu : 1995 tombait sur un opérande malformé que le
  lecteur PDF ne savait pas sauter. **Conclusion à retenir : un compte de mots
  aurait tranché en une minute ce que trois lignes lues à l'œil ont fait
  affirmer de travers.**

  `scripts/fetch/ccss_regimes.py` moissonne la mise en page moderne : **5 662
  valeurs, 22 caisses, 2011-2025**, avec cotisants vieillesse, bénéficiaires
  ventilés droit direct et dérivé, produits nets, charges nettes et
  prestations. C'est la seule source qui donne les effectifs ET les masses d'un
  régime dans le même tableau. Deux pièges y ont été traités et sont écrits au
  point 3 : le chapitre des régimes n'a pas de numéro fixe d'un millésime à
  l'autre, et le même régime change de graphie — cinquante et un libellés pour
  une vingtaine de caisses, ramenés par une table de motifs.

- **Septembre 2026, action 35, volet A, point 3, sixième passe : l'avant-2013
  ne se moissonne pas.** Demandé : moissonner aussi l'avant-2013. La réponse
  est non, et elle tient à trois mesures, pas à une impression.

  **Les deux ancres du moissonneur sont absentes partout** : zéro titre
  « Données générales » et zéro entrée de sommaire numérotée dans tous les
  rapports d'avant 2013. **De 1979 à 1998, il n'existe aucun tableau à colonnes
  d'années** — zéro en-tête croissant sur dix-huit millésimes, une seule
  exception en 1987 ; ces rapports présentent des tableaux d'UNE année à
  colonnes de risques, sporadiques, de 0 à 7 lignes de régime selon l'année.
  **De 2000 à 2006 et en 2010, ce sont des scans océrisés dont la géométrie ne
  tient pas** : 142 en-têtes sur 293 dans le désordre en 2001, et la
  reconstitution coupe les milliers — « 2 937,4 » ressort en « 937,4 » et
  « 2 » sur la même ligne. Changer la tolérance de regroupement n'y fait rien,
  essayé à 3,0, 1,5, 0,8 et 0,3.

  Faute de sommaire, il faudrait reconnaître le régime à son nom dans la prose,
  et c'est là que ça devient dangereux plutôt que seulement difficile : les
  motifs de la table canonique, sûrs sur un titre de sommaire, se trompent en
  prose — « Régimes de non-salariés non-agricoles » tombe sur `msa_salaries`.
  On produirait des chiffres faux sans le dire. **On s'arrête donc, et on écrit
  pourquoi.**

  **Deux acquis restent.** `rapports_tous()` indexe l'archive sans le plancher
  de 2013, qui était juste pour les séries certifiées par
  `ccss_transferts_retraite` et faux pour explorer. Et surtout **la
  réconciliation entre rapports** : chaque rapport portant quatre ou cinq
  exercices, une année est lue plusieurs fois, et on ne garde une valeur que si
  toutes les lectures s'accordent à 1 % près — sinon on ne tranche pas, on
  écarte et on verse aux `conflits`.

  C'était la défense qu'il aurait fallu pour l'ère ancienne ; elle vaut déjà
  pour la moderne, et son résultat la justifie à lui seul : **412 lectures sur
  5 662 ne s'accordent pas**, soit 7,3 %, et la moisson passe de 5 662 à 5 250
  valeurs contrôlées. Les conflits mêlent des révisions légitimes — 1,6 %
  d'écart sur les cotisants de la MSA salariés en 2014 — et des lectures
  franchement fausses, 78 874 contre 571 193 pour la même case. Sans
  confrontation, les secondes seraient passées pour des données.

- **Septembre 2026, action 35, volet A, point 3, septième passe : les 412
  conflits examinés.** Demandé : relancer la moisson avec le garde-fou et
  vérifier les conflits. Je n'en avais regardé que cinq, et j'en avais conclu
  un peu vite qu'ils mêlaient révisions de la DSS et lectures fausses. Les
  examiner tous dit autre chose : **ils dénonçaient surtout des bogues de mon
  propre lecteur**. Quatre corrections en sortent, et la moisson passe de 5 250
  valeurs et 412 conflits à **6 807 valeurs et 195 conflits, dont plus aucune
  contradiction interne** — zéro cas où un rapport se contredit lui-même,
  contre dix-sept au départ.

  Les quatre, dans l'ordre où ils sont apparus : une fiche porte PLUSIEURS
  « Données générales » que le titre distingue et que je fondais ; le titre
  brut ne peut pas servir de clé entre rapports, la mise en page l'écrivant
  tantôt avec ses espaces tantôt sans, si bien que ma première correction a
  ouvert une autre fuite — la confrontation tombant de 30 % à 19 % ; « retraite
  complémentaire obligatoire des NON-SALARIÉS AGRICOLES » porte
  `salariesagricoles` en sous-chaîne et tombait sur la MSA salariés ; et
  l'Agirc et l'Arrco, fusionnées seulement au 1er janvier 2019, étaient fondues
  sous un seul code, ce qui mélangeait leurs séries d'avant-fusion.

  **Une nuance qui manquait, et qui corrige la passe précédente.** Le garde-fou
  ne confronte que ce qui est lu deux fois : 1 353 valeurs sur 6 807, soit
  20 %. Les 80 % restantes ne sont pas « contrôlées », elles sont seulement non
  contredites. J'avais écrit « valeurs contrôlées » pour l'ensemble ; c'était
  trop fort, et c'est corrigé au point 3.

  **Le contrôle par source tierce, lui, est excellent** : CNIEG 2023 à 135 775
  et SNCF 2023 à 112 621, soit exactement ce que dit la fiche 4.1 ; CNRACL 2021
  à 2 189 791, soit exactement ce que disent la fiche 4.1 ET le recueil de la
  caisse. Trois coïncidences à l'unité sur quatre contrôles.

  **La leçon.** Un garde-fou qui rejette 7 % des lectures ne dit pas que la
  source est mauvaise : il dit d'aller lire ce qu'il rejette. Les quatre bogues
  étaient dans mon code, pas dans les rapports.

- **Septembre 2026, action 35, volet A, point 3, huitième passe : les 195
  conflits examinés.** Demandé : regarder les conflits restants. Ils ont
  dénoncé un bogue net et un problème que je n'ai pas su résoudre.

  **Le bogue : une note de bas de page lue comme un en-tête d'années.** La
  SNCF concentrait 53 des 195 conflits, dont 40 sur la seule année 2017. La
  note « le taux de cotisation T2 a été fixé à 11,81 % entre le 1er janvier
  2017 et le 30 avril 2017 » porte trois fois la même année, et mon détecteur,
  qui acceptait des années non décroissantes, la lisait comme des colonnes.
  Toute la fiche de la SNCF était datée de 2017. Les années doivent être
  strictement croissantes. Corrigé, la SNCF donne une série continue de
  156 963 cotisants en 2012 à 105 610 en 2025, dont trois points tombent à
  l'unité sur la fiche 4.1.

  **Le problème non résolu : l'attribution des tableaux aux fiches.** Le numéro
  de fiche est répété en tête de page, pas au-dessus de chaque tableau, et le
  chercher en remontant donne parfois la fiche précédente. J'ai essayé deux
  remèdes et **les deux ont fait pire** — préférer le titre du tableau a donné
  le SRE à la CNRACL, délimiter les fiches par intervalles a tout fait tomber
  dans un seul régime. Les deux sont annulés.

  **Faute de réparer, surveiller.** Deux filets s'ajoutent. Un filet grossier
  sur l'ordre de grandeur — une valeur à plus d'un facteur trois de la médiane
  de sa série — qui écarte 237 valeurs et ne voit pas les confusions entre
  régimes de taille voisine. Et un filet EXACT : une caisse n'a qu'un effectif
  de cotisants par année, donc deux tableaux qui remplissent la même case se
  dénoncent eux-mêmes ; 543 valeurs écartées, dont les 135 775 et 112 621
  portés tous deux à la CNIEG en 2023. On n'arbitre pas, les deux partent.

  **Le bilan est volontairement plus petit** : de 6 807 valeurs sans filet à
  5 289 passées par trois contrôles. Les contaminations connues sont devenues
  des trous plutôt que des erreurs silencieuses — la CNIEG n'a plus de 2023, ce
  qui vaut mieux que la valeur de la SNCF. Tous les contrôles par source tierce
  passent à l'unité : SNCF 2021, 2023, 2024 ; CNRACL 2013 et 2021 ; MSA
  exploitants 2021.

- **Septembre 2026, action 35, volet A, point 3, neuvième passe : l'attribution
  des tableaux aux fiches est réparée.** Trois tentatives avaient échoué faute
  d'avoir regardé la source. La quatrième a commencé par là.

  **La cause : le rapport de 2025 sort ses pages dans l'ordre INVERSE des
  fiches** — les marqueurs passent 4.15, 4.14, 4.13 à mesure que les lignes
  avancent. Chercher le marqueur « le plus proche au-dessus » d'un tableau y
  donne donc systématiquement la fiche voisine, d'où le tableau « de la branche
  vieillesse de la CNRACL » porté au crédit de la SNCF, et la CNRACL héritant du
  SRE.

  Le numéro de fiche est une TÊTE DE PAGE : il vaut pour sa page et pour elle
  seule. Le bon niveau n'était donc ni le marqueur le plus proche, ni le titre
  du tableau, ni un intervalle — c'était la page, qu'il a fallu exposer dans
  `lecture_pdf` par `lignes_par_page`. Sur les treize pages du rapport de 2025
  portant un « Données générales », chacune porte exactement un marqueur, et
  c'est le bon. `lecture_pdf` est scindé en `_fragments` et `_assembler` pour
  cela, refactor contrôlé neutre : mêmes 15 485 lignes, en 505 pages.

  **Un garde-fou est tombé avec le bogue, et c'est le signe que c'était le
  bon.** Le détecteur de « case remplie deux fois » écartait 318 valeurs ; une
  fois l'attribution réparée, ses 133 cas venaient TOUS de tableaux différents
  — la table vieillesse d'une fiche contre sa table « toutes branches », qui ne
  mesurent pas la même chose. Il ne rejette plus que la contradiction vraie, au
  sein d'un même tableau, et il n'en trouve plus aucune.

  **État : 5 419 valeurs, 25 régimes, 2011-2025, zéro case remplie deux fois.**
  Les contrôles par source tierce passent neuf fois sur dix à l'unité, et deux
  séries qui étaient fausses sont justes : la CNIEG de 2023 vaut 135 775 et non
  112 621 qui était la SNCF ; la CNRACL de 2024 vaut 2 151 694 et non 2 008 352
  qui était le SRE.

  **La leçon est la même que deux passes plus tôt** : les trois tentatives
  ratées ont consisté à corriger une heuristique par une autre sans ouvrir le
  document. Quinze lignes de diagnostic — afficher, pour chaque tableau, le
  marqueur trouvé et le titre — ont donné la réponse immédiatement.

- **Septembre 2026, action 35, volet A, point 3, dixième passe : le trou de la
  SNCF en 2021.** Demandé : regarder pourquoi. Il n'était dans aucun des trois
  garde-fous — la valeur n'avait jamais été lue. Deux causes distinctes.

  **Le tableau de la fiche SNCF est une IMAGE en 2022 et en 2023** : leurs
  pages ne portent que le titre, l'unité, la source et les notes, pas un
  chiffre. Ce n'est pas réparable, et c'est à savoir — toutes les fiches ne
  sont pas en texte tous les ans.

  **Et le numéro de fiche était collé en FIN de ligne** : le rapport de 2022
  écrit « correspond à la moyenne de ces deux taux . 5.6 », là où mon motif
  l'ancrait en début. Six pages à tableau n'avaient aucun marqueur en tête sur
  l'ensemble des millésimes ; cinq l'avaient en queue. Le motif de secours les
  récupère, et n'est essayé que si rien n'a été trouvé en tête.

  Cela comble le trou : la SNCF de 2021 vaut 123 019 cotisants, exactement ce
  qu'écrit la fiche 4.1, et la série est continue de 2012 à 2025.

  **Une remarque pour la suite** : « 123019 » figure aussi dans le TABLEAU DE
  SYNTHÈSE des rapports de 2022 et 2023 — la fiche 4.1 —, que ce moissonneur ne
  lit pas puisqu'il ne cible que les « Données générales » des fiches. Les deux
  familles se complètent : quand la fiche d'un régime est en image, la synthèse
  peut encore porter ses effectifs. La lire aussi est le prochain gain facile.

  **État final : 5 493 valeurs, 25 régimes, 2011-2025, zéro case remplie deux
  fois, neuf contrôles indépendants sur neuf à l'unité.**

- **Septembre 2026, action 35, volet A : la ventilation État/caisses par
  régime.** Première fois de cette série de passes que quelque chose entre dans
  le MODÈLE et non dans un relevé.

  `equilibre.py` savait que l'État verse une contribution d'équilibre au
  système ; il ne savait pas à qui. La page « Coût » ne pouvait donc pas poser
  la question qui décide du coût réel d'une réforme : un scénario à 18 % rend-il
  de l'argent à l'État ou en demande-t-il aux caisses ? Deux familles de régimes
  se lisent maintenant d'un coup d'œil — ceux que l'État porte, et de plus en
  plus (SNCF de 61 % à 95 % entre 2023 et 2070, fonction publique d'État à
  86 %, mines à 81 %), et ceux dont le déficit n'est couvert par personne
  (CNBF 58 % en 2070, CNRACL 49 %, Ircantec 36 %, CNAV 19 %).

  Livré : `data/reference/regimes/structure_financement.csv`, 930 valeurs, 22
  régimes, huit postes, certifié contre le classeur du COR ; la source déclarée
  sous `cor_regimes` ; `donnees/financement_regimes.py`, exposé par
  `Simulateur.financement_regimes`.

  Quatre limites sont écrites dans l'en-tête du fichier ET dans le lecteur,
  parce que c'est le genre de série qu'on réutilise sans relire sa provenance :
  le millésime est juin 2024 quand le dépôt tourne sur le COR 2026 ; les années
  sont éparses et le lecteur REFUSE d'interpoler ; les parts ne somment pas
  toujours à un et ne sont pas normalisées ; la fonction publique d'État est
  d'un seul tenant. Et un choix : les impôts et taxes affectés ne comptent pas
  dans `part_etat`, un impôt affecté n'étant ni ce que l'État verse comme
  employeur ni ce qu'il comble comme garant — `cout.py` tient déjà cette
  distinction pour l'agrégat. *[Corrigé le soir même : cette entrée écrivait
  « parce qu'ils compensent des exonérations », ce qui est la phrase que le
  dépôt avait démolie le matin.]*

  **Ce qui n'est pas fait, et c'est délibéré** : la page « Coût » n'affiche rien
  de tout cela. Le pas suivant demande une décision de MODÈLE et non de
  données — que devient la contribution d'équilibre de l'État quand le taux
  devient 18 % ? Le programme ne le dit pas, et le dépôt ne tranchera pas à sa
  place.

- **Septembre 2026, l'âge de référence passe à 64 ans.** À la demande. Nouveau
  mode `fixe_apres_bascule`, qui devient le DÉFAUT des deux moteurs : 64 ans —
  l'âge légal d'ouverture des droits — à partir de l'année de bascule, incluse,
  et le cliquet avant elle. La borne inclut la bascule exprès : c'est l'année où
  les droits acquis sont convertis, et une borne stricte aurait laissé le
  changement sans effet sur le seul calcul où l'âge de référence pèse sur une
  pension. Le cliquet reste en variante, et les trois tests qui le vérifient le
  nomment désormais au lieu de le supposer.

  *Ce que ça déplace, et ce qu'il faut savoir avant de s'en servir* : RIEN sur
  les quatre systèmes que le site compare — le scénario 1 ne lit jamais l'âge de
  référence, les rétroactifs ne figent aucun droit —, et 0 cellule sur 91 bouge
  dans leur grille de cas types. L'effet est tout entier sur les deux scénarios
  PROSPECTIFS, que l'action 31 a retirés de l'affichage : ils gagnent chacun un
  demi-point de PIB de dépense, le 3 recule son équilibre de 2044 à 2049, et le
  5 repasse SOUS le système actuel en solde moyen (−1,48 % contre −1,14 %). Le
  sursaut du premier temps, qui durait cinq ans et plafonnait à 1 %, dure
  jusqu'à huit ans et monte à 2,7 % : la conversion à un âge plus bas va tout
  entière aux générations de transition.

  *Et elle vide l'action 24 de sa moitié utile* : avec une référence à 64 ans,
  les deux conventions de conversion des droits acquis coïncident pour un départ
  à 64 ans. L'action ne mord plus que sur les départs avant 64.

  **Fichiers.** `ModeAgeReference.FIXE_APRES_BASCULE` et `age_reference_fixe`
  dans `config.py` et `config.js` ; `moteur/age_reference.py` et
  `moteur/js/age-reference.js` ; `AGES_REFERENCE` et le défaut de `Saisie` dans
  `web/pages.py` et `moteur/js/pages.js` ; la ligne du tableau de
  `simulateur.py`, qui ne nomme plus un mode sur quatre ; `docs/methodologie.md`
  §4 ; deux lignes du cahier des charges du `README.md` et son bloc d'exemple ;
  `tests/test_moteur.py`, `tests/test_simulateur.py`, `tests/test_cout.py` ; les
  témoins.

- **Septembre 2026, le profil salarial cesse de réécrire le passé.** Trouvé en
  vérifiant les chiffres de l'action 24 : sous le réglage actuel, le pot de
  droits acquis valait 419 792 € pour un départ à 60 ans et 397 677 € pour un
  départ à 67, sur ce qui devait être le même passé. La cause n'était pas la
  conversion mais la CONSTRUCTION DE LA CARRIÈRE. La déformation salariale
  (60 % à 130 % du niveau saisi en profil ascendant) se mesurait sur
  l'avancement dans la carrière de l'ASSURÉ : une même année civile s'y
  trouvait moins avancée dans une carrière plus longue, donc moins payée.
  Décider de travailler jusqu'à 67 ans rabaissait donc ses propres salaires de
  1996 à 2025.

  *Mesuré avant correction* : −5,2 % sur les salaires d'avant 2026 en profil
  ascendant entre 60 et 67 ans, −8,4 % en fortement ascendant. Douze des treize
  cas types portent un profil déformé, seul le SMIC carrière complète est plat.
  Pas d'inversion de signe — testé de 58 à 70 ans, la pension monte toujours —
  mais un biais : le site annonçait +83,3 % de gain à travailler de 60 à 67 ans
  dans le système actuel, contre +79,3 % à passé inchangé. **Quatre points, et
  ils avantageaient le système actuel**, dont le salaire de référence ne retient
  que les meilleures années. Les scénarios notionnels, eux, ne bougeaient que de
  trois dixièmes de point.

  *L'étalon retenu* : la durée d'assurance requise pour le taux plein, PAR
  GÉNÉRATION — 157 trimestres pour 1940, 172 pour 1975 —, que l'assuré ne
  choisit pas. Au-delà d'une carrière complète, l'avancement plafonne. Un
  ancrage unique à 64 ans avait été essayé d'abord et écarté : anachronique
  pour les générations qui liquidaient à 60 ou 65, il coupait le passé de 1940
  de 6,4 % contre 2,1 % pour 2000, ce qui redressait la trajectoire de la page
  Coût de plus d'un demi-point de PIB — un artefact, pas un résultat.

  *Ce que la correction a déplacé* : 58 cellules sur 91. Les carrières
  complètes ne bougent pas (−0,4 % à +0,4 %) ; tout l'effet porte sur les
  départs précoces, dont la carrière est plus courte qu'une carrière complète et
  qui n'atteignent donc plus le haut de la fourchette salariale — militaire
  −16,4 %, agent de conduite SNCF −11,6 %, catégorie active −8,6 %, IEG −7,4 %.
  Les ÉCARTS entre systèmes, qui sont ce que le site affiche, ne bougent pas :
  médiane +0,0 point sur les trois comparaisons. Page Coût : 19,39 % à 19,49 %
  du PIB en 2070, soldes moyens déplacés de deux à trois centièmes de point.

  *Au passage*, la lecture des tables par génération passe par un chargeur
  mémorisé commun (`charger_table_par_generation`), là où `carriere.py` et
  `scenarios/actuel.py` auraient analysé le même fichier chacun de son côté.

  **Fichiers.** `_duree_carriere_complete` dans `carriere.py` et
  `dureeCarriereComplete` dans `moteur/js/carriere.js` ;
  `charger_table_par_generation` et `valeur_par_generation` dans
  `donnees/chargement.py`, dont `TableParGeneration` de `scenarios/actuel.py`
  hérite désormais la mémorisation ; l'aide du profil dans `web/pages.py` et son
  portage, qui annonce le haut de la fourchette « après une carrière complète »
  et non « au dernier emploi » ; `docs/methodologie.md` ; le bloc d'exemple du
  `README.md` ; `tests/test_moteur.py` ; les témoins.

- **19 septembre 2026, action 42.** Ouverte : une passe visuelle exhaustive du
  site, neuf pages à trois largeurs (360, 768 et 1280 points), états
  interactifs compris — résultats, dépliants ouverts, bulle du glossaire,
  erreur de saisie, focus clavier, lecture au survol, impression. Vingt
  constats, rangés par gravité sous l'action, chacun avec sa cause dans le
  code et la correction proposée. Rien n'a été corrigé dans cette session :
  la liste est le livrable, la correction est l'action.
- **Septembre 2026, le profil de carrière est lu chez l'INSEE.** Trouvé en
  remontant la piste de l'action 24 : le profil salarial valait trois nombres
  écrits à la main — 60 % du niveau saisi au premier emploi, 130 % au dernier,
  190 % pour un cadre —, sans source, dans un dépôt dont la règle est qu'une
  valeur non lue à la source n'entre pas. Rien dans `sources.yaml`, rien dans
  `limites.md`, et l'historique ne remonte pas avant la réécriture du fichier.
  Il pesait pourtant SEPT POINTS sur l'écart que le site affiche : à salaires
  cumulés identiques, passer du profil plat au profil ascendant faisait passer
  la proposition de −31,7 % à −39,2 % du système actuel.

  *La source.* `DS_DERA_PRIVE_SERIES_LONGUES` et `DS_DERA_PRIVE_ANNUEL`, par
  l'API Melodi de l'INSEE, sans clé. Aucune ne suffit seule et c'est le cœur de
  la conception : la première porte quatre tranches d'âge de 1962 à 2024 mais
  est AGRÉGÉE — elle mélange l'effet d'âge et un effet de composition, les
  jeunes étant plus souvent dans les catégories mal payées, si bien que son
  écart entre les bords vaut 0,46 quand celui des ouvriers vaut 0,24 ; la
  seconde croise l'âge et la catégorie, et est donc la seule à décrire une
  CARRIÈRE, mais ne porte que 2024. La forme vient donc de la seconde,
  l'évolution dans le temps de la première.

  *Ce que la mesure a dit.* Le profil était trop pentu d'un tiers — ×1,69 de 26
  à 55 ans contre ×1,30 observé pour un employé, ×2,42 contre ×1,86 pour un
  cadre — et il était le MÊME pour toutes les générations, quand l'observation
  diverge : ×1,25 pour celle de 1940, ×1,32 pour 1950, ×1,38 pour 1960. Le
  modèle retrouve désormais ces pentes à quelques centièmes près.

  *Ce que ça déplace, et c'est beaucoup.* Le système actuel perd 11 % sur la
  carrière témoin du README, et l'écart du scénario 4 y passe de +9,5 % à
  +39,9 %. La raison est mécanique : un profil moins pentu abaisse les
  dernières années, donc le salaire de référence du système actuel, qui ne
  retient que les vingt-cinq meilleures, et relève les premières, que le compte
  notionnel porte au compte comme les autres. **Le profil inventé flattait le
  système actuel**, et c'est ce que sept points d'écart voulaient dire. Sur la
  grille des cas types, l'écart médian de la proposition passe à −41,4 % ; la
  trajectoire 2070 de la page Coût descend de 19,49 % à 19,24 % du PIB.

  *Ce qui n'est pas comblable*, et qui est écrit au §1 de `limites.md` : rien
  avant 1962, les deux bords d'âge seulement depuis 1996, l'écart entre
  catégories observé sur la seule année 2024 — et la série longue du public ne
  croisant pas l'âge et le statut, les fonctionnaires et les militaires portent
  le profil du privé.

  *Au passage*, l'étalon par génération posé le matin même devient inutile : un
  profil lu à (âge, année) ne peut pas dépendre d'une décision future, et
  l'effet de génération vient de l'observation au lieu d'être supposé.

  **Fichiers.** `scripts/fetch/insee_profil_salaire_age.py` ;
  `data/reference/macro/profil_salaire_age.csv` et
  `profil_salaire_categorie.csv`, avec leurs deux règles de certification dans
  `scripts/verifier_donnees.py` et leurs deux entrées dans `data/sources.yaml` ;
  `charger_table_csv` dans `donnees/chargement.py` ; `profil_salaire` et
  `bornes_deformation` dans `carriere.py` et leur portage ;
  `scripts/construire_donnees.py` ; `docs/methodologie.md`, `docs/limites.md`
  §1, le bloc d'exemple du `README.md` ; `tests/test_moteur.py`,
  `tests/test_cout.py`, `tests/test_donnees.py`, `tests/test_web.py` ; les
  témoins.

- **Septembre 2026, le profil se choisit sur l'affiliation, et le public a le
  sien.** Suite immédiate de la note précédente. Le profil lu chez l'INSEE
  était celui du PRIVÉ, servi à tout le monde : le jeu annuel détaillé de la
  fonction publique croise pourtant l'âge et le statut — le seul des trois à le
  faire —, et les pentes y sont très éloignées. De 26 à 55 ans : **×1,11 pour
  un catégorie C, ×1,22 pour un catégorie B, ×1,56 pour un catégorie A**, contre
  ×1,30 servi à tous. Le profil du privé était donc trop pentu de 17 % pour un
  catégorie C — le cas type « catégorie active », aide-soignant ou agent
  technique territorial — et trop plat de 20 % pour un catégorie A.

  *Le piège du codage, évité de justesse.* Le code `PM` de ce jeu n'est pas
  « personnels militaires » mais **personnels MÉDICAUX** : il n'existe que dans
  le versant hospitalier et vaut 6 765 € nets par mois quand l'ensemble du
  public en vaut 2 682. Les militaires ne sont dans aucun de ces jeux, et les
  cas types militaires prennent le profil de l'État, faute de mieux.

  *Le profil se choisit désormais sur l'AFFILIATION* — `PROFIL_PAR_AFFILIATION`
  —, et non sur un réglage saisi : on ne demande pas sa progression de carrière
  à quelqu'un qui a déjà dit qu'il était fonctionnaire de l'État. Les
  affiliations publiques prennent le profil de leur VERSANT (×1,60 pour l'État,
  ×1,27 pour la territoriale, ×1,32 pour l'hospitalière) parce qu'aucune ne
  porte le A, le B ou le C, et que le profil du versant pondère déjà les
  catégories par leurs effectifs réels : deviner la catégorie de chaque
  affiliation aurait été réinventer ce qu'on venait de retirer. Le profil se lit
  MÉTIER PAR MÉTIER, l'affiliation pouvant changer en cours de carrière.

  *Ce que ça déplace* : l'écart médian de la proposition sur la grille passe de
  −41,4 % à −41,6 %, celui du compte notionnel deux parts de −33,5 % à −34,5 %,
  et la trajectoire 2070 de 19,24 % à 19,28 % du PIB. Peu, donc — les quatre cas
  types publics pèsent peu dans la pondération par effectifs —, mais ce sont
  quatre carrières sur treize qui cessent de porter un profil qui n'est pas le
  leur.

  *Trois tests l'ont senti passer*, et c'est le bon signe : ils comparaient deux
  statuts « à rémunération égale » pour isoler le périmètre de cotisation ou la
  grille des forfaits marins, et le défaut leur donnait désormais deux profils
  différents. Ils nomment leur profil, et disent pourquoi.

  **Fichiers.** `DS_DERA_PUBLIC_ANNUEL` ajouté à
  `scripts/fetch/insee_profil_salaire_age.py` ;
  `data/reference/macro/profil_salaire_statut_public.csv` et sa règle de
  certification ; `data/sources.yaml` ; `PROFIL_PAR_AFFILIATION`,
  `PROFIL_AUTOMATIQUE` et le profil par métier dans `carriere.py` et son
  portage ; `castypes.py` et `castypes.js`, où deux fiches portent enfin la
  catégorie que leur commentaire annonçait ; `PROFILS` et le défaut de `Saisie`
  dans `web/pages.py` et son portage ; `docs/methodologie.md`,
  `docs/limites.md` §1 ; `tests/test_simulateur.py`, `tests/test_donnees.py` ;
  les témoins.

- **19 septembre 2026, action 42, suite et fin.** Les vingt constats sont
  corrigés, en deux temps, dans les deux portages, avec les témoins
  régénérés et cinq tests mis au niveau du gabarit ; le détail est sous
  l'action, qui passe à `fait`. Deux choses apprises en chemin, notées là
  aussi : une `<caption>` ne peut pas être collante, et Chromium rend tout
  `<button>` en bloc en ligne. Une passe suivante repartira du script décrit
  sous « Comment refaire la passe ».

- **19 septembre 2026, action 42, seconde passe.** Refaite de zéro sur
  `main` après les vingt corrections : rien ne revient, sept constats de
  moins de gravité trouvés et corrigés le jour même (marges des graphiques
  sur téléphone, bande de lecture qui doublait la légende, bascules coupées,
  colonnes de phrases, largeur des grands tableaux). Le détail est sous
  l'action.
- **Septembre 2026, les régimes spéciaux, et le relevé des impasses.** Ils
  portaient le profil salarial des employés du privé, faute de mieux. Sept
  pistes ont été parcourues avant d'en trouver une, et elles sont ici pour
  qu'on ne les reparcoure pas :

  - **Catalogue Melodi de l'INSEE, 147 jeux** — quatre jeux de salaires,
    aucun par régime ni par secteur assez fin.
  - **INSEE BDM, 244 flux** — aucune dimension d'âge sur les salaires.
  - **Secteur × âge × catégorie de l'INSEE (2024)** — existe, mais `B_D_E`,
    qui porte les IEG et les mines, n'a rien au niveau agrégé : il n'est
    ventilé que par taille d'établissement, et les grandes cellules sont vides.
  - **Fiches de régimes du dépôt** — règles de pension seulement, aucune
    structure salariale.
  - **Compléments par régime du COR** — effectifs, masses, ressources, âge
    moyen de départ : pas de salaire par âge.
  - **CNIEG** — le site répond, mais ne publie qu'une page de pilotage, sans
    annuaire statistique.
  - **RATP open data** — 26 jeux, tous d'exploitation ferroviaire.
  - **Injoignables depuis ce conteneur** : `data.gouv.fr`, `opendata.sncf.com`,
    le site de la CPRPSNCF, `epsilon.insee.fr`. À reprendre ailleurs. La vraie
    source, si elle existe, serait les BILANS SOCIAUX de la SNCF, de la RATP et
    d'EDF, que la loi impose de publier et qui portent la masse salariale par
    tranche d'âge.

  *Ce qui a été trouvé* : l'enquête européenne sur la structure des salaires
  (`earn_ses18_20`, `earn_ses22_20`), qui ventile par âge et par SECTION
  d'activité. Deux sections tombent sur un périmètre de régime plutôt qu'à
  côté — `D`, électricité et gaz, est le champ du statut des IEG ; `H`,
  transports, est là où sont la SNCF et la RATP. Deux vagues, ce qui permet de
  trier : le facteur de l'électricité-gaz vaut 1,41 puis 1,35, celui des
  transports 0,928 puis 0,931, mais celui des mines passe de 0,93 à 1,19 et
  celui des spectacles de 0,83 à 1,08 — ces deux-là ne sont que du bruit, et
  leurs régimes gardent le profil du privé sans correction.

  *L'hypothèse, et elle est assumée.* La source est AGRÉGÉE par secteur : elle
  mélange l'effet d'âge et un effet de composition, et aucune source ne croise
  l'âge, le secteur et la profession — vérifié chez Eurostat comme chez
  l'INSEE. Le modèle n'en prend donc qu'un rapport de pentes, secteur sur
  ensemble, appliqué à la forme intra-catégorie, ce qui suppose ce rapport
  identique des deux côtés. **Rien ne le démontre.** C'est l'hypothèse la plus
  forte du profil salarial, elle est écrite dans le fichier certifié, au
  manifeste des sources, dans `limites.md` §1 et dans `methodologie.md`, et un
  test tient ses deux bornes : elle ne touche que les affiliations nommées, et
  pas celles dont le facteur ne tient pas.

  *Ce que ça déplace* : rien de visible — les écarts médians et la trajectoire
  2070 ne bougent pas au centième près, les régimes spéciaux pesant peu dans la
  pondération par effectifs. Ce qui change est qu'un agent des IEG progresse
  désormais 38 % plus vite qu'un employé du privé, et un agent SNCF 7 % moins
  vite, au lieu de progresser exactement comme lui.

  **Fichiers.** `scripts/fetch/eurostat_profil_salaire_secteur.py` ;
  `data/reference/macro/profil_salaire_secteur.csv` et sa règle de
  certification ; `data/sources.yaml` ; `PROFIL_SECTEUR_PAR_AFFILIATION` et
  `_facteur_secteur` dans `carriere.py` et leur portage ;
  `scripts/construire_donnees.py` ; `docs/methodologie.md`, `docs/limites.md`
  §1 ; `tests/test_moteur.py`, `tests/test_donnees.py` ; les témoins.

### 37. Chiffrer les trente-neuf avantages non contributifs, et les montrer — `en cours`

**La demande.** « J'aimerais qu'on fasse la liste des avantages en retraite
actuels qui ne sont pas contributifs dans le scénario 1. Le but serait de
calculer le coût de chacun et de voir l'évolution de son coût au cours du temps.
Le but est d'être exhaustif pour ne passer à côté de rien : cela explique en
partie pourquoi les retraites actuelles sont gonflées par rapport à ce que les
gens ont vraiment cotisé. »

**Ce qui est fait.** La liste existe, et elle est tenue par un test.
`data/reference/legislation/avantages_non_contributifs.yaml` porte trente-neuf
dispositifs — huit `chiffré`, onze `intégré`, trois `déclaré`, dix-sept
`absent` —, chacun avec sa base légale lue dans l'index LEGI, les régimes qui le
servent, et le moyen d'en mesurer le coût. `tests/test_avantages.py` (neuf
tests) exige que tout code employé par l'une des trois listes préexistantes du
dépôt — les champs de `Neutralisations`, les `avantages_non_contributifs` des
fiches, les lignes de la cascade `AvantageApplique` — ait sa ligne, sous son code
ou sous un alias ; que toute ligne de cascade pointe un avantage chiffré et
réciproquement ; qu'un avantage non chiffré dise POURQUOI ; et que tout renvoi à
`veille.yaml` ou au manifeste des sources existe. `scripts/cout_avantages.py`
porte la décomposition de l'individu à la masse par la méthode de `cout.py`, et
`docs/avantages_non_contributifs.md` commente le tout.

**Ce que ça a déplacé, et ce n'est pas ce qui était prévu.** Le premier chiffrage
donnait **5,3 milliards d'avantages gratuits en 2024, soit 1,2 % de la
dépense**, là où le COR chiffre les droits de solidarité à « de l'ordre d'un
cinquième des retraites tous régimes ». Il en vaut aujourd'hui **93,9, soit
22,0 %** : 12,6 par les recalculs du volet B, puis la réversion (volet E) et
huit postes publiés (volet F), qui font à eux seuls 87 % du total. Le chemin
importe plus que le chiffre d'arrivée, parce que les deux causes de l'écart
initial ne se corrigeaient pas de la même façon, et que la seconde était
inconnue :

- *Trente et un dispositifs sur trente-neuf n'étaient pas chiffrés*, et
  l'inventaire disait lesquels. La réversion pesait à elle seule plus que tout
  ce qui était mesuré, et le modèle ne peut pas la voir : il décrit une
  carrière, pas un ménage. Elle est désormais LUE (volet E), comme sept autres
  lignes (volet F) ; vingt-quatre restent sans chiffre, chacune avec sa raison
  écrite.
- *La grille de cas types n'a pas d'enfants.* Un seul des treize en a —
  `carriere_interrompue`, deux enfants —, si bien que la majoration de pension
  pour trois enfants et plus vaut **zéro toutes les années de la série**, quand
  la CNAF en rembourse 5,9 milliards en 2025 ; la surcote parentale vaut zéro
  pour la même raison ; l'AVPF et la MDA ne sont portées que par ce seul cas
  type. C'est exactement l'erreur déjà rencontrée sur la garantie vieillesse à
  l'action 1 — les 93 milliards tirés des cas types, corrigés à 18,4 par la
  distribution DREES. La grille est un instrument de RAPPORT, où les erreurs de
  niveau s'annulent au dénominateur ; le coût d'un avantage est un compte de
  POPULATION. **La correction a été faite par l'autre bout** (volet F) : lire
  le poste que la DREES publie, plutôt que reconstruire la population qui
  permettrait de le calculer. Reconstruire reste souhaitable, mais pour
  vérifier et projeter, non plus pour chiffrer.

**Ce qui reste, dans l'ordre du gain.**

1. *Une structure de population par nombre d'enfants*, par sexe et par
   génération. Sans elle, toute la famille des droits familiaux vaut zéro ou
   presque — et c'est la plus documentée du système français. Source probable :
   l'échantillon interrégimes de retraités de la DREES (`drees_eir_distribution`
   est déjà au manifeste pour la distribution des pensions).
2. *La réversion, lue et non calculée* — **fait, volet E.** 38,3 Md€ en 2024,
   lus dans l'enquête annuelle de la DREES auprès des caisses. Restent hors de
   l'inventaire chiffré l'allocation veuvage et les pensions d'orphelin.
3. *Les onze lignes « intégré », chiffrées par retrait* — **fait, volets B et
   D.** Huit le sont ; les trois autres ne sont pas des dispositifs et se lisent
   ailleurs. Ce qui reste n'est plus une mesure mais une population : quatre des
   huit ne pèsent rien sur la fenêtre publiée, faute de chômeurs, d'appelés et
   de parents dans la grille. C'est le point 1 de cette liste.
4. *Les trois contrôles externes du dépôt, opposés au résultat* :
   `cnaf_avpf` et `cnaf_majorations` pour les droits familiaux,
   `fsv_cotisations` pour le chômage, `unedic_agirc_arrco` pour les points
   gratuits de complémentaire (`macro/transferts_retraite.csv`). Aucun ne couvre
   le même champ que le modèle ; tous doivent varier dans le même sens.
5. *Porter la décomposition dans `cout.py` et sur la page Coût*. L'objection qui
   la retenait — elle mesurait 1,2 % de ce qu'elle prétend mesurer — est levée :
   elle en mesure 22,0 %, et elle a sa page (volets C et F). Reste à décider si
   la page Coût doit la reprendre, ou seulement y renvoyer.

**Une contradiction relevée au passage.** `Neutralisations` porte
`reversion: bool = True` pendant que son propre docstring dit que le scénario 1
ne sert pas la réversion. Neutraliser ce que l'étalon n'a jamais servi ne change
rien, et l'écart annoncé entre les systèmes n'en contient pas un euro. La ligne
reste — elle décrit une intention de réforme —, mais l'inventaire la range sous
`declare` et dit pourquoi.

**Volet B — les périodes assimilées et la catégorie active, chiffrées.** À la
demande. Les deux sont servies par le scénario 1 sans que la cascade les isole :
leur effet passe par un trimestre ou par un âge. Elles sont désormais mesurées
par recalcul, dans `scripts/cout_avantages.py`, à date de liquidation inchangée.

- *Les périodes assimilées valent 6,8 milliards en 2024*, ce qui en fait la plus
  grosse ligne de la décomposition. On refait la pension en donnant aux périodes
  non travaillées le motif `sans_activite`, qui ne valide rien, et l'AVPF est
  retranchée de l'écart — la cascade la porte déjà, et elle serait comptée deux
  fois. Le chiffre agrégé reste un plancher extrême : aucun cas type ne connaît
  le chômage. D'où `--par-carriere`, qui donne le chiffre parlant — **cinq années
  de chômage indemnisé valent 7 154 € de pension annuelle à une carrière au
  salaire moyen, soit 29 % de sa pension**, et entre un sixième et un tiers selon
  le cas type. Sous-produit obtenu par un détour : le chômage indemnisé et le
  chômage non indemnisé valident les mêmes trimestres, seul le premier ouvrant
  des points de complémentaire ; l'écart entre les deux EST la valeur de ces
  points, 612 € par an.

- *La catégorie active vaut 0,6 milliard sur le montant, et 8,8 sur la durée.*
  C'est le résultat de ce volet, et il n'était pas prévu. Mesurée à date de
  départ inchangée contre le statut sédentaire de mêmes régimes, elle ne vaut
  que 868 € par an à un agent classé de la génération 1960 — parce que **la
  décote est plafonnée à vingt trimestres** et que l'agent classé et l'agent
  sédentaire partis le même jour butent tous deux sur le même plafond. Une
  décote plafonnée ne sait pas dire qui part cinq ans trop tôt. Ce que
  l'avantage coûte vraiment, ce sont les annuités servies avant l'âge légal :
  `--duree` les compte à l'âge légal de chaque génération, et trouve **13,7
  milliards en 2024** — 7,5 pour le classement, 2,4 pour les régimes spéciaux,
  3,8 pour la carrière longue. Treize fois l'effet de montant. La composition
  change au cours du temps : rien pour la carrière longue jusqu'aux années 2010,
  puis 5,6 milliards, mécaniquement, à mesure que l'âge légal monte au-dessus de
  l'âge auquel une carrière commencée tôt réunit sa durée.

- *Un refus, qui est un résultat.* La jouissance immédiate de la pension
  militaire n'est PAS chiffrée sur le montant. Sa contrefactuelle naturelle — le
  même agent en fonctionnaire civil, qui relève des mêmes régimes — déplace
  aussi la durée requise, 172 trimestres contre 160, si bien que la
  proratisation change avec le statut et que l'écart ressort négatif. Le script
  pose un garde-fou qui compare les durées requises, refuse la ligne, imprime la
  raison, et la refuse PARTOUT dès qu'elle est faussée quelque part : une ligne
  mesurée pour certaines générations et pas pour d'autres donnerait un agrégat
  biaisé dont le biais serait invisible.

- *Cinq tests de plus* protègent les hypothèses du recalcul, qu'une fiche
  modifiée casserait sans bruit : le statut témoin relève des mêmes régimes que
  le statut classé ; aucun cas type ne porte à la fois des interruptions et un
  classement, faute de quoi l'addition de deux retraits d'âge surestimerait ;
  `sans_activite` ne valide rien ; le recalcul rend un montant positif et
  inférieur à la pension ; la décomposition somme toujours à la pension entière.

**Ce qui reste du volet B.** La réserve sur `--duree` est écrite partout où le
chiffre l'est : ce sont des annuités ANTICIPÉES, non un surcoût NET — partir
tôt, c'est aussi cotiser moins et mourir plus tôt en moyenne. Chiffrer le net
demanderait de projeter la carrière contrefactuelle jusqu'à l'âge légal, donc de
décider ce que l'agent aurait fait de ces années : le dépôt ne tranchera pas à
sa place. C'est exactement l'arbitrage qu'un coefficient de conversion notionnel
rend automatique et que le droit actuel ne rend nulle part.

**Volet C — la page « Avantages » du site.** À la demande : « une page en plus
qui illustre par un graphique tous les avantages non contributifs qui existent
au cours du temps ». Elle est en ligne, sous `#/avantages`, dans le groupe « La
preuve » de la barre.

*Trois graphiques, et ils n'ont pas le même statut* — c'est la contrainte de
construction, et elle décide de l'ordre. Le premier COMPTE : combien de
dispositifs sont en vigueur chaque année, par famille, de 1831 à 2026. Rien n'y
est calculé, chaque barre est une somme de lignes d'inventaire, et c'est
pourquoi il mène : **33 aujourd'hui contre un seul en 1831**, un escalier qui ne
redescend que trois fois en deux siècles. Le deuxième MESURE, et la carte dit
avant la courbe que c'est un plancher très bas. Le troisième mesure une AUTRE
GRANDEUR, les annuités servies avant l'âge légal, ventilées par ce qui ouvre le
départ.

*Le modèle a déménagé du script vers `src/`.* `scripts/cout_avantages.py`
portait la décomposition ; elle est maintenant dans
`src/retraite_notionnelle/avantages.py`, que le script appelle et que
`moteur/js/avantages.js` porte à l'identique. Le paquet de données transporte
l'inventaire sous la clé `avantages`, comme il transporte déjà celui des
régimes. Deux rendus au caractère près, vérifiés par le témoin `avantages` de
`tests/temoins/pages.json`.

*Le calcul est six fois plus rapide en JavaScript qu'en Python* (0,6 s contre
4,0 s), et deux fois plus rapide qu'il ne l'était : `decomposer` ne calcule plus
que le scénario 1, là où la grille rendait les six alors que cette décomposition
n'a besoin que de l'étalon.

**UNE ERREUR TROUVÉE EN TRAÇANT LA COURBE, ET C'EST LE RÉSULTAT DU VOLET.** Le
troisième graphique portait un pic : la bande des régimes spéciaux triplait sur
les deux dernières années, et le total de 2024 annonçait 23,7 milliards. Effet
de bord. Chaque génération de la grille représente cinq cohortes, qui portent
toutes l'âge de départ calculé pour la génération ; la comparaison, elle,
opposait cet âge à l'âge légal de CHACUNE des cinq. Comme la réforme de 2023
relève cet âge d'un trimestre par génération, les cohortes les plus jeunes de
chaque tranche devenaient « anticipées » sans que rien n'avance leur départ.
L'âge légal est désormais lu une fois, pour la génération de la grille, et seules
les années réellement précoces comptent. **Le vrai chiffre est 13,7 milliards en
2024** — 7,5 pour le classement, 3,8 pour la carrière longue, 2,4 pour les
régimes spéciaux —, la série est continue, et l'attribution par motif cesse de
ranger des carrières du privé sous « régimes spéciaux ». Les chiffres du volet B
ont été repris partout où ils étaient écrits. La leçon : *un tracé voit ce qu'un
tableau cache*. La table par pas de dix ans ne montrait pas le pic ; la courbe
l'a montré au premier coup d'œil.

*Ce que la page a coûté en règles d'écriture.* Sept tests du dépôt l'ont refusée
avant de l'accepter : budget de lecture, incises en tiret, procédé « ce n'est pas
X, c'est Y », titre de gabarit « Ce que cette page ne dit pas », tableaux sans
légende ni en-tête de ligne, navigation. Tous ont été satisfaits en réécrivant,
aucun en desserrant une borne — sauf deux entrées nouvelles dans les tables de
budget, commentées sur place. Contrôlée au navigateur à 1280 et 390 pixels :
trois graphiques, aucun débordement horizontal, aucune erreur de console.

**Fichiers.** `src/retraite_notionnelle/avantages.py` ;
`moteur/js/avantages.js` ; `_avantages` et ses trois dépliants dans
`src/retraite_notionnelle/web/pages.py` et `moteur/js/pages.js` ; route et
message d'attente dans `index.html` ; barre de navigation dans
`web/gabarit.py` et `moteur/js/gabarit.js` ; `scripts/construire_donnees.py`
(clé `avantages`) et `scripts/construire_temoins.py` (témoin `avantages`).

**Volet D — les neuf lignes « intégré » qui restaient.** À la demande. Onze
avantages sont servis par le scénario 1 sans que la cascade les isole ; deux
avaient été mesurés au volet B. Les neuf autres le sont maintenant, ou disent
pourquoi elles ne le seront pas.

*Un mécanisme, trois voies, et aucune ne touche au moteur.* Un avantage qu'on ne
lit pas, on le retire, et l'écart est la ligne. `NEUTRALISATIONS` déclare pour
chacun par où le retrait passe : par la CARRIÈRE quand l'avantage tient à ce que
l'assuré a vécu (une année de chômage devient une année sans activité) ; par le
CATALOGUE quand la fiche du régime le déclare (un catalogue dont
`avantages_non_contributifs` ou `points_minimum_annuels` est dépouillé produit un
régime qui ne sert plus l'avantage) ; par une TABLE quand il vient d'un barème
daté (le barème de carrière longue vidé, la date d'effet du salaire de référence
des parents repoussée). C'est la condition pour que la mesure reste une mesure :
si le calcul changeait, on comparerait deux modèles et non deux droits.

*La voie du catalogue est validée par un second chemin.* La catégorie active se
mesurait déjà en changeant le STATUT de l'agent pour le statut sédentaire de
mêmes caisses. Les deux chemins — l'un par les données du régime, l'autre par
celles de la carrière — donnent **le même euro sur cinq générations**, et un test
l'exige. La mesure retenue est celle du catalogue : elle vaut pour tout avantage
qu'une fiche déclare, là où le statut témoin suppose qu'il en existe un, ce
qu'aucun régime spécial n'offre.

*Ce que chacune vaut, génération 1985, à date de départ inchangée* : catégorie
active 4 530 €, jouissance militaire 4 420 €, périodes assimilées 4 526 €,
salaire de référence des parents 729 €, garantie minimale de points 205 €,
carrière longue 0 €. Sous une dose de cinq années de chômage et d'une année de
service national — hypothèse affichée comme telle : périodes assimilées 12 062 €
au salaire moyen et 18 350 € au cadre, service national 2 996 € et 5 693 €,
points gratuits de complémentaire 1 427 € et 8 585 €.

**TROIS RÉSULTATS QU'ON N'ATTENDAIT PAS.**

- *La carrière longue ne vaut rien sur le montant.* Le barème vidé, la pension ne
  bouge pas d'un euro : un assuré entré tôt réunit sa durée de toute façon, et le
  taux plein lui est acquis avec ou sans le dispositif. Elle ouvre la porte ;
  elle ne remplit pas la pension. Tout son prix est dans la durée — 3,8 Md€ en
  2024, rien avant 2010.

- *La décote surpunit l'anticipation ordinaire et sous-punit l'extrême.* Comparée
  au coefficient de conversion notionnel, qui est actuariel par construction, sur
  un fonctionnaire sédentaire de 1965 : le droit actuel est plus dur de 2,3
  points à deux ans d'avance, de 6,4 points à cinq ans, puis la décote bute sur
  son plafond de vingt trimestres et il devient plus doux — de 1,5 point à huit
  ans, de 5,1 à dix, de 7,6 à douze. Or l'anticipation extrême est exactement
  celle de la catégorie active, de la super-active, de la conduite SNCF et des
  militaires. **Le barème est le plus clément là où il devrait l'être le moins**,
  et c'est ce que `--duree` retrouvait par un autre chemin.

- *Chiffrer les neuf n'a pas déplacé la masse d'un euro.* La décomposition
  annuelle vaut toujours 12,6 Md€ en 2024, aux mêmes sept lignes. Quatre des huit
  mesures sont nulles sur la fenêtre publiée, et aucune de ces absences n'est un
  défaut : le salaire de référence des parents ne s'applique qu'aux pensions de
  septembre 2026 et la dernière dépense publiée est de 2024 ; la garantie
  minimale de points ne mord que sur des carrières qui liquident après 2024 ; le
  service national et les points gratuits de complémentaire ne sont portés par
  aucun cas type. **Le but n'était pas de déplacer le total mais de savoir
  pourquoi chaque ligne vaut ce qu'elle vaut.** Une liste qui ne dit pas cela
  n'est pas une liste : c'est un tableau de zéros.

*Le refus reste, et il est mieux argumenté.* La jouissance militaire se mesure
sur certaines générations — 4 420 € en 1985 — et se refuse sur d'autres, où le
retrait déplace aussi la durée requise, 172 trimestres contre 160. Le garde-fou
compare les deux durées et refuse partout dès qu'elle est faussée quelque part.

*Les trois dernières ne sont pas des dispositifs*, et se chiffrent ailleurs : le
rendement supérieur à ce que l'assiette porte est le rapport du scénario 2 au
scénario 1, soit 307,5 Md€ en part salariale et 133,7 avec la part patronale ; le
financement non contributif se lit dans `structure_ressources_retraite.csv`, où
les cotisations ne font que 65,6 % des ressources de 2025, dont un noyau
indiscutable de 13,5 % pour la contribution d'équilibre et les subventions.

*Quatre tests de plus*, dont celui qui prouve que les deux chemins de la
catégorie active coïncident, celui qui exige qu'une neutralisation nomme ce
qu'elle retire, celui qui interdit qu'une douzième ligne « intégré » apparaisse
sans réponse, et celui qui vérifie qu'une variante ne déplace pas une pension
qu'elle ne concerne pas — un catalogue sans classement ne doit rien faire à un
cadre du privé.

*Le portage suit, et la parité est vérifiée couple par couple* : les 342 couples
de la grille rendent exactement les mêmes parts des deux côtés. Le calcul JS
passe de 0,6 à 1,5 seconde, le Python de 4 à 8.

**Fichiers.** `src/retraite_notionnelle/avantages.py` (`Neutralisation`,
`NEUTRALISATIONS`, `scenarios_neutralises`, `recalculer`) et son portage
`moteur/js/avantages.js` ; `scenario-actuel.js`, dont le seuil des parents
devient une propriété d'instance comme l'attribut de classe du Python ;
`scripts/cout_avantages.py` (`--par-carriere` montre les huit lignes et la dose) ;
`tests/test_avantages.py` ; `data/reference/legislation/avantages_non_contributifs.yaml` ;
`docs/avantages_non_contributifs.md` §4 ter ; `docs/limites.md` §5.

**Volet E — la réversion, lue dans les séries de la DREES.** À la demande, et
c'était la deuxième priorité de la liste ci-dessous. C'est la ligne la plus
lourde de tout l'inventaire : **38,3 Md€ en 2024, soit 9,0 % de la dépense de
retraite**, contre 25,4 Md€ en 2004. À elle seule, elle pèse trois fois tout ce
que le modèle mesure par ailleurs, et porte le total chiffré de 12,6 à
**50,9 Md€, soit 11,9 % de la dépense** au lieu de 3,0 %. Le COR chiffre les
droits de solidarité à « de l'ordre d'un cinquième » : on en tient désormais les
trois cinquièmes.

*Elle ne se calcule pas, et aucune des trois voies de retrait du volet D n'y
peut rien* : on ne retire pas un avantage qui n'a jamais été servi. Le modèle
décrit une CARRIÈRE et non un ménage — ni conjoint, ni date de décès, ni
ressources du survivant —, et les 756 périodes du catalogue qui déclarent
`reversion` sont une intention que nul code ne sert. La seule issue était de la
LIRE.

*La source était déjà dans le dépôt, à une colonne près.* L'enquête annuelle de
la DREES auprès des caisses de retraite alimentait les effectifs de retraités de
droit direct depuis l'action 1. La même feuille porte, pour chaque couple
(caisse, année), le nombre de bénéficiaires d'un droit dérivé et le montant
mensuel moyen de ce droit-là. `lire_cadrage` a donc été généralisée à un couple
(champ, mesure) plutôt que dupliquée : les deux lectures passent par le même
filtrage et la même règle de millésime, et deux fonctions séparées auraient
divergé à la première correction de campagne.

**DEUX PIÈGES, ET ILS COÛTENT CHER.**

- *La colonne.* Le classeur porte `mont`, qui est la pension TOTALE du
  bénéficiaire, droit direct compris — 745,60 € à la Cnav en 2020 —, et `m2`,
  qui est la seule part dérivée : 326,70 €. Prendre la première aurait doublé la
  masse. Le classeur se contrôle lui-même : la moyenne des `m2` du champ
  « dérivé seul » et du champ « cumul des deux », pondérée par leurs effectifs,
  vaut exactement le `m2` du champ « dérivé total ».
- *La somme des caisses.* Un polypensionné touche une réversion à la Cnav ET à
  l'Agirc-Arrco : la somme des effectifs compte deux fois la même veuve, 8,5
  millions au lieu de 4,4. Les MASSES, elles, s'additionnent sans double compte,
  et leur somme recoupe la ligne « tous régimes » à 2 % près — c'est le contrôle
  interne de la série, et il est écrit dans son en-tête.

*Ce qu'elle change au statut de la page.* C'est la ligne la plus SÛRE de tout
l'inventaire, par un renversement qui mérite d'être dit : elle est la seule qui
ne repose pas sur les treize carrières types, et dénombre 4,4 millions de
personnes réelles. Les huit lignes mesurées par retrait sont, elles, aussi
bonnes que la grille — c'est-à-dire pas très bonnes.

*Une carte pour tout, et une fenêtre pour prix.* La réversion a d'abord eu sa
carte, pour une raison graphique : empilée avec les autres, dont la série
remonte à 1959, elle dessinait une falaise de vingt-cinq milliards en 2004. À la
demande — « je voudrais ne pas faire de carte dédiée, je souhaite garder une
carte pour tous les avantages dans une seule carte » —, les deux ont été
réunies, et c'est la FENÊTRE qui absorbe la difficulté : le tracé commence en
2004, là où la réversion commence. Le choix gagne même en cohérence, les poids
des carrières types venant eux aussi d'une série que la DREES ne publie que
depuis 2004 ; la fenêtre commune est celle où chaque terme du produit est
observé. Ce que les années antérieures montraient — un minimum vieillesse qui
pesait le tiers de la dépense en 1960 — reste dans le script, qui remonte à
1959. La page garde ses trois cartes et ses budgets de lecture d'origine.

*Ce qui reste hors de portée.* La réversion n'est pas tout le droit dérivé.
L'allocation veuvage est marginale ; la majoration de réversion de L. 353-6 est
comprise dans ce que l'EACR mesure, la caisse la versant avec la réversion ; les
pensions d'orphelin sont publiées à part par le Service des retraites de l'État
et n'ont pas été reprises.

**Fichiers.** `scripts/fetch/drees_eacr.py` (`lire_cadrage` généralisée,
`CHAMP_DERIVE`, `COLONNE_DERIVE`) ; `scripts/verifier_donnees.py`
(`source_droits_derives`, certification `droits_derives`) ;
`data/reference/macro/droits_derives.csv`, 305 valeurs certifiées 2004-2024 ;
`donnees/depenses.py` et son portage, qui exposent `reversion(annee)` ;
`avantages.py` (`LIGNES_LUES`) et `moteur/js/avantages.js` ; la carte
`avantages-reversion` de la page, dans les deux portages ;
`data/reference/legislation/avantages_non_contributifs.yaml` ;
`docs/avantages_non_contributifs.md` §4 quater ; `docs/limites.md` §5.

**Fichiers.** `data/reference/legislation/avantages_non_contributifs.yaml` ;
`tests/test_avantages.py` ; `scripts/cout_avantages.py` ;
`docs/avantages_non_contributifs.md` ; renvois posés dans
`docs/methodologie.md` §6 et `docs/limites.md` §5.
- **Septembre 2026, action 35, volet A : la convention de l'État, tranchée.**
  Le programme a décidé — la contribution d'équilibre disparaît, l'État cotise
  à 18 % comme tout employeur.

  **Vérifier avant d'implémenter a changé le travail** : le code faisait déjà
  cela. La contribution d'équilibre est marquée `contributive` dans
  `equilibre.py`, elle entre donc dans `part_contributive` — 77,3 % des
  ressources, dont 65,6 de cotisations et 11,7 de contribution — et c'est toute
  cette enveloppe que les 18 % remplacent ; le terme reconduit est son
  complément, d'où elle est absente. Le raccord n'est juste que parce que
  l'assiette couvre TOUTES les branches, traitements des fonctionnaires
  compris : les 18 % qu'on leur applique SONT ce que l'État verse désormais.

  **Ce n'est donc pas un changement de calcul mais une mise sous garde.** La
  convention était vraie par accident de construction : elle reposait sur un
  drapeau que personne ne protégeait, et décocher `contributive` sur ce poste
  aurait fait reconduire la contribution EN PLUS des 18 % sans qu'aucun test ne
  bronche. Le docstring l'écrit maintenant, et un test la tient.

  **Ce que la décision ne tranche pas** : 23,1 % des ressources restent
  reconduites — impôts affectés 1,944 point de PIB, transferts 0,665,
  subventions d'équilibre 0,274, autres produits 0,303. Les subventions sont le
  cas le plus discutable, et la ventilation par régime dit pourquoi : 60,8 % du
  financement de la SNCF et de la RATP en 2023, 81,1 % des mines, et 94,5 % de
  la SNCF en 2070. Ce ne sont pas des cotisations d'employeur que 18 %
  remplaceraient, mais des charges de liquidation de régimes fermés que le
  budget porte quoi qu'il arrive.

- **Septembre 2026, action 35, volet A : les subventions d'équilibre sortent
  du scénario 6.** Décision du programme, et l'argument ne porte pas sur la
  comptabilité mais sur la NATURE de ce qu'on reconduisait.

  Une subvention d'équilibre comble le compte d'un régime dont les cotisants
  ont disparu avant les retraités — la SNCF, les mines, les marins, financés à
  61, 81 et 76 % par le budget en 2023, et la SNCF à 94,5 % en 2070 selon le
  classeur du COR. **Le scénario 6 fusionne tous les régimes : il n'y a plus de
  retraité sans cotisants dès lors qu'il n'y a plus qu'un régime.** L'objet de
  la subvention disparaît avec les régimes qu'elle équilibrait ; les pensions
  restent dues et sont servies comme les autres, pour partie recalculées à la
  baisse par le notionnel, pour partie portées par les cotisants du système
  unifié.

  **Mesuré** : le solde moyen du scénario 6 sur les 45 années projetées passe
  de −0,875 % à −1,117 % du PIB, soit 0,242 point perdu. C'est exactement ce
  que l'ancienne hypothèse lui offrait, et reconduire une subvention dont
  l'objet a disparu était la dernière grande faveur qu'on lui faisait.

  La feuille de route affirmait le contraire — que ces subventions « survivent
  à toute réforme le temps que leurs pensionnés s'éteignent ». C'est faux d'une
  réforme qui FUSIONNE, et la ligne est corrigée au volet A, point 4.

  Porté dans `moteur/js/cout.js`, témoins régénérés, 956 tests verts. Reste
  reconduit et non tranché : impôts et taxes affectés (1,944 point de PIB),
  transferts (0,665), autres produits (0,303).

  [Corrigé le 19 septembre 2026 au soir.] Cette entrée ajoutait ici que « le
  même argument vaudrait pour les impôts, qui compensent des allègements qu'un
  système sans exonération ne consent pas ». C'est faux, et c'est la phrase que
  le dépôt avait démolie le matin même : la TVA qui compense les allègements
  finance la branche maladie. Les impôts affectés sont bien sortis le soir,
  mais par l'argument des 18 %, et l'entrée qui clôt ce journal le dit.

  **Rien n'est écrit au public**, à la demande du programme : la page affiche
  les chiffres nouveaux, mais aucune prose n'explique encore ce fonctionnement.
  Il faut d'abord vérifier que ces chiffres font un système cohérent.

- **Septembre 2026, action 35, les impôts et taxes affectés sortent aussi.**
  Troisième et dernière des décisions du 19 septembre, et celle qui exigeait
  d'abord une rétractation : l'argument offert au programme pour la lui
  proposer — « ils compensent des allègements de cotisations patronales qu'un
  système sans exonération ne consent pas » — est celui que le dépôt avait
  lui-même démoli le matin même, deux entrées plus haut. La TVA qui compense
  les allègements finance la branche MALADIE, et le compte de la CNAV n'en
  porte aucune ligne. La phrase reconduite à tort dans cette feuille de route
  au paragraphe précédent est donc fausse, et remplacée par celle-ci.

  **L'argument qui vaut est celui des 18 %** : un compte notionnel ne crédite
  que ce qui est assis sur un revenu d'activité. Un impôt affecté n'ouvre de
  droit à personne ; le porter au crédit d'un système qui ne rend que ce qui a
  été cotisé, c'est lui prêter une recette sans contrepartie. C'est le même
  argument qui a fait sortir la contribution d'équilibre et les subventions, et
  il n'a rien à voir avec ce que ce poste compense.

  **Il fallait ne le retirer qu'une fois.** 38 % du poste sont les ressources
  du fonds de solidarité vieillesse (21,7 des 57,1 Md€ de 2024), et ce que ce
  fonds VERSE aux régimes — 19,6 Md€ — était déjà retiré par `retrait` depuis
  le matin. Sortir le poste en entier sans toucher au retrait aurait fait
  sortir la même somme deux fois : exactement l'erreur que le dépôt avait
  relevée et corrigée quelques heures plus tôt. D'où `retrait_par_impot`, qui
  est cette somme et que le scénario 6 rend au compte à l'instant où le poste
  s'en va. Les quatre autres scénarios notionnels, qui encaissent toujours les
  impôts affectés, gardent le retrait entier. Un organisme porte désormais le
  drapeau `recette_par_impot` dans `equilibre.py`, et c'est le seul.

  **Mesuré** : le solde moyen du scénario 6 sur 2026-2070 passe de −1,117 % à
  **−2,512 %** du PIB, contre −1,135 % pour le système actuel. Il est plus
  déficitaire que lui dans 38 des 45 années (contre 27 avant), ne revient à
  l'équilibre sur aucune, et son coefficient d'équilibre tombe de 0,97 à 0,82.
  La sortie coûte 1,395 point, six fois ce que coûtaient les subventions.

  **Ce que les trois décisions donnent ensemble** : le scénario 6 ne compte
  plus que les 73 % de ressources assises sur un revenu d'activité, et il est
  désormais, sur la moyenne des 45 années, le PLUS déficitaire des chemins
  comparés. La convention `rapport`, qui reste calculable, ne porte AUCUNE des
  trois décisions : elle n'est plus « l'ancienne façon de calculer le taux »
  mais un repère d'avant septembre 2026, et son test le dit maintenant.

  Porté dans `moteur/js/cout.js` et `moteur/js/equilibre.js`, témoins
  régénérés, 984 tests verts. Deux postes restent reconduits, et cette fois
  sans qu'un argument traîne pour les retirer : les transferts d'organismes
  extérieurs (0,665 point de PIB, et ce qu'ils portent de non acquis sort déjà
  par `retrait`) et les autres produits (0,303 point, des recettes de gestion
  des caisses).

  **La glose publiée portait encore l'argument faux** et a été corrigée dans
  les deux ports : le poste « impôts et taxes affectés » annonçait « pour
  l'essentiel, la compensation des allègements généraux ». La réserve de la
  page Coût qui disait ces postes « reconduits tels quels » a été réécrite.

  **Rien de plus n'est écrit au public**, toujours à la demande du programme.


**Volet F — tous les avantages sur la page, et les huit postes que les comptes
publient.** À la demande : « je veux qu'on mette absolument tous les avantages
sur cette page, j'ai l'impression qu'on n'a même pas mis moitié jusqu'à
présent ». C'était exact : douze dispositifs sur trente-neuf portaient un
chiffre, et la page ne nommait les autres que dans un dépliant refermé.

- *Huit postes des Comptes de la protection sociale* renseignent chacun une
  ligne de l'inventaire, et sont certifiés dans
  `data/reference/macro/prestations_non_contributives.csv` (40 valeurs,
  2020-2024). **Là où ils existent, ils REMPLACENT la ligne calculée** — premier
  critère de `data/sources.yaml`, le producteur prime sur le repreneur.
  L'écart dit ce que la grille coûtait : la majoration de pension pour trois
  enfants et plus valait **zéro** toutes les années de la série, faute d'un cas
  type qui atteigne le seuil de trois enfants, quand les comptes en portent
  **7,78 milliards**. Le total chiffré passe de 50,9 à **93,9 milliards en
  2024, soit 22,0 % de la dépense** — le COR chiffre les droits de solidarité à
  « de l'ordre d'un cinquième », et on y est. **Les lignes lues font 87 % de ce
  total** : ce que le modèle apporte ici n'est pas le chiffre, c'est la liste.

- *Les trente-neuf sont nommés sur la page*, famille par famille, chacun avec
  son coût ou, quand la case est vide, la phrase qui dit pourquoi — quinze
  chiffres, vingt-quatre raisons. Chaque montant dit aussi **d'où il vient**,
  « lu » ou « calculé » : un compte de personnes réelles et un recalcul sur
  treize carrières types ne se lisent pas avec la même confiance. Un test
  refuse qu'une ligne n'ait ni chiffre ni raison.

- *Trois défauts trouvés en vérifiant, et c'est le vrai contenu de ce volet.*
  **La page annonçait vingt-deux cases pleines et en montrait quinze** : elle
  comptait ce que le modèle SAIT chiffrer là où son tableau montre ce qui PORTE
  un chiffre — un avantage éteint se mesure très bien et vaut zéro. **La ligne
  de commande et le site avaient divergé**, 12,6 milliards contre 93,9, parce
  que la commande refaisait la décomposition pour elle seule, sans les postes
  lus ; le calcul vit désormais dans le modèle et les deux portes y mènent.
  **Le graphique empilait quinze lignes sur neuf couleurs**, six bandes
  portant la couleur d'une autre : il empile maintenant les familles, qui sont
  sept. Sa fenêtre, enfin, se CALCULE — l'intersection des fenêtres de
  publication des lignes lues — au lieu de tester la seule réversion comme
  avant ; sans quoi les postes publiés depuis 2020 auraient dessiné une falaise
  de quarante milliards où le lecteur aurait lu une explosion de la dépense.

- *Deux tests de plus* tiennent ce qui vient d'être réparé : toute ligne
  chiffrée appartient à une famille, faute de quoi elle disparaîtrait du
  graphique sans bruit tout en comptant dans le tableau ; et une série publiée
  ne s'interrompt jamais entre son premier et son dernier point, faute de quoi
  la fenêtre se couperait en deux.

**Ce qui reste du volet F.** L'allocation veuvage, les bonifications de service
des militaires et des corps actifs, les départs anticipés pour handicap et la
majoration de durée au titre du congé parental ne sont ni calculés ni isolés
par un poste publié. La page les nomme et dit ce qui manque à chacun ; c'est
une limite écrite, pas une dette cachée.


**Volet G — tous les chiffres, et sur le plus d'années possibles.** À la
demande : « il faut les chiffres pour tous et sur le plus d'années possibles ».
Deux demandes qui tirent en sens opposés, puisque chaque ligne nouvelle vient
d'une source plus courte que le modèle.

- *Un défaut d'abord, et il était grave.* La règle du volet F — le poste publié
  remplace la ligne calculée — n'était appliquée qu'aux années que le poste
  couvre. Le minimum vieillesse valait donc **0,02 Md€ en 2019 par le modèle et
  4,01 Md€ en 2020 par les comptes, dans la même série** : un facteur deux
  cents à l'intérieur d'une ligne, invisible tant que le graphique commençait
  en 2020. Une falaise cachée dans une ligne est pire qu'une falaise entre deux
  lignes, parce que personne ne va la chercher. Règle posée et testée : **une
  ligne qui a une fois un poste publié est publiée sur toute sa longueur.**

- *Deux tracés plutôt qu'un compromis.* Vérifié auprès du producteur et non
  supposé : l'API des comptes de la protection sociale ne publie aucun
  sous-poste du risque vieillesse-survie avant 2020, quand le total remonte à
  1959. Aucune fenêtre ne contient tout. La page porte donc le NIVEAU sur
  2020-2024 (95,2 Md€, 22,3 %) et la FORME sur 1959-2024 (le modèle seul,
  13,1 Md€, 3,1 %), en disant qu'ils ne s'additionnent pas. La forme longue
  montre un **minimum vieillesse à 31 % de la dépense en 1959**, qui s'éteint à
  mesure que les carrières se complètent, puis une remontée à partir des années
  1980 : les dispositifs qui rattrapent une carrière incomplète remplacent ceux
  qui secouraient une carrière absente.

- *Trois dispositifs que l'inventaire ne portait pas*, trouvés en parcourant
  l'arbre des comptes poste par poste, base légale lue dans l'index LEGI :
  l'**indemnité temporaire de retraite outre-mer** (décret n° 52-1050 du
  10 septembre 1952, fermée par l'article 137 de la LFR 2008), 0,26 Md€ ; la
  **retraite du combattant** (L. 321-1 CPMIVG), 0,50 ; la **majoration de
  pension des assurés handicapés** (L. 351-1-3 CSS), 0,03. Elles ne pèsent que
  0,8 milliard, et ce n'est pas le point : elles étaient publiées depuis 2020 et
  personne ne les avait regardées. L'inventaire avait été bâti depuis les trois
  listes du dépôt, qui disent ce que le MODÈLE sait faire, au lieu de la
  nomenclature du producteur, qui dit ce que le SYSTÈME verse. C'est la seconde
  qui fait foi sur l'exhaustivité.

- *Le compte écrit en prose a été retiré partout où il n'était pas calculé.*
  « Trente-neuf » figurait en toutes lettres à huit endroits du site et s'est
  périmé d'un coup en passant à quarante-deux. Un nombre qui vit dans une
  phrase est un nombre qui ment un jour.

**Ce qui reste du volet G.** Vingt-quatre dispositifs sur quarante-deux n'ont
toujours pas de chiffre, et les raisons se rangent en trois tas. Deux ne sont
pas encore en vigueur (surcote parentale, salaire de référence des parents,
applicables à compter de 2026) : aucun chiffre ne peut exister. Trois ne sont
pas des dispositifs mais des écarts de règle, mesurés ailleurs. Les
dix-neuf autres attendent une source : les bonifications de service des
militaires et des corps actifs, dont le rapport du Service des retraites de
l'État ne donne PAS la masse — vérifié, voir le volet H ; l'allocation
veuvage, que les comptes noient dans un poste « autres droits dérivés » ; le
service national et le congé parental, qu'aucune nomenclature n'isole.


**Volet H — le rapport du SRE, lu : il ne porte pas les bonifications.** À la
demande. Le volet G laissait les bonifications de service comme « prochain
gisement, et il est identifié » : le rapport annuel du Service des retraites de
l'État. Il a été lu, et la piste est fausse.

- *Quatre éditions lues* — 2019, 2021, 2023, 2024 — plus les deux infographies
  « Les chiffres-clés des retraites de l'État » de juin 2026. C'est un rapport
  d'**activité**, pas un document statistique : les bonifications n'y
  apparaissent que comme part du contentieux (8 % des nouvelles affaires en
  2023, 5,5 % en 2024) et comme jurisprudence du Conseil d'État. Aucune masse,
  aucun effectif, aucun trimestre. Les infographies n'en parlent pas du tout.

- *Le bon document est le jaune budgétaire* « Pensions de retraite de la
  fonction publique ». La preuve est dans son tableur compagnon, mis en ligne
  sur data.gouv.fr pour le PLF 2012 : il porte une feuille nommée
  `bonifications`. Les éditions récentes sont sur budget.gouv.fr, que protège
  un pare-feu anti-robot (Incapsula) — ni `curl` ni navigateur ne passent, et
  le dépôt ne contourne pas. La limite est donc DOCUMENTÉE au lieu d'être
  ouverte, ce qui vaut mieux qu'une piste qu'on croit tenir.

- *Un gain latéral, qui n'était pas cherché.* La jurisprudence citée par le
  rapport 2023 (Conseil d'État, 11 octobre 2023, n° 454135 et suivants) nomme
  le texte de la bonification du cinquième des personnels actifs de police, que
  l'inventaire portait depuis le début en « statuts particuliers — à
  certifier ». Lu dans LEGI et posé : **loi n° 57-444 du 8 avril 1957, articles
  1er et 6**, un cinquième du temps passé en services actifs, plafonné à cinq
  annuités, et subordonné depuis le 28 décembre 2023 à la condition de durée de
  services du onzième alinéa du 1° du I de l'article L. 24. Une des deux lignes
  « à certifier » de l'inventaire est close.

**Ce qui reste du volet H.** Deux voies pour la masse, et aucune n'est
satisfaisante : demander le tableur du jaune à sa source, ou reprendre celui du
PLF 2012, dont les valeurs auraient quinze ans. Les textes des corps autres que
la police restent à certifier : l'index renvoie l'article 125 de la loi
n° 83-1179 du 29 décembre 1983 pour les sapeurs-pompiers, dans une version qui
s'arrête en 2000, et la suite n'a pas été lue.


**Volet I — le tableur du jaune PLF 2012, récupéré et lu.** À la demande, et
dans la suite du volet H, qui avait établi que le rapport du SRE ne porte pas
les bonifications et que le jaune budgétaire les porte.

- *Une seule édition est publique hors de budget.gouv.fr*, celle du PLF 2012,
  sur data.gouv.fr. Récupérée. Sa feuille `bonifications` donne, pour les
  pensions entrées en paiement en 2010, le nombre de bénéficiaires et la durée
  moyenne en trimestres de sept bonifications, civils et militaires séparés.

- *Le chiffre qui saute aux yeux* : la bonification du cinquième touche
  **12 817 des 12 912 pensions militaires de l'année, soit 99,3 %**, pour 16,4
  trimestres en moyenne — plus de quatre annuités que personne n'a cotisées,
  servies à la quasi-totalité des militaires qui partent. Les bénéfices de
  campagne en touchent quatre sur cinq (12,8 trimestres), les services aériens
  ou sous-marins plus d'un sur deux. Chez les civils, la plus longue est celle
  qui ne relève pas de l'article L. 12 du CPCMR, 19,1 trimestres, que la note
  du tableau dit principalement attribuée aux policiers et aux agents
  pénitentiaires : c'est la bonification de la loi n° 57-444 certifiée au
  volet H.

- *Ce n'est pas un coût, et ces chiffres ne sont pas certifiés.* Trois réserves
  dont chacune suffirait : c'est un FLUX d'entrée et non un stock ; ce sont des
  bénéficiaires et des trimestres, jamais des euros ; ils datent de 2010. Ils
  vivent donc dans les notes de l'inventaire, avec leur date, et la page ne les
  affiche pas. L'inventaire disait pourtant de ces lignes « population
  étroite » : c'est vrai chez les civils et faux chez les militaires, où la
  bonification est la règle. Une ligne sans chiffre invite à la croire petite.

- *Il a fallu écrire le lecteur.* Le lecteur de classeurs Excel 97 du dépôt ne
  rendait que les nombres, par un choix assumé et écrit dans son en-tête. La
  feuille rendait donc trente-sept nombres et pas un libellé. La table des
  chaînes partagées est maintenant décodée, coupures comprises — un même mot
  peut être coupé en latin-1 et reprendre en UTF-16, parce qu'Excel choisit la
  largeur morceau par morceau. Mal décodée, la table ne lève rien : elle
  DÉCALE, et tous les libellés suivants glissent sous d'autres lignes. Un test
  synthétique force ce cas. Le lecteur rend désormais `float | str`, comme
  celui des classeurs modernes, et son unique appelant a été mis à l'abri des
  en-têtes qu'il reçoit maintenant en plus des années.

**Ce qui reste du volet I.** Une édition récente du jaune, que budget.gouv.fr ne
laisse pas lire. Et la conversion en euros, qui demanderait une valeur du
trimestre par corps et par génération : le dépôt sait la calculer, mais ce
serait une déduction posée sur un flux de 2010, c'est-à-dire un chiffre
plausible et faux.

---

### 38. Le salaire net d'un actif, sous chaque système — `fait`

**La demande.** « Il faudrait afficher le salaire net pour chaque scénario pour
les actifs. Si on prend moins de cotisations, il faut montrer aux gens
l'avantage en net qu'ils reçoivent, sinon ce n'est pas très convaincant. C'est
vraiment le travail de réduire l'écart entre le net et le brut que tant de
politiques veulent mettre en place mais ne chiffrent jamais. »

**Ce qui est fait.** `src/retraite_notionnelle/remuneration.py` écrit une fiche
de paie — coût du travail, salaire brut, salaire net — sous n'importe quel bloc
retraite, et `data/reference/legislation/prelevements_remuneration.yaml` porte
les taux hors retraite qui manquaient au dépôt : maladie, famille, chômage,
accidents du travail, CSG, CRDS, et les contributions d'équilibre CEG, CET et
APEC, que les fiches de régime ne portent pas parce qu'elles n'acquièrent aucun
droit. Le site affiche trois chiffres sous les quatre pensions — le net
d'aujourd'hui, celui de la proposition, l'écart — et la fiche entière dans un
dépliant. Le portage `moteur/js/remuneration.js` suit, et trente-trois tests
tiennent l'ensemble.

Les systèmes 1, 2 et 3 partagent la même fiche de paie, au centime : ils ne
changent pas ce qui est PRÉLEVÉ, seulement ce qui est PORTÉ AU COMPTE. Seul le
système 4 y touche.

**Trois décisions, prises par le programme et écrites plutôt que devinées.**

- **L'incidence est intégrale.** Le coût du travail est tenu fixe — c'est ce que
  l'employeur a budgété, et aucune réforme des retraites ne le change — et le
  brut est celui qui l'épuise sous les nouveaux taux. Une cotisation patronale
  est du salaire différé ; ce que l'employeur ne verse plus remonte dans le
  brut, puis dans le net. C'est ce que veut dire « réduire l'écart entre le net
  et le brut », et le module le calcule par dichotomie au lieu de le postuler.
- **Les 18 % sont partagés moitié-moitié**, comme les 5 % capitalisés. La
  proposition ne le dit pas.
- **La réduction générale est modélisée**, et c'est elle qui commande le
  résultat.

**Deux résultats qui n'étaient pas prévus, et qui sont le sujet.**

*Un.* **Le gain net est négatif au SMIC** — −38 € par mois —, nul vers 1,2 SMIC,
et croît ensuite : +73 € au salaire moyen, +216 € à cinq SMIC. La raison est
mécanique, et tient à la réduction générale dégressive unique entrée en vigueur
le 1er janvier 2026. Son coefficient maximal, 40,21 %, est EXACTEMENT la somme
des taux patronaux de son périmètre : au SMIC, l'employeur ne verse déjà plus
rien. Un salarié au SMIC ne supporte donc aujourd'hui que les 11,3 points
salariaux ; la proposition en prélève 23, dont 9 seulement sont effacés. La loi
fixe ce coefficient « dans la limite de la somme des taux des cotisations
incluses dans le périmètre » (L. 241-13, III), si bien qu'un scénario qui baisse
la cotisation retraite baisse aussi l'allègement : le modèle refait l'addition —
0,3821 aujourd'hui, 0,3054 sous la proposition — plutôt que de figer le chiffre.
Les cinq points capitalisés font à eux seuls la bascule : sans eux, le gain est
positif à tous les niveaux de salaire. Ils ne sont pas perdus pour autant, et le
site les compte à part — ce compte reste au nom de l'assuré et se transmet.

*Deux, et c'est le plus lourd.* **Le partage salarial/patronal du taux unique
n'est pas neutre**, alors qu'on l'attendrait sous l'incidence intégrale. Les
tests l'ont démenti, pour deux raisons distinctes : la CSG et la CRDS sont
assises sur le BRUT, que le partage déplace ; et la réduction générale n'efface
que des cotisations PATRONALES. Au salaire moyen, le gain net mensuel vaut
**−144 €** si les 23 points sont entièrement salariaux, **+73 €** moitié-moitié,
**+275 €** s'ils sont entièrement patronaux. Le paramètre que la proposition
laisse ouvert pèse donc plus que la baisse de taux elle-même. C'est un résultat
sur le droit actuel plus que sur la proposition : il fait dépendre le salaire
net de la frontière entre les deux parts, alors que cette frontière ne change
rien à ce que le travail coûte ni à ce qu'il rapporte au système.

**L'extension aux trois autres familles, et la décision qu'elle demandait.**
La fiche de paie n'a longtemps valu que pour les salariés du PRIVÉ, et le site
n'en affichait aucune aux autres statuts plutôt qu'un net faux. Elle couvre
maintenant le public, les régimes spéciaux et les indépendants. Ce qui a été
tranché, et pourquoi :

- **Le découpage n'est pas celui des familles de statut, mais celui de ce qu'on
  SAIT de l'employeur.** Quatre profils : `salarie_prive` (employeur connu,
  régime général et Agirc-Arrco) ; `salarie_ircantec` (agent non titulaire,
  même chose sans la CEG, la CET et l'APEC) ; `agent_seul` (la fiche du régime
  ne porte que la retenue) ; `independant` (pas d'employeur). Le choix se lit
  dans les fiches de régime — `perimetre_taux == "agent_seul"` — et non dans
  une liste de statuts : c'est ainsi qu'un agent SNCF, que la fermeture de 2023
  a versé au régime général, reçoit bien la fiche de paie d'un salarié du
  privé, et qu'un régime spécial fermé demain suivra tout seul.
- **Pas de ligne « coût du travail » pour le profil `agent_seul`**, et c'est la
  première branche de l'alternative qui avait été posée. La contribution de
  l'employeur public est un taux d'ÉQUILIBRE — 82,28 % du traitement pour
  l'État en 2026 —, fixé pour que le compte « Pensions » tombe juste. Poser
  dessus l'incidence intégrale afficherait une hausse de salaire de
  soixante-dix points qui n'existe pas : la dette de pensions qu'il finance
  reste à payer, et c'est la page Coût qui en traite. La seconde branche —
  emprunter une contribution « de droit commun » — aurait demandé d'inventer un
  taux que personne ne verse ; le dépôt n'en écrit pas. Le traitement
  indiciaire brut est donc tenu fixe et seule la retenue de l'agent bouge :
  c'est `Incidence.ASSIETTE`, que le docstring du module annonçait depuis le
  début sans qu'elle existe, et qui existe maintenant.
- **Un indépendant paie tout lui-même**, et il fallait le corriger : la fiche
  du régime général porte la répartition 45/55 d'un salarié, qui ne le concerne
  pas. `bloc_droit_en_vigueur` lit désormais `sans_employeur`, comme
  `moteur/compte.py` le faisait déjà pour le compte notionnel ; sans ce
  correctif la fiche lui montrait un employeur qui n'existe pas et sous-estimait
  de moitié ce qu'il verse. Et les 18 % de la proposition sont à sa charge en
  entier, puisqu'elle les annonce « salariale et patronale additionnées ».
- **Les barèmes progressifs des indépendants ont été lus dans LEGI, pas dans
  OpenFisca**, qui en porte encore la rédaction de 2018 : la réforme de
  l'assiette unique de 2024 les a réécrits. Maladie et maternité (D. 621-1 et
  D. 621-2 : 8,50 % sous trois plafonds, réduits par cinq paliers en deçà),
  allocations familiales (D. 613-1), indemnités journalières (D. 621-3 : 0,50 %
  et non 0,70 %). Leur forme n'est pas celle d'un barème par tranches — le taux
  interpolé porte sur la TOTALITÉ de l'assiette —, d'où `BaremeProgressif`, et
  un test qui exige la continuité au raccord avec les tranches.

**Trois résultats de l'extension.** *Un.* Le salarial d'un fonctionnaire
titulaire se réduit à la retenue pour pension et à la CSG-CRDS, et la liste de
postes vide de son profil est un résultat vérifié : la cotisation maladie
salariale a disparu en 2018 comme dans le privé, un titulaire n'est pas assuré
contre le chômage, et la contribution exceptionnelle de solidarité a été
supprimée la même année. Son net vaut **79,4 %** de son traitement, à deux
dixièmes de point de celui d'un salarié du privé. *Deux.* La proposition ne
déplace presque rien pour lui : sa retenue passe de 11,10 % à 11,50 %, soit
−13 € par mois au salaire moyen. Tout le mouvement est du côté de l'État, et il
n'est pas sur une fiche de paie. *Trois.* Un indépendant ne garde aujourd'hui
que **57 à 60 %** de son revenu professionnel, contre 79 % pour un salarié — il
porte les deux parts —, et c'est le profil auquel la proposition rend le plus
au voisinage du revenu médian : +56 € par mois au SMIC, +89 € à 1,6 SMIC.

**Ce qui reste.** La MSA, l'outre-mer et les élus n'ont toujours pas de fiche de
paie : leurs taux hors retraite ne sont pas ceux du régime général, et mieux
vaut rien qu'un net faux. La RAFP, assise sur les primes, reste hors de
l'assiette du dépôt. Restent aussi à lire à la source les deux décrets de 2025
qui fixent la réduction générale, l'arrêté du taux d'accidents du travail retenu
dans son périmètre, et la convention d'assurance chômage de 2024 : le dépôt n'en
connaît aujourd'hui que les valeurs transcrites par OpenFisca, d'où la fiabilité
`haute` du fichier. Les neuf réserves sont dans `docs/limites.md` § 5 ante bis.

**Fichiers.** `src/retraite_notionnelle/remuneration.py` ;
`data/reference/legislation/prelevements_remuneration.yaml` ;
`scripts/fetch/openfisca_prelevements.py` ; `moteur/js/remuneration.js` ;
`tests/test_remuneration.py` ; `part_salariale_taux_unique` dans `config.py` et
`config.js` ; le bloc `_salaire_net` de `web/pages.py` et son portage ;
`scripts/construire_donnees.py` et le témoin `simuler_agent_non_titulaire` de
`scripts/construire_temoins.py` ; `docs/limites.md` § 5 ante bis ; les deux
lignes de journal du 19 septembre 2026 dans `legislation/veille.yaml`.

- **Septembre 2026, action 35, volet C : la ventilation droits directs /
  droits dérivés.** Le volet C demandait trois choses : ventiler la base,
  n'appliquer le rapport qu'aux droits directs, et DIRE ce que le scénario 6
  fait de la réversion. Les trois sont faites.

  **Le défaut, d'abord, parce qu'il n'était pas petit.** Le rapport de masses
  par lequel un scénario notionnel fait réagir la dépense est le quotient de
  deux masses calculées sur treize cas types, qui n'ont ni conjoint ni
  survivant : aucune réversion n'y entre, et `config.py` la range depuis
  toujours parmi les droits que même l'étalon ne sert pas. La base à laquelle
  il s'appliquait, elle, porte les deux. **Un scénario notionnel réduisait donc
  la réversion dans la même proportion que les pensions propres, sans que rien
  ne l'ait décidé** — et il le faisait aux trois endroits où un rapport
  multiplie une base : la dépense observée de 1959 à 2024, la trajectoire
  projetée, et le solde. La colonne « part de PIB » de la page Coût le faisait
  une quatrième fois, en multipliant directement `part_pib` par le rapport.
  `masse_du_scenario` est maintenant le seul chemin.

  **La source, et elle est meilleure que prévu.** Le classeur du COR déjà
  moissonné par `cor_regimes.py` porte les masses de pensions de droit direct
  et de droit dérivé, 2010-2070, régime par régime. Douze des vingt-deux
  régimes publient leur droit dérivé à part ; pour les dix autres — dont la
  fonction publique d'État et la CNRACL, qui pèsent — c'est la différence entre
  la masse de prestations et le droit direct, qui porte en plus un résidu de
  0,3 % des prestations. D'où `part_droits_derives.csv`, 61 années, niveau
  `haute` : **12,4 % en 2010, 10,4 % en 2024, 9,5 % en 2040, 5,7 % en 2070.**
  La réversion recule, et c'est la projection du COR qui le dit.

  **Le contrôle externe, qui est le point fort de cette passe.** La DREES
  ventile ses propres comptes en droit direct (poste `E11-21.1`) et droit
  dérivé (`E11-22.1`) depuis 2020, et `drees_cps.py` les récupérait DÉJÀ sans
  que rien ne les écrive. Ils entrent au niveau `certifiee` sous
  `pensions_droits.csv`. Deux producteurs, deux périmètres, deux
  nomenclatures, cinq années communes : **les parts s'écartent de 0,06 point au
  plus, et de 0,01 point deux fois.** `controle_part_droits_derives` l'exerce à
  chaque vérification, et un test le refait dans la suite.

  **La décision, écrite parce qu'il le fallait.** Ce que la ventilation ne
  tranche pas, c'est ce que le scénario fait de la part dérivée, et ce n'est
  pas un calcul. Le dépôt la SERT — la réversion est reconduite telle quelle,
  comme en Italie, où le capital notionnel du défunt se partage.
  `convention_reversion="supprimee"` calcule l'autre chemin, celui de la Suède,
  et il n'est pas le défaut pour une raison unique : **c'est le plus flatteur
  des deux.** Il rendrait 1,19 point de PIB au scénario 6 et de 0,4 à 1,2 point
  à chacun des autres, et le dépôt ne prend pas l'hypothèse flatteuse sans
  qu'un programme l'ait tranchée. À trancher, donc, par le Parti libéral.

  [Tranché le jour même, et dans l'autre sens : voir l'entrée suivante. Ce
  paragraphe raconte l'état du dépôt entre les deux, il ne décrit plus le code.]

  **Mesuré**, en point de solde moyen 2026-2070 : scénario 2, −0,81 ;
  scénario 3, −0,23 ; scénario 4, −0,27 ; scénario 5, −0,09 ; scénario 6,
  −0,35. Le scénario 1 ne bouge pas d'un iota, son rapport valant un, et un
  test l'exige. Le scénario 6 passe de −2,512 % à **−2,861 % du PIB** contre
  −1,135 % pour le système actuel ; il est plus déficitaire que lui dans 41 des
  45 années, contre 38 avant. Le scénario 5 franchit au passage la borne de
  −1 %, ce qui a demandé de rouvrir son test.

  **Deux bogues trouvés en chemin, et corrigés.** Le premier est à moi : les
  clés de `source_structure_financement_regimes` étaient des entiers là où le
  vérificateur attend des chaînes, si bien que `--appliquer` faisait planter la
  trace et aurait dupliqué chaque ligne du fichier. Il ne se voyait pas dans la
  suite de tests, qui lit les CSV sans relancer le vérificateur. Le second est
  d'affichage : la page multipliait `part_pib` par le rapport à la main, hors
  de tout chemin commun.

  **Ce qui reste du volet C** : dire ce qu'une réversion notionnelle SERAIT
  — partage du capital, ou rien — reste une convention et non un calcul ; le
  modèle ne saura pas en chiffrer une tant qu'il n'a pas de ménages. Et la
  part est très légèrement surestimée pour les dix régimes sans bloc dédié.

  Porté dans `moteur/js/cout.js`, `moteur/js/depenses.js` et
  `moteur/js/pages.js`, témoins régénérés, 1019 tests verts. La page Coût
  compte une douzième réserve, qui dit au public ce que les systèmes font de la
  réversion.

- **Septembre 2026, la réversion ne reste que dans le scénario 1.** Décision du
  Parti libéral, prise le jour même où le volet C a séparé les deux masses, et
  elle ne fait qu'appliquer à cette ligne la règle des trente-huit autres.

  **L'argument est celui du dépôt, pas un de plus.** Les scénarios 2 à 6
  retirent tous les avantages non contributifs, et
  `legislation/avantages_non_contributifs.yaml` range la réversion parmi eux
  depuis toujours : « non contributive au sens strict, la cotisation de
  l'assuré ayant déjà été rendue par sa propre pension », et « de très loin la
  PREMIÈRE dépense non contributive du système ». La servir dans un compte
  notionnel était l'exception non écrite. Ces cinq scénarios servent de témoins
  pour dire ce qu'une retraite composée UNIQUEMENT de part contributive
  représente ; une pension de réversion n'en est pas. Le scénario 1 la sert
  dans tous les cas : il est le droit en vigueur.

  **Un détour par une hypothèse que le programme a refusée, et qu'il faut
  consigner.** On avait d'abord retiré la réversion PROGRESSIVEMENT dans les
  scénarios prospectifs, au motif qu'une réversion dérive de la pension du
  défunt et qu'une réforme de 2026 ne reprend pas un droit ouvert en 2010 —
  avec une `part_post_bascule` calculée dans `_masses`. Le programme a tranché
  autrement, et sa règle est plus simple : **les cinq scénarios la retirent à
  tout le monde, du jour où ils s'appliquent.** Le code de la progressivité est
  retiré ; il ne reste qu'un drapeau, `reforme_en_vigueur`, qui dit si la
  bascule a eu lieu.

  Ce drapeau ne sert qu'aux scénarios PROSPECTIFS, et pour une raison qui n'est
  pas une nuance sur la réversion : avant leur bascule, ils SONT le système
  actuel — ils y recopient ses pensions, et un test tient l'égalité de leurs
  courbes à l'euro près. Leur retirer quoi que ce soit avant qu'ils existent
  ferait dire au modèle qu'une réforme de 2026 a économisé de l'argent en 1990.

  **À noter, parce que ce n'est pas le traitement des autres avantages.** Dans
  un scénario prospectif, un minimum contributif servi à qui a liquidé en 2010
  lui reste acquis pour toujours, sa pension entière étant recopiée. La
  réversion fait exception, et par décision du programme : aucun scénario
  notionnel n'en verse à compter du jour où il s'applique.

  **Mesuré** : **+1,19 point de solde moyen 2026-2070 à chacun des cinq**,
  exactement le même chiffre. La réversion retirée est une part de la BASE, qui
  ne dépend d'aucun rapport de masses, et les cinq la retirent sur la même
  fenêtre, celle qui commence à la bascule. Le scénario 1 ne bouge pas d'un
  iota, et un test l'exige.

  Le scénario 6 passe de −2,861 % à **−1,674 % du PIB**, contre −1,135 % pour
  le système actuel ; il n'est plus pire que lui que dans 33 des 45 années,
  contre 41. Le scénario 5 retrouve l'équilibre dès la bascule et repasse
  au-dessus du système actuel, sa moyenne restant négative — son test a été
  rouvert et réécrit.

  Porté dans `moteur/js/`, témoins régénérés, 1046 tests verts. La douzième
  réserve de la page Coût dit désormais l'inverse de ce qu'elle disait le
  matin : seul le système actuel sert la réversion.

---

### 39. Choisir entre le net et le brut, à toutes les étapes — `fait`

**La demande.** « Je veux qu'on puisse choisir entre le net et le brut dans
toutes les étapes du simulateur. »

**Le préalable, qui était tout le travail.** Le site savait déjà écrire un
salaire net — action 38 —, mais pas une pension nette : il opposait donc un net
à un brut, deux grandeurs différentes. Écrire une pension nette demande un taux
de CSG, et l'article L. 136-8 le fait dépendre du REVENU FISCAL DE RÉFÉRENCE du
foyer, que le simulateur ne demande pas. **Le programme a tranché pour le taux
plein**, appliqué à tous : 8,30 % de CSG, 0,50 % de CRDS, 0,30 % de CASA, soit
9,10 %. La convention surestime le prélèvement sur les petites pensions — une
pension de 660 € par mois serait exonérée des trois —, et c'est écrit sous la
clé de lecture comme dans `docs/limites.md` § 5 ante ter.

**Ce qui est fait.** Un réglage unique, `montants`, gouverne le simulateur
entier :

- **la saisie** : en mode net, le nombre tapé est un net mensuel, et le modèle
  remonte au brut en RÉSOLVANT la fiche de paie du statut — ce n'est pas une
  estimation mais l'inverse exact du calcul qui produit le net
  (`ConstructeurFiche.brut_a_net_donne`). Les quatre profils sont couverts ;
  les statuts sans fiche de paie lisent le nombre tel quel, et le formulaire le
  dit au lieu de le taire ;
- **l'affichage** : les deux chiffres de chaque carte, la composition de la
  proposition, la clé de lecture et son unité suivent le mode ;
- **l'adresse** : `montants` s'y écrit toujours, comme l'unité, parce qu'il
  gouverne l'interprétation du nombre « salaire ». Une adresse partagée décrit
  donc la carrière qu'on a calculée.

**Le piège, et c'est le même qu'à la bascule d'unité.** Le lien qui change de
mode TRADUIT les montants saisis. Le recopier tel quel ferait relire un net
comme un brut, et la page reviendrait en décrivant une autre carrière, mieux
payée d'un quart. Un test fait l'aller-retour : 2 500 € net ↔ 3 158 € brut, et
retour sur 2 500.

**Le défaut est le NET.** C'est ce qu'on touche et ce qu'on connaît de soi, et
c'est la seule comparaison cohérente avec le salaire net que l'action 38 avait
mis en avant. Le brut reste à un clic, et reste la langue de tout ce qui n'a pas
de net : un capital notionnel, une assiette de cotisation, les tableaux de
détail. La bascule ne gouverne que ce qu'on TOUCHE.

**Ce qui reste.** La cotisation maladie de 1 % sur la retraite complémentaire
n'est pas comptée — les scénarios notionnels ne distinguent pas base et
complémentaire, et l'appliquer aux uns et pas aux autres fabriquerait un écart
sans règle. La rente du pilier capitalisé suit le barème des pensions, par la
convention de la rente viagère à titre gratuit. Et le taux de CSG reste le taux
plein tant que le formulaire ne demandera pas de quoi faire mieux : le rendre
exact suppose un champ de plus, ou une inférence depuis la pension — celle que
le dépôt fait déjà pour l'ASPA.

**Fichiers.** Le volet `pensions` de
`data/reference/legislation/prelevements_remuneration.yaml` ;
`PrelevementsPension`, `brut_a_net_donne`, `salaire_brut_depuis_net` et
`salaire_net_depuis_brut` dans `src/retraite_notionnelle/remuneration.py` et
leur portage ; `MODES_MONTANT`, `Saisie.montants`, `Echelle`, `Montants`,
`_bascule_montants`, `_mention_conversion` et `_note_du_mode` dans
`web/pages.py` et `moteur/js/pages.js` ; paquet de données en version 15 ;
`docs/limites.md` § 5 ante ter ; la ligne de journal du 19 septembre 2026 dans
`legislation/veille.yaml`.
### 40. Un réglage se voit ou n'existe pas — `fait`

**Demande.** « Est-ce qu'on peut rendre plus simple et plus visible le bouton de
changement de brut/net ? Il faut quelque chose d'élégant et visible. »

**Le diagnostic.** L'action 39 avait posé la bascule en lien discret — « Voir
les montants en brut » —, sous les quatre cartes. Trois défauts, et le même à
chaque fois : un lien ne dit pas qu'il est un RÉGLAGE. Il ne montre pas l'état
courant, il ne montre pas l'autre état, et placé sous les chiffres il arrive
après qu'on les a lus. Le réglage le plus structurant du simulateur — celui qui
décide si le nombre affiché est ce qu'on touche — était le moins visible de la
page.

**Ce qui est fait.** Un composant, `g.bascule(légende, branches, actif)`, qui
écrit SES DEUX ÉTATS côte à côte, remplit l'actif à l'or du dépôt et laisse
l'autre en lien. C'est l'idiome des onglets, en plus petit : même bordure de
2 px, même hauteur de touche de 2,75 rem, `role="group"` et `aria-current` sur
l'état courant. Il tient sans JavaScript, chaque branche étant une adresse
complète.

Trois emplois, et le troisième n'était pas demandé :

- **le formulaire** : `MONTANTS [net] [brut]` ;
- **les résultats** : la même bascule, REMONTÉE au-dessus des quatre cartes.
  Un réglage qu'on découvre après avoir lu les chiffres arrive trop tard ;
- **l'unité** : `UNITÉ [€ par mois] [× salaire moyen]`, convertie au même
  composant. Deux réglages de même nature rendus différemment — un lien souligné
  d'un côté, un contrôle de l'autre — c'était précisément ce qui n'était pas
  élégant.

**Et l'étiquette du champ suit le mode.** « Revenu **net** mensuel », avec ses
repères convertis : SMIC 1 443 €, moyenne 2 751 €, plafond 3 170 € en net contre
1 823 €, 3 475 € et 4 005 € en brut. Demander un revenu brut sous une bascule
qui annonce le net faisait taper l'un pour l'autre.

**Un défaut trouvé au téléphone, et corrigé.** La première version mettait la
légende et les deux branches à plat dans un conteneur qui se replie : à 390 px,
« UNITÉ » gardait « € par mois » et renvoyait « × salaire moyen » à la ligne
suivante. Deux touches décalées d'une ligne ne se lisent plus comme un choix
entre deux états — elles se lisent comme deux boutons. Les branches vivent donc
dans une enveloppe `.choix` déclarée insécable : c'est la légende qui passe à la
ligne, et le contrôle reste entier. Un test l'exige.

**Le bogue que la bascule a révélé : deux croisillons dans une adresse.** La
bascule des résultats portait une ancre, `#resultats`, pour revenir sur les
chiffres plutôt qu'en haut du formulaire. Mais ici la ROUTE vit dans le
fragment — `#/simuler?…` —, et un second `#` ne fabrique pas une ancre : il
allonge la DERNIÈRE VALEUR de la requête. L'adresse écrivait donc
`montants=brut#resultats`, qui n'est pas un mode connu ; le modèle retombait sur
son défaut, la page revenait en net, et le salaire déjà converti en brut y était
relu comme un net. Le lecteur qui cliquait « brut » voyait ses montants monter
d'un quart, toujours étiquetés « € net/mois », et la bascule refusait de
revenir. L'ancre était de surcroît inutile : `reprendre()`, dans `index.html`,
pose déjà le focus sur `#resultats` et y fait défiler à chaque rendu.

Le test qui en sort ne garde pas la bascule mais **tout le site** : aucune
adresse rendue par aucune page ne porte deux croisillons. Il a immédiatement
trouvé une seconde occurrence, plus ancienne et jamais signalée — deux liens
`{g.lien("/methode/")}#capitalisation` dont le chemin devenait
`/methode/#capitalisation`, inconnu du routeur, qui renvoyait donc à l'accueil.
Ils pointent maintenant sur la page Méthode, dont le plan porte la section. Pour
aller à une section, le site a `data-vers`, que le routeur traite sans toucher à
l'adresse ; le docstring de `g.lien` le disait déjà — « l'ancre de section ne
peut pas s'y ajouter, la place est prise » —, et deux appels l'avaient contourné
à la main.

**La clé de lecture démentait les chiffres qu'elle explique.** Elle est écrite
une fois pour toutes, et l'action 39 ne l'avait pas relue : au-dessus de quatre
montants nets, elle annonçait « Montants BRUTS et au centime, comme la caisse
les verse : avant CSG, CRDS et impôt », puis « un brut sur un brut, donc plus
bas qu'un taux calculé sur des nets » au-dessus d'un taux de remplacement
calculé, précisément, sur des nets. Elle disait donc au lecteur de corriger
mentalement dans le MAUVAIS SENS le seul chiffre de la page qu'il ne peut pas
vérifier. Elle suit désormais le mode, et nomme le prélèvement en clair —
9,10 % de CSG, CRDS et Casa. Un test exige que chaque mode nomme son unité et
seulement la sienne.

Le glossaire, lui, sert les deux modes ET les pages qui n'ont pas de bascule :
il disait « Ici, un brut sur un brut », il dit maintenant que les deux termes
sont pris dans la même unité, quelle qu'elle soit. La page Méthode, qui
expliquait que tout le modèle est brut, ajoute que le simulateur sait afficher
des nets — le calcul, lui, reste brut de bout en bout.

**L'aide du champ promettait une conversion qui n'avait pas lieu.** Sous un
statut dont le dépôt n'a pas les prélèvements hors retraite — la MSA, l'élu,
l'ultramarin, qui n'a pas d'emploi —, le nombre saisi est lu TEL QUEL, et un
avertissement le dit. L'aide du champ, deux lignes plus haut, continuait
pourtant d'annoncer que « le modèle remonte au brut par les prélèvements de
votre statut ». Deux phrases se contredisaient à l'écran, sans rien pour dire
laquelle concernait le lecteur. L'aide suit désormais le même test que
l'avertissement — `echelle.convertit(statut)` —, et dit alors qu'elle ne peut
pas remonter au brut.

**Fichiers.** `bascule()` et son bloc CSS dans `web/gabarit.py` et
`moteur/js/gabarit.js` ; `_bascule_montants`, `_bascule_unite` et `_champ_revenu`
dans `web/pages.py` et `moteur/js/pages.js` ; feuille de style et témoins
régénérés.
---

### 41. Tarir la prose périmée, au lieu de la réparer un chiffre à la fois — `en cours`

**Pourquoi.** Le dépôt affirme des milliers de chiffres en prose, et une
vingtaine seulement étaient tenus par un test. Les autres étaient des
souvenirs : cette feuille de route donnait « plus de trois mille lignes » à
`actuel.py`, qui en fait plus de quatre mille, et « douze mille lignes » au
portage, qui en fait près du double ; le README annonçait un premier
chargement de 310 Ko quand il en transfère plus du double, « 123 simulations »
quand les témoins en figent 485, « quatre pages » à deux endroits quand la même
page en annonce six, et « près de cinq cents tests » pour un dépôt qui en
comptait plus de mille.

Le mal n'est pas le chiffre faux : c'est qu'on ne puisse pas savoir. Le dépôt
écrit son ÉTAT et son HISTOIRE dans les mêmes fichiers, dans la même
typographie, sans frontière. « 263 Ko de modèle » est faux aujourd'hui et était
vrai du temps de Pyodide, une ligne plus haut. Un test qui corrigerait ce
chiffre abîmerait le récit — et c'est pourquoi aucun test général n'était
possible.

La réponse d'avant était un test par chiffre, écrit après chaque dérive
constatée. Chacun répare, aucun n'empêche la suivante, parce qu'il faut à
chaque fois qu'un humain ait remarqué. Et la vague ne protège pas : le README
écrivait « près de cinq cents tests » pour n'avoir pas à tenir un compte exact,
et se trompait du double.

**Ce qui est en place.** `data/reference/prose/zones.yaml` déclare, section par
section, ce qu'elle affirme — `etat`, `recit`, `produit`, `a_declarer` ;
`scripts/verifier_prose.py` recalcule tout chiffre ancré et refuse un chiffre
nu dans une zone d'état ; `tests/test_prose.py` en fait une obligation. Deux
cliquets, dans `zones.yaml`, ne peuvent que décroître : les sections non
déclarées et les chiffres qui portent l'aveu `a_verifier`. Tout est décrit dans
`docs/fraicheur.md`.

**Ce qui reste — et c'est le travail, qui se fait section par section.**
Abaisser le premier cliquet. `limites.md` est le morceau principal et le plus
mélangé : trois sections au présent, qui disent ce que les chiffres du dépôt
valent, et une cinquantaine au passé, qui racontent des corrections faites.
`methodologie.md`, `avantages_non_contributifs.md` et le reste du README
suivent. Rien n'oblige à tout reprendre d'un coup, et rien ne permet de
reculer.

**L'angle mort à traiter ensuite.** Ce contrôle ne juge pas une phrase,
seulement un nombre : « la bascule ne reprend aucun droit acquis » lui est
invisible. C'est l'action 34, et les deux se complètent — l'une tient les
chiffres du dépôt, l'autre les affirmations du site.

**Fichiers.** `scripts/verifier_prose.py`, `data/reference/prose/zones.yaml`,
`tests/test_prose.py`, `docs/fraicheur.md` (neufs) ; les ancres posées dans
`README.md`, `docs/feuille_de_route.md` et `docs/limites.md`.

### 42. La passe visuelle du 19 septembre 2026 : vingt constats, du téléphone au bureau — `fait`

**Pourquoi.** Le site n'avait jamais été regardé page par page à plusieurs
largeurs depuis la refonte en affiche (action 30) et la bascule net/brut
(action 39). Cette passe l'a fait : les neuf routes à 360, 768 et 1280 points,
puis les états qu'une capture de page ne montre pas — les résultats d'une
simulation, chaque dépliant ouvert, la bulle d'un mot du glossaire, un refus de
saisie, le focus clavier, la lecture d'un graphique au survol, la version
imprimée. Aucune page ne défile horizontalement, aucune erreur de console, la
bulle, le refus de saisie et les anneaux de focus sont justes. Le reste est
ci-dessous, du plus visible au plus discret ; les lignes renvoient à
`src/retraite_notionnelle/web/gabarit.py` (la feuille de style y vit) sauf
mention contraire. **Rien n'a été corrigé** : cette action est la liste.

**Ce qui se voit de loin — corrigé le 19 septembre 2026, comme le reste.**
Ce qui a été fait, point par point, est dit à la fin de l'action ; les
constats restent tels qu'ils ont été écrits, avec les lignes d'alors.

1. *La bande de lecture d'un graphique est cassée.* Au survol d'une courbe,
   la bande sous le tracé affiche « • ■Ce qui sort13,5 » : puces de liste,
   pastille collée au libellé, valeur collée au libellé. Le script
   (`index.html`, ligne 680) écrit `<span class="annee">` puis un `<ul>` de
   `<li>` avec une `.pastille` ; la feuille (ligne 1170) attend des enfants
   directs en colonnes de grille avec `.etiquette`, `.valeur` et `.complement`.
   Les deux ont été écrits dans le même commit et ne se sont jamais rencontrés.
   Correction : écrire la CSS de la structure réelle — `ul` sans puces en
   `display: flex`, `li` en `inline-flex` avec un `gap`, `.valeur` en graisse
   900 —, ou faire produire par le script la structure que la CSS attend.
2. *Les graphiques sont illisibles sur téléphone.* À 360 points, le SVG est
   réduit à 42 % : la règle de la ligne 1496 grossit bien les graduations à 24
   unités, mais les marges (ligne 2560 et suivantes : 66 à gauche, 24 à droite)
   restent en unités du repère et ne suivent pas. Résultat : « k€ » sur
   « 1 500 », « 1831 » collé à « 1850 », « 2060 » sur « 2070 », l'étiquette
   « espérance de vie : 89,7 ans » qui sort du cadre, et l'unité de l'axe
   (« Md€ courants ») coupée au bord gauche de la carte. Toutes les pages à
   graphique (Trajectoire, Coût, Avantages, résultats) sont touchées.
   Correction : un second jeu de marges sous 34 rem — ou, plus simple, une
   `viewBox` recalculée pour le téléphone, portée par un attribut que la CSS
   choisit —, et l'unité de l'axe ancrée à `text-anchor="start"` sur le bord
   gauche (ligne 2973) plutôt qu'à `end` sur l'axe, ce qui la ferait tenir
   quelle que soit sa longueur (à 1280 points déjà, « Md€ courants » déborde de
   quarante pixels dans la marge de la carte).
3. *La légende « PREMIER MÉTIER » du simulateur est invisible.* Elle est
   écrite dans `--sur-creme-doux` (ligne 673), la couleur du texte doux SUR
   CRÈME, alors que le formulaire de la page Simuler est sur carte sombre :
   du vert foncé sur vert foncé, à toutes les largeurs. Elle n'est lisible
   qu'à l'impression. Correction : `color: var(--texte-doux)`, la couleur du
   fond crème n'étant à prendre que sous `.creme`.
4. *Une bande sombre borde la droite de chaque tableau posé sur une carte.*
   Le voile de l'ombre de défilement (ligne 726) est peint dans `--fond`, le
   vert de la page ; sur une carte `--fond-carte` (les sections clés de Coût,
   Avantages, Méthode, les résultats, la fiche de paie), il fait un rectangle
   d'un ton plus sombre de 2,5 rem au bord droit, même quand rien ne défile.
   Correction : une variable `--fond-defilant` que `.cle`, `.encadre` et les
   autres cartes redéfinissent à leur couleur.
5. *Sur téléphone, la légende d'un tableau qui défile est coupée.* La
   `<caption>` est large comme le tableau, pas comme l'écran : « Ce que le
   plancher individualisé change, p », « La proposition libérale : taux
   unique de 18 % et g », « Ce que chaque règle d'indexation aurait cons »
   (accueil, Cas types, Méthode à 360 points). Correction : sortir le titre
   du tableau vers un `<p>` au-dessus de `.defilant` (avec `aria-describedby`
   ou en le gardant en `caption` positionnée `sticky; left: 0`, à vérifier
   dans les deux moteurs).
6. *Des nombres se coupent en deux.* « 300 € et 1 500 € » se lit « 300 € et
   1 500 / € » puis « 5 / 000 € » dans le tableau du plancher à 360 points :
   les espaces de la ligne 2204 de `pages.py` sont ordinaires, pas fines
   insécables comme partout ailleurs. Même famille : « 12 028,70 € par / an »
   dans les étapes de la garantie vieillesse (résultats, 1280 points),
   « 62 / ans » dans les deux dernières colonnes de l'âge de liquidation (Cas
   types), « 2026-09- / 14 » sur les 88 lignes de la page Données. Correction :
   `white-space: nowrap` sur `td.nombre` et sur la colonne des dates, et les
   espaces insécables dans les libellés composés.
7. *Un mot du glossaire dans une case étroite se brise en bloc.* Sur l'accueil
   à 360 points, « vos 25 meilleures années, un taux » devient « vos /
   25 meilleures / années / , un taux » : le `<button class="terme">` est un
   `inline-block` (ligne 1100), et un bloc ne coule pas dans une phrase. Même
   cause, autre effet : dans les repères des résultats, « capital notionnel
   rétroactif, en euros de 2039 » s'affiche CENTRÉ sur deux lignes, parce
   qu'un bouton centre son texte. Correction : `display: inline` sur le
   bouton (à vérifier dans Chromium, qui traite parfois un bouton comme un
   bloc quoi qu'on lui dise ; sinon un `<span role="button" tabindex="0">`)
   et `text-align: inherit`.
8. *Les colonnes de phrases sont alignées à droite.* La CSS prévoit
   `td.texte` pour cela (ligne 753), mais les tableaux qui portent des
   phrases ne l'utilisent pas : « D'où vient le chiffre, ou pourquoi il
   manque » sur Avantages (39 lignes en drapeau à droite, mot par mot à 360
   points), « Ce qu'elle fait », « Ce qui se passe », « Calcul » et « Placé »
   dans les résultats, la colonne des notes des 89 régimes sur Données — où
   une note de trente lignes dans une colonne de 200 points fait une rangée de
   700 points de haut. Correction : poser `.texte` dans `pages.py` sur ces
   colonnes, et donner aux notes longues une glose sous le tableau
   (`dl.gloses`) plutôt qu'une cellule.

**Ce qui se voit de près.**

9. *Les engagements 02 et 04 sont décalés à 768 points.* La grille passe à
   une colonne dès que deux fois 45 % ne tiennent plus, mais le retrait et le
   filet des cartes paires (ligne 497) ne sont retirés qu'à 34 rem (ligne
   1459) : entre les deux, une carte sur deux est en retrait de 24 points.
   Correction : aligner les deux seuils, ou porter le filet par un
   `:nth-child(even)` sous une requête de conteneur.
10. *Le dernier filet d'un tableau s'arrête sous la première colonne.* La
    règle `tbody tr:last-child td { border-bottom: none }` (ligne 749) ne
    couvre pas le `<th>` de rangée : chaque tableau finit par un trait
    orphelin de la largeur de sa première cellule. Visible sur tous.
    Correction : `tbody tr:last-child :is(th, td)`.
11. *« UNITÉ … × salaire moyen MONTANTS net brut » sans espace.* Les deux
    bascules du formulaire sont des `inline-flex` sans marge entre elles
    (ligne 833) : la seconde légende colle au dernier bouton de la première.
    Correction : `column-gap` sur le conteneur ou `margin-right: 1.25rem`.
12. *Sur l'accueil et Trajectoire, le menu « Statut » descend sous les
    autres champs.* La grille courte aligne ses cellules par le bas (ligne
    464), et « Statut » est le seul champ sans ligne d'aide ni de rappel
    dessous : son menu tombe 30 points plus bas que les dates. Correction :
    lui donner une aide (« régime au premier emploi ») ou aligner par le
    haut avec une hauteur d'étiquette fixe.
13. *« Les règles du calcul (indexation, projection, bascule…) » n'est pas
    une section.* Sur Cas types, Coût et Avantages, ce dépliant suit la pile
    des `details.section` sans en avoir le style : chevron décalé, sans
    graisse, sans filet, avec un vide au-dessus. Il porte un formulaire, pas
    un texte, et c'est peut-être voulu — mais il se lit comme un oubli.
    Correction : soit `class="section"`, soit un style propre et nommé.
14. *Les trois repères de la page Données ne sont pas alignés.* « Valeurs
    recontrôlées contre leur source » tient sur deux lignes et pousse son
    nombre 20 points sous « 89 » et « 28 » (ligne 995 : colonne flexible,
    étiquette avant le nombre). Correction : `grid-template-rows: auto 1fr
    auto` avec le nombre calé en bas, ou une hauteur minimale d'étiquette.
15. *Sur Avantages à 360 points, les tableaux des trente-neuf ne se
    comportent pas tous pareil.* Le premier se comprime jusqu'à un mot par
    ligne, les suivants dépassent et défilent : chaque tableau décide seul,
    selon son contenu. Correction : la même largeur minimale pour tous
    (`table { min-width: 34rem }` sous `.defilant` à cette largeur), ou une
    mise en page en liste sous 34 rem.
16. *Les aperçus des cartes à publier sont illisibles à 360 points.* Réduits
    au rapport 16/9 de leur colonne, leurs textes tombent à cinq pixels. Ce
    sont des aperçus d'image, donc tolérable ; un lien « voir l'image en
    grand » sous chacun réglerait la question.

**Ce qui se voit à peine.**

17. *« ESTIMEE »* dans le badge de fiabilité des résultats et du compartiment
    capitalisé, sans accent : `nomFiabilite` rend la clé et la CSS la met en
    capitales. « Estimée » et l'accent survivrait à `text-transform`.
18. *L'en-tête collant des tableaux de points d'un graphique* est peint en
    `--fond-carte` (ligne 1246) même hors carte, dans les dépliants des
    résultats : une bande d'un ton plus clair au-dessus du tableau.
19. *La page Trajectoire parle des « quatre montants du haut »* qu'elle ne
    montre pas : la phrase vient du dépliant des résultats et n'a pas été
    adaptée à la page.
20. *À 768 points exactement, le bandeau tient sur deux rangées* et la
    seconde n'a que trois entrées ; à 360 il en faut trois, et il n'est plus
    collant (voulu, ligne 1427). Rien à faire, noté pour mémoire.

**Vérifié, et sain.** Le contraste de tous les textes courants ; les anneaux
de focus, y compris sur les résumés des dépliants et les appels de bulle ; la
bulle du glossaire, qui reste dans l'écran à 360 points ; le refus de saisie ;
la pile des trois repères et des engagements à 360 points ; la version
imprimée du simulateur ; le formulaire long à toutes les
largeurs, hormis les points 3 et 11 ; le pied de page.

**Comment refaire la passe.** Servir le dépôt (`python -m http.server`),
lancer Chromium par Playwright à trois largeurs, capturer chaque route en
page entière, puis rejouer les états : soumettre le formulaire, ouvrir tous
les `<details>`, cliquer un `.terme`, tabuler, survoler un `svg`, passer en
média `print`. Un script de vingt lignes fait tout ; il devrait rejoindre
`scripts/` avec cette action, et écrire ses captures hors du dépôt.

**Ce qui a été corrigé (les huit premiers).** 1 : la feuille décrit
maintenant la structure que le script écrit — année en tête, liste sans
puces, pastille, nom, valeur en graisse —, empilée sous 48 rem. 2 : sous
34 rem le tracé ne descend plus sous 30 rem et défile dans sa figure, les
graduations passent de 24 à 18 unités ; l'unité de l'axe part du bord gauche
du repère (`text-anchor="start"` à `x="0"`) et l'étiquette du repère se pose
du côté où il reste de la place, dans les deux portages. 3 : la légende du
métier est dans `--texte-doux`, et ne reprend `--sur-creme-doux` que sous
`.creme`. 4 : une variable `--fond-defilant`, que `.carte`, `.note`,
`.plan`, `.erreur`, `.cadre-carte`, `.engagements`, `section.cle` et
`.creme` redéfinissent à leur couleur. 5 : la `<caption>` porte un `<span>`
collant large de `100cqw`, `.defilant` étant devenu conteneur de requête —
une `<caption>` ne peut pas être collante elle-même, et en bloc Chromium la
range sous l'en-tête ; les deux ont été essayés. 6 : `td.nombre`, `td.date`
et `th.date` ne se coupent plus (`white-space: nowrap`), la colonne des
dates de la page Données porte `date`, et les couples du plancher sont
écrits avec des espaces insécables ordinaires — la fine (U+202F) que le site
emploie dans ses nombres est presque invisible en gras, et ces libellés
voisinent des cellules qui gardent une espace pleine. 7 : le mot du
glossaire est un `<span role="button" tabindex="0">`, parce que Chromium
rend tout `<button>` en bloc en ligne quoi qu'on lui dise (essayé :
`display: inline` reste `inline-block`) ; `index.html` lui donne Entrée et
Espace, `text-align: inherit` défait le centrage, et l'appel de bulle reste
un vrai bouton. 8 : `.texte` posé sur les cinq colonnes de phrases, et
`.texte long` (18 rem au moins) sur les notes des 89 régimes. Les deux
tests qui attendaient un `<button>` ou une espace pleine ont été mis à jour
avec le gabarit.

**Ce qui a été corrigé ensuite (les points 9 à 20, le même jour).** 9 : la
grille des engagements est à deux colonnes fixes, et passe à une seule sous
48 rem, dans la même requête que le retrait et le filet des cartes paires —
`auto-fit` la repliait dès 40 rem, quatorze rem avant ses filets. 10 :
`tbody tr:last-child :is(th, td)`. 11 : `margin-right: 1.25rem` sur la
bascule. 12 : « Statut » porte une ligne d'aide (« celui du premier
emploi »), et la grille courte s'aligne par le haut, le bouton centré. 13 :
le dépliant des règles porte `class="section"`. 14 : les repères sont une
sous-grille (`grid-template-rows: subgrid`, trois rangées partagées) là où
elle existe, la colonne flexible ailleurs. 15 : chaque famille de dispositifs
est dans une boîte `.dispositifs`, et sous 34 rem ses tableaux gardent 30 rem
et défilent tous. 16 : sous 34 rem l'aperçu d'une carte à publier garde 36 rem
et défile dans sa figure — le texte y reste lisible parce que les `cqw` se
mesurent sur cette largeur-là. 17 : `fiabilite_en_clair` (`fiabiliteEnClair`
en JavaScript) accentue les niveaux partout où ils s'affichent — badges,
tableaux, menus de filtre —, les clés restant sans accent dans les attributs
et les adresses. 18 : l'en-tête collant des tableaux de points est peint en
`--fond-defilant`, comme le voile. 19 : la page Trajectoire ouvre sur
« Chaque système sert une pension mensuelle ; ce graphique les additionne »,
le dépliant de Simuler gardant sa phrase. 20 : rien à faire, comme noté.
Trois tests qui cherchaient l'ancienne classe du bloc de réglages ont été mis
à jour.

**La seconde passe, le même jour, après les vingt.** Refaite de zéro sur
`main`, avec les mêmes captures et un diagnostic automatique de plus — les
textes d'un SVG qui sortent du cadre ou se recouvrent. Aucune page ne
déborde, aucune erreur de console, et rien des vingt ne revient. Sept
constats de moins de gravité, corrigés dans la foulée : sur téléphone,
l'unité d'un graphique recouvrait la graduation du haut et le « 0 » de
l'axe recouvrait la première année (les marges du repère passent de 26 et
28 à 34 unités, les années descendent de 8, la marge de droite loge la
moitié de « 2070 » à 18 unités) ; la bande de lecture d'un graphique
doublait la légende — deux listes des mêmes séries, l'une chiffrée — et
prend maintenant sa place, la légende revenant quand le pointeur sort ; les
branches d'une bascule se coupaient en deux (« € par / mois ») ; quatre
colonnes de phrases restaient alignées à droite (la base légale et le
modèle des 42 dispositifs, « ce que cela veut dire », la caisse de chaque
cas type) ; les tableaux des 91 séries et des 89 régimes, et tout tableau
d'au moins quatre colonnes sous 34 rem, gardent une largeur de lecture et
défilent au lieu de mettre un mot par ligne. Ce qui reste et qu'on laisse :
une note de quinze lignes dans une cellule de l'inventaire des régimes fait
une rangée haute, à toutes les largeurs — c'est le contenu, et la glose
sous le tableau proposée au point 8 est la vraie réponse.

**Les champs d'une même rangée, sur la même ligne.** Signalé après la
seconde passe : dans les formulaires, les contrôles d'une rangée ne
partaient pas de la même hauteur. Deux causes. Chaque cellule était une
colonne flexible dont le libellé absorbait la hauteur en trop, ce qui
calait les contrôles par le BAS : une date, qui garde sa ligne de rappel
sous elle (« soit 21 ans »), remontait d'autant au-dessus de ses voisins,
et le mot du glossaire d'un libellé sur deux lignes (« Sexe », « Règle
d'indexation ») faisait remonter le sien de soixante-dix points. Et les
contrôles n'avaient pas la même hauteur : 54 points pour une date, 47 pour
un menu, 52 pour un nombre. Chaque cellule est maintenant une sous-grille de
trois rangées — libellé, contrôle, rappel — partagées par toute la rangée,
avec un repli en colonne flexible là où la sous-grille n'existe pas, et tout
contrôle a 3,375 rem de haut au moins. Le bouton du formulaire court occupe
les mêmes trois rangées et se pose sur celle des contrôles. Mesuré dans
Chromium à 768 et 1 280 points, sur l'accueil et sur Simuler avec tous les
dépliants ouverts : plus aucune rangée où deux contrôles partent de hauteurs
différentes.

**Fichiers touchés le 19 septembre.** `web/gabarit.py` et `moteur/js/gabarit.js`
(feuille, `mot`, `tableau`, `graphique`, `fiabilite_en_clair`), `web/pages.py`
et `moteur/js/pages.js` (classes de colonnes, libellés du plancher, aide du
statut, classe du bloc de réglages, boîte des dispositifs, niveaux en clair,
phrase de Trajectoire), `index.html` (Entrée et Espace sur un mot du
glossaire), `tests/test_web.py`, `moteur/style.css` et
`tests/temoins/pages.json` régénérés.

**Fichiers à toucher pour une passe suivante.** `src/retraite_notionnelle/web/gabarit.py` (la
feuille, les marges du graphique, l'unité de l'axe), `index.html` (la bande
de lecture), `src/retraite_notionnelle/web/pages.py` et son portage
`moteur/js/pages.js` (classes `.texte`, espaces insécables, « Estimée »,
la phrase de Trajectoire), puis `python scripts/construire_donnees.py` et les
témoins.

**Un vingt-et-unième constat, venu d'un lecteur le même jour.** Sous le champ
« Revenu brut mensuel », l'aide donnait trois repères : « SMIC 1 823 €,
moyenne 3 475 €, plafond 4 005 € ». Le troisième est le plafond mensuel de la
Sécurité sociale, mais sous un champ numérique, le mot se lit comme le maximum
que le champ accepte — et c'est ainsi qu'il a été lu. Le repère ne parle qu'à
qui connaît la tuyauterie des régimes ; il est retiré, et « moyenne » devient
« salaire moyen » : « Repères : SMIC 1 823 €, salaire moyen 3 475 € ». Les
deux portages, `tests/test_web.py`, le README et `tests/temoins/pages.json`
suivent. Le champ, lui, n'a pas changé : il accepte de 0,1 à 10 fois le
salaire moyen, et le refus au-delà le dit en euros.

### 43. Une mère, enfant par enfant : ce que chaque système lui sert — `fait`

**Pourquoi.** La question posée le 19 septembre 2026 : que devient la pension
d'une femme qui a eu un ou plusieurs enfants, sous le droit en vigueur et sous
la proposition libérale ? Le modèle savait répondre — le scénario 1 porte la
majoration de durée d'assurance, la bonification de la fonction publique, la
majoration de 10 % à trois enfants, l'AVPF sur les années d'arrêt, la surcote
parentale et les trimestres d'enfants réputés cotisés ; les scénarios
notionnels neutralisent tout cela, un compte ne portant que ce qui a été
cotisé —, mais aucun endroit du dépôt ne mettait les deux face à face pour une
mère. Un seul cas type en a, avec deux enfants, et l'action 37 avait relevé que
la majoration pour trois enfants y valait zéro.

**Marche.** `scripts/scenarios_meres.py` : une même femme, salariée du privé à
0,9 fois le salaire moyen, entrée à vingt et un ans, et treize situations —
zéro à trois enfants, carrière complète ou trois et six ans d'arrêt, départ au
taux plein ou à l'âge légal, mi-temps au SMIC, fonctionnaire d'État. L'âge de
départ est résolu par le droit de la génération, comme pour les cas types :
c'est par là que les trimestres d'enfants se voient, une mère de deux enfants
atteignant le taux plein seize trimestres avant la femme sans enfant. Chaque
ligne donne la pension mensuelle des scénarios 1 et 6, en euros de 2026, et
l'« effet des enfants » de chacun : l'écart à la même carrière sans enfant,
partie au même âge, ses années d'arrêt devenant de simples années sans
activité. `--generation`, `--niveau`, `--affiliation`, `--detail` (les
avantages appliqués sous chaque ligne), `--csv`. Six tests dans
`tests/test_scenarios_meres.py`.

**Ce que ça mesure, génération 1966.** Le scénario 6 ne sert rien au titre
des enfants, dans aucune ligne : c'est la construction même du compte, et le
test l'exige. Le scénario 1 sert, à carrière complète, 134 € par mois pour un
enfant, 143 € pour deux, 366 € pour trois — les deux premiers presque tout par
le départ neuf mois plus tôt au même montant, le troisième par la majoration
de 10 %. Avec des années d'arrêt, l'AVPF et les trimestres assimilés font le
gros : 543 € pour deux enfants et trois ans, 846 € pour trois enfants et six
ans. L'écart entre les deux systèmes se creuse d'autant : −30 % sans enfant,
−34 % avec un ou deux, −40 % avec trois, −46 % pour trois enfants et six ans
d'arrêt. Le mi-temps au SMIC à trois enfants est le seul cas où la garantie
vieillesse joue : 711 € à 63 ans et 3 mois, 1 050 € à 65 ans — le plancher
d'une personne seule —, contre 1 322 € puis 1 437 € sous le scénario 1. La
fonctionnaire d'État à deux enfants est la seule qui gagne au scénario 6
(+11 %), par la part patronale de l'État portée au compte ; elle y perd dès
qu'elle a trois enfants et trois ans d'arrêt (−3 %).

**Ce qui n'y est pas.** La réversion, que le modèle ne voit pas ; la
majoration pour congé parental et celle pour enfant handicapé, absentes du
scénario 1 ; le partage de la MDA entre les parents, que la loi de 2010
permet et que le modèle donne entière à la mère ; et une population : la
grille dit ce qu'une mère perd ou gagne, pas ce que les mères pèsent.
